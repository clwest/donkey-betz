"""Legal-domain audit models (S2803 Phase 3.0).

Compliance-audit surface for the Colorado Family Law drafting flow. Kept
in a dedicated module (rather than appended to models_unified_system.py)
so future audit-model extensions (per-tool-call trace, disclosure history,
retention policy) have a clean home.

Session 2803 Phase 3.0 (Rigby SIGN Fold 2 mitigation + Fold 3 future_trigger):
    - LegalDocumentDispatchLog rows are written for every drafting
      dispatch (UI endpoint + Rigby PA path via the shared
      dispatch_legal_draft helper). Both paths enforce
      disclaimer_acknowledged=True before writing.
    - resulting_document / status / completed_at / error_message are
      updated post-hoc when the Celery task finishes (in-task update
      preferred; safe against agent-side errors).
    - client_session_pin correlates dispatches with the PA conversation
      pin that issued them (empty for UI-only dispatches).
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class LegalDocumentDispatchLog(models.Model):
    """One row per drafting dispatch. Never deleted (compliance retention)."""

    STATUS_CHOICES = [
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='legal_dispatch_logs',
    )

    # Celery task the dispatch created
    task_id = models.CharField(max_length=64, db_index=True)
    task_description = models.TextField(
        help_text="The user's original drafting request",
    )

    # Client provenance at dispatch time
    dispatched_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    client_session_pin = models.CharField(
        max_length=64, blank=True, db_index=True,
        help_text="PA conversation pin if dispatch came via _handle_legal_agent; empty for UI dispatches",
    )

    # Disclaimer acknowledgement — enforcement gate at dispatch time
    disclaimer_acknowledged = models.BooleanField(
        default=False,
        help_text="Whether the caller explicitly acknowledged the not-legal-advice disclaimer",
    )

    # Terminal state — filled by draft_legal_document_task on completion/failure
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default='dispatched',
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    resulting_document = models.ForeignKey(
        'core.LegalDocument',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='dispatch_log',
    )

    class Meta:
        app_label = 'core'
        ordering = ['-dispatched_at']
        verbose_name = 'Legal Document Dispatch Log'
        verbose_name_plural = 'Legal Document Dispatch Logs'
        indexes = [
            models.Index(fields=['user', '-dispatched_at']),
            models.Index(fields=['task_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"LegalDispatch {self.task_id[:8]} · {self.user_id} · {self.status}"
