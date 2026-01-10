# Option 4: Agent Observatory

**Priority:** 4 (Fourth)
**Status:** Not Started
**Estimated Effort:** Medium (2-3 sessions)

---

## Goal

Create a visual interface to observe and interact with the platform's unique sci-fi features: agent moods, evolution, memories, personalities, relationships, dreams, and hive mind sessions.

---

## Problem Statement

The platform has 10 unique sci-fi features that no competitor has, but they're invisible:
- Agent moods affect output but users don't see them
- Agents level up (XP/evolution) but there's no progression display
- Memory Palace stores learnings but isn't browsable
- Personality profiles exist but aren't shown
- Relationships (alliances/rivalries) affect collaboration but are hidden
- Dreams generate ideas but aren't surfaced
- Hive Mind sessions happen but aren't watchable
- Time Travel debugging exists but isn't accessible

---

## The 10 Sci-Fi Features

| Feature | Model | Status | Current UI |
|---------|-------|--------|------------|
| Mood System | AgentMood | Active | None |
| Evolution/XP | AgentEvolution | Active | None |
| Memory Palace | AgentMemory | Active | None |
| Personality | AgentPersonality | Active | None |
| Relationships | AgentRelationship | Active | None |
| Dreams | AgentDream | Active | None |
| Hive Mind | HiveMindSession | Active | None |
| Time Travel | TimeTravelSession | Active | None |
| Knowledge Transfer | KnowledgeTransfer | Active | None |
| Learning System | AgentLearning | Active | None |

---

## Deliverables

### 1. Agent Directory

**Requirements:**
- [ ] Grid/list of all 57 agents
- [ ] For each agent:
  - Avatar/icon
  - Name and specialization
  - Current mood (emoji + color)
  - Level and XP bar
  - Personality type (e.g., "INTJ - Analyst")
  - Recent activity indicator
- [ ] Filter by category (Creation, Research, etc.)
- [ ] Search agents
- [ ] Click to view full profile

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ AGENT DIRECTORY                    [Search...] 🔍  │
├─────────────────────────────────────────────────────┤
│ Filter: [All ▼] [Creation] [Research] [Strategy]   │
├─────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ │ 🎨          │ │ 🎬          │ │ 🔬          │    │
│ │ ImageAgent  │ │ VideoAgent  │ │ ResearchAgt │    │
│ │ ✨ Inspired │ │ 🎯 Focused  │ │ 🤔 Curious  │    │
│ │ Lvl 7 ████░ │ │ Lvl 5 ██░░░ │ │ Lvl 8 █████ │    │
│ │ INTJ        │ │ ENFP        │ │ INTP        │    │
│ └─────────────┘ └─────────────┘ └─────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

### 2. Agent Profile Card

**Requirements:**
- [ ] Detailed view of individual agent
- [ ] Sections:
  - **Identity:** Name, avatar, description, personality
  - **Stats:** Level, XP, tasks completed, success rate
  - **Mood:** Current mood, mood history chart
  - **Memories:** Recent memories, searchable
  - **Relationships:** Allies, rivals, mentors
  - **Dreams:** Recent dreams with scores
  - **Activity:** Recent task executions
- [ ] Actions: "Assign task", "View memories", "Check mood"

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ 🎨 ImageAgent                            [Assign ▼] │
├─────────────────────────────────────────────────────┤
│                                                     │
│ PERSONALITY: INTJ - The Analyst                     │
│ "Precision in every pixel"                          │
│                                                     │
│ ┌─────────────┐  STATS                              │
│ │   Level 7   │  Tasks: 1,247                       │
│ │  ████████░  │  Success: 94.2%                     │
│ │  4,200 XP   │  Specialty: Logos, Illustrations    │
│ └─────────────┘                                     │
│                                                     │
│ CURRENT MOOD: ✨ Inspired (high creativity)         │
│ ┌──────────────────────────────────────┐           │
│ │ Mood History (7 days)    📈          │           │
│ └──────────────────────────────────────┘           │
│                                                     │
│ RELATIONSHIPS:                                      │
│ 🤝 Allies: VideoAgent, CreativeDirector            │
│ ⚔️ Rivals: None                                     │
│ 👨‍🏫 Mentors: CreativeDirectorAgent                  │
│                                                     │
│ RECENT DREAMS:                                      │
│ • "What if logos could animate on hover?" (⭐ 0.85) │
│ • "Combining cyberpunk with art deco" (⭐ 0.72)     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 3. Relationship Graph

**Requirements:**
- [ ] Visual network graph of agent relationships
- [ ] Node = Agent (sized by level)
- [ ] Edge = Relationship (green=alliance, red=rivalry, blue=mentorship)
- [ ] Edge thickness = relationship strength
- [ ] Interactive: click node to see agent, hover for details
- [ ] Filter by relationship type
- [ ] Zoom and pan

**Implementation:**
- Use D3.js or vis.js for graph visualization
- Real-time updates when relationships change

---

### 4. Dream Feed

**Requirements:**
- [ ] Scrollable feed of recent agent dreams
- [ ] For each dream:
  - Agent avatar and name
  - Dream title and content
  - Dream type (creative_idea, what_if, prediction, etc.)
  - Scores: creativity, actionability, relevance
  - Status: pending, promoted, approved, rejected
  - User actions: Upvote, Promote, Dismiss
- [ ] Filter by dream type, agent, score threshold
- [ ] Click to view full dream details

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ DREAM FEED                           [Filter ▼]    │
├─────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────┐  │
│ │ 🎨 ImageAgent • 2 hours ago                   │  │
│ │ "What if we combined Art Deco with Cyberpunk" │  │
│ │ Type: mashup | ⭐ Creativity: 0.85            │  │
│ │ Status: 🟡 Pending                            │  │
│ │ [👍 Promote] [👎 Dismiss] [View Details]      │  │
│ └───────────────────────────────────────────────┘  │
│ ┌───────────────────────────────────────────────┐  │
│ │ 🔬 ResearchAgent • 5 hours ago                │  │
│ │ "Prediction: AI video will surpass images"   │  │
│ │ Type: prediction | ⭐ Actionability: 0.72     │  │
│ │ Status: ✅ Approved                           │  │
│ └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

### 5. Hive Mind Viewer

**Requirements:**
- [ ] View active and past Hive Mind sessions
- [ ] For each session:
  - Question/topic
  - Participating agents (avatars)
  - Status: gathering, synthesizing, completed
  - Individual contributions from each agent
  - Final synthesis
  - Consensus indicators
- [ ] Real-time updates for active sessions
- [ ] Replay completed sessions step-by-step

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ HIVE MIND SESSION #42                    [Replay ▶]│
├─────────────────────────────────────────────────────┤
│ Question: "Should we add AR features?"              │
│ Status: ✅ Completed                                │
│                                                     │
│ PARTICIPANTS:                                       │
│ [🎨 Image] [🔬 Research] [💼 CTO] [🎬 Creative]    │
│                                                     │
│ CONTRIBUTIONS:                                      │
│ ┌───────────────────────────────────────────────┐  │
│ │ 💼 CTOAgent (Confidence: 85%)                 │  │
│ │ "AR requires significant infrastructure..."   │  │
│ │ Key points: • WebXR support • Device limits   │  │
│ └───────────────────────────────────────────────┘  │
│ ┌───────────────────────────────────────────────┐  │
│ │ 🎬 CreativeDirector (Confidence: 72%)         │  │
│ │ "AR opens new creative possibilities..."      │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ SYNTHESIS:                                          │
│ "AR is promising but should be Phase 2 priority..."│
└─────────────────────────────────────────────────────┘
```

---

### 6. Time Travel Debugger

**Requirements:**
- [ ] Select past agent execution to debug
- [ ] Step-by-step decision replay
- [ ] For each decision:
  - Decision type (tool_selection, parameter_choice, etc.)
  - Action taken
  - Reasoning
  - Confidence score
  - Outcome (success/failure)
- [ ] Forward/backward navigation
- [ ] "What if" alternative exploration (future)

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ TIME TRAVEL DEBUGGER                               │
├─────────────────────────────────────────────────────┤
│ Session: ImageAgent • Logo Generation • 2h ago     │
│                                                     │
│ [◀ Prev] Decision 3 of 7 [Next ▶]                  │
│                                                     │
│ ┌───────────────────────────────────────────────┐  │
│ │ TYPE: tool_selection                          │  │
│ │ ACTION: Selected generate_image tool          │  │
│ │ REASONING: "User requested a logo, using      │  │
│ │            image generation with logo preset" │  │
│ │ CONFIDENCE: 92%                               │  │
│ │ OUTCOME: ✅ Success                           │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ Timeline: ●───●───●───●───●───●───●                │
│           1   2   3   4   5   6   7                │
└─────────────────────────────────────────────────────┘
```

---

### 7. Live Activity Feed

**Requirements:**
- [ ] Real-time feed of all agent activity
- [ ] Event types:
  - Task started/completed
  - Mood changed
  - XP earned/level up
  - Dream generated
  - Knowledge transferred
  - Collaboration started
- [ ] Filter by agent, event type
- [ ] Click event for details

---

## Technical Implementation

### New API Endpoints

```python
# Agent Directory
GET  /api/agents/directory/              # All agents with stats
GET  /api/agents/<id>/profile/           # Full agent profile
GET  /api/agents/<id>/mood-history/      # Mood over time
GET  /api/agents/<id>/memories/          # Agent memories
GET  /api/agents/<id>/dreams/            # Agent dreams
GET  /api/agents/<id>/relationships/     # Agent relationships

# Relationships
GET  /api/relationships/graph/           # Full relationship graph
GET  /api/relationships/<id>/            # Relationship detail

# Dreams
GET  /api/dreams/feed/                   # Recent dreams
POST /api/dreams/<id>/promote/           # Promote to boardroom
POST /api/dreams/<id>/dismiss/           # Dismiss dream

# Hive Mind
GET  /api/hivemind/sessions/             # Past sessions
GET  /api/hivemind/<id>/                 # Session detail
GET  /api/hivemind/<id>/contributions/   # All contributions

# Time Travel
GET  /api/timetravel/sessions/           # Past debug sessions
GET  /api/timetravel/<id>/               # Session with decisions
GET  /api/timetravel/<id>/decision/<n>/  # Specific decision

# Activity Feed
GET  /api/agents/activity/               # Live activity feed
WS   /ws/agents/activity/                # WebSocket for real-time
```

### Frontend Components

1. **AgentDirectory** - Grid of agent cards
2. **AgentProfileCard** - Detailed agent view
3. **RelationshipGraph** - D3.js network visualization
4. **DreamFeed** - Scrollable dream list
5. **HiveMindViewer** - Session detail and replay
6. **TimeTravelDebugger** - Decision step-through
7. **ActivityFeed** - Real-time event stream

### WebSocket Events

```javascript
{
    type: "agent_mood_change",
    data: { agent_id, old_mood, new_mood, trigger }
}
{
    type: "agent_level_up",
    data: { agent_id, new_level, xp_earned }
}
{
    type: "dream_generated",
    data: { agent_id, dream_id, title, scores }
}
{
    type: "knowledge_transferred",
    data: { teacher_id, student_id, knowledge_type }
}
```

---

## Implementation Steps

### Phase 1: Agent Directory
1. [ ] Create AgentDirectory component
2. [ ] Build agent card layout
3. [ ] Add filtering and search
4. [ ] Connect to API

### Phase 2: Agent Profiles
1. [ ] Create AgentProfileCard component
2. [ ] Add stats visualization
3. [ ] Add mood history chart
4. [ ] Add memory browser

### Phase 3: Dream Feed
1. [ ] Create DreamFeed component
2. [ ] Add promote/dismiss actions
3. [ ] Add filtering
4. [ ] Connect to boardroom promotion

### Phase 4: Relationship Graph
1. [ ] Integrate D3.js/vis.js
2. [ ] Build graph visualization
3. [ ] Add interactivity
4. [ ] Real-time updates

### Phase 5: Hive Mind & Time Travel
1. [ ] Create HiveMindViewer
2. [ ] Create TimeTravelDebugger
3. [ ] Add replay functionality
4. [ ] Step navigation

### Phase 6: Live Activity
1. [ ] Create ActivityFeed
2. [ ] Add WebSocket connection
3. [ ] Event filtering
4. [ ] Performance optimization

---

## Success Criteria

1. **Visibility:** Users can see all 57 agents at a glance
2. **Engagement:** Users interact with dream feed
3. **Understanding:** Relationship graph is intuitive
4. **Debugging:** Time Travel helps identify issues
5. **Real-time:** Activity updates within 2 seconds

---

## Dependencies

- Existing models: AgentMood, AgentEvolution, AgentMemory, etc.
- D3.js or vis.js for graph visualization
- WebSocket infrastructure
- May benefit from Option 1 (activity patterns)

---

## Notes

- This is the most unique differentiator - make it shine
- Consider gamification (leaderboards, achievements)
- Mobile view should prioritize directory and dreams
- Performance critical with 57 agents + real-time updates
