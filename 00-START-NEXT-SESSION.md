# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2751 CLOSED — I-0302 OBJECT-LEVEL AUTHORIZATION **ARC CLOSED** (ratified); 5 PLAYBOOK CANDIDATES QUEUED FOR v0.5

**Refreshed 2026-07-10 (SESSION 2751 CLOSED — Chris D-verdict "agree all" on BOTH Phase 4 close AND I-0302 arc close in a single continuous session.**

**Two arc-close ceremonies shipped:**

- **Phase 4 close** — PR #3129 (close doc + ratification + arch amendments) + PR #3130 (handoff + start-here + cascade, 3 embed / 73 chunks).
- **Arc close** — PR #3131 (arc-close doc `I-030299` + ratification record + final I-030203 §8 append) + cascade output (2 embed / 85 chunks: 50 arc-close + 35 ratification).

**S2751 total:** 3 substantive PRs (#3129, #3130, #3131) + 1 close-out cascade PR (this one). I-0302 Phase 4 + Phase 5 (arc close) both CLOSED. Sub-phase 3 was closed at S2750.

**5 playbook-candidate patterns promoted to v0.5 queue** (per arc-close ratification §5):
1. Report-only → batch-fix → enforce three-PR substrate pattern
2. Phase-close doc + ratification record + arch amendments = 1 PR
3. Watchpoint-attestation SIGN (W1..Wn) shape
4. Phase-close doc changes serialized on single close-doc PR (anti-pattern → codified)
5. 1 close-doc PR + 1 cascade PR at every close (with combined-vs-split shape)

**RUR-C1 parent still gates on I-0303** (async-boundary enforcement — not-yet-opened).**

Session anchors (read in order):

1. [`docs/handoffs/SESSION_2751_I0302_ARC_CLOSED.md`](docs/handoffs/SESSION_2751_I0302_ARC_CLOSED.md) — S2751 part 2 (arc close), delivery ledger, playbook candidates promoted, S2752 open protocol
2. [`docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md`](docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md) — S2751 part 1 (Phase 4 close), delivery ledger, session pivot analysis
3. [`docs/research/implementation/tenant_boundary_lockdown/I-030299_i0302_arc_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030299_i0302_arc_close.md) — arc-close doc (frozen; §7.1 playbook candidates)
4. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md) — arc-close ratification record (frozen; §5 v0.5 queue)
5. [`docs/research/implementation/tenant_boundary_lockdown/I-030205_phase4_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030205_phase4_close.md) — Phase 4 close doc (frozen)
6. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md) — Phase 4 ratification record (frozen)
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)

**Prior sessions (background context):** S2750 (Sub-phase 3 CLOSED); S2749 (Sub-phase 3 partial + Rigby stall fix); S2748 (Sub-phases 0/1/2 COMPLETE); S2747 (Phase 3 wiring COMPLETE); S2746 (Phase 2 predicate module RATIFIED); S2742 (Playbook v0.4.1 + I-0301 CLOSED + I-0302 scoping + Phase 1 + Phase 2).

---

## P0 — COST THRESHOLD OBSERVATION CHECK-IN (now actionable — 2026-07-11+)

**Do this FIRST before candidate selection.** Deferred through S2750 → S2751 per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md` — actionable on 2026-07-11 sessions onward. If S2752 opens 2026-07-11 or later, run the check-in.

**State at open (from S2743-S2750 arc):**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation only)
- Observation period started 2026-07-10 07:35 MDT

**Report to Chris at session open:**

1. **Current threshold config** — run `python manage.py cost_thresholds`; confirm `month: $500.00` still set and mode still `monitor`.
2. **Accumulation** — query `LLMCallLog` since 2026-07-10 07:35 MDT. Report total accumulated $, % of $500 ceiling, top 3 cost drivers.
3. **Anomalies** — any single-hour spike >$20, any new provider, any `[COST_MONITOR]` near-threshold log lines. If clean, say so explicitly.
4. **Advance recommendation** — is 24+ hours of clean observation enough to advance to `--set-mode freeze` (shadow mode)? Rigby SIGN before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.**

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83`.

---

## P0.5 — CI BILLING STATUS CHECK

**Do this SECOND, right after the cost check-in.** Still blocked at S2751 close (run 29139031286 same annotation). `--admin` merge flag remains active on all merges.

**Report to Chris at session open:**

1. **Fresh CI run** — `gh api /repos/clwest/donkey-betz-platform/actions/runs -q '.workflow_runs[0]'`.
2. **Flag state** — if CI is green: drop `--admin`, delete memory rule `feedback_gh_pr_merge_admin_until_billing_fixed.md`, remove MEMORY.md line.
3. **If still billing-blocked:** continue `--admin` merges + "Local verification limits" PR body sections.
4. **Cross-check arc-close recovery gate** — if CI becomes green during S2752, note whether first `tests/security/**`-touching PR run passes. If any Phase 4 test module regresses on that first green run, **Phase 4 close reopens** per `RATIFICATION_2026-07-10_i0302_phase4_close.md` §5, which **cascades to reopening the arc close** per arc-close ratification §6.

---

## SESSION PIN RETIRE (do FIRST after P0 + P0.5)

**Pin `pa-e71c011bfa3d4124`** was the S2749 arc pin. Carried through Sub-phase 3 → Phase 4 close → arc close.

**Natural retire point:** NOW. Arc is CLOSED.

Retire via: `session_tool.retire conversation_id=pa-e71c011bfa3d4124` (verified works per memory `feedback_session_tool_retire_works.md`).

Then mint fresh pin scoped to whatever S2752 opens (playbook v0.5 arc / I-0303 arc / net-new engineering / etc.).

---

## OPEN RUNTIME ITEMS (from S2751 close)

1. **PA celery worker bounce** — Rigby stall fix (#3119) still not activated. To activate: `pkill -f celery && OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES make celery`. Deferred to Chris.
2. **P0 observation check-in** — see above; NOW ACTIONABLE.
3. **P0.5 CI billing status** — see above; blocks lint-enforcement flips + `--admin` posture + Phase 4/arc close behavioral-verify recovery gate.
4. **Session pin retire** — see above; natural retire at arc close.
5. **Playbook v0.5 codification cycle** — 5 candidates queued; Chris D-verdict at arc close ratified them as CANDIDATES only. Awaits distinct v0.5 ratification cycle.

---

## PRIMARY WORK CANDIDATES — S2752

### CANDIDATE A — PLAYBOOK v0.5 CODIFICATION CYCLE

**5 candidates ready to codify** (per `RATIFICATION_2026-07-10_i0302_arc_close.md` §5):

1. **Report-only → batch-fix → enforce three-PR substrate pattern** — 2 triggers CONFIRMED. Proposed slot: PLAYBOOK-6.10.7.
2. **Phase-close doc + ratification record + arch amendments = 1 PR** — 2 triggers CONFIRMED. Proposed slot: PLAYBOOK-6.12.x.
3. **Watchpoint-attestation SIGN (W1..Wn) shape** — 2 triggers CONFIRMED. Proposed slot: PLAYBOOK-6.6.15.
4. **Phase-close doc changes serialized on single close-doc PR (anti-pattern → codified)** — 2 triggers CONFIRMED. Proposed slot: PLAYBOOK-6.12.y.
5. **1 close-doc PR + 1 cascade PR at every close (combined-vs-split shape)** — 2 triggers CONFIRMED with divergence. Proposed slot TBD in v0.5 draft.

**Ship pattern:**
1. Draft playbook v0.5 patch (Claude) — folds 5 candidates + Appendix D chain row.
2. Rigby SIGN (watchpoint-attestation shape — dogfooding candidate §5.3).
3. Chris D-verdict → v0.5 body commit + tag `playbook-v0.5` + workspace ratification record + L7 anchor refresh in CLAUDE.md.
4. Single PR (per candidate §5.2 shape — dogfooding).

Would be first MINOR playbook release since v0.4.0 (which introduced PLAYBOOK-6.10.6).

### CANDIDATE B — I-0303 (async-boundary enforcement) OPEN

RUR-C1 parent close blocks on I-0303 shipping shared cross-tenant regression pass. Open scoping doc following `I-0302_scoping.md` pattern:

- Async-boundary surface enumeration (Celery tasks, agents, Employee OS, WebSocket).
- Inherited scope from I-0302 §5.5.a Document WebSocket + §5.1.a Deliverable non-view sites.
- Scope decision on non-canonical models (`LegalDocument`, `LitigationDocument`, `ReviewDocument`) per arc-close doc §5.2.
- Phase decomposition (audit → design → wire → harness → arc close, mirroring I-0302 shape).

Fresh arc-open, not an execution session. Rigby SIGN + Chris D-verdict opens the arc; Phase 1 audit ledger follows.

### CANDIDATE C — NET-NEW ENGINEERING (per S2745 engineering-bias rule)

Carry-forward from S2751 open menu. Chris considered B3a (Cost Guardian dashboard tab) at S2751 open but pivoted to Phase 4 close then arc close.

1. **B3a — Cost Guardian dashboard tab** (Claude S2751 lean; Rigby de-risk asks: lock MVP to 3 tiles + 1 table, LLMCallLog-first, decide admin-only vs. redacted-for-users up front). Ties directly to P0 check-in workflow.
2. **B1a — Cost Guardian Employee OS employee** (backend-only variant of B3a).
3. **New spider on Chris-named data gap**.
4. **Employee OS employee #4** (backend + admin visibility).

### CANDIDATE D — META-METHODOLOGY (only if Chris explicitly asks)

- **Arc close template extraction** — arc-close doc §9.2 suggestion: extract `I-030199` + `I-030299` common structure into `arc_close_template.md`. Would help I-0303 close down the line.
- **Single-session multi-close ceremony pattern** — S2751 shipped both Phase 4 close AND arc close in one session with clean pin carry-forward. Signal at 1 trigger; watch for second in a future session (e.g., I-0303 double-close if the arc lands compact).

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `1176b67a` (PR #3131 merged; I-0302 arc CLOSED) — plus cascade PR (this session close-out) |
| Playbook version | v0.4.1 (unchanged) — **5 candidates queued for v0.5** |
| Playbook rule count | 196 |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-e71c011bfa3d4124` (active — retire at S2752 open per §6 above) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-e71c011bfa3d4124` (rotate after retire) |
| Live infra state | Cost threshold monitor mode $500/mo (observation period ~1 day at S2752 open); PA celery worker running pre-#3119 code; CI billing-blocked (`--admin` on merges) |
| RUR arc state | **I-0301 CLOSED · I-0302 CLOSED (all 5 phases; arc ratified S2751)** · I-0303 not yet opened · RUR-C1 parent still OPEN (gates on I-0303) |
| Playbook v0.5 queue | 5 candidates ratified as CANDIDATES at arc close; awaits separate codification cycle |

---

## What S2751 shipped (4 PRs total)

| PR | Content | HEAD | Session part |
|---|---|---|---|
| #3129 | I-0302 Phase 4 CLOSED — ratification + close doc + arch amendments | `f341581a` | Part 1 |
| #3130 | S2751 (part 1) handoff + start-here refresh + cascade (3 embed / 73 chunks) | `2a691ca5` | Part 1 |
| #3131 | I-0302 ARC CLOSED — arc-close doc + ratification + final I-030203 §8 append | `1176b67a` | Part 2 |
| this PR | S2751 (part 2) handoff + start-here refresh + cascade (2 embed / 85 chunks) | pending | Part 2 |

**Cumulative I-0302 arc (S2742 → S2751): 32 PRs** (26 substrate + 5 docs/handoff/cascade + 1 arc-close). Full ledger in `I-030299_i0302_arc_close.md` §3 + `SESSION_2751_I0302_ARC_CLOSED.md` §3.

---

## Recommended session-open protocol (S2752)

1. `context-kit orient`
2. Read `SESSION_2751_I0302_ARC_CLOSED.md` (§1 delivery + §5 playbook candidates + §6 open items) + `SESSION_2751_I0302_PHASE_4_CLOSED.md` (Phase 4 close context)
3. Verify runtime state: `git log --oneline -5`, `celery inspect ping`
4. **P0 check** (now actionable): run the observation check-in
5. **P0.5 CI billing status** — check + flag drop if resumed; arc-close recovery gate cross-check
6. **Retire pin `pa-e71c011bfa3d4124`** + mint fresh pin scoped to S2752 work
7. **Primary work decision** — surface A/B/C via Rigby; recommend **A (Playbook v0.5)** per completeness momentum: 5 candidates are hot, dogfooding pattern #2 (1-PR ratification) + pattern #3 (watchpoint SIGN) codifies them via the codified shape itself. Chris chooses.
8. **On acceptance of A:** draft v0.5 patch; Rigby watchpoint SIGN; Chris D-verdict; body commit + `playbook-v0.5` tag; L7 anchor refresh; workspace ratification record.
9. **On acceptance of B:** open I-0303 scoping doc; Rigby SIGN; Chris D-verdict; arc opens.
10. **On acceptance of C:** Chris names the slice; scope + Rigby SIGN before code.
11. **Docs cascade** — run 4-step at close; report chunk count.

---

## Reference documents

Ordered by frequency of use:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor v0.4.1)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules); **v0.5 candidates queued**
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030299_i0302_arc_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030299_i0302_arc_close.md) — arc-close doc (frozen S2751)
5. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md) — arc-close ratification record (frozen)
6. [`docs/research/implementation/tenant_boundary_lockdown/I-030205_phase4_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030205_phase4_close.md) — Phase 4 close doc (frozen)
7. [`docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md`](docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md) — Phase 4 ratification (frozen)
8. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — Phase 4 architecture (§8 chain-of-custody TERMINAL row = arc CLOSED)
9. [`docs/research/implementation/tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md) — I-0301 arc close (sibling precedent for I-030299)
10. [`docs/research/platform/platform_capability_graph.md`](docs/research/platform/platform_capability_graph.md) — capability chains + append-only refreshes
