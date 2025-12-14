"""
Voice Marketplace Models - Session 440

Database models for the AI Pixar voice marketplace:
- VoiceProfile: Cloned or original voices available for use
- VoiceTransaction: Record of voice usage for revenue tracking
- VoiceReview: User reviews and ratings of marketplace voices
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as User


class VoiceProfile(models.Model):
    """
    A cloned or original voice available for use in the marketplace.

    Voices can be created via:
    - Discord voice recording + ElevenLabs cloning
    - ElevenLabs web interface
    - Pre-existing ElevenLabs voices
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_profiles')

    # Basic info
    name = models.CharField(max_length=100, help_text="Display name for the voice")
    description = models.TextField(blank=True, help_text="Description of the voice character")

    # ElevenLabs integration
    elevenlabs_voice_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="ElevenLabs voice ID"
    )

    # Voice characteristics
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('neutral', 'Neutral'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='neutral')

    AGE_RANGE_CHOICES = [
        ('child', 'Child (5-12)'),
        ('teen', 'Teen (13-19)'),
        ('young_adult', 'Young Adult (20-35)'),
        ('adult', 'Adult (35-55)'),
        ('senior', 'Senior (55+)'),
    ]
    age_range = models.CharField(max_length=20, choices=AGE_RANGE_CHOICES, default='adult')

    accent = models.CharField(max_length=50, blank=True, help_text="Accent (e.g., British, Southern US)")
    language = models.CharField(max_length=50, default='English')

    # Style tags for searchability
    style_tags = models.JSONField(
        default=list,
        help_text="Tags like 'warm', 'authoritative', 'friendly', 'narrator'"
    )

    # Use cases
    USE_CASE_CHOICES = [
        ('narration', 'Narration/Audiobook'),
        ('animation', 'Animation/Character'),
        ('commercial', 'Commercial/Advertisement'),
        ('podcast', 'Podcast/YouTube'),
        ('gaming', 'Gaming/Character'),
        ('assistant', 'Virtual Assistant'),
        ('general', 'General Purpose'),
    ]
    primary_use_case = models.CharField(max_length=50, choices=USE_CASE_CHOICES, default='general')

    # Marketplace settings
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this voice is available in the public marketplace"
    )

    PRICING_MODEL_CHOICES = [
        ('per_minute', 'Per Minute'),
        ('per_character', 'Per 1000 Characters'),
        ('flat_rate', 'Flat Rate per Generation'),
    ]
    pricing_model = models.CharField(max_length=20, choices=PRICING_MODEL_CHOICES, default='per_minute')

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.50'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Price per unit (minute, 1000 chars, or generation)"
    )

    # Sample audio
    sample_audio_url = models.URLField(blank=True, null=True, help_text="URL to sample audio")
    sample_text = models.TextField(blank=True, help_text="Text used in the sample")
    sample_duration_seconds = models.IntegerField(default=0)

    # Statistics
    total_uses = models.IntegerField(default=0)
    total_characters_generated = models.IntegerField(default=0)
    total_minutes_generated = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Ratings (calculated from reviews)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)

    # Quality indicators
    quality_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI-assessed quality score 0-1"
    )
    is_verified = models.BooleanField(default=False, help_text="Verified by platform")
    is_featured = models.BooleanField(default=False, help_text="Featured in marketplace")

    # Creation tracking
    CREATION_METHOD_CHOICES = [
        ('discord_clone', 'Cloned via Discord Recording'),
        ('web_clone', 'Cloned via Web Upload'),
        ('elevenlabs_library', 'From ElevenLabs Library'),
        ('professional', 'Professional Voice Actor'),
    ]
    creation_method = models.CharField(max_length=30, choices=CREATION_METHOD_CHOICES, default='discord_clone')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-is_featured', '-average_rating', '-total_uses']
        indexes = [
            models.Index(fields=['owner', 'is_public']),
            models.Index(fields=['is_public', 'is_active', '-average_rating']),
            models.Index(fields=['gender', 'age_range', 'primary_use_case']),
        ]

    def __str__(self):
        return f"{self.name} by {self.owner.username}"

    def get_price_display(self):
        """Get human-readable price string."""
        if self.pricing_model == 'per_minute':
            return f"${self.price}/min"
        elif self.pricing_model == 'per_character':
            return f"${self.price}/1k chars"
        else:
            return f"${self.price}/gen"

    def calculate_cost(self, text_length: int = None, duration_seconds: int = None) -> Decimal:
        """Calculate the cost for a generation."""
        if self.pricing_model == 'per_minute' and duration_seconds:
            minutes = Decimal(duration_seconds) / Decimal('60')
            return (self.price * minutes).quantize(Decimal('0.01'))
        elif self.pricing_model == 'per_character' and text_length:
            thousands = Decimal(text_length) / Decimal('1000')
            return (self.price * thousands).quantize(Decimal('0.01'))
        else:
            return self.price

    def update_statistics(self, characters: int, duration_seconds: int, revenue: Decimal):
        """Update usage statistics after a generation."""
        self.total_uses += 1
        self.total_characters_generated += characters
        self.total_minutes_generated += Decimal(duration_seconds) / Decimal('60')
        self.total_revenue += revenue
        self.save(update_fields=[
            'total_uses', 'total_characters_generated',
            'total_minutes_generated', 'total_revenue'
        ])

    def recalculate_rating(self):
        """Recalculate average rating from reviews."""
        reviews = self.reviews.filter(is_active=True)
        if reviews.exists():
            self.average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.rating_count = reviews.count()
            self.save(update_fields=['average_rating', 'rating_count'])


class VoiceTransaction(models.Model):
    """
    Record of voice usage for revenue tracking.

    Created whenever a user generates TTS using a marketplace voice.
    Handles revenue split between voice owner and platform.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Parties
    voice = models.ForeignKey(VoiceProfile, on_delete=models.PROTECT, related_name='transactions')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_purchases')

    # Generation details
    text_length = models.IntegerField(help_text="Number of characters generated")
    audio_duration_seconds = models.IntegerField(help_text="Duration of generated audio")

    # The actual text (stored for potential dispute resolution)
    generated_text = models.TextField(blank=True, help_text="Text that was converted to speech")

    # Financial
    gross_price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Total price charged")
    platform_fee = models.DecimalField(max_digits=8, decimal_places=2, help_text="30% platform fee")
    owner_payout = models.DecimalField(max_digits=8, decimal_places=2, help_text="70% to voice owner")

    # Payout tracking
    PAYOUT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    payout_status = models.CharField(max_length=20, choices=PAYOUT_STATUS_CHOICES, default='pending')
    payout_processed_at = models.DateTimeField(null=True, blank=True)

    # Stripe references
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_transfer_id = models.CharField(max_length=100, blank=True)

    # Content reference (what project/content this was used for)
    project_id = models.UUIDField(null=True, blank=True, help_text="Associated project if any")

    CONTENT_TYPE_CHOICES = [
        ('animated_series', 'Animated Series'),
        ('audiobook', 'Audiobook'),
        ('video', 'Video Narration'),
        ('podcast', 'Podcast'),
        ('commercial', 'Commercial'),
        ('personal', 'Personal Use'),
        ('other', 'Other'),
    ]
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPE_CHOICES, default='other')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['voice', '-created_at']),
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['payout_status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.buyer.username} used {self.voice.name} - ${self.gross_price}"

    @classmethod
    def create_transaction(
        cls,
        voice: VoiceProfile,
        buyer: User,
        text: str,
        duration_seconds: int,
        content_type: str = 'other',
        project_id: str = None
    ) -> 'VoiceTransaction':
        """Create a transaction with automatic revenue split calculation."""

        # Calculate price
        gross_price = voice.calculate_cost(
            text_length=len(text),
            duration_seconds=duration_seconds
        )

        # Revenue split: 70% owner, 30% platform
        platform_fee = (gross_price * Decimal('0.30')).quantize(Decimal('0.01'))
        owner_payout = gross_price - platform_fee

        # Create transaction
        transaction = cls.objects.create(
            voice=voice,
            buyer=buyer,
            text_length=len(text),
            audio_duration_seconds=duration_seconds,
            generated_text=text[:1000],  # Store first 1000 chars only
            gross_price=gross_price,
            platform_fee=platform_fee,
            owner_payout=owner_payout,
            content_type=content_type,
            project_id=project_id if project_id else None,
        )

        # Update voice statistics
        voice.update_statistics(len(text), duration_seconds, gross_price)

        return transaction


class VoiceReview(models.Model):
    """
    User reviews and ratings of marketplace voices.

    Helps other users choose voices and provides feedback to voice owners.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    voice = models.ForeignKey(VoiceProfile, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_reviews')

    # Rating
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1-5 star rating"
    )

    # Review content
    title = models.CharField(max_length=100, blank=True)
    review_text = models.TextField(blank=True)

    # What they used it for
    use_case = models.CharField(max_length=100, blank=True, help_text="What they used the voice for")

    # Quality aspects (optional detailed ratings)
    clarity_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Voice clarity 1-5"
    )
    naturalness_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How natural it sounds 1-5"
    )
    consistency_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Consistency across generations 1-5"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Whether reviewer actually used this voice"
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ['voice', 'reviewer']  # One review per user per voice
        indexes = [
            models.Index(fields=['voice', '-created_at']),
            models.Index(fields=['voice', 'is_active', '-rating']),
        ]

    def __str__(self):
        return f"{self.reviewer.username}'s review of {self.voice.name}: {self.rating}/5"

    def save(self, *args, **kwargs):
        # Check if this is a verified purchase
        if not self.pk:  # Only on creation
            self.is_verified_purchase = VoiceTransaction.objects.filter(
                voice=self.voice,
                buyer=self.reviewer
            ).exists()

        super().save(*args, **kwargs)

        # Recalculate voice rating
        self.voice.recalculate_rating()


class VoiceCloneRequest(models.Model):
    """
    Track voice cloning requests from Discord recordings.

    Stores the recording session state and final result.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_clone_requests')

    # Discord context
    discord_user_id = models.CharField(max_length=50)
    discord_guild_id = models.CharField(max_length=50)
    discord_channel_id = models.CharField(max_length=50)

    # Recording status
    STATUS_CHOICES = [
        ('pending', 'Pending Recording'),
        ('recording', 'Recording'),
        ('processing', 'Processing'),
        ('cloning', 'Cloning with ElevenLabs'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Recording data
    recording_started_at = models.DateTimeField(null=True, blank=True)
    recording_ended_at = models.DateTimeField(null=True, blank=True)
    recording_duration_seconds = models.IntegerField(default=0)

    # Audio file path (temporary storage during processing)
    audio_file_path = models.CharField(max_length=500, blank=True)

    # Result
    voice_profile = models.OneToOneField(
        VoiceProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clone_request'
    )

    # Error tracking
    error_message = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Clone request by {self.user.username} - {self.status}"

    def start_recording(self):
        """Mark recording as started."""
        self.status = 'recording'
        self.recording_started_at = timezone.now()
        self.save(update_fields=['status', 'recording_started_at', 'updated_at'])

    def stop_recording(self):
        """Mark recording as stopped and calculate duration."""
        self.recording_ended_at = timezone.now()
        if self.recording_started_at:
            delta = self.recording_ended_at - self.recording_started_at
            self.recording_duration_seconds = int(delta.total_seconds())
        self.status = 'processing'
        self.save(update_fields=['status', 'recording_ended_at', 'recording_duration_seconds', 'updated_at'])

    def mark_failed(self, error_message: str):
        """Mark the request as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])

    def complete(self, voice_profile: VoiceProfile):
        """Mark as completed with the created voice profile."""
        self.status = 'completed'
        self.voice_profile = voice_profile
        self.save(update_fields=['status', 'voice_profile', 'updated_at'])
