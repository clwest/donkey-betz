# CLAUDE - AI Session Entry Point

**Last Updated:** December 28, 2025 - Session 567
**Status:** 100% Reality Score | Django Web App | ALL 6 PHASES COMPLETE + 15 Sci-Fi Features

## System Stats (Session 567 Full Audit)
| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 71 | 47 routable, 24 sub-agents |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **Database Models** | 324+ | 37 categories |
| **Celery Tasks** | 226 | 53 scheduled (Beat) |
| **Services** | 93 | Business logic layer |
| **Discord Commands** | 112 | 29 Cog categories |
| **Advisors** | 25 | Famous figures + domain experts |
| **Sci-Fi Features** | 14 | All active (Session 567 cleanup) |

**Chief of Staff Layer:** Human-in-the-loop review system with Pro/Con interrogation
**Prediction Markets:** Kalshi integration with RSA-PSS authenticated trading
**Betting Dashboard:** Web UI with 8 sub-tabs, Push Notifications for Arb Alerts
**LLM Model:** GPT-5-mini (reasoning model - uses `max_completion_tokens`, no `temperature`)

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
- `core/agents/` - **Canonical agent location** (71 agents with learning hooks)
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
| `core/services/review_document.py` | Chief of Staff review generation |
| `core/services/side_chat.py` | Pro/Con interrogation service |

---

## Agent Ecosystem (71 Agents)

All agents in `core/agents/` with learning hooks connected to collective intelligence.
**47 routable** (in AgentRouter) | **24 non-routable** (sub-agents managed by coordinators)

| Category | Count | Agents |
|----------|-------|--------|
| **Creation** | 4 | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| **Editing** | 2 | ImageEditingAgent, VideoEditingAgent |
| **Research** | 1 | ResearchAgent |
| **Content Writing** | 1 | ContentWriterAgent |
| **Strategy** | 4 | ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent |
| **Executive** | 4 | CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent |
| **Analysis** | 3 | TrendAnalysisAgent, OpportunityScoringAgent, MarketIntelligenceAgent* |
| **Training** | 2 | CharacterTrainingAgent, TrainedCreationAgent |
| **Security** | 2 | MemoryIsolationAgent, ContentAuditAgent |
| **Business** | 5 | CompetitorAnalysisAgent, CustomerResearchAgent, BrandStrategyAgent*, ContentStrategyAgent (business)*, MarketingStrategyAgent* |
| **Development** | 4 | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent |
| **Blockchain** | 5 | BlockchainAuditCoordinator, SmartContractAuditorAgent*, TransactionMonitorAgent*, WhaleWatcherAgent*, ExploitDetectorAgent* |
| **Legal** | 1 | LegalDocDrafterAgent |
| **Narrative** | 4 | NarrativeDriftCoordinator*, NarrativeHistorianAgent*, TrendBreakDetectorAgent*, CulturalImpactAgent* |
| **Content Studio** | 4 | AutonomousContentStudioCoordinator, TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent |
| **Podcast** | 4 | PodcastCoordinatorAgent, DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent |
| **Rendering** | 1 | ResolveAgent |
| **Orchestration** | 4 | WorkflowAgent, WorkflowOrchestrationAgent*, OpportunityPipelineAgent*, ContentExecutorAgent* |
| **Campaign** | 2 | CampaignOrchestratorAgent, AISeriesWorkflowAgent |
| **Stocks** | 9 | StockAuditCoordinator, StockAnalystAgent*, MarketMovementMonitorAgent*, InstitutionalWatcherAgent*, MarketAnomalyDetectorAgent*, BullCaseAgent*, BearCaseAgent*, SignalScannerAgent*, MarketIntelligenceCoordinator* |
| **Markets** | 3 | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector |
| **Entry Point** | 1 | PersonalAssistantAgent |
| **Special** | 1 | ThinkingAgent* |

*\* = Non-routable (sub-agents orchestrated by coordinators)*

### Agent Architecture
- **BaseAgent** - All agents inherit TimeTravelMixin, learning hooks, memory creation
- **Router** - `core/agent_router.py` - Deterministic routing (no LLM)
- **Learning** - All agents connected to collective intelligence system
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
| 567 | Full System Audit - 71 agents, 77 spiders, 324+ models, 226 Celery tasks, 93 services | `SESSION_567_FULL_SYSTEM_AUDIT.md` |
| 566 | Intelligence Sources UI panel + GPT-5-mini token fix | - |
| 565 | Context-Aware PA with Platform Intelligence | - |
| 562 | Push Notifications for Arb Alerts - Web Push API, service worker, preferences UI | `SESSION_562_PUSH_NOTIFICATIONS.md` |
| 561 | Line Movement Charts - Historical odds tracking, movement visualization, movers API | `SESSION_561_LINE_MOVEMENT_CHARTS.md` |
| 560 | Betting Dashboard Enhancements - Futures tab, Kelly Calculator, Bet Logging, WebSocket updates | `SESSION_560_BETTING_DASHBOARD_ENHANCEMENTS.md` |
| 559 | Betting Dashboard UI - Web interface for odds, arbitrage, bankroll tracking | `SESSION_559_BETTING_DASHBOARD_UI.md` |
| 556 | Chief of Staff Extensions - Discord commands, Boardroom UI, auto-reviews, dream reviews | `SESSION_556_CHIEF_OF_STAFF_EXTENSIONS.md` |
| 555 | Chief of Staff Layer - Human-in-the-loop with Pro/Con review documents | `SESSION_555_CHIEF_OF_STAFF_LAYER.md` |
| 553 | PA ↔ Intelligence Mapping - 99.8% of knowledge invisible to PA | `SESSION_553_PA_INTELLIGENCE_MAPPING.md` |
| 552 | Research Demo Tab Complete Fix - APIs, colors, live feed, self-blog | `SESSION_552_RESEARCH_DEMO_FIXES.md` |
| 551 | Boardroom Deduplication + Pending Dreams Tracking | `SESSION_551_BOARDROOM_DEDUPLICATION.md` |

For older sessions, see `docs/handoffs/` directory.

---

## Documentation

| Doc | Purpose |
|-----|---------|
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/CAPABILITIES.md` | Full feature list |
| `docs/AGENTS.md` | Agent documentation (71 agents) |
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
