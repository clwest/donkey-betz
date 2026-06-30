"""Shared persistence helpers for Employee OS job runners.

When a ``MissionRunner`` step needs to incrementally write findings
into ``OpsRun.summary``, it uses ``_persist_to_summary`` from here.
Each job module (``morning_brief``, ``platform_audit``, ``bug_triage``,
…) calls the same helper so the summary write semantics are guaranteed
identical across all employees.

Lifted from inline definitions in ``core/jobs/morning_brief.py`` and
``core/jobs/platform_audit.py`` at Session 1267 PR 4.0 per Rigby SIGN
decision D6 — the N=4 employee (Bug Triage Specialist) was the
trigger to centralize the pattern that had been duplicated 2x.

Why a shared helper instead of repeating the 3-line body each time:

* One canonical write-pattern → guaranteed JSON-safe + queryable
  semantics across all employees (no nested workflow envelope per
  Rigby S1257 SIGN-WITH-EDITS lock #2).
* Future drift (e.g., switching to ``F()`` expressions, adding
  ``last_summary_write_at`` telemetry, or coalescing concurrent
  writes) lands in one place.

This helper is the step-side complement to ``MissionRunner``'s own
``_persist_summary``: steps write scalar findings keys (per-employee
domain output); the runner later merges runner-level keys
(``wall_time_ms``, ``verdict``, ``failed_step``, ``error_tail``, …)
on top. The two key sets are documented in
``EMPLOYEE_OS_PRIMITIVES.md`` and do not collide.
"""

from __future__ import annotations

from typing import Any


def _persist_to_summary(mission, **fields: Any) -> None:
    """Atomically merge ``fields`` into ``mission.summary``.

    Each scalar field is written individually so the summary stays
    JSON-safe + queryable (no nested workflow envelope per Rigby
    S1257 SIGN-WITH-EDITS lock #2). MissionRunner's own
    ``_persist_summary`` later merges runner-level keys
    (``wall_time_ms``, ``verdict``, ``failed_step``, ``error_tail``,
    …) without overwriting step-written keys — the two key sets
    don't collide.

    Parameters
    ----------
    mission : OpsRun
        The mission row whose ``summary`` JSONField is being written.
        Caller is responsible for ensuring the row already exists.
    **fields : Any
        Keys to merge into ``mission.summary``. Values should be
        JSON-serializable (primitives, dicts, lists). Existing keys
        with the same name are overwritten by the new value.
    """
    existing = mission.summary or {}
    mission.summary = {**existing, **fields}
    mission.save(update_fields=["summary"])
