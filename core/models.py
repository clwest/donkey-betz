"""
Core models for the Unified Donkey Betz Platform

These models provide the foundation for the unified mega-platform,
including base classes that will be inherited by all other apps.
"""

# Import unified system models
from .models_unified_system import *

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator, MaxValueValidator
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
        ('gpt-5-mini', 'GPT-4'),
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
    
    # Professional information
    skills = models.JSONField(default=list, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    current_role = models.CharField(max_length=200, blank=True, default='')
    industries = models.JSONField(default=list, blank=True, null=True)
    portfolio_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    resume_id = models.CharField(max_length=100, blank=True, null=True)

    # Job preferences
    remote_only = models.BooleanField(default=True)
    contract_work = models.BooleanField(default=True)
    full_time = models.BooleanField(default=True)
    hourly_rate_min = models.IntegerField(default=50)
    salary_min = models.IntegerField(default=50000)

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


class UserPreferences(models.Model):
    """
    User AI preferences and configuration settings
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='ai_preferences')

    # AI Configuration
    default_model = models.CharField(max_length=50, default='gpt-5')
    reasoning_level = models.CharField(max_length=20, default='medium')
    automation_level = models.CharField(max_length=20, default='semi-auto')
    daily_token_limit = models.IntegerField(default=100000)
    monthly_spending_limit = models.FloatField(default=500.0)
    memory_retention_days = models.IntegerField(default=30)
    share_memory_across_agents = models.BooleanField(default=True)

    # Assigned agents
    assigned_agents = models.JSONField(default=list, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_userpreferences'
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"{self.user.username}'s preferences"


class ConversationMemory(models.Model):
    """
    Store conversation history for personalization
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='conversation_memories')
    message = models.TextField()
    response = models.TextField()
    agents_used = models.JSONField(default=list)
    intent = models.CharField(max_length=100, blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_conversation_memory'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


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
    """Create UserProfile, ExtendedUserProfile, and UserStatistics when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)
        UserStatistics.objects.create(user=instance)
        ExtendedUserProfile.objects.create(user=instance)
    else:
        # Ensure profile and stats exist for existing users
        UserProfile.objects.get_or_create(user=instance)
        UserStatistics.objects.get_or_create(user=instance)
        ExtendedUserProfile.objects.get_or_create(user=instance)


class ExtendedUserProfile(UnifiedBaseModel):
    """
    Extended user profile with professional information for job applications.

    This model extends the basic UserProfile with detailed career information,
    skills, work history, and job preferences needed for AI workforce automation.
    """
    REMOTE_PREFERENCES = [
        ('remote', 'Remote Only'),
        ('hybrid', 'Hybrid (Remote + Office)'),
        ('onsite', 'On-site Only'),
        ('no_preference', 'No Preference'),
    ]

    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level (0-2 years)'),
        ('junior', 'Junior (2-4 years)'),
        ('mid', 'Mid Level (4-7 years)'),
        ('senior', 'Senior (7-10 years)'),
        ('lead', 'Lead/Principal (10+ years)'),
        ('executive', 'Executive (C-Level)'),
    ]

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='extended_profile'
    )

    # Personal Information
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    timezone = models.CharField(max_length=50, blank=True)

    # Professional Profile
    current_title = models.CharField(max_length=200, blank=True)
    years_experience = models.IntegerField(default=0)
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVELS,
        default='entry'
    )
    desired_salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    desired_salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Skills & Certifications (JSON fields for flexibility)
    skills = models.JSONField(
        default=list,
        help_text="List of skills with proficiency levels: [{'name': 'Python', 'proficiency': 'Expert', 'years': 5}]"
    )
    certifications = models.JSONField(
        default=list,
        help_text="List of certifications: [{'name': 'AWS Certified', 'issued_by': 'Amazon', 'date': '2023-01-01'}]"
    )

    # Work History & Education
    work_history = models.JSONField(
        default=list,
        help_text="Work experience entries with company, role, dates, responsibilities"
    )
    education = models.JSONField(
        default=list,
        help_text="Education entries with degree, institution, graduation year"
    )

    # Documents
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        help_text="Primary resume file"
    )
    portfolio_url = models.URLField(blank=True)
    cover_letters = models.JSONField(
        default=dict,
        help_text="Cover letter templates by industry/role type"
    )

    # Platform Credentials for Job Applications
    linkedin_url = models.URLField(blank=True)
    indeed_profile = models.CharField(max_length=200, blank=True)
    github_username = models.CharField(max_length=100, blank=True)

    # Job Preferences
    job_preferences = models.JSONField(
        default=dict,
        help_text="Job search preferences including industries, role types, company sizes"
    )
    remote_preference = models.CharField(
        max_length=20,
        choices=REMOTE_PREFERENCES,
        default='no_preference'
    )
    willing_to_relocate = models.BooleanField(default=False)

    # Profile Completion Tracking
    profile_completeness = models.FloatField(
        default=0.0,
        help_text="Percentage of profile completion (0-100)"
    )

    def calculate_profile_completeness(self):
        """Calculate and update profile completion percentage."""
        required_fields = [
            'full_name', 'phone', 'location', 'current_title',
            'years_experience', 'skills', 'work_history', 'resume'
        ]

        completed_fields = 0
        total_fields = len(required_fields)

        for field in required_fields:
            value = getattr(self, field)
            if value:  # Check if field has a value
                if isinstance(value, list) and len(value) > 0:
                    completed_fields += 1
                elif isinstance(value, str) and value.strip():
                    completed_fields += 1
                elif isinstance(value, (int, float)) and value > 0:
                    completed_fields += 1
                elif hasattr(value, 'name'):  # File field
                    completed_fields += 1

        self.profile_completeness = (completed_fields / total_fields) * 100
        return self.profile_completeness

    def get_skills_list(self):
        """Get list of skill names for easy access."""
        return [skill.get('name', '') for skill in self.skills if skill.get('name')]

    def get_top_skills(self, limit=5):
        """Get top skills by proficiency for display."""
        sorted_skills = sorted(
            self.skills,
            key=lambda x: x.get('years', 0),
            reverse=True
        )
        return sorted_skills[:limit]

    class Meta:
        verbose_name = "Extended User Profile"
        verbose_name_plural = "Extended User Profiles"

    def __str__(self):
        return f"{self.user.username}'s extended profile ({self.profile_completeness:.1f}% complete)"


class JobApplication(UnifiedBaseModel):
    """
    Track all job applications made through the platform.

    This model stores comprehensive information about each job application,
    including status tracking, employer responses, and success metrics.
    """
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('viewed', 'Application Viewed'),
        ('screening', 'Initial Screening'),
        ('phone_interview', 'Phone Interview'),
        ('technical_interview', 'Technical Interview'),
        ('final_interview', 'Final Interview'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    APPLICATION_METHODS = [
        ('quick_apply', 'Quick Apply (AI-Generated)'),
        ('manual', 'Manual Application'),
        ('agent_automated', 'Agent Automated'),
        ('bulk_apply', 'Bulk Application'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Job Information
    job_id = models.CharField(max_length=200, help_text="External job posting ID")
    platform = models.CharField(max_length=50, help_text="Job platform (LinkedIn, Indeed, etc.)")
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    job_url = models.URLField(blank=True)

    # Application Details
    applied_date = models.DateTimeField(auto_now_add=True)
    application_method = models.CharField(
        max_length=20,
        choices=APPLICATION_METHODS,
        default='quick_apply'
    )
    resume_version = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which resume version was used"
    )
    cover_letter_used = models.TextField(blank=True)

    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )
    last_status_update = models.DateTimeField(auto_now=True)

    # Response Tracking
    employer_response = models.TextField(blank=True)
    interview_dates = models.JSONField(
        default=list,
        help_text="List of interview dates and types"
    )
    notes = models.TextField(blank=True)

    # Success Metrics
    response_time_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Days from application to first response"
    )
    match_score = models.FloatField(
        default=0.0,
        help_text="AI-calculated fit score (0-100)"
    )

    # Salary Information
    salary_offered = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    salary_negotiated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    def calculate_response_time(self):
        """Calculate response time if we have employer response."""
        if self.employer_response and self.status != 'applied':
            delta = self.last_status_update - self.applied_date
            self.response_time_days = delta.days
            return self.response_time_days
        return None

    def is_successful(self):
        """Check if application was successful."""
        return self.status in ['offer_received', 'offer_accepted']

    def is_in_progress(self):
        """Check if application is still in progress."""
        return self.status in [
            'applied', 'viewed', 'screening',
            'phone_interview', 'technical_interview', 'final_interview'
        ]

    def save(self, *args, **kwargs):
        """
        Save and trigger learning loops based on application status

        LEARNING LOOP: Update agent learning and user embeddings on outcomes
        """
        # Track if status changed
        status_changed = False
        old_status = None

        if self.pk:
            try:
                old_instance = JobApplication.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    status_changed = True
                    old_status = old_instance.status
            except JobApplication.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Trigger learning loops on status changes
        if status_changed or not self.pk:
            self._update_learning_from_status()

    def _update_learning_from_status(self):
        """
        LEARNING LOOP: Update UserAgentLearning and UserEmbedding based on application status
        """
        try:
            # Import here to avoid circular imports
            from django.utils import timezone

            # Success states - update with positive learning
            if self.status in ['offer_received', 'offer_accepted']:
                self._create_success_learning()
                self._create_success_embedding()

            # Failure states - update with negative learning
            elif self.status == 'rejected':
                self._create_failure_learning()

            # Progress states - update engagement metrics
            elif self.status in ['phone_interview', 'technical_interview', 'final_interview']:
                self._update_engagement_learning()

        except Exception as e:
            # Don't fail the save if learning update fails
            import logging
            logging.error(f"Failed to update job application learning: {e}", exc_info=True)

    def _create_success_learning(self):
        """Create/update learning from successful application"""
        learning, created = UserAgentLearning.objects.get_or_create(
            user=self.user,
            agent_name='JobMatcherAgent',
            learning_domain='opportunity_matching',
            defaults={
                'learning_content': {},
                'confidence_score': 0.5,
                'learning_source': 'success_pattern'
            }
        )

        # Track successful companies
        if 'successful_companies' not in learning.learning_content:
            learning.learning_content['successful_companies'] = []
        learning.learning_content['successful_companies'].append({
            'company': self.company,
            'position': self.position,
            'platform': self.platform,
            'match_score': self.match_score,
            'timestamp': timezone.now().isoformat()
        })

        # Track successful platforms
        if 'platform_success_rate' not in learning.learning_content:
            learning.learning_content['platform_success_rate'] = {}

        platform_data = learning.learning_content['platform_success_rate'].get(self.platform, {'success': 0, 'total': 0})
        platform_data['success'] += 1
        platform_data['total'] += 1
        learning.learning_content['platform_success_rate'][self.platform] = platform_data

        # Record success and update metrics
        learning.record_success()
        learning.last_interaction = timezone.now()
        learning.save()

    def _create_success_embedding(self):
        """Create embedding for similarity-based job matching"""
        try:
            # Create a content string that represents successful pattern
            content = f"{self.position} at {self.company} - {self.platform}"

            # For now, create a placeholder embedding
            # TODO: Integrate with actual embedding service when available
            embedding_vector = self._generate_placeholder_embedding(content)

            UserEmbedding.objects.create(
                user=self.user,
                content=content,
                content_type='successful_application',
                embedding_vector=embedding_vector,
                confidence_score=self.match_score / 100.0 if self.match_score else 0.5,
                source_application=self,
                source_metadata={
                    'company': self.company,
                    'position': self.position,
                    'platform': self.platform,
                    'salary_offered': float(self.salary_offered) if self.salary_offered else None,
                    'application_date': self.applied_date.isoformat()
                }
            )
        except Exception as e:
            import logging
            logging.error(f"Failed to create success embedding: {e}")

    def _create_failure_learning(self):
        """Create/update learning from rejected application"""
        learning, created = UserAgentLearning.objects.get_or_create(
            user=self.user,
            agent_name='JobMatcherAgent',
            learning_domain='opportunity_matching',
            defaults={
                'learning_content': {},
                'confidence_score': 0.5,
                'learning_source': 'failure_analysis'
            }
        )

        # Track rejected companies/positions
        if 'rejected_patterns' not in learning.learning_content:
            learning.learning_content['rejected_patterns'] = []

        learning.learning_content['rejected_patterns'].append({
            'company': self.company,
            'position': self.position,
            'platform': self.platform,
            'match_score': self.match_score,
            'timestamp': timezone.now().isoformat()
        })

        # Record failure to adjust confidence
        learning.record_failure()
        learning.last_interaction = timezone.now()
        learning.save()

    def _update_engagement_learning(self):
        """Track interview progression as positive signal"""
        learning, created = UserAgentLearning.objects.get_or_create(
            user=self.user,
            agent_name='JobMatcherAgent',
            learning_domain='opportunity_matching',
            defaults={
                'learning_content': {},
                'confidence_score': 0.5,
                'learning_source': 'performance_tracking'
            }
        )

        # Track companies that lead to interviews
        if 'interview_progression' not in learning.learning_content:
            learning.learning_content['interview_progression'] = []

        learning.learning_content['interview_progression'].append({
            'company': self.company,
            'position': self.position,
            'stage': self.status,
            'timestamp': timezone.now().isoformat()
        })

        learning.save()

    def _generate_placeholder_embedding(self, content):
        """
        Generate a simple placeholder embedding
        TODO: Replace with actual embedding service integration
        """
        import hashlib
        # Create a deterministic but distributed vector based on content
        hash_obj = hashlib.sha256(content.encode())
        hash_bytes = hash_obj.digest()

        # Convert to list of floats normalized to [-1, 1]
        embedding = []
        for i in range(min(128, len(hash_bytes))):
            # Normalize byte value (0-255) to (-1, 1)
            embedding.append((hash_bytes[i] / 127.5) - 1.0)

        # Pad to 128 dimensions if needed
        while len(embedding) < 128:
            embedding.append(0.0)

        return embedding[:128]

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-applied_date']
        indexes = [
            models.Index(fields=['user', '-applied_date']),
            models.Index(fields=['status', '-applied_date']),
            models.Index(fields=['platform', '-applied_date']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.position} at {self.company} ({self.status})"


class UserEmbedding(UnifiedBaseModel):
    """
    Store user-specific knowledge embeddings for personalized AI responses.

    This model creates a learning loop where the system stores and learns
    from user interactions, preferences, and successful patterns.
    """
    CONTENT_TYPES = [
        ('successful_application', 'Successful Application Pattern'),
        ('rejected_application', 'Rejected Application Analysis'),
        ('interview_notes', 'Interview Experience'),
        ('skill_validation', 'Skill Validation Data'),
        ('preference_update', 'User Preference Change'),
        ('success_pattern', 'General Success Pattern'),
        ('failure_pattern', 'Failure Pattern Analysis'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Embedding Data
    embedding_vector = models.JSONField(
        help_text="Vector representation for similarity search"
    )
    content = models.TextField(help_text="Original content that was embedded")
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPES)

    # Metadata
    confidence_score = models.FloatField(
        default=0.5,
        help_text="Confidence in this embedding (0-1)"
    )
    usage_count = models.IntegerField(
        default=0,
        help_text="How many times this embedding has been used"
    )
    last_used = models.DateTimeField(null=True, blank=True)

    # Source Information
    source_application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Associated job application if applicable"
    )
    source_metadata = models.JSONField(
        default=dict,
        help_text="Additional source information"
    )

    def increment_usage(self):
        """Increment usage counter and update last used."""
        from django.utils import timezone
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])

    def update_confidence(self, feedback_score):
        """Update confidence based on feedback."""
        # Simple confidence update algorithm
        self.confidence_score = (self.confidence_score + feedback_score) / 2
        self.save(update_fields=['confidence_score'])

    class Meta:
        verbose_name = "User Embedding"
        verbose_name_plural = "User Embeddings"
        indexes = [
            models.Index(fields=['user', 'content_type']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['-last_used']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.content_type} (confidence: {self.confidence_score:.2f})"


class ResumeVersion(UnifiedBaseModel):
    """
    Store different versions of user resumes for different job types.

    Users can have multiple resume versions optimized for different industries,
    roles, or application strategies.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Version Information
    version_name = models.CharField(
        max_length=100,
        help_text="Name for this resume version (e.g., 'Software Engineer', 'Data Scientist')"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary/default resume"
    )

    # File and Content
    resume_file = models.FileField(upload_to='resumes/versions/')
    resume_text = models.TextField(
        blank=True,
        help_text="Extracted text content of the resume"
    )

    # Optimization Data
    target_industries = models.JSONField(
        default=list,
        help_text="Industries this resume is optimized for"
    )
    target_roles = models.JSONField(
        default=list,
        help_text="Role types this resume is optimized for"
    )
    keywords = models.JSONField(
        default=list,
        help_text="Keywords included in this resume version"
    )

    # Usage Statistics
    times_used = models.IntegerField(default=0)
    success_rate = models.FloatField(
        default=0.0,
        help_text="Success rate when using this resume (0-100)"
    )

    def calculate_success_rate(self):
        """Calculate success rate based on applications using this resume."""
        applications = JobApplication.objects.filter(
            user=self.user,
            resume_version=self.version_name
        )

        if applications.count() == 0:
            return 0.0

        successful = applications.filter(
            status__in=['offer_received', 'offer_accepted']
        ).count()

        self.success_rate = (successful / applications.count()) * 100
        return self.success_rate

    def increment_usage(self):
        """Increment usage counter."""
        self.times_used += 1
        self.save(update_fields=['times_used'])

    class Meta:
        verbose_name = "Resume Version"
        verbose_name_plural = "Resume Versions"
        unique_together = ['user', 'version_name']
        ordering = ['-is_primary', '-updated_at']

    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.user.username}: {self.version_name}{primary}"


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


class EnhancedUserProfile(models.Model):
    """
    Comprehensive user profile for deep personalization and memory retrieval.
    """

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='enhanced_profile')

    # ========== 1. KEY ROLES & LONG-TERM GOALS ==========
    primary_role = models.CharField(
        max_length=200,
        help_text="Primary professional role (e.g., CEO, Software Engineer, PhD Student)",
        blank=True
    )
    secondary_roles = models.JSONField(
        default=list,
        help_text="Additional roles and responsibilities"
    )
    long_term_goals = models.JSONField(
        default=list,
        help_text="Major life/career goals with target dates"
    )
    current_projects = models.JSONField(
        default=list,
        help_text="Active projects with priority levels and deadlines"
    )
    quarterly_objectives = models.JSONField(
        default=dict,
        help_text="OKRs or quarterly goals"
    )

    # ========== 2. COMMUNICATION & DECISION PREFERENCES ==========
    communication_style = models.CharField(
        max_length=50,
        choices=[
            ('concise', 'Concise - Brief and to the point'),
            ('detailed', 'Detailed - Comprehensive information'),
            ('balanced', 'Balanced - Mix based on context'),
            ('visual', 'Visual - Prefer charts and diagrams'),
            ('narrative', 'Narrative - Story-based explanations')
        ],
        default='balanced'
    )

    preferred_channels = models.JSONField(
        default=dict,
        help_text="Preferred communication channels by context (e.g., {urgent: 'phone', updates: 'email'})"
    )

    optimal_meeting_times = models.JSONField(
        default=list,
        help_text="Best times for meetings/calls (e.g., ['9-11am PST', '2-4pm PST'])"
    )

    decision_framework = models.CharField(
        max_length=50,
        choices=[
            ('data_driven', 'Data-Driven - Metrics and analytics focused'),
            ('intuitive', 'Intuitive - Gut feeling and experience'),
            ('collaborative', 'Collaborative - Team consensus'),
            ('analytical', 'Analytical - Pros/cons analysis'),
            ('rapid', 'Rapid - Quick decisions, iterate later')
        ],
        default='analytical'
    )

    delegation_preferences = models.JSONField(
        default=dict,
        help_text="What to delegate vs handle personally"
    )

    # ========== 3. PERSONAL PREFERENCES & ROUTINES ==========
    work_schedule = models.JSONField(
        default=dict,
        help_text="Typical work hours by day of week"
    )

    time_zone = models.CharField(
        max_length=50,
        default='America/Los_Angeles'
    )

    morning_routine = models.TextField(
        blank=True,
        help_text="Morning routine for optimal productivity"
    )

    energy_patterns = models.JSONField(
        default=dict,
        help_text="Energy levels throughout the day (e.g., {morning: 'high', afternoon: 'medium'})"
    )

    dietary_preferences = models.JSONField(
        default=dict,
        help_text="Dietary restrictions, allergies, preferences"
    )

    travel_preferences = models.JSONField(
        default=dict,
        help_text="Travel hubs, airline preferences, hotel chains, etc."
    )

    personal_values = models.JSONField(
        default=list,
        help_text="Core personal values that guide decisions"
    )

    stress_indicators = models.JSONField(
        default=list,
        help_text="Signs of stress and preferred interventions"
    )

    # ========== 4. SKILL LEVELS & LEARNING INTERESTS ==========
    core_competencies = models.JSONField(
        default=dict,
        help_text="Skills with proficiency levels (1-10)"
    )

    learning_style = models.CharField(
        max_length=50,
        choices=[
            ('visual', 'Visual - Images, diagrams, videos'),
            ('auditory', 'Auditory - Lectures, discussions'),
            ('reading', 'Reading/Writing - Text-based'),
            ('kinesthetic', 'Kinesthetic - Hands-on practice'),
            ('mixed', 'Mixed - Combination of styles')
        ],
        default='mixed'
    )

    current_learning_goals = models.JSONField(
        default=list,
        help_text="Skills or topics currently learning"
    )

    knowledge_gaps = models.JSONField(
        default=list,
        help_text="Identified areas for improvement"
    )

    preferred_learning_resources = models.JSONField(
        default=dict,
        help_text="Favorite learning platforms, authors, courses"
    )

    certifications = models.JSONField(
        default=list,
        help_text="Professional certifications with expiry dates"
    )

    # ========== 5. PRIVACY & UPDATE SETTINGS ==========
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public - Share with all agents'),
            ('professional', 'Professional - Work-related only'),
            ('personal', 'Personal - Close assistants only'),
            ('private', 'Private - Encrypted, user only')
        ],
        default='professional'
    )

    sensitive_topics = models.JSONField(
        default=list,
        help_text="Topics to handle with extra care"
    )

    data_retention_days = models.IntegerField(
        default=90,
        validators=[
            MinValueValidator(7),
            MaxValueValidator(365)
        ],
        help_text="How long to retain interaction history"
    )

    update_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily - High-frequency updates'),
            ('weekly', 'Weekly - Regular check-ins'),
            ('biweekly', 'Bi-weekly - Every two weeks'),
            ('monthly', 'Monthly - Monthly review'),
            ('quarterly', 'Quarterly - Seasonal updates')
        ],
        default='weekly'
    )

    last_profile_review = models.DateTimeField(
        auto_now_add=True,
        help_text="Last time profile was reviewed/updated"
    )

    # ========== ORGANIZATION: STABLE VS DYNAMIC FIELDS ==========
    stable_attributes = models.JSONField(
        default=dict,
        help_text="Rarely changing attributes (personality, core values)"
    )

    dynamic_attributes = models.JSONField(
        default=dict,
        help_text="Frequently changing attributes (current mood, energy)"
    )

    # ========== METADATA & ANALYTICS ==========
    profile_completeness = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ]
    )

    interaction_count = models.IntegerField(default=0)

    memory_retrieval_stats = models.JSONField(
        default=dict,
        help_text="Statistics on which profile fields are most accessed"
    )

    ai_insights = models.JSONField(
        default=dict,
        help_text="AI-generated insights about user patterns"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Enhanced User Profile"
        verbose_name_plural = "Enhanced User Profiles"

    def calculate_completeness(self) -> float:
        """Calculate profile completeness percentage."""
        from datetime import datetime

        required_fields = [
            'primary_role', 'long_term_goals', 'communication_style',
            'work_schedule', 'core_competencies', 'learning_style'
        ]

        completed = 0
        for field in required_fields:
            value = getattr(self, field, None)
            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                completed += 1

        optional_fields = [
            'secondary_roles', 'current_projects', 'quarterly_objectives',
            'dietary_preferences', 'travel_preferences', 'certifications'
        ]

        for field in optional_fields:
            value = getattr(self, field, None)
            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                completed += 0.5

        total_possible = len(required_fields) + (len(optional_fields) * 0.5)
        self.profile_completeness = (completed / total_possible) * 100
        return self.profile_completeness

    def get_context_for_ai(self, context_type: str = 'general') -> dict:
        """
        Get relevant profile context for AI assistants based on context type.

        Args:
            context_type: Type of context needed ('general', 'work', 'personal', 'learning')

        Returns:
            Dictionary with relevant profile information
        """
        base_context = {
            'user_id': self.user_id,
            'primary_role': self.primary_role,
            'communication_style': self.communication_style,
            'decision_framework': self.decision_framework,
            'timezone': self.time_zone
        }

        if context_type == 'work':
            base_context.update({
                'current_projects': self.current_projects,
                'quarterly_objectives': self.quarterly_objectives,
                'work_schedule': self.work_schedule,
                'delegation_preferences': self.delegation_preferences,
                'optimal_meeting_times': self.optimal_meeting_times
            })

        elif context_type == 'personal':
            if self.privacy_level in ['personal', 'public']:
                base_context.update({
                    'personal_values': self.personal_values,
                    'dietary_preferences': self.dietary_preferences,
                    'travel_preferences': self.travel_preferences,
                    'energy_patterns': self.energy_patterns,
                    'stress_indicators': self.stress_indicators
                })

        elif context_type == 'learning':
            base_context.update({
                'learning_style': self.learning_style,
                'current_learning_goals': self.current_learning_goals,
                'knowledge_gaps': self.knowledge_gaps,
                'core_competencies': self.core_competencies,
                'preferred_learning_resources': self.preferred_learning_resources
            })

        else:  # general
            base_context.update({
                'long_term_goals': self.long_term_goals[:3] if self.long_term_goals else [],
                'current_projects': self.current_projects[:2] if self.current_projects else [],
                'core_competencies': list(self.core_competencies.keys())[:5] if self.core_competencies else []
            })

        return base_context

    def track_memory_access(self, field_name: str):
        """Track which fields are accessed for memory optimization."""
        if not self.memory_retrieval_stats:
            self.memory_retrieval_stats = {}

        if field_name not in self.memory_retrieval_stats:
            self.memory_retrieval_stats[field_name] = 0

        self.memory_retrieval_stats[field_name] += 1
        self.save(update_fields=['memory_retrieval_stats'])

    def should_update_profile(self) -> bool:
        """Check if profile needs updating based on frequency setting."""
        from datetime import datetime

        if not self.last_profile_review:
            return True

        days_since_update = (datetime.now().date() - self.last_profile_review.date()).days

        update_intervals = {
            'daily': 1,
            'weekly': 7,
            'biweekly': 14,
            'monthly': 30,
            'quarterly': 90
        }

        return days_since_update >= update_intervals.get(self.update_frequency, 7)

    def __str__(self):
        return f"{self.user.username} - {self.primary_role} ({self.profile_completeness:.0f}% complete)"


class UserMemoryContext(models.Model):
    """
    Contextual memory storage for user interactions.
    Links profile data with specific memories for better retrieval.
    """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='memory_contexts')
    profile = models.ForeignKey(EnhancedUserProfile, on_delete=models.CASCADE)

    memory_type = models.CharField(
        max_length=50,
        choices=[
            ('decision', 'Decision Made'),
            ('preference', 'Preference Stated'),
            ('feedback', 'Feedback Given'),
            ('instruction', 'Instruction Provided'),
            ('context', 'Context Shared'),
            ('goal', 'Goal Mentioned'),
            ('constraint', 'Constraint Identified'),
            ('interaction', 'User Interaction'),
            ('agent_action', 'Agent Action'),
            ('agent_learning', 'Agent Learning'),
            ('agent_recommendation', 'Agent Recommendation'),
            ('cross_agent', 'Cross-Agent Communication'),
            ('system_insight', 'System Insight'),
            ('agent_usage', 'Agent Usage'),
            ('skill', 'Skill Identified'),
            ('project', 'Project Information'),
            ('learning', 'System Learning'),
            ('pattern', 'Pattern Detected')
        ]
    )

    content = models.TextField()
    source = models.CharField(
        max_length=100,
        default='assistant',
        help_text="Source of memory (e.g., 'assistant', 'agent:JobMatcher')"
    )

    related_project = models.CharField(max_length=200, blank=True)
    related_goal = models.CharField(max_length=200, blank=True)

    importance = models.IntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    tags = models.JSONField(default=list)

    context_metadata = models.JSONField(
        default=dict,
        help_text="Additional context like mood, energy level, time of day"
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this memory becomes less relevant"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    accessed_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-importance', '-created_at']
        indexes = [
            models.Index(fields=['user', 'memory_type', '-created_at']),
            models.Index(fields=['user', '-importance']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.memory_type}: {self.content[:50]}..."


# ===============================================
# AGENT ERROR LEARNING MODELS
# ===============================================

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


class AgentLearningSession(models.Model):
    """Track agent learning sessions and improvements over time"""

    session_id = models.CharField(max_length=100, unique=True)
    agent_type = models.CharField(max_length=50)  # 'AgentErrorHandler', 'GPT4oMini', etc.

    # Session statistics
    total_errors_encountered = models.IntegerField(default=0)
    total_errors_fixed = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    average_resolution_time = models.FloatField(default=0.0)

    # Learning metrics
    new_patterns_learned = models.IntegerField(default=0)
    patterns_improved = models.IntegerField(default=0)
    knowledge_base_size_before = models.IntegerField(default=0)
    knowledge_base_size_after = models.IntegerField(default=0)

    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    session_duration_minutes = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-started_at']
        verbose_name = "Agent Learning Session"
        verbose_name_plural = "Agent Learning Sessions"

    def __str__(self):
        return f"{self.agent_type} - {self.session_id} ({self.success_rate:.1%})"


class AgentCollaboration(models.Model):
    """Track how different agents collaborate and learn from each other"""

    primary_agent = models.CharField(max_length=50)
    assisting_agent = models.CharField(max_length=50)
    collaboration_type = models.CharField(max_length=50)  # 'fallback', 'consultation', 'parallel'

    # Problem context
    problem_domain = models.CharField(max_length=100)  # 'code_generation', 'error_fixing', 'optimization'
    problem_complexity = models.CharField(max_length=20)  # 'simple', 'moderate', 'complex'

    # Outcome
    collaboration_successful = models.BooleanField(default=False)
    primary_agent_contribution = models.TextField(blank=True)
    assisting_agent_contribution = models.TextField(blank=True)
    final_solution = models.TextField()

    # Learning transfer
    knowledge_transferred = models.TextField(blank=True)  # What the primary agent learned
    pattern_reinforced = models.ForeignKey(ErrorPattern, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Agent Collaboration"
        verbose_name_plural = "Agent Collaborations"

    def __str__(self):
        return f"{self.primary_agent} + {self.assisting_agent}: {self.problem_domain}"


class LearningInsight(models.Model):
    """Store insights and patterns discovered by the AI system"""

    insight_type = models.CharField(max_length=50)  # 'error_pattern', 'code_pattern', 'project_pattern'
    insight_category = models.CharField(max_length=100)  # 'common_mistakes', 'best_practices', 'optimization'

    # Insight content
    title = models.CharField(max_length=200)
    description = models.TextField()
    code_example = models.TextField(blank=True)
    solution_approach = models.TextField()

    # Evidence and confidence
    supporting_instances = models.IntegerField(default=1)  # How many times this was observed
    confidence_level = models.FloatField(default=0.5)
    applicability_scope = models.JSONField(default=dict)  # Where this insight applies

    # Impact tracking
    times_applied = models.IntegerField(default=0)
    success_when_applied = models.IntegerField(default=0)
    impact_score = models.FloatField(default=0.0)

    discovered_at = models.DateTimeField(auto_now_add=True)
    last_validated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-confidence_level', '-impact_score']
        verbose_name = "Learning Insight"
        verbose_name_plural = "Learning Insights"

    def __str__(self):
        return f"{self.insight_category}: {self.title} ({self.confidence_level:.1%})"


class GeneratedProject(UnifiedBaseModel):
    """
    Stores information about AI-generated projects
    """
    name = models.CharField(max_length=255, help_text="Project name")
    project_type = models.CharField(max_length=100, help_text="Type of project (e.g., ecommerce, content_factory)")
    description = models.TextField(blank=True, help_text="Project description")
    agents_used = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="List of agent names that worked on this project"
    )
    advisors_consulted = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="List of advisors consulted for this project"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('generating', 'Generating'),
            ('completed', 'Completed'),
            ('error', 'Error'),
            ('cancelled', 'Cancelled')
        ],
        default='generating'
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='generated_projects',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'core_generated_projects'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.project_type})"


class GeneratedCode(UnifiedBaseModel):
    """
    Stores AI-generated code files with full persistence
    """
    project = models.ForeignKey(
        GeneratedProject,
        on_delete=models.CASCADE,
        related_name='code_files'
    )
    filename = models.CharField(max_length=255, help_text="Name of the file")
    file_path = models.CharField(max_length=500, help_text="Relative path from project root")
    content = models.TextField(help_text="The actual code content")
    language = models.CharField(
        max_length=50,
        choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('html', 'HTML'),
            ('css', 'CSS'),
            ('sql', 'SQL'),
            ('json', 'JSON'),
            ('yaml', 'YAML'),
            ('other', 'Other')
        ],
        default='python'
    )
    agent_creator = models.CharField(
        max_length=100,
        help_text="Name of the agent that created this code"
    )
    task_description = models.TextField(
        blank=True,
        help_text="Description of the task this code was created for"
    )
    is_latest = models.BooleanField(
        default=True,
        help_text="Whether this is the latest version of this file"
    )
    execution_status = models.CharField(
        max_length=50,
        choices=[
            ('untested', 'Untested'),
            ('success', 'Executed Successfully'),
            ('error', 'Execution Error'),
            ('timeout', 'Execution Timeout'),
            ('fixed', 'Auto-Fixed and Working')
        ],
        default='untested'
    )
    execution_output = models.TextField(
        blank=True,
        help_text="Output from code execution or error messages"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='generated_code',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'core_generated_code'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'filename']),
            models.Index(fields=['project', 'is_latest']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.filename} - {self.project.name}"

    def save(self, *args, **kwargs):
        # When saving a new version, mark others as not latest
        if self.is_latest:
            GeneratedCode.objects.filter(
                project=self.project,
                filename=self.filename
            ).exclude(id=self.id).update(is_latest=False)
        super().save(*args, **kwargs)


class Revenue(UnifiedBaseModel):
    """
    Model to track all revenue and earnings from the platform
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='revenues'
    )

    # Revenue details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Revenue amount in USD"
    )

    source = models.CharField(
        max_length=100,
        choices=[
            ('quick_apply', 'Quick Apply Job'),
            ('freelance', 'Freelance Project'),
            ('consulting', 'Consulting'),
            ('ai_project', 'AI Project'),
            ('content', 'Content Creation'),
            ('trading', 'Trading/Investment'),
            ('sports_betting', 'Sports Betting'),
            ('affiliate', 'Affiliate Commission'),
            ('other', 'Other')
        ],
        default='quick_apply'
    )

    status = models.CharField(
        max_length=50,
        choices=[
            ('potential', 'Potential'),
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('received', 'Received'),
            ('withdrawn', 'Withdrawn'),
            ('cancelled', 'Cancelled')
        ],
        default='potential'
    )

    # Related opportunity/job
    opportunity_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID of the job or opportunity"
    )
    opportunity_title = models.CharField(
        max_length=500,
        blank=True,
        help_text="Title of the job or opportunity"
    )
    company = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or client name"
    )

    # Application details
    application_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the application was submitted"
    )
    confirmation_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the revenue was confirmed"
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was received"
    )

    # Additional info
    description = models.TextField(
        blank=True,
        help_text="Additional details about this revenue"
    )

    # Tracking
    spider_source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which spider found this opportunity"
    )
    agent_involved = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which agent helped secure this revenue"
    )

    # Metrics
    match_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How well this opportunity matched user profile"
    )

    class Meta:
        db_table = 'core_revenue'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'amount']),
        ]

    def __str__(self):
        return f"${self.amount} - {self.opportunity_title} ({self.status})"

    @property
    def is_realized(self):
        """Check if revenue has been realized (not just potential)"""
        return self.status in ['confirmed', 'received', 'withdrawn']

    @classmethod
    def get_user_total(cls, user, status=None):
        """Get total revenue for a user, optionally filtered by status"""
        queryset = cls.objects.filter(user=user)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @classmethod
    def get_user_stats(cls, user):
        """Get comprehensive revenue statistics for a user"""
        return {
            'total_potential': cls.get_user_total(user, 'potential'),
            'total_pending': cls.get_user_total(user, 'pending'),
            'total_confirmed': cls.get_user_total(user, 'confirmed'),
            'total_received': cls.get_user_total(user, 'received'),
            'total_all': cls.get_user_total(user),
            'count_opportunities': cls.objects.filter(user=user).count(),
            'avg_amount': cls.objects.filter(user=user).aggregate(
                avg=models.Avg('amount')
            )['avg'] or 0
        }


class UserAgentLearning(UnifiedBaseModel):
    """
    Connects user profiles to agent learning - making agents learn FOR specific users

    This model enables personalized agent learning where agents track what works
    for each individual user, building user-specific knowledge over time.

    Example:
        For User A (software engineer):
        - Job Matcher Agent learns A prefers remote Python roles at startups
        - Content Creator Agent learns A likes technical blog style
        - Income Builder learns A's best opportunities are on HackerNews

        For User B (designer):
        - Job Matcher Agent learns B prefers agency creative director roles
        - Content Creator Agent learns B likes visual portfolio style
        - Income Builder learns B's best opportunities are on Dribbble
    """

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='agent_learnings',
        help_text="User this learning applies to"
    )

    agent_name = models.CharField(
        max_length=200,
        help_text="Name of the agent (e.g., 'JobMatcherAgent', 'IncomeBuilder')"
    )

    learning_domain = models.CharField(
        max_length=100,
        choices=[
            ('opportunity_matching', 'Job/Opportunity Matching'),
            ('content_creation', 'Content Creation Style'),
            ('communication', 'Communication Preferences'),
            ('decision_making', 'Decision Making Patterns'),
            ('skill_development', 'Skill Development Path'),
            ('revenue_optimization', 'Revenue Optimization'),
            ('platform_preferences', 'Platform Preferences'),
            ('timing_patterns', 'Optimal Timing Patterns'),
            ('success_factors', 'Success Factor Analysis'),
            ('general', 'General Learning'),
        ],
        default='general',
        help_text="What domain is this learning about"
    )

    # What the agent learned
    learning_content = models.JSONField(
        help_text="Structured learning data specific to this agent-user pair"
    )

    # How confident is the agent in this learning
    confidence_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Agent's confidence in this learning (0-1)"
    )

    # How many times this learning was validated
    validation_count = models.IntegerField(
        default=0,
        help_text="How many times this learning proved correct"
    )

    # How many times this learning failed
    failure_count = models.IntegerField(
        default=0,
        help_text="How many times this learning proved incorrect"
    )

    # Success rate calculated from validation/failure
    success_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Success rate of this learning"
    )

    # Source of this learning
    learning_source = models.CharField(
        max_length=100,
        choices=[
            ('user_feedback', 'Direct User Feedback'),
            ('success_pattern', 'Observed Success Pattern'),
            ('failure_analysis', 'Failure Analysis'),
            ('interaction_mining', 'Interaction Pattern Mining'),
            ('explicit_instruction', 'Explicit User Instruction'),
            ('performance_tracking', 'Performance Tracking'),
        ],
        default='success_pattern'
    )

    # Context when this was learned
    context_metadata = models.JSONField(
        default=dict,
        help_text="Context when learning occurred (time, situation, etc.)"
    )

    # When this learning expires (if temporary)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this learning becomes obsolete (null = never expires)"
    )

    # How many times this learning was used
    usage_count = models.IntegerField(
        default=0,
        help_text="How many times this learning influenced agent behavior"
    )

    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this learning was last applied"
    )

    class Meta:
        verbose_name = "User-Agent Learning"
        verbose_name_plural = "User-Agent Learnings"
        indexes = [
            models.Index(fields=['user', 'agent_name', 'learning_domain']),
            models.Index(fields=['user', '-confidence_score']),
            models.Index(fields=['user', '-success_rate']),
            models.Index(fields=['agent_name', '-confidence_score']),
        ]

    def __str__(self):
        return f"{self.agent_name} → {self.user.username}: {self.learning_domain} (confidence: {self.confidence_score:.1%})"

    def record_success(self):
        """Record that this learning proved correct"""
        self.validation_count += 1
        self.usage_count += 1
        self.last_used = timezone.now()
        self._update_metrics()
        self.save()

    def record_failure(self):
        """Record that this learning proved incorrect"""
        self.failure_count += 1
        self.usage_count += 1
        self.last_used = timezone.now()
        self._update_metrics()
        self.save()

    def _update_metrics(self):
        """Update confidence and success rate based on validation/failure counts"""
        total_attempts = self.validation_count + self.failure_count

        if total_attempts > 0:
            # Calculate success rate
            self.success_rate = self.validation_count / total_attempts

            # Adjust confidence based on success rate and sample size
            # More samples = more confidence in the success rate
            sample_weight = min(total_attempts / 20.0, 1.0)  # Fully confident after 20 samples

            # Confidence approaches success rate as sample size grows
            self.confidence_score = (
                self.confidence_score * (1 - sample_weight) +  # Old confidence
                self.success_rate * sample_weight  # New evidence
            )

    @classmethod
    def get_user_agent_knowledge(cls, user, agent_name, domain=None):
        """
        Get all learnings for a specific user-agent pair

        Args:
            user: User instance
            agent_name: Name of the agent
            domain: Optional domain filter

        Returns:
            QuerySet of learnings, ordered by confidence and recency
        """
        learnings = cls.objects.filter(
            user=user,
            agent_name=agent_name,
            is_active=True
        )

        if domain:
            learnings = learnings.filter(learning_domain=domain)

        # Filter out expired learnings
        from django.utils import timezone
        learnings = learnings.filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        )

        return learnings.order_by('-confidence_score', '-updated_at')

    @classmethod
    def create_learning(cls, user, agent_name, domain, content, source='success_pattern', confidence=0.5):
        """
        Create a new learning or update existing one

        Args:
            user: User instance
            agent_name: Name of the agent
            domain: Learning domain
            content: Learning content (JSON)
            source: Learning source
            confidence: Initial confidence score

        Returns:
            UserAgentLearning instance
        """
        learning, created = cls.objects.get_or_create(
            user=user,
            agent_name=agent_name,
            learning_domain=domain,
            defaults={
                'learning_content': content,
                'confidence_score': confidence,
                'learning_source': source,
                'context_metadata': {
                    'created_at': timezone.now().isoformat()
                }
            }
        )

        if not created:
            # Update existing learning
            learning.learning_content = content
            learning.confidence_score = confidence
            learning.save()

        return learningfrom core.models_engagement_metrics import EngagementMetrics, OpportunityInteraction
