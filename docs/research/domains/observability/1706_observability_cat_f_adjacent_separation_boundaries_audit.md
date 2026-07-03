---
title: "Group 1700 Cat F — Adjacent / Separation Boundaries Child Audit"
authority: child-audit
category: child_audit
session: 1706
child_slot: P6
domain_slug: observability
research_group: 1700
status: active
generated: 2026-07-03
verifier_loop: [pre-explore-verified, post-explore-verified, sign-cycle-1-signed-with-edits, folds-f1-f4-landed]
sibling_children:
  - 1701_observability_cat_a_celery_task_event_audit.md
  - 1702_observability_cat_b_llm_call_event_audit.md
  - 1703_observability_cat_c_agent_execution_audit.md
  - 1704_observability_cat_d_tool_call_record_audit.md
  - 1705_observability_cat_e_ops_run_event_audit.md
parent_scoping: 1700_observability_domain_scoping.md
canonical_summary: 1799_observability_canonical_summary.md (pending)
sub_slots:
  - F.a Body Systems / HeartBeat
  - F.b SLO framework audit
  - F.c Event-model catalog + WRITE-ONLY-FORGOTTEN audit
  - F.d Doc-claim verifier drift as meta-observability signal
  - F.e Observability↔Event-Architecture terminology boundary
---

# Group 1700 Cat F — Adjacent / Separation Boundaries Child Audit

> **Sixth and LAST child audit under Group 1700 (Observability arc) — precedes S1799 xx99 canonical summary.** Applies playbook §11.2 20-section child audit template + §13 6-parallel-Explore sweep + §14 verifier-loop discipline (pre-Explore + post-Explore). Cat F owns everything observability-adjacent that is NOT one of the 5 execution-telemetry layers (Cat A-E). Sub-slotted per parent §5.F Rigby SIGN cycle 1 F2 fold to prevent internal scope-magnet: F.a Body Systems / HeartBeat, F.b SLO framework, F.c 14 event-shaped models, F.d doc-claim verifier drift, F.e Observability↔Event-Architecture terminology. Feeds xx99 §5 D74 posture-decision brief with the sixth axis cell (OBSERVABILITY-FRAMEWORK-UNBOUNDED-RETENTION), a WRITE-ONLY-FORGOTTEN correction (1/14 not 3/14), and a permeable-boundary terminology recommendation.

---

## 1. Executive Summary

Cat F is the observability-adjacent bin: Body Systems health telemetry + SLO framework + 14 event-shaped Django models + doc-claim verifier + terminology boundary. Unlike Cat A-E which each own a single primary execution-telemetry layer, Cat F owns a heterogeneous surface unified by the negative-space definition ("everything else observability-adjacent"). Per parent §5.F stop conditions, this audit catalogs producer/consumer wiring, retention posture, and correlation-primitive presence per sub-slot; it does NOT design the SLO framework, does NOT propose HeartBeat export pipeline, does NOT act on event-model deprecation decisions, does NOT integrate verifier drift into observability infrastructure, and does NOT rename subsystems.

**Coverage at HEAD.** F.a HeartBeat table exists at `core/models_heart.py:25-103` (10 fields, no correlation columns); pulse writer runs every 600s via `core.tasks.run_heartbeat` beat-scheduled at `core/celery.py:39-42`. F.b SLO surface = 1 beat-scheduled task (`check_learning_loop_slo` at `core/tasks.py:13170`) + 1 beat-scheduled cost SLO (`check_llm_cost_spike` at `core/tasks_misc.py:5048`) + 8 on-demand hardcoded SLOs in `_ops_slo_status()` at `core/services/td_handlers_ops.py:365-648` (2-min cache, zero persistence). F.c 14 event-shaped models all exist as concrete Django models (verified pre-Explore), 11 WIRED-BOTH-SIDES + 2 WIRED-via-self-consumer + 1 truly WRITE-ONLY-FORGOTTEN. F.d doc-claim verifier at `core/services/doc_claim_verification.py` has **75 registered `@register_claim` decorators** and is consumed daily by `core/jobs/docs_cascade.py` (DRIFT_LABEL = `step_5_drift_observed`). F.e terminology boundary recommendation: **PERMEABLE with producer/consumer split** (execution telemetry Cat A-E = Group 1700 core; 14+ event models = observability-adjacent producers, Group 1900 owns consumer/routing side).

**Distinctive Cat F pattern.** The primary structural finding is a **passive-leak pattern** — writers work, readers work, but purge does not exist for the largest observability-adjacent tables. HeartBeat, DeliverableEvent, OpsRunEvent (S1705 F6 inheritance) all lack date-based retention despite comparable-cadence peer tables (LearningReadbackEvent 30-day at `core/celery.py:246`, FleetEvent 30-day at `core/services/fleet_event_cleanup.py:70`, CeleryTaskEvent weekly at `core/celery.py:cleanup_celery_task_events`) that DO have beat-scheduled purge. Cat F is not actively broken (Cat D F1) and not flag-gated (Cat E F1); it is silently accumulating disk.

**Candidate-surface dispositions (Rigby SIGN cycle 1 Q1 F1 fold).** Four candidate surfaces were considered for Cat F inclusion and dispositioned OUT of scope to close the "did we miss an observability-adjacent surface?" loop: (a) **resolve_node / DaVinci / render infrastructure telemetry** — separate media/render ops subsystem, not Group 1700 observability core spine; LOW impact on F9 axis; (b) **memory_pressure signals (`ops_tool.memory_pressure` / worker_memory snapshots)** — ops surface, not an Event Architecture model; does not alter Cat F boundary conclusions; LOW-MED impact on F9 axis (strengthens "observability exists" but doesn't change the retention/unbounded-growth claim); (c) **fleet-side auth token audit** — security/compliance desk surface, not Cat F; LOW impact; (d) **sibling `RIGBY_*_INTAKE_ENABLED` flags beyond `RIGBY_EVENT_INTAKE_ENABLED` + `RIGBY_DELEGATION_ENABLED`** — none found/relied upon for Cat F conclusions; LOW impact.

**Maturity STABLE for HeartBeat writer + PARTIAL for SLO framework (single-task + on-demand-hardcoded) + STABLE for 14-model event taxonomy (with one WRITE-ONLY-FORGOTTEN outlier) + DESIGN-INTENT-LATENT for doc-claim verifier (built but not observability-integrated) + BOUNDARY-CLARIFIED for terminology (permeable recommendation for xx99 §5) + Risk MEDIUM.**

### 1.1 Findings lock-in (F1-F9)

| # | Severity | Section | Finding |
|---|----------|---------|---------|
| **F1** | HIGH | §14+§15 | **Passive-leak retention pattern.** HeartBeat + DeliverableEvent + OpsRunEvent lack date-based purge tasks despite comparable-cadence peer tables (LearningReadbackEvent, FleetEvent, CeleryTaskEvent) all having beat-scheduled cleanup. Contrast: `heart-service-heartbeat` (`core/celery.py:39-42`) writes every 600s but no `purge-heartbeat-*` counterpart exists in `core/celery.py`. Growth projection at 10-min cadence: 144/day × 365 = ~52.5K HeartBeat rows/year unbounded. Structural inheritance of S1705 F6 + S1704 F5 + S1702 F4 + S1701 F6 across Cat F surface. |
| **F2** | MEDIUM | §14 | **10-vs-9 body systems drift.** `core/services/body_vitals.py:340-790` defines 10 getter methods (`_get_heart_vitals`, `_get_lungs_vitals`, `_get_circulatory_vitals`, `_get_spine_vitals`, `_get_immune_vitals`, `_get_digestive_vitals`, `_get_muscular_vitals`, `_get_brain_vitals`, `_get_skin_vitals`, **`_get_nervous_vitals`**). PLATFORM_INVENTORY.md line 24 + CLAUDE.md `Live Counts` autoblock both claim "9 body systems monitored by run_all_systems_scan." Nervous is the missing 10th. Runtime works correctly; drift on-doc-only. Owed to xx99 anchor-update PR + `python manage.py refresh_doc_inventory_blocks` regeneration to catch the 10th. |
| **F3** | MEDIUM | §14 | **`check_learning_loop_slo` line drift.** Parent §5.F, start-here L89, and S1273 line 1969 all cite `core/tasks.py:12492`. Actual position at HEAD: `core/tasks.py:13170` — +678 line drift. Confirmed via grep. Owed to xx99 anchor-update PR. |
| **F4** | POSITIVE differentiator (§17) | §17 | **1/14 not 3/14 event-shaped models are WRITE-ONLY-FORGOTTEN.** Pre-Explore Agent 3 report claimed 3 (CockpitIncidentEvent, CockpitAutopilotEvent, ABTestEvent). Post-Explore verifier-loop correction: CockpitIncidentEvent is consumed via `core/views_diagnostics.py:3889` (`CockpitIncidentEvent.objects.filter(incident=inc).order_by('created_at')`); CockpitAutopilotEvent is consumed via `core/views_diagnostics.py:3367` (`CockpitAutopilotEvent.objects.select_related('policy')[:limit].values(...)`). Only **ABTestEvent** (writer at `core/views_ab_testing.py:481`; no consumer sites in main core after grep) is truly WRITE-ONLY-FORGOTTEN. Cat F event-model surface is healthier than S1273 lines 1912-1917 hypothesized. |
| **F5** | MEDIUM | §15 | **SLO surface = 2 beat-scheduled tasks + 8 on-demand hardcoded + 0 persistence layer.** `check_learning_loop_slo` (`core/tasks.py:13170`, daily 9 AM Denver) + `check_llm_cost_spike` (`core/tasks_misc.py:5048`, `HumanAttentionItem` alert action) are the 2 scheduled TRUE-SLOs. `_ops_slo_status()` at `core/services/td_handlers_ops.py:365-648` computes 8 additional SLOs (celery task success ≥99.9%, agent success ≥99.95%, agent timeout ≤0.2%, deliberation zero-turn ≤0.1%, content publish conversion ≥40%, publish-ready age p95 ≤72h, PA tool success ≥99.9%, HTTP failure ≤5%) as if/elif branches with 2-min cache — no persistence, no historical audit. CTO/COO/Trend Analysis dailies at `core/services/diagnostics/{cto_daily,coo_daily}.py` + `core/services/scheduled_diagnostic_runner.py` are threshold-gated alert escalators, NOT SLO monitors. No `SLOResult` / `SLABreach` / `ServiceLevelObjective` model exists across `core/models*.py`. |
| **F6** | POSITIVE (§11) | §11 | **Doc-claim verifier is comprehensive but not observability-integrated.** `core/services/doc_claim_verification.py` (128,672 bytes, 3275 lines, 75 `@register_claim` decorators verified via `grep -c`) covers agent counts (7), PA tools (13), spider (4), Celery (5), services (5), agent structural integrity (5+). Consumed daily via `core/jobs/docs_cascade.py:105 DRIFT_LABEL="step_5_drift_observed"` emitting `OpsRunEvent.detail` with `drift_count` + `drift_items_count`. Embedded in `PLATFORM_INVENTORY.md` via `core/services/platform_inventory.py:605-639`. But: zero dedicated persistence table (no `DocClaimDrift` model), zero CI/GitHub Actions gating (`--fail-on-drift` unused in `.github/workflows/*.yml`), zero alert/notification integration. Classification: **DESIGN-INTENT-LATENT** (S1705 F1 analog) — telemetry-worthy candidate awaiting explicit observability-boundary crossing per xx99 §5 posture-decision brief. |
| **F7** | POSITIVE (§17) | §17 | **HeartBeat + BodyVitalsService + 10 body systems are structurally intact.** Producer wired (`run_heartbeat` @ `core/celery.py:39-42` every 600s, executes `heart.pulse()` at `core/services/heart.py:121-201` → `record_heartbeat()` at `:649-665` writing to HeartBeat table). 4 consumer sites: REST at `core/views_heart.py:78, 705`, agent narrative at `core/agents/content_writer_agent.py:544`, task-detail debug at `core/services/td_handlers_ops.py:3845, 4917, 4943`. Redis pub/sub publish at `core/tasks_misc.py:3045` (no consumer for `heart:status` channel found). Discord alert path at `core/services/heart.py:667-698`. S1273 line 1965 export gap VERIFIED as integration-gap (REST endpoints exist; frontend `.tsx/.ts` files show ZERO imports of `/api/heart/*`). S1273 line 1964 "digestive+muscular sluggish/paralyzed on fresh DB" claim NOT verified via code — cold-start logic in `core/services/digestive.py:103-114` + `core/services/muscular.py:115-170` defaults to healthy/strong (100.0 score) on zero-execution baseline. Flagged SPECULATIVE. |
| **F8** | MEDIUM (§16) | §16 | **Observability↔Event-Architecture boundary recommendation: PERMEABLE with producer/consumer split.** Execution telemetry (Cat A-E) unambiguously Group 1700 core scope. 14+ event-shaped models are observability-adjacent PRODUCERS (state-change telemetry records) whose CONSUMERS (routing logic, decision gates, integrations) belong to Group 1900 Event Architecture. Not a naming problem — a producer/consumer structural division. Terminology stability grid: Event/Telemetry/Observation/Signal DRIFTED (codebase uses "event" for both routing and audit-only cases); Metric/Log/Trace UNSTABLE (trace_id dead on deprecated `AgentExecution` per S1703 F1 landmine); Alert/Notification/Incident STABLE; Monitor/SLO/Health-check DRIFTED; Producer/Emitter/Writer STABLE; Consumer/Aggregator/Sink STABLE. Recommendation for xx99 §5 posture-decision brief: catalog as **PERMEABLE**, do NOT rename subsystems at HEAD. |
| **F9** | D74 axis contribution (§9) | §9 | **RETENTION-PATTERN-INCONSISTENT (unbounded growth across key observability/event tables).** Cat F contributes a sixth axis cell to the cross-cat correlation matrix distinct from Cat A DEEP-WIRED, Cat B DEEP-WIRED-BUT-DEDUP-UNRESOLVED, Cat C COVERAGE-GAP-ON-PA-PATH, Cat D ACTIVELY-BROKEN, Cat E LATENT-VIABLE-BUT-FLAG-GATED. Cat F tables are WRITING + READING correctly (not broken like Cat D, not flag-gated like Cat E) but retention is uneven — some peer tables (LearningReadbackEvent, FleetEvent, CeleryTaskEvent) have working purge; the highest-cadence Cat F peers (HeartBeat, DeliverableEvent, OpsRunEvent) do not. **This is a cross-cat pattern (A/B/D/E/F evidence), with Cat F serving as the consolidation/ratification point rather than a unique root cause** (Rigby SIGN cycle 1 Q3 F2 fold). Feeds xx99 §5 evidence brief as the "peer-comparison" input — if D74 posture selects canonical-unification, retention policy design belongs in the spine ADR; if structural-separability, retention policy is per-layer follow-on. |

---

## 2. Domain Purpose

Cat F answers three overlapping "why does this exist" questions:

1. **Body Systems (F.a) purpose.** Provide a self-diagnostic health signal for the platform's internal control loops — RSS pressure, agent execution success rate, LLM latency, workspace operation success. The 10 body systems each own a domain-specific health metric (LUNGS = budget/token, MUSCULAR = agent execution, BRAIN = LLM, etc.); HeartBeat is the periodic snapshot that aggregates the components into a coarse operational verdict (healthy / degraded / critical / offline) with a 0-100 numeric score.

2. **SLO framework (F.b) purpose.** Detect and surface service-level degradation (learning loop underuse, cost spikes, task success rate drops) with a threshold verdict → downstream action (log, HumanAttentionItem, agent dispatch). Today the surface is single-task + on-demand-hardcoded rather than a first-class framework.

3. **Event-shaped models (F.c) + doc-claim verifier (F.d) + terminology (F.e) purpose.** F.c models straddle observability (state-change telemetry records) and event architecture (producer/consumer patterns delegated to Group 1900). Doc-claim verifier is a meta-observability tool — treating docs as an artifact and drift as a signal. Terminology work protects the Group 1700↔Group 1900 handoff at xx99.

**What Cat F does NOT own:**

- Event bus adoption + schema versioning (Group 1900 delegation per parent D2).
- DeliverableEvent consumer contract (Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E).
- BodyCoordinator autonomic reflex correctness (Employee OS concurrent scope).
- Individual body-system service internal correctness (per parent §7 anti-scope).
- Verifier bug fixes (per parent §7 item 15).
- SLO framework design (per parent §6.1 parked candidate).

---

## 3. Canonical Entry Points

| Sub-slot | File:Line | Purpose |
|----------|-----------|---------|
| F.a HeartBeat model | `core/models_heart.py:25-103` | Persistence layer for periodic pulse snapshot |
| F.a Heart service | `core/services/heart.py:121-201` (pulse) + `:649-665` (record_heartbeat) | Pulse execution + persistence |
| F.a BodyVitalsService | `core/services/body_vitals.py:126-189` (get_all_vitals) + `:340-790` (10 getters) | On-demand full-body aggregation |
| F.a Heartbeat beat task | `core/celery.py:39-42` (`heart-service-heartbeat`) | Every-600s pulse scheduler |
| F.a `run_heartbeat` task | `core/tasks.py:7403-7406` (dispatch) + `core/tasks_misc.py:3004-3063` (`_impl_run_heartbeat`) | Task body |
| F.b `check_learning_loop_slo` | `core/tasks.py:13170` (task def) + `core/celery.py:599-602` (beat @ 09:00 Denver) | Daily learning usage SLO (threshold 5% over 24h) |
| F.b `check_llm_cost_spike` | `core/tasks_misc.py:5048` | LLM hourly spend spike alert (creates `HumanAttentionItem`) |
| F.b `_ops_slo_status` | `core/services/td_handlers_ops.py:365-648` | 8 on-demand SLOs, 2-min cache, no persistence |
| F.b Diagnostics runner | `core/services/scheduled_diagnostic_runner.py` + `core/services/diagnostics/{cto_daily,coo_daily}.py` | Threshold-gated alert escalators (NOT SLOs) |
| F.c 14 event models | See §4 Major Models table | Producer surface |
| F.d Doc-claim verifier | `core/services/doc_claim_verification.py` (3275 lines, 75 `@register_claim`) | Claim registry |
| F.d `verify_doc_claims` command | `core/management/commands/verify_doc_claims.py` (166 lines) | Runner CLI |
| F.d Docs cascade consumer | `core/jobs/docs_cascade.py:105, 386, 612, 677` | Daily drift observer emitting `step_5_drift_observed` OpsRunEvent |
| F.d Inventory embedder | `core/services/platform_inventory.py:605-639` | PLATFORM_INVENTORY.md drift-summary section |
| F.e Terminology corpus | `docs/EVENT_SYSTEM_INVENTORY.md` + `docs/topics/{celery-workers,agent-system,employee-os}.md` | Doc-side terminology drift catalog |

---

## 4. Major Models

### 4.1 HeartBeat (F.a)

**File:** `core/models_heart.py:25-103`. 10 fields.

| Field | Type | Line | Notes |
|-------|------|------|-------|
| `id` | UUIDField (PK) | 32-36 | Auto-generated |
| `health_score` | FloatField | 40-41 | 0-100 percentile |
| `overall_status` | CharField + StatusChoices | 43-48 | Indexed. {HEALTHY, DEGRADED, CRITICAL, OFFLINE} |
| `is_alive` | BooleanField | 50-52 | Quick operational flag |
| `components` | JSONField | 56-59 | Nested per-component health map |
| `check_duration_ms` | IntegerField | 62-63 | Latency of pulse check |
| `components_checked` | IntegerField | 65-66 | Cardinality of polled components |
| `components_healthy` | IntegerField | 68-69 | Healthy count |
| `alerts_sent` | BooleanField | 73-75 | Discord alert dispatch flag |
| `recorded_at` | DateTimeField | 79-82 | Indexed. Default `timezone.now`. |

Computed `components_degraded` property at line 100-102 = `components_checked - components_healthy`.

**No correlation columns** (`trace_id` / `execution_id` / `task_id` / `mission_id` absent). Body-system-scoped only.

**No retention primitive** — no `on_delete` cascade to a parent, no TTL, no purge task. See F1.

### 4.2 14 event-shaped models (F.c)

Verified via pre-Explore that all 14 are concrete Django models at HEAD:

| # | Model | File:Line | Producer sites | Consumer sites | Retention | Correlation ID | Verdict |
|---|-------|-----------|---------------|---------------|-----------|--------|---------|
| 1 | DeliverableEvent | `core/models_deliverables.py:561` | `core/signals/deliverable_status_signals.py:205` | `core/services/ops_autopilot/intelligence.py:812,874,878`; `core/services/diagnostics/coo_daily.py:474,493,510`; `core/views_deliverables.py`; `core/employees/status.py` | Meta ordering only (no purge) | MISSING | WIRED-BOTH-SIDES |
| 2 | ImpactEvent | `core/models_impact_events.py:21` | `core/services/ops_autopilot/impact.py:375,431,488` | `core/services/ops_autopilot/budget.py`; `core/services/ops_autopilot/experiment.py`; `core/services/diagnostics/coo_daily.py`; `core/views_diagnostics.py` | Meta ordering + 3 composite indexes (no purge) | trace_id at `models_impact_events.py:71` | WIRED-BOTH-SIDES |
| 3 | EngagementEvent | `core/models_engagement.py:18` | UNKNOWN (no `.create()` grep hits — may be webhook/import path) | `core/services/ops_autopilot/engagement.py:260,280,302,335,357,380,400,402,409,416` | Meta ordering only | trace_id (CharField) at `models_engagement.py:116` | PRODUCER-ONLY-BY-DESIGN |
| 4 | TriggerEvent | `core/models_situation_triggers.py:389` | `core/models_situation_triggers.py:377` | `core/views_spider_intelligence.py`; `core/services/system_state_aggregator.py`; `core/services/system_reality_checker.py`; `core/services/proactive_intelligence.py`; `core/views_autonomous_dashboard.py` | Meta ordering + 3 composite indexes | MISSING | WIRED-BOTH-SIDES |
| 5 | FleetEvent | `core/models/fleet.py:462` | `core/services/fleet_events.py:91` | `core/views_fleet_events.py`; `core/services/fleet_event_cleanup.py` | **30-day HARD-DELETE** via `core/services/fleet_event_cleanup.py:70` (`FLEET_EVENT_RETENTION_DAYS=30`) | MISSING | WIRED-BOTH-SIDES **(RETENTION EXEMPLAR)** |
| 6 | CockpitIncidentEvent | `core/models_cockpit_incidents.py:41` | `core/views_diagnostics.py:3819, 3957, 4009` | `core/views_diagnostics.py:3889` (`filter(incident=inc).order_by('created_at')`) — **verifier-loop correction vs Agent 3** | Meta ordering + CASCADE FK to CockpitIncident | MISSING | WIRED-BOTH-SIDES (self-consumer in diagnostics UI) |
| 7 | CockpitAutopilotEvent | `core/models_cockpit_autopilot.py:33` | `core/views_diagnostics.py:3144` | `core/views_diagnostics.py:3367` (`select_related('policy')[:limit].values(...)`) — **verifier-loop correction vs Agent 3** | Meta ordering + CASCADE FK to CockpitAutopilotPolicy | MISSING | WIRED-BOTH-SIDES (self-consumer in diagnostics UI) |
| 8 | ThreatEvent | `core/models_immune.py:119` | `core/services/immune.py:402` | `core/services/immune.py` (self-consume via `pattern.total_detections` aggregate) | Meta ordering + 5 composite indexes | MISSING | WIRED-BOTH-SIDES |
| 9 | ABTestEvent | `core/models_unified_system.py:8686` | `core/views_ab_testing.py:481` | **ZERO consumer sites found across core** | Meta ordering + 2 indexes | MISSING | **WRITE-ONLY-FORGOTTEN** |
| 10 | ConversionEvent | `core/models_unified_system.py:19761` | `core/services/roi_tracker.py:198` | `core/services/roi_tracker.py:182,263,320,637,901,938`; `core/views_roi_metrics.py` | Meta ordering + 3 composite indexes | MISSING (attribution_source/medium/campaign present but no trace_id) | WIRED-BOTH-SIDES |
| 11 | BadContextEvent | `core/models_unified_system.py:21158` | `core/services/context_tracing.py:400` | `core/services/context_tracing.py` (`get_recent_by_agent/trace`); `core/views_diagnostics.py` | Meta ordering + 3 composite indexes | trace_id (CharField) at `models_unified_system.py:21187` | WIRED-BOTH-SIDES |
| 12 | RelationshipEvent | `core/models_unified_system.py:12418` | `core/views_agent_relationships.py:188,232,243` | `core/views_agent_relationships.py` (implicit via FK aggregate) | Meta ordering only | MISSING | WIRED-BOTH-SIDES |
| 13 | AuditLog | `core/models_unified_system.py:19302` | `core/views_personal_assistant.py`; `core/views_diagnostics.py`; `core/services/fleet_auth.py`; `core/services/provenance_tracker.py` | `core/services/ops_autopilot/intelligence.py`; `core/views_diagnostics.py`; `core/views_provenance.py`; `core/services/provenance_tracker.py` | Meta ordering + `action_type` indexed | MISSING | WIRED-BOTH-SIDES |
| 14 | NotificationLog | `core/models_push_notifications.py:183` | `core/services/push_notification_service.py` (via `PushSubscription` related) | `core/services/push_notification_service.py` (self-consume via `sent_at` filter) | Meta ordering + 2 composite indexes | MISSING | WIRED-BOTH-SIDES |

**Cross-cutting summary matrix:**

| Metric | Numerator | Denominator | % |
|--------|-----------|-------------|---|
| **WIRED-BOTH-SIDES** (active producer + consumer) | 12 | 14 | 85.7% |
| **PRODUCER-ONLY-BY-DESIGN** | 1 | 14 | 7.1% (EngagementEvent — no `.create()` grep hit; may be webhook path) |
| **WRITE-ONLY-FORGOTTEN** | 1 | 14 | 7.1% (**ABTestEvent** only, post-verifier-loop correction) |
| **DEAD** (no producer + no consumer) | 0 | 14 | 0% |
| **With date-based retention purge task** | 1 | 14 | 7.1% (FleetEvent only) |
| **Carrying trace_id / execution_id / task_id / mission_id** | 3 | 14 | 21.4% (ImpactEvent, EngagementEvent, BadContextEvent) |

**Interpretation.** The event-model surface is healthier than the S1273 hypothesis anticipated. Only ABTestEvent is truly orphan. Retention is the systemic gap, not producer/consumer wiring. Correlation-ID coverage is thin but higher than Cat E (0/224 rows carry cross-cat IDs per S1705 F1) because 3 tables have trace_id columns as first-class fields.

---

## 5. Major Services

### 5.1 BodyVitalsService (F.a)

`core/services/body_vitals.py`, ~858 lines. `SYSTEM_GETTERS` dict at :54-65 maps 10 system names → getter method names. `get_all_vitals(include_details=False)` at :126-189 iterates all 10 getters. Each getter (`_get_heart_vitals` … `_get_nervous_vitals`) calls the underlying service singleton's `.get_vitals()` / `.digest()` / `.flex()` / `.think()` / `.feel()` method and returns a normalized dict. Aggregation is in-memory; results cache in Redis (short TTL) via body-vitals internal path, not persisted.

**Key: NOT autonomously beat-scheduled.** `run_heartbeat` at `core/tasks.py:7403-7406` invokes `heart.pulse()` (not `get_all_vitals()`); `get_all_vitals()` is invoked on-demand from REST endpoints, PA context, agent narrative.

### 5.2 HeartMonitorService (F.a)

`core/services/heart.py`, ~700 lines. `.pulse()` at :121-201 checks 8 named components (brain, nervous, organs, sensory, skin, memory, celery, resolve_node), computes `health_score` from healthy/total ratio (thresholds at :175-177 map 80/50 boundaries to excellent/degraded/critical), calls `record_heartbeat()` at :649-665 to persist. `alert_if_critical()` at :667-698 fires Discord webhook on `status='critical'`.

### 5.3 10 body-system service singletons (F.a)

`core/services/{heart,lungs,circulatory,spine,immune,digestive,muscular,brain,skin,nervous}.py`. Each exports a service singleton with a domain-specific `.get_vitals()` / `.digest()` / `.flex()` / `.think()` / `.feel()` method. Metrics are persisted to per-system pulse tables (BreathCycle, CirculationPulse, SpineStatus, ImmuneStatus, DigestivePulse, MuscularPulse, BrainPulse, SkinPulse, and NERVOUS's persistence layer). **Individual per-system service correctness is out of scope per parent §6.4/§6.5 parked candidates.**

### 5.4 Scheduled Diagnostic Runner (F.b analog)

`core/services/scheduled_diagnostic_runner.py`. Generic two-task orchestration (run + post) called by CTO/COO/Trend daily diagnostics (`core/services/diagnostics/{cto_daily,coo_daily}.py` + trend equivalents). Threshold gates via env vars (CTO_DIAG_FAILRATE_HIGH=0.06 default, CRIT=0.10, etc.; COO gates 13 tunables — VELOCITY_DROP_PCT=0.30, etc.). On breach → dispatch corresponding *Agent + post to `attention_bridge.create_diagnostic_alert()` as `type='cto_daily_diagnostic'` etc. Dedupe + cooldown via cache (36h TTL dedupe key, 20h/6h cooldowns by severity). **Not SLOs** — alert escalators.

### 5.5 Doc-claim verifier (F.d)

`core/services/doc_claim_verification.py`, 3275 lines, 75 `@register_claim` decorators. `ClaimResult` dataclass at :71-116 carries `matched`/`expected`/`actual`/`severity` (`ok|skipped|low|medium|high|critical|error`). `register_claim` decorator at :131-155 populates module `_REGISTRY` list. `run_all()` / `run_filtered()` at :233-247 execute with optional doc filter + `only_drift` flag. `summarize()` at :250-278 rolls up counts by severity + doc.

Consumers: (a) `core/management/commands/verify_doc_claims.py` (CLI runner, 166 lines); (b) `core/services/platform_inventory.py:605-639` (embed drift snapshot into PLATFORM_INVENTORY.md); (c) `core/jobs/docs_cascade.py:105, 386, 612, 677` (daily post-flight drift observation → `step_5_drift_observed` OpsRunEvent).

---

## 6. Major APIs and Interfaces

### 6.1 HeartBeat REST surface (F.a)

- `GET /api/heart/pulse/` at `core/views_heart.py:21-77` — trigger fresh pulse + persist row + Discord alert on critical.
- `GET /api/heart/status/` at `core/views_heart.py:78` — latest HeartBeat row (`.order_by('-recorded_at').first()`).
- `GET /api/heart/history/` at `core/views_heart.py:705` — history query with `recorded_at__gte=cutoff`.

### 6.2 SLO surface (F.b)

- `check_learning_loop_slo` output = task return dict (`ignore_result=True`, so discarded by Celery result backend); logs only.
- `_ops_slo_status` reachable via `ops_tool` PA tool → 8 SLO verdicts + 2-min cache. No REST endpoint dedicated to SLO status.

### 6.3 Doc-claim verifier CLI (F.d)

- `python manage.py verify_doc_claims` with flags `--doc <path>`, `--only-drift`, `--format {text,json}`, `--list`, `--fail-on-drift` (see `core/management/commands/verify_doc_claims.py:52-61`). Zero CI/GitHub Actions gates use `--fail-on-drift`; developer-invocation-only.

---

## 7. Runtime Flows

### 7.1 HeartBeat pulse cycle (F.a, every 10 min)

1. Celery Beat fires `heart-service-heartbeat` per `core/celery.py:39-42` → dispatches `core.tasks.run_heartbeat`.
2. `run_heartbeat` at `core/tasks.py:7403-7406` → `_impl_run_heartbeat` at `core/tasks_misc.py:3004-3063`.
3. `HeartMonitorService.pulse()` at `core/services/heart.py:121-201` polls 8 named components.
4. `record_heartbeat()` at `:649-665` writes HeartBeat row.
5. Redis publish at `core/tasks_misc.py:3045` to `heart:status` channel (**no consumer found**).
6. If `status='critical'` → `alert_if_critical()` at `:667-698` sends Discord.

### 7.2 SLO daily verdict (F.b, `check_learning_loop_slo`)

1. Beat fires at 09:00 Denver per `core/celery.py:599-602`.
2. Task at `core/tasks.py:13170` queries `core_learningreadbackevent` for 24h window; counts total / learning_used / prompt_injection_applied.
3. Calculates `usage_rate = used / total * 100`.
4. If `used == 0` → `logger.warning()`; if `usage_rate < 5%` → `logger.info("Below target")`; else `logger.info("OK")`.
5. Return dict discarded (`ignore_result=True`).

### 7.3 Doc-claim drift observation (F.d, daily via docs_cascade)

1. `docs_cascade` mission runs per Employee OS daily schedule.
2. Post-flight step 5 at `core/jobs/docs_cascade.py:386` invokes `verify_doc_claims --only-drift --format json`.
3. On success → emit `step_5_drift_observed` info OpsRunEvent with `detail = {"drift_count": N, "drift_items_count": M}` at `:424-430, :458-465, :612-677`.
4. On failure → escalation via Deliverable + PA chat at `:471-575`.
5. **No dashboard consumer, no alert on threshold, no notification. Purely observational.**

---

## 8. Data Ownership and Lifecycle

Per parent §5.F stop conditions Cat F does NOT own individual per-system model correctness (deferred to Employee OS / body-systems reliability). Cat F does own the aggregate observability contract: (a) HeartBeat table persists periodic snapshots; (b) 14 event-shaped models persist domain-scoped state transitions; (c) doc-claim verifier persists no state (compute-and-emit-only) except via `docs_cascade` writing OpsRunEvent detail.

**Retention posture summary (F1 evidence):**

| Table | Cadence | Purge task | Growth projection |
|-------|---------|-----------|--------------------|
| HeartBeat | ~144/day (10 min) | **NONE** | ~52.5K rows/year unbounded |
| DeliverableEvent | Per state transition | **NONE** | Grows with deliverable throughput |
| OpsRunEvent (S1705 F6 ref) | Per mission step | **NONE** | ~4,088/year projected per S1705 |
| LearningReadbackEvent | Per learning readback | `cleanup_learning_readback_events` @ `core/celery.py:246` (30d) | Bounded |
| FleetEvent | Per fleet action | `fleet_event_cleanup` @ 30d (`core/services/fleet_event_cleanup.py:70`) | Bounded |
| CeleryTaskEvent (S1701 F6 ref) | Per Celery task | `cleanup_celery_task_events` weekly (~7d cutoff) | Bounded |

The peer contrast is the load-bearing evidence for F1 severity: THREE tables (LearningReadbackEvent, FleetEvent, CeleryTaskEvent) have working purge tasks, showing that retention IS a solved pattern in this codebase — it's simply not extended to HeartBeat / DeliverableEvent / OpsRunEvent.

---

## 9. Integrations With Other Domains

### 9.1 D74 axis contribution

Cat F extends the D74 cross-cat axis matrix with a **sixth cell**:

| Cat | Axis cell | Evidence |
|-----|-----------|----------|
| Cat A CeleryTaskEvent | DEEP-WIRED | S1701 F9 |
| Cat B LLMCallEvent | DEEP-WIRED-BUT-DEDUP-UNRESOLVED | S1702 F9 |
| Cat C AgentExecution | COVERAGE-GAP-ON-PA-PATH | S1703 F9 |
| Cat D ToolCallRecord | ACTIVELY-BROKEN (100% NULL trace_id) | S1704 F9 |
| Cat E OpsRunEvent | LATENT-VIABLE-BUT-FLAG-GATED | S1705 F9 |
| **Cat F Adjacent surface** | **RETENTION-PATTERN-INCONSISTENT (unbounded growth across key observability/event tables)** | **S1706 F9 (this audit)** |

**Interpretation.** Cat F is the "not-broken, not-flag-gated, not-coverage-gapped, but-uneven-retention" cell. **This is a cross-cat pattern (A/B/D/E/F evidence), with Cat F serving as the consolidation/ratification point rather than a unique root cause** (Rigby SIGN cycle 1 Q3 F2 fold). Feeds xx99 §5 posture-decision brief as evidence that even correctly-wired observability surfaces suffer if retention discipline is left implicit. If xx99 D74 posture selects **canonical unification** (single execution_id + trace_id spine), retention should be a first-class field in the spine ADR. If posture selects **structural separability**, retention becomes a per-layer follow-on with Cat F as the primary evidence for prioritizing HeartBeat / OpsRunEvent / DeliverableEvent first.

### 9.2 Cross-domain integrations

| Peer | Integration point | Direction |
|------|-------------------|-----------|
| Employee OS | HeartBeat consumed by content_writer narrative at `core/agents/content_writer_agent.py:544`; docs_cascade emits step_5_drift_observed OpsRunEvent | Inbound (both) |
| Cat E OpsRunEvent | docs_cascade writes `detail={"drift_count":N}` per S1705 §5 discussion; RIGBY_EVENT_INTAKE flag also gates DeliverableEvent side | Inbound + outbound |
| Group 1600 Content | DeliverableEvent producer wired; consumer contract handoff at Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E | Cross-arc |
| Group 1900 Event Architecture (future) | 14+ event-shaped model consumers/routing/schema versioning is Group 1900 scope | Delegated |
| Employee OS body-systems reliability | Cold-start behavior (S1273 line 1964) + export gap (S1273 line 1965) fixes deferred to Employee OS | Delegated |

---

## 10. Event Flows

Cat F is the LARGEST source of event-shaped rows in the codebase per §4.2 matrix. Producers span:

- `core/signals/*` (`deliverable_status_signals.py:205` DeliverableEvent; `rigby_delegation_signals.py` OpsRunEvent when RIGBY_DELEGATION_ENABLED)
- `core/services/*` (impact.py ImpactEvent; roi_tracker.py ConversionEvent; immune.py ThreatEvent; context_tracing.py BadContextEvent; fleet_events.py FleetEvent; heart.py HeartBeat)
- `core/views_*` (views_diagnostics.py Cockpit*Event; views_ab_testing.py ABTestEvent; views_agent_relationships.py RelationshipEvent)
- `core/models_situation_triggers.py:377` TriggerEvent (model-internal producer)

**Consumers span:**

- Ops Autopilot intelligence (`core/services/ops_autopilot/*.py` — DeliverableEvent + ImpactEvent + AuditLog + EngagementEvent)
- COO daily diagnostics (`core/services/diagnostics/coo_daily.py` — DeliverableEvent + ImpactEvent)
- Diagnostic views (`core/views_diagnostics.py` — CockpitIncidentEvent + CockpitAutopilotEvent + BadContextEvent + AuditLog)
- REST endpoints (`core/views_deliverables.py`, `core/views_roi_metrics.py`, `core/views_agent_relationships.py`, etc.)
- Self-consume via aggregate/rollup patterns (ThreatEvent, NotificationLog, RelationshipEvent)

**Cross-cat correlation.** 3/14 tables carry trace_id (ImpactEvent, EngagementEvent, BadContextEvent). 0/14 carry execution_id or task_id at HEAD. If Group 1700 xx99 posture selects canonical unification, Cat F event models are candidate homes for the spine per §9.1.

---

## 11. Existing Documentation

### 11.1 Prior research anchors

- `docs/EVENT_SYSTEM_INVENTORY.md` — 14+ event-model catalog + producer/consumer + boundary framing at §3 line 373-376 ("emission is rich; consumption solid; decision layer empty").
- `docs/topics/celery-workers.md` §Observability at lines 182-305 — CeleryTaskEvent framed as **telemetry** (audit record), not event.
- `docs/topics/agent-system.md` at lines 107-113 — ToolCallRecord framed as **audit trail** (`__init_subclass__()` decorator).
- `docs/topics/employee-os.md` at lines 19-27 — OpsRun/OpsRunEvent framed as **audit**, evidence trail includes 4-way postmortem join at :64-65 (S1705 F7 named-but-broken).
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor (not a counts source).
- `docs/PLATFORM_INVENTORY.md` — runtime anchor; line 24 asserts "9 body systems" (**F2 drift**).
- `docs/research/platform_architecture_inventory.md` (S1273) — lines 1912-1917 catalog 14+ event models; lines 1964-1965 flag HeartBeat cold-start + export gaps; line 1969 flags SLO ad-hoc-only.
- `CLAUDE.md` — Live Counts autoblock references 9 body systems (**F2 drift**).

### 11.2 Prior audit anchors

- S1701 Cat A audit (F6 no-retention).
- S1702 Cat B audit (F4/F5 no-retention).
- S1703 Cat C audit (F1-F3 3-class landmine + F4 PA path coverage gap).
- S1704 Cat D audit (F1 trace_id 100% NULL, F4 mining pipeline gap, F5 no-retention).
- S1705 Cat E audit (F1 detail-JSON correlation 0/224 + F4 CTO/COO/Trend fully-wired POSITIVE differentiator + F5 producer-only + F6 no-retention + F7 named-but-broken evidence_for_mission join + F8 MissionRunner I1-I9 verified).

---

## 12. Research Coverage

Cat F sub-slots inherit prior research at these anchor points:

- HeartBeat cold-start observability (S1273 §3.25 baseline + Session 1099 origin of doc-claim verifier).
- 14+ event-model orphan hypothesis (S1273 lines 1912-1917 baseline).
- Employee OS `evidence_for_mission` join (S1705 F7 for Cat D-side, applies here for consumer-side).
- Group 1600 xx99 DeliverableEvent consumer contract handoff (S1699 T0/Gate).

Coverage tier at HEAD: **MEDIUM-DEEP** for HeartBeat + 14-model producer/consumer catalog; **MEDIUM** for SLO framework (single-task footprint); **MEDIUM** for doc-verifier (comprehensive framework, low observability integration); **PARTIAL** for terminology boundary (recommendation issued, not yet ratified for xx99 §5 brief).

---

## 13. Architecture Maturity

| Sub-slot | Maturity | Evidence |
|----------|----------|----------|
| **F.a HeartBeat writer** | **STABLE** | 10-min beat + record + Discord alert; producer/consumer wiring intact |
| **F.a HeartBeat export path** | **PARTIAL** | REST endpoints exist; frontend UI wiring absent; Redis pub with no consumer |
| **F.a Body Systems service framework** | **STABLE** | 10 getters wired; on-demand aggregation working; individual services out of scope |
| **F.b SLO scheduled** | **PARTIAL** | 2 beat-scheduled true-SLOs (check_learning_loop_slo + check_llm_cost_spike); no framework wrapper |
| **F.b SLO on-demand** | **PARTIAL** | 8 SLOs hardcoded in `_ops_slo_status`; 2-min cache; no persistence |
| **F.b Diagnostic escalators** | **STABLE-BUT-MISCATEGORIZED** | CTO/COO/Trend Analysis daily WORKING but not SLOs (per S1705 F4 recognition) |
| **F.c 14 event models** | **STABLE (with 1 orphan)** | 12/14 WIRED-BOTH-SIDES; 1 PRODUCER-ONLY-BY-DESIGN; 1 WRITE-ONLY-FORGOTTEN (ABTestEvent) |
| **F.c Retention** | **PARTIAL** | 1/14 has purge (FleetEvent 30d); rest unbounded |
| **F.d Verifier framework** | **STABLE** | 75 registered claims, comprehensive severity model |
| **F.d Verifier observability integration** | **DESIGN-INTENT-LATENT** | Consumed only by docs_cascade + PLATFORM_INVENTORY embed; no CI gate, no continuous emission, no alert |
| **F.e Terminology corpus** | **DRIFTED-BUT-BOUNDED** | 3 pairs STABLE, 2 pairs DRIFTED, 1 UNSTABLE — permeable boundary recommendation for xx99 |

Overall Cat F maturity verdict: **PARTIAL** — writers and consumers largely intact; retention + framework wrapper + observability integration are the systemic gaps.

---

## 14. Known Drift

### 14.1 F2 — 10 body systems in code vs 9 in inventory/CLAUDE.md

**Source of truth (code):** `core/services/body_vitals.py:340-790` — 10 `_get_*_vitals` methods (heart, lungs, circulatory, spine, immune, digestive, muscular, brain, skin, **nervous**).

**Drift sites:**
- `docs/PLATFORM_INVENTORY.md:24` — "9 body systems monitored by run_all_systems_scan"
- `docs/PLATFORM_INVENTORY.md:body-systems-section-headline` — "9 body systems"
- `CLAUDE.md` Live Counts autoblock — "9 body systems"

**Severity: MEDIUM.** Runtime works correctly; drift is on-doc-only. Owed to xx99 anchor-update PR + `python manage.py refresh_doc_inventory_blocks` regeneration.

### 14.2 F3 — check_learning_loop_slo line drift

**Actual:** `core/tasks.py:13170` (verified via grep `check_learning_loop_slo`).

**Claimed:**
- Parent §5.F entry: `core/tasks.py:12492`
- `00-START-NEXT-SESSION.md:89`: `core/tasks.py:12492`
- S1273 line 1969 origin: `core/tasks.py:12492`

**Drift: +678 lines.** Likely from Sessions 1093-1094 CTO diagnostic + runner refactor blocks + subsequent unrelated additions.

**Severity: MEDIUM.** Cite target is stable (the task name resolves the grep). Owed to xx99 anchor-update PR.

### 14.3 F7 SPECULATIVE — cold-start "sluggish/paralyzed" (S1273 line 1964)

**Code path inspected:**
- `core/services/digestive.py:103-114` — `check_intake()` / `check_processing()` / `check_enrichment()` / `check_routing()` query SpiderExecutionLog + TaskProcessingQueue + Embedding + others; on fresh DB, all counts 0 → weighted average = 100.0 (healthy).
- `core/services/muscular.py:115-170` — `_get_execution_stats()` queries AgentExecution; on fresh DB → zero executions → `critical_avg=100`, `non_critical_avg=100` → `strength_score=100`, status='**strong**'.

**Verdict.** Code paths default to healthy on zero-execution baseline. The "sluggish/paralyzed on fresh DB" claim may refer to observed operational behavior (queue init delays, startup race conditions) not visible in code logic. **Flagged SPECULATIVE.**

**Owed:** If xx99 posture requires resolution, need runtime reproduction on fresh DB. Not blocking Cat F audit lock-in.

### 14.4 Additional drift owed to xx99

- CLAUDE.md `Live Counts` autoblock body-systems row (F2).
- `docs/PLATFORM_INVENTORY.md` body-systems row (F2).
- Parent scoping §5.F line-cite for `check_learning_loop_slo` (F3).
- S1273 line 1969 pointer (F3, transitively).
- `docs/research/OPEN_ARCS.md` — Group 1700 In-progress row current-child update S1705 → S1706.
- `docs/research/ARCHITECTURE_INDEX.md` — S1706 registration in §1.52 + §8 timeline + version bump v48 → v49.

---

## 15. Known Technical Debt

### 15.1 D1 — Passive-leak retention (F1)

**Severity: HIGH.** HeartBeat + DeliverableEvent + OpsRunEvent are the three highest-cadence observability tables in Cat F scope and lack purge tasks. Peer tables with beat-scheduled purge (LearningReadbackEvent, FleetEvent, CeleryTaskEvent) demonstrate the pattern is codebase-native — extension is a small mechanical PR, not a design question.

**Debt cost.** DB size accumulation over time; possible index inefficiency; downstream query cost on any historical analysis.

**Fix outline (post-arc T-slot):** Add `cleanup_heartbeat_rows(retention_days=30)` + `cleanup_deliverable_events(retention_days=90)` + `cleanup_ops_run_events(retention_days=90)` tasks, beat-schedule each daily (04:00-05:00 Denver window per `cleanup_learning_readback_events` precedent), gate defaults via env vars per FleetEvent pattern.

### 15.2 D2 — SLO framework absence (F5)

**Severity: MEDIUM.** 2 scheduled true-SLOs + 8 on-demand hardcoded SLOs + 0 persistence + 0 audit trail. No `SLOResult` / `SLABreach` / `ServiceLevelObjective` model. Cost: no compliance history, no trend visualization, no cross-time SLO breach analysis.

**Deferred:** Framework design is parent §6.1 parked candidate.

### 15.3 D3 — Doc-claim verifier not observability-integrated (F6)

**Severity: LOW-MEDIUM.** Verifier produces 75-claim comprehensive coverage but downstream integration is thin: 1 daily-cascade consumer + 1 inventory-embed + 0 CI gates + 0 alerting. Debt cost: doc drift accumulates silently until Chris or Claude manually invokes; regression risk on doc-lifecycle discipline.

**Deferred:** Integration is post-arc parent §6.7 parked candidate; classification (candidate-vs-not) is xx99 §5 posture-decision brief input.

### 15.4 D4 — ABTestEvent WRITE-ONLY-FORGOTTEN (F4)

**Severity: LOW.** Single-model orphan. Writer at `core/views_ab_testing.py:481` records impressions/clicks/conversions; no downstream test analytics service consumes them. Debt cost: A/B testing history accumulates without analysis capability at HEAD.

**Deferred:** Per parent §5.F F.c stop condition + §7 anti-scope, deprecation decisions are Group 1900 territory.

### 15.5 D5 — HeartBeat export gap (F7)

**Severity: LOW.** REST endpoints exist but no frontend UI wiring; Redis pub/sub has no consumer. Debt cost: operational visibility for the internal health signal is limited to REST-poll or Discord alert.

**Deferred:** Export pipeline design is parent §6.5 parked candidate (post-xx99).

### 15.6 D6 — Terminology drift (F8)

**Severity: LOW.** Codebase uses "event" for both routing-semantics (DeliverableEvent → COO consumer) and audit-only (CeleryTaskEvent, LLMCallEvent). Debt cost: cognitive load on new-Claude sessions + doc coherence risk.

**Deferred:** Terminology recommendation issued for xx99 §5; renames are post-arc.

---

## 16. Boundary Violations

Cat F sub-slots were selected as "everything observability-adjacent that is NOT one of the 5 execution-telemetry layers." The audit inspected the 5 canonical writer surfaces for accidental Cat F encroachment:

| Candidate boundary case | Status | Evidence |
|-------------------------|--------|----------|
| HeartBeat writing to CeleryTaskEvent? | LEGITIMATE (no cross-write) | `heart.pulse()` never touches CeleryTaskEvent; only records HeartBeat + emits Discord |
| BodyVitalsService calling MissionRunner? | LEGITIMATE (no boundary crossing) | On-demand aggregation only; doesn't dispatch missions |
| check_learning_loop_slo writing OpsRunEvent? | LEGITIMATE (returns dict; logs only) | No OpsRunEvent side effect |
| doc-claim verifier writing observability tables? | LEGITIMATE via docs_cascade only | docs_cascade emits `step_5_drift_observed` OpsRunEvent — expected integration point |
| CTO/COO diagnostics writing OpsRunEvent? | LEGITIMATE via mission scheduler | Threshold-gated dispatch → agent → attention_bridge |
| 14 event models calling any of Cat A-E writer paths? | LEGITIMATE (independent writer paths) | Each model has its own signal handler / service.method / view.create() path |

**No boundary violations detected. Cat F is self-contained per parent §5.F sub-slotting design.**

### 16.1 Observability↔Event-Architecture recommendation (F8)

Boundary posture recommendation for xx99 §5 posture-decision brief: **PERMEABLE with producer/consumer structural split.** Execution telemetry (Cat A-E) is unambiguously Group 1700 core scope. 14+ event-shaped models are observability-adjacent PRODUCERS (state-change telemetry) whose CONSUMERS (routing logic, decision gates) belong to Group 1900. Not a naming problem; a structural producer/consumer division. This preserves parent D2 delegation to Group 1900 while keeping producer-side telemetry within Cat A-F Observability scope.

**Terminology stability grid:**

| Pair | Verdict | Codebase evidence |
|------|---------|-------------------|
| Event vs Telemetry vs Observation vs Signal | DRIFTED | "event" used for both routing (DeliverableEvent) and audit-only (CeleryTaskEvent) semantics |
| Metric vs Log vs Trace | UNSTABLE | trace_id dead on deprecated `AgentExecution` per S1703 F1 landmine; no live trace-reconstruction |
| Alert vs Notification vs Incident | STABLE | Clean map: rule-condition / user-message / marked-state |
| Monitor vs SLO vs Health-check | DRIFTED | "monitor" conflates task-level polling with observability practice |
| Producer vs Emitter vs Writer | STABLE | Clean map: publish-with-contract / signal-write / DB-insert |
| Consumer vs Aggregator vs Sink | STABLE | Clean map: subscribe / reduce / write-terminus |

---

## 17. Duplicate or Overlapping Systems

### 17.1 SLO surface duplication (F5 detail)

Three separate SLO-shaped surfaces exist:
1. **Beat-scheduled task** (`check_learning_loop_slo` + `check_llm_cost_spike`) — 2 SLOs.
2. **On-demand hardcoded** (`_ops_slo_status` 8-branch `if/elif` in `core/services/td_handlers_ops.py:365-648`) — 8 SLOs.
3. **Diagnostic escalators** (CTO/COO/Trend Analysis dailies at `core/services/diagnostics/`) — miscategorized as SLOs in narrative but architecturally alert-escalators.

No unifying `ServiceLevelObjective` class; no registry; no historical audit. This is a structural duplicate pattern, not a naming issue.

### 17.2 Event-shaped model overlap (F4 detail)

**Verifier-loop correction to Agent 3 report.** Pre-Explore Agent 3 flagged CockpitIncidentEvent + CockpitAutopilotEvent + ABTestEvent as WRITE-ONLY-FORGOTTEN. Verifier-loop grep found:

- **CockpitIncidentEvent** — consumed at `core/views_diagnostics.py:3889` via `.filter(incident=inc).order_by('created_at')`. **CORRECTED to WIRED-BOTH-SIDES** (diagnostics UI self-consume).
- **CockpitAutopilotEvent** — consumed at `core/views_diagnostics.py:3367` via `.select_related('policy')[:limit].values(...)`. **CORRECTED to WIRED-BOTH-SIDES** (diagnostics UI self-consume).
- **ABTestEvent** — writer at `core/views_ab_testing.py:481`; NO consumer sites found in main core. **CONFIRMED WRITE-ONLY-FORGOTTEN.**

True WRITE-ONLY-FORGOTTEN count: **1/14 (7.1%)** — not 3/14 as pre-Explore Agent 3 report suggested. Cat F event-model surface is healthier than S1273 lines 1912-1917 hypothesized.

### 17.3 HeartBeat vs Body-System pulse tables

HeartBeat aggregates the 8-9 components (brain, nervous, organs, sensory, skin, memory, celery, resolve_node — note: HeartMonitorService's 8-component view differs from BodyVitalsService's 10-getter view, since HeartMonitorService is the coordinator layer). Per-system pulse tables (BreathCycle, CirculationPulse, etc.) live below HeartBeat and hold richer per-system detail. No true duplicate — layered aggregation pattern.

---

## 18. Ownership Gaps

| Item | Current owner | Gap |
|------|---------------|-----|
| Cat F table retention | None | Owed to post-arc T-slot; peer tables have owned purge tasks |
| SLO framework | None (single-task footprint) | Parent §6.1 parked; xx99 will surface as candidate |
| doc-claim verifier observability integration | None (docs_cascade is a consumer only) | Parent §6.7 parked; xx99 posture-decision brief |
| HeartBeat export UI wiring | None | Parent §6.5 parked; post-xx99 design |
| 10th body system (nervous) doc registration | Runtime code | Owed to xx99 anchor-update PR |
| ABTestEvent consumer / deprecation | None | Group 1900 territory per parent §5.F F.c stop |
| Terminology boundary ratification | Chris (via xx99) | Recommendation issued in this audit; ratification post-arc |

---

## 19. Recommended Future Research (R1–R10)

Ordered by impact + reversibility. All R-items are **post-arc T-slot** per parent §7 anti-scope + playbook §14.5 no-implementation-during-research rule.

- **R1 (HIGH) — F1 retention posture decision.** Chris-gated ADR on HeartBeat / DeliverableEvent / OpsRunEvent purge policy. Recommended default: 30-day for HeartBeat (matches LearningReadbackEvent); 90-day for DeliverableEvent / OpsRunEvent (matches business-lifecycle windows). **xx99 output is a posture/decision + evidence brief; purge-task implementation is post-arc T-slot per playbook §14.5** (Rigby SIGN cycle 1 Q4 F3 fold). **Owed to xx99 §7 or T0/Gate depending on D74 posture resolution.**
- **R2 (HIGH) — F9 D74 axis posture decision.** Chris-gated selection between canonical-unification (single execution_id + trace_id spine spanning task→LLM→agent→tool→ops) vs structural-separability (per-layer correlation, retention, and dedup owned independently). Cat F evidence contribution: **retention must be first-class in either posture** — the passive-leak pattern is not resolvable through spine unification alone. **xx99 §5 posture-decision brief consumes this.**
- **R3 (MEDIUM) — F5 SLO framework scoping.** Follow-on design-preparation arc (Group 1701 candidate or subsumed by Group 1900). Requires: `ServiceLevelObjective` model spec, historical audit table, registry pattern, breach-alert wiring. Parent §6.1 parked.
- **R4 (MEDIUM) — F6 doc-claim verifier observability integration.** Chris-gated ADR on whether verifier drift is a first-class telemetry signal. Post-xx99. Requires: `DocClaimDrift` model spec, continuous-emission wiring, CI gate policy, alert threshold.
- **R5 (MEDIUM) — F8 terminology recommendation ratification.** xx99 §5 posture-decision brief includes the PERMEABLE-with-producer/consumer-split recommendation; Chris ratifies (or overrides) as the Group 1700 canonical terminology stance. Feeds Group 1900 arc-open scoping.
- **R6 (MEDIUM) — F2 body-system inventory refresh.** Regenerate PLATFORM_INVENTORY via `python manage.py refresh_doc_inventory_blocks` and `python manage.py generate_platform_inventory`; update CLAUDE.md autoblock via same. Adds nervous to the "10 body systems" claim.
- **R7 (LOW) — F4 ABTestEvent orphan disposition.** Group 1900 scope. Cat F flags; Group 1900 acts. Not Cat F R-scope.
- **R8 (LOW, non-blocking) — F7 HeartBeat export UI wiring.** Design-preparation arc if Chris ratifies at xx99. Parent §6.5 parked. **Optional / non-blocking per Rigby SIGN cycle 1 Q4 F4 fold — not required shipping work during research.**
- **R9 (LOW, non-blocking) — F7 SPECULATIVE cold-start behavior verification.** Runtime reproduction on fresh DB to confirm/refute S1273 line 1964 claim. Employee OS or body-systems reliability project. **Optional / non-blocking per Rigby SIGN cycle 1 Q4 F4 fold.**
- **R10 (LOW) — F3 parent scoping / start-here line-cite refresh.** Update `check_learning_loop_slo` line pointer from 12492 → 13170 across parent §5.F + `00-START-NEXT-SESSION.md:89` at next-arc-close. Also owed: fix the "six sub-slots" text vs 5-actual-slots wording in the parent §5.F preamble.

---

## 20. Appendix

### 20.1 Verifier-loop record

**Pre-Explore verified (playbook §14, front-runs Rigby grep):**
- `core/models_heart.py` + `core/services/{heart,body_vitals,doc_claim_verification}.py` all EXIST as concrete files.
- `check_learning_loop_slo` at `core/tasks.py:13170` (not 12492 as parent claims — F3 drift caught pre-Explore).
- All 14 event-shaped models exist as concrete Django model classes at their claimed file:line anchors (verified via `grep -E '^class (DeliverableEvent|...)\(' --type py`).
- `RIGBY_EVENT_INTAKE_ENABLED` default `False` confirmed at `core/signals/deliverable_status_signals.py:47`.

**Post-Explore verified (playbook §14, trust-but-verify sub-agent claims):**
- **10 vs 9 body systems drift** — confirmed `_get_nervous_vitals` at `core/services/body_vitals.py:744-790` present; PLATFORM_INVENTORY.md:24 + CLAUDE.md autoblock say 9. F2 locked.
- **CockpitIncidentEvent consumer** — grep found `views_diagnostics.py:3889` filter+order_by consumer; Agent 3 verdict corrected from WRITE-ONLY-FORGOTTEN to WIRED-BOTH-SIDES. F4 locked.
- **CockpitAutopilotEvent consumer** — grep found `views_diagnostics.py:3367` select_related+values consumer; Agent 3 verdict corrected. F4 locked.
- **ABTestEvent WRITE-ONLY-FORGOTTEN** — grep across `core` returned only `views_ab_testing.py:481` writer + `core/models_unified_system.py:8686` model def + `core/views_ab_testing.py:13` import. No consumer. F4 locked as true 1/14 orphan.
- **75 `@register_claim` decorators** — `grep -c '@register_claim'` in `doc_claim_verification.py` returned 75. F6 locked.
- **`step_5_drift_observed` OpsRunEvent** — grep confirmed at `core/jobs/docs_cascade.py:105 DRIFT_LABEL = "step_5_drift_observed"` plus emission sites at :386, :612, :677. F6 locked.
- **HeartBeat purge absence** — grep of `core/celery.py` for "heartbeat" returned only writer beat entry at :39-42; no cleanup task. F1 locked.
- **FleetEvent 30-day purge** — confirmed at `core/services/fleet_event_cleanup.py:70` (`FLEET_EVENT_RETENTION_DAYS=30`). Peer-comparison evidence for F1.
- **LearningReadbackEvent cleanup beat-scheduled** — confirmed at `core/celery.py:246` (`'task': 'core.tasks.cleanup_learning_readback_events'`). Peer-comparison evidence for F1.

**Verifier-loop verdict.** Two Agent 3 claims materially corrected pre-Rigby (CockpitIncidentEvent + CockpitAutopilotEvent). One Agent 3 claim confirmed (ABTestEvent). All other load-bearing claims verified as posted.

### 20.2 Sub-agent digest per playbook §13

- **Agent 1 (F.a)** — HeartBeat schema + 10 body-system getters + producer/consumer + export gap verification + cold-start SPECULATIVE flag.
- **Agent 2 (F.b)** — SLO framework absence + 2-scheduled + 8-on-demand + CTO/COO diagnostics as alert escalators + line drift catch.
- **Agent 3 (F.c)** — 14-model WRITE-ONLY-FORGOTTEN matrix (later corrected by verifier-loop).
- **Agent 4 (F.d)** — Doc-claim verifier 75-claim framework + docs_cascade consumer + DESIGN-INTENT-LATENT classification.
- **Agent 5 (F.e)** — Terminology stability grid + PERMEABLE boundary recommendation.
- **Agent 6 (cross-cutting)** — S1701-S1705 pattern inheritance matrix + D74 axis contribution as OBSERVABILITY-FRAMEWORK-UNBOUNDED-RETENTION.

### 20.3 Cross-references

- Playbook §11.2 20-section child audit template.
- Playbook §13 6-parallel-Explore sweep contract.
- Playbook §14 verifier-loop discipline (pre-Explore + post-Explore).
- Playbook §15 Rigby SIGN cycle 1 required-full for child audits.
- Parent scoping `1700_observability_domain_scoping.md` §5.F + §6 parked candidates + §7 anti-scope.
- Prior child audits `1701_*`, `1702_*`, `1703_*`, `1704_*`, `1705_*` for F1-F9 pattern inheritance.
- Cross-arc handoffs: Group 1600 T0/Gate DeliverableEvent + Group 1500 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN precedent.

### 20.4 Repo state at draft

Branch: `main` at commit `7b8dd128` (post-S1705 close). Working tree clean pre-draft. This audit doc is the only new artifact this session pre-close.

### 20.5 Rigby SIGN cycle 1 pending

Routing target per playbook §15 required-full + parent-scoping precedent (S1600/S1700/S1701/S1702/S1703/S1704/S1705): arc pin `pa-e7fbacc996b34b44` doubles as SIGN pin; fresh SIGN isolation pin `pa-a5ce5fdd56364dee` minted per §15 promoted rule but expected routed-around by `tools/pa_local.sh:128` wrapper hard-code (retire at S1706 close per §16). Single-batch 4-question pattern per D48 22-consecutive-clean-arms precedent (S1503+…+S1705 17-consecutive-fully-clean-arms sub-pattern; 23rd arm anticipated at this SIGN cycle).

**Pressure-test questions (single batch):**

1. **Coverage completeness.** Did S1706 miss any observability-adjacent surface? Candidates to grep-check: (a) resolve_node infrastructure telemetry, (b) memory pressure signals under BRAIN, (c) fleet-side auth token audit, (d) any `RIGBY_*_INTAKE_ENABLED` sibling flags beyond RIGBY_EVENT_INTAKE_ENABLED + RIGBY_DELEGATION_ENABLED already catalogued.
2. **Drift severity.** Are F1 (passive-leak retention), F2 (10-vs-9 body systems), F3 (line drift) all correctly ranked at HIGH/MEDIUM? Should F1 be CRITICAL given unbounded-growth compounding risk?
3. **D74 axis correctness.** Is OBSERVABILITY-FRAMEWORK-UNBOUNDED-RETENTION the right sixth axis cell? Does the F1 evidence justify a distinct cell vs subsumption under Cat A F6 / Cat B F4 / Cat D F5 / Cat E F6 as "no-retention pattern"?
4. **R1-R10 ranking + xx99 scope discipline.** Are R1 (retention posture) + R2 (D74 axis) correctly HIGH? Should R3 (SLO framework) be MEDIUM or LOW given parent §6.1 parked-candidate status? Does R5 (terminology ratification) belong in xx99 §5 or in a separate Chris-ratification ADR? Any R-item that violates playbook §14.5 no-implementation rule if left as-is?

### 20.6 Post-SIGN fold record

Rigby SIGN cycle 1 delivered 2026-07-03 on arc pin `pa-e7fbacc996b34b44` (fresh SIGN isolation pin `pa-a5ce5fdd56364dee` minted per playbook §15 promoted rule but routed-around by `tools/pa_local.sh:128` wrapper hard-code — S1600/S1700/S1701/S1702/S1703/S1704/S1705 precedent). D48 preemptive stability-probe gate 23rd arm HOLDING CLEAN — single-batch 4-question pattern per S1701-S1705 precedent; **18-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704+S1705+S1706 CONFIRMED** at S1706 close.

**Verdict summary:**

| Q | Verdict | Confidence | Folds landed |
|---|---------|-----------|--------------|
| Q1 coverage completeness | SIGN-with-edits | Medium | F1 (candidate-surface disposition bullet list — resolve_node / memory_pressure / fleet auth / RIGBY_*_INTAKE flags) added to §1 executive |
| Q2 drift severity | CONFIRM | Medium-High | No folds (F1 stays HIGH not CRITICAL; F2/F3 rankings confirmed) |
| Q3 D74 axis correctness | SIGN-with-edits | Medium | F2 (F9 axis label renamed OBSERVABILITY-FRAMEWORK-UNBOUNDED-RETENTION → RETENTION-PATTERN-INCONSISTENT + "cross-cat pattern with Cat F as consolidation point" clarifying line added to §1.1 F9 + §9.1 D74 matrix) |
| Q4 R1-R10 ranking + xx99 scope discipline | CONFIRM (with 2 small scope-discipline edits) | Medium-High | F3 (R1 "xx99 output = posture/decision + evidence; purge-task implementation post-arc T-slot per §14.5") + F4 (R8/R9 marked "optional / non-blocking — not required shipping work during research") |

**F1-F4 folds all landed pre-commit** per playbook §16 draft→canonical commit policy. No CONFIRM verdicts required rework. No MUST-FIX verdicts issued. No FLAG-EDIT verdicts issued.

**Three "do not regress" notes for PR:**
1. Preserve F1 candidate-surface disposition block in §1 executive (Q1 F1 fold).
2. Preserve F9 axis label "RETENTION-PATTERN-INCONSISTENT" both in §1.1 F9 row and §9.1 D74 matrix cell (Q3 F2 fold).
3. Preserve R1 "xx99 = posture + evidence, not implementation" scope-discipline sentence + R8/R9 non-blocking labels (Q4 F3+F4 folds).

### 20.7 Session close checklist

- [ ] Rigby SIGN cycle 1 delivered on arc pin `pa-e7fbacc996b34b44` (fresh SIGN pin `pa-a5ce5fdd56364dee` routed-around per wrapper precedent).
- [ ] Fold F1-Fn per SIGN verdict pre-commit.
- [ ] Retire fresh SIGN pin `pa-a5ce5fdd56364dee` via `session_tool.retire`.
- [ ] Update `docs/research/ARCHITECTURE_INDEX.md` — v48 → v49 with §1.52 S1706 registration + §8 timeline S1706 row + line-6 v49 preamble.
- [ ] Update `docs/research/OPEN_ARCS.md` Group 1700 In-progress row: current-child S1705 → S1706 AND prepare row for transition to Awaiting summary at S1799 next.
- [ ] Write `docs/handoffs/SESSION_1706_OBSERVABILITY_CAT_F_ADJACENT_SEPARATION_BOUNDARIES.md`.
- [ ] Overwrite `00-START-NEXT-SESSION.md` → S1799 xx99 canonical summary as next-session priority.
- [ ] Commit S1706 artifact set to `main` via Chris merge + PR.
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule `feedback_docs_cascade_at_every_close.md`.

### 20.8 Handoff notes to xx99

- **F9 D74 axis matrix now complete** with six cells (A DEEP-WIRED, B DEEP-WIRED-BUT-DEDUP-UNRESOLVED, C COVERAGE-GAP-ON-PA-PATH, D ACTIVELY-BROKEN, E LATENT-VIABLE-BUT-FLAG-GATED, F OBSERVABILITY-FRAMEWORK-UNBOUNDED-RETENTION). xx99 §5 posture-decision brief has full evidence base for D74 spine-vs-separability question.
- **F5 producer-only inheritance from S1705** and **F4 (7/14 event models) plus F.c matrix** together give xx99 the "how healthy is the event-model surface" evidence. Recommendation: xx99 §7.4 canonical note that 12/14 WIRED-BOTH-SIDES + 1 orphan (ABTestEvent, Group 1900 disposition) + 1 by-design (EngagementEvent webhook path) is a POSITIVE health verdict, not a WRITE-ONLY-FORGOTTEN-ARC-WIDE crisis.
- **F1 retention gap unifies across all six Cats.** xx99 §19 R-slot should surface a single unified retention-policy ADR spanning A-F rather than per-Cat retention specs.
- **F8 permeable-boundary recommendation** is xx99 §5 posture-decision brief input; do NOT ratify at xx99 without Chris.

_Rigby SIGN cycle 1 SIGN-with-edits at Medium/Medium-High confidence; F1-F4 folds landed pre-commit. `status: active`._
