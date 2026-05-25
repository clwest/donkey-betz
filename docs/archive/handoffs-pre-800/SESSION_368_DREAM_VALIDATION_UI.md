# Session 368: Dream Validation UI + Agent Execution Engine

**Date:** December 5, 2025
**Focus:** Add validation UI APIs + Agent Execution Engine for real deliverables
**Status:** COMPLETE - Full dream lifecycle from approval to validated deliverables

---

## Summary

Session 368 added the API layer for dream validation UI. Users can now:

1. View promoted dreams in the Boardroom
2. Make decisions on dreams (approve/defer/reject)
3. View dream implementations and their status
4. Rate dreams with thumbs up/down
5. Validate/reject completed implementations with quality ratings
6. Track agent performance metrics

---

## Problem

After Session 367, dreams could be:
- Approved in the Boardroom
- Assigned to agents for implementation
- Tracked with status (pending -> in_progress)

But there was no API to:
- List Boardroom dreams separately from all dreams
- Make decisions on dreams via API
- View implementation list with status
- Rate dreams quickly (thumbs up/down)
- Validate completed implementations
- Track agent performance metrics

---

## Solution

### New API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/boardroom/dreams/` | GET | Get promoted dreams pending decision |
| `/api/boardroom/dreams/{id}/decide/` | POST | Approve/defer/reject a dream |
| `/api/dream-implementations/` | GET | List all implementations with status |
| `/api/dream-implementations/{id}/validate/` | POST | Validate or reject an implementation |
| `/api/dream-implementations/metrics/` | GET | Get validation metrics per agent |
| `/api/agent-dreams/{id}/rate/` | POST | Quick thumbs up/down rating |

### Endpoint Details

#### GET /api/boardroom/dreams/

Get dreams promoted to the Boardroom for decision.

**Query params:**
- `limit`: Max dreams to return (default 20)
- `status`: Filter by decision_outcome (pending/approved/deferred/rejected)
- `min_score`: Minimum composite score (default 0)

**Response:**
```json
{
  "success": true,
  "dreams": [
    {
      "id": "uuid",
      "title": "Dream Title",
      "content": "Dream content...",
      "dream_type": "creative_idea",
      "agent_name": "CreativeDirectorAgent",
      "composite_score": 0.83,
      "decision_outcome": "pending",
      "has_implementation": false
    }
  ],
  "status_counts": {
    "pending": 16,
    "approved": 4,
    "deferred": 0,
    "rejected": 0
  }
}
```

#### POST /api/boardroom/dreams/{id}/decide/

Make a decision on a promoted dream.

**Body:**
```json
{
  "decision": "approved|deferred|rejected",
  "notes": "optional notes"
}
```

#### GET /api/dream-implementations/

Get implementation status and details.

**Query params:**
- `limit`: Max implementations (default 20)
- `status`: Filter by status (pending/assigned/in_progress/completed/validated/rejected)
- `agent_id`: Filter by assigned agent

**Response:**
```json
{
  "success": true,
  "implementations": [
    {
      "id": "uuid",
      "dream_title": "Interactive AI Art Fusion Gallery",
      "assigned_agent_name": "CreativeDirectorAgent",
      "status": "validated",
      "status_display": "User Validated",
      "implementation_plan": "1. Design...",
      "quality_rating": 0.85,
      "user_feedback": "Great work!"
    }
  ],
  "status_counts": {
    "pending": 0,
    "assigned": 0,
    "in_progress": 3,
    "completed": 0,
    "validated": 1,
    "rejected": 0
  }
}
```

#### POST /api/dream-implementations/{id}/validate/

Validate or reject a completed implementation.

**Body:**
```json
{
  "action": "validate|reject",
  "rating": 0.85,
  "feedback": "Great execution!"
}
```

#### GET /api/dream-implementations/metrics/

Get validation metrics per agent.

**Response:**
```json
{
  "success": true,
  "agent_metrics": [
    {
      "agent_name": "CreativeDirectorAgent",
      "total_implementations": 3,
      "validated": 1,
      "rejected": 0,
      "in_progress": 2,
      "success_rate": 1.0,
      "avg_quality_rating": 0.85
    }
  ],
  "overall": {
    "total_implementations": 4,
    "validated": 1,
    "rejected": 0,
    "avg_quality_rating": 0.85
  }
}
```

#### POST /api/agent-dreams/{id}/rate/

Quick thumbs up/down rating for dreams.

**Body:**
```json
{
  "rating": "up|down"
}
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/views_agent_learning.py` | Added 6 new API endpoints (lines 1247-1675) |
| `core/urls.py` | Added endpoint imports and URL patterns |

---

## Test Results

### Validation Flow Test

```python
# 1. Approve a pending dream
dream.record_decision('approved', 'Testing validation flow')
# ✅ Dream approved!

# 2. Process approved dreams -> Create implementation
process_approved_dreams()
# ✅ 1 implementation created

# 3. Complete implementation
impl.complete_implementation(
    deliverable_type='document',
    deliverable_path='/docs/plan.md',
    summary='Implementation plan document'
)
# ✅ Status: completed

# 4. Validate implementation
impl.validate(rating=0.85, feedback='Great execution!')
# ✅ Status: validated, Rating: 0.85
```

### Current Stats

| Metric | Value |
|--------|-------|
| Promoted Dreams | 19 |
| Pending Decisions | 14 |
| Approved Dreams | 5 |
| Implementations | 4 |
| Validated | 1 |
| In Progress | 3 |

---

## Complete Dream Pipeline

```
[GENERATE] agent_dream_cycle (15 min)
     |
     v
[SCORE] dream_productization_cycle (20 min)
     |
     v
[PROMOTE] Auto-promote if composite >= 0.7
     |
     v
[BOARDROOM] GET /api/boardroom/dreams/
     |
     v
[DECIDE] POST /api/boardroom/dreams/{id}/decide/  <-- NEW!
     |
     v
[IMPLEMENT] dream_implementation_cycle (15 min)
     |
     v
[TRACK] GET /api/dream-implementations/  <-- NEW!
     |
     v
[VALIDATE] POST /api/dream-implementations/{id}/validate/  <-- NEW!
     |
     v
[METRICS] GET /api/dream-implementations/metrics/  <-- NEW!
```

---

## Agent Execution Engine (Part 2)

### New Task: execute_dream_implementations

The execution engine takes in-progress implementations and generates real deliverables:

| Implementation Type | Deliverable | Description |
|---------------------|-------------|-------------|
| feature/improvement | specification | Feature specification with requirements, timeline, risks |
| content | content_strategy | Content calendar, audience targeting, distribution plan |
| research | research_report | Full research report with findings and recommendations |
| experiment | experiment_report | Hypothesis, methodology, simulated findings |
| other | document | Generic implementation document |

### Celery Beat Schedule

Added `dream-execution-cycle`:
- **Frequency:** Every 20 minutes
- **Task:** `core.tasks.execute_dream_implementations`
- **Purpose:** Execute in-progress implementations and generate deliverables

**Total autonomous tasks: 19** (was 18)

---

## Test Results

### Execution Engine Test

```python
Result: {
    'status': 'success',
    'stats': {
        'executed': 3,
        'completed': 3,
        'deliverables_generated': 3,
        'failed': 0,
        'deliverable_types': {
            'experiment_report': 1,
            'research_report': 1,
            'specification': 1
        }
    }
}
```

### Implementation Status After Execution

| Status | Deliverable Type | Dream Title |
|--------|------------------|-------------|
| validated | document | Interactive AI Art Fusion Gallery |
| completed | specification | TrendSync Creative Hub |
| completed | research_report | AI Artistry Revolution Unleashed |
| completed | experiment_report | Creative Thought |

---

## Frontend: Thumbs Up/Down Reactions

Added thumbs down button to dream cards:
- 👍 (up) - More dreams like this
- 👎 (down) - Fewer dreams like this

Uses new `/api/agent-dreams/{id}/rate/` endpoint.

Files modified:
- `ai_core/templates/partials/js/agent_dashboard.html`
- `ai_core/templates/ai_image_studio.html`

---

## GPT-5-mini Migration (Part 4)

Updated all `gpt-4o-mini` references in `core/tasks.py` to use `gpt-5-mini` with proper parameters for reasoning models:

| Task/Function | Changes |
|--------------|---------|
| `score_and_promote_dreams` (actionability) | `gpt-5-mini`, `max_completion_tokens=50` |
| `score_and_promote_dreams` (relevance) | `gpt-5-mini`, `max_completion_tokens=100` |
| `generate_directed_dreams` (content) | `gpt-5-mini`, `max_completion_tokens=500` |
| `generate_directed_dreams` (title) | `gpt-5-mini`, `max_completion_tokens=50` |
| `process_approved_dreams` | `gpt-5-mini`, `max_completion_tokens=800` |
| `_execute_feature_implementation` | `gpt-5-mini`, `max_completion_tokens=2500` |
| `_execute_content_implementation` | `gpt-5-mini`, `max_completion_tokens=2500` |
| `_execute_research_implementation` | `gpt-5-mini`, `max_completion_tokens=2500` |
| `_execute_experiment_implementation` | `gpt-5-mini`, `max_completion_tokens=2500` |
| `_execute_generic_implementation` | `gpt-5-mini`, `max_completion_tokens=2500` |

**Key changes for reasoning models:**
- Changed `max_tokens` → `max_completion_tokens`
- Removed `temperature` parameter (not supported)
- Increased token limits to account for internal reasoning + output

---

## What's Next (Session 369)

### Option A: Frontend UI Integration
- Show implementations in a dedicated UI panel
- View deliverable content inline
- Validation modal for completed implementations

### Option B: Image/Video Generation
- Connect execution engine to ImageAgent
- Generate actual images for visual implementations
- Store real media files

### Option C: Multi-Agent Dream Sessions
- Multiple agents collaborate on a dream topic
- Build on each other's ideas
- Generate more sophisticated proposals

---

## Quick Test

```bash
# Test boardroom dreams endpoint
curl http://localhost:8000/api/boardroom/dreams/

# Test implementations endpoint
curl http://localhost:8000/api/dream-implementations/

# Test metrics endpoint
curl http://localhost:8000/api/dream-implementations/metrics/

# Run execution engine manually
.venv/bin/python manage.py shell -c "
from core.tasks import execute_dream_implementations
result = execute_dream_implementations()
print(result)
"
```

---

## Commits

```
feat(Session 368): Dream Validation UI API + Agent Execution Engine

Part 1 - Dream Validation UI API:
- Added GET /api/boardroom/dreams/ for promoted dreams
- Added POST /api/boardroom/dreams/{id}/decide/ for decisions
- Added GET /api/dream-implementations/ for implementation list
- Added POST /api/dream-implementations/{id}/validate/ for validation
- Added GET /api/dream-implementations/metrics/ for agent metrics
- Added POST /api/agent-dreams/{id}/rate/ for thumbs up/down

Part 2 - Agent Execution Engine:
- Added execute_dream_implementations Celery task
- Generates deliverables based on implementation type
- Types: specification, content_strategy, research_report, experiment_report
- Added dream-execution-cycle to Celery Beat (every 20 min)
- First run: 3 implementations completed with real deliverables

Part 3 - Frontend Thumbs Up/Down:
- Added 👎 thumbs down button to dream cards
- rateDream() function for quick feedback

Autonomous tasks: 18 -> 19
```
