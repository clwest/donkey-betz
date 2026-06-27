"""Session 1244 — rename core.AgentChannel → core.ProjectChannel.

Removes cross-app name collision with `agents.AgentChannel` (the
orchestration-oriented variant). Different concepts: this one is
project-scoped Slack-style channels with `project_id` FK / pinned
messages / member counts. The agents variant has orchestration_id,
active_agents tracking, and a richer metadata model.

Both tables empty (0 rows). RenameModel is atomic and data-safe.

Also renames the two FK-pointed related models (AgentChannelMessage,
AgentChannelMembership) that reference this channel — they keep their
class names but their FK target name updates to `ProjectChannel`.
The FK targets are model-class references in the same file
(core/models_unified_system.py), updated in the same PR.

Audit: deliverable 86870fdd-… Finding 1.4.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0368_session_1244_delete_agentlearningsession"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AgentChannel",
            new_name="ProjectChannel",
        ),
    ]
