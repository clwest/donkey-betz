"""
Session 861: Decision Recording System

Provides always-on decision recording for agents. Unlike the TimeTravelMixin
which requires explicit session management, this model records ALL decisions
automatically for audit trail and debugging.

This addresses the MEDIUM RISK data persistence gap where ~90% of agent
decisions were not recorded because trace_id was opt-in.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class DecisionRecord(models.Model):
    """
    Records agent decisions automatically - always on.

    This is a simpler model than DecisionPoint/AgentSession for cases where
    you just want to record what decisions agents made without the full
    time travel debugging infrastructure.

    Example:
        from core.models_decision_records import DecisionRecord

        DecisionRecord.record(
            agent_name='StockAnalystAgent',
            decision_type='tool_call',
            action='Calling analyze_filing',
            reasoning='LLM requested SEC filing analysis',
            confidence=0.9
        )
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tracing
    trace_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Trace ID for linking related decisions"
    )
    conversation_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Conversation ID if from chat context"
    )

    # Agent info
    agent_name = models.CharField(
        max_length=255, db_index=True,
        help_text="Name of the agent that made the decision"
    )

    # Decision details
    DECISION_TYPES = [
        ('analysis', 'Analysis'),
        ('selection', 'Selection'),
        ('action', 'Action'),
        ('tool_call', 'Tool Call'),
        ('delegation', 'Delegation'),
        ('output', 'Output Generation'),
        ('validation', 'Validation'),
        ('error_handling', 'Error Handling'),
        ('other', 'Other'),
    ]
    decision_type = models.CharField(
        max_length=50, db_index=True,
        help_text="Type of decision"
    )
    action = models.TextField(
        help_text="The action taken"
    )
    reasoning = models.TextField(
        blank=True,
        help_text="Why this decision was made"
    )

    # Alternatives considered
    alternatives = models.JSONField(
        default=list,
        help_text="Other options that were considered"
    )

    # Context
    context = models.JSONField(
        default=dict,
        help_text="Additional context for this decision"
    )
    task_summary = models.CharField(
        max_length=500, blank=True,
        help_text="Summary of the task being executed"
    )

    # Metrics
    confidence = models.FloatField(
        default=0.8,
        help_text="Confidence score (0-1)"
    )

    # Outcome tracking
    was_successful = models.BooleanField(
        null=True, blank=True,
        help_text="Whether the decision led to success (set after completion)"
    )
    outcome_notes = models.TextField(
        blank=True,
        help_text="Notes about the outcome"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'core_decision_record'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_name', 'created_at']),
            models.Index(fields=['decision_type', 'created_at']),
            models.Index(fields=['trace_id', 'created_at']),
        ]

    def __str__(self):
        return f"{self.agent_name}: {self.decision_type} - {self.action[:50]}"

    @classmethod
    def record(
        cls,
        agent_name: str,
        decision_type: str,
        action: str,
        reasoning: str = '',
        alternatives: list = None,
        context: dict = None,
        confidence: float = 0.8,
        trace_id: str = None,
        conversation_id: str = None,
        task_summary: str = '',
    ) -> 'DecisionRecord':
        """
        Convenience method to record a decision.

        Args:
            agent_name: Name of the agent making the decision
            decision_type: Type of decision (analysis, selection, etc.)
            action: The action taken
            reasoning: Why this decision was made
            alternatives: Other options considered
            context: Additional context
            confidence: Confidence score (0-1)
            trace_id: Optional trace ID for linking
            conversation_id: Optional conversation ID
            task_summary: Optional summary of the task

        Returns:
            DecisionRecord instance
        """
        # Parse UUIDs
        trace_uuid = None
        if trace_id:
            try:
                trace_uuid = uuid.UUID(str(trace_id))
            except (ValueError, TypeError):
                pass

        conv_uuid = None
        if conversation_id:
            try:
                conv_uuid = uuid.UUID(str(conversation_id))
            except (ValueError, TypeError):
                pass

        return cls.objects.create(
            agent_name=agent_name,
            decision_type=decision_type,
            action=action[:2000] if action else '',  # Truncate to reasonable size
            reasoning=reasoning[:2000] if reasoning else '',
            alternatives=alternatives or [],
            context=context or {},
            confidence=confidence,
            trace_id=trace_uuid,
            conversation_id=conv_uuid,
            task_summary=task_summary[:500] if task_summary else '',
        )

    def mark_outcome(self, success: bool, notes: str = ''):
        """Mark the outcome of this decision."""
        self.was_successful = success
        self.outcome_notes = notes
        self.save(update_fields=['was_successful', 'outcome_notes'])


class DecisionAggregate(models.Model):
    """
    Aggregated statistics for decisions by agent and type.

    Updated periodically to provide quick access to:
    - Decision counts per agent/type
    - Success rates
    - Confidence patterns
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Aggregation key
    agent_name = models.CharField(max_length=255, db_index=True)
    decision_type = models.CharField(max_length=50, db_index=True)
    date = models.DateField(db_index=True)

    # Counts
    total_decisions = models.IntegerField(default=0)
    successful_decisions = models.IntegerField(default=0)
    failed_decisions = models.IntegerField(default=0)
    pending_decisions = models.IntegerField(default=0)

    # Confidence stats
    avg_confidence = models.FloatField(default=0.0)
    min_confidence = models.FloatField(default=0.0)
    max_confidence = models.FloatField(default=0.0)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_decision_aggregate'
        unique_together = ['agent_name', 'decision_type', 'date']
        ordering = ['-date', 'agent_name']

    def __str__(self):
        rate = (self.successful_decisions / self.total_decisions * 100) if self.total_decisions > 0 else 0
        return f"{self.agent_name} {self.decision_type} ({self.date}): {self.total_decisions} decisions, {rate:.1f}% success"

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        evaluated = self.successful_decisions + self.failed_decisions
        if evaluated == 0:
            return 0.0
        return (self.successful_decisions / evaluated) * 100
