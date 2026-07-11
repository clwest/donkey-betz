# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2750 CLOSED — SUB-PHASE 3 CLOSED (all 6 substrates done); PHASE 4 CLOSE OPENS FOR S2751

**Refreshed 2026-07-10 (SESSION 2750 CLOSED. 2 PRs merged closing out Phase 4 Sub-phase 3: deferred-surface coverage-gap report (#3125) + VIP-scope carve-out coverage on `get_deliverable` (#3126). All 6 Sub-phase 3 substrates now CLOSED. New workflow rule: `gh pr merge --admin` until CI billing is fixed. Phase 4 close blockers remain (CI wiring verify, Rigby SIGN on shipped harness, Chris D-verdict, close-doc write). Full session substance in `docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md`.**

Session anchors (read in order):

1. [`docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md`](docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md) — S2750 delivery ledger, 2 substrate closes, `--admin` rule, Phase 4 close blockers, S2751 open protocol
2. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — Phase 4 architecture doc; §6 steps 12+14 marked DONE, §7 close criterion #4 marked DONE, §8 chain-of-custody rows added
3. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — Phase 1 ledger with all Sub-phase 3 amendments
4. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)

**Prior sessions (background context):** S2749 (Phase 4 Sub-phase 3 — 4 of 6 substrates CLOSED, 8 PRs); S2748 (Phase 4 Sub-phases 0/1/2 COMPLETE); S2747 (Phase 3 wiring COMPLETE); S2746 (Phase 2 predicate module RATIFIED); S2745 (engineering-pivot directive + cost threshold observation opened); S2742 (Playbook v0.4.1 + RUR CAMPAIGN parent doc + I-0301 CLOSED).

---

## P0 — COST THRESHOLD OBSERVATION CHECK-IN (actionable 2026-07-11+)

**Do this FIRST before candidate selection.** Deferred at S2746 → S2750 per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md` — **actionable on 2026-07-11 sessions onward.** If S2751 opens on 2026-07-11 or later, run the check-in.

**State at open:**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation only)
- Set locally on Chris's dev DB via `python manage.py cost_thresholds --set month 500`
- Observation period started 2026-07-10 07:35 MDT

**Report to Chris at session open:**

1. **Current threshold config** — run `python manage.py cost_thresholds`; confirm `month: $500.00` still set and mode still `monitor`. Flag any drift.
2. **Accumulation** — query `LLMCallLog` (or equivalent cost-accumulation surface used by the beat task) for the period since 2026-07-10 07:35 MDT. Report: total accumulated $, % of $500 ceiling, top 3 cost drivers by model/service.
3. **Anomalies** — any single-hour spike >$20, any new provider showing up, any `[COST_MONITOR]` log lines showing near-threshold behavior. If clean, say so explicitly.
4. **Advance recommendation** — based on observation-period data, is 24+ hours of clean observation enough to advance to `--set-mode freeze` (shadow mode), or does Chris want to observe longer? Rigby SIGN on the recommendation before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.** Per S2735 P1 gate discipline.

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` ("Rigby: Cost threshold observation period — opened 2026-07-10 (S2744)").

---

## P0.5 — CI BILLING STATUS CHECK

**Do this SECOND, right after the cost check-in.** Confirmed at S2750 close: all GitHub Actions checks are failing with "job did not start — billing" annotation. Every merge now uses `--admin` per `feedback_gh_pr_merge_admin_until_billing_fixed.md`.

**Report to Chris at session open:**

1. **Fresh CI run** — trigger any recent PR's CI or check `gh api /repos/clwest/donkey-betz-platform/actions/runs -q '.workflow_runs[0]'` to see the latest run's `conclusion` + annotations. If billing is fixed, `conclusion: success` will surface on a new run.
2. **Flag state** — if CI is green again: drop the `--admin` flag from `gh pr merge` calls this session, delete the memory file `feedback_gh_pr_merge_admin_until_billing_fixed.md`, and remove the corresponding line from `MEMORY.md`.
3. **If still billing-blocked:** continue `--admin` merges; every PR body includes a "Local verification limits" section stating what was verified locally as the fallback quality gate.

---

## OPEN RUNTIME ITEMS (from S2750 close)

1. **PA celery worker bounce.** PR #3119 landed the Rigby gpt-5.2 stall fix (S2749) but the running PA celery worker still has old code loaded. To activate: `pkill -f celery && OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES make celery`. Deferred to Chris; not urgent — pre-#3119 behavior remains functional.
2. **P0 observation check-in** — see above; actionable 2026-07-11+.
3. **P0.5 CI billing status** — see above; blocks lint-enforcement flips + `--admin` flag posture.
4. **Docs cascade for S2750 shipped docs** — this handoff + 00-START-NEXT-SESSION.md have not yet been run through the 4-step docs cascade. Run at S2751 open if not already done in a follow-on cascade PR.

---

## PRIMARY WORK CANDIDATES — S2751

### CANDIDATE A — I-0302 Phase 4 CLOSE (4 blockers remaining)

Per I-030203 §7, Phase 4 closes when all of:

1. **CI wiring verify** — `security-conformance.yml` runs the Phase 4 harness on every relevant PR. Workflow already picks up `tests/security/*.py`; verify explicit run-through once CI billing resumes.
2. **Rigby SIGN-PASS on shipped harness** — Rigby runs the full matrix + sentinels + AST + coverage-gap + VIP-carve-out through her tool surface and confirms SIGN-PASS. Post-merge behavioral verification loop.
3. **Chris D-verdict ratifying Phase 4 close.**
4. **Phase 4 close doc** — either amend I-030203 §8 with close statement OR create `I-030204_phase4_close.md`. Content: chain-of-custody roll-up (S2748→S2750), Rigby SIGN log, Chris D-verdict record, links to all 10 S2749+S2750 PRs, delta from architecture doc.

Ship pattern: single close-doc PR (blocker #4) that references verifications done for blockers #1-#3 in the PR body. **Do NOT interleave close-doc PRs with substrate PRs** — S2750's shared-doc rebase-conflict signals the anti-pattern.

### CANDIDATE B — NET-NEW ENGINEERING (per S2745 engineering-bias rule)

Always propose 1-3 net-new candidates every session:

1. **New Employee OS employee (4th)** — vertical slice: new `AIEmployee` + `JobContract` + MissionRunner steps + admin visibility. Chris to name the role.
2. **New spider on Chris-named data gap** — spider class + fixture + test + registry entry + signal wiring.
3. **New Command Center / Workspace UI page** — 61 routes; requires Chris naming the workflow.
4. **Discord bot new command** — bounded Cog + slash-command slice.
5. **Betting dashboard new tab / feature** — 9-tab dashboard, Chris names the gap.

### CANDIDATE C — META-METHODOLOGY (only if Chris explicitly asks)

- **"Interleaved substrate PRs on shared arc doc = rebase-conflict pattern"** — S2750's shared-doc rebase-conflict. Watch for 2nd instance before codifying as a playbook rule (e.g., "arc-close doc changes must be serialized").
- **"Discovery-first-then-batch-fix three-PR arc pattern"** — applied twice cleanly in S2749 (§14 codification + endpoint sentinels). NOT repeated in S2750 (both S2750 substrates were single-PR ships). If it repeats a third time in a future arc, codify as a Sub-phase close playbook rule.
- **"CI-billing-blocked → local verification fallback"** — established as workflow rule in S2750. If the fallback pattern (AST parse + Django-loaded import probes + fixture-wiring checks + prior-CI-green-on-identical-shape rationale) repeats across multiple PRs while billing remains blocked, could codify as a playbook §11.x subsection.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `ad3721db` (PR #3126 merged; VIP-scope carve-out coverage; S2750 close) |
| Playbook version | v0.4.1 (unchanged since S2742) |
| Playbook rule count | 196 |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-e71c011bfa3d4124` (active — carry-forward from S2749; retire at Phase 4 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-e71c011bfa3d4124` |
| Live infra state | Cost threshold monitor mode $500/mo, observation period accumulating; PA celery worker running pre-#3119 code (bounce needed to activate stall fix); CI billing-blocked (`--admin` flag on merges per memory rule) |
| RUR arc state | I-0301 CLOSED · I-0302 Phases 1-3 CLOSED · Phase 4 Sub-phases 0/1/2/3 CLOSED · Phase 4 close — 4 blockers OPEN · Phase 5 (arc close) not yet opened · I-0303 not yet opened · RUR-C1 parent OPEN |

---

## What S2750 shipped (2 PRs)

Full delivery ledger in `docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md` §1. Compressed:

| PR | Substrate | HEAD |
|---|---|---|
| #3125 | Deferred-surface coverage-gap report | `4bd511d0` |
| #3126 | VIP-scope carve-out coverage on `get_deliverable` | `ad3721db` |

**Cumulative site-level guardrails shipped this session: 1 new test module + 1 new report artifact + 2 new fixtures + 1 new matrix cell + 1 new memory rule.**

---

## Recommended session-open protocol (S2751)

1. `context-kit orient`
2. Read `docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md` in full — §1 delivery ledger + §5 `--admin` rule + §6 Phase 4 close blockers + §7 open runtime items + §10 what this session taught us
3. Verify runtime state: `git log --oneline -5`, `celery inspect ping`
4. **P0 check** (per callout above, if 2026-07-11+): run the observation check-in
5. **P0.5 CI billing status** — check + flag drop if resumed
6. `pa_local.sh` pin carry-forward at `pa-e71c011bfa3d4124` — verify with `python tools/pa_chat.py "ping — verify pin active" --tools`
7. **Primary work decision** — propose Candidate A (Phase 4 close, 4 blockers) OR Candidate B (net-new engineering, per S2745 pivot rule). Recommend surfacing both to Chris + letting him choose. Bias toward net-new per the pivot rule unless Chris explicitly wants to close Phase 4 first.
8. **On acceptance of Phase 4 close:** ship a single close-doc PR (blocker #4) referencing verifications done for blockers #1-#3. Do NOT interleave with substrate PRs.
9. **On acceptance of net-new:** Chris names the specific slice; scope + Rigby SIGN before code.
10. **Docs cascade** — if not already run, execute the 4-step cascade for S2750 shipped docs (this file + SESSION_2750 handoff). Report chunk count in a follow-on PR.

---

## Reference documents

Ordered by frequency of use:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor v0.4.1)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — Phase 4 architecture (§6 steps 12+14 DONE, §7 criterion #4 DONE, §8 chain-of-custody with S2750 rows)
5. [`docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md`](docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md) — AST rule spec (path 2 fallback design)
6. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — Phase 1 ledger with §5.1.b + §14 tally amendments
7. [`docs/research/platform/platform_capability_graph.md`](docs/research/platform/platform_capability_graph.md) — capability chains + append-only refreshes
