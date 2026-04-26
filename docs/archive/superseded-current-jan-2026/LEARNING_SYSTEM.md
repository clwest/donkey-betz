<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Agent learning-loop notes
>
> **Where to look now:**
> - [docs/topics/agent-system.md](/docs/topics/agent-system.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Unified Learning System Documentation

**Generated:** Session 666 (January 5, 2026)
**Status:** Comprehensive Guide to ALL Learning in the Platform

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Learning Entities Overview](#learning-entities-overview)
3. [Agent Learning Infrastructure](#agent-learning-infrastructure)
4. [Learning Loop Service](#learning-loop-service)
5. [Collective Intelligence](#collective-intelligence)
6. [Sci-Fi Features Learning](#sci-fi-features-learning)
7. [Learning Bridges](#learning-bridges)
8. [Autonomous Situations Learning](#autonomous-situations-learning)
9. [Pilot & Experiment Learning](#pilot--experiment-learning)
10. [ML Scoring Engine](#ml-scoring-engine)
11. [Spider Intelligence Learning](#spider-intelligence-learning)
12. [Data Flow Architecture](#data-flow-architecture)
13. [Database Models](#database-models)
14. [Verification Commands](#verification-commands)
15. [Troubleshooting](#troubleshooting)

---

## Executive Summary

The Unified Donkey Betz Platform has **12 interconnected learning systems** that enable continuous improvement across all components. Learning happens at multiple levels:

| Level | What Learns | How It Learns |
|-------|-------------|---------------|
| **Agent** | 72 agents | Execution outcomes, memory creation, knowledge sharing |
| **Collective** | Agent ecosystem | Cross-agent knowledge transfer, collaboration insights |
| **Sci-Fi** | Individual agents | XP/Evolution, Dreams, Memory Palace, Mood adaptation |
| **Bridges** | System connections | Signal-based automatic learning (8 bridges) |
| **Autonomous** | 19 situations | Outcome tracking, confidence adjustment |
| **Governance** | Pilot gates | Success/failure feedback to decisions |
| **ML Models** | Scoring engine | XGBoost retraining on outcomes |
| **Spiders** | 77 data collectors | Trend analysis, source authority scoring |

### Key Metrics

| Component | Count | Learning Active |
|-----------|-------|-----------------|
| Agents with learning hooks | 72 | Yes |
| AgentKnowledgeSource records | ~2,000+ | Yes |
| AgentMemory records | ~300+ | Yes |
| AgentEvolution records | ~50+ | Yes |
| Learning Bridges | 8 | Yes |
| Autonomous Situations | 19 | Yes |

---

## Learning Entities Overview

### What Learns in This System?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED LEARNING ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│  │  72 AGENTS      │     │  77 SPIDERS     │     │  25 ADVISORS    │   │
│  │  ─────────────  │     │  ─────────────  │     │  ─────────────  │   │
│  │  • Execute      │     │  • Collect      │     │  • Consult      │   │
│  │  • Learn        │     │  • Analyze      │     │  • Advise       │   │
│  │  • Share        │     │  • Index        │     │  • Learn prefs  │   │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘   │
│           │                       │                       │             │
│           └───────────────────────┼───────────────────────┘             │
│                                   ▼                                      │
│           ┌───────────────────────────────────────────┐                 │
│           │         LEARNING LOOP SERVICE             │                 │
│           │  ─────────────────────────────────────── │                 │
│           │  • Record outcomes (success/failure)      │                 │
│           │  • Award XP to agents                     │                 │
│           │  • Detect patterns                        │                 │
│           │  • Update agent selection weights         │                 │
│           └───────────────────────┬───────────────────┘                 │
│                                   │                                      │
│           ┌───────────────────────┼───────────────────┐                 │
│           │                       ▼                   │                 │
│  ┌────────┴────────┐     ┌─────────────────┐  ┌──────┴───────┐         │
│  │ 8 LEARNING      │     │ COLLECTIVE      │  │ 19 AUTONOMOUS │         │
│  │ BRIDGES         │     │ INTELLIGENCE    │  │ SITUATIONS    │         │
│  │ ────────────── │     │ ─────────────── │  │ ───────────── │         │
│  │ • Revenue      │     │ • Aggregate     │  │ • Market Intel │         │
│  │ • Agent Exec   │     │ • Share         │  │ • Content Gen  │         │
│  │ • Application  │     │ • Gap detect    │  │ • Blockchain   │         │
│  │ • Spider Data  │     │ • Improvements  │  │ • Stocks       │         │
│  │ • Advisor      │     │                 │  │ • Narratives   │         │
│  │ • Personalize  │     │                 │  │ • Jobs         │         │
│  │ • Collaborate  │     │                 │  │ • Legal        │         │
│  │ • Sports Bet   │     │                 │  │ • Research     │         │
│  └─────────────────┘     └─────────────────┘  └───────────────┘         │
│                                                                          │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│  │ SCI-FI FEATURES │     │ PILOT/EXPERIMENT│     │ ML SCORING      │   │
│  │ ─────────────── │     │ ─────────────── │     │ ─────────────── │   │
│  │ • Evolution/XP  │     │ • Readiness Gate│     │ • XGBoost model │   │
│  │ • Dreams        │     │ • Success track │     │ • SHAP explain  │   │
│  │ • Memory Palace │     │ • Outcome learn │     │ • Auto-retrain  │   │
│  │ • Mood System   │     │ • KPI ownership │     │ • Feature eng   │   │
│  │ • Rivalries     │     │                 │     │                 │   │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Learning Infrastructure

### Location
- **Primary:** `core/agents/base_agent.py` (lines 1585-1830)
- **Models:** `core/models_unified_system.py`

### Learning Hooks in BaseAgent

Every agent inherits these learning methods from `BaseAgent`:

#### 1. `_record_learning_outcome()` (line 1587)

Records execution outcomes for learning, XP, and pattern detection.

```python
def _record_learning_outcome(
    self,
    result: 'AgentResult',
    task: str,
    context: Dict[str, Any],
    spider_data_used: bool = False,
    scifi_context_used: bool = False,
    success: bool = None
) -> Optional[str]:
    """
    Called at end of execute() to:
    1. Record outcome for learning loop
    2. Award XP to agent on success
    3. Detect patterns in interactions
    """
```

**What gets recorded:**
- Query type (creation, editing, research, question, other)
- Agents used
- Execution time
- Success/failure
- Tool calls made
- Decisions made

#### 2. `_create_execution_memory()` (line 1660)

Creates persistent memories from meaningful interactions.

```python
def _create_execution_memory(
    self,
    result: 'AgentResult',
    task: str,
    memory_type: str = "interaction",
    importance: float = 0.5
) -> Optional[Any]:
    """
    Memory types:
    - success: What worked
    - failure: What didn't work
    - preference: User preferences discovered
    - technique: Learned techniques
    - insight: Discoveries
    - interaction: General interaction
    """
```

**Stored in:** `AgentMemory` model

#### 3. `_share_knowledge()` (line 1764)

Shares learned knowledge for cross-agent learning.

```python
def _share_knowledge(
    self,
    knowledge_type: str,
    title: str,
    knowledge_value: Any,
    confidence: float = 0.8
) -> Optional[Any]:
    """
    Knowledge types:
    - trend: Trending topics/patterns
    - market: Market insights
    - opportunity: Business opportunities
    - competitor: Competitor intelligence
    - pricing: Pricing insights
    - user_behavior: User behavior patterns
    - content_idea: Content ideas
    - tool_discovery: New tools/techniques
    """
```

**Stored in:** `AgentKnowledgeSource` model

#### 4. `_get_relevant_knowledge_for_task()` (line 408)

Retrieves learned knowledge to enhance task execution.

```python
def _get_relevant_knowledge_for_task(self, task: str, limit: int = 5) -> List[Dict]:
    """
    Hybrid retrieval:
    1. Semantic search on spider data (embeddings)
    2. Keyword matching on AgentKnowledgeSource

    Returns knowledge from:
    - This agent's past executions
    - Other agents' shared knowledge
    - Spider-derived intelligence
    """
```

#### 5. `_track_contribution()` (line 1722)

Tracks agent contributions to created content.

```python
def _track_contribution(
    self,
    content_type: str,
    content_id: int,
    contribution_type: str = "primary_creator",
    contribution_score: float = 1.0
) -> Optional[Any]:
    """
    Contribution types:
    - primary_creator
    - assistant
    - reviewer
    - optimizer
    """
```

**Stored in:** `AgentContribution` model

### Usage Pattern in Agents

```python
class MyAgent(BaseAgent):
    def execute(self, task: str, context: Dict) -> AgentResult:
        # 1. Get relevant knowledge before execution
        knowledge = self._get_relevant_knowledge_for_task(task)

        # 2. Execute task with knowledge context
        result = self._perform_task(task, knowledge)

        # 3. Record learning outcome
        self._record_learning_outcome(result, task, context)

        # 4. Create memory if significant
        if result.success:
            self._create_execution_memory(result, task, "success", 0.7)

        # 5. Share knowledge if valuable
        if result.insights:
            self._share_knowledge("insight", "Task insight", result.insights)

        return result
```

---

## Learning Loop Service

### Location
- **Service:** `core/super_platform/learning_loop.py`
- **Model:** `CoordinatorOutcome` in `core/models_unified_system.py`

### Purpose

The Learning Loop Service enables continuous improvement:

```
Action → Outcome → Pattern → Adaptation → Better Action
```

### Key Classes

#### OutcomeType (Enum)
```python
class OutcomeType(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    USER_SATISFIED = "user_satisfied"
    USER_UNSATISFIED = "user_unsatisfied"
```

#### FeedbackType (Enum)
```python
class FeedbackType(Enum):
    EXPLICIT_POSITIVE = "explicit_positive"   # User said good
    EXPLICIT_NEGATIVE = "explicit_negative"   # User said bad
    IMPLICIT_POSITIVE = "implicit_positive"   # User used result
    IMPLICIT_NEGATIVE = "implicit_negative"   # User ignored/retried
    ENGAGEMENT = "engagement"                  # User engaged further
```

#### LearningLoopService

```python
class LearningLoopService:
    """
    Core methods:
    - record_outcome(): Store execution result
    - get_agent_performance(): Query agent metrics
    - get_query_type_stats(): Analyze by query type
    - get_best_agents_for_query(): Adaptive selection
    - award_xp(): Reward successful agents
    """

    # Thresholds
    MIN_SAMPLES_FOR_LEARNING = 5
    CONFIDENCE_THRESHOLD = 0.6
    PERFORMANCE_WINDOW_DAYS = 30
```

### How It Works

1. **Outcome Recording**
   ```python
   outcome_id = learning_loop.record_outcome(
       query_type='research',
       query_text='Find AI trends',
       execution_mode='agent',
       agents_used=['ResearchAgent'],
       response='Found 10 trends...',
       execution_time_ms=1500,
       success=True
   )
   ```

2. **Performance Analysis**
   ```python
   performance = learning_loop.get_agent_performance('ResearchAgent')
   # Returns: success_rate, avg_execution_time, best_query_types, trend
   ```

3. **Adaptive Agent Selection**
   ```python
   best_agents = learning_loop.get_best_agents_for_query('research')
   # Returns agents ranked by success rate for query type
   ```

4. **XP Rewards**
   - On success: Agent receives XP via Evolution system
   - XP amount varies by task complexity
   - Contributes to agent leveling

---

## Collective Intelligence

### Location
- **Service:** `core/services/collective_intelligence.py`
- **Supporting:** `core/services/agent_collaboration.py`

### Purpose

Harnesses combined intelligence of all agents to:
- Aggregate insights from multiple agents on topics
- Generate multi-perspective reports
- Identify knowledge gaps
- Propose agent improvements

### Key Classes

#### AgentInsight
```python
@dataclass
class AgentInsight:
    agent_name: str
    topic: str
    insight_type: str    # observation, recommendation, warning, opportunity
    content: str
    confidence: float    # 0.0 - 1.0
    supporting_data: Dict
    timestamp: datetime
```

#### CollectiveReport
```python
@dataclass
class CollectiveReport:
    id: str
    topic: str
    summary: str
    participating_agents: List[str]
    insights: List[AgentInsight]
    recommendations: List[Dict]
    consensus_score: float      # How much agents agreed
    confidence_score: float     # Overall confidence
    knowledge_gaps: List[str]
```

### Key Methods

```python
class CollectiveIntelligenceService:

    def aggregate_insights(self, topic: str, domains: List[str] = None):
        """Gather insights from all relevant agents"""

    def generate_report(self, topic: str, depth: str = 'standard'):
        """Generate comprehensive multi-agent report"""

    def identify_knowledge_gaps(self, domain: str):
        """Find areas where agents lack knowledge"""

    def propose_improvements(self, agent_name: str):
        """Suggest improvements based on learning data"""
```

### How Knowledge Flows

```
Agent A learns → Shares to AgentKnowledgeSource
                         ↓
                 CollectiveIntelligenceService queries
                         ↓
Agent B retrieves → Uses in task execution
                         ↓
                 Better outcome → More learning
```

---

## Sci-Fi Features Learning

### 1. Agent Evolution (XP System)

**Model:** `AgentEvolution` in `core/models_unified_system.py` (line 11054)

```python
class AgentEvolution(models.Model):
    agent = OneToOneField('Agent')

    # XP and Level
    total_xp = PositiveIntegerField(default=0)
    current_level = PositiveIntegerField(default=1)
    xp_to_next_level = PositiveIntegerField(default=100)

    # Stats
    tasks_completed = PositiveIntegerField(default=0)
    tasks_failed = PositiveIntegerField(default=0)
    collaborations_completed = PositiveIntegerField(default=0)

    # Bonuses from leveling
    speed_bonus = FloatField(default=0.0)       # % faster
    quality_bonus = FloatField(default=0.0)     # % better output
    creativity_bonus = FloatField(default=0.0)  # % more creative
    efficiency_bonus = FloatField(default=0.0)  # % less resources
```

**Level Titles (1-10):**
1. Novice → 2. Apprentice → 3. Journeyman → 4. Expert → 5. Master
6. Grandmaster → 7. Legend → 8. Mythic → 9. Transcendent → 10. Omniscient

**XP Curve:** Exponential - `100 * (1.5 ^ (level - 1))`

**How agents earn XP:**
- Task completion (+10-50 XP)
- Successful collaboration (+25 XP)
- Knowledge sharing (+5 XP)
- User satisfaction (+20 XP)

### 2. Agent Dreams

**Model:** `AgentDream` in `core/models_unified_system.py` (line 8374)

```python
class AgentDream(models.Model):
    agent = ForeignKey('Agent')
    title = CharField(max_length=200)
    content = TextField()

    dream_type = CharField(choices=[
        ('creative_idea', 'Creative Idea'),
        ('what_if', 'What If?'),
        ('mashup', 'Mashup'),
        ('prediction', 'Prediction'),
        ('improvement', 'Improvement'),
        ('observation', 'Observation'),
        ('wild_thought', 'Wild Thought'),
    ])

    # Quality scores
    vividness_score = FloatField()      # 0-1
    creativity_score = FloatField()     # 0-1
    actionability_score = FloatField()  # 0-1 - How implementable
    relevance_score = FloatField()      # 0-1 - Relevance to projects

    # Productization pipeline
    promoted_to_decision = BooleanField()  # → Boardroom
    decision_outcome = CharField()          # pending/approved/deferred/rejected
```

**Learning from Dreams:**
- 10% of dreams are based on `[Learned]` knowledge from other agents
- High-scoring dreams get promoted to Boardroom for decisions
- Outcomes feed back into agent learning

### 3. Agent Memory (Memory Palace)

**Model:** `AgentMemory` in `core/models_unified_system.py` (line 9368)

```python
class AgentMemory(models.Model):
    agent = ForeignKey('Agent')
    title = CharField(max_length=200)
    content = TextField()

    memory_type = CharField(choices=[
        ('success', 'Successful Outcome'),
        ('failure', 'Failed Attempt'),
        ('preference', 'User Preference'),
        ('technique', 'Learned Technique'),
        ('insight', 'Discovery/Insight'),
    ])

    # Retrieval
    importance_score = FloatField()  # 0-1
    embedding = VectorField()        # For semantic search

    # Decay
    access_count = IntegerField()
    last_accessed = DateTimeField()
```

**Memory Palace Retrieval:**
- Semantic similarity via embeddings
- Importance weighting
- Recency bias
- Access frequency boost

### 4. Agent Mood System

**Model:** `AgentMood` in `core/models_unified_system.py` (line 10302)

```python
class AgentMood(models.Model):
    agent = ForeignKey('Agent')

    current_mood = CharField(choices=[
        ('inspired', 'Inspired'),
        ('focused', 'Focused'),
        ('curious', 'Curious'),
        ('confident', 'Confident'),
        ('contemplative', 'Contemplative'),
        ('energetic', 'Energetic'),
        ('calm', 'Calm'),
        ('frustrated', 'Frustrated'),
        ('tired', 'Tired'),
        ('playful', 'Playful'),
    ])

    # Mood dimensions (0-1)
    creativity_level = FloatField()
    precision_level = FloatField()
    sociability_level = FloatField()
    risk_tolerance = FloatField()
    intensity = FloatField()
```

**How mood affects learning:**
- Success → Mood improves (more confident)
- Failure → Mood may dip (more contemplative)
- Mood influences task selection preferences
- High creativity mood → More innovative outputs

---

## Learning Bridges

### Location
- **Base:** `core/learning_bridges/base.py`
- **Implementations:** `core/learning_bridges/*.py`

### Purpose

Learning Bridges are **signal-based automatic connections** between system events and learning mechanisms. They fire automatically when events occur.

### Bridge Architecture

```python
class LearningBridge(ABC):
    """All bridges implement these methods"""

    @abstractmethod
    def process_event(self, event_data: Any) -> Dict:
        """Main event processing"""

    @abstractmethod
    def _extract_patterns(self, event_data: Any) -> Dict:
        """Extract learnable patterns"""

    @abstractmethod
    def _update_learning(self, patterns: Dict) -> None:
        """Update learning records"""

    @abstractmethod
    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Generate actionable insights"""
```

### 8 Active Bridges

| Bridge | File | Triggers On | What It Learns |
|--------|------|-------------|----------------|
| **Revenue Attribution** | `revenue_attribution_bridge.py` | Payment received | What makes money |
| **Agent Execution** | `agent_execution_bridge.py` | Agent completes task | Agent effectiveness |
| **Application Outcome** | `application_outcome_bridge.py` | Job application result | What applications succeed |
| **Spider Data** | `spider_data_bridge.py` | New spider data | Data quality, source reliability |
| **Advisor Feedback** | `advisor_feedback_bridge.py` | Advisor consultation | Advisor effectiveness |
| **Personalization** | `personalization_bridge.py` | User interaction | User preferences |
| **Collaboration** | `collaboration_bridge.py` | Multi-agent collab | Team effectiveness |
| **Sports Betting** | `sports_betting_bridge.py` | Bet outcome | Prediction accuracy |

### Example: Agent Execution Bridge

```python
class AgentExecutionBridge(LearningBridge):
    def process_event(self, event_data):
        """Process agent execution event"""
        patterns = self._extract_patterns(event_data)

        # Update agent performance metrics
        self._update_learning(patterns)

        # Award XP if successful
        if patterns['success']:
            self._award_xp(event_data['agent'], patterns['xp_amount'])

        # Generate insights
        insights = self._generate_insights(patterns)

        return {
            'processed': True,
            'patterns': patterns,
            'insights': insights
        }
```

---

## Autonomous Situations Learning

### Location
- **Models:** `core/models_autonomous_situations.py`
- **Sessions:** `AutonomousSituationSession` model

### 19 Autonomous Situations

Each situation has its own learning loop:

| Situation | Domain | What It Learns |
|-----------|--------|----------------|
| Market Intelligence | Financial | Bull/Bear accuracy, trend prediction |
| Autonomous Content Studio | Content | Topic performance, timing |
| Narrative Drift Detector | Research | Narrative shift patterns |
| Blockchain Alerts | Crypto | Whale behavior, exploit patterns |
| Stock Intelligence | Stocks | Price movement predictors |
| SEC Filing Analyzer | Financial | Filing impact patterns |
| Crypto Sentiment | Crypto | Sentiment accuracy |
| Earnings Predictor | Financial | Earnings surprise factors |
| Design Trends | Creative | Trend emergence patterns |
| Viral Predictor | Content | Virality factors |
| Thumbnail Optimizer | Creative | Click-through patterns |
| Job Match | Income | Job fit predictors |
| Freelance Scout | Income | Gig success factors |
| Side Hustle Detector | Income | Opportunity quality |
| Tech Stack Tracker | Research | Technology adoption |
| AI Model Monitor | Research | Model performance |
| Course Analyzer | Research | Course value |
| Case Law Monitor | Legal | Precedent relevance |
| Regulatory Detector | Legal | Regulatory impact |

### Learning Mechanism

```python
class AutonomousSituationSession(models.Model):
    situation_type = CharField()

    # Execution data
    started_at = DateTimeField()
    completed_at = DateTimeField()

    # Outcomes
    success = BooleanField()
    confidence_score = FloatField()

    # Learning
    outcome_tracked = BooleanField()
    outcome_result = CharField()  # correct/incorrect/partial

    # This feeds back to situation confidence
```

**Learning Flow:**
1. Situation fires (scheduled or event-triggered)
2. Generates prediction/alert/content
3. Tracks outcome (e.g., was prediction correct?)
4. Adjusts confidence multiplier for future runs
5. High-confidence patterns get reinforced

---

## Pilot & Experiment Learning

### Location
- **Models:** `core/models_pilot_readiness.py`
- **Services:** `core/services/experiment_*.py`

### The Governance Pipeline

```
Dream → Boardroom Decision → [PILOT READINESS GATE] → Pilot → Full Implementation
                                                         ↓
                                                    Learning
```

### Pilot Readiness Gate

```python
class PilotReadinessGate(models.Model):
    decision = OneToOneField('AgentDecisionSummary')

    status = CharField(choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('ready', 'Ready for Review'),
        ('approved', 'Approved for Pilot'),
        ('blocked', 'Blocked'),
        ('waived', 'Waived (Low Risk)'),
    ])

    risk_level = CharField(choices=[
        ('low', 'Low - Auto-waivable'),
        ('medium', 'Medium - Basic checklist'),
        ('high', 'High - Full safety review'),
        ('critical', 'Critical - Executive approval'),
    ])

    # Success/Failure criteria for learning
    success_criteria = TextField()
    failure_criteria = TextField()

    # Phase timestamps for latency analysis
    decision_made_at = DateTimeField()
    gate_approved_at = DateTimeField()
    pilot_started_at = DateTimeField()
    pilot_completed_at = DateTimeField()
```

### Experiment Tracking

```python
class ExperimentTracking(models.Model):
    gate = ForeignKey('PilotReadinessGate')

    # KPI ownership
    kpi_owner = CharField()      # Agent responsible
    primary_kpi = CharField()     # What we're measuring
    target_value = FloatField()   # Success threshold
    current_value = FloatField()  # Actual result

    # Outcome
    outcome = CharField(choices=[
        ('success', 'Success - Met KPIs'),
        ('partial', 'Partial - Some KPIs met'),
        ('failure', 'Failure - Did not meet KPIs'),
    ])
```

### Learning Flow

1. **Decision made** → Gate created
2. **Pilot runs** → Metrics collected
3. **Pilot completes** → Outcome recorded
4. **Learning extracted:**
   - What made pilots successful?
   - Which risk levels need more artifacts?
   - Which agents own successful KPIs?
5. **Future decisions** use this learning for better risk assessment

---

## ML Scoring Engine

### Location
- **Service:** `core/services/ml_scoring_engine.py`

### Purpose

XGBoost-based scoring with SHAP explainability for opportunity ranking.

### Architecture

```python
class MLScoringEngine:
    """
    Provides:
    1. Feature extraction from SpiderData
    2. XGBoost-based scoring
    3. SHAP explanations
    4. Hybrid scoring: 60% ML + 40% rule-based
    5. Model versioning
    """
```

### Features Extracted (15 total)

```python
FEATURE_NAMES = [
    'relevance_score',        # 0-100 from spider
    'source_authority',       # Source quality score
    'data_freshness_hours',   # Hours since creation
    'title_length',           # Title character count
    'has_url',               # Has source URL
    'category_tech',         # One-hot categories
    'category_financial',
    'category_jobs',
    'category_creative',
    'category_news',
    'keyword_ai',            # Keyword presence
    'keyword_trending',
    'keyword_urgent',
    'keyword_opportunity',
    'historical_success_rate',  # Past success for similar
]
```

### Training & Adaptation

```python
# Auto-training triggers
- 100+ OpportunityOutcome records → Initial training
- Weekly Sunday 3:30 AM → Scheduled retraining
- Daily 6:30 AM → Accuracy evaluation
- Performance degradation → Auto-retrain
```

### Learning Flow

1. **Score opportunity** → Prediction + SHAP explanation
2. **User interacts** → Outcome recorded
3. **Outcomes accumulate** → Model quality degrades
4. **Auto-retrain** → Model improves
5. **New scoring** → Better predictions

### Hybrid Scoring Formula

```python
final_score = (0.6 * ml_score) + (0.4 * rule_based_score)
```

This ensures:
- ML handles complex patterns
- Rules provide baseline quality
- Explainability via SHAP

---

## Spider Intelligence Learning

### Location
- **Service:** `core/services/spider_intelligence.py`
- **Models:** `SpiderData` in `core/models_unified_system.py`

### What Spiders Learn

Spiders don't "learn" in the traditional sense, but they contribute to system learning:

```
Spider collects data
       ↓
SpiderData stored
       ↓
Embeddings generated (text-embedding-3-small)
       ↓
AgentKnowledgeSource created
       ↓
Agents retrieve for tasks
       ↓
Outcomes feed back to source authority scoring
```

### Source Authority Scoring

```python
SOURCE_AUTHORITY = {
    'reuters_rss': 95,
    'bbc': 90,
    'techcrunch': 90,
    'yahoo_finance': 85,
    'hackernews': 85,
    'producthunt': 80,
    'coingecko': 80,
    'reddit': 75,
    'remoteok': 75,
    # ... etc
}
```

**Authority is adjusted based on:**
- Data quality scores
- Agent usage success rates
- User engagement with spider-sourced content

### Trend Analysis Learning

```python
class SpiderIntelligenceService:
    def get_trending_topics(self, category='tech', hours=24):
        """
        Learns:
        - Which topics trend together
        - Timing patterns (when trends emerge)
        - Category correlations
        """

    def get_market_insights(self):
        """
        Learns:
        - Market sentiment patterns
        - Price correlation factors
        """
```

---

## Data Flow Architecture

### Complete Learning Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     COMPLETE LEARNING DATA FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

USER ACTION
    │
    ▼
┌─────────────────┐
│ Personal        │
│ Assistant       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Agent Router    │────▶│ Selected Agent  │
└─────────────────┘     └────────┬────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                            │                            │
    ▼                            ▼                            ▼
┌─────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Knowledge   │         │ Execute Task    │         │ Sci-Fi Context  │
│ Retrieval   │         │                 │         │ (Memory, Mood)  │
└─────────────┘         └────────┬────────┘         └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ AgentResult     │
                        └────────┬────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                            │                            │
    ▼                            ▼                            ▼
┌─────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Learning    │         │ Memory          │         │ Knowledge       │
│ Outcome     │         │ Creation        │         │ Sharing         │
└──────┬──────┘         └────────┬────────┘         └────────┬────────┘
       │                         │                           │
       ▼                         ▼                           ▼
┌─────────────┐         ┌─────────────────┐         ┌─────────────────┐
│Coordinator  │         │ AgentMemory     │         │AgentKnowledge   │
│Outcome      │         │ (DB)            │         │Source (DB)      │
└──────┬──────┘         └─────────────────┘         └────────┬────────┘
       │                                                     │
       ▼                                                     │
┌─────────────┐                                             │
│ XP Award    │                                             │
│ (Evolution) │                                             │
└──────┬──────┘                                             │
       │                                                     │
       └──────────────────────┬──────────────────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Learning Loop   │
                     │ Analysis        │
                     └────────┬────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Pattern     │      │ Agent Selection │      │ Future Task     │
│ Detection   │      │ Optimization    │      │ Enhancement     │
└─────────────┘      └─────────────────┘      └─────────────────┘
```

---

## Database Models

### Core Learning Models

| Model | Table | Purpose |
|-------|-------|---------|
| `AgentKnowledgeSource` | `core_agentknowledgesource` | Shared agent knowledge |
| `AgentMemory` | `core_agentmemory` | Agent memories |
| `AgentEvolution` | `core_agentevolution` | XP and leveling |
| `AgentDream` | `core_agentdream` | Agent dreams |
| `AgentMood` | `core_agentmood` | Current mood state |
| `CoordinatorOutcome` | `core_coordinatoroutcome` | Execution outcomes |
| `SharedKnowledge` | `core_sharedknowledge` | Cross-agent knowledge |
| `UserAgentLearning` | `intelligence_useragentlearning` | User-specific learning |
| `EngagementMetrics` | `intelligence_engagementmetrics` | A/B testing |
| `OpportunityInteraction` | `intelligence_opportunityinteraction` | User interactions |

### Quick Stats Query

```sql
-- Learning system health check
SELECT
    (SELECT COUNT(*) FROM core_agentknowledgesource) as knowledge_count,
    (SELECT COUNT(*) FROM core_agentmemory) as memory_count,
    (SELECT COUNT(*) FROM core_agentevolution) as evolution_count,
    (SELECT COUNT(*) FROM core_agentdream) as dream_count,
    (SELECT COUNT(*) FROM core_coordinatoroutcome) as outcome_count;
```

---

## Verification Commands

### Check Learning System Health

```bash
# Knowledge sharing
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentKnowledgeSource
print(f'Knowledge records: {AgentKnowledgeSource.objects.count()}')
print(f'Active: {AgentKnowledgeSource.objects.filter(is_active=True).count()}')
print(f'By type:')
for kt in AgentKnowledgeSource.objects.values('knowledge_type').annotate(c=Count('id')).order_by('-c')[:5]:
    print(f'  {kt[\"knowledge_type\"]}: {kt[\"c\"]}')
"

# Memory creation
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentMemory
from django.db.models import Count
print(f'Memories: {AgentMemory.objects.count()}')
for mt in AgentMemory.objects.values('memory_type').annotate(c=Count('id')).order_by('-c'):
    print(f'  {mt[\"memory_type\"]}: {mt[\"c\"]}')
"

# Evolution/XP
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentEvolution
print('Top agents by XP:')
for e in AgentEvolution.objects.order_by('-total_xp')[:10]:
    print(f'  {e.agent.name}: Level {e.current_level} ({e.total_xp} XP)')
"

# Dreams
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentDream
from django.db.models import Count
print(f'Dreams: {AgentDream.objects.count()}')
print(f'Promoted to decisions: {AgentDream.objects.filter(promoted_to_decision=True).count()}')
"

# Learning outcomes
.venv/bin/python manage.py shell -c "
from core.models_unified_system import CoordinatorOutcome
print(f'Outcomes recorded: {CoordinatorOutcome.objects.count()}')
print(f'Successful: {CoordinatorOutcome.objects.filter(outcome=\"success\").count()}')
"
```

### Check Knowledge Retrieval

```bash
# Test semantic search
.venv/bin/python manage.py shell -c "
from core.services.spider_semantic_search import get_spider_semantic_search
search = get_spider_semantic_search()
results = search.semantic_search_with_db_embeddings('AI trends', limit=3)
for r in results:
    print(f'{r.title[:50]}: {r.similarity:.2f}')
"
```

### Check Learning Bridges

```bash
# Verify bridges are registered
.venv/bin/python manage.py shell -c "
from core.learning_bridges import *
print('Learning Bridges:')
print('  - RevenueAttributionBridge')
print('  - AgentExecutionBridge')
print('  - ApplicationOutcomeBridge')
print('  - SpiderDataBridge')
print('  - AdvisorFeedbackBridge')
print('  - PersonalizationBridge')
print('  - CollaborationBridge')
print('  - SportsBettingBridge')
"
```

---

## Troubleshooting

### Common Issues

#### 1. Knowledge Not Being Retrieved

**Symptoms:** Agents not using learned knowledge

**Check:**
```bash
# Verify knowledge exists
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentKnowledgeSource
print(AgentKnowledgeSource.objects.filter(is_active=True).count())
"

# Check if agent calls retrieval
grep -n "_get_relevant_knowledge" core/agents/*.py
```

**Fix:** Ensure agent's `execute()` calls `_get_relevant_knowledge_for_task()`

#### 2. XP Not Being Awarded

**Symptoms:** Agents stuck at Level 1

**Check:**
```bash
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentEvolution
stuck = AgentEvolution.objects.filter(current_level=1, total_xp=0)
print(f'Agents with 0 XP: {stuck.count()}')
"
```

**Fix:** Ensure `_record_learning_outcome()` is called after execution

#### 3. Embeddings Not Generated

**Symptoms:** Semantic search returns empty

**Check:**
```bash
.venv/bin/python manage.py shell -c "
from core.models_unified_system import SpiderData
with_embed = SpiderData.objects.exclude(embedding__isnull=True).count()
total = SpiderData.objects.count()
print(f'With embeddings: {with_embed}/{total} ({100*with_embed/total:.1f}%)')
"
```

**Fix:** Run `backfill_spider_embeddings` Celery task

#### 4. Learning Bridges Not Firing

**Symptoms:** Events occur but learning not updated

**Check:** Verify Django signals are connected

**Fix:** Ensure `core.learning_bridges` is in `INSTALLED_APPS`

---

## Summary

The Unified Donkey Betz platform has a comprehensive learning system with:

- **72 agents** with built-in learning hooks
- **8 learning bridges** for automatic learning connections
- **Sci-Fi features** (Evolution, Dreams, Memory, Mood) for agent enrichment
- **19 autonomous situations** with outcome tracking
- **ML Scoring Engine** with auto-retraining
- **Pilot/Experiment system** for governance learning

The key to maximizing learning:
1. Ensure agents call learning hooks in `execute()`
2. Run Celery Beat for scheduled learning tasks
3. Track outcomes for all executions
4. Let the system run - learning improves over time

**Reality Score Target:** 95%+ with all learning systems active
