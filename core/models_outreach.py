"""
OutreachDraft — Approval-based outreach sequencing.

Session: Autonomy #22 — Policy 26

Tracks outreach drafts from lead discovery through approval and
follow-up sequencing. Never auto-sends — all outreach requires
explicit human approval.

Lifecycle: draft → approved → sent → replied/expired
"""

import uuid
from django.conf import settings
from django.db import models


class OutreachDraft(models.Model):
    """
    One outreach message draft tied to a lead (SpiderData item).

    Created by OutreachSequencer, approved/rejected via PA tool,
    follow-ups auto-scheduled on approval.
    """

    STATUS_CHOICES = [
        ('draft', 'Draft — pending review'),
        ('approved', 'Approved — ready to send'),
        ('rejected', 'Rejected'),
        ('sent', 'Sent'),
        ('replied', 'Got reply'),
        ('expired', 'Expired — no response after sequence'),
    ]

    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to source lead (SpiderData)
    spider_data_id = models.UUIDField(
        db_index=True,
        help_text="SpiderData item that sourced this lead",
    )

    # Lead info (denormalized for quick display)
    lead_title = models.CharField(max_length=200)
    lead_source = models.CharField(max_length=100, blank=True)
    lead_url = models.URLField(max_length=500, blank=True)
    lead_score = models.IntegerField(default=0)

    # Outreach content
    offer_key = models.CharField(
        max_length=50, blank=True,
        help_text="Which offer template was used (e.g. 'ai_automation', 'content_engine')",
    )
    subject_line = models.CharField(max_length=200, blank=True)
    body_text = models.TextField(
        help_text="Draft outreach message body",
    )
    channel = models.CharField(
        max_length=20, choices=CHANNEL_CHOICES, default='email',
    )

    # Sequencing
    touch_number = models.IntegerField(
        default=1,
        help_text="Which touch in the sequence (1=initial, 2=first follow-up, etc.)",
    )
    parent_draft = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='follow_ups',
        help_text="Previous draft in this sequence",
    )
    next_touch_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When next follow-up should be generated",
    )

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True,
    )
    rejection_reason = models.CharField(max_length=200, blank=True)
    edited_text = models.TextField(
        blank=True,
        help_text="If user edited the text before approving",
    )

    # Tracking
    opportunity = models.ForeignKey(
        'core.Opportunity', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='outreach_drafts',
        help_text="Linked Opportunity record (created on approve)",
    )
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
        db_table = 'core_outreach_draft'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['spider_data_id']),
            models.Index(fields=['touch_number', 'status']),
        ]

    def __str__(self):
        return f"Touch {self.touch_number} | {self.status} | {self.lead_title[:50]}"
