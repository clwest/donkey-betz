# Session 998: System Governance Hardening
# - SelfBlog.author field for tracking who/what created content
# - UnifiedUser.platform_role: add 'reviewer' choice

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0239_session_996_initiative_ownership"),
    ]

    operations = [
        # 1. Add author field to SelfBlog
        migrations.AddField(
            model_name="selfblog",
            name="author",
            field=models.CharField(
                blank=True,
                default="",
                help_text='Session 998: Author — agent name or "human"',
                max_length=100,
            ),
        ),
        # 2. Update platform_role choices to include 'reviewer'
        migrations.AlterField(
            model_name="unifieduser",
            name="platform_role",
            field=models.CharField(
                choices=[
                    ("admin", "Platform Administrator"),
                    ("sports_analyst", "Sports Analytics User"),
                    ("content_creator", "Content Generation User"),
                    ("agent_manager", "Agent Orchestration Manager"),
                    ("unified_user", "Full Platform Access"),
                    ("reviewer", "Read-Only Reviewer"),
                ],
                default="unified_user",
                help_text="Primary role/access level on the platform",
                max_length=50,
            ),
        ),
    ]
