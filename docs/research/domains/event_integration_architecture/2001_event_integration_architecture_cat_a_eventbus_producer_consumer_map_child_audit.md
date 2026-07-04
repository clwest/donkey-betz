---
title: "Group 2000+ — Cat A — EventBus Producer/Consumer Map + Contract Verification (S2001 P1)"
status: draft
session: 2001
child_slot: P1_cat_a
domain_slug: event_integration_architecture
research_group: 2000
mission_type: child_audit
date: 2026-07-04
authority: |
  P1 child audit under Group 2000+ Event / Integration Architecture arc.
  Scope inherited from parent scoping §5.1
  (`2000_event_integration_architecture_domain_scoping.md`), which itself
  consumes S1273 §3.31 (EventBus inventory), S1274 §12.1 (P0
  producer/consumer map audit), and S2000 SIGN cycle 1 Q4 fold
  (α/β/γ/δ contract-verification 4-deliverable expansion).

  This doc is RESEARCH AUDIT only. It enumerates the current EventBus
  producer/consumer topology at commit-time HEAD, classifies each
  stream × direction pair per S1274 §11 4-tier strength (STRONG /
  WEAK / MISSING / OVERCOUPLED — with UNKNOWN forbidden per Rigby
  S2001 SIGN emphasis #1), and documents the current-state contract
  verification surfaces (schema shape, runtime asserts, version gate,
  replay).

  Explicit non-scope, per playbook §14.5 no-implementation rule:
  - Does NOT design HAI event schema (that IS P2 / S2002).
  - Does NOT pick schema-versioning go-forward policy (that IS P2).
  - Does NOT design cross-substrate composition rules (that IS P3 /
    S2003).
  - Does NOT ship migrations, ORM changes, EventBus wrapper changes,
    beat-schedule enrollment, or DLQ cleanup implementation.
  - Does NOT re-open S1273 §3.31 EventBus inventory scope or S1274
    §12.1 P0 producer/consumer map audit scope; consumes both as
    prior work.
  - Does NOT design the per-user authority MECHANISM (P2 preamble
    guardrail per parent §5.2 and §7.2, Rigby S2000 SIGN cycle 1 Q1
    fold).

  Load-bearing inheritance chain re-attested at S2001 open:
  - S1273 §3.31 EventBus inventory (8 streams + 1 DLQ + 3 consumer
    groups + 6 publisher wrappers + 4 Celery consumer tasks).
  - S1274 §12.1 P0 producer/consumer registry style (STRONG / WEAK /
    MISSING classification; UNKNOWN allowed there as flagged
    non-verified).
  - S1274 v2 Rigby SIGN fold (EventBus mis-classified as "dormant"
    → upgrade WEAK not MISSING when partial adoption is verified).
  - S1275 event schema precedent (per-event `schema_version` field
    with graduation contract) — γ policy audit current state; P2
    designs go-forward.
  - S1806 §7.4 + §10 six-plane learning-surface event-emission gap
    durable-at-six catalog — not restated here; consumed by P2.
  - S1899 §8.1 T0/Gate item 6 R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES
    — parked for P2; P1 documents current state only.
  - S1401 §10.2 T9 `EventStream.OPPORTUNITY_CREATED` dormancy finding
    — verified here as F2.
companion_docs:
  - docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md
  - docs/research/symbol_mapping_event_schema_design.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/EVENT_SYSTEM_INVENTORY.md
verifier_loop: |
  Pre-Explore (playbook §14 MC-1 REQUIRED, CODIFICATION-CONFIRMED at
  S1899 close). Direct file:line reads before any sub-agent dispatch:

  (a) `EventStream` enum at `core/services/event_bus.py:21-30` —
      verified 8 stream values (SPIDER_DATA + OPPORTUNITY_CREATED +
      OPPORTUNITY_SCORED + VALIDATION_REQUIRED + VALIDATION_DECIDED
      + OUTCOME_RECORDED + MODEL_TRAINED + SYSTEM_ALERT). DLQ
      constant `DEAD_LETTER_STREAM = "mi:dead_letter"` at line 106.
  (b) 7 publisher wrappers at `event_bus.py:539` (spider_data), 559
      (opportunity_scored), 596 (validation_required), 619
      (validation_decided), 643 (outcome_recorded), 665
      (model_trained), 686 (system_alert). **No wrapper exists for
      OPPORTUNITY_CREATED** — confirmed via `def publish_` grep.
  (c) Publisher call-site sweep via `Grep(publish_[a-z_]+_event)`
      across all `**/*.py`. Matching non-definition sites: 3 files —
      `core/services/scoring_dispatcher.py` (1 wrapper + 2 call
      sites at :282, :480), `core/services/hitl_validation.py` (2
      wrappers imported + 2 call sites at :30, :38),
      `core/services/event_bus.py` (definitions only).
      **Zero callers** for `publish_spider_data_event`,
      `publish_outcome_recorded_event`, `publish_model_trained_event`,
      `publish_system_alert_event`.
  (d) Direct `bus.publish(...)` / `get_event_bus().publish(...)`
      grep — 7 hits, all inside the wrapper bodies at
      `event_bus.py:547,580,605,629,652,673,703`. **Zero direct
      publisher call sites bypass the wrappers.**
  (e) Consumer workers at `core/services/event_handlers.py:521`
      (`create_scoring_worker` → SPIDER_DATA + OPPORTUNITY_CREATED),
      :531 (`create_validation_worker` → OPPORTUNITY_SCORED +
      VALIDATION_REQUIRED), :541 (`create_analytics_worker` →
      VALIDATION_DECIDED + OUTCOME_RECORDED + MODEL_TRAINED). All
      three use `block_ms=0` non-blocking (Session 1075). **No
      worker subscribes to `EventStream.SYSTEM_ALERT`.**
  (f) Celery consumer tasks at `core/tasks.py:4726`
      (process_event_bus_scoring_queue), 4760 (validation), 4794
      (analytics), 4828 (claim_stale_events), 4874
      (get_event_bus_stats). All 5 are `@shared_task` defined; task
      routing at `core/settings.py:1315-1317,1579` (all → `broadcast`
      queue).
  (g) `PeriodicTask` ORM probe (2026-07-04, local DB): **only
      `claim-stale-events` is enrolled and enabled**
      (`core.tasks.claim_stale_events`, last_run_at ~5min ago). Zero
      PeriodicTask rows for the other 4 consumer tasks. Verified via
      `PeriodicTask.objects.filter(task__endswith='<task>').values_list(...)`.
  (h) Beat schedule at `core/celery.py:532` also confirms only
      `claim-stale-events` scheduled in the code-defined
      `beat_schedule` dict. No other event_bus task appears in the
      code-defined schedule.
  (i) DLQ emission code path: `_move_to_dead_letter` at
      `event_bus.py:451-477`, called only from `consume` at line 275
      (parse-error path). `xadd` with `maxlen=1000` at line 468-471.
      **Not called on handler failure** — verified by reading
      `EventConsumerWorker.process_batch` at
      `event_handlers.py:415-475`: on handler error the code paths
      to `events_failed += 1` at line 458 and appends error but does
      NOT ACK and does NOT move to DLQ.
  (j) DLQ consumer sweep: grep for `xrange.*dead_letter` /
      `xreadgroup.*dead_letter` / `DEAD_LETTER_STREAM` — only
      `get_event_bus_stats` reads `xlen(DEAD_LETTER_STREAM)` at
      `event_bus.py:528`. **No consumer reads DLQ contents.**
  (k) `schema_version` grep across `event_bus.py` — 0 matches. All
      publisher wrappers assemble Event.data payloads without a
      `schema_version` field. γ current state: no versioning.
  (l) Runtime assert grep (`assert.*event\.data|assert data\.get`)
      across `core/` — 1 match in a test file only. **Zero runtime
      asserts on payload shape in production consumer code.**
  (m) Second AND third spider-agent substrates: verified via Rigby
      SIGN cycle 1 Q3 fold. **Two classes named `SpiderAgentConnector`
      exist** in parallel: (i) `ai_core/agents/spider_agent_connector.py:40`
      whose `publish_spider_data` at :311 uses raw
      `redis.publish(channel, json)` on `self.channels['spider_data']`
      — real callers: `ai_core/agents/concrete_executor.py:637-638`
      (imports singleton + assigns to `self.spider_connector`),
      `core/views_agent_intelligence.py:352,355` (reads
      `routing_table`); (ii) `intelligence/spider_agent_connector.py:20`
      whose `_build_routing_map` at :31 uses an in-process
      `Dict[str, List[str]]` category → agent-keyword mapping (NO
      pub/sub, NO Redis) — real callers: `core/tasks_spiders.py:260,307`,
      `core/tasks.py:1355,1359`, `core/management/commands/process_spider_data.py:6,16`,
      `core/management/commands/activate_spiders.py:10,234`.
      **THREE substrates for "spider data → agents": EventBus
      (dormant), ai_core pub/sub (2 callers), intelligence in-process
      routing (4 caller sites).** Cross-referenced with P3
      (Cross-Substrate Composition Design) — recorded as F11 for P3
      inheritance.
  (n) Prior contradiction cross-check: S1273 §3.31 classified
      `publish_model_trained_event` as UNKNOWN. Direct read confirms
      wrapper exists at `event_bus.py:665`. **Caller sweep finds zero
      callers.** Verdict corrected in F7: UNKNOWN → MISSING (dead
      code — wrapper defined but never invoked). Rigby SIGN cycle 1
      Q2 fold verified via `train_ml_scoring_model` grep: the real
      ML retrain path is `_impl_train_ml_scoring_model` at
      `core/tasks_financial.py:32-201`, called from Celery task
      `train_ml_scoring_model` at `core/tasks.py:2221-2223` and
      auto-invoked by `_impl_evaluate_ml_model_performance` at
      `core/tasks_financial.py:277` on drift detection. The retrain
      body writes `MLModelVersion.objects.create(...)` at
      `core/tasks_financial.py:157-168` with all the fields the
      MODEL_TRAINED wrapper would want (`version`,
      `training_samples`, `train_r2`/`test_r2`,
      `feature_importance`) but **never calls
      `publish_model_trained_event`**. F7 verdict strengthened:
      MODEL_TRAINED is not just "wrapper without caller" — it is
      "wrapper without caller AND the code path that should call it
      instead writes to `MLModelVersion` ORM directly bypassing
      EventBus".

  Sub-agent dispatches: NONE. All findings sourced from direct
  file:line reads + ORM probes. Per playbook §14 Pre-Explore
  discipline: parent Claude verifier-loop is sufficient for producer/
  consumer registry work when the surface fits in ~2k lines of
  primary code (event_bus.py ~730 + event_handlers.py ~550 + relevant
  tasks.py + settings.py rows).

  Zero-UNKNOWN attestation (Rigby S2001 SIGN emphasis #1): every one
  of the 8 streams + 1 DLQ has a producer classification AND a
  consumer classification in §10.2. Where evidence supports only
  WEAK/MISSING (not STRONG), the classification is downgraded — not
  parked as UNKNOWN.

  Evidence-backed attestation (Rigby S2001 SIGN emphasis #2): every
  producer classification cites publisher wrapper file:line + caller
  file:line (or explicit "zero callers grep"). Every consumer
  classification cites worker file:line + Celery task file:line +
  PeriodicTask enrollment status.
---

# Session 2001 — Group 2000+ Cat A — EventBus Producer/Consumer Map + Contract Verification

## 1. Executive Summary

The EventBus (`core/services/event_bus.py:90:EventBus`) is a Redis
Streams pub/sub substrate declaring **8 named streams + 1 DLQ + 3
consumer groups** that was designed as the central asynchronous
integration surface for the Market Intelligence Platform (Session
470). This P1 audit executes the S1274 §12.1 P0 producer/consumer map
against commit-time HEAD and reaches three headline findings.

**Headline 1 — Producer adoption is thin and asymmetric.** Only 3 of
the 8 streams have any producer call site outside `event_bus.py`
itself: `OPPORTUNITY_SCORED` (2 sites in `scoring_dispatcher.py`),
`VALIDATION_REQUIRED` (1 site in `hitl_validation.py`), and
`VALIDATION_DECIDED` (1 site in `hitl_validation.py`). The remaining
5 streams (`SPIDER_DATA`, `OPPORTUNITY_CREATED`, `OUTCOME_RECORDED`,
`MODEL_TRAINED`, `SYSTEM_ALERT`) have **zero non-definition producer
callers**. `OPPORTUNITY_CREATED` has no publisher wrapper at all
(only a stream constant + a dormant consumer subscription).

**Headline 2 — The entire consumer runtime is dormant on beat.** 3 of
the 5 EventBus-consumer Celery tasks
(`process_event_bus_scoring_queue`, `process_event_bus_validation_queue`,
`process_event_bus_analytics_queue`), plus the stats monitor
(`get_event_bus_stats`), are **defined + queue-routed but not
enrolled in `PeriodicTask`**. Only `claim_stale_events` runs on beat.
Because `claim_stale_events` can only reclaim events that a fresh
consumer already delivered to itself and failed to acknowledge, the
absence of the primary consumers means events accumulate in Redis
Streams until they hit `STREAM_MAX_LEN=10000` and are silently
truncated (F9). The 3 real producers (`scoring_dispatcher.py` and
`hitl_validation.py`) publish into streams that nothing reads at
runtime.

**Headline 3 — Contract-verification surfaces are largely absent.**
None of the 7 publisher wrappers stamps a `schema_version` field (γ
current state: no versioning; adopting S1275 precedent would be a
green-field addition, not a migration). No consumer asserts payload
shape at runtime — every handler uses `data.get(key, default)` and
would silently accept a schema-breaking change (β current state:
zero runtime asserts). The `replay()` method exists at
`event_bus.py:311` but has zero callers (δ current state: replay
surface available, zero regression tests use it). DLQ (`mi:dead_letter`)
is bounded (MAXLEN=1000) and only fed by parse errors — handler
failures do NOT reach DLQ, they retry-loop forever via
`claim_stale_events` reclaim (F14, F15).

**Corrections to prior research.** S1273 §3.31 classified
`publish_model_trained_event` as UNKNOWN; this audit finds the
wrapper defined at `event_bus.py:665` with zero callers → MISSING
(F7). S1274 §6.2 characterized DLQ as accumulating unbounded; this
audit confirms `xadd(..., maxlen=1000)` at line 468-471 caps DLQ at
1000 entries — the real DLQ risk is not unboundedness but silent
handler-failure invisibility (F15). The `cross_domain_integration_audit.md`
row for `OPPORTUNITY_SCORED` classified as WEAK with a caller cite of
`scoring_dispatcher.py:21-40,282,480` — verified: the wrapper
`_publish_scoring_event` at :21-56 is called from :282 (realtime) and
:480 (batch). Since consumer beat is dormant, the pair is still WEAK
(producer STRONG × consumer DORMANT → resolved to WEAK). See §10.2.

**What P1 hands to P2.** A completed 8-stream + 1-DLQ producer/consumer
map with zero UNKNOWNs, α/β/γ/δ per-stream tables enumerating current
schema shape / runtime asserts / version-gate posture / replay
feasibility, and 18 findings (F1–F18) covering dead-code, missing
connections, drift, boundary violations, and technical debt. P2
inherits the α column as the baseline against which HAI event schema
design will be drafted; γ current state (no versioning) as the
policy-decision surface P2 must resolve; F14/F15 handler-failure
loop as a technical-debt item that constrains any HAI event contract
that expects at-least-once semantics.

## 2. Domain Purpose

**Q1 (What does this domain do?):** EventBus provides asynchronous,
durable, at-least-once pub/sub messaging between decoupled producer
and consumer subsystems using Redis Streams. It defines a fixed
catalog of 8 event stream types (`EventStream` enum) covering the
market-intelligence lifecycle: raw data ingestion (SPIDER_DATA),
opportunity creation (OPPORTUNITY_CREATED), scoring (OPPORTUNITY_SCORED),
human-in-the-loop validation (VALIDATION_REQUIRED / VALIDATION_DECIDED),
outcome tracking (OUTCOME_RECORDED), model retraining
(MODEL_TRAINED), and out-of-band alerts (SYSTEM_ALERT). It ships
consumer groups (`scoring_workers`, `validation_workers`,
`analytics_workers`), a bounded DLQ (`mi:dead_letter`, MAXLEN=1000),
replay-from-Redis-Streams for debugging, and stale-event reclaim.

**Q2 (Why does it exist?):** Session 470 introduced the substrate as
Phase 4 of the Market Intelligence Architecture to decouple spider →
opportunity → scoring → validation → outcome flows so that (a)
producers do not synchronously wait on consumer completion, (b)
consumer failures do not lose events, and (c) analytics and ML
retraining can subscribe to lifecycle transitions without coupling
back to producers. The design intent is a canonical event contract
per lifecycle transition; the current runtime falls significantly
short of that intent (see F1–F18).

## 3. Canonical Entry Points

Producer entry points (publisher wrappers):

| Wrapper | Line | Stream | Documented purpose |
|---|---|---|---|
| `publish_spider_data_event(spider_name, spider_data_id, record_count, source)` | `event_bus.py:539` | `SPIDER_DATA` (`"mi:spider_data"`) | New spider data collected |
| `publish_opportunity_scored_event(opportunity_id, spider_data_id, ml_score, rule_score, hybrid_score, confidence, source)` | `event_bus.py:559` | `OPPORTUNITY_SCORED` (`"mi:opportunity_scored"`) | Opportunity scored |
| `publish_validation_required_event(validation_request_id, opportunity_id, confidence, priority, source)` | `event_bus.py:596` | `VALIDATION_REQUIRED` (`"mi:validation_required"`) | Needs human review |
| `publish_validation_decided_event(validation_request_id, opportunity_id, decision, decided_by, override_score, source)` | `event_bus.py:619` | `VALIDATION_DECIDED` (`"mi:validation_decided"`) | Human decision made |
| `publish_outcome_recorded_event(opportunity_id, outcome_type, outcome_value, actual_revenue, source)` | `event_bus.py:643` | `OUTCOME_RECORDED` (`"mi:outcome_recorded"`) | Actual outcome tracked |
| `publish_model_trained_event(model_version, training_samples, metrics, source)` | `event_bus.py:665` | `MODEL_TRAINED` (`"mi:model_trained"`) | ML model retrained |
| `publish_system_alert_event(alert_type, message, severity, details, source)` | `event_bus.py:686` | `SYSTEM_ALERT` (`"mi:system_alert"`) | System alerts |
| **(no wrapper)** | — | `OPPORTUNITY_CREATED` (`"mi:opportunity_created"`) | New opportunity created — never given a publisher wrapper |

Consumer entry points (Celery tasks that instantiate workers):

| Task | Line | Consumer group | Streams read | Beat status |
|---|---|---|---|---|
| `process_event_bus_scoring_queue` | `core/tasks.py:4726` | `scoring_workers` | `SPIDER_DATA` + `OPPORTUNITY_CREATED` | **NOT ENROLLED** — 0 `PeriodicTask` rows (F9) |
| `process_event_bus_validation_queue` | `core/tasks.py:4760` | `validation_workers` | `OPPORTUNITY_SCORED` + `VALIDATION_REQUIRED` | **NOT ENROLLED** (F9) |
| `process_event_bus_analytics_queue` | `core/tasks.py:4794` | `analytics_workers` | `VALIDATION_DECIDED` + `OUTCOME_RECORDED` + `MODEL_TRAINED` | **NOT ENROLLED** (F9) |
| `claim_stale_events` | `core/tasks.py:4828` | (all 3) | (all subscribed streams, ≥60s idle) | ENROLLED (5min beat, `core/celery.py:532`) |
| `get_event_bus_stats` | `core/tasks.py:4874` | — | (reads `xlen` of every stream + DLQ) | **NOT ENROLLED** (F10) |

Handler entry points (dispatched by `EventHandlerRegistry` in
`event_handlers.py:31`, registered at `_register_default_handlers`
:42-62): 7 handler functions keyed by `event_type` string
(spider_crawl_complete, opportunity_scored, validation_queued,
validation_decided, outcome_recorded, model_trained, alert_error,
alert_critical). Registry is instantiated per `EventConsumerWorker`
(one per Celery task run) — no long-lived shared handler registry
process.

## 4. Major Models

The EventBus surface has no Django ORM models; all durable state
lives in Redis. Relevant in-memory dataclasses (`event_bus.py`):

| Model | Line | Fields | Purpose |
|---|---|---|---|
| `EventStream` (str-Enum) | :21-30 | 8 values | Canonical stream identity + Redis key (e.g., `"mi:spider_data"`) |
| `EventPriority` (str-Enum) | :33-38 | LOW / NORMAL / HIGH / CRITICAL | Priority metadata (not enforced by broker; informational) |
| `Event` (dataclass) | :41-77 | `event_type`, `stream`, `data`, `timestamp`, `event_id`, `priority`, `source`, `correlation_id` | Canonical envelope. `data` is `Dict[str, Any]` — no per-stream typing |
| `ConsumerInfo` (dataclass) | :80-87 | `name`, `group`, `handler`, `streams`, `active` | In-memory consumer registration; unused by current code path (see F18-adjacent — decorative structure) |
| `HandlerResult` (dataclass) | `event_handlers.py:20-28` | `success`, `event_id`, `handler`, `message`, `error`, `processing_time_ms` | Per-handler outcome; consumed by `process_batch` to compute ACK vs. non-ACK |

Redis-side data structures:

| Structure | Redis key(s) | Access | Retention |
|---|---|---|---|
| Per-stream event log | `mi:spider_data`, `mi:opportunity_created`, ..., `mi:system_alert` | `xadd`, `xreadgroup`, `xrange`, `xlen`, `xack`, `xpending_range`, `xclaim`, `xinfo_stream`, `xinfo_groups` | `STREAM_MAX_LEN=10000` (line 104) — trim at write time; oldest events silently evicted past cap |
| Dead-letter queue | `mi:dead_letter` | `xadd` (only from `_move_to_dead_letter` at line 468-471), `xlen` (from stats), `xrange` (from `replay()` if called) | `maxlen=1000` (line 471) — trim at write time |
| Per-metric counter | `mi:metrics:<name>` (`_increment_metric` at :479) | `incr` | No TTL set (see F16) |

**S1275 event schema precedent NOT adopted** — no `schema_version`
field on `Event`, no per-stream schema type registry, no shared
schema validation layer. All 8 streams share an untracked schema
(F12).

## 5. Major Services

| Service | Location | Role | Adoption |
|---|---|---|---|
| `EventBus` | `event_bus.py:90-532` | Singleton wrapping Redis client + consumer-group provisioning + `publish` / `consume` / `acknowledge` / `replay` / `get_pending` / `claim_stale` / `_move_to_dead_letter` / `get_stats` | STRONG — used everywhere EventBus is touched; sole publisher path |
| Publisher wrappers | `event_bus.py:539-713` | 7 typed helpers that construct `Event.data` payload + call `bus.publish(stream=..., data=...)` | Adoption per §10.2 |
| `EventHandlerRegistry` | `event_handlers.py:31-117` | Per-`event_type` handler dispatch. Default registrations at :42-62 | WEAK — instantiated fresh per worker, no shared state |
| Handler functions | `event_handlers.py:125-383` | 7 default handlers keyed by `event_type` string | See F18 — 6 of 7 are log-only or log + Discord (no DB writes) |
| `EventConsumerWorker` | `event_handlers.py:391-503` | Consumes from streams, dispatches, ACKs on success, reclaims stale | STRONG — sole consumer implementation |
| `create_scoring_worker` / `create_validation_worker` / `create_analytics_worker` | `event_handlers.py:521-552` | Factory functions returning pre-configured workers | STRONG when Celery tasks fire; but F9 blocks the beat path |
| `SpiderAgentConnector.publish_spider_data` (**separate substrate**) | `ai_core/agents/spider_agent_connector.py:311-325` | Uses raw `redis.publish()` on a pub/sub channel, NOT EventStream.SPIDER_DATA | Second substrate — recorded as F11 for P3 |

## 6. Major APIs and Interfaces

**Programmatic (Python) surface** — publishing:

```python
# Preferred: typed wrapper
from core.services.event_bus import publish_opportunity_scored_event
publish_opportunity_scored_event(
    opportunity_id="...", spider_data_id="...",
    ml_score=0.82, rule_score=0.75, hybrid_score=0.79,
    confidence=88.0, source="scoring_dispatcher_realtime"
)

# Direct (bypass wrapper) — zero call sites found in codebase
from core.services.event_bus import get_event_bus, EventStream
get_event_bus().publish(
    stream=EventStream.OPPORTUNITY_SCORED,
    event_type="opportunity_scored",
    data={"opportunity_id": "..."},
)
```

**Programmatic surface** — consuming:

```python
# Preferred: factory-instantiated worker (via Celery task)
from core.services.event_handlers import create_validation_worker
worker = create_validation_worker(consumer_name="celery_validation_worker")
result = worker.process_batch()  # returns {events_processed, events_succeeded, events_failed, errors}
```

**Redis-side surface** (accessible via `redis-cli`):

- `XLEN mi:opportunity_scored` — stream length
- `XPENDING mi:opportunity_scored validation_workers` — unacknowledged events
- `XRANGE mi:opportunity_scored - +` — replay from start
- `XLEN mi:dead_letter` — DLQ size (currently the only DLQ observability)

**No HTTP / REST surface** — EventBus is a Python-internal substrate
only. No `/api/events/...` routes were found. Chat with the platform
via PA tools does not expose EventBus directly (Rigby has no
`event_bus_tool` handler at time of audit).

**Monitoring surface**: `get_event_bus_stats` (`core/tasks.py:4874`)
is defined but not scheduled (F10). Its output shape is
`{"streams": {name: len}, "total_events": int, "dead_letter_count": int}`.

## 7. Runtime Flows

Present-state runtime flows (post-audit, distinct from Session 470
design intent):

**Flow A — Opportunity scoring (only end-to-end live producer):**
```
Spider data lands in `SpiderData` model
  ↓  (Celery task or direct call in scoring_dispatcher)
core/services/scoring_dispatcher.py:_score_realtime  (line ~282)
  ↓  _publish_scoring_event(spider_data, result, 'realtime', latency_ms)  (line :21)
  ↓  publish_opportunity_scored_event(opportunity_id=..., spider_data_id=..., ml_score=..., rule_score=..., hybrid_score=..., confidence=..., source="scoring_dispatcher_realtime")
  ↓  bus.publish(stream=EventStream.OPPORTUNITY_SCORED, event_type="opportunity_scored", data={...}, priority=<HIGH/NORMAL/LOW>, source=...)
  ↓  redis.xadd("mi:opportunity_scored", event_dict, maxlen=10000)
  ↓
  ↓  ┌── VALIDATION_WORKERS consumer group — subscribed via event_handlers.py:536 (streams=[OPPORTUNITY_SCORED, VALIDATION_REQUIRED])
  ↓  └── BUT: process_event_bus_validation_queue is NOT scheduled on beat (F9)
  ↓
  ×  Events pile up in stream. STREAM_MAX_LEN=10000 triggers silent truncation on 10001st write.
```

**Flow B — HITL validation (isolated producer):**
```
HITL service creates ValidationRequest
  ↓
core/services/hitl_validation.py:_publish_validation_event(event_type="validation_required", data={...})  (line :21)
  ↓  publish_validation_required_event(validation_request_id, opportunity_id, confidence, priority, source="hitl_service")  (line :30)
  ↓  bus.publish(stream=EventStream.VALIDATION_REQUIRED, ...)
  ↓  redis.xadd("mi:validation_required", ...)
  ↓  (consumer dormant per Flow A — F9)

Human decides via UI / Rigby
  ↓
core/services/hitl_validation.py:_publish_validation_event(event_type="validation_decided", data={...})
  ↓  publish_validation_decided_event(...)  (line :38)
  ↓  redis.xadd("mi:validation_decided", ...)
  ↓  (analytics_workers consumer subscribed via event_handlers.py:547 — but F9)
```

**Flow C — Stale event reclaim (only live consumer path):**
```
Beat fires claim_stale_events every 5min
  ↓  core/tasks.py:4828
  ↓  Instantiates 3 workers (scoring/validation/analytics) with consumer_name="celery_stale_claimer"
  ↓  For each worker: calls claim_stale_events(min_idle_ms=60000)
  ↓    ↓ event_bus.py:393:claim_stale — get_pending → xclaim → dispatch handlers → ACK on success
  ↓
  Because process_event_bus_*_queue tasks are dormant, no consumer has ever
  called xreadgroup with '>' — so xpending is empty — so claim_stale returns [].
  Effective outcome: claim_stale_events runs, does nothing.
```

**Flow D — Handler failure retry loop (design counter-hypothetical):**
If a consumer WERE running and a handler raised, the failed event
would NOT be ACK'd (`event_handlers.py:458` — `events_failed += 1`,
no `acknowledge()` call), would NOT be moved to DLQ (only parse
failures reach DLQ, `event_bus.py:275`), would appear in `xpending`
after 60s, and would be reclaimed by `claim_stale_events` — which
re-dispatches to the same handler → same failure → infinite loop with
no exponential backoff and no give-up counter (F14).

**Flow E — DLQ emission (parse-error path):**
```
consumer.xreadgroup returns malformed message
  ↓  event_bus.py:consume:271 — Event.from_dict raises
  ↓  event_bus.py:275 — _move_to_dead_letter(stream_name, msg_id, msg_data, str(e))
  ↓  event_bus.py:468 — xadd("mi:dead_letter", {original_stream, original_id, error, timestamp, **event_data}, maxlen=1000)
  ↓  (no reader consumes DLQ — F15)
```

**Absent flows (design intent, not implemented):**
- SPIDER_DATA fan-out from spider tasks: no `publish_spider_data_event` caller.
- OPPORTUNITY_CREATED emission from opportunity-creation code path: no wrapper, no direct-publish site.
- OUTCOME_RECORDED emission from `BettingOutcomeVerifier` / outcome-tracking code: no caller.
- MODEL_TRAINED emission from ML retraining code: no caller.
- SYSTEM_ALERT emission from any monitoring code: no caller.

## 8. Data Ownership and Lifecycle

- **Producer wrappers** own the payload schema (nowhere else does the
  event-`data` shape get validated). Ownership is implicit — the
  wrapper docstring lists field names; no schema type is exported.
- **Stream events** live in Redis for at most `STREAM_MAX_LEN=10000`
  entries per stream. Age-based retention is NOT configured — an
  event survives until it's the 10001st write. Under low producer
  volume the stream can hold stale events for weeks; under high
  producer volume very recent events are the only ones surviving.
- **DLQ events** live for at most 1000 entries. Same silent-truncation
  eviction policy. No age-based TTL.
- **Consumer group state** (pending set + last-delivered-id) has no
  eviction — persists in Redis indefinitely. If a consumer group is
  ever created for a stream that later goes dormant, the group state
  and any pending events remain in memory.
- **`Event.timestamp`** is `datetime.utcnow()` at publish time (line
  47). No consumer-side clock or delivery timestamp is stamped by the
  substrate.
- **`Event.correlation_id`** is publisher-provided; no wrapper injects
  it automatically. All 7 wrappers omit correlation_id → every real
  emission today has `correlation_id=None`.
- **No user / actor identity** carried on the event envelope. `source`
  is a short string (e.g., `"scoring_dispatcher_realtime"`,
  `"hitl_service"`). Group 1900 P1 `executor_actor` /
  `sponsor_actor` / `principal_user` trio is NOT propagated on
  EventBus events today.

## 9. Integrations With Other Domains

Table (S1274 §12.1 registry style, pair classification per §12
STRONG / WEAK / MISSING / OVERCOUPLED):

| Producer domain | → EventBus stream | Producer classification | Consumer domain | Consumer classification | Rationale |
|---|---|---|---|---|---|
| Revenue (Scoring — Group 1400 §5.1) | `OPPORTUNITY_SCORED` | STRONG | Validation (HITL — Group 1400) | WEAK (subscribed, beat dormant) | 2 producer call sites verified (`scoring_dispatcher.py:282,480`); consumer group `validation_workers` subscribed at `event_handlers.py:536` but `process_event_bus_validation_queue` unscheduled (F9) |
| Validation (HITL — Group 1400) | `VALIDATION_REQUIRED` | WEAK | Analytics (Group 1400 + Group 1700 observability substrate) | WEAK (subscribed, beat dormant) | 1 producer call site (`hitl_validation.py:30`); consumer group `validation_workers` subscribed (self-loop with own decision writes); F9 |
| Validation (HITL — Group 1400) | `VALIDATION_DECIDED` | WEAK | Analytics + Learning (Group 1400) | WEAK (subscribed, beat dormant) | 1 producer call site (`hitl_validation.py:38`); consumer group `analytics_workers` subscribed at :547 (F9) |
| Spiders (Group 1500 + 1400) | `SPIDER_DATA` | MISSING | Scoring | WEAK (subscribed, beat dormant) | Publisher wrapper `event_bus.py:539` has 0 non-definition caller sites; `SpiderAgentConnector` in ai_core uses a **separate** pub/sub channel (F11); consumer `scoring_workers` subscribed at :526 (F9) |
| Opportunity creation (Group 1400) | `OPPORTUNITY_CREATED` | MISSING | Scoring | MISSING | No publisher wrapper defined; consumer group `scoring_workers` subscribed at :526 but never receives (F2) |
| Outcome tracking (Group 1400 + 1500 sports) | `OUTCOME_RECORDED` | MISSING | Analytics + Learning | WEAK (subscribed, beat dormant) | Publisher `event_bus.py:643` has 0 callers; consumer `analytics_workers` subscribed :548 (F6) |
| ML training (Group 1400) | `MODEL_TRAINED` | MISSING (corrects S1273 §3.31 UNKNOWN) | Analytics + Notifications | WEAK (subscribed, beat dormant) | Publisher `event_bus.py:665` has 0 callers; consumer `analytics_workers` subscribed :549 (F7) |
| System monitoring (Group 1700 observability) | `SYSTEM_ALERT` | MISSING | (nothing — no worker subscribes to stream) | MISSING | Publisher `event_bus.py:686` has 0 callers; **no worker's `streams=[...]` list includes `SYSTEM_ALERT`** (F8 — handler dispatch registered by `event_type` but stream subscription omitted from the 3 factory workers) |
| Any consumer whose handler raises | `mi:dead_letter` | WEAK (parse-error path only) | (nothing — no worker consumes DLQ) | MISSING | `_move_to_dead_letter` called at `event_bus.py:275` from `consume` parse-error path only; F14 shows handler failure never reaches DLQ; F15 shows no DLQ reader exists |

**Domain-pair strength summary (S1274 §11 tier count):** STRONG × any:
1 pair (Revenue → OPPORTUNITY_SCORED producer). WEAK × any: 4 pairs
(the 2 hitl_validation producers + the 2 dormant-consumer sides of
STRONG/WEAK producers). MISSING × any: 6 pairs (SYSTEM_ALERT double
+ SPIDER_DATA producer + OPPORTUNITY_CREATED producer +
OUTCOME_RECORDED producer + MODEL_TRAINED producer + DLQ consumer).

**Comparison to prior classification** (`cross_domain_integration_audit.md`
lines 373-380): the platform-level integration audit classified 6 of
7 stream × direction pairs as UNKNOWN pending caller sweep. This P1
audit resolves all 8 streams × direction pairs — **zero UNKNOWN
remaining** (Rigby S2001 SIGN emphasis #1 satisfied).

## 10. Event Flows

### 10.1 Stream × direction producer/consumer map (STRONG / WEAK / MISSING classification)

For every stream, both directions (producer + consumer) classified.
Numeric evidence per Rigby S2001 SIGN emphasis #2.

| Stream | Producer class | Producer evidence | Consumer class | Consumer evidence | Runtime state |
|---|---|---|---|---|---|
| `SPIDER_DATA` (`mi:spider_data`) | **MISSING** | Wrapper defined at `event_bus.py:539`; caller grep across `**/*.py` returns 0 non-definition, non-docs hits. `SpiderAgentConnector.publish_spider_data` at `ai_core/agents/spider_agent_connector.py:311` uses a different substrate (raw redis.publish, F11) | **WEAK** | `create_scoring_worker` subscribes at `event_handlers.py:526`; task `process_event_bus_scoring_queue` at `core/tasks.py:4726` — but 0 `PeriodicTask` rows (F9) | Stream unused |
| `OPPORTUNITY_CREATED` (`mi:opportunity_created`) | **MISSING** | **No publisher wrapper defined at all.** Direct-publish grep for `stream=EventStream.OPPORTUNITY_CREATED` returns 0 hits | **MISSING** | `create_scoring_worker` subscribes at :526 alongside SPIDER_DATA; but F9 blocks + F2: even if F9 fixed, no producer would ever fire | Stream unused (F2) |
| `OPPORTUNITY_SCORED` (`mi:opportunity_scored`) | **STRONG** | Wrapper at `event_bus.py:559`. 2 call sites via helper `_publish_scoring_event` at `scoring_dispatcher.py:21-56`, called from `:282` (realtime) + `:480` (batch) | **WEAK** | `create_validation_worker` subscribes at :536; `process_event_bus_validation_queue` at `core/tasks.py:4760` — 0 `PeriodicTask` rows (F9) | Producer fires; consumer dormant |
| `VALIDATION_REQUIRED` (`mi:validation_required`) | **WEAK** | Wrapper at `event_bus.py:596`. 1 call site via `_publish_validation_event` at `hitl_validation.py:29-36`; caller depth: uncertain (may be called from admin flows and Rigby tools — grep on `_publish_validation_event` shows definition only, so effective producer volume unknown but non-zero on paper) | **WEAK** | `create_validation_worker` subscribes at :536; F9 dormant | Producer fires but low volume; consumer dormant |
| `VALIDATION_DECIDED` (`mi:validation_decided`) | **WEAK** | Wrapper at `event_bus.py:619`. 1 call site via `_publish_validation_event` at `hitl_validation.py:37-45` | **WEAK** | `create_analytics_worker` subscribes at :547; `process_event_bus_analytics_queue` at :4794 — 0 `PeriodicTask` rows (F9) | Producer fires but low volume; consumer dormant |
| `OUTCOME_RECORDED` (`mi:outcome_recorded`) | **MISSING** | Wrapper at `event_bus.py:643`. 0 caller grep hits | **WEAK** | `create_analytics_worker` subscribes at :548; F9 dormant | Stream unused (F6) |
| `MODEL_TRAINED` (`mi:model_trained`) | **MISSING** | Wrapper at `event_bus.py:665`. 0 caller grep hits. **Corrects S1273 §3.31 UNKNOWN.** | **WEAK** | `create_analytics_worker` subscribes at :549; F9 dormant | Stream unused (F7) |
| `SYSTEM_ALERT` (`mi:system_alert`) | **MISSING** | Wrapper at `event_bus.py:686`. 0 caller grep hits | **MISSING** | Handler `handle_system_alert_event` registered for `event_type=alert_error/alert_critical` at `event_handlers.py:61-62`, but **no worker's `streams=[...]` list includes `SYSTEM_ALERT`**. Even if published, the handler would never fire because no consumer group reads the stream (F8) | Double MISSING |
| `mi:dead_letter` (DLQ) | **WEAK** | `_move_to_dead_letter` at `event_bus.py:451-477`, called at `event_bus.py:275` from parse-error path only. Handler failures do NOT reach DLQ (F14, F15) | **MISSING** | No `xreadgroup` / `xrange` / `xreadgroup` caller reads `mi:dead_letter`. Only `get_event_bus_stats` reads `xlen` at `event_bus.py:528` — read-only length; no consumer of contents (F15) | DLQ receives parse errors; nothing reads |

### 10.2 α — Schema-shape doc per stream

Per Rigby S2001 SIGN emphasis #3 — stream-by-stream, not generic.
Payload shape derived from the wrapper implementation. **No `schema_version`
present on any wrapper (F12).**

| Stream | Wrapper (line) | Payload fields (`Event.data`) | Types (inferred from wrapper signatures) | schema_version | Envelope fields set by wrapper |
|---|---|---|---|---|---|
| SPIDER_DATA | :539 | `spider_name`, `spider_data_id`, `record_count` | str, str, int | absent (F12) | `event_type="spider_crawl_complete"`, `source` (default `"spider_network"`), `priority=NORMAL` (default) |
| OPPORTUNITY_CREATED | (no wrapper) | — undefined — | — | absent (F12) | — (no publisher ever set) |
| OPPORTUNITY_SCORED | :559 | `opportunity_id`, `spider_data_id`, `hybrid_score`, `ml_score`, `rule_score`, `confidence` | Optional[str], Optional[str], Optional[float], Optional[float], Optional[float], Optional[float] | absent (F12) | `event_type="opportunity_scored"`, `source` (default `"scoring_engine"`), `priority` computed from `confidence` (HIGH if ≥85, LOW if <50, else NORMAL) |
| VALIDATION_REQUIRED | :596 | `validation_request_id`, `opportunity_id`, `confidence`, `priority` | str, str, float, int | absent (F12) | `event_type="validation_queued"`, `source` (default `"hitl_service"`), `priority=HIGH` (forced) |
| VALIDATION_DECIDED | :619 | `validation_request_id`, `opportunity_id`, `decision`, `decided_by`, `override_score` | str, str, str, str, Optional[float] | absent (F12) | `event_type="validation_decided"`, `source` (default `"hitl_service"`), `priority=NORMAL` (default) |
| OUTCOME_RECORDED | :643 | `opportunity_id`, `outcome_type`, `outcome_value`, `actual_revenue` | str, str, float, Optional[float] | absent (F12) | `event_type="outcome_recorded"`, `source` (default `"outcome_tracker"`), `priority=NORMAL` (default) |
| MODEL_TRAINED | :665 | `model_version`, `training_samples`, `metrics` | str, int, Dict[str, float] | absent (F12) | `event_type="model_trained"`, `source` (default `"ml_training"`), `priority=HIGH` (forced) |
| SYSTEM_ALERT | :686 | `message`, `severity`, `details` | str, str, Optional[Dict] | absent (F12) | `event_type=f"alert_{alert_type}"`, `source` (default `"system"`), `priority` mapped from severity |
| DLQ | :468 (`_move_to_dead_letter`) | `original_stream`, `original_id`, `error`, `timestamp` **+ arbitrary `**event_data`** spread from failed parse | str, str, str, ISO-8601 str, mixed | absent | Not an Event dataclass — raw `xadd` |

Envelope-level fields set by `bus.publish` for all streams (from
`Event.to_dict` at :53-63): `event_type`, `stream`, `data`
(json-serialized), `timestamp` (ISO-8601, `datetime.utcnow()` at
publish), `priority`, `source`, `correlation_id` (empty string if
None). Every real-world emission today has `correlation_id=""`
because no wrapper accepts a correlation_id arg and no publisher
passes one via `bus.publish(...)` directly.

### 10.3 β — Runtime assert audit

Per Rigby S2001 SIGN emphasis #3 — stream-by-stream.

| Stream | Current asserts | Handler location | β posture |
|---|---|---|---|
| SPIDER_DATA | `data.get('spider_name')` (line 136), `data.get('spider_data_id')` (137), `data.get('record_count', 0)` (138). One implicit null check: `if not spider_data_id: return` (140-142) | `handle_spider_data_event` :125-161 | Only spider_data_id treated as required (early return on absence). Other fields silently default |
| OPPORTUNITY_CREATED | (no handler — no event_type match; `_register_default_handlers` :42-62 registers no `opportunity_created` handler) | — | Handler MISSING |
| OPPORTUNITY_SCORED | `data.get('opportunity_id')`, `data.get('confidence', 0)`, `data.get('hybrid_score', 0)` | `handle_opportunity_scored_event` :164-188 | No required-field assertions. Numeric defaults 0 silently corrupt logging math |
| VALIDATION_REQUIRED | `data.get('validation_request_id')`, `data.get('opportunity_id')`, `data.get('confidence', 0)`, `data.get('priority', 3)` | `handle_validation_queued_event` :191-231 | No asserts. Priority defaults to 3 (medium) if missing |
| VALIDATION_DECIDED | `data.get('validation_request_id')`, `data.get('opportunity_id')`, `data.get('decision')`, `data.get('decided_by')`, `data.get('override_score')` | `handle_validation_decided_event` :234-261 | No asserts. `if override_score is not None:` at :257 is the only check |
| OUTCOME_RECORDED | `data.get('opportunity_id')`, `data.get('outcome_type')`, `data.get('outcome_value')`, `data.get('actual_revenue')` | `handle_outcome_recorded_event` :264-301 | No asserts. Handler queries `OpportunityOutcome.objects.filter(actual_outcome__isnull=False).count()` — no dep on payload |
| MODEL_TRAINED | `data.get('model_version')`, `data.get('training_samples')`, `data.get('metrics', {})` | `handle_model_trained_event` :304-339 | No asserts. Uses `metrics.get('test_r2', 'N/A')` for Discord — no failure surface |
| SYSTEM_ALERT | `data.get('message')`, `data.get('severity', 'warning')`, `data.get('details', {})` | `handle_system_alert_event` :342-383 | No asserts. Message defaults to None; would log as `None` if missing |
| DLQ | (no consumer — see §10.1) | — | β N/A — no reader |

**β aggregate posture:** across all 7 handlers, there are **zero
`assert` statements on payload fields**. Every handler uses
`data.get(key, default)` which silently accepts arbitrary payload
shape. A P2 schema-versioning contract must either (a) add per-stream
Pydantic validation at the wrapper OR consumer boundary, or (b)
accept β-drift as tolerable given F18 (handlers are largely
decorative anyway).

### 10.4 γ — Version gate policy (current state)

Per Rigby S2001 SIGN emphasis #3 — stream-by-stream.

| Stream | schema_version present? | Version gate at consumer? | Migration path today |
|---|---|---|---|
| SPIDER_DATA | No | No | Ad-hoc — a wrapper field addition would silently work (default-tolerant handlers) but any field removal or type change is invisible to consumers |
| OPPORTUNITY_CREATED | N/A (no publisher) | N/A | — |
| OPPORTUNITY_SCORED | No | No | Same as SPIDER_DATA |
| VALIDATION_REQUIRED | No | No | Same |
| VALIDATION_DECIDED | No | No | Same |
| OUTCOME_RECORDED | No | No | Same |
| MODEL_TRAINED | No | No | Same |
| SYSTEM_ALERT | No | No | Same |
| DLQ | No | N/A | — |

**γ current state: NO versioning policy exists.** S1275 event schema
design shipped a per-event `schema_version` field with graduation
contract as precedent (see `docs/research/symbol_mapping_event_schema_design.md`)
— but the EventBus wrappers do NOT stamp `schema_version` and no
consumer reads or dispatches on it. Adopting S1275 precedent would
be a **green-field addition** (add field to wrapper + add
version-dispatch table in `EventHandlerRegistry`), not a migration.
P2 decides the go-forward policy (parent §5.2 explicitly hands γ to
P2); P1 documents this as the baseline.

### 10.5 δ — Replay-test enumeration

Per Rigby S2001 SIGN emphasis #3 — stream-by-stream.

| Stream | Replay window (Redis retention) | Replay code surface | Replayable for regression test? |
|---|---|---|---|
| SPIDER_DATA | `STREAM_MAX_LEN=10000` — oldest evicted at 10001st write | `EventBus.replay(stream=EventStream.SPIDER_DATA, start_id='0', end_id='+', count=100)` at `event_bus.py:311-351` | Yes in principle; zero producers means the stream is empty in most environments |
| OPPORTUNITY_CREATED | Same | Same replay surface | Empty stream — no history to replay |
| OPPORTUNITY_SCORED | Same | Same | Yes — this is the ONE stream with production replay potential today. Volume proportional to spider→scoring pipeline throughput; capped at 10000 |
| VALIDATION_REQUIRED | Same | Same | Yes; volume proportional to HITL flow |
| VALIDATION_DECIDED | Same | Same | Yes; low volume |
| OUTCOME_RECORDED | Same | Same | Empty — no producers |
| MODEL_TRAINED | Same | Same | Empty — no producers |
| SYSTEM_ALERT | Same | Same | Empty — no producers |
| DLQ | `maxlen=1000` at DLQ write time | `xrange('mi:dead_letter', ...)` — `EventBus.replay` does not accept DLQ as an `EventStream` value (DLQ is a raw string constant, not enum member) | Yes via raw redis-cli or a new `EventBus.replay_dlq()` method (not implemented). Contents are parse-error records with `**event_data` spread — schema is heterogeneous |

**δ aggregate posture:** `EventBus.replay()` exists but has **zero
callers in the codebase** (grep on `\.replay\(` in `core/` returns
only the definition + `event_bus.py:346` internal logger). No
regression tests exercise the replay surface (F17). Adopting replay
as a first-class regression tool would require (i) a Django
management command wrapping `EventBus.replay`, (ii) a test-harness
that seeds a Redis Stream + runs a worker against it + asserts
consumer output — no such harness exists today.

### 10.6 Handler-registration vs stream-subscription overlap audit

Cross-cut: for each event_type registered in
`_register_default_handlers` (`event_handlers.py:42-62`), verify
that at least one worker subscribes to the corresponding stream.

| event_type | Handler | Consumer group subscribing to source stream | Coverage |
|---|---|---|---|
| `spider_crawl_complete` | `handle_spider_data_event` | `scoring_workers` (SPIDER_DATA at :526) | ✓ (dormant per F9) |
| `opportunity_scored` | `handle_opportunity_scored_event` | `validation_workers` (OPPORTUNITY_SCORED at :536) | ✓ (dormant per F9) |
| `validation_queued` | `handle_validation_queued_event` | `validation_workers` (VALIDATION_REQUIRED at :536) | ✓ (dormant per F9) |
| `validation_decided` | `handle_validation_decided_event` | `analytics_workers` (VALIDATION_DECIDED at :547) | ✓ (dormant per F9) |
| `outcome_recorded` | `handle_outcome_recorded_event` | `analytics_workers` (OUTCOME_RECORDED at :548) | ✓ (dormant per F9) |
| `model_trained` | `handle_model_trained_event` | `analytics_workers` (MODEL_TRAINED at :549) | ✓ (dormant per F9) |
| `alert_error` | `handle_system_alert_event` | **no worker subscribes to SYSTEM_ALERT** | ✗ (F8) |
| `alert_critical` | `handle_system_alert_event` | **no worker subscribes to SYSTEM_ALERT** | ✗ (F8) |

## 11. Existing Documentation

- `docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md` — parent scoping (this arc, S2000). §5.1 defined the current P1 mission.
- `docs/research/platform/cross_domain_integration_audit.md` — 6 of 7 stream × direction pairs classified UNKNOWN pending a caller sweep (this P1 audit resolves them).
- `docs/research/platform_architecture_inventory.md` — inventory snapshot of EventBus row + DLQ.
- `docs/research/employee_os_collaboration_patterns.md` — includes EventBus wrapper table (lines 194 + 431-444 + 705).
- `docs/research/employee_os_communication_substrate_audit.md` — EventBus row (line 135); erroneously says "6 named streams + DLQ" — should be **8 named streams + DLQ** (see PLATFORM_INVENTORY drift item).
- `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` — §10.1 verified `OPPORTUNITY_SCORED` producer/consumer pair; §10.2 T9 flagged `OPPORTUNITY_CREATED` as `dead_code_candidate` (which this audit confirms as F2).
- `docs/research/symbol_mapping_event_schema_design.md` — S1275 precedent for `schema_version` field; not adopted by EventBus wrappers.
- `docs/EVENT_SYSTEM_INVENTORY.md` — event system inventory (referenced by parent §64).
- `docs/archive/handoffs-pre-800/SESSION_472_EVENT_BUS.md` — original Session 470 phase-4 design intent (archived; the runtime has drifted substantially — this audit documents the drift).

## 12. Research Coverage

**MODERATE.** Prior focused docs exist: the platform-level integration
audit (`cross_domain_integration_audit.md`), the Revenue Group 1400
P1 (`1401_revenue_opportunity_discovery_scoring_audit.md`), and the
Employee OS communication substrate audit
(`employee_os_communication_substrate_audit.md`). This P1 is the
first dedicated EventBus deep-audit; before this, the substrate was
touched in cross-cutting audits without a producer/consumer registry
that resolves all UNKNOWNs.

Post-P1, research coverage advances to **DEEP** for the EventBus
producer/consumer topology + current-state contract-verification
surfaces; **MODERATE** remains for HAI event contract (P2 territory)
and for cross-substrate composition (P3 territory).

## 13. Architecture Maturity

**PARTIAL.** The scaffolding is comprehensive and cohesive (8-stream
enum + typed wrappers + consumer group factories + DLQ + replay +
stale-claim). Runtime adoption is thin and asymmetric:

- 3 of 7 wrappers see any producer call site (all in `scoring_dispatcher.py`
  or `hitl_validation.py`).
- 0 of 5 consumer beat tasks other than `claim_stale_events` are
  scheduled.
- 0 of 8 streams have `schema_version` stamped.
- 0 of 7 handlers assert payload shape.
- 0 callers of `replay()`.
- 1 of 3 producer-active streams (OPPORTUNITY_SCORED) is the only
  end-to-end publish → consume flow — and even it terminates in a
  dormant consumer group.

The substrate is not experimental — it is a working library that
downstream code chose not to use. Maturity classification is PARTIAL
per playbook §12 (works in places but not cohesive or fully wired).

## 14. Known Drift

- **F9 — consumer beat tasks unscheduled at runtime.** Design intent
  (per docstrings at `core/tasks.py:4726/4760/4794/4874`) is 30s /
  30s / 60s / 15min beat cadences. Actual PeriodicTask enrollment:
  zero. Only `claim_stale_events` runs (5min).
- **F12 — schema_version not adopted.** S1275 precedent exists; no
  publisher wrapper stamps it, no consumer dispatches on it.
- **F13 — no runtime asserts.** Handlers use `data.get(key, default)`
  exclusively.
- **F15 — DLQ silence on handler failure.** DLQ receives only parse
  errors; handler failures never reach DLQ.
- **F16 — DLQ has cleanup gap, corrected characterization.** S1274
  §6.2 said "no cleanup task" implying unbounded growth. Actual:
  `xadd` includes `maxlen=1000` so DLQ IS bounded — the real gap is
  no reader / no alerting on DLQ growth (F15 subsumes this concern).
- **F17 — replay() unused.** Replay surface exists at
  `event_bus.py:311` but has zero callers in production code.
- **F18 — decorative consumer handlers.** 6 of 7 default handlers
  are log-only or log + Discord — only `handle_spider_data_event`
  queues a downstream Celery task (`score_spider_data_async.delay`).
  No consumer handler writes to a DB model.

Prior drift explicitly corrected by this audit:

- S1273 §3.31 classified `publish_model_trained_event` as UNKNOWN.
  This audit finds the wrapper defined at `event_bus.py:665` and 0
  callers → **MISSING (dead-code wrapper)**. See F7.
- S1274 §6.2 characterized DLQ as accumulating unbounded. Actual:
  DLQ bounded at 1000. See F16.
- `cross_domain_integration_audit.md` classified 6 of 7 pairs as
  UNKNOWN. This audit resolves every pair to STRONG / WEAK / MISSING.
  Zero UNKNOWN remaining.
- `employee_os_communication_substrate_audit.md:135` says "6 named
  streams + DLQ" — actual is 8 named streams. Recommend correction
  (see §7.4 anchor recommendation to P4 CONSOLIDATION).

## 15. Known Technical Debt

- **F14 — handler failure retry loop with no give-up.** When a
  handler raises, the event is not ACK'd, not moved to DLQ, and gets
  reclaimed by `claim_stale_events` every 60s of pending idle. No
  delivery-count cap, no exponential backoff. If a handler bug ever
  ships, every affected event loops forever until Redis Stream
  truncation (10000 write horizon) or human intervention.
- **F15 — DLQ blind to handler failures.** DLQ observes parse errors
  only. The dominant real-world failure mode (handler raises) is
  invisible to `get_event_bus_stats` and to any future DLQ reader.
- **F16 — DLQ retention/alerting gap.** DLQ MAXLEN=1000 caps growth
  but nothing alerts on DLQ length trending upward and nothing
  consumes DLQ contents to root-cause or retry.
- **F17 — replay unused as regression tool.** No management command
  or test harness invokes `EventBus.replay`. Regression testing of
  consumer handlers on real event history is not on-ramp today.
- **`Event.correlation_id` never populated.** No wrapper accepts
  correlation_id; every real emission today has
  `correlation_id=None`/`""`. This forecloses cross-substrate
  request tracing (Group 1700 observability territory).
- **`ConsumerInfo` dataclass at `event_bus.py:80-87` unused.** No
  code path registers a `ConsumerInfo` instance; the substrate
  works despite the dataclass being dead. Candidate for deletion or
  actual wiring — flag for P4 CONSOLIDATION.

## 16. Boundary Violations

- **F11 — three parallel substrates for spider-data → agents
  (SIGN-expanded).**
  (i) `ai_core/agents/spider_agent_connector.py:311:SpiderAgentConnector.publish_spider_data`
  uses raw `redis.publish()` on `self.channels['spider_data']` —
  bypassing the EventBus Redis Streams substrate + the
  `publish_spider_data_event` wrapper entirely. Real callers:
  `ai_core/agents/concrete_executor.py:637-638` (imports singleton
  + assigns to `self.spider_connector`) + `core/views_agent_intelligence.py:352,355`
  (reads `routing_table`). (ii) `intelligence/spider_agent_connector.py:20:SpiderAgentConnector`
  is a completely separate class with the same name in a different
  Django app. It does NOT use Redis pub/sub OR EventBus — its
  `_build_routing_map` at :31 returns an in-process `Dict[str,
  List[str]]` category → agent-keyword mapping consumed by 6 real
  caller sites (`core/tasks_spiders.py:260,307` + `core/tasks.py:1355,1359`
  + `core/management/commands/process_spider_data.py:6,16` +
  `core/management/commands/activate_spiders.py:10,234`). (iii)
  EventBus `SPIDER_DATA` stream + `publish_spider_data_event`
  wrapper is dormant (0 callers per F1). The three substrates are
  architecturally distinct (pub/sub fire-and-forget with no
  durability; in-process routing with no persistence; Streams
  durable + replayable), but the shared purpose "route spider data
  to agents" plus the two identically-named `SpiderAgentConnector`
  classes create serious naming collision + duplicate-model drift.
  **This is P3's territory (Cat C Cross-Substrate Composition
  Design)** — recorded here for inheritance.

## 17. Duplicate or Overlapping Systems

- **F11 — three substrates for spider-data → agents (SIGN-expanded).**
  See §16. THREE substrates carry conceptually the same signal
  ("new spider data available") with incompatible durability + fan-out
  semantics + two of them share the class name `SpiderAgentConnector`
  in different Django apps. P3 will design the separation contract
  including the naming-collision de-duplication.
- **`EventHandlerRegistry.dispatch` handler-per-event_type vs
  worker `streams=[...]` subscription.** Both mechanisms exist:
  handler dispatch is by `event_type` string, worker subscription is
  by stream. F8 (`SYSTEM_ALERT` handler registered but no worker
  subscribes to the stream) is the concrete drift this dual-mechanism
  creates. Recommend either (i) collapsing to a single mechanism
  (subscribe-by-event_type OR subscribe-by-stream), or (ii)
  documenting the two-layer contract explicitly — P4 CONSOLIDATION
  candidate.

## 18. Ownership Gaps

- **No named DLQ owner.** Nothing consumes DLQ, nothing alerts on DLQ
  growth. If DLQ fills, nothing outside a manual `xlen` inspection
  will notice. Recommend P3 or a post-arc T-slot owner (probably the
  Group 1700 Observability arc).
- **No named schema-registry owner.** Each publisher wrapper owns its
  own payload shape by convention. If a wrapper is modified, no
  registry or CI check catches consumer-side impact. P2 will pick the
  go-forward policy; the owner is TBD at that point.
- **No named handler-failure retry policy owner.** F14 loop has no
  designated owner. This is the highest-leverage post-arc T-slot for
  ops hardening — flag for post-arc queue.
- **Consumer registration is code-side, not config-side.** Adding a
  new consumer group requires editing `event_handlers.py` factory
  functions + `core/tasks.py` beat-task wrapper + `core/settings.py`
  task-route + `PeriodicTask` row. No single-file config or admin
  UI. P3 territory.

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows:

1. **P2 will consume this doc as its baseline** — no separate audit
   needed for HAI event schema design; the α column of §10.2 + the γ
   current-state finding are P2's starting point.
2. **F9 root-cause investigation** (post-arc T-slot, HIGH priority):
   Why are the 4 consumer beat tasks unscheduled? Options: (a) beat
   sync command bug (see `feedback_audit_findings_12_canonical_celery_deferred_list.md`
   §12 for related deferred-by-policy patterns), (b) intentional
   dormancy pending downstream work, (c) drift from a prior cleanup
   pass. Recommend: audit `AUDIT_FINDINGS.md` §12 for prior
   `process_event_bus_*` entries; run `python manage.py
   audit_celery_zero_fire` (S1245) to verify beat-side status;
   cross-check `Procfile` + `Makefile celery` target parity per
   `feedback_procfile_makefile_queue_parity.md`.
3. **F14 handler-failure retry policy design** (post-arc T-slot,
   MEDIUM-HIGH priority): design an at-most-N-retries + move-to-DLQ
   contract. Coordinate with P2 schema-versioning policy (retries
   only make sense if consumers can distinguish transient from
   permanent failures — schema_version disambiguates).
4. **F11 second pub/sub surface reconciliation** — **inherit to P3**
   (Cat C Cross-Substrate Composition Design) per parent §5.3
   6-substrate separation contract mission.
5. **F17 replay-as-regression-tool** (post-arc T-slot, LOW-MEDIUM):
   ship a management command + test harness that seeds a Redis
   Stream + runs a worker + asserts consumer output. Enables Cat B
   post-implementation validation for P2's HAI event contract.
6. **F18 handler decorativeness audit** (post-arc T-slot, LOW):
   determine whether the 6 log-only handlers reflect design intent
   (analytics + Discord notifications only) or drift from a fuller
   analytics-writing intent. If the latter, spec the missing model
   writes.
7. **F16 DLQ retention + alerting design** — inherit to Group 1700
   Observability follow-on work (already in the joint retention ADR
   queue per parent §5.2 references to Group 1700 T0/Gate).

## 20. Appendix

### 20.1 Files inspected (direct file:line reads)

- `core/services/event_bus.py` (full — 729 lines).
- `core/services/event_handlers.py` (full — ~552 lines).
- `core/services/scoring_dispatcher.py` (lines 1-100, plus targeted
  grep on `_publish_scoring_event`).
- `core/services/hitl_validation.py` (lines 1-80).
- `core/tasks.py` (lines 4720-4900 — the 5 EventBus Celery tasks +
  narrative-drift boundary).
- `core/celery.py` (targeted grep on `event_bus` / `claim_stale`).
- `core/settings.py` (targeted grep on `process_event_bus` /
  `get_event_bus_stats`).
- `ai_core/agents/spider_agent_connector.py` (lines 290-430) — F11
  second-substrate verification.
- `docs/research/platform/cross_domain_integration_audit.md` (targeted
  lines 373-380 + 949-996).
- `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md`
  (targeted lines 113 + 247 + 428-464 + 577).
- `docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md`
  (parent) — full read via §1 + §5.1 + §5.2 + §5.3 + §7.

### 20.2 Grep patterns used

- `publish_spider_data_event|publish_opportunity_scored_event|publish_validation_required_event|publish_validation_decided_event|publish_outcome_recorded_event|publish_model_trained_event|publish_system_alert_event|publish_opportunity_created_event` — publisher wrapper call-site sweep across `**/*.py`.
- `EventStream\.SPIDER_DATA|EventStream\.OPPORTUNITY_CREATED|EventStream\.OPPORTUNITY_SCORED|EventStream\.VALIDATION_REQUIRED|EventStream\.VALIDATION_DECIDED|EventStream\.OUTCOME_RECORDED|EventStream\.MODEL_TRAINED|EventStream\.SYSTEM_ALERT` — direct enum reference sweep.
- `bus\.publish\(|get_event_bus\(\)\.publish\(|event_bus\.publish\(|EventBus\(\)\.publish\(` — direct-publish sweep (bypass-wrapper).
- `dead_letter|DEAD_LETTER|mi:dead_letter` — DLQ read/write sweep.
- `from core\.services\.event_bus import|from core\.services import event_bus|import event_bus` — importer sweep.
- `schema_version|SCHEMA_VERSION|schemaVersion` in `core/services/event_bus.py` — γ posture check.
- `assert.*event\.data|assert.*event_data|assert data\.get|assert data\[` in `core/` — β posture check.
- `process_event_bus_scoring_queue|process_event_bus_validation_queue|process_event_bus_analytics_queue|get_event_bus_stats` in `**/*.py` — consumer task caller sweep.

### 20.3 ORM probes

- `PeriodicTask.objects.filter(task__endswith='<task>').values_list('name', 'task', 'enabled')` for each of the 5 EventBus consumer tasks. Result: only `claim_stale_events` returns 1 row; the other 4 return `NONE`.

### 20.4 Unresolved unknowns

- None. Zero-UNKNOWN attestation held (Rigby S2001 SIGN emphasis #1
  satisfied). Every stream × direction pair has an evidence-backed
  STRONG / WEAK / MISSING classification.

### 20.5 Conflicts between sources

- S1273 §3.31 said `publish_model_trained_event` producer UNKNOWN.
  Actual: wrapper defined at `event_bus.py:665`; 0 callers → MISSING.
  Corrected in F7.
- S1274 §6.2 said DLQ accumulates unbounded. Actual: `maxlen=1000` at
  `event_bus.py:471` bounds DLQ. Corrected in F16.
- `cross_domain_integration_audit.md` lines 373-380: 6 of 7 pairs
  classified UNKNOWN pending caller sweep. This audit resolves all
  pairs; zero UNKNOWN remaining.
- `employee_os_communication_substrate_audit.md:135` says "6 named
  streams + DLQ". Actual: 8 named streams + DLQ. Recommend
  correction (P4 CONSOLIDATION anchor-update recommendation).

### 20.6 Verifier-loop corrections (Rigby SIGN cycle 1)

Rigby SIGN cycle 1 pre-commit on arc pin `pa-dd7e973617da464d`,
batched to 3 highest-leverage findings per
`feedback_rigby_sign_worker_instability_recovery` large-audit
hygiene. Verdicts + folds:

- **Q1 F9 (consumer beat dormancy, CRITICAL) — CONFIRMED.** Rigby
  `scheduled_tasks_tool` ORM probe returned zero rows for filter
  `event_bus` / `process_event_bus` / `event bus`. Filter
  `claim_stale_events` returned exactly one enabled row:
  `claim-stale-events` @ `cron(*/5 * * * *)`, `total_runs=4983`,
  `last_run=2026-07-04T20:20:00Z`. **F9 stands as CRITICAL** — no
  bootstrap sync or beat_schedule enrollment; the 4 process_event_bus_*
  + get_event_bus_stats tasks are genuinely dormant at runtime,
  matching the code-side observation that `core/celery.py:532` is
  the only entry in the code-defined beat_schedule.

- **Q2 F7 (MODEL_TRAINED wrapper 0 callers → MISSING, corrects
  S1273 §3.31 UNKNOWN) — CONFIRMED + STRENGTHENED.** Rigby
  `repo_tool.search("publish_model_trained_event")` returned 1
  file: `core/services/event_bus.py:665` (definition only).
  Rigby's `model_trained` search matched 7 files but none emit via
  EventBus — `ml_pipeline/enhanced_ml_pipeline.py` uses
  `_is_model_trained` as an internal bool check on model state,
  not an event emission. Rigby's `retrain` search surfaced
  `train_ml_scoring_model` at `core/tasks.py:2221` and
  `_impl_train_ml_scoring_model` at `core/tasks_financial.py:32`
  as the real retrain path. Direct read of :32-201 verified: (i)
  writes `MLModelVersion.objects.create(...)` at :157-168 with
  version + training_samples + train_r2 + test_r2 +
  feature_importance — all fields MODEL_TRAINED would carry; (ii)
  never calls `publish_model_trained_event`. **F7 verdict
  strengthened** — see verifier_loop (n) above. Corresponding
  update: §14 Known Drift + §20.7 F7 row.

- **Q3 F11 (second pub/sub surface, boundary_violation MEDIUM) —
  CONFIRMED + EXPANDED to THIRD substrate.** Rigby's Q3 attempt
  hit a `repo_tool` timeout so parent Claude did the grep sweep
  directly. Result: `SpiderAgentConnector` grep returns
  callers in `ai_core/agents/concrete_executor.py:637-638` +
  `core/views_agent_intelligence.py:352,355` for the ai_core
  variant, AND callers in `core/tasks_spiders.py:260,307` +
  `core/tasks.py:1355,1359` +
  `core/management/commands/process_spider_data.py:6,16` +
  `core/management/commands/activate_spiders.py:10,234` for a
  SECOND class in `intelligence/spider_agent_connector.py:20`.
  Direct read of `intelligence/spider_agent_connector.py:1-100`
  verified: this class does NOT use Redis pub/sub OR EventBus —
  it uses an in-process `Dict[str, List[str]]` category → agent
  keyword mapping (`_build_routing_map` at :31). **F11 verdict
  expanded from "two substrates" to "three substrates for spider-
  data → agents" — EventBus (dormant), ai_core pub/sub (2
  callers), intelligence in-process routing (6 caller sites).**
  Corresponding update: §16 + §17 + §20.7 F11 row (rewritten).

**Zero-UNKNOWN attestation held post-SIGN** — Rigby's Q1 + Q2
folds confirmed both classifications; Q3 expanded but did not
introduce a new UNKNOWN (third substrate documented explicitly).

**Rigby SIGN cycle 1 confidence:** CLEAN with 3 folds landed
pre-commit (per parent S2000 §15 stage-table cycle-1 discipline).
Arc pin `pa-dd7e973617da464d` preserved (not retired) per playbook
§16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED at S1999
close.

### 20.7 Finding index (F1–F18)

| ID | Finding | Type | Risk |
|---|---|---|---|
| F1 | `SPIDER_DATA` producer wrapper defined but has 0 non-definition callers; consumer subscribed but beat dormant | `missing_connection` | LOW |
| F2 | `OPPORTUNITY_CREATED` has NO publisher wrapper at all; dormant consumer subscription | `dead_code` | LOW |
| F3 | `OPPORTUNITY_SCORED` producer STRONG (2 sites in scoring_dispatcher.py) but consumer beat dormant → effective WEAK | `missing_connection` | HIGH |
| F4 | `VALIDATION_REQUIRED` producer WEAK (1 site in hitl_validation.py); consumer beat dormant | `missing_connection` | HIGH |
| F5 | `VALIDATION_DECIDED` producer WEAK (1 site); consumer beat dormant | `missing_connection` | HIGH |
| F6 | `OUTCOME_RECORDED` producer wrapper 0 callers; consumer beat dormant | `dead_code` | MEDIUM |
| F7 | `MODEL_TRAINED` producer wrapper (line 665) 0 callers → MISSING; corrects S1273 §3.31 UNKNOWN. **SIGN-strengthened:** real retrain path `_impl_train_ml_scoring_model` at `core/tasks_financial.py:32-201` writes `MLModelVersion.objects.create(...)` at :157-168 with the exact fields MODEL_TRAINED would carry (version + training_samples + train_r2 + test_r2 + feature_importance) but never calls the wrapper — bypasses EventBus for ORM. Consumer beat also dormant per F9 | `dead_code` / `drift` | MEDIUM (raised from LOW at SIGN) |
| F8 | `SYSTEM_ALERT` producer wrapper 0 callers + **no worker subscribes to the stream** — double MISSING despite `alert_error`/`alert_critical` handlers being registered by `event_type` | `dead_code` / `drift` | LOW |
| F9 | 3 of 5 EventBus consumer Celery tasks unscheduled at runtime (0 `PeriodicTask` rows); entire consumer surface dormant | `dead_code` | CRITICAL |
| F10 | `get_event_bus_stats` also unscheduled → no substrate-level monitoring visibility | `drift` | MEDIUM |
| F11 | **THREE substrates for spider-data → agents (SIGN-expanded from two):** (i) EventBus `publish_spider_data_event` — dormant, 0 callers. (ii) `ai_core/agents/spider_agent_connector.py:40:SpiderAgentConnector.publish_spider_data` at :311 — raw `redis.publish()` on `self.channels['spider_data']`, 2 real callers (`concrete_executor.py:637-638` + `views_agent_intelligence.py:352,355`). (iii) `intelligence/spider_agent_connector.py:20:SpiderAgentConnector` — completely separate class, in-process `Dict[str, List[str]]` routing (no pub/sub, no Redis), 6 real caller sites (`core/tasks_spiders.py:260,307` + `core/tasks.py:1355,1359` + 2 management commands). Two independent classes named `SpiderAgentConnector` in two apps | `boundary_violation` / `duplicate_model` | HIGH (raised from MEDIUM at SIGN) |
| F12 | No `schema_version` field stamped by any publisher wrapper — S1275 precedent not adopted; all 8 streams share an untracked schema | `drift` | HIGH |
| F13 | Zero runtime asserts on payload in production handlers; all use `data.get(key, default)` | `technical_debt` | HIGH |
| F14 | Handler-failure retry loop with no give-up: failed handler → no ACK → reclaimed every 60s → re-dispatched → same failure → infinite loop | `technical_debt` | HIGH |
| F15 | DLQ blind to handler failures — `_move_to_dead_letter` only called on parse errors at `event_bus.py:275`; F14 loop never reaches DLQ | `technical_debt` | HIGH |
| F16 | DLQ bounded at `maxlen=1000` (corrects S1274 §6.2); no reader consumes DLQ contents; no alerting on DLQ growth | `drift` | LOW |
| F17 | `EventBus.replay()` method at `event_bus.py:311` has zero callers — replay surface exists but is not exercised by regression tests | `technical_debt` | LOW |
| F18 | 6 of 7 default handlers are decorative (log or log + Discord); only `handle_spider_data_event` queues a downstream Celery task | `drift` | MEDIUM |

### 20.8 Provenance chain (playbook §6 discipline)

- Parent: `2000_event_integration_architecture_domain_scoping.md` §5.1
  (Chris-ratified D95 4-child taxonomy + Rigby S2000 SIGN cycle 1 Q4
  fold α/β/γ/δ expansion).
- Ancestor audits inherited: S1273 §3.31 (EventBus inventory), S1274
  §12.1 (P0 producer/consumer map audit), S1275 (event schema
  versioning precedent), S1401 §10 (Revenue OPPORTUNITY_SCORED
  trace).
- Contributes forward to: P2 (S2002 HAI Event Contract Design) —
  inherits α/γ + F14/F15 constraints; P3 (S2003 Cross-Substrate
  Composition) — inherits F11 second-substrate; P4 (S2004 Cat F
  CONSOLIDATION) — inherits F8 dual-mechanism drift + F18 handler
  decorativeness; xx99 (S2099) — inherits F1–F18 for §2 What Arc
  Answered per-child rollup.
