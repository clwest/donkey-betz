# Session 441: Discord Voice Recording for Voice Cloning

**Date:** December 13, 2025
**Status:** Complete
**Focus:** Implementing real voice recording in Discord for ElevenLabs voice cloning

---

## Summary

Implemented full Discord voice recording capability to enable users to clone their voice directly from Discord. This completes the voice cloning pipeline from Session 440.

---

## What Was Built

### 1. Voice Recorder Class (`core/services/discord_voice.py`)

New classes for voice recording:

- **`RecordingSession`** - Dataclass tracking recording state
  - user_id, guild_id, channel_id
  - audio_chunks list
  - started_at timestamp
  - output_path for saved audio

- **`VoiceRecorder`** - Main recording manager
  - `start_recording(user_id, guild_id, channel_id)`
  - `add_audio_chunk(user_id, audio_data)`
  - `stop_recording(user_id)` - Saves to WAV file
  - `get_recording_duration(user_id)` - Real-time duration
  - `cleanup_old_files()` - Garbage collection

- **`VoiceRecordingSink`** - Audio sink for discord-ext-voice-recv
  - Captures audio for a specific target user
  - Writes PCM data to the recorder

### 2. ElevenLabs Voice Cloner Class

- **`ElevenLabsVoiceCloner`** - API integration
  - `clone_voice(audio_path, name, description, ...)` - Async cloning
  - `get_voice_info(voice_id)` - Voice details
  - `delete_voice(voice_id)` - Remove voice

API endpoint: `POST https://api.elevenlabs.io/v1/voices/add`
- Multipart form upload
- Header: `xi-api-key`
- Returns: `{"voice_id": "...", "requires_verification": false}`

### 3. `/voice-clone` Discord Command (Updated)

Complete rewrite with three actions:

#### `/voice-clone start`
1. Checks user is in voice channel
2. Creates `VoiceCloneRequest` in database
3. Connects bot to voice channel with `voice_recv.VoiceRecvClient`
4. Starts listening to the specific user
5. Shows recording instructions and sample text

#### `/voice-clone stop <voice_name>`
1. Stops recording and saves to WAV file
2. Validates duration (min 30 seconds, recommends 60+)
3. Sends audio to ElevenLabs API
4. Creates `VoiceProfile` with returned voice_id
5. Cleans up temp files

#### `/voice-clone status`
1. Shows current recording duration (if active)
2. Shows clone status (pending/recording/cloning/completed/failed)
3. Shows created voice profile if completed

---

## Dependencies Added

```bash
pip install discord-ext-voice-recv
```

This required downgrading PyNaCl from 1.6.1 to 1.5.0.

---

## File Changes

| File | Changes |
|------|---------|
| `core/services/discord_voice.py` | Added RecordingSession, VoiceRecorder, VoiceRecordingSink, ElevenLabsVoiceCloner classes |
| `core/services/discord_bot.py` | Rewrote `/voice-clone` command with full implementation |

---

## Recording Flow

```
User in Voice Channel
       │
       ▼
/voice-clone start
       │
       ▼
Bot joins channel with VoiceRecvClient
       │
       ▼
VoiceRecordingSink captures user audio
       │
       ▼
Audio chunks stored in RecordingSession
       │
       ▼
/voice-clone stop my_voice
       │
       ▼
Chunks combined → WAV file
       │
       ▼
WAV sent to ElevenLabs /v1/voices/add
       │
       ▼
VoiceProfile created in DB
       │
       ▼
User can use voice in marketplace!
```

---

## Audio Format

Discord audio specs:
- Sample rate: 48kHz
- Channels: 2 (stereo)
- Bit depth: 16-bit PCM
- Bytes per second: 192,000

WAV file saved with these specs for ElevenLabs compatibility.

---

## Testing

```python
# Test imports
DJANGO_SETTINGS_MODULE=core.settings python -c "
from core.services.discord_voice import (
    VoiceRecorder, ElevenLabsVoiceCloner, VOICE_RECV_AVAILABLE
)
print('Voice Recording Available:', VOICE_RECV_AVAILABLE)  # True
"
```

---

## Error Handling

- User not in voice channel → Error message with instructions
- Recording too short (<30s) → Error, suggests retrying
- No audio captured → Error, suggests speaking while recording
- ElevenLabs API error → Error with details, recorded in VoiceCloneRequest

---

## Next Steps (Session 442+)

1. **Test with real Discord voice channel** - Validate audio capture quality
2. **Add voice sample generation** - Generate sample audio after cloning
3. **Voice publishing flow** - UI for making voices public
4. **Voice pricing settings** - Configure per-minute rates
5. **Marketplace UI panel** - Browse voices in AI Studio

---

## Sources

- [discord-ext-voice-recv](https://github.com/imayhaveborkedit/discord-ext-voice-recv) - Voice receiving extension
- [ElevenLabs Voice Clone API](https://elevenlabs.io/docs/api-reference/voices/add) - Cloning endpoint
- [ElevenLabs IVC Cookbook](https://elevenlabs.io/docs/cookbooks/voices/instant-voice-cloning) - Best practices
