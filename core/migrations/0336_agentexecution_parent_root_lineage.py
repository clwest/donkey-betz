# Session 1098 PR #4: lineage fields on AgentExecution.
#
# `parent_execution_id` — the execution_id that spawned this run. When a
# parent agent dispatches a child agent, the child records the parent's
# execution_id here.
#
# `root_execution_id` — the top-of-chain ancestor. Set to parent's root
# (or parent_execution_id if parent has no parent). Lets budget + cancel
# checks do O(1) lookup against the root instead of walking ancestry on
# every check.
#
# Both fields NULL for pre-PR-#4 rows and for root executions (the root
# of the tree has parent=NULL; its own id IS the root_execution_id).
#
# See core/services/cancel_registry.is_execution_cancelled — when this
# migration lands, that check walks the ancestry and returns True if ANY
# ancestor was cancelled.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0335_agentexecution_cancelled_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="agentexecution",
            name="parent_execution_id",
            field=models.UUIDField(
                blank=True,
                db_index=True,
                help_text=(
                    "Session 1098 PR #4: the AgentExecution.id of the "
                    "dispatch that spawned this run. NULL for root "
                    "executions (top-of-tree) and for legacy rows."
                ),
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="agentexecution",
            name="root_execution_id",
            field=models.UUIDField(
                blank=True,
                db_index=True,
                help_text=(
                    "Session 1098 PR #4: the top-of-chain execution_id. "
                    "Equals self.id for root executions. Used for O(1) "
                    "budget + cancel-ancestor lookups."
                ),
                null=True,
            ),
        ),
    ]
