# DaVinci Resolve Integration

**Investment:** $295 (DaVinci Resolve Studio license)
**Sessions Built:** 103, 478, 479
**Status:** FULLY INTEGRATED & OPERATIONAL
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Setup & Configuration](#setup--configuration)
5. [Usage](#usage)
6. [Color Grade System](#color-grade-system)
7. [Learning Loop](#learning-loop)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)
10. [Development Guide](#development-guide)

---

## Overview

The DaVinci Resolve integration provides professional-grade video rendering with automatic trend-driven color grading. The system connects spider network data (Dribbble, Behance, Pinterest trends) to color grade selection, creating a learning loop that improves over time.

### Key Features

| Feature | Description |
|---------|-------------|
| **Professional Rendering** | Broadcast-quality video exports via DaVinci Resolve Studio |
| **Automatic Color Grading** | 11 presets auto-selected based on creative trends |
| **Learning Loop** | User ratings improve future grade selection |
| **Discord Integration** | 6 slash commands for complete control |
| **Web Gallery** | View, download, and rate renders in AI Studio |
| **Celery Tasks** | Async rendering with status polling |

### Investment ROI

- **License Cost:** $295 (one-time)
- **Development:** Sessions 103, 478, 479
- **Status:** Fully operational with Discord, Web, and Agent access

---

## Architecture

```
                        ┌─────────────────────────────────────┐
                        │         USER INTERFACES              │
                        │  Discord Bot  │  AI Studio Web UI   │
                        └───────┬───────┴──────────┬──────────┘
                                │                  │
                    ┌───────────▼──────────────────▼───────────┐
                    │              DJANGO BACKEND               │
                    │           http://localhost:8000           │
                    │                                           │
                    │  ┌─────────────────────────────────────┐  │
                    │  │          ResolveAgent               │  │
                    │  │    core/agents/resolve_agent.py     │  │
                    │  │                                     │  │
                    │  │  Tools:                             │  │
                    │  │  - render_video                     │  │
                    │  │  - apply_color_grade                │  │
                    │  │  - get_render_status                │  │
                    │  │  - get_trending_grades              │  │
                    │  └──────────────┬──────────────────────┘  │
                    │                 │                         │
                    │  ┌──────────────▼──────────────────────┐  │
                    │  │       Celery Async Tasks            │  │
                    │  │  - start_resolve_render             │  │
                    │  │  - poll_resolve_job_status          │  │
                    │  │  - record_resolve_outcome           │  │
                    │  └──────────────┬──────────────────────┘  │
                    │                 │                         │
                    │  ┌──────────────▼──────────────────────┐  │
                    │  │     ResolveLearningService          │  │
                    │  │  core/services/resolve_learning.py  │  │
                    │  └─────────────────────────────────────┘  │
                    └─────────────────┬─────────────────────────┘
                                      │ HTTP (port 5001)
                    ┌─────────────────▼─────────────────────────┐
                    │            RESOLVE NODE                    │
                    │         http://localhost:5001              │
                    │                                            │
                    │  ┌──────────────┐  ┌───────────────────┐   │
                    │  │ FastAPI App  │  │  Job Queue        │   │
                    │  │  app.py      │──│  (Thread Worker)  │   │
                    │  └──────────────┘  └─────────┬─────────┘   │
                    │                              │              │
                    │  ┌───────────────────────────▼───────────┐  │
                    │  │        ResolveController              │  │
                    │  │     resolve_controller.py             │  │
                    │  └───────────────────────────┬───────────┘  │
                    └──────────────────────────────┼──────────────┘
                                                   │ Python API
                    ┌──────────────────────────────▼──────────────┐
                    │          DAVINCI RESOLVE STUDIO             │
                    │           (must be running)                 │
                    │                                             │
                    │  Python API Location:                       │
                    │  /Library/Application Support/              │
                    │  Blackmagic Design/DaVinci Resolve/         │
                    │  Developer/Scripting/Modules                │
                    └─────────────────────────────────────────────┘
```

### Two Server Architecture

The system has two separate server components:

| Server | Port | Purpose | Location |
|--------|------|---------|----------|
| **resolve_node** | 5001 | Agent-based rendering with job queue | `resolve_node/` |
| **davinci_bridge** | 9090 | Legacy bridge server (optional) | `davinci_bridge/` |

**Note:** The `resolve_node` on port 5001 is the primary server used by ResolveAgent.

---

## Components

### 1. ResolveAgent

**Location:** `core/agents/resolve_agent.py`

The main agent for professional video rendering. Follows BaseAgent pattern with TimeTravelMixin and learning hooks.

```python
from core.agents import get_resolve_agent

agent = get_resolve_agent(user)
result = agent.execute(
    task="Render video with cinematic color grading",
    context={'video_ids': ['R1'], 'template': 'default_mp4'},
    scifi_context={},
    spider_context={'creative_trends': trends}
)
```

**Tools:**
| Tool | Purpose |
|------|---------|
| `render_video` | Send videos to DaVinci Resolve for rendering |
| `apply_color_grade` | Apply color grading preset |
| `get_render_status` | Check render job status |
| `get_trending_grades` | Get grades matching current spider trends |

### 2. resolve_node Server

**Location:** `resolve_node/`

FastAPI server that manages render jobs and communicates with DaVinci Resolve.

```
resolve_node/
├── app.py                 # FastAPI server (entry point)
├── resolve_controller.py  # DaVinci Resolve API wrapper
├── job_queue.py           # Job queue with worker thread
├── color_grades.py        # 11 color grade presets
├── config.py              # Configuration settings
├── models.py              # RenderJob data model
├── utils.py               # Logging and helpers
├── results/               # Rendered output files
├── jobs/                  # Job state persistence
└── logs/                  # Server logs
```

### 3. Color Grades Registry

**Location:** `resolve_node/color_grades.py`

11 professional color grade presets with spider trend mapping.

### 4. ResolveLearningService

**Location:** `core/services/resolve_learning.py`

Learning loop service that tracks user feedback and improves grade selection.

### 5. ResolveRenderJob Model

**Location:** `core/models_unified_system.py`

Database model for tracking render jobs with learning fields.

### 6. Discord Commands (ResolveCommands Cog)

**Location:** `core/services/discord_bot.py`

6 slash commands for Discord integration.

### 7. Celery Tasks

**Location:** `core/tasks.py`

Async tasks for render job management:
- `start_resolve_render`
- `poll_resolve_job_status`
- `record_resolve_outcome`
- `cleanup_old_resolve_jobs`

---

## Setup & Configuration

### Prerequisites

1. **DaVinci Resolve Studio** ($295 license) - Free version does NOT include Python API
2. **Python 3.11+**
3. **Redis** (for Celery)
4. **PostgreSQL** (for Django)

### Environment Variables

```bash
# Required
RESOLVE_NODE_URL=http://localhost:5001
RENDER_NODE_TOKEN=your-secure-token-here

# Optional (defaults shown)
DAVINCI_BRIDGE_URL=http://localhost:9090
DAVINCI_BRIDGE_API_KEY=dev-key-change-in-production
MOCK_MODE=false
```

### Starting the Resolve Node

```bash
# 1. Navigate to resolve_node directory
cd /Users/donkeyking/development/unified-donkey-betz/resolve_node

# 2. Start DaVinci Resolve Studio (must be running!)
open -a "DaVinci Resolve"

# 3. Set environment variables
export RENDER_NODE_TOKEN="your-secure-token-here"

# 4. Start the server
python app.py

# Server starts at http://localhost:5001
```

### Mock Mode (Testing without Resolve)

```bash
MOCK_MODE=true python app.py
```

### Verify Setup

```bash
# Health check
curl http://localhost:5001/health

# Expected response:
# {"status": "healthy", "queue_size": 0, "active_jobs": 0}
```

---

## Usage

### Discord Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/videos-list` | List available videos with IDs | `/videos-list` |
| `/resolve-render` | Start professional render | `/resolve-render video_ids:R1` |
| `/color-grade` | Apply specific color grade | `/color-grade video_id:R1 grade:cyberpunk_neon` |
| `/render-status` | Check job status | `/render-status job_id:abc123` |
| `/render-download` | Download completed render | `/render-download job_id:abc123` |
| `/trending-grades` | View trend-matched grades | `/trending-grades` |

### Video ID Formats

| Format | Example | Description |
|--------|---------|-------------|
| `R1, R2, R3...` | `R1` | Rescued videos by index (easiest!) |
| `#1, #2...` | `#1` | Database videos by index |
| Full UUID | `f0eb0cfe-dd9d-4de2-8cc9-d82dc5686972` | Exact match |
| Partial UUID | `f0eb0cfe` | First 8+ characters |
| With extension | `f0eb0cfe.mp4` | Auto-stripped |

### Workflow Example (Discord)

```
1. /videos-list                           → See available videos
2. /resolve-render video_ids:R1,R2        → Start render with auto grading
3. /render-status job_id:446eb8e6         → Check progress
4. /render-download job_id:446eb8e6       → Get the video!
```

### Python API

```python
from core.agents import get_resolve_agent
from core.services.resolve_learning import get_resolve_learning_service
from core.services.spider_intelligence import SpiderIntelligenceService

# Get spider trends for auto-grading
spider_service = SpiderIntelligenceService()
trends = spider_service.get_creative_trends(hours=48)

# Initialize agent
agent = get_resolve_agent(user)

# Render with auto color grading
result = agent.execute(
    task="Render video professionally",
    context={
        'video_ids': ['R1', 'R2'],
        'template': 'default_mp4',
        'color_grade': 'auto'  # Will auto-select based on trends
    },
    scifi_context={},
    spider_context={'creative_trends': trends}
)

if result.success:
    print(f"Job started: {result.data['job_id']}")
    print(f"Color grade: {result.data['color_grade']}")

# Record feedback for learning loop
learning = get_resolve_learning_service()
learning.record_user_feedback(
    job_id=result.data['job_id'],
    rating=5,  # 1-5 stars
    was_used=True,
    revenue_generated=Decimal('50.00')
)

# Get learning insights
insights = learning.get_learning_insights()
print(f"Top rated grade: {insights['top_rated_grades'][0]['name']}")
```

### Web Gallery API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resolve-renders/` | GET | List completed renders |
| `/api/resolve-renders/<id>/download/` | GET | Download video file |
| `/api/resolve-renders/<id>/rate/` | POST | Rate render (1-5) |

---

## Color Grade System

### Available Presets (11 Total)

| Preset | Description | Best For | Auto-Selected When |
|--------|-------------|----------|-------------------|
| `cinematic_warm` | Orange/teal Hollywood look | Ads, dramatic scenes | warm, terracotta, earth-tones |
| `cinematic_cool` | Cool teal sci-fi look | Sci-fi, thrillers | cool, teal, futuristic |
| `cyberpunk_neon` | High contrast neon colors | Tech, gaming | neon, cyberpunk, vibrant |
| `vintage_film` | Nostalgic film grain | Indie, nostalgic | vintage, retro, muted |
| `nordic_cool` | Desaturated Scandinavian | Minimalist, clean | scandinavian, minimalist |
| `sunset_golden` | Golden hour warmth | Lifestyle, travel | golden hour, warm |
| `moody_dark` | Dark dramatic atmosphere | Noir, mysterious | dark, moody, mysterious |
| `natural_vibrant` | Enhanced natural colors | Nature, products | natural, vibrant (default) |
| `pastel_soft` | Soft pastel tones | Fashion, beauty | pastel, soft, feminine |
| `broadcast_standard` | Broadcast-safe colors | TV, professional | broadcast, corporate |
| `corporate_clean` | Clean professional look | Business, B2B | corporate, professional |

### Trend Matching Algorithm

```python
# Pseudo-code for trend matching
def match_grade_to_trends(spider_trends):
    # 1. Extract trending styles and colors from spider data
    trending_styles = spider_trends.get('trending_styles', [])
    trending_colors = spider_trends.get('trending_colors', [])

    # 2. Score each preset
    for preset_name, preset_config in COLOR_GRADE_PRESETS.items():
        score = 0

        # Style matches (weight: 2.0)
        for style in preset_config['spider_styles']:
            if style in trending_styles:
                score += 2.0

        # Color matches (weight: 1.5)
        for color in preset_config['spider_colors']:
            if color in trending_colors:
                score += 1.5

    # 3. Return highest scoring preset
    return best_preset or 'natural_vibrant'
```

### Using Specific Grades

```bash
# Discord
/resolve-render video_ids:R1 grade:cyberpunk_neon

# Python
result = agent.execute(
    task="Render with specific grade",
    context={'video_ids': ['R1'], 'color_grade': 'cyberpunk_neon'},
    ...
)
```

---

## Learning Loop

The learning loop improves color grade selection by tracking user feedback.

### How It Works

```
1. Render completes → record_resolve_outcome task fires
2. User rates render (1-5 stars) via Discord or Web
3. ResolveLearningService aggregates performance data
4. get_best_grade_for_trends() uses historical data + trend matching
5. Future renders benefit from learned preferences
```

### Scoring Algorithm

```python
# Final score combines historical performance + trend relevance
grade_score = (
    (avg_rating * 2) +       # User ratings
    (usage_rate * 3) +       # Was the video actually used?
    (revenue_rate * 2) +     # Did it generate revenue?
    (trend_relevance * 2)    # Match to current trends
)
```

### Recording Feedback

```python
# Python
from core.services.resolve_learning import get_resolve_learning_service

learning = get_resolve_learning_service()
learning.record_user_feedback(
    job_id='abc123',
    rating=5,
    was_used=True,
    revenue_generated=Decimal('100.00')
)
```

### Getting Insights

```python
insights = learning.get_learning_insights()

# Returns:
{
    'status': 'ready',  # or 'learning', 'insufficient_data'
    'total_jobs': 50,
    'rated_jobs': 35,
    'rating_coverage': 70.0,
    'top_rated_grades': [
        {'name': 'cinematic_warm', 'avg_rating': 4.5},
        {'name': 'cyberpunk_neon', 'avg_rating': 4.2}
    ],
    'most_used_grades': [
        {'name': 'natural_vibrant', 'usage_rate': 0.8}
    ],
    'auto_vs_manual': {
        'auto_avg_rating': 4.1,
        'manual_avg_rating': 3.8,
        'auto_better': True
    },
    'recommendation': "'cinematic_warm' is performing excellently!"
}
```

---

## API Reference

### resolve_node Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Health check (basic) |
| `/health` | GET | No | Detailed health status |
| `/render/start` | POST | Yes | Start render job |
| `/render/status/{job_id}` | GET | Yes | Get job status |
| `/render/result/{job_id}` | GET | Yes | Download result |
| `/jobs` | GET | Yes | List all jobs |

### Authentication

All authenticated endpoints require header:
```
X-Render-Token: your-token-here
```

### Start Render Request

```bash
curl -X POST http://localhost:5001/render/start \
  -H "X-Render-Token: your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "timeline_name": "My Render",
    "clip_paths": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
    "template": "default_mp4",
    "webhook_url": "http://localhost:8000/api/resolve/callback/"
  }'
```

### Response

```json
{
  "job_id": "abc123",
  "status": "queued"
}
```

### Check Status

```bash
curl -H "X-Render-Token: your-token" \
  http://localhost:5001/render/status/abc123
```

### Response

```json
{
  "job_id": "abc123",
  "status": "done",
  "progress": 100.0,
  "output_file": "/path/to/render_abc123.mov",
  "created_at": "2025-12-17T10:00:00Z",
  "completed_at": "2025-12-17T10:02:30Z"
}
```

---

## Troubleshooting

### Common Issues

#### 1. "DaVinci Resolve not available"

**Cause:** DaVinci Resolve Studio is not running.

**Solution:**
```bash
open -a "DaVinci Resolve"
# Wait for it to fully load, then restart resolve_node
```

#### 2. "Could not connect to DaVinci Resolve"

**Cause:** Python API not found or wrong Resolve version.

**Solution:**
- Ensure you have **Studio** version (free version lacks API)
- Check Python path includes Resolve modules:
  ```
  /Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules
  ```

#### 3. "Render job added but never started"

**Cause:** No render preset loaded.

**Solution:** The controller attempts to load "H.264 Master" preset automatically. If this fails:
1. Open DaVinci Resolve manually
2. Go to Deliver page
3. Ensure render presets are available

#### 4. "Timeline already exists" popup

**Cause:** Timeline name conflict.

**Solution:** This was fixed in Session 479. Timelines now use unique names: `Render_{uuid}`

#### 5. Video ID not found

**Cause:** Invalid ID format or video doesn't exist.

**Solution:** Use `/videos-list` to see available videos and their IDs.

### Health Check Commands

```bash
# Check resolve_node server
curl http://localhost:5001/health

# Check from Django
python manage.py shell -c "
from core.agents.resolve_agent import ResolveNodeClient
client = ResolveNodeClient()
print(client.health_check())
"
```

### Log Locations

| Component | Log Location |
|-----------|--------------|
| resolve_node | `resolve_node/logs/` |
| Django/Agent | Standard Django logs |
| Celery Tasks | Celery worker output |

---

## Development Guide

### Adding a New Color Grade

1. Edit `resolve_node/color_grades.py`:

```python
COLOR_GRADE_PRESETS["my_new_grade"] = {
    "description": "Description of the look",
    "use_case": "Best for X, Y, Z content",
    "spider_styles": ["style1", "style2"],  # For trend matching
    "spider_colors": ["color1", "color2"],
    "resolve_settings": {
        "ColorWheels": {
            "lift": {"red": 0.0, "green": 0.0, "blue": 0.0},
            "gamma": {"red": 0.0, "green": 0.0, "blue": 0.0},
            "gain": {"red": 0.0, "green": 0.0, "blue": 0.0},
        },
        "Contrast": 1.0,
        "Saturation": 1.0,
        "Temperature": 0,
    },
}
```

2. Test trend matching:
```python
from resolve_node.color_grades import match_grade_to_trends
result = match_grade_to_trends({'trending_styles': ['style1']})
assert result == 'my_new_grade'
```

### Adding New Render Templates

1. Edit `resolve_node/config.py` or `resolve_controller.py`
2. Add template-specific settings in `configure_render_settings()`

### Extending the Agent

Add new tools to `ResolveAgent.tools` list in `core/agents/resolve_agent.py`:

```python
{
    "type": "function",
    "function": {
        "name": "my_new_tool",
        "description": "What it does",
        "parameters": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}
```

Then implement `_my_new_tool()` method.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| `docs/handoffs/SESSION_478_DAVINCI_RESOLVE_FULL_UTILIZATION.md` | Initial integration |
| `docs/handoffs/SESSION_479_DAVINCI_RESOLVE_FULL_INTEGRATION.md` | Discord commands & fixes |
| `docs/apis/DAVINCI_RESOLVE_FFMPEG.md` | FFmpeg fallback methods |
| `resolve_node/README.md` | Server documentation |

---

## Summary

The DaVinci Resolve integration transforms a $295 software investment into a fully automated professional video rendering system with:

- **ResolveAgent** for agent-based rendering
- **11 color grade presets** with spider trend matching
- **Learning loop** that improves over time
- **Discord commands** for easy access
- **Web gallery** for viewing and rating renders
- **Async Celery tasks** for reliable job management

The system is production-ready and actively used for professional video output.
