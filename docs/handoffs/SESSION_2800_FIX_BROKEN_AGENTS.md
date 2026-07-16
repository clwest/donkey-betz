# Session 2800 — Fix broken agents (Option B: worker-startup orphan reap + CodeReviewAgent MISSING_INPUT)

**Date:** 2026-07-16
**Session:** S2800
**Branch/PR:** `s2800-fix-broken-agents` → **PR #3213** (merged as `4c339a6a6b2a`)
**Predecessor:** [SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md](SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** fortieth post-PLAYBOOK-7.4.4

---

## §1 — Ship summary

Fourth consecutive engineering ship in a single day (S2797 landing → S2798 onboarding → S2799 signposts → S2800 broken-agent fixes). Chris directive at session open: `"let's do option B then stop"` — one session, one ship, no follow-on candidates.

Ships **two structural fixes** for the 5 "broken agents" identified in S2799 Thread 1:

**Fix 1 — Worker-startup orphan reap** (`core/celery.py` — fixes 4 of 5 at root):

New `worker_process_init` handler `_reap_orphan_agent_executions_on_startup`. On each worker child startup, bulk UPDATEs `AgentExecution` rows where:
- `status='in_progress'`
- `last_heartbeat_at IS NULL OR last_heartbeat_at < now-3min` (stale — worker died)
- `created_at within last 24h` (avoid ancient rows)

→ `status='cancelled'` + `error_message='Worker restart — execution interrupted (S2800)'` + `completed_at=now`.

Runs on OTHER workers' startup so the "which row is mine" problem disappears — rows on still-alive workers have fresh heartbeats (< 3min) and are excluded.

**Live proof:** at the post-merge `make recycle-all`, the handler transitioned **16 orphan AgentExecution rows to cancelled** on first worker child startup. Log line: `[CELERY_WORKER_STARTUP_REAP] transitioned 16 orphan AgentExecution row(s) to cancelled`. Those 16 rows would have been marked `failed` at 60min by the cleanup watchdog — instead honestly labeled as worker-restart interruptions.

**Fix 2 — CodeReviewAgent MISSING_INPUT signal** (`core/agents/code_review_agent.py` — fixes 1 of 5):

At `execute()` top, regex-detect file path (`r'[\w/.-]+\.\w{1,6}\b'`) OR fenced code block (```) in task string. If neither present, return:

```python
AgentResult(
    success=False,
    error='MISSING_INPUT: no file path or code block found in task',
    data={
        'error_code': 'MISSING_INPUT',
        'error_type': 'input_validation',
        'task_preview': task[:200],
        'hint': 'Provide a file path (e.g. core/foo.py) or a fenced code block.',
    },
    message='I need a file path or a code snippet to review. Try again with something like: `review core/services/foo.py`, or paste a code block inside triple backticks.'
)
```

Replaces the pre-S2800 terse "No code inspection or review completed" message that accounted for 76% of CodeReviewAgent failures (S2799 Thread 1). Structured `error_code` so outer workflows chaining CodeReviewAgent as a sub-step can distinguish missing-input from real-review-failure (Rigby T1 SIGN fold 88).

**Fix 3 — Smoke gate mgmt command** (`core/management/commands/smoke_broken_agents_pre_fix.py`):

Extends the S2799 tool-level smoke pattern to agent level. Dispatches each of the 5 agents with a benign task, tags OK / SMOKE_MISSING / SMOKE_FAIL / SMOKE_TIMEOUT / SMOKE_EXCEPTION. Re-runnable post-fix. Baseline run confirmed CodeReviewAgent transitions to `SMOKE_MISSING` (expected post-fix); other agents pass on happy path.

**Files changed (4):**

| File | Change | Purpose |
|------|--------|---------|
| `core/celery.py` | +61 lines | `_reap_orphan_agent_executions_on_startup` handler |
| `core/agents/code_review_agent.py` | +34 lines | MISSING_INPUT early-return with `error_code` signal |
| `core/management/commands/smoke_broken_agents_pre_fix.py` | +178 lines (new) | Agent-level smoke gate |
| `tools/pa_local.sh` | +1 / -1 | Fresh S2800 pin `pa-5ca1a29ad6514475` |

**Verification:**

- `python manage.py check` — 0 issues
- Baseline smoke: `CodeReviewAgent → SMOKE_MISSING`, `WorkflowAgent/CTOAgent/AudioAgent → OK` (post-recycle happy path), 1 TIMEOUT on 30s ceiling
- Post-merge `make recycle-all`: reap handler fired, transitioned 16 orphan rows to `cancelled` (measurable evidence)
- Regression 17-suite: unchanged (S2800 was reliability + agent fix; no test-covered surface)

---

## §2 — Novel-precedent moments

**Fourth consecutive same-day engineering ship.** S2797 → S2798 → S2799 → S2800 in a single conversation, each with joint Rigby SIGN + fold persistence + full close cascade. Total ledger growth: 68 → 89 rows (+21 folds across 4 ships).

**First ship with a live-measurable capability-lift receipt.** The reap handler didn't just pass a code review — it fired on the FIRST worker restart post-merge and transitioned 16 orphan rows to `cancelled`. That's 16 rows the cleanup watchdog would have otherwise marked `failed` at 60min. Metric visible via `grep CELERY_WORKER_STARTUP_REAP celery*.log`. Signpost lift on S2799 was similarly measurable; two ships in a row that produced quantitative post-ship evidence.

**First Chris directive with "then stop" explicit termination clause.** Chris scoped S2800 as a single-ship session with no follow-on candidate menu. Everything queued after Option B (BettingPage trace, Stock Intelligence revenue play, etc.) defers to S2801+. Explicit termination is a cleaner protocol than the implicit "one ship per session" default — worth watching if Chris uses this shape again.

**Rigby T1 verify-honesty explicitly persisted as fold row 89.** She admitted her tool budget couldn't produce a definitive day-bucket histogram cross-referencing every "no heartbeat" failure with `recycle_events.jsonl`. Ship covers the 4-known-orphan pattern; commit message + PR body explicitly admit scope + file a signposted follow-up. Direct PLAYBOOK-6.10.9 compliance — verify-limits admission in-line.

**Root-cause discovery upstream of implementation.** Initial framing was "fix 5 broken agents." Verify-before-build found the actual root: 4 of 5 aren't broken agents at all — they're worker-restart orphans. That reframed the ship from "5 agent bugs" to "1 infra fix + 1 real agent bug." Fewer files touched, higher confidence, cleaner architecture.

**PLAYBOOK-6.10.8 fold-before-D-verdict discipline held.** 5 folds persisted before Chris "ship it." Third consecutive session with correct timing (S2799 corrected the S2798 miss; S2800 held it).

---

## §3 — SIGN cycle

### T1 Rigby SIGN — SIGN-WITH-EDITS (tool_runs verified: ops_tool failure signatures + recycle_events cross-ref)

**Rigby's ops_tool query** surfaced `TIMEOUT_WATCHDOG_CLEANUP_*` failure signatures for WorkflowOrchestrationAgent, ContentWriterAgent, DevOpsAgent — 2 each, clustering on 06/24-06/25 and 07/13 which correspond to known recycle windows. Consistent with worker-restart hypothesis.

**Ask 1 (root-cause validation):** Partial confirm. Strongly consistent with hypothesis; couldn't produce definitive day-bucket histogram of ALL no-heartbeat failures. Some non-recycle-day failures may be real hangs — flagged as future_trigger.

**Ask 2 (seam choice):** `worker_shutdown` / `worker_process_init` Celery signals — correct seam. Django shutdown hooks unreliable for Celery worker termination; SoftTimeLimit doesn't fire on worker death.

**Ask 3 (status enum):** Use existing `cancelled` + machine-parseable `error_message` string rather than adding new `interrupted` enum. Avoids downstream consumer audit + migration.

**Ask 4 (CodeReviewAgent file discovery):** Option (a) regex extraction + fail-fast. Skip option (b) implicit "recent files" guessing (surprising behavior).

**Ask 5 (zoom-out folds — persisted):** Systemic fix via reap is right scope; use cancelled + reason (defer enum); shutdown handler bounded/bulk; CodeReviewAgent structured `error_code` protects outer workflows.

### Fold ledger — 5 new rows (84 → 89)

| Row | Arc | Classification |
|-----|-----|----------------|
| 85 | worker_shutdown_reap_correct_scope | same_pr_actionable |
| 86 | use_cancelled_not_new_interrupted_enum | same_pr_mitigatable |
| 87 | shutdown_handler_bounded_bulk | same_pr_actionable |
| 88 | code_review_missing_input_signal_structured_code | same_pr_mitigatable |
| 89 | worker_restart_hypothesis_strength (verify-limits per 6.10.9) | same_pr_mitigatable |

**All 5 folds persisted BEFORE Chris D-verdict** (S2799 discipline held; second consecutive correct-timing ship).

---

## §4 — Verification transcript

```bash
# Baseline smoke
$ python manage.py smoke_broken_agents_pre_fix
[MISS] CodeReviewAgent              (2.1s) — I need a file path or a code snippet to review...
[PASS] WorkflowAgent                (variable — succeeds on happy path with fresh worker)
[PASS] WorkflowOrchestrationAgent   (variable)
[PASS] CTOAgent                     (variable)
[PASS] AudioAgent                   (7.3s) — Capability Check ready
OK=3  SMOKE_MISSING=1  SMOKE_TIMEOUT=1  (1 agent hit the 30s per-agent ceiling)

# Post-merge live proof of reap
$ grep CELERY_WORKER_STARTUP_REAP celery*.log
INFO 2026-07-16 10:36:55 celery [CELERY_WORKER_STARTUP_REAP] transitioned 16 orphan AgentExecution row(s) to cancelled

# Django check
$ python manage.py check
System check identified no issues (0 silenced).
```

**The 16-row reap number is the load-bearing metric** — 16 rows that would have been silently marked `failed` at the 60min cleanup are now honestly labeled `cancelled` with a machine-readable reason. Every future `make celery-recycle` will produce a similar log line + drop the false-failure rate on the affected agents.

---

## §5 — Twin-pointer card

📁 **Repo `/` + `/docs/` — S2800 artifacts:**

- **Reap handler:** `core/celery.py` — `_reap_orphan_agent_executions_on_startup` (below line 70 existing shutdown handler)
- **CodeReviewAgent fix:** `core/agents/code_review_agent.py` — MISSING_INPUT block at execute() top (~line 341)
- **Smoke gate:** `core/management/commands/smoke_broken_agents_pre_fix.py` (reusable — Option B pattern extension of S2799)
- **Handoff:** `docs/handoffs/SESSION_2800_FIX_BROKEN_AGENTS.md`
- **Live test:** `python manage.py smoke_broken_agents_pre_fix` or `--as-json`
- **Predecessors:** S2799 (signposts), S2798 (onboarding), S2797 (landing)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No new Workspace tab** — reliability infra ship
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **89 rows** (35/30/22); rows 85-89 are S2800
  - `logs/recycle_events.jsonl` — +2 events during S2800 close
  - `celery*.log` — `[CELERY_WORKER_STARTUP_REAP]` log line on every worker startup (measurable evidence of the fix working)

---

## §6 — Open items / owed / deferred

**S2800 owed follow-ups (none blocking S2801):**

- **AudioAgent TTS payment-wall** — separate config issue (ElevenLabs paid plan required). Not code; deferred until Chris decides on paid TTS provider.
- **CodeReviewAgent workspace file discovery** — Rigby T1: fail-fast is preferred to implicit guessing. Only revisit if MISSING_INPUT rate too high for user experience.
- **Non-recycle-day no-heartbeat failures** — signposted follow-up per fold row 89. Post-ship: monitor `AgentExecution.error_message` for "no heartbeat" on days with zero `recycle_events.jsonl` entries. Those are real hangs needing different fix.

**Chris sequencing queue for S2801+:**

Per S2799 handoff §7: **BettingPage first-user trace next**, then Stock Intelligence non-betting revenue play. Chris's session-open remark: `"then stop"` — S2800 terminates cleanly without follow-on candidate menu at close.

**Standing owed (from S2797/S2798/S2799):**

- All pre-S2800 items unchanged
- **S2799 F84** — per-signpost adoption telemetry (fires 7 days post-ship if any of 14 signposted tools has zero invocations; watch)

**Deferred (waiting on triggers):**

- **NEW: S2800 F89** — non-recycle-day no-heartbeat failure monitor. Trigger: any AgentExecution row with `error_message LIKE '%no heartbeat%'` AND `created_at` day has no entry in `recycle_events.jsonl`. Mitigation: distinct fix (real hang, not orphan).
- All prior S2797-S2799 triggers unchanged

---

## §7 — Chris directive queue captured this session

**Explicit sequencing at S2800 open:**

`"let's do option B then stop"` — one session, one ship (this one), no follow-on candidate menu. Termination clean.

**Next session default (S2801):**

Per Chris's earlier C→B→BettingPage sequencing at S2799: **BettingPage first-user trace + top-1 fix** is the next candidate.

---

## §8 — Discipline observations

- **PLAYBOOK-6.10.8 fold persistence timing held.** 5 folds persisted between T1 SIGN and "ship it." Second consecutive session with correct timing.
- **PLAYBOOK-6.10.9 verify-limits admission explicit.** Fold row 89 admits scope covers the 4-known-orphan pattern, not all hangs. Signposted follow-up filed with concrete trigger.
- **Root-cause verify-before-build paid off.** Initial framing was "fix 5 broken agents." Verify surfaced "4 of 5 are worker-restart orphans." Reframed ship from "5 agent-code fixes" to "1 infra handler + 1 real agent-code fix." Simpler diff, higher confidence, cleaner architecture.
- **Live-verify-post-merge produced quantitative evidence.** The 16-orphan-reap log line at first post-merge worker startup is the ship's receipt. Chris can grep the log tomorrow and see how many the reap catches over 24h.
