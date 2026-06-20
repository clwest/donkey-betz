# Session 1174 — PRIMING: Rigby autonomous follow-up on dispatched agents

**Status:** PRIMING DOC — work has not started.
**Date drafted:** 2026-06-20 (end of Session 1173)
**Trigger:** Chris asked "how can Rigby follow up with Agents after they begin work?" while Rigby was busy running platform validation. Recon done; work deferred to a fresh session.

## Problem statement

Rigby dispatches an agent to `long_running` queue, hands back a task_id, and her function-calling turn ends. She has no autonomous way to know the agent finished, much less proactively tell the user. Today's UX:

> User: "Rigby, run the ContentWriterAgent on this brief."
> Rigby: "Task dispatched (id=abc123). Use job_status to check progress."
> *[silence forever, until user manually asks]*

What Chris wants:

> Rigby: "Task dispatched (id=abc123). I'll check back when it finishes."
> *[~30s later, in the same conversation]*
> Rigby: "ContentWriterAgent finished. Here's the result..."

## Recon findings (file:line)

1. **Dispatch is async + fire-and-forget**: `core/services/td_handlers_agents.py:997` calls `execute_agent_task.apply_async(args=[agent_name, task_text, context], queue='long_running')`. PA's FC loop exits immediately after returning the task_id message to the user.

2. **Completions broadcast to the WRONG group**: `core/tasks_agents.py:81-96` (`send_execution_update`) uses `async_to_sync(channel_layer.group_send)(f"agent_execution_{execution_id}", ...)`. PA conversation consumer subscribes to `pa_conversation_<conversation_id>` (`core/consumers_pa_conversation.py:50`). The two groups are disjoint — completion never reaches Rigby's conversation channel.

3. **No PA-side polling tool**: `core/services/pa_tool_schemas.py` has a media-generation `job_status` action (line 1326, 1334) but no generic agent-status checker Rigby can call.

4. **No in-conversation tracking of pending work**: `UnifiedPAEntrypoint` knows the `conversation_id` throughout (`unified_pa_entrypoint.py:213,475,712`) but never stores `pending_executions` for that conversation. The task_id is plain-text in the assistant message and forgotten by the next turn.

5. **No re-invocation mechanism for the PA loop**: `_run_agentic_loop` is one-shot. There's no "wake Rigby back up when X happens" path.

## The three gaps

To enable autonomous follow-up, all three must close. Closing any subset gets partial behavior:

| Gap | What it enables on its own |
|---|---|
| **(a)** Signal handler that pushes AgentExecution completion to `pa_conversation_<id>` | UI ticker / banner could show "agent finished" in the chat surface, but Rigby herself is still asleep |
| **(b)** New consumer handler `agent_completed` in `PAConversationConsumer` | (only useful in combination with a) — pure plumbing |
| **(c)** Re-invocation mechanism for Rigby's FC loop with the completion result | Without a+b, this is the actual answer. Two flavors: (c1) scheduled "check back" task at dispatch time, OR (c2) new tool Rigby self-invokes (e.g., `schedule_followup(task_id, after_seconds=30)`) |

## Proposed Phase 1 scope (Session 1174)

Vertical slice, ~1-2 hours:

**1174-1 — AgentExecution gets conversation_id**: thread `conversation_id` through `execute_agent_task.apply_async` and persist on the AgentExecution row. Required precondition for any follow-up to know whose conversation to ping.

**1174-2 — Signal handler ping PA conversation group**: in `core/tasks_agents.py` `send_execution_update` (or a new post-save signal), ALSO push to `pa_conversation_<conversation_id>` when the row has one. Event name: `agent.completed` with `task_id`, `agent_name`, `status` (ok/error), `result_summary`, `latency_ms`. Fail-open (lessons from Session 1172).

**1174-3 — PA consumer handler**: add `async def agent_completed(self, event)` to `PAConversationConsumer`. Phase 1 surfaces this as a chat-side banner (similar shape to Rigby tool ticker) — user sees "✓ ContentWriterAgent finished" inline.

**1174-4 — Re-invoke Rigby with the result** (the hard one): choose between:
- **(c1)** At dispatch time, schedule a Celery beat-style follow-up that re-enters the PA pipeline with a synthetic "system message" containing the agent's result. Pro: works with any tool Rigby calls. Con: needs `process_pa_chat_task` to accept a system-message variant.
- **(c2)** Add a new PA tool `schedule_followup(task_id, after_seconds=30)` that Rigby explicitly calls when she wants to be re-woken. Pro: surgical, opt-in per tool call. Con: requires Rigby to remember to use it.

**1174-5 — Handoff + memory rules + 60s demo** per the vertical-slice pattern.

## Design decisions to put to Rigby before code (Session 1174 step 1)

- **D1**: Closing scope — all 4 tickets in one PR, or split (a+b in PR 1, c in PR 2)?
- **D2**: Re-invocation flavor — c1 (auto-wake) or c2 (explicit tool)? c1 feels more like "magic," c2 feels more like "Rigby intentionally choosing." Could ship both, c2 first.
- **D3**: Should `agent.completed` events also push to the UI ticker (Session 1172 component) or get their own banner? Probably banner — different semantic from "Rigby is using X tool."
- **D4**: How long should `schedule_followup` allow as `after_seconds`? Cap at 600s (10min) initially? Beyond that is a different feature (scheduled work).
- **D5**: What happens if the user has moved on (sent another message) before the follow-up fires? Skip the follow-up message? Append regardless? Park as a notification?

## Files to touch (estimate)

- `core/tasks_agents.py` — signal handler additions
- `core/models_*.py` — `conversation_id` field on AgentExecution (likely migration needed)
- `core/services/td_handlers_agents.py` — thread `conversation_id` at dispatch
- `core/consumers_pa_conversation.py` — `agent_completed` handler
- `core/services/pa_tool_schemas.py` + `core/services/tool_dispatcher.py` — new `schedule_followup` tool (if c2)
- `core/services/unified_pa_entrypoint.py` — system-message re-entry if c1
- Frontend: `bodyStore` or new `agentStore` for the banner state, plus a small banner component

## Known risks / questions

- AgentExecution model already has `~22` fields per a glance at `core/models_agent_*.py`. Adding `conversation_id` is fine but migration timing matters.
- If we go c1 (auto-wake), `process_pa_chat_task` will need an idempotency check so two completing agents don't double-fire the PA loop.
- The PA worker (`pa` queue) is solo-pool. Re-entering the FC loop from a completion event is single-threaded; backlog risk if many agents complete simultaneously.

## Out of scope (Phase 2+)

- Multi-agent fan-out follow-up ("I'm running 3 agents in parallel, I'll tell you when all finish").
- User-facing "cancel agent" affordance.
- Result summarization compression (don't dump 50KB of agent output back into the FC loop — needs a `result_summary` field on AgentExecution).
- Cross-conversation follow-up (agent that wraps up while user is in a different conversation).

## Session 1174 step 1

Open a fresh workspace with Rigby, paste the design decisions above, get sign-off, then code 1174-1 first (conversation_id on AgentExecution + dispatch threading) since every other ticket depends on it.
