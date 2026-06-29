"""Platform Auditor task (Session 1257 PR 2.2).

Thin Celery wrapper around the MissionRunner-driven Platform Audit
job. All job-specific logic (step functions, escalation formatter,
shift-report wrapper, audit-report Deliverable builder) lives in
``core.jobs.platform_audit``; mission lifecycle is owned by
``core.employees.mission_runner.MissionRunner``.

The task name ``platform_auditor_run`` is the identifier referenced
by:
  * ``core/celery.py`` ``app.conf.imports`` (worker boot)
  * ``core/services/td_handlers_employee._RUN_NOW_TASKS`` (PA tool
    ``employee_tool action=run_now`` dispatch)
  * Future PeriodicTask migration in PR 2.3 (beat schedule)

PR 2.2 deliberately ships **no beat schedule** — the task is callable
manually via ``employee_tool action=run_now employee=platform_auditor
job=platform_audit`` and via the Celery shell. The cron + beat
schedule lands in PR 2.3.
"""

from __future__ import annotations

import logging

from celery import shared_task

from core.jobs.platform_audit import build_platform_audit_runner

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="platform_auditor_run",
    # Bound generously — the audit cascade is read-only DB queries +
    # file reads. Real cost should be < 30s. Soft + hard limits match
    # the docs_cascade task to keep mission lifecycle uniform.
    soft_time_limit=2700,    # 45min soft cap
    time_limit=3000,         # 50min hard kill
    acks_late=False,         # match process_pa_chat_task + docs cascade
    ignore_result=False,
)
def platform_auditor_run(self) -> dict:
    """Run the Platform Auditor mission end-to-end.

    Thin Celery wrapper around the MissionRunner-driven Platform Audit
    cascade. Idempotent within the same calendar day (MissionRunner
    handles daily idempotency).

    Returns the result envelope as a JSON-safe dict:
        {
            ok: bool,
            mission_id: str,
            status: str,
            verdict: Optional[str],
            wall_time_ms: int,
            summary: dict,
            already_ran: bool,
        }
    """
    runner = build_platform_audit_runner()
    result = runner.run()
    return result.as_dict()


__all__ = ["platform_auditor_run"]
