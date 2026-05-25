---
originating_session: 931
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 931 - PA Architecture Refactor

**Date:** February 4, 2026
**Focus:** Unified PA Entrypoint + ToolDispatcher
**Status:** COMPLETE

---

## Summary

Refactored the Personal Assistant architecture to consolidate 3-4 fragmented implementations into a single canonical entrypoint with centralized tool execution.

---

## Problem Statement

The PA had multiple overlapping implementations causing:
- Inconsistent behavior between endpoints
- Silent tool failures (tools fail without trace)
- Numbers drift (609 attention items vs 17)
- No structured error handling

---

## Solution Implemented

### 1. UnifiedPAEntrypoint (Single Front Door)

**File:** `core/services/unified_pa_entrypoint.py`

All PA requests now route through a single entrypoint that:
- Builds context (user profile, conversation history, system vitals)
- Routes requests semantically or via keyword matching
- Executes tools via ToolDispatcher
- Logs outcomes with trace_id

```python
class UnifiedPAEntrypoint:
    async def process_message(self, message: str, context: Optional[Dict] = None,
                              generate_audio: bool = False) -> PAResponse
```

### 2. ToolDispatcher (No Silent Failures)

**File:** `core/services/tool_dispatcher.py`

Every tool call now returns a structured result:

```python
@dataclass
class ToolResult:
    ok: bool
    tool: str
    latency_ms: int
    error_code: Optional[str]
    error_message: Optional[str]
    trace_id: str
    result: Optional[Any]
```

Features:
- Timeout handling (default 30s, 60s for complex tools)
- Standardized error codes: TOOL_NOT_FOUND, TOOL_TIMEOUT, TOOL_ERROR
- Trace ID for debugging
- No silent failures ever

### 3. WebSocket Consumer Updated

**File:** `core/consumers_unified_v2.py`

Updated to route through UnifiedPAEntrypoint:
- `_process_through_unified_pa()` - Main processing method
- `_generate_fallback_response()` - Backup if UnifiedPA fails
- Legacy methods preserved but not primary path

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `core/services/unified_pa_entrypoint.py` | NEW | Single PA entry point |
| `core/services/tool_dispatcher.py` | NEW | Centralized tool execution |
| `core/consumers_unified_v2.py` | MODIFIED | Route through UnifiedPA |
| `docs/PERSONAL_ASSISTANT_ARCHITECTURE.md` | NEW | Full documentation |

---

## Response Contract

All PA responses now include:

```json
{
    "type": "message",
    "content": "Response text...",
    "trace_id": "abc123",
    "tool_runs": [
        {"tool": "human_decisions_tool", "ok": true, "latency_ms": 234}
    ],
    "audio_url": "/media/audio_cache/...",
    "intent": "income_generation",
    "profile_completeness": 65,
    "latency_ms": 1500
}
```

---

## Tool Inventory (47 Tools)

Documented in `docs/PERSONAL_ASSISTANT_ARCHITECTURE.md`:

| Category | Count | Status |
|----------|-------|--------|
| Creation | 8 | ✅ All working |
| Research | 7 | ✅ All working |
| ML Pipeline | 5 | ⚠️ Need audit |
| Universal Access | 2 | ✅ Working |
| Body Systems | 3 | ✅ Working |
| Intelligence | 5 | ⚠️ Need audit |
| Workflow | 5 | ✅ Working |
| Legal | 1 | ✅ Working |

---

## TTS Integration

Already implemented in Session 926:
- `ListenButton.tsx` component
- `/api/tts/generate/` endpoint
- Cost warning modal for long content
- "Listen to All" for conversations

---

## Next Steps (Session 932+)

1. ~~**Attention Aggregator** - Single endpoint returning labeled counts (system vs human)~~ ✅ DONE
2. **Wire REST API** - Route `views_personal_assistant.py` through UnifiedPA
3. **Audit "Needs Audit" tools** - ML Pipeline and Intelligence tools
4. **Learning Loop** - Define success signals for tool executions

---

## Session 932 Addition: Attention Aggregator

Fixed the 609 vs 17 attention items mismatch.

**New Files:**
- `core/services/attention_aggregator.py` - Unified attention aggregator

**New Endpoints:**
- `GET /api/assistant/attention/unified/` - Full unified response
- `GET /api/assistant/attention/stats/` - Stats only (fast)

**Usage:**
```python
from core.services.attention_aggregator import get_attention_aggregator

aggregator = get_attention_aggregator(user)
result = aggregator.get_unified_attention()
# Returns both system_attention and human_attention with clear labels
```

---

## Testing

To test the new architecture:

1. Connect to WebSocket at `/ws/assistant/`
2. Send: `{"type": "message", "content": "Find me income opportunities"}`
3. Response should include `trace_id` and `tool_runs` array

---

## Related Documentation

- [PERSONAL_ASSISTANT_ARCHITECTURE.md](../PERSONAL_ASSISTANT_ARCHITECTURE.md) - Full PA documentation
- [SESSION_930_USER_CONTEXT_LEARNING.md](SESSION_930_USER_CONTEXT_LEARNING.md) - Profile interview
- [SESSION_926_UNIVERSAL_AGENT_VOICE.md](SESSION_926_UNIVERSAL_AGENT_VOICE.md) - TTS integration
