# Session 268: Clean Architecture Implementation - Phase 1

**Date:** November 29, 2025
**Previous Session:** 267 (Clean Architecture Proposal)
**Session Type:** Major Architecture Overhaul
**Status:** READY TO IMPLEMENT

---

## CRITICAL CONTEXT: Why We're Doing This

### The Problem (Session 267)
The Personal Assistant has 14+ tools available and GPT picks the wrong one:
- "Create a cyberpunk logo" → GPT calls `video_generation_agent` (WRONG!)
- Questions → GPT calls `workflow_orchestration_agent` (WRONG!)
- We tried band-aid fixes (tool descriptions, ordering, safety redirects) - they don't work reliably

### The Root Cause
**The Assistant knows too much.** It sees all tools and makes bad choices.

### The Solution: Layered Architecture
```
User → Personal Assistant → Agent Router → Specialized Agents → Tools
```

- **Assistant** has ONLY `delegate_to_agent` - cannot misroute
- **Each Agent** has ONLY its domain tools - ImageAgent cannot generate video
- **Router** is deterministic string matching - no GPT guessing

---

## APPROVED ARCHITECTURE

Full proposal: `docs/SESSION_267_CLEAN_ARCHITECTURE_PROPOSAL.md`

### Key Design Decisions:

| Decision | Choice |
|----------|--------|
| Assistant Tools | ONLY: `delegate_to_agent`, `remember_preference`, `recall_memory` |
| Agent Tool Isolation | Each agent sees ONLY its own tools |
| Routing | Deterministic (string match on agent_name), NOT LLM-based |
| Workflow Orchestration | Server-side WorkflowAgent, NOT frontend loop |
| Sci-Fi Integration | All 15 features preserved via SciFiContext injection |
| Spider Integration | SpiderIntelligenceService feeds ContextAggregator |
| Migration | Feature flag `USE_CLEAN_AGENT_ARCHITECTURE` |

---

## Phase 1 Tasks (This Session)

### 1. Create Base Agent Class
```
core/agents/base_agent.py
```
- Abstract base class
- TimeTravelMixin integration
- Standard execute() interface
- Sci-Fi context injection point
- Spider context injection point

### 2. Create ImageAgent (Test Case)
```
core/agents/image_agent.py
```
- System prompt: "You create images. That's all."
- Tools: ONLY `generate_image`, `batch_generate`
- NO video, audio, 3D, or search tools
- Connects to existing Stability AI integration

### 3. Create Agent Router
```
core/agent_router.py
```
- Simple dictionary mapping: `agent_name` → `AgentClass`
- Injects SciFiContext before execution
- Injects SpiderContext before execution
- Returns AgentResult

### 4. Add Feature Flag
```python
# In settings or constants
USE_CLEAN_AGENT_ARCHITECTURE = False  # Start disabled
```

### 5. Test ImageAgent in Isolation
- Direct call to ImageAgent.execute()
- Verify it can ONLY generate images
- Verify sci-fi context is injected
- Verify spider context is injected

---

## Files to Create

```
core/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py       # Abstract base with TimeTravelMixin
│   └── image_agent.py      # Image generation ONLY
├── agent_router.py         # Simple deterministic routing
```

---

## Reference: Existing Code to Leverage

### Image Generation (use this)
```python
# core/views_image.py - _execute_generate_image()
# This is the actual Stability AI integration - ImageAgent should call this
```

### TimeTravelMixin (inherit this)
```python
# agents/time_travel_mixin.py - TimeTravelMixin
# Provides record_decision(), time_travel_session()
```

### SciFi Integration (use this)
```python
# core/super_platform/scifi_integration.py - SciFiIntegrationService
# Provides get_context(agent_name) → SciFiContext
```

### Spider Intelligence (use this)
```python
# core/services/spider_intelligence.py - SpiderIntelligenceService
# Provides get_insights_for_prompt(query) → context dict
```

---

## Implementation Pattern

```python
# core/agents/base_agent.py
from abc import ABC, abstractmethod
from agents.time_travel_mixin import TimeTravelMixin

class BaseAgent(ABC, TimeTravelMixin):
    """Base class for all clean architecture agents."""

    name: str = "BaseAgent"
    system_prompt: str = ""
    tools: list = []

    @abstractmethod
    def execute(self, task: str, context: dict,
                scifi_context: dict, spider_context: dict) -> dict:
        """Execute the agent's task. Must be implemented by subclasses."""
        pass

    def _build_prompt(self, task: str, scifi_context: dict, spider_context: dict) -> str:
        """Build the complete prompt with all context."""
        prompt = self.system_prompt

        # Add mood modifier if available
        if scifi_context.get('mood'):
            prompt += f"\n\nCurrent mood: {scifi_context['mood']['state']}"
            prompt += f"\n{scifi_context['mood']['prompt_modifier']}"

        # Add spider insights if available
        if spider_context.get('trends'):
            prompt += f"\n\nCurrent trends: {spider_context['trends']}"

        prompt += f"\n\nTask: {task}"
        return prompt
```

```python
# core/agents/image_agent.py
from core.agents.base_agent import BaseAgent
from core.views_image import _execute_generate_image

class ImageAgent(BaseAgent):
    """Agent specialized in image generation. Cannot do anything else."""

    name = "ImageAgent"
    system_prompt = """You are ImageAgent, a specialist in creating images.

Your ONLY job is to generate images based on the task given to you.
You have ONE tool: generate_image.

When given a task like "create a cyberpunk logo for a tech startup":
1. Enhance the prompt for better results
2. Call generate_image with appropriate parameters
3. Return the result

You cannot create videos, audio, or anything else. Just images."""

    tools = [
        {
            "type": "function",
            "name": "generate_image",
            "description": "Generate an image from a text prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Text description"},
                    "count": {"type": "integer", "default": 1},
                    "style": {"type": "string"},
                    "size": {"type": "string", "default": "1024x1024"}
                },
                "required": ["prompt"]
            }
        }
    ]

    def execute(self, task: str, context: dict,
                scifi_context: dict, spider_context: dict) -> dict:
        """Generate images based on the task."""
        with self.time_travel_session("image_generation", task):
            # Build prompt with context
            prompt = self._build_prompt(task, scifi_context, spider_context)

            # Call GPT with ONLY image tools
            # ... GPT call here ...

            # Execute the tool call
            # result = _execute_generate_image(user, params, session)

            return result
```

---

## Testing Checklist

After Phase 1 implementation:

- [ ] `ImageAgent` can be instantiated
- [ ] `ImageAgent.execute()` generates images
- [ ] `ImageAgent` has NO access to video tools
- [ ] `AgentRouter.route("ImageAgent", task)` works
- [ ] Sci-Fi context is injected into prompt
- [ ] Spider context is injected into prompt
- [ ] TimeTravelMixin records decisions
- [ ] Feature flag controls old vs new path

---

## What NOT To Do Yet

- Do NOT modify Personal Assistant yet (Phase 4)
- Do NOT modify frontend yet (Phase 5)
- Do NOT create all agents yet (Phase 2)
- Do NOT remove old code yet (Phase 6)

Focus ONLY on Phase 1: base class, ImageAgent, router, feature flag, testing.

---

## Quick Reference Commands

```bash
# Start servers
make start
make celery

# Test ImageAgent directly (after implementation)
python manage.py shell
>>> from core.agents.image_agent import ImageAgent
>>> from core.agent_router import AgentRouter
>>>
>>> agent = ImageAgent()
>>> result = agent.execute("create a cyberpunk logo", {}, {}, {})
>>> print(result)
```

---

## Full Implementation Plan (All Phases)

| Phase | Focus | Status |
|-------|-------|--------|
| **1** | Base agent + ImageAgent + Router | **THIS SESSION** |
| 2 | All creation/editing/research agents | Pending |
| 3 | Super Platform Coordinator integration | Pending |
| 4 | Personal Assistant modification | Pending |
| 5 | Frontend updates | Pending |
| 6 | Testing & cleanup | Pending |

---

## Platform Stats

| Metric | Count |
|--------|-------|
| Total Spiders | 70 |
| Real Data Sources | 24 |
| Agents | 22 |
| Sci-Fi Features | 15 |
| Development Sessions | 267 |

---

**GOAL:** Create the foundation (base agent, ImageAgent, router) that proves the clean architecture pattern works. Test in isolation before proceeding.
