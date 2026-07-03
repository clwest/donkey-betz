---
title: "S1700 Observability / Telemetry / SLOs — Parent Architecture Scoping (Group 1700 mission plan)"
status: active (parent — Chris D-decisions D69 D70 D71 D72 D73 D74 locked 2026-07-02 via "agree all + SIGN" ratification round; Rigby light SIGN cycle 1 SIGN-with-edits at High confidence — F1-F6 folds landed pre-commit — 2 CONFIRM + 2 MUST-FIX + 4 FLAG-EDIT; F1 Cat C write-path boundary sentence + F2 Cat F sub-slots F.a-F.e with stop conditions + F3 Cat B/Cat D accounting rule + F4 P5 dependency clause P1+P3+P4 → P1+P2+P3+P4 + F5 §5 Correlation primitives working-definitions box HYPOTHESIS-TO-BE-VERIFIED with 5 primitives (task_id / execution_id / trace_id / tool_call_id / mission_id) + F6 §7 anti-scope items 19/20/21 (Frontend/WebSocket telemetry + Auth token telemetry + RigbyTelemetry new-layer buildout))
authority: parent-doc for Group 1700 research arc + FOURTH application of Chris's Phase 0 3-step methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) — playbook v3 §11.1 template promotion CONFIRMED-STRENGTHENED via Group 1600 fourth-application (S1699 §10 meta-methodology) with F.i/F.ii/F.iii durable at fourth-application; this arc applies methodology unchanged for four-consecutive-application confirmation + adopts D62 = (a) 6-sibling exemplar mini-schema propagation-upfront pattern per S1599 §10.2 codify-ready candidate (extended by S1699 §10.2)
category: parent_scoping
session: 1700
date: 2026-07-02
decisions_locked: 2026-07-02 (D69 D70 D71 D72 D73 D74 all Chris-ratified via "agree all + SIGN" round; SIGN cycle 1 SIGN-with-edits at High confidence delivered F1-F6 folds all landed pre-commit; no D-verdict override or edit required)
domain_slug: observability
research_group: 1700
authors: Claude Code (Chris directed via short command "Start research group 1700" at S1700 open; D1-D2-D3 ratified via terminal card: D1 = Observability domain confirmed; D2 = delegate event architecture to Group 1900; D3 = parent-only this session, P1 next-session)
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                             # process — §11.1 template applied here for the fourth time
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                    # OS — arc-open contract §8.1; §12.3 "Start Group NNNN: Observability" target
  - docs/research/OPEN_ARCS.md                                            # arc manifest — Group 1600 → Group 1700 handoff
  - docs/research/ARCHITECTURE_INDEX.md                                    # v42 → v43 bump owed at S1700 close (§1.46 registration)
  - docs/research/platform/cross_domain_integration_audit.md              # S1274 15-finding baseline; §11.6 "5-layer execution-telemetry dedup" originating evidence
  - docs/research/platform_architecture_inventory.md                       # S1273 32-domain map; §3.25 Observability row (DEEP coverage tier); §5.13 dedup naming
  - docs/research/domains/memory/1300_memory_domain_scoping.md            # parent-with-children exemplar (S1300 — first arc parent)
  - docs/research/domains/memory/1399_memory_canonical_summary.md         # first formal xx99 canonical summary (S1399)
  - docs/research/domains/revenue/1400_revenue_domain_scoping.md          # first application of Phase 0 F.i/F.ii/F.iii methodology (S1400) — trigger 1 of two-triggers rule
  - docs/research/domains/revenue/1499_revenue_canonical_summary.md       # second xx99 canonical summary + second §11.3 §10 template application
  - docs/research/domains/sports/1500_sports_domain_scoping.md            # second application of Phase 0 methodology (S1500) — trigger 2 of two-triggers rule
  - docs/research/domains/sports/1599_sports_canonical_summary.md         # third xx99 + §12.4 discriminative-value criterion → playbook v3 §11.1 promotion TRIGGERED
  - docs/research/domains/content/1600_content_domain_scoping.md          # third application of methodology (S1600); fourth-application prep
  - docs/research/domains/content/1699_content_canonical_summary.md       # fourth xx99 canonical summary; §10 fourth-application meta-methodology confirms F.i/F.ii/F.iii durable
  - docs/topics/celery-workers.md                                         # Sessions 983/1113/1167/1169 observability sections (CeleryTaskEvent, worker instrumentation, retention, monitor-task overhead)
  - docs/topics/agent-system.md                                           # ToolCallRecord (S970 + S1115 all-return-path fix), AgentExecution wrapper, provenance sections
  - docs/PLATFORM_INVENTORY.md                                            # runtime counts anchor (Body Systems 9, Celery beat 92 enabled, Discord 96 commands)
  - docs/PLATFORM_WHAT_IT_IS.md                                           # narrative anchor
scope: Phase 0 domain-definition — decide whether Group 1700 is a single canonical audit or a parent-with-children research arc; produce candidate subdomain taxonomy grounded in verified runtime surface; propose child mission sequence for Chris to lock; frame (do NOT decide) the analog D59/D65-load-bearing question — "are the 5 execution-telemetry layers structurally separable, or do they need canonical unification (execution_id + trace_id spine)?" — as the arc's lens question owed to xx99 canonical summary as evidence plan, not recommendation
non_goals:
  - the audit itself (that begins after Chris picks parent-vs-single + locks §5 sequence)
  - answering the 28 playbook canonical questions (that is the audit's job)
  - resolving the load-bearing dedup posture at Phase 0 (requires child evidence sweeps; posture-decision framing + evidence plan only — Chris gates actual selection post-arc after xx99 evidence lands)
  - any implementation proposal (this is scoping, not architecture design)
  - event bus / pub-sub / routing design (delegated to Group 1900 Event Architecture per D2 ratification)
  - Content Deliverable event contracts (Group 1600 Content arc already closed at S1699 xx99; T0/Gate R.CONTENT.XX99-ADR-BUNDLE owns)
  - Memory learning-loop internals (Group 1300 Memory arc closed at S1399; observability of Memory-writes is in-scope but Memory internal correctness is not)
  - SLO framework DESIGN (in-scope: audit what SLO coverage exists today; out-of-scope: design the systemic SLO framework — that's a follow-on design-preparation arc if Chris ratifies at xx99)
  - Rigby v0 event intake activation (RIGBY_EVENT_INTAKE_ENABLED=False today per S1273 line 1959; Group 1700 audits observability gaps; wiring Rigby to intake is a downstream implementation project)
delegates_to:
  - Group 1900 Event Architecture arc (event bus adoption, cross-domain event routing/schema versioning, DeliverableEvent + ImpactEvent + EngagementEvent producer-consumer contracts — per D2 ratification at S1700 open)
  - Group 1600 Content arc (already closed; T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E owns DeliverableEvent consumer-contract disposition — Group 1700 evidence should inform whether DeliverableEvent producer-side telemetry is complete, but consumer wiring is Content's ADR)
  - Group 1300 Memory arc (closed; AgentMemory + UserAgentLearning writer telemetry is in-scope for Group 1700; Memory learning-loop business logic is Memory domain scope only)
  - Employee OS (concurrent, not a separate arc — MissionRunner + AIEmployee + JobContract own mission execution; Group 1700 audits OpsRunEvent audit trail from those runs; MissionRunner internal correctness is Employee OS scope)
delegated_from:
  - S1273 §3.25 Observability row (DEEP-coverage-tier baseline)
  - S1273 §5.13 "5-layer execution-telemetry dedup" mission naming
  - S1274 §11.6 cross-domain integration audit dedup evidence
  - S1699 §8 T-slots (Content arc T-slot handoffs relevant to observability: DeliverableEvent producer-side telemetry, PA-tool feedback bridge learning telemetry)
owner: claude (Chris directed at S1700 open via short command "Start research group 1700"; D1-D2-D3 ratified via terminal card)
verifier_loop: Rigby light SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-02 via arc pin `pa-e7fbacc996b34b44` (Chris ratified "agree all + SIGN" at S1700 open). 4 pressure-test questions batched in single turn (no pin instability observed; D48 preemptive stability-probe gate 17th arm HOLDING CLEAN through parent SIGN). Verdicts: Q1 CONFIRM High (parent-vs-single verdict) / Q2(i) CONFIRM Medium-High + F1 fold (Cat C write-path boundary sentence) / Q2(ii) FLAG-EDIT Medium + F2 fold (Cat F sub-slots F.a-F.e with stop conditions) / Q2(iii) FLAG-EDIT Medium + F3 fold (Cat B/Cat D accounting rule for LLM-in-tool calls) / Q3(i) CONFIRM High (P1-P6 ordering) / Q3(ii) MUST-FIX High + F4 fold (P5 dependency clause P1+P3+P4 → P1+P2+P3+P4 for mission-scoped LLM-cost aggregation) / Q3(iii) CONFIRM Medium-High (P6 Cat F last) / Q4 MUST-FIX High + F5 fold (§5 Correlation primitives working-definitions box with 5 HYPOTHESIS-TO-BE-VERIFIED primitives: task_id/execution_id/trace_id/tool_call_id/mission_id) + F6 fold (3 anti-scope items 19/20/21 added: Frontend/WebSocket telemetry + Auth token/OAuth telemetry + RigbyTelemetry new-layer buildout). F1-F6 folds all landed pre-commit. Three "do not regress" notes for PR: (i) preserve §5 P1→P2→P3→P4→P5→P6 sequence + explicit F4 P5 dependency-on-P2 clause + F5 Correlation primitives box; (ii) preserve §8 D71 delegation-boundary framing (Group 1900 handoff explicit, not implicit); (iii) preserve Cat C boundary-rule F1 write-path sentence (P3 identifies canonical + deprecation ADR out-of-scope). No landmines beyond F1-F6 catalog (parent verifier-loop pre-flagged 3-class AgentExecution landmine already caught). SIGN pin = arc pin (parent stage per S1600 precedent); arc pin `pa-e7fbacc996b34b44` continues in service for downstream child audits.
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/topics/celery-workers.md
  - docs/topics/agent-system.md
---

# Session 1700 — Observability / Telemetry / SLOs Domain Taxonomy Proposal (Phase 0)

> **What this doc is.** A scoping deliverable produced *before* any
> Observability domain audit begins. Chris typed the short command
> "Start research group 1700" at S1700 open — the D-launch verdict
> per playbook §22 next-arc queue default (Group 1600 closed at
> S1699) + OS §12.3 "Start Group NNNN: Observability" target
> pattern. This doc opens the arc by (a) recording the six proposed
> Chris-ratified verdicts D69-D74 (pending Rigby optional light SIGN
> pressure-test), (b) demonstrating from verified runtime evidence
> that Observability / Telemetry / SLOs is larger than any single
> telemetry-layer view captures — a **5-parallel-execution-telemetry-
> layer surface** (`CeleryTaskEvent` + `LLMCallEvent` + `AgentExecution`
> + `ToolCallRecord` + `OpsRunEvent`) + adjacent Body Systems health
> telemetry (`HeartBeat` + 9-body-system scan) + ad-hoc SLO framework
> (single `check_learning_loop_slo` task, no meta-framework) + Ops
> Autopilot diagnostic consumer layer + 14+ event-shaped adjacent
> models (`DeliverableEvent` + `ImpactEvent` + `EngagementEvent` +
> `TriggerEvent` + `FleetEvent` + others per `EVENT_SYSTEM_INVENTORY.md`)
> with cross-cutting concerns (Rigby v0 intake DISABLED
> `RIGBY_EVENT_INTAKE_ENABLED=False`, monitor-task overhead spiral
> risk, doc-claim verifier drift as meta-observability signal),
> (c) proposing a candidate subdomain taxonomy Chris can inspect and
> edit, and (d) framing the load-bearing dedup question — "are the 5
> execution-telemetry layers structurally separable (each owns a
> distinct concern), or do they need canonical unification (single
> execution_id + trace_id spine spanning task→LLM→agent→tool→ops)?"
> — as the arc's lens question with **posture-decision framing +
> evidence plan** as the deliverable owed to xx99, NOT posture
> recommendation (analog D59/D65 refinement anticipated pre-lock).
>
> **What this doc is not.** The audit itself. A design proposal. A
> recommendation about *how* the observability layers should
> restructure. Not a posture selection between unification-canonical
> and structural-separability — that decision is Chris-gated per
> D74-analog and requires child evidence sweeps that have not yet
> run. Not an event bus design (delegated to Group 1900 per D2
> ratification). Not an SLO framework design (Group 1700 audits what
> exists; framework design is a follow-on design-preparation arc if
> Chris ratifies at xx99). Every claim below cites either an
> existing research doc (S1273 / S1274 / S1300 / S1399 / S1400 /
> S1499 / S1500 / S1599 / S1600 / S1699) or a verified file:line at
> the current `main` HEAD (`2b7dbd89`).

---

## 1. Why Phase 0

The Group 1600 Content / Deliverables / Publishing arc closed at
S1699 as the **fourth successful parent-with-children application**
(following Group 1300 Memory closed at S1399 + Group 1400 Revenue
closed at S1499 + Group 1500 Sports/DBAO/Intelligence closed at
S1599). All four prior arcs opened with Phase 0 scoping doctrine:
Group 1300 established the pattern (S1300 parent scoping → 5-child
arc → S1399 canonical summary); Group 1400 refined it by applying
Chris's Phase 0 F.i/F.ii/F.iii 3-step methodology (D29 Chris-locked
at S1400 open) as a first empirical application proposed for
playbook v3 §11.1 template addition on the two-triggers rule;
Group 1500 applied it unchanged as the second trigger per D58;
S1599 §12.4 discriminative-value criterion check **satisfied all 4
evidence types** (Scope confusion prevented via D60 + Rework
reduced via §11.4 F.ii boundary + Cleaner arc close via 6-of-6
SIGN-with-edits + Chris-lock efficiency via single agree-all round
D56-D61) → **playbook v3 §11.1 template promotion TRIGGERS** per
Rigby SIGN cycle 1 Q7 fold; Group 1600 was the **third application**
and adopted D62 = (a) 6-sibling exemplar mini-schema
propagation-upfront pattern per S1599 §10.2 codify-ready candidate;
S1699 §10 fourth-application meta-methodology **CONFIRMS
F.i/F.ii/F.iii durable at fourth-application** with F6 fold
third-application tightening satisfied. **Group 1700 is the fourth
application of the methodology** and continues the same shape
without modification, plus inherits S1699 §10.2 seven
codify-ready-for-playbook-v3 candidates (D48 stability-probe gate +
D62 6-of-6 sequence + F2-fold rubric + F1 during-SIGN grep + cross-
arc CORRECTION propagation + F9 binary posture framing + F10
dependency-clauses).

The playbook §22 domain queue row for Group 1700 is verbatim:

> **1700** | Observability / Telemetry / SLOs | §3.25 | DEEP |
> **5-layer telemetry dedup audit named by S1273 §5.13 + S1274 §12.6**

The OS §12.3 "Start Group NNNN" target block explicitly names
Observability as the exemplar arc-open command with 6-child
suggested sequence (P1 CeleryTaskEvent, P2 LLMCallEvent, P3
AgentExecution, P4 ToolCallRecord, P5 OpsRunEvent, P6 Event vs
Observability separation, S1799 summary). Group 1700 §5 proposes
this sequence with one modification (see §5 for detail): P6 is
scoped as **Adjacent / Separation** rather than only "Event vs
Observability separation" — it also covers HeartBeat + Body Systems
telemetry, SLO framework audit, and terminology clarification
between "Observability" and "Event System." The Event Architecture
scope proper (event bus adoption, cross-domain event routing,
schema versioning) is **delegated to Group 1900 per D2
ratification** at S1700 open.

Phase 0 exists because a "Group 1700 = Observability" invocation
without decomposition would collide with three failure modes:

1. **Scope-confusion between execution-telemetry and event-
   architecture.** S1273 §3.25 catalogs Observability entry points
   including CeleryTaskEvent + LLMCallEvent + OpsRunEvent +
   AgentExecution + HeartBeat + 14+ event-shaped models. Without
   an explicit boundary rule, an auditor would collapse "event
   models" (routing/pub-sub concerns) with "execution telemetry"
   (audit trail concerns). D2 ratification bounds the event-bus
   scope OUT.

2. **AgentExecution model duplication landmine.** Three
   `class AgentExecution` definitions exist at HEAD (2b7dbd89):
   `intelligence/models/agent_execution.py:11` (ActionPlan-scoped),
   `intelligence/models.py:587` (duplicate class body, same fields,
   ActionPlan-scoped), `core/models_unified_system.py:882`
   (DEPRECATED per docstring — points at `agents.models` which is
   now a compatibility shim). Any Phase-1 "AgentExecution audit"
   that lands without a category-scope statement would inherit
   this landmine mid-child.

3. **Rigby v0 intake disabled today.** S1273 line 1959 flags
   `RIGBY_EVENT_INTAKE_ENABLED=False` — the observability
   infrastructure exists but Rigby doesn't consume it. Without
   Phase 0 scope, "wire Rigby to intake" could scope-magnet the
   whole arc into a Rigby integration project rather than a
   telemetry-layer audit.

Phase 0 records these framings before child work starts.

---

## 2. What existing inventory already tells us

Per playbook §7 cross-reference policy, this section CITES prior
research and connects each citation to Group 1700's evidence-plan
input — it does NOT duplicate content. Each subsection is one
one-line citation + verbatim excerpt (where load-bearing) +
"concrete Observability evidence-plan input" paragraph.

### 2.1 S1273 §3.25 Observability row (`platform_architecture_inventory.md`)

Verbatim citation:

> **§3.25 Observability / Telemetry / SLOs — DEEP coverage tier.**
> 4–5 parallel execution telemetry layers exist; no dedup audit.
> HeartBeat collection never exported — no dashboard/alerting.
> HeartBeat cold-start issue: digestive + muscular report
> sluggish/paralyzed on fresh DB. SLO check not systemic — one
> task-specific check; no meta-SLO framework. Observability
> deduplication needed.

**Concrete Observability evidence-plan input.** This row is the
canonical arc rationale. It names four load-bearing observations:
(a) 4–5 parallel execution telemetry layers with no dedup audit
(→ P1 through P5 child scope); (b) HeartBeat export gap (→ P6
scope); (c) HeartBeat cold-start correctness issue (→ P6 scope +
handoff to Employee OS if body-systems reliability is the actual
scope owner); (d) SLO framework absence (→ P6 audit + follow-on
design-preparation arc if Chris ratifies). The DEEP coverage tier
means S1273 already produced detailed evidence — Group 1700 does
not need to re-inventory; it needs to dedup + rationalize.

### 2.2 S1274 §11.6 5-layer execution-telemetry dedup (`cross_domain_integration_audit.md`)

The mission naming for Group 1700 traces to S1274 §11.6 and S1273
§5.13. Both name "5-layer execution telemetry" as the arc scope.
Load-bearing evidence:

> A single agent-tool-LLM execution path fires 5 telemetry writes
> (CeleryTaskEvent → LLMCallEvent → AgentExecution → ToolCallRecord
> → OpsRunEvent). No canonical `execution_id` / `trace_id` spans
> all 5. Correlation is best-effort per-layer. Deduplication
> rationale + unification proposal owed to Observability arc.

**Concrete Observability evidence-plan input.** This is the
load-bearing dedup question. The xx99 canonical summary at S1799
owes evidence for whether the 5 layers can be structurally
separated (each owns a distinct concern; correlation is
lightweight FK) OR need canonical unification (single execution_id
+ trace_id spine with unified write path). This is the D74-analog
posture question framed in §8 D74 — Group 1700 gathers evidence
per child audit; xx99 consolidates; Chris ratifies posture post-arc.

### 2.3 S1300 Memory arc (closed S1399) — learning-loop telemetry writer

S1399 canonical summary §7 anchor-updates named the learning-loop
path as delegates_to Memory arc. Group 1600 xx99 §7 inherited this
delegation. Group 1700 inherits it further: **AgentMemory /
UserAgentLearning / AgentKnowledgeSource** write-side telemetry
lives in the observability domain even though the learning-loop
business logic is Memory domain scope.

**Concrete Observability evidence-plan input.** P3 AgentExecution
audit should include a scope statement: "AgentExecution captures
agent intent/outcome; the AgentLearningService.record_interaction()
write pathway (Session 991) is a telemetry sink — does it correlate
to AgentExecution via execution_id, or is it a parallel write
pathway with its own correlation contract?" Answer bounds cross-arc
handoff to Group 1300 Memory (already closed).

### 2.4 S1400 Revenue arc (closed S1499) — outreach delivery telemetry gap

S1402 F.B1 outreach delivery MISSING was arc headline finding: 6/6
Revenue lifecycle stages had missing runtime-owners; outreach
delivery specifically had zero outbound channel wired. Group 1600
Content arc extended this pattern via S1699 §7.4 auto_publish "daily
6 AM" cross-arc CORRECTION propagation.

**Concrete Observability evidence-plan input.** `EngagementEvent`
(defined, unverified writers per S1273 line 1916) may be the
observability sink where a Revenue outreach delivery is *supposed*
to write when delivery completes. If EngagementEvent has no
producers OR no consumers, that's a producer-observability gap
that Group 1700 should catalog. P3 AgentExecution and P4
ToolCallRecord audits will surface whether Revenue-owned agents
(OutreachAgent, EngagementAgent) actually write anything to
EngagementEvent.

### 2.5 S1500 Sports arc (closed S1599) — SportsBettingBrief WRITE-ONLY-FORGOTTEN pattern

S1504 §14.3 named the "WRITE-ONLY-FORGOTTEN" observability
antipattern: 2 producers, 0 consumers. This is a canonical example
of observability drift — telemetry writes to a model but nothing
reads it.

**Concrete Observability evidence-plan input.** P6 Adjacent /
Separation audit should include a first-class scope item:
"WRITE-ONLY-FORGOTTEN pattern audit — how many event-shaped models
have producers but no consumers?" Candidates (from S1273 line 1912
"Defined, unverified writers"): CockpitIncidentEvent,
CockpitAutopilotEvent, EngagementEvent, ThreatEvent, ABTestEvent,
ConversionEvent, BadContextEvent, RelationshipEvent. Cross-check
each for producer/consumer wiring. This audit sits at the
observability↔event-architecture boundary; results inform Group
1900 evidence.

### 2.6 S1600 Content arc (closed S1699) — DeliverableEvent event-to-action gap

S1699 §7.4 catalog names DeliverableEvent as producer-side wired
but consumer-side ambiguous. S1273 line 2805 verbatim: "event-to-
action gap — DeliverableEvent rows written; [no clear consumers]."
Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E
owns the consumer-side disposition.

**Concrete Observability evidence-plan input.** P1-P5 child audits
should stay narrow to *execution telemetry* — the DeliverableEvent
producer-side telemetry contract belongs to Group 1700 (does the
producer write completely? does the write path fail silently?),
but the consumer-side wiring is Group 1600's T0/Gate. Boundary
rule: **Observability owns producer-side telemetry contract
completeness; domains own their consumer-side wiring decisions.**
This is a boundary that xx99 will reinforce.

### 2.7 `docs/topics/celery-workers.md` — monitor-task overhead spiral risk

Sessions 1167 (`capture_worker_memory_snapshot` every 5m) and 1169
(soft_time_limit / time_limit discipline; probe decomposition for
broker inspect and Redis BLPOP calls) documented that observability
tasks themselves can become the largest wall-clock consumer if
unbounded. Session 1167 tone verbatim: "monitor task at top of
wall-clock consumption = P1 reliability debt."

**Concrete Observability evidence-plan input.** P1 CeleryTaskEvent
child audit should include an **observability-of-observability**
scope statement: "Are the observability write pathways themselves
bounded by time limits? Do they produce their own retention
overhead? Do they crash silently under load?" This is a
meta-observability question that S1273 does not explicitly
inventory but is load-bearing for arc close-out.

### 2.8 `docs/topics/agent-system.md` — ToolCallRecord all-return-path fix precedent

Session 970 introduced automatic ToolCallRecord capture via
BaseAgent `__init_subclass__()`. Session 1115 fixed dispatcher to
write on all return paths (prior incomplete coverage). Session 1169
added agent_name dimension with best-effort fallback; backfill =
none, so pre-S1169 rows carry `agent_name=''` and don't surface in
by-agent views.

**Concrete Observability evidence-plan input.** P4 ToolCallRecord
audit should verify all 74 enabled agents write records on all
return paths at HEAD (regression check post-S1115). Also verify
whether managed-agent + orchestration-agent + PA-dispatch wrapper
call paths all write. Also catalog dimensions with retroactive-vs-
prospective coverage gaps (agent_name backfill=none is one
example).

### 2.9 S1699 §8 T-slots — cross-arc handoffs relevant to observability

Two T-slot items from S1699 §8 unified follow-on queue have
observability-domain touchpoints:

- **T1 #17 Cat E learning-loop bridge** — PA-tool feedback bridge
  writes to Memory arc; producer-side telemetry contract completeness
  is Group 1700 scope; Memory business logic is closed Group 1300.
- **T1 #18 unified event stream** — event schema/routing is Group
  1900 delegation, but "does event stream telemetry exist and is it
  consistent across producers" is Group 1700 scope.

**Concrete Observability evidence-plan input.** P6 Adjacent /
Separation child audit should reference these T-slots as evidence
that the observability↔event-architecture boundary is real and
already-mapped; the boundary rule from §2.6 applies.

### 2.10 `docs/PLATFORM_INVENTORY.md` — runtime counts anchor

Verified 2026-07-02 20:16:33 at git HEAD `f3fe1493`:

- **Body Systems:** 9 systems monitored by `run_all_systems_scan`
- **Celery Beat:** 92 enabled + 5 disabled = 97 PeriodicTask rows
- **Celery Tasks:** 415 user-defined
- **Discord:** 96 @*.command decorators
- **PA Tools:** 113 tool schemas + 156 registered handlers

**Concrete Observability evidence-plan input.** These are baseline
counts P1-P5 should verify their layer covers proportionally. If
CeleryTaskEvent covers 415 tasks × 92 beat schedules, and a P1
audit finds only 60% coverage in production event rows, that's the
kind of quantitative gap child audits should produce. Body Systems
9 = P6 in-scope. PA Tools 113/156 = P4 ToolCallRecord scope
verification target.

---

## 3. Candidate subdomain taxonomy

The taxonomy proposes six categories A–F. Each has a **boundary
rule** (one-sentence rule preventing scope-magnet bleed into
adjacent categories), **scope** (runtime file:line evidence
anchoring the category), **load-bearing question owed to xx99** (the
specific evidence plan the child audit gathers), and **cross-arc
references** (how this category informs or depends on other arcs).

### A — Task / Worker Execution Telemetry (`CeleryTaskEvent`)

- **Boundary rule.** Category A owns telemetry emitted by the
  Celery task lifecycle boundary (signal-handler-driven writes on
  prerun/postrun/failure). It does NOT own telemetry emitted from
  inside a task body (LLM call → Cat B; tool call → Cat D; agent
  execution → Cat C). The audit stops at the Celery signal
  handler boundary.

- **Scope.**
  - Model: `core/models_celery_telemetry.py` (`CeleryTaskEvent`)
  - Signal handlers: `core/celery_telemetry.py:74-177` (task_prerun /
    task_postrun / task_failure)
  - Consumers (PA tools): `status_snapshot_tool`, `system_health_tool`,
    `task_breakdown_tool`
  - Retention: `CELERY_TASK_EVENT_RETENTION_DAYS` (default 30 per
    Memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md`)
  - Baseline coverage: 415 user-defined Celery tasks + 92 enabled
    PeriodicTasks (`PLATFORM_INVENTORY.md`)

- **Load-bearing question owed to xx99.** Does CeleryTaskEvent
  cover **all** task states across all workers? Is the agent_name
  dimension (Session 1169) retroactively defensible or
  backfill-incomplete? What is the observed vs configured
  retention window at HEAD? What is the monitor-task overhead
  spiral risk (Session 1167 precedent)?

- **Cross-arc references.** Cross-check dedup contract with Cat B
  (does LLMCallEvent inherit execution_id from CeleryTaskEvent, or
  independent?), Cat C (does AgentExecution correlate to
  CeleryTaskEvent via task_id?), Cat E (does OpsRunEvent aggregate
  CeleryTaskEvent per mission?).

### B — LLM Call Telemetry (`LLMCallEvent`)

- **Boundary rule.** Category B owns telemetry emitted at the
  LLM request/response boundary via the S1098 llm_call_wrapper
  path. It does NOT own tool-call telemetry (that's Cat D) or
  agent-outcome telemetry (that's Cat C). The audit stops at the
  wrapper's post-call hook.

- **Scope.**
  - Model: `core/models_llm_telemetry.py:30-100` (`LLMCallEvent`)
  - Wrapper: `core/services/llm_call_wrapper.py` (Session 1098)
  - Fields: model, prompt_tokens, completion_tokens, total_tokens,
    latency_ms, cost, execution_id (correlation key), success,
    error
  - Providers covered: 6 (`LLMProviderRegistry`: OpenAI, Anthropic,
    Together AI, Ollama, DeepSeek, Gemini)

- **Load-bearing question owed to xx99.** What is the scope of
  execution_id? Does it span a full agent-tool-LLM sequence, or
  just a single LLM call? Does every LLM caller route through
  `llm_call_wrapper` (or are there rogue direct `Anthropic()` /
  `OpenAI()` invocations bypassing telemetry — cross-check
  Memory rules `feedback_anthropic_client_factory.md` +
  `feedback_openai_client_factory.md`)? Is cost accounting
  accurate (S1224 gpt-5 max_completion_tokens floor precedent)?

- **Cross-arc references.** Cross-check with Cat A dedup
  (execution_id ↔ task_id correlation contract), Cat C (does
  AgentExecution.llm_call_count match LLMCallEvent count per
  agent per execution?), Cat D (tool calls sometimes invoke LLM
  internally — those are NOT double-counted per accounting rule
  below).

- **Accounting rule (Cat B / Cat D boundary, per Rigby SIGN
  cycle 1 F3 fold).** LLM calls made from inside a tool
  invocation remain **Cat B**, regardless of caller (agent-direct
  vs tool-internal). **Cat D never attempts to "own" LLM cost or
  token accounting** — Cat D counts tool invocations only, and
  dedup between Cat B and Cat D is performed via correlation
  keys (execution_id + trace_id + tool_call_id), not by
  redefining ownership. This resolves the LLM-in-tool
  double-count risk via measurement semantics rather than
  boundary rule alone.

### C — Agent Execution Telemetry (`AgentExecution`)

- **Boundary rule.** Category C owns telemetry emitted at the
  agent `route()` boundary — agent-level intent (what task
  requested?) and outcome (success/failure/result). It does NOT
  own per-tool audit (Cat D) or per-LLM-call (Cat B) — those are
  child-level details inside agent execution. The audit stops at
  the wrapper's post-route hook. **P3 MUST identify the actual
  write path(s) and canonical table/class used at runtime at HEAD
  (which of the 3 `AgentExecution` classes is written to by
  BaseAgent's `route()` wrapper, and via which import path); ADR
  to remove/merge the deprecated 2 is explicitly out-of-scope for
  P3 and belongs to post-arc T-slot (per §6.3 parked candidate).**
  This distinguishes "P3 catalogs + names canonical + defines
  correlation contract" (in-scope) from "P3 designs the
  deprecation" (out-of-scope) per Rigby SIGN cycle 1 F1 fold.

- **Scope (with landmine).**
  - **THREE classes named `AgentExecution` exist at HEAD 2b7dbd89:**
    - `intelligence/models/agent_execution.py:11` — ActionPlan-scoped,
      canonical per Session 1273 §3.25 mention
    - `intelligence/models.py:587` — duplicate class body, same
      fields, ActionPlan-scoped (likely legacy import re-export
      OR true duplicate — child audit determines)
    - `core/models_unified_system.py:882` — **DEPRECATED per
      docstring** ("Use agents.models.AgentExecution instead. This
      model is deprecated as of Session 287"), tied to
      `UnifiedAgentTemplate` + Agent FK + trace_id + experiment.
      Docstring points at `agents.models` — but that is now a
      compatibility shim (`agents/models.py` Session 391 comment:
      "These models have been migrated to
      `core/models/agents_registry/`") — and no `AgentExecution`
      class exists in the target path. **Deprecation notice is
      stale/wrong at HEAD.**
  - Wrappers: `core/agent_execution_wrapper.py` +
    `core/services/execution_tracker.py`
  - Baseline: 83 AGENT_MAP agents (74 enabled + 9 rerouted); 90
    Agent DB rows (`PLATFORM_INVENTORY.md`)

- **Load-bearing question owed to xx99.** Which of the 3
  `AgentExecution` classes is the actual canonical audit trail at
  HEAD? Which of the 3 does BaseAgent's `route()` wrapper write to?
  What is the correlation between them (FK / trace_id / none)? Is
  the S287 deprecation stale (i.e., all callers already migrated),
  a live orphan, or masking a migration incomplete? Is the S843
  trace_id field usable as the canonical arc-wide correlation
  spine?

- **Cross-arc references.** This category's landmine is
  **scope-magnet** risk: if P3 audit expands to fully deprecate
  and remove 2 of 3 classes, that becomes a design-preparation +
  implementation project. **Boundary discipline:** P3 catalogs
  the 3 classes + names canonical + defines the correlation
  contract; deprecation ADR is post-arc T-slot.

### D — Tool Call Telemetry (`ToolCallRecord`)

- **Boundary rule.** Category D owns telemetry emitted at the
  per-tool-call boundary inside agent execution (Session 970
  BaseAgent `__init_subclass__()` wrapper; Session 1115
  all-return-path fix). It does NOT own the tool schema/registry
  (that's PA tool surface concern) or the agent-level outcome
  (Cat C). The audit stops at the tool-call wrapper.

- **Scope.**
  - Model: `core/models_tool_calls.py:19` (`ToolCallRecord`)
  - Auto-wrap mechanism: `BaseAgent.__init_subclass__()` (S970)
  - Coverage fix: dispatcher writes on all return paths (S1115)
  - Baseline: 113 PA tool schemas + 156 registered handlers
    (`PLATFORM_INVENTORY.md`); 74 enabled AGENT_MAP agents that
    inherit BaseAgent

- **Load-bearing question owed to xx99.** Do all 74 enabled
  agents actually write ToolCallRecord on all tool calls at HEAD?
  Does the managed-agent path write? The orchestration-agent
  path? The PA-dispatch path (PA tools invoked via
  `unified_pa_entrypoint`)? Are there wrapped-tool call sites
  (delegation between agents) that skip the wrapper? Does the
  wrapper survive tool-call retries (per-retry write or one row
  per logical call)?

- **Cross-arc references.** Cross-check with Cat C (per-agent
  execution ↔ tool call correlation via execution_id or
  AgentExecution FK), Cat B (LLM calls invoked by tools —
  double-counted risk with Cat B), Cat E (OpsRun-scoped mission
  tools).

### E — Ops / Mission Telemetry (`OpsRun` + `OpsRunEvent`)

- **Boundary rule.** Category E owns telemetry at the Ops /
  Mission orchestration boundary — MissionRunner (Employee OS) +
  Ops Autopilot pipelines. It does NOT own the mission business
  logic (that's Employee OS scope) or the per-agent/per-tool
  detail (Cats C/D). The audit stops at the OpsRun / OpsRunEvent
  writer boundary.

- **Scope.**
  - Models: `core/models_ops_runs.py:11-117` (`OpsRun` +
    `OpsRunEvent`), `domain` enum = {ops, mission}
  - Writer: `core/tasks_ops.py` (introduced S1250 PR3)
  - Related: `core/employees/mission_runner.py` (Employee OS
    orchestrator; per CLAUDE.md "no separate MissionRun model —
    uses `OpsRun(domain='mission')` + `OpsRunEvent` audit rows")
  - Consumer: DiagnosticPipelineService (CTO daily / COO daily /
    Trend Analysis daily) at `core/services/ops_autopilot/`

- **Load-bearing question owed to xx99.** How does OpsRunEvent
  correlate to the 4 prior layers (CeleryTaskEvent, LLMCallEvent,
  AgentExecution, ToolCallRecord)? Is OpsRunEvent a **producer**
  (introducing its own event contract) or a **consumer** (writing
  aggregate outcome from prior-layer events)? Does MissionRunner
  actually write OpsRun rows at HEAD (Employee OS integration
  reality check)? Are there orphan OpsRun rows (missions started
  but no MissionRunner integration)?

- **Cross-arc references.** Employee OS concurrent (not a
  separate arc) — MissionRunner + AIEmployee + JobContract own
  the mission execution; Group 1700 audits the observability
  trail. If P5 discovers OpsRunEvent has "0 consumers" pattern
  (WRITE-ONLY-FORGOTTEN mirror), that's a cross-arc handoff to
  Employee OS + Group 1900 event-bus scope.

### F — Adjacent / Separation Boundaries

- **Boundary rule.** Category F owns everything observability-
  adjacent that is NOT one of the 5 execution-telemetry layers.
  **Cat F is internally sub-slotted per Rigby SIGN cycle 1 F2
  fold to prevent internal scope-magnet within the child audit:**

  - **F.a — Body Systems / HeartBeat.** `HeartBeat` model +
    BodyVitalsService + 9-body-system health scan. **Stop
    condition:** catalog export gap + cold-start correctness
    issue (S1273 lines 1964-1965); do NOT design the export
    pipeline or fix cold-start — both are Employee OS or a
    dedicated body-systems reliability project (per §6.4 + §6.5
    parked candidates).
  - **F.b — SLO framework audit.** Single ad-hoc
    `check_learning_loop_slo` task at `core/tasks.py:12492` (S1273
    line 1969). **Stop condition:** catalog what SLO coverage
    exists today (single task; no meta-framework); do NOT design
    the systemic SLO framework — that's a follow-on
    design-preparation arc if Chris ratifies at xx99 (per §6.1
    parked candidate).
  - **F.c — Event-model catalog + WRITE-ONLY-FORGOTTEN audit.**
    14+ event-shaped models from S1273 lines 1912-1917
    (DeliverableEvent + ImpactEvent + EngagementEvent +
    TriggerEvent + FleetEvent + CockpitIncidentEvent +
    CockpitAutopilotEvent + ThreatEvent + ABTestEvent +
    ConversionEvent + BadContextEvent + RelationshipEvent +
    AuditLog + NotificationLog). **Stop condition:** catalog
    producer/consumer wiring per model; do NOT act on
    deprecation decisions — those are Group 1900 Event
    Architecture territory (per §6.6 parked candidate).
  - **F.d — Doc-claim verifier drift as meta-observability
    signal.** `core/services/doc_claim_verification.py` +
    `verify_doc_claims` command. **Stop condition:** catalog
    whether verifier drift is a telemetry-worthy signal; do NOT
    integrate verifier drift into observability infrastructure
    or fix any verifier bugs (per §6.7 parked candidate + §7 item
    15 anti-scope).
  - **F.e — Observability↔Event-Architecture terminology
    boundary.** Clarify where "Observability" ends and "Event
    System" (EVENT_SYSTEM_INVENTORY.md) begins. **Stop
    condition:** produce a terminology recommendation for xx99
    §5 posture-decision brief; do NOT rename subsystems or
    refactor terminology at HEAD.

  Cat F does NOT own event bus routing/design (Group 1900
  delegation) or the internal correctness of adjacent-domain
  business logic. Rigby SIGN Q2(ii) FLAG-EDIT verdict: sub-slots
  keep Cat F as cross-cutting bin without promoting to Cat G/H,
  while preventing sprawl per stop conditions.

- **Scope.**
  - HeartBeat: `core/models_heart.py:HeartBeat` (via `core/services/heart.py`)
  - BodyVitalsService: `core/services/body_vitals.py:run_all_systems_scan`
    (every 10m via `run_heartbeat` task; 9 body systems per
    `PLATFORM_INVENTORY.md`)
  - Known drift: HeartBeat "collection never exported — no
    dashboard/alerting"; digestive + muscular "sluggish/paralyzed
    on fresh DB" cold-start (S1273 lines 1964-1965)
  - SLO: `core/tasks.py:12492:check_learning_loop_slo` (daily 9
    AM; usage_rate ≥ 5% over 24h; single ad-hoc check; no
    meta-framework — S1273 line 1969)
  - Doc-claim verifier: `core/services/doc_claim_verification.py`
    + `verify_doc_claims` management command (per CLAUDE.md
    "regenerable" doc lifecycle)
  - Event-shaped model catalog: 14+ models per S1273 lines
    1912-1917 (`DeliverableEvent`, `ImpactEvent`,
    `EngagementEvent`, `TriggerEvent`, `FleetEvent`,
    `CockpitIncidentEvent`, `CockpitAutopilotEvent`,
    `ThreatEvent`, `ABTestEvent`, `ConversionEvent`,
    `BadContextEvent`, `RelationshipEvent`, `AuditLog`,
    `NotificationLog`)

- **Load-bearing question owed to xx99.** For each adjacent
  concern (Body Systems / SLO / meta-observability / event-model
  catalog): should it be canonically part of Observability
  domain, or delegated to another domain (Employee OS for Body
  Systems health? Group 1900 for event-model catalog? follow-on
  design-preparation arc for SLO framework?)? Where is the
  "Observability vs Event System" terminology boundary — S1273
  §3.25 uses "Observability / Telemetry / SLOs" but
  EVENT_SYSTEM_INVENTORY.md lists 14+ event models — is this a
  named-terminology drift or an actual scope boundary?

- **Cross-arc references.** This category is the **cross-cutting
  category** — it inherits framings from Groups 1200 (Employee
  OS), 1300 (Memory), 1600 (Content — DeliverableEvent), 1900
  (Event Architecture — upcoming). Its evidence feeds Group 1900
  parent scoping when that arc opens.

### Explicit non-candidates (bounded OUT)

The following are NOT proposed subdomain categories. Each has
one-sentence rationale.

1. **Event bus / pub-sub / routing** — delegated to Group 1900
   Event Architecture per D2 ratification at S1700 open. Group
   1700 audits execution telemetry writer boundaries; Group 1900
   owns event flow contracts.

2. **Rigby v0 event intake activation** —
   `RIGBY_EVENT_INTAKE_ENABLED=False` today; Group 1700 catalogs
   the gap; wiring Rigby is a downstream implementation project
   post-xx99 if Chris ratifies.

3. **Discord broadcast telemetry internals** — Discord
   integration observability is bounded to "does the broadcast
   task write ToolCallRecord?" (Cat D scope). Broadcast latency /
   Discord API health is Discord subsystem responsibility.

4. **DeliverableEvent consumer contract** — Group 1600 T0/Gate
   R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E owns. Group 1700
   audits producer-side telemetry completeness only.

5. **Memory learning-loop business logic** — Group 1300 Memory
   arc closed at S1399. Group 1700 audits Memory-writer
   telemetry contract completeness (does the writer actually
   write); Memory internal correctness is not in scope.

6. **Content Deliberation pipeline retries** — Content
   observability is Group 1600 T-slot territory. Group 1700
   audits generic Celery/agent/tool telemetry that Content uses,
   not Content-specific retry pathways.

7. **Sports betting outcome telemetry** — Group 1500 arc closed
   at S1599. Group 1700 audits generic telemetry infrastructure
   Sports uses; sports-specific pattern types (P11
   SignalCluster gap COMPLETED per Group 1500 findings) are not
   re-audited.

8. **SLO framework DESIGN** — Group 1700 audits what SLO
   coverage exists today (single ad-hoc task); framework design
   is a follow-on design-preparation arc if Chris ratifies at
   xx99.

9. **BaseAgent refactor** — BaseAgent is 5,575 lines and hosts
   ToolCallRecord auto-wrap. Group 1700 audits the wrapper
   contract; refactor of BaseAgent is out of scope.

10. **PA tool surface unification** — Group 1600 Cat E anchor
    LOCKED per S1605 F9 (Rigby PA-tool tactical-split). Group
    1700 audits ToolCallRecord coverage of PA tool dispatch;
    tool surface unification is Content T-slot territory.

11. **AI provider selection / cost optimization** — Cat B
    audits LLMCallEvent completeness including cost accounting;
    provider selection (OpenAI vs Anthropic vs Together AI vs
    Ollama vs DeepSeek vs Gemini) is product decision.

12. **Body Systems cold-start reliability fix** — Cat F catalogs
    the drift (S1273 line 1964); the fix belongs to Employee OS
    or a Body-Systems-focused reliability arc.

13. **Celery worker Procfile queue design** — Cat A audits
    CeleryTaskEvent per-queue coverage; queue routing design is
    infrastructure concern.

14. **Fleet application observability** — Cross-repo fleet apps
    (character-os + infra + others per Memory rule
    `feedback_fleet_caller_verification_before_celery_deletes.md`)
    have their own telemetry. Group 1700 scope is
    unified-donkey-betz only.

15. **Historical arc T-slot inheritance** — Group 1400/1500/1600
    post-arc §7 anchor-update queues and T1 CRITICAL remediation
    queues stay in their owning arcs' backlogs.

16. **Doc-claim verifier fix pass** — Cat F catalogs verifier
    drift as meta-observability signal; verifier bug fixes belong
    to the doc-claim verifier's own PR track.

17. **Governance Ratification Ledger observability** — Governance
    decision audit trail (per CLAUDE.md `docs/governance_redesign.md`)
    is a separate observability sub-question if it surfaces at
    xx99; not a P1-P6 candidate.

18. **Rigby SIGN worker-instability D48 pattern investigation** —
    Meta-methodology finding tracked in `feedback_rigby_sign_worker_
    instability_recovery.md`; belongs to research OS meta layer,
    not observability domain.

---

## 4. Parent-vs-single recommendation

**Verdict: PARENT-WITH-CHILDREN.**

Four evidence bullets per playbook §2 STAGE 0 verdict procedure:

1. **Multi-substrate domain (STAGE 0 criterion 1 + 2).** S1273
   §3.25 catalogs Observability as 1 row in the 32-domain map, but
   the row contains 5 parallel execution-telemetry model layers +
   HeartBeat + SLO check + 14+ event-shaped adjacent models +
   Ops Autopilot diagnostic consumer + doc-claim verifier drift
   signal. Single-audit shape cannot produce independent evidence
   for each substrate; correlation contract questions require
   per-layer evidence gathering. Multi-substrate + explicit
   §5.13 dedup naming triggers criterion 2.

2. **Runtime surface inventory exceeds single-audit capacity.**
   Baseline counts: 415 user-defined Celery tasks + 92 enabled
   PeriodicTasks (Cat A scope) + 6 LLM providers × unbounded
   call sites (Cat B scope) + 74 enabled AGENT_MAP agents +
   3 AgentExecution classes (Cat C scope with landmine) + 113 PA
   tool schemas × 156 handlers × 74 agents (Cat D scope) +
   OpsRun+OpsRunEvent + MissionRunner integration (Cat E scope)
   + 9 body systems + SLO framework + 14+ event models (Cat F
   scope). No single 3–6 hour audit session can produce 120+
   evidence anchors per playbook §17 across this surface.

3. **Load-bearing dedup question requires evidence from all
   children (STAGE 0 criterion 4).** The D74-analog question
   ("are the 5 execution-telemetry layers structurally separable
   or do they need canonical unification?") requires evidence
   from each of Cat A/B/C/D/E individually before xx99 can
   synthesize. A single audit would collapse layer-specific
   evidence and force premature posture recommendation.

4. **Cross-arc handoffs owe evidence per child.** Group 1900
   Event Architecture inherits evidence about producer-side
   telemetry contracts (Cat F WRITE-ONLY-FORGOTTEN catalog +
   Cat A dedup rationale). Employee OS inherits evidence about
   OpsRunEvent integration reality (Cat E). Groups 1300/1400/
   1500/1600 (all closed) inherit backlog items only if xx99
   surfaces novel observability drift in their domains. Per-arc
   handoff owed evidence must be produced by the respective
   child audits.

**Alternative rejected: single-audit-then-defer.** A "single Cat A
audit covering only CeleryTaskEvent, defer the rest to follow-on
arcs" pattern fails the load-bearing dedup question (§2.2 above)
because dedup rationale requires all 5 layers to be inventoried
before the correlation contract can be evaluated. Per S1273 §5.13
explicit naming, the arc scope IS the 5-layer dedup — deferring 4
of 5 layers is scope-abandonment.

---

## 5. Child mission sequence

Six children P1–P6 + P7 canonical summary, sequenced with
explicit dependency clauses per playbook §14 F10 fold. Table
format matches S1600 §5 shape.

### Correlation primitives (working definitions — HYPOTHESIS-TO-BE-VERIFIED)

**Added per Rigby SIGN cycle 1 F5 MUST-FIX fold.** The single
most poisoning ambiguity for the arc is **execution_id scope**:
does it span a full task→LLM→agent→tool→ops sequence, or just a
single LLM call? If the answer is "just a single LLM call," the
proposed sequencing produces incompatible correlation
conclusions across children. This subsection names the working
definitions so each child audit begins with the same starting
premise; each definition is labeled **HYPOTHESIS** and must be
verified/refined by the named child audit.

| Primitive | Working definition (HYPOTHESIS) | Verify at |
|-----------|--------------------------------|-----------|
| **`task_id`** | Celery task UUID assigned at task-dispatch time by Celery core. One `task_id` per Celery task invocation. Written by CeleryTaskEvent signal handlers (Cat A). | P1 verifies coverage completeness + retention. |
| **`execution_id`** | Cross-layer correlation key intended to span a full agent-tool-LLM sequence. Written by LLMCallEvent (`core/services/llm_call_wrapper.py`, Session 1098) as an FK-like column. **HYPOTHESIS:** execution_id is intended to span the full task→LLM→agent→tool sequence, but the scope may be narrower today (single LLM call only). | P2 verifies actual scope + writer contract; P3 verifies AgentExecution↔execution_id correlation; P4 verifies ToolCallRecord↔execution_id correlation. |
| **`trace_id`** | S843 field on the DEPRECATED `AgentExecution` at `core/models_unified_system.py:882` per docstring — "Trace ID linking this execution to a broader workflow." **HYPOTHESIS:** trace_id was intended as the arc-wide correlation spine but may be unused at HEAD because the class it lives on is deprecated (per Cat C landmine catalog); the canonical `AgentExecution` at `intelligence/models/agent_execution.py:11` does NOT carry trace_id. | P3 verifies whether trace_id is written by any live path or is dead code. |
| **`tool_call_id`** | Per-tool-call unique identifier inside ToolCallRecord (`core/models_tool_calls.py:19`). **HYPOTHESIS:** tool_call_id is scoped to a single tool invocation; correlation to LLMCallEvent (when the tool internally calls an LLM) is via a shared execution_id or by tool_call_id being included as FK-like column on LLMCallEvent. | P4 verifies whether ToolCallRecord↔LLMCallEvent correlation exists; if absent, this is a debt item for xx99 §5 posture-decision brief. |
| **`mission_id`** | OpsRun / OpsRunEvent primary identifier at `core/models_ops_runs.py:11-117` (S1250 PR3). **HYPOTHESIS:** mission_id is Ops-scope correlation, NOT cross-layer — MissionRunner writes OpsRun rows but doesn't necessarily propagate execution_id / task_id / trace_id from prior 4 layers. | P5 verifies whether OpsRunEvent is a producer (independent event contract) or consumer (aggregates prior 4 layers via correlation keys). |

**Load-bearing rule for xx99 §5 posture-decision brief.** If P1
+ P2 discover execution_id is scope-single-LLM-call at HEAD, the
D74 "structural separability vs canonical unification" posture
decision resolves in favor of **canonical unification** (a
single execution_id + trace_id spine must be designed to make
5-layer trace queryable). If P1 + P2 discover execution_id
already spans agent-tool-LLM sequences at HEAD, structural
separability remains viable — the dedup rationale becomes
lightweight-FK cleanup, not spine redesign. **xx99 does NOT
select the posture; the correlation-primitive evidence gathered
by P1-P5 goes into the §5 evidence brief for Chris-gated ADR
post-arc.**

### P1–P7 sequence table

| Slot | Session | Category | Subdomain | Rationale + dependency clause |
|------|---------|----------|-----------|-------------------------------|
| **P1** | S1701 | **A** | Task / Worker Execution Telemetry (`CeleryTaskEvent`) | **First child, no dependencies inbound.** CeleryTaskEvent is the foundational execution boundary — every agent task fires as a Celery task, so P1 establishes the baseline coverage question (415 tasks × 92 beat schedules × observed event rate) and the retention/agent-name-dimension canonical answer. P2-P5 all inherit "does layer N inherit execution_id from CeleryTaskEvent?" so P1 must land the correlation-contract framing first. Additionally: P1 answers the observability-of-observability meta question (monitor-task overhead spiral risk per §2.7). |
| **P2** | S1702 | **B** | LLM Call Telemetry (`LLMCallEvent`) | **Depends on P1 execution_id contract.** P2 must answer "does every LLM call route through `llm_call_wrapper`, and does its execution_id correlate to P1's task_id?" — without P1 landing the correlation contract, P2 cannot evaluate coverage completeness. P2 also independently audits cost accounting (S1224 gpt-5 floor precedent), rogue-caller detection (Anthropic/OpenAI factory rules per Memory), and 6-provider coverage symmetry. |
| **P3** | S1703 | **C** | Agent Execution Telemetry (`AgentExecution`) | **Depends on P1 + P2.** AgentExecution bundles task-level + LLM-call-level detail; P3 must answer the 3-class landmine question first (which of `intelligence/models/agent_execution.py:11`, `intelligence/models.py:587`, `core/models_unified_system.py:882` is canonical at HEAD?), then evaluate whether AgentExecution correlates to P1's CeleryTaskEvent and P2's LLMCallEvent. P3's scope-magnet risk: 3-class landmine could pull deprecation ADR into the audit — **boundary discipline**: catalog + name canonical; deprecation ADR is post-arc T-slot. |
| **P4** | S1704 | **D** | Tool Call Telemetry (`ToolCallRecord`) | **Depends on P1 + P3.** ToolCallRecord sits inside AgentExecution — tools are called by agents, dispatched via Celery, wrapped by BaseAgent `__init_subclass__()`. P4 must verify all 74 enabled agents write records on all return paths at HEAD (S1115 regression check) + managed-agent + orchestration-agent + PA-dispatch paths + wrapped-tool delegation. Depends on P3 because AgentExecution↔ToolCallRecord correlation contract must be defined before per-tool coverage can be evaluated. |
| **P5** | S1705 | **E** | Ops / Mission Telemetry (`OpsRun` + `OpsRunEvent`) | **Depends on P1 + P2 + P3 + P4** (P2 explicitly added per Rigby SIGN cycle 1 F4 MUST-FIX fold). OpsRunEvent aggregates mission-scoped outcomes; P5 must answer "does OpsRunEvent produce a new event contract, or consume from prior 4 layers?" + "does MissionRunner (Employee OS) actually write OpsRun rows at HEAD?" Depends on P1 (does OpsRun correlate via CeleryTaskEvent task_id?), P2 (mission-scoped LLM cost + latency aggregation requires LLMCallEvent evidence; "is OpsRunEvent producer vs consumer" cannot be answered without LLM-spend attribution semantics landed at P2), P3 (does it aggregate AgentExecution outcomes?), P4 (does it aggregate ToolCallRecord counts?). P5 also detects WRITE-ONLY-FORGOTTEN pattern per Group 1500 §14.3 precedent. |
| **P6** | S1706 | **F** | Adjacent / Separation Boundaries | **Depends on P1-P5 evidence base.** Once execution telemetry is rationalized, P6 asks: (a) what other telemetry is in scope but isn't execution-tracing? (b) where is the Observability↔Event-Architecture boundary? (c) which adjacent concerns should Group 1900 inherit (event-model catalog) vs Employee OS (Body Systems health) vs follow-on design-preparation arc (SLO framework)? P6 also does the WRITE-ONLY-FORGOTTEN catalog audit (14+ event-shaped models from S1273 lines 1912-1917) since that pattern crosses the observability↔event-architecture boundary. |
| **P7** | S1799 | **canonical_summary** | xx99 canonical summary — 5-layer dedup rationalization | **Consumes P1-P6.** Per playbook §11.3 12-section template + §11.3 §10 meta-methodology template FIFTH application (after S1399 first + S1499 second + S1599 third + S1699 fourth). §5 four-axis (or fewer, per Cat F evidence) posture-decision evidence brief — the load-bearing D74-analog question about structural-separability vs canonical-unification. §8 T0/Gate + T1 unified follow-on queue. §10 fifth-application meta-methodology confirms F.i/F.ii/F.iii durable at five-consecutive-application. Rigby SIGN cycle 1 required per playbook §15. |

**Capacity consideration.** Per playbook §17 120+ evidence anchors
per child audit, Chris's ratified capacity = 1 child + close-out
per session, total sessions = N+2 (parent + N children + summary).
Group 1700 = 1 parent + 6 children + 1 summary = **8-doc arc**
matching S1499 (Revenue) + S1599 (Sports) + S1699 (Content)
precedent. Total arc runtime target: 8 sessions across arc close;
child audits ~1300-1700 lines each (per S1600/S1500/S1400
precedent); xx99 canonical summary ~1900-2100 lines (per S1699 =
2017 lines + S1599 = 2241 lines + S1499 = 1915 lines).

**Parallelism note (per D3 next-session cadence).** D3 ratified at
S1700 open: parent-only this session; P1 kicks off next-session.
Per playbook precedent (Groups 1400/1500/1600 all sequential), no
parallel-child execution proposed. Chris can re-scope at any
future session-open if cadence needs to compress.

---

## 6. Parked candidate issues

Items scoping-but-not-answering — Chris-gated for later T-slots or
follow-on arcs.

### 6.1 SLO framework design

S1273 line 1969 flags "no meta-SLO framework." Group 1700 audits
what exists (single `check_learning_loop_slo`). If xx99 surfaces
"systemic SLO framework is load-bearing," it's a follow-on
design-preparation arc — NOT part of Group 1700's six child
audits. Chris ratifies at xx99 whether SLO design becomes a T0/Gate
ADR or a later arc.

### 6.2 Rigby v0 event intake activation

S1273 line 1959: `RIGBY_EVENT_INTAKE_ENABLED=False`. Group 1700
catalogs the gap; wiring Rigby to intake events is a downstream
implementation project post-xx99. If Cat F surfaces "Rigby intake
is load-bearing for consumer-side of P5 OpsRunEvent," Chris
ratifies at xx99 whether it becomes a T1 item.

### 6.3 3-class AgentExecution deprecation ADR

P3 catalogs the 3-class landmine; the deprecation ADR (choose
canonical + retire 2 others) is post-arc T-slot. If Chris
ratifies as T0/Gate at xx99, the ADR blocks any downstream P4
audit implementation work.

### 6.4 HeartBeat cold-start reliability

S1273 line 1964: digestive + muscular systems report sluggish/
paralyzed on fresh DB. Cat F catalogs; fix is Employee OS or
Body-Systems reliability project. Group 1700 does NOT own the fix.

### 6.5 HeartBeat export / dashboard / alerting

S1273 line 1965: collection exists but never exported. Cat F
catalogs; design of the export pipeline is post-xx99.

### 6.6 WRITE-ONLY-FORGOTTEN event-model deprecation

Cat F catalogs 14+ event-shaped models per S1273 lines 1912-1917;
per-model deprecation decisions (keep-and-wire vs remove) are
Group 1900 Event Architecture territory. Group 1700 produces the
catalog; Group 1900 acts on it.

### 6.7 Doc-claim verifier meta-observability integration

Cat F catalogs whether doc-claim verifier drift is a
telemetry-worthy signal. Integration of verifier drift into
observability infrastructure is post-xx99 design-preparation.

### 6.8 Monitor-task overhead systematic bound

Cat A P1 audits the observability-of-observability question
(§2.7). If the answer is "monitor tasks are unbounded and eating
X% of wall-clock," systematic bound design is post-xx99.

---

## 7. Anti-scope

Bounded-OUT items per Chris D-decisions D69-D74. Each has
one-sentence rationale + cross-reference to prior arc where
pattern repeats.

1. **Event bus adoption + design.** Group 1900 delegation per D2.
   Per S1274 §11.1 EventBus adoption.

2. **Event schema versioning.** Group 1900 delegation. Per S1274
   §11.2 event-schema evidence.

3. **DeliverableEvent consumer wiring.** Group 1600 T0/Gate
   R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E owns.

4. **Memory learning-loop internal correctness.** Group 1300
   Memory arc closed at S1399. Producer-side telemetry contract IS
   in scope; internal Memory logic is not.

5. **Content Deliberation pipeline retry policies.** Group 1600
   Content arc territory; Group 1700 audits generic telemetry
   Content uses, not Content-specific retry pathways.

6. **Sports betting pattern types + SignalCluster gap remediation.**
   Group 1500 closed at S1599; P11 6-arc consumer-side
   SignalCluster gap COMPLETED per S1599 pattern class 11.

7. **Revenue outreach delivery re-scope.** Group 1400 R.B1
   OutreachDraft delivery ADR is a Group 1400 cross-arc handoff;
   Group 1700 evidence may inform it but does not own it.

8. **Employee OS mission runner refactor.** Concurrent Employee
   OS scope; Group 1700 audits OpsRunEvent trail from
   MissionRunner runs, not the runner's internal correctness.

9. **PA tool surface unification.** Group 1600 Cat E anchor
   LOCKED per S1605 F9 (tactical-split); Group 1700 audits
   ToolCallRecord coverage of dispatch, not tool surface design.

10. **BaseAgent refactor / decomposition.** BaseAgent is 5,575
    lines; refactor is out of scope.

11. **AI provider selection / cost optimization strategy.** Cat B
    audits LLMCallEvent cost accounting completeness; provider
    selection is product decision.

12. **Body Systems cold-start reliability fix.** Cat F catalogs
    drift (S1273 line 1964); fix is Employee OS territory.

13. **Fleet application observability sweep.** Cross-repo fleet
    apps have their own telemetry; Group 1700 scope is
    unified-donkey-betz only.

14. **Historical arc T-slot inheritance.** Group 1300/1400/1500/
    1600 post-arc §7 anchor-update queues + T1 CRITICAL
    remediation queues stay in their owning arcs' backlogs.

15. **Doc-claim verifier bug fixes.** Cat F catalogs verifier
    drift as observability signal; verifier bug fixes belong to
    verifier PR track.

16. **Governance Ratification Ledger observability.** Governance
    decision audit trail (per `docs/governance_redesign.md`) is
    surfaceable at xx99 but not a P1-P6 candidate. Follow-on
    Chris-ratification.

17. **Rigby SIGN worker-instability D48 pattern investigation.**
    Meta-methodology finding tracked in Memory
    `feedback_rigby_sign_worker_instability_recovery.md`; belongs
    to research OS meta layer, not observability domain.

18. **AGENT_MAP agent retirement audit.** Group 1700 uses AGENT_MAP
    counts (74 enabled) as observability baseline; agent retirement
    is agent-registry concern.

19. **Frontend / WebSocket / client telemetry** (per Rigby SIGN
    cycle 1 F6 fold). Browser + React runtime instrumentation +
    WebSocket connection health + client-side error tracking
    (Sentry-analog) is a frontend-observability subdomain that
    Group 1700 does NOT own. Cat F may reference Frontend
    WebSocket as event-flow consumer (per Group 1600 §7 topic
    references), but frontend-runtime observability is
    out-of-scope. Follow-on candidate: if Chris ratifies at
    xx99, a "Frontend Observability" scope opens as a separate
    arc.

20. **Auth token / external-integration telemetry** (per Rigby
    SIGN cycle 1 F6 fold). OAuth token issuance / rotation /
    revocation audit trails + external-API key usage tracking +
    permission-scope logs (per Memory rules
    `feedback_anthropic_client_factory.md` +
    `feedback_openai_client_factory.md` provider timeout
    boundaries) belong to a security/identity observability
    scope, NOT execution-telemetry. Cat B audits LLMCallEvent
    completeness including provider identity; Cat B does NOT
    audit OAuth flow observability. Follow-on: if xx99 surfaces
    provider-auth observability as load-bearing, a
    "Security/Identity Observability" scope opens as separate
    arc.

21. **"RigbyTelemetry" or any new observability layer buildout**
    (per Rigby SIGN cycle 1 F6 fold). If a P1-P6 audit
    identifies a gap requiring a NEW observability model/layer
    (analog to OpsRunEvent introduction at S1250 PR3), the
    recommendation lands as an xx99 §8 follow-on item — **not**
    as an in-scope design task. Group 1700 audits existing 5+
    layers + adjacent; it does not design new ones. This bounds
    activation of the currently-disabled Rigby v0 intake
    (`RIGBY_EVENT_INTAKE_ENABLED=False`, per §7 item 2 + §6.2
    parked candidate) explicitly OUT of the audit scope.

---

## 8. Decisions recorded (Chris-locked 2026-07-02)

Six D-verdicts D69-D74 all Chris-ratified via "agree all + SIGN"
round at S1700 open. Rigby light SIGN cycle 1 SIGN-with-edits at
High confidence delivered F1-F6 folds landed pre-commit; no
D-verdict override or edit required. Status flipped draft →
active same-commit.

- **D69 — Parent shape.** Group 1700 = PARENT-WITH-CHILDREN
  6-child arc (P1 Cat A + P2 Cat B + P3 Cat C + P4 Cat D + P5
  Cat E + P6 Cat F + P7 xx99 canonical summary). Evidence per §4.
  Alternative: single-audit rejected per §4 alternative-rejected
  paragraph. **Default lean: (a) accept 6-child shape.**

- **D70 — Category count + boundary rules.** Six categories A–F
  with boundary rules per §3. F1-F12 Rigby folds (if light SIGN
  routed) may refine boundary rules pre-lock. Alternatives:
  4-category (collapse Cat A+E into single "orchestration
  telemetry") rejected because dedup evidence requires per-layer
  independence; 8-category (split Cat F into Body Systems + SLO
  + WRITE-ONLY-FORGOTTEN separate categories) rejected because
  Cat F is the natural cross-cutting bin. **Default lean:
  (a) accept 6 categories.**

- **D71 — Delegation boundary with Group 1900 Event Architecture.**
  Group 1700 owns execution-telemetry writer contracts (Cat A/B/C/
  D/E) + adjacent cataloging (Cat F). Group 1900 owns event bus /
  routing / schema versioning + cross-domain event flow contracts.
  Explicit boundary: **"Observability owns producer-side telemetry
  contract completeness; Event Architecture owns cross-domain
  event routing."** Alternatives: (i) Group 1700 also owns event
  bus (over-scoped, rejected); (ii) Group 1900 also owns
  producer-side telemetry (blurs boundary, rejected). **Default
  lean: (a) accept explicit boundary as stated.**

- **D72 — Child sequence + dependency clauses.** P1 Cat A → P2
  Cat B → P3 Cat C → P4 Cat D → P5 Cat E → P6 Cat F → P7 xx99
  sequential per §5. Explicit dependency clauses embedded in §5
  rationale column per F10 fold pattern. Alternatives:
  (i) reorder Cat C before Cat B (rejected because AgentExecution
  requires LLM-call correlation contract from Cat B evidence);
  (ii) parallel P3+P4 (rejected because ToolCallRecord scope
  needs AgentExecution boundary defined first). **Default lean:
  (a) accept sequential P1→P7.**

- **D73 — Posture-decision framing vs recommendation.** xx99
  produces posture-decision **evidence plan** for D74-analog
  question (§8 D74) — NOT posture recommendation. Follows S1599
  D59 + S1699 D65a/D65b/D65c/D65e precedent (four-axis brief
  with Chris-gated selection tag per axis). Alternative:
  xx99 recommends posture (rejected per S1600 D65 precedent —
  Chris gates posture selection post-arc). **Default lean:
  (a) accept posture-decision framing = evidence plan; posture
  selection is Chris-gated post-arc ADR.**

- **D74 — Load-bearing arc lens question (posture-decision
  frame).** "Are the 5 execution-telemetry layers structurally
  separable (each layer owns a distinct concern with lightweight
  FK correlation), OR do they need canonical unification (single
  execution_id + trace_id spine spanning task→LLM→agent→tool→ops
  with unified write path)?" This is the D74-analog question that
  P1-P6 child audits gather evidence for. xx99 §5 produces the
  posture-decision evidence brief; Chris ratifies selection
  post-arc. Alternative: "recommend canonical unification"
  (rejected per D73 posture-framing discipline). **Default lean:
  (a) accept as arc lens question, evidence-plan framing only.**

---

## 9. Next step

Chris ratifies D69-D74 via "agree all + D-N=(a)" round OR
per-verdict override. Optional: Chris routes to Rigby light SIGN
pressure-test pre-lock per playbook §15 stage-table parent row
(default: skip light SIGN — Chris decides based on how confident
he is in the taxonomy).

After D69-D74 ratification:

1. Update this doc's frontmatter: `status: active` + append
   D-verdicts + Chris-lock date to `decisions_locked` field.
2. If light SIGN routed + returned SIGN-with-edits: land F1-F? folds
   at commit-time; add "do not regress" notes to `verifier_loop`.
3. Move S1700 handoff to `docs/handoffs/SESSION_1700_OBSERVABILITY_
   ARC_OPEN.md`.
4. Overwrite `00-START-NEXT-SESSION.md` with next-session
   priorities (P1 CeleryTaskEvent audit per D72 sequence).
5. Bump `docs/research/ARCHITECTURE_INDEX.md` v42 → v43 with §1.46
   S1700 registration + line-6 preamble bump.
6. Move `docs/research/OPEN_ARCS.md` Group 1700 row from "Not
   started" to "In-progress"; bump line-6 preamble.
7. Chris merges S1700 PR to `main` between sessions.
8. Run post-merge 4-step docs cascade + `build_docs_provenance`
   per Memory rule `feedback_docs_cascade_at_every_close.md`.

Next session opens on P1 CeleryTaskEvent audit (S1701) per D72.
Arc runtime target: 8 sessions (S1700 parent + S1701-S1706 children
+ S1799 xx99) matching Groups 1400/1500/1600 precedent.

---

## Appendix — Frontmatter provenance

The frontmatter fields at the top of this document conform to
`DOMAIN_RESEARCH_PLAYBOOK.md` §6 metadata standard for parent-doc
type. Key fields:

- `authority: parent-doc for Group 1700 research arc` (required
  for arcs; parent-doc scope)
- `category: parent_scoping` (arc slot)
- `session: 1700` (arc-parent session)
- `research_group: 1700`
- `child_slot: P0` (implicit — parent-doc)
- `domain_slug: observability`
- `supersedes: none` (no prior observability parent-doc)
- `status: draft` (pending Chris ratification of D69-D74)
- `verifier_loop:` scope of verification + Rigby SIGN state
  (parent = optional light SIGN per §15 stage table)
- `delegates_to:` Group 1900 Event Architecture (D2) + Group
  1600 Content T0/Gate + Group 1300 Memory + Employee OS
- `delegated_from:` S1273 §3.25 + S1273 §5.13 + S1274 §11.6 +
  S1699 §8 T-slots

Pattern-precedent: matches `docs/research/domains/content/1600_content_domain_scoping.md`
(third-application methodology exemplar). Frontmatter shape
inherited from Group 1600 parent per playbook §11.1 template.
