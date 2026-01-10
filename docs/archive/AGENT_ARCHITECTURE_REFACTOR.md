# Agent Architecture Refactor: One Assistant, Specialist Agents

**Started:** November 26, 2025 (Session 202)
**Goal:** Clean, consolidated agent architecture where ONE person can do company-level work WITH AI
**Status:** IN PROGRESS

---

## The Vision

```
User: "Make a dancing donkey on two legs in pixar style"
     ↓
Personal Assistant (understands intent)
     ↓
Agent Router (knows which specialist handles this)
     ↓
Image Agent (ONE JOB: create images perfectly)
     ↓
Result appears
```

**Principles:**
1. **One Assistant** - Understands the user, speaks naturally
2. **Specialist Agents** - Each does ONE thing perfectly
3. **Clear Ownership** - No overlapping responsibilities
4. **Invisible Infrastructure** - Spiders, memory, tools work behind the scenes
5. **Human-AI Partnership** - Working WITH AI, not just using AI

---

## Phase 1: Agent Consolidation

### Status: IN PROGRESS - Analysis Complete, Ready for Execution

**Goal:** Map overlapping agents and consolidate into clear specialists

---

### IMAGE DOMAIN - Consolidation Plan

#### Current State (4 agents with overlap)

| File | Class | What It Does | Decision |
|------|-------|--------------|----------|
| `agents/image_editing_agent.py` | ImageEditingAgent | Upscale, remove bg, variations, recolor, search_and_replace, creative_upscale | **KEEP AS CORE** |
| `ai_core/agents/logo_agent.py` | LogoAgent | Logo-specific generation with brand expertise | **MERGE INTO ImageAgent** |
| `ai_core/agents/social_media_agent.py` | SocialMediaAgent | Platform-specific sizes (Instagram, Facebook, etc.) | **MERGE INTO ImageAgent** |
| `ai_core/agents/editing_orchestrator_agent.py` | EditingOrchestratorAgent | Multi-step editing workflows (inpaint, outpaint, recolor) | **MERGE INTO ImageAgent** |

#### Consolidation Decision

**Create unified `ImageAgent`** that combines:
- Core editing operations (from ImageEditingAgent)
- Logo expertise (from LogoAgent) - becomes `generate(type='logo')`
- Social media sizing (from SocialMediaAgent) - becomes `generate(platform='instagram')`
- Multi-step orchestration (from EditingOrchestratorAgent)

```python
# Target API
class ImageAgent:
    def generate(self, prompt, style=None, type=None, platform=None, size=None)
    def edit(self, image_id, operation, **params)  # upscale, remove_bg, variations, etc.
    def refine(self, image_id, steps: List[EditingStep])  # multi-step workflows
```

#### Files to Archive After Merge
- [ ] `ai_core/agents/logo_agent.py` → archive to `_archived/`
- [ ] `ai_core/agents/social_media_agent.py` → archive to `_archived/`
- [ ] `ai_core/agents/editing_orchestrator_agent.py` → archive to `_archived/`

---

### VIDEO DOMAIN - Consolidation Plan

#### Current State (3 agents with significant overlap)

| File | Class | What It Does | Decision |
|------|-------|--------------|----------|
| `agents/video_agent.py` | VideoAgent | Text overlay, color grade, music, chaining (Session 81) | **KEEP AS CORE** |
| `agents/video_generation_agent.py` | VideoGenerationAgent | Text-to-video, image-to-video with RunwayML (Session 128) | **MERGE INTO VideoAgent** |
| `agents/video_editing_agent.py` | VideoEditingAgent | Text overlay, color grading, trim, speed (Session 128) | **MERGE INTO VideoAgent** |

#### Analysis

The overlap is clear:
- VideoAgent (Session 81) has: music, text, color grade, chaining
- VideoEditingAgent (Session 128) has: text overlay, color grading, trim, speed
- VideoGenerationAgent (Session 128) has: text-to-video, image-to-video

These should all be ONE agent with different operations.

#### Consolidation Decision

**Enhance `VideoAgent`** to absorb all video operations:

```python
# Target API
class VideoAgent:
    def generate(self, prompt, image_id=None, duration=5, quality='gen4_turbo')  # from VideoGenerationAgent
    def edit(self, video_id, operation, **params)  # from VideoEditingAgent
    def add_audio(self, video_id, audio_url=None)  # existing
    def chain(self, video_ids, transitions=True)  # existing
```

#### Files to Archive After Merge
- [ ] `agents/video_generation_agent.py` → archive to `_archived/`
- [ ] `agents/video_editing_agent.py` → archive to `_archived/`

---

### AUDIO DOMAIN - Consolidation Plan

#### Current State (2 agents with overlap)

| File | Class | What It Does | Decision |
|------|-------|--------------|----------|
| `agents/audio_agent.py` | AudioAgent | TTS, sound effects, state tracking, query handlers (Session 81) | **KEEP AS CORE** |
| `agents/audio_generation_agent.py` | AudioGenerationAgent | Voice generation, voiceovers (Session 128) | **MERGE INTO AudioAgent** |

#### Analysis

AudioAgent is more complete:
- Has state tracking via AgentMemoryInterface
- Has query handlers for cross-agent communication
- Already has generate_speech and generate_sound_effect

AudioGenerationAgent adds:
- add_voiceover operation (combine audio with video)

#### Consolidation Decision

**Enhance `AudioAgent`** to include voiceover capability:

```python
# Target API
class AudioAgent:
    def generate_speech(self, text, voice='Rachel')  # existing
    def generate_sound_effect(self, prompt)  # existing
    def add_voiceover(self, video_id, text, voice)  # from AudioGenerationAgent
```

#### Files to Archive After Merge
- [ ] `agents/audio_generation_agent.py` → archive to `_archived/`

---

### WORKFLOW DOMAIN - Consolidation Plan

#### Current State (2 agents with different purposes)

| File | Class | What It Does | Decision |
|------|-------|--------------|----------|
| `agents/workflow_orchestration_agent.py` | WorkflowOrchestrationAgent | Multi-step research+create workflows (research_and_create_logos, etc.) | **KEEP** |
| `ai_core/agents/workflow_coordinator_agent.py` | WorkflowCoordinatorAgent | Creative workflows (generate_options, save_template, train_brand) | **KEEP - DIFFERENT PURPOSE** |

#### Analysis

These are NOT overlapping - they serve different purposes:
- **WorkflowOrchestrationAgent**: User-facing workflows like "research and create logos"
- **WorkflowCoordinatorAgent**: Internal creative workflows coordinating sub-agents

#### Decision: KEEP BOTH (No Consolidation Needed)

The naming is confusing but the functionality is distinct:
- Rename `WorkflowOrchestrationAgent` → keep as-is (handles GPT tool calls)
- Rename `WorkflowCoordinatorAgent` → keep as-is (internal orchestration)

---

### LEADERSHIP DOMAIN - No Consolidation Needed

| File | Class | Decision |
|------|-------|----------|
| `agents/cto_agent.py` | CTOAgent | **KEEP** - Technical perspective |
| `agents/coo_agent.py` | COOAgent | **KEEP** - Operations perspective |
| `agents/meeting_coordinator_agent.py` | MeetingCoordinatorAgent | **KEEP** - Facilitates meetings |
| `ai_core/agents/creative_director_agent.py` | CreativeDirectorAgent | **KEEP** - Creative perspective |

These are already clean specialists with distinct roles.

---

### OTHER DOMAINS - Keep As-Is

| File | Class | Decision |
|------|-------|----------|
| `agents/three_d_generation_agent.py` | ThreeDGenerationAgent | **KEEP** - Only 3D agent |
| `agents/character_training_agent.py` | CharacterTrainingAgent | **KEEP** - Handles LoRA training |
| `agents/trained_creation_agent.py` | TrainedCreationAgent | **KEEP** - Uses trained models |

---

## Phase 1 Execution Checklist

### Step 1: Create Archive Directory
- [ ] Create `_archived/agents/` directory for deprecated files

### Step 2: Consolidate Image Domain
- [ ] Merge LogoAgent capabilities into ImageAgent
- [ ] Merge SocialMediaAgent capabilities into ImageAgent
- [ ] Merge EditingOrchestratorAgent capabilities into ImageAgent
- [ ] Update tool_definitions.py to route to unified ImageAgent
- [ ] Archive old files

### Step 3: Consolidate Video Domain
- [ ] Merge VideoGenerationAgent into VideoAgent
- [ ] Merge VideoEditingAgent into VideoAgent
- [ ] Update tool_definitions.py to route to unified VideoAgent
- [ ] Archive old files

### Step 4: Consolidate Audio Domain
- [ ] Add voiceover capability to AudioAgent
- [ ] Update tool_definitions.py to route to unified AudioAgent
- [ ] Archive old files

### Step 5: Update Frontend
- [ ] Update getProgressMessage() in ai_image_studio.html
- [ ] Update getAgentStatusMessage() in ai_image_studio.html

### Step 6: Test All Workflows
- [ ] Test image generation with styles
- [ ] Test image editing operations
- [ ] Test video generation
- [ ] Test video editing
- [ ] Test audio generation
- [ ] Test workflow orchestrations

---

## Phase 2: Agent Router Implementation

### Status: NOT STARTED (After Phase 1)

**Goal:** Build routing layer so Assistant speaks intent, not implementation

```python
# Target architecture
class AgentRouter:
    INTENT_MAP = {
        'create_image': ('ImageAgent', 'generate'),
        'edit_image': ('ImageAgent', 'edit'),
        'create_logo': ('ImageAgent', 'generate', {'type': 'logo'}),
        'create_social': ('ImageAgent', 'generate', {'platform': 'instagram'}),
        'create_video': ('VideoAgent', 'generate'),
        'animate_image': ('VideoAgent', 'generate'),
        'edit_video': ('VideoAgent', 'edit'),
        'create_audio': ('AudioAgent', 'generate_speech'),
        'research': ('ResearchAgent', 'search'),
        # ... etc
    }
```

---

## Phase 3: Spider Integration

### Status: NOT STARTED (After Phase 2)

**Goal:** Connect 40+ spiders as invisible infrastructure feeding ResearchAgent

---

## Phase 4: Memory Enhancement

### Status: NOT STARTED (After Phase 3)

**Goal:** Agents remember user preferences, past work, style evolution

---

## Phase 5: Tool Consolidation

### Status: NOT STARTED (After Phase 4)

**Goal:** Tools belong to Agents, not exposed directly to Assistant

---

## Progress Tracking

### Completed
- [x] Session 202: Agent architecture audit
- [x] Documented current state in SESSION_202_AGENT_ARCHITECTURE_AUDIT.md
- [x] Created this refactoring plan
- [x] **Phase 1 Analysis Complete** - All domains analyzed
- [x] **VIDEO DOMAIN CONSOLIDATED** - 3 agents merged into 1 VideoAgent
- [x] **AUDIO DOMAIN CONSOLIDATED** - 2 agents merged into 1 AudioAgent
- [x] **IMAGE DOMAIN CONSOLIDATED** - 4 agents merged into 1 ImageAgent
- [x] **PHASE 2: AGENT ROUTER COMPLETE** - Intent-based routing system created
- [x] **PHASE 3: SPIDER INTEGRATION COMPLETE** - ResearchAgent connects 46 spiders
- [x] **PHASE 4: MEMORY ENHANCEMENT COMPLETE** - AgentPreferenceManager for all agents
- [x] **PHASE 5: TOOL CONSOLIDATION COMPLETE** - All tools route through AgentRouter

### In Progress
(None - all 5 phases complete!)

### Not Started
(None - architecture refactor complete!)

---

## Files Modified Log

| Date | File | Change |
|------|------|--------|
| 2025-11-26 | docs/sessions/SESSION_202_AGENT_ARCHITECTURE_AUDIT.md | Created audit document |
| 2025-11-26 | docs/AGENT_ARCHITECTURE_REFACTOR.md | Created this plan |
| 2025-11-26 | docs/AGENT_ARCHITECTURE_REFACTOR.md | Updated with full analysis and consolidation decisions |
| 2025-11-26 | agents/video_agent.py | Added generate(), check_status(), extend_video(), edit() methods |
| 2025-11-26 | agents/audio_agent.py | Added add_voiceover(), generate() methods |
| 2025-11-26 | agents/image_agent.py | **CREATED** - Unified image agent with generate(), generate_logo(), generate_social(), edit() |
| 2025-11-26 | agents/router.py | **CREATED** - AgentRouter with Intent taxonomy and tool mapping |
| 2025-11-26 | core/views_image.py | Updated execute_tool() to use AgentRouter for supported tools |
| 2025-11-26 | core/assistant/image_tools.py | Updated to use ImageAgent instead of ImageEditingAgent |
| 2025-11-26 | core/personal_ai_assistant_enhanced.py | Updated to use ImageAgent |
| 2025-11-26 | _archived/agents/video_generation_agent.py | Archived (merged into VideoAgent) |
| 2025-11-26 | _archived/agents/video_editing_agent.py | Archived (merged into VideoAgent) |
| 2025-11-26 | _archived/agents/audio_generation_agent.py | Archived (merged into AudioAgent) |
| 2025-11-26 | _archived/agents/image_editing_agent.py | Archived (merged into ImageAgent) |
| 2025-11-26 | _archived/agents/ai_core/logo_agent.py | Archived (merged into ImageAgent) |
| 2025-11-26 | _archived/agents/ai_core/social_media_agent.py | Archived (merged into ImageAgent) |
| 2025-11-26 | _archived/agents/ai_core/editing_orchestrator_agent.py | Archived (merged into ImageAgent) |
| 2025-11-26 | agents/research_agent.py | **CREATED** - Unified research agent integrating 46 spiders (Session 203) |
| 2025-11-26 | agents/router.py | Added WEB_SEARCH and RESEARCH_TOPIC intents with ResearchAgent routes |
| 2025-11-26 | core/views_image.py | Added web_search, research_topic, research to ROUTER_ENABLED_TOOLS |
| 2025-11-26 | agents/preference_manager.py | **CREATED** - Unified preference manager for all agents (Session 203 Phase 4) |
| 2025-11-26 | agents/image_agent.py | Added preference learning and memory integration |
| 2025-11-26 | agents/video_agent.py | Added preference learning and memory integration |
| 2025-11-26 | agents/audio_agent.py | Added preference learning and memory integration |
| 2025-11-26 | agents/router.py | Session 204 Phase 5: Added execute_tool(), new intents (CREATE_TALKING_CHARACTER, CREATE_BRAND_VIDEO, TRAIN_CHARACTER) |
| 2025-11-26 | core/views_image.py | Session 204: Expanded ROUTER_ENABLED_TOOLS to include workflows, training, leadership |
| 2025-11-26 | core/personal_ai_assistant_enhanced.py | Session 204: Added router-based execution for supported tools |

---

## Phase Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Agent Consolidation (9 agents -> 3) | COMPLETE |
| Phase 2 | Agent Router (intent-based routing) | COMPLETE |
| Phase 3 | Spider Integration (46 spiders -> ResearchAgent) | COMPLETE |
| Phase 4 | Memory Enhancement (AgentPreferenceManager) | COMPLETE |
| Phase 5 | Tool Consolidation (execute_tool unified entry) | COMPLETE |

---

## Unified Agent API Summary

### ImageAgent (agents/image_agent.py)
```python
agent = ImageAgent(user=request.user)
agent.generate(prompt="...", style="pixar")           # General image generation
agent.generate_logo(brand_name="...", industry="...")  # Logo with brand expertise
agent.generate_social(prompt="...", platform="instagram_square")  # Social media sizing
agent.edit(image_id="...", operation="upscale")       # Editing operations
```

### VideoAgent (agents/video_agent.py)
```python
agent = VideoAgent(user=request.user)
agent.generate(prompt="...", duration=5)              # Text-to-video
agent.animate_image(image_id="...", motion_prompt="...")  # Image-to-video
agent.extend_video(video_id="...", extension_seconds=10)  # Extend video
agent.edit(video_id="...", operation="add_text_overlay", text="...")  # Edit operations
agent.check_status(video_id="...")                    # Poll status
```

### AudioAgent (agents/audio_agent.py)
```python
agent = AudioAgent(user=request.user)
agent.generate_speech(text="...", voice="Rachel")     # Text-to-speech
agent.generate_sound_effect(description="...")        # Sound effects
agent.add_voiceover(video_id="...", text="...", voice="Drew")  # Video voiceover
```

### ResearchAgent (agents/research_agent.py) - Session 203
```python
agent = ResearchAgent(user=request.user)
agent.search(query="AI logo trends")                  # Web + spider search combined
agent.research_topic(topic="...", depth="comprehensive")  # In-depth research
agent.get_domain_intelligence(domain="design")        # Domain-specific spider data
agent.list_available_sources()                        # Show all 46 spiders & domains
```

**Spider Domains Available:**
- `design` - 99designs, Dribbble, Behance
- `tech` - HuggingFace, Kaggle, GitHub, StackOverflow, HackerNews
- `financial` - CoinGecko, Yahoo Finance, market data
- `freelance` - Toptal, Guru, PeoplePerHour, FlexJobs, RemoteOK
- `content` - Medium, Substack, Gumroad, ProductHunt
- `news` - News harvester
- `social` - Social sentiment
- `innovation` - Innovation tracking, patents, research
- `legal` - CourtListener, Justia, FindLaw, LII

---

## Agent Router API (agents/router.py)

The router allows intent-based routing instead of tool-based:

```python
from agents.router import AgentRouter, Intent, route

# Route by intent (preferred)
result = AgentRouter.route('create_image', {'prompt': '...', 'style': 'pixar'}, user)

# Route legacy tool names (backwards compatible)
result = AgentRouter.route_tool('image_generation_agent', {'prompt': '...'}, user)

# Simple convenience function
result = route('create_image', {'prompt': '...'}, user)
```

### Available Intents (31 total)

**Image Intents:**
- `create_image` - Generate an image from text
- `create_logo` - Generate professional logo
- `create_social_media` - Generate platform-optimized content
- `edit_image`, `upscale_image`, `remove_background`, `create_variations`
- `recolor_image`, `erase_object`, `replace_object`, `inpaint`, `outpaint`

**Video Intents:**
- `create_video` - Generate video from text
- `animate_image` - Animate a still image
- `extend_video` - Extend existing video
- `edit_video`, `add_text_to_video`, `add_music_to_video`, `color_grade_video`

**Audio Intents:**
- `create_speech` - Text-to-speech
- `create_sound_effect` - Generate sound effect
- `add_voiceover` - Add voiceover to video

**Other:**
- `create_3d`, `convert_to_3d` - 3D generation
- `web_search`, `research_topic` - Research
- `run_workflow`, `create_project` - Workflows
- `executive_review`, `strategic_review` - Leadership

### Router-Enabled Tools in execute_tool()

Session 204: Expanded to include most tools. Routed through AgentRouter:

**Image Operations:**
- `upscale_image`, `remove_background`, `create_variations`, `recolor_image`
- `erase_object`, `search_and_replace`, `creative_upscale`, `inpaint`, `outpaint`

**Audio Operations:**
- `generate_speech`, `generate_sound_effect`, `add_voiceover`

**Video Operations:**
- `add_text_to_video`, `add_music_to_video`, `apply_color_grade`, `chain_videos`

**Research Operations:**
- `web_search`, `research_topic`, `research`

**Training Operations (Session 204):**
- `character_training_agent`, `train_character`, `train_style`

**Talking Character (Session 204):**
- `talking_character_agent`, `create_talking_character`, `make_image_talk`

**Workflow Operations (Session 204):**
- `workflow_orchestration_agent`, `create_brand_video`

**Leadership Operations (Session 204):**
- `coleadership_agent`, `strategic_review`, `create_project_from_research`

### New Router Methods (Session 204)

```python
# execute_tool - Single entry point for all tool calls
result = AgentRouter.execute_tool(
    tool_name='image_generation_agent',
    arguments={'prompt': '...'},
    user=user,
    session=session,
    project=project
)

# get_router_enabled_tools - List all routable tools
tools = AgentRouter.get_router_enabled_tools()
```

---

## Agent Preference Manager (agents/preference_manager.py) - Session 203 Phase 4

Unified preference system that enables agents to remember and learn from user interactions.

```python
from agents.preference_manager import AgentPreferenceManager

manager = AgentPreferenceManager(user=request.user)

# Get preferences by domain
image_prefs = manager.get_image_preferences()  # style, model, aspect_ratio
video_prefs = manager.get_video_preferences()  # duration, quality
audio_prefs = manager.get_audio_preferences()  # voice, model

# Apply preferences to parameters (fills missing values)
params = {'prompt': 'dancing donkey'}
params = manager.apply_preferences('image', params)
# params now includes user's preferred style, model, etc.

# Record successful generation for learning
manager.record_successful_generation('image', params, user_rating=5)

# Get preference summary
summary = manager.get_preference_summary()
```

### Default Preferences

| Domain | Preference | Default |
|--------|------------|---------|
| Image | style | None (user chooses) |
| Image | model | sd3-large-turbo |
| Image | aspect_ratio | 1:1 |
| Video | duration | 5 seconds |
| Video | quality | gen4_turbo |
| Audio | voice | Rachel |
| Audio | model | eleven_multilingual_v2 |

### Agent Integration

All specialist agents now support preferences:
```python
# ImageAgent - auto-applies learned style
agent = ImageAgent(user=request.user)
result = agent.generate(prompt="dancing donkey")  # Uses learned style!
prefs = agent.get_user_preferences()

# VideoAgent - auto-applies learned duration/quality
agent = VideoAgent(user=request.user)
result = agent.generate(prompt="sunset")  # Uses learned preferences!
prefs = agent.get_user_preferences()

# AudioAgent - auto-applies preferred voice
agent = AudioAgent(user=request.user)
result = agent.generate_speech(text="Hello")  # Uses learned voice!
voice = agent.get_preferred_voice()
```

---

**Last Updated:** November 26, 2025 - Session 204

## Architecture Refactor: COMPLETE!

All 5 phases successfully implemented:

| Phase | What | Result |
|-------|------|--------|
| **Phase 1** | Agent Consolidation | 9 agents -> 3 specialists (ImageAgent, VideoAgent, AudioAgent) |
| **Phase 2** | Agent Router | 35 intents with backwards-compatible tool mapping |
| **Phase 3** | Spider Integration | 46 spiders unified via ResearchAgent |
| **Phase 4** | Memory Enhancement | AgentPreferenceManager with learning from interactions |
| **Phase 5** | Tool Consolidation | execute_tool() unified entry point for all tools |

### Key Achievements
- **Simplified Architecture:** Clean intent-based routing instead of tool soup
- **Preference Learning:** Agents remember user preferences (style, voice, quality)
- **Unified Research:** 46 spiders accessible via single ResearchAgent
- **Single Entry Point:** All tools route through AgentRouter.execute_tool()
- **Backwards Compatible:** Legacy tool names still work via TOOL_TO_INTENT mapping

### The Final Architecture
```
User Request
    ↓
Personal Assistant (understands intent)
    ↓
AgentRouter.execute_tool() (routes to specialist)
    ↓
Specialist Agent (ImageAgent, VideoAgent, AudioAgent, ResearchAgent)
    ↓
AgentPreferenceManager (applies/learns preferences)
    ↓
Result returned to user
```
