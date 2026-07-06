# Next Session — Start Here

---

## READ THIS FIRST — IOS v1.5 REFINEMENT IN FLIGHT; ARC I-0100 STAGE 2 ADR-A AUTHORING BLOCKED PENDING v1.5 MERGE

**Refreshed 2026-07-06 per IOS §15.15** (IOS patch PR type — v1.4 → v1.5 design-prep first-class artifact refinement).

### Phase

**`implementation`.** IOS status: `active v1.5` on branch `docs/ios-v1.5-design-prep-first-class-artifact` (until merge). `active v1.4` on `main` (until v1.5 PR merges). Research trajectory paused per §15.3.

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`
- **Scoping doc:** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md`

### Current stage

- **Stage:** `2`
- **`stage_state`:** `active` (Stage 2 opened + ADR-B ratified as ADR-0002 via #2951 merged 2026-07-06; ADR-A authoring NOT yet started)

### Stage 2 ADR progress

| ADR | Slug | Status | Notes |
|-----|------|--------|-------|
| **ADR-0002** (ADR-B) | `pa-write-shape-and-correlation-contract` | **accepted** 2026-07-06 | Chris agree-all-F1-F8; unblocks P4. |
| ADR-0003 (ADR-A) | `mission-runner-staged-enable-posture` | **NOT authored — blocked pending v1.5 merge** | Per Chris directive: standalone design-prep required (per equivalence-assessment finding on scoping §9.1 line 3). v1.5 codifies this as mandatory. |
| ADR-0004 (ADR-C, optional) | `d74-six-axis-correlation-spine-posture` | **NOT authored** | Optional per F4; blocked on ADR-A completion. |

### Next executable action

**Merge IOS v1.5 patch PR (#TBD — number assigned on push).**

Once v1.5 merges:

1. `context-kit orient` first tool call.
2. Verify IOS v1.5 active on main: `grep '^status:' docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` returns `status: active v1.5`.
3. **Author standalone design-prep artifact for ADR-A** per new IOS v1.5 §4.3 mandatory rule + §4.3.a canonical template. File: `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md`. Content per §4.3.a canonical structure (§1 Context / §2 Decision Qs / §3 Constraints / §4 Options × consequence-field matrix / §5 Pressure test / §6 Verification implications / §7 Recommendation / §8 Alternatives / §9 Provenance / §10 optional meta-methodology).
   - Decision questions: `MISSION_RUNNER_ENABLED` + `RIGBY_DELEGATION_ENABLED` staged-enable posture; rollback triggers; observability during phases.
   - Options: shadow-only-permanent, shadow → partial (10%) → full (F8-iii baseline), direct full-enable, canary-per-instance, hybrid. Minimum 3 per §4.3.a.
   - Constraints: F8-iii pattern from scoping F8 fold; R2 OpsRunEvent volume-spike; R3 delegation handler dormancy since S1250 PR8; ADR-0002 §3.3 F7 warning on ToolCallRecord.conversation_id UUID mismatch propagates.
   - Cross-refs to ADR-0002 §3.3 F6 (parent_execution_id chain) — delegation-triggered executions populate `parent_execution_id = <pa_execution_id>`.
   - Update `stage_state: active → design-prep-in-flight` in the design-prep authoring commit per §4.3.0 v1.5 flip discipline.
4. **Author ADR-0003** citing design-prep as canonical source per new §4.3 v1.5 rule.
5. **Rigby SIGN Cycle 1** on ADR-0003 per §7.2 v1.4 (single-batch × 2–4-Q on arc pin `pa-c5b235f7b15f45be`; no rotation).
6. **Fold + Chris ratification card via Rigby.**
7. **Open ADR-0003 PR** with design-prep + ADR both bundled OR separately (either shape permitted per §4.3.a bundling rule).
8. **Cascade** + `00-START-NEXT-SESSION.md` refresh per §15.15.
9. **Update `stage_state: design-prep-in-flight → active`** at ADR-0003 ratification.

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be` (label `ios-arc-open-I-0100`). No rotation between ADRs.
- **Paused-research pin preserved:** `pa-44a6eb70d8814e34` (T4 Group 1700).

### Pending PRs

| # | Title | State |
|---|-------|-------|
| **#TBD** (this PR) | IOS v1.5 design-prep first-class artifact refinement | `OPEN` (awaiting Chris review + merge) |

Once #TBD merges, no other pending PRs until ADR-A design-prep authoring begins.

---

## Read as background (Level C step C.4–C.6 loads specific to ADR-A authoring under IOS v1.5)

- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5 (particularly §4.3 Stage 2 v1.5 mandatory design-prep rule + §4.3.a canonical template + §4.3.0 stage_state enum with new `design-prep-in-flight` sub-state + §12.5.b RAG-critical list with design-prep added + §14.1 codification example marking design-prep-first-class as codified + §14.2.a Chris refinement-authority prerogative formalization).
- **`docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md`** — **canonical reference example** for §4.3.a template. Read in full before authoring the ADR-A design-prep.
- `docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md` — ADR shape template + F5/F6/F7 correlation-contract semantics that ADR-A must respect (delegation-triggered executions populate `parent_execution_id`).
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md` §7.3 R3 (delegation handler dormancy risk) + §8 F8 (three risks + F8-iii staged-enable pattern) + §5 P3 (planned rollout for IB-1799-T1-03) + §9.1 line 3 (ADR-A pre-scoping — INSUFFICIENT per equivalence assessment).
- `docs/research/domains/observability/1799_observability_canonical_summary.md` §1 point 3 (Cat E OpsRun/OpsRunEvent design-intent-latent evidence) + §8.2 T1 item 3.
- `core/services/rigby_delegation_signals.py` (S1250 PR8 handler; RIGBY_DELEGATION_ENABLED-gated).
- `settings.py` (MISSION_RUNNER_ENABLED, RIGBY_DELEGATION_ENABLED defaults).
- `docs/adr/ADR-0001-establish-adr-corpus.md` §3.3 + §3.4 (frontmatter + body templates).
- MEMORY rules (as usual): `feedback_session_open_with_orient`, `feedback_rigby_comms`, `feedback_claude_directs_rigby_then_verifies`, `feedback_docs_cascade_at_every_close`, `feedback_cascade_pr_must_include_embed_step`, `feedback_rigby_sign_worker_instability_recovery`.
- MEMORY project entry: `project_ios_v15_design_prep_first_class_codification_candidate` — codification history. Update after v1.5 merges to mark candidate as SHIPPED.

---

## Session ready check (before ADR-A design-prep authoring)

1. **First tool call: `context-kit orient`**.
2. Verify IOS v1.5 active on main: `grep '^status:' docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` returns `active v1.5`.
3. Verify ADR-A files not yet exist: `ls docs/adr/ADR-0003*` returns not-found; `ls docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_*` returns not-found.
4. `tools/pa_local.sh "platform_config_tool action=overview"` — verify local context under arc pin `pa-c5b235f7b15f45be`.
5. Read IOS §4.3 Stage 2 v1.5 mandatory-design-prep rule + §4.3.a canonical template (in full).
6. Read Arc I-0100 ADR-B design-prep (`I-0100_design_prep_adr_b_pa_write_shape.md`) in full as canonical reference exemplar.
7. Read ADR-0002 body (§3 + §4 + §5 + §7 §7.1 sub-decision pattern) as ADR body-template exemplar.
8. Read Arc I-0100 scoping §7.3 R3 + §8 F8 + §5 P3 + §9.1 line 3 (ADR-A pre-scoping context).
9. Read 1799 xx99 §1 point 3 + §8.2 T1 item 3 + §5 D74 context.
10. Read `core/services/rigby_delegation_signals.py` + `settings.py` for current handler + flag state.
11. Update `stage_state: active → design-prep-in-flight` in the first ADR-A-touching commit per §4.3.0 v1.5 flip.
12. Author `I-0100_design_prep_adr_a_mission_runner_staged_enable.md` per §4.3.a canonical template. Minimum 3 options; 5-field consequence matrix; pressure test; recommendation.
13. Author `docs/adr/ADR-0003-mission-runner-staged-enable-posture.md` citing design-prep as canonical source.
14. Route Rigby SIGN Cycle 1 per §7.2 v1.4.
15. Fold + Chris ratification card via Rigby.
16. Open ADR-0003 PR (may bundle design-prep + ADR OR ship separately).
17. Cascade + this-file refresh per §15.15.
18. Flip `stage_state: design-prep-in-flight → active` at ADR-0003 ratification housekeeping.
