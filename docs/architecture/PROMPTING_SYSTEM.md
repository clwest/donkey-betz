<!-- DOC-POINTER-V1 (Session 1145) -->
> **⚠ Pattern doc with drift warning.** The orchestrator + function-calling pipeline concept described here is still in use, but specific counts (spider sources, registered agents, preset styles), model versions, and class names (e.g. `EnhancedPersonalAIAssistant`, `views_assistant_bypass.py`) may have drifted from code.
> **Last reviewed for drift labeling:** Session 1145 (2026-05-25)
> **Current truth:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (runtime counts) + [`docs/topics/personal-assistant.md`](../topics/personal-assistant.md) (current PA architecture).
> **Note:** Live PA route is `POST /api/pa/chat/` (this doc already carries an inline historical note about that at line 14). Per `DOC_LIFECYCLE.md` §2c, `PLATFORM_INVENTORY` + `docs/INDEX` are the only authoritative count sources. Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge.

# Prompting System Architecture

**Date:** November 27, 2025 - Session 238
**Status:** Complete Documentation
**Purpose:** Document the complete flow from user input to AI response

> Historical note: this document predates Rigby unification. The live route is `POST /api/pa/chat/`. `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compatibility-only shims.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Entry Points](#entry-points)
4. [Processing Pipeline](#processing-pipeline)
5. [Execution Paths](#execution-paths)
6. [Response Flow](#response-flow)
7. [Integration Points](#integration-points)
8. [Gap Analysis](#gap-analysis)

---

## System Overview

The prompting system is the heart of the AI Content Studio platform. It connects:
- **User chat input** (main AI Assistant)
- **Image/Video/Audio generation** (Stability AI, Runway ML, ElevenLabs)
- **Workflow orchestration** (research + creation pipelines)
- **Spider intelligence** (real-time data from 21 sources)
- **Agent execution** (149 registered agents)
- **Style system** (80+ preset styles)
- **User personalization** (learned preferences, conversation history)

### Philosophy

The system uses a **GPT-5.1 as orchestrator** pattern:
1. User input goes to GPT-5.1 with function calling enabled
2. GPT decides which agent/tool to invoke
3. Backend executes the tool and returns results
4. GPT can chain multiple operations in a workflow

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                                   │
│                    ai_image_studio.html (~45k lines)                    │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │ Chat Input  │  │ Generate    │  │ Quick       │  │ Trending     │   │
│  │ (Tab/Modal) │  │ Form        │  │ Actions     │  │ Topic Click  │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘   │
│         │                │                │                │            │
│         └────────────────┴────────────────┴────────────────┘            │
│                                  │                                       │
│                    ┌─────────────▼─────────────┐                        │
│                    │     AIAssistant Class     │                        │
│                    │   (sendMessage method)    │                        │
│                    └─────────────┬─────────────┘                        │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │
                        fetch('/api/pa/chat/')
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                                    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              views_assistant_bypass.py                           │   │
│  │              assistant_chat_bypass()                             │   │
│  │                                                                   │   │
│  │  1. Validate input (rate limiting, CSRF, sanitization)          │   │
│  │  2. Get authenticated user                                       │   │
│  │  3. Initialize EnhancedPersonalAIAssistant(user)                │   │
│  │  4. Call assistant.process_message(message, context)             │   │
│  └───────────────────────────────┬─────────────────────────────────┘   │
│                                  │                                       │
│                                  ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │           EnhancedPersonalAIAssistant                            │   │
│  │           personal_ai_assistant_enhanced.py                      │   │
│  │                                                                   │   │
│  │  CONTEXT BUILDING (process_message):                             │   │
│  │  ├── User patterns analysis                                      │   │
│  │  ├── Conversation history (last 3-5 messages)                   │   │
│  │  ├── Enhanced profile (role, skills, goals)                     │   │
│  │  ├── Recent assets context (images/videos in 10-min window)     │   │
│  │  ├── Style preferences (Session 169 learned preferences)        │   │
│  │  ├── Project brief context (Session 181)                        │   │
│  │  └── Memory context (unified memory manager)                    │   │
│  │                                                                   │   │
│  │  SYSTEM PROMPT (~150 lines):                                     │   │
│  │  ├── User profile (name, role, skills, goals)                   │   │
│  │  ├── Conversation context                                        │   │
│  │  ├── Recent memories                                             │   │
│  │  ├── Agent activities                                            │   │
│  │  ├── Style preferences                                           │   │
│  │  ├── Available assets                                            │   │
│  │  ├── Project context (active project ID)                        │   │
│  │  └── 18+ critical instructions for GPT behavior                 │   │
│  │                                                                   │   │
│  │  TOOL DEFINITIONS (get_tool_definitions):                        │   │
│  │  ├── image_generation_agent (Stability AI)                      │   │
│  │  ├── image_editing_agent (upscale, remove_bg, recolor, etc.)   │   │
│  │  ├── video_generation_agent (Runway ML)                         │   │
│  │  ├── audio_generation_agent (ElevenLabs)                        │   │
│  │  ├── video_editing_agent (DaVinci/ffmpeg)                       │   │
│  │  ├── three_d_generation_agent (Replicate TRELLIS)               │   │
│  │  ├── character_training_agent (FLUX LoRA)                       │   │
│  │  ├── coleadership_agent (executive team opinions)               │   │
│  │  ├── talking_character_agent (TTS + animation + lip sync)       │   │
│  │  ├── workflow_orchestration_agent (research + create)           │   │
│  │  └── web_search (Google Custom Search)                          │   │
│  └───────────────────────────────┬─────────────────────────────────┘   │
│                                  │                                       │
│                          LLM Enforcer                                    │
│                      (OpenAI GPT-5.1 API)                               │
│                                  │                                       │
│                                  ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    TOOL EXECUTION LAYER                          │   │
│  │                                                                   │   │
│  │  GPT-5.1 returns tool_calls → Backend executes each tool:       │   │
│  │                                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │ Creation    │  │ Editing     │  │ Workflow                │  │   │
│  │  │ Agent       │  │ Agent       │  │ Orchestration           │  │   │
│  │  │             │  │             │  │ Agent                   │  │   │
│  │  │ Stability   │  │ Upscale     │  │ research →              │  │   │
│  │  │ AI API      │  │ Remove BG   │  │ exec_review →           │  │   │
│  │  │             │  │ Recolor     │  │ generate →              │  │   │
│  │  │             │  │ Inpaint     │  │ save                    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  │                                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │ Video       │  │ Audio       │  │ Video                   │  │   │
│  │  │ Generation  │  │ Generation  │  │ Editing                 │  │   │
│  │  │ Agent       │  │ Agent       │  │ Agent                   │  │   │
│  │  │             │  │             │  │                         │  │   │
│  │  │ Runway ML   │  │ ElevenLabs  │  │ DaVinci Resolve         │  │   │
│  │  │ API         │  │ API         │  │ + ffmpeg                │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Entry Points

### 1. Main Chat Input (Primary)

**Frontend Location:** `ai_image_studio.html:21156` - `AIAssistant` class

**Event Flow:**
```
User types message in #tabAssistantInput
    → Enter key or Send button click
    → AIAssistant.sendMessage('tab')
    → Builds request body with message, conversation_history, context
    → authenticatedFetch('/api/pa/chat/', { method: 'POST', body: JSON.stringify(requestBody) })
    → Receives response with message and/or tool_calls
    → If tool_calls: executeTools() → formatToolResults() → display
    → If message: display in chat
```

**Key Code:**
- `ai_image_studio.html:21920` - `sendMessage()` method
- `ai_image_studio.html:22965` - `callAI()` method (calls `/api/pa/chat/`)

### 2. Image Generation Form

**Frontend Location:** `ai_image_studio.html:11328`

**Event Flow:**
```
User fills prompt in #generateForm
    → Submit button or Enter key
    → Form submit handler
    → Optional: /api/v1/gallery/optimize-prompt/ (prompt optimization)
    → /api/v1/gallery/generate/ (direct generation)
    → Display result in gallery
```

### 3. Quick Actions

**Frontend Location:** `ai_image_studio.html:21274-21280`

**Event Flow:**
```
Quick action buttons (.tab-quick-action)
    → Click handler
    → handleQuickAction(action)
    → Routes to appropriate workflow
```

### 4. Trending Topic Clicks

**Frontend Location:** `ai_image_studio.html:12959-12963`

**Event Flow:**
```
Trending topic click
    → Sets prompt in #asstUserInput
    → User can modify and send
```

### 5. Tool Execution (Internal)

**Frontend Location:** `ai_image_studio.html:11071`

```
/api/tools/execute/ - Direct tool execution bypassing GPT
```

---

## Processing Pipeline

### Step 1: Input Validation

**File:** `core/views_assistant_bypass.py:36`

```python
@never_cache
@require_POST
@rate_limit('ai_generation')  # 10 requests/min
def assistant_chat_bypass(request):
    # 1. Parse JSON body
    # 2. Validate prompt (1-10000 chars)
    # 3. Sanitize to prevent XSS/injection
    # 4. Verify authentication
    # 5. Validate project_id if provided
```

### Step 2: Context Building

**File:** `core/personal_ai_assistant_enhanced.py:5324`

```python
def process_message(self, message: str, context: Optional[Dict[str, Any]] = None):
    # 1. Analyze user patterns
    user_patterns = self._analyze_user_patterns()

    # 2. Load conversation history (last 3-5 messages)
    conversation_history = self._load_conversation_history(limit=3)

    # 3. Create personalized context
    personalized_context = self._create_personalized_context(message, user_patterns)

    # 4. Load enhanced profile
    profile_context = self.enhanced_profile.get_context_for_ai('chat')

    # 5. Merge all contexts
    full_context = {
        'user_profile': profile_context,
        'user_role': self.enhanced_profile.primary_role,
        'communication_style': self.enhanced_profile.communication_style,
        'goals': self.enhanced_profile.long_term_goals,
        'skills': {'top_skills': list(self.enhanced_profile.core_competencies.keys())[:5]},
        'conversation_history': conversation_context,
        ...
    }
```

### Step 3: System Prompt Construction

**File:** `core/personal_ai_assistant_enhanced.py:4800-4920`

The system prompt includes:

1. **User Profile Section**
   - Name, username, role
   - Communication style, learning style
   - Long-term goals, current projects
   - Core skills

2. **Context Sections**
   - Conversation history
   - Recent memories (from UnifiedMemoryManager)
   - Recent agent activities
   - User style preferences (Session 169 learned preferences)
   - Available assets (images/videos in current context)
   - Project brief (Session 181)

3. **Critical Instructions (18+)**
   - Address user by name
   - Maintain conversation continuity
   - Intelligent asset chaining (use images for videos)
   - Credit conservation warnings
   - Agent orchestration announcements
   - Tool calling requirements
   - Single tool call for counted requests
   - No hallucinating completed work
   - Workflow orchestration for research+create

### Step 4: Tool Definitions

**File:** `core/personal_ai_assistant_enhanced.py:66-500`

10+ agent-based tools defined for GPT-5.1:

| Tool | Description | Backend |
|------|-------------|---------|
| `image_generation_agent` | Create new images | Stability AI |
| `image_editing_agent` | Modify existing images | Stability AI |
| `video_generation_agent` | Create/animate videos | Runway ML |
| `audio_generation_agent` | Text-to-speech | ElevenLabs |
| `video_editing_agent` | 25+ operations | DaVinci/ffmpeg |
| `three_d_generation_agent` | Image to 3D | Replicate |
| `character_training_agent` | Train LoRA models | FLUX |
| `coleadership_agent` | Executive opinions | Internal |
| `talking_character_agent` | Full pipeline | Multiple |
| `workflow_orchestration_agent` | Multi-step flows | Internal |
| `web_search` | Research | Google |

### Step 5: LLM Call

**File:** `core/llm_enforcer.py`

```python
# OpenAI GPT-5.1 API call
params = {
    'model': "gpt-5.1-mini",  # or configured model
    'messages': [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ],
    'tools': tool_definitions,
    'max_completion_tokens': max_tokens
}
response = openai.chat.completions.create(**params)
```

---

## Execution Paths

### Path 1: Direct Text Response

```
User: "What can you help me with?"
    → GPT-5.1 understands this is a question
    → Returns text response (no tool_calls)
    → Frontend displays message
```

### Path 2: Single Tool Call

```
User: "Create a logo for a coffee shop"
    → GPT-5.1 identifies image generation request
    → Returns tool_calls: [image_generation_agent(prompt="...", count=1)]
    → Backend executes via _handle_image_generation_agent()
    → Calls CreationAgent → Stability AI API
    → Returns result with image_id
    → Frontend displays image
```

### Path 3: Workflow Orchestration

```
User: "Research modern AI company logo trends and create 3 professional logos"
    → GPT-5.1 identifies research + create pattern
    → Returns tool_calls: [workflow_orchestration_agent(workflow="research_and_create_logos", topic="modern AI company", count=3)]
    → Backend executes full workflow:
        1. Web search for trends
        2. Executive review (coleadership opinions)
        3. Image generation (3 logos)
        4. Project creation
    → Returns comprehensive result
    → Frontend displays all steps + images
```

### Path 4: Multi-Step Autonomous Workflow

```
User: "Create 3 logos and animate the best one"
    → Iteration 1: GPT calls image_generation_agent(count=3)
        → Returns 3 images
    → Iteration 2: GPT evaluates and calls video_generation_agent(operation="animate", image_id="X")
        → Returns video task
    → Frontend tracks cumulative stats across iterations
    → MAX_ITERATIONS = 5 (prevents infinite loops)
```

### Path 5: Batch Operations

```
User: "Upscale images 20-25"
    → GPT calls image_editing_agent(operation="upscale", image_id="20-25")
    → Backend parses range → [20, 21, 22, 23, 24, 25]
    → Processes each sequentially
    → Returns batch summary
```

---

## Response Flow

### Frontend Response Handling

**File:** `ai_image_studio.html:22993-23032`

```javascript
// In callAI() method:

// 1. Check for tool_calls
if (data.tool_calls && data.tool_calls.length > 0) {
    // Execute tools autonomously
    const results = await this.executeTools(data.tool_calls);

    // Strip image URLs from results (prevent context overflow)
    const resultsForGPT5 = stripImageUrls(results);

    return {
        message: this.formatToolResults(results),
        tool_results: resultsForGPT5
    };
}

// 2. Normal text response
else if (data.response || data.message) {
    return { message: data.response || data.message };
}
```

### Tool Results Display

**File:** `ai_image_studio.html` - `formatToolResults()` method

- Images displayed inline with copy ID button
- Videos displayed with player controls
- Workflow steps shown with research sources, executive opinions
- Success/failure status with appropriate styling

---

## Integration Points

### 1. Spider Intelligence Integration

**How spider data enters prompts:**

Currently, spider data is NOT directly injected into prompts. Instead:
- Spider data feeds trending topics (frontend)
- User can click trending topics to start prompts
- Opportunity Engine uses spider data for scoring

**Files:**
- `core/views_spider_intelligence.py` - API endpoints
- `ai_image_studio.html:12864` - `loadIntelligenceFeed()`

**Gap:** Spider intelligence could be injected as context for prompts.

### 2. Style System Integration

**80+ style presets defined in:**
- `content/image_generation.py:176-269` - `style_mappings` dictionary

**How styles enter prompts:**

```python
def _apply_style_to_prompt(self, prompt: str, style: str) -> str:
    style_mappings = {
        'photorealistic': f"{prompt}, photorealistic, ultra detailed, professional photography...",
        'pixar': f"{prompt}, Pixar 3D animation style, Disney Pixar movie quality...",
        'dreamworks': f"{prompt}, DreamWorks 3D animation style, stylized expressive characters...",
        # ... 80+ styles
    }
    return style_mappings.get(style, prompt)
```

**User mentions style → GPT extracts → Backend applies style mapping**

### 3. User Style Preferences (Session 169)

**Learned preferences injected via:**
- `_get_style_preferences_context()` method
- `style_memory.embedding_bridge.get_style_context_for_user()`

**Adds to system prompt:**
```
User Style Preferences (Session 169 - Personalized Generation):
- Prefers vibrant colors and modern aesthetics
- Frequently uses photorealistic and fantasy styles
```

### 4. Project Context

**Project ID flows through:**
1. Frontend stores `activeProjectId`
2. Sent in request body to `/api/pa/chat/`
3. Backend resolves to `CreativeProject` object
4. Passed to agent tool calls
5. Generated assets linked to project

### 5. Agent Communication

**Agent-to-agent communication via:**
- `intelligence/agent_query_protocol.py` - Redis pub/sub
- Enables VideoAgent to request audio from AudioAgent
- Enables workflow orchestration

---

## Gap Analysis

### 1. Spider Intelligence Not in Prompts

**Current:** Spider data displayed separately in UI
**Opportunity:** Inject relevant spider intelligence as context:
```
Recent Market Intelligence:
- "AI content tools" trending +45% this week
- Top opportunity: Logo design for tech startups
- Competitor analysis: [spider data]
```

### 2. Limited Prompt Optimization Feedback

**Current:** Prompt optimization is one-way
**Opportunity:** Learn from successful generations to improve optimization

### 3. No Cross-Session Learning

**Current:** Each session starts fresh
**Opportunity:** Remember successful prompts and styles across sessions

### 4. Style Recommendation Gap

**Current:** User must know style names
**Opportunity:** AI could recommend styles based on content type:
```
"For a coffee shop logo, I'd recommend 'minimalist' or 'art_deco' style"
```

### 5. Workflow Templates Not Discoverable

**Current:** 6 workflows exist but user must know them
**Opportunity:** GPT could suggest relevant workflows:
```
"I notice you want research + creation. Would you like me to run the
'research_and_create_logos' workflow?"
```

---

## File Reference

### Core Files

| File | Lines | Purpose |
|------|-------|---------|
| `ai_core/templates/ai_image_studio.html` | ~45k | Main UI, AIAssistant class |
| `core/views_assistant_bypass.py` | 173 | Chat endpoint |
| `core/personal_ai_assistant_enhanced.py` | ~6k | Main assistant logic |
| `core/llm_enforcer.py` | ~400 | OpenAI API calls |
| `core/assistant/tool_definitions.py` | varies | GPT tool schemas |
| `content/image_generation.py` | ~1.5k | Stability AI + style system |
| `content/video_provider.py` | ~800 | Runway ML |
| `content/elevenlabs_provider.py` | ~330 | ElevenLabs |
| `agents/workflow_orchestration_agent.py` | varies | Multi-step workflows |

### Agent Files

| File | Purpose |
|------|---------|
| `agents/creation_agent.py` | Standard image generation |
| `agents/trained_creation_agent.py` | LoRA-based generation |
| `agents/video_agent.py` | Video operations |
| `agents/audio_agent.py` | Audio operations |

### Intelligence Files

| File | Purpose |
|------|---------|
| `core/services/spider_intelligence.py` | Spider data queries |
| `style_memory/embedding_bridge.py` | Style preference embeddings |
| `core/unified_memory_manager.py` | User memory system |

---

## Summary

The prompting system uses a **GPT-5.1 orchestrator pattern** where:

1. **User input** enters through the AIAssistant class
2. **Context** is built from user profile, conversation history, assets, and preferences
3. **System prompt** (~150 lines) guides GPT behavior with 18+ critical instructions
4. **Tool definitions** (10+ agents) give GPT execution capabilities
5. **GPT decides** which tools to call (or returns text)
6. **Backend executes** tools via specialized agents
7. **Results flow** back to frontend for display

**Strengths:**
- Unified orchestration through GPT
- Rich context building
- Flexible tool execution
- Multi-step workflow support
- Batch operations

**Opportunities:**
- Inject spider intelligence into prompts
- Cross-session learning
- Style recommendations
- Workflow discovery

---

**Last Updated:** Session 238 - November 27, 2025
**Author:** Claude (Documentation Session)
