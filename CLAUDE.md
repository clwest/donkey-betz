# CLAUDE - AI Session Entry Point

**Last Updated:** December 27, 2025 - Session 562
**Status:** 100% Reality Score | Django Web App | ALL 6 PHASES COMPLETE + 15 Sci-Fi Features
**Spider Network:** 76 spiders | 20,712+ data records | 88.1% embeddings
**Agent Ecosystem:** 71 agents (47 routable) | Autonomous Content Generation | 3-Agent Debates
**Chief of Staff Layer:** Human-in-the-loop review system with Pro/Con interrogation
**Prediction Markets:** Kalshi integration with RSA-PSS authenticated trading
**Betting Dashboard:** Web UI with 8 sub-tabs, Push Notifications for Arb Alerts (Session 562)
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
- `core/services/` - Business logic services
- `core/prompts/` - Central prompt registry
- `ai_core/spiders/` - Spider network (72 spiders)
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

## Spider Network (72 Spiders)

Real data sources across 20 categories:
- **Tech:** TechCrunch, The Verge, Wired, MIT Tech Review, HackerNews API
- **Jobs:** RemoteOK, WeWorkRemotely, Adzuna API
- **Financial:** CoinGecko API, Yahoo Finance API, Etherscan
- **Creative:** Dribbble, Behance, Unsplash API
- **Community:** Reddit (20+ subreddits)

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
| 562 | Push Notifications for Arb Alerts - Web Push API, service worker, preferences UI | `SESSION_562_PUSH_NOTIFICATIONS.md` |
| 561 | Line Movement Charts - Historical odds tracking, movement visualization, movers API | `SESSION_561_LINE_MOVEMENT_CHARTS.md` |
| 560 | Betting Dashboard Enhancements - Futures tab, Kelly Calculator, Bet Logging, WebSocket updates | `SESSION_560_BETTING_DASHBOARD_ENHANCEMENTS.md` |
| 559 | Betting Dashboard UI - Web interface for odds, arbitrage, bankroll tracking | `SESSION_559_BETTING_DASHBOARD_UI.md` |
| 556 | Chief of Staff Extensions - Discord commands, Boardroom UI, auto-reviews, dream reviews | `SESSION_556_CHIEF_OF_STAFF_EXTENSIONS.md` |
| 555 | Chief of Staff Layer - Human-in-the-loop with Pro/Con review documents | `SESSION_555_CHIEF_OF_STAFF_LAYER.md` |
| 553 | PA ↔ Intelligence Mapping - 99.8% of knowledge invisible to PA | `SESSION_553_PA_INTELLIGENCE_MAPPING.md` |
| 552 | Research Demo Tab Complete Fix - APIs, colors, live feed, self-blog | `SESSION_552_RESEARCH_DEMO_FIXES.md` |
| 551 | Boardroom Deduplication + Pending Dreams Tracking | `SESSION_551_BOARDROOM_DEDUPLICATION.md` |
| 520 | Projects Tab Unification - Fixed CreativeProject vs PartnershipProject disconnect | `SESSION_520_PROJECTS_TAB_AUDIT.md` |
| 519 | Auto-Project Creation & Content Display | `SESSION_519_AUTO_PROJECT_CREATION_AND_CONTENT_DISPLAY.md` |
| 513 | Campaign Orchestrator Agent - Marketing hub | `SESSION_513_CAMPAIGN_ORCHESTRATOR.md` |
| 511 | ML Scoring Sub-Tab Enhancement | `SESSION_511_ML_SCORING_SUBTAB_ENHANCEMENT.md` |

For older sessions, see `docs/handoffs/` directory.

---

## Documentation

| Doc | Purpose |
|-----|---------|
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/CAPABILITIES.md` | Full feature list |
| `docs/AGENTS.md` | Agent documentation |
| `docs/SPIDERS.md` | Spider network details |
| `docs/SCIFI_FEATURES.md` | 15 advanced AI features |

---

## Platform Phases (All Complete)

| Phase | Focus | Status |
|-------|-------|--------|
| 1-6 | Creative Intelligence Empire | DONE |
| 7-15 | Sci-Fi Features (Dreams, Memory, Evolution, etc.) | DONE |
| Super Platform | Unified intelligence coordinator | DONE |

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
