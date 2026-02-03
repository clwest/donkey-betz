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
from django.db import models
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

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Initiative'
        verbose_name_plural = 'Initiatives'

    def __str__(self):
        return f"{self.name} (Stage {self.current_stage}/5)"

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

        # Create the deliverable
        deliverable = Deliverable.objects.create(
            user=user,
            title=f"Completed: {self.name}",
            content=full_content,
            deliverable_type='document',
            content_format='markdown',
            status='published',
            initiative=self,
            dream=source_dream,
            category='initiative_completion',
            agent_name='InitiativePipeline',
            metadata={
                'stages_completed': 5,
                'initiative_id': str(self.id),
                'completed_at': timezone.now().isoformat(),
                'stage_names': [stage.stage_name for stage in stages],
            }
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

    def __str__(self):
        return f"{self.initiative.name} - Stage {self.stage}: {self.stage_name}"

    @property
    def stage_name(self):
        return STAGE_NAMES.get(self.stage, 'Unknown')

    @property
    def stage_purpose(self):
        return STAGE_PURPOSES.get(self.stage, '')

    def approve(self, approved_by='system', notes=''):
        """
        Session 862: Mark this stage as approved and advance initiative.

        If all 5 stages are now approved, creates final Deliverable.

        Args:
            approved_by: Who approved (user or 'system')
            notes: Optional approval notes

        Returns:
            Deliverable or None: Final deliverable if all stages complete
        """
        self.status = self.StageStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        if notes:
            self.notes = (self.notes or '') + f"\n\nApproval notes: {notes}"
        self.save()

        # Try to advance the initiative
        self.initiative.advance_stage()

        # Check if all stages are now complete
        if self.initiative.is_complete():
            return self.initiative.create_final_deliverable()

        return None

    def reject(self, reason=''):
        """Mark this stage as rejected."""
        self.status = self.StageStatus.REJECTED
        self.rejection_reason = reason
        self.save()


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
