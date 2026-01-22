"""
Session 702: LUNGS Service Migration

Creates the database tables for the LUNGS (Limits, Usage, Notifications, Governance, Spending)
service - the resource and capacity management system of the AI body.

Models:
- Budget: Budget configuration with limits and thresholds
- BreathCycle: Time-series consumption tracking per period
- RespiratoryStatus: Current breathing status cache

Also creates default budgets for system, OpenAI, and Anthropic.
"""

from decimal import Decimal
from django.db import migrations, models
import uuid


def create_default_budgets(apps, schema_editor):
    """Create default budget configurations."""
    Budget = apps.get_model('core', 'Budget')

    default_budgets = [
        {
            'name': 'System Daily Budget',
            'scope': 'system',
            'scope_identifier': '',
            'period': 'daily',
            'cost_limit': Decimal('50.00'),
            'token_limit': None,
            'warning_threshold': 0.8,
            'critical_threshold': 0.95,
            'is_active': True,
            'enforce_hard_limit': False,
        },
        {
            'name': 'System Monthly Budget',
            'scope': 'system',
            'scope_identifier': '',
            'period': 'monthly',
            'cost_limit': Decimal('500.00'),
            'token_limit': None,
            'warning_threshold': 0.7,
            'critical_threshold': 0.90,
            'is_active': True,
            'enforce_hard_limit': False,
        },
        {
            'name': 'OpenAI Daily Budget',
            'scope': 'provider',
            'scope_identifier': 'openai',
            'period': 'daily',
            'cost_limit': Decimal('30.00'),
            'token_limit': None,
            'warning_threshold': 0.8,
            'critical_threshold': 0.95,
            'is_active': True,
            'enforce_hard_limit': False,
        },
        {
            'name': 'Anthropic Daily Budget',
            'scope': 'provider',
            'scope_identifier': 'anthropic',
            'period': 'daily',
            'cost_limit': Decimal('20.00'),
            'token_limit': None,
            'warning_threshold': 0.8,
            'critical_threshold': 0.95,
            'is_active': True,
            'enforce_hard_limit': False,
        },
        {
            'name': 'Together AI Daily Budget',
            'scope': 'provider',
            'scope_identifier': 'together_ai',
            'period': 'daily',
            'cost_limit': Decimal('10.00'),
            'token_limit': None,
            'warning_threshold': 0.8,
            'critical_threshold': 0.95,
            'is_active': True,
            'enforce_hard_limit': False,
        },
        {
            'name': 'DeepSeek Daily Budget',
            'scope': 'provider',
            'scope_identifier': 'deepseek',
            'period': 'daily',
            'cost_limit': Decimal('5.00'),
            'token_limit': None,
            'warning_threshold': 0.8,
            'critical_threshold': 0.95,
            'is_active': True,
            'enforce_hard_limit': False,
        },
    ]

    for budget_data in default_budgets:
        Budget.objects.create(id=uuid.uuid4(), **budget_data)


def create_default_respiratory_statuses(apps, schema_editor):
    """Create default respiratory status entries."""
    RespiratoryStatus = apps.get_model('core', 'RespiratoryStatus')

    default_statuses = [
        {
            'component': 'system',
            'display_name': 'System Overall',
            'status': 'normal',
            'oxygen_level': 100.0,
            'daily_cost_limit': Decimal('50.00'),
        },
        {
            'component': 'provider:openai',
            'display_name': 'OpenAI',
            'status': 'normal',
            'oxygen_level': 100.0,
            'daily_cost_limit': Decimal('30.00'),
        },
        {
            'component': 'provider:anthropic',
            'display_name': 'Anthropic',
            'status': 'normal',
            'oxygen_level': 100.0,
            'daily_cost_limit': Decimal('20.00'),
        },
        {
            'component': 'provider:together_ai',
            'display_name': 'Together AI',
            'status': 'normal',
            'oxygen_level': 100.0,
            'daily_cost_limit': Decimal('10.00'),
        },
        {
            'component': 'provider:deepseek',
            'display_name': 'DeepSeek',
            'status': 'normal',
            'oxygen_level': 100.0,
            'daily_cost_limit': Decimal('5.00'),
        },
        {
            'component': 'provider:gemini',
            'display_name': 'Gemini',
            'status': 'normal',
            'oxygen_level': 100.0,
            'daily_cost_limit': None,  # No limit set
        },
        {
            'component': 'provider:ollama',
            'display_name': 'Ollama (Local)',
            'status': 'normal',
            'oxygen_level': 100.0,
            'daily_cost_limit': None,  # Free (local)
        },
    ]

    for status_data in default_statuses:
        RespiratoryStatus.objects.create(**status_data)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0147_session_701_heart_service'),
    ]

    operations = [
        # Budget model - budget configuration
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                )),
                ('name', models.CharField(max_length=100)),
                ('scope', models.CharField(
                    choices=[
                        ('system', 'System-wide'),
                        ('provider', 'Per Provider'),
                        ('agent', 'Per Agent'),
                    ],
                    default='system',
                    max_length=20,
                )),
                ('scope_identifier', models.CharField(
                    blank=True,
                    default='',
                    max_length=100,
                    help_text='Provider name or agent name for scoped budgets',
                )),
                ('period', models.CharField(
                    choices=[
                        ('daily', 'Daily'),
                        ('weekly', 'Weekly'),
                        ('monthly', 'Monthly'),
                    ],
                    default='daily',
                    max_length=20,
                )),
                ('token_limit', models.BigIntegerField(
                    blank=True,
                    null=True,
                    help_text='Maximum tokens per period (null = unlimited)',
                )),
                ('cost_limit', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    max_digits=10,
                    null=True,
                    help_text='Maximum cost in USD per period (null = unlimited)',
                )),
                ('warning_threshold', models.FloatField(
                    default=0.8,
                    help_text='Send warning alert at this % of limit (0.8 = 80%)',
                )),
                ('critical_threshold', models.FloatField(
                    default=0.95,
                    help_text='Send critical alert at this % of limit (0.95 = 95%)',
                )),
                ('is_active', models.BooleanField(default=True)),
                ('enforce_hard_limit', models.BooleanField(
                    default=False,
                    help_text='If True, block LLM calls when budget exceeded',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'core_budget',
                'verbose_name': 'Budget',
                'verbose_name_plural': 'Budgets',
                'ordering': ['scope', 'name'],
            },
        ),

        # BreathCycle model - time-series consumption tracking
        migrations.CreateModel(
            name='BreathCycle',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                )),
                ('budget', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='breath_cycles',
                    to='core.budget',
                )),
                ('period_start', models.DateTimeField()),
                ('period_end', models.DateTimeField()),
                ('tokens_used', models.BigIntegerField(default=0)),
                ('cost_incurred', models.DecimalField(
                    decimal_places=4,
                    default=0,
                    max_digits=10,
                )),
                ('call_count', models.IntegerField(default=0)),
                ('tokens_remaining', models.BigIntegerField(blank=True, null=True)),
                ('cost_remaining', models.DecimalField(
                    blank=True,
                    decimal_places=4,
                    max_digits=10,
                    null=True,
                )),
                ('utilization_percent', models.FloatField(
                    default=0.0,
                    help_text='Budget utilization 0-100%',
                )),
                ('warning_sent', models.BooleanField(default=False)),
                ('critical_sent', models.BooleanField(default=False)),
                ('projected_end_usage', models.DecimalField(
                    blank=True,
                    decimal_places=4,
                    max_digits=10,
                    null=True,
                    help_text='Projected cost at end of period based on velocity',
                )),
                ('on_pace_to_exceed', models.BooleanField(
                    default=False,
                    help_text='True if projected to exceed budget',
                )),
                ('recorded_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'core_breath_cycle',
                'verbose_name': 'Breath Cycle',
                'verbose_name_plural': 'Breath Cycles',
                'ordering': ['-period_start'],
                'unique_together': {('budget', 'period_start')},
            },
        ),

        # RespiratoryStatus model - current breathing status cache
        migrations.CreateModel(
            name='RespiratoryStatus',
            fields=[
                ('component', models.CharField(
                    help_text='Scope key: system, provider:openai, agent:ResearchAgent',
                    max_length=100,
                    primary_key=True,
                    serialize=False,
                )),
                ('display_name', models.CharField(max_length=100)),
                ('status', models.CharField(
                    choices=[
                        ('normal', 'Normal Breathing'),
                        ('elevated', 'Elevated Usage'),
                        ('hyperventilating', 'Over Budget'),
                        ('holding', 'Rate Limited'),
                    ],
                    default='normal',
                    max_length=20,
                )),
                ('oxygen_level', models.FloatField(
                    default=100.0,
                    help_text='Remaining budget percentage (100 = full, 0 = empty)',
                )),
                ('respiratory_rate', models.FloatField(
                    default=0.0,
                    help_text='LLM calls per minute (recent average)',
                )),
                ('tokens_used_today', models.BigIntegerField(default=0)),
                ('cost_today', models.DecimalField(
                    decimal_places=4,
                    default=0,
                    max_digits=10,
                )),
                ('calls_today', models.IntegerField(default=0)),
                ('daily_token_limit', models.BigIntegerField(blank=True, null=True)),
                ('daily_cost_limit', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    max_digits=10,
                    null=True,
                )),
                ('last_breath', models.DateTimeField(
                    blank=True,
                    null=True,
                    help_text='Timestamp of last LLM call',
                )),
                ('last_check', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'core_respiratory_status',
                'verbose_name': 'Respiratory Status',
                'verbose_name_plural': 'Respiratory Statuses',
            },
        ),

        # Add indexes
        migrations.AddIndex(
            model_name='budget',
            index=models.Index(fields=['scope', 'scope_identifier'], name='core_budget_scope_idx'),
        ),
        migrations.AddIndex(
            model_name='budget',
            index=models.Index(fields=['is_active'], name='core_budget_active_idx'),
        ),
        migrations.AddIndex(
            model_name='breathcycle',
            index=models.Index(fields=['budget', '-period_start'], name='core_breath_budget_period_idx'),
        ),
        migrations.AddIndex(
            model_name='breathcycle',
            index=models.Index(fields=['-recorded_at'], name='core_breath_recorded_idx'),
        ),
        migrations.AddIndex(
            model_name='breathcycle',
            index=models.Index(fields=['period_start', 'period_end'], name='core_breath_period_idx'),
        ),

        # Create default data
        migrations.RunPython(create_default_budgets, migrations.RunPython.noop),
        migrations.RunPython(create_default_respiratory_statuses, migrations.RunPython.noop),
    ]
