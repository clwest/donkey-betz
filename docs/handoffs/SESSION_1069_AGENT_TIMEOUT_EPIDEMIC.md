---
originating_session: 1069
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1069: Agent Timeout Epidemic Fix

**Date:** 2026-02-23
**PRs:** #1436, #1438

## What Was Done

### PA-Driven Deep Dive (continued from Session 1068)

Queried Railway PA for detailed failure analysis across 7 days:

#### Agent Timeout Breakdown (190 total in 7 days)
- TrendAnalysisAgent: 36 timeouts (28.1% failure rate)
- ContentWriterAgent: 34 timeouts (12.0%)
- WorkflowAgent: 20 timeouts (41.7%)
- CompetitorAnalysisAgent: 15 (3.2%)
- BearCaseAgent: 8 (21.1%)
- 15+ other agents with smaller counts

#### Celery Task Failures (170 total in 7 days)
- `generate_initiative_stage_document`: **157 failures** (92% of all Celery failures)
- Various other tasks: 13 combined

#### Root Cause Analysis
1. **Context gathering cascade**: 11 sequential `_get_*_context` calls in `AgentRouter.route()`, each can hang 30s+ = 5+ minutes just for context
2. **WorkflowAgent wall clock**: 45-minute limit with 5 iteration rounds; each delegation triggers full context gathering for the sub-agent
3. **Stage document tasks**: No time limit at all, agents run indefinitely until 45-minute cleanup kills them. With `max_retries=2`, each failure retries twice = 157 failures from ~52 unique tasks

## Fixes — PR #1436

### 1. Parallel Context Gathering in AgentRouter

**Root cause:** 11 context-gathering calls executed sequentially. Any single slow call (DB timeout, Redis hang, external API) blocked all subsequent calls. Cumulative risk: 11 × 30s = 5.5 minutes.

**Fix:** Replaced sequential calls with `ThreadPoolExecutor` parallel execution:
- All 11 context methods run simultaneously in separate threads
- 10-second per-call timeout — any call exceeding 10s returns `{}`
- `_safe_ctx` wrapper handles Django DB connection cleanup per thread
- Total context gathering: max ~10s (was potentially 5+ minutes)
- Failed/timed-out contexts gracefully degrade to empty dict

### 2. WorkflowAgent Iteration + Wall Clock Reduction

**Root cause:** 5 iteration rounds × multi-agent delegations × full context gathering per delegation = easily exceeded 45-minute cleanup threshold.

**Fix:**
- Max iterations: 5 → 3 (most workflows complete in 2-3 steps)
- Wall clock: 45 min → 10 min (matches Celery time limits)
- Fewer iterations + faster context = fewer timeout kills

### 3. Stage Document Task Time Limits

**Root cause:** `generate_initiative_stage_document` had NO `soft_time_limit` or `time_limit`. Tasks routed to agents that ran indefinitely, killed by 45-min cleanup, then retried twice. 157 failures in 7 days.

**Fix:**
- Added `soft_time_limit=600, time_limit=660` (10 min)
- `SoftTimeLimitExceeded` handler resets stage to PENDING with timeout note
- Reduced `max_retries` from 2 to 1 (if it times out, retrying usually also times out)

## Files Changed

| File | Change |
|------|--------|
| `core/agent_router.py` | Parallelized 11 context-gathering calls with ThreadPoolExecutor + 10s timeout |
| `core/agents/workflow_agent.py` | Reduced iterations 5→3, wall clock 45min→10min |
| `core/tasks.py` | Added time limits + SoftTimeLimitExceeded handler to stage doc task, max_retries 2→1 |

## Fixes — PR #1438

### 4. VideoAgent Input Validation

**Root cause:** `RunwayMLProvider.text_to_video()` and `image_to_video()` had no input validation — invalid model names, durations, and ratios were passed directly to the Runway ML API, causing HTTP 400 errors.

**Fixes:**
- Added model name whitelist validation (invalid → default to `veo3.1_fast`/`gen4_turbo`)
- Added duration range validation (invalid → default to 4s/5s)
- Added ratio whitelist validation (invalid → default to `1920:1080`/`1280:720`)
- Log full HTTP response body on non-200 errors for debugging
- Fixed bare `except` in `_prepare_image` — now raises `ValueError` with details
- Fixed localhost URL fallthrough bug — reject early with clear error message

### 5. Redis-Resilient Legal Agent Dispatch

**Root cause:** `_handle_legal_agent` called `draft_legal_document_task.delay()` without try/except. When Redis broker was temporarily unreachable, the exception crashed the PA tool handler.

**Fix:** Wrapped `.delay()` with try/except — returns meaningful error message instead of crashing.

## Files Changed

| File | Change |
|------|--------|
| `core/agent_router.py` | Parallelized 11 context-gathering calls with ThreadPoolExecutor + 10s timeout |
| `core/agents/workflow_agent.py` | Reduced iterations 5→3, wall clock 45min→10min |
| `core/tasks.py` | Added time limits + SoftTimeLimitExceeded handler to stage doc task, max_retries 2→1 |
| `content/video_provider.py` | Input validation for model/duration/ratio, error logging, _prepare_image fixes |
| `core/services/tool_dispatcher.py` | Try/except around legal agent Celery dispatch |

## Expected Impact

| Metric | Before | Expected After |
|--------|--------|----------------|
| Agent timeouts/7d | 190 | <30 (context gathering no longer cascades) |
| Stage doc failures/7d | 157 | <10 (10-min limit prevents indefinite runs) |
| WorkflowAgent failure rate | 41.7% | <15% (fewer iterations + faster context) |
| Context gathering time | Up to 5+ min | Max 10 seconds |
