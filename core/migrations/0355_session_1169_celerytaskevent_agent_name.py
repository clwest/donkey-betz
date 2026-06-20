"""Session 1169 — add agent_name dim to CeleryTaskEvent.

Surgical migration: ONLY adds the new ``agent_name`` field. The
auto-generated migration that ``makemigrations`` produced for this
change also picked up a pile of pre-existing model drift (4 new
Narrative tables + AlterFields on AgentExecution / CuratedSignalEntry /
FinalAppliedOverrides / FleetPaChatAuditRow) that is NOT part of this
PR's scope. That drift was pulled out into a separate follow-on
ticket; this migration carries only the change that closes Session
1169 item F.

Carryover for ops triage: run ``python manage.py makemigrations core``
on a clean main and capture the diff to a deliverable so someone can
own the Narrative + AlterField drift cleanup as its own PR.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0354_session_1163_b_final_applied_overrides"),
    ]

    operations = [
        migrations.AddField(
            model_name="celerytaskevent",
            name="agent_name",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                help_text=(
                    "Session 1169: agent dim sourced from task kwargs at "
                    "prerun. Empty = non-agent task or pre-migration row."
                ),
                max_length=255,
            ),
        ),
    ]
