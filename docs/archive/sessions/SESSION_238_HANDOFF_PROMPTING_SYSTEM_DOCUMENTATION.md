# Session 238 Handoff: Prompting System Documentation

**Priority:** HIGH - This is foundational work for improving the entire platform
**Type:** Pure Documentation & Analysis (No Code Changes)
**Previous Session:** 237 - Spider Intelligence & Trending Topics Improvements

---

## Mission Statement

Document the complete prompting system architecture from user input to AI response. This documentation will serve as the blueprint for understanding, debugging, and improving the entire AI content creation pipeline.

---

## Why This Matters

The prompting system is the heart of the platform. It connects:
- User chat input (Assistant)
- Image/Video/Audio generation
- Workflow orchestration
- Spider intelligence data
- Agent execution
- Style system (80+ presets)

**Problem:** Nobody fully understands how all these pieces connect. Before we can improve it, we need to map it completely.

---

## Objectives for Session 238

### 1. Document Entry Points
Trace every way a user can trigger AI processing:
- Main chat input on Assistant page
- Image generation prompt field
- Video generation prompt field
- Workflow execution triggers
- Quick action buttons
- Trending topic clicks

### 2. Document Processing Pipeline
For each entry point, trace:
- Where does the prompt text go first?
- What parsing/classification happens?
- How is the AI engine selected (GPT vs Stability vs Runway)?
- What context is injected (spider data, user history, style)?
- How are tools/functions selected?

### 3. Document Execution Paths
Map the actual API calls:
- OpenAI GPT calls (assistant, chat completions)
- Stability AI calls (image generation)
- Runway ML calls (video generation)
- ElevenLabs calls (audio generation)
- Internal agent execution

### 4. Document Response Flow
Trace the output path:
- How are results formatted?
- Where is history stored?
- What feedback loops exist?
- How does learning happen?

---

## Key Files to Investigate

### Frontend (Entry Points)
```
ai_core/templates/ai_image_studio.html
- Main UI (~30k lines)
- Chat input handlers
- Generation form handlers
- WebSocket connections
```

### Backend Processing
```
core/assistant/                    # Assistant system
  - tool_definitions.py           # GPT function definitions
  - constants.py                  # System prompts, constants

core/views_chat.py                # Chat API endpoint
core/views_image.py               # Image generation
core/views_video.py               # Video generation
core/views_assistant.py           # Assistant endpoints

agents/                           # Agent system
  - workflow_orchestration_agent.py
  - (14 AI content agents)
```

### Intelligence Integration
```
core/services/spider_intelligence.py  # Spider data queries
ai_core/spiders/real_data_collector.py # Real data fetching
```

### Style System
```
content/image_generation.py       # 80+ style presets
```

---

## Questions to Answer

### Entry Points
1. When user types in chat, what JavaScript function handles it?
2. What API endpoint receives the chat message?
3. How does the system distinguish "generate an image" from "answer a question"?

### Processing
4. Where is the system prompt defined for the Assistant?
5. How are GPT tools/functions registered?
6. What decides if spider data should be included in context?
7. How does the style system inject into prompts?

### Execution
8. What's the exact flow from chat input to Stability AI call?
9. How do workflows chain multiple operations?
10. Where do agent results get stored?

### Response
11. How are generated images saved and returned to UI?
12. What triggers the portfolio/history update?
13. Where does user feedback get captured?

---

## Expected Deliverables

### 1. Architecture Diagram (Text-Based)
```
User Input
    │
    ▼
[Entry Point] ─────────────────────────────────┐
    │                                          │
    ▼                                          │
[Prompt Parser/Classifier]                     │
    │                                          │
    ├── Chat/Question ──► OpenAI GPT           │
    │                         │                │
    ├── Image Request ──► Stability AI         │
    │                         │                │
    ├── Video Request ──► Runway ML            │
    │                         │                │
    └── Workflow ──► Orchestration Agent       │
                          │                    │
                          ▼                    │
                    [Result Handler] ◄─────────┘
                          │
                          ▼
                    [UI Update + Storage]
```

### 2. Detailed Flow Documentation
For each path, document:
- File locations
- Function names
- API endpoints
- Data transformations

### 3. Gap Analysis
Identify:
- Disconnected components
- Unused code paths
- Missing integrations
- Improvement opportunities

---

## How to Execute This Session

### Phase 1: Frontend Tracing (30 min)
1. Search for form submit handlers in ai_image_studio.html
2. Trace what happens when user presses Enter in chat
3. Trace what happens when user clicks "Generate"
4. Document all fetch() calls to backend

### Phase 2: Backend Mapping (45 min)
1. Follow each API endpoint from urls.py
2. Map the view functions
3. Trace into service classes
4. Document external API calls

### Phase 3: Integration Points (30 min)
1. How does spider data get into prompts?
2. How does style system modify prompts?
3. How do agents communicate?

### Phase 4: Documentation (30 min)
1. Create the architecture diagram
2. Write the flow documentation
3. Identify gaps and opportunities

---

## System Status at Handoff

### Services Running
- Daphne (ASGI): Running on :8000
- Redis: Running
- Celery Worker: Running
- Celery Beat: Running

### Recent Fixes (Session 237)
- Trending topics now show meaningful terms (AI, Developer, Security)
- Frontend uses correct spider-intelligence API endpoints
- Legacy portfolio URL redirect working
- Removed broken insights API calls

### API Keys Status
- OpenAI: Configured
- Stability AI: Needs refresh (key rejected)
- Runway ML: Configured
- ElevenLabs: Configured

---

## Commands to Start

```bash
# Verify services are running
curl http://localhost:8000/health/ping/

# Access the UI
open http://localhost:8000/ai-studio/

# Check current context
cat 00-START-NEXT-SESSION.md
```

---

## Success Criteria

Session 238 is complete when:
1. Complete architecture diagram exists
2. All entry points are documented
3. All processing paths are traced
4. All execution paths are mapped
5. Gap analysis is complete
6. Documentation saved to docs/architecture/PROMPTING_SYSTEM.md

---

**Note to Future Claude:** This is a DOCUMENTATION session. Do NOT make code changes unless absolutely necessary to understand the system. The goal is to create a complete map of the prompting system that can be used for improvements in future sessions.
