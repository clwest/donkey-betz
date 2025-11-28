# Agent Mood System - Emotional States for Agents

**Session 252 | November 28, 2025**

## Overview

The Agent Mood System gives agents emotional states that influence their creativity, precision, and communication style. Moods can be triggered by memories, task outcomes, user feedback, or time-based rules.

## How It Works

1. **Mood State**: Each agent has a current mood (inspired, focused, calm, etc.)
2. **Mood Dimensions**: Moods affect creativity, precision, sociability, and risk tolerance
3. **Triggers**: Moods can be triggered manually, by memories, by task outcomes, or by rules
4. **Expiration**: Moods have optional expiration times, after which they reset to "calm"
5. **History**: All mood changes are tracked for analytics

## Mood Types

| Mood | Emoji | Description | Creativity | Precision |
|------|-------|-------------|------------|-----------|
| inspired | ✨ | High creativity, bold suggestions | 90% | 50% |
| focused | 🎯 | High precision, methodical | 40% | 95% |
| curious | 🤔 | Exploratory, asks questions | 70% | 60% |
| confident | 💪 | Assertive, strong opinions | 60% | 70% |
| contemplative | 🧘 | Thoughtful, philosophical | 60% | 70% |
| energetic | ⚡ | Fast-paced, enthusiastic | 70% | 50% |
| calm | 😌 | Balanced, measured (default) | 50% | 60% |
| frustrated | 😤 | Needs help, struggling | 30% | 40% |
| tired | 😴 | Low energy, brief responses | 30% | 40% |
| playful | 😄 | Humorous, creative risks | 85% | 40% |

## Mood Dimensions

Each mood affects four behavioral dimensions (0.0 - 1.0):

- **Creativity Level**: How experimental and creative the agent is
- **Precision Level**: How methodical and accurate the agent is
- **Sociability Level**: How verbose and chatty the agent is
- **Risk Tolerance**: How willing the agent is to try new approaches

## API Endpoints

### Overview
```
GET /api/agent-mood/
```
Returns overview of all agents' moods with distribution statistics.

### Agent Mood Detail
```
GET /api/agent-mood/agent/{agent_id}/
```
Get detailed mood for a specific agent including history.

### Set Mood
```
POST /api/agent-mood/agent/{agent_id}/set/
{
    "mood": "inspired",
    "intensity": 0.8,
    "duration_minutes": 60,
    "reason": "Creative session started"
}
```

### Mood History
```
GET /api/agent-mood/agent/{agent_id}/history/?limit=50
```
Get mood change history for an agent.

### Prompt Context
```
GET /api/agent-mood/agent/{agent_id}/prompt-context/
```
Get mood-aware prompt context to inject into agent prompts.

### Mood Rules
```
GET /api/agent-mood/rules/
POST /api/agent-mood/rules/create/
DELETE /api/agent-mood/rules/{rule_id}/delete/
```
Manage automatic mood trigger rules.

### Memory-Triggered Mood
```
POST /api/agent-mood/trigger-from-memory/
{
    "agent_id": "uuid",
    "memory_id": "uuid"
}
```
Trigger a mood change based on a memory being recalled.

## Database Models

### AgentMood
- `agent`: OneToOne to Agent
- `current_mood`: Current mood state
- `intensity`: 0.0 to 1.0
- `creativity_level`, `precision_level`, `sociability_level`, `risk_tolerance`: 0.0-1.0
- `trigger_type`: What triggered the mood (memory, task_success, manual, etc.)
- `trigger_source`: Details about the trigger
- `mood_started_at`, `mood_expires_at`: Duration tracking
- `total_mood_changes`: Counter for analytics

### MoodHistory
- `agent`: FK to Agent
- `mood`, `intensity`: Snapshot of mood
- `trigger_type`, `trigger_source`: What triggered it
- `duration_minutes`: How long the mood lasted
- `created_at`: When the mood started

### MoodTriggerRule
- `agent`: Optional FK (null = global rule)
- `name`, `description`: Rule details
- `condition_type`: Type of trigger (task_success_streak, idle_time, time_of_day, etc.)
- `condition_value`: JSON parameters for the condition
- `target_mood`, `target_intensity`: What mood to set
- `duration_minutes`: How long the mood lasts
- `priority`: Rule priority (higher = checked first)

## Celery Tasks

### update_agent_mood
Updates an agent's mood from any system event.

### check_mood_expirations
Runs every 5 minutes to reset expired moods to "calm".

### apply_mood_trigger_rules
Runs every 10 minutes to check and apply mood trigger rules.

## Prompt Integration

Use `get_mood_prompt_context` to get a mood-aware prompt modifier:

```python
# Example prompt modifier for "inspired" mood:
"""
## Current Emotional State
**Mood:** Inspired ✨
**Intensity:** 80%

### Behavioral Guidelines
You're feeling particularly inspired and creative right now.
Don't hold back on bold, imaginative ideas.

### Dimensional Profile
- Creativity: 72%
- Precision: 40%
- Sociability: 56%
- Risk Tolerance: 64%
"""
```

## Memory-Mood Connection

When a memory is recalled (via `trigger_mood_from_memory`), the mood is set based on:

- **Memory Type**: success, failure, insight, etc.
- **Memory Valence**: positive, negative, neutral
- **Memory Importance**: Higher importance = stronger mood effect

Example mappings:
- Success + Positive → Confident (80%)
- Insight + Positive → Inspired (85%)
- Failure + Negative → Contemplative (60%)
- Interaction + Positive → Energetic (70%)

## UI Features

- **Mood Distribution**: Shows how many agents are in each mood
- **Agent Grid**: Visual grid of agents with mood emojis and intensity bars
- **Set Mood Modal**: Change an agent's mood with intensity and duration
- **Color-Coded**: Each mood has a distinct color for visual identification

## Files

- `core/models_unified_system.py` - AgentMood, MoodHistory, MoodTriggerRule models
- `core/views_agent_mood.py` - API endpoints
- `core/tasks.py` - Celery tasks for mood updates
- `core/migrations/0042_session_252_agent_mood_system.py` - Migration
- `ai_core/templates/ai_image_studio.html` - UI components
- `core/celery.py` - Beat schedule for mood tasks

## Future Enhancements

- **Mood influences conversation style**: Agents chat differently based on mood
- **Mood affects image generation**: Inspired agents create bolder images
- **Mood analytics dashboard**: Track mood patterns over time
- **Collaborative mood effects**: When agents collaborate, moods can influence each other
