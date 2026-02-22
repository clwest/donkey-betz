# Session 1064 — PeriodicTask Queue Sync Fix

**Date:** February 22, 2026
**PR:** (pending)

---

## Problem

celery-worker and celery-long-running were OOMing because 179 `PeriodicTask` records in the django_celery_beat DB had wrong or missing `queue` values. When `PeriodicTask.queue` is `'default'` or NULL, it either overrides or bypasses `CELERY_TASK_ROUTES`, causing heavy tasks (LLM calls, agent orchestrations, spider init, embeddings) to land on the 200MB celery-worker instead of their intended queues.

**Root cause:** `sync_celery_beat` (run during every deploy) creates PeriodicTask records but never sets the `queue` field. Tasks created before routing rules were added retain stale queue values that persist across deploys.

**Evidence:** 179 misrouted tasks found comparing PeriodicTask.queue vs CELERY_TASK_ROUTES. Examples:
- `core.tasks.process_spider_data_automatic` (route: long_running) had `queue='default'` in DB
- `content.tasks.poll_pending_trainings` (route: content) had `queue=NULL`

## Solution

### 1. New management command: `sync_task_queues`

**File:** `core/management/commands/sync_task_queues.py`

Reads `CELERY_TASK_ROUTES` from Django settings, resolves the intended queue for each enabled PeriodicTask (explicit routes first, then glob patterns), and updates any that differ.

| Flag | Behavior |
|------|----------|
| (default) | Dry run — prints what would change |
| `--apply` | Persists changes to DB |
| `--verbose` | Shows all tasks including already-correct ones |

Dry run output: `Updated: 179 | Already correct: 36 | No route (skipped): 68`

### 2. Added to Procfile release command

`sync_task_queues --apply` now runs after `sync_celery_beat` on every deploy:

```
release: python manage.py migrate --noinput && python manage.py sync_celery_beat --apply --create-only --disable-missing && python manage.py sync_task_queues --apply && python manage.py setup_codebase_workspace
```

This ensures queue fields are corrected on every deploy, so future `sync_celery_beat` task creation never leaves stale queues.

### 3. Deleted `check_routes.py`

Temporary diagnostic script used during investigation. No longer needed.

---

## Files Changed

| File | Change |
|------|--------|
| `core/management/commands/sync_task_queues.py` | NEW — management command |
| `Procfile` line 11 | Added `sync_task_queues --apply` to release |
| `check_routes.py` | DELETED — temp diagnostic |

## Verification

- Dry run locally shows 179 tasks to fix, 36 already correct, 68 unmatched
- Next step: `railway run python manage.py sync_task_queues --apply` to fix production DB
- Then redeploy celery-worker and celery-long-running to pick up corrected queue assignments

## Key Insight

`CELERY_TASK_ROUTES` is a runtime router that Celery uses when dispatching tasks. But `PeriodicTask.queue` is a DB field that celery-beat sends directly in the task message. If `PeriodicTask.queue` is set (even to 'default'), it **overrides** the router. If it's NULL, behavior depends on whether celery-beat loads router config. The safest approach is to always set `PeriodicTask.queue` to match `CELERY_TASK_ROUTES` explicitly.
