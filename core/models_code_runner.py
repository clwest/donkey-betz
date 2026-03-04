"""
CodeRun model — tracks code-agent runs dispatched from the mobile Code Runner screen.

Admin-only. Each run is workspace-restricted (v0: mobile/ only) with a runtime cap,
output cap, and secret redaction in logs.
"""

from django.conf import settings
from django.db import models

from core.models.base import UnifiedBaseModel


class CodeRunMode(models.TextChoices):
    DRY_RUN = 'dry_run', 'Dry Run'
    APPLY = 'apply', 'Apply'


class CodeRunStatus(models.TextChoices):
    QUEUED = 'queued', 'Queued'
    RUNNING = 'running', 'Running'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'


class CodeRun(UnifiedBaseModel):
    """A tracked code-agent execution dispatched from the Code Runner screen."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='code_runs',
    )
    mode = models.CharField(
        max_length=10,
        choices=CodeRunMode.choices,
        default=CodeRunMode.DRY_RUN,
    )
    task = models.TextField(help_text='The task/prompt sent to the code agent')
    status = models.CharField(
        max_length=12,
        choices=CodeRunStatus.choices,
        default=CodeRunStatus.QUEUED,
    )
    workspace = models.CharField(
        max_length=100,
        default='mobile',
        help_text='Workspace restriction (v0: always mobile)',
    )

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    log_lines = models.JSONField(
        default=list,
        help_text='Captured output lines (capped at LOG_MAX_LINES)',
    )

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['created_by', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.status}] {self.mode} run by {self.created_by} — {self.task[:60]}"
