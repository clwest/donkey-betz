---
originating_session: 1157
provenance_confidence: HIGH
provenance_note: hand-authored Session 1157 handoff
---

# Session 1157 — celery-beat-schedule CONFLICT cleanup (option A applied; underlying footgun closed; verifier signal still pending broader sweep)

**Date:** 2026-05-25 (thirteenth back-to-back session — first session of post-P3.5 pivot)
**Branch state at session close:** PR #2243 merged. Main is clean. The celery-beat-schedule code-level contradiction is closed; context-kit's CONFLICT signal still flags due to broader heuristic scope (queued follow-up).

---

## TL;DR

Session 1157 was the first session after the P3.5 arc closed. Picked Rigby's flagged top-priority post-arc item: the `celery-beat-schedule` CONFLICT cleanup. Chris picked **option A (code-first single source of truth)** out-of-band before the session started.

Two stop-and-flag moments during the cleanup revealed the work was **bigger than a doc-only edit**:

1. **First flag:** the CONFLICT isn't doc-vs-code drift — it's a **code-vs-code contradiction**. `core/celery.py:app.conf.beat_schedule` is in intentional "MINIMAL token-conservation mode" since Session 1077, while `core/management/commands/add_critical_celery_tasks.py` carried its own `CRITICAL_TASKS` dict with ~100+ entries claiming "MUST be running" — different entries AND different cadences (e.g., `heart-service-heartbeat` every 60s vs every 600s). Footgun: running the mgmt command would re-enable conserve-mode-disabled tasks. Rigby called option B refactor (make the mgmt command read from `core/celery.py`); Chris approved as prep-only.

2. **Second flag:** after the refactor + 3 doc edits + canonical-source comment, context-kit verify STILL flagged CONFLICT. Its heuristic spans ~36 files (other sync commands, services, views, migrations, tests, docs) — not just the add_critical_celery_tasks ↔ core/celery.py pair we identified. Rigby's call: ship anyway, the architectural fix is the right thing; clearing context-kit's broader signal is separate follow-up (detector tuning OR targeted 36-file sweep).

Chris explicitly greenlit the merge after Rigby's recommendation.

**PR #2243 merged under bypass.** Smoke-test on main confirmed idempotent behavior (77/77 entries, 0 DB changes).

---

## What landed

| PR | What | Files | Net |
|---|---|---|---|
| **#2243** | celery-beat-schedule cleanup option A — refactor `add_critical_celery_tasks` to materialize from `core/celery.py`; canonical-source comment + doc clarifications | 4 | +198/-632 (net -434, simpler) |
| **This PR** | Session 1157 handoff + 00-START transition | 2 | — |

**Behavioral change (closed footgun):**

- **Before:** `add_critical_celery_tasks.py` carried `CRITICAL_TASKS = {...}` with ~100 entries from the pre-Session-1077 full schedule. Running the command re-enabled all of them — overriding `core/celery.py`'s intentional minimal mode and burning through API token budget.
- **After:** `add_critical_celery_tasks.py` reads `core/celery.py:app.conf.beat_schedule` directly, translates each entry (both `int seconds` → `IntervalSchedule` and `celery.schedules.crontab` → `CrontabSchedule`), and materializes `PeriodicTask` rows. Idempotent. Running it against current state produces zero DB churn (77/77 entries already in sync).

**Doc edits:**

- `core/celery.py:22` — banner comment block declaring canonical-source status, naming `add_critical_celery_tasks` as the materializer/repair tool.
- `docs/ARCHITECTURE.md:678` — code sample fixed (wrong attribute name `CELERY_BEAT_SCHEDULE` → `app.conf.beat_schedule`; outdated tasks like `run-spider-network` → current entries from `core/celery.py`).
- `docs/AUDIT_FINDINGS.md:882` — disambiguated split-ownership wording.

---

## Active issues (carrying into Session 1158)

### 1. context-kit `celery-beat-schedule` CONFLICT still flagged

The architectural fix is in, but context-kit's CONFLICT signal will still surface in local Repo Guardrails runs. Reason: its detector is keyword/path-based across ~36 files, not semantic. After PR #2243, context-kit still sees "exclusive ownership claims" in files like:

- Other sync commands: `sync_celery_beat.py`, `sync_celery_schedules.py`, `sync_task_queues.py`, `build_beat_audit.py`, `db_health_snapshot.py`, `system_health_check.py`, `setup_workspace_autopilot.py`
- Services: `celery_health.py`, `contract_monitor.py`, `td_handlers_gateway.py`, `td_handlers_ops.py`, `platform_inventory.py`, `system_reality_checker.py`, `doc_claim_verification.py`
- Views: `views_platform_command.py`, `views_agent_analytics.py`, `views_agent_learning.py`, `views_ecosystem.py`, `views_status_api.py`
- Tests, migrations, docs (`CLAUDE.md`, `BEAT_AUDIT.md`, `CELERY_AUDIT.md`, `PLATFORM_INVENTORY.md`)

**Two paths to actually clear:** (i) tune context-kit's detector to be semantic rather than keyword-based, or (ii) do a targeted token-pattern doc sweep across the 36-file set with consistent canonical-source language. Both are bigger scope than this session.

### 2. GH Actions billing — still down

13th session of bypass mode. Local-mirror discipline still holding cleanly across 18 consecutive merges this arc. Same protocol — no change.

### 3. Pre-existing 3-row drift between DB and canonical (noted, not fixed)

Smoke-test showed 80 `PeriodicTask` rows in DB vs 77 entries in `core/celery.py:app.conf.beat_schedule`. The 3-row gap is pre-existing drift from other sync paths (likely Session 1115 or earlier — possibly via the other `sync_celery_*` commands flagged in #1 above). Out of scope for this PR; separate cleanup item.

---

## Rigby's wide-open check-in (Session 1157, before the celery work started)

Chris asked me to ping Rigby for open updates. Her report (preserved here for future-session context):

**Service health snapshot (live at session start):**
- 0 SLO breaches in last 24h (all 8 SLOs clear, 100% Celery success rate over 1875 tasks)
- Autopilot: 0 actions taken, 0 blocks last 24h (healthy idle)
- Fleet (7 apps): all healthy
- Celery workers normal, `long_running` queue 2 active

**Two flags she surfaced to Chris** (both addressed during the celery cleanup):
1. Manual guardrails mode reminder — only human process enforcing gates during outage.
2. `celery-beat-schedule` CONFLICT is the **first thing to address when Actions returns** (otherwise CI stays red). Chris's option-A decision came directly from this flag.

**No parallel work happening on Rigby's side.** No queued questions for Chris. No anomalies detected.

This was the wide-open check-in Chris asked for after Session 1156 closed the P3.5 arc. Future sessions should periodically repeat this kind of open-format check-in.

---

## Decisions made this session

1. **Option A (code-first) confirmed by Chris.** Out-of-band before session work started.

2. **Refactor scope expansion from doc-only → code refactor.** Triggered by the discovery that the conflict was code-vs-code, not doc-vs-code. Rigby's call: option B refactor (materialize from canonical) is the only path that actually delivers "option A" in code.

3. **Prep-only PR, then merge under bypass.** Chris originally said "prep-only" expecting a doc-touchup. After seeing the architectural fix + Rigby's recommendation to merge anyway, Chris flipped to merge-under-bypass. Pattern: directives are conditional on scope; surface scope changes before assuming the directive still applies.

4. **Accept that context-kit's CONFLICT signal won't clear from this PR.** Rigby's framing: "easy path is chasing the tool; right path is fixing the underlying contradiction. Don't hold the real fix hostage to the verifier." Logged the detector-vs-architecture distinction explicitly in the PR body so future audits don't re-litigate.

5. **Skip the cosmetic `load_all_agents_advisors 149→139` fix in this session.** Same Rigby reasoning from Session 1150 — "tiny changes are exactly what becomes annoying if later we need to unwind during offline guardrails."

---

## Cross-session lessons (new this session)

- **NEW (1157):** context-kit CONFLICT findings can have heuristic scope far broader than the underlying real-world contradiction they're surfacing. When investigating one, enumerate the full evidence list **before** scoping the fix — what looks like a 2-file disagreement may be a 36-file heuristic match. The fix to the real contradiction may not satisfy the heuristic; that's a separate problem from a real bug.

- **NEW (1157):** "Prep-only" directives are scope-conditional. When investigation expands the scope (doc-only → code refactor), the directive needs re-confirmation, not silent extension. Chris's "prep-only" in Session 1157 implicitly assumed a doc-touchup; once the work became an architectural refactor, the directive needed explicit re-decision (and Chris flipped to merge-under-bypass after Rigby's recommendation).

- **NEW (1157):** Pre-existing log/docstring/dict text in command files can encode a stale schedule that contradicts the current canonical one. The Session 810 `CRITICAL_TASKS` dict was preserved verbatim through Sessions 1077-1156 even though `core/celery.py` had been re-pegged to minimal mode. Pattern: when migrating an authoritative source (like minimal-mode schedule), audit all *secondary* sources that may carry stale duplicates of the old authority. Same class of finding as the Session 1149 `load_all_agents_advisors` "149 Specialized Agents" → 139 actual reconciliation.

---

## Carryover for Session 1158

### Top priority (Rigby's call from Session 1157)

**`celery-beat-schedule` context-kit CONFLICT — second-half cleanup.** Two paths:

1. **Detector tuning (preferred if tractable):** inspect context-kit's `celery-beat-schedule` detector source. Find what tokens/patterns it matches as "exclusive ownership claim." If it's a simple keyword regex, propose an upstream fix that distinguishes "incidental mention" from "ownership claim." This would clear the CONFLICT without repo-wide doc churn.

2. **Targeted token-pattern doc sweep:** if detector tuning isn't tractable, identify the ~5-10 specific phrases triggering "ownership claim" in each of the 36 files, then apply a consistent canonical-source phrasing template. Bigger PR, still no guarantee.

Recommend trying (1) first — read-only investigation of upstream context-kit before deciding.

### Other queued items (unchanged from Session 1156 close, minus #1 which closed this session)

**If Actions is back:**
- Topic-doc body-count sweep (the explicit-scope one)
- Infra track: exists_on_disk flag, beat-schedule regens, build_learning_bridge_audit generator fix, Redis pooling sweep

**Continued bypass mode:**
- Older `docs/topics/` sweep (recon-first) — 7 Feb-March docs deferred from Session 1147 #2221
- Cosmetic `load_all_agents_advisors.py 149→139` fix
- `docs/reports/` + `docs/patents/` recon

**Chris-call-only:**
- Decision Command backend cleanup
- DaVinci route removal
- Mission refresh PR #2190

**Not-HIGH handoffs (783 untagged):**
- The P3.5 backfill only handled HIGH-provenance handoffs. The 783 not-HIGH ones need different treatment (manual or alternative heuristic). Separate explicitly-scoped track if/when prioritized.

---

## Arc update (Sessions 1145 → 1157)

| Session | Theme | PRs |
|---|---|---|
| 1145-1148 | Architecture + audits + P3.5 r1-r2 + SYSTEM_OWNER drift | 12 |
| 1149-1156 | SYSTEM_OWNER §3 + drift fixes + P3.5 r3-r9 (FINAL) | 16 |
| **1157 (this)** | **celery-beat-schedule cleanup (option A)** | **1 + handoff** |
| **Arc total since 1145** | | **30+ PRs across 13 sessions** |

**Bypass-mode discipline now holding cleanly across 18 consecutive merges** during the multi-day GH Actions billing outage. The discipline that's kept it safe: local mirrors every PR, only pre-existing CONFLICT acceptable, every commit subject-tagged, every merge documents both bypasses, never chain mechanical batches, surface scope changes for re-confirmation.

---

## Closing note

Session 1157 was a clean post-arc pivot. P3.5's mechanical cadence ended Session 1156; Session 1157 took on a single substantive code refactor, surfaced two stop-and-flag findings mid-investigation, both got proper Rigby + Chris input before proceeding, and the resulting PR closed a real production footgun.

The pattern of "stop, surface scope changes, get re-decision" was the load-bearing discipline. Without it, this would have shipped as a doc-only PR that didn't fix the real footgun.
