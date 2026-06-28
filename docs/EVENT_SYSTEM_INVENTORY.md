---
title: "Event System Inventory"
status: active
session: 1250
generated: 2026-06-28
last_reviewed: 2026-06-28
companion_docs:
  - PLATFORM_INVENTORY.md
  - PLATFORM_WHAT_IT_IS.md
owner: rigby-and-claude (direction approved by Rigby; structure + evidence from Claude)
---

# Event System Inventory

> **Purpose.** Map what event-shaped infrastructure already exists in
> the repo, so future work toward an event-driven Rigby intake layer
> reuses existing primitives instead of inventing parallel ones. This
> is a **discovery snapshot**, not a design spec. It exists to make the
> next decisions cheaper.
>
> **Scope.** Documentation only. No behavior changes ship with this
> doc.
>
> **How this doc came to be.** Session 1250 ran two parallel Explore
> agents across the codebase (emission-side and consumption-side) to
> find every event-named model, signal receiver, emit helper, audit
> table, websocket consumer, broadcast helper, intake/router surface,
> and SSE endpoint. Findings were synthesized and routed through Rigby
> for direction approval before landing here.

---

## 0. TL;DR

- The platform has **rich emission**: 14+ event-shaped models, 40+
  Django signal receivers, multiple emit helpers (`EventBus.publish`,
  `emit_orchestration_event`, `emit_event` (fleet), `record_op`,
  `emit_tool_started/completed`).
- It has **rich consumption infrastructure**: ~57 WebSocket consumer
  classes, channels `group_send` fan-out, an SSE endpoint (FleetEvent
  stream), Celery Beat consumers that poll Redis Streams.
- It has **no central decision layer**. Every emitter routes directly
  to a domain-specific consumer. There is no "all events route here,
  then Rigby decides" surface today.
- **PA / Rigby is currently pull-only.** No Celery task, signal, or
  hook currently invokes `unified_pa_entrypoint.process_message()`
  without user initiation.
- The cleanest existing transition emitter is **DeliverableEvent**
  (Deliverable status flips → DeliverableEvent rows with direction
  classification). This is the agreed first emitter for v0 intake
  (see §4).
- The closest existing run-timeline primitive is **OpsRun +
  OpsRunEvent**. v0 will add compatibility fields (`domain`,
  `run_kind`, `mission_id`) without conflating ops vs mission
  semantics (see §4 and §5).

---

## 1. Existing event-like models

The table below is the model surface. "Live" means a writer was
verified during discovery. "Defined" means the model exists but no
explicit writer was found in this pass — that does not prove it is
dead; it is a hint for follow-up verification.

For each model: model path · purpose · known write path · known
consumers · status · estimated usefulness for Rigby intake · risk
level.

### 1.1 CeleryTaskEvent

- **Path:** `core/models_celery_telemetry.py:17`
- **Purpose.** Per-task lifecycle telemetry. One row per Celery
  prerun/postrun/failure with status, duration, error info, RSS delta,
  agent name, priority match.
- **Write path.** `core/celery_telemetry.py:74` (`task_prerun`),
  `:115` (`task_postrun`), `:177` (`task_failure`) Celery signal
  handlers.
- **Retention.** `CELERY_TASK_EVENT_RETENTION_DAYS = 30`
  (`core/settings.py:102`); see also `AUDIT_FINDINGS.md` §12 for the
  audit-canonical deferred-task list.
- **Consumers.** PA `ops_tool.celery_task_history`, `audit_celery_zero_fire`
  management command (`core/management/commands/audit_celery_zero_fire.py`).
- **Status.** Live.
- **Rigby intake usefulness.** Medium. High volume; useful for
  failure-driven intake events (e.g., "task X failed Y times in 1h")
  but not all rows are mission-relevant.
- **Risk level.** Medium — large table, watermarking required.

### 1.2 LLMCallEvent

- **Path:** `core/models_llm_telemetry.py:30`
- **Purpose.** Per-LLM-call telemetry: provider, model, tokens in/out,
  duration, error type, cancellation, execution_id correlation.
- **Write path.** `core/services/llm_call_wrapper.py` (S1098). Rows
  survive AgentExecution cleanup (decoupled retention).
- **Consumers.** Postmortem analysis, cost tracking, S1219-S1220
  watchdog / cleanup arc.
- **Status.** Live.
- **Rigby intake usefulness.** Low for intake. High for verification
  ("did agent X actually call the LLM?").
- **Risk level.** Medium — large table.

### 1.3 ImpactEvent

- **Path:** `core/models_impact_events.py:21`
- **Purpose.** Business-impact ledger. Types: `wager_profit`,
  `revenue`, `content_action`, `save`, `export`, `share`. Has
  `value_usd`, `desk`, `agent_name`, `source_object_type/id`,
  `trace_id`.
- **Write path.** S1089 IQROI computation paths; PortfolioAllocator.
- **Consumers.** IQROI rollups, revenue dashboards.
- **Status.** Live.
- **Rigby intake usefulness.** High — these are inherently
  mission-relevant (revenue / engagement signal).
- **Risk level.** Low — schema is purpose-built and stable.

### 1.4 DeliverableEvent

- **Path:** `core/models_deliverables.py:561`
- **Purpose.** Per-deliverable lifecycle event log. Event types
  include `synthesis_viewed`, `saved`, `exported`, `shared`,
  `task_created`, `action_taken`, and **`status_transition`**
  (direction-classified).
- **Write path.** `core/signals/deliverable_status_signals.py:71`
  (`pre_save` stash) + `:94` (`post_save` record) on Deliverable.
  Writes `{from, to, direction, ctx}` metadata.
- **Consumers.** S1095 COO rework / bounce gate. Frontend deliverable
  history.
- **Status.** Live. **Best-shaped emitter in the repo for v0 intake.**
- **Rigby intake usefulness.** **High.** Status transitions are
  semantically meaningful; the direction classifier already exists.
- **Risk level.** Low — bounded volume, clean schema, already
  classified.

### 1.5 OpsRunEvent

- **Path:** `core/models_ops_runs.py:52`
- **Purpose.** Per-step timeline for OpsRun. Event types:
  `step_start`, `pass`, `fail`, `info`, `heartbeat`.
- **Write path.** Ops control loop, manual run helpers, smoke tests.
- **Consumers.** Ops UI timeline view, smoke-test assertions.
- **Status.** Live.
- **Rigby intake usefulness.** Medium for intake (failures /
  heartbeat misses), high as the **run-timeline primitive v0 will
  reuse for MissionRun** (see §4).
- **Risk level.** Medium — semantic-contamination concern if
  MissionRun and OpsRun are not kept distinct (see §5).

### 1.6 TriggerEvent

- **Path:** `core/models_situation_triggers.py:389`
- **Purpose.** Audit trail for SituationTrigger rule evaluations.
- **Write path.** Defined; writers unverified in this pass. Trigger
  signals at `core/signals/trigger_signals.py:26` populate adjacent
  WorkspaceTrigger rows.
- **Consumers.** Conductor → `process_trigger_events` Celery task →
  WorkspaceTrigger work-item creation (with `target_agent`).
- **Status.** Live (model + adjacent flow); event-row writers
  unverified.
- **Rigby intake usefulness.** High once writers verified — these are
  already shaped as "something interesting happened, decide what to
  do."
- **Risk level.** Medium — need to verify writer paths before relying
  on this as a foundational source.

### 1.7 FleetEvent

- **Path:** `core/models/fleet.py:462`
- **Purpose.** Cross-app fleet lifecycle events; persists to DB and
  publishes to Redis pub/sub channel.
- **Write path.** `core/services/fleet_events.py:71`
  (`emit_event(event_type, app_slug, payload)`).
- **Consumers.** `core/views_fleet_events.py:159` SSE endpoint
  (`GET /api/fleet/events/stream`) with Last-Event-ID replay (cap 200)
  and 15s keepalive.
- **Status.** Live; consumer surface is SSE for external fleet apps.
- **Rigby intake usefulness.** Medium — fleet events are
  cross-app-scoped, not always platform-wide mission-relevant.
- **Risk level.** Low for sourcing, high for re-use — fleet semantics
  are already spec'd; do not repurpose.

### 1.8 CockpitIncidentEvent

- **Path:** `core/models_cockpit_incidents.py:41`
- **Purpose.** Cockpit incident audit trail (event_type, user,
  metadata).
- **Write path.** Defined; writers unverified.
- **Consumers.** Unverified.
- **Status.** Defined / unverified.
- **Rigby intake usefulness.** Potentially high, but **explicitly
  deferred** per Rigby's PR 1 direction — do not use as a foundational
  source yet (see §4).
- **Risk level.** Medium-high — unverified writers + cockpit-specific
  semantics.

### 1.9 CockpitAutopilotEvent

- **Path:** `core/models_cockpit_autopilot.py:33`
- **Purpose.** Autopilot run audit (autopilot_run FK, event_type,
  status, metadata).
- **Write path.** Defined; writers unverified.
- **Consumers.** Unverified.
- **Status.** Defined / unverified.
- **Rigby intake usefulness.** Same as 1.8 — deferred.
- **Risk level.** Same as 1.8.

### 1.10 Other event-shaped models found

These are catalogued for completeness; none are v0 candidates.

| Model | Path | Notes |
|---|---|---|
| EngagementEvent | `core/models_engagement.py` | Defined; writers unverified |
| ThreatEvent | `core/models_immune.py:119` | Immune-system threat tracking |
| ABTestEvent | `core/models_unified_system.py:8686` | A/B test capture |
| ConversionEvent | `core/models_unified_system.py:19761` | Revenue tracking |
| BadContextEvent | `core/models_unified_system.py:21158` | Context-error capture |
| RelationshipEvent | `core/models_unified_system.py:12418` | Agent relationship tracking |
| HeartBeat | `core/models_heart.py` | Body-system health snapshots |
| ToolCallRecord | `core/models_tool_calls.py:19` | Per-tool-call telemetry (S861) |

### 1.11 Adjacent audit/log tables (not "event" shaped but in scope)

- `AuditLog` — `core/models_unified_system.py:19302` (Market
  Intelligence audit, 30+ action_type choices)
- `AuditReport` / `AuditFinding` / `AuditRemediationTask` /
  `AuditVerificationRun` — `core/models_audit_tracking.py:16+` (S819
  audit system)
- `CockpitAuditLog` — `core/models_cockpit_audit.py:10` (RBAC
  audit; same defer rule as Cockpit*Event)
- `NotificationLog` — `core/models_push_notifications.py:183`
- `LLMCallLog` — `core/models_llm_routing.py:297`
- `StageTransitionLog` — `core/models_document_registry.py:1709`
- `SpiderExecutionLog`, `PerformanceLog`, `AutomatedActionLog`,
  `AutonomousActionLog`, `ArtifactExtractionLog`, `ModelPerformanceLog`,
  `CodeJobLog`, `WebSocketConnectionLog`, `ResumeOptimizationLog` —
  catalogued but not v0 candidates.

---

## 2. Existing event flows

Each arrow is a verified path with `file:line` evidence. "→" =
synchronous; "↪" = Celery dispatch; "⇢" = WebSocket / pub-sub fan-out.

### 2.1 Deliverable status transition (cleanest)

```
Deliverable.status changes
  → deliverable_status_signals.py:71  (pre_save: stash prior status)
  → deliverable_status_signals.py:94  (post_save: classify direction)
    → DeliverableEvent('status_transition', {from, to, direction, ctx})
       → COO rework/bounce gate (S1095)              [no agent dispatch]
       → Frontend deliverable history                [UI only]
```

### 2.2 Dream approval → Initiative + agent execution (only live direct-trigger path)

```
AgentDream.approved → True
  → dream_signals.py:23 (pre_save: cache _was_approved)
  → dream_signals.py:46 (post_save)
    → promote_to_initiative()                        [creates Initiative row]
    ↪ Celery: execute_single_dream                   [direct agent dispatch]
```

### 2.3 Spider data ingest → trigger evaluation

```
SpiderData created
  → trigger_signals.py:26
    ↪ Celery: process_trigger_events                 [SituationTrigger eval]
    → WorkspaceTrigger row (with target_agent)       [conductor picks up]
    → Learning bridges: SpiderDataBridge.process_event()
```

### 2.4 Celery task lifecycle telemetry

```
@shared_task fires
  → core/celery_telemetry.py:74   (task_prerun)
  → core/celery_telemetry.py:115  (task_postrun)
  → core/celery_telemetry.py:177  (task_failure)
    → CeleryTaskEvent row                            [telemetry only, no reactor]
```

### 2.5 LLM SDK call → LLMCallEvent

```
Any LLM SDK call (Anthropic/OpenAI/Together/Ollama/DeepSeek/Gemini)
  → core/services/llm_call_wrapper.py
    → LLMCallEvent row                               [telemetry only]
```

### 2.6 PA tool execution → chat UI status

```
tool_dispatcher.execute(tool_name, params)
  → pa_status_events.py:116  (emit_tool_started)
  → pa_status_events.py:180  (emit_tool_completed)
    ⇢ channels.group_send(pa_conversation_<id>, ...)
      → PAConversationConsumer → browser chat UI     [UI only]
```

### 2.7 FleetEvent → SSE

```
fleet_events.py:71  emit_event(event_type, app_slug, payload)
  → FleetEvent row
  → Redis publish (channel keyed by app_slug)
    ⇢ /api/fleet/events/stream (SSE; Last-Event-ID replay; 15s ping)
      → external fleet app subscribers
```

### 2.8 EventBus (Redis Streams)

```
EventBus.publish(stream, event_type, data, ...)        # core/services/event_bus.py:137
  → Redis Stream (one of 8: SPIDER_DATA, OPPORTUNITY_*, VALIDATION_*,
                            OUTCOME_RECORDED, MODEL_TRAINED, SYSTEM_ALERT)
    ↪ Celery Beat: process_event_bus_{scoring|validation|analytics}_queue
      → EventConsumerWorker.process_batch
        → EventHandlerRegistry.dispatch(event_type)    # event_handlers.py:31
          → default handler                            # (e.g., discord_notifications on system_alert)
```

### 2.9 Sports signals → WebSocket fan-out

```
OddsLine / LineMovement / ArbitrageOpportunity / BettingRecommendation /
Game / Bet / BettingMarket  post_save
  → sports/signals.py:{25,82,133,238,287,332,413}
    → PlatformMetrics row
    ⇢ channels.group_send(<named group>, ...)
      → WebSocket consumers → dashboards / alerts UIs
```

### 2.10 Body Coordinator autonomic reflexes

```
Body-system probe writes (LUNGS / HEART / IMMUNE / DIGESTIVE / MUSCULAR /
                          CIRCULATORY / SPINE / BRAIN / SKIN / NERVOUS)
  → body_coordinator.py:110-200
    → CoordinationEventType (26 states) → handler map
      → throttle_mode / circuit-break / response log    [autonomic; no PA loop]
```

---

## 3. Current gaps vs. desired pipeline

The desired pipeline is:

```
Platform Event → Rigby Event Intake → Mission Impact Assessment
              → Decision → Delegate / Verify / Learn
```

Stage-by-stage gap analysis:

| Pipeline stage | What exists today | What is missing |
|---|---|---|
| **Platform Event** | 14+ event-shaped models; 40+ signal emitters; 5+ emit helpers; cleanest sources are DeliverableEvent, CeleryTaskEvent, ImpactEvent, FleetEvent. | No **canonical normalized event shape** spanning sources. No shared `correlation_id` convention across tables. Multiple parallel emit conventions (signals vs. helpers vs. EventBus publish). |
| **Rigby Event Intake** | Nothing. Closest patterns: opportunity pipeline orchestrator (`core/services/opportunity_pipeline_orchestrator.py`), body coordinator (`core/services/body_coordinator.py`), learning-bridge `process_event` abstract (`core/learning_bridges/base.py`). | No single surface that consumes platform events and routes to decisions. **PA has zero non-user-initiated callers** — `unified_pa_entrypoint.process_message()` is pull-only today. |
| **Mission Impact Assessment** | None as a primitive. S1095 COO rework gate is the only "evaluate this transition" surface, and it's deliverable-only. | No reusable "is this event mission-relevant, and at what severity?" service. |
| **Decision** | Implicit only — scattered handlers (discord_notifications on system_alert; conductor on WorkspaceTrigger.target_agent; body coordinator on body events). | No central decision layer with explicit choices: ignore / log / monitor / notify-Chris / create-initiative / delegate-agent. No decision audit trail. |
| **Delegate** | Agent dispatch surface exists: `core/agent_router.py` (`route(agent_name, task, context)`), `execute_agent_task` Celery task, conductor task. | No "Rigby chose to delegate this to agent X for reason Y" path. Agents are dispatched by callers, never by an intake layer. |
| **Verify** | None as a primitive. | No verification step. Outcomes do not loop back to the intake decision that produced them. |
| **Learn** | Learning bridges exist (`core/learning_bridges/`, 10 implementations) but they pattern-extract from raw signals — they don't close the loop back to a re-dispatched agent. | No outcome → re-evaluate signal. No "this decision turned out to be wrong; update the rule" feedback. |
| **MissionRun / Logbook** | `OpsRun` + `OpsRunEvent` (`core/models_ops_runs.py`) is the closest existing pattern: a run + per-step timeline + heartbeat. DeliverableEvent is a per-object journal. | No "mission" concept yet. OpsRun is **ops-scoped** by design; **mission** semantics must be added without contaminating ops. |

**Bottom line.** Emission is rich (and noisy — many parallel patterns).
Consumption infrastructure is solid (Channels, EventBus, SSE).
**The decision/intake layer in the middle is empty.** Everything
currently routes source → domain-specific consumer with no
intermediary.

---

## 4. Approved v0 direction

Approved by Rigby Session 1250. The following constraints govern all
follow-up PRs (PR 2+):

### 4.1 Sources

- **Do not** create a new `PlatformEvent` table in v0.
- Use existing event tables as sources (per §1).
- Start with **DeliverableEvent status transitions** as the first
  safe emitter (PR 5). Reasons: cleanest schema, bounded volume,
  pre-classified direction, already in active use.
- **Defer** Cockpit-family events (`CockpitIncidentEvent`,
  `CockpitAutopilotEvent`, `CockpitAuditLog`) — writers unverified;
  they are not foundational sources for v0.
- **Do not** depend on the Redis EventBus for v0 wiring. EventBus
  remains operational for the MI pipeline; v0 intake does not
  subscribe to it.

### 4.2 Read API

- Add a **read-only `platform_event_view`** service in PR 2. It will
  yield a normalized `{source, source_id, kind, severity, ts,
  payload, correlation_id}` shape over existing tables. No table
  writes.
- The service must support **watermarks** (per-source) so consumers
  do not full-scan large event tables.

### 4.3 Run-timeline primitive

- Reuse **`OpsRun` / `OpsRunEvent`** as the MissionRun v0 primitive,
  **only if ops vs mission separation is preserved**. PR 3 adds
  compatibility fields without conflating semantics:
  - `domain` (e.g., `ops` | `mission`)
  - `run_kind` (sub-classification within domain)
  - `mission_id` (nullable; populated when domain=mission)
- Ops-scoped runs must remain unaffected. No backfill. Migration is
  additive only.

### 4.4 Intake task

- Add a **`rigby_event_intake(event_ref, dry_run=True)`** Celery task
  on the `pa` queue in PR 4.
- Loads the referenced event via `platform_event_view`.
- Runs a **rule-based** impact assessment. **No LLM in v0.**
- Writes a decision row (Ignore / Log / Monitor / Notify /
  CreateInitiative / Delegate).
- **Dry-run** = decision row written; no side effect executed.
- Idempotent on `event_ref`.

### 4.5 Subscriber

- PR 5 subscribes intake to **DeliverableEvent status transitions
  only**. Still dry-run by default.
- PR 6 enables **one low-risk decision class** (Notify-Chris). Agent
  delegation deferred to PR 7+.

### 4.6 Triggering agents

- **Do not** trigger agents directly from events in v0.
- All agent delegation goes through `agent_router.route()` and is
  invoked by Rigby Event Intake's decision step, never by an emitter
  or signal.
- Deterministic low-risk Celery tasks (metrics aggregation, cleanup)
  remain on their existing direct-dispatch paths — they are out of
  intake scope.

---

## 5. Risks and guardrails

| Risk | Guardrail |
|---|---|
| **Ops vs mission semantic contamination.** Adding mission fields to OpsRun could leak ops semantics into mission queries (or vice versa). | PR 3 fields are nullable + additive. All mission-side reads must filter `domain='mission'`. Ops-side reads keep current behavior. Tests assert that an ops-domain OpsRun never appears in a mission-domain query and vice versa. |
| **Scanning large event tables without watermarks.** CeleryTaskEvent and LLMCallEvent are high-volume; a naive intake subscriber could full-scan. | `platform_event_view` (PR 2) requires a per-source watermark. Subscribers must commit watermark after successful intake. No `Model.objects.all()` reads. |
| **Non-idempotent event refs.** Re-running intake on the same event would create duplicate decisions. | All event refs must be uniquely keyed by `(source_table, source_id)`. Intake task is idempotent on this key. Decision row has a unique constraint on event_ref. |
| **Operational noise.** Subscribing to every emitter risks turning intake into a firehose. | v0 subscribes to **one emitter** (DeliverableEvent). Adding emitters requires a separate PR with explicit volume estimation. |
| **Premature certainty on impact.** A rule-based assessment can claim "high impact" when evidence is thin. | Mission impact assessments default to `Unknown` when not evidenced. Rules must cite which evidence in the event payload triggered them. |
| **Telemetry on intake itself.** We need to see what intake is doing without spelunking logs. | Each intake invocation writes counts: `events_seen / processed / ignored / dropped / lag_ms`. Surfaced via existing ops tooling. |
| **Dry-run regression.** A future PR could accidentally flip dry_run=False everywhere. | dry_run defaults to True; flipping requires explicit caller-side opt-in. Tests assert that a dry-run intake call writes a decision row but produces zero side effects. |
| **Cockpit / EventBus drift.** Either could change shape during v0 development. | Both are explicitly excluded from v0 sourcing (§4.1). If a later PR adds them, it must include a writer-verification step first. |

---

## 6. Proposed PR sequence

Approved by Rigby Session 1250. Each PR is independently revertible
and lands in order.

| PR | Scope | Notes |
|---|---|---|
| **PR 1** | **Event inventory doc** (this file). + `build_docs_index` regen. | **In this PR.** No code. No behavior change. |
| **PR 2** | Read-only `platform_event_view` service. | New module at `core/services/platform_event_view.py`. Yields normalized event shape over existing tables. Watermarked. Tests against a fixture DB. **Do not implement until PR 1 lands.** |
| **PR 3** | OpsRun MissionRun-compatibility additions. | Migration: add nullable `domain`, `run_kind`, `mission_id` to OpsRun. Additive only. No backfill. Tests assert ops/mission isolation in queries. |
| **PR 4** | `rigby_event_intake(event_ref, dry_run=True)` Celery task. | On `pa` queue. Rule-based assessment only. Writes decision row. Idempotent. Dry-run default. |
| **PR 5** | Subscribe one safe emitter. | DeliverableEvent('status_transition') → intake task (dry_run=True). |
| **PR 6** | Enable one low-risk action class. | Flip dry_run=False for `Notify Chris` decisions only. Feature-flagged. PA-visible. |
| **PR 7+** | Additional emitters / delegate decisions. | Defer until PR 6 is observed under load for ≥1 week. Each new emitter is its own PR. Agent delegation requires explicit re-review of intake rules. |

---

## 7. Uncertainty noted during writing

These are surfaced honestly so PR 2+ can resolve them rather than
inherit the ambiguity:

1. **TriggerEvent / CockpitIncidentEvent / CockpitAutopilotEvent
   writers were not located in this discovery pass.** They are
   classified "Defined / unverified" in §1. Cockpit-family is already
   excluded from v0 sourcing, but TriggerEvent's status should be
   verified before any later PR considers it.
2. **EventBus subscriber liveness.** The `process_event_bus_*_queue`
   Beat tasks are scheduled and non-blocking (S1075), but whether
   they are actively dispatching to handlers under current load was
   not measured. v0 explicitly does not depend on EventBus, so this
   does not block PR 2 — but if EventBus is dormant, future PRs that
   want to consume it must verify first.
3. **AgentExecution status-transition signals.** The model has a
   heartbeat mechanism (S1100) and the LLMCallEvent + CeleryTaskEvent
   correlation, but explicit pre/post_save signal receivers for
   `status` field flips were not confirmed in this pass. If v0 later
   wants AgentExecution as an emitter, this needs explicit
   verification.
4. **`emit_orchestration_event` consumer.** It publishes to a
   `system_events` Channels group, but the consumer that subscribes
   to that group (if any) was not enumerated in this pass.
5. **`record_op` write coverage.** The helper exists
   (`core/services/operation_recorder.py:27`) but how many of the
   "significant operations" in the platform actually call it vs.
   bypass it was not measured.

None of these block PR 1. They are noted so the next PR's author can
resolve them in the platform_event_view design rather than discover
them at integration time.

---

## 8. References

- **Companion docs.** `docs/PLATFORM_INVENTORY.md` (runtime
  inventory anchor), `docs/PLATFORM_WHAT_IT_IS.md` (narrative
  anchor), `docs/handoffs/SESSION_1250_*.md` (when written).
- **Key code paths cited in this doc** (all verified to exist as of
  session 1250 open):
  - `core/models_celery_telemetry.py:17`
  - `core/models_llm_telemetry.py:30`
  - `core/models_impact_events.py:21`
  - `core/models_deliverables.py:561`
  - `core/models_ops_runs.py:52`
  - `core/models_situation_triggers.py:389`
  - `core/models/fleet.py:462`
  - `core/models_cockpit_incidents.py:41`
  - `core/models_cockpit_autopilot.py:33`
  - `core/celery_telemetry.py:74` (`task_prerun`), `:115`
    (`task_postrun`), `:177` (`task_failure`)
  - `core/signals/deliverable_status_signals.py:71`, `:94`
  - `core/signals/dream_signals.py:23`, `:46`
  - `core/signals/trigger_signals.py:26`
  - `core/services/event_bus.py:137`
  - `core/services/event_handlers.py:31`
  - `core/services/fleet_events.py:71`
  - `core/services/operation_recorder.py:27`
  - `core/services/orchestration_events.py:24`
  - `core/services/pa_status_events.py:116`, `:180`
  - `core/services/body_coordinator.py:110-200`
  - `core/services/opportunity_pipeline_orchestrator.py`
  - `core/services/llm_call_wrapper.py`
  - `core/agent_router.py`
  - `core/views_fleet_events.py:159`
  - `core/learning_bridges/` (10 bridge implementations)
- **Settings.** `core/settings.py:102`
  (`CELERY_TASK_EVENT_RETENTION_DAYS = 30`).
- **Audit context.** `docs/AUDIT_FINDINGS.md` §12 (canonical Celery
  deferred-task list).

---

## 9. PR 2 — `platform_event_view` service (read-only)

> Status: shipped in PR 2 of the Rigby Event Intake arc. Documentation
> only; no behavior change for existing emitters. The service is a
> read API over rows that already exist — it writes nothing.

### 9.1 Adapters implemented

| Adapter | Source name | Source model | Volume class |
|---|---|---|---|
| `DeliverableEventAdapter` | `deliverable_event` | `core.models_deliverables.DeliverableEvent` | `low` |
| `OpsRunEventAdapter` | `ops_run_event` | `core.models_ops_runs.OpsRunEvent` | `medium` |

Both are registered in `core/services/platform_event_view.py` via
`_ADAPTERS`. Callers list adapters with `supported_sources()` and
declare per-adapter volume with `volume_class(source)`.

### 9.2 Normalized record (`PlatformEvent`)

Frozen `@dataclass` defined in `core/services/platform_event_view.py`:

| Field | Type | Meaning |
|---|---|---|
| `source` | `str` | Adapter name (`deliverable_event` / `ops_run_event`). |
| `source_id` | `str` | String form of the source row's primary key. |
| `kind` | `str` | Source event_type, verbatim — not remapped. |
| `severity` | `str` | One of `SUPPORTED_SEVERITIES`. `unknown` when source row doesn't evidence a mapped severity. |
| `ts` | `datetime` | Source row's `created_at` (timezone-aware). |
| `payload` | `Mapping[str, Any]` | Per-source dict. Keys are stable per adapter; shape differs across sources. |
| `correlation_id` | `Optional[str]` | Best-effort cross-source key. |
| `raw_ref` | `str` | `<source>:<source_id>` — stable handle for the row. |

### 9.3 Severity vocabularies (closed)

`SUPPORTED_SEVERITIES = {debug, info, notice, warn, error, critical, unknown}`.

**DeliverableEvent.**

| Event type | Severity rule |
|---|---|
| `status_transition` | derived from `metadata['direction']`: `forward` / `same` → `info`; `backward` → `warn`; `terminal` → `notice`; missing / unrecognized → `unknown` |
| `synthesis_viewed`, `deliverable_saved`, `deliverable_exported`, `shared` | `info` |
| `task_created`, `followup_created`, `action_taken` | `notice` |
| Any other / unmapped value | `unknown` |

**OpsRunEvent.**

| Event type | Severity rule |
|---|---|
| `step_fail` | `error` |
| `step_pass` | `info` |
| `step_start`, `heartbeat` | `debug` |
| `info` | `info` |
| Any other / unmapped value | `unknown` |

### 9.4 Fields mapped per adapter

**DeliverableEvent → PlatformEvent.**

| Source field | Normalized location |
|---|---|
| `id` (UUID) | `source_id` (str), `raw_ref` suffix |
| `event_type` | `kind` |
| `created_at` | `ts` |
| `metadata['direction']` (for `status_transition`) | drives `severity` |
| `metadata['trace_id']` → `['execution_id']` → `['ctx']['trace_id']` → `['ctx']['execution_id']` | `correlation_id` (first non-empty) |
| `deliverable_id` | `payload['deliverable_id']` |
| `user_id` | `payload['user_id']` |
| `source` (provenance field on the row) | `payload['event_source']` (renamed to avoid collision with the normalized `source` field) |
| `metadata` (full dict) | `payload['metadata']` |

**OpsRunEvent → PlatformEvent.**

| Source field | Normalized location |
|---|---|
| `id` (UUID) | `source_id` (str), `raw_ref` suffix |
| `event_type` | `kind` |
| `created_at` | `ts` |
| `event_type` | drives `severity` |
| `detail['trace_id']` → `['execution_id']` → `['ctx']['trace_id']` → `['ctx']['execution_id']` | `correlation_id` (first non-empty) |
| `run_id` | `payload['run_id']` |
| `label` | `payload['label']` |
| `detail` (full dict) | `payload['detail']` |

### 9.5 Watermark + ordering

- Ordering: `ts ASC, source_id ASC`. Deterministic and stable across runs.
- Watermark API: `iter_events(source, since_ts=..., since_id=..., limit=...)`.
  - Both `since_ts` and `since_id` set: strict resume after the
    `(ts, source_id)` pair. Boundary tie (`ts == since_ts`) is
    decided by `source_id > since_id`.
  - `since_ts` alone: strict `ts > since_ts`.
  - Both `None`: from the beginning.
- Memory: unbounded reads use `qs.iterator(chunk_size=200)`. Bounded
  reads (`limit=N`) materialize at most `N` rows into a list (sliced
  QuerySets cannot use `.iterator()`).
- Idempotent: identical arguments yield identical records in identical
  order assuming the underlying rows do not change.

### 9.6 Deferred sources (explicitly NOT in PR 2)

These adapters are deliberately **not implemented** per the v0
direction in §4. Adding any of them is a separate PR with explicit
verification (writer liveness, volume estimation, severity vocab):

- `celery_task_event` (high volume; needs watermark stress testing)
- `llm_call_event` (high volume; per-call telemetry)
- `impact_event` (mission-relevant but needs schema review)
- `fleet_event` (semantics owned by fleet team; do not repurpose)
- `trigger_event` (writer paths unverified in PR 1 §7)
- `cockpit_incident_event`, `cockpit_autopilot_event`,
  `cockpit_audit_log` (defer per §4)
- Anything sourced from the Redis EventBus

### 9.7 Known limitations

1. **`payload` shape varies across adapters.** Callers must do per-source
   interpretation. This is intentional — the goal is normalization of
   identity / time / classification, not a unified payload schema. A
   future PR can add per-source TypedDicts if intake-side code starts
   to suffer.
2. **Watermark is `(ts, source_id)`, not a single monotonic cursor.**
   Storing a resume token means storing both. This is the cost of
   honest tie-break under `auto_now_add` clocks. A `BIGSERIAL`-style
   cursor would be simpler but requires a schema change to the source
   tables; out of scope for PR 2.
3. **No multi-source merging.** `iter_events` reads one source at a
   time. Cross-source ordering / fan-in is intake-side responsibility
   (deferred to PR 4+).
4. **`limit=N` materializes a list, not a cursor.** Memory bound is
   `N rows × normalized record size`. Safe for any reasonable batch
   size; do not pass `limit=10_000_000`.
5. **Severity mappings are conservative.** "Unknown" is the explicit
   fallback whenever the source row does not evidence a mapped
   classification. This is per §5 guardrail "Keep mission impact as
   Unknown when not evidenced." Tightening any mapping is a future PR
   that should also update tests.
6. **`correlation_id` fallback is best-effort.** If no event in the
   chain populates the metadata, `correlation_id` is `None`. PR 4+
   intake-side code should handle `None` explicitly rather than skip
   uncorrelated events.
7. **No DB-level enforcement of read-only.** Module is read-only by
   convention + AST tests. A future PR could route through a
   read-only DB user / replica if production hardening becomes
   warranted.

### 9.8 What lands in this PR

- `core/services/platform_event_view.py` — new module (~310 lines).
- `core/tests/test_platform_event_view.py` — new test file (~470
  lines, 30 tests, real-DB integration over 120 mixed fixture rows).
- This §9 added to `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/INDEX.md` regenerated via `python manage.py build_docs_index`.

No code changes outside the new service file + tests. No migrations.
No behavior change for existing emitters or consumers.

---

*This is a discovery snapshot. The runtime inventory in
`PLATFORM_INVENTORY.md` remains the authoritative source for any
quantitative count; if this doc and the inventory disagree on a
number, the inventory wins per `DOC_LIFECYCLE.md` §2c.*
