# Backend Inventory & Documentation

**Last Updated:** April 26, 2026 - Session 1100 (refreshed counts; original Session 775 narrative below)
**Backend Stack:** Django 4.2 + Django REST Framework + Celery + Redis + PostgreSQL + Channels (WebSockets)
**Source of truth:** `docs/PLATFORM_INVENTORY.md` (regenerable). When this doc disagrees with PLATFORM_INVENTORY, that wins.

---

## Summary Stats

### Canonical Inventory

For current verified counts, use [`docs/PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md).
This document keeps historical notes and backend structure, but it no longer
repeats the live summary table so it cannot drift independently.

### Manual Snapshot (history)

| Metric | Count |
|--------|-------|
| **Total Python Lines** | 1,029,692 (Jan 2026 snapshot — line counts not re-verified Session 1100) |
| **Lines (excl. migrations)** | 956,014 (Jan 2026 snapshot) |
| **Django Apps** | 23 |
| **Django Models** | 570 |
| **URL Endpoints** | 1,831 |
| **Celery Tasks** | 365 |
| **Agents** | 83 in AGENT_MAP + 223 DB persona-eligible rows = 306 total |
| **Services** | 320 files / 112 `*Service` classes |
| **Spiders** | 80 (172 files including management) |
| **Views Files** | 200 |
| **Management Commands** | 153 |
| **WebSocket Consumers** | 67 |
| **Discord Commands** | 144 (96 `@*.command` + 48 `@app_commands.command`) |
| **Script Files** | 311 (Jan 2026 snapshot) |
| **Test Files** | 87+ (Jan 2026 snapshot) |

---

## Code Distribution

### All Top-Level Directories

| Directory | Lines | Files | Purpose |
|-----------|-------|-------|---------|
| `core/` | 528,007 | 1,200+ | Main Django application |
| `ai_core/` | 118,044 | 172 | Spider network |
| `scripts/` | 68,205 | 311 | Setup, migration, utility scripts |
| `archive/` | 54,985 | 193 | Archived/deprecated code |
| `intelligence/` | 45,935 | 103 | Intelligence Django app |
| `content/` | 21,825 | 71 | Content Django app |
| `tests/` | 19,705 | 87 | Test suite |
| `sports/` | 14,248 | 32 | Sports betting Django app |
| `agents/` | 14,024 | 93 | Additional agent definitions |
| `ml/` | 10,344 | 24 | Machine learning models |
| `persistence/` | 4,519 | 17 | Persistence Django app |
| `self_awareness/` | 4,322 | 13 | Self-awareness Django app |
| `mythology/` | 2,809 | 10 | Mythology/hallucination Django app |
| `resolve_node/` | 2,353 | 9 | DaVinci Resolve integration |
| `coleadership/` | 2,265 | 10 | Co-leadership features |
| `advisors/` | 1,640 | 2 | Advisor system |
| `style_memory/` | 1,594 | 11 | Style memory system |
| `pipelines/` | 1,499 | 11 | Data pipelines |
| `davinci_bridge/` | 1,359 | 3 | DaVinci bridge |
| `ml_pipeline/` | 1,128 | 2 | ML pipeline |
| `dashboard/` | 915 | 8 | Dashboard features |
| `rendering/` | 886 | 9 | Rendering services |
| `revenue/` | 799 | 2 | Revenue tracking |
| `workflows/` | 548 | 2 | Workflow definitions |
| `sports_betting/` | 464 | 7 | Sports betting utilities |
| `tools/` | 399 | 3 | Utility tools |
| `ml_intelligence/` | 367 | 2 | ML intelligence |
| Other small dirs | ~5,000 | 50+ | Various utilities |

### Core App Breakdown

| Subdirectory | Lines | Purpose |
|--------------|-------|---------|
| `core/services/` | 122,086 | Business logic services |
| `core/agents/` | 81,966 | AI agent implementations |
| `core/management/` | 17,130 | Django management commands |
| `core/super_platform/` | 7,550 | Super platform orchestration |
| `core/models/` | 5,163 | Additional model definitions |
| `core/tools/` | 4,281 | Agent tools |
| `core/assistant/` | 4,029 | Personal assistant logic |
| `core/tests/` | 3,598 | Test files |
| `core/learning_bridges/` | 2,810 | Learning system bridges |
| `core/prompts/` | 2,795 | Prompt templates |
| `core/views/` | 2,606 | Additional views |

---

## Largest Files

### Top 30 Python Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/tasks.py` | 24,896 | Celery task definitions |
| `core/models_unified_system.py` | 20,196 | Main unified models |
| `core/views_image.py` | 14,779 | Image generation views |
| `core/services/discord_bot.py` | 14,485 | Discord bot service |
| `core/agents/personal_assistant_agent.py` | 13,894 | Main PA agent |
| `core/personal_ai_assistant_enhanced.py` | 12,243 | Enhanced PA |
| `core/views_video.py` | 9,053 | Video generation views |
| `core/agents/legal/legal_doc_drafter_agent.py` | 7,753 | Legal document agent |
| `core/views_agent_learning.py` | 5,516 | Agent learning views |
| `core/urls.py` | 3,962 | URL routing (1,578 endpoints) |
| `core/services/workflow_orchestration_agent.py` | 3,427 | Workflow orchestration |
| `core/agents/base_agent.py` | 3,351 | Base agent class |
| `core/consumers.py` | 3,068 | WebSocket consumers |
| `core/consumers_base.py` | 3,068 | Base consumer classes |
| `core/views_odds_sports.py` | 2,936 | Sports betting views |
| `core/models.py` | 2,828 | Core models |
| `core/views_analytics.py` | 2,703 | Analytics views |
| `core/views_projects_api.py` | 2,567 | Projects API |
| `core/services/discord_notifications.py` | 2,273 | Discord notifications |
| `core/views_spider_intelligence.py` | 2,259 | Spider intelligence |

---

## Django Models (413 Total)

### By App

| App | Model Count | Examples |
|-----|-------------|----------|
| **core** | 301 | Agent, AgentExecution, CustomWorkflow, Memory, etc. |
| **content** | 22 | ContentPiece, ContentChannel, Episode |
| **sports** | 14 | SportEvent, Wager, BettingMarket |
| **agents** | 10 | AgentRegistry, AgentCapability |
| **persistence** | 7 | PersistentMemory, KnowledgeBase |
| **mythology** | 7 | MythologyTest, HallucinationCase |
| **django_celery_beat** | 6 | PeriodicTask, CrontabSchedule |
| **ai_intelligence** | 6 | Intelligence models |
| **intelligence** | 6 | Gate, Pilot, Opportunity |
| **self_awareness** | 6 | SelfAwareness models |

### Key Model Files

| File | Lines | Models |
|------|-------|--------|
| `models_unified_system.py` | 20,196 | 150+ models (main unified file) |
| `models.py` | 2,828 | Core models |
| `models_pilot_readiness.py` | 1,364 | Pilot system models |
| `models_autonomous_situations.py` | 1,011 | Situation trigger models |
| `models_situation_triggers.py` | 972 | Trigger definitions |
| `models_legal.py` | 920 | Legal document models |
| `models_partnership.py` | 895 | Partnership models |
| `models_llm_routing.py` | 791 | LLM routing models |
| `models_orchestration.py` | 534 | Orchestration models |
| `models_human_interface.py` | 482 | Human-in-the-loop models |

---

## Agents (72 Unique)

### By Category

| Category | Count | Agents |
|----------|-------|--------|
| **Top-Level** | 33 | BaseAgent, PersonalAssistantAgent, ResearchAgent, ContentWriterAgent, etc. |
| **Stocks** | 9 | StockAuditCoordinator, StockAnalystAgent, MarketMovementMonitorAgent, etc. |
| **Business** | 6 | CompetitorAnalysisAgent, CustomerResearchAgent, BrandStrategyAgent, etc. |
| **Blockchain** | 5 | BlockchainAuditCoordinator, SmartContractAuditorAgent, etc. |
| **Narrative** | 5 | NarrativeDriftCoordinator, NarrativeHistorianAgent, etc. |
| **Podcast** | 4 | PodcastCoordinatorAgent, DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent |
| **Executive** | 4 | CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent |
| **Strategy** | 4 | ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent |
| **Content** | 3 | ImageAgent, VideoAgent, AudioAgent |
| **Analysis** | 3 | TrendAnalysisAgent, OpportunityScoringAgent, MarketIntelligenceAgent |
| **Markets** | 3 | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector |
| **Legal** | 3 | LegalDocDrafterAgent, LegalResearchAgent, LegalAnalysisAgent |
| **Security** | 2 | MemoryIsolationAgent, ContentAuditAgent |
| **Training** | 2 | CharacterTrainingAgent, TrainedCreationAgent |

### Largest Agent Files

| Agent | Lines | Purpose |
|-------|-------|---------|
| `personal_assistant_agent.py` | 13,894 | Main entry point agent |
| `legal_doc_drafter_agent.py` | 7,753 | Legal document drafting |
| `base_agent.py` | 3,351 | Base class for all agents |
| `customer_research_agent.py` | 1,948 | Customer research |
| `content_writer_agent.py` | 1,500+ | Content writing |

---

## Services (167 Files)

### Largest Services

| Service | Lines | Purpose |
|---------|-------|---------|
| `discord_bot.py` | 14,485 | Discord bot integration |
| `workflow_orchestration_agent.py` | 3,427 | Multi-agent workflows |
| `discord_notifications.py` | 2,273 | Discord notification system |
| `opportunity_pipeline_orchestrator.py` | 1,848 | Opportunity execution |
| `research_orchestrator.py` | 1,701 | Research coordination |
| `creative_orchestrator.py` | 1,654 | Creative content coordination |
| `proper_agent_executor.py` | 1,607 | Agent execution engine |
| `collective_intelligence.py` | 1,533 | Collective learning system |
| `workspace_manager.py` | 1,459 | Project workspace management |
| `litigation_brain.py` | 1,321 | Legal case analysis |
| `autonomous_action_executor.py` | 1,300 | Autonomous action execution |
| `ml_scoring_engine.py` | 1,262 | ML model scoring |
| `roi_tracker.py` | 1,176 | ROI tracking |
| `workflow_engine.py` | 1,149 | Workflow execution |
| `spider_intelligence.py` | 1,115 | Spider data processing |
| `body_coordinator.py` | 1,111 | Body systems coordination |
| `pipeline_learning.py` | 1,103 | Pipeline learning system |
| `model_registry.py` | 1,098 | ML model registry |
| `llm_provider_registry.py` | 1,061 | LLM provider management |
| `learning_pattern_engine.py` | 1,043 | Learning pattern extraction |

### Service Categories

| Category | Services | Purpose |
|----------|----------|---------|
| **Orchestration** | orchestration_engine, workflow_engine, proper_agent_executor | Multi-agent coordination |
| **Body Systems** | heart, lungs, spine, immune, digestive, muscular, brain, skin, body_coordinator | System health monitoring |
| **Intelligence** | spider_intelligence, collective_intelligence, learning_pattern_engine | Knowledge processing |
| **Integration** | discord_bot, discord_notifications, platform_integrations | External integrations |
| **ML/AI** | ml_scoring_engine, model_registry, llm_provider_registry | Machine learning |
| **Content** | creative_orchestrator, research_orchestrator, content_diversity | Content generation |
| **Finance** | roi_tracker, cost_tracker, revenue_attribution | Financial tracking |

---

## Spiders (77 Working)

### Spider Categories

| Category | Count | Examples |
|----------|-------|----------|
| **Specialized** | 114 files | News, Finance, Tech, Legal, etc. |
| **Management** | 8 files | Registry, base classes |

### By Data Source Type

| Type | Count | Method |
|------|-------|--------|
| **REST API** | 32 | Direct API calls |
| **RSS Feeds** | 30 | RSS parsing |
| **Web Scraping** | 10 | HTML parsing |
| **Playwright** | 2 | Browser automation |
| **JSON** | 3 | Static JSON endpoints |

### Spider Examples by Domain

| Domain | Spiders |
|--------|---------|
| **News/Media** | TechCrunch, TheVerge, BBC, CNN, NPR, Reuters, NewsAPI |
| **Financial** | CoinGecko, YahooFinance, Polygon, Finnhub, Kalshi, TheOdds |
| **Tech** | HackerNews, DevTo, GitHub, Ars Technica, Kickstarter |
| **Legal** | CourtListener, FindLaw, LII, Colorado Family Law, Justia |
| **Education** | Teachable, Udemy, Coursera, Kaggle |

---

## Views (164 Files)

### Largest View Files

| File | Lines | Endpoints |
|------|-------|-----------|
| `views_image.py` | 14,779 | Image generation, editing |
| `views_video.py` | 9,053 | Video generation |
| `views_agent_learning.py` | 5,516 | Agent learning APIs |
| `views_odds_sports.py` | 2,936 | Sports betting APIs |
| `views_analytics.py` | 2,703 | Analytics endpoints |
| `views_projects_api.py` | 2,567 | Project management |
| `views_spider_intelligence.py` | 2,259 | Spider data APIs |
| `views_opportunity.py` | 1,807 | Opportunity pipeline |
| `views.py` | 1,617 | Core views |
| `views_legal.py` | 1,443 | Legal document APIs |
| `views_provenance.py` | 1,381 | Content provenance |
| `views_platform_integrations.py` | 1,374 | Platform integration APIs |
| `views_content.py` | 1,337 | Content management |
| `views_preferences.py` | 1,333 | User preferences |
| `views_rag_embeddings.py` | 1,255 | RAG/embedding APIs |
| `views_orchestration.py` | 1,200+ | Orchestration APIs |

---

## URL Endpoints (1,578 Total)

### Endpoint Categories (Estimated)

| Category | Count | Prefix |
|----------|-------|--------|
| **Image/Video** | 200+ | `/api/image/`, `/api/video/` |
| **Agents** | 150+ | `/api/agents/`, `/api/agent-learning/` |
| **Analytics** | 100+ | `/api/analytics/` |
| **Orchestration** | 50+ | `/api/orchestration/` |
| **Spider/Intelligence** | 80+ | `/api/spider/`, `/api/intelligence/` |
| **Content** | 100+ | `/api/content/`, `/api/projects/` |
| **Auth/User** | 30+ | `/api/auth/`, `/api/user/` |
| **Body Systems** | 65+ | `/api/body/`, `/api/health/` |
| **Legal** | 40+ | `/api/legal/` |
| **Betting/Sports** | 60+ | `/api/betting/`, `/api/odds/` |
| **Dashboard** | 20+ | `/api/dashboard/` |
| **Learning** | 40+ | `/api/learning/` |
| **Other** | 600+ | Various |

---

## Celery Tasks (243 Total)

### Task Distribution

| File | Tasks | Purpose |
|------|-------|---------|
| `tasks.py` | 150+ | Main task definitions |
| `tasks_agents.py` | 40+ | Agent execution tasks |
| `tasks_learning.py` | 20+ | Learning system tasks |
| Other files | 30+ | Specialized tasks |

### Key Scheduled Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| `check_heart` | 30s | System health monitoring |
| `check_lungs` | 60s | Resource monitoring |
| `check_skin` | 90s | Workspace monitoring |
| `process_spider_queue` | 5m | Spider data processing |
| `cleanup_old_executions` | 1h | Database maintenance |
| `sync_agent_stats` | 15m | Agent statistics |

---

## WebSocket Consumers (52 Classes)

### Consumer Files

| File | Consumers | Purpose |
|------|-----------|---------|
| `consumers_base.py` | 21 | Base consumer classes |
| `consumers.py` | 21 | Main consumers |
| `consumers_agents.py` | 3 | Agent-specific consumers |
| `consumers_sports.py` | 1 | Sports betting updates |
| `consumers_collaboration.py` | 1 | Team collaboration |
| `consumers_consciousness.py` | 1 | AI consciousness events |
| `consumers_enhanced_ai.py` | 1 | Enhanced AI features |
| `consumers_hallucination.py` | 1 | Hallucination detection |
| `consumers_ai_training.py` | 1 | Training updates |
| `consumers_unified_v2.py` | 1 | Unified v2 consumer |

### Key WebSocket Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/ws/system-events/` | Global system events |
| `/ws/agent-activity/` | Real-time agent activity |
| `/ws/orchestration/` | Workflow execution updates |
| `/ws/betting/` | Sports betting updates |
| `/ws/chat/` | Chat/assistant communication |

---

## Management Commands (63)

### Command Categories

| Category | Commands | Examples |
|----------|----------|----------|
| **Agent Management** | 15+ | `register_agents`, `sync_agents`, `test_agent` |
| **Data Sync** | 10+ | `sync_spiders`, `sync_models`, `backfill_data` |
| **System Health** | 8+ | `health_check`, `verify_services`, `check_integrations` |
| **Content** | 8+ | `generate_content`, `fix_episode_titles`, `cleanup_content` |
| **Database** | 6+ | `migrate_data`, `cleanup_old_records`, `verify_models` |
| **Testing** | 5+ | `test_llm`, `test_spider`, `run_agent_test` |
| **Setup** | 5+ | `setup_defaults`, `create_workflows`, `initialize_system` |

---

## Discord Integration

### Discord Bot (`discord_bot.py` - 14,485 lines)

| Feature | Count |
|---------|-------|
| **Commands** | 231 |
| **Cog Categories** | 29 |
| **Event Handlers** | 15+ |

### Command Categories

| Category | Commands | Examples |
|----------|----------|----------|
| **Agent** | 30+ | `/agent run`, `/agent list`, `/agent status` |
| **Content** | 25+ | `/create image`, `/create video`, `/create blog` |
| **Research** | 20+ | `/research topic`, `/analyze trends` |
| **Betting** | 15+ | `/odds`, `/arbitrage`, `/wagers` |
| **System** | 20+ | `/health`, `/status`, `/metrics` |
| **Admin** | 15+ | `/admin`, `/config`, `/debug` |

---

## Prompt Registry

### Prompt Templates

| Category | Templates |
|----------|-----------|
| **Agent Prompts** | 72 (one per agent) |
| **System Prompts** | 15+ |
| **Tool Prompts** | 20+ |
| **Workflow Prompts** | 10+ |

---

## Learning System

### Learning Bridges (9)

| Bridge | Purpose |
|--------|---------|
| `agent_execution_bridge.py` | Track agent execution outcomes |
| `application_outcome_bridge.py` | Job application results |
| `revenue_attribution_bridge.py` | Revenue attribution |
| `advisor_feedback_bridge.py` | Advisor feedback loops |
| `collaboration_bridge.py` | Agent collaboration |
| `personalization_bridge.py` | User personalization |
| `sports_betting_bridge.py` | Betting outcome learning |
| `spider_data_bridge.py` | Spider data quality |
| `trigger_signals.py` | Situation trigger learning |

---

## Body Systems (9)

| System | Service File | Purpose |
|--------|--------------|---------|
| **HEART** | `heart.py` | Central health monitoring |
| **LUNGS** | `lungs.py` | Resource/capacity management |
| **SPINE** | `spine.py` | API routing |
| **CIRCULATORY** | `circulatory.py` | Data flow monitoring |
| **IMMUNE** | `immune.py` | Security/threat detection |
| **DIGESTIVE** | `digestive.py` | Data ingestion |
| **MUSCULAR** | `muscular.py` | Agent work execution |
| **BRAIN** | `brain.py` | Cognitive processing |
| **SKIN** | `skin_layer.py` | Workspace output monitoring |

---

## Architecture Overview

```
unified-donkey-betz/
├── core/                          # Main Django app (528k lines)
│   ├── agents/                    # 86 agent files (81k lines)
│   │   ├── base_agent.py         # Base class
│   │   ├── personal_assistant_agent.py
│   │   ├── stocks/               # 9 stock agents
│   │   ├── blockchain/           # 5 blockchain agents
│   │   ├── podcast/              # 4 podcast agents
│   │   └── ...
│   ├── services/                  # 167 service files (122k lines)
│   │   ├── discord_bot.py        # Discord integration
│   │   ├── orchestration_engine.py
│   │   ├── heart.py, lungs.py... # Body systems
│   │   └── ...
│   ├── models*.py                 # 41 model files (413 models)
│   ├── views*.py                  # 164 view files
│   ├── tasks*.py                  # Celery tasks (243)
│   ├── consumers*.py              # WebSocket consumers (52)
│   ├── urls.py                    # URL routing (1,578 endpoints)
│   ├── management/commands/       # 63 management commands
│   ├── prompts/                   # Prompt templates
│   ├── learning_bridges/          # 9 learning bridges
│   └── ...
├── ai_core/                       # Spider network (118k lines)
│   ├── spiders/
│   │   ├── specialized/          # 114 spider files
│   │   └── management/           # 8 management files
│   └── ...
├── frontend/                      # React frontend (see UI_INVENTORY.md)
├── docs/                          # Documentation
└── manage.py                      # Django management
```

---

## Database Schema

### Core Tables (301 models in `core` app)

| Category | Tables | Examples |
|----------|--------|----------|
| **Agents** | 30+ | Agent, AgentExecution, AgentMemory, AgentCapability |
| **Content** | 25+ | ContentPiece, ContentChannel, Episode, Blog |
| **Orchestration** | 10+ | CustomWorkflow, OrchestrationExecution, WorkflowStep |
| **Intelligence** | 15+ | Gate, Pilot, Opportunity, Prediction |
| **Memory** | 10+ | Memory, MemoryCluster, MemoryConnection |
| **User** | 10+ | User, UserPreference, UserProfile |
| **Learning** | 15+ | LearningPattern, KnowledgeTransfer, Feedback |
| **Body Systems** | 20+ | HeartStatus, LungsCapacity, SkinPulse |
| **Betting** | 14 | SportEvent, Wager, Arbitrage, BettingMarket |
| **Legal** | 10+ | LegalDocument, Case, LitigationItem |

---

## Additional Django Apps

Beyond the main `core` app, these Django apps provide specialized functionality:

### intelligence/ (45,935 lines, 103 files)

AI intelligence and decision-making system.

| Component | Purpose |
|-----------|---------|
| `models.py` | Gate, Pilot, Opportunity, Prediction models |
| `tasks.py` | Celery tasks for intelligence processing |
| `consumers.py` | WebSocket consumers |
| `personal_assistant_interviewer.py` | User interview system |

### content/ (21,825 lines, 71 files)

Content creation and management.

| Component | Purpose |
|-----------|---------|
| `models.py` | ContentPiece, Episode, Channel models |
| `video_provider.py` | Video generation providers |
| `processors.py` | Content processors |
| `hybrid_video_processor.py` | Hybrid video processing |

### sports/ (14,248 lines, 32 files)

Sports betting and analytics.

| Component | Purpose |
|-----------|---------|
| `models.py` | SportEvent, Wager, Market models |
| `services.py` | Betting services |
| `consumers.py` | Real-time odds consumers |
| `views.py` | Sports API views |

### persistence/ (4,519 lines, 17 files)

Data persistence and knowledge base.

| Component | Purpose |
|-----------|---------|
| `models.py` | PersistentMemory, KnowledgeBase |
| `services.py` | Persistence services |

### self_awareness/ (4,322 lines, 13 files)

System self-awareness and monitoring.

| Component | Purpose |
|-----------|---------|
| `intelligence.py` | Self-awareness intelligence |
| `embeddings.py` | Self-awareness embeddings |

### mythology/ (2,809 lines, 10 files)

Hallucination detection and testing.

| Component | Purpose |
|-----------|---------|
| `views.py` | Mythology lab views |
| `models.py` | MythologyTest, HallucinationCase |

---

## Scripts Directory (68,205 lines, 311 files)

Utility and setup scripts organized by purpose:

| Category | Files | Purpose |
|----------|-------|---------|
| `scripts/setup/` | 50+ | System setup and initialization |
| `scripts/migrations/` | 30+ | Data migration scripts |
| `scripts/testing/` | 20+ | Test utilities |
| `scripts/analysis/` | 20+ | Data analysis scripts |
| `scripts/deployment/` | 15+ | Deployment scripts |
| `scripts/utilities/` | 100+ | Various utilities |

---

## Machine Learning (ml/, 10,344 lines)

ML model definitions and training.

| Component | Purpose |
|-----------|---------|
| Model definitions | 17 ML models |
| Training scripts | Model training |
| Inference | Model inference |

---

## API Authentication

| Method | Endpoints |
|--------|-----------|
| **Session Auth** | Browser-based access |
| **Token Auth** | API access |
| **API Key** | External integrations |

---

## External Integrations

| Service | Purpose | Config |
|---------|---------|--------|
| **OpenAI** | GPT models | `OPENAI_API_KEY` |
| **Anthropic** | Claude models | `ANTHROPIC_API_KEY` |
| **ElevenLabs** | TTS | `ELEVENLABS_API_KEY` |
| **Discord** | Bot integration | `DISCORD_TOKEN` |
| **Polygon.io** | Financial data | `POLYGON_API_KEY` |
| **The Odds API** | Sports odds | `ODDS_API_KEY` |
| **Various News APIs** | Spider data | Multiple keys |

---

## Related Documentation

| Document | Description |
|----------|-------------|
| `docs/UI_INVENTORY.md` | Frontend UI inventory |
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/AGENTS.md` | Agent documentation |
| `docs/SERVICES.md` | Service documentation |
| `docs/SPIDERS.md` | Spider network docs |
| `docs/DATABASE_MODEL_REFERENCE.md` | Database reference |
| `CLAUDE.md` | Session entry point |

---

*Generated: Session 775 - January 18, 2026*
