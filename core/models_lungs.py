"""
Session 702: LUNGS Service Database Models

LUNGS = Limits, Usage, Notifications, Governance, Spending

The LUNGS manage the system's "breathing" - taking in resources (API credits)
and expelling them (token consumption).

Human Body Metaphor:
- Inhale = Budget allocation (credits available)
- Exhale = Token consumption (usage)
- Breath Cycle = Budget period (daily/weekly/monthly)
- Lung Capacity = Total budget limit
- Oxygen Level = Remaining budget %
- Hyperventilation = Overspending alert
- Holding Breath = Rate limit pause
- Respiratory Rate = Calls per minute
"""

import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone


class Budget(models.Model):
    """
    Budget configuration for token/cost limits.

    Supports three scopes:
    - system: System-wide budget
    - provider: Per-provider budget (e.g., OpenAI, Anthropic)
    - agent: Per-agent budget (e.g., ResearchAgent)
    """

    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    SCOPE_CHOICES = [
        ('system', 'System-wide'),
        ('provider', 'Per Provider'),
        ('agent', 'Per Agent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='system')
    scope_identifier = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Provider name or agent name for scoped budgets'
    )
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='daily')

    # Limits (null means unlimited)
    token_limit = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='Maximum tokens per period (null = unlimited)'
    )
    cost_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Maximum cost in USD per period (null = unlimited)'
    )

    # Alert thresholds (percentage of limit)
    warning_threshold = models.FloatField(
        default=0.8,
        help_text='Send warning alert at this % of limit (0.8 = 80%)'
    )
    critical_threshold = models.FloatField(
        default=0.95,
        help_text='Send critical alert at this % of limit (0.95 = 95%)'
    )

    # Status flags
    is_active = models.BooleanField(default=True)
    enforce_hard_limit = models.BooleanField(
        default=False,
        help_text='If True, block LLM calls when budget exceeded'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_budget'
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        ordering = ['scope', 'name']
        indexes = [
            models.Index(fields=['scope', 'scope_identifier']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        if self.scope_identifier:
            return f"{self.name} ({self.scope}:{self.scope_identifier})"
        return f"{self.name} ({self.scope})"

    def get_scope_key(self) -> str:
        """Get unique key for this budget's scope."""
        if self.scope_identifier:
            return f"{self.scope}:{self.scope_identifier}"
        return self.scope

    @property
    def has_token_limit(self) -> bool:
        return self.token_limit is not None

    @property
    def has_cost_limit(self) -> bool:
        return self.cost_limit is not None


class BreathCycle(models.Model):
    """
    Tracks resource consumption per budget period.

    This is a time-series model - one record per budget per period.
    Think of it as "one breath" in the respiratory cycle.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='breath_cycles'
    )

    # Period boundaries
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    # Consumption metrics
    tokens_used = models.BigIntegerField(default=0)
    cost_incurred = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    call_count = models.IntegerField(default=0)

    # Calculated remaining (updated during breathe() checks)
    tokens_remaining = models.BigIntegerField(null=True, blank=True)
    cost_remaining = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True
    )
    utilization_percent = models.FloatField(
        default=0.0,
        help_text='Budget utilization 0-100%'
    )

    # Alert tracking (to avoid duplicate alerts)
    warning_sent = models.BooleanField(default=False)
    critical_sent = models.BooleanField(default=False)

    # Forecasting
    projected_end_usage = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Projected cost at end of period based on velocity'
    )
    on_pace_to_exceed = models.BooleanField(
        default=False,
        help_text='True if projected to exceed budget'
    )

    # Timestamps
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_breath_cycle'
        verbose_name = 'Breath Cycle'
        verbose_name_plural = 'Breath Cycles'
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['budget', '-period_start']),
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['period_start', 'period_end']),
        ]
        # Ensure only one cycle per budget per period
        unique_together = [['budget', 'period_start']]

    def __str__(self):
        return f"{self.budget.name} - {self.period_start.date()}"

    def update_remaining(self):
        """Calculate remaining budget and utilization."""
        if self.budget.cost_limit:
            self.cost_remaining = self.budget.cost_limit - self.cost_incurred
            self.utilization_percent = float(self.cost_incurred / self.budget.cost_limit) * 100
        elif self.budget.token_limit:
            self.tokens_remaining = self.budget.token_limit - self.tokens_used
            self.utilization_percent = (self.tokens_used / self.budget.token_limit) * 100
        else:
            self.utilization_percent = 0.0

    def get_oxygen_level(self) -> float:
        """Get remaining budget as percentage (100 = full, 0 = empty)."""
        return max(0.0, 100.0 - self.utilization_percent)

    def is_warning(self) -> bool:
        """Check if utilization has crossed warning threshold."""
        return self.utilization_percent >= (self.budget.warning_threshold * 100)

    def is_critical(self) -> bool:
        """Check if utilization has crossed critical threshold."""
        return self.utilization_percent >= (self.budget.critical_threshold * 100)


class RespiratoryStatus(models.Model):
    """
    Current breathing status cache - one record per scope.

    This is a denormalized cache for fast lookups of current status
    without scanning the time-series BreathCycle table.
    """

    STATUS_CHOICES = [
        ('normal', 'Normal Breathing'),
        ('elevated', 'Elevated Usage'),
        ('hyperventilating', 'Over Budget'),
        ('holding', 'Rate Limited'),
    ]

    # Primary key is the scope identifier
    component = models.CharField(
        primary_key=True,
        max_length=100,
        help_text='Scope key: system, provider:openai, agent:ResearchAgent'
    )
    display_name = models.CharField(max_length=100)

    # Current status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='normal'
    )
    oxygen_level = models.FloatField(
        default=100.0,
        help_text='Remaining budget percentage (100 = full, 0 = empty)'
    )
    respiratory_rate = models.FloatField(
        default=0.0,
        help_text='LLM calls per minute (recent average)'
    )

    # Current period statistics
    tokens_used_today = models.BigIntegerField(default=0)
    cost_today = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    calls_today = models.IntegerField(default=0)

    # Limits (cached from Budget for quick access)
    daily_token_limit = models.BigIntegerField(null=True, blank=True)
    daily_cost_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Timestamps
    last_breath = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp of last LLM call'
    )
    last_check = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_respiratory_status'
        verbose_name = 'Respiratory Status'
        verbose_name_plural = 'Respiratory Statuses'

    def __str__(self):
        return f"{self.display_name}: {self.status} ({self.oxygen_level:.1f}%)"

    @classmethod
    def get_or_create_status(cls, component: str, display_name: str = None):
        """Get or create a respiratory status record."""
        status, created = cls.objects.get_or_create(
            component=component,
            defaults={
                'display_name': display_name or component.replace(':', ' - ').title()
            }
        )
        return status

    def update_status_from_oxygen(self):
        """Update status based on oxygen level."""
        if self.oxygen_level >= 80:
            self.status = 'normal'
        elif self.oxygen_level >= 50:
            self.status = 'elevated'
        elif self.oxygen_level >= 20:
            self.status = 'hyperventilating'
        else:
            self.status = 'holding'

    def mark_breath(self, tokens: int, cost: float):
        """Record a breath (LLM call)."""
        self.tokens_used_today += tokens
        self.cost_today += Decimal(str(cost))
        self.calls_today += 1
        self.last_breath = timezone.now()

        # Recalculate oxygen level if we have a limit
        if self.daily_cost_limit and self.daily_cost_limit > 0:
            used_pct = float(self.cost_today / self.daily_cost_limit) * 100
            self.oxygen_level = max(0.0, 100.0 - used_pct)
        elif self.daily_token_limit and self.daily_token_limit > 0:
            used_pct = (self.tokens_used_today / self.daily_token_limit) * 100
            self.oxygen_level = max(0.0, 100.0 - used_pct)

        self.update_status_from_oxygen()

    def reset_daily_stats(self):
        """Reset daily statistics (called at midnight)."""
        self.tokens_used_today = 0
        self.cost_today = Decimal('0.0000')
        self.calls_today = 0
        self.oxygen_level = 100.0
        self.status = 'normal'

    @classmethod
    def get_all_vitals(cls) -> dict:
        """Get all respiratory statuses as a dictionary."""
        vitals = {}
        for status in cls.objects.all():
            vitals[status.component] = {
                'display_name': status.display_name,
                'status': status.status,
                'oxygen_level': status.oxygen_level,
                'respiratory_rate': status.respiratory_rate,
                'tokens_used_today': status.tokens_used_today,
                'cost_today': float(status.cost_today),
                'calls_today': status.calls_today,
                'daily_cost_limit': float(status.daily_cost_limit) if status.daily_cost_limit else None,
                'last_breath': status.last_breath.isoformat() if status.last_breath else None,
                'last_check': status.last_check.isoformat() if status.last_check else None,
            }
        return vitals
