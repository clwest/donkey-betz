"""Chief of Staff Morning Brief task (Session 1257 PR 3.2;
production-promoted Session 1258 PR 3.3).

Thin Celery wrapper around the MissionRunner-driven Chief of Staff
mission. All job-specific logic (the wrapper step that calls the
existing workflow, scalar-only summary extraction, postflight
brief_chars derivation, CoS-flavored escalation body formatter) lives
in ``core.jobs.morning_brief``; mission lifecycle is owned by
``core.employees.mission_runner.MissionRunner``.

The task name ``chief_of_staff_morning_brief_run`` is the identifier
referenced by:
  * ``core/celery.py`` ``app.conf.imports`` (worker boot)
  * ``core/services/td_handlers_employee._RUN_NOW_TASKS`` (PA tool
    ``employee_tool action=run_now`` dispatch)
  * ``core/celery.py`` beat schedule entry ``generate-morning-brief-daily``
    (production beat target since S1258 PR 3.3)

PR 3.2 shipped the wrapper without a beat schedule and left the
legacy ``core.tasks.generate_morning_brief_daily`` as the daily beat
target so production fires continued unaffected. PR 3.3 (this PR)
flips the beat row's ``task`` field to
``chief_of_staff_morning_brief_run`` and removes the legacy task
module. From S1258 onward, the 07:00 Denver fire executes via
MissionRunner.

Fail-loud contract: unlike Platform Auditor (PR 2.2), this wrapper
**re-raises on ``result.ok=False``** so the CeleryTaskEvent row
records FAILURE alongside the escalation Deliverable. Matches the
Session 1234 D1 fail-loud pattern carried forward from the deleted
``core.tasks.generate_morning_brief_daily`` — belt + suspenders. The
escalation Deliverable is the human-readable failure surface; the
re-raise keeps Celery observability honest. See discovery
deliverable ``2983377c-08e3-44e6-aeef-cfcf742ae4cd`` § Risk R2 +
Section 12 (PR 3.2) and ``cc4c0641-c361-4c19-a1db-a6ccfa92b281``
(PR 3.3 discovery).
"""

from __future__ import annotations

import logging

from celery import shared_task

from core.jobs.morning_brief import build_chief_of_staff_runner

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="chief_of_staff_morning_brief_run",
    # Generous bounds — the underlying workflow runs 5+ sub-agent LLM
    # calls (3 lane syntheses + Decision Card + strategic synthesis).
    # Legacy task uses soft_time_limit=900 / time_limit=1080 (15/18
    # min); CoS wrapper uses the same so behavior matches and the
    # mission row keeps shape parity with docs_cascade /
    # platform_audit. Real cost typically 5-12 minutes.
    soft_time_limit=900,
    time_limit=1080,
    acks_late=False,
    ignore_result=False,
)
def chief_of_staff_morning_brief_run(self) -> dict:
    """Run the Chief of Staff Morning Brief mission end-to-end.

    Thin Celery wrapper around the MissionRunner-driven brief
    cascade. Idempotent within the same calendar day (MissionRunner
    handles daily idempotency via the
    ``(domain='mission', run_kind='morning_brief', started_at__date)``
    lookup in ``_existing_mission_for_today``).

    On ``result.ok=False``: emits a greppable
    ``[CHIEF_OF_STAFF_BRIEF_FAILED]`` log line and re-raises so the
    CeleryTaskEvent row records FAILURE. The escalation Deliverable
    has already been created by MissionRunner at this point —
    re-raising adds the second failure surface (Celery row), not
    duplicate ones.

    Returns (on success) the result envelope as a JSON-safe dict:
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
    runner = build_chief_of_staff_runner()
    result = runner.run()

    if not result.ok:
        # Fail-loud — Session 1234 D1 pattern carried forward from
        # the deleted core.tasks.generate_morning_brief_daily.
        logger.error(
            "[CHIEF_OF_STAFF_BRIEF_FAILED] task_id=%s mission_id=%s "
            "status=%s verdict=%s wall_time_ms=%s summary=%s",
            self.request.id,
            result.mission_id,
            result.status,
            result.verdict,
            result.wall_time_ms,
            result.summary,
        )
        raise RuntimeError(
            f"Chief of Staff Morning Brief mission failed: "
            f"mission_id={result.mission_id} status={result.status} "
            f"verdict={result.verdict}. See escalation Deliverable for "
            "full evidence."
        )

    return result.as_dict()


__all__ = ["chief_of_staff_morning_brief_run"]
