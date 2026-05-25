---
originating_session: 847
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 847 - Initiative Pipeline Implementation

**Date:** January 27, 2026
**Focus:** Wire ThinkingAgent to Initiative 5-stage pipeline
**ChatGPT Feedback:** "You're missing the middle. ThinkingAgent → Initiative → Stages → Documents → Actions"

---

## Problem Statement

The system had:
- ✅ Autonomous sensing (77 spiders)
- ✅ Autonomous diagnosis (ThinkingAgent)
- ✅ Autonomous remediation (Self-healing)
- ❌ **No unified project spine**

Documents (SelfBlog, Deliverables) were "floating" without being organized into coherent projects. The Initiative model existed but was never used by ThinkingAgent.

**Key Stats Before:**
- 0 Initiatives in production
- 96% of gates being auto-waived (governance concern)
- Floating blogs not linked to any workflow

---

## What Was Implemented

### 1. InitiativeIntegrationService (NEW)
**File:** `core/services/initiative_integration_service.py`

A service that wires ThinkingAgent outputs to the Initiative pipeline:

- `get_or_create_initiative()` - Auto-creates initiatives when actions are triggered
- `link_document_to_stage()` - Auto-links SelfBlogs to appropriate stages
- `promote_stage()` - Advances stages through the pipeline
- `auto_promote_if_ready()` - Auto-promotes stages with approved documents
- `get_initiative_health()` - Calculates health (healthy/stale/blocked)
- `get_all_initiatives_dashboard()` - Dashboard data for UI

**Stage Mapping:**
| Document Type | Stage |
|---------------|-------|
| research_brief, research | 1 - Research Brief |
| prototype_plan, proposal | 2 - Prototype Plan |
| evaluation, audit | 3 - Evaluation Protocol |
| technical_document | 4 - Technical Design |
| pilot, report, blog | 5 - Pilot Execution |

### 2. AutonomousActionExecutor Integration
**File:** `core/services/autonomous_action_executor.py`

Updated `execute_action()` to:
- Call `_link_to_initiative()` after every action
- Return `initiative_id` in action results
- Track which documents belong to which initiatives

**New Action Types:**
- `promote_initiative_stage` - Advance an initiative's stage
- `review_initiatives` - Check health of all initiatives, auto-promote ready stages

### 3. ThinkingAgent Updated
**File:** `core/agents/thinking_agent.py`

Added to prompt:
- New actions: `promote_initiative_stage`, `review_initiatives`
- Context about the 5-stage Initiative Pipeline
- Instructions on how documents map to stages

### 4. Initiative Dashboard UI (NEW)
**File:** `frontend/src/pages/workspace/tabs/InitiativesTab.tsx`

React component showing:
- All initiatives with progress bars (Stage 1-5)
- Health indicators (On Track, Stale, Blocked)
- Filter by status (All, Active, Stale, Blocked)
- Detail modal with stage-by-stage breakdown
- Document links for each stage
- "Populate from Deliverables" button for existing content

**Added to workspace tabs in:**
- `WorkspacePageNew.tsx`
- `workspace/tabs/index.ts`
- `workspace/types.ts`
- `frontend/src/lib/api.ts`

### 5. Stricter Gate Waiving
**File:** `core/models_pilot_readiness.py`

Added `initiative` ForeignKey to `PilotReadinessGate`:
```python
initiative = models.ForeignKey(
    'core.Initiative',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    help_text="If linked to an initiative, stricter rules apply"
)
```

Updated `waive()` method:
- Initiative-linked gates **cannot be auto-waived** (unless `force=True`)
- Addresses the 96% gate waiving concern
- Gates associated with structured projects require human review

**Migration:** `0194_session_847_initiative_pipeline.py`

---

## Files Changed

| File | Change |
|------|--------|
| `core/services/initiative_integration_service.py` | **NEW** - Initiative pipeline integration |
| `core/services/autonomous_action_executor.py` | Added Initiative linking + 2 new action handlers |
| `core/agents/thinking_agent.py` | Added 2 new actions + Initiative context |
| `core/models_pilot_readiness.py` | Added `initiative` FK + stricter waive() logic |
| `core/migrations/0194_session_847_initiative_pipeline.py` | **NEW** - Migration |
| `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` | **NEW** - Initiative Dashboard |
| `frontend/src/pages/workspace/tabs/index.ts` | Export InitiativesTab |
| `frontend/src/pages/workspace/types.ts` | Added 'initiatives' WorkspaceTab |
| `frontend/src/pages/WorkspacePageNew.tsx` | Added Initiatives tab |
| `frontend/src/lib/api.ts` | Added `initiatives()` and `populateInitiatives()` |

---

## How It Works Now

```
ThinkingAgent decides action (request_research, create_report, etc.)
    ↓
AutonomousActionExecutor executes action
    ↓
_link_to_initiative() is called
    ↓
InitiativeIntegrationService:
  1. get_or_create_initiative(topic)
  2. link_document_to_stage(document, initiative)
    ↓
Document now belongs to Initiative Stage 1-5
    ↓
User can view in Initiative Dashboard
    ↓
ThinkingAgent can promote_initiative_stage when ready
    ↓
Gates linked to initiatives require human review (not auto-waived)
```

---

## API Endpoints

```bash
# Get all initiatives with stage status
GET /api/v1/initiatives/

# Populate initiatives from existing deliverables
POST /api/v1/initiatives/populate/
```

---

## Testing

1. Start the platform: `make start && make celery`
2. Access Initiatives tab: http://localhost:8000/ai-studio/ → Workspace → Initiatives
3. Click "Populate from Deliverables" if no initiatives exist
4. Trigger a ThinkingAgent cycle (or wait for automated cycle)
5. New documents should appear linked to initiatives

---

## Known Limitations

1. **Migration not yet applied** - Run `python manage.py migrate` before use
2. **No initiative creation UI** - Initiatives are auto-created, not manually created
3. **Stage promotion is manual** - ThinkingAgent can auto-promote, but no UI button yet
4. **Health calculation is simple** - Based on update time and rejected stages

---

## Next Steps (Session 848+)

1. **Apply migration to production** - `python manage.py migrate`
2. **Run populate_initiatives** - Link existing deliverables to initiatives
3. **Monitor initiative health** - Watch for stale/blocked initiatives
4. **Add manual promotion button** - UI control to advance stages
5. **Enhance health logic** - More sophisticated stale/blocked detection
6. **Initiative notifications** - Alert when initiatives are blocked

---

## ChatGPT Feedback Summary

> "This is the last big piece. Once initiatives are wired in, you'll have a self-managing product org. Most startups never get here."

The Initiative pipeline creates the "project spine" that was missing. Documents are no longer floating - they belong to structured projects with clear stages and governance.

---

**Session 847 Complete - Initiative Pipeline implemented**
