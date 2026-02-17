# Session 1027 - Start Here

**Previous Session:** 1026 (Remediation Redesign) + 1027 (Agent Execution Audit)
**Date:** February 17, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,573 SIGNAL CLUSTERS (ALL SCORED)** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 269** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **DELIVERABLE DEDUP: LIVE** | **CONVERSATION DEDUP: LIVE** | **REMEDIATION: DISCOVERY ONLY** | **AGENT WASTE REMOVED** | **COST SAVINGS: ~$10.81/day (target ~$6/day)** | **SEMANTIC SPIDER SEARCH: LIVE** | **EVIDENCE GATES: COMPLETE (4 LAYERS)** | **SCORING CONTRACT: LIVE (2-TRACK PIPELINE)**

---

## Session 1027 Summary (Just Completed)

### Agent Execution Audit & Waste Removal (PRs #1271, #1272, #1273)

**Problem:** Overnight agent executions: 589 runs, $16.76/day. Audit found 4 waste sources burning ~$10/day.

**Fixes:**

1. **PR #1271 — Remediation Redesign** ($9/day saved)
   - Disabled 3 Celery Beat execution schedules (CodeGeneratorAgent running in empty sandbox)
   - Kept discovery/assignment schedules (findings are real and valuable)
   - Created `show_remediation_findings` management command
   - Cancelled 79 stuck tasks, reset 69 findings to 'open' in Railway DB

2. **PR #1272 — UserProfile Duplicate Fix**
   - Renamed `unified_storage.UserProfile` to `StorageUserProfile` (prevented RuntimeError)
   - Fixed broken import in `discord_bot.py` line 3489
   - Marked 6 AuditFindings as fixed

3. **PR #1273 — Agent Execution Waste** ($1.81/day saved)
   - Removed CodeGeneratorAgent from `run_development_tech_agents` (sandbox, can't write code)
   - Removed AudioAgent from `run_content_creation_agents` (ElevenLabs quota exceeded, 100% failure)
   - Rewrote WorkflowAgent task — old task spawned ~30 unbounded ResearchAgent sub-tasks/day
   - Rewrote OpportunityPipelineAgent task — old task triggered "no revenue" assessment 51x/day

**Key files:**
- `core/celery.py` — 3 execution schedules disabled
- `core/tasks.py` — Agent groups cleaned up, bounded tasks
- `core/unified_storage.py` — StorageUserProfile rename
- `core/management/commands/show_remediation_findings.py` — NEW

See `docs/handoffs/SESSION_1027_AGENT_EXECUTION_AUDIT.md`

---

## Session 1025 Summary

### Scoring Contract: Reach, Intent & Replicability (PRs #1267, #1268, #1269)

- Added 5 new fields to `SignalCluster` + rule-based `ContentScoringService`
- 1,573 clusters scored: attention=604, intent=169, unclassified=800
- See `docs/handoffs/SESSION_1025_SCORING_CONTRACT.md`

---

## Session 1024 Summary

### Semantic Spider Search — Root Cause Fix (PR #1265)

- `search_spider_data()` replaced keyword matching with pgvector semantic similarity (primary), keyword fallback
- See `docs/handoffs/SESSION_1024_SEMANTIC_SPIDER_SEARCH.md`

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 92 (54 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 397+ |
| Services | 135 |
| Celery Tasks | 269 (3 remediation execution schedules disabled) |
| Intelligence Desks | 4 (Stocks, Sports, Blockchain, Narrative) — ALL RUNNING |
| Workspace Tabs | 9 |
| Frontend Routes | 27 |
| Agents Persisting Output | 43 (via `_save_to_deliverable()` with 4h dedup) |
| PA Tools | 97 |
| PA Intents | 39 |
| Enrichment Services | 8 |
| Sports Leagues | 6 with predictions (NCAAB, NHL, EPL, La Liga, MLS, NCAAF) |
| Active Initiatives | 3 (Stage 2, IN_REVIEW) + 1 TRIAGE |
| Blogs | 497 |
| Signal Clusters | 1,573 (all scored: 604 attention, 169 intent, 800 unclassified) |
| Deliverables | ~3,737 (cleaned from 9,577) |
| Daily LLM Cost | ~$6/day (down from $17/day) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Spider Search | Semantic (pgvector KNN) primary, keyword fallback |
| Evidence Gates | 4 layers complete (Layers 1-3 defensive + root cause fix) |
| Scoring Contract | Live — reach/intent/replicability/source_confidence/track on all clusters |

---

## Verify Before Starting

### 1. Cost Reduction (Session 1027)
- Verify agent execution waste is eliminated:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentExecution
  from django.utils import timezone; from datetime import timedelta
  from django.db.models import Sum
  since = timezone.now() - timedelta(hours=24)
  execs = AgentExecution.objects.filter(created_at__gte=since)
  total_cost = execs.aggregate(c=Sum('cost'))['c'] or 0
  print(f'Total: {execs.count()} runs, \${total_cost:.2f}')
  for name in ['CodeGeneratorAgent', 'AudioAgent', 'OpportunityScoringAgent', 'ResearchAgent']:
      count = execs.filter(agent__name=name).count()
      cost = execs.filter(agent__name=name).aggregate(c=Sum('cost'))['c'] or 0
      print(f'  {name}: {count} runs, \${cost:.2f}')
  "
  ```
- Expect: CodeGeneratorAgent=0, AudioAgent=0, OpportunityScoringAgent<10, total cost<$8

### 2. Semantic Search Health (Session 1024)
- Verify semantic search is active (NOT falling back to keyword):
  ```
  railway run python manage.py shell -c "
  from core.services.spider_intelligence import SpiderIntelligenceService
  svc = SpiderIntelligenceService()
  results = svc.search_spider_data('blockchain security vulnerabilities', limit=3)
  print(f'Results: {len(results)}')
  for r in results:
      print(f'  {r[\"source\"]:20} rel={r[\"relevance\"]:.3f} terms={r[\"matching_terms\"]}')
  print()
  print('PASS' if results and results[0]['matching_terms'] == ['semantic_match'] else 'FAIL - using keyword fallback')
  "
  ```
- Expect results with `matching_terms=['semantic_match']`, NOT keyword terms

### 3. Deliverable Count (Session 1022)
- Verify deliverable count stabilized:
  ```
  railway run python manage.py shell -c "
  from core.models_deliverables import Deliverable
  from django.utils import timezone; from datetime import timedelta
  last_24h = Deliverable.objects.filter(created_at__gte=timezone.now()-timedelta(hours=24)).count()
  total = Deliverable.objects.count()
  print(f'New deliverables (24h): {last_24h}')
  print(f'Total deliverables: {total}')
  "
  ```
- Expect ~150-300 new/day (down from 1,500+)

### 4. Scoring Contract (Session 1025)
- Verify clusters are being scored on creation:
  ```
  railway run python manage.py shell -c "
  from core.models import SignalCluster
  for track in ['attention', 'intent', 'unclassified']:
      count = SignalCluster.objects.filter(track=track).count()
      print(f'{track}: {count}')
  "
  ```
- Expect non-zero counts for all three tracks

---

## Known Issues / Open Items

### Evidence Pipeline Maturity Roadmap
1. Semantic spider search — DONE (Session 1024, PR #1265)
2. Evidence gates (4 layers) — DONE (Session 1023, PRs #1262-1264)
3. Scoring contract (reach, intent, replicability) — DONE (Session 1025)
4. Auto-experiment generator — FUTURE

**Next within this roadmap:** Track-based routing (consuming `SignalCluster.track` to route attention-track signals to content agents and intent-track signals to micro-product agents). Backfill complete — all 1,573 clusters scored.

### Evidence Gate Layer 3b — Per-Agent Adoption
Each of 20+ provenance-tracked agents should compute `domain_match_rate` and pass it to `build_provenance()`. Currently only CompetitorAnalysisAgent and BaseBusinessResearchAgent subclasses enforce evidence gates. The `build_provenance()` infrastructure is ready (Session 1023, PR #1264).

### Rubber-Stamped Initiatives — NEEDS AUDIT
Initiatives that reached Stage 5 via the skip-ahead bug (PR #1251) have Stage 3-5 docs generated out of order with no real data. May need doc regeneration.

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Remediation System — REDESIGNED (Session 1026/1027)
Discovery + assignment still running (finds real issues). Execution disabled — CodeGeneratorAgent was burning $9/day in empty sandbox. 80 open findings now surfaced via:
```
railway run python manage.py show_remediation_findings
railway run python manage.py show_remediation_findings --priority P0 P1
railway run python manage.py show_remediation_findings --verbose --limit 10
```
Fix findings in Claude Code sessions, then mark: `AuditFinding.objects.filter(id="<uuid>").update(status="fixed", fixed_by="Session XXXX")`
See `docs/handoffs/SESSION_1026_REMEDIATION_REDESIGN.md`

### Agent Group Schedules — MAPPED (Session 1027)
19 agent group schedules drive all automated agent executions. Full map in `docs/handoffs/SESSION_1027_AGENT_EXECUTION_AUDIT.md`. Key pattern: `_run_agent_group()` (tasks.py:30247) calls `universal_agent_workspace_output()` for each agent. To stop an agent from running, remove it from its group list.

### Dream Pipeline — NO-OP
Zero approved dreams, zero DreamImplementations. Only $0.54/day so not urgent, but the entire dream->implementation pipeline is non-functional.

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
- Agent execution waste: **FIXED** (PR #1273)
- UserProfile duplicates: **FIXED** (PR #1272)
- Evidence gate (irrelevant data): **FIXED** (PRs #1262-#1265)
- AudioAgent: **REMOVED from schedule** (PR #1273, ElevenLabs quota)
- Remaining: assorted agent failures (~18/day, low cost)

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

**Agent group schedules (Session 1027):**
- 19 schedules in `core/celery.py` drive all automated agent runs
- All use `_run_agent_group()` (tasks.py:30247) -> `universal_agent_workspace_output()`
- To stop an agent: remove from its group list in `run_*_agents()` function
- Unbounded task descriptions ("check and advance", "review and prioritize") cause sub-task spawning
- Bounded tasks ("report summary only, do NOT delegate") prevent cascading execution

**django_celery_beat DB persistence (Session 1027):**
- Commenting out schedule definitions in `celery.py` does NOT disable DB-persisted schedules
- Must also run: `PeriodicTask.objects.filter(name='...').update(enabled=False)`

**Spider search (Session 1024):**
- `search_spider_data()` uses pgvector semantic similarity (primary) -> keyword matching (fallback)
- Key file: `core/services/spider_intelligence.py`
- Constants: `SEMANTIC_TOP_K=50`, `SEMANTIC_MIN_SIMILARITY=0.25`, `NOISY_SPIDERS`
- Monitor logs for `[spider_search] keyword fallback` — should NOT appear in normal operation

**Scoring contract (Session 1025):**
- `SignalCluster` has `reach_score`, `intent_score`, `replicability_score`, `source_confidence`, `track`
- `ContentScoringService` in `core/services/content_scoring_service.py` — rule-based, no LLM
- Auto-applied in `SignalAggregationService._create_signal_clusters()` via `_apply_scores()`
- Track values: `'attention'` (content), `'intent'` (micro-products), `'unclassified'`

**Agent model confusion (Session 1022):**
- `core.models_unified_system.Agent` — has `name`, used by `AgentExecution` FK
- `core.models.agents_registry.Agent` — has `display_name`, used by agent registry
- Always use `.name` for `AgentExecution.agent` — NOT `.display_name`

**Deliverable dedup (Session 1022):**
- `_save_to_deliverable()` checks 4-hour window by `title` + `agent_name`
- If match found, updates existing row instead of creating new

**Conversation dedup (Session 1022):**
- Both `run_agent_conversation` and `run_multi_agent_conversation` check 6-hour window
- Dedup on both `related_knowledge` FK and topic string
- Only applies to `trigger_type='scheduled'` conversations

**Initiative pipeline (Session 1021):**
- `advance_initiative_pipeline` only processes `init.current_stage` — never scans ahead
- Prior stage must be `APPROVED` before current stage is processed
- `_gather_initiative_research()` queries SpiderData, SignalClusters, AgentConversations, Deliverables
- `TechnicalDocumentAgent` has NO tools — only works with data provided in prompt/context

**Initiative 6 creation paths (Session 1020):**
- All have circuit breaker + similarity dedup

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
