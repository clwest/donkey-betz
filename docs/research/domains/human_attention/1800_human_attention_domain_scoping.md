---
title: "S1800 HumanAttention / Feedback / Learning — Parent Architecture Scoping (Group 1800 mission plan)"
status: active (Chris D-decisions D75 D76 D77 D78 D79 D80 all locked at default lean (a) via "agree all" ratification round 2026-07-03; no Rigby light SIGN routed per Chris choice — parent scoping row §15 stage-table default is "optional light SIGN"; Chris skipped SIGN this round)
authority: parent-doc for Group 1800 research arc + FIFTH application of Chris's Phase 0 3-step methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) — playbook v3 §11.1 template promotion CONFIRMED-STRENGTHENED via S1700 fourth-application (Rigby SIGN Q3 F5 correlation-primitive HYPOTHESIS box fold codification-candidate at S1799 §10.2 MC-3); this arc applies methodology unchanged for five-consecutive-application confirmation + adopts D62 = (a) 6-sibling exemplar mini-schema propagation-upfront pattern per S1599 §10.2 codify-ready candidate (extended by S1699 + S1799)
category: parent_scoping
session: 1800
date: 2026-07-03
decisions_locked: 2026-07-03 (D75 D76 D77 D78 D79 D80 all Chris-ratified via "agree all" round; no Rigby light SIGN routed; no D-verdict override or edit required)
domain_slug: human_attention
research_group: 1800
authors: Claude Code (Chris directed via short command "merge it and start 1800" at S1800 open post PR #2850 merge; interpretation: Group 1800 open per OPEN_ARCS Not-started queue row = HumanAttention / Feedback / Learning "Round-trip learning loop scope expansion")
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                     # process — §11.1 template applied here for the fifth time
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                             # OS — arc-open contract §8.1
  - docs/research/OPEN_ARCS.md                                                    # arc manifest — Group 1700 → Group 1800 handoff
  - docs/research/ARCHITECTURE_INDEX.md                                            # v50 → v51 bump owed at S1800 close (§1.54 registration)
  - docs/research/domains/observability/1799_observability_canonical_summary.md   # prior arc close (Group 1700 Observability xx99 — 2070 lines; §10 meta-methodology FIFTH application; MC-1 + MC-2 CODIFICATION-READY)
  - docs/research/domains/content/1699_content_canonical_summary.md               # fourth xx99
  - docs/research/domains/sports/1599_sports_canonical_summary.md                 # third xx99
  - docs/research/domains/revenue/1499_revenue_canonical_summary.md               # second xx99
  - docs/research/domains/memory/1399_memory_canonical_summary.md                 # first xx99 — DEEP prior coverage of AgentMemory + AgentKnowledgeSource + UserAgentLearning
  - docs/research/platform/cross_domain_integration_audit.md                      # S1274 §4.7 canonical round-trip Human → HAI → FeedbackProcessor → Learning; §3.3 CRITICAL Failure Cluster → HAI gap; §3.8 MEDIUM Signal Pattern → HAI gap; 5+ cross-domain HAI-consumer gaps catalog
  - docs/research/platform_architecture_inventory.md                              # S1273 §3.16 HumanAttention row (WORKING, MODERATE coverage) + §3.13 Memory row (STABLE, DEEP coverage — closed at S1399); §4.7 canonical round-trip; F5 HumanPreference topic_weights/source_weights never-saved bug
  - docs/research/governance_authority_evolution.md                                # S1269 governance/authority audit — human plane inventory + F5 finding
  - docs/PLATFORM_INVENTORY.md                                                    # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                                   # narrative anchor
scope: Phase 0 domain-definition — decide whether Group 1800 is a single canonical audit or a parent-with-children research arc; produce candidate subdomain taxonomy grounded in verified runtime surface; propose child mission sequence for Chris to lock; frame (do NOT decide) the analog D65/D74-load-bearing question — **"Is the human-in-the-loop attention queue the canonical learning-signal aggregation surface, OR are learning bridges autonomous domain-specific consumers that bypass HAI?"** — as the arc's lens question owed to xx99 canonical summary as evidence plan, not recommendation
non_goals:
  - the audit itself (that begins after Chris picks parent-vs-single + locks §5 sequence)
  - answering the 28 playbook canonical questions (that is the audit's job)
  - resolving the load-bearing round-trip-canonicalization posture at Phase 0 (requires child evidence sweeps; posture-decision framing + evidence plan only — Chris gates actual selection post-arc after xx99 evidence lands)
  - any implementation proposal (this is scoping, not architecture design)
  - Memory / Knowledge / Embeddings internal correctness (delegated to Group 1300 Memory arc closed at S1399; AgentMemory + AgentKnowledgeSource + UserAgentLearning internals are Memory scope)
  - HumanPreference F5 topic_weights/source_weights never-saved bug fix (Cat D catalog only; fix is post-arc T-slot per playbook §14.5 no-implementation)
  - S746 verification_outcome trigger-point identification implementation (Cat E catalog only; fix is post-arc T-slot)
  - Learning-bridge deprecation decisions (Cat C catalogs; deprecation is post-arc T-slot per parent §6)
  - Frontend Command Center / Boardroom UI redesign (out-of-scope; production surface)
delegates_to:
  - Group 1300 Memory arc (closed at S1399; AgentMemory + AgentKnowledgeSource + UserAgentLearning internals delegated; Cat C learning-bridge WRITERS are Group 1800 scope but learning-bridge OUTPUT consumers land in Group 1300 territory when they hit AgentLearning/UserAgentLearning models)
  - Group 1500 Sports arc (closed at S1599; SportsBettingLearningBridge outputs to sports pipeline are Sports domain; Group 1800 audits the bridge writer contract, not sports business logic)
  - Group 1600 Content arc (closed at S1699; ContentPipeline learning-bridge integrations for content generation are Content domain scope; Group 1800 audits the bridge writer contract, not content deliberation logic)
  - Group 1700 Observability arc (closed at S1799; AgentExecutionLearningLoop is Cat C S1703 territory for observability signals; Group 1800 audits the bridge writer contract, not observability internals)
  - Group 1900 Event Architecture (future; downstream of S1274 §11.1 EventBus adoption; HAI-adjacent event routing / schema versioning is Group 1900 scope; Group 1800 catalogs producer-side telemetry contract completeness for HAI events but does NOT own cross-domain routing)
  - Employee OS (concurrent, not a separate arc — MissionRunner + AIEmployee + JobContract may create HAI escalations per S1705 F8; Group 1800 audits HAI writer contract from mission escalation, not mission internal correctness)
delegated_from:
  - S1273 §3.16 HumanAttention row (WORKING coverage-tier baseline + F5 HumanPreference bug + S746 verification loop partial)
  - S1273 §4.7 canonical Human → HAI → FeedbackProcessor → Learning round-trip narrative (ONLY round-trip w/ learning per §2.5)
  - S1274 §3.3 CRITICAL Failure Cluster → HumanAttentionItem cross-domain integration gap + §3.8 MEDIUM Signal Pattern → HAI gap + Body Systems / Signal Engine / Revenue Pipeline / Observability all MISSING HAI-consumer integrations
  - S1269 governance_authority_evolution audit — human plane inventory + F5 HumanPreference finding
  - S1399 Memory canonical summary (first xx99; AgentLearning + UserAgentLearning + AgentKnowledgeSource covered; learning-bridge OUTPUTS territory)
  - S1699 Content canonical summary (fourth xx99; RAG-SCOPE + PA-tool learning bridge)
  - S1799 Observability canonical summary (fifth xx99; §10 MC-1 + MC-2 CODIFICATION-READY; §4.6 CX-P6 consumer-partial-wiring systemic pattern applies here; F5 correlation-primitive HYPOTHESIS box discipline candidate for MC-3 second application at S1800 parent scoping)
owner: claude (Chris directed at S1800 open via short command "merge it and start 1800"; D75-D80 pending ratification)
verifier_loop: |
  Chris ratifies D75-D80 verdicts via "agree all + SIGN" round OR per-verdict override + optional Rigby light SIGN pressure-test pre-lock per playbook §15 stage-table parent row.
  Load-bearing claims verified pre-Explore via file:line direct read before firing sub-agents:
    - HumanAttentionItem model at `core/models_human_interface.py:20-227` (confirmed; 8-state lifecycle + verification loop S746 fields)
    - HumanFeedbackRecord at `:230-266` (confirmed)
    - HumanPreference at `:268-358` (confirmed; F5 topic_weights/source_weights bug catalogued)
    - HumanAttentionLifecycleService at `core/services/human_attention_lifecycle.py:36-728` (confirmed; auto-escalate ladder LOW 72h → MEDIUM 48h → HIGH 24h → CRITICAL auto-dismiss 3d; beat `process_human_attention_lifecycle` every 10 min)
    - FeedbackProcessor at `core/models_feedback_processing.py:122-180, 216-330` (confirmed via S1273 §3.16 cite; classifies HumanFeedbackRecord positive/negative post_save → creates AgentLearning + LearningInsight)
    - HumanInterfaceService at `core/services/human_interface_service.py:295-353, 738` (confirmed; record_decision() writes HAI + HumanFeedbackRecord + triggers ML feedback)
    - LearningBridge abstract at `core/learning_bridges/base.py:13` (confirmed via grep)
    - 10+ concrete LearningBridge subclasses: PersonalizationFeedbackLoop (`personalization_bridge.py:69`) + SpiderDataLearningLoop (`spider_data_bridge.py:27`) + CollaborationLearningLoop (`collaboration_bridge.py:23`) + AdvisorFeedbackLearningLoop + AutoConsultationLearningLoop (`advisor_feedback_bridge.py:50, 250`) + ApplicationOutcomeLearningLoop (`application_outcome_bridge.py:34`) + AgentExecutionLearningLoop (`agent_execution_bridge.py:24`) + SportsBettingLearningBridge (`sports_betting_bridge.py:30`) + RevenueAttributionLearningLoop (`revenue_attribution_bridge.py:31`) (grep-verified; 9 subclasses in core/learning_bridges/ + 2 external in ai_core/intelligence/{reddit,bluesky}_learning_bridge.py)
    - AgentLearning model at `core/models_unified_system.py:3655` (confirmed via grep; Group 1300 Memory domain territory per S1399)
    - UserAgentLearning at `:3912` (confirmed; per-user per-agent adaptive; Group 1300 territory)
    - AgentLearningConnection at `:630` (confirmed)
    - LearningInsight at `ai_core/intelligence/learning_loop.py:92` (confirmed via grep; intelligence-app dataclass)
    - S1274 §4.7 "only round-trip w/ learning" claim verified via cross_domain_integration_audit.md line 328 grep
    - S1274 §3.3 CRITICAL failure-cluster → HAI gap verified at line 438-447 grep
    - S1274 §3.8 MEDIUM signal-pattern → HAI gap verified at line 526-539 grep
  Rigby light SIGN cycle 1 optional per playbook §15 stage-table parent row (Chris ratifies per §22 default lean; typical S1400/S1500/S1600/S1700 precedent = light SIGN routed on 4 pressure-test questions with 3-4 folds landing pre-commit).
methodology_ratifications:
  - Playbook §11.1 parent template FIFTH application (S1400 Revenue first + S1500 Sports second + S1600 Content third + S1700 Observability fourth + S1800 HumanAttention/Feedback/Learning = fifth)
  - Playbook §11.3 §10 meta-methodology template FIFTH application at S1799 xx99 close (CODIFICATION-READY-STRENGTHENED-EVEN-FURTHER; playbook v3 promoted-rule anticipated at S1800 close if fifth-consecutive confirms durable)
  - D48 preemptive stability-probe gate 25th arm start on fresh arc pin `pa-ae5931ea706b4537` (19-consecutive-fully-clean-arms sub-pattern S1503+…+S1706+S1799 CONFIRMED per single-batch-4-question criterion at S1799 close; 20th anticipated at S1800 parent-scoping SIGN if Chris routes light SIGN)
  - Playbook §14 verifier-loop REQUIRED promotion CODIFICATION-READY per S1799 §10.2 MC-1 (pre-Explore + post-Explore discipline is enforced here in this parent doc)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/domains/observability/1799_observability_canonical_summary.md
---

# Session 1800 — HumanAttention / Feedback / Learning Domain Taxonomy Proposal (Phase 0)

> **What this doc is.** A scoping deliverable produced *before* any
> HumanAttention / Feedback / Learning domain audit begins. Chris
> typed the short command "merge it and start 1800" at S1800 open
> post PR #2850 merge — the D-launch verdict per OPEN_ARCS
> Not-started queue row for Group 1800 = "HumanAttention / Feedback
> / Learning — Round-trip learning loop scope expansion" + Chris
> D-override of playbook §22 default queue lean (which pointed at
> Group 1900 Event Architecture per Group 1700 xx99 §9.1 handoff).
> This doc opens the arc by (a) recording the six proposed
> Chris-ratified verdicts D75-D80 (pending ratification), (b)
> demonstrating from verified runtime evidence that HumanAttention /
> Feedback / Learning is larger than any single audit view captures
> — a **five-parallel-surface layer** (`HumanAttentionItem` core +
> `FeedbackProcessor` + 10+ `LearningBridge` subclasses +
> `HumanPreference` personalization + S746 verification loop) plus
> adjacent cross-arc handoffs (Memory / Sports / Content /
> Observability / Employee OS) + 5+ CRITICAL/MEDIUM cross-domain
> HAI-consumer integration gaps (per S1274 §3.3 + §3.8 + §5+ MISSING rows).

## 1. Why Phase 0

Chris's Phase 0 methodology is now on its **fifth application** (after
S1400 Revenue + S1500 Sports + S1600 Content + S1700 Observability).
Playbook v3 §11.1 template promotion was CONFIRMED-STRENGTHENED at S1799
xx99 close via §10.2 MC-1 (playbook §14 verifier-loop REQUIRED promotion)
+ MC-2 (18-consecutive-fully-clean-arms sub-pattern §15 codification)
BOTH CODIFICATION-READY at fifth-consecutive-application. This arc
applies methodology unchanged for five-consecutive-application confirmation
+ tests whether MC-3 (F5 correlation-primitive HYPOTHESIS box discipline
at parent §5, per S1799 §10.2 CODIFICATION-CANDIDATE) meets two-triggers
threshold via second application at Group 1800 parent scoping.

**Chris's F.i/F.ii/F.iii methodology** (verified durable across four
applications):

- **F.i Domain Definition** — What ARE HumanAttention / Feedback / Learning
  as a bounded domain in this codebase? What are the core primitives
  (models, services, agents, bridges)? What semantic scope is coherent
  vs incoherent?
- **F.ii Existing Knowledge Inventory** — What prior research covers
  this domain? Where are the drift + debt + boundary artifacts already
  documented? What load-bearing questions have prior arcs raised?
- **F.iii Success Criteria** — What does a research-complete arc look
  like? What are the observable outputs Chris ratifies?

## 2. What existing inventory already tells us

### 2.1 S1273 §3.16 HumanAttention row (WORKING, MODERATE coverage)

**Purpose per S1273.** Route agent-generated items requiring human
decision-making (arbitrage signals, approvals, verification, escalations)
with attention queue, urgency levels, and verification feedback loop for
learning.

**S1273 catalog:**
- `HumanAttentionItem` at `core/models_human_interface.py:20-227` — UUID
  PK; source_type/source_id/source_agent; item_type; title/summary/payload;
  urgency (critical/high/medium/low); status (pending/viewed/acted/deferred/
  ignored/expired/watching/verified — **8-state lifecycle**); decision
  (decision, decision_feedback, decided_at, time_to_decision_ms); ML
  context (ml_prediction, ml_confidence, ml_recommendation); verification
  (verification_outcome, verified_at, verification_profit,
  event_completed_at — **S746**). Indexes on (user, status),
  (user, urgency), (source_type), (created_at).
- `HumanFeedbackRecord` at `:230-266` — HAI FK, decision + feedback_text +
  confidence; ML context snapshot; `fed_to_ml` flag.
- `HumanPreference` at `:268-358` — per-user collab policy;
  `topic_weights` / `source_weights` — **NEVER POPULATED (F5 finding,
  governance research §1.4)**.
- `HumanAttentionLifecycleService` at `human_attention_lifecycle.py:36-728`
  — auto-expire/dismiss/escalate/approve; beat
  `process_human_attention_lifecycle` every 10 min; auto-escalate ladder
  LOW(72h) → MEDIUM(48h) → HIGH(24h) → CRITICAL(auto-dismiss 3d).
- `FeedbackProcessor` at `models_feedback_processing.py:122-180, 216-330`
  — classifies HumanFeedbackRecord positive/negative post_save →
  creates `AgentLearning` + `LearningInsight` (**only round-trip with
  learning** per S1274 §2.5).
- `HumanInterfaceService` at `human_interface_service.py:295-353, 738` —
  `record_decision()` writes HAI + HumanFeedbackRecord + triggers ML
  feedback.

**S1273 known drift:**
- HumanPreference `topic_weights` / `source_weights` set locally in
  `update_learned_stats()` but **never saved** (F5).
- `_broadcast_thread_update()` referenced in `views_inbox.py:177` —
  consumer not identified.

**S1273 known technical debt:**
- Two-layer lifecycle (bridge + lifecycle service) not consolidated.
- Verification loop trigger points undocumented (who calls
  `record_verification`?).

### 2.2 S1274 §4.7 canonical round-trip narrative

**The ONLY round-trip with learning at HEAD** per S1274 §2.5:

```
Agent creates HumanAttentionItem(urgency, ml_prediction, source_type)
  → Attention Queue on Command Center / Boardroom
  → User decision via POST /api/human/decisions/<id>/record/
  → HumanAttentionItem.record_decision(decision, feedback, confidence)
  → HumanInterfaceService writes HAI + HumanFeedbackRecord
  → post_save signal → FeedbackProcessor
    → classify positive/negative
    → create AgentLearning + LearningInsight (only round-trip w/ learning)
  → HumanPreference.update_learned_stats() — topic_weights modified
    LOCAL ONLY (NEVER SAVED, F5)
  → S746 verification loop: event completes → record_verification(outcome, profit)
```

**Domains involved:** HumanAttention (16), Frontend (18 — Boardroom +
CommandCenter), Memory/Knowledge (13 — AgentLearning), Governance (23
— human plane).

### 2.3 S1274 cross-domain HAI-consumer integration gaps

**CRITICAL and MEDIUM gaps catalog** (per S1274 §3.3 + §3.8 + §5+
MISSING rows):

- **§3.3 CRITICAL Failure Cluster → HumanAttentionItem** — no
  failure-cluster aggregator emits auto-HAI on system state degradation
  (S1273 §3.30 drift; Body Systems reads system states but emits no
  autonomic HAI).
- **§3.8 MEDIUM Signal Pattern Threshold → HumanAttentionItem** — no
  pattern-strength threshold gate for auto-HAI (Agent 3 §2.9);
  high-confidence signal patterns don't auto-escalate.
- **Body Systems (30) → HumanAttention (16) — MISSING** — HeartBeat rows
  accumulated; no consumer; no HAI on IMMUNE/DIGESTIVE degradation.
- **Revenue Pipeline (32) → HumanAttention (16) — MISSING** — no auto-HAI
  when opportunity requires human approval (Agent 3 §2.6).
- **Observability (25) → HumanAttention (16) — MISSING** — no
  failure-cluster aggregator → HAI (Agent 3 §2.3; this Cat E S1705
  named-but-broken analog for observability signals).
- **Signal Engine (9) → HumanAttention (16) — MISSING** — no pattern-strength
  threshold consumer.

**§4.7 STRONG connections at HEAD:**
- HumanAttention (16) → Memory (13) — round-trip learning via FeedbackProcessor.
- HumanAttention (16) → Governance (23) — WEAK (read-only; HAI consumes
  governance state but does not gate governance mode changes).

### 2.4 Learning-bridge surface (grep-verified 2026-07-03)

**10+ LearningBridge subclasses at HEAD:**

`core/learning_bridges/` (9 concrete subclasses):
- `LearningBridge` abstract base (`base.py:13`)
- `PersonalizationFeedbackLoop` (`personalization_bridge.py:69`)
- `SpiderDataLearningLoop` (`spider_data_bridge.py:27`)
- `CollaborationLearningLoop` (`collaboration_bridge.py:23`)
- `AdvisorFeedbackLearningLoop` (`advisor_feedback_bridge.py:50`)
- `AutoConsultationLearningLoop` (`advisor_feedback_bridge.py:250`)
- `ApplicationOutcomeLearningLoop` (`application_outcome_bridge.py:34`)
- `AgentExecutionLearningLoop` (`agent_execution_bridge.py:24`) —
  overlaps Group 1700 Cat C S1703 §10 post_save receiver
- `SportsBettingLearningBridge` (`sports_betting_bridge.py:30`) —
  overlaps Group 1500 Sports arc S1501-1506 territory
- `RevenueAttributionLearningLoop` (`revenue_attribution_bridge.py:31`)
  — overlaps Group 1400 Revenue arc territory

`ai_core/intelligence/` (2 external-domain bridges):
- `RedditLearningBridge` (`reddit_learning_bridge.py:96`)
- `BlueskyLearningBridge` (`bluesky_learning_bridge.py:108`)

**Related learning-signal models + services:**
- `AgentLearning` (`core/models_unified_system.py:3655`) — Group 1300
  Memory territory
- `UserAgentLearning` (`:3912`) — Group 1300 Memory territory
- `AgentLearningConnection` (`:630`)
- `LearningInsight` (`ai_core/intelligence/learning_loop.py:92`) —
  intelligence-app dataclass
- `AgentLearningEvent` (`ai_core/intelligence/models.py:15`)
- `AgentLearningSession` (`ai_core/intelligence/models.py:211`) — deleted
  per S1244 migration 0002 (dead-code candidate)
- `AgentLearningService` (`core/services/agent_learning_service.py:122`)
- `PALearningInsightsService` (`core/services/pa_learning_insights.py:24`)
- `AgentLearningSystem` (`intelligence/agent_learning.py:22`)
- `AgentLearningEngine` (`ai_core/intelligence/agent_learning_engine.py:69`)
- `PersistentLearningEngine` (`ai_core/intelligence/persistent_learning_engine.py`)

**Observation.** Learning surface has **11+ distinct implementations
across 3 apps** (`core/learning_bridges/`, `ai_core/intelligence/`, and
`intelligence/`). This is a **duplicate/overlap SUSPECT surface** per
S1273 §5.13 pattern — one Cat may consolidate this via canonicalization
verdict.

### 2.5 Load-bearing questions for arc lens (D80 candidates)

**The D80-analog arc-lens question** (mirrors S1499 D53 + S1599 D59 +
S1699 D65 + S1799 D74 posture-decision pattern):

> **"Is the human-in-the-loop attention queue (HumanAttentionItem) the
> canonical learning-signal aggregation surface, OR are learning bridges
> autonomous domain-specific consumers that bypass HAI?"**

At HEAD: S1274 §2.5 says HAI → FeedbackProcessor → AgentLearning is the
**ONLY** round-trip w/ learning. But 10+ LearningBridge subclasses
exist independent of HAI (some consume domain signals like sports
outcomes, spider data, agent executions, advisor consultations —
**no human-in-the-loop involvement**).

**Two postures Chris will gate at xx99:**

- **Option A (Canonical Unification):** HAI is the canonical learning
  hub; all learning bridges should route domain signals through HAI
  first (or explicit human-in-the-loop bypass rationale). Implementation
  would require: (i) LearningBridge writer contract must classify
  "requires-human-approval" vs "autonomous" per bridge; (ii)
  autonomous bridges retain autonomy but must emit HAI-shape shadow
  event for governance visibility; (iii) HumanPreference F5 bug fix.
- **Option B (Structural Separability):** HAI is the human-attention
  surface; LearningBridges are autonomous signal consumers with
  independent contracts. Human-in-the-loop is one signal source among
  many. Implementation would require: (i) explicit boundary catalog
  between HAI-mediated and autonomous learning paths; (ii) no unification
  of learning surface; (iii) per-domain governance for autonomous bridges.
- **Option C (Hybrid):** HAI is canonical for approval/verification
  signals; learning bridges are canonical for outcome/attribution signals;
  explicit boundary between "requires-human" and "autonomous" signals
  documented per bridge.
- **Option D (Shared surface):** Both HAI and LearningBridges emit into
  a shared canonical learning-event schema (mirrors S1703 F9 Option C
  shared correlation-view pattern).

**xx99 §5 posture-decision brief consumes P1-P5 evidence + Cat F
evidence plan verbatim per D80 four-option framing.**

### 2.6 F5 correlation-primitive HYPOTHESIS box (per S1799 §10.2 MC-3 CODIFICATION-CANDIDATE second application)

The single most poisoning ambiguity for this arc is **"what is a
learning signal at HEAD?"** If the answer is "any writer to
AgentLearning + UserAgentLearning + LearningInsight," the arc must
audit 11+ bridge + service writers. If the answer is "only outcomes
that update model weights," the arc must audit far fewer. This
subsection names working definitions so each child audit begins with
the same starting premise; each definition is labeled **HYPOTHESIS**
and must be verified/refined by the named child audit.

| Primitive | Working definition (HYPOTHESIS) | Verify at |
|-----------|--------------------------------|-----------|
| **`HAI_item_id`** | `HumanAttentionItem.id` UUID PK — per-attention-item identifier. Written by HAI producer agents (10+ producer sites across signal / revenue / verification paths). **HYPOTHESIS:** HAI_item_id is a per-attention singleton; no downstream model carries `hai_item_id` scalar reference; correlation to FeedbackRecord is via FK (source_type='HumanAttentionItem'). | P1 (Cat A) verifies coverage + producer inventory + retention. |
| **`feedback_record_id`** | `HumanFeedbackRecord.id` — per-feedback-record UUID. Written by `HumanInterfaceService.record_decision()`. Points at HAI via FK. **HYPOTHESIS:** feedback_record_id is the trigger event for FeedbackProcessor post_save signal; classified positive/negative; consumed once then `fed_to_ml=True`. | P2 (Cat B) verifies classifier + fed_to_ml lifecycle + missed-consumption cases. |
| **`learning_event_id` / `agent_learning_id`** | `AgentLearning.id` UUID (Group 1300 territory) — per-learning-event identifier. Written by FeedbackProcessor for HAI round-trip + written by 10+ LearningBridges for autonomous signals. **HYPOTHESIS:** learning_event_id is a cross-source primitive whose provenance (HAI-mediated vs bridge-autonomous) is NOT tagged at schema level. Would need `source_kind` enum to distinguish. | P3 (Cat C) verifies bridge writer inventory + source_kind absence + cross-bridge dedup. |
| **`user_pref_id`** | `HumanPreference.id` — per-user preference row. Written by `update_learned_stats()`. **HYPOTHESIS:** F5 bug — `topic_weights` / `source_weights` set locally but never `.save()`d; verify F5 root cause + downstream consumers (are there ANY readers of topic_weights at HEAD?). | P4 (Cat D) verifies F5 + reader inventory. |
| **`verification_id`** | S746 verification loop primitive on HAI schema. **HYPOTHESIS:** `verification_outcome` + `verified_at` + `verification_profit` + `event_completed_at` fields exist on HAI; but who WRITES them? What triggers `record_verification`? S1273 says trigger points undocumented. | P5 (Cat E) verifies verification triggers + writer inventory + who-calls-record_verification. |

**Load-bearing rule for xx99 §5 posture-decision brief.** If P1-P5
discover HAI is the ONLY producer path for `learning_event_id` at HEAD,
the D80 posture resolves in favor of **Option A canonical unification**
(HAI is canonical). If P1-P5 discover 10+ LearningBridge writers dominate
`learning_event_id` production, structural separability (Option B) is
the defensible default — HAI is one of many. Options C/D emerge if the
mix is roughly even. **xx99 does NOT select the posture; the primitive
evidence gathered by P1-P5 goes into the §5 evidence brief for
Chris-gated ADR post-arc.**

## 3. Candidate subdomain taxonomy

Six subdomain categories A–F proposed for Chris D-verdict D76. Each
has: boundary rule, canonical entry points at HEAD (file:line where
verified), and delegation callouts to prior/concurrent arcs.

### A — HumanAttentionItem core (`HumanAttentionItem` + producers + lifecycle)

**Scope.** The 8-state HumanAttentionItem lifecycle model +
`HumanAttentionLifecycleService` beat-scheduled auto-escalate ladder +
all producer sites that create HumanAttentionItem rows.

**Canonical entry points:**
- Model: `core/models_human_interface.py:20-227` (HumanAttentionItem).
- Service: `core/services/human_attention_lifecycle.py:36-728`
  (HumanAttentionLifecycleService).
- Beat: `process_human_attention_lifecycle` every 10 min.
- Producer sites: grep across `core/` for `HumanAttentionItem.objects.create`
  or `HumanAttentionItem(...)` instantiation (~20+ sites hypothesized per
  S1273 §3.16 + S1274 §3.3 catalog).

**Boundary rule:** Cat A owns the HAI model + lifecycle + producer
inventory. Cat A does NOT own the decision-recording surface (Cat B) or
the FeedbackProcessor classifier (Cat B) or the LearningBridges
(Cat C) or HumanPreference (Cat D) or S746 verification writers (Cat E).

**Load-bearing questions:**
- Q1 (S1273 §3.16 debt): Two-layer lifecycle (bridge + lifecycle service)
  not consolidated. Is `HumanAttentionBridge` at `human_attention_bridge.py`
  the second layer? What are its writers vs the lifecycle service?
- Q2 (S1274 §3.3 gap): Failure-cluster aggregator CRITICAL gap —
  Body Systems / Signal Engine / Revenue / Observability do NOT create
  HAI. Should Cat A catalog which producers SHOULD exist but don't?
- Q3 (S1273 catalog): Is the 8-state lifecycle (pending/viewed/acted/
  deferred/ignored/expired/watching/verified) coverage-complete at HEAD?
  What percentage of HAI rows terminate in each state?
- Q4: Producer coverage completeness — grep + ORM verify all 20+
  hypothesized producer sites at HEAD; are all governance-visible?
- Q5: Retention posture — does HAI have date-based retention? (S1273
  silent; grep-verify at Cat A.)

### B — Feedback processing (`HumanFeedbackRecord` + `FeedbackProcessor` + `HumanInterfaceService.record_decision`)

**Scope.** The decision-recording path from user action through
FeedbackProcessor classification through AgentLearning + LearningInsight
creation. Owns the **canonical round-trip narrative** per S1274 §4.7.

**Canonical entry points:**
- Model: `core/models_human_interface.py:230-266` (HumanFeedbackRecord).
- Service: `core/services/human_interface_service.py:295-353, 738`
  (`record_decision()`).
- Processor: `core/models_feedback_processing.py:122-180, 216-330`
  (FeedbackProcessor + classify_positive_negative + fed_to_ml lifecycle).
- API: `POST /api/human/decisions/<id>/record/`.
- Signal: `post_save` on HumanFeedbackRecord → FeedbackProcessor
  invocation.

**Boundary rule:** Cat B owns HumanFeedbackRecord + FeedbackProcessor +
record_decision path. Cat B does NOT own the HAI model itself (Cat A)
or the LearningBridges (Cat C) or HumanPreference `update_learned_stats`
(Cat D) or S746 verification (Cat E).

**Load-bearing questions:**
- Q1: FeedbackProcessor classifier semantics — how does positive vs
  negative classification decide AgentLearning row creation?
- Q2: `fed_to_ml` lifecycle — under what conditions does a
  HumanFeedbackRecord get `fed_to_ml=True`? What happens if it never
  does?
- Q3: FeedbackProcessor writes to `AgentLearning` (Group 1300 Memory
  territory); Cat B audits the WRITER contract, not the Memory-internal
  correctness. Boundary rule verify.
- Q4: Round-trip completeness — S1274 §4.7 says this is the ONLY
  round-trip with learning; verify at HEAD via grep of FeedbackProcessor
  producer + consumer sites.
- Q5: Retention posture — do HumanFeedbackRecord rows have date-based
  retention? What about `fed_to_ml=False` orphan detection?

### C — Learning bridges (`LearningBridge` abstract + 10+ concrete subclasses)

**Scope.** The 10+ LearningBridge subclasses across 3 apps
(`core/learning_bridges/` + `ai_core/intelligence/` + `intelligence/`)
that consume domain signals (spider outcomes, sports betting outcomes,
agent executions, advisor consultations, application outcomes, revenue
attribution, personalization, collaboration, Reddit/Bluesky external
signals).

**Canonical entry points:**
- Abstract: `core/learning_bridges/base.py:13` (LearningBridge).
- 9 concrete in `core/learning_bridges/`: PersonalizationFeedbackLoop +
  SpiderDataLearningLoop + CollaborationLearningLoop +
  AdvisorFeedbackLearningLoop + AutoConsultationLearningLoop +
  ApplicationOutcomeLearningLoop + AgentExecutionLearningLoop +
  SportsBettingLearningBridge + RevenueAttributionLearningLoop.
- 2 external-domain in `ai_core/intelligence/`: RedditLearningBridge +
  BlueskyLearningBridge.
- Services: AgentLearningService (`core/services/`), PALearningInsightsService,
  AgentLearningSystem (intelligence app), AgentLearningEngine +
  PersistentLearningEngine (ai_core app).
- Downstream models: AgentLearning (Group 1300 territory), UserAgentLearning
  (Group 1300 territory), AgentLearningConnection, LearningInsight
  dataclass.

**Boundary rule:** Cat C owns the bridge WRITER contract completeness +
per-bridge trigger points + bridge-inventory duplicate/overlap analysis.
Cat C does NOT own the AgentLearning / UserAgentLearning internals
(Group 1300 Memory arc closed at S1399) or per-domain business logic
(sports outcomes, revenue attribution, etc. — those live in respective
domain arcs).

**Cross-arc handoffs (important!):**
- AgentExecutionLearningLoop is Cat C for THIS arc but its output goes
  to Group 1300 Memory + Group 1700 Observability Cat C AgentExecution
  post_save receiver (S1703 §10 finding — verified).
- SportsBettingLearningBridge is Cat C for THIS arc but its output goes
  to Group 1500 Sports arc territory.
- RevenueAttributionLearningLoop is Cat C for THIS arc but its output
  goes to Group 1400 Revenue arc territory.

**Load-bearing questions:**
- Q1: Bridge inventory completeness — grep-verify all 11+ bridges at
  HEAD + verify each writer's trigger + input signal source.
- Q2: **Cross-bridge duplicate/overlap analysis** — do any two bridges
  write to the same AgentLearning row? Do they emit compatible
  `source_kind` semantics? Are any bridges deprecated / WRITE-ONLY-FORGOTTEN
  (S1704 F4 pattern applied)?
- Q3: Autonomous vs HAI-mediated split — how many bridges route
  signals through HAI first vs consume directly? This is the load-bearing
  D80 evidence.
- Q4: AgentLearningSession is deleted per S1244 migration 0002 — verify
  it's truly gone + no orphan callers.
- Q5: Duplicate service surface — AgentLearningService + AgentLearningSystem
  + AgentLearningEngine + PersistentLearningEngine all coexist at HEAD;
  are they duplicative? Is one canonical?

### D — HumanPreference / personalization (`HumanPreference` + `update_learned_stats` + F5 never-saved bug)

**Scope.** The per-user preference surface + F5
`topic_weights`/`source_weights` never-saved bug + any HumanPreference
readers (governance / personalization / recommendation).

**Canonical entry points:**
- Model: `core/models_human_interface.py:268-358` (HumanPreference).
- Writer: `HumanPreference.update_learned_stats()` — sets weights locally
  but never `.save()`s (F5 finding from governance research §1.4).
- Readers: UNKNOWN at HEAD; grep-verify at Cat D.

**Boundary rule:** Cat D owns HumanPreference model + F5 bug reproduction
+ reader inventory. Cat D does NOT fix F5 (that's post-arc T-slot per
playbook §14.5 no-implementation rule).

**Load-bearing questions:**
- Q1: F5 verification — reproduce the never-saved bug at HEAD; is it
  really F5 or has it been fixed since S1269?
- Q2: Reader inventory — grep for `HumanPreference.objects.get` or
  `.topic_weights` or `.source_weights` references. If zero readers,
  F5 is silently no-op (governance-visible only). If readers exist,
  F5 is silently miscomputing personalization.
- Q3: Governance intersection — S1269 audit surfaced F5; are there
  governance-plane implications for the bug status at HEAD?

### E — Verification loop (S746 `verification_outcome` + `record_verification` + trigger points)

**Scope.** The S746 verification-loop half of HAI schema:
`verification_outcome`, `verified_at`, `verification_profit`,
`event_completed_at`. Who triggers `record_verification()`? What
completes the round-trip from HAI decision back to outcome measurement?

**Canonical entry points:**
- Model fields: `HumanAttentionItem.verification_outcome`,
  `verified_at`, `verification_profit`, `event_completed_at` (per
  S1273 §3.16 catalog).
- Writer: `HumanAttentionItem.record_verification(outcome, profit)` per
  S1274 §4.7 narrative.
- **Triggers: UNDOCUMENTED per S1273 debt catalog** — who calls
  record_verification and when?

**Boundary rule:** Cat E owns the verification schema fields + trigger
point discovery + writer contract completeness. Cat E does NOT own the
producer paths that create HAI in the first place (Cat A) or the
FeedbackProcessor learning path (Cat B).

**Load-bearing questions:**
- Q1: Trigger discovery — grep all callers of `record_verification()`
  at HEAD.
- Q2: Coverage — what percentage of HAI rows in DB have
  `verification_outcome != null` at HEAD?
- Q3: S746 completeness — is the verification loop actually running
  end-to-end at HEAD, or is it partially wired?
- Q4: Cross-cat with Cat A — if verification is triggered by event
  completion, which producer paths emit event-completion signals?

### F — Adjacent / Separation Boundaries (external bridges + cross-arc handoffs + cross-domain HAI gaps + F.a/F.b/F.c/F.d/F.e sub-slots per Rigby SIGN F2 fold pattern)

**Scope.** Everything HumanAttention/Feedback/Learning-adjacent that
is NOT one of Cat A-E core surface. Sub-slotted per S1706 Cat F pattern.

**Sub-slots:**
- **F.a External-domain LearningBridges** (RedditLearningBridge +
  BlueskyLearningBridge in `ai_core/intelligence/`) — external social
  signal ingestion; boundary between "internal domain signals" and
  "external social signals."
- **F.b Cross-domain HAI-consumer integration gaps** (S1274 §3.3 +
  §3.8 + Body Systems / Signal Engine / Revenue / Observability all
  MISSING HAI-consumer integrations; ~5+ gap catalog). Cat F catalogs;
  fix ADRs are cross-arc T-slot per parent §6.
- **F.c PA-tool learning integration** (PALearningInsightsService +
  Rigby PA-tool patterns from Group 1600 Content Cat E S1605 tactical-split
  precedent). Boundary between HAI-learning surface and PA-learning surface.
- **F.d Duplicate learning service inventory** (AgentLearningService +
  AgentLearningSystem + AgentLearningEngine + PersistentLearningEngine
  coexistence — dedup catalog + canonical verdict). Follows S1273
  §5.13 dedup pattern; boundary between service consolidation and
  arc-scope discipline.
- **F.e Terminology boundary** ("feedback" vs "learning" vs "signal"
  vs "preference" vs "personalization" — 5 overlapping-but-distinct
  terms across the arc). Recommendation for xx99 §5 posture-decision
  brief per S1706 Cat F F8 PERMEABLE-boundary precedent.

**Boundary rule:** Cat F catalogs; does NOT act on any of F.a-F.e items
(all are post-arc T-slot per playbook §14.5). Consolidates the 5-cat
audits into arc-close evidence brief.

### Explicit non-candidates (bounded OUT)

Not proposed as Cat A-F candidates; bounded OUT per §7 anti-scope:

- **Cat: Frontend UI** — Command Center Attention Queue + Boardroom Tab
  UI implementation is out-of-scope (production surface).
- **Cat: Governance mode changes** — S1269 governance research covered
  this; Group 1800 audits HAI ↔ Governance READ-only weak connection
  but does NOT re-audit governance surface.
- **Cat: Memory internals** — Group 1300 Memory arc closed at S1399;
  AgentMemory + AgentKnowledgeSource + UserAgentLearning internals are
  Memory scope. Cat C audits WRITER contract to these models, not
  Memory-internal correctness.
- **Cat: PA tool surface** — Group 1600 Content Cat E S1605 tactical-split
  precedent already anchors PA tool surface; Cat F sub-slot F.c catalogs
  PA-learning intersection but does NOT re-audit PA tool architecture.
- **Cat: EventBus adoption** — Group 1900 delegation per S1274 §11.1.
  Group 1800 catalogs HAI event surface (candidate producers) but does
  NOT design event bus.
- **Cat: HAI producer domain-specific logic** — arbitrage signal
  generation (sports), opportunity qualification (revenue), failure-cluster
  detection (observability), signal pattern threshold (intelligence)
  are respective domain-arc scopes. Cat A audits WRITER contract to
  HAI, not producer-domain business logic.

## 4. Parent-vs-single recommendation

**Verdict: PARENT-WITH-CHILDREN** (6-child arc + xx99 canonical summary).

Evidence:
1. **Multi-substrate surface.** Six architecturally distinct concerns
   (HAI core + Feedback processing + Learning bridges + HumanPreference
   + S746 verification + Adjacent boundaries) each warrant independent
   audits per S1273 §3.16 + §5+ MISSING integrations + S1274 §4.7
   canonical round-trip + F5 governance debt.
2. **Surface exceeds single-audit capacity.** 4 models
   (HAI + HumanFeedbackRecord + HumanPreference + AgentLearning bridging)
   × 3 services (HAILifecycleService + HumanInterfaceService +
   FeedbackProcessor) × 10+ LearningBridge subclasses × 5+ cross-domain
   HAI-consumer gaps × 4+ duplicate learning-service candidates = >100
   evidence anchors per playbook §17 threshold.
3. **Load-bearing D80 posture requires per-Cat evidence.** The Option
   A vs B vs C vs D posture-decision requires evidence from each of
   Cat A-E (per-Cat producer/consumer/spine analysis) plus Cat F
   consolidation, mirroring S1699 D65 four-axis + S1799 D74 four-option
   evidence-plan discipline.
4. **Cross-arc handoffs owe per-child evidence.** Group 1300 Memory
   (learning-bridge outputs), Group 1400 Revenue (RevenueAttributionLearningLoop),
   Group 1500 Sports (SportsBettingLearningBridge), Group 1600 Content
   (PALearningInsightsService + Content-Reviewer feedback), Group 1700
   Observability (AgentExecutionLearningLoop overlap S1703 §10 post_save
   receiver), Employee OS (mission escalation → HAI), Group 1900 Event
   Architecture (HAI event candidates) all need per-Cat evidence.

**Alternative rejected: single-audit.** A single "HumanAttention audit"
would either (a) skip Feedback processing + Learning bridges surface
entirely (too narrow, misses the load-bearing D80 question), or (b)
compress 100+ evidence anchors into one child slot violating playbook
§17 evidence-anchor ceiling. Rejected per same alternative-rejected
paragraph pattern in S1600 + S1700 parent scoping.

## 5. Child mission sequence

Six children P1–P6 + P7 canonical summary, sequenced with explicit
dependency clauses per playbook §14 F10 fold. Table format matches
S1600 + S1700 §5 shape.

### Correlation primitives (working definitions — HYPOTHESIS-TO-BE-VERIFIED)

See §2.6 above for full 5-primitive table (HAI_item_id + feedback_record_id
+ learning_event_id + user_pref_id + verification_id). This is the
**second application** of the F5 correlation-primitive HYPOTHESIS box
discipline (first at S1700 parent §5 per Rigby SIGN cycle 1 F5 MUST-FIX
fold). Two-triggers threshold met — MC-3 CODIFICATION-CANDIDATE from
S1799 §10.2 promotes to CODIFICATION-READY at S1800 close if pattern
holds.

### P1–P7 sequence table

| Slot | Session | Category | Subdomain | Rationale + dependency clause |
|------|---------|----------|-----------|-------------------------------|
| **P1** | S1801 | **A** | HumanAttentionItem core + producers + lifecycle | **First child, no dependencies inbound.** HAI is the foundational primitive — Cat B/E/F all inherit HAI schema + producer contracts. P1 establishes the baseline coverage question (20+ producer sites + 8-state lifecycle + auto-escalate ladder) and the 5+ CROSS-DOMAIN GAP catalog from S1274 §3.3 + §3.8. Additionally: P1 answers the two-layer lifecycle question (HumanAttentionBridge vs HumanAttentionLifecycleService debt from S1273). |
| **P2** | S1802 | **B** | Feedback processing + FeedbackProcessor + round-trip | **Depends on P1 HAI producer contract.** P2 must answer "does every HAI decision route through record_decision → HumanFeedbackRecord → FeedbackProcessor?" — without P1 landing the producer contract, P2 cannot evaluate coverage completeness. P2 also independently audits FeedbackProcessor classifier semantics + `fed_to_ml` lifecycle + missed-consumption cases. |
| **P3** | S1803 | **C** | Learning bridges + 10+ subclasses + duplicate-service inventory | **Depends on P1 + P2.** Cat C bundles bridge writer contracts; P3 must answer the 11+ bridge inventory question first (are all 11 grep-verified alive at HEAD?), then evaluate cross-bridge dedup + autonomous-vs-HAI-mediated split (load-bearing D80 evidence). P3's scope-magnet risk: 4+ duplicate learning-service surface (AgentLearningService + Engine + System + PersistentLearningEngine) could pull deprecation ADR into the audit — **boundary discipline**: catalog + name canonical; deprecation ADR is post-arc T-slot. |
| **P4** | S1804 | **D** | HumanPreference + F5 never-saved bug + reader inventory | **Depends on P1 + P2** (P1 for HAI context; P2 for FeedbackProcessor→HumanPreference.update_learned_stats trigger chain). P4 reproduces F5 at HEAD + inventories readers. If zero readers, F5 is governance-visible only. If readers exist, F5 is silently miscomputing personalization. |
| **P5** | S1805 | **E** | Verification loop + S746 + record_verification triggers | **Depends on P1 + P2 + P3.** Cat E must answer "who calls record_verification and when?" — S1273 debt catalog says triggers are undocumented. Requires P1 (HAI producers create the row that gets verified), P2 (FeedbackProcessor may play role), P3 (LearningBridges may consume verified outcomes). |
| **P6** | S1806 | **F** | Adjacent / Separation Boundaries (F.a external bridges + F.b cross-domain gaps + F.c PA-tool intersection + F.d duplicate service inventory + F.e terminology) | **Depends on P1-P5 evidence base.** Cat F sub-slotted per Rigby SIGN F2 fold pattern (S1706 Cat F precedent). Cat F consolidates arc evidence into xx99 §5 posture-decision brief input; catalogs cross-domain HAI-consumer gaps for future arc handoffs; issues terminology recommendation per S1706 F8 PERMEABLE-boundary precedent. |
| **P7** | S1899 | **canonical_summary** | xx99 canonical summary — round-trip learning canonicalization posture | **Consumes P1-P6.** Per playbook §11.3 12-section template + §11.3 §10 meta-methodology template SIXTH application (after S1399/S1499/S1599/S1699/S1799). §5 four-option D80 posture-decision evidence brief. §8 T0/Gate + T1 unified follow-on queue. §10 sixth-application meta-methodology confirms MC-1 + MC-2 (from S1799 §10.2) + MC-3 (F5 correlation-primitive HYPOTHESIS box) durable at multi-application. Rigby SIGN cycle 1 required per playbook §15. |

**Capacity consideration.** Per playbook §17 120+ evidence anchors per
child audit, Chris's ratified capacity = 1 child + close-out per
session, total sessions = N+2 (parent + N children + summary). Group
1800 = 1 parent + 6 children + 1 summary = **8-doc arc** matching S1499
(Revenue) + S1599 (Sports) + S1699 (Content) + S1799 (Observability)
precedent. Total arc runtime target: 8 sessions across arc close;
child audits ~1000-1300 lines each (per S1701-S1706 precedent); xx99
canonical summary ~1900-2200 lines (per S1499=1915 + S1599=2241 +
S1699=2017 + S1799=2070 precedent).

**Parallelism note (per D3-analog next-session cadence).** Per S1400/S1500/S1600/S1700
precedent, D3 ratified at parent-scoping open: parent-only this session,
P1 kicks off next-session. Per playbook precedent (Groups 1400/1500/1600/1700
all sequential), no parallel-child execution proposed. Chris can
re-scope at any future session-open if cadence needs to compress.

## 6. Parked candidate issues

Items scoping-but-not-answering — Chris-gated for later T-slots or
follow-on arcs.

### 6.1 F5 HumanPreference never-saved bug fix

S1269 governance research §1.4 + S1273 §3.16 flag `topic_weights` /
`source_weights` never persisted. Group 1800 Cat D reproduces + catalogs
readers. If Chris ratifies at xx99, fix is a follow-on 1-PR
implementation, NOT part of Group 1800 six child audits.

### 6.2 S746 verification-trigger identification implementation

S1273 debt catalog says `record_verification` trigger points are
undocumented. Group 1800 Cat E discovers triggers. If P5 finds "no
production trigger exists," Chris ratifies at xx99 whether wire-up is
a follow-on implementation OR a design-preparation arc.

### 6.3 Cross-domain HAI-consumer integration ADRs (S1274 §3.3 + §3.8)

Cat F.b catalogs 5+ MISSING HAI-consumer integrations from cross_domain
audit. Per-integration ADRs (Body Systems → HAI, Signal Engine → HAI,
Revenue → HAI, Observability → HAI, failure-cluster aggregator → HAI)
are post-arc T-slot. If Chris ratifies at xx99 as T0/Gate, the ADRs
become blockers for downstream domain arcs.

### 6.4 Duplicate learning-service consolidation ADR

Cat F.d catalogs AgentLearningService + AgentLearningSystem +
AgentLearningEngine + PersistentLearningEngine coexistence. Per-service
canonical verdict is post-arc T-slot. If Chris ratifies at xx99 as
T0/Gate, the dedup ADR blocks Group 1300 Memory extension work.

### 6.5 HAI producer coverage gap ADRs

Cat A catalogs 20+ producer sites at HEAD. If some producers are
missing (e.g., no auto-HAI from failure clusters per S1274 §3.3),
per-domain ADRs to wire producers become T1 follow-ons for respective
domain arcs.

### 6.6 Learning-signal source_kind schema addition

If Cat C finds `learning_event_id` has no `source_kind` tagging at
HEAD (all writers write to same `AgentLearning` without provenance),
adding `source_kind` enum is a Group 1300 Memory + Group 1800 joint
schema change post-arc.

### 6.7 HAI event contract for Group 1900 EventBus

Cat F.b catalogs HAI event candidates for Group 1900 arc-open scoping.
Per-event schema is Group 1900 scope; Group 1800 provides catalog only.

## 7. Anti-scope

Bounded-OUT items per Chris D-decisions D75-D80. Each has one-sentence
rationale + cross-reference to prior arc where pattern repeats.

1. **Event bus adoption + design.** Group 1900 delegation per S1274
   §11.1. Same as S1700 §7 item 1.
2. **Event schema versioning.** Group 1900 delegation. Same as S1700 §7 item 2.
3. **DeliverableEvent consumer wiring.** Group 1600 T0/Gate
   R.CONTENT.XX99-ADR-BUNDLE owns. Same as S1700 §7 item 3.
4. **Memory learning-loop internal correctness.** Group 1300 Memory
   arc closed at S1399. Producer-side WRITER contract IS in scope
   (Cat B FeedbackProcessor + Cat C LearningBridges write to
   AgentLearning); internal Memory logic is not.
5. **Content Deliberation pipeline retry policies.** Group 1600 Content
   arc territory.
6. **Sports betting outcome verification.** Group 1500 Sports arc
   closed at S1599; SportsBettingLearningBridge WRITER contract IS in
   scope (Cat C); sports outcome verification internals are not.
7. **Revenue outreach delivery re-scope.** Group 1400 R.B1 handoff;
   RevenueAttributionLearningLoop WRITER contract IS in scope (Cat C);
   revenue attribution internals are not.
8. **Employee OS MissionRunner refactor.** Concurrent Employee OS scope;
   Group 1800 audits HAI writer contract from mission escalation,
   not runner internal correctness.
9. **PA tool surface unification.** Group 1600 Cat E S1605 tactical-split
   locked; PALearningInsightsService integration IS in scope (Cat F.c);
   PA tool architecture is not.
10. **BaseAgent refactor.** BaseAgent is 5,575 lines; refactor out of scope.
11. **HAI producer domain-specific logic.** Arbitrage signal generation,
    opportunity qualification, failure-cluster detection, signal pattern
    threshold are respective domain-arc scopes.
12. **Frontend Command Center / Boardroom UI redesign.** Production
    surface; out-of-scope.
13. **Governance mode changes.** S1269 covered; Cat A audits HAI ↔ Governance
    read-only weak connection but does NOT re-audit governance.
14. **Fleet application HAI sweep.** Cross-repo fleet apps have own
    HAI equivalents; scope is unified-donkey-betz only.
15. **Historical arc T-slot inheritance.** Group 1300/1400/1500/1600/1700
    post-arc §7 anchor-update queues + T1 CRITICAL remediation queues
    stay in their owning arcs' backlogs.
16. **F5 HumanPreference bug fix.** Cat D catalogs; fix is post-arc T-slot.
17. **S746 verification-trigger implementation.** Cat E catalogs; wire-up
    is post-arc T-slot.
18. **AgentLearningSession dead-code cleanup.** S1244 migration 0002
    deleted the model; Cat C verifies no orphan callers but does NOT
    author cleanup PR.
19. **Rigby SIGN worker-instability D48 pattern investigation.**
    Meta-methodology finding tracked in Memory `feedback_rigby_sign_worker_instability_recovery.md`;
    belongs to research OS meta layer, not human-attention domain.

## 8. Decisions recorded (Chris-locked pending)

Six D-verdicts D75-D80 proposed for Chris ratification via "agree all +
SIGN" round OR per-verdict override. Optional: Chris routes to Rigby
light SIGN pressure-test pre-lock per playbook §15 stage-table parent
row.

- **D75 — Parent shape.** Group 1800 = PARENT-WITH-CHILDREN 6-child arc
  (P1 Cat A + P2 Cat B + P3 Cat C + P4 Cat D + P5 Cat E + P6 Cat F + P7
  xx99 canonical summary). Evidence per §4. Alternative: single-audit
  rejected per §4 alternative-rejected paragraph. **Default lean:
  (a) accept 6-child shape.**

- **D76 — Category count + boundary rules.** Six categories A–F with
  boundary rules per §3. F1-F? Rigby folds (if light SIGN routed) may
  refine boundary rules pre-lock. Alternatives: 4-category (collapse
  Cat A+B into single "HAI-lifecycle" + Cat D+E into single "verification-personalization")
  rejected because evidence-per-Cat independence required for D80
  posture; 8-category (split Cat C by app: core/learning_bridges vs
  ai_core/intelligence vs intelligence) rejected because
  Cat F.a already handles external-bridge split. **Default lean:
  (a) accept 6 categories.**

- **D77 — Delegation boundary with prior arcs.** Group 1800 owns
  HAI + Feedback + Learning-bridge WRITER contracts (Cat A/B/C).
  Group 1300 Memory owns AgentLearning/UserAgentLearning internals.
  Group 1400 Revenue / Group 1500 Sports / Group 1600 Content / Group
  1700 Observability own respective domain business logic that
  LearningBridges consume. Group 1900 Event Architecture owns event
  bus. Employee OS owns MissionRunner correctness. Explicit boundary:
  **"HumanAttention/Feedback/Learning owns human-in-the-loop attention
  + feedback processing + learning-bridge writer contract completeness;
  respective domain arcs own the source-domain business logic that
  bridges consume; Memory arc owns AgentLearning internal correctness."**
  Alternatives rejected per boundary discipline. **Default lean:
  (a) accept explicit boundary as stated.**

- **D78 — Child sequence + dependency clauses.** P1 Cat A → P2 Cat B →
  P3 Cat C → P4 Cat D → P5 Cat E → P6 Cat F → P7 xx99 sequential per
  §5. Explicit dependency clauses embedded in §5 rationale column per
  F10 fold pattern. Alternatives rejected (reorder Cat B before Cat A
  = HAI producer contract must land first; parallel P3+P4 = Learning
  bridges + HumanPreference share `update_learned_stats` trigger chain).
  **Default lean: (a) accept sequential P1→P7.**

- **D79 — Posture-decision framing vs recommendation.** xx99 produces
  posture-decision **evidence plan** for D80-analog question (§8 D80)
  — NOT posture recommendation. Follows S1599 D59 + S1699 D65a/b/c/e
  + S1799 D74 precedent (multi-option Chris-gated selection). **Default
  lean: (a) accept posture-decision framing = evidence plan; posture
  selection is Chris-gated post-arc ADR.**

- **D80 — Load-bearing arc lens question (posture-decision frame).**
  **"Is the human-in-the-loop attention queue (HumanAttentionItem) the
  canonical learning-signal aggregation surface, OR are learning
  bridges autonomous domain-specific consumers that bypass HAI?"** This
  is the D80-analog D65/D74 question that P1-P6 child audits gather
  evidence for. Four posture options catalogued at §2.5: Option A
  Canonical Unification / Option B Structural Separability / Option C
  Hybrid / Option D Shared surface. xx99 §5 produces the posture-decision
  evidence brief; Chris ratifies selection post-arc. Alternative:
  "recommend Option A/B/C/D" (rejected per D79 posture-framing discipline).
  **Default lean: (a) accept as arc lens question, evidence-plan
  framing only.**

## 9. Next step

Chris ratifies D75-D80 via "agree all + D-N=(a)" round OR per-verdict
override. Optional: Chris routes to Rigby light SIGN pressure-test
pre-lock per playbook §15 stage-table parent row (default: skip light
SIGN — Chris decides based on how confident he is in the taxonomy).

After D75-D80 ratification:

1. Update this doc's frontmatter: `status: active` + append D-verdicts
   + Chris-lock date to `decisions_locked` field.
2. If light SIGN routed + returned SIGN-with-edits: land F1-F? folds
   at commit-time; add "do not regress" notes to `verifier_loop`.
3. Move S1800 handoff to `docs/handoffs/SESSION_1800_HUMAN_ATTENTION_ARC_OPEN.md`.
4. Overwrite `00-START-NEXT-SESSION.md` with next-session priorities
   (P1 HumanAttentionItem core audit per D78 sequence).
5. Bump `docs/research/ARCHITECTURE_INDEX.md` v50 → v51 with §1.54
   S1800 registration + line-6 preamble bump.
6. Move `docs/research/OPEN_ARCS.md` Group 1800 row from "Not started"
   to "In-progress"; bump line-6 preamble.
7. Chris merges S1800 PR to `main` between sessions.
8. Run post-merge 4-step docs cascade + `build_docs_provenance` per
   Memory rule `feedback_docs_cascade_at_every_close.md`.

Next session opens on P1 HumanAttentionItem core audit (S1801) per
D78. Arc runtime target: 8 sessions (S1800 parent + S1801-S1806
children + S1899 xx99) matching Groups 1400/1500/1600/1700 precedent.

---

## Appendix — Frontmatter provenance

The frontmatter fields at the top of this document conform to
`DOMAIN_RESEARCH_PLAYBOOK.md` §6 metadata standard for parent-doc
type. Key fields:

- `authority: parent-doc for Group 1800 research arc` (required for
  arcs; parent-doc scope)
- `category: parent_scoping` (arc slot)
- `session: 1800` (arc-parent session)
- `research_group: 1800`
- `child_slot: P0` (implicit — parent-doc)
- `domain_slug: human_attention`
- `supersedes: none` (no prior human-attention parent-doc)
- `status: draft` (pending Chris ratification of D75-D80)
- `verifier_loop:` scope of verification + Rigby SIGN state (parent =
  optional light SIGN per §15 stage table)
- `delegates_to:` Group 1300 Memory (closed) + Group 1400 Revenue
  (closed) + Group 1500 Sports (closed) + Group 1600 Content (closed)
  + Group 1700 Observability (closed) + Group 1900 Event Architecture
  (future) + Employee OS (concurrent)
- `delegated_from:` S1273 §3.16 + S1273 §4.7 + S1274 §3.3 + §3.8 +
  S1269 governance + S1399/S1499/S1699/S1799 xx99s

Pattern-precedent: matches
`docs/research/domains/observability/1700_observability_domain_scoping.md`
(fourth-application methodology exemplar). Frontmatter shape,
D-verdict structure (D75-D80 mirrors D69-D74), §3 six-category
taxonomy with sub-slotted Cat F, §5 dependency-clause table, §5 F5
correlation-primitive HYPOTHESIS box (second application, MC-3
CODIFICATION-CANDIDATE two-triggers threshold met), §7 anti-scope
19-item list, §8 D75-D80 default-lean structure all replicate S1700
parent precedent verbatim per methodology-unchanged rule.
