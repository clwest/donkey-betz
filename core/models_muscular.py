"""
Session 707: MUSCULAR SYSTEM - Agent Work Execution Models

The MUSCULAR SYSTEM is the work execution layer of the AI body - monitoring
how agents perform their tasks and tracking strength, fatigue, and strain.

Models:
- MuscleGroup: Configuration for monitored agent muscle groups
- MuscularPulse: Time-series records of muscular system state
- MuscleStatus: Current muscle status per group (cached state)

Human Body Metaphor:
- Muscles = Agent categories (Creation, Research, Strategy, etc.)
- Muscle Fibers = Individual agents within category
- Flexing = Agent task execution
- Strength = Execution success rate & performance
- Fatigue = High execution load, slow response times
- Strain = Error rate, failed executions
- Recovery = Time since last execution
- Muscle Memory = Agent learning from past executions
"""

import uuid
from django.db import models
from django.utils import timezone


class MuscleGroup(models.Model):
    """Configuration for a monitored agent muscle group."""

    CATEGORY_CHOICES = [
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
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Agent filter - which agents belong to this muscle group
    agent_names = models.JSONField(default=list, help_text="List of agent names in this group")

    # Thresholds
    target_success_rate = models.FloatField(default=90.0, help_text="Target success rate %")
    max_avg_execution_time_ms = models.IntegerField(default=30000, help_text="Max avg execution time")
    max_fatigue_level = models.FloatField(default=80.0, help_text="Max fatigue before warning %")
    max_daily_executions = models.IntegerField(default=1000, help_text="Max daily executions before overwork")

    # Status
    is_active = models.BooleanField(default=True)
    is_critical = models.BooleanField(default=False, help_text="Alert on failure")
    is_builtin = models.BooleanField(default=False, help_text="System-defined group")

    # Statistics
    total_executions = models.BigIntegerField(default=0)
    total_successful = models.BigIntegerField(default=0)
    total_failed = models.BigIntegerField(default=0)
    last_execution = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_muscle_group'
        ordering = ['category', 'name']
        verbose_name = 'Muscle Group'
        verbose_name_plural = 'Muscle Groups'

    def __str__(self):
        return f"{self.display_name or self.name} ({self.category})"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.replace('_', ' ').title()
        super().save(*args, **kwargs)

    @property
    def agent_count(self) -> int:
        """Get count of agents in this muscle group."""
        return len(self.agent_names) if self.agent_names else 0


class MuscularPulse(models.Model):
    """Time-series record of muscular system state - periodic snapshots."""

    STATUS_CHOICES = [
        ('strong', 'Strong'),        # High success rate, normal load
        ('fit', 'Fit'),              # Good performance, manageable load
        ('fatigued', 'Fatigued'),    # High load, slower responses
        ('strained', 'Strained'),    # High error rate, needs attention
        ('paralyzed', 'Paralyzed'),  # No activity or all failing
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Overall metrics
    overall_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='fit')
    strength_score = models.FloatField(default=100.0, help_text="0-100% strength")
    is_strong = models.BooleanField(default=True)

    # Execution metrics (24h)
    total_executions_24h = models.IntegerField(default=0)
    successful_executions_24h = models.IntegerField(default=0)
    failed_executions_24h = models.IntegerField(default=0)
    success_rate_24h = models.FloatField(default=100.0)

    # Performance metrics
    avg_execution_time_ms = models.FloatField(default=0)
    min_execution_time_ms = models.FloatField(default=0)
    max_execution_time_ms = models.FloatField(default=0)
    total_tokens_used_24h = models.BigIntegerField(default=0)
    total_cost_24h = models.DecimalField(max_digits=12, decimal_places=4, default=0)

    # Load metrics
    total_agents = models.IntegerField(default=0)
    active_agents = models.IntegerField(default=0, help_text="Agents with executions in 24h")
    idle_agents = models.IntegerField(default=0, help_text="Agents with no recent activity")
    fatigued_agents = models.IntegerField(default=0, help_text="Agents with high load")
    strained_agents = models.IntegerField(default=0, help_text="Agents with high error rate")

    # Group breakdown (per-category metrics)
    group_metrics = models.JSONField(default=dict)

    # Issues detected
    weak_muscles = models.JSONField(default=list, help_text="Agents with low success rate")
    overworked_muscles = models.JSONField(default=list, help_text="Agents with high execution count")

    # Groups checked
    groups_checked = models.IntegerField(default=0)
    groups_strong = models.IntegerField(default=0)
    groups_fit = models.IntegerField(default=0)
    groups_fatigued = models.IntegerField(default=0)
    groups_strained = models.IntegerField(default=0)
    groups_paralyzed = models.IntegerField(default=0)

    # Integration status
    heart_connected = models.BooleanField(default=False)
    digestive_connected = models.BooleanField(default=False)

    # Check metadata
    check_duration_ms = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_muscular_pulse'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['overall_status', '-recorded_at']),
        ]
        verbose_name = 'Muscular Pulse'
        verbose_name_plural = 'Muscular Pulses'

    def __str__(self):
        return f"Muscular: {self.overall_status} ({self.strength_score:.1f}%) @ {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    def get_status_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'strong': '💪',      # Flexed bicep - strong
            'fit': '🏃',         # Runner - fit
            'fatigued': '😓',    # Sweating - tired
            'strained': '🥵',    # Hot face - stressed
            'paralyzed': '🦽',   # Wheelchair - immobile
        }.get(self.overall_status, '❓')


class MuscleStatus(models.Model):
    """Current muscle status per group - cached state updated on each check."""

    STATUS_CHOICES = [
        ('strong', 'Strong'),        # High success, normal load
        ('fit', 'Fit'),              # Good performance
        ('fatigued', 'Fatigued'),    # High load, slower response
        ('strained', 'Strained'),    # High error rate
        ('paralyzed', 'Paralyzed'),  # No activity or all failing
    ]

    group = models.OneToOneField(
        MuscleGroup,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='status'
    )

    # Current status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='fit')
    is_healthy = models.BooleanField(default=True)

    # Current metrics
    strength_score = models.FloatField(default=100.0, help_text="0-100 strength")
    fatigue_level = models.FloatField(default=0, help_text="0-100 (higher = more tired)")
    strain_level = models.FloatField(default=0, help_text="0-100 (higher = more errors)")

    # 24h rolling metrics
    executions_24h = models.IntegerField(default=0)
    successful_24h = models.IntegerField(default=0)
    failed_24h = models.IntegerField(default=0)
    success_rate_24h = models.FloatField(default=100.0)
    avg_execution_time_ms = models.FloatField(default=0)
    tokens_used_24h = models.BigIntegerField(default=0)
    cost_24h = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Agent counts
    total_agents = models.IntegerField(default=0)
    active_agents = models.IntegerField(default=0)
    idle_agents = models.IntegerField(default=0)

    # Top performers/underperformers
    top_performer = models.CharField(max_length=100, blank=True, help_text="Best performing agent")
    worst_performer = models.CharField(max_length=100, blank=True, help_text="Worst performing agent")

    # Timestamps
    last_execution = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_failure = models.DateTimeField(null=True, blank=True)
    last_check = models.DateTimeField(auto_now=True)

    # Alert tracking
    warning_alert_sent = models.BooleanField(default=False)
    critical_alert_sent = models.BooleanField(default=False)
    last_alert_at = models.DateTimeField(null=True, blank=True)

    # Notes
    last_issue = models.TextField(blank=True)

    class Meta:
        db_table = 'core_muscle_status'
        verbose_name = 'Muscle Status'
        verbose_name_plural = 'Muscle Statuses'

    def __str__(self):
        return f"{self.group.name}: {self.status} (strength: {self.strength_score:.1f}%)"

    def update_status(self, new_status: str, is_healthy: bool):
        """Update status and reset alerts if recovering."""
        if self.status != new_status:
            # Reset alerts when recovering to healthy states
            if new_status in ('strong', 'fit'):
                self.warning_alert_sent = False
                self.critical_alert_sent = False

        self.status = new_status
        self.is_healthy = is_healthy

    def get_status_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'strong': '💪',
            'fit': '🏃',
            'fatigued': '😓',
            'strained': '🥵',
            'paralyzed': '🦽',
        }.get(self.status, '❓')
