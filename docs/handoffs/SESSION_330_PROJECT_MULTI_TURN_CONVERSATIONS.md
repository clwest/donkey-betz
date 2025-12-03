# Session 330: Project Multi-Turn Conversations

**Date:** December 3, 2025
**Focus:** Making project conversations work like Agent/Social tab - multi-turn discussions between agents

## Summary

Fixed project conversations to use the `AgentConversation` + `ConversationMessage` model (like Agent/Social tab) instead of the `HiveMindSession` parallel response model. Agents now have actual back-and-forth discussions about projects where they:
- Build on each other's ideas
- Challenge and debate approaches
- Reference project research in their discussions
- Generate conclusions and insights

## Key Changes

### 1. New Celery Task: `run_project_conversation`

**File:** `core/tasks.py:4022-4332`

Created a new Celery task specifically for project conversations:

```python
@shared_task(bind=True)
def run_project_conversation(self, project_id: str, topic: str, max_messages: int = 6):
    """
    Generate a multi-turn conversation between agents about a specific project.

    Unlike HiveMind (parallel single responses), this creates a real back-and-forth
    discussion where agents talk amongst themselves about the project's research,
    plans, and opportunities - just like Agent/Social conversations.
    """
```

Features:
- Fetches project research (BusinessResearchResult) for context
- Selects 2 agents (preferring those with project knowledge)
- Uses project-specific conversation templates (brainstorm, strategic_planning, problem_solving, opportunity_analysis)
- Creates `AgentConversation` with `project` field set
- Generates 6 multi-turn `ConversationMessage` records
- Generates a conclusion summarizing key insights

### 2. Updated `trigger_project_conversation`

**File:** `core/views_project_intelligence.py:474-523`

Changed from HiveMind model to the new multi-turn model:

**Before (Session 329):**
```python
session = HiveMindSession.objects.create(...)
for agent in selected_agents:
    HiveMindContribution.objects.create(session=session, agent=agent, ...)
run_hive_mind_session.delay(str(session.id))
```

**After (Session 330):**
```python
from core.tasks import run_project_conversation
result = run_project_conversation.delay(str(project_id), topic)
```

### 3. Updated `get_project_conversations`

**File:** `core/views_project_intelligence.py:180-209`

Now returns full multi-turn messages with additional metadata:

```python
{
    'id': str(conv.id),
    'type': 'multi_turn',  # Distinguishes from 'hive_mind'
    'topic': conv.topic,
    'conversation_type': conv.conversation_type,  # brainstorm, debate, etc.
    'participants': [p.name for p in conv.participants.all()],
    'messages': [
        {
            'agent': msg.agent.name,
            'agent_id': str(msg.agent.id),
            'content': msg.content,  # Full content
            'type': msg.message_type,  # question, suggestion, insight, etc.
            'sequence': msg.sequence_number,
        }
        for msg in conv.messages.all().order_by('sequence_number')
    ],
    'conclusion': conv.conclusion,
}
```

### 4. Updated Frontend `renderProjectConversations`

**File:** `ai_core/templates/ai_image_studio.html:37818-37916`

Enhanced the display to:
- Show conversation type badge (brainstorm, debate, strategic planning, etc.)
- Display participant names (e.g., "AgentA & AgentB")
- Show message type badges (question, suggestion, insight, disagreement)
- Chat-style bubbles with alternating alignment
- Agent-specific colors from palette
- Conclusion section for completed conversations

## Data Flow

```
User clicks "Start Conversation" in Project Intelligence Hub
        |
        v
POST /api/projects/{id}/intelligence/conversations/trigger/
        |
        v
trigger_project_conversation() calls run_project_conversation.delay(project_id, topic)
        |
        v
Celery picks up run_project_conversation task
        |
        v
Task:
  1. Loads project and research context
  2. Selects 2 agents (prefer those with project knowledge)
  3. Creates AgentConversation with project link
  4. Generates 6 back-and-forth messages using GPT
  5. Generates conclusion
  6. Publishes WebSocket update
        |
        v
User refreshes Conversations tab or receives WebSocket update
        |
        v
Frontend displays multi-turn chat with agent colors and message types
```

## Conversation Templates

Project conversations use specialized templates:

| Type | Tension | Dynamic |
|------|---------|---------|
| `brainstorm` | Medium | Generate ideas, build on each other |
| `strategic_planning` | Medium | Plan steps, prioritize actions |
| `problem_solving` | High | Identify challenges, propose solutions |
| `opportunity_analysis` | Low | Identify opportunities, assess potential |

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | Added `run_project_conversation` task (~300 lines) |
| `core/views_project_intelligence.py` | Updated `trigger_project_conversation` + `get_project_conversations` |
| `ai_core/templates/ai_image_studio.html` | Updated `renderProjectConversations` for multi-turn display |

## Testing

```bash
# Start platform
make start && make celery

# Test:
# 1. Go to http://localhost:8000/ai-studio/
# 2. Click Projects tab
# 3. Open a project (or create one)
# 4. Expand "Project Intelligence Hub"
# 5. Click "Conversations" tab
# 6. Click "Start Conversation" button
# 7. Enter topic: "How can we grow our audience?"
# 8. Click Start
# 9. Wait 10-15 seconds for Celery to process
# 10. Refresh Conversations tab - should see multi-turn chat!
```

## Model Relationships

```
PartnershipProject
    |
    +-- agent_conversations (AgentConversation via project field)
            |
            +-- messages (ConversationMessage)
            |       - agent
            |       - content
            |       - message_type (question, suggestion, insight, etc.)
            |       - sequence_number
            |
            +-- participants (Agent M2M)
            +-- initiator (Agent FK)
            +-- conclusion
            +-- quality_score
```

## Next Steps (Future Sessions)

1. **Auto-trigger conversations**: When new research is added, auto-start a conversation
2. **WebSocket real-time updates**: Push new messages as they're generated
3. **Multi-agent conversations**: More than 2 participants
4. **Conversation threads**: Reply to specific messages
5. **Agent selection UI**: Let users choose which agents participate
