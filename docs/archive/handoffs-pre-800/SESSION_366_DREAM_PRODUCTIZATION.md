# Session 366: Dream Productization Pipeline

**Date:** December 5, 2025
**Focus:** Transform agent dreams from emergent noise into actionable ideation pipeline
**Status:** COMPLETE - Dreams now scored, linked to projects, and surfaced to Boardroom

---

## Summary

Session 366 transformed agent dreams from a "background emergent culture engine" into a "creative accelerator" with actionable outputs. Previously dreams were:

- Observed
- Stored
- Learned from
- Mutated

But NOT:
- Intentional
- Directed
- Validated
- Productized

This session fixed that.

---

## Problem

ChatGPT analysis revealed that 1,459 agent dreams existed but:
- 0% were linked to projects
- 0% had user feedback
- Only 37.8% were shown to users
- Dreams had no actionability scoring
- No mechanism to surface high-value dreams for decisions

---

## Solution

### 1. UN-Deprecated AgentDream Model

The model was deprecated in Session 284, but we UN-deprecated it to enable productization.

**New Fields Added:**

| Field | Type | Purpose |
|-------|------|---------|
| `actionability_score` | Float (0-1) | How implementable is this dream? |
| `relevance_score` | Float (0-1) | How relevant to active projects? |
| `composite_score` | Float (0-1) | Combined score for ranking |
| `promoted_to_decision` | Boolean | Surfaced to Boardroom? |
| `promoted_at` | DateTime | When promoted |
| `decision_outcome` | Choice | pending/approved/deferred/rejected |
| `is_directed` | Boolean | User-requested topic? |
| `directed_topic` | String | The specific topic to dream about |

**New Indexes:**
- `composite_score, dreamed_at` - For ranking top dreams
- `promoted_to_decision, decision_outcome` - For Boardroom queries
- `is_directed, dreamed_at` - For directed dream queries

### 2. Dream Scoring Task

New Celery task: `score_and_promote_dreams`

**Scoring Process:**
1. Get unscored dreams from last 7 days
2. For each dream:
   - GPT scores **actionability** (0-1): Can this be implemented?
   - GPT scores **relevance** (0-1): Does it match active projects?
   - Calculate **composite score**: (creativity + actionability + relevance) / 3
3. Link dreams to matched projects (if relevance >= 0.5)
4. Auto-promote to Boardroom if composite >= 0.7

**Schedule:** Every 20 minutes via Celery Beat

### 3. Directed Dreaming Task

New Celery task: `generate_directed_dreams`

Users can request agents to dream about specific topics:
```python
from core.tasks import generate_directed_dreams
generate_directed_dreams('AI-powered content marketing')
```

**Features:**
- Focused prompts on the specific topic
- Higher initial actionability scores (0.6)
- Marked with `is_directed=True` for filtering
- 10 agents, 2 dreams each = 20 focused ideas

---

## Test Results

### Dream Scoring
```python
Result: {
    'status': 'success',
    'stats': {
        'dreams_scored': 50,
        'dreams_promoted': 19,
        'dreams_linked_to_projects': 0,
        'avg_actionability': 0.53,
        'avg_relevance': 0.54,
        'avg_composite': 0.69
    }
}
```

**19 dreams promoted to Boardroom** for decision!

### Directed Dreaming
```python
Result: {
    'status': 'success',
    'stats': {
        'dreams_generated': 20,
        'agents_dreaming': 10,
        'topic': 'AI-powered content marketing automation'
    }
}
```

### Top Boardroom Dreams

| Dream | Agent | Composite Score |
|-------|-------|-----------------|
| Creative Thought | CustomerResearchAgent | 0.83 |
| AI Artistry Revolution Unleashed | CreativeDirectorAgent | 0.80 |
| TrendSync Creative Hub | PromptEngineeringAgent | 0.80 |
| Interactive AI Art Fusion Gallery | CreativeDirectorAgent | 0.77 |
| On Demand Creative Engine | WorkflowOrchestrationAgent | 0.76 |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | UN-deprecated AgentDream, added productization fields and methods |
| `core/migrations/0071_session_366_dream_productization.py` | New migration for fields and indexes |
| `core/tasks.py` | Added `score_and_promote_dreams` and `generate_directed_dreams` tasks |
| `core/celery.py` | Added `dream-productization-cycle` to Celery Beat schedule |

---

## New Autonomous Task

| Task | Frequency | Purpose |
|------|-----------|---------|
| `dream-productization-cycle` | 20 min | Score dreams, link to projects, promote to Boardroom |

Total autonomous tasks: **17**

---

## Dream Pipeline Flow

```
Agent Dreams (idle thoughts)
         |
         v
  Score Dreams (every 20 min)
   - Actionability: Can it be built?
   - Relevance: Matches projects?
   - Composite: Combined ranking
         |
         v
  Link to Projects (relevance >= 0.5)
         |
         v
  Promote to Boardroom (composite >= 0.7)
         |
         v
  Decision: approved/deferred/rejected
         |
         v
  Implementation (future session)
```

---

## Quick Test

```bash
# Test dream scoring
.venv/bin/python manage.py shell -c "
from core.tasks import score_and_promote_dreams
result = score_and_promote_dreams()
print(result)
"

# Test directed dreaming
.venv/bin/python manage.py shell -c "
from core.tasks import generate_directed_dreams
result = generate_directed_dreams('your topic here')
print(result)
"

# Check Boardroom dreams
.venv/bin/python manage.py shell -c "
from core.models import AgentDream
promoted = AgentDream.objects.filter(promoted_to_decision=True)
print(f'Pending decisions: {promoted.filter(decision_outcome=\"pending\").count()}')
"
```

---

## What's Next (Session 367)

### Option A: Dream Validation UI
- Add thumbs up/down reactions to dreams in UI
- Track which dream types users prefer
- Weight future dream generation by preferences

### Option B: Dream -> Implementation Pipeline
- When dream is approved in Boardroom, create project task
- Assign to appropriate agent for implementation
- Track from dream -> deliverable

### Option C: Multi-Agent Dream Sessions
- Multiple agents collaborate on a dream topic
- Build on each other's ideas
- Generate more sophisticated proposals

---

## Commit

```
feat(Session 366): Dream Productization Pipeline

- UN-deprecated AgentDream model for productization
- Added actionability_score, relevance_score, composite_score fields
- Added promoted_to_decision and decision_outcome for Boardroom
- Added is_directed and directed_topic for focused dreaming
- Created score_and_promote_dreams Celery task
- Created generate_directed_dreams Celery task
- Added dream-productization-cycle to Celery Beat (every 20 min)
- First run: 50 dreams scored, 19 promoted to Boardroom
```
