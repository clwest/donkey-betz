"""
HAI Dispatch Log — CDR-001 §7 Gap 2 (§16 wrap-up bundle)
========================================================

Cross-channel dispatch audit table for HumanAttentionItem fanout.
Complements the sports-scoped ``NotificationLog`` (at
``core/models_push_notifications.py:183``) which cannot audit
Discord / Expo / Inbox dispatches.

Each row records one channel dispatch attempt for one
(user, source_type, source_id) tuple. A ``(user, source_type,
source_id, channel)`` unique constraint prevents double-writes for
the same dispatch. Cross-channel dedup queries then read this table
to determine whether any given HAI has already been dispatched on
any channel.

Identity carriage per CDR-001 §21 F6 warning (S1271 F6 drop-boundary):
``executor_actor`` + ``sponsor_actor`` + ``principal_user`` fields
capture the three actor roles even when only a subset is populated
at write time.

Ratified rules governing this model:
- PLAYBOOK-2.2.2 (CDR discipline) — CDR-001 §7 Gap 2 covers scope
- PLAYBOOK-3.2.2 (acceptance-tests-first) — AT16-2 pre-drafted

Governance:
- Acceptance tests at ``core/tests/test_hai_wrap_up_bundle.py::AT16_2``
  verify the model contract at runtime.
- ``status`` field choices align with ``ChannelDispatchState`` enum in
  ``core/services/hai_dispatch_state.py``.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models

from core.services.hai_dispatch_state import ChannelDispatchState


class HAIDispatchLog(models.Model):
    """One row per (recipient, source_type, source_id, channel) dispatch."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hai_dispatch_logs',
        help_text=(
            'Recipient of the notification — the user whose HumanAttentionItem '
            'triggered this dispatch attempt.'
        ),
    )

    source_type = models.CharField(
        max_length=100,
        help_text='HAI source_type — matches HumanAttentionItem.source_type',
    )
    source_id = models.CharField(
        max_length=200,
        help_text='HAI source_id — matches HumanAttentionItem.source_id',
    )

    channel = models.CharField(
        max_length=32,
        help_text=(
            "Channel identifier — 'discord' | 'webpush' | 'expo' | 'inbox' "
            'as of v1. New channels MAY be added without schema migration; '
            'the enum contract is on ChannelDispatchState, not on this field.'
        ),
    )

    dispatched_at = models.DateTimeField(
        auto_now_add=True,
        help_text='UTC timestamp of the dispatch attempt.',
    )

    status = models.CharField(
        max_length=32,
        choices=[(state.value, state.name) for state in ChannelDispatchState],
        default=ChannelDispatchState.NOT_ATTEMPTED.value,
        help_text=(
            'Dispatch outcome per ChannelDispatchState enum.'
        ),
    )

    error_message = models.TextField(
        blank=True,
        default='',
        help_text=(
            'Error details for status=failed. Empty for other statuses.'
        ),
    )

    executor_actor = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text=(
            'The agent that executed the action producing the HAI. '
            'Free-text for backward compat; may be an Agent name or ID.'
        ),
    )
    sponsor_actor = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text=(
            'The agent that sponsored the executor (e.g., orchestrator). '
            'Free-text.'
        ),
    )
    principal_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hai_dispatch_logs_as_principal',
        help_text=(
            'The user on whose behalf the action was taken (if different '
            'from recipient). Preserves the S1271 F6 principal identity.'
        ),
    )

    class Meta:
        db_table = 'hai_dispatch_logs'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'source_type', 'source_id', 'channel'],
                name='hai_dispatch_log_dedup_recipient_source_channel',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'dispatched_at']),
            models.Index(fields=['source_type', 'source_id']),
            models.Index(fields=['channel', 'status', 'dispatched_at']),
        ]
        ordering = ['-dispatched_at']

    def __str__(self) -> str:  # pragma: no cover — debug only
        return (
            f'HAIDispatchLog[{self.channel}] {self.source_type}/{self.source_id} '
            f'→ user={self.user_id} status={self.status}'
        )
