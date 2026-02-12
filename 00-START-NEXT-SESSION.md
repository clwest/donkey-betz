# Session 993 - Start Here

**Previous Session:** 992 (Wire 3 Remaining Unwired Services)
**Date:** February 12, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** | **Workspace: 9 TABS** | **Bundle: 2,305 KB** | **Unified PA: ANALYTICAL ADVISOR** | **PA Tools: 93** | **PA Intents: 36** | **Enrichment Services: 8** | **Context Layers: 11** | **Content Feedback Loop: CLOSED** | **Reviewers: REAL VERDICTS**

---

## Session 992 Summary (Just Completed)

### Wire 3 Remaining Unwired Services

Connected three fully-built but unwired services (~1,330 lines combined) into the main execution paths:

**DynamicTeamBuilder** (610 lines) — now wired into ConversationOrchestrator:
- `_select_agents_for_topic()` tries `DynamicTeamBuilder.build_team()` first (embedding similarity + synergy scoring)
- Falls back to original `AgentRegistry` text matching on any exception
- Only fires for multi-agent conversations (`auto_select_agents=True`), not every `route()` call

**PlatformIntelligenceBriefingService** (472 lines) — now wired into PA enrichment pipeline:
- Added `platform_briefing` enrichment to 2 intents: `system_overview`, `execution_history`
- Aggregates 6 sources: knowledge transfers, conversations, dreams, boardroom, spider highlights, platform health
- Formatted as `=== PLATFORM ACTIVITY ===` section in analytical prompts
- Capped at 500 chars, respects relevance gate

**PlatformIntegration** (248 lines) — now wired into agent_router:
- `gather_context()` injects `platform_tools_directive` into `spider_context`
- "Use internal tools, not external services" prompt now reaches router-executed agents (previously only Celery-executed)

**Files changed:** `conversation_orchestrator.py` (3 edits), `unified_pa_entrypoint.py` (6 edits), `agent_router.py` (3 edits)

No new models, no migrations, no new Celery tasks, no frontend changes.

### Session 991 Summary (Prior)

### Wire ProactiveIntelligenceService + AgentLearningService

Connected two fully-built but uncalled services (~1,300 lines combined) into the main execution paths:

**ProactiveIntelligenceService** (545 lines) — now wired into the PA enrichment pipeline:
- Added `proactive_intelligence` enrichment to 4 intents: `opportunities`, `stock_intelligence`, `content_review`, `system_overview`
- Queries SpiderData, TriggerEvent, BlockchainSecurityAlert, Opportunity, MarketIntelligenceBrief
- Formatted as `=== PROACTIVE INTELLIGENCE ===` section in analytical prompts
- Capped at 500 chars, respects relevance gate for non-direct intents

**AgentLearningService** (778 lines) — now wired into the agent router:
- Records every `route()` execution via `record_interaction()` (Redis-based, success or failure)
- Injects adaptive preferences via `get_adaptive_context()` into `user_context['agent_learned_preferences']`
- Surfaced through `gather_context()` into `spider_context` so agents see learned preferences
- All calls wrapped in try/except — never breaks execution

**Files changed:** `unified_pa_entrypoint.py` (6 edits), `agent_router.py` (4 edits)

No new models, no migrations, no new Celery tasks, no frontend changes.

### Session 990 Summary (Prior)

Closed PA-to-Agent content feedback loop. When PA publishes/archives/revises content, the decision is recorded back to the originating agent via AgentMemory, UserAgentLearning, and FeedbackLoopEngine.

### Session 989 Summary (Prior)

Production verification of 5 open items. Fixed SpiderData field names, execution history payload, AgentExecution FK traversal, DeliberationSession participants extraction. Discovered Railway multi-service deployment gotcha.

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
| PA Tools | 93 |
| PA Intents | 36 |
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

---

## What Could Come Next

### Fix chat_conversations.platform Migration
Create migration for the missing `platform` column to fix PA conversation persistence.

### Fix Profile Loading Async Issue
Wrap profile loading in `sync_to_async` or use thread pool to avoid async context errors.

### Content Deliberation v2 via PA
`POST /api/v1/research/self-blog/generate-v2/` exists but PA can't trigger it. Add intent for "create blog with full review" / "deliberated blog".

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
