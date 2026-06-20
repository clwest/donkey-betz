# Session 1171 — ML Queue Flood + Auth Middleware Triage

**Date:** 2026-06-20
**Workspace:** `Session 1171 — ML Queue Flood + Auth Middleware Triage` (id `f5c6c04a-d9c9-4ddc-a72b-21afa9232e6b`)
**PR:** [#2328](https://github.com/clwest/donkey-betz-platform/pull/2328)

## TL;DR

Rigby flagged the local `ml` Celery queue at 533 messages, projected ~40h drain. Investigation found the backlog accumulated since 2026-06-14, drained at ~2 per 4min, and triggered live: during debugging, daphne started returning 401 "Invalid authentication token" for every API call because Postgres hit `too many clients already` and the auth middleware silently swallowed the OperationalError — a real bug that masked the connection-exhaustion symptom.

Four tickets, four deliverables:
1. **Containment** — purged 533-msg backlog via `redis-cli -n 2 DEL ml` after JSONL backup.
2. **Root cause** — old beat process (PID 9418, ran 06-14 → 06-19) firing `*/15` with no TTL on messages.
3. **Guardrail** — `@singleton_task` + fail-open depth-gate on `backfill_spider_embeddings` + restore `expire_seconds=900` on PeriodicTask row.
4. **Auth middleware** — distinguish 401 "no such token" from 503 "auth backend unreachable" by raising a typed exception instead of swallowing all errors.

## Behavioral invariants (post-merge)

- `backfill_spider_embeddings` cannot run twice concurrently (singleton lock, TTL 600s).
- `backfill_spider_embeddings` no-ops when the `ml` queue exceeds 50 messages (fail-open on Redis errors).
- PeriodicTask row id=43 (`backfill-spider-embeddings`) now has `expire_seconds=900`. Row remains `enabled=False`.
- `validate_token` raises `TokenValidationInfrastructureError` on any non-`DoesNotExist` exception.
- Strict-auth callsite returns **503 `auth_backend_unavailable`** when the auth backend is unreachable; **401** only for actually invalid/missing tokens.
- Optional-auth callsite continues to fail-open (anon-equivalent) even on backend errors.

## Rollback levers

| Change | Disable / revert |
|---|---|
| Singleton lock on `backfill_spider_embeddings` | Revert PR — single-file Python change. |
| Depth-gate threshold (currently 50) | Change `BACKFILL_SPIDER_EMBEDDINGS_DEPTH_GATE` constant in `core/tasks.py:1208`. |
| `expire_seconds=900` on PeriodicTask | Reverse migration: `python manage.py migrate core 0355_session_1169_celerytaskevent_agent_name` (sets back to NULL). |
| Auth 503 escalation | Revert PR — single-file change to `core/auth_middleware.py`. |
| PeriodicTask id=43 re-enabled accidentally | `UPDATE django_celery_beat_periodictask SET enabled=false WHERE id=43;` |

## Worker restart caveat

The new `backfill_spider_embeddings` body activates only after the `long_running` worker restarts. Per Session 1162 gotcha — helper modules a task body imports get cached in `sys.modules` after first call. Until then:
- PeriodicTask remains disabled → no fires.
- Migration's `expire_seconds=900` is DB-side, already active.
- If the row is re-enabled before a worker restart, the OLD task body (no guard) will run.

Sequence Chris approved: merge → row stays disabled → next natural worker restart picks up new code → optionally re-enable row.

## 24h watch checklist

```bash
# 1) Confirm queue stays empty (or near-empty) post-merge
redis-cli -n 2 LLEN ml                    # expect: 0–5

# 2) Watch for depth-gate trips (would indicate something refilling queue)
grep "depth-gate tripped" server.log celery*.log | tail -10
grep "depth-gate check skipped" server.log celery*.log | tail -10

# 3) Watch for singleton lock collisions (would indicate misconfiguration)
PGPASSWORD=secure_password psql -h 127.0.0.1 -U unified_user -d unified_donkey_betz -c "
SELECT task_id, started_at, status, error_message
FROM core_celerytaskevent
WHERE task_name = 'core.tasks.backfill_spider_embeddings'
  AND started_at > now() - interval '24 hours'
ORDER BY started_at DESC LIMIT 20;
"

# 4) Watch for auth 503 appearances (real PG outage signal)
grep "auth_backend_unavailable\|Auth backend unreachable" server.log | tail -10

# 5) Confirm PeriodicTask row stays disabled
PGPASSWORD=secure_password psql -h 127.0.0.1 -U unified_user -d unified_donkey_betz -c "
SELECT name, enabled, expire_seconds, total_run_count, last_run_at
FROM django_celery_beat_periodictask
WHERE name='backfill-spider-embeddings';
"
```

## Forensic artifacts

| Path | Contents |
|---|---|
| `logs/session_1171/ml_queue_pre_purge_20260620_102127.jsonl` | All 533 queue messages, JSON-per-line, captured before purge. |

Distribution of pre-purge messages:
- 530× `core.tasks.backfill_spider_embeddings` (kwargs={'batch_size': 500} → beat-origin, not warmup or PA-trigger)
- 3× `core.tasks.generate_document_embeddings` (retries from Document post_save signal, unrelated)
- 451 messages from `gen9418@Chriss-MacBook-Pro.local` — a dead beat process that ran 06-14 13:41 → 06-19 14:20
- Zero new `backfill_spider_embeddings` enqueues since 2026-06-19 22:45 (sent_at evidence)

## Tickets + Rigby deliverables

| Ticket | Initiative ID | Status | Rigby deliverable |
|---|---|---|---|
| 1171-1 Containment | `7b91199f-38f0-4e9f-a97d-3a8369d9692c` | COMPLETED | `0621b962-794d-43bd-8345-fd1db2c70384` |
| 1171-2 Root Cause | `8990c79d-2371-4b2a-be25-6d75b72baad8` | COMPLETED | `f3363854-08c7-46a7-8d5f-cf1b4da1b0ec` |
| 1171-3 Guardrail | `94dbf24b-694a-4d1c-8d4d-79daa6908783` | COMPLETED | `d0ac95a7-46ba-43e4-9568-140256cc0636` |
| 1171-4 Auth Middleware | `1e39ca31-0a0d-4419-88d9-54e86b9bd23a` | COMPLETED | `fd6cf08e-bf61-4179-b236-bb14a497335d` |

## Out of scope / queued for follow-on

- Rollout of `@singleton_task` + depth-gate to other ml-bound tasks (`backfill_memory_embeddings`, `backfill_conversation_embeddings`, `generate_document_embeddings`) — per primitives + opt-in apply list Phase 1 pattern.
- WebSocketAuthenticationMiddleware audit — same swallow-everything pattern may exist there.
- Bumping Postgres `max_connections` (currently 100) or pooling reform — would have prevented the underlying connection exhaustion that triggered the auth-middleware bug discovery.
- Re-enable of PeriodicTask id=43 — explicit human decision, not a code change.
- Generate_document_embeddings retry chain trace (3 messages caught in the purge with `parent_id=c3136622-...`) — unrelated to the backfill flood; worth investigating if it recurs.

## Memory rules referenced this session

- `feedback_rigby_comms.md` — all decisions routed through Rigby.
- `feedback_pa_chat_local_override.md` + `feedback_pa_local_verify_ownership.md` — pa_chat.py needed `PA_API_URL=http://localhost:8000` + chris's token.
- `feedback_primitives_plus_optin_applylist_phase1.md` — applied Session 1165's `@singleton_task` to ONE callsite, deferred rollout.
- `feedback_new_shared_task_needs_worker_restart.md` — explained why we didn't restart workers mid-session.
- `feedback_handoff_operational_sections.md` — invariants + rollback levers + 24h watch checklist structure.
