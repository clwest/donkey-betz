---
originating_session: 1043
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1043 - Brainstorm Bulk Export Endpoint

**Date:** February 19, 2026
**Focus:** Add paginated `list` action to brainstorm tool for bulk conversation export

---

## Problem

The PA identified ~13,256 agent-to-agent brainstorm conversations (last 30 days) but had no way to enumerate them at scale. The existing `brainstorm_tool` actions (`search`, `recent`, `details`, `stats`) only return small result sets (limit 10-20). A grounding classification audit (A-F categories) requires bulk access.

## Changes

### 1. `list_conversations()` in BrainstormSearchService

**File:** `core/services/brainstorm_search_service.py`

New method with offset-based pagination:
- Filters AgentConversation by `Discussion:`/`Panel:` prefix + date range
- Optional `conversation_type` ('discussion'/'panel'), `status` filters
- Returns per conversation: id, topic, type, started_at, status, message_count, quality_score, conclusion (truncated 300 chars), participants (agent names)
- `include_transcript=True` adds full messages array
- Pagination metadata: `total_count`, `offset`, `limit`, `has_more`

### 2. `list` action in tool dispatcher

**File:** `core/services/tool_dispatcher.py` (in `_handle_brainstorm`)

New `elif action == 'list':` block delegating to `list_conversations()`. Limit capped at 200.

### 3. Updated PA tool schema

**File:** `core/services/pa_tool_schemas.py`

- `list` was already in the action enum (added in session 1036)
- Added new params: `offset` (int), `days` (int), `type` (string), `status` (string), `include_transcript` (boolean)
- Updated description to mention bulk listing

### 4. PA formatter + NLU payload builder

**File:** `core/services/unified_pa_entrypoint.py`

- **Payload builder:** Added `list` action detection for "list all", "export", "enumerate", "bulk" keywords with offset/limit/days extraction
- **Formatter:** Markdown table with #, Type (D/P), Topic, Msgs, Participants, Date columns. Pagination hint when `has_more`.

## Files Modified

| File | Lines Changed |
|------|--------------|
| `core/services/brainstorm_search_service.py` | +80 (new method) |
| `core/services/tool_dispatcher.py` | +20 (new action block) |
| `core/services/pa_tool_schemas.py` | +13 (new params) |
| `core/services/unified_pa_entrypoint.py` | +51 (formatter + payload) |
| `docs/topics/personal-assistant.md` | Updated tool list |

## Verification

```bash
# Railway shell
railway run python manage.py shell -c "
from core.services.brainstorm_search_service import brainstorm_search_service
r = brainstorm_search_service.list_conversations(days_back=30, offset=0, limit=5, include_transcript=True)
print(f'Total: {r[\"total_count\"]}, returned: {len(r[\"conversations\"])}, has_more: {r[\"has_more\"]}')
"
```

PA prompts to test:
1. "List all brainstorm conversations from the last 30 days"
2. "List brainstorm conversations offset 50 limit 50"
3. "Export all panel discussions"
