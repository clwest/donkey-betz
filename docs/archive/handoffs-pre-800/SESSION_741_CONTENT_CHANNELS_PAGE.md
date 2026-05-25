# Session 741: Content Channels Page & Episode Title Fix

**Date:** January 10, 2026
**Focus:** Content Channels UI + Episode Title Generation Fix

## Summary

Created a new Content Channels page to display autonomous content created by the AutonomousContentStudioCoordinator, and fixed the bug where all episodes had identical generic titles.

## Changes Made

### 1. New Content Channels API Endpoints

**File:** `core/views_content_calendar.py`

Added 3 new endpoints:
- `GET /api/content-channels/` - List all channels with episode previews
- `GET /api/content-channels/<uuid>/` - Channel detail with all episodes and debates
- `GET /api/content-channels/episode/<uuid>/` - Full episode detail with script

### 2. Frontend Content Channels Page

**File:** `frontend/src/pages/ContentChannelsPage.tsx` (NEW - ~450 lines)

Features:
- Stats cards showing total channels, active channels, total episodes
- Expandable channel cards with metadata (platform, frequency, audience)
- Episode list with script previews
- Episode detail modal with:
  - Full script content
  - Agent debate information (TopicMiner, Contrarian, Analyst positions)
  - Performance metrics (views, engagement, retention)
- Responsive design with dark theme

### 3. Episode Title Generation Fix

**Problem:** All episodes had identical generic titles like "Daily AI News: Latest AI Developments in Artificial Intelligence, Machine Learning, AI Research, and Tech Innovation"

**Root Cause:** `AutonomousContentStudioCoordinator._trigger_content_creation()` was using the channel's `topic_domain` as the episode title instead of generating a unique title.

**Solution:**
- **File:** `core/agents/autonomous_content_studio_coordinator.py`
- Added GPT-4o-mini call after script generation to extract a unique, catchy title from the script content
- New titles are max 60 characters and capture the specific topic discussed

### 4. Management Command to Fix Existing Titles

**File:** `core/management/commands/fix_episode_titles.py` (NEW)

```bash
# Preview changes
python manage.py fix_episode_titles --dry-run

# Fix all generic titles
python manage.py fix_episode_titles

# Fix specific channel
python manage.py fix_episode_titles --channel "Daily AI News"

# Limit number of episodes
python manage.py fix_episode_titles --limit 10
```

**Results:** Fixed 18 episodes with generic titles across 3 channels.

### 5. Auth Middleware Update

**File:** `core/auth_middleware.py`

Added `/api/content-channels/` to `PUBLIC_PATHS` for React frontend access.

### 6. Frontend Integration

**Files Updated:**
- `frontend/src/lib/api.ts` - Added content channels API functions
- `frontend/src/App.tsx` - Added route for `/content-channels`
- `frontend/src/components/layout/Sidebar.tsx` - Added "Channels" navigation item

## Content Statistics

| Channel | Episodes | Platform | Frequency |
|---------|----------|----------|-----------|
| Narrative Shift Reports | 68 | Discord | As needed |
| Daily AI News | 15 | YouTube | Daily |
| AI Weekly Test | 8 | YouTube | Weekly |

**Total: 91 episodes** with full scripts (3-4k characters each)

## Sample Title Transformations

| Before (Generic) | After (Unique) |
|------------------|----------------|
| "Latest AI Developments in Artificial Intelligence..." | "AI Beyond Buzz: High-Leverage Trends Reshaping Industries" |
| "Latest AI Developments in Artificial Intelligence..." | "Unleashing Creativity: The Generative AI Revolution" |
| "Latest narrative shifts, cultural trends..." | "AI Regulation: EU Act's Ripple Effects on Culture" |

## Access Points

- **React App:** http://localhost:3000/content-channels
- **API:** http://localhost:8000/api/content-channels/

## Files Changed

```
core/views_content_calendar.py         # +250 lines (3 new endpoints)
core/urls.py                           # +3 URL patterns
core/auth_middleware.py                # +1 PUBLIC_PATH
core/agents/autonomous_content_studio_coordinator.py  # +25 lines (title generation)
core/management/commands/fix_episode_titles.py       # NEW (120 lines)
frontend/src/pages/ContentChannelsPage.tsx           # NEW (450 lines)
frontend/src/lib/api.ts                # +3 API functions
frontend/src/App.tsx                   # +2 lines (import + route)
frontend/src/components/layout/Sidebar.tsx           # +1 nav item
```

## Next Steps

- Consider adding content approval workflow
- Add ability to edit/regenerate scripts from the UI
- Connect to actual publishing (YouTube, Discord)
