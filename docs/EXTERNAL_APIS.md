# External API Integrations

**Last Updated:** December 10, 2025
**Total Integrations:** 6 production APIs + 1 unused

---

## Quick Reference

| API | Purpose | Status | Cost |
|-----|---------|--------|------|
| Stability AI | Image generation/editing | Active | ~$0.10/image |
| Runway ML | Video generation | Active | ~$1-3/video |
| ElevenLabs | Audio/TTS | Active | ~$0.001/100 chars |
| OpenAI | LLM + Whisper | Active | ~$0.01/call |
| Replicate | 3D + LoRA training | Active | ~$1/training |
| DaVinci Resolve | Pro video rendering | **UNUSED** | $300 (license) |
| Serper | Web search | Active | ~$0.01/search |

---

## 1. Stability AI (Images)

**API Base:** `https://api.stability.ai`
**Integration:** `content/image_generation.py` (1,500+ lines)
**Documentation:** [docs/apis/STABILITY_AI.md](apis/STABILITY_AI.md)

### Features (13 endpoints)

| Feature | Endpoint | Credits |
|---------|----------|---------|
| Generate (Core) | `/v2beta/stable-image/generate/core` | 6.5 |
| Generate (SDXL) | `/v1/generation/{engine}/text-to-image` | Varies |
| Generate (SD3) | `/v2beta/stable-image/generate/sd3` | 6.5 |
| Generate (Ultra) | `/v2beta/stable-image/generate/ultra` | 8 |
| Recolor | `/v2beta/stable-image/edit/recolor` | 3 |
| Erase | `/v2beta/stable-image/edit/erase` | 3 |
| Inpaint | `/v2beta/stable-image/edit/inpaint` | 3 |
| Outpaint | `/v2beta/stable-image/edit/outpaint` | 4 |
| Remove Background | `/v2beta/stable-image/edit/remove-background` | 3 |
| Fast Upscale | `/v2beta/stable-image/upscale/fast` | 25 |
| Conservative Upscale | `/v2beta/stable-image/upscale/conservative` | 25 |
| Creative Upscale | `/v2beta/stable-image/upscale/creative` | 40 |
| Search & Replace | `/v2beta/stable-image/edit/search-and-replace` | 25 |

### Usage

```python
from content.image_generation import StabilityAI

stability = StabilityAI()

# Generate image
result = stability.generate_image_sd3(
    prompt="A cyberpunk cityscape at sunset",
    aspect_ratio="16:9",
    style_preset="cinematic"
)

# Remove background
result = stability.remove_background(image_path="/path/to/image.png")

# Upscale
result = stability.upscale_image(
    image_path="/path/to/image.png",
    mode="creative",
    creativity=0.3
)
```

### Environment Variable

```bash
STABILITY_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

---

## 2. Runway ML (Video)

**API Base:** `https://api.dev.runwayml.com`
**Integration:** `content/video_provider.py` (800+ lines)
**Documentation:** [docs/apis/RUNWAY_ML.md](apis/RUNWAY_ML.md)

### Features (5 endpoints)

| Feature | Description | Credits |
|---------|-------------|---------|
| Text-to-Video | Generate video from text | ~10 |
| Image-to-Video | Animate still image | ~10 |
| Video-to-Video | Style transfer | ~20 |
| Extend | Make video longer | ~20 |
| Upscale | Enhance resolution | ~10 |

### Usage

```python
from content.video_provider import RunwayML

runway = RunwayML()

# Generate video
result = runway.generate_video(
    prompt="Ocean waves crashing on rocks",
    duration=5
)

# Animate image
result = runway.animate_image(
    image_path="/path/to/image.png",
    motion_prompt="Slow zoom in with clouds moving"
)
```

### Models

- **Gen-3 Turbo** - Fast, good quality
- **Gen-4 Aleph** - Highest quality, slower
- **Veo 3** - Google's model (experimental)

### Environment Variable

```bash
RUNWAY_API_KEY=rw-xxxxxxxxxxxxxxxxxxxxx
```

---

## 3. ElevenLabs (Audio)

**API Base:** `https://api.elevenlabs.io`
**Integration:** `content/elevenlabs_provider.py` (331 lines)
**Documentation:** [docs/apis/ELEVENLABS.md](apis/ELEVENLABS.md)

### Features (2 endpoints)

| Feature | Endpoint | Speed |
|---------|----------|-------|
| Text-to-Speech | `/v1/text-to-speech/{voice_id}` | 1-2 seconds |
| Sound Effects | `/v1/sound-generation` | 2-3 seconds |

### Voices (12 configured)

```python
VOICES = {
    'alloy': 'pNInz6obpgDQGcFmaJgB',      # Neutral
    'echo': 'TxGEqnHWrfWFTfGW9XjX',       # Deep
    'fable': 'CYw3kZ02Hs0563khs1Fj',      # British
    'onyx': 'IKne3meq5aSn9XLyUdCD',       # Strong
    'nova': 'z9fAnlkpzviPz146aGWa',       # Warm
    'shimmer': 'N2lVS1w4EtoT3dr4eOWO',    # Soft
    # ... 6 more
}
```

### Usage

```python
from content.elevenlabs_provider import ElevenLabsProvider

elevenlabs = ElevenLabsProvider()

# Generate speech
result = elevenlabs.generate_speech(
    text="Welcome to our platform!",
    voice="alloy",
    output_format="mp3_44100_128"
)

# Generate sound effect
result = elevenlabs.generate_sound_effect(
    prompt="Dramatic thunder with rain",
    duration_seconds=5
)
```

### Environment Variable

```bash
ELEVENLABS_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

---

## 4. OpenAI (LLM + Whisper)

**API Base:** `https://api.openai.com`
**Integration:** `core/views_image.py`, all agents
**Documentation:** [docs/apis/OPENAI.md](apis/OPENAI.md)

### Services

| Service | Model | Purpose |
|---------|-------|---------|
| Chat Completions | gpt-5-mini | Agent reasoning |
| Audio Transcription | whisper-1 | Voice-to-text |
| Image Generation | dall-e-3 | Backup image gen |
| Embeddings | text-embedding-3-small | Semantic search |

### GPT-5-mini Configuration

**CRITICAL:** GPT-5-mini is a reasoning model with different parameters!

```python
# CORRECT
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000,  # NOT max_tokens!
    timeout=120
    # NO temperature parameter!
)

# WRONG - will cause errors
response = client.chat.completions.create(
    model="gpt-5-mini",
    max_tokens=1000,      # Wrong parameter
    temperature=0.7       # Not supported
)
```

### Usage

```python
from openai import OpenAI

client = OpenAI()

# Chat completion (agent)
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": "You are an image generation agent..."},
        {"role": "user", "content": "Create a logo for a tech startup"}
    ],
    max_completion_tokens=6000,
    tools=[...]  # Function calling
)

# Transcription
response = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="en"
)

# Embeddings
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="AI content generation trends"
)
```

### Environment Variable

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

---

## 5. Replicate (3D + Training)

**API Base:** `https://api.replicate.com`
**Integration:** `content/replicate_provider.py` (370 lines)
**Documentation:** [docs/apis/REPLICATE.md](apis/REPLICATE.md)

### Features

| Feature | Model | Cost |
|---------|-------|------|
| 3D Generation | shap-e | ~$0.05 |
| FLUX LoRA Training | flux-dev-lora-trainer | ~$1.00 |
| Character Generation | flux-dev (with LoRA) | ~$0.10 |

### Usage

```python
from content.replicate_provider import ReplicateProvider

replicate = ReplicateProvider()

# Convert image to 3D
result = replicate.convert_to_3d(
    image_path="/path/to/image.png",
    output_format="glb"
)

# Train character LoRA
result = replicate.train_character(
    images_zip="/path/to/training_images.zip",
    trigger_word="my_character",
    steps=1000
)

# Generate with trained model
result = replicate.generate_with_lora(
    prompt="my_character in a cyberpunk setting",
    lora_url="https://replicate.delivery/..."
)
```

### Environment Variable

```bash
REPLICATE_API_TOKEN=r8-xxxxxxxxxxxxxxxxxxxxx
```

---

## 6. DaVinci Resolve (Video Rendering)

**Status:** FULLY BUILT BUT UNUSED
**Investment:** $300+ (license)
**Location:** `/resolve_node/`
**Documentation:** [DAVINCI_RESOLVE.md](DAVINCI_RESOLVE.md)

### Features (Built)

| Feature | Status | Notes |
|---------|--------|-------|
| REST API | Complete | FastAPI on port 5001 |
| Job Queue | Complete | Persistent queue |
| Render Templates | Complete | MP4, ProRes |
| Django Webhook | Complete | Auto-upload |
| Authentication | Complete | Token-based |

### Why Unused

We use ffmpeg for quick operations (2-5 seconds), while DaVinci Resolve is slower (20-30 seconds) but offers professional features like color grading.

### Activation Path

1. Start DaVinci Resolve
2. Start render node: `cd resolve_node && python app.py`
3. Add UI toggle for "Professional Render"

### Environment Variables

```bash
RENDER_NODE_TOKEN="your-secure-token"
DJANGO_BACKEND_URL="http://localhost:8000"
```

---

## 7. Serper (Web Search)

**API Base:** `https://google.serper.dev`
**Integration:** ResearchAgent tools
**Cost:** ~$0.01/search

### Usage

```python
import requests

response = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": SERPER_API_KEY},
    json={"q": "AI trends 2025", "num": 10}
)
```

### Environment Variable

```bash
SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxxx
```

---

## Cost Summary

### Monthly Estimates (Light Usage)

| API | Est. Monthly | Notes |
|-----|--------------|-------|
| Stability AI | $20-50 | 200-500 images |
| Runway ML | $50-100 | 20-50 videos |
| ElevenLabs | $5-10 | ~5000 chars/month |
| OpenAI | $20-50 | Agent calls + embeddings |
| Replicate | $10-20 | Occasional 3D/training |
| Serper | $5-10 | Research queries |
| **Total** | **$110-240** | |

### Per-Operation Costs

| Operation | Cost |
|-----------|------|
| Image (SD3) | ~$0.10 |
| Image (Ultra) | ~$0.12 |
| Upscale | ~$0.40 |
| Video (5s) | ~$1.00 |
| Video (10s) | ~$3.00 |
| TTS (100 chars) | ~$0.001 |
| 3D conversion | ~$0.05 |
| LoRA training | ~$1.00 |
| Agent call | ~$0.01 |
| Embedding | ~$0.0001 |

---

## Error Handling Pattern

All integrations follow this pattern:

```python
try:
    response = api_call(...)
    response.raise_for_status()
    return {"success": True, "data": response.json()}

except requests.exceptions.Timeout:
    logger.error("Request timed out")
    return {"success": False, "error": "Request timed out"}

except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP {e.response.status_code}: {e.response.text}")
    if e.response.status_code == 402:
        return {"success": False, "error": "Insufficient credits"}
    elif e.response.status_code == 429:
        return {"success": False, "error": "Rate limited"}
    return {"success": False, "error": f"HTTP {e.response.status_code}"}

except Exception as e:
    logger.exception("Unexpected error")
    return {"success": False, "error": str(e)}
```

---

## Testing APIs

### Quick Test Script

```bash
# Test all API connections
python scripts/test_api_keys.py

# Test specific APIs
python test_stability_image.py
python test_replicate_connection.py
```

### Manual Testing

```python
# Test Stability AI
from content.image_generation import StabilityAI
stability = StabilityAI()
result = stability.generate_image_sd3("test image")
print(result)

# Test Runway ML
from content.video_provider import RunwayML
runway = RunwayML()
result = runway.generate_video("test video", duration=5)
print(result)

# Test ElevenLabs
from content.elevenlabs_provider import ElevenLabsProvider
elevenlabs = ElevenLabsProvider()
result = elevenlabs.generate_speech("Hello world", voice="alloy")
print(result)
```

---

## Related Documentation

- [docs/apis/](apis/) - Detailed API references (4,220 lines total)
- [DAVINCI_RESOLVE.md](DAVINCI_RESOLVE.md) - Unused render node
- [ARCHITECTURE.md](ARCHITECTURE.md) - System integration
