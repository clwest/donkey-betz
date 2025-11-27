# Session 238: Prompting System Documentation

**Date:** November 27, 2025
**Previous Session:** 237 (Spider Intelligence & Trending Topics)
**Session Type:** DOCUMENTATION ONLY - No Code Changes

---

## CRITICAL: READ THIS FIRST

This is a **DOCUMENTATION SESSION**. The goal is to completely map and document the prompting system architecture. **DO NOT** make code changes unless absolutely necessary to understand the system.

### The Mission

Document the complete flow from user input to AI response. This includes:
- All entry points (chat, image gen, video gen, workflows)
- Processing pipeline (parsing, routing, context injection)
- Execution paths (OpenAI, Stability, Runway, agents)
- Response flow (formatting, storage, feedback)

---

## Why This Matters

The prompting system is the heart of the platform but nobody fully understands how all pieces connect:
- Chat input handling
- AI engine selection (GPT vs Stability vs Runway)
- Style system integration (80+ presets)
- Spider intelligence context injection
- Workflow orchestration
- Agent execution

**Before we can improve it, we must document it.**

---

## Session 237 Accomplishments

### Fixes Applied
1. **Trending Topics** - Now shows meaningful terms (AI, Developer, Security, Programming)
   - Added ~150 stopwords to filter generic terms
   - Prioritized tags over extracted keywords

2. **Frontend API Calls** - Fixed to use correct endpoints
   - `loadIntelligenceFeed()` → `/api/spider-intelligence/trends/`
   - `loadTrendingTab()` → `/api/spider-intelligence/trends/` + `/tech/`
   - Removed broken `/insights/` calls (requires prompt param)

3. **Portfolio URLs** - Added redirect handler
   - `/api/portfolio/generated_images/` → `/media/generated_images/`

### System Status
- All services running (Daphne, Redis, Celery Worker, Celery Beat)
- Spider network active (67 spiders, 646 data points)
- 5 real data sources live (HackerNews, Dev.to, WeWorkRemotely, CoinGecko, TechCrunch)

---

## How to Execute Session 238

### Phase 1: Frontend Tracing (30 min)
1. Open `ai_core/templates/ai_image_studio.html`
2. Find all form submit handlers
3. Trace what happens when user presses Enter in chat
4. Trace what happens when user clicks "Generate"
5. Document all fetch() calls to backend

### Phase 2: Backend Mapping (45 min)
1. Follow each API endpoint from `core/urls.py`
2. Map the view functions in `core/views_*.py`
3. Trace into service classes
4. Document external API calls (OpenAI, Stability, Runway)

### Phase 3: Integration Points (30 min)
1. How does spider data get into prompts?
2. How does style system modify prompts?
3. How do agents communicate?

### Phase 4: Documentation (30 min)
1. Create the architecture diagram
2. Write the flow documentation
3. Identify gaps and opportunities
4. Save to `docs/architecture/PROMPTING_SYSTEM.md`

---

## Key Files to Investigate

### Frontend
```
ai_core/templates/ai_image_studio.html   # Main UI (~30k lines)
```

### Backend
```
core/urls.py                             # All routes
core/views_chat.py                       # Chat endpoint
core/views_image.py                      # Image generation
core/views_video.py                      # Video generation
core/views_assistant.py                  # Assistant endpoints
core/assistant/tool_definitions.py       # GPT function definitions
core/assistant/constants.py              # System prompts
```

### Agents & Workflows
```
agents/workflow_orchestration_agent.py   # Workflow system
ai_core/agents/                          # 14 AI content agents
```

### Intelligence
```
core/services/spider_intelligence.py     # Spider queries
```

### Style System
```
content/image_generation.py              # 80+ style presets
```

---

## Expected Deliverable

Create `docs/architecture/PROMPTING_SYSTEM.md` containing:

1. **Architecture Diagram** (text-based)
2. **Entry Points Documentation** - All ways users trigger AI
3. **Processing Pipeline** - How prompts are handled
4. **Execution Paths** - Which API gets called when
5. **Response Flow** - How results return to user
6. **Gap Analysis** - What's missing or disconnected

---

## Quick Start Commands

```bash
# Verify services are running
curl http://localhost:8000/health/ping/

# Access the UI
open http://localhost:8000/ai-studio/

# Read the detailed handoff
cat docs/sessions/SESSION_238_HANDOFF_PROMPTING_SYSTEM_DOCUMENTATION.md
```

---

## Success Criteria

Session 238 is complete when:
- [ ] Complete architecture diagram created
- [ ] All entry points documented
- [ ] All processing paths traced
- [ ] All execution paths mapped
- [ ] Gap analysis complete
- [ ] Documentation saved to `docs/architecture/PROMPTING_SYSTEM.md`

---

**Detailed handoff:** `docs/sessions/SESSION_238_HANDOFF_PROMPTING_SYSTEM_DOCUMENTATION.md`
**Previous session:** `docs/sessions/SESSION_237_SPIDER_INTELLIGENCE.md`
