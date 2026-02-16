"""
CodeArtifact model - Patch-first workflow for autonomous code generation.

When CodeGeneratorAgent produces code but cannot persist it to the filesystem
(e.g. on Railway where no writable workspace exists), the output is captured
as a CodeArtifact for human review and later application.
"""

from django.conf import settings
from django.db import models

from core.models.base import UnifiedBaseModel


class CodeArtifactKind(models.TextChoices):
    FILE_CREATE = 'file_create', 'File Create'
    FILE_EDIT = 'file_edit', 'File Edit'
    PATCH = 'patch', 'Patch'


class CodeArtifactStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    APPLIED = 'applied', 'Applied'
    STALE = 'stale', 'Stale'


class CodeArtifact(UnifiedBaseModel):
    """A captured code output from an agent that couldn't write to the filesystem."""

    agent_name = models.CharField(max_length=120)
    agent_execution = models.ForeignKey(
        'core.AgentExecution',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='code_artifacts',
    )
    initiative = models.ForeignKey(
        'core.Initiative',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='code_artifacts',
    )
    trace_id = models.CharField(max_length=120, blank=True, default='')

    kind = models.CharField(
        max_length=20,
        choices=CodeArtifactKind.choices,
        default=CodeArtifactKind.FILE_CREATE,
    )
    status = models.CharField(
        max_length=20,
        choices=CodeArtifactStatus.choices,
        default=CodeArtifactStatus.PENDING,
    )

    target_path = models.CharField(max_length=500)
    content = models.TextField()
    content_before = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')

    review_note = models.TextField(blank=True, default='')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_code_artifacts',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.status}] {self.kind} {self.target_path} by {self.agent_name}"
