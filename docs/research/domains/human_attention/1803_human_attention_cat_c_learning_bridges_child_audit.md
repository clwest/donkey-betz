---
title: "Group 1800 Cat C — Learning bridges + 10+ subclasses + duplicate-service inventory child audit"
session: 1803
child_slot: P3
domain_slug: human_attention
research_group: 1800
category: child_audit
authority: child-audit for Category C per parent §5 D78 sequence + THIRD child under Group 1800
head_commit: 69cf2dd1
status: active
authors: Claude Code (Chris directed via short command "start research group 1803" — interpreted per playbook §21 short-command intent as S1803 child under Group 1800 D78 P3 slot; Rigby confirmed interpretation on arc pin pa-ae5931ea706b4537)
prior_children:
  - 1801_human_attention_cat_a_human_attention_item_core_audit.md (S1801 Cat A)
  - 1802_human_attention_cat_b_feedback_processor_child_audit.md (S1802 Cat B)
parent: 1800_human_attention_domain_scoping.md
delegates_to: []
related_arcs:
  - 1300 Memory (AgentLearning + UserAgentLearning downstream — closed at S1399)
  - 1400 Revenue (RevenueAttributionLearningLoop handoff — closed at S1499)
  - 1500 Sports (SportsBettingLearningBridge handoff — closed at S1599)
  - 1600 Content (PALearningInsights handoff — closed at S1699)
  - 1700 Observability (AgentExecution shared post_save receiver — closed at S1799)
playbook_application: §11.2 20-section child template EIGHTH application overall + THIRD under Group 1800
verifier_loop: §14 verifier-loop REQUIRED CODIFICATION-READY (S1799 §10.2 MC-1) — pre-Explore + post-Explore performed
sign_status: SIGN-with-edits at High confidence 0.84 (2026-07-03) via Rigby SIGN cycle 1 single-batch 4-question on arc pin pa-ae5931ea706b4537 per S1801+S1802 arc-pin routing precedent; F2/F4-collision-mechanism/F5-serialization-boundary/F7-LearningPatternEngine-inclusion/F8-drift-framing folds landed pre-commit; D48 27th arm turn 1 CLEAN; 22nd consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch 4-question criterion
---

# Group 1800 Cat C — Learning bridges + 10+ subclasses + duplicate-service inventory (Child Audit)

## 1. Executive Summary

Cat C is the LearningBridge substrate: 9 concrete `LearningBridge` subclasses in `core/learning_bridges/` + 2 external social-signal bridges in `ai_core/intelligence/` + a MASTER `LearningOrchestrator` in `core/self_development/` + 11+ additional learning-service classes across three apps. This child audit inventories the full writer surface, evaluates the autonomous-vs-HAI-mediated split (load-bearing D80 evidence), and closes on the F5 correlation-primitive box for `learning_event_id`.

**Headline verdicts:**

- **9 concrete `LearningBridge` subclasses grep-verified alive at HEAD** across 8 files (`advisor_feedback_bridge.py` hosts both `AdvisorFeedbackLearningLoop` @ :50 AND `AutoConsultationLearningLoop` @ :250). Parent §3.C "9 concrete in `core/learning_bridges/`" — CONFIRMED.
- **2 external `*LearningBridge` classes in `ai_core/intelligence/` DO NOT inherit from `LearningBridge` ABC.** Both `RedditLearningBridge` (`reddit_learning_bridge.py:96`) and `BlueskyLearningBridge` (`bluesky_learning_bridge.py:108`) are standalone classes. Parent §3.C "2 external-domain in `ai_core/intelligence/`" — LABEL DRIFT.
- **Autonomous vs HAI-mediated split: 100% AUTONOMOUS at HEAD.** Zero of 9 core bridges reference `HumanAttentionItem`, `HumanFeedbackRecord`, `record_decision`, `HAI_item_id`, or `attention_item_id`. Cat C bridges consume domain signals directly (post_save receivers on Application / Revenue / Collaboration / AgentExecution / AdvisorConsultationFeedback / LegacySpiderData / OpportunityInteraction / ConversationMemory) and write `UserAgentLearning`. This is load-bearing D80 evidence for the xx99 §5 posture-decision brief.
- **F5 `learning_event_id` HYPOTHESIS box THIRD application → HYPOTHESIS REMAINS. Cross-system-primitive DISPROVEN.** grep across all `.py` files returns 4 hits across 2 files, both in `ai_core/intelligence/` (`persistent_learning_engine.py` + `embedding_generator.py`). Zero cross-domain reads. Matches S1802 `feedback_record_id` failure pattern; DIFFERS from S1801 `HAI_item_id` success pattern (8-10 domains). **MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1803 close** — SECOND consecutive HYPOTHESIS-DISPROVED-CROSS-SYSTEM outcome. The primitive-box DISCIPLINE itself remains CODIFICATION-CANDIDATE and is emerging as a meta-methodology finding for the Group 1800 xx99 §5 brief: primitive-box hypotheses that fail cross-system verification are valid research outcomes but signal that the primitive is domain-internal, not architectural spine.
- **F3 AgentLearningSession claim drift.** Parent §3.C Q4 says "AgentLearningSession deleted per S1244 migration 0002 — verify it's truly gone." At HEAD: (a) the S1244 delete migration is at `core/migrations/0368_session_1244_delete_agentlearningsession.py` (NOT 0002); (b) it deleted ONLY `core.AgentLearningSession`; (c) `ai_intelligence.AgentLearningSession` (`ai_core/intelligence/models.py:211`) is ALIVE at HEAD with a writer at `persistent_learning_engine.py:65`.
- **F4 duplicate-file name-collision surface HIGH-severity finding.** Two `BoardroomLearningService` classes coexist under `core/services/`: `boardroom_learning.py:27` (Session 602 weighted-formula variant, 449 LOC, 3 caller sites) and `boardroom_learning_service.py:32` (Session 940 PA feedback-loop variant, 420 LOC, 4 caller sites). Same class name, distinct purposes, both consumed. Identical pattern for `UnifiedLearningPipeline` (`core/unified_learning_pipeline.py:9` 55 LOC vs `ai_core/intelligence/unified_learning_pipeline.py:54` 609 LOC). Import-path-dependent class resolution is a silent bug surface.
- **F7 parent §3.C "4+ duplicate service candidates" is UNDER-COUNT.** Actual learning-service class inventory at HEAD: 16+ classes across three apps (see §17 for full catalog). Post-Rigby SIGN cycle 1 language-softening fold added the previously-missed `LearningPatternEngine` (1500 LOC, 10+ consumers) — the SIGN-driven exhaustiveness pass surfaced it.
- **F8 LearningOrchestrator drift.** `core/self_development/learning_orchestrator.py:38-49` `_initialize_bridges()` registers 8 bridges — MISSING `AutoConsultationLearningLoop` from the routing table despite it being an active LearningBridge subclass.

**Biggest gaps for future research:** (a) canonical verdict on the 2 duplicate FILES (R1); (b) `ai_intelligence.AgentLearningSession` continued-value verdict (R2); (c) LearningOrchestrator registration completeness (R3); (d) `source_kind` provenance schema on `UserAgentLearning` (R8); (e) 4 cross-domain direct writers to `UserAgentLearning` outside the bridge abstraction (R6).

Runtime maturity classification: **PARTIAL-to-WORKING** — bridges are all callable, all signal-registered, all writing coherent target models; but two-file name collisions + orchestrator-registration drift + zero observability signal on dispatch + zero transaction atomicity across multi-model writes prevent a STABLE rating.

## 2. Domain Purpose

**Category C bounds:** the WRITER contract completeness for LearningBridge subclasses + per-bridge trigger points + bridge-inventory duplicate/overlap analysis + duplicate learning-service surface catalog. Cat C explicitly does NOT own AgentLearning / UserAgentLearning internals (Group 1300 Memory closed at S1399) or per-domain business logic (sports outcomes / revenue attribution / spider quality tracking / etc., all in respective domain arcs).

**Question #1 from playbook §9:** *What problem does this domain solve?* — Cat C is the **autonomous-signal writer plane** for the platform's per-user-per-agent learning state. It consumes domain events (agent execution completion, user application outcomes, revenue attribution, advisor consultation feedback, collaboration completion, spider data collection, opportunity/conversation interaction) and produces `UserAgentLearning` rows that agent orchestrators later read to adapt behavior. It is architecturally parallel to but structurally decoupled from Cat B (`FeedbackProcessor`), which produces `AgentLearning` rows from human-vetted attention-decision signals.

**Question #2 from playbook §9:** *What are the domain's canonical mental models?* — Two learnings substrate:
- **`AgentLearning`** (Group 1300 Memory territory, `core/models_unified_system.py:3655`): per-agent per-event XP-style record. Writers are Cat B (`FeedbackProcessor` @ `core/models_feedback_processing.py:240, :296`) + 7 non-bridge sites (see §4).
- **`UserAgentLearning`** (Group 1300 Memory territory, `core/models_unified_system.py:3912`): per-user per-agent per-domain adaptive learning row keyed `(user, agent_name, learning_domain)`. Writers are 9 Cat C bridges (25+ direct call sites, see §4) + 4 non-bridge cross-domain writers.

These two models are semantically distinct: `AgentLearning` is human-vetted, `UserAgentLearning` is autonomous. Parent §3.C conflates them as "AgentLearning / UserAgentLearning" without naming the writer-plane split — this audit clarifies the split in §4.

## 3. Canonical Entry Points

### 3.1 LearningBridge abstract base

`core/learning_bridges/base.py:13` — `LearningBridge` abstract class with `process_event(...)` contract. Adopted at Session 1115 (per `docs/AUDIT_FINDINGS.md` Finding #9) as fix for "unused ABC that nobody inherits from" — all 9 concrete `core/learning_bridges/` subclasses now inherit.

### 3.2 9 concrete `LearningBridge` subclasses in `core/learning_bridges/`

| # | Class | File:line | Trigger | Input signal | Writer target | HAI-mediated? |
|---|-------|-----------|---------|--------------|---------------|---------------|
| 1 | `PersonalizationFeedbackLoop` | `personalization_bridge.py:69` | post_save `OpportunityInteraction` @ :476 + post_save `ConversationMemory` @ :493 | interaction/chat rows | `UserAgentLearning.get_or_create` @ :261 + :353 + :436 | NO |
| 2 | `SpiderDataLearningLoop` | `spider_data_bridge.py:27` | post_save `LegacySpiderData` @ :408 | spider raw rows | `UserAgentLearning.get_or_create` @ :240 | NO |
| 3 | `CollaborationLearningLoop` | `collaboration_bridge.py:23` | post_save `Collaboration` when status=='completed' @ :277 | collaboration rows | `UserAgentLearning.get_or_create` @ :156 + :212 | NO |
| 4 | `AdvisorFeedbackLearningLoop` | `advisor_feedback_bridge.py:50` | post_save `AdvisorConsultationFeedback` @ :241 | advisor feedback rows | `UserAgentLearning.get_or_create` @ :148 + :206 | NO |
| 5 | `AutoConsultationLearningLoop` | `advisor_feedback_bridge.py:250` (SAME FILE as #4) | direct-invocation from audit coordinators (`track_auto_consultation(dict)`) — no signal | dict payloads | `UserAgentLearning.get_or_create` @ :344 | NO |
| 6 | `ApplicationOutcomeLearningLoop` | `application_outcome_bridge.py:34` | post_save `Application` when status ∈ {accepted, rejected} @ :315 + post_save `JobApplication` @ :329 | application rows | `UserAgentLearning.get_or_create` @ :184 + :236 + :274 + :381 | NO |
| 7 | `AgentExecutionLearningLoop` | `agent_execution_bridge.py:24` | post_save `AgentExecution` when status ∈ {completed, failed} @ :317 | execution rows | `UserAgentLearning.get_or_create` @ :174 + :241; also `_trigger_orchestrator` @ :282 → `trigger_learning_cycle(...)` in `core/self_development/learning_orchestrator.py:401` | NO |
| 8 | `SportsBettingLearningBridge` | `sports_betting_bridge.py:30` | invocation-driven `sync_user_betting_to_learning(user)` + `record_arbitrage_outcome(...)` — no post_save signal | user + `BankrollManagement` + `UserBet` + `MLPrediction` reads | `UserAgentLearning.update_or_create` @ :131 + :177 + :251 + :503 + :579; ALSO `AgentMemory.objects.create` @ :532 + :606 | NO (but writes AgentMemory too, outside parent §3.C catalog) |
| 9 | `RevenueAttributionLearningLoop` | `revenue_attribution_bridge.py:31` | post_save `Revenue` @ :227 | revenue rows | `UserAgentLearning.update_or_create` @ :147 + :181 | NO |

Total UserAgentLearning writer sites from bridges: **22**. AutoConsultationLearningLoop system-user fallback pattern @ `advisor_feedback_bridge.py:405-421` creates `system_advisor_tracker` User on first invocation — side-effect during learning write path (see §15 D6).

### 3.3 2 external `*LearningBridge` classes in `ai_core/intelligence/` (NOT `LearningBridge` subclasses)

| # | Class | File:line | ABC contract | Output |
|---|-------|-----------|--------------|--------|
| 1 | `RedditLearningBridge` | `ai_core/intelligence/reddit_learning_bridge.py:96` | Standalone (does NOT inherit `LearningBridge`) | Structured dataclasses `RedditInsight` + `SubredditTrend` + `CommunityConsensus`; no `UserAgentLearning.objects.*` writes detected |
| 2 | `BlueskyLearningBridge` | `ai_core/intelligence/bluesky_learning_bridge.py:108` | Standalone (does NOT inherit `LearningBridge`) | Structured dataclasses `ExpertInsight` + `MarketSignal` + `TrendAnalysis`; no `UserAgentLearning.objects.*` writes detected |

Both are consumed via singleton getter functions (`get_reddit_learning_bridge()` @ `ai_core/consciousness/unified_mind.py:144`; `get_bluesky_learning_bridge()` @ `ai_core/consciousness/unified_mind.py:137`) and by `learning_loop.py` in ai_core (3 call sites @ :879, :1032, :1149). See F2 in §14 for the label-drift finding.

### 3.4 LearningOrchestrator MASTER coordinator

`core/self_development/learning_orchestrator.py:22` — `LearningOrchestrator` class. `_initialize_bridges()` @ :38-49 declares an 8-entry bridge registry (docstring at :6 says "Connects all 8 learning bridges"). **AutoConsultationLearningLoop is NOT registered** despite being a live subclass. Entry function `trigger_learning_cycle(user, event_type, event_data)` @ :401 is called from AgentExecutionLearningLoop `_trigger_orchestrator` @ `agent_execution_bridge.py:295`. See F8 in §14.

### 3.5 Signal receiver registration

All 8 signal-driven bridges use `@receiver(post_save, sender=<Model>)` decorators inside the bridge module file (post-Session-1115 pattern):

| Bridge | Receiver location |
|--------|-------------------|
| PersonalizationFeedbackLoop | `personalization_bridge.py:476` + `:493` (dual receiver, guarded by try/except ImportError) |
| SpiderDataLearningLoop | `spider_data_bridge.py:408` |
| CollaborationLearningLoop | `collaboration_bridge.py:277` |
| AdvisorFeedbackLearningLoop | `advisor_feedback_bridge.py:241` |
| AutoConsultationLearningLoop | **NONE** (invocation-driven) |
| ApplicationOutcomeLearningLoop | `application_outcome_bridge.py:315` + `:329` (dual for Application + JobApplication) |
| AgentExecutionLearningLoop | `agent_execution_bridge.py:317` |
| SportsBettingLearningBridge | **NONE** (invocation-driven) |
| RevenueAttributionLearningLoop | `revenue_attribution_bridge.py:227` |

7 signal-driven; 2 invocation-driven (AutoConsultation + SportsBetting).

## 4. Major Models

Cat C bridges + services target 8 models across 2 model modules. All are Group 1300 Memory arc territory (Memory closed at S1399); this section catalogs the WRITER surface only, not model internals.

### 4.1 `AgentLearning` (`core.AgentLearning`)

- **Location:** `core/models_unified_system.py:3655` — PK: `UUIDField` — FK: `teacher_agent → Agent.CASCADE`, `student_agent → Agent.CASCADE`, `solution → AgentSolution.CASCADE`.
- **Writer inventory (9 sites total):**
  - `core/models_feedback_processing.py:240` — **FeedbackProcessor (Cat B territory)** — VERIFIED S1802 §14 F1
  - `core/models_feedback_processing.py:296` — **FeedbackProcessor (Cat B territory)** — VERIFIED S1802 §14 F1
  - `intelligence/connect_all_agents.py:349` — non-bridge, seed script call
  - `intelligence/spider_agent_connector.py:299` — non-bridge, spider→agent wiring
  - `intelligence/learning_path_orchestrator.py:371` + `:413` — non-bridge, learning-path bootstrap
  - `core/views_ai_ecosystem.py:172` — non-bridge, REST view
  - `core/management/commands/bootstrap_learning_system.py:268` — non-bridge, seed command
  - `core/management/commands/connect_all_agents.py:273` — non-bridge, wiring command
- **Retention:** SAVED-FOREVER — no TTL, no purge task. Parallel to S1801 F6/D7 + S1802 F6/D7 pattern.
- **Load-bearing observation:** **ZERO writers from `core/learning_bridges/` touch `AgentLearning` directly.** All 9 bridges write `UserAgentLearning` instead. This is a critical WRITER-PLANE SPLIT (see F6 in §14).

### 4.2 `UserAgentLearning` (`core.UserAgentLearning`)

- **Location:** `core/models_unified_system.py:3912` — inherits `UnifiedBaseModel` — FK: `user → User.CASCADE`. Keyed by `(user, agent_name, learning_domain)` composite semantics.
- **Writer inventory (25+ sites):**
  - **22 sites across 8 bridge files** — see §3.2 table
  - **4 cross-domain direct writers OUTSIDE the bridge abstraction:**
    - `revenue/models.py:144` — Revenue app direct write
    - `core/models/jobs/models.py:134` — Jobs app direct write
    - `core/models/jobs/models.py:191` — Jobs app direct write
    - `core/services/td_handlers_content.py:222` — PA tool handler direct write
- **Retention:** SAVED-FOREVER at schema level, but `expires_at` field exists at :~4026 and `get_active_learnings()` filter exists at :~4116. **NO automatic cleanup task defined.** TTL hook is aspirational, not operational.
- **Load-bearing observation:** the 4 non-bridge writers to `UserAgentLearning` bypass the `LearningBridge.process_event(...)` contract entirely and are not cataloged in parent §3.C. See F10 + R6.

### 4.3 `LearningInsight` (`core.LearningInsight`)

- **Location:** `core/models/ai_learning/models.py:41` — standard Django PK — no direct FKs; stores immutable pattern records.
- **Writer inventory:** `core/models_feedback_processing.py:257` (FeedbackProcessor Cat B, lazy-loaded `self.LearningInsight.objects.create()` guarded conditional). Zero non-Cat-B production writers found.
- **Retention:** SAVED-FOREVER — no TTL; `discovered_at` immutable, `last_validated` auto-updates on save.
- **NOT a duplicate.** A comment at `ai_core/intelligence/models.py:259` confirms `ai_intelligence.LearningInsight` was deleted in the Session 1244 Cat 2 dormant cleanup; the `core` variant is canonical.

### 4.4 `AgentLearningConnection` (`core.AgentLearningConnection`)

- **Location:** `core/models_unified_system.py:630` — PK: `UUIDField` — FK: `teacher_agent → Agent.CASCADE`, `student_agent → Agent.CASCADE` — composite unique `(teacher_agent, student_agent)`.
- **Writer inventory:** zero `.objects.create()` sites found in production. Metadata-only — updated via `.apply_mythology_penalty()` method @ :698.
- **Retention:** SAVED-FOREVER — `is_active` boolean provides soft-disable.

### 4.5 `ai_intelligence.AgentLearningSession` (`ai_intelligence.AgentLearningSession`)

- **Location:** `ai_core/intelligence/models.py:211` — PK: `UUIDField` (session_id) — no cross-app FK references; stores JSON arrays (`agents_involved`, `signal_types_processed`, `data_sources`).
- **Writer inventory:** **1 site** — `ai_core/intelligence/persistent_learning_engine.py:65-77` (wrapped in `transaction.atomic() + try/except`).
- **Retention:** SAVED-FOREVER — no TTL; status enum tracks lifecycle {active, completed, failed, paused}.
- **Load-bearing observation:** parent §3.C Q4 conflates this with `core.AgentLearningSession` which S1244 deleted. This variant is alive at HEAD. See F3.

### 4.6 `ai_intelligence.LearningDocument` + `LearningEmbedding` + `LearningInsight` (ai_core variants)

- **Locations:** `ai_core/intelligence/models.py:67` (`LearningDocument`) + `:169` (`LearningEmbedding`) + additional at same file.
- **Writers:** `ai_core/intelligence/document_generator.py:249, 308, 376, 438` (4 sites for `LearningDocument`); `ai_core/intelligence/embedding_generator.py:137, 213` (2 sites for `LearningEmbedding`).
- **Retention:** SAVED-FOREVER; cascade delete on parent event.
- **Note:** `ai_intelligence.LearningInsight` was deleted in S1244 (see §4.3 note).

### 4.7 `LegacySpiderData` (writer's INPUT, not output)

- Consumed by `SpiderDataLearningLoop` via post_save receiver @ `spider_data_bridge.py:408`. Cross-arc reference: Spider Network scope, not Group 1800.

### 4.8 `Revenue`, `Application`, `JobApplication`, `Collaboration`, `AdvisorConsultationFeedback`, `AgentExecution`, `OpportunityInteraction`, `ConversationMemory`

- Consumed as INPUT signals via post_save receivers. Cross-arc references to Groups 1400 (Revenue), Cat A/B (Application/JobApplication if via HAI producer), Employee OS (Collaboration), Advisor domain (AdvisorConsultationFeedback), Cat A/B (AgentExecution via S1703), and Cat A (OpportunityInteraction + ConversationMemory).

## 5. Major Services

Cat C service surface is 15+ classes across three apps. This section inventories each with 1-line purpose + consumer count + verdict.

### 5.1 Parent §3.C named services (5)

| Service | File:line | Purpose | Consumers | Verdict |
|---------|-----------|---------|-----------|---------|
| `AgentLearningService` | `core/services/agent_learning_service.py:122` | 14 AI content agents adapt via record_interaction() → Redis-backed preferences | 6+ import sites, wired to REST @ `core/views_agent_learning.py` :39, :94, :134, :167, :232 | ALIVE |
| `AgentLearningSystem` | `intelligence/agent_learning.py:22` | Agents learn from performance + adapt predictions | ~3 caller sites (grep limited) | UNCLEAR |
| `AgentLearningEngine` | `ai_core/intelligence/agent_learning_engine.py:69` | Continuous learning for 152 agents from real-time spider data | ~4 instantiation sites | ALIVE |
| `PersistentLearningEngine` | `ai_core/intelligence/persistent_learning_engine.py:42` | Persistent `AgentLearningSession` + `AgentLearningEvent` writer | Called from `unified_learning_pipeline.py` in ai_core | ALIVE |
| `PALearningInsightsService` | `core/services/pa_learning_insights.py:24` | PA-tool-facing learning insight surface | Referenced in bridges but callers unverified | UNCLEAR |

### 5.2 Additional learning-service classes found beyond parent §3.C catalog (10+)

| Service | File:line | Purpose | Consumers | Verdict |
|---------|-----------|---------|-----------|---------|
| `MetaLearningEngine` | `self_awareness/intelligence.py:70` | Meta-learning about learning patterns | Unverified | UNCLEAR |
| `WeightedLearningService` | `core/services/weighted_learning.py:33` | ChatGPT weighted-formula for experiment outcomes | 5 callers | ALIVE |
| `PipelineLearningService` | `core/services/pipeline_learning.py:42` | Pipeline stage → learning-row transforms | 3 callers | ALIVE |
| `BoardroomLearningService` (Session 602) | `core/services/boardroom_learning.py:27` | Weighted-formula Boardroom decision integration | 3 caller sites: `core/views_agent_learning.py:2509, :2548`; `core/services/decision_prioritization.py:81` | ALIVE (name-collision with 5.2b) |
| `BoardroomLearningService` (Session 940) | `core/services/boardroom_learning_service.py:32` | PA feedback loop for boardroom approve/ignore | 4 caller sites in `core/services/td_handlers_agents.py:4450, :4522, :4576, :4619` | ALIVE (name-collision with 5.2a) |
| `ResolveLearningService` | `core/services/resolve_learning.py:29` | Resolve-mode learning surface | 3 callers | ALIVE |
| `LiveLearningOrchestrator` | `core/services/live_learning_orchestrator.py:216` | Real-time learning-loop for live agent updates | 5 callers | ALIVE |
| `ImplicitLearningService` | `core/services/implicit_learning.py:41` | Implicit-pattern extraction from behavior | 3 callers | ALIVE |
| `UnifiedLearningPipeline` (core) | `core/unified_learning_pipeline.py:9` | Cross-domain insight applier (55 LOC) | 2 callers: `core/learning_bridges/sports_betting_bridge.py:297` (imports `LearningInsight` + `LearningType` from it); `scripts/testing/test_phase3_integration.py:21` | ALIVE (name-collision with 5.2b) |
| `UnifiedLearningPipeline` (ai_core) | `ai_core/intelligence/unified_learning_pipeline.py:54` | Async spider→agent orchestrator (609 LOC) | 2 callers: `ai_core/intelligence/learning_metrics_dashboard.py:238, :445` | ALIVE (name-collision with 5.2a) |
| `SpiderLearningOrchestrator` | `ai_core/intelligence/spider_learning_orchestrator.py:98` | Orchestrates spider data → agent learning flow | ~4 callers | ALIVE |
| `SpiderLearningLoop` | `intelligence/spider_quality_tracker.py:169` | Spider quality metrics for adaptive collection | ~2 callers | ALIVE |
| `LearningOrchestrator` (MASTER) | `core/self_development/learning_orchestrator.py:22` | Master coordinator; connects 8-of-9 bridges | Called from `AgentExecutionLearningLoop._trigger_orchestrator` @ `agent_execution_bridge.py:295` | ALIVE (F8 registry drift) |
| `LearningPatternEngine` | `core/services/learning_pattern_engine.py:28` | Pattern mining / storage / application; singleton via `get_learning_pattern_engine()` @ :1505 | 10+ import sites: `core/tasks.py:516, :7816, :7854, :7896` + `core/conversation_orchestrator.py:329` + `core/agent_router.py:507` + `core/services/knowledge_first_router.py:177` + `core/services/context_tracking.py:81` + `core/personal_ai_assistant_enhanced.py:2279` + `intelligence/spider_agent_connector.py:262` | ALIVE (heavy-consumer service, ~1500 LOC — surfaced via Rigby SIGN cycle 1 language-softening fold on F7 exhaustiveness claim) |

### 5.3 God-service check (>3000 lines)

Zero god-services in bridge files (all ≤696 LOC). `ai_core/intelligence/learning_loop.py` @ 52kB / ~1550 LOC is largest ai_core learning file but below threshold. `ai_core/intelligence/consumers.py` @ 82kB IS a god-service candidate but is out-of-scope (consumer plane, not bridge-writer plane).

## 6. Major APIs and Interfaces

### 6.1 REST endpoints touching Cat C

Ten endpoints in `core/views_agent_learning.py` + `core/views_learning_loop.py` + `core/views_diagnostics.py` expose learning services:

| Method | Path | View | Backend |
|--------|------|------|---------|
| POST | `/api/agent-learning/interaction/` | record_interaction @ `views_agent_learning.py:39` | `AgentLearningService.record_interaction()` |
| GET | `/api/agent-learning/preferences/{agent_name}/` | get_preferences @ :94 | `AgentLearningService.get_top_preferences()` |
| GET | `/api/agent-learning/context/{agent_name}/` | get_adaptive_context @ :134 | `AgentLearningService.get_adaptive_context()` |
| GET | `/api/agent-learning/stats/` | get_learning_stats @ :167 | `AgentLearningService.get_learning_stats()` |
| POST | `/api/agent-learning/apply/` | apply_preferences @ :232 | `AgentLearningService.apply_preferences()` |
| GET | `/api/learning/velocity/dashboard/` | get_learning_velocity_dashboard @ :2594 | `LiveLearningOrchestrator` |
| GET | `/api/learning/loop/stats/` | learning_loop_stats @ :985 | `LearningLoopOrchestrator.get_learning_effectiveness_stats()` |
| POST | `/api/learning/loop/run/` | run_learning_cycle @ :1059 | `LearningLoopOrchestrator.run_learning_cycle()` |
| GET | `/api/learning/loop/agent/<agent>/` | get_agent_learnings @ :1082 | `LearningLoopOrchestrator.get_learnings_for_agent()` |
| GET | `/api/cockpit/learning-loop/` | cockpit_learning_loop @ `views_diagnostics.py:4169` | Diagnostics control panel |

### 6.2 WebSocket surface

No dedicated learning WebSocket consumer. `tasks_agents.py:3361-3381, 3619` publishes to Redis `agent_learning` channel (indirect); no Django Channels consumer for this channel found in Cat C scope.

### 6.3 PA tool surface

`core/services/tool_dispatcher.py:405, :442` registers two learning-related tool handlers:

- `learning_patterns_tool` → `_handle_learning_patterns()` — retrieves `LearningPattern` rows for PA reasoning context.
- `learning_tool` → `_handle_learning()` — PA Learning Loop insight management.

Plus PA Tool Learning Enricher @ `core/services/pa_tool_learning_enricher.py:20-50` — injects `PAToolInsight` records into PA system prompt (approved + non-expired).

Additionally 4 sites in `core/services/td_handlers_agents.py:4450, :4522, :4576, :4619` import `BoardroomLearningService` (Session 940 variant) for PA-facing boardroom feedback aggregation.

### 6.4 Management commands touching Cat C

- `bootstrap_learning_system.py` — seeds `AgentLearning` and runs a learning cycle for fresh deployments.
- `build_learning_bridge_audit.py` — AST-parses bridge classes and generates `docs/LEARNING_BRIDGE_AUDIT.md`.
- `sync_agent_learning.py` — syncs agent learning state (purpose unverified in this audit).
- `discover_learning_cohorts.py`, `seed_learning_journeys.py`, `sync_persona_learning.py`, `start_learning_demo.py`, `backfill_experiment_learnings.py` — auxiliary commands.
- `connect_all_agents.py` — writes `AgentLearning` @ :273.

### 6.5 Celery / Beat surface (see §7 for detail)

Three beat-scheduled tasks + additional on-demand tasks — see §7.2.

## 7. Runtime Flows

### 7.1 Canonical Cat C runtime flow (autonomous plane)

```
Domain event fires (Application saved / Revenue saved / etc.)
    ↓
Django signal (@receiver post_save) — declared inside bridge module
    ↓
Bridge.process_event(instance) — inherits base LearningBridge contract
    ↓
Bridge-internal:
    - Compute derived metrics (success_rate, effectiveness, XP delta)
    - UserAgentLearning.get_or_create(user=…, agent_name=…, learning_domain=…) → learning row
    - .learning_content = {...}; .save()
    - (optional) agent.metrics update + agent.save()
    - (only AgentExecutionLearningLoop) _trigger_orchestrator(...) → learning_orchestrator.trigger_learning_cycle(...)
    ↓
No signal emitted downstream. No observability signal. No telemetry emit.
```

Contrast S1801 §7 HAI-plane flow (producer → HAI row → auto-escalate ladder → decision → HFR → FeedbackProcessor → AgentLearning + LearningInsight) — Cat C bypasses HAI entirely.

### 7.2 Cat C beat + on-demand Celery surface

Beat-scheduled (`core/celery.py`):

| Entry name | Task | Cadence | Queue |
|-----------|------|---------|-------|
| `cleanup-learning-readback` | `core.tasks.cleanup_learning_readback_events` (`core/tasks.py:245`) | 4:10 AM daily | default |
| `decay-learning-patterns` | `core.tasks.decay_learning_patterns` (`core/tasks.py:252`) | Sunday 5 AM | default |
| `check-learning-loop-slo` | `core.check_learning_loop_slo` (`core/tasks.py:600`) | 9 AM daily | default |

On-demand (`core/tasks.py` + `core/tasks_agents.py`):

- `run_learning_loop_cycle` @ `tasks.py:443` — manual/scheduled trigger.
- `run_agent_learning_cycle` @ `tasks_agents.py:2944` (wrapped `tasks.py:2779`) — 10-min Redis publish to `agent_learning` channel @ :3361.
- `broadcast_learning_status` @ `tasks_agents.py:3514` (wrapped `tasks.py:2791`) — broadcasts learning stats via Redis + WebSocket.
- `embed_daily_agent_learning` @ `tasks_agents.py:3790` (wrapped `tasks.py:2799`) — creates `DocumentEmbedding` for `AgentLearning` rows @ :3908-4020.
- `update_agent_effectiveness_from_learning` @ `tasks_agents.py:2944+` — AgentEvolution XP award loop @ :4461-4487.
- `learning_loop.track_prediction_outcomes` @ `tasks.py:4631` — no beat entry.
- `learning_loop.calculate_agent_accuracy` @ `tasks.py:4635` — no beat entry.
- `core.tasks.mine_learning_patterns` @ `tasks.py:7797` — no beat entry.

## 8. Data Ownership and Lifecycle

**Data ownership boundary:** Cat C owns bridge WRITER contracts (per parent §3.C boundary rule). `AgentLearning` + `UserAgentLearning` + `LearningInsight` + `AgentLearningConnection` model internals are Group 1300 Memory territory (closed at S1399). Cat C bridge outputs land as writer rows in Group 1300 tables.

**Retention posture (parallel to S1801 F6/D7 + S1802 F6/D7):**
- `AgentLearning`: SAVED-FOREVER. No purge task.
- `UserAgentLearning`: SAVED-FOREVER at operational level; `expires_at` field + `get_active_learnings()` filter exist at schema level but zero cleanup task drives them.
- `LearningInsight` (core): SAVED-FOREVER.
- `AgentLearningConnection`: SAVED-FOREVER.
- `ai_intelligence.AgentLearningSession`: SAVED-FOREVER; status enum tracks lifecycle {active, completed, failed, paused} but no retention job triggers on completion.
- `ai_intelligence.LearningDocument` + `LearningEmbedding`: SAVED-FOREVER (cascade delete on parent event only).

**Lifecycle state machine:** none present on `AgentLearning` / `UserAgentLearning`. Rows are append-mostly with metric updates; no promoted / archived / retired states.

## 9. Integrations With Other Domains

### 9.1 Cross-arc handoff table (verified at HEAD)

| Bridge | Consumed model (INPUT) | Written model (OUTPUT) | Cross-arc source | Cross-arc target |
|--------|------------------------|------------------------|------------------|------------------|
| PersonalizationFeedbackLoop | OpportunityInteraction + ConversationMemory | UserAgentLearning | Cat A HAI+ChatCore adjacencies | Group 1300 Memory |
| SpiderDataLearningLoop | LegacySpiderData | UserAgentLearning | Spider Network | Group 1300 Memory |
| CollaborationLearningLoop | Collaboration | UserAgentLearning | Employee OS / Collaboration surface | Group 1300 Memory |
| AdvisorFeedbackLearningLoop | AdvisorConsultationFeedback | UserAgentLearning | Advisor surface (out-of-scope domain) | Group 1300 Memory |
| AutoConsultationLearningLoop | dict payloads from audit coordinators | UserAgentLearning | Advisor surface | Group 1300 Memory |
| ApplicationOutcomeLearningLoop | Application + JobApplication | UserAgentLearning | Group 1400 Revenue-adjacent | Group 1300 Memory |
| AgentExecutionLearningLoop | AgentExecution | UserAgentLearning + Agent.metrics + LearningOrchestrator (via trigger_learning_cycle) | Group 1700 shares source model with separate Rigby receiver | Group 1300 Memory (+ core.self_development) |
| SportsBettingLearningBridge | BankrollManagement + UserBet + MLPrediction (READ from sports.models) | UserAgentLearning + AgentMemory | Group 1500 Sports | Group 1300 Memory |
| RevenueAttributionLearningLoop | Revenue | UserAgentLearning | Group 1400 Revenue | Group 1300 Memory |

### 9.2 D80 posture evidence (load-bearing for xx99 §5 four-option brief)

**Autonomous vs HAI-mediated split: 100% AUTONOMOUS at HEAD.**

Verification: grep across all 9 core/ bridge files for `HumanAttentionItem` + `HumanFeedbackRecord` + `record_decision` + `HAI_item_id` + `attention_item_id` — **ZERO hits.** Cat C bridges do not participate in the HAI plane at HEAD.

Only HAI-mediated learning row writes: FeedbackProcessor (Cat B) @ `core/models_feedback_processing.py:240, :296` writing `AgentLearning`.

**D80 posture-decision evidence brief (for xx99):** The codebase demonstrates a **DUAL-PLANE LEARNING ARCHITECTURE** — a human-vetted plane (Cat B FeedbackProcessor → `AgentLearning`) and an autonomous plane (Cat C bridges → `UserAgentLearning`). The two planes target DIFFERENT models with different key semantics. This is not conflict; it is a deliberate split. The xx99 §5 posture-decision should evaluate whether this split is intentional canonical architecture (Option A) or historical accident that Option B/C/D should consolidate.

### 9.3 Cross-domain HAI-consumer integration gap intersections

Per S1274 §3.3 CRITICAL cluster + §3.8 MEDIUM signal pattern:

- **AgentExecutionLearningLoop** — writes `UserAgentLearning` with execution metrics, does NOT surface execution failures to HAI. Gap: high-value execution failures not routed to human review.
- **RevenueAttributionLearningLoop** — writes revenue-optimization learning from Revenue signal, does NOT surface high-value revenue events to HAI. Gap.
- **CollaborationLearningLoop** — writes team-formation + collaboration-skills learning from Collaboration completion. Does NOT surface collaboration outcomes to HAI. Gap.
- **AutoConsultationLearningLoop** — writes auto-consultation accuracy, does NOT surface consultation misses to HAI. Gap.
- **SpiderDataLearningLoop** — writes spider intelligence learning from LegacySpiderData; does NOT surface spider signal patterns to HAI. Gap — parallel to S1274 §3.8 signal pattern absence.

Five Cat C bridges are candidates for S1274 §3.8 signal-pattern-to-HAI improvements. Three have implicit HAI overlap (Personalization via ConversationMemory, AdvisorFeedback via advisor insights, ApplicationOutcome via high-stakes decisions).

### 9.4 Duplicate learning-service intersections with Cat E adjacency-boundary

Boundary rule (parent §3.C): Cat C bundles bridge writer contracts + duplicate-service inventory + canonical verdict. Deprecation ADRs are POST-arc T-slot per playbook §14.5 no-implementation rule. Cat C catalogs (see §5.1 + §5.2 + §17), Cat F sub-slot F.d @ S1806 consolidates.

## 10. Event Flows

Cat C does NOT emit domain events at HEAD (no Django signals dispatched OUT; no message-bus writes; no WebSocket publishes from bridge write path). Bridge outputs are ORM writes only. Downstream reads occur asynchronously via:

- REST API pull (`/api/agent-learning/*` @ §6.1)
- Celery-driven aggregation (`broadcast_learning_status` publishes stats via Redis + WebSocket every 10min)
- Direct ORM query from consumer services (`AgentLearningService.get_adaptive_context()` etc.)

**Event-emit gap (parallel to S1801 F6 + S1802 F7):** bridge dispatch is not observable at the event plane. No `pre_dispatch` / `post_dispatch` signal exists. If a bridge silently swallows an exception (parallel to S1801 D5 + S1802 D3), zero downstream visibility. See D3 in §15.

## 11. Existing Documentation

Documentation coverage of Cat C is **LIGHT** (playbook §12 classification) despite bridge and service surface being wide.

**Positive doc surface:**
- `docs/LEARNING_BRIDGE_AUDIT.md` (auto-generated from `build_learning_bridge_audit.py`) — catalogs 9 bridge modules + 9 learning-loop classes with docstring summaries. NAMING inconsistency flagged (7 `*LearningLoop` + 1 `*LearningBridge` + 1 `*FeedbackLoop`). Not cited from `PLATFORM_INVENTORY.md`.
- `docs/topics/agent-system.md:87` — mentions `AgentLearningService` only.
- `docs/AUDIT_FINDINGS.md` Finding #9 (`✅ fixed Session 1115`) — documents ABC migration of bridges to inherit from `LearningBridge` base class.
- Session 1115 handoff — closed the unused-ABC finding.
- Session 991 handoff — proactive intelligence + AgentLearning wiring.
- Session 930 handoff — user context learning + UserAgentLearning introduction.
- Session 1244 delete migration `core/migrations/0368_...py` — inline comment documents the S1244 removal of `core.AgentLearningSession`.
- `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` §3.C — parent scoping (this audit's parent doc).
- S1802 §14 F1 references FeedbackProcessor's AgentLearning writes.
- S1703 (`docs/research/domains/observability/`) mentions AgentExecution post_save receivers (bridge + Rigby signal).

**Gaps:**
- 11 bridge classes + 15+ service classes have zero unified catalog.
- `PLATFORM_INVENTORY.md` does NOT count learning-related classes or bridges.
- No doc clarifies the writer-plane split between AgentLearning (Cat B) and UserAgentLearning (Cat C).
- Duplicate-file name collisions (BoardroomLearningService x2, UnifiedLearningPipeline x2) undocumented.
- `ai_intelligence.AgentLearningSession` alive-at-HEAD state undocumented.
- 4 non-bridge cross-domain UserAgentLearning writers undocumented.
- LearningOrchestrator registry (`_initialize_bridges()`) missing AutoConsultationLearningLoop is undocumented.
- No canonical glossary for "feedback" vs "learning" vs "signal" vs "personalization" vs "insight" — F.e terminology sub-slot deferred to S1806.

## 12. Research Coverage

**Verdict: LIGHT → MODERATE (fragmented; no canonical single surface).**

- **LIGHT:** most topic docs mention `AgentLearningService` only; no bridge coverage.
- **MODERATE (single artifact):** `LEARNING_BRIDGE_AUDIT.md` catalogs 9 bridges but lacks cross-domain duplication analysis and is not authoritative-anchor-cited.
- **DEEP (segment only):** S1399 Memory canonical summary covers `AgentLearning`/`UserAgentLearning` model internals but not bridge writer plane. S1274 §4.7 canonical narrative covers ONLY the HAI→Learning path (Cat B), not Cat C bridge writers.
- **NOT CANONICAL:** no single authoritative inventory exists that covers all 9 bridges + 2 external + 15+ services + writer-plane split + retention posture.

## 13. Architecture Maturity

**Verdict: PARTIAL-to-WORKING** (per playbook §12 classification).

Rationale:
- **Signal integration alive** for 7 of 9 bridges (post_save receivers registered @ `apps.py` + module-level `@receiver`).
- **123 total method definitions** across bridges (23 in base.py + 100 in concrete subclasses).
- **All 9 bridges callable + all write UserAgentLearning coherently** (25+ verified writer sites).
- **REST + PA tool consumption alive** at 10 endpoints + 2 tool handlers.
- **BUT**: 2 duplicate FILE name collisions (F4 HIGH), ABC-contract violation on Reddit/Bluesky (F2 MED), missing observability signals (D3 MED), zero transaction atomicity across multi-model writes (D2 MED), best-effort silent-skip pattern (D5 MED), orchestrator registry drift (F8 MED), retention SAVED-FOREVER across all 8 models (D4 MED), 4 cross-domain direct writers bypassing bridge abstraction (F10 SPEC). Architecture INTENT is clear; IMPLEMENTATION is fragile.

Would rate WORKING if the two duplicate-file name collisions were resolved. Would rate STABLE if additionally the observability signal gap + retention posture + transaction atomicity were addressed.

**Compound-impact framing (per Rigby SIGN cycle 1 Q4 architectural-risk fold).** The biggest architectural risk in Cat C at HEAD is NOT any single finding — it is the **COMBINATION** of F4 (duplicate class-name collision) + D2 (zero transaction atomicity) + D3 (signal-handler silent exception swallow) + D7 (SAVED-FOREVER retention). Individually each is a MED-to-HIGH finding; combined they produce a "you can't trust what was learned, when, or why, and you can't reliably replay" failure mode:
- **F4 name collision** means the wrong-import bug is possible at every future call site.
- **D2 non-atomic multi-model writes** means partial-write corruption if the bridge dies mid-flow.
- **D3 silent exception swallow** hides both the F4 wrong-import symptoms and the D2 partial-write symptoms.
- **D7 SAVED-FOREVER retention** means the corrupt / silently-missed rows are indistinguishable from healthy rows forever after.

Post-arc T-slot: consider treating F4+D2+D3+D7 as a **single compound remediation ticket** rather than four independent fixes, since fixing one without the others leaves the compound failure mode partially open. Rigby's recommended "unified learning plane contract" (see R0 in §19) is the design-level response to this compound.

## 14. Known Drift

### F1 (LOW) — Parent §3.C 9-subclass claim clarification

Parent §3.C names "9 concrete in `core/learning_bridges/`" without disambiguating file count vs class count. At HEAD: 9 concrete `LearningBridge` subclasses across 8 files (`advisor_feedback_bridge.py` hosts BOTH `AdvisorFeedbackLearningLoop` @ :50 AND `AutoConsultationLearningLoop` @ :250). CLARIFICATION not DRIFT. Recommendation: parent §3.C should read "9 concrete `LearningBridge` subclasses across 8 files" for future callers.

### F2 (MED) — External `*LearningBridge` classes lack ABC inheritance

Parent §3.C labels `RedditLearningBridge` (`ai_core/intelligence/reddit_learning_bridge.py:96`) + `BlueskyLearningBridge` (`ai_core/intelligence/bluesky_learning_bridge.py:108`) as "external-domain in `ai_core/intelligence/`" — implying LearningBridge subclass semantics. At HEAD: **on the search patterns `class .*LearningBridge` + `class .*LearningLoop` + `class .*FeedbackLoop` across `ai_core/intelligence/` + `intelligence/` + `core/learning_bridges/`,** neither inherits from `LearningBridge` abstract (`core/learning_bridges/base.py:13`). Both are standalone classes. **Language caveat per Rigby SIGN cycle 1 fold #1:** the audit found no additional `LearningBridge`-named subclasses under those search patterns, but "bridge-like" components that don't carry the "Bridge" name (e.g., `*Adapter`, `*Emitter`, `*Ingester`, `*Connector`, `*Collector`) may exist and were not exhaustively swept — post-arc R10 companion. Runtime polymorphism risk if MasterOrchestrator or any consumer expects contract; observability risk if bridges are treated as fungible by name. **Recommendation:** either (a) migrate to LearningBridge ABC (post-arc T-slot), or (b) rename to `*LearningExternalCollector` / `*InsightGenerator` to signal they are NOT bridges.

### F3 (HIGH) — Parent §3.C Q4 AgentLearningSession claim imprecise (multi-drift)

Parent §3.C Q4: "AgentLearningSession is deleted per S1244 migration 0002 — verify it's truly gone + no orphan callers." At HEAD:

1. **Migration offset drift:** S1244 delete migration is at `core/migrations/0368_session_1244_delete_agentlearningsession.py` (0368 not 0002).
2. **Scope drift:** S1244 deleted ONLY `core.AgentLearningSession` (see `core/migrations/0368_...py` docstring). Migration docstring specifically notes: "Was registered in both `core.AgentLearningSession` (this) and `ai_intelligence.AgentLearningSession` (in ai_core.intelligence.models). The ai_intelligence variant has a writer in `persistent_learning_engine.py:65` (gracefully wrapped in try/except)."
3. **Alive-at-HEAD drift:** `ai_intelligence.AgentLearningSession` (`ai_core/intelligence/models.py:211`) is ALIVE with a single writer at `ai_core/intelligence/persistent_learning_engine.py:65-77` (wrapped `transaction.atomic() + try/except`). Retention SAVED-FOREVER.

Multi-drift confirms parent §3.C Q4 needs a fold to name (a) both variants historically existed, (b) S1244 deleted core.* only, (c) ai_intelligence.* remains alive with single writer.

### F4 (HIGH) — Duplicate FILES with same class name

Two distinct pairs at HEAD:

**BoardroomLearningService x2:**
- `core/services/boardroom_learning.py:27` — 449 LOC — Session 602 — "ChatGPT weighted learning formula for Boardroom decisions" — 3 callers (`views_agent_learning.py:2509, :2548`; `decision_prioritization.py:81`).
- `core/services/boardroom_learning_service.py:32` — 420 LOC — Session 940 — "Records user boardroom decisions for PA learning" — 4 callers (`td_handlers_agents.py:4450, :4522, :4576, :4619`).

Different purposes; different call signatures; same class name; different modules.

**UnifiedLearningPipeline x2:**
- `core/unified_learning_pipeline.py:9` — 55 LOC — "Cross-domain learning: Sports → Job matching" — 2 callers (`sports_betting_bridge.py:297` imports `LearningInsight` + `LearningType` from it; `scripts/testing/test_phase3_integration.py:21`).
- `ai_core/intelligence/unified_learning_pipeline.py:54` — 609 LOC — "Complete Spider-to-Agent Learning System" — 2 callers (`learning_metrics_dashboard.py:238, :445`).

Both alive. Different architectures. Same class name.

**Collision mechanism (Rigby SIGN cycle 1 fold #3 — explicit statement per pair):**

Python's `from X.Y import ClassName` resolves the class from whichever module path is specified — there is no runtime collision (both modules load independently, both classes exist). The RISK surface is developer-side: (a) IDE autocomplete + go-to-definition can land on either module; (b) grep-based search returns two hits and the wrong file may be edited; (c) a future contributor unaware of the split may import "the" `BoardroomLearningService` expecting one behavior and get the other; (d) refactor tools that assume unique class names will silently fail; (e) documentation that says "BoardroomLearningService does X" is now ambiguous unless it qualifies the module path.

**Blast radius per pair:**
- BoardroomLearningService: 3 callers on the Session 602 (weighted-formula) variant + 4 callers on the Session 940 (PA-feedback) variant = **7 total production call sites** across `views_agent_learning.py`, `decision_prioritization.py`, and `td_handlers_agents.py`. Wrong-import bug would surface as `AttributeError` (missing method) rather than silent behavior drift because the class contracts are distinct enough. Detection-time: minutes to hours.
- UnifiedLearningPipeline: 2 callers on the core (cross-domain) variant + 2 callers on the ai_core (async orchestrator) variant = **4 total production call sites** across `sports_betting_bridge.py`, `test_phase3_integration.py`, and `learning_metrics_dashboard.py`. Wrong-import bug would surface as either `ImportError` (missing symbol) or `AttributeError` (wrong signature) — the two variants export different auxiliary types (`LearningInsight`/`LearningType` from core; different API from ai_core). Detection-time: minutes.

**Severity HIGH because:** (a) both pairs have active consumers on both sides of the collision; (b) both silent-import risks compound with each new caller added over time; (c) diagnosing a wrong-import bug requires human recognition that two modules share a class name — grep can hide this; (d) documentation ambiguity affects future-maintainer confidence. NOT CRITICAL because (a) both current call-site sets are correct (right module for right purpose); (b) the collision failure mode is loud (`AttributeError` / `ImportError`), not silent behavior drift. Post-arc T-slot: canonical-verdict ADR per file — options are (1) rename one variant, (2) merge into single canonical file, or (3) explicit docstring "collision-warning" + `__all__` guard.

### F5 (MED) — F5 correlation-primitive `learning_event_id` HYPOTHESIS THIRD application — HYPOTHESIS REMAINS. Cross-system-primitive DISPROVEN.

Parent §2.6 row #3: "learning_event_id / agent_learning_id — HYPOTHESIS: learning_event_id is a cross-source primitive whose provenance (HAI-mediated vs bridge-autonomous) is NOT tagged at schema level. Would need `source_kind` enum to distinguish."

Verification at HEAD (grep `learning_event_id|agent_learning_id` across all `.py`): **4 hits across 2 files, both in `ai_core/intelligence/`**:
- `ai_core/intelligence/persistent_learning_engine.py:88` — `'learning_event_id': None` (default in results dict)
- `ai_core/intelligence/persistent_learning_engine.py:101` — `processing_results['learning_event_id'] = str(learning_event.event_id)` (write)
- `ai_core/intelligence/persistent_learning_engine.py:264` — `result.get('learning_event_id')` (conditional check)
- `ai_core/intelligence/embedding_generator.py:382` — `result['learning_event_id'] = str(embedding.learning_event.event_id)` (write)

**Zero cross-domain hits for the ID-primitive name.** Not referenced from Group 1300 core models, not from Group 1400 revenue, Group 1500 sports, Group 1600 content, Group 1700 observability, Group 1800 human_attention (Cat A/B/C bridges), or PA plane.

**Serialization-boundary caveat (Rigby SIGN cycle 1 fold #4 — search-scope discipline).** Primitives sometimes travel across systems as opaque strings inside JSON payloads, `metadata[...]` dicts, or log lines rather than as typed IDs. Broader search grepping for `learning_event` (not the `_id` suffix, allowing the string tag to surface) returned:
- `content_type='learning_event'` @ `ai_core/intelligence/embedding_generator.py:141` — internal ai_core scope.
- `source_type: 'learning_event'` @ `ai_core/intelligence/knowledge_base_manager.py:35, :218` — internal ai_core scope.
- `content_type` field with `'learning_event'` as choice @ `ai_core/intelligence/models.py:182` — internal ai_core scope.
- `'type': 'learning_event'` @ `core/learning_feed_consumer.py:156` — consumer payload label.
- `'type': 'learning_event'` @ `core/project_intelligence_consumer.py:519, :591` — consumer payload label (2 sites).

These are **TYPE-STRING TAGS**, not ID primitives — they classify payload categories in WebSocket / consumer / knowledge-base contexts. The ID-primitive `learning_event_id` itself does NOT travel through these consumer payloads. The verdict on `learning_event_id` as CROSS-SYSTEM PRIMITIVE holds: DOMAIN-INTERNAL. However, `learning_event` AS TYPE-STRING has 6 hits across 4 additional files (learning_feed_consumer + project_intelligence_consumer + knowledge_base_manager + ai_core models), suggesting the type-classification vocabulary IS shared across app boundaries — a distinct observation from the primitive-box verdict but worth noting for future arcs.

**Verdict:** `learning_event_id` is DOMAIN-INTERNAL to `ai_core/intelligence/` — it correlates the `AgentLearningEvent` → `LearningEmbedding` chain within one subsystem. It is NOT a cross-system architectural spine primitive.

**Contrast pattern:**
- S1801 F5 `HAI_item_id`: PASSED cross-system (8-10 domains, 25+ direct-create sites, VERIFIED-AT-CHILD).
- S1802 F5 `feedback_record_id`: FAILED cross-system (0 non-Cat-B hits, HYPOTHESIS REMAINS with DISPROVEN cross-system verdict).
- **S1803 F5 `learning_event_id`: FAILED cross-system (0 non-ai_core hits, HYPOTHESIS REMAINS with DISPROVEN cross-system verdict).**

**MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1803 close.** The primitive-box discipline itself remains a valid research methodology (naming a HYPOTHESIS + verifying/refuting at child audit is load-bearing research), but the SECOND consecutive DISPROVED-CROSS-SYSTEM outcome signals a meta-methodology finding: **primitive-box hypotheses that fail cross-system verification are useful signals that the named primitive is domain-internal, not architectural spine.** This meta-methodology finding is a candidate for §10 promotion in the Group 1800 xx99 canonical summary (S1899 close).

### F6 (MED) — Writer-plane split not surfaced in parent scope

Parent §3.C names "AgentLearning (Group 1300 territory), UserAgentLearning (Group 1300 territory), AgentLearningConnection, LearningInsight dataclass" as downstream models without clarifying that:

- **AgentLearning** is written by Cat B FeedbackProcessor (2 sites) + 7 non-bridge sites — ZERO Cat C bridge writers.
- **UserAgentLearning** is written by Cat C bridges (22 sites) + 4 non-bridge cross-domain writers — ZERO Cat B FeedbackProcessor writes.

Two distinct writer planes on two distinct models. Parent §3.C implicitly treats them as fungible. **Recommendation for fold:** clarify at parent §3.C that Cat B and Cat C write DIFFERENT models with DIFFERENT key semantics.

### F7 (HIGH) — Parent §3.C "4+ duplicate service candidates" undercounted

Parent §3.C names 5 duplicate service candidates: AgentLearningService + AgentLearningSystem + AgentLearningEngine + PersistentLearningEngine + PALearningInsightsService. At HEAD, on search patterns `class .*Learning.*(Service|Engine|System|Pipeline|Orchestrator|Loop)` across `core/`, `ai_core/`, `intelligence/`, and `self_awareness/`: **16+ learning-service classes** (see §5 full catalog, including the S1803 Rigby SIGN cycle 1 fold #2 addition of `LearningPatternEngine` @ `core/services/learning_pattern_engine.py:28` — a 1500-LOC heavy-consumer service with 10+ import sites that would have been missed without the SIGN-driven language-softening pass). Undercounted by ~11 classes. This is not a fatal error — parent scoping accepts scope-magnet risk — but the "4+ duplicate" framing understates the surface. **Language caveat:** the S1803 search patterns are enumerated in §20.3 and are grep-based on the "Learning" naming prefix; classes that participate in the learning plane without carrying the "Learning" prefix (e.g., `KnowledgeFirstRouter`, `WeightedLearning`-adjacent `PatternMining`) may exist and were not exhaustively swept. Recommendation for fold: parent §3.C should read "5+ named duplicates plus 11+ additional learning-service classes surfaced by Cat C inventory, verified on `class .*Learning.*(Service|Engine|System|Pipeline|Orchestrator|Loop)` search patterns; non-Learning-named participants remain post-arc R6 companion scope."

### F8 (MED) — LearningOrchestrator missing AutoConsultationLearningLoop registration (plausible drift, framing per Rigby SIGN cycle 1 fold #5)

`core/self_development/learning_orchestrator.py:38-49` `_initialize_bridges()` declares 8-bridge registry. AutoConsultationLearningLoop (`advisor_feedback_bridge.py:250`) is NOT in the registry despite being an active LearningBridge subclass at HEAD. The orchestrator's docstring at :6 says "Connects ALL learning systems together" — the "ALL" claim is inaccurate.

**Plausible drift framing (per Rigby SIGN fold):** treat as either **design-intent gap** OR **incomplete wiring**, without pre-selecting which:
1. **Design-intent gap** — AutoConsultationLearningLoop is invocation-driven from audit coordinators (not signal-driven). Orchestrator design may have chosen to exclude invocation-driven bridges from the registry because they don't participate in the signal-fanout mechanism the orchestrator coordinates. If this is the intent, the docstring "ALL learning systems" is misleading and should be clarified.
2. **Incomplete wiring** — orchestrator was authored before AutoConsultation was extracted from AdvisorFeedback (see `advisor_feedback_bridge.py:250` line-number position within same file as AdvisorFeedbackLearningLoop @ :50), and the registry was never updated when the second class was added.

Cat C cannot resolve which is correct without design-intent statement from the orchestrator author (R3). Both interpretations are consistent with the observed state; the fold framing preserves ambiguity per Rigby SIGN evidence discipline.

### F9 (LOW) — Parent §3.C AgentExecutionLearningLoop cross-arc phrasing imprecise

Parent §3.C: "AgentExecutionLearningLoop is Cat C for THIS arc but its output goes to Group 1300 Memory + Group 1700 Observability Cat C AgentExecution post_save receiver (S1703 §10 finding — verified)."

At HEAD, the bridge's OUTPUT lands only in Group 1300 (UserAgentLearning writes @ :174, :241 + Agent.metrics update @ :280 + trigger_learning_cycle call to `core/self_development/learning_orchestrator.py`). Group 1700's involvement is that a SEPARATE post_save receiver on the same `AgentExecution` source model exists in `rigby_delegation_signals.py` (Group 1700 territory per S1703). The bridge does NOT emit to Group 1700 — the observability layer shares the source signal, not the bridge output.

Recommended phrasing: "AgentExecutionLearningLoop shares the AgentExecution post_save signal with a separate Group 1700 Observability receiver (Rigby delegation signals). Cat C output is Group 1300 only."

### F10 (SPECULATIVE) — 4 cross-domain direct UserAgentLearning writers OUTSIDE bridge abstraction

Beyond the 22 bridge writer sites, 4 additional production sites write `UserAgentLearning` directly:
- `revenue/models.py:144`
- `core/models/jobs/models.py:134`
- `core/models/jobs/models.py:191`
- `core/services/td_handlers_content.py:222`

These bypass the LearningBridge `.process_event()` contract entirely. They may be legacy (pre-Session-1115 ABC migration) or intentional (specific domain models chose to write learning rows without going through bridges). Cat C cannot resolve intent without design-review (R6).

## 15. Known Technical Debt

### D1 (HIGH) — Duplicate-file name-collision surface (F4 companion)

BoardroomLearningService x2 + UnifiedLearningPipeline x2 (see F4). Silent import ambiguity. Post-arc consolidation ADR per file needed (R1).

### D2 (MED) — Zero `transaction.atomic()` on multi-model writes across 9 bridges

25+ `UserAgentLearning.get_or_create` + `update_or_create` sites, plus co-writes to Agent metrics (agent_execution_bridge.py), AgentMemory (sports_betting_bridge.py) — none wrapped in `transaction.atomic()`. Partial-write corruption risk if bridge dies mid-flow. Parallel to S1802 D1 pattern.

### D3 (MED) — Signal handler silent Exception swallow (parallel S1801 D5 + S1802 D3)

6+ sites across bridges silently catch `Exception` and log warning without re-raising. Examples:
- `sports_betting_bridge.py:277-280` — `except Exception as e: logger.warning(...)` + continue
- `agent_execution_bridge.py:322-324` — signal handler `except Exception as e: logger.error(...) exc_info=True`
- `personalization_bridge.py:96-106` — try/except ImportError blocks wrap signal handlers; if either input model is missing, signals silently don't register.

Combined with D4 (missing observability signal), a broken bridge fails silently in production. Parallel to S1801 D5 + S1802 D3.

### D4 (MED) — Missing observability signal on bridge dispatch

No `pre_dispatch` / `post_dispatch` signal or telemetry emit exists on bridge write path. If a bridge silently drops an event (via D3 pattern), zero downstream visibility. Parallel to S1801 D5 + S1802 D4.

### D5 (MED) — Best-effort silent-skip on FK lookups (parallel S1802 D5)

- `sports_betting_bridge.py:124` catches `BankrollManagement.DoesNotExist` and continues.
- `sports_betting_bridge.py:551, :626` catches exceptions on `AgentMemory.objects.create` and logs warning.
- `personalization_bridge.py:473-485` + `:488-529` — dual `try/except ImportError` around signal registration.

No dead-letter queue, no retry, no aggregation. Learning row silently missing.

### D6 (MED) — AutoConsultationLearningLoop system-user race condition

`advisor_feedback_bridge.py:405-421` — `_get_system_user()` catches `User.DoesNotExist` and creates `system_advisor_tracker` user with hardcoded email + obfuscated password. Side-effect on User table during a learning write path. Concurrent invocations from parallel audit coordinators could race on User.objects.get → create. Recommended: (a) idempotent get_or_create OR (b) explicit init-time system user seed via management command.

### D7 (MED) — Retention SAVED-FOREVER (parallel S1801 F6/D7 + S1802 F6/D7)

All 8 Cat C target models are SAVED-FOREVER at operational level. No purge job. `UserAgentLearning.expires_at` field exists at schema but no operational cleanup task drives it. Combined with S1801 + S1802 findings, the Group 1800 xx99 §5 canonical summary faces a MULTI-MODEL retention-posture ADR item (R7 paired with S1801 R1 + S1802 R1).

### D8 (LOW-MED) — Missing `source_kind` field on `AgentLearning` + `UserAgentLearning`

Parent §2.6 F5 hypothesis: "learning_event_id is a cross-source primitive whose provenance (HAI-mediated vs bridge-autonomous) is NOT tagged at schema level. Would need `source_kind` enum to distinguish." Verified at HEAD: no `source_kind`, no `origin`, no `writer_plane` field on either model. Cat C write-path and Cat B write-path are indistinguishable in schema. Post-arc: `source_kind` schema-change ADR (R8), joint Group 1300 + Group 1800 scope.

### D9 (LOW) — Missing composite indexes on writer FKs

`AgentLearning.teacher_agent` + `student_agent` FKs at `core/models_unified_system.py:~3660` have no `db_index=True` or composite `index_together` / `Meta.indexes` declaration. `UserAgentLearning` composite `(user, agent_name, learning_domain)` is used for get_or_create but no explicit index confirmed. Read-heavy learning queries will full-scan. Parallel S1801 D9 + S1802 D9.

### D10 (LOW-SPECULATIVE) — Dead lazy-import fallback in RedditLearningBridge

`ai_core/intelligence/reddit_learning_bridge.py:14-30` (lazy-import block for RedditHandler): if import fails, bridge falls back to mock classes and remains callable with zero real Reddit data. No observability signal fires. Parallel S1802 D10 pattern.

## 16. Boundary Violations

### 16.1 SportsBettingLearningBridge cross-app writes

`core/learning_bridges/sports_betting_bridge.py` reads from Group 1500 Sports models (`sports.models.BankrollManagement`, `UserBet`, `MLPrediction` @ :112, :237, :298) and writes to BOTH `UserAgentLearning` (Group 1300 Memory) AND `AgentMemory` (Group 1300 Memory) @ :532, :606.

**Cat C scope allows:**
- Cross-arc READS from source domain (sports.models is Group 1500's territory).
- Writes to Group 1300 UserAgentLearning (bridge-writer-contract-scope per parent §3.C).

**Cat C scope does NOT explicitly cover:**
- Writes to `AgentMemory` (Group 1300 Memory territory but not named in parent §3.C's "downstream models" catalog).

This is a scope-parent-catalog gap, not a violation per se. AgentMemory writes from a LearningBridge are unusual — bridges typically write UserAgentLearning. Post-arc recommendation: catalog AgentMemory writers separately (R6 companion).

### 16.2 4 non-bridge writers to UserAgentLearning (see F10)

`revenue/models.py`, `core/models/jobs/models.py`, `core/services/td_handlers_content.py` all write `UserAgentLearning` directly without going through a `LearningBridge` subclass. This bypasses the bridge abstraction and the base class contract's implicit lifecycle guarantees. Not a boundary violation (Cat C claims the writer plane, not the bridge-only writer plane) but a design-consistency question. Post-arc R6.

## 17. Duplicate or Overlapping Systems

Cat C is the arc's DENSEST duplicate-surface region. Full inventory:

### 17.1 Duplicate FILES with same class name

- `BoardroomLearningService` x2 (F4) — Session 602 weighted formula (`boardroom_learning.py`) vs Session 940 PA feedback loop (`boardroom_learning_service.py`). BOTH alive with active consumers. Import-path resolution ambiguity.
- `UnifiedLearningPipeline` x2 (F4) — 55-LOC core cross-domain applier vs 609-LOC ai_core async orchestrator. BOTH alive with active consumers.

### 17.2 Duplicate MODELS across apps

- `AgentLearningSession` was historically defined in BOTH `core.AgentLearningSession` (deleted at S1244) AND `ai_intelligence.AgentLearningSession` (alive at HEAD). Cross-app name collision that was PARTIALLY resolved by S1244 dedup — see F3.
- `LearningInsight` was historically defined in BOTH `core.LearningInsight` (alive) AND `ai_intelligence.LearningInsight` (deleted at S1244 per comment @ `ai_core/intelligence/models.py:259`). Fully resolved.

### 17.3 Overlapping LEARNING-SERVICE surface

15+ classes named `*Learning*Service|Engine|System|Pipeline|Orchestrator|Loop` at HEAD (see §5 full inventory). Semantic overlap between:

- `AgentLearningService` (core) vs `AgentLearningSystem` (intelligence) vs `AgentLearningEngine` (ai_core intelligence) — three classes with near-identical names, three different apps, unclear canonical.
- `LearningOrchestrator` (core self_development) vs `LiveLearningOrchestrator` (core services) vs `SpiderLearningOrchestrator` (ai_core intelligence) — three orchestrators with different scopes.
- `UnifiedLearningPipeline` x2 (see F4) — direct duplicate.
- `PersistentLearningEngine` (ai_core) vs `LearningLoopOrchestrator` (referenced in §6.1 REST) — potential overlap.

### 17.4 Overlapping BRIDGE surface

- `AdvisorFeedbackLearningLoop` vs `AutoConsultationLearningLoop` — both in `advisor_feedback_bridge.py`, both write `UserAgentLearning` from advisor-domain signals. Semantic overlap: one from `AdvisorConsultationFeedback` post_save, one from audit-coordinator dict. Could arguably be combined; F.d canonical verdict.
- `SpiderDataLearningLoop` (core bridge) vs `SpiderLearningOrchestrator` (ai_core) vs `SpiderLearningLoop` (intelligence) — three spider-domain "learning" classes, three apps, three abstractions.
- `PersonalizationFeedbackLoop` vs `PALearningInsightsService` — semantic overlap in personalization-plane learning.

**Cat C verdict:** the duplicate-service surface is a **CATALOG only** at S1803. Canonical-verdict ADRs per duplicate pair are POST-arc T-slot per playbook §14.5 no-implementation rule, deferred to Cat F sub-slot F.d @ S1806.

## 18. Ownership Gaps

**No `CODEOWNERS` file exists at HEAD** (confirmed via `Glob CODEOWNERS`). Bridge code has mixed session-provenance (Sessions 602, 930, 940, 991, 1115, 1244, etc.) but no assigned human/team owner. If a bridge produces a bad learning row, bug triage lands nowhere specific.

**Cross-cutting ownership gap:** who owns the LearningOrchestrator registry drift (F8)? Who owns the duplicate-file name collision (F4)? Who owns the `ai_intelligence.AgentLearningSession` alive-at-HEAD posture (F3)? These are three distinct architectural decisions that ownership assignment could resolve.

Recommendation R11 (post-arc, LOW): add a `CODEOWNERS` entry for `core/learning_bridges/` + `ai_core/intelligence/` + `core/self_development/` + `core/services/*learning*` naming a single learning-plane owner.

## 19. Recommended Future Research

Post-arc T-slot items with Chris-gated priority ordering. Ordering here is post-SIGN (Rigby's architecture-leverage ranking landed via SIGN cycle 1 Q4 fold — R0 elevated to top; R1 retains second position; balance of R2-R11 unchanged pending Chris ratification).

### R0 (POST-ARC, HIGH — Rigby SIGN cycle 1 Q4 fold-added top priority) — Unified learning-plane contract ADR

Rigby's SIGN cycle 1 Q4 verdict named "unify/clarify the 'learning plane contract'" as the most important next research. Scope: (a) single canonical pipeline / service entrypoint (replaces the current 16+ learning-service class surface with a documented canonical hierarchy), (b) single event schema for bridge dispatch (paired with R5 observability signal), (c) explicit retention + observability + atomicity contract on canonical entrypoint. This is the design-level response to the F4+D2+D3+D7 compound-impact framing in §13. Group 1800 xx99 T0/Gate candidate; potential joint scope with Group 1300 Memory arc extension work.


### R1 (POST-ARC, HIGH) — Duplicate-file consolidation ADR

BoardroomLearningService x2 + UnifiedLearningPipeline x2 canonical-verdict ADRs per file (F4). Options: (a) rename one variant, (b) merge into single canonical file, (c) explicit ImportError guard + docstring warning. Owning group: Group 1800 xx99 T0/Gate candidate.

### R2 (POST-ARC, HIGH) — ai_intelligence.AgentLearningSession posture ADR

Is the ai_intelligence variant of AgentLearningSession still needed given S1244 deleted the core variant? If yes: document its scope + name-collision handling. If no: delete migration + wire out `persistent_learning_engine.py:65` writer. Owning group: Group 1800 xx99 T1 candidate paired with F3.

### R3 (POST-ARC, MED) — LearningOrchestrator registry completeness

F8: is AutoConsultationLearningLoop's omission from `_initialize_bridges()` intentional (invocation-driven bridge exclusion) or drift? If intentional, document the exclusion policy at :38-49. If drift, add AutoConsultation to registry. Owning group: Group 1800 xx99 T2.

### R4 (POST-ARC, MED) — F5 durability meta-methodology posture

Two of three F5 primitive-box HYPOTHESES (S1802 feedback_record_id + S1803 learning_event_id) DISPROVED cross-system. Only S1801 HAI_item_id passed. Meta-methodology finding for Group 1800 xx99 §5 posture-decision brief + §10 meta-methodology retrospective: primitive-box discipline REMAINS valid research methodology but 2-of-3 negative results signal that "correlation primitives" are more often domain-internal than architectural spine. §10 promotion candidate.

### R5 (POST-ARC, MED) — Bridge dispatch observability signal (parallel S1801 R6 + S1802 R6)

D3 + D4 combined: bridges silently swallow exceptions and emit no dispatch telemetry. Add `pre_dispatch` + `post_dispatch` signals on `LearningBridge.process_event(...)` OR emit `BridgeDispatchEvent` OR log structured `[CAT_C_BRIDGE_DISPATCH]` line. Paired with S1801 R6 (HAI observability) + S1802 R6 (record_decision observability) — potential common observability infrastructure.

### R6 (POST-ARC, MED) — 4 non-bridge UserAgentLearning writers routing decision

F10: `revenue/models.py:144`, `core/models/jobs/models.py:134, :191`, `core/services/td_handlers_content.py:222` all write `UserAgentLearning` directly. Options: (a) migrate to bridge abstraction, (b) declare them intentionally-non-bridged (with rationale), (c) add non-bridge writer catalog to bridge docs. AgentMemory writer catalog is a companion item.

### R7 (POST-ARC, MED) — Retention posture ADR (paired S1801 R1 + S1802 R1)

D7: SAVED-FOREVER across `AgentLearning` + `UserAgentLearning` + `LearningInsight` + `AgentLearningConnection` + `ai_intelligence.AgentLearningSession` + `LearningDocument` + `LearningEmbedding`. Parallel HAI-plane SAVED-FOREVER (S1801 F6) + Cat B HumanFeedbackRecord SAVED-FOREVER (S1802 F6). Group 1800 xx99 T0/Gate candidate: unified retention ADR across the entire domain.

### R8 (POST-ARC, MED) — `source_kind` schema field on AgentLearning + UserAgentLearning

D8: no provenance tagging on learning rows. Cat B writes and Cat C writes are indistinguishable in schema. Adding `source_kind` enum {HAI_mediated, autonomous_bridge, non_bridge_direct, other} enables downstream cross-plane analytics and retention differentiation. Joint Group 1300 + Group 1800 schema-change ADR.

### R9 (POST-ARC, LOW-MED) — Transaction atomicity on bridge multi-model writes

D2: wrap `.get_or_create` + `.save()` combos and multi-model write blocks in `transaction.atomic()`. Local per-bridge change; low blast radius.

### R10 (POST-ARC, LOW) — RedditLearningBridge + BlueskyLearningBridge ABC contract migration

F2: rename or refactor Reddit+Bluesky classes so name matches ABC-contract state. Either migrate to `LearningBridge` subclass or rename to non-bridge idiom.

### R11 (POST-ARC, LOW) — CODEOWNERS entry for learning plane

§18 ownership gap: add `CODEOWNERS` entry for `core/learning_bridges/` + `ai_core/intelligence/` + `core/self_development/` + `core/services/*learning*`.

## 20. Appendix

### 20.1 Files inspected (grep-verified)

**Bridges (9 subclass, 8 files):**
- `core/learning_bridges/base.py`
- `core/learning_bridges/personalization_bridge.py`
- `core/learning_bridges/spider_data_bridge.py`
- `core/learning_bridges/collaboration_bridge.py`
- `core/learning_bridges/advisor_feedback_bridge.py`
- `core/learning_bridges/application_outcome_bridge.py`
- `core/learning_bridges/agent_execution_bridge.py`
- `core/learning_bridges/sports_betting_bridge.py`
- `core/learning_bridges/revenue_attribution_bridge.py`

**External bridges (2):**
- `ai_core/intelligence/reddit_learning_bridge.py`
- `ai_core/intelligence/bluesky_learning_bridge.py`

**Services (15+ inventoried):**
- `core/services/agent_learning_service.py`
- `core/services/pa_learning_insights.py`
- `core/services/weighted_learning.py`
- `core/services/pipeline_learning.py`
- `core/services/boardroom_learning.py`
- `core/services/boardroom_learning_service.py`
- `core/services/resolve_learning.py`
- `core/services/live_learning_orchestrator.py`
- `core/services/implicit_learning.py`
- `core/services/pa_tool_learning_enricher.py`
- `core/services/tool_dispatcher.py`
- `core/services/td_handlers_agents.py`
- `core/services/td_handlers_content.py`
- `core/services/decision_prioritization.py`
- `core/unified_learning_pipeline.py`
- `core/self_development/learning_orchestrator.py`
- `intelligence/agent_learning.py`
- `intelligence/spider_quality_tracker.py`
- `intelligence/connect_all_agents.py`
- `intelligence/spider_agent_connector.py`
- `intelligence/learning_path_orchestrator.py`
- `ai_core/intelligence/agent_learning_engine.py`
- `ai_core/intelligence/persistent_learning_engine.py`
- `ai_core/intelligence/spider_learning_orchestrator.py`
- `ai_core/intelligence/unified_learning_pipeline.py`
- `ai_core/intelligence/learning_metrics_dashboard.py`
- `ai_core/intelligence/embedding_generator.py`
- `ai_core/intelligence/document_generator.py`
- `self_awareness/intelligence.py`

**Models:**
- `core/models_unified_system.py` (AgentLearning + UserAgentLearning + AgentLearningConnection)
- `core/models/ai_learning/models.py` (LearningInsight core variant)
- `core/models_feedback_processing.py` (FeedbackProcessor writes to AgentLearning + LearningInsight)
- `ai_core/intelligence/models.py` (AgentLearningSession + LearningDocument + LearningEmbedding ai_core variants)

**Migrations:**
- `core/migrations/0368_session_1244_delete_agentlearningsession.py`
- `ai_core/migrations/0002_alter_commandexecution_id_alter_databasechange_id_and_more.py` (CREATE for ai_intelligence.AgentLearningSession)
- `intelligence/migrations/0001_initial.py`, `0002_earningrecord_...py`, `0003_session_1243_...py`

**Views + REST:**
- `core/views_agent_learning.py`
- `core/views_learning_loop.py`
- `core/views_diagnostics.py`

**Tasks + Beat:**
- `core/tasks.py`
- `core/tasks_agents.py`
- `core/celery.py`

**Management commands:**
- `core/management/commands/bootstrap_learning_system.py`
- `core/management/commands/build_learning_bridge_audit.py`
- `core/management/commands/connect_all_agents.py`
- 8+ additional `*learning*` commands.

### 20.2 Docs inspected

- `docs/PLATFORM_WHAT_IT_IS.md`
- `docs/PLATFORM_INVENTORY.md`
- `docs/topics/agent-system.md`
- `docs/topics/personal-assistant.md`
- `docs/topics/initiative-pipeline.md`
- `docs/topics/spider-network.md`
- `docs/topics/frontend.md`
- `docs/AGENTS.md`
- `docs/SERVICES.md`
- `docs/AUDIT_FINDINGS.md`
- `docs/LEARNING_BRIDGE_AUDIT.md`
- `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` (parent)
- `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` (S1801 sibling)
- `docs/research/domains/human_attention/1802_human_attention_cat_b_feedback_processor_child_audit.md` (S1802 sibling)
- `docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md` (cross-arc)
- `docs/research/domains/memory/1399_memory_canonical_summary.md` (Group 1300 close)
- `docs/research/platform/cross_domain_integration_audit.md` (S1274 canonical)
- `00-START-NEXT-SESSION.md`
- Session handoffs S1115 + S1244 + S991 + S930.

### 20.3 Grep patterns used

- `class\s+\w+.*(?:LearningBridge|LearningLoop|FeedbackLoop|LearningEngine|LearningSystem|LearningService|LearningInsights|LearningPipeline|LearningSession|LearningOrchestrator|LearningDashboard)` — service + bridge inventory
- `UserAgentLearning\.objects\.(get_or_create|update_or_create|create)` — writer count
- `AgentLearning\.objects\.(create|get_or_create|update_or_create)` — writer count
- `learning_event_id|agent_learning_id` — F5 cross-system verification
- `from\s+core\.services\.boardroom_learning(_service)?\s+import|from\s+.*unified_learning_pipeline\s+import` — F4 name-collision consumers
- `HumanAttentionItem|HumanFeedbackRecord|record_decision|HAI_item_id|attention_item_id` — HAI-mediation check per bridge
- `AgentMemory|from\s+sports\.models|from\s+sports` — boundary violation check on sports_betting_bridge

### 20.4 Unresolved unknowns

- `PALearningInsightsService` (core/services/pa_learning_insights.py:24) consumer surface unverified — see §5.1.
- `AgentLearningSystem` (intelligence/agent_learning.py:22) — 3 caller sites found via grep but purpose unclear.
- `MetaLearningEngine` (self_awareness/intelligence.py:70) — 0 external caller sites verified in this audit.
- `ResolveLearningService` purpose statement — grep-verified callers (3) but internals not read.
- `LearningOrchestrator` intent for AutoConsultationLearningLoop omission (F8) — cannot resolve without design-review.
- Downstream READ consumers of `UserAgentLearning` rows — Cat C bounded to writer plane; reader inventory is Cat A/D territory.
- Whether the 4 non-bridge cross-domain UserAgentLearning writers (F10) predate the Session 1115 ABC migration.
- `LearningInsight` (core variant) writer count — conditional lazy-load at `models_feedback_processing.py:257` guarded by `if self.LearningInsight` — runtime-dependent fire path.
- Auto-generated `docs/LEARNING_BRIDGE_AUDIT.md` freshness at HEAD (not verified against latest `build_learning_bridge_audit.py` run).

### 20.5 Conflicts between sources

- Explore Agent 1 vs Agent 2 on UserAgentLearning writer count: Agent 1 said "0 production sites"; Agent 2 said "9 bridges write." Post-Explore verifier resolved to Agent 2's claim (25+ verified sites). See §4.2.
- Explore Agent 2 vs Agent 6 on BoardroomLearningService duplicate verdict: Agent 2 said "DIFFERENT purposes, NOT duplicates"; Agent 6 said "CRITICAL duplicate FILE." Post-Explore verifier: BOTH accurate — different purposes AND same class name AND both alive with consumers = name-collision risk. See F4.
- Explore Agent 4 vs parent §3.C on AgentExecutionLearningLoop cross-arc phrasing: Agent 4 flagged "parent claim mismatch"; parent §3.C is technically imprecise (bridge output → Group 1300 only; Group 1700 shares source signal via separate receiver). See F9.

### 20.6 Verifier-loop corrections (Rigby SIGN cycle 1 fold record — landed pre-commit)

Rigby SIGN cycle 1 on arc pin `pa-ae5931ea706b4537` at 2026-07-03 returned **SIGN-with-edits at High confidence 0.84**. D48 27th arm turn 1 CLEAN; 22nd consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch 4-question criterion. Q4 4-question format satisfied. Below fold record.

**Fold #1 — Language softening on "ONLY" and "complete" claims.** Rigby flagged that absolute-language claims without explicit search-strategy notes carry over-claim risk. Landed at:
- F2 (§14) — external `*LearningBridge` classes: added "on the search patterns `class .*LearningBridge` + `class .*LearningLoop` + `class .*FeedbackLoop` across `ai_core/intelligence/` + `intelligence/` + `core/learning_bridges/`" with explicit caveat that "bridge-like" non-`Bridge`-named participants (Adapter/Emitter/Ingester/Connector/Collector) were not exhaustively swept — R10 companion.
- F7 (§14) — service catalog exhaustiveness: added "on search patterns `class .*Learning.*(Service|Engine|System|Pipeline|Orchestrator|Loop)`" + explicit caveat that non-`Learning`-named participants may exist — R6 companion.

**Fold #2 — Service catalog completeness pass.** Rigby's Q1 push produced a second grep pass that surfaced `LearningPatternEngine` @ `core/services/learning_pattern_engine.py:28` — a 1500-LOC heavy-consumer service with 10+ import sites (`core/tasks.py:516, :7816, :7854, :7896` + `core/conversation_orchestrator.py:329` + `core/agent_router.py:507` + `core/services/knowledge_first_router.py:177` + `core/services/context_tracking.py:81` + `core/personal_ai_assistant_enhanced.py:2279` + `intelligence/spider_agent_connector.py:262`). Added to §5.2 catalog; F7 count updated to 16+; Executive Summary count updated.

**Fold #3 — F4 explicit collision-mechanism + blast-radius per pair.** Landed at §14 F4. Added: (a) Python import resolution mechanism (no runtime collision but developer-side risk: IDE autocomplete, grep search hits, silent-refactor); (b) blast-radius per pair (7 call sites for BoardroomLearningService x2 + 4 call sites for UnifiedLearningPipeline x2); (c) failure-mode analysis (loud `AttributeError` / `ImportError`, not silent behavior drift — hence HIGH not CRITICAL); (d) three remediation options.

**Fold #4 — F5 serialization-boundary caveat.** Rigby's Q2 push produced a broader search for `learning_event` (not the `_id` suffix, allowing string-tag surfaces): 6 additional hits across 4 files (`core/learning_feed_consumer.py:156` + `core/project_intelligence_consumer.py:519, :591` + `ai_core/intelligence/knowledge_base_manager.py:35, :218` + `ai_core/intelligence/embedding_generator.py:141` + `ai_core/intelligence/models.py:182`) but ALL are TYPE-STRING TAGS classifying payload categories, NOT ID primitives. The verdict on `learning_event_id` as CROSS-SYSTEM PRIMITIVE holds: DOMAIN-INTERNAL. The serialization-boundary caveat itself is worth naming for future arcs — landed at F5 (§14).

**Fold #5 — F8 drift framing reframed as "plausible drift."** Landed at §14 F8. Reframed the two-interpretation split as neither pre-selected: "design-intent gap" OR "incomplete wiring" — Cat C cannot resolve without design-intent statement (R3). Fold preserves ambiguity per Rigby SIGN evidence discipline.

**Fold #6 (Q4 compound-impact framing) — Architecture-risk framing.** Rigby named "silent divergence + collision in learning infrastructure" as the biggest architectural risk. Landed at §13 architecture maturity as "Compound-impact framing" subsection: F4 + D2 + D3 + D7 combine to produce a "you can't trust what was learned, when, or why, and you can't reliably replay" failure mode. Rigby-recommended remediation is treating them as a SINGLE compound ticket, not four independent fixes.

**Fold #7 (Q4 R-slot ordering) — R0 elevated.** Rigby's Q4 "most important next research" verdict was "unify/clarify the learning plane contract." Landed at §19 as new R0 (POST-ARC, HIGH) above R1. Post-SIGN Chris-gate ordering: **R0 → R1 → R2 → balance**. Group 1800 xx99 T0/Gate candidate.

**Confidence signal verdict.** Confidence 0.84 (above the 0.80 threshold per S1801+S1802 arc-standard SIGN acceptance). D48 27th arm turn 1 substantive + on-topic + no worker-instability signals. Sub-pattern advancing per S1799 §10.2 MC-2 CODIFICATION-READY promotion path.

**Not folded (Q3 severity):** Rigby's response was truncated mid-Q3 D2/D3/D7 severity discussion. On the evidence returned, F4 HIGH is confirmed justified. D2/D3/D7 severity ratings unchanged pending Chris ratification (or Q3 follow-up ping if Chris directs). The compound-impact framing (Fold #6) partially addresses the severity conversation by naming that the combination is the real risk vector, whatever the individual severities.

### 20.7 F5 methodology interpretation note

The F5 correlation-primitive HYPOTHESIS box discipline is a research-process pattern first applied at S1700 parent §5 (per S1700 Rigby SIGN cycle 1 F5 MUST-FIX fold) and now on its third application (S1800 second application). The pattern names an expected cross-system primitive as HYPOTHESIS at parent-scoping time, then verifies/refutes at the corresponding child audit.

At Group 1800 close (post S1803 F5 outcome), the box results across three application rounds are:

| Row | Primitive | Verified at | Cross-system verdict |
|-----|-----------|-------------|----------------------|
| #1 | `HAI_item_id` | S1801 (Cat A) | **PASSED** — 8-10 domains, 25+ direct-create sites |
| #2 | `feedback_record_id` | S1802 (Cat B) | **FAILED** — 0 non-Cat-B hits |
| #3 | `learning_event_id` | S1803 (Cat C) | **FAILED** — 0 non-ai_core hits |

Two of three FAILED cross-system verification. This is a meta-methodology finding, not a research failure. The primitive-box DISCIPLINE ITSELF remains valid — naming a HYPOTHESIS is load-bearing scaffolding for evidence-gathering. But the pattern of hypothesizing cross-system primitives that turn out to be domain-internal signals that:

1. The team's intuition about "which primitives are architecturally spine" is over-optimistic.
2. Most correlation primitives are single-domain implementation details.
3. Only rarely do IDs earn cross-system spine status (HAI_item_id is the exception, not the rule).

The Group 1800 xx99 canonical summary (S1899) should include this meta-methodology finding in its §10 retrospective. It also weights toward Option B/C/D over Option A in the D80 posture-decision (if primitives don't cross domains, canonical unification is a design fiction).

**Framing note:** this §20.7 subsection interprets the primitive-box methodology from within a single child audit; it is NOT a canonical methodology verdict. Canonical verdict belongs to the xx99 canonical summary at S1899 close per playbook §11.3 §10 discipline. This subsection is a candidate methodology observation, not a rule.

### 20.8 Appendix — UserAgentLearning cross-domain direct writers (non-bridge inventory)

Beyond the 22 bridge writer sites (§3.2), 4 additional production sites write `UserAgentLearning` directly at HEAD, bypassing the `LearningBridge` abstraction:

| # | Site | Context | Note |
|---|------|---------|------|
| 1 | `revenue/models.py:144` | Revenue app model-layer write | Model method presumably; pre-Session-1115 pattern possible |
| 2 | `core/models/jobs/models.py:134` | Jobs app model-layer write | Model method |
| 3 | `core/models/jobs/models.py:191` | Jobs app model-layer write | Model method |
| 4 | `core/services/td_handlers_content.py:222` | PA tool handler for content operations | Handler-layer write; likely intentional (per-request context) |

Post-arc R6 evaluates whether these should migrate to bridge abstraction or remain intentionally non-bridged.

### 20.9 Frontmatter provenance

- Session: 1803
- Category: child_audit
- Child slot: P3
- Domain: human_attention
- Research group: 1800
- Playbook application: §11.2 EIGHTH application overall + THIRD under Group 1800
- Head commit: 69cf2dd1
- Prior children: 1801 (Cat A), 1802 (Cat B)
- Delegates to: none (Cat D + Cat E + Cat F children remain queued)
- Related arcs: Groups 1300, 1400, 1500, 1600, 1700
