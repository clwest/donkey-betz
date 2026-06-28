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

## 10. PR 3 — OpsRun MissionRun-compatibility fields

> Status: shipped in PR 3 of the Rigby Event Intake arc. Additive
> migration to OpsRun + Option B domain filtering in
> `platform_event_view`. No new model. No behavior change for existing
> OpsRun callers.

### 10.1 Why OpsRun, not a new MissionRun model

PR 1 §4.3 approved reusing `OpsRun` / `OpsRunEvent` as the MissionRun
v0 primitive **only if ops vs mission separation is preserved**. PR 3
honors that constraint:

- OpsRun already has the right shape: a run + per-step timeline +
  heartbeat (`step_start` / `step_pass` / `step_fail` / `info` /
  `heartbeat` events).
- A parallel MissionRun model would duplicate that infrastructure and
  force per-source plumbing in `platform_event_view`, signal handlers,
  ops UIs, and the body coordinator. None of that delivers user value
  in v0.
- The honest cost of reuse is one CharField (`domain`) that callers
  must read; the honest cost of a parallel model is duplicated
  migrations, duplicated indexes, duplicated docs, and an integration
  surface that has to bridge the two later. PR 3 buys the cheap option.

The decision is **reversible**. If mission semantics diverge from ops
semantics enough that a separate model is justified, a future PR can
introduce `MissionRun` and migrate mission-domain rows over without
breaking ops callers. The fields added in PR 3 (`domain`, `run_kind`,
`mission_id`) are the same fields a `MissionRun` model would have, so
the data is portable.

### 10.2 Fields added to OpsRun

Migration: `core/migrations/0370_session_1250_opsrun_mission_fields.py`.

| Field | Type | Default | Index | Purpose |
|---|---|---|---|---|
| `domain` | `CharField(max_length=20, choices=ops/mission)` | `'ops'` | yes | Top-level scope. Do **not** overload `run_type`. |
| `run_kind` | `CharField(max_length=40, blank=True)` | `''` | no | Sub-classification within domain (e.g., `intake` / `decision` / `delegation` / `verification` for mission). Free-form per-domain. |
| `mission_id` | `UUIDField(null=True, blank=True)` | `None` | yes | Mission identity. Null for ops-domain rows. |

Migration is **additive only**. No backfill. No behavior change for
existing OpsRun callers: every legacy creation path
(`ops_loop` / `smoke_test` / `deploy_verify` / `manual` /
`llm_routing`) gets `domain='ops'` implicitly via the column default.

`OpsRunEvent` schema is **unchanged**. The event-row's domain is
derivable via the parent join (`OpsRunEvent.run__domain`), not stored
on the event row itself.

### 10.3 The ops/mission separation invariant

The contract enforced by tests in
`core/tests/test_opsrun_mission_fields.py`:

- `OpsRun.objects.filter(domain='ops')` returns **only** ops-domain
  rows; mission rows are excluded.
- `OpsRun.objects.filter(domain='mission')` returns **only**
  mission-domain rows; ops rows are excluded.
- `run_type` is orthogonal to `domain`. A mission-domain row can still
  carry `run_type='manual'` for compatibility with existing ops
  tooling that filters on `run_type`. Mission taxonomy lives in
  `run_kind`, not in `run_type`.
- `OpsRunEvent` is unaware of domain at the schema level. Consumers
  that need domain-aware filtering go through the
  `platform_event_view` adapter (§10.4).

**What this invariant prevents.** Ops dashboards, ops alerts, ops
metrics rollups, and the body coordinator all filter on `run_type`
(legacy) and/or `domain='ops'` (new). None of them surface
mission-domain rows by accident. Mission-side code does the inverse.

### 10.4 Domain filtering in `platform_event_view`

PR 3 implements Option B from the PR 2 report: the read API exposes
domain filtering at the public entrypoint, so consumers cannot
accidentally pull cross-domain rows.

```python
# All ops-run events (ops + mission) — PR 2 behavior preserved
list(iter_events("ops_run_event"))

# Ops-domain events only
list(iter_events("ops_run_event", domain="ops"))

# Mission-domain events only
list(iter_events("ops_run_event", domain="mission"))
```

**Semantics:**

- `domain=None` (default): yields all rows for the source —
  byte-identical to PR 2 behavior.
- `domain='ops'`: filters via `OpsRunEvent.objects.filter(run__domain='ops')`.
- `domain='mission'`: filters via `OpsRunEvent.objects.filter(run__domain='mission')`.
- `domain` outside `{'ops', 'mission'}`: raises `ValueError`.
- `domain` provided on any source other than `'ops_run_event'` (e.g.,
  `iter_events('deliverable_event', domain='ops')`): raises
  `ValueError`. DeliverableEvent has no domain concept; this is a
  hard error, not a silent ignore.

The capability is declared at module level via
`SUPPORTED_DOMAINS = {'ops', 'mission'}` and
`DOMAIN_FILTER_SOURCES = {'ops_run_event'}`.

### 10.5 What is still out of scope

- **No new MissionRun model.** Per §10.1.
- **No OpsRunEvent schema changes.** Event-row schema is frozen for
  v0. Per §10.2.
- **No `run_type` overloading.** Mission taxonomy goes into
  `run_kind`. Per §10.3.
- **No intake task.** That is PR 4.
- **No signal handlers** to react to OpsRun creation / mission_id
  changes. PR 4 / PR 5 may add these.
- **No agent dispatch** triggered by mission rows.
- **No frontend changes.** Ops UIs continue to filter on
  `domain='ops'` (or via the existing `run_type` filters); mission UIs
  do not exist yet.
- **No backfill** of historical OpsRun rows to a mission domain. All
  legacy rows are ops-domain. If a future PR identifies rows that
  should be reclassified, it can do so with an explicit data
  migration.
- **No reverse-migration safety beyond Django's `AddField` default.**
  If a future operator runs `migrate core 0369`, the three new
  columns will drop; any data in them will be lost. This is standard
  Django behavior; not a v0 concern.

### 10.6 What lands in this PR

- `core/migrations/0370_session_1250_opsrun_mission_fields.py` — new
  migration (additive, 3 fields).
- `core/models_ops_runs.py` — adds the 3 fields + `DOMAIN_CHOICES`
  constant. Existing model behavior unchanged.
- `core/services/platform_event_view.py` — adds `domain` kwarg
  validation at the public entrypoint + `domain` join on the
  OpsRunEventAdapter. DeliverableEventAdapter ignores the kwarg (the
  public entrypoint rejects it before the adapter runs).
- `core/tests/test_opsrun_mission_fields.py` — new test file (~180
  lines, 13 tests: defaults, mission isolation, index presence,
  OpsRunEvent schema unchanged).
- `core/tests/test_platform_event_view.py` — extended with
  `OpsRunEventDomainFilterTests` (7 new tests, covers all 6 spec
  cases + composition with watermark).
- This §10 added to `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/INDEX.md` regenerated via `python manage.py build_docs_index`.

All 50 tests across `test_platform_event_view` +
`test_opsrun_mission_fields` pass in ~0.5s on the real PostgreSQL
test DB.

---

## 11. PR 4 — `rigby_event_intake` Celery task (dry-run)

> Status: shipped in PR 4 of the Rigby Event Intake arc. **No new
> model. No new migration. No subscribers wired.** The task is
> invocable by hand or from future PR 5 subscribers and is
> `dry_run=True` by default.

### 11.1 Architecture: MissionRun-as-intake-record

PR 4 honors the Session 1250 architecture decision documented in
§10.1: **no `IntakeDecision` model is created.** The intake-decision
record lives inside an `OpsRun` row with `domain='mission'` and
`run_kind='intake'`. The lifecycle is captured as `OpsRunEvent` rows
on the same parent, forming a single authoritative record from
event → assessment → decision.

```
Platform Event arrives
   │
   ▼
rigby_event_intake(event_ref, dry_run=True)  ── core/services/rigby_event_intake.py
   │
   ├── derive_mission_id(event_ref)
   │     = uuid5(MISSION_INTAKE_NAMESPACE, event_ref)
   │
   ├── platform_event_view.get_event(event_ref)   ── PR 2 read API
   │
   ├── OpsRun.objects.get_or_create(
   │       mission_id=<derived>,
   │       domain='mission', run_kind='intake',
   │       defaults={title, run_type='manual', triggered_by='pa_tool',
   │                 status='running', summary={event_ref, dry_run, ...}},
   │   )
   │
   ├── OpsRunEvent.get_or_create(run=<>, label='intake_started',
   │       defaults={event_type='info', detail={event_ref, dry_run,
   │                                            source, source_id}})
   │
   ├── apply_rules_v0(event)
   │     │
   │     ▼ DecisionResult(decision, mission_impact, rules_fired, reason)
   │
   ├── OpsRunEvent.get_or_create(run=<>, label='impact_assessed',
   │       defaults={event_type='info',
   │                 detail={mission_impact, severity, rules_fired, reason}})
   │
   ├── OpsRunEvent.get_or_create(run=<>, label='decision_made',
   │       defaults={event_type=('info'|'step_pass'),
   │                 detail={decision, mission_impact, rules_fired,
   │                         reason, dry_run}})
   │
   ├── If still 'running': MissionRun.summary updated, status='passed',
   │   finished_at=now.
   │
   └── Telemetry: structured log line `[RIGBY_INTAKE] ...`
```

### 11.2 Why no IntakeDecision model

Reasoning is in §10.1 (the MissionRun-as-primitive argument) plus the
Session 1250 reevaluation. The short form:

- **One authoritative record.** Decision + lifecycle in one place,
  walkable via `OpsRunEvent.objects.filter(run__mission_id=...)`.
- **Future stages (delegation / verification / learning) are additive.**
  Each is one new OpsRunEvent label. No new model ever.
- **Existing infrastructure already reads MissionRun.** PR 3's
  `platform_event_view` adapter sees mission events; ops UIs / mission
  UIs share code paths.
- **DB-level enforcement (closed-vocab `decision`) is not a v0
  requirement** — Python validation + tests + the `DecisionResult`
  dataclass enforce the contract at write time. (CharField `choices=`
  validate form/admin input only — see memory
  `feedback_deliverable_create_defaults_to_completed.md`.)

### 11.3 Idempotency via `mission_id = uuid5(NAMESPACE, event_ref)`

- `MISSION_INTAKE_NAMESPACE = uuid5(NAMESPACE_DNS,
  'rigby-event-intake.donkeybetz.com')` — derived once at module load,
  stable across processes.
- Same `event_ref` → same `mission_id` → same `OpsRun` via
  `get_or_create`.
- Each lifecycle event uses `get_or_create(run=<>, label=<>)` keyed on
  the `(run, label)` pair, so re-running writes zero duplicates.
- MissionRun is only finalized if status is still `running` —
  prevents an over-write on re-run.

**Known limitation:** without a unique constraint on
`(domain, run_kind, mission_id)`, two concurrent processes could
race on first creation. V0 acceptable; addressable later via a
unique-together migration or a Postgres advisory lock.

### 11.4 Decision rules v0

Hard-coded in `apply_rules_v0`. **No rule registry, no pluggability —
Option A per the Session 1250 reevaluation.** First match wins;
otherwise `ignore`:

| Condition | Decision | Mission impact | Rule id |
|---|---|---|---|
| `deliverable_event` + `status_transition` + `metadata.direction == 'backward'` | `monitor` | `low` | `deliverable_status_backward` |
| `deliverable_event` + `status_transition` + `metadata.direction == 'terminal'` | `notify` | `medium` | `deliverable_status_terminal` |
| `ops_run_event` + `kind == 'step_fail'` | `notify` | `medium` | `ops_step_fail` |
| Otherwise | `ignore` | `unknown` | (none) |

**Invariants enforced by `DecisionResult.__post_init__`:**

- `decision ∈ {ignore, log, monitor, notify, create_initiative, delegate}`.
- `mission_impact ∈ {unknown, low, medium, high}`.
- Non-`unknown` mission_impact **requires** at least one entry in
  `rules_fired`. A silent "this is medium impact" without evidence is
  a `ValueError` at construction time.

### 11.5 dry_run behavior (v0 default)

- **Default:** `dry_run=True`.
- **Allowed v0 side effects** (under any caller context):
  - One MissionRun (OpsRun with `domain='mission'`).
  - Up to three OpsRunEvent timeline rows.
  - One structured log line.
- **Forbidden v0 side effects** (no flag flips them on):
  - No notifications.
  - No initiative creation.
  - No agent dispatch.
  - No tool dispatch.
  - No external HTTP calls.
  - No LLM invocations.

Tests assert these absences by counting rows on adjacent models
(Deliverable / DeliverableEvent) before vs. after the task runs, and
by inspecting which model rows the task touched.

### 11.6 Telemetry contract

The single `[RIGBY_INTAKE]` log line carries:

| Field | Type | Meaning |
|---|---|---|
| `events_seen` | int | Always `1` for single-event invocation. |
| `processed` | int | `1` if a decision was reached, `0` if dropped. |
| `ignored` | int | `1` if `decision == 'ignore'`, else `0`. |
| `dropped` | int | `1` if the event row could not be loaded, else `0`. |
| `lag_ms` | int | Wall time in the task body. |
| `event_ref` | str | Echo of the caller-provided event_ref. |
| `decision` | str | Closed-vocab decision value. |
| `dry_run` | bool | The dry_run flag (always `True` in v0 actual usage). |
| `mission_id` | UUID | Derived mission_id. |

### 11.7 Timeline event labels (stable)

These are the public surface of the intake — future stages (PR 5+)
extend the timeline by adding new labels, never modifying existing
ones.

| Label | Event type | When written | Detail keys |
|---|---|---|---|
| `intake_started` | `info` | First call. | `event_ref`, `dry_run`, `source`, `source_id` |
| `impact_assessed` | `info` | After rules evaluated (event loaded successfully). | `mission_impact`, `severity`, `rules_fired`, `reason` |
| `decision_made` | `info` (ignore) / `step_pass` (any other) / `step_fail` (drop) | After decision reached or drop confirmed. | `decision`, `mission_impact`, `rules_fired`, `reason`, `dry_run`, `dropped?` |

### 11.8 Drop vs. error: who raises, who records

| Input shape | Behavior |
|---|---|
| Malformed `event_ref` (empty / no colon / missing source / missing id) | `ValueError`; **no MissionRun created** |
| Unknown source (e.g., `celery_task_event:...`) | `ValueError`; **no MissionRun created** |
| Valid source, source_id missing in DB | MissionRun created with `status='failed'`; `decision_made` event_type=`step_fail`; telemetry `dropped=1`; **does not raise** |

The split is intentional: caller-side bugs (malformed input) crash
loud; legitimate drops (stale event_ref) leave a paper trail.

### 11.9 What is still out of scope (deferred)

- **No subscribers wired.** The task is not invoked by any signal,
  Beat schedule, or consumer in PR 4. PR 5 wires the first
  subscriber.
- **No agent dispatch.** Even if `decision == 'delegate'`, the task
  writes the decision and stops. The actual delegation to
  `agent_router.route()` is PR 7+.
- **No notifications.** `decision == 'notify'` writes the decision;
  PR 6 enables the actual notify pathway.
- **No LLM in assessment.** Rules are deterministic.
- **No rule registry.** Adding rules in PR 5+ means editing
  `apply_rules_v0` directly. Refactor to a registry only if rule count
  outgrows the if/elif chain.
- **No `worker` import edit.** The task is registered via
  `@shared_task` decoration; Celery picks it up when the module is
  imported. PR 5's subscriber will import this module → registration
  becomes ambient. The PR 4 tests bypass `.apply()` (which closes
  test-transaction DB connections via Celery's
  `close_old_connections` signal) and call the inner `_run_intake`
  function directly.
- **No `core/celery.py` change** to add the module to
  `app.conf.imports`. Defer to PR 5 when there's an actual caller.

### 11.10 What lands in this PR

- `core/services/rigby_event_intake.py` — new module (~330 lines).
  Includes constants, `DecisionResult` dataclass, `derive_mission_id`,
  `apply_rules_v0`, `_run_intake` (the implementation), and the
  Celery task entrypoint.
- `core/services/platform_event_view.py` — adds `get_event(event_ref)`
  and a `BaseAdapter.get(source_id)` abstract method. Both adapters
  implement `get` via `Model.objects.get`. Read-only still holds.
- `core/tests/test_rigby_event_intake.py` — new test file (~480
  lines, 38 tests).
- This §11 added to `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/INDEX.md` regenerated via `python manage.py build_docs_index`.

**Test summary (real PostgreSQL test DB):**
- 38/38 PR 4 tests green in 0.56s.
- 88/88 across PR 2 + PR 3 + PR 4 green in 0.96s.
- All earlier static guardrails (no EventBus / LLM / Cockpit imports
  / writes / `.objects.all()` scans) still pass against the modified
  `platform_event_view.py`.

---

## 12. PR 5 — Subscribe DeliverableEvent → Rigby Intake

> Status: shipped in PR 5 of the Rigby Event Intake arc. First real
> emitter wired. **Default OFF.** The subscriber is deploy-controlled
> via ``settings.RIGBY_EVENT_INTAKE_ENABLED`` until PR 6 flips it on
> after observation.

### 12.1 First subscribed emitter

The post_save receiver in
`core/signals/deliverable_status_signals.py` already wrote a
`DeliverableEvent('status_transition')` row on every Deliverable status
flip (since Session 1095). PR 5 adds **one additional step** to that
receiver:

```
Deliverable.status changes (forward / backward / terminal)
   │
   ▼ deliverable_status_signals.py
   │
   ├── DeliverableEvent('status_transition') row written
   │
   └── transaction.on_commit(lambda: _enqueue_rigby_intake(event_ref, deliverable_id))
       │
       ▼ if settings.RIGBY_EVENT_INTAKE_ENABLED:
       │     rigby_event_intake.apply_async(
       │         args=['deliverable_event:<de.id>'],
       │         kwargs={'dry_run': True},
       │     )
       │     log [RIGBY_INTAKE_SUBSCRIBE] event_ref task_id deliverable_id dry_run flag
       │
       └── else: no-op (silent)
```

Other DeliverableEvent event_types (`synthesis_viewed`, `shared`,
`task_created`, etc.) are **not** subscribed. Only the
``status_transition`` path enqueues. Asserted by
`test_synthesis_viewed_event_does_not_enqueue` and
`test_shared_event_does_not_enqueue`.

### 12.2 Feature flag behavior

| Setting | Default | When False | When True |
|---|---|---|---|
| `RIGBY_EVENT_INTAKE_ENABLED` | `False` | `_enqueue_rigby_intake()` returns immediately; no `apply_async`. The `DeliverableEvent` row is still written (the legacy COO rework path is unaffected). | `apply_async` is called with `args=['deliverable_event:<de.id>']`, `kwargs={'dry_run': True}`, on the `pa` queue. Logged via `[RIGBY_INTAKE_SUBSCRIBE]`. |

The flag is read from the environment variable
`RIGBY_EVENT_INTAKE_ENABLED` (string `'true'`/`'false'`, case-insensitive)
and bound at Django startup in `core/settings.py`. Operators flip it
via deploy env, not via runtime `config_tool` — this is the **first
real event subscription**, so deploy-controlled gating is the
appropriate caution level for v0.

### 12.3 dry_run behavior

PR 5 always passes `dry_run=True`. There is no callsite in PR 5 that
sets `dry_run=False`. That flag flip lives in PR 6 and will be gated
behind a separate setting / decision-class allowlist.

### 12.4 `transaction.on_commit` protection

The enqueue is wrapped in `transaction.on_commit(lambda: ...)`. This
guarantees:

- If the surrounding transaction **commits**, the callback runs and
  `apply_async` is invoked.
- If the surrounding transaction **rolls back**, the callback is
  **discarded** — no enqueue happens, so we never reference a
  `DeliverableEvent` row that was never persisted.
- Outside any explicit transaction (autocommit mode), the callback
  fires immediately after the save returns.

Tests verify both halves of this contract:
`TransactionRollbackTests.test_rollback_suppresses_enqueue` and
`test_commit_fires_enqueue`. Real `TransactionTestCase` is used here
(not `TestCase`) because `TestCase`'s outer transaction always rolls
back, which would prevent any `on_commit` callbacks from firing.

For tests that DO use `TestCase` (the FlagOn / FlagOff classes),
Django's `self.captureOnCommitCallbacks(execute=True)` context
manager is used to flush callbacks at the end of the test block.

### 12.5 Worker registration

`core/celery.py` `app.conf.imports` tuple now includes
`'core.services.rigby_event_intake'`. Workers import this module at
boot, which registers the task name
`'core.services.rigby_event_intake.rigby_event_intake'` in the Celery
task registry. Without this, `apply_async()` from the signal handler
would fail with `KeyError: <task name>` at runtime.

Verified by `TaskRegistrationTests.test_task_is_registered_on_celery_app`
and `test_task_in_app_conf_imports`.

### 12.6 Telemetry contract

On every successful enqueue, the subscriber emits a `[RIGBY_INTAKE_SUBSCRIBE]`
log line carrying:

| Field | Source | Purpose |
|---|---|---|
| `event_ref` | `f'deliverable_event:{de.id}'` | What was queued. |
| `task_id` | `apply_async()` return | Trace into Celery's CeleryTaskEvent rows / `[RIGBY_INTAKE]` task log. |
| `deliverable_id` | `instance.pk` | Trace back to the source Deliverable. |
| `dry_run` | always `True` in PR 5 | Explicit, not implicit. |
| `flag` | always `ON` when the line emits | Confirms the gate was checked and open. |

This line is the join key between (a) the signal-side
`[RIGBY_INTAKE_SUBSCRIBE]` log, (b) the task-side `[RIGBY_INTAKE]`
log (PR 4 §11.6), and (c) the `MissionRun.summary` written by the
task.

### 12.7 Current operational state

| Surface | State |
|---|---|
| `DeliverableEvent('status_transition')` post_save receiver | wired to intake task via `transaction.on_commit` |
| `RIGBY_EVENT_INTAKE_ENABLED` setting | `False` by default (deploy-controlled) |
| Worker task registration | live (via `app.conf.imports`) |
| `dry_run=True` | hard-coded by subscriber; PR 5 has no way to flip it |
| Other emitters (CeleryTaskEvent, LLMCallEvent, ImpactEvent, OpsRunEvent direct, FleetEvent, TriggerEvent, Cockpit*) | not subscribed (deferred — PR 7+) |
| Notifications / agent dispatch / initiative creation | not enabled (deferred — PR 6 for notify, PR 7+ for others) |

**Net behavior when `RIGBY_EVENT_INTAKE_ENABLED=False`** (the
production default): zero functional change vs. PR 4. The path
exists; no enqueues fire.

### 12.8 What is still out of scope

- **No flag flip to ON in production.** PR 5 ships the wiring with
  the flag OFF. Operators may flip it in staging / locally to
  observe; PR 6 is the first PR that recommends a production flip.
- **No `dry_run=False`.** PR 6 introduces decision-class gating
  (e.g., "Notify-Chris decisions actually emit notifications now").
- **No agent dispatch.** PR 7+.
- **No new emitters beyond DeliverableEvent.** OpsRunEvent staying
  unsubscribed is intentional — it's the source the intake task
  itself writes to (it would self-loop if subscribed naively).
- **No config_tool runtime toggle.** Deploy-controlled v0 only.
- **No LLM in assessment.** PR 4's rule-based path is the contract.

### 12.9 Known limitation — pre-existing CeleryTaskEvent NOT NULL drift

During eager-mode end-to-end tests in PR 5 we observed
`IntegrityError: null value in column "queue" of relation
"core_celerytaskevent"` from the existing Celery telemetry signal
handlers (`core/celery_telemetry.py`). The error is **caught and
swallowed** by the existing telemetry code, so it does not affect
intake behavior or test results — but it indicates a pre-existing
drift in `CeleryTaskEvent.queue` column NOT NULL constraint that
the telemetry writer does not honor for eager-mode invocations.

Out of scope for PR 5. Documented here so a future PR (or a
`build_celery_audit` follow-up) can address it.

### 12.10 What lands in this PR

- `core/settings.py` — adds `RIGBY_EVENT_INTAKE_ENABLED` (default
  `False`).
- `core/celery.py` — adds `'core.services.rigby_event_intake'` to
  `app.conf.imports` for worker registration.
- `core/signals/deliverable_status_signals.py` — adds
  `_enqueue_rigby_intake()` helper + `transaction.on_commit()` hook
  in `record_status_transition`. Other behavior unchanged.
- `core/tests/test_deliverable_intake_subscriber.py` — new test file
  (~330 lines, 13 tests).
- This §12 added to `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/INDEX.md` regenerated via `python manage.py build_docs_index`.

**Test summary (real PostgreSQL test DB):**
- 13/13 PR 5 tests green in 5.85s (slower than prior PRs because
  TransactionTestCase + eager Celery require real commits).
- 101/101 across PR 2 + PR 3 + PR 4 + PR 5 green in 6.77s.
- All earlier static guardrails still pass.

---

## 13. PR 6 — Rigby internal work queue (`RigbyWorkItem`)

> Status: shipped in PR 6 of the Rigby Event Intake arc. **No human
> notification. No agent dispatch.** Actionable intake decisions
> create a `RigbyWorkItem` row in Rigby's own queue. Default OFF.

### 13.1 Why Notify-Chris was deferred

The original PR 5 → PR 6 path proposed "Notify Chris" as the first
live action. **Chris's S1250 directive overrode that.** The principle:
**events should first create operational awareness for Rigby. Humans
should only be notified when Rigby determines human judgment is
needed.**

Making Chris the default target of every actionable intake decision
would have:

- Made Chris the exception handler for every status_transition.
- Skipped the prior step where Rigby evaluates whether the decision
  even needs a human at all.
- Coupled Rigby's operational maturity to Chris's attention budget.

PR 6 instead gives Rigby a **queue she can review on her own
cadence**. Chris becomes the exception handler — escalated only when
Rigby decides she needs him. The Notify-Chris path is still on the
roadmap (later PR), but it now sits **after** Rigby's queue, not
parallel to it.

### 13.2 `RigbyWorkItem` purpose

One row per actionable intake decision. The queue is Rigby's own
operational surface — what she has open, what she's acknowledged,
what she's resolved, what she's ignored.

**Schema** (`core/models_rigby_work_items.py`):

| Field | Type | Purpose |
|---|---|---|
| `id` | UUID | Primary key. |
| `source_mission_run` | FK → `OpsRun` | The MissionRun (domain='mission') that produced this work item. |
| `source_event_ref` | CharField (indexed) | Canonical `<source>:<source_id>` handle of the originating event. |
| `decision` | CharField (indexed) | Mirror of intake decision (`monitor` / `notify` in v0). |
| `severity` | CharField | PR 2 closed vocab. |
| `mission_impact` | CharField | PR 4 closed vocab. |
| `priority` | PositiveSmallIntegerField (indexed) | Derived from mission_impact (unknown=1 / low=3 / medium=5 / high=8). Higher = sooner. |
| `title` | CharField(200) | Short human-readable title for Rigby's queue UI. |
| `summary` | TextField | Reason / context — quoted from the rule. |
| `recommended_next_action` | TextField | What Rigby (or her future tooling) should consider doing. |
| `evidence` | JSONField | `{event_ref, rules_fired, decision_reason, source, kind, severity}`. |
| `status` | CharField (choices, indexed) | `open` / `acknowledged` / `resolved` / `ignored`. Default `open`. |
| `created_at` | DateTimeField (indexed) | auto_now_add. |
| `updated_at` | DateTimeField | auto_now. |
| `resolved_at` | DateTimeField (nullable) | Populated by future PR when Rigby resolves an item. |

**Constraints:**

- `unique_together = ('source_event_ref', 'decision')` — idempotent
  on re-run. Re-running the intake on the same event_ref returns the
  same work item; never produces a duplicate row. Different decisions
  on the same event_ref (would only happen if rules change between
  runs — not in v0) get distinct rows.
- `indexes` on `(status, -priority, -created_at)` and
  `(decision, -created_at)` so Rigby's queue can be sorted cheaply.

### 13.3 How the internal work queue fits the COO model

```
Platform Event arrives
   │
   ▼
rigby_event_intake (PR 4 / 5)
   │
   ├── MissionRun (OpsRun, domain='mission', run_kind='intake')
   ├── OpsRunEvent: intake_started → impact_assessed → decision_made
   │
   ├── If decision is actionable AND RIGBY_INTERNAL_WORK_QUEUE_ENABLED:
   │     RigbyWorkItem (status='open')           ← PR 6 lands HERE
   │
   ├── MissionRun.status = 'passed' (or 'failed' on drop)
   │
   ▼
[Rigby reviews her queue async — PR 7+]
   │
   ├── work_item.acknowledged → Rigby has seen it
   ├── work_item.resolved → Rigby took action
   ├── work_item.ignored → Rigby decided no action needed
   │
   ▼
[Escalate to human — PR 8+ if needed]
   │
   ├── Notify Chris (only when Rigby decides human judgment is needed)
   ├── Create Initiative (formal multi-step workflow)
   ├── Delegate to specific agent
```

This sequence respects the new principle: **Rigby first, Chris on
escalation.** It also extends the MissionRun timeline naturally —
future PRs adding `escalated_to_chris` / `delegated_to_agent_X` /
`resolved` events on the same OpsRun parent row keep the full
event-to-outcome lineage in one place.

### 13.4 v0 actionable decision set

```python
ACTIONABLE_DECISIONS = {"monitor", "notify"}
```

- `ignore` — never produces a work item (intentional; the rule
  decided there is nothing to do).
- `log` — reserved closed-vocab value, no v0 rule produces it; no
  work item path.
- `create_initiative` / `delegate` — deferred to later PRs which need
  to make additional plumbing decisions about what those mean.

### 13.5 Feature flag behavior

`settings.RIGBY_INTERNAL_WORK_QUEUE_ENABLED` (default `False`).
Environment-controlled via `RIGBY_INTERNAL_WORK_QUEUE_ENABLED=true`.

| Setting | Behavior |
|---|---|
| `False` (default) | Intake still runs end-to-end; MissionRun + 3 OpsRunEvents still written; **no RigbyWorkItem rows created** regardless of decision. |
| `True` | Actionable decisions (`monitor` / `notify`) create a RigbyWorkItem row via `get_or_create(source_event_ref=..., decision=...)`. `ignore` decisions never produce a row. |

This is the **second** feature flag in the intake pipeline. Both must
be on for the full chain to execute:

| Flag | Gates |
|---|---|
| `RIGBY_EVENT_INTAKE_ENABLED` (PR 5) | DeliverableEvent → `apply_async(rigby_event_intake)` |
| `RIGBY_INTERNAL_WORK_QUEUE_ENABLED` (PR 6) | Actionable decision → RigbyWorkItem row |

Belt-and-braces gating means flipping just one flag is well-defined:

- Only PR 5 flag ON: intake runs but no work items created.
- Only PR 6 flag ON: signal does not enqueue, so intake never runs;
  the PR 6 flag has nothing to act on.
- Both ON: full chain executes.

### 13.6 Priority ladder (v0)

| `mission_impact` | `priority` |
|---|---|
| `unknown` | 1 |
| `low` | 3 |
| `medium` | 5 |
| `high` | 8 |

Higher priority = Rigby should look at it sooner. The ladder is
intentionally sparse (1/3/5/8) so future tiers can land between
existing values without renumbering.

### 13.7 What is still out of scope

- **No human notification.** PR 6 does NOT send anything to Chris,
  Discord, email, push, or any other human-facing channel. The work
  item is a Rigby-internal row only.
- **No agent dispatch.** No `agent_router.route()` call, no Celery
  task targeting an agent, no tool dispatch.
- **No initiative creation.** `create_initiative` is a decision value
  but not v0 actionable.
- **No queue consumer.** PR 6 only **writes** to the queue. Rigby's
  side (review / acknowledge / resolve / ignore) is PR 7+. There is
  no consumer code yet; the queue accumulates.
- **No queue surface in the Workspace UI.** Frontend exposure is a
  separate PR.
- **No LLM in assessment.** Decision rules remain deterministic (PR
  4).
- **No new emitters.** Only DeliverableEvent + OpsRunEvent (via PR
  5's wired subscriber and direct calls in tests).

### 13.8 What lands in this PR

- `core/models_rigby_work_items.py` — new model file (~110 lines).
- `core/migrations/0371_session_1250_rigby_work_item.py` — additive
  migration.
- `core/models/__init__.py` — re-export `RigbyWorkItem`.
- `core/services/rigby_event_intake.py` — adds `ACTIONABLE_DECISIONS`
  constant, `_PRIORITY_BY_IMPACT` map, `_compose_work_item_fields`
  helper, `_maybe_create_work_item` function; calls it after
  `decision_made` event. Return dict gains `work_item_id` (str or
  `None`).
- `core/settings.py` — adds `RIGBY_INTERNAL_WORK_QUEUE_ENABLED`
  (default `False`).
- `core/tests/test_rigby_work_item.py` — new test file (~340 lines,
  18 tests).
- This §13 added to `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/INDEX.md` regenerated via `python manage.py build_docs_index`.

**Test summary (real PostgreSQL test DB):**
- 18/18 PR 6 tests green in 0.73s.
- 119/119 across PR 2 + PR 3 + PR 4 + PR 5 + PR 6 green in 7.30s.
- All earlier static guardrails still pass.

---

## 14. PR 7 — Rigby work-queue review tools

> Status: shipped in PR 7 of the Rigby Event Intake arc. PA tool
> surface for Rigby to read and transition her own queue. **Still no
> human notification. Still no agent dispatch.** Default OFF.

### 14.1 Tools added

One new PA tool, `rigby_work_item`, with four actions:

| Action | Purpose | Required | Optional |
|---|---|---|---|
| `list` | Paginated read | — | `status`, `decision`, `priority_min`, `since` (ISO datetime), `limit` (default 25, max 100), `offset` |
| `acknowledge` | open → acknowledged | `work_item_id` | `note` |
| `resolve` | → resolved (sets `resolved_at`) | `work_item_id`, `outcome` (closed vocab) | `note` |
| `ignore` | → ignored | `work_item_id`, `reason` (non-empty) | — |

`outcome` closed vocab: `acted` / `delegated_externally` / `no_action_needed`.

Tool surface lives in `core/services/td_handlers_rigby_work_queue.py`
(new mixin) and is registered on `ToolDispatcher` via
`RigbyWorkQueueReviewMixin`. Schema added to `PA_TOOL_SCHEMAS` in
`core/services/pa_tool_schemas.py`.

### 14.2 Lifecycle transitions

```
       ┌──────────┐                 ┌──────────────┐
       │   open   │   acknowledge   │ acknowledged │
       │ (default)│ ──────────────► │              │
       └────┬─────┘                 └──────┬───────┘
            │                              │
            │   resolve (outcome)          │   resolve (outcome)
            │   ────────────────►          │   ────────────────►
            │                              │
            │   ┌───────────┐              │
            └──►│ resolved  │◄─────────────┘
                │ (terminal)│
                └───────────┘
            │                              │
            │   ignore (reason)            │   ignore (reason)
            │   ───────────────►           │   ───────────────►
            │                              │
            │   ┌──────────┐               │
            └──►│  ignored │◄──────────────┘
                │(terminal)│
                └──────────┘
```

**Terminal states** (`resolved`, `ignored`) cannot transition further.
Attempting to acknowledge/resolve/ignore a terminal item returns a
clean error (`ok=False`) with no DB side effect.

**Idempotency** at each transition:
- `acknowledge` of already-`acknowledged` → no-op response (no new
  audit row).
- `resolve` of already-`resolved` → no-op response.
- `ignore` of already-`ignored` → no-op response.

### 14.3 MissionRun timeline audit (Option A)

**Every** state transition appends an `OpsRunEvent` row to the parent
`MissionRun` (i.e., `source_mission_run`). This is Option A from the
PR 7 design decision — the audit trail lives in the existing
MissionRun timeline; **no separate transition table**.

| Transition | OpsRunEvent label | `event_type` | `detail` keys |
|---|---|---|---|
| `* → acknowledged` | `work_item_acknowledged` | `info` | `work_item_id, from_status, to_status, note` |
| `* → resolved` | `work_item_resolved` | `step_pass` | `work_item_id, from_status, to_status, outcome, note` |
| `* → ignored` | `work_item_ignored` | `info` | `work_item_id, from_status, to_status, reason` |

This extends the MissionRun timeline established in §11.7 with three
new labels. Future PRs that add more transitions must keep these
labels stable.

To replay a full mission lineage:

```python
OpsRunEvent.objects.filter(run__mission_id=<mid>).order_by('created_at')
# → intake_started → impact_assessed → decision_made
#   → work_item_acknowledged → work_item_resolved
#   (or → work_item_ignored)
```

One MissionRun. One ordered timeline. From event arrival to outcome.

### 14.4 Feature flag behavior

`settings.RIGBY_WORK_QUEUE_REVIEW_ENABLED` (default `False`).
Environment-controlled via `RIGBY_WORK_QUEUE_REVIEW_ENABLED=true`.

| Setting | Behavior |
|---|---|
| `False` (default) | `rigby_work_item` schema **is still advertised** to the LLM. Handler returns a structured `{ok: False, error: 'tools disabled', flag: 'RIGBY_WORK_QUEUE_REVIEW_ENABLED'}` response. No DB writes. No transitions. No audit rows. |
| `True` | All four actions work end-to-end. Transitions write OpsRunEvent audit rows on the parent MissionRun. |

**Why advertise the schema even when off:** keeps `SCHEMA_VERSION`
stable across deploys (no cache invalidation on flip), and gives the
LLM a clear "disabled" signal instead of "unknown tool." Operators
get an explicit error message naming the flag.

This is the **third** feature flag in the intake pipeline:

| Flag | Default | Gates |
|---|---|---|
| `RIGBY_EVENT_INTAKE_ENABLED` (PR 5) | `False` | signal → enqueue intake |
| `RIGBY_INTERNAL_WORK_QUEUE_ENABLED` (PR 6) | `False` | actionable decision → RigbyWorkItem |
| `RIGBY_WORK_QUEUE_REVIEW_ENABLED` (PR 7) | `False` | PA tool actions on the queue |

All three must be on for the full chain (event → intake → work item →
Rigby review) to fire. Defaults compose to **net zero behavior change
in production**.

### 14.5 What is still out of scope

- **No human notification.** Rigby's PA chat surface remains the only
  consumer. No Discord / email / push / Workspace UI surfacing of
  work items.
- **No agent dispatch.** No `agent_router.route()` call from any work
  item transition.
- **No initiative creation.** No `Initiative.objects.create(...)`.
- **No automatic state transitions.** Rigby explicitly transitions
  items via the PA tools; nothing auto-acknowledges on a timer or
  auto-resolves on event recurrence.
- **No SLA / escalation tracking.** A work item can sit `open`
  forever; nothing nags Rigby or escalates to Chris.
- **No LLM-assisted decisioning.** Acknowledge / resolve / ignore are
  manual operator actions; no model picks the transition.
- **No frontend UI work.** Rigby uses her existing PA chat to call
  the tools; no Workspace tab / Cockpit panel added.
- **No new emitters.** Same set as PR 5 (DeliverableEvent →
  status_transition).
- **No `config_tool` runtime toggle.** Deploy-controlled flag only.

### 14.6 What lands in this PR

- `core/services/td_handlers_rigby_work_queue.py` — new mixin
  (~370 lines): `RigbyWorkQueueReviewMixin`, action dispatcher,
  per-action handlers, `_write_transition_event` helper, closed-vocab
  constants.
- `core/services/tool_dispatcher.py` — mixin added to
  `ToolDispatcher`'s base class tuple; handler registered as
  `rigby_work_item` (registry now 153 tools, up from 152).
- `core/services/pa_tool_schemas.py` — new schema entry for the
  `rigby_work_item` tool with action enum + parameters.
- `core/settings.py` — new `RIGBY_WORK_QUEUE_REVIEW_ENABLED`
  (default `False`).
- `core/tests/test_rigby_work_queue_review.py` — new test file
  (~430 lines, 30 tests covering flag-off, list pagination /
  filters / ordering, each transition action, idempotency,
  invalid-transition error paths, audit event shape, side-effect
  containment, schema registration sanity).
- This §14 added to `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/INDEX.md` regenerated via `python manage.py build_docs_index`.

**Test summary (real PostgreSQL test DB):**
- 30/30 PR 7 tests green in 0.14s.
- 149/149 across PR 2 + PR 3 + PR 4 + PR 5 + PR 6 + PR 7 green in 7.34s.
- Tool dispatcher registers 153 handlers (was 152).
- All earlier static guardrails still pass.

---

## 15. PR 8 — Rigby Mission Delegation

> Status: shipped in PR 8 of the Rigby Event Intake arc. Rigby
> becomes the operations layer: she delegates actionable work items
> to agents and observes completion via the existing
> `AgentExecution.post_save` signal. **No human notification. No
> direct agent dispatch outside existing infrastructure. No LLM.**
> Default OFF.

### 15.1 Delegation lifecycle (new in PR 8)

```
RigbyWorkItem(decision='monitor', status='open' or 'acknowledged')
   │
   ▼ Rigby invokes PA tool: rigby_work_item action='delegate'
   │
   ▼ delegate_work_item(work_item_id) — core/services/rigby_mission_delegation.py
   │
   ├── 1. Resolve work item + check flag (RIGBY_DELEGATION_ENABLED)
   ├── 2. Routing check: decision → agent (deterministic table)
   ├── 3. Re-delegation guard: reject if non-terminal AgentExecution exists
   ├── 4. Append OpsRunEvent:  label='delegation_started'
   │      detail={work_item_id, decision, routed_agent, task_preview}
   │
   └── 5. execute_agent_task.apply_async(args=[agent_name, task, context],
                                          queue='long_running')
          context['parent_object_type'] = 'RigbyWorkItem'
          context['parent_object_id']   = str(work_item.id)
          context['auto_followup']      = False

[Celery worker picks up execute_agent_task → _impl_execute_agent_task creates
 AgentExecution row with parent_object_type/parent_object_id from context]
   │
   ▼ AgentExecution.save(created=True)
   │
   ▼ post_save signal — core/signals/rigby_delegation_signals.py
   │   ├── Filter: parent_object_type == 'RigbyWorkItem' + flag ON
   │   └── Append OpsRunEvent: label='agent_assigned'
   │       detail={execution_id, agent_name, work_item_id, decision}
   │
   ▼ AgentRouter.route() runs the agent synchronously inside the task
   │
   ▼ AgentExecution.save(status='completed'|'failed'|'cancelled')
   │
   ▼ post_save signal fires again (idempotent — checks for prior
   │  agent_completed event before writing)
   │
   ├── Append OpsRunEvent: label='agent_completed'
   │      detail={execution_id, status, time_ms, tokens, cost, error?}
   │
   ├── Append OpsRunEvent: label='verification_started'
   │
   ├── Deterministic verification (no LLM):
   │     verdict = (
   │         'verified'              if status='completed' and ≥1 LLMCallEvent(SUCCESS)
   │         'failed_no_llm_calls'   if status='completed' but 0 LLMCallEvent
   │         'failed_agent_error'    if status in {failed, cancelled}
   │     )
   │     evidence = {llm_success_count, tool_call_success_count, ...}
   │
   ├── Append OpsRunEvent: label='verification_completed'
   │      detail={verdict, evidence}
   │
   └── Append OpsRunEvent: label='mission_closed'
          detail={verified, verdict, decided_via='delegation'}
```

The MissionRun timeline is the single authoritative record. After
PR 8, a fully-delegated mission reads:

```
intake_started → impact_assessed → decision_made
  → work_item_acknowledged (optional, from PR 7)
  → delegation_started → agent_assigned → agent_completed
  → verification_started → verification_completed → mission_closed
```

### 15.2 v0 routing table

Hardcoded in `core/services/rigby_mission_delegation.py`:

```python
DELEGATION_ROUTING = {
    "monitor": "TrendAnalysisAgent",
}
```

- `notify` decisions are **not delegatable** in v0. The PA tool
  returns `{ok: False, not_delegatable: True}` and the work item
  stays in Rigby's queue. Rationale: `notify` is about surfacing
  human-readable summaries; delegating doesn't help. Future PR can
  add `notify → ContentWriterAgent` if useful.
- Adding more decisions = edit the dict + tests. No LLM, no rule
  engine, no plugin registry.

### 15.3 Feature flag (the 4th in the pipeline)

`settings.RIGBY_DELEGATION_ENABLED` (default `False`). When OFF:

- `delegate` PA tool action returns
  `{ok: False, error: 'rigby delegation is disabled (flag off)', flag: 'RIGBY_DELEGATION_ENABLED'}`.
- The `post_save` lifecycle signal short-circuits — even if a
  delegated AgentExecution somehow exists, no lifecycle events get
  written.

Four-flag chain after PR 8:

| Flag | Default | Gates |
|---|---|---|
| `RIGBY_EVENT_INTAKE_ENABLED` (PR 5) | `False` | signal → enqueue intake task |
| `RIGBY_INTERNAL_WORK_QUEUE_ENABLED` (PR 6) | `False` | actionable decision → RigbyWorkItem |
| `RIGBY_WORK_QUEUE_REVIEW_ENABLED` (PR 7) | `False` | PA tool actions on the queue |
| `RIGBY_DELEGATION_ENABLED` (PR 8) | `False` | `delegate` action + post_save lifecycle |

Net behavior with all four OFF (production default): zero functional
change vs. PR 4 close.

### 15.4 Re-delegation policy

```python
NON_TERMINAL_STATUSES = {"pending", "in_progress"}

active = AgentExecution.objects.filter(
    parent_object_type="RigbyWorkItem",
    parent_object_id=work_item.id,
    status__in=NON_TERMINAL_STATUSES,
).first()
if active is not None:
    return {ok: False, error: "non-terminal execution exists"}
```

- **Active delegation blocks re-delegation.** Rigby must wait for the
  prior execution to reach a terminal state.
- **`failed` / `cancelled` permit explicit re-delegation.** A fresh
  call to `delegate` after a failure spawns a new AgentExecution row;
  the old one stays in the timeline as the failed attempt.
- **`completed` is NOT in the guard set.** A second `delegate` after
  success technically creates another execution. v0 documents this
  but doesn't block it — the assumption is that Rigby's queue UI
  closes the work item after a successful verification, so duplicate
  delegations are an operator choice. v1 may tighten this if
  operationally needed.
- **No automatic retries.** PR 8 spec rule. Each delegation is an
  explicit Rigby action.

### 15.5 MissionRun timeline events (PR 8 additions)

PR 8 adds six new stable labels on the parent MissionRun's
`OpsRunEvent` stream. Future PRs must keep these stable.

| Label | Event type | When written | Idempotency key |
|---|---|---|---|
| `delegation_started` | `info` | At `delegate_work_item` dispatch time (in service) | none — multiple delegations create multiple events |
| `agent_assigned` | `info` | On `AgentExecution.created=True` with `parent_object_type='RigbyWorkItem'` | `detail.execution_id` |
| `agent_completed` | `step_pass` / `step_fail` | On terminal save (`completed` / `failed` / `cancelled`) | `detail.execution_id` |
| `verification_started` | `info` | Immediately after `agent_completed` | written together with `agent_completed` (gated by same idempotency check) |
| `verification_completed` | `step_pass` / `step_fail` | After deterministic verification | same |
| `mission_closed` | `step_pass` / `info` | Final lifecycle event | same |

Idempotency: the signal handler queries
`OpsRunEvent.objects.filter(run=mission_run, label='agent_completed', detail__execution_id=str(execution.id)).exists()`
before writing the terminal-lifecycle block. The signal can fire
multiple times for the same AgentExecution (e.g., `update_fields`
saves); only the first terminal save writes the lifecycle.

### 15.6 Deterministic verification

The verification step uses **only** structured telemetry rows already
populated by the existing platform:

```python
def _verify_execution(execution) -> (verdict, evidence):
    if execution.status != "completed":
        return "failed_agent_error", {execution_status, error_message?}
    llm_ok = LLMCallEvent.objects.filter(
        execution_id=execution.id, status="SUCCESS"
    ).count()
    if llm_ok == 0:
        return "failed_no_llm_calls", {execution_status, llm_success_count: 0}
    tool_ok = ToolCallRecord.objects.filter(
        trace_id=execution.trace_id, success=True
    ).count() if execution.trace_id else 0
    return "verified", {execution_status, llm_success_count, tool_call_success_count}
```

**No LLM-as-judge.** No external API. No human-in-the-loop. Verdict
is fully deterministic from existing rows. `failed_no_llm_calls`
catches the "agent returned `completed` but did no real work" case
(would-be silent success).

`MissionRun.status` is **not touched** by verification. It stays at
whatever the intake task set (typically `passed`). The verdict lives
in the `mission_closed` event's `detail.verdict`. This honors §10.1:
the timeline is the audit trail, not the parent row's status field.

### 15.7 Tool surface

The existing `rigby_work_item` PA tool gains a 5th action:

| Action | Required | Optional |
|---|---|---|
| `delegate` | `work_item_id` | — |

The handler is a thin wrapper around
`delegate_work_item(work_item_id)`. No additional knobs — Rigby
doesn't pick the agent; the routing table decides.

### 15.8 What changes outside the new modules

| Touch | Change | Reason |
|---|---|---|
| `core/tasks_agents.py` `_impl_execute_agent_task` | +2 lines: read `parent_object_type` / `parent_object_id` from context, plumb into `_create_kwargs` | The sync `route()` path already honors these (via `_create_execution_record`); this brings the async wrapper to parity. Backward-compatible — empty/None when callers don't set them. |
| `core/apps.py:ready()` | +1 try/except block calling `connect_rigby_delegation_signals()` | Standard pattern (matches PR 5's deliverable_status_signals registration). |
| `core/signals/__init__.py` | re-export `on_delegation_lifecycle` + `connect_rigby_delegation_signals` | Standard pattern. |

### 15.9 What is still out of scope

- **No human notification.** Rigby's PA chat remains the only consumer.
- **No new model.** Linkage via existing
  `AgentExecution.parent_object_type` + `parent_object_id` (Session
  843 fields).
- **No new migration.**
- **No UI.** Frontend exposure is a separate PR.
- **No `agent_router.route()` bypass.** All execution goes through the
  existing async wrapper (`execute_agent_task` Celery task), which
  itself calls `route()` inside the worker.
- **No automatic retries.** Each delegation is an explicit Rigby
  action.
- **No automatic planning / multi-agent orchestration.** One work item,
  one delegated agent, one completion.
- **No LLM in routing or verification.** Both are deterministic.
- **No new EventBus / signal framework.** Reuse Django `post_save` on
  the existing `AgentExecution` model.
- **No config_tool runtime toggle.** Deploy-controlled.
- **No `MissionRun.status` mutation.** The mission's final verdict
  lives in the `mission_closed` event's `detail`, not the parent
  row's status.

### 15.10 What lands in this PR

- `core/services/rigby_mission_delegation.py` — new module (~250
  lines): routing table, `delegate_work_item()` service, helpers,
  closed-vocab constants.
- `core/signals/rigby_delegation_signals.py` — new module (~210
  lines): single `post_save` receiver, `_verify_execution`,
  six lifecycle-label constants.
- `core/signals/__init__.py` — re-export the new signal hooks.
- `core/apps.py` — register the new signal via `ready()`.
- `core/services/td_handlers_rigby_work_queue.py` — new
  `_rigby_work_item_delegate` method (~25 lines), wired into the
  action dispatcher.
- `core/services/pa_tool_schemas.py` — extend `rigby_work_item`
  action enum + description.
- `core/services/rigby_mission_delegation.py` import side: pulls
  `execute_agent_task` from `core.tasks` (not `core.tasks_agents`)
  per the Celery registration site.
- `core/tasks_agents.py` `_impl_execute_agent_task` — additive
  context plumbing for `parent_object_type` / `parent_object_id`.
- `core/settings.py` — `RIGBY_DELEGATION_ENABLED` flag (default
  `False`).
- `core/tests/test_rigby_mission_delegation.py` — new test file
  (~500 lines, 25 tests).
- This §15 added to `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/INDEX.md` regenerated via `python manage.py build_docs_index`.

**Test summary (real PostgreSQL test DB):**
- 25/25 PR 8 tests green in 0.58s.
- 174/174 across PR 2 + PR 3 + PR 4 + PR 5 + PR 6 + PR 7 + PR 8
  green in 7.76s.
- All earlier static guardrails still pass.

---

## 16. PR 9 — Local intake observation harness

> Status: shipped in PR 9 of the Rigby Event Intake arc. **Two new
> management commands. No new model. No new code paths that fire the
> pipeline.** This PR adds observability so we can safely enable the
> first stage locally before any downstream side-effect flag flips.

### 16.1 Local-only rollout shape

Per the PR 9 directive, only one flag is flipped, and only locally:

| Flag | Status after PR 9 | How to enable |
|---|---|---|
| `RIGBY_EVENT_INTAKE_ENABLED` | local: **ON** (operator choice); production: **OFF** | `export RIGBY_EVENT_INTAKE_ENABLED=true` in your shell or `.env.local` |
| `RIGBY_INTERNAL_WORK_QUEUE_ENABLED` | **OFF** everywhere | (deferred to later PR) |
| `RIGBY_WORK_QUEUE_REVIEW_ENABLED` | **OFF** everywhere | (deferred to later PR) |
| `RIGBY_DELEGATION_ENABLED` | **OFF** everywhere | (deferred to later PR) |

Net behavior with `RIGBY_EVENT_INTAKE_ENABLED=true` locally + others
OFF:
- Every Deliverable status_transition triggers the intake task on
  the `pa` queue.
- The intake task writes a MissionRun (OpsRun, domain='mission',
  run_kind='intake') with the three lifecycle OpsRunEvents
  (`intake_started`, `impact_assessed`, `decision_made`).
- **No RigbyWorkItem rows are created** (PR 6 flag off).
- **No PA tool review surface for queues** (PR 7 flag off).
- **No agent delegation** (PR 8 flag off).
- **No notifications. No agent dispatch. No external HTTP calls.**

The intake task is millisecond-scale and side-effect-bounded —
exactly what we want to observe in isolation.

**Production defaults are untouched.** PR 9 changes no settings;
`os.environ.get('RIGBY_EVENT_INTAKE_ENABLED', 'false')` still
evaluates to `False` in production.

### 16.2 `rigby_intake_status` — recent runs + aggregates

Read-only. Reports on recent intake MissionRuns and gives a
flag-state snapshot at the top of the output.

```
python manage.py rigby_intake_status
python manage.py rigby_intake_status --limit 20
python manage.py rigby_intake_status --json
```

Sample human output (against an empty local DB):

```
Rigby Intake Status
  generated: 2026-06-28T19:36:52.877804+00:00

Flags:
  [off]  RIGBY_EVENT_INTAKE_ENABLED
  [off]  RIGBY_INTERNAL_WORK_QUEUE_ENABLED
  [off]  RIGBY_WORK_QUEUE_REVIEW_ENABLED
  [off]  RIGBY_DELEGATION_ENABLED

Totals:
  all-time intake runs : 0
  last 24h             : 0
  last 7d              : 0
  currently running    : 0

Decision breakdown (7d):
  (no decisions in window)

Recent intake runs (latest 0):
  (no rows)
```

JSON output shape:

```json
{
  "generated_at": "...",
  "flags": {
    "RIGBY_EVENT_INTAKE_ENABLED": false,
    "RIGBY_INTERNAL_WORK_QUEUE_ENABLED": false,
    "RIGBY_WORK_QUEUE_REVIEW_ENABLED": false,
    "RIGBY_DELEGATION_ENABLED": false
  },
  "totals": {
    "all_time": 0, "last_24h": 0, "last_7d": 0, "running_count": 0
  },
  "decision_breakdown_7d": {"ignore": 12, "monitor": 3, "notify": 1},
  "recent": [
    {
      "mission_run_id": "...", "started_at": "...", "finished_at": "...",
      "status": "passed", "source_event_ref": "deliverable_event:...",
      "decision": "ignore", "mission_impact": "unknown",
      "timeline_event_count": 3, "has_work_item": false,
      "mission_id": "..."
    }
  ]
}
```

### 16.3 `rigby_intake_lag_check` — stuck-running detector

Read-only. Flags any intake MissionRun in `status='running'` past
the threshold. **Report only — no notifications, no
WorkspaceOperation, no remediation.**

```
python manage.py rigby_intake_lag_check
python manage.py rigby_intake_lag_check --threshold 10
python manage.py rigby_intake_lag_check --json
```

Sample human output (clean state):

```
Rigby Intake Lag Check — OK (threshold 5m)
  generated: 2026-06-28T19:36:58.296008+00:00
  No stuck intake MissionRuns.
```

Sample human output (one stuck run):

```
Rigby Intake Lag Check — 1 stuck (threshold 5m)
  generated: 2026-06-28T19:40:00+00:00

  c25e3a7d3ec5.. age=11.4m started_at=2026-06-28T19:28:36+00:00 event_ref=deliverable_event:abc...
```

The 5-minute default is a heuristic: the intake task is
millisecond-scale; anything in `running` past that is almost
certainly a crashed worker, a stuck dispatch, or a manual
intervention. The threshold is operator-tunable.

### 16.4 What healthy looks like

After flipping `RIGBY_EVENT_INTAKE_ENABLED=true` locally and
exercising a Deliverable status_transition (e.g., changing a
deliverable's status via the admin or PA tool), running
`rigby_intake_status` should show:

- `Flags: [ON]  RIGBY_EVENT_INTAKE_ENABLED` (and `[off]` for the
  other three).
- `Totals.last_24h` increases by 1 per status transition observed.
- `Totals.running_count == 0` (the intake task finishes
  millisecond-scale).
- `Decision breakdown` populated with one of `ignore` / `monitor` /
  `notify` based on the direction of the transition.
- Each recent row has `timeline_event_count == 3`
  (intake_started + impact_assessed + decision_made).
- `has_work_item: false` (PR 6 flag is off).

`rigby_intake_lag_check` should consistently report
`OK (threshold 5m) / No stuck intake MissionRuns`.

If either command reports anomalies (running_count > 0 for >5min, or
the lag check finds a stuck run, or decision_breakdown shows
unexpected values), that's the signal to investigate **before**
flipping any of the PR 6/7/8 flags.

### 16.5 What is still out of scope

- No production flag flip — only local enablement.
- No PR 6/7/8 flag flips — those stay default OFF.
- No human notifications surfaced by either command (Discord /
  email / push / WorkspaceOperation / chat).
- No remediation of stuck runs (no kill / restart / requeue).
- No new emitters.
- No UI / Workspace surface for the status report.
- No automatic alerting / Beat-scheduled lag check (commands are
  on-demand only).

### 16.6 What lands in this PR

- `core/management/commands/rigby_intake_status.py` — new command
  (~170 lines).
- `core/management/commands/rigby_intake_lag_check.py` — new
  command (~105 lines).
- `core/tests/test_rigby_intake_observation.py` — new test file
  (~360 lines, 25 tests covering source-default invariants,
  status-shape, aggregates, decision breakdown, work-item presence,
  lag detection / threshold semantics, read-only behavior, no
  downstream side effects).
- This §16 added to `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/INDEX.md` regenerated via `python manage.py build_docs_index`.

**No model changes. No migrations. No settings changes
(production defaults preserved). No new emitters. No new flags.**

**Test summary (real PostgreSQL test DB):**
- 25/25 PR 9 tests green in 0.15s.
- 199/199 across PR 2 + PR 3 + PR 4 + PR 5 + PR 6 + PR 7 + PR 8 +
  PR 9 green in 7.73s.
- All earlier static guardrails still pass.

---

## 17. PR 10 — Local intake exercise & observation write-up

> Status: docs-only PR. Operator validation against the live local
> DB. Full handoff at
> [`docs/handoffs/SESSION_1250_PR10_LOCAL_INTAKE_EXERCISE.md`](handoffs/SESSION_1250_PR10_LOCAL_INTAKE_EXERCISE.md).

### 17.1 What we did

Locally flipped `RIGBY_EVENT_INTAKE_ENABLED=true`, kept the other
three flags OFF, restarted the `pa` Celery worker with the env var
set, then triggered three Deliverable status transitions:

1. **forward** (`draft → ready`) — expected `decision='ignore'`.
2. **backward** (`ready → draft`) — expected `decision='monitor'`.
3. **terminal** (`draft → archived`) — expected `decision='notify'`.

### 17.2 What happened

All three transitions produced exactly the expected behavior:

| Transition | Decision | Mission impact | Timeline events | Work item created |
|---|---|---|---|---|
| forward | `ignore` | `unknown` | 3 (`intake_started`/`impact_assessed`/`decision_made`) | no (queue flag off) |
| backward | `monitor` | `low` | 3 | no (queue flag off) |
| terminal | `notify` | `medium` | 3 | no (queue flag off) |

All three MissionRuns reached `status='passed'` in ~6ms each. The lag
check reported `OK / No stuck intake MissionRuns`. Zero RigbyWorkItem
rows and zero `AgentExecution` rows linked to delegation were created
— every Stage 2/3/4 gate held closed.

### 17.3 Operator gotcha (documented for future operators)

`settings.RIGBY_EVENT_INTAKE_ENABLED` is checked **in the
signal-emitting process** (the Django shell / runserver / whichever
worker saves the Deliverable), not in the `pa` worker that runs the
intake task. Setting the env var only on the worker is insufficient
— the gate short-circuits in the calling process and `apply_async`
never fires.

Correct pattern: ensure the env var is visible to **both** the
process saving the Deliverable AND the `pa` worker. For ad-hoc shell
work:

```bash
RIGBY_EVENT_INTAKE_ENABLED=true .venv/bin/python manage.py shell
```

For long-running services, set it in the same env block as the
worker (`make celery` should pick it up if exported in the shell
that invokes make).

### 17.4 Stage 1 verdict + next stage

**Stage 1 (intake) is safe to proceed.** All three rule branches
fire correctly. All side-effect gates held closed. The lag check
correctly reports clean.

**Next stage (PR 11):** flip `RIGBY_INTERNAL_WORK_QUEUE_ENABLED=true`
locally, keep the other two flags OFF, re-exercise with the same
three transitions. Expected: backward → 1 RigbyWorkItem with
`decision='monitor'`, `priority=3`; terminal → 1 RigbyWorkItem with
`decision='notify'`, `priority=5`; forward → no work item.

If PR 11 looks clean, PR 12 flips `RIGBY_WORK_QUEUE_REVIEW_ENABLED`
and exercises the PA tool review surface. PR 13+ flips
`RIGBY_DELEGATION_ENABLED` and exercises delegation. Production
flips remain deferred until local observation is complete for each
stage.

### 17.5 What lands in this PR

Documentation only — no code, no settings, no flag flips persisted.

- `docs/handoffs/SESSION_1250_PR10_LOCAL_INTAKE_EXERCISE.md` —
  full handoff with command outputs, expected-vs-actual table,
  three anomalies surfaced (operator gotcha; pre-existing cascade
  drift; status-snapshot semantics), cleanup state, and the PR 11
  recommendation.
- This §17 — short summary + link.
- `docs/INDEX.md` — regenerated.

Production defaults for all four Rigby flags remain `False`. The
exercise was local-only and operator-driven.

---

*This is a discovery snapshot. The runtime inventory in
`PLATFORM_INVENTORY.md` remains the authoritative source for any
quantitative count; if this doc and the inventory disagree on a
number, the inventory wins per `DOC_LIFECYCLE.md` §2c.*
