# Session 1025 - Start Here

**Previous Session:** 1024 (Semantic Spider Search — Root Cause Fix for Evidence Gates)
**Date:** February 17, 2026
**Status:** 92 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **497 BLOGS** | **1,488 SIGNAL CLUSTERS** | **Workspace: 9 TABS** | **PA Tools: 97** | **PA Intents: 39+** | **Enrichment Services: 8** | **ALL 4 DESKS RUNNING (5/5 SPORTS AGENTS)** | **43 AGENTS PERSIST TO DELIVERABLE** | **Celery Tasks: 268** | **Frontend Routes: 27** | **6 Sports Leagues w/ Predictions** | **SPORTS PIPELINE 100% AUTOMATED** | **BETTING DASHBOARD: 12 TABS POLISHED** | **DELIVERABLE DEDUP: LIVE** | **CONVERSATION DEDUP: LIVE** | **REMEDIATION SYSTEM: PAUSED** | **COST SAVINGS: ~$14/day** | **SEMANTIC SPIDER SEARCH: LIVE** | **EVIDENCE GATES: COMPLETE (4 LAYERS)**

---

## Session 1024 Summary (Just Completed)

### Semantic Spider Search — Root Cause Fix (PR #1265)

**Problem:** `search_spider_data()` used word-boundary regex keyword matching over 300 most recent SpiderData rows. A HuggingFace ML page mentioning "blockchain" in a tag scored `relevance=1.0` for blockchain queries, drowning out actual blockchain data. This was the root cause behind all evidence gate work.

**Fix:** `core/services/spider_intelligence.py` — `search_spider_data()` now uses pgvector `CosineDistance` semantic similarity as the primary search path, with keyword matching as automatic fallback only.

**Architecture:**
- `search_spider_data()` → `_semantic_search_db()` (primary) → `_keyword_search()` (fallback)
- Generates query embedding via `SpiderSemanticSearch._generate_embedding()` (OpenAI `text-embedding-3-small`)
- DB-side KNN using HNSW index (`spiderdata_embedding_hnsw_idx`)
- Filters by `similarity >= 0.25`, returns top 50 results
- Falls back to keyword matching when: pgvector ImportError, embedding API fails, no embedded data, any DB error

**All 6 callers benefit automatically** — no code changes needed: `base_agent.py` spider_query, `base_business_research_agent.py`, `spider_context_builder.py`, `research_agent.py`, `views_spider_intelligence.py`, `context_aggregator.py`.

**Verified on Railway:** 85% embedding coverage. Crypto queries return etherscan data, not huggingface. No keyword fallback in normal operation.

See `docs/handoffs/SESSION_1024_SEMANTIC_SPIDER_SEARCH.md`

---

## Session 1023 Summary

### Evidence Gate Layers 1-3 (PRs #1262, #1263, #1264)

- **Layer 1:** CompetitorAnalysisAgent hard gates (< 3 data points or 0% domain match → `insufficient_evidence`)
- **Layer 2:** BaseBusinessResearchAgent gate (affects ContentStrategy, MarketingStrategy)
- **Layer 3:** `build_provenance()` infrastructure (`domain_match_rate` param, < 15% blocks publishing)
- See `docs/handoffs/SESSION_1023_EVIDENCE_GATE_LAYERS.md`

---

## Session 1022 Summary

### Cost Optimization Audit (PRs #1253-#1258)

- Deliverable dedup (4h window), conversation dedup (6h window), remediation paused, agent execution 500 fix
- See `docs/handoffs/SESSION_1022_COST_OPTIMIZATION_AUDIT.md`

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 92 (54 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 396+ |
| Services | 134 |
| Celery Tasks | 268 (5 remediation schedules paused) |
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
| Signal Clusters | 1,488 |
| Deliverables | ~3,737 (cleaned from 9,577) |
| Daily LLM Cost | ~$13/day → expected ~$6/day after fixes |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Spider Search | Semantic (pgvector KNN) primary, keyword fallback |
| Evidence Gates | 4 layers complete (Layers 1-3 defensive + root cause fix) |

---

## Verify Before Starting

### 1. Semantic Search Health (Session 1024)
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

### 2. Cost Reduction (Session 1022)
- Verify deliverable count stabilized (should NOT grow by 1,500/day anymore):
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

### 3. Conversation Dedup (Session 1022)
- Verify conversation count dropped:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import AgentConversation
  from django.utils import timezone; from datetime import timedelta
  cutoff = timezone.now() - timedelta(hours=24)
  topics = list(AgentConversation.objects.filter(started_at__gte=cutoff).values_list('topic', flat=True))
  unique = len(set(topics))
  print(f'Conversations (24h): {len(topics)}, Unique: {unique}, Dupe rate: {1 - unique/max(len(topics),1):.0%}')
  "
  ```
- Expect <150 total, <20% dupe rate (down from 293 / 59%)

### 4. Embedding Coverage (Session 1024)
- Check embedding backfill is running:
  ```
  railway run python manage.py shell -c "
  from core.models_unified_system import SpiderData
  from django.utils import timezone; from datetime import timedelta
  since = timezone.now() - timedelta(hours=72)
  total = SpiderData.objects.filter(created_at__gte=since).count()
  with_emb = SpiderData.objects.filter(created_at__gte=since, embedding__isnull=False).count()
  print(f'SpiderData (72h): {total} total, {with_emb} with embeddings ({100*with_emb//max(total,1)}%)')
  "
  ```
- Expect >80% coverage

---

## Known Issues / Open Items

### Evidence Pipeline Maturity Roadmap
1. Semantic spider search — DONE (Session 1024, PR #1265)
2. Evidence gates (4 layers) — DONE (Session 1023, PRs #1262-1264)
3. Scoring contract (reach, intent, replicability) — DONE (Session 1025)
4. Auto-experiment generator — FUTURE

**Next within this roadmap:** Track-based routing (consuming `SignalCluster.track` to route attention-track signals to content agents and intent-track signals to micro-product agents). Run `backfill_signal_scores` on Railway to score existing 1,488 clusters.

### Evidence Gate Layer 3b — Per-Agent Adoption
Each of 20+ provenance-tracked agents should compute `domain_match_rate` and pass it to `build_provenance()`. Currently only CompetitorAnalysisAgent and BaseBusinessResearchAgent subclasses enforce evidence gates. The `build_provenance()` infrastructure is ready (Session 1023, PR #1264).

### Rubber-Stamped Initiatives — NEEDS AUDIT
Initiatives that reached Stage 5 via the skip-ahead bug (PR #1251) have Stage 3-5 docs generated out of order with no real data. May need doc regeneration.

### PA Context Awareness — NEEDS WORK
PA doesn't understand page context. When user says "I just created an image but it's not displaying" from Image Studio, PA asks generic clarifying questions instead of checking ImageHistory.

### Remediation System — PAUSED (Session 1022)
All 5 Celery Beat schedules commented out. 86 tasks in DB contain some valuable findings:
- `_calculate_error_rate()` always returns 0.0
- Multiple `AgentExecution` models across modules
- `core/tasks.py` is 12,000+ lines
- 1,200+ endpoints without docs
Re-enable when agents have real workspace access. Consider surfacing valuable findings via HumanAttentionItem/Boardroom.

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
- Remediation waste: **FIXED** (PR #1257)
- Evidence gate (irrelevant data): **FIXED** (PRs #1262-#1265)
- Remaining: AudioAgent (ElevenLabs quota, ~7/day), assorted others (~18/day)

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

**Spider search (Session 1024):**
- `search_spider_data()` uses pgvector semantic similarity (primary) → keyword matching (fallback)
- Key file: `core/services/spider_intelligence.py`
- Constants: `SEMANTIC_TOP_K=50`, `SEMANTIC_MIN_SIMILARITY=0.25`, `NOISY_SPIDERS`
- Monitor logs for `[spider_search] keyword fallback` — should NOT appear in normal operation

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
