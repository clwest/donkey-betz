"""
Session 704: SPINE - Central API Router Migration

Creates RoutePattern, RouteMetrics, SpineStatus, and RequestTrace models
with default route patterns for major API categories.
"""

import uuid
from django.db import migrations, models
import django.db.models.deletion


def create_default_patterns(apps, schema_editor):
    """Create default route patterns for monitoring."""
    RoutePattern = apps.get_model('core', 'RoutePattern')
    SpineStatus = apps.get_model('core', 'SpineStatus')

    default_patterns = [
        # Authentication Routes
        {
            'pattern': '/api/v1/auth/',
            'display_name': 'Authentication API',
            'category': 'auth',
            'priority': 'critical',
            'max_latency_ms': 2000,
            'max_error_rate': 0.01,
            'description': 'User authentication and session management',
        },
        {
            'pattern': '/health/',
            'display_name': 'Health Checks',
            'category': 'monitoring',
            'priority': 'critical',
            'max_latency_ms': 500,
            'max_error_rate': 0.001,
            'description': 'System health endpoints',
        },

        # Agent Orchestration
        {
            'pattern': '/api/agents/',
            'display_name': 'Agent Orchestration',
            'category': 'agents',
            'priority': 'high',
            'max_latency_ms': 30000,
            'max_error_rate': 0.05,
            'requires_healthy_heart': True,
            'description': '72 specialized AI agents',
        },
        {
            'pattern': '/api/agent-execution/',
            'display_name': 'Agent Execution',
            'category': 'agents',
            'priority': 'high',
            'max_latency_ms': 60000,
            'max_error_rate': 0.05,
            'requires_healthy_heart': True,
            'requires_healthy_lungs': True,
            'description': 'Agent task execution with LLM calls',
        },

        # Spider Network
        {
            'pattern': '/api/spider/',
            'display_name': 'Spider Network',
            'category': 'spiders',
            'priority': 'normal',
            'max_latency_ms': 30000,
            'max_error_rate': 0.10,
            'description': '77 data source spiders',
        },

        # Content & Media
        {
            'pattern': '/api/v1/content/',
            'display_name': 'Content API',
            'category': 'content',
            'priority': 'normal',
            'max_latency_ms': 10000,
            'max_error_rate': 0.05,
            'description': 'Content management endpoints',
        },
        {
            'pattern': '/api/gallery/',
            'display_name': 'Gallery API',
            'category': 'content',
            'priority': 'normal',
            'max_latency_ms': 5000,
            'max_error_rate': 0.05,
            'description': 'Image and media gallery',
        },

        # Business Logic
        {
            'pattern': '/api/opportunities/',
            'display_name': 'Opportunities API',
            'category': 'business',
            'priority': 'high',
            'max_latency_ms': 10000,
            'max_error_rate': 0.05,
            'description': 'Opportunity discovery and management',
        },
        {
            'pattern': '/api/projects/',
            'display_name': 'Projects API',
            'category': 'business',
            'priority': 'normal',
            'max_latency_ms': 5000,
            'max_error_rate': 0.05,
            'description': 'Project management',
        },

        # Creative Pipeline
        {
            'pattern': '/api/creative-projects/',
            'display_name': 'Creative Projects',
            'category': 'creative',
            'priority': 'normal',
            'max_latency_ms': 60000,
            'max_error_rate': 0.10,
            'requires_healthy_lungs': True,
            'description': 'Creative generation pipeline',
        },
        {
            'pattern': '/api/workflows/',
            'display_name': 'Workflow Engine',
            'category': 'creative',
            'priority': 'normal',
            'max_latency_ms': 30000,
            'max_error_rate': 0.05,
            'description': 'Multi-step workflow orchestration',
        },

        # Sci-Fi Features
        {
            'pattern': '/api/agent-dreams/',
            'display_name': 'Agent Dreams',
            'category': 'scifi',
            'priority': 'low',
            'max_latency_ms': 120000,
            'max_error_rate': 0.15,
            'description': 'Agent dream generation system',
        },
        {
            'pattern': '/api/memory-palace/',
            'display_name': 'Memory Palace',
            'category': 'scifi',
            'priority': 'low',
            'max_latency_ms': 30000,
            'max_error_rate': 0.10,
            'description': 'Spatial memory organization',
        },

        # System Monitoring
        {
            'pattern': '/api/heart/',
            'display_name': 'HEART Service',
            'category': 'monitoring',
            'priority': 'critical',
            'max_latency_ms': 5000,
            'max_error_rate': 0.01,
            'description': 'System health monitoring',
        },
        {
            'pattern': '/api/lungs/',
            'display_name': 'LUNGS Service',
            'category': 'monitoring',
            'priority': 'critical',
            'max_latency_ms': 5000,
            'max_error_rate': 0.01,
            'description': 'Resource and capacity management',
        },
        {
            'pattern': '/api/circulatory/',
            'display_name': 'CIRCULATORY System',
            'category': 'monitoring',
            'priority': 'critical',
            'max_latency_ms': 15000,
            'max_error_rate': 0.01,
            'description': 'Data flow monitoring',
        },

        # LLM Routing
        {
            'pattern': '/api/v1/llm-routing/',
            'display_name': 'LLM Routing',
            'category': 'llm',
            'priority': 'high',
            'max_latency_ms': 2000,
            'max_error_rate': 0.01,
            'description': 'LLM provider and model routing',
        },

        # Admin & System
        {
            'pattern': '/api/v1/system/',
            'display_name': 'System Admin',
            'category': 'admin',
            'priority': 'normal',
            'max_latency_ms': 10000,
            'max_error_rate': 0.05,
            'description': 'System administration endpoints',
        },

        # WebSocket
        {
            'pattern': '/ws/',
            'display_name': 'WebSocket Connections',
            'category': 'websocket',
            'priority': 'high',
            'max_latency_ms': 1000,
            'max_error_rate': 0.05,
            'description': 'Real-time WebSocket connections',
        },
    ]

    for pattern_data in default_patterns:
        RoutePattern.objects.create(**pattern_data)

    # Create initial spine status
    SpineStatus.objects.create(
        status='aligned',
        is_healthy=True,
        health_score=100.0,
        total_patterns=len(default_patterns),
        healthy_patterns=len(default_patterns),
    )


def remove_default_patterns(apps, schema_editor):
    """Remove default patterns."""
    RoutePattern = apps.get_model('core', 'RoutePattern')
    SpineStatus = apps.get_model('core', 'SpineStatus')
    RoutePattern.objects.all().delete()
    SpineStatus.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0149_session_703_circulatory_system'),
    ]

    operations = [
        # Create RoutePattern model
        migrations.CreateModel(
            name='RoutePattern',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('pattern', models.CharField(max_length=200, unique=True, help_text='URL pattern (regex or prefix)')),
                ('display_name', models.CharField(blank=True, max_length=150)),
                ('category', models.CharField(
                    choices=[
                        ('agents', 'Agent Orchestration'),
                        ('spiders', 'Spider Network'),
                        ('content', 'Content & Media'),
                        ('business', 'Business Logic'),
                        ('creative', 'Creative Pipeline'),
                        ('scifi', 'Sci-Fi Features'),
                        ('monitoring', 'System Monitoring'),
                        ('llm', 'LLM Routing'),
                        ('admin', 'Admin & System'),
                        ('websocket', 'WebSocket'),
                        ('auth', 'Authentication'),
                        ('other', 'Other'),
                    ],
                    default='other',
                    max_length=20
                )),
                ('priority', models.CharField(
                    choices=[
                        ('critical', 'Critical'),
                        ('high', 'High'),
                        ('normal', 'Normal'),
                        ('low', 'Low'),
                    ],
                    default='normal',
                    max_length=20
                )),
                ('max_latency_ms', models.IntegerField(default=5000, help_text='Max acceptable latency in ms')),
                ('max_error_rate', models.FloatField(default=0.05, help_text='Max acceptable error rate (0-1)')),
                ('min_availability', models.FloatField(default=0.95, help_text='Minimum uptime (0-1)')),
                ('rate_limit_per_minute', models.IntegerField(default=0, help_text='Requests per minute (0=unlimited)')),
                ('rate_limit_per_hour', models.IntegerField(default=0, help_text='Requests per hour (0=unlimited)')),
                ('requires_healthy_heart', models.BooleanField(default=False, help_text='Require HEART healthy status')),
                ('requires_healthy_lungs', models.BooleanField(default=False, help_text='Require LUNGS budget available')),
                ('fallback_response', models.JSONField(default=dict, blank=True, help_text='Response when route unavailable')),
                ('is_active', models.BooleanField(default=True)),
                ('is_monitored', models.BooleanField(default=True, help_text='Track metrics for this pattern')),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Route Pattern',
                'verbose_name_plural': 'Route Patterns',
                'db_table': 'core_route_pattern',
                'ordering': ['category', 'pattern'],
            },
        ),

        # Create RouteMetrics model
        migrations.CreateModel(
            name='RouteMetrics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('pattern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics_history', to='core.routepattern')),
                ('total_requests', models.BigIntegerField(default=0)),
                ('successful_requests', models.BigIntegerField(default=0)),
                ('failed_requests', models.BigIntegerField(default=0)),
                ('rate_limited_requests', models.IntegerField(default=0)),
                ('status_2xx', models.IntegerField(default=0)),
                ('status_3xx', models.IntegerField(default=0)),
                ('status_4xx', models.IntegerField(default=0)),
                ('status_5xx', models.IntegerField(default=0)),
                ('avg_latency_ms', models.FloatField(default=0)),
                ('p50_latency_ms', models.FloatField(default=0)),
                ('p95_latency_ms', models.FloatField(default=0)),
                ('p99_latency_ms', models.FloatField(default=0)),
                ('max_latency_ms', models.FloatField(default=0)),
                ('success_rate', models.FloatField(default=1.0, help_text='Ratio of successful to total requests')),
                ('error_rate', models.FloatField(default=0, help_text='Ratio of failed to total requests')),
                ('throughput', models.FloatField(default=0, help_text='Requests per second')),
                ('is_healthy', models.BooleanField(default=True)),
                ('health_score', models.FloatField(default=100.0, help_text='0-100% health score')),
                ('period_start', models.DateTimeField()),
                ('period_end', models.DateTimeField()),
                ('period_duration_seconds', models.IntegerField(default=60)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Route Metrics',
                'verbose_name_plural': 'Route Metrics',
                'db_table': 'core_route_metrics',
                'ordering': ['-recorded_at'],
            },
        ),

        # Create indexes for RouteMetrics
        migrations.AddIndex(
            model_name='routemetrics',
            index=models.Index(fields=['-recorded_at'], name='core_route__recorde_idx'),
        ),
        migrations.AddIndex(
            model_name='routemetrics',
            index=models.Index(fields=['pattern', '-recorded_at'], name='core_route__pattern_idx'),
        ),
        migrations.AddIndex(
            model_name='routemetrics',
            index=models.Index(fields=['is_healthy', '-recorded_at'], name='core_route__is_heal_idx'),
        ),

        # Create SpineStatus model
        migrations.CreateModel(
            name='SpineStatus',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(
                    choices=[
                        ('aligned', 'Aligned'),
                        ('strained', 'Strained'),
                        ('compressed', 'Compressed'),
                        ('injured', 'Injured'),
                    ],
                    default='aligned',
                    max_length=20
                )),
                ('is_healthy', models.BooleanField(default=True)),
                ('health_score', models.FloatField(default=100.0, help_text='0-100% spine health')),
                ('total_patterns', models.IntegerField(default=0)),
                ('healthy_patterns', models.IntegerField(default=0)),
                ('degraded_patterns', models.IntegerField(default=0)),
                ('failed_patterns', models.IntegerField(default=0)),
                ('total_requests', models.BigIntegerField(default=0)),
                ('requests_per_second', models.FloatField(default=0)),
                ('avg_latency_ms', models.FloatField(default=0)),
                ('error_rate', models.FloatField(default=0)),
                ('category_health', models.JSONField(default=dict, help_text='Health score by category')),
                ('heart_status', models.CharField(blank=True, max_length=20, help_text='HEART service status')),
                ('lungs_status', models.CharField(blank=True, max_length=20, help_text='LUNGS service status')),
                ('circulatory_status', models.CharField(blank=True, max_length=20, help_text='CIRCULATORY status')),
                ('routes_blocked', models.IntegerField(default=0, help_text='Routes blocked due to health')),
                ('routes_rate_limited', models.IntegerField(default=0, help_text='Routes currently rate limited')),
                ('fallbacks_active', models.IntegerField(default=0, help_text='Routes using fallback responses')),
                ('last_check', models.DateTimeField(auto_now=True)),
                ('status_changed_at', models.DateTimeField(blank=True, null=True)),
                ('alert_sent', models.BooleanField(default=False)),
                ('last_alert_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Spine Status',
                'verbose_name_plural': 'Spine Statuses',
                'db_table': 'core_spine_status',
            },
        ),

        # Create RequestTrace model
        migrations.CreateModel(
            name='RequestTrace',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('correlation_id', models.CharField(max_length=64, unique=True, db_index=True)),
                ('method', models.CharField(max_length=10)),
                ('path', models.CharField(max_length=500)),
                ('pattern', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='traces', to='core.routepattern')),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('is_authenticated', models.BooleanField(default=False)),
                ('client_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('started_at', models.DateTimeField()),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('duration_ms', models.FloatField(blank=True, null=True)),
                ('status_code', models.IntegerField(blank=True, null=True)),
                ('response_size', models.IntegerField(blank=True, null=True)),
                ('was_rate_limited', models.BooleanField(default=False)),
                ('used_fallback', models.BooleanField(default=False)),
                ('health_check_result', models.JSONField(blank=True, default=dict)),
                ('routed_to_agent', models.CharField(blank=True, max_length=100)),
                ('llm_model_used', models.CharField(blank=True, max_length=100)),
                ('error_type', models.CharField(blank=True, max_length=100)),
                ('error_message', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Request Trace',
                'verbose_name_plural': 'Request Traces',
                'db_table': 'core_request_trace',
                'ordering': ['-started_at'],
            },
        ),

        # Create indexes for RequestTrace
        migrations.AddIndex(
            model_name='requesttrace',
            index=models.Index(fields=['-started_at'], name='core_reques_started_idx'),
        ),
        migrations.AddIndex(
            model_name='requesttrace',
            index=models.Index(fields=['path', '-started_at'], name='core_reques_path_idx'),
        ),
        migrations.AddIndex(
            model_name='requesttrace',
            index=models.Index(fields=['status_code', '-started_at'], name='core_reques_status__idx'),
        ),

        # Create default patterns
        migrations.RunPython(create_default_patterns, remove_default_patterns),
    ]
