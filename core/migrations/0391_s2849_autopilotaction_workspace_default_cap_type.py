# Generated for S2849 A1 W2 #2a — extends AutopilotAction.ACTION_TYPES with
# workspace_default_cap_set for the new operator-configurable global default
# cap. Choices-only change (max_length unchanged at 30); no schema alteration.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0390_s2848_autopilotaction_workspace_action_types"),
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
                    ("workspace_default_cap_set", "Workspace Default Cap Set"),
                ],
                max_length=30,
            ),
        ),
    ]
