# Session 794 - Deep Dive: Agents, Learning, Teaching, Doing

**Previous Session:** 793 (Neural Orchestra & Consciousness Fixes)
**Date:** January 23, 2026
**Status:** 74 Core + 139 Persona Agents | 45 Frontend Pages | ALL BODY SYSTEMS GREEN

---

## SESSION 794 FOCUS: Agent Learning & Execution Pipeline

The Neural Orchestra is now displaying real data. This session will deep dive into understanding and optimizing:

1. **Agent Execution** - What triggers agents? Why are most dormant?
2. **Agent Learning** - How do agents learn from success/failure?
3. **Knowledge Transfer** - How does knowledge flow between agents?
4. **Content Creation** - End-to-end image/video generation testing
5. **Agent Teaching** - How do successful agents teach others?

---

## RAILWAY DEPLOYMENT ACTIVE

**Production URL:** `https://donkey-betz-platform-production.up.railway.app/`

### Current Architecture
```
Railway Project: donkey-betz-platform
├── PostgreSQL (pgvector enabled)
├── Redis
├── Web Service (Daphne ASGI)
└── Celery Worker + Beat (261 scheduled tasks)
```

### Body System Health Status (All Green!)
| System | Status | Score |
|--------|--------|-------|
| HEART | Healthy | 100% |
| LUNGS | Normal | 100% |
| CIRCULATORY | Flowing | 100% |
| DIGESTIVE | Healthy | 91% |
| MUSCULAR | Fit | 78% |
| SPINE | Aligned | 100% |
| BRAIN | Focused | 100% |
| IMMUNE | Vigilant | 100% |
| SKIN | Healthy | 100% |

---

## Session 793 Summary

Fixed 6 major issues with Neural Orchestra and Consciousness:

| Issue | Before | After |
|-------|--------|-------|
| Collaborations | 0 | 195 |
| Orchestrations | 0 | 195 |
| Memory Crystals | 0 | 167,822 |
| Tracking Rate | 9400% | N/A (no content) |
| Live Feed Items | 1 | 20 |
| Learning Feed | 0 | 15 |
| Consciousness Level | 5.5% | ~60-70% |

**Key Fixes:**
- Added fallback logic for empty primary models
- Combined AgentContribution + AgentExecution for Live Feed
- Fixed Learning Tab field name bugs
- Persisted awakening_time in Redis
- Added DB fallbacks for consciousness calculation
- Fixed ImageAgent/VideoAgent unnecessary delegation

---

## Key Questions for Session 794

### Agent Execution
- Why have only ~10 unique agents executed in the last 24 hours?
- What triggers an agent to execute?
- How does the agent router decide which agent handles a task?
- Are Celery tasks properly triggering agent execution?

### Agent Learning
- With 167,822 AgentLearning records, what are agents learning?
- How does `_record_learning_outcome()` work in BaseAgent?
- What determines if a learning is "approved" vs "exploratory"?
- How does `learning_pattern_engine.py` mine patterns?

### Knowledge Transfer
- With 195 KnowledgeTransfer records, how is knowledge shared?
- What is the relationship between AgentLearning and KnowledgeTransfer?
- How does an agent "teach" another agent?
- What triggers a knowledge transfer event?

### Content Creation
- Why does AgentContribution only have 1 record?
- How do we track when ImageAgent creates an image?
- What's the full flow from task → agent → content → tracking?

---

## Models to Investigate

```python
# Query these on Railway to understand data state
from core.models_unified_system import (
    Agent,           # 74 agents
    AgentExecution,  # 132 executions
    AgentLearning,   # 167,822 learnings
    KnowledgeTransfer,  # 195 transfers
    AgentMemory,     # ? memories
    AgentSolution,   # ? solutions
    AgentLearningConnection,  # Teacher-student relationships
)
from core.models.agents_registry import AgentContribution  # 1 contribution
```

### Quick Queries
```bash
# Check model counts on Railway
railway run python manage.py shell -c "
from core.models_unified_system import Agent, AgentExecution, AgentLearning, KnowledgeTransfer, AgentMemory, AgentSolution
print(f'Agent: {Agent.objects.count()}')
print(f'AgentExecution: {AgentExecution.objects.count()}')
print(f'AgentLearning: {AgentLearning.objects.count()}')
print(f'KnowledgeTransfer: {KnowledgeTransfer.objects.count()}')
print(f'AgentMemory: {AgentMemory.objects.count()}')
print(f'AgentSolution: {AgentSolution.objects.count()}')
"

# Check recent agent executions
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone
from datetime import timedelta
last_24h = timezone.now() - timedelta(hours=24)
recent = AgentExecution.objects.filter(created_at__gte=last_24h).values('agent__name', 'status').order_by('-created_at')[:20]
for r in recent:
    print(f'{r[\"agent__name\"]}: {r[\"status\"]}')
"
```

---

## Services to Understand

| Service | File | Purpose |
|---------|------|---------|
| Learning Pattern Engine | `core/services/learning_pattern_engine.py` | Mines patterns from agent executions |
| Feedback Loop Engine | `core/services/feedback_loop_engine.py` | Tracks performance feedback |
| Spider Context Builder | `core/services/spider_context_builder.py` | Builds context for agents from spiders |
| Advisor Context Builder | `core/services/advisor_context_builder.py` | Injects advisor wisdom |
| Dynamic Team Builder | `core/services/dynamic_team_builder.py` | Creates cross-domain agent teams |

---

## Agent Architecture Reference

### BaseAgent Methods (Learning Hooks)
```python
class BaseAgent:
    def _record_learning_outcome(self, result, task, context, ...):
        """Records AgentLearning after execution"""

    def _create_execution_memory(self, result, task, memory_type, importance):
        """Creates AgentMemory for important events"""

    def _track_contribution(self, content_type, content_id, contribution_type, score):
        """Tracks AgentContribution for content creation"""

    def _share_knowledge(self, knowledge_type, title, knowledge_value, confidence):
        """Creates knowledge that can be transferred"""
```

### Agent Router
```python
# core/agent_router.py
def route_to_agent(task: str, context: dict) -> str:
    """Deterministic routing - no LLM involved"""
    # Keyword matching to determine agent
    # Returns agent name
```

---

## Local Development

```bash
# 1. Start Redis (if not running)
redis-server --daemonize yes

# 2. Start Daphne (Django ASGI server)
make start

# 3. Start Celery workers
make celery

# 4. Verify everything is running
curl http://localhost:8000/health/ping/

# 5. Access AI Studio
open http://localhost:8000/ai-studio/
```

---

## Railway Commands

```bash
# View logs
railway logs

# Run Django shell
railway run python manage.py shell

# Check body system health
railway run python manage.py shell -c "
from core.services.heart import get_heart_monitor
heart = get_heart_monitor()
print(heart.get_vitals())
"

# Trigger an agent execution manually
railway run python manage.py shell -c "
from core.agents.image_agent import ImageAgent
agent = ImageAgent()
result = agent.execute(
    task='Create a beautiful sunset over mountains',
    context={},
    scifi_context={},
    spider_context={}
)
print(result)
"
```

---

## Files Modified in Session 793

| File | Change |
|------|--------|
| `ai_core/consciousness/neural_orchestra_reality_bridge.py` | Fallback logic, Live Feed, Learning Tab fixes |
| `ai_core/spiders/consciousness.py` | Persistent awakening_time, DB fallbacks |
| `core/agents/image_agent.py` | Updated delegation prompt |
| `core/agents/video_agent.py` | Updated delegation prompt |

---

## Previous Sessions

- **Session 793:** Neural Orchestra & Consciousness Fixes - 6 major issues fixed
- **Session 792:** Body Systems & Railway Fixes - Fixed MUSCULAR, DIGESTIVE, SPINE, spider embeddings
- **Session 791:** Learning System Bootstrap - Fixed model fields, added persona agent context
- **Session 790:** Persona Agent Enhancement - 139 persona agents get spider data
- **Session 789:** Redis Production URL Migration - 27 files updated
- **Session 787-788:** First Railway Deployment - 11 issues fixed
- **Session 786:** DecisionSummary Fix + Curated Documentation Embedding

---

## Quick Reference

### Key Imports
```python
# Agents
from core.agents.base_agent import BaseAgent
from core.agent_router import route_to_agent

# Learning
from core.services.learning_pattern_engine import get_learning_engine
from core.services.feedback_loop_engine import get_feedback_engine

# Models
from core.models_unified_system import (
    Agent, AgentExecution, AgentLearning,
    KnowledgeTransfer, AgentMemory, AgentSolution
)
```

### Neural Orchestra Reality Bridge
```python
from ai_core.consciousness.neural_orchestra_reality_bridge import (
    get_neural_orchestra_bridge,
    get_real_agents_stats,
    get_real_learning_status,
    get_real_ecosystem_live_feed
)
```
