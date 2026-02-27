"""
Cockpit Agent State — per-agent pause/resume + throttle state.
Session P12: Agent Fleet Management for Focus Cockpit.
"""
import uuid
from django.db import models
from django.conf import settings


class CockpitAgentState(models.Model):
    """Per-agent operational state controlled from the cockpit."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=100, unique=True, db_index=True)
    enabled = models.BooleanField(default=True)
    paused_reason = models.TextField(blank=True, default='')
    paused_at = models.DateTimeField(null=True, blank=True)
    max_runs_per_hour = models.PositiveIntegerField(null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Cockpit Agent State'
        verbose_name_plural = 'Cockpit Agent States'

    def __str__(self):
        status = 'enabled' if self.enabled else 'paused'
        return f"{self.agent_name} [{status}]"
