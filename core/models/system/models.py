"""
System models for platform infrastructure
"""

from django.db import models
from ..base.models import UnifiedBaseModel


class SystemConfiguration(UnifiedBaseModel):
    """
    System-wide configuration settings.

    Stores configuration that affects the entire platform,
    including feature flags, API limits, and cross-system settings.
    """

    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Configuration key (e.g., 'max_concurrent_agents')"
    )

    value = models.JSONField(
        help_text="Configuration value (can be any JSON-serializable type)"
    )

    description = models.TextField(
        blank=True,
        help_text="Human-readable description of this configuration"
    )

    category = models.CharField(
        max_length=50,
        choices=[
            ('agents', 'Agent Orchestration'),
            ('sports', 'Sports Analytics'),
            ('content', 'Content Generation'),
            ('ai_services', 'AI Services'),
            ('system', 'System Settings'),
            ('security', 'Security Settings'),
            ('performance', 'Performance Tuning'),
        ],
        default='system'
    )

    is_sensitive = models.BooleanField(
        default=False,
        help_text="Whether this configuration contains sensitive data"
    )

    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.category}.{self.key}"

    @classmethod
    def get_config(cls, key, default=None):
        """Get a configuration value by key."""
        try:
            config = cls.objects.get(key=key, is_active=True)
            return config.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_config(cls, key, value, description="", category="system"):
        """Set a configuration value."""
        config, created = cls.objects.update_or_create(
            key=key,
            defaults={
                'value': value,
                'description': description,
                'category': category,
                'is_active': True
            }
        )
        return config


class PlatformMetrics(UnifiedBaseModel):
    """
    Platform-wide metrics and analytics.

    Stores metrics about system performance, usage, and health
    across all subsystems for monitoring and optimization.
    """

    metric_name = models.CharField(
        max_length=100,
        help_text="Name of the metric (e.g., 'active_agents', 'api_calls_per_hour')"
    )

    metric_value = models.FloatField(
        help_text="Numeric value of the metric"
    )

    metric_type = models.CharField(
        max_length=20,
        choices=[
            ('counter', 'Counter (cumulative)'),
            ('gauge', 'Gauge (point-in-time)'),
            ('histogram', 'Histogram (distribution)'),
            ('timer', 'Timer (duration)'),
        ],
        default='gauge'
    )

    subsystem = models.CharField(
        max_length=50,
        choices=[
            ('agents', 'Agent Orchestration'),
            ('sports', 'Sports Analytics'),
            ('content', 'Content Generation'),
            ('ai_services', 'AI Services'),
            ('gateway', 'API Gateway'),
            ('realtime', 'Real-time Systems'),
            ('system', 'System-wide'),
        ],
        default='system'
    )

    labels = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional labels/dimensions for the metric"
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When this metric was recorded"
    )

    class Meta:
        verbose_name = "Platform Metric"
        verbose_name_plural = "Platform Metrics"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_name', '-timestamp']),
            models.Index(fields=['subsystem', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.subsystem}.{self.metric_name}: {self.metric_value}"

    @classmethod
    def record_metric(cls, name, value, metric_type='gauge', subsystem='system', labels=None):
        """Record a new metric value."""
        return cls.objects.create(
            metric_name=name,
            metric_value=value,
            metric_type=metric_type,
            subsystem=subsystem,
            labels=labels or {}
        )


class ErrorPattern(models.Model):
    """Store error patterns and their solutions for agent learning"""

    error_type = models.CharField(max_length=100)  # NameError, SyntaxError, ImportError, etc.
    error_message_pattern = models.TextField()  # Regex pattern to match error messages
    file_extension = models.CharField(max_length=10, default='.py')  # .py, .js, .html, etc.
    project_type = models.CharField(max_length=50, blank=True)  # ecommerce, trading_bot, etc.

    # Solution strategy
    solution_strategy = models.CharField(max_length=50)  # 'add_import', 'fix_syntax', 'add_attribute', etc.
    solution_template = models.TextField()  # Template for the fix
    confidence_score = models.FloatField(default=0.5)  # How confident we are in this solution

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usage_count = models.IntegerField(default=0)  # How many times this pattern was used
    success_rate = models.FloatField(default=0.0)  # Success rate of this pattern

    class Meta:
        unique_together = ['error_type', 'error_message_pattern', 'file_extension']
        ordering = ['-confidence_score', '-success_rate']
        verbose_name = "Error Pattern"
        verbose_name_plural = "Error Patterns"

    def __str__(self):
        return f"{self.error_type}: {self.solution_strategy} ({self.confidence_score:.1%})"


class ErrorInstance(models.Model):
    """Store individual error instances and their resolutions"""

    project_name = models.CharField(max_length=100)
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()

    # Error details
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
    error_line_number = models.IntegerField(null=True, blank=True)
    error_context = models.TextField(blank=True)  # Code context around the error

    # Original problematic code
    original_code = models.TextField()

    # Solution applied
    solution_applied = models.TextField()
    fixed_code = models.TextField()
    fix_method = models.CharField(max_length=50)  # 'agent_handler', 'gpt4o_mini', 'manual'

    # Resolution status
    was_successful = models.BooleanField(default=False)
    attempts_count = models.IntegerField(default=1)
    resolution_time_seconds = models.FloatField(null=True, blank=True)

    # Learning metadata
    pattern_used = models.ForeignKey(ErrorPattern, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Error Instance"
        verbose_name_plural = "Error Instances"

    def __str__(self):
        return f"{self.project_name}: {self.error_type} ({'✅' if self.was_successful else '❌'})"