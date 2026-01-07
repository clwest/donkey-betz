"""
Session 706: DIGESTIVE SYSTEM - Data Ingestion & Processing Models

The DIGESTIVE SYSTEM is the data processing layer of the AI body - monitoring
how raw spider data is transformed into actionable intelligence.

Models:
- IngestionRoute: Configuration for monitored data ingestion routes
- DigestivePulse: Time-series records of digestion state
- DigestionStatus: Current digestion status per route (cached state)

Human Body Metaphor:
- Food = Raw spider data (RSS, API responses, scraped content)
- Mouth/Intake = Spider execution -> SpiderData creation
- Stomach = Processing queue - normalization, deduplication
- Enzymes = Transformation functions - embedding, scoring
- Intestines = Routing pipeline to agents/services
- Nutrients = Actionable intelligence (normalized, scored data)
- Waste = Filtered/irrelevant data (low scores, duplicates)
- Metabolism Rate = Processing throughput (items/minute)
"""

import uuid
from django.db import models
from django.utils import timezone


class IngestionRoute(models.Model):
    """Configuration for a monitored data ingestion route."""

    ROUTE_TYPE_CHOICES = [
        ('spider', 'Spider Data'),
        ('api', 'External API'),
        ('webhook', 'Webhook'),
        ('upload', 'File Upload'),
        ('stream', 'Event Stream'),
    ]

    STAGE_CHOICES = [
        ('intake', 'Intake'),           # Raw data received
        ('processing', 'Processing'),   # Being transformed
        ('enrichment', 'Enrichment'),   # Embeddings, scoring
        ('routing', 'Routing'),         # Sent to consumers
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPE_CHOICES)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    identifier = models.CharField(max_length=200, help_text="Spider category, API name, stream ID")
    description = models.TextField(blank=True)

    # Thresholds
    max_queue_depth = models.IntegerField(default=500, help_text="Max items waiting before warning")
    target_throughput = models.FloatField(default=10.0, help_text="Target items/minute")
    max_processing_time_ms = models.IntegerField(default=5000, help_text="Max processing time per item")

    # Status
    is_active = models.BooleanField(default=True)
    is_critical = models.BooleanField(default=False, help_text="Alert on failure")
    is_builtin = models.BooleanField(default=False, help_text="System-defined route")

    # Statistics
    total_items_processed = models.BigIntegerField(default=0)
    total_errors = models.BigIntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_ingestion_route'
        ordering = ['stage', 'route_type', 'name']
        verbose_name = 'Ingestion Route'
        verbose_name_plural = 'Ingestion Routes'

    def __str__(self):
        return f"{self.display_name or self.name} ({self.stage}/{self.route_type})"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.replace('_', ' ').title()
        super().save(*args, **kwargs)


class DigestivePulse(models.Model):
    """Time-series record of digestion state - periodic snapshots."""

    STATUS_CHOICES = [
        ('healthy', 'Healthy'),        # Normal data processing
        ('sluggish', 'Sluggish'),      # Slow processing, minor delays
        ('bloated', 'Bloated'),        # High queue depth, backlog
        ('blocked', 'Blocked'),        # Processing stuck
        ('starving', 'Starving'),      # No data intake
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Overall metrics
    overall_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='healthy')
    digestion_score = models.FloatField(default=100.0, help_text="0-100% digestion health")
    is_digesting = models.BooleanField(default=True)

    # Intake metrics (24h)
    items_ingested_24h = models.IntegerField(default=0)
    spiders_executed_24h = models.IntegerField(default=0)
    spider_success_rate = models.FloatField(default=100.0)
    intake_errors_24h = models.IntegerField(default=0)
    duplicates_filtered_24h = models.IntegerField(default=0)

    # Processing metrics
    items_processed_24h = models.IntegerField(default=0)
    items_pending = models.IntegerField(default=0, help_text="Queue depth")
    processing_throughput = models.FloatField(default=0, help_text="Items/minute")
    avg_processing_time_ms = models.FloatField(default=0)
    processing_errors_24h = models.IntegerField(default=0)

    # Enrichment metrics
    embeddings_generated_24h = models.IntegerField(default=0)
    embedding_coverage_pct = models.FloatField(default=0, help_text="% of items with embeddings")
    relevance_scores_calculated_24h = models.IntegerField(default=0)
    enrichment_errors_24h = models.IntegerField(default=0)

    # Output/Routing metrics
    items_routed_24h = models.IntegerField(default=0)
    items_filtered_24h = models.IntegerField(default=0, help_text="Low relevance filtered out")
    items_actionable_24h = models.IntegerField(default=0)
    routing_errors_24h = models.IntegerField(default=0)

    # Metabolism (throughput rates)
    intake_rate = models.FloatField(default=0, help_text="Items ingested per minute")
    processing_rate = models.FloatField(default=0, help_text="Items processed per minute")
    output_rate = models.FloatField(default=0, help_text="Items output per minute")

    # Stage-specific statuses
    intake_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='healthy')
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='healthy')
    enrichment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='healthy')
    routing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='healthy')

    # Bottlenecks detected
    bottlenecks = models.JSONField(default=list)

    # Routes checked
    routes_checked = models.IntegerField(default=0)
    routes_healthy = models.IntegerField(default=0)
    routes_warning = models.IntegerField(default=0)
    routes_critical = models.IntegerField(default=0)

    # Integration status
    heart_connected = models.BooleanField(default=False)
    circulatory_connected = models.BooleanField(default=False)

    # Check metadata
    check_duration_ms = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_digestive_pulse'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['overall_status', '-recorded_at']),
        ]
        verbose_name = 'Digestive Pulse'
        verbose_name_plural = 'Digestive Pulses'

    def __str__(self):
        return f"Digestion: {self.overall_status} ({self.digestion_score:.1f}%) @ {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    def get_status_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'healthy': '🍽️',     # Plate - digesting well
            'sluggish': '🐌',    # Snail - slow
            'bloated': '🎈',     # Balloon - full/backed up
            'blocked': '🚫',     # No entry - stuck
            'starving': '💀',    # Skull - no input
        }.get(self.overall_status, '❓')


class DigestionStatus(models.Model):
    """Current digestion status per route - cached state updated on each check."""

    STATUS_CHOICES = [
        ('healthy', 'Healthy'),        # Normal digestion
        ('sluggish', 'Sluggish'),      # Slow processing
        ('bloated', 'Bloated'),        # High queue depth
        ('blocked', 'Blocked'),        # Processing stuck
        ('starving', 'Starving'),      # No intake
    ]

    route = models.OneToOneField(
        IngestionRoute,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='status'
    )

    # Current status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='healthy')
    is_healthy = models.BooleanField(default=True)

    # Current metrics
    current_queue_depth = models.IntegerField(default=0)
    current_throughput = models.FloatField(default=0, help_text="Current items/minute")
    current_latency_ms = models.FloatField(default=0, help_text="Current avg processing time")

    # 24h rolling metrics
    items_ingested_24h = models.IntegerField(default=0)
    items_processed_24h = models.IntegerField(default=0)
    items_output_24h = models.IntegerField(default=0)
    errors_24h = models.IntegerField(default=0)
    success_rate_24h = models.FloatField(default=100.0)

    # Timestamps
    last_intake = models.DateTimeField(null=True, blank=True)
    last_output = models.DateTimeField(null=True, blank=True)
    last_error = models.DateTimeField(null=True, blank=True)
    last_check = models.DateTimeField(auto_now=True)

    # Alert tracking
    warning_alert_sent = models.BooleanField(default=False)
    critical_alert_sent = models.BooleanField(default=False)
    last_alert_at = models.DateTimeField(null=True, blank=True)

    # Notes
    last_error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'core_digestion_status'
        verbose_name = 'Digestion Status'
        verbose_name_plural = 'Digestion Statuses'

    def __str__(self):
        return f"{self.route.name}: {self.status} ({self.success_rate_24h:.1f}%)"

    def update_status(self, new_status: str, is_healthy: bool):
        """Update status and reset alerts if recovering."""
        if self.status != new_status:
            # Reset alerts when recovering to healthy
            if new_status == 'healthy':
                self.warning_alert_sent = False
                self.critical_alert_sent = False

        self.status = new_status
        self.is_healthy = is_healthy

    def get_status_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'healthy': '🍽️',
            'sluggish': '🐌',
            'bloated': '🎈',
            'blocked': '🚫',
            'starving': '💀',
        }.get(self.status, '❓')
