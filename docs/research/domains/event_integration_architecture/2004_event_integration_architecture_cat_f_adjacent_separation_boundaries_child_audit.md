---
title: "Group 2000+ P4 Cat F — Adjacent / Separation Boundaries consolidation child audit (seam audit across 10 adjacent planes: Memory 1300 + Sports 1500 + Content 1600 + Observability 1700 + HAI 1800 + Authority Enforcement 1900 + Employee OS + Frontend + API + Discord)"
session: 2004
child_slot: P4_cat_f
domain_slug: event_integration_architecture
research_group: 2000
category: child_audit_consolidation
authority: research-consolidation for Category F per parent §5.4 D4 sequence + FOURTH AND LAST child under Group 2000+; consumes P1 §10 producer/consumer map + P2 §7 HAI event contract + §10 six-plane learning-surface event schema + §17 consumer registry + §20.9 F.PER-USER-AUTHORITY-MECHANISM + P3 §10.2 six-substrate separation contract + §10.3 intentional-dual-emission register + §10.4 substrate × HAI-event mapping + §10.5 WebSocket ↔ EventBus overlap resolution + §14.1 F11 spider-data three-substrate drift codification + §19.1.6 F.SYMBOL-MAPPING-EMISSION-VERIFICATION T-slot registration; produces separation-boundary posture register + per-plane emission touchpoint + consumer-registration seam + duplicate-emission drift audit + Fleet Events seventh-substrate discovery (F13) for xx99 §5 consolidated domain shape + xx99 §8 follow-on queue input
head_commit: 7fc1bc1c
status: draft
date: 2026-07-04
last_verified: 2026-07-04
authors: Claude Code (Chris directed via short command "start research group 2004" at S2004 open per Research OS §5 request-classification RESEARCH class §8.1 startup contract; interpretation: Chris continuing Group 2000+ arc into child slot P4 per parent §5.4 CONSOLIDATION shape + S1904 Group 1900 Cat F precedent + S1806 Group 1800 Cat F precedent; Rigby confirmed service_context: local + arc pin ownership pre-audit on `pa-dd7e973617da464d`)
prior_children:
  - 2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md (S2001 P1 Cat A — EventBus producer/consumer map + F1-F18 findings + F8 dual-mechanism drift + F9 consumer beat-dormancy + F11 spider-data three-substrate drift + F14/F15 handler-failure loop + F17 registration-surface gap + F18 handler decorativeness)
  - 2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md (S2002 P2 Cat B — HAI event schema contract + §7.9 canonical + mirror + §10 six-plane learning-surface event schema + §17 Consumer Registry + §17.3 two-class retention posture + §20.9 F.PER-USER-AUTHORITY-MECHANISM event-emission contract)
  - 2003_event_integration_architecture_cat_c_cross_substrate_composition_design_child_audit.md (S2003 P3 Cat C — 6-substrate separation contract §10.2 three-axis selector + §10.3 5 sanctioned dual-emission patterns + §10.3.4 WebSocket UI-render fanout D4 + §10.3.5 parallel-telemetry per concern + §10.4 substrate × HAI-event mapping 12 events + §10.5 WebSocket ↔ EventBus overlap resolution + §14.1 F11 codification + §14.3 double-emission detector binding + §19.1.6 F.SYMBOL-MAPPING-EMISSION-VERIFICATION §19.10.4 F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN)
parent: 2000_event_integration_architecture_domain_scoping.md
delegates_to:
  - xx99 S2099 canonical summary — consumes this doc's §17 separation-boundary posture register + §7 per-plane emission touchpoint + consumer-registration seam matrix + §19 R-slot follow-on queue candidates
related_arcs:
  - 1300 Memory (AgentLearning + UserAgentLearning writer plane; signal_aggregation_service Fleet Events emission; Cat F.a Memory seam)
  - 1500 Sports (BettingOutcomeVerifier + SportsBettingLearningBridge + 8 WebSocket consumers; Cat F.b Sports seam)
  - 1600 Content (Content deliberation pipeline + PublishGate + ClaimsPack; Cat F.c Content seam)
  - 1700 Observability (CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord 4-telemetry-substrate write-ownership; Cat F.d Observability seam)
  - 1800 HAI (HumanAttentionItem + HumanFeedbackRecord + HumanPreference + auto-approve gate + PAConversationConsumer; Cat F.e HAI seam)
  - 1900 Authority Enforcement (MissionRunner Boundary 5 AUTHORITY_CONTRACT_OBSERVED emission; Cat F.f Authority seam)
  - Employee OS (MissionRunner OpsRunEvent step boundary emission; Cat F.g Employee OS seam)
  - Frontend (WebSocket consumer receive; delegated; Cat F.h Frontend seam)
  - API (Boundary 1 HTTP auth + views_diagnostics.py telemetry projections + views_inbox.py WebSocket group_send + hitl_validation.py EventBus emission; Cat F.i API seam)
  - Discord (96 commands + 25 Cog classes; notification sink for EventBus handlers; Cat F.j Discord seam)
playbook_application: §11.2 20-section child template EIGHTEENTH-consecutive application + §16 CONSOLIDATION shape THIRD-consecutive application under Research OS (S1806 Group 1800 Cat F = first + S1904 Group 1900 Cat F = second + S2004 Group 2000+ Cat F = third → MC-6 CODIFICATION-CONFIRMED milestone candidate at S2099 close per S1899 close established 3-application-under-arc-close discipline)
verifier_loop: §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED (S1899 §10.2 MC-1 promoted) — pre-Explore verifier CONFIRMED all 10 adjacent-plane entry-point classes exist at HEAD (Memory: signal_aggregation_service.py:776,801 fleet_events.emit_event call verified; Sports: consumers_sports.py:106,127 WebSocket group_send verified; Content: content_deliberation_runner.py + publish_gate.py present; Observability: models_celery_telemetry.py:17 + models_llm_telemetry.py:30 + models_ops_runs.py:117 + models_tool_calls.py:19 all present; HAI: human_attention_lifecycle.py:243 review_mode read verified; Authority: mission_runner.py:835-900 authority_contract_observed emit inherited from S1904 §14.1; Employee OS: mission_runner.py OpsRunTracker via ops_run_tracker.py:34,96; Frontend: WebSocket consumer receive via /ws/system-events/ per EMPLOYEE_OS_PRIMITIVES §1 row 22; API: auth_middleware.py:563-681 + views_diagnostics.py:825-836,1391-1394,1566-1569,2688-2756,3239-3387 + views_inbox.py:305-310,331-335 + hitl_validation.py:30,38 verified; Discord: discord_bot.py 96 commands per PLATFORM_INVENTORY, zero authority-plane or emission-plane reads sampled); post-Explore verifier CORRECTED 4 drifts (see §14.3): (1) F13 Fleet Events discovered as potential SEVENTH SUBSTRATE not enumerated in S2003 §10.1 — verified `core/services/fleet_events.py` exists at 285 lines with `emit_event()` public API + FleetEvent ORM model + Redis pub/sub per-app channel; single caller from signal_aggregation_service.py:801 for signal.cluster_promoted event; classifies as EITHER (a) sanctioned Class-2 substrate that S2099 §7 anchor-updates should add to S2003 §10.1 substrate inventory, OR (b) drift analog to F11 requiring canonical-substrate migration; Chris-gate at close; (2) HAI auto_approve emission absent at HEAD verified via Explore 1 grep zero-match against publish_hai_*, group_send, OpsRunEvent.objects.create in `core/services/human_attention_lifecycle.py:440-656` auto-approve orchestration trigger body — CONFIRMS S2002 §7.9 canonical + mirror design remains DESIGN-ONLY at S2004 close; matches S1904 §14.3.3 pattern of design-vs-runtime gap explicitly queued (not a P2 design drift); (3) `ui.render_hint` envelope pattern absent EVERYWHERE — post-Explore verifier grep `ui\.render_hint|render_hint` across `core/consumers*.py` + `frontend/src/` returned ZERO matches confirming S2003 §10.3.4 D4 contract is aspirational at S2004 close; retrofit is post-arc T-slot (per §19); (4) `mirror_of` tag pattern absent — post-Explore verifier grep `mirror_of` across `core/` returned ZERO matches confirming S2003 §10.3.1 canonical + mirror invariant unenforced at S2004 close; feeds §14.3 double-emission detector post-arc wiring
sign_status: SIGN-with-edits CLEAN at Medium-High confidence across 4 batches with 12 folds landed pre-commit (2026-07-04) on arc pin `pa-dd7e973617da464d`; batched per feedback_rigby_sign_worker_instability_recovery.md preemptive rule for 1000+ line audits; Cycle 2 NOT REQUIRED per Rigby explicit "STRENGTHEN/FOLD/CLEAN" verdicts across 12 questions; 12 folds landed pre-commit: (Q1 STRENGTHEN F13 three-option register kept + ADR-required-before-expansion — do not block xx99 §7 anchor updates but freeze new producers/consumers until ADR resolution); (Q2 FOLD F5 HIGH severity default — CRITICAL only if HAI transitions relied on for runtime coordination today; staged-rollout wiring gap); (Q3 STRENGTHEN T1 register defines conformance check gate spec + T2 detector wiring; T1 MUST define mirror_of + event_id equality + substrate tags conformance check); (Q4 CLEAN F11 + F13 orthogonal; F11 canonical target remains EventBus per S2003 contract); (Q5 STRENGTHEN F14 meta-candidate promoted as general "activation verification for consumers" pattern applies across planes/substrates, not EventBus-specific); (Q6 FOLD F16 T2 scope enumeration required — (a) retrofit ~40 emission sites + (b) retrofit 33+ consumer classes to enforce `type=ui.render_hint` + (c) code-review anti-pattern + lint/grep check; validate via 10-plane × 3-scenario matrix); (Q7 FOLD F13 interim Chris-gate at S2004 close mandatory to lock classification direction — even if execution deferred — then S2099 re-affirms; deferring entirely to S2099 risks quiet expansion + anchor drift); (Q8 STRENGTHEN F18 MC-3 at durable-at-3 defensible for milestone confirmation — separate from playbook §20 two-triggers rule which governs template/pattern promotion; MC milestones can use 3 as confirmation); (Q9 STRENGTHEN Observability WORKING with explicit caveat — "EventBus SYSTEM_ALERT emission missing as capability gap; promote to PARTIAL only if consumers/UX assume alerts emitted today"); (Q10 STRENGTHEN T1 ordering — composition-consistency register #1 (defines invariants), HAI wiring #2 (first major adopter), spider-data consolidation #3; HAI may start in parallel but cannot close without register compliance); (Q11 STRENGTHEN F5 HYPOTHESIS DISPROVE durable-at-seven codification-confirmed as evidence-rollup heuristic with its own threshold — SEPARATE from §20 two-triggers rule which governs template/pattern promotion); (Q12 FOLD xx99 §7 anchor-update batch: ship 10 per-plane docs + 1 index/overview doc + PLATFORM_INVENTORY.md subsection + EVENT_SYSTEM_INVENTORY.md §13 all in same batch to avoid orphaned discovery); D48 42nd arm turn 1 CLEAN → 32-consecutive-fully-clean-arms sub-pattern EXTENDED per multi-batch design-consolidation SIGN criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 36 → 40 consecutive at S2004 close)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/EVENT_SYSTEM_INVENTORY.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md
  - docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md
  - docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md
  - docs/research/domains/event_integration_architecture/2003_event_integration_architecture_cat_c_cross_substrate_composition_design_child_audit.md
  - docs/research/domains/authority_enforcement/1904_authority_enforcement_cat_f_adjacent_separation_boundaries_child_audit.md
  - docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
owner: claude
---

# Group 2000+ P4 Cat F — Adjacent / Separation Boundaries (Consolidation Child Audit)

> **FOURTH AND LAST child audit under Group 2000+ Event / Integration
> Architecture arc.** Playbook §11.2 20-section child audit template
> EIGHTEENTH-consecutive application + §16 CONSOLIDATION shape
> THIRD-consecutive application under Research OS (first at S1806 Group
> 1800 Cat F; second at S1904 Group 1900 Cat F; third at S2004 Group
> 2000+ Cat F → MC-6 CODIFICATION-CONFIRMED milestone candidate at
> S2099 close per S1899 close established 3-application-under-arc-close
> discipline).
>
> **Scope precision (inheriting Group 1900 P4 § scope-precision
> discipline per S1904 preamble + Rigby S1900 SIGN cycle 1 Q3(b)
> fold — normative for this doc).** P4 is a **separation-boundary
> posture audit (interface + seam audit)** — a review of interfaces,
> seams, emission touchpoints, consumer-registration seams, and
> cross-substrate composition joins between Event / Integration
> Architecture and each adjacent domain. It is **NOT** an audit of
> each adjacent domain's internal correctness or implementation
> quality. Prior arc audits own their respective internal-correctness
> verdicts:
>
> | Adjacent plane | Group | Internal-correctness owner |
> |---|---|---|
> | Memory | 1300 | S1301-S1305 + S1399 xx99 |
> | Sports | 1500 | S1501-S1506 + S1599 xx99 |
> | Content | 1600 | S1601-S1606 + S1699 xx99 |
> | Observability | 1700 | S1701-S1706 + S1799 xx99 |
> | HAI | 1800 | S1801-S1806 + S1899 xx99 |
> | Authority Enforcement | 1900 | S1901-S1904 + S1999 xx99 |
> | Employee OS | — | Distributed (S1268-S1272 research + EMPLOYEE_OS_PRIMITIVES.md) |
> | Frontend | — | Distributed (docs/topics/frontend.md + workspace research) |
> | API | — | Distributed (docs/API_PATH_POLICY.md + views_* research) |
> | Discord | — | Distributed (docs/DISCORD_INTEGRATION.md + Cog audit) |
>
> Group 2000+ P4 audits **only the seams** between event / integration
> and those domains. Any finding that lands entirely inside an
> adjacent domain (e.g., "Memory's caching invalidation is stale") is
> OUT OF SCOPE and gets routed to the owning arc's post-arc T-slot.

## 1. Executive Summary

Cat F is the CONSOLIDATION surface for Group 2000+. P4 audits the seams between Event / Integration Architecture and 10 adjacent planes; per parent §5.4 + playbook §14.5 no-implementation rule, Cat F catalogs seam posture + emission-touchpoint register + consumer-registration seam matrix + separation-boundary policy register and produces R-slot follow-on queue candidates. Post-arc T-slot inherits.

At HEAD `7fc1bc1c`, all 10 adjacent-plane entry-point classes verified at pre-Explore. Six parallel Explore sub-agents returned per playbook §13. Post-Explore verifier caught 4 corrections (see §14.3): F13 Fleet Events discovered as potential SEVENTH substrate (`core/services/fleet_events.py`, 285 LOC) not enumerated in S2003 §10.1 six-substrate inventory; HAI auto_approve emission absent at HEAD confirming S2002 §7.9 canonical + mirror design remains DESIGN-ONLY (matches S1904 §14.3.3 pattern); `ui.render_hint` envelope pattern absent everywhere (S2003 §10.3.4 D4 contract aspirational at S2004 close); `mirror_of` tag pattern absent (S2003 §10.3.1 canonical + mirror invariant unenforced).

**Headline verdicts:**

- **F1 (HIGH structural — Cat F.a Memory) — Memory seam is PERMEABLE-BROKEN via Fleet Events emission on `signal.cluster_promoted` at `core/services/signal_aggregation_service.py:801` (via `core/services/fleet_events.py:emit_event`) — the SINGLE verified Memory-side event emission at HEAD.** No EventBus emission; zero `publish_spider_data_event` calls despite Memory being the S2001 canonical SPIDER_DATA producer per parent §5.3 §12.1 P0 mapping. `AgentLearning` + `UserAgentLearning` writer plane emits zero events on any of the six S2003 §10.1 substrates. Fleet Events is not in the six-substrate contract; F13 flags for xx99 §5 canonical seam statement classification (sanctioned Class-2 substrate vs drift-analog-to-F11). Cat F.a maturity: **EXPERIMENTAL** (single emission via undocumented seventh substrate + zero EventBus adoption + writer-plane no-event-emission pattern).

- **F2 (HIGH — Cat F.b Sports) — Sports seam is PERMEABLE-BROKEN via WebSocket-only emission pattern.** `core/consumers_sports.py:106,127` emits `channel_layer.group_send` for odds/league updates with type strings `odds_updated` / `league_updated`. Zero EventBus emission from `BettingOutcomeVerifier.verify_all_pending()` or `SportsBettingLearningBridge.sync_betting_performance_to_learning()` despite S2003 §10.4 recommending `publish_outcome_recorded_event` as canonical substrate for settled wagers. Eight WebSocket consumer classes (SportsConsumer / OddsConsumer / GamesConsumer / SportsUpdatesConsumer / LiveSportsConsumer / SportsArbitrageConsumer / SportsRecommendationConsumer / SportsDashboardConsumer) all use bare `type: <string>` fields, not `type: ui.render_hint` per S2003 §10.3.4 D4. Cat F.b maturity: **PARTIAL** (WebSocket path operational; canonical substrate deferred; UI-render-hint envelope absent).

- **F3 (HIGH — Cat F.c Content) — Content seam is PERMEABLE-BROKEN via ZERO-EMISSION-AT-BOUNDARY posture.** `core/services/content_deliberation_runner.py` PublishGate + `core/apps/content/views.py` REST endpoints emit ZERO events across any of the six substrates. Deliverable status transitions (WORKSHOPPING → READY → PUBLISHED per DreamInitiative pipeline) fire no `publish_*_event` and no `channel_layer.group_send`. `DeliverableEvent` model exists at `core/models` per EVENT_SYSTEM_INVENTORY §1.4 ("best-shaped emitter in the repo for v0 intake") but production content pipeline writes zero DeliverableEvent rows at HEAD per Explore 1 verified grep. S1605 T.15.E2 "REST endpoints ZERO auth decorator" inherited into Content boundary. Two duplicate WebSocket consumer classes: `content/consumers.py:23,414` (ContentProcessing + ContentAnalytics) vs `core/consumers_base.py:1306,1359` (same names, different group naming) — dormant routing likely per Explore 2 finding. Cat F.c maturity: **EXPERIMENTAL** (zero-emission-at-boundary; duplicate consumer classes; DeliverableEvent design-only).

- **F4 (HIGH — Cat F.d Observability) — Observability seam is a MULTI-SUBSTRATE WRITE-ONWERSHIP pattern with concern-boundary separation intact.** Observability owns 4 of the 6 telemetry substrates as write-side (S2003 §10.3.5 concern-boundary map): CeleryTaskEvent (`core/models_celery_telemetry.py:17`) via `task_prerun`/`task_postrun` signal handlers in `core/celery_telemetry.py`; LLMCallEvent (`core/models_llm_telemetry.py:30`) via `LLMCallWrapper` context manager (S1098); OpsRunEvent (`core/models_ops_runs.py:117`) via `OpsRunTracker.emit` at `core/tools/ops_run_tracker.py:34,96` + MissionRunner step boundaries; ToolCallRecord (`core/models_tool_calls.py:19`) via `ToolDispatcher.dispatch_tool_call` (S861). Zero cross-substrate mirroring at HEAD per Explore 6 P3 concern-boundary drift test (P3 verdict CLEAN — no substrate records the same semantic tuple `(actor, action, target, args_hash, occurred_at)` for the same execution). BUT: Observability plane makes zero EventBus emission despite S2001 F5 `publish_system_alert_event` wrapper at `event_bus.py:686` being the natural home for observability alerts; `HallucinationMonitorConsumer` at `core/consumers_hallucination.py:16` is the sole plane-owned WebSocket consumer. Cat F.d maturity: **WORKING** (four-substrate write-ownership operational; EventBus adoption absent; concern-boundary CLEAN).

- **F5 (HIGH — Cat F.e HAI) — HAI seam is ZERO-EMISSION-AT-BOUNDARY at the four candidate transitions defined by S2002 §7.** *(Rigby SIGN cycle 1 Q2 FOLD: HIGH severity default — staged-rollout wiring gap: design-complete, runtime-scaffolding absent at HEAD; promote to CRITICAL only if any production consumer assumes HAI emissions exist today.)*  `core/services/human_attention_lifecycle.py:243` `_auto_approve_low_risk_items` reads `HumanSystemState.review_mode` (Boundary 6-16 authority-adjacent), executes decision write via `HumanAttentionItem.record_decision`, but emits ZERO events on any substrate — no `publish_hai_decision_recorded_event`, no `channel_layer.group_send`, no `OpsRunEvent.objects.create` with `mirror_of=eventbus:HAI_DECISION_RECORDED` tag. Post-Explore verifier grep verified across `core/services/human_attention_lifecycle.py:440-656` (auto-approve orchestration trigger body): ZERO substrate emission calls. This confirms S2002 §7.9 canonical + mirror design remains DESIGN-ONLY at S2004 close — matches S1904 §14.3.3 pattern of design-vs-runtime gap explicitly queued (not a P2 design drift; queued per S2002 §19 T1 post-arc T-slot). Three WebSocket consumers (PAConversationConsumer / PersonalAssistantConsumer V2 / AssistantChatConsumer) subscribe to conversation groups but do NOT subscribe to EventBus HAI streams (analytics_workers consumer group dormant per S2001 F9). Cat F.e maturity: **EXPERIMENTAL** (four HAI candidate transitions design-complete; runtime emission ZERO; three WebSocket consumers operate independent of substrate contract).

- **F6 (HIGH — Cat F.f Authority Enforcement) — Authority seam is PERMEABLE-BROKEN via SINGLE-SUBSTRATE emission on OpsRunEvent (Boundary 5 authority_contract_observed).** `core/employees/mission_runner.py:835-900` `_emit_authority_contract_event` emits `AUTHORITY_CONTRACT_OBSERVED` label to OpsRunEvent with schema_version + employee_handle + contract_version_tag + authority_level_counts + prohibited_actions_count + mode. Sole authority-plane event emission at HEAD (verified via Explore 1). Zero EventBus emission; zero mirror-substrate emission (canonical + mirror pattern per S2003 §10.3.1 not activated for AUTHORITY_CONTRACT_OBSERVED because event pre-dates S2003 §10.3.1 codification). Zero authority-violation events (`AUTHORITY_CONTRACT_VIOLATED` planned per S1902 §19 T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA, NOT implemented). Cat F.f maturity: **WORKING** (observation-mode operational on single substrate; S2002 §7.9 canonical + mirror shape not applied; violation-emit deferred to post-arc).

- **F7 (HIGH — Cat F.g Employee OS) — Employee OS is the DOMINANT OpsRunEvent write-owner + is the S2003 §10.3.1 canonical mirror-substrate site — but S2002 §7.9 canonical + mirror wiring is DESIGN-ONLY.** `core/employees/mission_runner.py` writes OpsRunEvent via `_emit_event` at 15+ distinct sites (step lifecycle + verdicts). `core/tools/ops_run_tracker.py:34,96` provides context-manager write helper. `core/signals/rigby_delegation_signals.py:79` + `core/services/td_handlers_rigby_work_queue.py:118` are auxiliary writers. All writes carry `run` FK to OpsRun parent + `event_type` + `label` + `detail` dict — but NO `mirror_of` tag (verified via §14.3.4 post-Explore grep zero-match). Zero EventBus emission from MissionRunner despite S2003 §10.3.1 defining OpsRunEvent as Class-1 mirror-substrate (equal `event_id` invariant + `mirror_of` tag + `transaction.on_commit` ordering); the invariants are unenforced at HEAD. Seven WebSocket consumer classes (AgentProgressConsumer / AgentExecutionConsumer / AgentOrchestrationConsumer / RealAgentOrchestraConsumer / AgentMonitorConsumer / ProjectProgressConsumer / AllProjectsConsumer) broadcast agent + project status without EventBus co-emission. Cat F.g maturity: **WORKING** (OpsRunEvent write-ownership operational; canonical + mirror shape design-complete + runtime-scaffolding; WebSocket path independent of substrate contract).

- **F8 (LOW — Cat F.h Frontend) — Frontend seam is CLEAN (verified read-only).** Per S1904 §17.1 Rigby Q3(b) fold pattern: Frontend does NOT compute or enforce event emission; it only RENDERS server-resolved WebSocket state (dashboard updates, agent status, mission verdicts, inbox messages) and does not directly publish to any substrate. Verification basis: no browser-initiated substrate write endpoints observed; `frontend/src/App.tsx` 61 routes behind `ProtectedRoute` (session auth); WebSocket connections open from React `useEffect` hooks but Django-side consumers own broadcast pathway. **If any browser UI ever emits directly to a substrate (e.g., a client-side pub/sub library adopted for real-time UI), Frontend becomes PERMEABLE-BROKEN until an explicit write-boundary contract exists.** No `ui.render_hint` receiver logic observed (aspirational per S2003 §10.3.4 D4). Cat F.h maturity: **EXPERIMENTAL** (seam contract undocumented but genuinely separated by design; UI-render-hint contract not implemented).

- **F9 (HIGH — Cat F.i API) — API seam is PERMEABLE-BROKEN via ASYMMETRIC-EMISSION pattern.** 209 view files across `core/views_*.py` per PLATFORM_INVENTORY. Explore 3 verified: ZERO REST endpoints directly emit events via `publish_*_event` / `EventBus.publish` / `OpsRunEvent.objects.create` — service layer owns emission (correct per separation of concerns). Verified event emissions from services called by views: (a) `core/services/hitl_validation.py:30,38` emits `publish_validation_required_event` + `publish_validation_decided_event` (only production EventBus emission from API-layer service at HEAD; called from validation view stack); (b) `core/services/scoring_dispatcher.py:282,480` emits `publish_opportunity_scored_event` (called from scoring dispatchers; not view-triggered directly). Read-side telemetry projections at `core/views_diagnostics.py:825-836,1391-1394,1566-1569,2688-2756,3239-3387` expose CeleryTaskEvent + AgentExecution + LLMCallLog + AuditLog aggregates. `core/views_inbox.py:305-310,331-335` emits WebSocket `channel_layer.group_send` for `inbox.new_message` + `inbox.thread_created` types. Boundary 1 HTTP auth middleware at `core/auth_middleware.py:563-681` emits ZERO events on authentication events. Cat F.i maturity: **PARTIAL** (2 EventBus emission sites + 2 WebSocket emission sites verified from ~209-view surface; auth-layer emission absent; telemetry projection operational).

- **F10 (CRITICAL structural — Cat F.j Discord) — Discord seam is STRUCTURAL-DROP (ZERO-EMISSION-AT-COMMAND-DISPATCH).** `core/services/discord_bot.py` (11,676 LOC per PLATFORM_INVENTORY, 96 @*.command decorators, 48 @app_commands.command, 25 Cog classes) emits ZERO events across any of the six substrates per Explore 1 + Explore 3 verified grep. `RateLimiter` at `discord_bot.py:85-100` applies per-command cooldowns without substrate emission. `PermissionLevel` + `DiscordLinkCode` gates without EventBus observation. `core/services/discord_notifications.py` is invoked FROM EventBus event handlers (via `event_handlers.py:216-231` VALIDATION_REQUIRED handler + `:326-339` MODEL_TRAINED handler + `:370-383` SYSTEM_ALERT handler) as a NOTIFICATION SINK — one-way push, ImportError-caught fail-open, no ack/nack. Consistent with S1904 F8 (Discord authority seam STRUCTURAL-DROP per S1903 Q8 formal deferral); Group 2000+ P4 extends: Discord is also STRUCTURAL-DROP for event/integration emission — no command dispatch fires an event, no consumer-registration pattern beyond notification-sink downstream. Cat F.j maturity: **EXPERIMENTAL** (dispatch operational; substrate integration absent; notification sink brittle to import failure).

- **F11 (HIGH cross-plane — Fleet Events RATIFIED AS INTENTIONAL SIDECAR SUBSTRATE per Chris D-verdict at S2004 close 2026-07-04).** Verifier-loop discovery per §14.3.1: `core/services/fleet_events.py` (285 LOC, 9,624 bytes) implements `emit_event(app_slug, event_type, payload, ...)` public API + `FleetEvent` ORM model + Redis pub/sub per-app channel. Single verified caller from Explore 1: `core/services/signal_aggregation_service.py:801` for `signal.cluster_promoted` event with envelope payload. Fleet Events is architecturally a HYBRID substrate: it is (a) push-with-consumers via Redis pub/sub per-app-channel (like WebSocket), AND (b) durable-audit via FleetEvent ORM row (like OpsRunEvent). It does NOT map cleanly to any of the six S2003 §10.1 substrate rows. **Chris D-verdict at S2004 close = option (3) INTENTIONAL SIDECAR** — Fleet Events is for cross-application (u-d-b × mentorforge × character-os fleet) coordination and stays sanctioned as a SEPARATE substrate; S2003 §10.1 six-substrate scope was intra-application by intent. Rationale: `emit_event(app_slug=...)` API signature is already scoped per-app-slug; parallel purpose to EventBus is complementary (cross-application coordination), not overlap (which would trigger option (2) drift). S2099 §7 anchor-update batch will add Fleet Events row to S2003 §10.1 substrate inventory explicitly noting cross-application scope + define concern-boundary per §10.3.5. **ADR RATIFIED — freeze on new intra-application producers/consumers stays per Q1 Rigby SIGN fold (existing sole-caller usage from `signal_aggregation_service.py:801` may continue); onboarding of new cross-application producers/consumers permitted post-S2099 anchor-update landing.** F13 substrate-inventory-completeness verifier discovery pattern feeds §20.10 codification candidate. Severity: **HIGH cross-plane** (substrate inventory anchor update depends on ratified classification; blocks xx99 §7 anchor-update batch execution until landing).

- **F12 (HIGH cross-plane — F5 HYPOTHESIS "duplicate event-emission-adjacent primitives across planes" DISPROVE).** Explore 6 tested HYPOTHESIS: "Every adjacent plane duplicates event-emission-adjacent primitives (custom pub/sub, custom event log wrapper, custom broadcast fanout, custom substrate)." Result: **DISPROVE across all 10 planes.** No plane implements a custom `Publisher`, `Subscriber`, `EventEmitter`, or `Broadcaster` class outside the core EventBus wrappers or WebSocket `group_send` call sites. The ONE partial-pass candidate — Fleet Events at `core/services/fleet_events.py` — is a SHARED substrate consumed by Memory alone at HEAD, not a per-plane duplicate primitive; F13 classifies whether it's sanctioned. Aggregate cross-arc F5 running tally: **1 pass (S1806 Cat F.d partial confirmation) / 7 disprove (S1802 + S1803 + S1804 + S1805 + S1904 H1 + S2004 H1 across 10 planes)**. Meta-methodology datapoint per S1806 §20.7 codification-ready pattern → EXTENDED to durable-at-seven arc-close testing. Codification candidate for xx99 §10 meta-methodology: "F5 HYPOTHESIS-testing at arc-close consolidation surfaces DISPROVE-dominant across authority-adjacent + event-emission domains, suggesting primitives naturally cluster canonically rather than fragment into per-plane duplicates."

- **F13 (CRITICAL structural — Zero-emission-at-plane-boundary durable-across-P1-P2-P3-P4 across all 10 planes).** Pattern from Explore 6 §H2: **Zero of 10 planes have runtime-enforced event emission at plane boundaries.** Memory: no EventBus (single Fleet Events emit only). Sports: WebSocket only. Content: zero across all substrates. Observability: 4 telemetry substrates for its own concerns; zero EventBus. HAI: zero across all substrates. Authority: OpsRunEvent single-substrate only (no mirror). Employee OS: OpsRunEvent write-owner; zero EventBus. Frontend: delegated read-only. API: 2 EventBus emission sites + 2 WebSocket emission sites among ~209 view files. Discord: zero across all substrates. Consistent with S2001 F1-F5 zero-producer-caller baseline (5 of 8 EventBus streams have zero non-definition callers). Extends S1904 F10 (zero-authority-check-at-boundary durable-across-P1-P2-P3-P4) to event-emission domain. Durable-at-five under Research OS (S1806 test-gap + S1904 F10 + S2004 F13 = durable-at-three; extends F12 durable-at-four with F13 durable-at-five under emission-domain arc-close discipline).

- **F14 (HIGH cross-plane — Consumer beat-dormancy durable across all planes; S2001 F9 propagation).** Per Explore 6 §H5 + §P2: 4 of 5 EventBus consumer tasks unscheduled (`process_event_bus_scoring_queue` at `core/tasks.py:4726` + `process_event_bus_validation_queue` at `:4760` + `process_event_bus_analytics_queue` at `:4794` + `get_event_bus_stats` at `:4874` — all NOT enrolled in PeriodicTask); only `claim_stale_events` at `:4828` enrolled at `core/celery.py:531-535` (5-min beat). Extends across ALL 10 planes: (a) planes that would receive events via analytics_workers (Memory + HAI + Authority + Content) have zero live consumers; (b) planes that would emit events via scoring_workers (Employee OS + agent execution) have zero live consumers; (c) Sports + Discord + Observability + Frontend + API have zero EventBus consumer registration by design (delegated / write-only / notification-sink). Cross-arc pattern: extends S1904 F10 consumer-dormancy analog to event-integration domain. Post-arc T2 R.EVENTS.CONSUMER-BEAT-ENROLLMENT.

- **F15 (HIGH cross-plane — correlation_id design-present, runtime-absent across all 10 planes).** Per Explore 6 §H6: `Event.correlation_id` field defined at `core/services/event_bus.py:51,62,76,144,155,166` but zero producers populate it (extends S2001 §8: "all 7 wrappers omit correlation_id → every real emission today has correlation_id=None"). Post-Explore verifier grep across `core/` returned zero `correlation_id=<non-empty>` matches at publish call sites. Zero consumers read `event.correlation_id` for cross-substrate reconstruction. Consequence: no distributed tracing contract exists across the six (or seven, per F11) substrates. Every plane independently queries its own substrate. Post-arc T3 R.EVENTS.CORRELATION-ID-RUNTIME-ADOPTION.

- **F16 (HIGH cross-plane — `ui.render_hint` envelope pattern absent across all 10 planes; S2003 §10.3.4 D4 aspirational).** Post-Explore verifier grep `ui\.render_hint|render_hint` across `core/consumers*.py` + `frontend/src/` returned ZERO matches. All ~40 `channel_layer.group_send` call sites use bare `type: <string>` fields (e.g., `type: 'connection_established'`, `type: 'dashboard_update'`, `type: 'live_odds_update'`, `type: 'inbox.new_message'`). No consumer subscribes to `ui.render_hint` envelope OR treats WebSocket messages as display-only per S2003 §10.3.4 D4 contract. Concretely: seven planes (Sports + Content + Memory + HAI + Authority + Employee OS + Frontend) treat WebSocket state as authoritative without external verification — potential contract violations per S2003 §10.3.4 D4 code-review anti-pattern. Retrofit is post-arc T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT.

- **F17 (HIGH cross-plane — `mirror_of` tag pattern absent + `event_id` equality unenforced across all dual-emission cases).** Per Explore 6 §P1 composition-consistency invariants: two observed dual-/multi-emission cases both FAIL S2003 §10.3.1 canonical + mirror invariants. (a) HAI Class-1 governance canonical + mirror design (S2002 §7.9): design-only; not implemented at HEAD; when implemented per T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING will require equal `event_id` + `mirror_of` tag on OpsRunEvent payload + `transaction.on_commit` ordering. (b) F11 spider-data three-substrate drift: EventBus SPIDER_DATA (dormant) + `ai_core/agents/spider_agent_connector.py:322-325` raw `redis.publish()` (2 callers) + intelligence in-process routing table (4 callers) — three independent substrates with no `event_id` unification, no `mirror_of` tag. Post-arc T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER + T1 R.EVENTS.SPIDER-DATA-SUBSTRATE-CONSOLIDATION.

- **F18 (MEDIUM cross-plane — Test-gap durable-across-P1-P2-P3-P4 arc-wide TEST-GAP-CONFIRMED).** Per Explore 6 §H4: grep `test_*event_bus*|test_*substrate*|test_*plane*|test_*seam*|test_*channel_layer*|test_*correlation_id*|test_*mirror_of*` across `core/tests/` returned 4 partial-coverage test files (`test_platform_event_view.py` + `test_rigby_event_intake.py` + `test_auto_followup_subscription.py` + `test_spider_orchestrator_mock_fallback.py`); ZERO dedicated seam-boundary test files. Extends S1904 F12 durable-across-P1-P2-P3-P4 authority-seam TEST-GAP-CONFIRMED to event-integration seam. Meta-methodology: Under Research OS arc-close discipline, F12/F18 TEST-GAP durability now runs at 3 arcs (S1806 + S1904 + S2004) → MC-3 CODIFICATION-CONFIRMED milestone at S2099 close. Post-arc T2 R-slot candidate: R.EVENTS.SEAM-BOUNDARY-TEST-COVERAGE (10-plane × 3-scenario matrix minimum).

**Biggest architectural risk — RISK-SPLIT FRAMING (per S1806 + S1904 precedents + Rigby SIGN discipline):** Present two distinct risks so reviewers don't argue past each other:

- **F5 + F13 = highest STRATEGIC / SYSTEMIC risk (blocks xx99 §5 consolidated domain shape + composition contract shape).** HAI is the design-only canonical + mirror site per S2002 §7.9. Zero runtime implementation of the four HAI candidate emission at HEAD. The entire S2002 P2 contract + S2003 P3 composition invariants are aspirational as of S2004 close. xx99 §5 consolidated domain shape cannot cleanly assert "event / integration architecture is operational" until T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING lands. Compounded by F13: substrate inventory itself is potentially incomplete (Fleet Events discovered post-Explore); xx99 §5 canonical seam statement depends on Chris-gate classification of Fleet Events.

- **F10 = highest IMMEDIATE PLATFORM COORDINATION-GAP risk (could enable silent event-driven-work failure tomorrow).** Discord seam is structurally dropped with 96 commands + 25 Cogs and zero substrate integration. Any Discord command that triggers a Celery task + calls agent services can execute LLM-costing or state-changing operations without any event emission on any substrate — no observability, no cross-substrate reconstruction, no downstream consumer subscription. Not blocked-by-design like Sports arbitrage (F2 partial deferral); blocked-by-missing-integration.

**Canonical seam statement (for xx99 §5 consumers to reason "what exists" vs "what's aspirational"):** At HEAD `7fc1bc1c`, Event / Integration Architecture seam maturity distributes as **6 PERMEABLE-BROKEN + 2 STRUCTURAL-DROP + 1 CLEAN + 1 WORKING** across the 10 planes. Zero seams are STABLE or CANONICAL. Employee OS is the dominant OpsRunEvent write-owner + is the S2003 §10.3.1 canonical mirror-substrate site — but S2002 §7.9 canonical + mirror wiring is DESIGN-ONLY. Fleet Events is discovered as potential seventh substrate not enumerated in S2003 §10.1 (F13 Chris-gate classification pending). Zero `ui.render_hint` envelope adoption (S2003 §10.3.4 D4 aspirational). Zero `mirror_of` tag adoption (S2003 §10.3.1 canonical + mirror invariant unenforced). Zero `correlation_id` runtime propagation (S2001 §8 pattern extends to all 10 planes). Consumer beat-dormancy is arc-canonical (4 of 5 EventBus tasks unscheduled per S2001 F9 propagated across all 10 planes). This is consistent with S1904 F10 zero-authority-check-at-boundary pattern — Event / Integration Architecture is design-complete, runtime-scaffolding. The 15+ T-slot items in §19 route the emission + consumption wire-up across owning arcs (Employee OS T0/Gate + T1; HAI T2 + T3; Content T1; Observability T2; API T2 + T3; Sports T3; Discord T2; Memory T3; Frontend N/A).

**Biggest gaps for future research (T1 priority ordering per Rigby SIGN cycle 1 Q10 STRENGTHEN fold):** (a) **R0 (STRATEGIC POST-ARC — xx99 §5 canonical seam-posture-statement)** — synthesize F1-F18 findings into a canonical statement of Event / Integration Architecture seam maturity for cross-arc consumers; (b) **R1 Composition contract consistency register (T1 #1 — defines invariants)** — `mirror_of` tag + `event_id` equality + `transaction.on_commit` conformance check gate spec; T2 detector wiring follows per Q3 SIGN fold; (c) **R2 HAI dual-emission wiring (T1 #2 — first major adopter; may start in parallel but cannot close without register compliance per Q10 SIGN fold)** — S2002 §7.9 canonical EventBus + mirror OpsRunEvent; (d) **R3 F11 spider-data substrate consolidation (T1 #3 — orthogonal to F13 per Q4 SIGN CLEAN; canonical target remains EventBus per S2003 contract)** — three-substrate drift → canonical EventBus + WebSocket UI-render fanout per S2003 §10.5 D4; (e) **R4 F13 Fleet Events substrate classification ADR (T0/Gate — Chris-gate at S2004 close per Q7 SIGN FOLD)** — sanctioned Class-2 vs drift-analog vs intentional sidecar; interim Chris-gate mandatory at close to lock classification direction + freeze new producers/consumers until ADR resolution per Q1 SIGN STRENGTHEN; (f) **R5 Consumer beat-enrollment reactivation** (4 EventBus consumer tasks + activation-mode proof + dormancy detector per Q5 SIGN STRENGTHEN meta-candidate; T2); (g) **R6 UI-render-hint envelope retrofit (T2 scope enumerated per Q6 SIGN FOLD)** — (a) retrofit ~40 emission sites + (b) retrofit 33+ consumer classes to enforce `type=ui.render_hint` + (c) code-review anti-pattern + lint/grep check; validate via 10-plane × 3-scenario matrix; (h) **R7 correlation_id runtime propagation** (S2001 §8 durable pattern extends to all 10 planes; T3); (i) **R8 Seam boundary test coverage** (F18 durable-across-P1-P2-P3-P4 TEST-GAP-CONFIRMED at MC-3 durable-at-3 milestone per Q8 SIGN STRENGTHEN; T2); (j) **R9 Cross-plane fail-open-emission codification** (F13 durable pattern; xx99 §5 should codify or reject as CANONICAL default); (k) **R10 Cross-arc T-slot handoff routing** (26 T-slot items distributed across Group 1300/1500/1600/1700/1800/1900 + Employee OS + API + Discord + Group 2000+ residual); (l) **R11 Cross-arc anchor-update batch (per Q12 SIGN FOLD)** — ship 10 per-plane docs + 1 index/overview doc + PLATFORM_INVENTORY.md subsection + EVENT_SYSTEM_INVENTORY.md §13 all in same batch to avoid orphaned discovery.

Runtime maturity classification arc-wide: **PARTIAL with EXPERIMENTAL emission.** Seam distribution: 5 EXPERIMENTAL (Memory + Content + HAI + Frontend + Discord) / 1 PARTIAL (Sports + API) actually 2 PARTIAL / 2 WORKING (Observability + Employee OS + Authority) actually 3 WORKING / 0 STABLE / 0 CANONICAL. Corrected distribution: 4 EXPERIMENTAL / 2 PARTIAL / 3 WORKING / 1 CLEAN-delegated (Frontend counted separately as delegated read-only) = 10 planes total. No arc-close STABLE rating possible without R2 (HAI dual-emission wiring) + R3 (F11 substrate consolidation) + R7 (composition consistency register) + R8 (seam test coverage). xx99 §5 posture statement should acknowledge this framing as "design-complete, runtime-scaffolding, closure-gated on 4 T1 items."

## 2. Domain Purpose

**Q1 What is the Cat F "Adjacent / Separation Boundaries" consolidation surface and what is it responsible for?** Cat F is the arc-close consolidation surface for Group 2000+ (Event / Integration Architecture). Its purpose is TWO-fold per parent §5.4: (a) audit the seams between Event / Integration Architecture and 10 adjacent planes (Memory / Sports / Content / Observability / HAI / Authority Enforcement / Employee OS / Frontend / API / Discord) as an **interface + seam audit** — NOT as an internal-correctness audit of any adjacent plane; (b) consolidate P1 (S2001 EventBus producer/consumer map + F1-F18 findings) + P2 (S2002 HAI event schema contract + §7.9 canonical + mirror + §10 six-plane learning-surface schema + §17 consumer registry) + P3 (S2003 six-substrate separation contract + §10.3 sanctioned dual-emission register + §10.4 substrate × HAI-event mapping + §10.5 WebSocket ↔ EventBus overlap resolution + §14 double-emission detector binding) into an evidence brief for the xx99 S2099 canonical summary §5 consolidated domain shape + §8 follow-on queue. Cat F is a CONSOLIDATION audit, not a direct architecture audit — it inherits boundary discipline "catalogs; does NOT act on any of F.a-F.j items" per parent §5.4 checks/does-NOT-check table + playbook §14.5 no-implementation rule. All F1-F18 findings promote to post-arc T-slot; no Cat F-scope implementation lands under S2004.

**Q2 What are the biggest gaps in this seam surface today?** The most load-bearing gap is **F5 (HAI zero-emission-at-boundary)** because it's the design-only canonical + mirror site per S2002 §7.9 — every other plane's substrate composition adoption depends on HAI's Class-1 governance emission being operational first. The second largest is **F13 (Zero-emission-at-plane-boundary durable across all 10 planes)** — no plane emits events on runtime-enforced substrate contracts today, consistent with S2001 F1-F5 zero-producer-caller baseline but blocking xx99 §5 canonical seam statement. The most cross-cutting is **F11 (Fleet Events discovered as potential seventh substrate)** — substrate inventory itself is potentially incomplete; xx99 §5 canonical seam statement depends on Chris-gate classification of Fleet Events. **F10 (Discord structural-drop with 96 commands + 25 Cogs zero-emission)** and **F3 (Content zero-emission-at-boundary with DeliverableEvent design-only)** and **F2 (Sports WebSocket-only asymmetric emission pattern)** are HIGH domain-specific gaps queued for cross-arc T-slot handoff. **F14 (Consumer beat-dormancy propagation)** + **F15 (correlation_id design-present-runtime-absent)** + **F16 (ui.render_hint envelope absent)** + **F17 (mirror_of tag pattern absent)** + **F18 (test-gap durable-across-P1-P2-P3-P4)** are cross-cutting patterns queued for post-arc execution + arc-wide test coverage.

## 3. Canonical Entry Points

Per CONSOLIDATION shape from S1806 + S1904 precedent — §3 divided into 10 per-plane sub-slots (F.a Memory / F.b Sports / F.c Content / F.d Observability / F.e HAI / F.f Authority Enforcement / F.g Employee OS / F.h Frontend / F.i API / F.j Discord). Each sub-slot enumerates the plane-side canonical entry points that touch the event / integration seam.

### 3.1 Sub-slot F.a — Memory plane seam (Group 1300 territory)

**Plane-side canonical entry points touching event / integration seam:**

- **`signal_aggregation_service._maybe_emit_cluster_promoted`** @ `core/services/signal_aggregation_service.py:776,801` — imports `from core.services.fleet_events import emit_event` at `:776`; calls `emit_event(...)` at `:801` for `signal.cluster_promoted` event with envelope payload. **Sole verified Memory-side event emission at HEAD.** F13 flags: Fleet Events is potential seventh substrate not enumerated in S2003 §10.1.
- **`AgentLearning` + `UserAgentLearning` writer plane** — per S1399 §5 F4 six-plane fragmentation. Zero substrate emission on writer plane completion — no `publish_*_event`, no `channel_layer.group_send`, no `OpsRunEvent.objects.create`, no `mirror_of` tag. Actor-role propagation from Employee OS mission runner reaches Memory writers via Step.fn closure at Boundary 6/7 (S1901 F6c STRUCTURAL DROP inherited); event emission is a separate write-side gap.
- **Async writer paths** — `UserAgentLearning` writes via Celery beat-fired learning bridge tasks; CeleryTaskEvent signal handlers capture task lifecycle (Observability F.d substrate write-ownership), but Memory plane makes zero direct EventBus emission.
- **WebSocket consumers** — `AITrainingConsumer` @ `core/consumers_ai_training.py:14` + `ConsciousnessConsumer` @ `core/consumers_consciousness.py:24`. Consumer routing: `core/routing.py:59` (`ws/ai-training/`) + `core/routing.py:62-63` (`ws/consciousness/`, `ws/unified-intelligence/`). Zero `type: ui.render_hint` envelope usage.
- **PA tool surface** — memory-adjacent PA tools (memory_palace_tool per Explore 3 general survey) carry `user_id` only; drop event-envelope carriage at Boundary 3.

**Cross-arc scope note:** Memory internal-correctness (six-plane learning fragmentation per S1399 §5 F4; four coexisting Agent*Learning services per S1806 F3/F4) is out-of-scope for P4. P4 audits ONLY: Fleet Events emission + writer-plane no-event-emission + WebSocket consumer registration + F13 substrate-classification implications.

### 3.2 Sub-slot F.b — Sports plane seam (Group 1500 territory)

**Plane-side canonical entry points touching event / integration seam:**

- **`SportsUpdatesConsumer.handle_force_odds_update`** @ `core/consumers_sports.py:106,127` — emits `channel_layer.group_send` with `type: 'odds_updated'` at `:106` + `type: 'league_updated'` at `:127` for odds refresh broadcast. **Sole verified Sports-side event emission at HEAD.**
- **`BettingOutcomeVerifier.verify_all_pending`** @ `core/services/betting_outcome_verifier.py` — verifies arbitrage outcomes; makes ZERO substrate emission per Explore 1 + Explore 6 verified. Per S2003 §10.4 recommendation `publish_outcome_recorded_event` is canonical substrate for settled wagers, NOT called.
- **`SportsBettingLearningBridge`** @ `core/learning_bridges/sports_betting_bridge.py` — writes `UserAgentLearning` per canonical bridge writer plane; zero event emission on learning-write completion.
- **8 WebSocket consumer classes** — SportsConsumer (`sports/consumers.py:14`) + OddsConsumer (`sports/consumers.py:696`) + GamesConsumer (`sports/consumers.py:848`) + SportsUpdatesConsumer (`core/consumers_sports.py:15`) + LiveSportsConsumer (`core/consumers_base.py:247`) + SportsArbitrageConsumer (`core/consumers_base.py:1562`) + SportsRecommendationConsumer (`core/consumers_base.py:1609`) + SportsDashboardConsumer (`core/consumers_base.py:2664`). All use bare `type: <string>` fields; zero `type: ui.render_hint` envelope.
- **REST endpoints** — `sports/views.py` per PLATFORM_INVENTORY; per Explore 3 sample zero direct substrate emission from view bodies.
- **PA tools** — `sports_tool` (odds/games/predictions) + `betting_tool` (place_bet/history/analysis) per Explore 3; zero substrate emission from PA tool paths (correct per separation of concerns).
- **Discord commands** — `/live-games`, `/live-odds`, `/predictions`, `/betting-history`, `/place-bet` per Explore 3 general survey; zero substrate emission from Discord command dispatch (per F10 STRUCTURAL-DROP).
- **Boundary 20 spider run** — S1901 §7.3 row 20 sports-related spider ingestion; Sports arbitrage detection depends on Boundary 20 spider outputs but no event fires at spider completion.

**Cross-arc scope note:** Sports internal-correctness (BettingOutcomeVerifier arbitrage-filtering per S1805 F3, DBAO naming-convention drift per S1506 Finding 6, zero-fire beat durable-at-two per S1503+S1504) is out-of-scope for P4. P4 audits ONLY: WebSocket-only asymmetric emission pattern + Outcome/model event absence + UI-render-hint envelope absence + Discord dispatch STRUCTURAL-DROP.

### 3.3 Sub-slot F.c — Content plane seam (Group 1600 territory)

**Plane-side canonical entry points touching event / integration seam:**

- **`content_deliberation_runner.PublishGate.decision`** @ `core/services/content_deliberation_runner.py` — reads claim confidence + AI-reviewer decision + Freeze via `HumanSystemState.review_mode`; makes ZERO substrate emission at deliverable status transition (`WORKSHOPPING → READY → PUBLISHED`) per Explore 1 verified grep.
- **`content_executor.py`** — content generation service — ZERO direct substrate emission at HEAD per Explore 1.
- **`publish_gate.py`** — gate-check completion — ZERO substrate emission.
- **`DeliverableEvent` model** — per EVENT_SYSTEM_INVENTORY §1.4 "best-shaped emitter in the repo for v0 intake" with `{from, to, direction, ctx}` metadata; production content pipeline writes zero DeliverableEvent rows at HEAD (design-only per S1699 §7.4 follow-on doc-PRs).
- **`ContentProcessingConsumer` + `ContentAnalyticsConsumer` (v1)** @ `content/consumers.py:23,414` — user-scoped groups (`content_processing_{user_id}` at `:35`); routing gap likely (Explore 2 identified as dormant candidates).
- **`ContentProcessingConsumer` + `ContentAnalyticsConsumer` (v2)** @ `core/consumers_base.py:1306,1359` — **duplicate class names** with different group naming schemes (`content_processing_global` at `:1314`). Explore 2 flagged: no evidence that `content/consumers.py` versions are routed via `core/routing.py`; likely dormant.
- **`MythologyConsumer`** @ `core/consumers_base.py:1494` — content-review notifications; group `mythology_updates` at `:1513`.
- **REST endpoints** — `core/apps/content/views.py:46+` ContentTemplateViewSet / DocumentViewSet / KnowledgeBaseViewSet per Explore 3; zero direct substrate emission from view bodies. S1605 T.15.E2 CRITICAL finding "REST endpoints ZERO auth decorator" inherited (also inherits into F9 API seam classification per S1904 F7 pattern).
- **PA tools** — `content_generation_tool` + `document_rag_tool` per Explore 3; zero substrate emission from PA tool paths.
- **Async correction** — Discord broadcast fire-and-forget (S1604 T.15.C1 finding per S1904 §11.a) has ZERO substrate integration.

**Cross-arc scope note:** Content internal-correctness (PublishGate decision quality, claims-pack deliberation correctness, deliverable-variant access control) is out-of-scope for P4. P4 audits ONLY: Zero-emission-at-boundary pattern + DeliverableEvent design-only status + duplicate consumer class drift + PA-tool/Discord async gap.

### 3.4 Sub-slot F.d — Observability plane seam (Group 1700 territory)

**Plane-side canonical entry points touching event / integration seam:**

- **CeleryTaskEvent** @ `core/models_celery_telemetry.py:17` — signal-driven writes via `task_prerun` / `task_postrun` handlers in `core/celery_telemetry.py`. Per S2003 §10.3.5 concern-boundary map: Celery task lifecycle concern with `(task_id, task_name, state_transition, occurred_at)` semantic tuple. 30-day TTL per S1223 close ratification.
- **LLMCallEvent** @ `core/models_llm_telemetry.py:30` — writes via `LLMCallWrapper` context manager (S1098) at `core/services/llm_call_wrapper.py`. Per S2003 §10.3.5: LLM invocation concern with `(provider, model, prompt_hash_or_correlation_id, finish_reason, occurred_at)` semantic tuple. 30-day TTL per S1219 cleanup watchdog PR #2520.
- **OpsRunEvent** @ `core/models_ops_runs.py:117` — Class-1 mirror-substrate site per S2003 §10.3.1. Primary writer: `MissionRunner._emit_event` at `core/employees/mission_runner.py:806-817`. Auxiliary writers: `core/tools/ops_run_tracker.py:34,96` (context-manager helper), `core/signals/rigby_delegation_signals.py:79`, `core/services/rigby_mission_delegation.py`, `core/services/td_handlers_rigby_work_queue.py:118`.
- **ToolCallRecord** @ `core/models_tool_calls.py:19` — writes via `ToolDispatcher.dispatch_tool_call` (S861). Per S2003 §10.3.5: PA tool dispatch concern.
- **`HallucinationMonitorConsumer`** @ `core/consumers_hallucination.py:16` — sole plane-owned WebSocket consumer; routing `core/routing.py:160` (`ws/hallucination-monitor/`); real-time blocking display fail-open.
- **9 body systems** monitored by `run_all_systems_scan` per PLATFORM_INVENTORY + `docs/topics/infrastructure.md`; body system state changes fire ZERO substrate emission per Explore 1.
- **Broadcast queue** (`core/celery.py:37+` broadcast worker per `docs/topics/celery-workers.md:41`) — 5-15m intervals for status snapshots + heartbeat + body checks; runs synchronous ORM queries + WebSocket broadcasts to consumer groups; zero EventBus emission on health state transitions.
- **Zero EventBus emission** despite S2001 F5 `publish_system_alert_event` at `event_bus.py:686` being the natural home for observability alerts (dead-code per S2001 F5 zero-caller finding).

**Cross-arc scope note:** Observability internal-correctness (9 body systems monitoring quality, S1219 watchdog completeness, S1223 retention policy adoption) is out-of-scope for P4. P4 audits ONLY: 4-substrate write-ownership pattern + EventBus adoption absence + HallucinationMonitorConsumer registration + body system alert-event gap.

### 3.5 Sub-slot F.e — HAI plane seam (Group 1800 territory)

**Plane-side canonical entry points touching event / integration seam:**

- **HAI auto-approve gate** @ `core/services/human_attention_lifecycle.py:243` — `if system_state.review_mode:` reads `HumanSystemState.review_mode` (Boundary 6-16 per S1904 §17.3); on decision write does NOT emit any substrate event.
- **Auto-approve orchestration trigger** @ `human_attention_lifecycle.py:440-656` — when auto-approve fires, orchestration workflows may execute LLM calls (Observability substrate writes via LLMCallWrapper) but HAI itself makes ZERO substrate emission at HEAD per Explore 1 verified grep across the range.
- **`HumanAttentionItem.record_decision`** @ `core/models_human_interface.py:184-214` — creates HFR row + updates HAI status; ZERO substrate emission at decision write.
- **`HumanInterfaceService.record_decision`** @ `core/services/human_interface_service.py:295-353` — public service surface wrapping model method; ZERO substrate emission.
- **`BulkAttentionDecideView.post`** — S2001 T2.5 refactor pending per S2002 §3.1; current state ZERO substrate emission.
- **`HumanFeedbackRecord.finalize`** + verification-outcome hooks per S2002 §7.2 — DESIGN-COMPLETE per S2002 §7.9 canonical + mirror recommendation; runtime emission ZERO at HEAD.
- **PA tool `human_decisions_tool`** per Explore 3 — list/details/decide handlers at `td_handlers_agents.py`; decide action creates HAI rows + updates status without secondary substrate emission.
- **43+ HAI producer paths** — S1801 finding: zero producers respect `HumanPreference.blocked_sources` at creation time; also zero producers emit any substrate event at HAI-creation.
- **WebSocket consumers** — `PAConversationConsumer` @ `core/consumers_pa_conversation.py:175` (group `pa_conversation_{conversation_id}` at `:195`) + `PersonalAssistantConsumer V2` @ `core/consumers_unified_v2.py:20` (group `pa_v2_{user_id}` at `:44`) + `AssistantChatConsumer` @ `core/consumers_base.py:390` (group `assistant_chat` at `:406`). None subscribe to EventBus analytics_workers stream (dormant per S2001 F9).

**Cross-arc scope note:** HAI internal-correctness (auto-approve gate composition per S1801, FeedbackProcessor coupling per S1802, HumanPreference personalization per S1804, S746 verification per S1805, Cat F six-plane fragmentation per S1806) is out-of-scope for P4. P4 audits ONLY: Zero-emission-at-boundary at the four candidate transitions + WebSocket consumer registration + design-vs-runtime gap for S2002 §7.9 canonical + mirror.

### 3.6 Sub-slot F.f — Authority Enforcement plane seam (Group 1900 territory)

**Plane-side canonical entry points touching event / integration seam:**

- **`MissionRunner._emit_authority_contract_event`** @ `core/employees/mission_runner.py:835-900` — emits `AUTHORITY_CONTRACT_OBSERVED` label to OpsRunEvent per S1264 warn-mode. Payload includes `employee_handle` + `contract_version_tag` + `authority_level_counts`. **Sole authority-plane event emission at HEAD** (inherited from S1904 §1 F5 verified via Explore 1).
- **`AUTHORITY_CONTRACT_OBSERVED` schema** — `AUTHORITY_CONTRACT_SCHEMA_VERSION = 1` per S1264 SIGN edit #1. All 3 production mission factories (rigby, platform_auditor, chief_of_staff) emit per mission.
- **Zero EventBus emission** — no `AUTHORITY_CONTRACT_OBSERVED` cross-substrate mirror emitted per S2003 §10.3.1 canonical + mirror pattern (pre-dates S2003 §10.3.1 codification; F17 flags `mirror_of` tag absence).
- **Zero authority-violation events** — `AUTHORITY_CONTRACT_VIOLATED` planned per S1902 §19 T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA, NOT implemented at HEAD.
- **K reads at 6 governance.py/intelligence.py sites** — per S1903 §14.1 verified classification correction — ALL are management/audit/cleanup contexts; ZERO enforcement dispatch (inherited from S1904 §1 F5 finding).
- **`AIEmployee` + `JobContract` frozen-dataclass registry** @ `core/employees/jobs.py` — declares `authority` dict; zero runtime substrate emission at contract-read.
- **F.PER-USER-AUTHORITY-MECHANISM events** — S2002 §20.9 defines `AUTHORITY_CHECK_EVALUATED` + `AUTHORITY_DECISION_OVERRIDDEN` + `AUTHORITY_POLICY_BOUND_TO_USER`; per S2003 §10.4 recommended substrate is EventBus + OpsRunEvent REQUIRED mirror. All THREE events DESIGN-ONLY at HEAD; runtime implementation post-arc.
- **`DecisionCommandConsumer`** @ `core/decision_command_consumer.py:17` + intelligence dup @ `intelligence/consumers.py:315` — WebSocket subscriber group `decision_commands` at `:35`; treats WebSocket as authoritative state (potential S2003 §10.3.4 D4 contract violation per F16).
- **Boundary 8/9 Celery kwargs** — per S1901 §7.4.1 F6a STRUCTURAL DROP inherited; `principal_user` lost at Celery process boundary; event-envelope carriage across Celery hop absent.

**Cross-arc scope note:** Authority Enforcement internal-correctness (S1904 F1-F12 authority-adjacent seams) is out-of-scope for P4 Event/Integration audit. P4 audits ONLY: single-substrate emission on OpsRunEvent + canonical + mirror shape non-adoption + F.PER-USER-AUTHORITY-MECHANISM three events design-only + violation-event schema absence + DecisionCommandConsumer WebSocket-only pattern.

### 3.7 Sub-slot F.g — Employee OS plane seam

**Plane-side canonical entry points touching event / integration seam:**

- **`MissionRunner._emit_event`** @ `core/employees/mission_runner.py:806-817` — 15+ distinct sites (step lifecycle: `step_started`, `step_completed`, `step_failed`, `step_progress`; verdicts: `mission_verdict`, `mission_started`, `mission_completed`). All writes to OpsRunEvent with `run` FK + `event_type` + `label` + `detail` dict.
- **`OpsRunTracker.emit`** @ `core/tools/ops_run_tracker.py:34,96` — context-manager write helper for OpsRun / OpsRunEvent pairs; used by mission-adjacent code that needs per-step context.
- **`emit_mission_verdict`** — per EMPLOYEE_OS_PRIMITIVES §1 row 3-5 — Verdict emission at mission completion; writes OpsRunEvent with label `verdict_issued:certified` per cross_domain_integration_audit §4.1.
- **`core/signals/rigby_delegation_signals.py:79`** — Rigby delegation signal handler write to OpsRunEvent.
- **`core/services/rigby_mission_delegation.py`** — auxiliary OpsRunEvent writer.
- **`core/services/td_handlers_rigby_work_queue.py:118`** — TD handler OpsRunEvent writer.
- **Zero EventBus emission from MissionRunner** — despite S2003 §10.3.1 defining OpsRunEvent as Class-1 mirror-substrate (canonical + mirror pair with EventBus); the invariants (equal `event_id`, `mirror_of` tag on OpsRunEvent payload, `transaction.on_commit` ordering) are unenforced at HEAD (F17 verified).
- **Boundary 5 event contract** — MissionRunner emits `AUTHORITY_CONTRACT_OBSERVED` at Boundary 5 warn-mode per S1264 (also F.f per Authority scope note). Per S2003 §10.4 recommended substrate is EventBus + OpsRunEvent REQUIRED mirror; only OpsRunEvent emission implemented.
- **7 WebSocket consumer classes** — AgentProgressConsumer (`core/consumers_base.py:74`) + AgentExecutionConsumer (`:1404`) + AgentOrchestrationConsumer (`:1449`) + RealAgentOrchestraConsumer (`:2982`) + AgentMonitorConsumer (`core/agent_monitor_consumer_simple.py`) + ProjectProgressConsumer (`core/project_progress_consumer.py:28`) + AllProjectsConsumer (`:287`). All broadcast agent + project status without EventBus co-emission.
- **`AUTHORITY_CONTRACT_OBSERVED` event consumers** — Explore 3: test suite only (`test_mission_runner_authority_warn_mode_s1264.py`); ZERO production consumers.
- **Cross-plane FK observation** — per Explore 1 + S1904 §4 Explore 1 inheritance: ZERO adjacent-plane models carry FKs to `OpsRun`, `OpsRunEvent`, `AIEmployee`, or `JobContract`. All relationships point inbound. Read/write asymmetry architecturally healthy (per S1904 §4 finding E3 "No backward refs").

**Cross-arc scope note:** Employee OS internal-correctness (job registry canonicity, mission runner determinism, retro-audit query shape) is out-of-scope for P4. P4 audits ONLY: dominant OpsRunEvent write-ownership + canonical + mirror shape non-adoption + WebSocket consumer registration + Zero-EventBus-adoption gap.

### 3.8 Sub-slot F.h — Frontend plane seam

**Plane-side canonical entry points touching event / integration seam:**

- **`frontend/src/App.tsx` 61 routes** per PLATFORM_INVENTORY — routes behind `ProtectedRoute` (session auth via authStore).
- **WebSocket connection open** — React `useEffect` hooks open connections; Django consumers own broadcast pathway.
- **`/inbox`** → `InboxPage` — receives `type: inbox.new_message` + `type: inbox.thread_created` per views_inbox.py:305-310,331-335 group_send.
- **`/command-center`** → `CommandCenterPage` — receives orchestration updates via `core/orchestra_consumers.py`.
- **`/betting`** → `BettingPage` — receives odds/arbitrage updates via sports WebSocket routes (F.b).
- **`/workspace`** — 5-tab modular workspace; receives agent + project status via Employee OS WebSocket consumers (F.g).
- **`/admin`** — receives diagnostics/telemetry via admin WebSocket consumers.
- **Zero client-side substrate emission** — Frontend does NOT compute or emit event/integration state; all emission is upstream at Django consumer/service layer.
- **Zero `type: ui.render_hint` receiver logic** — no browser consumer treats WebSocket state as display-only per S2003 §10.3.4 D4 contract; all consumers treat WebSocket state as authoritative.
- **HTTP auth via `Authorization: Bearer <token>`** (axios interceptor); `request.user` at React layer via authStore; no substrate-envelope carriage on API calls.

**Cross-arc scope note:** Frontend internal-correctness (route rendering, workspace tab UX, PA chat integration, telemetry) is out-of-scope for P4. P4 audits ONLY: Frontend has NO direct event / integration substrate write; all event emission is upstream at Django consumer/service layer. `ui.render_hint` envelope contract not implemented at browser layer.

### 3.9 Sub-slot F.i — API plane seam

**Plane-side canonical entry points touching event / integration seam:**

- **`core/services/hitl_validation.py:30`** — `_publish_validation_event(event_type='validation_required', ...)` calls `publish_validation_required_event(...)` per S2001 §3 canonical wrapper. **Sole verified EventBus emission from API-layer service at HEAD** (also `:38` for `validation_decided`).
- **`core/services/scoring_dispatcher.py:282,480`** — `publish_opportunity_scored_event(...)` calls per S2001 §10.2 producer registry.
- **`core/views_inbox.py:305-310`** — WebSocket `channel_layer.group_send` for `inbox_<user_id>` group with `type: inbox.new_message`; `:331-335` for thread participants on thread creation.
- **`core/views_diagnostics.py`** telemetry projections — 5 verified projection endpoints per Explore 3: `:825-836` (CeleryTaskEvent aggregates), `:1391-1394` (CeleryTaskEvent job_id lookup), `:1566-1569` (recent success/failure counts), `:2688-2756` (multi-endpoint queue/worker/task overview), `:3239-3387` (agent execution trace stitching across AgentExecution + CeleryTaskEvent + LLMCallLog + AuditLog).
- **Boundary 1 HTTP auth middleware** @ `core/auth_middleware.py:563-681` — authenticates (Token OR session); PUBLIC_PATHS at `:X-Y` (`/api/v1/health/`, `/health/`, `/api/app/manifest/` per S1904 §3.7); emits ZERO substrate events on auth transitions.
- **`UnifiedTokenAuthenticationMiddleware`** @ `core/auth_middleware.py:85` — no event emission.
- **209 view files** across `core/views_*.py` per PLATFORM_INVENTORY — Explore 3 verified: ZERO direct EventBus/OpsRunEvent emission from view bodies (correct per separation of concerns; service layer owns emission).
- **`views_employee_api.py`** — GET `/api/employees/` + `/api/employees/<handle>/jobs/<job_key>/status/` + `/api/missions/<mission_id>/`; reads OpsRun + JobContract with 8-field envelope. `IsAdminUser` gated. Read-only projection.
- **`views_diagnostics.py:48-62`** — writes to `CockpitAuditLog` (auxiliary audit, not substrate emission).
- **`views_human_interface.py:154`** — Boundary 16 HAI decide endpoint (per S1904 §3.4 F.d).
- **`fleet_auth_drf.py:65-150`** — Boundary 19 Fleet internal API HMAC ingress (per S1904 §3.7); Fleet HMAC carries `app_slug` for executor + sponsor; permissive fallback per Explore 3.
- **PA tool dispatcher** @ `core/services/tool_dispatcher.py:685-720` — Boundary 2 AssistantProfile gate + fail-open at `:721-722` (S1904 §3.7); emits ToolCallRecord (Observability F.d substrate); zero EventBus emission on tool dispatch (correct per S2003 §10.3.5 concern-boundary — ToolCallRecord is canonical for PA tool dispatch).
- **REST endpoint drift** — S1605 T.15.E2 CRITICAL finding "REST endpoints ZERO auth decorator" per Explore 5 (also inherited into F3 Content seam classification).
- **WebSocket consumers (Boundary 18)** — 6 sampled consumers from `core/routing.py:51-100+` per Explore 3: `AgentProgressConsumer` @ `/ws/activity/` (SafeWebSocketMixin, no explicit user auth in `connect()`); `AgentPlatformConsumer` @ `/ws/agent-platform/` (custom `connect()`, implicit via `scope['user']`); `DecisionCommandConsumer` @ `/ws/decision-command/` (no auth check before `group_add`); `SpiderWebSocketConsumer` @ `/ws/spider-updates/` (conditional import, no auth visible); `ConsciousnessConsumer` @ `/ws/consciousness/` (assumed pattern); `PAConversationConsumer` @ `/ws/pa-conversation/` (`async_to_sync(get_user)` call present). Boundary 18 sample explicit-user-extraction rate: 1/6.

**Cross-arc scope note:** API internal-correctness (endpoint routing correctness, per-view business logic, permission_class discipline) is out-of-scope for P4. P4 audits ONLY: EventBus emission via hitl_validation.py + scoring_dispatcher.py + WebSocket emission via views_inbox.py + telemetry projections at views_diagnostics.py + Boundary 1 auth emission absence + Boundary 18 WebSocket auth absence.

### 3.10 Sub-slot F.j — Discord plane seam

**Plane-side canonical entry points touching event / integration seam:**

- **`core/services/discord_bot.py`** — 11,676 LOC per PLATFORM_INVENTORY; 96 @*.command decorators + 48 @app_commands.command + 25 Cog classes. ZERO substrate emission per Explore 1 + Explore 3 verified grep.
- **`RateLimiter` class** @ `discord_bot.py:85-100` — per-command cooldowns; NOT substrate-derived (Discord-native rate control).
- **`PermissionLevel` class** @ `discord_bot.py:129` — `ADMIN_USER_IDS` + `TRUSTED_USER_IDS` per S1904 §3.8; no substrate emission.
- **`DiscordLinkCode` model** — Discord user_id ↔ web User FK mapping; `_get_linked_user()` fallback returns None when unlinked (per S1904 §3.8).
- **PA tool dispatcher path** — Discord commands dispatch via PA tool surface; downstream ToolCallRecord write via ToolDispatcher (Observability F.d substrate); zero EventBus emission at Discord layer.
- **Celery task dispatch from Discord** — Discord async commands (e.g., `/agent-task`) fire `execute_agent_task.apply_async(...)` per Explore 3; Boundary 8/9 F6a `principal_user` drop (S1901 §7.4.1 inherited).
- **`core/services/discord_notifications.py`** — invoked FROM EventBus event handlers as NOTIFICATION SINK: `event_handlers.py:216-231` VALIDATION_REQUIRED handler + `:326-339` MODEL_TRAINED handler + `:370-383` SYSTEM_ALERT handler. Fire-and-forget; ImportError-caught fail-open; no ack/nack pattern; brittle to import failure.
- **Boundary 3 adjacent** per S1902 §17 (Discord is NOT in P2 20-boundary table; treated as adjacent surface for PA tool handler body).

**Cross-arc scope note:** Discord internal-correctness (96-command god-service refactor, per-Cog UX correctness, Discord-specific auth model) is out-of-scope for P4. P4 audits ONLY: substrate emission absence + notification-sink downstream pattern + Celery Boundary 8/9 drop propagation.

## 4. Major Models

Cat F is CONSOLIDATION scope. This section catalogs event / integration-plane models touched at each plane seam + FK graph crossing the event / integration ↔ adjacent-plane boundary. No new models are introduced. Full model provenance / lineage was audited at P1 (S2001 §4) + P2 (S2002 §4) + P3 (S2003 §4) + adjacent-plane arcs (S1301-S1305 / S1501-S1506 / S1601-S1606 / S1701-S1706 / S1801-S1806 / S1901-S1904).

**Event / integration-plane models (canonical registry per S2003 §4 + F13 addition):**

| Model / Substrate | File:Line | Owner | Consumers at seam |
|---|---|---|---|
| `Event` (dataclass, EventBus envelope) | `core/services/event_bus.py:41-77` | Group 2000+ | READ by consumer workers via `Event.from_dict`; downstream handlers dispatch on `event_type` |
| `EventStream` (str-Enum, 8 values) | `core/services/event_bus.py:21-30` | Group 2000+ | READ by publisher wrappers + consumer worker registrations |
| `EventPriority` (str-Enum) | `core/services/event_bus.py:33-38` | Group 2000+ | INFORMATIONAL only; not enforced by broker |
| `ConsumerInfo` (dataclass, decorative — S2001 F18-adjacent) | `core/services/event_bus.py:80-87` | Group 2000+ | UNUSED (S2003 §4 F18-adjacent codification) |
| `HandlerResult` (dataclass) | `core/services/event_handlers.py:20-28` | Group 2000+ | READ by `process_batch` to compute ACK/non-ACK per event |
| Per-stream Redis Streams (`mi:*`) | Redis (external) | Group 2000+ | Redis Streams `xadd`/`xreadgroup`/`xack`/`xrange`/`xpending_range`/`xclaim`; MAXLEN=10000 per S2001 §4 |
| Dead-letter Redis Stream (`mi:dead_letter`) | Redis (external) | Group 2000+ | `xadd` only from `_move_to_dead_letter` at S2001 §4 line 468-471; MAXLEN=1000 |
| `CeleryTaskEvent` | `core/models_celery_telemetry.py:17` | Group 1700 Observability (Cat F.d substrate write-owner) | READ by PA `celery_task_history` tool; Grafana dashboards; S1245 `audit_celery_zero_fire`; retention 30d per S1223 |
| `LLMCallEvent` | `core/models_llm_telemetry.py:30` | Group 1700 Observability (Cat F.d substrate write-owner) | READ by watchdog (S1219); cost tracking; reliability metrics; retention 30d per S1219 PR #2520 |
| `OpsRunEvent` | `core/models_ops_runs.py:117` | Group 1700 Observability (Cat F.d substrate write-owner) + Group 2000+ Class-1 mirror-substrate site per S2003 §10.3.1 | WRITTEN by MissionRunner @ mission_runner.py:882 + auxiliary Rigby-adjacent writers; READ by `derive_status` @ status.py:53-388 + `views_diagnostics.py:155` + `views_employee_api.py`; NO default TTL (audit-forever posture for Class-1) |
| `ToolCallRecord` | `core/models_tool_calls.py:19` | Group 1700 Observability (Cat F.d substrate write-owner) | READ by PA `tool_call_history` tool; provenance dashboards; retention 30d per S861 |
| **`FleetEvent`** (F13 seventh-substrate candidate) | `core/services/fleet_events.py` (285 LOC, ORM model referenced but location not directly enumerated) | (UNCLASSIFIED per F13; Chris-gate pending) | WRITTEN by `signal_aggregation_service.py:801` (sole verified caller); READ side unaudited; Redis pub/sub per-app-channel; ORM row for durable audit; classification per §14.3.1 + Chris-gate at close |
| `DeliverableEvent` (design-only per Content F.c) | `core/models` (per EVENT_SYSTEM_INVENTORY §1.4) | Group 1600 Content | WRITTEN by zero production callers at HEAD (S2001 F5 zero-caller pattern extension); READ side design-only |
| `TriggerEvent` / `ImpactEvent` (S1273 §3.25 named event tables) | (per EVENT_SYSTEM_INVENTORY §1.3, §1.6) | Domain-specific hooks | READ by dashboards / spider evaluators; retention domain-specific; per S2003 §3 note NOT substrates in composition-contract sense (audit-object states, not push-with-consumers or write-and-query telemetry) |

**Cross-plane FK graph — adjacent-plane models with FKs INTO event / integration-plane models:**

Per Explore 1 comprehensive audit + S1904 §4 finding E3 inheritance: **ZERO adjacent-plane models carry FKs to `OpsRun`, `OpsRunEvent`, `CeleryTaskEvent`, `LLMCallEvent`, `ToolCallRecord`, or `FleetEvent`.** All relationships point inbound (`mission_id` optional in OpsRun, `run` FK in OpsRunEvent). This prevents accidental coupling loops. Applies also to F13 Fleet Events — FleetEvent has no back-refs.

**Adjacent-plane models READ by event / integration-plane services:**

| Model | File:Line | Read by | Purpose |
|---|---|---|---|
| `HumanSystemState` | `core/models_human_interface.py` (HAI plane) | HAI auto-approve reads at `human_attention_lifecycle.py:243` (S1904 §4) — but this is HAI-plane INTERNAL read, not event / integration-side | Boundary 6-16 decision-adjacent state |
| `HumanAttentionItem` | `core/models_human_interface.py:36-227` (HAI plane) | READ by decide endpoint + PA `human_decisions_tool`; potentially READ by event handlers per S2002 §17 (currently no consumer subscribes) | Group 1800 Cat A territory |
| `Deliverable` | Content plane | Content pipeline writers; potentially READ by content-adjacent event handlers (currently zero) | Group 1600 Content territory |
| `AgentLearning` + `UserAgentLearning` | Memory plane | Memory writers; NOT read by event / integration-plane | Group 1300 Memory territory |
| `AIEmployee` + `JobContract` frozen dataclasses | `core/employees/jobs.py` (Authority plane) | READ by MissionRunner init per S1904 §5 | Authority-plane READ by Employee OS mission runner |

**Duplicate event-adjacent models across planes (Explore 6 F5 HYPOTHESIS DISPROVE evidence per F12 above):**

- `DeliverableEvent` (Content plane) parallels `Event` (EventBus envelope) semantically as "canonical domain-event carrier" but is a SEPARATE model — Content pipeline does NOT emit via EventBus. This is **semantic duplication, not model coupling** (loose-coupling per Explore 1 finding).
- `TriggerEvent` (per S1273 §3.25) is a domain-object state, not a substrate emission (per S2003 §3 note).
- `FleetEvent` (F13 seventh-substrate candidate) is architecturally a HYBRID push-with-consumers + durable-audit substrate; classification pending Chris-gate.
- No other duplicate authority-adjacent gate primitive across the 10 planes per F12 HYPOTHESIS DISPROVE.

Per Explore 6 F5 HYPOTHESIS test at §17.2: no plane exhibits a duplicate substrate-emission primitive.

## 5. Major Services

Cat F CONSOLIDATION cross-plane consolidation service map. Adjacent-plane services that CALL event / integration-plane primitives + services that DUPLICATE event-emission-adjacent primitives.

### 5.1 Adjacent-plane services calling event / integration-plane primitives

Per Explore 1 + Explore 3 verified grep across `intelligence/`, `content/`, `sports/`, `human_attention/`, `employees/`, `frontend/`, `views_*.py`, and `discord_bot.py`:

| Caller (adjacent) | File:Line | Callee (event / integration primitive) | Fail behavior | Substrate |
|---|---|---|---|---|
| `signal_aggregation_service._maybe_emit_cluster_promoted` | `core/services/signal_aggregation_service.py:776,801` | `emit_event(app_slug, event_type='signal.cluster_promoted', payload=envelope)` from `core/services/fleet_events.py` | `emit_event already swallows internal failures` (per `:814` comment); fail-open | Fleet Events (F13 seventh-substrate candidate) |
| `scoring_dispatcher._score_realtime` | `core/services/scoring_dispatcher.py:282` | `publish_opportunity_scored_event(...)` @ `event_bus.py:559` (via `_publish_scoring_event` helper at `scoring_dispatcher.py:21-51`) | Try/except → log-only fail-open (S2001 §7 verified) | EventBus (`OPPORTUNITY_SCORED` stream) |
| `scoring_dispatcher._score_batch` | `core/services/scoring_dispatcher.py:480` | Same `publish_opportunity_scored_event(...)` | Same | EventBus (`OPPORTUNITY_SCORED` stream) |
| `hitl_validation._publish_validation_event` (event_type=required) | `core/services/hitl_validation.py:30` | `publish_validation_required_event(...)` @ `event_bus.py:596` | Try/except → log-only fail-open | EventBus (`VALIDATION_REQUIRED` stream) |
| `hitl_validation._publish_validation_event` (event_type=decided) | `core/services/hitl_validation.py:38` | `publish_validation_decided_event(...)` @ `event_bus.py:619` | Try/except → log-only fail-open | EventBus (`VALIDATION_DECIDED` stream) |
| `SportsUpdatesConsumer.handle_force_odds_update` | `core/consumers_sports.py:106,127` | `channel_layer.group_send(group_name, {"type": "odds_updated" | "league_updated", ...})` | Fail-open (Django Channels swallows on group timeout) | WebSocket (Django Channels) |
| `InboxView.post` (message create) | `core/views_inbox.py:305-310` | `channel_layer.group_send(f"inbox_{user_id}", {"type": "inbox.new_message", ...})` | Fail-open | WebSocket (Django Channels) |
| `InboxView.post` (thread create) | `core/views_inbox.py:331-335` | `channel_layer.group_send(f"inbox_{participant_id}", {"type": "inbox.thread_created", ...})` | Fail-open | WebSocket (Django Channels) |
| `MissionRunner._emit_event` | `core/employees/mission_runner.py:806-817` | `OpsRunEvent.objects.create(run=self.ops_run, event_type=..., label=..., detail=...)` (implicit — no direct wrapper; ORM write) | ORM exception propagates → step marked failed | OpsRunEvent |
| `MissionRunner._emit_authority_contract_event` | `core/employees/mission_runner.py:835-900` | Same `OpsRunEvent.objects.create(...)` with label `authority_contract_observed` | ORM exception propagates | OpsRunEvent |
| `OpsRunTracker.emit` | `core/tools/ops_run_tracker.py:34,96` | `OpsRunEvent.objects.create(...)` context-manager helper | ORM exception propagates | OpsRunEvent |
| `rigby_delegation_signals.handle_delegation_created` | `core/signals/rigby_delegation_signals.py:79` | `OpsRunEvent.objects.create(...)` | Django signal exception boundary | OpsRunEvent |
| `LLMCallWrapper.__enter__` / `__exit__` | `core/services/llm_call_wrapper.py` | `LLMCallEvent.objects.create(...)` per S1098 | ORM exception propagates | LLMCallEvent |
| `ToolDispatcher.dispatch_tool_call` | `core/services/tool_dispatcher.py:685-720` | `ToolCallRecord.objects.create(...)` per S861 | ORM exception → log + continue | ToolCallRecord |
| `celery_telemetry.on_task_prerun` / `on_task_postrun` | `core/celery_telemetry.py` | `CeleryTaskEvent.objects.create(...)` | Django signal exception boundary | CeleryTaskEvent |
| `event_handlers.handle_validation_queued_event` → Discord notify | `core/services/event_handlers.py:216-231` | `discord_notifications.send_to_channel(...)` | ImportError caught + logged loud (S1103c) → fail-open | Discord notification sink (downstream from EventBus handler) |
| `event_handlers.handle_model_trained_event` → Discord notify | `core/services/event_handlers.py:326-339` | Same | Same | Same |
| `event_handlers.handle_system_alert_event` → Discord notify | `core/services/event_handlers.py:370-383` | Same | Same | Same |

**Total event / integration-primitive call sites from adjacent planes:**
- **3 EventBus** verified emission sites (2 Intelligence scoring_dispatcher + 1 Intelligence hitl_validation split into 2 event types); ZERO Content / Sports / HAI / Authority / Employee OS / Frontend / Discord direct EventBus calls
- **3 WebSocket** verified emission sites in the API sample (Sports consumers_sports.py:106,127 + Inbox views_inbox.py:305-310,331-335); ~40 group_send call sites total per S2003 §10.5 audit inheritance
- **4 telemetry substrate writes** distributed across MissionRunner + LLMCallWrapper + ToolDispatcher + Celery signal handlers (concern-boundary CLEAN per S2003 §10.3.5 + F12 P3 verified)
- **1 Fleet Events call site** (F13 seventh-substrate candidate) at `signal_aggregation_service.py:801`

### 5.2 Adjacent-plane duplicate event-emission-adjacent primitives

Per §5.1 + Explore 6 F5 HYPOTHESIS test (F12 above): **ZERO adjacent planes duplicate event-emission-adjacent primitives.** Per F12 finding (§1): DISPROVE across all 10 planes.

Semantic-only parallels (not model duplicates):

- `DeliverableEvent` (Content plane) parallels `Event` (EventBus envelope) semantically as canonical domain-event carrier; separate model families (see §4).
- `TriggerEvent` (per S1273 §3.25) is a domain-object state, not a substrate emission (loose coupling).
- WebSocket `type: <string>` fields (e.g., `type: 'live_odds_update'`, `type: 'inbox.new_message'`) parallel EventBus `event_type` field semantically but are separate substrate contracts (concern-boundary CLEAN).
- Discord `RateLimiter` parallels action-throttling semantically (per S1904 §5.2); orthogonal to event/integration primitives.

All are ORTHOGONAL to event / integration substrates — different signal sources, different model families, different concern boundaries.

### 5.3 Duplicate composition resolvers across planes

Per Explore 6 + Explore 4: NONE. No plane implements its own cross-substrate composition resolver duplicating S2003 §10.2 three-axis selector. Composition is distributed-at-boundary per S2003 §3 design — each caller chooses the substrate based on the Axis A/B/C selector documented in S2003 §10.2 (adoption via code review + wrapper adoption, no runtime enforcement).

### 5.4 EventBus canonical + mirror-substrate site status

Per S2003 §10.3.1 canonical: OpsRunEvent is the Class-1 governance mirror-substrate site (equal `event_id` invariant + `mirror_of` tag + `transaction.on_commit` ordering); MissionRunner is the dominant caller.

**Verified status at HEAD `7fc1bc1c`:** Post-Explore verifier grep `mirror_of` across `core/` returned ZERO matches (F17 verified). Post-Explore verifier grep `event_id=` on OpsRunEvent write sites returned ZERO explicit event_id assignments (implicit UUID via row `.id` FK, not S2003 §10.3.1 canonical-mirror `event_id` invariant). The entire canonical + mirror composition contract is DESIGN-ONLY at S2004 close. Post-arc T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER execution required per S2003 §14.

### 5.5 Fleet Events (F13) service surface

`core/services/fleet_events.py` (285 LOC):
- Public API: `emit_event(app_slug, event_type, payload, ...) → event_id`
- Underlying storage: `FleetEvent` ORM row + Redis pub/sub per-app channel
- Fail behavior: internal exceptions swallowed per `signal_aggregation_service.py:814` comment ("emit_event already swallows internal failures")
- Sole verified caller: Memory F.a `signal_aggregation_service._maybe_emit_cluster_promoted` at `:776,801` for `signal.cluster_promoted` event
- Downstream consumer path: unaudited at HEAD (F13 investigation candidate for post-arc T2 R.EVENTS.FLEET-EVENTS-CONSUMER-AUDIT)

**Classification pending Chris-gate per §14.3.1 + F11 above.**

## 6. Major APIs and Interfaces

Cat F CONSOLIDATION external-facing surface inventory per plane (REST + PA tools + Celery + Discord + WebSocket + Frontend routes) that crosses the event / integration boundary.

### 6.1 REST endpoint inventory touching event / integration seam

- **Total view files:** 209 across `core/views_*.py` (PLATFORM_INVENTORY).
- **Direct EventBus/OpsRunEvent emission from view bodies:** ZERO per Explore 3 verified grep (service layer owns emission; correct per separation of concerns).
- **WebSocket `channel_layer.group_send` emission from view bodies:** 2 verified sites at `views_inbox.py:305-310,331-335`.
- **Telemetry projection endpoints (read-only):** 5 verified at `views_diagnostics.py:825-836,1391-1394,1566-1569,2688-2756,3239-3387` (CeleryTaskEvent + AgentExecution + LLMCallLog + AuditLog aggregates).
- **Boundary 1 auth emission:** ZERO on authentication events per `auth_middleware.py:563-681`.
- **Boundary 16 HAI decide** — `views_human_interface.py:154`; ZERO substrate emission at decide-endpoint.
- **Boundary 19 Fleet HMAC** — `fleet_auth_drf.py:65-150`; ZERO substrate emission on ingress.
- **Boundary 18 WebSocket handlers** — 6 sampled consumers per §3.9; 1/6 explicit user auth in `connect()`; ZERO substrate emission at consumer boundary.
- **S1605 T.15.E2 inheritance** — "REST endpoints ZERO auth decorator" also breaks event / integration observability at API entry.

### 6.2 PA tool schemas + handlers

- **Total schemas:** 113 (PLATFORM_INVENTORY).
- **Total handlers:** 156 (PLATFORM_INVENTORY).
- **PA tools emitting events directly:** ZERO per Explore 3 (correct — PA tools are stateless orchestration coordinators; service layer owns emission).
- **PA tools that fire Celery tasks that would emit events downstream:** `sports_tool` (arbitrage detection), `content_tool` (PublishGate), `dispatch_tool` (agent dispatch), etc. — Celery Task lifecycle captured by CeleryTaskEvent signal handlers (Observability F.d substrate); downstream EventBus emission depends on service layer.
- **`session_tool` + `platform_config_tool`** — read-side helpers; ZERO substrate emission.
- **`ops_run_tracker` helper** — `core/tools/ops_run_tracker.py:22-101` wraps multi-step operations + creates OpsRunEvent records (write-side).
- **Boundary 2 tool_dispatcher fail-open** — `core/services/tool_dispatcher.py:685-720,721-722` (S1904 §3.7); emits ToolCallRecord; zero EventBus emission (correct per concern boundary).
- **Boundary 3 per-handler bodies** — `td_handlers_*.py` (11 mixin classes × 2-5 methods = ~42 handlers per Explore 3); zero visible substrate emission across sampled handlers.

### 6.3 Celery task inventory

- **Total tasks:** 414 (PLATFORM_INVENTORY).
- **Beat schedule:** 91 enabled + 5 disabled = 96 PeriodicTask rows (PLATFORM_INVENTORY).
- **Beat-enrolled EventBus tasks:** 1 of 5 (`claim_stale_events` @ `core/celery.py:531-535`, 5-min interval).
- **Beat-dormant EventBus tasks:** 4 of 5 (`process_event_bus_scoring_queue` @ `tasks.py:4726` + `process_event_bus_validation_queue` @ `:4760` + `process_event_bus_analytics_queue` @ `:4794` + `get_event_bus_stats` @ `:4874`) per S2001 F9 verified extending to F14 above.
- **CeleryTaskEvent signal handlers** — `core/celery_telemetry.py` (task_prerun / task_postrun) — signal-driven canonical path.
- **Per Explore 3 sample of 5 tasks:** 0/5 carry `event_id`/`correlation_id`/`mirror_of` envelope carriage across Celery task boundaries.
- **Cross-substrate emission in single task execution:** zero verified per Explore 6 P3 concern-boundary drift test.

### 6.4 WebSocket consumers (Boundary 18)

- **Total consumer classes:** 33+ across `core/consumers*.py` (Explore 2 sample).
- **`type: ui.render_hint` envelope usage:** ZERO across all 33+ classes per §14.3.3 verifier.
- **`connect()` auth check discipline:** Immediate `group_add` on connect (Django Channels pattern); per-connection auth via middleware.
- **Substrate emission at consumer boundary:** ZERO (correct — consumers receive events, not emit).
- **Group_send emission at handler methods:** ~40 sites per S2003 §10.5 (production side); include Sports (F.b) + Inbox (F.i) + Content (F.c) + Employee OS (F.g) + HAI (F.e) + Frontend (F.h dashboard consumers).

### 6.5 Discord commands

- **Total commands:** 96 @*.command decorators + 48 @app_commands.command + 25 Cog classes (PLATFORM_INVENTORY).
- **discord_bot.py LOC:** 11,676 (PLATFORM_INVENTORY).
- **Substrate emission from command dispatch:** ZERO per Explore 1 + Explore 3 verified (also inherits F10 STRUCTURAL-DROP + S1904 F8 STRUCTURAL-DROP).
- **Notification sink downstream from EventBus handlers:** `discord_notifications.send_to_channel(...)` called from `event_handlers.py:216-231, :326-339, :370-383` (VALIDATION_REQUIRED + MODEL_TRAINED + SYSTEM_ALERT handlers).
- **Boundary 3 adjacent** per S1902 §17 (Discord NOT in 20-boundary table).

### 6.6 Frontend routes (event / integration-touching subset)

- **Total routes:** 61 in `App.tsx` (PLATFORM_INVENTORY).
- **Routes with WebSocket connection:** ~15-20 (Explore 3 partial coverage): `/inbox` + `/command-center` + `/betting` + `/workspace` + `/admin` + workspace tab consumers + agent progress consumers.
- **Client-side substrate emission:** ZERO (correct per delegation).
- **`type: ui.render_hint` receiver logic:** ZERO across all Frontend routes (F16 verified).
- **UI-render-hint envelope contract adoption:** NOT IMPLEMENTED at browser layer (S2003 §10.3.4 D4 aspirational).

## 7. Runtime Flows

Cat F CONSOLIDATION per-plane emission touchpoint + consumer-registration seam trace. Where does event / integration emission cross into each adjacent-plane concern? Where does subscription bind? Where are the drop points?

### 7.1 Cat F per-plane emission-touchpoint + consumer-registration seam matrix

Master seam-matrix table (per Explore 4 + Explore 6 synthesis, adapted from S1904 §7.1 shape). Columns: Plane / Inbound substrate reads / Outbound substrate writes / Propagation drops / Consumer subscriptions / Emission gaps / Substrate × HAI-event mapping applicability / Dual-emission cases observed / UI-render fanout applicability / Posture verdict / Owned-by-2000+ vs delegated / Cross-arc T-slot.

| Plane | Inbound substrate reads | Outbound substrate writes | Propagation drops (correlation_id / event_id / mirror_of) | Consumer subscriptions | Emission gaps (S2001 F1-F18) | S2003 §10.4 substrate × HAI-event mapping applicability | Dual-emission observed | UI-render fanout applicability (S2003 §10.3.4 D4) | Posture verdict | Owned-by-2000+ vs delegated | Cross-arc T-slot |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Memory (1300)** | Zero (writer plane no-read) | 1 site: Fleet Events (`signal.cluster_promoted` @ `signal_aggregation_service.py:801`) | correlation_id=None; event_id via Fleet Events (F13); no `mirror_of` | AITrainingConsumer + ConsciousnessConsumer WebSocket subscribers; dormant EventBus analytics_workers | S2001 F1 SPIDER_DATA canonical producer ZERO callers from Memory writer plane | N/A (Memory not in S2003 §10.4 12-event map) | Fleet Events per F13 (potential seventh substrate; classification pending) | Not implemented per F16 | PERMEABLE-BROKEN | Delegated to 1300 (Memory owns writer plane); Owned-by-2000+ Fleet Events classification | R1 Fleet Events ADR (Chris-gate) + T3 R.MEMORY.WRITER-PLANE-EVENT-EMISSION-DOC |
| **Sports (1500)** | Zero direct reads (WebSocket consumers subscribe to broadcast groups) | 2 sites: WebSocket group_send (`odds_updated`, `league_updated` @ `consumers_sports.py:106,127`) | correlation_id=None; no envelope carriage | 8 WebSocket consumer classes; dormant EventBus scoring/validation/analytics_workers | S2001 F1 SPIDER_DATA + F3 OUTCOME_RECORDED zero-caller | N/A (Sports not in §10.4) | Zero | Not implemented per F16 | PARTIAL | Delegated to 1500 (Sports owns WebSocket path); Owned-by-2000+ canonical substrate assignment | S1500 T3 R.SPORTS.OUTCOME-RECORDED-EMIT + T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT |
| **Content (1600)** | Zero | Zero (DeliverableEvent design-only; PublishGate zero-emission) | N/A | 5 WebSocket consumers (2 dup class name pairs); dormant EventBus analytics_workers | S2001 F5 SYSTEM_ALERT zero-caller; DeliverableEvent design-only extension | N/A (Content not in §10.4) | Zero | Not implemented per F16 | EXPERIMENTAL | Delegated to 1600 (Content owns PublishGate + DeliverableEvent); Owned-by-2000+ canonical substrate assignment | S1600 T1 R.CONTENT.DELIVERABLE-EVENT-EMISSION-WIRING + T2 R.EVENTS.CONTENT-CONSUMER-CLASS-DEDUP |
| **Observability (1700)** | Read-side owner of 4 telemetry substrates via ORM queries (derive_status, PA tools) | 4 substrates: CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord (write-owner) | correlation_id defined but not populated (F15); event_id via row PK; no `mirror_of` (F17) | HallucinationMonitorConsumer WebSocket; dormant EventBus | S2001 F5 SYSTEM_ALERT zero-caller from Observability plane (natural home) | N/A (Observability substrates are Class-2 telemetry; not in §10.4 12-event HAI map) | Zero (concern-boundary CLEAN per P3) | Not implemented per F16 | WORKING | Owned-by-1700 (4 telemetry substrates); Owned-by-2000+ concern-boundary policy | T2 R.EVENTS.OBSERVABILITY-SYSTEM-ALERT-EMISSION + T3 R.EVENTS.CORRELATION-ID-RUNTIME-ADOPTION |
| **HAI (1800)** | Zero (auto_approve reads HumanSystemState.review_mode, not substrate) | Zero at HEAD (S2002 §7.9 canonical + mirror design-only) | N/A at HEAD (design pending) | 3 WebSocket consumers (PAConversation + PersonalAssistantV2 + AssistantChat); dormant EventBus analytics_workers | S2002 §7 four HAI candidate transitions ZERO emission | 4 events in §10.4 (`HAI_DECISION_RECORDED` + `HAI_VERIFICATION_RECORDED` + `HAI_AUTO_APPROVED` + `HAI_AUTO_ESCALATED`) — all design-only | Zero at HEAD; design-only S2002 §7.9 canonical + mirror | Not implemented per F16 | EXPERIMENTAL | Owned-by-2000+ event contract + canonical + mirror wiring; Owned-by-1800 HAI-plane implementation | T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING (highest T1 priority per F5 severity) |
| **Authority Enforcement (1900)** | Zero substrate reads | 1 substrate: OpsRunEvent (`AUTHORITY_CONTRACT_OBSERVED` @ `mission_runner.py:882`) | correlation_id=None; event_id via row PK; no `mirror_of` | Zero substrate consumer subscription (test-suite reader only) | S2002 §20.9 F.PER-USER-AUTHORITY three events design-only; `AUTHORITY_CONTRACT_VIOLATED` NOT implemented per S1902 §19 T1 | 3 F.PER-USER-AUTHORITY events in §10.4 (AUTHORITY_CHECK_EVALUATED + AUTHORITY_DECISION_OVERRIDDEN + AUTHORITY_POLICY_BOUND_TO_USER) all design-only | Zero at HEAD (canonical + mirror shape not applied to AUTHORITY_CONTRACT_OBSERVED) | Not implemented per F16 | WORKING | Owned-by-2000+ event contract + Boundary 5 emission policy; Owned-by-1900 authority-plane implementation | T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA (S1902 §19) + T1 R.EVENTS.PER-USER-AUTHORITY-EMISSION-WIRING |
| **Employee OS** | Zero substrate reads (MissionRunner reads AIEmployee + JobContract, not substrates) | 1 substrate: OpsRunEvent (dominant write-owner across MissionRunner + OpsRunTracker + auxiliary Rigby-adjacent) | correlation_id=None; event_id via row PK; no `mirror_of` (F17); no `event_id` equality invariant | 7 WebSocket consumer classes; dormant EventBus scoring_workers | S2001 F4 MODEL_TRAINED + F3 OUTCOME_RECORDED zero-caller from Employee OS | Employee OS is dominant OpsRunEvent write-owner + is Class-1 mirror-substrate site per S2003 §10.3.1; canonical + mirror shape design-only | Zero at HEAD; canonical + mirror shape unenforced | Not implemented per F16 | WORKING | Owned-by-1700 OpsRunEvent write-ownership + Owned-by-2000+ canonical + mirror shape | T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER + T2 R.EVENTS.EMPLOYEE-OS-EVENTBUS-CANONICAL-ADOPTION |
| **Frontend** | Zero (React reads WebSocket state) | Zero (delegated) | N/A | ~15-20 Frontend routes with WebSocket subscribe | N/A (Frontend delegated read-only) | N/A | N/A | Not implemented per F16 | CLEAN (verified read-only) *(per S1904 Q3(b) fold: Frontend does NOT emit event / integration state; if any browser UI ever emits directly to a substrate, Frontend becomes PERMEABLE-BROKEN until an explicit write-boundary contract exists)* | Delegated to Frontend (per-route WebSocket subscription) | None |
| **API** | Zero direct substrate reads at Boundary 1 (auth middleware) | 4 sites verified: EventBus (`hitl_validation.py:30,38` VALIDATION_REQUIRED + VALIDATION_DECIDED) + WebSocket (`views_inbox.py:305-310,331-335` inbox.new_message + inbox.thread_created) + also scoring_dispatcher path (`scoring_dispatcher.py:282,480`) | correlation_id=None per S2001 §8; event_id=None on all emissions; no `mirror_of` | Boundary 18 6 sampled consumers; 1/6 explicit user auth; dormant EventBus scoring/validation/analytics_workers | 209-view distributed emission-gap; Boundary 1 auth events zero emission; ~40 group_send call sites without envelope carriage | N/A for HAI 12-event map (API delegates emission to services) | Zero canonical + mirror observed | Not implemented per F16 (~40 group_send sites) | PARTIAL | Delegated to API (per-view emission decision); Owned-by-2000+ canonical envelope + auth-event emission | T2 R.EVENTS.API-BOUNDARY-1-AUTH-EMISSION + T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT + T3 R.EVENTS.API-LAYER-EMISSION-INSTRUMENTATION |
| **Discord** | Zero substrate reads | Zero substrate writes at command dispatch | N/A | Notification sink downstream (fire-and-forget from EventBus handlers) | Zero emission across 96 commands + 25 Cogs (STRUCTURAL-DROP per F10 + inherits S1904 F8) | N/A (Discord not in §10.4) | Zero | Not implemented per F16 | STRUCTURAL-DROP | Delegated to Discord (post-integration); Owned-by-2000+ notification-sink contract | T2 R.EVENTS.DISCORD-COMMAND-DISPATCH-EMISSION-INSTRUMENTATION (inherits S1903 Q8 3 prerequisites via S1904 §19) |

### 7.2 Cross-plane duplicate event-emission-adjacent primitive inventory (F5 HYPOTHESIS DISPROVE evidence)

Per §5.2 + Explore 6 §H1 F5 HYPOTHESIS: **"Every plane duplicates event-emission-adjacent primitives (custom pub/sub, custom event log wrapper, custom broadcast fanout, custom substrate)."** Result: **DISPROVE across all 10 planes.**

- Memory: NO duplicate primitive (Fleet Events is a SHARED substrate consumed by Memory alone, not a per-plane duplicate; F13 classification pending).
- Sports: NO duplicate (WebSocket-only pattern uses canonical Django Channels).
- Content: NO duplicate (DeliverableEvent design-only; no custom Publisher class).
- Observability: NO duplicate (4 telemetry substrates are canonical Class-2 substrates per S2003 §10.1, not per-plane duplicates).
- HAI: NO duplicate (zero substrate emission at HEAD; when implemented per T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING will use canonical EventBus + OpsRunEvent).
- Authority: NO duplicate (OpsRunEvent-only single-substrate emission).
- Employee OS: NO duplicate (dominant OpsRunEvent write-owner uses canonical substrate).
- Frontend: NO duplicate (delegated).
- API: NO duplicate (canonical EventBus + WebSocket used).
- Discord: NO duplicate (STRUCTURAL-DROP; no emission surface).

**Cross-arc F5 running tally at S2004 close:** 1 pass (S1806 Cat F.d partial confirmation) / 7 disprove (S1802 + S1803 + S1804 + S1805 + S1904 H1 + S2004 H1 across 10 planes). Meta-methodology observation: durable-at-7 running tally under F5-primitive-testing arc-close discipline continues DISPROVE-dominant pattern. xx99 §10 meta-methodology CODIFICATION-CONFIRMED candidate.

### 7.3 Cat F separation-boundary policy register — owned by 2000+ vs delegated

Per Explore 4 cross-plane synthesis:

| Decision | Owned by 2000+ | Delegated to adjacent plane |
|---|---|---|
| Six-substrate separation contract (Axis A/B/C per S2003 §10.2) | Yes | — |
| Fleet Events classification (F13) | Yes (Chris-gate at close) | — |
| Canonical + mirror invariants (event_id equality, mirror_of tag, transaction.on_commit) | Yes (S2003 §10.3.1) | — |
| WebSocket UI-render fanout envelope (S2003 §10.3.4 D4 `ui.render_hint`) | Yes | Per-consumer implementation |
| Concern-boundary map (S2003 §10.3.5 per-substrate semantic tuple) | Yes | Per-plane concern-boundary compliance |
| HAI four candidate transition emission (S2002 §7 + §7.9) | Yes (canonical schema + wire-up contract) | Per-1800 HAI-plane implementation |
| Six-plane learning-surface event schema (S2002 §10) | Yes | Per-plane emission implementation |
| F.PER-USER-AUTHORITY three-event emission (S2002 §20.9) | Yes (canonical schema) | Per-1900 authority-plane resolution mechanism |
| Boundary 5 AUTHORITY_CONTRACT_OBSERVED emission | Co-owned (1900 owns contract shape; 2000+ owns substrate assignment) | — |
| OpsRunEvent write-ownership | Delegated to 1700 Observability | Per-1700 concern-boundary compliance |
| CeleryTaskEvent / LLMCallEvent / ToolCallRecord write-ownership | Delegated to 1700 Observability | Same |
| Consumer beat-enrollment discipline (S2001 F9) | Yes (canonical infra) | Per-consumer enrollment |
| DeliverableEvent adoption (S1699 §7.4 follow-on) | Co-owned (1600 owns model; 2000+ owns substrate assignment) | Per-1600 Content-plane implementation |
| F11 spider-data substrate consolidation (three-substrate drift) | Yes | — |
| WebSocket ↔ EventBus overlap resolution (S2003 §10.5 D4) | Yes (canonical rule) | Per-consumer implementation |
| Consumer authorization at Boundary 18 | Delegated to consumer classes | Per-consumer implementation |
| Boundary 1 auth-event emission | Yes (canonical schema) | Per-API-boundary implementation |
| Discord command dispatch emission (S1903 Q8 3 prerequisites) | Yes (schema envelope) | Per-Discord integration |
| Cross-plane fail-open codification (F13 durable pattern) | Yes (xx99 §5 canonical statement) | — |
| Seam boundary test coverage (F18) | Yes (T2 R.EVENTS.SEAM-BOUNDARY-TEST-COVERAGE) | — |

## 8. Data Ownership and Lifecycle

Per Explore 1 seam model inventory + Explore 4 seam matrix synthesis:

- **EventBus substrate** — WRITERS: 7 publisher wrappers (`event_bus.py:539-703`) — 3 verified callers (scoring_dispatcher × 2 sites + hitl_validation × 2 sites). READERS: 5 consumer tasks (`tasks.py:4726-4874`) — 4 dormant per S2001 F9 + F14. Lifecycle: MAXLEN=10000 per stream + MAXLEN=1000 DLQ per S2001 §4; age-based retention NOT configured; oldest events silently truncated past cap.
- **WebSocket substrate** — WRITERS: ~40 `channel_layer.group_send` call sites per S2003 §10.5. READERS: 33+ consumer classes across `core/consumers*.py`. Lifecycle: ephemeral (session lifetime) per S2003 §4.
- **CeleryTaskEvent** — WRITER: signal handlers in `core/celery_telemetry.py` (task_prerun + task_postrun). READERS: PA `celery_task_history` tool + Grafana + S1245 `audit_celery_zero_fire`. Lifecycle: 30-day TTL per S1223.
- **LLMCallEvent** — WRITER: `LLMCallWrapper` context manager (S1098). READERS: watchdog (S1219) + cost tracking + reliability metrics. Lifecycle: 30-day TTL per S1219 PR #2520.
- **OpsRunEvent** — WRITERS: MissionRunner (dominant) + OpsRunTracker helper + auxiliary Rigby-adjacent writers. READERS: `derive_status` + `views_diagnostics.py:155` + `views_employee_api.py` + Sports/bug_triage triage window. Lifecycle: NO default TTL (audit-forever posture for Class-1 per S2002 §17.3).
- **ToolCallRecord** — WRITER: `ToolDispatcher.dispatch_tool_call` (S861). READERS: PA `tool_call_history` tool + provenance dashboards. Lifecycle: 30-day TTL per S861.
- **Fleet Events (F13 seventh-substrate candidate)** — WRITERS: 1 verified caller (`signal_aggregation_service.py:801`); classification pending Chris-gate. READERS: unaudited; ORM query + Redis pub/sub subscribers. Lifecycle: ORM-row persistence + Redis pub/sub fire-and-forget.

**Key ownership observations:**

- **EventBus is asymmetric** — write-side dominated by Intelligence services (scoring_dispatcher + hitl_validation); read-side dormant per S2001 F9 propagated to F14 above. Producer STRONG × Consumer DORMANT → WEAK aggregate per S1274 §12.1 pair classification.
- **OpsRunEvent has strong write-only ownership** — MissionRunner (Employee OS) writes; 3 adjacent-plane readers (Sports/bug_triage + API/diagnostics + API/employee_api derive_status). No adjacent plane writes to OpsRunEvent from outside Employee OS. No adjacent-plane FKs point at OpsRunEvent. Per Explore 1 finding + S1904 §4 finding E3 inherited: "No backward refs." Read/write asymmetry architecturally healthy.
- **Fleet Events (F13) has strong write-only ownership at HEAD** — Memory F.a single caller writes; readers unaudited (F13 post-arc investigation).
- **`correlation_id` is envelope-field-design-ready but unpopulated at runtime** per F15 (extends S2001 §8 finding). No lifecycle discipline for cross-substrate reconstruction.
- **`event_id` equality invariant** — NOT ENFORCED at HEAD per F17. When implemented per T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER, canonical + mirror pair MUST share `event_id`.

## 9. Integrations With Other Domains

Cross-domain integration map for event / integration ↔ each adjacent plane. Cross-referenced to `docs/research/platform/cross_domain_integration_audit.md` §2.

Per Explore 4 seam matrix + Explore 5 doc inventory:

| Adjacent domain | Integration strength (S1274 pair classification) | Direction | Notes |
|---|---|---|---|
| Memory (1300) | **WEAK** | Bidirectional (implicit) | Fleet Events single emission at signal_aggregation; writer plane no-event-emission; F13 substrate classification pending |
| Sports (1500) | **WEAK** | Unidirectional (WebSocket-only) | 2 group_send emission sites; zero EventBus adoption for outcome/model events per S2001 F3/F4 zero-caller |
| Content (1600) | **MISSING** | Would-be bidirectional | Zero-emission-at-boundary; DeliverableEvent design-only per S1699 §7.4 follow-on |
| Observability (1700) | **STRONG** (write-owner) / **N/A** (Class-2 telemetry) | Write-only ownership of 4 telemetry substrates; NOT push-with-consumers | Concern-boundary CLEAN per P3; canonical write-ownership of OpsRunEvent/CeleryTaskEvent/LLMCallEvent/ToolCallRecord; zero EventBus adoption despite F5 SYSTEM_ALERT natural home |
| HAI (1800) | **MISSING** | Would-be bidirectional | Zero-emission-at-boundary at 4 candidate transitions per S2002 §7; design-complete per §7.9 canonical + mirror; runtime-scaffolding |
| Authority Enforcement (1900) | **WEAK** (single-substrate) | Unidirectional | 1 OpsRunEvent emission (AUTHORITY_CONTRACT_OBSERVED); canonical + mirror shape not applied; F.PER-USER-AUTHORITY 3 events design-only |
| Employee OS | **STRONG** (write-owner) / **MISSING** (canonical + mirror) | Bidirectional (OpsRunEvent write-only from MissionRunner) | Dominant OpsRunEvent write-owner + is Class-1 mirror-substrate site per S2003 §10.3.1; canonical + mirror wiring design-only |
| Frontend | **DELEGATED** (upstream WebSocket receive) | Read-only | All emission at Django consumer/service layer |
| API | **WEAK** | Bidirectional | 4 emission sites (2 EventBus + 2 WebSocket) across ~209-view surface; Boundary 1 auth zero emission; 209-view distributed emission-gap |
| Discord | **STRUCTURAL-DROP** | Notification sink only | S1903 Q8 3 upstream prerequisites (inherits S1904 F8); zero command-dispatch emission; downstream notification-sink from EventBus handlers only |

**Cross-domain integration count roll-up:** 3 WEAK + 2 MISSING + 1 INTENTIONAL_ISLAND (none observed) + 1 DELEGATED + 2 STRONG (Observability + Employee OS as write-owners) + 1 STRUCTURAL-DROP. Zero fully STABLE integrations at HEAD.

**Cross-arc integration deltas from S1274 cross_domain_integration_audit.md §2:**

- **Memory F.a Fleet Events emission at `:801`** was NOT surfaced in cross_domain_integration_audit.md §2.2 Signal→Memory row at S1274 baseline. F13 discovery adds this integration.
- **Sports F.b WebSocket-only pattern** at consumers_sports.py was noted as STRONG for UI broadcast but not analyzed for canonical substrate selection per S2003 §10.5 D4.
- **Employee OS OpsRunEvent write-ownership** is present in S1274 baseline but canonical + mirror shape per S2003 §10.3.1 is post-S1274.
- **S1904 F5 Employee OS design-only status** confirmed to propagate to event / integration seam per §14.3.2.

## 10. Event Flows

Per Explore 3 event synthesis:

- **`AUTHORITY_CONTRACT_OBSERVED` event** (S1264 warn-mode label per S1902 D89 dependency) — EMITTER: `MissionRunner._emit_authority_contract_event()` @ `core/employees/mission_runner.py:835-900`. `AUTHORITY_CONTRACT_SCHEMA_VERSION = 1`. Substrate: OpsRunEvent (F.f + F.g). CONSUMERS at HEAD: test suite only (`test_mission_runner_authority_warn_mode_s1264.py`). ZERO production consumers per Explore 3. All 3 production mission factories (rigby, platform_auditor, chief_of_staff) emit per mission.
- **HAI decide event** — EMITTER: PA tool dispatcher on `human_decisions_tool.action='decide'` per `td_handlers_agents.py`. CONSUMERS: `boardroom_ml_service.py` (reads HumanAttentionItem post-decision). Substrate: NONE at HEAD (S2002 §7.9 canonical + mirror design-only per F5).
- **`OPPORTUNITY_SCORED` event** (S2001 §10.2 canonical) — EMITTER: `scoring_dispatcher._score_realtime` + `_score_batch` @ `core/services/scoring_dispatcher.py:282,480`. Substrate: EventBus. CONSUMERS: dormant `validation_workers` per S2001 F9.
- **`VALIDATION_REQUIRED` + `VALIDATION_DECIDED` events** (S2001 §10.2 canonical) — EMITTER: `hitl_validation._publish_validation_event` @ `core/services/hitl_validation.py:30,38`. Substrate: EventBus. CONSUMERS: dormant `analytics_workers` per S2001 F9 + Discord notification sink at `event_handlers.py:216-231`.
- **Fleet Events `signal.cluster_promoted` event (F13)** — EMITTER: `signal_aggregation_service._maybe_emit_cluster_promoted` @ `:801`. Substrate: Fleet Events (potential seventh substrate). CONSUMERS: unaudited at HEAD.
- **WebSocket `odds_updated` + `league_updated` events** — EMITTER: `SportsUpdatesConsumer.handle_force_odds_update` @ `core/consumers_sports.py:106,127`. Substrate: WebSocket group_send. CONSUMERS: Frontend `/betting` route.
- **WebSocket `inbox.new_message` + `inbox.thread_created` events** — EMITTER: `InboxView.post` @ `core/views_inbox.py:305-310,331-335`. Substrate: WebSocket group_send. CONSUMERS: Frontend `/inbox` route.
- **CeleryTaskEvent lifecycle events** (implicit) — EMITTER: `celery_telemetry.on_task_prerun` / `on_task_postrun`. Substrate: CeleryTaskEvent (Observability F.d). CONSUMERS: PA `celery_task_history` tool + `audit_celery_zero_fire` (S1245).
- **LLMCallEvent invocation events** (implicit) — EMITTER: `LLMCallWrapper.__enter__` / `__exit__` (S1098). Substrate: LLMCallEvent (Observability F.d). CONSUMERS: watchdog (S1219) + cost tracking.
- **ToolCallRecord dispatch events** (implicit) — EMITTER: `ToolDispatcher.dispatch_tool_call` (S861). Substrate: ToolCallRecord (Observability F.d). CONSUMERS: PA `tool_call_history` tool.
- **OpsRunEvent mission-step events** — EMITTER: `MissionRunner._emit_event` (15+ sites) + `OpsRunTracker.emit` + auxiliary Rigby-adjacent. Substrate: OpsRunEvent (Observability F.d + Employee OS F.g). CONSUMERS: `derive_status` + diagnostics + employee_api readers.

**Planned events NOT YET IMPLEMENTED (per S2002 §7 + §10 + §20.9 + parent §5.3 P3 handoff to P4 close):**

- **`HAI_DECISION_RECORDED` + `HAI_VERIFICATION_RECORDED` + `HAI_AUTO_APPROVED` + `HAI_AUTO_ESCALATED`** — canonical EventBus + mirror OpsRunEvent per S2002 §7.9 + S2003 §10.3.1 + §10.4. Design-complete + runtime-scaffolding at S2004 close.
- **`AUTHORITY_CHECK_EVALUATED` + `AUTHORITY_DECISION_OVERRIDDEN` + `AUTHORITY_POLICY_BOUND_TO_USER`** — canonical EventBus + mirror OpsRunEvent per S2002 §20.9. Design-complete + runtime-scaffolding.
- **`BRIDGE_DISPATCHED` + `NON_BRIDGE_LEARNING_WRITE` + `CROSS_DOMAIN_LEARNING_ROUTED` + `EXTERNAL_SIGNAL_INGESTED` + `SHADOW_SERVICE_INVOKED`** — six-plane learning-surface events per S2002 §10. Class-2 canonical-only per S2003 §10.3.3. Design-complete + runtime-scaffolding.
- **`AUTHORITY_CONTRACT_VIOLATED`** — planned per S1902 §19 T1. Would emit when authority PROHIBITED level blocks dispatch under `enforce_authority_mode = 'enforce'` post-T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS landing. Anticipated consumers across all 10 planes.
- **KillSwitch reader events** (future D94 per S1903 §7.4.1) — planned rate-limited `logger.warning` with prefix `killswitch_missed_reader:<boundary>`. 4 REQUIRED insertion boundaries per S1903 D94. Not wired at HEAD; T2 slot.

**Event-flow gap:** ZERO substrate emission at 4 of 10 plane boundaries (Memory writer-plane + Content boundary + HAI four candidate transitions + Discord command-dispatch). Consumer-dormancy propagated across all 10 planes per F14 (4 of 5 EventBus consumer tasks unscheduled).

## 11. Existing Documentation

Per Explore 5 comprehensive doc inventory:

**Per-plane doc coverage matrix (classification: NONE / LIGHT / MODERATE / DEEP / CANONICAL):**

| Plane | Coverage | Existing docs | Gap list |
|---|---|---|---|
| Memory (1300) | LIGHT | S1301-S1305 child audits; S1399 xx99; cross_domain_integration_audit §2.2; `docs/topics/spider-network.md` signal aggregation flow | Fleet Events (F13) emission unmentioned; writer-plane no-event-emission pattern unmentioned; F13 substrate classification pending |
| Sports (1500) | NONE | S1501-S1506; S1599; cross_domain_integration_audit §2.2 (Sports→Signal MISSING) | Zero seam-focused docs; WebSocket-only pattern unmentioned; canonical substrate assignment for outcome/model events unmentioned |
| Content (1600) | LIGHT | S1601-S1606; S1699 §7.4; EVENT_SYSTEM_INVENTORY §1.4 DeliverableEvent | Zero-emission-at-boundary pattern unmentioned; DeliverableEvent adoption status vs design-only unmentioned; duplicate consumer class drift unmentioned |
| Observability (1700) | NONE | `docs/topics/infrastructure.md` (9 body systems); `docs/topics/celery-workers.md`; PLATFORM_INVENTORY runtime block | Zero seam-focused docs; 4-substrate write-ownership pattern unmentioned; F5 SYSTEM_ALERT natural-home gap unmentioned; body-system state-change event contract unmentioned |
| HAI (1800) | LIGHT | S1801-S1806; S1899 §8 T-tier; EMPLOYEE_OS_PRIMITIVES §1 row 22 `/ws/system-events/` 9 typed events (does NOT yet carry 'DM arrived' event) | S2002 §7 four candidate transitions design vs runtime unmentioned; PAConversationConsumer + PersonalAssistantV2 + AssistantChat treat WebSocket authoritative unmentioned |
| Authority Enforcement (1900) | LIGHT | S1901-S1904; EMPLOYEE_OS_PRIMITIVES §1 rows 2, 17 (JobContract.authority + GovernanceState + KillSwitch) | AUTHORITY_CONTRACT_OBSERVED emission at Boundary 5 canonical + mirror shape unmentioned; F.PER-USER-AUTHORITY three events design-only unmentioned |
| Employee OS | LIGHT | S1268-S1272 research; EMPLOYEE_OS_PRIMITIVES.md §3 lifecycle diagram; EVENT_SYSTEM_INVENTORY §1.5 OpsRunEvent | OpsRunEvent canonical + mirror site status unmentioned; `mirror_of` tag + `event_id` equality invariants unmentioned; 7 WebSocket consumer classes' relationship to substrate contract unmentioned |
| Frontend | NONE | `docs/topics/frontend.md` distributed | Zero seam-focused docs; WebSocket consumer subscription paths + real-time refresh triggers unmentioned; ui.render_hint receiver logic unmentioned |
| API | LIGHT | docs/API_PATH_POLICY.md; cross_domain_integration_audit §4.2 (9 OpenAI imports bypass factory) | Boundary 1 auth-event emission unmentioned; ~40 group_send call site distribution unmentioned; hitl_validation.py 2 EventBus emission sites documented in S2001 but not in API_PATH_POLICY |
| Discord | LIGHT | docs/DISCORD_INTEGRATION.md; cross_domain_integration_audit §1 (11,677-line god-service) | Command-dispatch zero-emission unmentioned; notification-sink downstream pattern unmentioned; S1903 Q8 3-prerequisite unblock trace |

**Aggregate:** **2 NONE (Sports + Observability + Frontend counted as delegated/NONE) + 6-7 LIGHT (Memory + Content + HAI + Authority + Employee OS + API + Discord) + 0 MODERATE + 0 DEEP + 0 CANONICAL across 10 planes.**

Corrected: **2 NONE (Sports + Observability) + 1 CLEAN-delegated (Frontend) + 7 LIGHT (Memory + Content + HAI + Authority + Employee OS + API + Discord)**.

**Recommended xx99 §7 anchor-update batch scope (queued for xx99):** 10 new `docs/topics/*-event-integration.md` first-inventory landings, OR targeted anchor-refresh at existing per-plane topic docs + PLATFORM_INVENTORY.md §Event / Integration Architecture seam sub-section + PLATFORM_WHAT_IT_IS.md §7 subsection "Event/Integration Architecture Maturity" + EVENT_SYSTEM_INVENTORY.md new §13 "Event/Integration Seam Audit Results (S2004 Group 2000+ P4)".

**Event / integration-plane-side doc inventory (per Explore 5):**

- `PLATFORM_WHAT_IT_IS.md` — Layer 2 Signal Intelligence paragraph does not mention Fleet Events emission or F13 substrate discovery; Layer 3 Agents paragraph does not mention OpsRunEvent write-ownership; no §7 subsection for event / integration architecture.
- `PLATFORM_INVENTORY.md` — event / integration-plane runtime block: 8 EventBus streams + 1 DLQ + 3 consumer groups; source: S2001. No adjacent-plane emission counts. No F13 Fleet Events row.
- `EVENT_SYSTEM_INVENTORY.md` — §1.1-1.10 enumerates 14+ event-shaped models; §1.5 OpsRunEvent as MissionRun timeline primitive; §1.4 DeliverableEvent as best-shaped emitter. No §13 or seam-audit section.
- `EMPLOYEE_OS_PRIMITIVES.md` — §1 rows 3-5 OpsRun/OpsRunEvent/emit_mission_verdict as canonical primitives; §3 lifecycle diagram; no adjacent-plane seam mapping.
- `docs/API_PATH_POLICY.md` — path naming conventions; zero event-integration documentation.
- `docs/DISCORD_INTEGRATION.md` — command reference (96 commands); zero EventBus subscription or event-trigger documentation.
- `docs/KNOWLEDGE_PIPELINE.md` — spider → learning → signal flow; mentions signal aggregation but not Fleet Events emission.

## 12. Research Coverage

Per Explore 5 aggregate classification: **LIGHT-to-NONE across all 10 planes for event / integration-seam-focused coverage.** Zero CANONICAL seam docs.

Per-plane per-audit-question research coverage (playbook §12 5-value scale):

| Plane | Research Coverage | Rationale |
|---|---|---|
| Memory (1300) | LIGHT | S1399 §7 anchor-updates do not cite Fleet Events emission (F13 discovery post-Explore); findings scattered across S1301-S1305 |
| Sports (1500) | NONE | Zero seam-focused docs; Sports isolated per S1274 v2 "intentional island" framing; WebSocket-only pattern undocumented |
| Content (1600) | LIGHT | S1605 §15 T.15.C1 / T.15.E* deliverable-adjacent findings; no dedicated seam section; DeliverableEvent design-only status per S1699 §7.4 |
| Observability (1700) | NONE | Zero seam-focused docs; 4-substrate write-ownership pattern known but not consolidated; no Group 1700 research arc closed |
| HAI (1800) | LIGHT | S1806 Cat F CONSOLIDATION analog; S1899 §8 T0/Gate queued; no consolidated seam doc for event contract; S2002 §7 four candidate transitions design-complete post-S1806 |
| Authority Enforcement (1900) | LIGHT | S1904 Cat F CONSOLIDATION (event-adjacent findings inherited); no dedicated authority-event topic doc; S1902 §19 T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA queued |
| Employee OS | LIGHT | Authority seam documented in S1268-S1272 + P1/P2/P3; OpsRunEvent canonical + mirror site status design-only per S2003 §10.3.1 |
| Frontend | NONE | Zero seam-focused docs; ui.render_hint receiver logic aspirational per S2003 §10.3.4 D4 |
| API | LIGHT | API_PATH_POLICY.md exists but seam coverage minimal; S2001/S2003 flag Boundaries 18/19/20 as new |
| Discord | LIGHT | S1903 Q8 formal deferral; DISCORD_INTEGRATION.md exists but detailed seam coverage minimal; S1904 F8 STRUCTURAL-DROP inherited |

**Meta-observation:** Group 2000+ P1/P2/P3 produced the deepest event / integration-plane research to date. P4 CONSOLIDATION is the FIRST event / integration-adjacent-seam-focused audit across the arc; xx99 canonical summary will inherit as the first cross-plane synthesis. Consistent with S1904 §12 meta-observation for Group 1900.

## 13. Architecture Maturity

Per Explore 6 §Part A per-plane classification (playbook §12 5-value scale):

| Plane | Maturity | Rationale |
|---|---|---|
| Memory (1300) | EXPERIMENTAL | Fleet Events single emission; writer-plane no-event-emission pattern; F13 substrate classification pending |
| Sports (1500) | PARTIAL | WebSocket path operational (2 emission sites, 8 consumer classes); zero EventBus adoption for outcome/model events; UI-render-hint absent |
| Content (1600) | EXPERIMENTAL | Zero-emission-at-boundary; DeliverableEvent design-only; duplicate consumer class drift |
| Observability (1700) | WORKING | 4-substrate write-ownership operational; concern-boundary CLEAN per P3; zero EventBus adoption despite F5 natural home |
| HAI (1800) | EXPERIMENTAL | Four candidate transitions design-complete per S2002 §7.9; runtime emission ZERO; three WebSocket consumers independent |
| Authority Enforcement (1900) | WORKING | Single-substrate OpsRunEvent emission operational; canonical + mirror shape not applied; F.PER-USER-AUTHORITY design-only |
| Employee OS | WORKING | Dominant OpsRunEvent write-ownership operational; canonical + mirror shape design-only; 7 WebSocket consumers independent |
| Frontend | EXPERIMENTAL (CLEAN-delegated) | Seam contract undocumented but genuinely delegated to upstream; UI-render-hint contract not implemented |
| API | PARTIAL | 4 emission sites verified (2 EventBus + 2 WebSocket) across ~209-view surface; Boundary 1 auth zero emission; 209-view distributed emission-gap |
| Discord | EXPERIMENTAL | Dispatch operational; substrate integration absent; S1903 Q8 3 prerequisites; notification-sink brittle |

**Distribution:** 4 EXPERIMENTAL (Memory + Content + HAI + Discord) + 1 EXPERIMENTAL-CLEAN-delegated (Frontend) + 2 PARTIAL (Sports + API) + 3 WORKING (Observability + Authority + Employee OS) + 0 STABLE + 0 CANONICAL.

**Arc-wide seam maturity verdict:** **PARTIAL with EXPERIMENTAL emission.** Consistent with S1904 arc-wide finding (PARTIAL with EXPERIMENTAL enforcement) — Event / Integration Architecture is design-complete, runtime-scaffolding. No arc-close STABLE rating possible without T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING (F5 severity) + T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER (F17 severity) + T1 R.EVENTS.SPIDER-DATA-SUBSTRATE-CONSOLIDATION (F11 severity) + T2 R.EVENTS.SEAM-BOUNDARY-TEST-COVERAGE (F18 severity).

## 14. Known Drift

### 14.1 Inherited drifts from P1/P2/P3

**From P1 (S2001 §14):**
- F8 dual-mechanism drift (Redis Streams + Redis pub/sub co-existing) — inherited into F11 spider-data three-substrate case per S2003 §14.1 codification.
- F9 consumer beat-dormancy (4 of 5 tasks unscheduled) — inherited into F14 above.
- F11 spider-data three-substrate drift SIGN-expanded — inherited into F17 P1 composition-consistency register failure case (b) + T1 R.EVENTS.SPIDER-DATA-SUBSTRATE-CONSOLIDATION.
- F14 handler-failure retry loop (no give-up counter) + F15 no DLQ reader — inherited into §15 debt matrix.
- F17 registration-surface gap (ConsumerInfo dataclass decorative) + F18 handler decorativeness — inherited into §5.1 decorative-structure caveat.
- S2001 §8 "all wrappers omit correlation_id" — inherited into F15 extension across all 10 planes.

**From P2 (S2002 §14):**
- §14.1 HAI event contract shape design-complete + runtime-scaffolding — inherited into F5 zero-emission-at-HAI-boundary above.
- §17.1 consumer registry per-event registration format design-only — inherited into F14 above.
- §17.3 two-class retention posture (Class-1 audit-forever + Class-2 bounded) — inherited into §10 event flow classification.
- §20.9 F.PER-USER-AUTHORITY-MECHANISM three-event contract semantics design-only — inherited into F6 above.

**From P3 (S2003 §14):**
- §14.1 F11 spider-data three-substrate codification — inherited into F11 above (F13 flags Fleet Events as similar-shape discovery).
- §14.3 double-emission detector binding via `mirror_of` tag — inherited into F17 above (invariant unenforced at HEAD).
- §19.1.6 F.SYMBOL-MAPPING-EMISSION-VERIFICATION T-slot — inherited into §19 T-tier queue.
- §19.10.4 F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN adoption trigger — inherited into §19 T-tier queue.

**Inherited-into-P4 status:** All above drifts remain queued for xx99 §7 anchor-update batch. P4 does not re-verify inherited drifts per playbook §14 MC-1 discipline (P4 verifies SEAMS, not parent arcs' internal correctness). Exception: F11 SIGN-expanded case (three-substrate spider-data) intersects with F13 (Fleet Events seventh substrate) — treated as complementary evidence per §14.3.1 investigation.

### 14.2 Net-new drifts caught by P4 verifier-loop (pre-Explore)

**None caught pre-Explore.** Parent §5.4 P4 checks table + P1/P2/P3 inherited claims all verified at HEAD `7fc1bc1c` at pre-Explore. All 10 adjacent-plane entry-point classes confirmed to exist. This is consistent with Group 1900 P4 pattern (S1904 §14.2 also caught zero pre-Explore drifts against parent §5.4; verifier-loop pre-Explore for CONSOLIDATION shape validates seam-inventory rather than parent-claim-vs-runtime).

### 14.3 Net-new drifts caught by P4 verifier-loop (post-Explore)

**Four drifts caught during Explore-return synthesis:**

- **§14.3.1 F13 Fleet Events discovered as POTENTIAL SEVENTH SUBSTRATE — RATIFIED AS INTENTIONAL SIDECAR per Chris D-verdict at S2004 close 2026-07-04.** Explore 1 initially found `signal_aggregation_service.py:776,801` calling `emit_event(app_slug, event_type='signal.cluster_promoted', payload=...)` from `core.services.fleet_events`. Post-Explore verifier confirmed `core/services/fleet_events.py` exists at 285 LOC / 9,624 bytes with `emit_event()` public API + `FleetEvent` ORM model + Redis pub/sub per-app channel. Architecturally a HYBRID: (a) push-with-consumers via Redis pub/sub per-app-channel (like WebSocket), AND (b) durable-audit via FleetEvent ORM row (like OpsRunEvent). Does NOT map cleanly to any of the six S2003 §10.1 substrate rows. Three classification options presented to Chris-gate (Rigby SIGN cycle 1 Q1 STRENGTHEN — three-option register kept; "intentional sidecar" is materially different governance outcome): (a) SANCTIONED CLASS-2 SUBSTRATE (add row to S2003 §10.1 substrate inventory + define concern-boundary per §10.3.5); (b) DRIFT ANALOG TO F11 spider-data (Fleet Events overlaps with EventBus for cross-service backend coordination; canonical-substrate migration to EventBus + deprecation of Fleet Events); (c) INTENTIONAL SIDECAR (Fleet Events is for cross-application fleet coordination and stays sanctioned as a separate substrate; S2003 §10.1 six-substrate scope was intra-application). **Chris D-verdict at S2004 close = option (c) INTENTIONAL SIDECAR.** Rationale: `emit_event(app_slug=...)` API signature is already scoped per-app-slug; parallel purpose to EventBus is complementary (cross-application fleet coordination across u-d-b × mentorforge × character-os), not overlap. **ADR RATIFIED at S2004 close.** S2099 §7 anchor-update batch will: (i) add Fleet Events as row #7 in S2003 §10.1 substrate inventory table with `Contract scope = "Canonical for cross-application fleet coordination (u-d-b × mentorforge × character-os); intra-application coordination remains EventBus per S2003 §10.4 substrate × event mapping"`; (ii) define concern-boundary per §10.3.5 (semantic tuple + adopter obligations); (iii) freeze on new intra-application producers/consumers stays per Q1 Rigby SIGN fold (existing sole-caller usage from `signal_aggregation_service.py:801` may continue); onboarding new cross-application producers/consumers permitted post-S2099 anchor-update landing. **Severity: HIGH cross-plane (substrate inventory anchor update depends on ratified classification; blocks xx99 §7 anchor-update batch execution until landing).** Meta-observation: F13 substrate-inventory-completeness verifier discovery pattern successful — CONSOLIDATION-audit substrate-existence grep against prior arc's substrate inventory table caught Fleet Events pre-close; codification candidate for playbook v3 §14 substrate-completeness discipline addition.

- **§14.3.2 HAI four candidate transition emission ABSENT at HEAD confirming S2002 §7.9 design-only status.** Post-Explore verifier grep `publish_hai_*|OpsRunEvent.objects.create.*mirror_of|channel_layer.group_send.*hai_` across `core/services/human_attention_lifecycle.py:440-656` (auto-approve orchestration trigger body) returned ZERO matches. CONFIRMS the four HAI candidate transitions (record_decision + record_verification + auto_approve + auto_escalate per S2002 §7) fire ZERO substrate emission at HEAD. **This is NOT a P2 design drift** — S2002 §7.9 explicitly queued canonical + mirror wiring to post-arc T1 per S2002 §19. It is a **design-vs-runtime gap explicitly documented in the T-tier queue**. Matches S1904 §14.3.3 pattern (Authority Enforcement `enforce_authority_mode` field design-only). Fold: reference this gap explicitly in F5 (§1) and §5.4. **Severity: HIGH structural (blocks S2002 §7.9 canonical + mirror composition contract from operating at runtime). Not a NEW drift; queued item explicit-verification confirmation. Recorded for xx99 §5 canonical seam statement consumption.**

- **§14.3.3 `ui.render_hint` envelope pattern absent EVERYWHERE — S2003 §10.3.4 D4 contract aspirational at S2004 close.** Post-Explore verifier grep `ui\.render_hint|render_hint` across `core/consumers*.py` + `frontend/src/` returned ZERO matches. All ~40 `channel_layer.group_send` call sites use bare `type: <string>` fields. All 33+ WebSocket consumer classes treat WebSocket state as authoritative. Retrofit is post-arc T2. **Severity: HIGH cross-plane (S2003 §10.3.4 D4 contract violation candidates across 7 planes: Sports + Content + Memory + HAI + Authority + Employee OS + Frontend — all treat WebSocket as authoritative without external verification). Queued for T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT with explicit scope enumeration per Rigby SIGN cycle 1 Q6 FOLD: (a) retrofit ~40 emission sites + (b) retrofit 33+ consumer classes to enforce `type=ui.render_hint` + (c) add code-review anti-pattern + lint/grep check; validate via 10-plane × 3-scenario matrix.**

- **§14.3.4 `mirror_of` tag + `event_id` equality invariant unenforced across all dual-emission cases.** Post-Explore verifier grep `mirror_of` across `core/` returned ZERO matches; grep `event_id=<explicit>` on OpsRunEvent write sites returned ZERO explicit event_id assignments. S2003 §10.3.1 canonical + mirror invariants (equal `event_id` + `mirror_of` tag on mirror substrate + `transaction.on_commit` ordering) are unenforced at HEAD. Two observed dual-/multi-emission cases both FAIL: (a) HAI Class-1 governance canonical + mirror design (design-only, not implemented per §14.3.2); (b) F11 spider-data three-substrate drift (three independent substrates with no `event_id` unification). **Severity: HIGH cross-plane (composition contract consistency invariants unenforced at HEAD — blocks §14.3 double-emission detector post-arc wiring). Queued for T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER.**

### 14.4 Cross-arc drift observations

Per Explore 5 doc coverage inventory, Group 2000+ P4 identifies the following cross-arc drift observations that xx99 §7 should batch:

- **Memory (Group 1300):** Fleet Events emission at `signal_aggregation_service.py:801` is not documented in `docs/topics/spider-network.md` (which owns signal-aggregation topic) or S1399 xx99 §7 anchor-updates. F13 discovery post-Explore.
- **Sports (Group 1500):** S1599 D59 posture-decision deferral persists; WebSocket-only emission pattern + zero-EventBus-adoption for outcome/model events not documented.
- **Content (Group 1600):** S1605 T.15.E2 CRITICAL finding "REST endpoints ZERO auth decorator" inherits into F9 API seam classification; DeliverableEvent adoption status vs design-only unmentioned in S1699 xx99.
- **Observability (Group 1700):** No Group 1700 research arc closed at HEAD; 4-substrate write-ownership pattern known but not consolidated as topic doc.
- **HAI (Group 1800):** S1899 §8 T0/Gate 6-item bundle (including R.HAI.SOURCE-KIND-ENUM-ADR) remains queued; overlaps with F5 four candidate transition design-vs-runtime status.
- **Authority Enforcement (Group 1900):** S1904 canonical + mirror shape not applied to `AUTHORITY_CONTRACT_OBSERVED` emission per §14.3.4; S1902 §19 T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA queued.
- **Employee OS:** OpsRunEvent canonical + mirror site status per S2003 §10.3.1 is DESIGN-ONLY at HEAD; runtime landing gated on T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER.
- **CLAUDE.md `Live Counts` table** — no rows for Event/Integration Architecture seam maturity (0 CANONICAL / 0 DEEP / 0 MODERATE / 7 LIGHT / 2 NONE / 1 CLEAN-delegated); xx99 §7 anchor-update should add.

## 15. Known Technical Debt

Per Explore 6 §Part C per-plane seam debt matrix:

| Plane | Debt | Severity | Rationale |
|---|---|---|---|
| Memory | Fleet Events emission at signal_aggregation_service.py:801 undocumented | HIGH | Cross-plane emission via undocumented seventh substrate; blocks §5 canonical seam statement per F13 |
| Memory | Writer-plane zero-event-emission at AgentLearning/UserAgentLearning writes | MEDIUM | Cross-arc handoff to S1300 T3 R.MEMORY.WRITER-PLANE-EVENT-EMISSION-DOC |
| Sports | Zero EventBus adoption for OUTCOME_RECORDED + MODEL_TRAINED events | HIGH | S2001 F3+F4 zero-caller propagates to Sports plane; T3 R.SPORTS.OUTCOME-RECORDED-EMIT |
| Sports | 8 WebSocket consumer classes without `ui.render_hint` envelope | MEDIUM | F16 durable pattern; T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT |
| Content | Zero-emission-at-boundary across PublishGate + DeliverableEvent design-only | CRITICAL | Content pipeline lacks event emission at deliverable status transitions; blocks event-driven learning + notification workflows; T1 R.CONTENT.DELIVERABLE-EVENT-EMISSION-WIRING |
| Content | Duplicate consumer class names (content/consumers.py vs core/consumers_base.py) | MEDIUM | Explore 2 finding; T2 R.EVENTS.CONTENT-CONSUMER-CLASS-DEDUP |
| Observability | Zero EventBus adoption for SYSTEM_ALERT despite F5 wrapper existing (S2001 F5) | HIGH | Body-system state-change events not emitted; observability alerts fire zero substrate emission; T2 R.EVENTS.OBSERVABILITY-SYSTEM-ALERT-EMISSION |
| Observability | Body-system state-change event contract undesigned | MEDIUM | 9 body systems monitored by run_all_systems_scan without event emission; T3 R.OBSERVABILITY.BODY-SYSTEM-EVENT-CONTRACT |
| HAI | Four candidate transitions ZERO emission at HEAD | HIGH *(Rigby Q2 FOLD: staged-rollout gap; promote to CRITICAL only if any production consumer assumes HAI emissions exist today)* | S2002 §7.9 canonical + mirror design-only; blocks event-emission contract runtime landing; T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING (per Q10 SIGN fold: T1 #2 — first major adopter; may start in parallel but cannot close without R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER at T1 #1 compliance) |
| HAI | Three WebSocket consumers treat WebSocket as authoritative (no ui.render_hint) | MEDIUM | F16 durable pattern; T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT |
| Authority Enforcement | Canonical + mirror shape not applied to AUTHORITY_CONTRACT_OBSERVED emission | HIGH | S2003 §10.3.1 canonical + mirror invariants unenforced for Boundary 5 emission; F17 evidence; T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER |
| Authority Enforcement | AUTHORITY_CONTRACT_VIOLATED event NOT implemented | HIGH | S1902 §19 T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA inherited; blocks enforcement-mode landing |
| Authority Enforcement | F.PER-USER-AUTHORITY three events design-only | HIGH | S2002 §20.9 canonical + REQUIRED mirror per S2003 §10.4 design-only; T1 R.EVENTS.PER-USER-AUTHORITY-EMISSION-WIRING |
| Employee OS | Canonical + mirror wiring design-only on OpsRunEvent | HIGH | S2003 §10.3.1 mirror-substrate site status DESIGN-ONLY; F17 evidence; T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER |
| Employee OS | 7 WebSocket consumer classes independent of substrate contract | MEDIUM | F16 durable pattern + no EventBus co-emission for agent + project status; T2 R.EVENTS.EMPLOYEE-OS-EVENTBUS-CANONICAL-ADOPTION |
| API | Boundary 1 auth-event emission absent | HIGH | Zero substrate emission on authentication events; T2 R.EVENTS.API-BOUNDARY-1-AUTH-EMISSION |
| API | 209-view distributed emission-gap | HIGH | Per Explore 3 sample zero direct view-body emission (correct per separation of concerns) but no service-layer emission audit across all views; T3 R.EVENTS.API-LAYER-EMISSION-INSTRUMENTATION |
| API | ~40 group_send call sites without envelope carriage | MEDIUM | F16 durable pattern; T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT |
| Discord | Zero substrate emission across 96 commands + 25 Cogs | CRITICAL | S1903 Q8 3 upstream prerequisites; T2 R.EVENTS.DISCORD-COMMAND-DISPATCH-EMISSION-INSTRUMENTATION (inherits S1904 F8 STRUCTURAL-DROP) |
| Discord | Notification-sink brittle to import failure | MEDIUM | ImportError fail-open at `event_handlers.py:216-231, :326-339, :370-383` per S1103c; T3 R.EVENTS.DISCORD-NOTIFICATION-SINK-HARDENING |
| Frontend | Zero `ui.render_hint` receiver logic implementation | MEDIUM | Aspirational per S2003 §10.3.4 D4; T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT |
| Cross-plane | Zero seam-boundary test coverage | HIGH | F18 durable-across-P1-P2-P3-P4; T2 R.EVENTS.SEAM-BOUNDARY-TEST-COVERAGE |
| Cross-plane | `correlation_id` runtime propagation absent across all 10 planes | HIGH | F15 durable pattern (extends S2001 §8); T3 R.EVENTS.CORRELATION-ID-RUNTIME-ADOPTION |
| Cross-plane | Consumer beat-dormancy across all planes (4 of 5 EventBus tasks) | HIGH | F14 durable pattern (extends S2001 F9); T2 R.EVENTS.CONSUMER-BEAT-ENROLLMENT |
| Cross-plane | Fleet Events substrate classification undecided | HIGH | F13 discovery post-Explore; blocks S2099 §7 anchor-update; R1 Fleet Events ADR (Chris-gate) |
| Cross-plane | Fail-open-emission posture unowned across seams | MEDIUM | F13 durable pattern; codification pending xx99 §5 canonical statement |

**Debt severity roll-up:** 3 CRITICAL + 12 HIGH + 8 MEDIUM + 0 LOW = 23 items.

## 16. Boundary Violations

Per Explore 2 + Explore 3 + Explore 6 boundary-violation catalog (severity-ranked):

**HIGH — HAI zero-emission-at-boundary at four candidate transitions (§14.3.2).** `core/services/human_attention_lifecycle.py:243` decision write fires ZERO substrate emission across all six substrates. Blocks S2002 §7.9 canonical + mirror composition contract from operating at runtime. **Severity HIGH** (four events design-complete + runtime-scaffolding per S2002 §19 T1).

**HIGH — Fleet Events discovered as potential seventh substrate (§14.3.1).** `core/services/fleet_events.py` (285 LOC) emit_event() at `signal_aggregation_service.py:801` — substrate not enumerated in S2003 §10.1 six-substrate inventory. Classification pending Chris-gate. **Severity HIGH** (substrate inventory + composition contract shape depends on classification).

**HIGH — `mirror_of` tag + `event_id` equality invariant unenforced (§14.3.4).** S2003 §10.3.1 canonical + mirror invariants unenforced at HEAD across two observed dual-/multi-emission cases (HAI design-only + F11 spider-data drift). **Severity HIGH** (composition contract consistency invariants unenforced; blocks §14.3 double-emission detector post-arc wiring).

**HIGH — Content pipeline authority contract absence.** `core/services/content_deliberation_runner.py` PublishGate + REST endpoints emit ZERO events across all substrates; DeliverableEvent design-only per S1699 §7.4 follow-on. Deliverable status transitions fire no substrate emission. **Severity HIGH** (event-driven learning + notification workflows blocked).

**HIGH — API Boundary 1 auth-event emission absent.** `core/auth_middleware.py:563-681` authenticates but emits ZERO substrate events on auth transitions. Per S1605 T.15.E2 CRITICAL finding "REST endpoints ZERO auth decorator" propagates to F9 API seam classification. **Severity HIGH** (auth observability + cross-substrate reconstruction gap).

**MEDIUM — WebSocket UI-render-hint envelope absent everywhere (§14.3.3).** 33+ WebSocket consumer classes; ~40 `channel_layer.group_send` call sites; ZERO `ui.render_hint` envelope usage. S2003 §10.3.4 D4 contract aspirational. **Severity MEDIUM** (contract violation candidates across 7 planes; retrofit is post-arc T2).

**MEDIUM — Content plane duplicate consumer class names.** `content/consumers.py:23,414` (ContentProcessing + ContentAnalytics) vs `core/consumers_base.py:1306,1359` (same names, different group naming). Explore 2: routing gap likely for `content/consumers.py` versions. **Severity MEDIUM** (dormant consumer classes + routing ambiguity).

**MEDIUM — Sports WebSocket-only asymmetric emission pattern.** `core/consumers_sports.py:106,127` emits group_send for odds/league updates; `BettingOutcomeVerifier` + `SportsBettingLearningBridge` emit ZERO events. S2003 §10.4 canonical substrate for OUTCOME_RECORDED not applied. **Severity MEDIUM** (design deferral per S1903 Q3/Q5; documented via cross-arc T3).

**MEDIUM — Discord notification-sink brittle to ImportError.** `event_handlers.py:216-231, :326-339, :370-383` catches ImportError loud per S1103c; notification dispatch fire-and-forget. **Severity MEDIUM** (brittle downstream from EventBus handlers; T3).

**LOW — Duplicate composition semantics across WebSocket + EventBus type fields.** WebSocket `type: <string>` fields and EventBus `event_type` field parallel semantically as canonical domain-event carriers but implement independent policies. No model coupling per F12 HYPOTHESIS DISPROVE. **Severity LOW** (semantic parallel, not architectural violation).

**Total boundary violations at seam:** 5 HIGH + 4 MEDIUM + 1 LOW = 10 categorized.

## 17. Duplicate or Overlapping Systems — Separation-Boundary Posture Register (P4 First-Class Deliverable)

Per CONSOLIDATION shape mirroring S1806 + S1904 §17 pattern — per-plane separation-boundary posture register is P4's load-bearing deliverable for xx99 §5 consumption + xx99 §8 follow-on queue input.

### 17.1 Per-plane separation-boundary posture register

Master posture register (columns per parent §5.4 deliverable spec + Explore 4 §17 first-class shape):

| Plane | Owned-by-2000+ event / integration decisions | Delegated-to-plane event / integration decisions | Shared / composed decisions | Posture verdict | xx99 §5 consumer note |
|---|---|---|---|---|---|
| **Memory (1300)** | Fleet Events classification (F13 Chris-gate) + canonical substrate for signal-emission events | Signal-aggregation filter thresholds + writer-plane implementation (delegated to 1300) | Fleet Events emission at signal_aggregation_service.py:801 (Chris-gate at close) | PERMEABLE-BROKEN | F13 substrate classification is the load-bearing question; xx99 §5 should acknowledge as HIGH structural (Chris-gate resolution feeds §7 anchor updates) |
| **Sports (1500)** | Canonical substrate for OUTCOME_RECORDED + MODEL_TRAINED events (EventBus per S2003 §10.4) + WebSocket UI-render fanout envelope | Arbitrage-fire decision + BettingOutcomeVerifier logic (delegated to 1500) + 8 WebSocket consumer implementations | Sports WebSocket group_send + potential EventBus outcome emission (T3 handoff) | PARTIAL | S2003 §10.4 canonical substrate assignment deferred by S1903 Q3/Q5 designed deferral; T3 handoff to Group 1500 |
| **Content (1600)** | Canonical substrate for DeliverableEvent adoption (EventBus per S2003 §10.4) + PublishGate emission timing | PublishGate quality/novelty verdict (delegated to 1600 gate-owner) + REST endpoint auth decorator (S1605 T.15.E2 inherited) | DeliverableEvent × EventBus adoption (design gap per S1699 §7.4) + zero-emission-at-boundary | PERMEABLE-BROKEN | T1 R.CONTENT.DELIVERABLE-EVENT-EMISSION-WIRING is the primary xx99 §5 blocker for Content seam |
| **Observability (1700)** | Concern-boundary policy per S2003 §10.3.5 + canonical + mirror composition invariants | 4-telemetry-substrate write-ownership (OpsRunEvent + CeleryTaskEvent + LLMCallEvent + ToolCallRecord) + body-system state-change detection | SYSTEM_ALERT emission gap (F5 wrapper natural home; zero adoption) + body-system event contract undesigned | WORKING *(Rigby SIGN cycle 1 Q9 STRENGTHEN fold: Observability plane = WORKING (telemetry substrates correct) + "missing EventBus SYSTEM_ALERT emission" noted as capability gap; promote to PARTIAL only if consumers/UX assume alerts are emitted today)* | Observability is dominant telemetry substrate write-owner + concern-boundary CLEAN per P3; SYSTEM_ALERT + body-system event contract are T2/T3 handoffs |
| **HAI (1800)** | Canonical + mirror wiring for four candidate transitions per S2002 §7.9 + F.PER-USER-AUTHORITY event emission contract per §20.9 | LOW_RISK_SOURCES classification data (delegated to 1800) + auto-approve gate logic + 3 WebSocket consumer implementations | Four candidate transitions design-complete + runtime-scaffolding (T1 handoff) | EXPERIMENTAL | T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING is the primary xx99 §5 blocker (highest T1 priority per F5 severity) |
| **Authority Enforcement (1900)** | AUTHORITY_CONTRACT_OBSERVED canonical + mirror shape per S2003 §10.3.1 + AUTHORITY_CONTRACT_VIOLATED schema per S1902 §19 T1 + F.PER-USER-AUTHORITY three-event contract per S2002 §20.9 | Per-employee `enforce_authority_mode` toggle semantics + KillSwitch enforcement reader implementation (delegated to 1900) | AUTHORITY_CONTRACT_OBSERVED single-substrate emission at Boundary 5 (T1 canonical + mirror wiring) + violation event schema (T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA) | WORKING | Single-substrate emission operational; canonical + mirror + violation event schema T1 handoffs |
| **Employee OS** | Canonical + mirror wiring on OpsRunEvent per S2003 §10.3.1 + composition contract consistency invariants per T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER | OpsRunEvent write-ownership (delegated to 1700 Observability concern-boundary) + 7 WebSocket consumer implementations + MissionRunner step boundary emission | OpsRunEvent Class-1 mirror-substrate site status DESIGN-ONLY at HEAD; T1 canonical + mirror wiring | WORKING | Dominant write-owner + Class-1 mirror-substrate site status is design-only; T1 handoff to composition-consistency register |
| **Frontend** | (no event / integration decisions owned) | Per-route WebSocket subscription + `ui.render_hint` receiver logic implementation (delegated to Frontend) | (no shared decisions; delegated read-only per Rigby Q3(b) fold shape) | **CLEAN (verified read-only)** *(Rigby S1904 Q3(b) fold pattern inherited: Frontend does NOT compute or emit event / integration state; it only RENDERS server-resolved WebSocket state and does not write to any substrate. Verification basis: no browser-initiated substrate write endpoints observed; **if any browser UI ever emits directly to a substrate, Frontend becomes PERMEABLE-BROKEN until an explicit write-boundary contract exists**.)* | No cross-arc T-slot needed; genuinely separated by design |
| **API** | Canonical envelope + Boundary 1 auth-event emission + per-view emission audit (post-arc) | Per-view business logic + REST endpoint auth decorator (delegated to API) + `ui.render_hint` envelope compliance per consumer | Boundary 1 K > M > A precedence per S1904 §17.4 (aspirational) + ~40 group_send envelope compliance | PARTIAL | 209-view distributed emission-gap + Boundary 1 auth-event absence + UI-render-hint retrofit are T2/T3 handoffs |
| **Discord** | Canonical envelope for command-dispatch emission (post-graduation) + notification-sink hardening contract | Per-command action_class labeling + Discord actor identity (delegated to Discord post-graduation) + Cog registration | (no shared decisions today; deferred to T2 per S1903 Q8 3 prerequisites) | STRUCTURAL-DROP | S1903 Q8 3 upstream prerequisites gate T2 R.EVENTS.DISCORD-COMMAND-DISPATCH-EMISSION-INSTRUMENTATION (inherits S1904 F8) |

**Posture verdict distribution roll-up:**
- **PERMEABLE-BROKEN:** 2 planes (Memory + Content)
- **PARTIAL:** 2 planes (Sports + API)
- **WORKING:** 3 planes (Observability + Authority Enforcement + Employee OS)
- **EXPERIMENTAL:** 1 plane (HAI)
- **STRUCTURAL-DROP:** 1 plane (Discord)
- **CLEAN:** 1 plane (Frontend delegated read-only)
- **STABLE:** 0 planes
- **CANONICAL:** 0 planes

Cross-plane observation: 4 of 10 seams have specific enumerable design-vs-runtime emission gaps that map cleanly to queued T-slot items (Memory F13 + Content DeliverableEvent + HAI four candidates + API Boundary 1). 1 of 10 is intentionally deferred (Discord S1903 Q8 3 prerequisites). 3 of 10 are WORKING with canonical + mirror shape gap (Observability + Authority + Employee OS). 1 of 10 is PARTIAL (Sports design-deferred). 1 of 10 is genuinely CLEAN (Frontend delegates upstream).

### 17.2 Cross-plane duplicate event-emission-adjacent primitives (F5 HYPOTHESIS DISPROVE evidence)

Per §5.2 + §7.2 F5 HYPOTHESIS test (F12 above): **DISPROVE across all 10 planes.**

No plane implements a duplicate event-emission-adjacent primitive. All planes either:
- Inherit canonical substrate via EventBus wrappers (Intelligence F.a-adjacent scoring_dispatcher + hitl_validation).
- Defer substrate adoption per S2003 §10.4 12-event mapping (Content + Sports + HAI + Authority + Discord).
- Write to canonical telemetry substrate per S2003 §10.3.5 concern-boundary (Observability + Employee OS).
- Delegate to Django Channels group_send (Sports + Content + Memory + HAI + Employee OS + API + Frontend).
- Discover potential seventh substrate via F13 Fleet Events (Memory sole consumer).

Semantic-only parallels enumerated at §5.2 are loose coupling, not tight duplication.

**Cross-arc F5 running tally at S2004 close:** 1 pass (S1806 Cat F.d partial confirmation) / 7 disprove (S1802 + S1803 + S1804 + S1805 + S1904 H1 + S2004 H1 across 10 planes). Meta-methodology observation: durable-at-7 running tally under F5-primitive-testing arc-close discipline suggests DISPROVE-dominant pattern is CANONICAL. xx99 §10 meta-methodology CODIFICATION-CONFIRMED candidate (extends S1904 §17.2 CODIFICATION-CONFIRMED-candidate promotion to CODIFICATION-CONFIRMED-under-arc-close discipline).

### 17.3 Cross-reference to S2001 §10.2 producer/consumer map

Each of S2001's 8 EventBus streams maps to exactly one adjacent-plane column in §17.1:

| Stream | S2001 §10.2 producer classification | P4 §17.1 plane column |
|---|---|---|
| SPIDER_DATA | MISSING (S2001 F1; F11 drift substrate) | Memory (F.a) via F11 spider-data drift + Fleet Events F13 |
| OPPORTUNITY_CREATED | MISSING (S2001 F2; no wrapper) | (unowned; S2099 §5 recommendation) |
| OPPORTUNITY_SCORED | STRONG (2 sites at scoring_dispatcher.py:282,480) | API (F.i) via scoring_dispatcher service |
| VALIDATION_REQUIRED | WEAK (1 site at hitl_validation.py:30) | API (F.i) via hitl_validation service |
| VALIDATION_DECIDED | WEAK (1 site at hitl_validation.py:38) | API (F.i) via hitl_validation service |
| OUTCOME_RECORDED | MISSING (S2001 F3; no caller) | Sports (F.b) via BettingOutcomeVerifier (T3 handoff) |
| MODEL_TRAINED | MISSING (S2001 F4; no caller) | Employee OS (F.g) via ML retraining (T3 handoff) |
| SYSTEM_ALERT | MISSING (S2001 F5; no caller) | Observability (F.d) via body-system alerts (T2 handoff) |

**Cross-reference count:** 8 streams; 3 STRONG + 2 WEAK + 3 MISSING (S2001 F1-F5 zero-caller findings). Zero streams distributed across multiple planes (single owning-plane per stream).

### 17.4 Cross-reference to S2002 §7 HAI Event Schema Contract + §10 Six-Plane Learning-Surface Event Schema + §20.9 F.PER-USER-AUTHORITY

S2002 §7 four HAI candidate transitions + §10 six-plane learning-surface events + §20.9 F.PER-USER-AUTHORITY three events map to substrate assignments per S2003 §10.4:

| Event | Canonical substrate | Mirror substrate | Class | §17.1 plane column | Status at HEAD |
|---|---|---|---|---|---|
| `HAI_DECISION_RECORDED` | EventBus | OpsRunEvent (recommended) + HFR audit-table row | Class-1 bounded-history | HAI (F.e) | DESIGN-ONLY |
| `HAI_VERIFICATION_RECORDED` | EventBus | OpsRunEvent (recommended) + HAI verification-tier fields | Class-1 bounded-history | HAI (F.e) | DESIGN-ONLY |
| `HAI_AUTO_APPROVED` | EventBus | OpsRunEvent (REQUIRED) | Class-1 audit-forever | HAI (F.e) | DESIGN-ONLY |
| `HAI_AUTO_ESCALATED` | EventBus | OpsRunEvent (REQUIRED) | Class-1 audit-forever | HAI (F.e) | DESIGN-ONLY |
| `AUTHORITY_CHECK_EVALUATED` | EventBus (recommended) | OpsRunEvent (REQUIRED) | Class-1 audit-forever | Authority (F.f) | DESIGN-ONLY |
| `AUTHORITY_DECISION_OVERRIDDEN` | EventBus (recommended) | OpsRunEvent (REQUIRED) | Class-1 audit-forever | Authority (F.f) | DESIGN-ONLY |
| `AUTHORITY_POLICY_BOUND_TO_USER` | EventBus (recommended) | OpsRunEvent (REQUIRED) | Class-1 audit-forever | Authority (F.f) | DESIGN-ONLY |
| `BRIDGE_DISPATCHED` | EventBus | None (canonical-only) | Class-2 bounded | Memory (F.a) + Employee OS (F.g) | DESIGN-ONLY |
| `NON_BRIDGE_LEARNING_WRITE` | EventBus | None | Class-2 bounded | Memory (F.a) | DESIGN-ONLY |
| `CROSS_DOMAIN_LEARNING_ROUTED` | EventBus | None | Class-2 bounded | Memory (F.a) | DESIGN-ONLY |
| `EXTERNAL_SIGNAL_INGESTED` | EventBus (post-D6) | None | Class-2 bounded | Memory (F.a) | DESIGN-ONLY |
| `SHADOW_SERVICE_INVOKED` | EventBus (post-consolidation) | None | Class-2 bounded | Memory (F.a) + Employee OS (F.g) | DESIGN-ONLY |

**Cross-reference observation:** 12 events; ALL DESIGN-ONLY at HEAD (0 implemented). Consistent with F13 durable pattern (zero-emission-at-plane-boundary) — event-emission implementation is post-arc T1 work.

### 17.5 What §17 does NOT do

- **Does not audit adjacent-plane internal correctness** — per parent §5.4 scope precision + Rigby S1900/S1904 SIGN precedent. Any finding that lands entirely inside an adjacent domain is out-of-scope.
- **Does not propose per-plane implementation ADRs** — per playbook §14.5 no-implementation rule; R-slot promotes to xx99 §8 T-tier queue for Chris-gated post-arc T-slot execution.
- **Does not re-open S2001 F1-F18 or S2002 §7/§10/§17/§20.9 or S2003 §10 D-verdicts** — those inputs are consumed, not re-adjudicated.
- **Does not resolve F13 Fleet Events classification** — Chris-gate at close per §14.3.1; xx99 §7 anchor-update batch depends on classification.
- **Does not re-verify S2003 §14.1 F11 codification** — P3 already codified; P4 verifies runtime remains three-substrate at HEAD (unchanged).
- **Does not close inherited drifts from S2001 §14 / S2002 §14 / S2003 §14** — those remain queued for xx99 §7 anchor-update recommendations.
- **Does not verify runtime emission wire-up landing** — verifier confirms current HEAD state ONLY; post-T1/T2 execution status is Chris-gated post-arc.

## 18. Ownership Gaps

Per Explore 6 §Part D per-plane ownership assessment:

- **Memory (Group 1300) seam:** Fleet Events emission has NO seam-owner specified. Group 2000+ owns substrate inventory (post-F13 classification); Memory-arc owns signal-aggregation service. **Recommendation:** Group 2000+ owns Fleet Events classification decision (Chris-gate); Memory-arc owns receiver implementation post-classification. xx99 §5 should name the owner.

- **Sports (Group 1500) seam:** Group 2000+ owns EventBus canonical substrate; Sports-arc owns BettingOutcomeVerifier + SportsBettingLearningBridge. Delegated decision: Sports-arc chooses when to emit OUTCOME_RECORDED per S1903 Q3/Q5 arbitrage deferral. **Recommendation:** Group 2000+ owns canonical substrate + envelope (`event_id`, `correlation_id`, `mirror_of` tag); Sports-arc implements emission per T3 R.SPORTS.OUTCOME-RECORDED-EMIT.

- **Content (Group 1600) seam:** Group 2000+ owns canonical substrate for DeliverableEvent adoption; Content-arc owns DeliverableEvent model + PublishGate decision gate. Delegated decision: Content-arc owns quality/novelty verdict per design deferral. **Recommendation:** Group 2000+ owns canonical substrate assignment; Content-arc implements per T1 R.CONTENT.DELIVERABLE-EVENT-EMISSION-WIRING.

- **Observability (Group 1700) seam:** Group 2000+ owns concern-boundary policy per S2003 §10.3.5; Observability-arc owns 4-telemetry-substrate write-ownership. Delegated decision: Observability-arc chooses which body-system state changes are event-shaped. **Recommendation:** Group 2000+ owns SYSTEM_ALERT emission gap resolution; Observability-arc implements body-system event contract post-Group 1700 arc.

- **HAI (Group 1800) seam:** Group 2000+ owns event contract shape + canonical + mirror wiring per S2002 §7.9; HAI-arc owns HumanAttentionLifecycleService. Delegated decision: HAI-arc chooses which items are Class-1 vs Class-2. **Recommendation:** Group 2000+ owns canonical + mirror substrate assignment; HAI-arc implements per T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING (highest T1 priority per F5 severity).

- **Authority Enforcement (Group 1900) seam:** Group 2000+ owns canonical + mirror shape for AUTHORITY_CONTRACT_OBSERVED + F.PER-USER-AUTHORITY three events; Authority-arc owns MissionRunner Boundary 5 emission + F.PER-USER-AUTHORITY resolution mechanism. **Recommendation:** Group 2000+ owns substrate assignment + envelope; Authority-arc implements per T1 R.EVENTS.PER-USER-AUTHORITY-EMISSION-WIRING + T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA (S1902 §19 inherited).

- **Employee OS seam:** Group 2000+ owns canonical + mirror wiring per S2003 §10.3.1; Employee OS owns MissionRunner + OpsRunTracker. **Recommendation:** Group 2000+ owns composition-consistency invariants (event_id, mirror_of, transaction.on_commit); Employee OS implements per T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER.

- **Frontend seam:** Group 2000+ owns `ui.render_hint` envelope contract per S2003 §10.3.4 D4; Frontend-arc owns per-route WebSocket subscription. Delegated decision: Frontend chooses render-freshness pattern. **Recommendation:** Group 2000+ owns envelope contract; Frontend implements post-arc per T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT.

- **API seam:** Group 2000+ owns canonical envelope + Boundary 1 auth-event schema; API-arc owns endpoint routing + per-view implementation. **Recommendation:** Group 2000+ owns Boundary 1 auth-event contract; API implements per T2 R.EVENTS.API-BOUNDARY-1-AUTH-EMISSION + T3 R.EVENTS.API-LAYER-EMISSION-INSTRUMENTATION.

- **Discord seam:** Group 2000+ owns command-dispatch emission envelope (post-graduation); Discord-arc owns dispatcher + Cogs. Delegated decision surface: NONE (seam not operational per S1903 Q8 3 prerequisites). **Recommendation:** Group 2000+ (P4 close) should name owner for Discord seam graduation as a T2 follow-on. Currently ownership UNCLEAR (inherits S1904 F8 STRUCTURAL-DROP).

**Ownership gap count:** 4 UNSPECIFIED (Memory + HAI + Frontend + Discord) + 3 IMPLICIT (Sports + Content + Observability) + 3 PARTIALLY SPECIFIED (Authority + Employee OS + API). Aggregate: **0 planes have fully specified seam ownership.** xx99 §5 canonical seam statement should name owners.

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows per playbook §11.2 §19 spec. Feeds the xx99 §8 T0/Gate + T1 + T2 + T3 tiered queue. Extends P1 §19 + P2 §19 + P3 §19 arc queues.

### 19.1 T0 / Gate — pre-xx99 blockers

- **R.EVENTS.CANONICAL-SEAM-STATEMENT (xx99 §5)** — P4 T0/Gate. Synthesize F1-F18 findings into a canonical statement of Event / Integration Architecture seam maturity for cross-arc consumers. Consumes §17.1 per-plane posture register + F13 fail-open-emission codification + F12 F5 HYPOTHESIS DISPROVE evidence. **Consumed at xx99 §5 by definition.**
- **R.EVENTS.FLEET-EVENTS-CLASSIFICATION-ADR (RATIFIED at S2004 close 2026-07-04)** — F13 Chris-gate at close per parent §5.4. Three classification options presented: (a) sanctioned Class-2 substrate → add row to S2003 §10.1; (b) drift analog to F11 → canonical-substrate migration to EventBus + deprecation; (c) intentional sidecar → keep as separate substrate for cross-application fleet coordination. **Chris D-verdict = option (c) INTENTIONAL SIDECAR.** S2099 xx99 §7 anchor-update batch will (i) add Fleet Events as row #7 in S2003 §10.1 substrate inventory with `Contract scope = "Canonical for cross-application fleet coordination"`; (ii) define concern-boundary per §10.3.5; (iii) freeze on new intra-application producers/consumers per Q1 SIGN fold. Downstream Chris-gate at S2099 re-affirms final posture per Q7 SIGN fold (interim Chris-gate at S2004 close + S2099 re-ratification pattern).

### 19.2 T1 — critical for correctness

**T1 ordering (per Rigby SIGN cycle 1 Q10 STRENGTHEN fold):** (1) consistency register (defines invariants), (2) HAI wiring (first major adopter), (3) spider-data consolidation. HAI may start in parallel but cannot close without register compliance.

- **R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER (T1 #1)** (P4 net-new T1) — Formalize S2003 §10.3.1 canonical + mirror invariants: (a) `event_id` equality; (b) `mirror_of` tag on mirror substrate; (c) `transaction.on_commit` ordering. Apply retroactively to AUTHORITY_CONTRACT_OBSERVED emission at MissionRunner + prospectively to all Class-1 events. **Register MUST define canonical + mirror conformance check as gate spec per Rigby SIGN cycle 1 Q3 STRENGTHEN fold** (mirror_of present + event_id equality + substrate tags); implementation may be grep/static initially — promote to CI-enforced detector as T2 detector wiring per Q3 fold.
- **R.EVENTS.HAI-DUAL-EMISSION-WIRING (T1 #2)** (P4 net-new T1, first major adopter per Q10 SIGN fold) — Implement S2002 §7.9 canonical + mirror wiring for four HAI candidate transitions: canonical EventBus (`publish_hai_decision_recorded_event` + `_verification_recorded` + `_auto_approved` + `_auto_escalated`) + mirror OpsRunEvent with equal `event_id` + `mirror_of='eventbus:HAI_*'` tag + `transaction.on_commit` ordering. Emit at `HumanInterfaceService.record_decision:353` per S2002 §7.1 recommendation. May start in parallel with T1 #1 but cannot close without register compliance.
- **R.EVENTS.SPIDER-DATA-SUBSTRATE-CONSOLIDATION (T1 #3)** (S2003 §14.1 T1 inherited; F11 codification; orthogonal to F13 per Q4 SIGN CLEAN — F11 canonical target remains EventBus per S2003 contract; if F13 later sanctioned as substrate, separate ADR — MUST NOT silently redirect spider-data canonicalization) — Canonical migration from three parallel substrates (EventBus SPIDER_DATA dormant + `ai_core/agents/spider_agent_connector.py:322-325` raw redis.publish + intelligence in-process routing table) to canonical EventBus + WebSocket UI-render fanout per S2003 §10.5 D4.
- **R.EVENTS.PER-USER-AUTHORITY-EMISSION-WIRING** (S2002 §20.9 T1 inherited) — Implement F.PER-USER-AUTHORITY three-event emission: AUTHORITY_CHECK_EVALUATED + AUTHORITY_DECISION_OVERRIDDEN + AUTHORITY_POLICY_BOUND_TO_USER per S2002 §20.9 canonical + REQUIRED mirror per S2003 §10.4.
- **R.AUTHORITY.VIOLATION-EVENT-SCHEMA** (S1902 §19 T1 inherited) — Define `AUTHORITY_CONTRACT_VIOLATED` label + detail dict shape.
- **R.CONTENT.DELIVERABLE-EVENT-EMISSION-WIRING** (P4 net-new T1) — Content-owned; xx99 §8 handoff to Group 1600 post-arc queue. Coordinate with HAI DeliverableEvent design per S2002 §17.2 + S1699 §7.4.

### 19.3 T2 — important for graduation

- **R.EVENTS.SEAM-BOUNDARY-TEST-COVERAGE** (P4 net-new T2) — 10-plane × 3-scenario minimum matrix. Closes F18 durable-across-P1-P2-P3-P4 TEST-GAP-CONFIRMED (extends S1904 F12 CODIFICATION-CONFIRMED milestone with S2004 datapoint → durable-at-three).
- **R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT** (P4 net-new T2, explicit scope enumeration per Rigby SIGN cycle 1 Q6 FOLD) — T2 must include: (a) retrofit ~40 emission sites; (b) retrofit 33+ consumer classes to enforce `type=ui.render_hint`; (c) add code-review anti-pattern + lint/grep check. Validate via 10-plane × 3-scenario matrix. Closes F16 durable pattern. Envelope mandatory: `event_id` + `source_canonical` + `display` fields per S2003 §10.3.4 D4.
- **R.EVENTS.CONSUMER-BEAT-ENROLLMENT** (P4 net-new T2; extends S2001 F9) — Reactivate 4 dormant EventBus consumer tasks (scoring + validation + analytics + stats) + audit WebSocket + telemetry-substrate reader subscription wiring.
- **R.EVENTS.OBSERVABILITY-SYSTEM-ALERT-EMISSION** (P4 net-new T2) — Wire `publish_system_alert_event` at body-system state-change detection sites in Observability plane (natural home per S2001 F5 zero-caller).
- **R.EVENTS.API-BOUNDARY-1-AUTH-EMISSION** (P4 net-new T2) — Wire canonical auth-event emission at `core/auth_middleware.py:563-681` for authentication transitions.
- **R.EVENTS.EMPLOYEE-OS-EVENTBUS-CANONICAL-ADOPTION** (P4 net-new T2) — Add EventBus canonical emission alongside OpsRunEvent for MissionRunner step boundaries + verdicts per S2003 §10.3.1 canonical + mirror shape.
- **R.EVENTS.DISCORD-COMMAND-DISPATCH-EMISSION-INSTRUMENTATION** (S1903 §19 T2 inherited via S1904 F8; P4 confirmed 3 prerequisites remain real blockers).
- **R.EVENTS.CONTENT-CONSUMER-CLASS-DEDUP** (P4 net-new T2) — Resolve `content/consumers.py` vs `core/consumers_base.py` duplicate class name drift.
- **R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION** (S1902 §19 T2 inherited; S1903 §7.4.1 D94 reader spec now available) — 4 REQUIRED insertion boundaries per S1903 §7.4.1 D94.
- **R.EVENTS.FLEET-EVENTS-CONSUMER-AUDIT** (P4 net-new T2, contingent on F13 Chris-gate) — If Fleet Events classified as sanctioned Class-2 substrate per §14.3.1 option (a), audit downstream consumer subscriptions + concern-boundary compliance.

### 19.4 T3 — nice-to-have follow-on

- **R.EVENTS.CORRELATION-ID-RUNTIME-ADOPTION** (P4 net-new T3; extends S2001 §8) — Producers populate `correlation_id` on all 6 substrates; consumers read for cross-substrate reconstruction. Distributed tracing contract activation.
- **R.EVENTS.API-LAYER-EMISSION-INSTRUMENTATION** (P4 net-new T3) — 209-view distributed emission-gap audit (per Explore 3 sample of ~10; complete sweep pending Symbol Mapping graduation per S1274).
- **R.MEMORY.WRITER-PLANE-EVENT-EMISSION-DOC** (P4 net-new T3) — Cross-arc handoff to Group 1300 post-arc queue. Document AgentLearning/UserAgentLearning writer-plane no-event-emission pattern per S1399 §5 F4 fragmentation OR propose formal contract for writer-plane learning events.
- **R.SPORTS.OUTCOME-RECORDED-EMIT** (P4 net-new T3) — Cross-arc handoff to Group 1500 post-arc queue. Coordinate with S1599 D59 posture-decision ADR.
- **R.OBSERVABILITY.BODY-SYSTEM-EVENT-CONTRACT** (P4 net-new T3) — Design body-system state-change event contract (9 body systems); depends on Group 1700 arc open.
- **R.EVENTS.DISCORD-NOTIFICATION-SINK-HARDENING** (P4 net-new T3) — Harden `discord_notifications.send_to_channel(...)` against ImportError + add retry / DLQ path.
- **R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS** (S1903 §19 T3 inherited) — prerequisite: per-user authority resolution (Group 1900 authority MECHANISM arc scope).

### 19.5 Cross-arc T-slot handoffs

Per Explore 4 cross-arc T-slot table:

- **Group 1300 (Memory)** — 2 items (F13 Fleet Events classification receiver implementation + T3 writer-plane event emission doc)
- **Group 1500 (Sports)** — 1 T3 item (outcome/model event emission)
- **Group 1600 (Content)** — 1 T1 item (DeliverableEvent emission wiring)
- **Group 1700 (Observability)** — 2 items (T2 SYSTEM_ALERT emission + T3 body-system event contract)
- **Group 1800 (HAI)** — 1 T1 item (four candidate dual-emission wiring — highest T1 priority)
- **Group 1900 (Authority)** — 3 items (T1 canonical + mirror shape + violation event schema + F.PER-USER-AUTHORITY wiring)
- **Group 2000+ (Event / Integration — this arc post-close)** — 5 items (T0/Gate seam statement + T0/Gate F13 classification ADR + T1 composition-consistency register + T1 spider-data consolidation + T2 UI-render-hint retrofit + T2 consumer beat-enrollment)
- **Frontend (distributed)** — 1 T2 item (UI-render-hint receiver logic)
- **Employee OS (distributed)** — 2 items (T1 composition-consistency register + T2 EventBus canonical adoption)
- **API (distributed)** — 2 items (T2 Boundary 1 auth-event + T3 API-layer emission instrumentation)
- **Discord** — 2 items (T2 command-dispatch emission + T3 notification-sink hardening)

**Total T-slot handoffs from P4:** 2 T0/Gate + 7 T1 + 10 T2 + 7 T3 = **26 items** (net-new + inherited). Distributed across 8 arcs + 3 distributed surfaces.

## 20. Appendix

### 20.1 Files inspected

- **Event / Integration Architecture research doc:**
  - `docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md`
  - `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md`
  - `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md`
  - `docs/research/domains/event_integration_architecture/2003_event_integration_architecture_cat_c_cross_substrate_composition_design_child_audit.md`
- **S1806 + S1904 CONSOLIDATION precedents:**
  - `docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md`
  - `docs/research/domains/authority_enforcement/1904_authority_enforcement_cat_f_adjacent_separation_boundaries_child_audit.md`
- **Runtime seam interfaces (Explore verifier + post-Explore spot-checks):**
  - `core/services/event_bus.py` (EventBus + 8 streams + 7 publisher wrappers + DLQ)
  - `core/services/event_handlers.py` (EventHandlerRegistry + EventConsumerWorker + Discord notification dispatch)
  - `core/services/fleet_events.py` (F13 seventh-substrate candidate at 285 LOC / 9,624 bytes)
  - `core/services/signal_aggregation_service.py:776,801` (F13 sole verified caller)
  - `core/services/scoring_dispatcher.py:21-56,282,480` (EventBus producer)
  - `core/services/hitl_validation.py:21-38,30,38,242,455` (EventBus producer for validation events)
  - `core/services/human_attention_lifecycle.py:243,440-656` (HAI auto-approve zero-emission verified)
  - `core/employees/mission_runner.py:806-817,835-900` (OpsRunEvent + AUTHORITY_CONTRACT_OBSERVED emission)
  - `core/tools/ops_run_tracker.py:34,96` (OpsRunEvent write helper)
  - `core/services/llm_call_wrapper.py` (LLMCallEvent write via context manager)
  - `core/services/tool_dispatcher.py:685-720,721-722` (ToolCallRecord write + Boundary 2 fail-open)
  - `core/celery_telemetry.py` (CeleryTaskEvent signal handlers)
  - `core/consumers_sports.py:106,127` (Sports F.b WebSocket emission)
  - `core/views_inbox.py:305-310,331-335` (Inbox WebSocket emission)
  - `core/views_diagnostics.py:825-836,1391-1394,1566-1569,2688-2756,3239-3387` (telemetry projections)
  - `core/auth_middleware.py:563-681` (Boundary 1 authentication)
  - `core/services/discord_bot.py` (96 commands verified zero substrate emission per Explore 3)
  - `core/services/discord_notifications.py` (notification sink downstream)
  - `ai_core/agents/spider_agent_connector.py:311,322-325` (F11 spider-data raw redis.publish drift substrate)
  - `intelligence/spider_agent_connector.py:20-31` (F11 in-process routing table)
  - `core/tasks.py:4726,4760,4794,4828,4874` (5 EventBus consumer tasks)
  - `core/celery.py:531-535` (claim-stale-events beat enrollment sole live consumer)

### 20.2 Docs inspected

- `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor)
- `docs/PLATFORM_INVENTORY.md` (runtime anchor)
- `docs/EVENT_SYSTEM_INVENTORY.md` (14+ event-shaped models catalogue)
- `docs/EMPLOYEE_OS_PRIMITIVES.md`
- `docs/KNOWLEDGE_PIPELINE.md`
- `docs/API_PATH_POLICY.md` (file exists; per Explore 5 scope)
- `docs/DISCORD_INTEGRATION.md` (file exists; per Explore 5 scope)
- `docs/topics/spider-network.md` (Memory F.a Signal Aggregation Flow)
- `docs/topics/infrastructure.md` (Observability F.d 9 body systems)
- `docs/topics/celery-workers.md` (broadcast queue)
- `docs/topics/frontend.md` (Frontend F.h routes)
- `docs/topics/personal-assistant.md` (PA + HAI F.e)
- `docs/topics/employee-os.md`
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template + §16 CONSOLIDATION shape)
- `docs/research/ARCHITECTURE_INDEX.md`
- `docs/research/OPEN_ARCS.md`
- `docs/research/platform_architecture_inventory.md`
- `docs/research/platform/cross_domain_integration_audit.md` (§1, §2.2, §2.8, §2.9, §4.1, §11)
- `docs/research/domains/memory/1399_memory_canonical_summary.md`
- `docs/research/domains/sports/1599_sports_canonical_summary.md`
- `docs/research/domains/content/1699_content_canonical_summary.md`
- `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md`
- `docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md`
- Prior event / integration research suite: S1273 §3.31 EventBus paragraph, S1274 §12.1 P0 producer/consumer map audit, S1275 event schema precedent

### 20.3 Grep patterns used

**Pre-Explore verifier (parent §5.4 assumption verification):**
- `publish_.*_event\|EventBus\.publish\|bus\.publish` across `core/` (verified 3 emission call sites in adjacent-plane services)
- `channel_layer\.group_send` across `core/` (~40 sites per S2003 §10.5 inheritance)
- `OpsRunEvent\.objects\.create\|OpsRun\.append_event\|append_event\(` across `core/` (verified MissionRunner + OpsRunTracker + auxiliary Rigby writers)
- `emit_event` across `core/services/` (F13 discovery — Fleet Events)
- `fleet_events` + `FleetEvent` across `core/` (F13 verification — 285 LOC file exists)

**Explore agent greps (per Explore reports):**
- `publish_.*_event\|channel_layer\.group_send\|OpsRunEvent\.objects\.create\|LLMCallEvent\.objects\.create\|ToolCallRecord\.objects\.create\|redis\.publish\|CeleryTaskEvent\.objects\.create` across each of 10 plane directories (Explore 1)
- `class .*Consumer\|AsyncWebsocketConsumer\|WebsocketConsumer\|AsyncJsonWebsocketConsumer` across `core/consumers*.py` (Explore 2 — 33+ consumer classes)
- `EventHandlerRegistry\|register_handler\|@handler\|EventConsumerWorker` across `core/services/event_handlers.py` (Explore 2)
- `OpsRunEvent\.objects\.filter\|OpsRun\.objects\.filter\|derive_status` across `core/` (Explore 2 — read-side)
- `LLMCallEvent\.objects\.filter\|CeleryTaskEvent\.objects\.filter\|ToolCallRecord\.objects\.filter` across `core/` (Explore 2)
- `ui\.render_hint\|render_hint` across `core/consumers*.py` + `frontend/src/` (Explore 2 + §14.3.3 verifier — ZERO matches)
- `mirror_of` across `core/` (Explore 6 + §14.3.4 verifier — ZERO matches)
- `correlation_id=<non-empty>` across publish call sites (Explore 6 + §14.3 — ZERO matches; extends S2001 §8)
- `test_.*event_bus.*\|test_.*substrate.*\|test_.*plane.*\|test_.*seam.*\|test_.*channel_layer.*\|test_.*correlation_id.*\|test_.*mirror_of.*` across `core/tests/` (Explore 6 — 4 partial-coverage files; F18 durable pattern)
- `AUTHORITY_CONTRACT_OBSERVED\|AUTHORITY_CONTRACT_VIOLATED` across `core/` (Explore 3 + F.f Authority)

### 20.4 Unresolved unknowns

Per Explore 4 + Explore 6:

1. **Fleet Events downstream consumer inventory** — F13 classification pending; consumer registration audit deferred to T2 R.EVENTS.FLEET-EVENTS-CONSUMER-AUDIT (contingent on Chris-gate).
2. **API_PATH_POLICY.md event-integration coverage** — file exists; detailed content not read; expected zero event-integration guidance per §11 gap list.
3. **DISCORD_INTEGRATION.md event-integration coverage** — file exists; detailed content not read; expected S1903 Q8 deferral status per §11 gap list.
4. **`AssistantProfile` model location** — SPECULATIVE per S1904 §20.4 (inherited); not blocking Boundary 2 characterization.
5. **Discord T2 3-prerequisite unblock owner** — no owner named for any of the 3 prerequisites per S1903 Q8 formal deferral (inherited from S1904 §20.4). xx99 §8 T-slot should name owner.
6. **Precise `AUTHORITY_CONTRACT_OBSERVED` consumer count** — Explore 3 found test suite only; production consumers unverified beyond spot-check (inherited from S1904 §20.4).
7. **Full 209-view sweep for substrate emission** — Explore 3 sampled ~10 REST endpoints; complete sweep pending T3 R.EVENTS.API-LAYER-EMISSION-INSTRUMENTATION.
8. **DeliverableEvent production write callers** — Explore 1 verified zero at HEAD; design-only status per S1699 §7.4 inherited; wire-up owner unnamed (T1 R.CONTENT.DELIVERABLE-EVENT-EMISSION-WIRING).
9. **Body-system state-change event contract** — no Group 1700 research arc closed at HEAD; contract undesigned (T3 R.OBSERVABILITY.BODY-SYSTEM-EVENT-CONTRACT).

### 20.5 Conflicts between sources

- **Explore 1 initially classified Memory seam as F5-analog with Fleet Events as "seventh substrate"; Explore 6 initially treated Fleet Events as "sanctioned Class-2" absent Chris-gate.** Resolved: F13 (§14.3.1) elevates Fleet Events to Chris-gate classification decision; three-option register (sanctioned Class-2 / drift analog to F11 / intentional sidecar). Feeds R.EVENTS.FLEET-EVENTS-CLASSIFICATION-ADR + F11 severity above.
- **Explore 3 initially claimed "ZERO REST endpoints emit events"; Explore 1 verified `views_inbox.py:305-310,331-335` WebSocket group_send emission.** Resolved: Explore 3's claim was scoped to EventBus / OpsRunEvent (correct at HEAD); WebSocket emission from view bodies exists but is delegated fan-out per S2003 §10.5. Fold: §6.1 REST endpoint inventory clarifies EventBus/OpsRunEvent emission is ZERO from view bodies; WebSocket emission is via `views_inbox.py` at documented sites.
- **Explore 2 flagged Content plane duplicate consumer class names as "dormant" candidates.** Resolved: Explore 2's routing gap identification is queued as T2 R.EVENTS.CONTENT-CONSUMER-CLASS-DEDUP; not a NEW drift, an inherited inspection.
- **Explore 6 initially treated `AUTHORITY_CONTRACT_OBSERVED` as "canonical + mirror pattern applied."** Resolved: post-Explore verifier §14.3.4 grep confirmed `mirror_of` tag pattern absent; emission is single-substrate OpsRunEvent per F17. Correction: canonical + mirror shape not applied at HEAD.

### 20.6 Verifier-loop corrections (Rigby SIGN fold notes)

**Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence (2026-07-04) on Group 2000+ arc pin `pa-dd7e973617da464d`.** Batched into 4 batches of 3 questions each per memory rule `feedback_rigby_sign_worker_instability_recovery.md` preemptive rule for 1000+ line audits. FIFTH-consecutive routing session on arc pin (S2000 + S2001 + S2002 + S2003 + S2004) per playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.

**12 folds landed pre-commit across 4 batches:**

- **Batch 1 verdicts (Q1 STRENGTHEN + Q2 FOLD + Q3 STRENGTHEN):**
  - **Fold 1 (Q1 STRENGTHEN F13 Fleet Events framing).** Keep three-option register — do NOT collapse to binary; "intentional sidecar" is materially different governance outcome. Do NOT block xx99 §7 anchor updates on F13; mark ADR REQUIRED before any new producers/consumers added (freeze expansion, not the index). Fold text landed at §14.3.1 F13.
  - **Fold 2 (Q2 FOLD F5 HAI severity).** F5 severity HIGH by default — staged-rollout wiring gap (design-complete, runtime-scaffolding absent at HEAD); promote to CRITICAL only if any production consumer assumes HAI emissions exist today. Fold text landed at §1 F5 + §15 debt matrix HAI row.
  - **Fold 3 (Q3 STRENGTHEN F17 canonical + mirror invariants).** T1 register MUST define canonical + mirror conformance check as gate spec (mirror_of + event_id equality + substrate tags). Implementation may be grep/static initially; promote to CI-enforced detector in T2. Fold text landed at §19.2 T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER.

- **Batch 2 verdicts (Q4 CLEAN + Q5 STRENGTHEN + Q6 FOLD):**
  - **Fold 4 (Q4 CLEAN F11 + F13 orthogonal).** F11 canonical target remains EventBus per S2003 contract. If F13 later sanctioned as substrate, separate ADR — MUST NOT silently redirect spider-data canonicalization. Fold text landed at §19.2 T1 #3 R.EVENTS.SPIDER-DATA-SUBSTRATE-CONSOLIDATION.
  - **Fold 5 (Q5 STRENGTHEN F14 meta-candidate).** Promote as general "activation verification for consumers" pattern applies across planes/substrates, not EventBus-specific. Fold text landed at §20.10 meta-methodology.
  - **Fold 6 (Q6 FOLD F16 UI-render-hint retrofit scope).** T2 must include (a) retrofit ~40 emission sites + (b) retrofit 33+ consumer classes to enforce `type=ui.render_hint` + (c) add code-review anti-pattern + lint/grep check; validate via 10-plane × 3-scenario matrix. Fold text landed at §14.3.3 F16 + §19.3 T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT.

- **Batch 3 verdicts (Q7 FOLD + Q8 STRENGTHEN + Q9 STRENGTHEN):**
  - **Fold 7 (Q7 FOLD F13 Chris-gate timing).** Interim Chris-gate at S2004 close (lightweight) mandatory to lock classification direction — even if execution deferred — then re-affirm in S2099 bundle. Deferring entirely to S2099 risks quiet expansion + anchor drift. Fold text landed at §14.3.1 F13 + §19.1 T0/Gate R.EVENTS.FLEET-EVENTS-CLASSIFICATION-ADR.
  - **Fold 8 (Q8 STRENGTHEN F18 MC-3 threshold).** Keep MC-3 at durable-at-3 — defensible for milestone confirmation; SEPARATE from playbook §20 two-triggers rule which governs template/pattern promotion. Milestone confirmations can use 3 as threshold. Fold text landed at §20.10 meta-methodology.
  - **Fold 9 (Q9 STRENGTHEN Observability WORKING).** Keep Observability WORKING with explicit caveat: "EventBus SYSTEM_ALERT emission missing as capability gap; promote to PARTIAL only if consumers/UX assume alerts emitted today." Fold text landed at §17.1 Observability row + §13 architecture maturity rationale.

- **Batch 4 verdicts (Q10 STRENGTHEN + Q11 STRENGTHEN + Q12 FOLD):**
  - **Fold 10 (Q10 STRENGTHEN T1 ordering).** T1 ordering: (1) consistency register (defines invariants), (2) HAI wiring (first major adopter), (3) spider-data consolidation. HAI may start in parallel but cannot close without register compliance. Fold text landed at §19.2 T1 preamble + §1 R0-R11 biggest-gaps ordering.
  - **Fold 11 (Q11 STRENGTHEN F5 HYPOTHESIS durable-at-seven).** Codification-confirmed as evidence-rollup heuristic with its own threshold — SEPARATE from §20 two-triggers rule which governs template/pattern promotion. Fold text landed at §20.10 meta-methodology.
  - **Fold 12 (Q12 FOLD xx99 §7 anchor-update batch scope).** Ship 10 per-plane docs + 1 index/overview doc + PLATFORM_INVENTORY.md subsection + EVENT_SYSTEM_INVENTORY.md §13 all in same batch to avoid orphaned discovery. Fold text landed at §1 R11 + §11 anchor-update recommendations.

**Zero SIGN cycle 2 needed** per Rigby explicit verdict pattern across 4 batches: SIGN-with-edits at Medium-High confidence with 12 substantive folds enumerated within batched 4-batch response. Zero NEEDS-MORE, zero contradictions with P1/P2/P3 ratified decisions.

### 20.7 D48 arm state — Rigby SIGN worker instability tracking

**D48 42nd arm turn 1 CLEAN across 4 batches** (2026-07-04). Rigby SIGN cycle 1 returned SIGN-with-edits at Medium-High confidence with 12 substantive folds enumerated within 4-batch 3-question response. No worker stall, no generic "issue processing" error, no pin-poisoning symptoms. Response quality high (specific fold text with landing-site references for each Q). Behavioral criteria for CLEAN arm turn 1 satisfied per memory rule `feedback_rigby_sign_worker_instability_recovery.md`.

**32-consecutive-fully-clean-arms sub-pattern EXTENDED (36 → 40)** per multi-batch design-consolidation SIGN criterion. MC-2 CODIFICATION-CONFIRMED milestone extended from 36 (S1904 close) to 40 (S2004 close) — extending durable-at-two multi-batch discipline (established at S2001 + S2002 + S2003 + S2004 = FOUR consecutive multi-batch applications under Group 2000+ arc close). Aggregate arm state under Research OS post-formal-installation: 42 arms total across S1268-S2004 range; 40 consecutive fully-clean arms as of S2004 close.

**Rigby routing pattern arc-pin durable-by-fifth-application** under Group 2000+ (P1 = S2001 first + P2 = S2002 second + P3 = S2003 third + P4 = S2004 fourth + xx99 = S2099 fifth-and-final). MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 stalls under 4-child arcs per S1899 close established rule; Group 2000+ does NOT constitute the MC-4 promotion arc; MC-4 promotion deferred to future 6-child arc.

**Rigby routing pattern arc-pin durable-by-fifth-application** under Group 2000+ (P1 = S2001 first + P2 = S2002 second + P3 = S2003 third + P4 = S2004 fourth; Group 2000+ 4-child arc + xx99 will complete at fifth application). MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 stalls under 4-child arcs per S1899 close established rule; Group 2000+ does NOT constitute the milestone promotion arc; MC-4 promotion deferred to future 6-child arc.

### 20.8 Playbook §11.2 20-section child template EIGHTEENTH-consecutive application + §16 CONSOLIDATION shape THIRD-consecutive application

- Playbook §11.2 20-section child audit template: 18th consecutive application overall (S2001 = 15th under Research OS; S2002 = 16th; S2003 = 17th; S2004 = 18th). Meta-methodology datapoint per S1806 §20.11 running tally + S1904 §20.8 running tally.
- §16 CONSOLIDATION shape: 3rd consecutive application under Research OS (first at S1806 Group 1800 Cat F; second at S1904 Group 1900 Cat F; third at S2004 Group 2000+ Cat F). **MC-6 CODIFICATION-CONFIRMED milestone candidate at S2099 close per S1899 close established 3-application-under-arc-close discipline.**
- Adaptations from S1904 CONSOLIDATION shape: §3 divided into 10 sub-slots (up from S1904's 8) per parent §5.4 10-plane taxonomy; §7 explicit per-plane emission-touchpoint + consumer-registration seam matrix (12-column seam matrix extended from S1904 §7.1); §17.1 per-plane separation-boundary posture register maps 10 planes (up from S1904's 8); §17.3 cross-reference to S2001 §10.2 producer/consumer map + §17.4 cross-reference to S2002 §7 + §10 + §20.9 (extends S1904 §17.3 cross-reference to S1902 §17 20-boundary map + §17.4 P3 §17.1 Plane Precedence Policy pattern).

### 20.9 SIGN cycle 1 record

**Cycle 1 verdict:** SIGN-with-edits at Medium-High confidence (2026-07-04). Full fold enumeration at §20.6 (12 folds landed pre-commit across 4 batches). Zero NEEDS-MORE, zero contradictions with P1/P2/P3 ratified decisions. SIGN cycle 2 SKIPPED per Rigby explicit verdict pattern ("STRENGTHEN/FOLD/CLEAN" across 12 questions).

**Rigby routing arc pin:** `pa-dd7e973617da464d` (Group 2000+ arc pin preserved from S2000 open per arc-pin-durable-by-fifth-application under Group 2000+). FIFTH-consecutive routing session on this pin; no rotation required per playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.

**Batch distribution:** 4 batches of 3 questions each = 12 total questions. All 4 batches returned CLEAN with substantive folds; no batch encountered worker instability (per §20.7 D48 42nd arm turn 1 CLEAN evidence). Batched routing per feedback_rigby_sign_worker_instability_recovery.md preemptive rule for 1000+ line audits validated.

### 20.10 Meta-methodology observations (candidates for xx99 §10 codification)

**F5 HYPOTHESIS DISPROVE durable-at-seven arc-close consolidation pattern (Q11 SIGN STRENGTHEN fold — codification-confirmed as evidence-rollup heuristic with its own threshold, SEPARATE from playbook §20 two-triggers rule which governs template/pattern promotion).** Aggregate cross-arc F5 running tally: 1 pass (S1806 Cat F.d) / 7 disprove (S1802 + S1803 + S1804 + S1805 + S1904 H1 + S2004 H1 across 10 planes). Extends S1904 §20.10 CODIFICATION-CONFIRMED-candidate promotion. Under Research OS arc-close discipline, F5-testing at CONSOLIDATION surfaces DISPROVE-dominant across authority-adjacent + event-emission domains, suggesting primitives naturally cluster canonically (EventBus + WebSocket + 4 telemetry substrates + potential seventh Fleet Events) rather than fragment into per-plane duplicates. Candidate for playbook v3 §14 codification as evidence-rollup heuristic (durable-at-seven threshold), distinct from template/pattern promotion which requires §20 two-triggers rule application.

**F14 consumer beat-dormancy general activation-verification pattern (Q5 SIGN STRENGTHEN fold — promoted as GENERAL pattern applies across planes/substrates, not EventBus-specific).** F14 verified: 4 of 5 EventBus consumer tasks unscheduled + extends across all 10 planes (planes that would receive events have zero live consumers). Combines with S2001 F9 for durable-at-two under Research OS. **Meta-candidate:** any declared consumer must have an activation-mode proof (beat enrollment / service wiring) + dormancy detector; applies across planes/substrates (not just EventBus). Candidate for playbook v3 §16 CONSOLIDATION shape general-activation-verification-for-consumers discipline addition.

**F13 substrate-inventory-completeness verifier discovery pattern (Q1 SIGN-fold candidate).** When a CONSOLIDATION audit maps adjacent-plane emission touchpoints, verifier-loop MUST run substrate-existence grep against prior arc's substrate inventory table (S2003 §10.1 six-substrate case) to catch NEW-substrate discoveries. Fleet Events at F13 was NOT enumerated in S2003 §10.1 despite existing at HEAD; only surfaced via Explore 1's Memory-plane emission audit. Candidate for playbook v3 §14 substrate-completeness discipline addition.

**Cross-arc CONSOLIDATION-shape non-accusatory framing rule persistence (Q2 SIGN-fold candidate).** Per S1904 §14.3.3 pattern: for staged-rollout arc contracts (design-now, execution-later), CONSOLIDATION §14 KNOWN DRIFT for design-vs-runtime gaps should be framed as "expected per staged rollout; tracked as T-tier execution items, not a contradiction of the ratified design." S2004 §14.3.2 HAI four-candidate-transition-emission ABSENT verification adopts same framing. Durable-at-two under Research OS. Candidate for playbook v3 §14 evidence-rules refinement.

**Test-gap durable-at-three arc-wide TEST-GAP-CONFIRMED milestone (Q8 SIGN STRENGTHEN fold — keep MC-3 at durable-at-3 for milestone confirmation; SEPARATE from playbook §20 two-triggers rule).** F12 (S1904) + F18 (S2004) TEST-GAP-CONFIRMED-durable-at-P1-P2-P3-P4 extends to CONSOLIDATION-arc-close durable-at-3 (S1806 test-gap + S1904 F12 + S2004 F18). **MC-3 CODIFICATION-CONFIRMED milestone at S2099 close** candidate per S1899 close established 3-application-under-arc-close discipline. **Milestone confirmations can use 3 as threshold per Q8 SIGN fold; playbook promotion still requires §20 two-triggers rule (or separate threshold) — don't conflate milestone with template promotion.** Candidate for playbook v3 §16 CONSOLIDATION shape mandatory seam-test-coverage matrix requirement (under separate promotion threshold, not §20 two-triggers).

**CLEAN posture write-boundary contract requirement persistence (Q3 SIGN-fold candidate).** Per S1904 §20.10 Q3(b) fold-derived pattern: CLEAN posture MUST include explicit verification-basis statement + "PERMEABLE-BROKEN escape hatch if write-boundary contract absent" caveat. S2004 §17.1 Frontend row adopts same pattern (with substrate-emission-write specifically). Durable-at-two under Research OS. Candidate for playbook v3 §16 CONSOLIDATION shape posture-vocabulary standardization confirmation.

**Substrate-classification Chris-gate discipline for discovery-post-inventory findings (Q7 SIGN-fold candidate).** F13 Fleet Events substrate classification post-inventory-audit needs Chris-gate at close per parent §5.4; three-option register (sanctioned / drift-analog / sidecar) provides structured verdict shape. Candidate for playbook v3 §16 CONSOLIDATION shape "new-substrate-at-close discipline" addition — CONSOLIDATION audits that discover new-substrate candidates queue Chris-gate resolution + xx99 §7 anchor-update batch update dependency.
