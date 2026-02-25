"""
Session 1074: ExecutionRun model — per-run ephemeral executor.
Session 1075: Repo registry model — multi-repo architecture.

Tracks plan-based execution runs with artifact capture (logs, diffs,
changed files). Integrates with the three-way collaboration protocol.

See: docs/decisions/ADR-0001-execution-per-run-ephemeral-containers.md
     docs/decisions/ADR-0002-moderate-dangerous-action-policy.md
"""

import uuid

from django.conf import settings as django_settings
from django.db import models


class Repo(models.Model):
    """A registered repository that the executor can operate on."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200, unique=True,
        help_text='Human-readable repo name (e.g. "donkey-betz-platform")',
    )
    repo_url = models.URLField(
        unique=True,
        help_text='Git clone URL',
    )
    default_base_branch = models.CharField(
        max_length=100, default='main',
        help_text='Default branch to clone from',
    )
    allowed_base_branches = models.JSONField(
        default=list,
        help_text='Branches allowed as base for executor runs',
    )
    protected_branches = models.JSONField(
        default=list,
        help_text='Branches that cannot be pushed to directly',
    )
    policy_profile = models.CharField(
        max_length=50, default='moderate',
        help_text='Policy profile name (moderate = Tier A/B/C)',
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'executor_repos'
        ordering = ['name']

    def __str__(self) -> str:
        return f'{self.name} ({self.repo_url})'


class ExecutionRun(models.Model):
    """A single executor run: clone repo, execute plan, capture artifacts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ── Status lifecycle ──────────────────────────────────────────────────
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='queued', db_index=True
    )

    # ── Repo & branch ────────────────────────────────────────────────────
    repo = models.ForeignKey(
        Repo,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='runs',
        help_text='Registry repo (null for runs created before repo registry)',
    )
    repo_url = models.URLField(
        default='https://github.com/clwest/donkey-betz-platform',
        help_text='Always pinned to settings.EXECUTOR_REPO_URL in single-repo mode',
    )
    base_branch = models.CharField(
        max_length=100, default='main',
        help_text='Branch to clone from (always main in single-repo mode)',
    )
    working_branch = models.CharField(
        max_length=200, blank=True,
        help_text='Auto-created branch: executor/<run_id>-<slug>',
    )

    # ── Plan ─────────────────────────────────────────────────────────────
    plan_json = models.JSONField(
        default=dict,
        help_text='Normalized PlanV1 JSON: {version, title, context, steps}',
    )
    plan_summary = models.TextField(
        blank=True,
        help_text='Human-readable summary of what this run does',
    )

    # ── Step-level execution state ─────────────────────────────────────
    current_step_index = models.IntegerField(
        default=0,
        help_text='Index of the next step to execute (resume point after approval)',
    )
    awaiting_approval_step_id = models.CharField(
        max_length=100, blank=True,
        help_text='Step ID that caused the run to pause for approval',
    )
    approved_steps = models.JSONField(
        default=list,
        help_text='List of step IDs that have been explicitly approved',
    )

    # ── Policy ───────────────────────────────────────────────────────────
    blocked_steps = models.JSONField(
        default=list,
        help_text='Steps blocked by Tier C policy',
    )
    approval_required_steps = models.JSONField(
        default=list,
        help_text='Steps requiring Tier B approval',
    )
    approved_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_executor_runs',
        help_text='User who approved Tier B steps',
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # ── Artifacts ────────────────────────────────────────────────────────
    log_text = models.TextField(
        blank=True,
        help_text='Combined stdout/stderr from all executed steps',
    )
    diff_patch = models.TextField(
        blank=True,
        help_text='git diff output after execution',
    )
    changed_files = models.JSONField(
        default=list,
        help_text='List of changed file paths from git status',
    )
    test_summary = models.JSONField(
        default=dict, blank=True,
        help_text='Optional: parsed test results',
    )

    # ── Execution metadata ───────────────────────────────────────────────
    steps_completed = models.IntegerField(default=0)
    steps_total = models.IntegerField(default=0)
    current_step = models.CharField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)
    execution_time_seconds = models.FloatField(null=True, blank=True)

    # ── Conversation linkage ─────────────────────────────────────────────
    conversation_id = models.CharField(
        max_length=255, blank=True, db_index=True,
        help_text='Collaboration protocol conversation to post updates to',
    )

    # ── Ownership ────────────────────────────────────────────────────────
    created_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='executor_runs',
    )

    # ── Timestamps ───────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        db_table = 'executor_runs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['conversation_id']),
        ]

    def __str__(self) -> str:
        return f'ExecutionRun {self.id} [{self.status}]'

    # ── Lifecycle helpers ────────────────────────────────────────────────

    def start(self) -> None:
        from django.utils import timezone
        self.status = 'running'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def succeed(self, diff: str = '', changed: list | None = None, log: str = '') -> None:
        from django.utils import timezone
        self.status = 'succeeded'
        self.completed_at = timezone.now()
        if self.started_at:
            self.execution_time_seconds = (self.completed_at - self.started_at).total_seconds()
        self.diff_patch = diff
        self.changed_files = changed or []
        self.log_text = log
        self.save()

    def fail(self, error: str, log: str = '') -> None:
        from django.utils import timezone
        self.status = 'failed'
        self.completed_at = timezone.now()
        if self.started_at:
            self.execution_time_seconds = (self.completed_at - self.started_at).total_seconds()
        self.error_message = error
        self.log_text = log
        self.save()

    def cancel(self) -> None:
        from django.utils import timezone
        self.status = 'canceled'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def request_approval(self, step_id: str = '') -> None:
        self.status = 'awaiting_approval'
        self.awaiting_approval_step_id = step_id
        self.save(update_fields=['status', 'awaiting_approval_step_id'])

    def approve(self, user) -> None:
        """Legacy: approve entire run (blanket approval)."""
        from django.utils import timezone
        self.approved_by = user
        self.approved_at = timezone.now()
        self.status = 'queued'
        self.awaiting_approval_step_id = ''
        self.save(update_fields=['approved_by', 'approved_at', 'status', 'awaiting_approval_step_id'])

    def approve_step(self, user, step_id: str) -> None:
        """Approve a specific step and re-queue the run."""
        from django.utils import timezone
        approved = self.approved_steps or []
        if step_id not in approved:
            approved.append(step_id)
        self.approved_steps = approved
        self.approved_by = user
        self.approved_at = timezone.now()
        self.status = 'queued'
        self.awaiting_approval_step_id = ''
        self.save(update_fields=[
            'approved_steps', 'approved_by', 'approved_at',
            'status', 'awaiting_approval_step_id',
        ])

    def generate_working_branch(self) -> str:
        """Generate a working branch name from the run ID and summary."""
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', (self.plan_summary or 'run')[:40].lower()).strip('-')
        branch = f'executor/{str(self.id)[:8]}-{slug}'
        self.working_branch = branch
        self.save(update_fields=['working_branch'])
        return branch
