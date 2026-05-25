---
originating_session: 968
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 968 — Review Insight De-dup / Bundling + Frontend Data Plumbing

**Date:** February 7, 2026
**PRs:** #970 (frontend data plumbing), remarkGfm fix, Phase 5A insight bundling (pending)
**Status:** COMPLETE

---

## What Was Done

### 1. Frontend Data Plumbing Audit + Unwired Visibility Layer (PR #970)
- Audit of frontend components for data connectivity
- Added unwired visibility layer for data flow inspection

### 2. remarkGfm Import Fix
- Fixed missing `remarkGfm` import in `ContentStudioTab`
- Commit: `72e802b5`

### 3. Phase 5A — Review Insight De-dup / Bundling
When the Content Deliberation Pipeline runs a review conversation, `ConversationOrchestrator.create_conversation_memories()` creates one `AgentMemory(memory_type='insight')` per participant agent. For a 2-agent review (EditorAgent + ContentStrategyAgent), that produces 2 near-identical insight memories sharing the same `source_id` (conversation UUID). In Memory Palace, users saw N duplicate cards.

**Solution:** Bundle by `source_id` — no migration, no new model fields.

#### Backend Changes (`core/views_memory_palace.py`, +3 lines)
- `get_agent_memories()`: Added `source_id` to serialization
- `list_all_memories()`: Added `source_id` and `tags` to serialization

#### Frontend Changes (`frontend/src/pages/MemoryPalacePage.tsx`, ~75 lines)
- Added `source_id` to `Memory` interface
- `bundleInsights()` utility: groups insight memories by `source_id`, singletons pass through
- `InsightBundleCard` component: collapsed shows representative title + "N agents" badge + max importance; expanded shows individual `MemoryCard` per agent
- Render loop branches between `InsightBundleCard` and `MemoryCard` via `isBundle()` type guard

---

## Files Modified

| File | Change |
|------|--------|
| `core/views_memory_palace.py` | Added `source_id` to 2 serializers |
| `frontend/src/pages/MemoryPalacePage.tsx` | Bundling logic + InsightBundleCard component |

## Key Decisions
- **No migration needed** — `source_id` already exists on `AgentMemory`, just wasn't exposed in list APIs
- **No tag manipulation** — bundling is purely a frontend display concern
- **Chronological sort preserved** — bundles sort by representative's `created_at`

## Testing
- Frontend build passes cleanly (no TS errors)
- Bundle display: insight memories from same conversation → single expandable card
- Solo insights (single-agent) render as normal cards
- All existing memory features unaffected
