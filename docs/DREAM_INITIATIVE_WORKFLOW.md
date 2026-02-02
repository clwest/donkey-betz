# Dream → Initiative Workflow

**Created:** Session 871 (January 29, 2026)
**Updated:** Session 906 (February 1, 2026)
**Status:** ACTIVE | AUTO-PROGRESSION ENABLED | TRACKING COMPLETE

---

## Overview

The Dream → Initiative workflow is an autonomous idea-to-implementation pipeline where AI agents generate creative ideas ("dreams") during idle time, which flow through quality gates and ultimately become structured deliverables.

```
Dream Generation → Scoring → Boardroom → Initiative → 5 Stages → Deliverable
```

---

## Architecture

### Data Flow

```
AgentDream (creative idea)
    ↓ Score ≥ 0.7
    ↓ Boardroom approval
Initiative
    ├── Stage 1: Research Brief
    ├── Stage 2: Prototype Plan
    ├── Stage 3: Evaluation Protocol
    ├── Stage 4: Technical Design
    └── Stage 5: Pilot Execution
            ↓ All stages APPROVED
        Deliverable (published)
```

### Key Models

| Model | File | Purpose |
|-------|------|---------|
| `AgentDream` | `core/models_unified_system.py:8695` | Creative ideas from idle agents |
| `Initiative` | `core/models_document_registry.py:37` | Approved dreams promoted to projects |
| `InitiativeStage` | `core/models_document_registry.py:250` | 5-stage pipeline stages |
| `DreamImplementation` | `core/models_unified_system.py:9344` | Execution tracking |
| `Deliverable` | `core/models_deliverables.py` | Final published output |

---

## Phase 1: Dream Generation

**Trigger:** Celery scheduled task (`generate_agent_dreams`)

When agents are idle (no executions in last 30 minutes), they "dream" - generating creative ideas based on their knowledge.

### Dream Types
| Type | Description |
|------|-------------|
| `creative_idea` | Novel feature or product concept |
| `what_if` | Speculative exploration |
| `mashup` | Combination of existing ideas |
| `prediction` | Future trend analysis |
| `improvement` | Enhancement to existing feature |
| `observation` | Pattern recognition insight |
| `wild_thought` | Experimental concept |

### Dream Origins (Session 765)
| Origin | Promotion Eligible |
|--------|-------------------|
| `serious` | Yes |
| `speculative` | Yes |
| `probe` | No - exploratory only |
| `joke` | No - humor only |

### Code Reference
```python
# core/tasks.py:8436
@shared_task
def generate_agent_dreams(max_dreamers=5, dreams_per_agent=2):
    # Find idle agents
    recent_cutoff = timezone.now() - timedelta(minutes=30)
    idle_agents = Agent.objects.exclude(
        executions__created_at__gte=recent_cutoff
    )

    # Generate dream via GPT-5-mini
    dream = AgentDream.objects.create(
        agent=agent,
        title=title,
        content=content,
        dream_type=selected_type,
        origin='serious'
    )
```

---

## Phase 2: Scoring & Promotion

**Trigger:** Celery scheduled task (`score_and_promote_dreams`)

Dreams are scored on three dimensions and auto-promoted if they meet the threshold.

### Scoring Dimensions
| Score | Weight | Description |
|-------|--------|-------------|
| `creativity_score` | 25% | Novelty and originality |
| `actionability_score` | 45% | Can it be implemented? |
| `relevance_score` | 30% | Matches active projects? |

### Composite Score
```python
composite = (creativity * 0.25) + (actionability * 0.45) + (relevance * 0.30)
```

### Promotion Threshold
- **Score ≥ 0.7:** Auto-promoted to Boardroom
- **Score < 0.7:** Remains in dream backlog

### Code Reference
```python
# core/tasks.py:8901
@shared_task
def score_and_promote_dreams(max_dreams=50, promote_threshold=0.7):
    if composite_score >= promote_threshold:
        dream.promoted_to_decision = True
        dream.decision_outcome = 'pending'
        dream.promoted_at = timezone.now()
```

---

## Phase 3: Boardroom Decision

**Trigger:** User interaction in UI

Promoted dreams appear in the Boardroom for human review.

### Decision Outcomes
| Outcome | Next Step |
|---------|-----------|
| `pending` | Awaiting review |
| `approved` | Creates Initiative |
| `deferred` | Review later |
| `rejected` | Archived |

### UI Location
- **Tab:** Initiatives (Workspace)
- **View:** Dream Boardroom panel

---

## Phase 4: Initiative Creation

**Trigger:** Signal handler on dream approval

When `decision_outcome` changes to `'approved'`, a signal automatically creates an Initiative.

### Signal Handler
```python
# core/signals/dream_signals.py:46
@receiver(post_save, sender='core.AgentDream')
def trigger_dream_execution_on_approval(sender, instance, **kwargs):
    if instance.decision_outcome == 'approved':
        initiative = instance.promote_to_initiative()
```

### What Gets Created
1. **Initiative** - Project container
2. **Stage 1** - Research Brief (status: DRAFT)
3. **Dream link** - `dream.initiative` FK set

### Code Reference
```python
# core/models_unified_system.py:9041
def promote_to_initiative(self, approved_by='system'):
    initiative = Initiative.objects.create(
        name=self.title,
        description=self.content,
        status='active',
        current_stage=1,
    )

    InitiativeStage.objects.create(
        initiative=initiative,
        stage=1,
        status='DRAFT',
    )

    self.initiative = initiative
    self.save()
    return initiative
```

---

## Phase 5: Stage Pipeline

**Trigger:** Celery scheduled task (`advance_initiative_pipeline`)

### The 5 Stages

| Stage | Name | Purpose | Document Type |
|-------|------|---------|---------------|
| 1 | **Research Brief** | Why does this matter? | Market analysis, feasibility |
| 2 | **Prototype Plan** | How would we build this? | Architecture, design |
| 3 | **Evaluation Protocol** | Should we proceed? | Testing criteria, acceptance |
| 4 | **Technical Design** | Exactly what to build | Implementation specs |
| 5 | **Pilot Execution** | What happened? | Deployment, postmortem |

### Stage Statuses
| Status | Description |
|--------|-------------|
| `PENDING` | Not started |
| `DRAFT` | Document created |
| `IN_REVIEW` | Awaiting approval |
| `APPROVED` | Stage complete |
| `REJECTED` | Needs revision |
| `SUPERSEDED` | Replaced by newer version |

### Stage Advancement
```python
# core/models_document_registry.py:143
def advance_stage(self):
    current_stage = self.get_stage_document(self.current_stage)
    if current_stage.status == 'APPROVED' and self.current_stage < 5:
        self.current_stage += 1
        InitiativeStage.objects.create(
            initiative=self,
            stage=self.current_stage,
            status='PENDING'
        )
```

### Auto-Progression (Session 906)

The system automatically advances initiatives through stages based on document quality. Runs every 10 minutes via Celery Beat.

**Quality Criteria:**
- Content length ≥ 500 characters
- Required sections present (varies by stage)
- No "insufficient data" markers
- Confidence threshold: **60%**

**Service:** `core/services/initiative_auto_progression.py`

```python
from core.services.initiative_auto_progression import InitiativeAutoProgressionService

service = InitiativeAutoProgressionService()
result = service.check_stage_for_progression(initiative_stage)
# Returns: {'qualifies': True, 'confidence': 0.75, 'criteria_met': [...], 'criteria_missing': [...]}

# Progress if qualifies
if result['qualifies']:
    service.progress_initiative_stage(initiative)
    service.trigger_next_stage_generation(initiative)  # Async via Celery
```

**Required Sections by Stage:**
| Stage | Required Sections |
|-------|-------------------|
| 1 (Research Brief) | executive_summary, key_findings, opportunity_analysis |
| 2 (Prototype Plan) | scope, architecture, milestones |
| 3 (Evaluation Protocol) | criteria, metrics, methodology |
| 4 (Technical Design) | implementation, dependencies, specifications |
| 5 (Pilot Execution) | results, lessons_learned, recommendations |

### Document Generation
Stage documents are generated by `TechnicalDocumentAgent`:

```python
# core/tasks.py:30642
@shared_task
def advance_initiative_pipeline(limit=5):
    for stage in pending_stages:
        # Generate document using agent
        agent = TechnicalDocumentAgent()
        content = agent.execute(task=stage_prompt)

        # Create SelfBlog and link
        blog = SelfBlog.objects.create(
            title=f"[Stage {stage.stage}] {initiative.name}",
            full_text=content,
        )
        stage.document = blog
        stage.status = 'DRAFT'
```

---

## Initiative Tracking (Session 906)

Auto-created initiatives (from blocked research, spider signals) now have full tracking records to enable the "Origin & Trigger" UI feature.

### Tracking Models

| Model | Purpose |
|-------|---------|
| `HiveMindSession` | Session record with `session_mode='autonomous'` |
| `HiveMindContribution` | Agent contribution linked to session |
| `AgentExecution` | Execution record with `metadata.initiative_id` |

### Auto-Creation Source

When blocked research triggers initiative creation (`autonomous_action_executor.py:_create_blocked_research_result`), the system now:

1. Creates `HiveMindSession` (mode: 'autonomous', status: 'completed')
2. Creates `HiveMindContribution` with research context
3. Creates `AgentExecution` with `metadata.initiative_id` linking

### Backfilling Orphan Initiatives

Pre-Session 906 initiatives without tracking can be fixed:

```bash
# Show orphan initiatives (dry run)
python manage.py fix_orphan_initiative_tracking

# Create tracking records for orphan initiatives
python manage.py fix_orphan_initiative_tracking --fix --limit=100
```

This creates backfilled records marked `[Session 906 Backfill]` in the synthesis.

---

## Phase 6: Completion

**Trigger:** All 5 stages APPROVED

When all stages are approved, the initiative is complete and generates a final Deliverable.

### Completion Check
```python
# core/models_document_registry.py:168
def is_complete(self):
    return self.stages.filter(status='APPROVED').count() == 5
```

### Final Deliverable Creation
```python
# core/models_document_registry.py:183
def create_final_deliverable(self):
    # Compile all stage documents
    content_parts = []
    for stage in self.stages.filter(status='APPROVED'):
        content_parts.append(stage.document.full_text)

    # Create published Deliverable
    deliverable = Deliverable.objects.create(
        title=f"Completed: {self.name}",
        content=''.join(content_parts),
        status='published',
        initiative=self,
    )

    self.status = 'COMPLETED'
    self.save()
    return deliverable
```

---

## Key Files Reference

### Models
| File | Lines | Content |
|------|-------|---------|
| `core/models_unified_system.py` | 8695-9086 | AgentDream |
| `core/models_unified_system.py` | 9344-9576 | DreamImplementation |
| `core/models_document_registry.py` | 37-228 | Initiative |
| `core/models_document_registry.py` | 250-354 | InitiativeStage |

### Celery Tasks
| Task | File:Line | Schedule |
|------|-----------|----------|
| `generate_agent_dreams` | `core/tasks.py:8436` | Every 2 hours |
| `score_and_promote_dreams` | `core/tasks.py:8901` | Every hour |
| `advance_initiative_pipeline` | `core/tasks.py:30642` | Every 30 min |
| `process_initiative_auto_progression` | `core/tasks.py` | Every 10 min |
| `detect_duplicate_initiatives` | `core/tasks.py` | Daily at 2 AM |

### Management Commands (Session 906)

```bash
# Title Cleanup - fix technical description titles
python manage.py clean_initiative_names              # Dry run
python manage.py clean_initiative_names --fix        # Apply fixes

# Duplicate Detection & Consolidation
python manage.py consolidate_duplicate_initiatives            # Dry run
python manage.py consolidate_duplicate_initiatives --fix      # Merge duplicates
python manage.py consolidate_duplicate_initiatives --threshold=0.8  # Higher similarity

# Orphan Initiative Tracking Fix
python manage.py fix_orphan_initiative_tracking              # Dry run
python manage.py fix_orphan_initiative_tracking --fix        # Create tracking records
python manage.py fix_orphan_initiative_tracking --initiative-id=<uuid>  # Single initiative

# Stage 2 Document Generation (sync mode for railway)
python manage.py trigger_stage2_generation --run --sync --limit=5

# Research Brief Backfill
python manage.py backfill_research_brief_links              # Dry run
python manage.py backfill_research_brief_links --fix        # Link briefs to stages
```

### Services
| Service | File | Purpose |
|---------|------|---------|
| `InitiativeIntegrationService` | `core/services/initiative_integration_service.py` | Pipeline orchestration |

### Signals
| Signal | File:Line | Trigger |
|--------|-----------|---------|
| `trigger_dream_execution_on_approval` | `core/signals/dream_signals.py:46` | Dream approved |

---

## UI Integration

### Workspace Tabs

| Tab | Feature |
|-----|---------|
| **Initiatives** | Dream boardroom, stage viewer, approval workflow |
| **AI Mind** | Dream visualization, consciousness metrics |
| **Content** | Stage documents, deliverables |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/initiatives/` | GET | List initiatives |
| `/api/initiatives/populate/` | POST | Create test data |
| `/api/v1/reasoning/thoughts/` | GET | Dream-like thoughts |

---

## Configuration

### Thresholds
| Setting | Value | Description |
|---------|-------|-------------|
| `promote_threshold` | 0.7 | Minimum composite score for Boardroom |
| `agent_idle_time` | 30 min | Time before agent can dream |
| `dream_lookback` | 7 days | How far back to score unscored dreams |

### Stage Weights
| Stage | Completion Weight |
|-------|-------------------|
| Stage 1 | 15% |
| Stage 2 | 20% |
| Stage 3 | 20% |
| Stage 4 | 25% |
| Stage 5 | 20% |

---

## Session History

| Session | Contribution |
|---------|--------------|
| 366 | Dream productization - actionability & relevance scoring |
| 765 | Origin tracking - prevent jokes/probes from promotion |
| 847 | Initiative Integration Service - connects to 5-stage pipeline |
| 862 | Content Flow Unification - Dream → Initiative bridge |
| 866 | Pipeline advancement - auto-generate stage documents |
| 905 | Auto-Progression Service - quality-based stage advancement (60%+ confidence) |
| 906 | Title Cleanup + Duplicate Detection + Orphan Tracking Fix |

---

## Troubleshooting

### Dreams Not Being Generated
1. Check agent idle time (need 30+ min without activity)
2. Verify Celery Beat is running: `make celery`
3. Check task logs: `celery -A core inspect active`

### Dreams Not Promoted
1. Check composite score (need ≥ 0.7)
2. Verify origin is `serious` or `speculative`
3. Check `promote_threshold` setting

### Stages Not Advancing
1. Verify stage status is `APPROVED`
2. Check `advance_initiative_pipeline` task is scheduled
3. Verify `TechnicalDocumentAgent` is available

### Deliverable Not Created
1. Verify all 5 stages are `APPROVED`
2. Check `is_complete()` returns True
3. Look for errors in `create_final_deliverable()`

---

*Documentation created by Claude Code - Session 871*
