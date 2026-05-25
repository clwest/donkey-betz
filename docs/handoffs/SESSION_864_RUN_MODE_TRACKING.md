---
originating_session: 864
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 864: Content Intelligence + Run Mode Tracking

**Date:** January 28, 2026
**Status:** COMPLETE
**Previous:** Session 863 (ConceptForge - Autonomous Think Tank Pipeline)

---

## Overview

This session had two major parts:

1. **Content Intelligence Improvements** - Refined PublishGate thresholds and added EditorAgent
2. **Run Mode Tracking** - Implemented 3-phase system to separate warmup exercises from production work

---

## Part 1: Content Intelligence Improvements

After running `apply_publish_gate --all --dry-run` on production, we identified three key issues:

| Metric | Before | After |
|--------|--------|-------|
| **Publish Ready** | 7 (2%) | Expected ~50+ |
| **Needs Enhancement** | 264 (73%) | Reduced (structure threshold lowered) |
| **Internal Only** | 92 (25%) | Increased (operational titles auto-classified) |

---

## Improvements Implemented

### 1. Auto-Classify Operational Titles

Content with operational title patterns now bypasses quality checks and goes directly to `internal_only`.

**Patterns Added:**
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

**Behavior:**
- Checks title at the START of `evaluate()` method
- Returns `internal_only` immediately with scores = 0.0
- Suggested category = `internal_note`
- Skips quality, novelty, structure scoring entirely

### 2. Lower Structure Threshold

Reduced `STRUCTURE_THRESHOLD` from 0.65 to 0.55 to catch more legitimate content.

**Rationale:** Most content was failing on structure (0.40-0.50) while passing quality (0.80+) and novelty (0.60+). The 0.65 threshold was too aggressive.

**Location:** `core/services/publish_gate.py:44`

```python
STRUCTURE_THRESHOLD = 0.55  # Session 864: Lowered from 0.65
```

### 3. EditorAgent for Auto-Enhancement

Created a new agent to automatically improve content structure for content marked as `needs_enhancement`.

**Location:** `core/agents/editor_agent.py`

**Enhancement Strategies:**
| Strategy | Description |
|----------|-------------|
| `hooks` | Add compelling opening questions, statistics, bold statements |
| `headers` | Make section headers action-oriented and varied |
| `engagement` | Add questions, stats, quotes, callouts |
| `structure` | Balance section lengths, improve transitions |
| `conclusion` | Create memorable, actionable endings |

**Usage:**
```python
from core.agents.editor_agent import EditorAgent, enhance_blog

# Single blog
result = enhance_blog(blog_id='uuid', save=True)

# All needing enhancement
from core.agents.editor_agent import enhance_all_needing_enhancement
results = enhance_all_needing_enhancement(limit=10, save=True)
```

**Celery Tasks:**
```python
# Single blog
enhance_blog_task.delay(blog_id='uuid', save=True)

# Batch processing
enhance_all_blogs_task.delay(limit=10, save=True)
```

---

## Files Created/Modified

### Created
| File | Purpose |
|------|---------|
| `core/agents/editor_agent.py` | New agent for content structure enhancement |

### Modified
| File | Changes |
|------|---------|
| `core/services/publish_gate.py` | Added operational title patterns, lowered structure threshold |
| `core/agents/__init__.py` | Added EditorAgent export |
| `core/tasks.py` | Added enhance_blog_task, enhance_all_blogs_task |

---

## Testing

### Test Operational Title Detection
```python
from core.services.publish_gate import PublishGate

gate = PublishGate()

# Should return True
assert gate._is_operational_title("[Research] Some topic") == True
assert gate._is_operational_title("[Stage 1 - Research Brief] Something") == True
assert gate._is_operational_title("[Report] System Insights") == True

# Should return False
assert gate._is_operational_title("How to Build AI Systems") == False
```

### Test EditorAgent
```python
from core.agents.editor_agent import EditorAgent

agent = EditorAgent()
result = agent.execute(
    task="Enhance blog",
    context={
        'content': {
            'title': 'Test Title',
            'intro': 'Some intro text...',
            'sections': [
                {'header': 'Section 1', 'content': 'Content here...'},
            ],
            'conclusion': 'Some conclusion...',
        },
        'focus_areas': ['hooks', 'headers'],
    },
    scifi_context={},
    spider_context={},
)
print(result.data['enhanced_content'])
```

### Run in Production
```bash
# Re-evaluate with new rules (dry run first!)
railway run python manage.py apply_publish_gate --all --dry-run

# Apply changes
railway run python manage.py apply_publish_gate --all

# Test enhancement
railway run python -c "
from core.tasks import enhance_all_blogs_task
enhance_all_blogs_task.delay(limit=5, save=False)
"
```

---

## Expected Impact

After these changes:

| Metric | Before | Expected After |
|--------|--------|----------------|
| Publish Ready | 7 (2%) | ~50+ (15%+) |
| Needs Enhancement | 264 (73%) | ~150 (40%) - reduced due to lower threshold |
| Internal Only | 92 (25%) | ~160 (45%) - increased due to operational title detection |

The EditorAgent can then process the "Needs Enhancement" queue to improve content structure automatically.

---

## Next Steps

### P1: Run in Production
1. Apply PublishGate with new rules
2. Check new distribution of decisions
3. Run batch enhancement on a few blogs

### P2: Celery Beat Scheduling
Add enhancement task to periodic schedule:
```python
'enhance-content-daily': {
    'task': 'core.tasks.enhance_all_blogs_task',
    'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    'kwargs': {'limit': 20, 'save': True},
},
```

### P3: UI Integration
- Add "Enhance" button on blog cards with status='needs_enhancement'
- Show enhancement progress/results
- Allow manual focus area selection

---

---

## Part 2: Run Mode Tracking (Warmup vs Production)

### Problem
The Operations Tab was showing generic agent-generated content like "Python utility functions" because `exercise_all_dormant_agents` was generating real content using default topics.

### Root Cause
`universal_agent_workspace_output()` was called for both:
1. Real production work (user requests, initiatives, dreams)
2. Exercise/warmup runs (health checks for dormant agents)

Both paths created real files and database records, polluting the workspace.

### Solution: 3-Phase Implementation

#### Phase 0: Signal Classification
Added run mode tracking to `WorkspaceOperation` model:

```python
# core/models_skin_layer.py
RUN_MODE_CHOICES = [
    ('production', 'Production'),
    ('warmup', 'Warmup/Exercise'),
]

TRIGGER_SOURCE_CHOICES = [
    ('initiative', 'Initiative Stage'),
    ('user', 'User Request'),
    ('dream', 'Dream Execution'),
    ('schedule', 'Scheduled Task'),
    ('warmup', 'Warmup/Exercise'),
    ('self_healing', 'Self-Healing'),
    ('conceptforge', 'ConceptForge'),
    ('unknown', 'Unknown'),
]

run_mode = models.CharField(...)       # production or warmup
trigger_source = models.CharField(...) # what triggered execution
initiative_id = models.UUIDField(...)  # FK to initiative
is_warmup = models.BooleanField(...)   # quick filter flag
```

**Migration:** `0207_session_864_run_mode_tracking.py`

#### Phase 1: Infra-Only Warmup
Rewrote `exercise_all_dormant_agents()` to use `_run_agent_warmup()`:

```python
def _run_agent_warmup(agent_name: str) -> dict:
    """Verify agent works WITHOUT content generation."""
    # 1. Verify agent class exists
    # 2. Verify agent can be instantiated
    # 3. Check required methods (execute, tools)
    # NO file creation, NO LLM calls
    return {
        'success': True,
        'agent': agent_name,
        'run_mode': 'warmup',
        'file_created': False,  # Key difference
    }
```

#### Phase 2: Initiative Queue
Added `_get_next_task_for_agent()` to pull real work:

```python
def _get_next_task_for_agent(agent_name: str) -> Optional[dict]:
    """Check for pending initiative work for this agent."""
    pending = InitiativeStage.objects.filter(
        assigned_agent=agent_name,
        status='pending',
    ).order_by('created_at').first()

    if pending:
        return {
            'initiative_id': str(pending.initiative_id),
            'stage_number': pending.stage_number,
            'topic': pending.description,
            'trigger_source': 'initiative',
        }
    return None
```

#### Phase 3: Quality Gate
Updated `universal_agent_workspace_output()` with intent-based routing:

```python
# PRODUCTION: Full execution with file output
if run_mode == 'production':
    result = agent.execute(task=topic, ...)
    _save_to_workspace(result)
    _create_operation_record(run_mode='production', ...)

# WARMUP: Telemetry only, quarantine to .warmups/
if run_mode == 'warmup':
    result = _run_agent_warmup(agent_name)
    _save_warmup_telemetry(result)
    # NO workspace files created
```

### API Changes

Operations endpoint now filters out warmups by default:

```python
# core/views_workspace_api.py
def get_queryset(self):
    queryset = WorkspaceOperation.objects.all()

    # Session 864: Exclude warmups by default
    include_warmups = self.request.query_params.get('include_warmups', 'false')
    if include_warmups.lower() != 'true':
        queryset = queryset.filter(is_warmup=False)

    # Filter by run_mode if specified
    run_mode = self.request.query_params.get('run_mode')
    if run_mode:
        queryset = queryset.filter(run_mode=run_mode)
```

**Usage:**
- `GET /api/workspace/operations/` - Production operations only (default)
- `GET /api/workspace/operations/?include_warmups=true` - All operations
- `GET /api/workspace/operations/?run_mode=warmup` - Warmup only

### Files Modified

| File | Changes |
|------|---------|
| `core/models_skin_layer.py` | Added run_mode, trigger_source, initiative_id, is_warmup fields + indexes |
| `core/tasks.py` | Rewrote universal_agent_workspace_output, added _run_agent_warmup, _get_next_task_for_agent |
| `core/views_workspace_api.py` | Added warmup filtering to Operations endpoint |
| `.gitignore` | Added `.warmups/` quarantine directory |

### Result

| Behavior | Before | After |
|----------|--------|-------|
| Exercise runs | Generated real content with default topics | Infra check only, no files |
| Operations Tab | Mixed production + warmup noise | Clean production-only view |
| Initiative queue | Unused | Agents pull real tasks first |
| Warmup tracking | No distinction | Full metadata + filtering |

---

## Agent Count Update

| Type | Count |
|------|-------|
| **Agents** | 75 (+1 EditorAgent) |
| **Celery Tasks** | 240 (+2) |
| **Database Models** | 378+ (WorkspaceOperation updated) |
