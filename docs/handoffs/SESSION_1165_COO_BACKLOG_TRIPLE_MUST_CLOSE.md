---
originating_session: 1165
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1165 handoff. Four PRs merged in one session, closing three MUSTs from Rigby's June 14 corrected v1 COO Nervous System Backlog (items #1 DB safety defaults, #3 stampede prevention, #6 retry-storm prevention). One additional wrapper-fix PR shipped first to fix a `donkeyking` user removal that surfaced as a 401 on the session-opening Rigby probe. Rigby ratified the design at every checkpoint — wrapper fix verdict ("unexpected drift, flag it"); pre-implementation review for each of the three MUSTs (scope, storage backend, apply lists, lock semantics); stagger pattern for hour=3/4 beat cluster; post-merge confirmation on each. Session also installed `pg_stat_statements` locally to make data-backed threshold picks (slowest observed query 2.4s → `statement_timeout=60s` = ~25× headroom) — a deliberate state change Chris explicitly authorized in-session.
---

# Session 1165 — COO Backlog triple-MUST close (#1, #3, #6)

**Date:** 2026-06-19
**Branch state at session close:** All work merged. Main is clean. Four PRs landed.

---

## TL;DR

Session 1165 ran a coordinated MUST-by-MUST close on Rigby's June 14 corrected-v1 COO Nervous System Backlog. Three of the four open MUSTs landed end-to-end, plus one pre-arc wrapper fix that surfaced when the session-opening Rigby probe 401-d on a stale `donkeyking` user token.

Four PRs landed:

- **#2294** (`fix`) — `tools/pa_local.sh` wrapper repointed at `chris`'s local DRF token after discovery that the local DB no longer has a `donkeyking` user.
- **#2295** (`feat`) — **COO #1 (MUST: DB safety defaults).** `statement_timeout=60s` + `idle_in_transaction_session_timeout=60s` via the existing PG-only `OPTIONS` block, plus task-boundary `close_old_connections()` in `core/celery_telemetry.py` postrun/failure handlers. Numbers picked from real `pg_stat_statements` data installed mid-session.
- **#2296** (`feat`) — **COO #3 (MUST: singleton locks + jitter).** New `core/services/redis_lock.py` primitive (`singleton_lock` context manager + `@singleton_task` decorator + `acquire_singleton_lock`/`release_singleton_lock` lower-level pair). Applied to 9 high-stampede-risk periodic tasks; 2 ad-hoc lock sites migrated to the canonical primitive; hour=3/4 MST beat clusters fully staggered per Rigby's plan (hour=4 :00 went 9 entries → 1).
- **#2297** (`feat`) — **COO #6 (MUST: retry-storm prevention).** New `core/services/retry_policy.py` (`compute_retry_countdown` exponential-with-jitter + `check_retry_budget` Redis-backed sliding-window counter + `reset_retry_budget` ops escape hatch). Applied to 4 high-fail-rate periodic tasks (`aggregate_roi_metrics_daily`, `evaluate_ml_predictions`, `verify_betting_outcomes`, `generate_daily_betting_brief`) that previously had `raise self.retry(exc=e)` with NO countdown.

| PR | Theme | Merge SHA |
|---|---|---|
| **#2294** | `pa_local.sh` wrapper → chris (donkeyking removed locally) | `053631c8` |
| **#2295** | DB safety defaults — statement_timeout + idle_in_tx_session_timeout + task-boundary `close_old_connections()` | `43933cfe` |
| **#2296** | Singleton-task stampede prevention + hour=3/4 beat stagger | `65b37fc3` |
| **#2297** | Retry-storm prevention — exponential backoff + retry budgets | `f5a080b3` |

**COO Backlog state after Session 1165:**

| Item | Tier | Status |
|---|---|---|
| #1 DB safety defaults | MUST | ✅ Session 1165 (#2295) |
| #2 Per-process Postgres `application_name` tagging | MUST | 🟡 Open — Session 1166 PRIORITY 1 candidate |
| #3 Singleton locks + jitter | MUST | ✅ Session 1165 (#2296) |
| #5 Memory telemetry + automatic downshift | SHOULD | 🟡 Open |
| #6 Retry-storm prevention | MUST | ✅ Session 1165 (#2297) |
| #7 Top Consumers ops endpoint | SHOULD | 🟡 Open — could fold into existing ops surface |
| #8 Queue depth + backlog age per queue | SHOULD | ✅ Closed Session 1164 |

Three of four open MUSTs from Rigby's June 14 corrected v1 are now landed in production code. The remaining MUST (#2 `application_name`) is the smallest-scope item left.

---

## What shipped

### PR #2294 — pa_local.sh wrapper → chris (donkeyking removed locally)

**Discovery:** Session-opening Rigby probe (`platform_config_tool overview` to confirm `service_context: local`) 401-d with `authentication_required`. Investigation showed the local DB has only 3 users: `chris` (chris@donkeybetz.com, superuser), `system`, `system_autonomous`. The hardcoded `PA_API_TOKEN` in `tools/pa_local.sh` belonged to a `donkeyking` user that no longer exists locally. Memory rule `feedback_pa_local_verify_ownership.md` predicted this exact failure mode — drift between hardcoded wrapper assumptions and local user state.

**Surface:** `tools/pa_local.sh` token swap to chris's local DRF token (`4b458900…`); comment block refreshed to record the drift + Rigby's verdict ("Unexpected drift — flag it. Token + conversation ownership should match `chris` if that's the operator account."). Both pinned conversations (`pa-f93d77e34f5d`, `pa-7684c8f93185`) verified owned by chris before the swap.

**Round-trip:** smoke-tested pre-merge AND post-merge through Rigby.

**No production code touched** — operator-tool config only.

### PR #2295 — DB safety defaults (COO #1)

**Surface:**
- `core/settings.py:268` — existing `options` connection string extended in-place from `'-c search_path=studio,public,dbao,shared'` to include `-c statement_timeout=60000 -c idle_in_transaction_session_timeout=60000`. PG-only block; SQLite path untouched.
- `core/celery_telemetry.py` — `try: close_old_connections() except: log` block added at the end of `on_task_postrun` + `on_task_failure`, after telemetry + notification. Runs even if upstream telemetry or notification fails (Rigby's nuance: "ensure it runs even if telemetry write fails").

**Numbers came from data, not vibes.** Installed `pg_stat_statements` locally during the session (Chris explicitly authorized: "If you need pg_stat_statements then install it") — edit to `/opt/homebrew/var/postgresql@15/postgresql.conf` line 740 (`shared_preload_libraries = 'pg_stat_statements'`), `brew services restart postgresql@15`, `CREATE EXTENSION IF NOT EXISTS pg_stat_statements;` as the `donkeyking` Homebrew owner. Sampled 1,005 query calls across 149 unique statements:

| Metric | Value |
|---|---|
| p50 mean | 0.08ms |
| p99 mean | 29.57ms |
| p99 max | 82.72ms |
| **Slowest single query** | **2,405ms** (`SELECT FROM core_spiderdata`) |
| Current `idle in transaction` count | 0 ✅ |

60s gives ~25× headroom over the slowest observed query. Rigby approved 60s/60s after seeing the data.

**4-step acceptance smoke** (all green):

1. `SELECT pg_sleep(75)` via fresh Django connection → terminated at **60.10s** with "canceling statement due to statement timeout" ✅
2. Opened transaction, idle 75s → Postgres killed the session (psycopg2 reconnect required) ✅
3. Burst 100 `core.tasks.run_heartbeat` tasks → connection count rose 31 → 57 and **stayed flat** (well under `max_connections=100`, no climb past natural concurrency) ✅
4. `python manage.py pa_acks_health --json` → `status: OK`, `sustain_gating` block present, `is_pa_relevant` filter intact ✅

**Auxiliary state change not in this PR:** Local Homebrew `postgresql@15` now loads `pg_stat_statements` via `shared_preload_libraries`. Edit lives in `/opt/homebrew/var/postgresql@15/postgresql.conf` (not tracked by git). Production / staging would need the same change separately if we want pg_stat_statements there — queued as aspirational follow-on, not blocking.

### PR #2296 — Singleton-task stampede prevention + hour=3/4 beat stagger (COO #3)

**New primitive — `core/services/redis_lock.py` (~165 lines + 12 tests):**

Three callable APIs, single canonical SETNX-style lock backed by Django cache (Redis under the hood):

- `singleton_lock(name, ttl, value)` — context manager
- `@singleton_task(name, ttl)` — decorator wrapping a Celery task body
- `acquire_singleton_lock(name, ttl, value)` + `release_singleton_lock(name)` — lower-level pair for callsites that need explicit early-release on a precondition-failed exit path

Design constraints from Rigby's pre-implementation review:

- **TTL-only release** in the contextmanager / decorator paths. Django cache lacks atomic compare-and-delete; unconditional release is unsafe under TTL contention with long-running holders (the well-known "long task TTL-expires, second acquirer takes lock, original holder finishes and deletes the new holder's lock, third invocation stampedes" race).
- Explicit `release_singleton_lock()` is opt-in for manual sites with early-exit shortcuts. Race-condition caveat documented in source.
- Lock value carries `task_id` when available (debuggable via `cache.get(LOCK_PREFIX + name)`).
- Key prefix `singleton_lock:` so a future ops surface can `KEYS singleton_lock:*` to enumerate active holders.

**Applied `@singleton_task` to 9 high-stampede-risk periodic tasks** (per Rigby's apply list, with `run_heartbeat` dropped on her nuance — "cheap + frequent; singletoning would hide scheduling lag"):

| Task | TTL |
|---|---|
| `capture_pa_acks_health_snapshot` | 300s |
| `monitor_celery_health` | 600s |
| `scan_spider_opportunities` | 1800s |
| `cleanup_stale_agent_executions` | 600s |
| `run_spider_network` | 7200s (historical 45h max from Session 1164 task-duration sniff) |
| `spider_data_retention` | 1800s |
| `enforce_data_retention` | 3600s |
| `promote_to_shared_knowledge` | 1800s |
| `detect_duplicate_initiatives` | 1800s |

**Migrated 2 ad-hoc lock sites to canonical primitive** (behavior-preserving, namespace-prefix changes):

- `core/tasks.py` `_pa_context_rebuild` — `f"pa_ctx:rebuild_lock:{hash}"` → `singleton_lock:pa-ctx-rebuild:{hash}`
- `core/tasks_content.py` `generate_self_blog_deliberation` — `deliberation_blog_running` → `singleton_lock:deliberation-blog-running`

**Deferred to focused follow-on PR:** `core/tasks_content.py` operator_edge (6 release sites across multiple exit paths) and `_circuit_breaker_check` step-3 single-flight lock. Both are bigger blast radius and worth their own review pass.

**Beat schedule stagger — hour 3 + 4 MST clusters:**

Per Rigby's stagger pattern (full plan in conversation `pa-f93d77e34f5d`). Worst hotspot was hour=4 minute=0 with 9 entries firing simultaneously; second worst was hour=4 minute=30 with 6.

Both clusters now spread across the full hour with no minute collisions. Heavy retention tasks (`spider_data_retention`, `enforce_data_retention`) pushed to end of hour 4 (`:55`, `:58`) for clear separation. Anchor wall-clock times preserved where Rigby called them out (hour=3 :00, :15, :30; hour=4 :00, :30, :45 — Sun-only `cleanup_llm_call_logs` stays at :15).

| Cluster | Before | After |
|---|---|---|
| Hour 3 :00 | 5 entries | 1 entry |
| Hour 3 :30 | 3 entries | 1 entry |
| Hour 4 :00 | 9 entries | 1 entry |
| Hour 4 :30 | 6 entries | 1 entry |

**Test coverage:** `core/tests/test_redis_lock.py` — 12 tests via `SimpleTestCase` (no DB dependency). All pass.

### PR #2297 — Retry-storm prevention (COO #6)

**New primitive — `core/services/retry_policy.py` (~215 lines + 19 tests):**

Two explicit helpers (no decorator — that fought Celery's `Retry` exception machinery; see module docstring for the design rationale of moving away from a decorator):

- `compute_retry_countdown(retries, base, max_delay, jitter)` — canonical exponential-with-jitter helper. `base * 2**retries`, capped at `max_delay` (default 3600s), ±25% jitter when enabled, floor of 5s.
- `check_retry_budget(task_name, window_seconds, max_retries, fingerprint)` — Redis-backed sliding-window counter via Django cache. Returns `(allowed, reason)`. Atomic on Redis backend; degrades to "allow but log" on hypothetical non-atomic backends.
- `reset_retry_budget(task_name, fingerprint)` — manual ops escape hatch.

Design constraints from Rigby's pre-implementation review:

- Django cache backend (matches `redis_lock.py`; sidesteps the Session 1144 Redis-pooling-sweep backlog by not adding another inline client).
- Counter increments only when callsite is about to schedule a retry, not on every task invocation.
- Default fingerprint = task_name only (global budget); multi-tenant callsites should pass a per-tenant fingerprint.
- Countdown floor (5s) + max_retries ceiling at decorator layer (belt + suspenders against unbounded loops).

**Applied to 4 high-fail-rate periodic tasks** (per Rigby's apply list; agent-task family deferred pending fingerprinting strategy):

| Task | Window | Max Retries | Base |
|---|---|---|---|
| `aggregate_roi_metrics_daily` | 3600s | 5 | 60s |
| `evaluate_ml_predictions` | 3600s | 5 | 60s |
| `verify_betting_outcomes` | 3600s | 5 | 60s |
| `generate_daily_betting_brief` | 3600s | 5 | 120s |

All 4 previously had `raise self.retry(exc=e)` with NO countdown — pure Celery-default retry behavior. Now budget-gated with explicit exponential backoff.

**Test coverage:** `core/tests/test_retry_policy.py` — 19 tests via `SimpleTestCase`. All pass. Combined with `test_redis_lock.py`: 31 tests total, all pass.

---

## New persistent artifacts

| File | Lines | Purpose |
|---|---|---|
| `core/services/redis_lock.py` | ~165 | Singleton-task lock primitive (Session 1165 PR #2296) |
| `core/tests/test_redis_lock.py` | ~157 | 12-test contract for redis_lock |
| `core/services/retry_policy.py` | ~215 | Retry policy primitive (Session 1165 PR #2297) |
| `core/tests/test_retry_policy.py` | ~189 | 19-test contract for retry_policy |

**Modified files:** `core/settings.py` (PG OPTIONS), `core/celery_telemetry.py` (close_old_connections hooks), `core/celery.py` (beat stagger), `core/tasks.py` (decorators + ad-hoc lock migration + retry policy applies), `core/tasks_content.py` (deliberation_blog migration + betting_brief retry policy), `core/tasks_financial.py` (2 retry policy applies), `intelligence/tasks.py` (`scan_spider_opportunities` decorator), `tools/pa_local.sh` (token swap).

---

## Coverage gaps closed

1. **COO Backlog #1 (MUST: DB safety defaults)** — `statement_timeout` + `idle_in_transaction_session_timeout` + task-boundary `close_old_connections()`. End-to-end via 4-step acceptance smoke.
2. **COO Backlog #3 (MUST: stampede prevention)** — canonical `singleton_lock` primitive + 9 task applies + 2 ad-hoc migrations + hour=3/4 stagger.
3. **COO Backlog #6 (MUST: retry-storm prevention)** — canonical `retry_policy` primitives + 4 task applies.
4. **Local Postgres observability gap** — `pg_stat_statements` extension installed locally; ad-hoc threshold picks can now be data-backed instead of vibes-based. Aspirational follow-on for staging/prod.
5. **`pa_local.sh` drift** — wrapper repointed at chris's token after `donkeyking` user removal. The `feedback_pa_local_verify_ownership.md` memory rule predicted this failure mode; now also documented in the wrapper's comment block.

---

## New gotchas captured

### "Decorators that catch exceptions can collide with Celery's `Retry` machinery"

My first draft of `core/services/retry_policy.py` included a `@with_retry_policy(...)` decorator that caught exceptions in a wrapper and called `self.retry()`. Bug: `self.retry()` from the task body raises `celery.exceptions.Retry` (which IS an `Exception` subclass), so my decorator's `except Exception` would catch it and double-retry. Fix: ditched the decorator, ship two explicit helpers (`compute_retry_countdown` + `check_retry_budget`) that callsites use directly. Each callsite stays transparent about what's happening.

**Rule:** when wrapping a Celery task body in a decorator that catches exceptions, either (a) explicitly let `celery.exceptions.Retry` propagate, or (b) prefer explicit helpers over the decorator pattern. The control flow in (b) is easier to reason about and skip the import dance.

### "Stale wrapper tokens silently 401 on session entry"

The Session 1165 entry probe failed with `authentication_required` because the local DB no longer has the `donkeyking` user that `tools/pa_local.sh` was pointing at. Memory rule `feedback_pa_local_verify_ownership.md` predicted this exact failure mode, but in practice we discovered it on the first call rather than via a pre-check.

**Rule extension:** the wrapper comment block should record the operator-account assumption (now done in #2294 — references chris explicitly). Future sessions opening with a 401 on the Rigby probe should immediately suspect wrapper drift before deeper investigation.

### "`pg_stat_statements` is a multi-step install, not a one-liner"

Running the data sniff for COO #1 required:
1. Edit `postgresql.conf` to add `shared_preload_libraries = 'pg_stat_statements'`
2. `brew services restart postgresql@15` (kills all active connections)
3. `CREATE EXTENSION IF NOT EXISTS pg_stat_statements;` as a superuser
4. Wait for organic traffic to populate the stats table

**Rule:** when a session needs ad-hoc Postgres-internal observability (slow queries, lock waits, connection patterns), the install is a substantial action requiring `brew services restart` and superuser CREATE EXTENSION. The Homebrew local `postgresql@15` is separate from the Docker `unified-postgres` — restarting the local instance doesn't affect Docker fleet apps but DOES break local daphne/celery connections (CONN_HEALTH_CHECKS handles the reconnect cleanly).

---

## Cross-session lessons

- **"Data wins over vibes" for threshold picks pays off twice.** COO #1's 60s timeout was data-backed via `pg_stat_statements` (slowest observed 2.4s → 25× headroom). The same discipline let me pick TTLs for `@singleton_task` from observed task durations (Session 1164 sniff) and budget caps for `retry_policy` from observed failure patterns.
- **The "primitives + opt-in apply list" scope is the right Phase 1 for stampede / retry-storm prevention.** Both PRs #2296 and #2297 followed this shape: ship the canonical primitive + tests + apply to a hand-picked set, defer bulk migration. Reduces blast radius; gives ops a chance to spot regressions on a small set before fanning out.
- **Manual stagger beats `before_task_publish` jitter for v1.** Rigby explicitly favored the deterministic manual rewrite over a clever invisible-modifier interceptor — operator surprise + debugging complexity were the named tradeoffs. The manual stagger is also self-documenting in the beat_schedule definition itself.
- **Drop one decorator's worth of magic when explicit helpers do the job.** First-draft `@with_retry_policy` decorator was discarded for `compute_retry_countdown` + `check_retry_budget`. Callsite verbosity is the small cost; control-flow transparency is the big win.
- **Pre-implementation Rigby review at every MUST scope** (not just "is this a good idea" but "scope A vs B, storage backend, apply list, error semantics") is the gating step that makes single-session triple-MUST closes possible. Without it, the apply list arguments would have eaten the session.
- **Workers need restart after `core/tasks.py` body changes.** Memory rule `feedback_new_shared_task_needs_worker_restart.md` covers `@shared_task` additions AND any module imported by a task body. Sessions 1165 PRs #2296 and #2297 both modified task bodies and both required `pkill -9 -f celery; rm -f .celery*.pid; make celery` after merge. Done; verified live via `celery -A core inspect registered`.

---

## Behavioral contracts / invariants (post-merge, system-wide)

Three statements that should now always be true. If any of these is violated under normal operation, that's a signal worth investigating — not a bug to silently patch around.

1. **No SQL statement should run longer than 60 seconds** unless the executing transaction has explicitly opted out via `SET LOCAL statement_timeout = '0'`. Any uncaught long query is either (a) a workload the timeout was specifically designed to catch (good — root-cause it), or (b) a legitimate batch operation that needs the per-tx escape and a comment explaining why.
2. **No task wrapped with `@singleton_task(name, ttl)` should ever overlap itself.** The lock guarantees at most one in-flight instance per task name across all workers. If you see two concurrent runs of the same protected task in `CeleryTaskEvent`, the lock primitive itself has regressed (or someone removed the decorator) — verify via `cache.get('singleton_lock:<name>')` and the `@singleton_task` decorator on the task definition.
3. **Retry-budget denials should not fire under normal conditions.** A `retry DENIED — budget_exhausted` log line implies one of: (a) an upstream dependency is down (broken API, DB outage, rate limit), (b) a real bug in the task itself burning retries on the same exception, or (c) the budget cap is set too tight for the task's natural failure rate. Each denial is a signal to investigate the root cause and either fix the upstream, fix the bug, or raise the cap with rationale.

These three invariants are the post-merge "should always be true" companion to the rollback levers below ("how to break them in an emergency") and the 24h watch checklist further down ("how to verify they hold").

---

## Rollback / disable levers (per Rigby's Session 1165 close-out review)

Operational escape hatches if any of the three MUSTs misbehaves in production. Documented here so a future operator can disable a single primitive without rolling the whole session.

### #2295 — DB safety defaults

**Location:** `core/settings.py:268` — the `options` connection string.

**Soften (recommended emergency lever):**
```python
# raise statement_timeout from 60000 → 120000 ms (2 min)
'options': (
    '-c search_path=studio,public,dbao,shared'
    ' -c statement_timeout=120000'
    ' -c idle_in_transaction_session_timeout=120000'
),
```
Then restart daphne + celery to flush old PG connections. Existing connections honor the OLD settings until they cycle (CONN_MAX_AGE=60).

**Fully disable:**
```python
# revert to pre-1165 state — no statement_timeout, no idle_in_tx
'options': '-c search_path=studio,public,dbao,shared',
```

**Per-tx override** (when a single tx legitimately needs to exceed the timeout — e.g., heavy backfill):
```python
from django.db import transaction, connection
with transaction.atomic():
    with connection.cursor() as c:
        c.execute("SET LOCAL statement_timeout = '0'")
        # ... long-running work ...
```
`SET LOCAL` is scoped to the transaction only; safe under `CONN_MAX_AGE=60` connection reuse.

**Task-boundary `close_old_connections()`:** the postrun/failure hooks in `core/celery_telemetry.py` are wrapped in `try/except` blocks that swallow any errors — they cannot break task execution. To disable, comment out the two `close_old_connections()` `try:` blocks added at the end of `on_task_postrun` and `on_task_failure`.

### #2296 — Singleton-task locks

**Lock key format:** `singleton_lock:<task_name>`. The `<task_name>` is the string passed to `@singleton_task(...)` — NOT the dotted Celery name. Example: the decorator `@singleton_task("capture-pa-acks-health-snapshot", ttl=300)` writes to Redis key `singleton_lock:capture-pa-acks-health-snapshot`.

**Bypass a lock for emergency run** (manual delete via Django shell):
```python
from django.core.cache import cache
from core.services.redis_lock import LOCK_PREFIX
cache.delete(LOCK_PREFIX + "capture-pa-acks-health-snapshot")
# now the next fire of the task will acquire cleanly
```

**Enumerate active locks** (find what's currently held):
```python
import redis
r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
keys = [k.decode() for k in r.scan_iter(match='*singleton_lock:*')]
for k in keys:
    print(k, '→', r.get(k))
# value carries task_id when @singleton_task wrapped a bind=True task
```

**Owner-aware semantics caveat:** TTL-only release per Rigby's Session 1165 design — we do NOT explicitly delete the key on task completion. The TTL is the only release path. If you manually delete a lock that a long-running task still holds, a second acquirer can take the lock; when the first task finally finishes, it does NOT delete the new acquirer's lock (no implicit release on context exit). Race is bounded to the TTL window.

**Fully disable** `@singleton_task` on a specific task: comment out the decorator line, restart workers (`pkill -9 -f celery; rm -f .celery*.pid; make celery`). Task reverts to pre-1165 stampede-prone behavior.

### #2297 — Retry budgets

**Budget key format:** `retry_budget:<task_name>[:<fingerprint>]`. The `<task_name>` is the string passed to `check_retry_budget(...)`, NOT necessarily the dotted Celery name.

**Identify "budget exhausted" vs real failures in logs:**
- Budget denial: log line `[TASK] retry DENIED — budget_exhausted: N/M retries in 3600s window (key=retry_budget:...)`. Task returns `{"retry_denied": True, "reason": ..., "original_exc": ...}` payload — marked SUCCESS by Celery, not FAILURE.
- Real failure (budget allows): log line `[retry_policy] <task> scheduling retry K/M at +Xs (allowed: K/N ...)`. Task remains in `RETRY` state.
- Find recent denials: `grep "retry DENIED" celery*.log`.
- Count denials per task in 24h: `grep "retry DENIED" celery*.log | awk -F"—" '{print $1}' | sort | uniq -c | sort -rn`.

**Temporarily raise budget for a specific task** — edit the callsite's `max_retries` argument:
```python
# core/tasks_financial.py line ~672 (aggregate_roi_metrics_daily)
allowed, reason = check_retry_budget(
    "aggregate_roi_metrics_daily",
    window_seconds=3600,
    max_retries=20,  # was 5 — emergency raise
)
```
Restart celery workers to pick up the change. Lower priority alternative: increase `window_seconds` to 7200 so the budget resets twice as fast in absolute terms while the per-window cap stays the same.

**Manually reset a budget counter** (ops escape hatch from the primitive):
```python
from core.services.retry_policy import reset_retry_budget
reset_retry_budget("aggregate_roi_metrics_daily")
# returns True if a counter was cleared, False if it didn't exist
```

**Fully disable budget gating on a specific task:** revert the callsite from the new pattern back to `raise self.retry(exc=e)`. No new tests required; the helper functions remain available for re-application later.

---

## What to watch in the first 24h post-merge

Lightweight observability checks for the first day after the Session 1165 PRs go live overnight. Rigby's recommendation: one AM check around 7:30–9:00 AM MST, then trust the existing observation surfaces.

### 1. PG connection state — should stay quiet

```bash
.venv/bin/python manage.py dbshell -- -c "
SELECT state, count(*) FROM pg_stat_activity
WHERE datname='unified_donkey_betz' GROUP BY state ORDER BY count DESC;"
```
**Expect:** total ~30–60 connections, `idle in transaction` count = 0. If `idle in transaction` > 0, something held a tx past the new 60s timeout — investigate.

### 2. `statement_timeout` terminations — count + offenders

```bash
# count of statement_timeout errors today
grep -i "canceling statement due to statement timeout" /opt/homebrew/var/log/postgresql@15.log 2>/dev/null | wc -l

# which task triggered (from Django logs)
grep -i "statement_timeout\|canceling statement" celery*.log daphne*.log 2>/dev/null | head -20
```
**Expect:** zero or near-zero. Each one is a signal that a real query is hitting the 60s cap — either a legitimate long query that needs `SET LOCAL statement_timeout = '0'` per-tx, or a runaway query that the timeout caught (good).

### 3. Singleton-lock skips for the 9 protected tasks

```bash
# from celery worker logs — every time @singleton_task refused a fire
grep -i "singleton_task.*skipping\|concurrent run detected" celery*.log | head -30

# count by task
grep -i "singleton_task.*skipping" celery*.log | grep -oE "skipping [a-z-]+" | sort | uniq -c | sort -rn
```
**Expect:** zero or low counts for `monitor-celery-health`, `cleanup-stale-agent-executions`, `capture-pa-acks-health-snapshot`. Higher counts for `run-spider-network` or `scan-spider-opportunities` are normal if those tasks legitimately take longer than their fire interval. Investigate if a task that should be fast (e.g., `monitor-celery-health`, 600s TTL) is hitting the lock — means it ran > 600s, which is itself a finding.

### 4. Retry-budget denials by task

```bash
# all denials today
grep "retry DENIED" celery*.log | head -30

# count by task
grep "retry DENIED" celery*.log | awk -F"]" '{print $1}' | sort | uniq -c | sort -rn
```
**Expect:** zero unless an upstream is down. Each denial means a task hit `max_retries=5` within a 1h window — investigate the root cause (broken API, DB outage, etc.) and use `reset_retry_budget(task_name)` to clear after fixing.

### 5. Celery queue depth around 3:00–5:00 AM MST — stagger validation

```bash
# from cockpit_tool.queue_lengths via PA chat OR direct redis
redis-cli LLEN celery
redis-cli LLEN long_running
redis-cli LLEN broadcast
redis-cli LLEN pa

# pa_acks_health JSONL for the overnight window
tail -20 logs/pa_acks_health/$(date +%Y-%m-%d).jsonl | .venv/bin/python -c "
import json, sys
for line in sys.stdin:
    d = json.loads(line)
    print(d['generated_at_mt'], 'status:', d['status'], 'depth:', d.get('queue_depth', {}).get('depth'))
"
```
**Expect:** no backlog cliff at 3:00 or 4:00 MST. With the stagger, queues should grow gradually as each minute fires its task rather than 9 tasks slamming the worker pool at :00.

### AM check execution plan

Around 7:30–9:00 AM MST, run all 5 checks above. Total expected time: <10 minutes. If everything is clean (zero unexpected terminations, zero retry denials, expected stampede-skip counts), document the result in the next session handoff and the operational surfaces can be trusted going forward. If any check surfaces unexpected behavior, use the rollback levers above to soften/disable while investigating.

---

## Open items carrying into Session 1166

### MUST tier
- **COO #2 — Per-process Postgres `application_name` tagging.** Smallest open MUST. Currently only the global `'unified_donkey_betz'` value. Needs service/queue/worker variation via Procfile entry or settings hook. Rigby's recommended next-quick-win.

### SHOULD tier
- **COO #5 — Memory telemetry + automatic downshift.** Procfile already has `--max-memory-per-child` caps; this adds visibility + throttle hook.
- **COO #7 — Top Consumers ops endpoint.** Pairs naturally with the queue_pressure surface Session 1164 added — could fold into a single ops snapshot rather than a separate gateway.

### Consolidation / deferred from Session 1165
- **Operator_edge lock consolidation** (`core/tasks_content.py:4216` + 6 release sites). Behavior-preserving but bigger blast radius; deferred from PR #2296.
- **`_circuit_breaker_check` step-3 lock consolidation.** Symmetric to operator_edge. Worth its own focused PR.
- **Agent-task family retry budgets.** Needs fingerprinting strategy (`agent_name + user_id + workspace_id`) to avoid global suppression during transient incidents.
- **Bulk migration of ~5 linear/fixed countdown sites** (`core/tasks_agents.py` family) to `compute_retry_countdown`.

### Carryovers from Session 1164 still queued
- **Item C (WARN-persist → CRIT escalation).** Now actionable after ~24h of new-schema `sustain_gating` JSONL telemetry post-#2292. Session 1166 can evaluate.
- **`capture_pa_acks_health_snapshot` slow-task investigation.** Rigby flagged 36-min max, 18-min avg as suspicious for a "snapshot" workload. Non-blocking, separate scope; also a canary for the new 60s `statement_timeout`.

### Aspirational
- Install `pg_stat_statements` on staging/prod for live p99-based threshold reviews (no longer just local).
- Beat-schedule the regens (weekly Celery beat for `_provenance.json` + 8 `build_*_audit` commands).
- Redis pooling sweep (~40 inline `redis.Redis.from_url(...)` sites) — Session 1144 backlog item still queued; Session 1165's two new services (`redis_lock.py` + `retry_policy.py`) intentionally avoided adding more.
