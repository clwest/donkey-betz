# Memory Safety Classification System

**Session 768 | January 17, 2026**

## Overview

The Memory Safety Classification system prevents test, exploratory, and low-quality content from polluting the agent learning system and embedding space. It implements an "immune response" that protects the system from convenience prompts that generate bad long-term memory.

## The Problem

When testing agents with prompts like "Say your name and one thing you can do", these test interactions were captured as learning artifacts. This creates several problems:

1. **Embedding Poison** - Self-promotional one-liners pollute retrieval
2. **False Learning** - Test patterns get memorized as real interactions
3. **Context Collapse** - Short responses lack the context needed for good RAG
4. **Gaming Vulnerability** - Easy to inject biased content via simple prompts

### Patterns That Poison Embeddings

These prompts feel harmless but are dangerous for long-term memory:

| Prompt Pattern | Why It's Poison |
|----------------|-----------------|
| "Describe yourself in one sentence" | Incentivizes sound bites over substance |
| "State your capability" | Erases context, highly gameable |
| "What are you good at?" | Self-promotional, collapses nuance |
| "Introduce yourself" | Abstract, lacks concrete evidence |

## Architecture

### Safety Classification Levels

| Class | Description | Embed? | Learn? | Use Case |
|-------|-------------|--------|--------|----------|
| `test_only` | Health checks, connectivity tests | Never | Never | Agent verification |
| `exploratory` | Research, exploration | Review | Review | Codebase exploration |
| `candidate` | Default for new memories | If low risk | If low risk | Normal operation |
| `approved` | Validated, safe content | Always | Always | Real work output |

### Poison Risk Detection

The `_detect_poison_risk()` method scores content (0-1) based on:

| Risk Factor | Score Increase | Pattern |
|-------------|----------------|---------|
| `too_short` | +0.30 | Less than 15 words |
| `self_promotional` | +0.25 | "I can", "I specialize in", "My capability" |
| `test_pattern` | +0.40 | "say your name", "health check", "testing" |
| `lacks_context` | +0.15 | Context field empty or < 20 chars |
| `highly_abstract` | +0.20 | No concrete terms (file, code, data, result) |

### Embedding Decision Flow

```
Memory Created
     |
     v
[Detect Poison Risk]
     |
     v
safety_class == 'test_only'? --> YES --> No Embedding (ever)
     |
     NO
     v
poison_risk >= 0.5? --> YES --> No Embedding
     |
     NO
     v
safety_class == 'approved'? --> YES --> Generate Embedding
     |
     NO
     v
safety_class == 'candidate' AND poison_risk < 0.3? --> Auto-Approve + Embed
     |
     NO
     v
Store as Candidate (no embedding yet)
```

## Database Schema

### New Fields on AgentMemory

```python
class AgentMemory(models.Model):
    # Existing fields...

    # Session 768: Memory Safety Classification
    SAFETY_CLASS_CHOICES = [
        ('test_only', 'Test Only'),
        ('exploratory', 'Exploratory'),
        ('candidate', 'Candidate Learning'),
        ('approved', 'Approved Learning'),
    ]
    safety_class = models.CharField(
        max_length=20,
        choices=SAFETY_CLASS_CHOICES,
        default='candidate',
        db_index=True
    )

    poison_risk_score = models.FloatField(default=0.0)
    poison_risk_factors = models.JSONField(default=list, blank=True)
```

## Usage

### Health Check Mode (Skip All Learning)

When testing agent connectivity, use health_check_mode to prevent any learning:

```python
from core.agents.image_agent import ImageAgent

# Create agent in health check mode
agent = ImageAgent(user, health_check_mode=True)

# Execute - NO memory created, NO learning recorded
result = agent.execute(
    "Say your name and one capability",
    context={},
    scifi_context={},
    spider_context={}
)
```

### Creating Test-Only Memory

When you must create a memory but don't want it embedded:

```python
from core.models_unified_system import AgentMemory

memory = AgentMemory.create_memory(
    agent=agent_model,
    title="Health check response",
    content="ImageAgent: I create images",
    safety_class='test_only'  # Will NEVER generate embedding
)
```

### Creating Approved Memory

For real work that should always be learned from:

```python
memory = AgentMemory.create_memory(
    agent=agent_model,
    title="Successfully created client logo",
    content="Created minimalist tech logo with blue gradient, 1024x1024...",
    context="Client: Acme Corp, Brief: Modern, minimal, tech-focused",
    safety_class='approved'  # Will generate embedding if poison_risk < 0.5
)
```

### Using Memory Embedding Service

The service automatically detects poison risk:

```python
from core.services.memory_embedding_service import MemoryEmbeddingService

service = MemoryEmbeddingService()

# This will auto-detect poison risk and classify
memory = service.create_memory(
    agent=agent_model,
    title="Research findings",
    content="Analyzed 50 competitor logos...",
    safety_class='candidate'  # Auto-promoted to 'approved' if low risk
)
```

## API

### Memory Creation Response

When creating memories via API, the response includes safety info:

```json
{
    "id": "uuid-here",
    "title": "Memory title",
    "safety_class": "candidate",
    "poison_risk_score": 0.15,
    "poison_risk_factors": ["lacks_context"],
    "has_embedding": true
}
```

### Querying by Safety Class

```python
# Get only approved memories
approved = AgentMemory.objects.filter(
    agent=agent,
    safety_class='approved'
)

# Exclude test memories from retrieval
learnable = AgentMemory.objects.exclude(
    safety_class='test_only'
)

# Find high-risk memories needing review
risky = AgentMemory.objects.filter(
    poison_risk_score__gte=0.5
)
```

## Files Reference

| File | Purpose |
|------|---------|
| `core/models_unified_system.py` | AgentMemory model with safety fields |
| `core/services/memory_embedding_service.py` | Embedding service with safety checks |
| `core/agents/base_agent.py` | BaseAgent with health_check_mode |
| `core/migrations/0172_session_768_memory_safety_classification.py` | Database migration |

## Future Enhancements

1. **Admin Review UI** - Interface to review `candidate` memories and promote to `approved`
2. **Bulk Classification** - Backfill existing memories with safety scores
3. **Monitoring Dashboard** - Track poison risk distribution over time
4. **API Filtering** - Expose safety_class in all memory API endpoints
5. **Decay Rules** - Auto-demote stale `approved` memories to `candidate`

## Related Documentation

- `docs/handoffs/SESSION_768_MEMORY_SAFETY_CLASSIFICATION.md` - Session handoff
- `docs/DATABASE_MODEL_REFERENCE.md` - Complete model documentation
- `docs/AGENTS.md` - Agent architecture including BaseAgent
