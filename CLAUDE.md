# CLAUDE - AI Session Entry Point

**Last Updated:** January 24, 2026 - Session 810
**Status:** Component Health: 100% | Integration Score: 95% | Data Display: 85% | Django Web App | 9 BODY SYSTEMS | 14/14 SCI-FI UI | 45 Frontend Pages

## System Stats (Session 746)
| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 74 | All synced to database + workspace integration (100% rotation verified Session 778-779) |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **PA Tools** | 86 | +body tools for all 9 systems |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **LLM Models** | 16 | GPT-5 family, Claude 4, Llama, DeepSeek V3, Gemini 2.5/3 |
| **Agent LLM Configs** | 75 | All agents mapped to optimal models (Session 699) |
| **LLM API Endpoints** | 7 | Status, providers, models, configs, logs, analytics (Session 699) |
| **ML Models** | 17 | 15 working (Sessions 677-685) |
| **Database Models** | 364+ | +2 SKIN models (SkinPulse, SkinStatus) |
| **Celery Tasks** | 228 | +60 critical tasks restored (Session 810) - ALL body systems active |
| **Services** | 118 | +4 context optimization services (Session 806: tool_category_router, context_budget_manager, lazy_context_loader, context_summarizer) |
| **Discord Commands** | 112 | 29 Cog categories |
| **Advisors** | 25 | Famous figures + domain experts |
| **Sci-Fi Features** | 14 | **14/14 have frontend UI (100%)** |
| **Running Pilots** | 18 | Auto-deployed via autonomous pipeline |
| **OPEN Systems** | 7/7 | Full composability (Session 653) |
| **Body Systems** | 9 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, **SKIN** |
| **Body API Endpoints** | 65 | +6 skin endpoints, unified via body_vitals.py |
| **Frontend Pages** | 45 | +DocsIndexPage (Session 784), +SpiderFeedPage (Session 783), +OrchestrationPage (Session 768), +IntegrationHealthPage (Session 758) |
| **Content Channels** | 3 | 91 episodes with unique AI-generated titles |
| **Frontend Bundle** | 1,390 KB | All sci-fi features + 9 body systems + enhanced data displays |

**Data Display Enhancements (Session 746):** Comprehensive audit revealed ~40% of API data wasn't displayed. Fixed: Human Page (stats, decision history, ML override indicators), Betting Page (singles vs parlays, per-sport breakdown, wager leg details), Dashboard (network graph visualization with active agents/connections), Intelligence Page (gate checklist details, execution history, latency metrics).
**Integration Roadmap COMPLETE (Session 744):** All 5 phases done - Celery health, spider-to-agent data flow, learning patterns, advisor wisdom, feedback loops. All 74 agents now receive context automatically + can delegate to specialists. DynamicTeamBuilder enables cross-domain agent teams.
**SKIN System (Session 723):** Workspace output monitoring - file writes, project changes, rollback availability, 6 API endpoints, 7 status levels (healthy/active/sweating/irritated/damaged/healing/dormant)
**BRAIN System (Session 722):** Cognitive processing monitoring - LLM calls, conversations, reasoning chains, 5 API endpoints, 6 status levels (focused/thinking/overloaded/foggy/resting/offline)
**Sci-Fi UI Complete (Session 718):** All 14 sci-fi features now have frontend UI - Spider Integration, Memory Clusters tab, Conversation Contract added in Sessions 717-718
**Body UI Unified:** HeartWidget rewritten for 8 real systems, Admin cleanup (-2,106 lines), body cards on Human/Workspace/Assistant pages (Session 712)
**MUSCULAR System:** Agent work execution monitoring - 10 muscle groups, 8 API endpoints, fatigue/strain detection (Session 707)
**DIGESTIVE System:** Data ingestion & processing - 8 ingestion routes, 8 API endpoints, bottleneck detection (Session 706)
**IMMUNE System:** Security & threat detection - 14 threat patterns, 10 API endpoints, quarantine management (Session 705)
**SPINE Service:** Central API routing - 19 route patterns across 12 categories, health-aware routing (Session 704)
**CIRCULATORY System:** Data flow monitoring - tracks data movement through the system (Session 703)
**LUNGS Service:** Resource & capacity management - LLM budget tracking (Session 702)
**HEART Service:** Central health monitoring - unified via body_vitals.py (Session 701)
**SKIN Layer:** All 74 agents can now write to real project workspaces with audit trail + rollback (Session 695, verified Session 778-779)
**LLM Routing:** GPT-5 models use Responses API (max_completion_tokens, no temperature)
**Memory Safety Classification (Session 768):** Prevents test/exploratory content from polluting learning. AgentMemory has `safety_class` (test_only/exploratory/candidate/approved) + `poison_risk_score`. BaseAgent has `health_check_mode` to skip learning entirely.
**Agent Conversation Voice (Session 781):** 3-level fix for repetitive conversation styles. Level 2: 22 role-anchored disagreement styles. Level 1: Opener de-duplication tracking. Level 3: Discourse memory with 50+ phrase tracking across 5 categories.
**Spider News Feed (Session 783):** Reddit/Yahoo-style human-facing feed for spider data with agent annotations. Agents flag items as useful/profitable/podcast_worthy/breaking_news. Humans browse, filter, search, vote.
**Documentation Index Browser (Session 784):** Cognitive Build Ledger UI - browse 1,512 docs with status badges (active/superseded/deprecated/draft), cross-reference graph (1,816 links), broken link detection (100), orphan detection (50). DocsIndexPage with filters, search, DocDetailsPanel showing inbound/outbound links with context snippets.
**Learning System Fix (Session 805):** Fixed 3 critical issues: (1) Anomaly detection false positives - 84 experiments incorrectly halted due to comparing to zero baseline, fixed with minimum 3/hour baseline. (2) Missing learnings - 87% of experiments had no learnings extracted, added `_extract_halt_learning()` to Experiment.halt(). (3) Negative learning weight - operational monitoring terms in safety keywords caused -1.0 signal for normal failures, fixed with v1.2 classification. Net weight improved from -3.169 to -0.944 (70% improvement).
**Personal Assistant Context Optimization (Session 806):** Reduced PA context token usage by ~70%. Created 4 new services: (1) ToolCategoryRouter - Two-stage tool routing (47→10 tools per request based on 8 categories). (2) ContextBudgetManager - Token tracking with tiktoken, priority-based allocation (4,000 token budget). (3) LazyContextLoader - On-demand context loading based on query classification (16→2-5 sections). (4) ContextSummarizer - 5-10x compression for spider/learning/advisor context. Feature flags enable gradual rollout.

---

## Quick Start

```bash
# 1. Read current context (MANDATORY)
cat 00-START-NEXT-SESSION.md

# 2. Start platform
make start
make celery

# 3. Access AI Studio
open http://localhost:8000/ai-studio/
```

## Documentation Maintenance

**IMPORTANT:** After creating or modifying documentation, regenerate the index:

```bash
# Regenerate docs/INDEX.md after ANY documentation changes
python manage.py build_docs_index

# Preview without writing (dry run)
python manage.py build_docs_index --dry-run
```

This command scans all `/docs/` folders and generates an up-to-date `INDEX.md` with:
- File counts by folder (handoffs, audits, designs, etc.)
- Recent session list (last 20)
- Recently modified files (last 10)
- Platform statistics pulled from this file (CLAUDE.md)

**Run this command when you:**
- Create a new session handoff document
- Add or modify audit reports
- Create new documentation files
- Complete a session with documentation updates

---

## Project Structure

### Key Directories
- `core/agents/` - **Canonical agent location** (74 agents with learning hooks)
- `core/services/` - Business logic services (93 service classes)
- `core/prompts/` - Central prompt registry
- `ai_core/spiders/` - Spider network (77 spiders)
- `ai_core/templates/` - Frontend (ai_image_studio.html)
- `docs/handoffs/` - Session handoff documents

### Key Files
| File | Purpose |
|------|---------|
| `00-START-NEXT-SESSION.md` | Current session priorities |
| `core/agent_router.py` | Deterministic agent routing |
| `core/tasks.py` | Celery background tasks |
| `core/celery.py` | Celery Beat schedules |
| `core/assistant/tool_definitions.py` | GPT tool schemas |
| `core/services/heart.py` | HEART Service - system health monitoring |
| `core/services/lungs.py` | LUNGS Service - resource & capacity management |
| `core/services/spider_context_builder.py` | Phase 2 - Agent-aware spider context |
| `core/services/learning_pattern_engine.py` | Phase 3 - Learning pattern mining |
| `core/services/advisor_context_builder.py` | Phase 4 - Advisor wisdom injection |
| `core/services/feedback_loop_engine.py` | Phase 5 - Performance feedback |
| `core/services/celery_health.py` | Phase 1 - Celery monitoring |
| `core/services/review_document.py` | Chief of Staff review generation |
| `core/services/side_chat.py` | Pro/Con interrogation service |
| `core/services/mission_control_executor.py` | **Session 763** - Action execution registry (17 handlers) |
| `core/conversation_orchestrator.py` | **Session 781** - Multi-agent conversations with voice de-duplication |
| `core/prompts/registry.py` | **Session 781** - CONVERSATION_ROLES (22 role-anchored styles) |
| `core/views_spider_feed.py` | **Session 783** - Spider News Feed API (6 endpoints for feed, trending, detail, annotate, vote, stats) |
| `core/views_docs_index.py` | **Session 784** - Documentation Index API (4 endpoints: index, stats, graph, detail) |
| `core/assistant/tool_category_router.py` | **Session 806** - Two-stage tool routing (8 categories, 47→10 tools) |
| `core/services/context_budget_manager.py` | **Session 806** - Token tracking with tiktoken (4,000 token budget) |
| `core/services/lazy_context_loader.py` | **Session 806** - On-demand context loading (16→2-5 sections) |
| `core/services/context_summarizer.py` | **Session 806** - Context compression (5-10x ratios) |

---

## Agent Ecosystem (74 Agents)

All agents in `core/agents/` with learning hooks connected to collective intelligence.
**49 routable** (in AgentRouter) | **25 non-routable** (sub-agents and coordinator teams)

| Category | Count | Agents |
|----------|-------|--------|
| **Creation** | 4 | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| **Editing** | 2 | ImageEditingAgent, VideoEditingAgent |
| **Research** | 1 | ResearchAgent |
| **Content Writing** | 1 | ContentWriterAgent |
| **Strategy** | 4 | ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent |
| **Executive** | 4 | CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent |
| **Analysis** | 3 | TrendAnalysisAgent, OpportunityScoringAgent, MarketIntelligenceAgent |
| **Training** | 2 | CharacterTrainingAgent, TrainedCreationAgent |
| **Security** | 2 | MemoryIsolationAgent, ContentAuditAgent |
| **Business** | 5 | CompetitorAnalysisAgent, CustomerResearchAgent, BrandStrategyAgent, ContentStrategyAgent (business), MarketingStrategyAgent |
| **Development** | 5 | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent, PromptEngineeringAgent |
| **Blockchain** | 5 | BlockchainAuditCoordinator, SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent, ExploitDetectorAgent |
| **Legal** | 1 | LegalDocDrafterAgent |
| **Narrative** | 4 | NarrativeDriftCoordinator, NarrativeHistorianAgent, TrendBreakDetectorAgent, CulturalImpactAgent |
| **Content Studio** | 4 | AutonomousContentStudioCoordinator, TopicMinerAgent*, ContrarianAgent*, PerformanceAnalystAgent* |
| **Podcast** | 4 | PodcastCoordinatorAgent, DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent |
| **Rendering** | 1 | ResolveAgent |
| **Orchestration** | 4 | WorkflowAgent, WorkflowOrchestrationAgent, OpportunityPipelineAgent, ContentExecutorAgent |
| **Campaign** | 2 | CampaignOrchestratorAgent, AISeriesWorkflowAgent |
| **Stocks** | 9 | StockAuditCoordinator, StockAnalystAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, MarketAnomalyDetectorAgent, BullCaseAgent, BearCaseAgent, SignalScannerAgent, MarketIntelligenceCoordinator |
| **Markets** | 3 | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector |
| **Entry Point** | 1 | PersonalAssistantAgent |
| **Special** | 3 | ThinkingAgent, TechnicalDocumentAgent, SystemIntelligenceAgent |

*\* = Non-routable (sub-agents used internally by AutonomousContentStudioCoordinator)*

### Agent Architecture
- **BaseAgent** - All agents inherit TimeTravelMixin, learning hooks, memory creation, **workspace integration** (Session 695)
- **Router** - `core/agent_router.py` - Deterministic routing (no LLM)
- **Learning** - All agents connected to collective intelligence system
- **SKIN Layer** - All agents can write to real project workspaces (Session 695)
- **Coordinators** - 5 coordinator agents manage teams of sub-agents:
  - BlockchainAuditCoordinator → 4 blockchain sub-agents
  - StockAuditCoordinator → 5 stock sub-agents
  - MarketIntelligenceCoordinator → 4 market sub-agents
  - NarrativeDriftCoordinator → 3 narrative sub-agents
  - AutonomousContentStudioCoordinator → 3 content sub-agents

---

## Spider Network (77 Spiders)

Real data sources across 20+ categories. 72 working, 5 need API keys.

| Category | Count | Examples |
|----------|-------|----------|
| **News/Media** | 10 | TechCrunch, TheVerge, BBC, CNN, NPR, Reuters, NewsAPI |
| **Financial** | 9 | CoinGecko, YahooFinance, Polygon, Finnhub, Kalshi, TheOdds |
| **Tech** | 8 | HackerNews, DevTo, GitHub, Ars Technica, Kickstarter |
| **Legal** | 6 | CourtListener, FindLaw, LII, Colorado Family Law, Justia |
| **Education** | 5 | Teachable, Udemy, Coursera, Kaggle |
| **Specialty Tech** | 5 | DefenseOne, MobiHealthNews, SecurityWeek, Wired, MIT Tech Review |
| **Community** | 4 | Reddit (8 subs), BlueSky, Discord, HackerNoon |
| **Entertainment** | 4 | Spotify, Giphy, YouTube, Polygon Gaming |
| **Lifestyle** | 4 | Lifehacker, Travel, Parenting, Food |
| **Other** | 22 | Startups, AI/ML, Content, Jobs, Weather, Science, Visual |

**Data Methods:** REST API (32), RSS (30), Web Scraping (10), Playwright (2), JSON (3)

---

## GPT-5-mini Configuration

**Critical:** GPT-5-mini is a reasoning model with different parameters!

```python
# CORRECT
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000  # NOT max_tokens
    # NO temperature parameter!
)
```

---

## Troubleshooting

```bash
# Full restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery

# macOS: If Celery crashes with SIGSEGV (Session 735 fix)
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l INFO --pool=solo

# Health check
curl http://localhost:8000/health/ping/

# Database check
.venv/bin/python manage.py shell -c "from core.models_unified_system import Agent; print(f'Agents: {Agent.objects.count()}')"
```

---

## Recent Sessions

| Session | Focus | Handoff |
|---------|-------|---------|
| **810** | **MASSIVE Celery Beat Fix** - Discovered settings.py CELERY_BEAT_SCHEDULE overrides celery.py when using DatabaseScheduler. 187 tasks were NOT running. Created `add_critical_celery_tasks.py` command with 94 critical tasks. Restored 60 missing tasks including ALL 11 body system health checks and ALL 15 agent category rotation tasks. Enabled tasks: 168→228. | See `00-START-NEXT-SESSION.md` |
| **806** | **Personal Assistant Context Optimization** - 4-component architecture to reduce context overload. ToolCategoryRouter (47→10 tools via 8 categories), ContextBudgetManager (tiktoken token tracking, 4,000 token budget), LazyContextLoader (16→2-5 context sections), ContextSummarizer (5-10x compression). Created 4 new services, modified 4 existing files. Token savings: ~70%. 1 PR merged (#82). | `SESSION_806_CONTEXT_OPTIMIZATION.md` |
| **805** | **Learning System Fix** - Fixed 3 critical issues identified by auto-generated blogs. (1) Anomaly detection false positives - added minimum baseline. (2) Missing learnings - added `_extract_halt_learning()` + backfilled 85 learnings. (3) Negative learning weight - fixed safety keyword classification v1.2. Learning coverage: 13%→100%, Net weight: -3.169→-0.944. Gate imbalance confirmed as by-design. 4 PRs merged. | See `00-START-NEXT-SESSION.md` |
| **804** | **Auto-Generated Blog Visibility Fix** - Fixed bug where 32 auto-generated blogs were invisible in Human Interface. Added `_create_blog_attention_item()` to autonomous_action_executor.py at all 4 SelfBlog creation sites. | See `00-START-NEXT-SESSION.md` |
| **803** | **LLM Cost Tracking + AI Assistant Performance** - Added cost tracking to LLMCallLog, meta question detection to skip spider data (88s→10s for "tell me about this system"), Daphne timeout increase to 120s. 4 PRs merged. | See `00-START-NEXT-SESSION.md` |
| **797** | **Integration Deepening** - Frontend batch actions + consultation triggers. Gate/opportunity consultations for human approval via PA chat. PR #17-21: QuerySet fix, full system scope prompt, batch UI, approve_gate/waive_gate/execute_opportunity handlers. | `SESSION_797_INTEGRATION_DEEPENING.md` |
| **796** | **Human-AI Assistant Connection** - 3 phases complete. PA surfaces pending decisions, batch_decide/auto_execute/consult actions, consultation response loop with pattern matching. | `SESSION_796_CONTEXT_PRESERVATION.md` |
| **795** | **Reasoning Engine Explained** - Gate system clarity, reasoning documentation | `SESSION_795_REASONING_ENGINE_EXPLAINED.md` |
| **784** | **Documentation Index Browser** - Cognitive Build Ledger UI. `build_docs_index` v2.2 with code block filtering, link context (occurrences + snippets), broken links detection. Backend API (4 endpoints), DocsIndexPage with stats dashboard, filterable list, DocDetailsPanel showing cross-references. 1,512 docs, 1,816 links, 100 broken, 50 orphans. | See commits |
| **783** | **Spider News Feed** - Reddit/Yahoo-style human-facing feed for spider data with agent annotations. New SpiderDataAnnotation model (8 annotation types), 6 API endpoints, BaseAgent._annotate_spider_data() method, SpiderFeedPage frontend (588 lines) with filters, voting, trending section. Agents can flag items as useful/profitable/podcast_worthy/breaking_news/etc. | `SESSION_783_SPIDER_NEWS_FEED.md` |
| **781** | **Agent Conversation Voice Fixes** - 3-level improvement for repetitive styles. Level 2: 22 role-anchored disagreement styles in CONVERSATION_ROLES. Level 1: Opener de-duplication with tracking. Level 3: Discourse memory tracking 50+ phrases across 5 categories. Eliminates "I'd push back slightly" repetition. | `SESSION_781_AGENT_VOICE_FIXES.md` |
| **779** | **PromptEngineeringAgent Created** - Created the missing PromptEngineeringAgent class (5 tools: design_prompt, optimize_prompt, create_prompt_library, analyze_prompt, generate_system_prompt). All 74 agents now verified working. | See commits |
| **778** | **Full Agent Rotation Test** - Executed all 74 agents across 15 categories via SKIN Layer. 73/74 succeeded (PromptEngineeringAgent missing class). ~2 hours runtime, 73 workspace files generated. Full rotation verified. | `00-START-NEXT-SESSION.md` |
| **771** | **Tool Result Rendering + RevenueMetrics Fix** - Added `renderToolResult()` to OrchestrationPage for smart JSON formatting (topics as pills, discussions as lists). Fixed `update_metrics_for_date` error in RevenueMetrics proxy class. | See commits |
| **770** | **Content Quality + Podcast TTS** - ContentQualityBlacklist model, TopicDiversityTracker, podcast TTS cost tracking, audio player component | See commits |
| **768** | **Memory Safety Classification** - Prevents test/exploratory content from polluting learning. Added `safety_class` (test_only/exploratory/candidate/approved) + `poison_risk_score` to AgentMemory. Added `health_check_mode` to BaseAgent. Embedding only for approved + low-risk content. | `SESSION_768_MEMORY_SAFETY_CLASSIFICATION.md` |
| **763** | **Mission Control System** - Wired agent outputs to Human Page with executable action buttons. Created ActionableOutputConfig in BaseAgent, MissionControlExecutor service (17 handlers), execute endpoint, dynamic UI actions. Configured 6 agents. **Foundation for Orchestration Layer** | `SESSION_763_MISSION_CONTROL_SYSTEM.md` |
| **761** | **Learning Tab Fixes + Activity Modal + Monitoring** - Fixed Knowledge Transfer effectiveness gain (was 0%, now uses usefulness_score). Added Generic Activity Detail Modal (all cards clickable). Created 3 monitoring API endpoints. Fixed dream "one"/"this" bug. Verified all services running (470 executions/24h, 97.7% success) | `SESSION_761_LEARNING_TAB_FIXES.md` |
| **760** | **Agent Output Detail Modal** - Created comprehensive modal to view full agent execution output_data. Backend APIs for execution history/detail. Type-safe frontend with special formatting for images, tool results, research. Fixed TypeScript errors, neural-orchestra 404, async thread executor error | `SESSION_760_AGENT_OUTPUT_DETAIL_MODAL.md` |
| **759** | **Memory Palace & Blog Surfacing Fixes** - Fixed Neural Orchestra Learning Card (0s → real data), ContentWriterAgent blogs surface in Human Interface, backfill command with age filter, error messages in failure memories, tool names display correctly | `SESSION_759_MEMORY_BLOG_FIXES.md` |
| **758** | **Integration Health Observability** - Added context tracking to all agent execution entry points. 100% context injection (spider data, learning patterns, advisor insights). Fixed Celery health detection. All 73 agents tested successfully | `SESSION_758_INTEGRATION_HEALTH_OBSERVABILITY.md` |
| **753** | **Memory Palace Data Gap Audit** - Comprehensive backwards audit revealing ~60% of data not displayed. Found 2 entire models with NO UI (MemoryConnection, ClusterEvolution), 3 unused API endpoints, 10+ hidden fields. Created 600+ line implementation plan for all missing features | `SESSION_753_MEMORY_PALACE_DATA_GAP_AUDIT.md` |
| **752** | **Error Tracking System & Live Feed Fix** - Created error tracking doc, fixed AgentContribution tracking (Live Feed stale 39 days), fixed Learning Orchestrator NoneType error, added thumbnail images to Live Feed cards | `SESSION_752_ERROR_TRACKING_AND_LIVE_FEED_FIX.md` |
| **751** | **Agent Social & Neural Orchestra Audit** - Fixed Conversations tab (auth, participant rendering, dates), Neural Orchestra (feed items, learning metrics). Confirmed 0 active agents is correct - no recent activity | `SESSION_751_SOCIAL_AND_ORCHESTRA_AUDIT.md` |
| **750** | **Time Travel Page Audit + Agent Integration** - Fixed frontend decision types, backend API signatures, duration display, simulation data. Added Time Travel to 28 remaining agents (71/73 = 96%) | `SESSION_750_TIME_TRAVEL_AUDIT.md` |
| **749** | **Mood Page & Time Capsules Audit** - Fixed Mood Page CRUD, Time Capsules GPT-5-mini token limits | `SESSION_749_MOOD_TIME_CAPSULES.md` |
| **746** | **Data Display Enhancements** - Comprehensive audit + fixes for hidden API data. Human Page (stats, decision history), Betting Page (singles vs parlays, per-sport, wager legs), Dashboard (network visualization), Intelligence Page (gate details, execution history). Data display coverage: 60% → 85% | `SESSION_746_DATA_DISPLAY_ENHANCEMENTS.md` |
| **745** | **Watch & Verify Feature** - Arbitrage paper trading on Human Page, Watching tab on Betting Page, deduplication for attention items | `SESSION_745_API_UI_COVERAGE_AUDIT.md` |
| **744** | **Integration Roadmap COMPLETE** - All 5 phases done (Celery health, spider-to-agent, learning patterns, advisor wisdom, feedback loops). Cross-agent delegation enabled for all 74 agents with 3-level chain support. Integration score: 95% | `SESSION_744_INTEGRATION_ROADMAP_COMPLETE.md` |
| **743** | **Content Diversity Orchestrator** - Ensures AI-generated content is diverse and non-repetitive | `SESSION_743_CONTENT_DIVERSITY_ORCHESTRATOR.md` |
| **742** | **Human Page Data Display** - Enhanced Human dashboard with real data | `SESSION_742_HUMAN_PAGE_DATA_DISPLAY.md` |
| **741** | **Content Channels Page + Episode Title Fix** - New Content Channels page to view autonomous content (3 channels, 91 episodes), fixed generic episode titles with GPT-generated unique titles, management command for bulk title fix | `SESSION_741_CONTENT_CHANNELS_PAGE.md` |
| **736** | **System Audit + Integration Reality** - Component audit passed (100%), but integration audit revealed critical gaps: 95% agents ignore spider data, 50 agents never executed, memory system dormant. Integration score: 30% | `docs/audits/SESSION_736_INTEGRATION_REALITY_REPORT.md` |
| **735** | **Cost Tracking & Output Formatting** - Fixed Celery SIGSEGV crashes, implemented orchestration cost tracking, formatted output modal with markdown parsing | `SESSION_735_COST_TRACKING_OUTPUT_FORMATTING.md` |
| **733** | **Embedding Fixes + Mythology Lab** - Fixed document embedding bugs (recursion, async), created Mythology Lab hallucination detection UI | See commits |
| **723** | **SKIN System** - 9th body system for workspace output monitoring (file writes, project changes, rollback) + Celery health fix | `SESSION_723_SKIN_BODY_SYSTEM.md` |
| **722** | **BRAIN System** - 8th body system for cognitive processing (LLM calls, conversations, reasoning) | `SESSION_722_BRAIN_SYSTEM.md` |
| **721** | **Body Health Detail Views** - Complete data display for all 7 body systems | See commits |
| **720** | **LUNGS Detail View** - Fixed LUNGS display + Digestive system documentation | See commits |
| **719** | **Body Health Refinements** - 7 commits for body system polish | See commits |
| **718** | **Spider Integration + Memory Clusters** - Spider Integration page (~450 lines), Memory Clusters tab in Memory Palace (~380 lines), 14/14 sci-fi features complete (100%) | See commits |
| **717** | **Conversation Contract Page** - Quality analytics for agent conversations (~500 lines), contract compliance visualization | See commits |
| **716** | **Sci-Fi Pages** - 8 new React pages (Evolution, Mood, Time Capsules, Time Travel, Social, Advisors, Relationships, Neural Orchestra), 11/14 sci-fi features now have UI | `SESSION_716_SCIFI_PAGES.md` |
| **712** | **Body UI Unification** - HeartWidget rewrite for 7 systems, Admin cleanup (-2,106 lines), body cards on 4 pages | `SESSION_712_BODY_UI_UNIFICATION.md` |
| **707** | **MUSCULAR System** - Agent work execution monitoring (10 muscle groups, 8 API endpoints, fatigue/strain detection) | `SESSION_707_MUSCULAR_SYSTEM.md` |
| **706** | **DIGESTIVE System** - Data ingestion & processing (8 ingestion routes, 8 API endpoints) | `SESSION_706_DIGESTIVE_SYSTEM.md` |
| **705** | **IMMUNE SYSTEM** - Security & threat detection (14 threat patterns, 10 API endpoints, quarantine) | `SESSION_705_IMMUNE_SYSTEM.md` |
| **704** | **SPINE - Central API Router** - Route patterns, health-aware routing, request tracing (19 patterns, 12 categories) | `SESSION_704_SPINE_ROUTER.md` |
| **703** | **CIRCULATORY System** - Data flow monitoring (Redis queues, Celery tasks, WebSocket, event streams, 9 routes) | `SESSION_703_CIRCULATORY_SYSTEM.md` |
| **702** | **LUNGS Service** - Resource & capacity management (token/cost budgets, 6 defaults, alerts) | `SESSION_702_LUNGS_SERVICE.md` |
| **701** | **HEART Service** - Central health monitoring (Brain, Nervous System, Organs, Sensory, Skin, Memory) | `SESSION_701_HEART_SERVICE.md` |
| **700** | **LLM Routing UI + File Tree** - Hierarchical file tree for workspaces, frontend ready | `FRONTEND_INTEGRATION_NOTE.md` |
| **699** | **LLM Routing API Endpoints** - 7 API endpoints + 75 agent configs (all agents mapped) | `FRONTEND_INTEGRATION_NOTE.md` |
| **698** | **Agent Router Expansion** - All 74 agents routable to optimal LLM models | See Session 699 |
| **697** | **Frontend Rich Data Display** - 6 UI enhancements exposing hidden API data (Dashboard stats, Knowledge Transfer Modal, Gate Checklist Viewer) + Multi-model LLM routing | `SESSION_697_FRONTEND_RICH_DATA.md`, `SESSION_697_ENHANCED_NERVOUS_SYSTEM.md` |
| **695** | **SKIN Layer** - All 74 agents can write to real project workspaces | `SESSION_695_SKIN_LAYER_COMPLETE.md` |
| **692** | **Prediction Detail Modal** - Clickable predictions, full text, 3 bug fixes | `SESSION_692_PREDICTION_DETAIL_MODAL.md` |
| **691** | **Implementation Review UI** - Modal for viewing/acting on pilot implementations | `SESSION_691_IMPLEMENTATION_REVIEW_UI.md` |
| **690** | **Implementation Pipeline** - Auto-generate and execute implementations for pilots | `SESSION_690_IMPLEMENTATION_PIPELINE.md` |
| **688-689** | **Intelligence Page** - Gates, Pilots, Opportunities, Predictions tabs complete | Multiple handoffs |
| **687** | **UI Data Display Audit** - Dashboard + Human page real data, Human Attention Bridge | `SESSION_687_UI_DATA_DISPLAY_AUDIT.md` |
| **686** | **Human Interface Layer** - Complete human-in-the-loop system | `docs/designs/HUMAN_INTERFACE_LAYER.md` |
| **677** | **Agent-Model Router Phase 1** - Foundation: models, registry, router, 24 configs | `SESSION_677_AGENT_MODEL_ROUTER_PHASE1.md` |
| **674** | **Universal Agent Tool** - 1 tool connects PA to ALL 69 agents | `SESSION_674_UNIVERSAL_AGENT_TOOL.md` |
| **666** | **Deep System Review** - SYSTEM_INTEGRATION_GUIDE.md (798 lines) | `docs/current/SYSTEM_INTEGRATION_GUIDE.md` |
| **663** | **SystemIntelligenceAgent** + **Agents Tab** + **Activity/Learning Tabs** | `SESSION_663_SYSTEM_INTELLIGENCE_AGENT.md` |
| **655** | **Gate Pipeline Fixes** + UI Enhancements | *(commits: c5aa87cd, ae29466c, 9b82eeec)* |
| **654** | **Autonomous Gate Approval Pipeline** + UI Reorganization | `SESSION_654_AUTONOMOUS_GATE_APPROVAL.md`, `SESSION_654_COMMAND_CENTER_SUBTABS.md` |
| **653** | **7/7 Full Composability** - All walls fixed | `SESSION_653_CROSS_DOMAIN_COMPOSABILITY_AUDIT.md` |
| 652 | Podcast Studio + Campaign Orchestrator Activated | `SESSION_652_PODCAST_STUDIO_ACTIVATION.md`, `SESSION_652_CAMPAIGN_ACTIVATION.md` |
| 651 | Empty Models Audit - 4/6 have data | `SESSION_651_EMPTY_MODELS_AUDIT.md` |
| 650 | Orphaned Services Audit - all services used | `SESSION_650_ORPHANED_SERVICES_AUDIT.md` |
| 648 | Celery Task Scheduling - 14 tasks added | `SESSION_648_CELERY_TASK_SCHEDULING.md` |
| 647 | Decision Executor Analysis - was duplicate | `SESSION_647_DECISION_EXECUTOR_ANALYSIS.md` |
| 646 | Data Flow Verification + Disconnected Features Audit | `SESSION_646_DATA_FLOW_VERIFICATION.md` |
| 645 | 71 Agents Verified + Spider Verification | `SESSION_645_71_AGENTS_VERIFIED.md` |
| 637 | AgentRouter expansion (47→68 routable) + agent fixes | `SESSION_637_SYSTEM_AUDIT_FIXES.md` |
| 636 | System Health Check command + Agent Introduction Party | `SESSION_636_SYSTEM_HEALTH_CHECK.md` |
| 596 | Experiment Tracking Registry - KPI ownership for pilots | `SESSION_596_EXPERIMENT_TRACKING.md` |
| 595 | Pilot Dashboard - Monitor running/completed pilots | `SESSION_595_PILOT_DASHBOARD.md` |
| 594 | AI-Powered Governance - Auto-completion & ThinkingAgent eval | `SESSION_594_PILOT_AUTO_COMPLETION.md` |
| 593 | ThinkingAgent Auto-Gates - AI generates pilot gates | `SESSION_593_THINKING_AGENT_AUTO_GATES.md` |
| 592 | Pilot Readiness Gate Complete - Full checklist system | `SESSION_592_PILOT_READINESS_GATE_COMPLETE.md` |

For older sessions, see `docs/handoffs/` directory.

---

## Documentation

### Core Documentation
| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [CAPABILITIES.md](docs/CAPABILITIES.md) | Full feature list |
| [AGENTS.md](docs/AGENTS.md) | Agent documentation (74 agents) |
| [SPIDERS.md](docs/SPIDERS.md) | Spider network (77 spiders) |
| [SERVICES.md](docs/SERVICES.md) | Services layer (93 services) |
| [SCIFI_FEATURES.md](docs/SCIFI_FEATURES.md) | 14 Sci-Fi AI features |
| [DATABASE_MODEL_REFERENCE.md](docs/DATABASE_MODEL_REFERENCE.md) | **IMPORTANT:** Which DB table for what |
| [WORKSPACE_USER_GUIDE.md](docs/WORKSPACE_USER_GUIDE.md) | SKIN Layer workspace guide |

### Documentation Indexes (Session 785)
| Index | Contents |
|-------|----------|
| [Handoffs Index](docs/handoffs/INDEX.md) | 447 session handoffs (Sessions 197-785) |
| [Audits Index](docs/audits/INDEX.md) | 61 system audits |
| [Reports Index](docs/reports/INDEX.md) | 30 status reports |
| [Architecture Index](docs/architecture/INDEX.md) | 22 architecture docs |
| [Features Index](docs/features/INDEX.md) | 17 feature docs |
| [Guides Index](docs/guides/INDEX.md) | 35 implementation guides |
| [Plans Index](docs/plans/INDEX.md) | 9 planning docs |
| [APIs Index](docs/apis/INDEX.md) | 7 API integration docs |

### Key References
| Doc | Purpose |
|-----|---------|
| [INTEGRATION_ROADMAP_2026.md](docs/roadmaps/INTEGRATION_ROADMAP_2026.md) | 5-phase integration plan |
| [System Audit](docs/audits/SESSION_736_COMPREHENSIVE_SYSTEM_AUDIT.md) | Component audit (100% pass) |
| [ERROR_TRACKING.md](docs/ERROR_TRACKING.md) | Track errors discovered during sessions |
| [MEMORY_SAFETY_CLASSIFICATION.md](docs/MEMORY_SAFETY_CLASSIFICATION.md) | Memory safety classification |
| [UI_COMPREHENSIVE_AUDIT.md](docs/UI_COMPREHENSIVE_AUDIT.md) | UI audit - 43 pages, 55+ APIs |

---

## Platform Phases (All Complete)

| Phase | Focus | Status |
|-------|-------|--------|
| 1-6 | Creative Intelligence Empire | DONE |
| 7-15 | Sci-Fi Features (Dreams, Memory, Evolution, etc.) | DONE |
| Super Platform | Unified intelligence coordinator | DONE |

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
