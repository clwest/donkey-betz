# Session 1172 — Rigby Live Tool Status in Chat UI

**Date:** 2026-06-20
**Workspace:** `Session 1172 — Rigby Live Status in Chat UI` (`42b5aca6-25ac-49bd-aa5d-4a19686c6b71`)
**PRs:** [#2329](https://github.com/clwest/donkey-betz-platform/pull/2329) (vertical slice), [#2330](https://github.com/clwest/donkey-betz-platform/pull/2330) (async-emit fix)

## TL;DR

The chat UI was silent between user submit and final reply, so a multi-tool turn (Rigby calling `cockpit_tool` → `work_tool` → `deliverable_tool`) looked indistinguishable from a stalled worker. Chris flagged this 12+ hours into Session 1171 — "the problem with the current UI is if Rigby is working on something behind the scenes there's really no way to tell."

Shipped a vertical slice: backend emits `rigby.tool.started` / `rigby.tool.completed` events to the existing `pa_conversation_<id>` WebSocket group; React frontend renders a thin ticker above the chat input. Verified E2E from a Python WebSocket client.

## Behavioral invariants (post-merge)

- During any PA function-calling turn, the WebSocket subscribers of `pa_conversation_<conversation_id>` receive `rigby.tool.started` immediately before the tool runs and `rigby.tool.completed` immediately after, on all 5 exit paths (denied / not-found / success / timeout / exception).
- `trace_id` is the PA-level `pa-N-XXXXXXXX` join key.
- `seq` is monotonic per (process, trace_id); UI dedupes by `(trace_id, seq)` on reconnect.
- `arg_summary` and `result_summary` are always empty strings in Phase 1 (privacy by default).
- The `CommandCenterPage` chat input renders the ticker (`RigbyToolTicker`). `GlobalPADock` is NOT instrumented in Phase 1.
- Non-PA dispatch paths (direct agent calls, scripts, helper agents in `unified_pa_entrypoint` outside the main FC loop) do NOT emit events — `pa_trace_id` defaults to `None` and the helpers short-circuit.
- Channels-layer push failures are WARN-logged but never block tool execution.

## Architecture map

```
User → POST /api/pa/chat/ → process_pa_chat_task (Celery, pa queue)
                                    │
                                    ▼
                          UnifiedPAEntrypoint.process_message
                          │  (creates pa_trace_id = "pa-N-XXXXXXXX")
                          ▼
                          tool_dispatcher.execute(
                              ...,
                              pa_trace_id=trace_id,         ← threaded through
                              conversation_id=self.conversation_id,
                          )
                                    │
                                    ▼
                          ┌─────────┴─────────┐
                          │ tool runs (async) │
                          └─────────┬─────────┘
                                    │
                          await emit_tool_started(...)   ← group_send
                          await tool_body(...)
                          await emit_tool_completed(...)  ← group_send
                                    │
                                    ▼
                Channels Layer (Redis): pa_conversation_<id> group
                                    │
                                    ▼
                Daphne PAConversationConsumer.rigby_tool_{started,completed}
                                    │
                                    ▼
                WebSocket → React CommandCenterPage onMessage
                                    │
                                    ▼
                Zustand paStore: handleToolStarted / handleToolCompleted
                                    │
                                    ▼
                RigbyToolTicker reads activeTool / recentTool
                                    │
                                    ▼
                "Rigby is using cockpit_tool..."  ←  visible to user
                "Rigby used cockpit_tool · 10236ms"
```

## Event contract (1172-1 spec)

```
rigby.tool.started:
  trace_id        str  PA-level (e.g. "pa-1-45705add") — join key
  seq             int  monotonic per (process, trace_id)
  tool_call_id    str  dispatcher-internal id (e.g. "tool-73-4a5ad99e")
  tool_name       str  stable, human-readable
  started_at      str  ISO 8601 UTC
  arg_summary     str  Phase 1: always ""

rigby.tool.completed:
  trace_id        str
  seq             int
  tool_call_id    str
  tool_name       str
  latency_ms      int
  status          str  "ok" | "error"
  result_summary  str  Phase 1: always ""
```

## Rollback levers

| Change | Disable / revert |
|---|---|
| Emit calls (any/all) | Revert PRs #2329 + #2330. Pure-add code, no schema, no migrations. |
| Per-callsite disable | Pass `pa_trace_id=None` at the relevant PA dispatch site — one-line change. |
| UI escape hatch | `localStorage['pa-dock-state']['activeTool']=null` + reload. |
| Channels-layer kill switch | Set `CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}` to force events into a per-process layer that nobody subscribes to. (Last resort — also kills the existing message.created flow.) |

## 24h watch checklist

```bash
# 1) Verify ticker events fire on real PA turns
grep "pa_status_events" celery-pa.log | tail -20
# Expect SILENCE on the happy path; WARNINGS only if channels-layer
# fails. Any WARNING here means the chat UI ticker missed.

# 2) Confirm dispatcher is using await (no sync-from-async errors)
grep "AsyncToSync in the same thread" celery-pa.log | tail -5
# Expect: nothing. If anything appears, the fix from PR #2330 regressed.

# 3) E2E from a Python WS client (anytime you want fresh proof)
python <<'EOF'
import asyncio, json, websockets, subprocess
async def main():
    async with websockets.connect(
        "ws://localhost:8000/ws/pa/conversations/pa-9fabec89a10f/"
        "?token=<chris-token>"
    ) as ws:
        subprocess.Popen([
            ".venv/bin/python", "tools/pa_chat.py",
            "Quick check — run cockpit queue_lengths",
            "--tools", "--conversation", "pa-9fabec89a10f"
        ], env={"PA_API_URL":"http://localhost:8000", "PA_API_TOKEN":"<token>"})
        for _ in range(20):
            msg = json.loads(await asyncio.wait_for(ws.recv(), 25))
            if "rigby.tool" in msg.get("type",""):
                print(msg)
asyncio.run(main())
EOF
```

## Forensic artifact: discovery + first-fix evidence

The vertical slice (PR #2329) shipped but didn't actually work — `async_to_sync` failed silently. The follow-on PR #2330 found and fixed it. Lesson: the same fail-open pattern that makes channel emits safe ALSO hides bugs from us. **Always end-to-end verify with a real WebSocket subscriber, not just "the warning logs are quiet."**

Memory rule saved: `feedback_async_to_sync_inside_async_handler.md` (this session).

## Tickets + Rigby deliverables

| Ticket | Initiative ID | Status | Rigby deliverable |
|---|---|---|---|
| 1172-1 Spec | `0189d4af-dcf5-4f18-9094-50e6f160fb0d` | COMPLETED | `2af9f96b-2bca-466c-9cb6-d60efe05684d` |
| 1172-2 Backend events | `71f923b8-40d9-4d73-8109-860ea272dc67` | (TBD — PR #2329 + #2330 merged) | — |
| 1172-3 Frontend ticker | `fb90b7b3-4bda-4222-856b-f02fb2a24f1d` | (TBD — PR #2329 merged) | — |
| 1172-4 E2E test | `e7c2c54f-525c-4526-911a-d41429dfe24c` | COMPLETED via WS subscriber | — |
| 1172-5 60s demo clip | `7642702e-1607-48c6-8dfd-0983de8bb2c7` | DEFERRED to Chris's screen recording | — |

## Out of scope (Phase 2)

- `arg_summary` / `result_summary` content — per-tool opt-in whitelist.
- "Rigby is thinking" indicator BEFORE the first tool fires (separate UX problem).
- Per-tool drilldown or history pane.
- Mirroring ticker into `GlobalPADock` (currently CommandCenter only).
- Instrumenting helper-agent dispatch sites in `unified_pa_entrypoint` beyond the 3 main FC-loop sites.
- Instrumenting non-PA tool callers (direct agent calls, management commands) — would require a different join key than `pa_trace_id`.

## Memory rules saved (Session 1172)

- `feedback_async_to_sync_inside_async_handler.md` — never use `async_to_sync` inside an `async def` function; `await` the underlying coroutine directly.
- `feedback_verify_e2e_not_just_silent_logs.md` — fail-open helpers hide silent bugs from log-tail verification. Always exercise the full path with a real consumer.
