# Session 2759 — Stale-Daphne / Stale-Celery Warning System Ratified

**Date:** 2026-07-11
**Predecessor:** S2758 (ops_tool.tenant_boundary_violations PA tool ratified; pin `pa-5fe224e5757f42c0` retired)
**Successor:** S2760 (multiple candidates — S2758 D2 canonical decision routing, D4 HIGH-RISK task file wiring extension, or net-new engineering; S2759 P0.5 freeze-mode routing + P0.75 CI billing still owed)
**Session pin:** `pa-58888db8e1d148ca` (label `s2759-rigby-dispatch-conversion` — stale label after mid-session scope pivot away from dispatch conversion; new label proposal for S2760 pin below; **retired at S2759 close** per protocol)
**HEAD at open:** `fd21d4bae` (post-S2758 tool merge)
**HEAD at close:** (filled at merge)

---

## §1 Delivery Ledger

Single 1-PR close-ceremony bundle per PLAYBOOK-7.4.1. Five consecutive phase-closes today (S2755 → S2756 → S2757 → S2758 → S2759).

| # | PR | Merge SHA | Content |
|---|---|---|---|
| 1 | (this PR) | pending | `make recycle-all` + `ops_tool.version` staleness detection + `check_process_staleness` Beat task + memory rule update + 10 tests + ratification envelope + handoff + docs cascade + pin retire commentary |

---

## §2 Scope Pivot Mid-Session

S2759 opened as C1 from S2758 close menu: "Rigby-side dispatch-path conversion" — motivated by the S2758 tool's real finding (Rigby's own PA loop dispatched `process_pa_chat_task` without acting-user header at conversation_id = S2758 session pin).

**Diagnostic pivot:** empirical testing PROVED the S2757 BATCH-FIX dispatch site conversion code was correct. Header propagation worked cleanly from a fresh Python shell. The S2758 finding was traced to a stale Daphne process (started Jun 30, 11 days pre-merge) holding cached module state that predated the S2755/S2756/S2757 view-layer changes.

**Chris directive:** *"this issue has now occurred three times so we might need to set up some type of 'recycle-all warning' or something so we don't have this happen in the future."* Session scope pivoted from operational C1 to codified stale-process detection.

---

## §3 Ratified Deliverables

### §3.1 `make recycle-all` Makefile target

Aliases existing `make restart` with S2759-explicit naming. Ordering: `make stop → make celery-stop → make start → make celery`. Placement: `Makefile:80-91`. `make restart` preserved for backwards-compat.

### §3.2 `ops_tool.version` staleness detection

Extended `_ops_version` response with:

- `staleness_verdict`: FRESH / STALE_DAPHNE / STALE_CELERY / STALE_BOTH / UNKNOWN
- `head_commit_sha`, `head_commit_timestamp`
- `daphne_pid`, `daphne_pid_age_seconds`, `daphne_started_before_head_commit`
- `celery_workers_status[]` — per-worker `{hostname, pid, pid_age_seconds, started_before_head_commit}`
- `staleness_fix` (when not FRESH) — points at `make recycle-all`
- `staleness_error` (when verdict is UNKNOWN) — fail-soft explanation

New helper `_compute_process_staleness(self)` (~130 lines) uses `psutil.process_iter()` for cross-platform process discovery. Deterministic threshold: process started before HEAD commit = stale.

### §3.3 `check_process_staleness` Beat task

`core/tasks_beat_health.py` — every 30 min via `crontab(minute='*/30')`. Registered in `core/celery.py:868`. Emits `OpsRunEvent(label='staleness_warning', event_type='step_fail', detail={...})` when verdict != FRESH. Never raises.

### §3.4 Test suite — 10 tests, 10/10 passing (190s runtime)

`tests/security/test_process_staleness_detection.py` (new): 4 verdict paths + UNKNOWN cases + grep-row exclusion + 3 Beat task paths. Uses monkey-patched `psutil.process_iter` + `subprocess.check_output`.

### §3.5 E2E verification (live, post `make recycle-all`)

Rigby dispatched `ops_tool.version` → `staleness_verdict=FRESH` with head_commit_sha=`fd21d4bae621a0b0b6a265350a7d5bae43c1773b`, Daphne pid_age_seconds=27, and all 5 Celery workers started_before_head_commit=false. Working E2E through PA loop.

### §3.6 Memory rule update

`feedback_local_truth_no_production.md` extended:
- `make recycle-all` is the canonical deploy step (not `make celery-recycle` alone)
- Trigger list: ASGI-served code (`core/views/**`, `services/**`, `urls.py`, `asgi.py`, middleware, auth/permission) + Celery-served (`tasks*`, Celery config)
- Freshness check via `ops_tool.version` at close of any session touching the trigger list
- Precedent block naming S2755/S2756/S2757 as the 3-incident class this codifies

### §3.7 Ratification envelope

`docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md` — frozen record with root cause analysis, empirical proof, two SIGN turn logs, Chris D-verdict, retroactive impact analysis, follow-up backlog.

---

## §4 Rigby SIGN Cycle — two turns, all PASS

### §4.1 Design SIGN turn 1 (pre-code)

F1–F6 PASS with 3 refinements:
- F1: hard-kill Daphne + print stopped processes (already in existing `stop:`)
- F2: include `head_commit_sha` in response (applied verbatim)
- F4: broaden memory-rule trigger to ASGI-served surfaces + auth/permission layer (applied verbatim)

### §4.2 Implementation SIGN turn 1 (post-code)

F1–F6 all PASS clean, no edits. Rigby executed live E2E verification post `make recycle-all`.

---

## §5 Chris D-Verdict — two ratification points

1. **Combined shape** — "lets do it"
2. **Final ship** — "approved, ship it"

Zero unresolved menus routed per S2753 agree-first rule.

---

## §6 Workflow Rules Exercised

### §6.1 Claude+Rigby agree-first (S2753 directive)
Two Rigby SIGN turns + two Chris D-verdict points. Zero unresolved menus routed.

### §6.2 Bias engineering / net-new builds (S2745 directive)
Codifies operational infrastructure preventing a 3-incident regression class. Net-new engineering per bias directive.

### §6.3 Verify-before-build (Cycle 1A rule)
Before shipping the warning system, empirically proved the root cause was stale Daphne (not a dispatch-path gap). Section §2 of the envelope documents the 3-test diagnostic proof. Pivoted scope on the evidence.

### §6.4 Twin-canonical-representations (S2754a rule)
Ratification lands TWO deliverables in RUR-C1 workspace (adjacent to S2758 tool that surfaced the signal):
- Governance-truth: `RATIFICATION_20260711_stale_daphne_warning_system`
- Engineering-truth: `Stale-Daphne Warning System (mirror)`

### §6.5 Docs cascade at every close (S1399 rule)
Full 4-step cascade at close: `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents --all-unembedded` + `build_docs_provenance`.

### §6.6 PLAYBOOK-7.4.1 close-ceremony 1-PR bundle
All artifacts land in ONE PR.

### §6.7 PLAYBOOK-7.6.1 SIGN watchpoint-attestation
Two SIGN turns (pre-code + post-code). Both PASS.

### §6.8 Local-truth rule (Chris S2758 directive, S2759 extension)
This session CODIFIES the local-truth rule with concrete tooling: `make recycle-all`, `ops_tool.version` staleness verdict, Beat task, memory rule update. The rule was previously prose-only; S2759 turns it into detectable infrastructure.

### §6.9 `gh pr merge --admin` (feedback rule)
Merged with `--admin` posture — GitHub Actions billing still blocked.

---

## §7 Session Timing + Cost

- Session open: 2026-07-11 (continued conversation post-S2758 close)
- First Rigby dispatch: after fresh pin mint (`pa-58888db8e1d148ca`; label stale after scope pivot)
- Rigby SIGN turns: 2 (pre-code + post-code) — all PASS
- Chris D-verdicts: 2 (combined shape / final ship)
- Test runs: 2 (first had NameError on `import os` + KeyError on beat-task test; both fixed on second run — 10/10 pass at 190s)
- E2E verifications: 2 (`make recycle-all` — first failed on BSD `ps -eo etimes`; migrated to psutil; second passed cleanly)
- Total local runtime: ~2 hours

---

## §8 S2760 Priorities (Informative)

Chris selects at S2760 open:

1. **S2758 D2** — canonical AgentExecution vs AgentTaskExecution decision routing (three approaches require Chris directive)
2. **S2758 D4** — HIGH-RISK task file wiring extension (REPORT-ONLY shape for tasks_initiatives/content/media/misc)
3. **Follow-up L2** — new `ops_tool.staleness_warnings` query action (parallel to S2758 tool shape) if Beat task warnings accumulate
4. **Net-new engineering** — new spider / UI page / capability per S2745 bias directive
5. Housekeeping: P0.5 freeze-mode routing + P0.75 CI billing

---

## §9 Provenance Chain

- **Predecessor session:** `docs/handoffs/SESSION_2758_OPS_TOOL_TENANT_BOUNDARY_VIOLATIONS_RATIFIED.md`
- **Sibling operational-infrastructure ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md` (S2758 tool surfaced the 3-incident signal)
- **Precedent-incident close ratifications (silent stale-Daphne class):**
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md` (S2755)
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md` (S2756)
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md` (S2757)
- **Memory rule updated:** `feedback_local_truth_no_production.md`
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (§7.4.x + §7.6.1)
- **Ratification envelope (this session):** `docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md`
