# UI Gaps: Complete System Frontend Audit

**Sessions:** 728 (agents migration), 731 (deep audit verification)
**Updated:** January 7, 2026
**Status:** Comprehensive frontend API gap documentation

---

## Overview

This document tracks ALL backend APIs that have NO corresponding frontend UI. These are fully functional backend features waiting for frontend exposure.

**Gap Summary (Session 734 Update):**

| System | Backend APIs | Frontend | Priority |
|--------|--------------|----------|----------|
| **RAG/Documents** | 6 endpoints | ✅ COMPLETE | DONE |
| **Mythology Lab** | 11 endpoints | ✅ COMPLETE | DONE |
| **Agent Channels** | 10 endpoints | ✅ COMPLETE | DONE |
| **Intelligence/Income** | 15+ endpoints | ✅ COMPLETE | DONE |
| **Agent Monitoring** | 6 endpoints | ✅ COMPLETE | DONE |
| **Agent Templates CRUD** | 5 endpoints | ✅ COMPLETE | DONE |
| **Agent Orchestrations** | 6 endpoints | ✅ COMPLETE | DONE |
| **Agent Tools** | 5 endpoints | ✅ COMPLETE | DONE |

---

## COMPLETED (Session 732-734)

### RAG/Document Embedding System - DONE

**Status:** ✅ Implemented in Session 732

**Implementation:**
- `ragApi` added to `frontend/src/lib/api.ts` (13 endpoints)
- `DocumentsPage.tsx` created (~600 lines)
- Route `/documents` added to `App.tsx`
- Navigation link added to `Sidebar.tsx`

**Features Delivered:**
- Document upload with drag-and-drop
- Semantic search interface with similarity scores
- Statistics dashboard (embeddings, documents, collections, chunks, storage)
- Document list with status badges and delete
- Collection organization support
- Storage optimization button

---

### Mythology Lab - DONE

**Status:** ✅ Implemented in Sessions 733-734

**Implementation:**
- `mythologyApi` added to `frontend/src/lib/api.ts` (11 endpoints)
- `MythologyLabPage.tsx` created (~900 lines)
- Route `/mythology-lab` added to `App.tsx`
- Navigation link added to `Sidebar.tsx`

**Features Delivered (Session 734 - Rich Data Display):**
- **Primary Stats:** Total Flagged, Pending Review, High Priority, Resolved Today
- **Neural Processing Stats:** Total Processed, Events/Hour, Prevention Rate, Avg Risk Score, False Positive Rate, Active Patterns
- **Secondary Stats:** Recent Events (24h), Unacknowledged Alerts, Avg Review Time, System Efficiency
- **Events Tab:** Risk level badges, mutation types, prevention status, patterns detected, confidence scores, content preview
- **Quarantine Tab:** Teacher→Student agent flow, violation types & counts, mythology warnings, violation patterns, spider sources, blocked content, approve/reject actions

**Smart Content Formatting (Session 734 - Final Polish):**
- `formatMythologyContent()` helper automatically cleans messy content:
  - Extracts source headers → cyan badges (e.g., "Venturebeat", "Gumroad")
  - Removes "Learned from X:" chains → blue agent badges
  - Cleans "Aggregated X data points" noise
- 15 pattern types with human-readable labels and icons (time_myth → "⏰ Time Claim")
- Content Analysis section with source + agents + clean content
- Collapsible "View Raw Original Content" for debugging
- Technical regex patterns filtered from metadata display

**Backend Endpoints Connected:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/mythology/stats/` | GET | Dashboard statistics (16 fields) |
| `/api/v1/mythology/recent-events/` | GET | Events with mutation_type, risk_level, prevention |
| `/api/v1/mythology/quarantine/` | GET | Teacher/student, violations, spider sources |
| `/api/v1/mythology/quarantine/{id}/approve/` | POST | Approve as false positive |
| `/api/v1/mythology/quarantine/{id}/reject/` | POST | Reject as confirmed myth |

---

## HIGH PRIORITY GAPS

### 1. Intelligence/Income Builder System (Session 729)

**Backend:** 41 ActionPlans, Income Builder fully functional

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/intelligence/income-builder/` | GET | Income analysis |
| `/api/v1/intelligence/income-builder/action-plan/` | GET/POST | Action plan management |
| `/api/v1/intelligence/income-builder/plans/` | GET | List persisted plans |
| `/api/v1/intelligence/income-builder/execute/` | POST | Execute action plan |
| `/api/v1/intelligence/revenue/opportunities/` | GET | Revenue opportunities |
| `/api/v1/intelligence/revenue/metrics/` | GET | Revenue metrics |
| `/api/v1/intelligence/automation/workflows/` | GET | Automation workflows |
| `/api/v1/intelligence/automation/execute/` | POST | Execute automation |

**Current Frontend:** `intelligenceApi` has basic status/opportunities but missing Income Builder

**Frontend API Addition Needed:**
```typescript
// Add to intelligenceApi
export const incomeBuilderApi = {
  analyze: () => api.get('/v1/intelligence/income-builder/'),
  getActionPlan: () => api.get('/v1/intelligence/income-builder/action-plan/'),
  createActionPlan: (data: { opportunity_id?: string; focus_area?: string }) =>
    api.post('/v1/intelligence/income-builder/action-plan/', data),
  listPlans: () => api.get('/v1/intelligence/income-builder/plans/'),
  executePlan: (planId: string) =>
    api.post('/v1/intelligence/income-builder/execute/', { plan_id: planId }),
  revenueOpportunities: () => api.get('/v1/intelligence/revenue/opportunities/'),
  revenueMetrics: () => api.get('/v1/intelligence/revenue/metrics/'),
  automationWorkflows: () => api.get('/v1/intelligence/automation/workflows/'),
  executeAutomation: (workflowId: string) =>
    api.post('/v1/intelligence/automation/execute/', { workflow_id: workflowId }),
};
```

**UI Enhancement Needed:** Add Income Builder tab to `IntelligencePage.tsx`

---

## Agent Channels ("Slack for AI Agents") - DONE

**Status:** ✅ Implemented in Session 734

### What It Is
A full communication system for AI agents, similar to Slack:
- **Channels** - Topic-based communication rooms
- **Messages** - Threaded conversations with reactions
- **Memberships** - Access control and roles

### Current Data
```
AgentChannel: 2 records
ChannelMessage: 0 records
ChannelMembership: 5 records
```

### Implementation (Session 734)
- `agentChannelsApi` added to `frontend/src/lib/api.ts` (12 endpoints)
- `ChannelsTab` component added to `AgentsPage.tsx` (~300 lines)
- Accessible via Agents → Channels tab (no new route needed)

**Features Delivered:**
- **Channel List:** Type badges (project/topic/team), member count, descriptions
- **Message Thread:** Real-time message display, sender info, timestamps
- **Members Panel:** Agent list with presence indicators (online/busy/offline)
- **Message Input:** Send messages with Enter key support
- **Responsive Layout:** 3-column grid on desktop, stacked on mobile

### Backend APIs Connected
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/agents/channels/` | GET | List all channels |
| `/api/v1/agents/channels/` | POST | Create channel |
| `/api/v1/agents/channels/{id}/` | GET | Channel detail |
| `/api/v1/agents/channels/{id}/join/` | POST | Join channel |
| `/api/v1/agents/channels/{id}/leave/` | POST | Leave channel |
| `/api/v1/agents/messages/` | GET | List messages |
| `/api/v1/agents/messages/` | POST | Send message |
| `/api/v1/agents/memberships/` | GET | List memberships |
| `/api/v1/agents/memberships/` | POST | Add member |

---

## Agent Tools Registry - DONE

**Status:** ✅ Implemented in Session 734

### What It Is
A registry of tools available to AI agents for task execution:
- **Tools** - External services, APIs, and capabilities agents can use
- **Configuration** - Tool-specific settings and parameters
- **Usage Stats** - Tracking of tool usage, success rates, response times

### Implementation (Session 734)
- `agentToolsApi` added to `frontend/src/lib/api.ts` (5 endpoints)
- `ToolsTab` component added to `AgentsPage.tsx` (~160 lines)
- Accessible via Agents → Tools tab (no new route needed)

**Features Delivered:**
- **Tool List:** Filterable by tool type (dropdown)
- **Tool Cards:** Display name, type, active status, usage stats
- **Stats Display:** Usage count, success rate, avg response time
- **Endpoint Info:** URL and supported operations count
- **Empty State:** Friendly message when no tools configured

### Backend APIs Connected
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/agents/tools/` | GET | List all tools |
| `/api/v1/agents/tools/` | POST | Create tool |
| `/api/v1/agents/tools/{id}/` | GET | Tool detail |
| `/api/v1/agents/tools/{id}/` | PATCH | Update tool |
| `/api/v1/agents/tools/{id}/` | DELETE | Delete tool |

---

## Agent Templates CRUD - DONE

**Status:** ✅ Implemented in Session 734

### What It Is
Full CRUD management for agent templates - reusable configurations for AI agents:
- **Create** - New templates with full configuration
- **Edit** - Update existing template settings
- **Delete** - Remove templates with confirmation
- **List** - Browse with search and specialization filter

### Implementation (Session 734)
- `agentTemplatesApi` added to `frontend/src/lib/api.ts` (5 endpoints)
- `TemplatesTab` component added to `AgentsPage.tsx` (~450 lines)
- Create/Edit modal with full form fields
- Accessible via Agents → Templates tab (no new route needed)

**Features Delivered:**
- **Template Cards:** Display name, specialization, usage stats, success rate, rating
- **Search & Filter:** Text search + specialization dropdown
- **Create Modal:** All template fields (name, description, system prompt, LLM config, etc.)
- **Edit/Delete:** Inline buttons on each card with confirmation
- **Visual Indicators:** Verified badge, public/private icons

### Backend APIs Connected
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/agents/templates/` | GET | List templates with filters |
| `/api/v1/agents/templates/` | POST | Create new template |
| `/api/v1/agents/templates/{id}/` | GET | Template detail |
| `/api/v1/agents/templates/{id}/` | PATCH | Update template |
| `/api/v1/agents/templates/{id}/` | DELETE | Delete template |

---

## Medium Priority Gaps

---

### ~~2. Agent Orchestrations Management~~ - DONE (Session 734)

**Status:** ✅ Implemented in Session 734

### What It Is
Multi-agent workflow coordination - orchestrations define sequences of agents working together:
- **Create** - Define new orchestration workflows
- **Edit** - Update orchestration configuration
- **Execute** - Run orchestration workflows
- **Monitor** - Track progress and status

### Implementation (Session 734)
- `agentOrchestrationsApi` added to `frontend/src/lib/api.ts` (6 endpoints)
- `OrchestrationsTab` component added to `AgentsPage.tsx` (~350 lines)
- Create/Edit modal with execution strategy selection
- Accessible via Agents → Orchestrations tab

**Features Delivered:**
- **Orchestration Cards:** Name, status, strategy, agent sequence preview
- **Status Indicators:** Pending/Running/Completed/Failed/Cancelled with icons
- **Progress Bar:** Real-time progress for running orchestrations
- **Execute Button:** Launch pending orchestrations
- **4 Strategies:** Sequential, Parallel, Conditional, Pipeline
- **Stats Display:** Execution count, total time, cost

### Backend APIs Connected
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/agents/orchestrations/` | GET | List with status filter |
| `/api/v1/agents/orchestrations/` | POST | Create orchestration |
| `/api/v1/agents/orchestrations/{id}/` | GET | Orchestration detail |
| `/api/v1/agents/orchestrations/{id}/` | PATCH | Update orchestration |
| `/api/v1/agents/orchestrations/{id}/` | DELETE | Delete orchestration |
| `/api/v1/agents/orchestrations/{id}/execute/` | POST | Execute orchestration |

---

### ~~3. Agent Tools Registry~~ - DONE (Session 734)

**Status:** ✅ Moved to Completed section - See "Agent Tools Registry - DONE" above

---

### 3. Agent Monitoring Dashboard

**Backend:** Multiple endpoints at `/api/v1/agents/monitoring/`
- `/monitoring/dashboard/` - Metrics dashboard
- `/monitoring/agent/{name}/` - Agent performance
- `/monitoring/report/` - Performance report
- `/monitoring/real-time/` - Real-time metrics
- `/monitoring/alerts/` - Alert status

**Current Frontend:** Basic health via `adminApi.agentHealth()`

**Missing:**
- Dedicated monitoring dashboard
- Per-agent performance graphs
- Alert configuration
- Real-time metrics streaming

**Frontend API Addition:**
```typescript
export const agentMonitoringApi = {
  dashboard: () => api.get('/v1/agents/monitoring/dashboard/'),
  agentPerformance: (agentName: string) =>
    api.get(`/v1/agents/monitoring/agent/${agentName}/`),
  report: () => api.get('/v1/agents/monitoring/report/'),
  realTime: () => api.get('/v1/agents/monitoring/real-time/'),
  alerts: () => api.get('/v1/agents/monitoring/alerts/'),
  clearCache: () => api.post('/v1/agents/monitoring/cache/clear/'),
}
```

---

## Low Priority Gaps

### 1. Agent Registry (Read-Only)

**Backend:** `AgentRegistryViewSet` at `/api/v1/agents/registry/`

**Current Frontend:** Available via comprehensive endpoint

**Missing:** Dedicated registry browser UI

---

### 2. Game Executions

**Backend:** `game_executions` at `/api/v1/agents/game/{game_id}/executions/`

**Current Frontend:** Used in BettingPage but could be enhanced

---

## Implementation Recommendations

### Phase 1: Agent Channels (High Priority)
1. Add `agentChannelsApi` to `frontend/src/lib/api.ts`
2. Create `AgentChannelsPage.tsx` with:
   - Channel list with search
   - Message thread viewer
   - Member management
   - Create channel modal
3. Add route to `App.tsx`
4. Add navigation item

### Phase 2: Agent Management (Medium Priority)
1. Enhance `AgentsPage.tsx` with:
   - Template CRUD buttons
   - Orchestration creation
   - Tool configuration
2. Add `AgentDetailPage.tsx` for per-agent management

### Phase 3: Monitoring Dashboard (Medium Priority)
1. Create `AgentMonitoringPage.tsx`
2. Add real-time metrics visualization
3. Alert configuration UI

---

## Related Files

| File | Purpose |
|------|---------|
| `core/views/agents.py` | Backend ViewSets (migrated from agents/) |
| `agents/urls.py` | URL routing for agent APIs |
| `frontend/src/lib/api.ts` | Frontend API definitions |
| `frontend/src/pages/AgentsPage.tsx` | Current agents page |

---

## Summary (Updated Session 734)

| Feature | Backend | Frontend | Data | Priority |
|---------|---------|----------|------|----------|
| **RAG/Documents** | ✅ 6 endpoints | ✅ COMPLETE | ✅ 7,239 embeddings | **DONE** |
| **Mythology Lab** | ✅ 11 endpoints | ✅ COMPLETE | ✅ 10 patterns, 56 events | **DONE** |
| **Agent Channels** | ✅ 12 endpoints | ✅ COMPLETE | ✅ 1 channel, 5 members | **DONE** |
| **Income Builder** | ✅ 10 endpoints | ✅ COMPLETE | ✅ 150 revenue plans | **DONE** |
| **Agent Monitoring** | ✅ 6 endpoints | ✅ COMPLETE | N/A (metrics) | **DONE** |
| **Agent Templates CRUD** | ✅ 5 endpoints | ✅ COMPLETE | ✅ Has data | **DONE** |
| **Agent Orchestrations** | ✅ 6 endpoints | ✅ COMPLETE | ✅ Has data | **DONE** |
| **Agent Tools** | ✅ 5 endpoints | ✅ COMPLETE | ✅ Has data | **DONE** |
| Agent Registry | ✅ 5 endpoints | ⚠️ Partial | ✅ Has data | LOW |

**Total: 9 systems with 58+ backend API endpoints with frontend exposure** (8 completed: RAG, Mythology, Agent Channels, Income Builder, Agent Monitoring, Agent Tools, Agent Templates, Agent Orchestrations)

---

## Implementation Priority Order

1. ~~**RAG/Documents** - DONE (Session 732)~~
2. ~~**Mythology Lab** - DONE (Sessions 733-734)~~
3. ~~**Agent Channels** - DONE (Session 734) - "Slack for AI Agents" tab in AgentsPage~~
4. ~~**Income Builder** - DONE (Session 734) - "Income Builder" tab in IntelligencePage~~
5. ~~**Agent Monitoring** - DONE (Session 734) - "Monitoring" tab in AgentsPage~~
6. ~~**Agent Tools** - DONE (Session 734) - "Tools" tab in AgentsPage~~
7. ~~**Agent Templates** - DONE (Session 734) - "Templates" tab in AgentsPage~~
8. ~~**Agent Orchestrations** - DONE (Session 734) - "Orchestrations" tab in AgentsPage~~
9. **Agent Registry** - LOW - Read-only registry browser

---

## Verification Status (Session 731)

All systems verified operational via shell commands:
- ✅ pgvector embeddings working (9 models, 9 HNSW indexes)
- ✅ Mythology patterns seeded (10 patterns)
- ✅ Intelligence ActionPlans populating (41 records)
- ✅ Agent Channels ready (2 channels, 5 memberships)
- ✅ Body Systems APIs exposed (10 systems)
- ✅ Memory Clusters connected (6 clusters, 843 memories)
