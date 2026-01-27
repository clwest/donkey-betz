"""
Session 555 - Phase A: Extracted Artifact Models

Actionable items extracted from agent conversations:
- Proposals
- Experiments
- Risks
- Data/Pipeline specs
- Open questions
- Action items
- Key insights

Note: Named ExtractedArtifact to avoid conflict with existing ConversationArtifact
model from Session 261 which stores structured outputs.
"""

import uuid
from django.db import models
from django.utils import timezone


class ExtractedArtifact(models.Model):
    """
    An actionable item extracted from an agent conversation.

    These flow into the Boardroom as "Proposals Awaiting Decision"
    alongside Dreams.

    Distinguished from ConversationArtifact (Session 261) which stores
    structured outputs. This model focuses on actionable proposals
    that require human decision.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Session 843: Orchestration Contract fields
    trace_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Session 843: Trace ID for cross-artifact linking"
    )
    project = models.ForeignKey(
        'core.PartnershipProject',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='extracted_artifacts',
        help_text="Session 843: Project this artifact belongs to"
    )

    # Source conversation
    conversation = models.ForeignKey(
        'AgentConversation',
        on_delete=models.CASCADE,
        related_name='extracted_artifacts'
    )
    extracted_at = models.DateTimeField(auto_now_add=True)

    # Artifact type
    ARTIFACT_TYPES = [
        ('proposal', 'Proposal'),           # "We should do X"
        ('experiment', 'Experiment'),       # "Test X vs Y"
        ('risk', 'Risk Identified'),        # "Risk: X could happen"
        ('data_spec', 'Data/Pipeline Spec'),# Technical specification
        ('question', 'Open Question'),      # "We need to decide X"
        ('insight', 'Key Insight'),         # Important observation
        ('action_item', 'Action Item'),     # "Someone needs to do X"
    ]
    artifact_type = models.CharField(max_length=20, choices=ARTIFACT_TYPES)

    # Content
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Attribution
    source_agent = models.ForeignKey(
        'Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proposed_extracted_artifacts'
    )
    source_message_index = models.IntegerField(
        null=True,
        blank=True,
        help_text="Index of message in conversation where this was proposed"
    )

    # Structured details (type-specific)
    details = models.JSONField(default=dict, blank=True)
    # Examples:
    # For experiment: {"hypothesis": "...", "metrics": [...], "duration": "4 weeks"}
    # For risk: {"severity": "high", "mitigation": "...", "likelihood": "medium"}
    # For data_spec: {"components": [...], "technologies": [...]}
    # For proposal: {"steps": [...], "resources": [...], "timeline": "..."}

    # Decision tracking
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
        ('implemented', 'Implemented'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        'core.UnifiedUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='extracted_artifact_decisions'
    )
    decision_notes = models.TextField(blank=True)

    # Scoring
    importance_score = models.FloatField(
        default=0.5,
        help_text="0-1, how important is this artifact"
    )
    urgency_score = models.FloatField(
        default=0.5,
        help_text="0-1, how urgent is this artifact"
    )
    confidence_score = models.FloatField(
        default=0.5,
        help_text="0-1, extraction confidence"
    )

    # Composite score for ranking
    composite_score = models.FloatField(
        default=0.5,
        help_text="Combined score for ranking in queue"
    )

    class Meta:
        ordering = ['-extracted_at']
        indexes = [
            models.Index(fields=['status', 'artifact_type']),
            models.Index(fields=['composite_score']),
            models.Index(fields=['conversation', 'artifact_type']),
        ]
        verbose_name = 'Extracted Artifact'
        verbose_name_plural = 'Extracted Artifacts'

    def __str__(self):
        return f"[{self.get_artifact_type_display()}] {self.title[:50]}"

    def save(self, *args, **kwargs):
        # Calculate composite score
        self.composite_score = (
            self.importance_score * 0.4 +
            self.urgency_score * 0.3 +
            self.confidence_score * 0.3
        )
        super().save(*args, **kwargs)

    def approve(self, user=None, notes=''):
        """Mark artifact as approved."""
        self.status = 'approved'
        self.decided_at = timezone.now()
        self.decided_by = user
        self.decision_notes = notes
        self.save()

    def reject(self, user=None, notes=''):
        """Mark artifact as rejected."""
        self.status = 'rejected'
        self.decided_at = timezone.now()
        self.decided_by = user
        self.decision_notes = notes
        self.save()

    def defer(self, user=None, notes=''):
        """Mark artifact as deferred for later."""
        self.status = 'deferred'
        self.decided_at = timezone.now()
        self.decided_by = user
        self.decision_notes = notes
        self.save()


class ArtifactExtractionLog(models.Model):
    """
    Log of extraction runs for debugging and monitoring.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        'AgentConversation',
        on_delete=models.CASCADE,
        related_name='extraction_logs'
    )

    extracted_at = models.DateTimeField(auto_now_add=True)

    # Results
    artifacts_found = models.IntegerField(default=0)
    extraction_time_ms = models.IntegerField(default=0)

    # Status
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)

    # Raw extraction data for debugging
    raw_response = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-extracted_at']
        verbose_name = 'Artifact Extraction Log'
        verbose_name_plural = 'Artifact Extraction Logs'

    def __str__(self):
        return f"Extraction for {self.conversation_id}: {self.status} ({self.artifacts_found} found)"


class ArtifactExecution(models.Model):
    """
    Session 555 - Phase B: Tracks execution attempts for approved artifacts.

    When an artifact is approved in the Boardroom, this model tracks
    the execution attempt(s) - which agent handled it, success/failure,
    and the resulting output.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the approved artifact
    artifact = models.ForeignKey(
        ExtractedArtifact,
        on_delete=models.CASCADE,
        related_name='executions'
    )

    # Execution details
    agent_name = models.CharField(max_length=100)
    task_description = models.TextField()
    context = models.JSONField(default=dict, blank=True)

    # Status tracking
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')

    # Results
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Metrics
    execution_time_ms = models.IntegerField(null=True, blank=True)
    tokens_used = models.IntegerField(default=0)

    # Timestamps
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-queued_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['artifact', 'status']),
        ]
        verbose_name = 'Artifact Execution'
        verbose_name_plural = 'Artifact Executions'

    def __str__(self):
        return f"Execution of '{self.artifact.title[:30]}' via {self.agent_name}: {self.status}"

    @property
    def duration_seconds(self):
        """Calculate execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class WeeklySynthesis(models.Model):
    """
    Session 555 - Phase C: Weekly executive summary.

    Aggregates artifacts, decisions, and executions into
    a comprehensive digest delivered to Discord #boardroom.

    Generated every Sunday at 8 AM via Celery Beat.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Period covered
    period_start = models.DateField()
    period_end = models.DateField()

    # Artifacts section
    artifacts_extracted = models.IntegerField(default=0)
    artifacts_by_type = models.JSONField(default=dict)  # {proposal: 5, risk: 3}
    artifacts_by_status = models.JSONField(default=dict)  # {pending: 2, approved: 5}
    top_artifacts = models.JSONField(default=list)  # High priority items

    # Decisions section
    decisions_approved = models.IntegerField(default=0)
    decisions_rejected = models.IntegerField(default=0)
    decisions_deferred = models.IntegerField(default=0)

    # Execution section
    executions_total = models.IntegerField(default=0)
    executions_succeeded = models.IntegerField(default=0)
    executions_failed = models.IntegerField(default=0)
    execution_success_rate = models.FloatField(default=0.0)
    avg_execution_time_ms = models.IntegerField(default=0)

    # Agent activity
    most_active_agents = models.JSONField(default=list)  # [{agent, count}]
    agent_success_rates = models.JSONField(default=dict)  # {agent: rate}

    # AI-generated insights
    trend_analysis = models.TextField(blank=True)  # GPT-5-mini summary
    key_themes = models.JSONField(default=list)  # Extracted themes
    recommendations = models.JSONField(default=list)  # Action items

    # Pending items requiring attention
    pending_high_priority = models.IntegerField(default=0)
    oldest_pending_days = models.IntegerField(default=0)

    # Discord delivery
    posted_to_discord = models.BooleanField(default=False)
    discord_message_id = models.CharField(max_length=100, blank=True)

    # Full markdown report
    report_markdown = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_end']
        verbose_name = 'Weekly Synthesis'
        verbose_name_plural = 'Weekly Syntheses'

    def __str__(self):
        return f"Weekly Synthesis: {self.period_start} to {self.period_end}"


class ReviewDocument(models.Model):
    """
    Session 555 - Phase D: Interactive decision brief with side chats.

    For any artifact awaiting human decision, generates:
    - Neutral summary
    - Pro case (arguments FOR)
    - Con case (arguments AGAINST)
    - Open questions
    - AI recommendation

    Supports "Ask Pro" / "Ask Con" mini-chats before decision.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Target (polymorphic - can review any type)
    TARGET_TYPES = [
        ('artifact', 'Extracted Artifact'),
        ('dream', 'Agent Dream'),
        ('project', 'Creative Project'),
        ('decision', 'Agent Decision'),
        ('experiment', 'Experiment'),
    ]
    target_type = models.CharField(max_length=50, choices=TARGET_TYPES)
    target_id = models.UUIDField()  # ID of the thing being reviewed

    # Content sections
    neutral_summary = models.TextField()
    pro_case = models.TextField()  # Arguments FOR
    con_case = models.TextField()  # Arguments AGAINST
    open_questions = models.JSONField(default=list)  # List of unresolved questions
    key_evidence = models.JSONField(default=dict)  # {pro: [...], con: [...]}

    # AI recommendation
    AI_LEAN_CHOICES = [
        ('strong_approve', 'Strong Approve'),
        ('lean_approve', 'Lean Approve'),
        ('neutral', 'Neutral - Need More Info'),
        ('lean_decline', 'Lean Decline'),
        ('strong_decline', 'Strong Decline'),
        ('pilot', 'Narrow Pilot First'),
        ('defer', 'Defer - Not Now'),
    ]
    ai_recommendation = models.TextField()  # Detailed recommendation
    ai_lean = models.CharField(max_length=30, choices=AI_LEAN_CHOICES)
    ai_confidence = models.FloatField(default=0.5)  # 0-1

    # Status workflow
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('awaiting_human', 'Awaiting Human Review'),
        ('approved', 'Approved'),
        ('approved_with_conditions', 'Approved with Conditions'),
        ('declined', 'Declined'),
        ('deferred', 'Deferred'),
    ]
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='awaiting_human')

    # Human decision
    decision_conditions = models.TextField(blank=True)  # If approved_with_conditions
    decision_reasoning = models.TextField(blank=True)  # Human's stated reasoning
    decided_by = models.ForeignKey(
        'UnifiedUser', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='review_decisions'
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    # Interaction tracking
    questions_asked_pro = models.IntegerField(default=0)
    questions_asked_con = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Review Document'
        verbose_name_plural = 'Review Documents'

    def __str__(self):
        return f"Review: {self.target_type} - {self.status}"


class SideChat(models.Model):
    """
    Session 555 - Phase D: Conversation with Pro or Con side.

    Tracks multi-turn Q&A with each perspective.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    review_document = models.ForeignKey(
        ReviewDocument, on_delete=models.CASCADE, related_name='side_chats'
    )

    SIDE_CHOICES = [
        ('pro', 'Pro Side'),
        ('con', 'Con Side'),
    ]
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)

    # Conversation history
    messages = models.JSONField(default=list)  # [{role, content, timestamp}]

    # Metadata
    started_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    message_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['review_document', 'side']
        verbose_name = 'Side Chat'
        verbose_name_plural = 'Side Chats'

    def __str__(self):
        return f"{self.get_side_display()} chat for {self.review_document}"

    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        from django.utils import timezone
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': timezone.now().isoformat()
        })
        self.message_count = len(self.messages)
        self.save()
