# Platform Architecture

**Last Updated:** Session 273 (November 29, 2025)

---

## Overview

The AI Content Studio is a Django-based platform that combines AI content creation with real-time intelligence gathering. The architecture follows a **layered approach** where specialized agents handle specific tasks, coordinated by a central brain.

---

## Architecture Diagram

```
User Request
    |
    v
+----------------------------------------------------------+
|                 SUPER PLATFORM COORDINATOR                |
|                                                           |
|  +------------------+  +------------------+               |
|  | QueryClassifier  |  | ContextAggregator|               |
|  | (Intent detect)  |  | (Spider+Memory)  |               |
|  +------------------+  +------------------+               |
|                                                           |
|  +------------------+  +------------------+               |
|  | PromptBuilder    |  | AgentRouter      |               |
|  | (Dynamic prompts)|  | (Deterministic)  |               |
|  +------------------+  +------------------+               |
+----------------------------------------------------------+
    |
    v
+----------------------------------------------------------+
|               PERSONAL ASSISTANT AGENT                    |
|                                                           |
|  Role: Traffic cop - routes to specialized agents         |
|                                                           |
|  Question? -> Answer directly (no delegation)             |
|  Creation? -> Delegate to ImageAgent/VideoAgent/etc.      |
|  Research? -> Delegate to ResearchAgent                   |
|  Complex?  -> Delegate to WorkflowAgent                   |
+----------------------------------------------------------+
    |
    +------------------+------------------+------------------+
    |                  |                  |                  |
    v                  v                  v                  v
+----------+    +----------+    +----------+    +----------+
| Image    |    | Video    |    | Audio    |    | Research |
| Agent    |    | Agent    |    | Agent    |    | Agent    |
+----------+    +----------+    +----------+    +----------+
    |                  |                  |                  |
    v                  v                  v                  v
+----------+    +----------+    +----------+    +----------+
|Stability |    | Runway   |    |ElevenLabs|    | Spider   |
| AI API   |    | ML API   |    | API      |    | Network  |
+----------+    +----------+    +----------+    +----------+
```

---

## Layer 1: Super Platform Coordinator

**Location:** `core/super_platform/`

The unified brain that orchestrates everything.

### Components

| Component | File | Purpose |
|-----------|------|---------|
| SuperPlatformCoordinator | `coordinator.py` | Main entry point |
| QueryClassifier | `query_classifier.py` | Detect user intent |
| ContextAggregator | `context_aggregator.py` | Gather spider data, memories, mood |
| DynamicPromptBuilder | `prompt_builder.py` | Build agent-specific prompts |

### Query Types
- `QUESTION` - User asking for information
- `CREATION` - User wants content generated
- `EDITING` - User wants to modify existing content
- `RESEARCH` - User wants trend/market data
- `WORKFLOW` - Multi-step complex request

---

## Layer 2: Clean Agent Architecture

**Location:** `core/agents/`

Each agent is specialized with isolated tools - cannot call other agents' tools.

### Agent Registry

| Agent | Tools | Cannot Access |
|-------|-------|---------------|
| PersonalAssistantAgent | delegate_to_agent | Any creation tools |
| ImageAgent | generate_image | Video, audio, 3D |
| VideoAgent | generate_video, animate_image | Image, audio, 3D |
| AudioAgent | generate_voice, generate_sfx | Image, video, 3D |
| ThreeDAgent | convert_to_3d | Image, video, audio |
| ImageEditingAgent | upscale, remove_bg, recolor | Creation tools |
| VideoEditingAgent | trim, add_text, effects | Creation tools |
| ResearchAgent | web_search, spider_query | Creation tools |
| WorkflowAgent | delegate_to_agent | Direct API calls |

### Base Agent Class

**Location:** `core/agents/base_agent.py`

```python
class BaseAgent(ABC):
    name: str
    system_prompt: str
    tools: List[Dict]

    def execute(self, task, context, scifi_context, spider_context) -> AgentResult
    def _call_openai(self, prompt) -> Dict  # GPT-4o-mini
    def _execute_tool_call(self, tool_name, arguments) -> Dict
```

All agents inherit `TimeTravelMixin` for decision replay.

---

## Layer 3: Spider Intelligence

**Location:** `core/services/spider_intelligence.py`

Real-time data collection from 70 spiders across 24 sources.

### Spider Categories

| Category | Count | Sources |
|----------|-------|---------|
| Tech | 9 | HackerNews, TechCrunch, DevTo, Wired, etc. |
| Financial | 8 | CoinGecko, Yahoo Finance |
| Jobs | 7 | RemoteOK, WeWorkRemotely, Adzuna |
| Creative | 5 | Dribbble, Behance, Unsplash |
| Community | 1 | Reddit (20+ subreddits) |
| + 15 more... | | |

### SpiderIntelligenceService Methods

```python
service = SpiderIntelligenceService()

# Get trending topics
service.get_trending_topics(hours=24, limit=10)

# Get tech trends with topic filter
service.get_tech_trends(hours=72, limit=15, topic_filter='ai')
# topic_filter options: 'ai', 'web', 'security', 'cloud', 'design'

# Search spider data
service.search_spider_data(query="machine learning", category="tech")

# Get market insights
service.get_market_insights()  # Crypto, stocks

# Get job market
service.get_job_market_summary()
```

---

## Layer 4: Sci-Fi Features

**Location:** `core/models_unified_system.py`

15 advanced AI features that enrich every agent interaction.

### Feature Integration

```
Agent Request
    |
    v
+----------------------------------+
| SciFiIntegrationService          |
|                                  |
| +------------+ +---------------+ |
| | Mood       | | Memory Palace | |
| | (affects   | | (past context)| |
| | behavior)  | |               | |
| +------------+ +---------------+ |
|                                  |
| +------------+ +---------------+ |
| | Evolution  | | Relationships | |
| | (XP/level) | | (allies/rivals| |
| +------------+ +---------------+ |
+----------------------------------+
    |
    v
Enriched Agent Context
```

---

## Layer 5: Tool Execution

### External APIs

| API | Purpose | Key File |
|-----|---------|----------|
| Stability AI | Image generation/editing | `content/image_generation.py` |
| Runway ML | Video generation | `content/video_generation.py` |
| ElevenLabs | Audio/TTS | `content/audio_generation.py` |
| Replicate | 3D generation | `content/threed_generation.py` |
| Serper | Web search | `core/tools/web_search.py` |
| OpenAI | GPT-4o-mini for agents | All agents |

### Backend Wrappers

**Location:** `core/views_image.py` (lines 13815-14435)

```python
_execute_generate_image()      # Stability AI
_execute_generate_video()      # Runway ML
_execute_upscale()             # Stability AI
_execute_remove_background()   # Stability AI
_execute_convert_to_3d()       # Replicate
_execute_generate_voice()      # ElevenLabs
_execute_edit_video()          # FFmpeg
```

---

## Data Flow

### 1. Question Flow (No Creation)
```
User: "What's trending in AI?"
    |
    v
PersonalAssistantAgent._is_question() = True
    |
    v
ResearchAgent.execute()
    |
    v
SpiderIntelligenceService.get_tech_trends(topic_filter='ai')
    |
    v
Return: Trending articles with clickable links
```

### 2. Creation Flow
```
User: "Create a cyberpunk logo"
    |
    v
PersonalAssistantAgent._detect_agent() = "ImageAgent"
    |
    v
AgentRouter.route("ImageAgent", task)
    |
    v
ImageAgent.execute()
    |
    v
_execute_generate_image() -> Stability AI
    |
    v
Return: Generated image + metadata
```

### 3. Workflow Flow
```
User: "Research AI trends and create 3 logos"
    |
    v
PersonalAssistantAgent._detect_agent() = "WorkflowAgent"
    |
    v
WorkflowAgent.execute()
    |
    v
Step 1: delegate_to_agent("ResearchAgent", "AI trends")
Step 2: delegate_to_agent("ImageAgent", "3 logos based on trends")
    |
    v
Return: Research summary + 3 images
```

---

## Key Configuration

### Feature Flag
```python
# Enable clean architecture
USE_CLEAN_AGENT_ARCHITECTURE = os.environ.get('USE_CLEAN_AGENT_ARCHITECTURE', 'False') == 'True'
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...
STABILITY_AI_API_KEY=sk-...
RUNWAY_API_KEY=...
ELEVENLABS_API_KEY=...

# Optional
SERPER_API_KEY=...  # For web search
REPLICATE_API_TOKEN=...  # For 3D
```

---

## Frontend Integration

**Location:** `ai_core/templates/ai_image_studio.html`

### API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/api/super-platform/process/` | Main chat endpoint (clean arch) |
| `/api/super-platform/status/` | System status |
| `/api/assistant/chat/` | Legacy endpoint |

### Response Format (Clean Architecture)
```json
{
  "success": true,
  "response": "Created 3 cyberpunk logos",
  "execution_mode": "agent",
  "agents_used": ["ImageAgent"],
  "artifacts": [
    {"type": "image", "data": {...}, "thumbnail": "..."}
  ],
  "execution_time_ms": 2500,
  "metadata": {
    "clean_architecture": true,
    "decisions_made": 3,
    "tool_calls": [...]
  }
}
```

---

## Database Models

### Core Models
- `ImageHistory` - Generated images
- `VideoHistory` - Generated videos
- `AudioHistory` - Generated audio
- `SpiderData` - Spider-collected data

### Sci-Fi Models
- `AgentMood` - Emotional states
- `AgentMemory` - Memory Palace
- `AgentEvolution` - XP/levels
- `AgentRelationship` - Allies/rivals
- `AgentConversation` - AI-to-AI chat
- `AgentDream` - Idle thoughts
- `AgentPrediction` - Prophecies
- `TimeCapsule` - Future messages

---

## See Also

- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
- [AGENTS.md](AGENTS.md) - Agent reference
- [SPIDERS.md](SPIDERS.md) - Spider network
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - 15 sci-fi features
