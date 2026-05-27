# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars. Current pinned conversation: `pa-f93d77e34f5d` (set Session 1159; carried into 1160).

## READ THIS SECOND — PA "CONSUME-1-THEN-HANG" IS USUALLY DISK PRESSURE

Memory: `feedback_pa_hang_from_disk_pressure.md`. If the PA worker processes exactly one task and then goes silent, check `df -h /System/Volumes/Data` + `sysctl vm.swapusage` BEFORE deeper Celery debugging. Single-digit GiB free or swap < 2 GiB free → free disk first. Don't restart Docker — `unified-postgres` lives there.

## READ THIS THIRD (NEW Session 1160) — `git show` IS THE FIRST MOVE FOR MTIME MYSTERIES

If you see a cluster of doc mtimes within minutes of each other and wonder "what generated this?", run `git log --since="<timestamp - 1min>" --until="<timestamp + 1min>"` first. Session 1160's "May 25 09:36 batch" mystery resolved instantly via `git show 9d75f78f` — it was Chris's own Session 1143 PR #2197. Future similar questions should start with the git history before invoking Rigby's ops tools.

## READ THIS FOURTH (NEW Session 1161, broadened Session 1162) — WORKER `sys.modules` CACHE ⇒ RESTART

Two restart triggers, one fix. **(1)** Adding a new `@shared_task` to `core/tasks.py` is invisible to running celery workers until they restart — they cache the registered-task list at process import time. Beat dispatches succeed (picks up new `PeriodicTask` rows via `DatabaseScheduler` polling), but workers reject with `Received unregistered task of type '<dotted>'`. **(2)** More broadly (Session 1162 discovery): even when the `@shared_task` itself is unchanged, any helper module the task body imports is cached in the worker's `sys.modules` after first call. Modifying the imported module's code (e.g., a `Command` class the task calls) does NOT propagate to running workers. Both cases need the same restart. Fix: `pkill -9 -f celery; rm -f .celery*.pid; make celery`. Verify with `.venv/bin/celery -A core inspect registered | grep <task_name>` (case 1) or by dispatching a manual call and checking output (case 2). PR-description anti-pattern to avoid: "no `@shared_task` changes — workers don't need restart" — wrong for case 2.

## SOURCE OF TRUTH

Per Session 1144 PR #2208 (canon rebase) + Session 1146 PR #2216 (Runtime Evidence promotion) + Session 1158 (narratives layer) + Session 1159 (EDITING_GUARDRAILS) + Session 1160 (patents README + PR template):

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`).
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts).
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/narratives/`** — 15 subsystem narratives (A–O). Operator-handbook layer.
5. **`docs/narratives/EDITING_GUARDRAILS.md`** — 7-rule editing contract + pre-PR checklist (Session 1160 add).
6. **`docs/patents/README.md`** — 4-workstream + disclosure → narrative cross-link map (Session 1160 add).
7. **`docs/case-studies/`** — historical case studies (Session 1160 added codex-audit + drift-reconciliation table).
8. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution.
9. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
10. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
11. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
12. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
13. **`docs/specs/`** — engineering specs.
14. **Runtime Evidence (auto-generated)** — the 8 `docs/*_AUDIT.md` files. DOC-AUTOGEN per-subsystem runtime evidence. Regenerate with `build_*_audit` mgmt commands.
15. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`**.
- `python scripts/verify_repo_guardrails.py`
- `python manage.py session_provenance --session N`
- `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json`.
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145–1160 ran 100% subject-tagged. Keep the streak.

## NARRATIVE-EDIT PR CHECKLIST (Session 1160)

`.github/PULL_REQUEST_TEMPLATE.md` includes a conditional "Narrative-edit checklist" that PR authors fill out when the PR modifies any file in `docs/narratives/`. The 7-item checkbox list maps 1:1 to `docs/narratives/EDITING_GUARDRAILS.md` rules. Required only when changes touch narratives.

Authoring rule of thumb: if the PR introduces a new rule/process, dogfood the rule on its own diff before opening. The `#2256 → #2257` loop (PR #2256 introduced EDITING_GUARDRAILS and still violated rules #1 + #5 in 5 places) is the cautionary tale captured both in the EDITING_GUARDRAILS source addendum and the Session 1159+1160 handoffs.

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
```

Tested Session 1159 post-Mac-reboot: full stack restart from cold-boot in ~30 s. Clear stale pids first (`rm -f .celery*.pid .daphne.pid`) before `make all`.

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- **PA tool registration needs BOTH daphne AND celery restart.** `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
- **search_docs originating_session filter cache:** `lru_cache(1)` per process. After `build_docs_provenance` regen, restart workers.
- **`process_pa_chat_task` uses `acks_late=False`** (Session 1159 PR #2255). Overrides the global `CELERY_TASK_ACKS_LATE=True` because the global setting + unstable macOS broker conn was producing tasks stuck in `unacked` for an hour.

---

## SESSION 1163 CLOSED — Disclosure L drift correction arc (C-style + B-style) (2026-05-26 → 2026-05-27)

**4 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1163_DISCLOSURE_L_DRIFT_CORRECTION_ARC.md`](docs/handoffs/SESSION_1163_DISCLOSURE_L_DRIFT_CORRECTION_ARC.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2283** | Disclosure L §13 path-move addendum (classes moved `core.py` → `governance.py` + `experiment.py` per commit `fe94c928` 2026-03-09) | `9bf87f4e` |
| **#2284** | `latest_overrides_snapshot` C-style honest interim PA tool + Disclosure L §14 mechanism drift addendum + narrative §6.4 rewrite + row_updated_at nit-fix | `dad9ec84` |
| **#2285** | Narrative §6.4 tool-name drift fix — `ops_tool` → `autopilot_tool` (self-referential dogfood loop captured) | `b99bfa0c` |
| **#2286** | **B-style `FinalAppliedOverrides` per-cycle table** + idempotent backfill + time-travel `at` arg + 90-day Celery beat retention + Disclosure L §14.7 "B-style shipped" + narrative §6.4 lineage table | `636ed6c7` |

**End-to-end verified post-merge:** 2 autopilot cycles ran; `at='2026-05-27T22:05:56+00:00'` (between cycles) correctly returned the older row; no-`at` query correctly returned the newer row. Time-travel selection working against real data (14 knobs populated, real `backlog_governor_level` + `desk_allocation:*` + `goal_allocation:*` keys).

**New persistent artifacts:**
- `FinalAppliedOverrides` Django model + migration 0354 + 90-day retention task + beat schedule entry `purge-finaloverrides-90d` (daily 02:40 MST).
- `autopilot_tool action=latest_overrides_snapshot at='<ISO 8601>'` PA tool action.
- Disclosure L §13 + §14 + §14.7 addenda (§1–§12 byte-identical).
- Narrative §6.4 lineage table (Session 1162 framing → Session 1163 discovery → C-style → B-style).
- New feedback memory `feedback_corpus_walks_surface_mechanism_drift.md` + MEMORY.md index entry.

**Coverage gaps closed:**
1. Disclosure L §5 Component 4 mechanism drift — patent claimed `FinalAppliedOverrides.objects.create(...)` per-cycle; as-built was single-row `SystemConfiguration` overwrite. Now matches patent intent.
2. Narrative §6.4 invalid ORM recipe — corrected to live recipe against new model.
3. Operator ergonomics gap — `latest_overrides_snapshot` tool with `at` arg replaces ad-hoc ORM debugging recipe.
4. Disclosure L §10(g) "for time-series auditability" counsel call — de-escalated from "amendment-to-match-reality" to optional "amendment-to-strengthen."

**New gotchas captured:**
- `cycle_id` mismatch between cycle wrapper (`core.py:2658` generates own `_uuid.uuid4()`) + arbitrator-issued snapshot ID. Minor cleanup candidate; joinability across `FinalAppliedOverrides` ↔ `AutopilotAction` would benefit from shared cycle_id.
- Self-referential dogfood loop continues: PR #2284 introduced a tool surface and got the tool name wrong in its own docs (caught by Rigby's post-merge smoke test, fixed in PR #2285). Same family as Session 1159 #2256 → #2257. Future corrective PRs introducing tool surfaces should invoke the tool against their own docs before merge.

### Session 1162 CLOSED — Narrative triple + PA acks observation completion (2026-05-26)

**8 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1162_NARRATIVE_TRIPLE_AND_PA_ACKS_OBSERVATION_PHASE.md`](docs/handoffs/SESSION_1162_NARRATIVE_TRIPLE_AND_PA_ACKS_OBSERVATION_PHASE.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2274** | `pa_acks_health` (PA-worker-set filter) — `is_pa_relevant` flag | `ffce1494` |
| **#2275** | `pa_acks_health` (Mountain time) — `generated_at_mt` alongside UTC | `25b2198a` |
| **#2276** | **`WORKSPACES_AND_SCOPING.md`** narrative (batch P, 484 lines) | `dc027f4f` |
| **#2277** | docs/INDEX.md regen post-workspace | `0cfaa767` |
| **#2278** | **`INITIATIVES_AND_LIFECYCLE.md`** narrative (batch Q, 724 lines) | `1ba017e3` |
| **#2279** | docs/INDEX.md regen post-initiative | `373148c7` |
| **#2280** | **`SELF_TUNING_AND_EXPERIMENTATION.md`** narrative (batch R, 606 lines, first patent-rooted) | `53879aef` |
| **#2281** | docs/INDEX.md regen post-self-tuning | `1670436d` |

**New persistent artifacts:** three new operator-handbook narratives (~1,814 lines combined) at `docs/narratives/`. Active doc count 904 → 907. New frontmatter pattern: `maps_to_patents` field for patent-rooted narratives.

**Coverage gaps closed:**
1. Workspace concept — scattered across 9 prior narratives, no canonical home → batch P.
2. Initiative entity + lifecycle + non-signal creation paths — companion to SIGNAL_INTELLIGENCE (signal arc) → batch Q.
3. Disclosure L self-tuning experimentation — Session 1161 carryover → batch R.

**Post-merge ops gotcha:** PRs #2274 + #2275 said "no `@shared_task` changes — workers don't need restart" but the worker `sys.modules` cache held the old `Command` class. Discovered when 12:30 CDT auto-fire wrote JSONL without new fields. Memory rule broadened (see READ THIS FOURTH above). Post-restart cadence is fully instrumented.

### Session 1161 CLOSED — PA acks_late watch instrumentation + 30-min cadence

**3 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1161_PA_ACKS_WATCH_INSTRUMENTATION_AND_CADENCE.md`](docs/handoffs/SESSION_1161_PA_ACKS_WATCH_INSTRUMENTATION_AND_CADENCE.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2269** | `pa_acks_health` (A) — `oldest_queued` + `inflight_estimate` ack-behavior proxies | `7244dfdb` |
| **#2270** | `pa_acks_health` (B) — `per_worker` rollup + `worker_last_event_at` heartbeat on hang samples | `77bd18d8` |
| **#2271** | `pa_acks_health` cadence — `build_report()` refactor + every-30-min beat task + JSONL persistence | `6656f193` |

**New persistent artifacts:** new `@shared_task` `core.tasks.capture_pa_acks_health_snapshot`, new beat entry `pa-acks-health-capture` (every 30 min, queue=broadcast), per-day JSONL log at `logs/pa_acks_health/YYYY-MM-DD.jsonl` (gitignored).

**Post-merge ops:** workers restarted to register the new task; full path verified end-to-end (beat → broadcast worker → task → JSONL write). Beat picked up the new `PeriodicTask` row automatically via `DatabaseScheduler` polling — no beat restart needed.

### Session 1160 CLOSED — Session 1158-carryover queue clear + EDITING_GUARDRAILS operational

**8 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1160_QUEUE_CLEAR_AND_GUARDRAILS_OPERATIONAL.md`](docs/handoffs/SESSION_1160_QUEUE_CLEAR_AND_GUARDRAILS_OPERATIONAL.md). Key PRs: #2259-#2264 (queue clear + EDITING_GUARDRAILS), #2266-#2267 (pa_acks_health scaffolding).

### Previous closed work still relevant for context

- **Session 1159** — PA acks_late fix + narrative B/C/D iterations + EDITING_GUARDRAILS contract. 3 PRs.
- **Session 1158** — 15 subsystem narratives shipped. Template v1-LOCKED. 8 PRs.

---

## 🚨 ACTIVE ISSUES carrying into Session 1164

### 1. GitHub Actions billing — still down

Same annotation as Sessions 1149-1163. Multi-day outage until Chris funds account.

**Self-merge protocol during outage** (Sessions 1149 + 1150 + 1158-1163 pattern):

For every PR, run local mirrors before push:
```bash
.venv/bin/python scripts/verify_repo_guardrails.py --inventory-advisory
.venv/bin/python tools/check_direct_llm_calls.py --root . --whitelist .ci/llm_whitelist.txt --warn-only
```

Self-merge with bypass requires:
1. Both local mirrors run.
2. Only failure is the pre-existing `celery-beat-schedule` CONFLICT.
3. Merge commit body documents the bypass with both `billing outage` and `pre-existing CONFLICT` named.
4. PR scope is documentation or low-risk verifier baselines (no production code changes).
5. Production-code changes need explicit per-PR Chris-authorization in-session (Session 1159 PR #2255 + Session 1163 PR #2286 precedent).

### 2. `celery-beat-schedule` CONFLICT — detector signal pending

Session 1157 PR #2243 closed the code-level footgun. Context-kit CONFLICT signal still flags because its detector heuristic is keyword/path-based across ~36 files. Queued for Session 1164+.

### 3. PA `acks_late=False` observation phase — FULLY INSTRUMENTED

Sessions 1161 + 1162 together closed the instrumentation gap. The watch produces durable JSONL data with all expected fields. Session 1163 entry-check pattern carries forward.

- `logs/pa_acks_health/YYYY-MM-DD.jsonl` grows by ~48 lines/day (`*/30` cadence).
- Each snapshot carries: UTC + MT timestamps, queue depth, per-worker rollup (with `is_pa_relevant` flag), `oldest_queued`, `inflight_estimate`, `slow_tasks` list, `hang_signature` samples (with `worker_last_event_at` heartbeat).
- WARN-level log line fires in celery-broadcast log whenever `status != OK`.

**Session 1163 close state (2026-05-27):** cadence ran clean through both Session 1163 daphne+celery restarts (one mid-day, one late-afternoon). Local rolled into 2026-05-27 during B-style verification. 24h+ of clean data is now available — **threshold tuning (item 6 below) becomes actionable as of Session 1164.**

**What Session 1164 should check on entry:**
- `wc -l logs/pa_acks_health/*.jsonl` — confirm overnight growth without errors.
- `grep "pa_acks_health" celery-broadcast.log | grep -v "succeeded\|received"` — any WARN lines?
- 24h+ of clean data should now exist; threshold tuning is actionable.

---

## SESSION 1164 — CURRENT ENTRY POINT

### FIRST THING this session

**Check the PA stack is healthy.** Run `platform_config_tool overview` through Rigby to confirm `service_context: local`. PA conversation pinned in `tools/pa_local.sh`: `pa-f93d77e34f5d` (carried from Sessions 1159-1163 — update the wrapper if Chris opened a new conversation).

**Disk check:** `df -h /System/Volumes/Data`. If < 10 GiB free, run cleanup playbook from `feedback_pa_hang_from_disk_pressure.md`.

**JSONL cadence check (continued from Session 1161-1163):** `wc -l logs/pa_acks_health/*.jsonl` should now show ~48 lines per full day across at least two days. `grep "pa_acks_health" celery-broadcast.log | grep -v "succeeded\|received"` should be empty unless a status changed. 24h+ of clean data should be available — threshold tuning (item 6) is actionable.

**Session 1163 B-style verification check:** `autopilot_tool action=latest_overrides_snapshot` should return `found: true` with `storage.table=core_final_applied_overrides`. The arbitrator beat cycle runs roughly every 10 min; if `found=false` past the first cycle of the session, check `celery-beat.log` for errors and `core/celery.py` for the cycle cadence — see Session 1163 handoff §"Carryover" item #2 (cycle_id joinability) for context.

### Queue is clear; Session 1163 closed the four self-tuning follow-on items (#3 → shipped as B + counsel call optional, #4 → shipped as §13, #5 still queued, #6 → shipped as autopilot_tool action)

No items are blocked on Chris-decision at session open. Chris can pick any of the active items below.

### Observation-mode items (may not produce a PR)

1. **JSONL review** — sample a handful of snapshots, confirm no errors. The Session 1161 cadence wrapper runs every 30 min and emits WARN log lines on non-OK transitions.
2. **EDITING_GUARDRAILS opportunistic rollout** to narratives A / E / F / G / H / I / J / K / M / N / O. Pick up when next editing each narrative; not a batch.

### Session 1163 small follow-on candidates (clean ~15-30-min PR each)

3. **Legacy `SystemConfiguration(key='policy_arbitrator_snapshot')` row cleanup** — small migration to hard-delete the legacy row after one or more new-model cycles have been observed. Per Rigby's Session 1163 "Pick (b) backfill + (c) cleanup later" recommendation. Local has 2 new-model cycles observed; prod has 0 yet (gated on next Railway deploy + at least one cycle there). Single-migration PR, no model/code changes. Doc tweak: narrative §6.4 lineage table can mention "legacy row removed" once shipped.

4. **`cycle_id` joinability fix** — make `_policy_policy_arbitrator` in `core.py:2658` accept the run-cycle's `cycle_id` instead of generating its own `_uuid.uuid4()`. Single-file edit. Makes `FinalAppliedOverrides.cycle_id` joinable against `AutopilotAction` records emitted in the same cycle. Test: extend `test_policy_arbitrator_latest_snapshot.py` to assert the `cycle_id` matches the run-cycle's `cycle_id` end-to-end.

5. **Opportunistic narrative §4 + §5 cleanup of stale `FinalAppliedOverrides` mentions** — §6.4 lineage table is the canonical correction source, but §4 (operational benefits "Time-travel auditability") and §5 (current state snapshot — "FinalAppliedOverrides. Treat the governance.py write site as canonical") still describe the pre-Session-1163 framing. Wait for the next time someone touches those sections; do not batch-edit.

### Carryover small follow-ons from Session 1162 (still queued)

6. **Threshold tuning** — fold `pa_acks_health` action thresholds into `_compute_status()`. Now actionable per Session 1163 close-state (24h+ clean JSONL).
   - WARN on queue depth ≥ 5 (currently ≥ 1).
   - CRIT "no workers sustained" — explicit sustain window (≥ 2 consecutive snapshots).
   - CRIT queue depth ≥ 20 — pair with second condition (workers < 2 OR oldest queued age > 120s).
   - **WARN persists 2 consecutive snapshots** → escalate. Net new logic (requires comparing adjacent JSONL snapshots).

7. **STRATEGY correction PR** — `WORKSPACES_AND_SCOPING.md` §6.1 + §6.2 flagged two STRATEGY narrative drifts (`LLMCallLog.workspace` FK + fleet "scoped workspace bootstrap" both named as implemented but aren't). Convert "is" → "planned / not yet implemented" on both; link back to the workspace narrative §6.

8. **TRIAGE policy PR** — `INITIATIVES_AND_LIFECYCLE.md` §6.2. Rigby's verdict: real gap (operational hygiene), not bug. Two conservative options:
   - opt-in archive rule (TRIAGE older than N days *only if* no action items + no stage docs + low confidence → ARCHIVED)
   - review queue surfacing (TRIAGE older than N days → `HumanAttentionItem`)

### Larger follow-on candidates

9. **Per-module `ops_autopilot` narratives** — `SELF_TUNING_AND_EXPERIMENTATION.md` §6.3 explicitly scoped out the other 7 files (budget/engagement/impact/intelligence/remediation/revenue/verification). Each is a future-narrative candidate; pick one. Patent-rooted pattern applies where relevant (budget → disclosures J + K). Rigby's verdict: separate per-module narratives, not an umbrella.

10. **(C) UI spinner proxy** — confirm `ChatConversation` (or similar) shape first; should be cheap to query for "request received but no assistant response after N minutes." Then implement as `pa_acks_health` field or a separate tool action.

11. **Counsel-side amendment to Disclosure L claim §10(g)** — now optional per Session 1163 §14.7 (de-escalated from "amendment-to-match-reality" to "amendment-to-strengthen"). Not a code change; counsel call.

### Active queue (Chris's call on priority)

12. **Old `docs/topics/` sweep** — 7 Feb-March docs deferred from Session 1147 #2221.
13. **Cosmetic `load_all_agents_advisors.py 149→139` fix** — queued from Session 1149.

### Deferred infrastructure track (avoid during offline-CI window)

14. **`celery-beat-schedule` CONFLICT — detector tuning** (preferred) or 36-file token-pattern phrasing sweep (fallback).
15. **Pre-existing PeriodicTask drift** (now 81 DB rows vs 79 entries in `core/celery.py` — Session 1163 added 1 beat entry `purge-finaloverrides-90d`). Folds into #14.
16. **`exists_on_disk: false` flag** in `_provenance.json` — 326 dead paths. Schema bump v1 → v2.
17. **Beat-schedule the regens** — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
18. **Fix `build_learning_bridge_audit.py` generator** — falsely flags "ABC unused".
19. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern from PR #2201.

### Chris-call-only carryovers (still parked)

20. **Decision Command backend cleanup** — 5 Python files (regressed feature).
21. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
22. **Mission refresh PR #2190** — preserved branch.

### Cross-session lessons (Sessions 1145–1163)

- **Recon before sweep.** Multiple back-to-back sessions where mid-recon findings flipped the PR plan.
- **Narratives become canon; topic docs get corrected to match** (1158).
- **`docs/*_AUDIT.md` files may be DOC-AUTOGEN** — check line 1 for marker before banner sweep (1146).
- **`build_*_audit` generators can lag reality** — fix the generator, not the output (1146).
- **Bypass-merging during a CI outage is workable IF disciplined** (1150).
- **"One mechanical batch then stop" applies even when batches are easy** (1150).
- **Cited-by-narrative is a triage signal** for the 778 not-HIGH handoffs (1158).
- **Disk + swap pressure mimics Celery bugs** — check disk first (1158).
- **`unified-postgres` lives in Docker** — don't `docker system prune` or restart Docker as a whole (1158).
- **EDITING_GUARDRAILS is load-bearing** for any narrative edit (1159).
- **Self-referential dogfood.** A guardrails-introducing PR can still violate its own rules — `#2256 → #2257` (1159). PR-template checklist closes the loop (1160).
- **Production-code bypass needs explicit per-PR Chris auth** (1159).
- **Stack restart playbook works in ~30 s** post-Mac-reboot (1159).
- **`git show` first for mtime mysteries** — before invoking ops tools, `git log --since/--until <timestamp>` resolves nearly every case (1160).
- **Symmetric cross-references prevent half-resolved navigation** — pair `maps_to_*` frontmatter with reverse "Related X" sections (1160).
- **Append-only edits are safer than restructure for high-trust documents** — PR #2263 added cross-link sections at the end of 6 narratives without touching milestone tables or vocabulary sections (1160).
- **Cadence wrappers belong in beat, not cron** (1161). `DatabaseScheduler` polls — adding a `PeriodicTask` row via `add_critical_celery_tasks` is the canonical path. Beat picks up new rows without restart.
- **New `@shared_task` decorators are invisible to running workers** (1161) until they restart. Generalized further Session 1162: *any module imported by a task body* is cached in `sys.modules` and needs the same restart even when the `@shared_task` is unchanged. Fix: `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
- **"Stop and watch" is its own ship-able milestone** (1161). Three sequential PRs that move from "snapshot tool" to "cadenced observation surface" can complete a session arc without the analytics layer on top. Threshold tuning waits for the data.
- **NEW (1162)** **The narrative-triple shipping pattern works at scale.** Code survey → draft → split-paste Rigby review → apply fixes → merge ran cleanly three times in one session. PA chat payload limit (~24 KB) forces multi-message review for any narrative >~24 KB; workable, not blocking.
- **NEW (1162)** **Patent-rooted narratives are a viable corpus pattern.** Frontmatter `maps_to_patents` field creates bidirectional cross-links between frozen IP artifacts and current-state operator-handbook docs. Patent text stays frozen (Rigby's verdict: addendum-only, never inline rewrite); narrative stays current; path drift handled via the patent's addendum section, not by editing the narrative away from the disclosure.
- **NEW (1162)** **PR-description anti-pattern to avoid:** "no `@shared_task` changes — workers don't need restart." Wrong for the case where the PR modifies a module that a task body imports. Correct phrasing: "Modifies [Command class] imported by [task_name] task body — celery workers need restart for scheduled fires to pick up the change."
- **NEW (1162)** **Anti-duplication discipline against companion narratives works.** `INITIATIVES_AND_LIFECYCLE.md` §8 punted 7 things to `SIGNAL_INTELLIGENCE.md`. Rigby's verdict: "clean and correct, not over-claiming." Model for future companion narratives where two docs cover related arcs.
- **NEW (1162)** **Open Questions are a triage surface, not just gap markers.** Each §6 item should resolve to a Rigby-stated verdict ("deliberate" / "real gap" / "known operational risk" / "design decision"), not stay as "Rigby's call" indefinitely. Three narratives x 5 open questions each = 15 verdicts captured this session; this triage is part of the review pass, not separate.
- **NEW (1163)** **The corpus walk IS the deliverable.** Chris's in-session value statement after Session 1163's `FinalAppliedOverrides` mechanism-drift discovery: *"This is why it's so important for us to go through all of the /docs/ like we have been doing, that's how we surface these issues!!"* Saved as feedback memory `feedback_corpus_walks_surface_mechanism_drift.md`. When mid-recon finds a doc-says-X-but-code-does-Y mismatch, STOP and route options through Rigby. Don't quietly bridge gaps by implementing what the doc said. Honest pattern: ship the C-style honest-tool PR + frozen-artifact addendum + queue the B-style correct fix with design Qs named.
- **NEW (1163)** **C-style honest interim ≠ A-style fake.** A C-style PR ships an honest small surface that explicitly documents what it does NOT support (storage block with `mechanism` field naming the limitation). An A-style PR ships a tool that pretends to support something it doesn't (e.g., accepts a `time` arg but silently ignores it). Rigby's verdict: "A is unacceptable — implicitly lies." Always C, never A.
- **NEW (1163)** **Frozen-artifact addenda scale across multiple discoveries.** Disclosure L gained §13 + §14 + §14.7 in a single session without editing §1–§12 once. Future patent disclosures with similar drift can follow the same pattern: append §N.x subsections, never inline-edit the original body. Each subsection records the lineage from disclosure-time intent → as-built state → corrective fix.
- **NEW (1163)** **Self-referential dogfood loop continues — corrective PRs can introduce their own drift.** PR #2284 corrected the narrative §6.4 to be honest about `FinalAppliedOverrides` not existing, AND in the correction misnamed the tool namespace (`ops_tool` instead of `autopilot_tool`). Caught by Rigby's post-merge smoke test, fixed in PR #2285. Same family as Session 1159 #2256 → #2257. Rule extension to the 00-START dogfood line: *"if your PR introduces a tool surface, invoke the tool against your own docs before merge."*
- **NEW (1163)** **Hand-written migrations beat auto-generated when scope matters.** `makemigrations` produced a 606-line migration including unrelated `AlterField` ops across multiple subsystems. The focused hand-written one was 168 lines, only the new model + index + idempotent backfill. For scoped subsystem PRs, prefer hand-written migrations — the auto-generated version pulls in every subsystem's pending drift as scope-creep.
- **NEW (1163)** **Idempotent backfills are cheap insurance.** The Session 1163 migration's `if FinalAppliedOverrides.objects.exists(): return` check makes re-running the migration safe and turns the backfill into a one-shot no-op if rows already exist. Per Rigby: "Pick (b) backfill + (c) cleanup later" is the safe pattern — never leave a post-deploy data gap, never foreclose the rollback path. The legacy source row stays put until ≥ 1 new-model cycle is observed.

---

## RECENT SESSION ARCS

- **Session 1163** — Disclosure L drift correction arc (path-move addendum + C-style honest tool + tool-name dogfood loop + B-style FinalAppliedOverrides per-cycle table). 4 PRs merged.
- **Session 1162** — narrative triple (workspace + initiative + self-tuning) + PA acks observation completion. 8 PRs merged.
- **Session 1161** — PA acks_late watch instrumentation + 30-min cadence. 3 PRs merged.
- **Session 1160** — 1158-carryover queue clear + EDITING_GUARDRAILS operational. 8 PRs merged.
- **Session 1159** — PA acks_late fix + narrative B/C/D iterations + EDITING_GUARDRAILS contract. 3 PRs merged.
- **Session 1158** — corpus-narrative program: 15 narratives + drift sweep + cited-handoff frontmatter + reports/patents recon. 8 PRs merged.
- **Session 1157** — celery-beat-schedule cleanup option A. 1 PR merged (bypass mode).
- **Session 1156** — P3.5 round 9 (FINAL) + P3.5 track CLOSE. 1 PR merged.
- **Session 1155** — P3.5 round 8. 1 PR merged.
- **Session 1154** — P3.5 round 7. 1 PR merged.
- **Session 1153** — P3.5 round 6. 1 PR merged.
- **Session 1152** — P3.5 round 5. 1 PR merged.
- **Session 1151** — P3.5 round 4. 1 PR merged.
- **Session 1150** — Session 1149 merge wave + P3.5 round 3. 4 PRs merged.
- **Session 1149** — SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes. 3 PRs.
- **Earlier:** see `docs/handoffs/CURRENT.md`.
