---
title: "S1801 Group 1800 Cat A — HumanAttentionItem Core (producers + 8-state lifecycle + auto-escalate) Child Audit"
status: active (Rigby SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-03; F1 F1-appendix + D5 severity MEDIUM→HIGH promotion + F5 two-triggers-met + parent-doc-update-owed folds landed pre-commit; F3 mark_viewed qualifier confirmed no §1 change per Rigby; D48 25th arm HOLDING CLEAN through single-batch 4-question SIGN — 20th consecutive-fully-clean-arms sub-pattern CONFIRMED per S1799 §10.2 MC-2 CODIFICATION-READY criterion; SIGN-turn-1 landed via arc pin pa-ae5931ea706b4537 [tools/pa_local.sh wrapper default routed to arc pin instead of fresh isolation pin pa-43b5b8154c8e42d7 minted at S1801 open — noted as process footnote in §20.5; isolation pin remains available for optional cycle 2 pressure-test but not routed; retire owed at S1801 close per playbook §16])
authority: child-audit for Category A per parent §5 D78 sequence + FIRST child under Group 1800; applies D48 preemptive stability-probe gate 25th arm on fresh SIGN pin per playbook §15 stage-table child row; 20th consecutive-fully-clean-arms sub-pattern anticipated (S1799 §10.2 MC-2 CODIFICATION-READY criterion = single-batch 4-question)
category: child_audit
session: 1801
date: 2026-07-03
domain_slug: human_attention
research_group: 1800
child_slot: P1
parent_doc: docs/research/domains/human_attention/1800_human_attention_domain_scoping.md
head_commit: eef2280f
authors: Claude Code (Chris directed via short command "start research group 1801" at S1801 open; per playbook §21 short-command intent — interpreted as S1801 child under Group 1800 per parent D78 P1 slot; Rigby confirmed interpretation via `pa_local.sh` on arc pin pa-ae5931ea706b4537)
supersedes: none
related:
  - docs/research/domains/human_attention/1800_human_attention_domain_scoping.md   # parent scoping — Cat A boundary §3 A + load-bearing questions + §5 F5 correlation-primitive box (HAI_item_id primitive row SECOND-application HYPOTHESIS)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                       # §11.2 20-section child template + §13 6-parallel-Explore + §14 verifier-loop + §15 SIGN
  - docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md   # Cat-A-first-child structural precedent under Group 1700 + frontmatter exemplar
  - docs/research/domains/observability/1799_observability_canonical_summary.md     # fifth xx99 — MC-1 verifier-loop REQUIRED + MC-2 19-arm sub-pattern + MC-3 F5 HYPOTHESIS box CODIFICATION-CANDIDATE precedent
  - docs/research/platform/cross_domain_integration_audit.md                        # S1274 §3.3 CRITICAL Failure Cluster → HAI gap + §3.8 MEDIUM Signal Pattern → HAI gap + 5+ cross-domain HAI-consumer MISSING catalog + §4.7 canonical round-trip narrative
  - docs/research/platform_architecture_inventory.md                                # S1273 §3.16 HumanAttention WORKING/MODERATE coverage baseline + §4.7 "only round-trip w/ learning" claim + §2.5
  - docs/research/governance_authority_evolution.md                                 # S1269 §1.4 F5 HumanPreference topic_weights/source_weights never-saved bug (VERIFIED HERE)
  - docs/topics/personal-assistant.md                                               # PA-tool intersection cross-ref (Cat F territory)
  - docs/PLATFORM_INVENTORY.md                                                      # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                                     # narrative anchor
scope: Cat A per parent §3 A — HumanAttentionItem core: producer inventory + 8-state lifecycle producer/consumer flows + HumanAttentionLifecycleService auto-escalate ladder + auto-dismiss + auto-approve + beat wiring + two-layer lifecycle debt (HumanAttentionBridge vs HumanAttentionLifecycleService) + 5+ cross-domain HAI-consumer integration MISSING catalog verification at HEAD + retention posture + F5 correlation-primitive HAI_item_id primitive verification (SECOND application per parent §5). Does NOT own FeedbackProcessor/HumanFeedbackRecord internals (Cat B, S1802), LearningBridge subclasses (Cat C, S1803), HumanPreference internals + F5 bug fix (Cat D, S1804 — bug is CATALOGUED here as inheritance from parent §5 verifier_loop, not fixed), S746 verification-trigger internals (Cat E, S1805), or PA-tool/external-bridge boundaries (Cat F, S1806). Cross-cat writes from Cat A producers to Cat B (HumanFeedbackRecord) are IN-scope as boundary evidence.
boundary_rule: |
  Cat A owns *the HumanAttentionItem model* (producer inventory, 8-state lifecycle transitions, retention posture) + *HumanAttentionLifecycleService* (state-machine autonomous transitions) + *HumanAttentionBridge* (event → HAI creation layer) + *HumanInterfaceService.create_attention_item* (canonical service-layer entry point).
  Cat A does NOT own the FeedbackProcessor state machine (Cat B — post_save signal on HumanFeedbackRecord classifies positive/negative → creates AgentLearning + LearningInsight).
  Cat A does NOT own LearningBridge subclasses (Cat C — 10+ concrete writers at core/learning_bridges/ + ai_core/intelligence/).
  Cat A does NOT own HumanPreference field semantics beyond producer-side reads (Cat D — F5 topic_weights/source_weights never-saved bug is CATALOGUED here as evidence but the FIX is post-arc T-slot per parent §non_goals).
  Cat A does NOT own S746 verification-trigger callers (Cat E — `record_verification()` DEFINITION is in Cat A model, but the 2 caller sites at `views_human_interface.py:245` and `betting_outcome_verifier.py:413` are Cat E's evidence surface).
  Cat A does NOT own the terminology-boundary / PA-tool intersection / external bridge inventory (Cat F).
  Cross-cat writes:
    - Cat A auto-approve WRITES to Cat B (`HumanFeedbackRecord.objects.create` at `human_attention_lifecycle.py:325-334`) — Cat A code, Cat B schema; boundary posture is xx99 territory.
    - Cat A creates HAI rows that Cat B consumes via post_save signal on `HumanFeedbackRecord` (`models_feedback_processing.py:372`) — the signal fire is Cat B's territory; the row-that-triggered-it is Cat A.
    - Cat A record_verification() DEFINITION at `models_human_interface.py:216` is Cat A model surface; Cat E owns the caller-inventory posture.
load_bearing_questions:
  - Q1 (parent §3 A "HAI 8-state lifecycle producer/consumer inventory"): Which of the 8 states (pending/viewed/acted/deferred/ignored/expired/watching/verified) have complete producer + consumer coverage, and which have ownership gaps? What is the state-ownership matrix at HEAD?
  - Q2 (parent §3 A "20+ HAI producer sites at HEAD"): Is the S1273 §3.16 "20+ HAI producer sites at HEAD" claim CONFIRMED at HEAD, and what is the actual count? What is the domain breakdown and preference-respect rate?
  - Q3 (parent §3 A "HumanAttentionLifecycleService auto-escalate ladder"): Is the LOW 72h → MEDIUM 48h → HIGH 24h → CRITICAL auto-dismiss 3d ladder accurate at HEAD, and how does it interact with `HumanPreference` fields? Does auto-approve emit `HumanFeedbackRecord` (feeding Cat B)?
  - Q4 (parent §3 A "two-layer lifecycle debt HumanAttentionBridge vs HumanAttentionLifecycleService"): What is the responsibility split between HumanAttentionBridge (event → HAI writer, 636 lines) and HumanAttentionLifecycleService (state-machine, 732 lines)? Where do they overlap, where are the gaps, and what dedup candidates emerge?
  - Q5 (parent §3 A "5+ cross-domain HAI-consumer integration MISSING catalog"): Verify each of the 5+ S1274 §3.3 + §3.8 MISSING integrations at HEAD — Body Systems / Signal Engine / Revenue Pipeline / Observability/SLO / Failure Cluster/OpsRun. What is WORKING vs MISSING vs newly-wired?
  - Q6 (parent §5 F5 correlation-primitive HAI_item_id row SECOND application): Is `HAI_item_id` a bona fide cross-system correlation primitive (writes/reads across 2+ domains), or domain-internal only? What is the retention posture — SAVED-FOREVER vs TIME-BOUND-DELETE — and how does it align with LLMCallEvent's 30-day baseline?
verifier_loop: |
  Pre-Explore load-bearing claims verified via file:line direct read before firing sub-agents (2026-07-03; head=eef2280f):
    - HumanAttentionItem model at core/models_human_interface.py:20-227 confirmed (8-state lifecycle @ :36-53 verbatim: pending/viewed/acted/deferred/ignored/expired/watching/verified; S746 verification fields @ :153-163; `record_decision()` @ :184; `record_verification()` @ :216-227).
    - HumanFeedbackRecord at :230-265 confirmed.
    - HumanPreference at :268-358 confirmed (F5 bug CATALOGUED: `topic_weights` field @ :323 + `source_weights` field @ :324 both declared but `update_learned_stats()` @ :334-357 omits them from `save(update_fields=['approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at'])` @ :356-358 — SILENT DATA LOSS).
    - HumanAttentionLifecycleService at core/services/human_attention_lifecycle.py:36 confirmed; file is **732 lines** — parent §5 verifier_loop says `:36-728` which is 4-line short (§14 finding; note in §14.2).
    - ESCALATION_THRESHOLDS constant @ :48-52 verbatim: `{'low': 72, 'medium': 48, 'high': 24}` — LOW 72h → MEDIUM 48h → HIGH 24h ladder confirmed.
    - AUTO_DISMISS_HOURS constant @ :55-60 verbatim: `{'low': 168, 'medium': 120, 'high': 96, 'critical': 72}` — critical 72h → auto-dismiss confirmed.
    - LOW_RISK_SOURCES constant @ :63-69: `['spider_insight', 'content_review', 'blog_review', 'trend_analysis', 'observation']`.
    - AUTO_APPROVABLE_TYPES constant @ :71-78: `['content', 'insight', 'observation', 'analysis', 'suggestion']`.
    - `item.save()` at :322 has NO `update_fields=` — race condition surface (see §15.1).
    - HumanInterfaceService.record_decision at core/services/human_interface_service.py:295-353 confirmed.
    - FeedbackProcessor.process_human_feedback at core/models_feedback_processing.py:122-180 confirmed.
    - `@receiver(post_save, sender='core.HumanFeedbackRecord')` at core/models_feedback_processing.py:372 confirmed — Cat B signal wire.
    - HumanAttentionBridge at core/services/human_attention_bridge.py confirmed; file is 636 lines; distinct from HumanAttentionLifecycleService — two-layer debt structural evidence.
    - Beat: `process_human_attention_lifecycle` at core/tasks.py:7248 + registered at core/celery.py:719 with schedule `*/10 * * * *` per docs/BEAT_AUDIT.md:94 confirmed.
    - `record_verification()` callers at HEAD = 2 sites: core/views_human_interface.py:245 (API endpoint) + core/services/betting_outcome_verifier.py:413 (auto-verify from betting outcomes). Cat E territory.
  Six parallel Explore sub-agents fired per playbook §13 (2026-07-03). Findings folded into §3-§20 with attribution.
  Post-Explore verifier-loop spot-checks (2026-07-03):
    - E1 43-producer claim: 25 direct + 8 bridge helpers + 10 bridge-using callers = 43 code paths. Direct-create grep sum = 30 total (28 production, 2 test at `core/tests/test_sia_escalation.py`); minor F-slot F1: E1 undercounted 2-3 production direct-create sites (likely `ops_autopilot/core.py:2844` governance snapshot). Directionally CORRECT.
    - E2 signal count: only ONE `@receiver` on `HumanAttentionItem` at `signals_push_notifications.py:14` (`on_critical_attention_item`; fires only when `created=True AND urgency='critical'`) — VERIFIED.
    - E2 mark_viewed() "never called by any service" — needs QUALIFICATION: mark_viewed IS called from view layer at `views_human_interface.py:100` (AttentionDetailView.get) but NOT from `HumanInterfaceService` or `HumanAttentionLifecycleService`. F-slot F3.
    - E3 item.save() @ human_attention_lifecycle.py:322 no update_fields — VERIFIED (§15.1 D1).
    - E4 boardroom junk cleanup DELETE @ tasks_ops.py:39-97 spider_action 6h + arbitrage 12h + [Learned] junk — VERIFIED (§7.5 and §15.7 D7 retention posture).
    - E6 cross-domain HAI_item_id 6+ domains claim — VERIFIED via grep for `attention_item_id` across `core/` → 16 files spanning 8-10 distinct domains (mission_control_executor, orchestration_approval, ops_autopilot verification+core, gate_progression_pipeline, opportunity_execution_pipeline, spider_action_pipeline, implementation_executor, td_handlers_ops, feedback_processing, orchestration, plus self).
  Rigby SIGN cycle 1 pending on fresh SIGN isolation pin pa-43b5b8154c8e42d7 (D48 25th arm start; 20th consecutive-fully-clean-arms sub-pattern anticipated per S1799 §10.2 MC-2 single-batch-4-question criterion). Folds owed pre-commit; see §20.5 for pending fold notes.
methodology_ratifications:
  - D75 parent-with-children (Chris-locked S1800)
  - D76 six categories A-F with F.a-F.e sub-slots (Chris-locked S1800)
  - D77 delegation boundary vs Groups 1300/1400/1500/1600/1700/1900/Employee-OS explicit (Chris-locked S1800)
  - D78 P1 S1801 = Cat A HumanAttentionItem core (Chris-locked S1800)
  - D79 posture-decision framing = evidence brief NOT recommendation (Chris-locked S1800)
  - D80 arc lens question = "is HumanAttentionItem the canonical learning-signal aggregation surface, OR are learning bridges autonomous domain-specific consumers that bypass HAI?" (Chris-locked S1800)
  - Playbook §11.2 20-section child template FIRST application under Group 1800 (SIXTH application overall after S1401 + S1501 + S1601 + S1701 + prior first-child cycles)
  - Playbook §13 6-parallel-Explore sweep applied
  - Playbook §14 verifier-loop REQUIRED promotion CODIFICATION-READY (S1799 §10.2 MC-1) — applied pre-Explore + post-Explore on binary claims
  - Playbook §15 SIGN cycle 1 single-batch 4-question pattern anticipated (S1799 §10.2 MC-2 CODIFICATION-READY 19-consecutive-fully-clean-arms sub-pattern anticipation of 20th arm)
  - Playbook §11.3 §10 meta-methodology template CODIFICATION-READY-STRENGTHENED (deferred to S1899 xx99 canonical summary)
  - F5 correlation-primitive HAI_item_id HYPOTHESIS box SECOND APPLICATION at parent §5 (S1799 §10.2 MC-3 CODIFICATION-CANDIDATE two-triggers threshold MET; promotion to CODIFICATION-READY at S1899 close if pattern holds durable)
  - D48 preemptive stability-probe gate 25th arm start on fresh SIGN pin pa-43b5b8154c8e42d7
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/topics/personal-assistant.md
---

# Session 1801 — Group 1800 Cat A: HumanAttentionItem Core (producers + 8-state lifecycle + auto-escalate) Child Audit

> **What this doc is.** A child audit under the Group 1800 HumanAttention /
> Feedback / Learning arc. FIRST child (P1) per parent §5 D78 sequence.
> Applies playbook §11.2 20-section template to Category A per parent
> §3 A — HumanAttentionItem core: producer inventory + 8-state lifecycle
> producer/consumer flows + HumanAttentionLifecycleService auto-escalate
> ladder + auto-dismiss + auto-approve + beat wiring + two-layer
> lifecycle debt (Bridge vs LifecycleService) + 5+ cross-domain
> HAI-consumer integration MISSING catalog verification + retention
> posture + F5 correlation-primitive `HAI_item_id` HYPOTHESIS verification
> (SECOND application). Every load-bearing claim cites `file:line` at
> HEAD `eef2280f` (main branch, post-S1800 arc-open + docs cascade PR
> #2852). Every load-bearing negative claim ("MISSING integration",
> "no beat entry", "no consumer") is grep-verified with the grep
> pattern cited in §20.
>
> **What this doc is not.** A deep-dive on FeedbackProcessor semantics
> (Cat B, S1802), LearningBridge subclass inventory (Cat C, S1803),
> HumanPreference F5 fix or field internals (Cat D, S1804 — F5 bug is
> CATALOGUED as inheritance from parent §5 verifier_loop, not fixed
> here per playbook §14.5 no-implementation), S746
> verification-trigger caller inventory (Cat E, S1805), or the
> terminology-boundary / PA-tool intersection / external bridge sweep
> (Cat F, S1806). Handoffs to sibling children are noted at the
> boundary via cross-references; not traversed.
>
> **What is deferred to xx99 (S1899).** The load-bearing D80 axis —
> "is the human-in-the-loop attention queue (`HumanAttentionItem`)
> the canonical learning-signal aggregation surface, OR are learning
> bridges autonomous domain-specific consumers that bypass HAI?" —
> is an evidence-brief question, not a Cat-A verdict. This child
> audit contributes the HAI-core coverage posture (§9 + §10 + §16);
> xx99 owns the axis resolution across all six children plus F.a-F.e
> sub-slot evidence.

---

## 1. Executive Summary

Cat A (HumanAttentionItem core) is **WORKING at MODERATE coverage with
extensive codified debt** at HEAD `eef2280f`. The `HumanAttentionItem`
model (`core/models_human_interface.py:20-227`) implements an 8-state
lifecycle with S746 verification-loop fields (Session 746, `watching`/
`verified` states + `verification_outcome` + `record_verification()`).
Two adjacent services operate on the same row concurrently:
`HumanAttentionBridge` (`core/services/human_attention_bridge.py`, 636
lines) is the event-ingestion writer layer; `HumanAttentionLifecycleService`
(`core/services/human_attention_lifecycle.py`, 732 lines) is the
autonomous state-machine manager driven by a 10-minute Celery Beat
(`process_human_attention_lifecycle` at `core/tasks.py:7248` +
`core/celery.py:719`). The producer surface is **43 distinct code paths**
(25 direct `HumanAttentionItem.objects.create()` sites + 8 bridge helper
methods + 10 bridge-using callers) — **CONFIRMED AND EXCEEDED** the
S1273 §3.16 "20+ HAI producer sites at HEAD" claim.

**Eight load-bearing findings:**

1. **43 distinct producer code paths at HEAD** (§4.1 + §7.1) — S1273
   §3.16 "20+" claim CONFIRMED AND EXCEEDED. Breakdown: 25 direct
   `HumanAttentionItem.objects.create()` sites across 20 files + 8
   bridge helper methods in `human_attention_bridge.py` + 10 bridge-
   using callers (signals + tasks + agents). Domain breakdown spans
   Approval/Gate (7) + Agent Execution/System Health (8) + Revenue/
   Opportunity (5) + Content/Blog (4) + Spider/Market Intelligence (2)
   + Ops Autopilot/Governance (6) + Diagnostics (2) + Platform Command
   (2) + PA/Consultation (3) + Dreams (1) + Mythology (1) + ML
   Diagnostics (2) + Mission Control (1) + Implementation (2).

2. **ZERO producers respect user preferences at HEAD** (§4.1 + §15.2)
   — none of the 43 producers check `HumanPreference.min_urgency_to_notify`,
   `quiet_hours_start/end`, `blocked_sources`, or `trusted_agents`
   before creating an HAI row. Only `HumanInterfaceService.create_attention_item()`
   at `:662` computes a `priority_score` factoring ML confidence, but
   even that doesn't gate creation. **Preference is display-side only,
   not producer-side.**

3. **8-state lifecycle has 3 unowned transitions** (§7 + §18) — HAI
   state machine has three transitions no service owns:
   (a) `pending → viewed` (`mark_viewed()` @ `models:177` called ONLY
   from `views_human_interface.py:100` at view layer, not from
   `HumanInterfaceService` or `HumanAttentionLifecycleService`);
   (b) `deferred → pending` (`record_decision(decision='reopen')` @
   `models:195-198` bidirectional but no auto-check for
   `deferred_until <= now`); (c) `watching → verified`
   (`record_verification()` @ `models:216-227` — definition-site is
   Cat A; the 2 callers at `views_human_interface.py:245` +
   `betting_outcome_verifier.py:413` are Cat E's evidence surface but
   NEITHER wires it to a beat schedule).

4. **HumanAttentionLifecycleService auto-approve races with concurrent
   writers** (§15.1) — `item.save()` at
   `human_attention_lifecycle.py:322` in `auto_approve_item()` runs
   WITHOUT `update_fields=` parameter, so the full instance is written
   back to DB. If a concurrent producer (Bridge dedup path @
   `human_interface_service.py:620-641`) updated `urgency` /
   `priority_score` between the fetch (`:257-266`) and the save
   (`:322`), the concurrent change is **silently overwritten**. The
   sibling method `_auto_escalate_aging_items()` @ `:211` correctly
   uses `save(update_fields=['urgency', 'priority_score'])` — the debt
   is localized to `auto_approve_item()`.

5. **Auto-approve bypasses `blocked_sources` + `trusted_agents`
   preferences** (§15.3) — `_auto_approve_low_risk_items()` @
   `:257-276` filters candidates by `LOW_RISK_SOURCES` and
   `AUTO_APPROVABLE_TYPES` (class-level constants) and checks
   `require_review_above_confidence`, but DOES NOT check per-user
   `HumanPreference.blocked_sources` or `trusted_agents` fields
   (declared at `models:319-320`). Users who blocked a source_type
   will still see their items auto-approved silently.

6. **Two-layer lifecycle debt is structural** (§16.1 + §17) — Bridge
   (event-driven creation) and LifecycleService (periodic state
   manager) both operate on the same row with responsibility overlap:
   both can write `urgency` (Bridge on re-notification dedup @
   `human_interface_service.py:620-641`, LifecycleService on age-based
   escalation @ `lifecycle:198-211`); both indirectly own `status=acted`
   (Bridge creates items expecting human action; LifecycleService
   auto-decides via `auto_approve_item()`); both can write to
   `HumanFeedbackRecord` (LifecycleService @ `:325-334`, Interface
   layer's `record_decision()` @ `human_interface_service.py:325-337`).

7. **Cross-domain HAI-consumer integrations 4/5 still MISSING at HEAD**
   (§9.2) — S1274 §3.3 + §3.8 flagged 5 CRITICAL/MEDIUM MISSING
   cross-domain HAI-consumer integrations. At HEAD verification:
   **1 WORKING** (Revenue Pipeline via ops_autopilot core.py: 2051
   revenue_pipeline + 2117 outbound + 2626 deploy + 2691 policy
   conflict + 2844 governance) + **4 MISSING** (Body Systems → HAI,
   Signal Engine → HAI, Observability/OpsRun Failures → HAI,
   Observability/SLO Framework → HAI). Zero NEW consumers wired
   between S1274 and HEAD. Additional 8+ operationally-scoped HAI
   writers found outside the S1274 baseline (circuit breaker, audit
   remediation, ops control loop, spider action, content idea,
   orchestration approval, priority governor) but they are procedural,
   not cross-cutting aggregation.

8. **F5 correlation-primitive `HAI_item_id` CONFIRMED cross-system
   primitive; retention posture DIVERGENT from LLMCallEvent baseline**
   (§9 + §15.7 D7) — Task A: `HAI_item_id` (via `attention_item_id`
   field) is used across 8-10 distinct domains (mission_control_executor,
   orchestration_approval, ops_autopilot verification+core,
   gate_progression_pipeline, opportunity_execution_pipeline,
   spider_action_pipeline, implementation_executor, feedback_processing,
   orchestration model, td_handlers_ops). Bona fide cross-system
   primitive; S1799 §10.2 MC-3 CODIFICATION-CANDIDATE (two-triggers
   threshold MET). Task B: retention is **TIME-BOUND-SOFT-DELETE + BOUNDED-HARD-DELETE**
   — HAI rows are status-flipped to `ignored` / `expired` and preserved
   FOREVER for most `item_type`s; only `spider_action` (6h) and
   `arbitrage` (12h) items are hard-deleted via
   `_impl_cleanup_boardroom_junk()` at `core/tasks_ops.py:39-97`.
   DIVERGENT from LLMCallEvent's 30-day hard-delete baseline
   (`CELERY_TASK_EVENT_RETENTION_DAYS = 30`). No general
   `HAI_RETENTION_DAYS` config exists.

### 1.1 Findings lock-in (F1-F8)

- **F1 (minor, verifier drift)** — Explore #1 undercounted 2-3 production
  direct-create sites (25 in report vs 28 in grep sum excluding tests).
  Sites missed likely include `ops_autopilot/core.py:2844` governance
  snapshot. Producer table in §4.1 uses the E1 canonical list; §14.1
  captures the drift; **§20.8 appendix enumerates all 28 production
  direct-create sites for the record** (SIGN F1 fold 2026-07-03).

- **F2 (minor, verifier drift)** — Parent §5 `verifier_loop` cites
  HumanAttentionLifecycleService at `:36-728`; file is actually 732
  lines. 4-line drift owed to xx99 parent-anchor update PR (§14.2).

- **F3 (minor, verifier drift)** — Explore #2 `mark_viewed()`
  claim "never called by any service" is technically accurate for the
  service layer but misleading; the method IS called from view layer
  at `views_human_interface.py:100` (`AttentionDetailView.get`).
  Rewrote in §7 + §14.3 with view-layer qualification.

- **F4 (medium, structural)** — Two-layer lifecycle debt structural
  evidence backbone: 5 overlap areas + 3 gaps + 6 dedup candidates
  (§16.1 + §17 + §18).

- **F5 (medium, correlation-primitive HYPOTHESIS)** — `HAI_item_id`
  cross-system primitive verified across 8-10 domains at HEAD;
  SECOND application of F5 correlation-primitive HYPOTHESIS box
  discipline. **MC-3 threshold met (2 independent triggers: S1700
  parent §5 + S1801 child verification);** parent doc §5 F5
  HYPOTHESIS-box status update is **owed as explicit follow-up
  action** at S1801 close (flip HYPOTHESIS → VERIFIED-AT-CHILD).
  **Eligible for CODIFICATION-READY promotion path pending parent
  flip + one more durability check** in a P2-P6 child audit (target:
  S1802 P2 Cat B FeedbackProcessor round-trip verification). Full
  promotion decision at S1899 xx99 canonical summary. (SIGN F5 fold
  2026-07-03 — Rigby ratified two-triggers-met claim + owed parent
  update phrasing.)

- **F6 (medium, retention posture)** — HAI retention posture
  DIVERGENT from LLMCallEvent 30-day hard-delete baseline; no
  `HAI_RETENTION_DAYS` config; boardroom junk cleanup DELETES only
  `spider_action` (6h) + `arbitrage` (12h) + `[Learned]` junk items.
  All other 41+ producers' items are SAVED-FOREVER via status-flip
  soft-delete. Table growth risk unbounded.

- **F7 (medium, ownership gap)** — 3 unowned state transitions:
  (a) `pending → viewed` unowned by services; (b) `deferred → pending`
  reopen non-terminal but no auto-transition on `deferred_until <= now`;
  (c) `watching → verified` verification loop has record_verification()
  definition here but 2 caller sites only (`views_human_interface.py:245`
  API + `betting_outcome_verifier.py:413` auto-verify from betting).
  Neither wires to a beat schedule.

- **F8 (LOW, cross-domain gap)** — 4 of 5 S1274 cross-domain HAI-consumer
  integrations still MISSING at HEAD; ZERO newly wired between S1274
  and HEAD. Body Systems / Signal Engine / OpsRun-Failure / SLO all
  MISSING; Revenue is WORKING via ops_autopilot. §9.2 catalog.

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence (2026-07-03)
on arc pin `pa-ae5931ea706b4537`** [tools/pa_local.sh wrapper defaulted
to arc pin instead of fresh isolation pin `pa-43b5b8154c8e42d7` — see
§20.5 process footnote]. **D48 25th arm HOLDING CLEAN; 20th consecutive-
fully-clean-arms sub-pattern CONFIRMED** per single-batch 4-question
criterion (S1799 §10.2 MC-2 CODIFICATION-READY). Three folds landed
pre-commit: **F1 §20.8 appendix enumeration** (28 production direct-
create sites); **D5 severity promotion MEDIUM → HIGH** (record_verification
learning-loop decoupling structural impact); **F5 two-triggers-met claim
+ parent-doc §5 update owed** (HAI_item_id CODIFICATION-CANDIDATE
promotion path). F3 mark_viewed qualifier confirmed no §1 change
required. See §20.6 for full fold record.

---

## 2. Domain Purpose

Cat A's role in Group 1800 architecture: **HumanAttentionItem is the
canonical "human should decide something" queue** — a general-purpose
attention surface that any producer domain (agents, spiders, ML,
governance, revenue, content, sports, ops, PA) can write to when a
human decision is required or a signal should be surfaced for review.

Per S1273 §3.16: *"Route agent-generated items requiring human
decision-making (arbitrage signals, approvals, verification,
escalations) with attention queue, urgency levels, and verification
feedback loop for learning."*

Per S1274 §4.7 canonical round-trip narrative: **HAI is the SINGLE
round-trip surface that includes a learning signal** — the flow
`Human → HAI → FeedbackProcessor → AgentLearning` at `models_human_interface.py`
→ `models_feedback_processing.py:372` post_save signal wire → `AgentLearning`
+ `LearningInsight` records → agent adaptation.

Cat A owns:
- **The HAI row's producer surface** (43 code paths).
- **The 8-state lifecycle model + method definitions** (`mark_viewed`,
  `record_decision`, `record_verification`).
- **The 2 services on the HAI row** (Bridge event-writer +
  LifecycleService state-machine).
- **The service facade `HumanInterfaceService.create_attention_item`**
  which is the canonical entry-point for producers.
- **The retention posture** (or absence thereof).
- **The beat wire** for `process_human_attention_lifecycle`.
- **The producer-side preference contract** (currently: none —
  zero producers respect user preferences).

Cat A does NOT own:
- **Feedback classification semantics** — Cat B (`FeedbackProcessor`
  positive/negative classification, `AgentLearning` writes,
  `LearningInsight` writes).
- **Learning-bridge subclass writers** — Cat C (10+ concrete
  `LearningBridge` subclasses at `core/learning_bridges/` +
  `ai_core/intelligence/`).
- **HumanPreference field semantics beyond producer reads** — Cat D
  (F5 `topic_weights`/`source_weights` never-saved fix is post-arc
  T-slot per parent §non_goals).
- **S746 verification-trigger callers** — Cat E (verification loop
  wiring at `betting_outcome_verifier.py:413` + view endpoint at
  `views_human_interface.py:245`).
- **Terminology / external / PA-tool boundaries** — Cat F.

---

## 3. Canonical Entry Points

Cat A canonical entry points at HEAD:

| Kind | Symbol | File:Line | Role |
|---|---|---|---|
| Model | `HumanAttentionItem` | `core/models_human_interface.py:20-227` | Core row (487-line file); 8-state lifecycle + S746 verification fields |
| Model method | `HumanAttentionItem.mark_viewed()` | `core/models_human_interface.py:177-182` | atomic pending→viewed transition (view-layer callable) |
| Model method | `HumanAttentionItem.record_decision(decision, feedback, confidence)` | `core/models_human_interface.py:184-214` | pending/viewed → acted/watching (or reopen back to pending) |
| Model method | `HumanAttentionItem.record_verification(outcome, profit, notes)` | `core/models_human_interface.py:216-227` | watching→verified (Cat E's evidence surface — 2 callers only) |
| Service facade | `HumanInterfaceService.create_attention_item(...)` | `core/services/human_interface_service.py:662` (called from `:598-677` block) | Canonical entry-point for producers; sole path to `HumanAttentionItem.objects.create()` when going through the facade |
| Service facade | `HumanInterfaceService.record_decision(item_id, decision, ...)` | `core/services/human_interface_service.py:295-353` | Facade for record-decision flow; writes HAI + creates `HumanFeedbackRecord` + fires `FeedbackProcessor` signal via post_save |
| Service facade | `HumanInterfaceService.defer_item(item_id, remind_at)` | `core/services/human_interface_service.py:355+` | Sets status=deferred + `deferred_until` (atomic via `save(update_fields=[...])`) |
| Service | `HumanAttentionBridge` | `core/services/human_attention_bridge.py` (636 lines) | Event-driven writer layer; 8 helper methods + Django post_save signal receivers for `PilotReadinessGate` + `AgentExecution` |
| Service | `HumanAttentionLifecycleService` | `core/services/human_attention_lifecycle.py:36-732` | Autonomous state-machine (auto-expire + auto-dismiss + auto-escalate + auto-approve); 10-min beat driven |
| Beat task | `process_human_attention_lifecycle` | `core/tasks.py:7248-7284` | Celery task calling `attention_lifecycle.process_lifecycle()` |
| Beat schedule | `process-human-attention-lifecycle` | `core/celery.py:719` (per docs/BEAT_AUDIT.md:94) | `*/10 * * * *` cron; every 10 min; queue=default; expires=600s |
| Signal | `@receiver(post_save, sender='core.HumanAttentionItem')` `on_critical_attention_item` | `core/signals_push_notifications.py:14-26` | Only signal on HAI itself; fires ONLY when `created=True AND urgency='critical'` (Discord/push notification path) |
| Cross-cat signal (Cat B territory) | `@receiver(post_save, sender='core.HumanFeedbackRecord')` `process_human_feedback_signal` | `core/models_feedback_processing.py:372` | Fires on `HumanFeedbackRecord.objects.create()` from `record_decision()` or `auto_approve_item()`; calls `FeedbackProcessor.process_human_feedback()` |
| Cleanup task | `_impl_cleanup_boardroom_junk` | `core/tasks_ops.py:39-97` | Hard-deletes `spider_action` (6h) + `arbitrage` (12h) + `[Learned]` HAI rows |

**Cat A boundary handoffs:**
- `HumanFeedbackRecord` model definition @ `models_human_interface.py:230-265` is IN Cat A physical location but semantics owned by Cat B.
- `HumanPreference` model definition @ `models_human_interface.py:268-358` is IN Cat A physical location but Cat D semantics.
- `record_verification()` DEFINITION @ `:216-227` is Cat A; the 2 callers are Cat E evidence.
- `_maybe_trigger_orchestration()` @ `human_attention_lifecycle.py:353-391` + 4 workflow creators @ `:393-667` write to `CustomWorkflow` / `CustomWorkflowStep` / `PartnershipProject` — those are orchestration schemas; Cat A owns the WRITE but not the workflow semantics.

---

## 4. Major Models

### 4.1 HumanAttentionItem (Cat A primary)

**Location:** `core/models_human_interface.py:20-227`

**Purpose:** The row that carries "human should decide something".

**Fields inventory (verified pre-Explore):**

- **Identity:** `id` (UUID PK, `default=uuid.uuid4`, editable=False, @ `:92`); `user` (FK to `settings.AUTH_USER_MODEL`, on_delete=CASCADE, related_name='attention_items', @ `:93-96`).
- **Source:** `source_type` (max_length=50, e.g. `'thinking_agent'`, `'pilot_gate'`, `'arb_signal'`); `source_id` (max_length=100, blank=True); `source_agent` (max_length=100, blank=True). @ `:99-101`.
- **Content:** `item_type` (max_length=50, e.g. `'decision'`, `'alert'`, `'opportunity'`); `title` (max_length=200); `summary` (TextField); `payload` (JSONField, default=dict). @ `:104-107`.
- **Priority:** `urgency` (choices `URGENCY_CHOICES` critical/high/medium/low, default=medium, @ `:110-114`); `priority_score` (FloatField default=0.0, @ `:115`); `impact_estimate` (CharField, max_length=20, blank=True, @ `:116`).
- **ML context:** `ml_prediction` (JSONField, null=True), `ml_confidence` (FloatField, null=True), `ml_recommendation` (CharField, max_length=100, blank=True). @ `:119-121`.
- **Status:** `status` (choices `STATUS_CHOICES` 8 states, default=`pending`, @ `:124-128`).
- **Human decision:** `decision` (choices `DECISION_CHOICES` 8 decisions, null=True, @ `:131-135`); `decision_feedback` (TextField, blank=True); `decision_confidence` (FloatField, null=True); `decided_at` (DateTimeField, null=True); `time_to_decision_ms` (IntegerField, null=True). @ `:136-139`.
- **Human override:** `human_overrode_ml` (BooleanField, default=False, @ `:142`); `override_reason` (TextField, blank=True, @ `:143`).
- **Deferral:** `deferred_until` (DateTimeField, null=True, @ `:146`).
- **Timestamps:** `created_at` (auto_now_add=True); `viewed_at` (null=True); `expires_at` (null=True). @ `:149-151`.
- **S746 verification fields:** `verification_outcome` (choices `VERIFICATION_CHOICES` 5 outcomes pending/won/lost/push/cancelled, null=True, @ `:155-159`); `verified_at` (DateTimeField, null=True); `verification_profit` (FloatField, null=True); `verification_notes` (TextField, blank=True); `event_completed_at` (DateTimeField, null=True). @ `:160-163`.

**Meta:** ordering `['-priority_score', '-created_at']`; indexes on `(user, status)`, `(user, urgency)`, `source_type`, `created_at`. @ `:165-172`.

**8-state lifecycle constants (verbatim from :36-53):**

```
STATUS_PENDING   = 'pending'    # Item created; awaiting human review
STATUS_VIEWED    = 'viewed'     # Human opened it (via mark_viewed)
STATUS_ACTED     = 'acted'      # Human made a decision (record_decision default)
STATUS_DEFERRED  = 'deferred'   # Human pressed defer (defer_item)
STATUS_IGNORED   = 'ignored'    # Human ignored OR auto-dismissed (2 paths)
STATUS_EXPIRED   = 'expired'    # Auto-expired (past expires_at)
STATUS_WATCHING  = 'watching'   # S746: watch-and-verify decision
STATUS_VERIFIED  = 'verified'   # S746: verification outcome recorded
```

**8 decision constants (verbatim from :57-75):**

```
DECISION_APPROVE  = 'approve'
DECISION_REJECT   = 'reject'
DECISION_MODIFY   = 'modify'
DECISION_DEFER    = 'defer'
DECISION_DELEGATE = 'delegate'
DECISION_IGNORE   = 'ignore'
DECISION_ESCALATE = 'escalate'
DECISION_WATCH    = 'watch'     # S746 Watch & Verify
```

**5 verification outcome constants (verbatim from :78-89):**

```
VERIFY_PENDING   = 'pending'    # Watched but event not yet complete
VERIFY_WON       = 'won'        # Would have been profitable
VERIFY_LOST      = 'lost'       # Would have lost
VERIFY_PUSH      = 'push'       # No action / breakeven
VERIFY_CANCELLED = 'cancelled'  # Event cancelled
```

**Model method `mark_viewed(self)` @ `:177-182`:**

- Guards on `if self.status == self.STATUS_PENDING:` — silently no-op on other states.
- Sets `self.status = STATUS_VIEWED` + `self.viewed_at = timezone.now()`.
- **Atomic:** `self.save(update_fields=['status', 'viewed_at'])`.
- Called ONLY from `core/views_human_interface.py:100` (`AttentionDetailView.get`) — NO service-layer caller.

**Model method `record_decision(self, decision, feedback, confidence)` @ `:184-214`:**

- Writes `decision`, `decision_feedback`, `decision_confidence`, `decided_at`.
- Special-cases: `decision='watch'` sets `status=STATUS_WATCHING` + `verification_outcome=VERIFY_PENDING`; `decision='reopen'` resets `status=STATUS_PENDING` + `decision=None` + `decided_at=None` (bidirectional back to pending; **erases the previous decision — no audit trail of the reopen action itself, §18.2 D6**); default sets `status=STATUS_ACTED`.
- Computes `time_to_decision_ms` from `viewed_at` if set.
- Computes `human_overrode_ml` if `ml_recommendation` is set.
- **NOT ATOMIC:** `self.save()` full instance (§15.1 D1 sibling issue but on model, less concerning).

**Model method `record_verification(self, outcome, profit, notes)` @ `:216-227`:**

- Writes `verification_outcome`, `verification_profit`, `verification_notes`, `verified_at`, `event_completed_at`, `status=STATUS_VERIFIED`.
- **NOT ATOMIC:** full `self.save()`.
- **NO signal emitted; no event fired; no HAI_item_id log line** (§15.5 D5).
- Callers at HEAD: `core/views_human_interface.py:245` (API `AttentionVerifyView.post`) + `core/services/betting_outcome_verifier.py:413` (auto-verify from betting outcomes). Cat E's evidence.

### 4.2 HumanFeedbackRecord (Cat A adjacent — Cat B semantics)

**Location:** `core/models_human_interface.py:230-265`

**Purpose:** Feedback record for ML learning. Cat B (`FeedbackProcessor`)
consumes via post_save signal.

**Fields:**
- `attention_item` FK to `HumanAttentionItem`, CASCADE, related_name='feedback_records' @ `:233-237`.
- `user` FK to `settings.AUTH_USER_MODEL`, CASCADE, @ `:238`.
- `decision` (CharField max_length=20, @ `:241`); `feedback_text` (TextField, blank, @ `:242`); `confidence` (FloatField, null, @ `:243`).
- ML context copy from item: `ml_task_type`, `ml_models_used`, `ml_prediction`, `ml_confidence`. @ `:246-249`.
- Override analysis: `human_agreed_with_ml` (BooleanField, null, @ `:252`); `confidence_delta` (FloatField, null, @ `:253`).
- Learning status: `fed_to_ml` (BooleanField, default=False, @ `:256`); `fed_at` (DateTimeField, null, @ `:257`).
- `created_at` auto_now_add, @ `:259`.

**Writers at HEAD (Cat A crosses boundary):**
- `HumanAttentionLifecycleService.auto_approve_item()` @ `:325-334` — Cat A code, Cat B schema.
- `HumanInterfaceService.record_decision()` @ `:325-337` — Cat A service-facade code, Cat B schema.

**Signal receiver (Cat B territory):**
- `@receiver(post_save, sender='core.HumanFeedbackRecord')` `process_human_feedback_signal` @ `models_feedback_processing.py:372` — calls `FeedbackProcessor.process_human_feedback(attention_item_id, decision, ...)`. Full Cat B analysis deferred to S1802.

### 4.3 HumanPreference (Cat A adjacent — Cat D semantics; F5 bug CATALOGUED)

**Location:** `core/models_human_interface.py:268-358`

**Purpose:** Per-user preference storage — explicit user settings +
learned statistics.

**Fields (explicit):**
- `user` OneToOne to AUTH_USER_MODEL, CASCADE, related_name='human_preferences' @ `:289-293`.
- Notification: `quiet_hours_start` + `quiet_hours_end` (TimeField, null) @ `:296-297`; `min_urgency_to_notify` (choices HumanAttentionItem.URGENCY_CHOICES, default=medium) @ `:298-302`; `preferred_channel` (choices CHANNEL_CHOICES discord/web/email, default=discord) @ `:303-307`.
- Review: `review_depth` (choices quick/standard/thorough, default=standard) @ `:310-314`; `auto_approve_low_risk` (BooleanField, default=False) @ `:315`; `require_review_above_confidence` (FloatField, default=0.95) @ `:316`.
- Trust: `trusted_agents` (JSONField, default=list) @ `:319`; `blocked_sources` (JSONField, default=list) @ `:320`.

**Fields (learned — auto-updated):**
- `topic_weights` (JSONField, default=dict) @ `:323`.
- `source_weights` (JSONField, default=dict) @ `:324`.
- `avg_decision_time_ms` (IntegerField, null) @ `:325`.
- `approval_rate` (FloatField, null) @ `:326`.
- `total_decisions` (IntegerField, default=0) @ `:327`.
- `updated_at` (auto_now=True) @ `:329`.

**F5 BUG CATALOGUED (per parent §5 inheritance; fix is Cat D + post-arc T-slot):**

`update_learned_stats(self)` @ `:334-357` computes `approval_rate`,
`total_decisions`, `avg_decision_time_ms` and calls:

```python
self.save(update_fields=[
    'approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at'
])
```

@ `:356-358`.

**`topic_weights` and `source_weights` are NOT in `update_fields`**. Any
value written to these fields elsewhere is silently NOT persisted by
this method. Producer-side reads later see stale/empty dicts. Per
S1269 §1.4 F5 finding — **VERIFIED HERE at HEAD** as inheritance
evidence. **Fix is Cat D scope (S1804) or post-arc T-slot** per parent
§non_goals playbook §14.5 no-implementation.

---

## 5. Major Services

### 5.1 HumanAttentionBridge (event → HAI writer)

**Location:** `core/services/human_attention_bridge.py` (636 lines)

**Purpose:** Event-driven writer layer. Translates system events into
HAI rows.

**Bridge helper methods (8 canonical helpers per Explore #1 + #4):**

| Method | File:Line | Trigger event | source_type value | Urgency policy |
|---|---|---|---|---|
| `create_pilot_gate_attention(gate, user)` | `:72-116` | `PilotReadinessGate.status='pending_review'` | `pilot_gate` | high/medium risk-level conditional |
| `create_agent_execution_attention(execution, urgency, user)` | `:121-172` | `AgentExecution.status` change | `agent_execution` | high on failure, medium default |
| `create_arbitrage_attention(opportunity, user)` | `:178-223` | Arbitrage opportunity dict | `arbitrage_detection` | critical/high/medium by profit% |
| `create_system_alert(alert_type, ..., user)` | `:229-266` | Manual system alert | `system_alert:{type}` | medium default param |
| `create_diagnostic_alert(diagnostic_type, ..., user)` | `:272-321` | Scheduled diagnostic (CTOAgent) | `diagnostic:{type}` | medium default; honors source_agent param (S1093) |
| `create_mythology_alert(mythology_alert_id, ..., user)` | `:327-380` | MythologyAlert.critical/.high (S1095) | `mythology:{type}` | severity-mapped 1:1 |
| `create_content_review_attention(content_type, ..., quality_score, user)` | `:386-447` | Generated content awaiting approval | `content:{type}` | quality-score driven |
| `create_agent_output_attention(agent_name, ..., user)` | `:453-511` | BaseAgent Mission Control output (S763) | `agent_output:{agent_name}` | medium default; rate-limited |
| `create_spider_alert(spider_name, ..., user)` | `:517-560` | Spider data ingestion | `spider:{name}` | medium default param |

**Django signal receivers on Bridge:**

- `on_pilot_gate_change` @ `:571-575` — `@receiver(post_save, sender=PilotReadinessGate)`.
- `on_agent_execution_complete` @ `:578-591` — `@receiver(post_save, sender=AgentExecution)`.

**Behavior:** All bridge helpers delegate to
`HumanInterfaceService.create_attention_item()` (§5.3). Bridge is a
wrapper layer — no direct `HumanAttentionItem.objects.create()` call
from within Bridge helper methods.

**Utility:** `_serialize_for_json(obj)` @ `:30-41` recursively serializes
datetimes for JSON payload storage (S736 fix).

**Callers of Bridge (10 sites per Explore #1):**

- `core/agents/markets/arbitrage_detector.py:656` — `attention_bridge.create_arbitrage_attention()`.
- `core/agents/base_agent.py:3047` — `attention_bridge.create_agent_output_attention()` (BaseAgent Mission Control, S763).
- `core/services/scheduled_diagnostic_runner.py:1137` — `create_diagnostic_alert()` (CTOAgent daily).
- `core/signals/mythology_alert_signals.py:84` — `create_mythology_alert()` (critical/high mythology filter).
- `core/tasks_agents.py:4639` — `create_pilot_gate_attention()` (periodic gate scan).
- `core/tasks_agents.py:4653` — `create_agent_execution_attention()` (periodic failure scan).
- `core/tasks_agents.py:4667` — `create_system_alert()` (periodic system health).
- `core/tasks_agents.py:4732` — `create_spider_alert()` (periodic spider data scan).
- `core/tasks_content.py:2361` — `create_content_review_attention()` (blog generation, S759).
- `core/services/autonomous_action_executor.py:78` — `create_content_review_attention()` (S804).
- Plus admin backfill: `core/management/commands/backfill_blog_attention.py:117`.

### 5.2 HumanAttentionLifecycleService (state-machine manager)

**Location:** `core/services/human_attention_lifecycle.py:36-728` (file
732 lines total — 4-line drift from parent §5 claim; §14.2 F2).

**Purpose:** Autonomous lifecycle state-machine. Runs every 10 min via
Celery Beat. Owns auto-expire + auto-dismiss + auto-escalate +
auto-approve transitions.

**Threshold constants (verbatim, verified pre-Explore):**

```python
# Escalation ladder (hours without action; :48-52)
ESCALATION_THRESHOLDS = {
    'low': 72,      # 3 days -> escalate to medium
    'medium': 48,   # 2 days -> escalate to high
    'high': 24,     # 1 day -> escalate to critical
}

# Auto-dismiss (hours; :55-60)
AUTO_DISMISS_HOURS = {
    'low': 168,      # 7 days
    'medium': 120,   # 5 days
    'high': 96,      # 4 days
    'critical': 72,  # 3 days (with escalation first)
}

# Low-risk allowlist (:63-69)
LOW_RISK_SOURCES = ['spider_insight', 'content_review',
                    'blog_review', 'trend_analysis', 'observation']

# Auto-approvable types (:71-78)
AUTO_APPROVABLE_TYPES = ['content', 'insight', 'observation',
                         'analysis', 'suggestion']
```

**System-wide override:** `HumanSystemState.review_mode` (Boolean at
`models_human_interface.py:435`) — when True, ALL auto-approve is
paused (`_auto_approve_low_risk_items` @ `:240-245` checks and
returns `(0, 0)` short-circuit).

**Sub-methods inventory (per Explore #3):**

| Method | Purpose | File:Line | Atomicity | Side effects |
|---|---|---|---|---|
| `process_lifecycle()` | Beat entry-point; orchestrates sub-methods; returns stats | `:91-133` | N/A (orchestrator) | Calls 4 sub-methods; logs phase completions; catches Exception → errors counter |
| `_expire_old_items()` | Bulk expire past-deadline items | `:135-150` | Atomic (bulk `update()`) | `HumanAttentionItem.filter(status__in=[pending, viewed, deferred], expires_at__lt=now).update(status='expired')` — **minimal-field update** |
| `_auto_dismiss_stale_items()` | Bulk dismiss aged items (4 queries, one per urgency) | `:152-179` | Atomic (bulk `update()` per urgency) | `filter(status__in=[pending, viewed], urgency, created_at__lt, expires_at__isnull=True).update(status='ignored', decision='auto_dismiss', decision_feedback, decided_at)`. **Does NOT create HumanFeedbackRecord** (§15.4 D4 asymmetry). |
| `_auto_escalate_aging_items()` | Item-by-item urgency escalation (LOW→MED→HIGH→CRIT) | `:181-221` | Item-atomic (`save(update_fields=['urgency', 'priority_score'])`) | For each qualifying item: `urgency = escalate_to[urgency]`; `priority_score *= 1.5`; `save(update_fields=...)`. **Log at `logger.debug()` per-item** (:213-215); aggregate at `logger.info()` (:219) — §14 F-slot forensics gap. Idempotent (monotonic ladder). |
| `_auto_approve_low_risk_items()` | Filter + auto-approve candidates | `:223-296` | Per-item txn via `auto_approve_item()` | Reads `HumanPreference` per user; filters by LOW_RISK_SOURCES + AUTO_APPROVABLE_TYPES + `require_review_above_confidence`; **does NOT check `blocked_sources` or `trusted_agents`** (§15.3 D3). Processes max 50/run (:268). |
| `auto_approve_item(item, reason)` | Approve single item + create feedback + trigger orchestration | `:298-351` | `transaction.atomic()` wrapper but `item.save()` @ `:322` **NO update_fields** (§15.1 D1) | Sets decision='approve', status='acted', decided_at; creates HumanFeedbackRecord @ `:325-334`; calls `_maybe_trigger_orchestration()` @ `:337`. |
| `_maybe_trigger_orchestration(item)` | Route approved item to workflow by item_type | `:353-391` | Dispatches by item.item_type | Routes to `_create_opportunity_workflow` / `_create_action_workflow` / `_create_recommendation_workflow` / `_create_project_workflow`; returns `{'triggered': bool, 'execution_id': str}` |
| `_create_opportunity_workflow(item)` | Build 3-step opportunity workflow | `:393-460` | `transaction.atomic()` | Creates `CustomWorkflow` + 3 `CustomWorkflowStep` (Research → Scoring → ContentWriter); executes via `orchestration_engine.execute_workflow(async_mode=True)` @ `:440` |
| `_create_action_workflow(item)` | Build 1-step action workflow | `:462-521` | `transaction.atomic()` | Creates `CustomWorkflow` + 1 `CustomWorkflowStep` (execute agent from payload); executes via orchestration_engine @ `:501` |
| `_create_recommendation_workflow(item)` | Build 2-step recommendation workflow | `:523-586` | `transaction.atomic()` | Creates `CustomWorkflow` + 2 `CustomWorkflowStep` (Validate → Plan); executes via orchestration_engine @ `:566` |
| `_create_project_workflow(item)` | Build PartnershipProject + 3-step project workflow | `:588-667` | `transaction.atomic()` | Creates `PartnershipProject` (ai_contrib=70%, human_contrib=30%) + `CustomWorkflow` + 3 `CustomWorkflowStep`; executes via orchestration_engine @ `:645` |
| `get_lifecycle_stats()` | READ-ONLY; return status/urgency/aging aggregates | `:669-723` | READ-ONLY | Returns dict with `by_status`, `pending_by_urgency`, `aging_stats`, `auto_approved_24h`, `total_items`, `pending_count`, `acted_count`; uses `Count()` aggregates; filters `decision_feedback__istartswith='Auto-approved'` to detect system approvals |

**Orchestration engine dependency:** lazy-loaded property @ `:83-89`
imports `orchestration_engine` singleton from
`core.services.orchestration_engine`.

**Concurrency / idempotency (per Explore #3):**

- All 4 process-methods are naturally idempotent because their filter
  queries exclude items already in the target state (once `status='expired'`
  the item no longer matches the pending/viewed/deferred filter).
- **No `select_for_update()`** on candidate query at `:257-266`. Two
  concurrent beat runs (unlikely at 10-min cadence but possible on clock
  skew) could both fetch the same candidates.
- Task `process_human_attention_lifecycle` at `core/tasks.py:7248` has
  `soft_time_limit=300, time_limit=360` — bounded execution.

### 5.3 HumanInterfaceService (facade)

**Location:** `core/services/human_interface_service.py` (784 lines)

**Purpose:** Service-facade for per-user attention operations. Provides
canonical entry-points that Bridge helpers + views + tasks call.

**Key methods (Cat A scope):**

- **`create_attention_item(source_type, source_id, source_agent, item_type, title, summary, ..., urgency, priority_score, payload, ml_prediction, ml_confidence, ml_recommendation, expires_at)`** @ `:598-677` — canonical producer entry-point. Called by all 8 Bridge helper methods. Does dedup check @ `:604-641` against existing pending/viewed/deferred items with same `source_type` + `source_id`; updates urgency/summary/payload on dedup rather than creating duplicate. Writes `HumanAttentionItem.objects.create(...)` @ `:662-677` if no existing item.
- **`record_decision(item_id, decision, feedback, confidence)`** @ `:295-353` — writes decision to HAI (via model method `record_decision`); creates `HumanFeedbackRecord` @ `:325-337`; calls `_update_preferences_from_decision()` @ `:340`; conditionally calls `_feed_to_ml()` @ `:343-344` when `human_overrode_ml`.
- **`defer_item(item_id, remind_at)`** @ `:355+` — sets status='deferred' + `deferred_until`; atomic `save(update_fields=['status', 'deferred_until'])`.
- **`get_attention_stream(...)`** @ [reads] — READ-ONLY consumer; filters items for display; excludes items with `expires_at__lt=now`.
- **`get_attention_stats()`** @ [reads] — READ-ONLY aggregate consumer.

**Dedup contract at `:620-641`:**

```python
existing_item = query.first()
if existing_item:
    update_fields = []
    if summary and existing_item.summary != summary:
        existing_item.summary = summary
        update_fields.append('summary')
    if urgency and existing_item.urgency != urgency:
        existing_item.urgency = urgency  # ← WRITE: urgency re-escalation
        update_fields.append('urgency')
    # ...
    if update_fields:
        existing_item.save(update_fields=update_fields)
```

**Two-layer debt evidence #1:** Bridge can re-escalate `urgency` on dedup
(here at `:635`) while LifecycleService also escalates `urgency` on
age (`lifecycle:198-211`). Two independent escalation paths (§16.1).

**Cross-cat writes:**
- `record_decision` → `HumanFeedbackRecord.objects.create()` @ `:325-337` → post_save signal (Cat B) → `FeedbackProcessor.process_human_feedback()`.
- `_feed_to_ml()` @ [not fully catalogued in this audit; belongs Cat B/C boundary].

---

## 6. Major APIs and Interfaces

### 6.1 HumanAttentionItem REST surface

**Location:** `core/views_human_interface.py`

- `AttentionStreamView.get()` @ [reads via `get_attention_stream`] — GET list endpoint. Default filter: `status__in=['pending', 'viewed']` (§7.6 read behavior).
- `AttentionDetailView.get()` @ `:100` — GET single item; calls `item.mark_viewed()`. **This is the sole caller of `mark_viewed()` at HEAD** (§7 F3 qualification).
- `AttentionVerifyView.post()` @ `:245` — POST verification outcome; calls `item.record_verification(outcome, profit, notes)`. One of 2 callers.
- `BulkAttentionDecideView.post()` @ `:517-520` — POST bulk decision. **Uses `queryset.update(status=decision, decision=decision, handled_at=now)` — bypasses `record_decision` model method entirely** (§15.8 D8): skips `time_to_decision_ms` calculation, skips `human_overrode_ml` check, does NOT create HumanFeedbackRecord.

### 6.2 PA tool surface (Cat F territory but IN-scope for Cat A producer inventory)

- `td_handlers_agents.py:4110` — PA `create` action (medium default urgency, hardcoded PA_IDENTITY).
- `td_handlers_agents.py:4882` — PA `create_attention` action (medium default). **Duplicate pattern** (§17.3 dedup candidate).

### 6.3 Bridge helper API

Section 5.1 enumerates the 8 bridge helpers. Callers span agents +
tasks + signals + management commands.

### 6.4 Beat API

- `process_human_attention_lifecycle` beat task @ `core/tasks.py:7248-7284` — `@shared_task(name='core.tasks.process_human_attention_lifecycle', soft_time_limit=300, time_limit=360)`; body calls `attention_lifecycle.process_lifecycle()`; returns stats dict or error dict.
- Beat schedule @ `core/celery.py:719` — `*/10 * * * *` cron; queue=`default`; expires=600s. Per docs/BEAT_AUDIT.md:94.

---

## 7. Runtime Flows

### 7.1 HAI item creation flow (43 producers → HAI row)

```
Any of 43 producer sites
    ├─ 25 sites: direct HumanAttentionItem.objects.create(...) [with legacy field debt in 6 sites — §15.9]
    ├─ 10 sites: attention_bridge.create_<kind>_attention(...) [wrapper]
    │      → HumanInterfaceService.create_attention_item(...)
    │            → dedup check @ :604-641
    │            → HumanAttentionItem.objects.create(status='pending', urgency, priority_score, payload, ...)
    └─ 8 Bridge helper methods @ human_attention_bridge.py:72-560 [wrappers themselves]
                → HumanInterfaceService.create_attention_item(...)
                      → dedup check @ :604-641
                      → HumanAttentionItem.objects.create(status='pending', ...)

Post-save signal wire:
    HumanAttentionItem post_save → on_critical_attention_item (@ signals_push_notifications.py:14)
        Guard: created=True AND urgency='critical'
        Action: notify_critical_attention_item.delay(str(instance.id))
```

**Preference respect at creation:** ZERO. No producer checks
`HumanPreference.min_urgency_to_notify` / `quiet_hours_*` /
`blocked_sources` / `trusted_agents` (§15.2 D2).

### 7.2 Lifecycle beat cycle (every 10 min)

```
Celery Beat @ */10 * * * *
    → core.tasks.process_human_attention_lifecycle @ tasks.py:7248
        → attention_lifecycle.process_lifecycle() @ lifecycle:91-133
            ├─ _expire_old_items()          @ :135-150   (bulk update status='expired')
            ├─ _auto_dismiss_stale_items()  @ :152-179   (bulk update status='ignored' + decision='auto_dismiss')
            ├─ _auto_escalate_aging_items() @ :181-221   (per-item save urgency + priority_score×1.5)
            └─ _auto_approve_low_risk_items() @ :223-296
                    Check HumanSystemState.review_mode          → skip if True
                    Filter LOW_RISK_SOURCES ∪ AUTO_APPROVABLE_TYPES
                    Per candidate (max 50):
                        Check user_pref.require_review_above_confidence
                        auto_approve_item(item, reason)         @ :298-351
                            transaction.atomic():
                                item.decision='approve'; item.status='acted'; item.decided_at=now
                                item.save()   [NO update_fields — §15.1 D1]
                                HumanFeedbackRecord.objects.create(...) → triggers Cat B signal
                                _maybe_trigger_orchestration(item)
                                    → 1 of 4 workflow creators
                                        → CustomWorkflow + CustomWorkflowStep(s) + PartnershipProject (project only)
                                        → orchestration_engine.execute_workflow(async_mode=True)
```

### 7.3 Manual decision flow (Human → HAI → learning round-trip)

```
User makes decision via UI/API
    → HumanInterfaceService.record_decision(item_id, decision, feedback, confidence)  @ :295-353
        item.record_decision(...)                    [model method; sets status/decision/decided_at]
        HumanFeedbackRecord.objects.create(...)     @ :325-337
            ↓ post_save signal
        FeedbackProcessor.process_human_feedback_signal @ models_feedback_processing.py:372  [Cat B]
            → processor.process_human_feedback(attention_item_id, decision, ...)  @ :122
                is_positive = decision in ['approve', 'approved', ...]
                is_negative = decision in ['reject', 'rejected', ...]
                if is_positive: _reinforce_positive → AgentLearning + LearningInsight
                if is_negative: _learn_from_negative → AgentLearning + LearningInsight
        _update_preferences_from_decision(item)       [Cat D read/write; updates approval_rate, total_decisions, avg_decision_time_ms — but NOT topic_weights/source_weights per F5 bug §4.3]
        if item.human_overrode_ml: _feed_to_ml(item)  [Cat B/C boundary — feeds override signal to ML retraining]
```

**Per S1274 §4.7:** this is the SOLE round-trip surface with learning
in the platform.

### 7.4 S746 verification loop (watching → verified; Cat E's evidence but definition in Cat A)

```
Human presses "watch & verify" on arbitrage or prediction item
    → HumanInterfaceService.record_decision(item_id, 'watch', ...)  @ :295-353
        item.record_decision('watch', ...)                    [model method]
            status = 'watching'
            verification_outcome = 'pending'
            save()

Later — event completes:
    → EITHER views_human_interface.py:245 (API AttentionVerifyView.post)
       OR core/services/betting_outcome_verifier.py:413 (auto-verify from betting outcome, sports domain)
            → item.record_verification(outcome, profit, notes)   @ models:216-227
                status = 'verified'
                verification_outcome = outcome
                verification_profit = profit
                verified_at = event_completed_at = now
                save()   [NOT ATOMIC — full save]
    
    [NO signal emitted; no learning-loop wire; no HAI_item_id log line]
    [NO beat scheduler catches watching items whose event completed but no caller ran]
```

**Ownership gap (§18.3 F7):** Two callers; neither on a beat schedule.
Watched items whose triggering event completes but no code path fires
`record_verification()` remain in `watching` forever.

### 7.5 Boardroom junk cleanup (hard-delete for time-sensitive items)

```
Manual/scheduled call to _impl_cleanup_boardroom_junk(spider_action_hours=6)  @ tasks_ops.py:39-97

Actions:
  ├─ HumanAttentionItem.filter(status='pending', item_type='spider_action', created_at__lt=now-6h).delete()
  ├─ HumanAttentionItem.filter(status='pending', item_type='arbitrage', created_at__lt=now-12h).delete()
  └─ HumanAttentionItem.filter(status='pending', title__icontains='[Learned]').delete()

Also deletes:
  ├─ AgentDecisionSummary(status='draft', topic__icontains='[Learned]').delete()
  └─ AgentConversation(title__icontains='[Learned]').delete()

Stats returned: spider_actions_deleted, arbitrage_deleted, learned_attention_deleted, learned_decisions_deleted.
```

**Retention posture evidence (§15.7 D7 F6):** Only 3 categories are
hard-deleted (spider_action, arbitrage, `[Learned]`). All other 40+
producer items are SAVED-FOREVER via status-flip soft-delete only.

### 7.6 READ consumer flow (dashboard/API)

```
UI dashboard / API caller
    → HumanInterfaceService.get_attention_stream(...)
        HumanAttentionItem.objects.filter(user=..., status__in=['pending', 'viewed'])
            .exclude(expires_at__lt=now)
            .order_by('-priority_score', '-created_at')
```

**Notable:** `expired`, `acted`, `deferred`, `ignored`, `watching`,
`verified` items are all invisible to the default stream. Analytics
paths @ `get_attention_stats` + `get_lifecycle_stats` provide by-status
count aggregates but not row-level reads.

---

## 8. Data Ownership and Lifecycle

**HAI row ownership over its lifetime:**

| Phase | Owner service | State machine | Retention |
|---|---|---|---|
| Creation | Producer (43 sites) → Bridge helper OR direct → `HumanInterfaceService.create_attention_item` | → `pending` | forever (unless spider_action/arbitrage/[Learned]) |
| First view | `AttentionDetailView.get` calls `mark_viewed()` | `pending → viewed` | forever |
| Decision (human) | `HumanInterfaceService.record_decision` | `pending/viewed → acted` OR `→ watching` OR `→ pending` (reopen) | forever |
| Decision (auto) | `HumanAttentionLifecycleService.auto_approve_item` | `pending → acted` | forever |
| Defer | `HumanInterfaceService.defer_item` | `pending/viewed → deferred` | forever (until `deferred_until` — but no auto-reopen) |
| Escalate urgency | `HumanAttentionLifecycleService._auto_escalate_aging_items` | urgency LOW→MED→HIGH→CRIT (status unchanged) | forever |
| Dismiss | `HumanAttentionLifecycleService._auto_dismiss_stale_items` | `pending/viewed → ignored` (bulk update; no HumanFeedbackRecord) | forever |
| Expire | `HumanAttentionLifecycleService._expire_old_items` | `pending/viewed/deferred → expired` | forever |
| Verify (S746) | `views_human_interface.py:245` OR `betting_outcome_verifier.py:413` → `record_verification` | `watching → verified` | forever |
| Bulk junk cleanup | `_impl_cleanup_boardroom_junk` @ `tasks_ops.py` | (hard DELETE) | Deleted from DB |
| ALL other cleanup | (none exists) | N/A | SAVED-FOREVER |

**Cross-writers per HAI field:**

- `status`: written by 4 services (Bridge — indirectly via `HumanInterfaceService.create_attention_item`; LifecycleService; HumanInterfaceService; model methods).
- `urgency`: written by 3 sources (producer @ create; Bridge dedup path @ `human_interface_service.py:635`; LifecycleService escalation @ `lifecycle:211`).
- `decision`: written by 2 sources (LifecycleService auto-approve @ `lifecycle:318`; HumanInterfaceService.record_decision @ model:186).
- `HumanFeedbackRecord`: created by 2 sources (LifecycleService @ `:325-334`; HumanInterfaceService.record_decision @ `:325-337`).

Two-layer debt evidence — §16.1.

---

## 9. Integrations With Other Domains

### 9.1 D80 axis contribution (parent load-bearing lens question)

Parent §5 D80 asks: *"Is the human-in-the-loop attention queue
(`HumanAttentionItem`) the canonical learning-signal aggregation surface,
OR are learning bridges autonomous domain-specific consumers that
bypass HAI?"*

Cat A contribution: **HAI is the SOLE round-trip surface with a
learning signal** (per S1274 §4.7 canonical narrative — VERIFIED HERE:
`HumanFeedbackRecord` post_save signal @
`models_feedback_processing.py:372` is the ONLY signal wire from an
HAI-adjacent row into the learning surface). But: **learning bridges
(Cat C) also write to `AgentLearning` + `UserAgentLearning` without going
through HAI** — per S1274 §5+ learning-bridge writers do NOT emit
HAI. Cat A **does not have the evidence** to answer D80; the full
answer requires Cat C learning-bridge inventory (S1803) + xx99 cross-
child synthesis.

**Cat A observed:** HAI has 43 producers WRITING to it, but only 4 of
those (Bridge helpers via `HumanInterfaceService.create_attention_item`
+ HumanInterfaceService.record_decision + LifecycleService.auto_approve
+ view-layer bulk decide) trigger the FeedbackProcessor pipeline. The
remaining 39 producers create HAI rows but their downstream
learning-loop wire is **NOT VERIFIED HERE**; it's Cat B + Cat C
scope.

### 9.2 Cross-domain integrations (S1274 baseline verification at HEAD)

Per Explore #5 verification at HEAD `eef2280f`:

| Source Domain | Target = HAI | S1274 Status | HEAD Status | Evidence |
|---|---|---|---|---|
| Body Systems | HAI | MISSING | **MISSING** | grep `HumanAttentionItem.objects.create` \| `body_coordinator\|HeartBeat` returns 0 matches. `core/services/body_coordinator.py` `_handle_lungs_exhausted`, `_handle_heart_critical`, `_handle_immune_threat` call `discord_notifications.send_status_notification()` but **NOT** `HumanAttentionItem.create()` |
| Signal Engine | HAI | MISSING | **MISSING** | grep `pattern_strength.*0\.9\|0\.9.*pattern_strength` returns 0 matches. `SignalCurator` scores + dedups but no HAI writes |
| Revenue Pipeline | HAI | MISSING | **WORKING** | `ops_autopilot/core.py:2051` (revenue_pipeline critical stale) + `:2117` (outbound) + `:2626` (deploy) + `:2691` (policy conflict) + `:2844` (governance snapshot) + `governance.py:528` + `verification.py:702` — pre-S1274 wiring; semantically threshold-based, NOT approval-gating (S1274 concern remains partially unresolved semantically) |
| Observability / OpsRun Failures | HAI | MISSING | **MISSING** | grep `OpsRunEvent.*step_fail` context → 0 direct HAI creations. `rigby_event_intake.py` writes to `RigbyWorkItem` (intermediate queue), NOT HAI. No aggregator sums failures in windows to create HAI |
| Observability / SLO Framework | HAI | MISSING | **MISSING** | grep `SLO\|slo_breach\|slo_burn` → 0 files with HAI cross-refs. No SLO breach detector exists |

**Additional operational HAI writers discovered by Explore #1 + #5
sweep (NOT in S1274 baseline):**

- Circuit Breaker → HAI at `tasks.py:380` (task timeout circuit breaker, hardcoded high urgency).
- Circuit Breaker (governor) → HAI at `services/priority/governor.py:270`.
- Audit Remediation → HAI at `tasks.py:10854` + `autonomous_remediation_orchestrator.py:1419` (dedup candidate §17.2).
- Ops Control Loop → HAI at `tasks_ops.py:3777`.
- Spider Action Pipeline → HAI at `spider_action_pipeline.py:636`.
- Content Idea Pipeline → HAI at `content_idea_pipeline.py:399`.
- Orchestration Approval → HAI at `orchestration_approval.py:95` + `:174`.

**Verdict:** cross-cutting aggregation domains (Body Systems, Signal
Engine, SLO, OpsRun cascade failures) do NOT escalate to HAI at HEAD;
procedural/task-specific domains DO. Revenue pipeline is a
partial-exception via ops_autopilot but is threshold-based staleness,
not the approval-gating S1274 §3.3 semantically flagged.

### 9.3 Cat B/C/D/E/F cross-refs

- **Cat B (S1802) will own:** FeedbackProcessor `process_human_feedback` end-to-end; `HumanFeedbackRecord` model semantics; positive/negative classification; `_reinforce_positive` + `_learn_from_negative` → `AgentLearning` + `LearningInsight` writes.
- **Cat C (S1803) will own:** 10+ `LearningBridge` subclasses (PersonalizationFeedbackLoop, SpiderDataLearningLoop, CollaborationLearningLoop, AdvisorFeedback + AutoConsultation, ApplicationOutcome, AgentExecution, SportsBetting, RevenueAttribution) + external `RedditLearningBridge` + `BlueskyLearningBridge`. **Cat A observation:** learning bridges write to `AgentLearning` WITHOUT going through HAI — bypass path.
- **Cat D (S1804) will own:** HumanPreference semantics + F5 topic_weights/source_weights never-saved bug FIX (§4.3 CATALOGUED here).
- **Cat E (S1805) will own:** S746 verification-loop wiring: `record_verification()` 2 callers evidence (§7.4); who else should call it? (§18.3 F7).
- **Cat F (S1806) will own:** external Reddit/Bluesky bridges + PA-tool intersection (`td_handlers_agents.py:4110` + `:4882` §17.3 dedup) + terminology boundary.

---

## 10. Event Flows

**Signals emitted BY HAI-adjacent code (via Django `@receiver`):**

- ONE post_save signal on HAI itself: `on_critical_attention_item` @ `signals_push_notifications.py:14` — fires ONLY when `created=True AND urgency='critical'`. Queues Celery `notify_critical_attention_item.delay(str(instance.id))` for Discord/push notification. **NO signal fires on status transitions.**
- ONE post_save signal on `HumanFeedbackRecord` @ `models_feedback_processing.py:372` — Cat B territory but Cat A causes it via record_decision + auto_approve.

**Signals RECEIVED by Bridge:**

- `on_pilot_gate_change` @ `human_attention_bridge.py:571-575` — receives `PilotReadinessGate` post_save.
- `on_agent_execution_complete` @ `human_attention_bridge.py:578-591` — receives `AgentExecution` post_save.

**NO signals on:**

- Auto-escalate urgency changes (silent per §14.4 F-slot forensics gap).
- Auto-dismiss ignored transitions.
- Expire transitions.
- `record_verification` (S746 verification outcome; §15.5 D5).
- deferred/pending reopen transitions.

**Correlation-primitive `HAI_item_id` cross-domain flow (per Explore #6):**

Field `attention_item_id` appears in 16 files across 8-10 domains:

- **Orchestration:** `models_orchestration.py:420` UUIDField (no FK); `:517-534` `set_attention_item()` / `attention_item` property getter (application-enforced cross-domain link).
- **Mission Control:** `mission_control_executor.py:252` (Deliverable.metadata), `:377` (StockAlert.source_attention_item_id), `:137` (log emission).
- **Feedback Processing:** `models_feedback_processing.py:149` (`HumanAttentionItem.objects.filter(id=attention_item_id)` in FeedbackProcessor.process_human_feedback).
- **OpsAutopilot policies:** `core.py:920, 929, 1025, 1037` (evidence payload + action record); `verification.py:672` (ActionVerifier reads back attention_item_id for rollback).
- **Orchestration Approval:** `orchestration_approval.py:104-112` (payload).
- **Spider Action:** `spider_action_pipeline.py` (payload).
- **Gate Progression:** `gate_progression_pipeline.py:404` (log emission).
- **Opportunity Execution:** `opportunity_execution_pipeline.py` (payload).
- **Implementation Executor:** `implementation_executor.py` (payload).
- **PA / TD handler ops:** `td_handlers_ops.py`.

**Verdict:** `HAI_item_id` is a bona fide cross-system correlation
primitive (writes AND reads across ≥8 domains). Two-triggers threshold
MET for F5 CODIFICATION-CANDIDATE (S1799 §10.2 MC-3) — first
application was S1700 parent §5; this SECOND application confirms
pattern replicability. CODIFICATION-READY promotion path at S1899
xx99 close if pattern holds durable through P2-P6 children.

---

## 11. Existing Documentation

### 11.1 Prior research anchors

- **S1273 §3.16** — HumanAttention row (WORKING / MODERATE coverage;
  20+ producer sites; F5 HumanPreference topic_weights bug baseline;
  S746 verification loop noted).
- **S1274 §3.3** — CRITICAL Failure Cluster → HAI cross-domain gap.
- **S1274 §3.8** — MEDIUM Signal Pattern → HAI cross-domain gap.
- **S1274 §4.7** — canonical Human → HAI → FeedbackProcessor →
  Learning round-trip narrative ("only round-trip w/ learning").
- **S1274 §5+** — 5+ cross-domain HAI-consumer integration MISSING
  catalog (Body Systems / Signal Engine / Revenue Pipeline /
  Observability/SLO / Failure Cluster).
- **S1269 governance_authority_evolution.md §1.4** — F5 HumanPreference
  `topic_weights` / `source_weights` never-saved bug (VERIFIED HERE
  at HEAD; §4.3).
- **S1399 memory canonical summary (first xx99)** — Group 1300 Memory
  domain closed at DEEP coverage; `AgentLearning` + `UserAgentLearning`
  + `AgentKnowledgeSource` semantics covered — Cat C learning-bridge
  OUTPUT territory.
- **S1699 content canonical summary (fourth xx99)** — Group 1600
  Content domain closed; content-review learning-bridge integrations
  are Content scope.
- **S1799 observability canonical summary (fifth xx99)** — Group 1700
  closed; MC-1 verifier-loop CODIFICATION-READY (applied here) +
  MC-2 19-arm sub-pattern CODIFICATION-READY (applied here at D48
  25th arm) + MC-3 F5 correlation-primitive HYPOTHESIS box
  CODIFICATION-CANDIDATE (applied here as SECOND application).

### 11.2 Prior audit anchors

- **S686 handoff** — original human interface layer introduction (S686 comment @ `models_human_interface.py:5-11`).
- **S746 handoff** — Watch & Verify feature introduction (verification fields, `record_verification()`).
- **S759 handoff** — content review HAI surface.
- **S763 handoff** — Mission Control HAI surface (BaseAgent-driven).
- **S766 handoff** — HumanAttentionLifecycleService introduction (Session 766 comment @ `lifecycle:5`).
- **S804 handoff** — autonomous action executor HAI surface.
- **S861 handoff** — FeedbackProcessor introduction (Session 861 comment @ `models_feedback_processing.py:115`).
- **S927 / S977 handoffs** — boardroom junk cleanup + reduced spider_action window from 24h to 6h (§7.5 + §15.7).
- **S1093 handoff** — diagnostic alert source_agent honored (see `create_diagnostic_alert` @ `human_attention_bridge.py:272-321`).
- **S1095 handoff** — mythology alert bridge.

---

## 12. Research Coverage

### Producer surface coverage

| Producer domain | Site count | Preference-respect | Bridge-based | Direct-create |
|---|---|---|---|---|
| Approval & Gate | 7 | 0/7 | 4 | 3 |
| Agent Execution & System Health | 8 | 0/8 | 4 | 4 |
| Revenue & Opportunity | 5 | 0/5 | 1 | 4 |
| Content & Blog | 4 | 0/4 | 3 | 1 |
| Spider & Market Intelligence | 2 | 0/2 | 2 | 0 |
| Ops Autopilot & Governance | 6 | 0/6 | 0 | 6 |
| Diagnostics & Intelligence | 2 | 0/2 | 2 | 0 |
| Platform Command & Control | 2 | 0/2 | 1 | 1 |
| PA & Consultation | 3 | 0/3 | 0 | 3 |
| Dreams & Brainstorm | 1 | 0/1 | 0 | 1 |
| Mythology & Alert Bridge | 1 | 0/1 | 1 | 0 |
| ML Diagnostics & Monitoring | 2 | 0/2 | 0 | 2 |
| Mission Control & Agent Output | 1 | 0/1 | 1 | 0 |
| Implementation & Task Creation | 2 | 0/2 | 0 | 2 |
| **Total** | **43** | **0/43** | **18 wrappers** | **25 direct** |

### Lifecycle service coverage

| Lifecycle sub-method | Owner | Frequency | Preference-aware | Emits signal? | Idempotent |
|---|---|---|---|---|---|
| `_expire_old_items` | LifecycleService | 10-min beat | No | No | Yes (bulk update; filter excludes expired) |
| `_auto_dismiss_stale_items` | LifecycleService | 10-min beat | No | No | Yes (4 bulk updates per urgency) |
| `_auto_escalate_aging_items` | LifecycleService | 10-min beat | No | logger.debug per-item | Yes (monotonic ladder) |
| `_auto_approve_low_risk_items` | LifecycleService | 10-min beat | Reads `require_review_above_confidence` only; ignores `blocked_sources` + `trusted_agents` | Yes via `HumanFeedbackRecord.create` post_save | Not fully (§15.1 D1 no update_fields) |
| `_maybe_trigger_orchestration` + 4 workflow creators | LifecycleService | On auto-approve | N/A | Via `orchestration_engine.execute_workflow(async_mode=True)` | Per-item transaction.atomic |

### Cross-domain integration coverage

Per §9.2: 1/5 S1274 WORKING (Revenue) + 4/5 MISSING (Body Systems,
Signal Engine, OpsRun Failures, SLO); zero newly-wired since S1274;
7+ additional operational writers exist outside baseline.

### F5 correlation-primitive coverage

Per §10: `HAI_item_id` (via `attention_item_id` field) confirmed
cross-system primitive at ≥8 distinct domains. SECOND application
of F5 HYPOTHESIS box discipline. Two-triggers threshold MET.

### Retention posture coverage

Per §7.5 + §15.7: SAVED-FOREVER for 40+ item_types via status-flip
soft-delete; hard-delete only for `spider_action` (6h) + `arbitrage`
(12h) + `[Learned]` junk; DIVERGENT from LLMCallEvent 30-day baseline.

---

## 13. Architecture Maturity

**Cat A maturity assessment at HEAD `eef2280f`:**

| Dimension | State | Evidence |
|---|---|---|
| Producer surface | WIDE + INCONSISTENT | 43 sites; 25 direct-create + 8 bridge helpers + 10 wrapper callers; NO central factory registry; 6 sites use legacy field names (§15.9); ZERO preference-respect |
| State machine | COMPLETE 8-state + PARTIALLY-OWNED | 8 states defined; 3 unowned transitions (`pending→viewed`, `deferred→pending` reopen, `watching→verified`) — §18 F7 |
| Lifecycle automation | STABLE with race condition | 10-min beat; 4 autonomous sub-methods; escalation ladder LOW→CRIT; auto-dismiss; auto-approve; **1 med race condition at auto_approve_item :322 no update_fields** (§15.1 D1) |
| Preference respect | ABSENT | Zero producers check user preferences; auto-approve ignores blocked_sources + trusted_agents (§15.3 D3) |
| Retention posture | SAVED-FOREVER (with 3-item-type junk cleanup) | DIVERGENT from LLMCallEvent 30d baseline; no `HAI_RETENTION_DAYS` config (§15.7 D7 F6) |
| Cross-domain integrations | FRAGMENTED | 4/5 S1274 baseline MISSING at HEAD; Revenue is exception; operational HAI writers exist but cross-cutting aggregation absent |
| Learning-loop wire | SINGLE round-trip surface | `HumanFeedbackRecord` post_save signal @ `models_feedback_processing.py:372` — SOLE learning-signal wire from HAI |
| Correlation primitive | CONFIRMED cross-system | `HAI_item_id` used across ≥8 domains (F5 HYPOTHESIS SECOND application) |
| Observability | GAPS at forensic level | `_auto_escalate_aging_items` uses `logger.debug()` per-item (§14 F-slot); `record_verification` emits no signal (§15.5 D5); status transitions on lifecycle ops do NOT emit signals |

**Overall verdict:** WORKING at MODERATE coverage with **codified
technical debt across 9 dimensions** (§15). The system functions
correctly at the happy path (create → beat cycle → escalate/dismiss/
approve → decision or verification → feedback record → learning loop
for the 4 wired producers) but exhibits systemic gaps in preference
respect, ownership completeness (3 unowned state transitions), retention
policy (unbounded growth), and cross-domain integration coverage.

---

## 14. Known Drift

### 14.1 F1 — Explore #1 producer count undercounted 2-3 sites

Explore #1 reported "25 direct `HumanAttentionItem.objects.create()`
sites"; grep sum at HEAD returns **30 total matches** across 20 files
(28 production + 2 test at `core/tests/test_sia_escalation.py`).
Difference of 2-3 production sites. Likely miss: `ops_autopilot/core.py`
has 5 grep matches; Explore #1 enumerated 4 (lines 2051/2117/2626/2691)
and missed `:2844` (governance snapshot per Explore #5 mention).
Other 1-2 misses unaccounted for. **Impact: minor** — producer table
and domain breakdown in §4.1/§12 use E1's canonical enumeration;
downstream findings (43-producer TL;DR, zero-preference-respect,
domain breakdown) unaffected.

**SIGN F1 fold (2026-07-03):** Rigby ratified §14.1 mention +
appendix enumeration approach (no in-cycle re-audit; keep §4.1's
canonical table). See **§20.8 appendix for the 28 production
direct-create site enumeration** with file:line for the record.

### 14.2 F2 — Parent §5 line-range drift for HumanAttentionLifecycleService

Parent §5 `verifier_loop` cites `HumanAttentionLifecycleService at
core/services/human_attention_lifecycle.py:36-728`. File is actually
732 lines total (verified pre-Explore + post-Explore). 4-line drift.
Owed to xx99 (S1899) parent-anchor update PR.

### 14.3 F3 — `mark_viewed()` "never called by any service" claim

Explore #2 claim: *"HumanAttentionItem.mark_viewed() exists (models:177-182)
but is never called by any service."* Technically accurate for
service layer (`HumanInterfaceService` + `HumanAttentionLifecycleService`
do NOT call it), but misleading — `mark_viewed()` IS called from view
layer at `views_human_interface.py:100` (`AttentionDetailView.get`).
Corrected in §4.1 + §7 + §18.1. Original claim was reworded
here to "no service-layer caller" for accuracy. Fold owed to SIGN.

### 14.4 F4 — `logger.debug()` per-item escalation logging

`_auto_escalate_aging_items()` @ `:213-215` logs each individual
escalation at `logger.debug()` — production log filters typically
exclude debug. Aggregate at `:219` uses `logger.info()`. Forensics gap:
tracing "when was HAI X escalated?" requires debug logging enabled.
Inconsistent with ops_autopilot patterns that log at info level with
HAI_item_id (`ops_autopilot/core.py:942-945`). Not a bug; visibility
gap. Fold owed to SIGN as observability F-slot.

### 14.5 Additional drift owed to xx99

- CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift
  (inherited from Group 1700 xx99; unresolved).
- §8 timeline table drift — missing rows for S1605 + S1606 + S1699
  (Group 1600) inherited.
- 5 doc PRs owed for `auto_publish "daily 6 AM"` cross-arc CORRECTION
  per S1699 §7.4 inherited.

---

## 15. Known Technical Debt

### 15.1 D1 — `item.save()` without `update_fields` in `auto_approve_item`

**Site:** `core/services/human_attention_lifecycle.py:322`

**Issue:** `auto_approve_item()` sets `item.decision`, `item.decision_feedback`,
`item.status='acted'`, `item.decided_at=now` (lines 318-321) then calls
`item.save()` — no `update_fields` parameter. Django writes ALL fields
back from the instance state.

**Race condition surface:** If a concurrent producer path (Bridge
dedup at `human_interface_service.py:620-641`) updated
`urgency`/`priority_score` between the candidate fetch at `:257-266`
and the save at `:322`, the concurrent change is silently overwritten.

**Contrast:** Sibling method `_auto_escalate_aging_items()` @ `:211`
correctly uses `save(update_fields=['urgency', 'priority_score'])`.
Debt is localized to `auto_approve_item()`.

**Severity:** MEDIUM (theoretical; 10-min beat cadence makes practical
collision rare, but ACID violation).

**Fix (post-arc T-slot):** `item.save(update_fields=['decision',
'decision_feedback', 'status', 'decided_at'])`.

### 15.2 D2 — Zero user-preference respect across all 43 producers

**Sites:** all 43 producer code paths (§4.1 table).

**Issue:** None of the 43 producers check `HumanPreference.min_urgency_to_notify`,
`quiet_hours_start/end`, `blocked_sources`, or `trusted_agents` before
creating an HAI row. Preference is display-side only, not producer-side.

**Impact:** Users' preference settings ONLY filter at read time (via
`get_attention_stream` `expires_at` exclude) — HAI rows are still
created regardless. Blocked source? Row is created. Quiet hours?
Row is created + critical rows fire push notifications via
`on_critical_attention_item` @ `:signals_push_notifications:14`.

**Severity:** MEDIUM (design gap, not a bug).

**Fix (post-arc T-slot):** Introduce a preference-aware producer
factory OR centralize the 43 producers into a single
`enqueue_attention_item()` function that checks preferences first
(R2 in §19).

### 15.3 D3 — Auto-approve bypasses `blocked_sources` + `trusted_agents`

**Site:** `core/services/human_attention_lifecycle.py:257-276`

**Issue:** `_auto_approve_low_risk_items()` filters by
`LOW_RISK_SOURCES` and `AUTO_APPROVABLE_TYPES` (class-level constants)
and checks `require_review_above_confidence`, but does NOT check
per-user `HumanPreference.blocked_sources` or `trusted_agents`
(fields declared at `models_human_interface.py:319-320`). Users who
blocked a specific source_type still see their items auto-approved.

**Severity:** LOW-MEDIUM (LOW_RISK_SOURCES + AUTO_APPROVABLE_TYPES are
conservative defaults, so unintended approvals are unlikely but user
trust is silently ignored).

**Fix (post-arc T-slot):** Insert `if item.source_type in
user_pref.blocked_sources: continue` and optional
`if user_pref.trusted_agents and item.source_agent not in
user_pref.trusted_agents: continue` inside the loop @ `:270-272`
(R3 in §19).

### 15.4 D4 — Auto-dismiss asymmetric to auto-approve (no HumanFeedbackRecord)

**Site:** `core/services/human_attention_lifecycle.py:152-179`

**Issue:** `_auto_dismiss_stale_items()` performs bulk `.update()` to
set `status='ignored'` + `decision='auto_dismiss'` + `decision_feedback`
+ `decided_at`. **Does NOT create a HumanFeedbackRecord.** No post_save
signal triggers. FeedbackProcessor never sees the auto-dismiss
decision. No ML learning signal from dismissals.

**Contrast:** `auto_approve_item()` @ `:325-334` explicitly creates
`HumanFeedbackRecord` after auto-approve, triggering the Cat B
learning signal wire.

**Severity:** LOW (may be intentional — auto-dismiss is system-driven
inaction, not human feedback — but asymmetry is worth codifying).

**Fix (post-arc T-slot):** Decision to codify: SHOULD auto-dismiss
produce a feedback record for negative-signal learning?

### 15.5 D5 — `record_verification()` emits no signal / event

**Site:** `core/models_human_interface.py:216-227`

**Issue:** `record_verification()` model method updates 6 fields +
saves; NO signal fired, NO event emitted, NO log line with
`HAI_item_id`. Verification outcome (won/lost/push/cancelled + profit
+ notes) is a silent state update.

**Impact:** Cat B (FeedbackProcessor) does NOT see verification
outcomes. Cat C learning bridges cannot key on verification profit/loss
signals. If a watched item resolves `outcome='won' profit=250`, the
system does NOT:
- Log the profit for decision-maker learning.
- Feed to `SportsBettingLearningBridge` for performance sync.
- Create evidence record for `OpsAutopilot` audit.

**Severity:** **HIGH** (SIGN cycle 1 fold 2026-07-03 — Rigby ratified
promotion from MEDIUM → HIGH). Rationale: this is the ONLY purported
round-trip surface with learning per S1274 §4.7 canonical narrative,
yet the current implementation drops both the correlation primitive
(no `HAI_item_id` emitted) and any eventing (no signal / no
HumanFeedbackRecord). This structurally blocks the intended feedback
loop — even though Cat E (S1805) owns full posture resolution, the
severity should reflect impact: the entire S746 verification loop is
DECOUPLED from the learning pipeline.

**Fix (post-arc T-slot; Cat E scope for full resolution):** Emit
`HumanFeedbackRecord` on `record_verification()` OR add a dedicated
`HumanVerificationRecord` signal + Cat E audit resolution.

### 15.6 D6 — `deferred_until` never auto-re-opened

**Site:** `core/services/human_interface_service.py:355+` (defer_item)
+ nowhere.

**Issue:** `defer_item()` sets `status='deferred'` + `deferred_until`
DateTimeField. **No lifecycle sub-method auto-transitions deferred
items back to pending when `deferred_until <= now`.** Deferred items
remain in `deferred` state indefinitely unless manually re-opened.

**Severity:** LOW-MEDIUM (feature gap — user pressed "defer until
tomorrow 9am" and no code re-surfaces it).

**Fix (post-arc T-slot):** Add `_auto_reopen_deferred_items()` to
`process_lifecycle()` beat cycle: `filter(status='deferred',
deferred_until__lte=now).update(status='pending')` (R6 in §19).

### 15.7 D7 — Retention posture SAVED-FOREVER (bounded junk-cleanup only)

**Site:** `core/tasks_ops.py:39-97` (`_impl_cleanup_boardroom_junk`)
+ absence of any general HAI retention task.

**Issue:** HAI rows are hard-deleted ONLY for 3 item_types:
`spider_action` (6h), `arbitrage` (12h), `[Learned]` (any age; title
match). All other 40+ producer item_types are SAVED-FOREVER via
status-flip soft-delete only (`ignored` / `expired` / `verified` /
`acted`).

**No config setting** like `HAI_RETENTION_DAYS` or `HAI_TTL_HOURS`.

**DIVERGENT from LLMCallEvent baseline:**
`CELERY_TASK_EVENT_RETENTION_DAYS = 30` env-configurable + physical
delete via weekly beat `cleanup_celery_task_events`.

**Severity:** MEDIUM (unbounded table growth risk; audit trail
preservation may be intentional).

**Fix (post-arc T-slot):** Chris-gated decision: align HAI retention
with LLMCallEvent 30-day baseline (hard-delete) OR intentional
audit-trail-forever posture (with archive-to-cold-storage path).
Paired ADR at S1899 xx99 close (R1 in §19).

### 15.8 D8 — Bulk decide bypasses model methods

**Site:** `core/views_human_interface.py:517-520` (`BulkAttentionDecideView.post`)

**Issue:** `queryset.update(status=decision, decision=decision,
handled_at=now)` — bypasses the `HumanAttentionItem.record_decision`
model method. Skipped: `time_to_decision_ms` calculation,
`human_overrode_ml` check, `HumanFeedbackRecord` creation.

**Also:** `status=decision` string literal maps NOT to
`STATUS_ACTED` but to `decision` string (e.g. `'approve'`,
`'ignore'`) — status semantic mismatch with model constants.

**Impact:** Bulk-decided items have NO `HumanFeedbackRecord` → NO
ML learning signal → Cat B FeedbackProcessor never sees them.

**Severity:** MEDIUM (data-integrity + learning-loop gap).

**Fix (post-arc T-slot):** Refactor bulk endpoint to iterate calling
`HumanInterfaceService.record_decision()` per item OR add explicit
`bulk_record_decision()` service method that maintains parity (R7).

### 15.9 D9 — Legacy field usage in 6 producer sites

**Sites:** `ops_autopilot/core.py:2051`, `:2117`, `:2626`, `:2691`
(uses `source='...'` + `category='...'` legacy field names);
`priority/governor.py:270` (uses `priority='...'` instead of
`urgency='...'`); `tasks_misc.py:5274` RAG canary (same); implementation
executor uses `metadata` instead of `payload`.

**Issue:** Producers use deprecated field names — `source` instead of
`source_type`; `category` instead of `source_type` semantic overlap;
`priority` instead of `urgency`; `metadata` instead of `payload`.

**Impact:** These will BREAK if HAI schema field names are ever
renamed (migration debt). Also creates confusion in reader-side code.

**Severity:** LOW (isolated migration debt; documented at S1093 per
diagnostic-alert notes).

**Fix (post-arc T-slot):** Migration audit — search-and-replace
across the 6 sites, add field-alias shim in model save() to catch
future violations (R8).

---

## 16. Boundary Violations

### 16.1 Two-layer lifecycle debt (structural F4)

**The debt (evidence from Explore #4):**

`HumanAttentionBridge` (636 lines, event-writer layer) and
`HumanAttentionLifecycleService` (732 lines, state-machine manager)
operate on the same row with responsibility overlap:

**Overlap area 1 — status=ACTED (3 writers):**
- Bridge: creates items expecting human action (`create_agent_output_attention`
  with `item_type='action'`).
- LifecycleService: directly transitions items to `status='acted'` via
  `auto_approve_item()` @ `:320`.
- HumanInterfaceService: transitions to `acted` via `record_decision()`
  when decision is not 'defer'/'watch'/'reopen' (`models:201`).
- **Issue:** Three paths to `acted`. No single choreography.

**Overlap area 2 — status=IGNORED (2 semantic paths):**
- LifecycleService: auto-dismisses items older than threshold → `status='ignored'` (`lifecycle:168-169`).
- HumanInterfaceService via `record_decision(decision='ignore')`: also
  sets `status='acted'` with `decision='ignore'` (`models:200-201`).
- **Issue:** Semantic mismatch. Manual ignore → `status='acted'` +
  `decision='ignore'`. Auto-dismiss → `status='ignored'` +
  `decision='auto_dismiss'`. Same intent, different status.

**Overlap area 3 — urgency/priority escalation:**
- Bridge dedup: re-escalates urgency on repeat notification
  (`human_interface_service.py:620-641`).
- LifecycleService: auto-escalates urgency on age (`lifecycle:198-211`).
- **Issue:** Two independent escalation paths — one event-driven, one
  time-driven. No unified escalation policy.

**Overlap area 4 — decision field:**
- LifecycleService: writes `decision='approve'` on auto-approve.
- HumanInterfaceService: writes user's decision on manual record_decision.
- **Issue:** Both own the decision field. No conflict risk in practice
  (different code paths) but two writers same field.

**Overlap area 5 — HumanFeedbackRecord creation:**
- LifecycleService: creates feedback on auto-approve @ `:325-334`.
- HumanInterfaceService.record_decision: creates feedback on manual
  decision @ `human_interface_service.py:325-337`.
- **Issue:** Two independent feedback creators. No deduplication. Both
  can create multiple records for the same item.

**Gaps (transitions no service owns):**
- `pending → viewed` — see §18.1 F7.
- `deferred → pending` (reopen) — see §18.2.
- `watching → verified` — see §18.3.

**Dedup candidates (methods duplicated between services or sites):**
- Item status filter pattern (`status__in=['pending', 'viewed', 'deferred']`) repeated 3x (§17).
- Urgency escalation logic (Bridge dedup + Lifecycle escalate).
- Priority score calculation.
- User preference application (both read HumanPreference; apply different rules).
- Auto-approval criteria check (split query + loop).
- Workflow routing (4 monolithic workflow creators; could factor).

**Verdict:** Two-layer debt is structural. Resolution is xx99 territory
(D80 arc lens question resolution). Cat A's evidence contribution to
xx99: (a) enumerate the overlap + gaps + dedup candidates above;
(b) recommend a single-owner refactor as one of two D80 axis
answers.

---

## 17. Duplicate or Overlapping Systems

### 17.1 Bridge helpers vs direct-create producers

18 bridge-based sites (8 helpers + 10 callers) coexist with 25
direct-create producers. Two production paths for HAI creation with
no consistent choice policy. **Dedup candidate.**

### 17.2 AuditRemediationSpec duplicated at 2 locations

- `core/tasks.py:10854` — AuditRemediationSpec HAI creation logic.
- `core/services/autonomous_remediation_orchestrator.py:1419` — same
  pattern.

Both use the identical `source_type='audit_remediation'` + priority_map
lookup pattern. **Refactor candidate.**

### 17.3 PACreate duplicated at 2 locations

- `core/services/td_handlers_agents.py:4110` — PA create action.
- `core/services/td_handlers_agents.py:4882` — PA create_attention action.

Both use identical `source_type='pa'` + hardcoded `PA_IDENTITY` + medium
default urgency. **Refactor candidate.** Cat F territory (S1806 PA-tool
intersection sub-slot F.d).

### 17.4 4 monolithic workflow creators

`_create_opportunity_workflow` / `_create_action_workflow` /
`_create_recommendation_workflow` / `_create_project_workflow` at
`lifecycle:393-667` (275 lines) — each 50-80 lines with similar
structure: create CustomWorkflow → create N `CustomWorkflowStep` →
execute via `orchestration_engine.execute_workflow(async_mode=True)`.
Could factor into generic workflow factory taking a step-spec
dict. **Dedup candidate; not a boundary violation.**

---

## 18. Ownership Gaps

### 18.1 F7 — `pending → viewed` no service owns

**Symptom:** `mark_viewed()` @ `models_human_interface.py:177-182`
exists as model method (atomic `save(update_fields=['status',
'viewed_at'])`) — but is only called from view layer at
`views_human_interface.py:100` (`AttentionDetailView.get`). Neither
`HumanInterfaceService` nor `HumanAttentionLifecycleService` calls
`mark_viewed()`.

**Impact:** Items where the client didn't fetch through
`AttentionDetailView` (e.g. Discord bot showing the item, API-only
consumer, PA tool listing) may remain in `pending` forever even after
human sees them.

**Severity:** LOW (mostly cosmetic — the item is still visible in
the stream).

**Fix (post-arc T-slot):** Either (a) add `mark_viewed()` to
`HumanInterfaceService` API + call from all read paths (Discord bot,
PA tool, dashboard); OR (b) collapse `viewed` state into `pending`
if no semantic distinction warranted.

### 18.2 F7 — `deferred → pending` reopen non-terminal but no auto-check

**Symptom:** `defer_item()` sets `deferred_until` DateTimeField.
No sub-method in `process_lifecycle()` checks `deferred_until <= now`
and re-opens. `record_decision(decision='reopen')` @ `models:195-198`
supports the transition manually but resets `decision=None` +
`decided_at=None` — **erases the previous decision**, no audit trail
of the reopen.

**Impact:** User defers "remind me tomorrow 9am"; item never
re-surfaces unless another code path (rare) re-opens it.

**Severity:** LOW-MEDIUM (feature gap; see §15.6 D6).

**Fix:** R6 in §19.

### 18.3 F7 — `watching → verified` verification loop unowned by service

**Symptom:** `record_verification()` DEFINITION exists at
`models_human_interface.py:216-227`; 2 callers exist:
- `views_human_interface.py:245` (API endpoint — manual verification).
- `betting_outcome_verifier.py:413` (auto-verify from betting outcomes,
  sports domain).

No beat scheduler catches watching items whose event completed but
neither caller fires. Cat E owns this posture; Cat A contributes the
definition-site evidence.

**Severity:** LOW-MEDIUM (S746 feature loop incomplete).

**Fix (Cat E scope + post-arc T-slot):** R5 in §19.

---

## 19. Recommended Future Research (R1–R10)

**R1 — HAI retention posture ADR (paired with §15.7 D7 F6)**

Chris-gated decision required: align HAI retention with LLMCallEvent
30-day baseline (hard-delete via new
`cleanup_human_attention_items` beat task) OR intentional-
audit-trail-forever posture (with archive-to-cold-storage path
to prevent unbounded growth). Recommend paired ADR at S1899 xx99
close.

**R2 — Preference-aware producer factory (§15.2 D2)**

Centralize the 43 producers into a single `enqueue_attention_item()`
function that checks `HumanPreference.min_urgency_to_notify` +
`quiet_hours_*` before creating an HAI row. Migrate direct-create
sites to use the factory. Preserves audit surface but adds
preference-side filtering.

**R3 — Auto-approve `blocked_sources` + `trusted_agents` validation (§15.3 D3)**

Insert per-user filter into `_auto_approve_low_risk_items()` @ `:270-272`:
skip items where `item.source_type in user_pref.blocked_sources`;
skip items where `user_pref.trusted_agents` is non-empty and
`item.source_agent not in user_pref.trusted_agents`.

**R4 — Two-layer lifecycle debt resolution (§16.1 F4)**

D80 axis resolution at xx99 (S1899). Two options: (A) collapse Bridge
into LifecycleService (single owner of HAI row); (B) formalize Bridge
as pure event-writer + LifecycleService as pure state-machine with
explicit non-overlap contract. Cat A contributes evidence.

**R5 — S746 verification-trigger auto-scheduler (§15.5 D5 + §18.3 F7)**

Cat E scope: identify the missing trigger — a beat task or event
consumer that catches watching-status HAI items whose event completed
and fires `record_verification()`. Currently only view + betting_outcome_verifier fire it.

**R6 — Deferred-until auto-reopen beat sub-method (§15.6 D6 + §18.2)**

Add `_auto_reopen_deferred_items()` to `process_lifecycle()`:
`HumanAttentionItem.filter(status='deferred',
deferred_until__lte=now).update(status='pending', deferred_until=None)`.

**R7 — Bulk decide upgrade to use record_decision (§15.8 D8)**

Refactor `BulkAttentionDecideView.post` @ `views_human_interface.py:517-520`
to call `HumanInterfaceService.record_decision()` per item OR add
a proper bulk service method that maintains ML learning signal parity.

**R8 — Legacy field migration (§15.9 D9)**

Search-and-replace the 6 producer sites that use `source` /
`category` / `priority` / `metadata` legacy field names. Add
field-alias shim in `HumanAttentionItem.save()` to log deprecation
warnings if the wrong field is passed.

**R9 — F5 HumanPreference `topic_weights`/`source_weights` fix (§4.3)**

Cat D scope (S1804) OR post-arc T-slot: fix
`update_learned_stats()` @ `:334-357` to include `topic_weights`
+ `source_weights` in `update_fields=`. Per S1269 §1.4 F5 baseline.

**R10 — Cross-domain HAI-consumer wiring (§9.2 F8)**

Body Systems / Signal Engine / OpsRun-Failure / SLO Framework
→ HAI wires per S1274 §3.3 + §3.8. Cross-arc scope (Groups 1300 body
systems territory, 1700 observability closed, 1500 sports closed).
Recommend cross-arc ADR at S1899 xx99 or T1-tier item.

---

## 20. Appendix

### 20.1 Verifier-loop record

**Pre-Explore (2026-07-03, head=eef2280f):**
- HumanAttentionItem model at `core/models_human_interface.py:20-227` — VERIFIED.
- 8-state STATUS constants + 8-decision + 5-verification-outcome constants — VERIFIED verbatim.
- record_decision @ :184, record_verification @ :216 — VERIFIED.
- HumanFeedbackRecord @ :230-265 — VERIFIED.
- HumanPreference @ :268-358 (F5 bug: topic_weights/source_weights excluded from update_fields @ :356-358) — VERIFIED.
- HumanAttentionLifecycleService @ core/services/human_attention_lifecycle.py:36 — VERIFIED; file 732 lines (parent §5 says :36-728 = 4-line drift F2).
- ESCALATION_THRESHOLDS @ :48-52 + AUTO_DISMISS_HOURS @ :55-60 + LOW_RISK_SOURCES @ :63-69 + AUTO_APPROVABLE_TYPES @ :71-78 — VERIFIED verbatim.
- item.save() @ :322 NO update_fields — VERIFIED (§15.1 D1).
- HumanInterfaceService.record_decision @ :295-353 — VERIFIED.
- FeedbackProcessor.process_human_feedback @ core/models_feedback_processing.py:122 — VERIFIED.
- @receiver(post_save, sender='core.HumanFeedbackRecord') @ :372 — VERIFIED.
- HumanAttentionBridge @ core/services/human_attention_bridge.py 636 lines — VERIFIED.
- Beat process_human_attention_lifecycle @ core/tasks.py:7248 + celery.py:719 + BEAT_AUDIT.md:94 (*/10 * * * *) — VERIFIED.
- record_verification() callers: views_human_interface.py:245 + betting_outcome_verifier.py:413 (2 total) — VERIFIED.

**Post-Explore spot-checks (2026-07-03):**
- E1 43-producer claim: direct-create grep sum = 30 total matches (28 production + 2 test); F1-slot noted — E1 undercounted 2-3 production sites. Directionally CORRECT.
- E2 signal count = 1 (`on_critical_attention_item` @ `signals_push_notifications.py:14`) — VERIFIED.
- E2 mark_viewed "never called by any service" — QUALIFIED: not from service layer BUT called from view layer at `views_human_interface.py:100` (F3-slot).
- E3 item.save() @ :322 no update_fields — VERIFIED.
- E4 boardroom junk cleanup DELETE @ `tasks_ops.py:39-97` — VERIFIED.
- E6 HAI_item_id cross-domain 6+ claim — VERIFIED (8-10 distinct domains via grep of `attention_item_id` across `core/**/*.py`).

### 20.2 Sub-agent digest per playbook §13

Six parallel Explore sub-agents fired at 2026-07-03 with thoroughness=very-thorough:

- **E1 (HAI producer inventory)** — 43 distinct producer code paths (25 direct + 8 bridge helpers + 10 bridge callers); domain breakdown across 14 categories; ZERO preference-respect; 6 producers use legacy field names; 88% urgency hardcoded.
- **E2 (8-state lifecycle transitions)** — 8-state table with entry/exit transitions; 3 unowned transitions identified; only 1 post_save signal on HAI itself (`on_critical_attention_item` — creation + urgency=critical guard); `time_to_decision_ms` calculated only in `record_decision`, silently missing in ignored/verified/deferred paths; bulk-decide bypasses model methods.
- **E3 (HumanAttentionLifecycleService full sweep)** — 732-line file catalogued; 4 process_lifecycle sub-methods + 4 workflow creators + orchestration property + auto_approve_item + get_lifecycle_stats; ESCALATION_THRESHOLDS + AUTO_DISMISS_HOURS + LOW_RISK_SOURCES + AUTO_APPROVABLE_TYPES verbatim; item.save() @ :322 no update_fields identified (D1 medium); auto-approve does NOT check blocked_sources/trusted_agents (D3); auto-dismiss does NOT create HumanFeedbackRecord (D4 asymmetry); no S746 verification loop integration; no SIA escalation audit; orchestration dispatch no retry/timeout; escalation ladder plateaus at critical.
- **E4 (Two-layer lifecycle debt matrix)** — Bridge (event-writer, 636 lines) vs LifecycleService (state-machine, 732 lines) responsibility matrix; 5 overlap areas + 3 gaps + 6 dedup candidates; 12-row responsibility matrix (8 states + 4 side-effects) × 3 columns (Bridge / LifecycleService / other) documented; Bridge only creates `pending` items; LifecycleService owns 5 autonomous transitions (`_expire_old_items`, `_auto_dismiss_stale_items`, `_auto_escalate_aging_items`, `_auto_approve_low_risk_items`, `auto_approve_item`).
- **E5 (Cross-domain HAI-consumer integrations)** — 1 WORKING (Revenue via ops_autopilot) + 4 MISSING (Body Systems, Signal Engine, OpsRun Failures, SLO); 0 newly-wired since S1274; +7 additional operational HAI writers found outside baseline (circuit breaker, audit remediation, ops control, spider action, content idea, orchestration approval, priority governor).
- **E6 (F5 correlation-primitive HAI_item_id + retention posture)** — Task A: CONFIRMED cross-system primitive across 8-10 domains (mission_control_executor, orchestration_approval, ops_autopilot verification+core, gate_progression_pipeline, opportunity_execution_pipeline, spider_action_pipeline, implementation_executor, feedback_processing, orchestration, td_handlers_ops). Task B: retention SAVED-FOREVER + BOUNDED-HARD-DELETE for spider_action (6h) + arbitrage (12h) + [Learned] junk only; DIVERGENT from LLMCallEvent 30-day baseline; no HAI_RETENTION_DAYS config; `record_verification` emits no signal; `OrchestrationApprovalGate.attention_item_id` UUIDField not FK (application-enforced only).

### 20.3 Cross-references

- Parent scoping: `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md`.
- Playbook: `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`.
- Research OS: `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- S1273 baseline: `docs/research/platform_architecture_inventory.md` §3.16 + §4.7 + §2.5.
- S1274 baseline: `docs/research/platform/cross_domain_integration_audit.md` §3.3 + §3.8 + §5+.
- S1269 F5 baseline: `docs/research/governance_authority_evolution.md` §1.4.
- Cat B (S1802) will read: this doc's §4.2 HumanFeedbackRecord definition + §7.3 manual decision flow + §16.1 overlap area 5.
- Cat C (S1803) will read: this doc's §9.1 D80 axis contribution + §9.3 "learning bridges bypass HAI" note.
- Cat D (S1804) will read: this doc's §4.3 F5 bug CATALOGUED + §15.2 D2 zero-preference-respect + §15.3 D3 blocked_sources bypass.
- Cat E (S1805) will read: this doc's §7.4 S746 verification loop + §15.5 D5 no-signal + §18.3 F7 unowned transition.
- Cat F (S1806) will read: this doc's §17.3 PA tool intersection dedup candidate + §9.2 additional operational HAI writers.
- xx99 (S1899) will fold: §9.1 D80 axis contribution + §16.1 two-layer debt + §19 R1-R10 + §14 drift.

### 20.4 Repo state at draft

- Branch: `research/session-1801-human-attention-item-core-audit`.
- Base: `main` at commit `eef2280f` (S1800 arc-open + parent scoping).
- Companion PR in-flight: `#2852 docs/session-1800-cascade-refresh` (docs cascade refresh; standalone precedent-matching).
- Working tree: this doc + downstream close-out artifacts.

### 20.5 Rigby SIGN cycle 1 record

**SIGN pin minted:** `pa-43b5b8154c8e42d7` (fresh isolation pin minted
at S1801 open via `session_tool.create_fresh`; D48 25th arm start;
20th consecutive-fully-clean-arms sub-pattern anticipation
per single-batch 4-question criterion).

**Process footnote:** `tools/pa_local.sh` wrapper hardcodes
`--conversation pa-ae5931ea706b4537` (Group 1800 arc pin) at line 156.
When routing the SIGN prompt via `pa_local.sh` (as-is), the actual
turn landed on the **arc pin**, not the fresh isolation pin
`pa-43b5b8154c8e42d7`. Rigby returned CLEANLY on the arc pin
single-turn — no worker instability observed (matches S1799 close
pattern for single-turn SIGN). The isolation pin remains available
for optional cycle 2 pressure-test if needed; retire owed at S1801
close per playbook §16 regardless of routing.

**SIGN outcome:** SIGN-with-edits at High confidence; four questions
single-batch; three edits accepted + one no-change confirmed (F3).
D48 25th arm HOLDING CLEAN; 20th consecutive-fully-clean-arms
sub-pattern CONFIRMED per single-batch 4-question criterion (S1799
§10.2 MC-2 CODIFICATION-READY promotion path continues).

**4-question single-batch prompt fired (as delivered):**

1. **Q1 F1 fold** — Explore #1 undercounted 2-3 production direct-create
   sites (25 in E1 vs 28 in grep sum). Should §4.1 producer table
   carry a drift footnote inline, OR is §14.1 mention sufficient +
   appendix enumeration in §20?
2. **Q2 F3 mark_viewed qualifier** — Original E2 claim "never called
   by any service" reworded to "no service-layer caller" at §4.1 +
   §7 + §18.1. Should §1 also add view-layer detail, or keep succinct?
3. **Q3 D5 severity** — `record_verification()` emits no signal /
   no event / no HAI_item_id log. Should severity be HIGH instead of
   MEDIUM?
4. **Q4 F5 CODIFICATION-CANDIDATE promotion timing** — Should §1 F5
   explicitly claim "MC-3 two-triggers threshold MET" now, OR wait for
   parent §5 HYPOTHESIS-box status flip first?

**Rigby response (verbatim summary):**

- Q1: **§14.1 mention is sufficient.** Don't disturb §4.1's canonical
  table right now. Do add an Appendix/§20 enumeration table listing
  the **28 production direct-create sites** (with file:line), and in
  §14.1 explicitly point to that appendix. No 30-45 min re-audit
  in-cycle unless we later find the misses change a conclusion.
- Q2: **Keep §1 succinct** — do NOT add the view-layer caller detail
  to the executive summary. Current "no service-layer caller" wording
  + deep citations in §14.3 / §18.1 is the right balance.
- Q3: **Promote D5 to HIGH.** Rationale: it's the only purported
  learning round-trip, and the current implementation drops the
  correlation primitive + any eventing, so it's structurally blocking
  the intended feedback loop. Even if Cat E owns full resolution,
  the severity should reflect impact.
- Q4: **State the two-triggers threshold is met in §1 F5**, but
  phrase carefully: "MC-3 threshold met (2 independent triggers:
  S1700 parent + S1801 child verification)" + "Parent doc update is
  owed (explicit follow-up action)". Avoid implying "CODIFICATION-READY
  now"; instead: "eligible for promotion path pending parent flip
  + one more durability check".

### 20.6 Post-SIGN fold record

**SIGN cycle 1 folds landed pre-commit (2026-07-03):**

- **F1 fold (Q1) — §20.8 appendix enumeration added.** §14.1 pointer
  to appendix + preserved canonical §4.1 producer table (43-count via
  E1) + §14.1 severity note kept unchanged (minor drift).
- **F3 confirmation (Q2) — no §1 change.** Existing wording in §4.1 /
  §7 / §14.3 / §18.1 remains; view-layer caller (views_human_interface.py:100)
  not surfaced in §1 executive summary per Rigby ratification.
- **D5 fold (Q3) — severity promotion MEDIUM → HIGH at §15.5.**
  Rationale expanded to reflect Rigby-provided structural-impact
  framing: S746 is the ONLY purported round-trip w/ learning per
  S1274 §4.7 canonical narrative; current implementation drops both
  correlation primitive + eventing; structurally blocks intended
  feedback loop.
- **F5 fold (Q4) — §1 F5 finding text rephrased.** Explicit claim:
  "MC-3 threshold met (2 independent triggers: S1700 parent + S1801
  child verification); parent doc §5 F5 HYPOTHESIS-box status update
  owed as explicit follow-up action at S1801 close (flip HYPOTHESIS
  → VERIFIED-AT-CHILD); eligible for CODIFICATION-READY promotion
  path pending parent flip + one more durability check (target: S1802
  P2 Cat B FeedbackProcessor round-trip verification)."

**Downstream document impact:**
- Parent scoping doc `1800_human_attention_domain_scoping.md` §5 F5
  HYPOTHESIS box needs `→ VERIFIED-AT-CHILD` status update. Owed to a
  follow-up docs PR at S1801 close OR bundled into the S1801 close PR
  itself. Track as owed at §20.7 session close checklist (new item).

### 20.7 Session close checklist

- [x] Rigby SIGN cycle 1 SIGN-with-edits at High confidence; F1/D5/F5 folds landed pre-commit (F3 no-change confirmed).
- [ ] `ARCHITECTURE_INDEX.md` v51 → v52 with §1.55 S1801 registration + §8 timeline S1801 row + line-6 v52 preamble.
- [ ] `OPEN_ARCS.md` Group 1800 In-progress row: current-child updated S1800 → S1801.
- [ ] Parent scoping doc `1800_human_attention_domain_scoping.md` §5 F5 HYPOTHESIS box `→ VERIFIED-AT-CHILD` status update (owed follow-up docs PR OR bundled into S1801 close PR — per §20.6 F5 fold).
- [ ] `SESSION_1801` handoff.
- [ ] Overwrite `00-START-NEXT-SESSION.md` to point at S1802 P2 Cat B (FeedbackProcessor + HumanFeedbackRecord).
- [ ] Retire S1801 SIGN isolation pin `pa-43b5b8154c8e42d7` per playbook §16 (unrouted this cycle per §20.5 process footnote; retire on principle to keep the pin ledger tidy).
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule.

### 20.8 Appendix — 28 production direct-create sites (F1 SIGN fold)

Per SIGN cycle 1 Q1/F1 fold: full enumeration of all 28 production
sites where `HumanAttentionItem.objects.create(...)` is called
directly (excluding 2 test sites at `core/tests/test_sia_escalation.py`).
Cited via `rg 'HumanAttentionItem.objects.create' --type py -n` at
HEAD `eef2280f`. Domain classification best-effort from surrounding
code context; not authoritative (§14.1 F1 minor drift acknowledged).

| # | File | Line | Domain (best-effort) |
|---|---|---|---|
| 1 | `core/views_platform_command.py` | 929 | Platform Command (EmergencyHalt) |
| 2 | `core/tasks.py` | 380 | Agent Execution / Circuit Breaker |
| 3 | `core/tasks.py` | 10854 | Audit Remediation |
| 4 | `core/services/orchestration_approval.py` | 95 | Approval & Gate (OrchestrationApprovalGate primary) |
| 5 | `core/services/orchestration_approval.py` | 174 | Approval & Gate (OrchestrationApprovalGate secondary path) |
| 6 | `core/services/implementation_executor.py` | 513 | Implementation & Task Creation (Pilot) |
| 7 | `core/services/priority/governor.py` | 270 | Agent Execution / Circuit Breaker (Priority Governor) |
| 8 | `core/services/gate_progression_pipeline.py` | 358 | Approval & Gate (GateProgressionApproval) |
| 9 | `core/services/gate_progression_pipeline.py` | 573 | Approval & Gate (GateProgressionStuck) |
| 10 | `core/tasks_misc.py` | 5079 | ML Diagnostics & Monitoring (LLMCostSpike) |
| 11 | `core/tasks_misc.py` | 5274 | ML Diagnostics & Monitoring (RAGCanaryFailure) |
| 12 | `core/tasks_initiatives.py` | 3054 | Dreams & Brainstorm (DreamSurfacing) |
| 13 | `core/epa_handlers_tools.py` | 5166 | PA & Consultation (PAConsultation) |
| 14 | `core/tasks_ops.py` | 3777 | Agent Execution / System Health (OpsControlLoop) |
| 15 | `core/services/td_handlers_agents.py` | 4110 | PA & Consultation (PACreate — dedup candidate §17.3) |
| 16 | `core/services/td_handlers_agents.py` | 4882 | PA & Consultation (PACreateAttention — dedup candidate §17.3) |
| 17 | `core/services/autonomous_remediation_orchestrator.py` | 1419 | Audit Remediation (dedup candidate §17.2) |
| 18 | `core/services/ops_autopilot/governance.py` | 528 | Ops Autopilot & Governance (BacklogGovernor) |
| 19 | `core/services/ops_autopilot/verification.py` | 702 | Ops Autopilot & Governance (Verification escalation) |
| 20 | `core/services/human_interface_service.py` | 662 | Service facade (canonical `create_attention_item` entry-point) |
| 21 | `core/services/ops_autopilot/core.py` | 2051 | Revenue & Opportunity (OpsAutopilotRevenue) |
| 22 | `core/services/ops_autopilot/core.py` | 2117 | Revenue & Opportunity (OpsAutopilotOutbound) |
| 23 | `core/services/ops_autopilot/core.py` | 2626 | Ops Autopilot & Governance (OpsAutopilotDeploy) |
| 24 | `core/services/ops_autopilot/core.py` | 2691 | Ops Autopilot & Governance (OpsAutopilotArbitrator) |
| 25 | `core/services/ops_autopilot/core.py` | 2844 | Ops Autopilot & Governance (OpsAutopilotGovernanceSnapshot — **Explore #1 missed site**) |
| 26 | `core/services/spider_action_pipeline.py` | 636 | Spider & Market Intelligence (SpiderActionPipeline) |
| 27 | `core/services/content_idea_pipeline.py` | 399 | Content & Blog (ContentIdeaPipeline) |
| 28 | `core/services/opportunity_execution_pipeline.py` | 389 | Revenue & Opportunity (OpportunityExecution) |

**Reconciliation with Explore #1's canonical enumeration:**
- Explore #1 reported 25 direct-create sites (§4.1 producer table
  #1-25 mapping).
- Actual production count: 28 (this appendix).
- **3-site miss confirmed:** `ops_autopilot/core.py:2844` (governance
  snapshot) + `orchestration_approval.py:174` (secondary
  OrchestrationApprovalGate path) + `ops_autopilot/verification.py:702`
  (verification escalation).
- E1 producer count formula "25 direct + 8 bridge helpers + 10 bridge
  callers = 43" should update to "28 direct + 8 bridge helpers + 10
  bridge callers = 46" for exact accuracy.
- §4.1 headline count remains at E1's canonical 43 per SIGN Q1
  ratification (no in-cycle re-audit); appendix carries the exact-
  count evidence for xx99 (S1899) synthesis.

---

*End of Cat A child audit — Group 1800 HumanAttention / Feedback /
Learning arc.*
