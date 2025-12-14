"""
Unified Content Pipeline Models - Session 440

The AI Content Factory: From $5 birthday messages to $5M movie pitches.

Models:
- ContentPackage: Complete content package (mascot, ad, series, etc.)
- ContentAsset: Individual files within a package
- ContentPurchase: Purchase/delivery records
- ContentShowroom: Discord channel showroom configuration
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as User


# =============================================================================
# CHOICES
# =============================================================================

class ContentTier(models.TextChoices):
    """Content package tiers - same pipeline, different scale"""
    QUICK = 'quick', 'Quick ($5-29) - Birthday messages, simple content'
    AD = 'ad', 'Ad ($29-99) - Small business ads'
    BRAND = 'brand', 'Brand ($99-499) - Full brand packages'
    SERIES = 'series', 'Series ($499-2999) - Content series'
    PITCH = 'pitch', 'Pitch ($2999-9999) - Series/movie pitches'
    PRODUCTION = 'production', 'Production ($9999+) - Full productions'


class ContentCategory(models.TextChoices):
    """Industry/use case categories"""
    RESTAURANT = 'restaurant', 'Restaurant & Food'
    RETAIL = 'retail', 'Retail & Shopping'
    HEALTHCARE = 'healthcare', 'Healthcare & Medical'
    EDUCATION = 'education', 'Education & Schools'
    TECH = 'tech', 'Tech & Startups'
    ENTERTAINMENT = 'entertainment', 'Entertainment & Media'
    REALESTATE = 'realestate', 'Real Estate'
    FITNESS = 'fitness', 'Fitness & Wellness'
    FINANCE = 'finance', 'Finance & Banking'
    NONPROFIT = 'nonprofit', 'Nonprofit & Charity'
    PERSONAL = 'personal', 'Personal & Events'
    OTHER = 'other', 'Other'


class PackageStatus(models.TextChoices):
    """Content package lifecycle status"""
    QUEUED = 'queued', 'Queued for generation'
    GENERATING = 'generating', 'Currently generating'
    READY = 'ready', 'Ready for sale/delivery'
    SOLD = 'sold', 'Sold (pending delivery)'
    DELIVERED = 'delivered', 'Delivered to buyer'
    FAILED = 'failed', 'Generation failed'


class AssetType(models.TextChoices):
    """Types of assets in a package"""
    IMAGE = 'image', 'Image (PNG, JPG)'
    VIDEO = 'video', 'Video (MP4, WebM)'
    AUDIO = 'audio', 'Audio (MP3, WAV)'
    DOCUMENT = 'document', 'Document (PDF, TXT)'
    SOURCE = 'source', 'Source File (PSD, AI, etc.)'
    SCRIPT = 'script', 'Script/Copy'
    THUMBNAIL = 'thumbnail', 'Thumbnail'
    PREVIEW = 'preview', 'Preview Asset'


class PaymentStatus(models.TextChoices):
    """Payment processing status"""
    PENDING = 'pending', 'Pending payment'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Payment completed'
    FAILED = 'failed', 'Payment failed'
    REFUNDED = 'refunded', 'Refunded'


# =============================================================================
# MODELS
# =============================================================================

class ContentPackage(models.Model):
    """
    A complete content package ready for sale/delivery.

    This is the core model - represents everything from a $5 birthday
    message to a $50,000 production package. Same structure, different scale.

    Examples:
    - Quick: "Happy Birthday Tommy from Spider-Man!" ($15)
    - Ad: "Tony's Pizza Brooklyn $2 Tuesdays" ($49)
    - Brand: "EcoClean sustainable cleaning products" ($249)
    - Series: "5-episode climate change explainer for kids" ($1,499)
    - Pitch: "Robot learning emotions - Netflix series" ($4,999)
    - Production: "Full 10-episode first season" ($49,999)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic Info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tier = models.CharField(max_length=20, choices=ContentTier.choices)
    category = models.CharField(
        max_length=20,
        choices=ContentCategory.choices,
        default=ContentCategory.OTHER
    )

    # The original prompt that created this
    prompt = models.TextField(help_text="Original creation prompt")

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    @property
    def final_price(self) -> Decimal:
        """Calculate price after discount"""
        if self.discount_percent > 0:
            discount = self.base_price * Decimal(self.discount_percent) / 100
            return self.base_price - discount
        return self.base_price

    # Status
    status = models.CharField(
        max_length=20,
        choices=PackageStatus.choices,
        default=PackageStatus.QUEUED
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Show in public marketplace"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature prominently in showroom"
    )

    # Generation configuration (stored for reproducibility)
    generation_config = models.JSONField(
        default=dict,
        help_text="All settings used during generation"
    )

    # Generation progress (0-100)
    generation_progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    generation_stage = models.CharField(
        max_length=50,
        blank=True,
        help_text="Current generation stage (research, script, character, voice, video, package)"
    )

    # Preview assets (quick access for marketplace display)
    preview_image_url = models.URLField(blank=True, null=True)
    preview_video_url = models.URLField(blank=True, null=True)
    preview_audio_url = models.URLField(blank=True, null=True)

    # Stats
    views = models.IntegerField(default=0)
    purchases = models.IntegerField(default=0)

    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_content_packages'
    )
    purchased_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchased_content_packages'
    )

    # Discord integration
    discord_message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Message ID in showroom channel"
    )
    discord_channel_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Showroom channel ID"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generation_started_at = models.DateTimeField(null=True, blank=True)
    generation_completed_at = models.DateTimeField(null=True, blank=True)
    purchased_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tier', 'status']),
            models.Index(fields=['category', 'is_public']),
            models.Index(fields=['created_by', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_tier_display()})"

    def start_generation(self):
        """Mark package as generating"""
        self.status = PackageStatus.GENERATING
        self.generation_started_at = timezone.now()
        self.save(update_fields=['status', 'generation_started_at'])

    def complete_generation(self):
        """Mark package as ready"""
        self.status = PackageStatus.READY
        self.generation_progress = 100
        self.generation_completed_at = timezone.now()
        self.save(update_fields=['status', 'generation_progress', 'generation_completed_at'])

    def mark_sold(self, buyer: 'User'):
        """Mark package as sold"""
        self.status = PackageStatus.SOLD
        self.purchased_by = buyer
        self.purchased_at = timezone.now()
        self.purchases += 1
        self.save(update_fields=['status', 'purchased_by', 'purchased_at', 'purchases'])

    def mark_delivered(self):
        """Mark package as delivered"""
        self.status = PackageStatus.DELIVERED
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])


class ContentAsset(models.Model):
    """
    Individual asset within a content package.

    Examples:
    - Mascot image (front pose)
    - 30-second video ad
    - Voiceover audio
    - Script document
    - Source PSD file
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(
        ContentPackage,
        on_delete=models.CASCADE,
        related_name='assets'
    )

    # Asset info
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # File info
    file_url = models.URLField()
    file_size = models.BigIntegerField(default=0, help_text="Size in bytes")
    file_format = models.CharField(max_length=20, blank=True)  # png, mp4, mp3, etc.

    # Type-specific metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Type-specific data (dimensions, duration, etc.)"
    )
    # Examples:
    # Image: {"width": 1920, "height": 1080, "format": "png"}
    # Video: {"duration": 30, "resolution": "1080p", "fps": 30}
    # Audio: {"duration": 45, "sample_rate": 44100, "channels": 2}

    # Is this a preview asset?
    is_preview = models.BooleanField(
        default=False,
        help_text="Show in marketplace preview"
    )

    # Ordering within package
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['package', 'order', 'asset_type']

    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"

    @property
    def file_size_display(self) -> str:
        """Human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"


class ContentPurchase(models.Model):
    """
    Record of a content package purchase.

    Tracks payment, customizations, and delivery.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    package = models.ForeignKey(
        ContentPackage,
        on_delete=models.PROTECT,  # Don't delete packages with purchases
        related_name='purchase_records'
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='content_purchases'
    )

    # Pricing at time of purchase (preserved even if package price changes)
    price_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_applied = models.IntegerField(default=0)
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Customizations requested by buyer
    customizations = models.JSONField(
        null=True,
        blank=True,
        help_text="Customization requests (name changes, colors, etc.)"
    )
    # Example: {"business_name": "Tony's Pizza", "colors": ["red", "white"], "voice_id": "abc123"}

    # Payment
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)

    # Delivery
    discord_channel_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Delivery channel ID"
    )
    delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_message_id = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Purchase: {self.package.name} by {self.buyer}"

    def mark_paid(self, stripe_payment_intent_id: str, stripe_charge_id: str = None):
        """Mark purchase as paid"""
        self.payment_status = PaymentStatus.COMPLETED
        self.stripe_payment_intent_id = stripe_payment_intent_id
        if stripe_charge_id:
            self.stripe_charge_id = stripe_charge_id
        self.save(update_fields=[
            'payment_status', 'stripe_payment_intent_id',
            'stripe_charge_id', 'updated_at'
        ])

    def mark_delivered(self, channel_id: str = None, message_id: str = None):
        """Mark purchase as delivered"""
        self.delivered = True
        self.delivered_at = timezone.now()
        if channel_id:
            self.discord_channel_id = channel_id
        if message_id:
            self.delivery_message_id = message_id
        self.save(update_fields=[
            'delivered', 'delivered_at', 'discord_channel_id',
            'delivery_message_id', 'updated_at'
        ])


class ContentShowroom(models.Model):
    """
    Discord channel showroom configuration.

    Maps Discord channels to content categories for the marketplace.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Discord info
    guild_id = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100, unique=True)
    channel_name = models.CharField(max_length=100)

    # What content to show
    tier_filter = models.CharField(
        max_length=20,
        choices=ContentTier.choices,
        blank=True,
        null=True,
        help_text="Only show this tier (null = all)"
    )
    category_filter = models.CharField(
        max_length=20,
        choices=ContentCategory.choices,
        blank=True,
        null=True,
        help_text="Only show this category (null = all)"
    )

    # Display settings
    max_items = models.IntegerField(default=50)
    auto_refresh = models.BooleanField(
        default=True,
        help_text="Auto-post new content"
    )
    show_prices = models.BooleanField(default=True)
    show_previews = models.BooleanField(default=True)

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Content showrooms"

    def __str__(self):
        return f"Showroom: #{self.channel_name}"


# =============================================================================
# GENERATION JOB MODEL
# =============================================================================

class ContentGenerationJob(models.Model):
    """
    Tracks a content generation job through the pipeline.

    Stages:
    1. research - Spider data gathering
    2. script - GPT script/copy generation
    3. character - Stability AI image generation
    4. voice - ElevenLabs voice generation
    5. video - Runway ML video generation
    6. package - Bundle and finalize
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.OneToOneField(
        ContentPackage,
        on_delete=models.CASCADE,
        related_name='generation_job'
    )

    # Current stage
    current_stage = models.CharField(
        max_length=20,
        default='queued',
        help_text="Current pipeline stage"
    )

    # Stage results (stored as completed)
    research_result = models.JSONField(null=True, blank=True)
    script_result = models.JSONField(null=True, blank=True)
    character_result = models.JSONField(null=True, blank=True)
    voice_result = models.JSONField(null=True, blank=True)
    video_result = models.JSONField(null=True, blank=True)

    # Errors
    error_message = models.TextField(blank=True)
    error_stage = models.CharField(max_length=20, blank=True)

    # Celery task tracking
    celery_task_id = models.CharField(max_length=100, blank=True, null=True)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Cost tracking
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    cost_breakdown = models.JSONField(
        default=dict,
        help_text="Cost per stage"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job for {self.package.name}: {self.current_stage}"

    def advance_stage(self, result: dict = None):
        """Move to next pipeline stage"""
        stages = ['queued', 'research', 'script', 'character', 'voice', 'video', 'package', 'complete']
        current_idx = stages.index(self.current_stage)

        # Save result for current stage
        if result and self.current_stage != 'queued':
            setattr(self, f'{self.current_stage}_result', result)

        # Move to next stage
        if current_idx < len(stages) - 1:
            self.current_stage = stages[current_idx + 1]

            # Update package progress
            progress = int((current_idx + 1) / (len(stages) - 1) * 100)
            self.package.generation_progress = progress
            self.package.generation_stage = self.current_stage
            self.package.save(update_fields=['generation_progress', 'generation_stage'])

        self.save()

    def fail(self, error: str):
        """Mark job as failed"""
        self.error_message = error
        self.error_stage = self.current_stage
        self.current_stage = 'failed'
        self.save()

        self.package.status = PackageStatus.FAILED
        self.package.save(update_fields=['status'])
