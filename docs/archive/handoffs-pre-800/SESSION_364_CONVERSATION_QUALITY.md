# Session 364: Conversation Quality and Multi-Agent Panel Fixes

**Date:** December 5, 2025
**Focus:** Fix conversation quality issues and multi-agent panel reliability
**Status:** COMPLETE - All fixes implemented and tested

---

## Summary

Session 364 addressed three critical issues with the autonomous agent conversation system:

1. **Initiator Self-Response Bug** - Agents were responding to themselves
2. **Repetitive Responses** - All agents making the same points ("11 data points is too small")
3. **Multi-Agent Panels Empty** - Panel conversations generating 0 messages

---

## Problems & Solutions

### 1. Initiator Self-Response Bug

**Problem:** When the responder returned an empty message, the code would:
1. Swap speakers on empty content
2. Swap again at end of loop iteration

This meant the initiator (e.g., PromptEngineeringAgent) would start the conversation, then when responder failed, initiator would critique their own opening statement.

**Solution:** Changed the empty-content handler to:
- Only swap once (to let the other agent retry)
- Added `consecutive_empty` counter to break if both fail
- Clear counter on successful message

```python
# Session 364: DON'T swap on empty - let next iteration try other speaker
if not content:
    logger.warning(f"Empty content from {current_speaker.name}")
    consecutive_empty += 1
    if consecutive_empty >= 2:
        logger.warning(f"Both agents returned empty, ending conversation early")
        break
    current_speaker, other_speaker = other_speaker, current_speaker
    continue

# Reset on success
consecutive_empty = 0
```

### 2. Repetitive Responses

**Problem:** All agents in a conversation would make essentially the same points because they all saw the same knowledge context and had no guidance to differentiate.

**Solution:** Added diversity prompts that rotate by message number:

```python
diversity_prompts = [
    "Focus on OPPORTUNITIES in this data - what could we build or do with it?",
    "Focus on RISKS and what could go wrong - play devil's advocate.",
    "Focus on NEXT STEPS - what concrete actions should we take?",
    "Focus on WHO benefits from this and HOW - the user perspective.",
    "Focus on TECHNICAL implementation - how would this actually work?",
    "Focus on MARKET implications - what trends or competitive insights are here?",
]
diversity_hint = diversity_prompts[msg_num % len(diversity_prompts)]
```

### 3. Multi-Agent Panels Producing Empty Messages

**Problem:** `run_multi_agent_conversation` would start conversations but generate 0 messages. The GPT model was intermittently returning empty strings.

**Root Causes:**
- `max_completion_tokens=500` was too low for reasoning models (gpt-5-mini)
- No retry logic for empty responses

**Solution:**
1. Increased `max_completion_tokens` from 500 to 2000
2. Added retry loop (2 attempts) for empty responses
3. Added 8 diversity prompts for panel discussions

```python
# Session 364: Retry up to 2 times if empty response
content = ""
for retry in range(2):
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[...],
        max_completion_tokens=2000,  # Increased from 500
    )
    content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

    if content:
        break
    logger.warning(f"Empty response from {current_agent.name}, retry {retry + 1}/2")
```

---

## Test Results

### Before Fixes
```
Multi-agent panels: 0 messages generated
2-agent conversations: Agents responding to themselves, repetitive content
```

### After Fixes
```python
Result: {
    'status': 'success',
    'stats': {
        'conversations_started': 2,
        'messages_generated': 24,  # Was 0!
        'agents_participated': ['ImageAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent', 'ResearchAgent'],
        'avg_participants': 4.0
    }
}
```

Panel conversations now have 12 messages each with diverse perspectives.

---

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | Fixed speaker swap logic, added diversity prompts, increased tokens, added retry |

---

## Commit

```
626ba3a - fix(Session 364): Improve conversation quality and multi-agent panel reliability
```

---

## Next Session Suggestions

### Option A: More Mood Diversity
- 23/24 agents are "calm" - add variety
- Implement mood-influenced conversation styles

### Option B: Conversation Quality Metrics
- Track conversation quality scores
- Measure topic drift
- Alert on low-quality outputs

### Option C: Agent Relationship Effects
- Use rivalries/alliances to influence tone
- More competitive dynamics in debates

---

## Quick Test

```bash
# Test multi-agent panels
.venv/bin/python manage.py shell -c "
from core.tasks import run_multi_agent_conversation
result = run_multi_agent_conversation()
print(result)
"

# Check recent conversations
.venv/bin/python manage.py shell -c "
from core.models import AgentConversation
recent = AgentConversation.objects.order_by('-started_at')[:3]
for c in recent:
    print(f'{c.topic[:40]}... - {c.messages.count()} messages')
"
```
