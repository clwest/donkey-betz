<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.

# Unified AI Platform - Complete System Overview

**Last Updated:** January 28, 2026 (Session 858) — narrative preserved; counts may drift
**Status:** Production-Ready | 100% Reality Score
**Focus:** Autonomous Intelligence, Content Creation, Revenue Generation, **User Personalization**

---

## Executive Summary

This is a comprehensive AI platform that goes **far beyond content creation**. While content generation (images, videos, audio, 3D) was the starting point, the platform has evolved into a sophisticated **Autonomous Intelligence System** with:

- **74 Specialized Agents** across 19 categories - **ALL with user context injection (Session 858 snapshot; canonical AGENT_MAP = 83 — see PLATFORM_INVENTORY)**
- **77 Production Spiders** collecting real-time data from 31+ sources (Session 858 snapshot; canonical = 80 across 41 categories — see PLATFORM_INVENTORY)
- **19 Autonomous Situations** with event-driven triggers
- **14 Active Sci-Fi Features** (emotional AI, agent evolution, memory systems)
- **Complete RAG Pipeline** with semantic search and anti-hallucination
- **124 Backend Services** powering 500+ API endpoints
- **ML Scoring Engine** with XGBoost + SHAP explainability
- **User Context Injection** - Personalized responses based on user profile, skills, goals, and preferences (Session 858)

---

## Platform Architecture at a Glance

```
                          ┌─────────────────────────────────────┐
                          │     USER INTERFACE LAYER            │
                          │  (Discord Bot, Web UI, APIs)        │
                          └──────────────┬──────────────────────┘
                                         │
                          ┌──────────────▼──────────────────────┐
                          │   SUPER PLATFORM COORDINATOR        │
                          │  (Unified Brain - Session 264)      │
                          │  - Query Classification             │
                          │  - Context Aggregation              │
                          │  - Dynamic Routing                  │
                          └──────────────┬──────────────────────┘
                                         │
         ┌───────────────┬───────────────┼───────────────┬───────────────┐
         │               │               │               │               │
         ▼               ▼               ▼               ▼               ▼
┌────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   57 AGENTS    │ │  67 SPIDERS  │ │ 19 AUTONOMOUS│ │   RAG +      │ │  10 SCI-FI   │
│   (Creation,   │ │  (Real-time  │ │  SITUATIONS  │ │  LEARNING    │ │  FEATURES    │
│   Research,    │ │   data from  │ │  (Event-     │ │  MYTHOLOGY   │ │  (Mood,      │
│   Legal, etc.) │ │   31 sources)│ │   driven)    │ │  (Anti-      │ │  Evolution,  │
│                │ │              │ │              │ │  hallucinate)│ │  Memory)     │
└────────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         │               │               │               │               │
         └───────────────┴───────────────┼───────────────┴───────────────┘
                                         │
                          ┌──────────────▼──────────────────────┐
                          │      PERSISTENT DATA LAYER          │
                          │  PostgreSQL + Redis + Embeddings    │
                          └─────────────────────────────────────┘
```

---

## Core System Components

### 1. Agent Ecosystem (57 Agents)

The platform operates through **57 specialized agents** organized into 19 categories:

| Category | Agent Count | Key Agents |
|----------|-------------|------------|
| Creation | 4 | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| Editing | 2 | ImageEditingAgent, VideoEditingAgent |
| Research | 1 | ResearchAgent |
| Strategy | 4 | ContentStrategyAgent, SEOOptimizerAgent, etc. |
| Executive | 4 | CTOAgent, COOAgent, CreativeDirectorAgent |
| Business Research | 5 | CompetitorAnalysisAgent, CustomerResearchAgent |
| Development | 4 | CodeGeneratorAgent, FullStackDeveloperAgent |
| Blockchain Audit | 5 | SmartContractAuditorAgent, WhaleWatcherAgent |
| Stock Analysis | 9 | StockAnalystAgent, BullCaseAgent, BearCaseAgent |
| Content Studio | 4 | TopicMinerAgent, ContrarianAgent (debate system) |
| Narrative | 4 | NarrativeHistorianAgent, TrendBreakDetectorAgent |
| Legal | 1 | LegalDocDrafterAgent (Colorado family law) |
| Rendering | 1 | ResolveAgent (DaVinci Resolve integration) |
| Other | 13+ | Orchestration, training, security agents |

**See:** [AGENTS.md](AGENTS.md) for complete documentation.

---

### 2. Spider Network (67 Spiders)

The platform maintains **67 production spiders** collecting real-time data from **31+ public sources**:

| Category | Spider Count | Key Sources |
|----------|--------------|-------------|
| News & Media | 11 | TechCrunch, Wired, The Verge, MIT Tech Review |
| Tech & Development | 8 | HackerNews, GitHub, Dev.to, HuggingFace |
| Financial | 5 | CoinGecko, Yahoo Finance, Etherscan |
| Community | 5 | Reddit (20+ subreddits), BlueSky |
| Legal | 4 | CourtListener, SCOTUSBlog, Colorado Courts |
| Jobs | 2 | RemoteOK, Adzuna (global aggregator) |
| Design | 3 | Behance, Unsplash, Awwwards |
| Science | 5 | ScienceDaily, Nature, arXiv |

**Data Pipeline:**
```
Spider Collection → SpiderData Model → Embedding Generation → Semantic Search → Agent Consumption
```

**See:** [SPIDERS.md](SPIDERS.md) for complete spider documentation.

---

### 3. Autonomous Systems (19 Situations)

The platform runs **19 autonomous situations** with **35 pre-configured triggers**:

| Domain | Situations | Key Features |
|--------|------------|--------------|
| Content & Creative | 3 | Content Studio, Narrative Drift, Viral Predictor |
| Income & Opportunities | 3 | Job Matching, Freelance Scout, Side Hustle |
| Financial Intelligence | 5 | Market Desk, SEC Filing, Crypto Sentiment |
| Research & Learning | 3 | Tech Stack Tracker, AI Model Monitor, Skill Gap |
| Legal | 2 | Case Law Monitor, Regulatory Change |
| Stock Market | 1 | Real-Time Alerts |

**The 5 Autonomous Properties:**
1. **Persistent Context** - Database-backed state
2. **Incoming Signals** - Spider data feeding decisions
3. **Internal Disagreement** - Multi-agent debates
4. **Outputs with Consequences** - Performance tracking
5. **Self-Renewal** - Auto-scheduling for next cycle

**See:** [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) for complete documentation.

---

### 4. Intelligence Systems

#### RAG (Retrieval-Augmented Generation)
- **Semantic Search:** OpenAI `text-embedding-3-small` for vector search
- **Unified Intelligence:** Combines SpiderData + BusinessResearchResult
- **Knowledge Attribution:** Tracks which sources informed each response

#### Learning System
- **Collective Intelligence:** Agents learn from each other's successes
- **Knowledge Transfer:** Teacher-student relationships with success tracking
- **Implicit Learning:** User preferences inferred from behavior

#### Mythology (Anti-Hallucination)
- **Validation Patterns:** 5 categories of unrealistic claims detected
- **Auto-Correction:** Exaggerated claims automatically softened
- **Legal Integration:** Extra validation for legal documents

**See:** [INTELLIGENCE_SYSTEMS.md](INTELLIGENCE_SYSTEMS.md) for complete documentation.

---

### 5. Sci-Fi Features (10 Active)

These unique features transform agents from task executors into evolving entities:

| Feature | Session | Description |
|---------|---------|-------------|
| **Mood System** | 253 | Emotional states affect output style |
| **Evolution** | 254 | XP, levels, progression (10 levels) |
| **Memory Palace** | 251-252 | Semantic memory with connections |
| **Personality** | 256 | MBTI-inspired profiles (16 types) |
| **Relationships** | 253 | Dynamic alliances and rivalries |
| **Hive Mind** | 248-250 | Multi-agent collaboration (4-8 agents) |
| **Time Travel** | 255 | Decision replay for debugging |
| **Dreams** | 247, 366 | Idle creative ideation with scoring |
| **Knowledge Transfer** | 243-245 | Agent-to-agent learning |
| **Learning System** | 243-245 | Success/failure tracking |

**See:** [SCIFI_FEATURES.md](SCIFI_FEATURES.md) for complete documentation.

---

### 6. Backend Services (57 Services)

The platform includes **57 backend services** powering all functionality:

| Category | Services | Key Examples |
|----------|----------|--------------|
| Intelligence | 8 | SpiderIntelligence, UnifiedSearch, Collective |
| Agent Services | 6 | Collaboration, Learning, Training |
| ML & Scoring | 5 | MLScoringEngine (XGBoost + SHAP) |
| Learning | 4 | PipelineLearning, ROITracker, ResolveLearning |
| Content | 6 | ContentPipeline, CreativeOrchestrator, StyleLibrary |
| Workflow | 3 | WorkflowBuilder, WorkflowAnalytics |
| Data & Memory | 3 | MemoryEmbedding, MemoryClustering |
| Analytics | 2 | AnalyticsService, EventBus |
| Integration | 4 | Stripe, Discord, ElevenLabs |

**API Endpoints:** 500+ REST endpoints + 17 WebSocket consumers

---

## Key Differentiators

### What Makes This Platform Unique

1. **Emotional AI (Mood System)** - No other platform gives agents emotional states that affect output
2. **Agent Progression (Evolution)** - Agents gain XP and level up, becoming more capable
3. **Semantic Memory with Connections** - Memories link to related concepts, not just text search
4. **Multi-Agent Debates** - Agents disagree and debate before making decisions
5. **Autonomous Situations** - 19 self-running intelligence cycles
6. **Decision Replay (Time Travel)** - Debug by replaying agent decisions step-by-step
7. **Creative Dreaming** - Agents generate ideas during idle time
8. **Anti-Hallucination (Mythology)** - Automatic detection and correction of unrealistic claims
9. **ML Explainability** - SHAP values explain why opportunities are scored the way they are
10. **Unified Intelligence** - Spider data, research, and memory all combined in one search

---

## Technology Stack

### Backend
- **Framework:** Django 5.1 + Django REST Framework
- **Database:** PostgreSQL with pgvector for embeddings
- **Cache:** Redis for caching and Celery broker
- **Task Queue:** Celery + Celery Beat (44 scheduled tasks)
- **WebSocket:** Django Channels + Daphne ASGI

### AI/ML
- **LLM:** GPT-5-mini (reasoning model)
- **Embeddings:** OpenAI text-embedding-3-small
- **ML Scoring:** XGBoost + SHAP
- **Voice:** ElevenLabs (TTS + Voice Cloning)
- **Image:** Stability AI (SDXL, Ultra, Core)
- **Video:** Runway ML (Gen-4 Aleph)
- **Rendering:** DaVinci Resolve (color grading)

### External Integrations
- **Discord:** Full bot with 40+ commands
- **Stripe:** Subscriptions + Voice Marketplace payments
- **31+ Data Sources:** RSS, REST APIs, Playwright scraping

---

## Quick Reference

### Starting the Platform
```bash
make start       # Start Daphne web server
make celery      # Start Celery worker + beat
make discord-bot # Start Discord bot (separate terminal)
```

### Key Documentation
- [AGENTS.md](AGENTS.md) - 57 agents documentation
- [SPIDERS.md](SPIDERS.md) - 67 spiders documentation
- [INTELLIGENCE_SYSTEMS.md](INTELLIGENCE_SYSTEMS.md) - RAG, Learning, Mythology
- [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) - 19 situations
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - 10 active features
- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture

### Key Files
- `core/super_platform/coordinator.py` - Unified brain
- `core/agents/base_agent.py` - Agent base class
- `ai_core/spiders/spider_registry.py` - 67 spiders
- `core/models_unified_system.py` - All database models
- `core/tasks.py` - Celery tasks
- `core/celery.py` - 44 scheduled tasks

---

## System Statistics

| Component | Count |
|-----------|-------|
| Agents | 57 |
| Spiders | 67 |
| Data Sources | 31+ |
| Autonomous Situations | 19 |
| Event Triggers | 35 |
| Sci-Fi Features | 15 (10 active) |
| Backend Services | 57 |
| REST Endpoints | 500+ |
| WebSocket Consumers | 17 |
| Celery Tasks | 44 |
| Discord Commands | 40+ |
| Style Presets | 80+ |

---

**This platform represents the frontier of agentic AI systems - not just content creation, but a complete autonomous intelligence ecosystem.**
