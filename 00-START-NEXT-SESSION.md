# Session 1030 - Start Here

**Previous Session:** 1030 (PA Routing & Memory Fixes)
**Date:** February 17, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,573 SIGNAL CLUSTERS (ALL SCORED)** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 269** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **DELIVERABLE DEDUP: LIVE** | **CONVERSATION DEDUP: LIVE** | **REMEDIATION: DISCOVERY ONLY** | **AGENT WASTE: ALL PATHS CLOSED** | **COST TARGET: ~$6/day** | **SEMANTIC SPIDER SEARCH: LIVE** | **EVIDENCE GATES: COMPLETE (4 LAYERS)** | **SCORING CONTRACT: LIVE (2-TRACK PIPELINE)** | **OOM FIX: LIVE** | **35 THRIVING AGENTS, 6 BOUNDED** | **PA ROUTING: 5 FIXES LIVE** | **PA CONVERSATION MEMORY: DB-BACKED**

---

## Session 1030 Summary (Just Completed)

### PA Routing & Memory Fixes (PRs #1287, #1288, #1289)

**Problem:** Production PA audit (12 test messages via Railway API) revealed 5 routing/payload failures — blog queries fell to `general`, agent execution routed to `research`, crypto search returned 0, conversation memory lost on worker recycle, sports betting misrouted to job opportunities.

**Root causes:** Intent keyword priority ordering (generic terms matched before specific intents) and missing payload builders for `agent_execution` and `crypto_price`.

**Fixes:**

1. **PR #1287 — Core 5 Fixes**
   - Sports betting keywords check moved before generic "opportunities"
   - Broader blog patterns + auto-set `type='blog'` for SelfBlog queries
   - Publish-ready guard (routes to `recent`, not `publish` action)
   - Agent execution check moved before research + regex pattern
   - Crypto price switched to `by_spider` action (CoinGecko processed_data)
   - Conversation memory: loads last 10 ChatConversation rows from DB on init
   - SelfBlog counts added to stats response
   - `processed_data` included in by_spider results (first 3 items)

2. **PR #1288 — Routing Refinements**
   - Agent execution regex: removed `\b` before "agent" (no word boundary in "researchagent")
   - Blog "show me" routing: added latest/recent/newest/show me as `recent` action before `details`

3. **PR #1289 — Agent Execution Payload**
   - Extracts `agent_name` (preserving PascalCase) and `task` from messages like "run ResearchAgent to find AI trends"

**All 5 tests verified on Railway production.**

See `docs/handoffs/SESSION_1030_PA_ROUTING_AND_MEMORY_FIXES.md`

---

## Session 1029 Summary

### OOM Fix + Agent Health Audit (PRs #1282, #1283, #1284, #1285)

- 5 heavy tasks rerouted default → long_running (celery-worker OOM fix)
- All waste agent dispatch paths closed (CodeGeneratorAgent, AudioAgent, OpportunityScoringAgent)
- 6 struggling agents bounded (TrendAnalysis, Competitor, Customer)
- See `docs/handoffs/SESSION_1029_OOM_FIX_AND_AGENT_HEALTH.md`

---

## Session 1027 Summary

### Agent Execution Audit & Waste Removal (PRs #1271, #1272, #1273)

- Disabled 3 Celery Beat remediation execution schedules ($9/day saved)
- Removed CodeGeneratorAgent from `run_development_tech_agents`
- Removed AudioAgent from `run_content_creation_agents`
- Bounded WorkflowAgent and OpportunityPipelineAgent tasks
- See `docs/handoffs/SESSION_1027_AGENT_EXECUTION_AUDIT.md`

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
| PA Intents | 39+ (5 routing fixes in Session 1030) |
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
| PA Conversation Memory | DB-backed (last 10 turns survive worker recycle) |

---

## Verify Before Starting

### 1. PA Routing (Session 1030)
```
curl -s -X POST "https://donkey-betz-platform-production.up.railway.app/api/pa/chat/" \
  -H "Authorization: Token 0cdc1c72dba99ea637485076ee952d571440aa30" \
  -H "Content-Type: application/json" \
  -d '{"message":"show me the latest blogs"}'
# Poll with task_id, expect: intent=content_review, action=recent
```

### 2. Agent Health (Session 1029)
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

### PA Tool Timeout — NEEDS WORK
`universal_agent_tool` has 30s timeout — too short for LLM-based agents (ResearchAgent times out). Intent routing works but execution gets killed.

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### PA Crypto Data Formatting — MINOR
CoinGecko data returns but LLM summary shows top market cap coin (Hyperliquid) instead of extracting the specific coin the user asked about. Needs better prompt engineering or pre-filtering.

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
- PA routing failures: **FIXED** (PRs #1287, #1288, #1289)
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

**PA intent ordering (Session 1030):**
- `_detect_intent_and_route()` checks keywords top-to-bottom — earlier matches win
- Specific intents (sports_betting, agent_execution) must come BEFORE generic ones (opportunities, research)
- Compound agent names like "ResearchAgent" become "researchagent" in lowercase — no word boundary before "agent"
- "show me" matches `details` action — specific phrases like "latest/recent/newest" must be checked first

**PA conversation memory (Session 1030):**
- `_load_conversation_history_from_db()` loads last 10 ChatConversation turns on init
- Survives Celery worker recycling (previously lost on every `max_tasks_per_child` restart)
- Each PA instance is user-scoped (stored in `_pa_instances` dict keyed by user)

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
