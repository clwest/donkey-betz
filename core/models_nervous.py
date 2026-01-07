"""
Session 724: NERVOUS SYSTEM - WebSocket Communication Monitoring

The NERVOUS system monitors real-time WebSocket communication - the nerves
that carry signals throughout the AI body. This includes connection health,
message throughput, latency, and channel layer status.

Human Body Metaphor:
- Nerves = WebSocket connections
- Nerve signals = WebSocket messages
- Synapses = Redis channel layer
- Neural pathways = Message routing
- Reflexes = Fast real-time updates
- Numbness = Disconnected consumers
- Pain signals = Connection errors
- Conduction velocity = Message latency
"""

import uuid
from django.db import models


class NervousPulse(models.Model):
    """
    Time-series record of nervous system health.
    Records WebSocket metrics at regular intervals.
    """

    STATUS_CHOICES = [
        ('responsive', 'Responsive'),      # Normal operation
        ('active', 'Active'),              # High activity
        ('sluggish', 'Sluggish'),          # Slow responses
        ('numb', 'Numb'),                  # Low connectivity
        ('overloaded', 'Overloaded'),      # Too many connections
        ('damaged', 'Damaged'),            # High error rate
        ('dormant', 'Dormant'),            # No activity
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Overall status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='responsive')
    health_score = models.FloatField(default=100.0, help_text='Overall nervous health 0-100')

    # Connection metrics
    total_consumers = models.IntegerField(default=0, help_text='Total registered consumer types')
    active_connections = models.IntegerField(default=0, help_text='Current WebSocket connections')
    peak_connections_24h = models.IntegerField(default=0, help_text='Max connections in 24h')
    disconnections_24h = models.IntegerField(default=0, help_text='Connection drops in 24h')
    connection_errors_24h = models.IntegerField(default=0, help_text='Connection errors in 24h')

    # Message metrics
    messages_sent_24h = models.IntegerField(default=0, help_text='Messages sent in 24h')
    messages_received_24h = models.IntegerField(default=0, help_text='Messages received in 24h')
    messages_per_second = models.FloatField(default=0, help_text='Current throughput')
    peak_messages_per_second = models.FloatField(default=0, help_text='Peak throughput in 24h')

    # Latency metrics
    avg_latency_ms = models.FloatField(default=0, help_text='Average message latency')
    max_latency_ms = models.FloatField(default=0, help_text='Max latency in 24h')
    p95_latency_ms = models.FloatField(default=0, help_text='95th percentile latency')

    # Channel layer metrics (Redis)
    channel_layer_connected = models.BooleanField(default=True)
    redis_ping_ms = models.FloatField(default=0, help_text='Redis ping latency')
    active_groups = models.IntegerField(default=0, help_text='Active channel groups')
    group_members = models.IntegerField(default=0, help_text='Total group memberships')

    # Consumer breakdown
    consumer_stats = models.JSONField(default=dict, help_text='Per-consumer metrics')
    busiest_consumers = models.JSONField(default=list, help_text='Most active consumers')
    error_consumers = models.JSONField(default=list, help_text='Consumers with errors')

    # Check metadata
    check_duration_ms = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Nervous Pulse'
        verbose_name_plural = 'Nervous Pulses'
        db_table = 'core_nervous_pulses'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at'], name='core_nervous_recorded_idx'),
            models.Index(fields=['status', '-recorded_at'], name='core_nervous_status_idx'),
        ]

    def __str__(self):
        return f"NervousPulse({self.status}, {self.health_score:.1f}%) @ {self.recorded_at}"


class NervousStatus(models.Model):
    """
    Current nervous system status - singleton cache.
    Updated by feel() method for fast status lookups.
    """

    STATUS_CHOICES = [
        ('responsive', 'Responsive'),
        ('active', 'Active'),
        ('sluggish', 'Sluggish'),
        ('numb', 'Numb'),
        ('overloaded', 'Overloaded'),
        ('damaged', 'Damaged'),
        ('dormant', 'Dormant'),
    ]

    # Singleton - always id=1
    id = models.IntegerField(primary_key=True, default=1)

    # Current status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='responsive')
    is_healthy = models.BooleanField(default=True)
    health_score = models.FloatField(default=100.0)

    # Connection summary
    total_consumers = models.IntegerField(default=0)
    active_connections = models.IntegerField(default=0)
    connection_rate = models.FloatField(default=0, help_text='Connections per minute')

    # Message summary
    messages_24h = models.IntegerField(default=0)
    messages_per_second = models.FloatField(default=0)
    avg_latency_ms = models.FloatField(default=0)

    # Channel layer
    channel_layer_healthy = models.BooleanField(default=True)
    redis_latency_ms = models.FloatField(default=0)
    active_groups = models.IntegerField(default=0)

    # Error summary
    error_rate = models.FloatField(default=0, help_text='Error percentage')
    disconnections_24h = models.IntegerField(default=0)

    # Activity level
    activity_level = models.CharField(
        max_length=20,
        default='normal',
        help_text='dormant, low, normal, high, intense'
    )

    # Timestamps
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    last_check = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Nervous Status'
        verbose_name_plural = 'Nervous Status'
        db_table = 'core_nervous_status'

    def __str__(self):
        return f"NervousStatus: {self.status} ({self.health_score:.1f}%)"

    @classmethod
    def get_current(cls):
        """Get or create the singleton status."""
        status, _ = cls.objects.get_or_create(id=1)
        return status


class WebSocketConnectionLog(models.Model):
    """
    Log of WebSocket connection events for debugging and analytics.
    """

    EVENT_CHOICES = [
        ('connect', 'Connected'),
        ('disconnect', 'Disconnected'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Connection info
    consumer_name = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=200, blank=True)
    group_name = models.CharField(max_length=100, blank=True)

    # Event
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    error_message = models.TextField(blank=True)

    # Client info
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    user_id = models.IntegerField(null=True, blank=True)

    # Duration (for disconnects)
    connection_duration_ms = models.IntegerField(null=True, blank=True)
    messages_during_session = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'WebSocket Connection Log'
        verbose_name_plural = 'WebSocket Connection Logs'
        db_table = 'core_websocket_connection_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='core_ws_log_created_idx'),
            models.Index(fields=['consumer_name', '-created_at'], name='core_ws_log_consumer_idx'),
            models.Index(fields=['event', '-created_at'], name='core_ws_log_event_idx'),
        ]

    def __str__(self):
        return f"{self.consumer_name} {self.event} @ {self.created_at}"
