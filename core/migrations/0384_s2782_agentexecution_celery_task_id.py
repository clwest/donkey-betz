# Session 2782 C1: add AgentExecution.celery_task_id for observability cross-
# reference to CeleryTaskEvent. See docs/handoffs/SESSION_2782_*.md.
#
# Nullable + indexed. Auto-populated via pre_save signal in
# core/models_unified_system.py when the save happens inside a Celery task
# context. Non-Celery creation paths (management commands, tests, direct API
# calls) leave the field NULL.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0383_llmcalllog_response_preview"),
    ]

    operations = [
        migrations.AddField(
            model_name="agentexecution",
            name="celery_task_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Session 2782: request.id of the enclosing Celery task, if any.",
                max_length=64,
                null=True,
            ),
        ),
    ]
