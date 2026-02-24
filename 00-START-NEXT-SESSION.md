# Session 1071 - Start Here

**Previous Sessions:** 1070 (Decision Gates — 4-question classification gate, stop auto-approving insights, boardroom classification UI), 1069 (Agent Timeout Epidemic — parallelize context gathering, reduce timeouts), 1068 (Artifact Execution Fix — fan-out execution, blank error messages, PA tool dispatch errors, error_summary_tool), 1067 (Boardroom/Governance Pages — critical decisions, spider attention items, decision modal fixes)
**Date:** February 23, 2026
**Status:** 218 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2, 43 tool schemas, 63+ handlers)** | 13 ACTIVE initiatives | 57 COMPLETED

---

## Session 1070 — What Happened

### Decision Gates: Classification Before Execution (PR #1440 — MERGED & DEPLOYED)

**Problem:** The system treated "insight exists" as "action should follow" without a human decision in between. All insights were auto-approved by `triage_extracted_artifacts` in `core/tasks.py`, bypassing any human classification.

**Fix — 4-Question Classification Gate:**
1. **What is this?** — research_finding / actionable_recommendation / scope_change / risk_flag / informational
2. **Who is it for?** — platform / end_users / founder / agents / public
3. **What data is allowed?** — public_only / internal_ops / api_data / user_data / all
4. **What phase is approved?** — research / prototype / pilot / production / none

**Changes:**
| File | Change |
|------|--------|
| `core/models_conversation_artifacts.py` | `classified`, `classified_at`, `classified_by`, `classification` fields + `classify()` method |
| `core/models_document_registry.py` | `target_audience`, `data_scope` on Initiative + `can_auto_progress` blocks at Stage 2+ |
| `core/tasks.py` (lines 842-867) | **Core fix:** auto-reject noise only (score < 0.3), all others stay `pending` |
| `core/services/artifact_execution.py` | Gate check: unclassified artifacts approved after 2026-02-24 cannot execute |
| `core/views_artifacts.py` | `POST api/artifacts/<uuid>/classify/` + `GET api/artifacts/needs-classification/` |
| `core/urls.py` | 2 new routes |
| `core/services/pa_tool_schemas.py` | `list_unclassified` + `classify_suggest` actions on boardroom_tool |
| `core/services/tool_dispatcher.py` | 2 new boardroom_tool handlers (list + suggest) |
| `frontend/src/pages/BoardroomPage.tsx` | "Needs Classification" tab with inline 4-dropdown forms |
| `frontend/src/lib/api.ts` | `classificationApi` with 2 methods |
| `core/migrations/0256_decision_gates.py` | Schema + data migration (324 artifacts grandfathered) |

**Key Numbers:**
| Metric | Value |
|--------|-------|
| Artifacts grandfathered | 324 |
| Pending needing classification | 2,339 |
| Gate activation date | 2026-02-24 |
| Noise threshold (auto-reject) | composite_score < 0.3 |
| Unclassified query threshold | composite_score >= 0.4 |

**Verified on Railway:** Migration applied, `needs-classification` endpoint returns data, grandfather clause working.

---

## Sessions 1067-1069 — Recent Context

### Session 1069: Agent Timeout Epidemic (PRs #1436-#1438)
- Parallelized context gathering in agent execution (was sequential, causing 30s+ timeouts)
- Video provider input validation fix
- Redis-resilient legal dispatch

### Session 1068: Artifact Execution Fix (PRs #1431-#1434)
- Fan-out artifact execution to prevent TimeLimitExceeded
- Blank error messages on agent failures fixed
- PA tool dispatch errors resolved
- error_summary_tool enhanced with timeout breakdown

### Session 1067: Boardroom/Governance Pages (PRs #1427-#1430)
- Critical decisions on Governance page with details drawer
- Spider attention items showing raw dict fixed
- ML prediction object handling in DecisionDetailModal

---

## Current System Health (post-Session 1070)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| PA tools | **43 schemas, 63+ handlers** — boardroom_tool extended with classify |
| Decision gates | **ACTIVE** — 2,339 artifacts need classification |
| Platform health score | **100** (7/7 components healthy) |
| Celery throughput | **1291 tasks/hour, 99.3% success** |
| Agents routable | **All 218** (82 AGENT_MAP + 139 DynamicPersonaAgent + 2 blocked) |
| Initiatives | **13 ACTIVE**, 57 COMPLETED |

---

## Known Issues / Open Items

### 2,339 Artifacts Need Classification
The decision gates are live but 2,339 pending artifacts need human classification before they can progress. The Boardroom page "Needs Classification" tab shows these. PA can help via `boardroom_tool(action=list_unclassified)` and `boardroom_tool(action=classify_suggest)`.

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

# 1. Verify classification endpoint
resp = urllib.request.urlopen(f'{BASE}/api/artifacts/needs-classification/?limit=3')
data = json.loads(resp.read())
print(f"Unclassified artifacts: {data['total_unclassified']}")
print(f"Sample: {[a['title'] for a in data['artifacts'][:3]]}")

# 2. Verify PA responds
data = json.dumps({'message': 'Check system health and list unclassified artifacts'}).encode()
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
```

---

## Critical Patterns & Gotchas

**Decision Gates (Session 1070):**
- Classification is decoupled from approval — `classify()` and `approve()` are separate operations
- `auto_approve` parameter in classify API is a convenience shortcut, not a coupling
- `classify_suggest` PA handler returns suggestions but NEVER applies them — human must confirm
- Grandfather clause: artifacts approved before 2026-02-24 skip classification gate
- Noise threshold (< 0.3) auto-rejects; 0.3-0.4 stays pending but hidden from classification UI (threshold >= 0.4)
- Initiative `can_auto_progress` blocks at Stage 2+ if `target_audience` or `data_scope` empty

**PA async flow (Session 974b):** POST `/api/pa/chat/` returns `{task_id}`. Poll GET `/api/pa/chat/status/<task_id>/` until `status != 'processing'`. Auth: `Authorization: Token <token>`.

**Railway resolve-node deployment (Session 1063):**
- Railway doesn't auto-create services from Procfile entries — must manually create via + Create
- Start command needs `bash -c "..."` wrapper — Railway doesn't run through a shell by default
- `RESOLVE_NODE_URL` + `RENDER_NODE_TOKEN` must be on **celery-pa** service
