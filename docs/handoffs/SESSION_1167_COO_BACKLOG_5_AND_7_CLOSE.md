---
originating_session: 1167
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1167 handoff. Three PRs merged: one doc-only follow-on from the Session 1166 close (date-suffix nit Rigby flagged on 1167 entry) and two SHOULD-tier closures (COO Backlog items #5 and #7). Rigby ratified all designs pre-implementation in conv pa-f93d77e34f5d (health score 80 at session entry; thread carried for both design passes) and reviewed each PR post-PR-open. All three followed the Session 1165+1166 bypass-merge pattern: production-code PRs received explicit per-PR Chris auth in-session; doc-only PR followed the standing bypass protocol. Live PA-dispatch verification of ops_tool.top_consumers (PR #2306) executed post-restart through Rigby.
---

# Session 1167 — COO Backlog #5 + #7 close

**Date:** 2026-06-19 (UTC: 2026-06-20)
**Branch state at session close:** All work merged. Main is clean. Three PRs landed.

---

## TL;DR

Session 1167 closed both remaining SHOULD-tier items from Rigby's June 14 corrected v1 COO Nervous System Backlog:

- **Doc nit (caught on session entry):** the 00-START FIRST THING playbook used `date +%Y-%m-%d` (local) to locate today's `pa_acks_health` JSONL but the cadence task names files in UTC. At 01:15 UTC (19:15 MDT) the bracket pointed at the previous UTC day's file — a predictable false-positive for early-morning MT checks. Fixed in PR #2304 by switching to `date -u +%Y-%m-%d` in all four occurrences + a NOTE block explaining the convention.
- **COO Backlog item #5 (SHOULD: Memory telemetry + automatic downshift)** — closes the visibility gap between Procfile memory caps and the OOM kill. New canonical primitive `core/services/memory_telemetry.py` samples per-worker RSS via psutil, parses `--max-memory-per-child` from each worker's cmdline (no env-var injection), computes pct of cap, applies sustained-pressure semantics (>=80% for N=3 consecutive adjacent samples → CRIT), and emits a soft downshift signal. JSONL-as-state at `logs/worker_memory/YYYY-MM-DD.jsonl` (UTC). New PA tool action `ops_tool.memory_pressure`.
- **COO Backlog item #7 (SHOULD: Top Consumers ops endpoint)** — closes the "which task is using the most wall-clock" gap. New service `core/services/top_consumers.py` performs a single PostgreSQL aggregate query per call with `percentile_cont(0.95) WITHIN GROUP` (p95 server-side). New PA tool action `ops_tool.top_consumers`. Live smoke immediately surfaced `capture_pa_acks_health_snapshot` at p95=1880s and `monitor_celery_health` at p95=1048s as the top long-tail offenders — exactly the kind of finding this surface targets.

| PR | Theme | Merge SHA |
|---|---|---|
| **#2304** | `docs` — fix 00-START FIRST THING date suffix to UTC (4 occurrences) | `4e9e08af` |
| **#2305** | `feat` — **COO #5 (SHOULD):** worker memory telemetry + soft downshift signal | `d7f27218` |
| **#2306** | `feat` — **COO #7 (SHOULD):** top wall-clock consumers ops endpoint | `cc838c4e` |

**COO Backlog state after Session 1167:**

| Item | Tier | Status |
|---|---|---|
| #1 DB safety defaults | MUST | ✅ Session 1165 (#2295) |
| #2 Per-process Postgres `application_name` tagging | MUST | ✅ Session 1166 (#2301) |
| #3 Singleton locks + jitter | MUST | ✅ Session 1165 (#2296) |
| #5 Memory telemetry + automatic downshift | SHOULD | ✅ **Session 1167 (#2305)** |
| #6 Retry-storm prevention | MUST | ✅ Session 1165 (#2297) |
| #7 Top Consumers ops endpoint | SHOULD | ✅ **Session 1167 (#2306)** |
| #8 Queue depth + backlog age per queue | SHOULD | ✅ Session 1164 |

All 4 MUSTs and all 3 SHOULDs from Rigby's June 14 corrected v1 COO Backlog are now closed. **The backlog is complete.**

---

## What shipped

### PR #2304 — `date -u +%Y-%m-%d` fix in 00-START FIRST THING (docs nit)

**Discovery:** Session 1167 entry sanity checks ran the FIRST THING playbook. The playbook uses `date +%Y-%m-%d` (local) for the JSONL filename suffix, but `core/tasks.py:12741` writes filenames using Django `timezone.now().strftime('%Y-%m-%d')` which is UTC under `USE_TZ=True`. At 01:15 UTC (19:15 MDT) the playbook pointed at `logs/pa_acks_health/2026-06-19.jsonl` (yesterday UTC, pre-restart, lacking the new `escalated_triggers` field) while the writer was appending to `2026-06-20.jsonl` (today UTC, has the field).

**Fix:** all 4 `date +%Y-%m-%d` occurrences switched to `date -u +%Y-%m-%d` + a NOTE block under check (4) explaining why. Verifier-only change; no runtime behavior touched.

**Rigby's verdict (in-session, pre-PR):** doc-only fix, no runtime change. *"The kind of operator-paper-cut that will bite again, especially during early-morning MT checks."*

### PR #2305 — Worker memory telemetry + soft downshift signal (COO #5)

**Problem (Rigby's wording, COO Backlog §5):** Procfile caps memory per child (`--max-memory-per-child=150000` etc., kilobytes) — but we have NO visibility into how close we get to those caps before the kill fires. And no automatic concurrency downshift when a worker pool is consistently pressing the cap.

**Surface:**

- `core/services/memory_telemetry.py` (~370 lines) — canonical sampler. `build_snapshot()` reads `app.control.inspect().stats()` for per-host `pid` + `pool.processes` (child PIDs for prefork; `None` → parent for threads/solo). For each leaf PID samples `psutil.Process(pid).memory_info().rss`. Cap parsed from each parent's `psutil.Process(pid).cmdline()` searching for `--max-memory-per-child=<N>`. Dependency-injected (inspect_stats, previous_reports, psutil_module, now) for trivial testing.
- `core/management/commands/worker_memory_health.py` — read-only CLI mirroring `pa_acks_health` shape. `--json` flag for machine output; human summary by default.
- `core/tasks.py` — new `@shared_task capture_worker_memory_snapshot` wrapped in `@singleton_task("capture-worker-memory-snapshot", ttl=300)`. Writes `logs/worker_memory/YYYY-MM-DD.jsonl` (UTC). Emits WARN log on `overall_status != OK`. Cadence wrapper.
- `core/celery.py` — new beat schedule entry `worker-memory-capture` every 5 min on broadcast queue.
- `core/services/td_handlers_ops.py` — `_ops_memory_pressure` reads latest JSONL line. Reduce-from-source-of-truth pattern (Session 1164 rule); no re-classification.
- `core/services/pa_tool_schemas.py` — `memory_pressure` action registered in `ops_tool` enum + operator-natural description.
- `docs/topics/celery-workers.md` — new "Memory telemetry (Session 1167 — COO Backlog #5)" subsection.
- 4 new test files, 40 tests total, all `SimpleTestCase` (no DB).

**Sustained-pressure semantics (borrowed verbatim from pa_acks_health item C, Session 1166):**

- **WARN** on any single sample with `pct_of_cap_max >= 0.80`.
- **CRIT** when the same worker stays above 0.80 for **N=3 consecutive adjacent samples** (cadence 5min × adjacency factor 2 = 600s tolerance per pair).
- First-run / stale-prior cases default to non-sustained — never auto-escalate without evidence.
- `sustain_gating.escalated_triggers` records labels like `crit_persist_3samples:<host>` for greppable observability.

**Soft downshift signal (no auto-restart, no Procfile rewrites):**

- `downshift_recommended_global: bool` set when any worker is CRIT.
- `suggested_concurrency_by_worker: {host: int}` populated only for CRIT workers above the concurrency floor.
- `concurrency_floor=1` **universally**. Workers already at 1 in CRIT get a `recommended_action` to investigate the leak / raise `--max-memory-per-child` / split queues — no further downshift possible.

**Design tradeoffs resolved with Rigby:**

1. *Where does memory telemetry live?* JSONL-as-state (mirrors pa_acks_health), not a state-only surface. Rationale: time-series RSS samples handle better in JSONL; sustained-pressure trigger needs lookback the JSONL already provides via `read_previous_snapshot`. **Approved.**
2. *Downshift signal surface?* Separate `ops_tool.memory_pressure`, not folded into `overview`. Rationale: list-shaped per-worker data fights overview's reduce-and-summarize contract. **Approved with note** to add a small rollup indicator (`memory_pressure_state` GREEN/YELLOW/RED + top offender) to overview in a follow-on PR — deferred to keep PR #2305 focused.
3. *Soft vs hard throttle?* Soft, flag-only. Rationale: per Rigby's spec "the cap is the kill — this is observation + signal, not an auto-modifier." Hard auto-restart adds 3+ design questions (override storage, recovery, restart survival) not worth blocking observation on. **Approved.**
4. *Threshold?* Ship 80% / N=3 as strawman from spec; revisit with 24-72h of data per Rigby. **Approved.**
5. *Schema fields?* `schema_version: 1` top-level; `sustain_gating` carries `cadence_seconds` + `adjacency_window_seconds` + `consecutive_required` so future calibration / audit is painless. **Rigby additions.**

**PID discovery (the design risk Rigby flagged):** `app.control.inspect().stats()` returns per-host `pid` (parent) and `pool.processes` (child PIDs for prefork; `None` for threads/solo). Verified locally pre-coding: pa pool prefork-c1 returns `pool.processes=[27551]`; broadcast pool threads returns `pool.processes=None`. Resolution: `resolve_leaf_pids(parent, pool_processes)` → `pool_processes if non-empty else [parent_pid]`. No new env-var injection required.

**Cap parsing:** `psutil.Process(pid).cmdline()` returns the literal `--max-memory-per-child=200000` flag. Regex `--max-memory-per-child(?:=|\s+)(\d+)` handles both `--flag=value` and `--flag value` forms. Workers launched without the flag report `cap_bytes=None` → status stays OK regardless of pressure (correct degraded-mode behavior). This is exactly what happens locally — `make celery` doesn't pass the flag (Procfile/Honcho-only concept).

**Live smoke (post-restart, verbatim):** `python manage.py worker_memory_health` against running stack returned 4 workers with correct pool_kind classification (`prefork` for pa/default; `threads_or_solo` for broadcast/long_running), RSS reported in MB, `cap_bytes=null` on all (local degraded mode), status OK across the board (no false positives from null cap). Manual celery task fire at 21:05 MDT (02:05 UTC) wrote the first JSONL line at `logs/worker_memory/2026-06-20.jsonl` carrying schema_version=1 + cadence_seconds=300 + sustain_gating block.

### PR #2306 — Top wall-clock consumers ops endpoint (COO #7)

**Problem (Rigby's wording, COO Backlog §7):** No quick way to find "which task is using the most DB connections / CPU / wall-time in the last 1h / 24h."

**Surface:**

- `core/services/top_consumers.py` (~170 lines) — pure aggregator. `compute_top_consumers(window, limit, *, now=None)` performs a **single SQL aggregate query** against `core_celerytaskevent` using PostgreSQL `percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_seconds)` so p95 is computed server-side. Returns `count`, `total_seconds`, `mean_seconds`, `max_seconds`, `p95_seconds` per task_name, sorted by `total_seconds` desc.
- `core/services/td_handlers_ops.py` — `_ops_top_consumers` thin pass-through to `compute_top_consumers`. New `elif action == 'top_consumers'` branch in `_handle_ops`.
- `core/services/pa_tool_schemas.py` — `top_consumers` action registered in `ops_tool` enum + operator-natural description ("which task is eating workers / hogging wall-clock").
- 18 new tests (5 pure + 13 DB-backed via `TestCase` with transactional rollback).

**Vocabulary:**
- Window: `1h` / `6h` / `24h` / `7d` / `30d` (matches existing ops_tool convention); default `24h`.
- Limit: default 20, max 50 (matches `celery_task_history` convention).
- Schema `schema_version: 1` + UTC ISO `generated_at` + UTC ISO `since` + `window_seconds`.

**Design tradeoffs resolved with Rigby:**

1. *Top consumers of WHAT?* Wall-clock time (`duration_seconds`) as v1 primary metric. Rationale: operator-natural primary signal for "what's eating workers right now"; `CeleryTaskEvent.duration_seconds` already indexed on `(task_name, -started_at)`; zero new instrumentation. **Approved.** Out of scope (deferred to separate surfaces): LLM spend (lives in noise_metrics / cost_tool), DB queries (pg_stat_statements needs task↔query attribution), memory (covered by COO #5).
2. *Scope?* Per `task_name` only in v1. Agent dim deferred — `CeleryTaskEvent` has no `agent_name` field today; canonical `agents.AgentExecution` may have `celery_task_id` but that's a join exercise Rigby explicitly punted ("skip in v1 rather than inventing joins"). **Approved.**
3. *Windows + percentiles?* One window per call via `window` arg (default `24h`). Fields: `count` + `total_seconds` + `mean_seconds` + **`max_seconds`** (Rigby's add) + `p95_seconds`. **Approved.**
4. *p95 computation?* **PostgreSQL `percentile_cont(0.95) WITHIN GROUP` — server-side.** Rigby's hard requirement: "don't do aggregate query + Python-side p95 from per-task duration list unless you're also willing to do a second query to fetch durations." Single aggregate query, no N+1.
5. *Surface?* Separate `ops_tool.top_consumers` action, not folded into `overview`. Rationale: list-shaped data fights overview's reduce-and-summarize contract. **Approved.**

**Acceptance smoke (verbatim PA-dispatch results, post-restart, end-to-end through PA path):**

1h window, limit=5:
```
core.tasks.run_spider_network          count=2  total=149.7s  mean=74.9s  p95=142.2s  max=149.7s
core.tasks.process_pa_chat_task        count=7  total=72.7s   mean=10.4s  p95=13.8s   max=14.3s
intelligence.tasks.scan_spider_opps    count=2  total=70.4s   mean=35.2s  p95=66.9s   max=70.4s
core.tasks.run_heartbeat               count=7  total=22.4s   mean=3.2s   p95=3.4s    max=3.4s
core.tasks.check_celery_health         count=7  total=21.8s   mean=3.1s   p95=3.2s    max=3.2s
```

24h window, top 5 (10 returned):
```
core.tasks.capture_pa_acks_health_snapshot   count=50   total=29128s  p95=1880s  max=2126s
core.tasks.check_celery_health               count=105  total=20279s  p95=971s   max=1044s
core.tasks.run_heartbeat                     count=205  total=17790s  p95=931s   max=1047s
core.tasks.run_spider_network                count=167  total=16271s  p95=144s   max=1186s
core.tasks.monitor_celery_health             count=48   total=5476s   p95=1048s  max=1316s
```

The signal is immediately actionable. `capture_pa_acks_health_snapshot` at p95=1880s = 31 minutes — exactly the Session 1165 carryover slow-task investigation surfaced concretely.

---

## Behavioral invariants — what's now true post-merge

These are the contracts the rest of the codebase can rely on after Session 1167:

1. **`logs/worker_memory/YYYY-MM-DD.jsonl` exists from the next `*/5` UTC mark forward** (cadence task on broadcast queue). UTC-dated filename.
2. **Every JSONL line carries `schema_version: 1`** + `sustain_gating` block including `cadence_seconds`, `adjacency_window_seconds`, `consecutive_required`. Calibration tooling can read these constants from the data itself.
3. **`ops_tool.memory_pressure` reads the latest JSONL line and returns the projected snapshot** — never re-samples, never re-classifies. Single source of truth is the cadence task.
4. **`build_snapshot()` is dependency-injectable** (inspect_stats, previous_reports, psutil_module, now). Tests don't hit the celery broker or filesystem.
5. **`compute_top_consumers(window, limit)` returns at most `MAX_LIMIT=50` rows** via a single PostgreSQL aggregate query — no N+1 risk regardless of event volume.
6. **`ops_tool.top_consumers` accepts the standard ops_tool window vocabulary** (`1h`/`6h`/`24h`/`7d`/`30d`). Unknown windows surface as `{"error": "Unknown window 'X'. Valid: [...]"}`, not 500.
7. **Workers launched without `--max-memory-per-child` (e.g. `make celery` locally) report `cap_bytes=None` and status `OK` regardless of RSS.** Correct degraded-mode behavior — false positives are not possible from cap-absent rows.
8. **The 00-START FIRST THING playbook commands point at the UTC-named JSONL.** Operator-facing checks at any local time will land on the correct file.

---

## Rollback levers (per change)

If Session 1168 surfaces a regression, here's how to roll each piece back without redeploying:

| Change | Soften / disable lever |
|---|---|
| `worker-memory-capture` beat task firing | Disable the PeriodicTask row: `python manage.py shell` → `PeriodicTask.objects.filter(name='worker-memory-capture').update(enabled=False)`. Beat picks up the change within its poll interval (no restart). |
| `capture_worker_memory_snapshot` runs but is too slow | Cadence is 5 min (`crontab(minute='*/5')`). Bump to `*/15` by editing the PeriodicTask's crontab via the Django admin or shell, or set the row to `enabled=False` outright. |
| Sustained-pressure threshold too aggressive (false CRITs) | Bump `PRESSURE_THRESHOLD = 0.80` in `core/services/memory_telemetry.py:62` to `0.90` and restart workers. Or raise `CONSECUTIVE_REQUIRED = 3` to `5`. |
| `ops_tool.memory_pressure` returning misleading data | Remove from `pa_tool_schemas.py` action enum (no-op behavior remains in handler but PA stops dispatching). |
| `ops_tool.top_consumers` SQL too slow on prod-scale data | The `core_celerytaskevent.celery_evt_name_time` index on `(task_name, -started_at)` covers the GROUP BY. If still slow, drop `MAX_LIMIT` from 50 to 20 in `core/services/top_consumers.py:60`. Last resort: remove the action from `pa_tool_schemas.py` enum. |
| `percentile_cont` portability concern (e.g. moving off PG) | The SQL is in one place (`top_consumers.py:113-127`). Swap to a Python-side percentile from a bounded sample if ever needed. Not relevant under current PostgreSQL stack. |
| Lock-key naming collisions with `@singleton_task` | Lock name is `capture-worker-memory-snapshot` (TTL 300s). No collision with `capture-pa-acks-health-snapshot` (Session 1165 lock). Both use the canonical `singleton_lock:<name>` prefix. |

---

## 24-hour watch checklist

Specific commands operators can paste during the AM check tomorrow:

```bash
# (1) Confirm worker-memory-capture cadence has been firing
wc -l logs/worker_memory/$(date -u +%Y-%m-%d).jsonl
# Expect: ~288 lines/day at */5 cadence. First-day expectation lower
# (started mid-day); look for steady accrual.

# (2) Sample the most-recent line — schema validation
tail -1 logs/worker_memory/$(date -u +%Y-%m-%d).jsonl | python -m json.tool | head -30
# Expect: schema_version=1, cadence_seconds=300, sustain_gating block
# with all 5 fields (previous_adjacent, cadence_seconds,
# adjacency_window_seconds, consecutive_required, gated_triggers, escalated_triggers).

# (3) Tally any sustained CRIT escalations
grep -o '"escalated_triggers":\[[^]]*\]' logs/worker_memory/$(date -u +%Y-%m-%d).jsonl | sort | uniq -c | sort -rn
# Expect: bulk empty lists. Any non-empty list = a real downshift-recommendation
# event worth investigating per the Session 1167 design notes.

# (4) Confirm overall_status distribution
.venv/bin/python -c "
import json, collections
c = collections.Counter()
for line in open('logs/worker_memory/$(date -u +%Y-%m-%d).jsonl'):
    c[json.loads(line).get('overall_status')] += 1
print(dict(c))
"
# Expect: bulk OK. Any WARN/CRIT = the sustained-pressure surface working
# as designed; investigate per the recommended_actions field on those lines.

# (5) Smoke ops_tool.memory_pressure through PA dispatch
./tools/pa_local.sh "Call ops_tool memory_pressure action and show me the overall_status + worker_count + downshift_recommended."

# (6) Smoke ops_tool.top_consumers through PA dispatch
./tools/pa_local.sh "Call ops_tool top_consumers with window=24h limit=10. Highlight any task with p95_seconds > 600."

# (7) Verify the percentile_cont SQL stays bounded
.venv/bin/python manage.py dbshell -- -c "
EXPLAIN ANALYZE
SELECT task_name, percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_seconds)
FROM core_celerytaskevent
WHERE started_at >= now() - interval '24 hours'
  AND duration_seconds IS NOT NULL
GROUP BY task_name ORDER BY 2 DESC LIMIT 20;"
# Expect: index scan on celery_evt_name_time, total time < 50ms at current scale.
# If sequential scan or > 500ms, file a perf ticket.
```

---

## New persistent artifacts

- **Code:**
  - `core/services/memory_telemetry.py` — canonical sampler + sustain semantics + status compute. ~370 lines.
  - `core/services/top_consumers.py` — per-task_name aggregator with server-side p95. ~170 lines.
  - `core/management/commands/worker_memory_health.py` — read-only CLI (`--json` flag).
  - `core/tasks.py: capture_worker_memory_snapshot` — singleton-locked cadence task.
- **Tests:**
  - `core/tests/test_memory_telemetry.py` (29 tests, SimpleTestCase)
  - `core/tests/test_worker_memory_health_command.py` (3 tests, SimpleTestCase)
  - `core/tests/test_capture_worker_memory_snapshot.py` (4 tests, SimpleTestCase)
  - `core/tests/test_ops_memory_pressure_action.py` (4 tests, SimpleTestCase)
  - `core/tests/test_top_consumers.py` (18 tests; 5 SimpleTestCase + 13 TestCase)
- **PA tool surface:**
  - `ops_tool.memory_pressure` action — reads `logs/worker_memory/*.jsonl`
  - `ops_tool.top_consumers` action — reads `core_celerytaskevent`
- **Beat schedule:**
  - `worker-memory-capture` — every 5 min on broadcast queue
- **Logs / state:**
  - `logs/worker_memory/YYYY-MM-DD.jsonl` (UTC-dated, gitignored under `logs/`)
- **Docs:**
  - `docs/topics/celery-workers.md` — new "Memory telemetry" subsection under "Observability"

---

## New feedback memories captured this session

None — both designs followed established Session 1164/1165/1166 patterns (JSONL-as-state + factory-style probes + reduce-from-source-of-truth + primitives + opt-in apply list + backward-compatible signatures + UTC-canonical timestamps in payloads). The 00-START playbook gotcha (local-vs-UTC date) was a one-off paper cut, not a new feedback class.

---

## Carryover into Session 1168

### Direct follow-ons from Session 1167

1. **`memory_pressure_state` rollup indicator on `ops_tool.overview`.** Small extension: GREEN/YELLOW/RED + top-offender + %cap. Defer-approved by Rigby in the PR #2305 design pass.
2. **`cap_coverage_pct` field on `ops_tool.memory_pressure` rollup.** Rigby's last-minute addition request — surface the fraction of sampled workers that actually have a parseable `--max-memory-per-child` cap. Saves an operator hunt for "is the sampler seeing prod caps." 4 lines.
3. **Operator playbook snippet: "If a monitor task is in top_consumers, treat it as P1 reliability debt."** Rigby's standing follow-up to the PR #2306 live smoke finding (`monitor_celery_health` p95=1048s).
4. **Targeted remediation for `monitor_celery_health` and `capture_pa_acks_health_snapshot`** — both flagged by the live PR #2306 smoke. p95 of 17.5 min and 31 min respectively for what are supposed to be "snapshot/monitor" workloads. Queue placement + timeouts + probe decomposition per Rigby. Aligns with the pre-existing Session 1165 carryover.
5. **Agent dim on `CeleryTaskEvent`.** Single migration + signal-handler tweak to add `agent_name` to the event row. Then a `top_consumers` variant that aggregates by agent_name. Deferred from Session 1167 per Rigby's "skip in v1 rather than inventing joins" rule.

### Carryover from Session 1165 (still queued)

- Operator_edge lock consolidation (`core/tasks_content.py:4216` + 6 release sites).
- `_circuit_breaker_check` step-3 lock consolidation.
- Agent-task family retry budgets (needs fingerprinting strategy).
- Bulk migration of ~5 linear/fixed countdown sites in `core/tasks_agents.py` family.

### Carryover from Sessions 1165/1166 (aspirational)

- `pg_stat_statements` on staging/prod (installed locally Session 1165).
- `capture_pa_acks_health_snapshot` slow-task investigation — top of `ops_tool.top_consumers` 24h now (p95=1880s). Concrete data exists.

### Standing infrastructure track (deferred during CI outage)

- `celery-beat-schedule` CONFLICT detector tuning.
- Pre-existing PeriodicTask drift.
- `exists_on_disk: false` flag in `_provenance.json` (326 dead paths).
- Beat-schedule the regens (weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands).
- Fix `build_learning_bridge_audit.py` generator (falsely flags "ABC unused").
- Redis pooling sweep (~40 inline `redis.Redis.from_url(...)` sites).

### Chris-call-only (still parked)

- Decision Command backend cleanup (5 Python files, regressed feature).
- DaVinci route removal (`core/views_davinci.py` still routed).
- Mission refresh PR #2190 (preserved branch).

---

## Active issues carried forward

### GitHub Actions billing — still down

Multi-day outage carried from Sessions 1149-1166. Bypass-merge protocol unchanged from Session 1166:

- Local guardrails run pre-push (`scripts/verify_repo_guardrails.py --inventory-advisory` + `tools/check_direct_llm_calls.py --warn-only`).
- Only acceptable pre-existing failure: `celery-beat-schedule` CONFLICT (detector heuristic, code-level footgun closed Session 1157 PR #2243).
- Doc-only PRs: no per-PR Chris auth needed.
- Production-code PRs: explicit per-PR Chris auth in-session (Session 1167 PRs #2305 + #2306 both received auth verbatim from Chris before code was written).

### COO Nervous System Backlog — CLOSED

All 4 MUSTs (#1, #2, #3, #6) and all 3 SHOULDs (#5, #7, #8) closed across Sessions 1164-1167. No items remain in the corrected v1 backlog.

---

## Process notes

- **Conversation continuity:** Single PA conversation `pa-f93d77e34f5d` carried both design passes (COO #5 + #7) plus the docs nit. Rigby's session-entry health check returned score 80/100 with recommendation `continue` — the design-pass workload stayed coherent. Implementation execution restart point was deferred to Session 1168 entry; thread still valid at session close.
- **Live smoke as design validation:** PR #2306's smoke against real CeleryTaskEvent immediately surfaced two long-tail offenders Rigby + operator-side suspicions already named (`monitor_celery_health`, `capture_pa_acks_health_snapshot`). Validates that the metric + window pick was right; we didn't have to wait 24h to see whether the surface is useful.
- **Worker restart discipline:** Per Sessions 1161-1162 memory rule, restarted workers after PR #2305 AND again after PR #2306 (the new `_ops_top_consumers` method on `OpsHandlersMixin` is imported by the task body of `process_pa_chat_task`, so `sys.modules` cache would otherwise hold the old class). End-to-end PA dispatch verified post-second-restart.
- **Operational handoff sections:** Per Rigby's Session 1165 close-out review, this handoff includes (1) behavioral invariants, (2) rollback levers per change, (3) 24h watch checklist with copy-paste commands. Aligns with the operational-handoff pattern that emerged after the triple-MUST close.
