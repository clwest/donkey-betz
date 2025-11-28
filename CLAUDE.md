# CLAUDE - AI Session Entry Point

**Last Updated:** November 28, 2025 - Session 246 (Real-Time Agent Conversations)
**Status:** 100% Reality Score | Django Web App | ALL 6 PHASES COMPLETE + Agent AI
**Current Focus:** AI Content Creation (images, videos, audio, 3D)
**Built-in Styles:** 80+ professional style presets
**Spider Network:** 67 spiders | 12 categories | 21 real data sources
**Agent Ecosystem:** 20 agents | 57 spider connections | Real-time conversations via WebSocket

---

## Quick Start (2 Minutes)

### 1. Read Current Context (MANDATORY)
```bash
cat 00-START-NEXT-SESSION.md
```

### 2. Start Platform
```bash
make start
make celery  # For spider network & background tasks
```

### 3. Access AI Studio
```bash
open http://localhost:8000/ai-studio/
```

---

## Creative Intelligence Empire - ALL 6 PHASES COMPLETE!

The 6-phase plan to transform spider data into revenue:

| Phase | Focus | Sessions | Status |
|-------|-------|----------|--------|
| 1. Opportunity Engine | Score data as opportunities | 223 | **DONE** |
| 2. Revenue Reality | Track actual money | 224-226 | **DONE** |
| 3. Team Power | Multi-agent collab | 227-228 | **DONE** |
| 4. Smart Distribution | Where to sell | 229-231 | **DONE** |
| 5. Learning Loop | Improve from success | 232-233 | **DONE** |
| 6. Proactive System | Alerts & suggestions | 234-236 | **DONE** |
| 7. Agent Learning | Autonomous knowledge sharing | 243-245 | **DONE** |
| 8. Agent Conversations | Real-time AI-to-AI chat | 244-246 | **DONE** |

---

## Current Focus

**DO:**
- AI content creation (images, videos, audio, 3D)
- Learning systems (agents learning from users)
- Workflow orchestration improvements
- Spider network data collection
- Platform polish and optimization

**DON'T:**
- Sports betting tools
- Mobile app development (archived)

---

## Platform Capabilities

| Category | Status |
|----------|--------|
| Stability AI | 13/13 features |
| Runway ML Video | 5/5 features |
| ElevenLabs Audio | 2/2 features |
| Video Editing | 14/14 features |
| 3D Generation | Complete |
| Character Training | 3/3 features |
| Workflow Orchestration | 6 workflows |
| Spider Network | 67 spiders + 21 real sources |
| **Opportunity Engine** | **Phase 1 Complete** |
| **Revenue Reality** | **Phase 2 Complete** |
| **Team Power** | **Phase 3 Complete** |
| **Smart Distribution** | **Phase 4 Complete** |
| **Learning Loop** | **Phase 5 Complete** |
| **Proactive System** | **Phase 6 Complete** |
| Real-Time Collaboration | Complete |
| Analytics Infrastructure | Complete |
| A/B Testing Framework | Complete |
| Goal Tracking | Complete |
| **Agent Learning** | **Autonomous knowledge sharing** |
| **Agent Conversations** | **Real-time WebSocket streaming** |

### Spider Network - REAL DATA
**21 Real Data Sources:**
- **Tech News:** TechCrunch, The Verge, Wired, MIT Tech Review, Axios, HackerNews API, Dev.to API
- **Jobs:** RemoteOK (JSON API), WeWorkRemotely (RSS)
- **Financial:** CoinGecko API, Yahoo Finance API
- **Creative:** Dribbble, Behance, Indiegogo, Kickstarter

**67 Registered Spiders across 17 categories:**
- Financial (8), Tech (9), Freelance (5), Creative Assets (5)
- AI/Creative Tools (4), Digital Products (5), Content Creation (3)
- Plus 28 more across News, Design, Education, Legal, etc.

### Available Workflows
- `research_and_create_logos` - Research + logos (1024x1024)
- `youtube_thumbnail_package` - Research + thumbnails (1280x720)
- `brand_identity_package` - Research + brand identity
- `product_photography_kit` - Research + product photos
- `video_thumbnail_series` - Consistent thumbnail series
- `logo_to_video` - Animate logo into video

### Agent Ecosystem (20 Real Agents)

All agents have actual Python implementations in `agents/` directory:

**Generation Agents:**
- `ImageAgent` - Unified image generation (logos, social media, illustrations)
- `VideoAgent` - Text-to-video, image-to-video, editing, color grading
- `AudioAgent` - Text-to-speech, sound effects, voiceovers
- `3DGenerationAgent` - 3D model and scene generation

**Research & Analysis:**
- `ResearchAgent` - Web search + spider intelligence
- `TrendAnalysisAgent` - Trending topics, colors, styles

**Workflow & Orchestration:**
- `WorkflowOrchestrationAgent` - Multi-step creative workflows
- `OpportunityScoringAgent` - Score spider data as opportunities

**Specialized Generation:**
- `CharacterTrainingAgent` - Train custom character styles
- `TrainedCreationAgent` - Generate with trained characters
- `CreationAgent` - General content creation
- `PromptEngineeringAgent` - Prompt optimization

**Strategy Agents (Session 241):**
- `ContentStrategyAgent` - Content recommendations from trends
- `SEOOptimizerAgent` - Hashtags, metadata, SEO optimization
- `BrandIdentityAgent` - Brand colors, styles, consistency
- `SocialMediaAgent` - Platform-specific content
- `CreativeDirectorAgent` - High-level creative direction

**Executive Agents:**
- `CTOAgent` - Technical decisions
- `COOAgent` - Operations oversight
- `MeetingCoordinatorAgent` - Team coordination

---

## Key File Locations

### Backend
- `core/views_image.py` - Image operations
- `core/views_video.py` - Video operations
- `core/views_spider_dashboard.py` - Spider network dashboard
- `core/views_opportunity.py` - Opportunity Engine + Revenue APIs
- `core/views_ab_testing.py` - A/B Testing Framework APIs (Session 235)
- `core/views_proactive.py` - Proactive System APIs (Session 234)
- `core/tasks.py` - Celery tasks (spider execution)
- `agents/workflow_orchestration_agent.py` - Workflow system
- `content/models.py` - Database models
- `core/models_unified_system.py` - All Phase 1-6 models

### Frontend
- `ai_core/templates/ai_image_studio.html` - Main UI (~45k lines)

### Configuration
- `core/assistant/tool_definitions.py` - GPT tool schemas
- `core/assistant/constants.py` - System constants
- `core/celery.py` - Celery Beat schedules

---

## Troubleshooting

### Server won't start
```bash
pkill -f daphne; pkill -f redis; pkill -f celery; rm -f .daphne.pid .celery.pid .celery-beat.pid && make start && make celery
```

### Check health
```bash
curl http://localhost:8000/health/ping/
make celery-status
```

### Database check
```bash
.venv/bin/python manage.py shell
>>> from content.models import ImageHistory
>>> ImageHistory.objects.count()
>>> from core.models_unified_system import SpiderData, Opportunity, ABTest, UserGoal
>>> SpiderData.objects.count()
>>> Opportunity.objects.count()
>>> ABTest.objects.count()
>>> UserGoal.objects.count()
```

---

## Style System (80+ Presets)

Built-in style library in `content/image_generation.py`:

**Animation Styles:**
- pixar, disney, dreamworks, south_park, simpsons, family_guy
- ghibli, anime, manga, looney_tunes, rick_and_morty, archer
- adventure_time, gravity_falls, bojack, cartoon, chibi

**Art Styles:**
- watercolor, oil_painting, pencil, charcoal, pastel
- impressionist, surreal, cubist, pop_art, art_deco

**Genre Styles:**
- cyberpunk, steampunk, fantasy, scifi, gothic, horror

**Usage:** Just say the style name - "Create a cyberpunk city" or "DreamWorks style mascot"

---

## Documentation

- **Current Priorities:** `00-START-NEXT-SESSION.md`
- **Prompting System:** `docs/architecture/PROMPTING_SYSTEM.md` (Session 238)
- **Feature Docs:** `docs/features/`
- **API Docs:** `docs/apis/`
- **Session History:** `docs/sessions/`
- **Architecture:** `docs/architecture/`

---

## Recent Sessions

- **Session 246:** Real-Time Agent Conversations - WebSocket streaming for live AI-to-AI chat, chat bubble UI, 5-min conversation schedule
- **Session 244-245:** Agent Conversations - Inter-agent communication models, GPT-4o-mini chat generation, conversation UI
- **Session 243:** Agent Learning System - Autonomous knowledge sharing, synthesized insights, learning connections
- **Session 242:** Spider-Agent Connections - Database-backed spider-agent relationships, 12 categories, 57 connections
- **Session 241:** Agent Cleanup - Audited 145 agents, deleted placeholders, created 5 new valuable agents, now 20 REAL agents
- **Session 240:** Workflow Engine v2 - User Vision SACRED philosophy, IntentParser preserves style/subject

---

## Pre-Session Checklist

- [ ] Read `00-START-NEXT-SESSION.md`
- [ ] Run `make start && make celery`
- [ ] Check: http://localhost:8000/ai-studio/

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
