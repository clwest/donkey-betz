# Generated for Session 788 - Restore Body System Tables
"""
Restores body system tables that were deleted by migration 0157
but never recreated:
- BrainPulse, CognitiveChannel, CognitiveStatus (BRAIN)
- SkinPulse, SkinStatus (SKIN)
- NervousPulse, NervousStatus, WebSocketConnectionLog (NERVOUS)
"""

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0180_add_included_documentation_to_intelligentpromptmetric'),
    ]

    operations = [
        # ==================== SKIN SYSTEM ====================
        migrations.CreateModel(
            name='SkinPulse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[
                    ('healthy', 'Healthy'), ('active', 'Active'), ('sweating', 'Sweating'),
                    ('irritated', 'Irritated'), ('damaged', 'Damaged'), ('healing', 'Healing'),
                    ('dormant', 'Dormant'),
                ], default='healthy', max_length=20)),
                ('health_score', models.FloatField(default=100.0)),
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
                ('bytes_written_24h', models.BigIntegerField(default=0)),
                ('rollbacks_available', models.IntegerField(default=0)),
                ('active_agents', models.IntegerField(default=0)),
                ('recent_errors', models.JSONField(default=list)),
                ('check_duration_ms', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Skin Pulse',
                'db_table': 'core_skin_pulses',
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.CreateModel(
            name='SkinStatus',
            fields=[
                ('id', models.IntegerField(default=1, primary_key=True, serialize=False)),
                ('status', models.CharField(default='healthy', max_length=20)),
                ('is_healthy', models.BooleanField(default=True)),
                ('health_score', models.FloatField(default=100.0)),
                ('total_workspaces', models.IntegerField(default=0)),
                ('active_workspaces', models.IntegerField(default=0)),
                ('operations_24h', models.IntegerField(default=0)),
                ('success_rate_24h', models.FloatField(default=100.0)),
                ('files_touched_24h', models.IntegerField(default=0)),
                ('bytes_written_24h', models.BigIntegerField(default=0)),
                ('activity_level', models.CharField(default='normal', max_length=20)),
                ('rollbacks_available', models.IntegerField(default=0)),
                ('last_operation_at', models.DateTimeField(blank=True, null=True)),
                ('last_check', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Skin Status',
                'db_table': 'core_skin_status',
            },
        ),

        # ==================== BRAIN SYSTEM ====================
        migrations.CreateModel(
            name='CognitiveChannel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(blank=True, max_length=150)),
                ('channel_type', models.CharField(max_length=20)),
                ('provider', models.CharField(blank=True, max_length=30)),
                ('model_name', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_critical', models.BooleanField(default=False)),
                ('total_calls', models.BigIntegerField(default=0)),
                ('total_tokens', models.BigIntegerField(default=0)),
                ('total_errors', models.BigIntegerField(default=0)),
                ('last_activity', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Cognitive Channel',
                'db_table': 'core_cognitive_channel',
            },
        ),
        migrations.CreateModel(
            name='BrainPulse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('overall_status', models.CharField(default='focused', max_length=20)),
                ('cognitive_score', models.FloatField(default=100.0)),
                ('is_thinking', models.BooleanField(default=True)),
                ('llm_calls_24h', models.IntegerField(default=0)),
                ('llm_success_rate', models.FloatField(default=100.0)),
                ('llm_avg_latency_ms', models.FloatField(default=0)),
                ('llm_errors_24h', models.IntegerField(default=0)),
                ('tokens_input_24h', models.BigIntegerField(default=0)),
                ('tokens_output_24h', models.BigIntegerField(default=0)),
                ('active_conversations', models.IntegerField(default=0)),
                ('conversations_24h', models.IntegerField(default=0)),
                ('rag_queries_24h', models.IntegerField(default=0)),
                ('agent_thoughts_24h', models.IntegerField(default=0)),
                ('provider_stats', models.JSONField(default=dict)),
                ('check_duration_ms', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Brain Pulse',
                'db_table': 'core_brain_pulse',
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.CreateModel(
            name='CognitiveStatus',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(default='focused', max_length=20)),
                ('cognitive_score', models.FloatField(default=100.0)),
                ('is_thinking', models.BooleanField(default=True)),
                ('last_check', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Cognitive Status',
                'db_table': 'core_cognitive_status',
            },
        ),

        # ==================== NERVOUS SYSTEM ====================
        migrations.CreateModel(
            name='NervousPulse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(default='calm', max_length=20)),
                ('health_score', models.FloatField(default=100.0)),
                ('websocket_connections', models.IntegerField(default=0)),
                ('api_latency_ms', models.FloatField(default=0)),
                ('events_processed_24h', models.IntegerField(default=0)),
                ('errors_24h', models.IntegerField(default=0)),
                ('check_duration_ms', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Nervous Pulse',
                'db_table': 'core_nervous_pulses',
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.CreateModel(
            name='NervousStatus',
            fields=[
                ('id', models.IntegerField(default=1, primary_key=True, serialize=False)),
                ('status', models.CharField(default='calm', max_length=20)),
                ('is_healthy', models.BooleanField(default=True)),
                ('health_score', models.FloatField(default=100.0)),
                ('websocket_connections', models.IntegerField(default=0)),
                ('api_latency_ms', models.FloatField(default=0)),
                ('events_processed_24h', models.IntegerField(default=0)),
                ('last_check', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Nervous Status',
                'db_table': 'core_nervous_status',
            },
        ),
        migrations.CreateModel(
            name='WebSocketConnectionLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('channel_name', models.CharField(max_length=255)),
                ('connection_type', models.CharField(max_length=50)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('connected_at', models.DateTimeField(auto_now_add=True)),
                ('disconnected_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'WebSocket Connection Log',
                'db_table': 'core_websocket_connection_logs',
                'ordering': ['-connected_at'],
            },
        ),
    ]
