"""
Cockpit Autopilot — policy-driven automation with guardrails.
Session P14: Autopilot for Focus Cockpit.
"""
import uuid
from django.db import models
from django.conf import settings


class CockpitAutopilotPolicy(models.Model):
    """A policy that evaluates conditions and proposes/executes actions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=80, unique=True, db_index=True)
    label = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    enabled = models.BooleanField(default=False)
    thresholds = models.JSONField(default=dict)
    cooldown_minutes = models.PositiveIntegerField(default=60)
    max_actions_per_run = models.PositiveIntegerField(default=5)
    last_evaluated_at = models.DateTimeField(null=True, blank=True)
    last_fired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['key']

    def __str__(self):
        return f"{self.key} [{'on' if self.enabled else 'off'}]"


class CockpitAutopilotEvent(models.Model):
    """Record of each autopilot evaluation + action taken."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy = models.ForeignKey(
        CockpitAutopilotPolicy,
        on_delete=models.CASCADE,
        related_name='events',
    )
    mode = models.CharField(max_length=20)  # 'dry_run' or 'execute'
    proposed_action = models.CharField(max_length=80)
    target_type = models.CharField(max_length=60, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True, default='')
    executed = models.BooleanField(default=False)
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.mode}] {self.proposed_action} → {self.target_id} @ {self.created_at}"
