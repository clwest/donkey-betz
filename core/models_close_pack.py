"""
ClosePack — Deal-closing document bundle.

Session: Autonomy #23 — Policy 27

When an Opportunity reaches high-intent (reply, meeting booked,
pricing request), a ClosePack is generated with:
  - 1-page proposal (scope, timeline, price)
  - Contract/SOW draft
  - Invoice draft

All documents require human approval before sending.
"""

import uuid
from django.conf import settings
from django.db import models


class ClosePack(models.Model):
    """
    A bundle of deal-closing documents for an Opportunity.

    Lifecycle: draft → approved → sent → won/lost/expired
    """

    STATUS_CHOICES = [
        ('draft', 'Draft — pending review'),
        ('approved', 'Approved — ready to send'),
        ('sent', 'Sent to prospect'),
        ('won', 'Deal won'),
        ('lost', 'Deal lost'),
        ('expired', 'Expired — no response'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to opportunity
    opportunity = models.ForeignKey(
        'core.Opportunity', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='close_packs',
    )

    # Offer details
    offer_key = models.CharField(
        max_length=50,
        help_text="Which offer template (e.g. 'ai_automation', 'content_engine', 'analytics_dashboard')",
    )
    price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Quoted price in USD",
    )
    timeline_days = models.IntegerField(
        default=14,
        help_text="Estimated delivery timeline in days",
    )

    # Generated documents (stored as text/markdown)
    proposal_text = models.TextField(
        blank=True,
        help_text="1-page proposal: scope, timeline, price, assumptions",
    )
    contract_text = models.TextField(
        blank=True,
        help_text="SOW/MSA-lite contract draft",
    )
    invoice_text = models.TextField(
        blank=True,
        help_text="Invoice draft: line items, payment terms",
    )

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True,
    )
    edited_proposal = models.TextField(blank=True)
    edited_contract = models.TextField(blank=True)
    edited_invoice = models.TextField(blank=True)

    # Tracking
    trace_id = models.CharField(max_length=100, blank=True, db_index=True)
    outreach_draft = models.ForeignKey(
        'core.OutreachDraft', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='close_packs',
        help_text="Linked outreach draft that triggered this close pack",
    )

    # Follow-up scheduling
    followup_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When to follow up if no response",
    )
    followup_count = models.IntegerField(default=0)

    # Owner
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_close_pack'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['offer_key', 'status']),
        ]

    def __str__(self):
        return (
            f"{self.offer_key} | ${self.price} | {self.status} | "
            f"{self.opportunity_id or 'no-opp'}"
        )
