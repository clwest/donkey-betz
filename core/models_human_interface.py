"""
Human Interface Layer - Data Models
====================================

Session 686: The Human layer connecting the operator to the autonomous AI ecosystem.

These models capture:
1. Attention items requiring human review
2. Human decisions and feedback
3. Human preferences (learned and explicit)
4. Control actions for audit trail
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class HumanAttentionItem(models.Model):
    """An item requiring human attention from any system source."""

    # Urgency levels
    URGENCY_CRITICAL = 'critical'
    URGENCY_HIGH = 'high'
    URGENCY_MEDIUM = 'medium'
    URGENCY_LOW = 'low'
    URGENCY_CHOICES = [
        (URGENCY_CRITICAL, 'Critical'),
        (URGENCY_HIGH, 'High'),
        (URGENCY_MEDIUM, 'Medium'),
        (URGENCY_LOW, 'Low'),
    ]

    # Status states
    STATUS_PENDING = 'pending'
    STATUS_VIEWED = 'viewed'
    STATUS_ACTED = 'acted'
    STATUS_DEFERRED = 'deferred'
    STATUS_IGNORED = 'ignored'
    STATUS_EXPIRED = 'expired'
    # Session 746: Add watching status for arbitrage verification
    STATUS_WATCHING = 'watching'
    STATUS_VERIFIED = 'verified'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_VIEWED, 'Viewed'),
        (STATUS_ACTED, 'Acted'),
        (STATUS_DEFERRED, 'Deferred'),
        (STATUS_IGNORED, 'Ignored'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_WATCHING, 'Watching'),
        (STATUS_VERIFIED, 'Verified'),
    ]

    # Decision types
    DECISION_APPROVE = 'approve'
    DECISION_REJECT = 'reject'
    DECISION_MODIFY = 'modify'
    DECISION_DEFER = 'defer'
    DECISION_DELEGATE = 'delegate'
    DECISION_IGNORE = 'ignore'
    DECISION_ESCALATE = 'escalate'
    # Session 746: Add watch decision for paper trading / verification
    DECISION_WATCH = 'watch'
    DECISION_CHOICES = [
        (DECISION_APPROVE, 'Approve'),
        (DECISION_REJECT, 'Reject'),
        (DECISION_MODIFY, 'Modify'),
        (DECISION_DEFER, 'Defer'),
        (DECISION_DELEGATE, 'Delegate'),
        (DECISION_IGNORE, 'Ignore'),
        (DECISION_ESCALATE, 'Escalate'),
        (DECISION_WATCH, 'Watch & Verify'),
    ]

    # Verification outcomes (for watched items)
    VERIFY_WON = 'won'
    VERIFY_LOST = 'lost'
    VERIFY_PUSH = 'push'
    VERIFY_CANCELLED = 'cancelled'
    VERIFY_PENDING = 'pending'
    VERIFICATION_CHOICES = [
        (VERIFY_PENDING, 'Pending Verification'),
        (VERIFY_WON, 'Would Have Won'),
        (VERIFY_LOST, 'Would Have Lost'),
        (VERIFY_PUSH, 'Push (No Action)'),
        (VERIFY_CANCELLED, 'Event Cancelled'),
    ]

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='attention_items'
    )

    # Source information
    source_type = models.CharField(max_length=50)  # 'thinking_agent', 'pilot_gate', etc.
    source_id = models.CharField(max_length=100, blank=True)
    source_agent = models.CharField(max_length=100, blank=True)

    # Content
    item_type = models.CharField(max_length=50)  # 'decision', 'alert', 'opportunity'
    title = models.CharField(max_length=200)
    summary = models.TextField()
    payload = models.JSONField(default=dict)

    # Priority
    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default=URGENCY_MEDIUM
    )
    priority_score = models.FloatField(default=0.0)
    impact_estimate = models.CharField(max_length=20, blank=True)

    # ML Context
    ml_prediction = models.JSONField(null=True, blank=True)
    ml_confidence = models.FloatField(null=True, blank=True)
    ml_recommendation = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    # Human Decision
    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        null=True, blank=True
    )
    decision_feedback = models.TextField(blank=True)
    decision_confidence = models.FloatField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    time_to_decision_ms = models.IntegerField(null=True, blank=True)

    # Human Override
    human_overrode_ml = models.BooleanField(default=False)
    override_reason = models.TextField(blank=True)

    # Deferral
    deferred_until = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Session 746: Verification fields for Watch & Verify feature
    # Used to track arbitrage/prediction outcomes without actually betting
    verification_outcome = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        null=True, blank=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_profit = models.FloatField(null=True, blank=True)  # Calculated profit/loss
    verification_notes = models.TextField(blank=True)
    event_completed_at = models.DateTimeField(null=True, blank=True)  # When the actual event finished

    class Meta:
        ordering = ['-priority_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'urgency']),
            models.Index(fields=['source_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"[{self.urgency.upper()}] {self.title}"

    def mark_viewed(self):
        """Mark item as viewed."""
        if self.status == self.STATUS_PENDING:
            self.status = self.STATUS_VIEWED
            self.viewed_at = timezone.now()
            self.save(update_fields=['status', 'viewed_at'])

    def record_decision(self, decision: str, feedback: str = '', confidence: float = None):
        """Record a human decision on this item."""
        self.decision = decision
        self.decision_feedback = feedback
        self.decision_confidence = confidence
        self.decided_at = timezone.now()

        # Session 746: Handle 'watch' decision - set status to watching instead of acted
        if decision == self.DECISION_WATCH:
            self.status = self.STATUS_WATCHING
            self.verification_outcome = self.VERIFY_PENDING
        elif decision == 'reopen':
            # Re-open deferred items back to pending for continued monitoring
            self.status = self.STATUS_PENDING
            self.decision = None
            self.decided_at = None
        else:
            self.status = self.STATUS_ACTED

        # Calculate time to decision
        if self.viewed_at:
            delta = self.decided_at - self.viewed_at
            self.time_to_decision_ms = int(delta.total_seconds() * 1000)

        # Check if human overrode ML
        if self.ml_recommendation:
            ml_would_approve = self.ml_recommendation.lower() in ['approve', 'proceed', 'yes']
            human_approved = decision == self.DECISION_APPROVE
            self.human_overrode_ml = ml_would_approve != human_approved

        self.save()

    def record_verification(self, outcome: str, profit: float = None, notes: str = ''):
        """
        Session 746: Record the verification outcome for a watched item.
        Call this after the event has completed to track whether it would have been profitable.
        """
        self.verification_outcome = outcome
        self.verification_profit = profit
        self.verification_notes = notes
        self.verified_at = timezone.now()
        self.event_completed_at = timezone.now()
        self.status = self.STATUS_VERIFIED
        self.save()


class HumanFeedbackRecord(models.Model):
    """Record of human feedback for ML learning."""

    attention_item = models.ForeignKey(
        HumanAttentionItem,
        on_delete=models.CASCADE,
        related_name='feedback_records'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # The Decision
    decision = models.CharField(max_length=20)
    feedback_text = models.TextField(blank=True)
    confidence = models.FloatField(null=True, blank=True)

    # ML Context at Decision Time
    ml_task_type = models.CharField(max_length=50, blank=True, null=True)
    ml_models_used = models.JSONField(null=True, blank=True)
    ml_prediction = models.JSONField(null=True, blank=True)
    ml_confidence = models.FloatField(null=True, blank=True)

    # Override Analysis
    human_agreed_with_ml = models.BooleanField(null=True)
    confidence_delta = models.FloatField(null=True, blank=True)

    # Learning Status
    fed_to_ml = models.BooleanField(default=False)
    fed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback: {self.decision} on {self.attention_item_id}"


class HumanPreference(models.Model):
    """Human preference settings - both explicit and learned."""

    REVIEW_DEPTH_QUICK = 'quick'
    REVIEW_DEPTH_STANDARD = 'standard'
    REVIEW_DEPTH_THOROUGH = 'thorough'
    REVIEW_DEPTH_CHOICES = [
        (REVIEW_DEPTH_QUICK, 'Quick (< 30s)'),
        (REVIEW_DEPTH_STANDARD, 'Standard (30s-2min)'),
        (REVIEW_DEPTH_THOROUGH, 'Thorough (> 2min)'),
    ]

    CHANNEL_DISCORD = 'discord'
    CHANNEL_WEB = 'web'
    CHANNEL_EMAIL = 'email'
    CHANNEL_CHOICES = [
        (CHANNEL_DISCORD, 'Discord'),
        (CHANNEL_WEB, 'Web Dashboard'),
        (CHANNEL_EMAIL, 'Email'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='human_preferences'
    )

    # Notification Preferences
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    min_urgency_to_notify = models.CharField(
        max_length=20,
        choices=HumanAttentionItem.URGENCY_CHOICES,
        default=HumanAttentionItem.URGENCY_MEDIUM
    )
    preferred_channel = models.CharField(
        max_length=50,
        choices=CHANNEL_CHOICES,
        default=CHANNEL_DISCORD
    )

    # Review Preferences
    review_depth = models.CharField(
        max_length=20,
        choices=REVIEW_DEPTH_CHOICES,
        default=REVIEW_DEPTH_STANDARD
    )
    auto_approve_low_risk = models.BooleanField(default=False)
    require_review_above_confidence = models.FloatField(default=0.95)

    # Trust Settings
    trusted_agents = models.JSONField(default=list)
    blocked_sources = models.JSONField(default=list)

    # Learned Preferences (auto-updated)
    topic_weights = models.JSONField(default=dict)
    source_weights = models.JSONField(default=dict)
    avg_decision_time_ms = models.IntegerField(null=True, blank=True)
    approval_rate = models.FloatField(null=True, blank=True)
    total_decisions = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"

    def update_learned_stats(self):
        """Update learned statistics from feedback history."""
        from django.db.models import Avg, Count

        # Get user's feedback records
        feedbacks = HumanFeedbackRecord.objects.filter(user=self.user)

        if feedbacks.exists():
            # Calculate approval rate
            total = feedbacks.count()
            approvals = feedbacks.filter(decision='approve').count()
            self.approval_rate = approvals / total if total > 0 else None
            self.total_decisions = total

            # Calculate average decision time from attention items
            items = HumanAttentionItem.objects.filter(
                user=self.user,
                time_to_decision_ms__isnull=False
            )
            avg_time = items.aggregate(avg=Avg('time_to_decision_ms'))['avg']
            self.avg_decision_time_ms = int(avg_time) if avg_time else None

            self.save(update_fields=[
                'approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at'
            ])


class HumanControlAction(models.Model):
    """Audit log of human control actions on the system."""

    ACTION_PAUSE_AGENT = 'pause_agent'
    ACTION_RESUME_AGENT = 'resume_agent'
    ACTION_PAUSE_ALL = 'pause_all'
    ACTION_RESUME_ALL = 'resume_all'
    ACTION_OVERRIDE_DECISION = 'override_decision'
    ACTION_ADJUST_THRESHOLD = 'adjust_threshold'
    ACTION_BLOCK_SOURCE = 'block_source'
    ACTION_UNBLOCK_SOURCE = 'unblock_source'
    ACTION_PRIORITY_BOOST = 'priority_boost'
    ACTION_QUIET_MODE = 'quiet_mode'
    ACTION_REVIEW_MODE = 'review_mode'
    ACTION_CHOICES = [
        (ACTION_PAUSE_AGENT, 'Pause Agent'),
        (ACTION_RESUME_AGENT, 'Resume Agent'),
        (ACTION_PAUSE_ALL, 'Pause All'),
        (ACTION_RESUME_ALL, 'Resume All'),
        (ACTION_OVERRIDE_DECISION, 'Override Decision'),
        (ACTION_ADJUST_THRESHOLD, 'Adjust Threshold'),
        (ACTION_BLOCK_SOURCE, 'Block Source'),
        (ACTION_UNBLOCK_SOURCE, 'Unblock Source'),
        (ACTION_PRIORITY_BOOST, 'Priority Boost'),
        (ACTION_QUIET_MODE, 'Quiet Mode'),
        (ACTION_REVIEW_MODE, 'Review Mode'),
    ]

    TARGET_AGENT = 'agent'
    TARGET_SOURCE = 'source'
    TARGET_MODEL = 'model'
    TARGET_SYSTEM = 'system'
    TARGET_CHOICES = [
        (TARGET_AGENT, 'Agent'),
        (TARGET_SOURCE, 'Source'),
        (TARGET_MODEL, 'Model'),
        (TARGET_SYSTEM, 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='control_actions'
    )

    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50, choices=TARGET_CHOICES)
    target_id = models.CharField(max_length=100)

    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)

    reason = models.TextField(blank=True)
    auto_revert_at = models.DateTimeField(null=True, blank=True)
    reverted = models.BooleanField(default=False)
    reverted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action_type} on {self.target_type}:{self.target_id}"


class HumanSystemState(models.Model):
    """
    Global system state controlled by humans.
    Singleton pattern - only one row should exist.
    """

    # Global controls
    system_paused = models.BooleanField(default=False)
    review_mode = models.BooleanField(default=False)  # All decisions require human approval
    quiet_mode = models.BooleanField(default=False)
    quiet_mode_until = models.DateTimeField(null=True, blank=True)

    # Paused agents (list of agent names)
    paused_agents = models.JSONField(default=list)

    # ML thresholds (override defaults)
    ml_confidence_threshold = models.FloatField(default=0.6)
    auto_approve_threshold = models.FloatField(default=0.95)

    # Last updated
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Human System State"
        verbose_name_plural = "Human System State"

    def __str__(self):
        status = []
        if self.system_paused:
            status.append("PAUSED")
        if self.review_mode:
            status.append("REVIEW MODE")
        if self.quiet_mode:
            status.append("QUIET")
        return f"System: {', '.join(status) if status else 'NORMAL'}"

    @classmethod
    def get_state(cls):
        """Get or create the singleton system state."""
        state, _ = cls.objects.get_or_create(pk=1)
        return state

    def pause_agent(self, agent_name: str):
        """Add an agent to the paused list."""
        if agent_name not in self.paused_agents:
            self.paused_agents.append(agent_name)
            self.save(update_fields=['paused_agents', 'updated_at'])

    def resume_agent(self, agent_name: str):
        """Remove an agent from the paused list."""
        if agent_name in self.paused_agents:
            self.paused_agents.remove(agent_name)
            self.save(update_fields=['paused_agents', 'updated_at'])

    def is_agent_paused(self, agent_name: str) -> bool:
        """Check if a specific agent is paused."""
        return self.system_paused or agent_name in self.paused_agents
