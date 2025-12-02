# Session 314: GPT-5 Responses API Migration + UI Cleanup

**Date:** December 2, 2025
**Focus:** Migrated agents to GPT-5 Responses API + Cleaned up UI badges

---

## Summary

This session completed two major tasks:
1. **GPT-5 API Migration** - Updated all connected agents to use the new `responses.create()` API instead of the deprecated `chat.completions.create()` API
2. **UI Cleanup** - Removed legacy session badges and consolidated agent stats display

---

## GPT-5 Responses API Migration

### Why This Matters

The OpenAI API changed significantly with GPT-5 models:
- New endpoint: `responses.create()` instead of `chat.completions.create()`
- New parameter structure for reasoning control
- Different response object structure

### Files Updated (5 Agents)

| File | API Calls Updated |
|------|-------------------|
| `agents/_deprecated/meeting_coordinator_agent.py` | 3 calls |
| `agents/_deprecated/coo_agent.py` | 3 calls |
| `agents/_deprecated/cto_agent.py` | 4 calls |
| `agents/content_executor.py` | 1 call |

### API Changes Reference

| Old (Chat Completions API) | New (Responses API) |
|---------------------------|---------------------|
| `client.chat.completions.create()` | `client.responses.create()` |
| `messages=[{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]` | `input="system prompt\n\nuser prompt"` |
| `max_tokens=1000` | `max_output_tokens=1000` |
| `max_completion_tokens=1000` | `max_output_tokens=1000` |
| `reasoning_effort="high"` | `reasoning={"effort": "high"}` |
| `temperature=0.7` | Not supported (remove) |
| `response_format={"type": "json_object"}` | `text={"format": {"type": "json_object"}}` |
| `response.choices[0].message.content` | `response.output_text` |

### Reasoning Effort Levels

| Level | Use Case |
|-------|----------|
| `minimal` | Fast responses, JSON extraction, simple tasks |
| `low` | Most agent tasks, standard operations |
| `medium` | Complex tasks requiring thought |
| `high` | Multi-step planning, coding, complex analysis |

### Example Migration

**Before (Old API):**
```python
response = self.client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    max_completion_tokens=4000,
    reasoning_effort="high"
)
result = response.choices[0].message.content
```

**After (New API):**
```python
full_input = f"{system_prompt}\n\n{user_prompt}"
response = self.client.responses.create(
    model="gpt-5-mini",
    input=full_input,
    reasoning={"effort": "high"},
    text={"verbosity": "medium"},
    max_output_tokens=4000
)
result = response.output_text
```

---

## UI Cleanup

### Removed Legacy Badges

| Badge | Location | Reason |
|-------|----------|--------|
| `S309` | Agent Memories card | Session reference no longer needed |
| `NEW ARCH` | Clean Agents card | All agents unified |
| `HOOKS` | Legacy + Learning card | Consolidated into single view |
| `SHARED` | Knowledge Sources card | Unnecessary label |

### Consolidated Agent Stats

**Before (4 separate cards):**
- Clean Agents (11) - NEW ARCH badge
- Legacy + Learning (14) - HOOKS badge
- Agent Memories (0) - S309 badge
- Knowledge Sources (0) - SHARED badge

**After (4 unified cards):**
- Total Agents (27) - No badge
- Learning Events (0) - No badge
- Agent Memories (0) - No badge
- Knowledge Sources (0) - No badge

### Files Modified for UI

| File | Changes |
|------|---------|
| `ai_core/templates/ai_image_studio.html` | Updated stats cards, removed badges |
| `ai_core/templates/components/panels/agents/agents_overview.html` | Updated stats cards, removed badges |
| `ai_core/templates/partials/js/agent_dashboard.html` | Updated JavaScript for new element IDs |

---

## Agent Count Fix (From Session 313)

The dashboard now correctly shows **27 connected tools** instead of 36+ database agents:

```python
# In core/services/collective_intelligence.py
'agents': {
    'total': connected_tools,        # 27 (displayed in UI)
    'connected_tools': connected_tools,
    'database_agents': total_agents,  # 36+ (for reference)
}
```

---

## Current Tool Count: 27

All 27 tools are now accessible via the Personal Assistant chat:

| # | Tool Name | Agent |
|---|-----------|-------|
| 1-12 | Core creative tools | CreationAgent, VideoAgent, etc. |
| 13-19 | Strategy tools | CompetitorAnalysis, CustomerResearch, etc. |
| 20-27 | Executive tools | CreativeDirector, CTO, COO, MeetingCoordinator, ContentExecutor, AIProjectBuilder |

---

## Testing Commands

```bash
# Verify tool count
.venv/bin/python manage.py shell -c "
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from django.contrib.auth import get_user_model
assistant = EnhancedPersonalAIAssistant(get_user_model().objects.first())
print(f'Total tools: {len(assistant.get_tool_definitions())}')
"
# Expected: Total tools: 27

# Test an agent with new API
.venv/bin/python manage.py shell -c "
from agents._deprecated.coo_agent import COOAgent
from django.contrib.auth import get_user_model
agent = COOAgent(get_user_model().objects.first())
result = agent.analyze_roadmap('AI content platform')
print(f'Status: {result.get(\"status\")}')
"
```

---

## Known Issues

### Agent Conversation Empty Messages
Some `AgentConversation` records have messages with empty `content` fields. This appears to be historical data from earlier conversation implementations. The newer conversations have proper content.

---

## Next Session (315): End-to-End UI Testing

**Focus:** Test all 27 agents through the chat UI to verify:
1. Each agent can be triggered via natural language
2. API calls use the new Responses API correctly
3. Results display properly in the UI
4. Error handling works as expected

### Test Plan

1. **Creative Agents** - Test image, video, audio, 3D generation
2. **Research Agents** - Test web search, competitor analysis, customer research
3. **Strategy Agents** - Test brand identity, content strategy, SEO, social media
4. **Executive Agents** - Test CTO, COO, Meeting Coordinator
5. **Content Agents** - Test content executor, AI project builder

---

## Files Modified in Session 314

| File | Changes |
|------|---------|
| `agents/_deprecated/meeting_coordinator_agent.py` | Migrated 3 API calls to Responses API |
| `agents/_deprecated/coo_agent.py` | Migrated 3 API calls to Responses API |
| `agents/_deprecated/cto_agent.py` | Migrated 4 API calls to Responses API |
| `agents/content_executor.py` | Migrated 1 API call to Responses API |
| `ai_core/templates/ai_image_studio.html` | Removed badges, consolidated stats |
| `ai_core/templates/components/panels/agents/agents_overview.html` | Removed badges, consolidated stats |
| `ai_core/templates/partials/js/agent_dashboard.html` | Updated JS for new element IDs |

---

## Quick Start for Session 315

```bash
# Start platform
make start && make celery

# Access AI Studio
open http://localhost:8000/ai-studio/

# Test via chat:
# "Analyze the roadmap for our AI platform" (COO Agent)
# "What are the risks in our current project?" (COO Agent)
# "Plan implementation for user authentication" (CTO Agent)
# "Start a meeting about platform scaling" (Meeting Coordinator)
```

---

**Status:** GPT-5 API migration complete. Ready for end-to-end testing.
