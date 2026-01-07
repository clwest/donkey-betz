"""
Session 723: SKIN System Migration

Creates SkinPulse and SkinStatus models for workspace output monitoring.
The SKIN is the 9th body system - tracks file writes, project changes,
rollback availability, and agent activity on workspaces.
"""

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0154_session_722_brain_system'),
    ]

    operations = [
        # Create SkinPulse - Time-series records
        migrations.CreateModel(
            name='SkinPulse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('active', 'Active'),
                    ('sweating', 'Sweating'),
                    ('irritated', 'Irritated'),
                    ('damaged', 'Damaged'),
                    ('healing', 'Healing'),
                    ('dormant', 'Dormant'),
                ], default='healthy', max_length=20)),
                ('health_score', models.FloatField(default=100.0, help_text='Overall skin health 0-100')),
                ('total_workspaces', models.IntegerField(default=0)),
                ('active_workspaces', models.IntegerField(default=0)),
                ('workspaces_with_errors', models.IntegerField(default=0)),
                ('operations_24h', models.IntegerField(default=0)),
                ('successful_operations_24h', models.IntegerField(default=0)),
                ('failed_operations_24h', models.IntegerField(default=0)),
                ('success_rate_24h', models.FloatField(default=100.0)),
                ('files_created_24h', models.IntegerField(default=0)),
                ('files_modified_24h', models.IntegerField(default=0)),
                ('files_deleted_24h', models.IntegerField(default=0)),
                ('commands_executed_24h', models.IntegerField(default=0)),
                ('git_operations_24h', models.IntegerField(default=0)),
                ('bytes_written_24h', models.BigIntegerField(default=0)),
                ('lines_changed_24h', models.IntegerField(default=0)),
                ('avg_operation_time_ms', models.FloatField(default=0)),
                ('rollbacks_available', models.IntegerField(default=0)),
                ('rollbacks_performed_24h', models.IntegerField(default=0)),
                ('pending_reviews', models.IntegerField(default=0)),
                ('active_agents', models.IntegerField(default=0)),
                ('most_active_agent', models.CharField(blank=True, max_length=100)),
                ('agent_operation_counts', models.JSONField(default=dict)),
                ('recent_errors', models.JSONField(default=list)),
                ('permission_denials', models.IntegerField(default=0)),
                ('check_duration_ms', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Skin Pulse',
                'verbose_name_plural': 'Skin Pulses',
                'db_table': 'core_skin_pulses',
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='skinpulse',
            index=models.Index(fields=['-recorded_at'], name='core_skin_p_recorde_idx'),
        ),
        migrations.AddIndex(
            model_name='skinpulse',
            index=models.Index(fields=['status', '-recorded_at'], name='core_skin_p_status__idx'),
        ),

        # Create SkinStatus - Cached current state
        migrations.CreateModel(
            name='SkinStatus',
            fields=[
                ('id', models.IntegerField(default=1, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('active', 'Active'),
                    ('sweating', 'Sweating'),
                    ('irritated', 'Irritated'),
                    ('damaged', 'Damaged'),
                    ('healing', 'Healing'),
                    ('dormant', 'Dormant'),
                ], default='healthy', max_length=20)),
                ('is_healthy', models.BooleanField(default=True)),
                ('health_score', models.FloatField(default=100.0)),
                ('total_workspaces', models.IntegerField(default=0)),
                ('active_workspaces', models.IntegerField(default=0)),
                ('total_files_tracked', models.IntegerField(default=0)),
                ('total_operations_all_time', models.IntegerField(default=0)),
                ('operations_24h', models.IntegerField(default=0)),
                ('success_rate_24h', models.FloatField(default=100.0)),
                ('files_touched_24h', models.IntegerField(default=0)),
                ('bytes_written_24h', models.BigIntegerField(default=0)),
                ('activity_level', models.CharField(default='normal', help_text='dormant, low, normal, high, intense', max_length=20)),
                ('operations_per_hour', models.FloatField(default=0)),
                ('error_rate_24h', models.FloatField(default=0)),
                ('avg_operation_time_ms', models.FloatField(default=0)),
                ('rollbacks_available', models.IntegerField(default=0)),
                ('pending_reviews', models.IntegerField(default=0)),
                ('last_operation_at', models.DateTimeField(blank=True, null=True)),
                ('last_successful_operation_at', models.DateTimeField(blank=True, null=True)),
                ('last_error_at', models.DateTimeField(blank=True, null=True)),
                ('last_check', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Skin Status',
                'verbose_name_plural': 'Skin Status',
                'db_table': 'core_skin_status',
            },
        ),
    ]
