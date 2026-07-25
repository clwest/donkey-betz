"""Adapter for the ``core.AgentExecution`` substrate.

Handles the 7 Tier-1 slices authored against ``AgentExecution`` rows
(slices 1-7 per the S2963 arc-close table).
"""

from __future__ import annotations

from django.db.models import QuerySet

from ..context import SUBSTRATE_AGENT_EXECUTION, EvalRunContext
from .base import SubstrateAdapter


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
    """Normalize ``core.AgentExecution`` rows to :class:`EvalRunContext`."""

    substrate_type = SUBSTRATE_AGENT_EXECUTION

    def build_context(self, primary_row_id: str) -> EvalRunContext:
        # Skeleton implementation (S2964 PR-1 foundation):
        # PR-2 will read the actual AgentExecution row, apply the receipt
        # filter (via ``exclude_synthesized_pa_receipts`` above), join
        # ToolCallRecord + LLMCallLog evidence via trace_id, derive
        # finalized_at from status + completed_at, and (opt-in per
        # canon_v2 Item 3) populate latency_ms from execution_time_ms.
        return EvalRunContext(
            substrate_type=self.substrate_type,
            primary_row_id=primary_row_id,
            evidence_ledger_refs=[],
            finalized_at=None,
            latency_ms=None,
        )
