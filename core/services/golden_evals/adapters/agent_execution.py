"""Adapter for the ``core.AgentExecution`` substrate.

Handles the 7 Tier-1 slices authored against ``AgentExecution`` rows
(slices 1-7 per the S2963 arc-close table).
"""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from ..context import (
    EVIDENCE_AGENT_EXECUTION_NATIVE,
    LEDGER_HEALTH_OK,
    LEDGER_HEALTH_UNAVAILABLE,
    SUBSTRATE_AGENT_EXECUTION,
    EvalRunContext,
)
from .base import SubstrateAdapter


# Statuses that mark an ``AgentExecution`` row as reached its final state.
# Runs still in ``pending`` / ``running`` / ``queued`` are mid-flight and
# validators should defer, not fail.
_FINALIZED_STATUSES: frozenset[str] = frozenset({"completed", "failed", "cancelled"})


def exclude_synthesized_pa_receipts(qs: QuerySet) -> QuerySet:
    """Apply canon_v2 Item 4 receipt-contamination filter to an
    ``AgentExecution`` queryset.

    Canon_v2 Item 4 predicate (S2963 arc-close ratification, source
    ``docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md``):

        NOT (parent_object_type = 'deliverable_factory'
             AND input_data.source = 'deliverable_factory.synthesized_pa_receipt')

    Synthetic deliverable-factory receipts (``tokens_used=0``, ``cost=0``,
    ``output_data.kind='deliverable_receipt'``) masquerade as real turns
    when the receipt fingerprint is not filtered. Any Tier-1 query on
    ``AgentExecution`` for real-usage sampling, evidence-pointer joins, or
    ground-truth selection MUST route through this helper — a shared,
    canon-documented function per Rigby's S2964 T1 SIGN Q5 REVISE ("prevents
    'helpful refactor' drift in S2965+").
    """
    return qs.exclude(
        parent_object_type="deliverable_factory",
        input_data__source="deliverable_factory.synthesized_pa_receipt",
    )


class AgentExecutionAdapter(SubstrateAdapter):
    """Normalize ``core.AgentExecution`` rows to :class:`EvalRunContext`.

    Evidence hierarchy (S2965 PR-2a):

    * **Primary (native):** ``AgentExecution.output_data['tool_calls']`` —
      BaseAgent.execute populates this list with ``{tool, arguments,
      result_summary}`` dicts. Tagged ``evidence_source =
      EVIDENCE_AGENT_EXECUTION_NATIVE``, always available for finalized
      rows, so ``ledger_health = LEDGER_HEALTH_OK``.
    * **Secondary (cost/latency):** ``LLMCallLog`` joined via
      ``trace_id`` — 100% populated in the live substrate (60,999 rows,
      0 NULL). Emitted only when the slice YAML declares latency as an
      evidence dimension (canon_v2 Item 3 opt-in).
    * **Tertiary (audit ledger):** ``ToolCallRecord`` joined via
      ``trace_id`` — theoretically canonical, but S2965 T1 raw-ORM
      verification found ``trace_id=NULL`` on 100% of 5,430 rows (Rigby
      Tool Gap Ledger #20). The join is attempted for portability; when
      it returns zero rows the row is silently ignored, native evidence
      remains authoritative. Not the primary substrate for
      ``AgentExecution`` slices — that role is reserved for
      ``ChatConversation`` (Rigby) which has no native tool-call array.
    """

    substrate_type = SUBSTRATE_AGENT_EXECUTION

    def __init__(self, include_latency: bool = False) -> None:
        """Construct the adapter.

        ``include_latency`` controls whether ``latency_ms`` is populated
        from ``execution_time_ms``. Off by default per canon_v2 Item 3
        (opt-in per slice YAML). The management command flips this on
        when a slice's ``expected_output_shape`` or ``acceptance_criteria``
        block declares latency as an evidence dimension.
        """
        self.include_latency = include_latency

    def build_context(self, primary_row_id: str) -> EvalRunContext:
        from core.models import AgentExecution
        from core.models_tool_calls import ToolCallRecord

        try:
            row = AgentExecution.objects.get(pk=primary_row_id)
        except AgentExecution.DoesNotExist as exc:
            raise LookupError(
                f"AgentExecution row {primary_row_id!r} does not exist"
            ) from exc

        # Enforce canon_v2 Item 4 at read time as a safety net: even if a
        # caller hands us the PK of a synthetic PA receipt directly (bypassing
        # ``exclude_synthesized_pa_receipts`` at query construction), the
        # adapter refuses to normalize the row into an ``EvalRunContext``.
        # Predicate mirrors the filter in :func:`exclude_synthesized_pa_receipts`.
        input_data = row.input_data or {}
        if (
            row.parent_object_type == "deliverable_factory"
            and isinstance(input_data, dict)
            and input_data.get("source") == "deliverable_factory.synthesized_pa_receipt"
        ):
            raise ValueError(
                f"AgentExecution {primary_row_id!r} is a synthesized PA "
                "receipt (canon_v2 Item 4 forbid). Filter with "
                "exclude_synthesized_pa_receipts() at query construction."
            )

        # Native tool-call evidence — the authoritative source for
        # ``AgentExecution`` substrates. ``output_data`` is a JSONField, so
        # ``tool_calls`` may be absent, ``None``, or a list. Coerce to a
        # concrete list before enumerating.
        output_data = row.output_data or {}
        native_tool_calls = output_data.get("tool_calls") or []
        if not isinstance(native_tool_calls, list):
            native_tool_calls = []

        evidence_refs: list[dict[str, Any]] = [
            {
                "kind": "agent_execution_tool_call",
                "index": idx,
                "tool": (call.get("tool") if isinstance(call, dict) else None),
            }
            for idx, call in enumerate(native_tool_calls)
        ]

        # Best-effort ToolCallRecord join for cross-substrate portability.
        # ``trace_id`` on ``AgentExecution`` is populated; ``trace_id`` on
        # ``ToolCallRecord`` is 100% NULL as of S2965 (Ledger #20), so this
        # join reliably returns zero rows. Kept in place because the join
        # becomes live the moment #20 is fixed — no adapter change needed.
        if row.trace_id is not None:
            ledger_ids = list(
                ToolCallRecord.objects.filter(trace_id=row.trace_id).values_list(
                    "id", flat=True
                )
            )
            for tcr_id in ledger_ids:
                evidence_refs.append(
                    {"kind": "tool_call_record", "id": str(tcr_id)}
                )

        # ``finalized_at`` is only meaningful when the row has reached a
        # terminal status; mid-flight rows leave it ``None`` so validators
        # can defer or skip rather than treat a still-running row as failed.
        finalized_at = (
            row.completed_at if row.status in _FINALIZED_STATUSES else None
        )

        return EvalRunContext(
            substrate_type=self.substrate_type,
            primary_row_id=str(row.id),
            evidence_ledger_refs=evidence_refs,
            finalized_at=finalized_at,
            latency_ms=(row.execution_time_ms if self.include_latency else None),
            evidence_source=EVIDENCE_AGENT_EXECUTION_NATIVE,
            # Native tool-call array is always trustworthy for finalized
            # rows; ledger health is only relevant to secondary joins.
            ledger_health=(
                LEDGER_HEALTH_OK if finalized_at is not None
                else LEDGER_HEALTH_UNAVAILABLE
            ),
        )
