# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0100 STAGE 2 ARCHITECTURE COMPLETE; STAGE 3 PRE-FLIGHT READY

**Refreshed 2026-07-06 per IOS §15.15.** Both required Stage 2 ADRs ratified. Transitioning from architecture to implementation.

### Phase

**`implementation`.** IOS `active v1.5` on `main`. Research paused per §15.3.

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`

### Current stage

- **Stage:** `2`
- **`stage_state`:** `active` (both required ADRs ratified; optional ADR-C not authored; Stage 3 pre-flight ready to open on Chris directive)

### Stage 2 ADR outcomes

| ADR | Slug | Status | Ratified | PR |
|-----|------|--------|----------|-----|
| **ADR-0001** | `establish-adr-corpus` | accepted | 2026-07-06 | #2948 |
| **ADR-0002** (ADR-B) | `pa-write-shape-and-correlation-contract` | accepted | 2026-07-06 | #2951 |
| **ADR-0003** (ADR-A) | `mission-runner-staged-enable-posture` | accepted | 2026-07-06 | #2953 |
| ADR-0004 (ADR-C, optional) | `d74-six-axis-correlation-spine-posture` | not authored | — | — |

### Next executable action

**Chris sequencing directive determines next action.** Four candidate paths per architecture-to-implementation transition:

- **(a) Open Stage 3 pre-flight for P2 (IB-1799-T1-01).** SPEC_COMPLETE per F3 fold — ships unconditional of any ADR. Lightest runtime path; useful early-wins arc-signaler.
- **(b) Open Stage 3 pre-flight for P4 (IB-1799-T1-02).** Requires ADR-0002 (satisfied). Discharges PA correlation gap. Data migration + write logic + regression tests. See ADR-0002 §3 for full spec.
- **(c) Open Stage 3 pre-flight for P3 (IB-1799-T1-03).** Requires ADR-0003 (satisfied) + Stage 3 pre-flight assumption-lock gate per ADR-0003 §3.3.a (6-row table). Ships `manage.py delegation_lifecycle_smoke_test` + Phase 1 + Phase 2 flag flip + auto-disable trigger implementation.
- **(d) Author ADR-0004 (ADR-C).** Optional per F4 fold. Requires standalone design-prep per IOS v1.5. Architecture-only track per F1 fold (no in-arc migrations beyond P2/P4).

Full dependency graph in the ratification report attached to #2953 merge.

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be` (label `ios-arc-open-I-0100`). No rotation. Retirement due at Stage 6 close per §7.2.
- **Paused-research pin preserved:** `pa-44a6eb70d8814e34` (T4 Group 1700).

### Pending PRs

| # | Title | State |
|---|-------|-------|
| _(none)_ | — | — |

All Stage 2 architecture PRs merged. No open PRs pending Chris review.

---

## Read as background (Level C step C.4–C.6 loads for Stage 3 pre-flight opening)

- All three accepted ADRs:
  - `docs/adr/ADR-0001-establish-adr-corpus.md`
  - `docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md`
  - `docs/adr/ADR-0003-mission-runner-staged-enable-posture.md`
- Both design-prep artifacts (canonical §4.3.a examples):
  - `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md`
  - `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md`
- Arc I-0100 scoping doc §5 (planned PR sequence) + §7 (anti-scope + risks + mitigations) + §9.3 (verification-method interface).
- 1799 xx99 §1 verdicts + §5 D74 + §8.2 T1 items 2–3.
- IOS v1.5 (particularly §4.3 Stage 3 pre-flight + §5.1 pre-code gates + §5.2 pre-merge gates + §5.3 post-merge gates + §5.4 migration + rollout + rollback discipline + §12.5 cascade + §15.15 this-file ownership).
- Runtime files touched by P2/P3/P4 (per ADR references):
  - `core/services/tool_dispatcher.py`, `core/agents/base_agent.py`, `core/services/unified_pa_entrypoint.py` (P2 + P4)
  - `core/models_unified_system.py` (P4 data migration for canonical `PersonalAssistant` Agent row)
  - `core/signals/rigby_delegation_signals.py`, `core/services/rigby_mission_delegation.py`, `core/settings.py:138-140` (P3)
- BACKLOG.md IB-1799-T1-01 / T1-02 / T1-03 rows (all IN_ARC).
- MEMORY rules (as usual).
- MEMORY project entry: `project_ios_v15_design_prep_first_class_codification_candidate` (SHIPPED).

---

## Session ready check (before Stage 3 pre-flight opening)

1. **First tool call:** `context-kit orient`.
2. Verify all Stage 2 ADRs accepted on main: `grep '^status: accepted' docs/adr/ADR-000{1,2,3}*.md` returns 3 matches.
3. Verify scoping doc `stage_state: active`.
4. Verify BACKLOG rows: `grep 'IB-1799-T1-0' docs/research/implementation/BACKLOG.md` — T1-01 SPEC_COMPLETE / IN_ARC; T1-02 RATIFIED_ADR / IN_ARC with `adr_ref: ADR-0002`; T1-03 RATIFIED_ADR / IN_ARC with `adr_ref: ADR-0003`.
5. `tools/pa_local.sh "platform_config_tool action=overview"` — verify local context on arc pin `pa-c5b235f7b15f45be`.
6. Read IOS §4.3 Stage 3 pre-flight in full + §5.1 pre-code gates in full.
7. Read the ADR + design-prep for whichever P (2/3/4) Chris directs for Stage 3 pre-flight opening.
8. Chris sequencing directive determines specific next action per §4.3 Stage 3 opening ceremony.
