"""
Canonical LLM per-token pricing catalog.

Single source of truth for per-1M-token USD rates used by every billing path
that writes ``LLMCallLog.cost`` or ``CostTracking.estimated_cost_usd``:

Billing plane (``LLMCallLog``):
- ``core/llm_enforcer.py`` (``_call_openai_v2`` gpt-5.2 path, ``_calculate_cost``
  gpt-5-mini helper, and ``_call_claude`` Anthropic path)
- ``core/services/llm_provider_registry.py`` (every provider's
  ``_calculate_cost`` — OpenAI / Anthropic / DeepSeek / Together / Gemini)
- ``core/services/ops_autopilot/pricing.py`` (re-exports from here; retained
  as a thin scoped-import compatibility shim for existing callers)

Analytics plane (``CostTracking``) — S2855 Phase 2A:
- ``core/agents/base_agent.py::_call_openai`` accumulated cost + return dict
  ``cost`` field (previously hardcoded $3/$12 per 1M; matched neither model)
- ``core/agents/base_agent.py::_track_llm_analytics`` per-user CostTracking
  write (previously hardcoded service='gpt-5-mini' + same wrong rates)

Display fallback estimators — S2855 Phase 2A:
- ``core/views_agent_dashboard.py::agent_costs_data`` (when
  ``AgentExecution.cost`` aggregate is null; response labels ``estimated:true``)
- ``core/views_analytics.py::cost_breakdown`` (agent-execution rollup card
  from ``AgentTaskExecution.tokens_used``; response labels ``estimated:true``)

Embedding pricing is NOT in this catalog — see
``core/services/embedding_service.EMBEDDING_COSTS`` for the canonical
embedding-rate table (text-embedding-3-small / -3-large / -ada-002).
``core/management/commands/triage_spider_embeddings.py`` imports from there
directly rather than duplicating rates.

DB-side ``LLMModel.cost_per_1m_input`` / ``cost_per_1m_output`` rows are kept for
admin/display parity but are treated as consumers of this Python authority;
seed data in ``models_llm_routing.DEFAULT_MODELS`` mirrors this table, and a
one-time data migration realigns any existing rows.

Decimal-typed throughout so callers that mix with ``LLMCallLog.cost`` (a
``DecimalField``) don't accrete float drift. Callers on the billing hot path
today expect ``float``; convert at the write boundary via ``float(...)``.
"""

from decimal import Decimal
from typing import Dict, Optional

# Per 1M tokens, USD. Rates align to the operational billing lineage as of
# S2854 (2026-07-20): the ``llm_enforcer._call_openai_v2`` / ``_calculate_cost``
# helpers are the site that has consistently produced the small number of
# real ``LLMCallLog.cost`` rows in production. Provider-registry inline
# tables previously diverged (gpt-5.2 $5.00/$20.00; gpt-5-mini $0.15/$0.60);
# they are aligned to the enforcer's values here.
#
# If OpenAI publishes a rate change, update THIS table + re-run
# ``python manage.py setup_llm_routing --sync-prices`` to backfill DB rows.
MODEL_PRICES: Dict[str, Dict[str, Decimal]] = {
    # ---- OpenAI ----
    'gpt-5.2': {
        'input': Decimal('1.75'),
        'output': Decimal('14.00'),
        'cached_input': Decimal('0.18'),
    },
    'gpt-5.1': {
        'input': Decimal('1.25'),
        'output': Decimal('10.00'),
    },
    'gpt-5-mini': {
        'input': Decimal('0.50'),
        'output': Decimal('1.50'),
    },
    'gpt-4-turbo': {
        'input': Decimal('10.00'),
        'output': Decimal('30.00'),
    },
    'gpt-4o': {
        'input': Decimal('2.50'),
        'output': Decimal('10.00'),
    },
    'gpt-4o-mini': {
        'input': Decimal('0.15'),
        'output': Decimal('0.60'),
    },

    # ---- Anthropic ----
    'claude-3.5-sonnet': {
        'input': Decimal('3.00'),
        'output': Decimal('15.00'),
    },
    'claude-3.5-haiku': {
        'input': Decimal('0.25'),
        'output': Decimal('1.25'),
    },
    'claude-3.5-opus': {
        'input': Decimal('15.00'),
        'output': Decimal('75.00'),
    },
    'claude-3-sonnet-20240229': {
        'input': Decimal('3.00'),
        'output': Decimal('15.00'),
    },
    # Haiku split rates. Pre-S2854 the enforcer applied a single blended
    # $0.25/1M to total tokens, silently under-charging every Claude call
    # (output tokens should charge 5x input).
    'claude-3-haiku-20240307': {
        'input': Decimal('0.25'),
        'output': Decimal('1.25'),
    },
    # Session 2846 baseline uses this ID from LLMProviderRegistry seed.
    'claude-3-haiku': {
        'input': Decimal('0.25'),
        'output': Decimal('1.25'),
    },

    # ---- DeepSeek ----
    'deepseek-coder': {
        'input': Decimal('0.14'),
        'output': Decimal('0.28'),
    },
    'deepseek-chat': {
        'input': Decimal('0.07'),
        'output': Decimal('0.14'),
    },

    # ---- Together AI (hosted OSS) ----
    'deepseek-ai/deepseek-coder-33b-instruct': {
        'input': Decimal('0.80'),
        'output': Decimal('0.80'),
    },
    'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo': {
        'input': Decimal('0.88'),
        'output': Decimal('0.88'),
    },
    'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo': {
        'input': Decimal('0.18'),
        'output': Decimal('0.18'),
    },
    'mistralai/Mixtral-8x7B-Instruct-v0.1': {
        'input': Decimal('0.60'),
        'output': Decimal('0.60'),
    },
    'Qwen/Qwen2.5-Coder-32B-Instruct': {
        'input': Decimal('0.80'),
        'output': Decimal('0.80'),
    },

    # ---- Gemini ----
    'gemini-2.0-flash': {
        'input': Decimal('0.075'),
        'output': Decimal('0.30'),
    },
    'gemini-2.5-flash': {
        'input': Decimal('0.075'),
        'output': Decimal('0.30'),
    },
    'gemini-2.0-pro': {
        'input': Decimal('1.25'),
        'output': Decimal('5.00'),
    },
    'gemini-2.5-pro': {
        'input': Decimal('1.25'),
        'output': Decimal('5.00'),
    },
    'gemini-pro': {
        'input': Decimal('0.50'),
        'output': Decimal('1.50'),
    },
}

# Per-provider fallback used when a caller passes a model_id we don't have
# a table entry for. Chosen to over-estimate (fail loud in dashboards) rather
# than silently under-charge. Applied only via ``calculate_cost`` — direct
# ``get_model_pricing`` returns None for unknown models.
_UNKNOWN_MODEL_FALLBACK: Dict[str, Decimal] = {
    'input': Decimal('1.00'),
    'output': Decimal('3.00'),
}

_ONE_MILLION = Decimal('1000000')


def get_model_pricing(model_id: str) -> Optional[Dict[str, Decimal]]:
    """
    Return the per-1M-token rate dict for ``model_id``, or None if unknown.

    Keys always present: ``input``, ``output``. Key ``cached_input`` present
    only when the model exposes a cache-hit discount (currently gpt-5.2).
    """
    return MODEL_PRICES.get(model_id)


def calculate_cost(
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
) -> Decimal:
    """
    Return total USD cost as Decimal for the given (model_id, token counts).

    - ``input_tokens`` are treated as UNCACHED billable input. Callers with
      cache-hit accounting (e.g. the enforcer) MUST subtract cached tokens
      before passing them in, then pass the cached-tokens count via
      ``cached_input_tokens`` so this function can price them at the model's
      cached-input rate.
    - If the model has no ``cached_input`` rate in its table but the caller
      passed ``cached_input_tokens > 0``, they are billed at the standard
      ``input`` rate (no silent discount).
    - Unknown models bill at ``_UNKNOWN_MODEL_FALLBACK`` rates and log
      nothing — callers wanting fail-loud behavior should combine with
      ``get_model_pricing(model_id) is None`` upstream.
    """
    prices = MODEL_PRICES.get(model_id) or _UNKNOWN_MODEL_FALLBACK

    input_d = Decimal(int(input_tokens or 0))
    output_d = Decimal(int(output_tokens or 0))
    cached_d = Decimal(int(cached_input_tokens or 0))

    cached_rate = prices.get('cached_input', prices['input'])
    return (
        input_d * prices['input'] / _ONE_MILLION
        + output_d * prices['output'] / _ONE_MILLION
        + cached_d * cached_rate / _ONE_MILLION
    )


def estimate_uncached_cost(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> Optional[Decimal]:
    """
    Backward-compat shim for ``core/services/ops_autopilot/pricing.py`` callers.

    Returns None if the model isn't in the canonical table (preserves the
    existing "estimator skips unknown models" contract used by
    ``workspace_budget_tool.enforcement_report`` when computing
    downgrade-savings).
    """
    if model_id not in MODEL_PRICES:
        return None
    return calculate_cost(model_id, prompt_tokens, completion_tokens)
