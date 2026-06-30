"""
Session 1267 PR 4.2 — seed PeriodicTask for Bug Triage Specialist.

Adds one beat schedule row::

    name     = 'bug_triage_daily_run'
    task     = 'bug_triage_daily_run'
    crontab  = daily 08:00 America/Denver
    enabled  = False  (PR 4.3 flips manually after first verified run)

The row is created with ``enabled=False`` so PR 4.2 merge has **zero
production behavior change** until PR 4.3 (or an explicit admin flip).
Cadence is daily at 08:00 Denver — chosen to run AFTER the Chief of
Staff Morning Brief (07:00 Denver) so triage incorporates the most
recent morning-brief OpsRun verdict.

Reverse migration deletes the row by name (no schedule rows
auto-created elsewhere collide on this name).
"""

from __future__ import annotations

import json

from django.db import migrations


PERIODIC_TASK_NAME = "bug_triage_daily_run"
CELERY_TASK_DOTTED = "bug_triage_daily_run"
TIMEZONE_NAME = "America/Denver"


def seed_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    CrontabSchedule = apps.get_model(
        "django_celery_beat", "CrontabSchedule"
    )

    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="8",
        day_of_week="*",
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
                "Session 1267 PR 4.2 — Bug Triage Specialist daily "
                "routine. Runs the 7-step failure-pattern scan as a "
                "MissionRun + produces one structured triage "
                "Deliverable per day. Default enabled=False; PR 4.3 "
                "flips to True after at least one clean manual run."
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
        ("core", "0374_session_1263_consolidate_claude_code_agent"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            seed_periodic_task,
            reverse_code=remove_periodic_task,
        ),
    ]
