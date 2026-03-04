"""
Meeting — Pipeline meeting tracking and pre-call briefs.

Session: Autonomy #25 — Policy 29

Tracks meetings from scheduling through follow-up.
Generates pre-call briefs with prospect context, pain points,
suggested offers, and discovery questions.

Lifecycle: scheduled -> briefed -> completed -> followed_up
"""

import uuid
from django.conf import settings
from django.db import models


class Meeting(models.Model):
    """
    A scheduled meeting tied to an Opportunity.

    Created manually or from EngagementEvent intent detection.
    Pre-call briefs generated automatically before the meeting.
    Post-meeting recaps require human approval before sending.
    """

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('briefed', 'Brief generated'),
        ('completed', 'Meeting completed'),
        ('no_show', 'No-show'),
        ('cancelled', 'Cancelled'),
        ('followed_up', 'Follow-up sent'),
    ]

    CHANNEL_CHOICES = [
        ('zoom', 'Zoom'),
        ('meet', 'Google Meet'),
        ('teams', 'Microsoft Teams'),
        ('phone', 'Phone call'),
        ('in_person', 'In person'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to opportunity
    opportunity = models.ForeignKey(
        'core.Opportunity', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='meetings',
    )

    # Link to engagement that triggered this meeting
    engagement = models.ForeignKey(
        'core.EngagementEvent', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='meetings',
    )

    # Meeting details
    title = models.CharField(max_length=300, blank=True)
    scheduled_at = models.DateTimeField(db_index=True)
    duration_minutes = models.IntegerField(default=30)
    channel = models.CharField(
        max_length=20, choices=CHANNEL_CHOICES, default='zoom',
    )
    meeting_link = models.URLField(max_length=500, blank=True)
    attendees = models.JSONField(
        default=list, blank=True,
        help_text="List of attendee dicts: [{name, email, role}]",
    )

    # Prospect info (denormalized)
    prospect_name = models.CharField(max_length=200, blank=True)
    prospect_company = models.CharField(max_length=200, blank=True)
    prospect_role = models.CharField(max_length=200, blank=True)

    # Pre-call brief
    brief_text = models.TextField(
        blank=True,
        help_text="Auto-generated pre-call brief",
    )
    brief_generated_at = models.DateTimeField(null=True, blank=True)

    # Post-meeting
    notes = models.TextField(
        blank=True,
        help_text="Meeting notes / outcome summary",
    )
    recap_draft = models.TextField(
        blank=True,
        help_text="Draft recap email for approval",
    )
    next_steps = models.TextField(
        blank=True,
        help_text="Agreed next steps from the meeting",
    )
    outcome = models.CharField(
        max_length=50, blank=True,
        help_text="Meeting outcome: interested, needs_followup, not_a_fit, deal_agreed",
    )

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='scheduled', db_index=True,
    )

    # Tracking
    trace_id = models.CharField(max_length=100, blank=True, db_index=True)

    # Owner
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_meeting'
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['-scheduled_at']),
        ]

    def __str__(self):
        return (
            f"{self.title or 'Meeting'} | {self.status} | "
            f"{self.prospect_name or 'unknown'} | "
            f"{self.scheduled_at.strftime('%Y-%m-%d %H:%M') if self.scheduled_at else 'unscheduled'}"
        )
