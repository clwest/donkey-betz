# Unified Donkey Betz - Complete Documentation Index

**Platform:** AI Content Creation Empire
**Sessions:** 420+ development sessions
**Last Updated:** December 11, 2025 (Session 420)
**Reality Score:** 100%

---

## Quick Links

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System layers, data flow, component relationships |
| [AGENTS.md](AGENTS.md) | 27 clean agents + capabilities + routing |
| [SPIDERS.md](SPIDERS.md) | 65 spiders, 60 working, data collection + training data |
| [SCIFI_FEATURES.md](SCIFI_FEATURES.md) | 15 advanced AI features (Memory, Mood, Evolution) |
| [EXTERNAL_APIS.md](EXTERNAL_APIS.md) | Stability AI, Runway ML, ElevenLabs, OpenAI, Replicate |
| [LEGAL_ASSISTANT.md](LEGAL_ASSISTANT.md) | Colorado family law system (Sessions 403-410) |
| [KNOWLEDGE_PIPELINE.md](KNOWLEDGE_PIPELINE.md) | Spider -> Embeddings -> Agent Learning flow |
| [DAVINCI_RESOLVE.md](DAVINCI_RESOLVE.md) | $300 render node investment (UNDERUTILIZED!) |
| [UNDERUTILIZED_FEATURES.md](UNDERUTILIZED_FEATURES.md) | Features built but not fully used |

---

## System Overview

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
    │  27 Clean   │       │  65 Total   │       │    APIs     │
    │  Agents     │       │  60 Working │       │  6 Services │
    └─────────────┘       └─────────────┘       └─────────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │       KNOWLEDGE PIPELINE            │
                    │  Spider Data → Embeddings → Agents  │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │        SCI-FI FEATURES              │
                    │  Memory Palace | Mood | Evolution   │
                    │  Dreams | Conversations | Hive Mind │
                    └─────────────────────────────────────┘
```

---

## Platform Statistics

### Agents
| Category | Count | Examples |
|----------|-------|----------|
| Creation | 4 | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| Editing | 2 | ImageEditingAgent, VideoEditingAgent |
| Strategy | 4 | ContentStrategy, BrandIdentity, SEO, SocialMedia |
| Executive | 4 | CTO, COO, CreativeDirector, MeetingCoordinator |
| Research | 1 | ResearchAgent |
| Analysis | 2 | TrendAnalysis, OpportunityScoring |
| Training | 2 | CharacterTraining, TrainedCreation |
| Business | 5 | Competitor, Customer, BrandStrategy, Marketing, BusinessContent |
| Legal | 1 | LegalDocDrafter |
| Workflow | 1 | WorkflowAgent |
| Entry | 1 | PersonalAssistant |
| **Total** | **27** | Clean architecture in `core/agents/` |

### Spiders
| Category | Count | Status |
|----------|-------|--------|
| Tech News | 9 | Working |
| Financial | 8 | Working |
| Freelance/Jobs | 7 | Working |
| Creative Assets | 5 | Working |
| AI/Creative Tools | 4 | Working |
| News/Media | 4 | Working |
| Legal | 6 | Working |
| **Training Data** | **1** | **Working (14 HuggingFace datasets)** |
| Other | 21 | Mixed |
| **Total** | **65** | **60 Working** |

### External APIs
| Provider | Features | Status |
|----------|----------|--------|
| Stability AI | 13 image operations | Active |
| Runway ML | 5 video operations | Active |
| ElevenLabs | 2 audio operations | Active |
| OpenAI | GPT-5-mini + Whisper | Active |
| Replicate | FLUX LoRA training | Active |
| DaVinci Resolve | Video rendering | **UNDERUTILIZED** |

### Sci-Fi Features
| Feature | Description | Status |
|---------|-------------|--------|
| Memory Palace | Persistent agent memories | Active |
| Mood System | 10 emotional states | Active |
| Evolution System | XP & leveling | Active |
| Agent Dreams | Idle creative thoughts | Active (2,949 dreams) |
| Agent Conversations | AI-to-AI chat | Active (2,899 chats) |
| Hive Mind Mode | Collective intelligence | Active |
| Time Travel Debug | Decision replay | Active |
| + 8 more | See SCIFI_FEATURES.md | Active |

---

## Recent Major Development

### Session 420: Discord Integration + Training Data Spider
Complete Discord notification system + automated training data collection:
- **5 Discord channels** (#agent-dreams, #agent-conversations, #system-status, #agent-learning, #boardroom)
- **Training Data Spider** - Fetches from 14 HuggingFace datasets (OpenAssistant, Alpaca, SlimOrca, etc.)
- **Automated collection** - Daily at 1 AM (50 records), Weekly Sundays (200 records)
- **94% quality rate** - Topics: business, AI, creative, programming, tech
- **Agent name fix** - Conversations now show actual agent names

### Sessions 403-410: Legal Assistant
Complete Colorado family law assistant with:
- Case intake forms with party/attorney/child management
- Document upload with OCR for scanned PDFs
- Motion analysis and JDF-format rewriting
- Document threading (motion → response → reply)
- **Sent to real Colorado lawyer for review!**

### Session 400: Knowledge Pipeline
Agents now USE their accumulated knowledge:
- Spider data automatically creates knowledge entries
- Knowledge injected into agent prompts
- Semantic search for relevant context

### Session 264: Super Platform Coordinator
Unified brain that orchestrates everything:
- Query classification (question, creation, research, workflow)
- Dynamic prompt building
- Multi-source context aggregation

---

## Underutilized Investments

### DaVinci Resolve Render Node ($300+)
**Location:** `/resolve_node/`
**Status:** Built in Session 103, never integrated!

A complete FastAPI render service:
- REST API for job submission
- Auto-upload to Django backend
- Multiple render templates
- Job queue management

**Why unused:** We use ffmpeg for most video operations, which is faster for simple tasks.

**Opportunity:** Could be activated for:
- Professional color grading
- ProRes exports
- Batch rendering
- Complex timeline editing

### Discord Integration (ACTIVE!)
**Location:** `core/services/discord_notifications.py`
**Status:** ✅ **LIVE with 5 channels** (Session 419-420)

Full Discord notification system now active:
- `#agent-dreams` - Agent creative thoughts (purple embeds)
- `#agent-conversations` - HiveMind sessions (pink embeds)
- `#agent-learning` - Knowledge sharing (blue embeds)
- `#boardroom` - Strategic decisions (gold embeds)
- `#system-status` - System health (variable colors)

**Requires:** `DISCORD_BOT_TOKEN` in .env

### Boardroom Decisions
**Location:** `docs/handoffs/SESSION_322_BOARDROOM_DECISIONS_BLUEPRINT.md`
**Status:** Blueprint complete, not implemented

Would capture governance decisions from agent conversations.

---

## File Locations Quick Reference

### Core Systems
```
core/super_platform/coordinator.py    - Unified brain
core/agent_router.py                  - Deterministic routing
core/agents/base_agent.py             - Base class with learning
core/agents/personal_assistant_agent.py - Entry point
core/prompts/registry.py              - Central prompts
core/services/spider_intelligence.py  - Spider analysis
```

### Models
```
core/models_unified_system.py         - All Phase 1-6 + Sci-Fi (10,596 lines)
core/models_legal.py                  - Legal assistant
content/models.py                     - Content/media
```

### Frontend
```
ai_core/templates/ai_image_studio.html - Main UI (55,625 lines)
ai_core/templates/components/panels/   - Panel components
```

### Spiders
```
ai_core/spiders/spider_registry.py    - Central registry (64 spiders)
ai_core/spiders/specialized/          - Individual implementations
```

---

## Getting Started

### 1. Start the Platform
```bash
make start      # Django + Daphne + Redis
make celery     # Celery workers + beat
```

### 2. Access UI
```bash
open http://localhost:8000/ai-studio/
```

### 3. Verify Health
```bash
curl http://localhost:8000/health/ping/
make celery-status
```

### 4. Test Agent Routing
```python
from core.agents.personal_assistant_agent import PersonalAssistantAgent
pa = PersonalAssistantAgent()
# Check available agents
print(pa.tools[0]['function']['parameters']['properties']['agent_name']['enum'])
```

---

## Session History

Full session history is archived in `docs/archive/sessions/` (255 files).

Recent handoffs are in `docs/handoffs/` (122 files).

Key milestone sessions:
- **Session 103:** DaVinci Resolve render node
- **Session 223-236:** 6-Phase Revenue Pipeline
- **Session 243-255:** 15 Sci-Fi Features
- **Session 264:** Super Platform Coordinator
- **Session 400:** Agent Knowledge Pipeline
- **Session 403-410:** Legal Assistant

---

## Contributing

When adding new features:
1. Update relevant documentation in `/docs/`
2. Create a handoff document in `/docs/handoffs/`
3. Update `CLAUDE.md` with key changes
4. Update agent counts in this INDEX if adding agents

---

**Read `00-START-NEXT-SESSION.md` for current priorities!**
