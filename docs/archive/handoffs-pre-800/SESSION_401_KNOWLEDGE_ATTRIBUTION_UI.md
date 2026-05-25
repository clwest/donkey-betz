# Session 401: Knowledge Attribution UI - Making Intelligence Visible

**Date:** December 9, 2025

---

## Summary

This session implemented **Knowledge Attribution** - a transparency feature that shows users what intelligence sources influenced each AI response. Users can now see:
- Which spider sources provided data
- What agents have learned that's relevant
- Confidence scores and data freshness
- Total sources consulted

---

## Problem Statement

The platform had a powerful knowledge pipeline (Session 400):
```
Spider Data (6,500+) -> Embeddings (2,100+) -> Learning Bridge -> Knowledge (878) -> Agent Prompts
```

But users had no visibility into this intelligence! They couldn't see:
- Why the AI responded the way it did
- What data sources were consulted
- How confident the AI was in its response
- How fresh the data was

---

## Solution: Knowledge Attribution

### Backend Changes

**1. `KnowledgeAttribution` Dataclass** (`core/agents/base_agent.py`)
```python
@dataclass
class KnowledgeAttribution:
    spider_sources: List[str]        # e.g., ['techcrunch', 'hackernews']
    knowledge_items: List[Dict]       # Relevant knowledge used
    confidence_score: float           # 0.0 - 1.0
    data_freshness_hours: float       # How old is the data
    total_sources: int                # Total sources consulted

    def to_dict(self) -> dict: ...
```

**2. `AgentResult` Updated**
- Added optional `knowledge_attribution` field
- Agents can now return attribution metadata with their responses

**3. `PersonalAssistantAgent` Updated**
- `_answer_question()` now uses `_build_prompt_with_attribution()`
- `_gpt_route()` now includes attribution and merges with delegated agent's attribution
- Direct routing path also builds attribution

**4. `SuperPlatformCoordinator` Updated**
- `_process_with_clean_architecture()` now extracts `knowledge_attribution` from agent result
- Includes attribution in response metadata

### Frontend Changes

**5. `formatKnowledgeAttribution()` Function** (`ai_core/templates/partials/js/ai_assistant.html`)
- Beautiful gradient card showing attribution
- Spider source badges
- Knowledge item summaries with agent names
- Stats row (confidence, sources, freshness)

**6. Clean Architecture Response Handler**
- Now checks for `metadata.knowledge_attribution`
- Renders attribution UI below responses

---

## UI Design

The attribution card appears below AI responses:

```
+------------------------------------------+
| Knowledge Attribution                     |
|                                           |
| Sources: [techcrunch] [hackernews] [reddit]|
|                                           |
| Learned:                                  |
| ResearchAgent: AI trends in 2025...       |
| CTOAgent: Technical analysis of...        |
|                                           |
| 87% confidence | 3 sources | 2h ago       |
+------------------------------------------+
```

**Design Details:**
- Cyan/teal gradient background (matches platform theme)
- Source badges with rounded corners
- Truncated titles for readability
- Freshness displayed as human-readable time

---

## Files Changed

| File | Changes |
|------|---------|
| `core/agents/base_agent.py` | `KnowledgeAttribution` dataclass (already existed from Session 400) |
| `core/agents/personal_assistant_agent.py` | Added attribution to `_answer_question()`, `_gpt_route()`, and direct routing |
| `core/super_platform/coordinator.py` | Include attribution in clean architecture response metadata |
| `ai_core/templates/partials/js/ai_assistant.html` | Added `formatKnowledgeAttribution()` function and call site |

---

## How It Works

1. **User sends message** to AI Assistant
2. **PersonalAssistantAgent** receives task
3. Agent calls `_build_prompt_with_attribution(task, scifi_ctx, spider_ctx)`
4. This method:
   - Calls `_get_relevant_knowledge_for_task(task)` to find relevant knowledge
   - Calls `_build_knowledge_attribution(knowledge)` to create attribution object
   - Builds the full prompt with knowledge injected
   - Returns both (prompt, attribution)
5. Agent executes with enriched prompt
6. Agent returns `AgentResult` with `knowledge_attribution` attached
7. **SuperPlatformCoordinator** extracts attribution into response metadata
8. **Frontend** receives response with `metadata.knowledge_attribution`
9. **formatKnowledgeAttribution()** renders the attribution card

---

## Testing

```bash
# Test knowledge retrieval
.venv/bin/python manage.py shell -c "
from core.agents.research_agent import ResearchAgent
agent = ResearchAgent()
knowledge = agent._get_relevant_knowledge_for_task('AI trends')
print(f'Found {len(knowledge)} items')
attribution = agent._build_knowledge_attribution(knowledge)
print(f'Spider sources: {attribution.spider_sources}')
print(f'Confidence: {attribution.confidence_score}')
"

# Full test
.venv/bin/python manage.py shell -c "
from core.agents.personal_assistant_agent import PersonalAssistantAgent
pa = PersonalAssistantAgent()
prompt, attr = pa._build_prompt_with_attribution('What are AI trends?', {}, {})
print(f'Has knowledge: {\"Relevant Knowledge\" in prompt}')
print(f'Attribution: {attr.to_dict()}')
"
```

---

## Next Steps (Future Sessions)

1. **Improve spider_sources population** - Currently AgentKnowledgeSource entries often lack `source_spider_names`
2. **Add clickable sources** - Link to original articles/data
3. **Expand attribution to legacy endpoint** - Currently only works with Clean Architecture endpoint
4. **Add attribution history** - Let users see how attribution evolves over conversation
5. **Attribution analytics** - Track which sources are most helpful

---

## Related Sessions

- **Session 400:** Agent Knowledge Pipeline - Added knowledge retrieval and prompt injection
- **Session 399:** Spider Renames and Data Feed Fix
- **Session 271:** Clean Architecture Phase 5

---

## Session Accomplishments

1. Created `KnowledgeAttribution` dataclass (Session 400)
2. Updated `AgentResult` to include attribution
3. Modified `PersonalAssistantAgent` to attach attribution to all responses
4. Updated `SuperPlatformCoordinator` to pass attribution through
5. Created `formatKnowledgeAttribution()` frontend function
6. Integrated attribution display into Clean Architecture response handling
7. Created comprehensive handoff documentation
