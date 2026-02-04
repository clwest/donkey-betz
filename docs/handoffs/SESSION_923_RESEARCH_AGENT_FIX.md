# Session 923: ResearchAgent Failure Investigation

**Date:** February 3, 2026
**PR:** #817

## Summary

Investigated why ~45% of Stage 1 document generation attempts were failing with "Research returned no results". Found three interrelated root causes and implemented fixes.

## Root Cause Analysis

### Problem 1: Prompt Mismatch

ResearchAgent has this in its system prompt (line 60):
```
Your ONLY job is to research topics and gather information. You do NOT create content.
```

But the Stage 1 prompt said:
```
Generate a Research Brief document for this initiative.
...
Create a comprehensive Research Brief document that builds on the previous stages.
```

GPT was being told to create content by an agent that explicitly says it doesn't create content.

### Problem 2: Keyword Trigger

ResearchAgent's system prompt (line 69-76) says:
```
INTERNAL DATA (Session 884):
For tasks about system internals (experiments, failures, executions, initiatives), use query_internal_data
```

The old prompt mentioned "initiative" multiple times:
- "Generate a Research Brief document for this initiative"
- "## Initiative Context"

When GPT saw "initiative", it called `query_internal_data` instead of `web_search`.

### Problem 3: Model Field Error

`query_internal_data` at line 1714 tried to filter:
```python
queryset = queryset.filter(Q(blocked=True) | Q(status='BLOCKED'))
```

But Initiative model doesn't have a `blocked` field. Error:
```
Cannot resolve keyword 'blocked' into field. Choices are: action_items, auto_topic, ...
```

## Fixes Applied

### 1. New Stage 1 Prompt (core/tasks.py)

```python
prompt = f"""Research this topic using EXTERNAL sources (web_search, spider_query).
DO NOT use query_internal_data - this is NOT about internal system analysis.

## Research Topic
{research_topic}

## Background Context
{initiative.description or 'Research this topic thoroughly.'}{enhanced_context}

## Instructions
1. Use web_search to find current information about this topic from the internet
2. Use spider_query to check recent news and trends from our spider network
3. Synthesize the findings into actionable insights

## Required Output
Provide a research brief with:
1. **Research Findings** - Specific facts, statistics, and data points you discovered
2. **Data Sources** - Which web sources and spider data you used
3. **Key Insights** - 3-5 most important takeaways
4. **Recommendation** - Should this project proceed? Why or why not?

IMPORTANT: Use web_search as your PRIMARY tool. This is external market/topic research, NOT internal system analysis."""
```

Key changes:
- Removed word "initiative" from prompt (triggers internal data query)
- Explicitly says "DO NOT use query_internal_data"
- Clear instructions to use web_search as PRIMARY tool
- Removed "generate document" language (ResearchAgent doesn't create content)

### 2. Initiative Filter Fix (core/agents/research_agent.py)

```python
# Old (broken)
if filter_type == 'blocked':
    queryset = queryset.filter(Q(blocked=True) | Q(status='BLOCKED'))

# New (fixed)
if filter_type == 'blocked':
    queryset = queryset.filter(status='BLOCKED')
```

Also added `stalled` filter and improved field access.

### 3. Research Topic Logging

Added logging to track what topic is being researched:
```python
logger.info(f"📝 [STAGE-GEN] Stage 1 research topic: {research_topic[:100]}...")
```

## Flow Diagram

```
Old Flow (Broken):
┌──────────────────────┐
│ generate_initiative_ │
│ stage_document()     │
└──────────┬───────────┘
           │ "Generate a Research Brief document for this initiative"
           v
┌──────────────────────┐
│ ResearchAgent        │ System prompt: "do NOT create content"
│ (prompt mismatch!)   │
└──────────┬───────────┘
           │ Sees "initiative" → calls query_internal_data
           v
┌──────────────────────┐
│ query_internal_data  │
│ filter(blocked=True) │ ← Field doesn't exist!
└──────────┬───────────┘
           │ Error
           v
┌──────────────────────┐
│ "Research returned   │
│  no results"         │
└──────────────────────┘

New Flow (Fixed):
┌──────────────────────┐
│ generate_initiative_ │
│ stage_document()     │
└──────────┬───────────┘
           │ "Research this topic using EXTERNAL sources"
           │ "DO NOT use query_internal_data"
           v
┌──────────────────────┐
│ ResearchAgent        │
│ (clear instructions) │
└──────────┬───────────┘
           │ Calls web_search/spider_query
           v
┌──────────────────────┐
│ External research    │
│ tools                │
└──────────┬───────────┘
           │ Returns results
           v
┌──────────────────────┐
│ Research Brief       │
│ created successfully │
└──────────────────────┘
```

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | New Stage 1 prompt with explicit tool instructions |
| `core/agents/research_agent.py` | Fixed Initiative filter (blocked → status='BLOCKED') |

## Testing

The fix needs to be merged before full testing. After merge:

```bash
railway run python manage.py shell -c "
from core.models_document_registry import InitiativeStage
from core.tasks import generate_initiative_stage_document

stages = InitiativeStage.objects.filter(
    status='DRAFT', stage=1, initiative__status='ACTIVE', document__isnull=True
).select_related('initiative')[:10]

success = 0
for stage in stages:
    result = generate_initiative_stage_document(str(stage.initiative.id), 1)
    if result.get('success'):
        success += 1
print(f'Success rate: {success}/10')
"
```

## Next Steps

1. Merge PR #817
2. Run test batch to measure new success rate
3. If success rate > 80%, continue full backfill of 216 remaining initiatives
4. If still failing, consider alternative approaches (ThinkingAgent, ContentWriterAgent, or direct spider data injection)

## Related PRs

- #812: `router.execute_agent()` → `router.route()` fix
- #814: Name detection for incomplete initiative names
- #816: Failed Agents UI wiring (error_message display)
- **#817**: This fix - explicit external research prompt + Initiative filter
