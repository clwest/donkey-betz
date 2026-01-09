# Database Model Reference

**Created:** Session 737 (January 9, 2026)
**Purpose:** Prevent confusion about which database table stores what data

---

## Quick Reference

| Purpose | Correct Model | Import From | Table Name |
|---------|---------------|-------------|------------|
| Agent execution memories | `AgentMemory` | `core.models_unified_system` | `core_agentmemory` |
| Agent execution outcomes | `CoordinatorOutcome` | `core.models_unified_system` | `core_coordinatoroutcome` |
| Agent execution records | `AgentExecution` | `core.models_unified_system` | `core_agentexecution` |
| Spider data ingest | `SpiderData` | `core.models` | `core_spiderdata` |
| Spider learning events | `AgentLearning` | `core.models_unified_system` | `core_agentlearning` |
| User chat history | `ConversationMemory` | `core.models` | `core_conversation_memory` |

---

## Model Details

### Memory Models

#### AgentMemory (ACTIVE - Use This!)
```python
from core.models_unified_system import AgentMemory
```
- **Table:** `core_agentmemory`
- **Purpose:** Stores memories created by agents during execution
- **Has Embeddings:** Yes (pgvector)
- **Created By:** `BaseAgent._create_execution_memory()`
- **Activity:** 647 records in last 7 days

#### ConversationMemory (Low Activity)
```python
from core.models import ConversationMemory
```
- **Table:** `core_conversation_memory`
- **Purpose:** Stores user chat history with Personal AI
- **Has Embeddings:** Yes
- **Created By:** `personal_ai_assistant_enhanced.py`, `personal_ai_orchestrator.py`
- **Activity:** 0 records in last 7 days (PA not heavily used)
- **NOTE:** This is NOT for agent execution memories!

#### MemoryCluster
```python
from core.models_unified_system import MemoryCluster
```
- **Table:** `core_memorycluster`
- **Purpose:** Groups related memories together
- **Activity:** 2 records in last 7 days

---

### Learning Models

#### CoordinatorOutcome (ACTIVE - Use This!)
```python
from core.models_unified_system import CoordinatorOutcome
```
- **Table:** `core_coordinatoroutcome`
- **Purpose:** Records agent execution outcomes for the learning loop
- **Created By:** `LearningLoopService.record_outcome()`
- **Activity:** 2,523 records in last 7 days

#### AgentLearning (Spider Intelligence)
```python
from core.models_unified_system import AgentLearning
```
- **Table:** `core_agentlearning`
- **Purpose:** Records spider intelligence ingest events
- **Created By:** Spider data processing tasks
- **Activity:** 37,493 records in last 7 days
- **NOTE:** This is for spider data events, NOT agent execution learning!

#### UserAgentLearning
```python
from core.models_unified_system import UserAgentLearning
```
- **Table:** `core_useragentlearning`
- **Purpose:** Per-user agent preference learning
- **Activity:** 28 records in last 7 days

---

### Agent Models

#### Agent
```python
from core.models_unified_system import Agent
```
- **Table:** `core_agent`
- **Purpose:** Agent registry (all 72+ agents)
- **Total:** 80 records

#### AgentExecution
```python
from core.models_unified_system import AgentExecution
```
- **Table:** `core_agentexecution`
- **Purpose:** Individual agent execution records with timing and status
- **Activity:** 94 records in last 7 days

---

### Spider Models

#### SpiderData
```python
from core.models import SpiderData
```
- **Table:** `core_spiderdata`
- **Purpose:** Raw data collected by spiders
- **Activity:** 2,822 records in last 7 days
- **Total:** 11,314 records

---

## Common Mistakes to Avoid

### Mistake 1: Checking ConversationMemory for agent activity
```python
# WRONG - This is for user chat history, not agents
from core.models import ConversationMemory
ConversationMemory.objects.filter(created_at__gte=cutoff).count()  # May be 0!

# CORRECT - Use AgentMemory for agent execution memories
from core.models_unified_system import AgentMemory
AgentMemory.objects.filter(created_at__gte=cutoff).count()  # Active!
```

### Mistake 2: Checking AgentLearning for agent execution learning
```python
# WRONG - This is for spider intelligence events
from core.models_unified_system import AgentLearning
AgentLearning.objects.filter(learning_type='agent_execution').count()  # 0!

# CORRECT - Use CoordinatorOutcome for agent execution outcomes
from core.models_unified_system import CoordinatorOutcome
CoordinatorOutcome.objects.filter(created_at__gte=cutoff).count()  # Active!
```

---

## Import Cheat Sheet

```python
# Agent execution metrics
from core.models_unified_system import (
    Agent,              # Agent registry
    AgentExecution,     # Execution records
    AgentMemory,        # Execution memories
    CoordinatorOutcome, # Learning outcomes
)

# Spider data metrics
from core.models import SpiderData
from core.models_unified_system import AgentLearning  # Spider intelligence events

# User interaction metrics
from core.models import ConversationMemory  # PA chat history
```

---

## Verification Query

Use this to verify system health:

```python
from django.utils import timezone
from datetime import timedelta
from core.models_unified_system import AgentMemory, CoordinatorOutcome, AgentExecution
from core.models import SpiderData

cutoff = timezone.now() - timedelta(days=7)

print("=== System Health (Last 7 Days) ===")
print(f"Agent Executions: {AgentExecution.objects.filter(created_at__gte=cutoff).count()}")
print(f"Agent Memories: {AgentMemory.objects.filter(created_at__gte=cutoff).count()}")
print(f"Learning Outcomes: {CoordinatorOutcome.objects.filter(created_at__gte=cutoff).count()}")
print(f"Spider Data: {SpiderData.objects.filter(discovered_at__gte=cutoff).count()}")
```

---

*Document created to prevent future confusion about database tables.*
*See: docs/audits/SESSION_736_INTEGRATION_REALITY_REPORT.md for the incident that prompted this.*
