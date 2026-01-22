# Generated for Session 789 - Add missing columns to body system tables
"""
Adds columns that were missing from migration 0181:
- BrainPulse.llm_timeouts_24h
- SkinStatus.total_files_tracked
- NervousStatus.total_consumers
- NervousPulse.total_consumers
- WebSocketConnectionLog.created_at
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0181_restore_body_system_tables'),
    ]

    operations = [
        # Add llm_timeouts_24h to BrainPulse
        migrations.AddField(
            model_name='brainpulse',
            name='llm_timeouts_24h',
            field=models.IntegerField(default=0),
        ),

        # Add total_files_tracked to SkinStatus
        migrations.AddField(
            model_name='skinstatus',
            name='total_files_tracked',
            field=models.IntegerField(default=0),
        ),

        # Add total_consumers to NervousStatus
        migrations.AddField(
            model_name='nervousstatus',
            name='total_consumers',
            field=models.IntegerField(default=0),
        ),

        # Add total_consumers to NervousPulse
        migrations.AddField(
            model_name='nervouspulse',
            name='total_consumers',
            field=models.IntegerField(default=0),
        ),

        # Add created_at to WebSocketConnectionLog
        migrations.AddField(
            model_name='websocketconnectionlog',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
