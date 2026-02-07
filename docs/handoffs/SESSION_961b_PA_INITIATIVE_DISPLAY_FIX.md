# Session 961b: PA Initiative Display Fix

**Date:** February 7, 2026
**Status:** Complete
**Branch:** main

---

## Problem Statement

When the user asks the PA about initiatives (e.g., "Audit all initiatives"), the response was triple-capped:

1. **tool_dispatcher.py** - `limit = payload.get('limit', 10)` fetched only 10 from DB
2. **unified_pa_entrypoint.py** - `for item in items[:7]` showed only 7 in response
3. **unified_pa_entrypoint.py** - `name[:40]` truncated initiative names to unreadable stubs

Additionally, the `count` in the response only reflected the post-limit count, not the total matching initiatives - so the PA couldn't tell the user "showing 10 of 169".

---

## What Was Changed

### 1. tool_dispatcher.py - `_handle_initiative()` list action

| Change | Before | After |
|--------|--------|-------|
| Default limit | 10 | 50 |
| Total count | Not tracked | `total_count = qs.count()` before slice |
| Response | `count` only | `count` + `total_count` |

### 2. unified_pa_entrypoint.py - Initiative list formatter

| Change | Before | After |
|--------|--------|-------|
| Display limit | 7 items | 25 items |
| Name truncation | `[:40]` | `[:80]` |
| Header | "Found 10 initiatives:" | "Found 169 initiatives (showing 50):" |
| Activity | Not shown | "no activity" for null `last_activity_at` |
| Action text | "action items" | "actions" (compact) |

---

## Files Modified

| File | Lines Changed |
|------|--------------|
| `core/services/tool_dispatcher.py` | 1896, 1923, 1948 |
| `core/services/unified_pa_entrypoint.py` | 1586-1621 |

---

## Testing

- 16/16 PA tests pass
- 6 voice test failures are pre-existing (unrelated `OpenAI` mock issue)
- No initiative-specific tests exist (no test changes needed)
