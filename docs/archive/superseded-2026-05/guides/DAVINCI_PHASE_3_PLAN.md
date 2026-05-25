# DaVinci Expansion Phase 3 - Planning Document

**Created:** November 21, 2025 (Session 163)
**Status:** PLANNING
**Estimated Sessions:** 2-3 sessions

---

## Overview

Phase 3 continues the DaVinci Expansion with advanced video effects. All features use **ffmpeg** (FREE) and follow the established pattern from Phase 1-2.

---

## Proposed Features (Priority Order)

### 1. Watermark/Logo Overlay (RECOMMENDED FIRST)

**Complexity:** Easy
**ffmpeg Filter:** `overlay`
**Use Case:** Brand videos with logo, add copyright marks

**Parameters:**
- `video_id` - Source video
- `image_id` or `image_url` - Logo/watermark image
- `position` - corner placement (top_left, top_right, bottom_left, bottom_right, center)
- `opacity` - 0.0 to 1.0 (default 0.8)
- `scale` - scale logo (default 0.15 = 15% of video width)
- `margin` - pixels from edge (default 20)

**Voice Commands:**
- "Add my logo to video 1"
- "Watermark video 2 with image 5 in the bottom right"
- "Add watermark to videos 1-5"

**ffmpeg Command Example:**
```bash
ffmpeg -i video.mp4 -i logo.png \
  -filter_complex "[1:v]scale=iw*0.15:-1[logo];[0:v][logo]overlay=W-w-20:H-h-20" \
  -c:a copy output.mp4
```

**Implementation Estimate:** ~200 lines (view function + handler + keywords)

---

### 2. Blur Region (Privacy/Censoring)

**Complexity:** Medium
**ffmpeg Filter:** `boxblur` + `overlay`
**Use Case:** Privacy protection, face blurring, hide sensitive info

**Parameters:**
- `video_id` - Source video
- `x`, `y` - Top-left corner of blur region (pixels or percentage)
- `width`, `height` - Size of blur region
- `blur_strength` - 1-20 (default 10)
- `start_time`, `end_time` - Optional time range (blur entire video if not specified)

**Voice Commands:**
- "Blur the top left corner of video 1"
- "Add blur to video 2 from 0:05 to 0:10"
- "Blur region 100,100 to 300,300 in video 3"

**ffmpeg Command Example:**
```bash
ffmpeg -i video.mp4 \
  -filter_complex "[0:v]crop=200:200:100:100,boxblur=10[blur];[0:v][blur]overlay=100:100" \
  output.mp4
```

**Implementation Estimate:** ~300 lines

---

### 3. Video Stabilization

**Complexity:** Medium
**ffmpeg Filter:** `vidstabdetect` + `vidstabtransform` (two-pass)
**Use Case:** Fix shaky handheld footage

**Parameters:**
- `video_id` - Source video
- `shakiness` - Detection sensitivity 1-10 (default 5)
- `smoothing` - Stabilization strength 0-100 (default 15)
- `crop` - Crop mode: 'keep' (black borders) or 'crop' (zoom in)

**Voice Commands:**
- "Stabilize video 1"
- "Fix shaky video 2"
- "Smooth out video 3"

**ffmpeg Command Example:**
```bash
# Pass 1: Detect motion
ffmpeg -i video.mp4 -vf vidstabdetect=shakiness=5:show=0 -f null -

# Pass 2: Apply stabilization
ffmpeg -i video.mp4 -vf vidstabtransform=smoothing=15:crop=keep output.mp4
```

**Note:** Requires `vidstab` library. Test availability first with `ffmpeg -filters | grep vidstab`

**Implementation Estimate:** ~350 lines (two-pass processing)

---

### 4. Text Animations (Enhanced Text Overlay)

**Complexity:** Medium
**ffmpeg Filter:** `drawtext` with expression-based positioning
**Use Case:** Animated titles, scrolling credits, bouncing text

**Parameters:**
- `video_id` - Source video
- `text` - Text to display
- `animation` - type: 'slide_in', 'slide_out', 'fade_in', 'fade_out', 'bounce', 'scroll'
- `position` - start position
- `duration` - animation duration
- `font_size`, `font_color`

**Voice Commands:**
- "Add scrolling text 'Subscribe' to video 1"
- "Slide in title 'Chapter 1' on video 2"
- "Add bouncing text to video 3"

**ffmpeg Command Example (scroll):**
```bash
ffmpeg -i video.mp4 -vf "drawtext=text='Rolling Credits':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-t*50" output.mp4
```

**Implementation Estimate:** ~400 lines (multiple animation types)

---

### 5. Green Screen / Chroma Key

**Complexity:** Hard
**ffmpeg Filter:** `chromakey` or `colorkey`
**Use Case:** Background replacement, special effects

**Parameters:**
- `video_id` - Source video (with green/blue screen)
- `background_video_id` or `background_image_id` - New background
- `key_color` - Color to remove (default: 0x00FF00 green)
- `similarity` - Color match tolerance 0.0-1.0 (default 0.3)
- `blend` - Edge blending 0.0-1.0 (default 0.1)

**Voice Commands:**
- "Remove green screen from video 1 and add video 2 as background"
- "Replace background in video 1 with image 5"
- "Chroma key video 1"

**ffmpeg Command Example:**
```bash
ffmpeg -i background.mp4 -i greenscreen.mp4 \
  -filter_complex "[1:v]chromakey=0x00FF00:0.3:0.1[fg];[0:v][fg]overlay" \
  output.mp4
```

**Implementation Estimate:** ~400 lines

---

## Implementation Pattern

Based on Phase 1-2, each feature requires:

### 1. View Function (`core/views_video.py`)
```python
@csrf_exempt
@require_http_methods(["POST"])
def add_watermark(request):
    """Add watermark/logo overlay to video."""
    # Parameter parsing
    # Hybrid ID resolution (Session 162 pattern)
    # ffmpeg execution
    # Save result to VideoHistory
    # Return JSON response
```

### 2. URL Route (`core/urls.py`)
```python
path('api/video/watermark/', views_video.add_watermark, name='add_watermark'),
```

### 3. Tool Handler (`core/personal_ai_assistant_enhanced.py`)
```python
elif operation == 'add_watermark':
    return self._tool_add_watermark(tool_args)

def _tool_add_watermark(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the add_watermark tool."""
    # Build request, call API, return result
```

### 4. Tool Definition (in `get_tool_definitions()`)
```python
"add_watermark": {
    "type": "string",
    "description": "Add watermark/logo overlay"
}
```

### 5. Keywords (in `operation_keywords`)
```python
'watermark', 'logo', 'brand', 'copyright'
```

---

## Recommended Session Plan

### Session 163: Watermark/Logo Feature
- Implement `add_watermark()` view function
- Add tool handler and definition
- Add keywords
- Test with voice commands
- **Estimated:** ~2 hours, ~250 lines

### Session 164: Blur Region Feature
- Implement `blur_region()` view function
- Add tool handler and definition
- Add keywords
- Test privacy blurring
- **Estimated:** ~2.5 hours, ~300 lines

### Session 165: Video Stabilization
- Check vidstab availability
- Implement two-pass `stabilize_video()` function
- Add tool handler and definition
- Test with shaky footage
- **Estimated:** ~3 hours, ~350 lines

---

## Alternative: PiP Improvements

If Phase 3 feels too ambitious, consider polishing existing PiP:

**Quick Wins:**
1. Increase default scale (25% → 35%)
2. Add border option (1-5px, color selectable)
3. Add shadow effect
4. Support custom x,y positions

**Voice Commands:**
- "Put video 2 in video 1 at 35% size with white border"
- "Add video 2 to corner of video 1 with shadow"

---

## Feature Comparison

| Feature | Complexity | Time | User Value | Uniqueness |
|---------|------------|------|------------|------------|
| Watermark | Easy | 2h | HIGH | Common need |
| Blur | Medium | 2.5h | HIGH | Privacy critical |
| Stabilization | Medium | 3h | HIGH | Pro feature |
| Text Animation | Medium | 3h | MEDIUM | Nice to have |
| Green Screen | Hard | 4h | MEDIUM | Niche use |

---

## Text Overlay Already Exists

**Important Discovery:** Text overlay functionality already exists from Session 128!

**Location:** `core/views_davinci.py:562` - `add_text_overlay_endpoint()`

**Already working:**
- Position: center, lower_third, upper_third
- Timing: start_second, duration
- Font size: 36-144

**Voice command:** "Add text 'Hello' to video 1"

**Consider testing existing text overlay before building text animations!**

---

## Recommendation for Session 163

**Best Path Forward:**

1. **Quick Win:** Implement Watermark/Logo (2 hours, high value)
2. **Test:** Verify text overlay still works
3. **Document:** Update feature list to 15 operations

This keeps momentum high while adding genuinely useful functionality!

---

**Total Phase 3 Potential: 5 new features = 19 total video operations**

All FREE using ffmpeg, all voice-controlled!
