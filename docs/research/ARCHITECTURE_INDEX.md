---
title: "Architecture Research Index — front page of Donkey Betz's engineering encyclopedia"
status: active
authority: navigation
session_added: 1268
last_verified: 2026-06-30 (v5 — S1273 registered `platform_architecture_inventory.md` as §1.9. Library scope broadens from Employee-OS-focused arc (§1.1-§1.8) to Employee-OS-arc PLUS whole-platform inventory (§1.9). Chris's direction at S1273 close: "the next cleanup should be updating ARCHITECTURE_INDEX.md so this becomes the whole-platform counterpart to the Employee OS research library." §1 preamble rewritten. §3 domain map extended for Revenue / Outreach / Engagement (S1273 surfaced this as a Rigby-caught missed domain). §4 dep graph extended with whole-platform arc as sibling branch. §5 new gaps §5.12-§5.14 for top-3 S1273 recommendations. §7 decision matrix +3 whole-platform rows. §8 timeline S1273 row. §9 lateral research expanded.) — prior v4 added §1.8 Authority Enforcement Design Space
companion_anchors:
  - docs/PLATFORM_INVENTORY.md       # runtime anchor (counts source)
  - docs/PLATFORM_WHAT_IT_IS.md      # narrative anchor (glossary)
  - docs/EMPLOYEE_OS_PRIMITIVES.md   # canonical primitives + anti-duplication
  - docs/00-START-HERE/DOC_LIFECYCLE.md  # governs the corpus itself
  - docs/KNOWLEDGE_PIPELINE.md       # runtime flow map
  - docs/AUDIT_FINDINGS.md           # canonical Celery deferred list
  - docs/EVENT_SYSTEM_INVENTORY.md   # observability layers (§1.9 dep)
verifier_loop: |
  v5 update (2026-06-30, S1273 Part 2): re-inventoried docs/research/
  after S1273 landing. `ls docs/research/` now shows 8 .md files
  (7 research + this index). `platform_architecture_inventory.md`
  registered as §1.9 per §10.1 maintenance rules. Library scope
  broadens: §1.1-§1.8 remain the Employee-OS-focused arc; §1.9 is
  the whole-platform counterpart (Chris's explicit S1273-close
  direction). §1 preamble rewritten to acknowledge dual-scope
  library. §3 domain map extended for Revenue / Outreach /
  Engagement (Rigby caught this as a missed domain during S1273
  SIGN review; folded into §3.32 of §1.9 + registered here as new
  Revenue Pipeline domain row). §4 dep graph extended with whole-
  platform arc as sibling branch (does NOT depend on §1.1-§1.8 —
  parallel scope). §5: §5.4 Memory Architecture partially covered
  by §1.9 §3.13; new gaps §5.12 (Revenue Pipeline canonical
  architecture doc), §5.13 (Observability Deduplication Audit),
  §5.14 (Sports/DBAO ↔ AI Studio Integration Sketch) added per
  S1273 top-3 recommendations. §7 decision matrix +3 whole-
  platform rows. §8 timeline S1273 row. §9 lateral research list
  expanded to reference the 11-mission whole-platform roadmap in
  §1.9.
  Prior v4 update (S1273 Part 1): S1272 Authority Enforcement
  Design Space registered as §1.8 (Appendix C notes; frontmatter
  bumped to v4 mid-session).
  Prior v3 update (S1271 close): S1270 Symbol Mapping + S1271
  Actor Identity registered as §1.6 + §1.7 (Appendix B notes).
  Prior v2 note (S1269 close): added §1.4 governance research;
  §3/§4/§5/§7/§8/§9 updated per maintenance rules §10.1.
  Prior v1 note (S1268 close): inventoried docs/research/ at
  2026-06-30. Three docs present. Re-read each frontmatter before
  classifying. Self-verifier pass looked for missing docs,
  duplicate classifications, incorrect dependency ordering,
  inconsistent statuses, and discoverability gaps.
owner: claude (drafted S1268; v2 update S1269; v3 update S1271; v4 update S1273 Part 1; v5 update S1273 Part 2)
---

# Architecture Research Index

> **What this is.** The front page of Donkey Betz's engineering
> encyclopedia. A Staff Engineer joining the project six months
> from now should read this document **first** — before opening
> any code, before reading CLAUDE.md, before touching a runtime
> file. It tells them what architectural research exists, why it
> exists, what order to read it in, and what decisions should
> never be made before reading specific documents.
>
> **What this is not.** A markdown link list. A taxonomy of every
> file under `docs/`. A historical archive. The wider `docs/`
> corpus has its own lifecycle (see
> `docs/00-START-HERE/DOC_LIFECYCLE.md`); this index governs the
> **research library specifically** — the docs that capture
> architectural reasoning *before* implementation.

---

## 0. Philosophy — why a research library exists

Before any system on this platform gets built or rebuilt, four
disciplines apply, in order:

1. **Research first.** Open-ended questions get a doc, not a
   sprint plan. The doc captures evidence with file:line cites
   and explicit unknowns; nothing is invented.
2. **Inventory before design.** Before you propose a primitive,
   you have to know what primitives already exist. The platform
   has **585 models**, **83 agents**, **113 PA tool schemas**,
   **91 enabled beat tasks** (see `docs/PLATFORM_INVENTORY.md`).
   Anything you "design" without that count in front of you is
   likely either re-inventing or violating
   `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 (the anti-duplication
   matrix).
3. **Reuse before invention.** If an existing primitive does
   80% of the job, the right move is a wrapper, not a new model.
   Every "new model" instinct has cost an operator hour before;
   the names of those hours live in
   `EMPLOYEE_OS_PRIMITIVES.md` §2.
4. **Implementation last.** Once research + inventory + reuse
   are documented and reviewed, only then does code follow.
   PRs reference the research that justified them; the research
   exists to make the PR small.

These four disciplines map to the four document types you will
find in this library: **Audit**, **Inventory**, **Sketch**,
**Decision Record**. The first three precede code; the fourth
documents what the team decided once code is imminent.

**The verifier loop is the load-bearing rule.** Every research
doc in this library is grounded in direct file reads (Grep,
Read, ORM probes) — never recall, never assumption. When a
sub-agent produces evidence, the parent agent re-verifies a
sample by directly reading the cited file:line before
synthesizing. Rigby (the platform's PA / co-author) gets an
independent SIGN review on every doc before it's considered
publishable. Verdicts are **SIGN-clean**, **SIGN-with-edits**,
or **NEEDS-MORE**; edits are folded and the verifier_loop
frontmatter field is updated.

---

## 1. Current Architecture Research Library

The library has **two scopes as of S1273:**

- **The Employee OS arc (§1.1–§1.8):** an 8-doc chain that goes
  deep on a single subsystem. Each doc builds on the previous;
  read in order unless goal-driven (see §2 reading paths). This
  is the arc that began S1268 and closed STAGE 2 at S1272.
- **The whole-platform inventory (§1.9):** one doc, whole-
  platform scope. Independent of the Employee OS arc — read it
  when you need to know what domains exist across all of Donkey
  Betz, not when you're going deep on one subsystem. S1273 close
  registered it as "the whole-platform counterpart to the
  Employee OS research library" (Chris's direction).

**When to read which.** If your work touches a subsystem the
Employee OS arc has already researched (comms, governance,
authority, actor identity, mission orchestration), go to §1.1-
§1.8 for the deep dive. If your work touches a subsystem NOT in
that arc (frontend, spiders, RAG, betting, revenue, notifications,
etc.) — or if you're new to the platform and need the shape of
the whole thing — start with §1.9.

The two scopes will merge over time: as future missions bring
§1.9's LIGHT-coverage domains up to DEEP, they'll get their own
research docs registered as §1.10+, and §1.9 will remain the
navigation-and-classification layer.

### 1.1 `employee_os_communication_substrate_audit.md`

- **Title.** Employee OS Communication Substrate — Audit
- **Purpose.** Inventory every communication / collaboration
  primitive the platform already ships, classify each one for
  reuse, and identify the failure classes any future
  inter-employee protocol would inherit.
- **Status.** Draft → Active (SIGN-clean from Rigby S1268
  conversation `pa-01e90a1d36f54880`).
- **Research type.** Inventory + Architecture Audit + Failure
  Analysis (composite).
- **Primary questions answered.**
  - What communication substrates exist today?
  - Which are safe / wrappable / off-limits for reuse?
  - What's the receipt contract on Celery-dispatched tools?
  - What's the silent-failure history Employee OS would
    inherit?
- **Dependencies.** `PLATFORM_INVENTORY.md` (runtime
  anchor), `EMPLOYEE_OS_PRIMITIVES.md` (§2 anti-duplication
  matrix), `topics/employee-os.md`,
  `topics/agent-system.md`, `topics/personal-assistant.md`,
  `handoffs/SESSION_1267_*.md`.
- **Recommended next reads.** §1.2 (protocol sketch), then
  §1.3 (collaboration patterns).
- **Overall importance.** Foundational. Anything that touches
  inter-employee or inter-agent comms needs this read first.

### 1.2 `employee_os_communication_protocol_sketch.md`

- **Title.** Employee OS Comms Protocol Sketch — Platform
  Auditor → Chief of Staff
- **Purpose.** Take the substrate audit's `SAFE TO REUSE`
  primitives and scope the *first* concrete inter-employee
  write path. Reuse-only — explicit "do not enable
  `messaging_tool.send_message`" + explicit "no new model."
- **Status.** Draft → Active (SIGN-with-edits from Rigby
  S1268; two substantive edits folded — L3 helper-side dedupe
  + cadence expires_at default; two clarifications folded).
- **Research type.** Design Research / Protocol Sketch (not a
  decision record — no implementation greenlight).
- **Primary questions answered.**
  - What does an inter-employee notice look like as a bounded
    DM on existing `MessageThread` + `DirectMessage`
    primitives?
  - How does it thread without polluting the existing
    per-(employee, job) shift-report channels?
  - What's the dedupe contract (helper-side L1/L2/L3,
    caller-side defense-in-depth)?
  - What stays out of scope for v0 (HumanAttentionItem
    spawning, reply lane, fan-out, cross-fleet)?
- **Dependencies.** §1.1 (substrate audit must be read
  first); `EMPLOYEE_OS_PRIMITIVES.md`;
  `handoffs/SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md`.
- **Recommended next reads.** §1.3 (the wider collaboration
  audit Rigby asked for as the next-mission frame).
- **Overall importance.** High for anyone scoping the first
  cross-employee write surface. Lower for anyone whose work
  doesn't touch inter-employee messaging.

### 1.3 `employee_os_collaboration_patterns.md`

- **Title.** Employee OS Collaboration Patterns — Platform-
  Wide Audit
- **Purpose.** Step back from "how do employees communicate"
  to "how do autonomous components *already* collaborate
  across the platform?" — so any future Employee OS work
  reuses existing collaboration mechanisms rather than
  reinventing them.
- **Status.** Draft → Active (SIGN-with-edits from Rigby
  S1268; one substantive correction folded — MissionRunner
  `verdict_issued` event is conditional on
  `auto_emit_verdict=True`, not guaranteed; one architectural
  blind-spot note added on canonical idempotency key across
  the two orthogonal orchestration paths).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite).
- **Primary questions answered.**
  - Q1–Q8 from the mission spec, answered explicitly in the
    doc.
  - What are the eleven distinct collaboration substrates
    already in production?
  - Which 33 primitives are SAFE to reuse, which 10 need
    wrappers, which 4 should not be reused, and which 5 are
    UNKNOWN?
  - What 29 documented failure modes does any future
    collaboration design inherit (12 new beyond the substrate
    audit's baseline)?
  - What is the canonical foundation for future Employee OS
    collaboration? (MissionRunner + OpsRun + OpsRunEvent +
    AgentFollowupSubscription + `post_shift_report`-style
    helpers.)
- **Dependencies.** §1.1 + §1.2 (both prior research docs);
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md`;
  `topics/employee-os.md`, `topics/celery-workers.md`,
  `topics/agent-system.md`, `topics/initiative-pipeline.md`.
- **Recommended next reads.** Once this lands, the
  recommended **next research mission** is Governance +
  Authority Evolution (see §5 below). The next *design* work
  is the protocol sketch's v0 PR (assuming Chris greenlights
  it).
- **Overall importance.** Mandatory for anyone touching
  collaboration, orchestration, scheduling, mission
  coordination, or autonomy escalation.

### 1.4 `governance_authority_evolution.md`

- **Title.** Governance + Authority Evolution — Architectural
  Discovery
- **Purpose.** The canonical research anchor for every future
  authority or governance discussion. Inventories the governance
  + authority surface that exists today, identifies what's
  runtime-enforced vs. observational vs. documentation-only,
  surfaces the gaps, and recommends the next research mission
  (Symbol Mapping Architecture).
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1269;
  two must-fix edits folded — Exec Summary now uses canonical
  "four planes" framing instead of mixed "two + plus" framing,
  and gate count corrected 34→35; two clarifications folded —
  DO-NOT-REUSE-for-enforcement language on
  `JobContract.authority`, F4 budget-plane intent claim
  softened).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.3 shape).
- **Primary questions answered.**
  - Q1–Q12 from the mission spec, answered explicitly in the
    doc's §12.1.
  - What are the four governance planes (autonomy / authority /
    budget / human governance) and why don't they compose today?
  - Where is authority enforced (35 runtime gates) vs. where is
    it only observed (warn-mode telemetry) vs. where does it
    disappear entirely (between MissionRunner and step.fn
    execution)?
  - What blocks the move from warn-mode to enforce-mode?
    (Symbol mapping — F2 + §11.)
  - What is the canonical foundation for governance reuse?
    (48 SAFE / 11 WRAPPER / 0 DO-NOT-REUSE / 0 DEPRECATED /
    3 UNKNOWN.)
- **Dependencies.** §1.1 + §1.2 + §1.3 (prior research docs);
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md` row 17
  (GovernanceState + KillSwitch); `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`
  (warn-mode design + enforce-mode prereqs).
- **Recommended next reads.** §1.5 (this index, for navigation
  context). The recommended **next research mission** per §11
  is Symbol Mapping Architecture (resolves §10 Q1 + Q12 of the
  collaboration audit + this doc's §9 Q1).
- **Overall importance.** Mandatory for anyone touching
  authority enforcement, governance modes, kill switches,
  budget controls, human approval lifecycles, or feature-flag
  gates.

### 1.5 Index doc (this file)

- **Title.** Architecture Research Index
- **Purpose.** Navigation. This doc.
- **Status.** Active (v3 — S1271 added §1.6 Symbol Mapping and
  §1.7 Actor Identity entries; §3-§9 updated per maintenance
  rules).
- **Research type.** Navigation / Decision Record (light).
- **Maintenance rule.** Every future research doc must update
  this index — see §10.

### 1.6 `symbol_mapping_architecture.md`

- **Title.** Symbol Mapping Architecture — Architectural Discovery
- **Purpose.** The canonical research anchor for the "WHAT
  action" question. What architectural bridge is missing between
  `JobContract.authority` policy strings and runtime symbols
  (tool names, step names, task names, function calls, model
  writes)? Enumerates the design space so authority enforcement
  can eventually be scoped.
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1270
  conversation `pa-cbcc410b32714f60`; two must-fix + three
  strongly-recommended optional edits folded — §8 narrowed
  `_AuthorityContractMalformedError` scope, §2.6 added
  parallel-vocabulary type/shape anchor, I-S4 wording softener,
  I-S3 dual-cite F1+F3, Option E "reversibility ≠ preference"
  disclaimer; §4.1 row 24 added for
  `AssistantProfile.get_allowed_tools`; §2.4 normalization caveat;
  §9 F11 with 7 architectural blind spots).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.3 + §1.4
  shape).
- **Primary questions answered.**
  - Q1–Q8 from the mission spec, answered explicitly in the
    doc's §12.1.
  - What are the 57 unique authority strings (68 total entries),
    and where do they live?
  - What runtime action surfaces exist (12) and which carry
    action_class metadata today? (None.)
  - What identifier registries already exist on the platform
    (24) that could serve as reuse candidates?
  - What are the five mapping options (A/B/C/D/E) and their
    tradeoffs?
  - Where are the 20 candidate enforcement layers?
  - What historical failures (5 YES + 10 PARTIALLY + 8 NO of 23)
    would Symbol Mapping have prevented?
- **Dependencies.** §1.4 (the governance audit named this
  mission), §1.3, §1.1; `PLATFORM_INVENTORY.md`;
  `EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication matrix;
  `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §1.7 (Actor Identity is the "WHO"
  companion). Then §9 roadmap STAGE 2 (Authority Enforcement
  Design Space) — the design mission that composes both.
- **Overall importance.** Mandatory for anyone scoping authority
  enforcement, adding a new employee's authority contract, or
  proposing action_class metadata on any runtime surface.

### 1.7 `actor_identity_attribution_architecture.md`

- **Title.** Actor Identity & Attribution Architecture —
  Architectural Discovery
- **Purpose.** The canonical research anchor for the "WHO
  performed it" question. Direct follow-on to §1.6 Symbol
  Mapping. When the platform records an action, how does it know
  who performed it? Both prereqs must land before authority
  enforcement can exist.
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1271
  conversation `pa-cbcc410b32714f60`; four must-fix + two
  strongly-recommended optional edits folded — §8.5 added
  introducing the executor_actor / sponsor_actor / principal_user
  3-role vocabulary as normative for the doc + §11 F11 summary
  finding; F1 language softened to "cannot answer reliably or
  queryably"; F9 softened to "the cleanest enforcement primitive";
  §3.5 added inventorying missing surfaces the platform does NOT
  ship; §9.4 Attribution-first counterargument paragraph; §5
  role-confusion framing note).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.6 shape).
- **Primary questions answered.**
  - Q1–Q10 from the mission spec, answered explicitly in the
    doc's §14.1.
  - What actor identity concepts exist (19)?
  - Where is actor identity recorded (22 attribution surfaces —
    13 Explicit / 2 Inferred / 4 Ambiguous / 1 Unreliable /
    2 Missing)?
  - Where does identity change shape (14 shape changes, 3
    structural drop boundaries)?
  - What identity collisions have happened (15 historical
    incidents; 7 YES + 4 PARTIALLY + 4 NO — 73% effective
    case)?
  - What existing identity registries can be reused (25 — 14 SAFE
    + 7 WRAPPER + 0 DO-NOT-REUSE + 1 DEPRECATED + 3 UNKNOWN)?
  - What are the 17 candidate enforcement boundaries?
  - What does "actor" need to mean for Employee OS? (§8, six
    semantic questions posed.)
  - What is the relationship between actor identity and
    authority? (§9, the WHAT + WHO = enforcement primitive.)
  - What should the next research mission be? (§13.1 — Authority
    Enforcement Design Space.)
- **Dependencies.** §1.6 (Symbol Mapping is the WHAT companion),
  §1.4 (governance planes), §1.3, §1.1; `PLATFORM_INVENTORY.md`;
  `EMPLOYEE_OS_PRIMITIVES.md`; `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §9 roadmap STAGE 2 (Authority
  Enforcement Design Space) — the first design mission that
  consumes both §1.6 and §1.7.
- **Overall importance.** Mandatory for anyone touching actor
  identity on any audit surface, adding a `user` FK to OpsRun (a
  documented anti-pattern per §1.7 F11 without role clarity),
  proposing an actor primitive, or scoping the delegation/trust
  question. **F11 is especially load-bearing**: a single "actor"
  label is insufficient — enforcement-grade attribution requires
  at least executor_actor / sponsor_actor / principal_user as
  distinct roles.

### 1.8 `authority_enforcement_design_space.md`

- **Title.** Authority Enforcement Design Space — Architectural
  Discovery
- **Purpose.** The design-space research that must precede any
  enforce-mode PR. Symbol Mapping (S1270) answered WHAT action;
  Actor Attribution (S1271) answered WHO acted; this doc asks:
  given both prereqs are shipped as research, what are the
  possible ways the platform could eventually decide whether an
  actor was allowed to perform a mapped action? Enumerates the
  design space so a downstream design-with-Chris-gate mission
  can consume it. **Design-space only — no implementation,
  no decision.**
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1272
  conversation `pa-cbcc410b32714f60`; **Medium confidence**;
  8 must-fix edits folded — §3 gained 3 first-class boundaries
  (WebSocket, Fleet, Spider) closing a completeness gap Rigby
  flagged as "biggest architectural risk"; §9.0 neutrality
  guardrail; §9.1 + §9.2 annotation-burden failure modes;
  §9.6 policy-ossification risk; §8.4 rephrased separating
  prevent-modes from audit/warn modes; §10 Tier-0 hazards
  callout naming #1 + #8 + #15 as disproportionately-high
  blast radius; §6.1 role-propagation rule of thumb;
  §14 P0/P1 dependency-not-preference semantics + §14.2
  (i)/(ii) split.
- **Research type.** Design-Space Research + Platform-Wide
  Inventory + Composition Analysis + Failure Analysis
  (composite — first mission carrying design-space content per
  §9 STAGE 2 pacing note; still research-only, not design
  decision).
- **Primary questions answered.**
  - Q1–Q12 from the mission spec, answered explicitly in the
    doc's §15.1.
  - What are the 24 current enforcement-adjacent inputs
    (13 RUNTIME-VERIFIED / 7 OBSERVATION-ONLY / 3 ASPIRATIONAL
    / 1 UNKNOWN + 8 GAPS)?
  - What are the 20 candidate enforcement boundaries
    (17 original + 3 SIGN-added: WebSocket, Fleet, Spider)?
  - What are the 12 enforcement modes and their 204-cell
    (17×12) mode × boundary compatibility matrix?
  - What are the 4 interpretations per AuthorityLevel value
    (16 total; §5)?
  - How do executor_actor / sponsor_actor / principal_user
    compose across 11 canonical scenarios (§6)?
  - How does authority enforcement compose with the 4 governance
    planes (§7; 1 existing cross-plane touch + 8 new
    composition questions)?
  - Which historical incidents would each mode have prevented
    (33-incident matrix across 4 prior catalogs; §8)?
  - What are the 6 major design options (A-F; §9)?
  - What are the 15 anti-patterns to avoid (§10; Tier-0
    hazards flagged)?
  - What are the 15 prerequisites for enforce-mode and their
    dependency DAG (§11)?
- **Dependencies.** §1.6 (Symbol Mapping — WHAT input premise),
  §1.7 (Actor Attribution — WHO input premise), §1.4
  (governance planes), §1.1, §1.3;
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md`;
  `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §14.1 recommends Symbol Mapping
  Option Selection Design as P0 next research. The 6 design
  options in §9 will be consumed by that downstream mission +
  the Authority Enforcement Design Decision that follows it.
- **Overall importance.** Mandatory reading for anyone scoping
  authority enforcement, evaluating one of the 6 §9 design
  options, proposing an OpsRun schema change, or wiring a new
  enforcement boundary. **F1 is especially load-bearing:**
  AuthorityLevel has exactly one runtime consumer today
  (shape-counter at `mission_runner.py:864-867`) — the enum is
  policy metadata, not enforcement metadata; any design
  introduces the first decision-making consumer. **F8 fail-open
  precedent is the second load-bearing finding:** LLMEnforcer
  at `llm_enforcer.py:237-238` sets the platform's precedent
  for INLINE-gate error handling — any authority enforcement
  design must decide fail-open vs. fail-closed and cite
  rationale.
- **Boundary caveat.** The 3 SIGN-added boundaries
  (WebSocket / Fleet / Spider) are named but not yet
  cross-tabulated against the 12 modes in the 204-cell matrix.
  A future research pass or design mission should extend the
  matrix.

### 1.9 `platform_architecture_inventory.md`

- **Title.** Donkey Betz Platform Architecture Inventory — first
  whole-platform map
- **Purpose.** The whole-platform counterpart to the Employee-OS-
  focused §1.1-§1.8 arc. Inventories every major architectural
  domain of Donkey Betz — 32 domains — with maturity ratings,
  research coverage, existing docs, drift, and technical debt.
  Names the recommended next 11 research missions. **This is the
  doc a Staff Engineer new to the platform should read to
  understand the shape of the whole system.**
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1273
  conversation `pa-02cfd3206302352f`; Medium overall confidence;
  6 substantive edits folded — (1) added missed §3.32 Revenue /
  Outreach / Engagement Pipeline domain + §4.9 cross-domain flow;
  (2) downgraded §3.27 Auth / Permissions maturity STABLE →
  PARTIAL with trust-boundary enumeration; (3) upgraded §3.7 LLM
  Provider Registry maturity WORKING → STABLE (core registry
  stable, failover missing); (4) tightened §1 Executive Summary
  count phrasing to autoblock-consistent language; (5) added
  §3.31 Event Bus vs Observability separation-of-concerns
  paragraph; (6) expanded §9 roadmap 10 → 11 missions with
  Revenue Pipeline canonical architecture doc elevated to #2).
- **Research type.** Architectural Inventory + Platform-Wide
  Mapping + Maturity Classification (whole-platform composite;
  distinct shape from §1.1-§1.8 which are Employee-OS-focused
  audits / sketches / discovery / design-space).
- **Primary questions answered.**
  - What are the 32 major architectural domains of Donkey Betz?
  - Which domains are mature (CANONICAL/STABLE) vs risky
    (PARTIAL/EXPERIMENTAL)?
  - Which domains are under-researched (NONE/LIGHT coverage)?
  - What are the 9 cross-domain flows that traverse ≥ 2
    domains?
  - Which systems duplicate or overlap (8 categories: multiple
    orchestration paths / multiple messaging systems / multiple
    identity concepts / multiple memory stores / multiple
    governance surfaces / multiple content pipelines / multiple
    task/execution logs / multiple agent dispatch systems)?
  - What are the 11 recommended next research missions, ranked
    by architectural uncertainty × risk × reuse × decisions
    unblocked?
- **Dependencies.** `PLATFORM_INVENTORY.md` (authoritative
  counts anchor), `PLATFORM_WHAT_IT_IS.md` (narrative anchor),
  `EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives),
  `KNOWLEDGE_PIPELINE.md`, `EVENT_SYSTEM_INVENTORY.md`,
  `AUDIT_FINDINGS.md` §12. Also depends on the entire Employee
  OS arc (§1.1-§1.8) for the subset of findings that overlap;
  cites governance-authority-evolution.md (§3.23),
  symbol_mapping_architecture.md (§9.1), and
  actor_identity_attribution_architecture.md (§5.3) where
  relevant.
- **Recommended next reads.** Depends on goal:
  - If interested in specific domain: jump to that §3.n
    inventory + cited docs.
  - If interested in cross-domain flows: read §4 (9 flows).
  - If interested in what's next: read §9 (11-mission roadmap
    — top-3 are Authority Enforcement Design Space (§5.2c
    here), Revenue Pipeline canonical architecture (§5.12
    here), Observability Deduplication Audit (§5.13 here)).
- **Overall importance.** **Foundational for whole-platform
  understanding.** The Employee OS arc (§1.1-§1.8) is deep on
  one subsystem; §1.9 is wide on all of them. A new hire should
  read §1.9 first to know the map, then dive into whichever arc
  their work touches. Existing team members should reference §1.9
  when scoping cross-domain work or evaluating "does this touch
  a mature domain or an experimental one?"
- **Verifier-loop note.** Six parallel Explore sub-agents
  produced independent domain sweeps; parent synthesized into
  the 32-domain map. Every domain row is grounded in file:line
  cites OR flagged UNKNOWN. Rigby SIGN-with-edits (fresh pin
  `pa-02cfd3206302352f`, NOT the shared S1270+ arc pin
  `pa-cbcc410b32714f60` — another Claude Code was on that pin;
  Chris flagged the context-crossing risk mid-session; isolation
  pin used to keep S1273 work separate).

---

## 2. Recommended Reading Paths

Engineers join with different goals. Each path lists docs in
order; bracketed numbers point back to §1.

### Path A — "I need to understand Employee OS"

1. `CLAUDE.md` (Quick Start + Working with Rigby section)
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives +
   anti-duplication matrix)
3. `docs/topics/employee-os.md` (subsystem narrative)
4. `docs/research/employee_os_communication_substrate_audit.md`
   [§1.1]
5. `docs/research/employee_os_collaboration_patterns.md`
   [§1.3]
6. Latest handoff: `docs/handoffs/SESSION_1267_*.md`

You will now know: the four current employees, the lifecycle
primitives that compose them, the comms surfaces they expose,
and the collaboration substrates available across the wider
platform.

### Path B — "I want to design new employees"

1. Path A above (in full).
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` §5 ("Quick-Start for
   Adding a New Employee").
3. `docs/research/employee_os_collaboration_patterns.md` §8
   (reuse classification — esp. SAFE rows) and §9
   (anti-duplication mapping).
4. `core/employees/jobs.py:74-162` (frozen `AIEmployee` +
   `JobContract` dataclass shapes) — read code, not docs.
5. `core/employees/mission_runner.py:1-230` (module docstring
   + lifecycle).
6. `core/employees/comms_docs_manager.py:1-122` (canonical
   per-employee comms wrapper pattern).

**Hard rule before opening a PR for Employee #5:** read
`EMPLOYEE_OS_PRIMITIVES.md` §2 + §4 in full. The 23-row "do
NOT build" matrix and the 7 explicit warnings exist because
each one cost real time before.

### Path C — "I want to understand governance"

1. `docs/research/governance_authority_evolution.md` [§1.4]
   — the canonical anchor (4 planes; 35 gates; 12 incidents;
   all Q1-Q12 answered).
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` row 17 (GovernanceState +
   KillSwitch).
3. `docs/research/employee_os_collaboration_patterns.md` §2
   rows 55-56 + §10 Q11 (collaboration audit's view of
   authority enforcement).
4. `core/models_governance.py:17-189` (GovernanceState +
   KillSwitch model definitions).
5. `core/employees/mission_runner.py:258-275` (authority
   warn-mode constants + S1264 design).
6. `docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`
   (authority contract observation design + Rigby SIGN edits).

**Big findings to internalize:** four governance planes don't
compose today (autonomy / authority / budget / human
governance). KillSwitch has full write path + TTL but **zero
dispatch consumers** — write surface works, enforcement
doesn't. `JobContract.authority` is observation-only;
enforcement blocked on Symbol Mapping prerequisite (P0 next
research per §5.2).

### Path D — "I want to build new communication"

1. `docs/research/employee_os_communication_substrate_audit.md`
   [§1.1] — esp. §8 reuse classifications and §7 known risks.
2. `docs/research/employee_os_communication_protocol_sketch.md`
   [§1.2] — concrete pattern to mirror.
3. `core/employees/comms.py:228-367`
   (`post_shift_report` — canonical bounded-comms helper).
4. `core/employees/comms_docs_manager.py:1-122` (thin
   wrapper pattern).
5. `core/models_messaging.py:21-141`
   (MessageThread / ThreadParticipant / DirectMessage shapes).

**Hard rule:** do NOT propose enabling
`messaging_tool.send_message` in any design. It is OFF by
design (per `EMPLOYEE_OS_PRIMITIVES.md` §4.7 and
substrate audit §8 DO-NOT-REUSE row). Free-form LLM outbound
is the wrong shape for structured comms; bounded helpers in
`core/employees/comms*.py` are the right shape.

### Path E — "I need to understand orchestration"

1. `docs/research/employee_os_collaboration_patterns.md` §3
   (12 collaboration flow diagrams) + §4 (delegation
   mechanism comparison table).
2. `docs/topics/celery-workers.md` (worker / queue topology).
3. `core/employees/mission_runner.py:1-1758` (one orchestrator).
4. `ai_core/agents/hybrid_executor.py:244,351` (the other
   orchestrator — Celery chain + group).
5. `core/agents/workflow_orchestration_agent.py:47,302`
   (ThreadPoolExecutor fan-out variant).

**Big finding to internalize:** there are **two orthogonal
durable orchestration paths** (Celery chain in
`hybrid_executor.py` vs. MissionRunner step loop in
`mission_runner.py`). They do NOT compose today. Choose one
based on durability needs; do not mix.

### Path F — "I want to understand autonomous execution"

1. `docs/topics/spider-network.md` + `docs/topics/initiative-pipeline.md`.
2. `docs/research/employee_os_collaboration_patterns.md` §3.6
   (Spider → Signal → Trigger → Work flow) and §3.7 (Spider →
   EventBus → Consumer Group flow).
3. `core/services/signal_aggregation_service.py:33-1161`
   (entity-token clustering; pattern detection).
4. `core/services/event_bus.py:21-728` (8 streams + DLQ).
5. `core/services/body_coordinator.py:110-300+` (9 body
   systems autonomic reflex layer).

**Gap to know:** autonomous→initiative auto-creation
(AutoTopic → Initiative) is UNCERTAIN per collaboration audit
§10 Q2 — no creation task traced. Treat as not-yet-wired.

### Path G — "I need to understand platform reliability"

1. `docs/research/employee_os_collaboration_patterns.md` §5
   (mission coordination — what survives process / Redis / DB
   restarts) and §7 (29 failure modes).
2. `docs/research/employee_os_communication_substrate_audit.md`
   §7 (12 incident classes).
3. `docs/AUDIT_FINDINGS.md` (canonical Celery deferred list,
   S1115 multi-batch audit).
4. `docs/topics/celery-workers.md` (queue + worker
   architecture).
5. `core/services/anthropic_client_factory.py:38-50` +
   `core/services/openai_client_factory.py:68-72`
   (centralized timeout contract — must use these factories).

**Hard rule:** any new LLM client call site MUST go through
the factory (per memory rules
`feedback_anthropic_client_factory` and
`feedback_openai_client_factory`). Bare `Anthropic()` /
`OpenAI()` defaults to 600s timeout, causing the zombie-thread
class documented in collaboration audit §7 row 17.

### Path H — "I need to understand the whole platform"

*Added S1273 v5.* This is the whole-platform onboarding path.
Use it when your work spans multiple domains or you're new to
the codebase.

1. `CLAUDE.md` (Quick Start + Working with Rigby + system stats).
2. `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor — glossary +
   subsystem summaries).
3. `docs/PLATFORM_INVENTORY.md` (runtime anchor — authoritative
   counts; regenerable via `generate_platform_inventory`).
4. `docs/research/platform_architecture_inventory.md` [§1.9] —
   the 32-domain map + 9 cross-domain flows + maturity matrix +
   11-mission roadmap.
5. Whichever specific §3.n inventory in §1.9 matches your work.
6. If that subsystem has an Employee OS-arc research doc
   (§1.1-§1.8), read it next.

**Big finding to internalize:** the platform combines four
historically-separate stacks (AI Studio + DBAO + Employee OS +
Revenue Pipeline) under one substrate. §1.9's §1 executive
summary + §5 duplicate/overlapping systems section will show you
where those stacks compose cleanly and where they don't.

---

## 3. Architecture Domains

The platform is partitioned into ~17 domains below (the S1268-
S1272 arc's view). For a **whole-platform 32-domain map**
(broader scope, added S1273 v5), see `docs/research/platform_
architecture_inventory.md` [§1.9] §2. The two are complementary:
this table is Employee-OS-adjacent depth; §1.9's table is
whole-platform breadth.

For each row, the table lists what research exists (in this
library), what is still missing, and current maturity.

| Domain | Existing research | Canonical anchors | Missing research | Maturity |
|---|---|---|---|---|
| **Employee OS — core** | §1.1, §1.2, §1.3 | EMPLOYEE_OS_PRIMITIVES.md; topics/employee-os.md | (none today; covered by §1.1 + §1.3) | **High** — 4 production employees, fully audited |
| **Mission System (MissionRunner)** | §1.3 (§2 row 19, §3.9, §6) | mission_runner.py (1758 lines); jobs.py:74-162 | Dedicated MissionRunner architecture doc (could lift from §1.3's flow + reuse rows) | **High** — production for 4 employees |
| **Governance** | §1.4 (full audit; 4 planes documented) + §1.3 (§2 rows 55-56) | models_governance.py | (well-covered; downstream is Cross-plane Composition — see §5.4) | **Medium-High** — primitives fully audited; freeze/safe_mode wired; KillSwitch enforcement missing |
| **Authority** | §1.4 (full audit; 68 entries / 30 prohibited / 35 gates) + §1.3 (§2 row 26 + §10 Q11) + §1.6 (Symbol Mapping — 57 unique action strings; 5 mapping options; 20 enforcement boundaries) + §1.7 (Actor Attribution — WHO composes with WHAT) + §1.8 (Authority Enforcement Design Space — 24 inputs / 20 boundaries / 12 modes / 6 options A-F / 33 incidents / 15 anti-patterns / 15 prereqs) | mission_runner.py:258-275 (S1264 warn-mode); jobs.py:41-52 (AuthorityLevel); llm_enforcer.py:200-262 (fail-open precedent) | **Symbol Mapping Option Selection Design** (recommended P0 next per §1.8 §14.1 — pick from §1.6's 5 options + Chris gate) | **Medium-High** — all three prereqs shipped as research (S1270 + S1271 + S1272); no design decision yet; enforcement remains observation-only |
| **Actor Identity / Attribution** | §1.7 (full audit; 19 identity concepts; 22 attribution surfaces; 15 historical failures; 25 identity registries; F11 executor/sponsor/principal role vocabulary) | `AIEmployee` (jobs.py:73-92); `UnifiedUser` (models/base/models.py:86); `_resolve_runs_as_user_id` (mission_runner.py:1585-1591); `canonicalize_agent_name` (deliverable_aliases.py:39-47) | (§1.7 F1: OpsRun has no user FK — largest attribution gap; downstream design gated by Symbol Mapping Option Selection per §1.8 §14.1) | **Medium** — mixed strong-FK / ambiguous-CharField attribution; role vocabulary proposed but not schema-enforced |
| **Authority Enforcement (design space)** | §1.8 (full design-space discovery; 6 options A-F; 12 modes; 15 anti-patterns; 15-prereq DAG) | S1264 warn-mode; LLMEnforcer fail-open pattern; MissionRunner `_emit_authority_contract_event` | Symbol Mapping Option Selection Design + downstream Authority Enforcement Design Decision (Chris-gated per §1.8 §14.3) | **Design-space only** — no runtime enforcement designed yet; **maintenance note:** enforce-mode requires §14.1 P0 selection first; do not treat §1.8 options as implementable without downstream Chris-gated design decision |
| **Communication (employee comms)** | §1.1 (full); §1.2 (specific path) | comms.py, comms_docs_manager.py, EMPLOYEE_OS_PRIMITIVES.md §4.7 | Inter-employee reply lane (§1.3 F4); cross-fleet messaging | **Medium** — outbound shift reports work; inter-employee design sketched but not built |
| **Messaging (raw substrate)** | §1.1 (§2 rows 35-37); §1.3 (§2 row 36) | models_messaging.py:21-141 | inbox UI semantics for `thread_kind='inter_employee_notice'` (frontend ticket, not research) | **High** — substrate is production |
| **Memory (employee / agent)** | (none in research library) | core/models_agent_memory.py | **Memory Architecture research doc** — esp. how do employees remember each other's past verdicts? | **Low / UNKNOWN** — no research yet |
| **Decision Making** | §1.3 (§2 rows 38-42 + §3.10) | models_human_interface.py; models_orchestration.py | Decision precedent + multi-stakeholder approvals (§1.3 §10 Q6) | **Medium** — HAI lifecycle is robust; collaborative decisions absent |
| **Human Interface** | §1.3 (§2 rows 38-42, 58-59) | HumanAttentionItem + HumanFeedbackRecord + HumanPreference; views_inbox.py | DM-arrived WebSocket event surfacing (frontend ticket) | **High** — HAI lifecycle service production |
| **Automation (workflow autopilot)** | §1.3 (§2 row 47 — `WorkspaceTrigger`) | models_skin_layer.py | `workspace_autopilot_tick` location UNKNOWN (§1.3 §10 Q1); needs trace | **Medium / UNKNOWN** |
| **Agents (BaseAgent + AGENT_MAP)** | §1.1 (§3); §1.3 (§2 rows 1-9) | core/agent_router.py; core/agents/base_agent.py; topics/agent-system.md | (well-covered) | **High** — 83 agents production |
| **Spiders** | §1.3 (§3.6 + §3.7) | ai_core/spiders/; topics/spider-network.md | (well-covered) | **High** — 80 spiders + 1.14M item hashes |
| **Signal Processing** | §1.3 (§2 rows 48-50) | signal_aggregation_service.py; content_scoring_service.py | AutoTopic → Initiative wiring (§1.3 §10 Q2) | **Medium** — clustering production; downstream uncertain |
| **Workflows (Initiative pipeline)** | §1.3 (§2 rows 43-44 + §3.8) | models_document_registry.py; topics/initiative-pipeline.md; DREAM_INITIATIVE_WORKFLOW.md | (Initiative is documented; cross-employee composition is not) | **High** (pipeline) / **Medium** (composition) |
| **Scheduling (beat)** | §1.3 (§3.11) + 5-agent scheduling sweep evidence | core/celery.py:37-797; topics/celery-workers.md; AUDIT_FINDINGS.md §12 | **Cross-employee scheduling research doc** | **Medium** — beat tasks documented; cross-employee handoffs absent |
| **Observability** | §1.3 (§6 evidence scoring) | OpsRunEvent + AgentExecution + ToolCallRecord + LLMCallEvent + CeleryTaskEvent | (well-covered) | **High** — five audit tables compose |
| **Telemetry (LLM costs)** | §1.3 (§2 rows 8, 63-64) | models_llm_telemetry.py | (well-covered) | **High** — cleanup watchdog + total-request bound |
| **Reliability** | §1.3 (§5 + §7) | anthropic_client_factory.py; openai_client_factory.py; cleanup beat tasks | (well-covered) | **High** — multi-layer defense |
| **Infrastructure** | (none in research library — runtime evidence only) | topics/infrastructure.md; topics/celery-workers.md; Procfile | Redis broker persistence config — UNKNOWN (§1.3 §10 Q5) | **Medium / UNKNOWN** |
| **Knowledge Pipeline** | (none in research library) | docs/KNOWLEDGE_PIPELINE.md | (covered by KNOWLEDGE_PIPELINE.md narrative) | **High** — production pipeline |
| **Revenue / Outreach / Engagement** *(new domain, added S1273 v5)* | §1.9 §3.32 (LIGHT coverage — models + services + agents enumerated; no canonical topic doc) | models_outreach.py:18 (OutreachDraft); models_engagement.py:18 (EngagementEvent); models_meeting.py:18 (Meeting); models_close_pack.py:20 (ClosePack); opportunity_pipeline_orchestrator.py; ops_autopilot/revenue.py + outreach_generation.py + engagement.py | **Revenue Pipeline canonical architecture doc** (models + services + agents + PA tools + outbound channel + attribution) — see §5.12 | **WORKING** (per §1.9 §3.32) — models + services + agents shipped; whether pipeline drives revenue in prod vs is scaffolding awaiting activation is UNKNOWN |

---

## 4. Architecture Dependency Graph

The library's documents build on each other in a specific
order. Reading them out of order is technically possible but
each downstream doc assumes its upstream context.

```
                ┌─────────────────────────────────────────┐
                │  PLATFORM_INVENTORY.md (runtime anchor) │
                │  PLATFORM_WHAT_IT_IS.md (narrative)     │
                └────────────────────┬────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │  EMPLOYEE_OS_PRIMITIVES.md          │
                    │  (canonical primitives + §2 anti-   │
                    │   duplication matrix)               │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  research/employee_os_communication_substrate_  │
        │  audit.md                                       │
        │  (Inventory of comms primitives + reuse class)  │
        └───────────────────┬─────────────────────────────┘
                            │
            ┌───────────────┴────────────────┐
            ▼                                ▼
┌───────────────────────────┐    ┌────────────────────────────────┐
│  research/employee_os_    │    │  research/employee_os_         │
│  communication_protocol_  │    │  collaboration_patterns.md     │
│  sketch.md                │    │  (Platform-wide inventory of   │
│  (One concrete path:      │    │  collaboration; 64-row table;  │
│  Auditor → Chief of Staff)│    │  11 substrates; 29 failures)   │
└──────────┬────────────────┘    └────────────────┬───────────────┘
           │                                      │
           ▼                                      ▼
┌───────────────────────────┐    ┌────────────────────────────────┐
│  [Future: v0 PR for the   │    │  research/governance_authority_│
│  protocol — gated by      │    │  evolution.md  [§1.4]          │
│  Chris's greenlight]      │    │  (4 planes; 35 gates; 12 inc.; │
│                           │    │  Symbol Mapping = P0 next)     │
└───────────────────────────┘    └────────────────┬───────────────┘
                                                  │
                                                  ▼
                                ┌──────────────────────────────────┐
                                │  research/symbol_mapping_        │
                                │  architecture.md  [§1.6]         │
                                │  (57 unique action strings; 5    │
                                │  mapping options A-E; 20         │
                                │  enforcement boundaries; SIGN-   │
                                │  with-edits from Rigby S1270)    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  research/actor_identity_        │
                                │  attribution_architecture.md     │
                                │  [§1.7]                          │
                                │  (19 identity concepts; 22       │
                                │  attribution surfaces; 25        │
                                │  registries; F11 executor/       │
                                │  sponsor/principal role vocab;   │
                                │  Rigby pressure-test SIGN-with-  │
                                │  edits S1271)                    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  research/authority_enforcement_ │
                                │  design_space.md  [§1.8]         │
                                │  (24 inputs; 20 boundaries; 12   │
                                │  modes; 6 options A-F; 15 anti-  │
                                │  patterns; 15-prereq DAG; Rigby  │
                                │  pressure-test SIGN-with-edits   │
                                │  S1272 — 3 SIGN-added boundaries │
                                │  WebSocket/Fleet/Spider)         │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  [Future research mission —      │
                                │  recommended P0 per §1.8 §14.1]  │
                                │  Symbol Mapping Option Selection │
                                │  Design (picks from §1.6's 5     │
                                │  options; Chris gate; converts   │
                                │  research to design decision)    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  [Further future research —      │
                                │  see §9 roadmap]                 │
                                │  Actor Role Propagation ·        │
                                │  Authority Enforcement Design    │
                                │  Decision · Trust Propagation ·  │
                                │  Memory · Mission Composition ·  │
                                │  Cross-Employee Scheduling · …   │
                                └──────────────────────────────────┘
```

**Sibling arc (added S1273 v5) — whole-platform inventory.**
`platform_architecture_inventory.md` [§1.9] is NOT downstream
of the Employee OS arc. It's a sibling arc off the same three
anchors:

```
                ┌─────────────────────────────────────────┐
                │  PLATFORM_INVENTORY.md (runtime anchor) │
                │  PLATFORM_WHAT_IT_IS.md (narrative)     │
                │  EMPLOYEE_OS_PRIMITIVES.md (primitives) │
                └────────────────────┬────────────────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       ▼                           ▼
        ┌──────────────────────────┐  ┌───────────────────────────┐
        │  Employee OS Arc         │  │  Whole-Platform Inventory │
        │  §1.1 → §1.2/§1.3 →      │  │  §1.9 (S1273)             │
        │  §1.4 → §1.6 → §1.7 →    │  │  32 domains + 9 flows +   │
        │  §1.8 (S1268-S1272)      │  │  11-mission roadmap       │
        └──────────────────────────┘  └───────────────────────────┘
```

§1.9 cites downstream findings from §1.4 (governance planes),
§1.6 (symbol mapping), and §1.7 (actor identity) where the
Employee-OS-arc research is the source of truth for a subset of
its findings. It does NOT depend on the arc's ordering.

**Reading the graph.** The two prior anchors at the top
(`PLATFORM_INVENTORY` + `PLATFORM_WHAT_IT_IS`) and the
primitives doc (`EMPLOYEE_OS_PRIMITIVES`) are *not* in the
research library but are **load-bearing context** for
everything in it. Any research doc that doesn't honor those
three is broken at the root.

The protocol sketch (§1.2) and the collaboration patterns
audit (§1.3) are siblings, both downstream of the substrate
audit (§1.1). They were written in the same session
(S1268) — the sketch came first, the wider audit came
second once Rigby's review of the sketch surfaced the broader
"how does collaboration work everywhere" question.

**Convention.** Every new research doc declares its parents
via the `companion_docs` frontmatter field. The dependency
graph above is reconstructable from those declarations.

---

## 5. Research Gaps

The library is **young** — 3 docs, all S1268. There are real
gaps. Below are the ones that have surfaced explicitly during
S1268 research, with priority and rationale. Each is a
*research* gap — i.e., something that should get its own
research doc before it gets implemented.

### 5.1 Governance + Authority Evolution — CLOSED S1269

**Closed by:** `docs/research/governance_authority_evolution.md`
(§1.4). Audit shipped 2026-06-30; Rigby SIGN-with-edits folded.
4 governance planes documented; 35 runtime gates inventoried;
warn-mode mechanics fully traced; 12 failure modes documented;
canonical foundation identified.

**Successor gap:** Symbol Mapping Architecture (see §5.2 below
— renumbered from prior §5.2; was P1, now P0 per §1.4 §11
recommendation).

### 5.2 Symbol Mapping Architecture — CLOSED S1270

**Closed by:** `docs/research/symbol_mapping_architecture.md`
(§1.6). Research shipped 2026-06-30; Rigby SIGN-with-edits
folded. 57 unique action strings enumerated across 68 total
entries. 5 mapping options (A steps self-declare / B tool
attribute / C hybrid / D central registry / E evidence-only)
inventoried with tradeoffs. 20 candidate enforcement layers
enumerated. 23 identifier registries classified (7 SAFE + 11
WRAPPER + 3 UNKNOWN post-Rigby-folded). §9 F11 blind spots
capture 7 architectural categories the design mission must
confront.

**Successor gap:** Authority Enforcement Design Space (see
§5.2b below) — first mission that composes §1.6 (WHAT) + §1.7
(WHO) into an actual enforcement gate.

### 5.2a Actor Identity & Attribution Architecture — CLOSED S1271

**Closed by:** `docs/research/actor_identity_attribution_architecture.md`
(§1.7). Research shipped 2026-06-30; Rigby pressure-test
SIGN-with-edits folded. 19 identity concepts inventoried, 22
attribution surfaces classified (13 Explicit / 2 Inferred / 4
Ambiguous / 1 Unreliable / 2 Missing), 14 identity shape
changes traced, 15 historical incidents catalogued (73%
effective case), 25 identity registries classified (14 SAFE
+ 7 WRAPPER + 1 DEPRECATED + 3 UNKNOWN), 17 enforcement
boundaries. **F11 introduces the executor_actor /
sponsor_actor / principal_user 3-role vocabulary** as
normative for downstream missions — treating any single field
as "the actor" without declaring which role it represents
produces "confidently wrong audit trails" (Rigby SIGN).

**Not a gap that pre-existed §5.2 explicitly**, but implicit
prerequisite that surfaced during §1.6 verifier loops (Symbol
Mapping cannot bind action_class without knowing which actor
attempted the action). Landed as an immediate follow-on same
day rather than deferred.

**Successor gap:** Authority Enforcement Design Space (see
§5.2b below).

### 5.2b Authority Enforcement Design Space — CLOSED S1272

**Closed by:** `docs/research/authority_enforcement_design_space.md`
(§1.8). Research shipped 2026-06-30; Rigby pressure-test
SIGN-with-edits folded (Medium confidence). 24 current
enforcement inputs classified; 20 candidate enforcement
boundaries (17 original + 3 SIGN-added: WebSocket / Fleet /
Spider); 12 enforcement modes with existing production
precedents for 8; 6 major design options A-F enumerated
neutrally (MissionRunner-centered / ToolDispatcher-centered /
Audit-first / Human-approval / Multi-layer / Governance-plane
composition); 33-incident historical matrix; 15 anti-patterns
(3 flagged as Tier-0 hazards: blocking all model writes,
enforcement before symbol mapping, silent enforcement); 15
prerequisites forming DAG (critical path Symbol Mapping →
Evidence Schema → Violation Event → Fallback → Layer choice →
Test Coverage + Human Review → Rollback → Per-Employee Opt-In →
Metrics Window → Trust + FP Thresholds). Named Symbol Mapping
Option Selection Design as the recommended P0 next research
per §14.1.

**Maintenance note:** §1.8 is **design-space research only**.
The 6 options A-F are enumerated for future consumption; none
is designated for implementation. Do not treat §1.8 as an
implementation greenlight — the downstream Authority
Enforcement Design Decision mission (see §14.3 in that doc)
requires Chris gate.

**Successor gap:** Symbol Mapping Option Selection Design (see
§5.2c below) — the first mission where the design space
narrows to a specific selection.

### 5.2c Symbol Mapping Option Selection Design (P0 — recommended next per §1.8 §14.1)

- **Why it matters.** §1.8 F6 (33-incident cluster of 7 —
  "Authority Symbol Mapping Gap") + F9 (Symbol Mapping choice
  constrains enforcement mode choice: Option E enables only
  5 of 12 modes; Options A/B/C/D enable all 12) + F11
  (15 prereqs form DAG with Symbol Mapping at critical-path
  root) all identify Symbol Mapping choice as the load-bearing
  predecessor to any enforcement design decision.
- **Priority.** P0. §1.8 §14.1 explicitly names this as the
  next mission. Rigby SIGN-clean on the ranking at S1272
  review.
- **Dependencies.** §1.6 (5 mapping options A-E enumerated),
  §1.7 (3-role vocabulary must be consumed), §1.8 (20
  boundaries + 12 modes + option compatibility matrix). No
  other dependencies.
- **Expected outcome.** A design decision doc (not a research
  doc) with Chris ratification. Should:
  - Evaluate the 5 §1.6 options against §1.8's 20 boundaries,
    12 modes, and 6 §9 design options
  - Recommend a v0 option (one, or hybrid) with explicit
    reversibility story
  - Identify the smallest reversible design that unlocks
    authority telemetry and future enforcement without
    overbuilding
  - Enumerate what must remain out-of-scope for v0 (per S1264
    "smallest honest thing" pattern)
  - Rigby SIGN review at close
  - **Chris gates the actual selection.**
- **Type.** Design decision — second design mission in the
  STAGE 2/3 arc per §9 pacing note.

### 5.3 Trust Propagation Model (P1)

- **Why it matters.** S1264 shipped `authority_contract_observed`
  in warn-mode only. Per `mission_runner.py:264-894`, the event
  emits shape evidence but **never blocks**. Every research doc
  in this library has hit "but warn-mode doesn't enforce" as a
  boundary. Cross-employee dispatch is the first surface where
  the boundary actually matters.
- **Priority.** P0 next research mission per §1.3's §11
  recommendation. Rigby SIGN-clean on that recommendation.
- **Dependencies.** §1.3 (esp. §10 Q11), `mission_runner.py:258-275`,
  `docs/handoffs/SESSION_1264_*.md`,
  `core/employees/jobs.py:489-505` (Platform Auditor
  authority dict shape).
- **Expected outcome.** A research doc that scopes the
  symbol-mapping work needed to take authority strings (like
  `"recommend_remediations"`) and bind them to runtime symbols
  (tool names, FK methods). Plus trust-propagation primitives
  (when Employee A trusts Employee B's verdict, what's the
  contract?). Plus boundary cases (what happens when an
  authority contract changes mid-run?).

### 5.4 Memory Architecture (P1)

- **Why it matters.** Employees do not "remember" each other's
  past verdicts in their reasoning today. Bug Triage *queries*
  OpsRun rows from other employees (read-only composition), but
  there is no synthesized memory layer — no "last week the
  Auditor flagged this same finding" awareness inside the
  reasoning context. Derived from §1.3 §1 Finding F4 (no
  in-platform A→A reply contract today) — memory naturally
  falls out as a sub-question under trust propagation once
  inter-employee read-of-other-employee semantics exist.
- **Priority.** P1. Probably falls out of the Governance + Authority
  research naturally — but if it doesn't, it deserves its own
  pass.
- **Dependencies.** Governance research (above);
  `core/models_agent_memory.py` (current per-agent memory shape).
- **Expected outcome.** A doc that maps the existing
  `AgentMemory` / `AgentLearning` / `LearningInsight` /
  `SharedKnowledge` primitives, identifies whether they're
  shared-readable across employees, and proposes (research-only)
  what a "cross-employee episodic memory" layer would reuse vs.
  invent.

### 5.5 Cross-Employee Scheduling (P1)

- **Why it matters.** Per §1.3 §1 Finding F4 and Q8, the
  minimum missing runtime surface for inter-employee delegation
  is **a durable "subscribe-to-(employee, verdict)" primitive**
  that routes verdicts to a target employee's *next mission's
  preflight*. Today's AgentFollowupSubscription handles
  conversation-scoped wakeups, not mission-to-mission handoffs.
- **Priority.** P1 — depends on Governance research closing
  first because authority semantics gate the dispatch.
- **Dependencies.** §1.2 (protocol sketch), §1.3 (§2 rows 27-29).
- **Expected outcome.** A research doc that scopes whether the
  primitive is (a) a new model, (b) an extension of
  `AgentFollowupSubscription`, or (c) a pure read-side query
  pattern. Not a design — just the scope of the smallest
  missing piece.

### 5.6 Mission Composition (P1)

- **Why it matters.** Per Rigby S1268 review architectural-blind-
  spot note (folded into §1.3 §10 Q12), the two durable
  orchestration paths (Celery chain vs. MissionRunner step
  loop) don't compose. When a future mission needs to chain
  Celery tasks across employees, the canonical idempotency key
  across substrates is an open question — calendar-date scope
  (MissionRunner) vs. task_id (Celery) vs. event_id (EventBus)
  vs. UUID (AgentExecution) don't reconcile.
- **Priority.** P1 — touches Reliability + Observability if
  done poorly.
- **Dependencies.** §1.3 (Q12), `topics/celery-workers.md`.
- **Expected outcome.** A doc that names the canonical
  idempotency key (or proves none exists and what would have to
  give).

### 5.7 Observability / Failure Recovery (P2 — already strong)

- **Why it matters.** Observability is well-covered by §1.3 §6
  (evidence-and-auditability scoring). Failure recovery is
  well-covered by §1.3 §7 (29 documented failure modes).
- **Priority.** P2. Most failure classes are already
  documented with mitigations. A dedicated doc would be a
  consolidation pass, not new research.
- **Dependencies.** §1.3 §6 + §7; `docs/AUDIT_FINDINGS.md`.
- **Expected outcome.** Optional consolidated "failure
  taxonomy" doc that pulls the §7 incidents into a single
  reference. Not blocking.

### 5.8 Security Model / Permission Model (P2 — needs scoping)

- **Why it matters.** Service-token auth is referenced
  (`core/auth_middleware.py:113` only documents
  `PA_DB_HEALTH_RPC_TOKEN`), but the full scope of
  dispatch surfaces requiring auth is UNKNOWN per substrate
  audit §9 Q3. Cross-fleet messaging requires this answered.
- **Priority.** P2 — only blocking if a future research
  mission wants to cross fleet boundaries.
- **Dependencies.** TBD; needs an initial scoping pass to
  even know what to audit.
- **Expected outcome.** First a *scoping* doc (one page) to
  identify which surfaces need auth; then full research if the
  surface is non-trivial.

### 5.9 Configuration Architecture (P3 — possibly out of scope)

- **Why it matters.** Feature flags
  (`RIGBY_EVENT_INTAKE_ENABLED`, `MESSAGING_TOOL_ALLOW_SEND`,
  `CTO_DIAGNOSTIC_ENABLED`, `COO_DIAGNOSTIC_ENABLED`) are
  scattered. There may be an implicit convention but no
  documented one.
- **Priority.** P3 — UNKNOWN whether this needs research or
  just a one-page note in
  `docs/00-START-HERE/DOC_LIFECYCLE.md`.
- **Dependencies.** TBD.
- **Expected outcome.** Either a one-page convention note OR
  a scoping doc.

### 5.10 Knowledge Graph (P? — not raised yet)

- **Why it matters.** Mentioned in the mission spec as a
  candidate. Not raised in any prior research. No production
  evidence found for a knowledge-graph layer today.
- **Priority.** P? — premature. Surface only if a future
  research mission has a specific use case for it.

### 5.11 Focus Mode Inventory (P? — flagged by Rigby S1269 review)

- **Why it matters.** Rigby's S1269 review on §1.4
  noted that **"focus mode"** is a governance-like throttle
  that may live outside the GovernanceState/KillSwitch plane.
  §1.4 didn't scope focus mode (wasn't part of the original
  evidence sweeps). A follow-up scoping pass should determine
  whether focus mode is a fifth governance plane, a sub-feature
  of one of the existing four, or a distinct concept entirely.
- **Priority.** P? — depends on whether Employee OS reasoning
  has any dependency on focus mode state. If not, deferred.
- **Dependencies.** §1.4 (governance audit's §10.8 flags it).
- **Expected outcome.** A scoping doc (one page) to identify
  the surfaces, NOT a full audit.

### 5.12 Revenue / Outreach / Engagement Pipeline Canonical Architecture (P0-parallel — added S1273 v5 per Rigby review)

- **Why it matters.** Rigby's S1273 review on §1.9 caught this
  as a missed whole-platform domain — it exists in tools/models/
  services but is not represented as an end-to-end platform
  subsystem with a canonical architecture doc. Missing this
  research means any revenue-adjacent feature has no baseline
  to work from.
- **Priority.** P0 (parallel with §5.2c Symbol Mapping Option
  Selection). Different scope than the Employee OS arc; runs
  independently.
- **Dependencies.** §1.9 §3.32 (domain inventory shell), §1.9
  §4.9 (cross-domain flow), models_outreach.py + models_
  engagement.py + models_meeting.py + models_close_pack.py,
  ops_autopilot/revenue.py + outreach_generation.py +
  engagement.py + impact.py, opportunity_pipeline_orchestrator.py.
- **Expected outcome.** A canonical architecture doc covering
  models + services + agents + PA tools + outbound channel
  integration + revenue-attribution logic. Verify runtime state
  vs aspirational docs (`MASTER_PLAN_CREATIVE_INTELLIGENCE_
  EMPIRE.md`, external `BILLING_MONETIZATION_SYSTEM.md`). Rigby
  SIGN review. Result: promotes §1.9 §3.32 coverage from LIGHT
  to DEEP + potentially spawns a §1.10 research doc.

### 5.13 Observability Deduplication Audit (P1 — added S1273 v5)

- **Why it matters.** Per §1.9 §5.7, the platform has 5 parallel
  execution telemetry layers (`CeleryTaskEvent`, `LLMCallEvent`,
  `AgentExecution`, `ToolCallRecord`, `OpsRunEvent`) plus 14+
  event-shaped audit models. Whether they're necessary and non-
  overlapping or duplicate is undocumented. Any future
  observability feature is guessing at the design boundary.
- **Priority.** P1. Touches every future observability feature.
- **Dependencies.** `docs/EVENT_SYSTEM_INVENTORY.md`, §1.9 §3.25,
  §1.9 §5.7.
- **Expected outcome.** Trace a single "agent executes a tool
  that calls the LLM" scenario through all 5 execution telemetry
  layers + adjacent audit tables. Recommend rationalization
  (which to keep, which to deprecate, which to merge). Rigby
  SIGN review.

### 5.14 Sports / DBAO ↔ AI Studio Integration Sketch (P1 — added S1273 v5)

- **Why it matters.** Per §1.9 §3.10 + §1.9 §4.8, the DBAO
  stack (sports/odds/betting agents + models) is
  operationally-separate from AI Studio (content/signals/
  initiatives/deliverables). `sports_odds` is not a valid
  `SignalCluster` data_type track; sports predictions do NOT
  auto-create Initiatives; betting outcomes NOT fed to
  deliberation. Resolves the platform's biggest structural
  question ("what IS Donkey Betz — one platform or two?").
- **Priority.** P1. Structural question; unblocks content-
  pipeline decisions for sports content and betting-related
  deliberation.
- **Dependencies.** §1.9 §3.10 (DBAO inventory), §1.9 §3.9
  (Signal Engine), §1.9 §3.11 (Content Pipeline), §1.9 §3.12
  (Initiative Pipeline), §1.9 §4.8 (Sports flow).
- **Expected outcome.** Research doc documenting whether and how
  MLPrediction / PlacedWager / SharpAction outcomes should feed
  Signal / Initiative / Deliverable surfaces. Alternative:
  documented intentional island. Rigby SIGN review.

---

## 6. Research Principles

The principles below are extracted from the three S1268 docs
and the verifier-loop pattern they all share. They are not
opinion — they are what *worked* on the first three docs,
verified by Rigby's SIGN reviews.

1. **Evidence before opinion.** Every claim in a research doc
   carries a file:line cite or is marked UNKNOWN. There is no
   third option. "I think the system does X" without a cite is
   forbidden.
2. **Inventory before implementation.** Before you can propose
   a primitive, you must list the existing primitives that
   already cover the same surface. Anti-duplication is load-
   bearing per `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1.
3. **Reuse before invention.** "Wrapper" beats "new model"
   beats "new admin UI." If a wrapper fits, the new model
   doesn't ship.
4. **Architecture before code.** Research docs exist to make
   PRs small. If a PR is small because the research is solid,
   the team has won.
5. **Document uncertainty.** When evidence is thin, mark
   UNKNOWN. Don't guess; don't fill gaps with plausible
   inference. The UNKNOWN list in §10 of each doc is the
   honest seed for the next research mission.
6. **Never silently assume.** When two doc-claims disagree
   (substrate audit said 6 EventBus streams; runtime says 8),
   the runtime wins per `DOC_LIFECYCLE.md` §2c. Flag the drift
   in the new doc; do not silently inherit the wrong number.
7. **Use verifier loops.** The doc author re-reads
   sub-agent cites by direct Grep/Read before synthesizing.
   No exceptions.
8. **Rigby independent review before architectural
   decisions.** Every research doc gets routed to Rigby via
   `tools/pa_local.sh` on the S1268 pinned conversation. The
   verdict (SIGN-clean / SIGN-with-edits / NEEDS-MORE) is
   recorded in the `verifier_loop` frontmatter field. Edits
   are folded before the doc is considered Active.
9. **Frontmatter declares lineage.** Every research doc lists
   its `companion_docs` so the dependency graph in §4 is
   reconstructable. If you don't declare your parents, you're
   not ready to publish.
10. **Authority is the only "must change" boundary.**
    Research-only missions don't touch runtime. The single
    exception: if mid-doc you discover that a prior research
    claim is wrong, the doc surfaces it (drift call) but does
    not patch the prior doc — patching happens in a separate
    pass with its own review.

---

## 7. Decision Matrix — "If you're about to work on…"

A pre-PR sanity gate. Find the row that matches your work;
read the documents in column 2 first. Skipping the read is the
fastest way to land a PR that violates the anti-duplication
matrix or re-introduces a closed failure class.

| About to work on… | Read these first |
|---|---|
| **Employee communication (anything)** | §1.1 + §1.2 + `EMPLOYEE_OS_PRIMITIVES.md` §4.7 (messaging_tool send guard) |
| **A new AI Employee** | Path B in full + `EMPLOYEE_OS_PRIMITIVES.md` §5 quick-start |
| **MissionRunner internals** | §1.3 §2 rows 17-23 + `mission_runner.py:1-230` + S1267 handoff |
| **`MissionRunnerConfig.auto_emit_verdict` semantics** | §1.3 Executive Summary item 6 (corrected by Rigby S1268 SIGN-with-edits) + §1.3 §2 row 19 + §1.3 §7 row 29 (protocol invariant change) + `core/employees/mission_runner.py:1127-1145` |
| **Governance flags or modes** | §1.4 §2.1 (full autonomy plane inventory) + §1.4 §4.6 (5 autonomy gates incl. KillSwitch UNKNOWN) + Path C |
| **Authority enforcement (vs. observation)** | §1.6 (5 mapping options + 20 boundaries) + §1.7 (17 boundaries + 3-role vocabulary) + §1.4 §3 (full lifecycle trace) + §1.4 §4.7 (authority plane gates) + §5.2b (Authority Enforcement Design Space P0 next) + S1264 handoff |
| **Anything using `JobContract.authority`** | §1.6 §2 (57 unique strings enumerated) + §1.6 §5 (mapping options A-E) + §1.6 §9 F1-F10 + §1.7 F11 + §1.7 §8.5 (executor/sponsor/principal roles) — a policy string is not a runtime symbol; do NOT assume it enforces anything today |
| **Actor identity on any new model / audit surface** | §1.7 §3.1 (22 attribution surfaces classified) + §1.7 §8.5 (3-role vocabulary) + §1.7 F11 — declare which of executor_actor / sponsor_actor / principal_user the field represents |
| **Adding `user` FK to OpsRun (or any "actor" field)** | §1.7 F1 + §1.7 F11 + §1.7 §13.1 — DO NOT ship without role clarity first; §1.7 explicitly warns adding a "user" field to OpsRun without role clarity codifies the executor / principal conflation as schema |
| **Any code using `agent_name` CharField** (ToolCallRecord / AgentExecution.owner_agent / LLMCallEvent) | §1.7 F4 (three ambiguous fields, undefined delegator-vs-executor semantics) + §1.7 §3.3 (evidence) — DO NOT assume the string is either delegator or executor; trace the call chain |
| **Any code using `runs_as_username` or `_resolve_runs_as_user_id`** | §1.7 §2.4 + §1.7 F3 (silent-None on missing User) + §1.7 F11 (this is a principal_user selector, NOT the executor_actor) — treating it as "actor" is a documented anti-pattern |
| **Duplicate Agent row risk** (any new agent-creation site) | §1.7 F5 (recurring failure class per S1263 PR #2754 + migration 0374) + `deliverable_aliases.py:33-47` (`canonicalize_agent_name` + `AGENT_NAME_ALIASES`) — must canonicalize at write time |
| **PA tool actor / user context propagation** | §1.7 §7 (17 boundaries; F6 identifies 3 structural drop points) + §1.6 §6 (20 symbol boundaries) + `tool_dispatcher.py:687-720` (`AssistantProfile.get_allowed_tools` is the ONLY canonical-actor gate today per §1.7 F7) |
| **Any authority enforcement idea** | §1.8 §9 (6 options A-F evaluated neutrally) + §1.8 §10 (15 anti-patterns incl. Tier-0 hazards) + §1.8 §11 (15-prereq DAG) — DO NOT ship enforce-mode before §5.2c Symbol Mapping Option Selection lands + Chris gates |
| **`AuthorityLevel` enum usage anywhere new** | §1.8 F1 — enum has exactly 1 runtime consumer today (shape-counter at `mission_runner.py:864-867`); adding decision-making consumer is a design-decision-scoped change |
| **New enforcement gate (INLINE)** | §1.8 F8 (LLMEnforcer fail-open precedent at `llm_enforcer.py:237-238`) + §1.8 §11 prereq #5 (fallback behavior must be explicit) — cite fail-open vs. fail-closed rationale |
| **Adding action_class to any audit model** | §1.8 §11 prereq #3 (Evidence Event Schema) + §11 prereq #4 (Violation Event Schema) — schema shape must precede any model migration |
| **WebSocket / Fleet / Spider handler that touches employee-scoped work** | §1.8 §3 rows 18-20 (added per Rigby SIGN pressure-test) — these boundaries are named but not yet mode-tabulated; design mission scope |
| **Cross-plane governance interaction (authority × autonomy × budget × human)** | §1.8 §7.5 (8 new composition questions) + §1.4 F1 (planes don't compose today) — this is deferred future research per §1.8 §14.4 |
| **KillSwitch (arming, status, enforcement)** | §1.4 §2.1 row 2 + §1.4 §4.6 (UNKNOWN row) + §1.4 §8 F3 (write-only finding) — DO NOT assume KillSwitch blocks dispatch today |
| **Budget freeze / LLM cost gates** | §1.4 §2.3 + §1.4 §8 F4 (one-way sync + desync risk) + `core/llm_enforcer.py:200-260` |
| **Human attention lifecycle (auto-approve / escalate)** | §1.4 §2.4 + §1.4 §5 (full flow + 7-condition auto-approve gate + escalation ladder) |
| **Adding any new tool to PA** | §1.1 §4.4 (handler/schema delta gotcha) + memory rule `feedback_llm_autofills_boolean_params_with_false.md` |
| **`messaging_tool` (any change)** | `EMPLOYEE_OS_PRIMITIVES.md` §4.7 + §1.1 §8 DO-NOT-REUSE row + `td_handlers_core.py:3693-3711` |
| **Mission scheduling (any new beat)** | Path E + `topics/celery-workers.md` + `EMPLOYEE_OS_PRIMITIVES.md` §4.6 (app.conf.imports requirement) |
| **Observability or audit chain** | §1.3 §6 (evidence-and-auditability scoring) + §1.3 §2 rows 7-9 |
| **Reliability / timeout / retry policy** | Path G + §1.3 §7 (rows 10, 17, 18, 19 esp.) |
| **Escalation surfaces** | §1.3 §3.5 (HAI creators) + §1.3 §3.9 (MissionRunner escalation) + §1.2 §8.1 (Auditor has no HAI creation authority) |
| **Human attention (HAI lifecycle)** | §1.3 §2 rows 38-41 + §3.5 + `core/services/human_attention_lifecycle.py:36-728` |
| **Deliverable creation / status flips** | Memory rules `feedback_deliverable_tool_use_append_for_large_payloads`, `feedback_deliverable_status_via_content_complete`, `feedback_deliverable_create_defaults_to_completed` + §1.1 §7.8 |
| **Spider → downstream work chains** | Path F + §1.3 §3.6 + §3.7 |
| **Anything that says "new model"** | `EMPLOYEE_OS_PRIMITIVES.md` §2 (anti-duplication matrix) + §1.3 §9 (anti-duplication analysis). If a row matches, you are not adding a model. |
| **Onboarding / any cross-domain scoping work** *(added S1273 v5)* | §1.9 whole-platform inventory (32-domain map + 9 cross-domain flows) — start here for shape of the system. Then dive into whichever §3.n row matches your work + cited Employee-OS-arc docs. |
| **Anything touching Revenue / Outreach / Engagement / Meeting / ClosePack** *(added S1273 v5)* | §1.9 §3.32 + §1.9 §4.9 + §5.12 (canonical architecture doc gap) — DO NOT assume the pipeline flow described in aspirational docs (`MASTER_PLAN_CREATIVE_INTELLIGENCE_EMPIRE.md`, external `BILLING_MONETIZATION_SYSTEM.md`) matches runtime; verify. |
| **Anything sports/betting-adjacent that touches content or signals** *(added S1273 v5)* | §1.9 §3.10 (DBAO inventory) + §1.9 §4.8 (Sports flow) + §5.14 (Integration Sketch gap). The two sides do NOT currently compose (`sports_odds` is not a valid SignalCluster data_type); do NOT assume they do. |

---

## 8. Architecture Timeline

The library is young. Here is the actual chronology with
influence callouts.

| When | Doc | What it added | Influenced |
|---|---|---|---|
| **S1268 P0 #1** (2026-06-30) | `employee_os_communication_substrate_audit.md` (§1.1) | First inventory of comms primitives between AI employees. 36-row table. Reuse classifications. 12 incident-class failure history. Rigby SIGN-clean. | Made §1.2 possible — the protocol sketch reused the SAFE rows directly. Also stated EventBus had "6 named streams" at line 135 — runtime is **8** per `event_bus.py:21-30`. The drift was caught in §1.3 §12 and Rigby independently corroborated it. The substrate audit text itself has **not** been amended (research-only constraint per S1268); the drift is flagged in §1.3 §12 (cross-reference + documentation drift table) and propagated forward as the canonical value. |
| **S1268 P0 #2** (2026-06-30) | `employee_os_communication_protocol_sketch.md` (§1.2) | First concrete inter-employee write path scoped (Platform Auditor → Chief of Staff). Helper signature, metadata envelope, threading model, 3-layer dedupe, terminal-gate, expires_at freshness boundary. Rigby SIGN-with-edits — 2 substantive edits folded (L3 helper-side dedupe + cadence Option A default). | Surfaced the question "but how does collaboration work *everywhere else* on the platform?" — which became §1.3. |
| **S1268 P0 #3** (2026-06-30) | `employee_os_collaboration_patterns.md` (§1.3) | Platform-wide audit. 64-row primitive inventory. 11 distinct collaboration substrates. 12 flow diagrams. 29 documented failure modes (12 new). Q1-Q8 answered. Rigby SIGN-with-edits — 1 substantive correction folded (MissionRunner verdict event is conditional, not guaranteed) + 1 architectural blind-spot note added (canonical idempotency key across orchestration paths). | Set the recommendation for the next research mission (Governance + Authority Evolution). Surfaced gaps that become §5.1–§5.7. |
| **S1268 P0 #4** (2026-06-30) | `ARCHITECTURE_INDEX.md` (this doc) | The first navigation / index doc for the research library. Establishes the corpus's identity, dependency graph, and maintenance rules. | Will be cited by every future research doc's `companion_docs`. |
| **S1269** (2026-06-30) | `governance_authority_evolution.md` (§1.4) | First architectural-discovery audit of the governance + authority surface. 63-row primitive inventory across 4 planes. 35 runtime gates. 12 governance-specific failure modes (3 new beyond S1268 collaboration audit baseline). 48 SAFE / 11 WRAPPER / 0 DO-NOT-REUSE / 0 DEPRECATED / 3 UNKNOWN. Rigby SIGN-with-edits (plane-count framing consistency, gate-count typo, two clarifications folded). | Set Symbol Mapping Architecture as the recommended P0 next research mission. Index v2 updated per maintenance rules §10.1 (this row + §1.4 + §3 domain map + §4 dependency graph + §5 gap recategorization + §7 decision matrix expansion + §9 roadmap promotion). |
| **S1270** (2026-06-30) | `symbol_mapping_architecture.md` (§1.6) | First architectural-discovery of the WHAT question. 57 unique action_class strings (68 total entries) enumerated. 5 mapping options (A steps self-declare / B tool attribute / C hybrid / D central registry / E evidence-only) with tradeoffs. 20 candidate enforcement layers. 23 identifier registries classified. 23 historical incidents (5 YES + 10 PARTIALLY + 8 NO). F1-F11 findings incl. F11 (7 architectural blind spots via Rigby SIGN). Rigby SIGN-with-edits — 2 must-fix (§8 `_AuthorityContractMalformedError` scope narrowed; §2.6 parallel-vocabulary type/shape anchor added) + 3 optional (I-S4 wording, I-S3 dual-cite, Option E disclaimer) + 2 discoverability (AssistantProfile registry, §2.4 normalization caveat) folded. | Established the "WHAT" half of the enforcement primitive. Surfaced the WHO question that became §1.7 (Actor Attribution) as an immediate follow-on same session. |
| **S1271** (2026-06-30) | `actor_identity_attribution_architecture.md` (§1.7) | First architectural-discovery of the WHO question. 19 identity concepts. 22 attribution surfaces classified (13 Explicit / 2 Inferred / 4 Ambiguous / 1 Unreliable / 2 Missing including OpsRun). 14 identity shape changes + 3 structural drop boundaries (HTTP→Celery, MissionRunner config→OpsRun, MissionRunner→Step.fn). 15 historical incidents (7 YES + 4 PARTIALLY + 4 NO — 73% effective case). 25 identity registries (14 SAFE + 7 WRAPPER + 0 DO-NOT-REUSE + 1 DEPRECATED + 3 UNKNOWN). 17 enforcement boundaries. Rigby pressure-test SIGN-with-edits, Medium confidence — 4 must-fix folded incl. **§8.5 introducing the executor_actor / sponsor_actor / principal_user 3-role vocabulary as normative** (biggest architectural risk: conflating the three into a single "actor" label). F1 + F9 language softened per Rigby. §3.5 added inventorying attribution patterns the platform does NOT ship. §9.4 Attribution-first counterargument acknowledged. §5 role-confusion framing note. | Established the "WHO" half of the enforcement primitive. Together with §1.6, closes the composite prereq. Set Authority Enforcement Design Space as recommended P0 next research (design mission that composes both). Index v3 updated per §10.1 (this row + §1.7 row above + §1.6 row above + §3 domain map + §4 dependency graph + §5 gap closure + §7 decision matrix expansion + §9 roadmap advancement). |
| **S1273** (2026-07-01) | `platform_architecture_inventory.md` (§1.9) | First whole-platform architectural inventory — the counterpart to the Employee-OS-focused §1.1-§1.8 arc. Six parallel Explore sub-agent sweeps synthesized into 32 domains (Cognition & agents: 7 / Data ingestion: 4 / Content & workflow: 2 / Revenue & GTM: 1 / Knowledge & memory: 3 / Human interface: 6 / API: 1 / Governance & ops: 4 / Infrastructure: 4). 9 cross-domain flows. 8 duplicate/overlapping system categories. Architecture Maturity Matrix rating every domain across Coverage / Maturity / Operational Health / Drift Risk / Debt Risk. 11-mission recommended research roadmap. Rigby SIGN-with-edits, Medium confidence, via fresh isolation pin `pa-02cfd3206302352f` (kept separate from shared S1270+ arc pin `pa-cbcc410b32714f60` per Chris's context-crossing directive). 6 substantive edits folded: (1) added missed §3.32 Revenue / Outreach / Engagement Pipeline domain + §4.9 flow — Rigby caught this as biggest missing platform subsystem; (2) downgraded §3.27 Auth STABLE → PARTIAL with trust-boundary enumeration; (3) upgraded §3.7 LLM Provider Registry WORKING → STABLE (core; failover missing); (4) tightened §1 Exec Summary count language; (5) added §3.31 Event Bus vs Observability separation-of-concerns paragraph; (6) expanded §9 roadmap 10 → 11 missions with Revenue Pipeline canonical architecture doc elevated to #2. | Established the whole-platform counterpart to the Employee-OS-focused arc. Chris's direction at close: "the next cleanup should be updating ARCHITECTURE_INDEX.md so this becomes the whole-platform counterpart to the Employee OS research library." Index v5 updated per §10.1 (this row + §1.9 row + §1 preamble rewrite + Path H reading path + §3 Revenue Pipeline domain row + §4 sibling-arc dependency graph extension + §5.12/§5.13/§5.14 gap entries + §7 decision matrix +3 whole-platform rows + §9 roadmap lateral research expansion referencing the 11-mission whole-platform roadmap in §1.9). Also caught + corrected v4 frontmatter drift — prior pass added Appendix C but never bumped last_verified line. |
| **S1272** (2026-06-30) | `authority_enforcement_design_space.md` (§1.8) | First design-space research — the mission that consumes S1270 + S1271 as INPUT premises and enumerates enforcement design options without picking. 24 enforcement inputs (13 RUNTIME-VERIFIED / 7 OBSERVATION-ONLY / 3 ASPIRATIONAL / 1 UNKNOWN + 8 GAPS). 20 candidate enforcement boundaries (17 original + 3 Rigby SIGN-added: WebSocket, Fleet, Spider — closing the biggest boundary-completeness gap). 12 enforcement modes with 8 existing production precedents; 4 without analog. 204-cell boundary × mode compatibility matrix (17-row form; 3 SIGN-added boundaries not yet cross-tabulated). 4-per-level AuthorityLevel semantics (16 interpretations, none chosen). 11 canonical actor-role scenarios × 3 roles + audit path. 4-plane governance composition with 8 new questions + 1 existing cross-plane touch. 33-incident consolidated historical matrix. **6 major design options A-F enumerated neutrally** (MissionRunner-centered / ToolDispatcher-centered / Audit-first / Human-approval / Multi-layer / Governance-plane composition). 15 anti-patterns (3 Tier-0 hazards: blocking all model writes, enforcement before symbol mapping, silent enforcement). 15-prereq DAG. Rigby pressure-test SIGN-with-edits, Medium confidence — 8 must-fix folded: §3 gained 3 first-class boundaries (WebSocket, Fleet, Spider); §9.0 neutrality guardrail; §9.1 + §9.2 annotation-burden failure modes; §9.6 policy-ossification risk; §8.4 rephrased separating prevent-modes from audit/warn modes; §10 Tier-0 hazards callout; §6.1 role-propagation rule of thumb; §14 P0/P1 dependency-not-preference semantics + §14.2 (i)/(ii) split. F1 (AuthorityLevel has 1 runtime consumer, a shape-counter) and F8 (LLMEnforcer fail-open precedent) are load-bearing findings. | Established the design space for authority enforcement. **First mission carrying design-space content per §9 STAGE 2 pacing note.** Set Symbol Mapping Option Selection Design as recommended P0 next research (§14.1). Maintenance note: this doc is **design-space only** — the 6 options A-F are for future consumption, not implementation. Index v4 updated per §10.1 (this row + §1.8 row + §3 domain map + §4 dependency graph + §5 gap closure §5.2b + new §5.2c + §7 decision matrix expansion + §9 roadmap advancement STAGE 2 → STAGE 3). |

**Pattern observation (updated S1273 v5).** The library grew
in two waves. First wave: 5 docs in 5 sessions (S1268/S1269/
S1270/S1271/S1272) — the Employee OS depth arc following the
"each doc names the next" discipline. Second wave (S1273):
a single whole-platform inventory doc that opens a sibling arc
alongside the depth arc. The library's *next* growth events
are now split across two arcs: (a) the Employee OS arc's STAGE
3 Symbol Mapping Option Selection Design (the first mission
that is a *design decision* gated on Chris), and (b) the
whole-platform arc's top-3 next missions per §1.9 §9 —
Revenue Pipeline canonical architecture (§5.12), Observability
Deduplication Audit (§5.13), Sports/DBAO ↔ AI Studio
Integration Sketch (§5.14). Parallel-safe if pursued
independently.

---

## 9. Future Research Roadmap

Not a design. Not a build plan. A recommended *research*
ordering to minimize architectural uncertainty.

The ordering rule: each research mission unlocks the next.
Skipping a dependency means the downstream doc has to invent
context it should have inherited.

```
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 0 — Governance + Authority Evolution  ✓ CLOSED S1269     │
│                                                                  │
│  Shipped: docs/research/governance_authority_evolution.md       │
│  4 governance planes; 35 runtime gates; 12 failure modes;       │
│  authority enforcement blocked on Symbol Mapping prereq         │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1 — Symbol Mapping Architecture  ✓ CLOSED S1270          │
│                                                                  │
│  Shipped: docs/research/symbol_mapping_architecture.md          │
│  57 unique action_class strings; 5 mapping options (A-E);       │
│  20 enforcement boundaries; 23 identifier registries; F11       │
│  captures 7 architectural blind spots. Rigby SIGN-with-edits    │
│  (2 must-fix + 3 optional + 2 discoverability folded).          │
│                                                                  │
│  Answered: WHAT action happened?                                │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1b — Actor Identity & Attribution  ✓ CLOSED S1271        │
│  (same-session follow-on to STAGE 1; surfaced during Symbol     │
│   Mapping verifier loops as the composite prereq)               │
│                                                                  │
│  Shipped: docs/research/actor_identity_attribution_             │
│           architecture.md                                       │
│  19 identity concepts; 22 attribution surfaces (F1: OpsRun has  │
│  no user FK); 15 historical failures; 25 registries; §8.5       │
│  executor/sponsor/principal 3-role vocabulary; F11 warning      │
│  against single-actor label conflation. Rigby pressure-test     │
│  SIGN-with-edits (4 must-fix + 2 optional folded).              │
│                                                                  │
│  Answered: WHO performed the action?                            │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 2 — Authority Enforcement Design Space  ✓ CLOSED S1272   │
│                                                                  │
│  Shipped: docs/research/authority_enforcement_design_space.md   │
│  24 inputs; 20 boundaries (17 + 3 SIGN-added WebSocket/Fleet/   │
│  Spider); 12 modes; 6 design options A-F enumerated neutrally;  │
│  15 anti-patterns (3 Tier-0 hazards); 15-prereq DAG.            │
│  Rigby pressure-test SIGN-with-edits, Medium confidence.        │
│                                                                  │
│  Type: DESIGN-SPACE research (first mission carrying design-    │
│  space content per §9 pacing). No option chosen. No design      │
│  decision. Chris gates any downstream selection.                │
│                                                                  │
│  Maintenance note: §1.8 is design-space only. The 6 options     │
│  are for future consumption; none is designated for             │
│  implementation. Do not treat as implementation greenlight.     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3 — Symbol Mapping Option Selection Design  ← recommended│
│  next (per §1.8 §14.1)                                          │
│                                                                  │
│  Scope: pick from §1.6's 5 Symbol Mapping options (A steps      │
│  self-declare / B tool attribute / C hybrid / D central         │
│  registry / E evidence-only). Chris-gated design decision.      │
│  Recommend smallest reversible v0 that unlocks authority        │
│  telemetry and future enforcement without overbuilding.         │
│  Must respect §1.7 §8.5 3-role actor vocabulary. Must respect   │
│  §1.8's 15-prereq DAG (Symbol Mapping is critical-path root).   │
│                                                                  │
│  Type: DESIGN DECISION (not pure research). Rigby SIGN review;  │
│  Chris ratification.                                            │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3b — Actor Role Propagation Design  (P1)                 │
│                                                                  │
│  Two layers per §1.8 §14.2 clarification:                       │
│  (i) Role schema + propagation contract — parallel-safe with    │
│      STAGE 3 (does not depend on Symbol Mapping option)         │
│  (ii) Implementation across boundaries — depends on STAGE 3     │
│       shipped                                                    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3c — Authority Enforcement Design Decision  (P1)         │
│                                                                  │
│  Convert §1.8's 6 design-space options into an actual design    │
│  decision. Consume §1.8's 33-incident catalog, 15 anti-         │
│  patterns, 15 prereqs. Rigby SIGN + Chris gate.                 │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  STAGE 4a       │  │  STAGE 4b       │  │  STAGE 4c       │
│  Trust          │  │  Memory         │  │  Mission        │
│  Propagation    │  │  Architecture   │  │  Composition    │
│  (§5.3)         │  │  (§5.4)         │  │  (§5.6)         │
│                 │  │                 │  │                 │
│  Inter-employee │  │  Cross-employee │  │  Canonical      │
│  trust contract │  │  episodic       │  │  idempotency    │
│  (today only    │  │  memory shape   │  │  key across     │
│  per-employee   │  │                 │  │  orchestration  │
│  trust exists)  │  │                 │  │  paths          │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 5                     │
                │  Cross-Employee Scheduling   │
                │  (§5.5) — depends on Stage   │
                │  4a + 4b + 4c                │
                └──────────────┬───────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 6                     │
                │  Employee Delegation Design  │
                │  (DESIGN, not research —     │
                │  prerequisites must close    │
                │  first)                      │
                └──────────────┬───────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 7 — Implementation    │
                │  (PRs, with research as the  │
                │  justification artifact)     │
                └──────────────────────────────┘

Lateral research that does not block the main chain:

  • Cross-plane Composition (§1.7 F10 + governance F1) — how do
    autonomy / authority / budget / human governance compose
    when all four are active? Blocking STAGE 2 completeness.
  • Security / Permission scoping (§5.8) — if cross-fleet
    surfaces enter scope.
  • Configuration Architecture note (§5.9) — when feature-flag
    growth becomes a documentation problem.
  • Observability consolidation (§5.7) — optional; no blocking
    downstream.
  • Knowledge Graph scoping (§5.10) — only if a use case
    materializes.
  • Focus Mode inventory (§5.11) — if Employee OS reasoning
    surfaces a dependency on it (flagged by Rigby S1269).

  Whole-platform arc (added S1273 v5 — parallel-safe to the
  Employee OS depth arc above):

  • §5.12 Revenue / Outreach / Engagement Pipeline canonical
    architecture doc — P0 parallel. Missed domain caught by
    Rigby S1273 review; blocks any revenue-adjacent work.
  • §5.13 Observability Deduplication Audit — P1. Trace a
    single execution scenario through 5 telemetry layers.
  • §5.14 Sports/DBAO ↔ AI Studio Integration Sketch — P1.
    Structural question about whether platform is one or two.
  • Full 11-mission whole-platform roadmap: see §1.9 §9
    (Notification Unification, Event Bus Producer/Consumer
    Map, Rigby v0 Event Intake Activation Plan, Advisor
    Persistence Contract, Content ↔ Initiative Wiring Audit,
    LLM Provider Failover + Cost Tracking, Claude Code
    Tooling Design Doc, etc.).
```

**Pacing note.** Stages 0 through 1b were pure research —
inventory + classification + failure analysis. STAGE 2
(Authority Enforcement Design Space) is the first mission with
*design* content: the doc will contain a proposal Chris must
gate. Stages 3-4 return to pure research; Stage 5 is design;
Stage 6 is implementation. The discipline that holds this
together is the verifier loop + Rigby SIGN review on every
transition.

---

## 10. Maintenance Rules

This index must evolve in lockstep with the library. The
rules below apply whenever any change happens.

### 10.1 When a new research doc is added

Within the same PR (or same session if no PR yet):

1. **Add a row to §1.** With Title / Purpose / Status / Type /
   Primary questions / Dependencies / Recommended next reads /
   Importance.
2. **Add the doc to §4 dependency graph.** Show its parents
   (via `companion_docs`) and where it sits in the lineage.
3. **Update §2 reading paths.** If the new doc belongs in
   Path A-G (or a new path), add it.
4. **Update §3 domain map.** Move the relevant domain row's
   "Missing research" → "Existing research" (or update
   maturity).
5. **Update §5 gaps.** If the new doc closes one of the named
   gaps, mark it closed with a pointer. If it surfaces new
   gaps, add them.
6. **Update §7 decision matrix.** If there's a class of work
   that should now read the new doc first, add the row.
7. **Update §8 timeline.** Append a new row chronologically.
8. **Update §9 roadmap.** If the new doc was the next stage,
   move the arrow forward.
9. **Bump `last_verified` in this doc's frontmatter.**

### 10.2 When a research doc is superseded

1. Add a pointer header at the top of the superseded doc per
   `DOC_LIFECYCLE.md` V2 conventions.
2. In §1, change Status to `Deprecated` and add a "Superseded
   by: [link]" line.
3. In §4, move the superseded doc to a "historical" footnote
   below the main graph. Do not remove from the corpus —
   per memory rule `feedback_docs_never_delete`, preservation
   matters.
4. In §7 decision matrix, replace references to the
   superseded doc with the successor.

### 10.3 When a doc's status changes (Draft → Active, Active → Canonical)

1. Update the doc's own frontmatter `status` field.
2. Update §1 row Status column.
3. If the doc has been moved to Canonical, add it to the
   appropriate canonical-anchor list in adjacent docs
   (`PLATFORM_INVENTORY.md`, `EMPLOYEE_OS_PRIMITIVES.md`,
   or this index's frontmatter `companion_anchors` if
   applicable).

### 10.4 When drift between docs is discovered

1. Per `DOC_LIFECYCLE.md` §2c: **inventory wins** on counts.
2. Add a drift call to the *newer* doc's drift section (every
   research doc has one — substrate audit cross-reference
   lives in Appendix A, collaboration patterns drift section
   lives in its §12).
3. Do **not** silently edit the older doc. If the older doc
   needs correction, that's a separate review pass with its
   own SIGN verdict.

### 10.5 When this index itself drifts from the library

If `ls docs/research/` shows a doc that isn't in §1, that's
the index's drift. Open a small fix-up PR that just updates
§1, §4, §5, §7, §8. Do not bundle it with anything else.

### 10.6 Authority on this index

This index is **authority: navigation**, not
**authority: canonical** — it points to canonical docs
without being one. If the index disagrees with a canonical
anchor (EMPLOYEE_OS_PRIMITIVES, PLATFORM_INVENTORY,
DOC_LIFECYCLE), the anchor wins; the index gets edited.

---

## Appendix A — Verifier-loop pass notes

This index was drafted from direct inventory of
`docs/research/` at 2026-06-30 (`ls` showed 3 .md files),
plus frontmatter re-reads of each, plus cross-reference
against `docs/` canonical anchors via `Glob`.

**Self-verifier pass (one round) before finalization
identified and fixed:**

- **Missing doc check.** `ls docs/research/` returns exactly
  3 files; all 3 cataloged in §1. No subdirectories. No
  hidden docs. ✓
- **Duplicate classifications.** Originally tagged §1.1 as
  pure "Inventory"; on second pass added "+ Architecture
  Audit + Failure Analysis" because §7 of that doc is
  substantively failure analysis. Same fix on §1.3. ✓
- **Dependency ordering.** First draft showed §1.2 and §1.3
  as parallel children of §1.1 in §4 graph. Re-verified
  against the actual creation order (§1.2 was written
  *before* §1.3 within the same session) and timeline §8 —
  graph is correct; chronologically §1.3 was the audit that
  surfaced the "wider question" raised by Rigby's review of
  §1.2. ✓
- **Inconsistent statuses.** First draft listed all three as
  "Active." Re-read each frontmatter and found all three are
  literally `status: draft` per their YAML. Updated §1 rows
  to "Draft → Active (SIGN-... from Rigby)" to honor both the
  frontmatter literal and the review-state reality. ✓
- **Discoverability.** Originally Path G ("platform
  reliability") didn't mention the client factories. Added
  the hard-rule callout on `anthropic_client_factory.py` /
  `openai_client_factory.py` because the memory rules
  (`feedback_anthropic_client_factory`,
  `feedback_openai_client_factory`) and the zombie-thread
  failure class (§1.3 §7 row 17) all converge on that
  enforcement. ✓
- **§3 domain map** — Memory domain originally not listed;
  added on second pass because §5.2 calls it out as a real
  research gap. Same for Knowledge Pipeline (added per
  `KNOWLEDGE_PIPELINE.md` existing as a canonical anchor
  outside the research library). ✓
- **§7 decision matrix** — first draft was missing the row
  for `MissionRunnerConfig.auto_emit_verdict`. Added on second
  pass because the protocol-invariant-change row (§1.3 §7 row
  29) was Rigby's SIGN-with-edits correction and deserves a
  decision-matrix anchor of its own.

**Status after self-verifier pass.** Publishable as v1.
Rigby independent SIGN review on this index is **not**
required per S1268 mission spec scope (the spec asks for a
verifier loop, not a Rigby pass on the index itself). If a
future session wants Rigby's read on the index, that's a fine
small follow-up.

## Appendix B — v3 update pass notes (S1271)

Triggered by the same-session landing of both `symbol_mapping_architecture.md`
(§1.6) and `actor_identity_attribution_architecture.md` (§1.7).
Both docs completed the verifier loop + Rigby SIGN review before
this index update, so §10.1 was applied wholesale.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 6 files
  (5 research + this index). Both new docs cataloged in §1.6
  and §1.7 respectively. No subdirectories. No hidden docs. ✓
- **Section renumbering.** §5.2 (was "Symbol Mapping — P0
  recommended next" pre-close) marked CLOSED with pointer to
  §1.6. §5.2a added for Actor Attribution close. §5.2b added
  for new P0 next research (Authority Enforcement Design
  Space). Prior §5.3-§5.11 numbering preserved so downstream
  references don't break; renumbering deferred to a future pass
  if it becomes needed. ✓
- **Roadmap stage advancement.** Prior STAGE 1 (Symbol Mapping)
  marked CLOSED. New STAGE 1b (Actor Attribution) inserted as
  same-session follow-on. New STAGE 2 (Authority Enforcement
  Design Space) is the "recommended next." Prior STAGE 2a/2b/2c
  (Trust Propagation / Memory / Mission Composition) renumbered
  to STAGE 3a/3b/3c. Downstream stages (Cross-Employee
  Scheduling → 4, Employee Delegation Design → 5,
  Implementation → 6) bumped by one. ✓
- **Dependency graph.** ASCII diagram in §4 extended with two
  new boxes for §1.6 and §1.7 in the correct downstream
  position, then the "Future research mission" box updated to
  point at Authority Enforcement Design Space (was previously
  pointing at Symbol Mapping, now landed). ✓
- **Domain map.** Governance row's "Missing research" cleared
  (Symbol Mapping was the pending item, now shipped);
  downstream noted as Cross-plane Composition. Authority row
  updated: existing research now includes §1.6 + §1.7; missing
  research is Authority Enforcement Design Space. New "Actor
  Identity / Attribution" domain row added citing §1.7 with
  F1's OpsRun gap as the flagship finding. ✓
- **Decision matrix.** 7 new rows added covering:
  `JobContract.authority` use; actor identity on any new model /
  audit surface; adding user field to OpsRun (explicit
  anti-pattern warning per §1.7 F1 + F11); code using
  `agent_name` CharField anywhere (F4 ambiguity); code using
  `runs_as_username` (F3 + F11); duplicate Agent row risk (F5);
  PA tool actor/user context propagation (§1.6 §6 + §1.7 §7).
  Prior "Authority enforcement (vs. observation)" row updated
  to cite §1.6 + §1.7 + §5.2b instead of the now-closed §1.4 §11
  recommendation. ✓
- **Timeline.** 2 rows appended (S1270 + S1271) with full
  content summaries + influence callouts. Pattern observation
  updated to reflect the 3-session growth cadence
  (S1269/S1270/S1271) after the S1268 burst. ✓
- **Discoverability.** Both new docs now surface via §1
  (rows), §3 (domain map, esp. new Actor Identity row), §4
  (dependency graph position), §5 (closed-gap + new-gap
  entries), §7 (7 new decision-matrix rows), §8 (timeline
  chronology), and §9 (roadmap stage boxes). Reading paths §2
  not extended in this pass; a Path H for "understanding actor
  identity end-to-end" was considered but deferred — Paths A-G
  already cover the reading order via §1.6 and §1.7's
  companion_docs frontmatter chains. Future session can add
  Path H if requested. ✓
- **Frontmatter last_verified.** Bumped from "v2" to "v3" with
  a summary line naming the two shipped docs + the roadmap
  advancement. verifier_loop field expanded with the v3
  changes and prior v1/v2 history preserved. owner field
  extended: "v3 update S1271." ✓

**Status after v3 pass.** Publishable as v3. Both new docs are
discoverable via all 8 index sections (§1-§9 plus this appendix
+ maintenance rules). Rigby independent SIGN review on the
index itself remains optional per §10 discipline; if requested,
a small follow-up pass suffices.

## Appendix C — v4 update pass notes (S1273 Part 1)

Triggered by S1272's landing (`authority_enforcement_design_space.md`)
during S1273's Part 1 documentation-maintenance work. This is
the first update that includes an explicit **maintenance note**
that a docs/research/ entry is design-space only — not
implementation greenlight — per S1273 mission-spec requirement.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 7 files
  (6 research + this index). §1.8 added for `authority_enforcement_design_space.md`.
  No subdirectories. ✓
- **Design-space vs. implementation distinction.** §1.8 status,
  §3 domain map row ("Authority Enforcement (design space)"),
  §5.2b closure note, §7 decision matrix new row on enforcement
  ideas, §8 timeline row, and §9 roadmap STAGE 2 box all
  explicitly state that §1.8 is **design-space only**. This is
  the explicit "maintenance note that Authority Enforcement is
  still design-space only, not implementation" required by
  S1273 mission spec. ✓
- **Roadmap advancement.** Prior STAGE 2 (Authority Enforcement
  Design Space) marked CLOSED S1272. Two new stages added
  parallel-ordered: STAGE 3 (Symbol Mapping Option Selection
  Design — the recommended P0 next), STAGE 3b (Actor Role
  Propagation Design — P1 parallel-safe on Layer (i)), STAGE
  3c (Authority Enforcement Design Decision — P1). Prior
  STAGE 3a/3b/3c (Trust Propagation / Memory / Mission
  Composition) renumbered to STAGE 4a/4b/4c. Downstream stages
  bumped: Cross-Employee Scheduling → 5, Employee Delegation
  Design → 6, Implementation → 7. ✓
- **Dependency graph.** ASCII diagram in §4 extended with new
  §1.8 box (with SIGN-added-boundaries callout). "Future
  research mission" downstream box updated to point at Symbol
  Mapping Option Selection Design (was Authority Enforcement
  Design Space, now landed). ✓
- **Domain map.** Authority row expanded to include §1.8;
  "Missing research" changed from "Authority Enforcement Design
  Space" to "Symbol Mapping Option Selection Design"; maturity
  bumped from "Medium" to "Medium-High" (all three prereqs now
  shipped as research). New "Authority Enforcement (design
  space)" row added citing §1.8 with explicit design-space-only
  maintenance note. Actor Identity row updated to reflect the
  new gating mission. ✓
- **Decision matrix.** 6 new rows added covering: any authority
  enforcement idea (must consult §1.8 anti-patterns + prereqs),
  AuthorityLevel enum usage anywhere new (F1 warning about
  single runtime consumer), new INLINE enforcement gate (F8
  fail-open precedent), adding action_class to any audit model
  (prereq #3 + #4), WebSocket/Fleet/Spider handlers touching
  employee-scoped work (§3 rows 18-20), cross-plane governance
  interaction (§7.5 8 questions). ✓
- **Timeline.** 1 new row appended (S1272) with content
  summary + influence callout. ✓
- **Discoverability.** §1.8 now surfaces via §1 (§1.8 row), §3
  (domain map — Authority row + new Authority Enforcement row),
  §4 (dependency graph position), §5 (§5.2b closed + new §5.2c
  gap), §7 (6 new decision-matrix rows), §8 (timeline), §9
  (roadmap STAGE 2 CLOSED + STAGE 3/3b/3c). ✓
- **Frontmatter.** Bumped from "v3" to "v4" with change
  summary. verifier_loop field expansion deferred to v5 or
  next larger update to keep this pass focused. owner field
  will be extended: "v4 update S1273 Part 1" at commit time. ✓

**Status after v4 pass.** Publishable as v4. §1.8 discoverable
via all 8 index sections. Maintenance note explicit at 4 sites
(§1.8 status, §3 row, §5.2b, §9 STAGE 2 box). Rigby independent
SIGN review on the index itself remains optional per §10.

**Frontmatter-drift note (caught S1273 v5).** The v4 pass
updated Appendix C but forgot to update the frontmatter's
`last_verified` and `owner` fields to reflect v4. That drift
was carried forward until S1273 v5 caught + corrected both.
Small process lesson: bump frontmatter in the same edit as the
appendix note; do not defer.

## Appendix D — v5 update pass notes (S1273 Part 2)

Triggered by S1273's landing of `platform_architecture_
inventory.md` (§1.9) as the first whole-platform architectural
inventory. Chris's direction at S1273 close: "the next cleanup
should be updating ARCHITECTURE_INDEX.md so this becomes the
whole-platform counterpart to the Employee OS research
library." This is the first update that expands the library's
scope from Employee-OS-focused-only to Employee-OS-arc PLUS
whole-platform inventory as a sibling arc.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 8 files
  (7 research + this index). §1.9 added for
  `platform_architecture_inventory.md`. No subdirectories. ✓
- **Scope split acknowledgment.** §1 preamble rewritten to
  distinguish (a) Employee OS arc §1.1-§1.8 (deep on one
  subsystem, S1268-S1272) from (b) whole-platform inventory
  §1.9 (wide on all subsystems, S1273). "When to read which"
  guidance added. ✓
- **Reading path.** New Path H "I need to understand the whole
  platform" added — CLAUDE.md → PLATFORM_WHAT_IT_IS →
  PLATFORM_INVENTORY → §1.9 → specific §3.n → optional
  Employee-OS-arc doc if subsystem covered. ✓
- **Domain map.** New Revenue / Outreach / Engagement row
  added citing §1.9 §3.32 + underlying models + services.
  Rigby caught this as a missed platform subsystem during
  S1273 SIGN review; folded into §1.9 §3.32 + registered here
  as new domain row per §10.1. Rest of §3 unchanged — the
  17-domain Employee-OS-adjacent view remains valid; §1.9's
  32-domain whole-platform view is complementary. ✓
- **Dependency graph.** Sibling-arc ASCII diagram added below
  the main graph, showing §1.9 as parallel to the Employee OS
  arc off the same three anchors (PLATFORM_INVENTORY +
  PLATFORM_WHAT_IT_IS + EMPLOYEE_OS_PRIMITIVES). §1.9 cites
  downstream findings from §1.4 + §1.6 + §1.7 where they overlap
  its own findings, but does NOT depend on the arc's ordering. ✓
- **Gap closures and additions.** §5.4 Memory Architecture
  noted as partially covered by §1.9 §3.13 (Memory / Knowledge
  / Embeddings — DEEP coverage; 5 memory tables enumerated,
  14-day freshness contract, PA-to-Agent feedback closure,
  auto-save ops facts). Three new gaps added — §5.12 Revenue
  Pipeline canonical architecture (P0 parallel; missed-domain
  finding from Rigby's S1273 review), §5.13 Observability
  Deduplication Audit (P1; addresses §1.9 §5.7 5-layer
  telemetry duplication), §5.14 Sports/DBAO ↔ AI Studio
  Integration Sketch (P1; addresses §1.9 §3.10 island-vs-
  integrated structural question). ✓
- **Decision matrix.** 3 new whole-platform rows added:
  onboarding / cross-domain scoping (start at §1.9); Revenue/
  Outreach/Engagement/Meeting/ClosePack work (§1.9 §3.32 +
  §4.9 + §5.12 gap); sports-betting content integration
  (§1.9 §3.10 + §4.8 + §5.14 gap). ✓
- **Timeline.** 1 new row appended (S1273, 2026-07-01) with
  content summary + Rigby SIGN-with-edits detail (Medium
  confidence, 6 substantive edits folded incl. missed Revenue
  Pipeline domain) + Chris's whole-platform-counterpart
  direction. Timeline note extended to reference the fresh
  isolation pin `pa-02cfd3206302352f` used for §1.9's Rigby
  review (kept separate from shared S1270+ arc pin
  `pa-cbcc410b32714f60` mid-session per context-crossing
  directive). ✓
- **Pattern observation.** Section 8 pattern-observation
  paragraph updated to reflect the two-wave library shape —
  first wave S1268-S1272 (Employee OS depth arc), second wave
  S1273 (whole-platform sibling arc). Next growth events now
  split: (a) Employee OS arc STAGE 3 Symbol Mapping Option
  Selection Design (Chris-gated); (b) whole-platform arc
  top-3 next missions (§5.12/§5.13/§5.14). Parallel-safe. ✓
- **Roadmap.** §9 lateral research list expanded to reference
  whole-platform arc with §5.12/§5.13/§5.14 as the top-3 next
  missions + pointer to §1.9 §9 for the full 11-mission
  roadmap. ✓
- **Frontmatter.** Bumped from "v4" to "v5" with change
  summary. verifier_loop field expanded with v5 changes and
  prior v1-v4 history preserved. owner field extended: "v5
  update S1273 Part 2." Also caught + corrected v4 frontmatter
  drift (v4 pass updated Appendix C but never bumped
  last_verified — see Appendix C's Frontmatter-drift note
  above). ✓
- **Discoverability.** §1.9 now surfaces via §1 (preamble +
  §1.9 row), §2 (new Path H), §3 (Revenue Pipeline row +
  cross-reference to §1.9's 32-domain map), §4 (sibling-arc
  dependency graph extension), §5 (§5.12/§5.13/§5.14 new gap
  entries + §5.4 partial-coverage note), §7 (3 new decision-
  matrix rows), §8 (timeline row + pattern-observation
  update), §9 (roadmap lateral research expansion). ✓

**Status after v5 pass.** Publishable as v5. §1.9 discoverable
via all 9 index sections. Dual-scope library shape is now
explicit throughout the doc (§1 preamble, §2 Path H, §4 sibling
arc, §8 pattern observation, §9 lateral research). Rigby
independent SIGN review on the index itself remains optional
per §10.6 — the index is `authority: navigation`, not
`authority: canonical`; anchors win when they disagree with the
index.
