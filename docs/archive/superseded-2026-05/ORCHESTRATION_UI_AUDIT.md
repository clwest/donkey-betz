# Orchestration UI Audit & Integration Plan

**Session 764 | January 15, 2026**
**Purpose:** Document all existing orchestration UI and plan integration of the new Orchestration Layer

---

## ✅ IMPLEMENTATION COMPLETE (Session 765)

**Option A was implemented:** The AgentsPage Orchestrations tab now includes sub-tabs for the new Orchestration Layer.

### What Was Built:

1. **Sub-Tab Navigation** (Lines 3101-3150)
   - Workflows | Executions | Agent Orchestrations (legacy)
   - Active execution count badge on Executions tab

2. **Workflows Sub-Tab** (Lines 3152-3240)
   - Grid display of CustomWorkflow objects from `orchestrationApi.listWorkflows()`
   - Shows execution_mode, step_count, max_retries, cost_budget
   - Execute button opens workflow input modal

3. **Executions Sub-Tab** (Lines 3243-3382)
   - List of OrchestrationExecution objects from `orchestrationApi.listExecutions()`
   - Progress bars, status badges, cost/token display
   - Resume/Cancel buttons for active executions
   - Click to open detailed execution view
   - Auto-refresh every 10 seconds

4. **Execute Workflow Modal** (Lines 3611-3700)
   - Shows workflow name and step count
   - JSON input textarea for workflow parameters
   - Budget warning display
   - Execute button triggers `orchestrationApi.execute()`

5. **Execution Detail Modal** (Lines 3703-3935)
   - Full execution stats (progress, cost, tokens, started time)
   - Step timeline with status icons
   - Approval gates display with expiration
   - Resume/Cancel action buttons
   - Auto-refresh every 5 seconds when open

---

## Executive Summary

The frontend currently has **TWO orchestration systems** with different purposes:

| System | API | UI Status | Purpose |
|--------|-----|-----------|---------|
| **Agent Orchestrations** (Session 734) | `agentOrchestrationsApi` | Fully Built | Simple agent chaining |
| **Orchestration Layer** (Session 764) | `orchestrationApi` | API Only, No UI | Full workflow execution with approvals |

**Key Insight:** These systems serve different needs and should be **unified** into a single, comprehensive orchestration experience.

---

## Current Orchestration UI Inventory

### 1. AgentsPage - Orchestrations Tab

**Location:** `frontend/src/pages/AgentsPage.tsx` (Lines 2972-3350+)

**Current Features:**
```
┌─────────────────────────────────────────────────────────────┐
│  Orchestrations Tab                                         │
├─────────────────────────────────────────────────────────────┤
│  [+ New Orchestration] [Filter: All Statuses ▼]             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ Content Pipeline│ │ Stock Analysis  │ │ Research Flow   ││
│  │ ● Running (45%) │ │ ○ Pending       │ │ ✓ Completed     ││
│  │ Agents: A,B,C+2 │ │ Agents: X,Y,Z   │ │ Agents: R,S     ││
│  │ Runs: 5 │ $1.20 │ │ Runs: 0 │ $0    │ │ Runs: 12│ $4.50 ││
│  │ [▶][👁][✏️][🗑] │ │ [▶][✏️][🗑]     │ │ [↻][👁][✏️][🗑] ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

**API Used:** `agentOrchestrationsApi`
- `list()` - List orchestrations with status filter
- `create()` - Create new orchestration
- `update()` - Edit orchestration
- `delete()` - Delete orchestration
- `execute()` - Start execution
- `reset()` - Reset for re-run
- `output()` - View results

**Data Model:**
```typescript
// Current (Session 734)
{
  id: string
  name: string
  description: string
  workflow_definition: object
  agent_sequence: string[]      // ["AgentA", "AgentB", "AgentC"]
  execution_strategy: string    // "sequential" | "parallel" | "pipeline"
  status: string               // "pending" | "running" | "completed" | "failed"
  execution_count: number
  total_execution_time: number
  total_cost: number
  created_at: string
  agent_outputs?: object[]     // Results from each agent
}
```

**Limitations:**
- No step-level tracking during execution
- No approval gates (runs to completion)
- No pause/resume capability
- No cost budgets or limits
- No dependency-based execution
- No retry logic
- No checkpoint/resume on failure

---

### 2. IntelligencePage - Gates Tab

**Location:** `frontend/src/pages/IntelligencePage.tsx` (Lines 1400-2200)

**Current Features:**
```
┌─────────────────────────────────────────────────────────────┐
│  Gates Tab                                                  │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Gate: Deploy New Feature                              │ │
│  │ Risk: HIGH │ Status: IN_PROGRESS │ Checklist: 3/5     │ │
│  │ Decision Type: experiment                             │ │
│  │                                                       │ │
│  │ ┌─ Checklist Items ────────────────────────────────┐ │ │
│  │ │ ✓ Unit tests passing                              │ │ │
│  │ │ ✓ Code review approved                            │ │ │
│  │ │ ✓ Documentation updated                           │ │ │
│  │ │ ○ Staging deployment verified                     │ │ │
│  │ │ ○ Rollback plan documented                        │ │ │
│  │ └───────────────────────────────────────────────────┘ │ │
│  │                                                       │ │
│  │ Success Criteria: [list]                              │ │
│  │ Failure Criteria: [list]                              │ │
│  │ Risk Factors: [list]                                  │ │
│  │                                                       │ │
│  │ [Decline] [Start] [Approve] [Waive]                   │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**API Used:** `pilotsApi`, `intelligenceApi`

**Purpose:** Approval workflow for pilots/experiments (NOT agent orchestration)

**Relevance to New Orchestration:**
- Gate approval UI pattern can be reused for orchestration approval gates
- Checklist pattern useful for step tracking visualization
- Action buttons pattern reusable for approve/reject/modify

---

### 3. HumanPage - Mission Control

**Location:** `frontend/src/pages/HumanPage.tsx` (Lines 685-710)

**Current Features:**
```
┌─────────────────────────────────────────────────────────────┐
│  Attention Item                                             │
├─────────────────────────────────────────────────────────────┤
│  📊 Stock Analysis: AAPL showing unusual volume             │
│  Source: StockAnalystAgent │ Urgency: High                  │
│                                                             │
│  [Review] [Set Alert] [Watchlist] [Dismiss]  <- Dynamic!    │
│                                                             │
│  💬 Feedback: [________________] (optional)                 │
└─────────────────────────────────────────────────────────────┘
```

**Key Pattern:** Dynamic action buttons from `payload.available_actions`

**Relevance to New Orchestration:**
- This IS where orchestration approval gates should appear
- Session 764 already registers handlers:
  - `approve_orchestration_step`
  - `reject_orchestration_step`
  - `modify_orchestration_step`
- HumanAttentionItem created by approval gates will show here

---

### 4. NeuralOrchestraPage - Monitoring Only

**Location:** `frontend/src/pages/NeuralOrchestraPage.tsx` (Line 381)

Shows `orchestrations_active` count but no execution control.

---

## New Orchestration Layer (Session 764) - No UI Yet

### API Defined in `frontend/src/lib/api.ts`

```typescript
// NEW - Lines 1956-2053
export interface OrchestrationWorkflow {
  id: string
  name: string
  description: string
  execution_mode: 'sequential' | 'parallel' | 'dependency'
  max_retries: number
  timeout_seconds: number
  cost_budget: string | null
  step_count: number
  created_at: string | null
  updated_at: string | null
}

export interface OrchestrationExecution {
  id: string
  workflow_id: string
  workflow_name: string
  status: 'pending' | 'running' | 'waiting_approval' | 'completed' | 'failed' | 'cancelled' | 'paused'
  current_step: number
  total_steps: number
  total_cost: string
  total_tokens: number
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  triggered_by: string | null
}

export interface OrchestrationStepExecution {
  step_number: number
  agent_name: string
  status: string
  started_at: string | null
  completed_at: string | null
  cost: string
  tokens: number
  retry_count: number
  error_message: string | null
  output_preview: string | null
}

export const orchestrationApi = {
  listWorkflows: () => api.get('/orchestration/workflows/'),
  execute: (workflowId, input?, async?) => api.post(`/orchestration/workflows/${workflowId}/execute/`),
  listExecutions: (params?) => api.get('/orchestration/executions/', { params }),
  getExecution: (executionId) => api.get(`/orchestration/executions/${executionId}/`),
  resume: (executionId, modifications?) => api.post(`/orchestration/executions/${executionId}/resume/`),
  cancel: (executionId, reason?) => api.post(`/orchestration/executions/${executionId}/cancel/`),
}
```

### Backend Components (No UI)

| Component | Location | Purpose |
|-----------|----------|---------|
| OrchestrationExecution | `core/models_orchestration.py` | Execution tracking |
| OrchestrationStepExecution | `core/models_orchestration.py` | Step-level tracking |
| OrchestrationApprovalGate | `core/models_orchestration.py` | Approval flow |
| orchestration_engine | `core/services/orchestration_engine.py` | Execution coordinator |
| step_executor | `core/services/orchestration_step_executor.py` | Step runner |
| checkpoint_manager | `core/services/orchestration_checkpoint.py` | State persistence |
| dependency_resolver | `core/services/orchestration_dependencies.py` | Step ordering |
| approval_service | `core/services/orchestration_approval.py` | Gate management |

---

## Gap Analysis: What's Missing

### Missing UI Components

| Component | Priority | Complexity | Notes |
|-----------|----------|------------|-------|
| Workflow List/Browser | HIGH | Medium | Display CustomWorkflows |
| Workflow Builder/Editor | HIGH | High | Create/edit step definitions |
| Execution Dashboard | HIGH | Medium | Monitor running executions |
| Step Timeline | MEDIUM | Medium | Visual step progress |
| Approval Gate Actions | HIGH | Low | Already in HumanPage pattern |
| Execution Input Form | MEDIUM | Low | Parameters for workflow start |
| Cost/Budget Display | LOW | Low | Add to execution cards |

### Missing Integrations

1. **Workflows not visible** - CustomWorkflow exists in DB but no UI to browse
2. **No execution monitoring** - Can't see step-by-step progress
3. **Approval gates disconnected** - Creates HumanAttentionItem but no clear link
4. **Two systems confusion** - Users see agentOrchestrationsApi but not orchestrationApi

---

## Recommended Integration Strategy

### Option A: Merge into AgentsPage (Recommended)

Enhance the existing Orchestrations tab to use the new orchestrationApi:

```
┌─────────────────────────────────────────────────────────────┐
│  Orchestrations Tab (Enhanced)                              │
├─────────────────────────────────────────────────────────────┤
│  [Workflows] [Executions] [Templates]  <- Sub-tabs          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WORKFLOWS SUB-TAB:                                         │
│  ┌─────────────────┐ ┌─────────────────┐                    │
│  │ Content Pipeline│ │ Stock Analysis  │                    │
│  │ Mode: Sequential│ │ Mode: Parallel  │                    │
│  │ Steps: 4        │ │ Steps: 3        │                    │
│  │ Budget: $5.00   │ │ Budget: $2.00   │                    │
│  │ [Execute] [Edit]│ │ [Execute] [Edit]│                    │
│  └─────────────────┘ └─────────────────┘                    │
│                                                             │
│  EXECUTIONS SUB-TAB:                                        │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Execution #abc123                         ● RUNNING   │ │
│  │ Workflow: Content Pipeline                            │ │
│  │ Progress: Step 2 of 4 (ResearchAgent)                 │ │
│  │ ████████░░░░░░░░ 50%                                  │ │
│  │                                                       │ │
│  │ Step Timeline:                                        │ │
│  │ [1] TopicMiner ✓ $0.12 │ 2.3s                        │ │
│  │ [2] Research   ● $0.45 │ running...                  │ │
│  │ [3] Writer     ○ -     │ pending                     │ │
│  │ [4] Publisher  ○ -     │ pending                     │ │
│  │                                                       │ │
│  │ Cost: $0.57 / $5.00 budget                           │ │
│  │ Tokens: 1,234                                        │ │
│  │                                                       │ │
│  │ [Pause] [Cancel]                                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Execution #def456                    ⏸ WAITING_APPROVAL│ │
│  │ Workflow: Stock Analysis                              │ │
│  │ Waiting for: Step 3 approval                         │ │
│  │                                                       │ │
│  │ [View in Mission Control]                             │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Users already know where to find orchestrations
- Consistent with existing mental model
- Less navigation

**Cons:**
- AgentsPage already large
- Mixes agent-level and workflow-level concepts

### Option B: New Dedicated Orchestration Page

Create `frontend/src/pages/OrchestrationPage.tsx`:

```
┌─────────────────────────────────────────────────────────────┐
│  Orchestration Center                                       │
├─────────────────────────────────────────────────────────────┤
│  WORKFLOWS                           LIVE EXECUTIONS        │
│  ┌─────────────────────────┐        ┌─────────────────────┐│
│  │ [+ New Workflow]        │        │ 3 Running           ││
│  │                         │        │ 2 Waiting Approval  ││
│  │ • Content Pipeline (4)  │        │ 12 Completed Today  ││
│  │ • Stock Analysis (3)    │        │                     ││
│  │ • Research Flow (2)     │        │ [View All]          ││
│  │ • Blockchain Audit (5)  │        └─────────────────────┘│
│  └─────────────────────────┘                                │
│                                                             │
│  EXECUTION MONITOR                                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    Step Flow                          │ │
│  │  ┌────┐    ┌────┐    ┌────┐    ┌────┐               │ │
│  │  │ S1 │ -> │ S2 │ -> │ S3 │ -> │ S4 │               │ │
│  │  │ ✓  │    │ ●  │    │ ○  │    │ ○  │               │ │
│  │  └────┘    └────┘    └────┘    └────┘               │ │
│  │  Topic     Research   Writer    Publish              │ │
│  │  $0.12     $0.45      -         -                    │ │
│  │                                                       │ │
│  │  Current Step Details:                                │ │
│  │  Agent: ResearchAgent                                 │ │
│  │  Status: Running (45s elapsed)                        │ │
│  │  Retries: 0/3                                         │ │
│  │                                                       │ │
│  │  Output Preview:                                      │ │
│  │  "Researching AI trends for 2026..."                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  APPROVAL GATES                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ ⚠️ Step 3 of "Content Pipeline" requires approval     │ │
│  │    Agent: ContentWriterAgent                          │ │
│  │    Expires: 23h 45m                                   │ │
│  │    [Approve] [Reject] [Modify]                        │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Clean separation of concerns
- Room for rich visualization
- Dedicated real estate for complex workflows

**Cons:**
- New navigation item
- May feel disconnected from Agents

### Option C: Hybrid Approach (Best of Both)

1. **Keep simple orchestrations in AgentsPage** - Quick agent chaining
2. **Add Orchestration link in AgentsPage** - "Advanced Workflows →"
3. **New OrchestrationPage for complex workflows** - Full builder, monitoring

---

## Migration Path: Old → New

### Phase 1: Add New UI (Non-Breaking)
1. Create execution monitoring in AgentsPage Orchestrations tab
2. Use `orchestrationApi` alongside `agentOrchestrationsApi`
3. Display step-level progress for running executions

### Phase 2: Unify Data Models
1. Migrate `agentOrchestrationsApi` data to `orchestrationApi`
2. Keep old API for backward compatibility
3. Add deprecation notices

### Phase 3: Full Migration
1. Remove old orchestrations tab
2. Use only `orchestrationApi`
3. Update all references

---

## Implementation Priority

### Must Have (P0)
1. **Execution Monitoring** - See running workflow status
2. **Step Progress Display** - Know which step is active
3. **Approval Gate in HumanPage** - Already works, just needs testing

### Should Have (P1)
4. **Workflow Browser** - See available workflows
5. **Execute with Input** - Start workflow with parameters
6. **Cancel/Resume Actions** - Control running executions

### Nice to Have (P2)
7. **Workflow Builder** - Create new workflows in UI
8. **Step Timeline Visualization** - Gantt chart view
9. **Cost Budget Display** - Show budget vs actual
10. **Retry History** - See failed attempts

---

## Files to Create/Modify

### New Files
| File | Purpose |
|------|---------|
| `frontend/src/components/orchestration/ExecutionCard.tsx` | Execution status card |
| `frontend/src/components/orchestration/StepTimeline.tsx` | Step progress visualization |
| `frontend/src/components/orchestration/WorkflowCard.tsx` | Workflow summary card |
| `frontend/src/components/orchestration/ApprovalGateCard.tsx` | Approval gate display |
| `frontend/src/hooks/useOrchestration.ts` | React Query hooks |

### Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/pages/AgentsPage.tsx` | Add execution monitoring to Orchestrations tab |
| `frontend/src/pages/HumanPage.tsx` | Ensure approval gates render correctly |
| `frontend/src/lib/api.ts` | Already has orchestrationApi |

---

## Testing Checklist

After implementation:

- [ ] Can list all workflows from `/api/orchestration/workflows/`
- [ ] Can execute a workflow and see it in executions list
- [ ] Can see step-by-step progress while running
- [ ] Approval gate appears in HumanPage when step requires approval
- [ ] Can approve/reject from HumanPage
- [ ] Workflow resumes after approval
- [ ] Can cancel a running execution
- [ ] Failed steps show error messages
- [ ] Costs aggregate correctly
- [ ] Completed workflows show final output

---

## Appendix: API Comparison

### agentOrchestrationsApi (Old)
```
GET  /v1/agents/orchestrations/           - List
POST /v1/agents/orchestrations/           - Create
GET  /v1/agents/orchestrations/{id}/      - Detail
PUT  /v1/agents/orchestrations/{id}/      - Update
DEL  /v1/agents/orchestrations/{id}/      - Delete
POST /v1/agents/orchestrations/{id}/execute/  - Execute
POST /v1/agents/orchestrations/{id}/reset/    - Reset
GET  /v1/agents/orchestrations/{id}/output/   - View output
```

### orchestrationApi (New)
```
GET  /api/orchestration/workflows/                    - List workflows
POST /api/orchestration/workflows/{id}/execute/       - Execute
GET  /api/orchestration/executions/                   - List executions
GET  /api/orchestration/executions/{id}/              - Get detail
POST /api/orchestration/executions/{id}/resume/       - Resume
POST /api/orchestration/executions/{id}/cancel/       - Cancel
```

**Key Differences:**
- New system separates "workflows" (definitions) from "executions" (runs)
- New system has step-level execution tracking
- New system supports approval gates
- New system has pause/resume capability
- New system tracks per-step costs and tokens
