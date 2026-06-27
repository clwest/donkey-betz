"""
Session 983: Celery Task Telemetry Signal Handlers

Connects to Celery signals (task_prerun, task_postrun, task_failure) and
writes lightweight CeleryTaskEvent rows for observability.

Import this module in core/celery.py after autodiscover_tasks() to activate.
"""

import logging
import os

import psutil
from celery.signals import (
    before_task_publish,
    task_failure,
    task_postrun,
    task_prerun,
)

logger = logging.getLogger(__name__)


def _get_rss_mb():
    """Return current process RSS in MB, or None on failure."""
    try:
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception as _e:
        logger.warning(
            "celery_telemetry._get_rss_mb: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return None


# Session 1169 — extraction order Rigby ratified in conv pa-639751f029bc432f.
# Order matters: explicit name beats class beats generic key. The `agent` key
# is intentionally accepted only when it's a string (callers sometimes pass an
# instance object, which we don't want to coerce to a meaningless repr).
_AGENT_NAME_KWARG_KEYS = ('agent_name', 'agent_class', 'agent', 'agent_type')


def _extract_agent_name(task_kwargs):
    """Find the first non-empty string under any of the known agent-name keys.

    Returns ``''`` when nothing usable is present — that's the model's default
    and signals 'not an agent task' to the top_consumers aggregator.
    """
    if not isinstance(task_kwargs, dict):
        return ''
    for key in _AGENT_NAME_KWARG_KEYS:
        if key not in task_kwargs:
            continue
        val = task_kwargs[key]
        if isinstance(val, str) and val.strip():
            return val.strip()[:255]
    return ''


# Session 1246 fix (was S1245 bonus finding): Celery signals carry the Task
# instance under `sender` (and sometimes `task`). `str(sender)` returns the
# Task repr ("<@task: core.tasks.X of <app> at 0xADDR>") — useless for joins
# and aggregations downstream. Pull `.name` off whichever object Celery gave
# us, in priority order, and only fall back to `str(sender)` as a last resort
# when the signal payload is unexpectedly shaped (still better than a row
# with task_name='').
def _extract_task_name(task, sender):
    name = getattr(task, 'name', None) or getattr(sender, 'name', None)
    if isinstance(name, str) and name:
        return name
    return str(sender) if sender is not None else ''


@task_prerun.connect
def on_task_prerun(sender=None, task_id=None, task=None, **kwargs):
    """Create a STARTED row when a task begins execution."""
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        from django.utils import timezone

        # Extract queue from delivery_info if available
        queue = ''
        request = kwargs.get('args', None)
        if hasattr(task, 'request') and hasattr(task.request, 'delivery_info'):
            delivery_info = task.request.delivery_info or {}
            queue = delivery_info.get('routing_key', '') or delivery_info.get('exchange', '')

        # Extract worker hostname
        worker = ''
        if hasattr(task, 'request') and hasattr(task.request, 'hostname'):
            worker = task.request.hostname or ''

        # Session 1169: agent_name dim. task_prerun's signal payload
        # carries the per-task kwargs at the 'kwargs' key. Best-effort —
        # extractor returns '' on any inspection failure.
        agent_name = _extract_agent_name(kwargs.get('kwargs'))

        CeleryTaskEvent.objects.update_or_create(
            task_id=task_id,
            defaults={
                'task_name': _extract_task_name(task, sender),
                'agent_name': agent_name,
                'queue': queue,
                'status': 'STARTED',
                'worker': worker,
                'started_at': timezone.now(),
                'rss_mb_start': _get_rss_mb(),
            },
        )
    except Exception:
        # Telemetry must never break task execution
        logger.debug(f"Celery telemetry: failed to record prerun for {task_id}", exc_info=True)


@task_postrun.connect
def on_task_postrun(sender=None, task_id=None, task=None, state=None, retval=None, **kwargs):
    """Update row to SUCCESS/FAILURE when a task completes."""
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        from django.utils import timezone

        now = timezone.now()
        rss_end = _get_rss_mb()

        event = CeleryTaskEvent.objects.filter(task_id=task_id).first()
        if event:
            event.status = state or 'SUCCESS'
            event.finished_at = now
            event.duration_seconds = (now - event.started_at).total_seconds()
            event.rss_mb_end = rss_end
            if rss_end is not None and event.rss_mb_start is not None:
                delta = rss_end - event.rss_mb_start
                event.rss_delta_mb = round(delta, 2)
                task_name = event.task_name
                if delta > 100:
                    logger.error(f"[MEMORY] {task_name} SPIKE {delta:.1f}MB (start={event.rss_mb_start:.1f}, end={rss_end:.1f})")
                elif delta > 50:
                    logger.warning(f"[MEMORY] {task_name} grew {delta:.1f}MB (start={event.rss_mb_start:.1f}, end={rss_end:.1f})")
            event.save(update_fields=[
                'status', 'finished_at', 'duration_seconds',
                'rss_mb_end', 'rss_delta_mb',
            ])
        else:
            # Prerun was missed (e.g. eager mode), create a complete row
            CeleryTaskEvent.objects.create(
                task_id=task_id,
                task_name=_extract_task_name(task, sender),
                status=state or 'SUCCESS',
                started_at=now,
                finished_at=now,
                duration_seconds=0,
                rss_mb_end=rss_end,
            )
    except Exception:
        logger.debug(f"Celery telemetry: failed to record postrun for {task_id}", exc_info=True)

    # Post completion notification to PA conversation if registered
    try:
        from core.services.task_notification import check_and_notify
        check_and_notify(task_id=task_id, state=state or 'SUCCESS', result=retval)
    except Exception:
        logger.debug(f"Celery telemetry: task notification failed for {task_id}", exc_info=True)

    # Session 1165 (COO Backlog item #1): close old DB connections at the
    # task boundary so connection counts don't climb under bursts. In
    # `finally`-style placement (after telemetry + notification) so
    # cleanup runs even if either of those failed. CONN_MAX_AGE=60 still
    # holds in steady state; this is the explicit hygiene call for
    # workers that ran a task and won't immediately run another.
    try:
        from django.db import close_old_connections
        close_old_connections()
    except Exception:
        logger.debug(f"Celery telemetry: close_old_connections failed for {task_id}", exc_info=True)


@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, traceback=None, **kwargs):
    """Update row to FAILURE with error details."""
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        from django.utils import timezone

        now = timezone.now()
        rss_end = _get_rss_mb()

        event = CeleryTaskEvent.objects.filter(task_id=task_id).first()
        if event:
            event.status = 'FAILURE'
            event.finished_at = now
            event.duration_seconds = (now - event.started_at).total_seconds()
            event.error_type = type(exception).__name__ if exception else ''
            event.error_message = str(exception)[:1000] if exception else ''
            event.rss_mb_end = rss_end
            if rss_end is not None and event.rss_mb_start is not None:
                delta = rss_end - event.rss_mb_start
                event.rss_delta_mb = round(delta, 2)
                task_name = event.task_name
                if delta > 100:
                    logger.error(f"[MEMORY] {task_name} SPIKE {delta:.1f}MB (start={event.rss_mb_start:.1f}, end={rss_end:.1f})")
                elif delta > 50:
                    logger.warning(f"[MEMORY] {task_name} grew {delta:.1f}MB (start={event.rss_mb_start:.1f}, end={rss_end:.1f})")
            event.save(update_fields=[
                'status', 'finished_at', 'duration_seconds',
                'error_type', 'error_message',
                'rss_mb_end', 'rss_delta_mb',
            ])
        else:
            CeleryTaskEvent.objects.create(
                task_id=task_id,
                task_name=_extract_task_name(None, sender),
                status='FAILURE',
                started_at=now,
                finished_at=now,
                duration_seconds=0,
                error_type=type(exception).__name__ if exception else '',
                error_message=str(exception)[:1000] if exception else '',
                rss_mb_end=rss_end,
            )
    except Exception:
        logger.debug(f"Celery telemetry: failed to record failure for {task_id}", exc_info=True)

    # Post failure notification to PA conversation if registered
    try:
        from core.services.task_notification import check_and_notify
        check_and_notify(task_id=task_id, state='FAILURE', error=exception)
    except Exception:
        logger.debug(f"Celery telemetry: task failure notification failed for {task_id}", exc_info=True)

    # Session 1165 (COO Backlog item #1): same task-boundary connection
    # hygiene as on_task_postrun. Placed after telemetry + notification
    # so cleanup runs even when either failed.
    try:
        from django.db import close_old_connections
        close_old_connections()
    except Exception:
        logger.debug(f"Celery telemetry: close_old_connections failed for {task_id}", exc_info=True)


@task_failure.connect
def on_agent_task_failure_bridge(sender=None, task_id=None, exception=None, **kwargs):
    """Mark AgentExecution rows associated with the failed Celery task as failed.

    Session 1219 P1 (deliverable 6b00c112-…). Closes the gap where Celery's
    SoftTimeLimitExceeded / generic task_failure propagates past the
    `_FuturesTimeout` cleanup in ``tasks_agents._impl_execute_agent_task``,
    leaving the AgentExecution row stuck in 'in_progress' until the next
    30-min cleanup-watchdog sweep catches it.

    Matches via ``input_data->>'celery_task_id'`` which is set at row creation
    time in ``tasks_agents.py:2179``. Hard SIGKILL cases (Celery's
    ``time_limit=3900``) cannot be handled here — the worker dies and this
    signal never fires; the cleanup watchdog remains the safety net for that
    class.

    Idempotent: filter is scoped to ``status IN ('running', 'in_progress')``
    so a re-fire (or race with the watchdog) is a no-op.
    """
    if not task_id:
        return
    try:
        from core.models_unified_system import AgentExecution
        from django.utils import timezone

        exc_name = type(exception).__name__ if exception else 'TaskFailure'
        exc_msg = str(exception)[:200] if exception else 'Celery task failed without exception detail'

        updated = AgentExecution.objects.filter(
            status__in=('running', 'in_progress'),
            input_data__celery_task_id=str(task_id),
        ).update(
            status='failed',
            error_message=f'Celery task failed: {exc_name}: {exc_msg}'[:2000],
            completed_at=timezone.now(),
        )

        if updated:
            logger.warning(
                "[celery_telemetry] Bridged Celery task_failure → AgentExecution: "
                "task_id=%s exc=%s rows=%d",
                task_id, exc_name, updated,
            )
    except Exception:
        logger.exception(
            "[celery_telemetry] AgentExecution failover failed for task_id=%s", task_id,
        )


@before_task_publish.connect
def stamp_sent_at(headers=None, **kwargs):
    """Stamp `headers["sent_at"]` at enqueue so cockpit_tool.queue_lengths can
    compute backlog age. Celery's default message envelope carries no
    timestamp, which leaves queue-pressure age computation blind. Idempotent:
    won't overwrite if upstream already set it.
    """
    import time
    if not isinstance(headers, dict):
        return
    if headers.get('sent_at') is None:
        headers['sent_at'] = time.time()
