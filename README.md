# Unified Donkey Betz Platform

**AI-Powered Intelligence, Execution, and Revenue Generation System**

**Status:** 95% Integrated | 83 Agents | 80 Spiders | 9 Body Systems | 14 Sci-Fi Features
**Session:** 786 | **Last Updated:** January 20, 2026

> **Canonical truth:** [`docs/PLATFORM_WHAT_IT_IS.md`](docs/PLATFORM_WHAT_IT_IS.md) + [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md). Runtime and inventory win over stale prose.
> **Rigby chat:** `POST /api/pa/chat/` is canonical. `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compatibility-only.

---

## Quick Start

```bash
# 1. Read current context (MANDATORY for AI sessions)
cat 00-START-NEXT-SESSION.md

# 2. Start platform
make start
make celery

# 3. Access AI Studio
open http://localhost:8000/ai-studio/
```

For detailed system context, see [CLAUDE.md](CLAUDE.md).

---

## What This Platform Is

An **AI-powered mega-platform** built over 786 collaborative sessions combining:

| System | Description |
|--------|-------------|
| **83 AI Agents** | Autonomous agents with learning hooks, workspace integration, and SKIN Layer for real file writes |
| **80 Intelligence Spiders** | Real-time data collection across news, finance, tech, legal, and more |
| **9 Body Systems** | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN |
| **14 Sci-Fi Features** | Dreams, Evolution, Memory Palace, Time Travel, Social Network, and more |
| **45 Frontend Pages** | React-based UI with real-time WebSocket updates |

Current runtime detail lives in the canonical inventory. This README is a human-facing overview, not the source of truth.

---

## System Architecture

```
                    ┌─────────────────────────────────────┐
                    │         AI STUDIO FRONTEND          │
                    │    (React + WebSocket + 45 pages)   │
                    └─────────────────┬───────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│   83 AGENTS     │        │   80 SPIDERS    │        │  9 BODY SYSTEMS │
│                 │◀──────▶│                 │◀──────▶│                 │
│ Learning Hooks  │        │ Data Collection │        │ Health Monitor  │
│ SKIN Layer      │        │ 20+ Categories  │        │ Resource Mgmt   │
│ Workspace Write │        │ Real-time Feed  │        │ System Status   │
└─────────────────┘        └─────────────────┘        └─────────────────┘
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │         COLLECTIVE INTELLIGENCE     │
                    │   Memory Palace | Learning Bridges  │
                    │   Cross-Agent Delegation | Advisors │
                    └─────────────────────────────────────┘
```

---

## Key Components

### Agent Ecosystem (83 Agents)

| Category | Count | Examples |
|----------|-------|----------|
| Creation | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| Executive | CTOAgent, COOAgent, CreativeDirectorAgent |
| Development | CodeGeneratorAgent, FullStackDeveloperAgent |
| Blockchain | SmartContractAuditorAgent, WhaleWatcherAgent |
| Stocks | StockAnalystAgent, MarketMovementMonitorAgent |
| Research | ResearchAgent |
| Strategy | ContentStrategyAgent, SEOOptimizerAgent |
| And more... | See [docs/AGENTS.md](docs/AGENTS.md) |

All agents feature:
- Learning hooks connected to collective intelligence
- SKIN Layer for real workspace file writes
- Cross-agent delegation with 3-level chain support
- Integration with 6 LLM providers (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini)

Rigby now has explicit `global` and `workspace` modes. Workspace mode activates from explicit workspace context, not guesswork. The Workspace Files tab now supports preview, edit/save, and file history on top of the workspace-scoped file APIs.

### Spider Network (80 Spiders)

| Category | Count | Examples |
|----------|-------|----------|
| News/Media | 10 | TechCrunch, BBC, Reuters, NPR |
| Financial | 9 | CoinGecko, YahooFinance, Polygon |
| Tech | 8 | HackerNews, DevTo, GitHub |
| Legal | 6 | CourtListener, FindLaw |
| And more... | 44 | See [docs/SPIDERS.md](docs/SPIDERS.md) |

### Body Systems (9 Systems)

| System | Purpose |
|--------|---------|
| HEART | Central health monitoring |
| LUNGS | Resource & capacity management |
| CIRCULATORY | Data flow monitoring |
| SPINE | Central API routing |
| IMMUNE | Security & threat detection |
| DIGESTIVE | Data ingestion & processing |
| MUSCULAR | Agent work execution |
| BRAIN | Cognitive processing (LLM calls) |
| SKIN | Workspace output monitoring |

---

## Technology Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Django 4.2+, Django Channels, Celery, PostgreSQL, Redis |
| **AI/ML** | OpenAI (GPT-5), Anthropic (Claude 4), DeepSeek V3, Gemini 2.5/3, LangChain |
| **Frontend** | React, TypeScript, Tailwind CSS, WebSocket |
| **Spiders** | BeautifulSoup4, Playwright, REST APIs, RSS |

---

## Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | **Primary context** - System stats, architecture, session history |
| [00-START-NEXT-SESSION.md](00-START-NEXT-SESSION.md) | **Current priorities** - What to work on next |
| [docs/AGENTS.md](docs/AGENTS.md) | Agent documentation (83 agents) |
| [docs/SPIDERS.md](docs/SPIDERS.md) | Spider network (80 spiders) |
| [docs/SERVICES.md](docs/SERVICES.md) | Services layer (93 services) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [docs/DATABASE_MODEL_REFERENCE.md](docs/DATABASE_MODEL_REFERENCE.md) | Database model guide |

### Documentation Indexes

| Index | Contents |
|-------|----------|
| [docs/handoffs/INDEX.md](docs/handoffs/INDEX.md) | 448 session handoffs |
| [docs/audit/README.md](docs/audit/README.md) | Current active audit workspace |
| [docs/audits/INDEX.md](docs/audits/INDEX.md) | 57 system audits |
| [docs/architecture/INDEX.md](docs/architecture/INDEX.md) | 23 architecture docs |

---

## Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python manage.py migrate

# Start services
make start      # Django + Daphne
make celery     # Celery workers + beat
```

### Key Commands

```bash
# Full restart
make restart

# Health check
curl http://localhost:8000/health/ping/

# Run all 83 agents
python manage.py shell -c "from core.models_unified_system import Agent; print(f'Agents: {Agent.objects.count()}')"
```

---

## Recent Highlights

| Session | Feature |
|---------|---------|
| 785 | Hybrid Workspace Autopilot - Event-driven autonomous operations |
| 783 | Spider News Feed - Reddit-style feed for spider data with agent annotations |
| 781 | Agent Voice Fixes - 22 role-anchored conversation styles |
| 768 | Memory Safety Classification - Prevents test content from polluting learning |
| 763 | Mission Control System - Agent outputs with executable action buttons |

---

## Project Stats

```
┌─────────────────────────────────────────────────────────────┐
│                    PLATFORM METRICS                          │
├─────────────────────────────────────────────────────────────┤
│  Sessions:         786      │  Database Models:  364+       │
│  Agents:           83       │  Celery Tasks:     139        │
│  Spiders:          80       │  Services:         114        │
│  Frontend Pages:   45       │  PA Tools:         86         │
│  Body Systems:     9        │  LLM Models:       16         │
│  Sci-Fi Features:  14       │  Advisors:         25         │
├─────────────────────────────────────────────────────────────┤
│  INTEGRATION SCORE: 95% - Production Ready                   │
└─────────────────────────────────────────────────────────────┘
```

---

## License

Proprietary - All Rights Reserved

---

**Built through 786 sessions of human-AI collaboration**
