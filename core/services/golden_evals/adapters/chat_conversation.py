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

from django.db.models import QuerySet

from ..context import SUBSTRATE_CHAT_CONVERSATION, EvalRunContext
from .base import SubstrateAdapter


BUYER_FACING_SOURCES: tuple[str, ...] = ("web", "pa")


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
    """Normalize ``core.ChatConversation`` rows to :class:`EvalRunContext`."""

    substrate_type = SUBSTRATE_CHAT_CONVERSATION

    def __init__(self, sources: tuple[str, ...] = BUYER_FACING_SOURCES) -> None:
        self.sources = sources

    def build_context(self, primary_row_id: str) -> EvalRunContext:
        # Skeleton implementation (S2964 PR-1 foundation):
        # PR-2 will read the ChatConversation row, apply the source filter
        # (via ``filter_to_buyer_facing_sources`` above), enumerate
        # ToolCallRecord rows joined by trace_id + created_at window,
        # detect Shape A vs Shape B metadata (async-callback vs
        # sync-dispatch, per rigby_agent.yaml §90 canonical_field_mapping),
        # derive finalized_at from response completion, and (opt-in)
        # populate latency_ms from response_time_ms per canon_v2 Item 3.
        return EvalRunContext(
            substrate_type=self.substrate_type,
            primary_row_id=primary_row_id,
            evidence_ledger_refs=[],
            finalized_at=None,
            latency_ms=None,
        )
