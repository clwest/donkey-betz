# Hive Mind Mode - Collective Intelligence

**Session 250 | November 28, 2025**

## Overview

Hive Mind Mode enables all relevant agents to work on a problem simultaneously, each contributing their unique specialty. This creates a "collective intelligence" experience where multiple AI perspectives combine to solve complex problems.

## How It Works

1. **Question Input**: User poses a complex question or task
2. **Agent Selection**: System automatically selects the most relevant agents (up to 8)
3. **Parallel Processing**: All agents think simultaneously using ThreadPoolExecutor
4. **Contribution Generation**: Each agent provides their unique perspective
5. **Synthesis**: A final synthesizer combines all contributions into a unified response

## Features

### Neural Network Visualization
- Central "brain" node represents the Hive Mind
- Agent nodes arranged in a circle around the center
- Visual status indicators:
  - **Pending** (gray): Waiting to start
  - **Thinking** (yellow, pulsing): Currently processing
  - **Completed** (green): Contribution received
  - **Failed** (red): Error occurred

### Real-Time Updates
- WebSocket connection for live status updates
- Progress bar showing completion percentage
- Contributions appear as agents complete

### Intelligent Agent Selection
Agents are selected based on:
- Keyword matching with their specializations
- Question content analysis
- Core agents always considered (Research, Trends, Content Strategy)

## API Endpoints

### Start Session
```
POST /api/hive-mind/start/
{
    "question": "Design a brand for a sustainable coffee company",
    "context": "Optional additional context",
    "max_agents": 8
}
```

### Get Session Status
```
GET /api/hive-mind/session/{session_id}/
```

### Preview Agents
```
POST /api/hive-mind/preview/
{
    "question": "Your question here",
    "max_agents": 8
}
```

### List Sessions
```
GET /api/hive-mind/sessions/?limit=10
```

## Database Models

### HiveMindSession
- `question`: The question posed to the collective
- `context`: Additional context
- `status`: initializing | gathering | synthesizing | completed | failed
- `participant_ids`: List of agent UUIDs
- `synthesis`: Final synthesized output
- `contribution_count`: Number of completed contributions
- `total_thinking_time`: Total seconds of processing

### HiveMindContribution
- `session`: Foreign key to session
- `agent`: Foreign key to agent
- `contribution`: The agent's contribution text
- `key_points`: Extracted bullet points
- `perspective_type`: analysis | creative | strategic | technical | general
- `thinking_time`: Seconds spent processing
- `status`: pending | thinking | completed | failed

## WebSocket

Connect to `/ws/hive-mind/` for real-time updates.

### Messages

**Subscribe to Session:**
```json
{
    "type": "subscribe",
    "session_id": "uuid-here"
}
```

**Contribution Update:**
```json
{
    "type": "contribution_update",
    "session_id": "...",
    "agent_name": "ResearchAgent",
    "status": "completed",
    "thinking_time": 5.2
}
```

**Session Status:**
```json
{
    "type": "session_status",
    "session_id": "...",
    "status": "completed"
}
```

## Example Session

**Question:** "How can we reduce climate change impact in urban areas?"

**Selected Agents:**
- ContentStrategyAgent (content perspective)
- ResearchAgent (analysis perspective)
- TrendAnalysisAgent (analytics perspective)

**Result:**
Each agent contributes their unique perspective:
- ContentStrategyAgent focuses on community engagement and narratives
- ResearchAgent provides data-driven smart city solutions
- TrendAnalysisAgent identifies design trends and sustainability patterns

The synthesizer combines these into a comprehensive action plan with unified recommendations.

## Files

- `core/models_unified_system.py` - HiveMindSession, HiveMindContribution models
- `core/views_hive_mind.py` - API endpoints
- `core/tasks.py` - run_hive_mind_session Celery task
- `core/hive_mind_consumer.py` - WebSocket consumer
- `core/routing.py` - WebSocket routes
- `ai_core/templates/ai_image_studio.html` - UI components

## Future Enhancements

From the SciFi Roadmap:
- **Memory Palace**: Spatial visualization of agent knowledge
- **Agent Mood System**: Emotional states affecting responses
- **Agent Rivalries**: Competitive dynamics between agents
- **Agent Evolution**: XP system for agent improvement
