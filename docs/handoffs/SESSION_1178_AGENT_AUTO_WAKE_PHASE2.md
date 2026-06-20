# Session 1178 — Phase 2 auto-wake shipped + live-verified + TTL hotfix

**Status:** All four PRs merged to main. Phase 2 auto-wake live and working end-to-end (both happy-path and opt-out verified backend-side). One real bug caught 4 minutes after the first merge — TTL hotfix shipped in the same session. Single-source-of-truth contract for the TTL window now enforced via CI test.
**Date:** 2026-06-20
**Driving question:** "Check back in with Rigby on where we are working with the Agents and what's next on the list." (Chris's Session 1177 close instruction.)
**Prior session handoffs:**
- [SESSION_1174_PRIMING_AGENT_FOLLOWUP.md](./SESSION_1174_PRIMING_AGENT_FOLLOWUP.md) — original Phase 1+2 design recon
- [SESSION_1175_FOLLOWUP_WAKE_CLOSE.md](./SESSION_1175_FOLLOWUP_WAKE_CLOSE.md) — Phase 1 c2 shipped (5 PRs merged + live verified)
- [SESSION_1176_AGENT_DISPATCH_RECON_CLOSE.md](./SESSION_1176_AGENT_DISPATCH_RECON_CLOSE.md) — recon + 3 findings (F1/F2/F3)
- [SESSION_1177_AGENT_DISPATCH_DEFENSE.md](./SESSION_1177_AGENT_DISPATCH_DEFENSE.md) — F1 + F3 fixed (PR #2342, #2343); failed-banner visual confirmed

## TL;DR

Phase 2 c1 = **every PA-originated agent dispatch auto-creates an armed `AgentFollowupSubscription`** at `execute_agent_task` entry. Rigby no longer has to call `schedule_followup` explicitly — the user gets the completion banner + Rigby-authored chat bubble by default. The explicit tool remains as an override (custom TTL, deterministic test harnesses).

Source-only — no migrations. Dedupe is DB-guaranteed via the existing `unique_together = [('execution', 'conversation_id')]` on `AgentFollowupSubscription` (`core/models_unified_system.py:1089`). `get_or_create` is race-safe with explicit `schedule_followup` for free.

Conv-ID recon (Session 1175 open follow-up #1) was done as part of the kickoff — finding: **not a real bug; close it.** Plumbing is invariant within a turn; Session 1175 divergence was wrapper-pin staleness across separate requests.

## What landed

| Item | Where | Status |
|---|---|---|
| Conv-ID divergence recon (open #1) | This handoff § "Conv-ID recon" | **Findings filed; closes #1 as "wrapper hygiene, not a bug"** |
| Phase 2 PR-1 — auto-wake | [PR #2345](https://github.com/clwest/donkey-betz-platform/pull/2345) merged at `9c5c944b` | **MERGED.** 6/6 unit tests green. Rigby review nits addressed (commit `64a81ab9`). |
| **Hotfix — TTL bump 30s→60s + shared model constants** | [PR #2347](https://github.com/clwest/donkey-betz-platform/pull/2347) merged at `039435fe` | **MERGED.** Caught by live verify; single source of truth on `AgentFollowupSubscription`. |
| **Cross-path invariant test** | [PR #2348](https://github.com/clwest/donkey-betz-platform/pull/2348) merged at `3185beb7` | **MERGED.** CI-enforced: Phase 1 and Phase 2 defaults can't drift again. |
| Demo doc Phase 2 section | `docs/handoffs/SESSION_1175_AGENT_FOLLOWUP_DEMO.md` | Appended (happy path + opt-out variant) |

## Contract update — D2 superseded by live verify

The original Session 1178 design card D2 ratified **30s** as the implicit auto-wake default. **Live verify caught that as wrong 4 minutes after the original merge** — ResearchAgent completion at 23:19:05 vs subscription expiry at 23:19:03 → 2-second race → sub stuck `armed`, no banner, no Rigby bubble. The exact silent-failure mode Phase 2 was meant to eliminate.

**Current contract (post-hotfix #2347):**

- `AgentFollowupSubscription.DEFAULT_TTL_SECONDS = 60` (was 30 in PR #2345)
- `AgentFollowupSubscription.MAX_TTL_SECONDS = 600` (unchanged; Phase 1 D4)
- **Both Phase 1 explicit (`_handle_schedule_followup`) and Phase 2 implicit (`create_implicit_followup_subscription`) read from these model constants — no hardcoded TTL literals elsewhere in the codebase.**
- Future changes to either constant require touching one place (the model class). CI test `test_default_after_seconds_matches_model_constant` (Phase 1 suite) fails if the explicit-tool default drifts from the model constant.

## Live verify trail (post-merge to main)

Two-pass verification, fully end-to-end:

| Pass | Execution ID | TTL config | Result |
|---|---|---|---|
| #1 (initial #2345 merge) | `d7fc8c50-...` | 30s | ❌ Sub expired 2s before completion. `fire_*` filter `expires_at__gt=now` returned 0 rows. Silent no-op. Bug confirmed. |
| #2 (post-hotfix #2347) | `2b1892c1-...`, sub `92c8eed2-...` | 60s | ✅ Sub created 23:26:55 (TTL 60s), flipped `armed → fired` at 23:27:25, ChatConversation row 588 persisted at 23:27:25. **Zero explicit `schedule_followup` calls.** |
| #3 (opt-out, post-hotfix) | `06f63afe-...` | n/a | ✅ `input_data.context.auto_followup = False` flowed through PA schema → `_CONTEXT_PROMOTE_KEYS` → context. Subscription count: 0. Silent skip. |

Browser side: ChatConversation row 588 exists in conv `pa-9b82bcc72e1945ce`. Chris's browser refresh shows the Rigby completion bubble for the ResearchAgent dispatch. The banner is a 6s-auto-fade transient UI element — not reproducible post-hoc but the persistent bubble is the load-bearing record.

## Conv-ID recon — Open follow-up #1 close-out

**Finding: NOT a real bug at runtime.** Within one `process_pa_chat_task` invocation, conversation_id is invariant from the View entrypoint through to `AgentExecution.conversation_id` and the matching `AgentFollowupSubscription.conversation_id`. Code trace:

| # | Where | Line | What |
|---|---|---|---|
| 1 | View | — | `process_pa_chat_task.apply_async(args=…, conversation_id=X)` |
| 2 | `core/tasks.py` | 11382 | task signature `(... conversation_id=None ...)` accepts the kwarg |
| 3 | `core/tasks_misc.py` | 4752 | `UnifiedPAEntrypoint(user, conversation_id=conversation_id)` |
| 4 | `core/services/unified_pa_entrypoint.py` | 258, 1637 | `self.conversation_id` set once, injected into every tool dispatch via `arguments['conversation_id']` |
| 5 | `core/services/td_handlers_agents.py` | 964-966 | universal_agent handler promotes `payload['conversation_id']` into `context['conversation_id']` |
| 6 | `core/services/td_handlers_agents.py` | 1007 | `execute_agent_task.apply_async(args=[agent_name, task_text, context], queue='long_running')` |
| 7 | `core/tasks_agents.py` | 1880 | `AgentExecution.objects.create(..., conversation_id=context.get('conversation_id') or None)` |
| 8 | `core/tasks_agents.py` | 99-176 | `fire_agent_followup_subscriptions` matches `sub.conversation_id == execution.conversation_id` and broadcasts to `pa_conversation_<X>` |

**Session 1175 "divergence" between `pa-639751…` and `pa-58c916…` was the wrapper test-harness pinning being stale across two separate requests**, not within one turn. The cross-conversation guard at `td_handlers_agents.py:4544` correctly rejected — that's the design.

**Action:** mark Session 1175 open follow-up #1 as closed. Optional next-time note: log when a wrapper pins a conversation_id so stale pins are obvious — that's a test harness improvement, not core product logic.

## PR #2345 — what's in it

| Path | Change |
|---|---|
| `core/tasks_agents.py` | New helper `create_implicit_followup_subscription` (fail-open per Session 1172 lessons, single-line warning with `execution_id` + `conversation_id` on exception). Called from `_impl_execute_agent_task` right after `AgentExecution.create` with conv_id stamped. |
| `core/services/tool_dispatcher.py` | `auto_followup` added to `_CONTEXT_PROMOTE_KEYS` (per-call opt-out reaches task body via `_handle_agent_tool`). |
| `core/services/td_handlers_agents.py` | Explicit `auto_followup` promotion in `universal_agent_tool` handler (which doesn't share `_CONTEXT_PROMOTE_KEYS`). False is meaningful, so test for membership not truthiness. |
| `core/services/pa_tool_schemas.py` | `auto_followup` (bool, default true) added to `run_agent` schema with description explaining test-harness opt-out semantics. |
| `core/tests/test_auto_followup_subscription.py` | 6 tests pinning the four invariants + both ordering races. |
| `docs/handoffs/SESSION_1175_AGENT_FOLLOWUP_DEMO.md` | Phase 2 demo section appended. |

## Ratified design card (Rigby sign-off Session 1178)

Conversation `pa-9b82bcc72e1945ce`. Three exchanges:

| D | Decision | Choice | Rigby caveat |
|---|---|---|---|
| D1 | Replace vs augment vs coexist with explicit `schedule_followup` | **Augment** | Explicit tool stays useful for tests + custom TTL |
| D2 | Default `after_seconds` for auto-sub | **30s** | — |
| D3 | Scope | **PA-only** via `conversation_id IS NOT NULL` (PR-1 invariant) | — |
| D4 | Opt-out mechanism | **Per-call** only (`auto_followup: false`) | No global/per-agent config in v1 |
| D5 | Multi-agent dispatch | **One banner per agent** | Rollup deferred (open follow-up #4) |
| D6 | Where the implicit sub is created | **At `execute_agent_task` entry** | Required dedupe; resolved via existing `unique_together` |

## Behavioral invariants (now true post-merge)

1. **Every PA-originated agent dispatch with `conversation_id` stamped auto-creates an armed subscription** unless `context['auto_followup'] is False`.
2. **At most one subscription per `(execution, conversation_id)` pair** — DB-level via `unique_together = [('execution', 'conversation_id')]` on `AgentFollowupSubscription` (unchanged since Session 1174 PR-2a).
3. **60s default TTL on the implicit auto-sub** (`AgentFollowupSubscription.DEFAULT_TTL_SECONDS`, model constant); **explicit `schedule_followup` can override up to 600s** (`MAX_TTL_SECONDS`, same model class). Bumped from 30s in PR #2347 after live verify caught a 2-second race against typical ResearchAgent runtime.
4. **Auto-sub creation never blocks dispatch** — fail-open warning includes `execution=` and `conv=` for correlation, then continues. **Incident grep:** `grep '\[auto_followup\] fail-open' .logs/celery*.log` surfaces all fail-open events with execution_id and conv_id; absence of this string means the helper path is healthy.
5. **Explicit `schedule_followup` racing the implicit auto-sub never produces a duplicate row** — `get_or_create` returns the existing row unchanged; whoever lands first keeps their TTL.
6. **All Phase 1 invariants are preserved** — atomic armed → fired transition, scope-rules NULL-conv gate, banner-fire-then-bubble-persist order, ChatConversation row metadata shape.

## Rollback levers

| Lever | When | How |
|---|---|---|
| **Per-callsite disable** | Auto-wake misbehaves on prod but explicit tool still works | Comment out the single line `create_implicit_followup_subscription(execution_record, context)` in `core/tasks_agents.py` (~L1898). Store-time gates (PR-1 + PR-2a) remain. |
| **Global revert** | The whole PR proves problematic | `git revert <merge-sha-for-#2345>`. Phase 1 c2 (explicit `schedule_followup`) continues to work unchanged. |
| **Per-execution opt-out** | A specific agent class needs auto-wake suppressed | Pass `auto_followup: false` in the `run_agent` payload (already supported). Phase 3 could promote this to a per-agent config table. |
| **Worker disable** | Auto-wake is creating noise and Chris just wants a quiet evening | Set a quick feature-flag check at the helper's top. (Not done in this PR; the simplest disable is the per-callsite comment-out above.) |

## 24h watch checklist (post-merge to main)

```bash
# (1) Auto-sub creation rate
# Expect: count rises after merge; fired/total ratio stays high.
USE_PGBOUNCER=1 .venv/bin/python manage.py shell --command "
from core.models_unified_system import AgentFollowupSubscription
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=24)
subs = AgentFollowupSubscription.objects.filter(created_at__gte=since)
print(f'last 24h subscriptions: {subs.count()}')
print(f'  states: armed={subs.filter(state=\"armed\").count()} '
      f'fired={subs.filter(state=\"fired\").count()} '
      f'expired={subs.filter(state=\"expired\").count()}')"

# (2) Spot-check log grep for [auto_followup] events.
# Expect: ~1 'created' line per PA-originated agent dispatch + 0 'fail-open' lines.
grep '\[auto_followup\]' .logs/celery.log 2>/dev/null | tail -20

# (3) Per-dispatch invariant — every PA dispatch should have a matching sub row.
# Expect: ratio ≈ 1.0 for executions in the last hour.
USE_PGBOUNCER=1 .venv/bin/python manage.py shell --command "
from core.models_unified_system import AgentExecution, AgentFollowupSubscription
from datetime import timedelta
from django.utils import timezone
since = timezone.now() - timedelta(hours=1)
pa_exec = AgentExecution.objects.filter(created_at__gte=since).exclude(conversation_id__isnull=True)
matched = pa_exec.filter(followup_subscriptions__isnull=False).distinct().count()
total = pa_exec.count()
ratio = matched/total if total else 0
print(f'PA-dispatched last 1h: {total}, with auto-sub: {matched} ({ratio:.0%})')"

# (4) Banner WS event reach (Phase 1 invariant — unchanged).
grep -c 'agent.completed' .logs/daphne.log 2>/dev/null || echo '0 (or check log path)'
```

## Post-merge live verify (one-shot)

After merge:

```bash
# 1. Restart workers so the new code is in sys.modules (per
#    feedback_celery_pid_cache_blocks_restart + feedback_new_shared_task_needs_worker_restart memories).
pkill -9 -f celery; rm -f .celery*.pid; make celery

# 2. Dispatch a quick agent via Rigby WITHOUT calling schedule_followup.
tools/pa_local.sh "Run ResearchAgent on this task: summarize one sentence about Phase 2 auto-wake. Do not call schedule_followup."

# 3. Watch the browser at http://localhost:8000/ on the pinned conversation.
#    Expect: ~5-30s after the dispatch, AgentCompletionBanner flashes + Rigby
#    bubble appears in chat. No explicit schedule_followup tool run in the
#    verbose ticker (that's the point).

# 4. Check the auto-sub row was created.
USE_PGBOUNCER=1 .venv/bin/python manage.py shell --command "
from core.models_unified_system import AgentFollowupSubscription
s = AgentFollowupSubscription.objects.order_by('-created_at').first()
print(f'{s.id} state={s.state} created={s.created_at} expires={s.expires_at}')
print(f'  delta(s) = {(s.expires_at - s.created_at).total_seconds():.0f}')
# Expect: state='fired' (or 'armed' if you're fast), delta ≈ 30."

# 5. Verify opt-out: same dispatch with auto_followup=false in run_agent args.
#    Expect: no banner, no Rigby bubble, no new subscription row for that execution.
```

## Carry-forward — open follow-ups for Phase 3+

| # | Item | Lean / status |
|---|---|---|
| 1 | `auto_followup_skipped` traceability — stamp on `AgentExecution.output_data` when opt-out path is taken | Pulled from PR #2345 to keep scope narrow. Easy 1-file PR; Rigby's optional Session 1178 suggestion. |
| 2 | Per-agent auto-wake config (e.g. "always skip auto-wake for X") | Phase 3 — needs a small config table or annotation on `AGENT_MAP`. |
| 3 | Global user-level kill switch | Phase 3 — needs an `AssistantProfile` field. |
| 4 | Multi-agent dispatch fan-out rollup ("tell me when all 3 finish") | Phase 2 open follow-up #4 — needs new tool variant + subscription rollup helper. |
| 5 | EditorAgent observability dashboard (C3 from Session 1177) | Session 1177's deferred item; builds on PR #2343's `content_provenance`. |
| 6 | Session 1175 Pass B matrix cells 3-8 (revoke / refresh-mid-run / second-tab / media-artifact) | Deliverable `61247479` has scaffold ready; Phase 1 stress-test coverage. |

## Session-structure notes worth carrying

1. **Recon-before-design pays off in token budget.** Spending ~15min walking the conv-ID code path before pitching Phase 2 decisions let me bring **findings** to Rigby's design card, not just questions. The result: full ratification in 2 exchanges instead of 5-6 (which would have been the recon-cost-amortized version).
2. **`feedback_corpus_walks_surface_mechanism_drift` memory generalizes to plumbing recon.** Same instinct — walk the code, surface what's actually there, present findings honestly. "Not a real bug; close #1" was the right call after the code walk, not the speculative "could be a bug" framing the open-follow-up text suggested.
3. **PgBouncer down meant `manage.py test` failed at DB-connect on :5433.** Workaround was `USE_PGBOUNCER=0 .venv/bin/python manage.py test ... --noinput`, which routes through `:5432` directly. Worth adding to the troubleshooting runbook if tests keep getting hit by PgBouncer-down conditions.
4. **Decision-card-with-leans + "agree all" worked again.** Two rounds (initial card + dedupe sub-card); Rigby disagreed on zero items. Pattern continues to scale.

## Conversations

`pa-9b82bcc72e1945ce` still healthy at close — used for kickoff, conv-ID recon report, Phase 2 D-card, dedupe confirmation, and PR review request. Session 1179 should reuse it unless Rigby flags otherwise.

## Memory updates (recommended for next session)

None new. The session reinforced these existing memory entries — no edits needed:

- `feedback_corpus_walks_surface_mechanism_drift.md` (used for conv-ID recon framing)
- `feedback_triage_decision_card_pattern.md` (used twice; pattern continues to work)
- `feedback_rigby_collaboration.md` (read Rigby's full responses before building — done explicitly here)
- `feedback_new_shared_task_needs_worker_restart.md` (auto-wake invokes a new module-level helper from the task body; will require restart post-merge)
- `feedback_celery_pid_cache_blocks_restart.md` (companion to above)
- `feedback_pgbouncer_startup_params.md` (PgBouncer:5433 down today; tests routed via :5432)
- `feedback_handoff_operational_sections.md` (this handoff follows the invariants + rollback levers + 24h watch checklist pattern)
