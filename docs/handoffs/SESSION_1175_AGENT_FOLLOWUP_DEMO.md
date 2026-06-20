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
| Auto-wake without explicit `schedule_followup` | Phase 2 c1 — every agent dispatch creates an implicit subscription |
| Banner shows artifact links (deliverable/blog/media URLs) | Wire `artifact_pointers` field on banner + link to deliverable detail |
| Tighter same-turn exclusion on `"Background completion: "` | Compare subscription's PA chat task vs the user_message's task |
| `metadata.kind`-aware bubble badge ("Agent" pill) | Extend the Message DTO from `/api/pa/conversations/<id>/` to include `metadata`; conditionally render a badge in CommandCenterPage |
