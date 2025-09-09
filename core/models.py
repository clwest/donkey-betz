"""
Core models for the Unified Donkey Betz Platform

These models provide the foundation for the unified mega-platform,
including base classes that will be inherited by all other apps.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.serializers.json import DjangoJSONEncoder
import json


class UnifiedBaseModel(models.Model):
    """
    Universal base model for all entities in the platform.
    
    Provides common fields and functionality that every model should have:
    - UUID primary key for better distributed system support
    - Timestamps for audit trails
    - JSON metadata field for extensibility
    - Version tracking for optimistic locking
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Universal unique identifier"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible metadata storage for extensibility"
    )
    
    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number for optimistic locking"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this record is active/enabled"
    )
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        """Override save to increment version on updates."""
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)
        
    def get_metadata(self, key, default=None):
        """Get a value from the metadata JSON field."""
        return self.metadata.get(key, default)
        
    def set_metadata(self, key, value):
        """Set a value in the metadata JSON field."""
        self.metadata[key] = value
        
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'id': str(self.id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.metadata,
            'version': self.version,
            'is_active': self.is_active,
        }


class UnifiedUser(AbstractUser):
    """
    Extended user model for the unified platform.
    
    Extends Django's AbstractUser with platform-specific fields
    for managing users across all subsystems (Sports, Content, Agents).
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Platform-specific fields
    platform_role = models.CharField(
        max_length=50,
        choices=[
            ('admin', 'Platform Administrator'),
            ('sports_analyst', 'Sports Analytics User'),
            ('content_creator', 'Content Generation User'),
            ('agent_manager', 'Agent Orchestration Manager'),
            ('unified_user', 'Full Platform Access'),
        ],
        default='unified_user',
        help_text="Primary role/access level on the platform"
    )
    
    # Subscription and billing
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free Tier'),
            ('pro', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='free'
    )
    
    # API and usage tracking
    api_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text="API key for programmatic access"
    )
    
    monthly_api_calls = models.PositiveIntegerField(
        default=0,
        help_text="API calls made this month"
    )
    
    api_call_limit = models.PositiveIntegerField(
        default=1000,
        help_text="Monthly API call limit"
    )
    
    # Cross-system preferences
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences across all platform systems"
    )
    
    # Timestamps using the base model pattern
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_preference(self, key, default=None):
        """Get a user preference value."""
        return self.preferences.get(key, default)
        
    def set_preference(self, key, value):
        """Set a user preference value."""
        self.preferences[key] = value
        self.save(update_fields=['preferences'])
        
    def can_make_api_call(self):
        """Check if user can make another API call this month."""
        return self.monthly_api_calls < self.api_call_limit
        
    def increment_api_calls(self):
        """Increment monthly API call counter."""
        self.monthly_api_calls += 1
        self.save(update_fields=['monthly_api_calls'])
        
    def reset_monthly_usage(self):
        """Reset monthly usage counters (called by scheduled task)."""
        self.monthly_api_calls = 0
        self.save(update_fields=['monthly_api_calls'])


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