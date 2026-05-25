# Session 442: Voice Cloning Pipeline + Voice-Ask - COMPLETE

**Date:** December 14, 2025
**Status:** Voice Cloning WORKING | `/voice-ask` WORKING | DonkeyKing's Voice Created

---

## Major Accomplishments

### 1. `/voice-ask` Command - Ask Agents, Hear Responses in YOUR Voice!

New Discord command that combines agent intelligence with voice cloning:

```
/voice-ask question:"What's trending in AI?" agent:Research voice:DonkeyKing
```

**Features:**
- Routes questions to any agent (Research, CTO, Image, etc.)
- GPT converts raw data to natural conversational speech (no URLs read aloud!)
- ElevenLabs TTS generates audio using your cloned voice
- Returns audio file + text preview

**Technical Implementation:**
- Added `make_speakable()` function that uses GPT-4o-mini to summarize agent output
- 15-second rate limit to prevent API abuse
- Falls back to "Rachel" voice if no cloned voice available

### 2. Voice Cloning Pipeline - FULLY WORKING

Successfully cloned "DonkeyKing's Voice" through Discord:

```
User in Voice Channel → /voice-clone start → Bot Records Audio
    → /voice-clone stop DonkeyKing's Voice → ffmpeg compression
    → ElevenLabs IVC API → VoiceProfile saved → Shows in /voice-market my-voices
```

### 2. Critical Fixes Applied

| Issue | Root Cause | Fix |
|-------|------------|-----|
| VoiceClient has no `.listen()` | Regular VoiceClient can't receive audio | Force disconnect & reconnect with `VoiceRecvClient` |
| Audio file too large (>10MB) | Raw WAV is huge | Added ffmpeg compression (WAV → MP3) |
| ElevenLabs 401 errors | Free tier, wrong API key | User upgraded to Creator tier ($22/mo) |
| `voices_write` permission | API key missing write scope | User updated API key permissions |
| Async ORM errors | Django ORM in async context | Wrapped all ORM calls with `sync_to_async` |
| Duplicate bot processes | Old bot not killed | Use `pkill -f "run_discord_bot"` before restart |

### 3. Disk Cleanup - 18GB Recovered

Cleaned cache directories to free space:
- `~/.cache/huggingface/` - Model cache
- `~/.cache/pip/` - Pip cache
- `~/Library/Caches/pip/` - macOS pip cache
- Various temp files

**Before:** 2.9GB free → **After:** 21GB free

---

## Files Modified

### `core/services/discord_voice.py`

1. **Enhanced Logging** - Packet counting in VoiceRecordingSink
2. **ffmpeg Compression** - Auto-compress WAV > 8MB to MP3:
```python
if file_size > 8 * 1024 * 1024:
    subprocess.run([
        'ffmpeg', '-y', '-i', audio_file_path,
        '-ac', '1', '-ar', '22050', '-b:a', '128k',
        mp3_path
    ])
```

### `core/services/discord_bot.py`

1. **VoiceRecvClient Fix** - Force clean reconnect:
```python
# ALWAYS disconnect first for clean VoiceRecvClient connection
if voice_client:
    await voice_client.disconnect(force=True)
    await asyncio.sleep(0.5)
voice_client = await voice_channel.connect(cls=voice_recv.VoiceRecvClient)
```

2. **Async ORM Fixes** - All `/voice-market` actions wrapped with `sync_to_async`:
   - `browse` action - `get_public_voices()`
   - `search` action - `search_voices()`
   - `my-voices` action - `get_user_voices()`
   - `earnings` action - `get_earnings()`

---

## ElevenLabs Configuration

**Required:** Creator tier or higher ($22/mo minimum)

**API Key Permissions Required:**
- `voices_write` - For creating cloned voices
- `voices_read` - For listing voices

**Current API Key Location:** `.env` → `ELEVENLABS_API_KEY`

---

## Voice Cloning Results

| Voice Name | Status | ElevenLabs ID | Owner |
|------------|--------|---------------|-------|
| DonkeyKing's Voice | Active | (in ElevenLabs) | .donkeyking |

---

## Testing Commands

```bash
# Start all services
make start && make celery

# Start Discord bot (single process!)
pkill -f "run_discord_bot"
source .venv/bin/activate
.venv/bin/python manage.py run_discord_bot

# In Discord:
/voice-market my-voices    # See your cloned voices
/voice-market browse       # Browse marketplace
/voice-market earnings     # Check earnings
```

---

## Next Session Priorities

1. **Make Voice Public** - Add command to toggle voice privacy
2. **Voice Preview** - Generate sample audio from cloned voice
3. **Text-to-Speech** - Use cloned voice for TTS generation
4. **Voice Marketplace Polish** - Complete all actions
5. **Payment Integration** - Stripe for voice purchases

---

## Key Learnings

1. **VoiceRecvClient** is separate from VoiceClient - must use `cls=voice_recv.VoiceRecvClient` in connect()
2. **Django + async** requires `sync_to_async` for ALL ORM operations
3. **ElevenLabs IVC** has 10MB file limit - compress audio first
4. **Discord bot** can have zombie processes - always `pkill` before restart
5. **Audio device matters** - User had audio going to monitor without speakers initially

---

## Commands Reference

| Command | Action | Status |
|---------|--------|--------|
| `/voice-clone start` | Begin recording | Working |
| `/voice-clone stop <name>` | Stop & create clone | Working |
| `/voice-clone status` | Check recording | Working |
| `/voice-market browse` | Browse marketplace | Fixed (async) |
| `/voice-market search <query>` | Search voices | Fixed (async) |
| `/voice-market my-voices` | Show your voices | Fixed (async) |
| `/voice-market earnings` | Show earnings | Fixed (async) |
