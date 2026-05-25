---
originating_session: 1064
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1064: Platform Hardening

**Date:** February 22, 2026
**Focus:** Safety checks, cost protection, stability, task timeouts, telemetry cleanup
**PR:** #1419 (merged), Railway deploy `2ee4aefa` SUCCESS

## Problem

Deep research into platform autonomy revealed 11 gaps across safety, stability, and coordination. Six required immediate code fixes:

1. AI decision promoter bypassed `NEVER_AUTO_AREAS` safety check
2. LUNGS `can_breathe()` existed but was never called from the LLM path
3. Body coordinator throttle factor was computed but never read by any task dispatch
4. `CeleryTaskEvent` and `LLMCallLog` grew unboundedly with no cleanup
5. ~10 heavy long_running tasks had no `soft_time_limit`, risking indefinite blocking
6. Prediction evaluator identified retraining candidates but only logged a warning

## What Was Built

### 1. NEVER_AUTO_AREAS Safety Check (`ai_decision_promoter.py`)
- `run_batch_promotion()` now excludes decisions with `impact_area in {security, infrastructure, agents}` before AI evaluation
- Matches the rule-based promoter's existing protection

### 2. LUNGS Budget Enforcement (`llm_enforcer.py`, `settings.py`)
- `can_breathe()` wired into `enforce_real_ai()` — the single entry point for ALL LLM calls
- When budget exhausted and `LUNGS_ENFORCE_HARD_LIMIT=true`: returns structured error dict with `blocked_by_lungs=True`, `success=False`, `call_id`, `agent`
- Callers check `result['success']` and degrade gracefully
- `try/except` ensures LUNGS bugs never break LLM calls
- 3 tests in `tests/test_lungs_hard_limit.py` (hard limit blocks, disabled skips, error doesn't block)

### 3. Body Throttle Mode (`tasks.py`)
- `execute_agent_task()` reads `get_throttle_factor()` and applies proportional delay (0-30s)
- Body health tasks (`run_heartbeat`, `check_breathing`, etc.), PA chat, and gate progression are separate Celery tasks that never flow through `execute_agent_task` — naturally exempt
- Initial implementation had a dead `_THROTTLE_EXEMPT` set checking `self.name` (always `execute_agent_task`); fixed by removing it — all agent work dispatched here is deferrable

### 4. Telemetry Cleanup Tasks (`tasks.py`, `celery.py`, `settings.py`)
- `cleanup_celery_task_events`: deletes records older than `CELERY_TASK_EVENT_RETENTION_DAYS` (default 30)
- `cleanup_llm_call_logs`: deletes records older than `LLM_CALL_LOG_RETENTION_DAYS` (default 30)
- Beat schedule: weekly Sunday 4:00 AM and 4:15 AM
- Routed to `broadcast` queue

### 5. Task Timeouts (`tasks.py`)
- `soft_time_limit` added to 10 heavy long_running tasks:
  - 1800s: `run_agent_conversation`, `run_multi_agent_conversation`, `execute_dream_implementations`, `run_autonomous_thinking_cycle`, `run_all_desks_intelligence`, `run_triggered_conversation`, `process_hivemind_sessions`, `execute_approved_dreams_via_orchestration`
  - 600s: `execute_approved_artifacts`, `generate_pending_reviews`
- Explicit `SoftTimeLimitExceeded` catches on all 10 with task-specific log tags (e.g., `[HIVEMIND] process_hivemind_sessions timed out (soft_time_limit=1800s)`)
- Tasks with retries (`run_multi_agent_conversation`, `run_triggered_conversation`) catch timeout before retry logic to prevent retry storms
- `run_all_desks_intelligence` extracted to `_run_desks_inner()` helper to catch timeout at top level (inner `except Exception` blocks would otherwise swallow it)
- Note: `soft_time_limit` does NOT enforce on `--pool=threads` (Railway) — SIGUSR1 only works with prefork

### 6. Retraining Dispatch (`sports/tasks.py`)
- `evaluate_completed_predictions` now dispatches `retrain_sport_model.delay(sport)` for candidates
- Guards: dedup via `set()`, 6-hour Redis cooldown per sport (`retrain_cooldown:{sport}`), structured logging with accuracy context
- Cache backend confirmed Redis in production (settings.py:271)

### 7. SpiderData Indexes (`models_unified_system.py`)
- 3 composite indexes for common query patterns:
  - `(is_processed, created_at)` — unprocessed data queries
  - `(spider_name, created_at)` — per-spider lookups
  - `(data_type, created_at)` — type-based filtering
- Migration `0254_spiderdata_composite_indexes.py`, ~110K rows, sub-second

### 8. Beat Schedule (`celery.py`, `settings.py`)
- `daily_priority_scan` wired into beat at 6:00 AM daily, routed to `broadcast` queue (not `long_running` — avoids starvation)

## Config Knobs

All require process restart to change (read at import time via `os.environ.get()`).

| Variable | Default | Purpose |
|----------|---------|---------|
| `LUNGS_ENFORCE_HARD_LIMIT` | `true` | Block LLM calls when budget exhausted |
| `CELERY_TASK_EVENT_RETENTION_DAYS` | `30` | CeleryTaskEvent cleanup retention |
| `LLM_CALL_LOG_RETENTION_DAYS` | `30` | LLMCallLog cleanup retention |
| `BODY_THROTTLE_MAX_DELAY_SECONDS` | `30` | Max proportional delay under throttle |

## Files Changed (9)

| File | Change |
|------|--------|
| `core/services/ai_decision_promoter.py` | NEVER_AUTO_AREAS exclusion in batch promotion |
| `core/llm_enforcer.py` | LUNGS budget check + CostTracking tenant_id TODO |
| `core/tasks.py` | Body throttle, cleanup tasks, SoftTimeLimitExceeded catches (8 new), `_run_desks_inner` extraction |
| `core/settings.py` | 4 config knobs, 2 cleanup task routes, daily_priority_scan route change |
| `core/celery.py` | 3 beat schedule entries (2 cleanup + daily_priority_scan) |
| `core/models_unified_system.py` | SpiderData Meta indexes |
| `core/migrations/0254_spiderdata_composite_indexes.py` | 3 composite indexes |
| `sports/tasks.py` | Retraining dispatch with dedup/cooldown/logging |
| `tests/test_lungs_hard_limit.py` | 3 SimpleTestCase tests for LUNGS enforcement |

## Design Items Deferred

These were part of the original 11 findings but are design-only (no code in this session):

- **3A: Unified Decision Queue** — Lightweight `PendingDecisionView` that unions 7 models into one feed
- **3B: Platform Goals** — `PlatformGoal` model for shared coordination across subsystems
- **3E: SpiderData-SignalCluster FK** — Replace JSON UUID list with proper M2M relationship

## Bugs Found & Fixed During Review

1. **Throttle exemption was dead code**: `_THROTTLE_EXEMPT` set checked `self.name` (always `execute_agent_task`) against unrelated task names. Those tasks (body health, PA chat, gates) are standalone Celery tasks that never flow through `execute_agent_task`. Removed the set entirely.
2. **daily_priority_scan** was initially routed to `long_running` which could starve under load. Changed to `broadcast`.

## Post-Deploy Verification Checklist

- [ ] `railway run python manage.py test tests.test_lungs_hard_limit` — 3 tests pass
- [ ] Verify `run_daily_priority_scan` appears in PeriodicTask table
- [ ] Verify cleanup beat entries registered: `cleanup-celery-task-events`, `cleanup-llm-call-logs`
- [ ] Check SpiderData indexes exist: `\di spiderdata_*` in psql
- [ ] Monitor logs for `Body throttle` messages when throttle_factor < 1.0
- [ ] Monitor logs for `retrain_dispatched` after next prediction evaluation cycle

## Next Session Priorities

1. Run post-deploy verification checklist above
2. Consider task timeout strategy for `--pool=threads` workers (SIGUSR1 doesn't work)
3. Implement design items (3A unified decision queue, 3B platform goals) if prioritized
4. Wire CostTracking `tenant` field once request-context tenant resolution is available
