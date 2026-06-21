<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.

# System Architecture

**Platform:** Unified Donkey Betz - AI Content Creation Empire
**Last Updated:** February 8, 2026 (Session 969b) — narrative preserved; counts may drift
**Total Lines of Code:** 200,000+ (Session 969b snapshot — see PLATFORM_INVENTORY for current)

---

## Table of Contents

1. [Three-Layer Architecture](#three-layer-architecture)
2. [Super Platform Coordinator](#super-platform-coordinator)
3. [Agent Layer](#agent-layer)
4. [Data Layer](#data-layer)
5. [External Integrations](#external-integrations)
6. [Request Flow](#request-flow)
7. [Database Schema](#database-schema)
8. [File Structure](#file-structure)

---

## Three-Layer Architecture

The platform is organized into three primary layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: ORCHESTRATION                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Super Platform Coordinator                     │   │
│  │  QueryClassifier | ContextAggregator | PromptBuilder    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 2: AGENTS                              │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │  Creation │ │  Editing  │ │ Research  │ │ Strategy  │       │
│  │  Agents   │ │  Agents   │ │  Agents   │ │  Agents   │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │ Executive │ │  Business │ │  Analysis │ │   Legal   │       │
│  │  Agents   │ │  Agents   │ │  Agents   │ │  Agents   │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 3: DATA & SERVICES                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │  Spiders  │ │  External │ │ Knowledge │ │  Sci-Fi   │       │
│  │  Network  │ │   APIs    │ │  Pipeline │ │ Features  │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Super Platform Coordinator

**Location:** `core/super_platform/`
**Created:** Session 264

The unified intelligence hub that orchestrates all platform capabilities.

### Components

#### 1. Query Classifier (`query_classifier.py`)
Determines user intent without using LLM:

```python
QUERY_TYPES = [
    'QUESTION',    # User asking for information
    'CREATION',    # Generate new content (image, video, audio)
    'EDITING',     # Modify existing content
    'RESEARCH',    # Trend/market analysis
    'WORKFLOW',    # Multi-step requests
]
```

**Detection Logic:**
- Questions: Contains "what", "how", "why", "?", etc.
- Creation: Contains "create", "generate", "make", etc.
- Editing: Contains "edit", "modify", "change", etc.
- Research: Contains "research", "analyze", "trends", etc.
- Workflow: Contains "and", multiple action verbs

#### 2. Context Aggregator (`context_aggregator.py`)
Gathers relevant context from multiple sources:

```python
context = {
    'spider_data': [...],      # Recent spider intelligence
    'memories': [...],         # Relevant agent memories
    'mood': {...},             # Current agent mood state
    'prior_research': [...],   # Previous business research
    'user_profile': {...},     # User preferences
}
```

#### 3. Dynamic Prompt Builder (`prompt_builder.py`)
Constructs agent-specific prompts with injected context:

```python
def build_prompt(agent, task, context):
    return f"""
    {AGENT_SYSTEM_PROMPT}

    ## Relevant Knowledge
    {context['memories']}

    ## Recent Spider Intelligence
    {context['spider_data']}

    ## Current Task
    {task}
    """
```

#### 4. Semantic Routing Service
Uses embeddings for intelligent agent selection (0.45 similarity threshold).

---

## Agent Layer

**Location:** `core/agents/`
**Base Class:** `core/agents/base_agent.py`

### Agent Inheritance

```python
class BaseAgent(ABC):
    """Abstract base class for all agents"""

    # TimeTravelMixin for decision tracking
    # Learning hooks for collective intelligence

    def execute(self, task, context=None, scifi_context=None, spider_context=None):
        """Main execution method - all agents implement this"""
        pass

    def _get_relevant_knowledge_for_task(self, task, limit=5):
        """Semantic search on learned knowledge"""
        pass

    def _get_fresh_spider_intelligence(self, categories, hours=24):
        """Real-time spider data"""
        pass

    def _build_prompt(self):
        """Auto-injects knowledge + context"""
        pass

    def _record_learning_outcome(self, result, task, context):
        """Records for XP/evolution system"""
        pass

    def _create_execution_memory(self, result, task, memory_type):
        """Creates persistent memories"""
        pass

    def _share_knowledge(self, knowledge_type, title, knowledge_value):
        """Shares with collective intelligence"""
        pass
```

### Agent Router

**Location:** `core/agent_router.py`

Deterministic routing without LLM involvement:

```python
AGENT_MAP = {
    "ImageAgent": ImageAgent,
    "VideoAgent": VideoAgent,
    "AudioAgent": AudioAgent,
    "ThreeDAgent": ThreeDAgent,
    "ImageEditingAgent": ImageEditingAgent,
    "VideoEditingAgent": VideoEditingAgent,
    "ResearchAgent": ResearchAgent,
    # ... 25 total agents
}

def route(agent_name: str, task: str, context: dict) -> AgentResult:
    """Route to specific agent with injected context"""
    agent_class = AGENT_MAP.get(agent_name)
    agent = agent_class()

    # Inject sci-fi context (mood, memories, relationships)
    # Inject spider context (trends, market data)

    return agent.execute(task, context)
```

### Agent Categories

| Category | Agents | Purpose |
|----------|--------|---------|
| **Creation** | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent | Generate new content |
| **Editing** | ImageEditingAgent, VideoEditingAgent | Modify existing content |
| **Research** | ResearchAgent | Web + spider queries |
| **Strategy** | ContentStrategy, BrandIdentity, SEO, SocialMedia | Planning & optimization |
| **Executive** | CTO, COO, CreativeDirector, MeetingCoordinator | Business guidance |
| **Analysis** | TrendAnalysis, OpportunityScoring | Data analysis |
| **Training** | CharacterTraining, TrainedCreation | FLUX LoRA |
| **Business** | Competitor, Customer, BrandStrategy, Marketing, BusinessContent | Business research |
| **Legal** | LegalDocDrafter | Colorado family law |
| **Workflow** | WorkflowAgent | Multi-step orchestration |
| **Entry** | PersonalAssistant | User interaction |

---

## Data Layer

### Spider Network

**Location:** `ai_core/spiders/`
**Registry:** `ai_core/spiders/spider_registry.py`

```
Spider Network (80 spiders — Session 1100 refresh; canonical: PLATFORM_INVENTORY)
    │
    ▼
Celery Beat (every 30 minutes)
    │
    ▼
SpiderData Model (8,424 records)
    │
    ▼
Embedding Service (text-embedding-3-small)
    │
    ▼
SpiderData.embedding (3,313 embedded)
    │
    ▼
spider_data_bridge.py (post_save signal)
    │
    ▼
AgentKnowledgeSource (953 knowledge items)
```

### Knowledge Pipeline

**Location:** `core/services/`

```python
# Unified Intelligence Search (Session 303)
from core.services.unified_intelligence_search import get_unified_intelligence_search

search = get_unified_intelligence_search()

# Search both spider data AND business research
results = search.unified_search("AI content generation")

# Get context for prompt injection
context = search.get_research_context("AI tools")

# Trigger fresh spider crawls
search.refresh_spiders_for_query("market analysis")
```

### Learning Bridges (8 Signals)

**Location:** `core/apps.py`

1. **Agent Execution Bridge** - Captures successful agent outputs
2. **Application Outcome Bridge** - Tracks real-world results
3. **Revenue Attribution Bridge** - Connects actions to revenue
4. **Advisor Feedback Bridge** - Incorporates expert guidance
5. **Collaboration Bridge** - Records multi-agent work
6. **Personalization Bridge** - User preference learning
7. **Sports Betting Bridge** - Betting outcome learning
8. **Spider Data Bridge** - Spider -> Agent knowledge

---

## External Integrations

### API Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT LAYER                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Stability  │    │  Runway ML  │    │ ElevenLabs  │
│     AI      │    │             │    │             │
│             │    │             │    │             │
│ - Generate  │    │ - Text2Vid  │    │ - TTS       │
│ - Edit      │    │ - Img2Vid   │    │ - SFX       │
│ - Upscale   │    │ - Extend    │    │             │
│ - Remove BG │    │ - Upscale   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   OpenAI    │    │  Replicate  │    │  DaVinci    │
│             │    │             │    │  Resolve    │
│             │    │             │    │             │
│ - GPT-5-mini│    │ - FLUX LoRA │    │ - Render    │
│ - Whisper   │    │ - Training  │    │ - Color     │
│ - DALL-E 3  │    │             │    │ (UNUSED!)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Provider Files

| Provider | Integration File | Lines |
|----------|------------------|-------|
| Stability AI | `content/image_generation.py` | 1,500+ |
| Runway ML | `content/video_provider.py` | 800+ |
| ElevenLabs | `content/elevenlabs_provider.py` | 331 |
| OpenAI | `core/views_image.py` | 7,000+ |
| Replicate | `content/replicate_provider.py` | 370 |
| DaVinci | `content/davinci_provider.py` | 900+ |

### Discord Integration (Sessions 419-432)

The Discord-First platform provides an alternative interface to the web app.

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISCORD BOT                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  21 Slash Commands                       │    │
│  │  /ask /create /research /gallery /profile /opportunities │    │
│  │  /setup /server-info /client-add /client-deliver ...    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│         ┌───────────────────┼────────────────────┐              │
│         ▼                   ▼                    ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Notifications│    │  Server     │    │   Client    │         │
│  │    System    │    │   Setup     │    │ Management  │         │
│  │              │    │             │    │             │         │
│  │ - Dreams     │    │ - Templates │    │ - Channels  │         │
│  │ - Convos     │    │ - Channels  │    │ - Delivery  │         │
│  │ - Status     │    │ - Config    │    │ - Invites   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

| Component | File | Purpose |
|-----------|------|---------|
| Bot Core | `core/services/discord_bot.py` | 21 slash commands, 7 Cogs |
| Notifications | `core/services/discord_notifications.py` | Dreams, conversations, status |
| User Linking | `core/views_discord.py` | Link Discord ↔ Web accounts |
| Models | `core/models/base/models.py` | DiscordServer, DiscordClient |

---

## User Context Injection (Session 858)

**Location:** `core/agent_router.py`, `core/agent_context_middleware.py`

All 76 agents now receive personalized user context for tailored responses.

### How It Works

```
User Request
    │
    ▼
AgentRouter._get_user_context()
    │
    ├─► AgentContextMiddleware.get_user_context_for_agent(user)
    │       └─► ExtendedUserProfile (skills, job_preferences, salary)
    │       └─► EnhancedUserProfile (goals, routines, learning style)
    │       └─► UserPreferences (AI model, automation level)
    │
    ├─► MemoryContextService.get_prompt_context(user)
    │       └─► UserMemoryContext (decisions, preferences, patterns)
    │
    └─► _apply_injection_policy(agent_category)
            └─► Filters context based on agent type
    │
    ▼
context['user'] = user_context
    │
    ▼
Agent.execute(task, context, scifi_context, spider_context)
```

### Injection Policy by Agent Category

| Category | Agents | Data Injected |
|----------|--------|---------------|
| **career** | OpportunityPipelineAgent, CustomerResearchAgent | skills, job_preferences, salary_range, success_patterns |
| **content** | ContentWriterAgent, SEOOptimizerAgent | communication_style, tone_preferences, goals |
| **financial** | StockAnalystAgent, SportsOddsAnalyst | risk_tolerance, betting_preferences, investment_goals |
| **development** | CodeGeneratorAgent, DevOpsAgent | skills, tech_stack, github_username |
| **research** | ResearchAgent, TrendAnalysisAgent | interests, learning_goals, preferred_topics |
| **default** | All other agents | name, goals, communication_style |

### Accessing User Context in Agents

```python
def execute(self, task, context, scifi_context, spider_context):
    # Session 858: Extract user context
    user_context = context.get('user', {})

    # Quick access fields
    user_name = context.get('user_name', '')
    user_skills = context.get('user_skills', [])
    user_goals = context.get('user_goals', [])
    user_communication_style = context.get('user_communication_style', 'professional')

    # Full user context dict
    if user_context.get('has_user_context'):
        risk_tolerance = user_context.get('risk_tolerance', 'moderate')
        memory_summary = user_context.get('memory_summary', '')
```

### Learning Feedback Loop

When agents succeed, patterns are recorded for future personalization:

```python
# In AgentRouter after successful execution
UserMemoryContext.objects.create(
    user=self.user,
    memory_type='success_pattern',
    content=f"Successfully used {agent_name} for: {task[:200]}",
    source=f'agent:{agent_name}',
)
```

---

## Request Flow

### Example: "Create a cyberpunk logo"

```
1. User Request
   │
   ▼
2. PersonalAssistantAgent
   │ - Parses intent
   │ - Detects: "creation" + "logo" -> ImageAgent
   │
   ▼
3. AgentRouter.route("ImageAgent", task)
   │ - Injects sci-fi context (mood, memories)
   │ - Injects spider context (trends)
   │ - Injects user context (Session 858)
   │
   ▼
4. ImageAgent.execute()
   │ - _get_relevant_knowledge_for_task()
   │ - _get_fresh_spider_intelligence(['creative'])
   │ - _build_prompt() with injected context
   │ - Uses context['user'] for personalization
   │
   ▼
5. GPT-5-mini Function Call
   │ - Decides: generate_image tool
   │ - Parameters: {prompt: "cyberpunk logo...", model: "sd3"}
   │
   ▼
6. Stability AI API
   │ - POST /v2beta/stable-image/generate/sd3
   │ - Returns: base64 image
   │
   ▼
7. ImageAgent._record_learning_outcome()
   │ - Stores execution memory
   │ - Updates XP/evolution
   │
   ▼
8. Response to User
   │ - Image displayed in UI
   │ - History entry created
```

### Example: "What's trending in AI?"

```
1. User Request
   │
   ▼
2. PersonalAssistantAgent._is_question() = True
   │ - No agent delegation needed
   │ - Direct spider query
   │
   ▼
3. SpiderIntelligenceService.get_tech_trends(topic_filter='ai')
   │ - Queries SpiderData with embeddings
   │ - Filters: AI/ML keywords, word boundaries
   │ - Excludes: Shopping, weather, GIFs
   │
   ▼
4. Return trending articles with clickable links
```

---

## Database Schema

### Core Models (`core/models_unified_system.py` - 10,596 lines)

```python
# Spider Data
class SpiderData(models.Model):
    spider_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    title = models.TextField()
    description = models.TextField()
    url = models.URLField()
    embedding = models.JSONField(null=True)  # OpenAI embedding
    fetched_at = models.DateTimeField()

# Agent System
class Agent(models.Model):
    name = models.CharField(max_length=255)
    agent_type = models.CharField(max_length=50)
    capabilities = models.JSONField()
    mood = models.CharField(max_length=50)
    xp = models.IntegerField(default=0)
    level = models.CharField(max_length=50)

# Knowledge
class AgentKnowledgeSource(models.Model):
    agent = models.ForeignKey(Agent)
    knowledge_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    knowledge_value = models.TextField()
    embedding = models.JSONField(null=True)

# Sci-Fi Features
class AgentMemory(models.Model):
    agent = models.ForeignKey(Agent)
    memory_type = models.CharField(max_length=50)
    content = models.TextField()
    embedding = models.JSONField(null=True)

class AgentConversation(models.Model):
    participants = models.ManyToManyField(Agent)
    topic = models.CharField(max_length=255)
    messages = models.JSONField()
    conclusion = models.TextField()

class AgentDream(models.Model):
    agent = models.ForeignKey(Agent)
    dream_content = models.TextField()
    dream_type = models.CharField(max_length=50)

# Revenue Pipeline
class Opportunity(models.Model):
    title = models.CharField(max_length=255)
    score = models.FloatField()
    source = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
```

### Legal Models (`core/models_legal.py`)

```python
class CaseProfile(models.Model):
    user = models.ForeignKey(User)
    case_number = models.CharField(max_length=100)
    court_name = models.CharField(max_length=255)
    case_type = models.CharField(max_length=50)

class Party(models.Model):
    case = models.ForeignKey(CaseProfile)
    role = models.CharField(max_length=50)  # petitioner/respondent
    name = models.CharField(max_length=255)

class LitigationDocument(models.Model):
    case = models.ForeignKey(CaseProfile)
    document_type = models.CharField(max_length=50)
    litigation_role = models.CharField(max_length=50)  # motion/response/reply
    title = models.CharField(max_length=255)
    content = models.TextField()
```

---

## File Structure

```
unified-donkey-betz/
├── core/                          # Main Django app
│   ├── agents/                    # 27 clean agents
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Abstract base
│   │   ├── personal_assistant_agent.py
│   │   ├── image_agent.py
│   │   ├── video_agent.py
│   │   ├── audio_agent.py
│   │   ├── research_agent.py
│   │   ├── legal/
│   │   │   └── legal_doc_drafter_agent.py
│   │   └── ...
│   ├── super_platform/            # Orchestration
│   │   ├── coordinator.py
│   │   ├── query_classifier.py
│   │   ├── context_aggregator.py
│   │   └── prompt_builder.py
│   ├── services/                  # Business logic
│   │   ├── spider_intelligence.py
│   │   ├── unified_intelligence_search.py
│   │   └── ...
│   ├── prompts/                   # Prompt registry
│   │   ├── registry.py
│   │   └── tool_descriptions.py
│   ├── models_unified_system.py   # 10,596 lines
│   ├── models_legal.py
│   ├── agent_router.py
│   ├── views_image.py             # 13,700 lines
│   ├── views_video.py             # 8,800 lines
│   └── views_legal.py
│
├── ai_core/                       # AI subsystem
│   ├── spiders/                   # Spider network
│   │   ├── spider_registry.py     # 64 spiders
│   │   ├── specialized/           # Individual spiders
│   │   └── real_data_collector.py
│   └── templates/
│       └── ai_image_studio.html   # 55,625 lines
│
├── content/                       # Media handling
│   ├── image_generation.py        # Stability AI
│   ├── video_provider.py          # Runway ML
│   ├── elevenlabs_provider.py     # ElevenLabs
│   └── replicate_provider.py      # Replicate
│
├── resolve_node/                  # DaVinci Resolve (UNUSED!)
│   ├── app.py                     # FastAPI server
│   ├── resolve_controller.py
│   └── README.md
│
├── docs/                          # Documentation
│   ├── INDEX.md                   # Main index
│   ├── ARCHITECTURE.md            # This file
│   ├── AGENTS.md
│   ├── SPIDERS.md
│   └── ...
│
└── CLAUDE.md                      # Session entry point
```

---

## Technical Notes

### GPT-5-mini Configuration

**Important:** GPT-5-mini is a reasoning model with different parameters!

```python
# CORRECT for gpt-5-mini
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000,  # High for reasoning + output
    timeout=120
)

# WRONG - will cause errors
response = client.chat.completions.create(
    model="gpt-5-mini",
    max_tokens=1000,      # Wrong parameter name
    temperature=0.7       # Not supported for reasoning models
)
```

### Celery Beat Schedules

The Celery beat schedule is split-owned across four sources by design: the primary static schedule lives in `core/celery.py` (`app.conf.beat_schedule` dict, code-first authoritative source per Session 1157 option A); the runtime store is `django-celery-beat`'s `PeriodicTask` rows; the bridge/bootstrap commands `core/management/commands/add_critical_celery_tasks` + `sync_celery_beat` + `sync_celery_schedules` materialize and repair those DB rows from the static dict without defining scheduling semantics; and `core/settings.py` carries the routing/config layer (`CELERY_BEAT_SCHEDULER = DatabaseScheduler`). Since Session 1077 the schedule has been in **minimal/token-conservation mode** — limited to essential health checks and DB-hygiene cleanups; the broader agent/spider/intelligence schedules from earlier sessions are preserved in git history but no longer active.

Illustrative shape (live entries live in `core/celery.py:app.conf.beat_schedule`):

```python
# core/celery.py — canonical
app.conf.beat_schedule = {
    'heart-service-heartbeat': {
        'task': 'core.tasks.run_heartbeat',
        'schedule': 600,  # Every 10 min
        'options': {'queue': 'broadcast', 'expires': 600},
    },
    'cleanup-expired-fleet-events': {
        'task': 'core.tasks.cleanup_expired_fleet_events',
        'schedule': crontab(hour=2, minute=25),  # 2:25 AM MST daily
        'options': {'queue': 'broadcast', 'expires': 3600},
    },
    # ... ~75 more entries — see core/celery.py for the full canonical list
}
```

---

## Performance Considerations

### Database Indexes
- `SpiderData.embedding` - GIN index for similarity search
- `AgentKnowledgeSource.embedding` - GIN index
- `SpiderData.fetched_at` - B-tree for recency queries

### Caching
- Redis for session data
- Embedding cache for repeated queries
- Spider data cache (15-minute TTL)

### Rate Limits
- Stability AI: Concurrent request limits
- Runway ML: Task polling intervals
- OpenAI: Token limits per minute

---

## ConceptForge: Autonomous Think Tank Pipeline (Session 863)

Transforms published content into comprehensive dossiers through 6-stage analysis.

```
SelfBlog (published, quality >= 0.80)
    ↓ [Django signal]
ConceptForgeRun
    ↓ [domain router]
DomainLab (Legal | Market | Tech | Content | Startup | Career)
    ↓
┌──────────────────────────────────────────────────────────────┐
│ Stage 1: Research   → ResearchAgent + Persona Advisors      │
│ Stage 2: Debate     → Legendary Advisors (pro/con)          │
│ Stage 3: Feasibility→ SystemsArchitectAgent                 │
│ Stage 4: Risk       → RiskAnalysisAgent + Legal Personas    │
│ Stage 5: Market     → MarketIntelligenceAgent               │
│ Stage 6: Synthesis  → ThinkingAgent → Dossier               │
└──────────────────────────────────────────────────────────────┘
```

**Key Design:**
- Config-first labs (no migrations needed for new domains)
- Advisor panel snapshotted per run (reproducibility)
- Legendary advisors as constraints, core agents as writers
- Gate logic: quality_score >= 0.80 + strategic_tag

**Files:**
- `core/conceptforge/` - Package with labs, panels, orchestrator
- `core/models_conceptforge.py` - Run tracking models
- `core/signals.py` - SelfBlog publish trigger

See [CONCEPTFORGE.md](CONCEPTFORGE.md) for full documentation.

---

## Diagnostic Pipeline (Session 856)

Transforms failure noise into actionable root cause analysis:

```
Failure Event
    ↓
FailureDetection (Phase 1: What happened)
    ↓ [signature grouping]
FailureSignature (deduplication + tracking)
    ↓ [evidence gathering]
FailureDiagnosis (Phase 2: Why it happened, blast radius)
    ↓ [solution ranking]
FailurePrescription (Phase 3: What to do, priority scoring)
    ↓
Initiative (auto-created remediation project)
```

**Files:** `core/models_diagnostic_pipeline.py`, `core/services/autonomous_remediation_orchestrator.py`

---

## Signal Intelligence + Initiative Pipeline (Sessions 900-904)

Spider data flows through signal clustering into auto-generated topics that trigger conversations, producing initiatives tracked through a 5-stage pipeline:

```
SpiderData (77 spiders)
    ↓ [SignalAggregationService, every 30 min]
SignalCluster (pattern detection: strength, confidence, novelty)
    ↓ [auto-topic generation]
AutoTopic (rationale + domain)
    ↓ [HiveMindSession creation]
Goal-Driven Conversation (agent router, objectives, success criteria)
    ↓ [conclusion parsing]
Initiative (5 stages) + InitiativeActionItem (next steps)
```

**Initiative UI:** Stages view (grouped by phase 1-5), List view, Cards view. Priority scoring: `impact*0.4 + urgency*0.2 + confidence*0.2 + revenue*0.2`. 52 active initiatives after Session 961c cleanup (from 568).

**Files:** `core/models_signal_intelligence.py`, `core/services/signal_aggregation_service.py`, `core/models_document_registry.py`

---

## Content Deliberation Pipeline (Session 964)

Multi-agent content review replacing single-agent blog generation:

```
SpiderData + SignalCluster
    ↓ [ClaimsPackBuilder]
ClaimsPack (deterministic IDs: C-xxxxxxxxxx)
    ↓ [ContentWriterAgent]
Blog Draft (citing [C-xxx] claims)
    ↓ [ContentReviewPanelV2]
3 Reviewers: Skeptic + FactChecker + DomainPersona
    ↓ [DecisionEnforcer]
Verdict: PUBLISH / REVISE / KILL
    ↓ [PublishGate]
SelfBlog (with stats_snapshot['deliberation'])
```

**v1 vs v2:** v1 (direct generation) and v2 (deliberation) run side-by-side for A/B testing. API: `POST /api/v1/research/self-blog/generate-v2/`. Replay: `GET /api/blog/<uuid>/deliberation/`.

**Files:** `core/services/claims_pack_builder.py`, `core/services/content_review_panel_v2.py`, `core/services/content_deliberation_runner.py`

---

## PA Intelligence System (Sessions 959-969b)

The Personal Assistant (PA) is an analytical advisor with 89 tools and real-time system awareness:

```
User Message
    ↓ [UnifiedPAEntrypoint._detect_intent_and_route()]
Intent + Tool Name (47 tool handlers)
    ↓ [INTENT_ENRICHMENT_MAP]
Enrichment Services (5 available, fired per intent):
  - PAIntelligenceEnricher
  - BlogPerformanceContext
  - DomainContentContext (9 domains)
  - SpiderContext
  - AdvisorContext
    ↓ [ToolDispatcher.execute()]
Tool Result (ToolResult dataclass)
    ↓ [Analytical Prompt Builder]
LLM Analysis (intent-specific directives)
    ↓
Structured Response (data first, analysis after)
```

**Telemetry Tools (969b):** `recent_activity_tool` (system activity snapshot), `system_health_tool` (health assessment: healthy/degraded/critical), `error_summary_tool` (failure patterns: severity none/low/moderate/high).

**Files:** `core/services/unified_pa_entrypoint.py` (89 tools, intent routing), `core/services/tool_dispatcher.py` (47 handlers), `core/services/pa_intelligence_enricher.py`

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Detailed agent documentation (76 agents)
- [SPIDERS.md](SPIDERS.md) - Spider network details (77 spiders)
- [DATABASE_MODEL_REFERENCE.md](DATABASE_MODEL_REFERENCE.md) - Complete model reference (386+ models)
- [SERVICES.md](SERVICES.md) - Services layer (134 services)
- [CONCEPTFORGE.md](CONCEPTFORGE.md) - Autonomous think tank pipeline
- [DREAM_INITIATIVE_WORKFLOW.md](DREAM_INITIATIVE_WORKFLOW.md) - Dream -> Initiative 5-stage pipeline
- [EXTERNAL_APIS.md](EXTERNAL_APIS.md) - API integration details
- [KNOWLEDGE_PIPELINE.md](KNOWLEDGE_PIPELINE.md) - Learning flow
- [API_PATH_POLICY.md](API_PATH_POLICY.md) - API path conventions
