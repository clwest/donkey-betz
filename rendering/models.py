"""
Rendering Models - Session 105

RenderJob model tracks render requests and integrates with DaVinci Resolve Render Node.
"""

import uuid
from django.db import models
from django.conf import settings


class RenderJob(models.Model):
    """
    Represents a video render job.

    Workflow:
    1. Created when user requests render (status: queued)
    2. Dispatched to Resolve Node (status: dispatching)
    3. Resolve Node renders (status: rendering)
    4. Render completes (status: done)
    5. Or fails (status: error)
    """

    # Status choices
    STATUS_QUEUED = 'queued'
    STATUS_DISPATCHING = 'dispatching'
    STATUS_RENDERING = 'rendering'
    STATUS_DONE = 'done'
    STATUS_ERROR = 'error'

    STATUS_CHOICES = (
        (STATUS_QUEUED, 'Queued'),
        (STATUS_DISPATCHING, 'Dispatching'),
        (STATUS_RENDERING, 'Rendering'),
        (STATUS_DONE, 'Done'),
        (STATUS_ERROR, 'Error'),
    )

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Ownership
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='render_jobs'
    )

    # Optional project/session linkage
    # Session 324: Unified from CreativeProject
    project = models.ForeignKey(
        'core.PartnershipProject',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='render_jobs'
    )
    session = models.ForeignKey(
        'content.AISession',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='render_jobs'
    )

    # Human-friendly title (Session 106)
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text='Human-friendly job title (auto-generated if empty)'
    )

    # Job state
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_QUEUED,
        db_index=True  # Frequently queried
    )
    progress = models.FloatField(
        default=0.0,
        help_text='Render progress from 0.0 to 1.0'
    )

    # Payloads
    source_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text='Data sent to Resolve Node (timeline name, media files, etc.)'
    )
    result_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text='Data received from Resolve Node (metadata, file info, etc.)'
    )

    # Results
    result_url = models.URLField(
        blank=True,
        null=True,
        help_text='URL to download rendered video'
    )
    error_message = models.TextField(
        blank=True,
        help_text='Error details if status == error'
    )

    # Resolve Node tracking
    node_job_id = models.UUIDField(
        null=True,
        blank=True,
        help_text='Job ID from Resolve Node (may differ from our ID)'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name = 'Render Job'
        verbose_name_plural = 'Render Jobs'

    def save(self, *args, **kwargs):
        """Override save to auto-generate title if empty."""
        if not self.title:
            self.title = self.generate_title()
        super().save(*args, **kwargs)

    def generate_title(self):
        """Generate a human-friendly title based on session/project."""
        if self.session:
            session_title = getattr(self.session, 'title', None)
            if session_title:
                return f"Session render: {session_title}"
            return f"Session render: {self.session.session_id}"

        if self.project:
            return f"Project render: {self.project.name}"

        return f"Render job {str(self.id)[:8]}"

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def is_complete(self):
        """True if job is in a terminal state (done or error)."""
        return self.status in [self.STATUS_DONE, self.STATUS_ERROR]

    @property
    def is_active(self):
        """True if job is currently being processed."""
        return self.status in [self.STATUS_DISPATCHING, self.STATUS_RENDERING]

    @property
    def progress_percentage(self):
        """Progress as a percentage (0-100)."""
        return round(self.progress * 100, 1)
