# Session 989 - Start Here

**Previous Session:** 988 (Stale Data, Modal Overflow, PA Routing Fixes)
**Date:** February 11, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** | **Workspace: 9 TABS** | **Bundle: 2,305 KB** | **Unified PA: ANALYTICAL ADVISOR** | **PA Tools: 92** | **Content Deliberation Pipeline: ACTIVE** | **Agent Knowledge: 14-DAY FRESHNESS FILTER** | **Execution History: INCLUDES CONVERSATIONS** | **Initiative Modals: OVERFLOW FIXED** | **Content Reviewers: IMPORT FIXED** | **PA Intent Order: INITIATIVES BEFORE BOARDROOM**

---

## Session 988 Summary (Just Completed)

### Production Bug Fixes (5 commits)

**Initiative Modal Overflow:** Both `InitiativeDetailModal` and `ComprehensiveInitiativeModal` had unbounded `initiative.description` in fixed headers, pushing scrollable content off-screen. Fixed with `line-clamp-2`, `truncate`, `min-h-0`, collapsible "Full Description" toggle.

**Content Reviewer Broken Import:** `core/services/content_review_panel_v2.py` imported from non-existent `core.llm_providers`. SkepticReviewer and FactCheckReviewer were returning synthetic FAIL for every blog. Fixed to use `core.services.llm_provider_registry`.

**PA Initiative Routing:** "What initiatives need attention?" matched "attention" → boardroom intent (1,462 items) before reaching initiative patterns. Moved initiative patterns before boardroom catch-all.

**Agent Stale Data Grounding:** All agents in multi-agent conversations referenced "Oct 23, 2023 Notion data" because `_get_agent_knowledge()` had no date filter. Added 14-day freshness cutoff + strengthened DATA GROUNDING REQUIREMENT prompt with dynamic current month/year injection.

**Execution History Formatter:** "What have agents been doing?" fell through to generic LLM because: (a) intent patterns didn't cover natural phrases, (b) formatter used wrong field names (`executions` vs `items`, `period_hours` vs `hours_back`), (c) `DeliberationSession` (agent conversations) was invisible. All three fixed.

### Session 987 Summary (Prior)

PA Wiring Completion: Blog revision feedback loop, 7 unrouted tool handlers wired, body vitals routing narrowed.

### Session 986 Summary (Prior)

Nervous System 60% Health Fix — Redis URL parsing, CeleryTaskEvent wiring, mild activity penalty.

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
| PA Intents | 35+ (execution_history expanded) |
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

### Content Reviewers — Verify on Railway
After the import fix, SkepticReviewer and FactCheckReviewer should now produce real verdicts. Trigger a blog generation and verify reviewer output shows actual PASS/FAIL with substantive feedback instead of synthetic FAIL from import errors.

### Agent Knowledge Freshness — Monitor Impact
14-day cutoff may be too aggressive if agents have genuinely useful older knowledge. Monitor agent conversation quality — if agents seem "uninformed", consider widening to 30 days or making freshness configurable per agent.

### DeliberationSession in Execution History — Verify on Railway
New `DeliberationSession` queries in `execution_history_tool` need verification. Ask PA "What have agents been doing?" and confirm it shows both executions and conversations.

### Railway Deploy: Verify Celery Prefork
Monitor celery-worker memory over 4+ hours. Look for "child process exiting" messages confirming child recycling is working.

### Railway Deploy: Migration Lock Risk
`AddConstraint` during blue-green deploy can hang on lock. For future migrations with exclusive locks, run manually before deploy.

### Muscular System Score (60.5%) — Agent Performance
Muscular health reflects actual agent execution success rates. Investigate `AgentExecution` records for underperforming groups.

### Legacy Routes Expire in ~2-4 Weeks
26 legacy routes redirect to workspace tabs. Telemetry tracks traffic. Remove redirect routes after transition period.

### Billing + Analytics Orphaned
`/billing` and `/analytics` standalone pages need an Admin tab or absorption into existing tab.

### ToolCallRecord Now Populating
Data is flowing but no analytics dashboard exists yet.

### FailureSignature Table Empty
The diagnostic pipeline (Session 856) has 0 records in production. May need activation.

---

## What Could Come Next

### Content Deliberation v2 via PA
`POST /api/v1/research/self-blog/generate-v2/` exists but PA can't trigger it. Add intent for "create blog with full review" / "deliberated blog".

### Auto-Revision Loop
If deliberation pipeline returns REVISE verdict, loop back through EditorAgent automatically instead of requiring manual re-trigger.

### Scheduled Task Visibility
PA has no visibility into Celery Beat scheduled tasks. Add `scheduled_tasks_tool` with "what's scheduled?", "automation status" intents.

### Agent Introspection
PA can invoke agents but can't describe their capabilities. Add "what can [agent name] do?" intent.

### AgentExecution from ConversationOrchestrator
Multi-agent conversations don't write `AgentExecution` records. The `DeliberationSession` workaround helps but a proper `AgentExecution` per agent turn would give full visibility.

### Ticker Lookup Enhancements
- Wire ticker lookup to PA: "look up AAPL"
- Historical price chart (sparkline)
- Watchlist feature
- Compare mode

### Stock Intelligence v2
- PATCH endpoint for bookmark toggle and user notes
- Prediction accuracy dashboard with charts

### CeleryTaskEvent Analytics
- Dashboard showing task stats, success rates, queue utilization
- Integrate with ToolCallRecord for end-to-end tracing

### Admin Tab
Dedicated workspace tab for Billing, Analytics, system configuration.

### Code-Splitting
`React.lazy()` for workspace tabs — all 9 are in the main bundle.

### Deep Sub-tab URLs
Support `?tab=system&sub=monitor` for direct deep-linking.

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
- These load ~800MB into Celery parent process
- Always use `try/except ImportError` or import inside the method that uses them

**Spider data_type values (Session 984):**
- Real types: `opportunity`, `job_posting`, `market_data`, `competitor_info`, `trend_data`, `user_feedback`, `product_info`, `pricing_data`, `content_idea`, `collaboration`, `news`, `research`, `tool_discovery`, `learning_resource`
- DO NOT use `market_alert`, `security_alert`, `price_alert`, `breaking_news`

**LLM Provider Registry (Session 988):**
- Correct import: `from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest`
- Usage: `registry = get_llm_provider_registry(); response = registry.complete(provider='openai', model_id='gpt-4.1-mini', request=LLMRequest(...))`
- `LLMResponse` has `.success`, `.content`, `.error`
- Do NOT use `from core.llm_providers import ...` (module doesn't exist)

**PA intent routing order (Session 988):**
- More specific patterns MUST come before generic catch-alls
- Initiative patterns run before boardroom (both match "attention")
- When adding new intents, check for keyword overlap with existing intents above

**Agent knowledge freshness (Session 988):**
- `_get_agent_knowledge()` filters to 14-day window
- Prevents agents grounding on stale data (e.g., "Oct 2023 Notion articles")
- DATA GROUNDING REQUIREMENT prompt injects current month/year dynamically

**Execution history tool (Session 988):**
- Handler returns `items` (not `executions`), `hours_back` (not `period_hours`)
- Now includes `DeliberationSession` data (agent conversations) alongside `AgentExecution`
- Formatter fixed to match handler field names

**Boardroom auto-approve (Session 984):**
- Items have 24h age gate before auto-approval
- `create_attention_item` has built-in dedup (source_type + item_type + title)

**PA boardroom response quality (Session 985):**
- `_handle_boardroom` stats action returns `top_items` (top 10 critical/high by priority_score)
- Boardroom LLM directive: "Max 3-5 bullets of INSIGHT only" — do NOT restate counts

**PA intent routing (Session 987):**
- 7 wired tools: revenue, task_management, workspace, budget, system_alerts, ml_analysis, pipeline_status
- Blog actions: `revise`, `needs_work`, `batch_enhance`
- Body vitals routing narrowed to body-specific phrases

**Workspace tab mapping (`types.ts`):**
- `normalizeWorkspaceTab(tab)` — maps 18 legacy tab IDs to 9 canonical IDs
- `legacyTabToSubTab(tab)` — returns sub-tab to pre-select

**controlledSubTab pattern:**
- Parent tab passes `controlledSubTab` to child → child hides its own nav
- Without the prop, children work standalone (backwards compatible)

**PA entrypoint (`unified_pa_entrypoint.py`):**
- Intent routing: `_detect_intent_and_route(message)` returns `(intent, tool_name)` tuple
- Order matters: new intent blocks must go BEFORE existing ones that share keywords

**PA async processing (Session 974b):**
- `unified_pa_chat` dispatches `process_pa_chat_task.delay()` → returns `task_id`
- Frontend polls `GET /api/pa/chat/status/<task_id>/` every 2s

**ToolDispatcher handler signature (Session 973):**
- Must be `def handler(self, tool_name: str, payload: Dict, user_id: Optional[int], trace_id: str)` — sync, not async

**Model import paths:**
- `HeartBeat`: `core.models_heart` (NOT `core.models`)
- `SpiderData`: `core.models_unified_system` (NOT `ai_core.models`)
- `FailureDetection`: `core.models_diagnostic_pipeline`
- `HeartBeat` uses `recorded_at` (NOT `created_at`) and `overall_status` (NOT `status`)
- `CeleryTaskEvent`: `core.models_celery_telemetry` (Session 983)
- `DeliberationSession`: `core.models_deliberation` (Session 988)

**Stock models (Session 975):**
- `MarketIntelligenceBrief`: `core.models_unified_system` — timestamp is `generated_at`
- `StockMarketAlert`: `core.models_autonomous_alerts` — timestamp is `detected_at`
- `PredictionOutcome`: `core.models_unified_system` — `was_correct_7_days`/`was_correct_30_days` are nullable booleans

**Ticker Lookup (Session 982):**
- `ticker_lookup` view: `core.views_stock_intelligence` — aggregates 6 sources with per-section try/except
- `FINANCIAL_SPIDERS = ['yahoo_finance', 'polygon', 'coingecko', 'sec_edgar']`

**Railway deploy (Session 980):**
- Start command is in Railway GraphQL API (`serviceInstanceUpdate` mutation), NOT `entrypoint.sh`
- Must use `sh -c '...'` wrapper for `$PORT` expansion
- Migrations with exclusive locks can hang during blue-green deploy

**SKIN Layer (Sessions 976, 983):**
- `_get_workspace_for_skin_layer()` returns "System Autonomous Workspace" at `generated_content/`
- `generated_content/` is gitignored
- On Railway, SKIN health uses 70-point baseline

**BaseAgent `__init_subclass__` (Session 970):**
- Auto-wraps `_execute_tool_call` in subclasses with ToolCallRecord recording
