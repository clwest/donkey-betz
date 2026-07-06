---
title: "Arc I-0100 — ADR-A Design Preparation: RIGBY_DELEGATION_ENABLED staged-enable posture (MISSION_RUNNER_ENABLED naming reconciliation)"
authority: design-preparation
status: active
arc_id: I-0100
arc_slug: observability_spine_mission_evidence_substrate
adr_target: ADR-0003
adr_slug_reserved: mission-runner-staged-enable-posture
session_authored: 2700
authored: 2026-07-06
authored_by: claude-code (Arc I-0100 Stage 2 — first design-prep under IOS v1.5 §4.3 Stage 2 mandatory rule)
source_finding_refs:
  - 1799 xx99 §1 point 3 (Cat E OpsRun / OpsRunEvent design-intent-latent evidence)
  - 1799 xx99 §2.5 (Cat E 9 load-bearing findings; ORM verification 36 OpsRun + 224 OpsRunEvent rows)
  - 1799 xx99 §120 canonical table row Cat E ("LATENT-VIABLE-BUT-FLAG-GATED — F1 DESIGN-INTENT-LATENT detail-JSON writer at rigby_delegation_signals.py:79-84 is RIGBY_DELEGATION_ENABLED=False-gated")
  - 1799 xx99 §8.2 T1 item 3 (MISSION_RUNNER + RIGBY_DELEGATION staged unlock)
  - Arc I-0100 scoping §5 P3 (planned rollout for IB-1799-T1-03; **contains the MISSION_RUNNER_ENABLED naming discrepancy**)
  - Arc I-0100 scoping §7.3 R2 (OpsRunEvent volume spike + retention shortage cascade risk)
  - Arc I-0100 scoping §7.3 R3 (delegation handler dormancy since S1250 PR8 wire-up)
  - Arc I-0100 scoping §8 F8-iii (Rigby SIGN Cycle 1 F8 fold: shadow → partial → full staged pattern; rollback triggers)
  - Arc I-0100 scoping §8 F4 (F4 ordering: ADR-B ratifies first — SATISFIED via ADR-0002; ADR-A ratifies second)
  - ADR-0002 §3.3 F6 fold (parent_execution_id correlation chain — delegation-triggered executions populate parent_execution_id)
  - ADR-0002 §3.3 F7 fold (ToolCallRecord.conversation_id UUID mismatch warning propagates to ADR-A)
sign_cycle_1: (pending — will route on arc pin pa-c5b235f7b15f45be per IOS §7.2 v1.4 implementation ADR SIGN cadence)
sign_cycle_1_pin: pa-c5b235f7b15f45be
companion_docs:
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md (canonical §4.3.a template reference)
  - docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md (ADR-B ratified; parent_execution_id correlation propagates)
  - docs/adr/ADR-0003-mission-runner-staged-enable-posture.md (companion ADR authored from this design-prep)
  - core/signals/rigby_delegation_signals.py (the flag-gated handler — 276 LOC)
  - core/services/rigby_mission_delegation.py (delegate_work_item — the second flag-gated surface)
  - core/employees/mission_runner.py (MissionRunner class — NOT flag-gated; already active for 3 employees)
  - core/settings.py:138-140 (RIGBY_DELEGATION_ENABLED flag definition; default False)
  - core/models_ops_runs.py (OpsRun + OpsRunEvent — already actively written)
verifier_loop: |
  First design-prep artifact authored under IOS v1.5 §4.3 Stage 2
  mandatory design-prep rule (v1.5 shipped 2026-07-06 via #2952).
  Follows §4.3.a canonical template pattern established by Arc
  I-0100 ADR-B design-prep. Investigation of runtime code state
  (rigby_delegation_signals.py, rigby_mission_delegation.py,
  mission_runner.py, settings.py) uncovered a naming discrepancy
  in the arc scoping doc §5 P3: "MISSION_RUNNER_ENABLED" flag does
  NOT exist as a runtime setting. The actual runtime gate is
  RIGBY_DELEGATION_ENABLED (settings.py:138-140). MissionRunner
  class itself is NOT flag-gated — it is invoked directly by
  3 employee Celery tasks (Documentation Manager, Platform
  Auditor, Chief of Staff) and produces OpsRun rows in
  production today (36 OpsRun + 224 OpsRunEvent rows verified
  per 1799 §2.5 ORM count 2026-07-03). This design-prep §1.4
  addresses the discrepancy explicitly and §7 recommendation
  scopes ADR-A to the actual runtime flag. Per Chris directive
  2026-07-06 ("treat IOS v1.5 as frozen unless a new systemic
  issue is discovered during execution... this issue is
  arc-specific, not structural"), the finding is recorded but
  does NOT interrupt implementation for IOS refinement. Design-
  prep pressure-tests 5 rollout-posture options against 5
  consequence-field matrix + recommends Option 2b (shadow-audit-
  synthetic → shadow-passive → canary-per-employee-instance →
  full) with recommendation-shape rationale in §7.
---

# ADR-A Design Preparation — RIGBY_DELEGATION_ENABLED staged-enable posture

**Purpose.** Canonical design-prep artifact for `ADR-0003-mission-runner-staged-enable-posture.md`. Per IOS v1.5 §4.3 Stage 2 mandatory rule + §4.3.a canonical template. ADR-0003 will cite this document as its `design-prep` source.

**Scope.** Two coupled decisions:

1. **What is the staged-enable posture for `RIGBY_DELEGATION_ENABLED`?** Multiple candidate rollout patterns evaluated in §4.
2. **What are the rollback triggers per stage?** Per Arc I-0100 scoping §7.3 R2 + R3 mitigations. Auto-disable thresholds + operator-intervention surfaces.

**Non-scope.**

- **D74 six-axis correlation-spine posture** — that's ADR-C (`ADR-0004` reserved slug).
- **PA write shape + PA↔LLMCallEvent correlation contract** — ADR-B / ADR-0002, ratified 2026-07-06.
- **Unified retention posture across 14 event models** — `IB-1799-T0-02` conditional per F2 fold; input to ADR-C.
- **Unlocking OpsRun / OpsRunEvent** — NOT the actual gate (see §1.4 finding). OpsRun/OpsRunEvent already flow (36 + 224 rows).

---

## §1. Context

### 1.1 Current runtime state

`core/signals/rigby_delegation_signals.py` implements the delegation lifecycle handler as a single `post_save` receiver on `AgentExecution` at line 131 (`on_delegation_lifecycle`). The handler:

- Filters cheaply on `parent_object_type='RigbyWorkItem'` (line 140–141) — non-delegated executions no-op.
- **Gated by `settings.RIGBY_DELEGATION_ENABLED` (default False), line 147.** When OFF, handler short-circuits.
- Writes 5 `OpsRunEvent` labels via `_write()` at lines 176–265: `agent_assigned`, `agent_completed`, `verification_started`, `verification_completed`, `mission_closed`.
- Deterministic verification (no LLM) — checks `AgentExecution.status` + `LLMCallEvent.objects.filter(execution_id=execution.id, status='SUCCESS').count()` at lines 87–128.
- Idempotency via `_has_event()` check at line 60.

`core/services/rigby_mission_delegation.py` implements `delegate_work_item()` at line 131 — the PA action that dispatches a `RigbyWorkItem` to an agent via `execute_agent_task.apply_async`. Also **gated by `RIGBY_DELEGATION_ENABLED`, line 157.** When OFF, returns structured "delegation disabled" response.

### 1.2 What OpsRun / OpsRunEvent look like today

Per 1799 §2.5 ORM verification 2026-07-03:

- **36 OpsRun rows** (19 ops + 17 mission) over 20 days.
- **224 OpsRunEvent rows** over 20 days.
- 17 mission rows all VERIFIED for MissionRunner nine invariants I1-I9 per S1705 F1 evidence (test_mission_runner.MissionRunnerImportContractTests).
- Zero divergence between MissionRunner spec + runtime observed.

**OpsRun / OpsRunEvent flow today via 3 Celery-invoked employees** (Documentation Manager, Platform Auditor, Chief of Staff) per CLAUDE.md Employee OS section. Each employee task instantiates `MissionRunner(config, steps).run()`; MissionRunner writes OpsRun + OpsRunEvent rows for its lifecycle.

### 1.3 What the RIGBY_DELEGATION_ENABLED flag actually gates

Two surfaces:

1. **`delegate_work_item()` PA action** — flip on / off entirely. When OFF, PA cannot dispatch RigbyWorkItem delegations. When ON, `delegate_work_item(work_item_id)` writes a `delegation_started` OpsRunEvent + dispatches via Celery.
2. **`rigby_delegation_signals.on_delegation_lifecycle` handler** — flip on / off the 5-label lifecycle writer. When OFF, terminal `AgentExecution.save()` on delegated executions writes nothing to OpsRunEvent. When ON, the 5 lifecycle events append.

The two surfaces are jointly gated because they only make sense together (dispatch without lifecycle observability is opaque; lifecycle without dispatch has nothing to observe).

### 1.4 Finding: `MISSION_RUNNER_ENABLED` naming discrepancy (arc-specific, not IOS-structural)

**Arc I-0100 scoping §5 P3 references "Existing feature flag flip: `MISSION_RUNNER_ENABLED = True` + `RIGBY_DELEGATION_ENABLED = True` (paired)."** This is a factual error inherited from upstream sources:

- **No `MISSION_RUNNER_ENABLED` setting exists in `core/settings.py` or any Python module.** Verified via `grep -rn 'MISSION_RUNNER_ENABLED' core/ agents/` — zero runtime matches (only test files that check the MissionRunner class import contract).
- **MissionRunner is NOT flag-gated.** `core/employees/mission_runner.py` header docstring confirms MissionRunner has no runtime flag; it is invoked directly by callers.
- **The only runtime flag is `RIGBY_DELEGATION_ENABLED`** at `core/settings.py:138-140`.

Interpretation: 1799 xx99 §120 canonical table (Cat E row) is CORRECT — it names `RIGBY_DELEGATION_ENABLED` as the F1 DESIGN-INTENT-LATENT gate. Arc I-0100 scoping §5 P3 introduced the `MISSION_RUNNER_ENABLED` naming as pair-shorthand — but the pair does not exist as two flags; it is one flag (`RIGBY_DELEGATION_ENABLED`) that gates two surfaces (dispatch + lifecycle writer per §1.3).

**Per Chris 2026-07-06 directive** ("Only interrupt implementation to propose IOS changes if ALL of the following are true... otherwise: Record observations as codification candidates only. Continue implementation without stopping"), this finding is:

- **Structural?** NO. Arc-specific naming discrepancy.
- **Not resolvable by IOS?** NO. IOS §14.2.a permits recording arc-scoped observations without IOS refinement.
- **Affects future arcs?** NO. Naming is Arc I-0100 scoping doc specific; future arcs will name their own gates.
- **Reduces cold-start correctness?** NO. Fresh Claude reading scoping + code + this design-prep §1.4 will resolve the discrepancy the same way.

Interruption criteria NOT met. Recorded as an arc-scoped observation; implementation continues per IOS v1.5 as written.

**ADR-A resolution:** scope to the actual runtime flag `RIGBY_DELEGATION_ENABLED`. Optionally recommend introducing a `MISSION_RUNNER_ENABLED` flag if future needs arise, but that would be a distinct decision (out of ADR-A scope; noted in §8 Alternatives).

### 1.5 What ADR-A must decide

Given §1.1–§1.4, ADR-A answers: **what is the staged-enable rollout posture for `RIGBY_DELEGATION_ENABLED`, and what are the rollback triggers per stage?**

The two surfaces gated by the flag (§1.3) can conceptually be enabled together OR independently, if a "shadow-audit-synthetic" mode is introduced. The five candidate options in §4 explore this space.

---

## §2. Decision questions (explicit)

**Q1 — Rollout posture.** What is the sequence of enable stages? Options: shadow-only-permanent, shadow → 10% partial → full (F8-iii baseline), direct full-enable, canary-per-employee-instance, hybrid.

**Q2 — Rollback triggers per stage.** What auto-disable + operator-intervention thresholds gate stage progression?

**Q3 — Shadow-mode implementation.** If the chosen posture includes a shadow phase, what does "shadow" concretely mean given that today the flag off means both surfaces are OFF (no dispatch, no lifecycle writer)? Options: (a) partial-flag `RIGBY_DELEGATION_SHADOW=True` that enables writer without dispatch, (b) synthetic-AgentExecution test rows to exercise the writer path in isolation, (c) reject shadow — skip to canary.

**Q4 — Correlation with ADR-0002 (ratified).** ADR-0002 §3.3 F6 fold specifies delegated executions populate `parent_execution_id = <pa_execution_id>`. Does ADR-A require code changes to make this parent-chain correlation land on delegation-triggered executions, or is it handled by ADR-B's runtime discharge (P4)? Answered in §6.

Q1–Q3 jointly resolved by option choice + sub-decisions in §4 + §5. Q4 resolved by cross-ref in §6.

---

## §3. Constraints (from ratified sources)

| Constraint | Source | Load-bearing implication |
|-----------|--------|--------------------------|
| **F4 fold ordering: ADR-A ratifies SECOND** (after ADR-B) | Arc I-0100 scoping §8 F4 (Chris ratified) | ADR-B / ADR-0002 accepted 2026-07-06; ADR-A now unblocked. |
| **F8-iii mitigation pattern** (shadow → partial → full; alerting on first error signature triggers immediate disable) | Arc I-0100 scoping §8 F8 + §5 P3 (Chris ratified) | ADR-A must adopt a staged pattern OR justify a departure; F8-iii is baseline recommended. |
| **F8-ii OpsRunEvent volume mitigation** (sampling/cap active during shadow + partial phases; threshold gate before full enable) | Arc I-0100 scoping §7.3 R2 (Chris ratified) | ADR-A must specify volume threshold + auto-disable gate. |
| **R3 delegation handler dormancy** — handler code shipped S1250 PR8 (2026-05-31); 0 events written since due to flag OFF | Arc I-0100 scoping §7.3 R3 | ADR-A must specify first-execution validation of handler code before any traffic phase. |
| **`RIGBY_DELEGATION_ENABLED` is the sole runtime gate** | `core/settings.py:138-140` verified 2026-07-06 | ADR-A scopes to this flag; do not require a mythical `MISSION_RUNNER_ENABLED` flag. See §1.4 finding. |
| **OpsRun / OpsRunEvent already flow** (36 + 224 rows verified) | 1799 §2.5 ORM verification | ADR-A rollout MUST NOT break existing OpsRun writes from Documentation Manager / Platform Auditor / Chief of Staff missions. |
| **Idempotency of handler writes** (via `_has_event` check) | `core/signals/rigby_delegation_signals.py:60-71` | ADR-A rollout can enable + disable the flag without duplicating OpsRunEvent rows on re-fire. |
| **Deterministic verification (no LLM)** | `core/signals/rigby_delegation_signals.py:87-128` | ADR-A verification-method interface per §6 is guaranteed no-LLM-dependency; ratifying ADR-A does not create LLM budget growth. |
| **F5 correlation contract** (LLMCallEvent.execution_id → AgentExecution.id per ADR-0002 §3.3) | ADR-0002 §3.3 ratified 2026-07-06 | Delegation handler at line 102 already queries `LLMCallEvent.objects.filter(execution_id=execution.id, status='SUCCESS')` — the correlation is Yes-required and already implemented, but relies on downstream code that populates `LLMCallEvent.execution_id` (ADR-B's runtime discharge, P4). Post-ADR-B ratification, P4 will populate for PA-driven executions; delegated executions (via Celery, non-PA) rely on router-agent path which already populates. |
| **F6 parent_execution_id chain** (per ADR-0002 §3.3 F6 fold) | ADR-0002 §3.3 ratified 2026-07-06 | Delegated executions must populate `parent_execution_id = <pa_execution_id>` when dispatched from a PA session. ADR-A must specify how this flows through `delegate_work_item` (see §6). |
| **F7 ToolCallRecord.conversation_id UUID warning** (per ADR-0002 §3.3 F7 fold) | ADR-0002 §3.3 ratified 2026-07-06 | ADR-A rollout MUST NOT use ToolCallRecord.conversation_id for PA-delegation correlation; use `trace_id` or `parent_execution_id`. |
| **v1 routing table single-agent** (`DELEGATION_ROUTING = {'monitor': 'TrendAnalysisAgent'}`) | `core/services/rigby_mission_delegation.py:47-49` | Only `monitor` decision is delegatable in v0/v1. ADR-A rollout blast-radius bounded by this routing table until it's expanded. |
| **`auto_followup=False` on delegation dispatch** | `core/services/rigby_mission_delegation.py` line 146 comment | Delegated executions do NOT trigger PA follow-up wake — matches MEMORY rule `feedback_auto_followup_false_suppresses_banner`. Chris + Rigby observability into delegation lifecycle comes from OpsRunEvent, not PA chat post. |

---

## §4. Options × 5-field consequence matrix

Consequence fields adapted for rollout-posture ADR (per §4.3.a v1.5 domain-adaptation clause): **rollout phases** / **rollback semantics per phase** / **observability during phase** / **runtime / storage volume implications** / **operator-intervention surface**.

Field-count = 5 per §4.3.a canonical template minimum.

### Option 1 — Shadow-only-permanent

`RIGBY_DELEGATION_ENABLED` stays FALSE indefinitely. Handler code remains dormant. Delegation observability provided via synthetic test-fixture executions (staff-only, no user traffic) OR via retrospective code review only.

| Field | Consequence |
|-------|-------------|
| **Rollout phases** | Zero phases. Flag stays OFF. R3 dormancy risk unmitigated — handler never proves it works on real traffic. |
| **Rollback semantics** | N/A — nothing to roll back from OFF. |
| **Observability during phase** | Zero. No OpsRunEvent from delegation path. `delegate_work_item()` returns "disabled" response for every call. |
| **Runtime / storage volume implications** | Zero net-new writes. Existing OpsRun/OpsRunEvent from 3 employee missions unaffected. |
| **Operator-intervention surface** | None required (nothing running). Chris + Rigby have no delegation surface to observe. |

### Option 2 — Shadow → 10% partial → full (F8-iii baseline, requires shadow-mode design)

Three phases: shadow-mode (handler writes events but no real dispatch), partial (10% cohort real dispatch), full (all traffic). Requires a sub-decision on how "shadow" is implemented (Q3 in §2).

**Two shadow sub-modes:**

- **2a — Shadow-passive:** enable RIGBY_DELEGATION_ENABLED=True but modify `delegate_work_item()` to return a fake dispatch response (writes `delegation_started` OpsRunEvent but does not `apply_async` the Celery task). Handler at `on_delegation_lifecycle` writes lifecycle events only if delegated AgentExecutions materialize — which they will not since dispatch is neutered. Effectively: dispatch-writer active + lifecycle-writer inactive.
- **2b — Shadow-audit-synthetic:** keep RIGBY_DELEGATION_ENABLED=False; author a management command / test fixture that synthesizes `AgentExecution` rows with `parent_object_type='RigbyWorkItem'` + non-terminal → terminal status transitions. Handler at `on_delegation_lifecycle` bypasses the flag check via test override (or the fixture temporarily flips the flag on then off for a single-execution window). Provides genuine handler-code validation without exposing real traffic.

| Field | Consequence (2a shadow-passive → partial 10% → full) |
|-------|------------------------------------------------------|
| **Rollout phases** | Phase 1 (shadow-passive, ~1 week): `delegation_started` OpsRunEvents accumulate; no dispatches. Phase 2 (partial 10%, ~1 week): real dispatch for 1-in-10 delegatable work items; observe end-to-end. Phase 3 (full): all delegatable work items dispatch. |
| **Rollback semantics** | Phase 1 → OFF: flip flag to False; no rows to clean up (dispatch was neutered). Phase 2 → Phase 1: modify dispatch to re-neuter; existing in-flight executions run to completion. Phase 3 → Phase 2: same. |
| **Observability during phase** | Phase 1: `delegation_started` count per day; validates PA-side write path. Phase 2: full 6-label lifecycle for 10% cohort; validates handler code. Phase 3: full for all. |
| **Runtime / storage volume implications** | Phase 1: ~1 `delegation_started` OpsRunEvent per delegable work item. Phase 2: 6 OpsRunEvents per delegable work item × 10% = 0.6 events per work item average. Phase 3: 6 events per work item × 100%. If daily delegable work-item cadence is N, Phase 3 net-new events = 6N/day. Requires baseline measurement at Stage 3 pre-flight. |
| **Operator-intervention surface** | Auto-disable on: (a) first `LABEL_AGENT_COMPLETED` with `event_type='step_fail'` in Phase 2 (per F8-iii latent-bug detection); (b) OpsRunEvent daily growth `> threshold`. Chris manual triggers: promote Phase 1 → 2, Phase 2 → 3. Rigby observability: `ops_tool.recent_ops_run_events` + `deliverable_provenance_tool.trace`. |

| Field | Consequence (2b shadow-audit-synthetic → partial 10% → full) |
|-------|--------------------------------------------------------------|
| **Rollout phases** | Phase 1 (shadow-audit-synthetic, ~2 sessions): author `manage.py delegation_lifecycle_smoke_test` command that spins up 3–5 synthetic AgentExecution rows + observes handler emissions. Phase 2 (partial 10%, ~1 week): flag ON; 10% real dispatch. Phase 3 (full). |
| **Rollback semantics** | Phase 1 → nothing to roll back (fixture only). Phase 2/3 → same as 2a. |
| **Observability during phase** | Phase 1: Rigby-runnable smoke test outputs pass/fail per label. Phase 2/3: same as 2a. |
| **Runtime / storage volume implications** | Phase 1: bounded by smoke-test fixture size (5 synthetic rows × 6 events = 30 OpsRunEvents; auto-cleanup). Phase 2/3: same as 2a. |
| **Operator-intervention surface** | Phase 1: Rigby-runnable via PA tool call OR direct Celery invocation. Phase 2/3: same as 2a. |

### Option 3 — Direct full-enable

Flip `RIGBY_DELEGATION_ENABLED=True`; observe production. No staged rollout.

| Field | Consequence |
|-------|-------------|
| **Rollout phases** | Single phase: FALSE → TRUE. |
| **Rollback semantics** | Flip TRUE → FALSE; new dispatches halt; in-flight executions run to completion; lifecycle events for in-flight complete on their post_save. |
| **Observability during phase** | Immediate 6-label OpsRunEvent volume for every delegable work item. If handler has a bug (R3 dormancy risk), it fires on every delegation → operator-visible impact. |
| **Runtime / storage volume implications** | Full 6N/day OpsRunEvents from day 1. No progressive volume ramp. |
| **Operator-intervention surface** | Auto-disable on same triggers as Option 2 but without a validation phase preceding. Higher risk of flag-flip-flop churn if latent bug surfaces. |

### Option 4 — Canary-per-employee-instance

Enable RIGBY_DELEGATION_ENABLED for one employee's Celery task pathway at a time (Documentation Manager → Platform Auditor → Chief of Staff). Requires per-employee gating logic on top of the global flag.

| Field | Consequence |
|-------|-------------|
| **Rollout phases** | Phase 1: enable for Documentation Manager only. Phase 2: add Platform Auditor. Phase 3: add Chief of Staff. Each phase ~3–5 days observation. |
| **Rollback semantics** | Per-phase: remove employee from allowlist. Non-destructive. |
| **Observability during phase** | Per-employee OpsRunEvent partition. Cross-employee handler-code differences (if any — none expected per §3 idempotency invariant) become visible. |
| **Runtime / storage volume implications** | Phase 1: 1/3 of full volume. Phase 2: 2/3. Phase 3: full. |
| **Operator-intervention surface** | Adds per-employee configuration surface (settings.py or new PA tool). More knobs = more operator load. |

### Option 5 — Hybrid: shadow-audit-synthetic (2b Phase 1) + direct full-enable (Option 3)

Skip the 10% partial phase after synthetic-smoke validation. Rationale: current delegable work-item cadence is LOW (v1 routing table has only `monitor` decision routed to `TrendAnalysisAgent`), so 10% partial approximates zero real traffic anyway. If synthetic smoke passes, direct-full is defensible.

| Field | Consequence |
|-------|-------------|
| **Rollout phases** | Phase 1: shadow-audit-synthetic (2b Phase 1). Phase 2: direct full-enable. |
| **Rollback semantics** | Phase 2 → OFF: same as Option 3 rollback. |
| **Observability during phase** | Phase 1: synthetic smoke. Phase 2: full production observability. |
| **Runtime / storage volume implications** | Phase 1 negligible. Phase 2 full 6N/day. |
| **Operator-intervention surface** | Chris manual promotion after Phase 1. Same auto-disable triggers as Options 2/3. |

---

## §5. Pressure test

Options scored against constraint set in §3 + judgment criteria (blast radius, reversibility, dormancy-mitigation, latent-bug-detection efficacy):

| Test | Option 1 (permanent OFF) | Option 2a (passive shadow) | Option 2b (synthetic shadow) | Option 3 (direct full) | Option 4 (per-employee canary) | Option 5 (hybrid 2b + direct) |
|------|--------------------------|---------------------------|------------------------------|------------------------|--------------------------------|-------------------------------|
| **Discharges R3 dormancy risk** | ❌ | ✅ partial (handler code not validated on real traffic yet) | ✅ (handler code validated on synthetic execution rows) | ⚠️ (validated on real traffic, but no safety net) | ✅ (validated per-employee sequentially) | ✅ (validated on synthetic + then real) |
| **Discharges R2 volume-spike risk** | ✅ (zero volume) | ✅ (bounded by neuter) | ✅ (bounded by fixture size) | ❌ (immediate full volume) | ✅ partial (1/3 volume ramp) | ⚠️ (jump from 0 to full) |
| **Requires new code (dispatch neuter, per-employee gating, smoke command)** | ✅ none | ⚠️ dispatch-neuter branch in `delegate_work_item` (new code) | ⚠️ new `manage.py delegation_lifecycle_smoke_test` command | ✅ none | ⚠️ per-employee gate + settings extension | ⚠️ smoke command only |
| **F8-iii baseline compliance** | ❌ (no staged phases) | ✅ | ✅ | ❌ (no shadow OR partial) | ⚠️ (canary-per-instance is a *different* staging axis than F8-iii shadow → partial → full) | ⚠️ (skips F8-iii partial) |
| **F8-ii volume-guardrail active during shadow + partial** | ✅ (no phases to fail) | ✅ | ✅ | ❌ (no phases) | ✅ | ⚠️ (Phase 2 is direct-full; guardrail is auto-disable only) |
| **Reversibility per ADR-0001 §3.5** | 5 (nothing to reverse) | 4 (flag flip + code revert) | 4 (flag flip + fixture cleanup) | 4 (flag flip only) | 3 (per-employee gating rollback more involved) | 4 |
| **Blast radius per §5.0** | LOCAL | SUBSYSTEM | LOCAL (synthetic only) | SUBSYSTEM–CROSS_DOMAIN (immediate real traffic) | SUBSYSTEM | SUBSYSTEM–CROSS_DOMAIN (Phase 2) |
| **Ops burden — flag-flip cadence** | 0 flips | 3 flips (shadow → partial → full) | 3 flips | 1 flip | 3–4 flips (per employee) | 2 flips |
| **Latent-bug detection efficacy** | ZERO (handler never runs) | LOW (writes only `delegation_started`; lifecycle writer still inactive) | HIGH (all 5 lifecycle labels exercised on synthetic rows) | HIGH-BUT-COSTLY (full traffic; bugs surface with real work-item impact) | MEDIUM (per-employee isolation limits cross-cutting bug detection) | HIGH (synthetic exercises all labels, then real traffic confirms) |
| **Time to full enable** | never | ~2 weeks | ~2 sessions + 1 week | 1 flip (same-day) | ~2 weeks | ~1 session + 1 flip |
| **Aligns with delegation routing table cadence (v0 only `monitor` decision)** | N/A | ❌ passive shadow relies on real delegable work-item cadence which is currently low | ✅ synthetic sidesteps low-cadence problem | ✅ direct-enable + low-cadence = safer than it looks | ⚠️ per-employee canary at low-cadence = little differential data | ✅ |

**Pressure-test verdict:** Option 2b (shadow-audit-synthetic) or Option 5 (hybrid 2b + direct) dominate. Option 5 is Option 2b's Phase 1 + Option 3's Phase 2 with the 10% partial phase skipped. The skip is defensible because:

1. **Delegation routing table v0 only routes `monitor`** (one decision) to `TrendAnalysisAgent`. The daily cadence of `monitor` work items is bounded (likely 0–5/day per historical work-item counts). A "10% partial" of ~5/day ≈ 0 dispatches — the partial phase provides no meaningful traffic differentiation.
2. **Synthetic smoke test in Phase 1 exercises the FULL lifecycle** (`agent_assigned` → `agent_completed` → `verification_started` → `verification_completed` → `mission_closed`) with deterministic outcomes. This is stronger latent-bug detection than 10% real traffic.
3. **Auto-disable triggers remain active in Phase 2** per §7.3 R2/R3 mitigations.
4. **Rollback cost is trivial** (flag flip to False).

**Non-blocking counter-arguments (kept for ADR §5 Alternatives):**

- **Option 2b full-3-phase value.** If delegation routing table expands beyond `monitor` before ADR-A runtime discharge (P3), the partial 10% phase becomes meaningful traffic differentiation. Recommendation: monitor `DELEGATION_ROUTING` at Stage 3 pre-flight; if it has grown past `{monitor: ...}`, revert to full 3-phase Option 2b.
- **Option 4 per-employee canary value.** If ADR-C (D74 spine) ratifies with per-employee retention posture differentiation (F2 fold conditional), per-employee rollout becomes structurally aligned. Recommendation: revisit at ADR-C ratification if applicable.

---

## §6. Verification implications

### 6.1 Interface (per Arc I-0100 scoping §9.3 F7 fold — verification-method-as-interface)

> **For a delegated PA turn or beat-scheduled delegation, retrieve the full lifecycle chain (agent_assigned → agent_completed → verification_completed → mission_closed) with correlation to the source AgentExecution + LLM calls.**

### 6.2 Concrete queries (Stage 3 pre-flight per F7)

Assuming Option 5 (recommended) ratifies:

1. **Delegation lifecycle chain for a work item:** `OpsRunEvent.objects.filter(run__ops_run_kind='mission', detail__work_item_id=<work_item_id>).order_by('created_at')` — should return 6 rows in strict order (delegation_started → agent_assigned → agent_completed → verification_started → verification_completed → mission_closed) for a successful delegation.
2. **Correlation to AgentExecution:** `AgentExecution.objects.filter(parent_object_type='RigbyWorkItem', parent_object_id=<work_item_id>)` — should return 1 row (the dispatched execution). `execution.id` matches OpsRunEvent detail `execution_id` per handler line 183.
3. **Correlation to LLM calls (per ADR-0002 §3.3):** `LLMCallEvent.objects.filter(execution_id=<agent_execution.id>, status='SUCCESS')` — matches handler's `_verify_execution` line 102 query.
4. **PA → delegation parent chain (per ADR-0002 §3.3 F6):** if the delegation originated from a PA session, `AgentExecution.objects.filter(id=<delegated_execution.id>).values('parent_execution_id').first()['parent_execution_id']` returns the PA-turn `AgentExecution.id`. Requires ADR-B P4 (write-side) to populate `parent_execution_id` when `delegate_work_item` is called from a PA context.

### 6.3 Rigby-exercisable surface

- **Phase 1 (synthetic smoke):** `manage.py delegation_lifecycle_smoke_test` — new command that spins synthetic AgentExecutions + verifies handler emissions.
- **Phase 2 (production):** Rigby PA tool calls — `ops_tool.recent_ops_run_events(label='delegation_started', limit=10)` returns the recent delegations; `ops_tool.mission_run_timeline(work_item_id=<id>)` returns the full 6-label chain.

### 6.4 Cross-ADR verification propagations

- **ADR-B §3.3 F6 parent_execution_id chain.** When `delegate_work_item` is called from a PA session (i.e., PA agentic loop initiated the delegation), the dispatched `AgentExecution` should have `parent_execution_id = <pa_execution_id>`. **This requires ADR-B's P4 runtime discharge to populate parent_execution_id in the PA-side dispatch context.** ADR-A does NOT block on P4 — ADR-A's Phase 1 (synthetic) and Phase 2 (production) both work regardless of parent_execution_id population. But full end-to-end provenance chain requires P4 to ship first.
- **ADR-B §3.3 F7 ToolCallRecord.conversation_id warning.** ADR-A's verification queries in §6.2 use `execution_id` and `trace_id` — NOT `ToolCallRecord.conversation_id`. Warning honored.

---

## §7. Recommendation

**Adopt Option 5 (hybrid): shadow-audit-synthetic Phase 1 → direct full-enable Phase 2. Skip F8-iii 10% partial phase per defensible-skip rationale in §5 pressure test.**

Rationale:

1. **Uses existing runtime flag `RIGBY_DELEGATION_ENABLED`.** No new flag introduced. Discharges R3 dormancy risk via Phase 1 synthetic exercise + Phase 2 real-traffic validation.
2. **Phase 1 provides genuine handler-code validation** without exposing real production traffic. Latent-bug-detection HIGH per §5 test.
3. **Phase 2 direct-full-enable is safe** given (a) delegation routing table v0 is single-agent (bounded cadence), (b) auto-disable triggers active from moment of flip, (c) rollback is 1-line flag flip.
4. **F8-iii partial-10% phase defensibly skipped** — at low cadence, 10% ≈ 0; skip is not a rule violation but a routing-table-cadence-informed adaptation.
5. **F8-ii volume-guardrail preserved** as Phase 2 auto-disable trigger.
6. **F5 correlation contract (ratified in ADR-0002) leveraged** — handler at line 102 already queries LLMCallEvent.execution_id; join works out-of-box.

### 7.1 Sub-decision: Phase 1 shadow-audit-synthetic implementation

**Adopt the `manage.py delegation_lifecycle_smoke_test` command approach.** This command:

- Creates a temporary `MissionRun` + `RigbyWorkItem` in a test-mode transaction.
- Creates 3–5 synthetic `AgentExecution` rows with `parent_object_type='RigbyWorkItem'` + `parent_object_id=<work_item.id>`.
- Transitions each execution through status states (pending → in_progress → completed / failed).
- Observes handler emissions to OpsRunEvent per execution.
- Verifies expected label ordering + idempotency (re-save should not duplicate rows).
- Cleans up all created rows before command exit (transactional rollback OR explicit cleanup).
- Output: pass/fail per label + summary chunk count.

**Rejected alternative — flag-flip-flop-single-window (Option 2b sub-variant):** temporarily flip `RIGBY_DELEGATION_ENABLED=True` for a bounded synthetic window, exercise, then flip back. Rejected because production users may hit `delegate_work_item()` during the window and receive real dispatches. Race condition risk.

### 7.2 Sub-decision: Auto-disable triggers per phase

| Trigger | Phase 1 (synthetic) | Phase 2 (production) |
|---------|---------------------|----------------------|
| First `LABEL_AGENT_COMPLETED` with `event_type='step_fail'` | N/A (synthetic passes deterministic) | Log ERROR + Rigby alert; do NOT auto-disable on first fail unless failure rate > threshold (protects against a single flaky work-item causing full-arc rollback) |
| OpsRunEvent daily growth `> threshold` | N/A | Threshold = baseline_daily_OpsRunEvent_count × 1.5 (measured at Stage 3 pre-flight). Auto-disable RIGBY_DELEGATION_ENABLED on breach; page Chris. |
| Handler exception rate `> N/hour` | N/A | Trigger auto-disable + Rigby alert. |
| Chris manual disable directive | Applies at any phase | Same |

### 7.3 Stage 3 pre-flight follow-ons (out of scope for ADR-A ratification, in scope for Stage 3)

- Measure baseline OpsRunEvent daily growth rate; set volume threshold.
- Author `manage.py delegation_lifecycle_smoke_test` command (~150 LOC estimate).
- Verify `DELEGATION_ROUTING` table state at pre-flight; if expanded beyond `{monitor: TrendAnalysisAgent}`, revert to full Option 2b 3-phase.
- Bounded consumer sweep for `OpsRunEvent.objects.filter(label='...')` sites — verify Phase 2 volume growth does not distort existing dashboards.
- Confirm ADR-B P4 status — Phase 2 requires ADR-B P4 (write-side) merged for full PA→delegation parent_execution_id chain (but does not BLOCK on it — see §6.4).

### 7.4 Cross-arc effects

- **`IB-1799-T1-03` (BACKLOG.md T1)** — discharged by P3 PR post-ADR-A ratification. Row flips `IN_ARC → SHIPPED` at P3 merge with `adr_ref: ADR-0003` and `pr_refs: #<P3>`.
- **Naming discrepancy correction:** BACKLOG.md IB-1799-T1-03 currently reads "Unlock OpsRun + OpsRunEvent via `MISSION_RUNNER_ENABLED` + paired `RIGBY_DELEGATION_ENABLED` staged unlock." Post-ADR-A ratification, either (a) row description gets corrected to reflect single-flag reality (small housekeeping edit) OR (b) ADR-A body notes the corrected scope inline (preserving BACKLOG description as historical intent). Chris/Rigby preference; ADR-A recommends (a) as cleaner.

---

## §8. Alternatives considered

Full alternatives enumeration for ADR-0003 §5 to inherit:

- **Option 1 permanent-OFF** — §4 Option 1. Rejected: unmitigated R3 dormancy risk; no observability into whether handler code works.
- **Option 2a shadow-passive** — §4 Option 2a. Rejected: passive shadow requires new dispatch-neuter branch (code cost) and only exercises the `delegation_started` writer, not the 5-label lifecycle. Weaker latent-bug detection than Option 2b/5.
- **Option 2b full-3-phase shadow-audit-synthetic → 10% partial → full** — §4 Option 2b. Available as fallback: if `DELEGATION_ROUTING` expands before P3, revert to this 3-phase pattern.
- **Option 3 direct-full-enable** — §4 Option 3. Rejected: skips R3 dormancy validation.
- **Option 4 per-employee canary** — §4 Option 4. Rejected: current per-employee handler code is uniform; canary provides no differential signal. Revisit if ADR-C introduces per-employee posture.
- **Option 5 hybrid 2b Phase 1 + direct full** (RECOMMENDED) — §4 Option 5.
- **New `MISSION_RUNNER_ENABLED` flag** — briefly considered per §1.4 finding. Rejected: (a) MissionRunner is not gated today and gating it would break existing OpsRun writes from 3 employee missions; (b) the naming discrepancy is scoping-doc-specific, not a real feature-flag requirement; (c) adding an unused flag violates §5.1 rule 7 (feature-flag consumer verification). Alternative retained as future decision if operator need surfaces.

---

## §9. Provenance

- **Design-prep author:** Claude Code, Arc I-0100 Stage 2 session (2026-07-06). First design-prep under IOS v1.5 §4.3 mandatory rule.
- **Consumed sources:**
  - Arc I-0100 scoping doc §5 P3 (planned rollout + naming discrepancy trigger) + §7.3 R2/R3 (risks) + §8 F4/F8 folds
  - ADR-0002 §3.3 (F5/F6/F7 correlation contract propagations)
  - 1799 xx99 §1 point 3 + §2.5 (Cat E ORM verification) + §120 canonical table
  - `core/signals/rigby_delegation_signals.py` (full read; 276 LOC)
  - `core/services/rigby_mission_delegation.py` (full read; ~200 LOC; delegate_work_item + routing)
  - `core/employees/mission_runner.py` (header only; ~60 LOC; MissionRunner class contract)
  - `core/settings.py:130-153` (RIGBY_DELEGATION_ENABLED flag definition + adjacent context)
  - Grep across `core/` + `agents/` for `MISSION_RUNNER_ENABLED` (zero runtime matches — trigger for §1.4 finding)
- **Rigby SIGN Cycle 1 target:** pending; will route on arc pin `pa-c5b235f7b15f45be` per IOS §7.2 v1.4. Design-prep NOT independently SIGN'd per IOS v1.5 §4.3.a rule — pressure-tested by SIGN cycle on ADR-0003.
- **Chris ratification target:** ADR-0003 body (not this design-prep). Design-prep does not need standalone Chris ratification.

---

## §10. What this design-prep taught us about how to do design-prep (meta-methodology)

- **Reading upstream CODE surfaced a scoping-doc factual error.** §1.4 finding — `MISSION_RUNNER_ENABLED` naming does not correspond to any runtime flag. Scoping doc §5 P3 introduced the naming as pair-shorthand; runtime reality is single-flag (`RIGBY_DELEGATION_ENABLED`). This is the SECOND instance in Arc I-0100 Stage 2 where reading code before authoring surfaced a decisive fact that scoping-only pre-scoping missed (first was ADR-B's Session 1174 PR-1 `conversation_id` field). Two consecutive design-preps confirming the same meta-observation: **§4.3.a §1 Context reading upstream code is not optional — it is the single most valuable step of a design-prep artifact.**
- **Domain-adapting the 5-consequence-field matrix worked well.** ADR-A did not need "schema shape / backward compatibility / migration surface / Rigby tool-surface / volume" (ADR-B's fields) — it needed "rollout phases / rollback semantics per phase / observability during phase / volume implications / operator-intervention surface." §4.3.a v1.5 permits domain adaptation as long as field-count ≥ 5. This was ratified 2026-07-06 and this design-prep is the first live test — it worked. Suggests §4.3.a template is correctly-abstract.
- **Sub-decisions inside options remain load-bearing.** §7.1 sub-decision on Phase 1 implementation (management-command approach vs flag-flip-flop-window) is ADR-A material — must ratify one. Similar pattern to ADR-B §3.2 sub-option 1(i) vs 1(ii). This is a general design-prep pattern worth codifying as a §4.3.a sub-clause in a future IOS refinement — but per Chris directive 2026-07-06 (do not proactively search for IOS refinements while executing Arc I-0100), this is recorded as a codification candidate ONLY. Not proposing IOS v1.6 unless a second trigger surfaces.
- **F8-iii-defensible-skip pattern.** Option 5 skips a scoping-doc-baseline phase (F8-iii 10% partial) with rationale (low delegation-routing cadence). Skipping a Chris-ratified scoping baseline requires strong justification + defensible rollback path. This pattern will recur; codification candidate for a future IOS §4.3.b "Ratified-baseline-skip discipline" section — RECORDED ONLY, not proposed.

---

**END DESIGN-PREP DOCUMENT — canonical design source for `ADR-0003-mission-runner-staged-enable-posture.md`.**
