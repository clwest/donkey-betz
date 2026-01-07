"""
Session 707: MUSCULAR SYSTEM - Agent Work Execution

Creates tables for the MUSCULAR system which monitors agent execution
performance, tracking strength, fatigue, and strain.

Models:
- MuscleGroup: Configuration for monitored agent muscle groups
- MuscularPulse: Time-series records of muscular system state
- MuscleStatus: Current muscle status per group

Default Groups:
- 10 muscle groups covering all 72 agents by category
"""

import uuid
from django.db import migrations, models
import django.db.models.deletion


def create_default_groups(apps, schema_editor):
    """Create default muscle groups for monitoring."""
    MuscleGroup = apps.get_model('core', 'MuscleGroup')
    MuscleStatus = apps.get_model('core', 'MuscleStatus')

    default_groups = [
        {
            'name': 'creation_muscles',
            'display_name': 'Creation Muscles',
            'category': 'creation',
            'description': 'Content creation agents (image, video, audio, 3D)',
            'agent_names': ['ImageAgent', 'VideoAgent', 'AudioAgent', 'ThreeDAgent'],
            'target_success_rate': 90.0,
            'max_avg_execution_time_ms': 60000,  # Creation takes longer
            'max_daily_executions': 500,
            'is_critical': False,
            'is_builtin': True,
        },
        {
            'name': 'research_muscles',
            'display_name': 'Research Muscles',
            'category': 'research',
            'description': 'Research and analysis agents',
            'agent_names': ['ResearchAgent'],
            'target_success_rate': 95.0,
            'max_avg_execution_time_ms': 45000,
            'max_daily_executions': 1000,
            'is_critical': True,
            'is_builtin': True,
        },
        {
            'name': 'strategy_muscles',
            'display_name': 'Strategy Muscles',
            'category': 'strategy',
            'description': 'Strategy and planning agents',
            'agent_names': ['ContentStrategyAgent', 'BrandIdentityAgent', 'SEOOptimizerAgent', 'SocialMediaAgent'],
            'target_success_rate': 90.0,
            'max_avg_execution_time_ms': 30000,
            'max_daily_executions': 800,
            'is_critical': False,
            'is_builtin': True,
        },
        {
            'name': 'development_muscles',
            'display_name': 'Development Muscles',
            'category': 'development',
            'description': 'Software development agents',
            'agent_names': ['CodeGeneratorAgent', 'FullStackDeveloperAgent', 'CodeReviewAgent', 'DevOpsAgent'],
            'target_success_rate': 85.0,
            'max_avg_execution_time_ms': 90000,  # Code generation takes longer
            'max_daily_executions': 300,
            'is_critical': True,
            'is_builtin': True,
        },
        {
            'name': 'blockchain_muscles',
            'display_name': 'Blockchain Muscles',
            'category': 'blockchain',
            'description': 'Blockchain analysis and audit agents',
            'agent_names': ['BlockchainAuditCoordinator', 'SmartContractAuditorAgent', 'TransactionMonitorAgent', 'WhaleWatcherAgent', 'ExploitDetectorAgent'],
            'target_success_rate': 95.0,
            'max_avg_execution_time_ms': 45000,
            'max_daily_executions': 600,
            'is_critical': False,
            'is_builtin': True,
        },
        {
            'name': 'stocks_muscles',
            'display_name': 'Stock Analysis Muscles',
            'category': 'stocks',
            'description': 'Stock market analysis agents',
            'agent_names': ['StockAuditCoordinator', 'StockAnalystAgent', 'MarketMovementMonitorAgent', 'BullCaseAgent', 'BearCaseAgent', 'SignalScannerAgent', 'MarketAnomalyDetectorAgent'],
            'target_success_rate': 90.0,
            'max_avg_execution_time_ms': 30000,
            'max_daily_executions': 1000,
            'is_critical': True,
            'is_builtin': True,
        },
        {
            'name': 'executive_muscles',
            'display_name': 'Executive Muscles',
            'category': 'executive',
            'description': 'Executive and coordination agents',
            'agent_names': ['CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'MeetingCoordinatorAgent'],
            'target_success_rate': 95.0,
            'max_avg_execution_time_ms': 20000,
            'max_daily_executions': 200,
            'is_critical': False,
            'is_builtin': True,
        },
        {
            'name': 'narrative_muscles',
            'display_name': 'Narrative Muscles',
            'category': 'narrative',
            'description': 'Narrative and cultural analysis agents',
            'agent_names': ['NarrativeDriftCoordinator', 'NarrativeHistorianAgent', 'TrendBreakDetectorAgent', 'CulturalImpactAgent'],
            'target_success_rate': 90.0,
            'max_avg_execution_time_ms': 40000,
            'max_daily_executions': 400,
            'is_critical': False,
            'is_builtin': True,
        },
        {
            'name': 'orchestration_muscles',
            'display_name': 'Orchestration Muscles',
            'category': 'orchestration',
            'description': 'Workflow orchestration agents',
            'agent_names': ['WorkflowAgent', 'WorkflowOrchestrationAgent', 'OpportunityPipelineAgent', 'ContentExecutorAgent'],
            'target_success_rate': 95.0,
            'max_avg_execution_time_ms': 25000,
            'max_daily_executions': 500,
            'is_critical': True,
            'is_builtin': True,
        },
        {
            'name': 'markets_muscles',
            'display_name': 'Market Muscles',
            'category': 'markets',
            'description': 'Prediction market and odds agents',
            'agent_names': ['PredictionMarketAnalyst', 'SportsOddsAnalyst', 'ArbitrageDetector'],
            'target_success_rate': 90.0,
            'max_avg_execution_time_ms': 30000,
            'max_daily_executions': 600,
            'is_critical': False,
            'is_builtin': True,
        },
    ]

    for group_data in default_groups:
        group = MuscleGroup.objects.create(**group_data)
        # Create corresponding status record
        MuscleStatus.objects.create(
            group=group,
            status='fit',
            is_healthy=True,
            total_agents=len(group_data['agent_names']),
        )


def reverse_default_groups(apps, schema_editor):
    """Remove default muscle groups."""
    MuscleGroup = apps.get_model('core', 'MuscleGroup')
    MuscleGroup.objects.filter(is_builtin=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0152_session_706_digestive_system'),
    ]

    operations = [
        # Create MuscleGroup table
        migrations.CreateModel(
            name='MuscleGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(blank=True, max_length=150)),
                ('category', models.CharField(choices=[
                    ('creation', 'Creation Agents'),
                    ('research', 'Research Agents'),
                    ('strategy', 'Strategy Agents'),
                    ('development', 'Development Agents'),
                    ('blockchain', 'Blockchain Agents'),
                    ('stocks', 'Stock Analysis Agents'),
                    ('executive', 'Executive Agents'),
                    ('narrative', 'Narrative Agents'),
                    ('orchestration', 'Orchestration Agents'),
                    ('markets', 'Market Agents'),
                ], max_length=30)),
                ('description', models.TextField(blank=True)),
                ('agent_names', models.JSONField(default=list, help_text='List of agent names in this group')),
                ('target_success_rate', models.FloatField(default=90.0, help_text='Target success rate %')),
                ('max_avg_execution_time_ms', models.IntegerField(default=30000, help_text='Max avg execution time')),
                ('max_fatigue_level', models.FloatField(default=80.0, help_text='Max fatigue before warning %')),
                ('max_daily_executions', models.IntegerField(default=1000, help_text='Max daily executions before overwork')),
                ('is_active', models.BooleanField(default=True)),
                ('is_critical', models.BooleanField(default=False, help_text='Alert on failure')),
                ('is_builtin', models.BooleanField(default=False, help_text='System-defined group')),
                ('total_executions', models.BigIntegerField(default=0)),
                ('total_successful', models.BigIntegerField(default=0)),
                ('total_failed', models.BigIntegerField(default=0)),
                ('last_execution', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Muscle Group',
                'verbose_name_plural': 'Muscle Groups',
                'db_table': 'core_muscle_group',
                'ordering': ['category', 'name'],
            },
        ),

        # Create MuscularPulse table (time-series)
        migrations.CreateModel(
            name='MuscularPulse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('overall_status', models.CharField(choices=[
                    ('strong', 'Strong'),
                    ('fit', 'Fit'),
                    ('fatigued', 'Fatigued'),
                    ('strained', 'Strained'),
                    ('paralyzed', 'Paralyzed'),
                ], default='fit', max_length=20)),
                ('strength_score', models.FloatField(default=100.0, help_text='0-100% strength')),
                ('is_strong', models.BooleanField(default=True)),
                # Execution metrics (24h)
                ('total_executions_24h', models.IntegerField(default=0)),
                ('successful_executions_24h', models.IntegerField(default=0)),
                ('failed_executions_24h', models.IntegerField(default=0)),
                ('success_rate_24h', models.FloatField(default=100.0)),
                # Performance metrics
                ('avg_execution_time_ms', models.FloatField(default=0)),
                ('min_execution_time_ms', models.FloatField(default=0)),
                ('max_execution_time_ms', models.FloatField(default=0)),
                ('total_tokens_used_24h', models.BigIntegerField(default=0)),
                ('total_cost_24h', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                # Load metrics
                ('total_agents', models.IntegerField(default=0)),
                ('active_agents', models.IntegerField(default=0, help_text='Agents with executions in 24h')),
                ('idle_agents', models.IntegerField(default=0, help_text='Agents with no recent activity')),
                ('fatigued_agents', models.IntegerField(default=0, help_text='Agents with high load')),
                ('strained_agents', models.IntegerField(default=0, help_text='Agents with high error rate')),
                # Group breakdown
                ('group_metrics', models.JSONField(default=dict)),
                # Issues detected
                ('weak_muscles', models.JSONField(default=list, help_text='Agents with low success rate')),
                ('overworked_muscles', models.JSONField(default=list, help_text='Agents with high execution count')),
                # Groups info
                ('groups_checked', models.IntegerField(default=0)),
                ('groups_strong', models.IntegerField(default=0)),
                ('groups_fit', models.IntegerField(default=0)),
                ('groups_fatigued', models.IntegerField(default=0)),
                ('groups_strained', models.IntegerField(default=0)),
                ('groups_paralyzed', models.IntegerField(default=0)),
                # Integration status
                ('heart_connected', models.BooleanField(default=False)),
                ('digestive_connected', models.BooleanField(default=False)),
                # Metadata
                ('check_duration_ms', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Muscular Pulse',
                'verbose_name_plural': 'Muscular Pulses',
                'db_table': 'core_muscular_pulse',
                'ordering': ['-recorded_at'],
            },
        ),

        # Add indexes to MuscularPulse
        migrations.AddIndex(
            model_name='muscularpulse',
            index=models.Index(fields=['-recorded_at'], name='core_muscul_recorde_idx'),
        ),
        migrations.AddIndex(
            model_name='muscularpulse',
            index=models.Index(fields=['overall_status', '-recorded_at'], name='core_muscul_status_idx'),
        ),

        # Create MuscleStatus table (per-group status)
        migrations.CreateModel(
            name='MuscleStatus',
            fields=[
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='status', serialize=False, to='core.musclegroup')),
                ('status', models.CharField(choices=[
                    ('strong', 'Strong'),
                    ('fit', 'Fit'),
                    ('fatigued', 'Fatigued'),
                    ('strained', 'Strained'),
                    ('paralyzed', 'Paralyzed'),
                ], default='fit', max_length=20)),
                ('is_healthy', models.BooleanField(default=True)),
                # Current metrics
                ('strength_score', models.FloatField(default=100.0, help_text='0-100 strength')),
                ('fatigue_level', models.FloatField(default=0, help_text='0-100 (higher = more tired)')),
                ('strain_level', models.FloatField(default=0, help_text='0-100 (higher = more errors)')),
                # 24h metrics
                ('executions_24h', models.IntegerField(default=0)),
                ('successful_24h', models.IntegerField(default=0)),
                ('failed_24h', models.IntegerField(default=0)),
                ('success_rate_24h', models.FloatField(default=100.0)),
                ('avg_execution_time_ms', models.FloatField(default=0)),
                ('tokens_used_24h', models.BigIntegerField(default=0)),
                ('cost_24h', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                # Agent counts
                ('total_agents', models.IntegerField(default=0)),
                ('active_agents', models.IntegerField(default=0)),
                ('idle_agents', models.IntegerField(default=0)),
                # Top performers
                ('top_performer', models.CharField(blank=True, help_text='Best performing agent', max_length=100)),
                ('worst_performer', models.CharField(blank=True, help_text='Worst performing agent', max_length=100)),
                # Timestamps
                ('last_execution', models.DateTimeField(blank=True, null=True)),
                ('last_success', models.DateTimeField(blank=True, null=True)),
                ('last_failure', models.DateTimeField(blank=True, null=True)),
                ('last_check', models.DateTimeField(auto_now=True)),
                # Alert tracking
                ('warning_alert_sent', models.BooleanField(default=False)),
                ('critical_alert_sent', models.BooleanField(default=False)),
                ('last_alert_at', models.DateTimeField(blank=True, null=True)),
                # Notes
                ('last_issue', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Muscle Status',
                'verbose_name_plural': 'Muscle Statuses',
                'db_table': 'core_muscle_status',
            },
        ),

        # Create default muscle groups
        migrations.RunPython(create_default_groups, reverse_default_groups),
    ]
