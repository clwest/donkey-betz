<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Unified Donkey Betz - Documentation Index

**Platform:** AI Content Creation Empire
**Version:** Session 661+
**Last Updated:** January 2026
**Reality Score:** 100%

---

## Quick Start

```bash
# 1. Read current priorities
cat 00-START-NEXT-SESSION.md

# 2. Start platform
make start && make celery

# 3. Access AI Studio
open http://localhost:8000/ai-studio/
```

---

## System Statistics

| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 72 | 69 routable, 3 sub-agents (Session 663: +SystemIntelligenceAgent) |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **Services** | 93+ | Business logic layer |
| **Celery Tasks** | 127+ | Background job processing |
| **Database Models** | 324+ | 37 categories |
| **Discord Commands** | 112 | 29 Cog categories |
| **PA Tools** | 77 | Personal Assistant capabilities |
| **Advisors** | 25 | Famous figures + domain experts |
| **Sci-Fi Features** | 14 | All active |
| **Autonomous Situations** | 19 | Running continuously |

---

## Documentation Map

### Core System Documentation

| Document | Description |
|----------|-------------|
| [AGENTS.md](AGENTS.md) | All 71 agents with capabilities |
| [SPIDERS.md](SPIDERS.md) | All 77 data collection spiders |
| [SERVICES.md](SERVICES.md) | All 93+ service classes |
| [CELERY_TASKS.md](CELERY_TASKS.md) | All background tasks |
| [MODELS.md](MODELS.md) | Database models (324+) |
| [DISCORD.md](DISCORD.md) | Discord integration (112 commands) |
| [API_ENDPOINTS.md](API_ENDPOINTS.md) | Django REST endpoints (200+) |
| [VIEWS.md](VIEWS.md) | Django view files (143) |
| [MANAGEMENT_COMMANDS.md](MANAGEMENT_COMMANDS.md) | CLI management commands (43) |

### Infrastructure Documentation

| Document | Description |
|----------|-------------|
| [INFRASTRUCTURE.md](INFRASTRUCTURE.md) | Middleware, signals, decorators, routing |
| [WEBSOCKETS.md](WEBSOCKETS.md) | Real-time WebSocket consumers (20+) |
| [ASSISTANT_SYSTEM.md](ASSISTANT_SYSTEM.md) | GPT-5.1 tool interface (21 tools) |

### Feature Documentation

| Document | Description |
|----------|-------------|
| [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) | 19 autonomous intelligence situations |
| [SPECIAL_FEATURES.md](SPECIAL_FEATURES.md) | 14 sci-fi features (dreams, memory palace, etc.) |
| [DAVINCI_RESOLVE.md](../DAVINCI_RESOLVE.md) | Professional video rendering |
| [LEGAL_ASSISTANT.md](LEGAL_ASSISTANT.md) | Colorado family law system |
| [CONTENT_PIPELINE.md](CONTENT_PIPELINE.md) | $5-$50K content tiers |

### Integration & Learning

| Document | Description |
|----------|-------------|
| [SYSTEM_INTEGRATION_GUIDE.md](SYSTEM_INTEGRATION_GUIDE.md) | Complete guide to how all components work together (Session 666) |
| [LEARNING_SYSTEM.md](LEARNING_SYSTEM.md) | Agent learning hooks and collective intelligence |

### Operations

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [QUICKSTART.md](QUICKSTART.md) | Getting started guide |

---

## Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │      SUPER PLATFORM COORDINATOR     │
                    │   (Unified Intelligence Brain)      │
                    └──────────────┬──────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │   AGENTS    │       │   SPIDERS   │       │  EXTERNAL   │
    │  71 Total   │       │  77 Total   │       │    APIs     │
    │  68 Routable│       │  72 Working │       │  10+ Svcs   │
    └─────────────┘       └─────────────┘       └─────────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │       KNOWLEDGE PIPELINE            │
                    │  Spider Data → Embeddings → Agents  │
                    └──────────────┬──────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │  SCI-FI     │       │  AUTONOMOUS │       │  LEARNING   │
    │  FEATURES   │       │  SITUATIONS │       │    LOOP     │
    │  14 Active  │       │  19 Running │       │  ML Scoring │
    └─────────────┘       └─────────────┘       └─────────────┘
```

---

## Agent Categories (71 Total)

| Category | Count | Agents |
|----------|-------|--------|
| Creation | 4 | Image, Video, Audio, 3D |
| Editing | 2 | ImageEditing, VideoEditing |
| Research | 1 | ResearchAgent |
| Writing | 1 | ContentWriterAgent |
| Strategy | 4 | ContentStrategy, BrandIdentity, SEO, SocialMedia |
| Executive | 4 | CTO, COO, CreativeDirector, MeetingCoordinator |
| Analysis | 3 | TrendAnalysis, OpportunityScoring, MarketIntelligence |
| Training | 2 | CharacterTraining, TrainedCreation |
| Security | 2 | MemoryIsolation, ContentAudit |
| Business | 4 | Competitor, Customer, BrandStrategy, MarketingStrategy |
| Legal | 1 | LegalDocDrafter |
| Development | 4 | CodeGenerator, FullStackDeveloper, CodeReview, DevOps |
| Stocks | 9 | StockAuditCoordinator + 8 sub-agents |
| Blockchain | 5 | BlockchainAuditCoordinator + 4 sub-agents |
| Narrative | 4 | NarrativeDriftCoordinator + 3 sub-agents |
| Content Studio | 4 | AutonomousContentStudioCoordinator + 3 sub-agents |
| Podcast | 4 | PodcastCoordinator + 3 debate agents |
| Markets | 3 | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector |
| Orchestration | 5 | Workflow, WorkflowOrchestration, OpportunityPipeline, ContentExecutor, Campaign |
| Special | 3 | ThinkingAgent, TechnicalDocument, PersonalAssistant |
| Rendering | 1 | ResolveAgent |
| Series | 1 | AISeriesWorkflowAgent |

---

## Spider Categories (77 Total)

| Category | Count | Examples |
|----------|-------|----------|
| News/Media | 10 | TechCrunch, BBC, Reuters, NPR, NewsAPI |
| Financial | 9 | CoinGecko, Yahoo Finance, Polygon, Finnhub, Kalshi |
| Tech | 8 | HackerNews, DevTo, GitHub, Kickstarter |
| Legal | 6 | CourtListener, FindLaw, Colorado Family Law |
| Education | 5 | Teachable, Udemy, Coursera, Kaggle |
| Community | 4 | Reddit, BlueSky, Discord, HackerNoon |
| Specialty | 5 | DefenseOne, MobiHealthNews, SecurityWeek |
| Jobs/Freelance | 6 | RemoteOK, WeWorkRemotely, Adzuna |
| Creative | 4 | Behance, Unsplash, Giphy |
| Other | 20 | Weather, Science, Lifestyle, Entertainment |

---

## Key File Locations

### Core Systems
```
core/super_platform/coordinator.py    - Unified intelligence brain
core/agent_router.py                  - Deterministic agent routing
core/agents/                          - All 71 agents
core/services/                        - All 93+ services
core/tasks.py                         - Celery tasks (18,000+ lines)
core/celery.py                        - Celery Beat schedules
```

### Models
```
core/models_unified_system.py         - Main models (10,000+ lines)
core/models_legal.py                  - Legal assistant models
core/models_autonomous_*.py           - Autonomous system models
```

### Frontend
```
ai_core/templates/ai_image_studio.html - Main UI (55,000+ lines)
ai_core/templates/components/panels/   - Panel components
```

### Spiders
```
ai_core/spiders/spider_registry.py    - Central registry
ai_core/spiders/specialized/          - 77 spider implementations
```

---

## External API Integrations

| Provider | Purpose | Status |
|----------|---------|--------|
| OpenAI | GPT-5-mini, Whisper, DALL-E | Active |
| Stability AI | Image generation (13 ops) | Active |
| Runway ML | Video generation (6 ops) | Active |
| ElevenLabs | TTS, voice cloning | Active |
| Replicate | FLUX LoRA, 3D | Active |
| DaVinci Resolve | Professional rendering | Active |
| Stripe | Payments/subscriptions | Active |
| Kalshi | Prediction markets | Active |
| The Odds API | Sports betting | Active |

---

## Recent Major Sessions

| Session | Focus |
|---------|-------|
| **670** | **ML Scoring Engine Phase 2** - LightGBM + Optuna, v7.1 model (+99% R²) |
| **669** | **ML Scoring Engine Phase 1** - Fixed dead features, v5.0 model |
| **668** | **ML Assessment** - Found 47% dead features, created roadmap |
| **666** | **System Integration Guide** - Deep system review documentation |
| **663** | **SystemIntelligenceAgent** + **Agents Tab** + **Activity/Learning Tabs** (10 commits) |
| 660 | ICC Tasks & Health Dashboards |
| 659 | ICC Governance UI Audit |
| 658 | AI Decision Promoter |
| 654 | Autonomous Gate Approval Pipeline |
| 653 | 7/7 Full Composability |
| 652 | Podcast Studio + Campaign Orchestrator |
| 648 | Celery Task Scheduling (14 tasks) |

---

## Environment Variables

```bash
# Required
OPENAI_API_KEY=
STABILITY_API_KEY=
RUNWAY_API_KEY=
ELEVENLABS_API_KEY=

# Optional but Recommended
DISCORD_BOT_TOKEN=
STRIPE_SECRET_KEY=
KALSHI_API_KEY=
THE_ODDS_API_KEY=

# DaVinci Resolve
RESOLVE_NODE_URL=http://localhost:5001
RENDER_NODE_TOKEN=
```

---

## Health Check Commands

```bash
# Platform health
curl http://localhost:8000/health/ping/

# Celery status
make celery-status

# Database check
.venv/bin/python manage.py shell -c "
from core.models_unified_system import Agent
print(f'Agents: {Agent.objects.count()}')
"

# Full restart
pkill -f daphne; pkill -f celery
make start && make celery
```

---

**Always read `00-START-NEXT-SESSION.md` for current priorities!**
