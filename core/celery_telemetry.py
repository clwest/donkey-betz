"""
Session 983: Celery Task Telemetry Signal Handlers

Connects to Celery signals (task_prerun, task_postrun, task_failure) and
writes lightweight CeleryTaskEvent rows for observability.

Import this module in core/celery.py after autodiscover_tasks() to activate.
"""

import logging
import os

import psutil
from celery.signals import task_prerun, task_postrun, task_failure

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

        CeleryTaskEvent.objects.update_or_create(
            task_id=task_id,
            defaults={
                'task_name': task.name if task else str(sender),
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
                task_name=task.name if task else str(sender),
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
                task_name=str(sender),
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
