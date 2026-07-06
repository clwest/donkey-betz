# Next Session — Start Here

---

## READ THIS FIRST — IOS PART 11 FIRST QUEUE RATIFIED 2026-07-06; SEED PR PENDING CHRIS APPROVAL; ARC I-0100 OBSERVABILITY SPINE QUEUED

**IOS is `active v1.1` on main** (v1 Chris-ratified 2026-07-06; v1.1 execution-refinement patch shipped same day via PR #2940 after Part 11 first-execution surfaced 7 findings). **Phase = IMPLEMENTATION.** Research trajectory (T4 Group 1700 Observability arc-open per S2699 close) is **PAUSED** per IOS v1.1 §15.3 phase-transition supersession rule until Chris explicitly re-enters research via a Research OS command (`Start / Continue / Close research group NNNN`).

**IOS Part 11 first-queue ratification COMPLETED 2026-07-06.** Chris ratified via Rigby on fresh IOS-scoped SIGN pin `pa-39d3694312ab4326` per new IOS v1.1 §15.14 pin lifecycle. Ratifications recorded canonically at `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md` (frozen).

**Ratification summary (2026-07-06):**
- Tier bands ratified as v0-partial (T0=32, T1=68, T2=91, T3=~180, DEFER=18, Cross-arc=5).
- First implementation arc identity ratified: **`I-0100_observability_spine_mission_evidence_substrate`** (Arc I-0100 — Observability correlation spine + mission evidence substrate). Rigby's recommendation over Claude's default (`I-0100_ios_bootstrap`); Chris accepted.
- T0 posture: individually Chris-gated at Stage 2 entry. **No T0 item is SAFE_AUTONOMOUS unless separately ratified later.**
- CX-P4 sequencing and CX-P7 shape DEFERRED per Axis 4.
- v0-partial snapshot accepted; deep-late xx99 leaf tail tracked as `IDBT-0001 PARTIAL_DISCHARGE HIGH` in `docs/research/implementation/IMPLEMENTATION_DEBT.md`; discharge via arc-scoped Stage 1 re-extraction (Chris implicit preference) OR dedicated third extraction session (backup path).

**Seed PR PENDING Chris approval.** New files under `docs/research/implementation/`:
- `RATIFICATION_2026-07-06_first_queue.md` (canonical frozen ratification record)
- `BACKLOG.md` (living intake register; T0 all enumerated + T1 Arc I-0100 seed rows + representative T1 + summary T2/T3 + DEFER + cross-arc initiatives; PARTIAL_DISCHARGE marker for tail)
- `IMPLEMENTATION_DEBT.md` (living debt register; `IDBT-0001` seed row)
- `00-START-NEXT-SESSION.md` overwrite (this file)

**Chris directive:** "Do not open Stage 1 until the backlog/debt seed PR is ready and I approve it."

---

## FIRST THING NEXT SESSION — CONFIRM SEED PR STATE

1. Run `context-kit orient` at session open (first tool call per MEMORY workflow rule `feedback_session_open_with_orient`).
2. Read this file + `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md`.
3. Check seed PR status via `gh pr view <PR#>` (PR # populated on push; see below):
   - **If MERGED and `docs/research/implementation/` exists on main**: proceed to §"Then Open Arc I-0100 Stage 1" below.
   - **If OPEN with Chris review comments**: read comments; apply requested changes; do NOT open Stage 1.
   - **If OPEN awaiting Chris review**: do NOT open Stage 1; report status to Chris and wait.
   - **If DENIED / CLOSED**: read Chris's rejection reason; escalate for guidance.
4. Verify `tools/pa_local.sh --conversation` per IOS v1.1 §15.14:
   - Active pin should be `pa-39d3694312ab4326` (`ios-part11-first-queue-ratification-v1`) until seed PR approval + Arc I-0100 open.
   - Paused-research T4 pin `pa-44a6eb70d8814e34` should be preserved as comment above `--conversation` line.
   - On Arc I-0100 open (post-seed-PR-approval), retire `pa-39d3694312ab4326` via `session_tool.retire force=true` and mint fresh `session_tool.create_fresh label='ios-arc-open-I-0100'`; rotate `--conversation` to new arc pin.

---

## THEN OPEN ARC I-0100 STAGE 1 — OBSERVABILITY SPINE + MISSION EVIDENCE SUBSTRATE

Only after seed PR merged. Per IOS §4.3 Stage 1 Scoping:

1. **Mint fresh arc-scoped SIGN pin** per §15.14: `session_tool.create_fresh label='ios-arc-open-I-0100'`. Retire the ratification pin `pa-39d3694312ab4326`. Rotate `tools/pa_local.sh` `--conversation` to the new arc pin.
2. **Create arc folder:** `docs/research/implementation/observability_spine_mission_evidence_substrate/`.
3. **Draft Stage 1 scoping doc:** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md`. Include per IOS §4.3 Stage 1:
   - Arc identity + slug + first-arc-override justification (Rigby's meta-argument: broken observability breaks verification-method for every downstream intake row per §2.2).
   - Intake seed rows: `IB-1799-T1-01` (`ToolCallRecord.trace_id` 100% NULL fix) + `IB-1799-T1-02` (PA agents bypass `AgentExecution` writes) + `IB-1799-T1-03` (OpsRun/OpsRunEvent behind `MISSION_RUNNER_ENABLED`). Chris confirmed these three as the minimum seed at 2026-07-06 ratification (Axis 2 Chris disposition, RATIFICATION doc §2 Axis 2).
   - **Stage 1 also discharges IDBT-0001 for the 1799 domain slice** — before Stage 2 opens, re-extract 1799 §8 in full at leaf granularity and append discovered rows to `BACKLOG.md` with `chris_gate: RATIFIED` inherited from band-level ratification. Candidate additional rows: `IB-1799-T0-02` (unified retention posture; T0 gates dependent T1 work); `IB-1799-T1-*` tail (retention per-model policy + failure-cluster aggregator + observability→HAI escalation).
   - Blast-radius + risk-class + expected-ship-size classification per §2.2.
   - Owner assignment per §7 (Claude session-slug or `chris` or `rigby`).
   - Verification-method-per-intake pre-fill sketch (populated at Stage 3 pre-flight; sketched at Stage 1).
   - Dependencies + blocks maps.
   - Rollback plan sketch per §5.4.
   - PR sizing per §6 (target: 3–8 findings per arc, ≤3,000 LOC, S/M PR sizes).
   - §14 anchor-update batch pre-declaration (what will be updated at Stage 6 close).
4. **Route Stage 1 scoping doc to Rigby SIGN cycle 1** per IOS §7.2 Stage 1 SIGN discipline (single-batch × 4-Q cadence, matching S1300–S2699 established pattern).
5. **Fold SIGN edits + present Chris ratification card** (via Rigby on arc-scoped pin). Chris ratifies Stage 1 exit.
6. **Stage 2 entry** — only after `IB-1799-T0-02` retention posture ADR ratifies (if it comes into scope) OR `MISSION_RUNNER_ENABLED` posture ADR ratifies. Otherwise Stage 2 opens directly to design-prep for `IB-1799-T1-01` (`ToolCallRecord.trace_id` fix) which is `SPEC_COMPLETE` per S1704 F1 evidence and can skip ADR authoring.

---

## RESEARCH OS TRAJECTORY — PAUSED

T4 Group 1700 Observability research arc-open remains queued per S2699 xx99 close but is **PAUSED** for the duration of the IOS implementation phase per IOS v1.1 §15.3 phase-transition supersession. To re-enter research:
- Chris issues explicit Research OS command (`Start research group 1700: Observability` per playbook §21 vocabulary + OS §3.2 deterministic route).
- On re-entry, `tools/pa_local.sh` `--conversation` rotates from active IOS pin back to `pa-44a6eb70d8814e34` per §15.14 restoration rule.

**Note on domain overlap.** Arc I-0100 (implementation-phase Observability Spine) and T4 Group 1700 Observability (research-phase) touch the same domain. IOS §7.2 no-parallel-arcs rule + §4.4 apply to same-surface work — same-surface implementation waits for research arc close. But the T4 Group 1700 arc has NOT been opened yet; it's queued. Arc I-0100 does not violate the no-parallel rule because there's no active same-surface research arc. If T4 Group 1700 opens mid-Arc-I-0100, Arc I-0100 pauses at its current Stage per §9.1 (sequential arcs on overlapping surface).

---

## CURRENT STATE SUMMARY (2026-07-06)

- **IOS status:** `active v1.1` on main (once PR #2940 merges) / on branch `docs/ios-v1.1-execution-refinement-patch` (until merge).
- **Phase:** IMPLEMENTATION (pre-first-arc; awaiting seed PR approval).
- **Active arc:** None yet. First arc `I-0100` queued pending seed PR approval + Stage 1 open.
- **Active SIGN pin:** `pa-39d3694312ab4326` (`ios-part11-first-queue-ratification-v1`), rotated into `tools/pa_local.sh` `--conversation` per §15.14. Paused-research T4 pin `pa-44a6eb70d8814e34` preserved as comment above line.
- **Backlog register:** `docs/research/implementation/BACKLOG.md` (seeded 2026-07-06; T0 + Arc I-0100 seed rows + representative T1 + DEFER + cross-arc initiatives enumerated; T2/T3 tail flagged as IDBT-0001 PARTIAL_DISCHARGE HIGH).
- **Debt register:** `docs/research/implementation/IMPLEMENTATION_DEBT.md` (seeded with IDBT-0001).
- **Ratification record:** `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md` (frozen).
- **PRs open:**
  - `#2940` (`docs/ios-v1.1-execution-refinement-patch`) — IOS v1.1 execution-refinement patch (Chris review pending).
  - **`#TBD`** (`docs/ios-part11-first-queue-seed`, stacked on #2940) — this seed PR (Chris review pending).

## READ AS BACKGROUND

- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.1 (particularly §11.2 Step 1 v1.1 leaf-granularity rule + §11.3 first-arc-override + §15.14 pin lifecycle + §15.3 v1.1 phase-transition supersession).
- `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md` (canonical Chris disposition per axis).
- `docs/research/implementation/BACKLOG.md` (tier bands + T0 + Arc I-0100 seed rows enumerated).
- `docs/research/implementation/IMPLEMENTATION_DEBT.md` (IDBT-0001 PARTIAL_DISCHARGE HIGH).
- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (upstream truth-discovery OS; still authoritative for research work when Chris re-enters research phase).
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (research-class specialization; not consumed during Arc I-0100 unless Chris re-enters research).
- `docs/research/ARCHITECTURE_INDEX.md` (research library navigation; still valid — implementation arcs will register here per §1 alongside research arcs).
- `docs/research/OPEN_ARCS.md` (in-progress = empty; T4 Group 1700 paused; Arc I-0100 opens on seed PR approval).
- `docs/topics/celery-workers.md` + `docs/topics/infrastructure.md` (existing observability context for Arc I-0100 Stage 1 input).
- MEMORY.md rules (`feedback_session_open_with_orient`, `feedback_rigby_comms`, `feedback_claude_directs_rigby_then_verifies`, `feedback_docs_cascade_at_every_close`, `feedback_cascade_pr_must_include_embed_step`, `feedback_rigby_sign_worker_instability_recovery`).

## SESSION READY CHECK (before opening Arc I-0100 Stage 1)

Only run this checklist AFTER seed PR merged:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active IOS pin (or fresh arc pin post-rotation).
2. Read `docs/research/implementation/BACKLOG.md` T0 + Arc I-0100 seed rows + `IB-1799-T*` cluster in full.
3. Read `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md` in full.
4. Read `docs/research/domains/observability/1799_observability_canonical_summary.md` §1 canonical verdict + §5 D74 six-axis correlation-spine + §8 T1 leaf tail (this discharges the IDBT-0001 slice for 1799).
5. Read IOS §4.3 Stage 1 Scoping + §5.1 pre-code gates + §7.2 Stage 1 SIGN discipline + §15.14 pin lifecycle.
6. Read `docs/topics/celery-workers.md` + `docs/topics/infrastructure.md` + `docs/topics/agent-system.md` for existing observability + agent-execution context.
7. Draft Arc I-0100 scoping doc per §4.3 template.
8. Route to Rigby SIGN cycle 1 on fresh arc-scoped pin.
9. Fold SIGN edits + Chris ratification.

**Arc I-0100 open command (Chris short command):** `Open implementation arc I-0100: observability spine` per IOS §10 short commands + §15.3 phase detection routing.
