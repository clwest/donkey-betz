"""
Ops-autopilot pricing table — SCOPED to enforcement_report savings estimation.

Do NOT use for billing. LLMCallLog.cost is the authoritative per-call cost
ledger; this module exists only so workspace_budget_tool.enforcement_report
can estimate "what would this have cost at the pre-downgrade model" without
duplicating pricing math inline in the handler.

Why this module is not the canonical price table:
- core/llm_enforcer.py:606-627 has inline pricing for gpt-5.2 (with cached
  input discount) — this is the site that actually records LLMCallLog.cost
  on every real API call.
- core/llm_enforcer.py:697-701 has inline pricing for gpt-5-mini used by
  the InterviewAssistant / _calculate_cost path.
- core/agents/base_agent.py:2592-2593 has DIVERGENT gpt-5-mini pricing
  ($3.00/$12.00 per 1M — 6x higher than llm_enforcer). Legacy estimator
  on a non-billing code path; reconciling all three sites to a true
  single-source MODEL_PRICES table is a separate refactor arc, deferred
  from S2853.

For this module, gpt-5-mini values are pulled from llm_enforcer.py:697-701
because that entry lives alongside the gpt-5.2 billing lineage in the
same file — a weaker provenance than "canonical", but a coherent one for
the ops-autopilot subsystem's scoped needs.
"""

from decimal import Decimal
from typing import Dict, Optional

# Per 1M tokens, USD. Decimal so callers can mix with LLMCallLog.cost
# (which is DecimalField) without float-drift creating negative savings.
MODEL_PRICES: Dict[str, Dict[str, Decimal]] = {
    'gpt-5.2': {
        'input': Decimal('1.75'),
        'output': Decimal('14.00'),
        'cached_input': Decimal('0.18'),
    },
    'gpt-5-mini': {
        'input': Decimal('0.50'),
        'output': Decimal('1.50'),
    },
}

_ONE_MILLION = Decimal('1000000')


def estimate_uncached_cost(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> Optional[Decimal]:
    """
    Return uncached USD cost estimate for (prompt_tokens, completion_tokens)
    at model_id's per-1M rates, or None if model_id is not in MODEL_PRICES.

    Uncached math only. LLMCallLog does not store historical cached_tokens,
    so the caller cannot reconstruct cache-adjusted "would have cost" for
    prior calls; the resulting overestimate is honest and stable.
    """
    prices = MODEL_PRICES.get(model_id)
    if prices is None:
        return None
    prompt = Decimal(int(prompt_tokens or 0))
    completion = Decimal(int(completion_tokens or 0))
    return (
        prompt * prices['input'] / _ONE_MILLION
        + completion * prices['output'] / _ONE_MILLION
    )
