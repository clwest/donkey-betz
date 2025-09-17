"""
Core models for the Unified Donkey Betz Platform

These models provide the foundation for the unified mega-platform,
including base classes that will be inherited by all other apps.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
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


class UserProfile(models.Model):
    """
    Extended user profile information for persistent storage.
    """
    ACCOUNT_TYPES = [
        ('free', 'Free'),
        ('pro', 'Professional'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    CONTENT_TONES = [
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('academic', 'Academic'),
        ('creative', 'Creative'),
        ('technical', 'Technical'),
    ]
    
    AI_MODELS = [
        ('gpt-5', 'GPT-5'),
        ('gpt-5-mini', 'GPT-5 Mini'),
        ('gpt-5-nano', 'GPT-5 Nano'),
        ('gpt-4', 'GPT-4'),
        ('claude-3-sonnet', 'Claude 3 Sonnet'),
    ]
    
    # Link to user
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='userprofile')
    
    # Profile information
    avatar = models.URLField(max_length=500, blank=True, null=True)
    avatar_file = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    display_name = models.CharField(max_length=100, blank=True, default='')
    occupation = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    
    # Preferences
    preferred_ai_model = models.CharField(max_length=20, default='gpt-5-mini')
    default_content_tone = models.CharField(max_length=20, default='professional')
    auto_save = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    default_citation_style = models.CharField(max_length=10, default='APA')
    preferred_book_length = models.CharField(max_length=10, default='medium')
    research_topics = ArrayField(
        models.CharField(max_length=100), 
        default=list, 
        blank=True
    )
    
    # Account information
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='premium')
    credits_remaining = models.IntegerField(default=10000)
    storage_used_mb = models.FloatField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_avatar_url(self):
        """Get the avatar URL, with fallback to default."""
        if self.avatar_file:
            # avatar_file is an ImageField, so use its url property if available
            try:
                url = self.avatar_file.url
                # Ensure it's an absolute URL for frontend compatibility
                if url and not url.startswith('http'):
                    return f"http://localhost:8000{url}"
                return url
            except:
                # Fallback if file doesn't exist
                return f"http://localhost:8000/media/{self.avatar_file}"
        elif self.avatar:
            # If avatar is already set (could be external URL or local)
            if self.avatar and not self.avatar.startswith('http'):
                return f"http://localhost:8000{self.avatar}"
            return self.avatar
        else:
            # Default avatar
            return f"https://api.dicebear.com/7.x/avataaars/svg?seed={self.user.username}"
    
    def get_display_name(self):
        """Get display name or fallback to full name or username."""
        if self.display_name:
            return self.display_name
        elif self.user.first_name or self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        else:
            return self.user.username


class UserStatistics(models.Model):
    """
    User content generation statistics for tracking.
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='userstatistics')
    
    # Content counts
    total_contents = models.IntegerField(default=0)
    total_images = models.IntegerField(default=0)
    total_videos = models.IntegerField(default=0)
    total_blogs = models.IntegerField(default=0)
    total_social_posts = models.IntegerField(default=0)
    total_ebooks = models.IntegerField(default=0)
    total_research_docs = models.IntegerField(default=0)
    total_campaigns = models.IntegerField(default=0)
    
    # Usage statistics
    total_ai_requests = models.IntegerField(default=0)
    total_tokens_used = models.BigIntegerField(default=0)
    total_exports = models.IntegerField(default=0)
    
    # Preferences
    favorite_style = models.CharField(max_length=50, blank=True, default='')
    
    # Activity tracking
    last_7_days_activity = models.IntegerField(default=0)
    last_30_days_activity = models.IntegerField(default=0)
    
    # Storage
    images_storage_mb = models.FloatField(default=0)
    videos_storage_mb = models.FloatField(default=0)
    documents_storage_mb = models.FloatField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_userstatistics'
        verbose_name = 'User Statistics'
        verbose_name_plural = 'User Statistics'
    
    def __str__(self):
        return f"{self.user.username}'s statistics"
    
    def get_total_storage_mb(self):
        """Calculate total storage used."""
        return self.images_storage_mb + self.videos_storage_mb + self.documents_storage_mb


# Signal handlers to create profile and statistics when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=get_user_model())
def create_user_profile_and_stats(sender, instance, created, **kwargs):
    """Create UserProfile and UserStatistics when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)
        UserStatistics.objects.create(user=instance)
    else:
        # Ensure profile and stats exist for existing users
        UserProfile.objects.get_or_create(user=instance)
        UserStatistics.objects.get_or_create(user=instance)


class ChatConversation(models.Model):
    """
    Model for storing chat conversations separately from document embeddings
    Fixes the confusion between chat memory and RAG document embeddings
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    conversation_id = models.CharField(max_length=255, db_index=True)
    user_message = models.TextField()
    assistant_response = models.TextField()

    # Context and metadata
    context_used = models.JSONField(default=dict)  # RAG context if any
    metadata = models.JSONField(default=dict)

    # Performance metrics
    response_time_ms = models.IntegerField(null=True, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    provider_used = models.CharField(max_length=50, blank=True)

    # Agent execution info
    agents_used = models.JSONField(default=list)
    agent_results = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_conversations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['conversation_id']),
        ]
        verbose_name = 'Chat Conversation'
        verbose_name_plural = 'Chat Conversations'

    def __str__(self):
        return f"{self.user.username}: {self.user_message[:50]}..."