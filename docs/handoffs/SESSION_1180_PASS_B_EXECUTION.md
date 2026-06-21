# Session 1180 — Pass B live execution: 3 structural fixes + 6 cells closed

**Status:** All 6 cells of Pass B matrix closed (3 PASS, 3 FAIL → remediated this session). 3 PRs merged on main; 2 Phase 3 PRs queued + 1 separate finding.
**Date:** 2026-06-20
**Pinned conversation:** `pa-a5fecc400c0f4152` (Session 1180 thread, healthy)
**Driving question:** "Is the agent follow-up wake loop actually wired end-to-end across the 6 stress-test cells Rigby drafted in Session 1179?"
**Prior session handoffs:**
- [SESSION_1179_PASS_B_MATRIX_DRAFTED.md](./SESSION_1179_PASS_B_MATRIX_DRAFTED.md) — matrix scaffold + code-walk predictions
- [SESSION_1178_AGENT_AUTO_WAKE_PHASE2.md](./SESSION_1178_AGENT_AUTO_WAKE_PHASE2.md) — Phase 2 auto-wake (the thing Pass B was testing)

## TL;DR

Pass B execution surfaced **three structural defects** in the agent follow-up wake loop, all fixed this session:

| # | Finding | PR | Architectural move |
|---|---|---|---|
| **P1** | 60s TTL races slow agents (ThinkingAgent 67s blew 60s in live verify) | **#2350** | Decouple sub expiry from agent runtime (auto-wake → `expires_at=NULL`) |
| **Cell 3** | Cancel terminal doesn't fire followup → leaked armed subs forever post-P1 | **#2351** | Add `fire_agent_followup_subscriptions` call to cancel path |
| **Cell 4** | Completion row only written if consumer subscribed at fire time (refresh = silent drop) | **#2352** | Decouple persistence from WS consumer (write row server-side in fire helper) |

The pattern across all three: **decouple a lifecycle concern from a wall-clock/connection-state concern.** That's now the architectural contract for the wake loop.

## PRs merged on main (in order)

| PR | SHA | Theme | Tests |
|---|---|---|---|
| **#2350** | `920cae05` | `feat(session-1180-agent-wake)` — completion-bound auto-followup (`expires_at` nullable) + idempotent completion rows | 10/10 |
| **#2351** | `cc3acef9` | `fix(session-1180-agent-wake)` — cancel terminal must fire followup subscriptions | 11/11 |
| **#2352** | `a6659096` | `fix(session-1180-agent-wake)` — server-side completion-row persistence (decouple from WS consumer) | 13/13 |

Total: 6 files modified, 1 migration (0359), 4 new tests, 0 regressions.

## Pass B matrix — final cell-by-cell results

| Cell | Theme | Result | Evidence |
|---|---|---|---|
| **5** | Second-tab dedupe | PASS-with-caveat | TTL race fix verified live (62s ThinkingAgent fired with `expires_at=NULL`). 2-consumer dedupe not reproducible from browser UI — SPA opens 1 PA-WS per conv across tabs (frontend-side dedupe). Unit test covers the 2-consumer collision case. |
| **3** | Revoke/cancel terminal | FAIL → fixed (PR #2351) | Cancel-path code-walk + DB simulation (exec `3ec70a67`, sub stayed `armed` forever post-P1). Live revoke blocked by separate Finding #4 (threaded-worker SIGTERM limitation). |
| **4** | Refresh-mid-run + WS reconnect | FAIL → fixed (PR #2352) | Cell 5 Run 2 already proved case (b): 49s ThinkingAgent ran, 0 consumers at fire time → 0 rows. Server-side persistence in PR #2352 closes (a)+(b)+(c) uniformly. |
| **7** | Multi-agent fanout (2 agents in one turn) | PASS | ResearchAgent (53.8s) + ThinkingAgent (51.4s) dispatched in same Rigby FC turn. Both subs fired, both rows persisted server-side, no collision. Banner-overwrite frontend concern remains as code-walk finding → Phase 3 PR4. |
| **8** | Media-artifact agent | FAIL → queued (Phase 3 PR5) | ImageAgent generated image (`output_data.metadata.images` populated), but `fire_agent_followup_subscriptions` hardcodes `artifact_pointers={}` at `tasks_agents.py:197`. Bubble surfaces "ImageAgent finished" with no link. |
| **6** | Tab-not-focused / backgrounded | PASS-by-reference | Post-PR #2352, persistence is execution-lifecycle-dependent, not WS-connection-dependent. Tab focus/visibility at fire time cannot cause loss of the bubble. Banner-refire-on-focus = nice-to-have, not correctness defect. |

## Open Phase 3 items (queued, not blocking)

| Item | Type | Scope estimate |
|---|---|---|
| **PR4** — banner queue / toast stack for multi-agent fanout | UI/UX | `paStore.ts:350-356` — replace single `recentAgentCompletion` slot with a queue; head fades over ~6s, then next item shows |
| **PR5** — populate `artifact_pointers` in fire helper from `execution_record.output_data` | Backend | Pluggable per-agent extractor (ImageAgent → `media_ids` from `output_data.metadata.images`, ContentWriterAgent → `deliverable_id`, etc) + bubble click-through |
| **Finding #4** — threaded-worker SIGTERM revoke limitation | Ops/Config | `long_running` queue is `--pool=threads --concurrency=2`. Celery `terminate=True` can't kill Python threads. Options: switch to `--pool=prefork`, document the limitation, or add a workaround `cancel` PA tool that updates DB + fires helper directly. |

## Evidence log

All cell-by-cell evidence (timestamps, execution_ids, subscription state transitions, SQL row counts) lives in deliverable `ffa23f86-91bd-4a5f-8797-7c649643ad57` ("Rigby: Session 1180 — Pass B Follow-up Wake: Live Execution Evidence Log"). Grew from 0 → ~10 KB across ~7 append calls (used append-only per `feedback_deliverable_tool_use_append_for_large_payloads`).

Source matrix lives in deliverable `61247479-1976-4ba8-bc8a-ea67f66ead45` (drafted Session 1179, ratified Session 1180).

## Behavioral invariants post-Session-1180

These are now load-bearing contracts on the wake loop:

1. **Auto-wake subs are execution-lifecycle-bound** (`expires_at=NULL`). Fire when execution reaches terminal regardless of runtime. Beat hygiene job is forbidden from expiring NULL-expiry rows (`expires_at__isnull=False` in filter).
2. **Explicit `schedule_followup(after_seconds=N)` keeps its delayed-reminder semantic.** Time-bounded TTL, expires via beat job. Different use case from completion wake.
3. **Completion row persistence is execution-lifecycle-dependent, not WS-connection-dependent.** `fire_agent_followup_subscriptions` writes the row server-side BEFORE broadcasting. Consumer-side `create_completion_row` remains as a no-op safety net via PR #2350's idempotency check.
4. **Cancel terminal fires the followup like every other terminal.** `agent_router.py` cancel path calls `fire_agent_followup_subscriptions(execution_record)` after the `status='cancelled'` UPDATE. Payload's `status` field reflects 'cancelled' (via `refresh_from_db` before the call).
5. **Idempotency per `(conversation_id, execution_id)` for completion rows.** App-level `get_or_create`-equivalent (lookup-then-create pattern). JSON-expression partial unique index deferred to a later hardening PR.
6. **Fail-open both directions in the fire helper.** Persist failure → still broadcast (connected consumers see live banner). Broadcast failure → still persisted (next history fetch surfaces bubble).

## Rollback / disable levers

Per `feedback_handoff_operational_sections.md` (Session 1165 standard):

| Lever | When to use | How |
|---|---|---|
| Revert PR #2350 | If P1 NULL-expiry causes unexpected leaks in some other path | `git revert 920cae05` + run migration `0358` (migration 0359 is just `AlterField`-nullable, safe to revert) |
| Revert PR #2351 | Cancel-path fire breaks something (very unlikely, fail-open wrapped) | `git revert cc3acef9` |
| Revert PR #2352 | Server-side persistence has unexpected DB pressure or duplicate-row issue | `git revert a6659096`. Consumer-side persistence (the pre-#2352 path) still works. |
| Disable auto-wake entirely | If the whole feature needs to soften | Pass `auto_followup: false` in PA tool `run_agent` calls (per-call opt-out per Session 1178 D4) |
| Hand-edit beat hygiene to expire NULL rows | If leaked armed rows become an issue (shouldn't, but) | `core/tasks.py:expire_stale_followup_subscriptions` — remove the `expires_at__isnull=False` filter. ⚠️ this kills NULL-expiry semantics entirely |

## 24h watch checklist

- [ ] Tail `celery-long-running.log` for `[auto_followup]` events — confirm `created` lines fire on PA dispatches, `fail-open` is absent
- [ ] Tail same log for `[router-cancel] fire_agent_followup_subscriptions fail-open` — should be absent
- [ ] Check `SELECT COUNT(*) FROM core_agentfollowupsubscription WHERE state='armed' AND expires_at IS NULL AND created_at < NOW() - INTERVAL '6 hours'` — should be 0 (or close to it). Anything > 10 suggests a terminal-save path we missed.
- [ ] Check `SELECT COUNT(*) FROM chat_conversations WHERE metadata->>'kind'='agent_completion' AND created_at > NOW() - INTERVAL '1 hour'` — confirms rows are persisting. Should non-zero if any agents dispatched.

## Carryover from prior sessions (still riding)

PgBouncer follow-up verifications, narrative dedup, agent-name dim checks, retry-policy bulk migrations, `pg_stat_statements` on staging/prod, `capture_pa_acks_health_snapshot` slow-task investigation, COO consolidation deferreds. Plus Session 1178 deferred items: `auto_followup_skipped` traceability stamp, EditorAgent observability dashboard (C3 from #2343).

## Conversation health (post-session)

`pa-a5fecc400c0f4152` is the active coord thread. Used heavily this session — Rigby tool ran ~15 times (deliverable_tool appends + execution_history_tool + image_generation_agent dispatch). Worth a `session_tool health_check` next session to see if it's near retirement threshold.

## What worked

- **Rigby as Pass B lead.** Every architectural decision (P1 over P2/P3, bundle Cell 5 fix into P1, P3-b over P3-a) went through her with explicit options + tradeoffs. Three PRs landed clean because she ratified scope before code was written.
- **Memory rule `feedback_corpus_walks_surface_mechanism_drift`** kicked in twice: once when Chris flagged "agents might take minutes" (halted Pass B, shipped P1 instead of bandaging); once when Cell 5 Run 2's WS disconnect surfaced the deeper persistence-vs-consumer coupling (halted Cell 4 live test, shipped PR #2352 instead).
- **Decoupling pattern.** Once P1 named the move ("lifecycle-bound vs runtime-bound"), Cells 3 and 4 became applications of the same principle. Consistency made each subsequent PR scope smaller.

## What was harder

- **Frontend SPA opens one WS per conversation across tabs** — discovered mid-Cell-5 when the daphne log showed only 1 PA-WS Connected event despite Chris's two browser tabs. Made strict 2-consumer dedupe untestable from the UI. Resolved by trusting unit test + accepting PASS-with-caveat.
- **Threaded-worker SIGTERM revoke can't kill Python threads** — Finding #4 from Cell 3 attempt 1. Standard Celery limitation but easy to forget. Forced the DB-simulation approach (Attempt 2) to land Cell 3 evidence.
- **First Cell 5 run had a 90s WS-disconnect-before-dispatch window** — surfaced by the daphne log post-hoc. Highlighted that `[PA-WS] Connected` events need to be live-tailed during stress tests, not grep'd after. Background `tail -F | grep &` doesn't persist cleanly through the tool harness — falling back to post-hoc grep was fine here but worth noting for future cell runs.
