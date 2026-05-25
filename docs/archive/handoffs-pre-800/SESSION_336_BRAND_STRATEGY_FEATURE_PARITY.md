# Session 336: BrandStrategyAgent Feature Parity with CompetitorAnalysisAgent

**Date:** December 3, 2025
**Branch:** `feature/session-52-ai-assistant`

---

## Overview

This session achieved **feature parity** between `BrandStrategyAgent` and `CompetitorAnalysisAgent`. The user identified that BrandStrategyAgent was missing key features that CompetitorAnalysisAgent had, specifically:

- `unified_search` service (Session 303)
- `refresh_spider_data` tool
- `get_prior_research` tool
- Auto spider refresh at start of execute()

These features are critical for the "cumulative intelligence" vision where each agent builds on existing research.

---

## Changes Made

### 1. Added `unified_search` Property (line 247-253)

```python
@property
def unified_search(self):
    """Session 336: Lazy-load Unified Intelligence Search Service."""
    if self._unified_search is None:
        from core.services.unified_intelligence_search import get_unified_intelligence_search
        self._unified_search = get_unified_intelligence_search()
    return self._unified_search
```

### 2. Added `refresh_spider_data` Tool (lines 230-252)

```python
{
    "type": "function",
    "function": {
        "name": "refresh_spider_data",
        "description": "Trigger spider network to fetch fresh, real-time data before analysis.",
        "parameters": {
            "properties": {
                "categories": {"type": "array", "items": {"type": "string"}}
            },
            "required": []
        }
    }
}
```

### 3. Added `get_prior_research` Tool (lines 253-281)

```python
{
    "type": "function",
    "function": {
        "name": "get_prior_research",
        "description": "Retrieve relevant past research from previous competitor, customer, and brand analyses.",
        "parameters": {
            "properties": {
                "market_topic": {"type": "string"},
                "research_type": {"type": "string", "enum": ["competitor", "customer", "brand_strategy", "all"]},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["market_topic"]
        }
    }
}
```

### 4. Added Auto Spider Refresh at Execute Start (lines 412-436)

```python
# Session 336: Store current task for tool access
self._current_task = task

# Session 336: Auto-trigger spider refresh for fresh branding data
try:
    refresh_result = self.unified_search.refresh_spiders_for_query(task)
    logger.info(f"Auto-triggered spider refresh: {refresh_result.get('categories', [])}")
except Exception as e:
    logger.warning(f"Auto spider refresh failed (continuing anyway): {e}")

# Session 336: Get prior research context
prior_context = ""
try:
    prior_context = self.unified_search.get_research_context(
        query=task,
        max_spider_items=3,
        max_research_items=2
    )
except Exception as e:
    logger.warning(f"Prior research lookup failed (continuing anyway): {e}")
```

### 5. Added Tool Handlers (lines 707-770)

```python
elif tool_name == "refresh_spider_data":
    result = self.unified_search.refresh_spiders_for_query(
        query=self._current_task if hasattr(self, '_current_task') else '',
        categories=categories if categories else None
    )
    return {'success': True, 'data': result}

elif tool_name == "get_prior_research":
    results = self.unified_search.unified_search(
        query=market_topic,
        include_spiders=False,
        include_research=True,
        research_limit=limit
    )
    return {'success': True, 'data': [...], 'context': context}
```

### 6. Frontend Updates for `brand_strategy` Research Type

Updated `ai_core/templates/ai_image_studio.html` in 4 locations:

1. **Line 51553-51554**: Added brand_strategy detection for project creation
2. **Line 51623-51624**: Added brand_strategy detection for adding research to project
3. **Lines 30915-30916**: Added brand_strategy icon and label in project dropdown
4. **Line 27104**: Added brand_strategy_agent to tool condition check

---

## Feature Comparison

| Feature | CompetitorAnalysisAgent | BrandStrategyAgent (After Session 336) |
|---------|------------------------|----------------------------------------|
| `unified_search` property | Yes | **Yes** |
| `refresh_spider_data` tool | Yes | **Yes** |
| `get_prior_research` tool | Yes | **Yes** |
| Auto spider refresh | Yes | **Yes** |
| Prior research context | Yes | **Yes** |
| Frontend dropdown support | Yes | **Yes** |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/business/brand_strategy_agent.py` | Added unified_search property, 2 new tools, tool handlers, auto spider refresh |
| `ai_core/templates/ai_image_studio.html` | Added brand_strategy detection in 4 locations |

---

## Testing

### Prerequisites
1. A project with existing research (e.g., "Donkey Betz Podcast")
2. Servers running: `make start && make celery`

### Test Steps
1. Go to http://localhost:8000/ai-studio/
2. Click on a project with competitor/customer research
3. Say "Create a brand strategy"
4. Verify:
   - Spider refresh happens automatically
   - Prior research is used as context
   - Report displays with 6 sections
   - "Add to Project" button works
   - Dropdown shows "Brand Strategy" with icon

---

## Architecture After Session 336

```
User Request: "Create a brand strategy"
         ↓
BrandStrategyAgent (Session 335 + 336)
         ↓
    ┌────────────────────────┐
    │ AUTO: spider refresh   │ → Ensures fresh data
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ AUTO: prior research   │ → Injects existing research context
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ get_project_research   │ → Reads project research
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ refresh_spider_data    │ → Optional: trigger more spiders
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ get_prior_research     │ → Optional: get more prior research
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ spider_query           │ → Gets brand trends
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ web_search             │ → Gets best practices
    └────────────────────────┘
         ↓
    ┌────────────────────────┐
    │ synthesize_brand_strategy │ → GPT synthesizes report
    └────────────────────────┘
         ↓
    BusinessResearchResult (saved with research_type='brand_strategy')
         ↓
    Frontend dropdown shows "Brand Strategy"
```

---

## Key Principle Reinforced

**"All agents should work like CompetitorAnalysisAgent"**

This session ensures BrandStrategyAgent follows the same pattern:
1. Auto-refresh spider data for fresh insights
2. Auto-inject prior research context
3. Provide tools for explicit data refresh/retrieval
4. Save to BusinessResearchResult with proper research_type
5. Frontend properly displays in project dropdown

---

**Status:** Session 336 COMPLETE. BrandStrategyAgent now has full feature parity with CompetitorAnalysisAgent!
