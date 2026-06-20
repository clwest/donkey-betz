"""Session 1169 — decorator-side timeouts on ``monitor_celery_health``.

Closes Session 1168 carryover item D (partial; the
``capture_pa_acks_health_snapshot`` probe-decomposition piece is
queued as a separate follow-on per Rigby's split-the-fix design call).

These tests pin the decorator-level options the task carries so a
future refactor can't silently drop the queue or timeouts.

Run::

    python manage.py test core.tests.test_monitor_celery_health_timeouts -v2
"""
from __future__ import annotations

from django.test import SimpleTestCase

from core.tasks import monitor_celery_health


class MonitorCeleryHealthDecoratorTests(SimpleTestCase):
    def test_queue_is_broadcast(self):
        """Direct dispatches (.delay / .apply_async) need to land on the
        broadcast queue, same as scheduled fires via beat. Pre-Session-1169
        the queue routing was only set in the beat schedule options block,
        so manual invocations ran on the default queue."""
        # Celery stores per-task queue routing on the task's `queue` attr
        # when @shared_task(queue=...) is used.
        self.assertEqual(monitor_celery_health.queue, 'broadcast')

    def test_soft_time_limit_is_60_seconds(self):
        self.assertEqual(monitor_celery_health.soft_time_limit, 60)

    def test_time_limit_is_90_seconds(self):
        self.assertEqual(monitor_celery_health.time_limit, 90)

    def test_task_name_unchanged(self):
        """Sanity: the @shared_task name='core.tasks.monitor_celery_health'
        still matches the beat schedule entry. If this drifts, beat dispatch
        breaks silently."""
        self.assertEqual(
            monitor_celery_health.name,
            'core.tasks.monitor_celery_health',
        )
