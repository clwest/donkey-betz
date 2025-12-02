# Session 311: Agent Conversations Fix + Dynamic Discussions

**Date:** December 1, 2025
**Focus:** Fixed empty conversation content + Added realistic debate dynamics

---

## Summary

Fixed the Agent Conversations feature which was generating empty messages, and enhanced conversation dynamics to create realistic back-and-forth discussions with disagreements, challenges, and debates.

---

## Problems Fixed

### 1. Empty Conversation Content
**Issue:** Conversations were being created but all message content was empty strings.

**Root Cause:** GPT-5-mini is a reasoning model that allocates `max_completion_tokens` between internal reasoning AND visible output. With only 150 tokens, all tokens were consumed by reasoning (150 reasoning_tokens = 150 completion_tokens), leaving 0 tokens for actual output text.

**Fix:** Increased `max_completion_tokens` from 150 to 800 for message generation, and from 100 to 400 for conclusion generation.

### 2. Overly Agreeable Conversations
**Issue:** Agents were always agreeing with each other, making conversations unrealistic.

**Root Cause:** The system prompt said "Be collaborative and constructive" which encouraged agreement.

**Fix:** Added conversation dynamics with tension levels (low/medium/high) and behavior guidelines that encourage:
- Challenging claims directly
- Pointing out flaws and risks
- Defending positions
- Asking tough questions
- Respectful but firm disagreement

---

## Code Changes

### File: `core/tasks.py`

**1. Enhanced conversation templates with tension levels:**
```python
conversation_templates = [
    {
        'type': 'knowledge_sharing',
        'tension_level': 'low',
        'dynamic': 'share expertise but question assumptions',
        ...
    },
    {
        'type': 'debate',
        'tension_level': 'high',
        'dynamic': 'strongly disagree, defend your position, find flaws',
        ...
    },
    {
        'type': 'critical_review',
        'tension_level': 'high',
        'dynamic': 'point out weaknesses, demand evidence, be skeptical',
        ...
    },
    {
        'type': 'devils_advocate',
        'tension_level': 'high',
        'dynamic': 'deliberately take opposing stance, challenge everything',
        ...
    }
]
```

**2. Dynamic system prompts based on tension level:**
- HIGH tension: "Challenge claims directly - don't just agree"
- MEDIUM tension: "Mix agreement with constructive pushback"
- LOW tension: "Share knowledge while remaining curious"

**3. Increased token limits for GPT-5 reasoning models:**
- Message generation: 150 → 800 tokens
- Conclusion generation: 100 → 400 tokens

---

## Results

### Before (Empty + Agreeable):
```
[1] ImageAgent: (EMPTY)
[2] CustomerResearchAgent: (EMPTY)
```

### After (Rich + Dynamic):
```
=== CRITICAL_REVIEW ===
[1] BookmakerAgent: You claim BookmakerAgent masters pricing, risk management...
[2] CreationAgent: You're leaning too heavily on historical correlations...
[3] BookmakerAgent: You're glossing over core operational risks...
[4] CreationAgent: You claim your bookmaking approach consistently outperforms...

=== DEBATE ===
[1] ContentExecutor: (sets position)
[2] CTOAgent: You're underestimating the operational and reputational risks...
[3] ContentExecutor: I disagree with your push to centralize content orchestration...
[4] CTOAgent: You're underestimating engineering constraints...
```

---

## GPT-5 Reasoning Model Notes

Key learnings about GPT-5-mini:
- Uses `max_completion_tokens` NOT `max_tokens`
- Does NOT support `temperature`, `top_p`, or `reasoning_effort` in chat completions
- Tokens are split between internal reasoning + visible output
- Need 500-800+ tokens minimum to ensure actual output text
- Check `response.usage.reasoning_tokens` to see token allocation

---

## Testing

```bash
# Run conversation generation
.venv/bin/python manage.py shell -c "
from core.tasks import run_agent_conversation
result = run_agent_conversation(max_conversations=3, max_messages=4)
print(result)
"

# Verify content
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentConversation, ConversationMessage
for conv in AgentConversation.objects.all():
    for msg in ConversationMessage.objects.filter(conversation=conv):
        print(f'{msg.agent.name}: {msg.content[:80]}...')
"
```

---

## Status

- Migrations: None needed (code-only changes)
- All conversations now generate with actual content
- Agents now have realistic debates and disagreements
- 6 conversation types with varying tension levels
