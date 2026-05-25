---
subsystems: [celery, personal-assistant]
decision_types: [performance, bug_fix]
status: active
originating_session: 1056
---

# Session 1056 — Railway Cost Throttle + PA Degenerate Loop Fix

**Date:** February 20, 2026

## 1. Railway Cost Reduction — Beat Schedule Throttling (PR #1356)

Railway compute hit $1,200/month (bumped to $1,500). 21 high-frequency Celery beat tasks were generating ~1,470 invocations/hour — all DB/Redis-only monitoring with no LLM spend.

### Changes (core/celery.py only)

| Category | Tasks | Old Interval | New Interval |
|----------|-------|-------------|--------------|
| Body Systems | 9 (heartbeat, circulatory, spine, immune, digestive, muscular, brain, skin, nervous) | 30-90s | 120-300s |
| Broadcast/Dashboard | 6 (learning, conversation, relationship, evolution, dream-journal, system-state-cache) | 60-180s | 120-600s |
| Event Bus/Infra | 5 (realtime-scoring, event-bus-scoring, event-bus-validation, event-bus-analytics, celery-health) | 30-120s | 60-300s |
| 3D Model Polling | 1 | 30s | 60s |

**NOT changed:** `body-coordinator-check` (60s) — gates LLM throttle mode.

All `expires` values set 10s below schedule interval to prevent task stacking.

**Impact:** ~21,000 fewer invocations/day (~59% reduction for these 21 tasks).

## 2. PA Degenerate Text Loop Fix (PR #1357)

GPT-5.2 occasionally generates filler text about wanting to call a tool ("Ok.Ok.Let's call.Ok.Ok.") instead of emitting actual function calls.

### Root Cause

`_run_agentic_loop()` (unified_pa_entrypoint.py) had a degenerate content detector (Session 1043), but it only ran when tool calls were present. The no-tool-calls early return at line 690 bypassed the check entirely, displaying garbage to the user.

### Fixes

1. **Added degenerate check in no-tool-calls path** — returns friendly error message instead of garbage
2. **Added Pattern 4 to `_is_degenerate_content()`** — detects high "Ok." density (>=8 occurrences)

### Files Changed

| File | Change |
|------|--------|
| `core/services/unified_pa_entrypoint.py` | Degenerate check in no-tool-calls path + Pattern 4 |
