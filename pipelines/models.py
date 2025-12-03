"""
Creative Pipeline Models

Session 109 - Creative Pipelines v1 (Template-Based Orchestration)

Models for reusable, named "recipes" that chain multiple AI operations.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class CreativePipelineTemplate(models.Model):
    """
    Template for a creative pipeline - defines the workflow structure.

    Templates are registered in code and stored in DB as a registry.
    """

    slug = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique identifier for the template (e.g. 'idea_to_image_set')"
    )
    name = models.CharField(
        max_length=200,
        help_text="Human-readable name (e.g. 'Idea to Image Set')"
    )
    description = models.TextField(
        help_text="Description of what this pipeline does"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is available for use"
    )
    config = models.JSONField(
        default=dict,
        help_text="Pipeline configuration (steps, agents, tools, parameters)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pipeline_templates'
        ordering = ['name']
        verbose_name = 'Creative Pipeline Template'
        verbose_name_plural = 'Creative Pipeline Templates'

    def __str__(self):
        return f"{self.name} ({self.slug})"


class CreativePipelineRun(models.Model):
    """
    A single execution of a pipeline template.

    Tracks status, progress, inputs, outputs, and logs.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pipeline_runs',
        help_text="User who initiated this pipeline run"
    )
    template = models.ForeignKey(
        CreativePipelineTemplate,
        on_delete=models.CASCADE,
        related_name='runs',
        help_text="Template used for this run"
    )
    # Session 324: Unified from CreativeProject
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pipeline_runs',
        help_text="Optional project to attach outputs to"
    )
    session = models.ForeignKey(
        'content.AISession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pipeline_runs',
        help_text="Optional session to attach outputs to"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the pipeline run"
    )
    current_step = models.IntegerField(
        default=0,
        help_text="Current step being executed (0-indexed)"
    )
    total_steps = models.IntegerField(
        default=0,
        help_text="Total number of steps in this pipeline"
    )
    input_payload = models.JSONField(
        default=dict,
        help_text="Original input from user (e.g. idea, parameters)"
    )
    output_payload = models.JSONField(
        default=dict,
        help_text="Final outputs (image URLs, video URLs, metadata)"
    )
    log = models.TextField(
        blank=True,
        default='',
        help_text="Human-readable log of pipeline execution"
    )
    error_message = models.TextField(
        blank=True,
        default='',
        help_text="Error message if pipeline failed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the pipeline finished (success or failure)"
    )

    class Meta:
        db_table = 'pipeline_runs'
        ordering = ['-created_at']
        verbose_name = 'Creative Pipeline Run'
        verbose_name_plural = 'Creative Pipeline Runs'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.template.name} - {self.status} ({self.id})"

    def append_log(self, message):
        """Append a message to the log with timestamp"""
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log += f"[{timestamp}] {message}\n"
        self.save(update_fields=['log', 'updated_at'])

    def mark_running(self):
        """Mark the pipeline as running"""
        self.status = 'running'
        self.save(update_fields=['status', 'updated_at'])

    def mark_completed(self):
        """Mark the pipeline as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_failed(self, error_message):
        """Mark the pipeline as failed with error message"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at', 'updated_at'])

    def update_progress(self, step_number):
        """Update the current step number"""
        self.current_step = step_number
        self.save(update_fields=['current_step', 'updated_at'])

    @property
    def progress_percentage(self):
        """Calculate progress as percentage"""
        if self.total_steps == 0:
            return 0
        return int((self.current_step / self.total_steps) * 100)

    @property
    def duration(self):
        """Calculate duration in seconds"""
        if self.completed_at:
            return (self.completed_at - self.created_at).total_seconds()
        return (timezone.now() - self.created_at).total_seconds()
