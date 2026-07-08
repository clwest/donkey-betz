"""Documentation Manager daily routine — Celery task + facade
(Session 1256 PR 1.2).

This module is a **thin facade** in front of the
MissionRunner-driven Documentation Manager job. The job-specific
"what" lives in ``core.jobs.docs_cascade`` (step functions, probes,
drift observation, escalation body, PA post hook). The mission
lifecycle "how" — OpsRun creation, OpsRunEvent timeline emission,
idempotency, error-signature classification, escalation create-or-
append, completed→ready audit transition, verdict emission, shift-
report dispatch — lives in
``core.employees.mission_runner.MissionRunner``.

Pre-1.2 behavior is preserved exactly: same task name, run_kind,
event labels (incl. the singular ``step_5_drift_observed`` /
``step_5_skipped`` events emitted from postflight), summary keys,
verdict + confidence selection, escalation Deliverable shape +
audit transition, PA escalation post, shift-report DM.

Re-exports at the bottom preserve test-import paths from the pre-1.2
module layout so existing tests keep their import lines without
touching assertions.
"""

from __future__ import annotations

import logging
from typing import Any

from celery import shared_task

# ── Test-import facade re-exports ────────────────────────────────────
#
# Existing tests import various helpers + constants from this module.
# PR 1.2 keeps the imports working by re-exporting from their new
# homes. New code should import from the new modules directly.

from core.employees.mission_runner import (
    MissionRunner,
    ERROR_TAIL_LINES_FIRST,
    ERROR_TAIL_LINES_RECURRENCE,
    _tail_lines,
)
from core.jobs.docs_cascade import (
    DRIFT_LABEL,
    MISSION_RUN_KIND,
    _emit_event,
    _probe_documents_count,
    _probe_embeddings_count,
    _probe_docs_indexed_count,
    _run_drift_observation,
    build_docs_manager_runner,
    post_pa_escalation as _post_pa_escalation_hook,
)

logger = logging.getLogger(__name__)


def _signature_for(failed_step: str, error_tail: str) -> str:
    """Backward-compat wrapper for the error-signature classifier.

    Real implementation: ``MissionRunner.make_error_signature``.
    Preserved so existing tests can keep their
    ``from core.tasks_documentation_manager import _signature_for``.
    """
    return MissionRunner.make_error_signature(failed_step, error_tail)


def _force_deliverable_ready(
    deliverable_id: Any,
    *,
    ops_run_id: Any,
    error_signature: str,
) -> None:
    """Backward-compat wrapper for the audited completed→ready flip.

    Real implementation: ``MissionRunner._force_deliverable_ready``
    with ``emit_audit_event=True``. Preserved for test compatibility
    — the input-validation contract matches (empty ``error_signature``
    or null ``ops_run_id`` raises ``ValueError``).
    """
    if not error_signature:
        raise ValueError(
            "_force_deliverable_ready requires a non-empty "
            "error_signature so the audit row is queryable."
        )
    if not ops_run_id:
        raise ValueError(
            "_force_deliverable_ready requires a non-null ops_run_id "
            "so the audit row links back to the MissionRun."
        )
    runner = build_docs_manager_runner()
    runner._force_deliverable_ready(
        deliverable_id,
        ops_run_id=ops_run_id,
        error_signature=error_signature,
        emit_audit_event=True,
    )


# ── Celery task entry point ──────────────────────────────────────────


@shared_task(
    bind=True,
    name="rigby_documentation_manager_daily",
    soft_time_limit=2700,    # 45min soft cap
    time_limit=3000,         # 50min hard kill
    acks_late=False,         # match process_pa_chat_task
    ignore_result=False,
)
def rigby_documentation_manager_daily(self, force: bool = False) -> dict:
    """Run Rigby's Documentation Manager daily routine end-to-end.

    Thin Celery wrapper around the MissionRunner-driven docs cascade.
    Idempotent within the same calendar day (handled by MissionRunner).

    Args:
        force: Cycle 1A KFI-4 (ADR-0140 §2.1 (5)) — when True, bypass
            the MissionRunner hash-delta preflight and always run the
            full cascade pipeline. This ``force`` is orthogonal to
            ``core.tasks.refresh_docs_corpus(force=...)`` — the two
            tasks live on distinct entry points, distinct cache keys,
            and distinct semantics. This ``force`` means ONLY
            "bypass MissionRunner preflight step in the docs-manager
            factory."

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
    runner = build_docs_manager_runner(force=force)
    result = runner.run()
    return result.as_dict()


__all__ = [
    # Celery task
    "rigby_documentation_manager_daily",
    # Test-facade re-exports
    "MISSION_RUN_KIND",
    "DRIFT_LABEL",
    "ERROR_TAIL_LINES_FIRST",
    "ERROR_TAIL_LINES_RECURRENCE",
    "_tail_lines",
    "_signature_for",
    "_force_deliverable_ready",
    "_emit_event",
    "_probe_documents_count",
    "_probe_embeddings_count",
    "_probe_docs_indexed_count",
    "_run_drift_observation",
    "build_docs_manager_runner",
]
