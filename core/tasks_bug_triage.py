"""Bug Triage Specialist task (Session 1267 PR 4.2).

Thin Celery wrapper around the MissionRunner-driven Daily Bug Triage
job. All job-specific logic (step functions, escalation formatter,
shift-report wrapper, triage-report Deliverable builder, bounded
summary postflight) lives in ``core.jobs.bug_triage``; mission
lifecycle is owned by ``core.employees.mission_runner.MissionRunner``.

The task name ``bug_triage_daily_run`` is the identifier referenced
by:
  * ``core/celery.py`` ``app.conf.imports`` (worker boot)
  * ``core/services/td_handlers_employee._RUN_NOW_TASKS`` (PA tool
    ``employee_tool action=run_now`` dispatch)
  * ``core/migrations/0375_session_1267_seed_bug_triage_beat.py``
    seeds the PeriodicTask row at ``enabled=False`` (PR 4.3 flips it
    to ``enabled=True``).

PR 4.2 ships the task module + migration only. The beat row stays
disabled until PR 4.3 (or admin flip) after ≥1 clean manual run.
"""

from __future__ import annotations

import logging

from celery import shared_task

from core.jobs.bug_triage import build_bug_triage_runner

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="bug_triage_daily_run",
    # Generous bounds — the cascade is read-only ORM queries + a
    # deterministic markdown build. Real cost should be < 90s. Soft +
    # hard limits match the Platform Auditor task to keep mission
    # lifecycle uniform.
    soft_time_limit=2700,    # 45min soft cap
    time_limit=3000,         # 50min hard kill
    acks_late=False,         # match docs cascade + Platform Auditor
    ignore_result=False,
)
def bug_triage_daily_run(self) -> dict:
    """Run the Bug Triage Specialist mission end-to-end.

    Thin Celery wrapper around the MissionRunner-driven Daily Bug
    Triage cascade. Idempotent within the same calendar day
    (MissionRunner handles daily idempotency).

    Returns the result envelope as a JSON-safe dict:

        {
            ok: bool,
            mission_id: str,
            status: str,            # 'passed' / 'failed' / 'partial'
            verdict: Optional[str], # None in v0 — no auto-certification
            wall_time_ms: int,
            summary: dict,
            already_ran: bool,
        }

    The ``verdict`` field is ``None`` because Bug Triage v0 sets
    ``MissionRunnerConfig.auto_emit_verdict=False`` (Rigby SIGN D1).
    Certification lives on Rigby/human's PA tool path which writes
    the actual ``verdict_issued:*`` OpsRunEvent later.
    """
    runner = build_bug_triage_runner()
    result = runner.run()
    return result.as_dict()


__all__ = ["bug_triage_daily_run"]
