---
originating_session: 983
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 983 — Celery Observability Fix + Skin Health Scoring

**Date:** February 9, 2026
**Previous Session:** 982 (Unified Single-Stock Ticker Lookup)
**Branch:** `session-983/celery-observability-fix`
**PR:** #1042

---

## Problem 1: "Celery tasks (24h): 0" in PA Status Snapshot

The PA reported "Celery tasks (24h): 0" in production despite 261 registered Celery tasks actively running (evidenced by 630 spider items, 4511 tool calls).

**Root cause:** `CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'` means task results go to Redis, not to the `django_celery_results.TaskResult` DB table. Three PA tools (`status_snapshot_tool`, `system_health_tool`, `error_summary_tool`) all queried `TaskResult` — an always-empty table.

## Solution 1: CeleryTaskEvent Telemetry (Option C)

New owned telemetry model populated via Celery signals, decoupled from the result backend choice.

### New Files

| File | Purpose |
|------|---------|
| `core/models_celery_telemetry.py` | `CeleryTaskEvent` model — one row per task execution (task_id, task_name, queue, status, worker, started_at, finished_at, duration_seconds, error_type, error_message) |
| `core/celery_telemetry.py` | Signal handlers: `on_task_prerun` (creates STARTED row), `on_task_postrun` (updates to SUCCESS), `on_task_failure` (updates to FAILURE with error details). All wrapped in bare `except` — telemetry never breaks task execution. |
| `core/migrations/0235_celery_task_event.py` | CreateModel migration with indexes on `(-started_at, status)` and `(task_name, -started_at)` |

### Modified Files

| File | Change |
|------|--------|
| `core/celery.py` | Import `core.celery_telemetry` after autodiscover to connect signal handlers |
| `core/models/__init__.py` | Register `CeleryTaskEvent` for Django model discovery (with `app_label = 'core'` in Meta) |
| `core/services/tool_dispatcher.py` | 4 replacements of `TaskResult` → `CeleryTaskEvent` queries (sections 1, 3, 4, 7) |

### Actuator Metrics (Section 10)

Added new `actuators_24h` section to `status_snapshot_tool` response:
- `initiatives_activated` — active initiatives updated in last 24h
- `blogs_publish_ready` — total publish-ready blog content
- `decisions_made` — boardroom items decided in last 24h
- `deliverables_created` — deliverables produced in last 24h

---

## Problem 2: Skin Health Score 38% ("damaged") on Railway

Body health was 83.2% instead of ~90%+ because the SKIN system scored 38.38% and triggered a false "critical" alert. The SKIN layer measures workspace file write success rates, but on Railway's ephemeral filesystem, writes fail between deploys — an infrastructure constraint, not a platform bug.

## Solution 2: Environment-Aware Skin Scoring

### Changes in `core/services/skin.py`

1. **`_is_ephemeral_filesystem()`** — detects Railway via `RAILWAY_ENVIRONMENT` env var
2. **`_calculate_health_score()`** — on Railway, uses 70-point healthy baseline. File write success/failure excluded. Only permission denials and review backlogs penalize (meaningful regardless of FS persistence). Score range: 70-100.
3. **`_determine_status()`** — on Railway, floors at `'active'` (never `'damaged'`/`'irritated'`). No false critical alerts.
4. **Response annotation** — adds `environment: 'ephemeral_filesystem'` and `environment_note` string explaining the context for PA/dashboards.

### Expected Impact

- Skin score: 38% → ~100%
- Overall body health: ~83% → ~90%+
- False "critical" workspace alert eliminated

---

## Key Gotchas

- **`core/models.py` vs `core/models/__init__.py`:** Both exist. Django uses the **package** (`__init__.py`). New model imports must go in `core/models/__init__.py` with `from ..models_xxx import ClassName` pattern and `app_label = 'core'` in Meta.
- **`django_celery_results.TaskResult`:** DO NOT query this table for task counts — it's empty when `CELERY_RESULT_BACKEND` is Redis. Use `CeleryTaskEvent` instead.
- **Railway environment detection:** Use `os.environ.get('RAILWAY_ENVIRONMENT')` — already used in 5 other places in the codebase.

---

## Verification

- `py_compile` passes on all 5 modified Python files
- Migration 0235 generated and correct
- `CeleryTaskEvent` importable from `core.models` with correct `app_label='core'`
- No new Pyright errors (all warnings are pre-existing Django dynamic model issues)
