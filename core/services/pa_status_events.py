"""Live PA tool-lifecycle status events for the chat UI (Session 1172).

When the Personal Assistant (Rigby) is in the middle of a function-calling
turn, the chat UI was previously silent until the final reply landed — a
multi-tool turn (cockpit_tool → work_tool → deliverable_tool) was visually
indistinguishable from a stalled worker. This module emits lightweight
`rigby.tool.started` / `rigby.tool.completed` events to the same channel
group the chat client is already subscribed to (`pa_conversation_<id>`),
so the UI can render a thin "Rigby is using <tool>..." ticker.

## Event contract (Session 1172, ticket 1172-1)

Both events go to the existing PA conversation group. Subscribers (the
React ChatUI) dedupe by `(trace_id, seq)`.

```
rigby.tool.started:
  trace_id        str   PA-level trace id (e.g. "pa-1-45705add") — join key
  seq             int   monotonic per (process, trace_id); UI orders by this
  tool_call_id    str   tool-dispatcher internal id (e.g. "tool-73-4a5ad99e")
  tool_name       str   stable, human-readable (e.g. "cockpit_tool")
  started_at      str   ISO 8601 UTC timestamp
  arg_summary     str   Phase 1: always "" (opt-in per tool deferred)

rigby.tool.completed:
  trace_id        str
  seq             int   monotonic per (process, trace_id) — continues from started
  tool_call_id    str
  tool_name       str
  latency_ms      int
  status          str   "ok" | "error"
  result_summary  str   Phase 1: always "" (opt-in per tool deferred)
```

## Failure semantics

All emits are fire-and-forget. Any exception during channel-layer push
is logged at WARNING and swallowed — the tool execution never blocks
on telemetry. If `pa_trace_id` or `conversation_id` is missing the
emit is a no-op (true backward-compat for non-PA dispatch paths).

## Backward compatibility

Pre-1172 callers (`tool_dispatcher.execute(...)` without `pa_trace_id`)
still work — the helpers no-op when join keys are absent. Only PA
pipelines that explicitly thread their trace_id through opt into the
live ticker.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from typing import Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


# Per-process monotonic counter keyed by pa_trace_id. UI uses this to
# order events and dedupe on reconnect. Memory-bounded by `_MAX_TRACES`
# (FIFO eviction) so a long-running worker doesn't accumulate trace
# entries indefinitely.
_seq_lock = threading.Lock()
_seq_counters: dict[str, int] = {}
_MAX_TRACES = 1024


def _next_seq(pa_trace_id: str) -> int:
    """Return the next monotonic seq for a PA trace_id. Thread-safe."""
    with _seq_lock:
        next_val = _seq_counters.get(pa_trace_id, 0) + 1
        _seq_counters[pa_trace_id] = next_val
        # FIFO eviction when we've accumulated too many trace_ids. Python
        # dicts preserve insertion order since 3.7, so popping the first
        # key gives us the oldest seen trace.
        if len(_seq_counters) > _MAX_TRACES:
            oldest = next(iter(_seq_counters))
            if oldest != pa_trace_id:
                _seq_counters.pop(oldest, None)
        return next_val


def _group_name(conversation_id: str) -> str:
    """PA conversation channel group name — must match consumer."""
    return f"pa_conversation_{conversation_id}"


def _emit(group: str, payload: dict) -> None:
    """Fire-and-forget push to the channel layer. Never raises."""
    try:
        layer = get_channel_layer()
        if layer is None:
            logger.debug("[pa_status_events] no channel layer configured — skip emit")
            return
        async_to_sync(layer.group_send)(group, payload)
    except Exception as exc:
        # Channels failures must never block tool execution.
        logger.warning(
            "[pa_status_events] failed to emit %s to %s (%s: %s) — chat UI ticker miss",
            payload.get("type", "?"),
            group,
            type(exc).__name__,
            exc,
        )


def emit_tool_started(
    *,
    pa_trace_id: Optional[str],
    conversation_id: Optional[str],
    tool_call_id: str,
    tool_name: str,
) -> Optional[int]:
    """Push `rigby.tool.started` to the PA conversation group.

    Returns the assigned `seq` so the caller can pair the matching
    `completed` event with the same `seq + 1` reference if needed (not
    required — `emit_tool_completed` will compute its own next seq).

    No-op (returns None) if either join key is missing — non-PA dispatch
    paths simply skip telemetry rather than emitting orphan events.
    """
    if not pa_trace_id or not conversation_id:
        return None
    seq = _next_seq(pa_trace_id)
    _emit(
        _group_name(str(conversation_id)),
        {
            "type": "rigby.tool.started",
            "trace_id": pa_trace_id,
            "seq": seq,
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "arg_summary": "",  # Phase 1: per-tool opt-in deferred
        },
    )
    return seq


def emit_tool_completed(
    *,
    pa_trace_id: Optional[str],
    conversation_id: Optional[str],
    tool_call_id: str,
    tool_name: str,
    latency_ms: int,
    status: str,
) -> Optional[int]:
    """Push `rigby.tool.completed` to the PA conversation group.

    `status` must be "ok" or "error" (the chat UI uses this to pick the
    icon — checkmark vs warning glyph).

    Returns the assigned seq, or None if either join key is missing.
    """
    if not pa_trace_id or not conversation_id:
        return None
    seq = _next_seq(pa_trace_id)
    _emit(
        _group_name(str(conversation_id)),
        {
            "type": "rigby.tool.completed",
            "trace_id": pa_trace_id,
            "seq": seq,
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "latency_ms": int(latency_ms),
            "status": status if status in ("ok", "error") else "ok",
            "result_summary": "",  # Phase 1: per-tool opt-in deferred
        },
    )
    return seq
