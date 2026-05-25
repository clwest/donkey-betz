<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge.
> **Note:** Agent count (74) stale (current: 83 in AGENT_MAP). Architecture narrative still useful; verify subsystem links against topics/personal-assistant.md. Per Session 1143 Phase 4 (Chris Q4=Y): PLATFORM_INVENTORY + docs/INDEX are the only authoritative counts.

# AI Assistant System Architecture

**Last Updated:** January 20, 2026 - Session 786
**Purpose:** Document how the main AI Assistant orchestrates the entire platform

---

## Executive Summary

The AI Assistant is the **unified brain** of the platform, connecting users to 74 specialized agents, 77 real-time data spiders, 17 ML models, and 9 body system monitors. Every user interaction flows through a sophisticated orchestration layer that classifies intent, aggregates context, routes to appropriate agents, and records outcomes for continuous learning.

**Key Stats:**
| Component | Count |
|-----------|-------|
| Specialized Agents | 74 |
| PA Tools | 86 |
| Data Spiders | 77 |
| ML Models | 17 |
| Integration Services | 6 |
| Body Systems | 9 |
| LLM Providers | 6 |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER REQUEST                                   │
│                    (Text, Voice, or API Call)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SUPER PLATFORM COORDINATOR                             │
│                "The Unified Brain" - Single Entry Point                     │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  CLASSIFY   │ → │  AGGREGATE  │ → │    ROUTE    │ → │   EXECUTE   │  │
│  │  (Intent)   │   │  (Context)  │   │   (Mode)    │   │   (Agent)   │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│    DIRECT     │         │     AGENT     │         │   WORKFLOW    │
│   RESPONSE    │         │   EXECUTION   │         │ ORCHESTRATION │
│               │         │               │         │               │
│  (Questions,  │         │  (PA → Router │         │  (Multi-step  │
│   Status)     │         │  → Specialist)│         │   Pipelines)  │
└───────────────┘         └───────────────┘         └───────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LEARNING LOOP                                     │
│          Record Outcomes → Award XP → Mine Patterns → Improve               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Super Platform Coordinator

**File:** `core/super_platform/coordinator.py`

The Coordinator is the central orchestrator that unifies all platform components. Every user interaction flows through here.

#### Classification (Query Types)

```python
class QueryType(Enum):
    QUESTION = "question"           # Answer directly with context
    CREATION = "creation"           # Generate content (images, video, audio)
    EDITING = "editing"             # Modify existing content
    RESEARCH = "research"           # Search, analyze, investigate
    WORKFLOW = "workflow"           # Multi-step orchestration
    STATUS = "status"               # System health queries
    OPPORTUNITY = "opportunity"     # Revenue/betting opportunities
```

#### Execution Modes

```python
class ExecutionMode(Enum):
    DIRECT_RESPONSE = "direct"      # Answer directly with context
    AGENT_EXECUTION = "agent"       # Execute via single agent
    WORKFLOW_ORCHESTRATION = "workflow"  # Multi-step workflow
    HIVE_MIND = "hive"              # Multi-agent collaboration/debate
    MEMORY_RECALL = "memory"        # Memory Palace query
    OPPORTUNITY = "opportunity"     # Revenue/opportunity handling
```

#### Coordinator Result

```python
@dataclass
class CoordinatorResult:
    success: bool
    response: str
    execution_mode: ExecutionMode
    classification: ClassificationResult
    context_used: Dict[str, Any]
    agents_used: List[str]
    artifacts: List[Dict[str, Any]]      # Generated images, videos, etc.
    execution_time_ms: float
    project_created: Optional[Dict]      # Auto-created project info
```

---

### 2. PersonalAssistantAgent (The Traffic Cop)

**File:** `core/agents/personal_assistant_agent.py`

The PA is the main interface between users and the 74 specialized agents. It understands intent and routes to the appropriate specialist.

#### Key Responsibilities

1. **Analyze** user message to understand intent
2. **Determine** if it's a question (answer directly) or action (delegate)
3. **Route** to appropriate specialized agent via AgentRouter
4. **Synthesize** and return the response

#### System Prompt Highlights

```
You are the Personal Assistant, the main interface for the AI Studio.

## CRITICAL: YOU HAVE REAL-TIME DATA ACCESS
You are NOT a vanilla LLM with a knowledge cutoff. You have:
- 77 LIVE SPIDERS that gather real-time data from the web
- 74 SPECIALIZED AGENTS with domain expertise
- Real-time sports odds and scores via TheOddsAPI
- Live news and trends from TechCrunch, HackerNews, Reddit
- Financial data from CoinGecko, Yahoo Finance, Polygon, Kalshi
- The current date is provided in your context
```

#### Primary Tool: delegate_to_agent

```python
tools = [{
    "name": "delegate_to_agent",
    "description": "Delegate a task to a specialized agent",
    "parameters": {
        "agent_name": {
            "type": "string",
            "description": "Which agent: ResearchAgent, ImageAgent, etc."
        },
        "task": {
            "type": "string",
            "description": "The specific task to perform"
        },
        "context": {
            "type": "object",
            "description": "Additional context for the agent"
        }
    }
}]
```

---

### 3. AgentRouter (Deterministic Routing)

**File:** `core/agent_router.py`

The router provides **deterministic** (no LLM) routing to specialized agents. It's a simple dictionary lookup that prevents wrong-agent selection.

```python
class AgentRouter:
    """
    Architecture: User → PA → AgentRouter → Specialized Agent → Tools

    Key Design: No LLM involved in routing - just dictionary lookup.
    """

    AGENT_MAP: Dict[str, Type[BaseAgent]] = {
        "ImageAgent": ImageAgent,
        "VideoAgent": VideoAgent,
        "ResearchAgent": ResearchAgent,
        # ... 74 agents total
    }

    def route(self, agent_name: str, task: str, context: dict) -> AgentResult:
        # 1. Lookup agent class
        agent_class = self.AGENT_MAP.get(agent_name)

        # 2. Inject all context types
        scifi_context = self._get_scifi_context(agent_name, task)
        spider_context = self._get_spider_context(task, agent_name)
        learning_context = self._get_learning_context(agent_name, task)
        advisor_context = self._get_advisor_context(agent_name, task)
        feedback_context = self._get_feedback_context(agent_name, task)

        # 3. Instantiate and execute
        agent = agent_class(user=self.user)
        return agent.execute(task, context, scifi_context, spider_context)
```

---

## Context Injection Pipeline

Every agent receives **5 types of context** automatically before execution:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CONTEXT INJECTION                              │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │   SPIDER    │  │   SCIFI     │  │  LEARNING   │                 │
│  │   CONTEXT   │  │   CONTEXT   │  │   CONTEXT   │                 │
│  │             │  │             │  │             │                 │
│  │ Real-time   │  │ Mood        │  │ Past        │                 │
│  │ data from   │  │ Evolution   │  │ successes   │                 │
│  │ 77 spiders  │  │ Relations   │  │ patterns    │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐                                  │
│  │  ADVISOR    │  │  FEEDBACK   │                                  │
│  │   CONTEXT   │  │   CONTEXT   │                                  │
│  │             │  │             │                                  │
│  │ 25 legendary│  │ Performance │                                  │
│  │ advisors'   │  │ metrics for │                                  │
│  │ wisdom      │  │ self-improve│                                  │
│  └─────────────┘  └─────────────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  AGENT PROMPT   │
                    │  All context    │
                    │  injected into  │
                    │  system prompt  │
                    └─────────────────┘
```

### Context Sources

| Context Type | Service | Purpose |
|--------------|---------|---------|
| **Spider** | `SpiderContextBuilder` | Real-time data from 77 spiders (news, financial, social) |
| **SciFi** | `SciFiIntegrationService` | Mood, evolution level, relationships, dreams |
| **Learning** | `LearningPatternEngine` | Past successful executions, proven strategies |
| **Advisor** | `AdvisorContextBuilder` | Decision frameworks from 25 legendary advisors |
| **Feedback** | `FeedbackLoopEngine` | Historical performance for self-improvement |
| **Knowledge** | `KnowledgeFirstRouter` | Check cached knowledge before external queries |

---

## The 86 PA Tools

The Personal Assistant has access to 86 tools connecting it to all platform capabilities:

### Agent Execution Tools (31)

| Tool | Agent | Purpose |
|------|-------|---------|
| `image_generation_agent` | ImageAgent | Create images |
| `video_generation_agent` | VideoAgent | Create videos |
| `audio_generation_agent` | AudioAgent | Voice/sound generation |
| `image_editing_agent` | ImageEditingAgent | Upscale, remove BG, variations |
| `video_editing_agent` | VideoEditingAgent | Trim, effects, text overlay |
| `workflow_orchestration_agent` | WorkflowAgent | Multi-step pipelines |
| `content_writer_agent` | ContentWriterAgent | Articles, blogs, copy |
| `competitor_analysis_agent` | CompetitorAnalysisAgent | Business research |
| `customer_research_agent` | CustomerResearchAgent | Customer personas |
| `legal_doc_drafter_agent` | LegalDocDrafterAgent | Legal documents |
| `universal_agent_tool` | **Any** | Access any of 74 agents by name |

### Body System Tools (9)

| Tool | Purpose |
|------|---------|
| `body_vitals_tool` | Query all 9 body systems (HEART, BRAIN, LUNGS, etc.) |
| `check_budget_tool` | Check LUNGS resource budget before expensive operations |
| `system_alerts_tool` | Get critical alerts from body systems |

### Intelligence Tools (4)

| Tool | Purpose |
|------|---------|
| `predictions_tool` | Query agent predictions and accuracy |
| `gates_tool` | Query pilot readiness gates |
| `pilots_tool` | Query pilot execution status |
| `ml_analysis_tool` | Auto-select optimal ML models for analysis |

### Pipeline Tools (4)

| Tool | Purpose |
|------|---------|
| `opportunity_manager_tool` | Query/filter opportunities |
| `task_manager_tool` | Manage OpportunityTasks |
| `pipeline_orchestrator_tool` | Manual pipeline execution |
| `revenue_tracker_tool` | Track revenue/outcomes |

### Workspace Tool (SKIN Layer)

| Tool | Purpose |
|------|---------|
| `workspace_tool` | Manage workspaces where agents write real code |

---

## Integration Services

### 1. SciFiIntegrationService

**File:** `core/super_platform/scifi_integration.py`

Injects personality and growth mechanics into agents:

```python
class SciFiIntegrationService:
    def get_scifi_context(self, agent_name: str, task: str, user) -> dict:
        return {
            'mood': self._get_agent_mood(agent_name),      # Affects response style
            'evolution': self._get_evolution(agent_name),  # XP, level, title
            'relationships': self._get_relationships(),    # Allies, rivals
            'dreams': self._get_recent_dreams(),          # Creative insights
            'memory_clusters': self._get_memory_clusters() # Related memories
        }
```

### 2. LearningLoopService

**File:** `core/super_platform/learning_loop.py`

Records outcomes and enables continuous improvement:

```python
class LearningLoopService:
    def record_execution_outcome(self, agent, task, success, result):
        """Record for future pattern mining"""

    def record_prediction_outcome(self, prediction, actual):
        """Track prediction accuracy for confidence calibration"""

    def award_xp(self, agent, amount, reason):
        """Level up agents based on performance"""

    def get_patterns_for_agent(self, agent_name, task):
        """Retrieve proven strategies for similar tasks"""
```

### 3. SpiderContextBuilder

**File:** `core/services/spider_context_builder.py`

Maps agents to relevant spider categories and builds targeted context:

```python
AGENT_SPIDER_MAPPING = {
    'ResearchAgent': ['tech', 'news', 'reddit', 'hackernews'],
    'StockAnalystAgent': ['financial', 'yahoo_finance', 'polygon'],
    'SportsOddsAnalyst': ['sports', 'the_odds_api', 'espn'],
    'ContentWriterAgent': ['tech', 'news', 'trending'],
    # ... mappings for all 74 agents
}
```

### 4. AdvisorContextBuilder

**File:** `core/services/advisor_context_builder.py`

Injects wisdom from 25 legendary advisors:

| Category | Advisors |
|----------|----------|
| **Investment** | Warren Buffett, Charlie Munger, Ray Dalio, Cathie Wood |
| **Tech** | Elon Musk, Steve Jobs, Jeff Bezos, Marc Andreessen |
| **Creative** | Kanye West, David Ogilvy, Seth Godin |
| **Strategy** | Peter Lynch, Howard Marks, Paul Graham |

### 5. FeedbackLoopEngine

**File:** `core/services/feedback_loop_engine.py`

Provides performance awareness for self-improvement:

```python
def get_feedback_for_agent(self, agent_name: str, task: str) -> dict:
    return {
        'reliability_score': 0.94,           # Historical success rate
        'performance_rating': 'excellent',   # Tier classification
        'recommendations': [...],            # Areas for improvement
        'recent_failures': [...],            # Learn from mistakes
    }
```

---

## Conversation Orchestrator (Multi-Agent Debates)

**File:** `core/conversation_orchestrator.py`

When agents need to collaborate or debate:

```python
class ConversationOrchestrator:
    def generate_conversation(
        self,
        agent1={'name': 'ResearchAgent', 'type': 'ResearchAgent'},
        agent2={'name': 'ContrarianAgent', 'type': 'ContrarianAgent'},
        topic='Should we cover AI trends?',
        num_turns=6
    ) -> ConversationResult:
        """
        Generates structured debates with:
        1. Constructive tension (no empty agreement)
        2. Platform grounding (real metrics cited)
        3. Role-specific voice (22 distinct styles)
        4. Decision summary with actionable insights
        """
```

### Conversation Contract Enforcement

```python
CONVERSATION_CONTRACT = {
    'min_tension_ratio': 0.3,      # 30% must challenge/disagree
    'max_empty_agreement': 0.2,    # Max 20% empty "great point!"
    'required_grounding': True,    # Must cite real platform data
}

# Banned repetitive phrases
DISALLOWED_OPENERS = [
    "I'd push back slightly",
    "That's a great point",
    "With all due respect",
    "I agree, however",
]
```

### 22 Role-Anchored Conversation Styles

| Agent | Role | Disagreement Style |
|-------|------|-------------------|
| ResearchAgent | DATA REALIST | "The data contradicts that assumption." |
| CTOAgent | TECHNICAL ARBITER | "The architecture doesn't support that at scale." |
| COOAgent | OPERATIONS REALIST | "We don't have the resources for that timeline." |
| ContrarianAgent | DEVIL'S ADVOCATE | "Everyone's already doing that - we'll get lost." |
| CreativeDirectorAgent | VISION HOLDER | "That's playing it too safe." |

---

## End-to-End Request Flow

### Example: "What's trending in AI and create 3 logos for an AI startup"

```
1. USER INPUT
   │
   ▼
2. SUPER PLATFORM COORDINATOR
   ├── Classify: WORKFLOW (research + creation)
   ├── Aggregate context from all 6 sources
   └── Route: WORKFLOW_ORCHESTRATION mode
   │
   ▼
3. PERSONAL ASSISTANT AGENT
   ├── Analyze: Multi-step request detected
   ├── Decision: Delegate to WorkflowAgent
   └── Tool call: delegate_to_agent("WorkflowAgent", task, context)
   │
   ▼
4. AGENT ROUTER
   ├── Lookup: WorkflowAgent in AGENT_MAP
   ├── Inject: Spider + SciFi + Learning + Advisor + Feedback context
   └── Execute: WorkflowAgent.execute(task, all_context)
   │
   ▼
5. WORKFLOW AGENT (Orchestrates Sub-Agents)
   │
   ├── Step 1: delegate_to_agent("ResearchAgent", "AI trends")
   │   └── ResearchAgent queries spiders, returns trends data
   │
   ├── Step 2: delegate_to_agent("ImageAgent", "3 AI startup logos")
   │   └── ImageAgent generates 3 images via Stability AI
   │
   └── Step 3: Package results, auto-create project
   │
   ▼
6. RESULTS FLOW BACK
   └── WorkflowAgent → PA → Coordinator → User
       ├── 3 generated logo images
       ├── AI trends research summary
       └── New project created with all assets
   │
   ▼
7. LEARNING LOOP
   ├── Record: Execution success for WorkflowAgent, ResearchAgent, ImageAgent
   ├── Award XP: +50 to each participating agent
   ├── Store patterns: "AI startup + logos" workflow successful
   └── Update: Agent confidence multipliers
```

---

## Agent Categories Overview

### Creation Agents (4)
- `ImageAgent` - Image generation (Stability AI)
- `VideoAgent` - Video generation (text-to-video, animate)
- `AudioAgent` - Voice/sound (ElevenLabs TTS)
- `ThreeDAgent` - 3D model generation

### Editing Agents (2)
- `ImageEditingAgent` - Upscale, remove BG, variations
- `VideoEditingAgent` - Trim, effects, text overlay

### Research & Analysis (4)
- `ResearchAgent` - Web search + 77 spider network
- `TrendAnalysisAgent` - Spider intelligence analysis
- `MarketIntelligenceAgent` - Market analysis (GNN ML)
- `OpportunityScoringAgent` - Opportunity scoring (RL)

### Content & Strategy (6)
- `ContentWriterAgent` - Articles, blogs, copy
- `ContentStrategyAgent` - Content recommendations
- `SEOOptimizerAgent` - Keywords, metadata
- `BrandIdentityAgent` - Brand consistency
- `SocialMediaAgent` - Platform-specific content
- `ContentDiversityOrchestrator` - Diversity enforcement

### Executive Suite (4)
- `CTOAgent` - Technical planning
- `COOAgent` - Operations planning
- `CreativeDirectorAgent` - Creative guidance
- `MeetingCoordinatorAgent` - Agent meetings

### Development (4)
- `CodeGeneratorAgent` - Generate code from specs
- `FullStackDeveloperAgent` - Full stack features
- `CodeReviewAgent` - Security, performance review
- `DevOpsAgent` - Docker, K8s, CI/CD

### Stock Intelligence (9)
- `StockAuditCoordinator` - Orchestrates team
- `MarketIntelligenceCoordinator` - Synthesizes briefs
- `BullCaseAgent` - Bullish thesis
- `BearCaseAgent` - Bearish thesis
- `SignalScannerAgent` - Technical patterns
- Plus 4 more specialists

### Blockchain (5)
- `BlockchainAuditCoordinator` - Orchestrates team
- `SmartContractAuditorAgent` - Vulnerability scanning
- `TransactionMonitorAgent` - Real-time monitoring
- `WhaleWatcherAgent` - Large wallet tracking (GNN)
- `ExploitDetectorAgent` - Exploit detection

### Prediction Markets (3)
- `PredictionMarketAnalyst` - Kalshi/Polymarket
- `SportsOddsAnalyst` - Sports betting odds
- `ArbitrageDetector` - Cross-book arbitrage

### Podcast Studio (4)
- `PodcastCoordinatorAgent` - Orchestrates podcast
- `ModeratorAgent` - Hosts debates
- `DebateAdvocateAgent` - Argues FOR
- `DebateSkepticAgent` - Argues AGAINST

### Orchestration (5)
- `WorkflowAgent` - Multi-step coordination
- `AISeriesWorkflowAgent` - Multi-episode series
- `CampaignOrchestratorAgent` - Marketing campaigns
- `WorkflowOrchestrationAgent` - Complex workflows
- `OpportunityPipelineAgent` - Opportunity evaluation

### Special Purpose
- `LegalDocDrafterAgent` - Colorado family law
- `SystemIntelligenceAgent` - Platform health
- `ThinkingAgent` - Extended reasoning
- `ResolveAgent` - DaVinci Resolve automation
- `PromptEngineeringAgent` - Prompt optimization

---

## Key Files Reference

| Component | File |
|-----------|------|
| **Coordinator** | `core/super_platform/coordinator.py` |
| **PA Agent** | `core/agents/personal_assistant_agent.py` |
| **Agent Router** | `core/agent_router.py` |
| **Base Agent** | `core/agents/base_agent.py` |
| **Tool Definitions** | `core/assistant/tool_definitions.py` |
| **SciFi Service** | `core/super_platform/scifi_integration.py` |
| **Learning Loop** | `core/super_platform/learning_loop.py` |
| **Spider Context** | `core/services/spider_context_builder.py` |
| **Advisor Context** | `core/services/advisor_context_builder.py` |
| **Feedback Loop** | `core/services/feedback_loop_engine.py` |
| **Conversation** | `core/conversation_orchestrator.py` |

---

## See Also

- [AGENTS.md](../AGENTS.md) - Complete agent reference (74 agents)
- [SPIDERS.md](../SPIDERS.md) - Spider network documentation (77 spiders)
- [SERVICES.md](../SERVICES.md) - Services layer (114 services)
- [SCIFI_FEATURES.md](../SCIFI_FEATURES.md) - Sci-Fi personality features
- [MULTI_AGENT_ARCHITECTURE.md](MULTI_AGENT_ARCHITECTURE.md) - Multi-agent patterns
- [MEMORY_SYSTEM_ARCHITECTURE.md](MEMORY_SYSTEM_ARCHITECTURE.md) - Memory and learning
