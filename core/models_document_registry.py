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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
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
        """Advance to the next stage if current stage is approved."""
        current = self.get_stage_document(self.current_stage)
        if current and current.status == 'APPROVED' and self.current_stage < 5:
            self.current_stage += 1
            self.save()
            return True
        return False


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

    def approve(self, approved_by='system'):
        """Mark this stage as approved."""
        self.status = self.StageStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()

        # Try to advance the initiative
        self.initiative.advance_stage()

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
