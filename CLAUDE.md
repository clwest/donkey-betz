# CLAUDE - AI Session Entry Point

**Last Updated:** January 6, 2026 - Session 706
**Status:** 100% Reality Score | Django Web App | ALL 6 BODY SYSTEMS COMPLETE

## System Stats (Session 706)
| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 72 | All synced to database + workspace integration |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **PA Tools** | 83 | +workspace_tool for SKIN layer |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **LLM Models** | 16 | GPT-5 family, Claude 4, Llama, DeepSeek V3, Gemini 2.5/3 |
| **Agent LLM Configs** | 75 | All agents mapped to optimal models (Session 699) |
| **LLM API Endpoints** | 7 | Status, providers, models, configs, logs, analytics (Session 699) |
| **ML Models** | 17 | 15 working (Sessions 677-685) |
| **Database Models** | 356+ | +3 DIGESTIVE models (IngestionRoute, DigestivePulse, DigestionStatus) |
| **Celery Tasks** | 136 | +check_digestion task |
| **Services** | 103 | +digestive.py (DigestiveSystemService) |
| **Discord Commands** | 112 | 29 Cog categories |
| **Advisors** | 25 | Famous figures + domain experts |
| **Sci-Fi Features** | 14 | All active |
| **Running Pilots** | 18 | Auto-deployed via autonomous pipeline |
| **OPEN Systems** | 7/7 | Full composability (Session 653) |
| **Body Systems** | 6 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE |

**DIGESTIVE System:** Data ingestion & processing - 8 ingestion routes, 8 API endpoints, bottleneck detection (Session 706)
**IMMUNE System:** Security & threat detection - 14 threat patterns, 10 API endpoints, quarantine management (Session 705)
**SPINE Service:** Central API routing - 19 route patterns across 12 categories, health-aware routing (Session 704)
**CIRCULATORY System:** Data flow monitoring - tracks data movement through the system (Session 703)
**LUNGS Service:** Resource & capacity management - LLM budget tracking (Session 702)
**HEART Service:** Central health monitoring - checks Brain, Nervous System, Organs, Sensory, Skin, Memory every 60s (Session 701)
**SKIN Layer:** All 72 agents can now write to real project workspaces with audit trail + rollback (Session 695)
**LLM Routing:** GPT-5 models use Responses API (max_completion_tokens, no temperature)

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

---

## Project Structure

### Key Directories
- `core/agents/` - **Canonical agent location** (72 agents with learning hooks)
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
| `core/services/review_document.py` | Chief of Staff review generation |
| `core/services/side_chat.py` | Pro/Con interrogation service |

---

## Agent Ecosystem (72 Agents)

All agents in `core/agents/` with learning hooks connected to collective intelligence.
**48 routable** (in AgentRouter) | **24 non-routable** (sub-agents and coordinator teams)

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
| **Development** | 4 | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent |
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

# Health check
curl http://localhost:8000/health/ping/

# Database check
.venv/bin/python manage.py shell -c "from core.models_unified_system import Agent; print(f'Agents: {Agent.objects.count()}')"
```

---

## Recent Sessions

| Session | Focus | Handoff |
|---------|-------|---------|
| **705** | **IMMUNE SYSTEM** - Security & threat detection (14 threat patterns, 10 API endpoints, quarantine) | `SESSION_705_IMMUNE_SYSTEM.md` |
| **704** | **SPINE - Central API Router** - Route patterns, health-aware routing, request tracing (19 patterns, 12 categories) | `SESSION_704_SPINE_ROUTER.md` |
| **703** | **CIRCULATORY System** - Data flow monitoring (Redis queues, Celery tasks, WebSocket, event streams, 9 routes) | `SESSION_703_CIRCULATORY_SYSTEM.md` |
| **702** | **LUNGS Service** - Resource & capacity management (token/cost budgets, 6 defaults, alerts) | `SESSION_702_LUNGS_SERVICE.md` |
| **701** | **HEART Service** - Central health monitoring (Brain, Nervous System, Organs, Sensory, Skin, Memory) | `SESSION_701_HEART_SERVICE.md` |
| **700** | **LLM Routing UI + File Tree** - Hierarchical file tree for workspaces, frontend ready | `FRONTEND_INTEGRATION_NOTE.md` |
| **699** | **LLM Routing API Endpoints** - 7 API endpoints + 75 agent configs (all agents mapped) | `FRONTEND_INTEGRATION_NOTE.md` |
| **698** | **Agent Router Expansion** - All 72 agents routable to optimal LLM models | See Session 699 |
| **697** | **Frontend Rich Data Display** - 6 UI enhancements exposing hidden API data (Dashboard stats, Knowledge Transfer Modal, Gate Checklist Viewer) + Multi-model LLM routing | `SESSION_697_FRONTEND_RICH_DATA.md`, `SESSION_697_ENHANCED_NERVOUS_SYSTEM.md` |
| **695** | **SKIN Layer** - All 72 agents can write to real project workspaces | `SESSION_695_SKIN_LAYER_COMPLETE.md` |
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

| Doc | Purpose |
|-----|---------|
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/CAPABILITIES.md` | Full feature list |
| `docs/AGENTS.md` | Agent documentation (72 agents) |
| `docs/SPIDERS.md` | Spider network (77 spiders) |
| `docs/SERVICES.md` | Services layer (93 services) |
| `docs/SCIFI_FEATURES.md` | 14 Sci-Fi AI features |

---

## Platform Phases (All Complete)

| Phase | Focus | Status |
|-------|-------|--------|
| 1-6 | Creative Intelligence Empire | DONE |
| 7-15 | Sci-Fi Features (Dreams, Memory, Evolution, etc.) | DONE |
| Super Platform | Unified intelligence coordinator | DONE |

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
