# Session 358: Enhanced Delta Detection for Agent Learning

**Date:** December 5, 2025
**Status:** COMPLETE - Semantic similarity now used in learning cycle

---

## Summary

Implemented Enhanced Delta Detection using semantic similarity (OpenAI embeddings + cosine similarity) to improve duplicate detection in the agent learning cycle. This catches semantic duplicates that exact title matching would miss.

---

## Problem

The Session 357 learning cycle used exact title matching, which missed semantic duplicates:
- "AI Content Tools for Creators" vs "Content Creation AI Tools" = treated as different
- "[Learned] Financial Intelligence" vs "Financial Data Analysis" = treated as different

This led to:
- Redundant knowledge accumulation
- Wasted learning cycles
- Bloated knowledge bases

---

## Solution

### New Service: `KnowledgeSimilarityService`

**Location:** `core/services/knowledge_similarity.py`

Uses:
- OpenAI `text-embedding-3-small` for embeddings
- Cosine similarity for comparison
- Configurable thresholds
- 24-hour cached embeddings for performance

### Key Methods

```python
from core.services.knowledge_similarity import get_knowledge_similarity_service

service = get_knowledge_similarity_service()

# Check if knowledge is semantically similar
result = service.is_semantically_similar(
    agent=student_agent,
    title="AI Content Tools",
    summary="Tools for AI-powered content creation",
    knowledge_type="tool_discovery",
    threshold=0.80
)
# Returns: SimilarityResult(is_similar=True, score=0.85, ...)

# Main learning cycle method
should_transfer, reason = service.should_transfer_knowledge(
    student_agent=student,
    teacher_knowledge=knowledge,
    threshold=0.80
)
# Returns: (False, "Similar to existing: 'Content AI Tools' (score=0.85)")

# Find top N similar knowledge items
results = service.find_most_similar(
    agent=agent,
    title="AI Tools",
    limit=5
)
```

### Thresholds

| Score | Classification | Action |
|-------|---------------|--------|
| 0.90+ | Very Similar | Skip transfer (almost identical) |
| 0.80+ | Similar | Skip transfer (same topic, different wording) |
| 0.70+ | Related | Allow transfer (connected but distinct) |
| < 0.70 | Not Similar | Allow transfer (new knowledge) |

---

## Integration

### Learning Cycle (`core/tasks.py`)

The `run_agent_learning_cycle` task now:

1. **First tries semantic similarity** via `should_transfer_knowledge()`
2. **Falls back to exact title matching** if embeddings fail
3. **Logs skipped transfers** with reason

```python
# Session 358: Enhanced Delta Detection using semantic similarity
try:
    from core.services.knowledge_similarity import get_knowledge_similarity_service
    similarity_service = get_knowledge_similarity_service()

    should_transfer, reason = similarity_service.should_transfer_knowledge(
        student_agent=student,
        teacher_knowledge=knowledge,
        threshold=0.80  # 80% similarity = duplicate
    )

    if not should_transfer:
        logger.debug(f"[LEARNING] Skipping transfer: {reason}")
        continue

except Exception as e:
    # Fallback to Session 357 exact title matching
    ...
```

---

## Testing Results

```python
# Test 1: Exact match
result = service.is_semantically_similar(
    agent=agent,
    title="[Learned] Financial - Financial Intelligence"
)
# is_similar=True, score=0.8124

# Test 2: Modified title (added "AI" everywhere)
result = service.is_semantically_similar(
    agent=agent,
    title="[Learned] AI Financial AI - AI Financial..."
)
# is_similar=False, score=0.7029
```

---

## Files Changed

| File | Changes |
|------|---------|
| `core/services/knowledge_similarity.py` | New service (310 lines) |
| `core/tasks.py` | Integrated service into learning cycle |

---

## Benefits

1. **Smarter Duplicate Detection**: Catches paraphrased/reworded duplicates
2. **Quality Over Quantity**: Prevents redundant knowledge accumulation
3. **Graceful Fallback**: Uses exact matching if embeddings fail
4. **Performance**: Cached embeddings (24-hour TTL)
5. **Configurable**: Adjustable threshold per use case

---

## Service Stats

```python
service.get_service_stats()
# {
#     'total_active_knowledge': 770,
#     'embedding_model': 'text-embedding-3-small',
#     'default_threshold': 0.8,
#     'thresholds': {'very_similar': 0.9, 'similar': 0.8, 'related': 0.7},
#     'openai_available': True
# }
```

---

## Related Sessions

- **Session 357:** Learning cycle fix - expanded knowledge types, improved exact title matching
- **Session 358:** Enhanced delta detection - semantic similarity

---

## Next Steps (Session 359)

1. **Monitor semantic similarity logs** - Track how many transfers are skipped
2. **Tune threshold** - May need adjustment based on real-world usage
3. **Add similarity metrics API** - Expose stats in dashboard
4. **Consider batch embeddings** - For initial knowledge base analysis
