<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.
> **Note:** content may be stale (last refreshed 2026-02-16) — workflow direction is still canonical (cited from CLAUDE.md), but verify stage names + service signatures against current code before relying on specifics.

# Dream → Initiative Workflow

**Created:** Session 871 (January 29, 2026)
**Updated:** Session 914.7 (February 2, 2026)
**Status:** ACTIVE | AUTO-PROGRESSION ENABLED | FOUNDER INTENT REQUIRED | EXECUTION TRACKS | SEMANTIC DRIFT GATES | RATE LIMITS | DAILY PRIORITIES | BOARDROOM APPROVAL | OPERATING RHYTHM | TRACKING COMPLETE

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

### Founder Intent (Session 914)

Before an initiative can progress beyond Stage 1, the founder must set explicit intent. This prevents the system from generating "beautiful docs for the wrong thing."

**Founder Intent Fields:**
| Field | Purpose |
|-------|---------|
| `execution_speed` | `fast` (stop at Stage 2), `balanced` (normal), `thorough` (extended) |
| `risk_tolerance` | `low`, `medium`, `high` |
| `budget_engineering_hours` | Max engineering time |
| `budget_llm_spend` | Max LLM API spend ($) |
| `stop_rule` | What outcome kills this initiative |
| `requires_boardroom_approval` | Whether explicit approval needed |

**Progression Control:**
- Stage 1 → Stage 2: **Can progress without intent** (to generate initial research)
- Stage 2+: **Requires founder intent** - system pauses and awaits human input
- Fast Track: Stops at Stage 2, awaits founder decision
- Thorough: Extended validation, Boardroom approval required

**Setting Intent:**
```bash
# List initiatives awaiting intent
python manage.py set_founder_intent --list

# Set intent for specific initiative
python manage.py set_founder_intent --initiative-id=<uuid> --speed=balanced

# Set intent for all pending initiatives
python manage.py set_founder_intent --all-pending --speed=fast

# Interactive mode
python manage.py set_founder_intent --interactive
```

**Code Reference:**
```python
# Set intent programmatically
initiative.set_founder_intent(
    execution_speed='balanced',
    risk_tolerance='medium',
    budget_engineering_hours=40,
    budget_llm_spend=50.00,
    stop_rule='If user adoption <10% after 30 days, kill it',
    set_by='founder'
)

# Check if can progress
if initiative.can_auto_progress:
    # Proceed with auto-progression
else:
    reason = initiative.progression_blocked_reason
    # "Awaiting founder intent - set execution_speed, risk_tolerance, and stop_rule"
```

---

### Execution Track (Session 914.2)

Initiatives follow one of two tracks based on their content and risk profile:

**Track Types:**
| Track | Max Stage | Use Case |
|-------|-----------|----------|
| `fast_track` | Stage 2 | Quick experiments, low-risk features, internal tools |
| `institutional` | Stage 5 | Public-facing, compliance-required, high-risk initiatives |

**Content Flags (Auto-Detection):**
| Flag | Meaning | Triggers Institutional |
|------|---------|----------------------|
| `external_data` | Uses external data/APIs | Yes |
| `user_data` | Handles user PII | Yes |
| `public_publishing` | Public-facing content | Yes |
| `legal_compliance` | Legal/regulatory requirements | Yes |
| `financial` | Financial transactions | Yes |
| `irreversible` | Irreversible actions | Yes |

**Institutional Stage Approvals:**
- Stage 2: Requires explicit approval before Stage 3
- Stage 3: Requires explicit approval before Stage 4
- Stage 4: Requires explicit approval before Stage 5
- Compliance review must be completed before any stage progression

**Setting Execution Track:**
```bash
# Auto-detect track based on content
python manage.py set_founder_intent --initiative-id=<uuid> --auto-detect-track

# Explicitly set track
python manage.py set_founder_intent --initiative-id=<uuid> --track=institutional

# Approve a stage (institutional track)
python manage.py set_founder_intent --initiative-id=<uuid> --approve-stage=2

# Complete compliance review
python manage.py set_founder_intent --initiative-id=<uuid> --complete-compliance
```

**Code Reference:**
```python
# Auto-detect track
track = initiative.auto_detect_execution_track()  # Returns 'fast_track' or 'institutional'

# Set track explicitly
initiative.set_execution_track(
    track='institutional',
    content_flags=['user_data', 'public_publishing'],
    set_by='founder'
)

# Check track properties
if initiative.is_fast_track:
    print(f"Max stage: {initiative.max_stage}")  # 2

if initiative.is_institutional:
    # Check if stage needs approval
    if initiative.requires_stage_approval(2):
        if not initiative.is_stage_approved(2):
            # Need to approve before progression
            initiative.approve_stage(2, approved_by='founder')
```

---

### Semantic Quality Gates (Session 914.3)

Ensures stage documents stay aligned with the original initiative intent. Uses embeddings to measure semantic similarity and blocks progression if drift is detected.

**Drift Thresholds:**
| Threshold | Similarity Required | Use Case |
|-----------|---------------------|----------|
| `strict` | 75%+ | Critical initiatives, precise alignment needed |
| `balanced` | 65%+ | Default - reasonable flexibility |
| `relaxed` | 55%+ | Exploratory initiatives, more flexibility |
| `disabled` | N/A | Skip drift checking entirely |

**How It Works:**
1. Compare initiative description + dream content → stage document content
2. Generate embeddings using OpenAI text-embedding-3-small
3. Calculate cosine similarity
4. If similarity < threshold, flag as "drifted"
5. Block auto-progression until human review or override

**Stage-Specific Adjustments:**
| Stage | Threshold Adjustment | Reason |
|-------|---------------------|--------|
| Stage 1 | No adjustment | Research should match intent |
| Stage 2 | +5% tolerance | Prototype may refine approach |
| Stage 3 | +5% tolerance | Evaluation may add metrics |
| Stage 4 | +10% tolerance | Technical details diverge naturally |
| Stage 5 | +10% tolerance | Execution may adapt to reality |

**Management Commands:**
```bash
# Check drift for an initiative
python manage.py check_initiative_drift --initiative-id=<uuid>

# Check all initiatives
python manage.py check_initiative_drift --all

# List flagged initiatives
python manage.py check_initiative_drift --list-flagged

# Override drift (allow progression)
python manage.py check_initiative_drift --initiative-id=<uuid> --stage=2 --override --reason="Intentional pivot"

# Set drift threshold
python manage.py check_initiative_drift --initiative-id=<uuid> --set-threshold=relaxed

# Disable drift checking
python manage.py check_initiative_drift --initiative-id=<uuid> --disable-drift
```

**Code Reference:**
```python
from core.services.semantic_drift_detector import check_semantic_drift, get_drift_detector

# Check a single stage
result = check_semantic_drift(initiative_stage)
if result['has_drift']:
    print(f"Drift: {result['drift_score']:.0%}")
    print(f"Similarity: {result['similarity_score']:.0%}")

# Check entire initiative
detector = get_drift_detector()
result = detector.check_initiative_drift(str(initiative.id))
print(f"Overall alignment: {result['overall_alignment']:.0%}")
```

---

### Rate Limits (Session 914.4)

Controls LLM spend by limiting how many stage progressions can happen per day.

**Default Limit:** 40 progressions/day

**How It Works:**
1. Each progression check first verifies rate limit
2. If limit reached, returns `rate_limited: True` error
3. Count resets at midnight (UTC)
4. Admin can reset count or adjust limit

**Management Commands:**
```bash
# View current rate limit status
python manage.py initiative_rate_limit --status

# Reset daily count (admin override)
python manage.py initiative_rate_limit --reset

# Set custom limit for today
python manage.py initiative_rate_limit --set-limit=60

# View recent progression history
python manage.py initiative_rate_limit --history
```

**Configuration:**
```python
# settings.py - Override default limit
INITIATIVE_DAILY_PROGRESSION_LIMIT = 60  # Default is 40
```

**Code Reference:**
```python
from core.services.initiative_auto_progression import (
    get_daily_progression_stats,
    reset_daily_progression_count,
    check_rate_limit
)

# Check current status
stats = get_daily_progression_stats()
print(f"Used: {stats['count']}/{stats['limit']}")
print(f"Remaining: {stats['remaining']}")

# Check if rate limited
can_progress, stats = check_rate_limit()
if not can_progress:
    print("Rate limit reached!")

# Reset count (admin)
reset_daily_progression_count()
```

---

### Daily Priorities (Session 914.5)

With 180+ initiatives, the system treats all equally. The Daily Priority Scan identifies the top 5 initiatives to focus resources on.

**How It Works:**
1. Run daily scan (morning) to compute priority scores for all active initiatives
2. Mark top 5 as "daily focus" initiatives
3. Auto-progression can prioritize daily focus initiatives
4. Dashboard shows daily focus clearly

**Priority Scoring Factors:**
| Factor | Boost | Description |
|--------|-------|-------------|
| Stage | +10% (Stage 1), +5% (Stage 2) | Earlier stages need to unblock pipeline |
| Freshness | +10% (updated today), +5% (this week), -10% (stale >14 days) | Active initiatives get priority |
| Speed | +10% (fast track), -5% (thorough) | Fast track initiatives move faster |
| Track | +5% (institutional) | Institutional track typically more important |
| Intent | +10% (set), -10% (not set) | Ready-to-go initiatives prioritized |

**Management Commands:**
```bash
# Run the daily priority scan
python manage.py daily_priorities --scan

# View current daily focus initiatives (with boost details)
python manage.py daily_priorities --list

# View priority summary
python manage.py daily_priorities --summary

# Manually set an initiative as top priority
python manage.py daily_priorities --set-priority <uuid> --rank=1 --reason="Critical for launch"

# Clear manual priority
python manage.py daily_priorities --clear-priority <uuid>

# Scan with different focus count
python manage.py daily_priorities --scan --focus-count=10
```

**Code Reference:**
```python
from core.services.daily_priorities import (
    run_daily_priority_scan,
    get_daily_focus_initiatives,
    set_manual_priority,
    is_daily_focus
)

# Run daily scan (marks top 5 as focus)
result = run_daily_priority_scan(focus_count=5)
print(f"Top {result['focus_count']} focus initiatives identified")

# Get current focus list
focus = get_daily_focus_initiatives()
for init in focus:
    print(f"{init['name']}: {init['final_score']:.2f}")
    print(f"  Boosts: {init['factors']}")

# Check if specific initiative is in focus
if is_daily_focus(initiative_id):
    print("This initiative is in today's focus")

# Manual priority override
set_manual_priority(initiative_id, priority_rank=1, reason="Customer deadline")
```

**Model Fields (Initiative):**
| Field | Type | Description |
|-------|------|-------------|
| `is_daily_focus` | Boolean | Is this in today's daily focus? |
| `daily_focus_date` | Date | When marked as daily focus |
| `manual_priority_rank` | Integer | Manual rank override (1-5) |
| `manual_priority_reason` | Text | Reason for manual override |

---

### Boardroom Approval (Session 914.6)

Institutional-track initiatives require explicit Boardroom approval before auto-progression can continue. This is now tracked separately from founder intent.

**Previous Behavior (Bug):** `founder_intent_set` was incorrectly used as a proxy for boardroom approval.

**New Behavior:** Boardroom approval is tracked independently with its own fields and approval workflow.

**When Required:**
- Initiatives on the `institutional` execution track
- Initiatives with content flags (external_data, user_data, public_publishing, etc.)
- Initiatives explicitly marked as `requires_boardroom_approval=True`

**Management Commands:**
```bash
# List initiatives pending boardroom approval
python manage.py boardroom_approval --list-pending

# Show approval status for an initiative
python manage.py boardroom_approval --status <uuid>

# Approve an initiative
python manage.py boardroom_approval --approve <uuid> --by="founder" --notes="Reviewed and approved"

# Revoke approval
python manage.py boardroom_approval --revoke <uuid> --reason="Needs re-review"

# Bulk approve all initiatives with founder intent set
python manage.py boardroom_approval --auto-approve-with-intent

# Dry run (show what would be approved)
python manage.py boardroom_approval --auto-approve-with-intent --dry-run
```

**Code Reference:**
```python
from core.models_document_registry import Initiative

# Approve an initiative
initiative.approve_in_boardroom(approved_by='founder', notes='Reviewed')

# Check approval status
status = initiative.boardroom_approval_summary
# Returns: {'required': True, 'approved': True, 'approved_at': ..., 'status': 'approved'}

# Revoke if needed
initiative.revoke_boardroom_approval(reason='Needs re-review')

# Check if can progress
if initiative.can_auto_progress:
    print("Ready for auto-progression")
else:
    print(f"Blocked: {initiative.progression_blocked_reason}")
```

**Model Fields (Initiative):**
| Field | Type | Description |
|-------|------|-------------|
| `boardroom_approved` | Boolean | Has this been approved by the Boardroom? |
| `boardroom_approved_at` | DateTime | When approval was granted |
| `boardroom_approved_by` | String | Who approved in the Boardroom |
| `boardroom_approval_notes` | Text | Notes or conditions from approval |

---

### Operating Rhythm (Session 914.7)

With 180+ initiatives, agents treat all equally. The Operating Rhythm provides a simple daily/weekly cadence for founder control:

**Daily:**
- Founder sets Top 3 priorities
- Agents must map initiatives to one of those priorities
- Unmapped initiatives = auto-defer

**Weekly:**
- System produces "Ship / Learn / Kill" report
- Founder gives one paragraph of feedback
- Feedback becomes training signal

**Management Commands:**
```bash
# Set today's top 3 priorities
python manage.py operating_rhythm --set-priorities "Priority 1" "Priority 2" "Priority 3"

# View current rhythm status
python manage.py operating_rhythm --status

# Generate weekly Ship/Learn/Kill report
python manage.py operating_rhythm --weekly-report

# Submit weekly feedback (becomes training signal)
python manage.py operating_rhythm --feedback "Focus on user-facing features, fewer infrastructure changes"

# Map an initiative to a priority
python manage.py operating_rhythm --map-initiative <uuid> --priority=1

# View feedback history
python manage.py operating_rhythm --history
```

**Code Reference:**
```python
from core.services.operating_rhythm import (
    set_daily_priorities,
    get_daily_priorities,
    generate_weekly_report,
    submit_weekly_feedback,
    map_initiative_to_priority,
    get_rhythm_status
)

# Set today's priorities
set_daily_priorities([
    "Launch podcast feature",
    "Fix authentication bugs",
    "Improve content quality"
])

# Get weekly report
report = generate_weekly_report()
print(report['shipped'], report['learned'], report['kill_candidates'])

# Submit feedback
submit_weekly_feedback("Focus on user-facing features this week")

# Map initiative to priority #1
map_initiative_to_priority(initiative_id, priority_index=0)
```

**Weekly Report Sections:**
| Section | Description |
|---------|-------------|
| `shipped` | Initiatives that progressed stages this week |
| `learned` | Experiment learnings from this week |
| `blocked` | Initiatives stuck at same stage for >3 days |
| `kill_candidates` | Low-priority initiatives with no progress in 14+ days |
| `needs_decision` | Initiatives awaiting founder input |

**Model: FounderFeedback** (`core/models_unified_system.py`)
| Field | Type | Description |
|-------|------|-------------|
| `feedback_type` | String | `daily_priorities`, `weekly_feedback`, `initiative_feedback`, `agent_feedback` |
| `content` | JSON | Feedback content (priorities, text, etc.) |
| `created_by` | String | Who submitted the feedback |
| `processed_as_learning` | Boolean | Has this been converted to agent learning? |

---

### Auto-Progression (Session 906)

The system automatically advances initiatives through stages based on document quality. Runs every 10 minutes via Celery Beat.

**Prerequisites (Session 914 - 914.7):**
- Daily rate limit not exceeded (default: 40/day)
- Founder intent must be set (for Stage 2+)
- Execution track limits respected (Fast Track stops at Stage 2)
- Institutional track requires stage approvals (Stages 2-4)
- Semantic drift check passed (document aligns with initiative intent)
- Boardroom approval granted (if required for institutional track)
- Daily focus initiatives can be prioritized for progression
- Initiative mapped to daily priority (or auto-deferred via operating rhythm)

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

### Document Generation (Updated Session 1021)

Stage documents are generated by `TechnicalDocumentAgent` with real system data:

```python
# core/tasks.py - advance_initiative_pipeline
# Session 1021: Only process current stage, gather real data first

# 1. Only process init.current_stage (never scan ahead)
stage_num = init.current_stage

# 2. Verify prior stage is APPROVED
if stage_num > 1:
    prior = InitiativeStage.objects.filter(initiative=init, stage=stage_num - 1).first()
    if not prior or prior.status != 'APPROVED':
        continue  # Skip — prior stage not done

# 3. Gather REAL system data
research_context = _gather_initiative_research(init, stage_num)
# Queries: SpiderData, SignalClusters, AgentConversations, Deliverables
# Returns formatted string with real data for the agent

# 4. Generate document with real data context
agent = TechnicalDocumentAgent()
result = agent.execute(
    task=f"Create a formal {stage_name} document...\n\nREAL DATA:\n{research_context}",
    context={
        'topic': init.name,           # Session 1021: was missing before
        'research_context': research_context,  # Session 1021: real data
        ...
    }
)

# 5. Create SelfBlog and link
blog = SelfBlog.objects.create(
    title=f"[Stage {stage.stage}] {initiative.name}",
    full_text=content,
)
stage.document = blog
stage.status = 'DRAFT'
```

**`_gather_initiative_research()` data sources:**
| Source | Query | Max Results |
|--------|-------|-------------|
| SpiderData | `embedding_text__icontains` keyword search, last 14 days | 5 |
| SignalClusters | `name__icontains` keyword search, last 14 days | 3 |
| AgentConversations | `topic__icontains` keyword search, last 14 days | 3 |
| Deliverables | Existing deliverables for the initiative | 3 |

Keywords extracted from initiative name (words > 3 chars, stop words excluded, max 6).

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

### Management Commands

```bash
# ===== Session 914: Founder Intent =====
# List initiatives awaiting founder intent
python manage.py set_founder_intent --list

# Set intent for specific initiative
python manage.py set_founder_intent --initiative-id=<uuid> --speed=balanced --risk=medium

# Set intent for all pending initiatives at Stage 2+
python manage.py set_founder_intent --all-pending --speed=fast

# Interactive mode - review each initiative
python manage.py set_founder_intent --interactive

# ===== Session 913: Signal Intelligence =====
# Backfill initiative signal links
python manage.py backfill_initiative_signals --dry-run
python manage.py backfill_initiative_signals --fix --limit=200

# ===== Session 906: Title & Duplicate Cleanup =====
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

# Fix stuck initiative documents
python manage.py fix_stuck_initiatives --dry-run
python manage.py fix_stuck_initiatives --fix
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
| 913 | Signal Intelligence linking - Initiative FK to SignalCluster/AutoTopic |
| **914** | **Founder Intent** - execution_speed, risk_tolerance, stop_rule, budget controls |
| **914.2** | **Execution Tracks** - Fast Track (Stage 1-2) vs Institutional (Full 5-stage), content flag auto-detection, stage approvals |
| **914.3** | **Semantic Quality Gates** - Drift detection using embeddings, blocks progression if document diverges from initiative intent |
| **914.4** | **Rate Limits** - Daily progression limit (40/day default), controls LLM spend, admin reset/override |
| **914.5** | **Daily Priorities** - Daily priority scan identifies top 5 focus initiatives, scoring by stage/freshness/speed/track/intent |
| **914.6** | **Boardroom Approval** - Proper tracking of boardroom approval separate from founder intent, fixes bypass issue |
| **914.7** | **Operating Rhythm** - Daily Top 3 priorities + Weekly Ship/Learn/Kill reports, founder feedback becomes training signal |
| 1018 | Initiative fast-track stall fix - auto-created initiatives use `balanced` speed instead of `fast` |
| 1020 | Stage 2 document creation, initiative dedup (6 paths), circuit breaker on all paths, temporal awareness |
| **1021** | **Pipeline Integrity** - DRAFT stage approval, no stage skip-ahead, real data gathering via `_gather_initiative_research()` |

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

### Stages Not Advancing (Session 914 - 1021)
1. **Check founder intent** - `python manage.py set_founder_intent --list`
2. **Check execution track** - Fast Track stops at Stage 2
3. **Check execution speed** - Must be `balanced` (not `fast`) for 5-stage flow (Session 1018)
4. **Check stage approvals** - Institutional requires approvals for Stages 2-4
5. **Check semantic drift** - `python manage.py check_initiative_drift --initiative-id=<uuid>`
6. If drift detected, override with: `--override --reason="Explanation"`
7. **Check rate limit** - `python manage.py initiative_rate_limit --status`
8. **Check daily focus** - `python manage.py daily_priorities --list` to see focused initiatives
9. **Check boardroom approval** - `python manage.py boardroom_approval --status <uuid>`
10. If pending, approve with: `python manage.py boardroom_approval --approve <uuid>`
11. **Check operating rhythm** - `python manage.py operating_rhythm --status` to see daily priorities
12. Map initiative to priority: `python manage.py operating_rhythm --map-initiative <uuid> --priority=1`
13. Verify stage status is `APPROVED` (DRAFT stages with docs are now auto-approved, Session 1021)
14. Check `advance_initiative_pipeline` task is scheduled
15. **Check prior stage approved** — pipeline only processes `current_stage` when prior is `APPROVED` (Session 1021)

### Stage Documents Contain Garbage
1. **Verify `_gather_initiative_research()` found data** — check logs for `[Initiative research]` entries
2. If no data found: initiative keywords may not match any SpiderData/SignalClusters in last 14 days
3. `TechnicalDocumentAgent` has NO tools — it can only work with data you provide in the prompt
4. Documents stating "No data available" are correct behavior when no matching system data exists

### Deliverable Not Created
1. Verify all 5 stages are `APPROVED`
2. Check `is_complete()` returns True
3. Look for errors in `create_final_deliverable()`

---

*Documentation created by Claude Code - Session 871*
