# Session 995 - Start Here

**Previous Session:** 994B (Initiative Pipeline Fixes — Stop the Bleeding)
**Date:** February 12, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **INITIATIVE PIPELINE: CIRCUIT BREAKER ENFORCED + TRIAGE STATUS + QUALITY GATE** | **Workspace: 9 TABS** | **Bundle: 2,305 KB** | **Unified PA: ANALYTICAL ADVISOR** | **PA Tools: 95 (added flow_metrics)** | **PA Intents: 37** | **Enrichment Services: 8** | **Context Layers: 11** | **Content Feedback Loop: CLOSED** | **Stock Predictions: FIXED** | **Podcast User Context: FIXED**

---

## Session 994B Summary (Just Completed)

### Initiative Pipeline Fixes — Stop the Bleeding

Production showed 158 active initiatives, ALL with `last_activity_at=None`, 64 created in 24h despite circuit breaker threshold of 50. Root cause: `InitiativeIntegrationService` bypassed the circuit breaker entirely.

**6 fixes implemented:**
1. **Circuit breaker enforcement** — `InitiativeIntegrationService.get_or_create_initiative()` now checks circuit breaker. Added `InitiativeCreationBlocked` exception caught by `DecisionExtractor` and `link_action_to_initiative`.
2. **Quality gate** — `_quality_gate()` in `ConversationInitiativePipeline` rejects exploratory conversations (20 explore patterns) and requires action verbs + substantive content (1000+ chars).
3. **TRIAGE status** — ALL auto-created initiatives start as TRIAGE, not ACTIVE. Migration `0238`. PA can update TRIAGE status.
4. **Intent-aware spawning** — Exploratory topics filtered by quality gate.
5. **Activity tracking** — `update_activity()` now called from `stage.approve()`, `generate_initiative_stage_document`, `handle_stage_task_completion`, and `process_initiative_auto_progression`. Previously only called from conversations.
6. **PA flow_metrics** — New `flow_metrics` action on `initiative_tool` shows creation rate, backlog, stage distribution, circuit breaker status.

**Files changed:** 10 files, 1 migration. See `docs/handoffs/SESSION_994B_INITIATIVE_PIPELINE_FIXES.md`.

## Session 994 Summary (Prior)

### Fix Stock Prediction Pipeline + Podcast User Context

Fixed two broken subsystem pipelines discovered via PA conversations on Railway production.

**Stock Prediction Pipeline** (`market_intelligence_coordinator.py`):
- `_parse_target_move()` crashed on numeric types from GPT JSON — added type safety for int/float inputs
- `_record_predictions_for_learning()` had single try/except around entire loop — one bad ticker killed ALL predictions for the brief. Added per-iteration error handling.

**Podcast Pipeline** (`tasks.py`):
- `PodcastCoordinatorAgent(user=episode.user)` — enables learning hooks, memory attribution, feedback recording

## Session 993 Summary (Prior)

### PA Capability Gaps: Write Actions + Blog Triage + V2 Generation

Added 11 new write actions across PA tools — the PA can now modify data, not just read it.

**Bulk Blog Triage + Publish/Archive** (5 new actions in `_handle_blog_query`):
- `triage` — groups ALL blogs into 3 quality tiers (publish-ready, needs-revision, archive-candidates)
- `publish` / `archive` — single blog publish/archive with content feedback recording
- `batch_publish` / `batch_archive` — bulk operations capped at 50 per call

**V2 Blog Generation** (new `generate_blog_tool` handler):
- With topic: runs `ContentDeliberationRunner.run_blog()` synchronously (full deliberation pipeline)
- Without topic: dispatches `generate_self_blog_deliberation_task` to Celery
- New intent: "generate a blog", "v2 blog", "deliberated blog", "generate content"

**Write Actions for Read-Only Tools** (5 new actions):
- `initiative_tool`: update_status, advance (next pipeline stage), complete_action_item
- `opportunity_manager_tool`: update_status
- `spider_data_tool`: trigger (dispatch spider run by category)

**Files changed:** `tool_dispatcher.py` (~200 lines added), `unified_pa_entrypoint.py` (12 lines added)

No new models, no migrations, no new Celery tasks, no frontend changes.

### Session 992 Summary (Prior)

Wire 3 Remaining Unwired Services — DynamicTeamBuilder, PlatformIntelligenceBriefingService, PlatformIntegration.

### Session 991 Summary (Prior)

Wire ProactiveIntelligenceService + AgentLearningService into execution paths.

### Session 990 Summary (Prior)

Closed PA-to-Agent content feedback loop. When PA publishes/archives/revises content, the decision is recorded back to the originating agent via AgentMemory, UserAgentLearning, and FeedbackLoopEngine.

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
