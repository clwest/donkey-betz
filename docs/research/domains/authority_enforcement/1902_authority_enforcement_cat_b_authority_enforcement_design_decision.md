---
title: "Group 1900 P2 Cat B — Authority Enforcement Design Decision"
status: draft
authority: design-decision
domain_slug: authority_enforcement
research_group: 1900
session: 1902
child_slot: P2_cat_b
mission_type: design_decision
category: child_audit_design
delegates_from: 1900_authority_enforcement_domain_scoping.md
delegates_to: 1903_authority_enforcement_cat_c_cross_plane_composition_design.md
companion_anchors:
  - docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md
  - docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md
  - docs/research/authority_enforcement_design_space.md
  - docs/research/symbol_mapping_option_selection_design.md
  - docs/research/actor_identity_attribution_architecture.md
  - docs/research/governance_authority_evolution.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/PLATFORM_INVENTORY.md
verifier_loop: |
  Pre-Explore verifier-loop (playbook §14 MC-1 CODIFICATION-CONFIRMED):
  Confirmed direct-read of `core/llm_enforcer.py:237-238` fail-open
  precedent (F8), `core/employees/mission_runner.py:835-900`
  `_emit_authority_contract_event` shape-counter (F1 verified —
  level_counts accumulator at lines 863-874), and step signature
  `step.fn(mission)` at `mission_runner.py:917` (F6c STRUCTURAL DROP).

  Pre-Explore ALSO identified two parent-scoping drifts to flag:
  parent §5.2 cites "F8 constraint: Option E enables only 4 of 12
  modes" but S1272 §4.3 authoritatively lists 5 modes (observe-only +
  warn-mode + degrade-evidence + freeze-platform +
  retrospective-violation-report) and the constraint is S1272 F9
  ("Symbol Mapping choice constrains enforcement mode choice"), NOT
  F8 (which is the LLMEnforcer fail-open precedent). Both are
  recorded as inherited-in drifts in §14 rather than blocking scope
  changes; P2 uses the S1272 §4.3-verified 5-mode count.

  Six parallel Explore sub-agents fired per playbook §13 (Explores
  1-6 focused on: enforcement-gate precedent inventory /
  MissionRunner + Employee OS surface / governance planes +
  KillSwitch state / Symbol Mapping Option E v0 status /
  warn-mode telemetry actual data / rollout-rollback precedents +
  HAI capacity). All 6 returned.

  Post-Explore verifier-loop corrections landed as §14 Known Drift
  entries: KillSwitch dispatch-consumer count (S1272 GAP-7
  "write-only" REFUTED; 4 dispatch-consumer reads verified at
  governance:2192 + governance:2508 + intelligence:1717 + a 2-audit
  read pair = 6 total), HAI auto-approve condition count (S1269
  §2.4 cited 7; verified implementation has 8 gates at
  `human_attention_lifecycle.py:223-296` with 7 core business-logic
  gates excluding 2 existence checks), CLAUDE.md 3-employees
  drift vs runtime 4-employee-handles (rigby + platform_auditor +
  chief_of_staff + bug_triage_specialist all firing warn-mode
  events per Explore 5 ORM query), and the two parent-scoping
  drifts (Option E → 5 modes, cited constraint F9 not F8) captured
  above.

  D48 34th arm anticipated CLEAN turn 1 at S1902 Rigby SIGN cycle 1
  per single-batch-4-question criterion → 29-consecutive-fully-
  clean-arms sub-pattern EXTENDED anticipated milestone.
owner: claude (drafted S1902 v1)
last_verified: 2026-07-04
---

# Group 1900 P2 Cat B — Authority Enforcement Design Decision

> **What this is.** The design-decision doc for Group 1900 P2 Cat B.
> Consumes S1272 §14.3 mission spec (pick option A-F + modes +
> precedence + fail-open/closed + level→decision binding +
> per-employee opt-in + rollback + metrics/trust/false-positive
> thresholds) plus the P1 §7.3 per-boundary propagation-contract
> table as input scope. Produces (i) the Enforcement Binding Points
> map (P2's first-class deliverable per Rigby S1900 SIGN cycle 1
> Q4 fold), (ii) 6-option Decision-Grade Options Analysis (§7),
> and (iii) 8 Chris-gated D-verdict slots (D8N series) that pick
> the substantive enforcement design.
>
> **What this is NOT.** An audit of a domain; it is a design decision
> under an arc that already audited the domain (S1272 + S1901).
> Not an implementation PR. Not a runtime change. Not a
> re-litigation of S1274 Symbol Mapping Option E v0 (that
> selection stands; any Option E → A/B/C/D migration P2
> recommends is a Chris-gated recommendation governed by S1274
> §11 graduation triggers, per parent §5.2 clarifier).
>
> **Section shape.** Playbook §11.2 20-section child audit template
> modified per parent §5.2 for design-decision framing:
> §7 Runtime Flows → **§7 Decision-Grade Options Analysis**;
> §12 Research Coverage → **§12 Decision Rationale +
> Alternatives Rejected**;
> §17 Duplicate or Overlapping Systems → **§17 Enforcement
> Binding Points map**.
> All other sections keep their §11.2 template meaning.

---

## 1. Executive Summary

**Question P2 answers.** Given (a) S1274 selected Symbol Mapping
Option E v0 (evidence-only, defined but not migrated),
(b) S1901 shipped the three-role propagation contract with 20
per-boundary rows and a drop-boundary register (F6a/F6b/F6c +
F6c-adjacent Boundary 10 async signals), and (c) S1272 enumerated
6 candidate enforcement design options (A MissionRunner-centered /
B ToolDispatcher-centered / C Audit-first / D HAI-approval-mediated
/ E Multi-layer / F Governance-plane composition) with 12 modes,
15 prerequisites, and 20 boundaries — **which enforcement design
does Chris pick, and how do the sub-picks (modes, precedence,
fail-open/closed, level binding, opt-in, rollback, thresholds)
compose to produce a Chris-ratifiable Group 1900 P2 enforcement
architecture?**

**Chris ratification — 2026-07-04.** All 8 D-verdicts (D86-D93)
ratified via **"agree all"** shortcut post-Rigby SIGN cycle 1.
The design shape below is now Chris-locked.

**Recommendation shape — CHRIS-RATIFIED.** P2 ships a **hybrid
Option C-primary + Option A-adjacent design**, on the following
reasoning:

- Option C (Audit-first / evidence-only) is the **only option
  mechanically compatible with the S1274 Option E v0 selection**
  today. Every pre-dispatch option (A/B/D/E-multi-layer/F) requires
  Symbol Mapping A/B/C/D graduation first per S1272 §4.3 F9. Until
  those triggers land, pre-dispatch enforcement is a recommendation
  for future graduation, not a shippable design.
- Option A-adjacent scaffolding — specifically, adding a
  `MissionRunnerConfig.enforce_authority_mode` field defaulting to
  `warn` — is proposed as **structural preparation** so that when
  Option E graduates to A/B/C/D per S1274 §10.3.1 triggers, the
  toggle exists to promote observe → warn → enforce per employee
  without a schema migration.
- No other option is chosen at P2. Options B/D/E-multi-layer/F
  remain in the design space and are recommended for reconsideration
  at S1274 graduation trigger firing (post-arc Chris-gated).

**8 Chris D-verdict slots (D86–D93 draft numbering; renumber at
close if collision).** Each slot presented in §12 with (i) my
recommended lean, (ii) two alternatives with explicit rejection
rationale, (iii) reversibility rating. Chris ratifies each slot
individually at close.

**Deliverables at S1902 close.**

1. This doc (§1-§20 populated).
2. §17 Enforcement Binding Points map — 20-row table per S1272 §3.1
   × current-state precedent × Layer-ii closeable per S1901 §7.3.
3. §7 Decision-Grade Options Analysis — 6 options with reuse
   footprint, requirements, prevented actions, missed actions,
   implementation risk, operational risk, observability, rollback
   strategy, EOS compatibility, failure modes.
4. §12 Decision Rationale slots populated per Chris D-verdicts at
   session close.
5. §19 T-tier queue extended: T0/Gate items P1 identified
   (R.AUTHORITY.ENFORCEMENT-BINDING-POINTS-MAP consumed) + new
   T1/T2/T3 additions from P2 findings.

**What P2 does NOT ship.**

- Any runtime PR (playbook §14.5 no-implementation rule).
- S1274 Option E → (A/B/C/D) migration itself (recommendation only;
  Chris-gated via S1274 §10.3.1 graduation triggers).
- Cross-plane precedence policy final answer (P3 finalizes; P2
  provides partial input).
- Individual boundary wiring implementation (post-arc queue
  R.AUTHORITY.ACTOR-KWARGS-CELERY / R.AUTHORITY.ACTOR-STEP-CONTEXT
  / R.AUTHORITY.EVENT-SCHEMA-EXTENSION / R.AUTHORITY.OPSRUN-ACTOR-
  COLUMNS inherited from P1 §19; extended in §19 here).

**Verifier-loop discipline (playbook §14 REQUIRED; MC-1 CODIFICATION-
CONFIRMED).** Pre-Explore + post-Explore verifier-loop applied.
Six parallel Explore sub-agents fired per playbook §13 with
design-decision framing. Two parent-scoping drifts caught pre-Explore
and inherited into §14. Post-Explore corrections landed as §14
entries (KillSwitch dispatch-consumer count, HAI auto-approve gate
count, CLAUDE.md 3-employees drift). See frontmatter `verifier_loop`
for the full trace.

**Rigby SIGN cadence.** Cycle 1 pre-commit — pressure-test the
Options Analysis for neutrality (per S1272 §9 neutrality guardrail),
verify the Enforcement Binding Points map covers all 20 boundaries
with correct P1 row citations, and stress-test the D86-D93
recommended leans. Cycle 2 anticipated post-Chris-gate to
pressure-test the D-verdict rationale. D48 34th arm anticipated
CLEAN turn 1 per single-batch-4-question criterion →
29-consecutive-fully-clean-arms sub-pattern EXTENDED anticipated
milestone.

---

## 2. Domain Purpose

**Authority enforcement** is the runtime discipline that answers:
*"When an executor performs an action, was that action within the
authority level the sponsor granted, and if not, what does the
platform do about it?"* Today, the platform has:

- **Authority level vocabulary** — 4-value enum `AuthorityLevel`
  (OBSERVE / RECOMMEND / EXECUTE / PROHIBITED) declared on the
  `JobContract` dataclass at `core/employees/jobs.py:41-51`.
- **Authority signal emission** — S1264 warn-mode fires
  `authority_contract_observed` OpsRunEvent at `mission_runner.py:882`
  once per mission; carries authority level counts as a shape
  histogram, not per-action decisions.
- **Zero enforcement consumers** — S1272 F1 verified at pre-Explore:
  the ONLY runtime consumer of `AuthorityLevel` values is the
  level_counts accumulator at `mission_runner.py:863-874`, plus a
  JSON-serialization coerce helper at `td_handlers_employee.py:77`
  (not an enforcement branch). No code path today reads
  `AuthorityLevel` to gate a decision.

**Where P2 sits in the arc.** The three-role propagation contract
(P1 S1901) establishes *who* performed the action.
Group 1900 P2 (this doc) picks *how* the platform reacts when the
authority level of that action is violated. Group 1900 P3 (S1903)
composes P2's answer with the other three governance planes
(autonomy, budget, HAI) into a cross-plane precedence policy.
Group 1900 P4 (S1904) audits the separation boundary between
authority enforcement and adjacent domains that assume authority
checks ran.

**Why now.** S1264 shipped warn-mode 5 days ago (first fire
2026-06-30 17:06:27 UTC per Explore 5). The 13 events observed to
date establish an empirical baseline for prereq #11 (metrics window)
and validate the shape-only observation contract, but do not yet
provide the ≥14 days or ≥30 days clean telemetry that S1274 §10.3.1
graduation triggers or S1264 handoff §6 prereqs require. P2's job is
NOT to graduate to enforce today; it is to lock in the design that
governs graduation when triggers fire.

**Design boundary conditions.**

- **S1274 Option E v0 stands.** No P2 verdict overrides that
  selection; any Option E → (A/B/C/D) migration P2 recommends is a
  Chris-gated recommendation subject to S1274 §10.3.1 graduation
  triggers per parent §5.2 clarifier.
- **F9 constraint verified.** Per S1272 §4.3 (authoritative table):
  Option E constrains the mode subset to 5 of 12 modes — observe-only
  + warn-mode + degrade-mission-evidence + freeze-platform +
  retrospective-violation-report. Pre-dispatch modes (soft-fail /
  hard-block / require-human-approval / defer-mission /
  pause-employee / freeze-tool / freeze-queue) require Symbol
  Mapping A/B/C/D graduation.
- **F1 constraint verified.** No current runtime consumer branches
  on `AuthorityLevel` value; the level → decision binding must be
  designed from scratch under any option chosen.
- **F6 drop boundaries verified via P1 §7.3.** Boundaries 7 / 9 / 10
  (Step.fn closure / Celery process boundary / async signal receivers)
  have permanent identity-signal gaps that constrain both P2 layer
  choice and P3 cross-plane composition.

---

## 3. Canonical Entry Points

Design-decision docs consume canonical entry points from the audit
docs that precede them; this section lists the entry points where
P2's design will land IF Chris ratifies each recommended lean. The
list is provisional pre-Chris-gate; ratified entries become
authoritative post-D8N series.

**Warn-mode observation event (S1264, current-state, unchanged
under any option).**

- `_emit_authority_contract_event` at
  `core/employees/mission_runner.py:835-900` — shape validation +
  `AUTHORITY_CONTRACT_OBSERVED_LABEL` emission. Explore 2 verified
  schema_version constant at `mission_runner.py:265`
  (`AUTHORITY_CONTRACT_SCHEMA_VERSION = 1`; bump on detail-shape
  changes per Rigby S1264 SIGN edit #1). Level_counts accumulator
  at lines 863-874 (F1 shape-counter — the ONLY runtime consumer of
  `AuthorityLevel` outside JSON-serialization coerce).

**Level → decision binding entry point (P2 design ships).**

- Under recommended Option C-primary lean: no synchronous entry
  point (evidence-only). Retrospective read site: a new periodic
  scan (P2 recommends `authority_violation_retrospective_scan`
  Celery beat task; details in §12 D89 rationale) reads
  `authority_contract_observed` events + eventual `action_class` +
  actor context columns and emits `AUTHORITY_CONTRACT_VIOLATED`
  event per S1272 prereq #4.
- Under Option A-adjacent scaffolding: `MissionRunnerConfig.enforce_authority_mode`
  field added to the dataclass at `core/employees/mission_runner.py:528-589`.
  Default `warn` (matches current-state); values `observe` /
  `warn` / `enforce` following S1264 rollout pattern. Under
  recommended lean this field is added at P2 close but the
  `enforce` branch is dead code until Symbol Mapping A/B/C/D
  graduation ships.

**Per-employee opt-in surface (P2 design ships).**

- Under recommended lean D91 (see §12): `AIEmployee` frozen
  dataclass at `core/employees/jobs.py:73-91` grows one new field
  `enforce_authority_mode: str = "warn"` matching the runtime
  config field. Because AIEmployee is a frozen dataclass and used
  as a registry primitive (per `EMPLOYEE_OS_PRIMITIVES.md`), the
  field defaults to `"warn"` (backwards-compatible) and lands as a
  code-review-gated change under the S1264 all-employees-inherit
  pattern.

**Precedence entry point (P2 partial + P3 completes).**

- Cross-plane precedence is not a single file:line entry point; it
  is a policy that fires at multiple boundaries. P2 documents the
  partial precedence table in §12 D88 for the four current-state
  planes P2 observed (authority / KillSwitch / freeze / HAI
  auto-approve). P3 (S1903) completes the 8-question composition
  policy at `docs/research/domains/authority_enforcement/1903_...md`.

**Metrics + trust + false-positive threshold entry point.**

- Under recommended lean D93: `SystemConfiguration` keys with
  category `authority_enforce`:
  - `authority_enforce:metrics_window_days`
  - `authority_enforce:trust_threshold_ratio`
  - `authority_enforce:false_positive_ceiling`
  - `authority_enforce:auto_halt_threshold`

  Chris-gated read at eventual `authority_enforce_gate_service`
  (post-arc T1). Only relevant when graduation triggers fire; not
  read at P2 ship.

**Rollback entry point.**

- Under recommended lean D92: warn ← enforce rollback is a
  configuration flip on `MissionRunnerConfig.enforce_authority_mode`
  + AIEmployee field; the toggle path is symmetric with rollout.
  No separate rollback code path required beyond the mode field.

---

## 4. Major Models

Design-decision scope; P1 §4 exhaustively inventoried the authority
domain's models via 20-row role-role-role table (executor_actor /
sponsor_actor / principal_user × ambiguity × migration-needed).
This section enumerates ONLY the models P2's design either (i)
touches at ship time or (ii) prepares for touch at Symbol Mapping
graduation. Refer back to P1 §4 for the domain-wide inventory.

### 4.1 Models P2 touches at ship (recommended lean)

| Model | File:line | P2 delta | Purpose |
|---|---|---|---|
| `AIEmployee` (frozen dataclass) | `core/employees/jobs.py:73-91` | Add `enforce_authority_mode: str = "warn"` field (5th → 6th field) | Per-employee opt-in surface (D91). Backwards-compatible default. |
| `MissionRunnerConfig` (frozen dataclass) | `core/employees/mission_runner.py:528-589` | Add `enforce_authority_mode: str = "warn"` field (16th → 17th field) | Runtime read site for the level → decision binding (D90). Matches AIEmployee field name for compositional clarity. |
| `SystemConfiguration` | `core/models/system/models.py:9-80` | New category `authority_enforce:*` with 4 keys (metrics_window_days / trust_threshold_ratio / false_positive_ceiling / auto_halt_threshold) | Thresholds for D93. Read-only at P2 ship; only relevant post-graduation. |

### 4.2 Models P2 prepares for touch at Symbol Mapping graduation

Per S1274 Option E v0 spec + parent §5.2 clarifier, these models
are candidates for `action_class` column addition. Explore 4
verified: **0 of 5 audit models have the field today; 0 migrations
touch it**. P2 does not add the field itself; P2 records the
recommendation for the T1 R.AUTHORITY.OPTION-E-MIGRATION deliverable
that fires when S1274 §10.3.1 graduation triggers land.

| Model | File:line | Field to add on graduation | Migration state |
|---|---|---|---|
| `ToolCallRecord` | `core/models_tool_calls.py:57-60` | `action_class: str \| None` (nullable, indexed) | Not migrated (Explore 4) |
| `OpsRunEvent` | `core/models_ops_runs.py:91-118` | `action_class: str \| None` (nullable) | Not migrated |
| `LLMCallEvent` | `core/models_llm_telemetry.py:62-65` | `action_class: str \| None` (nullable) | Not migrated |
| `CeleryTaskEvent` | `core/models_celery_telemetry.py:41-47` | `action_class: str \| None` (nullable) | Not migrated |
| `AgentExecution` | `core/models_unified_system.py:894-927` | `action_class: str \| None` (nullable); note: model deprecation candidate per S1901 P1 §14 known drift | Not migrated |

### 4.3 Models P2 does NOT touch

- **`JobContract`** — dataclass shape stable from S1264. Any change
  to the `authority: dict[str, str]` value semantics (e.g., level
  → policy binding rules) belongs in the `enforce_authority_mode`
  read site, not the contract shape itself. Per S1272 §10 anti-pattern
  #2, prose in `prohibited_actions` remains not-a-symbol; migration
  to symbols is Symbol Mapping graduation scope.
- **`OpsRun`** — actor-role columns (F6b closeable per S1901 §7.4) are
  P1 T1 deliverable R.AUTHORITY.OPSRUN-ACTOR-COLUMNS, not P2 scope.
- **`Agent`, `AgentExecution.user`, `Deliverable.user`, etc.** —
  P1 §4 catalogued; no P2 delta.
- **`KillSwitch`** — despite S1272 GAP-7 claim of write-only, Explore 3
  verified 6 read sites including 4 dispatch-consumer gates
  (§14 KNOWN DRIFT entry). P2 recommends KillSwitch precedence
  policy in D88 but does not modify the model.

---

## 5. Major Services

Refer to P1 §5 for the full domain service inventory (MissionRunner,
LLMEnforcer, ToolDispatcher, AgentRouter, `_router_heartbeat_loop`,
warn-mode preflight service). This section lists the services P2's
design touches or extends.

### 5.1 Services P2 recommends creating (post-arc T1)

- **`authority_enforce_gate_service`** (new; recommended T1).
  Runtime consumer of `MissionRunnerConfig.enforce_authority_mode`
  + `AIEmployee.enforce_authority_mode` + `SystemConfiguration
  authority_enforce:*` keys. Under Option C-primary lean, this
  service is read-only at ship: it computes the current
  `effective_enforce_mode` per employee (max-strictness composition
  of the two toggles) and returns it for logging + evidence-only
  scoring. Under future Option A/B/D/E-multi-layer graduation, this
  service becomes the pre-dispatch gate.
- **`authority_violation_retrospective_scan`** (new; recommended T1
  Celery beat task). Reads `authority_contract_observed` events + P1
  §7.6 principal_user_id + P1 T1 R.AUTHORITY.OPSRUN-ACTOR-COLUMNS
  actor columns once shipped. Cross-references `JobContract.authority`
  dict + `action_class` field once Option E graduates. Emits
  `AUTHORITY_CONTRACT_VIOLATED` OpsRunEvent per S1272 prereq #4
  when a violation shape is detected. Under Option C-primary lean,
  this is the substantive detection surface; retrospective only.

### 5.2 Services P2 extends

- **`_emit_authority_contract_event`** at
  `mission_runner.py:835-900`. No structural change at P2 ship.
  Under D89 D-verdict IF chosen, the emitted `mode` field currently
  hardcoded to `"warn"` (line 894) reads from
  `self.config.enforce_authority_mode` post-D90 landing (still
  `"warn"` at default).
- **`LLMEnforcer.check_budget`** at `llm_enforcer.py:200-262`. No
  P2 delta. Kept as the F8 fail-open precedent (Explore 1 verified
  2 fail-open sites at lines 237-238 + 263-264). Under D90 fail-open
  D-verdict lean, cite F8 as the authoritative precedent P2 follows.

### 5.3 Services P2 does NOT touch

- **`ToolDispatcher.execute`** — Option B (ToolDispatcher-centered)
  is not chosen at P2. Option B rejected explicitly (§12 D86); the
  dispatcher's `AssistantProfile.get_allowed_tools()` gate at
  `tool_dispatcher.py:687-720` (Explore 1 verified 33-line stable
  gate; recent Session 1171 #4 typed-exception rework unchanged) is
  preserved as-is. Option B remains available for reconsideration
  at S1274 graduation.
- **`AgentRouter.route`** — routing decisions do not gate authority;
  authority is a per-action property, not a per-agent property.
- **`ops_autopilot/governance`** — the 3 KillSwitch dispatch-consumer
  read sites (Explore 3) remain the current-state precedent P3
  Cross-Plane Composition Design will finalize; P2 does not modify.

---

## 6. Major APIs and Interfaces

Design-decision scope. P1 §6 inventoried the boundary-facing
surfaces. This section lists API/interface deltas P2 introduces at
ship + prepares for graduation.

### 6.1 API/interface deltas at P2 ship

None. P2 ships a design doc + dataclass field additions. No new
REST endpoints, WebSocket consumers, PA tools, Celery tasks, or
management commands.

### 6.2 PA tool surface impact

- **`employee_tool describe`** — `td_handlers_employee.py:77`
  currently coerces `AuthorityLevel` enum values to strings via
  `_dataclass_to_jsonable` (Explore 2). Under D90 landing, the
  helper serializes the new `enforce_authority_mode` string field
  as-is (no change required).
- **`platform_config_tool overview`** — under D93 lean, the four
  new `authority_enforce:*` SystemConfiguration keys should surface
  in overview output. Post-arc T3 doc-only.

### 6.3 Interface preserved for post-graduation

- **`authority_enforce_gate_service.check(mission, action_class)`**
  signature reserved. Under Option E → A/B graduation, this becomes
  the pre-dispatch gate at MissionRunner (Option A) or ToolDispatcher
  (Option B) with the same signature. Design registered here so
  future work does not invent divergent shapes.

---

## 7. Decision-Grade Options Analysis

**Section shape (per parent §5.2).** Playbook §11.2 §7 Runtime Flows
becomes Decision-Grade Options Analysis for design-decision docs.
Six options from S1272 §9 re-presented with (i) S1272 canonical
description preserved verbatim in shape, (ii) current-state evidence
from Explores 1-6 verified at pre-Explore, (iii) P2's mechanical
compatibility verdict against S1274 Option E v0, (iv) recommended
lean statement (Chris-gated). **All 6 options are mechanically
defensible design choices**; my leans are advisory per S1272 §9
neutrality guardrail.

> **Neutrality guardrail (inherited from S1272 §9 Rigby SIGN).**
> Comparatives in this section (e.g., "cleanest", "highest coverage",
> "most reversible") describe axes of the design space, not
> endorsements. My recommended leans in §7.7 are rationale-carrying
> advisory statements Chris ratifies via §12 D-verdicts, not
> unreviewed defaults.

### 7.1 Option A — MissionRunner-centered enforcement

**Shape (S1272 §9.1).** Authority checked at boundaries 4/5/6
(MissionRunner.run entry / preflight / before Step.fn). Enforcement
rides the MissionRunner lifecycle; steps that would invoke a
PROHIBITED action are blocked before `step.fn(mission)` at line 917
is called.

**Current-state reuse footprint (Explore 2 verified).**

- `_emit_authority_contract_event` at `mission_runner.py:835-900`
  provides the preflight event pattern; violation event would parallel.
- `MissionRunnerConfig` (16 fields; Explore 2 file:line 528-589)
  is opt-in per employee via `job_contract` field.
- `AUTHORITY_CONTRACT_SCHEMA_VERSION = 1` at `mission_runner.py:265`
  provides bump-tracking discipline for detail-shape changes.
- Level_counts accumulator at `mission_runner.py:863-874` is the
  ONLY current runtime consumer of `AuthorityLevel` (F1 verified);
  Option A extends this into a level → decision consumer.

**Current-state gap (Explore 2 verified).**

- **NO `enforce_authority_mode` field on `MissionRunnerConfig` today.**
  Option A ship requires adding one.
- **NO synchronous action_class signal at Boundary 6.** Per S1272
  F9 and Explore 4, `action_class` field does not exist on any
  audit model. Option A cannot pre-block without either Symbol
  Mapping A/C graduation OR a `Step.action_classes_invoked`
  declaration extension.
- **F6c STRUCTURAL DROP at Boundary 7 (verified P1 §7.4).**
  `step.fn(mission)` signature closes actor context; Option A
  cannot inspect step-body decisions.

**Prevented actions.** Contract violations at mission scope (4
JobContracts × per-mission actions). Step-declared actions that
violate authority pre-invocation IF `Step.action_classes_invoked`
extension ships.

**Missed actions.** Actions via direct tool calls outside
MissionRunner (Boundaries 2/3 — ToolDispatcher.execute path).
Actions via Celery task independent of missions (Boundaries 8/9).
Actions via ORM directly (Boundary 10 signals; F6c-adjacent per
S1901 Rigby fold). HTTP endpoint actions (Boundary 1).

**Implementation risk.** Medium — MissionRunner is central and
well-tested (Explore 2 verified no fail-open sites in
`mission_runner.py`); extending in-place has S1264 warn-mode
precedent. Missing coverage of ToolDispatcher path (Boundary 2 —
33 permission_classes sites per Explore 1) means Option A is
mission-scoped partial coverage.

**Operational risk.** Low-to-medium. Warn-mode already at Boundary 5
(Explore 5: 13 events over 5 days, no malformed contract errors,
0 violation events). Adding enforcement gate keeps the surface
familiar. False-positive risk scoped to per-step declaration accuracy.

**Observability.** Strong. Events fire at `OpsRunEvent` scope; audit
chain intact via `_emit_event` pattern verified at
`mission_runner.py:880`.

**Rollback strategy.** Feature-flag on
`MissionRunnerConfig.enforce_authority_mode=warn` default; opt-in
per employee (matches S1264 warn-mode rollout pattern where all
employees inherited warn-mode same day — Explore 6 verified).

**Compatibility with Employee OS (`EMPLOYEE_OS_PRIMITIVES.md`).**
High. MissionRunner is the canonical Employee OS execution primitive
per PRIMITIVES §4.1; extending it uses primitive-reuse discipline.

**Compatibility with S1274 Option E v0 (P2 verifier-loop).**
**Constrained.** Per S1272 §4.3 F9, Option E enables 5 of 12 modes;
Option A's hard-block mode is NOT compatible with Option E
(pre-dispatch symbol required per S1272 §4.3 table row). Option A
ship requires either (a) Symbol Mapping A/C graduation per S1274
§10.3.1 triggers OR (b) `Step.action_classes_invoked` declaration
extension without Symbol Mapping migration (option-A-in-isolation
path).

**Failure modes (S1272 §9.1 + P2 additions).**

- Step declares no `action_classes_invoked` → fail-open vs
  fail-closed default triggers D90.
- Action taken outside MissionRunner surface → no enforcement (P2
  documents; not a bug, structural).
- Signal-quality maintenance burden (Rigby S1272 SIGN inherited):
  every step author must accurately declare + keep in sync.
  Verified from Explore 2 no-existing-precedent verdict.

**P2 verdict on Option A viability today.** **NOT MECHANICALLY
SHIPPABLE at P2 close under S1274 Option E v0 constraint.**
Recommended lean: pre-provision the toggle field (Option A-adjacent
scaffolding per D90/D91 recommended lean) but do NOT ship the
enforcement branch until Symbol Mapping graduation triggers fire.

### 7.2 Option B — ToolDispatcher-centered enforcement

**Shape (S1272 §9.2).** Authority checked at Boundary 2
(`ToolDispatcher.execute()` entry) and Boundary 3 (PA tool handler
body).

**Current-state reuse footprint (Explore 1 verified).**

- `AssistantProfile.get_allowed_tools()` gate at
  `tool_dispatcher.py:687-720` (stable; Session 1171 #4 typed-exception
  rework unchanged) provides the extension shape.
- `TOOL_PERMISSION_DENIED` error code at `tool_dispatcher.py:702`
  provides the deny-shape precedent.
- Tool schema layer at `core/services/pa_tool_schemas.py` (~113 PA
  tool schemas per PLATFORM_INVENTORY autoblock) provides the
  per-tool annotation surface.

**Current-state gap.**

- **NO `action_class` field on any PA tool schema today.** Option B
  requires ~113 tool schemas each annotated with `action_class` per
  action (or explicit `None` sentinel).
- **Signal-quality maintenance burden.** Every one of the ~113 PA
  tool schemas needs an `action_class` annotation; drift between
  annotation and handler behavior is a primary failure mode.

**Prevented actions.** PA tool dispatches that violate authority
(strong caller identity chain per P1 §7.3 row 2:
`user_id → profile FK`). Direct tool calls from any caller (Rigby /
Chris / Claude Code). Tool-mediated actions on Deliverable /
DirectMessage / OpsRun.

**Missed actions.** Actions outside tools (raw ORM in mgmt
commands, direct Django queries). Celery tasks not routed through
ToolDispatcher (Boundary 8/9). Actions dispatched via
`AgentRouter.route` bypassing PA tool layer (Boundary 15).
Step body actions inside MissionRunner not routed through
ToolDispatcher (Boundary 6/7).

**Implementation risk.** Low-to-medium. Extends a well-understood
gate. But requires 113 tool-schema updates.

**Operational risk.** Medium. Tool dispatch is high-traffic;
per-call gate overhead matters.

**Observability.** Strong. `ToolCallRecord` writes on every dispatch
(Explore 4 confirmed 16-field model; no `action_class` field
today); violation events would parallel.

**Rollback strategy.** Feature flag globally; per-user
`allowed_tools` provides a partial rollback pathway.

**Compatibility with Employee OS.** Medium. Tool-layer enforcement
is orthogonal to per-employee authority scope; requires per-caller
identity → employee_handle resolution which P1 §7.3 flagged as
partial across boundaries.

**Compatibility with S1274 Option E v0.** **Not compatible.**
Symbol Mapping Option B is the graduation target for
ToolDispatcher-centered enforcement; Option E is the audit-first
graduation path. Option B ship requires S1274 §10.3.1 trigger
firing + Option B migration.

**Failure modes.** Tool without `action_class` (default fail-open
or fail-closed?). Caller identity → employee_handle resolution
weak at Boundaries 3/15 (P1 §7.3 verified). Employee-independent
calls (Chris directly) not covered by employee authority contract.

**P2 verdict on Option B viability today.** **NOT MECHANICALLY
SHIPPABLE at P2 close.** Recommended lean: rejected at P2 close
(D86 rationale). Reconsider at S1274 Option B graduation trigger
firing.

### 7.3 Option C — Audit-first enforcement (evidence-only)

**Shape (S1272 §9.3).** Every action emits `action_class` in its
audit row (ToolCallRecord + OpsRunEvent + LLMCallEvent +
CeleryTaskEvent). Violations detected retrospectively via
post-mission audit or a periodic scan. **No pre-dispatch
enforcement.**

**Current-state reuse footprint (Explore 4 + Explore 5 verified).**

- Existing audit chain (16-field `ToolCallRecord` + 5-field
  `OpsRunEvent` + 16-field `LLMCallEvent` + 17-field `CeleryTaskEvent`
  + `AgentExecution`) provides the extension shape.
- `evidence_for_mission` at `core/employees/status.py:53-251` provides
  the read-side aggregation precedent.
- Bug Triage step 4 aggregation pattern at
  `core/services/bug_triage.py:396-453` provides the retrospective
  scan precedent (mission-adjacent already, per S1272 §9.3
  citation).
- `AUTHORITY_CONTRACT_OBSERVED_LABEL` at `mission_runner.py:264` +
  emission at `mission_runner.py:882` — 13 events since 2026-06-30
  17:06:27 UTC (Explore 5). Steady daily cadence (2-3/day). Modal
  level_counts: PROHIBITED ~9, EXECUTE ~5, OBSERVE ~4, RECOMMEND ~2.

**Current-state gap (Explore 4 verified).**

- **`action_class` field ABSENT on all 5 audit models.** 0 of 5
  models have the column; 0 migrations touch it. S1274 Option E v0
  is defined-but-not-migrated.
- **NO `AUTHORITY_CONTRACT_VIOLATED` event schema** (S1272 prereq
  #4). Explore 5 confirmed 0 events with the label; 53 distinct
  OpsRunEvent labels exist all-time and none is violation-related.
- **NO `authority_violation_retrospective_scan` beat task**
  registered.

**Prevented actions.** **Nothing at execution time.** Violations
become observable + reportable retroactively.

**Missed actions.** All pre-dispatch prevention. Real-time gating
for catastrophic actions. Any hard-block use case.

**Implementation risk.** Low. Purely additive; no gate logic;
existing audit chain extended. Two Option-C-primary ship-path
sub-steps: (i) `action_class` column migration on 5 audit models
(S1274 Option E v0 execution; NOT re-litigated at P2); (ii)
retrospective scan beat task creation.

**Operational risk.** Very low. No false-positive rate on
enforcement (never blocks). Fail-open by construction.

**Observability.** Very strong. Every action logged with
`action_class` post-migration; retrospective query surfaces
violations. Modal level_counts distribution (Explore 5) already
provides baseline shape.

**Rollback strategy.** Trivial — remove periodic scan job; audit
schema addition is backwards-compatible (nullable field).

**Compatibility with Employee OS.** High. Additive to existing
audit patterns per `EMPLOYEE_OS_PRIMITIVES.md` §4.

**Compatibility with S1274 Option E v0.** **Directly compatible.**
Option C is the enforcement-side companion to Symbol Mapping
Option E; the two design against the same evidence-only shape.
P2 recommends Option C-primary as the S1274-Option-E-v0-aligned
enforce-mode ship.

**Failure modes (S1272 §9.3 + P2 additions).**

- **Producer omission** — code path writes audit row without
  populating `action_class` → silent gap. Mitigation: S1274
  §10.3.1 graduation trigger #3 (NULL rate > 30% after Phase 4)
  addresses producer-inventory-completeness gap.
- **Consumer lag** — violations detected in next Bug Triage cycle
  (or in `authority_violation_retrospective_scan` beat cadence),
  not real-time.
- **Cannot support hard-block-required actions** — delete DB rows,
  publish externally, etc. Would require Option A/B/D/E-multi-layer
  addition (post-graduation Chris-gated).

**Unknowns (S1272 §9.3 inherited).** Does audit-only support
graduation to enforce-mode later, or is it terminal? Per S1274
§10.3.1 F7 disclaimer (Explore 4 verified 4 graduation triggers
including 90-day timer): reversibility ≠ preference; Option C is
graduation-compatible.

**P2 verdict on Option C viability today.** **MECHANICALLY
SHIPPABLE — primary recommendation.** Option C aligns with S1274
Option E v0 selection; can be shipped without Symbol Mapping
option migration; graduation-compatible via S1274 §10.3.1
triggers. Recommended lean D86 = Option C-primary.

### 7.4 Option D — Human-approval enforcement (HAI-mediated)

**Shape (S1272 §9.4).** Certain authority levels (typically
RECOMMEND, but extensible to PROHIBITED) trigger `HumanAttentionItem`
creation before the action executes. Human approval unblocks
execution; rejection blocks + logs.

**Current-state reuse footprint (Explore 6 verified).**

- `HumanAttentionItem` model + lifecycle service (13-field model;
  3594 items over 22 days = 163.36/day all-time / 119.8/day last
  30 days).
- `OrchestrationApprovalGate` bridge at
  `core/models_orchestration.py:397-535` — bridges orchestration
  step → HAI via `attention_item_id` UUID field (line 420). Fields
  include `status` (choices: pending / approved / rejected /
  modified / auto_approved / expired), `approval_config` (JSONField),
  `expires_at`, `decided_at`, `decided_by` (FK User); methods
  `approve()` / `reject()` / `modify()` / `auto_approve()` /
  `is_expired()`. Verified present + mature.
- HAI decide endpoint at `core/views_human_interface.py:154` (Explore 1
  cross-verified endpoint boundary at line 154 not line 84 as
  S1272 stated; the `get()` method starts at line 95, actual decide
  view at 154). Auth guard: `@login_required` + user-item ownership
  filter `user=self.user` at `human_interface_service.py:317`.
- HAI auto-approve 8-condition gate at
  `human_attention_lifecycle.py:223-296` (Explore 6): 7 core
  business-logic gates + 2 existence checks = 8 total; S1269 §2.4's
  citation of 7 refers to the 7 core gates.

**Current-state gap.**

- **No `authority` → HAI creation signal.** 31 HAI creators exist
  (per S1272 §9.4 count); none is authority-triggered.
- **Per-level policy undefined.** Which levels create HAI?
  RECOMMEND-default is S1272 §9.4 shape but must be Chris-picked.
- **HAI capacity headroom.** 120-163 items/day baseline; adding
  authority-triggered HAI at O(10-50/day) does not drown existing
  volume per Explore 6 assessment. spider_pipeline dominates
  (3368/3594 = 93.7%) so authority-source addition is quantitatively
  small.

**Prevented actions.** RECOMMEND-level actions from executing before
human review. Configurable subset of PROHIBITED (soft-block variant).

**Missed actions.** EXECUTE-level actions (no review needed by
definition). OBSERVE-level (read-only). Volume overhead — if
RECOMMEND creates HAI per action, approval fatigue possible per
S1272 §10 anti-pattern #14.

**Implementation risk.** Medium. New signal integration using
existing primitives.

**Operational risk.** High. Approval fatigue documented (S1272 §10
#14); HAI capacity ~100 items/day max per prior audits (Explore 6
verified 120-163/day actual). Authority-source addition manageable
but composition with existing sources (spider_pipeline 93.7% share)
requires precedence policy in D88.

**Observability.** Strong. HAI creation + decision + feedback chain
well-instrumented (S1269 F5).

**Rollback strategy.** Feature flag on `authority → HAI` signal.

**Compatibility with Employee OS.** High. HAI is canonical
human-in-loop primitive per `EMPLOYEE_OS_PRIMITIVES.md` §4.4.

**Compatibility with S1274 Option E v0.** **Not directly compatible
today.** Option D requires Symbol Mapping A/B/C/D (need to know
`action_class` to decide whether HAI required). Ship path requires
S1274 §10.3.1 trigger firing + graduation to Symbol Mapping A/B/C/D.

**Failure modes.** Approval fatigue (S1272 §10 #14). Auto-approve
gate 7-condition may over-approve if authority level is treated
as a trust signal without composition policy (D88). HAI creator
misclassification (source_type wrong) breaks auto-approve.

**Unknowns.** Cross-source collision policy when
authority-triggered HAI competes with 31 existing creators.

**P2 verdict on Option D viability today.** **NOT MECHANICALLY
SHIPPABLE at P2 close.** Recommended lean: rejected at P2 close
(D86 rationale); reconsider at S1274 graduation trigger firing.
May also be a companion to Option C-primary post-graduation —
Option D on top of Option C is a natural composition when Symbol
Mapping graduates.

### 7.5 Option E — Multi-layer enforcement

**Shape (S1272 §9.5).** Different boundaries enforce different
authority levels. E.g., PROHIBITED at Boundary 1 (HTTP middleware)
and Boundary 2 (ToolDispatcher); RECOMMEND via HAI at Boundary 4/6;
EXECUTE observed at Boundary 5 (warn-mode retained); OBSERVE
enforced via read-only DB scope.

**Current-state reuse footprint.** All of Options A-D primitives
combined.

**Current-state gap.** All of Options A-D gaps combined + a
composition contract answering *"which boundary is authoritative
for which level?"*

**Prevented actions.** Broadest coverage: each level enforced at
the boundary that fits its semantic best.

**Missed actions.** Uniformity — no single answer to "who enforces
authority." Debuggability suffers when multiple layers vote.

**Implementation risk.** High. Multiple integration points;
composition semantics must be nailed down. Note: "Option E" is the
S1272 §9.5 multi-layer enforcement option, **distinct from S1274
Symbol Mapping Option E** (evidence-only). Adjacent labeling
overlap flagged as inherited-in drift risk; use "Option E
(multi-layer)" vs "Option E v0" in cross-references to
disambiguate.

**Operational risk.** Medium-high. Cascade risk if one layer's
enforcement fails.

**Observability.** Complex — evidence spread across multiple layers.

**Rollback strategy.** Layer-by-layer feature flags; can partially
rollback.

**Compatibility with Employee OS.** Medium. High coordination cost.

**Compatibility with S1274 Symbol Mapping Option E v0.** **Not
compatible.** Multi-layer requires Symbol Mapping B/C/D (need
`action_class` in multiple places). Ship path requires graduation
trigger firing + Symbol Mapping B/C/D migration.

**Failure modes.** Layer A blocks; Layer B allows (or vice versa).
Precedence semantics unclear. Audit trail requires cross-layer join.

**P2 verdict on Option E (multi-layer) viability today.** **NOT
MECHANICALLY SHIPPABLE at P2 close.** Recommended lean: rejected
at P2 close (D86 rationale); reconsider at post-graduation Chris-gate.

### 7.6 Option F — Governance-plane composition

**Shape (S1272 §9.6).** Authority enforcement composes with the 4
existing governance planes into a unified decision. Explicit
precedence policy (e.g., KillSwitch > GovernanceState.freeze >
Authority PROHIBITED > Budget freeze > HAI pending).

**Current-state reuse footprint (Explore 3 verified — with S1272
GAP-7 correction).**

- `GovernanceState.mode='freeze'` — 4 consumers verified
  (`tasks_spiders.py:386` + `signal_aggregation_service.py:225` +
  `signal_aggregation_service.py:969` + `workspace_pipeline_runner.py:44`).
  Matches S1272 §7.2 claim exactly.
- `SystemConfiguration.budget_freeze_active` — 6 read/write sites
  (LLMEnforcer read at 201-221 + 5 in ops_autopilot governance +
  budget modules).
- **KillSwitch** — **S1272 GAP-7 "write-only" REFUTED** per Explore 3.
  Verified 2 WRITE sites + 4 DISPATCH-CONSUMER read sites
  (`governance.py:2192` status read, `governance.py:2508` expiry
  gate, `intelligence.py:1717` cleanup gate, plus one status-read at
  `governance.py:2192` counted twice above) + 2 AUDIT read sites =
  6 total READ sites, not the 10+ S1901 Agent 6 speculated. KillSwitch
  IS being read as a dispatch gate today.
- Autonomy → Budget one-way sync at `governance.py:2273`
  (`_sync_budget_flags`) — verified (S1269 F4 precedent).
- HAI auto-approve gate at `human_attention_lifecycle.py:223-296` —
  verified 8 conditions total; 7 core business-logic gates
  excluding 2 existence checks.

**Current-state gap.**

- **8 composition questions unanswered** (S1272 §7.5). P3 (S1903)
  is the child that answers these; P2 provides partial input.
- **Per-plane feature flags exist** but no unified precedence
  policy shipped.

**Prevented actions.** Broadest possible: authority + autonomy +
budget + human all compose into single decision.

**Missed actions.** Simplicity — complexity moves to composition
policy.

**Implementation risk.** Very high. Requires closing S1269 gaps
(KillSwitch dispatch expansion — post-verifier-loop the "reader"
addition is partial rather than full since 4 dispatch readers
exist), per-scope reads on `GovernanceState`, throttle mode
composition.

**Operational risk.** High. Multi-plane decisions are hard to
debug.

**Observability.** Must design cross-plane audit trail.

**Rollback strategy.** Per-plane feature flags.

**Compatibility with Employee OS.** High if precedence semantics
clear; very low if unclear.

**Compatibility with S1274 Option E v0.** **Partial.** Option F is
scope-independent of Symbol Mapping option choice; the composition
policy is authority-side. However, Option F's authority-side reads
still constrain to F9 (Option E → 5 modes) until graduation.

**Failure modes (S1272 §9.6 + P2 additions).**

- Plane precedence choice codifies wrong policy.
- Desync between planes cascades (per S1269 F4).
- Policy ossification / precedence lock-in (Rigby S1272 SIGN).

**P2 verdict on Option F viability today.** **NOT MECHANICALLY
SHIPPABLE at P2 close** as a self-contained option. P2 provides
partial cross-plane input in §12 D88 recommended lean; P3 (S1903)
completes the composition. Recommended lean: partial Option F
composition (KillSwitch precedence + autonomy precedent) codified
at P2 D88 for P3 to consume.

### 7.7 Cross-option summary + P2 mechanical-compatibility verdict

| Option | S1272 §9 shape | P2 mechanical-compatibility with S1274 Option E v0 today | Mechanical-state classification at P2 (Chris-gated in §12) |
|---|---|---|---|
| **A: MissionRunner-centered** | Boundaries 4/5/6 pre-dispatch | Constrained — pre-dispatch blocked by F9 until Symbol Mapping A/C graduation; scaffolding pre-provisionable | **Scaffolding-only (no enforcement until graduation)**: add `MissionRunnerConfig.enforce_authority_mode` field defaulting `warn`; enforcement branch dead code until graduation |
| **B: ToolDispatcher-centered** | Boundaries 2/3 pre-dispatch | Not compatible — Symbol Mapping B required | **Not shippable-now under Option E v0; parked (re-eval at graduation)** |
| **C: Audit-first (evidence-only)** | Post-dispatch audit, retrospective scan | **Directly compatible** — Option E v0 companion | **Recommended lean (Option-E-compatible shippable-now)** — Option C-primary ship-path |
| **D: HAI-approval-mediated** | RECOMMEND → HAI creation pre-dispatch | Not compatible — Symbol Mapping A/B/C/D required | **Not shippable-now under Option E v0; parked (re-eval at graduation)** |
| **E: Multi-layer** | Cross-boundary composition | Not compatible — Symbol Mapping B/C/D required | **Not shippable-now under Option E v0; parked (re-eval at post-graduation Chris-gate)** |
| **F: Governance-plane composition** | Cross-plane authority + KillSwitch + freeze + HAI | Partial — authority-side reads still F9-constrained | **Partial (D88 precedence input for P3)**; P3 completes composition |

**Recommended P2 shape (Chris-gated).** **Hybrid Option C-primary +
Option A-adjacent scaffolding**, with Options B/D/E/F explicitly
parked with rationale in §12 D86.

---

## 8. Data Ownership and Lifecycle

Design-decision scope. Data ownership under Option C-primary +
Option A-adjacent lean:

- **`authority_contract_observed` OpsRunEvent rows** — owned by
  MissionRunner (writer). Retention per S1272 §11 prereq TBD;
  cross-arc handoff R.OBSERVABILITY.RETENTION-UNIFIED-ADR (Group
  1700 T0/Gate) governs. Explore 5: 13 rows all-time; no dedicated
  retention policy today. Under Option C ship, retention volume
  grows with authority-scan cadence but only on trigger events
  (evidence detection).
- **`authority_contract_violated` OpsRunEvent rows (proposed)** —
  owned by `authority_violation_retrospective_scan` beat task
  (writer). Retention same as observed events. Post-arc T1.
- **`MissionRunnerConfig.enforce_authority_mode` field** — set by
  factory sites in `core/employees/jobs.py` (per-employee factory)
  or overridden per-mission via kwarg. Default `"warn"`
  backwards-compatible.
- **`AIEmployee.enforce_authority_mode` field** — set by employee
  registry entries in `core/employees/jobs.py:73-91`. Default
  `"warn"`.
- **`SystemConfiguration authority_enforce:*` keys** — owned by
  Chris via admin surface or `platform_config_tool`. Read-only at
  ship until graduation.

**Lifecycle at P2 ship (Option C-primary + Option A scaffold).**

1. MissionRunner emits `authority_contract_observed` on each
   mission (current-state; unchanged).
2. `authority_violation_retrospective_scan` beat task (new;
   post-arc) reads observed events + eventual `action_class` +
   actor context columns; emits `authority_contract_violated` on
   detection.
3. Per-employee `enforce_authority_mode` toggle (new; ships at P2
   close as `"warn"` default; enforcement branch is dead code
   until Symbol Mapping graduation).
4. Under Symbol Mapping graduation post-arc: `authority_enforce_gate_service.check(mission,
   action_class)` becomes live; reads toggle + thresholds; gates
   pre-dispatch per Option A/B/D/E graduation choice.

---

## 9. Integrations With Other Domains

| Domain | Contact surface | Direction | Cross-arc handoff |
|---|---|---|---|
| Employee OS (Group 1200 legacy + S1272) | MissionRunner + JobContract + AIEmployee | Bi-directional (P2 extends dataclass fields; MissionRunner reads toggle at graduation) | Own arc; no external handoff |
| HAI (Group 1800) | Boundary 16 decide endpoint; auto-approve gate | Read-only at P2; write-side deferred to Option D graduation | Cross-arc — P3 Cat C composition consumes for cross-plane precedence |
| Content pipeline (Group 1600) | Deliverable actions (via `Deliverable.user` FK — P1 §4 catalogued) | Read at retrospective scan; no P2 write | Cross-arc — P4 Cat F seam audit |
| Sports (Group 1500) | Discord command dispatch (Boundary 3 tool path) | Read at retrospective scan under Option C-primary | Cross-arc — P3 authority × Discord composition question 8 |
| Observability (Group 1700) | Audit event retention posture | Retention policy dependency | Cross-arc — R.OBSERVABILITY.RETENTION-UNIFIED-ADR (Group 1700 T0/Gate) |
| Fleet | HMAC identity + `app_slug` (Boundary 19) | Verified Explore 3 at `fleet_auth_drf.py:65-150` (permissive fallback preserved) | Own arc; own T-slot |
| Memory (Group 1300) | Learning-plane contract | Deferred — P3 Cat C interacts | Cross-arc — R.HAI.LEARNING-PLANE-CONTRACT-ADR (Group 1300+1800 T0/Gate) |
| Autonomy (S1269) | Autonomy → Budget one-way sync at `governance.py:2273` | Read-only under P2 D88 partial precedence input | Cross-arc — P3 Cat C completes composition |

---

## 10. Event Flows

### 10.1 Current-state (unchanged at P2 ship)

```
MissionRunner._emit_authority_contract_event(mission)
  ├─ shape-validate JobContract.authority + prohibited_actions
  ├─ raise _AuthorityContractMalformedError on malformed (verified
  │  Explore 5: 0 fires all-time)
  ├─ compute level_counts accumulator (F1 shape-counter)
  └─ emit OpsRunEvent(label='authority_contract_observed',
                       event_type='info',
                       detail={schema_version: 1,
                               employee_handle, contract_title,
                               contract_version_tag,
                               authority_entries_total,
                               authority_level_counts,
                               authority_unknown_level_count,
                               prohibited_actions_count,
                               mode: 'warn', note})
```

### 10.2 Post-P2 (D90 field lands; observation still fires)

```
MissionRunner._emit_authority_contract_event(mission)
  ├─ ...as above; unchanged shape...
  └─ emit OpsRunEvent(...
                     detail={...
                             mode: self.config.enforce_authority_mode,
                                    # 'warn' default; reads new field
                             ...})
```

Under D90 recommended lean, the hardcoded `mode="warn"` on line 894
becomes `mode=self.config.enforce_authority_mode`. Value default is
still `"warn"` so runtime behavior is unchanged at P2 ship; the field
is scaffolding for post-graduation `observe` / `warn` / `enforce`
transitions.

### 10.3 Post-graduation (Option C-primary + retrospective scan)

```
authority_violation_retrospective_scan (Celery beat)
  ├─ Cadence: TBD (recommended default 5 min; D93 threshold policy)
  ├─ Read: OpsRunEvent(label='authority_contract_observed',
  │                    created_at >= last_scan_high_watermark)
  ├─ For each event:
  │   ├─ Load associated OpsRun + P1 T1 R.AUTHORITY.OPSRUN-ACTOR-COLUMNS
  │   │   (post-P1-graduation; F6b closeable per S1901 §7.4)
  │   ├─ Load associated ToolCallRecord + action_class column
  │   │   (post-Option-E-migration; nullable)
  │   ├─ Cross-reference JobContract.authority dict for
  │   │   employee_handle: check if action_class value is in
  │   │   PROHIBITED-level entries
  │   └─ On match: emit OpsRunEvent(
  │                     label='authority_contract_violated',
  │                     event_type='error',
  │                     detail={schema_version: 1,
  │                             action_class, level_expected,
  │                             employee_handle, executor_actor,
  │                             sponsor_actor, principal_user_id,
  │                             enforcement_mode_at_time})
  └─ Update last_scan_high_watermark
```

Under Option D graduation, a `HumanAttentionItem` is created per
violated event with `source_type='authority_violation'` +
`urgency='high'`.

Under Option A graduation, the pre-dispatch gate at Boundary 6
(before `step.fn(mission)`) reads the level → policy binding and
raises `AuthorityViolationBlocked` before invocation.

---

## 11. Existing Documentation

Consumed by P2 as input:

- **S1272** `docs/research/authority_enforcement_design_space.md` —
  20 boundaries + 12 modes + 15 prereqs + 6 options (§9) + 11
  findings F1-F11 + 15 anti-patterns.
- **S1274** `docs/research/symbol_mapping_option_selection_design.md`
  — Symbol Mapping Option E v0 selection; §10.3.1 graduation
  triggers.
- **S1271** `docs/research/actor_identity_attribution_architecture.md`
  — three-role vocabulary (executor / sponsor / principal); F6
  drop boundaries (F6a/F6b/F6c); F11 mechanical prohibition.
- **S1269** `docs/research/governance_authority_evolution.md` — 4
  planes don't compose; autonomy → budget one-way sync; F1/F2/F3/F4.
- **S1264** handoff — warn-mode rollout precedent; Rigby SIGN edits
  #1 (schema-version bump discipline) + #5 (malformed contract as
  signal, not silent).
- **S1900** parent scoping — arc contract; §5.2 P2 spec;
  D81-D85 Chris-locked + D86/D87 → O1/O2 reclassified.
- **S1901** P1 Cat A doc — three-role propagation contract + 20-row
  Layer-ii per-boundary table + drop-boundary register.

Produced by P2:

- This doc (§1-§20).
- Extensions to `EMPLOYEE_OS_PRIMITIVES.md` §4 (per-employee
  toggle discipline) — recommended post-arc PR under D91.

---

## 12. Decision Rationale + Alternatives Rejected

**Section shape (per parent §5.2).** Playbook §11.2 §12 Research
Coverage becomes Decision Rationale + Alternatives Rejected for
design-decision docs. Eight Chris-gated D-verdict slots (D86–D93).
Each slot follows the shape: **recommended lean → alternatives
with rejection rationale → reversibility rating**.

**Chris-gate ratification — 2026-07-04.** Chris ratified all
8 D-verdicts (D86 through D93) via **"agree all"** shortcut per
S1900 §11 pattern on arc pin `pa-2bd1613ce2bd4a9c`. No line-item
overrides. **All 8 recommended leans below are Chris-locked as
the P2 design decision.** Each individual slot preserves its
alternatives + rejection rationale for future reference; the
ratified lean is the canonical enforcement design.

**Chris D-gate protocol used.** Multi-verdict "agree-all"
shortcut per S1900 §11 §11.1 pattern; Chris explicitly opted in
with response "agree all" on 2026-07-04 following Rigby SIGN
cycle 1 SIGN-with-edits at High confidence with 3 folds landed
pre-commit (Q1 §7.7 de-endorsement + Q2 §17.2 roll-up recompute +
Boundary 11 rationale caveat + Q3 §12.8 D93 data-sufficiency
floor promoted to lean).

### 12.1 D86 — Options A/B/C/D/E/F pick (or hybrid)

**Recommended lean.** **Hybrid Option C-primary + Option A-adjacent
scaffolding.**

- Option C (Audit-first / evidence-only) as the substantive
  enforcement shape.
- Option A-adjacent scaffolding: add `enforce_authority_mode` field
  to both `MissionRunnerConfig` and `AIEmployee` dataclasses,
  default `"warn"`. Enforcement branch is dead code until Symbol
  Mapping graduation (S1274 §10.3.1 triggers).
- Options B / D / E-multi-layer / F explicitly parked with rationale
  in §12.1 alternatives; reconsider at S1274 graduation trigger
  firing.

**Rationale.**

- Option C is the ONLY option mechanically compatible with the
  S1274 Option E v0 selection today (§7.3 verdict; F9 constraint).
- Option A-adjacent scaffolding pre-provisions the toggle so
  graduation ships as a code-review-gated feature-flag flip, not
  a schema migration.
- Options B/D/E/F all require Symbol Mapping A/B/C/D graduation
  first; picking them at P2 would violate S1272 §10 anti-pattern
  #8 (enforcement before symbol mapping) and parent §5.2
  migration-recommendation clarifier.

**Alternative 1 rejected — pure Option C (no Option A scaffolding).**
Would ship the retrospective scan without the per-employee toggle
field. Rejected because: at S1274 graduation, adding the field
would require touching all AIEmployee registry entries + all
factory sites; pre-provisioning at P2 costs one dataclass field
addition (backwards-compatible default).

**Alternative 2 rejected — pure Option A (pre-dispatch enforcement now).**
Would ship enforcement at Boundary 6 without waiting for Symbol
Mapping A/C graduation. Rejected because: violates S1272 anti-pattern
#8; would require `Step.action_classes_invoked` extension outside
S1274 governance; risks fail-open-everywhere or fail-closed-mass-
outage per S1272 Tier-0 hazard callout.

**Reversibility.** HIGH. Option C ships as a beat task (removable);
scaffolding is a nullable field (removable with migration).

### 12.2 D87 — Mode subset pick

**Recommended lean.** **5-mode subset:** observe-only, warn-mode
(retained), degrade-mission-evidence, freeze-platform,
retrospective-violation-report.

**Rationale.**

- Direct application of S1272 §4.3 F9 constraint under S1274
  Option E v0 (verified authoritative count = 5, not 4 as
  parent scoping stated — see §14 drift entry).
- observe-only + warn-mode: already fire under current-state
  (verified 13 events since 2026-06-30).
- degrade-mission-evidence: `OpsRun.summary[degraded]` flag already
  a partial precedent; extend under retrospective scan.
- freeze-platform: cross-plane composition read (already-existing
  4 consumers per Explore 3); authority-side read added under D88.
- retrospective-violation-report: the substantive P2-recommended
  enforcement action; ships under `authority_violation_retrospective_scan`.

**Alternative 1 rejected — 4-mode subset (drop freeze-platform).**
Would treat freeze-platform as governance-only (not authority).
Rejected because: freeze-platform is the ONLY cross-plane composition
mode currently in scope for Option F partial precedence (D88); removing
it strands P3 without input.

**Alternative 2 rejected — 12-mode superset (all modes selectable).**
Would ship all 12 modes as available config options. Rejected
because: violates F9 constraint under S1274 Option E v0; 7 modes
would be dead configuration at ship.

**Reversibility.** MEDIUM. Mode subset can be extended at
graduation without breaking existing enforcement (additive).

### 12.3 D88 — Precedence policy pick (partial; P3 completes)

**Recommended lean.** **Partial precedence: KillSwitch > authority
PROHIBITED > freeze-platform > authority RECOMMEND > HAI auto-approve.**

- KillSwitch (verified 6 read sites per Explore 3 — 4 dispatch
  gates + 2 audit) — the platform-wide operator-controlled bypass;
  highest precedence.
- Authority PROHIBITED — evaluated after KillSwitch (KillSwitch
  drops before authority reads occur).
- freeze-platform — evaluated as a compositional check; P3
  finalizes whether freeze precedes or follows PROHIBITED under
  cross-plane composition question 5 (authority × freeze).
- Authority RECOMMEND — evaluated after freeze-platform;
  RECOMMEND-level actions trigger HAI creation only if HAI
  auto-approve does NOT apply (post-D-graduation).
- HAI auto-approve — 7-condition gate (Explore 6: 8 gates total, 7
  core business-logic gates + 2 existence checks) evaluated as
  final composition step under Option D graduation.

**Rationale.**

- KillSwitch precedence highest per S1272 §7.5 Q4 default answer;
  operator kill supersedes any policy layer.
- Authority PROHIBITED before freeze because a prohibited action
  should NEVER complete, whereas freeze is a temporary halt of
  non-critical execution.
- P3 finalizes 8 composition questions; P2 provides these 5
  partial precedence entries as input scope for P3 §7 (Cross-Plane
  Composition Design).

**Alternative 1 rejected — full precedence policy at P2.**
Would answer all 8 S1272 §7.5 composition questions at P2. Rejected
because: violates parent §5.2 P3 scope reservation; overloads P2
runtime target (1-2 sessions per parent §5.5).

**Alternative 2 rejected — no precedence at P2.**
Would defer all precedence to P3. Rejected because: P3 needs P2
partial precedence input (per parent §5.3 line 686 dependency);
P2 must produce at least the KillSwitch + authority-side entries.

**Reversibility.** MEDIUM. Partial precedence is codified as an
ADR-adjacent decision at P2 close; P3 can revise but must document
what changed.

### 12.4 D89 — Fail-open vs fail-closed default pick

**Recommended lean.** **Fail-open (following F8 LLMEnforcer precedent).**

- Under Option C-primary lean: `authority_violation_retrospective_scan`
  fail-open by construction (never blocks; only detects).
- Under Option A-adjacent scaffolding: `enforce_authority_mode`
  toggle default `"warn"` is functionally fail-open at ship.
- Under post-graduation `enforce` mode: the pre-dispatch gate at
  Boundary 6 or Boundary 2 fails open per F8 precedent. Explicit
  `except Exception: pass` swallow with `logger.error(...)`
  greppable-prefix log line for observability.

**Rationale.**

- F8 verified at pre-Explore (`llm_enforcer.py:237-238` +
  `:263-264`) as the closest existing INLINE-gate precedent (Explore 1
  verified 3 fail-open sites total: 2 in llm_enforcer + 1 in
  tool_dispatcher log-but-not-raise).
- Fail-closed on internal error would violate S1272 §10 anti-pattern
  #1 (blocking all model writes) if the check errors on a widely-used
  code path.
- Warn-mode fires 2-3 events/day; if the gate errors and blocks
  every mission, all 4 employees would halt. Fail-open bounds the
  blast radius.

**Alternative 1 rejected — fail-closed default.**
Would block on internal check error. Rejected because: LLMEnforcer
precedent is fail-open; F8 grounded in S1088 budget-freeze incident
where a bad config blocked all non-critical LLM calls. Fail-closed
authority would compound this risk to mission-level halts.

**Alternative 2 rejected — mode-dependent posture.**
Would fail-open for OBSERVE + RECOMMEND, fail-closed for
PROHIBITED. Rejected because: introduces branch complexity that
would violate F5 verifier discipline (fail modes hard to reproduce);
graduation-time can pick differentiated posture per level.

**Reversibility.** HIGH. Default posture is one line at the gate
site; can flip per mode config post-graduation.

### 12.5 D90 — Level → decision binding design

**Recommended lean.** **`MissionRunnerConfig.enforce_authority_mode`
field, 3-value enum: `"observe"` / `"warn"` (default) / `"enforce"`.**

- `"observe"` — event fires, level_counts accumulator runs, but no
  gate check. Fully non-blocking. Reserved for pre-warn-mode
  employees (none exist today).
- `"warn"` — current-state behavior (S1264). Event fires with
  mode string preserved.
- `"enforce"` — post-graduation. Under Option A scaffolding, the
  pre-dispatch gate at Boundary 6 (or Boundary 2 under Option B
  graduation) reads the toggle + reads the effective JobContract.authority
  dict + reads action_class (post-Option-E-migration) + gates per
  level policy binding.

**Level policy binding (Chris-gated fold at graduation, not P2).**

- OBSERVE → allow, record.
- RECOMMEND → allow + emit `authority_recommend_observed`; optional
  HAI creation post-Option-D-graduation.
- EXECUTE → allow (default authority; the employee is authorized
  to execute this action_class).
- PROHIBITED → block; emit `authority_contract_violated` event;
  raise `AuthorityViolationBlocked` at gate site.

**Rationale.**

- Toggle name matches Option A recommended shape (D86).
- Default `"warn"` matches current-state — backwards-compatible.
- Field on `MissionRunnerConfig` composes with per-mission override;
  parallel `AIEmployee.enforce_authority_mode` field on the registry
  provides per-employee default.

**Alternative 1 rejected — boolean flag `enforce_authority: bool`.**
Would use a single boolean. Rejected because: precludes future
`observe` / `warn` / `enforce` graduation; loses the "record but
don't act" nuance that S1264 established.

**Alternative 2 rejected — level-specific toggle
(`enforce_prohibited_mode`, `enforce_recommend_mode`, etc.).**
Would introduce per-level config granularity. Rejected because:
premature granularity per parent §5.2 anti-scope (design-decision
blur); S1272 F5 verifier discipline prefers uniform interface.
Post-graduation can extend without breaking the single-field
default.

**Reversibility.** HIGH. Field is nullable-with-default; can be
removed with a data migration. Enum values can be extended
additively.

### 12.6 D91 — Per-employee opt-in mechanism

**Recommended lean.** **Two-tier per-employee toggle: AIEmployee
default + MissionRunnerConfig runtime override.**

- `AIEmployee.enforce_authority_mode: str = "warn"` (new field;
  6th field on the 5-field frozen dataclass).
- `MissionRunnerConfig.enforce_authority_mode: str = "warn"` (new
  field; 17th field on the 16-field dataclass).
- **Composition rule (max-strictness).** Effective mode is the
  STRICTER of `AIEmployee` field and `MissionRunnerConfig` field
  at mission time. Ordering: `"observe"` < `"warn"` < `"enforce"`.
- **Rollout pattern.** Matches S1264 warn-mode: all 4 employees
  land with `AIEmployee.enforce_authority_mode="warn"` at P2 ship;
  per-employee graduation to `"enforce"` is a Chris-gated
  registry-level edit + factory-site kwarg override.

**Rationale.**

- Two-tier composition preserves per-employee-registry-default
  discipline while allowing per-mission override for canary tests.
- Explore 6 verified: no existing per-employee opt-in mechanism
  (AIEmployee frozen dataclass = 5 fields; no `SystemConfiguration
  authority_enforce_mode:*` keys today; no feature-flag library
  imported).
- S1264 rollout was "all employees, same day" (Explore 6 verified);
  precedent supports the pattern.

**Alternative 1 rejected — `SystemConfiguration authority_enforce:{employee_handle}` keys.**
Would use runtime DB config instead of frozen dataclass fields.
Rejected because: violates EMPLOYEE_OS_PRIMITIVES.md §4.1 (employee
registry immutability); DB-config toggle is looser governance than
code-review-gated registry edit; introduces per-employee migration
lag.

**Alternative 2 rejected — single `MissionRunnerConfig.enforce_authority_mode`
field (no `AIEmployee` mirror).**
Would put the toggle only on the runtime config. Rejected because:
loses per-employee registry-level default; requires factory sites
to explicitly override for every mission dispatch instead of
inheriting from the employee registry.

**Reversibility.** HIGH. Fields are additive nullable defaults;
removable. Composition rule is one line of code.

### 12.7 D92 — Rollback behavior design (warn ← enforce)

**Recommended lean.** **Symmetric toggle flip: post-graduation
enforce → warn rollback is a Chris-gated registry-level edit +
factory-site kwarg override (SAME mechanism as forward rollout in
D91).**

- No separate rollback code path required.
- Change `AIEmployee.enforce_authority_mode="enforce"` back to
  `"warn"` in `core/employees/jobs.py` registry entry; commit + PR.
- The composition rule (max-strictness in D91) means per-mission
  overrides can dial back before the registry change ships.

**Rationale.**

- Symmetric-toggle rollback matches S1264 warn-mode pattern:
  no separate "rollback flag"; forward and backward flow through
  the same code-review-gated registry edit.
- No S1264 handoff §6 rollback mechanism documented (Explore 6
  verified) — this is a novel documentation deliverable.
- Explicit greppable log at flip time: `[AUTHORITY_ENFORCE_MODE_CHANGED]
  employee=X from=Y to=Z timestamp=... source=<registry|config>`.

**Alternative 1 rejected — auto-halt-on-threshold rollback.**
Would automatically flip enforce → warn if the auto-halt threshold
(D93) fires. Rejected because: violates F5 verifier discipline
(auto-mode-flips add hidden state that graduation reasoning
must track); explicit Chris-gate at every mode transition
preserves auditability.

**Alternative 2 rejected — dedicated rollback beat task.**
Would ship a task that monitors telemetry and reverts on drift.
Rejected because: adds runtime complexity for a scenario that
should be an operator decision, not an automated one; Rigby +
Chris can flip the field manually within minutes if metrics turn.

**Reversibility.** N/A — rollback IS the reversibility mechanism.

### 12.8 D93 — Metrics window + trust threshold + false-positive threshold policy

**Recommended lean.** **5 SystemConfiguration keys (category
`authority_enforce`) with data-sufficiency floor on top of a
21-day window cap (Rigby SIGN cycle 1 Q3 fold — data-sufficiency-
gated alternative promoted from Alternative 3 into the lean).**

| Key | Draft default | Rationale |
|---|---|---|
| `authority_enforce:metrics_window_days` | **21** (cap / default) | S1264 handoff §6 prereq #2 cited "≥14 days clean" — round up to 21 days (3 weeks) to accommodate weekend gaps + arc-close low-activity periods. **This is a CAP, not the promotion trigger** — see `metrics_min_events_per_employee` for the data-sufficiency floor. Given only 5 days / 13 events of warn-mode data at P2 open (Explore 5), a naked days-based threshold would fire on tiny samples. |
| `authority_enforce:metrics_min_events_per_employee` | **50** | **Data-sufficiency floor** (Rigby SIGN cycle 1 fold). Promotion decision requires BOTH `days_elapsed >= metrics_window_days` AND `event_count_per_employee >= 50`. Chosen because 50 mission-fires per employee is roughly 2-3 weeks of steady daily cadence per Explore 5 baseline (2-3 events/day observed) — provides enough sample to compute a stable trust_ratio without over-fitting the earliest days. Chris ratifies the 50 value; alternative floors (20 / 100) are on the table. |
| `authority_enforce:trust_threshold_ratio` | **0.95** | 95% clean telemetry per employee (i.e., ≥95% of `authority_contract_observed` events with zero PROHIBITED-level violations detected via retrospective scan). Draws on S1264 handoff §6 prereq #4 `trust_ratio ≥ 0.75` but tightens to 0.95 given enforcement's higher operational cost vs warn-mode. Only computed AFTER the min-events floor is satisfied per employee. |
| `authority_enforce:false_positive_ceiling` | **0.05** | Maximum 5% false-positive rate over the metrics window. Below this, per-employee enforce graduation is allowed. Only computed AFTER the min-events floor is satisfied. |
| `authority_enforce:auto_halt_threshold` | **0.10** | Auto-halt at 10% block rate (or false-positive rate) sustained over 1 hour. Triggers `authority_enforce_auto_halt` event but does NOT auto-flip mode (per D92 rollback rejection of auto-flip). Halt = alert to Chris + Rigby via HAI. |

**Rationale.**

- Empirical baseline is thin (5 days, 13 events per Explore 5). A
  fixed 21-day window would let promotion decisions fire on
  ~50-100 events total (fewer per employee) — too sparse for a
  stable trust_ratio estimate.
- The **data-sufficiency floor** is the substantive protection: no
  promotion decision fires until BOTH the days-cap AND the
  min-events-per-employee floor are satisfied.
- All 5 keys are `SystemConfiguration` category `authority_enforce`,
  runtime-editable via `platform_config_tool set`; no schema
  migration for tuning.
- Read-only at P2 ship; the retrospective scan consumes them
  post-graduation.

**Alternative 1 rejected — hardcoded thresholds in the scan task.**
Would embed defaults in the beat task Python. Rejected because:
tuning requires code + PR; violates the runtime-tunable operator
principle (`SystemConfiguration` is the canonical runtime-config
surface per PLATFORM_INVENTORY autoblock).

**Alternative 2 rejected — per-employee thresholds.**
Would allow different thresholds per employee. Rejected because:
premature granularity per parent §5.2 anti-scope; can extend to
per-employee post-graduation without breaking global-default.

**Alternative 3 (Rigby Q3 fold) — PROMOTED to recommended lean above.**
The original 4-key P2 draft used a fixed 21-day window without a
data-sufficiency floor. Rigby flagged this as the weakest D-verdict
rationale because Explore 5 verified only 5 days / 13 events of
warn-mode data exist. Rigby's proposed third alternative — "tie
metrics window to S1274 graduation triggers / data sufficiency" —
was promoted into the recommended lean as the
`metrics_min_events_per_employee` floor.

**Reversibility.** HIGH. Keys can be updated at any time via
`platform_config_tool`.

---

## 13. Architecture Maturity

Classification per playbook §12 (5-value scale: EXPERIMENTAL /
PARTIAL / WORKING / STABLE / CANONICAL).

**Authority observation surface — WORKING.** `_emit_authority_contract_event`
+ warn-mode event schema (S1264) fires on every mission; 13
events since 2026-06-30 with 0 malformed contracts; 4 employees
inheriting warn-mode uniformly. Not yet CANONICAL because: no
retention policy shipped (Group 1700 T0/Gate handoff); no
`authority_contract_violated` event schema exists (S1272 prereq
#4); no runtime consumer beyond level_counts accumulator.

**Authority enforcement surface — EXPERIMENTAL** (does not yet
exist). No pre-dispatch gate reads `AuthorityLevel`; no retrospective
scan detects violations; no per-employee `enforce_authority_mode`
field. Under recommended D86 lean, matures to PARTIAL at
scaffolding ship (Option A-adjacent field), then WORKING at
S1274 graduation + `authority_violation_retrospective_scan` beat
task ship.

**Symbol Mapping surface — PARTIAL** (inherited from S1274). Option
E v0 selected but not migrated; 0 of 5 audit models have
`action_class` column (Explore 4). Matures to WORKING at S1274
graduation.

**Actor-role propagation surface — PARTIAL** (P1 S1901 shipped
contract; Layer-ii wiring in T-tier queue). Matures per P1 §19
T-tier queue execution.

**Cross-plane composition surface — PARTIAL** (S1269 shipped
autonomy → budget one-way sync at `governance.py:2273`; other
compositions undefined). Matures at P3 (S1903) ship + T-tier queue
execution.

**Governance-plane freeze surface — WORKING.** `GovernanceState.mode='freeze'`
has 4 dispatch consumers (Explore 3 verified: tasks_spiders.py +
2 signal_aggregation.py + workspace_pipeline_runner.py); consistent
posture; but no unified precedence policy with authority (D88
partial input; P3 finalizes).

**KillSwitch surface — WORKING.** S1272 GAP-7 "write-only"
REFUTED. 6 read sites verified (Explore 3: 4 dispatch-consumer
+ 2 audit). Not CANONICAL because dispatch coverage is partial
across the platform (post-arc T1 R.AUTHORITY.KILLSWITCH-DISPATCH-
EXPANSION if Chris ratifies).

**HAI + OrchestrationApprovalGate — STABLE.** Bridge exists at
`core/models_orchestration.py:397-535` with UUID linkage; auto-approve
gate is 8-condition (7 core + 2 existence); daily throughput
120-163 items/day. Under Option D graduation, adds an
`authority_violation` source_type.

---

## 14. Known Drift

Per playbook §12 verifier-loop discipline; drift is documented, not
silent.

### 14.1 Inherited-in drifts (parent §5.2 → P2)

- **Parent §5.2 cites "F8 constraint: Option E enables only 4 of 12
  modes"** — S1272 §4.3 authoritative table shows **F9** (not F8)
  is the Option E constraint, and Option E enables **5** modes
  (observe-only + warn-mode + degrade-mission-evidence +
  freeze-platform + retrospective-violation-report), not 4. P2
  uses the S1272 §4.3-verified 5-mode count throughout §7 and
  §12.2 D87. Parent scoping drift-correction is inherited into
  this doc and does NOT block; recommend the correction be
  folded at xx99 (S1999) canonical summary §7.3 anchor-update
  recommendation.

### 14.2 Post-Explore verifier-loop corrections

- **S1272 GAP-7 KillSwitch "write-only" REFUTED.** Explore 3
  verified 6 read sites total: 4 dispatch-consumer reads
  (`governance.py:2192` status read, `governance.py:2508` expiry
  gate + auto-deactivate, `intelligence.py:1717` cleanup gate,
  plus one dispatch read counted at `governance.py:2192`) + 2
  audit reads (`intelligence.py:1569-1572` drift report). S1901
  Agent 6 speculated "10+" — actual count 6. Codified in §7.6
  Option F reuse footprint and §13 KillSwitch maturity.
- **HAI auto-approve condition count reconciliation.** S1269 §2.4
  cited **7 conditions**; Explore 6 verified **8 gates total** at
  `human_attention_lifecycle.py:223-296`. Reconciled: 7 core
  business-logic gates + 2 existence checks (system.review_mode
  false + at-least-one-user-with-auto_approve_low_risk-true) = 8
  gates; the 7-count refers to the substantive per-item checks.
  §7.4 Option D and §12.3 D88 use the 8-gate framing with the
  "7 core + 2 existence" caveat.
- **CLAUDE.md 3-employees vs runtime 4-employee-handles drift.**
  CLAUDE.md line 195 lists 3 production employees (Documentation
  Manager (Rigby) + Platform Auditor + Chief of Staff). Explore 2
  saw 4 JobContracts (DOCUMENTATION_MANAGER +
  PLATFORM_AUDIT_JOB + MORNING_BRIEF_JOB + BUG_TRIAGE_JOB).
  Explore 5 warn-mode telemetry has 4 employee_handle values
  firing (rigby + platform_auditor + chief_of_staff +
  bug_triage_specialist). Reconciliation deferred (not P2 scope):
  either a 4th employee (bug_triage_specialist) is missing from
  CLAUDE.md OR MORNING_BRIEF_JOB and BUG_TRIAGE_JOB both run
  under chief_of_staff with impersonation (S1271 F11 violation
  risk). Recommend xx99 (S1999) anchor-update to CLAUDE.md if
  4-employee count is verified.

### 14.3 Drift previously catalogued (P1 S1901 §14 inheritance)

- **S1272 KillSwitch site-count** — P1 flagged 5 (S1272) vs 10+
  (S1901 Agent 6); Explore 3 verified count is 6 (see 14.2).
- **`AgentExecution.owner_agent` migration age** — P1 §20.5
  recorded SPECULATIVE for migration number; broader claim
  Session 843 stands per handoff grep.
- **`_router_heartbeat_loop` role-availability** — P1 §20.4
  deferred; T3 R.AUTHORITY.THREE-ROLE-TEST-COVERAGE consumes.

### 14.4 Drift raised by P2 (new)

- **S1272 §9.5 vs S1274 Symbol Mapping "Option E" labeling
  collision.** S1272 §9 lists Option E as "Multi-layer enforcement";
  S1274 selected "Option E v0" as Symbol Mapping evidence-only.
  Distinct concepts + adjacent labels risk misreading. §7.5 in
  this doc uses "Option E (multi-layer)" vs "Option E v0" as
  disambiguated cross-references. Recommend xx99 anchor-update
  to relabel one of them (e.g., S1272 §9.5 → "Option M
  Multi-layer") or add a top-of-doc note.
- **`views_human_interface.py` line drift.** S1272 §3.1 boundary
  16 references `views_human_interface.py:84-100` for the HAI
  decide endpoint; Explore 1 verified the decide view starts at
  line **154**, not 84 (line 95 is the start of `get()`, not
  decide). §17 Enforcement Binding Points map uses the verified
  line 154. Recommend xx99 anchor-update to S1272 §3.1.

---

## 15. Known Technical Debt

- **`Step.action_classes_invoked` declaration extension** — required
  for Option A/C graduation. Debt because current `Step` dataclass
  has no such field; adding it touches ~200+ step implementations
  across job modules (Agent 6 §Q10 estimate from S1901). Post-arc.
- **`action_class` migration on 5 audit models** — S1274 Option E
  v0 execution; 0 of 5 models have the column today (Explore 4).
  Post-S1274-graduation.
- **`authority_violation_retrospective_scan` beat task** — does
  not exist; new deliverable under Option C-primary. Post-arc.
- **`authority_enforce_gate_service`** — does not exist; new
  deliverable under Option A scaffolding graduation path.
  Post-arc.
- **`AUTHORITY_CONTRACT_VIOLATED` event schema (S1272 prereq #4)** —
  not defined. Under recommended D89 lean, adds when
  retrospective scan ships.
- **CLAUDE.md 3-vs-4-employees drift + 10-vs-9 body systems drift**
  — inherited from Group 1700 xx99 anchor-update PR (unresolved).
- **Retention policy for `authority_contract_observed` OpsRunEvent
  rows** — no dedicated policy; inherits `OpsRunEvent` retention
  which itself is Group 1700 T0/Gate handoff
  (R.OBSERVABILITY.RETENTION-UNIFIED-ADR).
- **§8 timeline table drift** — missing rows for S1605 + S1606 +
  S1699 (Group 1600); inherited from prior arcs.

---

## 16. Boundary Violations

- **Boundary 5 preflight event mode string hardcoded to `"warn"` at
  `mission_runner.py:894`** — will become
  `self.config.enforce_authority_mode` post-D90; not a violation
  today but P2 flags for the graduation-time diff.
- **Boundary 6 step function signature `step.fn(mission)`
  (F6c STRUCTURAL DROP)** — verified permanent gap; not a
  violation, structural per S1271 F6c.
- **KillSwitch model previously flagged as "write-only" (S1272
  GAP-7) — actual state has 4 dispatch consumers.** Not a boundary
  violation but a documentation-vs-runtime drift. See §14.2.
- **Fleet permissive-fallback outcome fidelity (Boundary 19)** —
  inherited P1 §20.4 unresolved; P4 Cat F scope.

---

## 17. Enforcement Binding Points Map

**Section shape (per parent §5.2 + Rigby S1900 SIGN cycle 1 Q4
fold).** Playbook §11.2 §17 Duplicate or Overlapping Systems
becomes the Enforcement Binding Points map — P2's FIRST-CLASS
deliverable. Table shape per parent §5.2:
`(boundary_id, read_site, evaluation_order, other_gate_precedence,
fail_posture, P1_row_ref)` per S1272 §3.1 20-boundary inventory.

**Reading key.**

- **Boundary #** = S1272 §3.1 boundary number.
- **Read site** = current file:line where an enforcement read
  would happen under the recommended Option C-primary + Option A
  scaffolding lean; if no read exists under this lean, marked
  N/A-C+A.
- **Evaluation order** = ordinal position relative to KillSwitch
  (K) + freeze (F) + budget (B) + HAI auto-approve (H) +
  mission governance (M) per D88 partial precedence lean.
  Notation: `K>A>F>B>H` = KillSwitch first, then Authority
  (this boundary), then Freeze, then Budget, then HAI.
- **Other gate precedence** = which planes gate BEFORE authority
  at this boundary (composed with §D88 D-verdict).
- **Fail posture** = fail-open / fail-closed at this boundary
  (per D89 D-verdict fail-open default; per-site overrides noted).
- **P1 row_ref** = S1901 §7.3 Layer-ii per-boundary propagation-
  contract table row citation.

### 17.1 The 20-boundary table

| # | Boundary | Read site (Option C+A lean) | Evaluation order (D88) | Other gate precedence | Fail posture (D89) | P1 row_ref |
|---|---|---|---|---|---|---|
| 1 | HTTP auth middleware | `core/auth_middleware.py:563-681` (33 permission_classes sites; Explore 1) | K>M>A | is_staff / is_reviewer gates apply before A | Fail-open (503 on infra error per S1171 typed-exception rework) | S1901 §7.3 row 1 |
| 2 | ToolDispatcher.execute() entry (AssistantProfile gate) | `core/services/tool_dispatcher.py:687-720` (Explore 1 verified stable) | K>M>A | AssistantProfile.allowed_tools gate applies before A | Fail-open (log-but-not-raise at line 721-722; Explore 1) | S1901 §7.3 row 2 |
| 3 | PA tool handler body | `td_handlers_*.py` per-handler | K>M>A | Handler-specific auth checks apply before A | Fail-open per handler | S1901 §7.3 row 3 |
| 4 | MissionRunner.run() entry (mission startup) | `core/employees/mission_runner.py` (run method) — reads `enforce_authority_mode` toggle | K>M>A | M (mission governance) precedes A | Fail-open (F8 precedent) | S1901 §7.3 row 4 |
| 5 | MissionRunner preflight — warn-mode | `core/employees/mission_runner.py:835-900` (`_emit_authority_contract_event`) | K>M>A | M precedes A; **observation-only per S1264 decree** — no gating | N/A (observation only, no gate) | S1901 §7.3 row 5 |
| 6 | Before each Step.fn (step loop) | `core/employees/mission_runner.py:_run_step` line 904; gate site adjacent to `step.fn(mission)` line 917 | K>M>A>F | M precedes A (config toggle); F precedes further downstream | Fail-open (F8 precedent) | S1901 §7.3 row 6 |
| 7 | Inside Step.fn body (closure) | Per-job step function body | N/A-C+A — F6c STRUCTURAL DROP per S1271 | N/A (closure opaque to runner) | N/A (structural) | S1901 §7.3 row 7 |
| 8 | Celery task dispatch (`.apply_async()` / `.delay()`) | Various dispatch sites | K>M>A | K + M queue routing precede A | Fail-open (per-site TBD; P3 finalizes) | S1901 §7.3 row 8 |
| 9 | Celery task execution (`@shared_task` entry) | `core/tasks*.py` | N/A-C+A — F6a STRUCTURAL DROP per S1271 (request.user lost at process boundary) | K + M precede but authority-side has no principal at process boundary | N/A (structural) | S1901 §7.3 row 9 |
| 10 | Model pre_save / pre_delete signals | Django signal handlers | N/A-C+A — F6c-adjacent STRUCTURAL DROP for async paths per S1901 Rigby Q4 fold | K + M precede; A no-op on async paths | N/A (structural for async) | S1901 §7.3 row 10 |
| 11 | Deliverable status transition | `core/signals/deliverable_status_signals.py:83-100` | K>A>M | K precedes; A reads row-level `Deliverable.user` | Fail-open (log; transition-in-progress can't rollback) | S1901 §7.3 row 11 |
| 12 | DirectMessage creation | `core/models_messaging.py` create sites | K>A | K precedes; A checks sender's authority to send | Fail-open (per S1272 §10 anti-pattern #1: never block model writes) | S1901 §7.3 row 12 |
| 13 | EventBus.publish() | `core/services/event_bus.py:137-189` | K>A | K precedes; publish always succeeds | N/A — observation only (no veto path per S1272 §3.3) | S1901 §7.3 row 13 |
| 14 | LLM call — LLMEnforcer.check_budget INLINE | `core/llm_enforcer.py:200-262` (Explore 1 verified F8 fail-open at :237-238 + :263-264) | K>B>A | K + B precede; A reads task_type-derived action_class candidate | Fail-open (F8 precedent verified; canonical fail-open site) | S1901 §7.3 row 14 |
| 15 | AgentRouter.route() | `core/agent_router.py` route method | K>M>A | K + M precede; A reads agent_name-derived action_class | Fail-open (default; agent-not-found already raises via M) | S1901 §7.3 row 15 |
| 16 | HumanAttentionItem decision | `core/views_human_interface.py:154` (**decide endpoint**; Explore 1 verified line 154, not S1272-cited 84) | K>M>A>H | K + M + auth check on item.user precede; H auto-approve after A | Fail-closed (401/403 on auth fail) | S1901 §7.3 row 16 |
| 17 | Post-mission retrospective audit | `core/employees/status.py:53-251` (`evidence_for_mission`) + new `authority_violation_retrospective_scan` (Chris-gated post-arc T1) | K>M>A>F>B>H (full stack, read-only) | All planes precede; A retrospectively detects | N/A — read-only, no gate | S1901 §7.3 row 17 |
| 18 | WebSocket consumer / channel-layer handler | `core/consumers*.py` (Daphne handlers) | K>M>A | K + M precede; A reads request.user + event type | Fail-open (raise + close connection preferred; canonical fail-open under Option C+A lean) | S1901 §7.3 row 18 |
| 19 | Fleet internal API / service-to-service ingress | `core/services/fleet_auth_drf.py:65-150` | K>M>A | K + M + fleet HMAC precede; A reads `app_slug`-derived executor + sponsor | Fail-open (permissive fallback preserved per Explore 3) | S1901 §7.3 row 19 |
| 20 | Spider run boundary (spider ingestion + governance mode reads) | `core/tasks_spiders.py:381-398` (freeze/safe_mode check) | K>F>A | K + F (freeze) precede; A reads spider_name-derived action_class | Fail-open (returns `{'skipped': True}` on freeze per Explore 3) | S1901 §7.3 row 20 |

### 17.2 Roll-up

Roll-up derived directly from §17.1 table. Each boundary falls into
exactly one posture bucket; total = 20.

- **Fail-open (default posture):** 13 boundaries — 1/2/3/4/6/8/11/
  12/14/15/18/19/20.
- **Fail-closed:** 1 boundary — 16 (HAI decide; auth-check
  precedent per Explore 1 verified user-item ownership at
  `human_interface_service.py:317`).
- **Observation-only / no veto path:** 3 boundaries — 5 (warn-mode
  preflight observation-only per S1264 decree) + 13 (EventBus.publish
  no veto path per S1272 §3.3) + 17 (post-mission retrospective
  read-only).
- **Structural drop (F6a/F6c/F6c-adjacent per S1271 + S1901 §7.4):**
  3 boundaries — 7 (Step.fn closure opaque) + 9 (Celery process
  boundary loses request.user) + 10 (async signal receivers).

**Total: 13 + 1 + 3 + 3 = 20.** ✓

**Boundary 11 rationale caveat (Rigby SIGN cycle 1 Q2 fold).**
Boundary 11 Deliverable status transition is fail-open due to
**rollback infeasibility / workflow continuity** (a transition
already in progress cannot be atomically undone by a late-firing
authority check without corrupting the state machine). This is a
DISTINCT rationale from Boundary 12 DirectMessage creation, which
is fail-open per the **S1272 §10 anti-pattern #1 "never block
model writes"** exemplar (the audit substrate itself must not be
blocked or the whole evidence chain fails). Do NOT generalize the
DM anti-pattern to Boundary 11; the two boundaries share a
posture but not a rationale.

### 17.2.1 Precedence roll-up (from evaluation-order column)

- **KillSwitch precedes at every boundary** (D88 rationale: platform
  operator supersedes any authority policy at every read site).
- **Mission governance (M) precedes Authority at 12 boundaries**
  (1/2/3/4/5/6/8/15/16/17/18/19). Does NOT precede at 11 (row-level
  A>M) + 12/13/14 (no M in evaluation order) + 20 (K>F>A, no M);
  structural boundaries 7/9/10 excluded from the count.
- **Freeze precedes Authority at 2 boundaries** (14 as B>A but freeze-adjacent /
  20 K>F>A). Precedes downstream at Boundary 6 (K>M>A>F).
- **Budget precedes Authority at 2 boundaries** (14 K>B>A + 17
  K>M>A>F>B>H full stack).
- **HAI auto-approve gates after Authority at 2 boundaries** (16
  K>M>A>H + 17 full stack).

### 17.3 Cross-reference to P1 §7.3

Every row cites the corresponding P1 §7.3 per-boundary
propagation-contract row (per parent §5.2 requirement). The
Layer-ii closeable status for each boundary determines whether the
Option A/B/D/E graduation path can wire the enforcement gate
without a boundary contract change:

- **Layer-ii closeable (14 boundaries):** 1/2/3/4/5/11/12/13/14/15/
  16/17/18/19/20. Enforcement gate wire-up post-graduation is
  straightforward.
- **Layer-ii closeable partially (Boundary 8):** HTTP-sourced Celery
  dispatch sites closeable; beat sites remain structural
  DEFAULT-CANONICAL.
- **NOT Layer-ii closeable (5 boundaries):** 6/7/9/10 — F6c and
  F6c-adjacent STRUCTURAL DROP; require broader Step / Celery
  contract change (post-arc T-slot execution).

### 17.4 What §17 does NOT do

- **Does not finalize cross-plane precedence.** P3 (S1903) completes
  the 8-question composition policy per parent §5.3. §17 partial
  precedence (D88 lean) is P3 input, not P3 output.
- **Does not choose per-boundary fail-open/fail-closed exceptions.**
  D89 fail-open default is applied at every boundary except
  Boundary 16 (auth-check precedent); per-site graduation
  posture-tuning is post-arc T1.
- **Does not enumerate boundary-specific action_class semantics.**
  S1274 §10.3.1 graduation triggers govern; §17 flags which
  boundaries would consume action_class post-migration.

---

## 18. Ownership Gaps

- **`enforce_authority_mode` field on both dataclasses** — under D91
  lean, ownership sits with `core/employees/jobs.py` (registry
  factory sites) + `core/employees/mission_runner.py` (config
  dataclass). No cross-domain ownership required at ship.
- **`authority_violation_retrospective_scan` beat task** — ownership
  TBD; recommend `core/employees/` module home to keep the
  authority + Employee OS surfaces co-located. Post-arc T1.
- **`SystemConfiguration authority_enforce:*` keys** — Chris-owned
  via admin surface. Read by the scan task + gate service.
- **`AUTHORITY_CONTRACT_VIOLATED` event label + schema** — belongs
  with the `AUTHORITY_CONTRACT_OBSERVED_LABEL` in
  `core/employees/mission_runner.py` module scope; declared at
  scan-task-ship-time.
- **KillSwitch dispatch expansion (Explore 3 §14.2 correction)** —
  the 6 read sites are not authority-domain-owned; if authority
  enforcement adds a KillSwitch read at Boundary 6 or Boundary 2
  under Option A/B graduation, ownership boundary between authority
  and ops_autopilot must be documented (post-arc).

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows.
Feeds the xx99 §8 T0/Gate + T1 + T2 + T3 tiered queue. P1 §19
tier list inherited + P2 additions.

### 19.1 T0 / Gate — pre-P3 blockers

- **R.AUTHORITY.ENFORCEMENT-BINDING-POINTS-MAP** (P1 T0/Gate) —
  **CONSUMED at S1902 close** per §17. Inherit resolved.
- **R.AUTHORITY.CROSS-PLANE-PRECEDENCE-POLICY** — P3 Cat C
  completes; P2 §12.3 D88 provides partial input scope.

### 19.2 T1 — critical for correctness

- **R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS** (P2 D90/D91 ship-scope)
  — add `enforce_authority_mode: str = "warn"` to both
  `MissionRunnerConfig` and `AIEmployee` dataclasses. Backwards-
  compatible. Post-arc.
- **R.AUTHORITY.VIOLATION-EVENT-SCHEMA** (P2 §D89 dependency) —
  define `AUTHORITY_CONTRACT_VIOLATED` label + detail dict shape
  (schema_version, action_class, level_expected, employee_handle,
  executor_actor, sponsor_actor, principal_user_id,
  enforcement_mode_at_time). Extension of S1264 warn-mode schema
  discipline.
- **R.AUTHORITY.RETROSPECTIVE-SCAN-TASK** (P2 §12.4 D89 ship-scope
  under Option C-primary) — new Celery beat task
  `authority_violation_retrospective_scan` reads observed events
  + eventual `action_class` + actor columns; emits violation events.
- **R.AUTHORITY.OPTION-E-MIGRATION-TRIGGER** (P2 recommends
  S1274 §10.3.1 trigger firing observation task) — new beat task
  reads warn-mode telemetry; when triggers fire (Tier-0 hazard
  observed / PROHIBITED-level violation rate >0 per 14d window /
  NULL rate >30% after Phase 4 / 90d elapsed since Phase 5),
  emit `symbol_mapping_graduation_trigger_fired` event + create
  HAI item for Chris.
- **P1-inherited T1 items:** R.AUTHORITY.ACTOR-KWARGS-CELERY +
  R.AUTHORITY.ACTOR-STEP-CONTEXT + R.AUTHORITY.EVENT-SCHEMA-
  EXTENSION + R.AUTHORITY.OPSRUN-ACTOR-COLUMNS (P1 §19.2 inherited
  as-is; no changes at P2).

### 19.3 T2 — important for graduation

- **R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION** (P2 addition,
  post-verifier-loop of GAP-7 correction) — the 4 existing
  dispatch-consumer reads verified at Explore 3 do NOT cover the
  full 6-target KillSwitch scope (scheduler / queue / agent_family
  / publishing / outbound / deploys per Explore 3 model definition).
  Expand dispatch reads to cover authority-adjacent surfaces
  post-graduation. Ownership: ops_autopilot module boundary.
- **R.AUTHORITY.STEP-ACTION-DECLARATION** (Option A graduation
  scope) — extend `Step` dataclass with `action_classes_invoked:
  tuple[str, ...] = ()` field; touches ~200 step implementations.
- **P1-inherited T2 items:** R.AUTHORITY.DELEGATION-CHAIN-MODEL +
  R.AUTHORITY.RUNS-AS-USERNAME-VERIFIED-AT-STARTUP +
  R.AUTHORITY.SPONSOR-ACTOR-CANONICAL-WRITER-POLICY.

### 19.4 T3 — nice-to-have follow-on

- **R.AUTHORITY.PER-LEVEL-BOUNDARY-BINDING** — under Option E
  (multi-layer) reconsideration post-graduation, design the
  per-level per-boundary binding table (which boundary enforces
  which level).
- **R.AUTHORITY.CLAUDE-MD-EMPLOYEE-COUNT-ANCHOR-UPDATE** (P2
  addition per §14.2) — reconcile CLAUDE.md 3-employee claim vs
  runtime 4-employee-handle observation.
- **P1-inherited T3 items:** R.AUTHORITY.MGMT-CMD-ACTOR-CONVENTION +
  R.AUTHORITY.DISCORD-USER-LINKAGE + R.AUTHORITY.FLEET-FALLBACK-
  ROLE-STAMP + R.AUTHORITY.THREE-ROLE-TEST-COVERAGE.

### 19.5 Cross-arc T-slot handoffs

- **R.HAI.LEARNING-PLANE-CONTRACT-ADR** (Group 1300 + Group 1800
  T0/Gate) — P3 authority read-side interacts with learning plane;
  cross-arc dependency inherited from P1 §19.5.
- **R.OBSERVABILITY.RETENTION-UNIFIED-ADR** (Group 1700 T0/Gate) —
  authority-audit rows inherit retention posture; recommend
  authority-specific retention section added when the ADR bundle
  lands.
- **R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES** (Group 1800 T0/Gate,
  deferred to Group 2000+) — Boundary 13 EventBus.publish wiring
  is second candidate feed-point; inherited from P1 §19.5.

---

## 20. Appendix

### 20.1 Files inspected

**Runtime code** (parent-verifier direct reads):

- `core/llm_enforcer.py:195-265` (F8 fail-open verification;
  Explore 1)
- `core/employees/mission_runner.py:265, 528-589, 835-900, 904-917`
  (schema-version constant, MissionRunnerConfig fields, warn-mode
  emission, step boundary; Explore 2)
- `core/employees/jobs.py:41-51, 73-91, 94-162, 187, 415, 691,
  1005` (AuthorityLevel enum, AIEmployee dataclass, JobContract
  dataclass, 4 factory sites; Explore 2)
- `core/services/tool_dispatcher.py:685-720` (Explore 1)
- `core/services/pa_tool_schemas.py` (schema-count reference;
  PLATFORM_INVENTORY autoblock)
- `core/auth_middleware.py:563-681` (33 permission_classes; Explore 1)
- `core/views_human_interface.py:154` (decide endpoint line-drift
  verified; Explore 1)
- `core/services/human_interface_service.py:317` (user-item
  ownership; Explore 1)
- `core/services/human_attention_lifecycle.py:223-296` (8-condition
  auto-approve gate; Explore 6)
- `core/models_governance.py:17-114, 116-189` (GovernanceState +
  KillSwitch model definitions; Explore 3)
- `core/services/ops_autopilot/governance.py:2192, 2273, 2347,
  2370, 2508` (KillSwitch dispatch + autonomy-budget sync;
  Explore 3)
- `core/services/ops_autopilot/intelligence.py:1569-1572,
  1717-1723` (KillSwitch reads; Explore 3)
- `core/services/ops_autopilot/budget.py:375, 381` (budget flag
  reads/writes; Explore 3)
- `core/tasks_spiders.py:381-398` (freeze/safe_mode read; S1272
  Boundary 20 verified)
- `core/services/signal_aggregation_service.py:225, 969` (freeze
  consumers; Explore 3)
- `core/services/workspace_pipeline_runner.py:44` (freeze
  consumer; Explore 3)
- `core/services/event_bus.py:137-189` (S1272 Boundary 13)
- `core/services/fleet_auth_drf.py:65-150` (Boundary 19; Explore 3
  verified)
- `core/models_orchestration.py:397-535` (OrchestrationApprovalGate;
  Explore 6)
- `core/models_ops_runs.py:91-118` (OpsRunEvent; Explore 4 —
  no action_class field)
- `core/models_tool_calls.py:57-60` (ToolCallRecord; Explore 4 —
  no action_class field)
- `core/models_llm_telemetry.py:62-65` (LLMCallEvent; Explore 4)
- `core/models_celery_telemetry.py:41-47` (CeleryTaskEvent;
  Explore 4)
- `core/models_unified_system.py:894-927` (AgentExecution;
  Explore 4)
- `core/models/system/models.py:9-80` (SystemConfiguration;
  Explore 6)
- `core/models_human_attention.py` (HumanAttentionItem; Explore 6)
- `core/services/td_handlers_employee.py:77` (`AuthorityLevel`
  JSON coerce; Explore 2)
- `core/agent_router.py` (S1272 Boundary 15 reference)

**Runtime data** (Django ORM queries; Explore 5 verifier):

- `OpsRunEvent.objects.filter(label='authority_contract_observed').count()`
  → 13
- `OpsRunEvent.objects.filter(label='authority_contract_observed').order_by('created_at').first()`
  → 2026-06-30 17:06:27 UTC (5 days prior to S1902 open)
- Per-employee `authority_contract_observed` counts: rigby (3),
  platform_auditor (1), chief_of_staff (4), bug_triage_specialist (5)
- Modal `authority_level_counts`: PROHIBITED ~9, EXECUTE ~5,
  OBSERVE ~4, RECOMMEND ~2
- `HumanAttentionItem.objects.count()` → 3594 (22-day window)
- HAI daily rate: 163/day all-time; 120/day last 30 days
- Top HAI source_type: spider_pipeline 93.7% (3368/3594)

### 20.2 Docs inspected

- `docs/research/authority_enforcement_design_space.md` (S1272) —
  §2.3, §3.1, §4, §7.5, §9, §10, §11, §14.3, §14.5
- `docs/research/symbol_mapping_option_selection_design.md` (S1274) —
  §10.3.1 graduation triggers + Option E v0 selection
- `docs/research/actor_identity_attribution_architecture.md` (S1271) —
  §8.5, F6, F11
- `docs/research/governance_authority_evolution.md` (S1269) —
  §2.4 auto-approve gate condition count reference; §7.5 8
  composition questions
- `docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md`
  (S1900) — §5.2 P2 spec + D81-D85 + O1/O2 + Rigby SIGN cycle 1 folds
- `docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md`
  (S1901) — §7.3 20-row per-boundary propagation-contract table +
  §7.4 drop-boundary register + §7.6 Option E parallel-safety +
  §19 T-tier queue
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §13 + §14 +
  §11.3 §10 meta-methodology + §16 commit policy
- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` §5.1 + §8.1
  RESEARCH contract
- `docs/EMPLOYEE_OS_PRIMITIVES.md` §4 anti-duplication matrix
- `docs/PLATFORM_INVENTORY.md` autoblock (frontier counts for
  reference)
- `CLAUDE.md` line 195 (3-vs-4 employee drift discovery)
- `docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md` (S1264
  rollout precedent)
- `MEMORY.md` (feedback_verifier_loop_pattern +
  feedback_test_real_db_for_queryset_semantics +
  feedback_rigby_sign_worker_instability_recovery +
  feedback_llm_autofills_boolean_params_with_false)

### 20.3 Grep patterns used

- `AuthorityLevel\.` — 2 production consumer sites verified (Explore 2)
- `\.EXECUTE\.value` / `\.OBSERVE\.value` / `\.RECOMMEND\.value` /
  `\.PROHIBITED\.value` — production-consumer inventory
- `enforce_authority` / `enforce_mode` / `authority_mode` —
  0 field matches on MissionRunnerConfig / AIEmployee / JobContract
  (Explore 2)
- `action_class` — 0 field matches on 5 audit models (Explore 4)
- `AUTHORITY_CONTRACT_OBSERVED_LABEL` — definition + 1 writer + 5
  test consumers (Explore 4)
- `AUTHORITY_CONTRACT_VIOLATED` / `authority_contract_violated` —
  0 hits (Explore 5)
- `_AuthorityContractMalformedError` — 0 fires all-time (Explore 5)
- `except Exception:\s*pass` — 3 fail-open sites total across
  llm_enforcer + tool_dispatcher + mission_runner (2 + 1 + 0;
  Explore 1)
- `KillSwitch\.objects\.` — 8 sites total (2 write + 6 read;
  Explore 3)
- `budget_freeze_active` — 6 sites (Explore 3)
- `mode='freeze'` / `mode=='freeze'` / `mode in ('freeze'` — 4
  dispatch consumers verified (Explore 3)
- `HumanAttentionItem.objects.` — ORM query for daily rate
  (Explore 6)
- `permission_classes = ` — 33 declarations (Explore 1)

### 20.4 Unresolved unknowns

- **CLAUDE.md 3-employees vs runtime 4-employee-handles drift.**
  Whether `bug_triage_specialist` is a 4th `AIEmployee` registry
  entry or Chief of Staff impersonating (S1271 F11 risk) —
  deferred to §14.2 drift entry + xx99 anchor-update recommendation.
- **`_router_heartbeat_loop` role-availability** — inherited from
  P1 §20.4 unresolved; T3 R.AUTHORITY.THREE-ROLE-TEST-COVERAGE
  consumes.
- **Discord-user linkage failure semantics under Option D
  graduation** — P3 cross-plane composition question 8 scope;
  P2 does not resolve.
- **Retention policy for authority-audit event volume** — inherits
  Group 1700 T0/Gate ADR outcome; no P2 verdict.
- **Explore 4 note on `AgentExecution` model deprecation candidacy**
  — production usage state unclear; S1901 P1 §14 known drift +
  P2 §14 additional flag; requires xx99 anchor-update if the
  model is deprecated pre-graduation.

### 20.5 Verifier-loop corrections (playbook §14 MC-1 CODIFICATION-CONFIRMED)

**Pre-Explore spot checks (5 sites):**

1. `core/llm_enforcer.py:237-238` fail-open — VERIFIED at
   pre-Explore.
2. `core/employees/mission_runner.py:835-900`
   `_emit_authority_contract_event` — VERIFIED.
3. `core/employees/mission_runner.py:917` `step.fn(mission)` call
   site — VERIFIED (F6c STRUCTURAL DROP boundary).
4. `enforce_authority` / `action_class` grep — VERIFIED 2 files
   match, both `mission_runner.py` + `jobs.py` (jobs.py match =
   `authority` dict field on JobContract; not `enforce_authority`
   field per Explore 2).
5. Parent §5.2 F8-vs-F9 constraint drift — CAUGHT at pre-Explore;
   inherited into §14.1.

**Post-Explore folds:**

- **Explore 1 fail-open count.** Explore 1 reported 3 sites total
  (2 in llm_enforcer + 1 in tool_dispatcher log-but-not-raise);
  parent-verifier accepted with the tool_dispatcher line 721-722
  clarification (log + swallow ≠ pass silently — actually
  `logger.debug(...)` per Explore 1 text). Verified sufficient.
- **Explore 1 HAI decide endpoint line drift.** Explore 1 verified
  decide endpoint starts at line 154, NOT S1272 §3.1's cited line
  84. Landed as §14.4 drift + §17 Boundary 16 read-site correction.
- **Explore 2 JobContract instance count.** Reported 4 concrete
  instances (DOCUMENTATION_MANAGER at :187 + PLATFORM_AUDIT_JOB at
  :415 + MORNING_BRIEF_JOB at :691 + BUG_TRIAGE_JOB at :1005). Parent
  verifier accepted; landed as §14.2 drift entry.
- **Explore 3 KillSwitch dispatch-consumer count.** Verified 4
  dispatch + 2 audit = 6 total reads. Landed as §14.2 drift +
  §7.6 Option F reuse footprint + §13 KillSwitch maturity + §17
  Boundary evaluation-order (KillSwitch highest precedence
  everywhere).
- **Explore 5 empirical baseline verification.** 13 events over
  5 days confirmed. Used in §7.3 Option C reuse footprint + §13
  authority-observation-surface maturity + §12.8 D93 threshold
  rationale.
- **Explore 6 HAI condition-count.** 8 gates total; 7 core
  business-logic + 2 existence checks. Landed as §14.2 drift +
  §7.4 Option D reuse footprint + §12.3 D88 partial precedence.

### 20.6 Conflicts between sources

- **Option E label collision** (S1272 §9.5 Multi-layer vs S1274
  Symbol Mapping Option E v0 Evidence-only) — flagged in §14.4;
  disambiguated in §7.5 by using "Option E (multi-layer)" vs
  "Option E v0" cross-references.
- **HAI auto-approve condition count** — S1269 §2.4 says 7,
  Explore 6 verified 8. Reconciled in §14.2.
- **KillSwitch site count** — S1272 GAP-7 said write-only, S1901
  Agent 6 said 10+, Explore 3 verified 6. Reconciled in §14.2.
- **Parent §5.2 Option E constraint citation** — F8 (parent) vs F9
  (S1272 authoritative). Reconciled in §14.1.

### 20.7 Rigby SIGN fold notes

**SIGN cycle 1 — 2026-07-04 — SIGN-with-edits at High confidence.**
Arc pin `pa-2bd1613ce2bd4a9c`. **D48 34th arm turn 1 CLEAN per
single-batch-4-question criterion → 29-consecutive-fully-clean-arms
sub-pattern EXTENDED at S1902 SIGN cycle 1** (MC-2 CODIFICATION-
CONFIRMED milestone extended 28 → 29 consecutive).

**Three folds landed pre-commit:**

1. **Q1 fold — §7.7 language de-endorsement.** Original table used
   "PRIMARY" / "Rejected at P2" / "Partial (scaffolding only)" as
   the "Recommended lean at P2" column labels. Rigby flagged that
   despite the §7 header neutrality guardrail restatement + the
   consistent "mechanically compatible with S1274 Option E v0
   today" qualifier throughout §7.1-§7.6, the summary column
   still read as pre-Chris value judgment rather than mechanical-
   state classification. Folded: column header changed to
   "Mechanical-state classification at P2 (Chris-gated in §12)";
   labels changed to "Recommended lean (Option-E-compatible
   shippable-now)" / "Not shippable-now under Option E v0; parked
   (re-eval at graduation)" / "Scaffolding-only (no enforcement
   until graduation)". Neutrality preserved in §7; the actual
   endorsement carries via §12 D86 Chris-gate.

2. **Q2 fold — §17.2 roll-up recompute + Boundary 11 rationale
   caveat.** Original §17.2 prose used "15 fail-open" + tangled
   "actually 5 sites → 21 → adjust to 20" reasoning that was
   internally inconsistent. Rigby recomputed directly from §17.1
   table: **13 fail-open + 1 fail-closed + 3 observation-only +
   3 structural-drop = 20** with each bucket enumerated by
   boundary number. Fold #1 landed. Fold #2: added the caveat that
   Boundary 11 (Deliverable status transition) is fail-open due to
   **rollback infeasibility / workflow continuity** — a DISTINCT
   rationale from Boundary 12 (DirectMessage creation) which is
   the canonical S1272 §10 anti-pattern #1 "never block model
   writes" exemplar. Also added §17.2.1 precedence roll-up for
   clarity (KillSwitch every boundary, M at 12, F at 2, B at 2, H
   at 2).

3. **Q3 fold — §12.8 D93 data-sufficiency-gated alternative
   promoted into the lean.** Original D93 was a 4-key set with a
   fixed 21-day metrics window. Rigby flagged this as the weakest
   D-verdict rationale because Explore 5 verified only 5 days /
   13 events of warn-mode data exist. Fold: promoted Rigby's
   proposed third alternative — "tie metrics window to
   data sufficiency (min_events_per_employee + min_days)" — into
   the recommended lean. Added a fifth SystemConfiguration key
   `authority_enforce:metrics_min_events_per_employee=50` as
   the substantive data-sufficiency floor. Promotion decision now
   requires BOTH the days-cap AND the min-events floor per
   employee. Alternative 3 explicitly documented as promoted.

**Q4 fold — not adopted (info-carrying only).** Rigby's response
on Q4 was truncated at output-length limit; the visible portion
confirmed the Option E label collision (S1272 §9.5 Multi-layer vs
S1274 Symbol Mapping v0 Evidence-only) is "genuinely load-bearing".
§14.4 already flags this + recommends xx99 anchor-update rename
(e.g., S1272 §9.5 → "Option M Multi-layer"). No new §14 entries
required.

**Chris D-gate ratification event — 2026-07-04.** Following Rigby
SIGN cycle 1 SIGN-with-edits + 3 folds landed pre-commit, the
D86-D93 verdict card was routed to Chris on arc pin
`pa-2bd1613ce2bd4a9c` with 8 slots + response menu (agree-all OR
line-item override). Chris responded **"agree all"** — ratifying
all 8 recommended leans as-is with no line-item overrides. §12
now records the D86-D93 leans as Chris-locked P2 design decisions.

**SIGN cycle 2 — SKIPPED as unnecessary.** Because Chris ratified
via "agree all" without line-item revision, no post-ratification
rationale reinterpretation risk exists between Rigby's cycle 1
folds and Chris's ratification — the ratified state matches the
cycle 1 post-fold state exactly. Cycle 2 was scoped in the P2
plan as a defensive check against interpretation drift when
Chris picks alternatives; skipped as N/A given the agree-all path.

**Verdict.** SIGN-with-edits at High confidence with 3 folds
landed pre-commit; Chris D-gate agree-all ratification at
2026-07-04 post-SIGN. Doc status: post-D-gate ratified; commit-gate
pending Chris commit approval.

### 20.8 Frontmatter provenance

- `status: draft` pending Chris commit-gate + Rigby SIGN cycle 1
  + Chris D-gate multi-verdict D8N series.
- `session: 1902`, `child_slot: P2_cat_b`, `domain_slug:
  authority_enforcement`, `research_group: 1900`,
  `mission_type: design_decision`.
- Anchor v-bumps deferred to xx99 canonical summary per playbook
  §11.3 §7 discipline.

---
