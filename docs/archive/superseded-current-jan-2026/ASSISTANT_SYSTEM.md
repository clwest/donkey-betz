<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Personal Assistant architecture snapshot
>
> **Where to look now:**
> - [docs/topics/personal-assistant.md](/docs/topics/personal-assistant.md)
> - [docs/PERSONAL_ASSISTANT_ARCHITECTURE.md](/docs/PERSONAL_ASSISTANT_ARCHITECTURE.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Assistant System Documentation

**Location:** `core/assistant/`
**Total Files:** 8
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [File Reference](#file-reference)
4. [Tool Definitions](#tool-definitions)
5. [Mixins](#mixins)
6. [Usage](#usage)
7. [Request Flow](#request-flow)

---

## Overview

The Assistant System is the GPT-5.1 interface layer that coordinates 81 tools/agents for AI-powered content creation, research, orchestration, and ML Pipeline management. It uses a mixin architecture for clean separation of concerns.

### Package Structure

```
core/assistant/
├── __init__.py          # Package init & exports
├── base.py              # EnhancedPersonalAIAssistant class
├── tool_definitions.py  # GPT-5.1 tool schemas (21 tools)
├── constants.py         # Configuration values
├── utils.py             # ID resolution & parsing utilities
├── image_tools.py       # Image editing mixin
├── video_tools.py       # Video generation & editing mixins
└── audio_tools.py       # Audio generation mixin
```

---

## Architecture

### Request Flow

```
GPT-5.1 Response API
        ↓
  Tool Call (JSON)
        ↓
EnhancedPersonalAIAssistant.process_message()
        ↓
_execute_tool_call() - Parse tool call
        ↓
_route_tool_call() - Route to handler
        ↓
Handler Methods (_handle_*_agent)
        ↓
Mixin Methods (_tool_*) - Specific operations
        ↓
Agent Classes (ImageAgent, VideoAgent, etc.)
        ↓
External APIs (Stability AI, Runway ML, ElevenLabs)
```

### Mixin Inheritance

```python
class EnhancedPersonalAIAssistant(
    ImageToolsMixin,
    AudioToolsMixin,
    VideoGenerationToolsMixin,
    VideoEditingToolsMixin,
    PersonalAIAssistant  # Base class
):
    pass
```

---

## File Reference

### `__init__.py`

Package initialization and public API exposure.

```python
from core.personal_ai_assistant import PersonalAIAssistant
from .base import EnhancedPersonalAIAssistant
```

### `base.py`

Core `EnhancedPersonalAIAssistant` class that coordinates all tools.

**Key Attributes:**
```python
system_access_enabled: bool
database_queries_executed: list
llm_enforcer: LLMEnforcer
memory_manager: unified memory management
agent_registry: agent orchestration
advisor_registry: advisor access
recently_generated_assets: {images: [], videos: [], timestamps: {}}
_current_context: tool execution context
_last_tool_result: result caching
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `__init__(user)` | Initialize with Django user |
| `get_tool_definitions()` | Returns 21 GPT-5.1 tool schemas |
| `_execute_tool_call(tool_call)` | Main tool execution dispatcher |
| `_route_tool_call(name, args)` | Routes to specific handlers |
| `_handle_image_generation_agent()` | Image generation |
| `_handle_video_generation_agent()` | Video generation |
| `_handle_audio_generation_agent()` | Audio generation |
| `_handle_coleadership_agent()` | Multi-agent decisions |

### `tool_definitions.py`

GPT-5.1 Responses API function calling schemas.

**Function:** `get_tool_definitions() → List[dict]`

Returns 21 tool definitions organized by category (see [Tool Definitions](#tool-definitions) below).

### `constants.py`

Centralized configuration values.

```python
# Operations
IMAGE_EDITING_OPERATIONS = 6 types
VIDEO_GENERATION_OPERATIONS = 5 types
AUDIO_GENERATION_OPERATIONS = 2 types
VIDEO_EDITING_ALL_OPERATIONS = 20+ types

# Voice options
ELEVENLABS_VOICES = ['Rachel', 'Antoni', 'Bella', ...]  # 12 voices

# Quality presets
IMAGE_QUALITY_PRESETS = {'fast', 'balanced', 'high', 'premium'}

# Defaults
DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 1024
DEFAULT_VIDEO_DURATION = 5
DEFAULT_VOICE = 'Rachel'
DEFAULT_QUALITY = 'balanced'
DEFAULT_LORA_SCALE = 0.8

# Limits
CONVERSATION_HISTORY_LIMIT = 20
MEMORY_RETRIEVAL_LIMIT = 10

# Workflow types
WORKFLOW_TYPES = 13 types
```

### `utils.py`

Utility functions for ID resolution and range parsing.

| Function | Purpose |
|----------|---------|
| `resolve_hybrid_image_id(id, user)` | Convert sequential number to UUID |
| `resolve_hybrid_video_id(id, user)` | Convert sequential number to UUID |
| `parse_id_range(id_str)` | Parse `"20-25"` → `["20","21",...,"25"]` |
| `is_batch_operation(id_str)` | Detect batch (range/list) |
| `format_batch_result(...)` | Standardize batch results |
| `safe_json_loads(str, default)` | Safe JSON parsing |

**Batch ID Format Support:**
- Single: `"5"` or full UUID
- Range: `"20-25"`
- List: `"5, 8, 12"`
- Combined: `"10-15, 20, 25-27"`

---

## Tool Definitions

### Core Tools Organized by Category (25 documented below, 81 total)

#### Creation Tools (6)

| Tool | Purpose |
|------|---------|
| `image_generation_agent` | Text-to-image (Stability AI or trained LoRA) |
| `image_editing_agent` | Upscale, variations, remove bg, recolor, search_replace |
| `video_generation_agent` | Generate, animate, extend, chain, lip_sync |
| `audio_generation_agent` | TTS (generate_voice, add_voiceover) |
| `three_d_generation_agent` | Image to 3D model conversion |
| `video_editing_agent` | 30+ video editing operations |

#### Creative Tools (5)

| Tool | Purpose |
|------|---------|
| `character_training_agent` | LoRA character model training |
| `coleadership_agent` | Multi-agent decisions (CTO, COO, Creative Director) |
| `talking_character_agent` | Complete pipeline: TTS + video + lip sync |
| `create_brand_video` | Brand video creation |
| `workflow_orchestration_agent` | Multi-step creative workflows |

#### Research Tools (5)

| Tool | Purpose |
|------|---------|
| `competitor_analysis_agent` | Market research |
| `customer_research_agent` | Customer persona research |
| `brand_strategy_agent` | Brand strategy development |
| `content_strategy_agent` | Content strategy planning |
| `marketing_strategy_agent` | Marketing plan creation |

#### Specialized Tools (5)

| Tool | Purpose |
|------|---------|
| `legal_doc_drafter_agent` | Colorado family law assistance |
| `content_writer_agent` | Blog posts, scripts, articles |
| `web_search` | Web search integration |
| `create_project_from_research` | Project creation from research |
| `strategic_review` | Research analysis |

#### ML Pipeline Tools (4) - Session 673

| Tool | Purpose |
|------|---------|
| `opportunity_manager_tool` | Query, filter, search opportunities from ML Pipeline |
| `task_manager_tool` | Manage OpportunityTask lifecycle (accept, apply, complete) |
| `pipeline_orchestrator_tool` | Manual pipeline execution, status, queue |
| `revenue_tracker_tool` | Log revenue, track ML prediction accuracy |

#### Universal Agent Tool (1) - Session 674

| Tool | Purpose |
|------|---------|
| `universal_agent_tool` | Invoke ANY of 69 routable agents by name - blockchain, stocks, development, podcast, markets, narrative, etc. |

This single tool connects the PA (brain) to ALL 42 previously unreachable agents (organs).

---

## Mixins

### `image_tools.py` - ImageToolsMixin

Image editing operations, all delegating to unified `ImageAgent`.

| Method | Operation |
|--------|-----------|
| `_tool_upscale_image()` | Upscale resolution |
| `_tool_remove_background()` | Remove background |
| `_tool_create_variations()` | Generate variations |
| `_tool_recolor_image()` | Change colors |
| `_tool_search_and_replace()` | Object replacement |
| `_tool_creative_upscale()` | AI-enhanced upscale |
| `_tool_erase_object()` | Object removal |
| `_tool_refine_image()` | Image refinement |

### `video_tools.py` - VideoGenerationToolsMixin

Video generation via Runway ML.

| Method | Operation |
|--------|-----------|
| `_tool_generate_video()` | Text-to-video or image-to-video |
| `_tool_extend_video()` | Extend duration |
| `_tool_animate_image()` | Image to video with motion |
| `_tool_chain_videos()` | Combine multiple videos |
| `_tool_lip_sync()` | Sync lips to audio |
| `_tool_talking_character()` | Complete talking character pipeline |

### `video_tools.py` - VideoEditingToolsMixin

Video editing operations.

| Method | Operation |
|--------|-----------|
| `_tool_extract_video_frame()` | Extract frame at timestamp |
| `_tool_reverse_video()` | Play backwards |
| `_tool_trim_video()` | Trim to time range |
| `_tool_change_video_speed()` | Speed change (0.25-4.0x) |
| `_tool_concatenate_videos()` | Combine 2+ videos |
| `_tool_rotate_flip_video()` | Rotate or flip |
| `_tool_fade_video()` | Fade in/out |
| `_tool_crop_resize_video()` | Crop or aspect ratio change |
| `_tool_audio_controls()` | Volume, mute, extract |
| `_tool_picture_in_picture()` | Video overlay |
| `_tool_add_watermark()` | Add logo/watermark |
| `_tool_blur_region()` | Blur for privacy |

### `audio_tools.py` - AudioToolsMixin

Audio generation via ElevenLabs.

| Method | Operation |
|--------|-----------|
| `_handle_audio_generation_agent()` | Router for audio ops |
| `_tool_generate_voice()` | Text-to-speech |
| `_tool_add_voiceover()` | Add narration to video |

**Voice Options (12):**
Rachel, Antoni, Daniel, Emily, Bella, George, Clyde, Dave, Dorothy, James, Grace, Sarah

---

## Usage

### Initializing the Assistant

```python
from core.assistant import EnhancedPersonalAIAssistant

# Create assistant for user
assistant = EnhancedPersonalAIAssistant(user=request.user)

# Get tool definitions for GPT-5.1
tools = assistant.get_tool_definitions()

# Process a message
response = await assistant.process_message(
    message="Create a cyberpunk logo",
    conversation_history=[]
)
```

### Batch Operations

```python
# Edit images 20-25
result = assistant._handle_image_editing_agent({
    'image_id': '20-25',
    'operation': 'upscale'
})

# Returns aggregated results
{
    'success': True,
    'batch': True,
    'total': 6,
    'successes': 6,
    'failures': 0,
    'results': [...]
}
```

### Complex Pipeline (Talking Character)

```python
result = assistant._tool_talking_character({
    'image_id': '5',
    'text': 'Hello, welcome to my channel!',
    'voice': 'Rachel',
    'duration': 5,
    'motion_prompt': 'subtle talking motion',
    'sync_mode': 'loop',
    'temperature': 0.5
})

# Pipeline: TTS → Image-to-Video → Lip Sync
```

---

## Request Flow

### Tool Handler Pattern

All tool handlers follow a consistent structure:

```python
def _tool_operation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("TOOL CALLED!")
    try:
        # 1. Extract arguments
        param = arguments['required_param']
        optional = arguments.get('optional', default)

        # 2. Get project context
        current_project = getattr(self, 'project', None)

        # 3. Delegate to Agent
        agent = SpecializedAgent(
            user=self.user,
            project_id=current_project.id if current_project else None
        )

        result = agent.execute(...)

        # 4. Return standardized result
        return {'success': True, 'message': '...', 'data': result}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {'success': False, 'error': str(e)}
```

### Data Flow Example

**Talking Character Video:**

```
Input: {image_id: '5', text: 'Hello!', voice: 'Rachel'}
  ↓
utils.resolve_hybrid_image_id('5', user) → UUID
  ↓
Get image URL from ImageHistory
  ↓
TalkingCharacterPipeline.generate_talking_video_async():
  1. Generate audio via ElevenLabs TTS (~$0.015)
  2. Create video via Runway (~$0.50)
  3. Sync lips via latentsync (~$0.10)
  ↓
Return: {success: True, status: 'generating', estimated_cost: $0.665}
```

---

## External Integrations

| Service | Purpose |
|---------|---------|
| **Stability AI** | Image generation (CORE, SDXL, SD3, ULTRA) |
| **Runway ML** | Video generation (Gen-4 Turbo) |
| **ElevenLabs** | Text-to-speech (12 voices) |
| **Replicate** | Lip sync (latentsync, sync_labs) |
| **OpenAI** | GPT-5.1 function calling |

---

## Performance Characteristics

| Operation | Time |
|-----------|------|
| Image generation | 30-120s |
| Video generation | 60-180s |
| Audio TTS | 5-15s |
| Lip sync | 30-60s |
| Batch operations | Sequential |

---

## Session History

| Session | Change |
|---------|--------|
| 184 | Refactored 6,905-line file into modules |
| 186 | Extracted audio tools |
| 202 | Updated to unified ImageAgent |
| 266 | Moved descriptions to central registry |
| 293 | Added 5 business research agents |
| 403 | Added legal document drafter |
| 496 | Added content writer agent |

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agent details
- [SERVICES.md](SERVICES.md) - Backend services
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - REST endpoints
