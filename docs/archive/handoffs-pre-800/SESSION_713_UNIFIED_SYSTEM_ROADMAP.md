# Session 713: Unified Human System - Complete Roadmap & Workflow

**Date:** January 7, 2026
**Purpose:** Complete system integration roadmap - DO NOT LOSE THIS CONTEXT
**Status:** Master Planning Document

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Inventory](#current-state-inventory)
3. [14 Sci-Fi Features Status](#14-sci-fi-features-status)
4. [6 Main UI Pages Status](#6-main-ui-pages-status)
5. [Complete Gap Analysis](#complete-gap-analysis)
6. [Unified Human System Architecture](#unified-human-system-architecture)
7. [Integration Roadmap (5 Phases)](#integration-roadmap)
8. [Detailed Workflows](#detailed-workflows)
9. [API Inventory](#api-inventory)
10. [Implementation Checklist](#implementation-checklist)

---

## Executive Summary

### The Numbers

| Metric | Count | Notes |
|--------|-------|-------|
| **Backend API Endpoints** | 1,435 | Full capability |
| **Frontend API Calls** | ~45 | 3% utilization |
| **Sci-Fi Features** | 14 | All backend complete |
| **Sci-Fi Features in UI** | 1 | Dreams only (partial) |
| **Main UI Pages** | 6 | All isolated |
| **Cross-Page Connections** | 0 | Need to build |
| **Hidden Backend Potential** | 97% | Massive opportunity |

### The Problem

Pages work in ISOLATION. We built an incredible brain but forgot to connect the neurons.

### The Solution

5-phase integration roadmap to create a truly unified human system.

---

## Current State Inventory

### Backend Services (106 total)

| Category | Count | Key Services |
|----------|-------|--------------|
| Body Systems | 7 | heart, lungs, circulatory, spine, immune, digestive, muscular |
| Memory | 6 | memory_palace, memory_clusters, memory_embedding, memory_system, memory_access_control, unified_memory_manager |
| Agent | 8 | agent_router, agent_mood, agent_evolution, agent_relationships, agent_llm_router |
| Intelligence | 5 | collective_intelligence, spider_intelligence, ml_scoring_engine, autonomous_action_executor |
| Sci-Fi | 4 | scifi_integration, hive_mind, time_travel, consciousness |
| Revenue | 3 | distribution, roi_tracking, auto_kpi_tracking |
| Learning | 3 | learning_analytics, style_evolution, user_learning |

### Database Models (359+ total)

| Category | Models |
|----------|--------|
| Agents | Agent, AgentExecution, AgentPerformanceMetric |
| Body | HeartPulse, LungsPulse, CirculatoryPulse, SpinePulse, ImmunePulse, DigestivePulse, MuscularPulse |
| Memory | AgentMemory, MemoryPalaceRoom, MemoryConnection, MemoryCluster, MemoryClusterMembership |
| Dreams | AgentDream, DreamImplementation, DreamExploration |
| Evolution | AgentEvolution, AgentAbility, XPHistory, LevelMilestone |
| Mood | AgentMood, MoodHistory, MoodTriggerRule |
| Hive Mind | HiveMindSession, HiveMindContribution |
| Time Capsules | TimeCapsule |
| Mythology | MythologyQuarantine |
| Relationships | AgentAlly, AgentRivalry, AgentPersonality |
| Intelligence | Opportunity, PilotGate, Pilot, Experiment, Prediction |

---

## 14 Sci-Fi Features Status

| # | Feature | Backend | Frontend | API Routes | Priority |
|---|---------|---------|----------|------------|----------|
| 1 | **Agent Learning** | Complete | Partial (Learning tab) | 8 | HIGH |
| 2 | **Agent Conversations** | Complete | Partial (Modal) | 6 | MEDIUM |
| 3 | **Agent Dreams** | Complete | Partial (Modal) | 15 | DONE |
| 4 | **Hive Mind** | Complete | NONE | 5 | HIGH |
| 5 | **Memory Palace** | Complete | NONE | 12 | CRITICAL |
| 6 | **Mood System** | Complete | NONE | 9 | HIGH |
| 7 | **Rivalries/Alliances** | Complete | NONE | 14 | MEDIUM |
| 8 | **Evolution System** | Complete | NONE | 14 | HIGH |
| 9 | **Time Travel Debug** | Complete | NONE | 4 | LOW |
| 10 | **Personality Profiles** | Complete | NONE | 3 | LOW |
| 11 | **Memory Clusters** | Complete | NONE | 9 | HIGH |
| 12 | **Time Capsules** | Complete | NONE | 5 | MEDIUM |
| 13 | **Conversation Contract** | Complete | NONE | 2 | LOW |
| 14 | **Spider Integration** | Complete | Partial | 10 | DONE |

### Features Needing New UI Pages

1. **Memory Palace Dashboard** - Visualize agent memories, rooms, connections
2. **Mood Dashboard** - Real-time agent emotional states
3. **Evolution Leaderboard** - XP, levels, abilities
4. **Hive Mind Console** - Start/view collective sessions
5. **Memory Clusters Visualization** - Semantic memory graphs
6. **Relationships Graph** - Agent rivalries & alliances
7. **Time Capsules Inbox** - Future messages
8. **Mythology Quarantine** - Review blocked knowledge

---

## 6 Main UI Pages Status

### Page Connection Matrix

```
                 Assistant  Human  Agents  Intel  Body  Workspace
Assistant           -        R      N       N      R      N
Human               R        -      P       N      R      N
Agents              N        N      -       N      N      N
Intelligence        N        N      N       -      N      N
Body Health         R        R      N       N      -      R
Workspace           N        N      N       N      R      -

R = Read-only badge/card
P = Partial (can pause agents)
N = No connection
```

### Per-Page Details

#### 1. Assistant Page
- **APIs:** 12 endpoints
- **Shows:** Chat, tools, attention items, learning, body badge
- **Missing:** Agent visibility, workspace context, opportunity awareness

#### 2. Human Page
- **APIs:** 14 endpoints
- **Shows:** Attention stream, controls, paused agents, body badge
- **Missing:** Gate escalation, agent feedback, prediction context

#### 3. Agents Page
- **APIs:** 14 endpoints
- **Shows:** Agent list, executions, dreams, conversations, decisions
- **Missing:** Real-time status, workspace files, LLM routing, evolution

#### 4. Intelligence Page
- **APIs:** 18 endpoints
- **Shows:** Opportunities, gates, pilots, experiments, predictions
- **Missing:** Agent feedback, body impact, human decision link

#### 5. Body Health Page
- **APIs:** 13 endpoints
- **Shows:** 7 systems, alerts, coordination status
- **Missing:** Action controls, agent impact, predictive alerts

#### 6. Workspace Page
- **APIs:** 14 endpoints
- **Shows:** Files, git, operations, reviews, body badge
- **Missing:** Agent links, opportunity context, body governance

---

## Complete Gap Analysis

### Category 1: Cross-Page Navigation (0 connections)

| From | To | What's Missing |
|------|----|--------------------|
| Workspace | Agents | Click agent name → Agent profile |
| Workspace | Intelligence | Click operation → See source opportunity |
| Intelligence | Agents | See which agents work on opportunity |
| Intelligence | Human | Escalate critical gates |
| Agents | Workspace | See files agent modified |
| Agents | Body | See execution impact on body |
| Body | Human | Alert on critical conditions |
| Body | Intelligence | Block pilots when critical |

### Category 2: Shared State (0 shared stores)

| Data | Currently | Should Be |
|------|-----------|-----------|
| Body health | Fetched per-page | Shared store |
| Active opportunity | Not tracked | Global state |
| Pending decisions | Human page only | Shared count |
| Recent activity | Per-page fetch | Shared feed |

### Category 3: Event Broadcasting (1 WebSocket)

| Event Type | Currently | Should Be |
|------------|-----------|-----------|
| Agent completes | Not broadcast | All pages notified |
| Gate becomes critical | Not broadcast | Human page alert |
| Body goes critical | Not broadcast | All pages block |
| File modified | Not broadcast | Workspace + Agents notified |

### Category 4: Sci-Fi Features (13 missing UIs)

| Feature | Endpoints Ready | UI Status |
|---------|-----------------|-----------|
| Memory Palace | 12 | NONE |
| Memory Clusters | 9 | NONE |
| Hive Mind | 5 | NONE |
| Mood System | 9 | NONE |
| Evolution | 14 | NONE |
| Relationships | 14 | NONE |
| Time Capsules | 5 | NONE |
| Mythology | 10 | NONE |
| Consciousness | 2 | NONE |
| Time Travel | 4 | NONE |
| Personality | 3 | NONE |
| Conversation Contract | 2 | NONE |
| Spider Integration | 10 | Partial |

### Category 5: Hidden Backend APIs (97% unused)

| Domain | Endpoints | UI Exposure |
|--------|-----------|-------------|
| Revenue/Distribution | 43 | 0% |
| Learning Analytics | 35 | 5% |
| Projects Extended | 63 | 10% |
| Agents Extended | 41 | 20% |
| Monitoring | 11 | 0% |
| Legal | 26 | 0% |
| Teams | 20 | 0% |
| Marketplace | 12 | 0% |
| Autonomous | 12 | 5% |
| Collective Intelligence | 14 | 0% |

---

## Unified Human System Architecture

### Target Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIFIED HUMAN SYSTEM                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    CONSCIOUSNESS LAYER                       │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │   │
│  │  │ Shared  │  │ Event   │  │ Body    │  │ Cross-  │        │   │
│  │  │ State   │  │ Bus     │  │ Govern  │  │ Nav     │        │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│         ┌────────────────────┼────────────────────┐                │
│         │                    │                    │                │
│         ▼                    ▼                    ▼                │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐        │
│  │   BRAIN     │◄────►│    MIND     │◄────►│   NERVOUS   │        │
│  │ (Assistant) │      │  (Human)    │      │  (Intel)    │        │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘        │
│         │                    │                    │                │
│         │    ┌───────────────┼───────────────┐   │                │
│         │    │               │               │   │                │
│         ▼    ▼               ▼               ▼   ▼                │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐        │
│  │   MEMORY    │◄────►│   ORGANS    │◄────►│   SENSES    │        │
│  │ (Workspace) │      │  (Agents)   │      │ (Dashboard) │        │
│  └──────┬──────┘      └──────┬──────┘      └─────────────┘        │
│         │                    │                                     │
│         └────────────────────┼─────────────────────────────────┐  │
│                              │                                  │  │
│                              ▼                                  ▼  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                       BODY SYSTEMS                           │  │
│  │  ❤️ HEART  🫁 LUNGS  🩸 CIRC  🦴 SPINE  🛡️ IMMUNE            │  │
│  │                    🍽️ DIGEST  💪 MUSCULAR                    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                      SCI-FI LAYER                            │  │
│  │  🧠 Memory Palace  💭 Dreams  🎭 Mood  ⚔️ Relationships      │  │
│  │  📈 Evolution  🐝 Hive Mind  ⏰ Time Capsules  📜 Mythology   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Integration Layers

#### Layer 1: Shared State Store (Zustand)

```typescript
interface UnifiedSystemState {
  // Body Health (global)
  body: {
    overall: 'healthy' | 'degraded' | 'critical'
    score: number
    alerts: Alert[]
    blocksOperations: boolean
  }

  // Active Work
  activeWork: {
    opportunity: Opportunity | null
    assignedAgents: string[]
    progress: number
    pilot: Pilot | null
  }

  // Pending Decisions
  decisions: {
    criticalGates: Gate[]
    attentionItems: AttentionItem[]
    count: number
  }

  // Sci-Fi Status
  scifi: {
    hiveMindActive: boolean
    recentDreams: Dream[]
    evolutionLeaders: AgentEvolution[]
    activeMoods: Record<string, Mood>
  }

  // Navigation Context
  navigation: {
    lastAgent: string | null
    lastOpportunity: string | null
    lastWorkspace: string | null
  }
}
```

#### Layer 2: Event Bus (WebSocket)

```typescript
interface SystemEvent {
  type:
    | 'agent_execution_complete'
    | 'agent_execution_failed'
    | 'gate_became_critical'
    | 'body_status_changed'
    | 'file_modified'
    | 'pilot_started'
    | 'pilot_completed'
    | 'dream_generated'
    | 'level_up'
    | 'hive_mind_started'

  payload: any
  timestamp: string
  source: string
  affectedPages: string[]
}
```

#### Layer 3: Body Governance

```typescript
interface BodyGovernance {
  // Check before operations
  canStartPilot(): boolean
  canExecuteAgent(agentId: string): boolean
  canWriteFile(workspaceId: string): boolean
  canStartHiveMind(): boolean

  // Escalation
  escalateToHuman(reason: string, severity: 'low' | 'medium' | 'high' | 'critical'): void

  // Recovery
  requestCoordination(systems: string[]): void
  throttleSystem(level: number): void
}
```

#### Layer 4: Cross-Page Navigation

```typescript
interface NavigableEntity {
  type: 'agent' | 'opportunity' | 'file' | 'prediction' | 'gate' | 'dream' | 'memory'
  id: string
  label: string
  targetPage: string
  targetTab?: string
  context?: Record<string, any>
}

// Usage: <EntityLink entity={entity} />
// Renders clickable link that navigates with context
```

---

## Integration Roadmap

### Phase 1: Foundation (Body Governance + Alerts)

**Goal:** Make body health ACTIONABLE, not just viewable

**Duration:** 1-2 sessions

#### Tasks

1. **Global Body Alert Banner**
   - Add to all page layouts
   - Shows critical alerts with dismiss
   - Links to Body Health page

2. **Body Governance Service**
   ```typescript
   // frontend/src/services/bodyGovernance.ts
   export const bodyGovernance = {
     canStartPilot: () => bodyStore.overall !== 'critical',
     canExecuteAgent: (id) => bodyStore.muscular.status !== 'paralyzed',
     canWriteFile: (ws) => bodyStore.spine.status !== 'critical',
   }
   ```

3. **Operation Blocking**
   - Intelligence page: Block "Start Pilot" when body critical
   - Workspace page: Warn before writes when body degraded
   - Agents page: Show body impact on agent cards

4. **Shared Body State**
   ```typescript
   // frontend/src/stores/bodyStore.ts
   export const useBodyStore = create<BodyState>((set) => ({
     vitals: null,
     alerts: [],
     blocksOperations: false,
     fetchVitals: async () => {...},
   }))
   ```

#### Deliverables
- [ ] `frontend/src/components/GlobalAlertBanner.tsx`
- [ ] `frontend/src/services/bodyGovernance.ts`
- [ ] `frontend/src/stores/bodyStore.ts`
- [ ] Updated Intelligence page with body checks
- [ ] Updated Workspace page with body warnings

---

### Phase 2: Cross-Page Navigation

**Goal:** Every entity clickable, navigates to correct page

**Duration:** 1-2 sessions

#### Tasks

1. **EntityLink Component**
   ```typescript
   // frontend/src/components/EntityLink.tsx
   interface EntityLinkProps {
     type: 'agent' | 'opportunity' | 'file' | 'dream' | 'memory'
     id: string
     label: string
     className?: string
   }
   ```

2. **Navigation Context Store**
   ```typescript
   // frontend/src/stores/navigationStore.ts
   export const useNavigationStore = create<NavigationState>((set) => ({
     fromPage: null,
     context: {},
     setContext: (ctx) => set({ context: ctx }),
   }))
   ```

3. **Update All Pages**
   | Page | Add Links To |
   |------|--------------|
   | Workspace | Agent profiles (from operations) |
   | Workspace | Opportunities (from file context) |
   | Intelligence | Agent profiles (from opportunity) |
   | Intelligence | Human page (from gates) |
   | Agents | Workspace (files modified) |
   | Agents | Intelligence (opportunities worked) |
   | Body | Agents (causing strain) |

4. **Breadcrumb Navigation**
   - Add "Back to X" when navigating with context
   - Preserve scroll position

#### Deliverables
- [ ] `frontend/src/components/EntityLink.tsx`
- [ ] `frontend/src/stores/navigationStore.ts`
- [ ] Updated Workspace page with agent links
- [ ] Updated Intelligence page with agent links
- [ ] Updated Agents page with workspace/intel links
- [ ] Breadcrumb component

---

### Phase 3: Event Broadcasting

**Goal:** Real-time updates across all pages

**Duration:** 1-2 sessions

#### Tasks

1. **System Event WebSocket**
   ```python
   # core/consumers/system_events_consumer.py
   class SystemEventsConsumer(AsyncWebsocketConsumer):
       async def connect(self):
           await self.channel_layer.group_add("system_events", self.channel_name)
           await self.accept()

       async def system_event(self, event):
           await self.send(json.dumps(event))
   ```

2. **Event Emitters (Backend)**
   ```python
   # Add to core/tasks.py after agent execution
   async_to_sync(channel_layer.group_send)(
       "system_events",
       {
           "type": "system.event",
           "event_type": "agent_execution_complete",
           "agent_id": str(agent.id),
           "success": result.success,
           "timestamp": now().isoformat(),
       }
   )
   ```

3. **Event Listeners (Frontend)**
   ```typescript
   // frontend/src/hooks/useSystemEvents.ts
   export function useSystemEvents(handler: (event: SystemEvent) => void) {
     const ws = useRef<WebSocket | null>(null)

     useEffect(() => {
       ws.current = new WebSocket('/ws/system-events/')
       ws.current.onmessage = (e) => handler(JSON.parse(e.data))
       return () => ws.current?.close()
     }, [])
   }
   ```

4. **Page Subscriptions**
   | Page | Listens For |
   |------|-------------|
   | All | body_status_changed |
   | Intelligence | agent_execution_complete, pilot_started |
   | Agents | agent_execution_complete, level_up, dream_generated |
   | Workspace | file_modified |
   | Human | gate_became_critical |
   | Dashboard | All events (activity feed) |

#### Deliverables
- [ ] `core/consumers/system_events_consumer.py`
- [ ] `core/routing.py` update
- [ ] Event emission in `core/tasks.py`
- [ ] `frontend/src/hooks/useSystemEvents.ts`
- [ ] Page-specific event handlers

---

### Phase 4: Shared State Store

**Goal:** Pages share data, reduce duplicate API calls

**Duration:** 1-2 sessions

#### Tasks

1. **Unified Store**
   ```typescript
   // frontend/src/stores/unifiedStore.ts
   interface UnifiedStore {
     // Body (from Phase 1)
     body: BodyState

     // Active work
     activeOpportunity: Opportunity | null
     activePilot: Pilot | null
     assignedAgents: string[]

     // Decisions
     pendingDecisions: number
     criticalGates: Gate[]

     // Recent activity
     recentEvents: SystemEvent[]

     // Actions
     setActiveOpportunity: (opp: Opportunity | null) => void
     addEvent: (event: SystemEvent) => void
   }
   ```

2. **Migrate Pages to Shared State**
   - Body vitals: All pages use `useBodyStore`
   - Pending decisions: Badge on all pages from shared count
   - Active opportunity: Show in sidebar across pages

3. **Optimistic Updates**
   - When starting pilot, immediately update shared state
   - When pausing agent, immediately update agent list
   - Rollback on API failure

4. **Cache Invalidation**
   - Event triggers refetch of affected queries
   - Example: `agent_execution_complete` → refetch agent list

#### Deliverables
- [ ] `frontend/src/stores/unifiedStore.ts`
- [ ] Migrate body state to shared store
- [ ] Add pending decisions badge to header
- [ ] Add active opportunity sidebar
- [ ] Optimistic update patterns

---

### Phase 5: Sci-Fi Features UI

**Goal:** Expose the 13 hidden sci-fi features

**Duration:** 3-5 sessions

#### Sub-Phase 5A: Memory System (Critical)

1. **Memory Palace Page**
   - Agent memory browser
   - Room visualization (7 room types)
   - Memory connections graph
   - Search with semantic similarity

2. **Memory Clusters Page**
   - Cluster visualization
   - Coherence scoring
   - Cross-agent clusters

#### Sub-Phase 5B: Agent Enhancement

3. **Evolution Dashboard**
   - XP leaderboard
   - Level progression
   - Ability showcase
   - Recent XP gains

4. **Mood Dashboard**
   - Real-time mood grid
   - Mood history charts
   - Trigger rules management

5. **Relationships Graph**
   - Rivalries & alliances visualization
   - Collaboration success rates
   - Mentor/student connections

#### Sub-Phase 5C: Collective Intelligence

6. **Hive Mind Console**
   - Start new session
   - View active sessions
   - Synthesis results

7. **Time Capsules Inbox**
   - Pending capsules
   - Opened capsules
   - Create new capsule

#### Sub-Phase 5D: Governance

8. **Mythology Quarantine**
   - Blocked knowledge review
   - Approve/reject interface
   - Source tracing

#### Deliverables (Per Feature)
- [ ] API bindings in `frontend/src/lib/api.ts`
- [ ] New page in `frontend/src/pages/`
- [ ] Route in `frontend/src/App.tsx`
- [ ] Sidebar link

---

## Detailed Workflows

### Workflow 1: Gate Escalation to Human

```
1. Gate becomes critical (passed deadline, failed items)
2. Backend emits: gate_became_critical event
3. Human page receives event
4. Alert banner shows: "Critical gate needs attention"
5. User clicks → navigates to Human page Attention tab
6. Gate details shown with approve/reject options
7. Decision recorded → event emitted
8. Intelligence page updates gate status
```

### Workflow 2: Agent Execution → Workspace Update

```
1. Agent executes task
2. Agent writes file via SKIN layer
3. Backend emits: file_modified event
4. Workspace page receives event
5. File tree highlights modified file
6. Operations list shows new entry
7. User can click agent name → Agents page
8. User can see opportunity context → Intelligence page
```

### Workflow 3: Body Critical → Operation Block

```
1. Body health drops to critical
2. Backend emits: body_status_changed event
3. All pages receive event
4. Global alert banner appears (red)
5. Intelligence page: "Start Pilot" button disabled
6. Workspace page: File writes show warning
7. Human page: "Body critical" attention item created
8. User addresses issue → body recovers → operations unblocked
```

### Workflow 4: Hive Mind Session

```
1. User navigates to Hive Mind Console (new page)
2. Selects agents and problem
3. Body governance check: system healthy?
4. Session started → hive_mind_started event
5. Progress shown in real-time
6. Synthesis completed → dream_generated events
7. Results navigable to Dreams gallery
8. Insights can create new Opportunities
```

### Workflow 5: Agent Evolution Level Up

```
1. Agent completes high-quality task
2. XP awarded → level_up event (if threshold crossed)
3. Evolution Dashboard shows celebration
4. Agent card shows new level badge
5. New abilities unlocked (shown in ability showcase)
6. Leaderboard updates
```

---

## API Inventory

### Currently Used APIs (45)

```typescript
// Body (4)
bodyApi.vitals()
bodyApi.alerts()
bodyApi.history()
bodyApi.summary()

// Agents (14)
agentsApi.comprehensive()
agentsApi.health()
agentsApi.executionHistory()
dreamsApi.list()
dreamsApi.detail()
dreamsApi.react()
conversationsApi.list()
conversationsApi.detail()
decisionsApi.list()
decisionsApi.detail()
experimentsApi.list()
activityApi.recent()
activityApi.learning()

// Intelligence (18)
intelligenceApi.status()
opportunitiesApi.list()
opportunitiesApi.detail()
opportunitiesApi.act()
opportunitiesApi.dismiss()
pilotsApi.dashboard()
pilotsApi.gates()
pilotsApi.gateDetail()
pilotsApi.updateGateStatus()
pilotsApi.approveAllItems()
pilotsApi.startPilot()
pilotsApi.implementationDetail()
experimentsApi.portfolio()
experimentsApi.updateKpi()
experimentsApi.complete()
experimentsApi.halt()
spidersApi.status()
intelligenceApi.predictions()

// Human (14)
humanApi.attention()
humanApi.attentionStats()
humanApi.decide()
humanApi.control()
humanApi.pauseAgent()
humanApi.resumeAgent()
humanApi.setQuietMode()
humanApi.setReviewMode()
humanApi.adjustThreshold()
humanApi.preferences()
humanApi.updatePreferences()

// Workspace (14)
workspaceApi.list()
workspaceApi.getActive()
workspaceApi.dashboard()
workspaceApi.stats()
workspaceApi.files()
workspaceApi.readFile()
workspaceApi.writeFile()
workspaceApi.gitStatus()
workspaceApi.gitCommit()
workspaceApi.gitBranch()
workspaceApi.operations()
workspaceOperationsApi.list()
workspaceOperationsApi.detail()
workspaceOperationsApi.rollback()
workspaceOperationsApi.review()
workspaceOperationsApi.pendingReviews()

// Assistant (12)
assistantApi.getAttentionItems()
assistantApi.getLearning()
assistantApi.chat()
assistantApi.transcribe()
assistantApi.feedback()
assistantApi.reset()
userLearningApi.getAllPreferences()
userLearningApi.getStyleEvolution()
userLearningApi.getInsights()
userLearningApi.getVelocity()
userLearningApi.generateInsights()
```

### APIs to Add (Sci-Fi)

```typescript
// Memory Palace (12)
memoryPalaceApi.overview()
memoryPalaceApi.agentMemories(agentId)
memoryPalaceApi.agentRooms(agentId)
memoryPalaceApi.agentSummary(agentId)
memoryPalaceApi.memoryDetail(memoryId)
memoryPalaceApi.deleteMemory(memoryId)
memoryPalaceApi.memoryConnections(memoryId)
memoryPalaceApi.roomMemories(roomId)
memoryPalaceApi.createMemory(data)
memoryPalaceApi.searchMemories(query)
memoryPalaceApi.assignToRoom(memoryId, roomId)
memoryPalaceApi.connectMemories(id1, id2)

// Memory Clusters (9)
memoryClustersApi.overview()
memoryClustersApi.agentClusters(agentId)
memoryClustersApi.clusterDetail(clusterId)
memoryClustersApi.visualization()
memoryClustersApi.generateAll()
memoryClustersApi.addMemory(clusterId, memoryId)
memoryClustersApi.removeMemory(clusterId, memoryId)
memoryClustersApi.evolution(agentId)
memoryClustersApi.findSimilar(clusterId)

// Evolution (14)
evolutionApi.overview()
evolutionApi.agentDetail(agentId)
evolutionApi.awardXP(agentId, amount)
evolutionApi.prestige(agentId)
evolutionApi.recordTask(agentId, data)
evolutionApi.unlockAbility(agentId, abilityId)
evolutionApi.abilities()
evolutionApi.createAbility(data)
evolutionApi.leaderboard()
evolutionApi.recentXPGains()
evolutionApi.initialize()

// Mood (9)
moodApi.overview()
moodApi.agentMood(agentId)
moodApi.setMood(agentId, mood)
moodApi.history(agentId)
moodApi.promptContext(agentId)
moodApi.rules()
moodApi.createRule(data)
moodApi.deleteRule(ruleId)
moodApi.triggerFromMemory(data)

// Hive Mind (5)
hiveMindApi.start(data)
hiveMindApi.session(sessionId)
hiveMindApi.sessions()
hiveMindApi.availableAgents()
hiveMindApi.previewAgents(agentIds)

// Relationships (14)
relationshipsApi.list()
relationshipsApi.agentRelationships(agentId)
relationshipsApi.alliances()
relationshipsApi.allianceDetail(id)
relationshipsApi.createAlliance(data)
relationshipsApi.rivalries()
relationshipsApi.rivalryDetail(id)
relationshipsApi.createRivalry(data)
relationshipsApi.compete(rivalryId)

// Time Capsules (5)
timeCapsuleApi.list()
timeCapsuleApi.pending()
timeCapsuleApi.create(data)
timeCapsuleApi.open(id)
timeCapsuleApi.react(id, reaction)

// Mythology (10)
mythologyApi.dashboard()
mythologyApi.flaggedContent()
mythologyApi.flaggedDetail(id)
mythologyApi.submitReview(id, data)
mythologyApi.recentEvents()
mythologyApi.report(data)
mythologyApi.quarantine()
mythologyApi.quarantineStats()
mythologyApi.quarantineDetail(id)
mythologyApi.approveQuarantine(id)
mythologyApi.rejectQuarantine(id)
```

---

## Implementation Checklist

### Phase 1 Checklist ✅ COMPLETE (Session 713)
- [x] Create `frontend/src/stores/bodyStore.ts`
- [x] Create `frontend/src/services/bodyGovernance.ts`
- [x] Create `frontend/src/components/GlobalAlertBanner.tsx`
- [x] Add GlobalAlertBanner to layout
- [x] Update Intelligence page with body checks
- [x] Update Workspace page with body warnings
- [x] Test body critical blocking

### Phase 2 Checklist ✅ COMPLETE (Session 713)
- [x] Create `frontend/src/components/EntityLink.tsx`
- [x] Create `frontend/src/stores/navigationStore.ts`
- [x] Add agent links to Workspace operations
- [x] Add agent links to Intelligence opportunities
- [x] Add workspace links to Agents page
- [x] Add breadcrumb component
- [x] Test navigation flows

### Phase 3 Checklist (Session 714) - COMPLETE
- [x] Create `core/consumers/system_events_consumer.py`
- [x] Update `core/routing.py` with new consumer
- [x] Add event emission to `core/tasks.py`
- [x] Create `useSystemEvents` hook in `frontend/src/hooks/useWebSocket.ts`
- [x] Add event handlers to IntelligencePage, AgentsPage, WorkspacePage
- [x] Add event handlers to DashboardPage, HumanPage

### Phase 4 Checklist
- [ ] Create `frontend/src/stores/unifiedStore.ts`
- [ ] Migrate body state to unified store
- [ ] Add pending decisions badge
- [ ] Add active opportunity sidebar
- [ ] Implement optimistic updates
- [ ] Test cache invalidation

### Phase 5 Checklist

#### 5A: Memory
- [ ] Add memory palace APIs to `api.ts`
- [ ] Create `MemoryPalacePage.tsx`
- [ ] Create `MemoryClustersPage.tsx`
- [ ] Add routes and sidebar links

#### 5B: Agent Enhancement
- [ ] Add evolution APIs to `api.ts`
- [ ] Create `EvolutionPage.tsx`
- [ ] Add mood APIs to `api.ts`
- [ ] Create `MoodDashboardPage.tsx`
- [ ] Add relationships APIs to `api.ts`
- [ ] Create `RelationshipsPage.tsx`

#### 5C: Collective
- [ ] Add hive mind APIs to `api.ts`
- [ ] Create `HiveMindPage.tsx`
- [ ] Add time capsules APIs to `api.ts`
- [ ] Create `TimeCapsulePage.tsx`

#### 5D: Governance
- [ ] Add mythology APIs to `api.ts`
- [ ] Create `MythologyPage.tsx`

---

## Success Metrics

| Metric | Start | Phase 1 ✅ | Phase 2 ✅ | Phase 3 ✅ | Phase 4 | Phase 5 |
|--------|-------|-----------|-----------|---------|---------|---------|
| Cross-page links | 0 | 0 | **10+** | **10+** | 20+ | 30+ |
| Shared state stores | 0 | **2** | **3** | **3** | 4 | 4 |
| Event types broadcast | 1 | 1 | 1 | **10** | 10+ | 15+ |
| Backend API utilization | 3% | **5%** | **7%** | **8%** | 12% | 25% |
| Sci-Fi features in UI | 1 | 1 | 1 | 1 | 1 | 9 |
| Body governance active | No | **Yes** | **Yes** | **Yes** | Yes | Yes |
| Pages with real-time events | 0 | 0 | 0 | **5** | 5 | 6 |

**Current Status (After Phase 3):**
- 3 shared Zustand stores: `bodyStore`, `navigationStore`, `unifiedStore` (partial)
- 10 system event types: agent_execution, pilot lifecycle, dreams, hive mind, gates, body, files
- 10+ cross-page navigation links via EntityLink component
- Body governance blocking operations when critical
- Breadcrumb navigation showing context

---

## Quick Reference

### Files to Create (Phase 1-4)

```
frontend/src/
├── stores/
│   ├── bodyStore.ts
│   ├── navigationStore.ts
│   └── unifiedStore.ts
├── services/
│   └── bodyGovernance.ts
├── components/
│   ├── GlobalAlertBanner.tsx
│   └── EntityLink.tsx
└── hooks/
    └── useSystemEvents.ts

core/
└── consumers/
    └── system_events_consumer.py
```

### Files to Create (Phase 5)

```
frontend/src/pages/
├── MemoryPalacePage.tsx
├── MemoryClustersPage.tsx
├── EvolutionPage.tsx
├── MoodDashboardPage.tsx
├── RelationshipsPage.tsx
├── HiveMindPage.tsx
├── TimeCapsulePage.tsx
└── MythologyPage.tsx
```

---

**This document is the master reference for the Unified Human System integration.**

**Do not lose this context. All workflows, checklists, and architectures are captured here.**

---

*Created: Session 713, January 7, 2026*
*Last Updated: Session 713*
