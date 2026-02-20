# Session 1048 - Task Volume Breakdown API + PA Tool

**Date:** February 19, 2026
**Branch:** `feat/docx-csv-processors`
**Commit:** `08ad8dde`

## What Was Done

Added two new REST endpoints and a PA tool for one-click Celery task volume analysis, querying `CeleryTaskEvent` directly (bypassing the broken `TaskResult` table).

## Files Changed

| File | Change |
|------|--------|
| `core/views_celery_api.py` | `TaskBreakdownView` (aggregation) + `TaskBreakdownDetailView` (drill-down) |
| `core/urls.py` | 2 URL patterns: `/api/celery/breakdown/`, `/api/celery/breakdown/task/` |
| `core/services/pa_tool_schemas.py` | `task_breakdown_tool` schema (summary/drilldown) + TOOL_ENRICHMENT_MAP + TOOL_TO_INTENT_MAP |
| `core/services/tool_dispatcher.py` | `_handle_task_breakdown` handler registered as 59th handler |
| `core/services/unified_pa_entrypoint.py` | `task_breakdown` formatter (markdown tables) + added to fallback bypass list |

## Endpoints

### `GET /api/celery/breakdown/`
Query params: `window` (15m/60m/2h/6h/24h, default 60m), `limit` (default 25, max 50)

Returns:
- `totals`: tasks/success/failure/started counts
- `by_task`: top N tasks with count, failure rate, avg/p50/p95 duration (ms), top queues
- `by_agent`: top N agents by execution count with failure rate (from AgentExecution)

### `GET /api/celery/breakdown/task/`
Query params: `task_name` (required), `window` (default 60m), `limit` (default 50, max 200)

Returns: list of recent executions with task_id, started_at, finished_at, duration_ms, status, queue, worker, error snippet.

## PA Tool

`task_breakdown_tool` with actions:
- `summary`: same as breakdown endpoint
- `drilldown`: same as detail endpoint

Triggered by: "what's driving load?", "top failing tasks", "task volume", "task breakdown", "Celery performance"

## Design Decisions

1. **Percentiles in Python** — sorted list index. Data volume is manageable (~few thousand rows per 24h window)
2. **Handler duplicates view logic** — queries are straightforward (~10 lines each), avoids coupling views to PA
3. **No enrichment services** — task breakdown is self-contained telemetry, no intelligence enrichment needed
4. **Formatter uses markdown tables** — both summary and drilldown render as compact tables in PA chat

## Key Model References

- `CeleryTaskEvent` from `core.models_celery_telemetry`: task_id, task_name, queue, status (STARTED/SUCCESS/FAILURE/REVOKED), worker, started_at, finished_at, duration_seconds, error_type, error_message
- `AgentExecution` from `core.models`: agent (FK to Agent, use `agent__name`), status ('completed'/'failed'), created_at (NOT started_at)

## Verification

```bash
# Test aggregation endpoint
curl https://RAILWAY_URL/api/celery/breakdown/?window=60m

# Test drill-down
curl https://RAILWAY_URL/api/celery/breakdown/task/?task_name=core.tasks.run_agent_conversation&window=24h

# Test via PA
# "What tasks are driving load right now?"
# "Show me the top failing celery tasks in the last 24 hours"
# "Drill into core.tasks.execute_agent_task"
```
