# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2751 CLOSED — I-0302 PHASE 4 CLOSED (ratified); PHASE 5 (ARC CLOSE / RETRO) AUTHORIZED TO OPEN FOR S2752

**Refreshed 2026-07-10 (SESSION 2751 CLOSED. I-0302 Phase 4 CLOSED with Chris D-verdict "agree all". 1 close-doc PR merged (#3129): standalone `I-030205_phase4_close.md` + ratification record + I-030203 §8 amendments. Rigby SIGN-PASS clean W1..W5 on shipped harness. Cascade run: 2 embed / 55 chunks. Phase 5 (I-0302 arc close / retro) authorized to open. RUR-C1 parent still gates on I-0303 (not-yet-opened). Full session substance in `docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md`.**

Session anchors (read in order):

1. [`docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md`](docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md) — S2751 delivery ledger, Phase 4 close attestation, Rigby SIGN log, session pivot analysis, S2752 open protocol
2. [`docs/research/implementation/tenant_boundary_lockdown/I-030205_phase4_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030205_phase4_close.md) — Phase 4 close doc (§7 recovery gate; §8 lessons; §9 follow-on)
3. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md) — frozen canonical ratification record
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — arch doc (§8 chain-of-custody now ends at S2751)
5. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)

**Prior sessions (background context):** S2750 (Sub-phase 3 CLOSED, 2 PRs); S2749 (Sub-phase 3 partial, 8 PRs); S2748 (Sub-phases 0/1/2 COMPLETE); S2747 (Phase 3 wiring COMPLETE); S2746 (Phase 2 predicate module RATIFIED); S2745 (engineering-pivot directive + cost threshold observation opened); S2742 (Playbook v0.4.1 + RUR CAMPAIGN parent doc + I-0301 CLOSED).

---

## P0 — COST THRESHOLD OBSERVATION CHECK-IN (now actionable — 2026-07-11+)

**Do this FIRST before candidate selection.** Deferred through S2750 → S2751 per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md` — actionable on 2026-07-11 sessions onward. Since S2752 opens on or after 2026-07-11, run the check-in.

**State at open (from S2743-S2750 arc):**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation only)
- Set locally on Chris's dev DB via `python manage.py cost_thresholds --set month 500`
- Observation period started 2026-07-10 07:35 MDT — now ~1 day of accumulation

**Report to Chris at session open:**

1. **Current threshold config** — run `python manage.py cost_thresholds`; confirm `month: $500.00` still set and mode still `monitor`. Flag any drift.
2. **Accumulation** — query `LLMCallLog` (or equivalent cost-accumulation surface used by the beat task) for the period since 2026-07-10 07:35 MDT. Report: total accumulated $, % of $500 ceiling, top 3 cost drivers by model/service.
3. **Anomalies** — any single-hour spike >$20, any new provider showing up, any `[COST_MONITOR]` log lines showing near-threshold behavior. If clean, say so explicitly.
4. **Advance recommendation** — based on observation-period data, is 24+ hours of clean observation enough to advance to `--set-mode freeze` (shadow mode), or does Chris want to observe longer? Rigby SIGN on the recommendation before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.** Per S2735 P1 gate discipline.

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` ("Rigby: Cost threshold observation period — opened 2026-07-10 (S2744)").

---

## P0.5 — CI BILLING STATUS CHECK

**Do this SECOND, right after the cost check-in.** Confirmed at S2751 open on run 29139031286: still `conclusion: failure` with "recent account payments failed / spending limit needs increase" annotation. Every merge this session used `--admin` per `feedback_gh_pr_merge_admin_until_billing_fixed.md`.

**Report to Chris at session open:**

1. **Fresh CI run** — trigger any recent PR's CI or check `gh api /repos/clwest/donkey-betz-platform/actions/runs -q '.workflow_runs[0]'` to see the latest run's `conclusion` + annotations. If billing is fixed, `conclusion: success` will surface on a new run.
2. **Flag state** — if CI is green again: drop the `--admin` flag from `gh pr merge` calls this session, delete the memory file `feedback_gh_pr_merge_admin_until_billing_fixed.md`, and remove the corresponding line from `MEMORY.md`.
3. **If still billing-blocked:** continue `--admin` merges; every PR body includes a "Local verification limits" section stating what was verified locally as the fallback quality gate.
4. **Cross-check Phase 4 close recovery gate** — if CI becomes green during S2752, note in `docs/handoffs/SESSION_2752_*.md` whether the first `tests/security/**`-touching PR run passed. If any Phase 4 test module regresses on that first green run, Phase 4 close reopens per `RATIFICATION_2026-07-10_i0302_phase4_close.md` §5.

---

## OPEN RUNTIME ITEMS (from S2751 close)

1. **PA celery worker bounce.** Rigby stall fix (#3119) still not activated — running PA celery worker has pre-#3119 code loaded. To activate: `pkill -f celery && OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES make celery`. Deferred to Chris; not urgent — pre-#3119 behavior remains functional (Anthropic fallback + response body capture are opt-in improvements).
2. **P0 observation check-in** — see above; NOW ACTIONABLE.
3. **P0.5 CI billing status** — see above; blocks lint-enforcement flips + `--admin` flag posture + Phase 4 close behavioral-verify recovery gate.
4. **Session pin rotation** — `pa-e71c011bfa3d4124` was the S2749 arc pin; Phase 4 arc-scoped closure natural retire point. Recommend retire at S2752 open unless immediately opening Phase 5 (which would keep an arc pin useful). Verify via `session_tool.retire conversation_id=pa-e71c011bfa3d4124`.

---

## PRIMARY WORK CANDIDATES — S2752

### CANDIDATE A — I-0302 PHASE 5 (arc close / retro)

Phase 5 authorized to open per `RATIFICATION_2026-07-10_i0302_phase4_close.md` §6. Ship pattern per Phase 2 → Phase 4 precedent:

1. Draft Phase 5 arc-close doc — `I-030299_i0302_arc_close.md` (following the I-030199 arc-close pattern for I-0301).
2. Retrospective content: cross-phase patterns, F-block ledger roll-up, playbook-candidate finalization per two-triggers threshold tracked in `I-030205 §8.4` (report-only→batch-fix→enforce three-PR pattern is at 2 triggers; watchpoint-attestation SIGN shape is at 1 trigger; behavioral-verify recovery gate is at 1 trigger).
3. Rigby SIGN cycle on Phase 5 arc close doc.
4. Chris D-verdict on Phase 5 arc close → I-0302 arc CLOSED.
5. On I-0302 arc close: assess I-0303 open readiness and RUR-C1 parent close gate.

Composition: single arc-close PR + ratification record + INDEX+DOCS cascade. Same 1-PR shape as S2751 close-doc PR.

### CANDIDATE B — I-0303 (async-boundary enforcement) OPEN

RUR-C1 parent close blocks on I-0303 shared cross-tenant regression per Q2 D-verdict. Open scoping doc (mirrors I-0302 scoping doc pattern): audit + boundary claim + phase decomposition. This is a fresh arc-open, not an execution session.

### CANDIDATE C — NET-NEW ENGINEERING (per S2745 engineering-bias rule)

Carry-forward from S2751 open menu. Chris considered B3a (Cost Guardian dashboard tab) but pivoted to Phase 4 close. If S2752 wants a break from RUR arcs, propose:

1. **B3a — Cost Guardian dashboard tab** (Claude S2751 lean; Rigby de-risk asks: lock MVP to 3 tiles + 1 table, LLMCallLog-first, decide admin-only vs. redacted-for-users up front)
2. **B1a — Cost Guardian Employee OS employee** (backend-only variant of B3a)
3. **New spider on a Chris-named data gap**

### CANDIDATE D — META-METHODOLOGY (only if Chris explicitly asks)

- **"Phase-close doc + ratification record + arch amendments = 1 PR"** — 1 trigger from S2751. Watch for second in a future phase close (e.g. Phase 5 close) before codifying.
- **"Watchpoint-attestation SIGN (W1..Wn) shape"** — 1 trigger. Codify if applied a second time cleanly (Phase 5 close is a natural second trigger).
- **"Behavioral-verify recovery gate on CI-billing-blocked closes"** — 1 trigger. Watch for repeat use before playbook §11.x subsection.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `f341581a` (PR #3129 merged; I-0302 Phase 4 CLOSED) — plus cascade PR (this session close-out) |
| Playbook version | v0.4.1 (unchanged since S2742) |
| Playbook rule count | 196 |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-e71c011bfa3d4124` (active — S2749 arc pin; retire at S2752 open unless immediately opening Phase 5) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-e71c011bfa3d4124` (rotate on retire) |
| Live infra state | Cost threshold monitor mode $500/mo (observation period ~1 day at S2752 open); PA celery worker running pre-#3119 code (bounce needed to activate stall fix); CI billing-blocked (`--admin` flag on merges per memory rule) |
| RUR arc state | I-0301 CLOSED · I-0302 Phases 1-4 CLOSED · Phase 5 authorized to open · I-0303 not yet opened · RUR-C1 parent OPEN |

---

## What S2751 shipped

Full delivery ledger in `docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md` §1. Compressed:

| PR | Content | HEAD |
|---|---|---|
| #3129 | I-0302 Phase 4 CLOSED — ratification + close doc + arch amendments | `f341581a` |

Plus this session's cascade PR (this file + handoff + docs/INDEX.md refresh + step 4 embed).

**Cumulative Phase 4 arc (S2748 → S2751): 15 PRs (14 substrate + 1 close-doc), 6 harness modules under `tests/security/`, 50 matrix cells, 28 enforcing sentinels, AST + coverage-gap + VIP-carve-out, 1 ratification record. Full roll-up in `I-030205_phase4_close.md` §1 + §3.**

---

## Recommended session-open protocol (S2752)

1. `context-kit orient`
2. Read `docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md` in full — §2 close attestation + §4 SIGN log + §5 session pivot analysis + §9 what this session taught us
3. Verify runtime state: `git log --oneline -5`, `celery inspect ping`
4. **P0 check** (now actionable): run the observation check-in from §P0 above
5. **P0.5 CI billing status** — check + flag drop if resumed; Phase 4 close recovery gate cross-check
6. **Session pin decision** — retire `pa-e71c011bfa3d4124` or carry-forward; depends on S2752 work choice
7. **Primary work decision** — propose Candidate A (Phase 5 arc close) OR Candidate B (I-0303 open) OR Candidate C (net-new engineering). Surface all three to Chris via Rigby; recommend A per RUR arc momentum unless Chris explicitly wants a break.
8. **On acceptance of Phase 5 close:** draft `I-030299_i0302_arc_close.md` in the same 1-PR shape as S2751 (close doc + ratification + INDEX + cascade). Do NOT interleave with any other substrate work.
9. **Docs cascade** — run the 4-step cascade for whatever docs S2752 ships; report chunk count in follow-on PR.

---

## Reference documents

Ordered by frequency of use:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor v0.4.1)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030205_phase4_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030205_phase4_close.md) — Phase 4 close doc (S2751)
5. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md) — Phase 4 ratification record (frozen)
6. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — Phase 4 architecture (§8 chain-of-custody ends at S2751)
7. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — Phase 1 ledger
8. [`docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md`](docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md) — AST rule spec
9. [`docs/research/implementation/tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md) — I-0301 arc close (sibling precedent for Phase 5 arc-close doc shape)
10. [`docs/research/platform/platform_capability_graph.md`](docs/research/platform/platform_capability_graph.md) — capability chains + append-only refreshes
