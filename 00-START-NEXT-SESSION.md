# Session 269: Clean Architecture Implementation - Phase 2

**Date:** November 29, 2025
**Previous Session:** 268 (Phase 1 Complete - Foundation)
**Session Type:** Major Architecture Overhaul
**Status:** READY TO IMPLEMENT

---

## Phase 1 Complete!

Session 268 successfully implemented the foundation:

| File | Purpose | Status |
|------|---------|--------|
| `core/agents/__init__.py` | Package init | DONE |
| `core/agents/base_agent.py` | Abstract base with TimeTravelMixin | DONE |
| `core/agents/image_agent.py` | Image generation ONLY | DONE |
| `core/agent_router.py` | Deterministic routing | DONE |
| `core/settings.py` | Added `USE_CLEAN_AGENT_ARCHITECTURE` flag | DONE |

All tests pass:
- ImageAgent instantiation
- AgentRouter routing
- SciFi context injection
- Spider context injection
- TimeTravelMixin integration
- Feature flag exists (False by default)

---

## Phase 2 Tasks (This Session)

### 1. Create All Creation Agents

```python
# core/agents/video_agent.py
class VideoAgent(BaseAgent):
    name = "VideoAgent"
    system_prompt = "You create videos. That's all."
    tools = [generate_video, animate_image, extend_video, chain_clips]

# core/agents/audio_agent.py
class AudioAgent(BaseAgent):
    name = "AudioAgent"
    system_prompt = "You create audio. That's all."
    tools = [generate_voice, generate_sfx, add_voiceover]

# core/agents/three_d_agent.py
class ThreeDAgent(BaseAgent):
    name = "ThreeDAgent"
    system_prompt = "You create 3D models. That's all."
    tools = [convert_to_3d, generate_3d_scene]
```

### 2. Create All Editing Agents

```python
# core/agents/image_editing_agent.py
class ImageEditingAgent(BaseAgent):
    name = "ImageEditingAgent"
    system_prompt = "You modify existing images. That's all."
    tools = [upscale, remove_bg, recolor, create_variations, search_replace]

# core/agents/video_editing_agent.py
class VideoEditingAgent(BaseAgent):
    name = "VideoEditingAgent"
    system_prompt = "You modify existing videos. That's all."
    tools = [trim, add_effects, add_text, concatenate, extract_frame, ...]
```

### 3. Create Research Agents

```python
# core/agents/research_agent.py
class ResearchAgent(BaseAgent):
    name = "ResearchAgent"
    system_prompt = "You search the web and spider network. That's all."
    tools = [web_search, spider_query]

# core/agents/trend_agent.py
class TrendAnalysisAgent(BaseAgent):
    name = "TrendAnalysisAgent"
    system_prompt = "You analyze trends and patterns. That's all."
    tools = [analyze_trends, predict_opportunities]
```

### 4. Create Orchestration Agents

```python
# core/agents/workflow_agent.py
class WorkflowAgent(BaseAgent):
    name = "WorkflowAgent"
    system_prompt = "You coordinate multi-step workflows. You can delegate to other agents."
    tools = [delegate_to_agent]  # Special: can call other agents

# core/agents/hive_mind_agent.py
class HiveMindAgent(BaseAgent):
    name = "HiveMindAgent"
    system_prompt = "You synthesize multi-agent intelligence."
    tools = [gather_perspectives, synthesize, debate]
```

### 5. Update AgentRouter

Add all new agents to `AGENT_MAP`:

```python
AGENT_MAP = {
    "ImageAgent": ImageAgent,
    "VideoAgent": VideoAgent,
    "AudioAgent": AudioAgent,
    "ThreeDAgent": ThreeDAgent,
    "ImageEditingAgent": ImageEditingAgent,
    "VideoEditingAgent": VideoEditingAgent,
    "ResearchAgent": ResearchAgent,
    "TrendAnalysisAgent": TrendAnalysisAgent,
    "WorkflowAgent": WorkflowAgent,
    "HiveMindAgent": HiveMindAgent,
    "ContentStrategyAgent": ContentStrategyAgent,
    "SEOOptimizerAgent": SEOOptimizerAgent,
    "BrandIdentityAgent": BrandIdentityAgent,
}
```

---

## Reference: Existing Tool Functions

Use these existing functions in the new agents:

### Video Tools (core/views_video.py)
- `_execute_generate_video(user, params, session)` - Text-to-video
- `_execute_animate_image(user, params, session)` - Image-to-video
- `_execute_extend_video(user, params, session)` - Extend duration
- `_execute_chain_clips(user, params, session)` - Concatenate clips

### Audio Tools (core/views_audio.py)
- `generate_voice(user, params, session)` - Text-to-speech
- `add_voiceover(user, params, session)` - Add voice to video

### Image Editing (core/views_image.py)
- `_execute_upscale(user, params, session)`
- `_execute_remove_background(user, params, session)`
- `_execute_recolor(user, params, session)`
- `_execute_variations(user, params, session)`
- `_execute_search_replace(user, params, session)`

### Research Tools
- `SpiderIntelligenceService.search_spider_data(query)`
- `SpiderIntelligenceService.get_trending_topics()`
- Web search via Serper API

---

## Testing Checklist for Phase 2

After implementing each agent:

- [ ] Agent can be instantiated
- [ ] Agent has correct tools (and ONLY those tools)
- [ ] Agent.execute() works
- [ ] AgentRouter.route() works with new agent
- [ ] Agent cannot access tools from other domains

---

## What NOT To Do Yet

- Do NOT modify Personal Assistant (Phase 4)
- Do NOT modify frontend (Phase 5)
- Do NOT remove old code (Phase 6)

Focus on creating all agents and verifying isolation.

---

## Full Implementation Plan

| Phase | Focus | Status |
|-------|-------|--------|
| **1** | Base agent + ImageAgent + Router | **COMPLETE** |
| **2** | All creation/editing/research agents | **THIS SESSION** |
| 3 | Super Platform Coordinator integration | Pending |
| 4 | Personal Assistant modification | Pending |
| 5 | Frontend updates | Pending |
| 6 | Testing & cleanup | Pending |

---

## Quick Reference

```bash
# Start servers
make start
make celery

# Test new agents
python manage.py shell
>>> from core.agents import VideoAgent, AudioAgent
>>> from core.agent_router import AgentRouter
>>> router = AgentRouter()
>>> router.is_valid_agent("VideoAgent")
```

---

## Platform Stats

| Metric | Count |
|--------|-------|
| Total Spiders | 70 |
| Real Data Sources | 24 |
| Agents | 22 (+ 13 new clean agents) |
| Sci-Fi Features | 15 |
| Development Sessions | 268 |

---

**GOAL:** Create all specialized agents (video, audio, 3D, editing, research, orchestration) with isolated tool sets. Each agent must be unable to access tools from other domains.
