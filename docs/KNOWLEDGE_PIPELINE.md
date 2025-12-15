# Knowledge Pipeline

**Built:** Sessions 243-245 (learning), Session 400 (pipeline complete)
**Status:** Fully operational - agents USE their accumulated knowledge

---

## Overview

The Knowledge Pipeline transforms raw spider data into actionable intelligence that agents use during execution. This creates a self-improving system where:

1. Spiders collect real-time data
2. Data is embedded for semantic search
3. Learning bridges create knowledge entries
4. Agents query relevant knowledge
5. Knowledge is injected into prompts
6. Outcomes feed back into the system

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPIDER NETWORK (64 spiders)                  │
│  Tech(9) | Financial(8) | Jobs(7) | Creative(5) | Legal(6)...   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Celery Beat (every 30 min)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SPIDER DATA (8,424 records)                  │
│  title | description | url | category | spider_name | fetched_at│
└───────────────────────────┬─────────────────────────────────────┘
                            │ Embedding Service
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  EMBEDDED SPIDER DATA (3,313)                   │
│  ...same fields + embedding (1536-dim vector from OpenAI)       │
└───────────────────────────┬─────────────────────────────────────┘
                            │ spider_data_bridge (post_save signal)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT KNOWLEDGE SOURCE (953 entries)               │
│  agent | knowledge_type | title | knowledge_value | embedding   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ BaseAgent._get_relevant_knowledge_for_task()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT EXECUTION                             │
│  Knowledge + Spider Context + Task -> GPT-5-mini -> Result      │
└───────────────────────────┬─────────────────────────────────────┘
                            │ _record_learning_outcome()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING BRIDGES (8)                         │
│  Agent Execution | Revenue | Advisor | Collaboration | Spider...│
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Details

### Stage 1: Spider Collection

**Trigger:** Celery Beat schedule (every 30 minutes)
**Task:** `core.tasks.run_spider_network`

```python
# core/celery.py
CELERY_BEAT_SCHEDULE = {
    'run-spider-network': {
        'task': 'core.tasks.run_spider_network',
        'schedule': crontab(minute='*/30'),
    },
}
```

**Output:** New `SpiderData` records

```python
SpiderData.objects.create(
    spider_name='techcrunch_spider',
    category='tech',
    title='OpenAI Releases GPT-5',
    description='The latest model shows...',
    url='https://techcrunch.com/...',
    fetched_at=timezone.now()
)
```

### Stage 2: Embedding Generation

**Location:** `core/services/spider_semantic_search.py`
**Model:** `text-embedding-3-small` (OpenAI)
**Dimensions:** 1536

```python
from core.services.spider_semantic_search import get_spider_semantic_search

search = get_spider_semantic_search()

# Generate embedding for new entry
embedding = search._generate_embedding(f"{title} {description}")

# Store in SpiderData.embedding field
spider_data.embedding = embedding
spider_data.save()
```

**Backfill Command:**
```bash
.venv/bin/python manage.py shell -c "
from core.services.spider_semantic_search import get_spider_semantic_search
search = get_spider_semantic_search()
stats = search.backfill_embeddings(batch_size=100)
print(stats)
"
```

### Stage 3: Learning Bridge

**Location:** `core/services/spider_data_bridge.py`
**Signal:** `post_save` on `SpiderData`

```python
@receiver(post_save, sender=SpiderData)
def spider_data_to_knowledge(sender, instance, created, **kwargs):
    if created:
        # Find relevant agent based on category
        agent = get_agent_for_category(instance.category)

        # Create knowledge entry
        AgentKnowledgeSource.objects.create(
            agent=agent,
            knowledge_type='spider_intelligence',
            title=instance.title,
            knowledge_value={
                'description': instance.description,
                'url': instance.url,
                'source': instance.spider_name,
                'category': instance.category
            },
            spider_sources=[instance.spider_name]
        )
```

### Stage 4: Knowledge Retrieval

**Location:** `core/agents/base_agent.py`

```python
def _get_relevant_knowledge_for_task(self, task: str, limit: int = 5) -> list:
    """
    Semantic search on learned knowledge.

    Returns: [{
        'source_agent': 'ResearchAgent',
        'title': 'AI Trends 2025',
        'summary': 'Growth in LLM applications...',
        'knowledge_type': 'spider_intelligence',
        'confidence': 0.85,
        'spider_sources': ['techcrunch', 'hackernews']
    }]
    """
    # Get task embedding
    task_embedding = self._generate_embedding(task)

    # Query AgentKnowledgeSource with cosine similarity
    knowledge = AgentKnowledgeSource.objects.annotate(
        similarity=CosineDistance('embedding', task_embedding)
    ).filter(
        similarity__gt=0.5  # Relevance threshold
    ).order_by('-similarity')[:limit]

    return self._format_knowledge(knowledge)
```

### Stage 5: Prompt Injection

**Location:** `core/agents/base_agent.py`

```python
def _build_prompt(self, task: str) -> str:
    """Build prompt with injected knowledge and context."""

    # Get relevant knowledge
    knowledge = self._get_relevant_knowledge_for_task(task)

    # Get fresh spider intelligence
    spider_intel = self._get_fresh_spider_intelligence(
        categories=self.relevant_categories,
        hours=24
    )

    prompt = f"""
{self.system_prompt}

## Relevant Knowledge from Past Learning
{self._format_knowledge_section(knowledge)}

## Recent Spider Intelligence
{self._format_spider_section(spider_intel)}

## Current Task
{task}
"""
    return prompt
```

**Example Injected Section:**
```
## Relevant Knowledge from Past Learning
You have learned the following that may be relevant:

1. [ResearchAgent] Research: AI trends in 2025
   Analysis shows growth in LLM applications, with focus on...
   (from: techcrunch, hackernews)

2. [TrendAnalysisAgent] Market: Content creation tools
   Growing demand for AI-powered content tools in small...
   (from: reddit, producthunt)
```

### Stage 6: Learning Outcome Recording

**Location:** `core/agents/base_agent.py`

```python
def _record_learning_outcome(self, result, task: str, context: dict):
    """Record execution outcome for future learning."""

    # Create execution memory
    self._create_execution_memory(
        result=result,
        task=task,
        memory_type='success' if result.success else 'failure'
    )

    # Share knowledge if valuable
    if result.success and self._is_valuable_outcome(result):
        self._share_knowledge(
            knowledge_type='execution_insight',
            title=f"Successful {self.name} execution",
            knowledge_value={
                'task': task,
                'outcome': result.summary,
                'techniques': result.techniques_used
            }
        )

    # Update XP/evolution
    self._update_evolution(result)
```

---

## Learning Bridges (8 Types)

**Location:** `core/apps.py`

### 1. Agent Execution Bridge
Captures successful agent outputs.
```python
@receiver(post_save, sender=AgentExecution)
def execution_to_knowledge(sender, instance, **kwargs):
    if instance.success:
        # Create knowledge from successful execution
```

### 2. Application Outcome Bridge
Tracks real-world results (e.g., user adopted suggestion).

### 3. Revenue Attribution Bridge
Connects actions to actual revenue.

### 4. Advisor Feedback Bridge
Incorporates expert guidance from advisor agents.

### 5. Collaboration Bridge
Records multi-agent work outcomes.

### 6. Personalization Bridge
Learns user preferences over time.

### 7. Sports Betting Bridge
Learns from betting outcomes.

### 8. Spider Data Bridge
Converts spider data to agent knowledge.

---

## Services

### SpiderIntelligenceService

**Location:** `core/services/spider_intelligence.py`

```python
from core.services.spider_intelligence import SpiderIntelligenceService

service = SpiderIntelligenceService()

# Get trending topics
trending = service.get_trending_topics(hours=24, limit=10)

# Get tech trends with filter
tech = service.get_tech_trends(hours=72, topic_filter='ai')
# topic_filter: 'ai', 'web', 'security', 'cloud', 'design'

# Search spider data
results = service.search_spider_data(query="machine learning")
```

### SpiderSemanticSearch

**Location:** `core/services/spider_semantic_search.py`

```python
from core.services.spider_semantic_search import get_spider_semantic_search

search = get_spider_semantic_search()

# Semantic search with DB embeddings
results = search.semantic_search_with_db_embeddings(
    query="AI writing tools",
    limit=10
)

# Get embedding stats
stats = search.get_embedding_stats()
# {total_entries: 8424, with_embedding: 3313, coverage_percent: 39.3}
```

### UnifiedIntelligenceSearch

**Location:** `core/services/unified_intelligence_search.py`

```python
from core.services.unified_intelligence_search import get_unified_intelligence_search

search = get_unified_intelligence_search()

# Search BOTH spider data AND business research
results = search.unified_search("AI content generation")

# Get context for prompt injection
context = search.get_research_context("AI tools")

# Trigger fresh spider crawls
search.refresh_spiders_for_query("market analysis")
```

---

## Database Models

### SpiderData

```python
class SpiderData(models.Model):
    spider_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    title = models.TextField()
    description = models.TextField()
    url = models.URLField(max_length=2000)
    embedding = models.JSONField(null=True, blank=True)  # 1536-dim vector
    fetched_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### AgentKnowledgeSource

```python
class AgentKnowledgeSource(models.Model):
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE)
    knowledge_type = models.CharField(max_length=50)
    # Types: spider_intelligence, execution_insight, user_feedback, ...
    title = models.CharField(max_length=255)
    knowledge_value = models.JSONField()
    embedding = models.JSONField(null=True, blank=True)
    spider_sources = models.JSONField(default=list)
    confidence = models.FloatField(default=0.5)
    created_at = models.DateTimeField(auto_now_add=True)
```

### BusinessResearchResult

```python
class BusinessResearchResult(models.Model):
    project = models.ForeignKey('PartnershipProject', null=True)
    research_type = models.CharField(max_length=50)
    # Types: competitor_analysis, customer_research, market_analysis
    query = models.TextField()
    result = models.JSONField()
    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Statistics

**Current Counts (December 2025):**

| Model | Count | With Embedding |
|-------|-------|----------------|
| SpiderData | 8,424 | 3,313 (39%) |
| AgentKnowledgeSource | 953 | ~800 |
| BusinessResearchResult | ~50 | ~50 |
| AgentMemory | 1,000+ | ~900 |

---

## Verification Commands

### Check Pipeline Health

```bash
# Count spider data
.venv/bin/python manage.py shell -c "
from core.models_unified_system import SpiderData
print(f'Spider Data: {SpiderData.objects.count()}')
print(f'With embeddings: {SpiderData.objects.exclude(embedding__isnull=True).count()}')
"

# Count knowledge
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentKnowledgeSource
print(f'Knowledge: {AgentKnowledgeSource.objects.count()}')
"

# Test knowledge retrieval
.venv/bin/python manage.py shell -c "
from core.agents.research_agent import ResearchAgent
agent = ResearchAgent()
knowledge = agent._get_relevant_knowledge_for_task('AI trends')
print(f'Found {len(knowledge)} relevant knowledge items')
"
```

### Backfill Embeddings

```bash
# Backfill spider data embeddings
.venv/bin/python manage.py shell -c "
from core.services.spider_semantic_search import get_spider_semantic_search
search = get_spider_semantic_search()
stats = search.backfill_embeddings(batch_size=100)
print(stats)
"
```

---

## Session History

| Session | Focus | Key Changes |
|---------|-------|-------------|
| 243-245 | Agent Learning | Initial learning system |
| 293 | Semantic Search | Spider semantic search service |
| 303 | Unified Intelligence | Combined spider + research search |
| 380 | Learning Hooks | Added hooks to all agents |
| 381 | Architecture Doc | Documented collective intelligence |
| 400 | Pipeline Complete | Fixed spider_data_bridge, knowledge injection |

---

## Related Documentation

- [SPIDERS.md](SPIDERS.md) - Spider network details
- [AGENTS.md](AGENTS.md) - Agent knowledge methods
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - Memory Palace, Evolution
- [docs/handoffs/SESSION_400_AGENT_KNOWLEDGE_PIPELINE.md](handoffs/SESSION_400_AGENT_KNOWLEDGE_PIPELINE.md)
