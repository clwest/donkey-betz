# Session 1038 - Start Here

**Previous Sessions:** 1037 (Initiative Pipeline + Artifact Routing Fix), 1036 (PA Function Calling Hardening), 1035 (RAG Wiring, Legal Agent, Stability)
**Date:** February 19, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2)** | 82 routable agents (72 enabled, 8 rerouted, 2 blocked) | **Initiative pipeline UNBLOCKED** | 19 ACTIVE initiatives | 218 total agent personas (139 DB-only)

---

## Session 1037 — What Happened

### Initiative Pipeline Unblocked (TRIAGE -> ACTIVE)
All 20 non-completed initiatives were permanently stuck in TRIAGE — no promotion path existed. Fixed by adding a TRIAGE->ACTIVE promotion sweep to `process_initiative_auto_progression` (every 10 min) + `ResearchAgent` fallback for unowned initiatives.

**Result:** 0 ACTIVE -> **19 ACTIVE**, stages generating (38 APPROVED, 48 PENDING, 4 DRAFT, 5 BLOCKED).

### Artifact Execution Routing Fix
`execute_approved_artifacts` was failing for ~40% of approved artifacts (1,409/3,489) because `source_agent` pointed to DB-only agent personas not in `AgentRouter.AGENT_MAP`. Fixed `_select_agent()` to validate against `AGENT_MAP` before using `source_agent.name`, falling through to keyword/type matching for non-routable personas.

### Key Discovery: 218 Agent Personas
The Agent table has 218 entries: 82 routable (Python classes in AGENT_MAP) + **139 DB-only personas** (e.g. "Hidden Job Market Explorer", "Resume Optimizer AI", "Salary Negotiation Expert"). These are real agent personas created from conversations/dreams — NOT hallucinated names. They need a `DynamicPersonaAgent` to become routable.

### Commits
| Commit | Description |
|--------|-------------|
| fa448460 | Add TRIAGE->ACTIVE promotion sweep to unblock stuck initiatives |
| 52ce7d31 | Session 1036 handoff docs |
| 5746361d | Fall back to keyword/type routing when artifact source_agent not routable |

---

## Priority: DynamicPersonaAgent

Make all 218 agents routable by creating a single `DynamicPersonaAgent` class that loads persona from the Agent DB record.

### What exists
- `Agent` model has `name`, `description`, `system_prompt`, `tools` (JSONField), `enabled`
- `AgentRouter.AGENT_MAP` maps agent name -> Python class (currently 82 entries)
- `AgentRouter.route()` looks up `agent_name` in `AGENT_MAP`, fails if missing
- 139 DB-only personas have approved artifacts, learning records, and spider connections

### Proposed approach
1. Create `core/agents/dynamic_persona_agent.py` — subclass of `BaseAgent` that:
   - Receives agent name at construction time
   - Loads `system_prompt` and `description` from Agent DB record
   - Has access to standard tools (web_search, spider_query) but not creation tools
   - Falls back gracefully if DB record missing
2. Modify `AgentRouter.route()` to check `AGENT_MAP` first, then fall back to `DynamicPersonaAgent` for any Agent DB record with `enabled=True`
3. No need to add 139 entries to `AGENT_MAP` — the fallback is dynamic

### Questions to decide
- Which tools should DynamicPersonaAgent have access to? (web_search, spider_query, analyze_data?)
- Should the Agent DB `tools` JSONField drive tool access, or use a standard set?
- Should non-enabled DB personas be routable?

---

## Current System Health (post-Session 1037)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| PA latency (5-tool report) | **~16s** (was 140s with DB hang) |
| Agents routable | **82** (72 enabled + 8 rerouted + 2 blocked) |
| Agent personas (DB) | **218** total (139 DB-only, need DynamicPersonaAgent) |
| Initiatives | **19 ACTIVE**, 8 COMPLETED, 0 TRIAGE |
| Initiative stages | 38 APPROVED, 48 PENDING, 4 DRAFT, 5 BLOCKED |
| Artifact execution | Fixed — non-routable personas fall through to keyword/type routing |
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
- **DynamicPersonaAgent** — make all 218 agents routable (priority for Session 1038)
- Profile consolidation (Phase 4 model dedup)
- Build real backends for AgentsPage channels/tools/templates tabs
- Score remaining ~3,500 deliverables (periodic task handles over time)
- Enhance remaining ~111 `needs_enhancement` blogs (5 per 4h run)
- Test RAG document injection with uploaded court orders via PA legal assistant
- Consider removing legacy keyword router once function calling is proven stable

---

## Verify Before Starting

```bash
# 1. Check Railway errors (should be minimal — artifact "Unknown agent" errors should be gone)
railway logs -n 200 2>&1 | grep -i 'ERROR\|WARNING\|Traceback' | grep -v 'errors=0\|error_count\|error_message\|error_type\|INFO'

# 2. Initiative pipeline status (should show ACTIVE > 0, stages progressing)
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

# 3. Agent persona inventory
railway run python manage.py shell -c "
from core.models import Agent
from core.agent_router import AgentRouter
routable = set(AgentRouter.AGENT_MAP.keys())
total = Agent.objects.count()
db_only = Agent.objects.exclude(name__in=routable).count()
print(f'Total agent personas: {total}')
print(f'Routable (Python class): {len(routable)}')
print(f'DB-only (need DynamicPersonaAgent): {db_only}')
"

# 4. Test PA function calling
# Ask: "Run a full operator report: system health, agent stats, pipeline status, and resource budget."
# Should call 4+ tools via GPT-5.2 function calling, return raw numbers
```

---

## Critical Patterns & Gotchas

**Artifact routing fallback (Session 1037):** `_select_agent()` in `core/services/artifact_execution.py` checks `source_agent.name` against `AgentRouter.AGENT_MAP`. Non-routable DB personas fall through to keyword/type matching. 139 DB-only personas are real — do NOT delete them.

**Initiative promotion (Session 1037):** `process_initiative_auto_progression` (every 10 min) has demotion sweep (ACTIVE->TRIAGE) AND promotion sweep (TRIAGE->ACTIVE). Backfills `owner_agent` with `ResearchAgent` fallback. Uses `skip_invariant_check=True` to bypass `save()` override.

**PA function calling (Session 1036):** `PA_USE_FUNCTION_CALLING=true` env var. Agentic loop in `_run_agentic_loop()` — max 5 iterations, GPT-5.2 decides tool calls. `pa_tool_schemas.py` has all schemas. `TOOL_TO_INTENT_MAP` maps tool names -> intents for enrichment.

**PA context timeouts (Session 1035):** All `_build_context` DB steps have 3-5s `asyncio.wait_for`. History load uses `SET LOCAL statement_timeout = '5000'`. Graceful degradation — PA works without any context piece.

**Agent taxonomy (Session 1035):** `blocked_agents` (2), `rerouted_agents` (8), `fully_enabled_count` (72). Categories are disjoint and sum to `router_routable_total` (82). Defined in `_handle_agent_introspection` in tool_dispatcher.py.

**RAG context layer (Session 1034):** `_get_user_documents_context()` in AgentRouter — pgvector cosine search, threshold 0.45, top 5 chunks.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.

**Railway multi-service deployment:** GitHub push auto-deploys ALL services. Web service takes several minutes. Celery workers may take longer.
