# Session 443: Voice Marketplace - Publish & Preview

**Date:** December 14, 2025
**Status:** Voice Marketplace LIVE | DonkeyKing's Voice PUBLIC | Preview Working

---

## Major Accomplishments

### 1. Voice Marketplace Publishing System

Added ability for users to make their cloned voices available in the public marketplace:

```
/voice-market publish DonkeyKing    # Make voice public
/voice-market unpublish DonkeyKing  # Make voice private again
```

**Features:**
- Toggle `is_public` flag on VoiceProfile model
- Only voice owner can publish/unpublish
- Immediate visibility in `/voice-market browse`

### 2. Voice Preview System

Added audio preview generation for marketplace voices:

```
/voice-market preview DonkeyKing
/voice-market preview 25c189c1    # By ID prefix
```

**Features:**
- Generates TTS audio using ElevenLabs API
- Uses voice's `sample_text` or default preview text
- Sends audio file directly to Discord channel
- Shows voice details (owner, price, description)
- Works with both voice name and ID prefix lookups

### 3. Complete Marketplace Flow

Full user journey now supported:

```
1. /voice-clone start          # Record your voice
2. /voice-clone stop MyVoice   # Create clone
3. /voice-market my-voices     # See your voices (private by default)
4. /voice-market publish MyVoice   # Make it public
5. /voice-market browse        # See all public voices
6. /voice-market preview <voice>   # Hear any voice
7. /voice-market unpublish MyVoice # Make private again
```

---

## Files Modified

### `core/services/discord_bot.py`

1. **Publish Action** (~30 lines):
```python
elif action == "publish":
    @sync_to_async
    def publish_voice(discord_id, voice_name):
        voice = VoiceProfile.objects.filter(
            owner__discord_id=discord_id,
            name__icontains=voice_name
        ).first()
        voice.is_public = True
        voice.save(update_fields=['is_public', 'updated_at'])
        return voice, True, None
```

2. **Unpublish Action** (~30 lines):
```python
elif action == "unpublish":
    @sync_to_async
    def unpublish_voice(discord_id, voice_name):
        voice.is_public = False
        voice.save(update_fields=['is_public', 'updated_at'])
        return voice, True, None
```

3. **Preview Action** (~60 lines):
```python
elif action == "preview":
    # Find voice by ID or name
    # Check access (public or owner)
    # Generate TTS with ElevenLabs
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": preview_text, "model_id": "eleven_multilingual_v2"},
        timeout=60
    )
    # Send audio file to Discord
```

---

## Voice Marketplace Status

| Voice Name | Owner | Status | Price |
|------------|-------|--------|-------|
| DonkeyKing's Voice | .donkeyking | **PUBLIC** | $0.50/min |

---

## Testing Commands

```bash
# Start Discord bot
pkill -f "run_discord_bot"
source .venv/bin/activate
.venv/bin/python manage.py run_discord_bot

# In Discord:
/voice-market browse           # See public marketplace
/voice-market my-voices        # See your voices
/voice-market publish <name>   # Make voice public
/voice-market unpublish <name> # Make voice private
/voice-market preview <voice>  # Hear voice preview
```

---

## Session 444 Priorities

1. **Voice Purchase Flow** - Stripe integration for buying voice usage
2. **Voice Pricing UI** - Set custom prices per voice
3. **Usage Tracking** - Track minutes/characters generated
4. **Revenue Dashboard** - Show earnings from voice sales
5. **Voice Categories** - Filter by genre, accent, use case

---

## Revenue Model

- **70/30 Split**: Voice owners get 70%, platform gets 30%
- **Pricing Models**: Per minute, per 1000 characters, or flat rate
- **Default Price**: $0.50/min (configurable per voice)

---

## Commands Reference

| Command | Action | Status |
|---------|--------|--------|
| `/voice-clone start` | Begin recording | Working |
| `/voice-clone stop <name>` | Create clone | Working |
| `/voice-clone status` | Check recording | Working |
| `/voice-market browse` | Browse marketplace | Working |
| `/voice-market search <query>` | Search voices | Working |
| `/voice-market my-voices` | Show your voices | Working |
| `/voice-market earnings` | Show earnings | Working |
| `/voice-market publish <name>` | Make voice public | **NEW** |
| `/voice-market unpublish <name>` | Make voice private | **NEW** |
| `/voice-market preview <voice>` | Hear voice sample | **NEW** |
| `/voice-ask` | Ask agent, hear response | Working |

---

**Voice Marketplace is LIVE! First public voice: DonkeyKing's Voice!**
