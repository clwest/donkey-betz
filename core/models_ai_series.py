"""
AI Series Models - Session 445

Models for managing multi-episode content series created by AISeriesWorkflowAgent.

Models:
- AISeries: A complete content series project (educational, entertainment, marketing)
- SeriesEpisode: Individual episode within a series
- SeriesCharacter: Character definitions for consistency across episodes

Design Decisions:
- Episode count: 1-5 per series (starting conservative)
- Series types: educational, entertainment, marketing
- Sequential generation (one episode at a time for story continuity)
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

class SeriesType(models.TextChoices):
    """Types of content series"""
    EDUCATIONAL = 'educational', 'Educational - Tutorials, explainers, how-tos'
    ENTERTAINMENT = 'entertainment', 'Entertainment - Cartoons, stories, shorts'
    MARKETING = 'marketing', 'Marketing - Ad campaigns, brand series'


class SeriesStatus(models.TextChoices):
    """Series lifecycle status"""
    PLANNING = 'planning', 'Planning - Research and structure'
    GENERATING = 'generating', 'Generating - Creating episodes'
    COMPLETE = 'complete', 'Complete - All episodes ready'
    FAILED = 'failed', 'Failed - Generation error'


class EpisodeStatus(models.TextChoices):
    """Episode lifecycle status"""
    QUEUED = 'queued', 'Queued - Waiting to generate'
    GENERATING = 'generating', 'Generating - Currently creating'
    COMPLETE = 'complete', 'Complete - Ready for delivery'
    FAILED = 'failed', 'Failed - Generation error'


# =============================================================================
# MODELS
# =============================================================================

class AISeries(models.Model):
    """
    A complete AI-generated content series.

    Represents a multi-episode series like:
    - "AI Explained for Kids" (5 educational episodes)
    - "Space Adventures" (3 entertainment episodes)
    - "Brand Story Campaign" (3 marketing episodes)

    The AISeriesWorkflowAgent orchestrates creation by:
    1. Researching the topic/niche
    2. Planning episode arcs
    3. Locking character designs and style
    4. Generating episodes sequentially
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic Info
    name = models.CharField(max_length=200, help_text="Series title")
    description = models.TextField(blank=True, help_text="Series description/concept")
    prompt = models.TextField(help_text="Original creation prompt from user")

    # Series Configuration
    series_type = models.CharField(
        max_length=20,
        choices=SeriesType.choices,
        default=SeriesType.EDUCATIONAL
    )
    episode_count = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Number of episodes (1-5)"
    )
    target_audience = models.CharField(
        max_length=100,
        blank=True,
        help_text="Target audience description"
    )

    # Style Configuration (locked for consistency)
    style_config = models.JSONField(
        default=dict,
        help_text="Locked visual style settings for consistency"
    )
    # Example: {"style_preset": "pixar", "color_palette": ["#FF6B6B", "#4ECDC4"], "art_direction": "friendly, colorful"}

    # Character Configuration
    character_config = models.JSONField(
        default=dict,
        help_text="Character definitions for consistency"
    )
    # Example: {"main_character": {"name": "Luna", "description": "friendly robot"}, "supporting": [...]}

    # Story Arc
    story_arc = models.JSONField(
        default=dict,
        help_text="Overall story arc and episode summaries"
    )
    # Example: {"theme": "learning about space", "arc": "intro → exploration → conclusion", "episodes": [...]}

    # Research Data (from ResearchAgent)
    research_data = models.JSONField(
        default=dict,
        help_text="Research gathered during planning phase"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=SeriesStatus.choices,
        default=SeriesStatus.PLANNING
    )
    current_episode = models.IntegerField(
        default=0,
        help_text="Current episode being generated (0 = planning)"
    )
    generation_progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall progress percentage"
    )

    # Error Tracking
    error_message = models.TextField(blank=True)
    error_stage = models.CharField(max_length=50, blank=True)

    # Cost Tracking
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000'),
        help_text="Total API costs for series generation"
    )
    cost_breakdown = models.JSONField(
        default=dict,
        help_text="Cost per episode"
    )

    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_series'
    )

    # Discord Integration
    discord_message_id = models.CharField(max_length=100, blank=True, null=True)
    discord_channel_id = models.CharField(max_length=100, blank=True, null=True)

    # Celery Task Tracking
    celery_task_id = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    planning_completed_at = models.DateTimeField(null=True, blank=True)
    generation_started_at = models.DateTimeField(null=True, blank=True)
    generation_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "AI Series"
        indexes = [
            models.Index(fields=['series_type', 'status']),
            models.Index(fields=['created_by', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_series_type_display()}) - {self.episode_count} episodes"

    def start_planning(self):
        """Mark series as in planning phase."""
        self.status = SeriesStatus.PLANNING
        self.save(update_fields=['status', 'updated_at'])

    def complete_planning(self, research_data: dict, story_arc: dict, style_config: dict, character_config: dict):
        """Complete planning phase with all configuration."""
        self.research_data = research_data
        self.story_arc = story_arc
        self.style_config = style_config
        self.character_config = character_config
        self.planning_completed_at = timezone.now()
        self.save(update_fields=[
            'research_data', 'story_arc', 'style_config', 'character_config',
            'planning_completed_at', 'updated_at'
        ])

    def start_generation(self):
        """Start episode generation."""
        self.status = SeriesStatus.GENERATING
        self.generation_started_at = timezone.now()
        self.save(update_fields=['status', 'generation_started_at', 'updated_at'])

    def advance_episode(self):
        """Move to next episode."""
        self.current_episode += 1
        self.generation_progress = int((self.current_episode / self.episode_count) * 100)
        self.save(update_fields=['current_episode', 'generation_progress', 'updated_at'])

    def complete_generation(self):
        """Mark series as complete."""
        self.status = SeriesStatus.COMPLETE
        self.generation_progress = 100
        self.generation_completed_at = timezone.now()
        self.save(update_fields=['status', 'generation_progress', 'generation_completed_at', 'updated_at'])

    def fail(self, error: str, stage: str = ''):
        """Mark series as failed."""
        self.status = SeriesStatus.FAILED
        self.error_message = error
        self.error_stage = stage
        self.save(update_fields=['status', 'error_message', 'error_stage', 'updated_at'])

    def add_cost(self, episode_number: int, cost: Decimal):
        """Add cost for an episode."""
        self.total_cost += cost
        if not self.cost_breakdown:
            self.cost_breakdown = {}
        self.cost_breakdown[str(episode_number)] = float(cost)
        self.save(update_fields=['total_cost', 'cost_breakdown', 'updated_at'])


class SeriesEpisode(models.Model):
    """
    Individual episode within an AI series.

    Each episode is generated as a ContentPackage but tracked
    separately for series-level management.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(
        AISeries,
        on_delete=models.CASCADE,
        related_name='episodes'
    )

    # Episode Info
    episode_number = models.IntegerField(help_text="Episode number (1-5)")
    title = models.CharField(max_length=200, help_text="Episode title")
    synopsis = models.TextField(blank=True, help_text="Episode synopsis/summary")
    script = models.TextField(blank=True, help_text="Episode script/narration")

    # Story Arc Position
    arc_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position in story arc (intro, rising, climax, falling, conclusion)"
    )

    # Link to ContentPackage
    content_package = models.ForeignKey(
        'core.ContentPackage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='series_episodes',
        help_text="The ContentPackage containing episode assets"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=EpisodeStatus.choices,
        default=EpisodeStatus.QUEUED
    )
    generation_order = models.IntegerField(
        default=0,
        help_text="Order in generation queue"
    )

    # Generation Results (per-stage results)
    research_result = models.JSONField(null=True, blank=True)
    script_result = models.JSONField(null=True, blank=True)
    character_result = models.JSONField(null=True, blank=True)
    voice_result = models.JSONField(null=True, blank=True)
    video_result = models.JSONField(null=True, blank=True)

    # Error Tracking
    error_message = models.TextField(blank=True)
    error_stage = models.CharField(max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generation_started_at = models.DateTimeField(null=True, blank=True)
    generation_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['series', 'episode_number']
        unique_together = [['series', 'episode_number']]

    def __str__(self):
        return f"{self.series.name} - Episode {self.episode_number}: {self.title}"

    def start_generation(self):
        """Mark episode as generating."""
        self.status = EpisodeStatus.GENERATING
        self.generation_started_at = timezone.now()
        self.save(update_fields=['status', 'generation_started_at', 'updated_at'])

    def complete_generation(self, content_package=None):
        """Mark episode as complete."""
        self.status = EpisodeStatus.COMPLETE
        self.generation_completed_at = timezone.now()
        if content_package:
            self.content_package = content_package
        self.save(update_fields=['status', 'generation_completed_at', 'content_package', 'updated_at'])

    def fail(self, error: str, stage: str = ''):
        """Mark episode as failed."""
        self.status = EpisodeStatus.FAILED
        self.error_message = error
        self.error_stage = stage
        self.save(update_fields=['status', 'error_message', 'error_stage', 'updated_at'])


class SeriesCharacter(models.Model):
    """
    Character definition for series consistency.

    Stores character details to ensure visual and narrative
    consistency across all episodes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(
        AISeries,
        on_delete=models.CASCADE,
        related_name='characters'
    )

    # Character Info
    name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=50,
        help_text="main, supporting, recurring, guest"
    )
    description = models.TextField(help_text="Character description for image generation")

    # Visual Definition
    visual_prompt = models.TextField(
        blank=True,
        help_text="Detailed prompt for consistent image generation"
    )
    reference_image_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Reference image ID for consistency"
    )
    reference_image_url = models.URLField(blank=True, null=True)

    # Voice Definition
    voice_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ElevenLabs voice ID for this character"
    )
    voice_name = models.CharField(max_length=100, blank=True)

    # Personality
    personality_traits = models.JSONField(
        default=list,
        help_text="List of personality traits"
    )
    catchphrases = models.JSONField(
        default=list,
        help_text="Character catchphrases for dialogue"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['series', 'role', 'name']

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.series.name}"
