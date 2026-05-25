# Session 400: Agent Knowledge Pipeline - Spider Data → Embeddings → Agent Learning → Knowledge Usage

**Date:** December 8, 2025

---

## Summary

This session completed the full knowledge pipeline for agents:

1. **Fixed Spider Data Bridge** - Was listening to empty model, now uses correct SpiderData
2. **Verified Embedding Pipeline** - 6,500+ records, 2,100+ embedded
3. **Implemented Knowledge Injection** - Agents now USE their learned knowledge in prompts

---

## Problem Statement

The agent learning system had all the infrastructure in place but wasn't fully connected:

| Component | Before | After |
|-----------|--------|-------|
| Spider data storage | ✅ Working (6,500+ records) | ✅ Working |
| Embedding generation | ✅ Working (33% embedded) | ✅ Working |
| Learning bridge | ❌ Wrong model (0 records) | ✅ Fixed |
| Knowledge creation | ✅ Working (878 knowledge sources) | ✅ Working |
| **Knowledge USAGE** | ❌ Never retrieved | ✅ **Now injected into prompts** |

---

## Changes Made

### 1. Fixed Spider Data Learning Bridge

**File:** `core/learning_bridges/spider_data_bridge.py`

The bridge was listening to `persistence.models.SpiderData` (0 records) instead of `core.models_unified_system.SpiderData` (6,500+ records).

**Changes:**
- Updated import to use correct SpiderData model
- Updated agent lookup to use `Agent` model instead of `UnifiedAgentTemplate`
- Added `_get_target_agents_for_data()` to route spider data to relevant agents by category
- Adapted all field access for core SpiderData model (no `routed_to_agents`, `quality_score`, etc.)

**Category → Agent Mapping:**
```python
category_to_agents = {
    'tech': ['ResearchAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent', 'CTOAgent'],
    'news': ['ResearchAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent'],
    'jobs': ['OpportunityScoringAgent', 'ResearchAgent'],
    'design': ['CreativeDirectorAgent', 'BrandIdentityAgent', 'ContentStrategyAgent'],
    'financial': ['OpportunityScoringAgent', 'TrendAnalysisAgent', 'CTOAgent'],
    # ... etc
}
```

### 2. Added Knowledge Retrieval to BaseAgent

**File:** `core/agents/base_agent.py`

Added two new methods:

#### `_get_relevant_knowledge_for_task(task, limit=5)`

Retrieves learned knowledge relevant to the current task using a hybrid approach:
1. **Semantic search** on SpiderData embeddings
2. **Keyword matching** on AgentKnowledgeSource

Returns list of knowledge items with source, title, summary, confidence.

#### `_get_fresh_spider_intelligence(categories, hours=24, limit=5)`

Gets real-time spider data for specific categories:
- Queries recent SpiderData with embeddings
- Extracts sample titles from items
- Returns structured intelligence for prompt injection

### 3. Updated `_build_prompt()` for Knowledge Injection

The `_build_prompt()` method now automatically:
1. Calls `_get_relevant_knowledge_for_task(task)`
2. Injects relevant knowledge into the prompt before the task
3. Formats knowledge with source attribution

**Example prompt section:**
```
## Relevant Knowledge from Past Learning
You have learned the following that may be relevant:

1. [ResearchAgent] Research: AI trends in 2025
   Analysis shows growth in LLM applications...
   (from: techcrunch, hackernews)

2. [ContentStrategyAgent] Content strategy for AI tools
   Key topics include automation, RAG systems...
```

---

## Data Flow (Complete Pipeline)

```
Spider Network (102 spiders)
        ↓
    Celery Beat (every 30 min)
        ↓
core.models_unified_system.SpiderData (6,500+ records)
        ↓
    Embedding Service
        ↓
SpiderData.embedding (2,100+ embedded)
        ↓
spider_data_bridge.py (post_save signal)
        ↓
AgentKnowledgeSource (878 knowledge items)
        ↓
                          ┌────────────────────────────────────┐
                          │     AGENT EXECUTION                │
                          │                                    │
                          │  1. _get_relevant_knowledge_for_task()
                          │     - Semantic search on embeddings
                          │     - Keyword match on knowledge   │
                          │                                    │
                          │  2. _build_prompt() injects:       │
                          │     - Relevant learned knowledge   │
                          │     - Sci-fi context (mood, etc)   │
                          │     - Spider context (trends)      │
                          │     - The actual task              │
                          │                                    │
                          │  3. GPT receives enriched prompt   │
                          │     with accumulated knowledge     │
                          └────────────────────────────────────┘
```

---

## Verification Commands

```bash
# Test knowledge retrieval
.venv/bin/python manage.py shell -c "
from core.agents.research_agent import ResearchAgent
agent = ResearchAgent()
knowledge = agent._get_relevant_knowledge_for_task('AI trends')
print(f'Found {len(knowledge)} relevant items')
for k in knowledge:
    print(f'  [{k[\"source_agent\"]}] {k[\"title\"][:50]}')
"

# Test fresh spider intelligence
.venv/bin/python manage.py shell -c "
from core.agents.research_agent import ResearchAgent
agent = ResearchAgent()
intel = agent._get_fresh_spider_intelligence(categories=['tech', 'news'], limit=3)
print(f'Found {len(intel)} fresh items')
"

# Test prompt building with knowledge
.venv/bin/python manage.py shell -c "
from core.agents.research_agent import ResearchAgent
agent = ResearchAgent()
prompt = agent._build_prompt('Find AI opportunities', {}, {})
print('Knowledge injected:', '## Relevant Knowledge' in prompt)
"

# Check learning bridge is working
.venv/bin/python manage.py shell -c "
from core.models_unified_system import UserAgentLearning
print(f'Learning entries: {UserAgentLearning.objects.count()}')
"
```

---

## Related Files

- `core/agents/base_agent.py` - Knowledge retrieval + prompt injection
- `core/learning_bridges/spider_data_bridge.py` - Fixed to use correct models
- `core/services/spider_semantic_search.py` - Semantic search on embeddings
- `core/models_unified_system.py` - SpiderData, AgentKnowledgeSource models

---

## Next Steps (Future Sessions)

1. **Improve knowledge quality** - Filter out low-confidence or stale knowledge
2. **Add knowledge decay** - Old knowledge should have less influence
3. **Cross-agent learning** - Agents actively query other agents' expertise
4. **Feedback loop** - Track which knowledge actually helped task completion
5. **Knowledge summarization** - Compress verbose knowledge into key insights

---

## Session Accomplishments

1. ✅ Fixed spider_data_bridge.py to use correct SpiderData model
2. ✅ Added `_get_relevant_knowledge_for_task()` to BaseAgent
3. ✅ Added `_get_fresh_spider_intelligence()` to BaseAgent
4. ✅ Updated `_build_prompt()` to automatically inject relevant knowledge
5. ✅ Tested full pipeline from spider data → agent prompts
6. ✅ Agents now USE their accumulated knowledge when executing tasks
