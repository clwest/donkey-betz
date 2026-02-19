# Session 1037 - Start Here

**Previous Sessions:** 1036 (TRIAGE Promotion Fix), 1035 (PA Function Calling Hardening), 1034 (RAG Wiring, Legal Agent, Stability)
**Date:** February 19, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2)** | 82 routable agents (72 enabled, 8 rerouted, 2 blocked) | **Initiative pipeline UNBLOCKED** | 19 ACTIVE initiatives

---

## Session 1036 — What Happened

### Initiative Pipeline Unblocked (TRIAGE -> ACTIVE)
All 20 non-completed initiatives were permanently stuck in TRIAGE. Session 994 introduced TRIAGE as a quality gate, Session 1016 added demotion sweep + `can_promote_to_active()`, but **no promotion path was ever built**. The complete deadlock:
- New initiatives always created as TRIAGE
- `advance_initiative_pipeline` only queries ACTIVE — skipped TRIAGE entirely
- `_auto_assign_owner()` failed silently for `HiveMind:*` creators, leaving `owner_agent` empty (hard requirement for quality gate)
- Even manual promotion blocked by `save()` override

**Fix (2 files, ~30 lines):**
1. **`core/tasks.py`** — Added TRIAGE->ACTIVE promotion sweep inside `process_initiative_auto_progression` (runs every 10 min). Backfills `owner_agent` for unowned initiatives using `PROGRAM_OWNER_MAP` + `ResearchAgent` fallback, then promotes those passing `can_promote_to_active()`.
2. **`core/services/initiative_integration_service.py`** — Added `ResearchAgent` fallback in `_auto_assign_owner()` so `HiveMind:*` creators and `uncategorized` programs no longer leave `owner_agent` empty.

**Result verified on Railway:**
- Before: 20 TRIAGE, 0 ACTIVE, 8 COMPLETED
- After: **19 ACTIVE**, 0 TRIAGE, 8 COMPLETED
- `advance_initiative_pipeline` immediately picked up the ACTIVE initiatives
- `execute_initiative_stage_task` generating stage documents (72-146s per task)
- Stage breakdown: 38 APPROVED, 48 PENDING, 4 DRAFT, 5 BLOCKED

### Commits
| Commit | Description |
|--------|-------------|
| fa448460 | Add TRIAGE->ACTIVE promotion sweep to unblock stuck initiatives |

---

## Current System Health (post-Session 1036)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| PA latency (5-tool report) | **~16s** (was 140s with DB hang) |
| Agents routable | **82** (72 enabled + 8 rerouted + 2 blocked) |
| Initiatives | **19 ACTIVE**, 8 COMPLETED, 0 TRIAGE |
| Initiative stages | 38 APPROVED, 48 PENDING, 4 DRAFT, 5 BLOCKED |
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

### Artifact Execution Agent Name Mismatch
`execute_approved_artifacts` fails for initiatives with hallucinated agent names like "SEO Content Optimizer", "Content Strategy Planner", "Hidden Job Market Explorer", "Resume Optimizer AI" — these don't exist in the router. The `owner_agent` or artifact `assigned_agent` was set to a non-existent agent name. May need a name-normalization step or fallback routing.

### Future Improvements
- Fix artifact agent name mismatches (normalize to real agent names)
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

# 3. Test PA function calling
# Ask: "Run a full operator report: system health, agent stats, pipeline status, and resource budget."
# Should call 4+ tools via GPT-5.2 function calling, return raw numbers

# 4. Blog status
railway run python manage.py shell -c "
from core.models_unified_system import SelfBlog
from django.db.models import Count
for s in SelfBlog.objects.values('status').annotate(cnt=Count('id')).order_by('-cnt'):
    print(f'{s[\"status\"]:20} {s[\"cnt\"]}')
"
```

---

## Critical Patterns & Gotchas

**Initiative promotion (Session 1036):** `process_initiative_auto_progression` (every 10 min) now has both demotion sweep (ACTIVE->TRIAGE for bad initiatives) AND promotion sweep (TRIAGE->ACTIVE for qualifying ones). Backfills `owner_agent` with `ResearchAgent` fallback. Uses `skip_invariant_check=True` to bypass `save()` override.

**PA function calling (Session 1036):** `PA_USE_FUNCTION_CALLING=true` env var. Agentic loop in `_run_agentic_loop()` — max 5 iterations, GPT-5.2 decides tool calls. `pa_tool_schemas.py` has all schemas. `TOOL_TO_INTENT_MAP` maps tool names -> intents for enrichment.

**PA context timeouts (Session 1035):** All `_build_context` DB steps have 3-5s `asyncio.wait_for`. History load uses `SET LOCAL statement_timeout = '5000'`. Graceful degradation — PA works without any context piece.

**Agent taxonomy (Session 1035):** `blocked_agents` (2), `rerouted_agents` (8), `fully_enabled_count` (72). Categories are disjoint and sum to `router_routable_total` (82). Defined in `_handle_agent_introspection` in tool_dispatcher.py.

**RAG context layer (Session 1034):** `_get_user_documents_context()` in AgentRouter — pgvector cosine search, threshold 0.45, top 5 chunks.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.

**Railway multi-service deployment:** GitHub push auto-deploys ALL services. Web service takes several minutes. Celery workers may take longer.
