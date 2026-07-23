"""Action Metadata Map — per-(tool, action) safety + applicability classification.

Ratified at S2902 (Row 161 substrate arc, T1a Phase 1) via Claude+Rigby joint
SIGN + Chris green-light. Per T1c §8 (Candidate A confirmed): in-code registry
adjacent to ``ToolDispatcher``. Consumed by ``pa_tool_validate_harness``.

Design summary (all four decisions ratified in S2902 SIGN cycle):

- **SafetyClass** — 4 values: ``READ_ONLY / WRITE_GATED / MUTATION / IRREVERSIBLE``.
  ``IRREVERSIBLE`` = cannot be safely run in harness even with owner/staff
  identity or a ``dry_run`` flag (kill switches, non-recoverable deletes).
- **Field set** — 3 fields per action: ``safety_class`` + ``applicability`` +
  ``notes`` (T1c §8 MVP boundary). ``env_required`` deliberately NOT promoted
  to a top-level field — encode env/deps in ``notes`` per convention below.
- **Tool-level defaults** — ``TOOL_DEFAULTS`` lets a tool declare a
  ``default_safety_class`` so obviously-safe read-only surfaces don't need
  per-action metadata authored before the harness can dispatch (mitigates
  the "metadata-debt gating tax" zoom-out concern).
- **Missing metadata** — harness treats unclassified ``(tool, action)`` pairs
  as *skip*, never as WRITE_GATED-dispatch-with-empty-payload. See
  ``resolve_safety`` semantics.

Notes convention (parseable by T1b template extraction):

- ``env: external:<name>``  — action needs an external service (railway, obs, …)
- ``env: local:<key>``      — action needs a local runtime (redis, celery, …)
- ``deps: <handle>``        — action depends on a specific data substrate
- ``gate: <reason>``        — action gated on flag/role/permission
- ``revisit: <trigger>``    — revisit classification when trigger fires

Multiple keys space-separated (``env: external:railway gate: staff``).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional, Tuple


SafetyClass = Literal['READ_ONLY', 'WRITE_GATED', 'MUTATION', 'IRREVERSIBLE']
Applicability = Literal['always', 'conditional', 'gated']


@dataclass(frozen=True)
class ToolActionMetadata:
    """Per-``(tool_name, action)`` classification record."""

    safety_class: SafetyClass
    applicability: Applicability = 'always'
    notes: str = ''


@dataclass(frozen=True)
class ToolDefaults:
    """Tool-level defaults applied when a per-action record is absent.

    Presence of a default does NOT auto-classify every action — the harness
    still requires the action to be enumerated in the tool's schema. Defaults
    cover the "obvious surface" (e.g., a ``ops_tool`` whose read paths are
    uniformly safe) without forcing per-action authoring for every enum value.
    """

    default_safety_class: SafetyClass
    default_applicability: Applicability = 'always'
    notes: str = ''


# ── Tool-level defaults ─────────────────────────────────────────────────────
#
# Seeded conservatively for T1a MVP. Adding a default here is a signed-off
# claim that ALL actions of that tool share the declared safety class. If any
# action of a tool deviates, either (a) remove the tool-level default and
# author per-action records, or (b) override with a specific record in
# ``TOOL_ACTION_METADATA`` (per-action records win over tool defaults).

TOOL_DEFAULTS: Dict[str, ToolDefaults] = {
    # T1a Phase 2 seed (S2903). Four tools authored from validation-doc
    # evidence — every action in each is read-only per its respective
    # validation report. Per-action overrides live in ``TOOL_ACTION_METADATA``
    # below for the ONE deviation (``ops_tool.focus_mode_update``).
    #
    # Authoring evidence:
    # - ops_tool: `docs/research/tools/validation/ops_tool_validation.md` §5
    #   ("All actions are read-only except `focus_mode_update`")
    # - kb_tool: handler at `td_handlers_ops.py:7548` — all 5 actions are
    #   ORM/pgvector queries, no writes
    # - agent_introspection_tool: read-only introspection surface (list,
    #   stats, details, capabilities, tools)
    # - repo_tool: `docs/research/tools/validation/repo_tool_validation.md`
    #   line 3 ("read-only codebase introspection")
    'ops_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: git-head, worker-recycle-log, OpsRun/CeleryTaskEvent',
    ),
    'kb_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: UnifiedEmbedding + DocumentEmbedding (pgvector)',
    ),
    'agent_introspection_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: AGENT_MAP, Agent table, ToolCallRecord',
    ),
    'repo_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: local repo filesystem + git',
    ),
}


# ── Per-(tool, action) records ──────────────────────────────────────────────
#
# T1a Phase 1 seed: two records against ``ops_tool`` verified live at S2796
# (per T1c §7.1). Phase 2 (S2903) extends with:
#   - ``ops_tool.focus_mode_update`` override (WRITE_GATED — the one
#     mutating action in ops_tool per validation doc §5)
#   - ``session_tool`` mixed-safety fan-out (3 READ_ONLY + 4 MUTATION) —
#     tool-level default not usable because the safety class splits per
#     action (verified in ``session_tool_validation.md`` §4 handler trace).

TOOL_ACTION_METADATA: Dict[Tuple[str, str], ToolActionMetadata] = {
    ('ops_tool', 'version'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: git-head; verified live S2796',
    ),
    ('ops_tool', 'recent_recycles'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: worker-recycle-log; verified live S2796',
    ),
    # ops_tool override: everything else is READ_ONLY (via TOOL_DEFAULTS)
    # EXCEPT focus_mode_update, which writes Focus Mode config
    # (`td_handlers_ops.py:317` calls ``set_config`` — a persisted write).
    # Classified WRITE_GATED because the write path exists; harness does not
    # dispatch WRITE_GATED at MVP so no auth-boundary assertion needed. Auth
    # enforcement location not verified at seed time; revisit if/when we add
    # WRITE_GATED harness dispatch.
    ('ops_tool', 'focus_mode_update'): ToolActionMetadata(
        safety_class='WRITE_GATED',
        applicability='conditional',
        notes='writes Focus Mode config; revisit: auth-boundary at harness-dispatch',
    ),
    # session_tool — mixed. Read side classified for harness dispatch;
    # write side flagged for future MUTATION coverage (not exercised at MVP).
    ('session_tool', 'health_check'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ChatConversation; default action per handler',
    ),
    ('session_tool', 'list_recent'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ChatConversation queryset (F-S-3 mitigation shipped S2728)',
    ),
    ('session_tool', 'whoami'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: current conversation binding; provenance surface',
    ),
    ('session_tool', 'create_fresh'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='creates a new ChatConversation row',
    ),
    ('session_tool', 'retire'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='sets session_active=False; F-S-6 mitigation shipped S2728',
    ),
    ('session_tool', 'set_active'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='sets session_active=True on target conversation',
    ),
    ('session_tool', 'seed'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes ChatMessage with [SYSTEM SEED] marker',
    ),
}


# ── Lookup API ──────────────────────────────────────────────────────────────


ResolutionSource = Literal['action', 'tool_default', 'unclassified']


def get_metadata(tool_name: str, action: str) -> Optional[ToolActionMetadata]:
    """Return the per-action record, or ``None`` if unclassified."""
    return TOOL_ACTION_METADATA.get((tool_name, action))


def get_defaults(tool_name: str) -> Optional[ToolDefaults]:
    """Return the tool-level defaults, or ``None`` if none registered."""
    return TOOL_DEFAULTS.get(tool_name)


def resolve_safety(
    tool_name: str, action: str
) -> Tuple[Optional[SafetyClass], ResolutionSource]:
    """Resolve the effective safety class for ``(tool_name, action)``.

    Precedence:
    1. Per-action record in ``TOOL_ACTION_METADATA``  → ``'action'``.
    2. Tool-level default in ``TOOL_DEFAULTS``        → ``'tool_default'``.
    3. Neither present                                → ``(None, 'unclassified')``.

    Returning ``None`` for the safety class is the signal the harness uses to
    skip dispatch entirely (never dispatch-with-empty-payload). This is the
    Q4(a) behavior ratified in the S2902 SIGN cycle.
    """
    rec = TOOL_ACTION_METADATA.get((tool_name, action))
    if rec is not None:
        return rec.safety_class, 'action'
    tool_def = TOOL_DEFAULTS.get(tool_name)
    if tool_def is not None:
        return tool_def.default_safety_class, 'tool_default'
    return None, 'unclassified'


def coverage_stats() -> Dict[str, int]:
    """Return counts by resolution class — feeds the harness "top missing" report."""
    return {
        'per_action_records': len(TOOL_ACTION_METADATA),
        'tool_defaults': len(TOOL_DEFAULTS),
        'tools_with_at_least_one_record': len(
            {t for (t, _) in TOOL_ACTION_METADATA.keys()}
        ),
    }
