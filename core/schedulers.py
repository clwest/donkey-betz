"""
Session 1064: Custom DatabaseScheduler that preserves queue fields.

Problem: django_celery_beat's DatabaseScheduler.update_from_dict() calls
_unpack_options(queue=None) for beat schedule entries that don't specify a queue.
This passes queue=None into update_or_create(defaults=...), which OVERWRITES any
queue value set by sync_task_queues with NULL on every celery-beat restart.

Fix: Subclass ModelEntry to omit queue from defaults when not explicitly set,
so existing DB queue values (set by sync_task_queues) are preserved.
"""

from django_celery_beat.schedulers import DatabaseScheduler, ModelEntry


class QueuePreservingModelEntry(ModelEntry):
    """ModelEntry that doesn't reset queue to NULL when options.queue is absent."""

    @classmethod
    def _unpack_options(cls, queue=None, **kwargs):
        result = super()._unpack_options(queue=queue, **kwargs)
        if queue is None:
            result.pop('queue', None)
        return result


class QueuePreservingScheduler(DatabaseScheduler):
    """DatabaseScheduler using QueuePreservingModelEntry."""

    Entry = QueuePreservingModelEntry
