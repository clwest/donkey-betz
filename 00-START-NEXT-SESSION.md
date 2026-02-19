# Session 1039 - Start Here

**Previous Sessions:** 1038 (DynamicPersonaAgent), 1037 (Initiative Pipeline + Artifact Routing Fix), 1036 (PA Function Calling Hardening), 1035 (RAG Wiring, Legal Agent, Stability)
**Date:** February 19, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2)** | **All 218 agent personas now routable** (82 Python + 139 DynamicPersona) | **Initiative pipeline UNBLOCKED** | 19 ACTIVE initiatives

---

## Session 1038 — What Happened

### DynamicPersonaAgent — All 218 Agents Now Routable

Created `DynamicPersonaAgent` (`core/agents/dynamic_persona_agent.py`) — a single BaseAgent subclass that loads its identity from the Agent DB record at construction time. Makes all 139 DB-only agent personas routable without creating 139 separate Python files.

**How it works:**
1. `AgentRouter.route()` checks `AGENT_MAP` first (82 Python classes)
2. If not found, checks Agent DB for `name=agent_name, is_active=True`
3. If found, instantiates `DynamicPersonaAgent(persona_name=agent_name, user=user)`
4. DynamicPersonaAgent loads `description`, `specialization`, `agent_type` from DB and synthesizes a system prompt
5. Has `web_search` + `spider_query` tools (standard research tools, no creation tools)
6. Falls back gracefully if DB record missing

**Key files changed:**
- `core/agents/dynamic_persona_agent.py` — NEW: 260-line agent class
- `core/agent_router.py` — DynamicPersonaAgent fallback at line 778 + special instantiation at line 882
- `core/services/artifact_execution.py` — Simplified `_select_agent()` back to returning `source_agent.name` directly (router handles DB-only personas now)

### Commits
| Commit | Description |
|--------|-------------|
| 43dab41e | feat: add DynamicPersonaAgent to make all 218 agent personas routable |
| d0785f98 | docs: Session 1037 handoff |

---

## Current System Health (post-Session 1038)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| PA latency (5-tool report) | **~16s** (was 140s with DB hang) |
| Agents routable | **All 218** (82 AGENT_MAP + 139 DynamicPersonaAgent + 2 blocked) |
| Initiatives | **19 ACTIVE**, 8 COMPLETED, 0 TRIAGE |
| Initiative stages | 38+ APPROVED, stages progressing |
| Artifact execution | All source_agent names now routable via DynamicPersonaAgent |
| Content finishing loop | LIVE (auto-enhance every 4h) |
| RAG documents | Wired into all 92 agents |
| Agent health | 92.4% pass rate |

---

## Known Issues / Open Items

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
- Profile consolidation (Phase 4 model dedup)
- Build real backends for AgentsPage channels/tools/templates tabs
- Score remaining ~3,500 deliverables (periodic task handles over time)
- Enhance remaining ~111 `needs_enhancement` blogs (5 per 4h run)
- Test RAG document injection with uploaded court orders via PA legal assistant
- Consider removing legacy keyword router once function calling is proven stable
- Verify DynamicPersonaAgent working on Railway (check `execute_approved_artifacts` logs)

---

## Verify Before Starting

```bash
# 1. Check Railway errors
railway logs -n 200 2>&1 | grep -i 'ERROR\|WARNING\|Traceback' | grep -v 'errors=0\|error_count\|error_message\|error_type\|INFO'

# 2. Initiative pipeline status
railway run python manage.py shell -c "
from core.models import Initiative
from core.models_document_registry import InitiativeStage
from django.db.models import Count
print('=== Initiatives ===')
for s in Initiative.objects.values('status').annotate(cnt=Count('id')).order_by('-cnt'):
    print(f'{s[\"status\"]:15} {s[\"cnt\"]}')
print('=== Initiative Stages (ACTIVE only) ===')
for s in InitiativeStage.objects.filter(initiative__status='ACTIVE').values('status').annotate(cnt=Count('id')).order_by('-cnt'):
    print(f'{s[\"status\"]:15} {s[\"cnt\"]}')
"

# 3. Verify DynamicPersonaAgent is routable
railway run python manage.py shell -c "
from core.agent_router import AgentRouter
from core.models_unified_system import Agent as AgentModel
routable_map = set(AgentRouter.AGENT_MAP.keys())
db_active = set(AgentModel.objects.filter(is_active=True).values_list('name', flat=True))
dynamic_routable = db_active - routable_map
print(f'AGENT_MAP entries: {len(routable_map)}')
print(f'Active DB agents: {len(db_active)}')
print(f'DynamicPersona-routable: {len(dynamic_routable)}')
print(f'Total routable: {len(routable_map) + len(dynamic_routable)}')
"

# 4. Check artifact execution for DynamicPersonaAgent usage
railway run python manage.py shell -c "
from core.models_conversation_artifacts import ArtifactExecution
from django.utils import timezone
from datetime import timedelta
cutoff = timezone.now() - timedelta(hours=4)
recent = ArtifactExecution.objects.filter(queued_at__gte=cutoff)
print(f'Recent executions: {recent.count()}')
for status in ['completed', 'failed', 'running', 'queued']:
    print(f'  {status}: {recent.filter(status=status).count()}')
"

# 5. Test PA function calling
# Ask: "Run a full operator report: system health, agent stats, pipeline status, and resource budget."
```

---

## Critical Patterns & Gotchas

**DynamicPersonaAgent (Session 1038):** `AgentRouter.route()` falls back to `DynamicPersonaAgent` when `AGENT_MAP` lookup fails. Checks `Agent.objects.filter(name=agent_name, is_active=True)`. Instantiated with `persona_name=agent_name`. Loads system prompt from Agent DB fields (`description`, `specialization`, `agent_type`). Has `web_search` + `spider_query` tools only.

**Artifact routing (Session 1038):** `_select_agent()` in `artifact_execution.py` now returns `source_agent.name` directly without AGENT_MAP validation — the router handles DB-only personas via DynamicPersonaAgent fallback.

**Initiative promotion (Session 1037):** `process_initiative_auto_progression` (every 10 min) has demotion sweep (ACTIVE->TRIAGE) AND promotion sweep (TRIAGE->ACTIVE). Backfills `owner_agent` with `ResearchAgent` fallback. Uses `skip_invariant_check=True` to bypass `save()` override.

**PA function calling (Session 1036):** `PA_USE_FUNCTION_CALLING=true` env var. Agentic loop in `_run_agentic_loop()` — max 5 iterations, GPT-5.2 decides tool calls. `pa_tool_schemas.py` has all schemas. `TOOL_TO_INTENT_MAP` maps tool names -> intents for enrichment.

**PA context timeouts (Session 1035):** All `_build_context` DB steps have 3-5s `asyncio.wait_for`. History load uses `SET LOCAL statement_timeout = '5000'`. Graceful degradation — PA works without any context piece.

**RAG context layer (Session 1034):** `_get_user_documents_context()` in AgentRouter — pgvector cosine search, threshold 0.45, top 5 chunks.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.

**Railway multi-service deployment:** GitHub push auto-deploys ALL services. Web service takes several minutes. Celery workers may take longer.
