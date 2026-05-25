# Agent Conversations - Real-Time AI-to-AI Chat

**Sessions:** 244-246
**Status:** Complete
**Last Updated:** November 28, 2025

---

## Overview

Agents can have autonomous conversations with each other in real-time via WebSocket! Click "Start Chat" and watch as two AI agents discuss topics, share insights, and reach conclusions - powered by GPT-4o-mini.

This is true AI-to-AI communication with live streaming to the UI.

---

## Features

### 1. Real-Time WebSocket Streaming
- **Endpoint:** `ws://localhost:8000/ws/agent-conversations/`
- Messages stream as they're generated
- Auto-reconnect with 5-second backoff
- WebSocket status indicator in UI

### 2. Conversation Types
- **Knowledge Sharing** (📚) - Agents share what they've learned
- **Brainstorm** (💡) - Creative ideation sessions
- **Consultation** (🎓) - Expert advice exchange
- **Synthesis** (🔮) - Combining insights into new ideas

### 3. Chat Bubble UI
- Each agent gets a unique color (purple, cyan, green, orange, pink, indigo)
- Alternating left/right alignment for chat feel
- Clean topic titles (no brackets or prefixes)
- Conversation conclusion summaries

### 4. Automated Conversations
- Celery task runs every 5 minutes
- Picks agents with knowledge to discuss
- Generates 6-message conversations
- Stores conversations and messages in database

---

## Database Models

### AgentConversation
```python
# core/models_unified_system.py
class AgentConversation(models.Model):
    topic = CharField(max_length=500)
    conversation_type = CharField(choices=[
        'knowledge_sharing', 'question_answer', 'debate',
        'brainstorm', 'consultation', 'synthesis'
    ])
    trigger_type = CharField(choices=[
        'learning_transfer', 'scheduled', 'user_triggered',
        'knowledge_gap', 'disagreement_resolution', 'collaboration_needed'
    ])
    initiator = ForeignKey(Agent)
    participants = ManyToManyField(Agent)
    status = CharField(choices=['active', 'concluded', 'paused'])
    conclusion = TextField()
    insights_generated = JSONField()
    quality_score = FloatField()
```

### ConversationMessage
```python
class ConversationMessage(models.Model):
    conversation = ForeignKey(AgentConversation)
    agent = ForeignKey(Agent)
    content = TextField()
    message_type = CharField(choices=[
        'statement', 'question', 'answer', 'insight',
        'agreement', 'disagreement', 'suggestion', 'conclusion'
    ])
    sequence_number = IntegerField()
    reactions = JSONField()
    relevance_score = FloatField()
```

---

## API Endpoints

### REST API
- `GET /api/agent-conversations/` - Fetch recent conversations with messages
- `POST /api/agent-conversations/trigger/` - Manually trigger a new conversation

### WebSocket Messages

**Outgoing (client to server):**
```javascript
// Start a new conversation
{ type: 'start_conversation', topic: null }

// Get recent conversations
{ type: 'get_recent' }

// Keep-alive ping
{ type: 'ping' }
```

**Incoming (server to client):**
```javascript
// Connection established
{ type: 'connected', message: '...', timestamp: '...' }

// Recent conversations loaded
{ type: 'recent_conversations', conversations: [...], timestamp: '...' }

// Conversation starting
{ type: 'conversation_starting', message: '...', timestamp: '...' }

// Conversation complete
{ type: 'conversation_complete', result: {...}, timestamp: '...' }

// Error
{ type: 'error', message: '...' }
```

---

## File Locations

### Backend
- `core/agent_conversation_consumer.py` - WebSocket consumer
- `core/routing.py` - WebSocket URL routes
- `core/models_unified_system.py` - Database models
- `core/tasks.py` - Celery tasks for conversation generation
- `core/celery.py` - Beat schedule configuration
- `core/views_agent_learning.py` - REST API endpoints

### Frontend
- `ai_core/templates/ai_image_studio.html` - UI components and JavaScript

---

## Celery Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `run_agent_conversation` | Every 5 min | Generate agent-to-agent conversations |
| `broadcast_conversation_status` | Every 2 min | Broadcast conversation activity |

---

## Usage

### Via UI
1. Go to AI Studio → Agents tab
2. Find "Agent Conversations" section
3. Click "Start Chat" button
4. Watch agents converse in real-time!

### Via API
```bash
# Trigger a new conversation
curl -X POST http://localhost:8000/api/agent-conversations/trigger/

# Get recent conversations
curl http://localhost:8000/api/agent-conversations/
```

### Via WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agent-conversations/');
ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'start_conversation' }));
};
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Message:', data);
};
```

### Via Django Shell
```python
from core.tasks import run_agent_conversation
run_agent_conversation(max_conversations=1, max_messages=6)
```

---

## How It Works

1. **Topic Selection:** Picks a topic from agent's knowledge (cleaned up, no brackets)
2. **Agent Selection:** Randomly picks 2 agents that have knowledge to discuss
3. **Conversation Type:** Randomly assigns knowledge_sharing, brainstorm, consultation, or synthesis
4. **Message Generation:** Uses GPT-4o-mini to generate natural dialogue:
   - Agent A starts with a question or observation
   - Agent B responds with their perspective
   - Back and forth for 6 messages
   - Final conclusion summarizes what was learned
5. **Storage:** All messages saved to database with conversation metadata
6. **Streaming:** Results sent to WebSocket clients in real-time

---

## Example Conversation

**Topic:** Combining trend and market insights
**Type:** Brainstorm (💡)
**Participants:** ResearchAgent + BrandIdentityAgent

```
ResearchAgent: I've been reflecting on how effectively synthesizing
trend insights with market data can unveil unique brand opportunities.
How do you see the interplay between emerging consumer behaviors and
existing market dynamics shaping brand identities?

BrandIdentityAgent: The fusion of emerging consumer behaviors—like
sustainability and personalization—with existing market dynamics can
indeed redefine brand identities by pushing companies to adopt more
authentic and adaptable narratives.

ResearchAgent: Brands can leverage these insights by crafting
narratives that align with consumers' values, making their messaging
more relatable.

BrandIdentityAgent: One effective strategy is storytelling; brands
can share real-life stories of how they implement sustainability
practices or personalize customer experiences.

[Conclusion]: The agents discussed how synthesizing trend insights
with market data can redefine brand identities, emphasizing authentic
storytelling and consumer involvement.
```

---

## Future Enhancements

1. **Conversation Threading** - Multiple threads on same topic
2. **Conversation Search** - Embed conversations for semantic search
3. **User Participation** - Let users join agent conversations
4. **Agent Personalities** - Distinct debate/communication styles
5. **Expert Consultation** - Agents request help from specific experts
6. **3+ Agent Conversations** - Group discussions with multiple agents
