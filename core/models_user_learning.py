"""
Session 930: User Learning System Models

Models for tracking user feedback, goals, and skill evolution to enable
personalized agent interactions and continuous learning from user behavior.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class AgentFeedback(models.Model):
    """
    Session 930: Track user feedback on agent executions.

    Enables per-agent learning - understanding what works for each user
    with specific agents to improve future interactions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_feedbacks'
    )
    agent = models.ForeignKey(
        'core.Agent',
        on_delete=models.CASCADE,
        related_name='user_feedbacks'
    )

    # Link to the specific execution
    execution_id = models.UUIDField(
        null=True, blank=True,
        help_text='AgentExecution ID this feedback is for'
    )
    deliverable = models.ForeignKey(
        'core.Deliverable',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='feedbacks'
    )

    # Feedback data
    RATING_CHOICES = [
        (1, 'Helpful'),
        (0, 'Neutral'),
        (-1, 'Not Helpful'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback_text = models.TextField(blank=True, help_text='Optional detailed feedback')

    # Context snapshot - what was the context when this was generated
    context_snapshot = models.JSONField(
        default=dict,
        help_text='Snapshot of user context used for this execution'
    )

    # What the user was trying to accomplish
    task_description = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'agent']),
            models.Index(fields=['user', 'rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        rating_str = {1: '👍', 0: '😐', -1: '👎'}.get(self.rating, '?')
        return f"{self.user.username} → {self.agent.name}: {rating_str}"


class GoalProgress(models.Model):
    """
    Session 930: Track progress entries toward goals.

    Each entry represents a step toward goal completion, optionally
    linked to a deliverable or initiative that contributed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(
        'core.UserGoal',
        on_delete=models.CASCADE,
        related_name='goal_progress_entries'
    )

    # What contributed to progress
    deliverable = models.ForeignKey(
        'core.Deliverable',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='goal_contributions'
    )
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='goal_contributions'
    )

    # Progress details
    progress_delta = models.IntegerField(
        help_text='Percentage points added (e.g., 5 for +5%)'
    )
    milestone_reached = models.CharField(
        max_length=200, blank=True,
        help_text='Optional milestone description'
    )
    notes = models.TextField(blank=True)

    # Auto or manual
    is_automatic = models.BooleanField(
        default=False,
        help_text='True if system-detected, False if user-entered'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Goal progress entries'

    def __str__(self):
        goal_name = getattr(self.goal, 'name', str(self.goal_id))
        return f"{goal_name}: +{self.progress_delta}%"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update goal's current value if supported
        self._update_goal_progress()

    def _update_goal_progress(self):
        """Recalculate goal's total progress and update current_value"""
        from django.db.models import Sum
        from decimal import Decimal

        total = self.goal.goal_progress_entries.aggregate(
            total=Sum('progress_delta')
        )['total'] or 0

        # Old UserGoal uses current_value (Decimal), update it with progress total
        if hasattr(self.goal, 'current_value'):
            self.goal.current_value = Decimal(str(total))
            self.goal.save(update_fields=['current_value'])


class UserSkill(models.Model):
    """
    Session 930: Track user skill proficiency levels.

    Skills are inferred from successful deliverables and can evolve
    over time as users demonstrate competency.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tracked_skills'
    )

    # Skill identification
    skill_name = models.CharField(max_length=100)

    # Normalized skill category
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('creative', 'Creative'),
        ('analytical', 'Analytical'),
        ('communication', 'Communication'),
        ('leadership', 'Leadership'),
        ('domain', 'Domain Knowledge'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='technical')

    # Proficiency tracking (1-10 scale)
    proficiency_level = models.IntegerField(
        default=1,
        help_text='Skill level from 1 (beginner) to 10 (expert)'
    )

    # Evidence
    evidence_count = models.IntegerField(
        default=0,
        help_text='Number of times skill was demonstrated'
    )

    # Confidence in the assessment
    confidence = models.FloatField(
        default=0.5,
        help_text='Confidence in proficiency assessment (0-1)'
    )

    # Timestamps
    first_demonstrated = models.DateTimeField(auto_now_add=True)
    last_demonstrated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-proficiency_level', '-evidence_count']
        unique_together = ['user', 'skill_name']
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'proficiency_level']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.skill_name} (Level {self.proficiency_level})"

    def add_demonstration(self, quality_score: float):
        """
        Record a new skill demonstration and potentially level up.

        Args:
            quality_score: Quality of the demonstration (0-1)
        """
        self.evidence_count += 1
        self.last_demonstrated = timezone.now()

        # Increase confidence with more evidence
        self.confidence = min(1.0, self.confidence + 0.05)

        # Level up logic: need quality demonstrations to advance
        if quality_score >= 0.7 and self.evidence_count >= self.proficiency_level * 3:
            if self.proficiency_level < 10:
                self.proficiency_level += 1

        self.save()


class SkillDemonstration(models.Model):
    """
    Session 930: Record individual skill demonstrations.

    Each demonstration is evidence of a skill, linked to the
    deliverable or context where it was shown.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    skill = models.ForeignKey(
        UserSkill,
        on_delete=models.CASCADE,
        related_name='demonstrations'
    )

    # Source of demonstration
    deliverable = models.ForeignKey(
        'core.Deliverable',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='skill_demonstrations'
    )

    # Quality assessment
    quality_score = models.FloatField(
        help_text='Quality of this demonstration (0-1)'
    )

    # Context
    context = models.TextField(
        blank=True,
        help_text='How the skill was demonstrated'
    )

    # What triggered inference
    inference_source = models.CharField(
        max_length=50,
        default='deliverable',
        help_text='How skill was inferred (deliverable, manual, import)'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.skill.skill_name}: {self.quality_score:.0%} quality"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            # Update skill proficiency
            self.skill.add_demonstration(self.quality_score)


class ProfileCompletionPrompt(models.Model):
    """
    Session 930: Track when users were prompted about profile completion.

    Prevents over-prompting and tracks which prompts were helpful.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_prompts'
    )

    # What was prompted
    field_category = models.CharField(max_length=50)
    field_name = models.CharField(max_length=100)
    prompt_text = models.TextField()

    # Response
    was_completed = models.BooleanField(default=False)
    was_dismissed = models.BooleanField(default=False)
    response_value = models.TextField(blank=True)

    # Timing
    prompted_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-prompted_at']
        indexes = [
            models.Index(fields=['user', 'was_completed']),
        ]

    def __str__(self):
        status = '✅' if self.was_completed else ('❌' if self.was_dismissed else '⏳')
        return f"{self.user.username}: {self.field_name} {status}"
