"""
Session 1098 Fix B-full — DeliverableAppend.

Per-append record for a Deliverable. Each synthesis step (or any
multi-call write to a single Deliverable) becomes one row. The
Deliverable's ``content`` field is the materialized concatenation of
its committed appends in ``append_offset`` order.

Contract + design rationale live in:
    docs/plans/SESSION_1098_FIX_B_FULL_TICKET.md

Key points:
- Primary key is ``call_id`` (a UUID) — same UUID used by LLMCallEvent
  and the LLM wrapper, so idempotency naturally aligns with retries
  that reuse the same call_id.
- Unique constraint on ``(deliverable, call_id, chunk_index)`` — a
  repeat insert with the identical tuple becomes a no-op (caller
  retrieves the existing committed row).
- ``expected_initiative_id`` is a snapshot from dispatch time. When
  the helper opens the transaction, it re-reads the Deliverable's
  current ``initiative_id``. If they differ the append is recorded
  with status='superseded' and routed to the Unassigned fallback —
  never applied to a stale initiative link.
- Append content must be materialized back onto
  ``Deliverable.content`` so dashboards / reads don't need a JOIN.
  The helper does this inside the same transaction.
"""

import uuid

from django.db import models
from django.utils import timezone


class DeliverableAppend(models.Model):
    """Single append record for a Deliverable (Session 1098 Fix B-full)."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('committed', 'Committed'),
        ('failed', 'Failed'),
        ('superseded', 'Superseded'),
    ]

    # --- Identity ------------------------------------------------------
    #
    # Django-default id AutoField is the PK. call_id is the IDEMPOTENCY
    # KEY — same call_id can appear on multiple rows when a caller
    # streams N chunks under one LLM call (each chunk gets a distinct
    # chunk_index). The unique constraint on (deliverable, call_id,
    # chunk_index) guarantees dedupe while allowing streaming.

    call_id = models.UUIDField(
        default=uuid.uuid4,
        db_index=True,
        help_text=(
            'Callers pass the LLMCallEvent.call_id here so retries with the '
            'same (deliverable, call_id, chunk_index) dedupe automatically '
            'via the unique constraint.'
        ),
    )
    deliverable = models.ForeignKey(
        'core.Deliverable',
        on_delete=models.CASCADE,
        related_name='appends',
        db_index=True,
    )

    # --- Ownership snapshot for race detection -------------------------

    expected_initiative_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=(
            'Optional. The initiative_id the caller *expected* the '
            'Deliverable to still be linked to at commit time. If set '
            'and it does not match Deliverable.initiative_id inside '
            'the SELECT FOR UPDATE transaction, the append is recorded '
            'as status=superseded and routed to a fallback. See '
            'core/services/deliverable_append_service.append_to_deliverable.'
        ),
    )
    execution_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Owning AgentExecution.id — matches LLMCallEvent.execution_id.',
    )
    agent_name = models.CharField(max_length=120, db_index=True)

    # --- Content + position -------------------------------------------

    content = models.TextField()
    append_offset = models.IntegerField(
        null=True,
        blank=True,
        help_text=(
            'Byte offset into Deliverable.content where this append starts. '
            'Set when status transitions pending -> committed.'
        ),
    )
    chunk_index = models.IntegerField(
        default=0,
        help_text=(
            'For streaming: 0-based index within a single call. Unique per '
            '(deliverable, call_id). Non-streaming callers leave this at 0.'
        ),
    )

    # --- State ---------------------------------------------------------

    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    failure_reason = models.CharField(max_length=500, blank=True, default='')
    routing_metadata = models.JSONField(default=dict, blank=True)

    # --- Timestamps ---------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True,
    )
    committed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        constraints = [
            models.UniqueConstraint(
                fields=['deliverable', 'call_id', 'chunk_index'],
                name='deliverable_append_idempotent',
            ),
        ]
        indexes = [
            models.Index(
                fields=['deliverable', 'status'],
                name='deliv_append_deliv_status',
            ),
            models.Index(
                fields=['execution_id', '-created_at'],
                name='deliv_append_exec_time',
            ),
            models.Index(
                fields=['-created_at', 'status'],
                name='deliv_append_time_status',
            ),
        ]

    def __str__(self):
        return (
            f'DeliverableAppend({str(self.call_id)[:8]}, '
            f'deliv={str(self.deliverable_id)[:8]}, '
            f'status={self.status}, chunk={self.chunk_index})'
        )
