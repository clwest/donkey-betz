---
originating_session: 1161
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1161 handoff. Three sequential PRs that complete Rigby's PR #2266/#2267 follow-on work (A, B, cadence) — the PA acks_late=False watch window now has metrics, attribution, persistence, and a 30-min capture cadence. Session ended with Rigby's "stop and watch" greenlight after the cadence wrapper verified end-to-end.
---

# Session 1161 — PA acks_late watch instrumentation + 30-min cadence

**Date:** 2026-05-26 (seventeenth back-to-back session)
**Branch state at session close:** All work merged. Main is clean. Three PRs landed.

---

## TL;DR

Session 1161 turned the Session 1160 `pa_acks_health` mgmt command from a single-snapshot scaffold into a complete observation surface for the Session 1159 `acks_late=False` 24–48h watch window. Rigby ranked the work as three sequential follow-ons (A, B, cadence). Each shipped as its own PR with the next branch starting after the previous merged.

1. **(A) Ack-behavior proxy** (PR #2269) — added `oldest_queued` + `inflight_estimate` (recv − finished delta) so queue-depth alarms don't flap on a single in-flight task.
2. **(B) Per-worker attribution** (PR #2270) — unioned inspect-side workers with DB-side workers in window; added `worker_last_event_at` heartbeat proxy on each hang sample to distinguish "worker stuck" from "task wedged but worker alive."
3. **Cadence wrapper** (PR #2271) — extracted `Command.build_report()` from `handle()`, added `core.tasks.capture_pa_acks_health_snapshot` on a 30-min beat schedule, appends one snapshot per line to `logs/pa_acks_health/YYYY-MM-DD.jsonl`. WARN-level log line fires when status != OK.

Post-cadence-merge: workers restarted (`pkill -9 -f celery; rm -f .celery*.pid; make celery`) to pick up the newly-registered task. Full path verified end-to-end (beat → broadcast worker → task → JSONL write). JSONL grows every 30 minutes from session close forward.

Session ended with Rigby's "stop and watch" greenlight. OK/WARN/CRIT thresholds intentionally untouched — that tuning (item 3d in `00-START-NEXT-SESSION.md`) is deferred until 24–48h of cadence data exists to support it.

---

## What shipped

| PR | Theme | Merge SHA |
|----|-------|-----------|
| **#2269** | `pa_acks_health` (A) — `oldest_queued` + `inflight_estimate` ack-behavior proxies | `7244dfdb` |
| **#2270** | `pa_acks_health` (B) — `per_worker` rollup + `worker_last_event_at` on hang samples | `77bd18d8` |
| **#2271** | `pa_acks_health` cadence wrapper — `build_report()` refactor + every-30-min beat task + JSONL persistence | `6656f193` |

Three squash-merge commits to main, all via bypass-mode (GH Actions billing still down, multi-day). All three modified production code (new `@shared_task`, new beat entry, new mgmt-command method) and were explicitly Chris-authorized in-session per the Session 1159 PR #2255 precedent. Each PR's local mirrors passed with only the pre-existing `celery-beat-schedule CONFLICT` (active issue #2 in `00-START`).

---

## PR #2269 — (A) ack-behavior proxy

Rigby's PR #2266/#2267 follow-on (A): add `oldest_queued_age` + `recv_minus_finished` delta so queue-depth alarms don't flap. Her stated reason: a single STARTED task that ran 90s shouldn't trip the same alarm as a real backlog.

Two new top-level keys in the report:

- **`oldest_queued`** — age (seconds) of the oldest `CeleryTaskEvent` row with `status=QUEUED` for the focused task_name. Independent of total queue depth. Returns `present: false` when clear. Not bounded by the window because a queued row sitting for hours is exactly the signal we want to surface, even if it predates the lookback.
- **`inflight_estimate`** — `total − (success + failure + revoked)` over the window. Reuses the already-aggregated counts from `_task_stats` — no extra query. Equivalent to `started_still + queued` over the window plus any row in an unrecognized status.

Soft advisory flag added: fires when `oldest_queued.age > slow_threshold`. OK/WARN/CRIT thresholds **unchanged** — Rigby's A-vs-tuning separation. Threshold tuning waits on cadence data.

Live smoke at PR #2269 close: 14 tasks / 14 success / 0 hangs / inflight delta 0 / oldest_queued clear.

---

## PR #2270 — (B) per-worker attribution

Rigby's follow-on (B): localize WARN/CRIT signals to a specific worker process instead of just "something's wrong somewhere." She rejected the "wait 24h then do B" path because observation without attribution only tells you *something* is wrong, not *where*.

New top-level key `per_worker` — list of one row per worker, **unions** inspect-side workers (currently online) with DB-side workers (active in the window). Each row carries 8 fields:

| Field | Source | Purpose |
|---|---|---|
| `name`, `online` | inspect stats | identity + currently-online flag |
| `active_count`, `reserved_count` | inspect (None when offline) | current load |
| `started_still` | DB (STARTED-not-finished) | concurrent hangs on this worker |
| `slow_completed` | DB (SUCCESS\|FAILURE, duration >= threshold) | historical slowness |
| `oldest_started_age_seconds` | DB | max age of started-but-not-finished |
| `last_event_at` | DB (max started_at OR finished_at) | heartbeat proxy |

Enhanced `hang_signature` samples: each row now carries `worker_last_event_at` (most recent event from the same worker, across all task_names). If equal to `started_at`, the worker has done nothing since the hung task fired prerun — strong signal the worker process itself is stuck. If later, the task is wedged but the worker is alive. Single `Max()` per distinct worker — no N+1.

Live smoke at PR #2270 close: 4 workers online. `pa@Chriss-MBP.lan` showed `slow_completed=3` (matching the three 60-80s PA tasks from earlier in the session) + recent `last_event_at`. `broadcast/default/long_running` showed `last_event_at=None` — online but no PA work in window, which is correct since each handles different queue assignments. Status still OK.

---

## PR #2271 — cadence wrapper

After PRs #2269 + #2270 landed, Rigby's call: "pause for 24-48h observation now," but with two non-PR operational items first — set a cadence + define action thresholds. The cadence side became this PR. The thresholds doc lives below in this handoff (Rigby explicitly framed it as handoff content, not code).

Three pieces in one PR:

**1. `pa_acks_health.py` refactor** — extract `build_report()` from `handle()`. Pure refactor with kwargs-only signature matching CLI defaults. The `handle()` method now just calls `build_report()` and formats. Callers needing the structured report (the new beat task, future tools) skip CLI option parsing and stdout capture.

**2. `core/tasks.py` — `capture_pa_acks_health_snapshot`** — new `@shared_task` on the `broadcast` queue (60s soft / 90s hard timeout). Calls `Command().build_report()` directly, appends one JSON object per line to `logs/pa_acks_health/YYYY-MM-DD.jsonl`. Emits `logger.warning` whenever `status != OK` so daphne/celery log streams flag transitions independently of the JSONL. Returns a small summary (status, queue_depth, worker_count, hang_count, inflight_delta, log_path) for celery task event row searchability.

**3. `core/celery.py` — beat schedule entry** — new `pa-acks-health-capture` on `crontab(minute='*/30')`, queue=broadcast, expires=1800. Materialized via `add_critical_celery_tasks` (PeriodicTask row confirmed: `enabled=True`, schedule="*/30 * * * * America/Denver"). beat_schedule count went 77 → 78.

### Worker-restart gotcha after merge

After PR #2271 merged, beat dispatched the first scheduled fire at 10:30 PT (16:30 UTC). The broadcast worker rejected with `Received unregistered task of type 'core.tasks.capture_pa_acks_health_snapshot'`. Celery workers cache registered tasks at process import time — new `@shared_task` decorators are invisible until the worker process restarts. This is the same root cause as the memory rule that "PA tool registration needs both daphne and celery restart," now generalized to any new `@shared_task`.

Fix per Chris-authorized option 1:
```bash
pkill -9 -f celery
rm -f .celery*.pid
make celery
```

Beat picked up the new PeriodicTask row automatically (no restart needed there — `DatabaseScheduler` polls). After restart, manually-dispatched task succeeded end-to-end: beat → broadcast worker → task → JSONL write. JSONL grew from 2 → 3 entries.

**Memory rule generalized:** any new `@shared_task` in `core/tasks.py` requires worker restart to register, not just PA tool schema changes. Already captured in `feedback_celery_pid_cache_blocks_restart.md` — content covers the broader case.

---

## Action-threshold doc (per Rigby's Session 1161 ranking)

Documented here per Rigby's "in the handoff, not in code" framing. These are the thresholds that should trigger investigation while the cadence wrapper runs:

| Condition | Response |
|---|---|
| **Any CRIT** | look this hour |
| **WARN persists for 2 consecutive snapshots** (i.e., the same WARN signal appears in two adjacent `*/30` snapshots) | investigate |
| **Any `hang_age ≥ 180s`** | investigate even if it clears |

The cadence wrapper does NOT enforce these — they're operator-side. Once we have a few days of JSONL data and confirm the false-positive rate is low, threshold tuning (item 3d in `00-START`) can fold them into `_compute_status()`.

---

## Notes flagged by Rigby for the handoff

### Timezone clarity in the JSONL records

`generated_at` is a Django-default UTC ISO timestamp; the filename uses `timezone.now().strftime('%Y-%m-%d')` which is also UTC. The records don't currently carry a Mountain-time human-readable string. If operator readability becomes a friction point during the 48h watch, a follow-on PR can add `generated_at_mt` to the report dict (single line in `build_report()`). Filed as a candidate non-blocker; not shipped this session because it's cosmetic.

### Rotation / retention

Filename is date-based (`YYYY-MM-DD.jsonl`) so the file rotates daily at UTC midnight automatically. Expected size: ~48 snapshots/day × ~2-4 KB each = **~100-200 KB/day**. No retention policy currently — manual cleanup or a future beat task if/when it matters. For the 48h watch window that's ~400 KB total, well below any concern. `logs/` is gitignored so nothing is committed.

---

## What did NOT happen (carryovers + skipped items)

### Still queued (carryover from 00-START Session 1161)

- **(C) UI spinner proxy** — Rigby deferred this until a reliable turn/response table is identified. `ChatConversation` rows were Rigby's initial proposal; confirming whether that table has the right shape for "request received but no assistant response after N minutes" is the prerequisite work.
- **3d. Threshold tuning** — explicitly deferred. The whole point of the cadence wrapper is to gather the data that supports this. Earliest sensible session for this: 1162 if 24h of JSONL is enough, more likely 1163.
- **Old `docs/topics/` sweep** (7 Feb-March docs from Session 1147 #2221) — still queued.
- **Cosmetic `load_all_agents_advisors.py 149→139` fix** — still queued.

### Deferred infrastructure track (untouched this session — appropriate during offline-CI window)

- `celery-beat-schedule` CONFLICT detector tuning / 36-file token-pattern phrasing sweep
- Pre-existing 3-row PeriodicTask drift (now 4-row after Session 1161 added one entry; still not the right session for this)
- `exists_on_disk: false` flag in `_provenance.json`
- Beat-schedule the regens (weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands)
- Fix `build_learning_bridge_audit.py` generator
- Redis pooling sweep (~40 inline `redis.Redis.from_url(...)` sites)

### Optional cosmetic tweak NOT done

Rigby's "PA worker set vs generic online workers" filter — explicitly flagged as optional. Skipped to keep the session's scope clean.

### Chris-call-only carryovers (still parked)

- Decision Command backend cleanup (5 Python files, regressed feature)
- DaVinci route removal (`core/views_davinci.py`)
- Mission refresh PR #2190 (preserved branch)

---

## Active issues carrying into Session 1162

### 1. GitHub Actions billing — still down

Same annotation as Sessions 1149-1160. Multi-day outage. Self-merge protocol from Session 1160 still applies; each Session 1161 PR followed it exactly.

### 2. `celery-beat-schedule` CONFLICT — detector signal pending

Session 1157 PR #2243 closed the code-level footgun. Context-kit CONFLICT signal still flags because its detector heuristic is keyword/path-based across ~36 files. Queued for Session 1162+.

### 3. PA `acks_late=False` watch — NOW INSTRUMENTED, observation phase begins

The previous "passive observation" item is now an active capture. JSONL grows every 30 min. Next session should:
- Confirm JSONL has been growing without errors.
- Sample a few snapshots — do non-OK transitions surface in the celery-broadcast log too?
- If 24+ hours of clean data, consider threshold tuning (3d).

---

## Cross-session lessons added this session

- **NEW (1161)** **Cadence wrappers belong in beat, not cron.** The `DatabaseScheduler` polls — adding a `PeriodicTask` row via `add_critical_celery_tasks` is the canonical path. Beat picked up the new row in <2 minutes without restart.
- **NEW (1161)** **New `@shared_task` decorators are invisible to running workers.** Generalizes the existing PA-tool-registration restart rule to any task addition. The 1-step fix (`pkill + rm pid + make celery`) is fast and local.
- **NEW (1161)** **"Stop and watch" is its own ship-able milestone.** Three small sequential PRs that move from "snapshot tool" to "cadenced observation surface" can complete a session arc without needing to ship the analytics layer on top. Saving the threshold-tuning work for the next session (once data exists) is the right A-vs-tuning separation.

---

## Recent session arcs (rolling)

- **Session 1161** (this session) — PA acks_late watch instrumentation + cadence. 3 PRs merged.
- **Session 1160** — 1158-carryover queue clear + EDITING_GUARDRAILS operational. 8 PRs merged (6 cleanup + 2 `pa_acks_health` scaffolding).
- **Session 1159** — PA `acks_late=False` fix + narrative B/C/D iterations + EDITING_GUARDRAILS contract. 3 PRs merged.
- **Session 1158** — 15 subsystem narratives + drift sweep + cited-handoff frontmatter. 8 PRs merged.
- **Session 1157** — celery-beat-schedule cleanup option A. 1 PR.
- **Session 1156** — P3.5 round 9 (FINAL) + P3.5 track CLOSE.
- **Session 1155-1151** — P3.5 rounds 8–4.
- **Session 1150** — 1149 merge wave + P3.5 round 3.
- **Session 1149** — SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes.

Full handoff lineage: `docs/handoffs/CURRENT.md`.

---

## Session 1162 entry point candidates

Chris's call on priority. No items are blocked on Chris-decision at session open.

### Rigby's 24-48h readout checklist (added post-handoff)

After her review of the cadence wrapper close, Rigby flagged a specific readout for whichever session reviews the JSONL. Run these against `logs/pa_acks_health/*.jsonl`:

- **WARN/CRIT transition count** — expected 0. Any non-zero means a status change actually fired during the window.
- **`inflight_estimate` drift** — expected to stay near 0 except for brief bursts. Sustained positive drift = receive-faster-than-finish.
- **`oldest_queued` spikes** — expected rare and short. Persistent spikes = workers lagging.
- **Slow-completion clustering by worker** — does `per_worker.slow_completed` concentrate on one worker? A consistently-hot node is a different signal than uniform slowness.

If all four read clean, threshold tuning (3d) is safe to ship. If any read dirty, that's the actual signal to debug before tuning.

### Observation-mode items (passive, may not produce a PR)

1. **Review `logs/pa_acks_health/` JSONL** — sample a few snapshots, confirm no errors, check for any non-OK transitions in the celery-broadcast log. Use the Rigby checklist above.
2. **(3d) Threshold tuning** — if the 4-item readout reads clean, fold the action-threshold doc into `_compute_status()` (any CRIT, WARN-persists-2, hang_age >= 180s).

### Active queue (Chris's call on priority)

3. **(C) UI spinner proxy** — first task: confirm `ChatConversation` (or similar) has the right shape to measure "request received, no assistant response after N min" cheaply.
4. **Optional cosmetic** — Rigby's "PA worker set" filter in the per-worker rollup (truly optional).
5. **Old `docs/topics/` sweep** — 7 Feb-March docs from #2221.
6. **`load_all_agents_advisors.py 149→139`** — cosmetic.

### Deferred infrastructure track (avoid during offline-CI window)

7-12. Same set as Session 1161's deferred track (CONFLICT detector tuning, beat-drift, provenance v2, beat-schedule the regens, learning-bridge audit generator fix, Redis pooling sweep).

### Chris-call-only carryovers (still parked)

13. Decision Command backend cleanup, DaVinci route removal, Mission refresh PR #2190.

---

**Session ledger:** 3 PRs merged (#2269, #2270, #2271). Main clean. JSONL persistence active. Workers restarted. Beat dispatching every 30 min.
