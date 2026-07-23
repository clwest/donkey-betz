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
    # Seeded tools intentionally empty for T1a Phase 1 ship. Population lands
    # incrementally as sweep sessions author metadata alongside per-tool
    # validation docs (T1b template will include an authoring hook).
}


# ── Per-(tool, action) records ──────────────────────────────────────────────
#
# T1a Phase 1 seed: two records against ``ops_tool`` verified live at S2796
# (per T1c §7.1). Everything else defaults to SKIP so the first live run
# proves the pipeline end-to-end without exercising handlers that have
# unknown safety.

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
