"""
Session 1252 PR 2 — seed PeriodicTask for Documentation Manager.

Adds one beat schedule row::

    name     = 'rigby_documentation_manager_daily'
    task     = 'rigby_documentation_manager_daily'
    crontab  = weekdays 06:30 America/Denver
    enabled  = False  (Chris flips manually after first verified run)

The row is created with ``enabled=False`` so PR 2 merge has **zero
production behavior change** until Chris explicitly enables it.
Reverse migration deletes the row by name (no schedule rows
auto-created elsewhere collide on this name).
"""

from __future__ import annotations

import json

from django.db import migrations


PERIODIC_TASK_NAME = "rigby_documentation_manager_daily"
CELERY_TASK_DOTTED = "rigby_documentation_manager_daily"
TIMEZONE_NAME = "America/Denver"


def seed_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    CrontabSchedule = apps.get_model(
        "django_celery_beat", "CrontabSchedule"
    )

    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute="30",
        hour="6",
        day_of_week="1,2,3,4,5",  # Mon-Fri
        day_of_month="*",
        month_of_year="*",
        timezone=TIMEZONE_NAME,
    )

    PeriodicTask.objects.update_or_create(
        name=PERIODIC_TASK_NAME,
        defaults={
            "task": CELERY_TASK_DOTTED,
            "crontab": crontab,
            "enabled": False,
            "description": (
                "Session 1252 PR 2 — Documentation Manager daily routine. "
                "Runs the 4-step docs cascade as a MissionRun, certifies "
                "success or escalates failure. Default enabled=False; "
                "flip via Django admin or SQL after first verified run."
            ),
            "kwargs": json.dumps({}),
            "args": json.dumps([]),
        },
    )


def remove_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name=PERIODIC_TASK_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0371_session_1250_rigby_work_item"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            seed_periodic_task,
            reverse_code=remove_periodic_task,
        ),
    ]
