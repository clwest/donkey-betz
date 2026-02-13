# Session 996 - Start Here

**Previous Session:** 995 (Betting Outcome Verification + Learning Loop)
**Date:** February 12, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **BETTING OUTCOME VERIFICATION: LIVE** | **Workspace: 9 TABS** | **Bundle: 2,305 KB** | **Unified PA: ANALYTICAL ADVISOR** | **PA Tools: 95** | **PA Intents: 37** | **Enrichment Services: 8** | **Context Layers: 11** | **Content Feedback Loop: CLOSED** | **Celery Tasks: 262**

---

## Session 995 Summary (Just Completed)

### Betting Outcome Verification + Learning Loop

Closed the feedback loop for sports betting. Previously, PlacedWagers sat in `pending` forever, watched HumanAttentionItems never got verified, and no outcomes fed into learning.

**5 changes:**
1. **TheOddsSpider `fetch_scores()`** — Fetches completed game scores from `/v4/sports/{sport}/scores`. Same event_id as odds data.
2. **BettingOutcomeVerifier** (NEW service) — Finds pending wager legs (3h+ after commence), watched arb items. Batch-fetches scores per sport. Settles wagers (single + parlay), verifies arb items, creates learning records.
3. **`verify_betting_outcomes` task** — Celery task with retry, also recalculates BettingStats.
4. **Beat schedule** — Every 2h at :15 via `crontab(hour='*/2', minute='15')`.
5. **Learning bridge** — `record_wager_outcome()` (SportsOddsAnalyst → UserAgentLearning + AgentMemory) and `record_arbitrage_outcome()` (ArbitrageDetector → UserAgentLearning + AgentMemory).

**Files changed:** 5 files (1 new). No models, no migrations. See `docs/handoffs/SESSION_995_BETTING_OUTCOME_VERIFICATION.md`.

## Session 994B Summary (Prior)

### Initiative Pipeline Fixes — Stop the Bleeding

6 fixes: circuit breaker enforcement, quality gate, TRIAGE status, intent-aware spawning, activity tracking, PA flow_metrics. See `docs/handoffs/SESSION_994B_INITIATIVE_PIPELINE_FIXES.md`.

## Session 994 Summary (Prior)

### Fix Stock Prediction Pipeline + Podcast User Context

Fixed `_parse_target_move()` type safety + per-iteration error handling. Added `PodcastCoordinatorAgent(user=episode.user)`.

## Session 993 Summary (Prior)

### PA Capability Gaps: Write Actions + Blog Triage + V2 Generation

11 new write actions across PA tools, bulk blog triage, V2 blog generation via deliberation pipeline.

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 76 (49 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 77 (72 working, 5 need API keys) |
| Advisors | 25 |
| Active Initiatives | 52 (cleaned from 568 in Session 961c) |
| Database Models | 391+ (added CeleryTaskEvent) |
| Services | 134 |
| Celery Tasks | 262 |
| Workspace Tabs | 9 (down from 18) |
| Frontend Bundle | 2,305 KB |
| Frontend Routes | 37 (15 standalone + 22 redirects) |
| PA Tools | 94 |
| PA Intents | 37 |
| Enrichment Services | 8 (added platform_briefing in Session 992) |
| Attention Sections | 7 |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Standalone Pages | `/stocks`, `/advisors`, `/neural-orchestra`, `/conversation-contract`, `/mythology-lab`, `/billing`, `/analytics`, `/docs-index` |

---

## Known Issues / Open Items

### chat_conversations.platform Column Missing
`Failed to persist PA conversation: column chat_conversations.platform does not exist` — ChatConversation model has a `platform` field that hasn't been migrated. Create and run migration.

### Profile Loading in Async Context
`Failed to load profile: You cannot call this from an async context` — Profile loading fails in Celery PA worker. Need `sync_to_async` wrapper or thread-based approach.

### docs/USER_FEEDBACK_QUEUE.md Missing
Referenced by `docs_context_builder` as a critical doc but doesn't exist. Create it or remove from critical docs list.

### Agent Knowledge Freshness — Monitor Impact
14-day cutoff may be too aggressive. Monitor agent conversation quality.

### CoinGecko Spider Not Crawling
Crypto price intent works but returns 0 items. CoinGecko spider may need manual trigger or schedule check.

### Railway Deploy: Migration Lock Risk
`AddConstraint` during blue-green deploy can hang on lock.

### Legacy Routes Expire in ~2-4 Weeks
26 legacy routes redirect to workspace tabs. Remove after transition period.

### Billing + Analytics Orphaned
`/billing` and `/analytics` need an Admin tab.

### ToolCallRecord Analytics Dashboard
Data is flowing but no dashboard exists yet.

### FailureSignature Table Empty
Diagnostic pipeline (Session 856) has 0 records. May need activation.

### Disconnected Dots Audit (Session 972) — Ongoing
Many items remain from the audit: agent output persistence, orphan endpoints, enrichment data loss. Podcast user context fixed in 994. Stock predictions fixed in 994. Continue working through the list.

---

## What Could Come Next

### Verify Stock Prediction Fix on Railway
After deploy, check PredictionOutcome records from the next MarketIntelligenceCoordinator run to confirm non-zero `predicted_move` values.

### Verify Podcast Fix on Railway
Trigger a podcast generation and confirm user attribution in PodcastEpisode and agent execution records.

### Continue Disconnected Dots Audit
Session 972 identified ~200+ items. High-impact remaining items:
- Agent output persistence (ResearchAgent, ImageAgent, TrendAnalysisAgent outputs vanish)
- DecisionEnforcerAgent has `DecisionRecord` model but wiring incomplete
- 85-95% enrichment data loss from truncation
- Orphan API endpoints with no frontend consumers

### Fix chat_conversations.platform Migration
Create migration for the missing `platform` column to fix PA conversation persistence.

### Fix Profile Loading Async Issue
Wrap profile loading in `sync_to_async` or use thread pool to avoid async context errors.

### Auto-Revision Loop
If deliberation pipeline returns REVISE verdict, loop back through EditorAgent automatically.

### Scheduled Task Visibility
PA has no visibility into Celery Beat scheduled tasks. Add `scheduled_tasks_tool`.

### Agent Introspection
PA can invoke agents but can't describe their capabilities. Add "what can [agent name] do?" intent.

### CoinGecko Spider Schedule
Ensure CoinGecko spider runs on schedule so crypto price queries return data.

### Ticker Lookup Enhancements
- Wire ticker lookup to PA: "look up AAPL"
- Historical price chart (sparkline)

### CeleryTaskEvent Analytics
Dashboard showing task stats, success rates, queue utilization.

### Admin Tab
Dedicated workspace tab for Billing, Analytics, system configuration.

### Code-Splitting
`React.lazy()` for workspace tabs — all 9 are in the main bundle.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`).

**SpiderData actual fields (Session 989):**
- `spider_name`, `source_url`, `data_type`, `raw_data`, `processed_data`, `embedding_text`, `relevance_score`, `insights`, `is_processed`, `is_actionable`, `created_at`, `processed_at`
- DO NOT use `title`, `url`, `category`, `content` (don't exist)

**AgentExecution fields (Session 989):**
- `agent` is FK to Agent — use `agent__name` in `.values()` and `agent__name__icontains` in filters
- No `success` field — use `status='completed'` / `status='failed'`
- No `agent_name` field

**DeliberationSession.participants (Session 989):**
- JSONField containing dicts (not strings)
- Extract `.get('name')` before `', '.join()`

**_parse_target_move() (Session 994):**
- GPT may return numeric types — always handled via isinstance check
- Per-iteration error handling in prediction recording loops

**Railway multi-service deployment (Session 989):**
- Each Procfile process is a SEPARATE Railway service
- `railway up` deploys only the linked service
- `railway redeploy` during a build cancels build and redeploys OLD code
- GitHub push auto-deploys ALL services
- To check a specific worker: `railway service link celery-pa` then `railway logs`

**Model registration:** Use `core/models/__init__.py` (NOT `core/models.py`). New model imports: `from ..models_xxx import ClassName` with `app_label = 'core'`.

**Celery pool on Railway:** `--pool=prefork -c 1` (Linux), `--pool=threads` (macOS).

**ML imports:** Always lazy (inside methods). Module-level loads ~800MB.

**LLM Provider Registry:** `from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest`

**PA intent routing:** More specific patterns BEFORE generic catch-alls. Always test new patterns against likely user questions.

**Model import paths:**
- `HeartBeat`: `core.models_heart` — `recorded_at`, `overall_status`
- `SpiderData`: `core.models_unified_system`
- `CeleryTaskEvent`: `core.models_celery_telemetry`
- `DeliberationSession`: `core.models_deliberation`

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30` (User: Donkeyking)
