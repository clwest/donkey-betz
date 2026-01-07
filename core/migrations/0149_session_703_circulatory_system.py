"""
Session 703: CIRCULATORY SYSTEM Migration

Creates FlowRoute, CirculationPulse, and FlowStatus models
with default routes for Redis, Celery, WebSocket, and Event Streams.
"""

import uuid
from django.db import migrations, models
import django.db.models.deletion


def create_default_routes(apps, schema_editor):
    """Create default flow routes for monitoring."""
    FlowRoute = apps.get_model('core', 'FlowRoute')
    FlowStatus = apps.get_model('core', 'FlowStatus')

    default_routes = [
        # Redis Queues
        {
            'name': 'redis_cache',
            'display_name': 'Redis Cache (DB 1)',
            'route_type': 'redis_queue',
            'identifier': 'redis://localhost:6379/1',
            'max_depth': 10000,
            'max_latency_ms': 100,
            'is_critical': True,
            'description': 'Django cache backend - used for caching API responses, embeddings, etc.',
        },
        {
            'name': 'redis_celery_broker',
            'display_name': 'Celery Broker (DB 2)',
            'route_type': 'redis_queue',
            'identifier': 'redis://localhost:6379/2',
            'max_depth': 5000,
            'max_latency_ms': 50,
            'is_critical': True,
            'description': 'Celery task broker - queues all background tasks.',
        },
        {
            'name': 'redis_celery_results',
            'display_name': 'Celery Results (DB 3)',
            'route_type': 'redis_queue',
            'identifier': 'redis://localhost:6379/3',
            'max_depth': 10000,
            'max_latency_ms': 100,
            'is_critical': False,
            'description': 'Celery task results backend.',
        },

        # Celery Queues
        {
            'name': 'celery_default',
            'display_name': 'Celery Default Queue',
            'route_type': 'celery_queue',
            'identifier': 'celery',
            'max_depth': 1000,
            'max_latency_ms': 5000,
            'is_critical': True,
            'description': 'Default Celery queue for quick tasks.',
        },
        {
            'name': 'celery_long_running',
            'display_name': 'Celery Long Running Queue',
            'route_type': 'celery_queue',
            'identifier': 'long_running',
            'max_depth': 100,
            'max_latency_ms': 60000,
            'is_critical': False,
            'description': 'Queue for tasks that run 1-60+ minutes (spider network, agent dreams).',
        },
        {
            'name': 'celery_broadcast',
            'display_name': 'Celery Broadcast Queue',
            'route_type': 'celery_queue',
            'identifier': 'broadcast',
            'max_depth': 500,
            'max_latency_ms': 1000,
            'is_critical': True,
            'description': 'High-frequency broadcast queue (system state, heartbeat).',
        },

        # WebSocket
        {
            'name': 'websocket_channels',
            'display_name': 'WebSocket Channel Layer',
            'route_type': 'websocket',
            'identifier': 'channels_redis',
            'max_depth': 1000,
            'max_latency_ms': 500,
            'is_critical': False,
            'description': 'Redis-backed WebSocket channel layer for real-time updates.',
        },

        # Event Streams
        {
            'name': 'event_spider_data',
            'display_name': 'Event Stream: Spider Data',
            'route_type': 'event_stream',
            'identifier': 'mi:spider_data',
            'max_depth': 500,
            'max_latency_ms': 5000,
            'is_critical': False,
            'description': 'Event stream for new spider data collection.',
        },
        {
            'name': 'event_opportunity_scored',
            'display_name': 'Event Stream: Opportunity Scored',
            'route_type': 'event_stream',
            'identifier': 'mi:opportunity_scored',
            'max_depth': 200,
            'max_latency_ms': 2000,
            'is_critical': True,
            'description': 'Event stream for scored opportunities - feeds ML pipeline.',
        },
    ]

    for route_data in default_routes:
        route = FlowRoute.objects.create(**route_data)
        # Create corresponding FlowStatus
        FlowStatus.objects.create(
            route=route,
            status='flowing',
            is_healthy=True,
            health_score=100.0,
        )


def remove_default_routes(apps, schema_editor):
    """Remove default routes."""
    FlowRoute = apps.get_model('core', 'FlowRoute')
    FlowRoute.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0148_session_702_lungs_service'),
    ]

    operations = [
        # Create FlowRoute model
        migrations.CreateModel(
            name='FlowRoute',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(blank=True, max_length=150)),
                ('route_type', models.CharField(
                    choices=[
                        ('redis_queue', 'Redis Queue'),
                        ('celery_queue', 'Celery Queue'),
                        ('websocket', 'WebSocket Channel'),
                        ('event_stream', 'Event Stream'),
                    ],
                    max_length=20
                )),
                ('identifier', models.CharField(help_text='Queue name, channel, or stream identifier', max_length=200)),
                ('max_depth', models.IntegerField(default=1000, help_text='Queue depth warning threshold')),
                ('max_latency_ms', models.IntegerField(default=5000, help_text='Latency warning threshold in milliseconds')),
                ('min_throughput', models.FloatField(default=0, help_text='Minimum items/sec (0 = no minimum)')),
                ('is_active', models.BooleanField(default=True)),
                ('is_critical', models.BooleanField(default=False, help_text='Send Discord alert on failure')),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Flow Route',
                'verbose_name_plural': 'Flow Routes',
                'db_table': 'core_flow_route',
                'ordering': ['route_type', 'name'],
            },
        ),

        # Create CirculationPulse model
        migrations.CreateModel(
            name='CirculationPulse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('overall_status', models.CharField(
                    choices=[
                        ('flowing', 'Flowing'),
                        ('slow', 'Slow'),
                        ('congested', 'Congested'),
                        ('blocked', 'Blocked'),
                    ],
                    default='flowing',
                    max_length=20
                )),
                ('flow_score', models.FloatField(default=100.0, help_text='0-100% overall flow health')),
                ('total_routes_checked', models.IntegerField(default=0)),
                ('routes_healthy', models.IntegerField(default=0)),
                ('routes_slow', models.IntegerField(default=0)),
                ('routes_congested', models.IntegerField(default=0)),
                ('routes_blocked', models.IntegerField(default=0)),
                ('total_items_in_transit', models.BigIntegerField(default=0, help_text='Total items across all queues')),
                ('total_throughput', models.FloatField(default=0, help_text='Combined items/sec across all routes')),
                ('avg_latency_ms', models.FloatField(default=0, help_text='Average latency across all routes')),
                ('max_latency_ms', models.FloatField(default=0, help_text='Maximum latency detected')),
                ('bottlenecks', models.JSONField(default=list, help_text='List of detected bottlenecks')),
                ('bottleneck_count', models.IntegerField(default=0)),
                ('route_details', models.JSONField(default=dict, help_text='Per-route status details')),
                ('check_duration_ms', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Circulation Pulse',
                'verbose_name_plural': 'Circulation Pulses',
                'db_table': 'core_circulation_pulse',
                'ordering': ['-recorded_at'],
            },
        ),

        # Create indexes for CirculationPulse
        migrations.AddIndex(
            model_name='circulationpulse',
            index=models.Index(fields=['-recorded_at'], name='core_circul_recorde_idx'),
        ),
        migrations.AddIndex(
            model_name='circulationpulse',
            index=models.Index(fields=['overall_status', '-recorded_at'], name='core_circul_overall_idx'),
        ),
        migrations.AddIndex(
            model_name='circulationpulse',
            index=models.Index(fields=['flow_score', '-recorded_at'], name='core_circul_flow_sc_idx'),
        ),

        # Create FlowStatus model
        migrations.CreateModel(
            name='FlowStatus',
            fields=[
                ('route', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    related_name='current_status',
                    serialize=False,
                    to='core.flowroute'
                )),
                ('status', models.CharField(
                    choices=[
                        ('flowing', 'Flowing'),
                        ('slow', 'Slow'),
                        ('congested', 'Congested'),
                        ('blocked', 'Blocked'),
                    ],
                    default='flowing',
                    max_length=20
                )),
                ('is_healthy', models.BooleanField(default=True)),
                ('health_score', models.FloatField(default=100.0, help_text='0-100% route health')),
                ('current_depth', models.IntegerField(default=0, help_text='Current queue depth')),
                ('current_throughput', models.FloatField(default=0, help_text='Current items/sec')),
                ('current_latency_ms', models.FloatField(default=0, help_text='Current latency in ms')),
                ('items_processed_24h', models.BigIntegerField(default=0)),
                ('errors_24h', models.IntegerField(default=0)),
                ('avg_latency_24h_ms', models.FloatField(default=0)),
                ('peak_depth_24h', models.IntegerField(default=0)),
                ('peak_latency_24h_ms', models.FloatField(default=0)),
                ('active_workers', models.IntegerField(default=0)),
                ('active_tasks', models.IntegerField(default=0)),
                ('reserved_tasks', models.IntegerField(default=0)),
                ('last_activity', models.DateTimeField(blank=True, null=True)),
                ('last_check', models.DateTimeField(auto_now=True)),
                ('status_changed_at', models.DateTimeField(blank=True, null=True)),
                ('congestion_alert_sent', models.BooleanField(default=False)),
                ('blocked_alert_sent', models.BooleanField(default=False)),
                ('last_alert_at', models.DateTimeField(blank=True, null=True)),
                ('details', models.JSONField(default=dict, help_text='Additional route-specific details')),
                ('error_message', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Flow Status',
                'verbose_name_plural': 'Flow Statuses',
                'db_table': 'core_flow_status',
            },
        ),

        # Create default routes
        migrations.RunPython(create_default_routes, remove_default_routes),
    ]
