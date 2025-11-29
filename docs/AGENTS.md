# Agent Reference

**Last Updated:** Session 273 (November 29, 2025)

---

## Overview

The platform uses a **Clean Agent Architecture** where each agent is specialized with isolated tools. Agents cannot call each other's tools directly - they must delegate through the WorkflowAgent.

---

## Clean Architecture Agents (9)

### PersonalAssistantAgent

**Purpose:** Traffic cop - routes requests to specialized agents

**Location:** `core/agents/personal_assistant_agent.py`

**Tools:**
- `delegate_to_agent` - Send task to another agent

**Behavior:**
- Questions → Answer directly (no delegation)
- Creation requests → Delegate to ImageAgent/VideoAgent/etc.
- Research requests → Delegate to ResearchAgent
- Complex multi-step → Delegate to WorkflowAgent

**Intent Detection Keywords:**
```python
'ImageAgent': ['logo', 'banner', 'image', 'picture', 'illustration', 'icon', 'graphic']
'VideoAgent': ['video', 'animation', 'clip', 'movie', 'footage']
'AudioAgent': ['voice', 'speech', 'audio', 'sound', 'narration', 'voiceover']
'ResearchAgent': ['search', 'find', 'research', 'trending', 'what is', 'hot in']
'WorkflowAgent': ['research and create', 'find and make', 'package']
```

---

### ImageAgent

**Purpose:** Image generation ONLY

**Location:** `core/agents/image_agent.py`

**Tools:**
- `generate_image` - Create new images

**Parameters:**
```python
{
    "prompt": "A cyberpunk cityscape",
    "count": 3,
    "style": "cyberpunk",
    "quality": "sdxl"  # core, sdxl, sd3, ultra
}
```

**Cannot Access:** Video, audio, 3D, research tools

---

### VideoAgent

**Purpose:** Video generation ONLY

**Location:** `core/agents/video_agent.py`

**Tools:**
- `generate_video` - Text-to-video
- `animate_image` - Image-to-video
- `extend_video` - Extend existing video
- `chain_videos` - Concatenate clips

**Parameters:**
```python
{
    "prompt": "A sunset over the ocean",
    "duration": 5,
    "source_image_id": 123  # Optional for animate_image
}
```

**Cannot Access:** Image generation, audio, 3D, research tools

---

### AudioAgent

**Purpose:** Audio generation ONLY

**Location:** `core/agents/audio_agent.py`

**Tools:**
- `generate_voice` - Text-to-speech
- `generate_sfx` - Sound effects
- `add_voiceover` - Add narration to video

**Parameters:**
```python
{
    "text": "Welcome to our platform",
    "voice": "alloy",
    "video_id": 456  # For add_voiceover
}
```

**Cannot Access:** Image, video generation, 3D, research tools

---

### ThreeDAgent

**Purpose:** 3D generation ONLY

**Location:** `core/agents/three_d_agent.py`

**Tools:**
- `convert_to_3d` - Image to 3D model
- `generate_3d_scene` - Create 3D scenes

**Parameters:**
```python
{
    "image_id": 123,
    "output_format": "glb"  # glb, obj, gltf
}
```

**Cannot Access:** Image, video, audio, research tools

---

### ImageEditingAgent

**Purpose:** Image editing ONLY

**Location:** `core/agents/image_editing_agent.py`

**Tools:**
- `upscale` - 4x resolution increase
- `remove_background` - Transparent PNG
- `create_variations` - Similar images
- `recolor` - Change object colors
- `search_replace` - Replace objects

**Parameters:**
```python
{
    "image_id": 123,
    "operation": "upscale"
}
```

**Cannot Access:** Creation tools (image/video/audio generation)

---

### VideoEditingAgent

**Purpose:** Video editing ONLY

**Location:** `core/agents/video_editing_agent.py`

**Tools:**
- `trim` - Cut video
- `add_text` - Overlay text
- `add_effects` - Visual effects
- `extract_frame` - Get still image
- `concatenate` - Join videos
- `speed_change` - Adjust playback speed

**Parameters:**
```python
{
    "video_id": 456,
    "operation": "trim",
    "start_time": 0,
    "end_time": 5
}
```

**Cannot Access:** Creation tools

---

### ResearchAgent

**Purpose:** Web search + spider network ONLY

**Location:** `core/agents/research_agent.py`

**Tools:**
- `web_search` - Search the web (Serper API)
- `spider_query` - Query spider network data
- `analyze_trends` - Get trending topics

**Parameters:**
```python
{
    "query": "AI trends 2025",
    "category": "tech",  # tech, financial, jobs, creative
    "topic_filter": "ai",  # ai, web, security, cloud, design
    "hours": 72,
    "limit": 20
}
```

**Data Sources:**
- 70 spiders across 24 real sources
- SpiderIntelligenceService for trend analysis

**Cannot Access:** Any creation or editing tools

---

### WorkflowAgent

**Purpose:** Multi-step orchestration

**Location:** `core/agents/workflow_agent.py`

**Tools:**
- `delegate_to_agent` - Call other agents in sequence

**Workflow Examples:**
```python
# Research and create workflow
Step 1: delegate_to_agent("ResearchAgent", "Find AI trends")
Step 2: Analyze research results
Step 3: delegate_to_agent("ImageAgent", "Create logos based on trends")

# Brand package workflow
Step 1: Research brand aesthetics
Step 2: Generate logo options
Step 3: Create color palette
Step 4: Generate social media banners
```

**Special Powers:** Can orchestrate any other agent

---

## Legacy Agent Ecosystem (22 Agents)

These agents exist in `agents/` directory and are used by the legacy system:

### Generation Agents
- `CreationAgent` - Image generation
- `TrainedCreationAgent` - LoRA-based generation
- `VideoAgent` - Video operations
- `AudioAgent` - Voice/audio
- `3DGenerationAgent` - 3D models

### Research & Analysis
- `ResearchAgent` - Web search + spiders
- `TrendAnalysisAgent` - Trend detection

### Strategy Agents (Session 241)
- `ContentStrategyAgent` - Content recommendations
- `SEOOptimizerAgent` - Hashtags, metadata
- `BrandIdentityAgent` - Brand consistency
- `SocialMediaAgent` - Platform-specific content
- `CreativeDirectorAgent` - High-level direction

### Executive Agents
- `CTOAgent` - Technical decisions
- `COOAgent` - Operations
- `CFOAgent` - Financial strategy
- `HRAgent` - Team coordination
- `MeetingCoordinatorAgent` - Meeting management

### Specialized
- `WorkflowOrchestrationAgent` - Complex workflows
- `OpportunityScoringAgent` - Score opportunities
- `PromptEngineeringAgent` - Prompt optimization
- `DataAnalystAgent` - Data analysis
- `MemoryIsolationAgent` - Memory namespace management

---

## Advisor Network (25 Legendary Advisors)

**Location:** `advisors/registry.py`

Advisors provide expertise for complex decisions:

### Investment/Finance
- Warren Buffett - Value investing
- Charlie Munger - Mental models
- Ray Dalio - Macro economics
- Cathie Wood - Disruptive innovation
- Peter Lynch - Growth investing
- Howard Marks - Risk management

### Tech/Innovation
- Elon Musk - First principles
- Steve Jobs - Design/UX
- Jeff Bezos - Customer obsession
- Reid Hoffman - Network effects
- Marc Andreessen - Software trends
- Paul Graham - Startup wisdom

### Creative
- Kanye West - Creative boldness
- David Ogilvy - Advertising
- Seth Godin - Marketing

### Plus 10 more specialists...

---

## Agent Configuration

### Base Agent Class

```python
from core.agents.base_agent import BaseAgent, AgentResult

class MyAgent(BaseAgent):
    name = "MyAgent"

    system_prompt = """You are MyAgent. You do X.

    You ONLY have access to these tools:
    - tool_1: Description
    - tool_2: Description

    You CANNOT:
    - Do Y (that's OtherAgent's job)
    - Do Z (that's AnotherAgent's job)
    """

    tools = [
        {
            "type": "function",
            "function": {
                "name": "tool_1",
                "description": "...",
                "parameters": {...}
            }
        }
    ]

    def execute(self, task, context, scifi_context, spider_context):
        # Agent logic here
        return AgentResult(
            success=True,
            message="Task completed",
            data={...},
            agent_name=self.name
        )
```

### TimeTravelMixin

All agents inherit decision tracking:

```python
class MyAgent(BaseAgent, TimeTravelMixin):
    def execute(self, task, context, scifi_context, spider_context):
        with self.time_travel_session("task_type", task):
            self.record_decision(
                decision_type="tool_selection",
                action="Calling tool_1",
                reasoning="Because X",
                confidence=0.95
            )

            result = self._execute_tool_call("tool_1", {...})

            self.mark_decision_outcome(
                success=result['success'],
                result_summary="..."
            )
```

---

## Agent Router

**Location:** `core/agent_router.py`

Deterministic routing - no LLM needed:

```python
class AgentRouter:
    AGENT_MAP = {
        "ImageAgent": ImageAgent,
        "VideoAgent": VideoAgent,
        "AudioAgent": AudioAgent,
        "ThreeDAgent": ThreeDAgent,
        "ImageEditingAgent": ImageEditingAgent,
        "VideoEditingAgent": VideoEditingAgent,
        "ResearchAgent": ResearchAgent,
        "WorkflowAgent": WorkflowAgent,
    }

    def route(self, agent_name: str, task: str, context: dict) -> AgentResult:
        agent_class = self.AGENT_MAP.get(agent_name)

        # Inject context
        scifi_context = SciFiIntegrationService.get_context(agent_name)
        spider_context = SpiderIntelligenceService.get_insights_for_prompt(task)

        agent = agent_class()
        return agent.execute(task, context, scifi_context, spider_context)
```

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
- [SPIDERS.md](SPIDERS.md) - Spider network
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - Sci-fi features
