"""
Session 703: CIRCULATORY SYSTEM Models

The circulatory system monitors data flow health - the "blood flow" of the AI body.
Tracks Redis queues, Celery tasks, WebSocket channels, and event streams.

Models:
- FlowRoute: Configuration for monitored data flow routes
- CirculationPulse: Time-series records of circulation state
- FlowStatus: Current flow status per route (cached state)
"""

import uuid
from django.db import models
from django.utils import timezone


class FlowRoute(models.Model):
    """Configuration for a monitored data flow route."""

    ROUTE_TYPE_CHOICES = [
        ('redis_queue', 'Redis Queue'),
        ('celery_queue', 'Celery Queue'),
        ('websocket', 'WebSocket Channel'),
        ('event_stream', 'Event Stream'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPE_CHOICES)
    identifier = models.CharField(max_length=200, help_text="Queue name, channel, or stream identifier")

    # Thresholds for health determination
    max_depth = models.IntegerField(default=1000, help_text="Queue depth warning threshold")
    max_latency_ms = models.IntegerField(default=5000, help_text="Latency warning threshold in milliseconds")
    min_throughput = models.FloatField(default=0, help_text="Minimum items/sec (0 = no minimum)")

    # Status flags
    is_active = models.BooleanField(default=True)
    is_critical = models.BooleanField(default=False, help_text="Send Discord alert on failure")

    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_flow_route'
        ordering = ['route_type', 'name']
        verbose_name = 'Flow Route'
        verbose_name_plural = 'Flow Routes'

    def __str__(self):
        return f"{self.display_name or self.name} ({self.route_type})"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.replace('_', ' ').title()
        super().save(*args, **kwargs)


class CirculationPulse(models.Model):
    """Time-series record of circulation state - captures system-wide flow health."""

    OVERALL_STATUS_CHOICES = [
        ('flowing', 'Flowing'),        # 80-100% healthy
        ('slow', 'Slow'),              # 50-79% - some latency
        ('congested', 'Congested'),    # 20-49% - queue depth issues
        ('blocked', 'Blocked'),        # 0-19% - critical flow issues
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Overall metrics
    overall_status = models.CharField(max_length=20, choices=OVERALL_STATUS_CHOICES, default='flowing')
    flow_score = models.FloatField(default=100.0, help_text="0-100% overall flow health")

    # Aggregate route metrics
    total_routes_checked = models.IntegerField(default=0)
    routes_healthy = models.IntegerField(default=0)
    routes_slow = models.IntegerField(default=0)
    routes_congested = models.IntegerField(default=0)
    routes_blocked = models.IntegerField(default=0)

    # Flow metrics
    total_items_in_transit = models.BigIntegerField(default=0, help_text="Total items across all queues")
    total_throughput = models.FloatField(default=0, help_text="Combined items/sec across all routes")
    avg_latency_ms = models.FloatField(default=0, help_text="Average latency across all routes")
    max_latency_ms = models.FloatField(default=0, help_text="Maximum latency detected")

    # Bottleneck tracking
    bottlenecks = models.JSONField(default=list, help_text="List of detected bottlenecks")
    bottleneck_count = models.IntegerField(default=0)

    # Route-level details (JSON for flexibility)
    route_details = models.JSONField(default=dict, help_text="Per-route status details")

    # Check metadata
    check_duration_ms = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_circulation_pulse'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['overall_status', '-recorded_at']),
            models.Index(fields=['flow_score', '-recorded_at']),
        ]
        verbose_name = 'Circulation Pulse'
        verbose_name_plural = 'Circulation Pulses'

    def __str__(self):
        return f"Pulse {self.recorded_at.strftime('%Y-%m-%d %H:%M:%S')} - {self.overall_status} ({self.flow_score:.1f}%)"


class FlowStatus(models.Model):
    """Current flow status per route - cached state for quick access."""

    STATUS_CHOICES = [
        ('flowing', 'Flowing'),        # Normal operation
        ('slow', 'Slow'),              # High latency but working
        ('congested', 'Congested'),    # High queue depth
        ('blocked', 'Blocked'),        # No flow / errors
    ]

    route = models.OneToOneField(
        FlowRoute,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='current_status'
    )

    # Current state
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='flowing')
    is_healthy = models.BooleanField(default=True)
    health_score = models.FloatField(default=100.0, help_text="0-100% route health")

    # Current metrics
    current_depth = models.IntegerField(default=0, help_text="Current queue depth")
    current_throughput = models.FloatField(default=0, help_text="Current items/sec")
    current_latency_ms = models.FloatField(default=0, help_text="Current latency in ms")

    # Rolling 24h metrics
    items_processed_24h = models.BigIntegerField(default=0)
    errors_24h = models.IntegerField(default=0)
    avg_latency_24h_ms = models.FloatField(default=0)
    peak_depth_24h = models.IntegerField(default=0)
    peak_latency_24h_ms = models.FloatField(default=0)

    # Worker/connection metrics (for Celery queues)
    active_workers = models.IntegerField(default=0)
    active_tasks = models.IntegerField(default=0)
    reserved_tasks = models.IntegerField(default=0)

    # Timestamps
    last_activity = models.DateTimeField(null=True, blank=True)
    last_check = models.DateTimeField(auto_now=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)

    # Alert tracking
    congestion_alert_sent = models.BooleanField(default=False)
    blocked_alert_sent = models.BooleanField(default=False)
    last_alert_at = models.DateTimeField(null=True, blank=True)

    # Additional details
    details = models.JSONField(default=dict, help_text="Additional route-specific details")
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'core_flow_status'
        verbose_name = 'Flow Status'
        verbose_name_plural = 'Flow Statuses'

    def __str__(self):
        return f"{self.route.name}: {self.status} ({self.health_score:.1f}%)"

    def update_status(self, new_status: str, health_score: float):
        """Update status and track changes."""
        if self.status != new_status:
            self.status_changed_at = timezone.now()
            # Reset alert flags when recovering
            if new_status == 'flowing':
                self.congestion_alert_sent = False
                self.blocked_alert_sent = False

        self.status = new_status
        self.health_score = health_score
        self.is_healthy = new_status in ('flowing', 'slow')

    def get_status_display_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'flowing': '🩸',      # Blood flowing
            'slow': '🐌',         # Slow
            'congested': '⚠️',    # Warning
            'blocked': '🚫',      # Blocked
        }.get(self.status, '❓')
