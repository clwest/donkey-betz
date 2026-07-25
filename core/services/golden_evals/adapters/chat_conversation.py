"""Adapter for the ``core.ChatConversation`` substrate.

Handles the eighth Tier-1 slice (``evals/tier1/rigby_agent.yaml``) — the
first canon_version=1 file authored against a non-``AgentExecution``
substrate. Proves the two-substrate abstraction the harness commits to at
canon_v2 Item 6.

Canon_v2 Item 2 (source stratification): multi-source substrates like
``ChatConversation`` (``source IN ('web', 'mobile', 'discord', 'api',
'claude-code', 'pa')``) MUST declare + filter to the buyer-facing surface.
The default source filter here is ``('web', 'pa')`` — matches the
canonical filter declared in ``rigby_agent.yaml`` header line 78.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from django.db.models import QuerySet

from ..context import (
    EVIDENCE_LEDGER,
    EVIDENCE_METADATA_CACHE,
    LEDGER_HEALTH_OK,
    LEDGER_HEALTH_STALE,
    LEDGER_HEALTH_UNAVAILABLE,
    SUBSTRATE_CHAT_CONVERSATION,
    EvalRunContext,
)
from .base import SubstrateAdapter


BUYER_FACING_SOURCES: tuple[str, ...] = ("web", "pa")


# Anchors the ``LEDGER_HEALTH_STALE`` signal. If the most recent
# ``ToolCallRecord`` matched for the conversation is older than this delta
# from the ChatConversation row, treat the join as stale rather than
# ok — the PA write regression at 2026-06-19 (Ledger #21) means recent
# turns hit the metadata cache path only, and Rigby-specific fabrication
# predicates should treat that population as inconclusive.
_LEDGER_STALENESS_WINDOW = timedelta(days=1)


def filter_to_buyer_facing_sources(
    qs: QuerySet,
    sources: tuple[str, ...] = BUYER_FACING_SOURCES,
) -> QuerySet:
    """Apply canon_v2 Item 2 source-stratification filter.

    ``ChatConversation`` rows with ``source='claude-code'`` are
    developer-tolerant agent-to-agent traffic (Claude Code driving Rigby
    via ``bash tools/pa_local.sh`` dispatches) and MUST NOT be mixed into
    buyer-facing eval populations — same ``user_id`` (Chris) but a
    different trust surface. See ``rigby_agent.yaml`` header §"SOURCE-SPLIT
    FILTER" for the canonical framing.
    """
    return qs.filter(source__in=sources)


class ChatConversationAdapter(SubstrateAdapter):
    """Normalize ``core.ChatConversation`` rows to :class:`EvalRunContext`.

    Evidence hierarchy (S2965 PR-2a — Rigby A2 REVISE):

    * **Canonical (per rigby_agent.yaml canon_version=1):**
      ``ToolCallRecord`` joined via ``conversation_id`` (falling back to
      ``trace_id`` if #20 gets fixed). Tagged ``evidence_source =
      EVIDENCE_LEDGER``.
    * **Fallback:** ``ChatConversation.metadata.tool_calls`` and
      ``ChatConversation.metadata.tool_results`` — the convenience mirror
      returned by ``UnifiedPAEntrypoint.process_message`` and rendered in
      the Rigby chat UI. Tagged ``evidence_source =
      EVIDENCE_METADATA_CACHE``. Runners for Rigby-specific
      fabrication predicates (``no_fabricated_*``,
      ``detects_and_surfaces_tool_runs_empty_vs_claimed``) MUST gate on
      ``ledger_health`` before drawing conclusions from cache evidence —
      the cache is a convenience mirror written by the agent itself, not
      an authoritative audit trail.

    Ledger-health decision matrix:

    * ``ok`` — at least one ``ToolCallRecord`` row matches the
      conversation's ``conversation_id`` AND the most recent such row is
      inside :data:`_LEDGER_STALENESS_WINDOW` of the ChatConversation
      row's ``created_at``. Native evidence source is ``EVIDENCE_LEDGER``.
    * ``stale`` — some historical ``ToolCallRecord`` rows exist for this
      conversation_id but none inside the staleness window (i.e. the
      ledger stopped receiving writes at some point). Native evidence
      source falls back to ``EVIDENCE_METADATA_CACHE``.
    * ``unavailable`` — no ``ToolCallRecord`` rows for the
      conversation_id at all. Native evidence source is
      ``EVIDENCE_METADATA_CACHE``.

    All three cases produce a valid ``EvalRunContext`` — the caller
    (predicate runner) decides whether the ledger health signal permits
    fabrication assertions.
    """

    substrate_type = SUBSTRATE_CHAT_CONVERSATION

    def __init__(
        self,
        sources: tuple[str, ...] = BUYER_FACING_SOURCES,
        include_latency: bool = False,
    ) -> None:
        """Construct the adapter.

        ``include_latency`` controls whether ``latency_ms`` is populated
        from ``response_time_ms``. Off by default per canon_v2 Item 3
        (opt-in per slice YAML).
        """
        self.sources = sources
        self.include_latency = include_latency

    def build_context(self, primary_row_id: str) -> EvalRunContext:
        import uuid as _uuid

        from core.models import ChatConversation
        from core.models_tool_calls import ToolCallRecord

        try:
            row = ChatConversation.objects.get(pk=int(primary_row_id))
        except (ChatConversation.DoesNotExist, ValueError) as exc:
            raise LookupError(
                f"ChatConversation row {primary_row_id!r} does not exist "
                "or is not a valid integer PK"
            ) from exc

        # Safety net for canon_v2 Item 2: refuse rows outside the declared
        # buyer-facing source filter, even if the caller bypassed
        # ``filter_to_buyer_facing_sources`` at query time. Mirrors the
        # ``AgentExecutionAdapter``'s canon_v2 Item 4 safety net.
        if row.source not in self.sources:
            raise ValueError(
                f"ChatConversation {primary_row_id!r} has source={row.source!r}, "
                f"not in adapter's buyer-facing filter {self.sources!r}. Filter "
                "with filter_to_buyer_facing_sources() at query construction."
            )

        # ── Evidence-source resolution ──────────────────────────────────
        evidence_refs: list[dict[str, Any]] = []
        evidence_source = EVIDENCE_METADATA_CACHE
        ledger_health = LEDGER_HEALTH_UNAVAILABLE

        # Attempt ToolCallRecord ledger join on ``conversation_id``.
        # Substrate mismatch surfaced at S2965 T1 dogfood: ChatConversation
        # stores ``conversation_id`` as ``CharField`` (values like
        # ``pa-50542bacf8014a20`` — PA trace-prefix strings, Discord IDs,
        # etc.) while ``ToolCallRecord.conversation_id`` is a ``UUIDField``
        # that only accepts UUID-parseable values. For rows whose
        # ``conversation_id`` cannot round-trip through
        # ``uuid.UUID(...)``, the ledger join is structurally impossible —
        # treat as ``LEDGER_HEALTH_UNAVAILABLE`` and fall back to the
        # metadata cache without ever hitting Django's UUID coercion path.
        # The historical PA population that did land in the ledger used
        # UUID-shaped conversation_ids; the modern PA-prefix format
        # (2026-06-19+) does not, which is one facet of the write-path
        # regression captured in Rigby Tool Gap Ledger #21.
        ledger_qs = None
        try:
            conversation_uuid = _uuid.UUID(str(row.conversation_id))
        except (ValueError, TypeError, AttributeError):
            conversation_uuid = None

        if conversation_uuid is not None:
            ledger_qs = ToolCallRecord.objects.filter(
                conversation_id=conversation_uuid
            ).order_by("-created_at")

        latest_ledger_row = ledger_qs.first() if ledger_qs is not None else None
        if latest_ledger_row is not None:
            # Some ledger rows exist for this conversation. Decide
            # ok-vs-stale based on staleness window.
            age = row.created_at - latest_ledger_row.created_at
            if age <= _LEDGER_STALENESS_WINDOW:
                ledger_health = LEDGER_HEALTH_OK
                evidence_source = EVIDENCE_LEDGER
                # Only enumerate ledger refs when health is ok — otherwise
                # the caller might treat stale rows as authoritative.
                for tcr_id in ledger_qs.values_list("id", flat=True):
                    evidence_refs.append(
                        {"kind": "tool_call_record", "id": str(tcr_id)}
                    )
            else:
                # Ledger has historical rows but none in the recent window.
                ledger_health = LEDGER_HEALTH_STALE

        # When ledger health is not ok, populate evidence refs from the
        # metadata cache. Shape B (sync-dispatch) rows carry declared
        # tool_calls + outcomes; Shape A (async-callback) rows do not.
        # Enumerate whichever is present so downstream runners can consume
        # a uniform shape.
        if ledger_health != LEDGER_HEALTH_OK:
            metadata = row.metadata or {}
            if isinstance(metadata, dict):
                declared_calls = metadata.get("tool_calls") or []
                if isinstance(declared_calls, list):
                    for idx, call in enumerate(declared_calls):
                        evidence_refs.append(
                            {
                                "kind": "metadata_tool_call_declared",
                                "index": idx,
                                "tool": (
                                    call.get("tool")
                                    if isinstance(call, dict) else None
                                ),
                            }
                        )
                declared_results = metadata.get("tool_results") or []
                if isinstance(declared_results, list):
                    for idx, res in enumerate(declared_results):
                        evidence_refs.append(
                            {
                                "kind": "metadata_tool_result",
                                "index": idx,
                                "ok": (
                                    res.get("ok")
                                    if isinstance(res, dict) else None
                                ),
                            }
                        )

        # ── Finalization signal ─────────────────────────────────────────
        # Per Rigby T1 SIGN Q3 REVISE: only claim finalization when the
        # substrate has both a populated ``response_time_ms`` AND a
        # non-empty ``assistant_response``. Rows without either are
        # either mid-flight (write-path fired but PA pipeline hasn't
        # populated the response yet) OR instrumentation-missing (some
        # web rows have empty metadata + null response_time_ms, S2965 T1
        # dogfood observation) — in both cases ``finalized_at = None``
        # tells validators to defer or skip rather than fail.
        finalized_at: datetime | None = None
        if row.response_time_ms and row.assistant_response:
            finalized_at = row.created_at + timedelta(
                milliseconds=int(row.response_time_ms)
            )

        return EvalRunContext(
            substrate_type=self.substrate_type,
            primary_row_id=str(row.pk),
            evidence_ledger_refs=evidence_refs,
            finalized_at=finalized_at,
            latency_ms=(row.response_time_ms if self.include_latency else None),
            evidence_source=evidence_source,
            ledger_health=ledger_health,
        )
