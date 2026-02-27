"""
Cockpit Audit Log — append-only record of all cockpit mutations.
Session P11: RBAC + Audit for Focus Cockpit.
"""
import uuid
from django.db import models
from django.conf import settings


class CockpitAuditLog(models.Model):
    """Append-only audit log for cockpit mutation actions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cockpit_audit_logs',
    )
    action = models.CharField(max_length=80, db_index=True)  # e.g. 'approve_decision', 'retry_run'
    target_type = models.CharField(max_length=60, blank=True)  # e.g. 'HumanAttentionItem', 'AgentExecution'
    target_id = models.CharField(max_length=100, blank=True)
    request_body = models.JSONField(default=dict)
    response_summary = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.action}] {self.target_type}:{self.target_id} @ {self.created_at}"
