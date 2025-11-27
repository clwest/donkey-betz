# CLAUDE - AI Session Entry Point

**Last Updated:** November 27, 2025 - Session 224
**Status:** 100% Reality Score | Django Web App
**Current Focus:** AI Content Creation (images, videos, audio, 3D)
**Built-in Styles:** 80+ professional style presets
**Spider Network:** 67 active spiders | 21 real data sources

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

## Current Focus

**DO:**
- AI content creation (images, videos, audio, 3D)
- Learning systems (agents learning from users)
- Workflow orchestration improvements
- Spider network data collection
- **Creative Intelligence Empire (6 phases)**

**DON'T:**
- Sports betting tools
- Mobile app development (archived)

---

## Creative Intelligence Empire (NEW!)

The 6-phase plan to transform spider data into revenue:

| Phase | Focus | Status |
|-------|-------|--------|
| 1. Opportunity Engine | Score data as opportunities | **DONE (Session 223)** |
| 2. Revenue Reality | Track actual money | **Core DONE (Session 224)** |
| 3. Team Power | Multi-agent collab | Planned |
| 4. Smart Distribution | Where to sell | Planned |
| 5. Learning Loop | Improve from success | Planned |
| 6. Proactive System | Alerts & suggestions | Planned |

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
| **Revenue Reality** | **Core Complete** |
| Real-Time Collaboration | Complete |
| Analytics Infrastructure | Complete |

### Spider Network - REAL DATA (Sessions 221-222)
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

### Key Files Added (Sessions 219-224)
- `ai_core/spiders/real_data_collector.py` - Real web scraping for 21 sources
- `core/views_analytics.py` - Analytics API endpoints
- `core/views_project_collaboration.py` - Real-time collaboration
- `core/models_unified_system.py` - Analytics + Opportunity + Revenue models
- `agents/opportunity_scoring_agent.py` - Opportunity scoring AI agent (Session 223)
- `core/views_opportunity.py` - Opportunity Engine + Revenue API endpoints (Sessions 223-224)

---

## Key File Locations

### Backend
- `core/views_image.py` - Image operations
- `core/views_video.py` - Video operations
- `core/views_spider_dashboard.py` - Spider network dashboard
- `core/views_opportunity.py` - Opportunity Engine + Revenue APIs
- `core/tasks.py` - Celery tasks (spider execution)
- `agents/workflow_orchestration_agent.py` - Workflow system
- `content/models.py` - Database models

### Frontend
- `ai_core/templates/ai_image_studio.html` - Main UI (~30k lines)

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
>>> from core.models_unified_system import SpiderData, Opportunity, OpportunityRevenue
>>> SpiderData.objects.count()
>>> Opportunity.objects.count()
>>> OpportunityRevenue.objects.count()
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
- **Feature Docs:** `docs/features/`
- **API Docs:** `docs/apis/`
- **Session History:** `docs/sessions/`
- **Architecture:** `docs/architecture/`

---

## Recent Sessions

- **Session 224:** Revenue Reality - 3 new models (OpportunityRevenue, OpportunityContent, OpportunityPredictionAccuracy), 5 new API endpoints, Revenue UI with stats cards and Log Revenue modal
- **Session 223:** Opportunity Engine - Phase 1 complete with scoring agent, 8 API endpoints, Opportunities tab UI
- **Session 222:** Spider Intelligence Fixes - Fixed tags parsing (char-by-char bug), deduplication, job parsing, URL routing for invitations, agent learning null checks
- **Session 221:** Analytics Infrastructure - 4 new models (CostTracking, UsageMetric, PerformanceLog, AnalyticsAlert), real data collector for 21 web sources
- **Session 220:** Real-Time Collaboration - WebSocket-based project collaboration, live cursor sync, conflict resolution
- **Session 219:** Spider-Agent Integration - Connected spiders to agents, personalization, workflow marketplace

---

## Pre-Session Checklist

- [ ] Read `00-START-NEXT-SESSION.md`
- [ ] Run `make start && make celery`
- [ ] Check: http://localhost:8000/ai-studio/

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
