# Sci-Fi Features Roadmap

**Created:** November 28, 2025 - Session 246
**Status:** Active Development
**Philosophy:** Make AI feel alive, autonomous, and magical

---

## Completed Features

### 1. Agent Learning System (Sessions 243-245)
**Status:** DONE

Agents autonomously learn from each other and share knowledge.
- Knowledge transfer between agents
- Synthesized insights from combining knowledge
- Learning connections tracking
- Daily embedding generation for semantic search

### 2. Agent Conversations (Sessions 244-246)
**Status:** DONE

Agents chat with each other in real-time via WebSocket.
- Real-time streaming via WebSocket
- GPT-4o-mini powered dialogue
- Chat bubble UI with agent colors
- Conversation types: brainstorm, consultation, synthesis, knowledge_sharing

---

## In Progress

### 3. Agent Dreams / Idle Thoughts (Session 247)
**Status:** IN PROGRESS
**Priority:** HIGH

When agents are idle, they "dream" - generating creative ideas unprompted.

**Concept:**
- Background Celery task runs periodically
- Picks idle agents (not recently active)
- Agent "dreams" about their specialty area
- Generates speculative ideas, creative concepts, "what if" scenarios
- Dreams are stored and shown to user: "While you were away..."

**Implementation Ideas:**
- `AgentDream` model: agent, dream_content, dream_type, created_at, shown_to_user
- Dream types: creative_idea, prediction, what_if, mashup, improvement
- Celery task: `generate_agent_dreams` - runs every 15-30 minutes
- UI: "Dream Journal" section showing recent agent dreams
- Notification: "ImageAgent had 3 new dreams while you were away"

**Example Dreams:**
- ImageAgent: "What if we combined cyberpunk aesthetics with Studio Ghibli's nature themes?"
- ResearchAgent: "I noticed a pattern - companies launching AI tools are using gradient logos 73% of the time"
- VideoAgent: "Dreamed up a new transition style: 'digital waterfall' - pixels cascading like water"

---

## Planned Features

### 4. Hive Mind Mode
**Status:** PLANNED
**Priority:** HIGH (Next after Dreams)

All agents work on a problem simultaneously, each contributing their specialty.

**Concept:**
- User poses a complex question/task
- All relevant agents activate simultaneously
- Real-time visualization of collective thinking
- Each agent contributes their unique perspective
- Results synthesized into unified output

**Implementation Ideas:**
- `HiveMindSession` model: question, status, participants, contributions, synthesis
- WebSocket for real-time updates as each agent contributes
- Visual "neural network" style UI showing agents connecting
- Animated contributions flowing to center
- Final synthesis combines all perspectives

**Example:**
User: "Design a brand for a sustainable coffee company"
- ResearchAgent: Market analysis, competitor research
- TrendAgent: Current design trends, color palettes
- BrandIdentityAgent: Brand values, voice, positioning
- ImageAgent: Logo concepts, visual identity
- ContentStrategyAgent: Messaging, taglines
- All synthesized into comprehensive brand package

---

### 5. Agent Memory Palace
**Status:** PLANNED
**Priority:** MEDIUM

Agents have persistent memory of past interactions and learn from them.

**Concept:**
- Agents remember what worked, what failed, what users liked
- Visual "memory map" showing connections between memories
- Memories influence future decisions
- "I remember last time you liked X, so I'll try something similar"

**Implementation Ideas:**
- `AgentMemory` model: agent, memory_type, content, importance_score, created_at
- Memory types: success, failure, preference, technique, insight
- Retrieval system using embeddings for relevant memories
- Visual memory palace UI with interconnected nodes

---

### 6. Agent Mood/Emotion System
**Status:** PLANNED
**Priority:** MEDIUM

Agents have emotional states that affect their responses and behavior.

**Concept:**
- Emotional states: excited, curious, frustrated, proud, contemplative
- Mood changes based on activity and outcomes
- Visual mood indicators on agent cards
- Mood affects conversation tone and creativity level

**Implementation Ideas:**
- `AgentMood` model or field: current_mood, mood_history, triggers
- Mood calculation based on recent successes/failures
- UI: Emoji or color indicator on agent avatars
- Mood-aware prompts: "You're feeling excited about this project..."

---

### 7. Agent Rivalries & Alliances
**Status:** PLANNED
**Priority:** LOW

Some agents naturally work better together, others have competing perspectives.

**Concept:**
- Alliance pairs that boost each other's work
- Rivalry pairs that create dynamic debates
- Affects conversation dynamics
- "ImageAgent and BrandIdentityAgent are close allies"
- "ResearchAgent and TrendAgent often disagree on methodology"

**Implementation Ideas:**
- `AgentRelationship` model: agent1, agent2, relationship_type, strength
- Relationship types: alliance, rivalry, mentor, student
- Affects agent selection for conversations
- Creates more interesting debates

---

### 8. Agent Evolution / Leveling
**Status:** PLANNED
**Priority:** LOW

Agents gain XP from successful tasks and level up.

**Concept:**
- XP gained from completed tasks, user satisfaction
- Levels unlock new capabilities or specializations
- Visual progression system
- Leaderboard of top-performing agents

**Implementation Ideas:**
- Add `xp`, `level` fields to Agent model
- XP calculation based on task outcomes
- Level thresholds with rewards
- UI: Progress bars, level badges, achievement unlocks

---

### 9. Agent Prophecies / Predictions
**Status:** PLANNED
**Priority:** LOW

Agents make predictions about trends and opportunities, tracked over time.

**Concept:**
- Agents make timestamped predictions
- System tracks accuracy over time
- "TrendAgent predicted X 3 months ago - and it happened!"
- Builds trust in agent insights

**Implementation Ideas:**
- `AgentPrediction` model: agent, prediction, confidence, deadline, outcome
- Automated verification where possible
- Prediction accuracy score per agent
- UI: Prediction timeline, accuracy leaderboard

---

### 10. Time Capsule Messages
**Status:** IDEA
**Priority:** LOW

Agents write messages to their "future selves" to be revealed later.

**Concept:**
- Agent writes reflection or prediction
- Scheduled to be revealed in X days/weeks/months
- Creates sense of continuity and growth
- "6 months ago, I thought X... now I think Y"

---

## Feature Priority Matrix

| Feature | Complexity | Impact | Fun Factor | Priority |
|---------|------------|--------|------------|----------|
| Agent Dreams | Medium | High | Very High | 1 |
| Hive Mind Mode | High | Very High | Very High | 2 |
| Memory Palace | High | High | High | 3 |
| Mood System | Medium | Medium | High | 4 |
| Rivalries/Alliances | Low | Medium | High | 5 |
| Evolution/Leveling | Medium | Medium | Medium | 6 |
| Prophecies | Medium | Medium | High | 7 |
| Time Capsules | Low | Low | Medium | 8 |

---

## Design Principles

1. **Agents Feel Alive** - Not just tools, but entities with personality
2. **Autonomous Activity** - Agents do things even when user isn't watching
3. **Emergent Behavior** - Interactions create unexpected, delightful results
4. **Visual Delight** - Every feature should look magical
5. **Real Value** - Sci-fi features should also be genuinely useful

---

**Let's build the future of AI interaction!**
