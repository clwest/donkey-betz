# Session 1175 — Agent follow-up wake demo (60s script)

> **Closes the vertical slice** for Session 1174 + 1175's follow-up wake design.
> Backend (PR-1 / PR-2a / PR-2b-1 / PR-2b-2) + frontend (PR-2b-3) all merged.
> This script is what you run to *see* the feature work end-to-end in a browser.

## What this demonstrates

Rigby tells you when an agent finishes — even if you scrolled away from the
chat or moved on to a different conversation. The completion lands as a
real Rigby chat bubble in the conversation history (survives page refresh)
AND a transient banner fires in the composer footer the instant the WS
event arrives.

## Setup (one-time)

```bash
# Backend
make all              # daphne + celery + ml worker

# Frontend
cd frontend && npm run dev   # vite on :5173 (or whatever Vite picks)
```

## 60-second demo

> All times approximate. Best run with a fresh PA conversation so the chat
> surface is empty when the completion lands.

| Time | Action | What you should see |
|---|---|---|
| **0:00** | Open `http://localhost:5173/command-center` in the browser. Log in if needed. | Command Center loads. |
| **0:05** | Click "New conversation" in the sidebar. | Empty chat. The PA WS connects (check devtools: `ws://localhost:8000/ws/pa/conversations/<id>/`). |
| **0:10** | Type: `"Dispatch ResearchAgent with task: explain what a fixture is in software testing, two sentences."` Send. | Rigby's reply lands. She invokes `dispatch_agent` (tool ticker fires) and then `schedule_followup` (second tool ticker). |
| **0:25** | Rigby's text reply: "Subscribed to ResearchAgent completion." Scroll up in the chat — pretend you're reading older messages. | Chat history scrolled away from bottom. |
| **0:40** | ResearchAgent completes (~10–20s after dispatch). | **AgentCompletionBanner** appears in the composer footer: `✓ Agent ResearchAgent finished · see chat below`. Auto-fades after 6s. |
| **0:45** | Scroll back to the bottom of the chat. | A new Rigby bubble: `Agent **ResearchAgent** finished (execution `...`).` Optionally rendered as Markdown. |
| **0:55** | Hard-refresh the browser (Cmd+Shift+R). | The Rigby completion bubble is **still there** in conversation history — that's the load-bearing persistence from PR-2b-2 (ChatConversation row with `metadata.kind='agent_completion'`). |

## What you're testing

| Layer | What | Where |
|---|---|---|
| **PR-1 (#2334)** | `AgentExecution.conversation_id` populated on dispatch | DB row `core_agentexecution.conversation_id` |
| **PR-2a (#2336)** | Atomic `armed → fired` flip on completion + broadcast | `fire_agent_followup_subscriptions` in `core/tasks_agents.py:99` |
| **PR-2b-1 (#2337)** | `schedule_followup` PA tool (subscribe in same turn as dispatch) | `_handle_schedule_followup` in `core/services/td_handlers_agents.py:4429` |
| **PR-2b-2 (#2338)** | Server-side ChatConversation persistence (survives refresh) | `create_completion_row` in `core/consumers_pa_conversation.py:88` |
| **PR-2b-3 (this PR)** | Live banner + WS event wiring in the chat UI | `AgentCompletionBanner.tsx` + `handleAgentCompleted` in `paStore.ts` |

## Background-completion path (extended demo)

To exercise the `"Background completion: "` prefix:

1. After step 0:25 above, before the agent finishes, send a follow-up user message:
   `"While we're waiting — what's the weather like today?"`
2. Rigby answers.
3. When the agent eventually finishes (still inside the 180s subscription window),
   the persisted Rigby bubble is prefixed: `Background completion: Agent **ResearchAgent** finished...`.

This works because the detector (`check_background_completion` in
`core/consumers_pa_conversation.py:50`) sees a ChatConversation row with
non-empty `user_message`, `created_at > subscription.created_at`, and
`metadata.kind != 'agent_completion'` — exactly Rigby's stricter
"user moved on" heuristic.

> **Timing nuance (Session 1175 PR-2b-2 live smoke finding):** if the
> agent finishes *during the same PA turn* that dispatched it (i.e. the
> agent is fast enough that completion lands before the dispatching
> user_message row is written), the prefix CAN fire on what looks like
> a single-turn flow. The detector heuristic is timestamp-based and the
> behavior is consistent with the unit-tested contract. PR-2b-3 keeps
> it as-is — if the prefix proves misleading in practice, a future PR
> can tighten with a same-turn exclusion (compare the user_message to
> the PA chat task that armed the subscription).

## Failure-path demo

Replace the dispatch in step 0:10 with an agent task that will fail
(e.g. malformed input the agent can't recover from). The banner shows
`⚠ Agent X failed — <error_signature>` and the persisted Rigby bubble
shows the failure shape.

## Verification queries (after the demo)

```bash
# The persisted completion row
USE_PGBOUNCER=1 .venv/bin/python manage.py shell --command "
from core.models.conversations.models import ChatConversation
import json
rows = ChatConversation.objects.filter(metadata__contains={'kind': 'agent_completion'}).order_by('-created_at')[:3]
for r in rows:
    print(f'id={r.id} conv={r.conversation_id} status={r.metadata.get(\"status\")} text={r.assistant_response[:80]!r}')
"

# Subscription state machine
USE_PGBOUNCER=1 .venv/bin/python manage.py shell --command "
from core.models_unified_system import AgentFollowupSubscription
for s in AgentFollowupSubscription.objects.order_by('-created_at')[:5]:
    print(f'{s.id} state={s.state} fired_at={s.fired_at} expires_at={s.expires_at}')
"
```

## When you'd want to extend this

| Want | What to ship |
|---|---|
| Multi-agent fan-out ("tell me when ALL three finish") | Phase 2 — subscription rollup helper + new tool variant |
| Auto-wake without explicit `schedule_followup` | **Shipped Session 1178 (Phase 2 c1)** — see § below |
| Banner shows artifact links (deliverable/blog/media URLs) | Wire `artifact_pointers` field on banner + link to deliverable detail |
| Tighter same-turn exclusion on `"Background completion: "` | Compare subscription's PA chat task vs the user_message's task |
| `metadata.kind`-aware bubble badge ("Agent" pill) | Extend the Message DTO from `/api/pa/conversations/<id>/` to include `metadata`; conditionally render a badge in CommandCenterPage |

---

## Phase 2 — auto-wake (Session 1178)

Phase 1 above requires Rigby to call `schedule_followup(execution_id, after_seconds)` after every dispatch. Phase 2 makes the subscription implicit: every PA-originated agent dispatch auto-creates an armed `AgentFollowupSubscription` at `execute_agent_task` entry, with a 30s default TTL. Rigby still has `schedule_followup` available as an override (custom TTL, re-fire after expiry, deterministic test harnesses).

Ratified design card (Rigby sign-off Session 1178):

| D | Decision | Choice |
|---|---|---|
| D1 | Replace vs augment vs coexist | **Augment** — auto-sub at dispatch, explicit `schedule_followup` still works as an override |
| D2 | Default `after_seconds` for auto-sub | **30s** |
| D3 | Scope | **PA-only** — gated on `AgentExecution.conversation_id IS NOT NULL` (PR-1 invariant) |
| D4 | Opt-out mechanism | **Per-call only** — Rigby passes `auto_followup: false` in `run_agent` args |
| D5 | Multi-agent dispatch | **One banner per agent** — fan-out rollup deferred (Phase 1 open follow-up #4) |
| D6 | Where the implicit sub is created | **At `execute_agent_task` entry**, right after `AgentExecution.create` with `conversation_id` stamped. Dedupe is DB-guaranteed via `unique_together = [('execution', 'conversation_id')]` on `AgentFollowupSubscription` (`core/models_unified_system.py:1089`). Race-safe with `schedule_followup`. |

Code path:

```
PA chat → run_agent (auto_followup defaults True)
  → execute_agent_task entry (tasks_agents.py:1894+)
    → AgentExecution.objects.create(conversation_id=X, ...)
    → create_implicit_followup_subscription(execution, context)
       → get_or_create(execution=…, conversation_id=X, defaults={state='armed', expires_at=now+30s})
       → returns existing row if explicit schedule_followup raced ahead
  → agent runs → completion → fire_agent_followup_subscriptions
    → atomic armed → fired → pa_conversation_X group_send
    → PAConversationConsumer.agent_completed
       → persist Rigby-authored ChatConversation row + emit banner event
```

### Demo: 60-second auto-wake (no explicit `schedule_followup`)

Same setup as Phase 1 (Local stack up, browser at `http://localhost:8000/` on the pinned conversation):

```bash
# 1. Dispatch ResearchAgent through Rigby via the standard PA path.
#    Crucially: do NOT call schedule_followup. Auto-wake takes care of it.
tools/pa_local.sh "Run ResearchAgent on this task: summarize the current OpenAI rate-limit page. One paragraph."
```

What you should see:

1. Rigby returns the task_id in chat as usual.
2. **No explicit `schedule_followup` tool run appears in the verbose tool ticker.** (That's the point.)
3. ~5-30s later, the AgentCompletionBanner flashes in the composer footer.
4. A Rigby-authored chat bubble appears in the conversation with the agent's summary (subject to PR-2b-2 prefix rules).
5. Hard-refreshing the browser keeps the chat bubble (the banner is the live signal; the bubble is the durable record).

Then verify in the shell:

```bash
# Auto-sub was created at dispatch time (look for [auto_followup] created … in logs)
USE_PGBOUNCER=1 .venv/bin/python manage.py shell --command "
from core.models_unified_system import AgentFollowupSubscription
for s in AgentFollowupSubscription.objects.order_by('-created_at')[:3]:
    print(f'{s.id} state={s.state} created={s.created_at} fired_at={s.fired_at}')
"
# Expect: top row state='fired' (or 'armed' if the agent's still running)
# Expect: TTL ≈ 30s (created vs expires_at delta)
```

### Demo: opt-out via `auto_followup: false`

Useful for test-harness dispatches or sub-tasks where the banner would be noise.

```bash
tools/pa_local.sh "Run ResearchAgent on this short task (no follow-up needed): summarize OpenAI rate-limit page in one sentence. Pass auto_followup=false on the run_agent call."
```

What you should see:

1. Rigby dispatches as normal.
2. **No banner**, no Rigby completion bubble, even after the agent finishes.
3. The execution row exists, completes, and is queryable via `job_status` — the user just doesn't get the implicit completion event.

Then verify:

```bash
# No subscription created for this execution
USE_PGBOUNCER=1 .venv/bin/python manage.py shell --command "
from core.models_unified_system import AgentExecution, AgentFollowupSubscription
ex = AgentExecution.objects.order_by('-created_at').first()
print(f'execution {ex.id} status={ex.status} conv={ex.conversation_id}')
print(f'subscriptions for this execution: {AgentFollowupSubscription.objects.filter(execution=ex).count()}')
"
# Expect: 0 subscriptions despite a non-NULL conversation_id (opt-out won)
```

### How Phase 2 changes the Phase 1 demo

Phase 1 worked end-to-end if Rigby remembered to call `schedule_followup`. Phase 2 makes the implicit case the default — Rigby can ignore the tool entirely and the banner still fires. The explicit tool remains useful when:

- Rigby wants a longer TTL window than 30s (still capped at 600s).
- Rigby wants to subscribe to an execution she didn't dispatch herself in this turn (e.g., re-subscribe after the implicit sub expired).
- A test harness wants the deterministic immediate-fire path (subscribe-after-terminal) to verify the banner without timing-sensitivity.
