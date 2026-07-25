"""EvalRunContext + substrate/evidence/health constants.

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

**Evidence-source + ledger-health signals (Rigby S2965 T1 SIGN A2 REVISE):**
S2965 raw-ORM verification found that ``ToolCallRecord`` — the canonical
tool-call evidence ledger — has (a) zero rows with
``agent_name='PersonalAssistant'`` in the last 30d (last written
2026-06-19, 35d silent write regression), and (b) ``trace_id=NULL`` on
100% of 5,430 rows (the join key that ``rigby_agent.yaml``
``canonical_field_mapping`` §evidence_pointers depends on has never been
populated). To ship the harness end-to-end without pretending the ledger
is healthy, adapters explicitly label ``evidence_source`` (ledger vs
metadata_cache vs agent_execution_native) and report ``ledger_health``,
and Rigby-specific ``no_fabricated_*`` predicates gate on
``ledger_health=OK`` — returning ``INCONCLUSIVE_SUBSTRATE_BROKEN`` rather
than a false pass/fail against a broken audit trail. See Rigby Tool Gap
Ledger #20 + #21 for the underlying regression.
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


# Evidence-source constants. Records WHERE the adapter drew tool-call
# evidence from — the ledger, a convenience cache on the substrate row
# itself, or the substrate-native output. Introduced at S2965 PR-2 T1
# SIGN after raw-ORM discovery that ``ToolCallRecord`` has zero rows for
# ``agent_name='PersonalAssistant'`` in the last 30 days (35d silent
# PA write regression starting 2026-06-19) and 100% NULL ``trace_id``
# across all 5,430 rows. Rigby-specific ``no_fabricated_*`` predicates
# MUST gate on ``ledger_health`` before drawing conclusions from
# ``metadata_cache`` evidence — the cache is a convenience mirror, not
# an authoritative audit trail.
EVIDENCE_LEDGER = "toolcallrecord_ledger"
EVIDENCE_METADATA_CACHE = "metadata_cache"
EVIDENCE_AGENT_EXECUTION_NATIVE = "agent_execution_native"

KNOWN_EVIDENCE_SOURCES: frozenset[str] = frozenset(
    {
        EVIDENCE_LEDGER,
        EVIDENCE_METADATA_CACHE,
        EVIDENCE_AGENT_EXECUTION_NATIVE,
    }
)


# Ledger-health signals. Consumed by Rigby-specific predicates
# (``no_fabricated_tool_runs``, ``detects_and_surfaces_tool_runs_empty_vs_claimed``)
# to decide whether to pass/fail or return an ``INCONCLUSIVE`` verdict.
# Foundational assumption: "fabrication" claims MUST NOT be made against
# a broken evidence substrate (would silently generate false positives).
LEDGER_HEALTH_OK = "ok"
LEDGER_HEALTH_STALE = "stale"        # ledger exists but has not been written for the observed window
LEDGER_HEALTH_UNAVAILABLE = "unavailable"  # ledger structurally unavailable for the substrate

KNOWN_LEDGER_HEALTH: frozenset[str] = frozenset(
    {
        LEDGER_HEALTH_OK,
        LEDGER_HEALTH_STALE,
        LEDGER_HEALTH_UNAVAILABLE,
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

    evidence_source:
        Where the adapter drew tool-call evidence from. Member of
        :data:`KNOWN_EVIDENCE_SOURCES`. Introduced at S2965 PR-2 T1 SIGN
        (Rigby A2 REVISE) after raw-ORM discovery that ``ToolCallRecord``
        writes silently regressed 35d ago for ``PersonalAssistant`` and
        that ``trace_id`` has never been populated. Predicates that assert
        fabrication invariants MUST inspect this + ``ledger_health`` before
        pass/fail — evidence from ``EVIDENCE_METADATA_CACHE`` cannot ground
        the same fabrication claim as ``EVIDENCE_LEDGER``.

    ledger_health:
        Signal to downstream predicates about whether the ledger evidence
        source is trustworthy for the observation window. Member of
        :data:`KNOWN_LEDGER_HEALTH`. Rigby-specific fabrication predicates
        return ``INCONCLUSIVE_SUBSTRATE_BROKEN`` when this is
        ``LEDGER_HEALTH_STALE`` or ``LEDGER_HEALTH_UNAVAILABLE`` rather
        than pass/fail against sand.
    """

    substrate_type: str
    primary_row_id: str
    evidence_ledger_refs: list[dict[str, Any]] = field(default_factory=list)
    finalized_at: datetime | None = None
    latency_ms: int | None = None
    evidence_source: str = EVIDENCE_AGENT_EXECUTION_NATIVE
    ledger_health: str = LEDGER_HEALTH_OK

    def __post_init__(self) -> None:
        if self.substrate_type not in KNOWN_SUBSTRATES:
            raise ValueError(
                f"substrate_type={self.substrate_type!r} not in KNOWN_SUBSTRATES "
                f"{sorted(KNOWN_SUBSTRATES)}. Add it to context.py first, then "
                "ship an adapter that binds to the constant."
            )
        if self.evidence_source not in KNOWN_EVIDENCE_SOURCES:
            raise ValueError(
                f"evidence_source={self.evidence_source!r} not in "
                f"KNOWN_EVIDENCE_SOURCES {sorted(KNOWN_EVIDENCE_SOURCES)}."
            )
        if self.ledger_health not in KNOWN_LEDGER_HEALTH:
            raise ValueError(
                f"ledger_health={self.ledger_health!r} not in "
                f"KNOWN_LEDGER_HEALTH {sorted(KNOWN_LEDGER_HEALTH)}."
            )
