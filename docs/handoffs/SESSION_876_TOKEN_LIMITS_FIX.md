---
originating_session: 876
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 876: GPT-5-mini Token Limits Fix

## Summary
Fixed critical production issue where agents were returning empty content despite successful API calls. The root cause was GPT-5-mini reasoning models consuming all available tokens for internal reasoning, leaving nothing for visible output.

## Problem Statement
- **Symptom**: Operations Tab showing "No content generated" for all agent executions
- **Symptom**: Memory Palace not updating since previous day
- **Observation**: Production Celery workers running, HTTP 200 responses, but empty content

## Root Cause Analysis
GPT-5-mini is a **reasoning model**. Unlike standard chat models, reasoning models:
1. Consume tokens **internally** for chain-of-thought reasoning
2. Generate visible output from the **remaining** tokens
3. With `max_completion_tokens=1000`, complex prompts would exhaust all tokens on reasoning

**Example**: A content generation prompt might use 800-900 tokens for internal reasoning, leaving only 100-200 tokens for actual output - often resulting in empty or truncated responses.

## Solution
Increased `max_completion_tokens` from 1000 → 4000 across all GPT-5-mini usage:

| File | Context | Old | New |
|------|---------|-----|-----|
| `core/tasks.py` (line ~6305) | Agent conversations | 1000 | 4000 |
| `core/tasks.py` (line ~8736) | Dream generation | 1000 | 4000 |
| `core/views_rag_embeddings.py` | RAG query responses | 1000 | 4000 |
| `core/views_advisor_api.py` | Advisor consultations | 1000 | 4000 |
| `core/views_assistant_rag_enhanced.py` | Enhanced assistant | 1000 | 4000 |
| `core/views_assistant_intelligent.py` | Intelligent assistant | 1000 | 4000 |
| `core/services/weekly_synthesis.py` | Weekly reports | 1000 | 4000 |
| `core/services/research_orchestrator.py` | Opportunity scoring | 1000 | 4000 |
| `core/agents/ai_series_workflow_agent.py` | Script generation | 1000 | 4000 |
| `core/agents/business/customer_research_agent.py` | Persona generation | 1000 | 2000* |
| `pipelines/services.py` | Image prompt generation | 1000 | 4000 |
| `agents/executors/income_builder_executor.py` | Income analysis | 1000 | 4000 |
| `agents/executors/ai_project_executor.py` | Content generation | 1000 | 4000 |
| `coleadership/reflections.py` | Decision reflections | 1000 | 4000 |

*gpt-4o-mini (non-reasoning model) only needs 2000

## Technical Details

### GPT-5-mini Reasoning Model Behavior
```python
# WRONG - All tokens consumed by reasoning
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=1000  # Insufficient for reasoning + output
)

# CORRECT - Adequate headroom for reasoning + output
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=4000  # 4x increase for reasoning models
)
```

### Token Usage Logging (added for debugging)
```python
if hasattr(response, 'usage') and response.usage:
    total_tokens = response.usage.completion_tokens
    logger.info(f"[CONVERSATIONS] {speaker.name} used {total_tokens} completion tokens")
```

## Files Changed
| File | Changes |
|------|---------|
| `core/tasks.py` | 2 token limit increases + token usage logging |
| `core/views_rag_embeddings.py` | Token limit increase |
| `core/views_advisor_api.py` | Token limit increase |
| `core/views_assistant_rag_enhanced.py` | Token limit increase |
| `core/views_assistant_intelligent.py` | Token limit increase |
| `core/services/weekly_synthesis.py` | Token limit increase |
| `core/services/research_orchestrator.py` | Token limit increase |
| `core/agents/ai_series_workflow_agent.py` | Token limit increase |
| `core/agents/business/customer_research_agent.py` | Token limit increase |
| `pipelines/services.py` | Token limit increase |
| `agents/executors/income_builder_executor.py` | Token limit increase |
| `agents/executors/ai_project_executor.py` | Token limit increase |
| `coleadership/reflections.py` | Token limit increase |

## Related PRs
- PR #554 - Updated with token limit fixes (originally context tracing system)

## Verification
After Railway deployment:
1. Check Operations Tab - should show actual content instead of "No content generated"
2. Check Memory Palace - should show new entries after agent executions
3. Monitor Celery logs for token usage info

## Session Stats
- Duration: Session 876
- Files Changed: 13
- Total Token Limit Changes: 14 (12 files, 2 in core/tasks.py)
- PR Updated: #554

## Future Considerations
1. **Token Usage Monitoring**: Consider adding a dashboard to track token consumption
2. **Dynamic Limits**: Could adjust based on prompt complexity
3. **Cost Awareness**: 4x token increase = higher API costs (but necessary for functionality)
