# Session 1031 - Start Here

**Previous Session:** 1031 (Evidence Gate Fixes + Ghost Remediation Block)
**Date:** February 18, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,573 SIGNAL CLUSTERS (ALL SCORED)** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 269** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **DELIVERABLE DEDUP: LIVE** | **CONVERSATION DEDUP: LIVE** | **REMEDIATION: HARD-BLOCKED** | **AGENT WASTE: 1 LEAK REMAINING** | **COST TARGET: ~$6/day (ACTUAL: ~$15/day)** | **SEMANTIC SPIDER SEARCH: LIVE** | **EVIDENCE GATES: 4 LAYERS + BUSINESS AGENT FIXES** | **SCORING CONTRACT: LIVE (2-TRACK PIPELINE)** | **OOM FIX: LIVE** | **35 THRIVING AGENTS, 6 BOUNDED** | **PA ROUTING: 5 FIXES LIVE** | **PA CONVERSATION MEMORY: DB-BACKED**

---

## Session 1031 Summary (Just Completed)

### Evidence Gate Fixes for 4 Business Agents (PRs #1293-1296)

**Problem:** CompetitorAnalysisAgent, ResearchAgent, BrandStrategyAgent blocked by evidence gates. 69% completion rate for CompetitorAnalysis, ResearchAgent returning BLOCKED status.

**Root causes:**
1. `_synthesize_analysis` checked `isinstance(data, list)` but web_search returns dict — data silently dropped
2. Auto-extracted domain tags from task templates matched nothing in articles → 0% relevance → block
3. `WebSearchTool.search()` wrong method name — should be `.execute()`
4. Single-round tool calling (spider_query only, no web_search fallback)

**Fixes:**
- PR #1293: CompetitorAnalysisAgent dict normalization + domain tag skip + web_search fallback
- PR #1294: ResearchAgent lower threshold + web_search fallback
- PR #1295: BrandStrategyAgent dict handling + web_search fallback
- PR #1296: `.search()` → `.execute()` in 3 agents

**Result:** CompetitorAnalysis up from 69% → 90% completion. ResearchAgent at 97%.

### Ghost Remediation Block + Audit Cleanup (PR #1297)

**Problem:** `execute_remediation_tasks` ran 41x/48h and `run_autonomous_remediation_cycle` ran 4x despite being disabled in all known locations (Celery Beat, DB scheduler, no .delay() calls). Ghost dispatcher still unidentified.

**Root cause of garbage tasks:** `audit_tracker.py:_extract_table_findings()` regex too greedy — matched informational tables, creating AuditFindings with titles like "200+ | All 35+ integrations, API keys needed".

**Fixes:**
- Hard-blocked both tasks with early returns + warning logs
- Tightened table finding regex (first column must be issue-type header)
- Added row filters (numbers, file paths, bullet fragments, short strings)
- Raised gap finding min title from 10 → 25 chars
- Cleaned 34 garbage findings + 30 remediation tasks on Railway

### Endpoint Restoration (PR #1298)

**Problem:** `/api/agent-learning/activity/?limit=30` returning 404 every 30s in console.

**Fix:** URL route removed in Session 1009 orphan cleanup but view still existed. Re-added the route.

See `docs/handoffs/SESSION_1031_EVIDENCE_GATES_AND_GHOST_REMEDIATION.md`

---

## Session 1030 Summary

### PA Routing & Memory Fixes (PRs #1287, #1288, #1289)

- 5 PA routing/payload failures fixed (blog, agent execution, crypto, memory, sports betting)
- Intent keyword priority ordering + missing payload builders
- See `docs/handoffs/SESSION_1030_PA_ROUTING_AND_MEMORY_FIXES.md`

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 92 (54 routable, 25 non-routable, 26+ provenance-tracked) |
| Agent Health | 35 thriving (>80%), 6 bounded/helped, 3 waste paths closed, **1 leak (CodeGeneratorAgent)** |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 397+ |
| Services | 135 |
| Celery Tasks | 269 (remediation execution hard-blocked, metric triggers disabled) |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 27 |
| Agents Persisting Output | 43 (via `_save_to_deliverable()` with 4h dedup) |
| PA Tools | 97 |
| PA Intents | 39+ (5 routing fixes in Session 1030) |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Active Initiatives | 3 (all Stage 2) |
| Blogs | 497 |
| Signal Clusters | 1,573 (all scored: 604 attention, 169 intent, 800 unclassified) |
| Deliverables | ~3,737 (cleaned from 9,577) |
| Daily LLM Cost | Target ~$6/day (**Actual ~$15/day — CodeGeneratorAgent is $5.66**) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Spider Search | Semantic (pgvector KNN) primary, keyword fallback |
| Evidence Gates | 4 layers + business agent fixes (CompetitorAnalysis, Research, BrandStrategy) |
| Scoring Contract | Live — reach/intent/replicability/source_confidence/track on all clusters |
| PA Conversation Memory | DB-backed (last 10 turns survive worker recycle) |

---

## Priority: Deep Agent Testing

The platform is ready for systematic agent testing. Recommended approach:

### 1. Find & Close CodeGeneratorAgent Leak
CodeGeneratorAgent still runs 4x/2h post-deploy with garbage tasks. All known paths closed but something still dispatches it. This is the single biggest cost driver ($5.66/day).

```bash
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone; from datetime import timedelta
since = timezone.now() - timedelta(hours=4)
for e in AgentExecution.objects.filter(agent__name='CodeGeneratorAgent', created_at__gte=since).order_by('-created_at')[:5]:
    task = (e.task or '')[:80]
    trigger = (e.input_data or {}).get('trigger_source', 'unknown')
    parent = e.parent_object_type or 'none'
    print(f'{e.created_at.strftime(\"%H:%M\")} status={e.status} parent={parent} trigger={trigger}')
    print(f'  task: {task}')
"
```

### 2. Investigate Ghost Celery Dispatcher
`execute_remediation_tasks` was triggered 41x/48h from unknown source. Hard-blocked now but root cause unknown.

```bash
# Check if any DB-persisted periodic tasks are still enabled
railway run python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
for pt in PeriodicTask.objects.filter(enabled=True, task__icontains='remediat'):
    print(f'{pt.name}: {pt.task} (enabled={pt.enabled}, last_run={pt.last_run_at})')
print(f'Total enabled periodic tasks: {PeriodicTask.objects.filter(enabled=True).count()}')
"
```

### 3. Systematic Agent Health Audit
Run each agent category and verify success rates:

```bash
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone; from datetime import timedelta
from django.db.models import Count, Q, Sum
since = timezone.now() - timedelta(hours=24)
execs = AgentExecution.objects.filter(created_at__gte=since)

# Summary
total = execs.count()
ok = execs.filter(status='completed').count()
cost = float(execs.aggregate(c=Sum('cost'))['c'] or 0)
print(f'24h: {total} runs, {ok} ok ({ok/max(total,1)*100:.0f}%), \${cost:.2f}')
print()

# By agent (top 15)
for a in execs.values('agent__name').annotate(
    cnt=Count('id'),
    ok=Count('id', filter=Q(status='completed')),
    fail=Count('id', filter=Q(status='failed')),
    cost=Sum('cost')
).order_by('-cnt')[:15]:
    rate = a['ok']/max(a['cnt'],1)*100
    flag = ' !!!' if rate < 50 else ''
    print(f'{a[\"agent__name\"]:35} {a[\"cnt\"]:3} runs ({a[\"ok\"]} ok, {a[\"fail\"]} fail) {rate:.0f}% \${float(a[\"cost\"] or 0):.2f}{flag}')
"
```

### 4. Test Specific Agents Manually
```bash
railway run python manage.py shell -c "
from core.agents.business.competitor_analysis_agent import CompetitorAnalysisAgent
agent = CompetitorAnalysisAgent()
result = agent.execute(
    task='Perform a competitor audit for Donkey Betz covering Jasper.ai, Copy.ai, Writesonic',
    context={}, scifi_context={}, spider_context={}
)
print(f'Status: {result.status}')
print(f'Type: {result.data.get(\"type\", \"unknown\")}')
print(f'Data points: {result.data.get(\"data_points_analyzed\", 0)}')
"
```

---

## Verify Before Starting

### 1. Evidence Gates (Session 1031)
```bash
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone; from datetime import timedelta
since = timezone.now() - timedelta(hours=6)
for name in ['CompetitorAnalysisAgent', 'ResearchAgent', 'BrandStrategyAgent']:
    qs = AgentExecution.objects.filter(agent__name=name, created_at__gte=since)
    total = qs.count()
    ok = qs.filter(status='completed').count()
    blocked = 0
    for e in qs.filter(status='completed'):
        if e.output_data and isinstance(e.output_data, dict):
            if e.output_data.get('type') == 'insufficient_evidence':
                blocked += 1
    rate = ok/max(total,1)*100
    print(f'{name}: {total} runs, {ok} ok ({rate:.0f}%), {blocked} evidence-blocked')
"
```
- Expect: CompetitorAnalysis >85% completion, ResearchAgent >90%

### 2. Remediation Hard-Block (Session 1031)
```bash
railway run python manage.py shell -c "
from core.models_celery_telemetry import CeleryTaskEvent
from django.utils import timezone; from datetime import timedelta
since = timezone.now() - timedelta(hours=6)
for task in ['execute_remediation_tasks', 'run_autonomous_remediation_cycle']:
    c = CeleryTaskEvent.objects.filter(task_name__contains=task, started_at__gte=since).count()
    print(f'{task}: {c} runs (should be 0)')
"
```

### 3. Agent-Learning Endpoint (Session 1031)
```bash
curl -s -o /dev/null -w "%{http_code}" "https://donkey-betz-platform-production.up.railway.app/api/agent-learning/activity/?limit=5"
# Expect: 200
```

### 4. Cost Check
```bash
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone; from datetime import timedelta
from django.db.models import Sum
since = timezone.now() - timedelta(hours=24)
cost = float(AgentExecution.objects.filter(created_at__gte=since).aggregate(c=Sum('cost'))['c'] or 0)
print(f'24h cost: \${cost:.2f} (target: <\$6)')
"
```

---

## Known Issues / Open Items

### CodeGeneratorAgent Leak — URGENT
4 runs/2h post-deploy with garbage tasks. $5.66/day. All known dispatch paths supposedly closed (AGENT_WORKSPACE_REGISTRY, run_development_tech_agents) but something still triggers it. Tasks contain markdown table fragments from old AuditRemediationTask entries.

### Ghost Celery Dispatcher — HARD-BLOCKED
`execute_remediation_tasks` triggered 41x/48h from unknown source. Hard-blocked at function level. Root cause investigation needed — check django_celery_beat DB entries, Redis queued tasks, Railway scheduled jobs.

### Cost Overshoot — $15/day vs $6/day target
Breakdown: CodeGeneratorAgent $5.66, ResearchAgent $2.23, WorkflowAgent $1.23, CompetitorAnalysis $0.95, COOAgent $0.85, remainder spread thin. Closing CodeGeneratorAgent leak would bring it to ~$10/day.

### WorkflowAgent 42% Success Rate — NEEDS INVESTIGATION
24 runs, 10 completed. May need task bounding or timeout adjustment.

### PA Tool Timeout — NEEDS WORK
`universal_agent_tool` has 30s timeout — too short for LLM-based agents (ResearchAgent times out). Intent routing works but execution gets killed.

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Three Dispatch Systems (Session 1029) — MAPPED
Agents are dispatched from 3 independent systems. ALL waste paths now closed except CodeGeneratorAgent:
- System A: `run_*_agents()` group schedules — Fixed (PR #1273)
- System B: `AGENT_WORKSPACE_REGISTRY` / `agent_category_rotation()` — Fixed (PR #1283)
- System C: `MetricsActionTrigger` condition triggers — Fixed (PRs #1283, #1284)
- Plus: `workspace_autopilot_tick()`, `dream_execution_pipeline.py`, `auto_generate_podcast_episode()` — Fixed (PR #1285)
- Remediation execution: HARD-BLOCKED (PR #1297)

### Data-Starved Agents — NEEDS SPIDER DATA
CompetitorAnalysisAgent and CustomerResearchAgent evidence gates correctly block hallucination, but no competitive intelligence or customer data exists in the spider network. Need spiders configured to collect:
- Competitor product features, pricing, market share
- Customer behavior signals, reviews, preferences

### Evidence Pipeline Maturity Roadmap
1. Semantic spider search — DONE (Session 1024, PR #1265)
2. Evidence gates (4 layers) — DONE (Session 1023, PRs #1262-1264)
3. Scoring contract (reach, intent, replicability) — DONE (Session 1025)
4. Business agent evidence fixes — DONE (Session 1031, PRs #1293-1296)
5. Auto-experiment generator — FUTURE

### Evidence Gate Layer 3b — Per-Agent Adoption
Each of 20+ provenance-tracked agents should compute `domain_match_rate` and pass it to `build_provenance()`. Currently only CompetitorAnalysisAgent and BaseBusinessResearchAgent subclasses enforce evidence gates.

### Remediation System — HARD-BLOCKED (Session 1031)
Discovery + assignment still running (assign-open-findings-to-agents every 2h). Execution hard-blocked. 80 open findings surfaced via:
```
railway run python manage.py show_remediation_findings
railway run python manage.py show_remediation_findings --priority P0 P1
```

### Dream Pipeline — NO-OP
Zero approved dreams, zero DreamImplementations. Only $0.54/day so not urgent.

### Remaining Agent Failures — REDUCED
- `.metadata` crashes: **0** (PR #1236)
- False-positive timeouts: **0** (PR #1237)
- Conversation junk: **0** (PR #1239)
- Initiative stall: **FIXED** (PRs #1247, #1250)
- Initiative duplicates: **FIXED** (PR #1247)
- Initiative skip-ahead: **FIXED** (PR #1251)
- Initiative garbage docs: **FIXED** (PR #1252)
- Conversation date hallucination: **FIXED** (PR #1248)
- Deliverable spam: **FIXED** (PR #1256)
- Conversation duplication: **FIXED** (PR #1258)
- Remediation waste: **FIXED** (PRs #1257, #1271, **#1297**)
- Agent execution waste: **FIXED** (PRs #1273, #1283, #1284, **CodeGen leak remains**)
- UserProfile duplicates: **FIXED** (PR #1272)
- Evidence gate (irrelevant data): **FIXED** (PRs #1262-#1265, **#1293-#1296**)
- AudioAgent: **ALL PATHS CLOSED** (PRs #1273, #1283, #1285)
- CodeGeneratorAgent: **LEAK REMAINS** — 4 runs/2h still dispatched
- Struggling agent timeouts: **BOUNDED** (PR #1285)
- OOM crashes: **FIXED** (PR #1282)
- PA routing failures: **FIXED** (PRs #1287, #1288, #1289)
- Agent-learning 404: **FIXED** (PR #1298)
- Remaining: assorted agent failures (~10/day, low cost)

### CodeArtifact v2 — DEFERRED
- PatchApplier service, frontend review panel, initiative FK wiring
- 35 artifacts pending review

### Blog Topic Diversity — Monitor
19/40 published blogs about Security/Homeland. PR #1141 strengthens novelty scoring.

### Sports Prediction Accuracy — MONITOR
Initial accuracy is 70.2% (mostly NCAAB). Monitor by sport/model.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`).

**Evidence gate dict normalization (Session 1031):**
- `web_search` returns `{'results': [...], 'query': ...}` — NOT a list
- `spider_query` may return `{'data': [...]}` or a list
- Always normalize: `data = data.get('results', data.get('data', [data]))` before iteration
- Auto-extracted domain tags are unreliable — skip domain-relevance gate when `domain_tags_auto_extracted=True`

**Remediation pipeline (Session 1031):**
- `execute_remediation_tasks` and `run_autonomous_remediation_cycle` are HARD-BLOCKED with early returns
- Discovery (`run_audit_discovery`) + assignment (`assign_open_findings_to_agents`) still run on schedule
- `audit_tracker._extract_table_findings()` tightened: first column must be issue-type header
- AuditFinding fields: `title`, `description`, `priority`, `category`, `status`, `assigned_agent`, `raw_text`, `metadata`

**PA intent ordering (Session 1030):**
- `_detect_intent_and_route()` checks keywords top-to-bottom — earlier matches win
- Specific intents (sports_betting, agent_execution) must come BEFORE generic ones (opportunities, research)

**PA conversation memory (Session 1030):**
- `_load_conversation_history_from_db()` loads last 10 ChatConversation turns on init
- Survives Celery worker recycling

**Three agent dispatch systems (Session 1029):**
- System A: `run_*_agents()` group schedules (tasks.py) — 19 schedules
- System B: `AGENT_WORKSPACE_REGISTRY` / `agent_category_rotation()` (tasks.py)
- System C: `MetricsActionTrigger` (core/services/metrics_action_trigger.py)
- Plus: `workspace_autopilot_tick()`, `dream_execution_pipeline.py`, `auto_generate_podcast_episode()`
- To fully stop an agent: must check ALL paths, not just one

**Bounded vs unbounded tasks (Session 1029):**
- Unbounded: "Analyze current trends" → 45-min timeout, LLM reinterpretation
- Bounded: "Top 3 trends, 500 words, do NOT delegate" → completes in seconds

**django_celery_beat DB persistence (Session 1027):**
- Commenting out schedule definitions in `celery.py` does NOT disable DB-persisted schedules
- Must also run: `PeriodicTask.objects.filter(name='...').update(enabled=False)`

**Spider search (Session 1024):**
- `search_spider_data()` uses pgvector semantic similarity (primary) -> keyword matching (fallback)
- Key file: `core/services/spider_intelligence.py`

**Agent model confusion (Session 1022):**
- `core.models_unified_system.Agent` — has `name`, used by `AgentExecution` FK
- `core.models.agents_registry.Agent` — has `display_name`, used by agent registry
- Always use `.name` for `AgentExecution.agent` — NOT `.display_name`

**Railway multi-service deployment:**
- Each Procfile process is a SEPARATE Railway service
- GitHub push auto-deploys ALL services
- Web service can take several minutes to redeploy after push

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`).

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
