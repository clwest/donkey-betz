---
title: "Group 1900 — Authority Enforcement Design Space — Parent Scoping (Phase 0)"
status: draft
session: 1900
child_slot: parent
domain_slug: authority_enforcement
research_group: 1900
mission_type: parent_scoping
date: 2026-07-04
authority: |
  Parent-arc scoping only. This doc enumerates the child-mission
  taxonomy that Group 1900 will execute, ratifies Chris's Q1–Q5
  decisions from S1900 open, and hands off to P1 (Actor Role
  Propagation Design) at S1901. It does NOT choose Symbol Mapping
  option (S1274 recommendation stands), does NOT pick Authority
  Enforcement design option A–F (that IS S1272 §14.3, a P2 child
  deliverable), does NOT design cross-plane composition rules
  (that IS the P3 child), does NOT ship implementation PRs or
  modify runtime code / migrations / MissionRunner /
  LLMEnforcer / KillSwitch reads. Per playbook §14.5 no-
  implementation rule + S1272 §14 authorial framing (evidence-
  only research; downstream design-with-Chris-gate).

  The three actor roles from S1271 §8.5 — executor_actor,
  sponsor_actor, principal_user — are preserved as separate
  primitives throughout Group 1900. Collapsing them is anti-
  pattern per S1271 F11.

  Scope hand-off from S1272 §14 is EXPLICIT:
  - §14.1 Symbol Mapping selection → SHIPPED as S1274 (Option E
    v0 recommended) + S1275 event schema design; NOT re-opened
    in Group 1900.
  - §14.2 Actor Role Propagation Design → Group 1900 P1
    (Cat A) child mission.
  - §14.3 Authority Enforcement Design Decision → Group 1900
    P2 (Cat B) child mission — THE enforce-mode design pick.
  - §14.4 Cross-Plane Composition Design → Group 1900 P3
    (Cat C) child mission (elevated from P2 deferred per Chris
    D-override q5=(b) taxonomy ratification 2026-07-04).
  - Group 1900 P4 (Cat F Adjacent / Separation Boundaries
    CONSOLIDATION) → not in S1272 §14; added per Rigby+Chris
    ratified pre-taxonomy card 2026-07-04 to mirror the
    proven Group 1700 F / Group 1800 F CONSOLIDATION pattern.
companion_docs:
  - docs/research/authority_enforcement_design_space.md
  - docs/research/symbol_mapping_architecture.md
  - docs/research/symbol_mapping_option_selection_design.md
  - docs/research/symbol_mapping_event_schema_design.md
  - docs/research/actor_identity_attribution_architecture.md
  - docs/research/governance_authority_evolution.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/research/domains/human_attention/1899_human_attention_canonical_summary.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
verifier_loop: |
  Parent scoping doc; no Explore-sub-agent sweeps performed (Group
  1900 subagent sweeps deferred to child audits per playbook
  §13 discipline). Load-bearing structural claims about the
  design space are inherited from S1272's verified findings
  (F1–F11) + S1274's Option E recommendation + S1275's event
  schema handoff.

  S1272 verification chain re-attested:
  (a) LLMEnforcer.enforce_real_ai at core/llm_enforcer.py:139;
      fail-open pattern at 237–238 (`except Exception: pass  #
      Never block LLM calls due to budget check errors`) —
      F8 precedent for enforce-mode fail-open policy default.
  (b) HumanAttentionLifecycleService._auto_approve_low_risk_items
      at core/services/human_attention_lifecycle.py:223;
      LOW_RISK_SOURCES = 5; AUTO_APPROVABLE_TYPES = 5 — P3
      Cross-Plane Composition consumer for authority × HAI
      auto-approve interaction question.
  (c) KillSwitch dispatch enforcement absence (5 read sites, all
      management/cleanup contexts; 0 pre-dispatch enforcement)
      — F2 KillSwitch full write path + zero enforcement readers
      is the P3 Cross-Plane Composition load-bearing gap for
      the authority × KillSwitch precedence question.
  (d) MissionRunner._emit_authority_contract_event at
      core/employees/mission_runner.py:835–900 — F1 sole
      AuthorityLevel enum consumer + shape-counter-not-decision-
      maker; primary P2 Authority Enforcement Design Decision
      input surface.
  (e) AuthorityLevel enum runtime consumers = 1 grep hit for
      `.EXECUTE.value / .OBSERVE.value / .RECOMMEND.value /
      .PROHIBITED.value` outside jobs.py contract declarations
      — F1 evidence base.

  Independent SIGN review by Rigby scheduled: **S1900 SIGN cycle
  1** on this parent scoping doc pre-commit per Chris Q3=(a)
  ratification 2026-07-04. D48 32nd arm anticipated CLEAN turn 1
  per MC-2 26-consecutive-fully-clean-arms sub-pattern
  CODIFICATION-CONFIRMED extension milestone (S1899 close).
---

# Session 1900 — Group 1900 Authority Enforcement Design Space Parent Scoping (Phase 0)

> **Anchor:** playbook §11.1 9-section parent scoping template SIXTH
> application (after S1400 Revenue + S1500 Sports + S1600 Content +
> S1700 Observability + S1800 HumanAttention). Group 1900 kicks off
> the SEVENTH Research OS domain arc.
>
> **Chris D-override:** default playbook §22 queue lean was Event /
> Integration / Runtime Architecture arc-open, inheriting the Group
> 1800 T0/Gate `R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES` handoff
> (source_kind enum + six-plane learning-surface event-emission gap
> + HAI event candidates). Chris D-overrode 2026-07-04 via line-
> select at `docs/research/platform_architecture_inventory.md:191`
> — the §9 STAGE 2 top-1 next-research recommendation per S1273
> (composes S1270 Symbol Mapping + S1271 Actor Identity + S1272
> Authority Enforcement Design Space). Rationale (Chris + Rigby
> concurrence 2026-07-04):
> - Governance / Authority is PARTIAL maturity + HIGH drift risk
>   per S1273 v2 Rigby review — the biggest architectural risk in
>   the library.
> - Four governance planes exist and don't compose (S1269 F1).
> - KillSwitch full write path + zero enforcement readers is a
>   dangerous false-sense-of-control failure mode during incidents
>   or autonomy escalation.
> - S1272 §14 already sequenced the natural Group 1900 child cut
>   (§14.2 + §14.3 + §14.4); Group 1900 executes that sequence
>   under Chris-gate.

---

## 1. Why Phase 0

Group 1900 sits at the **downstream execution end of a 7-doc
research chain** already in the library (S1268 → S1275). Phase 0
parent scoping is required for four reasons:

**(1) The S1272 §14 hand-off is explicit but under-scoped as a
single-mission take.**

S1272 §14 identified four next-research missions (§14.1, §14.2,
§14.3, §14.4). §14.1 shipped as S1274 (Option E v0 recommended)
+ S1275 (event schema). Three missions remain (§14.2 Actor Role
Propagation, §14.3 Authority Enforcement Design Decision, §14.4
Cross-Plane Composition). Each has distinct dependency shape,
distinct evidence surface, and distinct Chris-gate points. Rolling
them into one arc without child taxonomy would violate playbook
§13 no-blur discipline (research vs. design vs. implementation).

**(2) Group 1900 is the FIRST arc where the design-decision
mission (§14.3) is on-the-critical-path.**

S1272 §14.3 is where the platform actually **picks** an
enforcement design option A–F, picks mode set, picks precedence
policy, and produces the ADR bundle that a downstream S2000-range
implementation arc will consume. This is a Chris-gated decision
mission — not a research audit. The playbook §11.3 canonical
summary discipline (which every prior arc has closed with) does
not directly cover "design decision" as a child slot. Parent
scoping must name this explicitly so P2 doesn't inherit an
inappropriate template.

**(3) Cross-plane composition (§14.4) needs its own arc-level
scoping, not P2-nested.**

S1272 §7.5 enumerates 8 cross-plane composition questions (autonomy
× authority priority, authority × budget layering order,
RECOMMEND-triggered HAI auto-creation, authority × KillSwitch
precedence, freeze × HAI auto-approve, etc.). These are load-
bearing for enforce-mode correctness — but they cut across four
governance planes and 2000+ lines of S1272 evidence. Folding them
into P2's decision doc would either (a) bloat P2 to 3000+ lines or
(b) short-change composition. P3 as its own child is the honest
cut.

**(4) The domain surface (Authority Enforcement) touches every
platform plane; CONSOLIDATION is load-bearing.**

Prior arcs proved this pattern: Group 1700 Cat F CONSOLIDATION
(Observability × Adjacent domains) caught retention discipline
drift + spine posture gaps that per-child audits missed. Group
1800 Cat F CONSOLIDATION caught duplicate-file collisions across
sibling children. Authority Enforcement crosses Memory / Content /
Sports / HAI / Employee OS / Frontend / API / Discord surfaces —
a CONSOLIDATION child (P4) is the mechanism that prevents
"accidental re-coupling" from creeping into the design-decision
posture at P2.

---

## 2. What existing inventory already tells us

### 2.1 Prior research chain (S1268 → S1275)

| Session | Doc | Deliverable | Status |
|---|---|---|---|
| S1268 | `docs/research/` (whole-platform intake — Chris audit) | 4-doc research library scaffolding | Shipped |
| S1269 | `governance_authority_evolution.md` | Governance/authority evolution audit; F1 = 4 planes don't compose; F2 = KillSwitch write-only; F3 = no gate reads `JobContract.authority` | Shipped |
| S1270 | `symbol_mapping_architecture.md` | 5 mapping options (A/B/C/D/E) enumerated; F2 = zero runtime surfaces carry `action_class` vocabulary; F6 = 3 structural drop boundaries | Shipped |
| S1271 | `actor_identity_attribution_architecture.md` | 3 actor roles (executor_actor / sponsor_actor / principal_user) defined; 22 attribution surfaces; F6 = 3 drop boundaries; F11 = never collapse the three roles | Shipped |
| S1272 | `authority_enforcement_design_space.md` | 2000+ lines; 20 boundaries × 12 modes matrix (204 cells / ~156 mechanical compatibilities); 6 design options A–F; 33 historical incidents; 15 anti-patterns; 15 prerequisites DAG; **§14 4-mission next-research recommendation** | Shipped (SIGN-with-edits, Medium confidence) |
| S1273 | `platform_architecture_inventory.md` | 32 domains × maturity/coverage matrix; **§9 STAGE 2 top-1 recommendation = Authority Enforcement Design Space** — the line Chris selected at :191 to trigger Group 1900 | Shipped (SIGN-with-edits per v2 Rigby review) |
| S1274 | `symbol_mapping_option_selection_design.md` | S1272 §14.1 execution; 5 options deep-evaluated; **Option E (evidence-only) recommended v0** with 4 must-fix Rigby SIGN edits folded | Shipped (SIGN-with-edits, Medium confidence) |
| S1275 | `symbol_mapping_event_schema_design.md` | Event schema for Option E; enforcement-adjacent event shapes | Shipped |

**Total prior investment:** 8 research docs, ~10,000+ lines of
evidence, 3 SIGN-with-edits cycles at Medium confidence. Group
1900 is the follow-on that turns evidence into design decisions.

### 2.2 Runtime state at S1900 open (attested via S1272 verifier loop)

**F1 — AuthorityLevel is policy metadata today, not enforcement
metadata.** `AuthorityLevel` enum at
`core/employees/jobs.py:41–52` has 4 members (OBSERVE, RECOMMEND,
EXECUTE, PROHIBITED). Runtime consumers = **1**:
`core/employees/mission_runner.py:864–867` accumulates
`level_counts` by iterating `authority.items()` — a **shape-
counter, not a decision-maker**. Zero code paths branch on a
specific level value. Any Group 1900 P2 design must introduce
the level → decision binding from scratch.

**F2 — 8 of 12 enforcement modes have production analogs; 4
don't.** Per S1272 §4 + §H:
- **With production analog (8):** warn-mode, soft-fail, hard-
  block, require-approval, pause-employee, freeze-platform,
  retro-audit, observe-only.
- **Without production analog (4):** defer-mission, freeze-queue,
  degrade-mission-evidence at step scope, retro-audit at
  authority-violation scope. Group 1900 P2 design pick must
  either restrict to the 8-mode subset or design new primitives
  for the 4-mode gap.

**F3 — Every existing enforcement gate uses a different
vocabulary; none read `JobContract.authority`.** Per S1272 F3 +
S1269 F3:
- `AssistantProfile.allowed_tools` — per-*human* scope.
- `LLMEnforcer.check_budget` — per-*platform* scope (task_type
  scoped + agent exempt list).
- `GovernanceState.mode='freeze'` — per-platform scope (declared
  per-agent/desk scopes never read).
- `messaging_tool.send_message` guard — per-tool scope.
- DRF `IsAuthenticated` / `IsAdminUser` — per-user-role.
Authority enforcement is a NEW vocabulary that does not inherit
precedent semantics. P2 design must decide how to bridge from
Symbol Mapping Option E's evidence-only track to actual decision
metadata.

**F4 — 4 governance planes do not compose; adding authority is a
5th surface.** Per S1269 F1 + S1272 F4: only **1 cross-plane
composition point** exists today — autonomy → budget one-way
sync at `governance.py:2285–2322`. S1272 §7.5 enumerates **8 new
composition questions** authority enforcement would introduce;
none have current-state answers. P3 Cross-Plane Composition is
where these get resolved.

**F5 — KillSwitch full write path + zero enforcement readers.**
Per S1272 verifier loop (c): KillSwitch reads exist at 5 sites
(`intelligence.py:1569,1717`; `governance.py:2192,2370,2508`) —
but ALL are management/cleanup contexts (status listing,
get-for-deactivate, expire loop, TTL cleanup). **NONE are
dispatch enforcement.** S1269 F2 "KillSwitch is write-only"
stands. This is the load-bearing example for the "dangerous
false-sense-of-control" failure mode — visible affordance without
enforcement is worse than no affordance. P2 + P3 must resolve
whether Group 1900 recommends adding KillSwitch enforcement
readers as part of the initial design pick or defers it.

**F6 — LLMEnforcer's fail-open pattern is the precedent for
enforce-mode fault tolerance.** Per S1272 F8 + verifier loop (a):
`core/llm_enforcer.py:237–238` — `except Exception: pass  #
Never block LLM calls due to budget check errors`. The budget
gate — closest existing analog to authority enforcement — fails
open on internal error. P2 design must decide fail-open vs.
fail-closed per mode and cite rationale. Default recommendation
from S1272 F8 is fail-open matching precedent, but S1272 does
not choose.

**F7 — HAI auto-approve is the load-bearing composition target.**
Per S1272 verifier loop (b) + F4:
`core/services/human_attention_lifecycle.py:223`
`_auto_approve_low_risk_items` beat task auto-closes items whose
source ∈ `LOW_RISK_SOURCES` = 5 (spider_insight, content_review,
blog_review, trend_analysis, observation) AND type ∈
`AUTO_APPROVABLE_TYPES` = 5 (content, insight, observation,
analysis, suggestion). Question for P3 Cross-Plane Composition:
does an authority RECOMMEND-triggered HAI item get auto-approved
if source ∈ LOW_RISK_SOURCES? Does an authority PROHIBITED-
triggered HAI item bypass auto-approve? Current answer = auto-
approve does not read authority at all.

**F8 — Symbol Mapping Option E enables only 4 of 12 modes; A/B/C/D
enable all 12.** Per S1272 F9 + S1274 evidence: S1274 recommended
Option E v0 (evidence-only, sponsor_actor via extended audit
models, mechanically carries all 3 roles). Enforce-mode design
(P2) inherits: only observe-only, warn-mode, degrade-evidence,
retro-audit are mechanically compatible with Option E v0. The 8
remaining modes (soft-fail, hard-block, require-approval, pause-
employee, freeze-platform, defer-mission, freeze-queue, retro-
audit@authority-scope) require future migration to Option A/B/C/D
OR a step-declaration layer added atop Option E. P2 must
explicitly acknowledge this constraint and either (a) restrict
scope to the 4-mode E-compatible subset, (b) propose a migration
sequence to A/B/C/D under a future arc, or (c) propose a hybrid
(evidence + step-declaration overlay).

**F9 — Actor role composition determines mode preconditions.**
Per S1272 F10: modes requiring only executor_actor (warn-mode,
soft-fail, degrade-evidence) can ship without full actor
resolution. Modes requiring sponsor_actor (hard-block for
delegation chains, pause-employee) or all three (require-
approval, retro-audit) presuppose S1271's role vocabulary is
fully wired. **Enforcement mode selection is downstream of Actor
Attribution implementation.** P1 (Actor Role Propagation Design)
is therefore the P2 prereq — not just a parallel workstream.

**F10 — 15 prerequisites form a DAG, not a checklist.** Per
S1272 F11 + §11.2: critical path is Symbol Mapping → Evidence
Schema → Violation Event Schema → Fallback → Enforcement Layer →
Test Coverage + Human Review → Rollback → Per-Employee Opt-In →
Metrics Window → Trust Threshold + False-Positive Threshold. Of
the 15, **zero are fully satisfied** at S1900 open; most are
partial. P2 design pick must sequence these; P3 Cross-Plane
Composition owns prereq #14; other prereqs distribute across
P1/P2 per S1272 §14 layering.

### 2.3 What we already know from S1272 §9 (the 6 design options)

**Option A — MissionRunner-centered enforcement.** Boundaries
4/5/6 (mission entry, preflight, before each Step.fn). Reuses
`MissionRunnerConfig.job_contract` + `authority_contract_observed`
event pattern. Requires Symbol Mapping Option A/C (step declares
`action_classes_invoked`) or Option D (central registry). Misses
tool-dispatch path (Boundary 2), Celery outside missions, ORM
direct, HTTP endpoints. Compatible with Employee OS. Failure mode:
signal-quality maintenance burden — step author must accurately
declare `action_classes_invoked` at code time + keep sync
forever.

**Option B — ToolDispatcher-centered enforcement.** Boundary 2
(ToolDispatcher.execute() entry) + Boundary 3 (inside PA tool
handler). Reuses `AssistantProfile.get_allowed_tools()` at
`tool_dispatcher.py:687–720`. Requires tool → action_class
registry. Misses MissionRunner steps outside tool dispatch,
Celery outside tool dispatch, ORM direct, HTTP endpoints.
Failure mode: tool-schema drift — every new tool must be
registered + drift-audited.

**Option C — Middleware / decorator enforcement.** Layer around
runtime call points via `@requires_action_class(...)` decorator.
Reuses no existing gate structure. Compatible with any Symbol
Mapping option. Requires decorator discipline across ~150+
runtime call sites. Failure mode: decorator drift — new call
sites forget decorator; existing sites drift.

**Option D — Central authority service enforcement.** New
`AuthorityService.check(actor, action_class, context)` service;
all boundaries route to it. Reuses no existing gate structure.
Compatible with any Symbol Mapping option. Highest reuse
footprint (single decision point). Failure mode: hot-path
latency; single point of failure.

**Option E — Evidence-only enforcement.** No pre-block; audit
after the fact. Reuses `OpsRunEvent` + `LLMCallEvent` +
`ToolCallRecord`. Compatible with S1274's recommended Option E
Symbol Mapping. Enables only 4 modes (observe / warn / degrade
/ retro-audit). Failure mode: no prevention — violations happen
in prod before detection.

**Option F — Hybrid: MissionRunner-primary + ToolDispatcher-
secondary + Evidence-tertiary.** Combines A + B + E in layered
coverage. Reuses all three gate structures. Highest coverage.
Failure mode: **policy ossification / precedence lock-in** —
codified precedence contracts retroactively invalidate audit
interpretations if changed (Rigby S1272 SIGN edit).

Group 1900 P2 (Authority Enforcement Design Decision) is where
Chris picks ONE of A/B/C/D/E/F, picks mode set, picks precedence
policy. P2 is a design decision doc, NOT a research audit.

### 2.4 What we already know from S1274 (Option E v0 recommendation)

S1274 recommended **Option E (evidence-only) as Symbol Mapping
v0**. Key implications for Group 1900:
- Options A/B/C/D remain future migration targets under S1274 §11
  graduation guardrails (4 telemetry triggers force Chris
  decision within 30 days).
- Option E mechanically carries all 3 actor roles IF audit models
  extended with sponsor_actor field.
- Coverage-vs-drift trade at v0 = narrow coverage (2 boundary
  YES / 4 PARTIAL / 14 NO per S1274 §8.8 tightening) with
  MEDIUM drift risk. Fleet / WebSocket / Spider excluded until
  instrumented.

Group 1900 P2 must design the enforcement layer that consumes
Option E's evidence surface. Option F hybrid remains a candidate
for P2 (combines E as evidence-tertiary with MissionRunner-
primary and ToolDispatcher-secondary).

---

## 3. Candidate subdomain taxonomy

### 3.1 Pre-taxonomy card (routed via Rigby 2026-07-04)

Per Chris D-override Q4=(b) at S1900 open (`agree all → (b/a/a/b)`),
a pre-taxonomy card was routed via Rigby on the fresh Group 1900
arc pin `pa-2bd1613ce2bd4a9c` before this parent scoping doc was
drafted. Card presented three candidate taxonomies with my lean +
Rigby lean.

### 3.2 Option (a) — Minimal 3-child (faithful to S1272 §14)

**Structure:**
- P1 = Actor Role Propagation Design (S1272 §14.2 both layers)
- P2 = Authority Enforcement Design Decision (S1272 §14.3)
- P3 = Cross-Plane Composition Design (S1272 §14.4)
- xx99 = canonical summary
- Runtime target: ~5 sessions.

**Pros:**
- Directly maps to S1272 §14 authorial recommendation.
- Minimal scope; every child directly closes a §14 rec.
- Playbook §11.1 template consumers = 3 child audits + 1 xx99.

**Cons:**
- Drops the proven CONSOLIDATION pattern from Group 1700 F / Group
  1800 F that caught boundary drift + separation violations.
- Authority Enforcement crosses every platform plane; without
  CONSOLIDATION, accidental re-coupling to Memory / Content /
  Sports / HAI / Employee OS / Frontend / API / Discord surfaces
  is a known failure mode.

### 3.3 Option (b) — 4-child with CONSOLIDATION (Chris-ratified)

**Structure:**
- P1 = Actor Role Propagation Design (S1272 §14.2 both layers)
- P2 = Authority Enforcement Design Decision (S1272 §14.3 — pick
  option A–F + modes + precedence)
- P3 = Cross-Plane Composition Design (S1272 §14.4)
- P4 = Cat F Adjacent / Separation Boundaries CONSOLIDATION
  (mirror Group 1700/1800 pattern; separates authority from
  Memory / Content / Sports / HAI / Employee OS / Frontend / API
  / Discord planes)
- xx99 = canonical summary
- Runtime target: ~6 sessions.

**Pros:**
- Respects S1272 authorial intent (3 real recs, not artificial
  split).
- Adds only the proven CONSOLIDATION pattern (SECOND consecutive
  arc application after Group 1700 / Group 1800).
- Playbook §11.2 20-section child template TWELFTH → FIFTEENTH
  consecutive application observation opportunity — MC-5
  CODIFICATION-READY promotion (S1899 close) gets 4 additional
  data points toward CODIFICATION-CONFIRMED.

**Cons:**
- Does NOT observe MC-4 (arc-pin routing durable-by-6th-
  application under 6-child arcs); Group 1900 as 4-child does
  not qualify.
- Runtime target 1 session longer than Option (a).

### 3.4 Option (c) — 6-child for MC-4 / MC-5 durability observation

**Structure:**
- P1 = Cat A — Actor Role Propagation Layer i (schema + contract;
  parallel-safe per S1272 §14.2)
- P2 = Cat B — Actor Role Propagation Layer ii (implementation
  across 20 boundaries)
- P3 = Cat C — Boundary × Mode selection matrix reduction (S1272
  §3+§4 → decision-grade cells)
- P4 = Cat D — AuthorityLevel semantics + precedence resolution
  (S1272 §5 4×4 interpretations)
- P5 = Cat E — Cross-Plane Composition (S1272 §7 + §14.4)
- P6 = Cat F — Adjacent / Separation Boundaries CONSOLIDATION
- xx99 = canonical summary
- Runtime target: ~8 sessions.

**Pros:**
- Creates MC-4 (arc-pin routing durable-by-6th-application)
  SEVENTH-consecutive-application observation → CODIFICATION-
  CONFIRMED candidate at Group 1900 close.
- Creates MC-5 (§11.2 20-section child template) TWELFTH → FIFTEENTH
  consecutive-application observation.
- Group 1800 precedent: 6-child arcs are library-native shape.

**Cons:**
- S1272 §14.3 authorial framing treats "pick option A–F + modes +
  precedence" as a **single design decision**. Splitting it across
  P3 + P4 + P5 forces an artificial break in the decision surface.
- Cat C / D / E become thin without the others as context — cross-
  child dependency overhead spikes.
- **Arc-shaping for MC observation is meta-methodology-first
  rather than scope-first** — violates playbook §14.5 spirit
  (research/design shape driven by domain, not by measurement
  needs).

### 3.5 Chris ratification

**Chris ratified Q5 = (b)** 2026-07-04 via Rigby (Chat UI) — the
4-child with CONSOLIDATION structure. Rigby concurred with my
lean on all three considerations:
- MC-4 / MC-5 durability observation value does not outweigh S1272
  §14 authorial framing.
- CONSOLIDATION is load-bearing at 4-child (authority crosses every
  plane; consolidation prevents accidental re-coupling).
- No missing S1272 §14 dependencies require the deeper (c) split.

### 3.6 Final child slot definitions (Chris-locked 2026-07-04)

Per Q5=(b) ratification, Group 1900 will execute this child
sequence:

| Slot | Session | Deliverable | Type | Prereq |
|---|---|---|---|---|
| Parent | S1900 | This doc | Parent scoping (Phase 0) | — |
| **P1** | S1901 | **Actor Role Propagation Design** — S1272 §14.2 both layers (schema + contract, implementation across 20 boundaries) | Research + Design | S1271 §8.5 (shipped); S1274 Option E (shipped) |
| **P2** | S1902 | **Authority Enforcement Design Decision** — S1272 §14.3 (pick option A–F + modes + precedence) | Chris-gated Design Decision | P1 shipped; S1272 §11 15-prereq DAG partial |
| **P3** | S1903 | **Cross-Plane Composition Design** — S1272 §14.4 (8 composition questions + plane precedence policy) | Research + Design | P2 shipped; S1269 F1 (autonomy × budget precedent) |
| **P4** | S1904 | **Cat F Adjacent / Separation Boundaries CONSOLIDATION** — mirror Group 1700/1800 F pattern | Research audit + consolidation | P1 + P2 + P3 shipped |
| **xx99** | S1999 | **Canonical summary** — playbook §11.3 12-section SEVENTH application + §11.3 §10 meta-methodology SEVENTH application | Canonical summary | P1 + P2 + P3 + P4 shipped |

**Sequencing note:** children are sequential, not parallel. P2's
design decision consumes P1's Actor Role Propagation outcome.
P3's Cross-Plane Composition consumes P2's enforcement mode +
option pick. P4's CONSOLIDATION consumes P1 + P2 + P3.

**Session numbering note:** P1–P4 use S1901–S1904 per playbook §4
intra-range convention. xx99 canonical summary at S1999. Sessions
S1905–S1998 remain buffer per playbook §4.6 xx99 buffer discipline
in case a child needs mid-arc SIGN re-work, verifier-loop cycle,
or a spawned sibling audit.

---

## 4. Parent-vs-single recommendation

**Recommendation: PARENT (multi-child arc).**

Group 1900 is the SEVENTH parent-arc application of the playbook
§11.1 template. Justification:

**(1) Deliverable diversity.** S1272 §14 identifies four distinct
mission-type deliverables:
- §14.2 = Research + Design (Actor Role Propagation contract).
- §14.3 = Chris-gated Design Decision (pick A–F + modes +
  precedence — this is a DECISION, not an audit).
- §14.4 = Research + Design (Cross-Plane Composition policy).
- §14 (implicit CONSOLIDATION) = Research audit consolidation.

Rolling these into a single doc would either (a) blur research/
design boundaries per playbook §13 or (b) produce a 4000+ line
single deliverable that cannot be reviewed as a coherent unit.

**(2) Chris-gate cadence.** P2 is Chris-gated (design decision).
P1, P3, P4 have Rigby SIGN + Chris ratification at close but do
not require Chris design-picks. Parent structure lets P2 receive
its own dedicated Chris-gate cycle without holding P1 hostage.

**(3) Sequential dependencies.** F9 (actor role composition
determines mode preconditions) makes P1 the strict prereq for
P2. P3's cross-plane composition consumes P2's mode pick. Parent
structure with sequential children matches the dependency shape.

**(4) Verifier-loop cadence per playbook §11.1.** MC-1 (verifier-
loop REQUIRED) CODIFICATION-CONFIRMED at S1899 close means every
child audit must run its own verifier loop. Parent arc structure
gives each child its own verifier-loop scope + SIGN gate.

**(5) Prior arc precedent.** Groups 1400 / 1500 / 1600 / 1700 /
1800 all ran as multi-child arcs. No single-doc precedent exists
for a topic this cross-cutting. Group 1900 mirrors the precedent.

### Runtime target

Runtime target: **6 sessions** (S1900 parent + S1901 P1 + S1902 P2
+ S1903 P3 + S1904 P4 + S1999 xx99). Actual runtime may extend
1–2 sessions if:
- SIGN-with-edits at a child requires more than one fold cycle.
- P2's design decision spawns a sub-decision (e.g., "before we
  can pick between Option A and Option F, we need a scoping doc
  on hybrid precedence policy").
- P3's 8 composition questions surface a load-bearing gap that
  requires a Cat E-analog spawn.

Runtime cap: **8 sessions** (S1900 + 6 child slots + xx99).
Beyond 8 sessions, escalate to Chris for re-scoping.

---

## 5. Child mission sequence (Chris-locked 2026-07-04)

### 5.1 P1 — Actor Role Propagation Design (S1901)

**Slot:** Cat A (per playbook §11.2 child audit template).

**Scope:** S1272 §14.2 both layers.

**Layer i — Role schema + propagation contract:**
- Define what each of `executor_actor / sponsor_actor /
  principal_user` means across boundary transitions.
- Specify the propagation contract:
  - Context dict shape.
  - Thread-local vs. explicit param semantics.
  - Defaults on gap (when a role is unknown at a boundary).
  - Failure semantics (drop the actor / raise / default).
- **Parallel-safe with S1274 Symbol Mapping Option E** (no
  dependency on which mapping option is chosen; Option E's
  audit-model extension pattern is compatible with all 3 roles).

**Layer ii — Implementation across 20 boundaries:**
- Wire propagation through S1272 §3's 20 candidate boundaries
  (HTTP entry, ToolDispatcher entry, PA tool handler,
  MissionRunner entry, preflight, before-step, Celery ingress,
  ORM signal handler, WebSocket consumer, Fleet API, Spider run,
  ...).
- Close S1271 F6 drop boundaries wherever possible (structural
  drop points may remain but must be documented explicitly).
- Deliverable: per-boundary propagation contract + drop-boundary
  register.

**Deliverable:** `docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md` per playbook §11.2 20-section child template.

**Prereqs:** S1271 §8.5 role vocabulary (shipped); S1274 Option E
recommendation (shipped for Layer i compatibility check).

**Rigby SIGN cadence:** Cycle 1 pre-commit per playbook §15
stage-table child-audit row.

**Chris-gate:** Ratification at close (not design pick — P1 is
research + design, not decision).

**Runtime target:** 1 session.

### 5.2 P2 — Authority Enforcement Design Decision (S1902)

**Slot:** Cat B.

**Scope:** S1272 §14.3 — the enforce-mode design pick.

**Deliverables (all in a single decision doc):**
- Pick one (or hybrid) of Options A / B / C / D / E / F (§2.3).
- Pick mode subset from S1272 §4's 12 modes (with F8 constraint:
  Option E enables only 4 of 12 modes).
- Pick precedence policy for authority × KillSwitch × freeze ×
  HAI auto-approve interactions (partial; P3 finalizes cross-
  plane composition rules).
- Pick fail-open vs. fail-closed default (F6 precedent).
- Design the level → decision binding (F1: currently none exists).
- Design per-employee opt-in mechanism (S1272 §11 prereq #10).
- Design rollback behavior (warn ← enforce; S1272 §11 prereq #6).
- Design metrics window + trust threshold + false-positive
  threshold policy (S1272 §11 prereqs #11–#13).

**Enforcement Binding Points map (required artifact per Rigby S1900 SIGN cycle 1 Q4 fold):** P2 must enumerate — as a first-class deliverable — which boundary/read-site(s) enforce authority (or intentionally do not), the evaluation order vs. KillSwitch / budget / freeze / HAI / mission governance, and fail-open vs. fail-closed posture per site. Rationale: without named binding points, precedence claims in the design decision are theoretical — contradictory behavior depends on which component happens to check first (or not at all). P3 cross-plane composition + P4 Cat F CONSOLIDATION are attachable only if P2 gives them named binding points. Deliverable shape: table of `(boundary_id, read_site, evaluation_order, other_gate_precedence, fail_posture)` per S1272 §3 20-boundary inventory.

**Migration-recommendation clarifier (per Rigby S1900 SIGN cycle 1 Q1+Q3(a) fold):** Any Option E → (A/B/C/D) or hybrid pathway P2 proposes is a **recommendation for Chris-gated decisioning** and remains governed by S1274 §11 graduation triggers; P2 does not itself override or re-litigate the S1274 Option E v0 selection. All implementation of such a migration is post-arc execution.

**Deliverable:** `docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md` per playbook §11.2 template modified for design-decision framing (§11.2 §7 Runtime Flows → §7 Decision-Grade Options Analysis; §11.2 §12 Research Coverage → §12 Decision Rationale + Alternatives Rejected; §11.2 §17 Duplicate or Overlapping Systems → §17 Enforcement Binding Points map).

**Prereqs:** P1 shipped (Actor Role Propagation contract).

**Rigby SIGN cadence:** Cycle 1 pre-commit + Cycle 2 post-Chris-
gate to pressure-test the decision doc.

**Chris-gate:** Multi-verdict at close — D8N series covering each
of the design picks above. This is where Chris actually picks the
enforcement design.

**Runtime target:** 1–2 sessions (may extend if Chris's design
pick spawns follow-on sub-decisions).

### 5.3 P3 — Cross-Plane Composition Design (S1903)

**Slot:** Cat C.

**Scope:** S1272 §14.4 — 8 cross-plane composition questions +
plane precedence policy.

**Deliverables:**
- Answer each of the 8 S1272 §7.5 questions with a designed
  resolution:
  1. authority × autonomy priority (which plane wins when they
     disagree?).
  2. authority × budget layering order (does budget freeze
     precede authority check or vice versa?).
  3. RECOMMEND-triggered HAI auto-creation (does an authority
     RECOMMEND emit an HAI item automatically?).
  4. authority × KillSwitch precedence (does KillSwitch bypass
     authority enforcement or vice versa?).
  5. freeze × HAI auto-approve (does platform freeze block HAI
     auto-approve?).
  6. authority × HumanAttentionLifecycle.LOW_RISK_SOURCES × HAI
     auto-approve (F7 evidence).
  7. authority × Employee OS MissionRunner enforcement toggle
     composition.
  8. authority × Discord command dispatch enforcement (or
     documented deferral).
- Design plane precedence policy: canonical resolution order
  when planes disagree.
- Add KillSwitch enforcement reader design if P2 recommended
  it; otherwise document deferral rationale.

**Deliverable:** `docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md` per playbook §11.2 template.

**Prereqs:** P2 shipped (mode + option pick).

**Rigby SIGN cadence:** Cycle 1 pre-commit.

**Chris-gate:** Ratification at close.

**Runtime target:** 1 session.

### 5.4 P4 — Cat F Adjacent / Separation Boundaries CONSOLIDATION (S1904)

**Slot:** Cat F CONSOLIDATION (mirror Group 1700 Cat F + Group
1800 Cat F).

**Scope:** Consolidate the boundary separation posture between
Authority Enforcement and every adjacent domain surface.

**Scope precision (per Rigby S1900 SIGN cycle 1 Q3(b) fold):**
This is a **separation-boundary posture audit (interface + seam
audit)** — a review of interfaces, seams, propagation drop
points, enforcement read-sites, and precedence joins between
Authority Enforcement and each adjacent domain. It is **NOT** an
audit of each adjacent domain's internal correctness or
implementation quality. Prior arc audits (Group 1300 Memory, Group
1500 Sports, Group 1600 Content, Group 1800 HAI, etc.) own their
respective internal-correctness verdicts. Group 1900 P4 audits the
seams between authority and those domains.

**P4 checks / P4 does NOT check (per Rigby S1900 SIGN cycle 1
Q3(b) optional extra-hardening):**

| P4 CHECKS | P4 does NOT check |
|---|---|
| Interface + seam between authority and each adjacent domain | Internal correctness of any adjacent domain |
| Propagation drop points where actor-role signals fall through | Domain-owned implementation quality |
| Enforcement read-sites in adjacent domains + their precedence joins | Adjacent domain's own governance / autonomy / budget layers |
| Duplicate authority-check-adjacent primitives across domains | Adjacent domain's test coverage or SLO posture |
| Gap points where a domain assumes an authority check ran but P2's design doesn't cover it | Domain-specific ADR bundles or T-slot execution items |
| Separation-boundary policy (which decisions owned by 1900 vs delegated to domain's governance layer) | Anything in scope of Group 1300/1500/1600/1800 post-arc T-slot queues |

**Deliverables:**
- **Separation-boundary posture audit (interface + seam audit)**
  for each plane authority touches: Memory (Group 1300) / Content
  (Group 1600) / Sports (Group 1500) / HAI (Group 1800) / Employee
  OS / Frontend / API / Discord.
- Register "propagation contract touchpoints" — where does the
  actor-role propagation from P1 cross into an adjacent
  domain's concern? Are there duplicate authority checks? Are
  there gap points where a domain assumes an authority check
  ran but P2's design doesn't cover it?
- Register "separation boundary posture" — which authority
  decisions are owned by Group 1900 vs. delegated to a domain's
  own governance layer?
- Follow-on queue candidates for post-arc T-slot execution.

**Deliverable:** `docs/research/domains/authority_enforcement/1904_authority_enforcement_cat_f_adjacent_separation_boundaries_child_audit.md` per playbook §11.2 template + §16 CONSOLIDATION shape from S1806 Group 1800 Cat F precedent.

**Prereqs:** P1 + P2 + P3 shipped.

**Rigby SIGN cadence:** Cycle 1 pre-commit.

**Chris-gate:** Ratification at close.

**Runtime target:** 1 session.

### 5.5 xx99 — Canonical summary (S1999)

**Slot:** xx99 canonical summary.

**Scope:** Playbook §11.3 12-section canonical-summary template
SEVENTH application + §11.3 §10 meta-methodology template
SEVENTH application.

**Deliverables (all 12 sections + Appendix):**
- §1 Executive Summary
- §2 What This Arc Answered
- §3 Consolidated Domain Shape
- §4 Cross-Cutting Patterns
- §5 Resolved Contradictions
- §6 Unresolved Unknowns
- §7 Anchor-Update Recommendations (PLATFORM_WHAT_IT_IS + PLATFORM_INVENTORY + CLAUDE.md as needed)
- §8 Follow-On Research Queue (T0/Gate + T1 + T2 + T3 tiered)
- §9 Cross-Links to Delegated Arcs
- §10 What This Research Taught Us About How to Do Research
  (SEVENTH meta-methodology application; MC-1/MC-2/MC-3
  CODIFICATION-CONFIRMED as of S1899; MC-4/MC-5 CODIFICATION-
  READY promotion candidates; MC-6/MC-7/MC-8/MC-9 candidates).
- §11 Arc Change Log
- §12 Appendix — Provenance

**Deliverable:** `docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md`.

**Prereqs:** P1 + P2 + P3 + P4 shipped.

**Rigby SIGN cadence:** Cycle 1 single-batch 4-question routed
via arc pin `pa-2bd1613ce2bd4a9c` per playbook §15 stage-table
canonical-summary row + §16 arc-pin durable-by-sixth-application
(CODIFICATION-READY at S1899 close per MC-4) → SEVENTH-
consecutive-application observation at Group 1900 close.

**Chris-gate:** Ratification at close + arc pin retirement via
`session_tool.retire` per playbook §16 arc-close discipline.

**Runtime target:** 1 session.

---

## 6. Parked candidate issues

Candidates considered for children but explicitly parked. These
may re-surface as post-arc T-slot execution items or as future
research arcs.

### 6.1 Parked from Option (c) 6-child taxonomy

- **Cat C — Boundary × Mode selection matrix reduction as
  standalone child.** Parked into P2 § "Decision-Grade Options
  Analysis". Rationale: §14.3 authorial framing treats matrix
  reduction as part of the single design decision; splitting
  would fragment.
- **Cat D — AuthorityLevel semantics + precedence resolution as
  standalone child.** Parked into P2 § "Level → Decision Binding
  Design". Rationale: level semantics are inseparable from mode
  pick.

### 6.2 Parked from S1272 §14.5 explicitly-NOT-recommended

- **Trust Propagation** (ARCHITECTURE_INDEX §5.3) — waits for
  P2 (§14.3) close per S1272 §14.5.
- **Employee Delegation Design** (ARCHITECTURE_INDEX §5.5) —
  waits for P2 close per S1272 §14.5.
- **Memory Architecture** (ARCHITECTURE_INDEX §5.4) — waits for
  P2 close per S1272 §14.5.

### 6.3 Parked from S1272 §11 15-prereq DAG

- **Prereq #14 Cross-plane composition** — becomes P3.
- **Prereq #15 Enforcement scope per action vs. per-employee** —
  becomes P2 sub-deliverable.
- Other 13 prereqs distribute across P1 + P2 per S1272 §11.2 DAG.

### 6.4 Parked from Group 1800 T0/Gate handoff

- **R.HAI.LEARNING-PLANE-CONTRACT-ADR** (joint Group 1300 +
  1800) — touches authority read-side enforcement but is
  primarily a HAI + Memory ADR. Group 1900 P3 references it
  where relevant but does not own it.
- **R.HAI.SOURCE-KIND-ENUM-ADR** — joint schema change; may
  cross-reference Actor Role §14.2 propagation but is not
  Group 1900 scope.
- **R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES** — the deferred
  Group 1900 Event Architecture arc queue lean. Remains parked
  for a future Group 2000 (or later) Event / Integration arc
  per playbook §22 D-override precedent.

### 6.5 Parked as post-arc execution items

Not researched by Group 1900 — flagged for post-arc T-slot
execution once P2 design pick is Chris-gated:
- Implementation PRs for chosen enforcement layer.
- LLMEnforcer read-side integration.
- KillSwitch enforcement reader addition (if P2 recommends).
- MissionRunner `_emit_authority_contract_event` graduation
  from shape-counter to decision-maker (if P2 recommends).
- Per-employee `AIEmployee.enforce_authority_mode` toggle
  implementation (if P2 recommends).
- Migration from Symbol Mapping Option E to Option A/B/C/D
  (if P2 recommends; per S1274 §11 graduation guardrails).

---

## 7. Anti-scope

Group 1900 will NOT do the following. This is enforced per
playbook §14.5 no-implementation rule + S1272 §14 authorial
framing (evidence-only research; downstream design-with-Chris-
gate).

### 7.1 No runtime changes

- **No modifications** to `core/llm_enforcer.py` (LLMEnforcer),
  `core/employees/mission_runner.py` (MissionRunner),
  `core/services/human_attention_lifecycle.py` (HAI auto-
  approve), or any KillSwitch read/write path.
- **No migrations** — no schema changes, no new fields on audit
  models (`ToolCallRecord`, `OpsRunEvent`, `LLMCallEvent`), no
  new `AuthorityLevel` enum members, no new event schemas
  materialized in code.
- **No new PA tool handlers** or PA tool schema additions.
- **No new Celery tasks** or beat schedule additions.

### 7.2 No design decisions outside child slots

- **No re-opening of S1274 Symbol Mapping Option E
  recommendation.** Option E stands as v0; future graduation is
  governed by S1274 §11's 4 telemetry triggers, not by Group
  1900. **Clarification (per Rigby S1900 SIGN cycle 1 Q3(a)
  fold):** P2 may recommend future graduation/migration
  pathways (E → A/B/C/D or hybrid) as **decision inputs for
  Chris-gated ratification**, but this is not a re-evaluation
  of Option E's v0 recommendation, and no runtime
  implementation changes occur in Group 1900. Any graduation
  decision Chris makes at P2 close remains subject to S1274 §11
  guardrails for execution timing.
- **No overriding of S1272 authorial framing.** S1272 §9's 6
  design options are the P2 candidate set; introducing a
  7th option requires justification against S1272 verifier
  loop.
- **No parallel-execution of children.** Per playbook §14.5
  parent + Chris directive: children are sequential (P1 →
  P2 → P3 → P4 → xx99). Parallel work risks compound context
  bloat + Rigby SIGN worker instability.

### 7.3 No design-decision blur

- **P1 does NOT pick which of the 3 actor roles is "primary"** —
  all three remain separate primitives per S1271 F11.
- **P2 does NOT design implementation** — P2 picks the design
  option; implementation is post-arc.
- **P3 does NOT re-open the S1269 F1 "4 planes don't compose"
  finding as a research question** — that's the accepted state;
  P3 designs the composition policy going forward.
- **P4 does NOT audit individual adjacent domains for internal
  correctness** — P4 audits the SEPARATION BOUNDARY between
  authority and each adjacent domain.

### 7.4 No parent scope creep

- **No inclusion of the deferred Group 1900 Event Architecture
  scope** (source_kind enum, six-plane learning-surface event-
  emission gap, HAI event candidates). That remains queued for
  a future arc.
- **No inclusion of S1272 §14.5 explicitly-NOT-recommended
  items** (Trust Propagation, Employee Delegation Design,
  Memory Architecture). Those wait for P2 close per S1272 §14.5.

### 7.5 No implementation coordination with other subsystems

- **No PR coordination with Group 1300 Memory** (LEARNING-PLANE-
  CONTRACT-ADR) — that ADR is joint but authored under Memory
  arc scope, not Group 1900.
- **No PR coordination with Group 1800 HumanAttention** post-
  arc T-slot items — those follow S1899 xx99 §8.1/8.2/8.3
  tiered execution per Chris post-arc gating.

---

## 8. Decisions recorded (Chris-locked 2026-07-04)

Group 1900 opens with 5 explicit Chris D-verdicts. All ratified
via `agree all → (b/a/a/b)` + `Q5 = (b)` at S1900 session open
2026-07-04.

### D81 — Group 1900 scope = Authority Enforcement Design Space

**Decision:** Group 1900 scope is Authority Enforcement Design
Space, NOT the playbook §22 default queue lean of Event /
Integration / Runtime Architecture.

**Rationale:**
- Chris line-select signal at `docs/research/platform_architecture_inventory.md:191` — the §9 STAGE 2 top-1 recommendation per S1273.
- Governance / Authority PARTIAL maturity + HIGH drift risk per S1273 v2 Rigby review — the biggest architectural risk in the library.
- KillSwitch full write path + zero enforcement readers = dangerous false-sense-of-control failure mode.
- S1272 §14 4-mission sequence already identified this as the natural next execution arc.

**Impact:** Event Architecture scope + Group 1800 T0/Gate `R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES` handoff remain parked for a future arc.

### D82 — Mint fresh Group 1900 arc pin

**Decision:** Mint fresh Group 1900 arc pin at S1900 open;
`tools/pa_local.sh:156` rotates immediately.

**Executed:** Rigby `session_tool.create_fresh` minted `pa-2bd1613ce2bd4a9c` (title "Session 1900 — Group 1900 Authority Enforcement Design Space parent scoping"). Wrapper rotated + header ledger updated with S1900 mint documentation + Group 1800 pin retirement entry.

**Rationale:** Playbook §16 arc-open fresh-thread discipline; SIGN routing precedent from S1801-S1806 arc-pin durable-by-sixth-application (CODIFICATION-READY at S1899 close per MC-4) → SEVENTH-consecutive-application observation opportunity at Group 1900 close.

### D83 — Route Rigby light SIGN cycle 1 on parent scoping

**Decision:** Route Rigby light SIGN cycle 1 pre-commit on this
S1900 parent scoping doc.

**Rationale:**
- S1900 = SIXTH application of playbook §11.1 template; SIGN keeps the pattern honest.
- D48 32nd arm at Group 1900 parent scoping — MC-2 26-consecutive-fully-clean-arms sub-pattern CODIFICATION-CONFIRMED extension milestone opportunity (extended to 27 at S1900 CLEAN turn 1).
- Playbook §15 stage-table parent-row light-SIGN default is OPTIONAL; Chris opted in.

### D84 — Pre-taxonomy card before §11.1 draft

**Decision:** Route pre-taxonomy card (3 candidate taxonomies)
through Rigby for Chris ratification BEFORE drafting the §11.1
parent doc.

**Executed:** Pre-taxonomy card routed via arc pin `pa-2bd1613ce2bd4a9c` 2026-07-04. Chris ratified Q5=(b) 2026-07-04.

**Rationale:** For Authority Enforcement specifically, the subdomain taxonomy is contested (S1273 §9 STAGE 2 references "composes S1270 + S1271" but child cuts vary by lens). Better to ratify taxonomy first than fold late.

### D85 — 4-child taxonomy with CONSOLIDATION

**Decision:** Group 1900 = 4-child arc:
- P1 = Actor Role Propagation Design (S1272 §14.2)
- P2 = Authority Enforcement Design Decision (S1272 §14.3)
- P3 = Cross-Plane Composition Design (S1272 §14.4)
- P4 = Cat F Adjacent / Separation Boundaries CONSOLIDATION
- xx99 canonical summary at S1999

**Rationale:**
- Respects S1272 authorial intent (3 real recs, not artificial split into (c)'s 6-child).
- Adds only the proven CONSOLIDATION pattern from Group 1700 F / Group 1800 F.
- Runtime target ~6 sessions.

**Trade-off accepted:** Group 1900 as 4-child does NOT observe MC-4 (arc-pin routing durable-by-6th-application under 6-child arcs). MC-4 observation deferred to a future 6-child arc.

**Trade-off accepted:** MC-5 (§11.2 20-section child template)
gets 4 additional consecutive-application data points (TWELFTH →
FIFTEENTH), which is honest observation without arc-shaping.

### Operational defaults / inherited constraints (not new Chris D-verdicts)

Per Rigby S1900 SIGN cycle 1 Q2 fold: the two items below are
recorded here for traceability but are **NOT** new Chris D-
verdicts. They are operational defaults derived from prior arc
precedent + playbook + memory rules. Chris's Q1-Q5 batch at
S1900 open ratified D81-D85 explicitly; these operational
defaults are inherited without requiring separate D-slots.

**O1 — Sequential child execution (derived from dependency shape + prior arc precedent + memory rule)**

Children run sequentially (P1 → P2 → P3 → P4 → xx99), not in parallel.

**Rationale:**
- F9 makes P1 the strict prereq for P2 (mode preconditions inherit from actor role composition).
- P3's cross-plane composition consumes P2's mode pick.
- P4's CONSOLIDATION consumes P1 + P2 + P3.
- Parallel child execution risks compound context bloat + Rigby SIGN worker instability per memory rule `feedback_no_parallel_research_arcs.md`.

**Trace:** operational default; not a new Chris D-verdict at S1900 open.

**O2 — xx99 §10 SEVENTH meta-methodology application (playbook §11.3 carry-over)**

Group 1900 xx99 canonical summary at S1999 includes §10 "What This Research Taught Us About How to Do Research" per playbook §11.3 SEVENTH application (after S1399 / S1499 / S1599 / S1699 / S1799 / S1899).

**Rationale:** Memory rule `feedback_xx99_meta_methodology_section.md` established at S1399 close; consistent application preserves durability observation for MC-1/MC-2/MC-3 CODIFICATION-CONFIRMED status + MC-4/MC-5 CODIFICATION-READY → CONFIRMED promotion candidates.

**Trace:** playbook §11.3 template carry-over; not a new Chris D-verdict at S1900 open.

---

## 9. Next step

### 9.1 Immediate (S1900 close)

1. **Rigby SIGN cycle 1** on this parent scoping doc pre-commit
   per D83. Single-batch 4-question routed via arc pin `pa-2bd1613ce2bd4a9c`. D48 32nd arm anticipated CLEAN turn 1.
2. **Fold** any SIGN-with-edits from cycle 1 pre-commit.
3. **Chris commit-gate** on S1900 artifact set + Rigby SIGN
   record.
4. **ARCHITECTURE_INDEX** bump v58 → v59 with §1.62 S1900
   registration + line-6 v59 preamble (preserving v58 preamble).
5. **OPEN_ARCS** move Group 1900 row from Not-started → In-
   progress.
6. **S1900 handoff** at `docs/handoffs/SESSION_1900_GROUP_1900_AUTHORITY_ENFORCEMENT_PARENT_SCOPING.md`.
7. **Overwrite `00-START-NEXT-SESSION.md`** to point at S1901 P1
   Actor Role Propagation Design as next-session priority.
8. **Post-merge 4-step docs cascade** + `build_docs_provenance`
   per memory rule (may batch into S1900 arc-open PR or into
   S1901 open PR per Chris preference).

### 9.2 Next session (S1901)

Execute **P1 Actor Role Propagation Design** per §5.1:
- Layer i: Role schema + propagation contract (parallel-safe).
- Layer ii: Implementation across 20 boundaries.
- Deliverable: `docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md` per playbook §11.2 20-section child template.
- Rigby SIGN cycle 1 pre-commit.
- Chris ratification at close.

### 9.3 Arc completion path

| Session | Deliverable | Chris-gate |
|---|---|---|
| S1900 | Parent scoping (this doc) | Ratification + D81–D87 commit |
| S1901 | P1 Actor Role Propagation Design | Ratification |
| S1902 | P2 Authority Enforcement Design Decision | Multi-verdict Chris design-pick (D8N series) |
| S1903 | P3 Cross-Plane Composition Design | Ratification |
| S1904 | P4 Cat F Adjacent / Separation Boundaries CONSOLIDATION | Ratification |
| S1999 | xx99 canonical summary | Ratification + arc pin `pa-2bd1613ce2bd4a9c` retire per playbook §16 |

Runtime target: **6 sessions**. Runtime cap: **8 sessions** (buffer for SIGN-with-edits, spawned sub-decisions, or Cat E-analog spawn from P3).

---

## Appendix — Frontmatter provenance

### A.1 Playbook §11.1 template SIXTH application

Group 1900 parent scoping is the **SIXTH application** of the
playbook §11.1 9-section parent scoping template:

| Session | Group | Domain | §11.1 Application |
|---|---|---|---|
| S1400 | 1400 | Revenue | FIRST |
| S1500 | 1500 | Sports | SECOND |
| S1600 | 1600 | Content | THIRD |
| S1700 | 1700 | Observability | FOURTH |
| S1800 | 1800 | HumanAttention | FIFTH |
| **S1900** | **1900** | **Authority Enforcement** | **SIXTH** |

**MC-4 durability observation opportunity:** Group 1900 with
4-child structure does NOT qualify for arc-pin routing durable-by-
6th-application under 6-child arcs observation (Q5=(b)
ratification accepted this trade-off). MC-4 observation deferred
to a future 6-child arc.

### A.2 Companion doc lineage

| Companion | Session | Contribution to Group 1900 |
|---|---|---|
| `authority_enforcement_design_space.md` | S1272 | Load-bearing design-space enumeration (F1–F11); §14 4-mission next-research handoff; §11 15-prereq DAG. |
| `symbol_mapping_architecture.md` | S1270 | 5 mapping options; F2 zero runtime action_class carriers; F6 3 structural drop boundaries. |
| `symbol_mapping_option_selection_design.md` | S1274 | Option E v0 recommendation with 4 must-fix Rigby SIGN edits folded; F8 constraint (Option E enables only 4 of 12 modes). |
| `symbol_mapping_event_schema_design.md` | S1275 | Event schema for Option E; enforcement-adjacent event shapes. |
| `actor_identity_attribution_architecture.md` | S1271 | 3 actor roles (executor / sponsor / principal); 22 attribution surfaces; F6 3 drop boundaries; F11 never collapse. |
| `governance_authority_evolution.md` | S1269 | Governance/authority audit; F1 4 planes don't compose; F2 KillSwitch write-only; F3 no gate reads `JobContract.authority`. |
| `platform_architecture_inventory.md` | S1273 | §9 STAGE 2 top-1 recommendation (Chris line-select origin); 32-domain maturity/coverage matrix. |
| `DOMAIN_RESEARCH_PLAYBOOK.md` | Living | §11.1 template + §14.5 no-implementation rule + §22 D-override precedent + §16 arc-pin discipline. |
| `ARCHITECTURE_INDEX.md` | Living | §1.62 S1900 registration (bumped v58 → v59 at close). |
| `OPEN_ARCS.md` | Living | Group 1900 row Not-started → In-progress at S1900 close. |
| `1899_human_attention_canonical_summary.md` | S1899 | MC-1/MC-2/MC-3 CODIFICATION-CONFIRMED baseline; MC-4/MC-5 CODIFICATION-READY promotion candidates; verifier-loop REQUIRED enforcement precedent. |
| `EMPLOYEE_OS_PRIMITIVES.md` | Living | `AIEmployee` + `JobContract` frozen-dataclass primitives; authority policy metadata locus. |

### A.3 Verifier loop notes

Parent scoping doc; no independent Explore-sub-agent sweeps
performed. Load-bearing structural claims about the design space
inherit from S1272's SIGN-verified findings + S1274's Option E
recommendation + S1275's event schema.

Re-attestation of 5 verification chains from S1272 recorded in
frontmatter `verifier_loop` field. No new verification chains
needed at parent scope; child audits will run their own verifier
loops per playbook §13 discipline + MC-1 CODIFICATION-CONFIRMED
(S1899 close).

### A.4 Rigby SIGN routing (D83 execution)

- **Arc pin:** `pa-2bd1613ce2bd4a9c` (fresh Group 1900 pin, minted 2026-07-04).
- **Cycle 1 scope:** Single-batch 4-question pressure test on this parent scoping doc, pre-commit.
- **D48 arm expectation:** 32nd arm CLEAN turn 1 per MC-2 26-consecutive-clean-arms sub-pattern.
- **SIGN questions:** posted at Rigby's discretion per playbook §15 pressure-test standard set (Q1 posture / Q2 evidence-decision fit / Q3 cross-pattern / Q4 most-important-thing-you-missed).
- **Cycle 1 verdict (landed 2026-07-04):** **SIGN-with-edits at HIGH confidence.**
  - **Most-accurate part:** §5 Child mission sequence (esp. §5.1–§5.3) + §7 Anti-scope — cleanly preserves S1272 §14 handoff, keeps research/design/implementation separation, sequential dependency chain explicit without pretending implementation is happening.
  - **Weakest part:** §8 "Decisions recorded" (D86/D87) — phrased as Chris-locked *decisions* but read more like operational defaults / carry-overs; risked inflating the D-ledger beyond what Chris explicitly ratified. **Folded via O1/O2 reclassification.**
  - **Q1 (Taxonomy shape):** 4-child structure does NOT over-index on S1272 §14 authorial framing. §14.3 is a single coupled decision surface; splitting for MC observation would fragment. No fifth child needed. **Folded via §5.2 migration-recommendation clarifier.**
  - **Q2 (D-verdict fidelity):** D86/D87 reclassified as O1/O2 operational defaults / inherited constraints. **Folded.**
  - **Q3(a) (§7.2 vs §5.2 blur):** Migration recommendation vs re-litigation distinction sharpened via ordering clarifier + explicit "recommendation for Chris-gated decisioning" language in both sections. **Folded in §5.2 + §7.2.**
  - **Q3(b) (§7.3 vs §5.4 blur):** "adjacent-domain audit" → "separation-boundary posture audit (interface + seam audit)" throughout §5.4 + explicit "not internal correctness" sentence + "P4 checks / P4 does NOT check" mini-table added. **Folded in §5.4.**
  - **Q4 (Most important thing missed):** Enforcement Binding Points map added as required P2 deliverable in §5.2 — enumerate boundary read-sites + evaluation order vs KillSwitch/budget/freeze/HAI/mission governance + fail-open/fail-closed posture per site. Prevents avoidable child-level spawn; makes P3 + P4 attachable. **Folded in §5.2.**
- **D48 32nd arm posture:** **CLEAN turn 1.** 27-consecutive-fully-clean-arms sub-pattern EXTENDED at S1900 SIGN cycle 1 → MC-2 CODIFICATION-CONFIRMED milestone extended from 26 → 27 consecutive.
- **Total SIGN folds landed pre-commit:** **5** (Q1 §5.2 migration clarifier + Q2 D86/D87 → O1/O2 reclassification + Q3(a) §5.2 + §7.2 migration-recommendation dual clarifier + Q3(b) §5.4 separation-boundary posture rename + explicit "not internal correctness" + P4 checks/does-NOT-check mini-table + Q4 §5.2 Enforcement Binding Points map required deliverable).

### A.5 Anticipated MC promotions at S1900 close

- **MC-1 (verifier-loop REQUIRED):** CODIFICATION-CONFIRMED at S1899 close; enforced at S1900 parent scoping via inherited S1272 verifier chain.
- **MC-2 (D48 26-consecutive-fully-clean-arms sub-pattern):** CODIFICATION-CONFIRMED at S1899 close; extended to 27 if D48 32nd arm turn 1 CLEAN at S1900 SIGN.
- **MC-3 (F5 correlation-primitive HYPOTHESIS box discipline under utility-rate-vs-pass-rate framing):** CODIFICATION-CONFIRMED at S1899 close; no new arc-open application observation at S1900 (child-level observation opportunity at P1–P4).
- **MC-4 (arc-pin routing durable-by-6th-application under 6-child arcs):** CODIFICATION-READY at S1899 close; **Group 1900 does NOT observe** (4-child structure per D85). MC-4 promotion path deferred.
- **MC-5 (§11.2 20-section child template durable at ELEVENTH consecutive application overall):** CODIFICATION-READY at S1899 close; Group 1900 child audits P1–P4 provide TWELFTH → FIFTEENTH consecutive-application observation → **CODIFICATION-CONFIRMED promotion candidate at S1999 xx99.**

---

_End of S1900 parent scoping._
