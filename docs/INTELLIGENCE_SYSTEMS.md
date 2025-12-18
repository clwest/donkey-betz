# Intelligence Systems - RAG, Learning & Anti-Hallucination

**Last Updated:** December 17, 2025 (Session 484)
**Status:** Production-Ready

---

## Overview

The platform implements a sophisticated **Intelligence Stack** consisting of three interconnected systems:

1. **RAG (Retrieval-Augmented Generation)** - Context retrieval from spider data and research
2. **Learning System** - Collective intelligence and knowledge transfer between agents
3. **Mythology (Anti-Hallucination)** - Detection and correction of unrealistic claims

---

## 1. RAG System (Retrieval-Augmented Generation)

### Architecture

```
Query Input
    │
    ▼
┌────────────────────────┐
│ Unified Intelligence   │
│ Search Service         │
│ (Session 303)          │
└──────────┬─────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐  ┌─────────────┐
│ Spider  │  │ Business    │
│ Data    │  │ Research    │
│ Search  │  │ Results     │
└────┬────┘  └─────┬───────┘
     │             │
     └──────┬──────┘
            ▼
    ┌──────────────────┐
    │ Combined Results │
    │ with Attribution │
    └──────────────────┘
```

### Semantic Search Implementation

**File:** `core/services/spider_semantic_search.py`

```python
# Uses OpenAI text-embedding-3-small for embeddings
@dataclass
class SemanticSearchResult:
    title: str
    description: str  # NOT 'content'!
    url: str
    source: str
    similarity: float
    category: str
    found_at: str
    tags: List[str] = None
```

**Key Methods:**
- `semantic_search_with_db_embeddings()` - Fast search using pre-computed embeddings
- `get_embedding_stats()` - Check embedding coverage
- `backfill_embeddings()` - Background embedding generation

**Performance Optimization (Session 468):**
- Uses pre-computed embeddings only (no on-the-fly generation)
- Retrieval time: <1 second (was 10+ minutes with fallback)
- Embedding coverage tracked: `with_embedding`, `marked_empty`, `pending`

### Unified Intelligence Search

**File:** `core/services/unified_intelligence_search.py`

Combines two data sources:
1. **SpiderData** - Real-time web crawls (67 spiders, 31+ sources)
2. **BusinessResearchResult** - AI-generated business analysis

```python
from core.services.unified_intelligence_search import get_unified_intelligence_search

search = get_unified_intelligence_search()

# Search both spider data AND business research
results = search.unified_search("AI content generation")

# Get formatted context for prompt injection
context = search.get_research_context("AI tools")

# Trigger fresh spider crawls before analysis
search.refresh_spiders_for_query("market analysis")
```

### Knowledge Attribution

**File:** `core/agents/base_agent.py`

Every agent response tracks which sources informed the output:

```python
@dataclass
class KnowledgeAttribution:
    spider_sources: List[str]      # Which spiders contributed
    knowledge_items: List[Dict]    # Top 3 knowledge items used
    confidence_score: float        # Average confidence (0-1)
    data_freshness_hours: int      # How old is the data
    total_sources: int             # Count of unique sources
```

### Agent Knowledge Pipeline (Session 400)

**File:** `core/agents/base_agent.py` lines 300-400

Agents automatically retrieve and use learned knowledge:

```python
class BaseAgent:
    def _get_relevant_knowledge_for_task(self, task: str, limit: int = 5):
        """Hybrid retrieval: semantic + keyword matching"""
        # 1. Try semantic search on pre-computed spider embeddings
        # 2. Fallback to keyword matching on AgentKnowledgeSource
        pass

    def _get_fresh_spider_intelligence(self, categories, hours, limit):
        """Get fresh spider data for agent's domain"""
        pass

    def _build_prompt_with_attribution(self, task, context):
        """Build prompt and return KnowledgeAttribution"""
        pass
```

---

## 2. Learning System

### Overview

The Learning System enables agents to:
- Learn from their own successes and failures
- Share knowledge with other agents
- Improve over time through experience
- Build collective intelligence

### Agent Learning Service

**File:** `core/services/agent_learning_service.py`

```python
# Interaction Types
class InteractionType(Enum):
    CREATED = "created"
    EDITED = "edited"
    SAVED = "saved"
    SHARED = "shared"
    DOWNLOADED = "downloaded"
    RATED = "rated"
    USED = "used"
    REJECTED = "rejected"
    FAVORITED = "favorited"

# Preference Categories
class PreferenceCategory(Enum):
    STYLE = "style"
    THEME = "theme"
    MODEL = "model"
    QUALITY = "quality"
    FORMAT = "format"
    COLOR = "color"
    MOOD = "mood"
    COMPLEXITY = "complexity"
```

**Key Methods:**
- `record_interaction()` - Log user action with agent output
- `_extract_preference_signals()` - Infer preferences from behavior
- `_update_preference()` - Update confidence scores
- `get_adaptive_context()` - Get learned context for prompts
- `apply_preferences_to_params()` - Auto-fill from preferences

### Collective Intelligence Service

**File:** `core/services/collective_intelligence.py` (1,800+ lines)

Aggregates knowledge across all agents:

```python
from core.services.collective_intelligence import get_collective_intelligence

service = get_collective_intelligence()

# Combine insights from multiple agents
insights = service.aggregate_insights(
    topic="AI content generation",
    domains=["creative", "research", "strategy"]
)

# Generate multi-perspective report
report = service.generate_collective_report(topic)

# Find gaps in collective knowledge
gaps = service.identify_knowledge_gaps()
```

### Knowledge Transfer Models

**File:** `core/models_unified_system.py`

```python
# What agents have learned
class AgentKnowledgeSource(models.Model):
    agent = ForeignKey(Agent)
    knowledge_type = CharField  # trend, market, opportunity, etc.
    source_spider_names = JSONField
    title = CharField
    summary = TextField
    confidence_score = FloatField  # 0.0-1.0
    freshness_score = FloatField   # 0.0-1.0
    is_validated = BooleanField

# Teacher-student relationships
class AgentLearningConnection(models.Model):
    teacher_agent = ForeignKey(Agent)
    student_agent = ForeignKey(Agent)
    learning_type = CharField  # complementary, specialization, pipeline
    shareable_knowledge_types = JSONField
    total_transfers = IntegerField
    successful_transfers = IntegerField
    avg_improvement_score = FloatField

# Individual knowledge transfers
class KnowledgeTransfer(models.Model):
    connection = ForeignKey(AgentLearningConnection)
    source_knowledge = ForeignKey(AgentKnowledgeSource)
    transfer_summary = TextField
    was_useful = BooleanField
    usefulness_score = FloatField
    was_applied = BooleanField
    application_result = TextField
```

### Learning Loop Integration

**File:** `core/super_platform/learning_loop.py`

Every agent execution is recorded for learning:

```python
class BaseAgent:
    def execute(self, task, context):
        # 1. Get learning context
        learned_context = self._learning_loop.get_context_for_agent(self)

        # 2. Execute task
        result = self._execute_with_context(task, context, learned_context)

        # 3. Record outcome for learning
        self._learning_loop.record_outcome(
            agent=self,
            task=task,
            success=result.success,
            quality_score=result.quality
        )

        return result
```

---

## 3. Mythology System (Anti-Hallucination)

### Overview

The Mythology system prevents agents from making unrealistic claims by:
1. Detecting patterns of common hallucinations
2. Auto-correcting exaggerated claims
3. Logging violations for improvement

### Mythology Validator

**File:** `ai_core/agents/mythology_validator.py`

```python
class MythologyValidator:
    """Prevents AI agents from making unrealistic promises."""

    # 5 categories of unrealistic claims
    VALIDATION_CATEGORIES = {
        'FINANCIAL_MYTHS': [
            r'\$\d+[k]?/day',           # "$500/day" claims
            r'guaranteed\s+income',      # "guaranteed income"
            r'risk-free',                # "risk-free"
            r'\d+x\s+your\s+money',      # "10x your money"
            r'passive\s+income',         # "passive income"
        ],
        'TECHNICAL_MYTHS': [
            r'100%\s+accurate',          # "100% accurate"
            r'never\s+fail',             # "never fail"
            r'instant\s+deployment',     # "instant deployment"
            r'no\s+bugs',                # "no bugs"
            r'unlimited\s+scaling',      # "unlimited scaling"
        ],
        'TIME_MYTHS': [
            r'build\s+in\s+seconds',     # "build in seconds"
            r'learn.*in\s+hours',        # "learn in hours"
            r'immediate\s+results',      # "immediate results"
        ],
        'DANGEROUS_MYTHS': [
            r'cure.*disease',            # Medical claims
            r'legal\s+advice',           # Unlicensed advice
            r'guaranteed\s+approval',    # False promises
        ],
        'SPIDER_DATA_MYTHS': [
            r'99%\s+market\s+share',     # Exaggerated stats
            r'every\s+business\s+uses',  # Universal claims
            r'millions\s+in\s+weeks',    # Unrealistic growth
            r'no\s+competition',         # False uniqueness
            r'viral\s+guaranteed',       # False virality
        ]
    }
```

### Validation Flow

```python
def validate_output(self, agent_name: str, output: str) -> Dict:
    """
    Validate agent output for unrealistic claims.

    Returns:
        {
            'valid': bool,
            'violations': List[str],
            'corrected_output': Optional[str]
        }
    """
    violations = []

    for category, patterns in self.VALIDATION_CATEGORIES.items():
        for pattern in patterns:
            if re.search(pattern, output, re.IGNORECASE):
                violations.append(f"{category}: {pattern}")

    return {
        'valid': len(violations) == 0,
        'violations': violations,
        'corrected_output': self.correct_output(output) if violations else None
    }
```

### Auto-Correction

```python
def correct_output(self, output: str) -> str:
    """Auto-correct unrealistic claims."""
    corrections = {
        r'\$\d+[k]?/day': 'potential earnings vary',
        r'guaranteed': 'potential',
        r'100%': 'highly reliable',
        r'unlimited': 'scalable',
        r'cure.*disease': 'may help with symptoms',
        r'never fail': 'highly reliable',
    }

    result = output
    for pattern, replacement in corrections.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result
```

### Integration Points

**BaseAgent Integration:**
```python
class BaseAgent:
    @property
    def mythology_enforcer(self):
        from ai_core.agents.mythology_validator import mythology_enforcer
        return mythology_enforcer

    def _validate_output(self, output: str) -> str:
        result = self.mythology_enforcer.validate_output(self.name, output)
        if not result['valid']:
            logger.warning(f"Mythology violation: {result['violations']}")
            return result['corrected_output']
        return output
```

**Legal Assistant Integration (Session 409):**
```python
# LegalDocDrafterAgent lines 1183, 2764
# Extra validation for legal documents to prevent hallucinated legal claims
def _validate_legal_output(self, output: str) -> str:
    # Additional patterns for legal context
    legal_patterns = [
        r'guaranteed\s+win',
        r'judge\s+will\s+definitely',
        r'opposing\s+counsel\s+always',
    ]
    # ... validation logic
```

### Statistics Tracking

```python
class MythologyEnforcer:
    validation_stats = {
        'total_checks': 0,
        'violations_found': 0,
        'corrections_made': 0,
    }

    violation_log = []  # Recent violations with timestamps
```

---

## Data Models Summary

### RAG Models

| Model | Purpose |
|-------|---------|
| SpiderData | Raw crawled data with embeddings |
| BusinessResearchResult | AI-generated research with embeddings |
| AgentKnowledgeSource | Agent-specific learned knowledge |

### Learning Models

| Model | Purpose |
|-------|---------|
| AgentLearningConnection | Teacher-student relationships |
| KnowledgeTransfer | Individual transfer records |
| SharedKnowledge | Cross-agent knowledge |
| AgentLearning | Learning outcome tracking |
| AgentInteraction | User interaction records |
| LearnedPreference | Inferred user preferences |

---

## Key Sessions

| Session | Feature |
|---------|---------|
| 293 | Spider Semantic Search Service |
| 303 | Unified Intelligence Search (spider + research) |
| 354 | Mythology validation integration |
| 394 | Spider embedding backfill optimization |
| 400 | Agent Knowledge Pipeline complete |
| 409 | Legal mythology validation |
| 468 | Embedding performance fix (<1s) |
| 483 | Spider data pipeline bug fixes |

---

## Testing Commands

```bash
# Test semantic search
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.spider_semantic_search import get_spider_semantic_search
search = get_spider_semantic_search()
results = search.semantic_search_with_db_embeddings('AI tools', limit=5)
for r in results:
    print(f'[{r.source}] {r.title[:50]}')"

# Check embedding coverage
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.spider_semantic_search import get_spider_semantic_search
stats = get_spider_semantic_search().get_embedding_stats()
print(f'Coverage: {stats[\"coverage_percent\"]}%')"

# Test knowledge pipeline
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.agents import ImageAgent
agent = ImageAgent()
results = agent._get_relevant_knowledge_for_task('AI trends')
print(f'Found {len(results)} items')"
```

---

## Configuration

### Embedding Settings
- **Model:** `text-embedding-3-small`
- **Dimension:** 768
- **Cache TTL:** 6 hours (21,600 seconds)
- **Batch Size:** 100 entries per cycle
- **Backfill Schedule:** Every 10 minutes (Celery Beat)

### Mythology Settings
- **Validation:** Enabled by default on all agents
- **Auto-correct:** Enabled
- **Logging:** All violations logged
- **Legal Extra Validation:** Enabled for LegalDocDrafterAgent

---

## Troubleshooting

### Low Embedding Coverage
```bash
# Manually trigger backfill
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.spider_semantic_search import get_spider_semantic_search
stats = get_spider_semantic_search().backfill_embeddings(batch_size=200, hours=168)
print(f'Processed: {stats[\"processed\"]}, Succeeded: {stats[\"succeeded\"]}')"
```

### Slow Retrieval
- Check embedding coverage (should be >80%)
- Verify Redis cache is running
- Check PostgreSQL query performance

### Mythology False Positives
- Review violation log for patterns
- Add exceptions for domain-specific terminology
- Adjust pattern regexes as needed
