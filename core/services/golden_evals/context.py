"""EvalRunContext + substrate-type constants.

Canonical evidence abstraction for the Golden Evals validator harness. All
validators consume ``EvalRunContext`` instances instead of substrate-native
rows so future substrates can be added without a per-validator ``if/else``
tree.

**Zoom-out guardrail (Rigby S2964 T1 SIGN Q5 REVISE):** substrate identity
is expressed as module-level constants — never as ad-hoc strings — so YAML
loaders, adapter registries, and ``GoldenEvalRun.substrate_type`` writes
all agree by definition rather than by convention. Adding a new substrate
requires (1) adding the constant here, (2) adding it to
``KNOWN_SUBSTRATES``, (3) shipping an adapter that binds to the constant.
The loader validates YAML substrate declarations against ``KNOWN_SUBSTRATES``.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# Substrate identity constants. Canon_v2 items 2 + 6 assume both current
# substrates; new substrates go here first.
SUBSTRATE_AGENT_EXECUTION = "agent_execution"
SUBSTRATE_CHAT_CONVERSATION = "chat_conversation"

KNOWN_SUBSTRATES: frozenset[str] = frozenset(
    {
        SUBSTRATE_AGENT_EXECUTION,
        SUBSTRATE_CHAT_CONVERSATION,
    }
)


@dataclass
class EvalRunContext:
    """Normalized shape for one substrate observation.

    Per canon_v2 Item 6, every substrate adapter yields ``EvalRunContext``
    instances. Validators are written against this shape and are ignorant of
    which substrate produced the observation. Fields:

    substrate_type:
        Must be a member of :data:`KNOWN_SUBSTRATES`. Adapters set this
        from their class-level identity, not from strings.

    primary_row_id:
        Substrate-native PK. For ``AgentExecution`` this is a UUID string;
        for ``ChatConversation`` this is the integer PK cast to string.
        Blank string ``""`` allowed when the harness runs in ``--dry-run``
        mode and no substrate row was produced.

    evidence_ledger_refs:
        List of typed dicts identifying auxiliary rows the adapter joined
        as evidence. Shape:
        ``[{"kind": "tool_call_record", "id": "..."}, ...]``.
        Empty list allowed.

    finalized_at:
        Substrate finalization timestamp when the row's state is stable.
        ``None`` when the substrate row is still in a mutable phase
        (e.g., ``ChatConversation`` pre-response) — validators use this
        signal to defer or skip mid-flight rows rather than treat them as
        failed.

    latency_ms:
        Opt-in latency evidence per canon_v2 Item 3. Only populated when
        the slice YAML declares latency as an evidence dimension. Absence
        (``None``) means "not observed" for this slice, not "zero".
    """

    substrate_type: str
    primary_row_id: str
    evidence_ledger_refs: list[dict[str, Any]] = field(default_factory=list)
    finalized_at: datetime | None = None
    latency_ms: int | None = None

    def __post_init__(self) -> None:
        if self.substrate_type not in KNOWN_SUBSTRATES:
            raise ValueError(
                f"substrate_type={self.substrate_type!r} not in KNOWN_SUBSTRATES "
                f"{sorted(KNOWN_SUBSTRATES)}. Add it to context.py first, then "
                "ship an adapter that binds to the constant."
            )
