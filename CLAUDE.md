# CLAUDE - AI Session Entry Point

**Last Updated:** February 9, 2026 - Session 980
**Status:** Component Health: 100% | Integration Score: 95% | Data Display: 98% | Django Web App | 9 BODY SYSTEMS | **Workspace: 9 TABS** (from 18) | **Bundle: 2,253 KB** (-26%) | **26 Legacy Routes → Redirects** | **Command Center "Now" Hub** | **Page Telemetry: ACTIVE** | **AI OS Boot Experience** | **Modular Workspace** | Self-Executing | **Celery Health Monitoring: ACTIVE** | **Executive Function: ACTIVE** | **Contracts: 3** | **Auto-Spawning: ACTIVE** | **Content Feedback Loop: ACTIVE** | **Domain Context Injection: ACTIVE** | **Signal Intelligence: WIRED** | **Initiative Priority: COMPLETE** | **Action Item Tracking: COMPLETE** | **Initiative UI: OVERHAULED** | **Report Provenance: ACTIVE** | **PDF Export: ACTIVE** | **Universal Agent Voice: ACTIVE** | **Initiative Conversations: ACTIVE** | **Agent Provenance: 18 AGENTS** | **PA Intelligence Enrichment: ACTIVE** | **Content Deliberation Pipeline: ACTIVE** | **PA Live Telemetry: ACTIVE** | **PA Status Snapshot: ACTIVE** | **Surgical Moves Verification: ACTIVE** | **ToolCallRecord: LIVE** | **Attention Coverage: 7 SECTIONS** | **PA Conversation History: ACTIVE** | **PA Async Processing: CELERY** | **Stock Intelligence Dashboard: ACTIVE** | **Stock Intelligence PA: WIRED** | **SKIN Layer Output: GITIGNORED** | **PA Production: FAST (3-64s)** | **Market Brief Save Guard: ACTIVE** | **Prediction Dedup: CONSTRAINED** | **Alert Quality: DEDUPED** | **Brief Detail UI: CARDS**

## System Stats
| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 76 | All synced + DecisionEnforcerAgent ("Prefrontal Cortex") |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **PA Tools** | 92 | +body tools for all 9 systems, +3 live telemetry tools, +surgical_moves_status, +status_snapshot, +stock_intelligence |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **LLM Models** | 16 | GPT-5 family, Claude 4, Llama, DeepSeek V3, Gemini 2.5/3 |
| **Database Models** | 386+ | Including Deliverable, AuditReport, SignalCluster, AutoTopic, InitiativeActionItem, ToolCallRecord, DecisionRecord, ResearchResult |
| **Celery Tasks** | 261 | ALL body systems active, autonomous remediation, async conversations, ConceptForge, health monitoring, signal aggregation, PA async chat |
| **Services** | 134 | Including AutoSpawnerService, SignalAggregationService, ActionItemParser, DomainContentContextBuilder (9 domains), ExperimentCollisionService, ClaimsPackBuilder, ContentReviewPanelV2, ContentDeliberationRunner |
| **Contracts** | 3 | ResearchContract, ExecutionMandate, SynthesisContract |
| **Body Systems** | 9 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN |
| **Advisors** | 25 | Famous figures + domain experts |
| **Frontend Bundle** | 2,253 KB | 9 workspace tabs (down from 18), 26 legacy redirects, collapsible sidebar |

## Key Capabilities
- **Stock Intelligence Production Hardening (980):** Nine PRs (#1030-#1038) fixing five production issues on the Stock Intelligence dashboard. (1) **Brief save guard:** `_save_brief_for_tomorrow` skips saving when `total_stocks_analyzed == 0`, preserving previous good brief; agent failure logging; 5-day weekend fallback for `_load_previous_brief`. (2) **Prediction dedup:** `_parse_target_move` regex parser for bull/bear targets (`"25%+"`, `"-25% or more"`); `update_or_create` keyed on `(brief, ticker, prediction_type)`; `UniqueConstraint` on PredictionOutcome (migration 0234 with raw SQL dedup). (3) **Railway deploy fixes:** Migration hung on lock during blue-green deploy; increased healthcheck to 600s via GraphQL API; temporarily removed migrate from start command; `sh -c` wrapper required for `$PORT` expansion. (4) **Brief detail UI:** Replaced `JsonSection` raw JSON dump with structured cards (ticker, recommendation badge, bull/bear arguments, risks). (5) **Alert quality:** Lowered Yahoo Finance threshold 5%→2%, removed `'rally'` keyword, added title-based dedup (seen_titles + 12h DB check), reduced news items 5→3; cleaned 319 duplicates in production.
- **Stock Intelligence PA Routing (979):** Wired Session 975's stock dashboard data to the PA. New `stock_intelligence` intent (before `spider_data` to avoid overlap) routes stock/market/SEC queries to `stock_intelligence_tool` with 5 actions (overview, briefs, alerts, predictions, sec_filings). Fixed misrouting bug: bare `'intelligence'` keyword in spider_data was catching "stock intelligence" queries and crashing with invalid `'list'` action. Made `spider_data_tool` defensive — unknown actions fall back to `'recent'` instead of raising `ValueError`. PR #1029.
- **PA Production Timeout Fix (977):** Fixed PA tool-routed queries (initiatives, system health, errors, blogs) timing out at 280s on Railway. Three-layer fix: (1) Dedicated `pa` queue routing + `celery-pa` worker to prevent queue starvation behind spider/initiative tasks (PRs #1016-1017). (2) Replaced `async_to_sync` deadlock with `new_event_loop()` + `run_until_complete()` (PRs #1018-1019). (3) Added 15s enrichment timeout, 60s LLM timeout, reduced reasoning effort ("analysis"→"conversation"), reduced max_tokens (8000→4000), step-level timing logs (PR #1020). Results: "hello" 3s, errors 3.4s, health 12.7s, overview 18.2s, blogs 46.6s, initiatives 64s. All previously timed out.
- **SKIN Layer Gitignore Fix (976):** Fixed SKIN Layer Celery tasks writing auto-generated files into the git repo root. `_get_workspace_for_skin_layer()` now uses "System Autonomous Workspace" at `generated_content/` (gitignored). Added `/reports/`, `/summaries/`, `/content/blog_*.md` to `.gitignore`. Removed 59 committed auto-generated files from git tracking. All 5 SKIN tasks use one helper — zero call-site changes.
- **Stock Intelligence Dashboard (975):** Dedicated `/stocks` page with sidebar entry surfaces stock market data previously only in Discord. 6 read-only API endpoints: dashboard overview (latest brief, alert counts, prediction accuracy, SEC count), paginated briefs, brief detail with full JSON fields, filterable alerts (type/symbol/action/bookmarked), predictions with 7D/30D accuracy stats, SEC Edgar filings. Frontend: 5 sub-tabs (Overview, Market Briefs, Alerts, SEC Filings, Predictions) with color-coded alert badges, bull/bear score bars, expandable brief detail, prediction accuracy table. Models: `MarketIntelligenceBrief`, `StockMarketAlert`, `PredictionOutcome`, `SpiderData`. Zero migrations.
- **PA Async Processing (974b):** Fixed Railway proxy timeouts for PA chat. Complex GPT-5.1 queries (117-172s) exceeded Railway's ~30s proxy timeout. Solution: `unified_pa_chat` now dispatches `process_pa_chat_task` Celery task (`time_limit=300`) and returns `{task_id}` instantly. New `GET /api/pa/chat/status/<task_id>/` polling endpoint. Frontend (GlobalPADock, CommandCenterPage, AssistantPage) polls every 2s with `isPolling` state + interval cleanup. ChatConversation persistence moved into the Celery task. Follows proven blog v2 pattern.
- **PA Conversation History (974):** ChatGPT-style conversation sidebar for the PA. `ChatConversation` model with `conversation_id`, `session_title`, auto-title generation via LLM. Three API endpoints: `list_pa_conversations`, `get_pa_conversation`, `create_pa_conversation`. Frontend `PAConversationSidebar` component in both GlobalPADock (overlay) and CommandCenterPage (sidebar). `paStore` manages `activeConversationId`, `conversations` list, sidebar state. PR #1011.
- **PA Live-First Upgrade (973):** Transformed PA from documentation narrator to live-data COO for broad system questions. New `system_overview` intent with 17 trigger phrases ("what updates", "how is everything", "executive summary", etc.) routes to `status_snapshot_tool` — 9 cheap `.count()` queries (Initiative, ToolCallRecord, HeartBeat, SpiderData, HiveMindSession, SignalCluster, TaskResult, FailureDetection, SelfBlog) with 60s Django cache. COO-level analytical directive: max 3-5 bullets, OBSERVED vs EXPECTED separation. Direct response role hardened to prevent doc narration on `general` fallthrough. PRs #1004-#1007.
- **UI + Discord Surface Reset (971b):** Consolidated navigation from 18 workspace tabs to 9 and 62 routes to 36. Seven PRs (#985-#990). (1) Page-view telemetry: fire-and-forget Redis counters via `usePageTracking()` hook, `POST /api/v1/telemetry/page-view/`. (2) Discord docs: `DISCORD_INTEGRATION.md` with all 112 commands, ACTIVE/DORMANT status, 12 notification channels. (3) Workspace shell reset: `normalizeWorkspaceTab()` maps 18 legacy tab IDs to 9 canonical; `legacyTabToSubTab()` preserves sub-tab context; SystemTab (Infra+Orch+Triggers), DataIntelTab (DataSources+Intelligence) adapters. (4) Content consolidation: Content Studio 6→9 sub-tabs (+Dossiers, Voices, Files via delegate pattern). (5) Double nav elimination: `controlledSubTab` prop on 4 original tabs suppresses inner nav when parent drives. (6) Legacy route cleanup: 26 standalone routes → `<Navigate replace>` redirects, 22 imports removed, bundle 3,062→2,249 KB (-26.5%). (7) Command Center "Now" hub: 3-panel strip (Attention Queue, Active Work, System Pulse) between header and PA chat, each clickable → workspace tab.
- **Surgical Moves Verification + ToolCallRecord + Attention Coverage (970):** Three deliverables. (1) Verification CLI (`manage.py verify_surgical_moves`) runs real 4-turn debate then prints structured pass/warn/fail report for Phases 0-3; `--mode=report-only` checks existing sessions without LLM spend. PA tool `surgical_moves_status_tool` with intent routing ("deliberation status", "what deliberations"). API endpoint `GET /api/deliberation/sessions/<uuid>/verification-report/`. Frontend `SurgicalMovesPanel` + `VerificationReportModal` in Orchestration Monitor tab. (2) ToolCallRecord activation: `__init_subclass__` in BaseAgent auto-wraps every subclass `_execute_tool_call` with recording — all 50+ agents now produce audit trail, zero agent files changed. Verified on Railway: 6 rows in first 3 minutes. (3) Expanded SystemStateAggregator attention surface: deliberation health (stuck sessions, contractless completions) + signal cluster freshness (stale active, untriggered high-strength). 7 attention sections total. PRs #977, #978.
- **PA Live Telemetry (969b):** 3 new PA tools for real-time system self-awareness. `recent_activity_tool` queries Celery tasks, SpiderData, HiveMindSession, SelfBlog, Initiative, SignalCluster within configurable time window. `system_health_tool` aggregates HeartBeat, ComponentStatus, Celery success rate, ToolCallAggregate, Spider freshness into computed overall_assessment (healthy/degraded/critical). `error_summary_tool` queries FailureSignature, FailureDetection, failed ToolCallRecord, failed Celery tasks with computed severity. Intent routing for natural phrases ("what's been going on?", "how's the system?", "any errors?"). Hours extraction from natural language. No migrations. PR #974.
- **Insight De-dup Bundling (968):** Memory Palace now bundles duplicate insight memories from the same conversation into a single expandable card. `source_id` exposed in `get_agent_memories()` and `list_all_memories()` APIs. Frontend `bundleInsights()` groups by `source_id`, `InsightBundleCard` shows collapsed "N agents" badge with expand/collapse. Also: remarkGfm import fix, frontend data plumbing audit (PR #970). No migrations.
- **Content Deliberation Pipeline (964):** Phase 4 multi-agent content pipeline: Spider signals -> ClaimsPack -> ContentWriter draft (citing [C-xxxxxxxxxx] claims) -> 3-reviewer panel (Skeptic + FactCheck + DomainPersona) -> DecisionEnforcer (PUBLISH/REVISE/KILL) -> PublishGate -> SelfBlog with `stats_snapshot['deliberation']`. ClaimsPackBuilder queries SpiderData (72h) + SignalCluster (active) with deterministic claim IDs. Structured reviewer output with validation (failure -> FAIL verdict, not skip). Full pipeline runner with graceful degradation. v2 Celery task + API endpoint (`POST /api/v1/research/self-blog/generate-v2/`). Blog deliberation replay endpoint (`GET /api/blog/<uuid>/deliberation/`). Old v1 flow untouched for A/B testing. No migrations needed.
- **PA Initiative Audit + Cleanup (961c):** Added `audit` action to initiative tool that classifies initiatives into real/stalled/noise/duplicates using Jaccard similarity clustering (Session 906). Keyword routing for audit/classify/triage/cleanup. Structured formatter with counts, samples, and cleanup recommendations. Production cleanup: merged 94 duplicates across 14 clusters, archived 420 noise initiatives. Active initiatives reduced from 566 to 52. PR #960.
- **PA Intelligence Upgrade (959):** Transformed the PA from a data listing tool into an analytical advisor. Wired 5 existing intelligence services (PAIntelligenceEnricher, BlogPerformanceContext, DomainContentContext, SpiderContext, AdvisorContext) into the PA response pipeline. Intent-to-enrichment mapping (12 intents, 14 aliases) determines which services fire per query. Relevance gating with regex tokenization prevents irrelevant context injection. Analytical prompt builder with intent-specific directives (content_review focuses on quality scores, initiatives on pipeline health, boardroom on triage urgency). Responses restructured: structured list always shown first, LLM analysis appended after separator. Expanded tool_dispatcher: blog quality scores (novelty, structure, publish_ready), initiative activity timestamps + critical action counts, boardroom ML confidence/priority/impact fields. Graceful degradation with individual try/except per enrichment service. PR #954.
- **Agent Provenance Expansion (953):** Extended Session 918 provenance tracking to 18 additional data-driven agents. Stock agents (8): BullCase, BearCase, MarketIntelligenceCoordinator, StockAuditCoordinator, MarketAnomalyDetector, SignalScanner, InstitutionalWatcher, MarketMovementMonitor (24h stale). Blockchain agents (5): BlockchainAuditCoordinator, WhaleWatcher, TransactionMonitor, ExploitDetector, SmartContractAuditor (4h stale). Analysis agents (3): TrendAnalysis, MarketIntelligence, OpportunityScoring (24h stale). Standalone agents (2): BookmakerAgent (2h), CreationAgent (24h). All agents now include provenance, publishable, and validation_status in output.
- **Initiative Conversations (928):** "Discuss with Agents" button in Initiative modal creates HiveMindSession linked to initiative via FK. Injects full context (origin, stages, action items, signals). Auto-selects relevant agents via AgentRouter. HiveMind sessions show linked initiative with clickable link. Endpoint: `POST /api/initiatives/<uuid>/start-conversation/`. Also fixed founder_intent blocker for 50 initiatives and reset 286 stub documents. PRs #828, #830, #831, #832.
- **Universal Agent Voice (927):** ListenButton throughout platform converts agent content to speech via ElevenLabs TTS. AudioCache model for content-based caching. 12 voices mapped to agent categories (Rachel=Research, Antoni=Financial, Bella=Creative, etc.). ListenAllButton for podcast-style sequential playback. Cost warning for content >2000 chars. Management command: `assign_agent_voices --apply`.
- **Panel/Advisor System Improvements (920):** Enhanced panel output quality with 7 improvements: (1) Dedupe post-processor removes repeated DecisionSummary blocks, (2) Provenance headers track generation metadata (generated_at, inputs_used, freshness_window, publishable), (3) Placeholder validation detects invalid topics like "target"/"[learned]" and auto-generates valid ones, (4) Extended DecisionSummary with Decision (chosen/rejected), Why Now, Risk Assessment, Operating Constraints sections, (5) Enhanced validation requires has_decision and has_risk, (6) Estimate labeling validates numeric estimates are cited or labeled, (7) ExperimentCollisionService prevents A/B test collisions on same target. PR #804.
- **Report Provenance + PDF Export (918):** Reports now track data sources, timestamps, and validation status via ReportProvenance dataclass. Publishing gates prevent stale data from being published. PDF export service using WeasyPrint with category-specific styling (sports=green, financial=blue, blockchain=purple, etc.). Frontend "Download PDF" button in Operations Panel. Operations pagination increased from 20 to 100. PRs #772, #774, #777, #779.
- **Initiative UI Overhaul (904):** Complete redesign of initiative display. Three view modes: Stages (grouped by pipeline phase 1-5, color-coded), List (compact rows), Cards (original grid). Comprehensive modal for ALL initiatives (not just completed) showing action items, signal intelligence, full trace. Live Activity section shows agents currently working with progress percentage and current step. Enhanced Origin & Trigger with Conversation Summary (topic, objective, success criteria, synthesis, timestamps). PRs #688-692.
- **Signal Intelligence Wired + Celery OOM Fix (903):** process_pending_auto_topics creates HiveMindSessions with signal_cluster/auto_topic FK links. trigger_signal_driven_conversation dispatches with full provenance chain. run_triggered_conversation accepts hive_session_id and updates status. Celery OOM fixed: task lock on scan_spider_opportunities (Django cache), reduced frequency 15→30 min, proper aiohttp connector cleanup.
- **Action Item Tracking (902):** Extract and track "Next Steps" from conversation conclusions. InitiativeActionItem model with status (pending/in_progress/completed/blocked), priority (critical/high/medium/low), timeline parsing ("Week 0-1" → due date), agent assignments. Parser service extracts items from `=== DecisionSummary ===` sections. 6 API endpoints for CRUD + bulk extraction. UI section in Initiative modal with stats bar, status checkboxes, priority badges, timeline indicators, manual creation input.
- **Initiative Priority & Portfolio (901):** Transform Initiative UI from firehose to strategic project management. Priority scoring: `impact*0.4 + urgency*0.2 + confidence*0.2 + revenue*0.2`. Priority levels: critical (>=0.8), high (>=0.6), medium (>=0.4), low (<0.4). Purpose categories: revenue, stability, learning, expansion, maintenance. Program groupings: 10 programs for portfolio organization. 4-tab UI: Active (working on), Portfolio (grouped by program), Archive (completed/archived), Stats (comprehensive breakdown). Priority badges, purpose icons, collapsible program sections.
- **Signal Intelligence (900):** Full provenance chain tracks WHY conversations happen, not just WHEN. SignalCluster groups spider signals into patterns (source_breakdown, strength, confidence, novelty, keywords). AutoTopic records why topics are chosen with rationale. Signal Aggregation Service clusters SpiderData every 30 min via Celery. API returns origin_signals with full chain. UI displays Origin Signals section in Initiative modal showing source breakdown, pattern metrics, sample signals, and auto topic rationale. Signal-Driven badge in headers. 22 clusters + 10 auto-topics in production.
- **Domain Content Context (891):** Unified system injects domain-specific platform data into ALL content. 9 domains: finance, crypto, sports, betting, ai_tech, legal, career, health, education. Auto-detects topic domain, supports cross-domain content (up to 2 domains). Gives every content type the "builder voice."
- **Podcast Quality System (890):** Anti-cliché detection (50+ phrases), PodcastStyleProfile model, host POV upgrade (takes stances), system war stories tool.
- **Content Feedback Loop (886):** BlogPerformanceContextBuilder injects past performance data into ContentWriterAgent prompts. Agent now "knows" quality scores, top topics, strengths/weaknesses, and active learning rules. Experiment audit: cleaned 81 junk experiments, raised error threshold 25%→35%, 87.5% real success rate.
- **AI OS Boot Experience (884):** Home page at `/` with personalized greeting, "while you were away" activity cards, active projects with progress bars, natural language input routing to PA, quick action buttons (Create, Research, Decide, Review, Build).
- **Executive Function + Contracts (872):** DecisionEnforcerAgent forces decisions after debate. ResearchContract, ExecutionMandate, SynthesisContract prevent vague outputs. AutoSpawnerService triggers data gathering reflexes. Prompt sharpening transforms hedging → decisive language.
- **Podcast TTS + Voice Profiles + ConceptForge UI (865):** Reconnected ElevenLabs TTS pipeline, VoiceProfileModal fetches real voices, custom voice selection. Added Dossiers tab with full 6-stage pipeline visualization. Celery health monitoring sends Discord alerts every 30 min.
- **Content Intelligence Improvements (864):** EditorAgent for auto-enhancement, operational title detection (auto-internal), lowered structure threshold 0.65→0.55. Expected: 2%→15%+ publish ready.
- **ConceptForge Pipeline (863):** Content → Intelligence → Strategy → Product. 6-stage autonomous think tank with 139 persona agents and 25 legendary advisors. Gate: quality >= 0.80 + strategic_tag.
- **Content Flow Unification (862):** Dream → Initiative → 5 Stages → Deliverable with full FK traceability. New ResearchResult model for Stage 1 tracking.
- **Data Persistence Complete (861):** Fixed 6 data persistence gaps - ToolCallRecord, DecisionRecord, SpiderAggregation, LearningBackup models + Content Tab modals with full content viewing
- **Initiative Pipeline + API Error Handling (860):** Documents now link to initiatives (25 backfilled) + fixed all console 404/401 errors and v.filter crashes
- **Workspace Inline Refactor (857):** 181 external links removed - all content displays inline, publish action creates Deliverables
- **User Context Injection (858):** All agents receive personalized user data (skills, goals, preferences) via context dict with category-based injection policy
- **Diagnostic Pipeline (856):** Detection → Diagnosis → Prescription system for failure analysis with evidence gathering
- **Experiment Learning Loop (836):** 251 learnings, 29 decision patterns, 89% success rate - Celery Beat fix + 3 production API fixes
- **Agent Output Rendering (835):** 10 output categories, 4 specialized renderers (Trends, Advisors, Investment, Security)
- **Async Conversations (827):** Production 502 fix - conversations run via Celery, instant response with task_id
- **Goal-Driven Conversations (826):** Objectives, success criteria, structured turn flows, topic-matched agents
- **Self-Healing System (820-823):** Auto-discovers audits → assigns to agents → executes fixes → verifies
- **SKIN Layer (695, 778):** All 74 agents write to real workspaces with rollback
- **UI Consolidation (825, 971b):** 29 pages → 18 tabs (825) → 9 tabs (971b), 26 legacy redirects, collapsible sidebar
- **Context Optimization (806):** 70% token reduction via ToolCategoryRouter + LazyContextLoader
- **Memory Safety (768):** Classification prevents test content from polluting learning
- **Integration Complete (744):** All 5 phases done - spider data, learning, advisors flow to agents

---

## Quick Start

```bash
# 1. Read current context (MANDATORY)
cat 00-START-NEXT-SESSION.md

# 2. Start platform
make start && make celery

# 3. Access AI Studio
open http://localhost:8000/ai-studio/
```

---

## Project Structure

### Key Directories
- `core/agents/` - 76 agents with learning hooks
- `core/services/` - 134 service classes
- `ai_core/spiders/` - 77 spiders
- `docs/handoffs/` - Session handoff documents

### Key Files
| File | Purpose |
|------|---------|
| `00-START-NEXT-SESSION.md` | Current session priorities |
| `core/agent_router.py` | Deterministic agent routing |
| `core/tasks.py` | Celery background tasks |
| `core/conversation_orchestrator.py` | Multi-agent conversations |
| `core/services/autonomous_remediation_orchestrator.py` | Self-healing system |
| `core/services/signal_aggregation_service.py` | Signal clustering & auto-topic generation |
| `core/services/unified_pa_entrypoint.py` | PA: 90 tools, intent routing, enrichment pipeline |
| `core/services/tool_dispatcher.py` | PA: 50 tool handlers including 3 telemetry tools, status_snapshot, stock_intelligence |
| `frontend/src/pages/WorkspacePageNew.tsx` | 9-tab modular workspace orchestrator |
| `frontend/src/pages/workspace/types.ts` | Tab types, normalizeWorkspaceTab(), legacyTabToSubTab() |
| `frontend/src/pages/CommandCenterPage.tsx` | Command Center with "Now" hub + PA chat |

---

## Agent Ecosystem (76 Agents)

**49 routable** | **25 non-routable** (sub-agents/coordinators) | **26+ provenance-tracked**

| Category | Count | Examples |
|----------|-------|----------|
| Creation | 4 | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| Development | 5 | FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent |
| Executive | 4 | CTOAgent, COOAgent, CreativeDirectorAgent |
| Stocks | 9 | StockAuditCoordinator, BullCaseAgent, BearCaseAgent |
| Blockchain | 5 | SmartContractAuditorAgent, WhaleWatcherAgent |
| Content | 8 | ContentWriterAgent, PodcastCoordinatorAgent |
| Analysis | 6 | TrendAnalysisAgent, MarketIntelligenceAgent |
| Special | 3 | ThinkingAgent, SystemIntelligenceAgent |

Full list: See `docs/AGENTS.md`

---

## Spider Network (77 Spiders)

| Category | Count | Examples |
|----------|-------|----------|
| News/Media | 10 | TechCrunch, BBC, Reuters, NewsAPI |
| Financial | 9 | CoinGecko, YahooFinance, Polygon, Kalshi |
| Tech | 8 | HackerNews, DevTo, GitHub |
| Legal | 6 | CourtListener, FindLaw, Justia |

Full list: See `docs/SPIDERS.md`

---

## GPT-5-mini Configuration

```python
# CORRECT - Reasoning model has different parameters
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000  # NOT max_tokens, NO temperature
)
```

---

## Troubleshooting

```bash
# Full restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery

# macOS Celery SIGSEGV fix
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l INFO --pool=solo
```

---

## Recent Sessions (Last 15)

| Session | Focus | Handoff |
|---------|-------|---------|
| **980** | Stock Intelligence Production Hardening - 9 PRs: brief save guard, prediction dedup + target parsing, migration 0234, Railway deploy fixes, brief detail UI cards, alert quality + dedup. PRs #1030-1038 | `SESSION_980_FIX_0_STOCK_BRIEF_SAVE.md` |
| **979** | Stock Intelligence PA Routing - New stock_intelligence intent + tool (5 actions), fixed 'intelligence' keyword misrouting to spider_data, defensive spider_data fallback PR #1029 | `SESSION_979_STOCK_INTELLIGENCE_PA_ROUTING.md` |
| **977** | PA Production Timeout Fix - Dedicated pa queue, async_to_sync deadlock fix, 15s enrichment timeout, 60s LLM timeout, reduced reasoning effort, step-level timing. Results: 3-64s (was 280s+ timeout) PRs #1016-1020 | `SESSION_977_PA_TIMEOUT_FIX.md` |
| **976** | SKIN Layer Gitignore Fix - Redirect auto-generated output to generated_content/, add gitignore patterns, remove 59 committed files from tracking | `SESSION_976_SKIN_LAYER_GITIGNORE_FIX.md` |
| **975** | Stock Intelligence Dashboard - Standalone /stocks page, 6 API endpoints, 5 sub-tabs (Overview, Briefs, Alerts, SEC, Predictions), sidebar entry, zero migrations | `SESSION_975_STOCK_INTELLIGENCE_DASHBOARD.md` |
| **974b** | PA Async Processing - Celery task for PA chat, polling endpoint, 3 frontend consumers updated, fixes Railway proxy timeouts | `SESSION_974b_PA_ASYNC_CELERY.md` |
| **974** | PA Conversation History - ChatGPT-style sidebar, ChatConversation model, auto-title, load/resume conversations PR #1011 | — |
| **973** | PA Live-First Upgrade - status_snapshot_tool (9 model queries), system_overview intent (17 phrases), COO analytical directive, direct response hardening PRs #1004-1007 | `SESSION_973_PA_LIVE_FIRST_UPGRADE.md` |
| **971b** | UI + Discord Surface Reset - 18→9 workspace tabs, 26 legacy route redirects, -26% bundle, Command Center "Now" hub, page telemetry, Discord 112-command docs PRs #985-990 | `SESSION_971b_UI_SURFACE_RESET.md` |
| **970** | Surgical Moves Verification + ToolCallRecord Activation + Attention Coverage - CLI verify command, PA tool, API endpoint, frontend panel, __init_subclass__ recording wrapper, 2 new attention sections PRs #977-978 | `SESSION_970_SURGICAL_MOVES_VERIFICATION.md` |
| **969b** | PA Live Telemetry - 3 tools (recent_activity, system_health, error_summary) for real-time system self-awareness, intent routing, natural language hours extraction PR #974 | `SESSION_969b_PA_LIVE_TELEMETRY.md` |
| **969** | Orchestration Tab Enrichment + ORM Fix + Blog Diversity - metrics bar, HiveMind sessions, execution detail, field name fix, 10 diverse fallback topics PR #971-972 | `SESSION_969_ORCHESTRATION_ENRICHMENT.md` |
| **968** | Insight De-dup Bundling - Memory Palace bundles duplicate insights by source_id, remarkGfm fix, frontend data plumbing PR #970 | `SESSION_968_INSIGHT_DEDUP_BUNDLING.md` |
| **964** | Phase 4 Content Deliberation Pipeline - ClaimsPack, 3-reviewer panel, DecisionEnforcer, PublishGate, v2 blog API | `SESSION_964_CONTENT_DELIBERATION_PIPELINE.md` |
| **961c** | PA Initiative Audit + Cleanup - Audit action classifies real/stalled/noise/duplicates, merged 94 dupes, archived 420 noise, 52 active remain | `SESSION_961c_PA_INITIATIVE_AUDIT.md` |
| **961b** | PA Initiative Display Fix - Raised limits, added total count, full names | `SESSION_961b_PA_INITIATIVE_DISPLAY_FIX.md` |
| **959** | PA Intelligence Upgrade - Analytical advisor with 5 enrichment services, intent mapping, relevance gating, expanded data fields | `SESSION_959_PA_INTELLIGENCE_UPGRADE.md` |
| **953** | Agent Provenance Expansion - Added provenance tracking to 18 data-driven agents (stocks, blockchain, analysis, standalone) | `SESSION_953_AGENT_PROVENANCE.md` |
| **928** | Initiative Conversations - "Discuss with Agents" button, HiveMind initiative FK, founder_intent fix, stub doc reset | `SESSION_928_INITIATIVE_CONVERSATIONS.md` |
| **927** | Universal Agent Voice - ListenButton for TTS, AudioCache model, 12 voice mappings, cost warnings | `SESSION_926_UNIVERSAL_AGENT_VOICE.md` |
| **920** | Panel/Advisor System Improvements - Dedupe, provenance headers, placeholder validation, extended DecisionSummary, estimate labeling, ExperimentCollisionService | `SESSION_920_PANEL_ADVISOR_IMPROVEMENTS.md` |
| **918** | Report Provenance + PDF Export - Data source tracking, publishing gates, WeasyPrint PDF service, download button, pagination fix | `SESSION_918_REPORT_PROVENANCE.md` |
| **904** | Initiative UI Overhaul - Stages view, comprehensive modal, live activity, conversation details | `SESSION_904_INITIATIVE_UI_OVERHAUL.md` |
**Older sessions:** See `docs/handoffs/` directory (Sessions 197-902)

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [AGENTS.md](docs/AGENTS.md) | Agent documentation (74 agents) |
| [SPIDERS.md](docs/SPIDERS.md) | Spider network (77 spiders) |
| [SERVICES.md](docs/SERVICES.md) | Services layer (120 services) |
| [DATABASE_MODEL_REFERENCE.md](docs/DATABASE_MODEL_REFERENCE.md) | Which DB table for what |
| [API_PATH_POLICY.md](docs/API_PATH_POLICY.md) | API path conventions (`/api/` vs `/api/v1/`) |
| [DREAM_INITIATIVE_WORKFLOW.md](docs/DREAM_INITIATIVE_WORKFLOW.md) | Dream → Initiative 5-stage pipeline |
| [DISCORD_INTEGRATION.md](docs/DISCORD_INTEGRATION.md) | Discord bot: 112 commands, 12 channels |

**Documentation Index:** Run `python manage.py build_docs_index` to regenerate `docs/INDEX.md`

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
