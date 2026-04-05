"""
Autonomous Content Studio Models - Session 466

Models for autonomous content channel management (Tier 1 Autonomous Situation #3).

This implements the "Autonomous Content Studio" where users create content channels
that run forever, autonomously creating and optimizing content based on performance.

Models:
- ContentChannel: An autonomous content channel (e.g., "AI for Kids" YouTube channel)
- ChannelEpisode: A single piece of content created for a channel
- TopicPerformance: Learning data about which topics perform well
- ContentDebate: Records of agent debates about content decisions

Design Pattern:
Follows Market Intelligence Desk pattern (Session 465) with all 5 autonomous properties:
1. Persistent Context - Channel configuration and performance history
2. Incoming Signals - Spider trends, performance metrics, audience feedback
3. Internal Disagreement - TopicMiner vs Contrarian vs Analyst debates
4. Outputs with Consequences - Published content tracked for performance
5. Self-Renewal - Schedules own next content cycle, improves strategy
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
    pass


# =============================================================================
# CHOICES
# =============================================================================

class ContentFrequency(models.TextChoices):
    """How often channel creates content"""
    DAILY = 'daily', 'Daily - 1 episode per day'
    WEEKLY = 'weekly', 'Weekly - 1 episode per week'
    BIWEEKLY = 'biweekly', 'Bi-weekly - 2 episodes per week'
    MONTHLY = 'monthly', 'Monthly - 1 episode per month'


class PublishingPlatform(models.TextChoices):
    """Where content is published"""
    YOUTUBE = 'youtube', 'YouTube'
    TIKTOK = 'tiktok', 'TikTok'
    INSTAGRAM = 'instagram', 'Instagram Reels'
    ALL = 'all', 'All Platforms'


class ChannelStatus(models.TextChoices):
    """Channel operational status"""
    ACTIVE = 'active', 'Active - Creating content autonomously'
    PAUSED = 'paused', 'Paused - Temporarily stopped'
    COMPLETED = 'completed', 'Completed - Goal achieved'
    FAILED = 'failed', 'Failed - Critical error'


# =============================================================================
# MODELS
# =============================================================================

class ContentChannel(models.Model):
    """
    An autonomous content channel that runs forever.

    Example: "AI Explained for Kids" YouTube channel
    - Publishes 2 videos/week
    - Educational style, Pixar animation
    - Uses "Rachel" voice
    - Learns from engagement metrics

    The AutonomousContentStudioCoordinator monitors all active channels and
    triggers content creation when next_content_due arrives.

    Properties of Autonomous Situation:
    1. Persistent Context - Stores config, performance history
    2. Incoming Signals - Gets trends from spiders, metrics from platforms
    3. Internal Disagreement - Agents debate topics before creating
    4. Outputs with Consequences - Published content tracked
    5. Self-Renewal - Updates next_content_due after each cycle
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='content_channels'
    )

    # Workspace linkage
    workspace = models.ForeignKey(
        'core.ProjectWorkspace', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='content_channels', db_index=True,
    )

    # =========================================================================
    # CHANNEL CONFIGURATION
    # =========================================================================

    name = models.CharField(
        max_length=200,
        help_text="Channel name (e.g., 'AI for Kids', 'Space Facts Weekly')"
    )

    topic_domain = models.TextField(
        help_text="Topic focus (e.g., 'artificial intelligence, machine learning, explained for children')"
    )

    target_audience = models.CharField(
        max_length=200,
        help_text="Target audience description (e.g., 'Kids 8-12', 'Tech professionals')"
    )

    content_frequency = models.CharField(
        max_length=20,
        choices=ContentFrequency.choices,
        default=ContentFrequency.WEEKLY,
        help_text="How often content is created"
    )

    # =========================================================================
    # STYLE CONFIGURATION
    # =========================================================================

    visual_style = models.CharField(
        max_length=200,
        default='pixar',
        help_text="Visual style for content (e.g., 'pixar, colorful, friendly')"
    )

    voice_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ElevenLabs voice ID from voice marketplace (Session 442-444)"
    )

    voice_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Voice name for reference"
    )

    content_type = models.CharField(
        max_length=20,
        default='educational',
        help_text="Content type: educational, entertainment, marketing"
    )

    # =========================================================================
    # PUBLISHING CONFIGURATION
    # =========================================================================

    platform = models.CharField(
        max_length=20,
        choices=PublishingPlatform.choices,
        default=PublishingPlatform.YOUTUBE,
        help_text="Publishing platform"
    )

    publish_automatically = models.BooleanField(
        default=False,
        help_text="If True, publishes content automatically. If False, queues for review."
    )

    # =========================================================================
    # PERFORMANCE TRACKING
    # =========================================================================

    total_episodes_created = models.IntegerField(
        default=0,
        help_text="Total number of episodes created"
    )

    total_views = models.IntegerField(
        default=0,
        help_text="Cumulative views across all episodes"
    )

    total_engagement = models.IntegerField(
        default=0,
        help_text="Cumulative engagement (likes + comments + shares)"
    )

    avg_retention_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average watch time retention (0-100%)"
    )

    # =========================================================================
    # AUTONOMOUS CONTROL (Property #5: Self-Renewal)
    # =========================================================================

    status = models.CharField(
        max_length=20,
        choices=ChannelStatus.choices,
        default=ChannelStatus.ACTIVE,
        help_text="Channel operational status"
    )

    next_content_due = models.DateTimeField(
        help_text="When next episode should be created"
    )

    last_content_created = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When last episode was created"
    )

    # =========================================================================
    # LEARNING CONFIGURATION (Like Session 464 Learning Loop)
    # =========================================================================

    confidence_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(0.5), MaxValueValidator(1.5)],
        help_text="Confidence multiplier (0.5-1.5) based on channel performance"
    )

    # =========================================================================
    # METADATA
    # =========================================================================

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_channel'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['next_content_due']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.content_frequency})"

    def schedule_next_content(self):
        """
        Property #5: Self-Renewal
        Schedules the next content creation cycle based on frequency.
        """
        from datetime import timedelta

        if self.content_frequency == ContentFrequency.DAILY:
            delta = timedelta(days=1)
        elif self.content_frequency == ContentFrequency.WEEKLY:
            delta = timedelta(weeks=1)
        elif self.content_frequency == ContentFrequency.BIWEEKLY:
            delta = timedelta(days=3.5)  # ~2x per week
        elif self.content_frequency == ContentFrequency.MONTHLY:
            delta = timedelta(days=30)
        else:
            delta = timedelta(weeks=1)  # Default to weekly

        self.next_content_due = timezone.now() + delta
        self.save(update_fields=['next_content_due'])

    def is_content_due(self):
        """Check if content creation is due"""
        return self.status == ChannelStatus.ACTIVE and timezone.now() >= self.next_content_due


class ChannelEpisode(models.Model):
    """
    A single piece of content created for a channel.

    Links to AISeries/SeriesEpisode (Session 445) for actual content generation.
    Tracks performance metrics for learning loop.

    Property #4: Outputs with Consequences
    Each episode's performance affects future content decisions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    channel = models.ForeignKey(
        ContentChannel,
        on_delete=models.CASCADE,
        related_name='episodes'
    )

    series = models.ForeignKey(
        'AISeries',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='channel_episodes',
        help_text="Link to AI Series Workflow content (Session 445)"
    )

    # =========================================================================
    # EPISODE INFO
    # =========================================================================

    title = models.CharField(
        max_length=200,
        help_text="Episode title"
    )

    topic = models.CharField(
        max_length=200,
        help_text="What this episode is about (for learning)"
    )

    description = models.TextField(
        blank=True,
        help_text="Episode description"
    )

    # Session 630: Add script field to store generated content
    script = models.TextField(
        blank=True,
        help_text="Generated script/content for this episode"
    )

    publish_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When episode was published"
    )

    platform_url = models.URLField(
        blank=True,
        help_text="URL on publishing platform (YouTube, TikTok, etc.)"
    )

    # =========================================================================
    # PERFORMANCE METRICS (Property #4: Outputs with Consequences)
    # =========================================================================

    views = models.IntegerField(
        default=0,
        help_text="Number of views"
    )

    likes = models.IntegerField(
        default=0,
        help_text="Number of likes"
    )

    comments = models.IntegerField(
        default=0,
        help_text="Number of comments"
    )

    shares = models.IntegerField(
        default=0,
        help_text="Number of shares"
    )

    watch_time_seconds = models.IntegerField(
        default=0,
        help_text="Total watch time in seconds"
    )

    retention_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average watch time retention (0-100%)"
    )

    # =========================================================================
    # LEARNING
    # =========================================================================

    performance_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Calculated performance score (views * retention * engagement)"
    )

    contributed_to_learning = models.BooleanField(
        default=False,
        help_text="Whether this episode's data has been processed for learning"
    )

    # =========================================================================
    # VOICE CRITIQUE SCORES (Session 784)
    # =========================================================================

    # Intent classification - what type of content is this?
    intent_type = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text="Content intent: visionary, technical_deep_dive, operator_diary, contrarian_take, postmortem, behind_the_scenes"
    )

    # Voice quality scores (0-100)
    distinctiveness_score = models.IntegerField(
        default=0,
        help_text="Voice distinctiveness score (0-100): Could this have been written by anyone?"
    )

    specificity_score = models.IntegerField(
        default=0,
        help_text="Specificity score (0-100): Does it use concrete examples vs. generic statements?"
    )

    opinion_strength_score = models.IntegerField(
        default=0,
        help_text="Opinion strength score (0-100): Does it take a real stance or hedge everything?"
    )

    # Generic detector flag
    generic_flag = models.BooleanField(
        default=False,
        help_text="True if content reads like 'every other AI blog' - buzzwords, corporate speak, lack of personality"
    )

    # Has this episode been scored by VoiceCriticAgent?
    voice_critique_completed = models.BooleanField(
        default=False,
        help_text="Whether VoiceCriticAgent has scored this episode"
    )

    # =========================================================================
    # METADATA
    # =========================================================================

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'channel_episode'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['channel', '-created_at']),
            models.Index(fields=['topic']),
            models.Index(fields=['contributed_to_learning']),
            models.Index(fields=['intent_type']),  # Session 784: Voice critique
            models.Index(fields=['voice_critique_completed']),  # Session 784: Voice critique
        ]

    def __str__(self):
        return f"{self.title} ({self.topic})"

    def calculate_performance_score(self):
        """
        Calculate composite performance score.
        Used for learning which topics/styles work best.
        """
        # Normalize metrics to 0-1 scale
        view_score = min(self.views / 10000, 1.0)  # Cap at 10k views
        retention_score = float(self.retention_rate) / 100  # 0-100% to 0-1
        engagement_rate = (self.likes + self.comments + self.shares) / max(self.views, 1)
        engagement_score = min(engagement_rate, 1.0)

        # Weighted composite (50% views, 30% retention, 20% engagement)
        score = (
            view_score * 0.5 +
            retention_score * 0.3 +
            engagement_score * 0.2
        ) * 100  # Scale to 0-100

        self.performance_score = Decimal(str(round(score, 2)))
        self.save(update_fields=['performance_score'])
        return self.performance_score


class TopicPerformance(models.Model):
    """
    Learning data about which topics perform well for a channel.

    Property #1: Persistent Context
    Enables the system to remember: "Space topics get 2x views, aliens get 3x"

    Used by PerformanceAnalystAgent to guide topic selection.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    channel = models.ForeignKey(
        ContentChannel,
        on_delete=models.CASCADE,
        related_name='topic_performance'
    )

    topic = models.CharField(
        max_length=200,
        help_text="Topic keyword or category"
    )

    # =========================================================================
    # PERFORMANCE AGGREGATES
    # =========================================================================

    episode_count = models.IntegerField(
        default=0,
        help_text="Number of episodes about this topic"
    )

    avg_views = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average views for this topic"
    )

    avg_engagement = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average engagement (likes + comments + shares)"
    )

    avg_retention = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average retention rate (0-100%)"
    )

    avg_performance_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average composite performance score"
    )

    # =========================================================================
    # LEARNING
    # =========================================================================

    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(0.5), MaxValueValidator(2.0)],
        help_text="Confidence multiplier (0.5-2.0) - how confident we are this topic works"
    )

    last_tested = models.DateTimeField(
        help_text="When we last created content about this topic"
    )

    # =========================================================================
    # METADATA
    # =========================================================================

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'topic_performance'
        ordering = ['-avg_performance_score']
        unique_together = [['channel', 'topic']]
        indexes = [
            models.Index(fields=['channel', '-avg_performance_score']),
            models.Index(fields=['topic']),
        ]

    def __str__(self):
        return f"{self.topic} (Score: {self.avg_performance_score})"


class ContentDebate(models.Model):
    """
    Records agent debates about content decisions.

    Property #3: Internal Disagreement
    Agents argue, critique, and pressure-test each other before creating content.

    Enables transparency: "Why did the system choose this topic?"
    Answer: "Here's the debate transcript where agents discussed it."
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    channel = models.ForeignKey(
        ContentChannel,
        on_delete=models.CASCADE,
        related_name='debates'
    )

    episode = models.ForeignKey(
        ChannelEpisode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debates',
        help_text="Episode that resulted from this debate (if created)"
    )

    debate_date = models.DateTimeField(auto_now_add=True)

    # =========================================================================
    # PROPOSED TOPIC
    # =========================================================================

    proposed_topic = models.CharField(
        max_length=200,
        help_text="Topic being debated"
    )

    proposed_by = models.CharField(
        max_length=100,
        help_text="Which agent proposed this topic (e.g., 'TopicMinerAgent')"
    )

    # =========================================================================
    # AGENT POSITIONS (Property #3: Internal Disagreement)
    # =========================================================================

    topic_miner_position = models.TextField(
        help_text="TopicMinerAgent's argument (e.g., 'Trending now because...')"
    )

    contrarian_position = models.TextField(
        help_text="ContrarianAgent's argument (e.g., 'Too saturated, try...')"
    )

    analyst_position = models.TextField(
        help_text="PerformanceAnalystAgent's argument (e.g., 'Past data shows...')"
    )

    director_position = models.TextField(
        help_text="CreativeDirectorAgent's argument (e.g., 'Unique angle could be...')"
    )

    # =========================================================================
    # DECISION
    # =========================================================================

    final_decision = models.CharField(
        max_length=200,
        help_text="Final topic decision after debate"
    )

    chosen_angle = models.TextField(
        help_text="Unique angle or approach chosen"
    )

    decision_reasoning = models.TextField(
        help_text="Why this decision was made"
    )

    consensus_reached = models.BooleanField(
        default=False,
        help_text="Whether agents agreed or coordinator had to decide"
    )

    # =========================================================================
    # OUTCOME
    # =========================================================================

    content_created = models.BooleanField(
        default=False,
        help_text="Whether content was actually created from this debate"
    )

    # =========================================================================
    # METADATA
    # =========================================================================

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_debate'
        ordering = ['-debate_date']
        indexes = [
            models.Index(fields=['channel', '-debate_date']),
            models.Index(fields=['proposed_topic']),
        ]

    def __str__(self):
        return f"Debate: {self.proposed_topic} ({self.final_decision})"
