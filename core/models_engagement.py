"""
EngagementEvent — Inbound engagement tracking.

Session: Autonomy #24 — Policy 28

Captures and classifies inbound prospect interactions (replies,
meeting bookings, form fills). Links to OutreachDraft, Opportunity,
and ClosePack for full pipeline continuity.

Lifecycle: unread -> classified -> actioned -> closed
"""

import uuid
from django.conf import settings
from django.db import models


class EngagementEvent(models.Model):
    """
    One inbound engagement signal from a prospect.

    Created when a reply, meeting booking, or form fill is detected.
    Auto-classified by intent. Draft replies require human approval.
    """

    STATUS_CHOICES = [
        ('unread', 'Unread — new signal'),
        ('classified', 'Classified — awaiting action'),
        ('needs_reply', 'Needs reply — draft pending approval'),
        ('actioned', 'Actioned — replied or routed'),
        ('disqualified', 'Disqualified'),
        ('closed', 'Closed — no further action'),
    ]

    INTENT_CHOICES = [
        ('positive', 'Positive — interested, wants more info'),
        ('neutral', 'Neutral — question or clarification'),
        ('objection', 'Objection — price, timing, scope concern'),
        ('meeting', 'Meeting — wants to schedule a call'),
        ('unsubscribe', 'Unsubscribe — opt-out request'),
        ('unknown', 'Unknown — could not classify'),
    ]

    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('form', 'Contact form'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to outreach that triggered this engagement
    outreach_draft = models.ForeignKey(
        'core.OutreachDraft', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='engagements',
    )

    # Link to opportunity (created or existing)
    opportunity = models.ForeignKey(
        'core.Opportunity', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='engagements',
    )

    # Prospect info (denormalized for quick display)
    prospect_name = models.CharField(max_length=200, blank=True)
    prospect_company = models.CharField(max_length=200, blank=True)
    prospect_role = models.CharField(max_length=200, blank=True)

    # Inbound message
    channel = models.CharField(
        max_length=20, choices=CHANNEL_CHOICES, default='email',
    )
    subject_line = models.CharField(max_length=300, blank=True)
    message_text = models.TextField(
        help_text="Inbound message content",
    )

    # Classification
    intent = models.CharField(
        max_length=20, choices=INTENT_CHOICES, default='unknown', db_index=True,
    )
    summary = models.TextField(
        blank=True,
        help_text="AI-generated summary of the engagement",
    )
    extracted_fields = models.JSONField(
        default=dict, blank=True,
        help_text="Extracted: company, role, need, budget_cues, timeline_cues",
    )
    suggested_action = models.CharField(
        max_length=100, blank=True,
        help_text="AI-suggested next step (e.g. 'send_close_pack', 'book_call')",
    )

    # Reply draft (approval-gated)
    draft_reply = models.TextField(
        blank=True,
        help_text="Draft reply text for approval",
    )
    edited_reply = models.TextField(
        blank=True,
        help_text="Human-edited reply text (overrides draft)",
    )

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='unread', db_index=True,
    )
    disqualify_reason = models.CharField(max_length=300, blank=True)

    # Tracking
    trace_id = models.CharField(max_length=100, blank=True, db_index=True)
    suppressed = models.BooleanField(
        default=False, db_index=True,
        help_text="Permanently suppressed (unsubscribe/opt-out)",
    )

    # Owner
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_engagement_event'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['intent', 'status']),
            models.Index(fields=['channel', '-created_at']),
        ]

    def __str__(self):
        return (
            f"{self.intent} | {self.status} | "
            f"{self.prospect_name or 'unknown'} | "
            f"{self.channel}"
        )
