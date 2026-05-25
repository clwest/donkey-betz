---
originating_session: 843
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 843: Orchestration Contract + trace_id System

**Date:** January 27, 2026
**Focus:** Implement trace_id system to connect agent outputs to workflow context

---

## Problem Summary

Agents produce outputs that float in "loose artifact space" - not properly linked to projects, tasks, or workflow executions. The user accurately described it as: "you have the spine, but some nerves aren't plugged in yet."

**Current State Before Fix:**
- `AgentExecution` lacked `project_id` and `trace_id`
- `Deliverable` links to workspace but most artifacts are orphaned
- `ExtractedArtifact`, `AuditReport`, `SelfBlog` have NO project linkage
- No unified `trace_id` across workflow executions
- Can't trace: conversation -> synthesis -> tasks -> documents -> experiments

**The Fix:** Implemented a mandatory "Orchestration Contract" with `trace_id` that persists across entire workflow executions.

---

## Implementation Details

### Phase 1: Model Field Additions

Added trace_id and project_id fields to 6 models in the system.

**AgentExecution** (`core/models_unified_system.py`):
```python
# Session 843: Orchestration Contract fields
trace_id = models.UUIDField(null=True, blank=True, db_index=True)
project = models.ForeignKey('core.PartnershipProject', null=True, blank=True, on_delete=models.SET_NULL, related_name='agent_executions')
parent_object_type = models.CharField(max_length=50, blank=True)
parent_object_id = models.UUIDField(null=True, blank=True, db_index=True)
owner_agent = models.CharField(max_length=100, blank=True, db_index=True)
```

**Deliverable** (`core/models_deliverables.py`):
```python
trace_id = models.UUIDField(null=True, blank=True, db_index=True)
parent_object_type = models.CharField(max_length=50, blank=True)
parent_object_id = models.UUIDField(null=True, blank=True, db_index=True)
```

**ExtractedArtifact** (`core/models_conversation_artifacts.py`):
```python
trace_id = models.UUIDField(null=True, blank=True, db_index=True)
project = models.ForeignKey('core.PartnershipProject', null=True, blank=True, on_delete=models.SET_NULL, related_name='extracted_artifacts')
```

**AuditReport** (`core/models_audit_tracking.py`):
```python
trace_id = models.UUIDField(null=True, blank=True, db_index=True)
project = models.ForeignKey('core.PartnershipProject', null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_reports')
```

**SelfBlog** (`core/models_unified_system.py`):
```python
trace_id = models.UUIDField(null=True, blank=True, db_index=True)
project = models.ForeignKey('core.PartnershipProject', null=True, blank=True, on_delete=models.SET_NULL, related_name='self_blogs')
```

**AgentDecisionSummary** (`core/models_unified_system.py`):
```python
trace_id = models.UUIDField(null=True, blank=True, db_index=True)
project = models.ForeignKey('core.PartnershipProject', null=True, blank=True, on_delete=models.SET_NULL, related_name='decision_summaries')
```

### Phase 2: WiringDefect Model

Created new model in `core/models_orchestration.py`:

```python
class WiringDefect(models.Model):
    """
    Session 843: Tracks artifacts created without proper trace/project linkage.
    Enables auditing orphaned outputs and retroactive fixing.
    """
    DEFECT_TYPES = [
        ('missing_project_id', 'Missing Project ID'),
        ('missing_trace_id', 'Missing Trace ID'),
        ('missing_parent', 'Missing Parent Object'),
        ('orphan_artifact', 'Orphan Artifact'),
    ]
    defect_type = models.CharField(max_length=30, choices=DEFECT_TYPES, db_index=True)
    object_type = models.CharField(max_length=100, db_index=True)
    object_id = models.UUIDField(db_index=True)
    trace_id = models.UUIDField(null=True, blank=True, db_index=True)
    agent_name = models.CharField(max_length=100, blank=True)
    execution_context = models.JSONField(default=dict)
    is_resolved = models.BooleanField(default=False, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Phase 3: TraceAttachmentService

Created `core/services/trace_attachment_service.py` with fallback rules:

**trace_id Resolution:**
1. Use explicit trace_id from context
2. Inherit from parent_object's trace_id
3. Inherit from conversation's trace_id
4. Generate new trace_id (root execution)

**project_id Resolution:**
1. Use explicit project_id from context
2. Inherit from parent_object
3. Infer from user's active project
4. Leave null (logged as WiringDefect)

Key methods:
- `generate_trace_id()` - Create new UUID
- `resolve_trace_id(context, parent_object)` - Apply fallback rules
- `resolve_project_id(context, parent_object, user)` - Apply fallback rules
- `attach_to_object(obj, context, parent_object, user, agent_name)` - Full attachment with defect logging
- `get_context_for_child(parent_execution, additional_context)` - Build context for child executions

### Phase 4: Agent Execution Integration

**agent_router.py** (`_create_execution_record`):
```python
from core.services.trace_attachment_service import TraceAttachmentService

# Session 843: Resolve trace_id and project_id
context = context_summary or {}
trace_id = TraceAttachmentService.resolve_trace_id(context)
project_id = TraceAttachmentService.resolve_project_id(context, user=self.user)

execution = AgentExecution.objects.create(
    # ... existing fields ...
    # Session 843: Orchestration contract fields
    trace_id=trace_id,
    project_id=project_id,
    owner_agent=agent_name,
    parent_object_type=context.get('parent_object_type', ''),
    parent_object_id=context.get('parent_object_id'),
)
```

**deliverable_envelope.py** (`wrap`):
```python
# Session 843: Attach trace context
from core.services.trace_attachment_service import TraceAttachmentService
TraceAttachmentService.attach_to_object(
    deliverable,
    context,
    parent_object=parent_execution,
    user=user,
    agent_name=agent_name,
)
deliverable.save()
```

### Phase 5: Trace Viewer API

Created `core/views_trace_viewer.py` with three endpoints:

**TraceViewerView** - `GET /api/traces/<trace_id>/`
- Gathers all artifacts linked to trace_id
- Builds chronological timeline
- Lists any wiring defects
- Returns summary statistics

**WiringDefectsListView** - `GET /api/wiring-defects/`
- Query params: resolved, type, object_type, limit
- Lists all wiring defects with filtering

**WiringDefectResolveView** - `POST /api/wiring-defects/<defect_id>/resolve/`
- Marks defect as resolved
- Optional notes parameter

---

## API Reference

### GET /api/traces/<trace_id>/

Returns all artifacts linked to a trace:

```json
{
  "trace_id": "uuid",
  "artifacts": {
    "agent_executions": [...],
    "deliverables": [...],
    "extracted_artifacts": [...],
    "audit_reports": [...],
    "self_blogs": [...],
    "decision_summaries": [...]
  },
  "timeline": [
    {"type": "agent_executions", "id": "uuid", "description": "...", "timestamp": "..."}
  ],
  "wiring_defects": [...],
  "summary": {
    "total_artifacts": 15,
    "defect_count": 2,
    "artifact_counts": {...},
    "status_breakdown": {...}
  }
}
```

### GET /api/wiring-defects/

Query parameters:
- `resolved` - Filter by resolved status (true/false)
- `type` - Filter by defect type
- `object_type` - Filter by object type
- `limit` - Max results (default 100, max 500)

### POST /api/wiring-defects/<defect_id>/resolve/

Body:
```json
{
  "notes": "Optional resolution notes"
}
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

## Rollback Plan

All fields are nullable - safe to rollback:
1. Revert migrations: `python manage.py migrate core 0191`
2. Remove new files: `trace_attachment_service.py`, `views_trace_viewer.py`
3. Remove integration points in `agent_router.py` and `deliverable_envelope.py`
4. Remove URL patterns from `core/urls.py`

No data loss - existing records unaffected.

---

## Verification

```bash
# Verify fields exist
python manage.py shell -c "
from core.models_unified_system import AgentExecution
print(f'Has trace_id: {hasattr(AgentExecution, \"trace_id\")}')
print(f'Has project: {hasattr(AgentExecution, \"project\")}')
"

# Test trace_id generation
python manage.py shell -c "
from core.services.trace_attachment_service import TraceAttachmentService
trace_id = TraceAttachmentService.generate_trace_id()
print(f'Generated trace_id: {trace_id}')
"
```

---

## Potential Next Steps

1. **Add trace_id to AgentConversation** - Allow conversations to propagate trace context
2. **Trace visualization UI** - Frontend component to view trace timelines
3. **Retroactive trace linking** - Script to link orphaned artifacts to traces
4. **WiringDefect alerting** - Notify when defects exceed threshold
5. **OrchestrationExecution integration** - Link to existing orchestration system

---

**Session 843 Complete - Orchestration Contract implemented, trace_id system active**
