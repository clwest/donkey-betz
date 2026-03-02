"""
Ops Runs — structured observability for multi-step backend operations.

Tracks ops_control_loop, smoke tests, deploy_verify, and manual runs
with parent OpsRun + child OpsRunEvent timeline.
"""
import uuid
from django.db import models


class OpsRun(models.Model):
    """A single execution of an ops operation (smoke test, control loop, etc.)."""
    RUN_TYPE_CHOICES = [
        ('ops_loop', 'Ops Loop'),
        ('smoke_test', 'Smoke Test'),
        ('deploy_verify', 'Deploy Verify'),
        ('manual', 'Manual'),
        ('llm_routing', 'LLM Routing'),
    ]
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('partial', 'Partial'),
    ]
    TRIGGERED_BY_CHOICES = [
        ('beat', 'Beat'),
        ('pa_tool', 'PA Tool'),
        ('management_cmd', 'Management Cmd'),
        ('manual', 'Manual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    run_type = models.CharField(max_length=40, choices=RUN_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    triggered_by = models.CharField(max_length=100, choices=TRIGGERED_BY_CHOICES, default='manual')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    summary = models.JSONField(default=dict)
    event_count = models.PositiveIntegerField(default=0)
    fail_count = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']

    def __str__(self):
        return f"[{self.run_type}] {self.title} ({self.status})"


class OpsRunEvent(models.Model):
    """A single event in an OpsRun timeline."""
    EVENT_TYPE_CHOICES = [
        ('step_start', 'Step Start'),
        ('step_pass', 'Step Pass'),
        ('step_fail', 'Step Fail'),
        ('info', 'Info'),
        ('heartbeat', 'Heartbeat'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        OpsRun,
        on_delete=models.CASCADE,
        related_name='events',
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    label = models.CharField(max_length=200)
    detail = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.event_type}: {self.label} on {self.run_id}"
