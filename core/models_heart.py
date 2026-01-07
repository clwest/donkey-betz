"""
Session 701: HEART Service Database Models

The HEART (Health, Events, Activity, Real-time Telemetry) service models
for tracking system health - the central heartbeat of the AI body.

Human Body Metaphor:
- HeartBeat: Individual pulse records (time-series health data)
- ComponentStatus: Current state of each body component (cached vitals)
"""

import uuid
from django.db import models
from django.utils import timezone


class StatusChoices(models.TextChoices):
    """Health status levels for components."""
    HEALTHY = 'healthy', 'Healthy'      # 80-100% - All systems operational
    DEGRADED = 'degraded', 'Degraded'   # 50-79% - Some components have issues
    CRITICAL = 'critical', 'Critical'   # 0-49% - Major systems failing
    OFFLINE = 'offline', 'Offline'      # Component unreachable


class HeartBeat(models.Model):
    """
    Individual heartbeat record - time-series health data.

    Each record represents a single pulse check of all system components.
    Used for historical analysis and trend monitoring.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this heartbeat"
    )

    # Overall health metrics
    health_score = models.FloatField(
        help_text="Overall health score (0-100%)"
    )
    overall_status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.HEALTHY,
        db_index=True,
        help_text="Overall system status"
    )
    is_alive = models.BooleanField(
        default=True,
        help_text="Quick flag: is system operational?"
    )

    # Component statuses (JSON for flexibility)
    components = models.JSONField(
        default=dict,
        help_text="Detailed status of each component {brain: {...}, organs: {...}, ...}"
    )

    # Metrics
    check_duration_ms = models.IntegerField(
        help_text="How long the health check took (milliseconds)"
    )
    components_checked = models.IntegerField(
        help_text="Number of components checked"
    )
    components_healthy = models.IntegerField(
        help_text="Number of components in healthy state"
    )

    # Alerts
    alerts_sent = models.BooleanField(
        default=False,
        help_text="Whether Discord alerts were sent for this heartbeat"
    )

    # Timestamps
    recorded_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When this heartbeat was recorded"
    )

    class Meta:
        db_table = 'core_heartbeat'
        verbose_name = 'Heart Beat'
        verbose_name_plural = 'Heart Beats'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['overall_status', '-recorded_at']),
            models.Index(fields=['is_alive', '-recorded_at']),
        ]

    def __str__(self):
        return f"HeartBeat {self.recorded_at.strftime('%Y-%m-%d %H:%M:%S')} - {self.overall_status} ({self.health_score:.1f}%)"

    @property
    def components_degraded(self) -> int:
        """Count of components not in healthy state."""
        return self.components_checked - self.components_healthy


class ComponentStatus(models.Model):
    """
    Current status of each body component (latest state cache).

    This is a denormalized cache of the most recent status for each component,
    allowing fast lookups without scanning the HeartBeat time-series.

    Components (Human Body Metaphor):
    - brain: ThinkingAgent (reasoning)
    - nervous_system: LLM/ML Routers (signal routing)
    - organs: 72 Specialized Agents (work execution)
    - sensory: 77 Spiders (data gathering)
    - skin: Workspace Manager (touching reality)
    - memory: Database & Redis (persistence)
    """
    component = models.CharField(
        primary_key=True,
        max_length=50,
        help_text="Component identifier (brain, organs, sensory, etc.)"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Human-readable component name"
    )
    description = models.TextField(
        blank=True,
        help_text="What this component represents in the AI body"
    )

    # Current status
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.HEALTHY,
        db_index=True,
        help_text="Current health status"
    )
    is_healthy = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Quick flag: is component healthy?"
    )

    # Timestamps
    last_check = models.DateTimeField(
        help_text="When this component was last checked"
    )
    last_healthy = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this component was last in healthy state"
    )

    # Performance metrics
    response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Response time of last health check (milliseconds)"
    )

    # 24-hour metrics
    error_count_24h = models.IntegerField(
        default=0,
        help_text="Number of errors in last 24 hours"
    )
    check_count_24h = models.IntegerField(
        default=0,
        help_text="Number of checks in last 24 hours"
    )
    uptime_percent_24h = models.FloatField(
        default=100.0,
        help_text="Percentage of time healthy in last 24 hours"
    )

    # Details
    details = models.JSONField(
        default=dict,
        help_text="Additional component-specific details"
    )
    last_error = models.TextField(
        blank=True,
        default='',
        help_text="Last error message if status is not healthy"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_component_status'
        verbose_name = 'Component Status'
        verbose_name_plural = 'Component Statuses'
        ordering = ['component']

    def __str__(self):
        return f"{self.display_name}: {self.status}"

    @classmethod
    def get_all_vitals(cls) -> dict:
        """Get current vitals for all components."""
        components = cls.objects.all()
        return {
            c.component: {
                'name': c.display_name,
                'status': c.status,
                'is_healthy': c.is_healthy,
                'last_check': c.last_check.isoformat() if c.last_check else None,
                'response_time_ms': c.response_time_ms,
                'uptime_percent_24h': c.uptime_percent_24h,
                'details': c.details,
                'last_error': c.last_error,
            }
            for c in components
        }

    def mark_healthy(self, response_time_ms: int = None, details: dict = None):
        """Update component as healthy."""
        now = timezone.now()
        self.status = StatusChoices.HEALTHY
        self.is_healthy = True
        self.last_check = now
        self.last_healthy = now
        self.last_error = ''
        if response_time_ms is not None:
            self.response_time_ms = response_time_ms
        if details is not None:
            self.details = details
        self.save()

    def mark_unhealthy(self, status: str, error: str, response_time_ms: int = None, details: dict = None):
        """Update component as unhealthy."""
        self.status = status
        self.is_healthy = False
        self.last_check = timezone.now()
        self.last_error = error
        self.error_count_24h += 1
        if response_time_ms is not None:
            self.response_time_ms = response_time_ms
        if details is not None:
            self.details = details
        self.save()
