"""
Workspace Hosted Previews + Multi-Repo Launchpad + Magic-Link Review

Models for deploying preview environments from workspace project bundles,
generating time-limited magic links for customer review, and capturing
structured feedback mapped to repos/commits.

Initiative: 2870f089-2439-4089-8d0e-b801e9ae0edf
"""

import hashlib
import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


# ── WorkspaceProject ──────────────────────────────────────────────────────


class WorkspaceProject(models.Model):
    """Bundle of repos that form a deployable project within a workspace."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "core.ProjectWorkspace",
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    default_preview_ttl_minutes = models.IntegerField(
        default=4320, help_text="Default TTL for preview environments (72h)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_workspace_projects"
        unique_together = [("workspace", "slug")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"


# ── ProjectRepo ───────────────────────────────────────────────────────────


class ProjectRepo(models.Model):
    """One repo in a project bundle (backend, web, or mobile)."""

    class Provider(models.TextChoices):
        GITHUB = "github", "GitHub"
        GITLAB = "gitlab", "GitLab"
        BITBUCKET = "bitbucket", "Bitbucket"

    class RepoType(models.TextChoices):
        BACKEND = "backend", "Backend"
        WEB = "web", "Web"
        MOBILE = "mobile", "Mobile"

    class BuildSystem(models.TextChoices):
        VERCEL = "vercel", "Vercel"
        RAILWAY = "railway", "Railway"
        FLYIO = "flyio", "Fly.io"
        EAS = "eas", "Expo EAS"
        NONE = "none", "None"

    class OutputKind(models.TextChoices):
        SERVICE = "service", "Service (API/Worker)"
        STATIC_SITE = "static_site", "Static Site"
        MOBILE_ARTIFACT = "mobile_artifact", "Mobile Build Artifact"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        WorkspaceProject, on_delete=models.CASCADE, related_name="repos"
    )
    name = models.CharField(max_length=200, help_text="e.g. norman-backend")
    provider = models.CharField(
        max_length=20, choices=Provider.choices, default=Provider.GITHUB
    )
    repo_url = models.URLField()
    provider_repo_id = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=20, choices=RepoType.choices)
    default_ref = models.CharField(max_length=200, default="main")
    build_system = models.CharField(
        max_length=20, choices=BuildSystem.choices, default=BuildSystem.NONE
    )
    build_command = models.CharField(max_length=500, blank=True)
    output_kind = models.CharField(
        max_length=20, choices=OutputKind.choices, default=OutputKind.SERVICE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_project_repos"
        ordering = ["type", "name"]

    def __str__(self):
        return f"{self.name} ({self.type})"


# ── ProjectEnvVar ─────────────────────────────────────────────────────────


class ProjectEnvVar(models.Model):
    """Environment variable scoped by environment and optionally by repo."""

    class Environment(models.TextChoices):
        PREVIEW = "preview", "Preview"
        STAGING = "staging", "Staging"
        PRODUCTION = "production", "Production"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        WorkspaceProject, on_delete=models.CASCADE, related_name="env_vars"
    )
    repo = models.ForeignKey(
        ProjectRepo, on_delete=models.CASCADE, null=True, blank=True,
        related_name="env_vars", help_text="Null = shared across all repos"
    )
    environment = models.CharField(
        max_length=20, choices=Environment.choices, default=Environment.PREVIEW
    )
    key = models.CharField(max_length=200)
    value = models.TextField()
    is_secret = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_project_env_vars"
        unique_together = [("project", "repo", "environment", "key")]

    def __str__(self):
        masked = "****" if self.is_secret else self.value[:30]
        return f"{self.key}={masked} ({self.environment})"


# ── PreviewEnvironment ────────────────────────────────────────────────────


class PreviewEnvironment(models.Model):
    """An ephemeral preview environment for a project."""

    class Status(models.TextChoices):
        PROVISIONING = "provisioning", "Provisioning"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"
        DESTROYED = "destroyed", "Destroyed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        WorkspaceProject, on_delete=models.CASCADE, related_name="preview_envs"
    )
    name = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PROVISIONING
    )
    ttl_expires_at = models.DateTimeField(db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_preview_environments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def is_expired(self):
        return timezone.now() > self.ttl_expires_at

    @property
    def web_url(self):
        """Return the primary web preview URL if available."""
        svc = self.services.filter(service_type="web").first()
        return svc.public_url if svc else None

    @property
    def api_url(self):
        """Return the primary API preview URL if available."""
        svc = self.services.filter(service_type="api").first()
        return svc.public_url if svc else None


# ── PreviewDeployment ─────────────────────────────────────────────────────


class PreviewDeployment(models.Model):
    """One deployment event across all repos in a preview environment."""

    class Trigger(models.TextChoices):
        MANUAL = "manual", "Manual"
        PUSH = "push", "Git Push"
        SCHEDULE = "schedule", "Scheduled"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    preview_env = models.ForeignKey(
        PreviewEnvironment, on_delete=models.CASCADE, related_name="deployments"
    )
    trigger = models.CharField(
        max_length=20, choices=Trigger.choices, default=Trigger.MANUAL
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.QUEUED
    )
    git_context = models.JSONField(
        default=dict, help_text="Refs/SHAs per repo"
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_preview_deployments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Deploy {self.id!s:.8} ({self.status})"

    @property
    def duration_seconds(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


# ── DeployJob ─────────────────────────────────────────────────────────────


class DeployJob(models.Model):
    """Per-repo build job within a deployment."""

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deployment = models.ForeignKey(
        PreviewDeployment, on_delete=models.CASCADE, related_name="jobs"
    )
    repo = models.ForeignKey(
        ProjectRepo, on_delete=models.CASCADE, related_name="deploy_jobs"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.QUEUED
    )
    provider_job_id = models.CharField(max_length=300, blank=True)
    logs_url = models.URLField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "core"
        db_table = "core_deploy_jobs"
        ordering = ["repo__type"]

    def __str__(self):
        return f"{self.repo.name} ({self.status})"


# ── PreviewService ────────────────────────────────────────────────────────


class PreviewService(models.Model):
    """A running service/URL produced by a preview environment."""

    class ServiceType(models.TextChoices):
        WEB = "web", "Web"
        API = "api", "API"
        WORKER = "worker", "Worker"
        ADMIN = "admin", "Admin"

    class HealthStatus(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        HEALTHY = "healthy", "Healthy"
        UNHEALTHY = "unhealthy", "Unhealthy"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    preview_env = models.ForeignKey(
        PreviewEnvironment, on_delete=models.CASCADE, related_name="services"
    )
    repo = models.ForeignKey(
        ProjectRepo, on_delete=models.CASCADE, related_name="preview_services"
    )
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    public_url = models.URLField(blank=True)
    internal_url = models.URLField(blank=True)
    provider_metadata = models.JSONField(default=dict, blank=True)
    health_status = models.CharField(
        max_length=20, choices=HealthStatus.choices, default=HealthStatus.UNKNOWN
    )
    last_health_check_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "core"
        db_table = "core_preview_services"

    def __str__(self):
        return f"{self.service_type}: {self.public_url or '(no url)'}"


# ── MagicLink ─────────────────────────────────────────────────────────────


class MagicLink(models.Model):
    """Time-limited, scoped access token for customer review."""

    class Scope(models.TextChoices):
        REVIEW = "review", "Review (can leave feedback)"
        VIEW_ONLY = "view_only", "View Only"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    preview_env = models.ForeignKey(
        PreviewEnvironment, on_delete=models.CASCADE, related_name="magic_links"
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    label = models.CharField(max_length=200, help_text='e.g. "Kurt review link"')
    scope = models.CharField(
        max_length=20, choices=Scope.choices, default=Scope.REVIEW
    )
    expires_at = models.DateTimeField(db_index=True)
    max_uses = models.IntegerField(null=True, blank=True)
    uses = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "core"
        db_table = "core_magic_links"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.label} (expires {self.expires_at})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_exhausted(self):
        return self.max_uses is not None and self.uses >= self.max_uses

    @property
    def is_valid(self):
        return not self.is_expired and not self.is_exhausted

    @classmethod
    def generate_token(cls):
        """Generate a secure random token and return (raw_token, token_hash)."""
        raw = secrets.token_urlsafe(32)
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return raw, hashed

    @classmethod
    def lookup(cls, raw_token):
        """Find a MagicLink by raw token. Returns None if not found or invalid."""
        hashed = hashlib.sha256(raw_token.encode()).hexdigest()
        try:
            link = cls.objects.select_related("preview_env__project").get(token_hash=hashed)
        except cls.DoesNotExist:
            return None
        if not link.is_valid:
            return None
        return link

    def record_use(self):
        """Increment usage counter."""
        self.uses = models.F("uses") + 1
        self.save(update_fields=["uses"])


# ── FeedbackItem ──────────────────────────────────────────────────────────


class FeedbackItem(models.Model):
    """Structured feedback from a customer or internal reviewer."""

    class Source(models.TextChoices):
        MAGIC_LINK = "magic_link", "Magic Link"
        INTERNAL = "internal", "Internal"

    class Severity(models.TextChoices):
        NIT = "nit", "Nit"
        IMPORTANT = "important", "Important"
        BLOCKER = "blocker", "Blocker"

    class Status(models.TextChoices):
        NEW = "new", "New"
        TRIAGED = "triaged", "Triaged"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        WONT_FIX = "wont_fix", "Won't Fix"

    class Category(models.TextChoices):
        COPY = "copy", "Copy/Text"
        DESIGN = "design", "Design/Layout"
        BUG = "bug", "Bug"
        FEATURE = "feature", "Feature Request"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    preview_env = models.ForeignKey(
        PreviewEnvironment, on_delete=models.CASCADE, related_name="feedback_items"
    )
    magic_link = models.ForeignKey(
        MagicLink, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="feedback_items"
    )
    source = models.CharField(
        max_length=20, choices=Source.choices, default=Source.MAGIC_LINK
    )
    page_url = models.URLField()
    page_path = models.CharField(max_length=500, blank=True)
    page_title = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.IMPORTANT
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW
    )
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OTHER
    )
    client_context = models.JSONField(
        default=dict, blank=True,
        help_text="Browser context: userAgent, viewport, locale"
    )
    # Reporter info (for magic link reviewers)
    reporter_name = models.CharField(max_length=200, blank=True)
    reporter_email = models.EmailField(blank=True)
    reporter_phone = models.CharField(max_length=30, blank=True)
    # Internal tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+"
    )
    triaged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+"
    )
    triaged_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    # Linking
    linked_repo = models.ForeignKey(
        ProjectRepo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="feedback_items"
    )
    linked_commit_sha = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_feedback_items"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["preview_env", "status"]),
            models.Index(fields=["preview_env", "severity"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.message[:60]}"
