# Celery Worker Lifecycle — Validation Report

**Tool:** Celery worker lifecycle — the substrate that decides when worker child processes recycle, how memory pressure is bounded, and whether operators can observe recycle events. Anchored to MEMORY `feedback_local_celery_stall_playbook` (April 2026 — 45 minutes chasing "tool broken?" before finding an 8-day-old ML deadlock + 332k stale queue backlog).

**Files traced:**
- `core/celery.py:18-22` — `Celery('unified_donkey_betz_core')` + `app.config_from_object('django.conf:settings', namespace='CELERY')`.
- `core/settings.py:837-866` — `CELERY_*` config incl. `WORKER_MAX_TASKS_PER_CHILD=50`, `WORKER_MAX_MEMORY_PER_CHILD=300_000`, `TASK_ACKS_LATE=True`, `TASK_REJECT_ON_WORKER_LOST=True`.
- `Procfile:31-38` — production celery workers (`--pool=prefork` on Railway/Linux; per-worker `--max-tasks-per-child` overrides).
- `Makefile:240-324` — local dev celery workers (`--pool=solo` on macOS; ignores per-worker recycle flags).
- `Makefile:357-414` — `celery-stop` target.
- `Makefile:416-426` — `celery-status` target.

**Session validated:** S2731 (Batch D tool 2 of 3).
**HEAD at validation:** `7770b7a2` (post-Batch-D-tool-1 close on feature branch).
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred.
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch D tool 2 of 3). Trace + 3 code/config patches (F-CW-1 Makefile celery-recycle + solo-pool note; F-CW-2 worker lifecycle signal handlers in `core/celery.py`; F-CW-3 celery-status completeness) + 14 regression tests complete; 272 total pass across all Batch A + B + C + D tools 1-2 validation-2728 files + `test_td_autofill_safety` + `test_pa_tool_args_malformed`.

---

## 1. Intended purpose

Celery worker child processes must recycle periodically to bound:
- **Memory drift** from accumulating Python cache state (module-level `_CLIENT_CACHE`, `_ASYNC_CLIENT_CACHE` in the LLM factories; `_aggregator_cache`, `_service_cache`, `_backlog_cache` across services).
- **Stale DB connections** that Django's `close_old_connections` doesn't always reap in long-lived worker children.
- **Eager-load damage** — MEMORY-crystallized failure class: `MLEngine.__init__` loading DistilBERT in the worker parent silently deadlocks the whole worker (S1871 fix).

The recycle knobs are `--max-tasks-per-child` (prefork-only) and `--max-memory-per-child` (prefork-only). Both are ignored under `--pool=solo` (macOS local dev) because solo pool doesn't fork children.

**Two-environment split:**
- **Railway (production, Linux, prefork)**: recycle flags per Procfile line honored; child dies after N tasks or MB threshold.
- **macOS local dev (solo pool)**: recycle flags in settings.py ignored; workers run indefinitely.

**This tool's scope**: verify the recycle contract matches deployment reality, sweep for observability gaps around silent recycle events, and patch the diagnostic gaps that made the S1184-adjacent stall pattern hard to see.

## 2. Rigby's belief (per MEMORY + prior tool context)

Load-bearing MEMORY:
- `feedback_local_celery_stall_playbook` — Rigby knows the 6-step diagnostic sequence: `CeleryTaskEvent` telemetry → queue depth check → `celery inspect ping` → log grep for ML deadlock markers → purge stale queues → restart WITHOUT beat first.

Rigby's mental model at HEAD:
- Workers recycle on Railway per Procfile flags. ✓ (VERIFIED at §3.2)
- Local workers running `make celery` recycle per `CELERY_WORKER_MAX_TASKS_PER_CHILD=50`. **✗ WRONG** — solo pool ignores this. Local workers never recycle.
- `celery inspect ping` works if worker is alive. ✓ (unless deadlocked in ML `__init__`).
- The stall diagnostic in the MEMORY rule works if the operator remembers to run it. But **no signal in worker logs** tells operators "your local worker has been running 12 days without recycle" — the drift class is silent until Rigby stalls.

## 3. Constants / signatures (verbatim capture)

### 3.1 `core/settings.py:856-866` — Celery worker config

```python
CELERY_TASK_ACKS_LATE = True                   # tasks acked on completion (except PA — S1159)
CELERY_TASK_REJECT_ON_WORKER_LOST = True       # requeue when worker crashes mid-task
CELERY_RESULT_EXPIRES = 3600                   # 1h TTL on Redis result rows
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50         # recycle after 50 tasks (prefork only)
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 300_000   # 300MB per child in KB (prefork only)
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60          # 25 min soft; 30 min hard (line 844)
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = 'redis://localhost:6379/2' # broker DB 2
CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'
CELERY_BROKER_POOL_LIMIT = 20
CELERY_BROKER_HEARTBEAT = 120
```

### 3.2 `Procfile:31-38` — production recycle flags

| Worker | `--pool` | `-c` | `--max-tasks-per-child` | `--max-memory-per-child` |
|---|---|---|---|---|
| celery-worker | prefork | 1 | 5 | 150000 KB (~150 MB) |
| celery-pa | prefork | 1 | 10 | 200000 KB (~200 MB) |
| celery-content | prefork | 1 | 2 | 250000 KB (~250 MB) |
| celery-long-running | prefork | 2 | 2 | 150000 KB (~150 MB) |
| celery-long-running-2 | prefork | 2 | 2 | 150000 KB (~150 MB) |
| celery-broadcast | threads | 3 | 50 | 200000 KB (~200 MB) |
| celery-beat | (scheduler) | — | — | — |
| code-worker | prefork | 1 | 1 | 400000 KB (~400 MB) |

**All prefork workers honor recycle flags.** celery-broadcast uses threads (not fork) — max-tasks-per-child ignored, memory limit ignored.

### 3.3 `Makefile:240-324` — local dev workers

All 5 local celery workers use `--pool=solo`. Solo pool does NOT fork child processes.

- **`CELERY_WORKER_MAX_TASKS_PER_CHILD=50` is silently ignored** — no children to recycle.
- **`CELERY_WORKER_MAX_MEMORY_PER_CHILD=300_000` is silently ignored** — no children to kill.
- Local workers run indefinitely; module-level caches grow indefinitely; DB connections may accumulate.

### 3.4 `Makefile:416-426` — `celery-status` target

```
Workers:
  ✓ Default worker (quick tasks)
  ✓ Long-running worker (slow tasks)
  ✓ Broadcast worker (status updates)
Scheduler:
  ✓ Celery beat running
```

**Missing from `celery-status`**:
- `pa` worker (started by `make celery` at line 257-267)
- `code_jobs` worker (started by `make celery` at line 315-324)

If either crashes but the 3 listed workers are up, `make celery-status` shows all-green.

## 4. Handler behavior (traced)

### 4.1 Railway (production) — VERIFIED-CORRECT

- Prefork children recycle per Procfile flags.
- `task_reject_on_worker_lost=True` requeues tasks if child dies mid-execution.
- `acks_late=True` (default) or `acks_late=False` (PA task per S1159 comment) — chosen per task.

### 4.2 macOS local dev — F-CW-1 DEFECT

- Solo pool ignores recycle flags.
- Module-level caches grow indefinitely.
- Operator has no signal until a stall reproduces (the S1184-adjacent pattern).

### 4.3 Worker recycle signal handlers — F-CW-2 DEFECT

Sweep of `core/` for `worker_process_init`, `worker_process_shutdown`, `worker_ready` signal handlers:

```bash
grep -rn "worker_process_init\|worker_process_shutdown\|worker_ready" core/
# → empty
```

**Zero signal handlers registered.** When a prefork child recycles on Railway, nothing logs — the recycle event is invisible unless the operator greps for the celery-internal "MainProcess: Restarting %r after max tasks reached" message (which fires at INFO from celery's `MainProcess` logger, easy to miss in tail).

### 4.4 `make celery-status` coverage — F-CW-3 DEFECT

Doesn't check `pa` or `code_jobs`. Silent misdiagnosis if either is crashed.

### 4.5 MEMORY rule diagnostic sequence — F-CW-4 VERIFIED

The 6-step sequence in `feedback_local_celery_stall_playbook` references:
- `CeleryTaskEvent` model → exists at `core/models.py` (verified).
- Redis broker at `localhost:6379/2` → matches `settings.py:837`.
- `celery inspect ping` → still the canonical Celery admin command.
- `.celery.pid`, `.celery-beat.pid` → still Makefile pidfile paths.
- `pkill -9 -f "celery -A core"` → still works.

**Rule remains VERIFIED at HEAD.**

## 5. Defaults inventory

| Default | Location | Value | Class |
|---|---|---|---|
| `CELERY_WORKER_MAX_TASKS_PER_CHILD` (default) | `settings.py:864` | 50 | prefork-only |
| `CELERY_WORKER_MAX_MEMORY_PER_CHILD` (default) | `settings.py:865` | 300_000 KB | prefork-only |
| `CELERY_TASK_TIME_LIMIT` | `settings.py:844` | 1800s (30 min) | universal |
| `CELERY_TASK_SOFT_TIME_LIMIT` | `settings.py:866` | 1500s (25 min) | universal |
| `CELERY_TASK_ACKS_LATE` | `settings.py:856` | True | overridden per-task |
| `CELERY_TASK_REJECT_ON_WORKER_LOST` | `settings.py:858` | True | universal |
| Local Makefile pool | `Makefile:252, 263, 278, 289, 321` | `--pool=solo` | ignores recycle |
| Procfile pool | `Procfile:31-38` | `--pool=prefork` (except broadcast=threads) | honors recycle |

## 6. Hidden filters inventory

Not applicable at this layer.

## 7. Limits inventory

See §5.

## 8. Silent-truncation test

Not applicable.

## 9. Silent-filter test

Not applicable.

## 10. Silent-fallback test

- **F-CW-1** (local solo pool ignores recycle flags): silent-fallback to unbounded-lifetime worker. No log signal.
- **F-CW-2** (no worker_process_init handlers): silent recycle on Railway. Recycle event visible only in celery's internal MainProcess logger.
- **F-CW-3** (celery-status incomplete): silent misdiagnosis when `pa` or `code_jobs` crashed.

## 11. Staleness test

- Local workers with module-level caches never invalidated between tasks: staleness class the MEMORY rule targets.

## 12. Freshness signal

- No worker uptime / task-count-in-child field in `celery-status`.
- No `[CELERY_WORKER_INIT]` log at child startup.

## 13. Provenance signal

Not applicable.

## 14. Authority / workspace assumptions

Not applicable.

## 15. Runtime dependencies

- Redis broker at `localhost:6379/2` (db=2 for broker, db=3 for result backend).
- Django `close_old_connections` requires task-level calls (13+ sites in `core/tasks_*.py` — none in `core/tasks_misc.py` PA task, which S1159 acks-late-false decision covers by design).

## 16. Recoverable failure modes

- Prefork child death → parent respawns automatically.
- `task_reject_on_worker_lost=True` → task requeued.
- Broker connection loss → 10 retries per `CELERY_BROKER_CONNECTION_MAX_RETRIES`.

## 17. STOP-and-report failure modes

- ML deadlock in worker parent — MEMORY-crystallized. Diagnostic sequence exists (F-CW-4); operator must run it.

## 18. Operator-action failure modes

- Local worker stall requires `make celery-stop && make celery` (documented in S2728 handoff §10).
- Stale queue backlog requires manual `redis-cli LLEN` + `DEL` per MEMORY rule.

## 19. Existing test coverage

**Zero.** Verified via:
```bash
grep -l "worker_max_tasks_per_child\|worker_process_init\|celery-status" core/tests/*.py
# → empty
```

## 20. Change list (code / docs / tests)

**Proposed patches (subject to Chris gate):**

- **F-CW-1 — Makefile comment note explaining solo-pool implication.**
  Local `--pool=solo` ignores `CELERY_WORKER_MAX_TASKS_PER_CHILD` and `CELERY_WORKER_MAX_MEMORY_PER_CHILD`. Adds a header comment to the `celery` target explaining this and suggesting `make celery-stop && make celery` as the periodic-recycle discipline for long-running local dev.
  Options:
  - **(a)** Comment-only.
  - **(b)** Comment + new `celery-recycle` target = `celery-stop` + `celery`.
  - **(c)** Switch local pool to `prefork` (would fix recycle but re-triggers macOS SIGSEGV issue — REJECT).
  Recommendation: **(b)** — one-line target aliasing `celery-stop && celery`, callable as `make celery-recycle`.

- **F-CW-2 — Register `worker_process_init` + `worker_process_shutdown` signal handlers.**
  Emit `[CELERY_WORKER_INIT]` at child startup (PID + hostname + queues) and `[CELERY_WORKER_SHUTDOWN]` at child exit. Recycle events on Railway become grep-visible in ≤1 second instead of requiring parse of celery's MainProcess logger.
  Signal registration in `core/celery.py` module scope (fires per-child on prefork; once per process on solo).

- **F-CW-3 — Extend `make celery-status` to check `pa` + `code_jobs` workers.**
  Adds two lines mirroring the existing pattern. Silent-crash class F-CW-3 identified closed. Also adds a per-worker log-tail-tail hint that Rigby / operator can copy-paste when a worker is missing.

- **F-CW-4 — Verified MEMORY rule at HEAD.**
  No patch. Rule remains VERIFIED.

- **F-CW-5 — Regression tests.**
  New file `core/tests/test_celery_worker_lifecycle_validation_2728.py`:
  - Source-level guard: `settings.py` still sets `CELERY_WORKER_MAX_TASKS_PER_CHILD` (any value; the MEMORY rule rests on the config-scope, not the specific number).
  - Source-level guard: `Procfile` sets `--max-tasks-per-child=N` on every prefork celery-* line.
  - Source-level guard: `Makefile` `celery-recycle` target exists (after F-CW-1 patch (b)).
  - Source-level guard: `worker_process_init` signal handler registered in `core/celery.py` (after F-CW-2 patch).
  - Source-level guard: `make celery-status` checks all 5 workers (default, long_running, broadcast, pa, code_jobs) after F-CW-3 patch.
  - MEMORY rule reinforcement: settings.py still has broker URL at db 2 + result backend at db 3 (the MEMORY rule's `redis-cli -u redis://localhost:6379/2` recipe rests on db 2).

---

## Findings

### F-CW-1 — Local Makefile solo pool silently ignores recycle flags
- **Class:** DEFECT (D2 — silent-config; operators believe local workers recycle when they don't).
- **Evidence:** `Makefile:252, 263, 278, 289, 321` all set `--pool=solo`. `settings.py:864-865` sets `CELERY_WORKER_MAX_TASKS_PER_CHILD=50` and `CELERY_WORKER_MAX_MEMORY_PER_CHILD=300_000` which are prefork-only.
- **Severity:** MEDIUM — chronic-drift class hidden until a stall reproduces.
- **Action:** patch — Makefile comment (a) + `celery-recycle` target (b). Recommendation: (b).

### F-CW-2 — No worker_process_init / worker_process_shutdown signal handlers
- **Class:** DEFECT (D2 — silent recycle events on Railway).
- **Evidence:** grep of `core/` for signal handlers returned empty.
- **Severity:** MEDIUM — S1184-adjacent diagnostic gap.
- **Action:** patch — emit `[CELERY_WORKER_INIT]` + `[CELERY_WORKER_SHUTDOWN]` logs.

### F-CW-3 — `make celery-status` doesn't check pa or code_jobs workers
- **Class:** DEFECT (D2 — silent misdiagnosis; incomplete observability).
- **Evidence:** `Makefile:416-426` checks only default, long_running, broadcast. `make celery` starts pa + code_jobs but celery-status doesn't verify them.
- **Severity:** MEDIUM.
- **Action:** patch — add pa + code_jobs checks.

### F-CW-4 — MEMORY rule diagnostic sequence VERIFIED at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** all 6 steps reference files/paths that exist at HEAD.
- **Severity:** N/A.
- **Action:** none.

### F-CW-5 — Zero test coverage
- **Class:** DEFECT (D9).
- **Evidence:** grep of `core/tests/*.py` returned empty.
- **Severity:** MEDIUM.
- **Action:** patch — add regression tests.

---

## Verdict (Batch D tool 2 CLOSED)

- Tool status at close: **VERIFIED — DEFECT-PATCHED-VERIFIED.**
- Rigby-safe: **yes** post-patch across all three boundaries. Railway/production recycle contract was already verified-correct pre-patch. Local dev now has an explicit `make celery-recycle` target + header comment documenting the solo-pool implication (F-CW-1). Recycle events on Railway now grep-visible via `[CELERY_WORKER_INIT]` / `[CELERY_WORKER_SHUTDOWN]` (F-CW-2). `make celery-status` verifies all 5 workers `make celery` starts, with tail-log hints on the failure path (F-CW-3).
- Regression tests added: `core/tests/test_celery_worker_lifecycle_validation_2728.py` — 14 tests (3 F-CW-1 Makefile guards; 4 F-CW-2 signal handler guards; 3 F-CW-3 status completeness; 3 F-CW-4 MEMORY rule accuracy; 1 companion Procfile prefork discipline guard).
- Cross-tool regression: 272/272 substantive tests pass across all 17 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py` (Batches A + B + C + D tools 1-2). Zero regressions.
- Docs updated: Makefile header comment + celery-recycle target inline docstring + celery.py signal-handler docstrings.
- Migration files: none.
- Follow-ups filed: worker_recycled `CeleryTaskEvent` marker (extending F-CW-2 into the audit substrate) — deferred to combined batch-close observation list per Chris's earlier scope guidance.

### Patches shipped

| Finding | Class | Commit |
|---|---|---|
| F-CW-1 + F-CW-3 | Makefile celery-recycle target + celery-status completeness | `c8defcfa` |
| F-CW-2 | worker lifecycle signal handlers in core/celery.py | `80c18262` |
| tests | 14 regression tests | `958b4262` |

### MEMORY rules reinforcement (per campaign plan §12.4)

- `feedback_local_celery_stall_playbook`: **VERIFIED at HEAD post-patch** (F-CW-4). The 6-step diagnostic sequence still works because the underlying substrate (CeleryTaskEvent, Redis broker at db 2, prefork recycle config) is intact — but the surface itself is now easier to diagnose because `[CELERY_WORKER_INIT]` / `[CELERY_WORKER_SHUTDOWN]` logs make recycle events visible, and `make celery-recycle` gives operators a one-command discipline that doesn't require reading the MEMORY rule to know how to bounce workers cleanly.

### Design decision: solo-pool doc note vs pool switch

Chris's Option (b) was refactor + doc rather than switching local workers to prefork. Rationale:
- macOS SIGSEGV with prefork is well-known (see CLAUDE.md); switching is a regression class.
- Chronic-drift is easier to fix with an operator-callable recycle than with prefork machinery on macOS.
- The Makefile header comment makes the trade-off visible in-file, so future operators reading `celery` don't have to trace to settings.py to understand why recycle appears to be ignored.
