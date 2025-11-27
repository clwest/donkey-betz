# CLAUDE - AI Session Entry Point

**Last Updated:** November 26, 2025 - Session 218
**Status:** 100% Reality Score | Django Web App
**Current Focus:** AI Content Creation (images, videos, audio, 3D)
**Built-in Styles:** 80+ professional style presets
**Spider Network:** 67 active spiders across 17 categories

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

**DON'T:**
- Income generation features
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
| Spider Network | 67/67 spiders active |

### Spider Network Categories (67 Spiders)
- **Financial (8):** CoinGecko, Yahoo Finance, Seeking Alpha, etc.
- **Tech (9):** HackerNews, DevTo, GitHub, ProductHunt, etc.
- **Freelance (5):** Upwork, Freelancer, Fiverr, etc.
- **Creative Assets (5):** Envato, CreativeMarket, AdobeStock, Shutterstock, Canva
- **AI/Creative Tools (4):** Midjourney, CivitAI, RunwayML, Replicate
- **Digital Products (5):** Etsy, LemonSqueezy, Sellfy, AppSumo, Gumroad
- **Content Creation (3):** ConvertKit, Notion, Figma
- **+ 28 more** across News, Design, Education, Legal, etc.

### Available Workflows
- `research_and_create_logos` - Research + logos (1024x1024)
- `youtube_thumbnail_package` - Research + thumbnails (1280x720)
- `brand_identity_package` - Research + brand identity
- `product_photography_kit` - Research + product photos
- `video_thumbnail_series` - Consistent thumbnail series
- `logo_to_video` - Animate logo into video

### Spider Network (Session 218)
- **67 active spiders** collecting real data across 17 categories
- Real APIs: HackerNews, DevTo, CoinGecko, WeWorkRemotely, Yahoo Finance
- AI Content Focus: Envato, CreativeMarket, Midjourney, CivitAI, RunwayML
- Digital Products: Etsy, Gumroad, LemonSqueezy, AppSumo
- Celery Beat: Scheduled every 30 minutes
- On-demand: Execute button in Spider Dashboard

---

## Key File Locations

### Backend
- `core/views_image.py` - Image operations
- `core/views_video.py` - Video operations
- `core/views_spider_dashboard.py` - Spider network dashboard
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
>>> from core.models_unified_system import SpiderData
>>> SpiderData.objects.count()
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

- **Session 218:** Spider Network expanded to 67 spiders with 16 new AI Content Creation spiders (Envato, Midjourney, CivitAI, etc.) + timezone fix for trends chart
- **Session 217:** Analytics Suite - Charts, Agent Training, Workflow Analytics (30 new endpoints)
- **Session 207:** Spider Network - All 46 spiders active with real data collection
- **Session 201:** Fixed style system, added 14 new animation styles (DreamWorks, South Park, etc.)

---

## Pre-Session Checklist

- [ ] Read `00-START-NEXT-SESSION.md`
- [ ] Run `make start && make celery`
- [ ] Check: http://localhost:8000/ai-studio/

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
