# Session 496: AI Podcast Studio - Audio Generation

**Date:** December 19, 2025
**Focus:** Podcast audio generation using ElevenLabs TTS

---

## Summary

Completed the AI Podcast Studio by adding audio generation capabilities. The system now generates multi-speaker podcast audio from debate scripts using ElevenLabs text-to-speech.

---

## What Was Built

### 1. Podcast Audio Service

**File:** `core/services/podcast_audio_service.py` (~250 lines)

**Functions:**
| Function | Purpose |
|----------|---------|
| `parse_podcast_script()` | Parse script into speaker segments with voice IDs |
| `generate_segment_audio()` | Call ElevenLabs TTS for single segment |
| `concatenate_audio_segments()` | Combine segments with pydub (500ms pause) |
| `generate_podcast_audio()` | Main orchestrator with progress callback |
| `estimate_audio_duration()` | Estimate podcast length from script |

**Voice Mapping:**
```python
PODCAST_VOICE_IDS = {
    "HOST": "ErXwobaYiN019PkySvjV",       # Antoni - warm narrator
    "MODERATOR": "ErXwobaYiN019PkySvjV",  # Antoni (alias)
    "ADVOCATE": "21m00Tcm4TlvDq8ikWAM",   # Rachel - enthusiastic
    "SKEPTIC": "2EiwWnXFnvU5JabPnv8n",    # Clyde - authoritative
    "ANALYST": "5Q0t7uMcjvnagumLfvZi",    # Paul - calm
}
```

### 2. Celery Task Update

**File:** `core/tasks.py` (lines 16615-16661)

Updated `generate_podcast_episode` task to:
1. Generate script (existing)
2. Call `generate_podcast_audio()` when `generate_audio=True`
3. Update episode with audio URL and duration
4. Progress tracking: 70-100% for audio generation phase

### 3. Test Results

Successfully generated audio for episode "Should AI replace some human jobs":
- **28 segments** parsed from script
- **590 seconds** (~9.8 minutes) of audio
- **14MB** MP3 file
- All 4 voices (Antoni, Rachel, Clyde, Paul) working

---

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `core/services/podcast_audio_service.py` | **NEW** | ~250 |
| `core/tasks.py` | Modified | +45 |
| `docs/CAPABILITIES.md` | Updated | +50 |
| `docs/AGENTS.md` | Updated | +85 |

---

## Dependencies Added

```bash
pip install pydub
```

pydub is used for audio concatenation. ffmpeg is also required (usually pre-installed on macOS).

---

## How It Works

### Script Parsing

The parser extracts speaker segments using regex:
```
HOST: Welcome to AI Debates!
ADVOCATE: I believe AI should...
SKEPTIC: But have we considered...
```

Skipped patterns:
- `[INTRO MUSIC - 5 seconds]`
- `[SEGMENT: Opening]`
- `---` dividers

### Audio Generation Flow

```
1. Load episode script from database
2. Parse into speaker segments
3. For each segment:
   - Get voice ID from PODCAST_VOICE_IDS
   - Call ElevenLabs TTS API
   - Store audio bytes
4. Concatenate all segments with 500ms pauses
5. Save final MP3 to media/podcasts/episodes/
6. Update episode with audio_url and duration
```

### Progress Tracking

Progress is reported via callback:
- 5%: Parsing script
- 5-85%: Recording segments (distributed evenly)
- 90%: Assembling podcast
- 95%: Saving audio file
- 100%: Complete

---

## Testing

### Manual Test

```bash
.venv/bin/python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from core.services.podcast_audio_service import generate_podcast_audio

result = generate_podcast_audio('EPISODE_ID', progress_callback=lambda p, m: print(f'[{p}%] {m}'))
print(result)
"
```

### Via Discord

```
/podcast-create topic:"Should AI replace jobs?" generate_audio:true
```

---

## Audio Storage

Files are saved to:
```
media/podcasts/episodes/podcast_{episode_id}_{random}.mp3
```

URL format:
```
/media/podcasts/episodes/podcast_85ba63c5_13a34c.mp3
```

---

## Known Limitations

1. **No streaming** - Entire podcast generated before playback
2. **No music/effects** - Pure voice only (could add intro/outro music)
3. **Serial generation** - Segments generated one at a time (could parallelize)
4. **ElevenLabs rate limits** - May hit limits on large podcasts

---

## Future Enhancements

1. Add intro/outro music segments
2. Parallel audio generation for speed
3. Background music under speech
4. Different voice styles per segment (emotional variance)
5. Audio waveform visualization in UI

---

## Discord Library Integration (Added)

**Channel:** `#podcast-library` (1451601597007134821)

Completed podcasts with audio automatically post to the library:

```python
from core.services.discord_notifications import discord_notify

discord_notify.send_podcast(
    episode_id=episode_id,
    topic=topic,
    duration_seconds=590,
    audio_file_path=full_path,
    segment_count=28,
    speakers=["Antoni (Host)", "Rachel (Advocate)", "Clyde (Skeptic)", "Paul (Analyst)"],
    audio_url=audio_url  # For files >8MB
)
```

**Features:**
- Files ≤8MB: Upload directly to Discord
- Files >8MB: Post embed with download link
- Rich embed with duration, segments, voices

---

## Session 497 Recommendations

1. **Playback UI** - Add audio player to AI Studio web interface
2. **Episode download** - Download button for podcast MP3
3. **Transcript sync** - Highlight transcript as audio plays
4. **Audio compression** - Reduce file sizes to fit Discord's 8MB limit
