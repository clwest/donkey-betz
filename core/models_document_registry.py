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
