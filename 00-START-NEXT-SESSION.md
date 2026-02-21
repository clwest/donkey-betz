# Session 1059 - Start Here

**Previous Sessions:** 1058 (Action Item Auto-Dispatch + Ghost Dispatcher Fix), 1057 (PA Tool Audit — 9 bugs fixed across 5 PRs), 1056 (Railway Cost Throttle + PA Degenerate Loop Fix), 1049 (INIT-000057 RAG Gaps + celery-content OOM Fix)
**Date:** February 20, 2026
**Status:** 218 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2, 41 tool schemas, 61 handlers)** | **All 218 agent personas routable** | **Tenant model Phase 1 landed** | 4 ACTIVE initiatives | 36 COMPLETED

---

## Session 1058 — What Happened

### Level 3: Prompt-Guided Action Items + Auto-Dispatch (PR #1366)

Stage prompts were not asking for action items, so extraction was unreliable. Now all stage prompts (1-5) explicitly request an "Action Items" section with `"- AgentName: Task description (Timeline)"` format.

| Change | File | Details |
|--------|------|---------|
| `internal_document` type instructions | `content_writer_agent.py:1421` | Added to `_get_type_instructions()` with explicit "Action Items (Required)" section |
| Stage prompt action items | `tasks.py:34457,34488` | All 5 stages now request action items in required output |
| `STAGE_TYPES` / `STAGES_WITH_AUTO_DISPATCH` | `models_document_registry.py:1213` | Constants classifying stages; auto-dispatch enabled for stages 4-5 only |
| `dispatch_pending_action_items` beat task | `tasks.py:33900`, `celery.py:2322` | Runs every 30 min, dispatches pending items to assigned agents |
| Safety gates | `tasks.py:33900` | Blocked agents, AGENT_MAP validation, 8/day cap, 6-hour dedup, 10/cycle cap |
| `start_action_item` PA tool | `tool_dispatcher.py:3607`, `pa_tool_schemas.py:67` | Humans can mark items in-progress via PA |

### Ghost Celery Dispatcher — ROOT CAUSE FOUND & FIXED (PR #1367)

**Root cause:** `DatabaseScheduler` keeps stale `PeriodicTask` DB entries even after tasks are removed from `celery.py`. The Procfile release command ran `sync_celery_beat --apply --create-only` but never `--disable-missing`, so `execute-remediation-tasks` (commented out in Session 1026) stayed `enabled=True` in the DB and kept firing at its original `crontab(minute=30, hour='*/4')` schedule — 6x/day, matching the observed 41 triggers/48h.

| Change | File | Details |
|--------|------|---------|
| Added `--disable-missing` to release | `Procfile:10` | Orphaned DB tasks now disabled on every deploy |
| Fixed orphan disable loop | `sync_celery_beat.py:130` | Was only iterating `orphaned[:20]`, now disables all |

**After next deploy:** Ghost triggers will drop to zero. The stale `execute-remediation-tasks`, `run-autonomous-remediation-cycle`, and `verify-completed-fixes` DB entries will be disabled.

---

## Current System Health (post-Session 1058)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| PA tools | **41 schemas, 61 handlers** — 36 fully working, `start_action_item` + `complete_action_item` added |
| Beat schedule | **21 tasks throttled** + 1 new (`dispatch-pending-action-items` every 30 min) |
| Agents routable | **All 218** (82 AGENT_MAP + 139 DynamicPersonaAgent + 2 blocked) |
| Initiatives | **4 ACTIVE**, 36 COMPLETED, 1 TRIAGE, 8 ARCHIVED (49 total) |
| Ghost dispatcher | **RESOLVED** — stale DB entries will be disabled on next deploy |
| Action item dispatch | **NEW** — stages 4-5 auto-dispatch pending items to assigned agents |

---

## Known Issues / Open Items

### WorkflowAgent / TrendAnalysisAgent Timeout Risk
Both take 43-44min to complete. Celery timeout is 45min. They PASS but have no margin.

### Railway Cost
User hit $1,200/month limit, bumped to $1,500. Session 1056 throttled 21 tasks (~59% reduction). Monitor Railway compute after 24h.

### DecisionExtractor Initiative Spam
DecisionExtractor creates initiatives from `suggested_feature` in decision summaries. 3 were archived (Session 1042). Consider adding stricter validation for DecisionExtractor-sourced initiatives.

### 3 Contaminated Stage 4 Docs (Session 1040)
These completed initiatives have Stage 4 docs filled with ThinkingAgent system diagnostics instead of real content:
- "Navigating Time-Sensitive Securities Fraud Alerts"
- "Revise and Enhance Class Action Landscape Briefing"
- "Revise Florida High School Soccer Playoff Broadcast Information"

### ContentWriterAgent high failure count
PA reports 44 ContentWriterAgent failures in 60 min. Most are likely pre-fix `internal_document` errors. Monitor after 24h — should drop to near zero.

### generate_blog_tool timeout
Full blog generation via PA exceeds the 30s tool timeout. Works fine as a Celery task, just can't complete within the PA agentic loop. Consider raising the PA tool timeout or making it async.

### Future Improvements
- Tenant Phases 2-3 (budget enforcement, customer API endpoints, TenantScopeMixin)
- Profile consolidation (Phase 4 model dedup)
- Initiative data validation gate (check data source exists before creating data-dependent initiatives)
- DecisionExtractor initiative title quality gate (reject vague "Enhancement" proposals)
- Build real backends for AgentsPage channels/tools/templates tabs
- Score remaining ~3,500 deliverables
- Enhance remaining ~111 `needs_enhancement` blogs
- Consider removing legacy keyword router once function calling is proven stable

---

## Verify Before Starting

```python
# Use Python to avoid shell escaping issues with curl
import urllib.request, json, time

TOKEN = 'YOUR_TOKEN'  # Get from /api/v1/auth/login/
BASE = 'https://donkey-betz-platform-production.up.railway.app'

# 1. Verify PA responds
data = json.dumps({'message': 'Hello, what can you help me with?'}).encode()
req = urllib.request.Request(f'{BASE}/api/pa/chat/', data=data, headers={
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
})
resp = json.loads(urllib.request.urlopen(req).read())
task_id = resp['task_id']
print(f'Task ID: {task_id}')

time.sleep(8)
req = urllib.request.Request(f'{BASE}/api/pa/chat/status/{task_id}/', headers={
    'Authorization': f'Token {TOKEN}',
})
result = json.loads(urllib.request.urlopen(req).read())
print(f"Status: {result['status']}")
print(result.get('content', '')[:500])

# 2. Check initiative health via PA
# "Use initiative_tool with action stats"

# 3. Check ghost dispatcher is gone (after deploy)
# "Use execution_history_tool with action failures and window 24h"
# Should show zero execute_remediation_tasks triggers
```

---

## Critical Patterns & Gotchas

**DatabaseScheduler orphan risk (Session 1058):** `django_celery_beat.DatabaseScheduler` keeps stale `PeriodicTask` entries even after removing tasks from `celery.py`. The release command now runs `--disable-missing` to clean these up. If you comment out a beat task, it won't stop firing until the next deploy runs `sync_celery_beat --disable-missing`.

**Action item dispatch (Session 1058):** `dispatch_pending_action_items` runs every 30 min. Only dispatches items from `STAGES_WITH_AUTO_DISPATCH` (stages 4-5) on ACTIVE initiatives. Safety: blocked agents, AGENT_MAP validation, 8/day cap per agent, 6-hour dedup, 10/cycle cap.

**PA Railway URL (Session 1057):** Use `https://donkey-betz-platform-production.up.railway.app` (NOT `donkeybetz.com`). Use Python `urllib` for requests to avoid shell escaping issues with curl.

**PA async flow (Session 974b):** POST `/api/pa/chat/` returns `{task_id}`. Poll GET `/api/pa/chat/status/<task_id>/` until `status != 'processing'`. Typical completion: 3-15s. Auth: `Authorization: Token <token>` (NOT Bearer).

**PA tool schema-handler pattern (Session 1057):** Many tool schemas had action enums that didn't match what the handler supports. Always check both `pa_tool_schemas.py` (what GPT-5.2 sees) and `tool_dispatcher.py` (what actually executes).

**PA tool serialization pattern (Session 1057):** ToolDispatcher handlers must return JSON-serializable dicts. Django model objects (ProjectWorkspace, Team, etc.) must be converted to dicts/strings before returning.

**Beat schedule throttling (Session 1056):** 21 tasks throttled. `body-coordinator-check` stays at 60s — it sets throttle mode that gates LLM calls. All `expires` values are 10s below schedule interval.

**Lazy ML loading (Session 1049):** `SentenceTransformerProvider._get_model()` defers model load to first use. NEVER add eager model loads at module level in files imported by Celery workers.

**ContentWriterAgent result structure (Session 1041):** `result.message` is a descriptive summary, NOT the actual content. Real content is in `result.data['content']['full_text']`.

**ThinkingAgent banned from document generation:** ThinkingAgent returns system diagnostics instead of reviewing content. NEVER use ThinkingAgent for content tasks.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.
