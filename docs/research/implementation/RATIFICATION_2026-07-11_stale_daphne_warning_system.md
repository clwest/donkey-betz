---
title: "Stale-Daphne / Stale-Celery Warning System Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2759
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (design → implementation) + Chris joint-recommend D-verdict
scope: net-new operational infrastructure (codifies 3-incident class regression)
precedent_incidents:
  - S2755 (I-0303 Phase 2 merge; view-layer code silent-stale for hours until S2758 diagnosis)
  - S2756 (I-0303 Phase 3 REPORT-ONLY merge; same class)
  - S2757 (I-0303 Phase 3 BATCH-FIX first-pass merge; same class)
ratified_documents:
  - Makefile (amended — `recycle-all` target added; aliases `restart`; S2759-explicit docstring)
  - core/services/td_handlers_ops.py (amended — `_ops_version` extended with staleness detection; `_compute_process_staleness` helper method added)
  - core/services/pa_tool_schemas.py (amended — ops_tool.version description extended for staleness verdict fields)
  - core/tasks_beat_health.py (amended — `check_process_staleness` Beat task added)
  - core/celery.py (amended — `check-process-staleness` Beat schedule entry added at crontab minute='*/30')
  - tests/security/test_process_staleness_detection.py (new — 10 tests, 190s runtime)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2759 — Rigby design SIGN turn 1 (pre-code): PASS on F1-F6 with 3 refinements (F1 hard-kill + print stopped processes; F2 include head_commit_sha; F4 broaden trigger to ASGI-served surfaces + core/urls.py + asgi.py + middleware + auth/permission layer)
  - S2759 — Rigby implementation SIGN turn 1 (post-code): PASS on F1-F6 clean (no edits)
  - S2759 — Live E2E verification (post make recycle-all): ops_tool.version returned staleness_verdict=FRESH with all 6 processes (Daphne + 5 Celery workers) reporting started_before_head_commit=false; head_commit_sha=fd21d4bae621a0b0b6a265350a7d5bae43c1773b
frozen: true
memory_rule_update: feedback_local_truth_no_production.md (extended with S2759 codification — make recycle-all as canonical deploy step; ASGI + Celery trigger list; ops_tool.version freshness check at close; precedent block naming S2755/S2756/S2757 as 3-incident class)
test_results:
  local_test_count: 10
  local_test_pass_rate: "10/10"
  local_test_runtime_seconds: 190
---

# Stale-Daphne / Stale-Celery Warning System Ratification Record

Frozen canonical record of Chris's ratification of the S2759 stale-process detection + warning system on 2026-07-11. Introduced to codify the 3-incident class regression that silently affected S2755 → S2756 → S2757 view-layer close-ceremony merges. Append-only; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** net-new operational infrastructure. Not an arc phase-close.
- **Precedent (3-incident class):** S2755 Phase 2 substrate merge, S2756 Phase 3 REPORT-ONLY merge, and S2757 Phase 3 BATCH-FIX first-pass merge — all three shipped view-layer code changes to `core/views_personal_assistant.py` and `core/views/agents.py` that DID NOT actually load in the running Daphne process. Daphne had been running since Jun 30 (~11 days) and held cached Python module state pre-dating all three merges. Only S2758's ops_tool.tenant_boundary_violations tool E2E finding + S2759 empirical diagnosis surfaced this silent regression.
- **Ratifier:** Chris (D-verdict against joint Claude+Rigby recommendation)

---

## §2. Root Cause Analysis (from S2759 empirical diagnosis)

**Symptom:** S2758 tool's first live query returned a `process_pa_chat_task / missing_acting_identity` OpsRunEvent finding for conversation_id = the S2758 session pin. Header wasn't propagating despite S2757 BATCH-FIX having converted the dispatch site to `apply_async_with_actor`.

**Empirical proof of stale Daphne:**

| Test | Dispatch path | Result |
|---|---|---|
| 1 | Shell-based `apply_async_with_actor` (fresh Python interpreter) | 0 envelopes emitted; header propagated correctly |
| 2 | HTTP dispatch via stale Daphne (`bash tools/pa_local.sh`) | `missing_acting_identity` envelope emitted (reproduced 4×) |
| 3 | HTTP dispatch after `make stop && make start` (Daphne bounced) | 0 envelopes emitted; header propagated correctly |

**Ps confirmation:** Daphne PID 70370 started `Tue Jun 30 14:36:20 2026` — 11 days before the S2755-S2757 close-ceremonies that changed `views_personal_assistant.py`. Every close-ceremony ran `make celery-recycle` (which bounces Celery workers only), never `make restart` or the equivalent that would have bounced Daphne.

**Root cause verdict:** `make celery-recycle` is NOT the full local "deploy" step — it does not touch Daphne's cached module imports. View-layer code changes require a Daphne bounce to load.

---

## §3. Ratified Deliverables

### §3.1 `make recycle-all` Makefile target

Aliases the existing `make restart` with S2759-explicit naming and docstring. Ordering matches the underlying restart target: `make stop` → `make celery-stop` → `make start` → `make celery`. `make restart` preserved for backwards-compat.

Placement: `Makefile:80-91` (immediately after `restart:`).

**Naming rationale:** `recycle-all` parallels the existing `celery-recycle` naming operators already know. Discoverable in `make help` output alongside other recycle-family targets.

**Fix path from staleness verdicts:** any `ops_tool.version` response with `staleness_verdict != 'FRESH'` returns `staleness_fix` pointing at `make recycle-all`. See §3.2.

### §3.2 `ops_tool.version` staleness surface extension

`_ops_version(...)` (core/services/td_handlers_ops.py) now includes staleness detection alongside the existing build/deploy metadata.

**New response fields:**

- `staleness_verdict`: `'FRESH'` / `'STALE_DAPHNE'` / `'STALE_CELERY'` / `'STALE_BOTH'` / `'UNKNOWN'`
- `head_commit_sha`: full 40-char SHA of git HEAD (Rigby F2 refinement — unambiguous debugging)
- `head_commit_timestamp`: iso-8601 of HEAD commit
- `daphne_pid`, `daphne_pid_age_seconds`, `daphne_started_before_head_commit`
- `celery_workers_status`: list of dicts `{hostname, pid, pid_age_seconds, started_before_head_commit}` — one per running worker
- `staleness_fix`: helpful sentence pointing at `make recycle-all` (present ONLY when verdict != FRESH)
- `staleness_error`: fail-soft explanation string when verdict is UNKNOWN

**Threshold rule (Rigby F2):** deterministic — a process is stale iff its `create_time` (unix ts) is strictly less than the git HEAD commit timestamp. No arbitrary "older than N hours" heuristic. Directly answers "did this process load the code I just merged?"

**Process discovery via psutil.** Initial implementation used `subprocess.check_output(['ps', '-eo', 'pid,etimes,command'])` but BSD ps (macOS default) rejected `etimes` with non-zero exit status. `psutil==7.0.0` was already in requirements.txt; `psutil.process_iter(['pid', 'name', 'cmdline', 'create_time'])` is cross-platform and returns `create_time` as a Unix timestamp for direct comparison. No format-string parsing.

**Fail-soft discipline:** any exception during staleness computation is caught at the `_ops_version` outer layer and yields `staleness_verdict='UNKNOWN'` + `staleness_error='<explanation>'`. `ops_tool.version` MUST remain useful even when the freshness signal is unavailable.

**Grep-row exclusion:** naive substring matching on `celery.*worker` would false-positive on shell pipes like `ps aux | grep celery`. Explicit `'grep' not in cmd` filter (test-backed).

### §3.3 `check_process_staleness` Beat task

`core/tasks_beat_health.py` — new `@shared_task(name='check_process_staleness', queue='default', ignore_result=True, soft_time_limit=30)`.

**Cadence:** every 30 min via `crontab(minute='*/30')`. Registered in `core/celery.py:868` beat schedule alongside `check-beat-health`.

**Behavior:**
- FRESH verdict → returns `{'verdict': 'FRESH'}`, does NOT emit OpsRunEvent
- STALE_DAPHNE / STALE_CELERY / STALE_BOTH → emits `OpsRunEvent(label='staleness_warning', event_type='step_fail', detail={source, verdict, head_commit_sha, head_commit_timestamp, daphne_pid, daphne_pid_age_seconds, daphne_started_before_head_commit, celery_workers_status, fix})`; returns `{'verdict': <stale>, 'ops_run_event_emitted': True, 'head_commit_sha': ...}`
- UNKNOWN → returns `{'verdict': 'UNKNOWN'}`, does NOT emit OpsRunEvent
- Any exception → caught + returns `{'skipped': 'compute_error:<class>'}`; never raises

**Purpose:** the passive "nobody remembered to check" defense in depth. Complements the live `ops_tool.version` verdict which is the active operator check.

### §3.4 Test suite — 10 tests, 190s runtime, 10/10 passing

`tests/security/test_process_staleness_detection.py` (new file):

- `test_verdict_fresh_when_all_processes_post_head_commit` — FRESH path
- `test_verdict_stale_daphne_when_only_daphne_pre_head` — Daphne-only stale (the exact S2755/S2756/S2757 signature)
- `test_verdict_stale_celery_when_only_workers_pre_head` — inverse Celery-only stale
- `test_verdict_stale_both_when_daphne_and_workers_pre_head` — both stale
- `test_verdict_unknown_when_git_metadata_unavailable` — fail-soft on missing git
- `test_verdict_unknown_when_no_processes_found` — no processes running
- `test_grep_matching_celery_word_is_excluded` — grep-row false-positive guard
- `test_beat_task_returns_fresh_verdict_no_ops_run_event` — Beat FRESH path no-op
- `test_beat_task_emits_ops_run_event_on_stale_verdict` — Beat stale emits envelope
- `test_beat_task_soft_fails_on_compute_exception` — Beat monitor-failure-must-not-crashloop

Test approach: monkey-patch `subprocess.check_output` for git metadata + inject synthetic `psutil.process_iter` returning fake `Process` info dicts. No live process dependency.

### §3.5 Schema description update

`core/services/pa_tool_schemas.py` — extended `ops_tool.version` action description with the new staleness verdict language and `make recycle-all` fix pointer.

---

## §4. Rigby SIGN Cycle

Two SIGN turns.

### §4.1 Design SIGN turn 1 (pre-code)

F1–F6 all PASS with 3 refinements:

- **F1 refinement:** `make stop` must hard-kill Daphne if graceful kill fails + print what was actually stopped. Already implemented in the existing `stop:` target.
- **F2 refinement:** include `head_commit_sha` in the response (cheap; unambiguous debugging).
- **F4 refinement:** broaden the memory-rule trigger from `views/*.py` + `services/*.py` + `tasks*.py` to cover the actual failure surface — `core/views/**`, `core/services/**`, `core/urls.py`, `asgi.py`, middleware, auth/permission layer, or anything imported by the request path.

Q leans confirmed: QA=Option C (Beat + memory-rule) · QB=separate verdicts · QC=(a) process started_before_head_commit_time · QD=`recycle-all` · QE=30 min · QF=scoped trigger.

### §4.2 Implementation SIGN turn 1 (post-code)

F1–F6 all PASS clean, no edits requested. Rigby's summary: *"PASS overall. I'm good to jointly recommend-to-Chris for D-verdict."*

Post-code E2E verification (Rigby-executed after `make recycle-all`):

- `staleness_verdict: FRESH`
- `head_commit_sha: fd21d4bae621a0b0b6a265350a7d5bae43c1773b`
- Daphne pid_age_seconds=27, `started_before_head_commit: false`
- 5 Celery workers, all `started_before_head_commit: false`

---

## §5. Chris D-Verdict

**Verdict:** **APPROVED** ("approved, ship it" — S2759, 2026-07-11)

Zero unresolved menus routed per S2753 agree-first rule. Two ratification points: original combined shape "lets do it" + final ship "approved, ship it".

**Effect:** Stale-Daphne warning system shipped. `make recycle-all` canonical; `ops_tool.version` staleness verdict live via `_compute_process_staleness`; Beat task registered at crontab `*/30`. Memory rule `feedback_local_truth_no_production` extended with S2759 codification.

---

## §6. Session Timing + Cost

- Session open: 2026-07-11 (S2759 continued conversation post-S2758 close)
- First Rigby dispatch: after fresh pin mint (`pa-58888db8e1d148ca`)
- Rigby SIGN turns: 2 (pre-code + post-code) — all PASS
- Chris D-verdicts: 2 (combined shape approve / final ship)
- Test suite: 2 runs during authoring (190s each; first run had NameError on missing `import os` + KeyError on beat-task test — both fixed on second run)
- E2E verification: 2 `make recycle-all` invocations (first failed on BSD `ps -eo etimes`; migrated to psutil; second passed cleanly)
- Total local runtime: ~2 hours (efficient — single-turn SIGN convergence per axis; empirical debugging pivoted the S2759 scope mid-session)

---

## §7. Retroactive Impact + Follow-Up Backlog

**Retroactive impact of the 3-incident class:** S2755, S2756, S2757 view-layer merges were technically shipped and unit-test-verified but not running live until the S2759 Daphne bounce. Because the platform is single-user pre-prod (per `project_single_user_pre_prod_operating_context.md`), no user-facing impact. But the ratification envelopes for those 3 sessions may benefit from an appendix noting "S2759 diagnosis surfaced that this view-layer code did not actually load until 2026-07-11 T19:19 UTC (post make recycle-all)". Deferred — envelopes are frozen; the retroactive note lives in this record's §2 instead.

**Follow-up L2:** no dedicated `ops_tool.staleness_warnings` query action yet. Warnings accumulate as `OpsRunEvent(label='staleness_warning')` rows — queryable via ORM or a future ops_tool extension modeled after `ops_tool.tenant_boundary_violations` (S2758). Cheap follow-up if warning volume rises.

---

## §8. Provenance Chain

- **Sibling operational-infrastructure ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md` (S2758 — tool whose first live query surfaced the S2755-S2757 stale-Daphne signal)
- **Predecessor session:** `docs/handoffs/SESSION_2758_OPS_TOOL_TENANT_BOUNDARY_VIOLATIONS_RATIFIED.md`
- **Precedent-incident close ratifications:**
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md` (S2755)
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md` (S2756)
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md` (S2757)
- **Memory rule updated:** `~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_local_truth_no_production.md`
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` — §7.4.x (close-ceremony 1-PR bundle) + §7.6.1 (SIGN watchpoint attestation, applied twice this session)
