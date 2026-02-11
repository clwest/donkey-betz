# Session 988 - Start Here

**Previous Session:** 987 (PA Wiring Completion)
**Date:** February 10, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** | **Workspace: 9 TABS** (down from 18) | **Bundle: 2,305 KB** | **26 Legacy Routes -> Redirects** | **Command Center "Now" Hub: ACTIVE** | **Page Telemetry: ACTIVE** | **Discord Docs: 112 COMMANDS** | **Unified PA: ANALYTICAL ADVISOR** | **PA Tools: 7 NEWLY WIRED** | **Blog Revision Loop: ACTIVE** | **Body Vitals Routing: FIXED** | **Phase 0-4 Deliberation: COMPLETE** | **Content Deliberation Pipeline: ACTIVE** | **PA Live Telemetry: ACTIVE** | **PA Status Snapshot: ACTIVE** | **Surgical Moves Verification: ACTIVE** | **ToolCallRecord: LIVE** | **Attention Coverage: 7 SECTIONS** | **PA Conversation History: ACTIVE** | **PA Async Processing: CELERY** | **Stock Intelligence Dashboard: ACTIVE** | **Stock Intelligence PA: WIRED** | **Ticker Lookup: ACTIVE** | **SKIN Layer Output: GITIGNORED** | **PA Production: FAST (3-64s)** | **Market Brief Save Guard: ACTIVE** | **Prediction Dedup: CONSTRAINED** | **Alert Quality: DEDUPED** | **Brief Detail UI: CARDS** | **Celery Telemetry: ACTIVE** | **Skin Ephemeral FS: FIXED** | **Boardroom Feeders: WIDENED** | **Celery Prefork: ACTIVE** | **PA Boardroom: ACTIONABLE** | **Nervous System: FIXED**

---

## Session 987 Summary (Just Completed)

### PA Wiring Completion

Three PRs (#1061, #1062) connecting disconnected PA capabilities:

**Blog Revision Feedback Loop (PR #1061):** PA can now say "revise blog [uuid]" to run EditorAgent with PublishGate editorial notes as focus areas, then re-score and show before/after quality comparison. Keywords: revise, improve, enhance, fix this blog, edit this blog, rewrite.

**7 Unrouted Tool Handlers Wired (PR #1062):** Connected revenue_tracker, task_manager, workspace, check_budget, system_alerts, ml_analysis, pipeline_orchestrator -- each with intent detection, payload builder, and formatted output.

**Blog Enhancement Actions (PR #1062):** `needs_work` lists blogs with `status='needs_enhancement'`; `batch_enhance` triggers bulk EditorAgent runs. Keywords: needs work, batch enhance, enhance all.

**Body Vitals Routing Fix (PR #1062):** Narrowed body vitals triggers from generic "health"/"status" to body-specific phrases. Generic "health" no longer hijacks system health queries.

**human_decisions_tool:** Confirmed redundant with boardroom_tool (superset). Left registered for old PA compatibility.

### Session 986 Summary (Prior)

Nervous System 60% Health Fix -- Redis URL string parsing in `_check_channel_layer()`, wired `_get_message_stats()` to CeleryTaskEvent, mild activity penalty. Railway 60% -> ~90-100%.

### Session 985 Summary (Prior)

PA Boardroom Response Improvement (top items inline, concise LLM directive) + Celery OOM Deep Fix (lazy ML imports). PRs #1049.

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
| PA Tools | 92 (7 newly wired in Session 987) |
| Attention Sections | 7 |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |
| Standalone Pages | `/stocks`, `/advisors`, `/neural-orchestra`, `/conversation-contract`, `/mythology-lab`, `/billing`, `/analytics`, `/docs-index` |

### 9-Tab Model

| Group | Tabs | Sub-tabs |
|-------|------|----------|
| Core | Command, Initiatives, Boardroom | -- |
| Content | Content Studio | gallery, channels, blogs, documents, podcast, distribution, dossiers, voices, files |
| System | System, Ops | health, services, llm, integration, monitor, workflows, hivemind, triggers |
| Data | Data & Intel, Knowledge, Learn | spiders, feed, learning, reasoning, safety, collective |

---

## Known Issues / Open Items

### Railway Deploy: Verify Celery Prefork
After deploy, monitor celery-worker memory over 4+ hours. Look for "child process exiting" messages in Railway logs confirming child recycling is working. If prefork causes issues, fall back to `--pool=solo` (single process, no concurrency, but does recycle).

### Railway Deploy: Migration Lock Risk
Migration 0234 showed that `AddConstraint` during blue-green deploy can hang on lock. For future migrations with exclusive locks, consider: (a) run migration manually before deploy, or (b) temporarily skip migrate in start command.

### Migration 0235 Needs Running on Railway
`CeleryTaskEvent` table must be created via `python manage.py migrate` on next deploy. No lock risk -- it's a simple `CreateModel`.

### Muscular System Score (60.5%) -- Agent Performance
Muscular health reflects actual agent execution success rates. Some agent groups may be hitting daily execution limits or running slow. Investigate `AgentExecution` records for underperforming groups.

### Legacy Routes Expire in ~2-4 Weeks
26 legacy routes redirect to workspace tabs. Telemetry counters track which routes still get traffic. After transition period, remove redirect routes entirely.

### Billing + Analytics Orphaned
`/billing` and `/analytics` are standalone pages with no home in the 9-tab model. Need an Admin tab or should be absorbed into an existing tab.

### Content Studio Has 9 Sub-tabs
Pushing visual limits -- consider "More" dropdown or grouping if adding more.

### ToolCallRecord Now Populating
Data is flowing but no analytics dashboard exists yet.

### FailureSignature Table Empty
The diagnostic pipeline (Session 856) has 0 records in production. May need activation.

---

## What Could Come Next

### Content Deliberation v2 via PA
`POST /api/v1/research/self-blog/generate-v2/` exists but PA can't trigger it. Add intent for "create blog with full review" / "deliberated blog". Would connect the full ClaimsPack -> 3-reviewer panel -> DecisionEnforcer pipeline to natural language.

### Auto-Revision Loop
If deliberation pipeline returns REVISE verdict, loop back through EditorAgent automatically instead of requiring manual re-trigger.

### Scheduled Task Visibility
PA has no visibility into Celery Beat scheduled tasks. Add `scheduled_tasks_tool` with "what's scheduled?", "automation status" intents.

### Agent Introspection
PA can invoke agents but can't describe their capabilities. Add "what can [agent name] do?" intent that returns agent class methods and supported actions.

### Post-Deploy Monitoring
- Verify celery-worker memory stays stable with prefork pool
- Verify Boardroom shows fresh attention items from widened feeders
- Check CeleryTaskEvent table is populated after migration 0235

### Body Health Improvements
- Investigate muscular system 60.5% -- which agent groups are underperforming?
- Verify nervous system score improved on Railway after deploy (was 60%, fix in Session 986)

### Ticker Lookup Enhancements
- Wire ticker lookup to PA: "look up AAPL" routes to ticker_lookup endpoint
- Add historical price chart (sparkline or mini chart component)
- Watchlist feature: save tickers, get notified on new alerts/predictions
- Compare mode: side-by-side view of two tickers

### Stock Intelligence v2
- PATCH endpoint for bookmark toggle and user notes on alerts
- Prediction accuracy dashboard with charts over time

### CeleryTaskEvent Analytics
- Dashboard showing task execution stats, success rates by task name, queue utilization
- Integrate with ToolCallRecord for end-to-end execution tracing

### Admin Tab
Create a dedicated workspace tab for Billing, Analytics, and system configuration pages.

### Code-Splitting
`React.lazy()` for workspace tabs -- currently all 9 tabs are in the main bundle. Lazy-loading could cut initial load significantly.

### Deep Sub-tab URLs
Support `?tab=system&sub=monitor` for direct deep-linking to specific sub-tabs.

### Sidebar Cleanup
Sidebar still shows `/mythology-lab` (now in DataIntel > Safety) and `/agents` (agents list accessible via workspace). Consolidate to match 9-tab model.

### Discord Command Pruning
Use the ACTIVE/DORMANT audit in `DISCORD_INTEGRATION.md` to remove or fix non-functional commands.

### ToolCallRecord Analytics
Build dashboards: tool usage by agent, latency percentiles, error rates.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`). Always use `DJANGO_SETTINGS_MODULE=core.settings`.

**Model registration:** Both `core/models.py` (file) and `core/models/` (package) exist. Django uses the **package** (`core/models/__init__.py`). New model imports must use `from ..models_xxx import ClassName` pattern with `app_label = 'core'` in Meta.

**Celery task counting:** DO NOT query `django_celery_results.TaskResult` -- it's empty when `CELERY_RESULT_BACKEND=redis`. Use `CeleryTaskEvent` from `core.models_celery_telemetry` instead.

**Celery pool on Railway (Sessions 984-985):**
- Procfile uses `--pool=prefork -c 1` (Linux-safe, enables child recycling via `max_tasks_per_child`)
- `--pool=threads` makes `max_tasks_per_child` a NO-OP (threads share one process)
- macOS local dev MUST use `--pool=threads` via Makefile (prefork causes SIGSEGV)
- `--max-memory-per-child=200000` (200MB) kills bloated children (300MB for long_running)

**ML imports MUST be lazy (Session 985):**
- NEVER `import torch`, `from sklearn`, `from transformers` at module level
- These load ~800MB into Celery parent process via: `core/assistant/` -> `personal_ai_assistant.py` -> `ml_engine.py`
- Always use `try/except ImportError` or import inside the method that uses them
- Follow the existing pattern in `_create_default_model` and `_initialize_nlp_models`

**Spider data_type values (Session 984):**
- Real types from `base_spider.py`: `opportunity`, `job_posting`, `market_data`, `competitor_info`, `trend_data`, `user_feedback`, `product_info`, `pricing_data`, `content_idea`, `collaboration`, `news`, `research`, `tool_discovery`, `learning_resource`
- Default fallback is `'research'`
- DO NOT use `market_alert`, `security_alert`, `price_alert`, `breaking_news` -- these don't exist

**Boardroom auto-approve (Session 984):**
- Items have 24h age gate before auto-approval (prevents stale Boardroom)
- `create_attention_item` has built-in dedup (source_type + item_type + title)

**PA boardroom response quality (Session 985):**
- `_handle_boardroom` stats action returns `top_items` (top 10 critical/high by priority_score)
- `_format_tool_result` shows items inline under "Needs your attention now"
- Boardroom LLM directive: "Max 3-5 bullets of INSIGHT only" -- do NOT restate counts
- To improve other PA intents, follow same pattern: enrich tool data + constrain LLM directive

**PA intent routing (Session 987):**
- 7 newly wired tools: revenue, task_management, workspace, budget, system_alerts, ml_analysis, pipeline_status
- Blog actions: `revise` (EditorAgent + PublishGate), `needs_work` (list needing enhancement), `batch_enhance` (bulk EditorAgent)
- Body vitals routing narrowed to body-specific phrases -- generic "health"/"status" no longer hijacks

**Workspace tab mapping (`types.ts`):**
- `normalizeWorkspaceTab(tab)` -- maps any of the 18 legacy tab IDs to 9 canonical IDs
- `legacyTabToSubTab(tab)` -- returns the sub-tab to pre-select (e.g., `orchestration -> monitor`)
- Both functions are in `frontend/src/pages/workspace/types.ts`

**controlledSubTab pattern:**
- When a parent tab (SystemTab, DataIntelTab) passes `controlledSubTab` to a child (InfrastructureTab, etc.), the child hides its own sub-tab nav and uses the parent's value
- Without the prop, children work standalone with their own nav (backwards compatible)

**PA entrypoint (`unified_pa_entrypoint.py`):**
- Intent routing: `_detect_intent_and_route(message)` returns `(intent, tool_name)` tuple
- Order matters: new intent blocks must go BEFORE existing ones that share keywords
- Tool results: `ToolResult` dataclass with `.ok`, `.result`, `.trace_id`

**PA async processing (Session 974b):**
- `unified_pa_chat` dispatches `process_pa_chat_task.delay()` -> returns `task_id`
- Frontend polls `GET /api/pa/chat/status/<task_id>/` every 2s
- Celery task handles persistence to `ChatConversation`

**ToolDispatcher handler signature (Session 973):**
- Must be `def handler(self, tool_name: str, payload: Dict, user_id: Optional[int], trace_id: str)` -- sync, not async
- `tool_name` is the first param after `self`

**Model import paths (Session 973):**
- `HeartBeat`: `core.models_heart` (NOT `core.models`)
- `SpiderData`: `core.models_unified_system` (NOT `ai_core.models`)
- `FailureDetection`: `core.models_diagnostic_pipeline` (NOT `core.models`)
- `HeartBeat` uses `recorded_at` (NOT `created_at`) and `overall_status` (NOT `status`)
- `CeleryTaskEvent`: `core.models_celery_telemetry` (Session 983)

**Stock models (Session 975):**
- `MarketIntelligenceBrief`: `core.models_unified_system` -- timestamp is `generated_at` (NOT `created_at`)
- `StockMarketAlert`: `core.models_autonomous_alerts` -- timestamp is `detected_at`
- `PredictionOutcome`: `core.models_unified_system` -- `was_correct_7_days`/`was_correct_30_days` are nullable booleans
- `PredictionOutcome` has UniqueConstraint on `(brief, ticker, prediction_type)` (Session 980)

**Ticker Lookup (Session 982):**
- `ticker_lookup` view: `core.views_stock_intelligence` -- aggregates 6 sources with per-section try/except
- Brief mentions: Python-side scan of last 30 briefs' JSON fields (`high_conviction_opportunities`, `debate_zone`, `bullish_opportunities`, `bearish_warnings`)
- SEC filings: searched by first word of company name (SEC data has no ticker field)
- `FINANCIAL_SPIDERS = ['yahoo_finance', 'polygon', 'coingecko', 'sec_edgar']`

**Railway deploy (Session 980):**
- Start command is in Railway GraphQL API (`serviceInstanceUpdate` mutation), NOT `entrypoint.sh` or `railway.toml`
- Service ID: `a840dd35-1f56-4053-a3cc-bc15f92c79e6`, Environment ID: `4045e5be-c118-4e3a-8931-c071f50ad119`
- Must use `sh -c '...'` wrapper for `$PORT` environment variable expansion
- Migrations with exclusive locks can hang during blue-green deploy

**SKIN Layer (Sessions 976, 983):**
- `_get_workspace_for_skin_layer()` returns "System Autonomous Workspace" at `generated_content/`
- All 5 SKIN tasks use this one helper -- no call-site changes needed
- `generated_content/` is gitignored (line 57 of `.gitignore`)
- On Railway, SKIN health uses 70-point baseline (file writes excluded from scoring)

**BaseAgent `__init_subclass__` (Session 970):**
- Auto-wraps `_execute_tool_call` in subclasses with ToolCallRecord recording
- Recording in `finally` with bare `except: pass` -- can never break agent execution

**Model field gotchas:**
- `SignalCluster`: in `core.models_signal_intelligence`, use `detected_at` (NOT `updated_at`)
- `AgentDecisionSummary`: does NOT have a `confidence` field
