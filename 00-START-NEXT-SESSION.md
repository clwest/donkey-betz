# Session 991 - Start Here

**Previous Session:** 990 (PA-to-Agent Content Feedback Loop)
**Date:** February 12, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** | **Workspace: 9 TABS** | **Bundle: 2,305 KB** | **Unified PA: ANALYTICAL ADVISOR** | **PA Tools: 93** | **PA Intents: 36** | **Content Feedback Loop: CLOSED** | **Reviewers: REAL VERDICTS**

---

## Session 990 Summary (Just Completed)

### PA-to-Agent Content Feedback Loop

Closed the feedback loop between PA content review decisions and originating agents. When the PA publishes, archives, or revises content, the decision is now recorded back to the originating agent via 3 mechanisms:

1. **AgentMemory** (type='feedback', tags=['pa_review']) -- agents see PA decisions in multi-agent conversations and future executions
2. **UserAgentLearning** -- per-user personalization (publish=success, archive=failure)
3. **FeedbackLoopEngine** -- `pa_review_feedback` and `pa_review_summary` in feedback context, extracted into `spider_context` by agent_router

**Files changed:** `tool_dispatcher.py` (new `_record_content_feedback()` + 3 call sites), `feedback_loop_engine.py` (PA review query), `agent_router.py` (context extraction)

No new models, no migrations, no new Celery tasks. Uses existing AgentMemory, UserAgentLearning, and context injection pipeline.

### Session 989 Summary (Prior)

### Production Verification (5 open items from Session 988)

All 5 items verified on Railway production (`donkey-betz-platform-production.up.railway.app`):

1. **Content Reviewers: VERIFIED** - SkepticReviewer returned real REVISE verdict (not synthetic FAIL). FactCheckReviewer ran. 14 claims, 14 sources, 1 revision pass. Import fix confirmed working.

2. **Execution History: VERIFIED** - "What have agents been doing?" returns 20 executions + 20 conversations. Required 3 additional fixes (see below).

3. **Crypto Price: VERIFIED** - "How much is BTC?" routes correctly to spider_data_tool. Query succeeds (0 items — CoinGecko spider not crawled recently). No field errors.

4. **Celery Prefork: INCONCLUSIVE** - Config correct (`--max-tasks-per-child=50`), but workers only processed ~15 tasks since deploy. Recycling threshold not yet reached.

5. **Muscular System: VERIFIED** - Status is "fit" (not 60.5%). Some groups paralyzed due to low volume.

### Production Bug Fixes (3 commits)

**SpiderData Wrong Field Names:** `_handle_spider_data` in tool_dispatcher.py referenced `title`, `url`, `category`, `content` which don't exist on SpiderData. Fixed to use `source_url`, `data_type`, `embedding_text`.

**Execution History Missing Payload:** `_build_tool_payload()` had no `execution_history` case — default `action='list'` was sent (invalid). Added payload builder with action detection.

**AgentExecution FK Field Names:** `AgentExecution.agent` is a FK to Agent, not a CharField. Handler used `agent_name` and `success` (both non-existent). Fixed to `agent__name` (FK traversal) and `status='completed'`/`'failed'`.

**DeliberationSession Participants:** `participants` JSONField contains dicts, not strings. `', '.join()` on dicts threw TypeError. Fixed to extract `name` key before joining.

### Railway Deployment Gotcha Discovered

Each Procfile process (`web`, `celery-pa`, `celery-worker`, etc.) is a **SEPARATE Railway service**. `railway up` only deploys the linked service. `railway redeploy` re-runs the last build (old code if new build was in progress). GitHub push auto-deploys ALL services. Always verify celery-pa has the latest code.

### Session 988 Summary (Prior)

Initiative modal overflow, content reviewer import fix, PA initiative routing, agent stale data grounding, execution history formatter, crypto price intent, capabilities narrowing.

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
| PA Tools | 92 |
| PA Intents | 36 (added crypto_price, narrowed capabilities) |
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
