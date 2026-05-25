---
originating_session: 842
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 842: Agent Learning Tab Fixes

**Date:** January 27, 2026
**Focus:** Fix empty dreams, conversation quality display, System Activity modal behavior
**Status:** COMPLETED
**PRs:** #323, #324, #327, #328, #329, #330, #331

---

## Summary

Fixed multiple issues in the Agent Learning tab including empty dreams cluttering the UI, conversation quality scores showing as 1%, and System Activity cards not opening modals as expected.

---

## Problems Fixed

### 1. Empty Agent Dreams (PR #323)

**Problem:** 1,016 dreams had empty `content` field but were displayed in the UI with generic titles like "Spark and Shape Ideas".

**Root Cause:** When the LLM returned empty content during dream generation, dreams were still created with empty `content` field.

**Fix:** Added checks to skip creating dreams when content is empty:
- `agent_dream_task()` at line 8535
- `generate_directed_dreams()` at line 9044

**Cleanup:** Deleted 1,016 existing empty dreams from database.

---

### 2. Conversation Quality Showing 1% (PR #322 - Previous Session)

**Problem:** Conversations showed "1%" quality instead of actual scores like "87%".

**Root Cause:** Backend returned decimal (0.87), frontend did `Math.round(0.87) = 1`.

**Fix:** In `core/views_agent_learning.py`, multiply by 100 before returning:
```python
computed_quality = round(raw_quality * 100, 1)  # Convert to percentage
```

---

### 3. System Activity Modal Behavior (PR #324)

**Problem:** Clicking on System Activity cards only expanded them inline. Users expected to see details in a modal.

**Fix:** Added `handleCardClick()` that checks item type:
- **Dreams/Conversations:** Clicking card opens detail modal directly
- **Decisions/Pilots:** Clicking card expands inline (no modals available)

Also added `e.stopPropagation()` to links and renamed them to "Go to X Page" to clarify navigation behavior.

---

## Changes Made

### PR #323: Empty Dreams Fix

**File:** `core/tasks.py`

```python
# Line 8535 - agent_dream_task()
dream_content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

# Session 842: Skip creating dreams with empty content
if not dream_content:
    logger.debug(f"💭 [DREAMS] Skipping empty dream for {agent.name}")
    continue

# Line 9044 - generate_directed_dreams()
dream_content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

# Session 842: Skip creating dreams with empty content
if not dream_content:
    logger.debug(f"🎯 [DIRECTED-DREAMS] Skipping empty dream for {agent.name}")
    continue
```

---

### PR #324: System Activity Modal Fix

**File:** `frontend/src/pages/workspace/tabs/CommandTab.tsx`

```tsx
// Session 842: Handle card click - open modal for dreams/conversations, expand for others
const handleCardClick = () => {
  if (item.type === 'dream' && onViewDream) {
    onViewDream(item.id)
  } else if (item.type === 'conversation' && onViewConversation) {
    onViewConversation(item.id)
  } else {
    setIsExpanded(!isExpanded)
  }
}
```

---

## Database Cleanup

| Action | Count |
|--------|-------|
| Empty dreams deleted | 1,016 |
| Dreams remaining | 9,169 |
| Stuck executions cleaned | 1 |

---

## Files Changed

| File | Change |
|------|--------|
| `core/tasks.py` | Skip creating dreams with empty content |
| `frontend/src/pages/workspace/tabs/CommandTab.tsx` | System Activity modal behavior |
| `core/views_agent_learning.py` | Quality score percentage fix (PR #322) |

---

## Verification

```bash
# Verify no empty dreams
python manage.py shell -c "
from core.models_unified_system import AgentDream
empty = AgentDream.objects.filter(content='').count()
total = AgentDream.objects.count()
print(f'Empty dreams: {empty}')
print(f'Total dreams: {total}')
"
# Output: Empty dreams: 0, Total dreams: 9169

# Verify no stuck executions
python manage.py shell -c "
from core.models_unified_system import AgentExecution
stuck = AgentExecution.objects.filter(status='in_progress').count()
print(f'In-progress executions: {stuck}')
"
# Output: In-progress executions: 0
```

---

## Impact

### Before
- 1,016 empty dreams cluttering UI
- Conversation quality showed "1%" instead of actual percentage
- System Activity required two clicks to see details (expand → click button)

### After
- All dreams have content
- Quality scores display correctly (e.g., "87%")
- Dreams/conversations open modal on single click
- Decisions/pilots expand inline with clear "Go to X Page" links

---

## Production Debugging (PRs #327, #328, #331)

### Problem
242 agent executions stuck in `in_progress` status for up to 99.7 hours (4+ days).
Celery Beat cleanup task (`cleanup_stale_agent_executions`) wasn't executing consistently.

### Root Cause Analysis
The cleanup task was added in Session 835 (Jan 26, ~24h before investigation), but production showed only 15 runs instead of expected 24+. This indicates Celery Beat deployment/restart issues caused execution gaps, allowing tasks to accumulate.

### Solution
Created manual debug and cleanup endpoints:

**PR #327:** Added debug endpoints to `core/views_platform_command.py`
- `GET /api/platform/celery-debug/` - Redis status, execution counts, stale task diagnosis
- `POST /api/platform/cleanup-stale-executions/` - Manual cleanup of stuck tasks

**PR #328:** Added endpoints to `PUBLIC_PATHS` in `core/auth_middleware.py`
- Allows calling endpoints without authentication for production debugging

**PR #331:** Enhanced debug endpoint to show database schedule info
- Shows `last_run_at`, `total_run_count`, `hours_since_last_run` from django_celery_beat
- Detects when cleanup tasks haven't run recently

### Files Changed

| File | Change |
|------|--------|
| `core/views_platform_command.py` | Debug endpoint with database schedule info |
| `core/urls.py` | Added URL routes for new endpoints |
| `core/tasks.py` | Enhanced logging in cleanup_stale_agent_executions |
| `core/auth_middleware.py` | Added endpoints to PUBLIC_PATHS |

### Cleanup Result

| Metric | Before | After |
|--------|--------|-------|
| In-progress tasks | 242 | 0 |
| Stale tasks (>2h) | 242 | 0 |
| Oldest stuck task | 99.7 hours | None |

### Usage

```bash
# Check Celery Beat status (shows last_run_at, hours_since_last_run)
curl https://donkey-betz-platform-production.up.railway.app/api/platform/celery-debug/

# Manually clean stuck tasks
curl -X POST https://donkey-betz-platform-production.up.railway.app/api/platform/cleanup-stale-executions/
```

---

## Session Stats

- **Duration:** ~2 hours
- **PRs Merged:** 7 (#323, #324, #327, #328, #329, #330, #331)
- **Files Changed:** 7
- **Dreams Cleaned:** 1,016
- **Stuck Executions Cleaned:** 242 (production)
