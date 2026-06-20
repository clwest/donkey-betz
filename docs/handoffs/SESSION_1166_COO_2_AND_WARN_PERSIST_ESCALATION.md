---
originating_session: 1166
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1166 handoff. Two PRs merged closing two distinct lines of work — COO Backlog item #2 (the last open MUST from Rigby's June 14 corrected v1) and pa_acks_health item C (the WARN-persist → CRIT escalation Session 1164 deferred until ≥24h of new-schema telemetry existed). Rigby ratified both designs pre-implementation (Path A vs B for application_name tagging; per-sub-trigger semantics + factory-style probe re-evaluation for item C) and reviewed each PR post-PR-open. Both PRs followed the Session 1165 close-out pattern: production-code bypass merge under the GitHub Actions billing outage, explicit per-PR Chris auth received in-session.
---

# Session 1166 — COO #2 + pa_acks_health item C

**Date:** 2026-06-19
**Branch state at session close:** All work merged. Main is clean. Two PRs landed (plus one doc-only follow-on commit).

---

## TL;DR

Session 1166 closed two distinct work-streams in a clean two-PR arc:

- **COO Backlog item #2 (MUST: per-process Postgres `application_name` tagging)** — the smallest and last MUST from Rigby's June 14 corrected v1 backlog. `pg_stat_activity` now shows per-component breakdown (`dbz:web`, `dbz:celery-pa`, `dbz:celery-broadcast`, `dbz:celery-long-running`, `dbz:celery-worker`, `dbz:celery-beat`) instead of one undifferentiated `unified_donkey_betz` bucket. Verifier added.
- **pa_acks_health item C (WARN persists 2 snapshots → CRIT escalation)** — the Session 1164 deferred item. Now actionable with 49+ lines of new-schema JSONL telemetry post-#2292. Per-sub-trigger semantics (hang↔hang, failures↔failures, depth↔depth); `no_workers` excluded because it already has its own sustain machinery.

| PR | Theme | Merge SHA |
|---|---|---|
| **#2301** | `feat` — **COO #2 (MUST):** per-process Postgres `application_name` tagging (`PG_APPLICATION_NAME=dbz:<role>` env var + 11 Procfile entries + Makefile + verifier) | `512c7922` |
| **#2302** | `feat` — pa_acks_health **item C:** WARN-persist 2 snapshots → CRIT escalation (3 new factory-style probes + `sustain_gating.escalated_triggers` field + 15 new truth-table tests) | `47de895c` |

**COO Backlog state after Session 1166:**

| Item | Tier | Status |
|---|---|---|
| #1 DB safety defaults | MUST | ✅ Session 1165 (#2295) |
| #2 Per-process Postgres `application_name` tagging | MUST | ✅ **Session 1166 (#2301)** |
| #3 Singleton locks + jitter | MUST | ✅ Session 1165 (#2296) |
| #5 Memory telemetry + automatic downshift | SHOULD | 🟡 Open — Session 1167 entry candidate |
| #6 Retry-storm prevention | MUST | ✅ Session 1165 (#2297) |
| #7 Top Consumers ops endpoint | SHOULD | 🟡 Open — pairs with queue_pressure surface |
| #8 Queue depth + backlog age per queue | SHOULD | ✅ Closed Session 1164 |

All 4 MUSTs from Rigby's June 14 corrected v1 are now closed. Only SHOULD-tier items remain in the COO Backlog.

---

## What shipped

### PR #2301 — Per-process Postgres `application_name` tagging (COO #2)

**Problem (Rigby's wording, COO Backlog §2):** Currently only the global `'unified_donkey_betz'` value. Operator can't see which service / queue / worker holds which connection in `pg_stat_activity`.

**Surface:**

- `core/settings.py:283` — `DATABASES['default']['OPTIONS']['application_name']` reads `os.environ.get('PG_APPLICATION_NAME', 'unified_donkey_betz')`. Default preserved for ad-hoc shells and one-off `python manage.py` invocations that don't set the env var.
- `Procfile` — all 11 entries prefixed with `PG_APPLICATION_NAME=dbz:<role>`. `release` entry wrapped in `sh -c "..."` to scope the env var across its chained `migrate` / `sync_celery_beat` / `sync_task_queues` / `setup_codebase_workspace` / `setup_pa_service_account` commands. `resolve-node` tagged uniformly even though it doesn't hit the unified_donkey_betz PG in practice — keeps the verifier free of special-case opt-outs.
- `Makefile` — `start` target's daphne launch tagged `dbz:web`; `celery` target's 4 worker commands + beat tagged to match their Procfile cousins. Local default worker serves `default,agents,content` (vs prod `celery-worker` which serves `default,agents,sports`) — same tag per Rigby's verdict ("application_name should answer what process class is this, not what queue mix this run is configured for").
- `scripts/verify_repo_guardrails.py` — two new checks. **Procfile coverage is strict** and blocks strict mode if any entry lacks `PG_APPLICATION_NAME=dbz:<role>` matching `^dbz:[a-z0-9\-]+$`. **Makefile coverage is advisory only** because local dev workflows vary. Handles backslash continuations so an env block on a preceding shell line counts as covering the call on the next.
- `tests/test_verify_repo_guardrails.py` — 11 new tests across two new classes covering both `classify_*` functions + the new `procfile_tag_blocking` branch of `classify_failures`. 30/30 verifier tests pass.
- `docs/topics/infrastructure.md` (follow-on commit `abdd52d4`) — "Postgres application_name tagging" subsection under Database Notes documenting the env var, format, verification query, lazy-bind note for the PA worker tag.

**Tag scheme:** `dbz:<procfile-entry-name>`. Locked with Rigby pre-implementation. Verifier regex `^dbz:[a-z0-9\-]+$` enforces lowercase + digits + hyphens only.

**Acceptance smoke (post-restart, verbatim Rigby acceptance criteria):**

```sql
SELECT application_name, count(*) FROM pg_stat_activity
WHERE datname='unified_donkey_betz' GROUP BY 1 ORDER BY 2 DESC;
```

```
dbz:web                   35    <- daphne
dbz:celery-broadcast       3
dbz:celery-long-running    3
dbz:celery-pa              3    <- bound lazily on first PA task (after Rigby ack ping)
dbz:celery-worker          1    <- default+agents+content (local-merged)
dbz:celery-beat            1
unified_donkey_betz        1    <- ad-hoc smoke-check shell (no env var); expected default
```

6 of 6 active process classes covered. The legacy `unified_donkey_betz` row is the smoke-check shell that doesn't set the env var — proves the legacy default still works for one-off interactive sessions.

**Design tradeoff resolved with Rigby:** Two viable implementation paths (Procfile env var vs. `core/celery.py` runtime hook deriving the tag from `CELERY_QUEUES`). Rigby's verdict: **Path A (Procfile env var)** — "explicit-over-clever, right fit for a COO MUST." The 11 file edits are one-shot; drift risk is real but a Procfile comment + the strict verifier covers it.

### PR #2302 — WARN-persist 2 snapshots → CRIT escalation (item C)

**Problem (Session 1164 deferred):** WARN status persisted across multiple snapshots with no escalation. A backlog forming-but-not-crisis (`depth >= 5` for 60 min) or recurring failures (`failure >= 1` for 60 min) stayed WARN indefinitely. Spec called for "WARN persists 2 consecutive snapshots → CRIT escalation" but was gated on ≥24h of new-schema `sustain_gating` JSONL telemetry post-#2292 so the escalation logic had stable observability to read.

**Surface:**

- `core/management/commands/pa_acks_health.py` — three new factory-style probes:
  - `_trips_warn_hang(report)` — `hang_count >= _WARN_HANG_COUNT` (1)
  - `_trips_warn_failures(report)` — `failures >= _WARN_FAILURE_COUNT` (1)
  - `_trips_warn_depth(report)` — `depth >= _WARN_QUEUE_DEPTH` (5)

  Mirror the Session 1164 `_trips_no_workers` / `_trips_depth_crit` pattern. Class methods so they're cheap to call against either `report` or `previous_report` without instance state.

- `core/management/commands/pa_acks_health.py:765` — in `_compute_status`, after the existing sustain-gating block, compute `escalated_triggers` via the same `previous_adjacent` check + the new probes:

  ```python
  escalated_triggers: list[str] = []
  if previous_adjacent:
      if self._trips_warn_hang(report) and self._trips_warn_hang(previous_report):
          escalated_triggers.append("warn_persist:hang")
      if self._trips_warn_failures(report) and self._trips_warn_failures(previous_report):
          escalated_triggers.append("warn_persist:failures")
      if self._trips_warn_depth(report) and self._trips_warn_depth(previous_report):
          escalated_triggers.append("warn_persist:depth")
  ```

- New `sustain_gating.escalated_triggers` field on every snapshot. Sibling to the existing `gated_triggers` field but with **boosting** semantics (this trigger fired because it persisted) rather than suppression semantics (this trigger was gated by sustain window). Schema choice ratified by Rigby: keep `gated_triggers` and `escalated_triggers` separate for clean semantics — no merge.

- CRIT short-circuit extended with `or escalated_triggers`. Any non-empty list → CRIT.

- `core/tests/test_pa_acks_health_thresholds.py` — 15 new tests across two new classes:
  - `TestWarnTierProbes` (3 helper tests, parallels `TestSustainGateCorrectness`).
  - `TestWarnPersistEscalation` (12 truth-table cases): each sub-trigger persisting → CRIT; each sub-trigger single-snapshot → WARN; stale previous → no escalation; previous=None → no escalation; cross-trigger drift → no escalation; multiple sub-triggers persisting → both recorded; no_workers persist → not double-escalated via warn_persist path; field always present; CRIT short-circuit preserves higher severity even when warn_persist also fires.
  - **52/52 tests pass** (15 new + 37 existing).

**Design decisions locked with Rigby:**

- **Path 2 (factory-style probe re-evaluation) over Path 1 (cached status field on previous JSONL line).** Robust against threshold changes between snapshots.
- **Per-sub-trigger semantics** — hang↔hang, failures↔failures, depth↔depth. Cross-trigger drift (depth then hang) is NOT counted as persistence because the signal isn't the same one continuing.
- **`no_workers` excluded** — already CRIT-escalates via the existing sustain machinery from PR #2292; adding it here would double-escalate.
- **Status when persist fires = CRIT.** No new intermediate `WARN_ESCALATED` tier — keep taxonomy simple.
- **Greppable labels** — `warn_persist:hang`, `warn_persist:failures`, `warn_persist:depth`. Each named after the sub-trigger that persisted.

**Edge case ratified pre-merge:** when a single-snapshot CRIT condition fires (e.g. `failures >= 3`) AND the WARN-persisted predicate is also true (previous `failures >= 1`), `status = CRIT` (from the failures>=3 path, short-circuits first) AND `escalated_triggers` records `warn_persist:failures`. Rigby's verdict: correct behavior. Preserves causal context ("this wasn't just a spike; it was already deteriorating") while the verdict stays CRIT for the primary reason. UI/log consumers treat `status` as the truth and `escalated_triggers` as annotations.

**End-to-end smoke (post-restart, manual cadence dispatch):**

```
tail -1 logs/pa_acks_health/2026-06-20.jsonl
-> generated_at: 2026-06-20T00:48:01.904236+00:00
   status: OK
   sustain_gating.escalated_triggers: []     <- healthy state, no persist this tick
```

Backward compatibility verified: pre-restart JSONL lines (without `escalated_triggers`) still parse via `_read_previous_snapshot` without errors. The new field is purely additive.

---

## Behavioral contracts / invariants (post-merge, system-wide)

Three statements that should now always be true. If any is violated under normal operation, that's a signal worth investigating — not a bug to silently patch around.

1. **Every long-lived Donkey Betz process tags its DB connection.** `SELECT application_name, count(*) FROM pg_stat_activity WHERE datname='unified_donkey_betz' GROUP BY 1` should never show ≥80% of connections under `unified_donkey_betz` — the legacy default. A handful of legacy-tagged connections is expected (ad-hoc shells, smoke checks, one-off `manage.py` runs); the bulk of connections should carry `dbz:<role>` tags reflecting their process class. If `unified_donkey_betz` dominates, either a Procfile entry was added without `PG_APPLICATION_NAME=` (verifier should catch this) or the env var failed to propagate at process startup.

2. **A WARN-tier sub-trigger that fires on two adjacent snapshots (within 60 min) becomes CRIT.** This is the new invariant added by item C. Hang persists for the full 60 min → CRIT. Same failure rate (`failures >= 1`) for two snapshots in a row → CRIT. Same backlog level (`depth >= 5`) for two snapshots in a row → CRIT. If the JSONL shows two adjacent snapshots both tripping the same `_trips_warn_*` probe but status stayed WARN, either `_is_previous_adjacent` returned False (the 60-min adjacency window was exceeded — check `generated_at` deltas) or the escalation logic regressed.

3. **`gated_triggers` and `escalated_triggers` have opposite semantics on the same `sustain_gating` block.** `gated_triggers` = "this trigger WOULD have fired but the sustain window suppressed it" (binary infra triggers like `no_workers`, `depth_crit`). `escalated_triggers` = "this trigger fired and persisted, so status was boosted to CRIT" (WARN-tier triggers like `warn_persist:hang`). Both lists can be empty, populated, or coexist on the same snapshot. A snapshot should NEVER have the same trigger label in both lists — that would mean we're both suppressing and boosting the same signal in one tick.

These three invariants are the post-merge "should always be true" companion to the rollback levers below ("how to break them in an emergency") and the 24h watch checklist further down ("how to verify they hold").

---

## Rollback / disable levers

Operational escape hatches if either of the two PRs misbehaves in production. Documented here so a future operator can disable a single primitive without rolling the whole session.

### #2301 — Per-process Postgres `application_name` tagging

**Location:** `core/settings.py:283` — the `DATABASES['default']['OPTIONS']['application_name']` assignment.

**Soften (recommended emergency lever)** — revert to the legacy static default while keeping the env-var read path intact:

```python
# core/settings.py:283 — comment out the env var read
DATABASES['default']['OPTIONS'] = {
    'application_name': 'unified_donkey_betz',  # was os.environ.get('PG_APPLICATION_NAME', 'unified_donkey_betz')
    ...
}
```

Then restart daphne + celery to flush old PG connections. Existing connections honor the OLD `application_name` until they cycle (`CONN_MAX_AGE=60`).

**Per-process override** — set `PG_APPLICATION_NAME` to anything you want on a specific shell or task to make it stand out in `pg_stat_activity`:

```bash
PG_APPLICATION_NAME=dbz:debug-shell python manage.py shell
# now this shell's connections will show as `dbz:debug-shell` instead of `unified_donkey_betz`
```

Useful for isolating an investigation: tag a one-off task or migration with a unique name, then query `pg_stat_activity` filtered to that tag.

**Fully disable the verifier check** (if the Procfile coverage check itself misfires) — pass `--no-strict` to `scripts/verify_repo_guardrails.py` or comment out the `procfile_tag_blocking=procfile_tag_blocking` arg in the `classify_failures` call inside `main()`. The advisory Makefile check is already non-blocking and needs no override.

**Bypass for prod hot-fix Procfile edits** — adding a new Procfile entry without the env var trips the strict verifier. If you legitimately need to push a new entry fast and add the tag in a follow-on commit, use `--no-strict` for that one verifier run. The PR template's narrative-edit checklist does not gate Procfile changes; the verifier does.

### #2302 — WARN-persist 2 snapshots → CRIT escalation

**Location:** `core/management/commands/pa_acks_health.py:_compute_status` — the `escalated_triggers` block + the CRIT short-circuit extension.

**Soften (recommended emergency lever)** — narrow which sub-triggers participate. If `failures` is producing too many false CRITs (e.g., the `_WARN_FAILURE_COUNT=1` threshold is too tight in practice):

```python
# core/management/commands/pa_acks_health.py — inside _compute_status, in the warn-persist block
if previous_adjacent:
    if self._trips_warn_hang(report) and self._trips_warn_hang(previous_report):
        escalated_triggers.append("warn_persist:hang")
    # if self._trips_warn_failures(report) and self._trips_warn_failures(previous_report):
    #     escalated_triggers.append("warn_persist:failures")  # DISABLED — failure rate too noisy
    if self._trips_warn_depth(report) and self._trips_warn_depth(previous_report):
        escalated_triggers.append("warn_persist:depth")
```

Or raise the underlying threshold (`_WARN_FAILURE_COUNT = 2`) so a single failure no longer trips WARN at all.

**Fully disable** — comment out the CRIT short-circuit extension:

```python
# core/management/commands/pa_acks_health.py — in the CRIT short-circuit
if (
    hang_count >= self._CRIT_HANG_COUNT
    or failures >= self._CRIT_FAILURE_COUNT
    or oldest_hang_age >= self._CRIT_HANG_AGE_SEC
    or depth_crit_sustained
    or (no_workers_sustained and self._CRIT_NO_WORKERS)
    # or escalated_triggers  # Session 1166 PR #2302 item C; disable to revert
):
    report["status"] = "CRIT"
    return
```

The `escalated_triggers` field still populates on every snapshot for observability — only the verdict path is disabled. Useful for "watch but don't escalate" mode if a false-positive incident surfaces and we need to debug what the persist semantics would have caught while keeping status verdicts conservative.

**Adjust adjacency window** — `_EXPECTED_INTERVAL_SECONDS = 1800` and `_SUSTAIN_ADJACENCY_FACTOR = 2` produce a 60-min window. To accept "less adjacent" snapshots (e.g., during a planned scheduler pause where cadence may slip):

```python
_SUSTAIN_ADJACENCY_FACTOR = 4   # was 2 — now accepts up to 120 min between snapshots
```

Note: widening the window makes the WARN-persist signal less sensitive (fewer escalations) AND less timely (more time before escalation). Typically you want this narrower, not wider — but the lever exists for emergency loosening.

**Manually clear an "escalated" state** — `escalated_triggers` is computed fresh every snapshot from `previous_report`. There's no persistent state to clear. If a CRIT escalation fires once and then the underlying triggers clear, the next snapshot naturally drops to WARN or OK. No ops escape hatch needed; just wait one cadence tick (30 min).

---

## What to watch in the first 24h post-merge

Lightweight observability checks for the first day after the Session 1166 PRs go live. The two PRs are independent, so the checks are split by PR.

### 1. `pg_stat_activity` per-component breakdown — confirm bulk of connections carry `dbz:` tags

```bash
.venv/bin/python manage.py dbshell -- -c "
SELECT application_name, count(*) FROM pg_stat_activity
WHERE datname='unified_donkey_betz' GROUP BY 1 ORDER BY 2 DESC;"
```

**Expect:** ≥80% of connections under `dbz:*` tags. A handful of `unified_donkey_betz` connections is fine (ad-hoc shells, smoke checks). If `unified_donkey_betz` dominates, check that the celery + daphne processes were restarted post-merge to pick up the env var — old connections honor the old `application_name` until they cycle (`CONN_MAX_AGE=60`, so within ~1 min of restart).

### 2. Procfile verifier — confirm strict pass on main

```bash
.venv/bin/python scripts/verify_repo_guardrails.py --inventory-advisory 2>&1 | grep -A 2 "Procfile PG_APPLICATION_NAME"
```

**Expect:** "OK: every Procfile entry sets PG_APPLICATION_NAME=dbz:<role>." If a Procfile entry was added without the tag (e.g., during an emergency hot-fix), the verifier will flag it. Either add the tag and re-run, or bypass with `--no-strict` for the one run.

### 3. `escalated_triggers` field populated on new JSONL lines

```bash
# count how many new-schema lines exist today
tail -10 logs/pa_acks_health/$(date +%Y-%m-%d).jsonl | .venv/bin/python -c "
import json, sys
for i, line in enumerate(sys.stdin, start=1):
    d = json.loads(line)
    sg = d.get('sustain_gating', {})
    print(f'  line {i}: status={d.get(\"status\")} escalated_triggers={sg.get(\"escalated_triggers\")} generated_at={d.get(\"generated_at\")}')"
```

**Expect:** every line carries `escalated_triggers` (empty list `[]` in healthy state). If lines lack the field, the workers haven't restarted post-merge — fix with `pkill -9 -f celery; rm -f .celery*.pid; make celery`.

### 4. Look for `warn_persist:*` escalations in the past 24h

```bash
# any escalation events recorded today
grep -o '"escalated_triggers":\[[^]]*\]' logs/pa_acks_health/$(date +%Y-%m-%d).jsonl | sort | uniq -c | sort -rn
```

**Expect:** the bulk under `"escalated_triggers":[]`. Any non-empty list is a real CRIT escalation worth investigating — find the snapshot line:

```bash
grep -n 'warn_persist:' logs/pa_acks_health/$(date +%Y-%m-%d).jsonl
```

The line context tells you WHICH WARN sub-trigger persisted (hang, failures, or depth). Use that to diagnose the root cause:
- `warn_persist:hang` → same task hang sample present 60 min apart; check `hang_signature.samples` for the task name + age
- `warn_persist:failures` → failure count stayed `>= 1` for 60 min; check celery worker logs for the failing task
- `warn_persist:depth` → backlog stayed `>= 5` for 60 min; check `cockpit_tool.queue_lengths` for which queue is backed up

### 5. CRIT escalation observability — check the celery-broadcast log for the WARN-level log line

```bash
grep -i "pa_acks_health" celery-broadcast.log | grep -v "succeeded\|received" | tail -20
```

**Expect:** WARN-level lines fire whenever `status != OK`. The new code path means CRIT can now be reached via the warn-persist route. If a CRIT line appears, the JSONL on the same timestamp will have `escalated_triggers` populated — cross-reference for context.

### AM check execution plan

Around 7:30–9:00 AM MST, run all 5 checks above. Total expected time: <5 minutes. If everything is clean (≥80% `dbz:*` tags in `pg_stat_activity`, every recent JSONL line carries `escalated_triggers`, no surprise CRIT escalations), document the result in the Session 1167 entry and the operational surfaces can be trusted going forward. If any check surfaces unexpected behavior, use the rollback levers above to soften/disable while investigating.

---

## Open items carrying into Session 1167

### MUST tier

- **NONE.** All four MUSTs from Rigby's June 14 corrected v1 backlog are now closed. Session 1166 closed #2; Session 1165 closed #1 + #3 + #6.

### SHOULD tier

- **COO #5 — Memory telemetry + automatic downshift.** Procfile already has `--max-memory-per-child` caps; this adds visibility + throttle hook. Likely needs Rigby's design pass on the throttle-hook surface (PA tool action? `cockpit_tool` extension? new gateway?) before code.
- **COO #7 — Top Consumers ops endpoint.** Pairs naturally with the queue_pressure surface Session 1164 added. Could fold into a single ops snapshot rather than a separate gateway.

### Consolidation / deferred from Session 1165 (focused follow-on PRs)

- **Operator_edge lock consolidation** (`core/tasks_content.py:4216` + 6 release sites). Migrate the third ad-hoc `cache.add()` site to the canonical `singleton_lock` primitive from PR #2296. Behavior-preserving but bigger blast radius — deferred from PR #2296.
- **`_circuit_breaker_check` step-3 lock consolidation.** Symmetric to operator_edge. Worth its own focused PR.
- **Agent-task family retry budgets.** Wire the `retry_policy` primitive from PR #2297 to the agent task family. Needs fingerprinting strategy first (`agent_name + user_id + workspace_id`) to avoid global suppression during transient incidents.
- **Bulk migration of ~5 linear/fixed countdown sites** (`core/tasks_agents.py` family) to `compute_retry_countdown` from PR #2297.

### Aspirational follow-ons (from Session 1165 — still queued)

- **`pg_stat_statements` on staging/prod.** Installed locally in Session 1165 for the COO #1 threshold sniff. Same change to `postgresql.conf` (`shared_preload_libraries = 'pg_stat_statements'`) + `brew services restart postgresql@<v>` + `CREATE EXTENSION` would enable live p99-based threshold reviews in non-local environments.
- **`capture_pa_acks_health_snapshot` slow-task investigation.** Rigby flagged 36-min max, 18-min avg as suspicious for a "snapshot" workload. Now also a canary for the new 60s `statement_timeout` — if it starts failing under the timeout, that's the symptom telling you what was slow.

### Carryover small follow-ons from Session 1163 (still queued)

1. **Legacy `SystemConfiguration(key='policy_arbitrator_snapshot')` row cleanup** — small migration to hard-delete the legacy row after one or more new-model cycles have been observed (single-PR scope).
2. **`cycle_id` joinability fix** — `_policy_policy_arbitrator` in `core.py:2658` accepts the run-cycle's `cycle_id` instead of generating its own (single-file edit; joins `FinalAppliedOverrides` against `AutopilotAction`).
3. **Opportunistic narrative §4 + §5 cleanup of stale `FinalAppliedOverrides` mentions** — wait for the next time someone touches those sections.

### Deferred infrastructure track (avoid during offline-CI window)

4. **`celery-beat-schedule` CONFLICT — detector tuning** (preferred) or 36-file token-pattern phrasing sweep (fallback).
5. **Pre-existing PeriodicTask drift** (Session 1163 added 1 entry).
6. **`exists_on_disk: false` flag** in `_provenance.json` — 326 dead paths. Schema bump v1 → v2.
7. **Beat-schedule the regens** — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
8. **Fix `build_learning_bridge_audit.py` generator** — falsely flags "ABC unused".
9. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern.

### Chris-call-only carryovers (still parked)

10. **Decision Command backend cleanup** — 5 Python files (regressed feature).
11. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
12. **Mission refresh PR #2190** — preserved branch.

---

## Cross-session lessons (NEW from Session 1166)

- **NEW (1166)** **The "smallest open MUST" is often the right next quick-win.** COO #2 looked trivial on paper (one settings line + N Procfile edits) and stayed trivial in practice — but the verifier-plus-doc-note follow-on captured 80% of the value of the change. The strict Procfile coverage verifier means a future Procfile edit can't drop the tag silently; the doc note in `infrastructure.md` means a future operator sees the scheme without having to grep. Without those two safeguards, the COO #2 surface would have rotted as soon as someone added a new Procfile entry. Right-sized scope = primitive + verifier + doc note, in one PR.
- **NEW (1166)** **Path A vs Path B framing is the right pre-implementation review surface.** Before code on COO #2, posted two viable implementation paths (Procfile env var vs `core/celery.py` runtime hook deriving the tag from `CELERY_QUEUES`) with pro/con for each + my lean. Rigby ratified Path A in one message ("explicit-over-clever, right fit for a COO MUST"). Same pattern worked on item C with Path 1 (cached status field) vs Path 2 (factory-style probe re-evaluation). The single-paragraph "here are the two ways, here's my lean, OK to lock?" frame keeps the design conversation tight without losing the alternative.
- **NEW (1166)** **Value-scheme naming is a separate locking step from path selection.** After Rigby locked Path A on COO #2, I posted a follow-up message with proposed 11 Procfile values (`dbz:release`, `dbz:web`, etc.) + 2 design points (local-vs-Procfile drift; resolve-node tag). She locked the scheme + ratified (i) same role tag in both local + prod + (ii) tag resolve-node anyway. Two-step framing (path then values) avoided mixing "which approach" with "what to call things" — both are real decisions; both deserve their own locking.
- **NEW (1166)** **`gated_triggers` (suppression) and `escalated_triggers` (boosting) want different field names.** Item C added a sibling field rather than overloading `gated_triggers` with mixed semantics. Rigby ratified the schema choice mid-PR: "keeping gated_triggers (suppression) separate from escalated_triggers (boost) is a clean schema choice—no need to merge." Lesson: when adding a new mechanism that operates on the same observability surface, prefer a new field over overloading an existing one if the directional semantics differ. The pair under one parent (`sustain_gating.{gated,escalated}_triggers`) reads cleanly in JSONL grep + dashboards.
- **NEW (1166)** **Two-step session arc beats single-PR-then-design-3rd.** Session 1166 shipped two PRs and stopped before #5 (Memory telemetry). The natural close was the handoff — not a third PR. Trying to fit #5's design pass into the same session would have meant a rushed Rigby review on a SHOULD-tier item; #5 deserves its own pre-implementation pass with Rigby (throttle hook surface design call) before code. Two-PR + handoff = one clean session arc; three PRs = drift.
- **NEW (1166)** **Backward-compat for additive observability fields is free.** PR #2302 added `sustain_gating.escalated_triggers` without touching `_read_previous_snapshot`. Old JSONL lines load via the same parser; the new field is only WRITTEN by the new code path. Item C's CRIT escalation only fires when BOTH current AND previous probes trip — pre-restart lines that don't have the new field aren't ELIGIBLE to trip the escalation because they're already stale post-restart by the time the new logic runs. No migration, no schema flag, no transition window. Lesson: additive-only changes to JSONL observability surfaces don't need transition machinery if the new logic is downstream of the writer.

---

## Self-merge protocol summary (Session 1166)

Both PRs merged via bypass mode under the GitHub Actions billing outage active since Session 1149.

| PR | Local mirrors run | Failure surface | Chris auth |
|---|---|---|---|
| #2301 | ✅ `verify_repo_guardrails.py --inventory-advisory` (only failure: pre-existing celery-beat-schedule CONFLICT); ✅ `check_direct_llm_calls.py --warn-only` (baseline) | NEW Procfile strict check PASSES; NEW Makefile advisory PASSES | "merge it" (in-session, 2026-06-19) |
| #2302 | ✅ `verify_repo_guardrails.py --inventory-advisory` (only failure: pre-existing celery-beat-schedule CONFLICT); ✅ `check_direct_llm_calls.py --warn-only` (baseline) | 52/52 tests pass | "Yes go ahead and merge!" (in-session, 2026-06-19) |

Bypass merge commit bodies document the protocol + Chris's per-PR auth (per memory rule `feedback_local_only_default.md` + Sessions 1159 PR #2255 + 1163 PR #2286 + 1165 PRs #2295/#2296/#2297 precedent).

---

## Commit message hygiene streak

Sessions 1145–1166 all 100% subject-tagged with `session-NNNN`. Session 1166 commits:

```
512c7922 Merge pull request #2301 from clwest/feat/session-1166-pg-application-name
abdd52d4 docs(session-1166): infrastructure.md note on PG_APPLICATION_NAME scheme
162fec29 feat(session-1166-ops): per-process Postgres application_name tagging (COO #2)
47de895c Merge pull request #2302 from clwest/feat/session-1166-warn-persist-crit-escalation
f1f18291 feat(session-1166-ops): WARN-persist 2 snapshots → CRIT escalation (item C)
```

5 commits, 5 subject-tagged. Streak intact.
