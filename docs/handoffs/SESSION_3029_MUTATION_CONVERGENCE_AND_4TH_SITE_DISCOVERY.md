# Session 3029 — mutation-style convergence + 4th silent site discovery

**Date:** 2026-07-28 · **HEAD at close:** `d0841a0f6` (PR #3747 merged) + docs cascade

## What shipped

**2 feature PRs merged this session.**

### PR #3746 (`2b72a973e`) — `feat(s3029): S3028 Fold A — mutation-style convergence`

Continues the S3026 → S3028 arc. S3028 closed the broadcast-side drift across 5 canonical-promotion paths; Fold A flagged that 2 of those 5 duplicated the field-mutation body inline instead of calling the model method.

**Fix:** both services now call `decision.promote_to_canonical(promoted_by=...)`. Per-service transaction semantics INTENTIONALLY preserved (Rigby A1 REVISE #1) — AI keeps `with transaction.atomic():`; Rules stays unwrapped (legacy S589 best-effort semantics).

**Spy test pattern** (Rigby A1 REVISE #2): `patch.object(AgentDecisionSummary, 'promote_to_canonical', autospec=True, side_effect=lambda self, promoted_by='human': original(self, promoted_by=promoted_by))`. The `side_effect` explicitly forwards to the original bound method (avoiding the `wraps=Class.method` double-self-binding trap the first attempt hit).

**Diff:** `core/services/ai_decision_promoter.py` +9/-6, `core/services/decision_promotion_rules.py` +8/-5, NEW `core/tests/test_s3029_promote_decision_model_method_convergence.py` (+131 lines, 2 spy tests). Both services grew a one-line comment near the call explaining atomic divergence — "don't harmonize without explicit evidence-backed decision" (Rigby A1 REVISE #3).

### PR #3747 (`d0841a0f6`) — `fix(s3029): PR-3746 A2 sweep follow-up — tasks_ops.py 4th silent site + data integrity fix`

**Rigby A2 zoom-out on PR #3746 flagged a repo-wide sweep for remaining inline canonical-promotion mutations.** Sweep discovered a **4th silent site MORE severe than the 3 fixed in S3028**: `_impl_auto_approve_boardroom_items` in `core/tasks_ops.py` had 4 bulk `.update(status='canonical')` calls that:

1. **Data integrity breach** — QuerySet.update() bypasses model save/signals. Auto-promoted rows had `status='canonical'` but `is_canonical=False`, `promoted_at=NULL`, `promoted_by=NULL`. Silent since ~S988. Any query filtering on `is_canonical=True` (used in `policy_context.py`, `views_project_intelligence.py`, `views_agent_learning.py`, `project_intelligence_consumer.py`) has been missing these rows for years.
2. **Silent broadcast** — same S3026-S3028 pattern.
3. **Different bug than the S3028 sites** — the 3 services (AI, Rules, PA) at least set all 4 fields inline. This task only set 1.

**Fix (Rigby A1 REVISE applied):** per-row loop calling `decision.promote_to_canonical(promoted_by='system-auto-approve')`. Consolidated the 4 duplicated blocks (`experiment`, `pipeline`, `research`, `guideline`) into a single loop over `_AUTO_PROMOTE_TYPES`. Single `transaction.atomic()` per decision_type. Broadcast emitted **outside** the atomic block (Redis-down never rolls back promotion).

**Diff:** `core/tasks_ops.py` +48/-22, NEW `core/tests/test_s3029_tasks_ops_auto_approve_promotion_convergence.py` (+123 lines, 3 tests).

## Results

| Metric | Actual |
|---|---|
| PR #3746 diff | +148/-11 (3 files: 2 services + 1 new test file) |
| PR #3747 diff | +183/-20 (2 files: tasks_ops + new test file) |
| S3029 convergence suite | **2/2 pass in 0.026s** |
| S3029 tasks_ops suite | **3/3 pass in 0.056s** |
| S3028 (mutation-swap regression) | **6/6 pass in 0.278s** — behavior unchanged |
| Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027 + S3028 + S3029 [both files]) | **69/69 pass in 7.107s** |
| Post-merge `make recycle-all` (both PRs) | HEAD `d0841a0f6`, `sha=d0841a0f67c2` recorded in `logs/recycle_events.jsonl` |

## Cycle 1A verify-before-build wins

**14th consecutive session** — Cycle 1A grep sweep at A2 zoom-out discovered the 4th silent site (previously unknown). Without the sweep, this session would have shipped a clean S3028 Fold A convergence (PR #3746) but left an even worse data-integrity bug running on the scheduled task.

**The Cycle 1A win here was Rigby's A2 zoom-out ask, not my initial verify-before-build.** Distinct signal: verify-before-build is upfront; zoom-out sweeps at A2 catch related silent bugs adjacent to the current change. Both matter.

## Rigby SIGN quality this session

**3 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3028 pattern (**15 sessions continuous**).

Cycle summary:

1. **A1 SIGN — AGREE + 3 REVISE conditions** on PR #3746 shape: keep per-service atomic semantics (don't push into model method), spy tests use `side_effect=lambda` forwarding (not `wraps=`), add atomic-divergence comment in each service. All applied same-PR.
2. **A2 SIGN — AGREE** on PR #3746 (all 4 verifications passed via `repo_tool`). Zoom-out identified 2 informational items: spy `side_effect=lambda` fragility (future signature change silently forwards wrong args), and repo-wide sweep suggestion for remaining silent sites.
3. **A1 SIGN (PR #3747) — REVISE** on scope + shape: same-session follow-up mandatory (integrity breach + running task = active harm), per-row model method (don't reintroduce mutation drift), tight filter + single atomic per type + broadcast outside atomic. All applied.

## Folds (pattern evidence, not automatic escalation)

### Fold A `informational` — Spy `side_effect=lambda` signature fragility

The S3029 convergence tests use `side_effect=lambda self, promoted_by='human': original(self, promoted_by=promoted_by)` to forward to the real bound method. If `promote_to_canonical` ever adds a required kwarg, the lambda silently forwards wrong args (still records the call, but the underlying save uses stale defaults). Codification candidate: swap for a `*args, **kwargs` forwarder. Rigby noted this is a minor nit, not urgent.

### Fold B `informational` (elevated from S3028 Fold B) — Duplicate-broadcast race unchanged

Still applies after S3029. The 6 promotion paths now all emit; two racing on the same row would fire two broadcasts. Low today (paths gate on `is_canonical=False` at query time); harden later via `did_promote` semantics.

### Fold C `1st trigger` — Rigby A2 zoom-out sweep as regular pattern

The pattern "at A2, sweep for adjacent silent bugs in the same class" caught the 4th site in this session. If it catches a 2nd cross-arc surprise in the next few sessions, codify as a workflow rule ("A2 SIGN routinely includes a repo-wide sweep for the drift-class being fixed"). Watch for 2nd trigger.

## Forward carries

### New from S3029

- **Fold A `informational`** — spy `side_effect=lambda` signature fragility.
- **Fold B `informational`** (elevated from S3028 Fold B, still applies) — duplicate-broadcast race.
- **Fold C `1st trigger`** — codify A2-zoom-out-sweep pattern.
- **S3030 primary directive candidate** — backfill migration/management command for existing drift rows (`AgentDecisionSummary.objects.filter(status='canonical', is_canonical=False)` created by 5 years of the S3029 PR #3747 bug). Rigby explicitly deferred this from PR #3747.

### Carried from S3028 (STATUS UPDATED)

- **S3028 Fold A FULLY RESOLVED** — all 6 promotion paths (was 5 known; +1 discovered) now delegate to model method OR (in tasks_ops case) loop through it.
- **S3028 Fold B `informational`** — folded into new Fold B (same content).

### Carried from S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — fold descriptions backed by evidence. S3029 A2-zoom-out sweep = supporting evidence for the general principle (evidence-driven investigation beats symptom-based description). Codification pressure stays at 1st trigger.
- **S3026 Fold B `informational`** — spec-invalidation watch. S3029 didn't spec-invalidate; both PRs shipped as designed after REVISE.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment.

### Carried from S3025 / S3024 / older — all preserved from S3028 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× Flow B spec→ship** (PR #3746 clean; PR #3747 discovered via A2 zoom-out + shipped same-session).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles. Zero rubber-stamp. 21 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "Lets keep going please" ratified S3029 primary continuing the arc.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` twice (once post-PR-3746, once post-PR-3747).
- **Fold classification (PLAYBOOK-6.10.8):** 3 folds. Fold A + B `informational`, Fold C `1st trigger` (codification candidate).
- **Verify-before-build (Cycle 1A):** **14th consecutive session** — Rigby A2 zoom-out sweep caught adjacent silent bug.

## Wrapper pin note

Session-open pin was `pa-5879c8b150324a2f` (retired at S3028 close). Active during session: `pa-6bf2053dd14a4ad7`. Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.
