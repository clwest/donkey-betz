# UI Gaps: agents/ Migration to core/

**Session:** 728
**Date:** January 7, 2026
**Status:** Documentation of frontend APIs needed

---

## Overview

The Session 728 migration of `agents/` to `core/` revealed several backend APIs that have NO corresponding frontend UI. These are fully functional backend features waiting for frontend exposure.

---

## Critical Gap: Agent Channels ("Slack for AI Agents")

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

### Backend APIs (Fully Functional)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/agents/channels/` | GET | List all channels |
| `/api/v1/agents/channels/` | POST | Create channel |
| `/api/v1/agents/channels/{id}/` | GET | Channel detail |
| `/api/v1/agents/channels/{id}/` | PUT/PATCH | Update channel |
| `/api/v1/agents/channels/{id}/` | DELETE | Delete channel |
| `/api/v1/agents/messages/` | GET | List messages |
| `/api/v1/agents/messages/` | POST | Send message |
| `/api/v1/agents/messages/{id}/` | GET | Message detail |
| `/api/v1/agents/memberships/` | GET | List memberships |
| `/api/v1/agents/memberships/` | POST | Add member |

### Frontend API Needed (`frontend/src/lib/api.ts`)
```typescript
export const agentChannelsApi = {
  // Channels
  list: () => api.get('/v1/agents/channels/'),
  create: (data: { name: string; description?: string; channel_type?: string }) =>
    api.post('/v1/agents/channels/', data),
  detail: (id: string) => api.get(`/v1/agents/channels/${id}/`),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/v1/agents/channels/${id}/`, data),
  delete: (id: string) => api.delete(`/v1/agents/channels/${id}/`),

  // Messages
  messages: (channelId: string, params?: { limit?: number }) =>
    api.get(`/v1/agents/messages/`, { params: { channel: channelId, ...params } }),
  sendMessage: (data: { channel: string; content: string; message_type?: string }) =>
    api.post('/v1/agents/messages/', data),

  // Memberships
  memberships: (channelId: string) =>
    api.get('/v1/agents/memberships/', { params: { channel: channelId } }),
  addMember: (data: { channel: string; agent_template?: string; role?: string }) =>
    api.post('/v1/agents/memberships/', data),
}
```

### UI Page Needed
Create `frontend/src/pages/AgentChannelsPage.tsx`:
- Channel list sidebar
- Message thread view
- Member management panel
- Create/edit channel modal

**Priority: HIGH** - This is a complete feature with data, just missing UI.

---

## Medium Priority Gaps

### 1. Agent Templates Management

**Backend:** `UnifiedAgentTemplateViewSet` at `/api/v1/agents/templates/`

**Current Frontend:** Read-only via `agentsApi.list()` and `agentsApi.comprehensive()`

**Missing:**
- Create new agent template
- Edit agent template
- Delete agent template
- Template configuration UI

**Frontend API Addition:**
```typescript
export const agentTemplatesApi = {
  list: () => api.get('/v1/agents/templates/'),
  create: (data: { name: string; description: string; category?: string }) =>
    api.post('/v1/agents/templates/', data),
  detail: (id: string) => api.get(`/v1/agents/templates/${id}/`),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/v1/agents/templates/${id}/`, data),
  delete: (id: string) => api.delete(`/v1/agents/templates/${id}/`),
}
```

---

### 2. Agent Orchestrations Management

**Backend:** `AgentOrchestrationViewSet` at `/api/v1/agents/orchestrations/`

**Current Frontend:** Listed in IntelligencePage but no CRUD

**Missing:**
- Create orchestration workflow
- Edit orchestration
- View orchestration details
- Monitor orchestration execution

**Frontend API Addition:**
```typescript
export const agentOrchestrationsApi = {
  list: (params?: { status?: string }) =>
    api.get('/v1/agents/orchestrations/', { params }),
  create: (data: { name: string; agents: string[]; workflow?: Record<string, unknown> }) =>
    api.post('/v1/agents/orchestrations/', data),
  detail: (id: string) => api.get(`/v1/agents/orchestrations/${id}/`),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/v1/agents/orchestrations/${id}/`, data),
  execute: (id: string) => api.post(`/v1/agents/orchestrations/${id}/execute/`),
}
```

---

### 3. Agent Tools Registry

**Backend:** `AgentToolViewSet` at `/api/v1/agents/tools/`

**Current Frontend:** None

**Missing:**
- Browse available agent tools
- Configure tool parameters
- Enable/disable tools per agent

**Frontend API Addition:**
```typescript
export const agentToolsApi = {
  list: (params?: { category?: string; agent?: string }) =>
    api.get('/v1/agents/tools/', { params }),
  detail: (id: string) => api.get(`/v1/agents/tools/${id}/`),
  configure: (id: string, data: { config: Record<string, unknown> }) =>
    api.patch(`/v1/agents/tools/${id}/`, data),
}
```

---

### 4. Agent Monitoring Dashboard

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

## Summary

| Feature | Backend | Frontend | Data | Priority |
|---------|---------|----------|------|----------|
| Agent Channels | ✅ Complete | ❌ Missing | ✅ Has data | **HIGH** |
| Agent Templates CRUD | ✅ Complete | ⚠️ Read-only | ✅ Has data | MEDIUM |
| Agent Orchestrations | ✅ Complete | ⚠️ Partial | ✅ Has data | MEDIUM |
| Agent Tools | ✅ Complete | ❌ Missing | ✅ Has data | MEDIUM |
| Agent Monitoring | ✅ Complete | ⚠️ Basic | N/A | MEDIUM |
| Agent Registry | ✅ Complete | ⚠️ Partial | ✅ Has data | LOW |

**Total: 6 features with backend APIs needing frontend exposure**
