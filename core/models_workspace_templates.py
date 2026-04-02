"""
Workspace Templates — Business-in-a-Box Presets
================================================

Defines reusable workspace templates that configure a ProjectWorkspace
as a self-contained business unit with pre-configured pipeline stages,
agent pools, deliverable categories, and default settings.

Templates are the foundation for "Create Newsletter Business",
"Create LeadGen Business", etc.
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class WorkspaceTemplate(models.Model):
    """
    A reusable template that defines how a workspace operates as a business unit.

    Example:
        template = WorkspaceTemplate.objects.get(slug='newsletter')
        workspace = template.provision(user=user, name="My Newsletter")
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='', blank=True)
    category = models.CharField(max_length=50, default='general', db_index=True)

    # Pipeline definition — ordered stages that content flows through
    # Example: [{"name": "Research", "agent": "ResearchAgent", "auto": true},
    #           {"name": "Draft", "agent": "ContentWriterAgent", "auto": true},
    #           {"name": "Review", "agent": null, "auto": false, "requires_approval": true},
    #           {"name": "Publish", "agent": null, "auto": false}]
    pipeline_stages = models.JSONField(
        default=list,
        help_text="Ordered pipeline stages with agent assignments and automation flags",
    )

    # Agent pool — which agents are available in this workspace type
    # Example: ["ResearchAgent", "ContentWriterAgent", "EditorAgent", "SEOOptimizerAgent"]
    agent_pool = models.JSONField(
        default=list,
        help_text="List of agent names available for this workspace type",
    )

    # Spider subscriptions — which data feeds this workspace consumes
    # Example: ["techcrunch", "hackernews", "reddit", "newsapi"]
    spider_subscriptions = models.JSONField(
        default=list,
        help_text="Spider names this workspace type subscribes to",
    )

    # Deliverable categories — what types of output this workspace produces
    # Example: ["Newsletter Draft", "Newsletter HTML", "Subject Lines", "Subscriber Report"]
    deliverable_categories = models.JSONField(
        default=list,
        help_text="Deliverable categories pre-configured for this workspace",
    )

    # Default settings for workspaces created from this template
    # Example: {"publish_schedule": "weekly", "max_drafts": 5, "auto_publish": false,
    #           "quality_threshold": 0.7, "review_required": true}
    default_settings = models.JSONField(
        default=dict,
        help_text="Default configuration applied when creating a workspace from this template",
    )

    # Workspace quotas
    # Example: {"max_deliverables_per_day": 10, "max_agent_runs_per_hour": 20,
    #           "max_initiatives": 5}
    default_quotas = models.JSONField(
        default=dict,
        help_text="Resource limits applied to workspaces created from this template",
    )

    # Template metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'workspace_templates'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}" if self.icon else self.name

    def provision(self, user, name, description=''):
        """Create a new ProjectWorkspace from this template."""
        from core.models_skin_layer import ProjectWorkspace

        workspace = ProjectWorkspace.objects.create(
            user=user,
            name=name,
            description=description or self.description,
            workspace_type='sandbox',
            root_path=f'/app/workspaces/{self.slug}/{uuid.uuid4().hex[:8]}',
        )

        # Apply template config via WorkspaceConfig
        WorkspaceConfig.objects.create(
            workspace=workspace,
            template=self,
            pipeline_config=self.pipeline_stages,
            agent_pool=self.agent_pool,
            spider_subscriptions=self.spider_subscriptions,
            deliverable_categories=self.deliverable_categories,
            settings=self.default_settings,
            quotas=self.default_quotas,
            status='active',
        )

        return workspace


class WorkspaceConfig(models.Model):
    """
    Business-unit configuration for a ProjectWorkspace.

    Extends ProjectWorkspace with everything needed to operate as
    a self-contained business: pipeline, agents, settings, metrics.
    One-to-one relationship — every business workspace has exactly one config.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.OneToOneField(
        'core.ProjectWorkspace',
        on_delete=models.CASCADE,
        related_name='config',
    )
    template = models.ForeignKey(
        WorkspaceTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instances',
    )

    # Business status
    STATUS_CHOICES = [
        ('setup', 'Setting Up'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='setup',
        db_index=True,
    )

    # Pipeline configuration (copied from template, can be customized)
    pipeline_config = models.JSONField(default=list)
    agent_pool = models.JSONField(default=list)
    spider_subscriptions = models.JSONField(default=list)
    deliverable_categories = models.JSONField(default=list)

    # Workspace brief — what this business does, who it serves, what to focus on
    # This feeds into every pipeline stage as context for agents
    workspace_brief = models.JSONField(
        default=dict,
        blank=True,
        help_text='{"topic": "...", "audience": "...", "tone": "...", "key_sources": [...], "focus_areas": [...], "notes": "..."}',
    )

    # Workspace-specific settings (merged over template defaults)
    settings = models.JSONField(default=dict)

    # Resource quotas
    quotas = models.JSONField(default=dict)

    # Governance mode override (null = use global)
    governance_mode = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Override global governance mode for this workspace (null = inherit global)",
    )

    # Metrics snapshot (updated periodically)
    metrics_snapshot = models.JSONField(
        default=dict,
        help_text="Cached workspace metrics: deliverable counts, agent runs, costs, etc.",
    )
    metrics_updated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'workspace_configs'

    def __str__(self):
        tmpl = self.template.name if self.template else 'Custom'
        return f"{self.workspace.name} ({tmpl})"

    @property
    def effective_governance_mode(self):
        """Return workspace-specific mode or fall back to global."""
        if self.governance_mode:
            return self.governance_mode
        try:
            from core.models_governance import GovernanceState
            gs = GovernanceState.objects.filter(scope='global').first()
            return gs.effective_mode if gs else 'normal'
        except Exception:
            return 'normal'

    def get_quota(self, key, default=None):
        """Get a quota value with fallback to template defaults."""
        val = self.quotas.get(key)
        if val is not None:
            return val
        if self.template:
            return self.template.default_quotas.get(key, default)
        return default

    def update_metrics(self):
        """Refresh the metrics snapshot from live data."""
        from core.models_deliverables import Deliverable
        from django.db.models import Count

        deliverables = Deliverable.objects.filter(workspace=self.workspace)
        by_status = dict(
            deliverables.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        self.metrics_snapshot = {
            'deliverables_total': deliverables.count(),
            'deliverables_by_status': by_status,
            'deliverables_saved': deliverables.filter(is_saved=True).count(),
        }
        self.metrics_updated_at = timezone.now()
        self.save(update_fields=['metrics_snapshot', 'metrics_updated_at'])


class PipelineRun(models.Model):
    """
    A single execution of a workspace's pipeline.

    Tracks each stage's status, timing, and output references so
    the frontend can show real-time progress.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.CASCADE,
        related_name='pipeline_runs',
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)

    # Pipeline config snapshot (frozen at run time)
    pipeline_snapshot = models.JSONField(default=list)

    # Per-stage status tracking
    # [{stage_index: 0, name: "Research", status: "completed", started_at: ..., finished_at: ...,
    #   agent: "ResearchAgent", task_id: "...", output: {...}}, ...]
    stage_results = models.JSONField(default=list)

    current_stage_index = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default='')

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        db_table = 'workspace_pipeline_runs'
        ordering = ['-created_at']

    def __str__(self):
        return f"PipelineRun {self.id} ({self.status})"

    @property
    def duration_seconds(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    @property
    def progress_pct(self):
        total = len(self.pipeline_snapshot)
        if total == 0:
            return 0
        done = sum(1 for s in self.stage_results if s.get('status') in ('completed', 'skipped'))
        return int((done / total) * 100)
