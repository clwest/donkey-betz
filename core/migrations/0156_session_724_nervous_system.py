"""
Session 724: NERVOUS SYSTEM Migration

Creates NervousPulse, NervousStatus, and WebSocketConnectionLog models
for WebSocket communication monitoring.

The NERVOUS system is the 10th body system - tracks real-time communication
health including WebSocket connections, message throughput, and Redis channel layer.
"""

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0155_session_723_skin_system'),
    ]

    operations = [
        # Create NervousPulse - Time-series records
        migrations.CreateModel(
            name='NervousPulse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[
                    ('responsive', 'Responsive'),
                    ('active', 'Active'),
                    ('sluggish', 'Sluggish'),
                    ('numb', 'Numb'),
                    ('overloaded', 'Overloaded'),
                    ('damaged', 'Damaged'),
                    ('dormant', 'Dormant'),
                ], default='responsive', max_length=20)),
                ('health_score', models.FloatField(default=100.0, help_text='Overall nervous health 0-100')),
                ('total_consumers', models.IntegerField(default=0, help_text='Total registered consumer types')),
                ('active_connections', models.IntegerField(default=0, help_text='Current WebSocket connections')),
                ('peak_connections_24h', models.IntegerField(default=0, help_text='Max connections in 24h')),
                ('disconnections_24h', models.IntegerField(default=0, help_text='Connection drops in 24h')),
                ('connection_errors_24h', models.IntegerField(default=0, help_text='Connection errors in 24h')),
                ('messages_sent_24h', models.IntegerField(default=0, help_text='Messages sent in 24h')),
                ('messages_received_24h', models.IntegerField(default=0, help_text='Messages received in 24h')),
                ('messages_per_second', models.FloatField(default=0, help_text='Current throughput')),
                ('peak_messages_per_second', models.FloatField(default=0, help_text='Peak throughput in 24h')),
                ('avg_latency_ms', models.FloatField(default=0, help_text='Average message latency')),
                ('max_latency_ms', models.FloatField(default=0, help_text='Max latency in 24h')),
                ('p95_latency_ms', models.FloatField(default=0, help_text='95th percentile latency')),
                ('channel_layer_connected', models.BooleanField(default=True)),
                ('redis_ping_ms', models.FloatField(default=0, help_text='Redis ping latency')),
                ('active_groups', models.IntegerField(default=0, help_text='Active channel groups')),
                ('group_members', models.IntegerField(default=0, help_text='Total group memberships')),
                ('consumer_stats', models.JSONField(default=dict, help_text='Per-consumer metrics')),
                ('busiest_consumers', models.JSONField(default=list, help_text='Most active consumers')),
                ('error_consumers', models.JSONField(default=list, help_text='Consumers with errors')),
                ('check_duration_ms', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Nervous Pulse',
                'verbose_name_plural': 'Nervous Pulses',
                'db_table': 'core_nervous_pulses',
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='nervouspulse',
            index=models.Index(fields=['-recorded_at'], name='core_nervous_recorded_idx'),
        ),
        migrations.AddIndex(
            model_name='nervouspulse',
            index=models.Index(fields=['status', '-recorded_at'], name='core_nervous_status_idx'),
        ),

        # Create NervousStatus - Cached current state
        migrations.CreateModel(
            name='NervousStatus',
            fields=[
                ('id', models.IntegerField(default=1, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[
                    ('responsive', 'Responsive'),
                    ('active', 'Active'),
                    ('sluggish', 'Sluggish'),
                    ('numb', 'Numb'),
                    ('overloaded', 'Overloaded'),
                    ('damaged', 'Damaged'),
                    ('dormant', 'Dormant'),
                ], default='responsive', max_length=20)),
                ('is_healthy', models.BooleanField(default=True)),
                ('health_score', models.FloatField(default=100.0)),
                ('total_consumers', models.IntegerField(default=0)),
                ('active_connections', models.IntegerField(default=0)),
                ('connection_rate', models.FloatField(default=0, help_text='Connections per minute')),
                ('messages_24h', models.IntegerField(default=0)),
                ('messages_per_second', models.FloatField(default=0)),
                ('avg_latency_ms', models.FloatField(default=0)),
                ('channel_layer_healthy', models.BooleanField(default=True)),
                ('redis_latency_ms', models.FloatField(default=0)),
                ('active_groups', models.IntegerField(default=0)),
                ('error_rate', models.FloatField(default=0, help_text='Error percentage')),
                ('disconnections_24h', models.IntegerField(default=0)),
                ('activity_level', models.CharField(default='normal', help_text='dormant, low, normal, high, intense', max_length=20)),
                ('last_message_at', models.DateTimeField(blank=True, null=True)),
                ('last_error_at', models.DateTimeField(blank=True, null=True)),
                ('last_check', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Nervous Status',
                'verbose_name_plural': 'Nervous Status',
                'db_table': 'core_nervous_status',
            },
        ),

        # Create WebSocketConnectionLog - Connection event logs
        migrations.CreateModel(
            name='WebSocketConnectionLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('consumer_name', models.CharField(max_length=100)),
                ('channel_name', models.CharField(blank=True, max_length=200)),
                ('group_name', models.CharField(blank=True, max_length=100)),
                ('event', models.CharField(choices=[
                    ('connect', 'Connected'),
                    ('disconnect', 'Disconnected'),
                    ('error', 'Error'),
                    ('timeout', 'Timeout'),
                    ('rejected', 'Rejected'),
                ], max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('client_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('connection_duration_ms', models.IntegerField(blank=True, null=True)),
                ('messages_during_session', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'WebSocket Connection Log',
                'verbose_name_plural': 'WebSocket Connection Logs',
                'db_table': 'core_websocket_connection_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='websocketconnectionlog',
            index=models.Index(fields=['-created_at'], name='core_ws_log_created_idx'),
        ),
        migrations.AddIndex(
            model_name='websocketconnectionlog',
            index=models.Index(fields=['consumer_name', '-created_at'], name='core_ws_log_consumer_idx'),
        ),
        migrations.AddIndex(
            model_name='websocketconnectionlog',
            index=models.Index(fields=['event', '-created_at'], name='core_ws_log_event_idx'),
        ),
    ]
