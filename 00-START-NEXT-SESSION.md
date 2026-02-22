# Session 1064 - Start Here

**Previous Sessions:** 1063 (PA Tools Expansion — deliverables update/delete/cleanup/pagination, media_tool, davinci_tool, resolve-node Railway deploy, celery OOM fixes), 1062 (PA Async Tool Pattern + Celery-Content OOM Fix), 1061 (Sports Betting Accuracy Handler), 1060 (PA Real-World Testing — 3 degenerate detector fixes, tool call observability, FC sanitizer)
**Date:** February 22, 2026
**Status:** 218 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2, 43 tool schemas, 63+ handlers)** | 13 ACTIVE initiatives | 57 COMPLETED

---

## Session 1064 — What's Done So Far

### PeriodicTask Queue Sync Fix (PR pending)

**Problem:** 179 `PeriodicTask` records in django_celery_beat DB had wrong/missing `queue` values, overriding `CELERY_TASK_ROUTES` and sending heavy tasks to the 200MB celery-worker.

**Fix:**
1. Created `core/management/commands/sync_task_queues.py` — reads `CELERY_TASK_ROUTES`, resolves intended queue per enabled PeriodicTask, updates mismatches. Supports `--apply` and `--verbose`.
2. Added `sync_task_queues --apply` to Procfile release command (runs after `sync_celery_beat` on every deploy).
3. Deleted `check_routes.py` temp diagnostic script.

**Status:** Code committed. **NOT YET applied on Railway.** Next step: deploy or `railway run python manage.py sync_task_queues --apply`, then redeploy celery-worker + celery-long-running.

**Dry run result:** 179 fixed, 36 already correct, 68 no route (skipped).

---

## Session 1063 — What Happened

### PA Tools Expansion (PRs #1407-#1411)

Systematically exposed missing capabilities to the PA, driven by live PA conversation where it identified its own gaps:

| PR | Feature | Details |
|----|---------|---------|
| #1407 | deliverables_tool update/delete | 9 actions, better schema descriptions so GPT-5.2 knows all capabilities |
| #1408 | resolve_agent in run_agent + media_tool | PA can now delegate to ResolveAgent and browse ImageHistory/VideoHistory/AudioHistory |
| #1409 | davinci_tool | Direct DaVinci control: health, render, status, result, jobs, grades |
| #1410 | resolve-node Railway service | FastAPI server deployed as standalone Railway service |
| #1411 | deliverables pagination + cleanup | offset pagination, category/agent filters, bulk cleanup (duplicates/orphans/low_quality with dry_run) |

### resolve-node Railway Deploy

| Item | Value |
|------|-------|
| Public URL | `https://resolve-node-production.up.railway.app` |
| Start command | `bash -c "cd resolve_node && MOCK_MODE=true uvicorn app:app --host 0.0.0.0 --port ${PORT:-5001}"` |
| Target port | 8080 (Railway injects PORT=8080) |
| Status | ONLINE, healthy, mock mode |

**Key env vars (set on celery-pa):** `RESOLVE_NODE_URL=https://resolve-node-production.up.railway.app`, `RENDER_NODE_TOKEN=<token>`

### Celery OOM Fixes (PRs #1412, #1413)

| Worker | Change | PR |
|--------|--------|-----|
| celery-worker | max-tasks-per-child 10→5 | #1412 |
| celery-long-running | concurrency 3→1, max-tasks 10→3 | #1413 |

---

## Current System Health (post-Session 1063)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| PA tools | **43 schemas, 63+ handlers** — media_tool + davinci_tool added |
| DaVinci render node | **ONLINE** (mock mode) at `resolve-node-production.up.railway.app` |
| Platform health score | **100** (7/7 components healthy) |
| Celery throughput | **1291 tasks/hour, 99.3% success** |
| Beat schedule | **21 tasks throttled** + `dispatch-pending-action-items` every 30 min |
| Agents routable | **All 218** (82 AGENT_MAP + 139 DynamicPersonaAgent + 2 blocked) |
| Initiatives | **13 ACTIVE**, 57 COMPLETED, 5 TRIAGE, 12 ARCHIVED (87 total) |

---

## Known Issues / Open Items

### Celery OOM (root cause fixed Session 1064)
celery-worker and celery-long-running were OOMing. Root cause: 179 PeriodicTask records had stale queue values overriding CELERY_TASK_ROUTES. Fix: `sync_task_queues` management command (runs on every deploy). **Needs Railway deploy** to take effect. Previous mitigations (lower concurrency/max-tasks) also still in place.

### Data Layer Gaps (discovered in PA testing)
1. **Revenue tracker**: $0 ingested, 0 records — needs Stripe/affiliate/ad data source integration
2. **Stock intelligence**: no watchlist concept — ticker-addressed only, needs portfolio model
3. **ML predictions table**: deprecated with 0 records

### Deliverable Cleanup Ready
cleanup tool built but not yet run. PA can do:
- `deliverables_tool cleanup strategy=duplicates dry_run=true` — preview duplicate removal
- `deliverables_tool cleanup strategy=orphans dry_run=true` — preview orphan removal
- Production had ~382 duplicate excess deliverables at time of analysis

### 25+ Untested PA Tools
High-priority untested: `brainstorm_tool`, `dream_tool`, `content_review_tool`, `learning_patterns_tool`, `opportunity_manager_tool`, `pilots_tool`, `reasoning_engine_tool`, `legal_doc_drafter_agent`, `legislation_tool`, `media_tool`, `davinci_tool`

### Other Open Items
- Railway cost: $1,200→$1,500/month limit, ~47k tasks/day
- 3 contaminated Stage 4 docs (ThinkingAgent diagnostics instead of real content)
- generate_blog_tool timeout (exceeds 30s PA tool timeout, works as Celery task)
- Tenant Phases 2-3, Profile consolidation Phase 4
- Real DaVinci integration when hardware available (currently mock mode only)

---

## Verify Before Starting

```python
import urllib.request, json, time

TOKEN = 'YOUR_TOKEN'
BASE = 'https://donkey-betz-platform-production.up.railway.app'

# 1. Verify PA responds
data = json.dumps({'message': 'Check system health and DaVinci render node status'}).encode()
req = urllib.request.Request(f'{BASE}/api/pa/chat/', data=data, headers={
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
})
resp = json.loads(urllib.request.urlopen(req).read())
task_id = resp['task_id']
print(f'Task ID: {task_id}')

time.sleep(10)
req = urllib.request.Request(f'{BASE}/api/pa/chat/status/{task_id}/', headers={
    'Authorization': f'Token {TOKEN}',
})
result = json.loads(urllib.request.urlopen(req).read())
print(f"Status: {result['status']}")
print(result.get('content', '')[:500])

# 2. Verify resolve-node directly
import urllib.request
resp = urllib.request.urlopen('https://resolve-node-production.up.railway.app/health')
print(json.loads(resp.read()))
# Expected: {"status":"healthy","queue_size":0,"active_jobs":0}
```

---

## Critical Patterns & Gotchas

**Railway resolve-node deployment (Session 1063):**
- Railway doesn't auto-create services from Procfile entries — must manually create via + Create
- Start command needs `bash -c "..."` wrapper — Railway doesn't run through a shell by default
- Railway injects PORT (usually 8080), overriding app defaults — public domain target port must match
- `RESOLVE_NODE_URL` + `RENDER_NODE_TOKEN` must be on **celery-pa** service (where PA tool handlers execute)

**deliverables_tool cleanup (Session 1063):** 3 strategies (duplicates/orphans/low_quality), all support `dry_run=true`. Duplicates keeps newest per title, deletes rest. Orphans deletes deliverables with no user. Low_quality deletes short content (<50 chars).

**PA degenerate detector patterns (Session 1060):** `_is_degenerate_content()` has 4 patterns. Pattern 1 (repetitive chunks) requires >40% ratio. Pattern 2 (filler words) uses word-boundary matching with narrow list.

**PA loop-break must drop previous_response_id (Session 1060):** When breaking out of loops, NEVER use `previous_response_id` from the current response — rebuild fresh messages via `_build_messages_array()`.

**PA tool calls now logged (Session 1060):** `ToolCallRecord` entries with `agent_name='PersonalAssistant'`. PA trace_id (format `pa-N-hex`) is in `task_summary` field.

**Initiative daily creation cap (Session 1059):** 15/day rolling limit. Similarity dedup includes COMPLETED initiatives from last 48h.

**PA Railway URL (Session 1057):** Use `https://donkey-betz-platform-production.up.railway.app` (NOT `donkeybetz.com`).

**PA async flow (Session 974b):** POST `/api/pa/chat/` returns `{task_id}`. Poll GET `/api/pa/chat/status/<task_id>/` until `status != 'processing'`. Auth: `Authorization: Token <token>`.
