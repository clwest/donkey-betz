---
title: "Symbol Mapping Option Selection Design — Research + Design Preparation (Chris-gated decision)"
status: draft
session: 1274
date: 2026-07-01
mission_type: design_preparation
authority: |
  Research + design-preparation. This mission narrows the Symbol
  Mapping design space (5 options from S1270 §5) and produces an
  evidence-based recommendation. The recommendation is NOT an
  implementation greenlight — Chris gates the actual selection.

  What this mission MAY do:
  - inventory + verify existing runtime symbol systems
  - deep-evaluate each of the 5 options along multiple axes
  - construct a comparative matrix
  - recommend a first move + end-state IF evidence supports it
  - explicitly say "no decision yet" IF evidence does NOT support one
  - route to Rigby for pressure-test SIGN review
  - fold SIGN-with-edits feedback

  What this mission MAY NOT do:
  - implement Symbol Mapping
  - modify runtime code / models / migrations
  - change MissionRunner / JobContract / tool dispatch behavior
  - create enforcement logic
  - choose an implementation without Chris gate

  Symbol Mapping is the S1272 §11 critical-path prereq. The
  recommendation here is the input to Chris's design decision,
  not a substitute for it. Actor role vocabulary from S1271 §8.5
  (executor_actor / sponsor_actor / principal_user) is preserved
  throughout — NEVER collapsed.
companion_docs:
  - docs/research/symbol_mapping_architecture.md
  - docs/research/actor_identity_attribution_architecture.md
  - docs/research/authority_enforcement_design_space.md
  - docs/research/governance_authority_evolution.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md
verifier_loop: |
  Five parallel Explore sub-agents produced evidence reports:
  (1) runtime symbol inventory across 24 systems with reuse
      potential ranked per option; verified 4 count drifts from
      S1270 (REMOVED_TOOL_ALIASES 12→13, GATEWAY_TOOLS 23→22,
      new registries PublishIntent + DirectMessage.thread_type +
      OpsRun.run_kind added);
  (2) coverage × reuse analysis producing 100-cell (5 options ×
      20 boundaries) matrix — Option A: 1 YES / 7 PARTIAL / 12
      NO; B: 2/6/12; C: 5/7/8; D: 11/7/1 (widest); E: 2/4/14;
  (3) drift risk analysis ranking A/B/C at VERY HIGH, D at HIGH,
      E at MEDIUM; test coverage cost per drift pattern; detection
      latency spread from immediate to 7-day Bug Triage cycle;
  (4) actor compatibility + enforcement readiness — Options A-D
      all HIGH cost for sponsor_actor propagation (F6-a universal);
      E is only option that mechanically carries all 3 roles IF
      audit models extended; E enables 5 of 12 modes vs. all 12
      for A/B/C/D with actor work;
  (5) failure modes + rollout strategy + minimum viable event
      shape covering S1272 §11 15-prereq DAG.

  Load-bearing structural claims already spot-verified in S1272
  drafting (llm_enforcer.py:200-221 fail-open; HAI auto-approve
  at human_attention_lifecycle.py:223; KillSwitch dispatch
  consumers absent; MissionRunner._emit_authority_contract_event
  at 835-900; AuthorityLevel enum consumer count = 1). No
  re-verification needed for this mission.

  Independent SIGN review by Rigby complete (S1274 PA conversation
  pa-cbcc410b32714f60): **SIGN-with-edits**. Rigby overall
  confidence: Medium. Rigby recommendation: **Modify** — agrees
  with Option E as v0 subject to 4 must-fix tightenings + several
  refinements. All must-fix folded:
  (1) §8.8 whole-platform generalization claim tightened —
      "STRONG once producers exist; v0 coverage remains narrow
      (2/4/14); Fleet/WebSocket/Spider excluded until instrumented"
      (was overstated as "STRONG" absolute).
  (2) §10.3.1 catastrophic-action graduation guardrail added —
      4 telemetry triggers force Chris decision within 30 days:
      Tier-0 hazard observed ≥1 time; PROHIBITED-level violation
      per employee per 14-day window; NULL rate >30% after Phase
      4; ≥90 days elapsed since Phase 5. Prevents "E-forever cope."
  (3) §12.1 non-NULL misclassification drift pattern added —
      sample-based truthing review + cross-source consistency +
      golden-flow tests. Explicitly higher-risk than producer
      omission (NULL count dashboards won't catch this class).
  (4) §11 employee_handle vs. executor_actor distinction added —
      employee_handle is Employee OS identity (NULL for
      non-mission actions); executor_actor is generalized runtime
      executor (may equal employee_handle, may be
      WorkerAgentName under delegation per S1271 F4). Do NOT
      collapse.
  Refinements folded: §8.7 smallest v0 reframed as "audit-model
  extensions (minimum set) + 3-5 highest-leverage producer sites,"
  not "5 migrations + 15-20 sites immediately."
  Rigby SIGN-clean on: risk posture + reversibility framing
  (strongest argument); actor role separation structural work;
  §14 anti-patterns; §16 next-mission recommendation
  (Symbol Mapping Event Schema Design). Options A/B/D softened
  from "tertiary forever" to "deferred pending evidence; high
  complexity / high coordination." Optional additions
  ("What E cannot ever do" box, graduation ladder diagram)
  deferred — §10.3 + §10.3.1 + §13 phase progression already
  cover the material.
owner: claude (drafted S1274) + rigby (independent pressure-test SIGN review, S1274)
---

# Symbol Mapping Option Selection Design

> **What this is.** The design-preparation mission that follows
> S1272 Authority Enforcement Design Space. Where S1272
> enumerated 6 enforcement design options neutrally, this doc
> narrows the *upstream* Symbol Mapping choice (the 5 options
> from S1270 §5) and produces an **evidence-based
> recommendation** for Chris's design gate. The recommendation
> is a starting point for Chris, not a substitute for his
> decision.
>
> **What this is not.** An implementation plan. A migration
> spec. A PR sketch. A Chris-final-decision. Every option
> below can still be chosen; the recommendation identifies the
> *smallest reversible first move* the evidence supports, not
> the *only defensible path*. The 3 actor roles are kept
> separate throughout (S1271 F11 discipline preserved).

---

## 1. Executive Summary

### The recommendation

**Recommended first move (v0):** **Option E — Evidence-only
mapping** as the smallest reversible v0. Extend 5 audit models
(`ToolCallRecord`, `OpsRunEvent`, `LLMCallEvent`,
`CeleryTaskEvent`, `AgentExecution`) with an optional
`action_class` field + all three actor role fields
(`executor_actor`, `sponsor_actor`, `principal_user`).
Instrument producers to populate these fields when known. Emit
observation events; **never block**. Consume via a new Bug
Triage-adjacent aggregation for retrospective violation reports.

**Recommended end-state (5-10 years out, Chris-gated later):**
Layered evolution — Option E foundation + Option B (tool schema
action_class attribute) for pre-dispatch tool-mediated
enforcement + Option A (step declaration) for mission-scoped
enforcement + Option D (central registry) reserved for
composite predicates only if per-tool + per-step becomes
insufficient. **Options C and D as standalone starting points
are rejected** per §1.3 below.

**Explicit non-recommendation:** *No option* is presented as
"the answer." The evidence supports E as the safest v0 first
move. It does *not* support E as the end-state. Chris chooses
whether to commit to a layered evolution or stop at pure
evidence-only.

### The recommendation in one sentence

**Ship the observation surface first (Option E), collect ≥14
days of clean warn-mode telemetry per S1264 prereq #2 on all 4
employees, then decide the enforcement surface (Option A / B /
C / D) with real data instead of speculation.**

### Why E as first move (evidence, not preference)

Per the five sub-agent evidence bundles:

1. **Lowest drift risk (Agent 3 MEDIUM vs. A/B/C VERY HIGH; D
   HIGH).** Evidence is immutable once written; drift is
   producer-omission (data quality issue, detectable via NULL
   counts), not silent behavior mismatch.

2. **Only option that mechanically carries all 3 actor roles
   end-to-end (Agent 4).** Audit rows can carry
   `executor_actor` + `sponsor_actor` + `principal_user` as
   separate fields; the other 4 options all lose at least one
   role at S1271 F6 drop boundaries and require HIGH-cost
   propagation work outside their scope.

3. **Highest reversibility (S1272 F7 taxonomy).** Purely
   additive schema. Rollback = remove producer calls + revert
   migration. No blocked missions to unwind.

4. **Preserves current fail-safe posture (S1264 warn-mode
   invariant).** Never blocks. Aligns with `mission_runner.py:895-899`
   in-code assertion that enforcement requires future symbol
   mapping — evidence-only *is* that mapping in its safest
   form.

5. **Compatible with every downstream option (Agent 4 §F).**
   Options A/B/C/D can layer on top of E. E's audit rows
   become the safety net that catches predicate misses (D),
   tool schema drift (B), step declaration drift (A), and
   hybrid reconciliation gaps (C). E as v0 does not close
   *any* downstream door.

6. **Directly unblocks S1272 §11 prereqs #3, #4, #7, #8, #9,
   #10, #11, #12, #13** (Evidence Event Schema, Violation
   Event Schema, Human Review Path, Test Coverage, Dry-Run
   Mode, Per-Employee Opt-In, Metrics Window, Trust Threshold,
   False-Positive Threshold). Options A/B/C/D unblock the same
   prereqs but *also* introduce the pre-dispatch failure
   surface that those prereqs are designed to gate. E unblocks
   without the risk.

7. **Ships fastest per Agent 5 rollout analysis.** Phases 1-3
   (inventory → observe-only → warn-mode dashboards) all fit
   inside E without decision surface change. Phase 4
   (per-employee dry run) reuses existing S1264 per-employee
   contract opt-in pattern.

### Why NOT choose A / B / C / D as first move

Per Agent 3 drift risk analysis:

- **Options A / B / C are VERY HIGH drift risk** at v0. Every
  step declaration or tool schema annotation is a maintenance
  burden that grows with every step-body or handler-body
  refactor. Detection latency up to 7 days (Bug Triage cycle).
  Test coverage cost is scattered across 17 steps + ~200 tool
  actions.

- **Option D (central registry)** is HIGH risk *and* HIGH
  authorship burden. Predicates are code (fragile), context
  shape is UNKNOWN (S1270 §5.4), and the registry becomes a
  single point of failure. Agent 4: "S1272 §14.3 recommends
  pairing D with Option E (evidence layer as safety net to
  catch predicate misses)" — this alone suggests D as
  standalone v0 is wrong.

- **Any pre-dispatch option (A/B/C/D) as v0** carries the
  fail-open vs. fail-closed decision (S1272 F8), the actor
  role propagation prereq (S1271 F6 drop boundaries — universal
  HIGH cost), and the false-positive threshold prereq (S1272
  §11 prereq #13). Deferring all three to a later phase after
  evidence-first is strictly safer.

### Why E is not the end-state

- **E enables only 5 of 12 modes** (Agent 4: observe-only,
  warn-mode, degrade-mission-evidence, retrospective-violation-
  report, freeze-platform). All 7 pre-dispatch modes
  (hard-block, soft-fail, require-approval, defer, pause-employee,
  freeze-tool, freeze-queue) are disabled.

- **E cannot prevent catastrophic actions in real time.** Per
  S1272 §10 Tier-0 hazards, some anti-patterns (e.g.,
  destructive model writes) benefit from pre-dispatch
  enforcement. E detects; it does not prevent.

- **E's coverage of the 20 boundaries is narrow (2 YES / 4
  PARTIAL / 14 NO per Agent 2).** Broad enforcement requires
  layering.

### Options explicitly rejected

- **Option C (Hybrid A+B) as standalone v0** — rejected.
  Doubles maintenance surface (Agent 3: "compounded VERY HIGH
  drift risk"). Precedence ambiguity unresolved per S1270 §5.3.
  Ships more code than any other option's v0. If both A+B are
  eventually shipped, they should ship sequentially (A first
  or B first), not together in a hybrid coupled release.

### Options deferred (not rejected)

- **Options A, B, D** as end-state layers. Each is a
  defensible next step *after* E ships and telemetry proves
  the design assumptions. This mission does not choose which
  of the three; Chris does that after ≥14 days of E telemetry
  (S1264 prereq #2 pattern).

### Confidence in the recommendation

**Medium.** The recommendation is evidence-based but the
platform's authority-enforcement track record is thin: S1264
warn-mode is the *only* precedent, and it is 3 months old at
this writing. The recommendation is safe but its "smallest
first move" framing assumes E's producer instrumentation cost
is genuinely lower than A/B declaration cost — an assumption
that could turn out wrong at scale if audit-producer sites
proliferate (Agent 5 §B failure mode: schema drift).

---

## 2. Prior Research Dependencies

### 2.1 Chain of prerequisites

Per `docs/research/ARCHITECTURE_INDEX.md` §4 dependency graph
(v4):

```
Governance + Authority Evolution (§1.4, S1269)
  ├─ named 4 governance planes that don't compose
  ├─ named Symbol Mapping as prereq for enforce-mode
  └─ 12 governance incidents + 3 new (I-G1: authority
     symbol-mapping gap)

Symbol Mapping Architecture (§1.6, S1270)
  ├─ enumerated 5 mapping options A-E
  ├─ 57 unique action_class strings
  ├─ 20 candidate enforcement boundaries
  ├─ F2: zero runtime surfaces carry action_class metadata
  ├─ F11: 7 architectural blind spots (Rigby SIGN)
  └─ recommended §11.1 Option Selection Design (THIS MISSION)

Actor Identity & Attribution (§1.7, S1271)
  ├─ 3-role vocabulary (executor / sponsor / principal)
  ├─ F1: OpsRun has no user FK
  ├─ F6: 3 drop boundaries (HTTP→Celery, config→OpsRun,
  │     Runner→Step.fn)
  ├─ F7: only AssistantProfile gate reads canonical actor
  └─ F11: single "actor" label produces confidently wrong
        audit trails

Authority Enforcement Design Space (§1.8, S1272)
  ├─ 24 enforcement inputs + 8 gaps
  ├─ 20 boundaries + 12 modes (204-cell compatibility matrix)
  ├─ 6 enforcement design options A-F
  ├─ 15 anti-patterns (3 Tier-0 hazards)
  ├─ 15-prereq DAG (Symbol Mapping at critical-path root)
  ├─ F8: LLMEnforcer fail-open precedent
  └─ recommended §14.1 Symbol Mapping Option Selection Design
     (THIS MISSION)

  ▼
Symbol Mapping Option Selection Design (§?, S1274 — THIS DOC)
  └─ narrows S1270's 5 options; recommends v0 + end-state
     shape; Chris gates
```

### 2.2 What each anchor established

Per S1269 F1: **authority plane is declarative, not enforced.**
`JobContract.authority` is a `dict[str, str]` with 57 unique
strings across 4 employees; zero runtime consumers gate on it
(S1270 F2).

Per S1270 F2: **the platform lacks a binding between authority
action_class strings and runtime actions.** Five options exist
(A-E) with tradeoffs; no choice made yet.

Per S1271 F11: **enforcement needs 3 actor roles kept separate**
(executor_actor / sponsor_actor / principal_user). Treating
`runs_as_username` as executor is anti-pattern #4 per S1272
§10.

Per S1272: **enforce-mode is blocked** until a Symbol Mapping
option is selected. §14.1 explicitly names this mission (S1274)
as P0 next research.

### 2.3 Critical constraints inherited

From S1272 §11 15-prereq DAG:
- **Prereq #1** — stable symbol mapping — is what this mission
  scopes.
- **Prereq #2** — actor role vocabulary — is DONE (S1271 §8.5).
- **Prereqs #3, #4, #5, #6, #7, #9, #10, #11, #12, #13** are
  downstream; this mission decides *which option's* schema they
  fill out.
- **Prereq #14** (cross-plane composition) is deferred per
  S1272 §14.4.

From S1264 warn-mode precedent:
- **Warn-mode preflight NEVER blocks** (mission_runner.py:833-843).
- **Prereq #2 for enforcement is ≥14 days clean telemetry on
  N≥4 employees.** This is the graduation gate for any
  observation-first option, per S1264 handoff.

From S1270 F11 (Rigby SIGN):
- **7 architectural blind spots** — namespace / lifecycle
  governance / bidirectionality / granularity mismatch / policy
  rail proliferation / WORKSPACE_AWARE_AGENTS as identity rail
  / auditability & evidence semantics. Any option choice must
  face at least a subset of these.

---

## 3. Current Runtime Symbol Inventory

Per sub-agent 1 (verified by direct file read on load-bearing
counts; PLATFORM_INVENTORY per DOC_LIFECYCLE §2c wins on
conflicts). Full inventory of 24 systems with reuse potential
per option.

### 3.1 Full inventory

| # | Symbol system | Count | file:line | Reuse potential |
|---|---|---|---|---|
| 1 | `JobContract.authority` action_class strings | **57 unique / 68 total** | jobs.py:238-250 (Rigby=11), 489-505 (Auditor=15), 782-812 (Chief=25), 1098-1116 (Triage=17) | **CRITICAL** — source vocabulary for any option |
| 2 | PA tool schemas | **113** (PLATFORM_INVENTORY) | pa_tool_schemas.py:24-5013 | **HIGH** for Option B; PR-reviewed |
| 3 | PA tool action enums | **~200+ actions** across 113 tools | pa_tool_schemas.py per-tool blocks | **HIGH** for Option B (per-action granularity) |
| 4 | Celery tasks | **~414** | core/tasks*.py + core/tasks_*.py | **MEDIUM** — stable routing keys |
| 5 | MissionRunner steps | **17** across 4 employees | mission_runner.py:372-388 (Step dataclass); jobs.py daily_routine tuples | **HIGH** for Option A; small enumerable set |
| 6 | Management commands | **193** (PLATFORM_INVENTORY) | core/management/commands/ | **LOW** — orthogonal to per-employee authority |
| 7 | AGENT_MAP agent names | **83** | agent_router.py AGENT_MAP | **MEDIUM** — user-facing not authority-facing |
| 8 | `AuthorityLevel` enum | **4** (OBSERVE/RECOMMEND/EXECUTE/PROHIBITED) | jobs.py:41-52 | **CRITICAL** — every authority dict value; reuse in every option |
| 9 | Employee handles | **4** | jobs.py:87 + registry 1327-1347 | **HIGH** — identity primitive |
| 10 | `mission_run_kind` | **4+** (one per employee mission) | models_ops_runs.py:68-73; jobs.py per-job field | **HIGH** — per-mission scope anchor |
| 11 | OpsRunEvent label constants | ≥4 named + many inline | mission_runner.py:264-316 + per-job files | **HIGH** — S1264 `authority_contract_observed` precedent |
| 12 | EventBus streams | **8** | event_bus.py:21-31 | **LOW** — infrastructure identifier |
| 13 | DeliverableType choices | **12** | models_deliverables.py:31-44 | **LOW-MEDIUM** — content classification |
| 14 | PublishIntent enum | **3** (INTERNAL_ONLY, PUBLISH_CANDIDATE, PUBLISH_REQUIRED) | models_deliverables.py:58-81 | **MEDIUM** — workflow intent |
| 15 | Deliverable.category | **UNKNOWN** (free CharField) | models_deliverables.py:137-142 | **LOW** — drift-prone; S1270 §3.5 gap |
| 16 | DirectMessage.thread_type | **3** (dm, group, rigby_routed) | models_messaging.py MessageThread | **LOW** — communication routing |
| 17 | HAI status choices | **8** | models_human_interface.py:35-54 | **MEDIUM** — approval workflow |
| 18 | HAI decision choices | **8** | models_human_interface.py:56-75 | **MEDIUM** — decision vocabulary |
| 19 | HAI urgency choices | **4** | models_human_interface.py:23-33 | **LOW** — priority orthogonal |
| 20 | REMOVED_TOOL_ALIASES | **13** (verified; S1270 said 12) | tool_dispatcher.py:210-229 | **CRITICAL for Option D** — exact registry precedent |
| 21 | GATEWAY_TOOLS | **22** (verified; S1270 said 23) | tool_dispatcher.py:232-242 | **MEDIUM** — canonical gateway set |
| 22 | AGENT_NAME_ALIASES | **2** (rigby→Rigby, ClaudeCode→claude-code) | deliverable_aliases.py:33-36 | **HIGH** — canonicalization precedent |
| 23 | WORKSPACE_AWARE_AGENTS | **20** | epa_handlers_tools.py:3873-3907 | **HIGH** — identity rail for workspace scope |
| 24 | `prohibited_actions` tuples | **30** across 4 employees | jobs.py:252-257, 507-517, 814-830, 1122-1131 | **INAPPLICABLE** — documentation-only vocabulary |

### 3.2 Drift from S1270 §4.1 (corrected)

Per sub-agent 1 verification:
- REMOVED_TOOL_ALIASES: **13** (not 12 as S1270 said)
- GATEWAY_TOOLS: **22** (not 23 as S1270 said)
- 3 systems added not in S1270: PublishIntent, DirectMessage.thread_type, OpsRun.run_kind

These corrections carry forward.

### 3.3 Highest-reuse candidates by scope

Per sub-agent 1 §E:

- **Per-employee-per-action-class:** employee_handle + AuthorityLevel + mission_run_kind + prohibited_actions
- **Per-PA-tool:** PA tool names + action enums + REMOVED_TOOL_ALIASES + GATEWAY_TOOLS + AGENT_NAME_ALIASES
- **Per-MissionRunner-step:** Step.name + Step.fn + OpsRunEvent labels + mission_run_kind + employee_handle
- **Per-agent:** AGENT_MAP + WORKSPACE_AWARE_AGENTS + AGENT_NAME_ALIASES

### 3.4 Out-of-scope symbols

Per sub-agent 1 §C — 10 systems out-of-scope for v0 Symbol
Mapping regardless of option: URL routes (~1857, too many),
mgmt commands (193, orthogonal), Deliverable.category (free
string), signals, feature flags, Celery queues, EventBus
streams, body systems, thread types, OpsRun.run_type.

---

## 4. Option A — Step Self-Declaration

**Shape (per S1270 §5.1 verbatim reuse):** Extend the `Step`
dataclass (`mission_runner.py:372-388`) with a new field
`action_classes_invoked: tuple[str, ...] = ()`. Each per-job
step declaration in `jobs.py` per-job `daily_routine` gains
explicit action_class declarations.

### 4.1 Coverage (per sub-agent 2 §A)

| Boundary | Coverage |
|---|---|
| 1 HTTP middleware | NO |
| 2 ToolDispatcher entry | NO |
| 3 PA tool handler | NO |
| 4 MissionRunner.run() entry | PARTIAL (mission kind visible, per-step action not yet) |
| 5 Preflight (warn-mode) | PARTIAL |
| **6 Before Step.fn** | **YES** (natural fit; declaration visible at step invocation) |
| 7 Inside Step.fn body | NO (closure opaque) |
| 8 Celery task dispatch | NO |
| 9 Celery task execution | NO |
| 10 Model pre_save | NO |
| 11 Deliverable transition | PARTIAL (via step attribution) |
| 12 DirectMessage create | PARTIAL |
| 13 EventBus publish | NO |
| 14 LLM call | PARTIAL (via step context) |
| 15 AgentRouter.route() | NO |
| 16 HAI decision | PARTIAL |
| 17 Retro audit | PARTIAL |
| 18 WebSocket | NO |
| 19 Fleet ingress | NO |
| 20 Spider run | NO |

**Coverage total:** 1 YES / 7 PARTIAL / 12 NO. **Concentrated
at mission step boundary.**

### 4.2 Reuse (Agent 1 + 2)

Reuses:
- `Step` frozen dataclass (`mission_runner.py:372-388`)
- `Step.name` + `Step.fn`
- `AuthorityLevel` enum (jobs.py:41-52)
- `mission_run_kind` (models_ops_runs.py:68-73)
- OpsRunEvent labels (mission_runner.py:264-316)
- Employee handles (jobs.py:1327-1332)
- `prohibited_actions` tuple shape as pattern

**New primitives introduced:** 1 field on Step dataclass.
**Anti-duplication:** PASS per EMPLOYEE_OS_PRIMITIVES.md §2.

### 4.3 Annotation burden (Agent 3)

- **Maintainer:** step author (17 sites at v0)
- **v0 sites:** 17 Step declarations across 4 employees
- **Ongoing sites:** +1 per new step; +1 per Celery task if
  extended
- **Refactor cost:** MEDIUM (declaration couples to step body;
  step body refactor may require sync)
- **Drift risk:** **VERY HIGH** (Rigby S1272 §9.1: "silent
  drift between declaration and body is a primary failure mode")

### 4.4 Actor compatibility (Agent 4)

- executor_actor: **LOW propagation cost** (already in
  MissionRunnerConfig)
- sponsor_actor: **HIGH cost** (lost at F6-a; requires new
  MissionRunnerConfig.sponsor_actor field + OpsRun.sponsor_actor
  FK + step context threading)
- principal_user: **HIGH cost** (lost at F6-c; requires OpsRun.user
  FK + summary JSON parsing at audit time)
- Role separation: **preserved** if new field added distinctly

### 4.5 Enforcement mode readiness (Agent 4)

Enables all 12 modes with downstream actor propagation work.
Pre-dispatch modes (hard-block, soft-fail, require-approval,
defer) at boundary 6 (before Step.fn) — natural fit but sponsor
propagation required.

### 4.6 Failure modes (Agent 5)

- Stale mappings YES — S1270 §5.1 "Declaration drift"
- Missing mappings YES — new action_class in step body without
  declaration update
- False positives YES — overdeclaration
- False negatives YES — underdeclaration ("step invokes actions
  not in declared set")
- Overblocking PARTIAL — mitigated by default `()` = unrestricted
- Silent non-enforcement YES — if backward-compat default masks
  gaps
- Test gaps HIGH — 17 golden-file tests + integration test per
  (employee, job) pair

### 4.7 Rollout compatibility (Agent 5)

Phases 1-3 (inventory / observe-only / warn-mode) all compatible.
Phase 4 (per-employee dry run) natural fit — matches S1264
per-employee opt-in pattern. Phases 5-7 require actor propagation
downstream.

**Smallest v0:** Add `action_classes_invoked` field with default
`()`; ship warn-mode event carrying declared tuple; observe
declared vs. observed drift. **~17 declarations at v0.**

### 4.8 Fit

- **Employee OS fit:** STRONG (17 steps, bounded, reviewable)
- **Whole-platform generalization:** WEAK (steps are
  mission-runner-specific; does not generalize to PA tools /
  agents / spiders / fleet / frontend)

---

## 5. Option B — Tool Registry Metadata

**Shape (per S1270 §5.2 verbatim reuse):** Extend each PA tool
schema in `pa_tool_schemas.py` with an `action_class` field per
tool + per action. ToolDispatcher reads the calling agent's
employee_handle from context; looks up
`JobContract.authority[action_class]`; gates before handler
invocation.

### 5.1 Coverage (Agent 2)

**Coverage total:** 2 YES (boundary 6 ToolDispatcher + boundary
14 audit chain) / 6 PARTIAL / 12 NO.

Bimodal distribution: dispatcher cluster + audit cluster. Weak
tail at indirect-tool boundaries.

### 5.2 Reuse (Agent 1 + 2)

Reuses:
- pa_tool_schemas.py (113 schemas)
- ToolDispatcher (tool_dispatcher.py:687-720)
- REMOVED_TOOL_ALIASES pattern (13 entries — exact registry
  precedent per Agent 1)
- GATEWAY_TOOLS set (22 entries)
- AGENT_NAME_ALIASES canonicalization pattern (2 entries)

**New primitives introduced:** 1 schema extension (per-tool +
per-action key). **Anti-duplication:** PASS.

### 5.3 Annotation burden (Agent 3)

- **Maintainer:** PA tool schema author
- **v0 sites:** 113 tool schemas × ~1.8 actions/tool avg =
  ~200 annotations
- **Ongoing sites:** +1 per new tool; +N per new actions
- **Refactor cost:** MEDIUM-to-HIGH
- **Drift risk:** **VERY HIGH** (Rigby S1272 §9.2: "silent drift
  between annotation and handler behavior is a primary failure
  mode")

### 5.4 Actor compatibility (Agent 4)

- executor_actor: **LOW cost**
- sponsor_actor: **HIGH cost** (dispatcher doesn't intrinsically
  know who authorized)
- principal_user: **HIGH cost** (F6-a boundary; lost from
  Celery-invoked tools)

### 5.5 Enforcement mode readiness (Agent 4)

All 12 modes with actor work. Layer 6 (dispatcher) natural
pre-dispatch site.

### 5.6 Failure modes (Agent 5)

- Stale action_class annotation — handler behavior changes,
  schema doesn't
- Handler behavior mismatch — schema says X, handler does Y
- Deprecated tool alias not cleaned up
- Tool renamed without schema update
- Per-action granularity confusion (mixing read_* + write_*)

### 5.7 Rollout compatibility (Agent 5)

All 7 phases compatible. Layer 6 already has AssistantProfile
gate precedent — enforcement lands as natural extension.

**Smallest v0:** Add `action_class: str | None = None` per tool
schema. Populate for ~10-20 highest-authority tools first.
Warn-mode dispatcher check.

### 5.8 Fit

- **Employee OS fit:** STRONG (tools are canonical Employee OS
  dispatch surface)
- **Whole-platform generalization:** STRONG (tools serve
  agents / PA / beat tasks / mgmt commands / any dispatcher
  caller). **Most platform-agnostic single mechanism.**

---

## 6. Option C — Hybrid Mapping

**Shape:** A + B. Steps declare high-level action families; tool
schemas declare fine-grained per-action authority.

### 6.1 Coverage (Agent 2)

**Coverage total:** 5 YES / 7 PARTIAL / 8 NO. Widest coverage of
mission + tool-dispatch scopes.

### 6.2 Reuse

Both A + B reuse footprints.

**New primitives introduced:** 2 (Step field + Tool schema
attribute). **Anti-duplication:** PASS but MAINTENANCE burden
compounds.

### 6.3 Annotation burden (Agent 3)

- **Maintainer:** step author + tool schema author (dual)
- **v0 sites:** 17 + ~200 = ~217 total
- **Refactor cost:** HIGH (dual surfaces; cross-check required)
- **Drift risk:** **VERY HIGH (compounded)** — both A and B
  drift risks apply independently

### 6.4 Actor compatibility (Agent 4)

Same as A + B: executor LOW; sponsor + principal HIGH.

### 6.5 Enforcement mode readiness

All 12 modes. Layers 4 + 6 both viable.

### 6.6 Failure modes (Agent 5)

All of A + all of B, plus:
- Cross-surface inconsistency (step says X, tool says Y)
- Redundant declaration conflict (precedence ambiguity per S1270
  §5.3)

### 6.7 Rollout compatibility

Both A + B phases available. Can ship A first then B, or B first
then A, or both in same PR. **Bundled release is not
recommended** per §1.3 above — dual maintenance burden without
proven value.

### 6.8 Fit

- Employee OS: STRONG (defense-in-depth for employee workflows)
- Generalization: STRONG unions, but non-tool-dispatch gaps
  remain (model writes, ORM, agent delegation)

**Rejected as standalone v0** per §1.3.

---

## 7. Option D — Central Registry

**Shape (per S1270 §5.4 verbatim reuse):** New module-level
registry mapping every action_class string to a runtime
*predicate* (callable that returns True when the runtime is
invoking that action_class). Predicate inspects mission context,
active tool call, in-flight model save, etc.

### 7.1 Coverage (Agent 2)

**Coverage total:** 11 YES / 7 PARTIAL / 1 N/A / 1 NO. **Flattest
coverage curve of all 5 options** — spans all 7 execution scopes.

### 7.2 Reuse

- `AuthorityLevel` enum (jobs.py:41-52)
- REMOVED_TOOL_ALIASES pattern (13 entries — closest existing
  registry shape)
- Step.name uniqueness pattern
- Employee handles
- Optionally prohibited_actions human-readable prose (as
  registry tooltip)

**New primitives introduced:** 1 new registry module +
predicates. **Anti-duplication:** PASS per Agent 2 §E — orthogonal
to existing _JOBS_BY_EMPLOYEE / _EMPLOYEES_BY_HANDLE /
REMOVED_TOOL_ALIASES.

### 7.3 Annotation burden (Agent 3)

- **Maintainer:** central registry maintainer (one owner or
  shared)
- **v0 sites:** ~57 predicates (one per authority string) or
  fewer if predicates factor
- **Ongoing sites:** +1 per new authority string; +0 per
  step/tool unless binding changes
- **Refactor cost:** LOW (centralized; local change)
- **Drift risk:** **HIGH** but lower than A/B — predicate logic
  errors (too broad / too narrow) rather than
  maintenance-scatter drift

### 7.4 Actor compatibility (Agent 4)

- executor_actor: **MEDIUM cost** (predicate context must
  include; context object shape UNKNOWN per S1270 §5.4)
- sponsor_actor: **HIGH cost** (same as A/B; F6-a boundary)
- principal_user: **HIGH cost** (same)

### 7.5 Enforcement mode readiness

All 12 modes at ANY boundary 1-20 where context is constructible
with roles. **Most flexible layer choice** if predicate context
shape is resolved.

### 7.6 Failure modes (Agent 5)

- Predicate mismatch (runtime symbol drifts; predicate no longer
  matches)
- Unmapped authority string (registry missing entry)
- Orphaned registry entry (predicate maps to deleted code)
- Predicate collision (two authority strings match same runtime
  call)
- Predicate too broad (false positives)
- Predicate too narrow (silent misses)

### 7.7 Rollout compatibility

All phases available but requires context shape design upfront.
Predicate context factory becomes a distinct sub-project.

### 7.8 Fit

- Employee OS: MODERATE (upfront authorship cost high)
- Generalization: STRONG (orthogonal to surface; scales to any
  boundary with context)

**S1272 §14.3 recommendation:** pair D with E as safety net.

---

## 8. Option E — Evidence-Only Mapping

**Shape (per S1270 §5.5 verbatim reuse):** No new binding.
Every action surface emits action_class as part of its audit row
(`ToolCallRecord.action_class`, `OpsRunEvent.detail.action_class`,
`LLMCallEvent.action_class`, `CeleryTaskEvent.action_class`,
`AgentExecution.action_class`). Violations detected retrospectively
via post-mission audit or a periodic scan. **No pre-dispatch
enforcement.**

### 8.1 Coverage (Agent 2)

**Coverage total:** 2 YES / 4 PARTIAL / 14 NO. Bimodal (audit +
retro). All pre-dispatch modes disabled.

### 8.2 Reuse (Agent 1 + 2)

Reuses:
- ToolCallRecord model
- OpsRunEvent model + `AUTHORITY_CONTRACT_OBSERVED_LABEL`
  pattern (mission_runner.py:264)
- LLMCallEvent model
- CeleryTaskEvent model
- AgentExecution model
- `evidence_for_mission()` at status.py:53-251
- Bug Triage step 4 aggregation pattern (bug_triage.py:396-453)
- `AuthorityLevel` enum for level annotations

**New primitives introduced:** 5 column additions across 5
audit models (`action_class`) + 3 role columns (`executor_actor`,
`sponsor_actor`, `principal_user`) or JSONField key extensions.
**Anti-duplication:** PASS per Agent 2 §E (extends existing
audit models; no new audit table).

### 8.3 Annotation burden (Agent 3)

- **Maintainer:** audit-row producer (~15-20 scattered
  producer sites across 5 audit models)
- **v0 sites:** 5 audit models × 2-5 producer sites each
- **Ongoing sites:** +1 per new audit-emission site; +0 per new
  step/tool
- **Refactor cost:** LOW-to-MEDIUM (each producer is 1-2 lines
  of additional field population)
- **Drift risk:** **MEDIUM** — evidence immutable once written;
  primary drift is producer omission (detectable via NULL
  count)

### 8.4 Actor compatibility (Agent 4)

- executor_actor: **MEDIUM** — audit models must carry
  agent_name or executor_id field (ToolCallRecord.agent_name
  exists; OpsRunEvent missing per S1272 §6.3)
- sponsor_actor: **MEDIUM** — new column addition
- principal_user: **MEDIUM** — audit models extended with
  user_id FK (ToolCallRecord.user, OpsRunEvent.user)
- **Only option that mechanically carries all 3 roles
  end-to-end IF audit models extended** (Agent 4 §A)

### 8.5 Enforcement mode readiness (Agent 4)

**Enables 5 of 12 modes:** observe-only, warn-mode,
degrade-mission-evidence, retrospective-violation-report,
freeze-platform. **All 7 pre-dispatch modes disabled.**

### 8.6 Failure modes (Agent 5)

- Missing action_class in producer (producer omits field)
- Wrong action_class populated (inferred incorrectly)
- Partial coverage (some audit models extended, others not)
- Evidence schema drift (JSONField structure changes)
- Producer lifecycle blind spot (row later updated / deleted by
  cleanup)

### 8.7 Rollout compatibility (Agent 5)

Phases 1-3 (inventory / observe-only / warn-mode) all natural
fit. Phase 4 (per-employee dry run) available. Phases 5-7 (per
boundary / human-reviewed / limited enforce) **NOT AVAILABLE**
— E is fundamentally post-dispatch. To reach enforcement,
layer A/B/C/D on top.

**Smallest v0 (per Rigby S1274 SIGN Q3 refinement):**
Audit-model schema extensions (**minimum set** — 2-3 models, not
all 5) + **3-5 highest-leverage producer sites**. Emit
`authority_action_observed` event (parallel to S1264's
`authority_contract_observed`). Remaining models + producers
land incrementally per §13 phase progression. **Chris does NOT
approve "5 migrations + 15-20 sites immediately" — that is the
end-of-Phase-5 shape, not v0.**

### 8.8 Fit

- **Employee OS fit:** STRONG (audit chain already carries
  employee action traces)
- **Whole-platform generalization potential (Rigby S1274 SIGN
  edit):** STRONG **once producers exist**. **v0 coverage
  remains narrow (2/4/14 per §8.1)** — the audit models are
  surface-agnostic in *shape* but only cover the surfaces where
  producers are instrumented. **Fleet / WebSocket / Spider are
  NOT covered at v0 until those specific producers emit
  `authority_action_observed` events.** Generalization is an
  *end-state property* under layered producer expansion, not a
  *v0 property*.

---

## 9. Comparative Matrix

Per mission spec §9 required table. Verdicts per row cite prior
analysis in §4-§8.

| Option | Coverage | Drift Risk | Annotation Burden | Enforcement Readiness | Employee OS Fit | Whole-Platform Fit | Rollback | Risk | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **A: Steps declare** | 1/20 YES + 7 PARTIAL (concentrated at mission step) | **VERY HIGH** (Agent 3) | 17 sites v0; MEDIUM refactor | All 12 modes with actor work; F6-c blocks step-internal enforcement | STRONG (17 steps bounded) | WEAK (mission-only; does not generalize) | Feature flag; per-employee opt-in | Pre-dispatch failure surface + drift risk | **POSSIBLE (secondary layer, not v0)** |
| **B: Tool attribute** | 2/20 YES + 6 PARTIAL (dispatcher + audit) | **VERY HIGH** (~200 sites; per-action drift) | ~200 sites v0; MEDIUM-HIGH refactor | All 12 modes with actor work; layer 6 natural | STRONG (canonical dispatch surface) | STRONG (tools serve all callers) | Feature flag on `action_class` field lookup | Schema-vs-handler drift + fail-open default | **POSSIBLE (secondary layer, not v0)** |
| **C: Hybrid** | 5/20 YES + 7 PARTIAL (mission + tool dispatch) | **VERY HIGH (compounded)** | 217 sites; HIGH refactor (dual) | All 12 modes; layer 4 + 6 both viable | STRONG (defense-in-depth) | STRONG (unions A+B) | Layer-by-layer feature flags | Precedence ambiguity + doubled maintenance | **REJECT (as standalone v0)** — see §1.3; A and B can ship sequentially |
| **D: Central registry** | 11/20 YES + 7 PARTIAL (flattest) | **HIGH** (predicate logic errors) | ~57 predicates v0; LOW refactor (centralized) | All 12 modes at ANY of 20 boundaries; context shape UNKNOWN | MODERATE (upfront authorship high) | STRONG (orthogonal to surface) | Registry disable / per-predicate | Predicate context shape UNKNOWN (S1270 §5.4); single point of failure | **DEFER (end-state candidate; not v0 without E safety net per S1272 §14.3)** |
| **E: Evidence-only** | 2/20 YES + 4 PARTIAL (audit + retro) | **MEDIUM** (producer omission; immutable evidence) | 15-20 producer sites v0; LOW refactor | 5 of 12 modes enabled (post-dispatch only) | STRONG (audit chain already exists) | STRONG (audit covers all surfaces) | Additive migration reversible; remove producer calls | Cannot prevent catastrophic actions in real time | **STRONG CANDIDATE (recommended v0 per §1.1 + §10)** |

---

## 10. Recommended Selection

Per mission spec §10 format:

**Recommended first move (v0):** **Option E — Evidence-only
mapping.**

**Recommended end-state (Chris-gated later; possibly 6-24
months out):** **E + B** layered — Option E as foundation
(post-dispatch audit + retro violation reports); Option B as
pre-dispatch tool-mediated enforcement. **Options A and D
reserved** as tertiary layers if per-tool + per-step + per-audit
coverage is insufficient to close the S1272 §11 15-prereq DAG.

### 10.1 Why

**Per §1 executive summary + §4-§8 detailed evaluation:**

1. **Lowest drift risk** (Agent 3 MEDIUM vs. VERY HIGH/HIGH for
   others). Evidence-only drift is producer omission, not silent
   behavior mismatch. Detectable via NULL count queries.

2. **Only option carrying all 3 actor roles end-to-end**
   (Agent 4 §A). E's audit rows can carry
   `executor_actor` + `sponsor_actor` + `principal_user` as
   separate columns. Options A/B/C/D all lose ≥1 role at S1271
   F6 drop boundaries.

3. **Highest reversibility** (S1272 F7). Additive schema
   migrations; rollback = revert migration + remove producer
   calls. No missions blocked; no need to unwind enforcement
   state.

4. **Preserves current fail-safe posture** aligned with
   `mission_runner.py:895-899` in-code assertion.

5. **Compatible with every downstream option.** A/B/C/D layer on
   top; E's rows become the safety net (Agent 4 §F +
   S1272 §14.3).

6. **Ships fastest** (Agent 5 §B). 5 audit model migrations +
   3-5 initial producer sites. Bug Triage step 4 aggregation
   already precedent for consuming the emitted events.

7. **Directly unblocks 9 of 15 prereqs** in S1272 §11 DAG
   without introducing the pre-dispatch failure surface those
   prereqs are designed to gate.

### 10.2 What it unlocks

- Authority telemetry across all runtime surfaces (audit rows
  fill in over N missions)
- Per-employee dry-run analysis: "if E's evidence trail had been
  in place last month, what would have been flagged?"
- The ≥14-day clean telemetry window per S1264 prereq #2
- Actor role separation in the audit chain (all 3 roles
  present in every row)
- Retrospective violation reports (Bug Triage step 4
  extension pattern)
- Data-driven downstream Chris decision: "Now that we have 14+
  days of E telemetry, which pre-dispatch option (A/B/C/D)
  should we add next?"

### 10.3 What it does not solve

- **Pre-dispatch prevention.** E is post-dispatch by design.
  Catastrophic actions execute before detection.
- **Hard-block-required actions** (per S1272 §10 Tier-0 hazards):
  destructive model writes, external outbound, secret access.
  These require A/B/C/D layered on top.
- **Real-time authority alerts.** E surfaces violations at
  next-mission aggregation, not at time of action.
- **Cross-plane composition** (per S1272 §7.5 8 open questions).
  E does not compose with autonomy / budget / human governance
  planes any more than the current state does; that remains
  deferred future research per S1272 §14.4.

### 10.3.1 Catastrophic-action graduation guardrail (Rigby S1274 SIGN edit)

**Why this is here:** without an explicit trigger for moving
beyond E-only, "safe v0" becomes "forever v0" (Rigby's phrasing).
A guardrail keeps E honest: E is instrumentation substrate + truth
data generator, **not** the mapping solution.

**Trigger to graduate from E-only to E+B (or other pre-dispatch
layer):** Chris must decide within 30 days when *any* of the
following telemetry signals fires:

1. **Tier-0 hazard observed ≥1 time** — E's audit chain records
   an action mapped to `open_pull_request`, `delete_database_rows`,
   `execute_arbitrary_code`, or `access_secret_values` (per
   S1272 §10 Tier-0 hazards + gap surfaces from S1270 §3.4).
   Rationale: even one instance is one too many; pre-dispatch
   enforcement layer must ship before it happens again.
2. **PROHIBITED-level violation rate > 0 per employee per 14-day
   window** — any employee's audit chain shows an action mapped
   to a PROHIBITED-level authority string. Rationale: PROHIBITED
   is the strongest documented policy; runtime violation of any
   PROHIBITED string demands enforcement graduation.
3. **Symbol Mapping NULL rate > 30% after Phase 4 (per-employee
   dry run) completes** — persistent NULL `action_class` rows
   indicate producer instrumentation is insufficient; E-only is
   surfacing "unknown" instead of enforceable evidence. Chris
   must choose whether to invest more producer sites (stay E) or
   layer B on top of tool dispatch for cleaner coverage.
4. **≥90 days elapsed since Phase 5 (all-employee steady state)
   without downstream layer decision** — regardless of telemetry
   noise, 3 months is the outer bound before "forever v0" risk
   materializes. Chris re-decides at that point (may confirm E
   is sufficient; may layer B/A/D on top).

**Not a graduation trigger:** low violation rate. A quiet audit
chain is not evidence that enforcement isn't needed — it may just
mean E's instrumentation is under-sampling.

**What "graduate to E+B" concretely means:** Chris commissions the
downstream Authority Enforcement Design Decision mission (S1272
§14.3) with E's telemetry as evidence input. That mission scopes
which pre-dispatch layer to add (B is the recommended pair per
S1272 §14.3, but A or D are on the table).

**What "stay E-only" means:** Chris explicitly re-ratifies E as
sufficient. This is a valid outcome per §10.6; the guardrail
exists to force the decision, not force the graduation.

### 10.4 What must remain out-of-scope for v0

- Any pre-dispatch check (defer to layered options)
- Any change to `MissionRunner` behavior beyond emitting the new
  `authority_action_observed` event
- Any change to `JobContract` schema (E does not expand it)
- Any change to `Step` dataclass (E does not extend it)
- Any change to PA tool schemas beyond audit population
- Any hard-fail behavior (E MUST fail-open per S1272 F8
  precedent)
- Any change to actor role plumbing beyond adding columns to
  audit models

### 10.5 Reversibility statement

Ship E as v0. If, after ≥14 days of telemetry, the evidence
does NOT support layering B (or A, or D) on top, revert the
migration + remove producer calls. No missions blocked; no
frozen state to unwind. Chris re-decides.

### 10.6 Alternative paths considered and not recommended

- **Ship B first (without E):** Rejected. Ships pre-dispatch
  fail-open at high scale (~200 schemas). No safety net for
  schema-vs-handler drift. Drift latency up to 7 days (Bug
  Triage cycle) without evidence trail to reconstruct what
  happened.

- **Ship C bundled A+B:** Rejected per §1.3. Doubles maintenance
  surface without proven value.

- **Ship D as v0:** Rejected. Predicate context shape UNKNOWN
  (S1270 §5.4). Predicate authorship burden is HIGH. S1272
  §14.3 explicit recommendation: pair D with E — E must ship
  first as safety net anyway.

- **Ship A first:** Possible but not recommended. Weak
  generalization (mission-only). Drift risk VERY HIGH. Would
  need to ship E anyway for observability. Sequencing A → E
  vs. E → A gives strictly worse rollback story.

- **Ship nothing (defer entire mission):** Rejected. S1272 §11
  prereq #1 blocks all downstream missions. Every day without a
  Symbol Mapping choice extends the enforcement gap S1264
  discovered.

### 10.7 Confidence and unknowns

**Confidence: Medium.** The recommendation is evidence-based
but the platform's authority-enforcement track record is thin.
Assumption load-bearing to the recommendation: **E's producer
instrumentation cost is genuinely lower than A/B declaration
cost.** If audit-producer sites proliferate at scale (Agent 5
§B schema drift), E's advantage diminishes.

**Known unknowns:**
- Audit-model retention policy (`CELERY_TASK_EVENT_RETENTION_DAYS=30`
  suggests ~30 days; is that long enough for the ≥14-day clean
  window + rolling analysis?)
- Producer inventory completeness (~15-20 sites estimated;
  actual may differ)
- Whether Rigby will pressure-test this recommendation and
  suggest a variant

---

## 11. Minimum Viable Symbol Event

Per mission spec §11. **Research only; do not implement.**
Field-by-field with data sources. Actor roles kept SEPARATE.

**Event label (per S1264 precedent):**
`authority_action_observed` (parallel to existing
`authority_contract_observed` label; same shape family, action-
level not contract-level).

**Event detail JSON shape:**

| Field | Type | Data source | Notes |
|---|---|---|---|
| `schema_version` | int | Constant | Bump on shape change (S1264 pattern) |
| `action_class` | str | inferred at producer time | The 57-string vocabulary; NULL if UNKNOWN |
| `runtime_symbol_type` | str enum | "step" / "tool" / "task" / "model" / "event" / "agent" / "spider" / "fleet" / "http" / "websocket" | Which surface emitted |
| `runtime_symbol` | str | Producer-specific (step.name, tool_name, task name, model class, event label, agent_name, spider_name, app_slug, route, consumer name) | The specific identifier |
| `mapping_source` | str enum | "step_declaration" / "tool_schema" / "central_registry" / "audit_producer_inferred" | Which of Options A/B/D/E populated it |
| `mapping_confidence` | str enum | "definite" / "inferred" / "probable" | Confidence level; NULL if not applicable |
| `executor_actor` | str | AIEmployee.handle or agent name or "system" or fleet app_slug | Runtime entity that ran the code (S1271 §8.5) |
| `sponsor_actor` | str | UnifiedUser.username or "system" (beat) or app_slug (fleet) or "claude-code" (source) | Entity that authorized (S1271 §8.5); NULL if UNKNOWN |
| `principal_user` | int (User FK) or NULL | Resolved via `_resolve_runs_as_user_id` at mission_runner.py:1585-1591 | User for row ownership (S1271 §8.5); NULL on lookup miss (S1271 F3) |
| `employee_handle` | str | MissionRunnerConfig.employee_handle | Same as executor_actor for mission-fired actions; separate for delegated |
| `job_key` | str | JobContract.job_key or NULL | For mission-scoped actions |
| `mission_id` | UUID or NULL | OpsRun.mission_id | For mission-scoped actions; NULL for standalone |
| `ops_run_id` | UUID or NULL | OpsRun.id | Parent audit row |
| `tool_call_id` | str or NULL | ToolCallRecord.trace_id | For tool-mediated actions |
| `celery_task_id` | str or NULL | Celery task_id | For Celery-executed actions |
| `boundary` | str enum | One of S1272 §3's 20 boundaries | Where the observation fired |
| `mode` | str enum | "observe-only" / "warn-mode" / "dry-run" | Mode at time of observation; per S1272 §4 vocabulary |
| `mapped_at` | timestamp | `timezone.now()` at producer time | For retention + rolling-window queries |
| `notes` | str or NULL | Free-form (degradation reason, mapping confidence explanation) | Per S1264 authority_contract_observed pattern |

**Actor role separation constraint:** the three actor role
fields (`executor_actor`, `sponsor_actor`, `principal_user`) are
STORED SEPARATELY. Never collapsed into a single "actor" column.
Per S1271 F11: a single actor label produces confidently wrong
audit trails.

**Employee_handle vs. executor_actor distinction (Rigby S1274
SIGN edit).** The event carries both `employee_handle` and
`executor_actor` fields. They are related but NOT interchangeable:

- **`employee_handle`** is the Employee OS identity (one of the
  4 registered handles: rigby, platform_auditor, chief_of_staff,
  bug_triage). Populated only when the action originated from a
  mission fired by an AIEmployee (per `AIEmployee.handle`).
  NULL for non-mission-fired actions (HTTP request, fleet call,
  standalone Celery task not tied to an employee mission).

- **`executor_actor`** is the generalized runtime executor
  identifier per S1271 §8.5 — may be an AIEmployee handle, a
  service `app_slug`, an agent name from AGENT_MAP, "system"
  for beat-fired non-employee tasks, "claude-code" for source-
  attributed autonomous engineer, or "anonymous" for
  unauthenticated actions.

- **Relationship:** for mission-fired actions,
  `employee_handle == executor_actor` in most cases. But
  when an employee mission dispatches a worker agent (per
  S1271 §8.1 Q7.4), `employee_handle='rigby'` while
  `executor_actor='WorkerAgentName'` — the delegator vs.
  executor distinction per S1271 F4 stays live in the audit
  trail.

- **Do NOT collapse them.** Readers of the audit chain must be
  able to answer both "which Employee OS employee's job ran
  this?" (`employee_handle`) and "which runtime actor executed
  the code path?" (`executor_actor`) independently.

**Backward-compatibility note:** all fields except
`schema_version`, `action_class`, `mapping_source`, and
`boundary` are optional / NULL-able. Additive at v0. Retention:
same policy as OpsRunEvent (currently ~30 days per
`CELERY_TASK_EVENT_RETENTION_DAYS`; needs verification for
authority events).

---

## 12. Testing and Drift Detection Strategy

Per mission spec §12. **Research only.**

### 12.1 Tests that would detect drift patterns

Per Agent 3 §C and Agent 5 §D:

| Drift pattern | Test type | Cost | Coverage |
|---|---|---|---|
| Unmapped `action_class` in `JobContract.authority` | Integration test (join every authority string against emitted events over 14-day window) | Standing (query cost) | Complete |
| Unmapped tool action (dispatcher observes action not in registry) | Unit test per tool + integration test at dispatch | 113 tests + 1 dispatcher-side | Per Option B |
| Step declared action not in JobContract | Unit test per employee (`declared` ⊆ `authority.keys()`) | 4 tests | Per Option A |
| JobContract action unused anywhere | Standing audit query over N-day window | 1 query | Detects orphans |
| Stale REMOVED_TOOL_ALIASES entries | Unit test (verify aliased tool has no active dispatchers) | 1 test | Complete for existing 13 |
| Duplicate symbol names | Unit test on registry uniqueness | 1 test | Complete |
| Mapping collision (Option D predicate matches multiple) | Predicate-collision test | 1 test | Sampled |
| Missing actor roles | Integration test (every emitted event has all 3 role fields present or explicit NULL) | 1 test | Complete |
| Missing evidence events | Producer instrumentation test (mock-capture per producer) | 15-20 tests | Complete per producer |
| **Misclassified non-NULL `action_class`** (wrong but non-NULL — false confidence per Rigby S1274 SIGN edit) | (a) Sample-based truthing review: monthly Rigby / Chris review of N=20-50 random emitted events; verify `action_class` inferred correctly. (b) Cross-source consistency: for the same runtime symbol (e.g., tool call), verify multiple producers agree on `action_class` (if 3 audit models emit for one action, all three must agree). (c) Golden-flow tests: for known reference missions (e.g., Rigby's daily docs cascade), verify the emitted `action_class` sequence matches a hand-annotated expected trace. | Standing (monthly review) + 3-5 golden flows | **Higher-risk drift than producer omission** — NULL count dashboards won't catch this class; sample-based review is the load-bearing detection mechanism |

### 12.2 Canary tests (S1244 queue-parity pattern precedent)

**Symbol Mapping canary:** For each authority string in
`JobContract.authority`, run a scan every N hours checking whether
the string was observed in the audit chain over the past 24
hours. If a string was observed but has `mapping_source='UNKNOWN'`,
alert. If a string is documented as EXECUTE-level but was
observed by a non-EXECUTE actor, alert.

**Reversibility canary:** If Option E is layered with any of
A/B/C/D later, canary that E's audit rows still emit for actions
the pre-dispatch gate allowed. Detects the "silent enforcement"
Tier-0 hazard from S1272 §10.

### 12.3 Cross-reference to Rigby S1270 §8 (SIGN blind spot #2)

Rigby's S1270 F11 blind spot #2 is "symbol lifecycle governance"
— canonical symbol + aliases + deprecation markers + removal
window. **This mission's E recommendation inherits that
concern:** how does E's `action_class` field evolve when
authority strings are renamed / deprecated / consolidated? Cross-
reference to REMOVED_TOOL_ALIASES pattern (13 entries; Session
1079 origin) for a proven lifecycle mechanism.

---

## 13. Rollout Strategy

Per mission spec §13. **Research only.**

### 13.1 Phase progression for Option E (recommended v0)

| Phase | Name | Actions | Reversibility | Exit criteria |
|---|---|---|---|---|
| **1** | Inventory-only | Enumerate audit models + producer sites; write migration; do NOT ship | Fully reversible (no runtime state) | Migration + producer list reviewed via PR |
| **2** | Observe-only event emission | Ship migration; instrument 3-5 producers; emit `authority_action_observed` events; consume in Bug Triage step 4 (extended) | Reversible via revert-migration + remove producers | 7 days of events emitted per employee; NULL rate <20% |
| **3** | Warn-mode dashboards | Extend `employee_tool action=evidence_for_mission` to surface authority_action_observed events + build simple dashboard (or Deliverable-based summary) | Reversible via config toggle | Chris confirms dashboard renders; per-employee cross-check by Rigby |
| **4** | Per-employee dry run | Extend E to more producers (aim ~15-20 sites); complete role-field population; verify sponsor + principal populated for ≥90% of rows for one employee (per-employee opt-in per S1264 pattern) | Reversible per-employee via config | 14 days clean telemetry on one employee (S1264 prereq #2 pattern) |
| **5** | All-employee steady state | Complete producer instrumentation across all 4 employees; verify NULL rates acceptable; retention policy confirmed | Steady-state; not phased | 14 days clean telemetry on all 4 employees (S1264 prereq #2 full pattern) |
| **6** | Chris decides next layer | With ≥14 days of clean E telemetry, Chris chooses whether to layer A / B / D on top. Downstream Authority Enforcement Design Decision mission (S1272 §14.3) consumes E telemetry as input | Downstream decision; not part of E rollout | Design decision by Chris gated |

**Note on phases 6-7 from mission spec** (human-reviewed
violations + limited enforce-mode): these are downstream of
Option E's rollout — they belong to whichever layered option
Chris chooses in phase 6. This mission does not scope those.

### 13.2 Phase transition safeguards

| Transition | Safeguard |
|---|---|
| 1 → 2 | Migration is reviewed by 2 engineers (Rigby + Chris); rollback tested in staging |
| 2 → 3 | 7 days of events emitted before dashboard ships; NULL rate baseline established |
| 3 → 4 | Chris confirms dashboard is useful (not noise); per-employee opt-in flag |
| 4 → 5 | ≥14 days clean telemetry on chosen employee before expanding |
| 5 → 6 | Chris gate; downstream design mission required before any pre-dispatch layer added |

### 13.3 Rollout for other options (if Chris chooses differently)

Per Agent 5 §D:

- **Option A rollout:** phases 1-4 same shape but ~17
  declarations at v0 instead of ~15-20 producer sites. Phase 5
  is per-employee opt-in for enforcement (not just observation)
  because A can layer pre-dispatch enforcement at step boundary
  from day one. Higher risk than E; higher speed if
  MissionRunner-only enforcement is sufficient.

- **Option B rollout:** phases 1-4 same shape but ~200 tool
  schema annotations at v0. Phase 5 is per-tool opt-in for
  pre-dispatch enforcement. Higher risk than E; broader
  platform coverage than A.

- **Option D rollout:** phases 1-4 require predicate context
  factory design as sub-project (phase 0.5). ~57 predicates at
  v0. Chris must approve the context shape before any
  predicate authorship starts.

---

## 14. Anti-Patterns

Per mission spec §14. Fifteen dangerous choices per S1272 §10
+ 3 mission-specific additions.

### 14.1 Inherited from S1272 §10

1. Blocking all model writes (Tier-0 hazard)
2. Enforcing free-form `prohibited_actions` prose (not a symbol)
3. Trusting LLM self-reported actions
4. Treating `runs_as_username` as executor_actor (S1271 F11)
5. Assuming employee_handle equals user
6. Enforcement via MissionRunner only (ignoring ToolDispatcher)
7. Enforcement via ToolDispatcher only (ignoring direct ORM
   writes)
8. Enabling enforcement before symbol mapping exists (Tier-0
   hazard)
9. Enabling enforcement before actor roles are resolved
10. Creating new approval models when HAI already exists
11. Enforcing at wrong layer (per S1270 §6.2)
12. Making enforcement unrollable
13. Collecting metrics before min telemetry window
14. False-positive tolerance > system capacity
15. Silent enforcement (Tier-0 hazard)

### 14.2 Mission-specific additions

16. **Trying to cover every runtime boundary on day one.** Option
    E's coverage table (Agent 2) is 2 YES / 4 PARTIAL / 14 NO.
    That is correct for v0. Attempting to close all 20
    boundaries in v0 turns E into "E+A+B+D bundled" — Option C
    variant that was rejected per §1.3.

17. **Choosing central registry (Option D) without ownership.**
    Predicate authorship + maintenance requires a dedicated
    owner. Without clear ownership, the registry rots. This
    inherits S1270 F11 blind spot #2 concern.

18. **Choosing step self-declaration (Option A) without drift
    tests.** Agent 3 marked A as VERY HIGH drift risk. Without
    the 17 golden-file tests + integration test per
    (employee, job), silent drift is inevitable.

19. **Treating evidence-only (Option E) as enforcement.** E
    detects; it does not prevent. Anti-pattern is downstream
    consumers reading E's rows and treating them as "actions
    were blocked" — they were not.

20. **Ignoring PA tools entirely.** Option A alone would miss
    tool-mediated actions (Agent 2 §B). Any v0 choice that
    doesn't observe PA tool dispatch has a load-bearing gap.

21. **Expanding JobContract prematurely.** The 57 authority
    strings are the current vocabulary. Adding new strings
    without runtime binding first (Option E audit trail) is
    guessing at future needs.

---

## 15. Open Questions

Genuine open questions for Chris.

**Q1 — Does Chris accept Option E as v0, or prefer a different
first move?**
This is the load-bearing question this mission scopes. Every
downstream question depends on it.

**Q2 — If Option E ships, what's the target NULL rate for role
fields?**
Per §11: `executor_actor`, `sponsor_actor`, `principal_user`
should all be present. If NULL rate is high (say >30%), E's
value diminishes.

**Q3 — What's the retention policy for `authority_action_observed`
events?**
`CELERY_TASK_EVENT_RETENTION_DAYS=30` is the current precedent.
Symbol-mapping telemetry may need longer retention for
retrospective analysis.

**Q4 — Should E be extended to include model-write events?**
Some actions (e.g., `modify_docs_files`) happen via ORM writes
outside all 5 audit models. Should E instrument Django signals
too? Or is that Option A/B/D territory?

**Q5 — Which downstream option (A/B/D) should Chris consider
after E ships?**
This is the S1272 §14.3 downstream mission — Chris decides
after telemetry.

**Q6 — Should the `mapping_source` enum include a value for
"human_review" or "chris_annotation"?**
For edge cases where Chris manually annotates an event's
action_class post-hoc. Design choice; not v0 critical.

**Q7 — How does E's evidence trail compose with S1264
`authority_contract_observed` events?**
Both are OpsRunEvent labels. Should they cross-reference? Or
stay independent?

**Q8 — What's the exit criterion for "enforce is safe"?**
Per S1272 §11 prereq #12 (trust threshold) and #13
(false-positive threshold). Chris + Rigby must jointly define
these before any pre-dispatch option layers on top of E.

**Q9 — Does the recommendation change if Chris wants pre-dispatch
enforcement in Q2 2026?**
E as v0 delays pre-dispatch by ≥14 days (metrics window) plus
downstream mission cycle. If timing pressure is urgent, Chris
may prefer B first (skip E foundation). Trade-off: speed vs.
reversibility.

**Q10 — Are there authority strings from the 57-unique set that
should be excluded from Symbol Mapping entirely (per S1270 §3.4
gap surfaces)?**
Strings like `open_pull_request`, `restart_worker`,
`modify_any_file`, `send_emails_externally`,
`execute_arbitrary_code`, `access_secret_values` have no
runtime hook. Should E's producer instrumentation skip them
explicitly, or emit UNKNOWN events?

---

## 16. Recommended Next Step

Per mission spec §16. Based on evidence.

### 16.1 Symbol Mapping Event Schema Design (if Chris ratifies E as v0)

**Scope.** With E chosen as v0, the next mission is to design the
concrete event schema (per §11 sketch above) + producer
instrumentation contract + retention policy + Bug Triage step 4
extension.

**Why next.** Deferring the schema design keeps E as words on
paper. Actual implementation (migrations + producer touch points)
requires a spec Rigby can SIGN.

**Prerequisites.** This mission's E recommendation ratified by
Chris.

**Expected outcome.** A design decision doc with concrete field
types, retention policy, and producer instrumentation checklist.
Rigby SIGN + Chris gate.

### 16.2 Alternative: Actor Role Propagation Design (S1272 §14.2)

**Scope.** If Chris ratifies a different Symbol Mapping option
(A, B, or D), the next mission shifts to Actor Role Propagation
Design — because A/B/D all have HIGH sponsor + principal
propagation costs, and that work must precede any pre-dispatch
enforcement.

**Prerequisites.** Chris's Symbol Mapping selection.

### 16.3 Explicitly NOT recommended as immediate next

- Any pre-dispatch enforcement implementation (S1272 §11 prereqs
  must close first)
- ToolDispatcher mapping pilot (waits for Option B ratification)
- MissionRunner step mapping pilot (waits for Option A
  ratification)
- Update ARCHITECTURE_INDEX (this doc registers on commit; INDEX
  update is Part 1 close of the S1274 mission per its spec)

---

## 17. Appendix

### 17.1 Files inspected

Per this mission's evidence-gathering:

- `core/employees/jobs.py` — JobContract.authority contract
  definitions (verified counts unchanged since S1270)
- `core/employees/mission_runner.py:372-388` — Step dataclass
  (verified per S1270 F1)
- `core/employees/mission_runner.py:835-900` —
  `_emit_authority_contract_event` (S1264 warn-mode; per S1272
  spot-check)
- `core/employees/mission_runner.py:864-867` — AuthorityLevel
  shape counter (only runtime consumer; S1272 F1)
- `core/employees/mission_runner.py:1585-1591` —
  `_resolve_runs_as_user_id` (S1271 F3)
- `core/services/tool_dispatcher.py:210-229` —
  REMOVED_TOOL_ALIASES (13 entries verified)
- `core/services/tool_dispatcher.py:232-242` —
  GATEWAY_TOOLS (22 entries verified)
- `core/services/tool_dispatcher.py:687-720` —
  AssistantProfile gate (S1272 §7 precedent)
- `core/services/deliverable_aliases.py:33-36` —
  AGENT_NAME_ALIASES (2 entries verified)
- `core/services/pa_tool_schemas.py:24-5013` — 113 PA tool
  schemas (PLATFORM_INVENTORY count preserved)
- `core/services/event_bus.py:21-31` — EventStream enum (8
  streams)
- `core/services/human_attention_lifecycle.py:63-296` —
  auto-approve gate (S1272 §2 precedent)
- `core/llm_enforcer.py:139-262` — LLMEnforcer (S1272 F8
  fail-open precedent)
- `core/models_ops_runs.py` — OpsRun (no user FK per S1271 F1)
- `core/models_deliverables.py:31-142` — DeliverableType +
  PublishIntent + Deliverable.category
- `core/epa_handlers_tools.py:3873-3907` —
  WORKSPACE_AWARE_AGENTS (20 entries verified)

### 17.2 Docs inspected

- `docs/research/symbol_mapping_architecture.md` — 5 options
  A-E; 57 authority strings; 20 boundaries; 24 registries
- `docs/research/actor_identity_attribution_architecture.md` —
  3-role vocabulary; 22 attribution surfaces; F1/F6/F7/F11
- `docs/research/authority_enforcement_design_space.md` — 24
  enforcement inputs; 12 modes; 6 design options;
  15 anti-patterns; 15-prereq DAG
- `docs/research/governance_authority_evolution.md` — 4
  governance planes; 35 gates; F1/F2/F3/F4
- `docs/research/ARCHITECTURE_INDEX.md` v4
- `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication matrix
- `docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md` —
  warn-mode precedent + prereq #2 (≥14 days clean telemetry)

### 17.3 Counts verified

Per sub-agent 1 §D:
- 113 PA tool schemas (PLATFORM_INVENTORY anchor)
- 83 AGENT_MAP agents
- 4 employees, 4 jobs
- 57 unique authority strings / 68 total
- 4 AuthorityLevel members
- 13 REMOVED_TOOL_ALIASES (S1270 said 12 — drift corrected)
- 22 GATEWAY_TOOLS (S1270 said 23 — drift corrected)
- 2 AGENT_NAME_ALIASES
- 20 WORKSPACE_AWARE_AGENTS
- 30 prohibited_actions entries
- 8 EventBus streams
- 12 DeliverableType choices
- 3 PublishIntent enum
- 8 HAI status; 8 HAI decision; 4 HAI urgency

### 17.4 Conflicts resolved

- REMOVED_TOOL_ALIASES 12→13 (per direct verification)
- GATEWAY_TOOLS 23→22 (per direct verification)
- Runtime-anchor conflicts on PA tool count, mgmt commands,
  Celery tasks: PLATFORM_INVENTORY wins per DOC_LIFECYCLE §2c.

### 17.5 Unknowns

- Predicate context shape for Option D (S1270 §5.4)
- Audit retention window beyond `CELERY_TASK_EVENT_RETENTION_DAYS=30`
- Full producer inventory for E's ~15-20 sites (needs code
  audit)
- Whether AssistantProfile.get_allowed_tools should be
  registered as a canonical actor gate for E's evidence-only
  taxonomy (Rigby S1270 Q3 flag)
- Whether Rigby will pressure-test the recommendation and
  produce a modified variant

### 17.6 Verifier-loop corrections

Self-verifier pass identified and fixed:

- Initial draft had "recommended path" appearing in §9 comparative
  matrix column headers; corrected to "Verdict" per mission spec
  §9 required format.
- §1 executive summary initially listed 6 reasons for E; expanded
  to 7 after adding "directly unblocks 9 of 15 prereqs" point per
  Agent 5 §E.
- §10.6 initially only rejected C bundled; added explicit rejects
  for "ship D as v0" (predicate context UNKNOWN) and "ship
  nothing" (S1272 §11 prereq #1 blocks all downstream).
- §11 event shape initially collapsed executor + sponsor into
  single "actor" field per an early draft convenience — corrected
  to 3 separate fields per S1271 F11 discipline.
- §14 anti-patterns list numbered 21 items but §14.2 header said
  "3 mission-specific additions" — corrected header count to 6
  (items 16-21).

### 17.7 Rigby SIGN review record

**Verdict: SIGN-with-edits.** Rigby overall confidence:
**Medium**. Rigby recommendation: **Modify** — agrees with Option
E as v0 subject to 4 must-fix tightenings.

**Rigby's SIGN summary:**
- **Strongest argument:** risk posture + reversibility are
  correctly prioritized for the first recommendation doc.
  "Your framing nails the key asymmetry: E adds an observation
  substrate without introducing the pre-dispatch failure surface
  (and you explicitly name that surface as the thing the prereq
  DAG is trying to gate)." Phase plan §13.1 correctly constrains
  v0 to 3-5 producers first.
- **Weakest argument:** generalization claims around E overstated
  relative to the 2/4/14 coverage matrix. Folded.
- **Biggest risk:** E becomes "permanent cope" and delays
  real-time prevention where it's needed. Folded via §10.3.1
  graduation guardrail.
- **Most likely drift source:** producer omission + inconsistent
  inference rules for `action_class` (not schema drift). The
  more dangerous drift is "wrong but non-NULL action_class"
  (false confidence). NULL-count dashboards won't catch that;
  sampled truthing tests required. Folded via §12.1 new drift
  pattern.
- **What I got wrong per Rigby:** (a) overclaiming E's
  whole-platform generalization; (b) implying "audit chain
  covers all surfaces" without stating Fleet/WebSocket/Spider
  remain uncovered until instrumented; (c) two different v0
  sizes stated (exec summary "5 migrations + 20 sites" vs.
  §8.7 "top 3-5 producers"). All folded.

**Answers to my 10 pressure-test asks (all captured):**
1. E-as-v0 justified? YES with modifications. Not overweighting
   reversibility; correctly treating pre-dispatch enforcement as
   the hazardous move.
2. Any option unfairly rejected? Rejecting C standalone is fair.
   A/B/D language softened from "tertiary forever" to "deferred
   pending evidence" per Rigby refinement.
3. Is first move too big? As written, yes — v0 reframed via
   §8.7 refinement to "minimum audit-model set + 3-5 top
   producers" (not "5 migrations + 20 sites immediately").
4. Preserves MissionRunner stability? Mostly yes. Rigby refined
   claim to "no changes to runtime decision logic; only
   additive audit emission" — E DOES touch MissionRunner via
   new event emission, just not control flow.
5. Preserves JobContract stability? Yes; hard constraint held.
6. Generalizes beyond Employee OS? Generalization potential
   STRONG (end-state); v0 generalization narrow (2/4/14).
   Folded.
7. Too much annotation burden? Real but manageable relative to
   A/B/C. But wrong-but-non-NULL is higher-risk than
   producer-omission. Folded via §12.1.
8. Ignores Fleet/WebSocket/Spider? Not conceptually, but v0
   does NOT cover them without explicit producer emission.
   Pairing with Option B does NOT auto-cover Fleet/WebSocket/
   Spider either. Folded via §8.8 explicit statement.
9. Actor roles kept separate? Structurally yes.
   employee_handle vs. executor_actor distinction added per
   §11 must-fix #4.
10. What to change? 4 must-fix (all folded); 2 optional
   deferred (What-E-cannot-do box and graduation ladder
   diagram — §10.3 + §10.3.1 + §13 already cover material).

**4 must-fix edits folded:**
1. §8.8 tone alignment on generalization vs. matrix.
2. §10.3.1 catastrophic-action graduation guardrail added.
3. §12.1 non-NULL misclassification drift pattern added with
   3 detection approaches.
4. §11 employee_handle vs. executor_actor clarification.

**Refinements folded:**
- §8.7 smallest v0 reframed per Q3.
- A/B/D language softened from "tertiary forever" to
  "deferred pending evidence" per Q2.
- §10.6 alternative-paths section unchanged (already covers
  "ship nothing" + "ship D as v0" rejections).

**Rigby SIGN-clean on:**
- Risk posture + reversibility framing (strongest argument).
- Actor role separation structural work (3 fields in event
  shape).
- §14 anti-patterns (21-item catalog).
- §16 next-mission recommendation (Symbol Mapping Event
  Schema Design).

**Not re-invoked (optional deferred):**
- "What E cannot ever do" box — §10.3 already lists what E
  doesn't solve.
- Graduation ladder diagram — §10.3.1 trigger list + §13.1
  phase progression already articulate this in text form.
