---
originating_session: 926
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 926: Universal Agent Voice System

**Date:** February 4, 2026
**Status:** COMPLETE
**PR:** #TBD

## Summary

Implemented a Universal Agent Voice System that adds "Listen" buttons throughout the platform, allowing any agent-generated content to be converted to speech via ElevenLabs TTS.

## Changes Made

### Phase 1: Database & Backend Foundation

1. **Added `voice_id` field to Agent model** (`core/models_unified_system.py`)
   - CharField for storing ElevenLabs voice ID or name
   - Allows per-agent voice customization

2. **Created AudioCache model** (`core/models_audio_cache.py`)
   - Content-based deduplication using SHA256 hash of text + voice_id
   - Tracks access count, file size, estimated cost
   - Supports cache eviction policies

3. **Created migrations**
   - `0225_add_voice_id_and_audio_cache.py` - Adds voice_id to Agent
   - `0226_add_audio_cache_model.py` - Creates AudioCache table

### Phase 2: TTS Service Enhancement

4. **Enhanced ElevenLabs TTS service** (`core/services/elevenlabs_tts_service.py`)
   - Added `AGENT_VOICE_MAP` for category-to-voice mapping
   - Added `get_voice_for_agent()` - Determines voice based on agent name/category
   - Added `generate_audio_cached()` - TTS with caching support
   - Added `estimate_tts_cost()` - Cost/duration estimation for warnings

### Phase 3: API Endpoints

5. **Added new TTS endpoints** (`core/views_audio.py`)
   - `POST /api/tts/generate/` - Generate TTS with caching
   - `POST /api/tts/estimate/` - Estimate cost before generation
   - `GET /api/tts/voices/` - List available voices

6. **Updated URL routing** (`core/urls.py`)
   - Added routes for new TTS endpoints

### Phase 4: Management Command

7. **Created voice assignment command** (`core/management/commands/assign_agent_voices.py`)
   - Maps agent categories to appropriate voices
   - Supports dry-run, apply, and force modes
   - Shows voice distribution statistics

### Phase 5: Frontend Components

8. **Created ListenButton component** (`frontend/src/components/ListenButton.tsx`)
   - States: idle, loading, playing, paused, error
   - Shows cost warning modal for content > 2000 chars
   - Icon-only design with Volume2/Square toggle

9. **Created ListenAllButton component** (same file)
   - Plays all messages in sequence (podcast-style)
   - Shows progress indicator (message 3 of 12)
   - Voice switching per agent

10. **Added ttsApi to frontend** (`frontend/src/lib/api.ts`)
    - `generate()`, `estimate()`, `voices()`, `settings()`, `speak()`

### Phase 6: Frontend Integration

11. **ConversationDetailModal** (`frontend/src/components/platform/ConversationDetailModal.tsx`)
    - ListenButton on each agent message
    - ListenAllButton in conversation header

12. **DreamsPanel** (`frontend/src/components/platform/DreamsPanel.tsx`)
    - ListenButton in expanded dream content

13. **DreamDetailModal** (`frontend/src/components/platform/DreamDetailModal.tsx`)
    - ListenButton for dream content

### Phase 7: Celery Task

14. **Added cache cleanup task** (`core/tasks.py`)
    - `cleanup_audio_cache()` - Evicts old entries daily
    - Eviction policy: >30 days with <5 accesses

15. **Updated Celery Beat schedule** (`core/celery.py`)
    - `cleanup-audio-cache` scheduled for 3 AM daily

## Voice Assignment Strategy

| Voice | ID | Assigned To |
|-------|-----|-------------|
| Rachel | 21m00Tcm4TlvDq8ikWAM | Research, Analysis, Default |
| Antoni | ErXwobaYiN019PkySvjV | Financial, Advisory |
| Bella | EXAVITQu4vr4xnSDxMaL | Content, Creative |
| Daniel | onwK4e9ZLuTAKqWW03F9 | Technical, Development |
| George | JBFqnCBsd6RMkjVDRZzb | Executive (CTO, COO) |
| Charlotte | XB0fDUnXU5powFXDhCwa | Legal, Compliance |
| Emily | LcfcDJNUP1GQjkzn1xUU | Marketing, Social |
| Matilda | XrExE9yKIg1WjnnlVkGX | Health, Wellness |
| Callum | N2lVS1w4EtoT3dr4eOWO | Strategy |
| Domi | AZnzlk1XvdvUeBnXmlld | Blockchain, Crypto |
| Sam | yoZ06aMxZJJ28mfd3POQ | Sports, Analysis |
| Elli | MF3mGyEYCl7XYWbV9V6O | Support, Assistant |

## Files Changed

### New Files
- `core/models_audio_cache.py`
- `core/management/commands/assign_agent_voices.py`
- `frontend/src/components/ListenButton.tsx`
- `core/migrations/0225_add_voice_id_and_audio_cache.py`
- `core/migrations/0226_add_audio_cache_model.py`

### Modified Files
- `core/models_unified_system.py` - Added voice_id field
- `core/models/__init__.py` - Import AudioCache
- `core/services/elevenlabs_tts_service.py` - Added caching layer
- `core/views_audio.py` - New TTS endpoints
- `core/urls.py` - New routes
- `core/tasks.py` - Cache cleanup task
- `core/celery.py` - Celery beat schedule
- `frontend/src/lib/api.ts` - ttsApi
- `frontend/src/components/platform/ConversationDetailModal.tsx` - ListenButton
- `frontend/src/components/platform/DreamsPanel.tsx` - ListenButton
- `frontend/src/components/platform/DreamDetailModal.tsx` - ListenButton

## Usage

### Assign Voices to Agents
```bash
# Dry run to see assignments
python manage.py assign_agent_voices

# Apply assignments
python manage.py assign_agent_voices --apply

# Overwrite existing
python manage.py assign_agent_voices --apply --force
```

### API Examples
```bash
# Generate TTS
curl -X POST /api/tts/generate/ \
  -d '{"text": "Hello world", "agent_name": "ContentWriterAgent"}'

# Estimate cost
curl -X POST /api/tts/estimate/ \
  -d '{"text": "Long content..."}'

# List voices
curl /api/tts/voices/
```

## Future Enhancements
- Add ListenButton to more components (Deliverables, HiveMind, Reports)
- Voice preferences per user
- Bulk audio generation for podcasts
- Audio download/export feature
