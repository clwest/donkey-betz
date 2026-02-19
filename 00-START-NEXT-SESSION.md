# Session 1036 - Start Here

**Previous Sessions:** 1035 (PA Function Calling Hardening), 1034 (RAG Wiring, Legal Agent, Stability)
**Date:** February 19, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2)** | 82 routable agents (72 enabled, 8 rerouted, 2 blocked) | DB timeout resilience | RAG documents wired into ALL agents

---

## Session 1035 — What Happened

### PA Function Calling Hardened
The PA redesign (Session 1036: keyword router → GPT-5.2 function calling) was hardened through iterative Railway testing:
- **Pyright cleanup:** 0 errors across all 4 PA files (pa_tool_schemas.py, llm_enforcer.py, tool_dispatcher.py, unified_pa_entrypoint.py)
- **Operator report accuracy:** Fixed 3 tool handlers (schema alignment, routable count, pipeline by_status)
- **Disjoint agent taxonomy:** blocked (2) + rerouted (8) + fully_enabled (72) = 82 total, with reconciliation field
- **Tool call metadata:** GPT function call names/arguments/call_ids now captured (was `name: unknown`)
- **DB timeout resilience:** All `_build_context` steps capped at 3-5s (was unbounded, 134s hang observed)

### Model Deduplication
- Removed deprecated `UserAgentLearning` from `core/models.py` (242 lines). Canonical version in `core/models_unified_system.py`.
- Fixed broken import in `core/models/jobs/models.py`

### Commits
| Commit | Description |
|--------|-------------|
| ea2de879 | Resolve all Pyright errors in PA function calling files |
| 3d0725f3 | Add stats to introspection schema, fix routable count, add pipeline by_status |
| cca9aac2 | Remove deprecated UserAgentLearning from core/models.py |
| f5366d8a | Split stats/list in agent_introspection, add blocked agent breakdown |
| 450be9a2 | Make agent introspection categories disjoint and reconcilable |
| 53aaf07b | Capture GPT function call names in PA tool_call_metadata |
| 3e777844 | Add timeouts to PA _build_context to prevent DB connection hangs |

---

## Current System Health (post-Session 1035)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| PA latency (5-tool report) | **~16s** (was 140s with DB hang) |
| PA _build_context timeout | **5s per step** (was unbounded) |
| Railway log errors | **0** |
| Agents routable | **82** (72 enabled + 8 rerouted + 2 blocked) |
| Initiatives | 23 total (20 TRIAGE, 3 COMPLETED, **0 ACTIVE**) |
| Content finishing loop | LIVE (auto-enhance every 4h) |
| RAG documents | Wired into all 92 agents |
| Agent health | 92.4% pass rate |
| 24h stats (observed) | 45,869 celery tasks, 1,977 spider items, 68 active spiders, 482 signal clusters |

---

## Known Issues / Open Items

### 20 Initiatives Stuck in TRIAGE
All initiatives are TRIAGE (20) or COMPLETED (3), none ACTIVE. The pipeline isn't promoting anything. Likely the `_get_next_task_for_agent()` function is broken (InitiativeStage has no `assigned_agent` field). Needs investigation.

### Profile Consolidation (Phase 4)
Three user profile models: UserProfile + ExtendedUserProfile + EnhancedUserProfile. Need to merge into UnifiedUserProfile. Requires unified schema, migration, FK management across 50+ consumers. Deferred from Session 1035.

### Ghost Celery Dispatcher — HARD-BLOCKED
`execute_remediation_tasks` triggered 41x/48h from unknown source. All 6 execution + assignment paths blocked. Root cause still unknown.

### WorkflowAgent / TrendAnalysisAgent Timeout Risk
Both take 43-44min to complete. Celery timeout is 45min. They PASS but have no margin.

### Railway Web Service Instability
Web service hung during deploy (Postgres connection timeout in release command). Required force redeploy. The timeout fix protects the PA but the release command (`migrate + sync_celery_beat + setup_codebase_workspace`) may also need timeouts.

### Railway Cost
User hit $1,200/month limit, bumped to $1,500. Schedule throttling (Session 1034) + media guards should reduce costs.

### Future Improvements
- Investigate and fix initiative TRIAGE → ACTIVE promotion
- Profile consolidation (Phase 4 model dedup)
- Build real backends for AgentsPage channels/tools/templates tabs
- Score remaining ~3,500 deliverables (periodic task handles over time)
- Enhance remaining ~111 `needs_enhancement` blogs (5 per 4h run)
- Test RAG document injection with uploaded court orders via PA legal assistant
- Consider removing legacy keyword router once function calling is proven stable

---

## Verify Before Starting

```bash
# 1. Check Railway errors (should be 0)
railway logs -n 200 2>&1 | grep -i 'ERROR\|WARNING\|Traceback' | grep -v 'errors=0\|error_count\|error_message\|error_type\|INFO'

# 2. Test PA function calling
# Ask: "Run a full operator report: system health, agent stats, pipeline status, and resource budget."
# Should call 4+ tools via GPT-5.2 function calling, return raw numbers

# 3. Quick agent taxonomy check
# Ask: "How many agents are fully enabled vs blocked vs rerouted? Verify the math adds up."
# Should return: 72 + 8 + 2 = 82, reconciliation_ok: true

# 4. Initiative & content status
railway run python manage.py shell -c "
from core.models import Initiative
from core.models_unified_system import SelfBlog
from django.db.models import Count
print('=== Initiatives ===')
for s in Initiative.objects.values('status').annotate(cnt=Count('id')).order_by('-cnt'):
    print(f'{s[\"status\"]:15} {s[\"cnt\"]}')
print('=== Blogs ===')
for s in SelfBlog.objects.values('status').annotate(cnt=Count('id')).order_by('-cnt'):
    print(f'{s[\"status\"]:20} {s[\"cnt\"]}')
"
```

---

## Critical Patterns & Gotchas

**PA function calling (Session 1036):** `PA_USE_FUNCTION_CALLING=true` env var. Agentic loop in `_run_agentic_loop()` — max 5 iterations, GPT-5.2 decides tool calls. `pa_tool_schemas.py` has all schemas. `TOOL_TO_INTENT_MAP` maps tool names → intents for enrichment.

**PA context timeouts (Session 1035):** All `_build_context` DB steps have 3-5s `asyncio.wait_for`. History load uses `SET LOCAL statement_timeout = '5000'`. Graceful degradation — PA works without any context piece.

**Agent taxonomy (Session 1035):** `blocked_agents` (2), `rerouted_agents` (8), `fully_enabled_count` (72). Categories are disjoint and sum to `router_routable_total` (82). Defined in `_handle_agent_introspection` in tool_dispatcher.py.

**RAG context layer (Session 1034):** `_get_user_documents_context()` in AgentRouter — pgvector cosine search, threshold 0.45, top 5 chunks.

**Legal agent routing (Session 1034):** `legal_assistance` intent → `universal_agent_tool` → `AgentRouter.route()` → `LegalDocDrafterAgent`.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.

**Railway multi-service deployment:** GitHub push auto-deploys ALL services. Web service takes several minutes. Celery workers may take longer.
