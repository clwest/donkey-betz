# Session 502: UI Consolidation + Podcast Web UI

**Date:** December 19, 2025
**Duration:** Single session
**Status:** Complete

---

## Summary

This session focused on web app improvements:
1. UI audit and consolidation - identified redundancies and hidden unused tabs
2. Podcast Studio web UI - brought Discord-only feature to web
3. Unified podcast view - combined PodcastEpisode + ChannelEpisode into one tab

---

## Part 1: UI Consolidation

### Problem
- 18 tabs in the main navigation was overwhelming
- Some tabs had overlapping content (spiders in 2 places, etc.)
- Several tabs weren't being actively used

### Solution
- Created comprehensive UI audit (`docs/UI_AUDIT_SESSION_502.md`)
- Hidden 3 unused tabs using CSS `display: none`
  - Leadership (Session 100)
  - Teams (Session 227)
  - Collaborate (Session 220)

### Files Modified
- `ai_core/templates/ai_image_studio.html` - Added `style="display: none;"` to nav items

### Result
- 18 tabs → 15 visible tabs (17% reduction)
- Tabs are hidden, not deleted (can be re-enabled if needed)

---

## Part 2: Podcast Studio Web UI

### Problem
- Podcast generation was Discord-only (`/create-podcast`, `/podcast-status`, etc.)
- No way to create or manage podcasts from the web interface
- Feature parity gap between Discord and Web

### Solution
Built complete web interface for Podcast Studio.

### New Files

#### `core/views_podcast.py` (~475 lines)
Real API endpoints with unified data sources:
```python
@login_required
def podcast_list(request):      # GET /api/podcasts/list/
def podcast_create(request):    # POST /api/podcasts/create/
def podcast_status(request):    # GET /api/podcasts/<id>/status/
def podcast_script(request):    # GET /api/podcasts/<id>/script/
def podcast_delete(request):    # DELETE /api/podcasts/<id>/
def podcast_stats(request):     # GET /api/podcasts/stats/
```

#### `ai_core/templates/components/panels/podcast_studio_panel.html` (~480 lines)
Full UI panel with:
- Stats row (total, complete, in progress, words, duration, failed)
- Filter tabs (All, Complete, In Progress, Failed)
- Podcast list with status badges and labeled action buttons
- Source badges (Podcast vs Content Studio)
- Create podcast modal (topic, format, participants, audio toggle)
- View script modal with copy functionality
- Audio player for generated podcasts

### Modified Files

#### `core/urls.py`
Added 6 new API routes:
```python
path('api/podcasts/list/', podcast_list_view, name='podcast-list-real'),
path('api/podcasts/create/', podcast_create_view, name='podcast-create'),
path('api/podcasts/stats/', podcast_stats_view, name='podcast-stats'),
path('api/podcasts/<uuid:episode_id>/status/', podcast_status_view, name='podcast-status'),
path('api/podcasts/<uuid:episode_id>/script/', podcast_script_view, name='podcast-script'),
path('api/podcasts/<uuid:episode_id>/', podcast_delete_view, name='podcast-delete'),
```

#### `ai_core/templates/components/panels/autonomous_dashboard_panel.html`
Added Podcasts sub-tab to Autonomous Systems Dashboard navigation.

---

## Part 3: Unified Podcast View

### Problem
- PodcastEpisode table had 4 records (from `/create-podcast`)
- ChannelEpisode table had 8 records (from Autonomous Content Studio)
- User expected to see all content in one place

### Solution
Combined both data sources into the Podcasts tab.

### Implementation
- Query both `PodcastEpisode` and `ChannelEpisode` tables
- Add `source` field: `'podcast'` or `'studio'`
- ChannelEpisodes treated as `status='complete'`
- Source badges in UI distinguish content origin
- Support `?source=podcast` or `?source=studio` filter

### UI Enhancements
- **Source Badge**: Pink "Podcast" or Purple "Content Studio"
- **Action Buttons with Labels**: Script, Play, Open, Refresh, Delete
- **Channel name and views** for studio content
- **Platform URL link** for external content

---

## API Reference

### List Podcasts (Unified)
```
GET /api/podcasts/list/?status=complete&source=podcast&limit=20&offset=0

Response: {
  "success": true,
  "episodes": [
    {
      "id": "...",
      "source": "podcast",      // or "studio"
      "topic": "AI Discussion",
      "status": "complete",
      "format_type": "debate",
      "channel": "",            // for studio content
      "views": 0,               // for studio content
      ...
    }
  ],
  "total_count": 12,
  "status_counts": {"complete": 10, "failed": 2, ...}
}
```

### Create Podcast
```
POST /api/podcasts/create/
Body: {
  "topic": "The future of AI",
  "format_type": "debate",       // debate, panel, interview, solo
  "participant_count": 3,        // 2-5
  "generate_audio": false        // uses ElevenLabs credits
}
```

### Get Podcast Status
```
GET /api/podcasts/<uuid>/status/

Response: {
  "success": true,
  "episode": {
    "id": "...",
    "source": "podcast",
    "status": "researching",
    "has_audio": false,
    ...
  }
}
```

### View Script
```
GET /api/podcasts/<uuid>/script/

Response: {
  "success": true,
  "script": "Full podcast script text...",
  "debate": {...}
}
```

### Delete Podcast
```
DELETE /api/podcasts/<uuid>/

Response: {
  "success": true,
  "message": "Podcast deleted"
}
```

---

## Feature Parity Update

| Feature | Discord | Web |
|---------|---------|-----|
| Podcast Studio | Yes | **Now Yes!** |
| Content Studio | Yes | **Now Yes!** |
| Series Creation | Yes | No |
| ROI Dashboard | Yes | No |
| Voice Clone | Yes | No |

---

## Testing

1. Start server: `make start && make celery`
2. Navigate to: http://localhost:8000/ai-studio/
3. Go to: Autonomous Tab → Podcasts sub-tab
4. Should see 12 episodes (4 Podcast + 8 Content Studio)
5. Click "Create Podcast" to test creation
6. Use filters to view different statuses

---

## Commits

1. `f929247` - refactor(Session 502): UI consolidation - hide unused tabs
2. `9889d34` - feat(Session 502): Podcast Studio web UI
3. `417a59d` - docs(Session 502): Add handoff and update start document
4. `1f8665b` - fix(Session 502): Podcast API uses correct model fields
5. `9551fba` - feat(Session 502): Unified podcast view - PodcastEpisode + ChannelEpisode
6. `410146e` - fix(Session 502): Add text labels to podcast action buttons

---

## Data Model Notes

### PodcastEpisode (core.models)
- Created via `/create-podcast` Discord or web UI
- Fields: `topic`, `title`, `status`, `script`, `audio_file`, `generation_config`
- `generation_config` JSON stores: `format`, `participant_count`, `generate_audio`

### ChannelEpisode (core.models_autonomous_studio)
- Created via Autonomous Content Studio (`/studio-create`)
- Fields: `title`, `topic`, `description`, `channel`, `views`, `platform_url`
- No status field - all are considered "complete"

---

## Next Session Suggestions

1. **Series Creation Web UI** - Similar pattern to podcast UI
2. **ROI Dashboard Web UI** - Port Discord `/roi` command
3. **Voice Clone Web UI** - Recording + marketplace
4. **Performance Optimization** - Profile slow areas

---

## Files Summary

| File | Action | Lines |
|------|--------|-------|
| `core/views_podcast.py` | Created | ~475 |
| `podcast_studio_panel.html` | Created | ~480 |
| `core/urls.py` | Modified | +20 |
| `autonomous_dashboard_panel.html` | Modified | +15 |
| `ai_image_studio.html` | Modified | +3 (hidden tabs) |
| `docs/UI_AUDIT_SESSION_502.md` | Created | ~100 |
| **Total** | | **~1,100 lines** |
