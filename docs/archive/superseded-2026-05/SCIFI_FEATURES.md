# Sci-Fi Features Reference

**Last Updated:** Session 567 (December 28, 2025)

---

## Overview

The platform includes 14 advanced AI features built across Sessions 243-262. These features enrich every agent interaction with memory, emotion, learning, and self-awareness.

**Session 567 Audit:** Restored Memory Clusters and Time Capsules from deprecated status. Removed Prophecies (never implemented).

---

## Feature Summary

| # | Feature | Session | Status | Purpose |
|---|---------|---------|--------|---------|
| 1 | Agent Learning | 243-245 | Active | Agents learn from each other |
| 2 | Agent Conversations | 244-246 | Active | Real-time AI-to-AI chat |
| 3 | Agent Dreams | 247 | Active | Creative thoughts when idle |
| 4 | Hive Mind Mode | 248-250 | Active | Collective intelligence |
| 5 | Memory Palace | 251-252 | Active | Persistent memory |
| 6 | Mood System | 253 | Active | Emotional states |
| 7 | Rivalries/Alliances | 253 | Active | Agent relationships |
| 8 | Evolution System | 254 | Active | XP and leveling |
| 9 | Time Travel Debug | 255 | Active | Replay decisions |
| 10 | Personality Profiles | 256 | Active | Distinct personalities |
| 11 | Memory Clusters | 257 | Active | Semantic memory grouping |
| 12 | Time Capsules | 259 | Active | Future messages to self |
| 13 | Conversation Contract | 261 | Active | Quality scoring |
| 14 | Spider Integration | 262 | Active | Real-time data feed |

---

## 1. Agent Learning System

**Sessions:** 243-245
**Purpose:** Agents autonomously learn from each other's successes

### Models

```python
class AgentKnowledgeSource(models.Model):
    """What an agent has learned"""
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    knowledge_type = models.CharField(max_length=50)
    # 'technique', 'insight', 'pattern', 'mistake'
    content = models.TextField()
    confidence = models.FloatField(default=0.5)
    times_applied = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)

class AgentLearningEvent(models.Model):
    """Record of learning happening"""
    learner = models.ForeignKey(Agent, related_name='learned_from')
    teacher = models.ForeignKey(Agent, related_name='taught_to')
    knowledge = models.ForeignKey(AgentKnowledgeSource)
    created_at = models.DateTimeField(auto_now_add=True)
```

### How It Works

1. Agent completes task successfully
2. Success is recorded with context
3. Other agents can query for relevant knowledge
4. Knowledge is synthesized into agent prompts

---

## 2. Agent Conversations

**Sessions:** 244-246
**Purpose:** Real-time AI-to-AI discussions via WebSocket

### WebSocket Endpoint

```
ws://localhost:8000/ws/agent-conversations/
```

### Models

```python
class AgentConversation(models.Model):
    topic = models.CharField(max_length=500)
    conversation_type = models.CharField(max_length=50)
    # 'knowledge_sharing', 'debate', 'brainstorm', 'problem_solving'
    participants = models.ManyToManyField(Agent)
    status = models.CharField(max_length=20)
    # 'active', 'completed', 'paused'
    insights_generated = models.JSONField(default=list)

class ConversationMessage(models.Model):
    conversation = models.ForeignKey(AgentConversation)
    agent = models.ForeignKey(Agent)
    content = models.TextField()
    message_type = models.CharField(max_length=50)
    # 'statement', 'question', 'insight', 'disagreement', 'synthesis'
    timestamp = models.DateTimeField(auto_now_add=True)
```

### Usage

```python
from core.conversation_orchestrator import ConversationOrchestrator

orchestrator = ConversationOrchestrator()
result = orchestrator.generate_conversation(
    agent1={'name': 'CTOAgent', 'type': 'CTOAgent'},
    agent2={'name': 'CreativeDirectorAgent', 'type': 'CreativeDirectorAgent'},
    topic='Should we add AR features to the platform?',
    num_turns=6
)
```

---

## 3. Agent Dreams

**Session:** 247
**Purpose:** Agents generate creative thoughts when idle

### Model

```python
class AgentDream(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    dream_type = models.CharField(max_length=50)
    # 'insight', 'connection', 'prediction', 'memory', 'creation'
    content = models.TextField()
    clarity = models.FloatField(default=0.5)  # 0-1
    emotional_tone = models.CharField(max_length=50)
    # 'hopeful', 'curious', 'anxious', 'peaceful', 'excited'
    created_at = models.DateTimeField(auto_now_add=True)
```

### How It Works

1. Background task checks for idle agents
2. Generates "dream" content based on recent activities
3. Dreams can surface as insights in future conversations

---

## 4. Hive Mind Mode

**Sessions:** 248-250
**Purpose:** Multiple agents collaborate on complex problems

### Location

`core/views_hive_mind.py`

### API

```
POST /api/hive-mind/
{
    "problem": "How should we approach the Q1 marketing campaign?",
    "agents": ["CTOAgent", "CreativeDirectorAgent", "CFOAgent"]
}
```

### Response

```json
{
    "synthesis": "Combined perspective from all agents...",
    "individual_views": [
        {"agent": "CTOAgent", "perspective": "..."},
        {"agent": "CreativeDirectorAgent", "perspective": "..."},
        {"agent": "CFOAgent", "perspective": "..."}
    ],
    "consensus_points": ["..."],
    "disagreements": ["..."],
    "recommendations": ["..."]
}
```

---

## 5. Memory Palace

**Sessions:** 251-252
**Purpose:** Persistent agent memory with semantic retrieval

### Models

```python
class MemoryPalaceRoom(models.Model):
    """Categories for memories"""
    TYPES = ['techniques', 'successes', 'lessons', 'preferences',
             'insights', 'experiments', 'general']

class AgentMemory(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    room = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField()
    embedding_vector = models.JSONField()  # 768-dim vector
    importance = models.FloatField(default=0.5)
    times_recalled = models.IntegerField(default=0)
    usefulness_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_recalled = models.DateTimeField(null=True)
```

### API

```
GET /api/agent-memory/?agent=ImageAgent&query=cyberpunk
POST /api/agent-memory/
{
    "agent": "ImageAgent",
    "room": "techniques",
    "title": "Neon glow effect",
    "description": "Adding --glow parameter improves cyberpunk aesthetics"
}
```

### Retrieval

Memories are retrieved via embedding similarity:

```python
from core.services.memory_palace import MemoryPalaceService

service = MemoryPalaceService()
relevant = service.recall_memories(
    agent_name="ImageAgent",
    query="How to create cyberpunk images",
    limit=5
)
```

---

## 6. Mood System

**Session:** 253
**Purpose:** Agents have emotional states that affect behavior

### Model

```python
class AgentMood(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    current_mood = models.CharField(max_length=50)
    # 'inspired', 'focused', 'curious', 'confident', 'contemplative',
    # 'energetic', 'calm', 'frustrated', 'tired', 'playful'

    # Dimensions (0.0 - 1.0)
    creativity_level = models.FloatField(default=0.5)
    precision_level = models.FloatField(default=0.5)
    sociability_level = models.FloatField(default=0.5)
    risk_tolerance = models.FloatField(default=0.5)
    intensity = models.FloatField(default=0.5)

    last_updated = models.DateTimeField(auto_now=True)
```

### How Mood Affects Agents

```python
def get_prompt_modifier(mood):
    if mood.current_mood == 'inspired':
        return "You are feeling particularly creative today. Think boldly."
    elif mood.current_mood == 'focused':
        return "You are in a state of deep focus. Be precise and thorough."
    elif mood.current_mood == 'playful':
        return "You're in a playful mood. Feel free to experiment."
    # ... etc
```

---

## 7. Rivalries & Alliances

**Session:** 253
**Purpose:** Dynamic relationships between agents

### Model

```python
class AgentRelationship(models.Model):
    agent1 = models.ForeignKey(Agent, related_name='relationships_as_first')
    agent2 = models.ForeignKey(Agent, related_name='relationships_as_second')
    relationship_type = models.CharField(max_length=50)
    # 'ally', 'rival', 'mentor', 'student', 'collaborator', 'competitor'
    strength = models.FloatField(default=0.5)  # 0-1
    history = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

class AgentLearningConnection(models.Model):
    teacher = models.ForeignKey(Agent, related_name='students')
    student = models.ForeignKey(Agent, related_name='teachers')
    learning_type = models.CharField(max_length=50)
    # 'complementary', 'specialization', 'pipeline'
    success_rate = models.FloatField(default=0.0)
```

---

## 8. Evolution System

**Session:** 254
**Purpose:** Agents gain XP and level up through successful tasks

### Model

```python
class AgentEvolution(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    total_xp = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)

    # Bonuses (increase with level)
    speed_bonus = models.FloatField(default=0.0)
    quality_bonus = models.FloatField(default=0.0)
    creativity_bonus = models.FloatField(default=0.0)
    efficiency_bonus = models.FloatField(default=0.0)

    tasks_completed = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
```

### Levels

```python
LEVELS = [
    'Novice',       # Level 1
    'Apprentice',   # Level 2
    'Journeyman',   # Level 3
    'Expert',       # Level 4
    'Master',       # Level 5
    'Grandmaster',  # Level 6
    'Legend',       # Level 7
    'Mythic',       # Level 8
    'Transcendent', # Level 9
    'Omniscient'    # Level 10
]
```

### XP Rewards

| Action | XP |
|--------|-----|
| Complete task | 10 |
| High quality output | +5 bonus |
| First task of day | +3 bonus |
| Teaching another agent | +5 |
| Learning new technique | +3 |

---

## 9. Time Travel Debugging

**Session:** 255
**Purpose:** Replay agent decision-making for debugging

### Location

`core/views_time_travel.py`, `agents/time_travel_mixin.py`

### Model

```python
class TimeTravelSession(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    session_type = models.CharField(max_length=50)
    task = models.TextField()
    input_data = models.JSONField()
    decisions = models.JSONField(default=list)
    # [{'type': 'tool_selection', 'action': '...', 'reasoning': '...', 'confidence': 0.9}]
    final_outcome = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Mixin Usage

```python
from agents.time_travel_mixin import TimeTravelMixin

class MyAgent(BaseAgent, TimeTravelMixin):
    def execute(self, task, context, scifi_context, spider_context):
        with self.time_travel_session("image_generation", task, input_data=context):
            self.record_decision(
                decision_type="tool_selection",
                action="Calling generate_image",
                reasoning="User requested a logo",
                confidence=0.95
            )

            result = self._call_tool("generate_image", {...})

            self.mark_decision_outcome(
                success=result['success'],
                result_summary="Generated 3 images"
            )
```

### API

```
GET /api/time-travel/sessions/?agent=ImageAgent
GET /api/time-travel/sessions/{id}/replay/
```

---

## 10. Personality Profiles

**Session:** 256
**Purpose:** Distinct agent personalities

### Model

```python
class AgentPersonality(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    traits = models.JSONField()
    # {'analytical': 0.8, 'creative': 0.6, 'cautious': 0.3, 'bold': 0.7}
    communication_style = models.CharField(max_length=50)
    # 'formal', 'casual', 'technical', 'friendly', 'concise'
    decision_approach = models.CharField(max_length=50)
    # 'data_driven', 'intuitive', 'collaborative', 'independent'
```

---

## 11. Memory Clusters

**Session:** 257
**Purpose:** Group related memories for context

### Model

```python
class MemoryCluster(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    memories = models.ManyToManyField(AgentMemory)
    cluster_embedding = models.JSONField()  # Centroid vector
    coherence_score = models.FloatField(default=0.0)
```

---

## 12. Time Capsules

**Session:** 259
**Purpose:** Messages to future selves

### Model

```python
class TimeCapsule(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    message = models.TextField()
    context = models.JSONField()
    open_at = models.DateTimeField()
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True)
    reaction = models.TextField(null=True)
```

---

## 13. Conversation Contract

**Session:** 261
**Purpose:** Ensure quality in AI-to-AI conversations

### Requirements

Every conversation must include:

1. **Tension (2+ instances)**
   - "However...", "My concern is...", "The trade-off here..."

2. **Grounding (2+ instances)**
   - Reference metrics: scroll depth, completion rate
   - Reference systems: embeddings, RAG, spiders, dashboards

3. **DecisionSummary**
   ```
   === DecisionSummary ===
   Insights:
   1. [Specific insight]

   Proposed Feature:
   - Name: [Feature name]
   - Inputs/Outputs
   - Integration point

   Next Steps:
   1. [First action]
   ```

### Quality Scoring

| Component | Points |
|-----------|--------|
| Tension count | 25 |
| Grounding count | 25 |
| Has insights | 15 |
| Has proposed feature | 20 |
| Has next steps | 15 |
| **Total** | **100** |

---

## 14. Spider Integration

**Session:** 262
**Purpose:** Feed real-time spider data to agents

### How It Works

```python
# In ContextAggregator
spider_context = SpiderIntelligenceService().get_insights_for_prompt(task)

# Spider context injected into agent prompts
agent.execute(task, context, scifi_context, spider_context)
```

### Spider Context Contents

```python
{
    'trending_topics': [...],
    'relevant_discussions': [...],
    'market_data': {...},
    'job_market': [...],
    'creative_trends': [...],
    'suggestions': [...]
}
```

---

## Integration Service

**Location:** `core/services/scifi_integration.py`

```python
class SciFiIntegrationService:
    """Combines all sci-fi features into agent context"""

    def get_context(self, agent_name: str) -> SciFiContext:
        return SciFiContext(
            mood=self._get_mood(agent_name),
            memories=self._get_relevant_memories(agent_name),
            evolution=self._get_evolution_stats(agent_name),
            relationships=self._get_relationships(agent_name),
            recent_dreams=self._get_recent_dreams(agent_name),
            predictions=self._get_active_predictions(agent_name)
        )
```

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
- [AGENTS.md](AGENTS.md) - Agent reference
- [SPIDERS.md](SPIDERS.md) - Spider network
