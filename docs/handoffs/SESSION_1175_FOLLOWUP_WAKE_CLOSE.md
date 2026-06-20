# Session 1175 — Follow-up wake vertical slice closed (PR-1 through PR-2b-3 all merged)

**Status:** All 5 PRs from the Session 1174+1175 follow-up wake design merged to main. Live-verified end-to-end in the browser. Vertical slice complete.
**Date:** 2026-06-20
**Driving question (Session 1174):** "How can Rigby follow up with agents after they begin work?"
**Driving question (Session 1175):** "Can the user actually see it work, end-to-end, in a browser?"
**Prior session handoffs:**
- [SESSION_1174_PRIMING_AGENT_FOLLOWUP.md](./SESSION_1174_PRIMING_AGENT_FOLLOWUP.md) — design recon + 5 design decisions for Rigby ratification
- [SESSION_1174_FOLLOWUP_WAKE_PR1_SHIP.md](./SESSION_1174_FOLLOWUP_WAKE_PR1_SHIP.md) — design ratification + PR-1 ship (later updated with Session 1175 addendum recording actual merge SHAs)
- [SESSION_1175_AGENT_FOLLOWUP_DEMO.md](./SESSION_1175_AGENT_FOLLOWUP_DEMO.md) — 60s demo script for the shipped feature

## TL;DR

Session 1174 ended with three PRs OPEN-but-unmerged (#2334 / #2336 / #2337) and a fourth (PR-2b-2) entirely unwritten. Session 1175 morning sanity check caught the drift, merged the three feature PRs, then shipped PR-2b-2 (server-side ChatConversation persistence + 11-key return-shape stability) and PR-2b-3 (banner UI + WS wiring + 60s demo). All five PRs are now in main; the feature was live-verified in the browser at session close (Rigby dispatch → subscribe → agent completes → banner flashes + Rigby chat bubble appears + survives hard refresh).

## What landed

| PR | Title | Squash SHA | Where |
|---|---|---|---|
| #2334 | PR-1 — `AgentExecution.conversation_id` (gating field) | `a3af6131` | `core/models_unified_system.py:889` |
| #2335 | Session 1174 handoff + Session 1175 entry-point doc | `b9880967` | `docs/handoffs/SESSION_1174_FOLLOWUP_WAKE_PR1_SHIP.md` + `00-START-NEXT-SESSION.md` |
| #2336 | PR-2a — Subscription model + signal bridge + consumer `agent.completed` handler + beat-scheduled expiry cleanup | `6722e0bf` | `core/models_unified_system.py:1017` (model), `core/tasks_agents.py:99` (signal bridge), `core/consumers_pa_conversation.py:171` (handler), `core/tasks.py:12917` (expire task) |
| #2337 | PR-2b-1 — `schedule_followup` PA tool + subscribe-after-terminal immediate-fire path | `c11b1600` | `core/services/td_handlers_agents.py:4429` |
| #2338 | PR-2b-2 — Server-side ChatConversation persistence in `agent_completed` consumer + 11-key return-shape stability on `schedule_followup` | `5e2bc956` | `core/consumers_pa_conversation.py:34` (3 module-level sync helpers), `core/services/td_handlers_agents.py:4411` (`_make_followup_response` helper) |
| #2339 | PR-2b-3 — Agent-completion banner UI + WS wiring + 60s demo script | `d68175ef` | `frontend/src/stores/paStore.ts` (store ext), `frontend/src/components/AgentCompletionBanner.tsx` (new), `frontend/src/pages/CommandCenterPage.tsx` (wiring), `docs/handoffs/SESSION_1175_AGENT_FOLLOWUP_DEMO.md` (demo) |

## Live verification trail

Four smokes ran end-to-end against `main` during Session 1175. All five executions completed and all checks passed.

| Smoke | Execution ID | Verification | Result |
|---|---|---|---|
| #1 (backend) | `3c368059-9cca-40a2-82ab-ae6df0d3ac7c` | dispatch → subscribe → completion → ChatConversation row 540 persisted with correct Rigby-bubble fields. Subscription `43506dd5` armed→fired in 21ms, row persisted 48ms after completion | ✅ |
| #2 (backend, fast agent) | `eeee7eca-4e3f-480d-83a4-f16c13400253` | Agent finished in 5s (before PA's async user_message write) → row 542 persisted with NO prefix (correct — no qualifying user_message existed at completion time) | ✅ |
| #2b (backend, slower agent + DB-injected user message) | `64bee7a5-666f-412f-b3d7-c6472f16f309` | Detector saw the dispatch user_message row 545 (written before completion) → row 546 persisted with **"Background completion: "** prefix end-to-end | ✅ |
| #3 (live browser, post-PR-2b-3) | `11ae30e7-be76-4a7a-83ad-6ec1b001f8ff` | Built bundle on `:8000` hard-refreshed. Subscription `ae94d8b9` fired → **banner flashed in composer footer** + Rigby completion bubble appeared in chat + survived hard refresh | ✅ |

## Behavioral invariants (now true post-merge)

1. **Every PA-originated agent dispatch has `AgentExecution.conversation_id` stamped.** Non-PA dispatches keep it NULL. (PR-1 gating field; PR-2a's `fire_agent_followup_subscriptions` bails on NULL conv_id.)
2. **At most ONE `agent.completed` event per `(execution_id, conversation_id)` pair.** Atomic `armed → fired` queryset update with `state='armed'` in the filter — rowcount=1 wins under any concurrent calls. (PR-2a.)
3. **Subscribe-after-terminal fires immediately.** If `schedule_followup` is called for an execution that's already in a terminal status, the immediate-fire path runs synchronously through the same atomic helper and emits the event in the same tool turn. (PR-2b-1.)
4. **`schedule_followup` always returns the same 11-key shape.** Success or error, the keys `{success, mode, subscription_id, execution_id, execution_status, state, expires_at, fired_at, after_seconds, message, error}` are always present (None where not applicable). (PR-2b-2.)
5. **Server-side ChatConversation persistence is fire-and-forget — no token/cost/embedding/last_message_at/unread side effects.** Q-C investigation confirmed ChatConversation has zero `post_save` signals. The persisted row renders identically to a regular Rigby turn (no metadata-aware variant rendering today). (PR-2b-2.)
6. **The "Background completion: " prefix is timestamp-based** — fires iff a ChatConversation row exists in the same conversation with `user_message != ''` AND `created_at > subscription.created_at` AND `metadata.kind != 'agent_completion'`. (PR-2b-2 / Rigby's ratified stricter heuristic.)
7. **Banner fires on `agent.completed` WS event AND auto-fades after 6s.** Independent of the persisted chat bubble (banner is the live signal, bubble is the load-bearing record that survives refresh). (PR-2b-3.)

## Rollback levers per PR

- **#2334 (PR-1):** Purely additive. Revert via `git revert a3af6131` + `python manage.py migrate core 0356` (drops the column + index). One nullable field + one optional kwarg + one promotion line; no callers depend on the field being present.
- **#2336 (PR-2a):** New model + signal bridge + consumer handler + beat task. Revert via `git revert 6722e0bf` + `python manage.py migrate core 0357` (drops AgentFollowupSubscription model). The signal bridge fail-opens, so reverting can't break the dispatch path. Beat task entry needs `add_critical_celery_tasks` regen to clean up.
- **#2337 (PR-2b-1):** Pure addition to `td_handlers_agents.py`. Revert removes the tool schema + handler; Rigby would get "unknown tool" if she tries to call it.
- **#2338 (PR-2b-2):** Pure source-only change. Revert removes the server-side persistence + the return-shape helper. The consumer's `agent_completed` falls back to the PR-2a WS-event-only behavior (banner stops working in browser but no crashes).
- **#2339 (PR-2b-3):** Frontend-only. Revert removes the banner from the composer footer. Backend keeps firing the WS event but the frontend ignores it.
- **Per-callsite disable for the whole feature (without revert):** Comment out the `fire_agent_followup_subscriptions(execution_record)` calls in `core/tasks_agents.py` (5 sites — completion, failure, soft-time-limit, generic-exception, dedup-skip). The store-time gates (PR-1's `conversation_id` field, PR-2a's subscription model) remain but no events fire, no rows persist, no banners flash.

## 24h watch checklist (post-merge)

```bash
# (1) PR-1 schema invariant — every PA-dispatched execution has conversation_id stamped
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
total = AgentExecution.objects.filter(created_at__gte=since).count()
with_conv = AgentExecution.objects.filter(created_at__gte=since).exclude(conversation_id__isnull=True).count()
print(f'last 24h: {total} executions, {with_conv} with conversation_id ({100*with_conv/total:.1f}%)')"
# Expect: with_conv > 0 (proves the field is populating on PA dispatches).
# Ratio depends on PA-vs-autonomous mix; falling to 0% on a known-active PA day is the alarm.

# (2) PR-2a subscription state machine — armed → fired transitions
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentFollowupSubscription
from collections import Counter
states = Counter(AgentFollowupSubscription.objects.values_list('state', flat=True))
print(dict(states))"
# Expect: roughly fired >> armed, expired present in small numbers.
# armed-only build-up → signal handler not firing.

# (3) Banner WS event is reaching the browser — count agent.completed broadcasts
grep -c 'agent.completed' .logs/daphne.log 2>/dev/null || echo '0 (or check log path)'
# Expect: ~one per fired subscription.

# (4) Beat-scheduled expire task is alive
.venv/bin/python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
p = PeriodicTask.objects.filter(task='core.tasks.expire_stale_followup_subscriptions').first()
print(f'enabled={p.enabled} last_run_at={p.last_run_at}' if p else 'NOT FOUND')"
# Expect: enabled=True with a recent last_run_at.

# (5) ChatConversation persistence is firing on completions
.venv/bin/python manage.py shell -c "
from core.models.conversations.models import ChatConversation
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
cnt = ChatConversation.objects.filter(
    created_at__gte=since,
    metadata__contains={'kind': 'agent_completion'},
).count()
print(f'agent_completion rows in last 24h: {cnt}')"
# Expect: roughly matches the count of armed→fired subscriptions in the same window.
```

## Open follow-ups (not blocking)

| # | Item | Why deferred |
|---|---|---|
| 1 | **Conv-ID divergence between dispatch and tool-context within a single Rigby turn.** Wrapper pinned at X → dispatch stamps execution.conversation_id=X → but `schedule_followup`'s payload context resolved to Y. PR-2a's cross-conversation guard rejected (defensive — correct), but the root-cause divergence in `unified_pa_entrypoint`'s conv_id plumbing is worth understanding. Reproduced Session 1175 morning between `pa-639751f029bc432f` (old wrapper pin) and `pa-58c916edf96044cc` (Rigby's tool-context). | Doesn't affect the feature once wrapper + tool-context are aligned (which is the case for `pa-58c916edf96044cc` now). Worth a small recon PR. |
| 2 | **Timing-dependent "Background completion: " prefix on same-turn dispatches.** When the agent is slow enough that completion lands AFTER the PA's async user_message write (smoke #2b pattern), the prefix fires even though the user never moved on. Timestamp-based heuristic working as ratified; documented in the demo script. If users find it misleading, future PR can add a same-turn exclusion (compare subscription's source PA chat task vs the user_message's task). | Behavior is consistent with the unit-tested contract; deferred until real-world UX feedback. |
| 3 | **Phase 2 c1 — auto-wake without explicit `schedule_followup`.** Every agent dispatch creates an implicit subscription so the user gets the completion message without Rigby needing to call the tool. Cleaner UX; subscription machinery is in place. | Out of scope for the explicit-subscribe-MVP design (D2 in the 1174 ratification). |
| 4 | **Phase 2 — multi-agent fan-out follow-up.** "Tell me when ALL three finish." Subscription rollup helper + new tool variant. | Out of scope; deferred per ratification. |
| 5 | **Phase 2 — cross-conversation follow-up.** Agent dispatched from conv A; user moves to conv B; completion delivered to conv B. | Out of scope; current invariant is same-conv only. Would require a separate mechanism. |
| 6 | **Banner enrichment — artifact_pointers as inline links.** The WS event payload already includes `artifact_pointers` (deliverable_ids / blog_ids / media_ids). The banner shows the agent name + status today; could extend to "Agent X finished — 2 deliverables" with click-through to the deliverable detail. | Visual nice-to-have; not load-bearing. |
| 7 | **`metadata.kind`-aware bubble badge.** The persisted ChatConversation row has `metadata.kind='agent_completion'` but the frontend chat bubble doesn't inspect metadata, so it renders identically to a normal Rigby turn. Could add a subtle "Agent" pill. Would require extending `/api/pa/conversations/<id>/` to expose `metadata` in the Message DTO. | Per ratified design, identical rendering was acceptable. |
| 8 | **Result summarization compression.** Don't dump 50KB of agent output back into the FC loop on the next turn. Needs a `result_summary` field on `AgentExecution`. | Out of scope for the wake feature; ties into broader memory/context architecture. |
| 9 | **User-facing "cancel agent" affordance** with subscription cleanup. | Out of scope; subscription state machine reserved `cancelled` for this. |

## Patterns worth capturing (Session 1175 specific)

1. **Always verify the handoff against `git log --oneline main` before trusting it.** Session 1175 morning recon caught that #2334/#2336/#2337 were OPEN-but-unmerged even though the Session 1174 handoff said "SHIPPED." Lesson: handoffs document the *prepared* state, not the *historical* state, unless the PR is squash-merged before close. The handoff-vs-reality check should be the first move on any session that says "X is already shipped."
2. **`metadata__kind='X'` (Django JSON lookup) silently excludes default-metadata rows from `.exclude(...)` due to Postgres NULL ternary logic.** `metadata->>'kind' = 'X'` returns NULL when `metadata={}`, and `NOT NULL` is NULL (treated as not-true in WHERE), so the row gets dropped. Switch to `metadata__contains={'kind': 'X'}` (JSONB containment) when you want to keep rows where the key is absent.
3. **The "last mile UI" rule has a literal interpretation: which bundle is the browser running?** Session 1175 PR-2b-3 looked broken because Chris's browser was loading the stale Django-served bundle while my edits lived on the vite dev server. Diagnostic order: check the `<script src>` of `index.html` from the actual origin the user is on, not from my dev server. If it's a stale hash, run `npm run build && cp frontend/dist/index.html core/templates/index.html && python manage.py collectstatic --no-input && make stop && make start` and have the user hard-refresh.
4. **Auth scoping splits dev and prod frontends.** `:3000` (vite dev) and `:8000` (Django + built bundle) don't share session cookies in this stack — `/api/*` calls from `:3000` return 401 because the session is bound to the `:8000` origin. Worth understanding before assuming a "frontend bug" — most "WS isn't connecting" symptoms on `:3000` are actually 401s upstream of the WS handshake.

## Session 1176 priorities (recommended)

Per the open follow-ups above, the natural next thread is whichever of #1–#3 lines up with Chris's priorities. My lean:

- **Highest-leverage / lowest-risk:** Item #1 (conv-ID divergence recon). Small fact-finding PR that documents where dispatch vs tool-context conv_id are pulled from in `unified_pa_entrypoint`. If they're sourced from the same place and we just witnessed a stale-pin artifact, close with a note. If they're really sourced differently, that's a real correctness issue to flag.
- **Highest-UX-leverage:** Item #6 (banner artifact-pointer enrichment). Banner is visible to the user; making it richer is direct user value with no schema or design risk.
- **Highest-architecture-leverage:** Item #3 (auto-wake / c1). Once Rigby doesn't need to manually call `schedule_followup`, the feature stops requiring an explicit tool invocation per agent dispatch — significantly more useful in practice.

The 1175 session arc summary is captured in this handoff; no priming doc needed unless Session 1176 picks up a different thread entirely.
