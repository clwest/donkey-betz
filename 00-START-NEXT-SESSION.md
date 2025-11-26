# Session 202: Agent Architecture Deep Dive & Spider Integration

**Date:** November 26, 2025
**Previous Session:** 201 (Style System & Prompting Fix)
**Current Reality Score:** 100%
**Status:** Ready for Agent Architecture Audit

---

## Session 201 - STYLE SYSTEM FIXED!

### What We Fixed

1. **Kung Fu Panda Bug** - Style expansions included character names that overrode user topics
2. **Bypassed Style System** - Workflow agent was using its own mini style dictionary instead of the 80+ built-in styles
3. **Missing Styles** - Added 14 new animation styles including DreamWorks, South Park, Simpsons, etc.

### New Animation Styles Added

| Style Key | Shows |
|-----------|-------|
| `dreamworks` | DreamWorks 3D animation |
| `south_park` | South Park cutout style |
| `simpsons` | The Simpsons |
| `family_guy` | Family Guy |
| `ghibli` | Studio Ghibli |
| `looney_tunes` | Looney Tunes |
| `rick_and_morty` | Rick and Morty |
| `archer` | Archer |
| `adventure_time` | Adventure Time |
| `gravity_falls` | Gravity Falls |
| `bojack` | BoJack Horseman |

### Files Modified in Session 201

| File | Changes |
|------|---------|
| `content/image_generation.py` | Added 14 new animation styles to `_apply_style_to_prompt()` |
| `agents/workflow_orchestration_agent.py` | Fixed to use built-in 80+ styles, removed character references |
| `ai_core/templates/ai_image_studio.html` | Fixed images vs logos detection, style extraction |
| `docs/sessions/SESSION_201_STYLE_SYSTEM_FIX.md` | Session documentation |

---

## Session 202 Focus: Agent Architecture Deep Dive

### Goal

Step back and audit ALL agents to ensure:
1. Every agent is being utilized properly
2. Agent flows are not being bypassed
3. The spider network is integrated for real-time research
4. No duplicate functionality exists

### Known Agents to Audit

**Content Generation Agents:**
- `image_generation_agent` - Generate new images
- `image_editing_agent` - Modify existing images (upscale, remove bg, etc.)
- `video_generation_agent` - Generate/animate videos
- `video_editing_agent` - Edit videos (trim, speed, effects)
- `audio_generation_agent` - Text-to-speech, sound effects
- `three_d_generation_agent` - Image to 3D model conversion
- `character_training_agent` - Train custom character models
- `talking_character_agent` - Create talking character videos

**Orchestration Agents:**
- `workflow_orchestration_agent` - Multi-step research + creation workflows
- `coleadership_agent` - Executive team meetings (CTO, COO, etc.)

**Research/Analysis Agents:**
- `web_search` - Web research capabilities
- Various spiders (need to audit)

### Key Questions to Answer

1. **What agents exist?** - Full inventory of all agents
2. **How are they called?** - Tool definitions, frontend detection, backend handlers
3. **Are any being bypassed?** - Like we found with the style system
4. **What spiders exist?** - And how can they feed into agents?
5. **What's underutilized?** - Features that exist but aren't being used

### Agent Architecture Files

**Agent Definitions:**
- `agents/` directory - All agent implementations
- `core/assistant/tool_definitions.py` - GPT tool schemas
- `core/assistant/constants.py` - Operation enums

**Agent Handlers:**
- `core/views_image.py` - `execute_tool()` function
- `core/personal_ai_assistant_enhanced.py` - Assistant agent handling

**Frontend:**
- `ai_core/templates/ai_image_studio.html` - `executeTools()`, `formatToolResults()`

---

## Spider Network (To Explore)

The platform has spider capabilities that could enhance agent research:

**Potential Spider Integration:**
- Real-time market research
- Trend analysis
- Competitor monitoring
- Price tracking
- Content discovery

**Questions:**
- Where are spiders defined?
- How do they currently operate?
- Can they feed data to agents?
- What APIs/sources do they crawl?

---

## Server Commands

```bash
# Full restart
pkill -f daphne; pkill -f redis; rm -f .daphne.pid && make start

# Check health
curl http://localhost:8000/health/ping/

# Open AI Studio
open http://localhost:8000/ai-studio/
```

---

## Style System Reference (80+ Styles)

The built-in style system is in `content/image_generation.py`:

**Example usage:**
```
"Create a cyberpunk city" → Uses built-in cyberpunk expansion
"Create a dreamworks style mascot" → Uses new dreamworks expansion
"Create a watercolor landscape" → Uses watercolor expansion
```

**Full style list:** See `_apply_style_to_prompt()` method (lines 173-280)

---

**Reality Score:** 100%
**Built-in Styles:** 80+
**Next Focus:** Agent architecture audit & spider integration
