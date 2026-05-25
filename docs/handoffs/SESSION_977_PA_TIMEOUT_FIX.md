---
originating_session: 977
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 977 — PA Production Timeout Fix

**Date:** February 9, 2026
**Previous Session:** 976 (SKIN Layer Gitignore Fix)
**Branch:** `main`

---

## Problem

PA tool-routed queries (initiatives, system health, errors, blogs) timed out at 280s on Railway production. The "hello" direct-response path worked in ~3s but anything routing through tools hung indefinitely.

### Root Causes (2 layers)

**Layer 1 — Queue starvation (PRs #1016-1017):**
PA tasks sat PENDING behind spider/initiative tasks because all `celery-worker` threads were saturated. Fixed by adding dedicated `pa` queue routing in `CELERY_TASK_ROUTES` and `celery-pa` Procfile entry.

**Layer 2 — async_to_sync deadlock (PRs #1018-1019):**
`async_to_sync(pa.process_message)` deadlocked in Celery's `--pool=threads` worker. Fixed by replacing with `asyncio.new_event_loop()` + `loop.run_until_complete()`.

**Layer 3 — Pipeline stalls (PR #1020):**
Even after fixing queue and async issues, tool-routed queries still took 260s+ because:
- `_enrich_tool_result()` ran up to 6 enrichment services **sequentially** (~60-90s total)
- `_generate_response_from_tool()` called GPT-5.1 with `task_type="analysis"` (medium reasoning effort) and `max_tokens=8000` (~120-170s)
- Combined: 180-260s, killed at `soft_time_limit=280`

---

## Solution (PR #1020)

Added timeouts and reduced LLM parameters in `core/services/unified_pa_entrypoint.py`:

1. **15s enrichment timeout** — `asyncio.wait_for()` around `_enrich_tool_result()`; if enrichment is slow, proceed without it
2. **60s LLM timeout** — `asyncio.wait_for()` around both LLM calls in `_generate_response_from_tool()`
3. **Reduced reasoning effort** — Changed enriched analysis from `task_type="analysis"` (medium reasoning) to `"conversation"` (low reasoning). Structured data is already computed; LLM just summarizes.
4. **Reduced token limits** — Enriched analysis: 8000→4000; fallback: 4000→2000
5. **Step-level timing logs** — Added timing for context build, tool dispatch, enrichment, and LLM generation

### Graceful Degradation

If enrichment times out → structured output + LLM analysis (without enrichment context)
If LLM times out → structured output only (still useful data with IDs)

---

## Changes

### Files Modified (1)

| File | Changes |
|------|---------|
| `core/services/unified_pa_entrypoint.py` | 15s enrichment timeout, 60s LLM timeout, task_type "analysis"→"conversation", max_tokens 8000→4000/4000→2000, step-level timing logs |

### Prior PRs in This Session

| PR | Change |
|----|--------|
| #1016 | Added `pa` queue to `CELERY_TASK_ROUTES` in settings.py + `celery-pa` worker in Procfile |
| #1017 | Added `pa` to `celery-worker` queue list as fallback for Railway |
| #1018 | Replaced `async_to_sync` with `asyncio.run()` in `process_pa_chat_task` |
| #1019 | Replaced `asyncio.run()` with `new_event_loop()` + `run_until_complete()` |
| #1020 | Enrichment timeout + LLM guardrails + step-level timing |

---

## Production Verification

| Query | Intent | Before | After |
|-------|--------|--------|-------|
| "hello" | general (direct) | 3s | **3.0s** |
| "any errors recently?" | error_summary | 280s+ timeout | **3.4s** |
| "how is the system doing?" | system_health_check | 280s+ timeout | **12.7s** |
| "how is everything?" | system_overview | 280s+ timeout | **18.2s** |
| "what blogs have been published?" | content_review | 280s+ timeout | **46.6s** |
| "show me my initiatives" | initiatives | 280s+ timeout | **64.0s** |

All queries complete successfully. The slowest (initiatives, 213 items) finishes in 64s.

---

## Technical Details

### Why "hello" Was Always Fast

The direct response path skips tool dispatch, enrichment, and analytical LLM calls entirely:
```
_build_context() → _generate_direct_response()
  └─ task_type="conversation" (low reasoning), max_tokens=2000
```

### Why Tool-Routed Was Slow

```
_build_context() → tool_dispatcher.execute() → _enrich_tool_result() → _generate_response_from_tool()
  sequential: 6 enrichment services            └─ task_type="analysis" (medium reasoning)
  each via asyncio.to_thread()                    max_tokens=8000
  total: ~60-90s                                  total: ~120-170s
```

### After Fix

```
_build_context() → tool_dispatcher.execute() → _enrich_tool_result() → _generate_response_from_tool()
  (same)           (30s timeout)                 (15s timeout cap)       (60s timeout cap)
                                                                         task_type="conversation"
                                                                         max_tokens=4000
```

No migrations needed.
