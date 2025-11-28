# Memory Palace - Agent Memory Visualization

**Session 251 | November 28, 2025**

## Overview

Memory Palace provides persistent memory storage for agents, allowing them to remember past experiences, learn from successes and failures, and build connections between related memories. The visual "palace" metaphor organizes memories into themed rooms.

## How It Works

1. **Memory Recording**: Agents record memories from interactions, successes, failures, insights, and preferences
2. **Embedding Generation**: Each memory gets a semantic embedding via OpenAI for similarity search
3. **Automatic Organization**: Memories are organized into themed "rooms" based on type
4. **Memory Retrieval**: Agents can search and retrieve relevant memories using semantic similarity
5. **Prompt Integration**: Memory summaries can be injected into agent prompts for context

## Memory Types

| Type | Emoji | Description |
|------|-------|-------------|
| success | ✅ | Things the agent did well |
| failure | ❌ | Things that didn't work |
| technique | ⚙️ | Learned methods and approaches |
| insight | 💡 | Realizations and discoveries |
| preference | ❤️ | User preferences and styles |
| interaction | 💬 | General conversation memories |
| feedback | 📝 | User feedback and corrections |

## Memory Palace Rooms

Default rooms created for each agent:

| Room | Icon | Contains |
|------|------|----------|
| Techniques | ⚙️ | Learned methods |
| Successes | 🏆 | Wins and achievements |
| Lessons | 📚 | Failures and lessons learned |
| Preferences | ❤️ | User preferences |
| Insights | 💡 | Discoveries and realizations |

## API Endpoints

### Overview
```
GET /api/memory-palace/
```
Returns overview of all agents' memories with type breakdown.

### Agent Memories
```
GET /api/memory-palace/agent/{agent_id}/memories/?type=&valence=&limit=50
```
Get memories for a specific agent with optional filters.

### Agent Rooms
```
GET /api/memory-palace/agent/{agent_id}/rooms/
```
Get all memory palace rooms for an agent (creates defaults if none exist).

### Memory Summary
```
GET /api/memory-palace/agent/{agent_id}/summary/?limit=10
```
Get a prompt-friendly summary of agent's top memories.

### Memory Detail
```
GET /api/memory-palace/memory/{memory_id}/
```
Get full details of a memory including connected memories.

### Room Memories
```
GET /api/memory-palace/room/{room_id}/memories/
```
Get all memories in a specific room.

### Create Memory
```
POST /api/memory-palace/create/
{
    "agent_id": "uuid",
    "title": "Memory Title",
    "content": "Memory content...",
    "memory_type": "insight",  // success, failure, technique, insight, preference, interaction, feedback
    "valence": "positive",     // positive, negative, neutral
    "importance": 0.5,         // 0.0 to 1.0
    "context": "",             // Optional context
    "source_type": "",         // Optional source type
    "source_id": ""            // Optional source ID
}
```

### Search Memories
```
POST /api/memory-palace/search/
{
    "agent_id": "uuid",
    "query": "search query",
    "memory_types": ["insight", "technique"],  // Optional filter
    "limit": 5
}
```

### Connect Memories
```
POST /api/memory-palace/connect/
{
    "source_id": "uuid",
    "target_id": "uuid",
    "connection_type": "similar",  // causal, similar, contrast, elaborates, temporal
    "strength": 0.5                // 0.0 to 1.0
}
```

### Assign to Room
```
POST /api/memory-palace/assign/
{
    "memory_id": "uuid",
    "room_id": "uuid"
}
```

### Delete Memory
```
DELETE /api/memory-palace/memory/{memory_id}/delete/
```

## Database Models

### AgentMemory
- `id`: UUID primary key
- `agent`: Foreign key to Agent
- `title`: Short title (200 chars)
- `content`: Full memory content
- `context`: Additional context
- `memory_type`: Type (success, failure, etc.)
- `valence`: Emotional tone (positive, negative, neutral)
- `importance_score`: 0.0 to 1.0
- `embedding`: JSON field for semantic vector
- `connected_memories`: M2M to other memories
- `source_type`: Where memory came from
- `source_id`: ID of source
- `access_count`: Times accessed
- `last_accessed_at`: Last access time

### MemoryConnection
- `source_memory`: Source memory FK
- `target_memory`: Target memory FK
- `connection_type`: Type of connection
- `strength`: Connection strength 0.0-1.0

### MemoryPalaceRoom
- `agent`: Foreign key to Agent
- `name`: Room name
- `room_type`: Room type (techniques, successes, lessons, etc.)
- `description`: Room description
- `color`: Emoji or icon
- `icon`: Display icon
- `display_order`: Sort order
- `memories`: M2M to AgentMemory

## Celery Tasks

### generate_memory_embedding
Generates semantic embedding for a memory using OpenAI's text-embedding-3-small.

### auto_connect_memories
Automatically finds and connects similar memories using embedding similarity.

### record_agent_memory
Convenience task to record a memory asynchronously from anywhere in the codebase.

### organize_memories_into_rooms
Automatically organizes memories into appropriate rooms based on type.

## UI Features

- **Agent Selector**: Dropdown to select an agent to explore
- **Room Cards**: Visual cards showing each room with memory count
- **Memory Cards**: Clickable cards showing memory title, type, valence, and importance
- **Memory Detail Modal**: Full view of memory with content, context, and connections
- **Semantic Search**: Search memories by meaning, not just keywords
- **Create Memory Form**: Manually add memories with type and valence selection

## Files

- `core/models_unified_system.py` - AgentMemory, MemoryConnection, MemoryPalaceRoom models
- `core/views_memory_palace.py` - API endpoints
- `core/tasks.py` - Celery tasks for embedding and organization
- `core/migrations/0041_session_251_memory_palace.py` - Migration
- `ai_core/templates/ai_image_studio.html` - UI components

## Future Enhancements

From the SciFi Roadmap:
- **Agent Mood System**: Memories could influence agent mood
- **Agent Rivalries**: Competitive memory about other agents
- **Agent Evolution**: XP system using success memories
- **Memory Visualization**: 3D spatial palace navigation
