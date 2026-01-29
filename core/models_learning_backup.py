"""
Session 861: Learning Data Backup System

Provides database persistence for learning data that was previously stored
only in Redis. This addresses the MEDIUM RISK data persistence gap where
Redis restart could result in total loss of learning data.

The dual-write pattern ensures data is written to both:
- Redis (for fast, real-time access)
- Database (for persistence and recovery)
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class AgentInteractionRecord(models.Model):
    """
    Database backup for agent interactions stored in Redis.

    Mirrors the AgentInteraction dataclass from agent_learning_service.py
    but provides persistent storage that survives Redis restarts.

    Example:
        record = AgentInteractionRecord.objects.create(
            user_id=123,
            agent_name='ContentWriterAgent',
            interaction_type='rated',
            input_data={'topic': 'AI trends'},
            output_data={'content': '...'},
            rating=5
        )
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User and Agent
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='agent_interactions',
        help_text="User who interacted with the agent"
    )
    user_id_legacy = models.IntegerField(
        null=True, blank=True, db_index=True,
        help_text="Legacy user ID for migration from Redis"
    )
    agent_name = models.CharField(
        max_length=100, db_index=True,
        help_text="Name of the agent"
    )

    # Interaction Details
    INTERACTION_TYPES = [
        ('created', 'Created'),
        ('edited', 'Edited'),
        ('saved', 'Saved'),
        ('shared', 'Shared'),
        ('downloaded', 'Downloaded'),
        ('rated', 'Rated'),
        ('used', 'Used'),
        ('rejected', 'Rejected'),
        ('favorited', 'Favorited'),
    ]
    interaction_type = models.CharField(
        max_length=20, choices=INTERACTION_TYPES, db_index=True,
        help_text="Type of interaction"
    )

    # Data
    input_data = models.JSONField(
        default=dict,
        help_text="Input provided to the agent"
    )
    output_data = models.JSONField(
        default=dict,
        help_text="Output from the agent"
    )

    # Feedback
    rating = models.IntegerField(
        null=True, blank=True,
        help_text="User rating (1-5 stars)"
    )
    was_modified = models.BooleanField(
        default=False,
        help_text="Whether user modified the output"
    )

    # Session tracking
    session_id = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text="Session ID for grouping interactions"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'core_agent_interaction_record'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_name', 'created_at']),
            models.Index(fields=['user', 'agent_name']),
            models.Index(fields=['interaction_type', 'created_at']),
        ]

    def __str__(self):
        rating_str = f" ({self.rating}★)" if self.rating else ""
        return f"{self.agent_name} - {self.interaction_type}{rating_str}"


class LearnedPreferenceRecord(models.Model):
    """
    Database backup for learned preferences stored in Redis.

    Stores user preferences learned from interaction patterns,
    providing persistent storage for personalization data.
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User and Agent
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='learned_preferences',
        help_text="User this preference belongs to"
    )
    user_id_legacy = models.IntegerField(
        null=True, blank=True, db_index=True,
        help_text="Legacy user ID for migration from Redis"
    )
    agent_name = models.CharField(
        max_length=100, db_index=True,
        help_text="Agent this preference applies to"
    )

    # Preference Details
    PREFERENCE_CATEGORIES = [
        ('style', 'Style'),
        ('theme', 'Theme'),
        ('model', 'Model'),
        ('quality', 'Quality'),
        ('format', 'Format'),
        ('color', 'Color'),
        ('mood', 'Mood'),
        ('complexity', 'Complexity'),
    ]
    category = models.CharField(
        max_length=20, choices=PREFERENCE_CATEGORIES, db_index=True,
        help_text="Category of preference"
    )
    value = models.CharField(
        max_length=255,
        help_text="The preference value"
    )

    # Confidence metrics
    confidence = models.FloatField(
        default=0.5,
        help_text="Confidence level (0-1)"
    )
    occurrences = models.IntegerField(
        default=1,
        help_text="Number of times this preference was observed"
    )
    positive_signals = models.IntegerField(
        default=0,
        help_text="Count of positive signals (saved, rated high, etc.)"
    )
    negative_signals = models.IntegerField(
        default=0,
        help_text="Count of negative signals (rejected, edited, etc.)"
    )

    # Timestamps
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_learned_preference_record'
        ordering = ['-confidence', '-occurrences']
        unique_together = ['user', 'agent_name', 'category', 'value']
        indexes = [
            models.Index(fields=['agent_name', 'category']),
            models.Index(fields=['user', 'agent_name']),
        ]

    def __str__(self):
        return f"{self.agent_name} - {self.category}: {self.value} ({self.confidence:.0%})"


class LearningProgressSnapshot(models.Model):
    """
    Periodic snapshots of learning progress metrics from Redis.

    Captures the state of learning:progress:latest and related keys
    at regular intervals for historical tracking and recovery.
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Metrics
    total_quality = models.FloatField(
        default=0.0,
        help_text="Total quality score across all agents"
    )
    total_complexity = models.FloatField(
        default=0.0,
        help_text="Total complexity score"
    )
    total_improvements = models.IntegerField(
        default=0,
        help_text="Total number of improvements made"
    )
    iteration = models.IntegerField(
        default=0,
        help_text="Learning iteration number"
    )

    # Agent-level data
    agent_scores = models.JSONField(
        default=dict,
        help_text="Per-agent quality and complexity scores"
    )

    # Status
    learning_active = models.BooleanField(
        default=False,
        help_text="Whether learning was active when snapshot taken"
    )

    # Timestamp
    snapshot_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'core_learning_progress_snapshot'
        ordering = ['-snapshot_at']
        get_latest_by = 'snapshot_at'

    def __str__(self):
        return f"Snapshot {self.snapshot_at.isoformat()} - iter {self.iteration}"


class AgentImprovementRecord(models.Model):
    """
    Database backup for agent improvement data from Redis.

    Captures agent:{agent_name}:improvement:{iteration} data
    for persistence and analysis.
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Agent and iteration
    agent_name = models.CharField(
        max_length=100, db_index=True,
        help_text="Name of the agent"
    )
    iteration = models.IntegerField(
        db_index=True,
        help_text="Learning iteration number"
    )

    # Improvement data
    stage = models.CharField(
        max_length=100, blank=True,
        help_text="Learning stage/focus"
    )
    quality_score = models.FloatField(
        default=0.0,
        help_text="Quality score for this iteration"
    )
    complexity_score = models.FloatField(
        default=0.0,
        help_text="Complexity score for this iteration"
    )

    # Additional metrics
    metrics = models.JSONField(
        default=dict,
        help_text="Additional improvement metrics"
    )

    # Timestamp
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'core_agent_improvement_record'
        ordering = ['-recorded_at']
        unique_together = ['agent_name', 'iteration']
        indexes = [
            models.Index(fields=['agent_name', 'iteration']),
        ]

    def __str__(self):
        return f"{self.agent_name} iter {self.iteration}: Q={self.quality_score:.2f}"


# Helper functions for dual-write pattern

def backup_interaction(
    user_id: int,
    agent_name: str,
    interaction_type: str,
    input_data: dict,
    output_data: dict,
    rating: int = None,
    was_modified: bool = False,
    session_id: str = '',
    user=None,
) -> AgentInteractionRecord:
    """
    Session 861: Backup an interaction to the database.

    Call this alongside Redis writes to ensure persistence.

    Args:
        user_id: Legacy user ID from Redis
        agent_name: Name of the agent
        interaction_type: Type of interaction
        input_data: Input provided to agent
        output_data: Output from agent
        rating: Optional user rating
        was_modified: Whether user modified output
        session_id: Optional session ID
        user: Optional User model instance

    Returns:
        AgentInteractionRecord instance
    """
    return AgentInteractionRecord.objects.create(
        user=user,
        user_id_legacy=user_id if not user else None,
        agent_name=agent_name,
        interaction_type=interaction_type,
        input_data=input_data or {},
        output_data=output_data or {},
        rating=rating,
        was_modified=was_modified,
        session_id=session_id or '',
    )


def backup_learning_progress(
    total_quality: float,
    total_complexity: float,
    total_improvements: int,
    iteration: int = 0,
    agent_scores: dict = None,
    learning_active: bool = False,
) -> LearningProgressSnapshot:
    """
    Session 861: Create a snapshot of learning progress.

    Call periodically (e.g., every 5 minutes) to persist Redis state.

    Returns:
        LearningProgressSnapshot instance
    """
    return LearningProgressSnapshot.objects.create(
        total_quality=total_quality,
        total_complexity=total_complexity,
        total_improvements=total_improvements,
        iteration=iteration,
        agent_scores=agent_scores or {},
        learning_active=learning_active,
    )


def backup_agent_improvement(
    agent_name: str,
    iteration: int,
    stage: str = '',
    quality_score: float = 0.0,
    complexity_score: float = 0.0,
    metrics: dict = None,
) -> AgentImprovementRecord:
    """
    Session 861: Backup agent improvement data.

    Returns:
        AgentImprovementRecord instance
    """
    record, created = AgentImprovementRecord.objects.update_or_create(
        agent_name=agent_name,
        iteration=iteration,
        defaults={
            'stage': stage,
            'quality_score': quality_score,
            'complexity_score': complexity_score,
            'metrics': metrics or {},
        }
    )
    return record
