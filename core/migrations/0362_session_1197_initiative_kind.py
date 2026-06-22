# Session 1197 — Initiative `kind` enum + `related_initiatives` JSON link.
#
# Trimmed-by-hand from the makemigrations auto-output. The auto-output
# bundled 16 AlterField ops + 4 Create-Narrative-model ops that belong
# to the parked Session 1196 migration drift (Set A + Set B in the
# Session 1196 close-out priorities). Those ops are out of scope for
# this PR; they get their own audit pass.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0361_session_1196_initiative_diagnostic_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="initiative",
            name="kind",
            field=models.CharField(
                choices=[
                    ("project", "Project (5-stage arc, time-bounded)"),
                    ("recurring_artifact", "Recurring artifact stream"),
                    ("investigation", "Investigation / recon workstream"),
                    ("spec_backlog", "Spec / follow-up backlog"),
                ],
                db_index=True,
                default="project",
                help_text=(
                    "Session 1197: semantic kind of this Initiative. "
                    "Orthogonal to status (lifecycle). Default is project; "
                    "apply_initiative_kind_classification mgmt cmd retro-labels "
                    "existing rows per the locked classification table."
                ),
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="initiative",
            name="related_initiatives",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text=(
                    "Session 1197: lightweight directional Initiative links. "
                    "List of {\"id\": \"<uuid>\", \"relation\": \"spawns\"|\"spawned_from\", "
                    "\"note\": \"...\"} entries. No FK — sparse use case."
                ),
            ),
        ),
    ]
