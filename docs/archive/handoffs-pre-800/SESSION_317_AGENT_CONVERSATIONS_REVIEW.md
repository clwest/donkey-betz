# Session 317: Agent Conversations System Review

**Date:** December 2, 2025
**Purpose:** Detailed review of Agent Conversations system for future improvements
**Context:** User noticed conversations were always between ContentExecutor + CustomerResearchAgent

---

## System Overview

The Agent Conversations feature allows AI agents to have autonomous discussions with each other. These conversations appear in the UI under **Agents > Social > Agent Conversations**.

### Key Files

| File | Purpose |
|------|---------|
| `core/tasks.py:3494-3800` | `run_agent_conversation()` - Celery task that triggers conversations |
| `core/conversation_orchestrator.py` | `ConversationOrchestrator` class - Generates conversation content |
| `core/conversation_roles.py` | Role definitions, tension indicators, contract enforcement |
| `core/agent_conversation_consumer.py` | WebSocket consumer for real-time streaming |
| `core/models.py` | `AgentConversation`, `ConversationMessage` models |

---

## Current Participant Selection Logic

Located in `core/tasks.py:3524-3614`:

```python
# Step 1: Get agents with knowledge (max 20)
agents_with_knowledge = Agent.objects.filter(
    is_active=True,
    knowledge_sources__isnull=False
).distinct()[:20]

# Step 2: Pick random initiator
initiator = random.choice(agents_list)

# Step 3: Try to find connected agent first
connected_agents = AgentLearningConnection.objects.filter(
    teacher_agent=initiator
).values_list('student_agent_id', flat=True)

# Step 4: Prefer connected agents, fall back to random
possible_responders = [a for a in agents_list if a.id != initiator.id]
if connected_agents:
    connected_responders = [a for a in possible_responders if a.id in connected_agents]
    if connected_responders:
        possible_responders = connected_responders

responder = random.choice(possible_responders)
```

### Current Statistics (as of Session 317)

| Metric | Value |
|--------|-------|
| Agents with knowledge | 36 |
| Learning connections | 7 (each with 1 student) |
| Max agents queried | 20 |
| Participants per conversation | **Always 2** (hardcoded) |

### Learning Connections (Teacher → Student)

Only 7 connections exist:
- AIProjectBuilder → 1 student
- BrandIdentityAgent → 1 student
- Creation Agent → 1 student
- OpportunityPipelineOrchestrator → 1 student
- OpportunityScoringAgent → 1 student
- SEOOptimizerAgent → 1 student
- Vegas AI → 1 student

---

## Why Repetitive Pairings Occur

Recent conversations observed:
- ContentExecutor + CustomerResearchAgent (3 times)
- ContentStrategyAgent + CustomerResearchAgent (2 times)

**Root Causes:**

1. **Sparse learning connections**: Only 7 teacher→student pairs exist out of 36 agents
2. **Random selection**: When initiator has no connections, falls back to random
3. **Knowledge-based filtering**: Some agents have more knowledge items, making them more likely to be picked
4. **Topic generation**: Uses knowledge item titles, leading to repetitive "Core expertise: X" topics

---

## Conversation Orchestrator Design

Located in `core/conversation_orchestrator.py`:

### Key Features
- **2-agent conversations only** (agent1, agent2 parameters)
- **Contract enforcement**: Requires tension, grounding, no empty agreement
- **Role-specific prompts**: Different behavior based on agent type
- **Live system stats injection** (Session 315): Agents reference real platform metrics

### Conversation Flow
1. Generate 6 turns (configurable via `num_turns`)
2. Alternate between agent1 and agent2
3. Final turn generates `DecisionSummary` with insights
4. Enforce "constructive tension" - agents must challenge each other

### Token Limits (Session 315 fix)
- Normal turns: `max_output_tokens=1000`
- Final turn with DecisionSummary: `max_output_tokens=2000`

---

## Potential Improvements

### 1. More Diverse Pairings

**Option A: Remove connection preference**
```python
# Simply pick any two random agents
possible_responders = [a for a in agents_list if a.id != initiator.id]
responder = random.choice(possible_responders)
```

**Option B: Create more learning connections**
- Auto-generate connections based on agent specializations
- Group agents by category and create cross-category connections

**Option C: Track recent pairings and avoid repeats**
```python
# Get recent conversation pairs
recent_pairs = AgentConversation.objects.filter(
    started_at__gte=timezone.now() - timedelta(hours=24)
).values_list('participants__id', flat=True)

# Exclude recently paired agents
possible_responders = [a for a in agents_list
                       if a.id != initiator.id
                       and (initiator.id, a.id) not in recent_pairs]
```

### 2. Multi-Agent Conversations (3+ participants)

**Current limitation**: `ConversationOrchestrator.generate_conversation()` only accepts `agent1` and `agent2`

**Changes needed**:
- Modify orchestrator to accept list of agents
- Update conversation model to track speaking order
- Update prompts to reference multiple participants
- Update UI to display multi-speaker conversations

**Example design**:
```python
def generate_conversation(
    self,
    agents: List[Dict[str, Any]],  # List of 2-5 agents
    topic: str,
    num_turns: int = 8,
    speaking_order: str = "round_robin"  # or "natural", "moderated"
)
```

### 3. Better Topic Generation

**Current**: Uses `knowledge_item.title` which produces repetitive topics like "Core expertise: ContentExecutor"

**Improvement options**:
- Generate topic via GPT based on both agents' specializations
- Use spider data trends as conversation topics
- Pull from recent platform activity (new opportunities, A/B test results)
- Combine knowledge from both agents for synthesis topics

**Example**:
```python
topic_prompt = f"""Generate a specific, engaging conversation topic for:
- {initiator.name} (specializes in {initiator.specialization})
- {responder.name} (specializes in {responder.specialization})

Make it actionable and relevant to AI content creation.
"""
```

### 4. Specialization-Based Pairing

**Current**: Random pairing ignores what agents are good at

**Improvement**: Match complementary or contrasting agents

```python
PAIRING_RULES = {
    'creative': ['analytical', 'strategy'],  # Creative + Analytical = good tension
    'research': ['execution', 'creative'],
    'strategy': ['execution', 'research'],
}

# Get initiator category
initiator_category = get_agent_category(initiator)

# Find complementary agents
complementary = PAIRING_RULES.get(initiator_category, [])
possible_responders = [a for a in agents_list
                       if get_agent_category(a) in complementary]
```

### 5. Conversation Types Based on Agent Roles

**Current**: 6 conversation templates (knowledge_sharing, Q&A, brainstorm, debate, critical_review, devils_advocate)

**Improvement**: Match conversation type to agent pairing

| Pairing | Best Conversation Type |
|---------|----------------------|
| Research + Strategy | brainstorm, synthesis |
| Creative + Analytical | critical_review, debate |
| Executive + Specialist | consultation, Q&A |
| Peer specialists | knowledge_sharing, devils_advocate |

---

## Database Models Reference

### AgentConversation (core/models.py)
```python
class AgentConversation(models.Model):
    topic = models.CharField(max_length=500)
    conversation_type = models.CharField(max_length=50)  # brainstorm, debate, etc.
    participants = models.ManyToManyField(Agent)  # Can support 2+ agents
    initiator = models.ForeignKey(Agent)
    status = models.CharField()  # active, concluded, abandoned
    trigger_type = models.CharField()  # scheduled, user_initiated, agent_initiated
    related_knowledge = models.ForeignKey(AgentKnowledgeSource)
    started_at = models.DateTimeField()
    concluded_at = models.DateTimeField(null=True)
```

### ConversationMessage (core/models.py)
```python
class ConversationMessage(models.Model):
    conversation = models.ForeignKey(AgentConversation)
    agent = models.ForeignKey(Agent)  # The speaker
    content = models.TextField()
    message_type = models.CharField()  # statement, question, challenge, summary
    sequence = models.IntegerField()
    created_at = models.DateTimeField()
```

---

## Celery Schedule

From `core/celery.py`:
```python
'agent-conversations': {
    'task': 'core.tasks.run_agent_conversation',
    'schedule': crontab(minute='*/20'),  # Every 20 minutes
    'args': [3, 6]  # max_conversations=3, max_messages=6
}
```

---

## Testing Commands

```bash
# Trigger conversation manually
.venv/bin/python manage.py shell -c "
from core.tasks import run_agent_conversation
result = run_agent_conversation()
print(result)
"

# Check recent conversations
.venv/bin/python manage.py shell -c "
from core.models import AgentConversation
for c in AgentConversation.objects.order_by('-started_at')[:5]:
    participants = list(c.participants.values_list('name', flat=True))
    print(f'{c.topic}: {participants}')
"

# Check learning connections
.venv/bin/python manage.py shell -c "
from core.models import AgentLearningConnection
for c in AgentLearningConnection.objects.all():
    print(f'{c.teacher_agent.name} -> {c.student_agent.name}')
"
```

---

## Recommended Next Steps

1. **Quick win**: Remove the "prefer connected agents" logic to get more variety immediately
2. **Medium effort**: Implement pairing history tracking to avoid recent repeats
3. **Larger effort**: Add specialization-based complementary pairing
4. **Major feature**: Expand to 3+ agent conversations (requires orchestrator rewrite)

---

## Session 317 Accomplishments

Before this review, Session 317 also:
1. Fixed Dream Journal empty content (token limits: 600→1000, 200→500)
2. Verified dream generation working (19+ new dreams)
3. Created handoff: `SESSION_317_DREAM_JOURNAL_FIX.md`
4. Committed: `cf5a4d2`

---

**Status:** Review complete. Ready for user to decide which improvements to implement.
