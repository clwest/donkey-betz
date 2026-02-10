# Session 983 - Start Here

**Previous Session:** 982 (Unified Single-Stock Ticker Lookup)
**Date:** February 9, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** | **Workspace: 9 TABS** (down from 18) | **Bundle: 2,305 KB** | **26 Legacy Routes -> Redirects** | **Command Center "Now" Hub: ACTIVE** | **Page Telemetry: ACTIVE** | **Discord Docs: 112 COMMANDS** | **Risk-Aware RAG: COMPLETE** | **Unified PA: ANALYTICAL ADVISOR** | **Phase 0-4 Deliberation: COMPLETE** | **Content Deliberation Pipeline: ACTIVE** | **PA Live Telemetry: ACTIVE** | **PA Status Snapshot: ACTIVE** | **Surgical Moves Verification: ACTIVE** | **ToolCallRecord: LIVE** | **Attention Coverage: 7 SECTIONS** | **PA Conversation History: ACTIVE** | **PA Async Processing: CELERY** | **Stock Intelligence Dashboard: ACTIVE** | **Stock Intelligence PA: WIRED** | **Ticker Lookup: ACTIVE** | **SKIN Layer Output: GITIGNORED** | **PA Production: FAST (3-64s)** | **Market Brief Save Guard: ACTIVE** | **Prediction Dedup: CONSTRAINED** | **Alert Quality: DEDUPED** | **Brief Detail UI: CARDS**

---

## Session 982 Summary (Just Completed)

### Unified Single-Stock Ticker Lookup (PR #1041)

New `/api/stocks/ticker/<symbol>/` endpoint aggregates 6 data sources for any ticker symbol: live quote (via MarketDataService), alerts, predictions, brief mentions (scans JSON fields of last 30 briefs), SEC filings (by company name), and spider data (by symbol). Per-section fault isolation — if one source fails, others still return.

New "Ticker Lookup" sub-tab is now the default view on the Stock Intelligence page. Search bar with auto-uppercase, hero quote card with 8-stat grid, color-coded analysis badges (momentum/volatility/signal), 52-week range position bar, and collapsible sections for all data types with count badges.

### Session 981 Summary (Prior)

Dynamic Ticker Selection — Sector rotation for market briefs. PR #1040.

### Session 980 Summary (Prior)

Stock Intelligence Production Hardening — 9 PRs (#1030-#1038): brief save guard, prediction dedup, Railway deploy fixes, brief detail UI cards, alert quality dedup.

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 76 (49 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 77 (72 working, 5 need API keys) |
| Advisors | 25 |
| Active Initiatives | 52 (cleaned from 568 in Session 961c) |
| Database Models | 390+ |
| Services | 134 |
| Celery Tasks | 262 |
| Workspace Tabs | 9 (down from 18) |
| Frontend Bundle | 2,305 KB |
| Frontend Routes | 37 (15 standalone + 22 redirects) |
| PA Tools | 92 |
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

### Railway Deploy: Migration Lock Risk
Migration 0234 showed that `AddConstraint` during blue-green deploy can hang on lock. For future migrations with exclusive locks, consider: (a) run migration manually before deploy, or (b) temporarily skip migrate in start command.

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

### Ticker Lookup Enhancements
- Wire ticker lookup to PA: "look up AAPL" routes to ticker_lookup endpoint
- Add historical price chart (sparkline or mini chart component)
- Watchlist feature: save tickers, get notified on new alerts/predictions
- Compare mode: side-by-side view of two tickers

### Stock Intelligence v2
- PATCH endpoint for bookmark toggle and user notes on alerts
- Prediction accuracy dashboard with charts over time

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

### Auto-Revision Loop
If deliberation pipeline returns REVISE verdict, loop automatically instead of requiring manual re-trigger.

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`). Always use `DJANGO_SETTINGS_MODULE=core.settings`.

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

**SKIN Layer workspace (Session 976):**
- `_get_workspace_for_skin_layer()` now returns "System Autonomous Workspace" at `generated_content/`
- All 5 SKIN tasks use this one helper -- no call-site changes needed
- `generated_content/` is gitignored (line 57 of `.gitignore`)

**BaseAgent `__init_subclass__` (Session 970):**
- Auto-wraps `_execute_tool_call` in subclasses with ToolCallRecord recording
- Recording in `finally` with bare `except: pass` -- can never break agent execution

**Model field gotchas:**
- `SignalCluster`: in `core.models_signal_intelligence`, use `detected_at` (NOT `updated_at`)
- `AgentDecisionSummary`: does NOT have a `confidence` field
