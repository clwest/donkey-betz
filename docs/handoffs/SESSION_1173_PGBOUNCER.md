# Session 1173 — PgBouncer in front of Postgres (local dev)

**Date:** 2026-06-20
**Workspace:** `Session 1173 — PgBouncer in front of Postgres (local dev)` (`951f1be0-a692-4864-958c-d9ffc593983d`)
**PR:** TBD on commit
**Phase 1 (max_connections bump)** done in-session, no PR — config-only change.

## TL;DR

Chris hit `503 auth_backend_unavailable` storms while loading the dashboard. PR #2328 (Session 1171 #4) was correctly surfacing the underlying cause — PG hitting `max_connections=100` during dashboard-mount bursts of ~30 simultaneous API calls. Combined with `CONN_MAX_AGE=60` holding daphne connections plus steady-state celery (~32 conns), bursts peaked over 100.

**Phase 1 (in-session, no PR):** bumped PG `max_connections` 100 → 300. Immediate relief.

**Phase 2 (this PR):** PgBouncer (Homebrew) on `:5433` in front of PG `:5432`, transaction pool, default_pool_size=25. Django routes through PgBouncer when `USE_PGBOUNCER=1` is set. PG now sees a stable small number of server conns regardless of app-side burst size.

**Verified:** 10-parallel-curl dashboard-mount simulation produces a peak of **5 PG server connections** (down from previously >100).

## Behavioral invariants (post-merge)

- With `USE_PGBOUNCER=1` in `.env`:
  - Django's default DB alias connects to `127.0.0.1:5433` (PgBouncer).
  - `CONN_MAX_AGE=0` and `DISABLE_SERVER_SIDE_CURSORS=True` on the default alias.
  - A second alias `migrations` connects directly to `127.0.0.1:5432` (PG) with `CONN_MAX_AGE=60` for session-state-dependent operations.
- Without `USE_PGBOUNCER`: existing behavior preserved (port 5432, CONN_MAX_AGE=60).
- PgBouncer uses `transaction` pool mode with `default_pool_size=25, reserve_pool_size=5, max_client_conn=500`.
- PG's `search_path`, `statement_timeout`, and `idle_in_transaction_session_timeout` are now set by PgBouncer's `connect_query` instead of Django's psycopg2 `options` startup parameter (PgBouncer rejects startup params under transaction pool).
- The Session 1166 per-process `application_name` tagging **degrades** under transaction pooling — only the first checkin's name persists per server connection. Mitigation deferred to Phase 3.
- Migrations and any code that relies on session state must use `manage.py migrate --database=migrations` or set the router/explicit DB alias.

## Setup steps (for any dev pulling this branch)

```bash
# 1. Install pgbouncer
brew install pgbouncer

# 2. Write the project config (see /opt/homebrew/etc/pgbouncer.ini in this PR's
#    handoff for the full content). Key points:
#    - listen_port=5433
#    - pool_mode=transaction
#    - connect_query='SET search_path TO studio,public,dbao,shared; SET statement_timeout TO 60000; SET idle_in_transaction_session_timeout TO 60000'
#    - ignore_startup_parameters=options,application_name
#    - default_pool_size=25, reserve_pool_size=5, max_client_conn=500

# 3. Start pgbouncer
brew services start pgbouncer

# 4. Verify
psql -h 127.0.0.1 -p 5433 -U unified_user pgbouncer -c "SHOW POOLS"

# 5. Enable in your local .env
echo "USE_PGBOUNCER=1" >> .env

# 6. Restart django + celery
make stop celery-stop
make start celery
```

Rollback per environment: comment out `USE_PGBOUNCER` in `.env` and restart. Django reverts to direct-to-PG behavior. PgBouncer can keep running idle without affecting Django.

## Architecture

```
                Browser (~30 parallel API calls on dashboard mount)
                    │
                    ▼
                Daphne (:8000)   ─── client conn ──▶ │
                                                     │
                Celery worker (pa, default,           │  PgBouncer (:5433)
                  long_running, broadcast)            │  transaction pool
                                  │ client conns ──▶ │  default_pool_size=25
                                                     │
                                                     ├── server conn pool ──▶ PG (:5432)
                                                     │                         max_connections=300
                                                     │                         (still capped, but PgBouncer
                                                     │                          keeps server-side small)
                                                     │
                Migrations / maintenance ─ direct ───┴───────────────────────▶ PG (:5432)
                  (alias `migrations`)
                  CONN_MAX_AGE=60, server cursors OK
```

## Rollback levers

| Change | Disable / revert |
|---|---|
| Django routes through PgBouncer | Remove or comment `USE_PGBOUNCER=1` in `.env`; restart daphne + celery. Reverts to existing 5432 behavior. |
| PgBouncer entirely | `brew services stop pgbouncer`. Combined with the `USE_PGBOUNCER` revert above, full rollback in 2 steps. |
| PG `max_connections=300` | Edit `/opt/homebrew/var/postgresql@15/postgresql.conf`, set back to 100; `brew services restart postgresql@15`. Backup at `postgresql.conf.bak-20260620_120512`. |
| Pool sizing tweaks | Edit `/opt/homebrew/etc/pgbouncer.ini`, `brew services restart pgbouncer`. |
| Migration alias collision | Migrations are explicit via `--database=migrations` for now. If a future router routes by default, add `DATABASE_ROUTERS` flag to disable PgBouncer routing per-model. |

## 24h watch checklist

```bash
# 1. PgBouncer pool saturation — sv_used == default_pool_size means
#    you're queuing waiters, consider bumping default_pool_size
psql -h 127.0.0.1 -p 5433 -U unified_user pgbouncer -c "SHOW POOLS"

# 2. PG server-side conn count — should stay well under 300 (target ~30-50)
PGPASSWORD=secure_password psql -h 127.0.0.1 -U unified_user -d postgres -c \
  "SELECT application_name, count(*) FROM pg_stat_activity WHERE datname='unified_donkey_betz' GROUP BY application_name ORDER BY count DESC;"

# 3. Any rejected client conns?
psql -h 127.0.0.1 -p 5433 -U unified_user pgbouncer -c "SHOW STATS"
# Look at total_xact_count growing steadily; total_wait_time should be near zero.

# 4. Django connection errors after restart?
grep -E "(too many clients|InterfaceError|OperationalError)" server.log celery*.log | tail -20

# 5. Auth backend unreachable (the 503 from PR #2328) — should be silent now
grep "auth_backend_unavailable" server.log | tail -5
```

## Trade-offs accepted

- **Per-process application_name attribution (Session 1166) DEGRADES** under transaction pool. Multiple celery workers + daphne share the same `unified_user` PgBouncer pool. PG's `pg_stat_activity.application_name` now reflects whichever process's connection first established each pool slot, not the actual current user. Worth a Phase 3 fix if attribution becomes critical.
- **`.iterator()` no longer uses server-side cursors.** Memory pressure on very large querysets may increase slightly. Audit candidate: spider data backfills, embedding regeneration. No known callsite >10K rows in a single iter; flagged for monitoring.
- **Migrations require explicit `--database=migrations`.** Standard Django pattern; documented in CLAUDE.md (TODO follow-on).
- **PgBouncer adds a new process to manage.** Mitigated by Homebrew services integration; `brew services list` shows status, restart is one command.

## Memory rules saved (Session 1173)

- `feedback_pgbouncer_startup_params.md` — PgBouncer transaction-mode rejects Django's `options` startup parameter. Move search_path + timeouts to `connect_query` on the database entry; add `ignore_startup_parameters` for any Django passes anyway.
- `feedback_pgbouncer_application_name_attribution.md` — per-process `application_name` (Session 1166) breaks under transaction pool. Don't rely on `pg_stat_activity.application_name` for attribution when PgBouncer is in front.

## Tickets

| Ticket | Initiative ID | Status |
|---|---|---|
| 1173-1 Install + base config | `b14eb6c8-1879-4958-84ec-ac79b870bd08` | COMPLETED |
| 1173-2 Django wiring | `2737e91e-8ba0-465e-841d-6fb6dc517cc7` | COMPLETED |
| 1173-3 Restart + burst verification | `4e55f892-f750-4380-b9a3-9a354acb66e6` | COMPLETED |
| 1173-4 Handoff + 24h watch + memory rules | `67cc9023-80b3-4d6d-859b-9c20fe3c0249` | this doc |

## Out of scope (Phase 3 candidates)

- **Recover per-process application_name attribution.** Options: switch celery workers (where attribution matters most) to session pool mode + dedicated PgBouncer database stanza; use a PG extension that tags by client IP; or accept the loss and use Redis tags for telemetry instead.
- **Frontend dashboard-mount burst reduction.** Collapse ~30 simultaneous calls to 1-2 boot calls. Touches many components; high-effort. PgBouncer makes this less urgent but still good hygiene.
- **Make migrations alias automatic via DATABASE_ROUTERS** instead of requiring `--database=migrations`. Avoids forgetting the flag.
- **Add a `frontend/src/stores/bodyStore.ts` AbortController + 30s timeout** so a single hung fetch can't wedge the in-flight flag (Session 1173 incident discovery side-bug).
- **Railway parity.** Railway uses its own pooler; this PR is local-only. Document the divergence and ensure CI doesn't try to start PgBouncer.

## Reference: pgbouncer.ini content

The actual config lives at `/opt/homebrew/etc/pgbouncer.ini` (outside the repo since it's machine-specific). Reference copy preserved in this handoff so any dev can reproduce it:

```ini
;; PgBouncer configuration for unified-donkey-betz (Session 1173)

[databases]
unified_donkey_betz = host=127.0.0.1 port=5432 dbname=unified_donkey_betz connect_query='SET search_path TO studio, public, dbao, shared; SET statement_timeout TO 60000; SET idle_in_transaction_session_timeout TO 60000'

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 5433

auth_type = trust
auth_file = /opt/homebrew/etc/pgbouncer-userlist.txt
auth_user = unified_user

pool_mode = transaction
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3
max_client_conn = 500
ignore_startup_parameters = options,application_name

server_reset_query = DISCARD ALL
query_wait_timeout = 10
server_idle_timeout = 600

logfile = /opt/homebrew/var/log/pgbouncer.log
pidfile = /opt/homebrew/var/run/pgbouncer.pid
log_pooler_errors = 1

admin_users = unified_user
stats_users = unified_user
```

And the userlist (trust mode, just satisfies the existence requirement):

```
;; /opt/homebrew/etc/pgbouncer-userlist.txt
"unified_user" ""
```
