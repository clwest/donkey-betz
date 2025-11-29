# Session 267: Clean Architecture Proposal (Complete)

## User → Assistant → Agent → Tools + Full Ecosystem

**Date:** November 29, 2025
**Status:** PROPOSAL - Requires Review
**Goal:** Eliminate tool routing confusion while preserving all 70 spiders, 22 agents, and 15 sci-fi features

---

## The Problem

The current architecture has the Personal Assistant directly calling GPT with ALL tools available:
- GPT sees 14+ tools and picks the wrong one
- "Create a logo" triggers `video_generation_agent`
- Questions trigger `workflow_orchestration_agent`
- We're adding more and more band-aid fixes

The root cause: **The Assistant knows too much.**

---

## The Solution: Layered Architecture with Full Ecosystem

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                      │
│                         (Web UI / Voice / API)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PERSONAL ASSISTANT                                   │
│                                                                              │
│  Role: Conversation partner, advisor, delegator                              │
│                                                                              │
│  CAN DO:                           │  CANNOT DO:                             │
│  • Answer questions                │  • Generate images (→ ImageAgent)       │
│  • Give advice/recommendations     │  • Generate videos (→ VideoAgent)       │
│  • Remember user preferences       │  • Edit content (→ EditingAgent)        │
│  • Delegate to specialized agents  │  • Search the web (→ ResearchAgent)     │
│                                    │  • ANY direct API calls                 │
│                                                                              │
│  Tools: delegate_to_agent, remember_preference                               │
│  NO CREATION TOOLS                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ delegate_to_agent("ImageAgent", task)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SUPER PLATFORM COORDINATOR                          │
│                        (The Unified Brain - Session 264)                     │
│                                                                              │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────┐                 │
│  │   CLASSIFY  │  │    AGGREGATE    │  │      ROUTE       │                 │
│  │             │  │                 │  │                  │                 │
│  │ QueryType:  │  │ Spider Data     │  │ ExecutionMode:   │                 │
│  │ • QUESTION  │  │ Memories        │  │ • DIRECT         │                 │
│  │ • CREATION  │  │ Agent Mood      │  │ • AGENT          │                 │
│  │ • WORKFLOW  │  │ Relationships   │  │ • WORKFLOW       │                 │
│  │ • ANALYSIS  │  │ User Prefs      │  │ • HIVE_MIND      │                 │
│  │ • MEMORY    │  │ Opportunities   │  │ • MEMORY_RECALL  │                 │
│  │ • COLLAB    │  │ Evolution Stats │  │ • OPPORTUNITY    │                 │
│  └─────────────┘  └─────────────────┘  └──────────────────┘                 │
│                                                                              │
│  Components:                                                                 │
│  • QueryClassifier - Understands intent                                      │
│  • ContextAggregator - Gathers all context                                   │
│  • DynamicPromptBuilder - Builds tailored prompts                            │
│  • AgentRouter - Simple deterministic dispatch                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   IMAGE AGENT   │     │   VIDEO AGENT   │     │  RESEARCH AGENT │
│                 │     │                 │     │                 │
│ Prompt: "You    │     │ Prompt: "You    │     │ Prompt: "You    │
│ create images.  │     │ create videos.  │     │ search the web  │
│ That's all."    │     │ That's all."    │     │ and spiders."   │
│                 │     │                 │     │                 │
│ Tools:          │     │ Tools:          │     │ Tools:          │
│ • generate_image│     │ • generate_video│     │ • web_search    │
│ • batch_generate│     │ • animate_image │     │ • spider_query  │
│                 │     │ • extend_video  │     │ • trend_analysis│
│ NO video tools  │     │ NO image tools  │     │ NO creation     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCI-FI CONTEXT LAYER                               │
│                      (Enriches every agent interaction)                      │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  MOOD SYSTEM │  │MEMORY PALACE │  │  EVOLUTION   │  │ RELATIONSHIPS│    │
│  │              │  │              │  │              │  │              │    │
│  │ 10 moods     │  │ Memory rooms │  │ XP/Levels    │  │ Allies       │    │
│  │ 4 dimensions │  │ Embeddings   │  │ 10 ranks     │  │ Rivals       │    │
│  │ Intensity    │  │ Clustering   │  │ Bonuses      │  │ Teachers     │    │
│  │ Triggers     │  │ Recall       │  │ Prestige     │  │ Students     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  HIVE MIND   │  │CONVERSATIONS │  │    DREAMS    │  │ TIME TRAVEL  │    │
│  │              │  │              │  │              │  │              │    │
│  │ Collective   │  │ AI-to-AI     │  │ Idle thoughts│  │ Decision     │    │
│  │ intelligence │  │ Real-time    │  │ Creative     │  │ replay       │    │
│  │ Multi-agent  │  │ WebSocket    │  │ insights     │  │ Debugging    │    │
│  │ synthesis    │  │ streaming    │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
│  SciFiIntegrationService: Combines all → SciFiContext for prompt building   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SPIDER INTELLIGENCE LAYER                           │
│                          (70 Spiders, 24 Real Sources)                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        SPIDER REGISTRY                               │    │
│  │                                                                      │    │
│  │  20 Categories:                                                      │    │
│  │  Tech(9), Financial(8), Freelance(5), Creative(5), AI Tools(4),     │    │
│  │  Digital Products(5), Content(3), News(4), Design(3), Education(3), │    │
│  │  Legal(4), Innovation(3), Remote Work(2), Sports(2), Market(1),     │    │
│  │  Social(1), Community(1), Visual Trends(1), Jobs(1)                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    SPIDER INTELLIGENCE SERVICE                       │    │
│  │                                                                      │    │
│  │  Methods:                                                            │    │
│  │  • get_trending_topics() - Tags + keywords from all sources          │    │
│  │  • get_tech_trends() - Tech discussions, projects                    │    │
│  │  • get_market_insights() - Crypto/stock prices                       │    │
│  │  • get_job_market_summary() - Remote jobs by category                │    │
│  │  • get_creative_trends() - Design styles, palettes                   │    │
│  │  • search_spider_data() - Full-text search                           │    │
│  │  • get_insights_for_prompt() - Context for AI prompts                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Data Flow: Spider executes → SpiderData model → SpiderIntelligence queries │
│             → ContextAggregator enriches → Agent receives context            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TOOL EXECUTION LAYER                                 │
│                                                                              │
│  External APIs:                    │  Storage:                               │
│  • Stability AI (images)           │  • PostgreSQL (records, history)        │
│  • Runway ML (videos)              │  • Redis (cache, sessions)              │
│  • ElevenLabs (audio)              │  • File system (media files)            │
│  • Serper (web search)             │  • Embeddings (768-dim vectors)         │
│  • Replicate (3D)                  │                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LEARNING & REVENUE LAYER                            │
│                                                                              │
│  ┌─────────────────────────┐    ┌─────────────────────────┐                 │
│  │     LEARNING LOOP       │    │   REVENUE INTEGRATION   │                 │
│  │                         │    │                         │                 │
│  │  Records:               │    │  Tracks:                │                 │
│  │  • What was asked       │    │  • Opportunities        │                 │
│  │  • Which agents used    │    │  • Conversions          │                 │
│  │  • What result was      │    │  • Revenue generated    │                 │
│  │  • Success metrics      │    │  • ROI per agent        │                 │
│  │                         │    │                         │                 │
│  │  Updates agent          │    │  Links spider data      │                 │
│  │  knowledge bases        │    │  to actual income       │                 │
│  └─────────────────────────┘    └─────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## How It Solves Current Problems

### Problem 1: "Create a logo" triggers video_generation_agent
**Solution:** Assistant only has `delegate_to_agent` tool. It delegates to "ImageAgent" for logos. ImageAgent has NO video tools - it literally cannot generate video.

### Problem 2: Questions trigger workflow_orchestration_agent
**Solution:** Assistant can just ANSWER questions. It only delegates when there's actual work to do. No tool = conversation mode.

### Problem 3: Autonomous workflow runs too many iterations
**Solution:** No more frontend workflow loop. Each agent runs once, returns result. If orchestration is needed, WorkflowAgent handles it server-side.

### Problem 4: Complex tool descriptions ignored by GPT
**Solution:** Each agent has minimal, focused tools. ImageAgent sees: `generate_image`. That's it. Can't pick wrong tool when there's only one.

---

## Complete Agent Registry

### Creation Agents (Isolated Tool Sets)

| Agent | System Prompt | Tools | CANNOT Access |
|-------|--------------|-------|---------------|
| **ImageAgent** | "You create images. That's all." | `generate_image`, `batch_generate` | Video, audio, 3D, search |
| **VideoAgent** | "You create videos. That's all." | `generate_video`, `animate_image`, `extend_video`, `chain_clips` | Image, audio, 3D, search |
| **AudioAgent** | "You create audio. That's all." | `generate_voice`, `generate_sfx`, `add_voiceover` | Image, video, 3D, search |
| **ThreeDAgent** | "You create 3D models." | `convert_to_3d`, `generate_3d_scene` | Image, video, audio, search |

### Editing Agents (Isolated Tool Sets)

| Agent | System Prompt | Tools | CANNOT Access |
|-------|--------------|-------|---------------|
| **ImageEditingAgent** | "You modify existing images." | `upscale`, `remove_bg`, `recolor`, `variations`, `search_replace` | Creation tools, video |
| **VideoEditingAgent** | "You modify existing videos." | `trim`, `add_effects`, `add_text`, `concatenate`, `extract_frame` | Creation tools, image |

### Research & Analysis Agents

| Agent | System Prompt | Tools | Special Access |
|-------|--------------|-------|----------------|
| **ResearchAgent** | "You search the web and spider network." | `web_search`, `spider_query`, `trend_analysis` | SpiderIntelligenceService |
| **TrendAnalysisAgent** | "You analyze trends and patterns." | `analyze_trends`, `predict_opportunities` | Full spider data access |
| **OpportunityScoringAgent** | "You score income opportunities." | `score_opportunity`, `rank_opportunities` | Opportunity model access |

### Orchestration Agents

| Agent | System Prompt | Tools | Special Powers |
|-------|--------------|-------|----------------|
| **WorkflowAgent** | "You coordinate multi-step workflows." | `delegate_to_agent` (can call other agents) | Can orchestrate any agent |
| **HiveMindAgent** | "You synthesize multi-agent intelligence." | `gather_perspectives`, `synthesize`, `debate` | Triggers AgentConversations |

### Strategy & Advisory Agents

| Agent | System Prompt | Tools | Focus |
|-------|--------------|-------|-------|
| **ContentStrategyAgent** | "You recommend content strategies." | `analyze_content`, `suggest_topics` | Spider trends → recommendations |
| **SEOOptimizerAgent** | "You optimize for discoverability." | `generate_hashtags`, `optimize_metadata` | SEO and discovery |
| **BrandIdentityAgent** | "You maintain brand consistency." | `analyze_brand`, `suggest_colors`, `check_consistency` | Brand guidelines |
| **CreativeDirectorAgent** | "You provide high-level direction." | `review_creative`, `suggest_direction` | Big picture guidance |

### Executive Agents (Co-Leadership)

| Agent | Persona | Focus |
|-------|---------|-------|
| **CTOAgent** | Technical visionary | Architecture, feasibility, tech trends |
| **COOAgent** | Operations expert | Efficiency, processes, scaling |
| **CFOAgent** | Financial strategist | Costs, ROI, monetization |
| **CreativeDirectorAgent** | Artistic leader | Style, aesthetics, brand |
| **DataAnalystAgent** | Insights specialist | Metrics, patterns, predictions |

---

## Sci-Fi Features Integration

Each agent interaction is enriched with sci-fi context:

### 1. Mood System (10 States)
```python
class AgentMood:
    STATES = ['inspired', 'focused', 'curious', 'confident', 'contemplative',
              'energetic', 'calm', 'frustrated', 'tired', 'playful']

    # Dimensions (0.0 - 1.0)
    creativity_level: float
    precision_level: float
    sociability_level: float
    risk_tolerance: float
    intensity: float

    def get_prompt_modifier(self) -> str:
        """Returns text to influence AI response style based on mood."""
```

**Integration:** Before each agent call, current mood modifies the system prompt.

### 2. Memory Palace
```python
class MemoryPalaceRoom:
    TYPES = ['techniques', 'successes', 'lessons', 'preferences',
             'insights', 'experiments', 'general']

class AgentMemory:
    title: str
    description: str
    embedding_vector: List[float]  # 768-dim for semantic search
    times_recalled: int
    usefulness_score: float
```

**Integration:** ContextAggregator retrieves relevant memories via embedding similarity.

### 3. Evolution System (10 Levels)
```python
LEVELS = ['Novice', 'Apprentice', 'Journeyman', 'Expert', 'Master',
          'Grandmaster', 'Legend', 'Mythic', 'Transcendent', 'Omniscient']

class AgentEvolution:
    total_xp: int
    current_level: int

    # Bonuses increase with level
    speed_bonus: float      # % faster execution
    quality_bonus: float    # % better output
    creativity_bonus: float # % more creative
    efficiency_bonus: float # % less resources
```

**Integration:** Higher-level agents get more trust and better prompts.

### 4. Relationships (Allies/Rivals)
```python
class AgentLearningConnection:
    teacher_agent: Agent
    student_agent: Agent
    learning_type: str  # complementary, specialization, pipeline
    success_rate: float
```

**Integration:** Related agents can be pulled into collaborative tasks.

### 5. Agent Conversations (AI-to-AI)
```python
class AgentConversation:
    topic: str
    conversation_type: str  # knowledge_sharing, debate, brainstorm
    participants: List[Agent]
    messages: List[ConversationMessage]
    insights_generated: List[str]
```

**Integration:** HiveMindAgent triggers multi-agent discussions.

### 6. Time Travel Debugging
```python
class TimeTravelMixin:
    def record_decision(self, decision_type, action, reasoning, alternatives):
        """Record decision point for later replay."""

    def replay_session(self, session_id):
        """Replay agent's thought process step by step."""
```

**Integration:** All agents inherit TimeTravelMixin for debugging.

---

## Spider-Agent Data Flow

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   SPIDER    │────▶│   SpiderData     │────▶│ SpiderIntelligence  │
│  (Celery)   │     │    (Model)       │     │    (Service)        │
└─────────────┘     └──────────────────┘     └─────────────────────┘
                                                       │
                                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT AGGREGATOR                            │
│                                                                  │
│  get_spider_context():                                           │
│  • Trending topics (tags + keywords)                             │
│  • Tech trends (discussions, projects)                           │
│  • Market insights (prices, movements)                           │
│  • Job market (remote opportunities)                             │
│  • Creative trends (styles, palettes)                            │
│                                                                  │
│  Returns: SpiderContext with all relevant data                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT KNOWLEDGE SOURCE                        │
│                                                                  │
│  Links agents to spider-derived knowledge:                       │
│  • knowledge_type: trend, market, opportunity, content_idea      │
│  • spider_category: tech, jobs, financial, creative              │
│  • confidence_score, relevance_score, freshness_score            │
│                                                                  │
│  AgentSpiderConnection: Defines which agents get which data      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SPECIALIZED AGENT                          │
│                                                                  │
│  Receives enriched context:                                      │
│  • Spider insights relevant to task                              │
│  • Memory context (past similar tasks)                           │
│  • Mood modifier (response style)                                │
│  • Evolution stats (confidence multiplier)                       │
│  • Relationship context (who to consult)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Assistant's New Tool Schema

```python
ASSISTANT_TOOLS = [
    {
        "type": "function",
        "name": "delegate_to_agent",
        "description": """Delegate a task to a specialized agent.

        Use this ONLY when the user wants something CREATED or DONE.
        For questions, advice, or conversation - just respond directly.

        CREATION AGENTS:
        - ImageAgent: Create NEW images (logos, banners, illustrations)
        - VideoAgent: Create NEW videos (animations, video clips)
        - AudioAgent: Create audio (text-to-speech, voiceovers, sfx)
        - ThreeDAgent: Create 3D models from images

        EDITING AGENTS:
        - ImageEditingAgent: MODIFY existing images (upscale, remove bg, variations)
        - VideoEditingAgent: MODIFY existing videos (trim, effects, captions)

        RESEARCH AGENTS:
        - ResearchAgent: Search web, query spider network, analyze trends
        - TrendAnalysisAgent: Deep trend analysis and predictions

        ORCHESTRATION:
        - WorkflowAgent: Multi-step projects (research AND create)
        - HiveMindAgent: Get multiple agent perspectives synthesized

        STRATEGY:
        - ContentStrategyAgent: Content recommendations
        - SEOOptimizerAgent: Hashtags, metadata, discovery
        - BrandIdentityAgent: Brand consistency checks
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "agent_name": {
                    "type": "string",
                    "enum": [
                        "ImageAgent", "VideoAgent", "AudioAgent", "ThreeDAgent",
                        "ImageEditingAgent", "VideoEditingAgent",
                        "ResearchAgent", "TrendAnalysisAgent",
                        "WorkflowAgent", "HiveMindAgent",
                        "ContentStrategyAgent", "SEOOptimizerAgent", "BrandIdentityAgent"
                    ],
                    "description": "Which agent to delegate to"
                },
                "task": {
                    "type": "string",
                    "description": "What the user wants done, in natural language"
                },
                "context": {
                    "type": "object",
                    "description": "Optional context (count, style, reference_id, etc.)"
                }
            },
            "required": ["agent_name", "task"]
        }
    },
    {
        "type": "function",
        "name": "remember_preference",
        "description": "Store a user preference for future reference",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "value": {"type": "string"}
            },
            "required": ["key", "value"]
        }
    },
    {
        "type": "function",
        "name": "recall_memory",
        "description": "Search agent memories for relevant past experiences",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"},
                "agent_name": {"type": "string", "description": "Optional: specific agent's memories"}
            },
            "required": ["query"]
        }
    }
]
```

---

## Example Flows

### Flow 1: Question (No Agent Needed)
```
User: "What style would work best for a tech startup logo?"

Personal Assistant (GPT call with tool_choice='auto'):
→ No delegate_to_agent called
→ Just answers: "For tech startups, I'd recommend minimalist, geometric,
   or modern sans-serif styles. Current spider data shows flat design
   and gradient meshes are trending..."
→ Uses spider context from ContextAggregator
→ No credits spent
```

### Flow 2: Simple Creation
```
User: "Create a cyberpunk logo for my tech startup"

Personal Assistant (GPT call):
→ Recognizes this needs action
→ Calls: delegate_to_agent("ImageAgent", "create cyberpunk logo for tech startup")

Super Platform Coordinator:
→ CLASSIFY: CREATION query (confidence 0.98)
→ AGGREGATE: Get trending cyberpunk styles from Dribbble/Behance spiders
→ ROUTE: ExecutionMode.AGENT_EXECUTION

Agent Router:
→ Routes to ImageAgent.execute()

ImageAgent (GPT call with ONLY image tools):
→ System prompt: "You create images. That's all."
→ Sci-Fi context: mood=focused, evolution=Expert (quality_bonus=15%)
→ Spider context: "Current cyberpunk trends: neon gradients, holographic effects"
→ Memory context: "User previously liked minimalist designs"
→ Tool available: generate_image
→ Calls: generate_image(prompt="cyberpunk logo...", count=3, style="cyberpunk")
→ Records decision via TimeTravelMixin
→ Returns: 3 images

Learning Loop:
→ Records: query, agent used, result, execution time
→ Updates ImageAgent XP
```

### Flow 3: Multi-Step Workflow
```
User: "Research AI trends and create 3 logos based on what you find"

Personal Assistant (GPT call):
→ Recognizes this needs research AND creation
→ Calls: delegate_to_agent("WorkflowAgent", "research AI trends then create 3 logos")

WorkflowAgent (orchestrator):
→ Step 1: delegate_to_agent("ResearchAgent", "AI trends 2025")
   → ResearchAgent queries spiders: TechCrunch, HackerNews, DevTo
   → Returns: trend summary with key themes

→ Step 2: Analyzes research, extracts visual directions

→ Step 3: delegate_to_agent("ImageAgent", "create 3 logos incorporating:
          neural networks, ambient computing, multimodal AI themes")
   → ImageAgent generates images with trend-informed prompts
   → Returns: 3 images

→ Returns to user: research summary + 3 images
```

### Flow 4: Hive Mind Collaboration
```
User: "Get the team's opinion on this brand direction"

Personal Assistant:
→ Calls: delegate_to_agent("HiveMindAgent", "review brand direction",
         context={"image_ids": [5, 6, 7]})

HiveMindAgent:
→ Triggers AgentConversation with:
  - CTOAgent (technical feasibility)
  - CreativeDirectorAgent (artistic direction)
  - CFOAgent (market viability)
  - DataAnalystAgent (trend alignment)

→ Each agent reviews with their expertise + mood influence
→ Conversation messages streamed via WebSocket
→ HiveMind synthesizes: consensus points, disagreements, recommendations

→ Returns: structured team opinion with individual perspectives
```

---

## Files to Create/Modify

### New Files: `core/agents/` (Clean Agent Implementations)

```
core/agents/
├── __init__.py
├── base_agent.py           # Abstract base with TimeTravelMixin
├── image_agent.py          # Image generation ONLY
├── video_agent.py          # Video generation ONLY
├── audio_agent.py          # Audio generation ONLY
├── three_d_agent.py        # 3D generation ONLY
├── image_editing_agent.py  # Image editing ONLY
├── video_editing_agent.py  # Video editing ONLY
├── research_agent.py       # Web + spider search ONLY
├── trend_agent.py          # Trend analysis ONLY
├── workflow_agent.py       # Orchestration (can delegate)
├── hive_mind_agent.py      # Multi-agent synthesis
├── strategy/
│   ├── content_strategy_agent.py
│   ├── seo_agent.py
│   └── brand_agent.py
└── executive/
    ├── cto_agent.py
    ├── coo_agent.py
    ├── cfo_agent.py
    └── creative_director_agent.py
```

### Modify: `core/agent_router.py`

```python
class AgentRouter:
    """Simple deterministic routing - NO LLM needed."""

    AGENT_MAP = {
        "ImageAgent": ImageAgent,
        "VideoAgent": VideoAgent,
        "AudioAgent": AudioAgent,
        # ... etc
    }

    def route(self, agent_name: str, task: str, context: dict) -> AgentResult:
        agent_class = self.AGENT_MAP.get(agent_name)
        if not agent_class:
            raise AgentNotFoundError(f"Unknown agent: {agent_name}")

        # Inject sci-fi context
        scifi_context = SciFiIntegrationService.get_context(agent_name)
        spider_context = SpiderIntelligenceService.get_insights_for_prompt(task)

        agent = agent_class()
        return agent.execute(task, context, scifi_context, spider_context)
```

### Modify: Personal Assistant

```python
# Remove ALL creation tools
# Keep ONLY: delegate_to_agent, remember_preference, recall_memory
# Update system prompt to be conversational

ASSISTANT_SYSTEM_PROMPT = """You are a helpful AI assistant for creative professionals.

For QUESTIONS and ADVICE:
- Just answer directly using your knowledge
- Reference spider trends when relevant
- No need to delegate

For CREATION REQUESTS (create, make, generate, design):
- Delegate to the appropriate agent
- ImageAgent for any static visuals (logos, banners, etc.)
- VideoAgent for any motion content
- Never try to create content yourself

You are conversational and helpful. You remember user preferences."""
```

---

## Implementation Plan

### Phase 1: Create Agent Infrastructure (1 session)
- [ ] Create `core/agents/base_agent.py` with TimeTravelMixin
- [ ] Create `core/agents/image_agent.py` (test case)
- [ ] Create `core/agent_router.py`
- [ ] Add feature flag: `USE_CLEAN_AGENT_ARCHITECTURE`
- [ ] Test ImageAgent in isolation

### Phase 2: Migrate All Agents (1-2 sessions)
- [ ] Create all creation agents (video, audio, 3D)
- [ ] Create all editing agents
- [ ] Create research agents with spider integration
- [ ] Create orchestration agents (workflow, hive mind)
- [ ] Create strategy agents
- [ ] Verify each has isolated tool set

### Phase 3: Integrate Super Platform Coordinator (1 session)
- [ ] Update QueryClassifier for new agent names
- [ ] Update ContextAggregator to feed agents
- [ ] Update DynamicPromptBuilder for per-agent prompts
- [ ] Wire router into coordinator execution

### Phase 4: Modify Personal Assistant (1 session)
- [ ] Remove ALL creation tools
- [ ] Add delegate_to_agent, remember_preference, recall_memory
- [ ] Update system prompt to be conversational
- [ ] Test: questions should NOT trigger any agent

### Phase 5: Update Frontend (1 session)
- [ ] Remove autonomous workflow loop
- [ ] Single request → single response
- [ ] Agent results displayed directly
- [ ] WebSocket updates for multi-agent conversations

### Phase 6: Testing & Cleanup (1 session)
- [ ] Test all paths: conversation, image, video, workflow, hive mind
- [ ] Verify spider data flows to agents
- [ ] Verify sci-fi context enriches prompts
- [ ] Remove old code behind feature flag
- [ ] Update documentation

**Total: 5-6 sessions for complete overhaul**

---

## Migration Strategy

1. **Build new system alongside old** (feature flag `USE_CLEAN_AGENT_ARCHITECTURE`)
2. **Test thoroughly with flag on** (internal testing)
3. **Once stable, default flag to True** (gradual rollout)
4. **Remove old system** (cleanup)
5. **Remove flag**

---

## Benefits

1. **Impossible to call wrong tool** - Agents only have their own tools
2. **Clean conversation mode** - Assistant can just talk without tool pressure
3. **Testable agents** - Each agent is a unit that can be tested independently
4. **Full ecosystem preserved** - All 70 spiders, 22 agents, 15 sci-fi features intact
5. **Debuggable** - Clear path: User → Assistant → Router → Agent → Tool
6. **Cost efficient** - Only make GPT calls when needed
7. **Extensible** - Adding new agents doesn't affect others

---

## Questions to Decide

1. **Should we keep existing agent files in `/agents/` or replace them?**
   - Recommendation: Create new `core/agents/` with clean implementations, deprecate old

2. **How does the frontend display agent progress?**
   - Recommendation: WebSocket updates from each agent, same as current

3. **How do we handle errors mid-workflow?**
   - Recommendation: WorkflowAgent catches and reports partial results

4. **Should HiveMind conversations be real-time or batched?**
   - Recommendation: Real-time WebSocket streaming (already have infrastructure)

---

## Next Steps

1. **Review and approve this proposal**
2. **Start Phase 1**: Create base agent class and ImageAgent
3. **Test ImageAgent** in isolation before proceeding
4. **Iterate** through remaining phases

---

*This architecture preserves everything we've built while solving the tool routing problem at its root.*
