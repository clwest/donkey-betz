"""
Session 983: Celery Task Telemetry Signal Handlers

Connects to Celery signals (task_prerun, task_postrun, task_failure) and
writes lightweight CeleryTaskEvent rows for observability.

Import this module in core/celery.py after autodiscover_tasks() to activate.
"""

import logging

from celery.signals import task_prerun, task_postrun, task_failure

logger = logging.getLogger(__name__)


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

        CeleryTaskEvent.objects.create(
            task_id=task_id,
            task_name=task.name if task else str(sender),
            queue=queue,
            status='STARTED',
            worker=worker,
            started_at=timezone.now(),
        )
    except Exception:
        # Telemetry must never break task execution
        logger.debug(f"Celery telemetry: failed to record prerun for {task_id}", exc_info=True)


@task_postrun.connect
def on_task_postrun(sender=None, task_id=None, task=None, state=None, **kwargs):
    """Update row to SUCCESS/FAILURE when a task completes."""
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        from django.utils import timezone

        now = timezone.now()
        event = CeleryTaskEvent.objects.filter(task_id=task_id).first()
        if event:
            event.status = state or 'SUCCESS'
            event.finished_at = now
            event.duration_seconds = (now - event.started_at).total_seconds()
            event.save(update_fields=['status', 'finished_at', 'duration_seconds'])
        else:
            # Prerun was missed (e.g. eager mode), create a complete row
            CeleryTaskEvent.objects.create(
                task_id=task_id,
                task_name=task.name if task else str(sender),
                status=state or 'SUCCESS',
                started_at=now,
                finished_at=now,
                duration_seconds=0,
            )
    except Exception:
        logger.debug(f"Celery telemetry: failed to record postrun for {task_id}", exc_info=True)


@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, traceback=None, **kwargs):
    """Update row to FAILURE with error details."""
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        from django.utils import timezone

        now = timezone.now()
        event = CeleryTaskEvent.objects.filter(task_id=task_id).first()
        if event:
            event.status = 'FAILURE'
            event.finished_at = now
            event.duration_seconds = (now - event.started_at).total_seconds()
            event.error_type = type(exception).__name__ if exception else ''
            event.error_message = str(exception)[:1000] if exception else ''
            event.save(update_fields=[
                'status', 'finished_at', 'duration_seconds',
                'error_type', 'error_message',
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
            )
    except Exception:
        logger.debug(f"Celery telemetry: failed to record failure for {task_id}", exc_info=True)
