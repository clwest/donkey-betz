"""
Learning Readback Events — telemetry for learning loop closure.

Records every PA routing decision and whether learning signals
influenced it. Enables answering: "Is the platform actually learning?"

Phase 1: Write-only telemetry (prove signals exist)
Phase 2: Read back to inform routing decisions
"""

from django.conf import settings
from django.db import models

from core.models.base.models import UnifiedBaseModel


class LearningReadbackEvent(UnifiedBaseModel):
    """
    One row per PA routing decision.

    Tracks whether UserAgentLearning data was consulted,
    what it recommended, and whether the recommendation was followed.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_readback_events',
    )
    trace_id = models.CharField(max_length=100, db_index=True)
    message_snippet = models.CharField(
        max_length=200,
        help_text="First 200 chars of user message (for debugging)",
    )

    # What routing decided
    intent = models.CharField(max_length=100, null=True, blank=True)
    routed_to = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="Tool/agent that was selected",
    )

    # Learning influence
    learning_consulted = models.BooleanField(
        default=False,
        help_text="Whether UserAgentLearning was queried",
    )
    learning_used = models.BooleanField(
        default=False,
        help_text="Whether learning actually changed the routing decision",
    )
    learning_record_ids = models.JSONField(
        default=list, blank=True,
        help_text="UUIDs of UserAgentLearning records that were consulted",
    )
    learning_explanation = models.TextField(
        blank=True, default='',
        help_text="Human-readable explanation of learning influence",
    )

    # Outcome tracking (filled in later if available)
    tool_ok = models.BooleanField(
        null=True,
        help_text="Whether the tool execution succeeded",
    )
    latency_ms = models.IntegerField(
        null=True,
        help_text="Tool execution latency",
    )

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['learning_used', '-created_at']),
        ]

    def __str__(self):
        status = "used" if self.learning_used else ("consulted" if self.learning_consulted else "none")
        return f"Readback {self.trace_id} → {self.routed_to} (learning={status})"
