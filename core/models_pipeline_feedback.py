"""
Pipeline Feedback Models - Session 449

Learning loop models for tracking feedback at each stage of the AI Content Pipeline:
1. Research Stage - Track which queries lead to better content
2. Script Stage - Track script quality metrics (engagement, completion)
3. Image Stage - Track which style presets perform best per audience
4. Voice Stage - Track voice selection effectiveness
5. Video Stage - Track video completion and engagement

These models enable the AISeriesWorkflowAgent to learn from outcomes and improve
future content generation based on what actually works.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count, F, Q
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as User


# =============================================================================
# CHOICES
# =============================================================================

class PipelineStage(models.TextChoices):
    """Stages in the AI Content Pipeline"""
    RESEARCH = 'research', 'Research - Topic and audience analysis'
    SCRIPT = 'script', 'Script - Script/narration generation'
    IMAGE = 'image', 'Image - Character and scene generation'
    VOICE = 'voice', 'Voice - Voiceover generation'
    VIDEO = 'video', 'Video - Video content generation'
    PACKAGE = 'package', 'Package - Final content packaging'


class FeedbackType(models.TextChoices):
    """Types of feedback that can be collected"""
    USER_RATING = 'user_rating', 'User Rating (1-5 stars)'
    IMPLICIT = 'implicit', 'Implicit (completion, engagement)'
    AUTOMATED = 'automated', 'Automated (quality checks)'
    A_B_TEST = 'ab_test', 'A/B Test Result'


class ContentOutcome(models.TextChoices):
    """Outcome of content after delivery/publish"""
    PENDING = 'pending', 'Pending - Not yet delivered'
    DELIVERED = 'delivered', 'Delivered - Sent to client'
    APPROVED = 'approved', 'Approved - Client accepted'
    REJECTED = 'rejected', 'Rejected - Client rejected'
    PUBLISHED = 'published', 'Published - Live on platform'
    VIRAL = 'viral', 'Viral - High engagement'


# =============================================================================
# CORE FEEDBACK MODEL
# =============================================================================

class PipelineStageFeedback(models.Model):
    """
    Generic feedback for any pipeline stage.

    Tracks both explicit (user ratings) and implicit (engagement) feedback
    at each stage of content generation. Used to learn what works.

    Example:
        - Script stage: User rates script as 4/5
        - Image stage: pixar style with "kids" audience gets 4.5 avg rating
        - Voice stage: "Rachel" voice with educational content gets 80% approval
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to Content
    series = models.ForeignKey(
        'core.AISeries',
        on_delete=models.CASCADE,
        related_name='stage_feedback',
        null=True,
        blank=True
    )
    episode = models.ForeignKey(
        'core.SeriesEpisode',
        on_delete=models.CASCADE,
        related_name='stage_feedback',
        null=True,
        blank=True
    )
    content_package = models.ForeignKey(
        'core.ContentPackage',
        on_delete=models.CASCADE,
        related_name='stage_feedback',
        null=True,
        blank=True
    )

    # Stage Info
    stage = models.CharField(
        max_length=20,
        choices=PipelineStage.choices,
        db_index=True
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FeedbackType.choices,
        default=FeedbackType.USER_RATING
    )

    # Rating (1-5 scale, normalized)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text="Rating from 1.0 to 5.0"
    )

    # Context for Learning
    context = models.JSONField(
        default=dict,
        help_text="Stage-specific context (style, voice, audience, etc.)"
    )
    # Example context for image stage:
    # {"style_preset": "pixar", "target_audience": "kids", "series_type": "educational"}

    # User providing feedback
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pipeline_feedback'
    )

    # Optional text feedback
    comment = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stage', 'created_at']),
            models.Index(fields=['series', 'stage']),
        ]

    def __str__(self):
        return f"{self.stage} feedback: {self.rating}/5"


# =============================================================================
# STYLE PRESET PERFORMANCE
# =============================================================================

class StylePresetPerformance(models.Model):
    """
    Track which style presets perform best for different audiences.

    Aggregates feedback to learn patterns like:
    - "pixar" style with "kids" audience: 4.7 avg rating
    - "anime" style with "young adults": 4.5 avg rating
    - "disney" style with "family": 4.8 avg rating

    Used by AISeriesWorkflowAgent to suggest best styles.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Style Configuration
    style_preset = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Style preset (pixar, disney, anime, etc.)"
    )
    target_audience = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Target audience category"
    )
    series_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Series type (educational, entertainment, marketing)"
    )

    # Aggregated Metrics
    total_uses = models.IntegerField(default=0)
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    approval_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Percentage of content approved/published (0-100)"
    )
    engagement_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Normalized engagement score (0-100)"
    )

    # Success Tracking
    successful_series_count = models.IntegerField(default=0)
    viral_content_count = models.IntegerField(default=0)
    rejection_count = models.IntegerField(default=0)

    # Confidence
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Confidence in this recommendation (0-1)"
    )

    # Last updated
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['style_preset', 'target_audience', 'series_type']]
        ordering = ['-avg_rating', '-total_uses']

    def __str__(self):
        return f"{self.style_preset} for {self.target_audience}: {self.avg_rating}/5 ({self.total_uses} uses)"

    @classmethod
    def get_best_style(cls, target_audience: str, series_type: str = '', min_uses: int = 3):
        """Get the best performing style for an audience."""
        queryset = cls.objects.filter(
            target_audience__icontains=target_audience,
            total_uses__gte=min_uses
        )
        if series_type:
            queryset = queryset.filter(series_type=series_type)

        return queryset.order_by('-avg_rating', '-confidence_score').first()

    @classmethod
    def record_usage(cls, style_preset: str, target_audience: str, series_type: str = '',
                     rating: float = None, approved: bool = None, engagement: float = None):
        """Record a new usage of a style preset with optional feedback."""
        obj, created = cls.objects.get_or_create(
            style_preset=style_preset.lower(),
            target_audience=target_audience.lower(),
            series_type=series_type.lower(),
            defaults={'total_uses': 0}
        )

        obj.total_uses += 1

        # Update running averages
        if rating is not None:
            obj.avg_rating = (obj.avg_rating * (obj.total_uses - 1) + Decimal(str(rating))) / obj.total_uses

        if approved is not None:
            if approved:
                obj.successful_series_count += 1
            else:
                obj.rejection_count += 1
            obj.approval_rate = Decimal(str(
                (obj.successful_series_count / (obj.successful_series_count + obj.rejection_count)) * 100
            ))

        if engagement is not None:
            obj.engagement_score = (obj.engagement_score * (obj.total_uses - 1) + Decimal(str(engagement))) / obj.total_uses

        # Update confidence based on sample size
        obj.confidence_score = min(Decimal('1.0'), Decimal(str(obj.total_uses / 100)))

        obj.save()
        return obj


# =============================================================================
# VOICE PERFORMANCE
# =============================================================================

class VoicePerformance(models.Model):
    """
    Track voice selection effectiveness.

    Learn which voices work best for:
    - Different content types (educational, entertainment, marketing)
    - Different audiences (kids, adults, professionals)
    - Different tones (friendly, authoritative, casual)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Voice Configuration
    voice_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="ElevenLabs voice ID"
    )
    voice_name = models.CharField(
        max_length=100,
        db_index=True
    )
    voice_style = models.CharField(
        max_length=50,
        blank=True,
        help_text="Voice style category (friendly, authoritative, etc.)"
    )

    # Content Context
    series_type = models.CharField(max_length=50, blank=True)
    target_audience = models.CharField(max_length=100, blank=True)

    # Performance Metrics
    total_uses = models.IntegerField(default=0)
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    approval_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Video completion rate when this voice is used"
    )

    # Confidence
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['voice_id', 'series_type', 'target_audience']]
        ordering = ['-avg_rating', '-total_uses']

    def __str__(self):
        return f"{self.voice_name} for {self.target_audience}: {self.avg_rating}/5"

    @classmethod
    def get_best_voice(cls, series_type: str = '', target_audience: str = '', min_uses: int = 3):
        """Get the best performing voice for context."""
        queryset = cls.objects.filter(total_uses__gte=min_uses)
        if series_type:
            queryset = queryset.filter(series_type=series_type)
        if target_audience:
            queryset = queryset.filter(target_audience__icontains=target_audience)

        return queryset.order_by('-avg_rating', '-confidence_score').first()


# =============================================================================
# CONTENT ENGAGEMENT
# =============================================================================

class ContentEngagement(models.Model):
    """
    Track engagement metrics for published content.

    Connects back to series/episodes to close the learning loop:
    - What gets views?
    - What gets completed (watched to end)?
    - What gets shared?
    - What converts to revenue?
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Content Reference
    series = models.ForeignKey(
        'core.AISeries',
        on_delete=models.CASCADE,
        related_name='engagement_metrics',
        null=True,
        blank=True
    )
    episode = models.ForeignKey(
        'core.SeriesEpisode',
        on_delete=models.CASCADE,
        related_name='engagement_metrics',
        null=True,
        blank=True
    )
    content_package = models.ForeignKey(
        'core.ContentPackage',
        on_delete=models.CASCADE,
        related_name='engagement_metrics',
        null=True,
        blank=True
    )

    # Platform
    platform = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Platform where content is published (youtube, tiktok, etc.)"
    )
    external_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="External platform ID for tracking"
    )

    # Engagement Metrics
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)

    # Watch Metrics (for video)
    avg_watch_time_seconds = models.IntegerField(default=0)
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Percentage who watched to completion (0-100)"
    )

    # Revenue (if applicable)
    revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Revenue generated by this content"
    )

    # Outcome
    outcome = models.CharField(
        max_length=20,
        choices=ContentOutcome.choices,
        default=ContentOutcome.PENDING
    )
    outcome_notes = models.TextField(blank=True)

    # Context (for learning)
    content_context = models.JSONField(
        default=dict,
        help_text="Content configuration at time of creation"
    )
    # Example: {"style_preset": "pixar", "voice": "Rachel", "series_type": "educational", "audience": "kids"}

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['platform', 'outcome']),
            models.Index(fields=['series', 'outcome']),
        ]

    def __str__(self):
        return f"{self.platform} engagement: {self.views} views, {self.completion_rate}% completion"

    @property
    def engagement_score(self) -> float:
        """Calculate normalized engagement score (0-100)."""
        if self.views == 0:
            return 0.0

        # Weighted engagement formula
        like_rate = (self.likes / self.views) * 100
        share_rate = (self.shares / self.views) * 100 * 2  # Shares weighted 2x
        comment_rate = (self.comments / self.views) * 100 * 1.5  # Comments weighted 1.5x

        raw_score = like_rate + share_rate + comment_rate + float(self.completion_rate)

        # Normalize to 0-100 (assuming 20% is excellent)
        return min(100, raw_score * 5)


# =============================================================================
# RESEARCH QUERY PERFORMANCE
# =============================================================================

class ResearchQueryPerformance(models.Model):
    """
    Track which research queries lead to better content.

    Learn patterns like:
    - Queries about "trending" topics correlate with higher engagement
    - Market research leads to better marketing content
    - Competitor analysis improves educational content
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Query Info
    query_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Type of research query (trending, competitor, audience, etc.)"
    )
    query_keywords = models.JSONField(
        default=list,
        help_text="Keywords used in query"
    )

    # Context
    series_type = models.CharField(max_length=50, blank=True)
    target_audience = models.CharField(max_length=100, blank=True)

    # Results
    total_uses = models.IntegerField(default=0)
    avg_content_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average rating of content produced from this research"
    )
    avg_engagement_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average engagement of content from this research"
    )

    # Success tracking
    successful_series_count = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-avg_content_rating', '-total_uses']

    def __str__(self):
        return f"Research '{self.query_type}': {self.avg_content_rating}/5 avg rating"


# =============================================================================
# LEARNING INSIGHTS
# =============================================================================

class PipelineLearningInsight(models.Model):
    """
    Store generated learning insights from the feedback data.

    Example insights:
    - "Pixar style performs 23% better than cartoon for kids educational content"
    - "Rachel voice has 40% higher completion rate for marketing content"
    - "Trending topic research correlates with 2x engagement"
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Insight
    stage = models.CharField(
        max_length=20,
        choices=PipelineStage.choices,
        db_index=True
    )
    insight_type = models.CharField(
        max_length=50,
        help_text="Type of insight (best_style, best_voice, correlation, etc.)"
    )
    insight_summary = models.CharField(
        max_length=500,
        help_text="Human-readable insight summary"
    )
    insight_data = models.JSONField(
        default=dict,
        help_text="Structured insight data for automated use"
    )

    # Applicability
    applicable_to = models.JSONField(
        default=dict,
        help_text="Conditions where this insight applies"
    )
    # Example: {"series_type": "educational", "target_audience": "kids"}

    # Confidence and Impact
    confidence = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Confidence in this insight (0-1)"
    )
    sample_size = models.IntegerField(
        default=0,
        help_text="Number of data points supporting this insight"
    )
    estimated_impact = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Estimated improvement percentage"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether to apply this insight"
    )
    times_applied = models.IntegerField(default=0)
    times_validated = models.IntegerField(
        default=0,
        help_text="Times insight was validated as correct"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this insight should be re-evaluated"
    )

    class Meta:
        ordering = ['-confidence', '-sample_size']
        indexes = [
            models.Index(fields=['stage', 'is_active']),
        ]

    def __str__(self):
        return f"{self.stage} insight: {self.insight_summary[:50]}..."

    @classmethod
    def get_active_insights(cls, stage: str = None, context: dict = None):
        """Get active insights, optionally filtered by stage and context."""
        queryset = cls.objects.filter(is_active=True)

        if stage:
            queryset = queryset.filter(stage=stage)

        # TODO: Filter by applicable_to matching context

        return queryset.order_by('-confidence', '-estimated_impact')
