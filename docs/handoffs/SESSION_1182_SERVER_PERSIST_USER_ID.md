# Session 1182 — Server-side persist user attribution fix (24h-watch finding)

**Status:** Closed. 1 fix PR shipped. Pass B still closed. New "Known issues" entry: pre-existing platform-wide CI guardrail conflict (not blocking, deferred to Session 1183).
**Date:** 2026-06-20
**Pinned conversation:** `pa-8f8ef45338ce4a24` (created at session open after `pa-a5fecc400c0f4152` hit health 55/100; carry-forward summary covered the Session 1180+1181 24h watch context).
**Driving question:** "Run the 24h watch from Session 1181's close. Confirm Pass B is holding. Pick green-field work if everything is clean."
**Prior session handoffs:**
- [SESSION_1181_PHASE3_BANNER_QUEUE_AND_ARTIFACTS.md](./SESSION_1181_PHASE3_BANNER_QUEUE_AND_ARTIFACTS.md) — Phase 3 queue drained, Pass B fully closed
- [SESSION_1180_PASS_B_EXECUTION.md](./SESSION_1180_PASS_B_EXECUTION.md) — Pass B execution + 3 structural fixes

## TL;DR

24h watch caught a real regression: PR #2352's server-side completion-row persistence was silently failing for PA-originated ImageAgent dispatches with `IntegrityError: null user_id`. Consumer-side safety net caught it (no UX impact), but the architectural intent of PR #2352 ("decouple completion persistence from WS consumer") was half-broken. Fixed in **PR #2357** with a tight 3-part patch + 4 new tests, merged as squash commit `51fdfe55`.

| PR | SHA | Theme | What it fixes |
|---|---|---|---|
| **#2357** | `51fdfe55` | `fix(session-1182-server-persist)` — resolve user attribution in fire helper + tighten `create_completion_row` contract | Server-side persist now fail-closed when ownership can't be resolved (was silent IntegrityError); typed `AnonymousCompletionRowError` raised early instead of degraded-to-None fallback. |

Backend-only. No migration. No frontend touch. Single-revert safe.

## The watch finding

### What the spot-check showed

The Session 1181 close handoff specified three 24h watch checks:
- (a) `[auto_followup]` log tail — `created` lines fire, `fail-open` absent
- (b) Stale armed-subs with NULL expires_at older than 6h — expect 0 or <10
- (c) `chat_conversations.metadata.artifact_pointers` non-empty for recent ImageAgent/EditorAgent completions (PR #2354 verification)

Results:
- **(a)** — Mixed. `[auto_followup] created` present (execution `0f7d4c85`), BUT one `fail-open` line surfaced from a DIFFERENT site: `[fire_agent_followup_subscriptions] server-side persist fail-open: execution=0f7d4c85 conv=pa-a5fecc400c0f4152 (IntegrityError: null value in column "user_id" of relation "chat_conversations")`
- **(b)** — Clean. **0 stale armed-subs**. State breakdown: 23 fired / 2 expired / 1 armed. Lifecycle-bound expiry semantic from Session 1180 PR #2350 is holding.
- **(c)** — Clean. **7/7 recent ImageAgent rows** in last 24h have `artifact_pointers` populated (5 with `media_ids`, 2 with `{}` — empty when no media generated; extractor still firing). PR #2354 verified live.

### What the regression actually was

PR #2352's `fire_agent_followup_subscriptions` server-side persist call:

```py
# core/tasks_agents.py:342 (pre-fix)
create_completion_row(
    user=getattr(execution_record, 'user', None),
    ...
)
```

For PA-originated ImageAgent dispatches via `process_pa_chat_task → run_agent → execute_agent_task`, `execution_record.user` was **None**. The downstream call to `ChatConversation.objects.create(user=None)` then hit the NOT NULL constraint on `chat_conversations.user_id` → IntegrityError → fail-open path swallowed it.

Compounding bug in `core/consumers_pa_conversation.py:create_completion_row`:

```py
# Before (footgun)
user=user if (user and getattr(user, 'is_authenticated', False)) else None,
```

The defensive `else None` made the contract violation silent. Since `user_id` is NOT NULL at the DB level, there was no legal path where `user=None` could succeed. The fallback only converted a programmer-contract violation into a runtime IntegrityError further downstream — harder to debug, looked like infra/data issue.

### Why UX wasn't broken

The consumer-side write path (PR #2352's idempotent safety net) ran successfully because `PAConversationConsumer.agent_completed` calls `create_completion_row(user=self.scope['user'], ...)` and `self.scope['user']` was a real authenticated user. Verified directly via DB: `chat_conversations` row 661 exists for execution `0f7d4c85` with `user_id=e0c9d44b...` populated.

But the **architectural intent** of PR #2352 ("decouple completion persistence from WS consumer") was inert — if both sides ever fail, refresh-mid-run regresses to the Cell 4 failure mode (no bubble, no banner, no history).

## The fix (PR #2357)

### Patch shape (ratified with Rigby pre-merge — Option 1)

**1. `core/tasks_agents.py` — new `_resolve_completion_user` helper:**

```py
def _resolve_completion_user(execution_record, conversation_id):
    user = getattr(execution_record, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        return user
    try:
        from core.models.conversations.models import ChatConversation
        owner_id = (
            ChatConversation.objects
            .filter(conversation_id=conversation_id)
            .exclude(user__isnull=True)
            .order_by('-created_at', '-id')          # total ordering on ties
            .values_list('user_id', flat=True)       # unambiguous
            .first()
        )
        if owner_id is None:
            return None
        from django.contrib.auth import get_user_model
        return get_user_model().objects.filter(pk=owner_id).first()
    except Exception as e:
        logger.warning('[_resolve_completion_user] lookup failed ...')
        return None
```

Resolution order: `execution.user` (fast path) → ChatConversation owner lookup (deterministic) → `None` (fail-closed).

**2. `fire_agent_followup_subscriptions` — distinct log key:**

```py
resolved_user = _resolve_completion_user(execution_record, conv_id)
if resolved_user is None:
    logger.warning(
        '[fire_agent_followup_subscriptions] persist_skipped_missing_user: '
        'execution=%s conv=%s — broadcasting only, consumer-side will persist if connected',
        execution_record.id, conv_id,
    )
else:
    try:
        # ... compose body + create_completion_row(user=resolved_user, ...)
    except Exception as persist_exc:
        logger.warning('[fire_agent_followup_subscriptions] server-side persist fail-open: ...')
# Broadcast (unchanged) regardless of persist outcome
```

The distinct log key `persist_skipped_missing_user` separates "we couldn't attribute, skipped persist intentionally" from `fail-open` ("we tried to persist and hit an exception but continued"). Better observability for the watch loop.

**3. `core/consumers_pa_conversation.py` — typed contract enforcement:**

```py
class AnonymousCompletionRowError(ValueError):
    """Raised when create_completion_row is called without an authenticated user."""

def create_completion_row(*, user, ...):
    if not user or not getattr(user, 'is_authenticated', False):
        raise AnonymousCompletionRowError(
            f'create_completion_row requires an authenticated user '
            f'(conversation_id={conversation_id}, execution_id={execution_id})'
        )
    ...
    return ChatConversation.objects.create(
        user=user,                                # was: user=user if (...) else None
        ...
    )
```

Failures become loud + local instead of downstream IntegrityError.

### Query volume

`fire_agent_followup_subscriptions` is called **once per terminal AgentExecution save** (5 fire sites in tasks_agents.py docstring). `_resolve_completion_user` is called **once per fire helper invocation**, never per-sub. The conv-owner fallback adds at most **2 queries** to the fire path (owner_id lookup + User row fetch) — and only when execution.user is missing.

### What this does NOT change

- `AgentFollowupSubscription` schema (no FK to user added; conversation-owner lookup is cheap enough — flagged as Phase 4 if/when needed).
- Consumer-side persist path (already passed `self.scope['user']` correctly).
- Behavioral invariants from Session 1180 #1-6 still hold.
- No migration, no schema change, no settings change.

## Tests

- **`test_unauthenticated_user_raises_typed_error`** (was `_resolved_to_none`) — the old test was scaffolding around the bug; its docstring explicitly flagged the schema drift. Updated to assert the new typed-error contract.
- **`test_none_user_raises_typed_error`** — explicit None case.
- **`ResolveCompletionUserTests`** — 4 tests:
  - `test_returns_execution_user_when_authenticated` (fast path)
  - `test_falls_back_to_conversation_owner_when_execution_user_missing` (the Session 1182 repro)
  - `test_returns_none_when_no_attribution_available` (no fast path + no conversation = fail-closed)
  - `test_picks_latest_owner_when_multiple_rows_exist` (deterministic ordering across distinct users)
- **`CompletionRowIdempotencyTests`** (Session 1180 P1) still green — no regression on the idempotency contract.

All 18 tests pass via `USE_PGBOUNCER=0 .venv/bin/python manage.py test core.tests.test_agent_completed_persistence --keepdb --noinput`.

PgBouncer note: the test runner can't go through PgBouncer because port 5433 doesn't have a `postgres` admin DB configured for test-DB creation. `USE_PGBOUNCER=0` routes the test runner to native postgres on 5432. Same workaround for the `_resolve_completion_user` tests via `manage.py shell`.

## Behavioral invariants (Session 1180 #1-6)

All six still hold post-PR-#2357. Specifically:
- **#6** ("fire helper fail-open both directions") — preserved on the `persist_skipped_missing_user` path. Broadcast still fires, the row just doesn't persist server-side, and the consumer-side safety net still writes if connected.
- **Failure-mode guarantee (new):** Server-side persistence is fail-closed when ownership can't be resolved; WS consumer still persists for live sockets. The "no consumer + missing attribution" case is explicitly logged and skipped.

## Rollback

Single-revert safe. No migration, no schema change. `git revert 51fdfe55` would restore pre-PR behavior; the consumer-side safety net was carrying the path already, so revert wouldn't break user-visible UX either.

## Known issues / follow-ups

### Pre-existing CI guardrail conflict (NOT caused by this PR)

`Repo Guardrails` check has been failing on `main` for at least 3 PRs (#2354, #2355, #2356 — all Session 1181 PRs merged through it). Root cause per `context-kit verify --json`:

```
CONFLICT — Celery beat schedule ownership
Docs/env claim exclusive ownership in [20+ files including
core/celery.py, core/management/commands/add_critical_celery_tasks.py,
core/services/celery_health.py, ...]
```

Not blocking — PRs merge with `--admin` bypass. But it makes the watch loop noisier and obscures real CI regressions. Triage cleanly in Session 1183:

- Option A: Update the canonical doc claim to reflect actual multi-file ownership (the schedule is genuinely split across migrations + setup commands + runtime services).
- Option B: Fix the guardrail's expectation that beat schedule ownership is single-file (it isn't, by design).
- Option C: Accept the bypass indefinitely and document the rationale.

Suggested first move: 10-minute triage at the top of Session 1183 to pick the lane.

### Phase 4: FK on `AgentFollowupSubscription`

Rigby's pre-merge review surfaced this as a "later if needed" improvement. Adding a `user FK` to `AgentFollowupSubscription` would:
- Remove the 2-query conv-owner fallback in `_resolve_completion_user`
- Enable analytics on subscriptions by user
- Enforce ownership immutability even if conversations get weird

Not load-bearing on anything today. Pick up if/when the conv-owner fallback shows up as a hotspot, or if user-keyed subscription analytics become a need.

## Conversations

- Opened on `pa-a5fecc400c0f4152` (carried over from Session 1180+1181 close).
- Rotated mid-session: `pa-a5fecc400c0f4152` hit health 55/100 (`suggest_fresh`) → created `pa-8f8ef45338ce4a24` ("Session 1182 — Post-PR2350-2355 24h Watch + Next Work") with tight carry-forward summary. `tools/pa_local.sh` updated to point at the new conversation.

## Evidence references

- Server-side persist fail-open line: `celery-long-running.log` line 2499 (execution `0f7d4c85`).
- chat_conversations row 661 (consumer-side fallback proof): user_id `e0c9d44b...`, metadata.agent_name `ImageAgent`, metadata.execution_id `0f7d4c85`.
- 24h watch state breakdown: `core_agentfollowupsubscription` — 23 fired / 2 expired / 1 armed; 0 stale.

## 24h watch checklist for Session 1183

Spot-check post-Session-1182:
- Tail `celery-long-running.log | grep persist_skipped_missing_user` — should appear rarely (only for genuinely-orphan conversations). If it's frequent, the conv-owner fallback isn't holding for some real path.
- Tail `celery-long-running.log | grep '\[fire_agent_followup_subscriptions\] server-side persist fail-open'` — should be **zero** for the IntegrityError-on-user_id signature.
- Continue the Session 1181 invariants: `[auto_followup] created` lines fire; armed-subs with NULL expires_at older than 6h stay at 0; `artifact_pointers` populated for recent ImageAgent/EditorAgent.
