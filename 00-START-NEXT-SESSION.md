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

## READ THIS FOURTH (NEW Session 1161) — NEW `@shared_task` ⇒ WORKER RESTART

Adding a new `@shared_task` to `core/tasks.py` is invisible to running celery workers until they restart — they cache the registered-task list at process import time. Beat dispatches succeed (it picks up new `PeriodicTask` rows via `DatabaseScheduler` polling), but workers reject with `Received unregistered task of type '<dotted.task.name>'`. Same root cause as the existing PA-tool-registration rule, generalized. Fix: `pkill -9 -f celery; rm -f .celery*.pid; make celery`. Verify with `.venv/bin/celery -A core inspect registered | grep <task_name>`.

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

## SESSION 1161 CLOSED — PA acks_late watch instrumentation + 30-min cadence (2026-05-26)

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

## 🚨 ACTIVE ISSUES carrying into Session 1162

### 1. GitHub Actions billing — still down

Same annotation as Sessions 1149-1161. Multi-day outage until Chris funds account.

**Self-merge protocol during outage** (Sessions 1149 + 1150 + 1158-1161 pattern):

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
5. Production-code changes need explicit per-PR Chris-authorization in-session (Session 1159 PR #2255 precedent).

### 2. `celery-beat-schedule` CONFLICT — detector signal pending

Session 1157 PR #2243 closed the code-level footgun. Context-kit CONFLICT signal still flags because its detector heuristic is keyword/path-based across ~36 files. Queued for Session 1162+.

### 3. PA `acks_late=False` 24-48h watch — NOW INSTRUMENTED, observation phase

Session 1161 closed the instrumentation gap. The watch now produces durable JSONL data:

- `logs/pa_acks_health/YYYY-MM-DD.jsonl` grows by ~48 lines/day (`*/30` cadence).
- WARN-level log line fires in celery-broadcast log whenever `status != OK`.
- All metrics in place: queue depth, oldest_queued, inflight_estimate, per_worker rollup, worker_last_event_at on hang samples.

What Session 1162 should check on entry:
- `wc -l logs/pa_acks_health/*.jsonl` — confirm growth without errors.
- `grep "pa_acks_health" celery-broadcast.log | grep -v "succeeded"` — any WARN lines?
- If 24+ hours of clean data exists, **threshold tuning (item 3d below) becomes actionable.**

---

## SESSION 1162 — CURRENT ENTRY POINT

### FIRST THING this session

**Check the PA stack is healthy.** Run `platform_config_tool overview` through Rigby to confirm `service_context: local`. PA conversation pinned in `tools/pa_local.sh`: `pa-f93d77e34f5d` (carried from Sessions 1159-1161 — update the wrapper if Chris opened a new conversation).

**Disk check:** `df -h /System/Volumes/Data`. If < 10 GiB free, run cleanup playbook from `feedback_pa_hang_from_disk_pressure.md`.

**JSONL cadence check (new this session):** `wc -l logs/pa_acks_health/*.jsonl` should show ~48 lines per full day. `grep "pa_acks_health" celery-broadcast.log | grep -v succeeded` should be empty unless a status changed.

### Queue is clear of Session 1158-1160 carryovers; Session 1161 closed the PA instrumentation gap

No items are blocked on Chris-decision at session open. Chris can pick any of the active items below.

### Observation-mode items (may not produce a PR)

1. **JSONL review** — sample a handful of snapshots, confirm no errors. The Session 1161 cadence wrapper runs every 30 min and emits WARN log lines on non-OK transitions.
2. **EDITING_GUARDRAILS opportunistic rollout** to narratives A / E / F / G / H / I / J / K / L / M / N / O. Pick up when next editing each narrative; not a batch.
3. **Disclosure L narrative coverage gap.** Self-tuning experimentation lacks a Session 1158 narrative. Fold into BODY_SYSTEMS or CONTENT_PIPELINE, or write a new narrative when the subsystem matures.

### `pa_acks_health` follow-ons — UPDATED after Session 1161

Sessions 1160-1161 closed (A) and (B). What remains:

3c. **(C) UI spinner symptom proxy** — chat requests with no assistant response recorded within N minutes (via `ChatConversation` rows). Rigby deferred this in Session 1161 pending confirmation that `ChatConversation` (or similar) has the right shape to measure it cheaply.

3d. **Threshold tuning** — NOW ACTIONABLE if 24+ hours of cadence data exists. The action thresholds (per Rigby's Session 1161 ranking, documented in the Session 1161 handoff):
   - WARN on queue depth ≥ 5 (currently ≥ 1).
   - CRIT "no workers sustained" — explicit sustain window (≥ 2 consecutive snapshots).
   - CRIT queue depth ≥ 20 — pair with second condition (workers < 2 OR oldest queued age > 120s).
   - Any hang_age ≥ 180s → CRIT (currently 180s already triggers CRIT via `_CRIT_HANG_AGE_SEC`).
   - **WARN persists 2 consecutive snapshots** → escalate. This one requires comparing adjacent JSONL snapshots — net new logic.

3e. **Optional cosmetic** — Rigby's "PA worker set" filter on the per-worker rollup. Truly optional; skipped from Session 1161 intentionally.

3f. **Timezone clarity** — JSONL records currently UTC-only. If operator readability matters during the 48h watch, add `generated_at_mt` (Mountain time string) to `build_report()`. Single line. Filed as non-blocker by Rigby Session 1161.

### Active queue (Chris's call on priority)

4. **Old `docs/topics/` sweep** — 7 Feb-March docs deferred from Session 1147 #2221.
5. **Cosmetic `load_all_agents_advisors.py 149→139` fix** — queued from Session 1149.

### Deferred infrastructure track (avoid during offline-CI window)

6. **`celery-beat-schedule` CONFLICT — detector tuning** (preferred) or 36-file token-pattern phrasing sweep (fallback).
7. **Pre-existing PeriodicTask drift** (now 81 DB rows vs 78 entries in `core/celery.py` after Session 1161 added one). Folds into #6.
8. **`exists_on_disk: false` flag** in `_provenance.json` — 326 dead paths. Schema bump v1 → v2.
9. **Beat-schedule the regens** — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
10. **Fix `build_learning_bridge_audit.py` generator** — falsely flags "ABC unused".
11. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern from PR #2201.

### Chris-call-only carryovers (still parked)

12. **Decision Command backend cleanup** — 5 Python files (regressed feature).
13. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
14. **Mission refresh PR #2190** — preserved branch.

### Cross-session lessons (Sessions 1145–1161)

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
- **NEW (1161)** **Cadence wrappers belong in beat, not cron.** `DatabaseScheduler` polls — adding a `PeriodicTask` row via `add_critical_celery_tasks` is the canonical path. Beat picks up new rows without restart.
- **NEW (1161)** **New `@shared_task` decorators are invisible to running workers** until they restart. Generalizes the existing PA-tool-registration restart rule to any task addition. Fix: `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
- **NEW (1161)** **"Stop and watch" is its own ship-able milestone.** Three sequential PRs that move from "snapshot tool" to "cadenced observation surface" can complete a session arc without the analytics layer on top. Threshold tuning waits for the data.

---

## RECENT SESSION ARCS

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
