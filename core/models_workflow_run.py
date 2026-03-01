"""
WorkflowRun model — tracks multi-step PA workflow executions.

First workflow: source_pack_comparison (auto-collect → ingest → embed → compare → export).
Each run records stage-by-stage progress, accumulated artifact IDs, and an append-only event log.
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class WorkflowRun(models.Model):
    """A single execution of a multi-step PA workflow."""

    WORKFLOW_CHOICES = [
        ('source_pack_comparison', 'Source Pack Comparison'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('collecting', 'Collecting Sources'),
        ('ingesting', 'Ingesting Documents'),
        ('embedding', 'Embedding Documents'),
        ('generating', 'Generating Comparison'),
        ('exporting', 'Exporting Deliverable'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_key = models.CharField(max_length=60, choices=WORKFLOW_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Progress
    stage = models.CharField(max_length=40, blank=True, default='')
    percent = models.IntegerField(default=0)
    stage_detail = models.CharField(max_length=500, blank=True, default='')

    # I/O
    input_json = models.JSONField(default=dict, blank=True, help_text='Workflow input parameters')
    output_json = models.JSONField(default=dict, blank=True, help_text='Accumulated artifact IDs')

    # Append-only event log
    events_json = models.JSONField(default=list, blank=True, help_text='[{timestamp, stage, message}]')

    # Error / Celery
    error_message = models.TextField(blank=True, default='')
    celery_task_id = models.CharField(max_length=255, blank=True, default='')

    # Ownership
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_runs',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_workflow_run'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['workflow_key', '-created_at']),
        ]

    def __str__(self):
        return f"WorkflowRun({self.workflow_key}, {self.status}, {self.percent}%)"

    # ── Helper methods ──────────────────────────────────────────────────

    def log_event(self, message, stage=None):
        """Append a timestamped event."""
        events = self.events_json if isinstance(self.events_json, list) else []
        events.append({
            'timestamp': timezone.now().isoformat(),
            'stage': stage or self.stage,
            'message': message,
        })
        self.events_json = events

    def advance_stage(self, stage, percent, detail=''):
        """Move to a new stage with progress update."""
        self.stage = stage
        self.status = stage
        self.percent = percent
        self.stage_detail = detail
        self.log_event(detail or f'Entered stage: {stage}', stage=stage)

    def mark_started(self, celery_task_id=''):
        """Mark workflow as started."""
        self.status = 'collecting'
        self.stage = 'collecting'
        self.started_at = timezone.now()
        if celery_task_id:
            self.celery_task_id = celery_task_id
        self.log_event('Workflow started')

    def mark_complete(self, output=None):
        """Mark workflow as successfully complete."""
        self.status = 'complete'
        self.stage = 'complete'
        self.percent = 100
        self.completed_at = timezone.now()
        if output:
            self.output_json = output
        self.log_event('Workflow completed')

    def mark_failed(self, error, partial_output=None):
        """Mark workflow as failed with error info."""
        self.status = 'failed'
        self.error_message = str(error)[:2000]
        self.completed_at = timezone.now()
        if partial_output:
            self.output_json = partial_output
        self.log_event(f'Failed: {str(error)[:200]}')

    def mark_cancelled(self):
        """Mark workflow as cancelled."""
        self.status = 'cancelled'
        self.completed_at = timezone.now()
        self.log_event('Workflow cancelled')
