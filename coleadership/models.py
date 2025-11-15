"""
AI-Human Co-Leadership Models - Session 99

These models implement the co-leadership decision tracking system where:
- AI agents provide recommendations with stances (support/concern/objection/alternative/neutral)
- Humans make final decisions (can override AI)
- Outcomes are tracked and attributed (AI vs Human correctness)
- "I told you so" moments are captured playfully but respectfully

Philosophy: AI and Human as EQUAL COLLABORATORS
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class CoLeadershipDecision(models.Model):
    """
    Represents a single decision moment tied to a boardroom session.

    This is the central entity that tracks a strategic decision where
    both AI agents and humans collaborate.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Context
    project = models.ForeignKey(
        "content.CreativeProject",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coleadership_decisions",
        help_text="Optional project context for this decision"
    )
    session = models.ForeignKey(
        "content.AISession",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coleadership_decisions",
        help_text="Usually a boardroom session where this decision was discussed"
    )

    # Decision details
    title = models.CharField(
        max_length=255,
        help_text="Short summary of the decision (e.g., 'Q1 AI roadmap')"
    )
    description = models.TextField(
        blank=True,
        help_text="Longer explanation or prompt that initiated this decision"
    )

    # Ownership and timeline
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="initiated_decisions",
        help_text="User who initiated this decision"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    frozen_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set when the human commits to a final decision"
    )

    class Meta:
        db_table = 'coleadership_decision'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['session', '-created_at']),
        ]

    def __str__(self):
        return f"Decision: {self.title} ({self.created_at.strftime('%Y-%m-%d')})"

    @property
    def is_frozen(self):
        """Check if decision has been committed by human"""
        return self.frozen_at is not None

    @property
    def has_outcome(self):
        """Check if outcome has been recorded"""
        return hasattr(self, 'outcome')


class AgentRecommendation(models.Model):
    """
    Each board agent's stance for a decision (CTO, COO, etc.).

    Agents can:
    - Support: Agree with the direction
    - Concern: Have reservations but not blocking
    - Objection: Strongly disagree
    - Alternative: Propose different path
    - Neutral: No strong opinion
    """

    STANCE_CHOICES = [
        ("support", "Support"),
        ("concern", "Concern"),
        ("objection", "Objection"),
        ("alternative", "Alternative"),
        ("neutral", "Neutral"),
    ]

    decision = models.ForeignKey(
        CoLeadershipDecision,
        related_name="recommendations",
        on_delete=models.CASCADE
    )
    agent_template = models.ForeignKey(
        "agents.UnifiedAgentTemplate",
        on_delete=models.CASCADE,
        help_text="Which agent provided this recommendation"
    )

    # Agent's position
    stance = models.CharField(
        max_length=20,
        choices=STANCE_CHOICES,
        help_text="Agent's overall stance on this decision"
    )
    summary = models.TextField(
        help_text="Brief summary of agent's position"
    )
    recommendation_text = models.TextField(
        help_text="Full recommendation from the agent"
    )

    # Risk and alternatives
    risk_analysis = models.TextField(
        blank=True,
        help_text="Risks identified by this agent"
    )
    alternative_paths = models.JSONField(
        default=list,
        blank=True,
        help_text="Alternative approaches suggested by this agent"
    )

    # Confidence and context
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Agent's confidence level (0.0 to 1.0)"
    )
    time_horizon = models.CharField(
        max_length=20,
        blank=True,
        help_text="Time horizon for this recommendation (short_term, long_term, etc.)"
    )

    # Raw data from agent
    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Full raw response from agent for reference"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coleadership_agent_recommendation'
        ordering = ['decision', '-confidence']
        unique_together = ['decision', 'agent_template']
        indexes = [
            models.Index(fields=['decision', 'stance']),
            models.Index(fields=['decision', '-confidence']),
        ]

    def __str__(self):
        return f"{self.agent_template.display_name}: {self.stance} ({self.decision.title})"

    @property
    def is_supportive(self):
        """Check if agent supports the decision"""
        return self.stance == "support"

    @property
    def is_objecting(self):
        """Check if agent objects to the decision"""
        return self.stance == "objection"

    @property
    def has_concerns(self):
        """Check if agent has concerns"""
        return self.stance == "concern"


class HumanDecision(models.Model):
    """
    What the human ultimately chose.

    This records the human's final decision and whether it overrode
    AI recommendations. The human is ALWAYS the ultimate decision-maker.
    """

    decision = models.OneToOneField(
        CoLeadershipDecision,
        related_name="human_decision",
        on_delete=models.CASCADE
    )

    # What the human chose
    chosen_path_summary = models.TextField(
        help_text="Human's final decision in their own words"
    )
    justification = models.TextField(
        blank=True,
        help_text="Why the human chose this path"
    )

    # Override tracking
    is_override = models.BooleanField(
        default=False,
        help_text="Did the human override the AI's top recommendation?"
    )
    overridden_agent = models.ForeignKey(
        "agents.UnifiedAgentTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Which agent's recommendation was overridden (if applicable)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coleadership_human_decision'

    def __str__(self):
        override_text = " (OVERRIDE)" if self.is_override else ""
        return f"Human Decision: {self.decision.title}{override_text}"

    def save(self, *args, **kwargs):
        """Set frozen_at on decision when human decision is saved"""
        if not self.decision.frozen_at:
            self.decision.frozen_at = timezone.now()
            self.decision.save(update_fields=['frozen_at'])
        super().save(*args, **kwargs)


class DecisionOutcome(models.Model):
    """
    What actually happened later.

    This tracks the real-world outcome of the decision and attributes
    correctness to AI vs Human. Used for learning and the playful
    "I told you so" engine.
    """

    OUTCOME_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failure", "Failure"),
        ("mixed", "Mixed"),
    ]

    ATTRIBUTION_CHOICES = [
        ("ai", "AI more correct"),
        ("human", "Human more correct"),
        ("both", "Both partly correct"),
        ("unknown", "Unknown/unclear"),
    ]

    decision = models.OneToOneField(
        CoLeadershipDecision,
        related_name="outcome",
        on_delete=models.CASCADE
    )

    # Outcome details
    status = models.CharField(
        max_length=20,
        choices=OUTCOME_CHOICES,
        default="pending"
    )
    realized_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the outcome became clear"
    )
    outcome_summary = models.TextField(
        blank=True,
        help_text="What actually happened"
    )
    metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Quantitative metrics about the outcome"
    )

    # Attribution and confidence
    attribution = models.CharField(
        max_length=20,
        choices=ATTRIBUTION_CHOICES,
        default="unknown",
        help_text="Who was more correct: AI or Human?"
    )
    ai_confidence_snapshot = models.FloatField(
        null=True,
        blank=True,
        help_text="AI's confidence at decision time"
    )
    human_confidence_snapshot = models.FloatField(
        null=True,
        blank=True,
        help_text="Human's confidence at decision time"
    )

    # "I Told You So" Engine
    told_you_so_triggered = models.BooleanField(
        default=False,
        help_text="Did this outcome trigger an 'I told you so' moment?"
    )
    told_you_so_message = models.TextField(
        blank=True,
        help_text="The playful (but respectful) message generated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coleadership_decision_outcome'

    def __str__(self):
        return f"Outcome: {self.decision.title} - {self.get_status_display()} ({self.get_attribution_display()})"

    @property
    def ai_was_right(self):
        """Check if AI was more correct"""
        return self.attribution == "ai"

    @property
    def human_was_right(self):
        """Check if human was more correct"""
        return self.attribution == "human"

    @property
    def both_partly_right(self):
        """Check if both were partly correct"""
        return self.attribution == "both"


class CoLeadershipPreferences(models.Model):
    """
    User preferences for co-leadership interactions.

    Session 99: Simple user settings for tone and "I told you so" behavior.
    Defaults are conservative (serious tone, no ITYS messages) until user opts in.
    """

    TONE_CHOICES = [
        ("serious", "Serious - Professional and straightforward"),
        ("playful", "Playful - Lighthearted and engaging"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coleadership_preferences",
        help_text="User these preferences belong to"
    )

    # "I Told You So" preferences
    allow_told_you_so = models.BooleanField(
        default=False,
        help_text="Allow playful 'I told you so' messages when outcomes favor AI"
    )

    # Tone preferences
    tone = models.CharField(
        max_length=20,
        choices=TONE_CHOICES,
        default="serious",
        help_text="Preferred tone for co-leadership interactions"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coleadership_user_preferences'
        verbose_name = "Co-Leadership Preferences"
        verbose_name_plural = "Co-Leadership Preferences"

    def __str__(self):
        return f"Preferences for {self.user.username}: tone={self.tone}, allow_itys={self.allow_told_you_so}"


# Signal to auto-create preferences for new users
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_coleadership_preferences(sender, instance, created, **kwargs):
    """Create default co-leadership preferences for new users"""
    if created:
        CoLeadershipPreferences.objects.get_or_create(
            user=instance,
            defaults={
                'allow_told_you_so': False,
                'tone': 'serious'
            }
        )
