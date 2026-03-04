"""
Session 856: Diagnostic Pipeline Models

Transform audit output from "stuff failed again" to "here's the one root issue
driving 77 failures, here's what we changed, here's proof it worked."

Key Principle: Separate Detection (what) -> Diagnosis (why) -> Prescription (fix)

Models:
- FailureSignature: Groups failures by stable signature (e.g., OPENAI_429_QUOTA)
- FailureDetection: Raw failure recording (Phase 1 - What happened)
- FailureDiagnosis: Root cause analysis with evidence (Phase 2 - Why it happened)
- FailurePrescription: Ranked, scoped solutions (Phase 3 - What to do)
"""

import hashlib
import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone


class FailureSignature(models.Model):
    """
    Groups failures by stable signature for deduplication and tracking.

    Example signatures:
    - OPENAI_429_QUOTA: OpenAI rate limit hit
    - TIMEOUT_PROVIDER_ANTHROPIC: Anthropic API timeout
    - DATA_ERROR_MISSING_FIELD_user_id: Missing required field
    """

    class Category(models.TextChoices):
        PROVIDER_ERROR = 'provider_error', 'Provider Error'
        TIMEOUT = 'timeout', 'Timeout'
        DATA_ERROR = 'data_error', 'Data Error'
        EXECUTION_ERROR = 'execution_error', 'Execution Error'
        RESOURCE_ERROR = 'resource_error', 'Resource Error'
        UNKNOWN = 'unknown', 'Unknown'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        KNOWN_OUTAGE = 'known_outage', 'Known Outage'
        DIAGNOSED = 'diagnosed', 'Diagnosed'
        RESOLVED = 'resolved', 'Resolved'
        IGNORED = 'ignored', 'Ignored'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Unique identifier for this failure type
    signature = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Stable signature like OPENAI_429_QUOTA"
    )
    signature_hash = models.CharField(
        max_length=32,
        unique=True,
        help_text="MD5 hash for fast lookup"
    )

    # Classification
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.UNKNOWN
    )
    provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="Provider name if provider-related (openai, anthropic, etc.)"
    )
    error_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="HTTP status code or error code (429, 500, etc.)"
    )

    # Tracking
    occurrence_count = models.PositiveIntegerField(
        default=0,
        help_text="Total times this signature has been seen"
    )
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    last_diagnosed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this signature was diagnosed (for cooldown)"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # Human-readable description
    description = models.TextField(
        blank=True,
        help_text="Human-readable explanation of this failure type"
    )

    # Metadata
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'core_failure_signature'
        ordering = ['-occurrence_count', '-last_seen_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['provider']),
            models.Index(fields=['-last_seen_at']),
        ]

    def __str__(self):
        return f"{self.signature} ({self.occurrence_count}x)"

    def increment_occurrence(self):
        """Increment count and update last_seen timestamp."""
        self.occurrence_count += 1
        self.last_seen_at = timezone.now()
        self.save(update_fields=['occurrence_count', 'last_seen_at'])

    def is_on_cooldown(self, cooldown_hours: int = 6) -> bool:
        """Check if this signature was diagnosed recently (within cooldown)."""
        if not self.last_diagnosed_at:
            return False
        cooldown_end = self.last_diagnosed_at + timedelta(hours=cooldown_hours)
        return timezone.now() < cooldown_end

    def mark_diagnosed(self):
        """Mark this signature as diagnosed and update timestamp."""
        self.status = self.Status.DIAGNOSED
        self.last_diagnosed_at = timezone.now()
        self.save(update_fields=['status', 'last_diagnosed_at'])

    @classmethod
    def generate_hash(cls, signature: str) -> str:
        """Generate MD5 hash for a signature."""
        return hashlib.md5(signature.encode()).hexdigest()


class FailureDetection(models.Model):
    """
    Phase 1 - Raw failure recording without analysis.

    Captures the raw error data from experiments, agent executions,
    spider runs, Celery tasks, or API calls.
    """

    class SourceType(models.TextChoices):
        EXPERIMENT = 'experiment', 'Experiment'
        AGENT_EXECUTION = 'agent_execution', 'Agent Execution'
        SPIDER = 'spider', 'Spider'
        CELERY_TASK = 'celery_task', 'Celery Task'
        API_CALL = 'api_call', 'API Call'
        PROVIDER = 'provider', 'Provider'
        HTTP_REQUEST = 'http_request', 'HTTP Request'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to signature (many detections per signature)
    signature = models.ForeignKey(
        FailureSignature,
        on_delete=models.CASCADE,
        related_name='detections'
    )

    # What failed
    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices
    )
    source_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of the failed entity (experiment, execution, etc.)"
    )
    source_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Human-readable name of what failed"
    )

    # Raw error data
    error_message = models.TextField(
        help_text="The actual error message"
    )
    error_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="HTTP status or error code"
    )
    stack_trace = models.TextField(
        blank=True,
        help_text="Full stack trace if available"
    )

    # Context at time of failure
    context_snapshot = models.JSONField(
        default=dict,
        help_text="Context data: provider, endpoint, model, params, etc."
    )

    # Processing status
    is_diagnosed = models.BooleanField(
        default=False,
        help_text="Has this detection been processed for diagnosis?"
    )

    # Timestamps
    detected_at = models.DateTimeField(auto_now_add=True)
    diagnosed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_failure_detection'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['source_type']),
            models.Index(fields=['is_diagnosed']),
            models.Index(fields=['-detected_at']),
            models.Index(fields=['signature', 'is_diagnosed']),
        ]

    def __str__(self):
        return f"{self.source_type}: {self.error_message[:50]}..."

    def mark_diagnosed(self):
        """Mark this detection as processed for diagnosis."""
        self.is_diagnosed = True
        self.diagnosed_at = timezone.now()
        self.save(update_fields=['is_diagnosed', 'diagnosed_at'])


class FailureDiagnosis(models.Model):
    """
    Phase 2 - Root cause analysis with multi-source evidence.

    Synthesizes evidence from multiple sources to determine
    the actual root cause of failures with this signature.
    """

    class BlastRadius(models.TextChoices):
        ISOLATED = 'isolated', 'Isolated (single component)'
        LIMITED = 'limited', 'Limited (few components)'
        WIDESPREAD = 'widespread', 'Widespread (many components)'
        CRITICAL = 'critical', 'Critical (system-wide)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # One diagnosis per signature (latest wins)
    signature = models.OneToOneField(
        FailureSignature,
        on_delete=models.CASCADE,
        related_name='diagnosis'
    )

    # Root cause analysis
    root_cause = models.TextField(
        help_text="Detailed explanation of why this is happening"
    )
    root_cause_confidence = models.FloatField(
        default=0.0,
        help_text="Confidence score 0-1"
    )

    # Evidence used
    evidence_sources = models.JSONField(
        default=list,
        help_text="List of evidence types used: ['exception', 'provider', 'rate_limit', 'system_event', 'llm_synthesis']"
    )
    evidence_details = models.JSONField(
        default=dict,
        help_text="Detailed evidence per source type"
    )

    # Impact assessment
    blast_radius = models.CharField(
        max_length=20,
        choices=BlastRadius.choices,
        default=BlastRadius.ISOLATED
    )
    affected_components = models.JSONField(
        default=list,
        help_text="List of affected components/agents/services"
    )

    # Stats from detection samples
    sample_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of detections used for this diagnosis"
    )
    sample_time_range = models.JSONField(
        default=dict,
        help_text="{'from': ISO timestamp, 'to': ISO timestamp}"
    )

    # Timestamps
    diagnosed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_failure_diagnosis'
        ordering = ['-diagnosed_at']

    def __str__(self):
        return f"Diagnosis: {self.signature.signature} ({self.root_cause_confidence:.0%} confidence)"

    def to_summary_dict(self) -> dict:
        """Return a summary for ThinkingAgent context."""
        return {
            'signature': self.signature.signature,
            'root_cause': self.root_cause[:500],
            'confidence': self.root_cause_confidence,
            'blast_radius': self.blast_radius,
            'evidence_sources': self.evidence_sources,
            'sample_count': self.sample_count,
            'diagnosed_at': self.diagnosed_at.isoformat(),
        }


class FailurePrescription(models.Model):
    """
    Phase 3 - Ranked, scoped solutions with implementation details.

    Provides concrete steps to fix the diagnosed issue, organized
    by scope (immediate, structural, observability).
    """

    class Scope(models.TextChoices):
        IMMEDIATE = 'immediate', 'Immediate (stop bleeding)'
        STRUCTURAL = 'structural', 'Structural (prevent recurrence)'
        OBSERVABILITY = 'observability', 'Observability (make obvious)'

    class Impact(models.TextChoices):
        HIGH = 'high', 'High Impact'
        MEDIUM = 'medium', 'Medium Impact'
        LOW = 'low', 'Low Impact'

    class Effort(models.TextChoices):
        TRIVIAL = 'trivial', 'Trivial (<30 min)'
        SMALL = 'small', 'Small (1-2 hours)'
        MEDIUM = 'medium', 'Medium (half day)'
        LARGE = 'large', 'Large (full day+)'

    class Status(models.TextChoices):
        PROPOSED = 'proposed', 'Proposed'
        APPROVED = 'approved', 'Approved'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to diagnosis (multiple prescriptions per diagnosis)
    diagnosis = models.ForeignKey(
        FailureDiagnosis,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )

    # Solution details
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Classification
    scope = models.CharField(
        max_length=20,
        choices=Scope.choices
    )
    expected_impact = models.CharField(
        max_length=10,
        choices=Impact.choices,
        default=Impact.MEDIUM
    )
    effort = models.CharField(
        max_length=10,
        choices=Effort.choices,
        default=Effort.SMALL
    )
    confidence = models.FloatField(
        default=0.0,
        help_text="Confidence that this fix will work (0-1)"
    )

    # Ranking (computed from impact, effort, confidence)
    priority_score = models.FloatField(
        default=0.0,
        help_text="Computed priority score for ranking"
    )

    # Implementation details
    technical_steps = models.JSONField(
        default=list,
        help_text="List of technical steps to implement"
    )
    files_to_modify = models.JSONField(
        default=list,
        help_text="List of file paths that need changes"
    )
    commands_to_run = models.JSONField(
        default=list,
        help_text="Shell commands to execute"
    )

    # Success criteria
    success_criteria = models.TextField(
        blank=True,
        help_text="How we'll know this fix worked"
    )
    verification_steps = models.JSONField(
        default=list,
        help_text="Steps to verify the fix"
    )

    # Link to Initiative (auto-created remediation project)
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions',
        help_text="Auto-created Initiative for tracking remediation"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROPOSED
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_failure_prescription'
        ordering = ['-priority_score', 'scope']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['scope']),
            models.Index(fields=['-priority_score']),
        ]

    def __str__(self):
        return f"[{self.scope}] {self.title}"

    def calculate_priority_score(self):
        """
        Calculate priority score based on impact, effort, and confidence.
        Higher score = higher priority.

        Formula: (impact_weight * confidence) / effort_weight
        """
        impact_weights = {'high': 3.0, 'medium': 2.0, 'low': 1.0}
        effort_weights = {'trivial': 1.0, 'small': 2.0, 'medium': 3.0, 'large': 4.0}

        impact_w = impact_weights.get(self.expected_impact, 2.0)
        effort_w = effort_weights.get(self.effort, 2.0)

        self.priority_score = (impact_w * self.confidence) / effort_w
        return self.priority_score

    def save(self, *args, **kwargs):
        # Auto-calculate priority score on save
        if self.confidence > 0:
            self.calculate_priority_score()
        super().save(*args, **kwargs)

    def mark_completed(self):
        """Mark prescription as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_verified(self):
        """Mark prescription as verified (fix confirmed working)."""
        self.status = self.Status.VERIFIED
        self.verified_at = timezone.now()
        self.save(update_fields=['status', 'verified_at', 'updated_at'])

        # Also mark signature as resolved if all prescriptions are verified
        diagnosis = self.diagnosis
        if not diagnosis.prescriptions.exclude(
            status__in=[self.Status.VERIFIED, self.Status.REJECTED]
        ).exists():
            diagnosis.signature.status = FailureSignature.Status.RESOLVED
            diagnosis.signature.save(update_fields=['status'])

    def to_summary_dict(self) -> dict:
        """Return a summary for ThinkingAgent context."""
        return {
            'title': self.title,
            'scope': self.scope,
            'impact': self.expected_impact,
            'effort': self.effort,
            'confidence': self.confidence,
            'priority_score': self.priority_score,
            'status': self.status,
            'files_to_modify': self.files_to_modify,
            'success_criteria': self.success_criteria,
        }


# ── AutopilotAction audit model (Session 1080) ──────────────────────────────


class AutopilotAction(models.Model):
    """Audit log for every action the ops autopilot takes (or considers)."""

    ACTION_TYPES = [
        ('block_agent', 'Block Agent'),
        ('unblock_agent', 'Unblock Agent'),
        ('attention_item', 'Created Attention Item'),
        ('deploy_watch', 'Deploy Watch Verdict'),
        ('dry_run', 'Dry Run (no action taken)'),
        ('retry_deliberation', 'Retry Failed Deliberation'),
        ('content_sweep', 'Content Pipeline Sweep'),
        ('auto_resolve', 'Auto-resolve Attention Item'),
        ('content_publish', 'Content Auto-Publish'),
        ('remediate', 'Auto-Remediation Applied'),
    ]

    VERIFICATION_STATES = [
        ('pending', 'Pending Verification'),
        ('passed', 'Verification Passed'),
        ('failed', 'Verification Failed'),
        ('rolled_back', 'Rolled Back'),
        ('skipped', 'Verification Skipped'),
    ]

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    agent_name = models.CharField(max_length=100, blank=True, default='')
    policy = models.CharField(max_length=100, help_text='Policy rule that triggered this action')
    dry_run = models.BooleanField(default=False)
    evidence = models.JSONField(default=dict, help_text='Signature IDs, counts, sample exec IDs, etc.')
    result = models.JSONField(default=dict, help_text='Outcome of the action')
    deploy_sha = models.CharField(max_length=40, blank=True, default='')

    # Verification + rollback fields (Session 1086 — safety layer)
    verification_state = models.CharField(
        max_length=20, choices=VERIFICATION_STATES,
        default='skipped', db_index=True,
        help_text='Pre/post verification outcome',
    )
    verification_result = models.JSONField(
        default=dict, blank=True,
        help_text='Pre-check results, post-verification SLO deltas, rollback details',
    )
    rolled_back = models.BooleanField(default=False)
    rolled_back_at = models.DateTimeField(null=True, blank=True)
    rollback_reason = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['agent_name', '-created_at']),
        ]

    def __str__(self):
        mode = ' [DRY RUN]' if self.dry_run else ''
        return f"{self.action_type}: {self.agent_name or 'system'}{mode} ({self.created_at})"


# ── Remediation Playbook (Session 1087 — Root-Cause Autonomy) ────────────────


class RemediationPlaybook(models.Model):
    """
    Known remediation patterns that worked before.

    When the system successfully resolves a failure pattern, the fix is
    recorded here as a playbook entry. On future occurrences of the same
    signature category, the engine can auto-apply the known fix.

    Safe remediation types (config-only, no code changes):
    - timeout_adjust: Increase/decrease agent timeout
    - model_fallback: Route to fallback LLM provider
    - retry_config: Adjust retry intervals or limits
    - block_and_wait: Temporary block until provider recovers
    - queue_reroute: Move tasks to a different Celery queue
    """

    REMEDIATION_TYPES = [
        ('timeout_adjust', 'Adjust Agent Timeout'),
        ('model_fallback', 'Switch to Fallback LLM'),
        ('retry_config', 'Adjust Retry Configuration'),
        ('block_and_wait', 'Block Agent Until Recovery'),
        ('queue_reroute', 'Reroute to Different Queue'),
    ]

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # What failure this playbook entry fixes
    signature_pattern = models.CharField(
        max_length=255, db_index=True,
        help_text='Signature pattern to match (exact or prefix, e.g. TIMEOUT_PROVIDER_*)',
    )
    failure_category = models.CharField(
        max_length=30, db_index=True,
        help_text='FailureSignature.Category value to match',
    )

    # What fix to apply
    remediation_type = models.CharField(max_length=30, choices=REMEDIATION_TYPES)
    config = models.JSONField(
        default=dict,
        help_text='Remediation config: {"agent": "X", "timeout_seconds": 900} etc.',
    )

    # Track effectiveness
    times_applied = models.PositiveIntegerField(default=0)
    times_succeeded = models.PositiveIntegerField(default=0)
    times_rolled_back = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(
        default=0.0,
        help_text='times_succeeded / times_applied',
    )

    # Whether this playbook entry is active
    enabled = models.BooleanField(default=True)
    min_confidence = models.FloatField(
        default=0.5,
        help_text='Min success_rate needed to keep auto-applying',
    )

    # Link back to the original diagnosis that created this entry
    source_diagnosis = models.ForeignKey(
        FailureDiagnosis, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='playbook_entries',
    )

    class Meta:
        app_label = 'core'
        ordering = ['-success_rate', '-times_applied']
        indexes = [
            models.Index(fields=['failure_category', 'enabled']),
            models.Index(fields=['signature_pattern']),
        ]

    def __str__(self):
        return f"{self.remediation_type}: {self.signature_pattern} ({self.success_rate:.0%})"

    def record_outcome(self, succeeded: bool):
        """Record whether a playbook application succeeded."""
        self.times_applied += 1
        if succeeded:
            self.times_succeeded += 1
        else:
            self.times_rolled_back += 1
        self.success_rate = self.times_succeeded / max(self.times_applied, 1)
        # Auto-disable if success rate drops below threshold
        if self.times_applied >= 3 and self.success_rate < self.min_confidence:
            self.enabled = False
        self.save(update_fields=[
            'times_applied', 'times_succeeded', 'times_rolled_back',
            'success_rate', 'enabled', 'updated_at',
        ])
