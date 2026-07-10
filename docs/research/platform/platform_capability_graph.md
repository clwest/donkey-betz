---
title: "Platform Capability Graph — end-to-end chains from producer to human value"
status: draft (S2734 baseline; awaiting Rigby SIGN + Chris ratification)
authority: engineering
session_added: 2734
campaign: platform_capability_engineering
head_sha: 56df8159
verified_at: 2026-07-09
predecessor: docs/research/platform/integration_readiness_matrix.md
companion_anchors:
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/platform/integration_readiness_matrix.md
  - docs/PLATFORM_INVENTORY.md
  - docs/EVENT_SYSTEM_INVENTORY.md
owner: claude (drafted S2734; Rigby SIGN pending)
---

# Platform Capability Graph

> **What this is.** An engineering artifact — not research. Every
> capability Donkey Betz is supposed to possess is drawn as one
> end-to-end chain from producer to human value. Each chain is one
> engineering unit. Each PR should complete or materially improve
> one chain. This is the new engineering vocabulary for the
> platform.
>
> **What this is not.** A domain map. A research audit. An ADR. A
> spec. Chris was explicit: "Do not begin coding until the graph
> is complete and reviewed." The graph is the review gate.
>
> **How to read.** Each chain has: (1) a compact chain diagram
> with `→` arrows and `MISSING` markers where the wire is absent;
> (2) the 15 mission-required attributes in compact form; (3)
> completeness score (`X of 15`) at HEAD 56df8159; (4) the specific
> missing edges. §20 groups by leverage. §21 recommends the first
> chain. §22 states the operating rule for future PRs.

---

## Chain format (used identically for each chain)

```
### N. Chain Name

Chain: producer → event → consumer → ... → human value
        (MISSING marked in-line where the wire is absent)

1  Human outcome        — ...
2  Trigger              — ...
3  Producer             — file:line
4  Intermediate events  — model / stream / signal
5  Consumers            — file:line
6  Persistence          — DB models
7  Notifications        — channels
8  Frontend updates     — route + push/poll
9  Human attention      — HAI production Y/N/N-A
10 Failure modes        — what breaks
11 Recovery             — retry / DLQ / manual
12 Verification         — how to know it worked
13 Existing tests       — file paths
14 Missing links        — SPECIFIC wire-up gap
15 Effort               — S / M / L

Completeness: X of 15 fully wired at HEAD.
```

---

## §1. Mission Completion

Chain: `MissionRunner.run()` → `emit_mission_verdict()` → `OpsRunEvent(label='verdict_issued:*')` → `Deliverable.status='ready'` (per bounded-summary postflight) → **MISSING: WebSocket broadcast** → **polling** → Frontend Active-Work panel → Human sees verdict.

1  Human outcome — Chris (or another human) sees "Mission complete: certified/partial/rejected" in Frontend Active-Work panel within 1s of runtime completion.
2  Trigger — `run_docs_manager_daily` / `run_platform_auditor_daily` / `run_chief_of_staff_daily` beat OR PA `employee_tool.run_now`.
3  Producer — `core/employees/mission_runner.py:1530-1570` (`emit_mission_verdict` wrapper) → `core/employees/mission_verdict.py:63` (framework helper).
4  Intermediate events — `OpsRun(domain='mission')` + `OpsRunEvent(label='verdict_issued:*')`; may also update `Deliverable.status` via bounded-summary postflight.
5  Consumers — `core/employees/status.py:422` (shift report). Frontend polls `/api/home/active-work/` every 15s.
6  Persistence — `OpsRun` + `OpsRunEvent` (audit trail). `Deliverable` (bounded-summary artifact).
7  Notifications — none wired from `verdict_issued`. Discord Cog references exist but not on this path.
8  Frontend updates — Active Work panel polls `/api/home/active-work/` every 15s. 51 WS routes exist; no WS route triggered on `OpsRunEvent.post_save`.
9  Human attention — HAI not produced from `verdict_issued`. Could be, per §14.10 authority arc T1.
10 Failure modes — mission times out (`SoftTimeLimitExceeded`); step fails (partial verdict); worker OOM (no verdict at all).
11 Recovery — beat re-fires next day; manual `employee_tool.run_now`; no auto-retry on partial.
12 Verification — `OpsRunEvent.objects.filter(label__startswith='verdict_issued:', run=<id>).exists()`.
13 Existing tests — `core/tests/test_mission_verdict.py` (~250 lines, 12 test methods incl. idempotency); `core/tests/test_mission_runner.py` (D1 lock verdict-issued events).
14 Missing links — one `@receiver(post_save, sender=OpsRunEvent)` where `label.startswith('verdict_issued:')` → `channel_layer.group_send` on a `home_active_work` group. Frontend already listens to `/ws/*/`; add a receiver in `active_work` component.
15 Effort — **S** (Small — one signal handler + one WS receiver + one existing group).

Completeness: **11 of 15** — items 7, 8, 9, 14 unwired.

---

## §2. Deliverable Ready

Chain: Content deliberation (or MissionRunner postflight, or agent authorship) → `Deliverable.status='ready'` → `post_save` signal → `DeliverableEvent(event_type='status_transition', direction='up')` → **query-side consumers** (`ops_autopilot/impact.py`, `diagnostics/coo_daily.py`, `td_handlers_gateway.py`, `employees/status.py`, `views_deliverables.py`) → **MISSING: notification fanout** → Human learns deliverable is ready.

1  Human outcome — Chris (or a channel subscriber) is proactively notified when a deliverable transitions to `ready`.
2  Trigger — any of: MissionRunner postflight, content deliberation completion, agent finalization, human status flip.
3  Producer — `core/signals/deliverable_status_signals.py:94,205` (post_save on `Deliverable` writes `DeliverableEvent`).
4  Intermediate events — `Deliverable` + `DeliverableEvent`. No EventBus stream yet (Event/Integration §14.11 T1 #6 content deliverable-event emission wiring is post-arc T1).
5  Consumers — query-side (state-only): `core/services/ops_autopilot/impact.py`, `core/services/diagnostics/coo_daily.py:474+` (rework gate), `core/services/td_handlers_gateway.py`, `core/employees/status.py`, `core/views_deliverables.py:832`. **Zero `@receiver(post_save, sender=DeliverableEvent)`.** `rigby_event_intake` task gated by `RIGBY_EVENT_INTAKE_ENABLED=False` default.
6  Persistence — `Deliverable`, `DeliverableEvent`; also `SelfBlog` when factory-adopted.
7  Notifications — none fired on `DeliverableEvent`. 5 channels exist (Web Push + Expo + Discord + Inbox + HAI).
8  Frontend updates — none pushed. `deliverablesApi` REST fetch shows the new deliverable on next page load.
9  Human attention — no HAI created when deliverable needs approval. `HumanAttentionBridge.create_pilot_gate_attention()` exists but is separate flow.
10 Failure modes — status flip does not fire signal (no post_save); DeliverableEvent write fails silently; consumers never see the row.
11 Recovery — manual query of `Deliverable.status='ready'`; nightly rework-gate at `coo_daily.py:474+`.
12 Verification — `DeliverableEvent.objects.filter(event_type='status_transition', to_status='ready', created_at__gte=…).exists()`.
13 Existing tests — `core/tests/test_deliverable_intake_subscriber.py`, `core/tests/test_deliverable_tool_set_status.py`, `core/tests/test_rigby_event_intake.py`, `core/tests/test_rework_signal_and_gate.py`, `core/tests/test_rigby_mission_delegation.py`.
14 Missing links — one **NotificationFanoutService** with a `@receiver(post_save, sender=DeliverableEvent)` receiver where `direction='up'` and `to_status='ready'`, that dedups by (recipient, deliverable_id) then fires N of {Web Push, Expo, Discord, Inbox `DirectMessage`, HAI} based on user prefs.
15 Effort — **M** (Medium — one service + one receiver + N channel adapters + dedup contract + 5 user-pref surfaces to consult).

Completeness: **10 of 15** — items 7, 8, 9, 14 unwired.

**Leverage note.** This chain is the highest-leverage in the graph per §20 because 4 other chains reuse the same NotificationFanout service once it exists (§8 HAI Escalation, §16 Notification Delivery, §14 Platform Health, §7 Revenue Opportunity).

---

## §3. Research Complete

Chain: Research arc lifecycle → domain scoping doc + child audits + canonical summary → docs cascade (4-step) → RAG surface refresh → Rigby answers questions from research.

1  Human outcome — the research is queryable by Rigby via `search_docs` / `kb_tool semantic_search` within 24h of arc close.
2  Trigger — canonical summary xx99 doc lands in `docs/research/domains/<slug>/` OR anchor doc updated.
3  Producer — arc author (Claude) commits the xx99 doc + updates `ARCHITECTURE_INDEX.md` + `OPEN_ARCS.md` → PR merges.
4  Intermediate events — `docs/INDEX.md` regenerated; `docs/_provenance.json` refreshed; `Document` rows created/updated; `DocumentEmbedding` rows created with pgvector.
5  Consumers — `search_docs` (LOCAL lane `core.rag.top_k` on `.rag/corpus.jsonl`); `kb_tool semantic_search` (PROD lane `core.rag_integration.search_embeddings` via `DocumentEmbedding` + HNSW).
6  Persistence — `Document`, `DocumentEmbedding` (pgvector).
7  Notifications — cascade step-count in PR description (per memory rule).
8  Frontend updates — Rigby chat surface reflects on next query.
9  Human attention — none required.
10 Failure modes — cascade run partially (steps 1-3 only, step 4 `embed_documents` skipped → docs indexed but not embedded → Rigby search blind); build_docs_index alone doesn't push to Document table.
11 Recovery — `python manage.py embed_documents --all-unembedded` after any partial cascade.
12 Verification — `Document.objects.filter(source_uri__contains='<slug>').exists()` + `DocumentEmbedding` rows via `sync_docs_index_to_documents --embed` output.
13 Existing tests — cascade smoke test at PR level. `python manage.py verify_doc_claims --only-drift` for drift.
14 Missing links — none load-bearing. Cascade PR discipline is well-owned (memory rule).
15 Effort — **N/A** (already operational).

Completeness: **15 of 15**. This chain works today.

---

## §4. Content Published

Chain: signals → ClaimsPack (3-source: `SignalCluster` + `LegacySpiderData` 72h + `DocumentEmbedding`) → deliberation runner → `SelfBlog` write → `PublishGate` intent check → publish rail (Discord broadcast OR Newsletter dry_run OR frontend approve) → Human reads content.

1  Human outcome — audience reads/consumes new content (blog post / Discord embed / newsletter / video).
2  Trigger — `auto_publish_approved_blogs` beat (docs claim daily 6 AM but **beat MISSING at HEAD** per §14.5 F1 correction; runtime-confirmed via `ops_tool.celery_task_history` 30d=0); OR manual `content_tool.publish`; OR reviewer approve.
3  Producer — `core/services/claims_pack_builder.py`; `core/services/content_deliberation_runner.py:1-150`; `core/services/content_writer_agent.py`.
4  Intermediate events — `SelfBlog` row; `PublishGate` state machine (SelfBlog-only at HEAD; §14.5 F.15.C1 triple-gate composition MISSING); `Deliverable` (agent-authored envelope).
5  Consumers — Discord broadcast rail (fire-and-forget, no retract per §14.5); Newsletter (dry_run parked >4mo); Frontend `blogsApi` + `deliverablesApi`.
6  Persistence — `SelfBlog`, `Deliverable`, `Blog`, `Document`.
7  Notifications — Discord broadcast is a notification. Newsletter dry_run only. No Web Push / Expo / Inbox for content-published.
8  Frontend updates — via `blogsApi` + `deliverablesApi` REST fetch. No WS push.
9  Human attention — post-publish correction ABSENT arc-wide (§14.5 T.15.C1); Discord broadcast immutable-once-fired.
10 Failure modes — beat never fires (auto-publish); Discord broadcast fails silently; Newsletter live-send infrastructure ABSENT; `_settle_wager` idempotency risk on retry.
11 Recovery — manual `content_tool.publish`; no post-publish correction path.
12 Verification — `SelfBlog.objects.filter(published_at__isnull=False).count()`; `Deliverable.objects.filter(status='ready', published_at__isnull=False)`; `ContentGeneration.state='PROCESSED'`.
13 Existing tests — `core/tests/test_content_deliberation.py` (if present); `core/tests/test_rework_signal_and_gate.py`.
14 Missing links — (a) restore `auto_publish_approved_blogs` beat entry to `core/celery.py`; (b) Newsletter live-send ADR + implementation (§14.5 T.15.C2); (c) post-publish correction path across 3 rails (per §14.5 T.15.C1); (d) triple-gate composition contract for `PublishGate` (§14.5 F.15.C1).
15 Effort — **L** (Large — depends on 4 Chris-gated ADRs D65a–D65e per §14.5).

Completeness: **7 of 15** — chain works partially; auto-publish is dark; newsletter is dark; correction path missing.

---

## §5. Spider Discovery

Chain: spider registry (80 spiders / 41 categories) → per-spider beat trigger → HTTP fetch → normalize → dedup via `SpiderItemHash` → `LegacySpiderData` insert → `SpiderExecutionLog` write.

1  Human outcome — fresh external data is available for downstream signal / content / opportunity / knowledge chains within the spider's TTL window.
2  Trigger — `PeriodicTask` beat per-spider (varies by category).
3  Producer — `core/tasks_spiders.py` + `ai_core/spiders/` (80 spiders across 41 categories).
4  Intermediate events — `LegacySpiderData` write; `SpiderExecutionLog(status='success'|'error'|'timeout')`; `SpiderItemHash` for dedup.
5  Consumers — `signal_aggregation_service.py` (entity-token clustering S1139); `claims_pack_builder.py` (72h window); `intelligence/spider_decision_bridge.py` (opportunity scoring); `AgentKnowledgeSource` via LearningBridge.
6  Persistence — `LegacySpiderData` (~1.14M `SpiderItemHash` rows per PLATFORM_INVENTORY).
7  Notifications — none direct. Discord `/odds` command bypasses coordinator per §14.4 F.HOT-PATH-CHOKE.
8  Frontend updates — spider stats via `ops_tool.spider_execution_history`.
9  Human attention — spider drought detection today runs daily → 24h invisibility window (§3.5).
10 Failure modes — silent spider (zero results over window); dedup collision silently skipped (§3.9); network flake; source schema drift.
11 Recovery — beat re-fires next scheduled interval; `SpiderExecutionLog(status='error')` records but doesn't escalate.
12 Verification — `LegacySpiderData.objects.filter(spider_type=…, created_at__gte=…).count()`; `SpiderExecutionLog` telemetry.
13 Existing tests — `core/tests/test_spider_registry.py` (if present).
14 Missing links — (a) `SpiderDroughtEvent` producer (aggregator over `SpiderExecutionLog` with zero-return threshold) → Platform Auditor employee OR HAI; (b) `SpiderDedupCollisionEvent` producer for data-quality alerting.
15 Effort — **S** (aggregator + one event model + producer).

Completeness: **11 of 15** — chain produces reliably; drought + collision escalation missing.

---

## §6. Signal Detection

Chain: `LegacySpiderData` writes accumulate → `signal_aggregation_service.py` entity-token clustering → `SignalCluster.pattern_type` (one of 10 types) → `SignalCuratorService` routes to AutoTopic → Initiative or Content Pipeline.

1  Human outcome — pattern-strength signals surface actionable topics for humans and downstream agents.
2  Trigger — `SignalAggregationService.run()` beat or dispatch.
3  Producer — `core/services/signal_aggregation_service.py:33` (SignalAggregationService class).
4  Intermediate events — `SignalCluster.objects.create(pattern_type=…, pattern_strength=…, cluster_size=…)`; MIN_CLUSTER_SIZE=3.
5  Consumers — `signal_curator_service.py`, `claims_pack_builder.py`, `system_state_aggregator.py`, `td_handlers_content.py`, `diagnostics/trend_analysis_daily.py`, `views_fleet_signals.py`, `initiative_signal_linker.py`, `td_handlers_ops.py`.
6  Persistence — `SignalCluster` (10 pattern types per PLATFORM_INVENTORY).
7  Notifications — none from `SignalCluster.post_save`.
8  Frontend updates — Signal-view via `views_fleet_signals.py`.
9  Human attention — `SignalCluster(pattern_strength > 0.9)` → HAI is MISSING per §3.8 (no threshold gate).
10 Failure modes — clustering fails silently; below MIN_CLUSTER_SIZE = no cluster; entity-token drift skews grouping.
11 Recovery — next beat cycle re-clusters.
12 Verification — `SignalCluster.objects.filter(pattern_strength__gte=0.9).count()`.
13 Existing tests — signal aggregation coverage in existing test files.
14 Missing links — `PatternCriticalityEvent` producer where `pattern_strength > 0.9` → HAI via `HumanAttentionBridge` (extend the bridge class with a `create_signal_pattern_attention()` method — pattern already exists for Arbitrage Detection).
15 Effort — **S** (one threshold check + one bridge method + one signal handler).

Completeness: **12 of 15** — producer + consumers wired; escalation missing.

---

## §7. Revenue Opportunity

Chain: spider data → `intelligence/spider_decision_bridge.py` → `OpportunityScoringAgent` → `Opportunity` row → `ImpactEvent` (revenue attribution via `MultiTouchAttributor._attribute_event:1233-1290`) → learning bridge → **MISSING: outreach delivery** → Human sees / closes opportunity.

1  Human outcome — Chris sees a high-value revenue opportunity and can act on it.
2  Trigger — spider produces relevant data OR beat re-scores existing opportunities.
3  Producer — `intelligence/spider_decision_bridge.py`; `OpportunityScoringAgent`; 20 writers on `Opportunity` mainline (dominant: `spider_decision_bridge.py` 99.96%; 19 non-dominant UNCLASSIFIED per §14.3).
4  Intermediate events — `Opportunity` write; `ImpactEvent(type='revenue', value_usd=…)` at `ops_autopilot/impact.py:375+,431+,488+`.
5  Consumers — `impact.py:582+,951+` (same-domain rollups); `revenue_attribution_bridge.py:22-28,227` (writes `UserAgentLearning` on core `Revenue` only — intelligence `RevenueRecord` orphaned per §14.3 F.E3 dual-schema drift).
6  Persistence — `Opportunity`, `Revenue`, `ImpactEvent`, `OutreachDraft`, `EngagementEvent`, `Meeting`, `ClosePack`.
7  Notifications — none from `Opportunity → *`. Outreach delivery MISSING all channels (grep-negative at HEAD `beda00e5` for `send_outreach|sendgrid|postmark|smtplib` per §14.3 F.B1).
8  Frontend updates — via `ops_tool` queries. No push.
9  Human attention — no auto-HAI on high-value opportunity (§14.3 F.D1 zero HAI writers from Meeting/ClosePack).
10 Failure modes — freelance/gig Cat F ORPHANED from `ImpactEvent` → learning chain entirely (§14.3 F.F6); `_impl_run_freelance_opportunity_scout` UNGUARDED 5-phantom-field writer (§14.3 F.F1 runtime `FieldError` guaranteed if invoked); intelligence-vs-mainline schema drift.
11 Recovery — none automated. Chris must query dashboards.
12 Verification — `Opportunity.objects.filter(created_at__gte=…, score__gte=THRESHOLD).count()`.
13 Existing tests — `core/tests/test_revenue_attribution_bridge.py` (if present).
14 Missing links — (a) outreach delivery ADR + implementation (SendGrid/Postmark/SES/Mailgun/LinkedIn/Rigby-DM) — §14.3 T5; (b) `OpportunityEscalationEvent` producer → auto-Initiative + HAI — §3.7; (c) Cat F freelance-lifecycle → `ImpactEvent` bridge — §14.3 F.F6; (d) intelligence-vs-mainline source-of-truth ADR — §14.3 T1 R.E3; (e) sibling JobContracts (Revenue Employee + Income/Jobs Employee) — §14.3 D55.
15 Effort — **L** (5 Chris-gated ADRs open per §14.3).

Completeness: **6 of 15** — scoring works; downstream monetization / attribution / delivery / escalation are all dark.

---

## §8. Human Attention Escalation

Chain: any producer (Deliverable / SignalCluster / OpsRunEvent / CeleryTaskEvent-failure-cluster / Body Systems / Opportunity / arbitrage) → `HumanAttentionBridge` methods → `HumanInterfaceService.create_attention_item()` → `HumanAttentionItem` row → Frontend inbox → Human decides.

1  Human outcome — Chris (or another target user) sees an attention item requiring decision within the SLA of urgency.
2  Trigger — any producer event that requires human review.
3  Producer — `core/services/human_attention_bridge.py:44 HumanAttentionBridge` class (5 documented categories: Pilot Gates, Agent Executions, Arbitrage Detection, System Alerts, Content Review); 22 total `HumanAttentionItem.objects.create` sites at HEAD (grep 2026-07-09).
4  Intermediate events — `HumanAttentionItem(source_type=…, source_id=…, urgency=…, item_type=…)`.
5  Consumers — `human_interface_service.py`; `views_platform_command.py`; Rigby `human_attention_tool`.
6  Persistence — `HumanAttentionItem`, `HumanFeedbackRecord` (once decided).
7  Notifications — depends on user prefs; no unified fanout today.
8  Frontend updates — inbox via `/ws/*/` broadcast OR REST poll.
9  Human attention — the round-trip: `FeedbackProcessor` → `AgentLearning` + `LearningInsight` (§14.2 STRONG per S1274 §2.5; §14.9 F7 CRITICAL identifies 4 break-points that make the loop compound false-confidence).
10 Failure modes — no auto-HAI producer for failure clusters (§3.3); no threshold on signal patterns (§3.8); no HAI on revenue opportunity (§14.3 F.D1); no HAI on body-system degradation (§2.2); F7 CRITICAL 4-break compound learning-loop.
11 Recovery — manual polling of Frontend inbox; direct `HumanAttentionItem.objects.create` via Rigby.
12 Verification — `HumanAttentionItem.objects.filter(urgency='high', decided_at__isnull=True).count()`.
13 Existing tests — `core/tests/test_sia_escalation.py`; `core/tests/test_platform_audit_routine.py`.
14 Missing links — (a) `FailureClusterAggregator` → `HumanAttentionBridge.create_failure_cluster_attention()` (§3.3); (b) `SignalPatternCriticality` gate → `HumanAttentionBridge.create_signal_pattern_attention()` (§3.8); (c) `HumanAttentionBridge.create_opportunity_escalation()` for high-value revenue (§14.3 F.D1); (d) `HumanAttentionBridge.create_body_system_degradation()` for HeartBeat degradation (§2.2); (e) fix F7 CRITICAL 4-break compound learning-loop (Group 1800 D80 4-option posture — Chris D-verdict).
15 Effort — **M** for a–d (bridge extensions); **L + Chris ADR** for e.

Completeness: **9 of 15** — infrastructure exists; 4 producer categories missing; learning-loop compound break requires ADR.

**Leverage note.** The `HumanAttentionBridge` class already contains the 5-category integration pattern (see file docstring). Extending it with 4 more categories is additive — one method per producer, one `@receiver(post_save, ...)` per model. §21 recommends completing this chain first.

---

## §9. Governance Enforcement

Chain: `GovernanceState` / `KillSwitch` / `SystemConfiguration` budget flags / `JobContract.authority` → operator action or auto-trigger → runtime enforcement point → PA / agent / task blocked or degraded → Human sees enforcement.

1  Human outcome — the platform correctly blocks unauthorized / over-budget / frozen operations at runtime instead of silently allowing them.
2  Trigger — operator sets mode via `governance_tool.set_mode('freeze')`; OR auto-trigger from cost/failure aggregator; OR JobContract dispatched with authority conflict.
3  Producer — `core/services/ops_autopilot/governance.py` (KillSwitch CRUD at 2347, 2508); `core/models_governance.py:17-189`; `JobContract` frozen dataclass.
4  Intermediate events — `GovernanceState` row; `KillSwitch(target=…, is_active=True)`; budget flag in `SystemConfiguration`.
5  Consumers — 4 active consumers of freeze/safe_mode (spiders / signal aggregation / workspace pipelines / LLM enforcer per §2.7); **KillSwitch has ZERO enforcement dispatch consumers** (grep 2026-07-09 — `governance.py:2192` is a status-dict populator; `intelligence.py:1569,1717` cleanup only); `JobContract.authority` observed via `_emit_authority_contract_event` but not enforced (§14.10 only Boundary 5 warn-mode event fires).
6  Persistence — `GovernanceState`, `KillSwitch`, `SystemConfiguration`, `JobContract` (frozen dataclass at `core/employees/jobs.py:73-162`).
7  Notifications — no PA warning-context injection on `budget_freeze_active` (§3.6); silent tool failure erodes user trust.
8  Frontend updates — none. Governance state is a query.
9  Human attention — no HAI on governance conflict.
10 Failure modes — `enforce_authority_mode` field ABSENT at HEAD (grep 2026-07-09); Boundary 5 warn-mode is the only observable signal; four planes drift into non-composed state.
11 Recovery — operator flips via `governance_tool.set_mode`; no auto-recovery.
12 Verification — `GovernanceState.objects.filter(is_active=True).values('mode')`; `KillSwitch.objects.filter(is_active=True).count()`; `OpsRunEvent.objects.filter(label__startswith='authority_warn:').count()`.
13 Existing tests — `core/tests/test_platform_audit_routine.py` (partial coverage); no dedicated authority-enforcement test.
14 Missing links — (a) add `enforce_authority_mode` field per S1999 T1; (b) activate KillSwitch enforcement dispatch reader per P3 D94 reader spec; (c) inject governance context into PA tool responses on freeze (§3.6); (d) HAI on 4-plane conflict.
15 Effort — **M** (Chris-gated ADR + migration + reader activation + PA context enricher).

Completeness: **7 of 15** — mode-observation works; enforcement dispatch is dark.

---

## §10. Authority Violation

Chain: agent / employee / PA attempts action requiring authority → boundary check reads `JobContract.authority[…]` → mismatch detected → observation event OR blocked action → audit trail → Human sees violation.

1  Human outcome — unauthorized action is observed, logged, and eventually blocked; audit trail proves it.
2  Trigger — any dispatch (agent, mission step, PA tool) crossing an authority boundary.
3  Producer — 4 planes exist and don't compose (`GovernanceState`, `KillSwitch`, `SystemConfiguration` budget, `JobContract.authority`) per S1269. Runtime enforcement layer is `_emit_authority_contract_event` warn-mode observation only.
4  Intermediate events — `AuthorityLevel` enum has 1 runtime consumer (level_counts accumulator at `mission_runner.py:863-874`); Boundary 5 warn-mode event.
5  Consumers — `AuthorityLevel` accumulator; audit reports; **no runtime consumer that BLOCKS on violation**.
6  Persistence — `OpsRunEvent(label='authority_warn:…')` at HEAD; not `authority_denied:` or `authority_blocked:`.
7  Notifications — none.
8  Frontend updates — none.
9  Human attention — no HAI on authority violation.
10 Failure modes — every plane drifts alone; enforcement never blocks; audit only records the warning.
11 Recovery — manual after-the-fact review.
12 Verification — `OpsRunEvent.objects.filter(label__startswith='authority_warn:', run__domain='mission').count()` (13 events / 5 days / 4 employee handles as of S1902 close).
13 Existing tests — `core/tests/test_mission_runner.py` covers `AuthorityLevel` accumulator.
14 Missing links — (a) `enforce_authority_mode` model field (§14.10 T1); (b) 4-plane composition rule (blocked on Symbol Mapping STAGE 3); (c) `authority_denied:` observation event class distinct from warn.
15 Effort — **L** — depends on STAGE 3 Symbol Mapping (per §12.5 governance plane composition).

Completeness: **5 of 15** — this is the platform's most-fragmented capability.

---

## §11. Memory Creation

Chain: agent / PA / user interaction → any of 7 flavors (Cat A–H per §14.2 Memory canonical) → `AgentMemory` / `AgentKnowledgeSource` / `UserAgentLearning` / `ConversationMemory` / RAG corpus / documentation corpus write → RAG-side visibility → Human/agent retrieval.

1  Human outcome — the platform remembers what happened and can act on it later without re-learning.
2  Trigger — 22+ `LearningBridge` ABC receivers on model post_save; agent execution; PA turn; conversation completion; document ingestion.
3  Producer — 9 `LearningBridge` receivers (Plane 2 autonomous canonical per §14.9); `FeedbackProcessor` (Plane 1 human-mediated canonical); Reddit + Bluesky external intelligence (Plane 3); `AgentLearningService` Redis-only (Plane 4); `AgentLearningEngine` DEFINED-BUT-UNSCHEDULED (Plane 5); `PersistentLearningEngine` DEFINED-BUT-UNUSED (Plane 6).
4  Intermediate events — 6 planes × distinct model writes per §14.9 six-plane fragmentation.
5  Consumers — `strategic_memory_service.py`; `conversation_orchestrator.py` 14-day freshness window; `BaseAgent._get_relevant_knowledge_for_task`.
6  Persistence — `AgentMemory`, `AgentKnowledgeSource`, `UserAgentLearning`, `ConversationMemory`, `Document`, `DocumentEmbedding`.
7  Notifications — none.
8  Frontend updates — memory surface tab (if enabled).
9  Human attention — Chris asks Rigby "what did we decide about X" — retrieval is the human-facing surface.
10 Failure modes — `AgentMemory.create_memory` write-authority MISSING (no user FK gate, no rate limit, no audit — §14.2 T10 HIGH); `AgentLearningService` within-process consistency gap (Redis write does not clear in-process dict — §14.2 D4); Plane 5+6 defined but not firing; F3 duplicate class-name collisions (BoardroomLearningService × 2 + UnifiedLearningPipeline × 2 per §14.9).
11 Recovery — LRU eviction; Redis TTL; manual purge.
12 Verification — `AgentMemory.objects.filter(user_id=…, updated_at__gte=…).count()` per flavor.
13 Existing tests — `core/tests/test_agent_learning.py` (if present).
14 Missing links — (a) write-authority framework ADR (§14.2 T10); (b) fix F3 duplicate class-name collisions (§14.9 F3 HIGH IMMEDIATE); (c) F7 CRITICAL 4-break compound learning-loop fixes (Chris D-verdict D80).
15 Effort — **M** for a-b; **L** for c (Chris ADR).

Completeness: **10 of 15** — writes work; discipline gaps + F7 compound loop are the load-bearing risks.

---

## §12. Knowledge Retrieval

Chain: Rigby (or agent, or user) has question → dispatch to `search_docs` (LOCAL) OR `kb_tool semantic_search` (PROD) → retrieval lane executes → results ranked → returned to caller → Human/agent uses.

1  Human outcome — Chris (via Rigby) or an agent gets an accurate, provenance-cited answer from platform knowledge.
2  Trigger — PA tool call OR agent `_get_relevant_knowledge_for_task` OR user query.
3  Producer — `search_docs` PA tool (`core/services/td_handlers_*.py`); `kb_tool` PA tool; agent-side auto-enrichment via `BaseAgent._get_relevant_knowledge_for_task`.
4  Intermediate events — none (retrieval is synchronous).
5  Consumers — the caller.
6  Persistence — read-only path.
7  Notifications — none.
8  Frontend updates — result shown in Rigby chat OR agent response.
9  Human attention — none required for basic retrieval.
10 Failure modes — LOCAL corpus (`.rag/corpus.jsonl`) stale vs PROD (`DocumentEmbedding`); `search_docs` hardcodes LOCAL and `kb_tool semantic_search` hardcodes PROD (§14.2 D8/D9); PA turn does NOT auto-invoke either lane (retrieval is tool-call-only — asymmetry with `BaseAgent`); provenance drift when embed step skipped.
11 Recovery — re-embed via `embed_documents --all-unembedded`; regenerate LOCAL corpus.
12 Verification — `verify_doc_claims --only-drift`; `DocumentEmbedding.objects.count()`; `search_docs` returns non-empty for known-present docs.
13 Existing tests — `core/tests/test_rag_integration.py` (if present); doc-cascade tests.
14 Missing links — (a) runtime lane selector (§14.2 F1 CANDIDATE + §14.12 T-slot execution PRs); (b) PA turn-context auto-enrichment symmetry with `BaseAgent._get_relevant_knowledge_for_task` (§14.2 R5 POSTURE-PENDING).
15 Effort — **M** for a; **M** for b.

Completeness: **11 of 15** — retrieval works; lane selection is manual; PA symmetry gap.

---

## §13. Document Cascade

Chain: docs edited → `python manage.py build_docs_index` → `python manage.py build_rag_corpus` → `python manage.py sync_docs_index_to_documents` → `python manage.py embed_documents --all-unembedded` → RAG surface fresh.

1  Human outcome — Rigby's RAG surface reflects HEAD docs within one cascade run.
2  Trigger — PR merge that modifies `docs/` OR arc/session close discipline.
3  Producer — cascade PR author (Claude).
4  Intermediate events — `docs/INDEX.md` (autogen), `.rag/corpus.jsonl` (LOCAL), `Document` rows, `DocumentEmbedding` rows.
5  Consumers — §12 Knowledge Retrieval consumers.
6  Persistence — `Document`, `DocumentEmbedding`.
7  Notifications — PR body should state the chunk count as evidence per memory rule `feedback_cascade_pr_must_include_embed_step`.
8  Frontend updates — indirect via Rigby chat.
9  Human attention — none.
10 Failure modes — steps 1-3 without 4 (embed) → RAG blind (S1802 caught: PR #2852+#2854 shipped without embed → Rigby's RAG blind to entire Group 1800 arc for ~2 sessions); `build_docs_index` alone doesn't push to Document table (memory rule); provenance drift.
11 Recovery — `embed_documents --all-unembedded` after any partial cascade.
12 Verification — `Document.objects.count()` before/after; `DocumentEmbedding.objects.filter(created_at__gte=…).count()`; `verify_doc_claims --only-drift`.
13 Existing tests — cascade smoke tests.
14 Missing links — none load-bearing. Discipline rule is well-owned (memory rule).
15 Effort — **N/A** (already operational).

Completeness: **15 of 15**. This chain works when discipline is followed.

---

## §14. Platform Health

Chain: `BodyCoordinator` runs 9-body-system scan every 10 min → each system produces `HeartBeat`-related metric → `HeartBeat(health_score, overall_status, is_alive, components_healthy)` row → readers (§services/heart.py, views_heart.py, td_handlers_ops.py, tasks.py, agents/content_writer_agent.py) → Discord alert on degradation → Human sees status.

1  Human outcome — Chris (or Rigby) can query platform health and receive automated alerts on degradation.
2  Trigger — beat every 10 min.
3  Producer — `core/services/heart.py`; `core/services/body_coordinator.py:110-300+`; 9 body systems (HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN).
4  Intermediate events — `HeartBeat` row; system-specific status enrichers.
5  Consumers — 6 non-doc readers at HEAD (grep 2026-07-09): `views_heart.py:78` (status display); `tasks.py:5655`; `agents/content_writer_agent.py:544`; `services/heart.py:705` (Discord alert path); `td_handlers_ops.py:3883, 4982, 5008` (PA tool query surface).
6  Persistence — `HeartBeat` model.
7  Notifications — `discord.send_system_alert()` at `services/heart.py:690` on degradation.
8  Frontend updates — via `views_heart.py:78` REST fetch.
9  Human attention — **no HAI production** on IMMUNE/DIGESTIVE degradation. Audit §2.2 "no reader" claim STALE at HEAD; but HAI producer gap is real.
10 Failure modes — beat drift; Discord API down; HeartBeat write fails silently; system-specific scanner fails.
11 Recovery — next beat cycle; Discord retry.
12 Verification — `HeartBeat.objects.filter(overall_status='degraded', recorded_at__gte=…).count()`.
13 Existing tests — `core/tests/test_body_systems.py` (if present).
14 Missing links — (a) `HumanAttentionBridge.create_body_system_degradation()` → HAI (extends bridge like §8); (b) autonomic Governance reaction on cluster degradation (Body Coordinator emits no autonomic actions per §14.11 audit); (c) trend / delta computation instead of instantaneous status.
15 Effort — **S** for a; **M** for b; **M** for c.

Completeness: **12 of 15** — status observable; escalation to HAI + Governance missing.

---

## §15. Worker Failure

Chain: Celery task fails → `task_failure.connect` handler at `core/celery_telemetry.py:177,240` → `CeleryTaskEvent(status='FAILURE')` written → bridge to `AgentExecution` at line 241 → **MISSING: failure-cluster aggregator** → HAI on cluster → Human sees cluster escalation.

1  Human outcome — cascade failures (DB pool exhaustion, worker OOM, broker congestion) page a human within 5 min instead of going unnoticed 10+ min.
2  Trigger — Celery `task_failure` signal.
3  Producer — `core/celery_telemetry.py:74 (task_prerun), 115 (task_postrun), 177 (task_failure), 240 (agent_task_failure_bridge)`.
4  Intermediate events — `CeleryTaskEvent(status='FAILURE', task_name=…, exception_type=…)`; `AgentExecution.status='FAILED'` on the bridge path.
5  Consumers — `views_diagnostics.py:828+`; `td_handlers_ops.celery_task_history` (PA tool surface). No cross-domain consumer.
6  Persistence — `CeleryTaskEvent`, `AgentExecution` (via bridge).
7  Notifications — none automatic. Discord alert path exists via `heart.py` but is health-scoped not failure-scoped.
8  Frontend updates — via `views_diagnostics.py`.
9  Human attention — no HAI on failure cluster (§3.3).
10 Failure modes — the observer itself fails (rare per S1214-1216 hardening arc); telemetry emit fails silently; TTL truncates old rows (`CELERY_TASK_EVENT_RETENTION_DAYS` default 30).
11 Recovery — Celery task retry policy per task; DLQ for EventBus events; manual restart via `make celery-recycle` (F-CW-1 helper from S2732 Batch D).
12 Verification — `CeleryTaskEvent.objects.filter(status='FAILURE', created_at__gte=…).count()`; audit CI checks.
13 Existing tests — `core/tests/test_celery_telemetry.py` (if present); campaign validation reports at `docs/research/tools/validation/`.
14 Missing links — `FailureClusterAggregator` (5-min sliding window over `CeleryTaskEvent(status='FAILURE')` GROUP BY task_name / worker / queue) → `HumanAttentionBridge.create_failure_cluster_attention()` extension.
15 Effort — **S** (aggregator + threshold + bridge method).

Completeness: **12 of 15** — telemetry is STRONG; escalation missing.

---

## §16. Notification Delivery

Chain: any producer → **MISSING: NotificationFanoutService** → per-user preferences → dedup by (recipient, source_id) → fan-out to N of {Web Push, Expo, Discord, Inbox `DirectMessage`, HAI} → device / channel → Human receives once.

1  Human outcome — user receives each unique notification exactly once through their preferred channels.
2  Trigger — any producer (§2 Deliverable Ready, §8 HAI Escalation, §14 Platform Health, §7 Revenue Opportunity, arbitrage, alerts).
3  Producer — 5 channel-specific senders exist independently (Web Push, Expo, Discord `send_system_alert`, `DirectMessage.create`, `HumanAttentionItem.create`).
4  Intermediate events — none unified today. Per-channel state (`NotificationLog`, `PushSubscription`) is separate.
5  Consumers — each device / channel client.
6  Persistence — `NotificationLog`, `PushSubscription`, `DirectMessage`, `HumanAttentionItem`.
7  Notifications — THIS IS the notification chain — recursion.
8  Frontend updates — inbox WS + Web Push handler.
9  Human attention — receiving a notification IS the human-attention moment.
10 Failure modes — same user receives same alert 4-5× through different paths (§5.4, §12.2); Discord API down; PushSubscription expired; user prefs unread.
11 Recovery — dedup service; retry per channel; user manually silences.
12 Verification — `NotificationLog.objects.filter(recipient_id=…, source_type=…).count() <= 1` per (recipient, source).
13 Existing tests — per-channel tests.
14 Missing links — one `NotificationFanoutService` with (a) user-pref lookup, (b) dedup by (recipient, source_type, source_id), (c) N adapter calls, (d) `NotificationLog` audit. **This is Sequence L2 from the Integration Readiness Matrix.**
15 Effort — **M** (unification service is the whole thing).

Completeness: **8 of 15** — 5 channels work; unification service does not exist.

---

## §17. Cost Protection

Chain: LLM call via factory → `LLMCallEvent(tokens_in, tokens_out, model, provider)` at `llm_call_wrapper.py:195` → **MISSING: cost_usd field** → aggregator over window → threshold → auto-`governance_tool.set_mode('freeze')` → Human sees freeze active + reason.

1  Human outcome — Chris cannot lose $500+ silently to a runaway reasoning-model loop.
2  Trigger — LLM cost aggregation window (e.g., 5 min sliding) exceeds threshold.
3  Producer — `core/services/llm_call_wrapper.py:195` writes `LLMCallEvent`.
4  Intermediate events — `LLMCallEvent`.
5  Consumers — `employees/status.py:461` (shift report); `rigby_delegation_signals.py:102`. Read by Employee OS shift reports only per §6.1.
6  Persistence — `LLMCallEvent` (no `cost_usd` field at HEAD).
7  Notifications — none on cost.
8  Frontend updates — none.
9  Human attention — no HAI on cost overrun.
10 Failure modes — 9 files + ~15+ sites bypass `openai_client_factory` (§4.2 §7.5.1 Rigby grep) → no `LLMCallEvent` emitted → cost invisible; TTL truncates history; per-call cost estimate error accumulates.
11 Recovery — manual `governance_tool.set_mode('freeze')`.
12 Verification — `LLMCallEvent.objects.filter(created_at__gte=…).aggregate(cost=Sum('cost_usd'))`.
13 Existing tests — `core/tests/test_llm_enforcer.py` (if present).
14 Missing links — (a) add `cost_usd` field on `LLMCallEvent`; (b) `_estimate_cost()` at wrapper; (c) aggregator + threshold; (d) auto-freeze trigger; (e) HAI on threshold breach; (f) direct `openai` import sweep (§4.2). **This is Sequence L5 from the Integration Readiness Matrix.**
15 Effort — **M** (migration + wrapper + aggregator + governance path + HAI).

Completeness: **6 of 15** — every load-bearing piece is missing; only per-call telemetry works.

---

## §18. Authentication

Chain: user → login form → `Token` created → `TokenAuthMiddleware` on each request → DRF `IsAuthenticated` → view/handler → response → session refresh / logout → cleanup.

1  Human outcome — users are authenticated correctly; 401s surface as explicit re-login prompts (not silent failures); logout revokes backend token.
2  Trigger — HTTP request; WS connect.
3  Producer — `authtoken_token` DB row; `FleetSignatureAuthentication`; `TokenAuthMiddleware`.
4  Intermediate events — DRF authentication chain; 285-entry path-list gate registry at `core/auth_middleware.py:94-561` (OVERCOUPLED per §14.15).
5  Consumers — 838 explicit `@permission_classes` decorator sites + 74 class-attr sites across 126 files (§14.15 not "coverage rate" — decoration density); 803 consumer call-sites classified by inheritance-path.
6  Persistence — `Token`, `AuthSession`.
7  Notifications — none.
8  Frontend updates — Zustand `authStore`; `syncUser`; `authApi.logout` (**NOT called from Sidebar** — §14.14 F-D-SIDEBAR-1).
9  Human attention — no HAI on auth failure cluster.
10 Failure modes — silent-401 SYSTEMIC (~630/1300 call-sites at risk per §14.14 F-B-CRIT-2); `Sidebar.tsx:356` clears authStore but does NOT call `authApi.logout()` → backend token never revoked; no refresh endpoint; VIPInvite.account_expires_at declared-fictional (not enforced); PA-chat 401 mid-conversation = agent-hang UX.
11 Recovery — user re-logs; token cleanup on TTL (if configured).
12 Verification — `Token.objects.filter(user_id=…).exists()`; response codes distribution.
13 Existing tests — `core/tests/test_auth_*.py`; new coverage post-S2499.
14 Missing links — 14 co-equal P0 items grouped as P0-A (platform-wide silent-401 remediation) + P0-B (token lifecycle) + P0-C (endpoint-specific). Most immediate: **F-D-SIDEBAR-1** — add `authApi.logout()` invocation in `Sidebar.tsx:356`. That is a single-file fix that closes the leaked-token indefinite-window today.
15 Effort — **L** overall (14 P0 items). **S** for F-D-SIDEBAR-1.

Completeness: **7 of 15** — mechanism works; contract silently violated across all 4 auth axes.

---

## §19. Conversation Lifecycle

Chain: user posts message → `POST /api/pa/chat/` → task dispatched to `pa` queue → `UnifiedPAEntrypoint.dispatch` → enrichment pipeline (8 services) → tool-loop (GPT-5.2 function calling) → assistant reply → `POST /api/pa/chat/status/<task_id>/` polling → WS push OR REST return → Human reads reply.

1  Human outcome — conversation turn completes with tool-attributed reply within acceptable latency; conversation state persists.
2  Trigger — `POST /api/pa/chat/` OR PA WS message.
3  Producer — `core/services/unified_pa_entrypoint.py` (7,613 lines); `core/services/tool_dispatcher.py` (1,267 lines); `core/services/pa_tool_schemas.py`.
4  Intermediate events — PA task on `pa` queue; `ToolCallRecord` per tool call; `LLMCallEvent` per LLM call; `ConversationMemory` update.
5  Consumers — assistant surfaces (chat UI, `pa_chat.py` CLI, Discord bridge if applicable).
6  Persistence — `Conversation`, `ConversationMemory`, `Message`, `ToolCallRecord`, `LLMCallEvent`, `AgentMemory` (via MemoryPromotionService).
7  Notifications — completion via WS `agent_completed` (per Cat D §10.4); `AgentFollowupSubscription` may arm follow-up.
8  Frontend updates — WS push OR 2s polling on `/api/pa/chat/status/<id>/`.
9  Human attention — none required for normal conversation. HAI on auto_followup_false suppresses banner (`feedback_auto_followup_false_suppresses_banner`).
10 Failure modes — `PA_USE_FUNCTION_CALLING=false` env drift → short-circuits to keyword intent (silent no-tool path); PA worker not restarted → running old code; `pa_local.sh` token drift → 401 mid-conversation; `session_tool.retire` needed for jammed pins; SIGN worker-instability after 2 substantive turns on inline prompts >~4k words.
11 Recovery — `make celery-recycle` (F-CW-1); `session_tool.create_fresh` for new pin; `session_tool.retire` for jammed pin; batched SIGN discipline.
12 Verification — `Conversation.objects.filter(id=<id>).exists()`; `[PA_TASK_SUMMARY].routing_path=fc|keyword` log line; `[PA_ROUTING_INIT]` startup log.
13 Existing tests — 293/293 tests pass across 18 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py` (S2732).
14 Missing links — (a) envelope-shape telemetry ABSENT at HEAD (0 shape-version fields across 3 canonical PA-client WS message classes per §14.16); (b) Cat D `authHandling: 'suppress_redirect'` telemetry gap; (c) REST↔WS parallel-delivery reconciliation-layer UNOWNED at HEAD (§14.16 §9.1a); (d) `Cat C2 α/β/γ` session-lifecycle Auth cascade DEFERRED per §14.14.
15 Effort — **M** for a-c (T4 Group 1700 Observability handoff bundle owned there); **L + Chris ADR** for d.

Completeness: **12 of 15** — mechanism operational; envelope + telemetry SoT gaps; auth cascade blocked on §14.14 Chris D-verdict.

---

## §20. Chains grouped by engineering leverage

Leverage = (% completeness at HEAD) × (breadth of downstream chains unlocked) ÷ (blast radius). Chains scored:

### Tier A — HIGHEST leverage (S–M effort, unlock ≥2 other chains)

| Chain | % | Missing links | Effort | Unlocks |
|---|---|---|---|---|
| §16 Notification Delivery | 8/15 | `NotificationFanoutService` unified layer | M | §2 Deliverable Ready, §8 HAI Escalation, §14 Platform Health, §7 Revenue Opportunity partially |
| §8 HAI Escalation | 9/15 | 4 producer categories added to existing `HumanAttentionBridge` | M | §5 Spider Drought, §6 Signal Detection, §7 Revenue, §14 Platform Health, §15 Worker Failure |
| §1 Mission Completion | 11/15 | one `post_save(OpsRunEvent)` → WS `group_send` on `home_active_work` | S | precedent for §2, §16 push patterns |

### Tier B — HIGH leverage (S effort, self-contained + high user impact)

| Chain | % | Missing links | Effort | Notes |
|---|---|---|---|---|
| §15 Worker Failure | 12/15 | `FailureClusterAggregator` + one bridge method | S | reuses §8 bridge pattern |
| §6 Signal Detection | 12/15 | pattern-strength threshold + bridge method | S | reuses §8 bridge pattern |
| §5 Spider Discovery | 11/15 | `SpiderDroughtEvent` + aggregator | S | closes silent-outage 24h window |
| §18 Auth F-D-SIDEBAR-1 (subset only) | one-file | add `authApi.logout()` at `Sidebar.tsx:356` | S | closes leaked-token indefinite window today |

### Tier C — MEDIUM leverage (M effort, Chris-ratifiable within one arc)

| Chain | % | Missing links | Effort | Notes |
|---|---|---|---|---|
| §14 Platform Health | 12/15 | bridge method + autonomic Governance reaction | S+M | reuses §8 bridge pattern |
| §17 Cost Protection | 6/15 | `cost_usd` field + aggregator + auto-freeze + HAI | M | needs migration; unblocks financial risk |
| §19 Conversation Lifecycle telemetry | 12/15 | envelope-shape telemetry + reconciliation-layer owner | M | T4 Group 1700 arc owns per §14.16 |
| §12 Knowledge Retrieval | 11/15 | runtime lane selector + PA turn-context auto-enrichment | M | tied to Group 2100 T-slot execution PRs |

### Tier D — HIGH VALUE but BLOCKED (L effort or Chris ADR)

| Chain | % | Missing links | Blocker |
|---|---|---|---|
| §4 Content Published | 7/15 | auto-publish beat + newsletter + correction path | 4 Chris ADRs D65a–D65e |
| §7 Revenue Opportunity | 6/15 | outreach delivery + escalation + Cat F freelance bridge + parallel-schema ADR + JobContracts | 5 Chris ADRs T1–T8 |
| §9 Governance Enforcement | 7/15 | `enforce_authority_mode` + KillSwitch dispatch reader | Chris ADR R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS |
| §10 Authority Violation | 5/15 | 4-plane composition | STAGE 3 Symbol Mapping (2-3 cycles) |
| §18 Auth (full scope) | 7/15 | 14 co-equal P0-A/B/C items | Chris D-verdict on 4-axis §14.14 |
| §11 Memory Creation | 10/15 | write-authority framework + F3 collisions + F7 4-break loop | Chris D-verdict D80 |

### Tier E — OPERATIONAL (No action required)

| Chain | % | Notes |
|---|---|---|
| §3 Research Complete | 15/15 | works when cascade discipline followed |
| §13 Document Cascade | 15/15 | works when cascade discipline followed |

---

## §21. Recommended first chain to complete

**Chain: §16 Notification Delivery** (via §2 Deliverable Ready as the first driver).

Rationale.

1. It is the single highest-leverage chain — 4 other chains reuse the same fanout service once it exists (§2, §8, §14, §7 partial).
2. All 5 channel adapters exist. All 5 persistence models exist. All 5 producer signals exist. **The engineering gap is one dedup + fan-out service — not a channel-side rebuild.**
3. It sets the pattern that §8 HAI Escalation reuses (extending the existing `HumanAttentionBridge` class with 4 new methods) and that Tier B chains follow.
4. It does NOT depend on any of the 6 Chris-gated D-verdict items (§21 of Integration Readiness Matrix). It ships without waiting for constitutional ADRs.
5. Rigby's audit correction — DeliverableEvent already has query-side consumers — proves the model is a live substrate. The wire missing is the *notification receiver*, not a new schema.

**Implementation sequence (draft — Rigby SIGN + Chris ratification required before coding).**

Step 1. Author `core/services/notification_fanout_service.py` with (a) `NotificationFanoutService.dispatch(recipient_id, source_type, source_id, urgency, payload)` public entry, (b) user-pref lookup (which channels does this user opt into for this source_type?), (c) dedup by `NotificationLog.objects.filter(recipient=…, source_type=…, source_id=…).exists()`, (d) fan-out to selected of {WebPushAdapter, ExpoAdapter, DiscordAdapter, InboxAdapter, HAIAdapter}, (e) `NotificationLog.objects.create(...)` audit.

Step 2. Wire one producer first — `@receiver(post_save, sender=DeliverableEvent)` where `direction='up'` AND `to_status='ready'` → `NotificationFanoutService.dispatch(...)`.

Step 3. Ship without other producers. Observe for one week (F-CW-1 celery-recycle to load code; verify via `NotificationLog` audit that dedup works and no user gets same alert twice).

Step 4. After proven, extend to §8 HAI Escalation as the second producer (extending `HumanAttentionBridge` with `create_failure_cluster_attention`, `create_signal_pattern_attention`, `create_opportunity_escalation`, `create_body_system_degradation`). Each extension is additive.

Step 5. §14 Platform Health + §7 Revenue Opportunity + §15 Worker Failure follow the same additive pattern.

**Warning — do NOT ship without addressing this one point.** §12.4 audit calls Cross-Domain Identity Carriage a P0-companion. Ship the fanout service without the 3-role vocabulary carriage and every notification loses actor identity crossing the S1271 F6 drop-boundary. **Recommended: add `executor_actor` / `sponsor_actor` / `principal_user` fields to `NotificationLog` from day 1 even if the producers can't populate them all initially.** Rigby's `paStore` 16-field pattern is precedent for capturing all fields even when only a subset is populated.

---

## §22. New engineering operating rule for Donkey Betz

Every PR henceforth answers **one** question:

> Which capability chain — from §1–§19 — became more complete because of this PR?

A PR that touches code but does not close a documented gap in one of these chains is either (a) closing an undocumented chain that this graph missed (in which case, propose the new chain first via PR-to-`platform_capability_graph.md`), or (b) not aligned with the campaign.

Rigby's SIGN dispatches henceforth should carry the chain reference in the ask so the verification loop stays coupled to the graph.

---

---

## §23. Rigby SIGN refinements (append-only fold from pin `pa-b77dd0dc2f7f4f2d`, 2026-07-09)

Fresh SIGN pin dispatched immediately after §1–§22 draft landed.
Verdict: **SIGN-with-refinements** across 5 questions. Refinements
folded here rather than rewriting §16 / §21 in place, per audit
v6 §14 append-only discipline. Reader cross-references §23 for the
latest verdict on §16 completeness score and §21 recommendation.

### F1 — Producer file:line refinement (Q1 CONFIRMED with correction)

- §1 Mission Completion producer verified at `core/employees/mission_runner.py:1530-1570` + `core/employees/mission_verdict.py:63`. **CONFIRMED.**
- §2 Deliverable Ready producer receivers are at `core/signals/deliverable_status_signals.py:133+` and `:205+` (not `:94` as originally cited — line 94 is a rank-comparison block, not the receiver). **File-correct; line-numbers refined.**

### F2 — §16 completeness score is optimistic (Q4 PARTIALLY-CONFIRMED)

Rigby's grep at HEAD 56df8159 evidenced 2 of 5 channel adapters — not 5 as §16 claimed:

- **Web Push CONFIRMED** — `core/services/push_notification_service.py` `PushNotificationService` class exists (VAPID, `pywebpush`, Session 562).
- **Inbox CONFIRMED** — 7 `DirectMessage.objects.create` sites: `views_inbox.py:141,165,223`; `td_handlers_core.py:3830`; `user_onboarding_service.py:123,209`; `employees/comms.py:343`.
- **Expo push UNEVIDENCED** — 77 files match "Expo" but zero match "expo push". Model-level surfaces (`PushSubscription`) may exist but the *sender* infrastructure at HEAD is not evidenced. Consistent with §14.17 (Mobile Expo push UI UNKNOWN).
- **Discord broadcast infra UNEVIDENCED** — not spot-checked in Rigby's pass. `discord_bot.py send_system_alert()` referenced in §14 Platform Health but not confirmed as a broadcast-fanout entrypoint.
- **HAI adapter UNEVIDENCED** — the class exists (`HumanAttentionBridge` per §8) but has not been confirmed as a `NotificationFanoutService.dispatch()` target yet.
- **Channel-preference surface UNEVIDENCED** — Claude claimed "per-user preferences" exist implicitly; Rigby did not evidence a `NotificationPreferences` model or similar. Do NOT assume the preference lookup is a query — it may need to be built.

**Score refinement.** §16 Notification Delivery drops from **8 of 15** to **6 of 15 with tracked uncertainty**. The 3 open items are (Expo, Discord, HAI adapter) confirmation OR net-new implementation, plus channel-preference schema.

### F3 — §21 recommendation revision (Q3 REFINEMENT)

Rigby's pressure-test: **"§1 may be a smaller/faster pattern-unlock (WS broadcast + notification scaffold) that should be evaluated head-to-head before locking §21."**

Head-to-head:

| Criterion | §1 Mission Completion | §16 Notification Delivery |
|---|---|---|
| Completeness at HEAD | 11 of 15 | 6 of 15 (per F2) |
| Missing links | 1 (`post_save(OpsRunEvent)` → WS `group_send`) | 3–4 (channel adapters + prefs + fanout service) |
| Effort | **S** | **M-L** (per F2 refinement) |
| Blast radius | LOW (additive) | MEDIUM (5-way integration) |
| Unlocks | Pattern precedent: WS-push-on-post_save | 4 other chains (§2, §8, §14, §7 partial) |
| Runtime dependency uncertainty | NONE — all pieces exist | HIGH — 3 channels + prefs unevidenced |
| Chris-daily observable | Yes (missions run daily) | Yes (deliverables produced daily) |
| Human-attention-loss per day at current usage | Medium (15s polling window) | Medium (silent deliverable-ready) |

**Revised §21 recommendation: §1 Mission Completion is the FIRST chain to complete. §16 Notification Delivery becomes the SECOND, blocked on a discovery pass to evidence Expo / Discord / HAI adapters + channel-preference surface.**

Rationale — the pattern §1 establishes (`post_save` → `channel_layer.group_send` on a Frontend WS group) is directly reusable by §16 for whichever channels turn out to already exist. Doing §1 first also *discovers* the WS-push scaffold that §16 needs (and possibly reveals that "notification" for many users is already "WS push to Frontend" — reducing §16's dependency count).

**Sequence revision.**
1. §1 Mission Completion — S effort; ship immediately.
2. Discovery pass — evidence Expo / Discord / HAI adapter existence + channel-preference schema. Deliverable: one-page evidence report.
3. §16 Notification Delivery — scope confirmed by (2); implement remaining adapters if needed; wire fanout.
4. §8 HAI Escalation extensions — reuse fanout service; add the 4 producer methods to `HumanAttentionBridge`.
5. §15 Worker Failure + §6 Signal Detection + §14 Platform Health — additive; each reuses the pattern.

### F4 — Candidate chains flagged for graph v2 (Q5 REFINEMENT)

Rigby flagged 4 candidate chains not present in §1–§19. Adding as CANDIDATE for a follow-up graph revision (do not treat as ratified without evidence pass):

- **§C1 Agent Learning Loop (Plane 1–6).** Distinct from §11 Memory Creation because §11 focuses on the write side; Agent Learning Loop is the round-trip: `HAI decided` → `FeedbackProcessor` → `AgentLearning` + `LearningInsight` → agent picks up learned bias on next execution → new HAI. §14.9 F7 CRITICAL identifies 4 break-points in this loop. If broken, learning creates false-confidence.
- **§C2 Feedback Processing.** HAI decided → `HumanFeedbackRecord` → `FeedbackProcessor` → downstream updates. Overlaps §C1 but scoped tighter to the immediate feedback ingestion event.
- **§C3 Beat Schedule Health.** Are the 92 enabled + 5 disabled `PeriodicTask` rows all firing as expected? Cross-check against `CeleryTaskEvent` per task_name over 24h window. Would surface every zero-fire beat instantly (§14.4 `verify_betting_outcomes` + `daily_betting_digest`; §14.5 `auto_publish_approved_blogs`).
- **§C4 Fleet Federation.** PA ↔ Fleet MISSING per §14.16 (FleetSignatureAuthentication conveys NO `workspace_id` at HEAD). Cross-repo capability chain.

**Priority for graph v2.** §C3 Beat Schedule Health has the highest leverage among the 4 — it turns "beat MISSING" from a per-arc discovery to an automated diagnostic. §C1 Agent Learning Loop is Chris-gated (D80 4-option posture); do not scope until §14.9 posture ratified. §C2 is inside §C1's scope. §C4 is cross-repo (per §14.16 v5 note).

### F5 — §17 Cost Protection completeness score NOT re-verified

Rigby's Q2 pass did not complete the §17 grep. Score remains **6 of 15** as Claude asserted but is NOT SIGN-CONFIRMED. Flag: a second pass on §17 is owed before ratifying §17 as a Tier C sequence in §20.

### F6 — Preserved: Cross-Domain Identity Carriage caveat (§21 F3 tightening)

Rigby's F3 refinement does not remove the §12.4 identity carriage prerequisite; it moves it. Now: identity carriage prerequisite attaches to **§16 discovery pass** (step 2 of the revised sequence), not to §1 Mission Completion. §1 does not cross the S1271 F6 drop-boundary at the notification frontier because the payload is an audit-log event, not a cross-recipient notification.

---

## §24. Revised operating rule

Same as §22, but with the correction:

> Every PR henceforth answers **one** question: *which capability chain — from §1–§19, or the CANDIDATE §C1–§C4 in §23 F4 — became more complete because of this PR?*

Rigby's SIGN-with-refinements pattern is the review discipline. Fresh pin per campaign phase. Independent verification is required for every producer / consumer / channel claim before scheduling implementation.

---

**End of draft. Status: engineering artifact — S2734 Claude
authorship + Rigby SIGN-with-refinements folded via fresh pin
pa-b77dd0dc2f7f4f2d 2026-07-09. §21 recommendation revised:
first chain to complete is §1 Mission Completion (S effort, 11 of
15 completeness, one wire-up gap). §16 Notification Delivery
becomes second, blocked on discovery pass per F2 tracked
uncertainty. Chris ratification is the gate to any implementation
begin.**

---

## §25. Post-CDR refinements — §16 + §12 (append-only, 2026-07-09)

Two Capability Discovery Records were authored and Chris-ratified
after §1–§24 landed. Both materially refined chain scoring based
on repository evidence. Append-only per playbook §14 discipline:
§1–§24 bodies remain verbatim; readers cross-reference §25 for
the latest verdict on §16 and §12.

### §25.1 CDR-001 — §16 Notification Delivery

Full record: `docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md`.

- **Score refinement.** §16 completeness at HEAD `2c2c6cc2`:
  8/15 (Claude draft) or 6/15 (§23 F2 refinement) → **12/15**
  (CDR-001 §5 evidence-based).
- **Missing-links refinement.** Item 14 3-item list from CDR-001 §7
  supersedes the graph §16 Item 14 4-item list. Add Gap 4 from
  CDR-001 §12.3 (Rigby's cross-channel dispatch contract
  normalization) → **4-item list at HEAD**.
- **Substrate confirmed shipped:** DocsContextBuilder-style receivers
  for Expo (`signals_push_notifications.on_critical_attention_item`
  S742-era PR #1458), Discord (S2735 PR #3038), Web Push (S2735
  PR #3040), all on `HumanAttentionItem.post_save` with
  `transaction.on_commit` + Celery task pattern. `HumanPreference`
  model (5 gate fields) + `_pref_gates_pass` shared helper.
- **§20 Tier reclassification.** §16 removed from Tier A (HIGHEST
  leverage); reclassified to Tier B / wrap-up bundle. 4 remaining
  items = 1–2 session wrap-up PR bundle, NOT a campaign.
- **§21 recommendation supersession.** F3's "§16 becomes second,
  blocked on discovery pass" is superseded — §16 no longer needs
  a campaign; wrap-up bundle queued behind the next campaign.
- **Canonical fanout pattern.** The receiver-driven pattern
  (`post_save` on unified event → `transaction.on_commit` →
  Celery task → re-load + re-gate → adapter) is the platform's
  ratified fanout shape. Any future chain proposing "fan-out"
  reads CDR-001 §2.3 as the reference implementation.

### §25.2 CDR-002 — §12 Knowledge Retrieval

Full record: `docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md`.

- **Trigger refinement.** §12 Item 4 (Trigger) — add: "PA turn
  `_build_context` auto-invocation via S773
  `PAKnowledgeInjector.get_context_for_query` (3s timeout,
  keyword-triggered system-state injection) + S943
  `DocsContextBuilder.build_context_for_agent` (5s timeout,
  docs-index lane)."
- **Failure-mode refinement.** §12 Item 10 — replace "PA turn
  does NOT auto-invoke either lane (retrieval is tool-call-only
  — asymmetry with `BaseAgent`)" with "PA turn auto-invokes
  keyword-triggered system-state (S773) + docs-index lane
  (S943); PA turn does NOT auto-invoke the embedding lane
  (`DocumentEmbedding` + pgvector). Two operational gates limit
  invocation: availability gate at `unified_pa_entrypoint.py:459-476`
  and early-return command paths at `:945-975`."
- **Missing-links refinement.** Item 14 — replace 2-item list
  ("(a) runtime lane selector, (b) PA symmetry") with 3-item
  list from CDR-002 §7:
  - Gap 1 — PA turn embedding-lane enrichment (M).
  - Gap 2 — runtime lane selector LOCAL vs PROD (S-M).
  - Gap 3 — PA/BaseAgent asymmetry closure OR design doc (S).
- **Score refinement.** §12 completeness 11/15 → **12/15**
  (CDR-002 §5).
- **Substrate confirmed shipped:** DocsContextBuilder (S798+S943,
  598 LOC), KnowledgeFirstRouter (S744, 729 LOC),
  ScopedRetrievalService (S786+S949, 712 LOC), BaseAgent hook
  (base_agent.py:1435), plus PAKnowledgeInjector (S773) —
  ~2,700+ LOC of already-shipped substrate. Two of the four
  are Rigby-SIGN-confirmed (Docs + KnowledgeFirstRouter); the
  other two carry a "cited-but-not-SIGN-verified" annotation
  discharged in P0.
- **Canonical PA turn enrichment surface.** The
  `UnifiedPAEntrypoint._build_context` sequence is the platform's
  canonical "auto-enrichment on every conversation" hook. Any
  future chain proposing "auto-invoke retrieval" should extend
  this hook, not parallel it.

### §25.3 Governance impact

- **Rule R2 (CDR discipline) discharged twice.** CDR-001 + CDR-002
  vindicate the CDR primitive across two consecutive Category A
  investigations. Playbook v0.1.1 methodology chapter should cite
  both when defining the pattern.
- **Rule R1 (Tool Autonomy Principle) proved out.** CDR-002 §12
  reconciliation is the reference case: Rigby's autonomy discovered
  PAKnowledgeInjector (S773) that Claude's grep missed, precisely
  because Claude did NOT prescribe grep patterns for her pass.
- **Graph scoring discipline.** Two consecutive graph "MISSING"
  claims (§16 + §12) proved to be under-credited shipped substrate.
  Future campaign selection MUST run Category A + optionally
  produce a CDR before treating a graph "MISSING" as a build
  directive. Cross-referenced: CDR-001 §11.1 + CDR-002 §11.1.

### §25.4 Active campaign

**§12 Knowledge Retrieval** — Chris ratified 2026-07-09.
Campaign SIGN pin `pa-5c76b58f70654409` (title
`campaign-s2736-knowledge-retrieval`). P0 begins immediately:
acceptance tests + independent substrate verification. P1-P4 per
CDR-002 §10.4. Any subsequent update to §12 in this graph MUST
cite CDR-002 (and any CDR-003+ that emerges) as authority.

---

## §26. §C5 Celery Eager-Mode Integration Verification (candidate chain — CDR-003 ratified 2026-07-09)

Candidate chain proposed by CDR-003 §8 Option A and ratified by Chris
2026-07-09. Frames a narrow, non-overclaimed capability for
integration testing that catches the class-of-bug §10.8.2-3
(SESSION_2737 handoff §10.8) at merge time — a class the receiver-side
`captureOnCommitCallbacks + patch(_ENQUEUE_PATH)` pattern cannot
catch.

### §26.1 Capability

"Selected Django integration tests can exercise: **receiver →
`transaction.on_commit` → Celery enqueue → task-body execution → ORM
side effect** against the test database before merge."

Chain::

    Test author writes `@pytest.mark.integration_celery`
      + `TestCase` subclass
      + `override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)`
      + `self.captureOnCommitCallbacks(execute=True)` context
      + producer save (e.g., `HumanAttentionItem.objects.create(...)`)
        → signal receiver fires
          → `on_commit` callback enqueues Celery task
            → task body runs INLINE (EAGER)
              → task body's ORM writes land in the test DB
                → test assertion on the real ORM row

### §26.2 Attributes (per graph 15-attribute template)

1  Human outcome — class-of-bug §10.8.2/10.8.3 caught at merge before shipping.
2  Trigger — test author authors an `integration_celery`-marked test.
3  Producer — `tests/conftest.py` + `pytest.ini` marker registration; `core/services/hai_dispatch_state.py`-style helpers where applicable.
4  Intermediate events — `on_commit` callback → EAGER `.delay(...)` inline → task body executes.
5  Consumers — test-author's assertion + CI runner + PR reviewer.
6  Persistence — test DB with savepoint rollback (`TestCase`, not `TransactionTestCase`).
7  Notifications — pytest report + CI status + PR check.
8  Frontend updates — N/A (test-time only).
9  Human attention — test failure blocks PR merge.
10 Failure modes — see §26.3 explicit boundary below.
11 Recovery — `pytest --create-db` for full test-DB reset; `--keepdb` for iterative dev.
12 Verification — 3 exemplars at `test_hai_runtime_integration.py`, `test_deliverable_intake_subscriber.py::EagerModeEndToEndTests`, `delegation_lifecycle_smoke_test`.
13 Existing tests — 3 exemplars (see #12) + full doc at `docs/testing/RUNTIME_INTEGRATION_TESTS.md`.
14 Missing links — none for the ratified narrow scope; broader Chapter 8 Runtime Discipline codification deferred to a future Playbook MINOR.
15 Effort — S-M **bundle already shipped** (CDR-003 authoring session).

Completeness: **14 of 15** at HEAD post-CDR-003 bundle merge. Item 14
is "none required for ratified scope."

### §26.3 Explicit boundary (Chris directive folded verbatim)

Per Chris's ratification directive: *"Do not overclaim this as
production-equivalent Celery verification. Explicitly document the
boundary."*

The `integration_celery` pattern **detects**:

- Task-body import errors (§10.8.2 class)
- Invalid model-field values (§10.8.3 class)
- Transaction-ordering defects
- ORM-side failures in the task's happy path

The pattern **does NOT replace**:

- Worker task-registry verification (§10.8.1 class — reachable only
  via a live worker)
- `make celery-recycle` after task-module changes
- `celery inspect registered`
- Queue-routing verification
- Serialization / concurrency verification
- End-to-end runtime smoke tests on live workers

Those remain runtime-close requirements and are candidate input for
the future PLAYBOOK Chapter 8 Runtime Discipline MINOR amendment
(currently STUB in `docs/ENGINEERING_PLAYBOOK.md`).

### §26.4 Discharge of CDR-002 §17.4 deferred future arc

CDR-002 §17.4 deferred a "PA `_build_context` integration-test
harness — proper Django TestCase fixture set covering profile +
memory + learned prefs + stats + workspace boundaries" as a future
arc. CDR-003 § C5 discharges that deferred arc by ratifying the
generalized pattern. Any future campaign proposing a
`_build_context` integration test reaches for the pattern documented
at `docs/testing/RUNTIME_INTEGRATION_TESTS.md` and adds a new
exemplar to that doc's `canonical_exemplars` frontmatter list.

### §26.5 Governance references

- CDR-003 authoritative record:
  `docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md`
- Doc pattern guide: `docs/testing/RUNTIME_INTEGRATION_TESTS.md`
- Marker registration: `pytest.ini` markers section +
  `tests/conftest.py` `pytest_configure`
- Ratified rules exercised: PLAYBOOK-2.2.2 (CDR discipline),
  PLAYBOOK-3.2.2 (acceptance-tests-first)
- Chris ratification directive: 2026-07-09
  ("Ratify all three decisions. ... Ratify §8 Option A. Add §C5 ...")
