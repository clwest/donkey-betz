"""Session 1258 PR 3.3 — flip Morning Brief beat row to MissionRunner runner.

The beat row ``generate-morning-brief-daily`` was created in S1233
Sub-step C with ``task='core.tasks.generate_morning_brief_daily'``.
PR 3.3 deletes the legacy task body and routes the same row to the
MissionRunner-backed ``chief_of_staff_morning_brief_run`` (PR 3.2's
Celery task).

Why a migration (not just sync_celery_beat)
-------------------------------------------

The Procfile release runs
``sync_celery_beat --apply --create-only --disable-missing``. With
this PR's flip of ``core/celery.py``, sync_celery_beat would:

  1. See the new task path (``chief_of_staff_morning_brief_run``) not
     in ``db_tasks`` (which is keyed by the OLD ``pt.task`` value
     pre-flip), so flag it as to_create.
  2. ``create_task`` does ``get_or_create(name=...)``, finds the
     existing row, hits the ``if not created`` branch, and updates
     the row's task field to the new value via a SEPARATE Python
     instance.
  3. ``orphaned`` was computed at compute-list time BEFORE step 2,
     using the original (now-stale) Python instance whose
     ``pt.task`` still reads the OLD value. So the row appears in
     the orphan list.
  4. With ``--disable-missing``, the orphan handler does
     ``pt.enabled = False; pt.save()``. ``pt.save()`` writes ALL
     fields back to the DB from the STALE Python instance — which
     overwrites the just-flipped task field AND sets enabled=False.

Net Railway release behavior without this migration: row gets
flipped, then immediately reverted to legacy + disabled. Beat
stops firing. The S1258 PR 3.3 discovery deliverable
(cc4c0641-c361-4c19-a1db-a6ccfa92b281 §7) initially mis-analyzed
this sequence; reality check during implementation caught it.

Fix: this migration runs in the Procfile release ``migrate`` step
BEFORE ``sync_celery_beat``, so the DB row already has the new
task field by the time sync_celery_beat reads it. Then
sync_celery_beat sees the row in-sync (task path now matches
celery.py), neither flagging it for to_create nor as orphan.

Idempotent: re-running this migration is a no-op (the update is
already in place).

Rollback
--------

The reverse migration sets the row back to
``core.tasks.generate_morning_brief_daily``. NOTE: rollback is only
behaviorally safe if the legacy task body is still present in
``core/tasks.py``. PR 3.3 deletes that body, so an emergency
rollback should use ``git revert <merge_sha>`` + redeploy (which
will re-run this migration's reverse_code AND restore the legacy
task body in the same release).
"""

from __future__ import annotations

from django.db import migrations


PERIODIC_TASK_NAME = "generate-morning-brief-daily"
LEGACY_TASK_PATH = "core.tasks.generate_morning_brief_daily"
NEW_TASK_NAME = "chief_of_staff_morning_brief_run"


def flip_to_new_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    row = PeriodicTask.objects.filter(name=PERIODIC_TASK_NAME).first()
    if row is None:
        # No row to flip — this is a fresh DB or one where the row
        # was never seeded. sync_celery_beat will create it with the
        # new task path on its first run (because it's not in
        # db_tasks at all, the to_create branch will create-or-update
        # it correctly without orphan-handler interference).
        return
    if row.task == NEW_TASK_NAME:
        # Already flipped (idempotent re-run, or row was hand-flipped).
        return
    row.task = NEW_TASK_NAME
    row.save(update_fields=["task"])


def flip_to_legacy_task(apps, schema_editor):
    """Reverse migration.

    SAFETY NOTE: only behaviorally safe if the legacy task body
    ``core.tasks.generate_morning_brief_daily`` is still present in
    the deployed build. PR 3.3 deletes that body, so the reverse
    migration alone does NOT restore production behavior — use
    ``git revert`` + redeploy for emergency rollback (which runs
    this reverse_code as part of the migrate step AND restores the
    legacy task body in the same release).
    """
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    row = PeriodicTask.objects.filter(name=PERIODIC_TASK_NAME).first()
    if row is None:
        return
    if row.task == LEGACY_TASK_PATH:
        return
    row.task = LEGACY_TASK_PATH
    row.save(update_fields=["task"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0372_session_1252_seed_docs_manager_periodic_task"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            flip_to_new_task,
            reverse_code=flip_to_legacy_task,
        ),
    ]
