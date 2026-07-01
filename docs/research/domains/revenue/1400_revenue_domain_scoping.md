---
title: "S1400 Revenue — Parent Architecture Scoping (Group 1400 mission plan)"
status: active (parent — all Chris decisions locked 2026-07-01: D21 D23 D24 D25 D26 D27 D28 D29 across three "agree all" ratification rounds; Rigby SIGN-clean cycles 1 + 2 folded; Phase 0 methodology per Chris directive applied at §10/§11/§12)
authority: parent-doc for Group 1400 research arc + first application of Chris's Phase 0 3-step methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) proposed as playbook v3 §11.1 template addition (D29 Chris-locked; promotion at Group 1500 close per two-triggers threshold)
category: parent_scoping
session: 1400
date: 2026-07-01
decisions_locked: 2026-07-01 (D21 via short command "start research group 1400"; D23 D24 D26 D27 D28 via "agree all" round 1; D25 F.i + D29 Yes-two-triggers via "agree all" round 2 after Phase 0 methodology directive)
domain_slug: revenue
research_group: 1400
authors: Claude Code (Chris directed via short command)
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                             # process (S1274 v1 → v2 S1276) — §11.1 template applied here
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                    # OS (S1278) — arc-open contract
  - docs/research/OPEN_ARCS.md                                            # arc manifest — Group 1300 → Group 1400 handoff
  - docs/research/platform_architecture_inventory.md §3.32                # Revenue / Outreach / Engagement Pipeline (S1273 v2 Rigby-added row)
  - docs/research/platform_architecture_inventory.md §4.9                 # Spider → Opportunity → Outreach → Engagement → Meeting → ClosePack → Revenue flow (S1273 v2)
  - docs/research/platform_architecture_inventory.md §5.12                # "Revenue Pipeline Canonical Architecture" 4-4h research mission (S1273 v2 recommendation)
  - docs/research/platform/cross_domain_integration_audit.md §2.4         # Revenue Pipeline integration classes (S1274)
  - docs/research/platform/cross_domain_integration_audit.md §3.7         # Revenue Opportunity → Initiative Suggestion MEDIUM finding (S1274)
  - docs/research/platform/cross_domain_integration_audit.md §5.10        # Outreach/Engagement/Meeting/Close tight-coupling classification (S1274)
  - docs/research/platform/cross_domain_integration_audit.md §9.6         # Revenue / Outreach Pipeline — LOW readiness (S1274)
  - docs/research/platform/cross_domain_integration_audit.md §14 line 1499 # Finding #36 — Revenue Pipeline no runtime owner HIGH (S1274)
  - docs/research/domains/memory/1300_memory_domain_scoping.md            # parent-with-children exemplar (S1300)
  - docs/research/domains/memory/1399_memory_canonical_summary.md         # first formal xx99 canonical summary (S1399)
  - docs/PLATFORM_INVENTORY.md                                            # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                           # narrative anchor
scope: Phase 0 domain-definition — decide whether Group 1400 is a single canonical audit or a parent-with-children research arc; produce candidate subdomain taxonomy grounded in verified runtime surface; propose child mission sequence for Chris to lock
non_goals:
  - the audit itself (that begins after Chris picks parent-vs-single + locks §5 sequence)
  - answering the 28 playbook canonical questions (that is the audit's job)
  - resolving any UNKNOWN from S1273 §10.3 / §3.32 (parked to child audits)
  - any implementation proposal (this is scoping, not architecture design)
  - Ops Autopilot runtime-primitive research (non-candidate — see §7)
  - Freelance opportunity subsystem lifecycle research beyond its FK-boundary to Opportunity (open question — see §3 Category F)
  - external companion project scope (BILLING_MONETIZATION_SYSTEM.md from ai-content-studio treated as design context, not runtime)
owner: claude (Chris directed at S1400 open via short command "start research group 1400")
---

# Session 1400 — Revenue Domain Taxonomy Proposal (Phase 0)

> **What this doc is.** A scoping deliverable produced *before* any
> Revenue domain audit begins. Chris typed the short command "start
> research group 1400" at S1400 open — the D21 launch verdict per
> `00-START-NEXT-SESSION.md` (default lean per playbook §22 queue).
> This doc opens the arc by (a) recording that verdict, (b)
> demonstrating from verified runtime evidence that Revenue is much
> larger than S1273 §3.32 captured, (c) proposing a candidate
> subdomain taxonomy Chris can inspect and edit, and (d) asking
> Chris to lock the parent-vs-single verdict + child mission
> sequence before any audit work begins.
>
> **What this doc is not.** The audit itself. A design proposal. A
> recommendation about *how* Revenue should work. Every claim below
> cites either an existing research doc (S1273 / S1274 / S1300 /
> S1399) or a verified file:line at the current `main` HEAD.

---

## 1. Why Phase 0

The Group 1300 Memory arc taught the library that any research
group whose S1273 domain row shows plural noun structure ("Memory
/ Knowledge / Embeddings") is a candidate for parent-with-children
shape. Group 1300 opened with the same Phase 0 discipline (S1300
parent scoping) and closed with a 5-child arc + xx99 canonical
summary (S1399). Playbook §11.1 codified this discipline for
future arcs.

The playbook §22 domain queue row for Group 1400 is:

> **1400** — Revenue / Outreach / Engagement Pipeline — §3.32 —
> LIGHT coverage — Rigby-caught missed domain (S1273 v2);
> business-value highest under-researched domain.

The label already contains three coordinated nouns ("Revenue /
Outreach / Engagement"). S1273 §3.32 folded them into a single
domain because the review sub-agents did not surface them; Rigby's
independent grep caught the gap and named it as one row. Whether
that folding still holds at audit time — or whether the three (or
more) subdomains under the Revenue label deserve separate child
audits — is exactly what Phase 0 answers.

The playbook (S1274 §2 rule 3) explicitly permits and encourages
this split:

> If the domain is bigger than expected, splitting into sub-groups
> is fine. Do not force a single session to cover a multi-subsystem
> domain.

The load-bearing question for Phase 0: **is Revenue one domain, or
is it a parent capability composed of several subdomains that each
warrant their own child audit?**

---

## 2. What existing inventory already tells us

Three research artifacts already say something material about the
Revenue surface. Every one either signals *"bigger than one audit
can cover"* or *"has load-bearing UNKNOWNs a single sub-agent sweep
cannot resolve."*

### 2.1 S1273 §3.32 Revenue / Outreach / Engagement Pipeline

S1273 v2 folded the domain into a single row after Rigby's SIGN
review caught its absence from v1. The row explicitly notes:

- **Coverage:** LIGHT (added S1273 v2 per Rigby review).
- **Maturity:** WORKING (tests reference end-to-end; unclear
  whether pipeline is actively driving revenue in prod).
- **Load-bearing UNKNOWNs (per S1273 §10.3):**
  1. Opportunity model exact location + schema.
  2. Outbound channel service for outreach (email? LinkedIn API?
     something else?).
  3. Close-pack conversion trigger (auto pipeline vs human
     approval via `HumanAttentionItem`).
  4. Whether opportunity → Initiative auto-creation exists.
  5. Ops Autopilot / standalone-service de-duplication path.

Three of the five (#2, #3, #4) are cross-domain wiring questions —
they cannot be resolved by staring at Revenue in isolation. That
alone hints at parent-with-children shape: sibling child audits
can each surface their piece of the wiring without any one child
being blocked on all five.

### 2.2 S1273 §4.9 cross-domain flow

The recorded end-to-end flow (S1273 v2 §4.9) touches **7 named
domains**:

> Spider Framework (8) → Signal Engine (9) → Traditional Agents
> (2) → Content Pipeline (11 via outreach_generation LLM path) →
> Revenue Pipeline (32) → Inbox/Messaging (17 for outbound
> channel) → HumanAttention (16 for meeting-scheduling escalation)
> → Observability (25 for ImpactEvent).

A single audit covering all seven cross-domain touchpoints would
lose fidelity to the receiving-domain boundaries. Splitting the
pipeline into subdomain audits lets each audit carry its
integration seam cleanly (e.g., an Outreach-composition audit
carries the Content Pipeline touchpoint; an Engagement-inbound
audit carries the Inbox touchpoint; etc.).

### 2.3 S1274 cross-domain integration audit

S1274 recorded **4 distinct findings** against domain 32:

| S1274 § | Finding | Class | Severity |
|---|---|---|---|
| §2.4 line 291 | Revenue Pipeline → Initiative Pipeline | MISSING | — |
| §2.4 line 293 | Revenue Pipeline → Inbox | MISSING (outbound channel UNKNOWN) | — |
| §2.4 line 294 | Revenue Pipeline → HumanAttention | MISSING (no auto-HAI on human-approval-required opportunity) | — |
| §3.7 | Revenue Opportunity → Initiative Suggestion | missing_connection | MEDIUM (revenue leakage) |
| §5.10 | Outreach / Engagement / Meeting / Close 4-model orphan-record risk | intentional tight coupling | LOW |
| §9.6 | Revenue / Outreach Pipeline extraction readiness | LOW (research-stage) | — |
| §14 finding #36 | Revenue Pipeline — no runtime owner | unclear_owner | HIGH |

Two are HIGH-severity findings (#36 no runtime owner; MISSING
Initiative wiring is MEDIUM but S1274 flagged as revenue-leakage
risk). Both are architectural / ownership questions, not
implementation bugs. They belong at parent scope (arc-wide
integration + ownership frame) rather than a single child audit.

### 2.4 PLATFORM_INVENTORY.md (2026-06-22 snapshot at `554a41d3`)

The current runtime inventory lists **substantially more surface**
than S1273 §3.32's rough sketch:

**Revenue-related models (17 concrete Django models):**

| Model | File:line | Cluster |
|---|---|---|
| `Opportunity` | `core/models_unified_system.py:1201` | core opportunity |
| `OpportunityScore` | `core/models_unified_system.py:1694` | scoring |
| `OpportunityAction` | `core/models_unified_system.py:2552` | lifecycle |
| `OpportunityRevenue` | `core/models_unified_system.py:2613` | attribution |
| `OpportunityContent` | `core/models_unified_system.py:2805` | content link |
| `OpportunityPredictionAccuracy` | `core/models_unified_system.py:2905` | ML feedback |
| `OpportunityTask` | `core/models_unified_system.py:3000` | lifecycle |
| `OpportunityOutcome` | `core/models_unified_system.py:3394` | attribution |
| `OpportunityDigest` | `core/models_unified_system.py:3493` | rollup |
| `OpportunityInteraction` | `core/models_engagement_metrics.py:164` | engagement |
| `OutreachDraft` | `core/models_outreach.py:18` | outreach |
| `EngagementEvent` | `core/models_engagement.py:18` | engagement |
| `EngagementMetrics` | `core/models_engagement_metrics.py:14` | engagement |
| `ContentEngagement` | `core/models_pipeline_feedback.py:370` | engagement |
| `Meeting` | `core/models_meeting.py:18` | meeting/close |
| `ClosePack` | `core/models_close_pack.py:20` | meeting/close |
| `FreelanceOpportunity` | `core/models_autonomous_situations.py:352` | freelance (adjacent) |

That is **10 Opportunity variants**, **4 Engagement variants**,
**1 Outreach**, **1 Meeting**, **1 Close**, and **1 Freelance
adjacent**. S1273 §3.32 named 4 models (`OutreachDraft`,
`EngagementEvent`, `Meeting`, `ClosePack`) and flagged Opportunity
model location as UNKNOWN. Reality is far larger.

**Revenue-related services (10+ classes):**

- `core/services/opportunity_pipeline_orchestrator.py:309`
  `OpportunityPipelineOrchestrator` (top-level)
- `core/services/opportunity_execution_pipeline.py:35`
  `OpportunityExecutionPipeline`
- `core/services/opportunity_scorer.py` (module)
- `core/opportunity_ai_analyzer.py:82` `OpportunityAIAnalyzer`
- `core/services/ops_autopilot/outreach_generation.py:92`
  `OpportunityDraftGenerator`
- `core/services/ops_autopilot/engagement.py:235`
  `EngagementEngine`
- `core/services/ops_autopilot/engagement.py:479` `MeetingEngine`
- `core/services/ops_autopilot/engagement.py:764`
  `EngagementAutonomyEngine`
- `core/services/ops_autopilot/revenue.py:605` `OutreachSequencer`
- `core/services/ops_autopilot/revenue.py:1504`
  `ClosePackAutonomyEngine`
- `core/services/ops_autopilot/revenue.py` (top-level revenue
  module — total 1500+ lines pre-`OutreachSequencer`)
- `core/services/ops_autopilot/impact.py` (impact scoring,
  `ImpactEvent` emitter)
- `intelligence/opportunity_storage.py`
- `intelligence/revenue_integration.py`
- `intelligence/revenue_tracking_bridge.py`
- `intelligence/spider_opportunity_connector.py`
- `intelligence/sports_opportunity_generator.py`

**Revenue-related agents (3):**

- `core/agents/analysis/opportunity_scoring_agent.py:131`
  `OpportunityScoringAgent`
- `core/agents/opportunity_pipeline_agent.py:89`
  `OpportunityPipelineAgent`
- `core/agents/executive/meeting_coordinator_agent.py:66`
  `MeetingCoordinatorAgent`

**Revenue-related infrastructure:**

- WebSocket consumer: `core/consumers_base.py:2512`
  `OpportunityScannerConsumer`
- ML: `ml_pipeline/opportunity_categorizer.py`
- Learning bridge: `core/learning_bridges/revenue_attribution_bridge.py`
- EventBus event: `OPPORTUNITY_SCORED` (S1274 §6.2 registry —
  publisher `event_bus.py:559:publish_opportunity_scored_event`,
  consumer `process_event_bus_scoring_queue`)
- Celery beat task: `calculate-daily-revenue-metrics`
  (`intelligence.tasks.calculate_daily_revenue_metrics`)
- Django view files: `views_opportunity.py`, `views_revenue.py`,
  `views_revenue_analytics.py`, `views_revenue_tracking.py`
- Frontend routes: `opportunity-detail`, `revenue`,
  `revenue-dashboard`, `revenue-opportunities`
- Signal pattern type: `opportunity_window` (1 of 10 canonical
  SignalCluster pattern types)
- Feedback signal handler: `revenue_attribution_bridge.py:22-28`
  (Revenue → UserAgentLearning bridge — S1274 §4.3)

That inventory has already registered Revenue as a **multi-model,
multi-service, multi-agent, cross-domain, cross-frontend surface**
with clear structural cleavages (scoring vs outreach vs engagement
vs meeting/close vs attribution vs adjacent freelance) — independent
evidence for parent-with-children shape.

### 2.5 S1399 Group 1300 canonical summary (methodology inheritance)

Group 1300 shipped the first formal xx99 canonical summary in the
library (S1399 §1.21 in ARCHITECTURE_INDEX v18) and named four
load-bearing methodology outputs (per S1399 §4 F1-F4):

- **F1** — provenance-filter drift class (writer/reader
  provenance-tag consistency).
- **F2** — row-level orphan-write pattern (fields written
  everywhere, read nowhere).
- **F3** — Redis-only durability + `@lru_cache` staleness pattern.
- **F4** — F1/F4-CANDIDATE + severity-correction discipline as
  inheritance methodology (sibling verifier-loop before hardening).

Group 1400 inherits these patterns as diagnostic lenses. F2
(orphan-write) is especially likely to appear in a 17-model
subsystem where models were added incrementally over time.

---

## 3. Candidate subdomain taxonomy

The following categories are candidates for child audits under
Research Group 1400. Each row lists the primary systems in scope
(from §2.4 above), the S1273 §3.32 fragment it corresponds to (if
any), and the drift already noted at the parent level.

### A — Opportunity Discovery + Scoring

**Primary systems.** `Opportunity` + `OpportunityScore` +
`OpportunityPredictionAccuracy` + `OpportunityDigest` +
`OpportunityInteraction` (as scoring feedback);
`OpportunityPipelineOrchestrator` +
`OpportunityExecutionPipeline` + `opportunity_scorer.py` +
`opportunity_ai_analyzer.py`; `OpportunityScoringAgent` +
`OpportunityPipelineAgent`; `intelligence/opportunity_storage.py`
+ `intelligence/spider_opportunity_connector.py` +
`intelligence/sports_opportunity_generator.py`;
`ml_pipeline/opportunity_categorizer.py`;
`OpportunityScannerConsumer` (WebSocket); EventBus
`OPPORTUNITY_SCORED`; signal type `opportunity_window`.

**S1273 §3.32 fragment.** "Spider → OpportunityScoringAgent →
Opportunity record" step of §4.9 flow; §3.32 "Major services"
first two bullets.

**Drift already flagged.**
- Opportunity model exact schema was UNKNOWN at S1273 close
  (§10.3 first bullet). §2.4 above now names `Opportunity` at
  `models_unified_system.py:1201` — but this is a claim in the
  inventory, not a schema audit. Child A verifies.
- Sports/DBAO → Opportunity integration is MISSING per S1274 §2.4
  line 270 — needs Category A to resolve whether the missing
  sports-integration is an intentional lane or an unshipped
  connection.
- `sports_opportunity_generator.py` exists in `intelligence/` —
  suggests a bridge does exist. Child A resolves.
- 10 Opportunity variants suggest possible F2 orphan-write
  pattern (each variant may have fields written by one path and
  read by another). Child A should apply the S1399 F2 lens.
- **Non-spider producer discovery** (added Rigby Light SIGN cycle
  1 nice-to-have #1). Discovery is presumed spider-first, but
  manual admin UI ingestion + API endpoints + import scripts may
  also produce Opportunity rows. Child A explicitly enumerates
  all producers (not just spider bridges) before naming
  discovery as "spider only."

### B — Outreach Composition + Delivery

**Primary systems.** `OutreachDraft` (`models_outreach.py:18`);
`ops_autopilot/outreach_generation.py:92 OpportunityDraftGenerator`;
`ops_autopilot/revenue.py:605 OutreachSequencer` (sequencing
layer sitting above per-draft composition).

**S1273 §3.32 fragment.** "OutreachDraft row → send via external
channel" step of §4.9 flow; §3.32 "Major services"
`outreach_generation.py` bullet.

**Drift already flagged.**
- Outbound channel service is UNKNOWN per S1273 §3.32 + §10.3
  second bullet. Child B answers: is outreach actually SENT?
  Where? Which service? Email? LinkedIn API? Discord? Rigby DM?
- S1274 §2.4 line 293 flagged Revenue → Inbox as MISSING —
  Child B resolves whether "MISSING" means "not wired" or "wired
  through a non-Inbox path (e.g., partner SMTP integration)."
- LLM-driven draft composition depth: is
  `OpportunityDraftGenerator` a single-shot LLM call, or does it
  use the Content Deliberation Pipeline (§3.11) reviewer chain?
  Child B verifies.

### C — Engagement Inbound

**Primary systems.** `EngagementEvent`
(`models_engagement.py:18`); `EngagementMetrics`
(`models_engagement_metrics.py:14`); `OpportunityInteraction`
(`models_engagement_metrics.py:164`); `ContentEngagement`
(`models_pipeline_feedback.py:370`);
`ops_autopilot/engagement.py:235 EngagementEngine`;
`ops_autopilot/engagement.py:764 EngagementAutonomyEngine`.

**S1273 §3.32 fragment.** "EngagementEvent inbound" step of §4.9
flow; §3.32 "Major services" `engagement.py` bullet (single
model named).

**Drift already flagged.**
- 4 engagement-shape models exist (`EngagementEvent`,
  `EngagementMetrics`, `OpportunityInteraction`,
  `ContentEngagement`). Distinction between them is UNKNOWN.
  Likely F2 orphan-write territory. Child C untangles which is
  read by whom.
- Autonomy semantics: `EngagementAutonomyEngine` implies a
  gated-vs-full autonomy toggle. Child C verifies gate location
  and default state (Governance domain §3.23 crossover).

**Category C hypothesis map** (added Rigby Light SIGN cycle 1
nice-to-have #2 — helps avoid over-splitting while keeping child
mission crisp). The 4 engagement models are hypothesized to
resolve onto two axes:

- **Event log axis** — `EngagementEvent` (canonical inbound
  event stream).
- **Aggregation axis** — `EngagementMetrics` +
  `ContentEngagement` (derived rollups / analytical surfaces).
- **Join artifact** — `OpportunityInteraction` (opportunity ↔
  engagement bridge model).

Child C mission crystallizes as: verify the canonical event
stream + map derived-metrics providers + identify who writes vs
who reads each. Does NOT presume a required split into multiple
children — the mission is untangle, not divide.

### D — Meeting + Close

**Primary systems.** `Meeting` (`models_meeting.py:18`);
`ClosePack` (`models_close_pack.py:20`); `OpportunityAction` +
`OpportunityTask` (lifecycle checkpoints);
`MeetingCoordinatorAgent` (`meeting_coordinator_agent.py:66`);
`ops_autopilot/engagement.py:479 MeetingEngine`;
`ops_autopilot/revenue.py:1504 ClosePackAutonomyEngine`.

**S1273 §3.32 fragment.** "MeetingCoordinatorAgent → Meeting →
ClosePack" step of §4.9 flow; §3.32 "Major services" implicit
via `engagement.py` + `revenue.py`.

**Drift already flagged.**
- Close-pack conversion trigger UNKNOWN per S1273 §10.3 third
  bullet — auto pipeline vs human approval via `HumanAttentionItem`.
  Child D resolves.
- S1274 §2.4 line 294 flagged Revenue → HumanAttention as
  MISSING for approval-required opportunities. Child D verifies
  whether the "missing" wiring is at the Meeting stage or the
  ClosePack stage or both.
- S1274 §5.10 intentional-tight-coupling classification flagged
  ORPHAN-RECORD risk (ClosePack without Meeting FK; Meeting
  without EngagementEvent trigger) with no integrity task
  auditing. Child D produces the integrity audit design (not
  implementation).

### E — Revenue Attribution + Analytics

**Primary systems.** `OpportunityRevenue`
(`models_unified_system.py:2613`); `OpportunityOutcome`
(`models_unified_system.py:3394`); `OpportunityContent`
(`models_unified_system.py:2805`);
`ops_autopilot/revenue.py` (top-level revenue module);
`ops_autopilot/impact.py`; `intelligence/revenue_integration.py`
+ `intelligence/revenue_tracking_bridge.py`;
`learning_bridges/revenue_attribution_bridge.py`;
`views_revenue.py` + `views_revenue_analytics.py` +
`views_revenue_tracking.py`; frontend routes `revenue`,
`revenue-dashboard`, `revenue-opportunities`, `opportunity-detail`;
Celery beat `calculate-daily-revenue-metrics`
(`intelligence.tasks.calculate_daily_revenue_metrics`).

**S1273 §3.32 fragment.** "ImpactEvent" step of §4.9 flow +
§3.32 "Major services" `revenue.py` + `impact.py` bullets.

**Drift already flagged.**
- Revenue attribution logic in `ops_autopilot/revenue.py` was
  UNKNOWN per S1273 §3.32 "Known drift" second bullet. Child E
  produces the definitive attribution logic map.
- S1274 §14 finding #36 flagged "Revenue Pipeline — no runtime
  owner" at HIGH severity — the beat task `calculate-daily-
  revenue-metrics` may be the runtime owner de-facto, but no
  JobContract exists. Child E verifies + produces ownership
  recommendation.
- S1274 §2.4 line 292 confirmed Revenue → Observability as
  STRONG via `ImpactEvent` — Child E verifies at file:line +
  documents the write/read sites (revenue-facing telemetry
  boundary with §3.25 Observability).
- 3 revenue view files + 4 frontend routes suggest possible
  UI/analytic drift (multiple dashboards for the same underlying
  data). Child E maps.

### F — Freelance / Gig Opportunity subsystem (open question)

**Primary systems.** `FreelanceOpportunity`
(`models_autonomous_situations.py:352`) — currently sits in the
"autonomous situations" model file (not in the mainline Revenue
model files). May be a distinct opportunity type (freelance/gig
income lane), a legacy prototype, or an alternative-entry-point
into the Category A pipeline.

**S1273 §3.32 fragment.** Not mentioned.

**Open question for Chris (Phase 0).** Is FreelanceOpportunity:
- **(F.i)** Its own subdomain — an **Income / Jobs lane** (not
  just the FreelanceOpportunity model) with its own discovery,
  scoring, matching, application, and revenue flow.
  **Adjacent surface** (added Rigby Light SIGN cycle 1
  nice-to-have #3 — Rigby confirmed via `intelligence/` grep
  these files exist):
  - `intelligence/ai_job_matcher.py`
  - `intelligence/ai_job_application_pipeline.py`
  - `intelligence/agent_income_tools.py`
  - `intelligence/income_builder.py`
  - `intelligence/income_builder_automation.py`
  - `intelligence/income_builder_connector.py`
  - `intelligence/income_spider_orchestrator.py`
  - `intelligence/job_income_bridge.py`
  - `intelligence/job_scanner_consumer.py`
  - `intelligence/ai_resume_generator.py`

  If Chris rules F.i, the Category F child audit covers the
  entire Income/Jobs lane, not just the FreelanceOpportunity
  model.
- **(F.ii)** A subordinate of Category A (a specialization of
  the mainline `Opportunity` type).
- **(F.iii)** A dormant / legacy prototype not in active use.

Recommendation: **verify shape at Phase 0 → route to Chris → lock
before audit sequence starts.** If (F.i), promote to Category F
child audit. If (F.ii), fold into Category A child audit as a
scoped sub-question. If (F.iii), park as non-candidate in §7 with
a S1274-style unclear_owner debt row.

### Explicit non-candidates

The following are explicitly OUT-of-scope for Group 1400 to
prevent scope creep. Each has a documented sibling arc or is
deferred by other reasoning.

- **Ops Autopilot as a runtime primitive.** The
  `core/services/ops_autopilot/` package is 12+ modules covering
  budget, config, core, engagement, experiment, governance,
  impact, intelligence, outreach_generation, remediation,
  revenue, verification. Only the revenue-facing modules
  (outreach_generation, engagement, impact, revenue) are in
  Group 1400 scope. The **cross-cutting Ops Autopilot runtime
  primitive** (state machine, config schema, remediation loops,
  verification hooks) belongs in a separate arc — likely
  Employee OS 1200s (`docs/EMPLOYEE_OS_PRIMITIVES.md`) or a new
  Ops Autopilot arc. Documented as playbook §22 candidate.
- **BILLING_MONETIZATION_SYSTEM.md** (from external companion
  project `external-project-docs/ai-content-studio/`). Treated as
  design context, not runtime. If Chris wants runtime billing +
  Stripe/invoicing integration audited, it needs a separate arc
  scoped to that external system.
- **Opportunity → Initiative auto-create implementation.** S1274
  §3.7 named this as MEDIUM severity `missing_connection`. Group
  1400 documents the missing wiring at parent scope (§6 below +
  child E integration section) but does NOT design the wiring —
  that is a design-preparation phase per playbook §3 phase
  discipline. Deferred to post-1400 ADR.
- **Sports/DBAO → Opportunity integration** at the DBAO domain
  level. Group 1400 Category A resolves the "does the bridge
  exist and what does it emit" question. Whether DBAO becomes a
  full producer of opportunity data (island vs integrated —
  S1274 §11.3) is deferred to Group 1500 (Sports / DBAO /
  Intelligence — playbook §22 queue).
- **Content Deliberation Pipeline usage by outreach composition**
  as a Content-domain audit. Group 1400 Category B verifies
  whether outreach uses the Content Deliberation pipeline; the
  Content Pipeline audit itself is Group 1600 (Content /
  Deliverables / Publishing — playbook §22 queue).

---

## 4. Parent-vs-single recommendation

**Recommendation: parent-with-children.** Six named categories
above (A–E confirmed candidates + F open question) cover surface
that a single-session audit cannot answer at the file:line
evidence density the library requires (playbook §14 evidence
rules). Concretely:

1. **17 models across 8 files** cannot be untangled at the
   per-field consumer-inventory density S1300 Group 1300 taught
   the library (S1301 §14 D3 + S1304 §19 R1 methodology). A
   single audit that stays at that density spans 4–6× the
   playbook §11.2 20-section budget.
2. **5 load-bearing UNKNOWNs from S1273 §10.3** each belong to a
   different category (Opportunity schema = A; outbound channel
   = B; close-pack trigger = D; opportunity→Initiative wiring =
   parent §6; Ops Autopilot dedup = non-candidate). No single
   child can carry all five without becoming an arc-summary
   masquerading as a child.
3. **4 S1274 findings** at MEDIUM+ severity (§3.7 medium; §14
   finding #36 HIGH) are cross-cutting integration + ownership
   questions. They belong at parent scope (arc-level frame) or
   distributed across children (with the parent aggregating).
4. **Sibling verifier-loop discipline (S1399 F4)** requires
   cross-child pressure-testing — Category C's "which of the 4
   engagement models is canonical" answer will affect Category
   D's Meeting → ClosePack integration audit, which will affect
   Category E's revenue-attribution schema. This is exactly the
   sibling-verifier-loop pattern the S1300 arc taught the
   library. A single audit collapses that discipline.
5. **Rigby SIGN routing** — playbook §15 stage table calls for
   distinct SIGN rounds per child audit (with §15's Q1–Q9 per
   child + Q10–Q13 for the eventual xx99 canonical summary). A
   parent-with-children shape unlocks that discipline; a single
   audit forces one SIGN round to cover everything.

Group 1300 (S1300–S1399) is the direct precedent — same signal
(plural noun label in playbook §22 row + LIGHT coverage + multiple
UNKNOWNs + cross-domain integration debt), same recommendation
(parent-with-children), same arc shape (5 children + xx99 canonical
summary). Group 1400 mirrors it.

---

## 5. Proposed child mission sequence (draft — awaiting Chris ratification)

The order below is a recommendation. Chris ratifies (or reorders /
merges / drops) before any child audit starts. Sequence rationale
runs bottom-up: each later child inherits the previous child's
verified surface, matching the S1301 → S1302 → S1303 → S1304 →
S1305 → S1399 arc shape.

| Slot | Session ID | Category | Primary evidence surface | Chris-lock question |
|---|---|---|---|---|
| P1 | S1401 | **A — Opportunity Discovery + Scoring** | 10 Opportunity models + orchestrator + 2 agents + spider bridge + ML categorizer + WebSocket consumer + EventBus | first child (widest surface; produces the "Opportunity is what" answer every other child depends on) |
| P2 | S1402 | **B — Outreach Composition + Delivery** | `OutreachDraft` + `OpportunityDraftGenerator` + `OutreachSequencer` + outbound channel (UNKNOWN) | resolves 2 of the 5 S1273 §10.3 UNKNOWNs (outbound channel + LLM composition depth) |
| P3 | S1403 | **C — Engagement Inbound** | 4 engagement-shape models + `EngagementEngine` + `EngagementAutonomyEngine` | untangles the 4-model engagement cluster; likely F2 orphan-write territory |
| P4 | S1404 | **D — Meeting + Close** | `Meeting` + `ClosePack` + `MeetingCoordinatorAgent` + `MeetingEngine` + `ClosePackAutonomyEngine` + `HumanAttentionItem` boundary | resolves close-pack conversion trigger + integrity-audit design |
| P5 | S1405 | **E — Revenue Attribution + Analytics** | attribution models + `ops_autopilot/revenue.py` + `ops_autopilot/impact.py` + revenue view files + frontend routes + Celery beat | resolves runtime-owner question (S1274 finding #36); produces attribution schema |
| P6 | S1406 | **F — Income/Jobs lane** *(D25 default lean; pending Chris explicit ratification)* | `FreelanceOpportunity` + 9-file `intelligence/` adjacency (`ai_job_matcher`, `ai_job_application_pipeline`, `agent_income_tools`, `income_builder`, `income_builder_automation`, `income_builder_connector`, `income_spider_orchestrator`, `job_income_bridge`, `job_scanner_consumer`) + `ai_resume_generator` | resolves whether Income/Jobs is active vs dormant + who produces + integration seam to Category A |
| P7 | S1499 | **xx99 canonical summary** | consumes P1–P6 outputs + S1273 §3.32 + S1274 findings + resolves contradictions between siblings + produces §12.5 Revenue Lifecycle Traceability Table | first-arc-after-S1399 to apply playbook §11.3 §10 meta-methodology (per S1399 close 2026-07-01 rule) + concrete "done" artifact per Chris F.iii directive |

**D25 status.** Chris-locked F.i via "agree all" round 2
2026-07-01: create Category F child audit as S1406 (full
Income/Jobs lane). Arc shape locked at 6 children + xx99.

**Sequencing notes:**

- **P1 first, not P5 first.** Group 1300 taught (S1301 first, not
  the runtime-correctness S1305 first) that the widest-surface
  child grounds the whole arc. P1 A resolves the "what IS an
  Opportunity in this platform" question the other 4 children
  all depend on.
- **P2 before P3.** Outreach composition (B) is a prerequisite
  for Engagement inbound analysis (C) because Engagement is
  triggered by sent outreach. Reversing the order would require
  C to hypothesize B's shape.
- **P3 before P4.** Engagement (C) is the trigger for Meeting
  (D). Same reasoning.
- **P5 last, not first.** Attribution (E) is downstream of every
  other child + surfaces multiple UI/frontend routes.
  Consolidating those requires the upstream schemas locked.
- **Dependency rationale for late E** (added Rigby Light SIGN
  cycle 1 nice-to-have #4 — pre-empts the "attribution should be
  first" counterargument): Category E validates attribution
  *once* upstream contracts are frozen by A–D. Running E first
  would force the attribution audit to hypothesize the upstream
  schemas it's supposed to attribute against. Every attribution
  model (`OpportunityRevenue`, `OpportunityOutcome`,
  `OpportunityContent`) references a lifecycle stage owned by
  A–D. Freezing A–D first prevents E-side rework.
- **P6 canonical summary** applies playbook §11.3 template
  including §10 "What This Research Taught Us About How to Do
  Research" (adopted S1399 close 2026-07-01 per Chris directive
  — first application at S1399; second application will be
  S1499).

---

## 6. Parked candidate issues

Findings surfaced at parent scope that don't yet fit any child
mission. Each is either escalated to the child that will handle
it, deferred to a post-arc research phase, or logged as
integration debt.

- **P6.1 Opportunity → Initiative auto-create missing wiring**
  (S1274 §3.7 MEDIUM). Parent-level frame: revenue-leakage risk.
  Child assignment: parent §6 owns the finding; Child E may
  produce ADR-preparation notes if attribution audit surfaces
  revenue-threshold heuristics. Full implementation ADR deferred
  to post-1400 design-preparation phase.
- **P6.2 Revenue Pipeline — no runtime owner** (S1274 §14
  finding #36 HIGH). Parent-level frame: no JobContract, no
  dedicated beat, no dedicated queue. Child assignment: Child E
  proposes an ownership recommendation (Employee OS lane vs
  standalone workflow). Actual ADR deferred to design-preparation
  phase.
- **P6.3 Ops Autopilot layer de-duplication** (S1273 §3.32 tech
  debt bullet #2). Parent-level frame: 4 revenue-facing
  ops_autopilot modules overlap standalone services / agents.
  Child assignment: each of B/C/D/E includes an ops_autopilot vs
  standalone-service overlap section in §17 "Duplicate or
  Overlapping Systems." Parent §6.3 aggregates.
- **P6.4 Orphan-record integrity risk** (S1274 §5.10 LOW). No
  integrity task audits `ClosePack → Meeting → EngagementEvent`
  FK chain. Child D produces an integrity audit design.
- **P6.5 Sports/DBAO → Opportunity integration MISSING** (S1274
  §2.4 line 270). `sports_opportunity_generator.py` exists in
  `intelligence/`; whether it emits into the mainline Opportunity
  pipeline is UNKNOWN. Child A resolves. Full DBAO integration
  deferred to Group 1500.
- **P6.6 Sports betting outcomes → revenue attribution MISSING**
  (S1274 §2.4 line 270). Deferred to Group 1500 or a Group 1400
  ↔ Group 1500 cross-arc mission.
- **P6.7 3 revenue view files + 4 frontend routes drift risk.**
  Child E maps whether these serve distinct user needs or are
  overlapping analytics UIs.
- **P6.8 FreelanceOpportunity ownership** (open question §3
  Category F). Chris-lock resolves at Phase 0. If F.iii, log as
  S1274-style unclear_owner debt row.

---

## 7. Anti-scope

The following are explicitly OUT-of-scope for Group 1400 to
prevent scope creep beyond the parent-with-children shape agreed
in §4:

- **Implementation PRs.** Group 1400 is research + design-
  preparation phase. Any ADR-caliber recommendation surfaced by a
  child gets deferred to post-arc phase per playbook §3.
- **Ops Autopilot runtime primitive audit** (see §3 Explicit
  non-candidates). Only revenue-facing modules are in scope.
- **External billing / Stripe / invoicing integration.** External
  companion project scope; deferred to a dedicated arc if Chris
  wants it.
- **Frontend UI redesign of revenue dashboards.** Group 1400
  Child E documents drift; UI redesign belongs to Frontend arc.
- **Opportunity → Initiative wiring implementation.** Design-
  preparation phase, not this arc.
- **Sports/DBAO island-vs-integrated resolution.** Deferred to
  Group 1500.
- **Group 1600 Content Pipeline reviewer-chain integration
  audit** (whether outreach composition uses the deliberation
  reviewer chain). Child B verifies whether it's used; Group
  1600 owns the reviewer-chain audit itself.
- **Full governance-domain audit** (added Rigby Light SIGN cycle
  1 nice-to-have #5). Governance is reviewed **only** as an
  integration seam that gates revenue actions — autonomy toggles,
  kill-switch state, policy mode gating on
  `EngagementAutonomyEngine` / `ClosePackAutonomyEngine`. NOT a
  full audit of §3.23 Governance surfaces. Governance-domain
  refactor belongs to a dedicated arc (deferred, no queue slot
  yet).
- **Deep sports strategy / integration work** (added Rigby Light
  SIGN cycle 1 nice-to-have #6 — clarified wording). Group 1400
  Category A will verify **only** whether the revenue pipeline
  depends on `intelligence/sports_opportunity_generator.py`
  outputs (thin seam check + producer/consumer verification). Any
  deeper sports strategy (island vs integrated per S1274 §11.3)
  or DBAO ↔ Revenue full integration work is deferred to Group
  1500.

---

## 8. Decisions recorded (draft — pending Chris ratification)

| ID | Decision | Verdict | Rationale | Lock date |
|---|---|---|---|---|
| D21 | Next-arc launch cadence: (i) Group 1400 default lean; (ii) single-child follow-on; (iii) parallel | **(i) Open Group 1400** | Chris short-command "start research group 1400" at S1400 open | 2026-07-01 (Chris-locked via short command) |
| D22 | Arc pin mint | `pa-34d43795e1b24bd3` minted; title "Session 1400 — Revenue research group (kickoff)" | Fresh thread per playbook §16 arc-open discipline; retired `pa-aa54193f240f4846` (Group 1300 arc pin) via `session_tool.retire force=true` (`updated_count: 29, retired: true, previously_active: true, is_current_bound: false`) | 2026-07-01 (Chris-locked via short command) |
| D23 | Parent-vs-single: is Revenue one audit or a parent arc? | **Proposed: parent-with-children** (see §4) | 17 models across 8 files + 5 UNKNOWNs + 4 S1274 findings + sibling verifier-loop discipline (see §4 5-point rationale) | **PENDING Chris lock** |
| D24 | Child mission sequence order (P1–P6) | **Proposed: A → B → C → D → E → xx99** (see §5) | Bottom-up dependency chain; matches S1301→S1305→S1399 precedent | **PENDING Chris lock** |
| D25 | Income/Jobs adjacency scoping (formerly "FreelanceOpportunity subdomain shape"; reframed after Chris's Phase 0 methodology directive 2026-07-01) | **Chris-locked F.i: create Category F child audit for the full Income/Jobs lane** (9-file `intelligence/` adjacency + `FreelanceOpportunity` + resume/matcher/pipeline surface). Arc = 6 children + xx99 (S1401 A → S1402 B → S1403 C → S1404 D → S1405 E → S1406 F → S1499 xx99). | Rigby cycle 2 confirmed; Chris agree-all round 2 locked | **2026-07-01 (Chris-locked via "agree all" round 2)** |
| D29 | Playbook v3 §11.1 template addition — codify Chris's Phase 0 F.i/F.ii/F.iii three-step framework as mandatory template sections | **Chris-locked Yes-two-triggers: Group 1400 pilots the framework (this doc = first application); playbook v3 promotion at Group 1500 close if second application unchanged.** If Group 1500 requires material modification, framework stays as optional appendix pattern per S1399 two-triggers threshold rigor. | Rigby cycle 2 agrees; matches S1399 close two-triggers precedent | **2026-07-01 (Chris-locked via "agree all" round 2)** |
| D26 | Ops Autopilot cross-cutting boundary | **Proposed: revenue-facing modules only** (outreach_generation, engagement, impact, revenue); cross-cutting Ops Autopilot primitive research is non-candidate | Prevents Group 1400 scope creep into Employee OS + governance surfaces | **PENDING Chris lock** |
| D27 | Group 1400 SIGN routing per playbook §15 | **Proposed: Light SIGN on this parent doc; Full 20-section SIGN on each child audit; Q10–Q13 canonical-summary SIGN on xx99** | Matches S1300 → S1301–S1305 → S1399 arc pattern | **PENDING Chris lock** (Rigby routing gets scheduled after D23 verdict) |
| D28 | Opportunity → Initiative wiring — child ownership assignment (Rigby Light SIGN cycle 1 Must-fix #2) | **Proposed options: (A) Child A owns as core lifecycle/emission contract from Opportunity pipeline into initiative system; (E) Child E owns as attribution/analytics-driven "when to promote to initiative" decisioning + thresholds**. Parent §6.1 still aggregates; one child owns primary evidence collection. | Rigby flagged as Must-fix #2 in cycle 1; needs Chris pick before Child A/E launches | **PENDING Chris lock** |

**Rigby SIGN cycle 1 status (2026-07-01).** SIGN-clean cycle 1 at
Medium confidence. **0 must-fix** after fold notes:

- Must-fix #1 (evidence integrity: `sports_opportunity_generator.py`
  citation) → downgraded to §Appendix Verifier-loop history fold
  note; direct grep confirmed the file exists at
  `intelligence/sports_opportunity_generator.py`.
  Rigby's original tree-tool query was truncated before reaching
  `s*` files.
- Must-fix #2 (child ownership for Opportunity → Initiative
  wiring) → escalated to D28 above; Chris resolves during
  D23–D28 lock.
- 6 nice-to-have items (Category A non-spider producers;
  Category C hypothesis map; Category F Income/Jobs lane
  adjacency; §5 dependency rationale; §7 governance-seam
  anti-scope; §7 sports-seam clarification) — all folded into
  the doc above.

**Chris commit-gate.** Per playbook §16, this parent doc does NOT
commit until D23–D28 are Chris-locked. Rigby's Light SIGN cycle 1
is complete (per Rigby: "Cycle 2 not required unless taxonomy or
sequence changes materially").

---

## 9. Next step

**Post-Chris-methodology-directive execution plan (2026-07-01):**

1. **Rigby Light SIGN cycle 2** on the extended parent doc (v2).
   Cycle 2 scope: (a) do the three new §10/§11/§12 sections
   answer all 12 Chris questions completely? (b) is §12.5
   Revenue Lifecycle Traceability Table concrete enough as
   definition of "done"? (c) does the 6-child arc shape (S1401
   A → S1402 B → S1403 C → S1404 D → S1405 E → S1406 F → S1499
   xx99) hold up given D25 default lean?
2. **Fold Rigby cycle 2 edits** per playbook §14 evidence rules.
3. **Route final v2 to Chris** for D25 explicit ratification +
   Phase 0 methodology addition confirmation.
4. **Chris D25 ratification:** if F.i-default (create Category F
   child audit as S1406) accepted, arc shape locks at 6 children
   + xx99. If Chris picks F.ii or F.iii, arc shape adjusts.
5. **Chris Phase 0 methodology confirmation:** propose to codify
   Chris's F.i/F.ii/F.iii three-step framework as playbook v3
   §11.1 template addition. Per S1399 close two-triggers
   threshold, this needs Group 1500+ to prove out before formal
   promotion. Group 1400 is first application (this doc);
   playbook v3 addition proposal is Group-1400-specific artifact.
6. **Commit parent doc** + rotate `00-START-NEXT-SESSION.md`
   with S1401 mission spec + move `OPEN_ARCS.md` Group 1400 row
   from Not-started → In-progress per playbook §16 commit gate +
   OS §14 completion contract.
7. **Open PR to `main`** for the parent doc + ancillary rotations.
8. **Run docs cascade** (build_docs_index → build_rag_corpus →
   sync_docs_index_to_documents → embed_documents +
   build_docs_provenance) per memory rule
   `feedback_docs_cascade_at_every_close.md`.
9. **Next session (S1401):** launch Child A audit
   (Opportunity Discovery + Scoring) per playbook §13 6-parallel-
   Explore sweep + §11.2 20-section template. Category A must
   answer the questions named at §12.1 Category A row.

---

## 9.5 Playbook v3 §11.1 template addition proposal (Group 1400 methodology contribution)

**Proposal.** Add three mandatory sections to playbook §11.1
parent-scoping template, based on Chris's Phase 0 methodology
directive 2026-07-01:

- **§ Domain Definition** — 5 questions: What is the actual
  architectural domain? What is explicitly in scope? What is
  explicitly out of scope? Does this domain overlap an existing
  research group? Should this be a single audit or a
  parent-with-children structure?
- **§ Existing Knowledge Inventory** — 4 questions: What
  previous research groups already cover parts of this domain?
  What inventory rows already exist? What narratives, handoffs,
  or architecture docs already answer some questions? Which
  findings are inherited rather than rediscovered?
- **§ Success Criteria** — 4 questions + 1 arc-specific
  artifact: What questions must be answered before the domain is
  considered understood? What evidence would change our current
  understanding? What would S1499 need to say for this group to
  be considered complete? Which adjacent research groups are
  explicitly deferred? *Group-specific:* what single artifact
  must exist at xx99 (schema / diagram / table) that gives a
  concrete definition of "done"?

**Rationale.** Chris's directive named the load-bearing gap in
playbook v2 §11.1: no formal Success Criteria section before
child audits launch. Existing template sections (§1–§9) answer
some questions implicitly but scattered. Making the answers
explicit gives Claude + Rigby + Chris a shared definition of
"done" before hours of research are spent.

**Promotion criteria** (per S1399 close two-triggers threshold
adopted 2026-07-01): playbook v3 addition should promote when
2+ arcs apply the framework cleanly. Group 1400 is first
application (this doc). Group 1500 (Sports/DBAO) will likely be
second. Promotion to playbook v3 §11.1 formal template happens
at Group 1500 close if the framework survives its second
application unchanged.

**Interim posture.** Every research group opened between
2026-07-01 and playbook v3 promotion optionally applies the
Chris directive as three named sections (§10/§11/§12 in this
doc's example) or embedded in existing §1–§9. Group 1400 uses
the §10/§11/§12 pattern for clarity.

Fallback: if Chris rejects the playbook v3 proposal (e.g., the
methodology proves too rigid at Group 1500 application), the
three §10/§11/§12 sections in this doc remain as
Group-1400-specific artifacts. No downstream impact.

**Material-modification clause** (added Rigby cycle 2 nice-to-have):
If Group 1500 applies the framework but requires material
modification (e.g., adds a fourth question set, drops one of
Chris's 13 questions, or restructures the section order), the
framework does NOT promote to playbook v3 §11.1. Instead it stays
as an OPTIONAL appendix pattern in the playbook, cited by name
but not mandatory. Promotion requires TWO applications with the
framework unchanged — matches S1399 two-triggers threshold rigor.

---

## 10. Phase 0 F.i — Domain Definition (Chris methodology directive 2026-07-01)

> **What this section is.** A formal answer to Chris's five Phase 0
> Domain Definition questions. Chris's directive at S1400 open
> (via arc pin `pa-34d43795e1b24bd3` immediately after "agree all"
> lock): every research group must answer these five questions
> explicitly before any exploration begins. Proposed as playbook
> v3 §11.1 template addition — Group 1400 is first application.
> Existing §1–§4 content is the source material; this section
> consolidates + locks the answers.

### 10.1 What is the actual architectural domain?

**Group 1400 domain:** the *end-to-end Revenue capability* — the
system-level pipeline that converts spider-sourced opportunities
into revenue via a discovery → outreach → engagement → meeting →
close → attribution lifecycle, plus the Income/Jobs adjacency
(freelance/gig income) as a parallel opportunity lane, plus the
integration seams into upstream domains (Spider Framework §3.8,
Signal Engine §3.9, Content Pipeline §3.11 for outreach LLM
composition, ML Pipeline for scoring) and downstream domains
(Observability §3.25 via `ImpactEvent`, Governance §3.23 via
autonomy toggles as integration seam only, Human Interface §3.16
for meeting-scheduling escalation, Inbox §3.17 for outbound
channel — currently UNKNOWN).

**Concretely, the domain includes:**
- 17 revenue-related Django models across 8 files (§2.4 census).
- 10+ services across `core/services/opportunity_*` +
  `core/services/ops_autopilot/` (revenue-facing modules) +
  `intelligence/opportunity_storage.py` +
  `intelligence/revenue_*` + `intelligence/spider_opportunity_connector.py` +
  `intelligence/sports_opportunity_generator.py`.
- 3 dedicated agents (`OpportunityScoringAgent`,
  `OpportunityPipelineAgent`, `MeetingCoordinatorAgent`).
- 1 WebSocket consumer (`OpportunityScannerConsumer`).
- 1 EventBus event (`OPPORTUNITY_SCORED`).
- 1 Celery beat task (`calculate-daily-revenue-metrics`).
- 3 Django view files (`views_opportunity.py`,
  `views_revenue.py`, `views_revenue_analytics.py`,
  `views_revenue_tracking.py`).
- 4 frontend routes (`opportunity-detail`, `revenue`,
  `revenue-dashboard`, `revenue-opportunities`).
- 1 signal pattern type (`opportunity_window`).
- 1 learning bridge (`revenue_attribution_bridge`).
- Adjacent Income/Jobs lane: 9 files in `intelligence/`
  (`ai_job_matcher.py`, `ai_job_application_pipeline.py`,
  `agent_income_tools.py`, `income_builder.py`,
  `income_builder_automation.py`, `income_builder_connector.py`,
  `income_spider_orchestrator.py`, `job_income_bridge.py`,
  `job_scanner_consumer.py`) + `ai_resume_generator.py` + the
  `FreelanceOpportunity` model at
  `core/models_autonomous_situations.py:352`.

### 10.2 What is explicitly in scope?

Six named subdomains (A–F) plus the parent-level integration frame.
See §3 for the full taxonomy + §5 for child mission sequence.

| Slot | Category | Primary evidence surface |
|---|---|---|
| A | Opportunity Discovery + Scoring | 10 Opportunity models + orchestrator + 2 agents + spider bridges + ML categorizer + WebSocket consumer + EventBus |
| B | Outreach Composition + Delivery | `OutreachDraft` + `OpportunityDraftGenerator` + `OutreachSequencer` + outbound channel (currently UNKNOWN) |
| C | Engagement Inbound | 4 engagement-shape models + `EngagementEngine` + `EngagementAutonomyEngine` |
| D | Meeting + Close | `Meeting` + `ClosePack` + `MeetingCoordinatorAgent` + `MeetingEngine` + `ClosePackAutonomyEngine` + `HumanAttentionItem` boundary |
| E | Revenue Attribution + Analytics | 3 attribution models + `ops_autopilot/revenue.py` + `ops_autopilot/impact.py` + 3 view files + 4 frontend routes + Celery beat + revenue-attribution learning bridge |
| F | Income/Jobs lane | 9-file adjacency in `intelligence/` + `FreelanceOpportunity` model + resume/matcher/application-pipeline surface |

**Cross-cutting scope (parent-level, not child-owned):**

- Cross-domain integration frame per S1274 §2.4: STRONG
  Spider→Opportunity; STRONG Revenue→Observability; MISSING
  Revenue→Initiative; MISSING Revenue→Inbox; MISSING
  Revenue→HumanAttention.
- Ownership / runtime-owner questions per S1274 §14 finding #36
  (HIGH severity).
- Orphan-record integrity design per S1274 §5.10 (LOW severity).

### 10.3 What is explicitly out of scope?

See §7 Anti-scope for the enumerated list. Consolidated summary:

- Implementation PRs (Group 1400 is research + design-preparation
  only per playbook §3 phase discipline).
- Ops Autopilot runtime primitive audit (only revenue-facing
  modules are in scope; cross-cutting primitives deferred to
  Employee OS or dedicated Ops Autopilot arc).
- External billing / Stripe / invoicing integration (external
  companion project scope).
- Frontend UI redesign of revenue dashboards (documented only;
  redesign belongs to Frontend arc).
- Opportunity → Initiative wiring implementation (documented at
  parent §6.1 + Child E owns per D28; ADR deferred to
  design-preparation phase).
- Sports/DBAO island-vs-integrated resolution (Group 1500).
- Content Deliberation reviewer-chain integration audit (Group
  1600).
- Full governance-domain audit (Group 1400 reviews governance only
  as integration seam gating revenue actions).
- Deep sports strategy / DBAO integration (Group 1400 verifies
  seam via `sports_opportunity_generator.py` only; deep work
  deferred to Group 1500).

### 10.4 Does this domain overlap an existing research group?

**Yes — 7 documented overlap points.** All are integration seams,
not scope collisions.

| Overlapping group | Overlap type | Group 1400 posture |
|---|---|---|
| **Group 1300 Memory / Knowledge / Embeddings (closed S1399)** | Learning bridge `revenue_attribution_bridge` writes to UserAgentLearning (S1274 §4.3) | Inherit S1399 F1/F2/F4 methodology; consume learning bridge as read-only integration surface. |
| **Employee OS 1200s (per S1274 §14 finding #36)** | Revenue Pipeline has no runtime owner → JobContract candidate | Child E surfaces ownership recommendation; actual JobContract creation deferred to Employee OS arc. |
| **Group 1500 Sports / DBAO / Intelligence (not started)** | `intelligence/sports_opportunity_generator.py` may bridge sports → mainline Opportunity; DBAO island-vs-integrated question is Group 1500 scope | Child A verifies bridge existence + emission shape; DBAO strategy deferred. |
| **Group 1600 Content / Deliverables / Publishing (not started)** | `OpportunityDraftGenerator` may use Content Deliberation reviewer chain | Child B verifies whether reviewer chain is used; Content Pipeline audit itself is Group 1600. |
| **Group 1700 Observability / Telemetry / SLOs (not started)** | `ImpactEvent` is Revenue→Observability integration surface (STRONG per S1274 §2.4) | Child E documents write/read sites for `ImpactEvent`; broader Observability dedup audit is Group 1700. |
| **Employee OS Cat G Mission Memory (S1399 §9 delegated arc)** | Meeting/Close conversion trigger may cross Mission Memory (`OpsRunEvent` + Employee OS audit trail) | Child D verifies MissionRunner boundary if reached. |
| **Post-1400 design-preparation phase** | 4 ADR/design-prep docs named at S1399 §9 (write-authority framework, provenance-system reconciliation, etc.) may inherit Group 1400 findings | Group 1400 produces evidence + open questions; ADRs are post-arc. |

None of the seven overlaps forces re-scoping. Each is a
cross-arc integration seam handled at parent §6 aggregation +
child-audit integration sections.

### 10.5 Should this be a single audit or a parent-with-children structure?

**Chris-locked verdict: parent-with-children** (D23 ratified via
"agree all" 2026-07-01). See §4 Parent-vs-single recommendation
for the 5-point rationale. See §5 Child mission sequence for
S1401–S1405 + S1499 order (with Category F insertion pending D25
resolution — proposed as S1406).

---

## 11. Phase 0 F.ii — Existing Knowledge Inventory (Chris methodology directive 2026-07-01)

> **What this section is.** A formal answer to Chris's four Phase
> 0 Existing Knowledge Inventory questions. Chris's directive:
> before looking for new findings, cite what's already known so
> we don't rediscover. This section is the "inherit, don't
> rediscover" contract for Group 1400.

### 11.1 What previous research groups already cover parts of this domain?

**Zero completed research groups directly cover Revenue.** Prior
research surfaced Revenue as a domain but did not audit it:

- **S1273 Whole-Platform Architecture Inventory (v2 close 2026-07-01)** —
  first surfacing. Rigby caught the missing domain during SIGN
  review; added as §3.32 with coverage LIGHT + maturity WORKING.
  Named 5 load-bearing UNKNOWNs at §10.3. No child audit followed.
- **S1274 Cross-Domain Integration Audit (close 2026-07-01)** —
  named 4 findings against domain 32: §2.4 integration classes
  (5 rows, 3 MISSING + 2 STRONG); §3.7 MEDIUM severity
  Opportunity→Initiative missing_connection; §5.10 LOW severity
  intentional tight-coupling orphan-record risk; §9.6 LOW
  readiness (research-stage); §14 finding #36 HIGH severity
  unclear_owner (no JobContract, no beat, no queue).
- **S1300–S1399 Group 1300 Memory arc (closed 2026-07-01)** —
  learning bridge `revenue_attribution_bridge` (Revenue →
  UserAgentLearning) noted at S1274 §4.3 as memory integration
  surface. No Revenue-specific finding.

**Zero partial-coverage research groups on Revenue.** Group 1400
is the first arc to audit the domain directly.

### 11.2 What inventory rows already exist?

**Two inventory rows at parent scope:**

- **`platform_architecture_inventory.md` §3.32** — Revenue /
  Outreach / Engagement Pipeline (S1273 v2 Rigby-added row).
  Coverage LIGHT + maturity WORKING; 5 load-bearing UNKNOWNs at
  §10.3. Named entry points, models, services, agents, and open
  questions.
- **`platform_architecture_inventory.md` §4.9** — end-to-end
  cross-domain flow: Spider → Opportunity → Outreach →
  Engagement → Meeting → ClosePack → Revenue → ImpactEvent (S1273
  v2 Rigby-added flow row).

**Runtime-derived rows (`PLATFORM_INVENTORY.md` 2026-06-22 snapshot):**

- 17 revenue-related models listed at §Database Models rows
  (Opportunity + 9 Opportunity variants + Outreach + 4
  Engagement variants + Meeting + ClosePack + FreelanceOpportunity).
- 3 agents at §Agents (MeetingCoordinatorAgent,
  OpportunityPipelineAgent, OpportunityScoringAgent).
- 1 Celery beat task at §Beat Schedule
  (`calculate-daily-revenue-metrics`).
- 4 view files + 4 frontend routes + 1 signal pattern type
  (`opportunity_window`).

### 11.3 What narratives, handoffs, or architecture docs already answer some questions?

**Narratives (partial coverage, treat as design context):**

- `docs/architecture/partnership_model.md` — partnership
  positioning; adjacent to Revenue Attribution + Category E.
- `docs/plans/MASTER_PLAN_CREATIVE_INTELLIGENCE_EMPIRE.md` —
  aspirational-heavy per S1273 §3.32 note; treat as design
  context, not runtime.
- `docs/reports/DECISION_COMMAND_IMPLEMENTATION_REPORT.md` —
  Decision Command surface adjacent to opportunity workflow.
- `external-project-docs/ai-content-studio/architecture/BILLING_MONETIZATION_SYSTEM.md` —
  external companion project; treat as external design context.

**Handoffs (partial coverage, cite selectively):**

- `docs/archive/handoffs-pre-800/SESSION_263_SUPER_PLATFORM_INTEGRATION_BLUEPRINT.md` —
  early integration blueprint; adjacent.
- No handoff dedicated to Revenue architecture.

**Architecture docs:**

- **No CANONICAL topic doc exists for Revenue** (S1273 §3.32
  explicit flag). Missing per playbook §22 rationale. Group 1400
  itself produces the first CANONICAL topic doc via S1499 xx99
  canonical summary.

### 11.4 Which findings are inherited rather than rediscovered?

**Inherited findings (do not rediscover; cite instead):**

| Finding | Source | Group 1400 posture |
|---|---|---|
| Revenue domain exists as a coherent architectural unit | S1273 §3.32 (Rigby SIGN caught) | Confirmed at F.i above; no audit needed. |
| Spider → Opportunity integration is STRONG | S1274 §2.4 line 290 | Confirmed; Child A verifies emission shape only. |
| Revenue → Observability is STRONG via ImpactEvent | S1274 §2.4 line 292 | Confirmed; Child E documents write/read sites. |
| Revenue → Initiative is MISSING | S1274 §2.4 line 291 + §3.7 MEDIUM | Confirmed; Child E owns primary evidence collection (D28); parent §6.1 aggregates. |
| Revenue → Inbox is MISSING (outbound channel UNKNOWN) | S1274 §2.4 line 293 | Confirmed; Child B resolves whether "MISSING" = "not wired" or "wired via non-Inbox path." |
| Revenue → HumanAttention is MISSING | S1274 §2.4 line 294 | Confirmed; Child D verifies at Meeting/Close boundary. |
| Sports/DBAO → Opportunity is MISSING | S1274 §2.4 line 270 | Confirmed; Child A thin seam check on `sports_opportunity_generator.py` only. |
| Outreach/Engagement/Meeting/Close tight coupling is INTENTIONAL (LOW risk) | S1274 §5.10 | Confirmed; Child D produces integrity audit design (not implementation). |
| Revenue Pipeline has no runtime owner (HIGH severity) | S1274 §14 finding #36 | Confirmed; Child E surfaces ownership recommendation. |
| Learning bridge `revenue_attribution_bridge` writes Revenue → UserAgentLearning | S1274 §4.3 | Confirmed; Child E documents read/write sites. |
| Revenue Pipeline extraction readiness is LOW | S1274 §9.6 | Confirmed; Group 1400 output can update readiness rating. |
| S1399 F1 (provenance-filter drift) methodology | S1399 §4 F1 | Inherited as diagnostic lens for Children A/B/C/D/E/F. |
| S1399 F2 (row-level orphan-write pattern) methodology | S1399 §4 F2 | Inherited as diagnostic lens; especially likely in 17-model + 10-Opportunity-variant surface. |
| S1399 F3 (Redis-only durability + `@lru_cache` staleness) methodology | S1399 §4 F3 | Inherited as diagnostic lens; Categories C/D/E should probe. |
| S1399 F4 (CANDIDATE + severity-correction discipline as inheritance methodology) | S1399 §4 F4 | Inherited as SIGN methodology across children. |

**Total inherited: 15 findings.** Group 1400 does not
rediscover any of these; each child audit's §20 Appendix cites
the source when the finding surfaces in its own investigation.

---

## 12. Phase 0 F.iii — Success Criteria (Chris methodology directive 2026-07-01)

> **What this section is.** A formal answer to Chris's four Phase
> 0 Success Criteria questions. Chris's directive: before
> launching the first child audit, define what "done" means so
> Claude and Rigby share a definition of completion before hours
> of research are spent. Group 1400 completion = S1499 xx99
> canonical summary + these criteria satisfied.

### 12.1 What questions must be answered before the domain is considered understood?

**Category-level questions (each child audit answers its share):**

- **Category A must answer:** What IS an Opportunity (10 variants;
  authoritative schema)? Who produces Opportunities (all
  producers, not just spiders)? How does scoring flow through
  `OpportunityScoringAgent` + `OpportunityPipelineAgent` + ML
  categorizer? What does `OPPORTUNITY_SCORED` event carry + who
  consumes? What is `OpportunityScannerConsumer` for? Does
  `sports_opportunity_generator.py` produce into mainline
  Opportunity or a separate lane?
- **Category B must answer:** How does `OpportunityDraftGenerator`
  compose outreach (single-shot LLM vs Content Deliberation
  reviewer chain)? Where does outreach actually get SENT (email?
  LinkedIn? Discord? Rigby DM?) — resolves S1273 §10.3 UNKNOWN #2.
  How does `OutreachSequencer` scheduling work?
- **Category C must answer:** Which of the 4 engagement models is
  canonical (`EngagementEvent`, `EngagementMetrics`,
  `OpportunityInteraction`, `ContentEngagement`)? What is the
  event stream vs aggregate axis (§3 Category C hypothesis map)?
  What does `EngagementAutonomyEngine` gate + what is the
  default state?
- **Category D must answer:** When does an EngagementEvent trigger
  a Meeting (auto vs manual)? How is ClosePack assembled +
  triggered — resolves S1273 §10.3 UNKNOWN #3. Where does
  HumanAttention interlock (approval-required conversion) —
  resolves S1274 §2.4 line 294 MISSING. What does the integrity
  audit design look like (S1274 §5.10 orphan-record risk)?
- **Category E must answer:** What is the revenue attribution
  algorithm (`ops_autopilot/revenue.py`) — resolves S1273 §3.32
  UNKNOWN drift. How does `ImpactEvent` emission work (write/read
  registry) — resolves S1274 §2.4 STRONG classification. How do
  4 frontend routes + 3 view files serve distinct vs overlapping
  needs? What is the runtime owner recommendation (resolves
  S1274 §14 finding #36 HIGH)?
- **Category F must answer:** Is the Income/Jobs lane
  (`FreelanceOpportunity` + 9-file `intelligence/` adjacency)
  actively driving income or dormant? Who produces
  FreelanceOpportunity rows? What is `income_builder_automation`
  + `income_spider_orchestrator` + `job_income_bridge` doing at
  runtime? Is `ai_resume_generator` production-invoked?

**Parent-level questions (S1499 xx99 answers):**

- Which of the 15 inherited findings from S1274 changed under
  child-audit evidence (CONFIRMED / CANDIDATE / DOWNGRADED /
  RESOLVED)?
- What are Revenue's F1/F2/F3/F4 diagnostic-lens hits (S1399
  methodology inheritance)?
- What integration seams did children discover that S1274 didn't
  name?
- What is the arc-wide runtime owner recommendation (aggregating
  Child E's proposal + Category F's income-lane ownership)?
- What are the D23–D28 + post-D28 decisions that need Chris lock
  before Group 1400 → post-arc design-preparation phase?

### 12.2 What evidence would change our current understanding?

Group 1400's mental model at Phase 0 is grounded in inherited
findings (§11.4) + inventory rows (§11.2). Evidence classes that
would change our understanding:

- **Owner-model-qualified consumer inventory** (per S1301 §14 D3
  + S1304 §19 R1 methodology). If any inherited "STRONG" or
  "MISSING" classification is overturned by a full consumer walk
  (e.g., Revenue → Inbox turns out to be wired via a non-Inbox
  outbound path we didn't name), Group 1400 updates S1274.
- **Runtime telemetry from `CeleryTaskEvent` / `LLMCallEvent` /
  `ImpactEvent` write history** (per S1245 audit_celery_zero_fire
  methodology). If any pipeline component has zero
  telemetry hits in 30d, it's dormant regardless of code
  presence. Group 1400 downgrades maturity accordingly.
- **F2 orphan-write pattern application** (per S1399 §4 F2
  methodology). Any Opportunity field written by ≥3 sites and
  read by ≤1 producer-model context is a candidate F2 finding.
- **F1 provenance-filter drift application** (per S1399 §4 F1
  methodology). Any writer/reader provenance-tag mismatch across
  the 17 revenue models is a candidate F1 finding.
- **Rigby SIGN pressure-tests per child audit** (per playbook
  §15 stage table). Each SIGN cycle can overturn a child's
  finding severity, hypothesis, or scope.
- **Cross-child verifier-loop findings** (per S1399 §4 F4
  methodology). Any sibling audit hypothesis contradicting a
  prior child audit is a candidate CANDIDATE → CONFIRMED
  decision at S1499 §5 resolved contradictions.

### 12.3 What would S1499 need to say for this group to be considered complete?

**S1499 xx99 canonical summary completion criteria** (mirrors
S1399 §17 playbook §17 graduation criteria):

1. **All 6 child audits SIGN-clean** (S1401 A, S1402 B, S1403 C,
   S1404 D, S1405 E, S1406 F — per D25 lock).
2. **All 6 audits committed to `main`** with matching handoffs.
3. **Cross-cutting patterns named** at S1499 §4 (F1–F4 hits +
   any new F5+ patterns Group 1400 surfaces).
4. **Consolidated Revenue domain shape delivered** at S1499 §3
   as a single map/diagram (see §12.5 traceability artifact
   below).
5. **Resolved contradictions between siblings** at S1499 §5 with
   canonical verdict + rationale.
6. **Unresolved unknowns explicitly named** at S1499 §6 and
   promoted to §8 follow-on queue.
7. **Anchor-update recommendations proposed** at S1499 §7 for:
   `platform_architecture_inventory.md` §3.32 + §4.9;
   `PLATFORM_INVENTORY.md`; `PLATFORM_WHAT_IT_IS.md`;
   `ARCHITECTURE_INDEX.md`; a new CANONICAL topic doc
   `docs/topics/revenue-pipeline.md` (S1273 §3.32 gap fill).
8. **Follow-on research queue ranked** at S1499 §8 by
   uncertainty × risk × unblocked flows.
9. **Cross-links to delegated arcs** at S1499 §9 for: Group 1500
   Sports/DBAO integration ADR; Group 1700 Observability
   ImpactEvent dedup; Employee OS 1200s Revenue Pipeline
   JobContract; post-arc Opportunity→Initiative ADR; post-arc
   revenue-attribution algorithm ADR.
10. **Meta-methodology §10** per playbook §11.3 (adopted S1399
    close 2026-07-01) — what Group 1400 taught the library about
    how to do research. Second application of the meta-
    methodology template; first application was S1399 itself.
11. **Arc Change Log §11** — which child, which session, which
    Rigby verdict, which fold edits.
12. **Provenance appendix §12** — every child's file path,
    evidence provenance, verifier-loop history.
13. **Rigby SIGN Q10–Q13 cleared** on canonical summary.
14. **Chris commit-gate.**

### 12.4 Which adjacent research groups are explicitly deferred?

Per §10.4 overlap table + §7 anti-scope, the following adjacent
arcs are explicitly deferred:

- **Group 1500 Sports/DBAO/Intelligence** — deep sports strategy
  + DBAO island-vs-integrated resolution.
- **Group 1600 Content/Deliverables/Publishing** — Content
  Deliberation reviewer-chain integration audit.
- **Group 1700 Observability/Telemetry/SLOs** — ImpactEvent
  dedup + broader Observability layer audit.
- **Employee OS 1200s** — Revenue Pipeline JobContract creation
  + Mission Memory boundary.
- **Post-1400 design-preparation phase** — Opportunity →
  Initiative wiring ADR; revenue-attribution algorithm ADR;
  runtime-owner JobContract ADR; orphan-record integrity task
  ADR; write-authority framework (from S1399 §9 delegation).

### 12.5 Group-1400-specific F.iii artifact requirement (Rigby cycle 2 addition)

**Rigby's F.iii pressure-test question (added Light SIGN cycle 2
2026-07-01):**

> *"What single artifact (schema/diagram/table) must exist at
> S1499 that lets us trace lead → opportunity → outreach →
> engagement → meeting → close → revenue received → attribution
> with named models/services and at least 3 verified writer/reader
> paths?"*

**S1499 must produce a single Revenue Lifecycle Traceability
Table** meeting all these criteria:

- Rows: each stage in the lead → attribution lifecycle (minimum 8
  stages).
- Columns per stage: (a) model(s) with file:line, (b) service(s)
  producing rows with file:line, (c) service(s) consuming rows
  with file:line, (d) event(s) emitted with file:line, (e) event
  consumer(s) with file:line, (f) F1/F2/F3/F4 diagnostic-lens
  hits (or explicit "clean" verdict).
- At least 3 verified writer/reader paths per stage (matches S1274
  §14.3 D3 verifier-loop density requirement).
- Cross-child sibling verification per S1399 F4 (any hypothesis
  contradicting a sibling gets called out in §5 resolved
  contradictions).

**Row example template** (added Rigby cycle 2 nice-to-have — prevents
S1499 bikeshedding on formatting + convergence between children):

| Stage | Model(s) file:line | Producer service(s) file:line | Consumer service(s) file:line | Event(s) emitted file:line | Event consumer(s) file:line | F1/F2/F3/F4 lens verdict |
|---|---|---|---|---|---|---|
| Stage 3 (example): Outreach composition | `core/models_outreach.py:18 OutreachDraft` | `ops_autopilot/outreach_generation.py:92 OpportunityDraftGenerator.generate:120` (writes OutreachDraft rows); `ops_autopilot/revenue.py:605 OutreachSequencer.enqueue:640` (schedules sends) | *(TBD by Child B: send-side service that reads pending OutreachDraft rows and dispatches to outbound channel)* | *(TBD: does OPPORTUNITY_OUTREACHED or similar exist?)* | *(TBD)* | F2 candidate lens: check whether any OutreachDraft field is written by ≥3 sites and read by ≤1 |

The Traceability Table is the **concrete definition of "done"**
for Group 1400 per Chris's F.iii directive. If S1499 ships
without it, the arc is not complete.

---

## Appendix — Frontmatter provenance

This doc's frontmatter cites the following provenance chain:

- **Source-of-truth chain for the domain**:
  `PLATFORM_INVENTORY.md` (2026-06-22 snapshot at `554a41d3`) →
  `PLATFORM_WHAT_IT_IS.md` (narrative) → child-scoped topic docs
  (none exist yet for Revenue — flagged as S1273 §3.32 tech
  debt).
- **Source-of-truth chain for the process**:
  `DOMAIN_RESEARCH_PLAYBOOK.md` (v2 S1276) §11.1 parent template
  + §22 queue row for Group 1400 → `RESEARCH_OPERATING_SYSTEM.md`
  (S1278) arc-open contract → `OPEN_ARCS.md` (2026-07-01 post-
  S1399 close) Not-started queue row for Group 1400.
- **Source-of-truth chain for the priors**:
  `platform_architecture_inventory.md` §3.32 + §4.9 (S1273 v2
  Rigby-added rows) → `cross_domain_integration_audit.md` §2.4 +
  §3.7 + §5.10 + §9.6 + §14 finding #36 (S1274) →
  `1300_memory_domain_scoping.md` (S1300 parent exemplar) +
  `1399_memory_canonical_summary.md` (S1399 xx99 exemplar +
  methodology inheritance).
- **Evidence density**: every §2.4 model/service/agent bullet
  cites a verified file:line at current `main` HEAD (post-
  S1399 merge PR #2781 = `6318787b`; latest commit at doc write
  time = `4b3719d4` from PR #2785 docs-cascade artifacts
  refresh). No aspirational citations; every file:line was
  grep-verified.
- **Verifier-loop history at Phase 0**:

  **Rigby Light SIGN cycle 1 fold notes (2026-07-01):**

  1. **Must-fix #1 false positive — `sports_opportunity_generator.py`
     citation.** Rigby's cycle 1 tree-tool query
     (`repo_tool tree='intelligence' depth=2`) was truncated
     before reaching `s*` files, causing a "file not found"
     verdict. Direct grep-based re-verification
     (`repo_tool search='sports_opportunity_generator'` returned
     `intelligence/sports_opportunity_generator.py:160` with a
     concrete match) confirmed the file exists. **Verifier-loop
     methodology:** when a directory-tree tool returns "not
     found," escalate to grep-based verification before treating
     it as a must-fix. Applies to any future Group 1400 child
     audit + generalizes to all research-library evidence
     verification.

  2. **Must-fix #2 escalated to D28.** Rigby correctly flagged
     that P6.1 (Opportunity → Initiative wiring) needed a single
     accountable child owner rather than remaining diffuse at
     parent §6. Rather than pick unilaterally, escalated to
     D28 (options A: Child A owns; E: Child E owns; parent §6
     aggregates).

  **Rigby final verdict:** SIGN-clean cycle 1 at Medium
  confidence, 0 must-fix after fold, cycle 2 not required
  unless taxonomy or sequence changes materially. All 6
  nice-to-haves folded into §3 A/C/F + §5 + §7.
