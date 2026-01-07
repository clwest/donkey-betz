"""
Session 704: SPINE - Central API Router Models

The SPINE is the backbone of the AI body - central request routing and coordination.
Tracks API metrics, provides health-aware routing, and manages request flow.

Models:
- RoutePattern: Configuration for monitored route patterns
- RouteMetrics: Time-series records of route performance
- SpineStatus: Current routing status and health
"""

import uuid
from django.db import models
from django.utils import timezone


class RoutePattern(models.Model):
    """Configuration for a monitored API route pattern."""

    CATEGORY_CHOICES = [
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
    ]

    PRIORITY_CHOICES = [
        ('critical', 'Critical'),  # Must always be available
        ('high', 'High'),          # Degraded mode if unavailable
        ('normal', 'Normal'),      # Standard routing
        ('low', 'Low'),            # Can be rate-limited
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pattern = models.CharField(max_length=200, unique=True, help_text="URL pattern (regex or prefix)")
    display_name = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')

    # Health thresholds
    max_latency_ms = models.IntegerField(default=5000, help_text="Max acceptable latency in ms")
    max_error_rate = models.FloatField(default=0.05, help_text="Max acceptable error rate (0-1)")
    min_availability = models.FloatField(default=0.95, help_text="Minimum uptime (0-1)")

    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=0, help_text="Requests per minute (0=unlimited)")
    rate_limit_per_hour = models.IntegerField(default=0, help_text="Requests per hour (0=unlimited)")

    # Routing configuration
    requires_healthy_heart = models.BooleanField(default=False, help_text="Require HEART 'healthy' status")
    requires_healthy_lungs = models.BooleanField(default=False, help_text="Require LUNGS budget available")
    fallback_response = models.JSONField(default=dict, blank=True, help_text="Response when route unavailable")

    # Status
    is_active = models.BooleanField(default=True)
    is_monitored = models.BooleanField(default=True, help_text="Track metrics for this pattern")

    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_route_pattern'
        ordering = ['category', 'pattern']
        verbose_name = 'Route Pattern'
        verbose_name_plural = 'Route Patterns'

    def __str__(self):
        return f"{self.display_name or self.pattern} ({self.category})"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.pattern.replace('/', ' ').strip().title()
        super().save(*args, **kwargs)


class RouteMetrics(models.Model):
    """Time-series record of route performance metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pattern = models.ForeignKey(
        RoutePattern,
        on_delete=models.CASCADE,
        related_name='metrics_history'
    )

    # Request counts
    total_requests = models.BigIntegerField(default=0)
    successful_requests = models.BigIntegerField(default=0)
    failed_requests = models.BigIntegerField(default=0)
    rate_limited_requests = models.IntegerField(default=0)

    # Status code distribution
    status_2xx = models.IntegerField(default=0)
    status_3xx = models.IntegerField(default=0)
    status_4xx = models.IntegerField(default=0)
    status_5xx = models.IntegerField(default=0)

    # Latency metrics (milliseconds)
    avg_latency_ms = models.FloatField(default=0)
    p50_latency_ms = models.FloatField(default=0)
    p95_latency_ms = models.FloatField(default=0)
    p99_latency_ms = models.FloatField(default=0)
    max_latency_ms = models.FloatField(default=0)

    # Derived metrics
    success_rate = models.FloatField(default=1.0, help_text="Ratio of successful to total requests")
    error_rate = models.FloatField(default=0, help_text="Ratio of failed to total requests")
    throughput = models.FloatField(default=0, help_text="Requests per second")

    # Health status
    is_healthy = models.BooleanField(default=True)
    health_score = models.FloatField(default=100.0, help_text="0-100% health score")

    # Period info
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    period_duration_seconds = models.IntegerField(default=60)

    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_route_metrics'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['pattern', '-recorded_at']),
            models.Index(fields=['is_healthy', '-recorded_at']),
        ]
        verbose_name = 'Route Metrics'
        verbose_name_plural = 'Route Metrics'

    def __str__(self):
        return f"{self.pattern.pattern} @ {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    def calculate_health_score(self):
        """Calculate health score based on metrics."""
        score = 100.0

        # Deduct for error rate (up to 40 points)
        if self.error_rate > 0:
            score -= min(40, self.error_rate * 400)

        # Deduct for high latency (up to 30 points)
        if self.pattern.max_latency_ms > 0:
            latency_ratio = self.p95_latency_ms / self.pattern.max_latency_ms
            if latency_ratio > 1:
                score -= min(30, (latency_ratio - 1) * 30)

        # Deduct for rate limiting (up to 20 points)
        if self.total_requests > 0:
            rate_limited_ratio = self.rate_limited_requests / self.total_requests
            score -= min(20, rate_limited_ratio * 100)

        # Deduct for low success rate (up to 10 points)
        if self.success_rate < 1:
            score -= min(10, (1 - self.success_rate) * 100)

        return max(0, score)


class SpineStatus(models.Model):
    """Current spine status - cached routing health."""

    STATUS_CHOICES = [
        ('aligned', 'Aligned'),        # All routes healthy
        ('strained', 'Strained'),      # Some routes degraded
        ('compressed', 'Compressed'),  # High load, routing slowed
        ('injured', 'Injured'),        # Critical routes failing
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Overall status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aligned')
    is_healthy = models.BooleanField(default=True)
    health_score = models.FloatField(default=100.0, help_text="0-100% spine health")

    # Route counts
    total_patterns = models.IntegerField(default=0)
    healthy_patterns = models.IntegerField(default=0)
    degraded_patterns = models.IntegerField(default=0)
    failed_patterns = models.IntegerField(default=0)

    # Request metrics (last check period)
    total_requests = models.BigIntegerField(default=0)
    requests_per_second = models.FloatField(default=0)
    avg_latency_ms = models.FloatField(default=0)
    error_rate = models.FloatField(default=0)

    # Category breakdown
    category_health = models.JSONField(default=dict, help_text="Health score by category")

    # Integration status
    heart_status = models.CharField(max_length=20, blank=True, help_text="HEART service status")
    lungs_status = models.CharField(max_length=20, blank=True, help_text="LUNGS service status")
    circulatory_status = models.CharField(max_length=20, blank=True, help_text="CIRCULATORY status")

    # Routing decisions
    routes_blocked = models.IntegerField(default=0, help_text="Routes blocked due to health")
    routes_rate_limited = models.IntegerField(default=0, help_text="Routes currently rate limited")
    fallbacks_active = models.IntegerField(default=0, help_text="Routes using fallback responses")

    # Timestamps
    last_check = models.DateTimeField(auto_now=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)

    # Alert tracking
    alert_sent = models.BooleanField(default=False)
    last_alert_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_spine_status'
        verbose_name = 'Spine Status'
        verbose_name_plural = 'Spine Statuses'

    def __str__(self):
        return f"Spine: {self.status} ({self.health_score:.1f}%)"

    def update_status(self, new_status: str, health_score: float):
        """Update status and track changes."""
        if self.status != new_status:
            self.status_changed_at = timezone.now()
            # Reset alert flag when recovering
            if new_status == 'aligned':
                self.alert_sent = False

        self.status = new_status
        self.health_score = health_score
        self.is_healthy = new_status in ('aligned', 'strained')

    def get_status_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'aligned': '🦴',      # Healthy spine
            'strained': '⚡',     # Some stress
            'compressed': '🔧',   # Under pressure
            'injured': '🚨',      # Critical
        }.get(self.status, '❓')


class RequestTrace(models.Model):
    """Individual request trace for detailed analysis."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correlation_id = models.CharField(max_length=64, unique=True, db_index=True)

    # Request info
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    pattern = models.ForeignKey(
        RoutePattern,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='traces'
    )

    # User info
    user_id = models.IntegerField(null=True, blank=True)
    is_authenticated = models.BooleanField(default=False)
    client_ip = models.GenericIPAddressField(null=True, blank=True)

    # Timing
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.FloatField(null=True, blank=True)

    # Response
    status_code = models.IntegerField(null=True, blank=True)
    response_size = models.IntegerField(null=True, blank=True)

    # Routing decisions
    was_rate_limited = models.BooleanField(default=False)
    used_fallback = models.BooleanField(default=False)
    health_check_result = models.JSONField(default=dict, blank=True)

    # Agent/service info
    routed_to_agent = models.CharField(max_length=100, blank=True)
    llm_model_used = models.CharField(max_length=100, blank=True)

    # Error info
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'core_request_trace'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['-started_at']),
            models.Index(fields=['correlation_id']),
            models.Index(fields=['path', '-started_at']),
            models.Index(fields=['status_code', '-started_at']),
        ]
        verbose_name = 'Request Trace'
        verbose_name_plural = 'Request Traces'

    def __str__(self):
        return f"{self.method} {self.path} ({self.status_code}) - {self.correlation_id[:8]}"

    def complete(self, status_code: int, response_size: int = None):
        """Mark request as complete."""
        self.ended_at = timezone.now()
        self.status_code = status_code
        self.response_size = response_size
        if self.started_at:
            self.duration_ms = (self.ended_at - self.started_at).total_seconds() * 1000
        self.save()
