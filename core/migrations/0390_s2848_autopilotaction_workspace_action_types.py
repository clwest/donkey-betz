# Generated for S2848 A1 W1.5 — extends AutopilotAction.ACTION_TYPES with
# per-workspace budget audit values (Phase 2/3 backfill + W1.5 downgrade).
# Choices-only change (max_length unchanged at 30); no schema alteration.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0389_llmcalllog_workspace_fk_s2846"),
    ]

    operations = [
        migrations.AlterField(
            model_name="autopilotaction",
            name="action_type",
            field=models.CharField(
                choices=[
                    ("block_agent", "Block Agent"),
                    ("unblock_agent", "Unblock Agent"),
                    ("attention_item", "Created Attention Item"),
                    ("deploy_watch", "Deploy Watch Verdict"),
                    ("dry_run", "Dry Run (no action taken)"),
                    ("retry_deliberation", "Retry Failed Deliberation"),
                    ("content_sweep", "Content Pipeline Sweep"),
                    ("auto_resolve", "Auto-resolve Attention Item"),
                    ("content_publish", "Content Auto-Publish"),
                    ("remediate", "Auto-Remediation Applied"),
                    ("config_tune", "Config Self-Tuning"),
                    ("budget_freeze", "Budget Hard Freeze"),
                    ("workspace_budget_freeze", "Workspace Budget Freeze (auto)"),
                    ("workspace_freeze_cleared", "Workspace Freeze Cleared"),
                    ("workspace_cap_set", "Workspace Cap Set"),
                    ("workspace_cap_cleared", "Workspace Cap Cleared"),
                    ("workspace_downgrade_set", "Workspace Downgrade Set (auto)"),
                    ("workspace_downgrade_cleared", "Workspace Downgrade Cleared"),
                ],
                max_length=30,
            ),
        ),
    ]
