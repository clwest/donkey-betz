# Session 887: Operations Tab Fix

**Date:** January 31, 2026
**Status:** Complete

## Problem Statement

The Operations Tab hadn't updated since January 29th (2 days). Despite:
- Celery workers showing online (4 workers, 6 active tasks)
- Tasks being triggered successfully (returning task_ids)
- Blogs being created (same `content` queue working)

The workspace-writing tasks (`agent_daily_summary`, `agent_workspace_status_report`, `agent_research_to_workspace`, `agent_content_to_workspace`) weren't creating WorkspaceOperation entries.

---

## Root Cause Analysis

The helper function `_get_workspace_for_skin_layer()` in `core/tasks.py` queries for workspaces in this order:

```python
# 1. Try codebase workspace first
workspace = ProjectWorkspace.objects.filter(
    workspace_type='codebase',
    is_active=True,
    allow_file_write=True
).first()

# 2. Try any active workspace that allows writes
workspace = ProjectWorkspace.objects.filter(
    is_active=True,
    allow_file_write=True  # <-- Problem here
).first()
```

**The production workspace had:**
- `workspace_type='git_remote'` (not `codebase`)
- `allow_file_write=None` (not `True`)

Both queries failed because `allow_file_write=None` doesn't match `allow_file_write=True`.

---

## Fix Applied

Updated the production workspace via PATCH request:

```bash
curl -X PATCH -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw '{"allow_file_write":true}' \
  "https://donkey-betz-platform-production.up.railway.app/api/workspaces/4728ea99-d6ca-4e7c-80d9-33e0696e91bf/"
```

**No code changes required** - this was a production database configuration issue.

---

## Verification

After the fix, triggered all operations tasks:

```bash
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw '{"task":"all"}' \
  "https://donkey-betz-platform-production.up.railway.app/api/workspace-triggers/trigger-operations/"
```

**Result:** 4 new operations created:
| Time | Agent |
|------|-------|
| 14:30:53 | ResearchAgent |
| 14:30:39 | ContentWriterAgent |
| 14:30:37 | DailySummaryTask |
| 14:29:43 | SystemIntelligenceAgent |

Operations Tab is now working and will continue to update automatically via Celery Beat.

---

## Scheduled Tasks (Working)

| Task | Schedule | Queue |
|------|----------|-------|
| `agent_daily_summary` | Daily at 12:30 AM | content |
| `agent_workspace_status_report` | Every 8 hours at :00 | content |
| `agent_research_to_workspace` | Every 4 hours at :45 | content |
| `agent_content_to_workspace` | Every 6 hours at :15 | content |

---

## Files Referenced (Not Modified)

| File | Purpose |
|------|---------|
| `core/tasks.py` | Contains `_get_workspace_for_skin_layer()` helper |
| `core/models_skin_layer.py` | ProjectWorkspace model with `allow_file_write` field |
| `core/views_workspace_triggers.py` | Manual trigger endpoint for debugging |

---

## Lessons Learned

1. The `allow_file_write` field defaulted to `True` in the model but was `None` on the production workspace (created before the field was added or migrated incorrectly)
2. Always verify that existing records have correct values after adding new fields with defaults
3. The manual trigger endpoint (`/api/workspace-triggers/trigger-operations/`) was essential for debugging

---

## Part 2: System Status Report Output Fix

### Problem
SystemIntelligenceAgent status reports were only showing JSON counts:
```json
{"items_count": 11, "warning_count": 1, "info_count": 10, "execution_time": 32.566}
```
Instead of the full LLM-generated report text.

### Root Cause
The `_extract_agent_output_content()` function in `core/tasks.py` was falling back to JSON serialization of `data` instead of using `result.message` when data only contained metadata counts.

### Fix Applied (PR #613)
Added `METADATA_ONLY_KEYS` detection to prefer `result.message` when data only contains counts:

```python
METADATA_ONLY_KEYS = {
    'items_count', 'critical_count', 'warning_count', 'info_count',
    'execution_time', 'count', 'total', 'success_count', 'error_count',
    'processed', 'skipped', 'duration', 'elapsed', 'timestamp'
}

# If data only contains metadata keys AND message is substantial, use message
if data_keys.issubset(METADATA_ONLY_KEYS):
    if hasattr(result, 'message') and result.message and len(result.message) > 100:
        return result.message
```

### Current System Warning

Found via `/api/assistant/attention-items/`:
- **WARNING**: 54 stale agent suggestions (over 7 days old)
  - Action: Archive or reject outdated suggestions
- **5 INFO**: Boardroom items awaiting review

---

**Operations Tab is now live. Status reports will now include full content.**
