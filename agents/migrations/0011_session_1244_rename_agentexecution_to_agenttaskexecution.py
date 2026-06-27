"""Session 1244 — rename agents.AgentExecution → agents.AgentTaskExecution.

Removes the cross-app name collision with `core.AgentExecution` (the
canonical orchestration-tracker in core.models_unified_system, 987 live
rows). This agents-app variant is a 39-column rich task-execution
surface (task_description, progress_percentage, websocket_channel,
token_usage, cost_breakdown, user_rating, quality_score) that never
had a writer wired up — table remained 0 rows. Renamed-rather-than-
deleted because 70+ read-side importers query against it (always
returning empty); preserves consumer code paths.

The model class lives in `core/models/agents_registry/models.py` but
is registered under the `agents` app label (Meta.app_label = 'agents').
This migration goes in the agents app accordingly.

Session 1084 prior-art comment at core/tasks_agents.py:2095-2113
documented this exact collision; this rename completes the disambiguation
that was deferred at that time.

Table is empty (0 rows). RenameModel is atomic and data-safe.

Audit: deliverable 86870fdd-… Finding 2.2.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("agents", "0010_session_752_make_agentcontribution_project_optional"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AgentExecution",
            new_name="AgentTaskExecution",
        ),
    ]
