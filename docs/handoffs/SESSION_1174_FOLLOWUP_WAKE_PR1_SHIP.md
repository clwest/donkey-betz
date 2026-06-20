# Session 1174 — Follow-up Wake PR-1 shipped; design ratified for PR-2

**Status:** PR-1 merged-ready (open as #2334). PR-2 design locked, code not started.
**Date:** 2026-06-20
**Prior priming doc:** [SESSION_1174_PRIMING_AGENT_FOLLOWUP.md](./SESSION_1174_PRIMING_AGENT_FOLLOWUP.md)
**Driving question:** "How can Rigby follow up with agents after they begin work?"

> **Session 1175 addendum (2026-06-20, post-Session-1174 close):** Session 1174
> ended with #2334, #2336, and #2337 OPEN-but-unmerged. Session 1175 morning
> sanity check caught the drift (handoff said "SHIPPED"; `main` did not have
> the commits or migrations). All three merged to main early in Session 1175:
> - #2334 → squash-merge `a3af6131`
> - #2336 → squash-merge `6722e0bf` (resolved an `docs/INDEX.md` conflict by regenerating per DOC-AUTOGEN policy)
> - #2337 → squash-merge `c11b1600` (same INDEX regeneration pattern)
>
> Local DB had migrations 0357 + 0358 already applied (from Session 1174
> branch-local testing), so no migration run was needed post-merge. Workers
> were restarted to pick up the new code per the worker-restart memory rule.
> Treat any "SHIPPED" / "merged-ready" wording below as Session 1174's
> *prepared* state — the actual `main`-merge happened Session 1175.

## TL;DR

The agent-follow-up wake design is fully ratified end-to-end. PR-1 ships the gating schema change (`AgentExecution.conversation_id`). PR-2 builds the actual follow-up loop (signal handler → consumer → `schedule_followup` tool → Rigby-authored completion chat message + banner) on top of that field.

The original three-gap diagnosis from the priming doc holds: completions broadcast to `agent_execution_<id>` while `PAConversationConsumer` listens on `pa_conversation_<conversation_id>`, the channels never meet, and the PA FC loop has no re-invocation hook. PR-1 plus PR-2 closes all three.

## What shipped — PR-1 (#2334)

**Branch:** `session-1174-pr1-conversation-id`
**Commit:** `50f42cc1`
**Title:** `feat(session-1174): conversation_id on AgentExecution (PR-1 of follow-up wake)`

Files (6 changed, +76 / −13):
- `core/models_unified_system.py` — `AgentExecution.conversation_id = CharField(64, null, blank, db_index=True)` on the canonical model (verified canonical via Session 1084 disambiguation comment at `tasks_agents.py:1606-1625`, NOT the `core/models/agents_registry` variant).
- `core/migrations/0357_session_1174_agentexecution_conversation_id.py` — hand-trimmed migration; makemigrations swept in unrelated `AlterField` drift from other models that was rejected to keep this surgical.
- `core/tasks_agents.py` — `_impl_execute_agent_task` persists `context['conversation_id']` via the `_optional_kwargs` graceful-fallback pattern Session 1100 used for `last_heartbeat_at`.
- `core/services/td_handlers_agents.py` — `_handle_universal_agent` now promotes `conversation_id` from payload root into context (matches existing `content`/`workspace_id` promotion; `_handle_agent_tool` already had it via `_CONTEXT_PROMOTE_KEYS`).
- `tools/pa_local.sh` — repointed to `pa-58c916edf96044cc` (Session 1174 implementation thread).
- `docs/INDEX.md` — refreshed.

E2E evidence captured locally before opening PR:
- PA dispatch (`run_agent ResearchAgent` via PA chat in `pa-58c916edf96044cc`) → execution `6197202f-785d-4c8b-a9d7-3da2720f5871` has `conversation_id='pa-58c916edf96044cc'` ✓ (ResearchAgent also completed successfully — no regression).
- Direct `execute_agent_task.apply_async(args=['ResearchAgent', '...', {}], queue='long_running')` → execution `4c9a1bba-a8f9-4b14-87ef-b1afde3e2c4a` has `conversation_id=None` ✓.
- DB index created: `core_agentexecution_conversation_id_12cfe0ed` + LIKE-index.

## Design ratified (PR-2 builds against this)

### D1–D5 from priming doc — Rigby + Chris agreed

- **D1 (PR scope):** Split. PR-1 = gating schema (done). PR-2 = vertical follow-up slice.
- **D2 (re-invocation flavor):** `c2 first` — explicit `schedule_followup` PA tool. Keyed on `execution_id` (accept `task_id` as lookup convenience). c1 auto-wake deferred Phase 2.
- **D3 (UI surface):** **Both** — banner (lightweight event signal + hook for Phase 2 auto-wake) **AND** Rigby-authored chat message (load-bearing; this is what Chris explicitly asked for in the problem statement).
- **D4 (`after_seconds` cap):** 600s in Phase 1.
- **D5 (user moved on):** Still post the follow-up message, tagged as "Background completion."

### `after_seconds` semantics — TTL not delay (locked after Rigby + Claude pushback round)

Rigby initially leaned **delay-to-arm** (Celery ETA flips subscription to "armed" after N seconds). Claude pushed back with three concerns:
1. **Fast-completion drop:** if agent finishes before arm time (cached lookup in 800ms), completion arrives at un-armed subscription and is silently dropped → reintroduces "Rigby goes silent forever."
2. **Spam premise depends on a human clicking** an affordance — but here Rigby herself decides when to call `schedule_followup`; a subscription existing IS the explicit signal that the notification is wanted.
3. **State machine simpler:** `armed | expired | fired` (event-driven) vs `scheduled → armed → fired` (Celery-dependent).

Rigby conceded and added a closing invariant that immediate-arm alone wouldn't catch:
- **Subscribe-after-terminal fires immediately.** In `schedule_followup(execution_id, after_seconds)` handler: validate execution exists; if status is already terminal (`completed | failed | cancelled`), fire immediately with the payload contract and mark dedupe; else create subscription `armed` with `expires_at = now + after_seconds`. This closes the "Rigby called slightly late" / "fast agent already finished" gap.

**Final locked semantics:**
- `after_seconds` = TTL window (cap 600s).
- Subscription is **eligible immediately** upon creation.
- If execution is already terminal at subscribe time → **deliver immediately + dedupe**.
- Completion handler check: `armed && now < expires_at && not fired` → fire atomically.
- No Celery ETA dependency for Phase 1.
- States: `armed | expired | fired`.
- If real-world spam emerges Phase 2: add explicit `quiet_period_seconds` field that buffers delivery — cleaner abstraction than overloading `after_seconds` with two semantics.

### Phase 1 invariants (must-haves, all blocking on PR-2)

- **Dedupe:** at most one `agent.completed` event per `(execution_id, conversation_id)` pair. Idempotent.
- **Scope rules:** only `AgentExecution` rows with persisted `conversation_id` AND an explicit `AgentFollowupSubscription` may post follow-up. PR-1's NULL invariant for non-PA dispatches is the first half of this gate.
- **Payload contract:** `agent.completed` event always carries `{execution_id, agent_name, status, completed_at, artifact_pointers}` where `artifact_pointers = {deliverable_ids?, blog_ids?, media_ids?}` when available.
- **Failure path:** failures also fire `agent.completed` with `status=error` + short `error_signature`. Half-useful otherwise.

### Out of scope (deferred Phase 2 per ratified design)

- **Rate limiting** (per-conversation cap, collapse-into-summary on overflow) — defer unless local testing shows spam.
- **Auto-linking** deliverable→initiative→workspace — waiting on BUG-UI-001 read-side fix. PR-2 posts IDs + URLs only.
- **c1 auto-wake** (subscription-less auto-completion broadcast) — Phase 2 lift on top of subscription machinery.
- **Multi-agent fan-out follow-up** ("I dispatched 3, tell me when ALL finish").
- **Cross-conversation follow-up** (agent that wraps up while user is in a different conversation).
- **User-facing "cancel agent" affordance.**
- **Result summarization compression** (don't dump 50KB of agent output back into FC loop — needs `result_summary` field on `AgentExecution`).

## PR-2 plan (next session OR same-session continuation)

Split into **PR-2a (backend foundation)** + **PR-2b (tool + UI + demo)** so partial progress is shippable.

### PR-2a — Backend foundation

Estimated 4-6 backend files, no frontend.

1. **`AgentFollowupSubscription` model** (likely new `core/models_followup.py` or appended to `core/models_unified_system.py`).
   - Fields: `id (UUID)`, `execution_id (FK to AgentExecution)`, `conversation_id (CharField, indexed)`, `state (CharField: armed|expired|fired)`, `expires_at (DateTimeField, indexed)`, `created_at`, `fired_at (nullable)`, `result_payload (JSONField, nullable)` — last is for the payload contract snapshot.
   - Unique constraint on `(execution_id, conversation_id)` enforces dedupe at the DB layer.
2. **Migration** for the new model.
3. **Signal handler bridge** — extend `core/tasks_agents.py:send_execution_update` (or new `post_save` signal on `AgentExecution`) to ALSO push to `pa_conversation_<conversation_id>` when the row has one AND there's an `armed` subscription that's not yet `fired` and `now < expires_at`. Fail-open per Session 1172 lessons. Event payload follows the contract.
4. **`PAConversationConsumer.agent_completed` handler** in `core/consumers_pa_conversation.py`:
   - Atomically transitions subscription `armed → fired`.
   - Persists a Rigby-authored message into the conversation history server-side (the load-bearing D3 chat bubble).
   - Emits a banner event to the WebSocket for the frontend (PR-2b consumes it).
   - If the user has sent another message since dispatch (compare timestamps), tag the message as "Background completion" per D5.
5. **Cleanup task** — beat-scheduled `expire_stale_followup_subscriptions` per memory rule "Observation cadence belongs in Celery beat, not OS cron". Reaps subscriptions where `state=armed AND expires_at < now()`.
6. **Tests + handoff section for PR-2a.**

### PR-2b — Tool + UI + demo (now split into 2b-1 / 2b-2 / 2b-3)

**PR-2b-1 (SHIPPED #2337):** `schedule_followup` PA tool + subscribe-after-terminal immediate-fire. Backend-only. Stacks on #2336.

**PR-2b-2 (next session):** ChatConversation server-side persistence so the Rigby-authored "agent finished" message survives a page refresh. Requires Q-C investigation pass first (token accounting, embeddings, `last_message_at`, unread counters — pattern of bypassed side effects when writing assistant rows outside the FC loop).

**PR-2b-3 (next session):** banner UI component (`agentStore` or `bodyStore` extension + new `<AgentCompletionBanner />`) + 60s demo script (dispatch → schedule_followup → wait → completion appears in chat without user input).

#### PR-2b-2 cleanup item from Rigby's PR-2b-1 review

Rigby flagged 4 verification points on #2337; 3 of 4 were met as-shipped. The one remaining item to land in PR-2b-2:

- **Return shape stability across all paths.** Today `schedule_followup` returns the standard keys (`mode, subscription_id, state, expires_at, after_seconds, execution_id, execution_status, message`) on success paths but ONLY `{success: false, error: <msg>}` on error paths. Rigby's ask: always include the standard keys (as nulls where not applicable) so callers can treat the response shape as a stable contract. Lift the `_handle_schedule_followup` error-return helpers into a single `_make_response(success, mode=None, ...)` helper that always emits the full shape.

PR-2b-2 is the natural spot for this since it's already touching this handler to wire up the immediate-fire path's `result_payload` / artifact_pointers.

### Files to touch (estimate)

Backend (PR-2a + PR-2b):
- `core/models_unified_system.py` OR new `core/models_followup.py` — new model
- `core/migrations/0358_*.py` — new model migration
- `core/tasks_agents.py` — signal handler additions
- `core/consumers_pa_conversation.py` — `agent_completed` handler
- `core/services/pa_tool_schemas.py` — new tool schema
- `core/services/tool_dispatcher.py` — new tool handler
- `core/celery.py` — beat schedule entry for expiry cleanup
- `core/tasks.py` — `expire_stale_followup_subscriptions` task

Frontend (PR-2b):
- `frontend/src/stores/agentStore.ts` (new) or `frontend/src/stores/bodyStore.ts` (extend)
- `frontend/src/components/AgentCompletionBanner.tsx` (new)
- Hook the banner into the workspace / command center chat surface

## Known risks / open questions

- **Signal handler ordering:** the existing `send_execution_update` in `core/tasks_agents.py` currently pushes to `agent_execution_<id>`. PR-2 should extend, not replace, so existing consumers don't break.
- **PAConversationConsumer message persistence:** writing a Rigby-authored message server-side bypasses the PA FC loop entirely. Need to confirm the message format / DB model matches what Rigby's normal LLM turn produces, so it renders identically in the chat UI.
- **Dedup race:** if completion event arrives twice (Celery retry, multiple workers), the atomic `armed → fired` transition needs to be done via `update()` queryset with `state='armed'` in the filter, returning rowcount. Only the row with rowcount=1 wins.
- **Worker restart memory rule:** PR-2's changes to `tasks_agents.py` and `tool_dispatcher.py` will require a long_running + pa worker restart to pick up. Document this in the PR description.
- **Banner UI vs chat message ordering:** banner fires from WebSocket consumer, chat message lands via server-side write to conversation history. UI should render the chat message first (or both atomically) — banner-without-message would be confusing.
- **Subscribe-via-task_id lookup:** if Rigby passes `task_id` instead of `execution_id`, the tool handler must query `AgentExecution.objects.filter(input_data__celery_task_id=task_id).first()`. That JSON field query needs to be indexed or fast — verify performance on a real local DB before merging.

## Memory rules to consider updating after PR-2 lands

- `feedback_subscription_persistence_pattern.md` — new pattern: explicit subscription record for re-invocation events, with TTL + atomic state machine.
- `feedback_signal_handler_dual_broadcast.md` — when extending existing signal handlers to add a new channel, never replace the old broadcast; both must fire (existing consumers shouldn't notice).
- `feedback_server_side_assistant_message_persistence.md` — pattern for writing assistant-authored messages server-side without going through the FC loop.

## 24h watch checklist (post-PR-1 merge)

- [ ] `core_agentexecution_conversation_id_12cfe0ed` index present in prod migration apply.
- [ ] No spike in PA worker errors mentioning `_create_kwargs` or `_optional_kwargs`.
- [ ] Rate of `AgentExecution` rows with non-NULL `conversation_id` matches PA-dispatch volume (sanity check that the threading actually works in prod, not just local).
- [ ] No spike in dispatch latency (the field add + promotion are O(1) but worth confirming).
- [ ] If anything goes sideways, the rollback is simple: PR-1 is purely additive (one nullable field + one optional kwarg + one promotion line). Reverting via `migrate core 0356` + revert PR is clean.

## Session arc summary

- Session opened with Chris flagging that Rigby's "I'll poll until it completes" claim was aspirational — recon'd in SESSION_1174 priming doc but not yet built.
- Started fresh PA conversation `pa-9fabec89a10f` (Chris noted "you guys are still in my old one" — the platform had threaded my fresh-ID request back into his morning Agent-Testing conversation; health 25/100 confirmed).
- Got Rigby's point-by-point D1-D5 read; ratified design with my answers on her 3 binary Qs.
- Migrated to fresh thread `pa-58c916edf96044cc` for implementation (prior thread saturated).
- Implemented PR-1 with E2E verification on both PA and non-PA dispatch paths.
- Pushed back on Rigby's `after_seconds` delay-to-arm lean; she conceded and added the subscribe-after-terminal invariant.
- PR #2334 opened.

**Resolution status:** PR-1 ready to merge. PR-2 design fully locked. Next session (or same-session continuation) starts on PR-2a.
