# Video Production Workflows - Complete Design

**Session 175: End-to-End Video Production System**
**Last Updated:** November 24, 2025

---

## Overview

Two distinct video production services built on the same infrastructure:

| Service | Duration | Use Case | Revenue Model |
|---------|----------|----------|---------------|
| **Promo Videos** | 30-60 seconds | Customer marketing, product demos, social ads | Per-video pricing ($50-200) |
| **YouTube Videos** | 2-10 minutes | Content creation, tutorials, explainers | Subscription + per-video |

---

## Current Capabilities Inventory

### Generation (Runway ML)
| Feature | Status | Duration | Cost |
|---------|--------|----------|------|
| Text-to-Video | ✅ Ready | 5-10s | ~10-20 credits |
| Image-to-Video | ✅ Ready | 5-10s | ~10-15 credits |
| Video Extension | ✅ Ready | +8-10s | ~15 credits |
| Video-to-Video Transform | ✅ Ready | 5-10s | ~15 credits |
| Character Performance (Act-Two) | ✅ Ready | 5-10s | ~20 credits |
| **Lip Sync** | ❌ MISSING | Up to 45s | ~5 credits/sec |

### Audio (ElevenLabs + Runway)
| Feature | Status | Notes |
|---------|--------|-------|
| Text-to-Speech | ✅ Ready | 12+ voices, 1-2s response |
| Voice Dubbing | ✅ Ready | Multi-language dubbing |
| Voice Isolation | ✅ Ready | Remove background noise |
| Speech-to-Speech | ✅ Ready | Voice transformation |
| Text-to-Sound (SFX) | ✅ Ready | Sound effects generation |

### Editing (FFmpeg - FREE)
| Feature | Status |
|---------|--------|
| Video Concatenation | ✅ Ready |
| Speed Control (0.25x-4x) | ✅ Ready |
| Trim/Cut | ✅ Ready |
| Transitions (35+ effects) | ✅ Ready |
| Text Overlay (frame-accurate) | ✅ Ready |
| Watermark/Logo | ✅ Ready |
| Color Grading (6 presets) | ✅ Ready |
| Upscale (2x/4x) | ✅ Ready |
| Rotate/Flip | ✅ Ready |
| Fade In/Out | ✅ Ready |
| Crop/Resize | ✅ Ready |
| Audio Controls | ✅ Ready |
| Picture-in-Picture | ✅ Ready |
| Green Screen/Chroma Key | ✅ Ready |
| Auto-Captioning (Whisper) | ✅ Ready |
| Stabilization | ✅ Ready |
| Export Presets (11 platforms) | ✅ Ready |

### Professional (DaVinci Resolve)
| Feature | Status |
|---------|--------|
| ProRes/DNxHD Render | ✅ Ready |
| LUT Application | ✅ Ready |
| Node-based Color Grading | ✅ Ready |

---

## SERVICE 1: Promo Video Production (30-60s)

### Target Use Cases
- Product launch videos
- Social media ads (Instagram, TikTok, YouTube Shorts)
- Company intro videos
- Event promotions
- Testimonial videos (with AI avatar)

### Workflow Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PROMO VIDEO PIPELINE (30-60s)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. INPUT COLLECTION                                                    │
│     ├── Brand assets (logo, colors, fonts)                              │
│     ├── Script/talking points                                           │
│     ├── Product images/videos                                           │
│     └── Voice preference (AI voice or upload)                           │
│                                                                         │
│  2. CONTENT GENERATION                                                  │
│     ├── Generate spokesperson/avatar image (Stability AI)               │
│     ├── Generate background scenes (Stability AI)                       │
│     ├── Generate product shots if needed (Stability AI)                 │
│     └── Generate background music (Runway Text-to-Sound)                │
│                                                                         │
│  3. AUDIO PRODUCTION                                                    │
│     ├── Script → ElevenLabs TTS (professional voice)                    │
│     ├── Split audio into segments (for lip sync)                        │
│     └── Generate sound effects if needed                                │
│                                                                         │
│  4. VIDEO SEGMENT CREATION  ⚠️ REQUIRES LIP SYNC                        │
│     ├── For each 10-15s segment:                                        │
│     │   ├── Avatar image + audio segment → Lip Sync → Talking video     │
│     │   └── Product shots → Image-to-Video animation                    │
│     └── Generate B-roll scenes (Text-to-Video)                          │
│                                                                         │
│  5. ASSEMBLY (FFmpeg)                                                   │
│     ├── Concatenate all segments                                        │
│     ├── Add transitions between scenes                                  │
│     ├── Add text overlays (titles, CTAs)                                │
│     ├── Add watermark/logo                                              │
│     └── Mix in background music                                         │
│                                                                         │
│  6. POST-PRODUCTION                                                     │
│     ├── Color grading (brand colors)                                    │
│     ├── Add captions (Whisper auto-caption)                             │
│     └── Final upscale if needed                                         │
│                                                                         │
│  7. EXPORT                                                              │
│     ├── Platform-specific exports (YouTube, Instagram, TikTok)          │
│     └── ProRes master (DaVinci Resolve)                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Promo Video Templates

#### Template 1: Product Launch (45s)
```
[0-5s]   Logo animation + intro sound
[5-15s]  Avatar introduces product (lip synced)
[15-25s] Product demo shots (animated images)
[25-35s] Avatar explains benefits (lip synced)
[35-42s] Customer testimonial or features
[42-45s] CTA + logo + contact info
```

#### Template 2: Company Intro (60s)
```
[0-5s]   Logo + tagline
[5-20s]  CEO/founder avatar welcome (lip synced)
[20-35s] Service/product showcase (animated scenes)
[35-50s] Team/values montage
[50-55s] Avatar closing statement (lip synced)
[55-60s] CTA + contact info
```

#### Template 3: Social Ad (30s)
```
[0-3s]   Hook/attention grabber
[3-12s]  Problem statement (avatar or text)
[12-22s] Solution showcase
[22-28s] Social proof/benefits
[28-30s] CTA
```

---

## SERVICE 2: YouTube Video Production (2-10 min)

### Target Use Cases
- Educational/tutorial content
- Explainer videos
- News/commentary
- Product reviews
- Story-driven content

### Workflow Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   YOUTUBE VIDEO PIPELINE (2-10 min)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. PRE-PRODUCTION                                                      │
│     ├── Script writing (AI-assisted or manual)                          │
│     ├── Storyboard generation                                           │
│     ├── Scene breakdown (segments of 30-45s each)                       │
│     └── Voice talent selection                                          │
│                                                                         │
│  2. ASSET GENERATION                                                    │
│     ├── Consistent character/presenter images (Character Training)      │
│     ├── Scene backgrounds for each segment                              │
│     ├── Diagrams/infographics for explanations                          │
│     ├── B-roll footage generation                                       │
│     └── Thumbnail image                                                 │
│                                                                         │
│  3. AUDIO PRODUCTION                                                    │
│     ├── Full script → ElevenLabs TTS                                    │
│     ├── Segment into 30-45s chunks (for lip sync limits)                │
│     ├── Generate background music (loopable)                            │
│     └── Sound effects library                                           │
│                                                                         │
│  4. SEGMENT PRODUCTION (Repeat for each 30-45s segment)                 │
│     │                                                                   │
│     │  ⚠️ CRITICAL: LIP SYNC REQUIRED                                   │
│     │                                                                   │
│     ├── Talking Head Segments:                                          │
│     │   └── Character Image + Audio → Lip Sync → 30-45s video           │
│     │                                                                   │
│     ├── Demonstration Segments:                                         │
│     │   ├── Product/concept images → Image-to-Video                     │
│     │   └── Voiceover added via FFmpeg                                  │
│     │                                                                   │
│     ├── B-Roll Segments:                                                │
│     │   ├── Text-to-Video for generic scenes                            │
│     │   └── Stock footage integration                                   │
│     │                                                                   │
│     └── Screen Recording Segments (if tutorial):                        │
│         └── Import + voiceover                                          │
│                                                                         │
│  5. CHAPTER ASSEMBLY                                                    │
│     ├── Group segments into chapters/sections                           │
│     ├── Add chapter transitions                                         │
│     ├── Insert chapter title cards                                      │
│     └── Add progress indicators                                         │
│                                                                         │
│  6. FULL VIDEO ASSEMBLY (FFmpeg + DaVinci)                              │
│     ├── Concatenate all chapters                                        │
│     ├── Add intro sequence                                              │
│     ├── Add outro sequence (subscribe CTA)                              │
│     ├── Mix background music (ducking during speech)                    │
│     ├── Add lower thirds                                                │
│     └── Insert subscribe/like reminders                                 │
│                                                                         │
│  7. POST-PRODUCTION                                                     │
│     ├── Color correction for consistency                                │
│     ├── Audio normalization                                             │
│     ├── Auto-captioning (Whisper)                                       │
│     └── Quality review                                                  │
│                                                                         │
│  8. EXPORT & PUBLISH                                                    │
│     ├── YouTube optimized export (1080p/4K)                             │
│     ├── Generate YouTube chapters from segments                         │
│     ├── Create description with timestamps                              │
│     └── Generate SEO tags                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### YouTube Video Templates

#### Template 1: Tutorial/How-To (5 min)
```
[0:00-0:15]   Hook + intro
[0:15-0:30]   What you'll learn (outline)
[0:30-1:30]   Step 1 (presenter + demonstration)
[1:30-2:30]   Step 2 (presenter + demonstration)
[2:30-3:30]   Step 3 (presenter + demonstration)
[3:30-4:30]   Common mistakes / Pro tips
[4:30-5:00]   Recap + CTA
```

#### Template 2: Explainer (3 min)
```
[0:00-0:10]   Hook question
[0:10-0:30]   Problem statement
[0:30-1:30]   Main explanation (presenter)
[1:30-2:15]   Visual examples/diagrams
[2:15-2:45]   Summary
[2:45-3:00]   CTA + related videos
```

#### Template 3: News/Commentary (8 min)
```
[0:00-0:20]   Headline hook
[0:20-1:00]   Context/background
[1:00-4:00]   Main story (with B-roll)
[4:00-6:00]   Analysis/commentary (presenter)
[6:00-7:30]   Implications/predictions
[7:30-8:00]   Outro + engagement CTA
```

---

## Missing Features to Implement

### Priority 1: CRITICAL (Blocks both workflows)

#### 1. Runway Lip Sync Integration
```python
# New method needed in video_provider.py
def lip_sync(
    self,
    image_or_video_url: str,
    audio_url: str = None,      # Option 1: Use audio file
    text: str = None,           # Option 2: Generate speech
    voice_id: str = None,       # For TTS option
    **kwargs
) -> VideoGenerationResult:
    """
    Create video with lip-synced speech

    Supports up to 45 seconds per call
    Cost: ~5 credits per second of audio
    """
```

**Estimated Implementation:** 4-6 hours
**Files to Modify:**
- `content/video_provider.py` - Add lip_sync method
- `core/views_video.py` - Add endpoint
- `core/personal_ai_assistant_enhanced.py` - Add tool definition
- `ai_core/templates/ai_image_studio.html` - Add UI

### Priority 2: HIGH (Enables automation)

#### 2. Script-to-Segments Processor
```python
# New service: content/script_processor.py
def process_script(
    script: str,
    max_segment_duration: int = 30,  # Lip sync limit
    include_directions: bool = True
) -> List[ScriptSegment]:
    """
    Break script into segments for video production

    Returns list of segments with:
    - Text for TTS
    - Estimated duration
    - Scene directions
    - Visual suggestions
    """
```

#### 3. Video Project Orchestrator
```python
# New service: content/video_orchestrator.py
class VideoProjectOrchestrator:
    """
    Coordinates end-to-end video production

    Manages:
    - Asset generation queue
    - Segment production pipeline
    - Assembly workflow
    - Export and delivery
    """

    def create_promo_video(self, config: PromoVideoConfig) -> VideoProject
    def create_youtube_video(self, config: YouTubeVideoConfig) -> VideoProject
    def get_project_status(self, project_id: str) -> ProjectStatus
```

### Priority 3: MEDIUM (Quality improvements)

#### 4. Audio Ducking for Background Music
- Automatically lower music during speech
- FFmpeg filter: `sidechaincompress`

#### 5. Consistent Character Generation
- Use trained LoRA models for consistent presenter
- Multiple poses/expressions from same character

#### 6. Smart Transition Selection
- AI-suggested transitions based on scene content
- Maintain visual consistency

### Priority 4: NICE-TO-HAVE

#### 7. Batch Processing Dashboard
- Queue multiple videos
- Progress tracking
- Cost estimation

#### 8. Template Library
- Pre-built video structures
- Customizable components

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Implement Runway Lip Sync in video_provider.py
- [ ] Create lip sync endpoint and AI Assistant tool
- [ ] Test lip sync with ElevenLabs audio
- [ ] Verify mouth movement quality

### Phase 2: Promo Video MVP (Week 2)
- [ ] Create script processor service
- [ ] Build promo video orchestrator
- [ ] Implement Template 1: Product Launch
- [ ] End-to-end test: script → video

### Phase 3: YouTube Video MVP (Week 3)
- [ ] Extend orchestrator for longer videos
- [ ] Implement chapter assembly
- [ ] Add audio ducking
- [ ] Implement Template 1: Tutorial

### Phase 4: Polish & Scale (Week 4)
- [ ] Template library expansion
- [ ] Batch processing
- [ ] Quality improvements
- [ ] Documentation & training

---

## Cost Estimation

### Promo Video (45s)
| Component | Cost |
|-----------|------|
| Avatar image | ~$0.03 (Stability AI) |
| Background scenes (3) | ~$0.09 |
| TTS Audio (45s) | ~$0.05 (ElevenLabs) |
| Lip Sync (45s) | ~$2.25 (5 credits × 45s × $0.01) |
| Background music | ~$0.10 (Runway) |
| FFmpeg editing | FREE |
| **Total** | **~$2.52** |
| **Sell Price** | **$50-200** |
| **Margin** | **95-99%** |

### YouTube Video (5 min = 300s)
| Component | Cost |
|-----------|------|
| Character images (5 poses) | ~$0.15 |
| Scene backgrounds (10) | ~$0.30 |
| TTS Audio (300s) | ~$0.30 |
| Lip Sync (300s in 45s chunks = 7 calls) | ~$15.00 |
| B-roll generation (5 clips) | ~$1.00 |
| Background music | ~$0.10 |
| FFmpeg editing | FREE |
| **Total** | **~$16.85** |
| **Sell Price** | **$200-500** |
| **Margin** | **92-97%** |

---

## Success Metrics

### Quality
- Lip sync accuracy > 90% (natural looking)
- No visible glitches or artifacts
- Consistent character appearance
- Professional audio quality

### Performance
- Promo video production < 15 minutes
- YouTube video production < 1 hour
- Batch processing: 10+ videos/day

### Business
- Customer satisfaction > 4.5/5
- Repeat customer rate > 60%
- Revenue per video meets targets

---

## Next Steps

1. **Immediate:** Implement Runway Lip Sync
2. **This Week:** Test end-to-end promo video
3. **Next Week:** YouTube video capability
4. **Ongoing:** Template expansion and optimization

---

*Document created: Session 175 - November 24, 2025*
