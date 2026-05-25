---
originating_session: 996
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 996: Initiative Ownership System

**Date:** February 12, 2026
**Focus:** Add accountability to initiatives via owner fields + PA actions + auto-assignment

## Problem

The PA told the user there was an "owner selector" for Initiatives, but no `owner` field existed on the Initiative model. `InitiativeActionItem` had `assigned_agent`/`assigned_user`, but the parent Initiative only had `created_by` (a CharField string, not a FK). ~169 active initiatives with no accountability. The PA couldn't answer "who owns this?" or "show me my initiatives."

## What Was Built

### 1. Model Changes
- Added `owner` FK to `UnifiedUser` (nullable, SET_NULL, related_name=`owned_initiatives`)
- Added `owner_agent` CharField (max_length=100, blank, default='')
- Migration: `0239_session_996_initiative_ownership` (applied locally + Railway)

### 2. PA Tool Handler (`tool_dispatcher.py`)
- **Owner filter on `list`:** `owner=me` (current user), `owner=unowned` (no owner), `owner=<name>` (agent name search)
- **Owner in `list` serialization:** Bulk-resolves owner_ids to usernames, adds `owner` field to each item
- **Owner in `details`:** Resolves owner FK or owner_agent to display name
- **New `assign_owner` action:** Takes `id` + `agent_name` or `user_name`, validates, sets owner, returns old/new owner
- Updated valid actions error message

### 3. PA Intent Detection + Payload Builder + Formatter (`unified_pa_entrypoint.py`)
- **Intent routing:** "assign owner", "who owns", "my initiatives", "unowned", "transfer ownership", "take ownership" all route to initiatives intent (checked BEFORE generic initiative match)
- **Payload builder:** `assign_owner` extracts ID + target agent/user; `my initiatives` → `owner=me`; `unowned` → `owner=unowned`; `who owns` → `details` action
- **Formatters:** `assign_owner` → "Done. **[name]** is now owned by **[new_owner]** (was: [old_owner])." Owner badge `[AgentName]` shown in list. "Owner: [name]" line in details. Also added formatters for `update_status` and `advance` actions.

### 4. Auto-Ownership Rules
- **`PROGRAM_OWNER_MAP`** in `initiative_integration_service.py`: Maps 8 programs to default owner agents (e.g., content_pipeline → ContentStrategyAgent, research → ResearchAgent)
- **`_auto_assign_owner(initiative)`** method: (1) If program matches map → use it; (2) Else if created_by looks like an agent name (not system/PA/human) → use created_by; (3) Otherwise leave unowned
- **4 creation paths patched:**
  - `InitiativeIntegrationService.get_or_create_initiative()` — calls `_auto_assign_owner()` after stage init
  - `ConversationInitiativePipeline` — calls `_auto_assign_owner()` after creation
  - `HiveMindExecutionPipeline` — calls `_auto_assign_owner()` after creation
  - `AgentDream.promote_to_initiative()` — sets `owner_agent` from dream's agent directly

## Files Changed (8)

| File | Change |
|------|--------|
| `core/models_document_registry.py` | +`owner` FK, +`owner_agent` CharField |
| `core/migrations/0239_session_996_initiative_ownership.py` | Auto-generated migration |
| `core/services/tool_dispatcher.py` | `assign_owner` action, owner filter/serialization in list/details |
| `core/services/unified_pa_entrypoint.py` | Intent detection, payload builder, formatters |
| `core/services/initiative_integration_service.py` | `PROGRAM_OWNER_MAP`, `_auto_assign_owner()` |
| `core/services/conversation_initiative_pipeline.py` | Call auto-assign after creation |
| `core/services/hivemind_execution_pipeline.py` | Call auto-assign after creation |
| `core/models_unified_system.py` | Set `owner_agent` in `promote_to_initiative()` |

## PA Commands

| Command | What Happens |
|---------|-------------|
| "show my initiatives" | Lists initiatives where `owner` = current user |
| "unowned initiatives" | Lists initiatives with no owner |
| "who owns [name]?" | Shows initiative details with owner |
| "assign [name] to ResearchAgent" | Sets owner_agent = ResearchAgent |
| "take ownership of [name]" | Sets owner FK = current user |
| "transfer ownership of [name] to [agent]" | Reassigns owner |

## Verification

- All 7 Python files pass `py_compile` syntax check
- Migration applied locally and on Railway
- 169 existing initiatives confirmed as unowned (will get owners as new initiatives are created or via PA assign command)
