# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0100 STAGE 2 ADR-B RATIFIED; NEXT ACTION IS ADR-0003 (ADR-A) AUTHORING

**Refreshed 2026-07-06 per IOS §15.15** (ratification-of-ADR-in-arc PR type). If any field below disagrees with `main` reality, `main` wins per §15.3 supersession.

### Phase

**`implementation`.** IOS status: `active v1.4` on `main`. Research trajectory (T4 Group 1700 Observability arc-open per S2699 close) is **PAUSED** per IOS §15.3 phase-transition supersession rule.

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`
- **Scoping doc:** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md`

### Current stage

- **Stage:** `2`
- **`stage_state`:** `active` (Stage 2 opened 2026-07-06 via P0 prep PR #2948 merge; ADR-B ratified 2026-07-06 as ADR-0002)

### Stage 2 ADR ratification progress

| ADR | Slug | Status | Ratified | Notes |
|-----|------|--------|----------|-------|
| **ADR-0002** (ADR-B) | `pa-write-shape-and-correlation-contract` | **accepted** | 2026-07-06 | Chris agree-all-F1-F8; Option 1 per-turn AgentExecution + Sub-option 1(i) canonical PA Agent row. Unblocks P4. |
| ADR-0003 (ADR-A) | `mission-runner-staged-enable-posture` | **proposed** (NOT YET AUTHORED) | (pending) | Next executable ADR authoring session. Ratifies SECOND per F4 fold. |
| ADR-0004 (ADR-C, optional) | `d74-six-axis-correlation-spine-posture` | **proposed** (NOT YET AUTHORED) | (pending) | Optional per F4 fold; ratifies THIRD if pursued. |

### Next executable action

**Author `docs/adr/ADR-0003-mission-runner-staged-enable-posture.md`** with a preceding standalone design-preparation document per IOS §4.3 Stage 2 v1.4 (see §15.15 notes on design-prep first-class question below).

Concrete sequence for the next session:

1. **First tool call:** `context-kit orient`.
2. **Verify state:** ADR-0002 status `accepted` on main via `grep '^status:' docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md`; ADR-0003 file does not yet exist via `ls docs/adr/`.
3. **Author standalone design-prep doc** — `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md`. Content:
   - Decision question: `MISSION_RUNNER_ENABLED` + `RIGBY_DELEGATION_ENABLED` staged-enable posture per F8-iii mitigation.
   - Options: shadow-mode-only enable, shadow → partial (10% cohort) → full, direct full-enable (rejected), etc.
   - Constraints: F8-iii three-stage enable pattern; R2 OpsRunEvent volume sampling/cap threshold gate; R3 delegation handler dormancy risk — dormant since S1250 PR8 wire-up.
   - Consequences per option: OpsRunEvent write volume, handler error visibility, rollback ease.
   - Verification implications: how each option ratifies the Stage 3 pre-flight verification-method interface for IB-1799-T1-03.
4. **Draft ADR-0003** per ADR-0001 §3.3 frontmatter + §3.4 body sections. Cite design-prep as source.
5. **Route Rigby SIGN Cycle 1** per §7.2 v1.4: single-batch × 2–4-Q (ADR-A has fewer decision axes than ADR-B; 2-Q minimum, 4-Q typical) on arc pin `pa-c5b235f7b15f45be`. Do NOT rotate.
6. **Fold SIGN edits** + present Chris ratification card via Rigby.
7. **Open ADR-0003 PR** with cascade + evidence block + `00-START-NEXT-SESSION.md` refresh per §15.15 (this-file refresh).

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be` (label `ios-arc-open-I-0100`). Retirement due at Stage 6 close per §7.2. Do NOT rotate between ADRs per §7.2 v1.4.
- **Paused-research pin preserved:** `pa-44a6eb70d8814e34` (T4 Group 1700).

### Pending PRs

| # | Title | State |
|---|-------|-------|
| **#TBD** (this PR) | ADR-0002 authoring + design-prep — ADR-B ratified | `OPEN` (awaiting Chris review + merge) |

Once #TBD merges, no pending PRs until ADR-0003 authoring begins.

---

## Notes on IOS v1.5 candidate refinement (design-prep first-class question — deferred pending Chris directive)

Task #39 evaluation surfaced Arc I-0100 ADR-B design-prep authoring as strong evidence that **design-preparation should become a first-class IOS artifact rather than an optional §4.3 Stage 2 v1.4 equivalence rule**. The equivalence rule creates a judgment call at every Stage 2 opening that will systematically fail because scoping doc §9 (a Stage 1 artifact) does not read upstream code and cannot enumerate consequences-per-option at design-prep depth. See ratification report for full analysis.

**Recommendation:** Ship IOS v1.5 codifying:

- §4.3 Stage 2 revision: mandatory standalone design-prep for every `NEEDS_ADR` intake with `design_state: POSTURE_PENDING` or `NONE`. `SPEC_COMPLETE` intake rows still skip.
- §4.3 Stage 2 design-prep canonical template: 3-option-×-5-field consequence-matrix + pressure-test structure used in Arc I-0100 ADR-B design-prep.
- §12.5.b RAG-critical artifact list: add design-prep docs explicitly.
- §14.2 note: Chris refinement-authority prerogative precedent at v1.1/v1.2/v1.3/v1.4 sets pattern for single-trigger codification when the trigger is a systematic gap observation.

**Awaiting Chris directive:** ship IOS v1.5 now, or wait until ADR-A design-prep confirms two-trigger threshold, or defer indefinitely.

---

## Read as background (Level C step C.4–C.6 loads specific to Arc I-0100 Stage 2 post-ADR-B)

- `docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md` (**accepted 2026-07-06** — reference for ADR-A body-section shape + provenance discipline).
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md` (design-prep template + canonical example).
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md` §7.3 R3 (delegation handler dormancy risk — ADR-A context); §8 F8 (three risks + F8-iii staged-enable pattern); §5 P3 row (planned rollout for IB-1799-T1-03).
- `docs/research/domains/observability/1799_observability_canonical_summary.md` §1 point 3 (Cat E OpsRun/OpsRunEvent design-intent-latent evidence); §8.2 T1 item 3 (MISSION_RUNNER + RIGBY_DELEGATION staged unlock).
- `core/services/rigby_delegation_signals.py:79-84` (S1250 PR8 handler; RIGBY_DELEGATION_ENABLED gated; 0/224 rows carry execution_id).
- `settings.py` (`MISSION_RUNNER_ENABLED`, `RIGBY_DELEGATION_ENABLED` feature flag defaults).
- `docs/adr/ADR-0001-establish-adr-corpus.md` §3.3 + §3.4 (frontmatter + body-section templates).
- IOS §4.3 Stage 2 + §7.2 v1.4 implementation ADR SIGN cadence + §12.5 cascade + §15.15 this-file ownership.
- MEMORY rules: `feedback_session_open_with_orient`, `feedback_claude_directs_rigby_then_verifies`, `feedback_docs_cascade_at_every_close`, `feedback_cascade_pr_must_include_embed_step`, `feedback_rigby_sign_worker_instability_recovery`.

---

## Session ready check (before authoring ADR-0003)

1. **First tool call: `context-kit orient`** per MEMORY workflow rule.
2. Verify ADR-0002 accepted + on main: `grep '^status:' docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md` returns `status: accepted`.
3. Verify ADR-0003 not yet authored: `ls docs/adr/` shows only ADR-0001 + ADR-0002.
4. `tools/pa_local.sh "platform_config_tool action=overview"` — verify local context under arc pin `pa-c5b235f7b15f45be`.
5. Read ADR-0002 §3 (Decision structure) + §4 (Consequences) + §5 (Alternatives) + §7 (Provenance) — template for ADR-0003 body.
6. Read Arc I-0100 scoping doc §7.3 R3 + §8 F8-iii + §5 P3 + §9.1 line 3 (ADR-A pre-scoping content).
7. Read 1799 xx99 §1 point 3 + §8.2 T1 item 3 (Cat E OpsRun/OpsRunEvent + MISSION_RUNNER staged unlock).
8. Read `core/services/rigby_delegation_signals.py` and `settings.py` for current flag state + handler code.
9. Author standalone design-prep doc for ADR-A (path listed in "Next executable action" step 3).
10. Draft ADR-0003 per ADR-0001 §3.3 + §3.4 templates.
11. Route Rigby SIGN Cycle 1 per §7.2 v1.4 on arc pin (no rotation).
12. Fold Rigby edits inline + present Chris ratification card.
13. Open ADR-0003 PR with cascade + evidence block + this-file refresh.
