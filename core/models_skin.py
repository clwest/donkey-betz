"""
SKIN Body System Models - Project Workspace Health Monitoring

The SKIN is the boundary layer where the AI system interfaces with actual
project workspaces - the execution environment that turns AI-generated
code into real, working software.

Session: 723

Human Body Metaphor:
    Skin Surface    = Project workspaces
    Pores           = File write operations
    Touch/Sensation = File change detection
    Healing         = Rollback capability
    Skin Health     = Workspace integrity
    Irritation      = Failed writes, permission errors
    Sweating        = High activity/throughput
"""

import uuid
from django.db import models
from django.utils import timezone


class SkinPulse(models.Model):
    """
    Time-series record of SKIN system state.
    Captures workspace activity and health metrics over time.
    """

    STATUS_CHOICES = [
        ('healthy', 'Healthy'),         # Normal operations, good success rate
        ('active', 'Active'),           # High activity, all good
        ('sweating', 'Sweating'),       # Very high activity (throughput)
        ('irritated', 'Irritated'),     # Some errors/failures
        ('damaged', 'Damaged'),         # High error rate, needs attention
        ('healing', 'Healing'),         # Rollbacks in progress
        ('dormant', 'Dormant'),         # No recent activity
    ]

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Overall Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='healthy'
    )
    health_score = models.FloatField(
        default=100.0,
        help_text="Overall skin health 0-100"
    )

    # Workspace Metrics
    total_workspaces = models.IntegerField(default=0)
    active_workspaces = models.IntegerField(default=0)
    workspaces_with_errors = models.IntegerField(default=0)

    # Operation Metrics (24h rolling window)
    operations_24h = models.IntegerField(default=0)
    successful_operations_24h = models.IntegerField(default=0)
    failed_operations_24h = models.IntegerField(default=0)
    success_rate_24h = models.FloatField(default=100.0)

    # File Operation Breakdown (24h)
    files_created_24h = models.IntegerField(default=0)
    files_modified_24h = models.IntegerField(default=0)
    files_deleted_24h = models.IntegerField(default=0)
    commands_executed_24h = models.IntegerField(default=0)
    git_operations_24h = models.IntegerField(default=0)

    # Activity Metrics
    bytes_written_24h = models.BigIntegerField(default=0)
    lines_changed_24h = models.IntegerField(default=0)
    avg_operation_time_ms = models.FloatField(default=0)

    # Healing/Rollback Metrics
    rollbacks_available = models.IntegerField(default=0)
    rollbacks_performed_24h = models.IntegerField(default=0)
    pending_reviews = models.IntegerField(default=0)

    # Agent Activity
    active_agents = models.IntegerField(default=0)
    most_active_agent = models.CharField(max_length=100, blank=True)
    agent_operation_counts = models.JSONField(default=dict)

    # Issues
    recent_errors = models.JSONField(default=list)
    permission_denials = models.IntegerField(default=0)

    # Check Metadata
    check_duration_ms = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_skin_pulses'
        ordering = ['-recorded_at']
        verbose_name = 'Skin Pulse'
        verbose_name_plural = 'Skin Pulses'
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['status', '-recorded_at']),
        ]

    def __str__(self):
        return f"SkinPulse {self.status} ({self.health_score}%) @ {self.recorded_at}"


class SkinStatus(models.Model):
    """
    Current SKIN system status - cached state for quick access.
    Singleton-style model (only one row expected).
    """

    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('active', 'Active'),
        ('sweating', 'Sweating'),
        ('irritated', 'Irritated'),
        ('damaged', 'Damaged'),
        ('healing', 'Healing'),
        ('dormant', 'Dormant'),
    ]

    # Identity (singleton pattern - use id=1)
    id = models.IntegerField(primary_key=True, default=1)

    # Current Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='healthy'
    )
    is_healthy = models.BooleanField(default=True)
    health_score = models.FloatField(default=100.0)

    # Current Workspace State
    total_workspaces = models.IntegerField(default=0)
    active_workspaces = models.IntegerField(default=0)
    total_files_tracked = models.IntegerField(default=0)
    total_operations_all_time = models.IntegerField(default=0)

    # 24h Rolling Metrics
    operations_24h = models.IntegerField(default=0)
    success_rate_24h = models.FloatField(default=100.0)
    files_touched_24h = models.IntegerField(default=0)
    bytes_written_24h = models.BigIntegerField(default=0)

    # Activity Level
    activity_level = models.CharField(
        max_length=20,
        default='normal',
        help_text="dormant, low, normal, high, intense"
    )
    operations_per_hour = models.FloatField(default=0)

    # Health Indicators
    error_rate_24h = models.FloatField(default=0)
    avg_operation_time_ms = models.FloatField(default=0)
    rollbacks_available = models.IntegerField(default=0)
    pending_reviews = models.IntegerField(default=0)

    # Last Activity
    last_operation_at = models.DateTimeField(null=True, blank=True)
    last_successful_operation_at = models.DateTimeField(null=True, blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    last_check = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_skin_status'
        verbose_name = 'Skin Status'
        verbose_name_plural = 'Skin Status'

    def __str__(self):
        return f"SkinStatus: {self.status} ({self.health_score}%)"

    @classmethod
    def get_current(cls):
        """Get or create the singleton status record."""
        status, _ = cls.objects.get_or_create(id=1)
        return status
