# Generated manually for Session 507 - Discord /narrative-watch command support
# Note: Columns already added via direct SQL, this migration just syncs state

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0114_alter_autonomoussituationsession_situation_type'),
    ]

    operations = [
        # These are state-only operations since we've already added the columns directly
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='narrativealert',
                    name='user_discord_id',
                    field=models.CharField(blank=True, db_index=True, default='', max_length=100),
                ),
                migrations.AddField(
                    model_name='narrativealert',
                    name='message',
                    field=models.TextField(blank=True, default=''),
                ),
                migrations.AddField(
                    model_name='narrativealert',
                    name='is_read',
                    field=models.BooleanField(default=False),
                ),
                migrations.AlterField(
                    model_name='narrativealert',
                    name='alert_type',
                    field=models.CharField(
                        choices=[
                            ('shift_detected', 'Narrative Shift Detected'),
                            ('new_narrative', 'New Narrative Emerging'),
                            ('narrative_dying', 'Narrative Fading'),
                            ('contradictions', 'Contradictions Detected'),
                            ('high_importance', 'High Importance Alert'),
                            ('subscription', 'User Subscription'),
                        ],
                        max_length=30
                    ),
                ),
                migrations.AlterField(
                    model_name='narrativealert',
                    name='title',
                    field=models.CharField(blank=True, default='', max_length=200),
                ),
                migrations.AlterField(
                    model_name='narrativealert',
                    name='summary',
                    field=models.TextField(blank=True, default=''),
                ),
            ],
            database_operations=[],  # Empty - columns already exist
        ),
    ]
