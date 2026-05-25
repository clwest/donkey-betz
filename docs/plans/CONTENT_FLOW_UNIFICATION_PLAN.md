<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL PLAN (Q4 2025 / Q1 2026 build phase).** Drafted during platform build-out; may be partially shipped, renamed in code, or quietly superseded. Preserved for historical reference, not current truth. For current truth see [`docs/INDEX.md`](../INDEX.md) + [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) + the latest handoff. See [`docs/plans/INDEX.md`](INDEX.md) for directory scope.

# Content Flow Unification Plan

**Created:** Session 861 (January 28, 2026)
**Implemented:** Session 862 (January 28, 2026)
**Status:** COMPLETE - All 4 phases implemented
**Priority:** HIGH - Critical data traceability gap

## Implementation Status

| Phase | Description | Status | PR |
|-------|-------------|--------|-----|
| Phase 1 | FK relationships | ✅ COMPLETE | #450-#451 |
| Phase 2 | Dream → Initiative bridge | ✅ COMPLETE | #452 |
| Phase 3 | ResearchResult model | ✅ COMPLETE | #452 |
| Phase 4 | Auto-stage progression & publish | ✅ COMPLETE | #452 |

---

## Executive Summary

The content creation system has **strong individual components** but **critical integration gaps** that prevent tracing content from idea to publication. This document outlines the complete fix plan across 4 phases.

### Previous Problem (RESOLVED)

```
AgentDream ──[DEAD END - No next step]       → NOW: promote_to_initiative()
Initiative ──[Works internally but isolated] → NOW: FK links to dreams, deliverables
Research ──[NO MODEL EXISTS]                 → NOW: ResearchResult model created
Content ──[Created but orphaned]             → NOW: Linked via FK relationships
Deliverable ──[No source tracking]           → NOW: initiative, dream FKs added
```

### Current State (IMPLEMENTED)

```
AgentDream (idea)
    ↓ promote_to_initiative() [Session 862]
Initiative (5-stage pipeline)
    ├─ Stage 1: ResearchResult → SelfBlog [Session 862]
    ├─ Stage 2-5: Various documents
    ↓ All approved → create_final_deliverable() [Session 862]
Deliverable (published)
    └─ Full traceability: dream_id, initiative_id, content FKs [Session 862]
```

---

## Current Architecture Analysis

### 1. AgentDream Model

**Location:** `core/models_unified_system.py:8687`

**Current Fields:**
```python
class AgentDream(models.Model):
    agent = ForeignKey(Agent)
    title = CharField(max_length=200)
    content = TextField()
    dream_type = CharField(choices=DREAM_TYPES)  # creative_idea, what_if, etc.

    # Boardroom promotion
    promoted_to_decision = BooleanField(default=False)
    promoted_at = DateTimeField(null=True)
    decision_outcome = CharField(null=True)  # approved, rejected, deferred

    # User interaction
    shown_to_user = BooleanField(default=False)
    user_reaction = CharField(null=True)
    user_feedback = TextField(blank=True)

    # Weak link
    project = ForeignKey(PartnershipProject, null=True)  # Optional, not used
```

**Problem:** Dreams can be promoted to boardroom but have no path to become Initiatives.

---

### 2. Initiative Model

**Location:** `core/models_document_registry.py`

**Current Fields:**
```python
class Initiative(models.Model):
    name = CharField(max_length=200)
    description = TextField()
    status = CharField(choices=STATUS_CHOICES)  # active, completed, archived
    current_stage = IntegerField(default=1)

    # Metadata
    created_by = CharField(max_length=100)
    parent_topic = CharField(max_length=200)  # For document linking

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**InitiativeStage Model:**
```python
class InitiativeStage(models.Model):
    class StageNumber(models.IntegerChoices):
        RESEARCH_BRIEF = 1
        PROTOTYPE_PLAN = 2
        EVALUATION_PROTOCOL = 3
        TECHNICAL_DESIGN = 4
        PILOT_EXECUTION = 5

    class StageStatus(models.TextChoices):
        PENDING = 'PENDING'
        DRAFT = 'DRAFT'
        IN_REVIEW = 'IN_REVIEW'
        APPROVED = 'APPROVED'
        REJECTED = 'REJECTED'
        SUPERSEDED = 'SUPERSEDED'

    initiative = ForeignKey(Initiative)
    stage = IntegerField(choices=StageNumber.choices)
    document = ForeignKey('core.SelfBlog', null=True)  # Only links to SelfBlog!
    status = CharField(choices=StageStatus.choices)

    approved_by = CharField(null=True)
    approved_at = DateTimeField(null=True)
    rejection_reason = TextField(blank=True)
```

**Problem:**
- No link FROM Dream
- Only links to SelfBlog (not podcasts, videos, etc.)
- No Research model for Stage 1

---

### 3. SelfBlog Model

**Location:** `core/models_unified_system.py:20012`

**Current Fields:**
```python
class SelfBlog(models.Model):
    title = CharField(max_length=500)
    intro = TextField()
    full_text = TextField()
    sections = JSONField(default=list)
    conclusion = TextField()

    category = CharField(choices=CATEGORIES)  # blog, audit, technical_document, etc.
    status = CharField(choices=STATUS)  # draft, approved, published

    # Weak tracing
    trace_id = UUIDField(null=True)  # Session 843
    project = ForeignKey(PartnershipProject, null=True)
    stats_snapshot = JSONField(default=dict)

    tags = JSONField(default=list)
    word_count = IntegerField(default=0)
```

**Problem:** No FK to Initiative or Dream - can't trace origin.

---

### 4. PodcastEpisode Model

**Location:** `core/models_podcast_studio.py:148`

**Current Fields:**
```python
class PodcastEpisode(models.Model):
    show = ForeignKey(PodcastShow)
    debate = OneToOneField(PodcastDebate, null=True)

    title = CharField(max_length=200)
    topic = CharField(max_length=500)
    script = TextField(blank=True)
    script_segments = JSONField(default=list)

    audio_file = FileField(null=True)
    audio_url = URLField(blank=True)

    status = CharField(choices=STATUS)  # draft, researching, debating, scripting, recording, complete

    created_at = DateTimeField(auto_now_add=True)
```

**Problem:** Completely isolated from Initiative pipeline.

---

### 5. Deliverable Model

**Location:** `core/models_deliverables.py:54`

**Current Fields:**
```python
class Deliverable(models.Model):
    user = ForeignKey(User)
    agent_name = CharField(max_length=100)  # String, not FK!

    title = CharField(max_length=500)
    content = TextField()
    content_type = CharField()  # blog, report, analysis, etc.
    content_format = CharField()  # markdown, html, json

    status = CharField(choices=STATUS)  # draft, ready, published, archived

    # Weak tracing (Session 843)
    trace_id = UUIDField(null=True)
    parent_object_type = CharField(null=True)  # String: 'agent_execution', 'conversation'
    parent_object_id = UUIDField(null=True)  # UUID as field, NOT FK!

    # Operation link
    source_operation = ForeignKey(WorkspaceOperation, null=True)

    # Quality metrics
    quality_score = FloatField(null=True)
    metadata = JSONField(default=dict)
```

**Problem:** Uses string UUIDs instead of real ForeignKeys - no database integrity.

---

## Implementation Plan

### Phase 1: Add Foreign Keys to Existing Models

**Goal:** Establish proper database relationships for traceability.

#### 1.1 Update Deliverable Model

**File:** `core/models_deliverables.py`

```python
# ADD these fields:
initiative = models.ForeignKey(
    'core.Initiative',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='deliverables',
    help_text='Initiative that produced this deliverable'
)

dream = models.ForeignKey(
    'core.AgentDream',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='deliverables',
    help_text='Dream that originated this deliverable'
)

self_blog = models.ForeignKey(
    'core.SelfBlog',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='deliverables',
    help_text='SelfBlog content for this deliverable'
)

podcast_episode = models.ForeignKey(
    'core.PodcastEpisode',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='deliverables',
    help_text='Podcast episode for this deliverable'
)
```

#### 1.2 Update SelfBlog Model

**File:** `core/models_unified_system.py`

```python
# ADD these fields to SelfBlog:
initiative = models.ForeignKey(
    'core.Initiative',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='blogs',
    help_text='Initiative this blog belongs to'
)

dream = models.ForeignKey(
    'AgentDream',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='blogs',
    help_text='Dream that originated this blog'
)

initiative_stage = models.ForeignKey(
    'core.InitiativeStage',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='blogs',
    help_text='Initiative stage this blog fulfills'
)
```

#### 1.3 Update PodcastEpisode Model

**File:** `core/models_podcast_studio.py`

```python
# ADD these fields to PodcastEpisode:
initiative = models.ForeignKey(
    'core.Initiative',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='podcast_episodes',
    help_text='Initiative this podcast belongs to'
)

dream = models.ForeignKey(
    'core.AgentDream',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='podcast_episodes',
    help_text='Dream that originated this podcast'
)

initiative_stage = models.ForeignKey(
    'core.InitiativeStage',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='podcast_episodes',
    help_text='Initiative stage this podcast fulfills'
)
```

#### 1.4 Update AgentDream Model

**File:** `core/models_unified_system.py`

```python
# ADD this field to AgentDream:
initiative = models.ForeignKey(
    'core.Initiative',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='source_dreams',
    help_text='Initiative created from this dream'
)
```

#### 1.5 Migration

```bash
python manage.py makemigrations core --name session_862_content_flow_fks
python manage.py migrate
```

---

### Phase 2: Dream → Initiative Bridge

**Goal:** When a Dream is approved in boardroom, automatically create an Initiative.

#### 2.1 Add Method to AgentDream

**File:** `core/models_unified_system.py`

```python
class AgentDream(models.Model):
    # ... existing fields ...

    def promote_to_initiative(self, approved_by='system'):
        """
        Session 862: Create an Initiative from this Dream.
        Called when dream is approved in boardroom.

        Returns:
            Initiative: The created initiative
        """
        from core.models_document_registry import Initiative, InitiativeStage

        if self.initiative:
            return self.initiative  # Already promoted

        # Create the Initiative
        initiative = Initiative.objects.create(
            name=self.title,
            description=self.content,
            status='active',
            current_stage=1,
            created_by=self.agent.name if self.agent else 'system',
            parent_topic=self.title,
        )

        # Create Stage 1 (Research Brief) as DRAFT
        InitiativeStage.objects.create(
            initiative=initiative,
            stage=1,  # RESEARCH_BRIEF
            status='DRAFT',
            notes=f"Created from Dream: {self.title}\n\nDream Content:\n{self.content}",
        )

        # Link dream to initiative
        self.initiative = initiative
        self.promoted_to_decision = True
        self.promoted_at = timezone.now()
        self.decision_outcome = 'approved'
        self.save()

        return initiative
```

#### 2.2 Update Boardroom Decision Flow

**File:** `core/services/boardroom_service.py` (or wherever boardroom decisions are handled)

```python
def approve_dream_decision(self, dream_id, approved_by):
    """When boardroom approves a dream, create initiative."""
    dream = AgentDream.objects.get(id=dream_id)

    # Create initiative from dream
    initiative = dream.promote_to_initiative(approved_by=approved_by)

    # Log the decision
    logger.info(f"Dream '{dream.title}' promoted to Initiative {initiative.id}")

    return initiative
```

---

### Phase 3: Create ResearchResult Model

**Goal:** Track research that feeds into Stage 1 (Research Brief) of initiatives.

#### 3.1 Create New Model

**File:** `core/models_research.py` (NEW FILE)

```python
"""
Session 862: Research Result Model

Tracks research conducted for Initiative Stage 1 (Research Brief).
Links spider data, search queries, and findings to initiatives.
"""

import uuid
from django.db import models
from django.utils import timezone


class ResearchResult(models.Model):
    """
    Research conducted for an Initiative's Research Brief stage.

    Captures:
    - What was researched (topic, queries)
    - Sources used (spider data, web searches)
    - Findings and analysis
    - Link to resulting document
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Initiative link
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.CASCADE,
        related_name='research_results',
        help_text='Initiative this research supports'
    )

    initiative_stage = models.ForeignKey(
        'core.InitiativeStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='research_results',
        help_text='Stage 1 this research fulfills'
    )

    # Research metadata
    topic = models.CharField(
        max_length=500,
        help_text='Research topic/question'
    )

    research_type = models.CharField(
        max_length=50,
        choices=[
            ('market_analysis', 'Market Analysis'),
            ('competitor_research', 'Competitor Research'),
            ('technical_research', 'Technical Research'),
            ('user_research', 'User Research'),
            ('trend_analysis', 'Trend Analysis'),
            ('feasibility_study', 'Feasibility Study'),
            ('literature_review', 'Literature Review'),
            ('data_analysis', 'Data Analysis'),
        ],
        default='market_analysis'
    )

    # Research inputs
    queries = models.JSONField(
        default=list,
        help_text='Search queries used during research'
    )

    spider_sources = models.ManyToManyField(
        'core.SpiderData',
        blank=True,
        related_name='research_results',
        help_text='Spider data used in this research'
    )

    external_sources = models.JSONField(
        default=list,
        help_text='External URLs and sources consulted'
    )

    # Research outputs
    findings = models.JSONField(
        default=dict,
        help_text='Structured research findings'
    )

    summary = models.TextField(
        blank=True,
        help_text='Executive summary of research'
    )

    recommendations = models.JSONField(
        default=list,
        help_text='Recommendations based on research'
    )

    confidence_score = models.FloatField(
        default=0.0,
        help_text='Confidence in research findings (0-1)'
    )

    # Resulting document
    self_blog = models.ForeignKey(
        'core.SelfBlog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='research_results',
        help_text='Research Brief document created from this research'
    )

    # Agent tracking
    conducted_by = models.CharField(
        max_length=100,
        default='ResearchAgent',
        help_text='Agent that conducted the research'
    )

    # Timestamps
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_research_result'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['initiative', 'research_type']),
            models.Index(fields=['completed_at']),
        ]

    def __str__(self):
        return f"Research: {self.topic[:50]} for {self.initiative.name}"

    def mark_complete(self, findings=None, summary=None):
        """Mark research as complete with findings."""
        if findings:
            self.findings = findings
        if summary:
            self.summary = summary
        self.completed_at = timezone.now()
        self.save()

    def create_research_brief(self):
        """
        Create a SelfBlog (Research Brief) from this research.
        Links it to the Initiative Stage 1.
        """
        from core.models_unified_system import SelfBlog

        # Create the research brief document
        blog = SelfBlog.objects.create(
            title=f"Research Brief: {self.topic}",
            intro=self.summary or f"Research findings for {self.initiative.name}",
            full_text=self._format_findings_as_markdown(),
            category='research_brief',
            status='draft',
            initiative=self.initiative,
            tags=['research', 'brief', self.research_type],
        )

        # Link to this research
        self.self_blog = blog
        self.save()

        # Link to initiative stage
        if self.initiative_stage:
            self.initiative_stage.document = blog
            self.initiative_stage.status = 'DRAFT'
            self.initiative_stage.save()

        return blog

    def _format_findings_as_markdown(self):
        """Format findings as markdown document."""
        md = f"# Research Brief: {self.topic}\n\n"
        md += f"## Executive Summary\n\n{self.summary}\n\n"

        md += "## Research Methodology\n\n"
        md += f"- **Type:** {self.get_research_type_display()}\n"
        md += f"- **Conducted by:** {self.conducted_by}\n"
        md += f"- **Confidence Score:** {self.confidence_score:.0%}\n\n"

        if self.queries:
            md += "### Search Queries\n\n"
            for q in self.queries:
                md += f"- {q}\n"
            md += "\n"

        md += "## Findings\n\n"
        if isinstance(self.findings, dict):
            for key, value in self.findings.items():
                md += f"### {key}\n\n{value}\n\n"
        else:
            md += str(self.findings)

        if self.recommendations:
            md += "## Recommendations\n\n"
            for i, rec in enumerate(self.recommendations, 1):
                md += f"{i}. {rec}\n"

        return md
```

#### 3.2 Add to Models Init

**File:** `core/models/__init__.py`

```python
# Add import
from core.models_research import ResearchResult
```

#### 3.3 Migration

```bash
python manage.py makemigrations core --name session_862_research_result
python manage.py migrate
```

---

### Phase 4: Auto-Stage Progression & Publish

**Goal:** Automatically advance stages when content is approved, and create Deliverable on completion.

#### 4.1 Update InitiativeStage.approve()

**File:** `core/models_document_registry.py`

```python
class InitiativeStage(models.Model):
    # ... existing fields ...

    def approve(self, approved_by='system', notes=''):
        """
        Session 862: Approve this stage and advance initiative.

        If all 5 stages are approved, creates final Deliverable.
        """
        from core.models_deliverables import Deliverable

        self.status = self.StageStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        if notes:
            self.notes = (self.notes or '') + f"\n\nApproval notes: {notes}"
        self.save()

        # Advance initiative to next stage
        self.initiative.advance_stage()

        # Check if all stages complete
        if self.initiative.current_stage > 5:
            self._create_final_deliverable()

        return self

    def _create_final_deliverable(self):
        """Create published Deliverable from completed initiative."""
        from core.models_deliverables import Deliverable
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get all stage documents
        stages = self.initiative.stages.filter(
            status=self.StageStatus.APPROVED
        ).order_by('stage')

        # Compile content from all stages
        content_parts = []
        for stage in stages:
            if stage.document:
                content_parts.append(f"## Stage {stage.stage}: {stage.get_stage_display()}\n\n")
                content_parts.append(stage.document.full_text or stage.document.intro)
                content_parts.append("\n\n---\n\n")

        full_content = ''.join(content_parts)

        # Get user (default to first superuser if none specified)
        user = User.objects.filter(is_superuser=True).first()

        # Create the deliverable
        deliverable = Deliverable.objects.create(
            user=user,
            title=f"Completed: {self.initiative.name}",
            content=full_content,
            content_type='initiative_completion',
            content_format='markdown',
            status='published',
            initiative=self.initiative,
            dream=self.initiative.source_dreams.first(),
            metadata={
                'stages_completed': 5,
                'initiative_id': str(self.initiative.id),
                'completed_at': timezone.now().isoformat(),
            }
        )

        # Update initiative status
        self.initiative.status = 'completed'
        self.initiative.save()

        return deliverable
```

#### 4.2 Add Initiative.advance_stage()

**File:** `core/models_document_registry.py`

```python
class Initiative(models.Model):
    # ... existing fields ...

    def advance_stage(self):
        """Advance to next stage if current stage is approved."""
        current = self.stages.filter(stage=self.current_stage).first()

        if current and current.status == 'APPROVED':
            self.current_stage += 1
            self.save()

            # Create next stage if it doesn't exist and we're not done
            if self.current_stage <= 5:
                InitiativeStage.objects.get_or_create(
                    initiative=self,
                    stage=self.current_stage,
                    defaults={'status': 'PENDING'}
                )

        return self.current_stage
```

#### 4.3 Update MissionControl Publish

**File:** `core/services/mission_control_executor.py`

```python
def _execute_publish(self, attention_item, user, feedback, extra_data):
    """
    Session 862: Enhanced publish with initiative/dream linking.
    """
    # ... existing code to get content ...

    # Try to find initiative/dream from context
    initiative = None
    dream = None

    # Check if content has initiative link
    if hasattr(content, 'initiative') and content.initiative:
        initiative = content.initiative
        dream = initiative.source_dreams.first()

    # Check metadata for IDs
    if not initiative and extra_data.get('initiative_id'):
        from core.models_document_registry import Initiative
        initiative = Initiative.objects.filter(id=extra_data['initiative_id']).first()

    if not dream and extra_data.get('dream_id'):
        from core.models_unified_system import AgentDream
        dream = AgentDream.objects.filter(id=extra_data['dream_id']).first()

    # Create Deliverable with proper links
    deliverable = Deliverable.objects.create(
        user=user,
        title=title,
        content=body,
        content_type=content_type,
        status='published',
        initiative=initiative,  # NEW: Real FK
        dream=dream,  # NEW: Real FK
        self_blog=content if hasattr(content, 'full_text') else None,  # NEW
        metadata={
            'tags': content.get('tags') if isinstance(content, dict) else [],
            'source_agent': attention_item.source_agent,
            'attention_item_id': str(attention_item.id),
        }
    )

    return deliverable
```

---

## Migration Summary

### Migrations to Create

1. `0202_session_862_content_flow_fks.py`
   - Add `initiative`, `dream` FKs to Deliverable
   - Add `self_blog`, `podcast_episode` FKs to Deliverable
   - Add `initiative`, `dream`, `initiative_stage` FKs to SelfBlog
   - Add `initiative`, `dream`, `initiative_stage` FKs to PodcastEpisode
   - Add `initiative` FK to AgentDream

2. `0203_session_862_research_result.py`
   - Create ResearchResult model
   - Create indexes and relationships

---

## Testing Plan

### After Phase 1 (FKs)

```python
# Verify FKs work
from core.models_deliverables import Deliverable
from core.models_document_registry import Initiative

initiative = Initiative.objects.first()
deliverable = Deliverable.objects.create(
    title="Test",
    content="Test content",
    initiative=initiative,  # Should work
)
assert deliverable.initiative == initiative

# Reverse lookup
assert initiative.deliverables.count() >= 1
```

### After Phase 2 (Dream Bridge)

```python
from core.models_unified_system import AgentDream

dream = AgentDream.objects.first()
initiative = dream.promote_to_initiative(approved_by='test')

assert dream.initiative == initiative
assert initiative.current_stage == 1
assert initiative.stages.filter(stage=1).exists()
```

### After Phase 3 (Research)

```python
from core.models_research import ResearchResult

research = ResearchResult.objects.create(
    initiative=initiative,
    topic="Market Analysis for XYZ",
    research_type='market_analysis',
    summary="Key findings...",
    findings={'market_size': '$10B', 'growth': '15%'},
)

blog = research.create_research_brief()
assert blog.initiative == initiative
assert 'Research Brief' in blog.title
```

### After Phase 4 (Auto-Progression)

```python
# Approve all 5 stages
for stage_num in range(1, 6):
    stage = initiative.stages.get(stage=stage_num)
    stage.approve(approved_by='test')

# Check deliverable created
assert initiative.status == 'completed'
assert initiative.deliverables.filter(status='published').exists()
```

---

## Rollback Plan

If issues arise, migrations can be reversed:

```bash
# Rollback Phase 4+3
python manage.py migrate core 0202_session_862_content_flow_fks

# Rollback Phase 1
python manage.py migrate core 0201_session_861_spider_aggregation
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `core/models_deliverables.py` | Add initiative, dream, self_blog, podcast_episode FKs |
| `core/models_unified_system.py` | Add initiative FK to AgentDream; Add initiative, dream, initiative_stage FKs to SelfBlog |
| `core/models_podcast_studio.py` | Add initiative, dream, initiative_stage FKs to PodcastEpisode |
| `core/models_document_registry.py` | Add advance_stage(), approve() methods |
| `core/models_research.py` | NEW FILE - ResearchResult model |
| `core/models/__init__.py` | Add ResearchResult import |
| `core/services/mission_control_executor.py` | Update _execute_publish() with FK linking |
| `core/services/boardroom_service.py` | Add approve_dream_decision() |

---

## Success Criteria

1. **Traceability:** Can query `Deliverable.objects.filter(initiative=X)` to find all outputs
2. **Dream → Initiative:** Approving a dream creates an initiative automatically
3. **Research Tracking:** Stage 1 has ResearchResult with spider sources linked
4. **Auto-Publish:** Completing all 5 stages creates a published Deliverable
5. **No Orphans:** All content has either initiative_id or dream_id set

---

## Estimated Effort

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1: FKs | 2-3 hours | None |
| Phase 2: Dream Bridge | 1-2 hours | Phase 1 |
| Phase 3: Research Model | 2-3 hours | Phase 1 |
| Phase 4: Auto-Progression | 2-3 hours | Phase 1, 2, 3 |
| **Total** | **7-11 hours** | Sequential |

---

## Document Owner

**Session:** 861
**Created:** January 28, 2026
**Implementation Session:** 862
