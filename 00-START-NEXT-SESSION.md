# Session 1057 - Start Here

**Previous Sessions:** 1056 (Railway Cost Throttle + PA Degenerate Loop Fix), 1049 (INIT-000057 RAG Gaps + celery-content OOM Fix), 1048 (Task Volume Breakdown API), 1043 (Brainstorm Bulk Export + DOCX/CSV + OOM Fix)
**Date:** February 20, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2, 41 tool schemas, 59 handlers)** | **All 218 agent personas routable** | **Tenant model Phase 1 landed** | 4 ACTIVE initiatives | 36 COMPLETED

---

## Session 1056 — What Happened

### Railway Cost Throttle (PR #1356)

Throttled 21 high-frequency Celery beat tasks to reduce Railway compute ~59%:
- **Body Systems (9 tasks):** 30-90s → 120-300s
- **Broadcast/Dashboard (6 tasks):** 60-180s → 120-600s
- **Event Bus/Infra (5 tasks):** 30-120s → 60-300s
- **3D Model Polling (1 task):** 30s → 60s

`body-coordinator-check` (60s) NOT changed — gates LLM throttle mode.
Estimated ~21,000 fewer invocations/day.

### PA Degenerate Text Loop Fix (PR #1357)

GPT-5.2 got stuck generating filler text ("Ok.Ok.Let's call.Ok.") instead of actual function calls. The degenerate content detector only ran when tool calls were present — text-only responses bypassed it.

**Fix:** Added degenerate check in the no-tool-calls early return path + Pattern 4 (high "Ok." density >=8). PA now returns friendly error instead of garbage.

---

## Priority: Working with the PA via Claude Code

**Next session focus:** Working with the PA through the Railway API from Claude Code.

### How to Connect to the PA via Railway

The PA runs on Railway at `https://donkeybetz.com`. Authentication uses DRF Token auth.

**Step 1: Get an auth token**
```bash
# Login to get token
curl -s -X POST https://donkeybetz.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}' | python -m json.tool
# Returns: {"token": "abc123...", "user": {...}}
```

**Step 2: Send a message to the PA (async — returns task_id)**
```bash
TOKEN="your-token-here"
curl -s -X POST https://donkeybetz.com/api/pa/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d '{"message": "What are the active initiatives?"}' | python -m json.tool
# Returns: {"success": true, "task_id": "celery-task-id", "status": "processing"}
```

**Step 3: Poll for the response**
```bash
TASK_ID="the-task-id-from-step-2"
curl -s https://donkeybetz.com/api/pa/chat/status/$TASK_ID/ \
  -H "Authorization: Token $TOKEN" | python -m json.tool
# Returns: {"success": true, "status": "completed", "response": "...", "tool_runs": [...]}
# If still processing: {"success": true, "status": "processing"}
# Poll every 2-3 seconds until status != "processing"
```

**Key endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/login/` | POST | Get auth token (`{username, password}` → `{token}`) |
| `/api/pa/chat/` | POST | Send message to PA (`{message}` → `{task_id}`) |
| `/api/pa/chat/status/<task_id>/` | GET | Poll async result → `{status, response, tool_runs}` |
| `/api/pa/context/` | GET | Get PA context (user profile, system state) |

**Important notes:**
- PA chat is **async** — POST returns a `task_id`, you must poll `/status/` for the response
- Polling typically completes in 3-15 seconds depending on tool calls
- The PA uses GPT-5.2 function calling with up to 5 agentic loop iterations
- All 41 tool schemas are available (initiative_tool, content_review_tool, dream_tool, task_breakdown_tool, brainstorm_tool, etc.)
- Auth header format: `Authorization: Token <token>` (NOT Bearer)

---

## Current System Health (post-Session 1056)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| PA tools | **41 schemas, 59 handlers** |
| Beat schedule | **21 tasks throttled** (~59% reduction, ~21k fewer invocations/day) |
| Agents routable | **All 218** (82 AGENT_MAP + 139 DynamicPersonaAgent + 2 blocked) |
| Initiatives | **4 ACTIVE**, 36 COMPLETED, 1 TRIAGE, 8 ARCHIVED (49 total) |
| Degenerate detection | **4 patterns** — repetition, filler ratio, unique ratio, Ok. density |

---

## Known Issues / Open Items

### Ghost Celery Dispatcher — HARD-BLOCKED
`execute_remediation_tasks` triggered 41x/48h from unknown source. All 6 execution + assignment paths blocked. Root cause still unknown.

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

```bash
# 1. Verify beat throttling deployed (check a throttled task)
railway logs 2>&1 | grep -c 'heart-service-heartbeat' # Should be ~12/hour now, not 60

# 2. Verify PA degenerate fix deployed
railway logs 2>&1 | grep 'Degenerate text-only'  # Should appear if triggered

# 3. Test PA connection from CLI
TOKEN=$(curl -s -X POST https://donkeybetz.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}' | python -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"

TASK_ID=$(curl -s -X POST https://donkeybetz.com/api/pa/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d '{"message": "Hello, what can you help me with?"}' | python -c "import sys,json; print(json.load(sys.stdin)['task_id'])")
echo "Task ID: $TASK_ID"

sleep 5
curl -s https://donkeybetz.com/api/pa/chat/status/$TASK_ID/ \
  -H "Authorization: Token $TOKEN" | python -m json.tool

# 4. Check initiative health
railway run python manage.py shell -c "
from core.models import Initiative
for s in ['ACTIVE', 'TRIAGE', 'COMPLETED', 'ARCHIVED']:
    c = Initiative.objects.filter(status=s).count()
    print(f'{s}: {c}')
"
```

---

## Critical Patterns & Gotchas

**PA async flow (Session 974b):** POST `/api/pa/chat/` returns `{task_id}`. Poll GET `/api/pa/chat/status/<task_id>/` until `status != 'processing'`. Typical completion: 3-15s. Auth: `Authorization: Token <token>` (NOT Bearer).

**PA degenerate detection (Session 1056):** `_is_degenerate_content()` has 4 patterns: (1) repeated short substrings from start, (2) filler word ratio > 0.5, (3) unique word ratio < 0.15, (4) "ok." count >= 8. Check runs in BOTH tool-call and no-tool-call paths.

**Beat schedule throttling (Session 1056):** 21 tasks throttled. `body-coordinator-check` stays at 60s — it sets throttle mode that gates LLM calls. All `expires` values are 10s below schedule interval. If body systems dashboard seems stale, this is expected (5-min refresh now).

**Lazy ML loading (Session 1049):** `SentenceTransformerProvider._get_model()` defers model load to first use. Global `rag_system` in `content/embeddings.py` is a `_LazyRAGSystem` proxy — importing it does NOT trigger construction. NEVER add eager model loads at module level in files imported by Celery workers.

**Task volume breakdown (Session 1048):** `task_breakdown_tool` queries `CeleryTaskEvent` (NOT `TaskResult`). REST endpoints at `/api/celery/breakdown/` and `/api/celery/breakdown/task/`.

**Initiative quality gate (Session 1042):** `ConversationInitiativePipeline._quality_gate()` now rejects content-review topics and any single explore pattern match.

**ContentWriterAgent result structure (Session 1041):** `result.message` is a descriptive summary, NOT the actual content. Real content is in `result.data['content']['full_text']`.

**Anti-hallucination guard (Session 1040):** Conversation system prompt includes CRITICAL instruction: if no REAL-WORLD INTELLIGENCE section appears, agent must say "No data available" and never fabricate.

**ThinkingAgent banned from document generation:** ThinkingAgent returns system diagnostics instead of reviewing content. NEVER use ThinkingAgent for content tasks.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.
