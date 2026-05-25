<!-- DOC-POINTER-V1 (Session 1145) -->
> **⚠ Pattern doc with drift warning.** The wrap-model-in-orchestrated-tool-workflow pattern remains central to how PA operates, but specific listed workflows (image-gen focused: `research_and_create_logos`, `brand_identity`, etc.), tool counts ("13 tools"), and model version (GPT-5.1) are stale.
> **Last reviewed for drift labeling:** Session 1145 (2026-05-25)
> **Current truth:** [`docs/topics/personal-assistant.md`](../topics/personal-assistant.md) (current PA deliberation router) + [`docs/topics/agent-system.md`](../topics/agent-system.md) (AGENT_MAP routing + ToolCallRecord) + [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (runtime tool/agent counts).
> **Note:** Current multi-agent orchestration lives in `core/conversation_orchestrator.py`; PA's deliberation routing is in `core/services/unified_pa_entrypoint.py`. The doc's pattern intent is preserved; treat the specific implementation details below as superseded.

# Workflow Orchestration Agent Architecture

**Session 191** - November 25, 2025
**Status:** Implementation in Progress

---

## Problem Statement

### The Issue We Discovered

When testing the "Research modern AI logos and create 3 professional logos" command, GPT-5.1 was calling tools in unexpected order and adding unnecessary tools:

**Expected Workflow:**
```
1. web_search (research)
2. coleadership_agent (executive review)
3. image_generation_agent (create 3 logos)
4. create_project_from_research (organize)
```

**What GPT Actually Did:**
```
1. web_search ✅
2. coleadership_agent ✅
3. image_generation_agent ✅
4. character_training_agent ❌ (not requested!)
5. audio_generation_agent ❌ (not requested!)
```

**Root Cause:** GPT-5.1 has access to ALL 13 tools and decides to "be helpful" by calling extra tools it thinks are useful, ignoring our system prompt instructions.

---

## Solution: Workflow Orchestration Agent

### Core Concept

Instead of GPT calling individual tools in sequence (which it can mess up), GPT calls **ONE workflow orchestration agent** that internally executes the correct steps in the correct order.

```
BEFORE (Current - Broken):
┌──────────────────────────────────────────────────────────────┐
│ GPT-5.1 sees ALL 13 tools, calls them in whatever order     │
│ it wants, adds "helpful" extra tools we didn't ask for      │
└──────────────────────────────────────────────────────────────┘

AFTER (New - Controlled):
┌──────────────────────────────────────────────────────────────┐
│ GPT-5.1 detects workflow type, calls ONE orchestration agent │
│ The agent internally executes steps in hardcoded order       │
│ GPT CANNOT deviate or add extra steps                        │
└──────────────────────────────────────────────────────────────┘
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    GPT-5.1 (AI Assistant)                        │
│  - Detects user intent                                          │
│  - Chooses: simple tool OR workflow agent                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
            ┌────────────────┴─────────────────┐
            │                                  │
            ▼                                  ▼
┌───────────────────────┐          ┌─────────────────────────────┐
│ Simple Tool Calls      │          │ Workflow Orchestration Agent │
│ (single operation)     │          │ (multi-step workflows)       │
│                        │          │                              │
│ Examples:              │          │ Predefined Workflows:        │
│ • "upscale image 3"    │          │ • research_and_create_logos  │
│ • "generate 1 logo"    │          │ • research_and_create_images │
│ • "remove background"  │          │ • research_and_create_video  │
│ • "make image talk"    │          │ • logo_package               │
│                        │          │ • brand_identity             │
│ Uses individual agents │          │                              │
└───────────────────────┘          │ Internally calls agents in   │
                                   │ FIXED order - no deviation!  │
                                   └─────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: research_and_create_logos (Session 191)

**Workflow Steps:**
```python
RESEARCH_AND_CREATE_LOGOS = [
    {
        'step': 1,
        'name': 'research',
        'agent': 'web_search',
        'description': 'Research the topic',
        'params_template': {
            'query': '{topic} logo trends {year} minimalist bold contemporary'
        }
    },
    {
        'step': 2,
        'name': 'executive_review',
        'agent': 'coleadership_agent',
        'description': 'Get executive team direction',
        'params_template': {
            'question': 'Based on the research about {topic}, what creative direction should we take for {count} professional logos?',
            'context': 'Research findings: {research_summary}'
        }
    },
    {
        'step': 3,
        'name': 'create_images',
        'agent': 'image_generation_agent',
        'description': 'Generate the logos',
        'params_template': {
            'prompt': 'single professional {topic} logo, minimalist, bold, {creative_direction}',
            'count': '{count}'
        }
    },
    {
        'step': 4,
        'name': 'create_project',
        'agent': 'create_project_from_research',
        'description': 'Organize into project',
        'params_template': {
            'project_name': '{topic} Logo Designs',
            'research_summary': '{research_summary}',
            'image_ids': '{generated_image_ids}'
        }
    }
]
```

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `agents/workflow_orchestration_agent.py` | CREATE | Main agent class (~350 lines) |
| `core/assistant/tool_definitions.py` | MODIFY | Add workflow_orchestration_agent definition |
| `core/assistant/constants.py` | MODIFY | Add workflow type constants |
| `core/views_image.py` | MODIFY | Add handler for workflow_orchestration_agent |
| `ai_core/templates/ai_image_studio.html` | MODIFY | Frontend handler for workflow progress |

---

## Detailed Implementation

### 1. WorkflowOrchestrationAgent Class

**Location:** `agents/workflow_orchestration_agent.py`

```python
"""
Workflow Orchestration Agent - Session 191

Manages multi-step creative workflows by executing agents in a fixed order.
This ensures GPT cannot deviate from the intended workflow or add extra steps.

Architecture:
    GPT detects workflow type → calls this agent → agent executes steps internally
"""

from agents.base_agent import BaseContentAgent
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class WorkflowOrchestrationAgent(BaseContentAgent):
    """
    Orchestrates multi-step creative workflows.

    Key Principle: GPT calls this ONE agent, and the agent internally
    executes the correct steps in the correct order. GPT cannot
    deviate or add extra steps.
    """

    agent_name = "WorkflowOrchestrationAgent"
    specialization = "workflow_orchestration"

    # Workflow definitions - HARDCODED order, no deviation allowed
    WORKFLOWS = {
        'research_and_create_logos': {
            'description': 'Research topic and create professional logos',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get executive team direction'
                },
                {
                    'step': 3,
                    'name': 'create_images',
                    'agent': 'image_generation_agent',
                    'description': 'Generate the logos'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into project'
                }
            ]
        }
        # Future workflows will be added here
    }

    def execute(self, workflow: str, **params) -> Dict[str, Any]:
        """
        Execute a complete workflow.

        Args:
            workflow: Workflow type (e.g., 'research_and_create_logos')
            **params: Workflow-specific parameters (topic, count, etc.)

        Returns:
            Complete result with outputs from all steps
        """
        # Implementation details...
```

### 2. Tool Definition

**Add to:** `core/assistant/tool_definitions.py`

```python
def _get_workflow_orchestration_agent_definition() -> Dict:
    """
    Workflow orchestration agent for multi-step creative workflows.

    Session 191: This agent ensures GPT cannot deviate from intended workflows.
    Instead of calling multiple tools, GPT calls this ONE agent which
    internally executes the correct steps in order.
    """
    return {
        "type": "function",
        "name": "workflow_orchestration_agent",
        "description": """IMPORTANT: Use this agent for ANY multi-step workflow that involves RESEARCH + CREATION.

When user says things like:
- "Research X and create Y logos/images/videos"
- "Look up trends and make content"
- "Find out about X then create Y"

Call this agent with the appropriate workflow type. The agent will internally execute all required steps in the correct order (research → review → create → organize).

DO NOT try to call web_search, coleadership_agent, image_generation_agent separately for these requests. Use this workflow agent instead.

For SIMPLE single-step requests (just "create a logo", "upscale image 3"), use the individual agents directly.""",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow": {
                    "type": "string",
                    "enum": ["research_and_create_logos"],
                    "description": "Workflow type: 'research_and_create_logos' for researching a topic and creating professional logos"
                },
                "topic": {
                    "type": "string",
                    "description": "The research topic (e.g., 'modern AI company', 'tech startup', 'coffee shop')"
                },
                "count": {
                    "type": "integer",
                    "default": 3,
                    "description": "Number of logos/images to create (1-5)"
                },
                "style_preferences": {
                    "type": "string",
                    "description": "Optional style preferences (e.g., 'minimalist', 'bold colors', 'geometric')"
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional existing project ID to add content to"
                }
            },
            "required": ["workflow", "topic"]
        }
    }
```

### 3. Backend Handler

**Add to:** `core/views_image.py` in `execute_tool()` function

```python
elif tool_name == 'workflow_orchestration_agent':
    from agents.workflow_orchestration_agent import WorkflowOrchestrationAgent

    agent = WorkflowOrchestrationAgent(
        user=request.user,
        project_id=parameters.get('project_id')
    )

    result = agent.execute(
        workflow=parameters.get('workflow'),
        topic=parameters.get('topic'),
        count=parameters.get('count', 3),
        style_preferences=parameters.get('style_preferences', '')
    )
```

### 4. Frontend Handler

**Add to:** `ai_image_studio.html` in `formatToolResults()`

```javascript
} else if (result.tool === 'workflow_orchestration_agent') {
    // Workflow Orchestration Agent - Multi-step workflow results
    message += `🔄 **Workflow Complete: ${result.result.workflow}**\n\n`;

    // Show each step's result
    if (result.result.steps) {
        result.result.steps.forEach((step, idx) => {
            const emoji = step.success ? '✅' : '❌';
            message += `${emoji} **Step ${idx + 1}: ${step.name}**\n`;
            if (step.summary) {
                message += `   ${step.summary}\n`;
            }
            message += `\n`;
        });
    }

    // Show final summary
    if (result.result.summary) {
        message += `📋 **Summary:** ${result.result.summary}\n\n`;
    }

    // Show created content
    if (result.result.image_ids && result.result.image_ids.length > 0) {
        message += `🖼️ **Created ${result.result.image_ids.length} images**\n`;
    }

    if (result.result.project_id) {
        message += `📁 **Project created:** ${result.result.project_name}\n`;
    }
}
```

---

## Execution Flow

### User Request → Result

```
1. User: "Research modern AI company logo trends and create 3 professional logos"

2. GPT-5.1 detects:
   - Keywords: "research" + "create" + "logos"
   - This is a multi-step workflow
   - Workflow type: research_and_create_logos

3. GPT calls:
   workflow_orchestration_agent(
       workflow="research_and_create_logos",
       topic="modern AI company",
       count=3
   )

4. WorkflowOrchestrationAgent executes (internally, in order):

   Step 1: web_search
   └─ Query: "modern AI company logo trends 2025 minimalist bold contemporary"
   └─ Returns: Research findings

   Step 2: coleadership_agent
   └─ Question: "Based on research about modern AI company logos, what direction for 3 logos?"
   └─ Returns: Executive team recommendations

   Step 3: image_generation_agent
   └─ Prompt: "single professional modern AI company logo, minimalist, bold, [recommendations]"
   └─ Count: 3
   └─ Returns: 3 image IDs

   Step 4: create_project_from_research
   └─ Name: "Modern AI Company Logo Designs"
   └─ Images: [id1, id2, id3]
   └─ Returns: Project created

5. Agent returns complete result:
   {
       success: true,
       workflow: "research_and_create_logos",
       steps: [
           {name: "research", success: true, summary: "Found 5 trend articles"},
           {name: "executive_review", success: true, summary: "Team recommends geometric style"},
           {name: "create_images", success: true, summary: "Created 3 logos"},
           {name: "create_project", success: true, summary: "Project organized"}
       ],
       image_ids: ["uuid1", "uuid2", "uuid3"],
       project_id: "project-uuid",
       project_name: "Modern AI Company Logo Designs"
   }

6. Frontend displays:
   - Research findings
   - Executive team opinions
   - 3 generated logo images
   - Project creation confirmation
```

---

## Testing Checklist

After implementation, verify:

- [ ] GPT correctly detects "research and create" requests
- [ ] GPT calls `workflow_orchestration_agent` (not individual tools)
- [ ] Workflow executes steps in correct order
- [ ] No extra steps are added (no character_training, no audio)
- [ ] Research results display in chat
- [ ] Executive team opinions display in chat
- [ ] 3 logo images are generated (one logo per image)
- [ ] Project is created with all content
- [ ] Frontend shows workflow progress/completion

---

## Future Workflows (Phase 2+)

| Workflow | Steps | Trigger Keywords |
|----------|-------|------------------|
| `research_and_create_images` | search → review → images → project | "research X create images" |
| `research_and_create_video` | search → review → video → project | "research X create video" |
| `logo_package` | images → animate → project | "create logo package" |
| `brand_identity` | search → review → logos → colors → fonts → project | "create brand identity" |
| `talking_character` | image → tts → animate → lipsync | "make character talk" |

---

## Key Decisions

1. **Single tool call for multi-step workflows** - GPT calls ONE agent, not multiple
2. **Hardcoded step order** - No deviation possible
3. **Individual tools still available** - For simple single-step requests
4. **Progress reporting** - Each step reports back to frontend
5. **Error handling** - If any step fails, workflow stops and reports

---

## Files Changed

| File | Lines Added | Description |
|------|-------------|-------------|
| `agents/workflow_orchestration_agent.py` | ~350 | New agent class |
| `core/assistant/tool_definitions.py` | ~50 | New tool definition |
| `core/assistant/constants.py` | ~10 | Workflow type constants |
| `core/views_image.py` | ~20 | Backend handler |
| `ai_image_studio.html` | ~40 | Frontend handler |

**Total: ~470 lines of new code**

---

## Related Documentation

- [MULTI_AGENT_ARCHITECTURE.md](./MULTI_AGENT_ARCHITECTURE.md) - Overall agent architecture
- [SYSTEM_ARCHITECTURE_MAP.md](./SYSTEM_ARCHITECTURE_MAP.md) - System overview
- Session 189-190 notes - Previous workflow order attempts

---

**Ready for implementation!**
