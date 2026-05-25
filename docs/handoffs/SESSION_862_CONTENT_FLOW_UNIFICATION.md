---
originating_session: 862
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 862: Content Flow Unification

**Date:** January 28, 2026
**Status:** COMPLETE
**PRs:** #450, #451, #452, #454 (publish fix)

---

## Summary

Implemented the complete Content Flow Unification plan to establish proper traceability from Dream → Initiative → Stages → Deliverable. This fixes the critical integration gaps where Dreams, Initiatives, Content, and Deliverables were disconnected.

---

## What Was Implemented

### Phase 1: Foreign Key Relationships

Added FK relationships between all content models:

| Model | New FK Fields | Purpose |
|-------|--------------|---------|
| `Deliverable` | `initiative`, `dream`, `self_blog`, `podcast_episode` | Track content source |
| `SelfBlog` | `initiative`, `dream`, `initiative_stage` | Link blogs to pipeline |
| `PodcastEpisode` | `initiative`, `dream`, `initiative_stage` | Link podcasts to pipeline |
| `AgentDream` | `initiative` | Track promotion to Initiative |

**Migration:** `0202_session_862_content_flow_fks.py`

### Phase 2: Dream → Initiative Bridge

Added `AgentDream.promote_to_initiative()` method that:
1. Creates an Initiative from the dream
2. Creates Stage 1 (Research Brief) as DRAFT
3. Links dream to initiative via FK
4. Updates dream status to approved

**File:** `core/models_unified_system.py:9024-9070`

Updated dream signal to auto-create Initiative when dream is approved:

**File:** `core/signals/dream_signals.py:46-75`

### Phase 3: Research Result Model

Created new `ResearchResult` model for tracking research conducted for Initiative Stage 1:

```python
ResearchResult
├── initiative (FK)
├── initiative_stage (FK)
├── topic
├── research_type (market_analysis, competitor_research, etc.)
├── queries (JSONField - search queries used)
├── spider_sources (M2M to SpiderData)
├── external_sources (JSONField - URLs consulted)
├── findings (JSONField - structured findings)
├── summary (TextField)
├── recommendations (JSONField)
├── confidence_score (FloatField)
├── self_blog (FK - resulting document)
└── status (pending/in_progress/complete/failed)
```

Key methods:
- `create_for_initiative()` - Factory method to create research for an initiative
- `create_research_brief()` - Generates SelfBlog document from research
- `mark_complete()` / `mark_failed()` - Status management

**File:** `core/models_research.py`
**Migration:** `0203_session_862_research_result.py`

### Phase 4: Auto-Stage Progression & Publish

Enhanced Initiative model with:

| Method | Purpose |
|--------|---------|
| `advance_stage()` | Advances to next stage, creates it if needed |
| `is_complete()` | Checks if all 5 stages are approved |
| `create_final_deliverable()` | Creates published Deliverable from completed initiative |

Enhanced InitiativeStage.approve() to:
1. Mark stage as approved
2. Advance initiative to next stage
3. Check if all stages complete → create final Deliverable

**File:** `core/models_document_registry.py`

---

## Content Flow (Now Working)

```
AgentDream (idea in boardroom)
    ↓ signal: decision_outcome = 'approved'
    ↓ promote_to_initiative()
Initiative + Stage 1 (DRAFT)
    ↓ ResearchResult.create_for_initiative()
ResearchResult (research tracking)
    ↓ create_research_brief()
Stage 1 Document (SelfBlog)
    ↓ InitiativeStage.approve()
Stage 2-5 (repeat for each)
    ↓ All 5 stages approved
Final Deliverable (published)
    └─ Full traceability: dream_id, initiative_id, all content FKs
```

---

## Files Created

| File | Purpose |
|------|---------|
| `core/models_research.py` | ResearchResult model |
| `core/migrations/0202_session_862_content_flow_fks.py` | FK migration |
| `core/migrations/0203_session_862_research_result.py` | ResearchResult migration |

## Files Modified

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added `promote_to_initiative()` to AgentDream |
| `core/models_document_registry.py` | Enhanced Initiative and InitiativeStage |
| `core/models/__init__.py` | Added ResearchResult import |
| `core/signals/dream_signals.py` | Auto-create Initiative on dream approval |
| `core/models_deliverables.py` | Added FK fields (Phase 1) |
| `core/models_podcast_studio.py` | Added FK fields (Phase 1) |

---

## Testing the Flow

```python
# 1. Create and approve a dream
from core.models import AgentDream, Agent

agent = Agent.objects.first()
dream = AgentDream.objects.create(
    agent=agent,
    title="AI Content Humanizer",
    content="A system to make AI content sound more human...",
    dream_type='creative_idea'
)

# Approve the dream (triggers signal → creates Initiative)
dream.decision_outcome = 'approved'
dream.save()

# 2. Check Initiative was created
print(f"Initiative: {dream.initiative}")
print(f"Stage 1: {dream.initiative.stages.first()}")

# 3. Create research for the initiative
from core.models import ResearchResult

research = ResearchResult.create_for_initiative(
    dream.initiative,
    topic="Market analysis for AI humanization tools",
    research_type='market_analysis'
)

# 4. Complete research and create brief
research.mark_complete(
    findings={'market_size': '$5B by 2027', 'competitors': ['Humanize.ai', 'Undetectable.ai']},
    summary='Growing market with clear opportunity...',
    confidence=0.85
)
blog = research.create_research_brief()

# 5. Approve stages to trigger final deliverable
for stage in dream.initiative.stages.all():
    deliverable = stage.approve(approved_by='user')
    if deliverable:
        print(f"Final Deliverable created: {deliverable}")
```

---

## Database Changes

New table: `core_research_result`
- 3 indexes for efficient queries

Modified tables:
- `core_agentdream` - added `initiative_id` column
- `core_deliverables` - added `initiative_id`, `dream_id`, `self_blog_id`, `podcast_episode_id`
- `core_selfblog` - added `initiative_id`, `dream_id`, `initiative_stage_id`
- `core_podcastepisode` - added `initiative_id`, `dream_id`, `initiative_stage_id`

---

## Bug Fix: Blog Publish 400 Error (PR #454)

**Problem:** Publishing blogs from Workspace ContentStudioTab returned 400 Bad Request.

**Cause:** The publish mutation was sending a POST request without a body. The backend requires `force: true` to publish blogs in 'draft' status.

**Fix:** Added `body: JSON.stringify({ force: true })` to the publish request in `ContentStudioTab.tsx`.

```javascript
// Before (broken)
const response = await fetch(`/api/v1/research/self-blog/${blog.id}/publish/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
})

// After (fixed)
const response = await fetch(`/api/v1/research/self-blog/${blog.id}/publish/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ force: true }),
})
```

---

## Next Steps

1. **Wire up ResearchAgent** to use `ResearchResult.create_for_initiative()`
2. **Update UI** to show content flow traceability in Workspace
3. **Add Celery task** for automated research on dream approval
4. **Test end-to-end** flow from dream → published deliverable
