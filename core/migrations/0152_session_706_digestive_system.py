"""
Session 706: DIGESTIVE SYSTEM - Data Ingestion & Processing

Creates tables for the DIGESTIVE system which monitors data ingestion
from spiders and transformation into actionable intelligence.

Models:
- IngestionRoute: Configuration for monitored data ingestion routes
- DigestivePulse: Time-series records of digestion state
- DigestionStatus: Current digestion status per route

Default Routes:
- 5 spider intake routes (news, financial, tech, legal, community)
- 3 pipeline routes (processing, enrichment, routing)
"""

import uuid
from django.db import migrations, models
import django.db.models.deletion


def create_default_routes(apps, schema_editor):
    """Create default ingestion routes for monitoring."""
    IngestionRoute = apps.get_model('core', 'IngestionRoute')
    DigestionStatus = apps.get_model('core', 'DigestionStatus')

    default_routes = [
        # Spider Intake Routes (by category)
        {
            'name': 'spider_news_intake',
            'display_name': 'Spider News Intake',
            'route_type': 'spider',
            'stage': 'intake',
            'identifier': 'news',
            'description': 'News spider data intake (TechCrunch, BBC, CNN, etc.)',
            'max_queue_depth': 500,
            'target_throughput': 15.0,
            'is_critical': False,
            'is_builtin': True,
        },
        {
            'name': 'spider_financial_intake',
            'display_name': 'Spider Financial Intake',
            'route_type': 'spider',
            'stage': 'intake',
            'identifier': 'financial',
            'description': 'Financial spider data intake (CoinGecko, Yahoo Finance, etc.)',
            'max_queue_depth': 300,
            'target_throughput': 20.0,
            'is_critical': True,
            'is_builtin': True,
        },
        {
            'name': 'spider_tech_intake',
            'display_name': 'Spider Tech Intake',
            'route_type': 'spider',
            'stage': 'intake',
            'identifier': 'tech',
            'description': 'Tech spider data intake (HackerNews, DevTo, GitHub, etc.)',
            'max_queue_depth': 400,
            'target_throughput': 12.0,
            'is_critical': False,
            'is_builtin': True,
        },
        {
            'name': 'spider_legal_intake',
            'display_name': 'Spider Legal Intake',
            'route_type': 'spider',
            'stage': 'intake',
            'identifier': 'legal',
            'description': 'Legal spider data intake (CourtListener, FindLaw, etc.)',
            'max_queue_depth': 200,
            'target_throughput': 5.0,
            'is_critical': True,
            'is_builtin': True,
        },
        {
            'name': 'spider_community_intake',
            'display_name': 'Spider Community Intake',
            'route_type': 'spider',
            'stage': 'intake',
            'identifier': 'community',
            'description': 'Community spider data intake (Reddit, BlueSky, Discord, etc.)',
            'max_queue_depth': 600,
            'target_throughput': 10.0,
            'is_critical': False,
            'is_builtin': True,
        },
        # Pipeline Routes (processing stages)
        {
            'name': 'data_processing_queue',
            'display_name': 'Data Processing Queue',
            'route_type': 'stream',
            'stage': 'processing',
            'identifier': 'spider_processing',
            'description': 'Main processing queue for spider data normalization',
            'max_queue_depth': 1000,
            'target_throughput': 30.0,
            'is_critical': True,
            'is_builtin': True,
        },
        {
            'name': 'embedding_pipeline',
            'display_name': 'Embedding Pipeline',
            'route_type': 'stream',
            'stage': 'enrichment',
            'identifier': 'embedding_queue',
            'description': 'Embedding generation and semantic enrichment pipeline',
            'max_queue_depth': 500,
            'target_throughput': 10.0,
            'max_processing_time_ms': 10000,
            'is_critical': False,
            'is_builtin': True,
        },
        {
            'name': 'agent_data_routing',
            'display_name': 'Agent Data Routing',
            'route_type': 'stream',
            'stage': 'routing',
            'identifier': 'agent_data',
            'description': 'Data routing to agents and services',
            'max_queue_depth': 300,
            'target_throughput': 25.0,
            'is_critical': True,
            'is_builtin': True,
        },
    ]

    for route_data in default_routes:
        route = IngestionRoute.objects.create(**route_data)
        # Create corresponding status record
        DigestionStatus.objects.create(
            route=route,
            status='healthy',
            is_healthy=True,
        )


def reverse_default_routes(apps, schema_editor):
    """Remove default routes."""
    IngestionRoute = apps.get_model('core', 'IngestionRoute')
    IngestionRoute.objects.filter(is_builtin=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0151_session_705_immune_system'),
    ]

    operations = [
        # Create IngestionRoute table
        migrations.CreateModel(
            name='IngestionRoute',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(blank=True, max_length=150)),
                ('route_type', models.CharField(choices=[
                    ('spider', 'Spider Data'),
                    ('api', 'External API'),
                    ('webhook', 'Webhook'),
                    ('upload', 'File Upload'),
                    ('stream', 'Event Stream'),
                ], max_length=20)),
                ('stage', models.CharField(choices=[
                    ('intake', 'Intake'),
                    ('processing', 'Processing'),
                    ('enrichment', 'Enrichment'),
                    ('routing', 'Routing'),
                ], max_length=20)),
                ('identifier', models.CharField(help_text='Spider category, API name, stream ID', max_length=200)),
                ('description', models.TextField(blank=True)),
                ('max_queue_depth', models.IntegerField(default=500, help_text='Max items waiting before warning')),
                ('target_throughput', models.FloatField(default=10.0, help_text='Target items/minute')),
                ('max_processing_time_ms', models.IntegerField(default=5000, help_text='Max processing time per item')),
                ('is_active', models.BooleanField(default=True)),
                ('is_critical', models.BooleanField(default=False, help_text='Alert on failure')),
                ('is_builtin', models.BooleanField(default=False, help_text='System-defined route')),
                ('total_items_processed', models.BigIntegerField(default=0)),
                ('total_errors', models.BigIntegerField(default=0)),
                ('last_activity', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Ingestion Route',
                'verbose_name_plural': 'Ingestion Routes',
                'db_table': 'core_ingestion_route',
                'ordering': ['stage', 'route_type', 'name'],
            },
        ),

        # Create DigestivePulse table (time-series)
        migrations.CreateModel(
            name='DigestivePulse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('overall_status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('sluggish', 'Sluggish'),
                    ('bloated', 'Bloated'),
                    ('blocked', 'Blocked'),
                    ('starving', 'Starving'),
                ], default='healthy', max_length=20)),
                ('digestion_score', models.FloatField(default=100.0, help_text='0-100% digestion health')),
                ('is_digesting', models.BooleanField(default=True)),
                # Intake metrics
                ('items_ingested_24h', models.IntegerField(default=0)),
                ('spiders_executed_24h', models.IntegerField(default=0)),
                ('spider_success_rate', models.FloatField(default=100.0)),
                ('intake_errors_24h', models.IntegerField(default=0)),
                ('duplicates_filtered_24h', models.IntegerField(default=0)),
                # Processing metrics
                ('items_processed_24h', models.IntegerField(default=0)),
                ('items_pending', models.IntegerField(default=0, help_text='Queue depth')),
                ('processing_throughput', models.FloatField(default=0, help_text='Items/minute')),
                ('avg_processing_time_ms', models.FloatField(default=0)),
                ('processing_errors_24h', models.IntegerField(default=0)),
                # Enrichment metrics
                ('embeddings_generated_24h', models.IntegerField(default=0)),
                ('embedding_coverage_pct', models.FloatField(default=0, help_text='% of items with embeddings')),
                ('relevance_scores_calculated_24h', models.IntegerField(default=0)),
                ('enrichment_errors_24h', models.IntegerField(default=0)),
                # Output metrics
                ('items_routed_24h', models.IntegerField(default=0)),
                ('items_filtered_24h', models.IntegerField(default=0, help_text='Low relevance filtered out')),
                ('items_actionable_24h', models.IntegerField(default=0)),
                ('routing_errors_24h', models.IntegerField(default=0)),
                # Metabolism rates
                ('intake_rate', models.FloatField(default=0, help_text='Items ingested per minute')),
                ('processing_rate', models.FloatField(default=0, help_text='Items processed per minute')),
                ('output_rate', models.FloatField(default=0, help_text='Items output per minute')),
                # Stage statuses
                ('intake_status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('sluggish', 'Sluggish'),
                    ('bloated', 'Bloated'),
                    ('blocked', 'Blocked'),
                    ('starving', 'Starving'),
                ], default='healthy', max_length=20)),
                ('processing_status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('sluggish', 'Sluggish'),
                    ('bloated', 'Bloated'),
                    ('blocked', 'Blocked'),
                    ('starving', 'Starving'),
                ], default='healthy', max_length=20)),
                ('enrichment_status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('sluggish', 'Sluggish'),
                    ('bloated', 'Bloated'),
                    ('blocked', 'Blocked'),
                    ('starving', 'Starving'),
                ], default='healthy', max_length=20)),
                ('routing_status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('sluggish', 'Sluggish'),
                    ('bloated', 'Bloated'),
                    ('blocked', 'Blocked'),
                    ('starving', 'Starving'),
                ], default='healthy', max_length=20)),
                # Bottlenecks
                ('bottlenecks', models.JSONField(default=list)),
                # Routes info
                ('routes_checked', models.IntegerField(default=0)),
                ('routes_healthy', models.IntegerField(default=0)),
                ('routes_warning', models.IntegerField(default=0)),
                ('routes_critical', models.IntegerField(default=0)),
                # Integration status
                ('heart_connected', models.BooleanField(default=False)),
                ('circulatory_connected', models.BooleanField(default=False)),
                # Metadata
                ('check_duration_ms', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Digestive Pulse',
                'verbose_name_plural': 'Digestive Pulses',
                'db_table': 'core_digestive_pulse',
                'ordering': ['-recorded_at'],
            },
        ),

        # Add indexes to DigestivePulse
        migrations.AddIndex(
            model_name='digestivepulse',
            index=models.Index(fields=['-recorded_at'], name='core_digest_recorde_idx'),
        ),
        migrations.AddIndex(
            model_name='digestivepulse',
            index=models.Index(fields=['overall_status', '-recorded_at'], name='core_digest_status_idx'),
        ),

        # Create DigestionStatus table (per-route status)
        migrations.CreateModel(
            name='DigestionStatus',
            fields=[
                ('route', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='status', serialize=False, to='core.ingestionroute')),
                ('status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('sluggish', 'Sluggish'),
                    ('bloated', 'Bloated'),
                    ('blocked', 'Blocked'),
                    ('starving', 'Starving'),
                ], default='healthy', max_length=20)),
                ('is_healthy', models.BooleanField(default=True)),
                # Current metrics
                ('current_queue_depth', models.IntegerField(default=0)),
                ('current_throughput', models.FloatField(default=0, help_text='Current items/minute')),
                ('current_latency_ms', models.FloatField(default=0, help_text='Current avg processing time')),
                # 24h metrics
                ('items_ingested_24h', models.IntegerField(default=0)),
                ('items_processed_24h', models.IntegerField(default=0)),
                ('items_output_24h', models.IntegerField(default=0)),
                ('errors_24h', models.IntegerField(default=0)),
                ('success_rate_24h', models.FloatField(default=100.0)),
                # Timestamps
                ('last_intake', models.DateTimeField(blank=True, null=True)),
                ('last_output', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.DateTimeField(blank=True, null=True)),
                ('last_check', models.DateTimeField(auto_now=True)),
                # Alert tracking
                ('warning_alert_sent', models.BooleanField(default=False)),
                ('critical_alert_sent', models.BooleanField(default=False)),
                ('last_alert_at', models.DateTimeField(blank=True, null=True)),
                # Notes
                ('last_error_message', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Digestion Status',
                'verbose_name_plural': 'Digestion Statuses',
                'db_table': 'core_digestion_status',
            },
        ),

        # Create default routes
        migrations.RunPython(create_default_routes, reverse_default_routes),
    ]
