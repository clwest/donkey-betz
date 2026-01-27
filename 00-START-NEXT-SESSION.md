# Session 844 - Start Here

**Previous Session:** 843 (Orchestration Contract + trace_id System)
**Date:** January 27, 2026
**Status:** 74 Agents | 77 Spiders | 25 Advisors | 235 Celery Tasks | **PRODUCTION HEALTHY**

---

## What Was Accomplished in Session 843

### Orchestration Contract Implementation

Implemented a unified trace_id system that connects all agent outputs to their workflow context. This fixes the "floating artifacts" problem where outputs weren't linked to projects, tasks, or workflow executions.

**Problem:** Agents produce outputs that float in "loose artifact space" - not properly linked to projects, tasks, or workflow executions.

**Solution:** Mandatory "Orchestration Contract" with trace_id that persists across entire workflow executions.

### Phase 1: Model Field Additions

Added trace_id and project_id fields to 6 models:

| Model | New Fields |
|-------|------------|
| `AgentExecution` | trace_id, project, parent_object_type, parent_object_id, owner_agent |
| `Deliverable` | trace_id, parent_object_type, parent_object_id |
| `ExtractedArtifact` | trace_id, project |
| `AuditReport` | trace_id, project |
| `SelfBlog` | trace_id, project |
| `AgentDecisionSummary` | trace_id, project |

### Phase 2: WiringDefect Model

Created `WiringDefect` model in `core/models_orchestration.py` to track artifacts created without proper trace/project linkage. Enables auditing orphaned outputs and retroactive fixing.

### Phase 3: TraceAttachmentService

Created `core/services/trace_attachment_service.py` with:

**trace_id Fallback Rules:**
1. Use explicit trace_id from context
2. Inherit from parent_object's trace_id
3. Inherit from conversation's trace_id
4. Generate new trace_id (root execution)

**project_id Fallback Rules:**
1. Use explicit project_id from context
2. Inherit from parent_object
3. Infer from user's active project
4. Leave null (logged as WiringDefect)

### Phase 4: Agent Execution Integration

Updated `agent_router.py` `_create_execution_record()` and `deliverable_envelope.py` `wrap()` to automatically attach trace context to all agent outputs.

### Phase 5: Trace Viewer API

Created API endpoints for trace debugging:

```bash
# View all artifacts linked to a trace
GET /api/traces/<trace_id>/

# List wiring defects
GET /api/wiring-defects/
GET /api/wiring-defects/?resolved=false

# Resolve a defect
POST /api/wiring-defects/<defect_id>/resolve/
```

---

## Files Changed

| File | Change |
|------|--------|
| `core/models_unified_system.py` | Added trace fields to AgentExecution, SelfBlog, AgentDecisionSummary |
| `core/models_deliverables.py` | Added trace fields to Deliverable |
| `core/models_conversation_artifacts.py` | Added trace fields to ExtractedArtifact |
| `core/models_audit_tracking.py` | Added trace fields to AuditReport |
| `core/models_orchestration.py` | Added WiringDefect model |
| `core/services/trace_attachment_service.py` | **NEW** - Trace attachment logic |
| `core/views_trace_viewer.py` | **NEW** - Trace viewer API |
| `core/urls.py` | Added trace viewer URL patterns |
| `core/agent_router.py` | Integrated trace context in execution creation |
| `core/services/deliverable_envelope.py` | Integrated trace context in wrap() |
| `core/migrations/0192_session_843_orchestration_contract.py` | Migration for all changes |

---

## Quick Start

```bash
# 1. Start platform
make start && make celery

# 2. Access workspace
open http://localhost:8000/ai-studio/

# 3. Test trace viewer (requires trace_id)
curl http://localhost:8000/api/traces/<some-uuid>/ -H "Authorization: Token <token>"
```

---

## Potential Next Steps

1. **Add trace_id to AgentConversation** - Allow conversations to propagate trace context
2. **Trace visualization UI** - Frontend component to view trace timelines
3. **Retroactive trace linking** - Script to link orphaned artifacts to traces
4. **WiringDefect alerting** - Notify when defects exceed threshold
5. **Add execution timeout within task** - Auto-fail individual tasks if they exceed time limit

---

## Key Documentation

- `docs/handoffs/SESSION_843_ORCHESTRATION_CONTRACT.md` - Detailed session handoff
- `docs/handoffs/SESSION_842_AGENT_LEARNING_TAB_FIXES.md` - Previous session
- `CLAUDE.md` - System overview
- `docs/AGENTS.md` - Agent documentation (74 agents)

---

## Previous Sessions

| Session | Focus |
|---------|-------|
| **843** | Orchestration Contract + trace_id System |
| **842** | Agent Learning Tab + Production Cleanup (242 stuck) + Celery Beat Investigation |
| **841** | Experiment Monitoring Fixes - Stop global halts, provider health, naming fix |
| **840** | Workspace Tabs Complete + Agent Error Fixes + React Error #31 |
| **839** | UI Status Mismatch Fix + Workspace Output Fix + API Audit |
| **838** | Finance Agent Audit Complete - MarketMovementMonitor, MarketAnomalyDetector |
| **837** | SignalScannerAgent placeholder fix - now uses real market data |
| **836** | Experiment System Diagnosis + Celery Beat fix + 5 Production API Fixes |
| **835** | Agent Output Audit (80+ agents) + 4 New Renderers + Modal Fixes |

---

**Session 843 Complete - Orchestration Contract implemented, trace_id system active**
