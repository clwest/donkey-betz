# Session 1250 PR 3: MissionRun-compatibility fields on OpsRun.
#
# Additive only. No backfill. No behavior change for existing callers.
# See docs/EVENT_SYSTEM_INVENTORY.md §10 for the ops/mission separation
# invariant.
#
# Fields added:
#   - domain (CharField, choices=ops/mission, default='ops', db_index)
#   - run_kind (CharField, max_length=40, blank=True, default='')
#   - mission_id (UUIDField, nullable, blank=True, db_index)
#
# Existing OpsRun rows receive domain='ops' via the field default at row
# read time; the migration sets the column default to 'ops' so any rows
# without an explicit domain are interpreted as ops-domain.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0369_session_1244_rename_agentchannel_to_projectchannel"),
    ]

    operations = [
        migrations.AddField(
            model_name="opsrun",
            name="domain",
            field=models.CharField(
                choices=[("ops", "Ops"), ("mission", "Mission")],
                db_index=True,
                default="ops",
                help_text=(
                    "Session 1250 PR 3: ops vs mission scope. "
                    "Do not overload run_type."
                ),
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="opsrun",
            name="run_kind",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Session 1250 PR 3: sub-classification within domain."
                ),
                max_length=40,
            ),
        ),
        migrations.AddField(
            model_name="opsrun",
            name="mission_id",
            field=models.UUIDField(
                blank=True,
                db_index=True,
                help_text=(
                    "Session 1250 PR 3: mission identity; "
                    "null for ops-domain rows."
                ),
                null=True,
            ),
        ),
    ]
