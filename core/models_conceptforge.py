"""
ConceptForge Models
===================

Session 863: Database models for ConceptForge pipeline execution tracking.

These models track RUNS and OUTPUTS only. Lab/panel configurations are
stored in code (conceptforge/labs.py, conceptforge/panels.py) for
flexibility without migrations.

Key design decisions:
- advisor_panel_snapshot: JSON snapshot for reproducibility
- inputs_snapshot: Captures what went into each stage
- Artifacts stored with version tracking
- Status tracking for monitoring and debugging
"""

import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class ConceptForgeRun(models.Model):
    """
    Represents a single ConceptForge pipeline execution.

    Created when a blog (or other content) triggers the pipeline.
    Tracks overall progress and stores the advisor panel snapshot.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    class SourceType(models.TextChoices):
        BLOG = 'blog', 'Blog Post'
        DECISION_SUMMARY = 'decision_summary', 'Decision Summary'
        RESEARCH_BRIEF = 'research_brief', 'Research Brief'
        AUDIT = 'audit', 'System Audit'
        MANUAL = 'manual', 'Manual Trigger'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Workspace linkage
    workspace = models.ForeignKey(
        'core.ProjectWorkspace', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='conceptforge_runs', db_index=True,
    )

    # Source content that triggered the pipeline
    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.BLOG
    )
    source_id = models.UUIDField(
        help_text='UUID of the source content (e.g., SelfBlog.id)'
    )
    source_title = models.CharField(
        max_length=500,
        blank=True,
        help_text='Title of source content for display'
    )

    # Domain lab assignment
    domain = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Domain lab (legal, market, tech, etc.)'
    )

    # Advisor panel snapshot (for reproducibility)
    advisor_panel_snapshot = models.JSONField(
        default=dict,
        help_text='Snapshot of advisor panel at run start'
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    current_stage = models.CharField(
        max_length=30,
        blank=True,
        help_text='Current stage being executed'
    )

    # Error tracking
    error = models.TextField(
        blank=True,
        help_text='Error message if failed'
    )

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(
        default=0,
        help_text='Total execution time in milliseconds'
    )

    # Trigger metadata
    triggered_by = models.CharField(
        max_length=50,
        default='system',
        help_text='What triggered this run (signal, manual, celery_beat)'
    )
    quality_score = models.FloatField(
        default=0.0,
        help_text='Quality score of source content that triggered run'
    )

    # User who owns this run (for permission filtering)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conceptforge_runs'
    )

    # Celery task tracking
    celery_task_id = models.CharField(max_length=100, blank=True)

    # Session 962 Phase 1: Deliberation envelope
    deliberation_session = models.ForeignKey(
        'core.DeliberationSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conceptforge_runs',
        help_text='Session 962: Unifying deliberation session wrapper'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_conceptforge_run'
        ordering = ['-created_at']
        verbose_name = 'ConceptForge Run'
        verbose_name_plural = 'ConceptForge Runs'
        indexes = [
            models.Index(fields=['source_type', 'source_id']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['domain', 'status']),
        ]

    def __str__(self):
        return f"ConceptForge: {self.source_title[:50]} ({self.domain})"

    def start(self):
        """Mark run as started."""
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def complete(self):
        """Mark run as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.save(update_fields=['status', 'completed_at', 'duration_ms', 'updated_at'])

    def fail(self, error_message: str):
        """Mark run as failed."""
        self.status = self.Status.FAILED
        self.error = error_message
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.save(update_fields=['status', 'error', 'completed_at', 'duration_ms', 'updated_at'])

    def set_current_stage(self, stage_name: str):
        """Update current stage being executed."""
        self.current_stage = stage_name
        self.save(update_fields=['current_stage', 'updated_at'])

    @property
    def progress_percentage(self) -> int:
        """Calculate progress based on completed stages."""
        total_stages = 6  # research, debate, feasibility, risk, market, synthesis
        completed = self.stages.filter(status='completed').count()
        return int((completed / total_stages) * 100)

    @property
    def stage_summary(self) -> dict:
        """Get summary of all stage statuses."""
        return {
            stage.stage_name: {
                'status': stage.status,
                'duration_ms': stage.duration_ms,
                'has_output': bool(stage.output_text),
            }
            for stage in self.stages.all()
        }


class ConceptForgeStageRun(models.Model):
    """
    Represents a single stage execution within a ConceptForge run.

    Each run has 6 stages: research, debate, feasibility, risk, market, synthesis.
    Tracks inputs, outputs, timing, and which agents/advisors contributed.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        SKIPPED = 'skipped', 'Skipped'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Parent run
    run = models.ForeignKey(
        ConceptForgeRun,
        on_delete=models.CASCADE,
        related_name='stages'
    )

    # Stage identification
    stage_name = models.CharField(
        max_length=30,
        db_index=True,
        help_text='Stage name: research, debate, feasibility, risk, market, synthesis'
    )
    stage_order = models.IntegerField(
        default=0,
        help_text='Order of execution (1-6)'
    )

    # Agent/Advisor tracking
    agent_used = models.CharField(
        max_length=100,
        blank=True,
        help_text='Core agent that executed this stage'
    )
    advisors_used = models.JSONField(
        default=list,
        help_text='Persona advisors consulted for this stage'
    )
    legendary_advisors_used = models.JSONField(
        default=list,
        help_text='Legendary advisors that provided positions'
    )

    # Input snapshot (for reproducibility and debugging)
    inputs_snapshot = models.JSONField(
        default=dict,
        help_text='Inputs provided to this stage'
    )

    # Output
    output_text = models.TextField(
        blank=True,
        help_text='Main output text from this stage'
    )
    output_metadata = models.JSONField(
        default=dict,
        help_text='Structured metadata from output'
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    error = models.TextField(
        blank=True,
        help_text='Error message if failed'
    )

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(
        default=0,
        help_text='Execution time in milliseconds'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_conceptforge_stage_run'
        ordering = ['run', 'stage_order']
        verbose_name = 'ConceptForge Stage Run'
        verbose_name_plural = 'ConceptForge Stage Runs'
        unique_together = ['run', 'stage_name']

    def __str__(self):
        return f"{self.run.source_title[:30]} - {self.stage_name}"

    def start(self):
        """Mark stage as started."""
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])
        # Update parent run's current stage
        self.run.set_current_stage(self.stage_name)

    def complete(self, output_text: str = '', output_metadata: dict = None):  # type: ignore
        """Mark stage as completed with output."""
        self.status = self.Status.COMPLETED
        self.output_text = output_text
        if output_metadata:
            self.output_metadata = output_metadata
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.save()

    def fail(self, error_message: str):
        """Mark stage as failed."""
        self.status = self.Status.FAILED
        self.error = error_message
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.save(update_fields=['status', 'error', 'completed_at', 'duration_ms', 'updated_at'])

    def skip(self, reason: str = ''):
        """Mark stage as skipped."""
        self.status = self.Status.SKIPPED
        self.error = reason
        self.save(update_fields=['status', 'error', 'updated_at'])


class ConceptForgeArtifact(models.Model):
    """
    Represents an artifact (document) produced by a ConceptForge run.

    The final synthesis stage produces the main dossier, but individual
    stages can also produce artifacts (research brief, debate transcript, etc.)
    """

    class Kind(models.TextChoices):
        MARKDOWN = 'md', 'Markdown'
        PDF = 'pdf', 'PDF'
        JSON = 'json', 'JSON'
        HTML = 'html', 'HTML'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Parent run
    run = models.ForeignKey(
        ConceptForgeRun,
        on_delete=models.CASCADE,
        related_name='artifacts'
    )

    # Optional: which stage produced this
    stage = models.ForeignKey(
        ConceptForgeStageRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='artifacts'
    )

    # Artifact identification
    name = models.CharField(
        max_length=200,
        help_text='Artifact name (e.g., "Research Brief", "Final Dossier")'
    )
    kind = models.CharField(
        max_length=10,
        choices=Kind.choices,
        default=Kind.MARKDOWN
    )

    # Content
    content = models.TextField(
        blank=True,
        help_text='Artifact content (for md/json/html)'
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='Path to file if stored in workspace'
    )

    # Versioning
    version = models.IntegerField(
        default=1,
        help_text='Version number for this artifact'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Is this the primary/final dossier artifact?'
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text='Additional metadata (word count, sections, etc.)'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_conceptforge_artifact'
        ordering = ['-created_at']
        verbose_name = 'ConceptForge Artifact'
        verbose_name_plural = 'ConceptForge Artifacts'

    def __str__(self):
        return f"{self.name} v{self.version} ({self.kind})"

    @classmethod
    def create_dossier(cls, run: 'ConceptForgeRun', content: str, metadata: dict = None):  # type: ignore
        """Create the primary dossier artifact for a run."""
        # Get current max version
        existing = cls.objects.filter(
            run=run,
            is_primary=True
        ).order_by('-version').first()

        version = (existing.version + 1) if existing else 1

        return cls.objects.create(
            run=run,
            name=f"Dossier: {run.source_title[:100]}",
            kind=cls.Kind.MARKDOWN,
            content=content,
            version=version,
            is_primary=True,
            metadata=metadata or {},
        )
