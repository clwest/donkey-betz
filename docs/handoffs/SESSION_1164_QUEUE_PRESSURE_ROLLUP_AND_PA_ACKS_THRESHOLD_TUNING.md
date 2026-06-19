---
originating_session: 1164
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1164 handoff. Three PRs merged in one session, closing the queue-pressure rollup work that started with #2289 (cockpit telemetry) in the prior session and the pa_acks_health threshold tuning that Session 1162 staged via the observation cadence. Rigby ratified the design at four checkpoints (pre-implementation spec for ops rollup; pre-merge for #2291 thresholds; pre-merge for #2292 sustain observability; post-merge verification). Session also surfaced a substantive scoreboard against Rigby's June 14 corrected v1 COO backlog — Session 1164 closed item #8 (SHOULD); items #1, #3, #5, #6, #7 (4 MUSTs + 1 SHOULD) remain open.
---

# Session 1164 — queue_pressure rollup + pa_acks_health threshold tuning

**Date:** 2026-06-19
**Branch state at session close:** All work merged. Main is clean. Three PRs landed.

---

## TL;DR

Session 1164 ran a clean end-to-end arc on the queue-pressure observability surface that #2289 opened in the prior session. Three PRs landed:

- **#2290** wired a queue_pressure rollup into `ops_tool.overview` — single source of truth preserved via `_handle_cockpit` proxy; no re-classification.
- **#2291** raised the pa_acks_health `_WARN_QUEUE_DEPTH` floor (1 → 5) and added a sustain-window gate so transient single-snapshot infra dips (zero workers, depth>=CRIT) no longer flip CRIT/WARN.
- **#2292** added time-adjacency to the sustain gate (stale previous snapshot ≠ "consecutive") and recorded sustain decisions on every snapshot via a new `sustain_gating` block.

The arc closed Rigby's June 14 corrected-v1 COO backlog item **#8 (SHOULD: Queue depth + backlog age per queue)** end-to-end. Workers restarted post-#2292 so the 30-min cadence task writes the new schema going forward — item C (WARN persists 2 snapshots → escalate to CRIT) becomes evaluable in Session 1165 once ~24h of new-schema JSONL accumulates.

The three PRs:

| PR | Theme | Merge SHA |
|---|---|---|
| **#2290** | `queue_pressure` rollup in `ops_tool.overview` — calls `cockpit_tool.queue_lengths` and reduces (no re-classification) | `e69aa5cf` |
| **#2291** | `_WARN_QUEUE_DEPTH` raised 1 → 5 + sustain-window for binary infra triggers (no_workers, depth_crit) | `0951222f` |
| **#2292** | Time-adjacency check + `sustain_gating` observability field on every snapshot | `420ae6d7` |

---

## What shipped

### PR #2290 — queue_pressure rollup in ops_tool.overview

**Surface:** New `_ops_queue_pressure_rollup(user_id, trace_id)` in `core/services/td_handlers_ops.py`. Called from `_handle_ops` overview block between `slo_status` and `failure_signatures` per Rigby's ordering spec.

**Shape:**

```json
"queue_pressure": {
  "overall_state": "CRITICAL",
  "queues_critical_count": 2,
  "queues_red_count": 0,
  "top_offenders": [
    {"queue": "long_running", "state": "CRITICAL", "depth": 964, "oldest_age_seconds": null, "reasons": ["depth>=500", "age_unknown"]},
    {"queue": "ml",           "state": "CRITICAL", "depth": 814, "oldest_age_seconds": null, "reasons": ["depth>=500", "age_unknown"]}
  ],
  "generated_at": "2026-06-19T21:32:53.522132+00:00"
}
```

**Design contract:**
- Calls `_handle_cockpit('cockpit_tool', {'action': 'queue_lengths'}, ...)` and **reduces**. Never re-classifies. Thresholds remain single-source-of-truth inside cockpit's `_classify`.
- Severity histogram (`queues_critical_count` / `queues_red_count`) computed from passthrough states.
- `top_offenders` sorted severity → depth → oldest_age, capped at 3 (Rigby ratified the cap).
- `redis_error` propagates from cockpit when present (degraded-but-usable surfaces an answer rather than going UNKNOWN).
- Explicit `{"overall_state": "UNKNOWN", "error": "..."}` block on any exception. `ops_tool.overview` never fails open.

**Live smoke at merge time:** real CRITICAL data with `long_running` depth=964 + `ml` depth=814 returned — matched cockpit one-for-one.

**Test coverage:** `core/tests/test_ops_queue_pressure_rollup.py` — 8 tests mocking the cockpit return: no-reclassification passthrough, severity counts, sort+3-cap, GREEN-exclusion, redis_error passthrough, cockpit-failure UNKNOWN, cockpit-non-dict UNKNOWN, ISO-8601 timestamp.

### PR #2291 — pa_acks_health threshold tuning A + B

**Surface:** `core/management/commands/pa_acks_health.py` — `_compute_status` extended with optional `previous_report` parameter; new `_read_previous_snapshot()` reader tailing the most recent JSONL line.

**Data behind the tuning** (last 7d × 331 snapshots from `logs/pa_acks_health/*.jsonl`):
- PA queue depth: **always 0** (p50=p90=p95=p99=0).
- Status mix: 96.4% OK / 3.6% CRIT / **0% WARN**.
- All 12 CRIT events fired on `failures >= 3` (single trigger).
- 0 hangs across 7d; worker count never zero.

**Change A — `_WARN_QUEUE_DEPTH` 1 → 5:** A single stray queued message no longer flips WARN. The depth=1 cutoff was dead code in observed data; raising the floor is preemptive — when depth stops being 0, a single message should not page.

**Change B — sustain-window for binary infra triggers:** Triggers gated on "both current AND previous snapshot trip":
- `worker_count == 0` (was: single-snapshot WARN + CRIT)
- `depth >= _CRIT_QUEUE_DEPTH` (was: single-snapshot CRIT)

Failure and hang triggers **stay single-snapshot** — spikes are spiky; sustain would mask the 12/12 real CRITs we already see. `previous_report=None` (first ever run or missing JSONL) defaults sustain to never-fire.

**Sustain-state source:** `_read_previous_snapshot()` tail-reads the most recent JSONL line (capped 64 KiB scan, returns None on any I/O / parse error). JSONL chosen over Redis per Rigby — deterministic, auditable, no new dependency injected into the very signal we're stabilizing.

**Truth table** (bolded rows = behavior change):

| Scenario | Old status | New status |
|---|---|---|
| Single queued msg (depth=1) | **WARN** | **OK** |
| Backlog forming (depth=5) | WARN | WARN |
| Real backlog single snapshot (depth=25, healthy prev) | **CRIT** | **WARN** |
| Real backlog sustained | CRIT | CRIT |
| Worker dip transient (healthy prev) | **CRIT** | **OK** |
| Worker dip sustained | CRIT | CRIT |
| Failure spike (>=3) | CRIT | CRIT |
| Hang spike (>=3) | CRIT | CRIT |
| Long hang (>=180s) | CRIT | CRIT |

**Test coverage:** `core/tests/test_pa_acks_health_thresholds.py` — 19 tests covering depth raise (4 cases), no_workers sustain (3 cases), depth_crit sustain (3 cases), single-snapshot triggers preserved (4 cases), sustain-gate correctness (3 cases including helpers), failure+depth interactions (2 cases).

### PR #2292 — time-adjacency + sustain observability

**Surface:** Two follow-on adds closing Rigby's pre-merge nits on #2291.

**Time adjacency:**
- New constants `_EXPECTED_INTERVAL_SECONDS = 1800` + `_SUSTAIN_ADJACENCY_FACTOR = 2`.
- New `_is_previous_adjacent(report, previous_report)` returns True iff both reports carry `generated_at` AND delta is in `[0, expected*factor]`. Negative delta (clock skew) and malformed timestamps return False.
- `_compute_status` consults adjacency before using the previous snapshot. **A stale previous from a long scheduler pause no longer falsely counts as consecutive.**

**Sustain observability:** Every snapshot now carries a `sustain_gating` block:

```json
"sustain_gating": {
  "previous_adjacent": true,
  "expected_interval_seconds": 1800,
  "adjacency_factor": 2,
  "gated_triggers": []
}
```

`gated_triggers` lists sustain-eligible triggers that **fired this snapshot but were blocked** by the sustain check. Additive + backwards-compatible; older JSONL lines without the field stay readable.

**Live smoke at merge time** (post-restart, manually fired cadence task):

```
status: OK
sustain_gating:
  previous_adjacent: True
  expected_interval_seconds: 1800
  adjacency_factor: 2
  gated_triggers: []
```

**Test coverage:** extended `test_pa_acks_health_thresholds.py` from 19 → 36 tests. New cases: adjacency window (30 min / 60 min boundary / 65 min stale / future / missing / malformed timestamp), observability (field present on every report; empty gated_triggers when nothing tripped; no_workers gated on first run; depth_crit gated on first run; both can be gated simultaneously; constants recorded), `_is_previous_adjacent` helper unit tests.

---

## Coverage gaps closed

1. **Queue pressure visible in `ops_tool.overview`.** Operators no longer need to drill into cockpit to see system-level queue health.
2. **pa_acks_health no longer noisy on transient infra dips.** Single-snapshot zero-workers or depth>=20 from a healthy state stays OK; only sustained dips escalate.
3. **Stale previous snapshot defense.** Scheduler pause + restart no longer falsely triggers CRIT on the first post-restart snapshot.
4. **Sustain-decision provenance recorded on the snapshot.** Item C threshold tuning (WARN persists 2 snapshots → CRIT) now has explicit adjacency evidence to work from.

---

## New persistent artifacts

- `core/services/td_handlers_ops.py:_ops_queue_pressure_rollup` — reducer for cockpit queue_lengths.
- `core/management/commands/pa_acks_health.py`:
  - `_WARN_QUEUE_DEPTH = 5` (raised from 1).
  - `_EXPECTED_INTERVAL_SECONDS = 1800` + `_SUSTAIN_ADJACENCY_FACTOR = 2` class constants.
  - `_is_previous_adjacent(report, previous_report)` classmethod.
  - `_trips_no_workers(report)` + `_trips_depth_crit(report)` probe helpers.
  - `_read_previous_snapshot()` JSONL tail-reader.
  - `_compute_status(report, previous_report=None)` extended signature.
  - `sustain_gating` block on every emitted report.
- `core/tests/test_ops_queue_pressure_rollup.py` (8 tests).
- `core/tests/test_pa_acks_health_thresholds.py` (36 tests).

No new models, migrations, or beat schedule entries this session.

---

## Carryover for Session 1165

### Now actionable (24h+ post #2292 deploy)

- **Item C — WARN persists 2 consecutive snapshots → escalate to CRIT.** Rigby's spec: wait for at least a day of telemetry on the new code so threshold tuning has explicit adjacency evidence. The `sustain_gating` field landed via #2292; once the cadence task has written ~48 ticks on the new schema, item C becomes evaluable from JSONL.

### COO Nervous System Backlog status (Rigby's June 14 corrected v1)

Source deliverable: `1be2cf55-2ece-4ffa-8c2b-27b777ee54c7` (workspace chris-personal `33aa1e08-5ed7-480e-b59f-f28ad863e295`).

| # | Item | Tier | Status |
|---|---|---|---|
| 1 | DB safety defaults (statement_timeout, idle_in_tx, conn hygiene) | MUST | OPEN |
| 2 | application_name tagging (per service/queue/worker) | MUST | PARTIAL (global tag only) |
| 3 | Periodic-task stampede prevention (singleton locks + jitter) | MUST | OPEN |
| 4 | Prefetch + acks_late normalization | MUST | DONE (Session 984 + Session 1159) |
| 5 | Memory telemetry + automatic downshift | MUST | OPEN |
| 6 | Retry-storm prevention (exp backoff + retry budgets) | MUST | OPEN |
| 7 | "Top Consumers" ops endpoint | SHOULD | OPEN |
| 8 | Queue depth + backlog age per queue | SHOULD | **DONE (Session 1164)** |
| 9 | Tool-call telemetry rollup | LATER | PARTIAL (task exists; rollup quality unverified) |
| 10 | Execution receipts | LATER | OPEN |

**Net:** 2 done, 2 partial, 6 open. Live order for Session 1165 (skipping done items): **#1 → #3 → #2 → #6 → #5 → #7 → #9 → #10**.

### Recommended Session 1165 entry

**Item #1 — DB safety defaults + task-boundary connection hygiene.**

Why first: lowest LOC, highest reliability impact, no observability gap to overcome before shipping. The DB exhaustion mode is what surfaces every other tier of governor failure; closing it lifts the floor for everything below.

Scope sketch:
- `core/settings.py` — add `'options': '-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000'` (or equivalent) to `DATABASES['default']['OPTIONS']`. Numbers chosen by acceptance criteria, not Vibes; verify against current pg_stat_activity p95.
- `core/tasks.py` or `core/celery.py` — task-boundary `close_old_connections()` hook so long-running workers don't accumulate idle connections across the `CONN_MAX_AGE=60` window.
- Acceptance criteria (Rigby's wording): slow queries terminated; no idle-in-tx linger; connection counts don't climb under bursts.

Verify locally:
1. Run a deliberately slow query via Django shell, confirm it terminates at the timeout.
2. Burst-enqueue 100+ short tasks, monitor `pg_stat_activity` connection count stays flat.
3. Confirm no regression: run the existing pa_acks_health snapshot — status OK, queue depth 0.

---

## Cross-session lessons

- **Source-of-truth discipline holds.** PR #2290 explicitly reduces cockpit output rather than re-classifying. The cost of duplicating thresholds in `ops_tool.overview` would have been zero today and unbounded tomorrow when someone tuned cockpit and forgot ops.
- **JSONL-as-state is the right substrate for low-frequency observability.** Sustain semantics needed prior state; JSONL already had it; introducing Redis state for a 30-min cadence task would have added a dependency to the very signal we're stabilizing. Rigby explicitly chose this trade.
- **Observability fields belong on the same artifact as the decision.** PR #2292 puts `sustain_gating` on every snapshot rather than in a separate audit log. Downstream tuning (item C) can read one file; ops dashboards see decision context next to outcome.
- **Distribution-first tuning beats vibes.** PR #2291 changed `_WARN_QUEUE_DEPTH` only after observing 331 consecutive snapshots at depth=0. The number (5) is still preemptive — but the *direction* (raise, not lower) was data-validated. Trying to tune `failures >= 3` without observing the 12 real CRIT events would have weakened the only signal doing work.
- **Pre-merge nit-as-spec is a useful pattern.** Rigby's two pre-merge nits on #2291 (log-tail order, time adjacency) split cleanly: one was already correct (lex == chrono for date-prefixed names), one became #2292's scope. The nit format made the boundary easy to draw.

---

## Coverage gaps NOT closed (surfaced for Session 1165+)

- Items #1, #3, #5, #6 are MUST-tier open items in Rigby's corrected v1 backlog. The COO Operator Report frames these as Tier 0 nervous-system work because they enable every other control. Sessions 1165+ should land them in the order above.
- Item #7 (Top Consumers ops endpoint) is a SHOULD that pairs naturally with item #4 (now done): the queue-pressure surface from this session could be folded into a broader ops snapshot rather than living as its own gateway action.
- Items #9 (tool-call telemetry rollup) + #10 (execution receipts) are LATER-tier; queue once MUSTs are closed.

---

## Verification at session close

- `git log --oneline origin/main -5` confirms three PRs landed (`420ae6d7` → `0951222f` → `e69aa5cf`).
- `python manage.py pa_acks_health --json` returns `status: OK` with `sustain_gating` block populated.
- Celery: 5 workers + beat restarted post-#2292; `.celery*.pid` files written; new code loaded in worker `sys.modules` (verified by manually firing `capture_pa_acks_health_snapshot` and confirming the new field landed in `2026-06-19.jsonl`).
- 8 + 36 = 44 unit tests pass; all CI mirrors clean except the pre-existing `celery-beat-schedule` CONFLICT signal (Session 1157 footgun closed; detector heuristic remains).
