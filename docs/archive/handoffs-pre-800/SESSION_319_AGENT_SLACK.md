# Session 319: Agent Slack - Multi-Agent Channel Communication

**Date:** December 2, 2025
**Previous Session:** 318 - Agent Conversations Comprehensive Fix
**Branch:** `feature/session-52-ai-assistant`

---

## Summary

Built an internal **Slack-like communication system** for agents within the platform. Agents can now:
- Join topic-based channels
- Collaborate on projects through group discussions
- Use @mentions to invite specific agents to respond
- Share knowledge contextually in conversations
- Have threaded discussions

---

## What Was Built

### 1. Database Models (`core/models_unified_system.py`)

Three new models for the Agent Slack system:

| Model | Purpose |
|-------|---------|
| `AgentChannel` | Slack-like channels (name, description, type, members, topic) |
| `ChannelMembership` | Tracks which agents are in which channels (role, presence, activity) |
| `ChannelMessage` | Messages in channels (content, reactions, threading, mentions) |

**Channel Types:**
- `project` - Linked to a specific project
- `topic` - General topic discussion
- `workflow` - Workflow coordination
- `team` - Team of agents
- `announcement` - Read-only announcements
- `emergency` - High-priority issues

**Message Features:**
- Threading (reply_count, thread_parent)
- @mentions (ManyToManyField to mentioned agents)
- Reactions (JSON field with emoji: [agent_ids])
- Attachments support
- Pinning

### 2. WebSocket Consumer (`core/agent_slack_consumer.py`)

Real-time WebSocket consumer for Agent Slack:

**Client Commands:**
- `message` - Send a message to the channel
- `join_channel` - Switch to a different channel
- `get_channels` - Get list of available channels
- `get_members` - Get channel members
- `get_history` - Get message history
- `create_channel` - Create a new channel
- `add_reaction` - Add reaction to a message
- `ping` - Keep-alive

**Server Events:**
- `channel_info` - Channel metadata + recent messages
- `channel_list` - List of all channels
- `member_list` - Channel members with presence
- `new_message` - New message posted
- `typing` - Typing indicator
- `channel_created` - New channel created

**Key Feature: @mention Agent Responses**
When a user types `@BrandIdentityAgent what do you think?`:
1. Message is saved and broadcast
2. Parser extracts mentioned agents
3. Each mentioned agent:
   - Shows typing indicator
   - Fetches their learned knowledge
   - Generates contextual response using GPT-5-mini
   - Posts response to channel

### 3. Channel Orchestrator (`core/channel_orchestrator.py`)

Orchestrates multi-agent collaboration in channels:

**Features:**
- `select_responding_agents()` - Intelligently select which agents should respond
- `generate_channel_response()` - Knowledge-aware response generation
- `orchestrate_discussion()` - Full multi-agent discussion on a topic
- `generate_thread_summary()` - Summarize thread discussions
- `suggest_agents_for_channel()` - Recommend agents for a channel based on purpose

### 4. Routing (`core/routing.py`)

New WebSocket endpoints:
```python
re_path(r'^ws/agent-slack/$', AgentSlackConsumer.as_asgi()),
re_path(r'^ws/agent-slack/(?P<channel_id>[^/]+)/$', AgentSlackConsumer.as_asgi()),
re_path(r'^ws/agent-workspace/$', AgentSlackConsumer.as_asgi()),
```

### 5. UI Component (`ai_core/templates/components/panels/agents/agents_slack.html`)

Slack-like UI with:
- Channel sidebar (list of channels)
- Online agents panel
- Message area with chat history
- Typing indicators
- @mention highlighting
- Message input with hint
- Create channel modal

**Added to:** `agents_social.html` (Social sub-tab)

---

## Default Channels Created

| Channel | Description |
|---------|-------------|
| `#general` | General discussion for all agents |
| `#content-strategy` | Content strategy discussions and planning |

---

## How to Test

```bash
# Start the platform
make start && make celery

# Navigate to AI Studio > Agents > Social tab
# The Agent Workspace should appear at the top

# Or connect directly via WebSocket:
websocat ws://localhost:8000/ws/agent-slack/general/

# Send a message
{"type": "message", "content": "@BrandIdentityAgent what's your take on our brand strategy?", "sender_type": "user", "sender_name": "User"}

# The agent will respond with knowledge-aware content
```

---

## Files Created/Modified

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added AgentChannel, ChannelMembership, ChannelMessage models |
| `core/agent_slack_consumer.py` | **NEW** - WebSocket consumer for Agent Slack |
| `core/channel_orchestrator.py` | **NEW** - Multi-agent channel orchestration |
| `core/routing.py` | Added agent-slack WebSocket routes |
| `ai_core/templates/components/panels/agents/agents_slack.html` | **NEW** - Slack-like UI component |
| `ai_core/templates/components/panels/agents/agents_social.html` | Added include for agents_slack.html |
| `core/migrations/0061_session_319_agent_slack_channels.py` | Database migration |

---

## Architecture

```
User/Agent                  WebSocket                    Backend
    |                           |                           |
    |-- message {"@Agent"} ---->|                           |
    |                           |-- save_message() -------->|
    |                           |<-- broadcast msg ---------|
    |<-- new_message -----------|                           |
    |                           |                           |
    |                           |-- trigger_agent_response--|
    |                           |   1. Show typing          |
    |<-- typing indicator ------|   2. Get agent knowledge  |
    |                           |   3. Generate response    |
    |                           |<-- save + broadcast ------|
    |<-- new_message (agent) ---|                           |
```

---

## Integration Points

### With Existing Systems:
- **Agent Knowledge** - Agents use their AgentKnowledgeSource and AgentMemory for responses
- **Agent Model** - Uses existing Agent model for membership
- **Conversation Orchestrator** - Similar knowledge injection pattern

### Future Integration Opportunities:
- Link to Projects (project_id field exists)
- Auto-create channels for workflows
- Celery task for scheduled agent discussions
- Integration with Hive Mind Mode for collective intelligence

---

## GPT-5 Token Reference

Agent Slack uses moderate tokens since responses are short:

| Use Case | Tokens |
|----------|--------|
| Channel message response | 500 |
| Thread summary | 200 |
| Agent selection | 200 |

---

## Next Steps (Session 320+)

1. **Connect to Projects** - Auto-create channels when projects are created
2. **Scheduled Discussions** - Celery task for agents to have morning standup
3. **Channel Analytics** - Track engagement, most active agents
4. **Search** - Search across channel messages
5. **File Sharing** - Attach images, documents to messages
6. **Voice/Video** - Agent "voice notes" using audio generation

---

**Status:** Agent Slack fully implemented with:
- 3 database models
- WebSocket consumer with @mention agent responses
- Channel orchestrator for multi-agent coordination
- Slack-like UI in Social tab
- 2 default channels (#general, #content-strategy)
