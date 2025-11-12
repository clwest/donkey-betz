# API Integration References

**Technical documentation for all external API integrations**

---

## 📚 Available References

### [Stability AI](STABILITY_AI.md) ✅
**Lines:** 650 | **Provider:** Stability AI | **Status:** Fully Integrated

Complete API reference for image generation:
- 13 API endpoints documented
- 4 models (sd3.5-large, SDXL, SD3, Ultra)
- Authentication & error handling
- Credit costs & optimization
- Complete code examples

**Key Endpoints:**
- Generate Image (text-to-image)
- Search & Recolor (color changes)
- Erase (remove objects)
- Inpaint (replace parts)
- Outpaint (extend boundaries)
- Remove Background
- Upscale (3 modes)
- Structure Control (image-to-image)

**Integration File:** `content/image_generation.py` (1,500+ lines)

---

### [Runway ML](RUNWAY_ML.md) ✅
**Lines:** 700 | **Provider:** Runway ML | **Status:** Fully Integrated

Complete API reference for video generation:
- 5 video endpoints
- Async task management system
- 3 models (Gen-3 Turbo, Gen-4 Aleph, Veo 3)
- Polling implementation
- VideoAgent integration

**Key Endpoints:**
- Text-to-Video (generate from text)
- Image-to-Video (animate images)
- Video-to-Video (transform style)
- Extend (make videos longer)
- Upscale (enhance resolution)

**Integration File:** `content/video_provider.py` (800+ lines)

---

### [ElevenLabs](ELEVENLABS.md) ✅
**Lines:** 600 | **Provider:** ElevenLabs | **Status:** Fully Integrated

Complete API reference for audio generation:
- Text-to-Speech (⚡ 1-2 seconds!)
- Sound Effects generation
- 12 professional voice configurations
- ffmpeg audio mixing integration
- AudioAgent coordination

**Key Endpoints:**
- Text-to-Speech (convert text to speech)
- Sound Generation (create sound effects)
- List Voices (available voices)

**Integration File:** `content/elevenlabs_provider.py` (331 lines)

---

### [OpenAI](OPENAI.md) ✅
**Lines:** 720 | **Provider:** OpenAI | **Status:** Fully Integrated

Complete API reference for AI orchestration:
- GPT-5-mini AI Assistant (20+ function tools)
- Whisper voice transcription
- DALL-E 3 image generation (backup)
- Function calling system
- Complete system prompt

**Key Services:**
- Chat Completions (AI Assistant with function calling)
- Audio Transcriptions (Whisper voice-to-text)
- Image Generation (DALL-E 3 backup)

**Integration File:** `core/views_image.py` (7,000+ lines)

---

### [Replicate](REPLICATE.md) ✅
**Lines:** 700 | **Provider:** Replicate | **Status:** Fully Integrated

Complete API reference for character training:
- FLUX LoRA training workflow
- Character model training
- Training monitoring
- Image preparation & ZIP creation
- Best practices

**Key Endpoints:**
- Create Training (start FLUX LoRA training)
- Get Training Status (monitor progress)
- List Trainings (view all trainings)
- Cancel Training (stop training)
- Use Trained Model (generate with model)

**Integration File:** `content/replicate_provider.py` (370 lines)

---

### [DaVinci Resolve + ffmpeg](DAVINCI_RESOLVE_FFMPEG.md) ✅
**Lines:** 850 | **Providers:** DaVinci Resolve Studio + ffmpeg | **Status:** Hybrid Integration

Complete reference for video editing:
- DaVinci Resolve color grading
- ffmpeg video chaining (Session 84!)
- ffmpeg audio mixing (Session 82!)
- Hybrid architecture explained
- Performance comparison

**DaVinci Operations:**
- Color Grading (professional quality)
- Text Overlays (frame-accurate)

**ffmpeg Operations:**
- Video Chaining (2-5 seconds!)
- Audio Mixing (2-5 seconds!)
- Video Information (duration, resolution)

**Integration File:** `content/davinci_provider.py` (900+ lines)

---

## 🎯 API Overview

### API Categories:

**Image Generation:**
- ✅ **Stability AI** - Primary image provider (13 features)
- ✅ **OpenAI DALL-E 3** - Backup option

**Video Generation:**
- ✅ **Runway ML** - Primary video provider (5 features)
- ✅ **DaVinci Resolve** - Color grading
- ✅ **ffmpeg** - Chaining & mixing

**Audio Generation:**
- ✅ **ElevenLabs** - Primary audio provider (2 features)
- ✅ **OpenAI Whisper** - Voice transcription

**AI Orchestration:**
- ✅ **OpenAI GPT-5-mini** - AI Assistant with function calling
- ✅ **Replicate** - Character training

---

## 📊 Integration Status

| API | Status | Endpoints | Lines | Last Updated |
|-----|--------|-----------|-------|--------------|
| Stability AI | ✅ Complete | 13 | 650 | Session 85 |
| Runway ML | ✅ Complete | 5 | 700 | Session 85 |
| ElevenLabs | ✅ Complete | 3 | 600 | Session 85 |
| OpenAI | ✅ Complete | 3 services | 720 | Session 85 |
| Replicate | ✅ Complete | 5 | 700 | Session 85 |
| DaVinci/ffmpeg | ✅ Complete | Hybrid | 850 | Session 85 |

**Total Documentation:** 4,220 lines

---

## 🔑 Authentication

### Environment Variables Required:

```bash
# .env file
STABILITY_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
RUNWAY_API_KEY=rw-xxxxxxxxxxxxxxxxxxxxx
ELEVENLABS_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
REPLICATE_API_TOKEN=r8-xxxxxxxxxxxxxxxxxxxxx

# DaVinci Resolve (optional for color grading)
RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/..."
RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/..."
```

### Verify All APIs:
```bash
python3 scripts/test_api_keys.py
```

---

## ⚡ Performance Summary

### Speed Comparison:

| Operation | Provider | Speed | Quality |
|-----------|----------|-------|---------|
| Image Generation | Stability AI | 2-4s | ⭐⭐⭐⭐⭐ |
| Video Generation | Runway ML | 15-45s | ⭐⭐⭐⭐⭐ |
| Audio Generation | ElevenLabs | 1-2s | ⭐⭐⭐⭐⭐ |
| Video Chaining | ffmpeg | 2-5s | ⭐⭐⭐⭐ |
| Audio Mixing | ffmpeg | 2-5s | ⭐⭐⭐⭐⭐ |
| Color Grading | DaVinci | 20-30s | ⭐⭐⭐⭐⭐ |
| Character Training | Replicate | 15-30min | ⭐⭐⭐⭐⭐ |

---

## 💰 Cost Summary

### Approximate Costs:

**Image Operations:**
- Standard Generation: 6.5 credits (~$0.10)
- Ultra Generation: 8 credits (~$0.12)
- Editing Operations: 3-4 credits (~$0.05)
- Upscaling: 25 credits (~$0.38)

**Video Operations:**
- Gen-3 (5s): ~10 credits (~$1.00)
- Gen-4 (10s): ~30 credits (~$3.00)
- Extension: ~20 credits (~$2.00)

**Audio Operations:**
- Text-to-Speech: ~100 chars (~$0.001)
- Sound Effects: ~250 chars (~$0.003)

**Character Training:**
- FLUX LoRA Training: ~$1.00 per training
- Generates unlimited images after training

---

## 🔧 Error Handling

### Common Error Codes:

**401 Unauthorized:**
- Check API key in .env
- Verify key is active

**429 Rate Limit:**
- Implement exponential backoff
- Reduce request frequency

**402 Insufficient Credits:**
- Add credits to account
- Check credit balance

**500 Server Error:**
- Retry with exponential backoff
- Contact provider support

### Our Error Handling Pattern:
```python
try:
    response = api_call(...)
    response.raise_for_status()
    return {"success": True, "data": ...}

except requests.exceptions.Timeout:
    return {"error": "Request timed out"}

except requests.exceptions.HTTPError as e:
    return {"error": f"HTTP {e.response.status_code}"}

except Exception as e:
    logger.exception("Unexpected error")
    return {"error": str(e)}
```

---

## 🧪 Testing

### Test All APIs:
```bash
# Test API keys
python3 scripts/test_api_keys.py

# Test specific integrations
python3 test_stability_image.py
python3 test_replicate_connection.py
```

### Manual Testing:
```python
# Test image generation
from content.image_generation import StabilityAI
stability = StabilityAI()
result = stability.generate_image_sd3("mountain sunset")

# Test video generation
from content.video_provider import RunwayML
runway = RunwayML()
result = runway.generate_video("ocean waves")

# Test audio generation
from content.elevenlabs_provider import ElevenLabsProvider
elevenlabs = ElevenLabsProvider()
result = elevenlabs.generate_speech("Hello world")
```

---

## 📖 How to Use These References

1. **Find the API you need** (Stability, Runway, etc.)
2. **Read the Overview** to understand capabilities
3. **Check Authentication** requirements
4. **Review Endpoints** for specific operations
5. **Study Code Examples** for implementation
6. **Test Error Handling** patterns
7. **Consult Best Practices** for optimization

---

## 🔗 Related Documentation

- **[Feature Guides](../features/)** - User-facing feature documentation
- **[System Architecture](../architecture/UNIFIED_SYSTEM_MAP.md)** - How APIs connect
- **[Agent Documentation](../agents/)** - Agent orchestration

---

## 🎯 Key Integration Achievements

**Session 75:** Image-to-image style transfer (Stability AI) 🎨✨
**Session 74:** Character training (Replicate FLUX LoRA) 🤖🎨
**Session 84:** Video chaining with ffmpeg 🔗⚡
**Session 82 Part 3:** Audio mixing with ffmpeg 🎵⚡
**Session 73:** Frame-accurate voice control (OpenAI Whisper + GPT-5-mini) 🎤⏱️

---

**All 6 external API integrations are production-ready and fully operational!** 🚀✨
