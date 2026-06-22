"""
Document Registry Models - Session 622

Provides a single source of truth for initiative document lifecycles.
Each initiative tracks its 5-stage document pipeline with approval status.

Stage Lifecycle:
  1. Research Brief      - Why does this matter?
  2. Prototype Plan      - How would we build this?
  3. Evaluation Protocol - Should we proceed? (PASS/LEARN/FAIL)
  4. Technical Design    - Exactly what to build
  5. Pilot Execution     - What happened and what did we learn?

Usage:
    from core.models_document_registry import Initiative, InitiativeStage

    # Create new initiative
    initiative = Initiative.objects.create(
        name="AI Humanizer",
        description="AI content humanization for podcast production"
    )

    # Link a document to a stage
    InitiativeStage.objects.create(
        initiative=initiative,
        stage=3,
        document=self_blog_instance,
        status='APPROVED'
    )
"""

import uuid
from django.db import models, transaction
from django.utils import timezone


class Initiative(models.Model):
    """
    Represents a product initiative with a 5-stage document lifecycle.

    Each initiative tracks:
    - Overall status (active, completed, archived)
    - Current stage in the pipeline
    - All associated stage documents
    """

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        ARCHIVED = 'ARCHIVED', 'Archived'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        TRIAGE = 'TRIAGE', 'Queued for Triage'  # Session 994: Auto-created, not yet reviewed

    # Session 901: Purpose categories for strategic grouping
    class Purpose(models.TextChoices):
        REVENUE = 'revenue', 'Revenue & Growth'
        STABILITY = 'stability', 'Platform Health'
        LEARNING = 'learning', 'Research & Learning'
        EXPANSION = 'expansion', 'New Capabilities'
        MAINTENANCE = 'maintenance', 'Maintenance'

    # Session 901: Program groupings for portfolio view
    class Program(models.TextChoices):
        GROWTH_INTELLIGENCE = 'growth_intelligence', 'Growth Intelligence'
        PLATFORM_HEALTH = 'platform_health', 'Platform Health'
        MONETIZATION = 'monetization', 'Monetization'
        CONTENT_PIPELINE = 'content_pipeline', 'Content Pipeline'
        AI_CAPABILITIES = 'ai_capabilities', 'AI Capabilities'
        USER_EXPERIENCE = 'user_experience', 'User Experience'
        INFRASTRUCTURE = 'infrastructure', 'Infrastructure'
        RESEARCH = 'research', 'Research'
        EXPERIMENTS = 'experiments', 'Experiments'
        UNCATEGORIZED = 'uncategorized', 'Uncategorized'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # Session 901: Strategic categorization
    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices,
        default=Purpose.LEARNING,
        help_text='Primary purpose of this initiative'
    )

    program = models.CharField(
        max_length=30,
        choices=Program.choices,
        default=Program.UNCATEGORIZED,
        help_text='Portfolio program this initiative belongs to'
    )

    # Session 901: Priority scoring inputs (0-1 scale)
    impact_score = models.FloatField(
        default=0.5,
        help_text='Expected impact of this initiative (0-1)'
    )
    urgency = models.FloatField(
        default=0.5,
        help_text='Time-sensitivity of this initiative (0-1)'
    )
    confidence = models.FloatField(
        default=0.5,
        help_text='Confidence in success (0-1)'
    )
    revenue_potential = models.FloatField(
        default=0.0,
        help_text='Potential revenue impact (0-1)'
    )

    # Track current stage (1-5, or 0 if not started)
    current_stage = models.IntegerField(default=1)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, default='system')

    # Session 945: Track last meaningful activity (conversations, action items, etc.)
    # More accurate than updated_at for staleness detection
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Session 945: Last meaningful activity (conversation, action item, etc.)'
    )

    # Optional: Link to parent research topic or decision
    parent_topic = models.CharField(max_length=200, blank=True)
    source_decision_id = models.UUIDField(null=True, blank=True)

    # Session 908: Link to target workspace for file operations
    target_workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiatives',
        help_text='Target workspace for this initiative\'s outputs'
    )

    # Session 996: Initiative ownership — who is accountable for this initiative?
    owner = models.ForeignKey(
        'core.UnifiedUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_initiatives',
        help_text='Session 996: Human owner responsible for this initiative'
    )
    owner_agent = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Session 996: Agent owner responsible (e.g., "ResearchAgent")'
    )

    # Session 913: Link to Signal Intelligence (Origin & Trigger)
    signal_cluster = models.ForeignKey(
        'core.SignalCluster',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiatives',
        help_text='Session 913: Signal cluster that triggered this initiative'
    )

    auto_topic = models.ForeignKey(
        'core.AutoTopic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiatives',
        help_text='Session 913: Auto-generated topic that created this initiative'
    )

    # =========================================================================
    # Session 914: Founder Intent Fields
    # Session 914.2: Execution Track (Fast Track vs Institutional)
    # =========================================================================
    # These fields capture the founder's explicit intent for each initiative.
    # Auto-progression pauses if founder_intent_set=False, requiring human input.
    #
    # Execution Tracks:
    # - FAST_TRACK: Stage 1-2 only, minimal gates, for quick experiments
    # - INSTITUTIONAL: Full 5 stages, compliance gates, for public/legal/data
    # =========================================================================

    class ExecutionTrack(models.TextChoices):
        FAST_TRACK = 'fast_track', 'Fast Track (Stage 1-2, quick experiments)'
        INSTITUTIONAL = 'institutional', 'Institutional (Full 5-stage, compliance required)'

    class ExecutionSpeed(models.TextChoices):
        FAST = 'fast', 'Fast (MVP, stop at Stage 2)'
        BALANCED = 'balanced', 'Balanced (normal 5-stage flow)'
        THOROUGH = 'thorough', 'Thorough (extended validation)'

    class RiskTolerance(models.TextChoices):
        LOW = 'low', 'Low (require all approvals)'
        MEDIUM = 'medium', 'Medium (standard gates)'
        HIGH = 'high', 'High (move fast, minimal gates)'

    # Session 914.2: Content flags that trigger Institutional track
    class ContentFlags(models.TextChoices):
        EXTERNAL_DATA = 'external_data', 'Uses External Data/APIs'
        USER_DATA = 'user_data', 'Handles User Data'
        PUBLIC_PUBLISHING = 'public_publishing', 'Public Publishing'
        LEGAL_COMPLIANCE = 'legal_compliance', 'Legal/Compliance'
        FINANCIAL = 'financial', 'Financial Transactions'
        IRREVERSIBLE = 'irreversible', 'Irreversible Actions'

    # Whether founder has explicitly set intent for this initiative
    founder_intent_set = models.BooleanField(
        default=False,
        help_text='Session 914: Has the founder explicitly set intent for this initiative?'
    )

    # Execution speed preference
    execution_speed = models.CharField(
        max_length=20,
        choices=ExecutionSpeed.choices,
        default=ExecutionSpeed.BALANCED,
        help_text='Session 914: How fast should this initiative move?'
    )

    # Risk tolerance level
    risk_tolerance = models.CharField(
        max_length=20,
        choices=RiskTolerance.choices,
        default=RiskTolerance.MEDIUM,
        help_text='Session 914: How much risk is acceptable?'
    )

    # Budget constraints
    budget_engineering_hours = models.IntegerField(
        null=True,
        blank=True,
        help_text='Session 914: Maximum engineering hours to spend'
    )

    budget_llm_spend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Session 914: Maximum LLM API spend in dollars'
    )

    # Stop rule - what outcome kills this initiative
    stop_rule = models.TextField(
        blank=True,
        default='',
        help_text='Session 914: What outcome or condition should kill this initiative?'
    )

    # Whether this initiative requires explicit Boardroom approval
    # (external data, compliance, published deliverables)
    requires_boardroom_approval = models.BooleanField(
        default=False,
        help_text='Session 914: Does this initiative require explicit Boardroom approval?'
    )

    # When founder intent was set
    founder_intent_set_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Session 914: When was founder intent explicitly set?'
    )

    # Who set the founder intent
    founder_intent_set_by = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Session 914: Who set the founder intent?'
    )

    # =========================================================================
    # Session 914.6: Boardroom Approval Fields
    # =========================================================================

    # Whether this initiative has been explicitly approved by the Boardroom
    boardroom_approved = models.BooleanField(
        default=False,
        help_text='Session 914.6: Has this initiative been approved by the Boardroom?'
    )

    # When boardroom approval was granted
    boardroom_approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Session 914.6: When was boardroom approval granted?'
    )

    # Who approved in the boardroom
    boardroom_approved_by = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Session 914.6: Who approved this initiative in the Boardroom?'
    )

    # Optional notes from the boardroom approval
    boardroom_approval_notes = models.TextField(
        blank=True,
        default='',
        help_text='Session 914.6: Notes or conditions from boardroom approval'
    )

    # =========================================================================
    # Session 914.2: Execution Track Fields
    # =========================================================================

    # Execution track determines the pipeline path
    execution_track = models.CharField(
        max_length=20,
        choices=ExecutionTrack.choices,
        default=ExecutionTrack.FAST_TRACK,
        help_text='Session 914.2: Fast Track (Stage 1-2) or Institutional (Full 5-stage)'
    )

    # Content flags that triggered Institutional track (comma-separated)
    content_flags = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Session 914.2: Content flags detected (e.g., external_data,user_data)'
    )

    # Whether track was auto-detected or manually set
    track_auto_detected = models.BooleanField(
        default=False,
        help_text='Session 914.2: Was the execution track auto-detected from content?'
    )

    # Compliance review status (for Institutional track)
    compliance_reviewed = models.BooleanField(
        default=False,
        help_text='Session 914.2: Has compliance review been completed?'
    )

    compliance_reviewed_by = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Session 914.2: Who completed compliance review?'
    )

    compliance_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Session 914.2: When was compliance review completed?'
    )

    # Stage-specific approval gates (for Institutional track)
    stage_2_approved = models.BooleanField(
        default=False,
        help_text='Session 914.2: Has Stage 2 (Prototype Plan) been explicitly approved?'
    )

    stage_3_approved = models.BooleanField(
        default=False,
        help_text='Session 914.2: Has Stage 3 (Evaluation Protocol) been explicitly approved?'
    )

    stage_4_approved = models.BooleanField(
        default=False,
        help_text='Session 914.2: Has Stage 4 (Technical Design) been explicitly approved?'
    )

    # Session 914.3: Semantic Quality Gates
    class DriftThreshold(models.TextChoices):
        STRICT = 'strict', 'Strict (75%+ similarity required)'
        BALANCED = 'balanced', 'Balanced (65%+ similarity required)'
        RELAXED = 'relaxed', 'Relaxed (55%+ similarity required)'
        DISABLED = 'disabled', 'Disabled (no drift check)'

    drift_threshold = models.CharField(
        max_length=20,
        choices=DriftThreshold.choices,
        default=DriftThreshold.BALANCED,
        help_text='Session 914.3: How strictly to enforce semantic alignment'
    )

    drift_check_enabled = models.BooleanField(
        default=True,
        help_text='Session 914.3: Whether to perform semantic drift checks'
    )

    last_drift_score = models.FloatField(
        null=True, blank=True,
        help_text='Session 914.3: Last recorded drift score (0=aligned, 1=drifted)'
    )

    last_drift_check_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Session 914.3: When drift was last checked'
    )

    # Session 914.5: Daily Priorities
    is_daily_focus = models.BooleanField(
        default=False,
        help_text='Session 914.5: Is this initiative in today\'s daily focus?'
    )

    daily_focus_date = models.DateField(
        null=True, blank=True,
        help_text='Session 914.5: Date when marked as daily focus'
    )

    manual_priority_rank = models.IntegerField(
        null=True, blank=True,
        help_text='Session 914.5: Manual priority rank (1-5, lower = higher priority)'
    )

    manual_priority_reason = models.TextField(
        blank=True, default='',
        help_text='Session 914.5: Reason for manual priority override'
    )

    # Session 1016: Quality gate fields
    next_action = models.TextField(
        blank=True, default='',
        help_text='Session 1016: Concrete next action for this initiative'
    )
    blocking_reason = models.TextField(
        blank=True, default='',
        help_text='Session 1016: Why this initiative is blocked/stalled'
    )

    # Session 1070: Decision gate classification fields
    target_audience = models.CharField(
        max_length=50, blank=True, default='',
        help_text='Session 1070: Who is this for? (platform/end_users/founder/agents/public)'
    )
    data_scope = models.CharField(
        max_length=50, blank=True, default='',
        help_text='Session 1070: What data is allowed? (public_only/internal_ops/api_data/user_data/all)'
    )

    # Session 1043: Human-friendly sequential IDs (INIT-000001)
    seq_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text='Session 1043: Sequential human-friendly ID number'
    )
    human_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        help_text='Session 1043: Human-friendly ID (e.g., INIT-000001)'
    )

    # Session 1196 — Plan C side-quest (Initiatives-First Backbone, P0).
    # Annotation layer for Initiatives that violate the no-orphan
    # contract by missing ``target_workspace_id``. Mirrors the Deliverable
    # diagnostic block (Session 1195 PR #2402) so the same sweep + clear
    # mental model applies. Phase 1 is label + TTL only — canonical
    # ``status`` stays the lifecycle owner. The daily sweep flips
    # ``status='ARCHIVED'`` when ``diagnostic_expires_at`` passes (sweep
    # records reason inside ``diagnostic_payload``; it does NOT set
    # ``diagnostic_status='archived'``, avoiding semantic collision with
    # the canonical ARCHIVED lifecycle status). NULL diagnostic_status
    # = ok. The update path clears all five fields back to NULL once
    # ``target_workspace_id`` is set.
    diagnostic_status = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        db_index=True,
        help_text="NULL = ok; 'diagnostic' = flagged for missing target_workspace_id",
    )
    diagnostic_code = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="e.g. 'missing_target_workspace_id'",
    )
    diagnostic_payload = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured details: created_by, callsite_hint, status_at_mark, trace, archive reason",
    )
    diagnostic_marked_at = models.DateTimeField(null=True, blank=True)
    diagnostic_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Initiative'
        verbose_name_plural = 'Initiatives'
        indexes = [
            # Session 1196 — Plan C side-quest sweep query.
            # 3-column composite per Rigby's PR #1 refinement: the sweep
            # filters on (diagnostic_status, diagnostic_code,
            # diagnostic_expires_at) so all future diagnostic codes don't
            # share an index hot path with missing_target_workspace_id.
            models.Index(
                fields=['diagnostic_status', 'diagnostic_code', 'diagnostic_expires_at'],
                name='init_diag_sweep_idx',
            ),
        ]

    def __str__(self):
        prefix = self.human_id or 'INIT-?'
        return f"{prefix} — {self.name} (Stage {self.current_stage}/5)"

    def save(self, *args, **kwargs):
        if self.seq_id is None:
            self._assign_seq_id()
        super().save(*args, **kwargs)

    def _assign_seq_id(self):
        """Concurrency-safe sequential ID assignment using SELECT FOR UPDATE."""
        from django.db.models import Max
        with transaction.atomic():
            # Lock the table's max seq_id row to prevent duplicates
            max_seq = (
                Initiative.objects
                .select_for_update()
                .aggregate(max_seq=Max('seq_id'))
            )['max_seq'] or 0
            self.seq_id = max_seq + 1
            self.human_id = f"INIT-{self.seq_id:06d}"

    @property
    def priority_score(self):
        """
        Session 901: Computed priority score for sorting.

        Formula:
        priority = impact_score * 0.4 + urgency * 0.2 + confidence * 0.2 + revenue_potential * 0.2

        Returns value 0-1, higher = more important.
        """
        return (
            (self.impact_score or 0.5) * 0.4 +
            (self.urgency or 0.5) * 0.2 +
            (self.confidence or 0.5) * 0.2 +
            (self.revenue_potential or 0.0) * 0.2
        )

    @property
    def priority_level(self):
        """
        Session 901: Human-readable priority level.

        Returns: 'critical', 'high', 'medium', or 'low'
        """
        score = self.priority_score
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'

    @property
    def purpose_display(self):
        """Session 901: Human-readable purpose label."""
        return self.get_purpose_display()

    @property
    def program_display(self):
        """Session 901: Human-readable program label."""
        return self.get_program_display()

    @property
    def stage_summary(self):
        """Returns a dict of stage statuses."""
        stages = {}
        for stage_doc in self.stages.all():
            stages[stage_doc.stage] = {
                'status': stage_doc.status,
                'document_id': str(stage_doc.document_id) if stage_doc.document_id else None,
                'approved_at': stage_doc.approved_at.isoformat() if stage_doc.approved_at else None,
            }
        return stages

    @property
    def completion_percentage(self):
        """
        Session 857: Calculate completion based on stages with actual work.

        Progress is weighted by status:
        - APPROVED: 100% for that stage (1.0)
        - IN_REVIEW: 80% for that stage (0.8)
        - DRAFT: 60% for that stage (0.6)
        - PENDING/REJECTED/SUPERSEDED: 0% (0.0)

        This fixes the issue where initiatives showed 0% even when
        documents existed but weren't approved yet.
        """
        status_weights = {
            'APPROVED': 1.0,
            'IN_REVIEW': 0.8,
            'DRAFT': 0.6,
            'PENDING': 0.0,
            'REJECTED': 0.0,
            'SUPERSEDED': 0.0,
        }

        total_weight = 0.0
        for stage in self.stages.all():
            total_weight += status_weights.get(stage.status, 0.0)

        # 5 stages, max weight = 5.0 (all approved)
        return int((total_weight / 5.0) * 100)

    @property
    def approved_percentage(self):
        """Session 857: Percentage of stages that are fully APPROVED."""
        approved = self.stages.filter(status='APPROVED').count()
        return int((approved / 5) * 100)

    @property
    def stages_with_work(self):
        """Session 857: Count of stages with documents (any status except PENDING)."""
        return self.stages.exclude(status='PENDING').count()

    def get_stage_document(self, stage_number):
        """Get the document for a specific stage."""
        try:
            return self.stages.get(stage=stage_number)
        except InitiativeStage.DoesNotExist:
            return None

    def advance_stage(self):
        """
        Session 862: Advance to the next stage if current stage is approved.

        Creates the next stage if it doesn't exist. Returns the new stage number
        or None if cannot advance.
        """
        current = self.get_stage_document(self.current_stage)
        if current and current.status == 'APPROVED' and self.current_stage < 5:
            self.current_stage += 1
            self.save()

            # Create the next stage if it doesn't exist
            InitiativeStage.objects.get_or_create(
                initiative=self,
                stage=self.current_stage,
                defaults={'status': 'PENDING'}
            )
            return self.current_stage

        return None

    def get_max_approved_stage(self) -> int:
        """
        Session 943: Get the highest stage number that has APPROVED status.

        Returns 0 if no stages are approved.
        """
        approved = self.stages.filter(status='APPROVED').values_list('stage', flat=True)
        return max(approved) if approved else 0

    def validate_stage_invariant(self) -> tuple:
        """
        Session 943: Validate that current_stage respects approval chain.

        HARD INVARIANT: current_stage must be <= max_approved_stage + 1

        This ensures initiatives cannot skip ahead to Stage 5 without
        actually having prior stages approved.

        Returns:
            (is_valid, error_message)
        """
        max_approved = self.get_max_approved_stage()
        max_allowed = max_approved + 1

        if self.current_stage > max_allowed:
            return (
                False,
                f"Stage invariant violated: current_stage={self.current_stage} "
                f"but max_approved={max_approved}. Maximum allowed is {max_allowed}."
            )

        return (True, None)

    def save(self, *args, **kwargs):
        """
        Session 943: Override save to enforce stage progression invariant.
        Session 1016: Also enforce ACTIVE quality gate.

        Use skip_invariant_check=True in kwargs to bypass (for migrations/fixes).
        """
        import logging
        logger = logging.getLogger(__name__)

        skip_check = kwargs.pop('skip_invariant_check', False)

        if not skip_check:
            # Session 1016: ACTIVE quality gate — demote to TRIAGE if requirements not met
            if self.status == 'ACTIVE':
                try:
                    # Check if transitioning TO active (new record or status change)
                    is_new = not self.pk
                    old_status = None
                    if self.pk:
                        try:
                            old_status = Initiative.objects.filter(pk=self.pk).values_list('status', flat=True).first()
                        except Exception as _e:
                            logger.warning(
                                "models_document_registry.save: swallowed (%s: %s) — degraded",
                                type(_e).__name__, _e,
                            )

                    if is_new or (old_status and old_status != 'ACTIVE'):
                        from core.services.initiative_circuit_breaker import can_promote_to_active
                        if not can_promote_to_active(self):
                            logger.warning(
                                f"[QUALITY_GATE] Demoting '{self.name[:50]}' to TRIAGE: "
                                f"missing owner_agent or evidence"
                            )
                            self.status = 'TRIAGE'
                except Exception as e:
                    logger.warning(f"[QUALITY_GATE] Check failed, allowing save: {e}")

            # Only check stage invariant for existing records
            if self.pk:
                try:
                    old_instance = Initiative.objects.get(pk=self.pk)
                    if old_instance.current_stage != self.current_stage:
                        is_valid, error_msg = self.validate_stage_invariant()
                        if not is_valid:
                            logger.error(f"[INVARIANT] {error_msg} for Initiative: {self.name[:50]}")
                            max_approved = self.get_max_approved_stage()
                            self.current_stage = min(self.current_stage, max_approved + 1)
                            logger.warning(
                                f"[INVARIANT] Auto-corrected current_stage to {self.current_stage}"
                            )
                except Initiative.DoesNotExist:
                    pass

        super().save(*args, **kwargs)

    def update_activity(self, reason: 'str | None' = None):
        """
        Session 945: Update last_activity_at timestamp.

        Call this when meaningful activity happens:
        - Conversation completed
        - Action item created/updated
        - Stage document attached

        Session 1191: `reason` is an optional caller-supplied hint logged
        at DEBUG. Backward-compatible (default None). The
        `initiative_activity_tick` beat task uses this to distinguish
        bootstrap writes ("auto_populate_create") from cheap-signal sweeps
        ("activity_tick_signal_max") in audit logs.
        """
        from django.utils import timezone
        self.last_activity_at = timezone.now()
        self.save(update_fields=['last_activity_at'], skip_invariant_check=True)
        if reason:
            import logging as _logging
            _logging.getLogger(__name__).debug(
                "Initiative.update_activity id=%s reason=%s", self.id, reason
            )

    def is_complete(self):
        """Check if all 5 stages are approved."""
        approved_count = self.stages.filter(status='APPROVED').count()
        return approved_count >= 5

    def create_final_deliverable(self):
        """
        Session 862: Create a published Deliverable from completed initiative.

        Called when all 5 stages are approved to generate the final output.
        """
        from core.models_deliverables import Deliverable
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get all approved stage documents
        stages = self.stages.filter(
            status='APPROVED'
        ).select_related('document').order_by('stage')

        # Compile content from all stages
        content_parts = []
        for stage in stages:
            content_parts.append(f"## Stage {stage.stage}: {stage.stage_name}\n\n")
            if stage.document:
                content_parts.append(stage.document.full_text or stage.document.intro or '')
            else:
                content_parts.append(f"*No document for {stage.stage_name}*")
            content_parts.append("\n\n---\n\n")

        full_content = ''.join(content_parts)

        # Get user (default to first superuser if none specified)
        user = User.objects.filter(is_superuser=True).first()

        # Get source dream if exists
        source_dream = self.source_dreams.first()

        # Resolve workspace from initiative
        from core.services.deliverable_workspace_resolver import resolve_workspace
        ws, ws_saved = resolve_workspace(initiative=self)

        # Create the deliverable
        from core.services.deliverable_factory import create_deliverable
        deliverable = create_deliverable(
            title=f"Completed: {self.name}",
            content=full_content,
            agent_name='InitiativePipeline',
            category='initiative_completion',
            deliverable_type='document',
            user=user,
            initiative_id=str(self.id),
            content_format='markdown',
            is_saved=ws_saved,
            metadata={
                'stages_completed': 5,
                'initiative_id': str(self.id),
                'completed_at': timezone.now().isoformat(),
                'stage_names': [stage.stage_name for stage in stages],
            },
            status='published',
            initiative=self,
            dream=source_dream,
            workspace=ws,
        )

        # Update initiative status
        self.status = self.Status.COMPLETED
        self.save(update_fields=['status'])

        return deliverable

    # =========================================================================
    # Session 914: Founder Intent Methods
    # =========================================================================

    def set_founder_intent(
        self,
        execution_speed: str = None,
        risk_tolerance: str = None,
        budget_engineering_hours: int = None,
        budget_llm_spend: float = None,
        stop_rule: str = None,
        requires_boardroom_approval: bool = None,
        set_by: str = 'founder'
    ):
        """
        Session 914: Set explicit founder intent for this initiative.

        This marks the initiative as having explicit human guidance, allowing
        auto-progression to continue. Without this, auto-progression will pause
        at Stage 1 and await human input.

        Args:
            execution_speed: 'fast', 'balanced', or 'thorough'
            risk_tolerance: 'low', 'medium', or 'high'
            budget_engineering_hours: Max engineering hours (optional)
            budget_llm_spend: Max LLM API spend in dollars (optional)
            stop_rule: What outcome kills this initiative (optional)
            requires_boardroom_approval: Whether explicit approval needed
            set_by: Who is setting the intent (default: 'founder')

        Returns:
            self for chaining
        """
        if execution_speed:
            self.execution_speed = execution_speed
        if risk_tolerance:
            self.risk_tolerance = risk_tolerance
        if budget_engineering_hours is not None:
            self.budget_engineering_hours = budget_engineering_hours
        if budget_llm_spend is not None:
            self.budget_llm_spend = budget_llm_spend
        if stop_rule:
            self.stop_rule = stop_rule
        if requires_boardroom_approval is not None:
            self.requires_boardroom_approval = requires_boardroom_approval

        self.founder_intent_set = True
        self.founder_intent_set_at = timezone.now()
        self.founder_intent_set_by = set_by

        self.save()
        return self

    def approve_in_boardroom(
        self,
        approved_by: str = 'boardroom',
        notes: str = ''
    ):
        """
        Session 914.6: Approve this initiative in the Boardroom.

        This grants boardroom approval for institutional-track initiatives
        that require explicit governance sign-off.

        Args:
            approved_by: Who is approving (default: 'boardroom')
            notes: Optional notes or conditions for the approval

        Returns:
            self for chaining
        """
        self.boardroom_approved = True
        self.boardroom_approved_at = timezone.now()
        self.boardroom_approved_by = approved_by
        if notes:
            self.boardroom_approval_notes = notes

        self.save(update_fields=[
            'boardroom_approved', 'boardroom_approved_at',
            'boardroom_approved_by', 'boardroom_approval_notes'
        ])
        return self

    def revoke_boardroom_approval(self, reason: str = ''):
        """
        Session 914.6: Revoke boardroom approval.

        Used when an initiative needs to be re-reviewed or was approved in error.

        Args:
            reason: Reason for revoking approval

        Returns:
            self for chaining
        """
        self.boardroom_approved = False
        self.boardroom_approved_at = None
        self.boardroom_approved_by = ''
        self.boardroom_approval_notes = f"REVOKED: {reason}" if reason else ''

        self.save(update_fields=[
            'boardroom_approved', 'boardroom_approved_at',
            'boardroom_approved_by', 'boardroom_approval_notes'
        ])
        return self

    @property
    def can_auto_progress(self):
        """
        Session 914: Check if this initiative can auto-progress.

        Returns False if:
        - founder_intent_set is False AND current_stage > 1
        - requires_boardroom_approval is True AND not explicitly approved
        - execution_speed is 'fast' AND current_stage >= 2

        This ensures the system pauses for human input when needed.
        """
        # Fast track stops at Stage 2
        if self.execution_speed == 'fast' and self.current_stage >= 2:
            return False

        # Session 914.6: If boardroom approval required, check if we have it
        # This is now separate from founder_intent_set
        if self.requires_boardroom_approval and not self.boardroom_approved:
            return False

        # Session 1070: Block at Stage 2+ if decision gate fields are empty
        if self.current_stage >= 2 and (not self.target_audience or not self.data_scope):
            return False

        # Allow Stage 1 to progress without intent (to generate initial research)
        # But pause at Stage 2+ if no intent is set
        if self.current_stage > 1 and not self.founder_intent_set:
            return False

        return True

    @property
    def progression_blocked_reason(self):
        """
        Session 914: Return the reason why auto-progression is blocked.

        Returns None if not blocked, otherwise returns a descriptive string.
        """
        if self.execution_speed == 'fast' and self.current_stage >= 2:
            return 'Fast Track mode - stopped at Stage 2 awaiting founder decision'

        # Session 914.6: Check boardroom approval separately
        if self.requires_boardroom_approval and not self.boardroom_approved:
            return 'Requires Boardroom approval - not yet approved'

        # Session 1070: Decision gate classification required at Stage 2+
        if self.current_stage >= 2 and (not self.target_audience or not self.data_scope):
            missing = []
            if not self.target_audience:
                missing.append('target_audience')
            if not self.data_scope:
                missing.append('data_scope')
            return f'Decision gate: missing classification fields ({", ".join(missing)})'

        if self.current_stage > 1 and not self.founder_intent_set:
            return 'Awaiting founder intent - set execution_speed, risk_tolerance, and stop_rule'

        return None

    @property
    def founder_intent_summary(self):
        """
        Session 914: Return a summary of founder intent settings.
        """
        return {
            'set': self.founder_intent_set,
            'set_at': self.founder_intent_set_at.isoformat() if self.founder_intent_set_at else None,
            'set_by': self.founder_intent_set_by,
            'execution_speed': self.execution_speed,
            'execution_speed_display': self.get_execution_speed_display() if self.execution_speed else None,
            'risk_tolerance': self.risk_tolerance,
            'risk_tolerance_display': self.get_risk_tolerance_display() if self.risk_tolerance else None,
            'budget_engineering_hours': self.budget_engineering_hours,
            'budget_llm_spend': float(self.budget_llm_spend) if self.budget_llm_spend else None,
            'stop_rule': self.stop_rule,
            'requires_boardroom_approval': self.requires_boardroom_approval,
            'boardroom_approved': self.boardroom_approved,
            'can_auto_progress': self.can_auto_progress,
            'blocked_reason': self.progression_blocked_reason,
        }

    @property
    def boardroom_approval_summary(self):
        """
        Session 914.6: Return a summary of boardroom approval status.
        """
        return {
            'required': self.requires_boardroom_approval,
            'approved': self.boardroom_approved,
            'approved_at': self.boardroom_approved_at.isoformat() if self.boardroom_approved_at else None,
            'approved_by': self.boardroom_approved_by,
            'notes': self.boardroom_approval_notes,
            'status': 'approved' if self.boardroom_approved else (
                'pending' if self.requires_boardroom_approval else 'not_required'
            )
        }

    # =========================================================================
    # Session 914.2: Execution Track Methods
    # =========================================================================

    # Keywords that trigger Institutional track
    INSTITUTIONAL_KEYWORDS = {
        'external_data': [
            'api', 'external', 'third-party', 'integration', 'webhook',
            'scrape', 'crawl', 'fetch', 'ingest', 'import'
        ],
        'user_data': [
            'user data', 'personal', 'pii', 'privacy', 'gdpr', 'ccpa',
            'customer', 'account', 'profile', 'credentials', 'password'
        ],
        'public_publishing': [
            'publish', 'public', 'blog', 'article', 'content', 'post',
            'social media', 'twitter', 'linkedin', 'youtube', 'podcast'
        ],
        'legal_compliance': [
            'legal', 'compliance', 'regulation', 'contract', 'terms',
            'license', 'copyright', 'trademark', 'patent', 'audit'
        ],
        'financial': [
            'payment', 'transaction', 'billing', 'subscription', 'revenue',
            'money', 'price', 'cost', 'fee', 'charge', 'refund'
        ],
        'irreversible': [
            'delete', 'remove', 'destroy', 'migrate', 'deploy', 'production',
            'rollout', 'launch', 'release', 'ship'
        ],
    }

    def detect_content_flags(self) -> list:
        """
        Session 914.2: Auto-detect content flags from initiative name/description.

        Scans the initiative name and description for keywords that indicate
        the initiative should use the Institutional track.

        Returns:
            List of detected content flag keys (e.g., ['external_data', 'public_publishing'])
        """
        detected_flags = []
        content = f"{self.name} {self.description}".lower()

        for flag_key, keywords in self.INSTITUTIONAL_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in content:
                    detected_flags.append(flag_key)
                    break  # Only add each flag once

        return detected_flags

    def auto_detect_execution_track(self, save: bool = True) -> str:
        """
        Session 914.2: Auto-detect and set execution track based on content.

        If any Institutional keywords are detected, sets track to INSTITUTIONAL.
        Otherwise, defaults to FAST_TRACK.

        Args:
            save: Whether to save the initiative after detection

        Returns:
            The detected execution track ('fast_track' or 'institutional')
        """
        flags = self.detect_content_flags()

        if flags:
            self.execution_track = 'institutional'
            self.content_flags = ','.join(flags)
            self.requires_boardroom_approval = True
        else:
            self.execution_track = 'fast_track'
            self.content_flags = ''

        self.track_auto_detected = True

        if save:
            self.save(update_fields=[
                'execution_track', 'content_flags',
                'track_auto_detected', 'requires_boardroom_approval'
            ])

        return self.execution_track

    def set_execution_track(
        self,
        track: str,
        content_flags: list = None,
        set_by: str = 'founder'
    ):
        """
        Session 914.2: Manually set execution track.

        Args:
            track: 'fast_track' or 'institutional'
            content_flags: Optional list of content flags
            set_by: Who is setting the track

        Returns:
            self for chaining
        """
        self.execution_track = track
        self.track_auto_detected = False

        if content_flags:
            self.content_flags = ','.join(content_flags)

        # Institutional track requires boardroom approval by default
        if track == 'institutional':
            self.requires_boardroom_approval = True

        self.save()
        return self

    @property
    def is_fast_track(self) -> bool:
        """Session 914.2: Check if initiative is on Fast Track."""
        return self.execution_track == 'fast_track'

    @property
    def is_institutional(self) -> bool:
        """Session 914.2: Check if initiative is on Institutional track."""
        return self.execution_track == 'institutional'

    @property
    def max_stage(self) -> int:
        """
        Session 914.2: Maximum stage for this initiative's track.

        Fast Track: Stage 2 (Research Brief + Prototype Plan)
        Institutional: Stage 5 (Full pipeline)
        """
        if self.is_fast_track:
            return 2
        return 5

    def requires_stage_approval(self, stage_num: int) -> bool:
        """
        Session 914.2: Check if a specific stage requires explicit approval.

        For Institutional track, stages 2, 3, and 4 require explicit approval.
        For Fast Track, only stage 2 requires approval (end of track).

        Args:
            stage_num: The stage number to check (1-5)

        Returns:
            True if the stage requires explicit approval
        """
        if self.is_fast_track:
            return stage_num == 2  # End of Fast Track

        # Institutional track - stages 2, 3, 4 require approval
        return stage_num in [2, 3, 4]

    def is_stage_approved(self, stage_num: int) -> bool:
        """
        Session 914.2: Check if a specific stage has been explicitly approved.

        Args:
            stage_num: The stage number to check (2, 3, or 4)

        Returns:
            True if the stage has been approved
        """
        if stage_num == 2:
            return self.stage_2_approved
        elif stage_num == 3:
            return self.stage_3_approved
        elif stage_num == 4:
            return self.stage_4_approved
        return True  # Stages 1 and 5 don't require explicit approval

    def approve_stage(self, stage_num: int, approved_by: str = 'founder'):
        """
        Session 914.2: Approve a specific stage for progression.

        Args:
            stage_num: The stage number to approve (2, 3, or 4)
            approved_by: Who is approving the stage

        Returns:
            self for chaining
        """
        if stage_num == 2:
            self.stage_2_approved = True
        elif stage_num == 3:
            self.stage_3_approved = True
        elif stage_num == 4:
            self.stage_4_approved = True

        self.save()
        return self

    def complete_compliance_review(self, reviewed_by: str = 'compliance'):
        """
        Session 914.2: Mark compliance review as complete.

        Required for Institutional track before Stage 4 (Technical Design).

        Args:
            reviewed_by: Who completed the compliance review

        Returns:
            self for chaining
        """
        self.compliance_reviewed = True
        self.compliance_reviewed_by = reviewed_by
        self.compliance_reviewed_at = timezone.now()
        self.save()
        return self

    @property
    def execution_track_summary(self) -> dict:
        """
        Session 914.2: Return a summary of execution track settings.
        """
        return {
            'track': self.execution_track,
            'track_display': self.get_execution_track_display() if self.execution_track else None,
            'is_fast_track': self.is_fast_track,
            'is_institutional': self.is_institutional,
            'max_stage': self.max_stage,
            'content_flags': self.content_flags.split(',') if self.content_flags else [],
            'track_auto_detected': self.track_auto_detected,
            'compliance_reviewed': self.compliance_reviewed,
            'compliance_reviewed_by': self.compliance_reviewed_by,
            'stage_2_approved': self.stage_2_approved,
            'stage_3_approved': self.stage_3_approved,
            'stage_4_approved': self.stage_4_approved,
        }


# Stage definitions (must be outside class for field definition)
STAGE_NAMES = {
    1: 'Research Brief',
    2: 'Prototype Plan',
    3: 'Evaluation Protocol',
    4: 'Technical Design',
    5: 'Pilot Execution',
}

STAGE_PURPOSES = {
    1: 'Discovery + framing - Why does this matter?',
    2: 'Translation layer - How would we build this?',
    3: 'Pre-pilot gate - Should we proceed? (PASS/LEARN/FAIL)',
    4: 'Implementation specification - Exactly what to build',
    5: 'Execution & postmortem - What happened and what did we learn?',
}

# Session 1058 Level 3: Stage type classification for action item dispatch
STAGE_TYPES = {
    1: 'research',       # External research — produces findings
    2: 'planning',       # Architecture/prototype plan — produces design doc
    3: 'evaluation',     # Go/no-go gate — produces criteria doc
    4: 'specification',  # Technical detail — produces spec doc + action items
    5: 'execution',      # Pilot execution — produces results + action items
}

# Stages where action items are expected and auto-dispatch is enabled
STAGES_WITH_AUTO_DISPATCH = {4, 5}

STAGE_CHOICES = [(i, f"Stage {i} - {STAGE_NAMES.get(i, 'Unknown')}") for i in range(1, 6)]


class InitiativeStage(models.Model):
    """
    Links an initiative to a specific stage document.

    Each stage can have:
    - A linked document (SelfBlog)
    - Approval status
    - Approver information
    - Notes
    """

    class StageStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        DRAFT = 'DRAFT', 'Draft'
        IN_REVIEW = 'IN_REVIEW', 'In Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        SUPERSEDED = 'SUPERSEDED', 'Superseded'
        BLOCKED = 'BLOCKED', 'Blocked - Awaiting Data'  # Session 905: For insufficient data

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='stages'
    )

    stage = models.IntegerField(choices=STAGE_CHOICES)

    # Link to actual document (SelfBlog)
    document = models.ForeignKey(
        'core.SelfBlog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiative_stages'
    )

    status = models.CharField(
        max_length=20,
        choices=StageStatus.choices,
        default=StageStatus.PENDING
    )

    # Approval tracking
    approved_by = models.CharField(max_length=100, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Notes and metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Session 914.3: Semantic Drift Tracking
    drift_score = models.FloatField(
        null=True, blank=True,
        help_text='Session 914.3: Semantic drift score (0=aligned, 1=drifted)'
    )

    similarity_score = models.FloatField(
        null=True, blank=True,
        help_text='Session 914.3: Semantic similarity to initiative intent (0-1)'
    )

    drift_checked_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Session 914.3: When drift was last checked'
    )

    drift_flagged = models.BooleanField(
        default=False,
        help_text='Session 914.3: Whether this stage was flagged for drift'
    )

    drift_override = models.BooleanField(
        default=False,
        help_text='Session 914.3: Human override to allow progression despite drift'
    )

    drift_override_by = models.CharField(
        max_length=100, blank=True,
        help_text='Session 914.3: Who approved the drift override'
    )

    drift_override_reason = models.TextField(
        blank=True,
        help_text='Session 914.3: Reason for allowing drift override'
    )

    class Meta:
        ordering = ['initiative', 'stage']
        unique_together = ['initiative', 'stage']
        verbose_name = 'Initiative Stage'
        verbose_name_plural = 'Initiative Stages'

    # Session 916: Hard invariant - APPROVED requires document
    _skip_document_check = False  # Escape hatch for data migrations only

    def clean(self):
        """
        Session 916: Django validation - enforces business rules.
        Called by forms, admin, and full_clean().
        """
        from django.core.exceptions import ValidationError
        super().clean()

        # INVARIANT: Cannot be APPROVED without a document
        if self.status == self.StageStatus.APPROVED and not self.document:
            raise ValidationError({
                'status': f"Cannot set status to APPROVED without a document. "
                          f"Stage {self.stage} requires a document before approval."
            })

        # INVARIANT: Cannot be APPROVED if previous stage is not APPROVED
        if self.status == self.StageStatus.APPROVED and self.stage > 1:
            try:
                prev_stage = InitiativeStage.objects.get(
                    initiative=self.initiative,
                    stage=self.stage - 1
                )
                if prev_stage.status != self.StageStatus.APPROVED:
                    raise ValidationError({
                        'status': f"Cannot approve Stage {self.stage} before Stage {self.stage - 1} is approved. "
                                  f"Current Stage {self.stage - 1} status: {prev_stage.status}"
                    })
            except InitiativeStage.DoesNotExist:
                pass  # Previous stage doesn't exist, allow (edge case)

    def save(self, *args, **kwargs):
        """
        Session 916: Hard invariant enforcement on every save.

        This catches ANY code path that tries to set status=APPROVED without a document,
        not just code that uses the approve() method.

        Use _skip_document_check=True ONLY for data migrations/fixes.

        Uses ValidationError (Django best practice) for proper admin/form integration.
        """
        from django.core.exceptions import ValidationError
        from django.db import transaction

        # Get initiative ID safely (works for both saved and unsaved instances)
        init_id = getattr(self, 'initiative_id', None) or (self.initiative.id if self.initiative else None)
        init_name = self.initiative.name if self.initiative else 'Unknown'

        # Check if we're trying to set APPROVED status
        if self.status == self.StageStatus.APPROVED and not self._skip_document_check:
            # INVARIANT 1: Must have a document
            if not self.document:
                raise ValidationError(
                    f"INVARIANT VIOLATION: Cannot save Stage {self.stage} as APPROVED without a document. "
                    f"Initiative: {init_name}. "
                    f"Use stage.approve() method or set _skip_document_check=True for data migrations."
                )

            # INVARIANT 2: Previous stage must be approved (unless Stage 1)
            # Use select_for_update() to prevent race conditions in concurrent approvals
            if self.stage > 1 and init_id:
                try:
                    with transaction.atomic():
                        prev_stage = InitiativeStage.objects.select_for_update().get(
                            initiative_id=init_id,
                            stage=self.stage - 1
                        )
                        if prev_stage.status != self.StageStatus.APPROVED:
                            raise ValidationError(
                                f"INVARIANT VIOLATION: Cannot approve Stage {self.stage} before Stage {self.stage - 1}. "
                                f"Stage {self.stage - 1} status: {prev_stage.status}. "
                                f"Initiative: {init_name}"
                            )
                except InitiativeStage.DoesNotExist:
                    pass  # Previous stage doesn't exist, allow

        # Reset the skip flag after use (one-time bypass only)
        self._skip_document_check = False

        super().save(*args, **kwargs)

    @classmethod
    def unsafe_update_status(cls, stage_id, new_status, reason='data_migration'):
        """
        Session 916: DANGER - Bypasses invariant checks for data migrations only.

        Use this ONLY for:
        - Data migrations
        - Audit fixes
        - Emergency repairs

        This method logs the bypass to the audit trail.

        Args:
            stage_id: UUID of the stage to update
            new_status: New status to set
            reason: Reason for bypassing checks (logged to audit)

        Returns:
            The updated stage instance
        """
        stage = cls.objects.get(id=stage_id)
        old_status = stage.status
        stage._skip_document_check = True
        stage.status = new_status
        stage.save()

        # Log the bypass
        StageTransitionLog.log_transition(
            stage=stage,
            from_status=old_status,
            to_status=new_status,
            triggered_by=f'unsafe_update:{reason}',
            trigger_type='manual',
            checks_passed={'invariant_bypassed': True, 'reason': reason},
            notes=f'INVARIANT BYPASS: {reason}'
        )

        return stage

    def __str__(self):
        return f"{self.initiative.name} - Stage {self.stage}: {self.stage_name}"

    @property
    def stage_name(self):
        return STAGE_NAMES.get(self.stage, 'Unknown')

    @property
    def stage_purpose(self):
        return STAGE_PURPOSES.get(self.stage, '')

    def approve(
        self,
        approved_by='system',
        notes='',
        quality_score=None,
        confidence_score=None,
        checks_passed=None,
        enforce_document=True
    ):
        """
        Session 862: Mark this stage as approved and advance initiative.
        Session 916: Added audit logging, document enforcement, and transaction safety.

        If all 5 stages are now approved, creates final Deliverable.

        This is the ONLY approved way to change status to APPROVED.
        Direct status assignment will be blocked by save() invariants.

        Args:
            approved_by: Who approved (user or 'system')
            notes: Optional approval notes
            quality_score: Quality score at approval (Session 916)
            confidence_score: Confidence in quality assessment (Session 916)
            checks_passed: Dict of validation checks passed (Session 916)
            enforce_document: If True, requires document to exist (Session 916)

        Returns:
            Deliverable or None: Final deliverable if all stages complete

        Raises:
            ValidationError: If document required but not attached, or sequence violated
        """
        from django.core.exceptions import ValidationError
        from django.db import transaction

        # Session 916: Enforce document existence
        if enforce_document and not self.document:
            raise ValidationError(
                f"Cannot approve Stage {self.stage} without a document. "
                f"Initiative: {self.initiative.name}. "
                f"Use stage.approve() only after attaching a document."
            )

        # Session 916: Use transaction.atomic() with select_for_update() for concurrency safety
        # This prevents race conditions when multiple Celery tasks try to approve stages
        with transaction.atomic():
            # Re-fetch with lock to ensure we have latest state
            locked_self = InitiativeStage.objects.select_for_update().get(id=self.id)

            old_status = locked_self.status
            locked_self.status = self.StageStatus.APPROVED
            locked_self.approved_by = approved_by
            locked_self.approved_at = timezone.now()
            if notes:
                locked_self.notes = (locked_self.notes or '') + f"\n\nApproval notes: {notes}"
            locked_self.save()

            # Update self to match locked version
            self.status = locked_self.status
            self.approved_by = locked_self.approved_by
            self.approved_at = locked_self.approved_at
            self.notes = locked_self.notes

            # Session 916: Log the transition (inside transaction)
            StageTransitionLog.log_transition(
                stage=locked_self,
                from_status=old_status,
                to_status=self.StageStatus.APPROVED,
                triggered_by=approved_by,
                quality_score=quality_score,
                confidence_score=confidence_score,
                checks_passed=checks_passed or {},
                notes=notes
            )

            # Session 994: Record activity on approval
            try:
                self.initiative.update_activity()
            except Exception:
                pass  # Don't let activity tracking block approval

            # Try to advance the initiative (inside transaction for consistency)
            self.initiative.advance_stage()

            # Check if all stages are now complete
            if self.initiative.is_complete():
                return self.initiative.create_final_deliverable()

        return None

    def reject(self, reason='', rejected_by='system'):
        """Mark this stage as rejected."""
        old_status = self.status
        self.status = self.StageStatus.REJECTED
        self.rejection_reason = reason
        self.save()

        # Session 916: Log transition
        StageTransitionLog.log_transition(
            stage=self,
            from_status=old_status,
            to_status=self.StageStatus.REJECTED,
            triggered_by=rejected_by,
            notes=f"Rejection reason: {reason}" if reason else None
        )


class StageTransitionLog(models.Model):
    """
    Session 916: Audit trail for initiative stage transitions.

    Logs every state change with full context for traceability:
    - What changed (from_status -> to_status)
    - When it changed (timestamp)
    - Who/what triggered it (agent, system, user)
    - Quality metrics at time of transition
    - What validation checks passed
    - Document state at transition

    This provides complete auditability of the initiative pipeline,
    ensuring no stage can be approved without proper verification.
    """

    class TriggerType(models.TextChoices):
        SYSTEM = 'system', 'System (Auto-progression)'
        AGENT = 'agent', 'Agent'
        USER = 'user', 'User'
        API = 'api', 'API Call'
        CELERY = 'celery', 'Celery Task'
        MANUAL = 'manual', 'Manual Override'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the stage
    stage = models.ForeignKey(
        InitiativeStage,
        on_delete=models.CASCADE,
        related_name='transition_logs'
    )

    # State change
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)

    # When
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Who/what triggered it
    trigger_type = models.CharField(
        max_length=20,
        choices=TriggerType.choices,
        default=TriggerType.SYSTEM
    )
    triggered_by = models.CharField(
        max_length=200,
        help_text='Agent name, user ID, task name, or system component'
    )

    # Quality state at transition
    quality_score = models.FloatField(
        null=True, blank=True,
        help_text='Quality score at time of transition (0-1)'
    )
    confidence_score = models.FloatField(
        null=True, blank=True,
        help_text='Confidence in the quality assessment (0-1)'
    )

    # Document state
    document_id = models.UUIDField(
        null=True, blank=True,
        help_text='Document ID at time of transition'
    )
    document_word_count = models.IntegerField(
        null=True, blank=True,
        help_text='Document word count at transition'
    )

    # Validation checks
    checks_passed = models.JSONField(
        default=dict,
        help_text='Dict of validation checks and their results'
    )

    # Additional context
    notes = models.TextField(
        blank=True,
        help_text='Additional context or notes about this transition'
    )

    # Error tracking
    had_error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Stage Transition Log'
        verbose_name_plural = 'Stage Transition Logs'
        indexes = [
            models.Index(fields=['stage', '-timestamp']),
            models.Index(fields=['triggered_by', '-timestamp']),
            models.Index(fields=['to_status', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.stage} | {self.from_status} → {self.to_status} | {self.timestamp}"

    @classmethod
    def log_transition(
        cls,
        stage: 'InitiativeStage',
        from_status: str,
        to_status: str,
        triggered_by: str,
        trigger_type=None,  # Optional[str]
        quality_score=None,  # Optional[float]
        confidence_score=None,  # Optional[float]
        checks_passed=None,  # Optional[dict]
        notes=None,  # Optional[str]
        had_error: bool = False,
        error_message=None  # Optional[str]
    ) -> 'StageTransitionLog':
        """
        Create a transition log entry.

        Args:
            stage: The InitiativeStage being transitioned
            from_status: Previous status
            to_status: New status
            triggered_by: Who/what triggered (agent name, user, system)
            trigger_type: Type of trigger (system, agent, user, api, celery)
            quality_score: Quality score at transition
            confidence_score: Confidence in quality assessment
            checks_passed: Dict of validation checks and results
            notes: Additional context
            had_error: Whether an error occurred
            error_message: Error details if any

        Returns:
            The created StageTransitionLog instance
        """
        # Auto-detect trigger type if not provided
        if trigger_type is None:
            if 'Agent' in triggered_by:
                trigger_type = cls.TriggerType.AGENT
            elif triggered_by in ('system', 'auto_pipeline', 'auto_quality_check'):
                trigger_type = cls.TriggerType.SYSTEM
            elif 'celery' in triggered_by.lower() or 'task' in triggered_by.lower():
                trigger_type = cls.TriggerType.CELERY
            elif 'api' in triggered_by.lower():
                trigger_type = cls.TriggerType.API
            else:
                trigger_type = cls.TriggerType.SYSTEM

        # Get document info if available
        document_id = None
        document_word_count = None
        if stage.document:
            document_id = stage.document.id
            document_word_count = stage.document.word_count

        return cls.objects.create(
            stage=stage,
            from_status=from_status,
            to_status=to_status,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            quality_score=quality_score,
            confidence_score=confidence_score,
            document_id=document_id,
            document_word_count=document_word_count,
            checks_passed=checks_passed or {},
            notes=notes or '',
            had_error=had_error,
            error_message=error_message or ''
        )

    @classmethod
    def get_stage_history(cls, stage: 'InitiativeStage') -> models.QuerySet:
        """Get all transitions for a stage in chronological order."""
        return cls.objects.filter(stage=stage).order_by('timestamp')

    @classmethod
    def get_initiative_history(cls, initiative: 'Initiative') -> models.QuerySet:
        """Get all transitions for an initiative across all stages."""
        return cls.objects.filter(stage__initiative=initiative).order_by('timestamp')


def create_initiative_from_deliverables(parent_topic: str) -> Initiative:
    """
    Create an Initiative and populate stages from existing deliverables.

    Args:
        parent_topic: The parent topic to search for in deliverables

    Returns:
        The created Initiative with linked stages
    """
    from core.models_unified_system import SelfBlog
    from django.db.models import Q

    # Create the initiative
    initiative, created = Initiative.objects.get_or_create(
        name=parent_topic,
        defaults={
            'description': f'Auto-created from existing deliverables for: {parent_topic}',
            'created_by': 'auto_populate'
        }
    )

    if not created:
        return initiative  # Already exists

    # Find deliverables for this topic
    deliverables = SelfBlog.objects.filter(
        Q(title__startswith='[Stage 1 -') |
        Q(title__startswith='[Stage 2 -') |
        Q(title__startswith='[Stage 3 -') |
        Q(title__startswith='[Stage 4 -') |
        Q(title__startswith='[Stage 5 -')
    ).filter(
        stats_snapshot__parent_topic__icontains=parent_topic.split(' ')[0]  # Partial match on first word
    )

    # Link each deliverable to its stage
    for doc in deliverables:
        stage_num = doc.stats_snapshot.get('stage') if doc.stats_snapshot else None
        if stage_num:
            InitiativeStage.objects.get_or_create(
                initiative=initiative,
                stage=stage_num,
                defaults={
                    'document': doc,
                    'status': InitiativeStage.StageStatus.APPROVED,
                    'approved_by': 'auto_populate',
                    'approved_at': doc.created_at,
                }
            )

    # Set current stage based on what's approved
    max_approved = initiative.stages.filter(status='APPROVED').aggregate(
        max_stage=models.Max('stage')
    )['max_stage'] or 0
    initiative.current_stage = min(max_approved + 1, 5)
    initiative.save()

    return initiative


class InitiativeActionItem(models.Model):
    """
    Session 902: Trackable action items extracted from conversation conclusions.

    Transforms text like "ResearchAgent: Define persona schema (Week 0-1)"
    into assignable, trackable items with completion status.

    Extracted from === DecisionSummary === sections in HiveMindSession conclusions.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        BLOCKED = 'blocked', 'Blocked'
        CANCELLED = 'cancelled', 'Cancelled'

    class Priority(models.TextChoices):
        CRITICAL = 'critical', 'Critical'
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to initiative
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='action_items'
    )

    # Source tracking - where did this action item come from?
    source_conversation = models.ForeignKey(
        'core.HiveMindSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='extracted_action_items',
        help_text='The conversation that generated this action item'
    )
    # Session 1058: Link to the pipeline stage whose document generated this item
    source_stage = models.ForeignKey(
        'InitiativeStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='action_items',
        help_text='The pipeline stage whose document generated this action item'
    )
    source_text = models.TextField(
        blank=True,
        help_text='Original text from conclusion that was parsed'
    )

    # Action item details
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    # Assignment
    assigned_agent = models.CharField(
        max_length=100,
        blank=True,
        help_text='Agent name responsible (e.g., "ResearchAgent")'
    )
    assigned_user = models.ForeignKey(
        'core.UnifiedUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_action_items'
    )

    # Timeline
    timeline_text = models.CharField(
        max_length=50,
        blank=True,
        help_text='Original timeline text (e.g., "Week 0-1")'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text='Calculated or manually set due date'
    )
    estimated_hours = models.FloatField(
        null=True,
        blank=True,
        help_text='Estimated effort in hours'
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    # Completion tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.CharField(max_length=100, blank=True)
    completion_notes = models.TextField(blank=True)

    # Blocking/dependencies
    blocked_reason = models.TextField(blank=True)
    depends_on = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='blocks'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, default='system')
    order = models.IntegerField(default=0, help_text='Display order within initiative')

    class Meta:
        ordering = ['initiative', 'order', '-priority', 'created_at']
        verbose_name = 'Initiative Action Item'
        verbose_name_plural = 'Initiative Action Items'

    def __str__(self):
        return f"{self.title} ({self.status})"

    def start(self, by='system'):
        """Mark as in progress."""
        self.status = self.Status.IN_PROGRESS
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def complete(self, by='system', notes=''):
        """Mark as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.completed_by = by
        if notes:
            self.completion_notes = notes
        self.save(update_fields=['status', 'completed_at', 'completed_by', 'completion_notes', 'updated_at'])

    def block(self, reason=''):
        """Mark as blocked."""
        self.status = self.Status.BLOCKED
        self.blocked_reason = reason
        self.save(update_fields=['status', 'blocked_reason', 'updated_at'])

    @property
    def is_overdue(self):
        """Check if action item is past due date."""
        if self.due_date and self.status not in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_until_due(self):
        """Days until due (negative if overdue)."""
        if self.due_date:
            return (self.due_date - timezone.now().date()).days
        return None
