"""
Base models for the Unified Donkey Betz Platform

These models provide the foundation for the unified mega-platform,
including base classes that will be inherited by all other apps.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


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
            ('reviewer', 'Read-Only Reviewer'),  # Session 998: Governance hardening
        ],
        default='unified_user',
        help_text="Primary role/access level on the platform"
    )

    # Session 1039: Multi-tenant customer access
    tenant = models.ForeignKey(
        'core.Tenant',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='members',
    )
    customer_role = models.CharField(
        max_length=20,
        choices=[
            ('viewer', 'Viewer'),
            ('user', 'User'),
            ('org_admin', 'Org Admin'),
        ],
        default='user',
        blank=True,
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

    # Discord Integration (Session 429)
    discord_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True,
        help_text="Discord user ID for account linking"
    )
    discord_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Discord username (cached for display)"
    )
    discord_linked_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When Discord account was linked"
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

    @property
    def is_reviewer(self) -> bool:
        """Session 998: Read-only reviewer role check."""
        return self.platform_role == 'reviewer'

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


class DiscordLinkCode(models.Model):
    """
    Temporary codes for linking Discord accounts to web accounts.
    Session 429: Discord User Account Linking
    """
    import secrets
    import string
    from django.utils import timezone as tz
    from datetime import timedelta

    code = models.CharField(max_length=6, unique=True)
    user = models.ForeignKey(
        UnifiedUser,
        on_delete=models.CASCADE,
        related_name='discord_link_codes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @classmethod
    def create_for_user(cls, user, expiry_minutes=10):
        """Create a new link code for a user."""
        import secrets
        import string
        from django.utils import timezone
        from datetime import timedelta

        # Delete any existing unused codes for this user
        cls.objects.filter(user=user, used=False).delete()

        # Generate unique 6-char code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        # Ensure uniqueness
        while cls.objects.filter(code=code).exists():
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        return cls.objects.create(
            code=code,
            user=user,
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes)
        )

    def __str__(self):
        return f"LinkCode {self.code} for {self.user.username}"


class DiscordServer(models.Model):
    """
    Session 431: Discord servers configured by users.

    Tracks which Discord servers belong to which users, what template
    they used, and which channels have been created.
    """

    TEMPLATE_CHOICES = [
        ('solo_creator', 'Solo Creator'),
        ('freelancer', 'Freelancer'),
        ('agency', 'Agency'),
        ('custom', 'Custom'),
    ]

    user = models.ForeignKey(
        UnifiedUser,
        on_delete=models.CASCADE,
        related_name='discord_servers'
    )

    guild_id = models.CharField(
        max_length=30,
        unique=True,
        help_text="Discord guild (server) ID"
    )

    guild_name = models.CharField(
        max_length=100,
        help_text="Discord server name"
    )

    template = models.CharField(
        max_length=20,
        choices=TEMPLATE_CHOICES,
        default='solo_creator',
        help_text="Server template used"
    )

    is_setup_complete = models.BooleanField(
        default=False,
        help_text="Whether server setup wizard is complete"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Channel IDs for quick access
    gallery_channel_id = models.CharField(max_length=30, blank=True, null=True)
    assistant_channel_id = models.CharField(max_length=30, blank=True, null=True)
    research_channel_id = models.CharField(max_length=30, blank=True, null=True)
    opportunities_channel_id = models.CharField(max_length=30, blank=True, null=True)
    notifications_channel_id = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Discord Server"
        verbose_name_plural = "Discord Servers"

    def __str__(self):
        return f"{self.guild_name} ({self.template}) - {self.user.username}"


class DiscordServerChannel(models.Model):
    """
    Session 431: Channels created in user Discord servers.

    Tracks individual channels created by the bot in user servers,
    including their purpose and any associated metadata.
    """

    CHANNEL_TYPE_CHOICES = [
        ('gallery', 'Gallery - Image deliveries'),
        ('assistant', 'Assistant - PA conversations'),
        ('research', 'Research - Spider data'),
        ('opportunities', 'Opportunities - Job alerts'),
        ('notifications', 'Notifications - System updates'),
        ('dashboard', 'Dashboard - Daily summaries'),
        ('client', 'Client - Client-specific channel'),
        ('custom', 'Custom'),
    ]

    server = models.ForeignKey(
        DiscordServer,
        on_delete=models.CASCADE,
        related_name='channels'
    )

    channel_id = models.CharField(
        max_length=30,
        unique=True,
        help_text="Discord channel ID"
    )

    channel_name = models.CharField(
        max_length=100,
        help_text="Channel name"
    )

    channel_type = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPE_CHOICES,
        help_text="Purpose of this channel"
    )

    # For client channels
    client_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Client name (for client-type channels)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['channel_type', 'channel_name']

    def __str__(self):
        return f"#{self.channel_name} ({self.channel_type}) in {self.server.guild_name}"


# Server template definitions
DISCORD_SERVER_TEMPLATES = {
    'solo_creator': {
        'name': 'Solo Creator',
        'description': 'Personal workspace for individual creators',
        'categories': [
            {
                'name': 'AI STUDIO',
                'channels': [
                    {'name': 'creations', 'type': 'gallery'},
                    {'name': 'research', 'type': 'research'},
                    {'name': 'assistant', 'type': 'assistant'},
                    {'name': 'dashboard', 'type': 'dashboard'},
                ]
            },
            {
                'name': 'NOTIFICATIONS',
                'channels': [
                    {'name': 'opportunities', 'type': 'opportunities'},
                    {'name': 'revenue', 'type': 'notifications'},
                    {'name': 'agent-activity', 'type': 'notifications'},
                ]
            },
        ]
    },
    'freelancer': {
        'name': 'Freelancer',
        'description': 'Workspace with client management channels',
        'categories': [
            {
                'name': 'WORKSPACE',
                'channels': [
                    {'name': 'creations', 'type': 'gallery'},
                    {'name': 'research', 'type': 'research'},
                    {'name': 'assistant', 'type': 'assistant'},
                    {'name': 'dashboard', 'type': 'dashboard'},
                ]
            },
            {
                'name': 'CLIENTS',
                'channels': [
                    {'name': 'client-template', 'type': 'client'},
                ]
            },
            {
                'name': 'NOTIFICATIONS',
                'channels': [
                    {'name': 'opportunities', 'type': 'opportunities'},
                    {'name': 'revenue', 'type': 'notifications'},
                ]
            },
        ]
    },
    'agency': {
        'name': 'Agency',
        'description': 'Full agency setup with team and client management',
        'categories': [
            {
                'name': 'TEAM',
                'channels': [
                    {'name': 'general', 'type': 'custom'},
                    {'name': 'projects', 'type': 'custom'},
                    {'name': 'resources', 'type': 'custom'},
                ]
            },
            {
                'name': 'AI STUDIO',
                'channels': [
                    {'name': 'creations', 'type': 'gallery'},
                    {'name': 'research', 'type': 'research'},
                    {'name': 'assistant', 'type': 'assistant'},
                ]
            },
            {
                'name': 'CLIENTS',
                'channels': [
                    {'name': 'client-template', 'type': 'client'},
                ]
            },
            {
                'name': 'ADMIN',
                'channels': [
                    {'name': 'analytics', 'type': 'dashboard'},
                    {'name': 'revenue', 'type': 'notifications'},
                    {'name': 'alerts', 'type': 'notifications'},
                ]
            },
        ]
    },
}


class DiscordClient(models.Model):
    """
    Session 431 Phase 3: Client management for freelancers/agencies.

    Tracks clients created via Discord commands with dedicated channels
    for deliveries and communication.
    """

    CLIENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]

    server = models.ForeignKey(
        DiscordServer,
        on_delete=models.CASCADE,
        related_name='clients'
    )

    name = models.CharField(
        max_length=100,
        help_text="Client name"
    )

    slug = models.CharField(
        max_length=100,
        help_text="URL-safe client identifier"
    )

    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Client email for notifications"
    )

    channel_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True,
        help_text="Discord channel ID for this client"
    )

    status = models.CharField(
        max_length=20,
        choices=CLIENT_STATUS_CHOICES,
        default='active'
    )

    deliverables_count = models.PositiveIntegerField(default=0)

    total_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total revenue from this client"
    )

    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the client"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = [['server', 'slug']]
        verbose_name = "Discord Client"
        verbose_name_plural = "Discord Clients"

    def __str__(self):
        return f"{self.name} ({self.server.guild_name})"


class ClientDeliverable(models.Model):
    """
    Session 431 Phase 3: Tracks deliverables sent to clients.

    Records every image/content delivered to a client's channel
    for history and reporting.
    """

    DELIVERABLE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]

    client = models.ForeignKey(
        DiscordClient,
        on_delete=models.CASCADE,
        related_name='deliverables'
    )

    deliverable_type = models.CharField(
        max_length=20,
        choices=DELIVERABLE_TYPE_CHOICES,
        default='image'
    )

    title = models.CharField(
        max_length=200,
        help_text="Deliverable title/description"
    )

    image_history_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="ID of ImageHistory record if applicable"
    )

    url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to the deliverable"
    )

    discord_message_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Discord message ID where this was delivered"
    )

    delivered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-delivered_at']

    def __str__(self):
        return f"{self.title} -> {self.client.name}"