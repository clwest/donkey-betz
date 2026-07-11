# Session 2750 — I-0302 Phase 4 Sub-phase 3 CLOSED — 2 PRs, all 6 substrates done

**Session:** 2750
**Date:** 2026-07-10 (continuous with S2749 close)
**Session type:** Engineering-execution arc — Sub-phase 3 remaining substrates + close
**System Owner directive at open:** "continue Sub-phase 3 with A" (coverage-gap first)
**System Owner directive at close:** "merge both" (PRs #3125 + #3126) + `--admin` rule for future merges + "close out the session"
**PA conversation pin (arc):** `pa-e71c011bfa3d4124` (S2749 carry-forward pin; still active at close)
**Preceding arc:** SESSION_2749 handoff (I-0302 Phase 4 Sub-phase 3 — 4 of 6 substrates CLOSED)

---

## §1 Delivery ledger

**2 PRs merged to main this session.** Sub-phase 3 closed cleanly — the two remaining substrates (deferred-surface coverage-gap report + VIP-scope carve-out on `get_deliverable`) both shipped.

| # | PR | Substrate | HEAD after merge |
|---|---|---|---|
| 1 | [#3125](https://github.com/clwest/donkey-betz-platform/pull/3125) | Deferred-surface coverage-gap report — informational JSON emitter for §5.3.b / §5.1.a / §5.5.a | `4bd511d0` |
| 2 | [#3126](https://github.com/clwest/donkey-betz-platform/pull/3126) | VIP-scope carve-out coverage on `get_deliverable` — fixture extension + matrix cell | `ad3721db` |

**Cumulative site-level guardrail count shipped this session:**
- **1 new test module** — `tests/security/test_i0302_p4_coverage_gap_report.py` (4 tests; emits `test_reports/i0302_p4_coverage_gaps.json`)
- **1 new report artifact** — `i0302_p4_coverage_gaps.json` (schema v1, deterministically sorted, informational-only per §4.2)
- **2 new fixtures** — `tb_vip_user` + `tb_vip_invite_in_ws_a` (extends `tb_golden` bundle 17 → 19 deps)
- **1 new matrix cell** — `TestMatrixDeliverableGetItemVIPCarveOut` (2 tests: VIP allow + VIP deny)
- **1 new memory rule** — `feedback_gh_pr_merge_admin_until_billing_fixed.md`

---

## §2 Sub-phase 3 CLOSED — 6 of 6 substrates complete

| Substrate | State | Session | PRs |
|---|---|---|---|
| §14 AST codification | CLOSED | S2749 | #3116 / #3117 / #3118 |
| Endpoint sentinels | CLOSED | S2749 | #3120 / #3121 / #3122 |
| Intentional-immutability contract | CLOSED | S2749 | #3123 |
| Rigby gpt-5.2 stall fix (bonus find) | CLOSED | S2749 | #3119 |
| Deferred-surface coverage-gap report | CLOSED | **S2750** | **#3125** |
| VIP-scope carve-out on `get_deliverable` | CLOSED | **S2750** | **#3126** |

**Phase 4 Sub-phase 3 → CLOSED.** Rolling total across S2749 + S2750: 10 PRs, 34 code fixes, 50 matrix cells (48 immutability + 2 VIP), 3 test harnesses (AST, sentinels, coverage-gap), 1 design spec, 2 memory rules.

---

## §3 Substrate arc closes (this session)

### §3.1 Deferred-surface coverage-gap report — CLOSED (PR #3125)

**Contract:** I-030203 §4.2 (report format) + §4.3 (posture probes) + I-030201 §5.3.b/§5.1.a/§5.5.a (deferred-surface amendments).

**What shipped:**
- `tests/security/test_i0302_p4_coverage_gap_report.py` — 4 tests: emit + shape + ledger-refs-resolve + specific-sites-files-exist. All pass locally in 1.6s.
- Emits `test_reports/i0302_p4_coverage_gaps.json` — schema v1, `informational` mode (never fails on missing coverage), deterministically sorted (`surface_id`, then `file+line`).
- Three deferred-surface classes covered:
  - **§5.3.b ChatConversation C2** — ledger 126 sites/43 files; live enum 114/36 (drift-visible without fail-on-drift assertion); 5 auth-mapping exemptions enumerated; Rigby inventory deliverable `7e3596c8`.
  - **§5.1.a Deliverable D-followup** — 4 hand-picked ledger sites (`distribution_agent.py:189`, `tasks.py` mixed, `mission_runner.py:1305/:1434`); no live enum since raw grep matches scoped `.get()` callers as noise.
  - **§5.5.a Document WebSocket D2-followup** — 3 lines in `content/consumers.py`; WebSocket surface probe-exempt per §4.3.
- All rows ship `posture_probed: false` today — current deferred surfaces are non-HTTP-addressable (services/tasks/agents/Employee OS) or WebSocket-exempt. Probe-machinery structure preserved for future HTTP-addressable rows.

**Rigby SIGN:** APPROVE, no F-blockers. Non-blocking asks applied: `schema_version: 1` + deterministic sorting.

### §3.2 VIP-scope carve-out coverage on `get_deliverable` — CLOSED (PR #3126)

**Contract:** I-030203 §6 step 14 + I-030201 §5.1.b tail (5th-site fix preserved the VIP carve-out).

**Background:** the §5.1.b 5th-site hotfix (S2748) added `@token_auth_required` to `get_deliverable` to fix an anonymous content leak, but explicitly preserved the VIP carve-out. Sub-phase 2 close deferred explicit regression coverage of this branch pending fixture extension. This substrate closes that deferral.

**What shipped:**
- `tests/security/fixtures/tenant_boundary.py` — added `tb_vip_user` + `tb_vip_invite_in_ws_a` (redeemed `VIPInvite`: `redeemed_by=vip_user`, `workspace=workspace_a`, `redeemed_at=now()`, `created_by=user_a`); `tb_golden` bundle extended 17 → 19 deps.
- `tests/security/conftest.py` — re-exported both new fixtures for auto-discovery.
- `tests/security/test_i0302_p4_matrix_harness.py` — new `TestMatrixDeliverableGetItemVIPCarveOut` matrix cell after `TestMatrixDeliverableGetItem`:
  - `test_vip_with_matching_workspace_can_read` — VIP viewer bound to workspace_a reads deliverable in workspace_a → **assert 200** (carve-out fires at `views_deliverables.py:191-208`).
  - `test_vip_with_mismatched_workspace_blocked` — same VIP viewer reads deliverable in workspace_b → **assert exactly 403** (carve-out scoped, not blanket; docstring documents that a future 404 migration is a policy change that should break loudly).

**Rigby SIGN:** APPROVE, no F-blockers. Non-blocking asks applied: mismatch-test docstring made intent explicit ("returns 403 (explicit denial) to ensure carve-out is scoped"). `created_by=user_a` verified via grep — no code path predicates on `VIPInvite.created_by`.

**Local verification limits (both PRs):** AST parse OK; Django-loaded fixture-wiring + `VIPInvite` field contract + `VIPScope` contract all verified via `python -c`. Full pytest blocked by pre-existing SQLite migration error (`near "[]": syntax error`) that also hits already-merged `TestMatrixDeliverableGetItem`. CI on Postgres is where the harness actually exercises. See §5.3 for the CI-billing caveat.

---

## §4 Merge conflict on the shared I-030203 doc — resolved cleanly

PR #3125 + PR #3126 both edited `docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`:
- #3125 added row `| S2750 | Deferred-surface coverage-gap report | ... |` to §8 chain-of-custody
- #3126 added row `| S2750 | VIP-scope carve-out coverage on get_deliverable | ... |` to the same table

After #3125 merged first, #3126's branch showed `mergeStateStatus: DIRTY`. Resolved via `git rebase origin/main` — single 3-line both-sides conflict on the chain-of-custody table (keep both rows). Rebased branch force-pushed with `--force-with-lease`, PR mergeable, merged clean.

**Non-blocking observation:** parallel Sub-phase substrate work will regularly conflict on the arc's central architecture doc. For Phase 4 close (S2751+), a single close-doc PR is preferable to interleaved substrate PRs so this pattern doesn't recur.

---

## §5 New workflow rule — `--admin` flag until CI billing fixed

**Directive at close (2026-07-10):** every future `gh pr merge` adds `--admin` until Chris confirms GitHub Actions billing is resumed.

### §5.1 Context

At S2750 close, all 4 CI checks failed on both #3125 and #3126 (`Failure-Data Safety Contract conformance`, `OpenAI reasoning-contract check`, `Direct LLM SDK usage check`, `Repo Guardrails`). Investigation via `gh run view` surfaced the annotation:

> The job was not started because recent account payments have failed or your spending limit needs to be increased.

Every check was red because the runner never started — not because tests actually failed.

### §5.2 The rule

- Add `--admin` to every `gh pr merge` invocation (e.g., `gh pr merge --admin --squash --delete-branch <PR>`).
- Rationale: signals "I know CI didn't run; overriding intentionally" instead of appearing to ignore red state.
- Every PR body under a "Local verification limits" section states what was verified locally as the fallback quality gate.
- Defer any check-enforcement flips (new required checks, new lint gates) until billing resumes — CI can't validate today.
- Drop the flag when Chris says billing is fixed.

### §5.3 Precedent

PRs #3125 + #3126 shipped without `--admin` (merge worked, but 4 red checks visible in the PR history). Chris flagged `--admin` immediately after, before the next merge cycle.

**Memory file:** `feedback_gh_pr_merge_admin_until_billing_fixed.md` (+ index entry in `MEMORY.md`).

---

## §6 Phase 4 close blockers — 4 remaining

Sub-phase 3 is CLOSED; Phase 4 as a whole is not yet closed. Per I-030203 §7 close criteria, remaining blockers:

| # | Blocker | Notes |
|---|---|---|
| 1 | CI wiring verify (§7 #5) — `security-conformance.yml` runs the Phase 4 harness on every relevant PR | Workflow already picks up `tests/security/*.py`; needs explicit run-through confirmation once CI billing resumes. |
| 2 | Rigby SIGN-PASS on shipped harness (§7 #6) | Post-merge behavioral verification loop pending. Rigby to run the full matrix + sentinels + AST + coverage-gap + VIP-carve-out through her tool surface and confirm SIGN-PASS. |
| 3 | Chris D-verdict ratifying Phase 4 close (§7 #7) | Requires the Phase 4 close artifact (blocker #4) to review against. |
| 4 | Phase 4 close doc (§7 #8) | Either amend I-030203 §8 with close statement OR create `I-030204_phase4_close.md`. Content: chain-of-custody roll-up, Rigby SIGN log, Chris D-verdict record, links to all 10 S2749+S2750 PRs, delta from architecture doc (deferred surfaces retained, VIP carve-out coverage extended, ops-carve-out substrate zero-current-uses baseline). |

**Phase 5 (arc close, retro) not yet opened.** Opens only after Phase 4 close is Chris-ratified.

**RUR-C1 parent close** not yet blocked on I-0302 alone; I-0303 async-boundary arc is still not opened.

---

## §7 Open runtime items carried into S2751

1. **PA celery worker bounce** — Rigby stall fix (#3119) is code-live at HEAD `ad3721db` but the running PA celery worker still has pre-#3119 code loaded. To activate: `pkill -f celery && OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES make celery`. Deferred to Chris; not urgent — pre-#3119 behavior remains functional (Anthropic fallback + response body capture are opt-in improvements).
2. **P0 cost threshold observation check-in** — deferred through S2750 per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md` (actionable 2026-07-11+). See §5 in `00-START-NEXT-SESSION.md` for the P0 report protocol.
3. **CI billing resumption** — signal to drop the `--admin` merge flag + resume enforcement-flip work.
4. **Docs cascade** — this handoff modifies 2 doc files (this + `00-START-NEXT-SESSION.md`) but was NOT run through the 4-step cascade in-session. Per memory rule `feedback_docs_cascade_at_every_close.md`, cascade should follow this PR's merge. Deferred to S2751 open OR run inline if a docs-cascade PR pattern kicks in.

---

## §8 Recommended session-open protocol (S2751)

1. `context-kit orient`
2. Read this handoff in full — §2 substrate close table + §5 `--admin` rule + §6 Phase 4 close blockers + §7 open runtime items.
3. Verify runtime state: `git log --oneline -5`, `celery inspect ping`.
4. **P0 check** (per memory rule, actionable 2026-07-11+): run the observation check-in from `00-START-NEXT-SESSION.md` P0 section; report accumulation, anomalies, advance recommendation to Chris.
5. **CI billing status** — check `gh api /repos/clwest/donkey-betz-platform/actions/permissions/access` or a fresh PR CI run to see if billing has resumed. If red, keep `--admin` flag. If green, drop the flag + delete the memory rule.
6. **Rigby PA celery worker bounce** — surface as an optional runtime item; not urgent.
7. **Primary work decision** — Phase 4 close (blockers §6.1-6.4) OR Class 1 net-new engineering per S2745 engineering-bias rule. If Phase 4 close: propose composition (blockers 1-4 in one session OR spread across two).
8. **Docs cascade** — run steps 1-4 of the 4-step cascade for the docs shipped this session if not already done. Report chunk count in a follow-on cascade PR.
9. Session pin carry-forward: `pa-e71c011bfa3d4124` still active at S2750 close — decide at S2751 open whether to rotate (arc-scoped pins typically retire at arc-close; Phase 4 close is the natural retire point).

---

## §9 Chain of custody

| Session | Event | Reference |
|---|---|---|
| S2748 | Phase 4 Sub-phases 0/1/2 COMPLETE — 4 PRs (#3111-#3114) + §5.1.b 5-site hotfix (#3113) + §14 threshold codification | SESSION_2748 handoff |
| S2749 | Phase 4 Sub-phase 3 — 8 PRs (#3116-#3123) — 4 of 6 substrates CLOSED; Rigby stall post-mortem + fix | SESSION_2749 handoff |
| S2750 | Phase 4 Sub-phase 3 CLOSED — 2 PRs (#3125 + #3126) — remaining 2 substrates shipped | This handoff |
| S2751 | Phase 4 close (blockers 1-4) OR net-new engineering | TBD |
| TBD | Rigby SIGN-PASS on shipped harness | Phase 4 close blocker #2 |
| TBD | Chris D-verdict ratifying Phase 4 close | Phase 4 close blocker #3 |
| TBD | Phase 4 close doc (I-030204_phase4_close.md OR amend I-030203 §8) | Phase 4 close blocker #4 |
| TBD | I-0302 arc close (Phase 5) | Opens after Phase 4 close |

---

## §10 What this session taught us

Per playbook §11.3 xx99 canonical-summary template addition — captured here despite not being an xx99 close, because two patterns worth codifying surfaced:

### §10.1 What worked

- **Shared-doc conflict handling** — force-with-lease rebase + single hand-merge kept the two S2750 PRs shippable in the same window. Trivially resolved because both PRs only ADDED rows (no deletes or in-place edits on the same lines).
- **Substrate manifest in Python-only test** — the coverage-gap emitter is a pure-Python pytest module (no DB setup, no Django ORM). Ships informational reports without adding to CI runtime cost. Pattern reusable for future informational reports.
- **Rigby SIGN with concrete watchpoints** — routing each PR SIGN with `(a) / (b) / (c) watchpoints` produced targeted APPROVE-with-non-blocking-tweaks rather than a raw thumbs-up. Both PRs shipped Rigby's non-blocking tweaks inline.

### §10.2 Anti-patterns to avoid

- **Merging with all-red-CI without stating why** — S2750 shipped PRs #3125 + #3126 without acknowledging the CI-billing cause in the merge message. Chris's `--admin` directive was in-part a correction: state the reason for the override, don't just silently merge past failing checks. Codified into `feedback_gh_pr_merge_admin_until_billing_fixed.md`.
- **Interleaved substrate PRs on a shared arc doc** — the S2750 rebase-conflict was cheap this time but signals a compound-substrate anti-pattern. For Phase 4 close, a single close-doc PR is preferable to interleaved substrate PRs.

### §10.3 Suggestions for future substrate handoffs

- When 2+ substrates edit the same arc doc, ship them in order (not parallel) OR consolidate into one PR from the start.
- When CI is billing-blocked, add a "Local verification limits" section to every PR body up front — don't wait for the reviewer to ask.

---

**End S2750 handoff. Sub-phase 3 CLOSED. Phase 4 close blockers remain (4 items in §6).**
