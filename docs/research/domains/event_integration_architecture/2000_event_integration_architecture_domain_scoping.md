---
title: "Group 2000+ — Event / Integration Architecture — Parent Scoping (Phase 0)"
status: draft
session: 2000
child_slot: parent
domain_slug: event_integration_architecture
research_group: 2000
mission_type: parent_scoping
date: 2026-07-04
authority: |
  Parent-arc scoping only. This doc enumerates the child-mission
  taxonomy that Group 2000+ will execute, records Chris's S2000-open
  D-verdict ratifying the playbook §22 default queue lean (Event /
  Integration Architecture over any D-override — first arc that
  consumes the default after two consecutive D-overrides at S1800
  HumanAttention + S1900 Authority Enforcement), and hands off to
  P1 (EventBus Producer/Consumer Map + Contract Verification) at
  S2001. It does NOT design event schema (that IS the P2 child
  deliverable), does NOT pick cross-substrate composition rules
  (that IS the P3 child), does NOT ship implementation PRs or
  modify runtime code / migrations / EventBus wrappers /
  WebSocket consumers / Celery beat schedule. Per playbook §14.5
  no-implementation rule.

  Scope hand-off from Group 1800 xx99 §8.1 T0/Gate is EXPLICIT:
  - R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES (Group 1800 T0/Gate
    §8.1 item 6) → Group 2000+ P2 (HAI Event Contract Design)
    child mission. Group 1800 provided catalog only; Group 2000+
    designs schema.
  - Six-plane learning-surface fragmentation event-emission gap
    (S1806 §10 arc-close durable-at-six) → Group 2000+ P2 scope.
  - source_kind provenance enum (R.HAI.SOURCE-KIND-ENUM-ADR
    T0/Gate item 5, joint Group 1300 + Group 1800 schema-change)
    → Group 2000+ P2 inherits the enum values for HAI event
    emission but does NOT re-open the Memory + HAI joint ADR
    scope.

  Scope hand-off from Group 1900 P3 §19 is EXPLICIT:
  - F.SYMBOL-MAPPING-STATUS-VERIFICATION (S1903 §19) → Group
    2000+ P3 scope (cross-substrate composition inherits Symbol
    Mapping Option E v0 evidence-only telemetry substrate; P3
    audits current graduation-trigger status per S1274 §11).
  - F.PER-USER-AUTHORITY-MECHANISM (S1903 §19) → Group 2000+ P2
    scope for authority × HAI event emission mapping (P2 designs
    HAI event candidates for per-user authority resolution
    triggers; per-user authority MECHANISM implementation
    remains post-arc).

  Load-bearing prior research chain re-attested (S1273 §3.31 +
  S1274 §12.1 + S1806 §10 + S1899 §8.1 + S1903 §19).
companion_docs:
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/research/domains/human_attention/1899_human_attention_canonical_summary.md
  - docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md
  - docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md
  - docs/research/symbol_mapping_option_selection_design.md
  - docs/research/symbol_mapping_event_schema_design.md
  - docs/EVENT_SYSTEM_INVENTORY.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
verifier_loop: |
  Parent scoping doc; no Explore-sub-agent sweeps performed (Group
  2000+ subagent sweeps deferred to child audits per playbook §13
  discipline). Load-bearing structural claims about the domain
  shape inherit from S1273 §3.31's EventBus inventory, S1274
  §12.1's P0 producer/consumer map audit, S1806 §10's six-plane
  learning-surface event-emission gap durable-at-six, and S1899
  §8.1's T0/Gate handoff (item 6 R.EVENTS.HAI-EVENT-CONTRACT-
  CANDIDATES).

  Re-attested runtime state at S2000 open:
  (a) EventBus at `core/services/event_bus.py:90:EventBus` —
      Redis Streams wrapper; 8 streams declared at lines 21–30
      (SPIDER_DATA + OPPORTUNITY_CREATED + OPPORTUNITY_SCORED +
      VALIDATION_REQUIRED + VALIDATION_DECIDED + OUTCOME_RECORDED
      + MODEL_TRAINED + SYSTEM_ALERT); DLQ `mi:dead_letter`
      declared; consumer groups scoring_workers +
      validation_workers + analytics_workers.
  (b) Publisher wrappers at `event_bus.py:539,559,596,619,643`
      (spider_data + opportunity_scored + validation_required +
      validation_decided + outcome_recorded + system_alert).
  (c) Consumer tasks at `core/tasks.py:4726` (scoring_queue) +
      `4760` (validation_queue) + `4794` (analytics_queue) +
      `4874` (get_event_bus_stats).
  (d) Producer/consumer registry MISSING per S1273 §3.31 known
      drift + S1274 §12.1 P0 finding — WEAK adoption per S1274 v2
      Rigby SIGN fold ("EventBus was mis-classified as 'dormant'
      — Rigby caught partial adoption; upgrade WEAK not MISSING").
  (e) HAI event candidates enumerated at S1806 §10 durable-at-
      six sub-slots (record_decision + record_verification +
      auto_approve + auto_escalate transitions) — catalog
      provided by Group 1800; schema design deferred to Group
      2000+ P2 per §8.1 T0/Gate handoff.
  (f) Six-plane learning-surface fragmentation (S1806 §7.4) —
      six writer planes (HAI-mediated + autonomous_bridge +
      non_bridge_direct + verification_outcome + external_signal
      + shadow_service) currently write to AgentLearning +
      UserAgentLearning without emitting structured events at
      plane-transition boundaries.
  (g) EventBus semantic overlap with WebSocket consumer message
      types + CeleryTaskEvent audit rows + LLMCallEvent audit
      rows + OpsRunEvent audit rows + ToolCallRecord audit rows
      undocumented per S1273 §3.31 known drift.

  Independent Rigby SIGN review on parent scoping opted-in by
  Chris D97 2026-07-04 per playbook §15 stage-table row.
  **SIGN cycle 1 CLEAN at 0.86 confidence 2026-07-04** on arc
  pin `pa-dd7e973617da464d`. **D48 38th arm CLEAN turn 1** per
  MC-2 32-consecutive-fully-clean-arms sub-pattern → extended
  to **33-consecutive** (MC-2 CODIFICATION-CONFIRMED milestone
  extended 32 → 33 consecutive per single-batch-4-question
  criterion).
  **4 folds landed pre-commit:** (1) §5.2 P2 preamble +
  §7.2 anti-scope scope guardrail (authority MECHANISM out-of-
  scope; contract semantics in-scope) per Q1 fold; (2) §2.6.2
  runtime evidence bundle parent-vs-child discipline explicit
  statement per Q2 fold; (3) §2.6.1 inheritance precedence
  order 1-2-3 subsection per Q3 fold; (4) §5.1 P1 Contract
  Verification expansion to 4 deliverables (α) schema-shape
  doc / (β) runtime assert audit / (γ) version gate policy /
  (δ) replay-test enumeration per Q4 fold. All in-place
  wording/structure folds, no scope changes.
---

# Session 2000 — Group 2000+ Event / Integration Architecture Parent Scoping (Phase 0)

> **Anchor:** playbook §11.1 9-section parent scoping template
> **SEVENTH** application (after S1400 Revenue + S1500 Sports +
> S1600 Content + S1700 Observability + S1800 HumanAttention +
> S1900 Authority Enforcement). Group 2000+ kicks off the EIGHTH
> Research OS domain arc.
>
> **Chris D-verdict (S2000 open 2026-07-04):** ratified playbook
> §22 default queue lean = Event / Integration Architecture over
> any D-override. This is the FIRST Group 2000+ arc opening that
> consumes the §22 default after two consecutive D-overrides at
> S1800 (HumanAttention over Event Architecture) + S1900
> (Authority Enforcement over Event Architecture). Rationale:
> - Group 1800 xx99 §8.1 T0/Gate item 6 R.EVENTS.HAI-EVENT-
>   CONTRACT-CANDIDATES explicitly parks HAI event schema design
>   for "Group 1900 arc-open scoping" — an inheritance that
>   S1900's D-override deferred; Group 2000+ now consumes it.
> - S1274 §12.1 P0 EventBus Adoption + Contract Verification is
>   the load-bearing gap Rigby explicitly flagged at S1274 SIGN
>   (mis-classification lesson: EventBus is partially adopted
>   with WEAK observability, not dormant — the producer/consumer
>   map is required before any composition or refactor work).
> - S1273 §3.31 EventBus row classifies architecture maturity as
>   EXPERIMENTAL with producer/consumer registry ABSENT — one of
>   the highest-drift-risk PARTIAL surfaces in the 32-domain map.
> - Group 1900 xx99 §9 delegates F.SYMBOL-MAPPING-STATUS-
>   VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM to "Group 2000+
>   Event / Integration Architecture" scope — the delegated
>   inheritance shape matches this arc's opening.

---

## 1. Why Phase 0

Group 2000+ sits at the **integration seam** between six prior
arcs (Groups 1300 Memory + 1500 Sports + 1600 Content + 1700
Observability + 1800 HumanAttention + 1900 Authority Enforcement)
and the runtime substrate that carries their events. Phase 0
parent scoping is required for four reasons:

**(1) The domain has TWO distinct integration surfaces that must
not blur.**

The name "Event / Integration Architecture" from playbook §22 +
S1273 §3.31 covers two mechanically distinct surfaces:

- **EventBus / Streams (runtime coordination)** — Redis Streams
  substrate for push-with-consumers pub/sub; publishers emit,
  consumer groups react asynchronously, DLQ catches unhandled.
  This is *runtime coordination* — consumer B reacts to producer
  A's action at execution time.
- **HAI event emissions (semantic event contract)** — the six-
  plane learning-surface + record_decision + record_verification
  + auto_approve + auto_escalate transition set the domain needs
  to emit for downstream analytics, retention differentiation,
  and cross-plane observability. This is *semantic contract* —
  what shape events take, how they version, who reads them.

S1273 §3.31 explicitly separates EventBus from Observability
(§3.25) — the same discipline must apply here: EventBus is
runtime push; HAI events are semantic contract. Rolling them
into a single child audit would either (a) collapse the
runtime-vs-contract distinction that S1273 §3.31 explicitly
protects, or (b) produce a 3000+ line deliverable that cannot
be reviewed coherently.

**(2) The producer/consumer map is a load-bearing prerequisite
for every downstream design question.**

S1274 §12.1 named EventBus Adoption + Contract Verification as
**P0 non-negotiable**. Rigby's SIGN-with-edits caught v1's
mis-classification of EventBus as "dormant" — the correct
classification is **WEAK adoption with partially-instrumented
consumers**. Publishers exist at 5 sites in `event_bus.py`
(lines 539/559/596/619/643); consumer tasks exist at 4 sites in
`tasks.py` (4726/4760/4794/4874); but the producer→consumer
mapping is UNKNOWN for 5 of 8 streams. Every downstream
integration question (which HAI events map to which stream, how
schema versioning applies, whether WebSocket + Celery + EventBus
substrate overlap is intentional) depends on the producer/consumer
map existing.

**(3) The cross-substrate composition question is a first-class
audit, not a corollary.**

Six substrates currently emit "events" in some sense: EventBus
(runtime coordination), WebSocket consumer message types
(realtime frontend push), `CeleryTaskEvent` (Celery task audit),
`LLMCallEvent` (LLM call audit), `OpsRunEvent` (ops run audit),
`ToolCallRecord` (PA tool audit). S1273 §3.31 flags the
EventBus × WebSocket semantic-surface overlap as known drift.
S1899 §8.1 T0/Gate item 4 R.HAI.RETENTION-UNIFIED-ADR pairs
retention posture across LLMCallEvent + HAI-arc's six models.
S1799 T0/Gate R.OBSERVABILITY.RETENTION-UNIFIED-ADR pairs
across the observability plane. Group 2000+ P3 must answer:
when does a new emission go to EventBus vs. WebSocket vs. a
telemetry table? What's the separation contract? Where's the
duplicate-emission risk? This is a distinct research question
from producer/consumer discovery (P1) or HAI event contract
design (P2).

**(4) The domain surface (Event / Integration) touches every
platform plane; CONSOLIDATION is load-bearing per proven
pattern.**

Prior arcs proved this pattern: Group 1700 Cat F CONSOLIDATION
(Observability × Adjacent domains) caught retention discipline
drift + spine posture gaps that per-child audits missed. Group
1800 Cat F CONSOLIDATION caught duplicate-file collisions across
sibling children. Group 1900 Cat F CONSOLIDATION locked
per-plane separation-boundary posture register + confirmed
MC-6 CODIFICATION-READY. Event / Integration crosses Spider /
Signal / Opportunity / Validation / Analytics / WebSocket /
Celery Task / Employee OS / HAI / Memory / Content / Sports /
Frontend / API / Discord surfaces — a CONSOLIDATION child (P4)
is the mechanism that prevents "accidental re-coupling" between
the runtime substrate and the semantic contract, and that
catches emission-plane drift across adjacent domains.

---

## 2. What existing inventory already tells us

### 2.1 Prior research chain (Groups 1300–1900)

| Group | Session | Doc | Contribution to Group 2000+ |
|---|---|---|---|
| — | S1273 | `platform_architecture_inventory.md` §3.31 | EventBus row: 8 streams + 3 consumer groups + DLQ; EXPERIMENTAL maturity; producer/consumer registry ABSENT; separation-of-concerns paragraph from Observability §3.25 |
| — | S1274 | `cross_domain_integration_audit.md` §12.1 | P0 EventBus Adoption + Contract Verification; Rigby SIGN v2 fold — WEAK not "dormant"; publisher wrappers at 5 sites; consumer tasks at 4 sites; producer/consumer map UNKNOWN for 5 of 8 streams |
| — | S1275 | `symbol_mapping_event_schema_design.md` | Event schema design for Symbol Mapping Option E; enforcement-adjacent event shapes; canonical schema-versioning precedent |
| 1300 | S1399 | `1399_memory_canonical_summary.md` | R.HAI.LEARNING-PLANE-CONTRACT-ADR joint (with Group 1800) — canonical learning writes entrypoint; source_kind provenance enum; explicit consumer registry pattern |
| 1600 | S1699 | `1699_content_canonical_summary.md` | Content plane emission points (S1699 §7.4 auto_publish cross-arc CORRECTION owes 5 doc PRs) |
| 1700 | S1799 | `1799_observability_canonical_summary.md` | Telemetry retention posture; five-layer observability dedup; T0/Gate R.OBSERVABILITY.RETENTION-UNIFIED-ADR (paired with Group 1800 R.HAI.RETENTION-UNIFIED-ADR) |
| 1800 | S1899 | `1899_human_attention_canonical_summary.md` | T0/Gate §8.1 item 6 R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES — the Group 2000+ P2 inheritance |
| 1800 | S1806 §10 | Cat F CONSOLIDATION | Six-plane learning-surface fragmentation event-emission gap durable-at-six; catalog of HAI event candidates |
| 1900 | S1903 §19 | P3 Cross-Plane Composition Design | F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM — Group 2000+ inheritance |
| 1900 | S1999 | `1999_authority_enforcement_canonical_summary.md` | Canonical seam-posture statement + 6 unresolved unknowns → Group 2000+ inherits the "record_decision when authority PROHIBITED fires" event emission question |

**Total prior investment:** 10+ arc documents, 20,000+ lines of
evidence, 15+ SIGN-with-edits cycles. Group 2000+ is where the
cross-arc emission substrate contract gets designed.

### 2.2 Runtime state at S2000 open (attested per verifier loop)

**F1 — EventBus infrastructure is real; adoption is WEAK.** Per
S1274 §12.1 + verifier loop (a)+(b)+(c):

- `EventBus` class at `core/services/event_bus.py:90` — Redis
  Streams wrapper implementing `xadd` + `xreadgroup` + `xack`.
- 8 streams declared at `event_bus.py:21–30`: `SPIDER_DATA`,
  `OPPORTUNITY_CREATED`, `OPPORTUNITY_SCORED`, `VALIDATION_REQUIRED`,
  `VALIDATION_DECIDED`, `OUTCOME_RECORDED`, `MODEL_TRAINED`,
  `SYSTEM_ALERT`.
- 1 DLQ: `mi:dead_letter`.
- 3 consumer groups: `scoring_workers`, `validation_workers`,
  `analytics_workers`.
- **Publisher wrappers (5)** at `event_bus.py:539` (spider_data),
  `:559` (opportunity_scored), `:596` (validation_required),
  `:619` (validation_decided), `:643` (outcome_recorded) —
  `system_alert` at `:686`.
- **Consumer tasks (3 + 1 stats)** at `core/tasks.py:4726`
  (`process_event_bus_scoring_queue`), `:4760`
  (`process_event_bus_validation_queue`), `:4794`
  (`process_event_bus_analytics_queue`), `:4874`
  (`get_event_bus_stats`).
- **Producer→consumer map:** UNKNOWN for 5 of 8 streams. Only
  OPPORTUNITY_SCORED → scoring_workers has a verified end-to-end
  chain per S1274 §6.2. SPIDER_DATA, VALIDATION_REQUIRED,
  VALIDATION_DECIDED, OUTCOME_RECORDED, SYSTEM_ALERT publisher
  call-sites not exhaustively traced. MODEL_TRAINED — no wrapper
  found; consumer TBD.
- **Adoption classification:** WEAK (not "dormant" per Rigby
  SIGN v2 correction).

**F2 — Six-plane learning-surface event-emission gap is
durable-at-six.** Per S1806 §7.4 + §10:

- Six writer planes (HAI-mediated + autonomous_bridge +
  non_bridge_direct + verification_outcome + external_signal +
  shadow_service) currently write to `AgentLearning` +
  `UserAgentLearning` at 22+ call sites.
- **Zero of these six planes emits a structured event at
  plane-transition boundaries.** Downstream cross-plane
  analytics, retention differentiation, and observability all
  degrade proportionally.
- Group 1800 T0/Gate item 5 (`R.HAI.SOURCE-KIND-ENUM-ADR`)
  provides the provenance enum; Group 2000+ P2 designs the
  event contract that emits at each transition.

**F3 — HAI transition points have four canonical event
candidates per S1806 §10 + parent §6.7.** The Group 1800 T0/Gate
handoff item 6 `R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES`
enumerates:

- `record_decision` (transition point when a human or auto-
  approver ratifies an HAI item).
- `record_verification` (transition point when a downstream
  verifier confirms or refutes a decision — sports settlement,
  content performance, etc.).
- `auto_approve` (transition point when
  `_auto_approve_low_risk_items` beat closes an item without
  human review).
- `auto_escalate` (transition point when an item's stale-timer
  fires or scale-threshold exceeds and escalation occurs).

Group 1800 provided the catalog; Group 2000+ P2 designs the
schema (field shape, versioning, retention, consumer contracts).

**F4 — Cross-substrate emission overlap is undocumented per
S1273 §3.31.** Six substrates currently emit "events" in some
sense:

| Substrate | File / Class | Semantic |
|---|---|---|
| EventBus | `core/services/event_bus.py:90:EventBus` | Runtime pub/sub |
| WebSocket consumers | `core/consumers.py` + `chat_consumers.py` + `command_center_consumers.py` | Realtime frontend push |
| `CeleryTaskEvent` | `core/models_ops_runs.py` | Celery task audit |
| `LLMCallEvent` | `core/models_llm_events.py` | LLM call audit |
| `OpsRunEvent` | `core/models_ops_runs.py` | Ops run audit |
| `ToolCallRecord` | `core/models.py` | PA tool audit |

S1273 §3.31 known drift flag: "Some semantic surface overlap
with WebSocket consumer message types (both broadcast realtime
state); relationship undocumented." Group 2000+ P3 audits this
overlap and designs the separation contract.

**F5 — Schema versioning has one precedent, one gap.** S1275
established the schema-versioning shape for Symbol Mapping
Option E events — canonical precedent. But no schema-versioning
policy applies to the 8 EventBus streams; publishers and
consumers rely on positional/name coupling with no `schema_version`
field. Any HAI event contract Group 2000+ P2 designs must
decide: adopt S1275 versioning precedent, or design a new one?

**F6 — Consumer groups + DLQ have no retention policy.** Per
S1274 §6.2 + S1273 §3.31: `mi:dead_letter` stream has no
cleanup task ("Cleanup task MISSING" — S1274 §6.2 registry).
`get_event_bus_stats` at `tasks.py:4874` reads DLQ length but
no consumer processes DLQ entries. Group 2000+ P1 must surface
this in the producer/consumer map; P3 must decide whether DLQ
retention pairs with the R.OBSERVABILITY.RETENTION-UNIFIED-ADR
+ R.HAI.RETENTION-UNIFIED-ADR joint bundle.

**F7 — F.SYMBOL-MAPPING-STATUS-VERIFICATION inheritance.** Per
S1903 §19 + S1274 §11: Symbol Mapping Option E v0 recommended
with 4 graduation triggers monitoring windows. Group 1900 P3
deferred Q6 + Q8 resolution pending Symbol Mapping graduation
status. Group 2000+ P3 (Cross-Substrate Composition) audits
current graduation-trigger status as prerequisite for
composition design.

**F8 — F.PER-USER-AUTHORITY-MECHANISM inheritance.** Per S1903
§19: per-user authority resolution mechanism is required by
Q6 (authority × HumanAttentionLifecycle.LOW_RISK_SOURCES × HAI
auto-approve). Group 2000+ P2 designs HAI event candidates for
per-user authority resolution triggers (not the mechanism
itself — the event-emission contract for downstream consumers).

### 2.3 What we already know from S1273 §3.31 (the EventBus row)

**Purpose.** Redis Streams pub/sub for event-driven architecture
across spiders, signals, opportunities, and validation.

**Canonical entry points enumerated.** `event_bus.py:90:EventBus`
+ 8 streams + 3 consumer groups + 1 DLQ.

**Research coverage:** LIGHT.

**Architecture maturity:** EXPERIMENTAL — schema defined; consumer
group infra in place; producer/consumer map MISSING.

**Known drift:** producer/consumer registry absent.

**Known technical debt:**
- Producer/consumer map missing — reuse decisions blocked.
- Semantic surface overlap with WebSocket consumer message types
  undocumented.

**Separation-of-concerns from Observability (§3.25):** Rigby-
verified — EventBus is *runtime coordination*, Telemetry is
*evidence-after-the-fact*. Do not merge in future refactors
without a research doc reviewing whether substrates should
converge.

### 2.4 What we already know from S1274 §12.1 (P0 EventBus Adoption)

**Priority:** P0 non-negotiable.

**Why:** EventBus has real publishers + consumers wired for at
least OPPORTUNITY_SCORED; other 7 streams unclear coverage
without dedicated call-site sweep.

**S1274 SIGN v2 correction (Rigby fold):** EventBus was mis-
classified as "dormant" in v1. Rigby ran independent grep and
caught partial adoption — verified via publisher wrappers at
`event_bus.py:539,559,596,619,643` and consumer task bodies
at `tasks.py:4726,4760,4794` (`process_event_bus_*_queue`).
Correct classification: **WEAK adoption + partial
instrumentation**. This lesson (do not use binary language for
continuous reality) is a durable playbook rule.

**S1274 §12.1 P0 deliverable shape:**
1. Publisher call-site sweep for all 8 streams.
2. Consumer task body inspection for `process_event_bus_scoring_queue`,
   `_validation_queue`, `_analytics_queue`.
3. Producer→consumer map with STRONG/WEAK/UNKNOWN classification.
4. Contract verification — does each publisher's payload shape
   match what each consumer expects?

Group 2000+ P1 executes this scope.

### 2.5 What we already know from S1899 §8.1 T0/Gate item 6

**Item name:** `R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES`

**Consolidated from:** S1806 §10 + parent §6.7.

**Scope:** Enumerate HAI event candidates (record_decision +
record_verification + auto_approve + auto_escalate transitions)
for [Group 2000+] EventBus adoption. Provide catalog only per
Group 1800 scope; [Group 2000+] designs schema.

**Blocks:** Group 2000+ arc-open scoping.

**Group 1800 delivery:** catalog of 4 candidate transitions +
six-plane learning-surface event-emission gap durable-at-six
sub-slots. No schema designed. No versioning policy chosen.
No consumer registry.

**Group 2000+ P2 execution:** design event schema per candidate;
adopt versioning policy (S1275 precedent or new); define
retention posture (paired with joint retention ADR); enumerate
consumer registry.

### 2.6 What we already know from S1903 §19 delegation

Per `1903_authority_enforcement_cat_c_cross_plane_composition_design.md`
§19 (Group 1900 P3 recommended future research):

- **F.SYMBOL-MAPPING-STATUS-VERIFICATION** — S1274 Option E v0
  graduation status monitoring; blocks Group 1900 P3 Q6 + Q8
  resolution; **Group 2000+ P3 scope**.
- **F.PER-USER-AUTHORITY-MECHANISM** — per-user authority
  resolution mechanism required by Q6; **Group 2000+ arc
  scope for design research** (implementation post-arc); Group
  2000+ P2 designs the event-emission contract for per-user
  authority resolution triggers.

### 2.6.1 Inheritance precedence order (per Rigby S2000 SIGN cycle 1 Q3 fold)

Group 2000+ has three load-bearing inheritances. Precedence
order is explicit so downstream child docs do NOT diverge on
load-bearing hierarchy:

1. **R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES** — PRIMARY SPINE.
   The T0/Gate inheritance from Group 1800 §8.1 item 6 is the
   load-bearing driver for P2 (4 candidate transitions +
   six-plane learning-surface event-emission gap). Every child
   scope ties back to this. Any child re-scoping request that
   would demote R.EVENTS.HAI below constraint status is a
   §7.2 anti-scope violation.

2. **F.PER-USER-AUTHORITY-MECHANISM** — CONSTRAINT shaping P2
   event-emission contract semantics. Extends the P2 contract
   with additional candidate transitions (per-user authority
   triggers) but is downstream of the primary spine. Per §5.2
   scope guardrail: contract semantics in-scope; MECHANISM
   out-of-scope.

3. **F.SYMBOL-MAPPING-STATUS-VERIFICATION** — P3 gate for
   cross-substrate composition graduation confidence. Status
   audit only; not a schema-shaping driver. P3 executes the
   status audit as prerequisite for composition-design
   confidence but does NOT reopen the S1274 Option E v0
   recommendation.

### 2.6.2 Runtime evidence bundle at parent scope (per Rigby S2000 SIGN cycle 1 Q2 fold)

Explicit parent-vs-child evidence discipline:

- **(a) Current EventBus attestation** — 8 streams + 3 consumer
  groups + DLQ + publisher wrappers at 5 sites + consumer tasks
  at 4 sites — **MANDATORY at parent scope** (re-attested in
  frontmatter `verifier_loop` chains a–g).
- **(b) Producer/consumer map for all 8 streams** — **DEFERRED
  to P1 execution.** P1 IS this deliverable; not a parent-
  scoping prerequisite.
- **(c) End-to-end contract verification for one stream** —
  **DEFERRED to P1 late-cycle + P2 early-cycle.** Canonical
  candidate: OPPORTUNITY_SCORED → scoring_workers (the one
  stream with verified end-to-end chain per S1274 §6.2). This
  is the P1 verification step that graduates the arc into P2
  confidently.

Rationale: parent scoping's purpose is to ratify the child cut
+ inheritances; the runtime evidence bundle proving the cut is
correct comes from child execution, not from parent
pre-establishment.

---

## 3. Candidate subdomain taxonomy

Three candidate taxonomies considered. My lean is Option (b) —
4-child arc with CONSOLIDATION — for reasons detailed under §3.3
and §3.4. Chris D-verdict at close of parent scoping ratifies
the taxonomy.

### 3.1 Option (a) — Minimal 3-child (EventBus + HAI events + xx99)

**Structure:**
- P1 = EventBus Producer/Consumer Map + Contract Verification
  (S1274 §12.1 P0 execution)
- P2 = HAI Event Contract Design (S1899 §8.1 item 6 inheritance)
- xx99 = canonical summary
- Runtime target: ~4 sessions.

**Pros:**
- Minimal scope; every child directly closes an inherited
  T0/Gate or §12.1 P0.
- Playbook §11.1 template consumers = 2 child audits + 1 xx99.
- Lowest runtime target.

**Cons:**
- **Drops cross-substrate composition as a first-class question.**
  Six substrates currently emit "events" in some sense; the
  overlap between EventBus + WebSocket + CeleryTaskEvent +
  LLMCallEvent + OpsRunEvent + ToolCallRecord is S1273 §3.31
  named drift. Rolling composition into P1 (EventBus map) forces
  scope creep on the map; rolling into P2 (HAI events) blurs
  the semantic-contract vs. cross-substrate-composition
  distinction.
- **Drops the proven CONSOLIDATION pattern** from Groups
  1700/1800/1900. Event / Integration crosses every platform
  plane; without CONSOLIDATION, accidental cross-substrate
  re-coupling is a known failure mode.
- **Does not observe MC-6 CODIFICATION-CONFIRMED promotion**
  (S1999 close listed MC-6 CODIFICATION-READY at 2 applications
  — Group 1700 F + Group 1800 F; MC-6 CONFIRMED needs 4+ per
  S1999 §10.2 scope guardrail language).

### 3.2 Option (b) — 4-child with CONSOLIDATION (my lean)

**Structure:**
- P1 = EventBus Producer/Consumer Map + Contract Verification
  (S1274 §12.1 P0 execution)
- P2 = HAI Event Contract Design (S1899 §8.1 item 6 inheritance;
  four candidate transitions + six-plane learning-surface event-
  emission gap + source_kind enum values + schema versioning
  policy + retention posture)
- P3 = Cross-Substrate Composition Design (EventBus vs. WebSocket
  vs. CeleryTaskEvent vs. LLMCallEvent vs. OpsRunEvent vs.
  ToolCallRecord — separation contract + duplicate-emission risk
  audit + Symbol Mapping graduation status verification per
  F.SYMBOL-MAPPING-STATUS-VERIFICATION inheritance)
- P4 = Cat F Adjacent / Separation Boundaries CONSOLIDATION
  (mirror Group 1700/1800/1900 pattern; separates event/integration
  from Memory / Sports / Content / HAI / Observability / Authority
  Enforcement / Employee OS / Frontend / API / Discord planes)
- xx99 = canonical summary
- Runtime target: ~6 sessions.

**Pros:**
- **Respects the runtime-vs-contract-vs-composition distinction**
  S1273 §3.31 established. P1 = runtime map. P2 = semantic
  contract. P3 = cross-substrate composition. Three distinct
  research questions, three distinct deliverables.
- **Adds the proven CONSOLIDATION pattern** (THIRD-consecutive
  arc application after Group 1700 / Group 1800 / Group 1900).
  MC-6 CODIFICATION-CONFIRMED milestone at Group 2000+ close
  (4 applications: 1700 + 1800 + 1900 + 2000+).
- **Playbook §11.2 20-section child template FIFTEENTH →
  EIGHTEENTH consecutive application** observation opportunity
  — MC-5 CODIFICATION-CONFIRMED at S1999 gets 4 additional
  data points beyond arc-scope (durable observation).
- **Runtime target 6 sessions** matches Group 1900 precedent —
  predictable arc runtime.
- **Aligns child slots to inherited T0/Gate items 1:1** — P1
  closes S1274 §12.1 P0; P2 closes S1899 §8.1 item 6; P3 closes
  F.SYMBOL-MAPPING + F.PER-USER-AUTHORITY inheritance; P4
  closes cross-plane emission-drift risk.

**Cons:**
- **Runtime target 1 session longer than Option (a).**
- **Does NOT observe MC-4 (arc-pin routing durable-by-6th-
  application under 6-child arcs)** — Group 2000+ as 4-child
  does not qualify. MC-4 was CODIFICATION-CONFIRMED-with-scope-
  guardrails at S1999 (durable across two distinct arc shapes:
  4-child Group 1900 + 6-child Group 1800). Third arc under a
  distinct shape (e.g., 5-child or 8-child) would upgrade
  confidence further but is NOT required for CONFIRMED.

### 3.3 Option (c) — 6-child for MC-4 durability observation

**Structure:**
- P1 = Cat A — EventBus infrastructure inventory (streams +
  consumer groups + DLQ)
- P2 = Cat B — EventBus producer/consumer map (publisher call-
  sites + consumer task bodies)
- P3 = Cat C — EventBus contract verification (payload-shape ×
  consumer-expectation match)
- P4 = Cat D — HAI Event Contract Design (schema + versioning)
- P5 = Cat E — Cross-Substrate Composition Design
- P6 = Cat F — Adjacent / Separation Boundaries CONSOLIDATION
- xx99 = canonical summary
- Runtime target: ~8 sessions.

**Pros:**
- Creates MC-4 arc-pin-routing SEVENTH-consecutive-application
  observation under a 6-child arc → confidence upgrade beyond
  CONFIRMED-with-scope-guardrails.
- Creates MC-5 §11.2 20-section child template FIFTEENTH →
  TWENTIETH consecutive-application observation → durable-at-
  20 sub-pattern.

**Cons:**
- **Splits S1274 §12.1 P0 into three artificial children** (Cat
  A infra + Cat B map + Cat C contract verification) — this is
  a single load-bearing gap, not three. Fragmentation forces
  cross-child dependency + Rigby SIGN cycle overhead.
- **Arc-shaping for MC observation is meta-methodology-first**
  rather than scope-first (S1999 §10.2 anti-pattern flagged
  under MC-4 scope guardrail language).
- **Runtime target 8 sessions** hits the Group 1900 runtime cap
  (playbook §14.6 informational). Escalation risk if any child
  spawns a sub-decision.

### 3.4 Recommended taxonomy: Option (b) — 4-child with CONSOLIDATION

**Rationale (my lean):**

1. **The three research questions are mechanically distinct.**
   EventBus producer/consumer map (P1) is a runtime call-site
   sweep. HAI event contract (P2) is a semantic-schema design.
   Cross-substrate composition (P3) is a separation-boundary
   audit + design. Each has distinct evidence surface, distinct
   verification chain, distinct Chris-gate points.

2. **Sequential dependencies match child cut.** P2's HAI event
   contract consumes P1's producer/consumer map (need to know
   which streams exist before designing which HAI events map to
   which stream). P3's cross-substrate composition consumes P2's
   HAI event schema (need to know shape before comparing to
   WebSocket / Telemetry substrates). P4's CONSOLIDATION consumes
   P1 + P2 + P3.

3. **CONSOLIDATION is load-bearing at 4-child.** Event /
   Integration crosses every platform plane; without a
   dedicated cross-plane CONSOLIDATION child, emission-drift
   across Adjacent domains (Memory / Sports / Content / HAI /
   Observability / Authority / Employee OS / Frontend / API /
   Discord) is not visible to per-child audits.

4. **Prior arc precedent.** Groups 1400 / 1500 / 1600 / 1700 /
   1800 / 1900 all ran as multi-child arcs. Groups 1700 / 1800 /
   1900 all included CONSOLIDATION as final pre-xx99 child.
   Group 2000+ mirrors the precedent.

5. **MC-6 CODIFICATION-CONFIRMED promotion opportunity.** MC-6
   was CODIFICATION-READY at S1999 (2 applications: Group 1700
   + Group 1800). Group 1900's P4 CONSOLIDATION was the SECOND-
   consecutive; Group 2000+ P4 would be the THIRD-consecutive,
   with the 8-sub-slot Group 1900 shape proven scalable. Group
   2000+ close would provide the FOURTH data point → MC-6
   CODIFICATION-CONFIRMED milestone.

**Chris D-verdict required at S2000 close (D95, pre-commit):**
Ratify Option (b) OR select alternate.

---

## 4. Parent-vs-single recommendation

**Recommendation: PARENT (multi-child arc).**

Group 2000+ is the SEVENTH parent-arc application of the playbook
§11.1 template. Justification:

**(1) Deliverable diversity.** Three distinct mission-type
deliverables + one CONSOLIDATION audit:
- P1 = Research audit (producer/consumer discovery — call-site sweep).
- P2 = Research + Design (HAI event contract — schema + versioning + retention + consumers).
- P3 = Research + Design (cross-substrate composition — separation contract + duplicate-emission audit).
- P4 = Research audit + CONSOLIDATION (per-plane separation-boundary posture).

Rolling these into a single doc would either (a) blur research/design/audit boundaries per playbook §13 no-blur discipline, or (b) produce a 4000+ line single deliverable that cannot be reviewed as a coherent unit.

**(2) Chris-gate cadence.** P1 has Rigby SIGN + Chris ratification at close but is not a design pick. P2 is a design contract (multi-verdict; D8N series possible). P3 is a design pick (single ratification at close). P4 is CONSOLIDATION audit ratification. Parent structure lets each child receive its own dedicated Chris-gate cycle.

**(3) Sequential dependencies.** P2 consumes P1's producer/consumer map. P3 consumes P2's HAI event schema + F.SYMBOL-MAPPING-STATUS-VERIFICATION status. P4 consumes P1+P2+P3.

**(4) Verifier-loop cadence per MC-1 CODIFICATION-CONFIRMED (S1899).** Every child audit runs its own verifier loop. Parent arc structure gives each child its own verifier-loop scope + SIGN gate.

**(5) Prior arc precedent.** Groups 1400/1500/1600/1700/1800/1900 all ran as multi-child arcs. No single-doc precedent exists for a topic this cross-cutting.

### Runtime target

Runtime target: **6 sessions** (S2000 parent + S2001 P1 + S2002
P2 + S2003 P3 + S2004 P4 + S2099 xx99). Actual runtime may
extend 1–2 sessions if:
- SIGN-with-edits at a child requires more than one fold cycle.
- P2's HAI event contract design spawns a versioning-policy sub-
  decision (S1275 precedent adoption vs. new).
- P3's cross-substrate composition surfaces a load-bearing gap
  requiring a Cat E-analog spawn (e.g., DLQ retention policy as
  its own sub-scope).

Runtime cap: **8 sessions** (S2000 + 6 child slots + xx99).
Beyond 8 sessions, escalate to Chris for re-scoping.

---

## 5. Child mission sequence (Chris-locked pending D95 ratification)

Per §3.4 recommended taxonomy, Group 2000+ will execute this
child sequence:

| Slot | Session | Deliverable | Type | Prereq |
|---|---|---|---|---|
| Parent | S2000 | This doc | Parent scoping (Phase 0) | — |
| **P1** | S2001 | **EventBus Producer/Consumer Map + Contract Verification** — S1274 §12.1 P0 execution | Research audit | S1273 §3.31 shipped; S1274 §12.1 shipped |
| **P2** | S2002 | **HAI Event Contract Design** — S1899 §8.1 item 6 inheritance (4 candidate transitions + six-plane learning-surface + source_kind + versioning + retention + consumers) | Research + Design | P1 shipped; S1275 event schema shipped; S1806 §10 durable-at-six catalog shipped; R.HAI.SOURCE-KIND-ENUM-ADR values inherited |
| **P3** | S2003 | **Cross-Substrate Composition Design** — 6-substrate separation contract + duplicate-emission audit + F.SYMBOL-MAPPING-STATUS-VERIFICATION inheritance | Research + Design | P2 shipped; S1274 §6.2 producer/consumer registry inherited; S1273 §3.31 separation-of-concerns paragraph inherited |
| **P4** | S2004 | **Cat F Adjacent / Separation Boundaries CONSOLIDATION** — mirror Group 1700/1800/1900 F pattern | Research audit + consolidation | P1 + P2 + P3 shipped |
| **xx99** | S2099 | **Canonical summary** — playbook §11.3 12-section EIGHTH application + §11.3 §10 meta-methodology EIGHTH application | Canonical summary | P1 + P2 + P3 + P4 shipped |

**Sequencing note:** children are sequential, not parallel. P2's
HAI event contract consumes P1's producer/consumer map. P3's
cross-substrate composition consumes P2's HAI event schema. P4's
CONSOLIDATION consumes P1 + P2 + P3.

**Session numbering note:** P1–P4 use S2001–S2004 per playbook
§4 intra-range convention. xx99 canonical summary at S2099 (not
S2999 — Group 2000+ uses the Group 2000 range, not a Group 2900
range). Sessions S2005–S2098 remain buffer per playbook §4.6
xx99 buffer discipline in case a child needs mid-arc SIGN
re-work, verifier-loop cycle, or a spawned sibling audit.

**Numbering-scheme note:** the "2000+" label in playbook §22 and
prior arc references reflects that the arc opens somewhere in
the S2000-and-later range. Group 2000+ resolves to Group 2000
for OPEN_ARCS + ARCHITECTURE_INDEX registration purposes.

### 5.1 P1 — EventBus Producer/Consumer Map + Contract Verification (S2001)

**Slot:** Cat A (per playbook §11.2 child audit template).

**Scope:** S1274 §12.1 P0 execution.

**Deliverables:**

- **Publisher call-site sweep** for all 8 streams. For each stream,
  enumerate every call site of the corresponding publisher wrapper
  in `core/services/event_bus.py` (`publish_spider_data_event` +
  4 more). Cross-reference `core/tasks.py` +
  `intelligence/tasks.py` + `core/services/*` + agent classes +
  spider classes.
- **Consumer task body inspection** for
  `process_event_bus_scoring_queue` +
  `process_event_bus_validation_queue` +
  `process_event_bus_analytics_queue` + `get_event_bus_stats`.
  Enumerate what each consumer does with received events (write
  to which model? emit which secondary signal? call which
  service?).
- **Producer→consumer map** with STRONG / WEAK / MISSING /
  UNKNOWN classification per S1274 §12.1 registry style. Cover
  all 8 streams + the 1 DLQ.
- **Contract verification (per Rigby S2000 SIGN cycle 1 Q4 fold
  — expanded)** — deliverable set:
  - **(α) Schema-shape doc per stream** — canonical schema-shape
    doc per stream, versioned, greppable. Enumerate every field
    per event class. Version each doc with `schema_version` header
    per S1275 precedent (unless P2 selects a new versioning
    policy).
  - **(β) Runtime assert audit** — enumerate current + target
    runtime assertions. Where do consumers assert payload shape
    today (e.g., `assert event.data.get('correlation_id')`)?
    Where should they? Flag missing assertions as post-arc
    T-slot items.
  - **(γ) Version gate policy** — how does a schema migration
    land? Adopt S1275 precedent (per-event `schema_version`
    graduation contract), or design a new policy? P1 documents
    the current state; P2 designs the go-forward policy.
  - **(δ) Replay-test enumeration** — which streams can be
    safely replayed for regression-testing? DLQ retention +
    stream retention (`MAXLEN`) inform which replay windows
    exist. Enumerate per stream.
  - Together (α)+(β)+(γ)+(δ) form the "verification/accountability
    surfaces" defending against the "designed but never adopted"
    failure mode Rigby flagged as biggest risk.
- **DLQ audit** — `mi:dead_letter` has no cleanup task (S1274
  §6.2). Enumerate what feeds DLQ + what should consume it.
- **MODEL_TRAINED stream investigation** — publisher wrapper
  UNKNOWN per S1273 §3.31; verify whether the stream is used at
  all.

**Deliverable:** `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md` per playbook §11.2 20-section child template.

**Prereqs:** S1273 §3.31 (shipped); S1274 §6.2 + §12.1 (shipped).

**Rigby SIGN cadence:** Cycle 1 pre-commit per playbook §15
stage-table child-audit row (REQUIRED full SIGN).

**Chris-gate:** Ratification at close (not design pick — P1 is
research audit).

**Runtime target:** 1 session.

### 5.2 P2 — HAI Event Contract Design (S2002)

**Slot:** Cat B.

**Scope guardrail (per Rigby S2000 SIGN cycle 1 Q1 fold):**
Group 2000+ P2 designs event-emission contract semantics for
authority triggers (record_decision-when-authority-PROHIBITED-
fires, record_verification-when-authority-check-lands, etc.);
authority MECHANISM (resolution logic, AuthorityService reads,
per-user policy binding) is out-of-scope and post-arc.

**Scope:** S1899 §8.1 item 6 R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES
execution + six-plane learning-surface event-emission gap
resolution + source_kind enum value adoption + schema-versioning
policy pick + retention posture + consumer registry design.

**Deliverables (all in a single design contract doc):**

- **Event schema for four HAI candidate transitions:**
  `record_decision`, `record_verification`, `auto_approve`,
  `auto_escalate`. Per-event: field shape, required vs.
  optional, JSON schema, mapping to existing HAI models (HAI +
  HFR + HumanPreference).
- **Six-plane learning-surface event schema:** for each of the
  6 planes (HAI-mediated + autonomous_bridge + non_bridge_direct
  + verification_outcome + external_signal + shadow_service),
  define plane-transition event + payload shape. Adopts
  `source_kind` enum from R.HAI.SOURCE-KIND-ENUM-ADR (joint
  Group 1300 + Group 1800 T0/Gate item 5).
- **Schema versioning policy** — pick S1275 precedent (per-
  event `schema_version` field with graduation contract) OR
  design new policy. Justify with backward-compat + forward-
  compat requirements.
- **Retention posture** — pair with joint R.OBSERVABILITY.RETENTION-
  UNIFIED-ADR (Group 1700 T0/Gate) + R.HAI.RETENTION-UNIFIED-ADR
  (Group 1800 T0/Gate). Recommend TTL per event class; recommend
  Redis Streams retention (`MAXLEN`) vs. audit-table retention
  hybrid.
- **Consumer registry** — per event, enumerate expected consumers.
  Draft consumer contracts. Not all consumers implemented at P2
  close; the registry documents the contract.
- **F.PER-USER-AUTHORITY-MECHANISM event-emission contract** —
  per S1903 §19 inheritance, design HAI event candidates for
  per-user authority resolution triggers. Not the mechanism
  itself; the event-emission contract that downstream per-user
  authority resolution will consume.

**Deliverable:** `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md` per playbook §11.2 template modified for design-contract framing (§11.2 §7 Runtime Flows → §7 HAI Event Schema Contract; §11.2 §12 Research Coverage → §12 Schema Alternatives Rejected; §11.2 §17 Duplicate or Overlapping Systems → §17 Consumer Registry + Retention Posture).

**Prereqs:** P1 shipped (need producer/consumer map before
designing HAI event contract); S1275 event schema design
(shipped); S1806 §10 durable-at-six catalog (shipped);
R.HAI.SOURCE-KIND-ENUM-ADR enum values (parked T0/Gate; P2
inherits enum shape but does not re-open joint ADR scope).

**Rigby SIGN cadence:** Cycle 1 pre-commit + optional Cycle 2
post-Chris-gate to pressure-test the versioning-policy choice.

**Chris-gate:** Multi-verdict at close — D8N series covering
each of: (a) schema per transition, (b) versioning policy,
(c) retention posture, (d) consumer registry. Design contract,
not full implementation.

**Runtime target:** 1–2 sessions (may extend if versioning-
policy choice spawns a sub-scope).

### 5.3 P3 — Cross-Substrate Composition Design (S2003)

**Slot:** Cat C.

**Scope:** Design the separation contract across the 6 event-
emitting substrates (EventBus + WebSocket + CeleryTaskEvent +
LLMCallEvent + OpsRunEvent + ToolCallRecord). Answer S1273 §3.31
known-drift questions. Inherit F.SYMBOL-MAPPING-STATUS-VERIFICATION
audit + F.PER-USER-AUTHORITY event-emission contract from P2.

**Deliverables:**

- **6-substrate separation contract** — canonical rule set:
  "when does a new emission go to EventBus vs. WebSocket vs.
  CeleryTaskEvent vs. LLMCallEvent vs. OpsRunEvent vs.
  ToolCallRecord?" Per-substrate criteria. Explicit
  "these emit to more than one substrate intentionally"
  register.
- **Duplicate-emission audit** — grep for existing sites that
  emit to multiple substrates. Classify intentional vs. drift.
  Flag drift for post-arc T-slot cleanup.
- **Substrate × HAI-event mapping** — from P2's HAI event
  schema, map each event to its intended substrate(s). Verify
  no unintentional duplicate emission.
- **Symbol Mapping graduation status verification** — per
  F.SYMBOL-MAPPING-STATUS-VERIFICATION inheritance. Audit
  S1274 §11 4-trigger monitoring status (which triggers have
  fired? which are in warn-mode? which are green?). Recommend
  graduation timing OR extension.
- **DLQ retention decision** — pair with joint retention ADRs
  from Groups 1700 + 1800; recommend TTL vs. unbounded.
- **WebSocket ↔ EventBus overlap resolution** — S1273 §3.31
  drift item; audit specific overlap sites and recommend
  canonical assignment.

**Deliverable:** `docs/research/domains/event_integration_architecture/2003_event_integration_architecture_cat_c_cross_substrate_composition_design_child_audit.md` per playbook §11.2 template.

**Prereqs:** P2 shipped (need HAI event schema before designing
cross-substrate assignment); S1273 §3.31 (shipped); S1899 §8.1
items 4 + 5 (joint retention + source_kind ADRs — parked T0/Gate;
P3 inherits scope hooks but does not execute the ADRs).

**Rigby SIGN cadence:** Cycle 1 pre-commit.

**Chris-gate:** Multi-verdict at close for (a) separation
contract, (b) duplicate-emission cleanup priorities, (c) DLQ
retention posture, (d) WebSocket ↔ EventBus canonical
assignment.

**Runtime target:** 1 session.

### 5.4 P4 — Cat F Adjacent / Separation Boundaries CONSOLIDATION (S2004)

**Slot:** Cat F CONSOLIDATION (mirror Group 1700/1800/1900 F
pattern; **THIRD-consecutive** F CONSOLIDATION application →
MC-6 CODIFICATION-CONFIRMED milestone at S2099 close).

**Scope:** Consolidate the separation-boundary posture between
Event / Integration Architecture and every adjacent domain
surface.

**Scope precision (inheriting Group 1900 P4 discipline):**
This is a **separation-boundary posture audit (interface +
seam audit)** — a review of interfaces, seams, emission
touchpoints, consumer-registration seams, and cross-substrate
composition joins between Event / Integration and each
adjacent domain. It is **NOT** an audit of each adjacent
domain's internal correctness or implementation quality.
Prior arc audits own their respective internal-correctness
verdicts. Group 2000+ P4 audits the seams between event /
integration and those domains.

**P4 checks / P4 does NOT check:**

| P4 CHECKS | P4 does NOT check |
|---|---|
| Interface + seam between event/integration and each adjacent domain | Internal correctness of any adjacent domain |
| Emission touchpoints where an adjacent domain writes to a substrate | Domain-owned implementation quality |
| Consumer-registration seams where an adjacent domain subscribes to a substrate | Adjacent domain's own governance / autonomy / budget layers |
| Duplicate emission-adjacent primitives across domains | Adjacent domain's test coverage or SLO posture |
| Gap points where a domain assumes an event fires but P2's contract doesn't cover it | Domain-specific ADR bundles or T-slot execution items |
| Separation-boundary policy (which emission decisions owned by Group 2000+ vs delegated to adjacent domain) | Anything in scope of Group 1300/1500/1600/1700/1800/1900 post-arc T-slot queues |

**Deliverables:**
- **Separation-boundary posture audit (interface + seam audit)**
  for each plane event/integration touches: Memory (Group 1300)
  / Sports (Group 1500) / Content (Group 1600) / Observability
  (Group 1700) / HAI (Group 1800) / Authority Enforcement
  (Group 1900) / Employee OS / Frontend / API / Discord.
- Register "emission touchpoints" — where does an adjacent
  domain write to a substrate? Are there duplicate emissions?
  Are there gap points where a domain assumes an event fires
  but P2's contract doesn't cover it?
- Register "consumer-registration seams" — where does an
  adjacent domain subscribe to a substrate? Are subscribers
  registered? Are there orphaned subscribers?
- Register "separation boundary posture" — which emission
  decisions are owned by Group 2000+ vs. delegated to a
  domain's own governance/telemetry layer?
- Follow-on queue candidates for post-arc T-slot execution.

**Deliverable:** `docs/research/domains/event_integration_architecture/2004_event_integration_architecture_cat_f_adjacent_separation_boundaries_child_audit.md` per playbook §11.2 template + §16 CONSOLIDATION shape from S1806 Group 1800 Cat F + S1904 Group 1900 Cat F precedent.

**Prereqs:** P1 + P2 + P3 shipped.

**Rigby SIGN cadence:** Cycle 1 pre-commit.

**Chris-gate:** Ratification at close.

**Runtime target:** 1 session.

### 5.5 xx99 — Canonical summary (S2099)

**Slot:** xx99 canonical summary.

**Scope:** Playbook §11.3 12-section canonical-summary template
**EIGHTH** application + §11.3 §10 meta-methodology template
**EIGHTH** application.

**Deliverables (all 12 sections + Appendix):**
- §1 Executive Summary
- §2 What This Arc Answered
- §3 Consolidated Domain Shape
- §4 Cross-Cutting Patterns
- §5 Resolved Contradictions
- §6 Unresolved Unknowns
- §7 Anchor-Update Recommendations (PLATFORM_WHAT_IT_IS +
  PLATFORM_INVENTORY + CLAUDE.md + docs/EVENT_SYSTEM_INVENTORY.md
  + docs/topics/agent-system.md as needed)
- §8 Follow-On Research Queue (T0/Gate + T1 + T2 + T3 tiered)
- §9 Cross-Links to Delegated Arcs
- §10 What This Research Taught Us About How to Do Research
  (EIGHTH meta-methodology application; MC-4 CODIFICATION-CONFIRMED-
  with-scope-guardrails at S1999 gets 3rd + 4th arc application →
  CODIFICATION-CONFIRMED-without-guardrails candidate; MC-6
  CODIFICATION-READY at S1999 gets 3rd + 4th application →
  CODIFICATION-CONFIRMED milestone; MC-7/MC-8/MC-9/MC-10
  candidates from S1999 evaluated for promotion.)
- §11 Arc Change Log
- §12 Appendix — Provenance

**Deliverable:** `docs/research/domains/event_integration_architecture/2099_event_integration_architecture_canonical_summary.md`.

**Prereqs:** P1 + P2 + P3 + P4 shipped.

**Rigby SIGN cadence:** Cycle 1 single-batch 4-question routed
via arc pin `pa-dd7e973617da464d` per playbook §15 stage-table
canonical-summary row.

**Chris-gate:** Ratification at close + arc pin retirement via
`session_tool.retire` per playbook §16 arc-close discipline.

**Runtime target:** 1 session.

---

## 6. Parked candidate issues

Candidates considered for children but explicitly parked. These
may re-surface as post-arc T-slot execution items or as future
research arcs.

### 6.1 Parked from Option (c) 6-child taxonomy

- **Cat A — EventBus infrastructure inventory as standalone
  child.** Parked into P1 § "Infrastructure Inventory". Rationale:
  §12.1 P0 authorial framing treats infrastructure inventory as
  part of the producer/consumer sweep; splitting would fragment.
- **Cat B — EventBus producer/consumer map as standalone child.**
  Parked into P1 core scope. Rationale: this IS the P0 scope.
- **Cat C — EventBus contract verification as standalone child.**
  Parked into P1 § "Contract Verification". Rationale: verification
  is the sanity check on the map; splitting would drop context.

### 6.2 Parked from Group 1800 T0/Gate inheritance

- **R.HAI.LEARNING-PLANE-CONTRACT-ADR** (Joint Group 1300 +
  1800) — touches P2 HAI event contract but is primarily a
  Memory + HAI single-canonical-entrypoint ADR. Group 2000+ P2
  references it where relevant but does not own it.
- **R.HAI.DUPLICATE-FILE-COLLISION-CONSOLIDATION** — Group 1800
  arc-specific; not Group 2000+ scope.
- **R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE** — Group 1800
  arc-specific; not Group 2000+ scope.
- **R.HAI.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.RETENTION-
  UNIFIED-ADR joint bundle** — Groups 1700 + 1800 T0/Gate paired;
  Group 2000+ P2 + P3 inherit retention posture recommendations
  as inputs (P2 event-retention pairs; P3 DLQ retention pairs)
  but do NOT execute the joint ADR bundle.
- **R.HAI.SOURCE-KIND-ENUM-ADR** — Joint Group 1300 + Group 1800
  schema-change; T0/Gate item 5. Group 2000+ P2 inherits enum
  values for HAI event schema but does NOT re-open joint ADR
  scope.

### 6.3 Parked from Group 1900 inheritance

- **F.SYMBOL-MAPPING-STATUS-VERIFICATION** → Group 2000+ P3 scope
  (see §5.3).
- **F.PER-USER-AUTHORITY-MECHANISM (design)** → Group 2000+ P2
  scope for event-emission contract (see §5.2). MECHANISM
  implementation post-arc; Group 2000+ designs only the
  event-emission contract for downstream consumers.
- **Group 1900 §8 20-item T-tier queue** — remains Chris-gated
  post-arc execution; Group 2000+ does not consume.
- **R.CONTENT.PUBLISHGATE-AUTHORITY-COMPOSITION** — Group 1900 T1
  item; Group 2000+ scope may reference where PublishGate
  emissions touch EventBus, but does NOT execute the composition
  design (that's Group 1600 + Group 1900 joint scope).

### 6.4 Parked from S1699 §7.4 cross-arc

- **auto_publish "daily 6 AM" 5 doc PRs owed** — Group 1600
  arc-close inherited debt; Group 2000+ P3 may reference where
  content-plane emissions touch EventBus but does NOT close
  the doc PRs.

### 6.5 Parked as post-arc execution items

Not researched by Group 2000+ — flagged for post-arc T-slot
execution once P2 design contract is Chris-gated:
- Implementation PRs for HAI event emission at four candidate
  transitions.
- Implementation PRs for six-plane learning-surface event
  emission.
- Producer/consumer map fixes (adding missing publishers,
  wiring orphaned consumers).
- DLQ cleanup task addition.
- WebSocket ↔ EventBus overlap cleanup (per P3 canonical
  assignment).
- Schema-versioning migration if P2 recommends new versioning
  policy over S1275 precedent.
- Symbol Mapping graduation execution if P3 recommends (per
  S1274 §11 graduation triggers).
- Per-user authority MECHANISM implementation (per Group 1900
  P3 §19 F.PER-USER-AUTHORITY-MECHANISM inheritance — Group
  2000+ designs event-emission contract only; mechanism is
  post-arc).

---

## 7. Anti-scope

Group 2000+ will NOT do the following. This is enforced per
playbook §14.5 no-implementation rule.

### 7.1 No runtime changes

- **No modifications** to `core/services/event_bus.py` (EventBus),
  `core/tasks.py` event-bus consumer tasks, any WebSocket
  consumer, or any of the six telemetry substrates.
- **No migrations** — no schema changes on
  `CeleryTaskEvent` / `LLMCallEvent` / `OpsRunEvent` /
  `ToolCallRecord` / any HAI arc model; no new EventBus streams
  materialized in code; no new consumer groups added.
- **No new PA tool handlers** or PA tool schema additions.
- **No new Celery tasks** or beat schedule additions.
- **No WebSocket consumer changes** or channel-layer routing
  changes.

### 7.2 No design decisions outside child slots

**Scope guardrail (per Rigby S2000 SIGN cycle 1 Q1 fold — echo
of §5.2 preamble):** Group 2000+ designs event-emission
contract semantics for authority triggers; authority MECHANISM
(resolution logic, AuthorityService reads, per-user policy
binding) is out-of-scope and post-arc. Any P2 or P3 draft that
proposes MECHANISM implementation is a §7.2 anti-scope
violation and must be re-scoped or deferred to post-arc T-slot
execution.

- **No re-opening of S1275 Symbol Mapping event schema design.**
  S1275 established the schema-versioning precedent; Group 2000+
  P2 either adopts or explicitly rejects with rationale.
- **No re-opening of S1274 Option E v0 recommendation.** Option E
  stands; Group 2000+ P3 audits graduation-trigger status (per
  F.SYMBOL-MAPPING-STATUS-VERIFICATION) but does not re-litigate
  the v0 selection.
- **No re-opening of Group 1800 T0/Gate item 5 R.HAI.SOURCE-KIND-
  ENUM-ADR joint scope.** Group 2000+ P2 inherits enum values but
  does not re-design the enum itself (which is joint Group 1300
  + Group 1800 arc scope).
- **No re-opening of Group 1900 authority enforcement mode +
  option pick.** Group 1900 P2 established the enforce-mode
  design decision; Group 2000+ inherits it as input.
- **No overriding of S1273 §3.31 separation-of-concerns**
  (EventBus is runtime coordination; telemetry substrates are
  audit-after-the-fact). Group 2000+ P3 audits overlap but does
  NOT merge substrates.
- **No parallel-execution of children.** Per playbook §14.5 +
  memory rule `feedback_no_parallel_research_arcs.md`: children
  are sequential (P1 → P2 → P3 → P4 → xx99).

### 7.3 No design-decision blur

- **P1 does NOT design event schema** — P1 discovers the
  producer/consumer map; the map informs P2's design.
- **P2 does NOT decide cross-substrate composition** — P2
  designs the HAI event contract; cross-substrate composition
  is P3.
- **P2 does NOT design implementation** — P2 designs the
  contract; implementation is post-arc.
- **P3 does NOT re-open S1273 §3.31 separation-of-concerns** —
  that's the accepted state; P3 designs the composition policy
  going forward.
- **P4 does NOT audit individual adjacent domains for internal
  correctness** — P4 audits the SEPARATION BOUNDARY between
  event/integration and each adjacent domain.

### 7.4 No parent scope creep

- **No inclusion of joint T0/Gate ADR execution.** R.HAI.LEARNING-
  PLANE-CONTRACT-ADR + R.HAI.SOURCE-KIND-ENUM-ADR + joint
  retention ADR bundle all remain Chris-gated joint work outside
  Group 2000+ scope.
- **No inclusion of per-user authority MECHANISM implementation.**
  F.PER-USER-AUTHORITY-MECHANISM is inherited for event-emission
  contract design only; the mechanism itself is post-arc.
- **No inclusion of Group 1900 §8 T-tier execution.**

### 7.5 No implementation coordination with other subsystems

- **No PR coordination with Group 1300 Memory** on
  R.HAI.LEARNING-PLANE-CONTRACT-ADR.
- **No PR coordination with Group 1800 HumanAttention** on
  §8.1 T0/Gate items.
- **No PR coordination with Group 1700 Observability** on
  RETENTION-UNIFIED-ADR.
- **No PR coordination with Group 1900 Authority Enforcement**
  on §8 20-item T-tier queue.

---

## 8. Decisions recorded (Chris-locked pending §9 close)

Group 2000+ opens with 1 explicit Chris D-verdict already
ratified (D94 — accept playbook §22 default). Additional D-
verdicts (D95, D96, D97) require Chris ratification at S2000
close.

### D94 — Group 2000+ scope = Event / Integration Architecture (RATIFIED 2026-07-04)

**Decision:** Group 2000+ scope is Event / Integration Architecture
per playbook §22 default queue lean. NOT a D-override.

**Rationale (Chris confirmation "Default" 2026-07-04):**
- Playbook §22 default queue lean for post-Group-1900 arc has
  been Event / Integration Architecture since S1899 close.
- Two consecutive prior D-overrides (S1800 HumanAttention over
  Event Architecture; S1900 Authority Enforcement over Event
  Architecture) parked the Event Architecture scope with each
  D-override; the pattern of parking is now exhausted with
  inherited T0/Gate + F.SYMBOL-MAPPING + F.PER-USER-AUTHORITY
  handoff pressure.
- Group 1800 xx99 §8.1 item 6 R.EVENTS.HAI-EVENT-CONTRACT-
  CANDIDATES is explicitly parked as "Group 1900 arc-open
  scoping" — inheritance already assumes Group 2000+ = Event
  Architecture.

**Impact:** Group 2000+ arc scope = Event / Integration
Architecture (4-child + xx99 pending D95 taxonomy ratification).

### D95 — 4-child taxonomy with CONSOLIDATION (PENDING RATIFICATION at §9)

**Proposed decision:** Group 2000+ = 4-child arc:
- P1 = EventBus Producer/Consumer Map + Contract Verification
  (S2001)
- P2 = HAI Event Contract Design (S2002)
- P3 = Cross-Substrate Composition Design (S2003)
- P4 = Cat F Adjacent / Separation Boundaries CONSOLIDATION
  (S2004)
- xx99 canonical summary at S2099

**Rationale (per §3.4 my lean):**
- Respects runtime-vs-contract-vs-composition distinction from
  S1273 §3.31.
- Adds proven CONSOLIDATION pattern (THIRD-consecutive after
  Groups 1700/1800/1900) → MC-6 CODIFICATION-CONFIRMED
  milestone at S2099 close.
- Runtime target ~6 sessions (Group 1900 precedent).
- Aligns child slots 1:1 with inherited T0/Gate items.

**Trade-off accepted (subject to Chris ratification):** Group
2000+ as 4-child does NOT observe MC-4 durability-under-6-child-
arcs milestone. MC-4 observation deferred to a future 6-child arc.

**Chris D-verdict at S2000 close ratifies OR selects alternate.**

### D96 — Mint fresh Group 2000+ arc pin (EXECUTED as operational default)

**Decision:** Mint fresh Group 2000+ arc pin at S2000 open;
`tools/pa_local.sh:215` rotates immediately.

**Executed:** Rigby `session_tool.create_fresh` minted
`pa-dd7e973617da464d` (title "Session 2000 — Group 2000+ Event
/ Integration Architecture parent scoping") at S2000 open.
Wrapper rotated at line 215 + header ledger updated with S2000
mint documentation + Group 1900 pin retirement entry.

**Rationale:** Playbook §16 arc-open fresh-thread discipline;
inherited MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at
S1999 close.

**Not a new Chris D-verdict** — operational default per playbook
§16 arc-open protocol.

### D97 — Route Rigby light SIGN cycle 1 on parent scoping (RATIFIED + EXECUTED 2026-07-04)

**Decision:** Route Rigby light SIGN cycle 1 pre-commit on this
S2000 parent scoping doc.

**Executed 2026-07-04:** Rigby SIGN cycle 1 routed via arc pin
`pa-dd7e973617da464d`. Single-batch 4-question pressure test
posted at Rigby's discretion. **Cycle 1 CLEAN verdict at 0.86
confidence** with 4 required folds — all landed in-place pre-
commit (Q1 §5.2+§7.2 scope guardrail, Q2 §2.6.2 evidence
bundle discipline, Q3 §2.6.1 inheritance precedence subsection,
Q4 §5.1 P1 Contract Verification 4-deliverable expansion).
**D48 38th arm CLEAN turn 1** → 32-consecutive-fully-clean-arms
sub-pattern extended to **33-consecutive** (MC-2 CODIFICATION-
CONFIRMED milestone extended 32 → 33).

**Rationale:**
- S2000 = SEVENTH application of playbook §11.1 template; SIGN
  keeps the pattern honest.
- D48 38th arm at Group 2000+ parent scoping — MC-2
  32-consecutive-fully-clean-arms sub-pattern CODIFICATION-
  CONFIRMED extension milestone opportunity ACHIEVED.
- Playbook §15 stage-table parent-row light-SIGN default is
  OPTIONAL; Chris opted in.

### Operational defaults / inherited constraints (not new Chris D-verdicts)

Per Rigby S1900 SIGN cycle 1 Q2 fold precedent: the items below
are recorded here for traceability but are **NOT** new Chris
D-verdicts. They are operational defaults derived from prior arc
precedent + playbook + memory rules.

**O1 — Sequential child execution** — children run sequentially
(P1 → P2 → P3 → P4 → xx99), not in parallel. Rationale: F3-F8
sequential dependencies + memory rule
`feedback_no_parallel_research_arcs.md`.

**O2 — xx99 §10 EIGHTH meta-methodology application** — Group
2000+ xx99 canonical summary at S2099 includes §10 "What This
Research Taught Us About How to Do Research" per playbook §11.3
EIGHTH application (after S1399 / S1499 / S1599 / S1699 / S1799
/ S1899 / S1999). Rationale: memory rule
`feedback_xx99_meta_methodology_section.md`.

**O3 — Post-arc docs cascade** — every child close + xx99 close
runs the full 4-step docs cascade (`build_docs_index` +
`build_rag_corpus` + `sync_docs_index_to_documents` +
`sync_docs_index_to_documents --embed`) + `build_docs_provenance`.
Rationale: memory rule
`feedback_cascade_pr_must_include_embed_step.md`.

---

## 9. Next step

### 9.1 Immediate (S2000 close)

1. **Chris D-verdict batch** on this parent scoping doc:
   - **D95** — Ratify 4-child + CONSOLIDATION taxonomy per §3.4
     recommendation OR select alternate.
   - **D97** — Opt in on Rigby light SIGN cycle 1 pre-commit
     OR skip.
2. **If D97 = opt-in:** Route Rigby light SIGN cycle 1 pre-
   commit. Single-batch 4-question routed via arc pin
   `pa-dd7e973617da464d`. D48 38th arm anticipated CLEAN turn 1
   per MC-2 32-consecutive-fully-clean-arms sub-pattern.
3. **Fold** any SIGN-with-edits from cycle 1 pre-commit.
4. **Chris commit-gate** on S2000 artifact set + Rigby SIGN
   record.
5. **ARCHITECTURE_INDEX** bump v64 → v65 with §1.68 S2000
   registration + line-6 v65 preamble (preserving v64 preamble
   as tail).
6. **OPEN_ARCS** move Group 2000+ row from Not-started → In-
   progress; last_updated bump with S2000 open preamble;
   preserve S1999 close preamble as tail.
7. **S2000 handoff** at
   `docs/handoffs/SESSION_2000_EVENT_INTEGRATION_ARCHITECTURE_PARENT_SCOPING.md`.
8. **Overwrite `00-START-NEXT-SESSION.md`** to point at S2001 P1
   EventBus Producer/Consumer Map + Contract Verification as
   next-session priority.
9. **Post-merge 4-step docs cascade** + `build_docs_provenance`
   per memory rule (may batch into S2000 arc-open PR or into
   S2001 open PR per Chris preference).

### 9.2 Next session (S2001)

Execute **P1 EventBus Producer/Consumer Map + Contract
Verification** per §5.1:
- Publisher call-site sweep for all 8 streams.
- Consumer task body inspection.
- Producer→consumer map with STRONG/WEAK/MISSING/UNKNOWN
  classification.
- Contract verification (payload-shape × consumer-expectation
  match).
- DLQ audit.
- MODEL_TRAINED stream investigation.
- Deliverable: `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md` per playbook §11.2 20-section child template.
- Rigby SIGN cycle 1 pre-commit (REQUIRED full SIGN per §15).
- Chris ratification at close.

### 9.3 Arc completion path

| Session | Deliverable | Chris-gate |
|---|---|---|
| S2000 | Parent scoping (this doc) | Ratification + D94–D97 commit |
| S2001 | P1 EventBus Producer/Consumer Map + Contract Verification | Ratification |
| S2002 | P2 HAI Event Contract Design | Multi-verdict Chris design-ratify (D8N series) |
| S2003 | P3 Cross-Substrate Composition Design | Multi-verdict Chris design-ratify |
| S2004 | P4 Cat F Adjacent / Separation Boundaries CONSOLIDATION | Ratification |
| S2099 | xx99 canonical summary | Ratification + arc pin `pa-dd7e973617da464d` retire per playbook §16 |

Runtime target: **6 sessions**. Runtime cap: **8 sessions**
(buffer for SIGN-with-edits, spawned sub-decisions, or Cat E-
analog spawn from P2 versioning-policy or P3 composition).

---

## Appendix — Frontmatter provenance

### A.1 Playbook §11.1 template SEVENTH application

Group 2000+ parent scoping is the **SEVENTH application** of the
playbook §11.1 9-section parent scoping template:

| Session | Group | Domain | §11.1 Application |
|---|---|---|---|
| S1400 | 1400 | Revenue | FIRST |
| S1500 | 1500 | Sports | SECOND |
| S1600 | 1600 | Content | THIRD |
| S1700 | 1700 | Observability | FOURTH |
| S1800 | 1800 | HumanAttention | FIFTH |
| S1900 | 1900 | Authority Enforcement | SIXTH |
| **S2000** | **2000+** | **Event / Integration Architecture** | **SEVENTH** |

**MC-4 durability observation:** Group 2000+ with 4-child
structure does NOT qualify for arc-pin routing durable-by-6th-
application under 6-child arcs observation. Group 2000+ close
extends MC-4 SEVENTH-consecutive-application observation under
CONFIRMED-with-scope-guardrails status; upgrade to without-
guardrails requires a distinct arc shape (e.g., 5-child or
8-child).

**MC-6 CODIFICATION-CONFIRMED milestone opportunity:** MC-6 was
CODIFICATION-READY at S1999 close (2 applications: Group 1700 F
+ Group 1800 F). Group 1900's P4 CONSOLIDATION was the SECOND-
consecutive; Group 2000+ P4 (if D95 ratified) would be the
THIRD-consecutive, with Group 2000+ close providing the FOURTH
data point → MC-6 CODIFICATION-CONFIRMED milestone.

### A.2 Companion doc lineage

| Companion | Session | Contribution to Group 2000+ |
|---|---|---|
| `platform_architecture_inventory.md` §3.31 | S1273 | EventBus row: 8 streams + 3 consumer groups + DLQ; EXPERIMENTAL maturity; producer/consumer registry ABSENT; separation-of-concerns paragraph. |
| `cross_domain_integration_audit.md` §12.1 + §6.2 | S1274 | P0 EventBus Adoption + Contract Verification; Rigby SIGN v2 correction (WEAK not "dormant"); publisher wrappers + consumer tasks registry. |
| `symbol_mapping_event_schema_design.md` | S1275 | Event schema versioning precedent; enforcement-adjacent event shapes. |
| `1399_memory_canonical_summary.md` | S1399 | R.HAI.LEARNING-PLANE-CONTRACT-ADR joint scope; source_kind provenance enum inheritance. |
| `1699_content_canonical_summary.md` | S1699 | Content plane emission points; auto_publish 5 doc PRs owed (cross-arc). |
| `1799_observability_canonical_summary.md` | S1799 | Telemetry retention posture; R.OBSERVABILITY.RETENTION-UNIFIED-ADR paired with Group 1800. |
| `1899_human_attention_canonical_summary.md` §8.1 item 6 | S1899 | R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES T0/Gate — the Group 2000+ P2 inheritance. |
| `1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md` §7.4 + §10 | S1806 | Six-plane learning-surface fragmentation event-emission gap durable-at-six; CONSOLIDATION shape precedent. |
| `1904_authority_enforcement_cat_f_adjacent_separation_boundaries_child_audit.md` | S1904 | CONSOLIDATION shape precedent (8 sub-slot scaling); §17.1 per-plane separation-boundary posture register template. |
| `1903_authority_enforcement_cat_c_cross_plane_composition_design.md` §19 | S1903 | F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM Group 2000+ inheritance. |
| `1999_authority_enforcement_canonical_summary.md` §10 | S1999 | MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails baseline; MC-5 CODIFICATION-CONFIRMED baseline; MC-6 CODIFICATION-READY baseline; MC-7/MC-8/MC-9/MC-10 candidates. |
| `EVENT_SYSTEM_INVENTORY.md` | Living | Existing event-system inventory (Tier 6 reference; may drift). |
| `DOMAIN_RESEARCH_PLAYBOOK.md` | Living | §11.1 template + §14.5 no-implementation rule + §22 default queue lean + §16 arc-pin discipline. |
| `ARCHITECTURE_INDEX.md` | Living | §1.68 S2000 registration (bumped v64 → v65 at close). |
| `OPEN_ARCS.md` | Living | Group 2000+ row Not-started → In-progress at S2000 close. |
| `EMPLOYEE_OS_PRIMITIVES.md` | Living | Emission touchpoint primitives (`OpsRun`/`OpsRunEvent` from Employee OS layer). |

### A.3 Verifier loop notes

Parent scoping doc; no independent Explore-sub-agent sweeps
performed. Load-bearing structural claims about the domain shape
inherit from S1273 §3.31, S1274 §12.1 + §6.2, S1899 §8.1, S1903
§19, S1806 §10 verifier-loop findings.

Re-attestation of 7 verification chains recorded in frontmatter
`verifier_loop` field. No new verification chains needed at
parent scope; child audits will run their own verifier loops per
playbook §13 discipline + MC-1 CODIFICATION-CONFIRMED (S1899).

### A.4 Rigby SIGN routing (D97 executed 2026-07-04)

- **Arc pin:** `pa-dd7e973617da464d` (fresh Group 2000+ pin,
  minted 2026-07-04).
- **Cycle 1 scope:** Single-batch 4-question pressure test on
  this parent scoping doc, pre-commit.
- **D48 arm outcome:** 38th arm CLEAN turn 1 → 32-consecutive-
  fully-clean-arms sub-pattern extended to **33-consecutive**
  (MC-2 CODIFICATION-CONFIRMED milestone extended 32 → 33).
- **SIGN questions posted 2026-07-04** (Rigby's discretion per
  playbook §15 pressure-test standard set):
  - Q1 — Taxonomy posture (authority-trigger semantics: first-
    class contract vs. downstream consumers vs. middle ground).
  - Q2 — Runtime re-attestation bundle (a/b/c mandatory-at-
    parent split).
  - Q3 — Cross-pattern inheritance precedence order 1-2-3.
  - Q4 — Most-important-thing-missed risk pre-mortem.
- **Cycle 1 verdict:** CLEAN at 0.86 confidence with 4 required
  folds. All 4 folded in-place pre-commit (no scope changes).
- **Cycle 2:** NOT REQUIRED per Rigby verdict (single-turn
  close on 4-question batch answers).
- **Fold landed pre-commit:**
  - Q1 fold: §5.2 P2 preamble + §7.2 anti-scope scope guardrail
    (authority MECHANISM out-of-scope; contract semantics
    in-scope).
  - Q2 fold: §2.6.2 runtime evidence bundle parent-vs-child
    discipline explicit statement.
  - Q3 fold: §2.6.1 inheritance precedence order 1-2-3
    subsection (R.EVENTS.HAI spine → F.PER-USER-AUTHORITY
    constraint → F.SYMBOL-MAPPING P3 gate).
  - Q4 fold: §5.1 P1 Contract Verification 4-deliverable
    expansion (α schema-shape doc / β runtime assert audit /
    γ version gate policy / δ replay-test enumeration).
