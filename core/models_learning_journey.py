"""
Learning Journey Models
Session 773: Replace stubs with real database-backed learning journeys

Models for tracking user learning paths, progress, and achievements.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


class LearningJourneyTemplate(models.Model):
    """Pre-defined learning path templates that users can start"""

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    CATEGORY_CHOICES = [
        ('agent_basics', 'Agent Basics'),
        ('content_creation', 'Content Creation'),
        ('automation', 'Automation'),
        ('analytics', 'Analytics'),
        ('integration', 'Integration'),
        ('advanced', 'Advanced Topics'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='agent_basics')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, default=2.0)
    steps_count = models.IntegerField(default=5)
    popularity = models.IntegerField(default=0)  # Number of times started
    tags = models.JSONField(default=list, blank=True)
    steps_data = models.JSONField(default=list)  # Template step definitions
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-popularity', 'name']

    def __str__(self):
        return f"{self.name} ({self.difficulty})"


class LearningJourney(models.Model):
    """A user's instance of a learning journey"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_journeys'
    )
    template = models.ForeignKey(
        LearningJourneyTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instances'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topic = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_step = models.IntegerField(default=1)
    total_steps = models.IntegerField(default=5)
    progress = models.IntegerField(default=0)  # Percentage 0-100
    goals = models.JSONField(default=list, blank=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, default=2.0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_activity_at']

    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.status})"

    def update_progress(self):
        """Calculate and update progress based on completed steps"""
        completed = self.steps.filter(status='completed').count()
        total = self.total_steps
        self.progress = int((completed / total) * 100) if total > 0 else 0
        self.save(update_fields=['progress', 'last_activity_at'])

    def to_dict(self):
        """Convert to frontend-expected format"""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'topic': self.topic,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'estimated_hours': float(self.estimated_hours),
            'goals': self.goals,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'steps': [step.to_dict() for step in self.steps.all().order_by('step_number')],
        }


class LearningJourneyStep(models.Model):
    """Individual step within a learning journey"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]

    STEP_TYPE_CHOICES = [
        ('lesson', 'Lesson'),
        ('exercise', 'Exercise'),
        ('explore', 'Explore'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journey = models.ForeignKey(
        LearningJourney,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    step_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    step_type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES, default='lesson')
    content = models.TextField(blank=True)
    content_meta = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    duration_minutes = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['step_number']
        unique_together = ['journey', 'step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.title}"

    def to_dict(self):
        """Convert to frontend-expected format"""
        return {
            'step_number': self.step_number,
            'title': self.title,
            'description': self.description,
            'step_type': self.step_type,
            'content': self.content,
            'content_meta': self.content_meta,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_minutes': self.duration_minutes,
            'notes': self.notes,
        }


class LearningAchievement(models.Model):
    """Achievement that can be earned by completing learning activities"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='trophy')
    requirement_type = models.CharField(max_length=50, default='journeys_completed')
    requirement_value = models.IntegerField(default=1)
    points = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['points', 'name']

    def __str__(self):
        return self.name


class UserLearningAchievement(models.Model):
    """Tracks which achievements a user has earned"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_achievements'
    )
    achievement = models.ForeignKey(
        LearningAchievement,
        on_delete=models.CASCADE,
        related_name='earned_by'
    )
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)  # For progressive achievements

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

    def to_dict(self):
        """Convert to frontend-expected format"""
        return {
            'id': str(self.id),
            'name': self.achievement.name,
            'description': self.achievement.description,
            'icon': self.achievement.icon,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'progress': self.progress,
            'total': self.achievement.requirement_value,
        }


class UserLearningStreak(models.Model):
    """Tracks user's learning streak (consecutive days of activity)"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_streak',
        primary_key=True
    )
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    total_steps_completed = models.IntegerField(default=0)
    total_journeys_completed = models.IntegerField(default=0)
    total_hours_spent = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.current_streak} day streak"

    def record_activity(self):
        """Record learning activity for today"""
        today = timezone.now().date()

        if self.last_activity_date is None:
            self.current_streak = 1
        elif self.last_activity_date == today:
            pass  # Already recorded today
        elif self.last_activity_date == today - timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1  # Streak broken

        self.last_activity_date = today
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.save()
