# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0100 STAGE 2 ADR-A (ADR-0003) AWAITING CHRIS RATIFICATION

**Refreshed 2026-07-06 per IOS §15.15.**

### Phase

**`implementation`.** IOS `active v1.5` on `main`. Research paused per §15.3.

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`

### Current stage

- **Stage:** `2`
- **`stage_state`:** `design-prep-in-flight` (per §4.3.0 v1.5 — will flip to `active` at ADR-0003 ratification)

### Stage 2 ADR progress

| ADR | Slug | Status | Notes |
|-----|------|--------|-------|
| **ADR-0002** (ADR-B) | `pa-write-shape-and-correlation-contract` | **accepted** 2026-07-06 (#2951 merged) | Chris agree-all-F1-F8. |
| **ADR-0003** (ADR-A) | `mission-runner-staged-enable-posture` | **proposed** — ratification-pending in this PR | Chris ratification card presented via Rigby on arc pin 2026-07-06. On Chris agree-all-F1-F8, follow-up commit flips status → accepted + stage_state → active. |
| ADR-0004 (ADR-C, optional) | `d74-six-axis-correlation-spine-posture` | not authored | Optional per F4 fold. |

### Next executable action

**Chris ratification of ADR-0003 F1-F8** via Rigby ratification card on arc pin `pa-c5b235f7b15f45be`.

On Chris ratification:
1. Follow-up commit flips ADR-0003 frontmatter `status: proposed → accepted`; populates `ratified: 2026-07-06`, `ratifier: chris`.
2. Flips Arc I-0100 scoping frontmatter `stage_state: design-prep-in-flight → active`.
3. Updates BACKLOG.md `IB-1799-T1-03` row: `design_state: POSTURE_PENDING → RATIFIED_ADR`; append `adr_ref: ADR-0003`.
4. Optional: BACKLOG.md `IB-1799-T1-03` naming correction per ADR-0003 §3.6 (single-flag scope).
5. If bundled with existing PR: amend commit. If separate housekeeping PR: open + merge.
6. `stage_transition_history` frontmatter appended with the ratification event.

If Chris requests specific fold overrides:
1. Apply override + re-run applicable analysis.
2. Re-present ratification card via Rigby.

If Chris overrides top-level Option 5 decision OR F8-iii defensible-skip:
1. Re-open design-prep §4 pressure test.
2. Author revised ADR-0003 draft.
3. Re-route SIGN Cycle 2 (BLOCKED-verdict-equivalent flow).

### After ADR-0003 ratification: authoring ADR-0004 (ADR-C, optional) OR P2/P3/P4 runtime discharge PRs

Per F4 fold ordering complete (ADR-B ratified 2026-07-06; ADR-A ratification pending). Post-ratification options:

- **ADR-0004 (ADR-C, optional per F4):** D74 six-axis correlation-spine posture. Requires standalone design-prep per IOS v1.5. Consumes ADR-0002 correlation contract + ADR-0003 rollout-posture volume projections as INPUT. F1 fold: architecture-only track; no in-arc migrations beyond P2/P4.
- **P2 runtime discharge (IB-1799-T1-01):** `ToolCallRecord.trace_id` write-side fix — SPEC_COMPLETE per F3 fold; ships unconditional of any ADR. Can proceed in parallel with ADR-C.
- **P3 runtime discharge (IB-1799-T1-03):** `manage.py delegation_lifecycle_smoke_test` command + Phase 1 execution + Phase 2 flag flip + auto-disable trigger implementation. Requires ADR-0003 accepted. Stage 3 pre-flight assumption-lock gate per §3.3.a table.
- **P4 runtime discharge (IB-1799-T1-02):** PA write shape runtime implementation per ADR-0002. Data migration for canonical `PersonalAssistant` Agent row + write logic in `unified_pa_entrypoint.py` + regression tests. Requires ADR-0002 accepted (satisfied).

Chris sequencing directive determines next executable action after ADR-0003 ratifies.

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be` (label `ios-arc-open-I-0100`). No rotation. Retirement due at Stage 6 close per §7.2.
- **Paused-research pin preserved:** `pa-44a6eb70d8814e34`.

### Pending PRs

| # | Title | State |
|---|-------|-------|
| **#TBD** (this PR) | Arc I-0100 Stage 2 ADR-A (ADR-0003) — RIGBY_DELEGATION_ENABLED staged-enable posture | `OPEN` (awaiting Chris ratification + PR review + merge) |

---

## Read as background (Level C step C.4–C.6 loads for post-ADR-A ratification session)

- `docs/adr/ADR-0003-mission-runner-staged-enable-posture.md` — this ADR (status `proposed`; flips on Chris ratification).
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md` — design-prep (first artifact under IOS v1.5).
- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5 §4.3 Stage 2 mandatory design-prep rule + §4.3.a canonical template + §7.2 v1.4 ADR SIGN cadence + §12.5 cascade + §15.15 this-file ownership.
- `docs/adr/ADR-0001-establish-adr-corpus.md` §3.3 + §3.4 (frontmatter + body-section templates).
- `docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md` §3.3 (F5/F6/F7 correlation contract propagations to ADR-A).
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md` §5 P3 + §7.3 R2/R3 + §8 F4/F8.
- `docs/research/domains/observability/1799_observability_canonical_summary.md` §1 point 3 + §2.5 + §120.
- `core/signals/rigby_delegation_signals.py` (handler code — R3 dormancy target).
- `core/services/rigby_mission_delegation.py` (`delegate_work_item` — dispatch surface).
- `core/settings.py:138-140` (RIGBY_DELEGATION_ENABLED flag definition).
- MEMORY rules (as usual).
- MEMORY project entry: `project_ios_v15_design_prep_first_class_codification_candidate` (SHIPPED status).

---

## Session ready check (before next executable action)

1. **First tool call:** `context-kit orient`.
2. Verify PR merge state via `git log -8` OR `gh pr view <TBD>` — confirm merged.
3. Verify ADR-0003 accepted on main: `grep '^status:' docs/adr/ADR-0003-mission-runner-staged-enable-posture.md` returns `status: accepted` post-ratification housekeeping.
4. Verify scoping doc `stage_state: active` (post-ratification housekeeping flip).
5. Verify BACKLOG `IB-1799-T1-03` `design_state: RATIFIED_ADR` + inline `adr_ref: ADR-0003`.
6. `tools/pa_local.sh "platform_config_tool action=overview"` — verify local context on arc pin.
7. Chris sequencing directive determines next action:
   - Option (a) Author ADR-0004 (ADR-C) via IOS v1.5 mandatory design-prep + ADR flow (same pattern as ADR-A).
   - Option (b) Open P2 runtime discharge PR (IB-1799-T1-01 SPEC_COMPLETE).
   - Option (c) Open P4 runtime discharge PR (IB-1799-T1-02, requires ADR-0002).
   - Option (d) Open P3 runtime discharge PR (IB-1799-T1-03, requires ADR-0003 + Stage 3 pre-flight assumption-lock gate per ADR-0003 §3.3.a).
