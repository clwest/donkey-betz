"""
Session 705: IMMUNE SYSTEM - Security & Threat Detection Models

The IMMUNE SYSTEM is the defense layer of the AI body - detecting and responding
to threats, suspicious patterns, and malicious activity.

Models:
- ThreatPattern: Known threat signatures to detect
- ThreatEvent: Individual threat detections/incidents
- ImmuneResponse: Actions taken in response to threats
- ImmuneStatus: Current immune system health and activity
- Quarantine: Blocked/restricted entities

Human Body Metaphor:
- Pathogens = Malicious requests, suspicious patterns
- Antibodies = Detection rules and patterns
- White Blood Cells = Active monitoring and response
- Fever = Elevated alert state
- Inflammation = Rate limiting, blocking
- Immune Memory = Historical threat database
"""

import uuid
from django.db import models
from django.utils import timezone


class ThreatPattern(models.Model):
    """Known threat patterns to detect - like antibodies recognizing antigens."""

    CATEGORY_CHOICES = [
        ('rate_abuse', 'Rate Limit Abuse'),
        ('auth_attack', 'Authentication Attack'),
        ('injection', 'Injection Attempt'),
        ('scraping', 'Aggressive Scraping'),
        ('dos', 'Denial of Service'),
        ('enumeration', 'Resource Enumeration'),
        ('privilege', 'Privilege Escalation'),
        ('data_exfil', 'Data Exfiltration'),
        ('bot', 'Bot/Automation'),
        ('anomaly', 'Behavioral Anomaly'),
        ('other', 'Other'),
    ]

    SEVERITY_CHOICES = [
        ('critical', 'Critical'),    # Immediate action required
        ('high', 'High'),            # Block and alert
        ('medium', 'Medium'),        # Rate limit and log
        ('low', 'Low'),              # Log and monitor
        ('info', 'Informational'),   # Just log
    ]

    DETECTION_TYPE_CHOICES = [
        ('signature', 'Signature Match'),     # Known pattern
        ('threshold', 'Threshold Exceeded'),  # Rate/count based
        ('anomaly', 'Anomaly Detection'),     # ML/statistical
        ('reputation', 'Reputation Based'),   # IP/user reputation
        ('behavioral', 'Behavioral'),         # Action sequence
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    detection_type = models.CharField(max_length=20, choices=DETECTION_TYPE_CHOICES, default='signature')

    # Detection configuration
    pattern = models.TextField(help_text="Regex pattern, threshold config, or detection rules (JSON)")
    description = models.TextField(blank=True)

    # Thresholds for threshold-based detection
    threshold_count = models.IntegerField(default=0, help_text="Number of occurrences to trigger")
    threshold_window_seconds = models.IntegerField(default=60, help_text="Time window for threshold")

    # Response configuration
    auto_respond = models.BooleanField(default=True, help_text="Automatically respond to detections")
    response_action = models.CharField(
        max_length=20,
        choices=[
            ('log', 'Log Only'),
            ('rate_limit', 'Rate Limit'),
            ('block_temp', 'Temporary Block'),
            ('block_perm', 'Permanent Block'),
            ('quarantine', 'Quarantine'),
            ('alert', 'Alert Only'),
        ],
        default='log'
    )
    block_duration_minutes = models.IntegerField(default=60, help_text="Duration for temporary blocks")

    # Status
    is_active = models.BooleanField(default=True)
    is_builtin = models.BooleanField(default=False, help_text="System-defined pattern")

    # Statistics
    total_detections = models.BigIntegerField(default=0)
    last_detection = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_threat_pattern'
        ordering = ['severity', 'category', 'name']
        verbose_name = 'Threat Pattern'
        verbose_name_plural = 'Threat Patterns'

    def __str__(self):
        return f"{self.display_name or self.name} ({self.severity})"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.replace('_', ' ').title()
        super().save(*args, **kwargs)


class ThreatEvent(models.Model):
    """Individual threat detection - like a pathogen encounter."""

    STATUS_CHOICES = [
        ('detected', 'Detected'),        # Just detected
        ('analyzing', 'Analyzing'),      # Being analyzed
        ('responded', 'Responded'),      # Response taken
        ('resolved', 'Resolved'),        # Threat neutralized
        ('false_positive', 'False Positive'),  # Not a real threat
        ('escalated', 'Escalated'),      # Requires human review
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pattern = models.ForeignKey(
        ThreatPattern,
        on_delete=models.SET_NULL,
        null=True,
        related_name='events'
    )

    # Detection info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected')
    severity = models.CharField(max_length=20, choices=ThreatPattern.SEVERITY_CHOICES)
    category = models.CharField(max_length=20, choices=ThreatPattern.CATEGORY_CHOICES)

    # Source identification
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    source_user_id = models.IntegerField(null=True, blank=True)
    source_user_agent = models.TextField(blank=True)
    source_path = models.CharField(max_length=500, blank=True)
    source_method = models.CharField(max_length=10, blank=True)

    # Detection details
    detection_details = models.JSONField(default=dict, help_text="Details of what triggered detection")
    confidence_score = models.FloatField(default=1.0, help_text="0-1 confidence in detection")

    # Request context
    request_count = models.IntegerField(default=1, help_text="Number of requests in this event")
    correlation_ids = models.JSONField(default=list, help_text="Related request correlation IDs")

    # Response tracking
    response_taken = models.CharField(max_length=20, blank=True)
    response_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'core_threat_event'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['-detected_at']),
            models.Index(fields=['status', '-detected_at']),
            models.Index(fields=['severity', '-detected_at']),
            models.Index(fields=['source_ip', '-detected_at']),
            models.Index(fields=['category', '-detected_at']),
        ]
        verbose_name = 'Threat Event'
        verbose_name_plural = 'Threat Events'

    def __str__(self):
        return f"{self.category} - {self.severity} @ {self.detected_at.strftime('%Y-%m-%d %H:%M')}"

    def resolve(self, resolution: str = 'resolved'):
        """Mark threat as resolved."""
        self.status = resolution
        self.resolved_at = timezone.now()
        self.save()


class ImmuneResponse(models.Model):
    """Actions taken in response to threats - like immune system responses."""

    ACTION_CHOICES = [
        ('log', 'Logged'),
        ('rate_limit', 'Rate Limited'),
        ('block_temp', 'Temporarily Blocked'),
        ('block_perm', 'Permanently Blocked'),
        ('quarantine', 'Quarantined'),
        ('alert_sent', 'Alert Sent'),
        ('escalated', 'Escalated to Human'),
        ('whitelisted', 'Whitelisted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ThreatEvent,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    # Response details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    is_automatic = models.BooleanField(default=True)
    success = models.BooleanField(default=True)

    # Target of response
    target_type = models.CharField(max_length=20, choices=[
        ('ip', 'IP Address'),
        ('user', 'User Account'),
        ('path', 'API Path'),
        ('session', 'Session'),
    ])
    target_value = models.CharField(max_length=200)

    # Duration for temporary actions
    duration_minutes = models.IntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    details = models.JSONField(default=dict)
    responded_at = models.DateTimeField(auto_now_add=True)
    responded_by = models.CharField(max_length=100, default='immune_system')

    class Meta:
        db_table = 'core_immune_response'
        ordering = ['-responded_at']
        verbose_name = 'Immune Response'
        verbose_name_plural = 'Immune Responses'

    def __str__(self):
        return f"{self.action} on {self.target_type}:{self.target_value}"

    def is_expired(self) -> bool:
        """Check if this response has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class Quarantine(models.Model):
    """Quarantined entities - blocked IPs, users, etc."""

    ENTITY_TYPE_CHOICES = [
        ('ip', 'IP Address'),
        ('ip_range', 'IP Range'),
        ('user', 'User Account'),
        ('user_agent', 'User Agent'),
        ('path', 'API Path Pattern'),
    ]

    REASON_CHOICES = [
        ('rate_abuse', 'Rate Limit Abuse'),
        ('auth_attack', 'Authentication Attack'),
        ('injection', 'Injection Attempt'),
        ('scraping', 'Aggressive Scraping'),
        ('dos', 'Denial of Service'),
        ('manual', 'Manual Block'),
        ('reputation', 'Bad Reputation'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Entity identification
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)
    entity_value = models.CharField(max_length=200, db_index=True)

    # Block details
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    is_permanent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Related events
    related_events = models.ManyToManyField(ThreatEvent, blank=True, related_name='quarantines')
    total_events = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)

    # Statistics
    blocked_requests = models.BigIntegerField(default=0)
    last_blocked_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, default='immune_system')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_quarantine'
        ordering = ['-created_at']
        unique_together = [['entity_type', 'entity_value']]
        indexes = [
            models.Index(fields=['entity_type', 'entity_value']),
            models.Index(fields=['is_active', 'expires_at']),
        ]
        verbose_name = 'Quarantine Entry'
        verbose_name_plural = 'Quarantine Entries'

    def __str__(self):
        status = "permanent" if self.is_permanent else f"until {self.expires_at}"
        return f"{self.entity_type}:{self.entity_value} ({status})"

    def is_expired(self) -> bool:
        """Check if quarantine has expired."""
        if self.is_permanent:
            return False
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def record_block(self):
        """Record a blocked request."""
        self.blocked_requests += 1
        self.last_blocked_at = timezone.now()
        self.save(update_fields=['blocked_requests', 'last_blocked_at'])


class ImmuneStatus(models.Model):
    """Current immune system status - overall health and activity."""

    STATUS_CHOICES = [
        ('healthy', 'Healthy'),           # Normal operation
        ('alert', 'Alert'),               # Elevated threat level
        ('fighting', 'Fighting'),         # Active threat response
        ('overwhelmed', 'Overwhelmed'),   # Too many threats
        ('compromised', 'Compromised'),   # System may be breached
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Overall status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='healthy')
    is_healthy = models.BooleanField(default=True)
    health_score = models.FloatField(default=100.0, help_text="0-100% immune health")

    # Threat levels
    threat_level = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('low', 'Low'),
            ('elevated', 'Elevated'),
            ('high', 'High'),
            ('severe', 'Severe'),
        ],
        default='none'
    )

    # Current activity
    active_threats = models.IntegerField(default=0)
    threats_detected_24h = models.IntegerField(default=0)
    threats_blocked_24h = models.IntegerField(default=0)
    false_positives_24h = models.IntegerField(default=0)

    # Quarantine status
    quarantined_ips = models.IntegerField(default=0)
    quarantined_users = models.IntegerField(default=0)
    total_quarantined = models.IntegerField(default=0)

    # Pattern activity
    active_patterns = models.IntegerField(default=0)
    patterns_triggered_24h = models.IntegerField(default=0)

    # Response metrics
    auto_responses_24h = models.IntegerField(default=0)
    manual_responses_24h = models.IntegerField(default=0)
    avg_response_time_ms = models.FloatField(default=0)

    # Category breakdown
    threats_by_category = models.JSONField(default=dict)
    threats_by_severity = models.JSONField(default=dict)

    # Integration status
    spine_connected = models.BooleanField(default=False)
    heart_connected = models.BooleanField(default=False)

    # Timestamps
    last_scan = models.DateTimeField(auto_now=True)
    last_threat = models.DateTimeField(null=True, blank=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)

    # Alerts
    alert_sent = models.BooleanField(default=False)
    last_alert_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_immune_status'
        verbose_name = 'Immune Status'
        verbose_name_plural = 'Immune Statuses'

    def __str__(self):
        return f"Immune: {self.status} ({self.health_score:.1f}%) - Threat Level: {self.threat_level}"

    def update_status(self, new_status: str, health_score: float, threat_level: str):
        """Update status and track changes."""
        if self.status != new_status:
            self.status_changed_at = timezone.now()
            # Reset alert flag when recovering
            if new_status == 'healthy':
                self.alert_sent = False

        self.status = new_status
        self.health_score = health_score
        self.threat_level = threat_level
        self.is_healthy = new_status in ('healthy', 'alert')

    def get_status_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'healthy': '🛡️',      # Shield - protected
            'alert': '⚠️',        # Warning
            'fighting': '⚔️',     # Sword - active defense
            'overwhelmed': '🔥',  # Fire - under attack
            'compromised': '💀',  # Skull - critical
        }.get(self.status, '❓')
