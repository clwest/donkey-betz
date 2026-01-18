# Session 768: Memory Safety Classification System

**Date:** January 17, 2026
**Focus:** Preventing test/exploratory content from polluting the learning system

## Context

ChatGPT analyzed a conversation where agents were tested with "Say your name and one thing you can do" prompts. The system captured this test as a learning artifact - a significant architectural flaw where:

> "Not all conversations should be allowed to teach the system."

This conversation became a **canary test** exposing that the system lacked distinction between:
- **Ephemeral agent tests** (health checks, connectivity tests)
- **Persistent memory contributions** (real learning, real work)

## Key Insight from ChatGPT

> "That one-sentence prompt almost guarantees superficial, self-promotional blurbs that will poison your training set."

Patterns that are **embedding poison**:
- "Describe yourself in one sentence"
- "State your capability"
- "What are you good at?"

These incentivize optimization for sound bites, erase context, and pollute retrieval later.

## What Was Implemented

### 1. Memory Safety Classification (AgentMemory model)

Added `safety_class` field with values:
- `test_only` - Health checks, connectivity tests - **NEVER embed/learn**
- `exploratory` - Research, exploration - review before using
- `candidate` - Default, potential learning - requires validation
- `approved` - Validated, safe to embed and learn from

### 2. Embedding Poison Risk Detection

Added `_detect_poison_risk()` method that flags content as high-risk if it is:
- **Too short** (<15 words) - capability one-liners
- **Self-promotional** - patterns like "I can", "I specialize in", "My capability"
- **Lacks context** - no task/situation details
- **Test pattern** - "say your name", "introduce yourself", "health check"
- **Highly abstract** - no concrete details (file, code, data, result, etc.)

Returns `poison_risk_score` (0-1) and `poison_risk_factors` list.

### 3. Health Check Mode in BaseAgent

Added `health_check_mode` parameter to `BaseAgent.__init__()`:
```python
agent = SomeAgent(user, health_check_mode=True)
```

When enabled:
- `_record_learning_outcome()` skips recording
- `_create_execution_memory()` skips memory creation
- No embeddings generated

### 4. Updated Memory Creation Pipeline

Both `AgentMemory.create_memory()` and `MemoryEmbeddingService.create_memory()`:
- Detect poison risk automatically
- Respect safety_class
- Only generate embeddings for `approved` + low poison risk (<0.5)
- Auto-approve `candidate` with very low risk (<0.3)
- Never embed `test_only`

### 5. Backfill Protection

`MemoryEmbeddingService.backfill_embeddings()` now excludes:
- `test_only` memories
- Memories with `poison_risk_score >= 0.5`

## Files Changed

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added `safety_class`, `poison_risk_score`, `poison_risk_factors` fields + `_detect_poison_risk()` method to AgentMemory |
| `core/services/memory_embedding_service.py` | Updated `create_memory()`, `update_memory_embedding()`, `backfill_embeddings()` to respect safety classification |
| `core/agents/base_agent.py` | Added `health_check_mode` parameter + checks in `_record_learning_outcome()`, `_create_execution_memory()` |
| `core/migrations/0172_session_768_memory_safety_classification.py` | Migration for new fields |

## Usage Examples

### Running a Health Check (No Learning)
```python
agent = ImageAgent(user, health_check_mode=True)
result = agent.execute("Say your name and one capability", context={}, scifi_context={}, spider_context={})
# No memory created, no learning recorded
```

### Creating Test-Only Memory
```python
memory = AgentMemory.create_memory(
    agent=agent,
    title="Health check response",
    content="ImageAgent: I create images",
    safety_class='test_only'  # Will NOT generate embedding
)
```

### Creating Approved Memory
```python
memory = AgentMemory.create_memory(
    agent=agent,
    title="Successfully created logo for client",
    content="Created minimalist tech logo with blue gradient...",
    safety_class='approved'  # Will generate embedding if poison_risk < 0.5
)
```

## Architectural Principle

The system now distinguishes between:

| Type | Purpose | Embed? | Learn? |
|------|---------|--------|--------|
| `test_only` | Health checks | ❌ | ❌ |
| `exploratory` | Research | Review | Review |
| `candidate` | Default | If low risk | If low risk |
| `approved` | Validated | ✅ | ✅ |

## ChatGPT's Final Assessment

> "This wasn't noise. This was your system saying: 'Hey — if you let everything teach me, I will break later.'"

The Memory Safety Classification system implements the system's immune response - slowing down and requiring validation before content can teach the system.

## Next Steps (Not Implemented)

1. **Admin UI** - Interface to review `candidate` memories and promote to `approved`
2. **Bulk Safety Classification** - Backfill existing memories with safety scores
3. **API Filtering** - Expose safety_class in API responses for frontend filtering
4. **Monitoring Dashboard** - Track poison risk distribution over time
