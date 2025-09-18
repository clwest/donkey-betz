"""
Agent Execution Memory Models
============================

Tracks agent performance and success patterns for intelligent recommendation.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class AgentExecutionMemory(models.Model):
    """
    Tracks individual agent executions and their success rates.

    This allows the assistant to remember which agents work best for specific
    tasks and users, enabling intelligent agent recommendations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_memories')

    # Agent identification
    agent_name = models.CharField(max_length=100, db_index=True)
    agent_id = models.CharField(max_length=100, null=True, blank=True)  # Registry ID

    # Task information
    task_type = models.CharField(max_length=50, db_index=True)  # "blog_writing", "data_analysis", etc.
    task_description = models.TextField()
    original_prompt = models.TextField()

    # Execution results
    success_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Success score from 0.0 (failed) to 1.0 (perfect)"
    )
    execution_time_seconds = models.FloatField(null=True, blank=True)

    # Outcome tracking
    outcome_description = models.TextField(
        help_text="Human-readable description of what the agent accomplished"
    )
    outcome_metrics = models.JSONField(
        default=dict,
        help_text="Quantifiable metrics like views, clicks, conversions, etc."
    )

    # User feedback
    user_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User's 1-5 star rating of the result"
    )
    user_feedback = models.TextField(null=True, blank=True)

    # Context
    page_context = models.CharField(max_length=100, null=True, blank=True)
    conversation_id = models.CharField(max_length=100, null=True, blank=True)

    # Timestamps
    execution_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'task_type', '-success_score']),
            models.Index(fields=['user', 'agent_name', '-execution_date']),
            models.Index(fields=['task_type', '-success_score']),
            models.Index(fields=['-execution_date']),
        ]
        ordering = ['-execution_date']

    def __str__(self):
        return f"{self.agent_name} - {self.task_type} ({self.success_score:.1f})"


class AgentRecommendation(models.Model):
    """
    Pre-computed agent recommendations based on execution history.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_recommendations')

    task_type = models.CharField(max_length=50, db_index=True)
    recommended_agent = models.CharField(max_length=100)

    # Recommendation strength
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    avg_success_rate = models.FloatField()
    total_executions = models.IntegerField()

    # Best outcome example
    best_outcome_description = models.TextField()
    best_outcome_metrics = models.JSONField(default=dict)

    # Cache invalidation
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'task_type', 'recommended_agent']
        indexes = [
            models.Index(fields=['user', 'task_type', '-confidence_score']),
        ]
        ordering = ['-confidence_score']

    def __str__(self):
        return f"{self.user.username}: {self.recommended_agent} for {self.task_type}"


class AgentPerformanceStats(models.Model):
    """
    Aggregated performance statistics for agents across all users.
    """

    agent_name = models.CharField(max_length=100, unique=True, primary_key=True)

    # Overall stats
    total_executions = models.IntegerField(default=0)
    avg_success_rate = models.FloatField(default=0.0)
    avg_execution_time = models.FloatField(default=0.0)

    # Task type breakdown
    task_type_stats = models.JSONField(
        default=dict,
        help_text="Performance breakdown by task type"
    )

    # Best results
    highest_rated_execution = models.ForeignKey(
        AgentExecutionMemory,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent_name} ({self.avg_success_rate:.1%} success)"