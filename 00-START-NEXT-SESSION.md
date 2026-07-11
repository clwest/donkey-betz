# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2752 CLOSED — PLAYBOOK v0.5 STAGE 1 SHAPE RATIFIED; STAGE 2 CODIFICATION READY FOR S2753

**Refreshed 2026-07-11 (SESSION 2752 CLOSED — Chris D-verdict "agree all" on Q1-Q5 v0.5 shape questions).**

**S2752 shipped:**

- **Playbook v0.5 Stage 1 shape doc** at `docs/research/platform/playbook_v0_5_proposal_shape.md` (drafted from a terminal-crash recovery, per Chris's B pick "shape now, execute fresh session per Playbook §10.2.2 Stage 1"). Rigby lean-recorded pre-D-verdict; Chris "agree all" on Q1-Q5 ratified.
- **PA pin rotation** `pa-e71c011bfa3d4124` (I-0302 arc pin) → `pa-44541f01cbb14b46` (v0.5 codification scope). Wrapper `tools/pa_local.sh` line 539 updated.
- **Single close-bundle PR** (this session): shape doc + start-here refresh + handoff + pa_local.sh pin update + cascade (dogfooding candidates §5.2 + §5.5 shapes pre-ratification).

**5 v0.5 candidates — SLOTS RATIFIED (Option B):**

| Rule ID | Chapter §7 sub-section | Candidate |
|---|---|---|
| PLAYBOOK-7.4.1 | §7.4 Close-ceremony delivery discipline | Phase-close 1-PR |
| PLAYBOOK-7.4.2 | §7.4 (same) | Phase-close serialization |
| PLAYBOOK-7.4.3 | §7.4 (same) | Close-doc + cascade PR |
| PLAYBOOK-7.5.1 | §7.5 Staged codification | Report-only → batch-fix → enforce three-PR |
| PLAYBOOK-7.6.1 | §7.6 Session-close SIGN-cycle | Watchpoint-attestation SIGN (EXTENDS ROS §6.10.3) |

**Structural finding S2752 codified into shape:** ratification §5's proposed slots under §6.6/§6.10/§6.12 were audit-corrected — 4 of 5 candidates are close-ceremony/delivery discipline (Ch 7 STUB natural fit), not provenance (Ch 6). Ch 7 activation partially executes v0.2+ STUB deferral.

**Version bump analysis (RATIFIED):** MINOR per PLAYBOOK-10.5.1 — 5 additions, 0 modifications. v0.5 continues chain v0.4.1 → **v0.5.0**.

**RUR-C1 parent still gates on I-0303** (unchanged from S2751 close).

Session anchors (read in order at S2753 open):

1. [`docs/research/platform/playbook_v0_5_proposal_shape.md`](docs/research/platform/playbook_v0_5_proposal_shape.md) — Stage 1 shape (frozen; §4 rule shape + §5 slot table + §7 Stage 2 execution plan + D-verdicts resolved in frontmatter)
2. [`docs/handoffs/SESSION_2752_PLAYBOOK_V0_5_STAGE_1_SHAPE_RATIFIED.md`](docs/handoffs/SESSION_2752_PLAYBOOK_V0_5_STAGE_1_SHAPE_RATIFIED.md) — S2752 close handoff (delivery ledger, D-verdict record, terminal-crash recovery note)
3. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md) §5 — original candidacy ratification (frozen; slot proposals superseded by Stage 1 audit)
4. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules; unchanged until Stage 2 ratifies v0.5)
5. [`docs/research/platform/engineering_playbook_evidence_manifest.md`](docs/research/platform/engineering_playbook_evidence_manifest.md) — frozen manifest (Stage 2 adds 13 entries per shape doc §6)

**Prior sessions (background context):** S2751 (I-0302 ARC CLOSED); S2750 (Sub-phase 3 CLOSED); S2749 (Sub-phase 3 substrate largely closed + Rigby stall fix); S2742 (Playbook v0.4.1 + I-0301 CLOSED + I-0302 scoping).

---

## P0 — PLAYBOOK v0.5 STAGE 2 CODIFICATION (per Q4 immediate D-verdict)

**Do this FIRST at S2753 open.** Chris D-verdict at S2752 close on Q4 = fresh session immediately after shape doc lands. Stage 2 is the codification session.

**Execution plan (from shape doc §7):**

1. Session-open orientation (this checklist + shape doc + arc-close ratification + v0.4.1 playbook state).
2. Verify pin `pa-44541f01cbb14b46` still active and scoped to v0.5 codification.
3. Manifest update — add 13 evidence entries to `engineering_playbook_evidence_manifest.md` per shape doc §6 (bundled under v0.5 SIGN per Q5).
4. Draft §7.4/§7.5/§7.6 subsections + Chapter 7 frontmatter update + Appendix D chain row.
5. Run 6-check author verification (PLAYBOOK-6.10.1 verifications 1-6) — record in amendment provenance.
6. Rigby SIGN cycle — using watchpoint-attestation SIGN shape (dogfooding candidate §5.3 / PLAYBOOK-7.6.1 pre-ratification).
7. Chris D-verdict on Stage 2 draft — ratify or block per SIGN findings.
8. Body commit + tag `playbook-v0.5` — single PR per candidate §5.2 / PLAYBOOK-7.4.1 (dogfooding).
9. L7 anchor refresh in CLAUDE.md + workspace ratification record (`RATIFICATION_2026-07-11_PLAYBOOK_V0_5`).
10. 4-step docs cascade + `build_docs_provenance` per memory rule.

**Estimated Stage 2 effort:** 1 focused session. All 5 rule shapes + evidence citations pre-locked in Stage 1.

**Do NOT re-open Q1-Q5 unless Stage 2 audit surfaces new blockers.** Shape is frozen at HEAD post-S2752 close PR.

---

## P0.5 — COST THRESHOLD OBSERVATION CHECK-IN (owed — deferred through S2752)

**Do this SECOND after Stage 2 codification opens.** Deferred through S2750 → S2751 → S2752 per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md`. Actionable 2026-07-11+.

**State at S2752 close (unchanged from S2751):**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation)
- Observation period started 2026-07-10 07:35 MDT

**Report to Chris at S2753 open:**

1. **Current threshold config** — `python manage.py cost_thresholds`; confirm `month: $500.00` still set, mode still `monitor`.
2. **Accumulation** — query `LLMCallLog` since 2026-07-10 07:35 MDT. Report total $, % of $500 ceiling, top 3 cost drivers.
3. **Anomalies** — any single-hour spike >$20, any new provider, any `[COST_MONITOR]` near-threshold log lines. If clean, say so explicitly.
4. **Advance recommendation** — is 24+ hours of clean observation enough to advance to `--set-mode freeze` (shadow mode)? Rigby SIGN before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.**

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83`.

---

## P0.75 — CI BILLING STATUS CHECK (still owed)

**Do this after P0.5.** Still blocked at S2751 close (run 29139031286 same annotation). `--admin` merge flag remains active on all merges (including S2752 close bundle + Stage 2 PRs).

**Report to Chris at S2753 open:**

1. **Fresh CI run** — `gh api /repos/clwest/donkey-betz-platform/actions/runs -q '.workflow_runs[0]'`.
2. **Flag state** — if CI is green: drop `--admin`, delete memory rule `feedback_gh_pr_merge_admin_until_billing_fixed.md`, remove MEMORY.md line.
3. **If still billing-blocked:** continue `--admin` merges + "Local verification limits" PR body sections.
4. **Cross-check arc-close recovery gate** — if CI becomes green during S2753, note whether first `tests/security/**`-touching PR run passes. If any Phase 4 test module regresses on that first green run, **Phase 4 close reopens** per `RATIFICATION_2026-07-10_i0302_phase4_close.md` §5, which cascades to reopening the arc close.

---

## SESSION PIN — CARRIES (do NOT retire at S2753 open)

**Pin `pa-44541f01cbb14b46`** minted at S2752 open for v0.5 codification scope. Rotated cleanly from `pa-e71c011bfa3d4124` (I-0302 arc pin, retired at S2752 open).

**Carries through Stage 2.** Natural retire point = post-v0.5 ratification. Do NOT rotate at S2753 open unless it jams or Chris directs otherwise.

Wrapper `tools/pa_local.sh` line 539 already points at `pa-44541f01cbb14b46`.

---

## OPEN RUNTIME ITEMS (from S2752 close)

1. **PA celery worker bounce** — Rigby stall fix (#3119) still not activated (carried from S2751). To activate: `pkill -f celery && OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES make celery`. Deferred to Chris.
2. **P0.5 cost-threshold observation check-in** — see above; owed since 2026-07-11 first-actionable window.
3. **P0.75 CI billing status** — see above; blocks lint-enforcement flips + `--admin` posture + Phase 4/arc close behavioral-verify recovery gate.
4. **Playbook v0.5 Stage 2 codification** — see P0 above; Q4 immediate D-verdict = P0 at S2753 open.
5. **I-0303 (async-boundary enforcement) OPEN** — RUR-C1 gates on it; blocked until v0.5 ratification lands (per Q4 sequencing — v0.5 first per Chris D-verdict).

---

## PRIMARY WORK — S2753

### PRIMARY WORK — v0.5 STAGE 2 CODIFICATION

Not a work-selection session. Q4 D-verdict at S2752 close locked Stage 2 as immediate P0. See P0 above.

### ADJACENT WORK CANDIDATES (post-v0.5)

Not for S2753 unless Stage 2 blocks:

1. **I-0303 (async-boundary enforcement) open** — RUR-C1 close-gate remaining sub-arc. Opens after v0.5 ratifies per Q4 sequencing.
2. **B3a — Cost Guardian dashboard tab** — Claude S2751 lean carried forward; ties to P0.5 check-in workflow.
3. **Cost Guardian Employee OS employee** — B1a backend-only variant of B3a.
4. **New spider on Chris-named data gap**.
5. **Employee OS employee #4** (backend + admin visibility).

### META-METHODOLOGY (only if Chris explicitly asks)

- **Arc close template extraction** — arc-close doc §9.2 suggestion: extract `I-030199` + `I-030299` common structure into `arc_close_template.md`.
- **Single-session multi-close ceremony pattern** — 1 trigger at S2751; watch for second in a future session.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2752 close bundle SHA (pending merge — will be recorded in S2752 handoff §1) |
| Playbook version | v0.4.1 (unchanged) — **v0.5 Stage 1 shape ratified; Stage 2 codifies at S2753** |
| Playbook rule count | 196 (Stage 2 target: 201) |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-44541f01cbb14b46` (v0.5 codification scope; carries to S2753) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-44541f01cbb14b46` |
| Live infra state | Cost threshold monitor mode $500/mo (observation period ~1 day at S2753 open); PA celery worker running pre-#3119 code; CI billing-blocked (`--admin` on merges) |
| RUR arc state | I-0301 CLOSED · I-0302 CLOSED · I-0303 not yet opened (blocked on v0.5 Stage 2 per Q4 sequencing) · RUR-C1 parent still OPEN |
| v0.5 Stage 1 | SHAPE RATIFIED (Chris "agree all" on Q1-Q5, S2752) |
| v0.5 Stage 2 | Pending (P0 at S2753 open) |

---

## What S2752 shipped

| PR | Content | Notes |
|---|---|---|
| S2752 close bundle | shape doc + start-here refresh + S2752 handoff + pa_local.sh pin update + cascade | Dogfooding candidate §5.2 (1-PR) + §5.5 (combined close+cascade) shapes pre-ratification |

**Cumulative v0.5 codification arc (Stage 1 only, S2752):** 1 PR (this bundle). Stage 2 target: 1 PR (playbook body + tag + ratification record) + 1 cascade PR.

---

## Recommended session-open protocol (S2753)

1. `context-kit orient`
2. Read this file end-to-end (all sections)
3. Read `SESSION_2752_PLAYBOOK_V0_5_STAGE_1_SHAPE_RATIFIED.md` — S2752 delivery ledger + D-verdict record + terminal-crash recovery note
4. Read `docs/research/platform/playbook_v0_5_proposal_shape.md` §4-§8 — locked rule shapes + evidence + Stage 2 plan
5. Verify runtime state: `git log --oneline -5`; confirm `tools/pa_local.sh:539` points at `pa-44541f01cbb14b46`
6. **P0.5 + P0.75** — cost-threshold check-in + CI billing status
7. **P0** — Stage 2 codification per shape doc §7 plan (steps 1-11)
8. **Docs cascade** — 4-step at close; report chunk count

---

## Reference documents

Ordered by frequency of use at S2753:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor still v0.4.1 until Stage 2 refresh)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules); **Stage 2 modifies to v0.5**
4. [`docs/research/platform/playbook_v0_5_proposal_shape.md`](docs/research/platform/playbook_v0_5_proposal_shape.md) — Stage 1 shape (frozen S2752)
5. [`docs/research/platform/engineering_playbook_evidence_manifest.md`](docs/research/platform/engineering_playbook_evidence_manifest.md) — frozen manifest (Stage 2 adds 13 entries)
6. [`docs/handoffs/SESSION_2752_PLAYBOOK_V0_5_STAGE_1_SHAPE_RATIFIED.md`](docs/handoffs/SESSION_2752_PLAYBOOK_V0_5_STAGE_1_SHAPE_RATIFIED.md) — S2752 close handoff
7. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md) — arc-close ratification §5 (candidacy record; Stage 1 audit superseded slot proposals)
