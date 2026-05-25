---
originating_session: 865
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 865: Podcast TTS + Voice Profile Integration + ConceptForge UI

**Date:** January 29, 2026
**Status:** COMPLETE
**Previous:** Session 864 (Content Intelligence + Run Mode Tracking)

---

## Overview

This session focused on four major areas:

1. **Spider Network Investigation** - Discovered Celery Beat had stopped 38 hours ago
2. **Celery Health Monitoring** - Added alerting when tasks stop running
3. **Podcast TTS Pipeline Reconnection** - Fixed auth bugs, connected VoiceProfileModal to real data
4. **ConceptForge UI** - Added Dossiers tab with full pipeline visualization

---

## Part 1: Spider Network Investigation

### Problem
Spider network showed data from 38 hours ago - all Celery Beat tasks had stopped.

### Root Cause
Railway deployment had become stale. Celery Beat scheduler wasn't running periodic tasks.

### Solution
Redeployed Railway services, which restarted Celery Beat and resumed all periodic tasks.

---

## Part 2: Celery Health Monitoring

Added a monitoring task that runs every 30 minutes to detect future outages.

### New Task: `monitor_celery_health`

**Location:** `core/tasks.py`

```python
@shared_task(name='core.tasks.monitor_celery_health')
def monitor_celery_health():
    """
    Session 865: Monitor Celery health and send Discord alerts.
    Runs every 30 minutes via Celery Beat.

    Checks:
    1. Spider data freshness (alert if no data in 6 hours)
    2. Periodic task staleness (alert if exercise_agents hasn't run in 6 hours)
    3. Stuck workspace operations (alert if > 10 stuck for > 2 hours)
    """
```

### Alerts Sent To
Discord #system-status channel via existing `send_discord_notification` helper.

### Celery Beat Schedule

**Location:** `core/settings.py`

```python
'monitor-celery-health': {
    'task': 'core.tasks.monitor_celery_health',
    'schedule': 1800.0,  # Every 30 minutes
},
```

### Files Modified
| File | Changes |
|------|---------|
| `core/tasks.py` | Added `monitor_celery_health` task |
| `core/settings.py` | Added to CELERY_BEAT_SCHEDULE |

---

## Part 3: Podcast TTS Pipeline

### Problem 1: Scripts Not Displaying

**Symptom:** Users could see 191 podcast episodes but couldn't read scripts in the UI.

**Root Cause:** `EpisodeDetailModal` used raw `fetch()` without authentication token.

**Fix:** Changed to `podcastApi.script(episode.id)` which includes auth via axios interceptor.

**Location:** `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2244-2251`

```typescript
// BEFORE (broken):
const response = await fetch(`/api/podcasts/${episode.id}/script/`)

// AFTER (fixed):
const response = await podcastApi.script(episode.id)
```

### Problem 2: Generate Audio Button Missing

**Symptom:** No way to trigger TTS audio generation from the UI.

**Fix:** Added "Generate Audio" button with loading/error states in `EpisodeDetailModal`.

**Location:** `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2376-2400`

### Problem 3: VoiceProfileModal Was a Stub

**Symptom:** Modal showed only "Default Voice" text, no real voice data.

**Fix:** Complete rewrite to connect to voice marketplace API.

**Location:** `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2530-2720`

---

## Voice Profile Integration (End-to-End)

### Data Flow

```
User → VoiceProfileModal → localStorage → handleGenerateAudio →
API (voice_profile_id) → Backend (VoiceProfile lookup) →
podcast_audio_service (custom_voice_id) → ElevenLabs TTS
```

### Frontend Changes

#### 1. VoiceProfileModal Rewrite

Now fetches real voice profiles:

```typescript
const { data: voicesData } = useQuery({
  queryKey: ['my-voices'],
  queryFn: async () => {
    const response = await voiceMarketplaceApi.myVoices()
    return response.data
  },
})
```

Shows:
- Default ElevenLabs voices (Antoni, Rachel, Clyde, Paul) for multi-voice podcast format
- User's custom cloned voices from VoiceProfile model

Selection stored in localStorage:
```typescript
localStorage.setItem('podcast_voice_profile_id', voiceId)
```

#### 2. API Method Updated

**Location:** `frontend/src/lib/api.ts:1006-1008`

```typescript
// Session 865: Generate TTS audio for an existing episode
// Accepts optional voiceProfileId to use a custom voice
generateAudio: (episodeId: string, voiceProfileId?: string) =>
  api.post(`/podcasts/${episodeId}/generate-audio/`,
    voiceProfileId ? { voice_profile_id: voiceProfileId } : {}),
```

#### 3. handleGenerateAudio Updated

**Location:** `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2253-2277`

```typescript
const handleGenerateAudio = async () => {
  // Get selected voice profile from localStorage
  const voiceProfileId = localStorage.getItem('podcast_voice_profile_id')
  // Pass voice profile to API (null/undefined uses default voices)
  const response = await podcastApi.generateAudio(episode.id, voiceProfileId || undefined)
  // ...
}
```

### Backend Changes

#### 1. New Endpoint: `podcast_generate_audio`

**Location:** `core/views_podcast.py:435-580`

```python
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def podcast_generate_audio(request, episode_id):
    """
    POST /api/podcasts/<episode_id>/generate-audio/

    Body (optional):
        - voice_profile_id: UUID of a VoiceProfile to use for all speakers
    """
    # Parse voice_profile_id from request body
    data = json.loads(request.body) if request.body else {}
    voice_profile_id = data.get('voice_profile_id')

    # Look up VoiceProfile to get ElevenLabs voice ID
    if voice_profile_id:
        voice_profile = VoiceProfile.objects.get(id=voice_profile_id)
        custom_voice_id = voice_profile.elevenlabs_voice_id
```

#### 2. URL Route Added

**Location:** `core/urls.py`

```python
path('api/podcasts/<uuid:episode_id>/generate-audio/',
     podcast_generate_audio_view, name='podcast-generate-audio'),
```

#### 3. Audio Service Updated

**Location:** `core/services/podcast_audio_service.py:219-240`

```python
def generate_podcast_audio(
    episode_id: str,
    progress_callback: Optional[callable] = None,
    custom_voice_id: Optional[str] = None,  # Session 865: New parameter
) -> Dict[str, Any]:
    # ...
    # Session 865: Use custom voice if provided, otherwise use segment's assigned voice
    voice_id_to_use = custom_voice_id if custom_voice_id else segment['voice_id']
```

---

## Default ElevenLabs Voices

The podcast system uses these default voices for the multi-speaker debate format:

| Role | Voice Name | ElevenLabs ID |
|------|------------|---------------|
| HOST | Antoni | ErXwobaYiN019PkySvjV |
| ADVOCATE | Rachel | 21m00Tcm4TlvDq8ikWAM |
| SKEPTIC | Clyde | 2EiwWnXFnvU5JabPnv8n |
| ANALYST | Paul | 5Q0t7uMcjvnagumLfvZi |

When a custom voice is selected, ALL speakers use that single voice (useful for single-narrator podcasts).

---

## Part 4: ConceptForge Dossier Pipeline UI

Added a complete UI for viewing and managing ConceptForge pipeline runs.

### Backend API (`core/views_conceptforge.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/conceptforge/runs/` | GET | List runs with filtering (status, domain, pagination) |
| `/api/conceptforge/runs/<id>/` | GET | Get run details with all stages and artifacts |
| `/api/conceptforge/runs/<id>/stages/<name>/` | GET | Get full content for a specific stage |
| `/api/conceptforge/runs/<id>/retry/` | POST | Retry a failed run |
| `/api/conceptforge/stats/` | GET | Pipeline statistics (total, success rate, by domain) |
| `/api/conceptforge/labs/` | GET | Available domain labs configuration |

### Frontend (`ConceptForgeTab.tsx`)

**Features:**
- Stats panel showing total runs, success rate, 7-day activity, in-progress count
- Run list with status badges and 6-stage progress indicators
- Filtering by status (completed, running, pending, failed)
- Detail view with stage tabs (Research, Debate, Feasibility, Risk, Market, Synthesis)
- Stage output viewer showing agent/advisor metadata
- Artifacts list with primary dossier indicator

**Stage Configuration:**
| Stage | Icon | Color |
|-------|------|-------|
| Research | FlaskConical | blue |
| Debate | Users | purple |
| Feasibility | Brain | cyan |
| Risk | Scale | orange |
| Market | TrendingUp | green |
| Synthesis | Lightbulb | yellow |

### Workspace Integration

- Added `conceptforge` to WorkspaceTab type
- Added "Dossiers" tab to workspace navigation with FlaskConical icon
- Renders ConceptForgeTab when tab is active

---

## Files Created/Modified

### Created
| File | Purpose |
|------|---------|
| `docs/handoffs/SESSION_865_PODCAST_TTS_VOICE_PROFILES.md` | This handoff document |
| `core/views_conceptforge.py` | ConceptForge API endpoints |
| `frontend/src/pages/workspace/tabs/ConceptForgeTab.tsx` | Dossier pipeline UI |

### Modified
| File | Changes |
|------|---------|
| `core/tasks.py` | Added `monitor_celery_health` task |
| `core/settings.py` | Added monitoring task to Celery Beat schedule |
| `core/views_podcast.py` | Added `podcast_generate_audio` endpoint with voice profile lookup |
| `core/urls.py` | Added URL routes for generate-audio and ConceptForge API |
| `core/services/podcast_audio_service.py` | Added `custom_voice_id` parameter |
| `frontend/src/lib/api.ts` | Updated `generateAudio` to accept voiceProfileId |
| `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx` | Fixed script auth, added Generate Audio button, rewrote VoiceProfileModal |
| `frontend/src/pages/workspace/tabs/index.ts` | Export ConceptForgeTab |
| `frontend/src/pages/WorkspacePageNew.tsx` | Added Dossiers tab to navigation |
| `frontend/src/pages/workspace/types.ts` | Added conceptforge to WorkspaceTab type |

---

## Testing

### Test Script Display
1. Go to AI Podcast Studio in Content Studio tab
2. Click on any episode
3. Verify script content displays (was previously empty/error)

### Test Voice Profile Modal
1. Click "Voice Profiles" button
2. Verify default voices display (Antoni, Rachel, Clyde, Paul)
3. Verify custom voices load (if any exist in VoiceProfile model)
4. Select a voice, close modal
5. Check localStorage: `localStorage.getItem('podcast_voice_profile_id')`

### Test Audio Generation
1. Select an episode with a script
2. Click "Generate Audio"
3. Verify loading state appears
4. Verify success/error message displays
5. If using custom voice, verify it's used in generated audio

### Test Celery Health Monitoring
```bash
# Force run the monitoring task
railway run python -c "
from core.tasks import monitor_celery_health
result = monitor_celery_health()
print(result)
"
```

---

## System Stats After Session 865

| Component | Count | Change |
|-----------|-------|--------|
| **Agents** | 75 | No change |
| **Celery Tasks** | 241 | +1 (monitor_celery_health) |
| **API Endpoints** | +8 | podcast_generate_audio + 7 ConceptForge endpoints |
| **Workspace Tabs** | 12 | +1 (Dossiers) |

---

## Next Steps

### P1: Test TTS End-to-End
- Create a test podcast episode
- Select a custom voice
- Generate audio
- Verify voice is correct

### P2: Test ConceptForge UI
- Navigate to Dossiers tab
- Verify stats load correctly
- Click on a run to see stage details
- Test filtering by status

### P3: Voice Recording UI
- Add recording interface for voice cloning
- Connect to ElevenLabs voice cloning API
- Save cloned voice to VoiceProfile model

### P4: Audio Player Enhancement
- Add waveform visualization
- Add playback controls (speed, skip)
- Add download button

---

## Related Documentation

- `core/services/podcast_audio_service.py` - Full audio generation pipeline
- `core/models_voice_marketplace.py` - VoiceProfile model
- `core/views_voice_marketplace.py` - Voice marketplace API
- `core/views_conceptforge.py` - ConceptForge API endpoints
- `core/models_conceptforge.py` - ConceptForge data models
