# Session 1029 - Start Here

**Previous Session:** 1029 (OOM Fix + Agent Health Audit)
**Date:** February 17, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,573 SIGNAL CLUSTERS (ALL SCORED)** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 269** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **DELIVERABLE DEDUP: LIVE** | **CONVERSATION DEDUP: LIVE** | **REMEDIATION: DISCOVERY ONLY** | **AGENT WASTE: ALL PATHS CLOSED** | **COST TARGET: ~$6/day** | **SEMANTIC SPIDER SEARCH: LIVE** | **EVIDENCE GATES: COMPLETE (4 LAYERS)** | **SCORING CONTRACT: LIVE (2-TRACK PIPELINE)** | **OOM FIX: LIVE** | **35 THRIVING AGENTS, 6 BOUNDED**

---

## Session 1029 Summary (Just Completed)

### OOM Fix + Agent Health Audit (PRs #1282, #1283, #1284, #1285)

**Problem 1: celery-worker OOM crashes** — 3 crashes in 18 min. 5 heavy tasks (150-500MB) on 512MB container.

**Problem 2: Waste agents still running** — Session 1027 only fixed 1 of 3 dispatch paths. CodeGeneratorAgent still ran 96 times/day ($8.72) via `AGENT_WORKSPACE_REGISTRY` and `workspace_autopilot_tick`.

**Problem 3: Struggling agents** — 6 agents below 80% success. Root cause: unbounded task descriptions causing 45-min timeouts, and missing spider data types.

**Fixes:**

1. **PR #1282 — OOM Fix** (5 tasks rerouted default → long_running)
   - `run_multi_agent_conversation`, `run_autonomous_thinking_cycle`, `process_hivemind_sessions`, `execute_approved_dreams_via_orchestration`, `warm_up_spider_network`

2. **PR #1283 — Close Secondary Waste Paths**
   - Removed CodeGeneratorAgent + AudioAgent from `AGENT_WORKSPACE_REGISTRY`
   - Disabled 2 remediation triggers in `metrics_action_trigger.py`

3. **PR #1284 — Revenue Trigger**
   - Disabled `zero_revenue_7d` trigger (spawned 62+ "no revenue" runs/day)

4. **PR #1285 — Struggling Agent Fixes**
   - Bounded TrendAnalysisAgent task (0% → expected ~80%): "Top 3 trends, 500 words"
   - Bounded CompetitorAnalysisAgent task (prevent "Step 3 audit" reinterpretation)
   - Bounded CustomerResearchAgent task (explicit "no data" instruction)
   - Replaced CodeGeneratorAgent in workspace_autopilot + dream pipeline
   - Disabled AudioAgent TTS in podcast auto-generation

**Key discovery:** Three parallel scheduling systems dispatch agents independently:
- System A: `run_*_agents()` group schedules
- System B: `AGENT_WORKSPACE_REGISTRY` / `agent_category_rotation()`
- System C: `MetricsActionTrigger` condition-based triggers

See `docs/handoffs/SESSION_1029_OOM_FIX_AND_AGENT_HEALTH.md`

---

## Session 1027 Summary

### Agent Execution Audit & Waste Removal (PRs #1271, #1272, #1273)

- Disabled 3 Celery Beat remediation execution schedules ($9/day saved)
- Removed CodeGeneratorAgent from `run_development_tech_agents`
- Removed AudioAgent from `run_content_creation_agents`
- Bounded WorkflowAgent and OpportunityPipelineAgent tasks
- See `docs/handoffs/SESSION_1027_AGENT_EXECUTION_AUDIT.md`

---

## Session 1025 Summary

### Scoring Contract: Reach, Intent & Replicability (PRs #1267, #1268, #1269)

- Added 5 new fields to `SignalCluster` + rule-based `ContentScoringService`
- 1,573 clusters scored: attention=604, intent=169, unclassified=800
- See `docs/handoffs/SESSION_1025_SCORING_CONTRACT.md`

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 92 (54 routable, 25 non-routable, 26+ provenance-tracked) |
| Agent Health | 35 thriving (>80%), 6 bounded/helped, 3 waste paths closed |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 397+ |
| Services | 135 |
| Celery Tasks | 269 (3 remediation + 3 metric triggers disabled) |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 27 |
| Agents Persisting Output | 43 (via `_save_to_deliverable()` with 4h dedup) |
| PA Tools | 97 |
| PA Intents | 39 |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Active Initiatives | 3 (all Stage 2) |
| Blogs | 497 |
| Signal Clusters | 1,573 (all scored: 604 attention, 169 intent, 800 unclassified) |
| Deliverables | ~3,737 (cleaned from 9,577) |
| Daily LLM Cost | Target ~$6/day (down from $17/day) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Spider Search | Semantic (pgvector KNN) primary, keyword fallback |
| Evidence Gates | 4 layers complete (Layers 1-3 defensive + root cause fix) |
| Scoring Contract | Live — reach/intent/replicability/source_confidence/track on all clusters |

---

## Verify Before Starting

### 1. Agent Health (Session 1029)
```
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone; from datetime import timedelta
from django.db.models import Sum, Count, Q
since = timezone.now() - timedelta(hours=24)
execs = AgentExecution.objects.filter(created_at__gte=since)
total_cost = float(execs.aggregate(c=Sum('cost'))['c'] or 0)
total = execs.count()
ok = execs.filter(status='completed').count()
print(f'Total: {total} runs, {ok} completed ({ok/total*100:.0f}%), \${total_cost:.2f}')
for name in ['CodeGeneratorAgent', 'AudioAgent', 'TrendAnalysisAgent', 'WorkflowAgent']:
    qs = execs.filter(agent__name=name)
    c = qs.count(); s = qs.filter(status='completed').count()
    cost = float(qs.aggregate(c=Sum('cost'))['c'] or 0)
    print(f'  {name}: {c} runs ({s} ok), \${cost:.2f}')
"
```
- Expect: CodeGeneratorAgent=0, AudioAgent=0, TrendAnalysis>50% success, total<$8

### 2. Bounded Tasks Working (Session 1029)
```
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone; from datetime import timedelta
since = timezone.now() - timedelta(hours=24)
# Check for new bounded task format
ta = AgentExecution.objects.filter(agent__name='TrendAnalysisAgent', task__startswith='Summarize the top 3', created_at__gte=since)
print(f'TrendAnalysis bounded tasks: {ta.count()} ({ta.filter(status=\"completed\").count()} ok)')
ca = AgentExecution.objects.filter(agent__name='CompetitorAnalysisAgent', task__startswith='List 3 recent', created_at__gte=since)
print(f'CompetitorAnalysis bounded tasks: {ca.count()} ({ca.filter(status=\"completed\").count()} ok)')
"
```
- Expect: Bounded tasks appearing with higher success rate than old tasks

### 3. Semantic Search Health (Session 1024)
```
railway run python manage.py shell -c "
from core.services.spider_intelligence import SpiderIntelligenceService
svc = SpiderIntelligenceService()
results = svc.search_spider_data('blockchain security vulnerabilities', limit=3)
print(f'Results: {len(results)}')
for r in results:
    print(f'  {r[\"source\"]:20} rel={r[\"relevance\"]:.3f} terms={r[\"matching_terms\"]}')
print('PASS' if results and results[0]['matching_terms'] == ['semantic_match'] else 'FAIL')
"
```

### 4. OOM Crashes (Session 1029)
- Check Railway celery-worker logs — should have zero OOM crashes
- `railway logs -s celery-worker -n 50`

---

## Known Issues / Open Items

### Three Dispatch Systems (Session 1029) — MAPPED
Agents are dispatched from 3 independent systems. ALL waste paths now closed:
- System A: `run_*_agents()` group schedules — Fixed (PR #1273)
- System B: `AGENT_WORKSPACE_REGISTRY` / `agent_category_rotation()` — Fixed (PR #1283)
- System C: `MetricsActionTrigger` condition triggers — Fixed (PRs #1283, #1284)
- Plus: `workspace_autopilot_tick()`, `dream_execution_pipeline.py`, `auto_generate_podcast_episode()` — Fixed (PR #1285)

### Data-Starved Agents — NEEDS SPIDER DATA
CompetitorAnalysisAgent and CustomerResearchAgent evidence gates correctly block hallucination, but no competitive intelligence or customer data exists in the spider network. Need spiders configured to collect:
- Competitor product features, pricing, market share
- Customer behavior signals, reviews, preferences

### Evidence Pipeline Maturity Roadmap
1. Semantic spider search — DONE (Session 1024, PR #1265)
2. Evidence gates (4 layers) — DONE (Session 1023, PRs #1262-1264)
3. Scoring contract (reach, intent, replicability) — DONE (Session 1025)
4. Auto-experiment generator — FUTURE

**Next within this roadmap:** Track-based routing (consuming `SignalCluster.track` to route attention-track signals to content agents and intent-track signals to micro-product agents).

### Evidence Gate Layer 3b — Per-Agent Adoption
Each of 20+ provenance-tracked agents should compute `domain_match_rate` and pass it to `build_provenance()`. Currently only CompetitorAnalysisAgent and BaseBusinessResearchAgent subclasses enforce evidence gates.

### Rubber-Stamped Initiatives — NEEDS AUDIT
Initiatives that reached Stage 5 via the skip-ahead bug (PR #1251) have Stage 3-5 docs generated out of order with no real data.

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Remediation System — REDESIGNED (Session 1026/1027)
Discovery + assignment still running. Execution disabled. 80 open findings surfaced via:
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
- Remediation waste: **FIXED** (PRs #1257, #1271)
- Agent execution waste: **FIXED** (PRs #1273, #1283, #1284)
- UserProfile duplicates: **FIXED** (PR #1272)
- Evidence gate (irrelevant data): **FIXED** (PRs #1262-#1265)
- AudioAgent: **ALL PATHS CLOSED** (PRs #1273, #1283, #1285)
- CodeGeneratorAgent: **ALL PATHS CLOSED** (PRs #1273, #1283, #1285)
- Struggling agent timeouts: **BOUNDED** (PR #1285)
- OOM crashes: **FIXED** (PR #1282)
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

**Three agent dispatch systems (Session 1029):**
- System A: `run_*_agents()` group schedules (tasks.py) — 19 schedules
- System B: `AGENT_WORKSPACE_REGISTRY` / `agent_category_rotation()` (tasks.py)
- System C: `MetricsActionTrigger` (core/services/metrics_action_trigger.py)
- Plus: `workspace_autopilot_tick()`, `dream_execution_pipeline.py`, `auto_generate_podcast_episode()`
- To fully stop an agent: must check ALL paths, not just one

**Bounded vs unbounded tasks (Session 1029):**
- Unbounded: "Analyze current trends" → 45-min timeout, LLM reinterpretation
- Bounded: "Top 3 trends, 500 words, do NOT delegate" → completes in seconds
- Always specify: scope (top N), length limit, and "do NOT delegate/spawn sub-tasks"

**Agent group schedules (Session 1027):**
- 19 schedules in `core/celery.py` drive all automated agent runs
- All use `_run_agent_group()` (tasks.py:30247) -> `universal_agent_workspace_output()`
- To stop an agent: remove from its group list in `run_*_agents()` function

**django_celery_beat DB persistence (Session 1027):**
- Commenting out schedule definitions in `celery.py` does NOT disable DB-persisted schedules
- Must also run: `PeriodicTask.objects.filter(name='...').update(enabled=False)`

**Spider search (Session 1024):**
- `search_spider_data()` uses pgvector semantic similarity (primary) -> keyword matching (fallback)
- Key file: `core/services/spider_intelligence.py`
- Constants: `SEMANTIC_TOP_K=50`, `SEMANTIC_MIN_SIMILARITY=0.25`, `NOISY_SPIDERS`

**Scoring contract (Session 1025):**
- `SignalCluster` has `reach_score`, `intent_score`, `replicability_score`, `source_confidence`, `track`
- `ContentScoringService` in `core/services/content_scoring_service.py` — rule-based, no LLM
- Track values: `'attention'` (content), `'intent'` (micro-products), `'unclassified'`

**Agent model confusion (Session 1022):**
- `core.models_unified_system.Agent` — has `name`, used by `AgentExecution` FK
- `core.models.agents_registry.Agent` — has `display_name`, used by agent registry
- Always use `.name` for `AgentExecution.agent` — NOT `.display_name`

**Deliverable dedup (Session 1022):**
- `_save_to_deliverable()` checks 4-hour window by `title` + `agent_name`

**Conversation dedup (Session 1022):**
- Both `run_agent_conversation` and `run_multi_agent_conversation` check 6-hour window
- Only applies to `trigger_type='scheduled'` conversations

**Initiative pipeline (Session 1021):**
- `advance_initiative_pipeline` only processes `init.current_stage` — never scans ahead
- Prior stage must be `APPROVED` before current stage is processed
- `TechnicalDocumentAgent` has NO tools — only works with data provided in prompt/context

**Agent timeout limits (Session 1017, tuned Session 1020):**
- `execute_agent_task`: `soft_time_limit=2700` (45 min), `time_limit=3000` (50 min)
- OpenAI client timeout: 60s
- `cleanup_stale_agent_executions`: threshold 45min, runs every 15min

**AgentResult fields (Session 1017):**
- `.content` is @property alias for `.message`
- `.metadata` is @property alias for `.data`

**Railway multi-service deployment:**
- Each Procfile process is a SEPARATE Railway service
- GitHub push auto-deploys ALL services
- Celery workers can take up to 30 min to go live after push

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`).

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
