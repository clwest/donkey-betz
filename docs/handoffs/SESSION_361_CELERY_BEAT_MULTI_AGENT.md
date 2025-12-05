# Session 361: Celery Beat Integration for Multi-Agent Panels

**Date:** December 5, 2025
**Status:** COMPLETE - Multi-agent panel discussions now run automatically via Celery Beat

---

## Summary

Added the `run_multi_agent_conversation()` task to Celery Beat so panel discussions run automatically every 20 minutes. This completes the multi-agent conversation feature from Session 360.

---

## Problem

Session 360 created the `run_multi_agent_conversation()` task, but it had to be triggered manually. For the system to benefit from ongoing multi-agent panel discussions, they need to run automatically alongside other learning cycles.

---

## Solution

### Celery Beat Schedule Entry

**Location:** `core/celery.py` (added to `CELERY_BEAT_SCHEDULE`)

```python
# Session 360/361: Multi-Agent Panel Conversations
# Panel discussions with 3-5 agents for richer insights
'multi-agent-panel-cycle': {
    'task': 'core.tasks.run_multi_agent_conversation',
    'schedule': crontab(minute='*/20'),  # Every 20 minutes - panels take longer
    'options': {
        'expires': 1200,  # 20 minutes
    },
    'kwargs': {
        'max_conversations': 1,  # 1 panel per cycle
        'participants_per_conversation': 4,  # 4 agents per panel
        'max_rounds': 3,  # 3 discussion rounds
    }
},
```

### Why 20 Minutes?

- Multi-agent panels are more resource-intensive than 2-agent conversations
- Each panel involves:
  - Agent selection and diversity checks
  - 3-5 LLM calls per round (one per agent)
  - 3 rounds = 9-15 LLM calls per panel
  - Synthesis and decision extraction
- Regular 2-agent conversations run every 5 minutes
- 20 minutes provides balanced coverage without overloading the system

---

## Testing

### Manual Test Run

```python
from core.tasks import run_multi_agent_conversation
result = run_multi_agent_conversation(max_conversations=1, participants_per_conversation=3, max_rounds=2)
# Result: {'status': 'success', 'stats': {...}}
```

### Verified Output

```json
{
  "status": "success",
  "stats": {
    "conversations_started": 1,
    "messages_generated": 2,
    "insights_discovered": 0,
    "agents_participated": ["ImageAgent", "ResearchAgent", "ContentStrategyAgent"],
    "avg_participants": 3.0
  }
}
```

### Sample Panel Conversation

- **Type:** `brainstorm_session`
- **Topic:** "Panel: [Learned] Guru - Freelance Intelligence"
- **Participants:** ContentStrategyAgent, ImageAgent
- **Messages:** Agents building on each other's ideas about product strategy

---

## Files Changed

| File | Changes |
|------|---------|
| `core/celery.py` | Added `multi-agent-panel-cycle` to `CELERY_BEAT_SCHEDULE` |
| `ai_core/templates/ai_image_studio.html` | Added panel UI differentiation (icons, badge, styling) |
| `ai_core/templates/partials/js/agent_dashboard.html` | Added panel UI differentiation (icons, badge, styling) |

---

## Complete Celery Beat Schedule (Agent Learning)

After Session 361, the agent learning schedule includes:

| Task | Frequency | Purpose |
|------|-----------|---------|
| `agent-learning-cycle` | Every 5 min | Knowledge propagation |
| `agent-conversation-cycle` | Every 5 min | 2-agent discussions |
| `multi-agent-panel-cycle` | Every 20 min | 3-5 agent panel discussions |
| `agent-dream-cycle` | Every 15 min | Creative thinking |
| `agent-mood-check` | Every 10 min | Emotional state updates |
| `agent-relationship-evolution` | Every 10 min | Alliance/rivalry updates |
| `broadcast-learning-status` | Every 3 min | WebSocket broadcasts |
| `broadcast-conversation-status` | Every 3 min | WebSocket broadcasts |

---

## Benefits

1. **Automated Rich Discussions**: Multi-agent panels run continuously without manual intervention
2. **Diverse Perspectives**: Each panel brings together agents from different specializations
3. **Living Projects Integration**: Panel insights feed into living projects automatically
4. **Balanced Load**: 20-minute interval prevents system overload while maintaining regular activity

---

## Architecture

```
Celery Beat Scheduler
    |
    +-- Every 5 min: run_agent_conversation (2 agents)
    |
    +-- Every 20 min: run_multi_agent_conversation (3-5 agents)  <-- NEW
    |
    +-- Every 15 min: generate_agent_dreams
    |
    +-- Every 10 min: check_mood_expirations, evolve_agent_relationships
```

---

## Related Sessions

- **Session 360:** Multi-Agent Conversations - Created `run_multi_agent_conversation()` task
- **Session 359:** Mythology Validation Expansion
- **Session 244-246:** Original Agent Conversations (2-agent)

---

## Next Steps (Session 362)

1. **UI Display** - Show multi-agent panels differently in Agents tab
2. **Panel Analytics** - Track which panel types generate best insights
3. **Cross-Panel Learning** - Insights from one panel inform others
