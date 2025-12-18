# Session 491: Agent Intelligence Context Fix

**Date:** December 18, 2025
**Focus:** Fix ForeignKey bug preventing knowledge retrieval in Agent Intelligence Context service

---

## Summary

Fixed a bug in `AgentIntelligenceContextService._get_relevant_knowledge()` where the `spider_category` ForeignKey was being filtered as if it were a CharField, causing all knowledge queries to fail with "Field 'id' expected a number but got 'tech'".

---

## The Bug

**Before (broken):**
```python
# spider_category is a ForeignKey to SpiderCategory
query = query.filter(spider_category__in=['tech', 'innovation'])
# Error: Field 'id' expected a number but got 'tech'
```

**After (fixed):**
```python
# Access the slug field through the FK relationship
query = query.filter(spider_category__slug__in=['tech', 'innovation'])
```

---

## Changes Made

### `core/services/agent_intelligence_context.py`

**1. Fixed FK filter (line 264):**
```python
# Session 491: Fix FK filter - spider_category is a ForeignKey, not a CharField
query = query.filter(spider_category__slug__in=categories)
```

**2. Optimized select_related (line 247):**
```python
# Session 491: Include spider_category in select_related to avoid N+1 queries
query = base_query.filter(search_conditions).select_related('agent', 'spider_category')...
```

**3. Fixed domain display (line 278):**
```python
# Session 491: spider_category is a FK - access .name for display
'domain': knowledge.spider_category.name if knowledge.spider_category else '',
```

---

## Test Results

**Before fix:**
```
Knowledge items: 0  (broken)
Conversations: 0
Policies: 5
```

**After fix:**
```
Knowledge items: 5  (working!)
Conversations: 0
Policies: 5

Knowledge Items:
  - [MeetingCoordinatorAgent] Convertkit - Content Creation Intelligence...
    Domain: Tech News & Innovation | Type: trend
  - [TrendAnalysisAgent] Convertkit - Content Creation Intelligence...
    Domain: Tech News & Innovation | Type: trend
```

---

## Service Integration Status

The service was already integrated into:
- `CompetitorAnalysisAgent.execute()` (lines 668-696)
- `CustomerResearchAgent.execute()` (similar location)

These agents call:
```python
agent_intel_context = self.agent_intelligence.get_context_for_research(
    topic=task,
    domain=domain,
    max_items_per_category=5
)
agent_intel_prompt = agent_intel_context.to_prompt_context()
```

The bug was preventing knowledge from being injected - now it works correctly.

---

## What the Service Provides

| Source | Data |
|--------|------|
| AgentKnowledgeSource | What agents have learned from spiders |
| KnowledgeTransfer | What agents have shared with each other |
| AgentConversation | What agents have discussed |
| AgentDecisionSummary | Boardroom policies and decisions |

All of this is formatted as context and injected into business research prompts.

---

## Files Modified

1. **core/services/agent_intelligence_context.py** (~6 lines changed)
   - Fixed spider_category FK filter
   - Added spider_category to select_related
   - Fixed domain display for FK

---

## Session 491 Summary

| Task | Status |
|------|--------|
| Agent Intelligence Context Fix | Complete |

The service was already integrated but had a bug preventing knowledge retrieval. Now business research agents receive full collective intelligence context including learned knowledge from 5+ agents.
