# Session 360: Multi-Agent Conversations

**Date:** December 5, 2025
**Status:** COMPLETE - Panel-style conversations with 3-5 agents now supported

---

## Summary

Extended the agent conversation system to support multi-agent panel discussions. Previously, conversations were limited to 2 agents (initiator + responder). Now, 3-5 agents can participate in round-robin discussions, creating richer insights through diverse perspectives.

---

## Problem

Session 359 conversations were limited to 2 agents:
- Initiator poses a topic
- Responder replies with their perspective
- Back-and-forth dialogue but only 2 viewpoints

This missed the opportunity for:
- Multiple expert perspectives on a single topic
- Cross-disciplinary insights
- More dynamic discussions with challenges and synthesis

---

## Solution

### New Task: `run_multi_agent_conversation()`

**Location:** `core/tasks.py` (lines 4059-4479)

**Parameters:**
- `max_conversations: int = 2` - Maximum new panels to start
- `participants_per_conversation: int = 4` - Agents per panel (3-5 recommended)
- `max_rounds: int = 3` - Complete rounds (each agent speaks once per round)

### Panel Discussion Templates

5 distinct panel styles with different dynamics:

| Template | Tension | Dynamic |
|----------|---------|---------|
| `roundtable` | Medium | Experts share perspectives, building on others |
| `expert_panel` | Low | Each expert presents from their specialty |
| `brainstorm_session` | Low | Creative idea generation and elaboration |
| `debate_panel` | High | Structured arguments and counterarguments |
| `strategy_session` | Medium | Action-oriented planning and decision-making |

### Tension Levels

Tension affects prompt selection:
- **Low tension:** `respond` prompts - "Building on what {prev_agent} said..."
- **Medium tension:** Mix of `respond` and `challenge`
- **High tension:** `challenge` prompts - "I disagree with {prev_agent}..."
- **Synthesis:** Always uses `synthesize` prompts on final rounds

### Agent Selection

Agents are selected to maximize diversity:
1. Pull agents with knowledge (up to 30)
2. Group by specialization category
3. Select from different specializations when possible
4. Ensures panels have varied perspectives

### Mythology Validation

All outputs go through `validate_agent_output()`:
- Line 4323: Individual messages validated
- Line 4398: Panel conclusions validated

---

## Code Structure

```python
@shared_task(bind=True, max_retries=2)
def run_multi_agent_conversation(self, max_conversations: int = 2,
                                  participants_per_conversation: int = 4,
                                  max_rounds: int = 3):
    """
    Session 360: Generate panel-style conversations with 3-5 agents.
    """

    # 1. Get agents with knowledge
    agents_with_knowledge = Agent.objects.filter(
        is_active=True,
        knowledge_sources__isnull=False
    ).distinct()[:30]

    # 2. Panel templates (5 styles)
    panel_templates = [
        {'type': 'roundtable', 'tension_level': 'medium', ...},
        {'type': 'expert_panel', 'tension_level': 'low', ...},
        # ... more templates
    ]

    # 3. Diverse agent selection by specialization
    for conv_num in range(max_conversations):
        # Select agents from different specialization categories
        panel_agents = select_diverse_agents(...)

        # Create AgentConversation
        conversation = AgentConversation.objects.create(
            conversation_type='multi_agent_panel',
            topic=topic,
            panel_type=template['type'],
            participants=[...],  # All agent IDs
            initiator=panel_agents[0]
        )

        # 4. Round-robin message generation
        for round_num in range(max_rounds):
            for agent_idx, current_agent in enumerate(panel_agents):
                # Select prompt based on tension
                prompt = get_prompt_for_tension(tension, is_final_round)

                # Generate with LLM
                content = openai_chat_completion(...)

                # Mythology validation (Session 359)
                content = validate_agent_output(current_agent.name, content)

                # Save message
                ConversationMessage.objects.create(...)

        # 5. Generate panel conclusion
        conclusion = generate_synthesis(all_messages)
        conclusion = validate_agent_output("MultiAgentSynthesizer", conclusion)

        # 6. Extract decisions for living projects
        try_extract_decisions(conclusion)
```

---

## Integration Points

### Decision Extraction
Panel conclusions are processed by `extract_decisions_from_conclusion()` for living projects integration.

### Redis Broadcasting
Completion stats are broadcast via Redis pub/sub:
```python
r.publish('agent_learning', json.dumps({
    'type': 'multi_agent_conversation_complete',
    'stats': {...}
}))
```

### Existing 2-Agent Conversations
The original `run_agent_conversation()` function is unchanged. Both systems can run in parallel.

---

## Files Changed

| File | Changes |
|------|---------|
| `core/tasks.py` | Added `run_multi_agent_conversation()` (~420 lines) |

---

## Benefits

1. **Richer Insights**: Multiple perspectives on each topic
2. **Cross-Disciplinary**: Agents from different specializations collaborate
3. **Dynamic Tension**: Templates provide variety in discussion style
4. **Synthesis**: Every panel produces a unified conclusion
5. **Mythology-Safe**: All outputs validated

---

## Usage

```python
# Run a multi-agent panel (3 conversations, 4 agents each, 3 rounds)
from core.tasks import run_multi_agent_conversation
run_multi_agent_conversation.delay(
    max_conversations=3,
    participants_per_conversation=4,
    max_rounds=3
)
```

---

## Example Output

```json
{
  "status": "success",
  "stats": {
    "conversations_started": 2,
    "messages_generated": 24,
    "insights_discovered": 6,
    "agents_participated": ["ResearchAgent", "TrendAnalysisAgent", "ContentStrategyAgent", "SEOOptimizerAgent"],
    "avg_participants": 4.0
  }
}
```

---

## Related Sessions

- **Session 359:** Mythology Validation Expansion
- **Session 358:** Enhanced Delta Detection
- **Session 244-246:** Original Agent Conversations (2-agent)
- **Session 248-250:** Hive Mind Mode

---

## Next Steps (Session 361)

1. **Add to Celery Beat** - Schedule multi-agent panels periodically
2. **UI Display** - Show multi-agent panels differently in the Agents tab
3. **Panel Analytics** - Track which panel types generate best insights
4. **Cross-Panel Learning** - Insights from one panel inform others
