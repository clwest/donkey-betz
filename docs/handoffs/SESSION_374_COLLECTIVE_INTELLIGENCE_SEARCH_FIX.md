# Session 374: Collective Intelligence Search Fix

## Summary
Fixed and enhanced the Collective Intelligence Search feature in the Memory -> Collaboration tab. The search was returning very few results because it only searched SharedKnowledge and CollaborationSession. Now it also searches AgentConversation, AgentDream, and AgentMemory.

## Problem
User reported "Collective Intelligence Search isn't working". Investigation revealed:
1. The search only looked in SharedKnowledge (title, tags, description) and CollaborationSession (task_description)
2. These tables had limited searchable content
3. 1,500+ agent conversations and 1,500+ dreams were not being searched

## Solution
Enhanced `aggregate_insights()` in `core/services/collective_intelligence.py` to search across 5 data sources:
1. **SharedKnowledge** - Best practices and learned knowledge
2. **CollaborationSession** - Multi-agent task results
3. **AgentConversation** - Agent-to-agent discussions
4. **AgentDream** - Creative ideation and "what if" scenarios
5. **AgentMemory** - Stored insights and experiences

## Files Modified

### Backend
- `core/services/collective_intelligence.py`
  - Extended imports to include `AgentConversation`, `AgentDream`, `AgentMemory`
  - Added conversation search (topic, conclusion fields)
  - Added dream search (content, title, related_topics fields)
  - Added memory search (content, title, context fields)
  - Fixed field name: `created_at` -> `dreamed_at` for AgentDream ordering

### Frontend
- `ai_core/templates/ai_image_studio.html`
  - Updated placeholder text to reflect enhanced search
  - Added insight type badges (Knowledge, Conversation, Dream, Memory, Collaboration)
  - Increased result display from 10 to 15 items
  - Color-coded badges for visual differentiation

## Results

### Before
- Search for "design" returned 2 results
- Search for "creative" returned minimal results
- Only SharedKnowledge and CollaborationSession data

### After
- Search for "creative" returns 36 insights from 15 agents
- Includes conversations, dreams, memories
- Color-coded badges show insight source type

## Bug Fixes
- Fixed `created_at` field error for AgentDream model (should be `dreamed_at`)
- Fixed field name issues for AgentConversation (uses FKs not string fields)
- Fixed field name issues for AgentMemory (uses FKs not string fields)

## Testing
```bash
# Clear cache and test search
redis-cli FLUSHALL

# Test the enhanced search
curl -s "http://localhost:8000/api/collective/insights/?topic=creative" | python3 -m json.tool

# Expected: 30+ insights with various types (knowledge, conversation, dream, memory)
```

## UI Changes
The search results now show:
- Agent name
- Insight type badge (color-coded):
  - Green: Knowledge
  - Blue: Conversation
  - Pink: Dream
  - Orange: Memory
  - Purple: Collaboration
- Confidence score
- Content preview (200 chars)

## Insight Types Available
| Type | Source | Color |
|------|--------|-------|
| knowledge | SharedKnowledge | Green |
| conversation | AgentConversation | Blue |
| dream | AgentDream | Pink |
| memory | AgentMemory | Orange |
| collaboration_result | CollaborationSession | Purple |
