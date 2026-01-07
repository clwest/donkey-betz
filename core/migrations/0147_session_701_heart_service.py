"""
Session 701: HEART Service Migration

Creates the database tables for the HEART (Health, Events, Activity, Real-time Telemetry)
service - the central heartbeat monitoring system of the AI body.

Models:
- HeartBeat: Time-series health check records
- ComponentStatus: Current status cache for each component
"""

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0146_session_697_llm_routing'),
    ]

    operations = [
        # HeartBeat model - time-series health records
        migrations.CreateModel(
            name='HeartBeat',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                    help_text='Unique identifier for this heartbeat'
                )),
                ('health_score', models.FloatField(
                    help_text='Overall health score (0-100%)'
                )),
                ('overall_status', models.CharField(
                    choices=[
                        ('healthy', 'Healthy'),
                        ('degraded', 'Degraded'),
                        ('critical', 'Critical'),
                        ('offline', 'Offline')
                    ],
                    default='healthy',
                    db_index=True,
                    max_length=20,
                    help_text='Overall system status'
                )),
                ('is_alive', models.BooleanField(
                    default=True,
                    help_text='Quick flag: is system operational?'
                )),
                ('components', models.JSONField(
                    default=dict,
                    help_text='Detailed status of each component'
                )),
                ('check_duration_ms', models.IntegerField(
                    help_text='How long the health check took (milliseconds)'
                )),
                ('components_checked', models.IntegerField(
                    help_text='Number of components checked'
                )),
                ('components_healthy', models.IntegerField(
                    help_text='Number of components in healthy state'
                )),
                ('alerts_sent', models.BooleanField(
                    default=False,
                    help_text='Whether Discord alerts were sent for this heartbeat'
                )),
                ('recorded_at', models.DateTimeField(
                    db_index=True,
                    help_text='When this heartbeat was recorded'
                )),
            ],
            options={
                'verbose_name': 'Heart Beat',
                'verbose_name_plural': 'Heart Beats',
                'db_table': 'core_heartbeat',
                'ordering': ['-recorded_at'],
            },
        ),

        # ComponentStatus model - current state cache
        migrations.CreateModel(
            name='ComponentStatus',
            fields=[
                ('component', models.CharField(
                    max_length=50,
                    primary_key=True,
                    serialize=False,
                    help_text='Component identifier (brain, organs, sensory, etc.)'
                )),
                ('display_name', models.CharField(
                    max_length=100,
                    help_text='Human-readable component name'
                )),
                ('description', models.TextField(
                    blank=True,
                    help_text='What this component represents in the AI body'
                )),
                ('status', models.CharField(
                    choices=[
                        ('healthy', 'Healthy'),
                        ('degraded', 'Degraded'),
                        ('critical', 'Critical'),
                        ('offline', 'Offline')
                    ],
                    default='healthy',
                    db_index=True,
                    max_length=20,
                    help_text='Current health status'
                )),
                ('is_healthy', models.BooleanField(
                    db_index=True,
                    default=True,
                    help_text='Quick flag: is component healthy?'
                )),
                ('last_check', models.DateTimeField(
                    help_text='When this component was last checked'
                )),
                ('last_healthy', models.DateTimeField(
                    blank=True,
                    null=True,
                    help_text='When this component was last in healthy state'
                )),
                ('response_time_ms', models.IntegerField(
                    blank=True,
                    null=True,
                    help_text='Response time of last health check (milliseconds)'
                )),
                ('error_count_24h', models.IntegerField(
                    default=0,
                    help_text='Number of errors in last 24 hours'
                )),
                ('check_count_24h', models.IntegerField(
                    default=0,
                    help_text='Number of checks in last 24 hours'
                )),
                ('uptime_percent_24h', models.FloatField(
                    default=100.0,
                    help_text='Percentage of time healthy in last 24 hours'
                )),
                ('details', models.JSONField(
                    default=dict,
                    help_text='Additional component-specific details'
                )),
                ('last_error', models.TextField(
                    blank=True,
                    default='',
                    help_text='Last error message if status is not healthy'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Component Status',
                'verbose_name_plural': 'Component Statuses',
                'db_table': 'core_component_status',
                'ordering': ['component'],
            },
        ),

        # Indexes for HeartBeat
        migrations.AddIndex(
            model_name='heartbeat',
            index=models.Index(
                fields=['-recorded_at'],
                name='core_heartb_recorde_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='heartbeat',
            index=models.Index(
                fields=['overall_status', '-recorded_at'],
                name='core_heartb_status_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='heartbeat',
            index=models.Index(
                fields=['is_alive', '-recorded_at'],
                name='core_heartb_alive_idx'
            ),
        ),
    ]
