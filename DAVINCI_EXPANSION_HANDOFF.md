# 🎬 DaVinci Resolve Feature Expansion - Session 160 Handoff

**Created:** November 21, 2025
**Updated:** November 21, 2025 - Session 160 (Phase 1 COMPLETE!)
**Purpose:** Leverage $295 DaVinci Resolve Studio investment to build professional video editing features
**Current Status:** ✅ PHASE 1 COMPLETE! (5/5 features) | 7/20+ features total
**Next Goal:** Phase 2 - Advanced Effects (Fade, Crop, Rotate, PiP, Audio)

---

## 🎉 PHASE 1 COMPLETE - Session 160

### ✅ All 5 Phase 1 Features Implemented:

| Feature | Session | Backend Function | URL | Status |
|---------|---------|------------------|-----|--------|
| Frame Extraction | 159 | `extract_video_frame()` | `/api/video/extract-frame/` | ✅ |
| Video Reverse | 159 | `reverse_video()` | `/api/video/reverse/` | ✅ |
| Video Trimming | 159 | `trim_video()` | `/api/video/trim/` | ✅ |
| Speed Control | 160 | `change_video_speed()` | `/api/video/speed/` | ✅ |
| Video Concatenation | 160 | `concatenate_videos()` | `/api/video/concatenate/` | ✅ |

### Natural Language Commands (All Working!):
- "Extract frame at 5 seconds from video 1"
- "Reverse video 1" / "Play video 3 backwards"
- "Trim video 1 from 10 to 20 seconds"
- "Make video 1 slow motion (0.5x)" / "Speed up video 2 to 2x"
- "Combine videos 1, 2, 3" / "Merge videos 5-8 together"

### Test Results:
- ✅ Frame extraction: 91KB JPG created
- ✅ Video reverse: 1.17MB reversed video
- ✅ Video trim: 1.37MB trimmed video (3s from 5s source)
- ✅ Speed control: 1.01MB slow-motion (3s → 6s at 0.5x)
- ✅ Video concatenation: 2.31MB combined (6s + 3s = 9s)

### Cost: FREE! All operations use ffmpeg locally!

---

## 🎯 Quick Start - Your $295 Investment is READY!

### What You Have Right Now:

**✅ DaVinci Resolve Studio** ($295 investment)
- Location: `/Applications/DaVinci Resolve/`
- Python API enabled and configured
- Professional color grading
- Industry-standard video editing

**✅ Render Node Service** (Session 103)
- FastAPI server on port 5001
- Located: `/Users/donkeyking/development/unified-donkey-betz/resolve_node/`
- Job queue system
- Automatic result upload

**✅ Current Features Working:**
1. **Text Overlay** - "Add text 'Welcome' to video 5 at 8 seconds"
2. **Color Grading** - "Make video 7 look cinematic"

**🚀 Ready to Add:** 18 more powerful features!

---

## 📊 Current System Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Django Backend (localhost:8000)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │   GPT-5-mini Personal Assistant                  │  │
│  │   (Natural Language → Tool Calls)                │  │
│  └─────────────────┬────────────────────────────────┘  │
│                    │                                    │
│                    ▼                                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │   Video Editing Tools (Session 128)              │  │
│  │   • add_text_overlay()                           │  │
│  │   • apply_color_grading()                        │  │
│  │   • upscale_video() (ffmpeg - Session 154)      │  │
│  │   • apply_video_effect() (ffmpeg - Session 154) │  │
│  └─────────────────┬────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────┘
                     │ HTTP POST
                     ▼
      ┌──────────────────────────────────────┐
      │  DaVinci Resolve Render Node         │
      │  FastAPI Server (localhost:5001)     │
      ├──────────────────────────────────────┤
      │  📂 resolve_node/                    │
      │  ├── app.py (FastAPI routes)         │
      │  ├── job_queue.py (Job management)   │
      │  ├── resolve_controller.py           │
      │  ├── jobs/ (pending jobs)            │
      │  ├── results/ (rendered videos)      │
      │  └── logs/ (operation logs)          │
      └──────────────────┬───────────────────┘
                         │ Python API
                         ▼
            ┌────────────────────────────┐
            │   DaVinci Resolve Studio   │
            │   (Must be running)        │
            └────────────────────────────┘
```

---

## 🏗️ How to Start the Render Node

### Option 1: Start Render Node Manually
```bash
cd /Users/donkeyking/development/unified-donkey-betz/resolve_node

# Install dependencies (first time only)
pip install -r requirements.txt

# Start DaVinci Resolve first (IMPORTANT!)
open "/Applications/DaVinci Resolve/DaVinci Resolve.app"

# Wait 10 seconds for Resolve to fully launch...

# Start the render node
python app.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:5001
# DaVinci Resolve Render Node Started!
```

### Option 2: Test Mode (No Resolve Required)
```bash
cd resolve_node
MOCK_MODE=true python app.py

# Runs in mock mode for testing API calls
# Useful for development without opening Resolve
```

### Check if Running:
```bash
curl http://localhost:5001/health
# Expected: {"status": "healthy", "resolve_connected": true}
```

---

## 🎨 Current Features - What's Already Built

### 1. Text Overlay (Session 128) ✅

**Natural Language:**
- "Add text 'Welcome' to video 5"
- "Put title 'My Video' at the top of video 3 for 5 seconds"
- "Add caption 'Subscribe!' at 10 seconds for 3 seconds"

**Code Location:**
- Tool Definition: `core/personal_ai_assistant_enhanced.py:241`
- Handler: `core/personal_ai_assistant_enhanced.py:1718`
- Backend: `core/views_video.py` (uses ffmpeg)

**Parameters:**
```python
{
  "video_id": "123 or UUID",
  "text": "Your text here",
  "position": "center|lower_third|upper_third",
  "start_second": 0,        # When to show
  "duration": 3,            # How long (seconds)
  "font_size": 72           # 36-144
}
```

### 2. Color Grading (Session 128) ✅

**Natural Language:**
- "Make video 7 look cinematic"
- "Apply vintage filter to my last video"
- "Add dramatic color grading to video 2"

**Code Location:**
- Tool Definition: `core/personal_ai_assistant_enhanced.py:247`
- Handler: `core/personal_ai_assistant_enhanced.py:1760`
- Backend: `core/views_video.py` (uses ffmpeg)

**Available Styles:**
| Style | Effect | Perfect For |
|-------|--------|-------------|
| cinematic_warm | Orange/golden tones | Film-like, sunset vibes |
| cinematic_cool | Blue/teal tones | Professional, modern |
| vintage | Retro film look + grain | Nostalgic, classic |
| modern | Clean and crisp | Contemporary, minimal |
| high_contrast | Bold dramatic look | Music videos, sports |
| soft | Muted gentle tones | Romantic, calm |
| vibrant | Saturated vivid colors | Social media, ads |

### 3. Video Upscaling (Session 154) ✅

**Natural Language:**
- "Upscale video 1"
- "Enhance video quality 2x"

**Uses:** ffmpeg lanczos algorithm (free!)

### 4. Video Effects (Session 154) ✅

**Natural Language:**
- "Apply cinematic effect to video 5"
- "Make video 3 look vintage"

**6 Effects:** cinematic, vintage, noir, warm, cool, vibrant

---

## 🚀 Next Features to Build - Prioritized List

### Phase 1: Essential Editing (High Priority) ✅ COMPLETE!

**Status:** 5/5 Features Implemented in Sessions 159-160!

#### 1. **Frame Extraction** ✅ DONE! (Session 159)
**Use Cases:** Create thumbnails, pull stills for social media
**Natural Language:** "Extract frame at 5 seconds from video 1"
**Complexity:** ⭐ (Very Easy - 1 hour)
**Method:** ffmpeg single frame export

**Implementation Pattern:**
```python
# New GPT tool: extract_frame
{
  "video_id": "123",
  "timestamp": 5.0,  # seconds
  "format": "jpg"    # or "png"
}

# ffmpeg command:
ffmpeg -i input.mp4 -ss 5.0 -frames:v 1 output.jpg
```

#### 2. **Video Trimming** ✅ DONE! (Session 159)
**Use Cases:** Cut clips, remove unwanted sections
**Natural Language:**
- "Trim video 1 from 10 to 20 seconds"
- "Keep only the first 15 seconds of video 2"
- "Cut video 3 from 0:30 to 1:45"

**Complexity:** ⭐⭐ (Easy - 2 hours)
**Method:** ffmpeg with precise timestamps

**Implementation Pattern:**
```python
# New GPT tool: trim_video
{
  "video_id": "123",
  "start_time": 10.0,   # seconds or "00:00:10"
  "end_time": 20.0,     # seconds or "00:00:20"
  "keep_audio": true
}

# ffmpeg command:
ffmpeg -i input.mp4 -ss 10.0 -to 20.0 -c copy output.mp4
```

#### 3. **Speed Control** ✅ DONE! (Session 160)
**Use Cases:** Slow motion, time-lapse, fast forward
**Natural Language:**
- "Make video 1 slow motion (0.5x speed)"
- "Speed up video 2 by 2x"
- "Create time-lapse effect on video 3"

**Complexity:** ⭐⭐ (Medium - 2-3 hours)
**Method:** ffmpeg setpts filter

**Implementation Pattern:**
```python
# New GPT tool: adjust_video_speed
{
  "video_id": "123",
  "speed": 0.5,      # 0.25-4.0 (0.5 = slow, 2.0 = fast)
  "adjust_audio": true,  # Also speed up audio
  "smooth": true     # Use motion interpolation
}

# ffmpeg command (video only):
ffmpeg -i input.mp4 -filter:v "setpts=2.0*PTS" output.mp4
# 2.0 = half speed, 0.5 = double speed

# With audio adjustment:
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" -map "[v]" -map "[a]" output.mp4
```

#### 4. **Video Reverse** ✅ DONE! (Session 159)
**Use Cases:** Creative effects, reveals
**Natural Language:**
- "Reverse video 1"
- "Play video 2 backwards"

**Complexity:** ⭐⭐ (Easy - 1-2 hours)
**Method:** ffmpeg reverse filter

**Implementation Pattern:**
```python
# New GPT tool: reverse_video
{
  "video_id": "123",
  "reverse_audio": true  # Also reverse audio
}

# ffmpeg command:
ffmpeg -i input.mp4 -vf reverse -af areverse output.mp4
```

#### 5. **Video Concatenation** ✅ DONE! (Session 160)
**Use Cases:** Create compilations, chain scenes
**Natural Language:**
- "Combine videos 1, 2, 3 into one video"
- "Merge video 5 and video 8"
- "Chain together videos 10-15"

**Complexity:** ⭐⭐ (Medium - 3 hours) - Already have chain_videos() in code!
**Method:** ffmpeg concat demuxer or existing chain_videos()

**Implementation Pattern:**
```python
# New GPT tool: concatenate_videos
{
  "video_ids": ["123", "456", "789"],
  "transition": "none",  # or "fade", "crossfade"
  "transition_duration": 0.5  # seconds
}

# Existing function in content/davinci_provider.py:
# chain_videos(video_paths, output_path)
```

---

### Phase 2: Advanced Effects (Medium Priority) 🎨 ← NEXT!

**Status:** 0/5 Features | Ready to implement in Session 161+

**Implementation Pattern:** Follow same pattern as Phase 1 (backend view → URL route → GPT tool → tool handler)

#### 6. **Fade In/Out** ⭐⭐
**Natural Language:** "Add fade in to video 1"
**Complexity:** ⭐⭐ (2 hours)
**Method:** ffmpeg fade filter

#### 7. **Crop/Resize**
**Natural Language:** "Crop video 1 to square format"
**Complexity:** ⭐⭐ (2 hours)
**Method:** ffmpeg crop filter

#### 8. **Rotate/Flip**
**Natural Language:** "Rotate video 90 degrees"
**Complexity:** ⭐ (1 hour)
**Method:** ffmpeg transpose

#### 9. **Picture-in-Picture**
**Natural Language:** "Add video 2 as small overlay on video 1"
**Complexity:** ⭐⭐⭐ (4 hours)
**Method:** ffmpeg overlay filter

#### 10. **Audio Controls**
**Natural Language:** "Increase volume of video 1 by 50%"
**Complexity:** ⭐⭐ (2-3 hours)
**Method:** ffmpeg audio filters

---

### Phase 3: DaVinci Resolve Professional (Advanced) 🎬

#### 11. **Advanced Transitions** (DaVinci!)
**Use Cases:** Smooth cuts between scenes
**Natural Language:** "Add crossfade between video 1 and 2"
**Complexity:** ⭐⭐⭐⭐ (6-8 hours)
**Method:** DaVinci Resolve Python API

#### 12. **Multi-Track Timeline** (DaVinci!)
**Use Cases:** Complex edits, B-roll, overlays
**Natural Language:** "Create timeline with video 1 as main, video 2 as B-roll"
**Complexity:** ⭐⭐⭐⭐⭐ (10+ hours)
**Method:** DaVinci Resolve Python API

#### 13. **Advanced Text Animations** (DaVinci!)
**Use Cases:** Professional titles, credits
**Natural Language:** "Add animated title with bounce effect"
**Complexity:** ⭐⭐⭐⭐ (8 hours)
**Method:** DaVinci Resolve Fusion

---

## 🛠️ Step-by-Step: Adding a New Video Feature

### Example: Let's Add "Video Reverse" Feature

#### Step 1: Create the Backend Function

**File:** `core/views_video.py`

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reverse_video(request):
    """
    Reverse a video (play backwards)
    Session 159: Video Reverse Feature

    POST /api/video/reverse/
    Body: {
        "video_id": "123 or UUID",
        "reverse_audio": true
    }
    """
    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        reverse_audio = data.get('reverse_audio', True)
        project_id = data.get('project_id')  # For project association

        # Get video
        try:
            if video_id.isdigit():
                video = VideoHistory.objects.filter(
                    user=request.user
                ).order_by('-created_at')[int(video_id)]
            else:
                video = VideoHistory.objects.get(id=video_id, user=request.user)
        except (VideoHistory.DoesNotExist, IndexError):
            return JsonResponse({
                'success': False,
                'error': f'Video {video_id} not found'
            }, status=404)

        # Get video file path
        video_path = video.video_file.path

        # Create output filename
        output_filename = f"reversed_{video.id}.mp4"
        output_path = os.path.join('/tmp', output_filename)

        # Build ffmpeg command
        if reverse_audio:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', 'reverse',
                '-af', 'areverse',
                '-y', output_path
            ]
        else:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', 'reverse',
                '-an',  # Remove audio
                '-y', output_path
            ]

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"ffmpeg error: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': 'Video reverse failed'
            }, status=500)

        # Save to Django storage
        with open(output_path, 'rb') as f:
            file_path = default_storage.save(
                f'videos/{output_filename}',
                ContentFile(f.read())
            )

        # Create VideoHistory record
        new_video = VideoHistory.objects.create(
            user=request.user,
            prompt=f"Reversed version of video {video_id}",
            video_file=file_path,
            video_url=request.build_absolute_uri(default_storage.url(file_path)),
            status='completed',
            model_used='ffmpeg-reverse',
            project_id=project_id  # Associate with project!
        )

        # Cleanup temp file
        os.remove(output_path)

        return JsonResponse({
            'success': True,
            'message': f'Video reversed successfully! {"(with audio)" if reverse_audio else "(silent)"}',
            'video_id': str(new_video.id),
            'video_url': new_video.video_url,
            'agent': 'VideoEditingAgent',
            'operation': 'reverse',
            'operation_display': f"Reversing video {'with audio' if reverse_audio else '(silent)'}"
        })

    except Exception as e:
        logger.error(f"Video reverse error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

#### Step 2: Add URL Route

**File:** `core/urls.py`

Find the video URL section (around line 870) and add:

```python
# Session 159: Video Reverse
path('api/video/reverse/', reverse_video, name='video-reverse'),
```

#### Step 3: Import the Function

At the top of `core/urls.py`, add to the video imports:

```python
from core.views_video import (
    # ... existing imports ...
    reverse_video  # Add this
)
```

#### Step 4: Add GPT Tool Definition

**File:** `core/personal_ai_assistant_enhanced.py`

Find the video_editing_agent tool definition (around line 241) and update:

```python
{
    "type": "function",
    "function": {
        "name": "video_editing_agent",
        "description": "...",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation: 'add_text_overlay' | 'apply_color_grading' | 'upscale' | 'apply_effect' | 'reverse'",
                    "enum": ["add_text_overlay", "apply_color_grading", "upscale", "apply_effect", "reverse"]
                },
                "parameters": {
                    "type": "object",
                    "description": "... For reverse: {reverse_audio: true}.",
                    "additionalProperties": true
                }
            },
            "required": ["video_id", "operation"]
        }
    }
}
```

#### Step 5: Add Tool Handler

**File:** `core/personal_ai_assistant_enhanced.py`

Find the execute_tool() function (around line 815) and add:

```python
elif operation == 'reverse':
    return self._tool_reverse_video(tool_args)
```

Then add the handler method (around line 1800):

```python
def _tool_reverse_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the reverse_video tool - Session 159."""
    try:
        from django.test import RequestFactory
        import json

        video_id = arguments.get('video_id')
        params = arguments.get('parameters', {})
        reverse_audio = params.get('reverse_audio', True)

        # Create request
        factory = RequestFactory()
        request_data = {
            'video_id': video_id,
            'reverse_audio': reverse_audio,
            'project_id': getattr(self, 'project_id', None)
        }

        request = factory.post('/api/video/reverse/',
                               data=json.dumps(request_data),
                               content_type='application/json')
        request.user = self.user

        # Call backend
        from core.views_video import reverse_video
        response = reverse_video(request)
        result = json.loads(response.content)

        if result.get('success'):
            return {
                'success': True,
                'message': result.get('message', 'Video reversed!'),
                'video_id': result.get('video_id'),
                'video_url': result.get('video_url')
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Video reverse failed')
            }

    except Exception as e:
        logger.error(f"Tool reverse_video error: {str(e)}")
        return {
            'success': False,
            'error': f"Failed to reverse video: {str(e)}"
        }
```

#### Step 6: Test It!

```bash
# Start Django
make start

# In AI Assistant chat (inside a project):
"Reverse video 1"
"Play video 5 backwards"
"Reverse video 3 with audio"
```

**Expected Result:**
- New video created (reversed)
- Appears in project gallery
- Playable in browser

---

## 📝 Implementation Checklist Template

When adding a new video feature, follow this checklist:

```
Feature: ___________________________

□ Step 1: Create backend view function in core/views_video.py
  □ Handle video_id (number or UUID)
  □ Execute ffmpeg or DaVinci operation
  □ Save result to storage
  □ Create VideoHistory record
  □ Include project_id for association
  □ Return success/error JSON

□ Step 2: Add URL route in core/urls.py
  □ Add path() in urlpatterns
  □ Import function at top

□ Step 3: Update GPT tool definition
  □ Add operation to enum
  □ Document parameters
  □ Add natural language examples

□ Step 4: Add tool handler
  □ elif operation == 'new_op' in execute_tool()
  □ Create _tool_new_operation() method
  □ Use RequestFactory pattern
  □ Handle errors gracefully

□ Step 5: Test
  □ Manual API test (curl or Postman)
  □ Natural language test via AI Assistant
  □ Verify project association
  □ Check video plays correctly

□ Step 6: Document
  □ Add to DAVINCI_EXPANSION_HANDOFF.md
  □ Update ACTUAL_WORKING_FEATURES.md
  □ Create session doc if major feature
```

---

## 🎯 Recommended Build Order (Session 159)

**My recommendation: Build these 5 features in this order:**

1. **Frame Extraction** (1 hour) - Easiest, very useful
2. **Video Reverse** (1-2 hours) - Fun, straightforward
3. **Video Trimming** (2 hours) - Highly requested feature
4. **Speed Control** (2-3 hours) - Cool effects
5. **Video Concatenation** (2 hours) - Leverage existing code

**Total Time:** 8-10 hours for 5 powerful features!
**User Value:** Massive! Professional video editing through conversation!

---

## 💡 Pro Tips

### FFmpeg Performance:
- Use `-c copy` when possible (fast, no re-encoding)
- For filters: use `-preset ultrafast` for speed
- Test on small videos first

### DaVinci Resolve Tips:
- Keep Resolve running while developing
- Check logs in `resolve_node/logs/`
- Use mock mode for API testing

### Error Handling:
- Always check video exists before processing
- Validate video format (MP4 preferred)
- Handle missing audio tracks
- Clean up temp files

### Testing:
- Create test videos: 5-10 seconds
- Test with/without audio
- Test different resolutions
- Test batch operations

---

## 📚 Reference Documentation

- **Session 103:** `/docs/SESSION_103_RESOLVE_NODE.md` - Render node setup
- **Session 128:** `/docs/SESSION_128_DAVINCI_VIDEO_EDITING.md` - Text overlay & color grading
- **Session 154:** Session notes for ffmpeg video enhancement
- **API Docs:** `/docs/apis/DAVINCI_RESOLVE_FFMPEG.md` - Complete API reference

---

## 🚀 Let's Build!

**Your DaVinci Resolve Studio is ready. The render node is operational. You have the patterns.**

**Pick your first feature and let's implement it! I recommend starting with Frame Extraction - it's the easiest and most satisfying!**

**Ready to add your first feature? Let me know which one excites you most! 🎬✨**
