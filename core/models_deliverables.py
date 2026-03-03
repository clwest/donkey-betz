"""
Deliverables Model - Session 819: Deliverables Marketplace

Transforms Operations tab from developer-focused log viewer into a
"Deliverables Marketplace" - a product catalog of AI outputs with
professional presentation, library management, and export capabilities.

This model standardizes agent outputs into a consistent "envelope" format
that can be displayed as product cards, saved to libraries, and exported.
"""

__all__ = [
    'DeliverableType',
    'ContentFormat',
    'Deliverable',
    'DeliverableExport',
    'DeliverableCollection',
    'DeliverableEvent',
]

import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify


class DeliverableType(models.TextChoices):
    """Types of deliverables that agents can produce."""
    DOCUMENT = 'document', 'Document'
    IMAGE = 'image', 'Image'
    VIDEO = 'video', 'Video'
    AUDIO = 'audio', 'Audio'
    CODE = 'code', 'Code'
    ANALYSIS = 'analysis', 'Analysis'
    REPORT = 'report', 'Report'
    TEMPLATE = 'template', 'Template'
    RESEARCH = 'research', 'Research'
    STRATEGY = 'strategy', 'Strategy'
    PLAN = 'plan', 'Plan'
    SCRIPT = 'script', 'Script'


class ContentFormat(models.TextChoices):
    """Content format types."""
    TEXT = 'text', 'Plain Text'
    MARKDOWN = 'markdown', 'Markdown'
    HTML = 'html', 'HTML'
    JSON = 'json', 'JSON'
    PYTHON = 'python', 'Python'
    TYPESCRIPT = 'typescript', 'TypeScript'
    JAVASCRIPT = 'javascript', 'JavaScript'


class Deliverable(models.Model):
    """
    A standardized envelope for agent outputs.

    Transforms raw agent results into a displayable product with:
    - Consistent metadata (title, type, category, tags)
    - Quality metrics (quality_score, confidence_score)
    - Library features (save, clone, templateize)
    - Export capabilities (PDF, DOCX, HTML)
    - Developer traceability (tool calls, raw output)

    Example:
        deliverable = Deliverable.objects.create(
            title="Blog Post: AI Market Analysis 2026",
            deliverable_type='document',
            category='Marketing',
            agent_name='ContentWriterAgent',
            content='# AI Market Analysis...',
            content_format='markdown'
        )
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=255,
        help_text="Human-readable title for the deliverable"
    )
    slug = models.SlugField(
        max_length=280,
        unique=True,
        help_text="URL-safe identifier"
    )

    # Classification
    deliverable_type = models.CharField(
        max_length=20,
        choices=DeliverableType.choices,
        default=DeliverableType.DOCUMENT,
        db_index=True
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Business category (e.g., Marketing, Development, Research)"
    )
    tags = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Tags for filtering and discovery"
    )

    # Session 843: Orchestration Contract fields
    trace_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Session 843: Trace ID for cross-artifact linking"
    )
    parent_object_type = models.CharField(
        max_length=50, blank=True,
        help_text="Session 843: Type of parent (agent_execution, conversation)"
    )
    parent_object_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Session 843: ID of parent object"
    )

    # Session 862: Content Flow Traceability - Real FKs for proper relationships
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliverables',
        help_text="Session 862: Initiative that produced this deliverable"
    )
    dream = models.ForeignKey(
        'core.AgentDream',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliverables',
        help_text="Session 862: Dream that originated this deliverable"
    )
    self_blog = models.ForeignKey(
        'core.SelfBlog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliverables',
        help_text="Session 862: SelfBlog content for this deliverable"
    )
    podcast_episode = models.ForeignKey(
        'core.PodcastEpisode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliverables',
        help_text="Session 862: Podcast episode for this deliverable"
    )

    # Source
    source_operation = models.ForeignKey(
        'WorkspaceOperation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliverables',
        help_text="The workspace operation that produced this deliverable"
    )
    agent_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Name of the agent that created this"
    )
    agent_task = models.TextField(
        blank=True,
        help_text="The task/prompt given to the agent"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deliverables',
        null=True,
        blank=True,
        help_text="User who owns this deliverable"
    )

    # Content
    content = models.TextField(
        help_text="The actual deliverable content"
    )
    content_format = models.CharField(
        max_length=20,
        choices=ContentFormat.choices,
        default=ContentFormat.TEXT,
        help_text="Format of the content (for rendering)"
    )
    preview_content = models.TextField(
        blank=True,
        help_text="Truncated preview for card display"
    )
    thumbnail_url = models.URLField(
        blank=True,
        help_text="Thumbnail image URL for visual deliverables"
    )

    # Quality Metrics
    quality_score = models.FloatField(
        default=0.0,
        help_text="AI-assessed quality score (0.0 to 1.0)"
    )
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Agent confidence in the output (0.0 to 1.0)"
    )

    # Library Features
    is_saved = models.BooleanField(
        default=False,
        db_index=True,
        help_text="User has saved this to their library"
    )
    is_template = models.BooleanField(
        default=False,
        db_index=True,
        help_text="This deliverable is a reusable template"
    )
    is_starred = models.BooleanField(
        default=False,
        help_text="User has starred/favorited this"
    )
    clone_count = models.IntegerField(
        default=0,
        help_text="Number of times this has been cloned"
    )
    cloned_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clones',
        help_text="Original deliverable if this is a clone"
    )

    # Execution Info (for Trace Drawer)
    execution_time_ms = models.IntegerField(
        default=0,
        help_text="How long the agent took to produce this"
    )
    llm_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text="Cost of LLM calls in USD"
    )
    tool_calls = models.JSONField(
        default=list,
        help_text="List of tool calls made during execution"
    )
    raw_output = models.JSONField(
        default=dict,
        help_text="Complete raw output from the agent (for debugging)"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata (file paths, URLs, etc.)"
    )

    # Session G2: Data sensitivity + retention
    DATA_SENSITIVITY_CHOICES = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
    ]
    data_sensitivity = models.CharField(
        max_length=20,
        choices=DATA_SENSITIVITY_CHOICES,
        default='internal',
        db_index=True,
        help_text="Data sensitivity level for retention and redaction policies"
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pinned deliverables override retention policies (never auto-deleted)"
    )

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ready',
        db_index=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_deliverables'
        ordering = ['-created_at']
        verbose_name = 'Deliverable'
        verbose_name_plural = 'Deliverables'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['deliverable_type', '-created_at']),
            models.Index(fields=['agent_name', '-created_at']),
            models.Index(fields=['is_saved', '-created_at']),
            models.Index(fields=['is_template', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            # Session 862: Content Flow indexes
            models.Index(fields=['initiative', '-created_at']),
            models.Index(fields=['dream', '-created_at']),
            # Session G2: Retention query index
            models.Index(fields=['data_sensitivity', '-created_at']),
        ]

    def __str__(self):
        type_icon = {
            'document': '📄',
            'image': '🖼️',
            'video': '🎬',
            'audio': '🎵',
            'code': '💻',
            'analysis': '📊',
            'report': '📋',
            'template': '📐',
            'research': '🔬',
            'strategy': '🎯',
            'plan': '📝',
            'script': '📜',
        }.get(self.deliverable_type, '📦')
        return f"{type_icon} {self.title}"

    def save(self, *args, **kwargs):
        # Auto-generate slug if not set
        if not self.slug:
            base_slug = slugify(self.title)[:250]
            slug = base_slug
            counter = 1
            while Deliverable.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Auto-generate preview if not set
        if not self.preview_content and self.content:
            self.preview_content = self.content[:500]
            if len(self.content) > 500:
                self.preview_content += '...'

        super().save(*args, **kwargs)

    @property
    def is_cloned(self) -> bool:
        """Check if this is a clone of another deliverable."""
        return self.cloned_from is not None

    @property
    def word_count(self) -> int:
        """Approximate word count of the content."""
        return len(self.content.split())

    @property
    def line_count(self) -> int:
        """Line count of the content."""
        return len(self.content.split('\n'))


class DeliverableExport(models.Model):
    """
    Track exports of deliverables to different formats.
    """

    EXPORT_FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
        ('json', 'JSON'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deliverable = models.ForeignKey(
        Deliverable,
        on_delete=models.CASCADE,
        related_name='exports'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deliverable_exports'
    )
    export_format = models.CharField(
        max_length=20,
        choices=EXPORT_FORMAT_CHOICES
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to exported file (if stored)"
    )
    file_url = models.URLField(
        blank=True,
        help_text="Download URL for exported file"
    )
    file_size_bytes = models.IntegerField(
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_deliverable_exports'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.deliverable.title} → {self.export_format.upper()}"


class DeliverableCollection(models.Model):
    """
    User-created collections for organizing deliverables.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deliverable_collections'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deliverables = models.ManyToManyField(
        Deliverable,
        related_name='collections',
        blank=True
    )
    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_deliverable_collections'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.deliverables.count()} items)"

    @property
    def item_count(self) -> int:
        return self.deliverables.count()


class DeliverableEvent(models.Model):
    """
    Lightweight event tracking for deliverable interactions.

    Used by the Stage 3 Evaluation Dashboard to compute ATR-24h
    (Action-Taken Rate within 24 hours) and other engagement metrics.
    """

    EVENT_TYPES = [
        ('synthesis_viewed', 'Synthesis Viewed'),
        ('deliverable_saved', 'Deliverable Saved'),
        ('deliverable_exported', 'Deliverable Exported'),
        ('shared', 'Shared'),
        ('task_created', 'Task Created'),
        ('followup_created', 'Follow-up Created'),
        ('action_taken', 'Action Taken'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deliverable = models.ForeignKey(
        Deliverable,
        on_delete=models.CASCADE,
        related_name='events',
    )
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Where the event originated: pa_tool, frontend, api",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_deliverable_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['deliverable', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} on {self.deliverable_id} at {self.created_at}"
