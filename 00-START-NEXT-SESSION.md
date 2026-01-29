# Session 865 - Start Here

**Previous Session:** 864 (Content Intelligence + Run Mode Tracking)
**Date:** January 28, 2026
**Status:** 75 Agents (+1 EditorAgent) | 77 Spiders | 25 Advisors | 139 Personas | 240 Celery Tasks (+2) | **Run Mode Tracking: COMPLETE** | **Content Intelligence: IMPROVED** | **ConceptForge: COMPLETE** | **Data Persistence: COMPLETE**

---

## What Was Accomplished in Session 864

**Handoff:** `docs/handoffs/SESSION_864_RUN_MODE_TRACKING.md`

### Part 1: Content Intelligence Layer Improvements

After analyzing production data from `apply_publish_gate --all --dry-run`, we identified and fixed three issues affecting content classification accuracy.

### Production Data Before

| Metric | Count | Percentage |
|--------|-------|------------|
| Publish Ready | 7 | 2% |
| Needs Enhancement | 264 | 73% |
| Internal Only | 92 | 25% |

### Three Improvements Implemented

#### 1. Auto-Classify Operational Titles

Content with operational title patterns now bypasses quality checks and goes directly to `internal_only`.

```python
OPERATIONAL_TITLE_PATTERNS = [
    r'^\[research\]',           # [Research] ...
    r'^\[stage \d+',            # [Stage 1 - Research Brief] ...
    r'^\[report\]',             # [Report] ...
    r'^\[audit\]',              # [Audit] ...
    r'^\[internal\]',           # [Internal] ...
    r'^\[debug\]',              # [Debug] ...
    r'^\[fix\]',                # [Fix] ...
    r'^\[todo\]',               # [TODO] ...
    r'^researchagent:',         # ResearchAgent: ...
    r'^systeminsights:',        # SystemInsights: ...
    r'^root.?cause',            # Root-cause analysis...
]
```

**Location:** `core/services/publish_gate.py:55-67`

#### 2. Lower Structure Threshold

Reduced `STRUCTURE_THRESHOLD` from 0.65 to 0.55. Most content was failing on structure (0.40-0.50) while passing quality (0.80+) and novelty (0.60+).

**Location:** `core/services/publish_gate.py:44`

#### 3. EditorAgent for Auto-Enhancement

New agent that automatically improves content structure for content marked as `needs_enhancement`.

**Enhancement Strategies:**
| Strategy | Description |
|----------|-------------|
| `hooks` | Add compelling opening questions, statistics, bold statements |
| `headers` | Make section headers action-oriented and varied |
| `engagement` | Add questions, stats, quotes, callouts |
| `structure` | Balance section lengths, improve transitions |
| `conclusion` | Create memorable, actionable endings |

**Location:** `core/agents/editor_agent.py`

### Files Created/Modified

| File | Changes |
|------|---------|
| `core/services/publish_gate.py` | Operational title patterns, lowered threshold |
| `core/agents/editor_agent.py` | NEW - Content structure enhancement agent |
| `core/agents/__init__.py` | Added EditorAgent export |
| `core/tasks.py` | Added enhance_blog_task, enhance_all_blogs_task |

### New Celery Tasks

- `enhance_blog_task` - Enhance single blog by ID
- `enhance_all_blogs_task` - Batch enhance blogs marked as 'needs_enhancement'

---

### Part 2: Run Mode Tracking (Warmup vs Production)

Fixed the Operations Tab showing generic content like "Python utility functions" by implementing a 3-phase system to separate warmup exercises from production work.

**Problem:** `exercise_all_dormant_agents` was generating real content with default topics, polluting the workspace.

#### Phase 0: Signal Classification
Added fields to `WorkspaceOperation`:
- `run_mode` - 'production' or 'warmup'
- `trigger_source` - initiative, user, dream, schedule, warmup, self_healing, conceptforge
- `initiative_id` - FK to initiative
- `is_warmup` - Quick filter boolean

**Migration:** `0207_session_864_run_mode_tracking.py`

#### Phase 1: Infra-Only Warmup
`_run_agent_warmup()` verifies agent works WITHOUT content generation:
- Checks agent class exists and can be instantiated
- Verifies required methods (execute, tools)
- NO file creation, NO LLM calls

#### Phase 2: Initiative Queue
`_get_next_task_for_agent()` pulls real work from `InitiativeStage` before using default topics.

#### Phase 3: Quality Gate
Operations API filters out warmups by default:
- `GET /api/workspace/operations/` - Production only (default)
- `GET /api/workspace/operations/?include_warmups=true` - All operations
- `GET /api/workspace/operations/?run_mode=warmup` - Warmup only

### Files Modified (Run Mode)

| File | Changes |
|------|---------|
| `core/models_skin_layer.py` | Added run_mode, trigger_source, initiative_id, is_warmup fields |
| `core/tasks.py` | Rewrote universal_agent_workspace_output, added warmup helpers |
| `core/views_workspace_api.py` | Added warmup filtering to Operations endpoint |
| `.gitignore` | Added `.warmups/` quarantine directory |

---

## Priority for Session 865

### Option A: Run PublishGate with New Rules (Recommended)

Test the Session 864 improvements on production:

```bash
# Re-evaluate with new rules (dry run first!)
railway run python manage.py apply_publish_gate --all --dry-run

# Apply changes
railway run python manage.py apply_publish_gate --all

# Test enhancement on a few blogs
railway run python -c "
from core.tasks import enhance_all_blogs_task
enhance_all_blogs_task.delay(limit=5, save=False)
"
```

### Option B: Add Enhancement Celery Beat Schedule

Add enhancement task to periodic schedule:

```python
'enhance-content-daily': {
    'task': 'core.tasks.enhance_all_blogs_task',
    'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    'kwargs': {'limit': 20, 'save': True},
},
```

### Option C: ConceptForge UI Integration

Add ConceptForge dossier view to Workspace:

1. Create "Dossiers" tab matching initiative phase cards
2. Show stage tabs: Research | Debate | Feasibility | Risk | Market | Synthesis
3. Add "Promote to ConceptForge" button on blog cards

### Option D: UI for Enhancement

Add UI elements for EditorAgent:

1. "Enhance" button on blog cards with status='needs_enhancement'
2. Show enhancement progress/results
3. Allow manual focus area selection

### Option E: Apply Run Mode Migration (Required for Production)

Apply the Session 864 migration to production:

```bash
# Apply migration
railway run python manage.py migrate core 0207_session_864_run_mode_tracking

# Verify warmup filtering works
railway run python -c "
from core.models_skin_layer import WorkspaceOperation
print(f'Total operations: {WorkspaceOperation.objects.count()}')
print(f'Production: {WorkspaceOperation.objects.filter(run_mode=\"production\").count()}')
print(f'Warmup: {WorkspaceOperation.objects.filter(is_warmup=True).count()}')
"
```

---

## Quick Start

```bash
# Test ConceptForge
python manage.py shell

from core.conceptforge import ConceptForgeOrchestrator
orchestrator = ConceptForgeOrchestrator()

# Check if content qualifies
should_trigger, reason, domain = orchestrator.should_trigger(
    quality_score=0.85,
    tags=['legal', 'automation'],
)
print(f"Should trigger: {should_trigger}, Reason: {reason}, Domain: {domain}")

# Manual trigger
from core.tasks import promote_to_conceptforge
promote_to_conceptforge.delay(
    source_type='blog',
    source_id='<blog-uuid>',
    domain='legal',
)
```

---

## Session 862/864 Content Intelligence (PRODUCTION DEPLOYED)

### What Was Added (Session 862)
- **PublishGate**: Quality evaluation before publishing (quality, novelty, structure scores)
- **ContentClassifier**: Routes content to public/internal/strategic
- **SelfBlog Updates**: content_type field, new categories (build_log, internal_note, playbook, dossier)

### Improvements (Session 864)
- **Operational Title Detection**: Auto-classifies `[Research]`, `[Stage X -`, etc. as internal
- **Lowered Structure Threshold**: 0.65 → 0.55 (catches more legitimate content)
- **EditorAgent**: Automatically enhances content structure

### Test the Content Intelligence
```bash
# Evaluate a specific blog
railway run python manage.py apply_publish_gate --blog-id <uuid>

# Evaluate all blogs with new rules
railway run python manage.py apply_publish_gate --all --dry-run

# Enhance a blog
railway run python -c "from core.agents.editor_agent import enhance_blog; print(enhance_blog('<blog-id>', save=False))"
```

### Handoffs
- `docs/handoffs/SESSION_862_CONTENT_INTELLIGENCE.md`
- `docs/handoffs/SESSION_864_RUN_MODE_TRACKING.md`

---

## Recent Session History

| Session | Focus | Status |
|---------|-------|--------|
| **864** | Content Intelligence + Run Mode Tracking (warmup vs production) | ✅ COMPLETE |
| **863** | ConceptForge - Autonomous Think Tank Pipeline | ✅ COMPLETE |
| **862** | Content Intelligence - PublishGate + ContentClassifier | ✅ PRODUCTION DEPLOYED |
| **862** | Content Flow Unification - Dream → Initiative → Deliverable | ✅ COMPLETE |
| **861** | Data Persistence - 6 gap fixes + Content Tab UI | ✅ COMPLETE |
| **860** | Initiative Pipeline + API Error Handling | ✅ COMPLETE |

---

**Always read this file first - it has the current priorities!**
