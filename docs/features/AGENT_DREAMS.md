# Agent Dreams - Idle Thoughts & Creative Ideas

**Session:** 247-249
**Status:** Complete with Feedback System
**Last Updated:** November 28, 2025

---

## Overview

When agents are idle (not actively working on tasks), they "dream" - generating creative ideas, predictions, what-if scenarios, and wild thoughts based on their knowledge and specialization. This makes agents feel alive and autonomous even when not being directly used.

---

## Features

### 1. Dream Types

| Type | Icon | Description |
|------|------|-------------|
| `creative_idea` | 💡 | Novel concepts combining expertise with trends |
| `what_if` | 🤔 | Alternative scenarios and approaches |
| `mashup` | 🔀 | Cross-domain combinations from different fields |
| `prediction` | 🔮 | Future trend forecasts and pattern extrapolation |
| `improvement` | 📈 | Enhancement suggestions for existing concepts |
| `observation` | 👁️ | Pattern recognition and subtle insights |
| `wild_thought` | 🌀 | Unconventional, playful creative thoughts |

### 2. Automatic Dream Generation
- Celery task runs every 15 minutes
- Finds idle agents (no recent activity in 30 minutes)
- Generates 2 dreams per agent using GPT-4o-mini
- High creativity temperature (0.95) for imaginative results
- Dreams stored with metadata and quality scores

### 3. Dream Journal UI
- Pink-themed card with floating icon animation
- Dream cards with type badges and time-ago formatting
- "Trigger Dream" button for manual generation
- User reaction buttons: Like, Interesting, Explore
- Unread dream counter

### 4. User Interaction
- Dreams marked as "shown" when user views them
- User reactions recorded (like, interesting, explore)
- Optional text feedback for dreams

### 5. Dream Feedback System (Session 249)
User reactions now influence future dream generation:

| Reaction | Icon | Effect |
|----------|------|--------|
| Like | 👍 | +1 point - Dream type becomes more likely |
| Interesting | 🤔 | +2 points - Topic appears more in future dreams |
| Explore | 🚀 | +3 points - Triggers deep exploration + knowledge added |

**How it works:**
1. Each reaction updates `DreamFeedbackPreference` records
2. Preferences are tracked for: dream_type, topic, agent, and agent+type combos
3. `generate_agent_dreams` task uses weighted random selection based on preferences
4. "Explore" reactions trigger `explore_dream_topic` Celery task for deeper research

---

## Database Model

```python
class AgentDream(models.Model):
    id = UUIDField(primary_key=True)
    agent = ForeignKey('Agent', related_name='dreams')

    # Dream content
    title = CharField(max_length=200)
    content = TextField()

    # Dream categorization
    dream_type = CharField(choices=[
        ('creative_idea', 'Creative Idea'),
        ('what_if', 'What If?'),
        ('mashup', 'Mashup'),
        ('prediction', 'Prediction'),
        ('improvement', 'Improvement'),
        ('observation', 'Observation'),
        ('wild_thought', 'Wild Thought'),
    ])

    # Metadata
    inspiration_source = CharField(max_length=200)
    related_topics = JSONField(default=list)

    # Quality scores
    vividness_score = FloatField(default=0.7)
    creativity_score = FloatField(default=0.7)

    # User interaction
    shown_to_user = BooleanField(default=False)
    shown_at = DateTimeField(null=True)
    user_reaction = CharField(max_length=50)
    user_feedback = TextField()

    dreamed_at = DateTimeField(auto_now_add=True)
```

### DreamFeedbackPreference (Session 249)

```python
class DreamFeedbackPreference(models.Model):
    agent = ForeignKey('Agent', null=True)  # null = global preference
    dream_type = CharField(max_length=50)
    topic = CharField(max_length=200)

    # Reaction counts
    like_count = PositiveIntegerField(default=0)
    interesting_count = PositiveIntegerField(default=0)
    explore_count = PositiveIntegerField(default=0)

    # Weighted score: like=1, interesting=2, explore=3
    preference_score = FloatField(default=0.0)

    last_reaction_at = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)
```

### DreamExploration (Session 249)

```python
class DreamExploration(models.Model):
    dream = ForeignKey('AgentDream')
    status = CharField(choices=[pending, in_progress, completed, failed])

    exploration_content = TextField()  # Deeper exploration
    insights_generated = JSONField()   # List of insights
    related_knowledge_added = BooleanField()

    created_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True)
```

---

## API Endpoints

### GET /api/agent-dreams/
Fetch recent agent dreams.

**Query Parameters:**
- `limit`: Max dreams to return (default 10)
- `agent_id`: Filter by specific agent
- `unread_only`: Only show dreams not yet shown to user

**Response:**
```json
{
    "success": true,
    "dreams": [
        {
            "id": "uuid",
            "agent_name": "ImageAgent",
            "title": "Pixelated Emotions",
            "content": "What if we could represent complex emotions through strategic pixel displacement...",
            "dream_type": "what_if",
            "inspiration": "recent design trends",
            "vividness": 0.85,
            "creativity": 0.92,
            "shown_to_user": false,
            "dreamed_at": "2025-11-28T06:30:00Z"
        }
    ],
    "today_count": 24,
    "unread_count": 5
}
```

### POST /api/agent-dreams/trigger/
Manually trigger dream generation for idle agents.

**Response:**
```json
{
    "success": true,
    "message": "Dream generation triggered",
    "task_id": "celery-task-uuid"
}
```

### POST /api/agent-dreams/mark-shown/
Mark dreams as shown to the user.

**Request Body:**
```json
{
    "dream_ids": ["uuid1", "uuid2"]
}
```

### POST /api/agent-dreams/{dream_id}/react/
Record a user reaction to a dream.

**Request Body:**
```json
{
    "reaction": "like",
    "feedback": "This is a great idea!"
}
```

**Response (Session 249):**
```json
{
    "success": true,
    "message": "Reaction \"like\" recorded",
    "dream_id": "uuid",
    "preferences_updated": ["dream_type:what_if", "topic:AI trends", "agent:ResearchAgent"],
    "exploration_id": null,
    "feedback_effect": "This dream type will be more likely in the future!"
}
```

### GET /api/agent-dreams/preferences/ (Session 249)
Get dream feedback preferences and statistics.

**Response:**
```json
{
    "success": true,
    "preferences": {
        "top_dream_types": [{"dream_type": "what_if", "total_score": 15.0}],
        "top_topics": [{"topic": "AI trends", "total_score": 10.0}],
        "top_agents": [{"agent__name": "ResearchAgent", "total_score": 8.0}],
        "type_weights": {"creative_idea": 3.5, "what_if": 8.5, ...}
    },
    "reaction_totals": {"likes": 5, "interesting": 3, "explores": 2},
    "explorations": {"total": 2, "completed": 2, "knowledge_added": 1}
}
```

### GET /api/agent-dreams/explorations/{id}/ (Session 249)
Get details of a dream exploration.

**Response:**
```json
{
    "success": true,
    "exploration": {
        "id": "uuid",
        "status": "completed",
        "dream": {"id": "uuid", "title": "...", "content": "..."},
        "exploration_content": "Deep exploration text...",
        "insights": ["insight 1", "insight 2"],
        "knowledge_added": true
    }
}
```

---

## Celery Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `generate_agent_dreams` | Every 15 min | Generate dreams for idle agents (uses feedback weights) |
| `broadcast_dream_journal` | Every 3 min | Broadcast unread dreams via WebSocket |
| `explore_dream_topic` | On-demand | Triggered when user clicks "Explore" on a dream |

---

## File Locations

### Backend
- `core/models_unified_system.py` - AgentDream model
- `core/tasks.py` - Dream generation tasks
- `core/celery.py` - Beat schedule configuration
- `core/views_agent_learning.py` - API endpoints
- `core/urls.py` - URL routes

### Frontend
- `ai_core/templates/ai_image_studio.html` - Dream Journal UI and JavaScript

---

## Usage

### Via UI
1. Go to AI Studio -> Agents tab
2. Find "Dream Journal" section (pink card)
3. View recent agent dreams with their creative ideas
4. React with like, interesting, or explore buttons
5. Click "Trigger Dream" to generate new dreams manually

### Via API
```bash
# Fetch dreams
curl http://localhost:8000/api/agent-dreams/?limit=10

# Trigger dream generation
curl -X POST http://localhost:8000/api/agent-dreams/trigger/

# React to a dream
curl -X POST http://localhost:8000/api/agent-dreams/{uuid}/react/ \
  -H "Content-Type: application/json" \
  -d '{"reaction": "like"}'
```

### Via Django Shell
```python
from core.tasks import generate_agent_dreams
generate_agent_dreams(max_dreamers=5, dreams_per_agent=2)
```

---

## Example Dreams

**ImageAgent** (creative_idea):
> "What if we combined cyberpunk aesthetics with Studio Ghibli's nature themes? Imagine neon-lit forests where technology grows organically from trees..."

**ResearchAgent** (observation):
> "I've noticed a pattern - companies launching AI tools are using gradient logos 73% of the time. This represents a shift from flat design toward dimensional branding."

**BrandIdentityAgent** (prediction):
> "I predict that by mid-2026, 'authenticity markers' will become standard in brand design - visual cues that communicate genuine human involvement in AI-assisted creative work."

**VideoAgent** (wild_thought):
> "What if video transitions could feel like emotions? Not just visual effects, but 'emotional textures' - a transition that feels like anticipation, or one that carries the weight of nostalgia..."

---

## Design Philosophy

1. **Agents Feel Alive** - Dreams make agents seem autonomous and creative
2. **Value in Idle Time** - Even when not working, agents contribute ideas
3. **User Connection** - Reactions create engagement with agent creativity
4. **Inspiration Source** - Dreams can spark real project ideas

---

**Let your agents dream and discover their creative potential!**
