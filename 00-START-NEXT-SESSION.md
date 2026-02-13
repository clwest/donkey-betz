# Session 999 - Start Here

**Previous Session:** 998B (Live Scores + AI Predictions)
**Date:** February 12, 2026
**Status:** 79 Agents | 79 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **SPORTS BETTING PIPELINE: LIVE** | **LIVE SCORES + AI PICKS** | **BETTING HUB: LIVE** | **Workspace: 9 TABS** | **Unified PA: ANALYTICAL ADVISOR** | **PA Tools: 97** | **PA Intents: 38** | **Enrichment Services: 8** | **Content Feedback Loop: CLOSED** | **Celery Tasks: 264** | **GOVERNANCE: HARDENED**

---

## Session 998B Summary (Just Completed)

### Live Scores + AI Predictions on Today's Games

Today's Games tab now shows live scores for in-progress games and odds-consensus AI predictions with W/L outcome tracking.

**Spider fix:** `TheOddsSpider.fetch_scores()` no longer filters out in-progress games — returns both completed and live games with scores.

**AI Predictions:** Replaced broken `MLPrediction` DB lookup with inline odds-implied probability calculation. `_american_to_probability()` converts American moneyline odds → picks favorite > 55%. Completed games track `prediction_correct: True/False`.

**Frontend:** Live games show scores, AI Pick banners change color (green W / red L / purple pending), stats row shows Live / AI Picks / Completed / Upcoming.

**Files changed:** 3 files. See `docs/handoffs/SESSION_998B_BETTING_HUB_LIVE_SCORES.md`.

### Earlier in 998B: Betting Hub + Odds Table Fix

- Sports Betting Hub tab with news/injury feed (2 new spiders: SportsNewsSpider, SportsInjurySpider)
- Migration `0241` recreated missing odds tables on Railway
- Guarded PA conversations against None values

## Session 998 Summary (Prior)

### System Governance Hardening

PublishGate now blocks publishing when `publish_ready=False`. SelfBlog.author tracks creation source. New 'reviewer' platform_role with read-only middleware enforcement. Migration `0240`. See `docs/handoffs/SESSION_998_GOVERNANCE_HARDENING.md`.

## Session 997B Summary (Prior)

### Podcast Cleanup + Boardroom Preview + Betting Sidebar

Podcast tab cleaned up (removed ChannelEpisode noise, inline generation). Boardroom summary preview + betting sidebar. Backfill initiative owners management command. PA 'review' keyword routing fix. See `docs/handoffs/SESSION_997B_PODCAST_BOARDROOM_BETTING_SIDEBAR.md`.

## Session 997 Summary (Prior)

### Mythology Validation for PA Responses + PublishGate Scoring

Wired mythology services into PA responses (risk flagging + disclaimers) and PublishGate (new mythology_score dimension). See `docs/handoffs/SESSION_997_MYTHOLOGY_PUBLISHGATE.md`.

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 79 (52 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 79 (74 working, 5 need API keys) |
| Advisors | 25 |
| Database Models | 391+ |
| Services | 134 |
| Celery Tasks | 264 |
| Workspace Tabs | 9 |
| Frontend Routes | 37 (15 standalone + 22 redirects) |
| PA Tools | 97 |
| PA Intents | 38 |
| Enrichment Services | 8 |
| Attention Sections | 7 |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Migrations | Through 0241 |
| Standalone Pages | `/stocks`, `/advisors`, `/betting`, `/neural-orchestra`, `/conversation-contract`, `/mythology-lab`, `/billing`, `/analytics`, `/docs-index` |

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
Many items remain from the audit: agent output persistence, orphan endpoints, enrichment data loss.

---

## What Could Come Next

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

### Betting Prediction Tracking
Track AI pick accuracy over time. Dashboard showing hit rate by sport, confidence band performance.

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

**Initiative ownership (Session 996):**
- `owner` = FK to User (nullable), `owner_agent` = CharField (agent name)
- Only one should be set at a time (assign_owner clears the other)
- Auto-assigned via `PROGRAM_OWNER_MAP` or `created_by` at creation time

**Odds-consensus predictions (Session 998B):**
- `_american_to_probability()` in `views_odds_sports.py` — converts American odds to implied probability
- Only predicts when implied prob > 55%
- `prediction_correct` field: `True`/`False` for completed, `None` for pending

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
