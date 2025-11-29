# Session 269: Clean Architecture Implementation - Phase 3

**Date:** November 29, 2025
**Previous Session:** 268 (Phases 1 & 2 Complete - Full Agent Ecosystem)
**Session Type:** Major Architecture Overhaul
**Status:** READY TO IMPLEMENT

---

## Phases 1 & 2 Complete!

Session 268 successfully implemented:

### Phase 1 - Foundation
| File | Purpose | Status |
|------|---------|--------|
| `core/agents/__init__.py` | Package exports | DONE |
| `core/agents/base_agent.py` | Abstract base with TimeTravelMixin | DONE |
| `core/agents/image_agent.py` | Image generation ONLY | DONE |
| `core/agent_router.py` | Deterministic routing | DONE |
| `core/settings.py` | `USE_CLEAN_AGENT_ARCHITECTURE` flag | DONE |

### Phase 2 - Complete Agent Ecosystem
| Agent | Tools | Status |
|-------|-------|--------|
| `ImageAgent` | generate_image | DONE |
| `VideoAgent` | generate_video, animate_image, extend_video, chain_videos | DONE |
| `AudioAgent` | generate_voice, generate_sfx, add_voiceover | DONE |
| `ThreeDAgent` | convert_to_3d, generate_3d_scene | DONE |
| `ImageEditingAgent` | upscale, remove_background, create_variations, recolor, search_replace | DONE |
| `VideoEditingAgent` | trim, add_text, add_effects, extract_frame, concatenate, speed_change | DONE |
| `ResearchAgent` | web_search, spider_query, analyze_trends | DONE |
| `WorkflowAgent` | delegate_to_agent (can call other agents) | DONE |

All tests pass:
- 8 agents instantiated correctly
- Tool isolation verified (ImageAgent can't access video tools, etc.)
- AgentRouter routes to all 8 agents
- Context injection (SciFi + Spider) working
- WorkflowAgent can delegate to 7 other agents

---

## Phase 3 Tasks (This Session)

### Goal: Integrate with Super Platform Coordinator

The Super Platform Coordinator (`core/super_platform/coordinator.py`) needs to use the new agent architecture instead of the old tool-based system.

### 1. Create Personal Assistant Agent

This is the "traffic cop" that decides which agent to delegate to:

```python
# core/agents/personal_assistant_agent.py
class PersonalAssistantAgent(BaseAgent):
    """
    The main entry point for user requests.

    This agent:
    1. Receives user messages
    2. Classifies intent (question vs. creation request)
    3. Delegates to appropriate specialized agent
    4. Returns synthesized response
    """

    tools = [
        {
            "function": {
                "name": "delegate_to_agent",
                "description": "Delegate task to a specialized agent",
                "parameters": {
                    "properties": {
                        "agent_name": {
                            "enum": [
                                "ImageAgent", "VideoAgent", "AudioAgent", "ThreeDAgent",
                                "ImageEditingAgent", "VideoEditingAgent",
                                "ResearchAgent", "WorkflowAgent"
                            ]
                        },
                        "task": {"type": "string"},
                        "context": {"type": "object"}
                    }
                }
            }
        }
    ]
```

### 2. Update SuperPlatformCoordinator

Modify to use AgentRouter when feature flag is enabled:

```python
# core/super_platform/coordinator.py

def process_request(self, message, user):
    if settings.USE_CLEAN_AGENT_ARCHITECTURE:
        # Use new layered architecture
        return self._process_with_agents(message, user)
    else:
        # Use old tool-based architecture
        return self._process_legacy(message, user)

def _process_with_agents(self, message, user):
    # 1. Classify intent
    intent = self.query_classifier.classify(message)

    # 2. If question, answer directly
    if intent.is_question:
        return self._answer_question(message)

    # 3. Route to appropriate agent
    router = AgentRouter(user=user)
    agent_name = self._determine_agent(intent)
    result = router.route(agent_name, message)

    return result
```

### 3. Intent-to-Agent Mapping

Create mapping logic:

| Intent | Agent |
|--------|-------|
| create image/logo/banner | ImageAgent |
| create video/animate | VideoAgent |
| create audio/voiceover | AudioAgent |
| create 3D model | ThreeDAgent |
| upscale/edit image | ImageEditingAgent |
| trim/edit video | VideoEditingAgent |
| search/research/find | ResearchAgent |
| multi-step workflow | WorkflowAgent |
| question (no creation) | No agent (direct GPT response) |

### 4. Testing Checklist

- [ ] PersonalAssistantAgent can classify intents
- [ ] Correct agent selected for each intent type
- [ ] Feature flag controls architecture choice
- [ ] End-to-end test: "create a logo" → ImageAgent
- [ ] End-to-end test: "what is trending" → ResearchAgent or direct answer
- [ ] End-to-end test: "research trends and create 3 logos" → WorkflowAgent

---

## What NOT To Do Yet

- Do NOT modify frontend (Phase 5)
- Do NOT remove old code (Phase 6)

Focus on integrating the agent router with the Super Platform Coordinator.

---

## Full Implementation Plan

| Phase | Focus | Status |
|-------|-------|--------|
| **1** | Base agent + ImageAgent + Router | **COMPLETE** |
| **2** | All creation/editing/research agents | **COMPLETE** |
| **3** | Super Platform Coordinator integration | **THIS SESSION** |
| 4 | Personal Assistant modification | Next |
| 5 | Frontend updates | Pending |
| 6 | Testing & cleanup | Pending |

---

## Quick Reference

```bash
# Start servers
make start
make celery

# Test the agents
python manage.py shell
>>> from core.agents import ImageAgent, VideoAgent, WorkflowAgent
>>> from core.agent_router import AgentRouter
>>> router = AgentRouter()
>>> router.get_available_agents()

# Enable new architecture (for testing)
export USE_CLEAN_AGENT_ARCHITECTURE=True
```

---

## Key Files

| File | Purpose |
|------|---------|
| `core/agents/*.py` | All 8 specialized agents |
| `core/agent_router.py` | Deterministic routing |
| `core/super_platform/coordinator.py` | Super Platform (to modify) |
| `core/super_platform/query_classifier.py` | Intent classification |
| `core/settings.py` | Feature flag |

---

## Platform Stats

| Metric | Count |
|--------|-------|
| Total Spiders | 70 |
| Real Data Sources | 24 |
| Clean Agents | 8 |
| Total Tools | 25 (isolated per agent) |
| Development Sessions | 268 |

---

**GOAL:** Integrate the new agent architecture with Super Platform Coordinator. When `USE_CLEAN_AGENT_ARCHITECTURE=True`, requests should be routed through the AgentRouter to specialized agents instead of using the legacy tool-based system.
