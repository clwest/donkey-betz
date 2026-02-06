"""
Session 948: User Feedback Model

Stores user feedback, bug reports, and feature requests persistently.
This enables the PA to log issues for future sessions to address.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# Import base model - handle both package and direct import
try:
    from core.models.base import UnifiedBaseModel
except ImportError:
    from core.models import UnifiedBaseModel


class UserFeedback(UnifiedBaseModel):
    """
    Store user feedback, bug reports, and feature requests.

    This model provides database persistence for user feedback so it works
    in any deployment (not just local dev with file system access).

    The PA logs feedback here when users report issues. This creates a
    queue that can be reviewed and addressed across sessions.
    """
    FEEDBACK_TYPES = [
        ('ui_ux_issue', 'UI/UX Issue'),
        ('bug', 'Bug Report'),
        ('feature_request', 'Feature Request'),
        ('feedback', 'General Feedback'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('addressed', 'Addressed'),
        ('wont_fix', "Won't Fix"),
        ('duplicate', 'Duplicate'),
    ]

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='feedback_items'
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        default='feedback'
    )
    message = models.TextField(help_text="The user's feedback message")
    trace_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="PA trace ID for debugging"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    resolution_notes = models.TextField(
        blank=True,
        help_text="Notes about how this was addressed"
    )
    session_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="Session number when this was addressed"
    )

    class Meta:
        db_table = 'core_user_feedback'
        ordering = ['-created_at']
        verbose_name = 'User Feedback'
        verbose_name_plural = 'User Feedback'

    def __str__(self):
        username = getattr(self.user, 'username', 'unknown')
        return f"[{self.feedback_type}] {username}: {self.message[:50]}..."

    @classmethod
    def get_open_feedback(cls):
        """Get all open feedback items."""
        return cls.objects.filter(status='open').order_by('-created_at')

    @classmethod
    def get_feedback_summary(cls):
        """Get summary counts by type and status."""
        from django.db.models import Count
        return {
            'by_type': dict(cls.objects.values('feedback_type').annotate(count=Count('id')).values_list('feedback_type', 'count')),
            'by_status': dict(cls.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'total_open': cls.objects.filter(status='open').count(),
        }
