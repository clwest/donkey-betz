"""Session 2964: Golden Evals validator harness (canon_v2 ratified S2963).

The harness executes ``evals/tier1/*.yaml`` slices against real runtime
substrates, records results into ``core.GoldenEvalRun``, and provides the
foundation for the S2965+ pass-rate drift dashboard.

Canon_v2 items bound in this foundation:
    * Item 1 — orm_inspect_tool allowlist extension for ChatConversation +
      ToolCallRecord (ships alongside this package in the same PR at
      ``core/services/td_handlers_agents.py``).
    * Item 6 — ``EvalRunContext`` is the canonical evidence abstraction all
      validators consume; per-substrate adapters normalize substrate-native
      rows into this shape.

See ``docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md`` for the full
ratification record.
"""

from .context import (
    KNOWN_SUBSTRATES,
    SUBSTRATE_AGENT_EXECUTION,
    SUBSTRATE_CHAT_CONVERSATION,
    EvalRunContext,
)

__all__ = [
    "EvalRunContext",
    "KNOWN_SUBSTRATES",
    "SUBSTRATE_AGENT_EXECUTION",
    "SUBSTRATE_CHAT_CONVERSATION",
]
