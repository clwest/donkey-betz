---
originating_session: 893
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 893 - Workspace Context Fix for System Tasks

**Date:** January 31, 2026
**Focus:** Enable workspace context for all agents including system tasks
**Status:** Complete

---

## Problem Statement

User noticed that MarketIntelligenceAgent and other agents showed `workspace: False` in the Command tab when triggered by scheduled tasks. This meant agents running without a user context were missing workspace information.

---

## Root Cause

**Location:** `core/agent_router.py` line 1284 (`_get_workspace_context` method)

The original code (Session 800) explicitly skipped workspace context for system tasks:

```python
if self.user is None:
    logger.debug(f"📁 [Session 800] Skipping workspace context for {agent_name} (system task, no user)")
    return {}
```

When agents are triggered by Celery Beat or other system processes, `self.user` is `None`. This caused the workspace context to be completely skipped, resulting in `workspace: False` for those executions.

---

## Solution

Modified `_get_workspace_context()` to fall back to a default workspace for system tasks:

```python
# Session 893: Get workspace for ALL agents, including system tasks
manager = None
if self.user is None:
    # Fall back to the "Codebase" workspace which is the main system workspace
    workspace = AgentWorkspace.objects.filter(
        name__icontains='codebase'
    ).first() or AgentWorkspace.objects.filter(is_active=True).first()

    if not workspace:
        logger.debug(f"📁 [Session 893] No default workspace available for system task {agent_name}")
        return {}

    logger.debug(f"📁 [Session 893] Using default workspace '{workspace.name}' for system task {agent_name}")
else:
    manager = get_workspace_manager(self.user)
    workspace = manager.get_active_workspace()

# Build context directly from workspace for system tasks if no manager
if manager:
    context = manager.get_workspace_context_for_agent(...)
else:
    # Session 893: Build basic context directly from workspace for system tasks
    context = {
        'workspace_name': workspace.name,
        'root_path': workspace.root_path,
        'tech_stack': workspace.tech_stack or {},
        'key_files': workspace.key_files or {},
        'directory_purposes': workspace.directory_purposes or {},
        'coding_patterns': workspace.coding_patterns or {},
        'import_aliases': workspace.import_aliases or {},
        'protected_paths': workspace.protected_paths or [],
        'total_files': workspace.total_files or 0,
    }
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agent_router.py` | Modified `_get_workspace_context()` to fall back to default workspace for system tasks |

---

## PRs Merged

| PR | Description |
|----|-------------|
| #641 | Workspace context fix for system tasks |

---

## Impact

- All 76 agents now have workspace context regardless of trigger source
- System tasks (Celery Beat, scheduled jobs) get context from default "Codebase" workspace
- Command tab will now show `workspace: True` for all agent executions

---

**Session 893 Workspace Context Fix Complete.**
