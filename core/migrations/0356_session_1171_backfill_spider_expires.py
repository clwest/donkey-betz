"""Session 1171 #3 (C): restore expires on backfill-spider-embeddings PeriodicTask.

The 06-14 → 06-19 ml-queue flood (533 msgs accumulated) had a contributing
cause beyond the producer + drain mismatch: the PeriodicTask row had
`expire_seconds=NULL`, so beat-fired messages had no TTL and accumulated
indefinitely. (DatabaseScheduler wins over the static `expires=900` declared
in `core.celery.app.conf.beat_schedule`.)

This migration restores `expire_seconds=900` on the row so that even if it's
re-enabled in the future, accidental backlog cannot persist past one schedule
cycle. The row is left disabled (Rigby's call on whether/when to re-enable).

See:
- handoffs/SESSION_1171_ML_QUEUE_FLOOD_AND_AUTH_MIDDLEWARE.md
- core/tasks.py:backfill_spider_embeddings (singleton_task + depth-gate)
"""

from django.db import migrations


def restore_expire_seconds(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(
        name="backfill-spider-embeddings",
        task="core.tasks.backfill_spider_embeddings",
    ).update(expire_seconds=900)


def noop_reverse(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(
        name="backfill-spider-embeddings",
        task="core.tasks.backfill_spider_embeddings",
    ).update(expire_seconds=None)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0355_session_1169_celerytaskevent_agent_name"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(restore_expire_seconds, noop_reverse),
    ]
