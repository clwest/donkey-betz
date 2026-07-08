"""Cycle 1A KFI-4 (ADR-0140 §2.1 (2)) — drop legacy
``refresh-docs-corpus-daily`` PeriodicTask row.

Rationale: KFI-4 supersedes the legacy Session-1235-P5#2 daily cascade
beat entry. The scheduled invocation moves to
``rigby_documentation_manager_daily`` (MissionRunner path with
hash-delta preflight). The legacy ``core.tasks.refresh_docs_corpus``
function itself is preserved as a callable-only compatibility API
(deprecation docstring on the task function). This migration only
drops the DB PeriodicTask row that mirrored the static beat_schedule
entry which is also removed in this same PR at ``core/celery.py``.

Deploy ordering (Chris directive F2 Option A + D):

    1. ``python manage.py migrate`` → drops the PeriodicTask row.
    2. Restart Celery Beat → picks up the removed static entry.
    3. Restart Celery workers → reloads task facade with the new
       ``force`` param on ``rigby_documentation_manager_daily``.

Reverse is idempotent: re-creates the row with the original crontab
(hour=4, minute=0 Denver time) via ``core.tasks.refresh_docs_corpus``.
"""

from __future__ import annotations

import json

from django.db import migrations


PERIODIC_TASK_NAME = "refresh-docs-corpus-daily"
CELERY_TASK_DOTTED = "core.tasks.refresh_docs_corpus"
CRONTAB_MINUTE = "0"
CRONTAB_HOUR = "4"
CRONTAB_DOM = "*"
CRONTAB_MONTH = "*"
CRONTAB_DOW = "*"
TIMEZONE_NAME = "America/Denver"


def drop_periodic_task(apps, schema_editor):
    """Delete the legacy PeriodicTask row by stable name."""
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    # filter().delete() is idempotent: 0-row match returns without error.
    PeriodicTask.objects.filter(name=PERIODIC_TASK_NAME).delete()


def recreate_periodic_task(apps, schema_editor):
    """Reverse hook — re-seed the row from the original crontab."""
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")

    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute=CRONTAB_MINUTE,
        hour=CRONTAB_HOUR,
        day_of_month=CRONTAB_DOM,
        month_of_year=CRONTAB_MONTH,
        day_of_week=CRONTAB_DOW,
        timezone=TIMEZONE_NAME,
    )
    PeriodicTask.objects.update_or_create(
        name=PERIODIC_TASK_NAME,
        defaults={
            "task": CELERY_TASK_DOTTED,
            "crontab": crontab,
            "interval": None,
            "enabled": True,
            "queue": "default",
            "kwargs": json.dumps({}),
            "args": json.dumps([]),
            "expire_seconds": 3600,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0377_arc_i0100_p4_canonical_pa_agent"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            drop_periodic_task,
            reverse_code=recreate_periodic_task,
        ),
    ]
