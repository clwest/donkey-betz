"""
Session 1267 PR 4.3 — flip Bug Triage Specialist PeriodicTask to enabled=True.

PR 4.2 seeded ``PeriodicTask(name='bug_triage_daily_run', enabled=False)``
at cron(minute=0, hour=8, timezone='America/Denver'). V13 verification
ran cleanly post-merge of PR 4.2: 7 step_pass events, zero
``verdict_issued`` OpsRunEvent rows (D1 lock), bounded-summary postflight
(D5), and a 1440-char Deliverable with all 6 contract sections.

This migration flips the beat row to ``enabled=True`` so the first
scheduled fire happens at the next 08:00 America/Denver tick. Reverse
restores ``enabled=False`` so a rollback returns the beat row to the
post-PR-4.2 dormant state without dropping the row entirely.

Migration is idempotent: ``update_or_create`` with ``defaults`` so
re-running against an already-flipped row is a no-op.
"""

from __future__ import annotations

from django.db import migrations


PERIODIC_TASK_NAME = "bug_triage_daily_run"


def flip_enabled_true(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name=PERIODIC_TASK_NAME).update(
        enabled=True
    )


def flip_enabled_false(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name=PERIODIC_TASK_NAME).update(
        enabled=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0375_session_1267_seed_bug_triage_beat"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            flip_enabled_true,
            reverse_code=flip_enabled_false,
        ),
    ]
