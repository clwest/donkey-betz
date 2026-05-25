<!-- DOC-POINTER-V2 (Session 1143) -->
> **Status:** Deprecated
> **Originally:** Session 84 (Nov 13 2025) — DaVinci Resolve agent-based architecture design
> **Last verified:** Session 1143 (2026-05-25)
> **Change reason:** **DaVinci Resolve integration sunset by Chris in Session 1143** following abandoned-features audit (PR #2191). The agent-based architecture was designed but the underlying DaVinci integration never reached active usage. Do not implement.
> **Preserved because:** historical design record.

# 🎬 Session 84: DaVinci Resolve Agent-Based Video Editing Architecture

**Date:** November 13, 2025
**Status:** DEPRECATED (Session 1143) — design preserved but integration sunset
**Goal:** Build comprehensive Agent-powered DaVinci Resolve video editing workflow

---

## 📊 Current State Audit

### Available Resources:
- ✅ **39 videos in database** (excellent testing material!)
- ✅ **5 video files on disk** (ready to use)
- ✅ **DaVinci Resolve Studio activated** ($295 investment)
- ✅ **DaVinci Provider complete** (10+ methods implemented)
- ✅ **VideoAgent exists** (needs DaVinci enhancement)
- ✅ **3 AI Assistant tools** (chain, text, music)

### DaVinci Provider Capabilities:
```python
# Project Management
- create_project(project_name: str)
- close_project()
- render_project() → DaVinciRenderResult

# Media Import
- import_video(video_path: str)
- _download_media(url_or_path: str, media_type: str)

# Timeline Operations
- add_clip_to_timeline(video_path, position, duration)
- add_transition(transition_type, at_second, duration)
- add_text_overlay(text, position, start_second, duration, font_size)
- add_audio(audio_path, volume, start_second)
- add_music_to_video(video_path, audio_path, audio_volume) → mixed video
- apply_color_grading(style, intensity)

# Helpers
- _get_timeline_duration() → float
```

### Existing AI Assistant Tools:
1. **chain_videos** (Session 71)
   - Chains multiple videos with transitions
   - Parameters: video_count, transition_type, project_name

2. **add_text_to_video** (Session 72)
   - Adds text overlays with perfect spelling
   - Parameters: text, position, start_second, duration, font_size

3. **add_music_to_video** (Session 72/81)
   - Adds background music or voiceover
   - Parameters: video_selection, audio_url, audio_volume

---

## 🎯 Design Goals

### Primary Objective:
**Create an Agent-based workflow where users can edit videos using natural language commands through the VideoAgent + DaVinci Resolve API**

### User Experience Vision:
```
User: "Take my last 3 videos, add the text 'Mountain Adventures'
       at the start, apply cinematic color grading, and add music"

VideoAgent:
  1. Fetches last 3 videos from gallery
  2. Creates DaVinci project "Mountain Adventures Edit"
  3. Chains videos with Cross Dissolve transitions
  4. Adds text overlay "Mountain Adventures" at 0s for 3s
  5. Applies cinematic color grading (teal/orange LUT)
  6. Queries AudioAgent for recent music/generates music
  7. Mixes audio at 30% volume
  8. Renders final video
  9. Returns: 24-second professional video with all edits applied

Result: User gets publication-ready video in 60 seconds!
```

---

## 🏗️ Architecture Design

### Component 1: VideoAgent DaVinci Orchestrator

**New Methods:**

```python
class VideoAgent:
    """Enhanced with DaVinci Resolve orchestration"""

    def create_edited_video(
        self,
        video_ids: List[str],
        operations: List[Dict[str, Any]],
        project_name: str = None
    ) -> Dict[str, Any]:
        """
        Orchestrate multiple DaVinci operations on selected videos.

        Args:
            video_ids: List of video IDs from database
            operations: List of editing operations to perform
            project_name: Optional project name

        Operations format:
            [
                {'type': 'chain', 'transition': 'Cross Dissolve', 'duration': 1.0},
                {'type': 'text', 'text': 'Hello', 'position': 'center', 'start': 0, 'duration': 3},
                {'type': 'color_grade', 'style': 'cinematic', 'intensity': 0.7},
                {'type': 'audio', 'audio_url': 'url', 'volume': 0.3}
            ]

        Returns:
            {
                'success': True,
                'video_id': 'new_video_id',
                'video_url': 'url',
                'operations_applied': 4,
                'duration': 24.0,
                'message': 'Video edited successfully!'
            }
        """
        pass

    def add_text_overlay_davinci(
        self,
        video_id: str,
        text: str,
        position: str = 'center',
        start_second: float = 0,
        duration: float = 3,
        font_size: int = 72
    ) -> Dict[str, Any]:
        """
        Add text overlay to a single video using DaVinci.
        Simpler than full orchestration - for single operations.
        """
        pass

    def apply_color_grade_davinci(
        self,
        video_id: str,
        style: str = 'cinematic',
        intensity: float = 0.5
    ) -> Dict[str, Any]:
        """
        Apply color grading to a video using DaVinci.

        Args:
            video_id: Video to grade
            style: 'cinematic' | 'vibrant' | 'vintage' | 'noir' | 'warm' | 'cool'
            intensity: 0.0-1.0 (how strong the grade is)
        """
        pass

    def chain_videos_davinci(
        self,
        video_ids: List[str],
        transition_type: str = 'Cross Dissolve',
        transition_duration: float = 1.0,
        add_transitions: bool = True
    ) -> Dict[str, Any]:
        """
        Chain multiple videos together using DaVinci.
        """
        pass
```

### Component 2: AI Assistant Enhanced Tools

**New AI Assistant Tools:**

```python
# 1. Enhanced edit_video tool (master orchestrator)
{
    "name": "edit_video",
    "description": "Perform multiple editing operations on videos using DaVinci Resolve",
    "parameters": {
        "video_selection": {
            "type": "string",
            "enum": ["last", "last_2", "last_3", "specify_ids"],
            "description": "Which videos to edit"
        },
        "operations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"enum": ["text", "color_grade", "audio", "chain"]},
                    # ... operation-specific parameters
                }
            },
            "description": "List of editing operations to perform in sequence"
        },
        "project_name": {
            "type": "string",
            "description": "Name for the DaVinci project"
        }
    }
}

# 2. apply_color_grade tool
{
    "name": "apply_color_grade",
    "description": "Apply professional color grading to a video",
    "parameters": {
        "video_selection": {"type": "string", "default": "last"},
        "style": {
            "type": "string",
            "enum": ["cinematic", "vibrant", "vintage", "noir", "warm", "cool"],
            "description": "Color grading style"
        },
        "intensity": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "default": 0.5,
            "description": "How strong the color grade is"
        }
    }
}

# 3. Enhanced chain_videos (already exists, but update)
# - Add transition_duration parameter
# - Add transition_type options: Cross Dissolve, Fade, Wipe, Slide

# 4. Enhanced add_text_to_video (already exists, but update)
# - Add font_family parameter
# - Add text_color parameter
# - Add animation options: fade_in, fade_out, slide_in
```

### Component 3: System Prompt Enhancement

**Add to AI Assistant system prompt:**

```markdown
## Video Editing Operations (DaVinci Resolve)

You can perform professional video editing operations using DaVinci Resolve:

1. **Text Overlays**
   - User: "Add the text 'Welcome' to my video"
   - Tool: add_text_to_video(text="Welcome", position="center", start_second=0, duration=3)

2. **Color Grading**
   - User: "Make my video look cinematic"
   - Tool: apply_color_grade(video_selection="last", style="cinematic", intensity=0.7)

3. **Video Chaining**
   - User: "Chain my last 3 videos together"
   - Tool: chain_videos(video_count=3, transition_type="Cross Dissolve")

4. **Complex Edits**
   - User: "Edit my last video: add title, color grade, and music"
   - Tool: edit_video(operations=[
       {"type": "text", "text": "Mountain Adventures", ...},
       {"type": "color_grade", "style": "cinematic"},
       {"type": "audio", "audio_url": "..."}
     ])

**Natural Language Parsing:**
- "cinematic look" → apply_color_grade(style="cinematic")
- "add music" → check AudioAgent for recent audio → add_music_to_video()
- "add title" → add_text_to_video(position="center", duration=3)
- "chain videos" → chain_videos()
- "make it warmer" → apply_color_grade(style="warm")
```

---

## 🔄 Workflow Examples

### Example 1: Simple Text Overlay
```
User: "Add the text 'Ocean Waves' to my last video"

AI Assistant:
  → Calls: add_text_to_video(text="Ocean Waves", video_selection="last")

VideoAgent:
  1. Fetches last completed video
  2. Creates DaVinci project "Text Overlay - Ocean Waves"
  3. Imports video to timeline
  4. Adds text overlay "Ocean Waves" at center for 3 seconds
  5. Renders final video
  6. Saves to VideoHistory with video_type='text_overlay'

Result: New video with text overlay in 15-20 seconds
```

### Example 2: Color Grading
```
User: "Make my snowboard video look cinematic"

AI Assistant:
  → Calls: apply_color_grade(video_selection="last", style="cinematic", intensity=0.7)

VideoAgent:
  1. Fetches last video (snowboard)
  2. Creates DaVinci project "Color Grade - Cinematic"
  3. Imports video
  4. Applies cinematic LUT (teal/orange color science)
  5. Renders with color grade
  6. Saves to VideoHistory with video_type='color_graded'

Result: Cinematic-looking video in 20-30 seconds
```

### Example 3: Multi-Operation Edit (Complex)
```
User: "Take my last 3 videos, chain them, add the title
       'Mountain Adventures 2025' at the start, apply warm
       color grading, and add that music I generated"

AI Assistant:
  → Queries AudioAgent for recent audio
  → Calls: edit_video(
      video_selection="last_3",
      operations=[
        {"type": "chain", "transition": "Cross Dissolve", "duration": 1.0},
        {"type": "text", "text": "Mountain Adventures 2025", "start": 0, "duration": 3},
        {"type": "color_grade", "style": "warm", "intensity": 0.6},
        {"type": "audio", "audio_url": "[retrieved from AudioAgent]", "volume": 0.3}
      ],
      project_name="Mountain Adventures 2025"
    )

VideoAgent:
  1. Fetches last 3 completed videos
  2. Creates DaVinci project "Mountain Adventures 2025"
  3. Imports all 3 videos to timeline
  4. Adds Cross Dissolve transitions between clips (2 transitions)
  5. Adds text overlay "Mountain Adventures 2025" at 0s for 3s
  6. Applies warm color grading (golden hour look)
  7. Mixes audio from AudioAgent at 30% volume
  8. Renders final video (estimated 24 seconds)
  9. Saves to VideoHistory with video_type='multi_edit'

Result: Publication-ready video in 45-60 seconds
```

### Example 4: Quick Enhancement
```
User: "Make my last video look more vibrant"

AI Assistant:
  → Calls: apply_color_grade(style="vibrant", intensity=0.8)

VideoAgent:
  1. Fetches last video
  2. Applies vibrant color grade (boosted saturation + contrast)
  3. Renders enhanced video

Result: Enhanced video in 15 seconds
```

---

## 📝 Implementation Plan

### Phase 1: VideoAgent Enhancement (30 min)
1. Add `create_edited_video()` orchestrator method
2. Add `add_text_overlay_davinci()` simple method
3. Add `apply_color_grade_davinci()` simple method
4. Add `chain_videos_davinci()` simple method
5. Add error handling and state management

### Phase 2: AI Assistant Tools (30 min)
1. Create `_execute_edit_video()` function (master orchestrator)
2. Create `_execute_apply_color_grade()` function
3. Update `_execute_chain_videos()` with new parameters
4. Update `_execute_add_text_to_video()` with new parameters
5. Register all tools in GPT-5-mini function list

### Phase 3: System Prompt Enhancement (15 min)
1. Add video editing section to system prompt
2. Add natural language parsing examples
3. Add DaVinci operation descriptions
4. Add usage guidelines

### Phase 4: Testing (30 min)
1. Test simple text overlay on existing video
2. Test color grading on existing video
3. Test video chaining (3 videos)
4. Test complex multi-operation edit
5. Test error handling (invalid video ID, missing audio, etc.)

### Phase 5: Documentation (15 min)
1. Update CLAUDE.md with new features
2. Update ACTUAL_WORKING_FEATURES.md
3. Create SESSION_84_COMPLETE.md
4. Update 00-START-NEXT-SESSION.md

**Total Time:** ~2 hours

---

## 🎯 Success Criteria

**Minimum (MVP):**
- ✅ VideoAgent can add text overlays via DaVinci
- ✅ VideoAgent can apply color grading via DaVinci
- ✅ AI Assistant can call text and color grade tools
- ✅ Operations complete in <30 seconds
- ✅ Results saved to database correctly

**Complete (Full Feature):**
- ✅ All minimum criteria
- ✅ Multi-operation orchestration working
- ✅ Video chaining with transitions
- ✅ Audio integration working
- ✅ Natural language parsing accurate
- ✅ Error handling robust

**Polish (Ideal):**
- ✅ All complete criteria
- ✅ Progress feedback during rendering
- ✅ Preview of edits before rendering
- ✅ Undo/redo capability
- ✅ Save edit presets

---

## 🚀 Technical Advantages

### Why This Approach is Powerful:

1. **Agent-Based = Autonomous**
   - VideoAgent manages entire workflow
   - No manual clicking through UI
   - Complex operations become single commands

2. **DaVinci API = Professional Quality**
   - Perfect text rendering (no AI text artifacts)
   - Professional color grading tools
   - Real transitions and effects
   - Broadcast-quality output

3. **Natural Language = Easy UX**
   - "Make it cinematic" → professional color grade
   - "Add title" → perfectly rendered text
   - "Chain my videos" → seamless video editing

4. **Multi-Agent Coordination**
   - VideoAgent queries AudioAgent for music
   - Automatic workflow integration
   - Shared memory enables complex orchestrations

5. **Existing Videos = Immediate Value**
   - 39 videos ready to enhance
   - No new generation needed
   - Instant professional upgrades

---

## 📦 Deliverables

### Code:
1. **agents/video_agent.py** - Enhanced with DaVinci methods (~200 lines)
2. **core/views_image.py** - New AI Assistant tools (~400 lines)
3. **content/davinci_provider.py** - Minor enhancements if needed (~50 lines)

### Documentation:
1. **docs/SESSION_84_DAVINCI_AGENT_ARCHITECTURE.md** - This file
2. **docs/SESSION_84_COMPLETE.md** - Implementation results
3. **CLAUDE.md** - Updated with Session 84
4. **ACTUAL_WORKING_FEATURES.md** - Add DaVinci Agent features

### Testing:
1. Test script for each operation type
2. Integration test for multi-operation workflow
3. Error handling tests

---

## 💭 Future Enhancements

**After MVP is working:**

1. **Advanced Color Grading**
   - Custom LUT uploads
   - Color wheel adjustments
   - Shot-matching between clips

2. **Advanced Text**
   - Animated titles
   - Lower thirds with graphics
   - End credits crawl

3. **Advanced Transitions**
   - Custom transition timing
   - Effect parameters
   - Match cuts

4. **Audio Enhancement**
   - Multi-track mixing
   - Audio ducking (lower music when voice plays)
   - Fade in/out
   - EQ and compression

5. **Batch Operations**
   - Apply same edits to multiple videos
   - Template-based editing
   - Bulk color grading

6. **Collaboration**
   - Share edit projects
   - Review and approval workflow
   - Version control

---

## 🎬 Ready to Build!

**Next Step:** Implement Phase 1 - VideoAgent Enhancement

This architecture gives us:
- ✅ Clear implementation path
- ✅ Professional quality output
- ✅ Natural language interface
- ✅ Multi-agent coordination
- ✅ Immediate value (39 videos to enhance!)

**Let's build something amazing!** 🚀✨
