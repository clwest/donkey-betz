---
title: "Group 2000+ — Cat C — Cross-Substrate Composition Design (S2003 P3)"
status: draft
session: 2003
child_slot: P3_cat_c
domain_slug: event_integration_architecture
research_group: 2000
mission_type: child_audit
date: 2026-07-04
authority: |
  P3 child audit under Group 2000+ Event / Integration Architecture arc.
  Scope inherited from parent scoping §5.3
  (`2000_event_integration_architecture_domain_scoping.md`), which
  itself consumes S1273 §3.31 (EventBus / Streams substrate paragraph
  + Observability separation-of-concerns paragraph), S2001 §16 (F11
  three-substrate boundary violation for spider-data → agents,
  SIGN-expanded), S2002 §7.9 (canonical + mirror emission policy for
  Class-1 governance events), S2002 §17.2 (per-event consumer
  registry), S2002 §17.3 (two-class retention posture Class-1 audit-
  forever + Class-2 bounded), and S2002 §20.9 (F.PER-USER-AUTHORITY-
  MECHANISM event-emission contract). Cat F.SYMBOL-MAPPING-STATUS-
  VERIFICATION inheritance from Group 1900 §19 lands here per parent
  §5.3.

  This doc is a **design-contract-shape** child audit under playbook
  §11.2's 20-section template (SIXTEENTH-consecutive application;
  SECOND design-contract-shape audit after S2002 in the arc-wide
  design-contract sequence). Its output is a canonical rule set — the
  6-substrate separation contract — with:

  - A separation-contract table naming per-substrate emission criteria.
  - An explicit intentional-dual-emission register consuming S2002
    §7.9 canonical + mirror as the founding case.
  - A duplicate-emission audit register with `intentional` vs `drift`
    classification per site.
  - A substrate × HAI-event mapping consuming S2002 §7 four candidate
    transitions.
  - A WebSocket ↔ EventBus overlap resolution recommendation.
  - A DLQ retention decision paired with Groups 1700 + 1800 T0/Gate
    joint retention ADRs.
  - A F.SYMBOL-MAPPING-STATUS-VERIFICATION audit against the S1274
    §10.3.1 four graduation triggers.

  Explicit non-scope, per playbook §14.5 no-implementation rule:
  - Does NOT re-open S2001 P1 producer/consumer map — consumes it
    as baseline (F11 explicitly inherited; F14/F15 handler-failure /
    DLQ gap explicitly inherited as constraint).
  - Does NOT re-open S2002 P2 HAI event schema design — consumes it
    as substrate-assignment input (D5 hybrid canonical+mirror per
    §7.9).
  - Does NOT re-open S1274 Symbol Mapping option selection — audits
    S1274 §10.3.1 four graduation triggers only; graduation decision
    itself remains Chris's per S1274 §10.3.1.
  - Does NOT execute the joint retention ADRs (R.OBSERVABILITY.
    RETENTION-UNIFIED-ADR + R.HAI.RETENTION-UNIFIED-ADR); these
    remain T0/Gate per S1899 §8.1 items 4 + 5. P3 recommends the
    DLQ posture that the joint ADR resolution should honor.
  - Does NOT design the per-user authority MECHANISM — that remains
    Group 1900 arc scope. P3 documents the substrate-assignment for
    the P.U.A. events per S2002 §20.9 provisional contract, but does
    not define resolution semantics.
  - Does NOT ship migrations, ORM changes, EventBus wrapper changes,
    WebSocket consumer changes, OpsRunEvent write-site changes,
    beat-schedule enrollment, or DLQ cleanup implementation.
  - Does NOT rotate arc pin `pa-dd7e973617da464d` — preserved through
    S2099 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-
    CONFIRMED-with-scope-guardrails.

  Load-bearing inheritance chain re-attested at S2003 open:
  - S1273 §3.31 EventBus / Streams substrate paragraph + Observability
    separation-of-concerns paragraph — canonical basis for the six
    substrates as distinct architectural surfaces.
  - S1274 §10.3.1 Symbol Mapping catastrophic-action graduation
    guardrail — four telemetry triggers Chris must decide against.
  - S2000 parent §5.3 4-verdict Chris-gate: separation contract,
    duplicate-emission cleanup priorities, DLQ retention posture,
    WebSocket ↔ EventBus canonical assignment.
  - S2001 §16 F11 SIGN-expanded: three substrates for spider-data
    → agents (raw redis.publish + in-process routing + EventBus
    dormant) — canonical duplicate-emission drift example.
  - S2001 §17 F8: `EventHandlerRegistry.dispatch` handler-per-
    event_type vs worker `streams=[...]` dual-mechanism drift.
  - S2001 §17.1 DLQ semantics + §17.2 §15 F14/F15 handler-failure
    invisibility + no DLQ reader — constraint on P3's DLQ retention
    recommendation.
  - S2002 §7.9 canonical + mirror emission policy (EventBus-first
    canonical + OpsRunEvent mirror for Class-1 governance).
  - S2002 §17.2 20-row consumer registry — inherited as source of
    truth for HAI candidate substrate assignments.
  - S2002 §17.3 two-class retention posture (Class-1 audit-forever
    + Class-2 MAXLEN=10000 bounded).
  - S2002 §20.9 F.PER-USER-AUTHORITY-MECHANISM three governance
    events (AUTHORITY_CHECK_EVALUATED + AUTHORITY_DECISION_OVERRIDDEN
    + AUTHORITY_POLICY_BOUND_TO_USER) provisional surface.
  - S1806 §10 six-plane learning-surface event-emission gap
    catalog — six plane events per S2002 §10 designed with
    substrate implication.
  - S1899 §8.1 T0/Gate items 4 + 5 (joint retention ADRs +
    source_kind enum ADR) — DLQ retention decision recommends but
    does not execute.
companion_docs:
  - docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md
  - docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md
  - docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/symbol_mapping_option_selection_design.md
  - docs/research/symbol_mapping_event_schema_design.md
  - docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md
  - docs/research/domains/human_attention/1899_human_attention_canonical_summary.md
  - docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/EVENT_SYSTEM_INVENTORY.md
verifier_loop: |
  Pre-Explore (playbook §14 MC-1 REQUIRED, CODIFICATION-CONFIRMED at
  S1899 close, extended through S2001 + S2002). Direct file:line reads
  before any sub-agent dispatch:

  (a) `EventStream` enum + wrapper set at `core/services/event_bus.py`
      — verified S2001 §1 baseline unchanged at S2003 open: 8 streams
      (SPIDER_DATA + OPPORTUNITY_CREATED + OPPORTUNITY_SCORED +
      VALIDATION_REQUIRED + VALIDATION_DECIDED + OUTCOME_RECORDED +
      MODEL_TRAINED + SYSTEM_ALERT) + DLQ (`mi:dead_letter`, line
      106) + 7 wrappers at :539/:559/:596/:619/:643/:665/:686 (no
      OPPORTUNITY_CREATED wrapper per S2001 F2).
  (b) WebSocket `channel_layer.group_send` sweep across all `**/*.py`
      — 40+ call sites confirmed at S2003 open across `ai_core/`,
      `intelligence/`, `core/`, `sports/`. Not a curated wrapper set;
      each site assembles its own `type` field routing to a consumer
      method. No canonical broadcast wrapper analogous to
      `publish_*_event`.
  (c) `CeleryTaskEvent` write sites — 7 grep hits, dominant call
      sites in `core/celery_telemetry.py` (signal handlers, 2 rows)
      + `core/models_celery_telemetry.py` (model helper, 1) +
      `core/services/td_handlers_gateway.py` (1). Non-runtime write
      sites: `core/tests/test_top_consumers.py` (3, tests). Canonical
      entrypoint: Celery `task_prerun` / `task_postrun` signals.
  (d) `LLMCallEvent` write sites — 4 grep hits, dominant call site
      is `core/services/llm_call_wrapper.py:LLMCallWrapper` (S1098
      arc). Model helper at `core/models_llm_telemetry.py`. Non-runtime
      writes: `tests/services/test_llm_call_event_watchdog.py` (1) +
      `core/tests/test_rigby_mission_delegation.py` (1). Canonical
      entrypoint: `LLMCallWrapper` context manager.
  (e) `OpsRunEvent` write sites — 25 grep hits across 12 files;
      dominant runtime writers: `core/employees/mission_runner.py`
      (2 sites, MissionRunner step boundaries + verdicts),
      `core/tools/ops_run_tracker.py` (1, OpsRun helper),
      `core/employees/jobs.py` (1, employee bootstrap),
      `core/models_ops_runs.py` (1, model helper),
      `core/signals/rigby_delegation_signals.py` (1, Rigby delegation
      signal handler), `core/services/rigby_mission_delegation.py`
      (1, Rigby delegation runtime),
      `core/services/td_handlers_rigby_work_queue.py` (1).
      Non-runtime write sites: 8 in `core/tests/*`. Highest
      scatter of all telemetry substrates but bounded by intentional
      audit boundaries (mission steps, delegation checkpoints).
  (f) `ToolCallRecord` write sites — 6 grep hits, dominant runtime
      writer: `core/services/tool_dispatcher.py:ToolDispatcher` (S861
      arc). Model helper at `core/models_tool_calls.py` (2). Non-
      runtime writes: `core/tests/test_deliverable_provenance.py` (2)
      + `core/services/unified_pa_entrypoint.py` (1). Canonical
      entrypoint: `ToolDispatcher.dispatch_tool_call` + PA agentic
      loop.
  (g) F11 three-substrate spider-data topology re-verified per S2001
      §16: (i) `ai_core/agents/spider_agent_connector.py:311:
      SpiderAgentConnector.publish_spider_data` uses raw
      `redis.publish()` on `self.channels['spider_data']` (real
      callers: `ai_core/agents/concrete_executor.py:637-638`,
      `core/views_agent_intelligence.py:352,355`); (ii)
      `intelligence/spider_agent_connector.py:20:SpiderAgentConnector`
      (same class name, different app, DIFFERENT implementation) uses
      an in-process `Dict[str, List[str]]` category → agent-keyword
      mapping (real callers: `core/tasks_spiders.py:260,307`,
      `core/tasks.py:1355,1359`, `core/management/commands/
      process_spider_data.py:6,16`, `core/management/commands/
      activate_spiders.py:10,234`); (iii) EventBus `SPIDER_DATA` +
      `publish_spider_data_event` wrapper is dormant (0 non-
      definition callers per S2001 F1).
  (h) S1274 §10.3.1 four Symbol Mapping graduation triggers re-read:
      trigger 1 = Tier-0 hazard observed ≥1 time
      (`open_pull_request` / `delete_database_rows` /
      `execute_arbitrary_code` / `access_secret_values`); trigger 2
      = PROHIBITED-level violation rate > 0 per employee per 14-day
      window; trigger 3 = Symbol Mapping NULL `action_class` rate >
      30% after Phase 4 (per-employee dry run); trigger 4 = ≥90 days
      elapsed since Phase 5 without downstream layer decision.
  (i) S1273 §3.31 substrate paragraph + Observability separation-of-
      concerns paragraph re-read: EventBus = "runtime coordination"
      (push-with-consumers, asynchronous reaction); Observability
      substrates = "evidence-after-the-fact" (write-and-query, audit
      rows written *after* the event fires). "Some semantic surface
      overlap with WebSocket consumer message types (both broadcast
      realtime state); relationship undocumented." — the exact drift
      item S2003 must resolve.
  (j) S2002 §7.9 canonical + mirror re-read: EventBus canonical +
      OpsRunEvent mirror ONLY for Class-1 governance events (HAI
      four candidate transitions + F.PER-USER-AUTHORITY three
      governance events per §20.9); Class-2 default = canonical-
      EventBus-only. Same `event_id` (envelope UUID) ties canonical
      + mirror; ordering enforced via `transaction.on_commit`.
  (k) S2002 §17.2 twenty-row consumer registry re-read: 4 HAI-
      candidate rows + six-plane learning-surface rows + F.PER-USER-
      AUTHORITY row. `security_audit_consumer` REQUIRED across HAI_
      DECISION_RECORDED + HAI_AUTO_APPROVED + HAI_AUTO_ESCALATED
      per SIGN batch 2 Q5 FOLD. `ml_training_signal_consumer`
      REQUIRED on HAI_DECISION_RECORDED + HAI_VERIFICATION_RECORDED.
  (l) S2002 §17.3 two-class retention posture re-read: Class-1
      audit-forever (HAI_AUTO_APPROVED, HAI_AUTO_ESCALATED, F.PER-
      USER-AUTHORITY events → OpsRunEvent no TTL); Class-1 bounded-
      history (HAI_DECISION_RECORDED, HAI_VERIFICATION_RECORDED →
      EventBus MAXLEN=10000 + audit-table via HFR/HAI durable
      row); Class-2 bounded (plane events → EventBus MAXLEN=10000).
  (m) S1275 §7.5 substrate-change bump rules re-read: canonical-
      substrate change = major bump; mirror-add = minor bump;
      mirror-remove = minor bump. Applied to §17 duplicate-emission
      audit for drift-fix bump policy.
  (n) Prior-arc classifications inherited without re-verification
      (per playbook §14.5 no-re-inventory rule): S2001 F1-F18
      classifications for EventBus streams; S2002 D1-D5 decisions
      for HAI event contract; S1273 §3.31 EventBus substrate
      description.

  Sub-agent dispatches: NONE. All findings sourced from direct
  file:line reads + ORM probes + S2001/S2002 attested prior-arc
  classifications. Per playbook §14 Pre-Explore discipline: parent
  Claude verifier-loop is sufficient for cross-substrate composition
  design when the surface is bounded by the six named substrates +
  S2001 producer/consumer inventory + S2002 HAI event contract.
  Substrate write-site sweeps use `Grep(type=py)` for
  `CeleryTaskEvent(` / `LLMCallEvent(` / `OpsRunEvent(` /
  `ToolCallRecord(` / `channel_layer.group_send(` / `publish_*_event(`
  + direct `event_bus.publish(` — coverage is exhaustive within the
  Django code corpus.

  Design-contract shape verifier (SIGN batch 4 Q12 STRENGTHEN from
  S2002 meta-methodology capture applied here): the substrate
  contract exposes a Contract Surface Matrix (§10.2 substrate ×
  event class) + a Consistency Invariants Checklist (§10.3
  intentional-dual-emission register). Both surfaces will be Rigby-
  SIGN-verified on the batched cycle per playbook §15 stage-table
  design-contract row + parent §5.3 cadence.

  Zero-UNKNOWN attestation (Rigby S2001 SIGN emphasis #1 extended):
  every one of the 6 named substrates + F11 raw-redis-publish drift
  substrate has a per-criterion classification in §10.2. Every
  duplicate-emission site in §17 classifies as `intentional`,
  `drift`, or `unresolved (Chris-gate pending)`.
owner: claude (drafted S2003; Rigby SIGN-with-edits pending at commit-gate)
---

# Session 2003 — Group 2000+ Cat C — Cross-Substrate Composition Design

> **SECOND design-contract-shape audit under Group 2000+ Event / Integration Architecture arc + SIXTEENTH-consecutive application of playbook §11.2 20-section child template.** Playbook §11.2 20-section child audit template SIXTEENTH-consecutive application (after S1601 Cat B Content + S1602 Cat B Content Reviewers + S1603 Cat C + S1604 Cat D + S1605 Cat E + S1606 Cat F + S1701 Cat A + S1702 Cat B + S1703 Cat C + S1704 Cat F + S1901 Cat A + S1902 Cat B + S1903 Cat C + S1904 Cat F + S2001 Cat A + S2002 Cat B). SECOND design-contract-shape audit after S2002 (SIGN batch 4 Q12 STRENGTHEN meta-methodology capture applied here).

## 1. Executive Summary

The Donkey Betz platform has **six named event-emitting substrates** — EventBus (Redis Streams, `core/services/event_bus.py:90`), WebSocket (Django Channels `channel_layer.group_send`), CeleryTaskEvent (`core/models_celery_telemetry.py:17`), LLMCallEvent (`core/models_llm_telemetry.py:30`), OpsRunEvent (`core/models_ops_runs.py:117`), and ToolCallRecord (`core/models_tool_calls.py:19`) — plus **one de-facto drift substrate**: raw `redis.publish()` pub/sub on `SpiderAgentConnector.publish_spider_data` (`ai_core/agents/spider_agent_connector.py:311`, per S2001 F11 SIGN-expanded). This audit designs the canonical composition contract that answers *"when does a new emission go to which substrate?"* — the parent §5.3 P3 mission and the S1273 §3.31 known-drift resolution.

**Headline 1 — Substrates split cleanly along the runtime-coordination-vs-audit-after-the-fact axis established at S1273 §3.31.** EventBus (Redis Streams) and WebSocket (Channels group_send) are **push-with-consumers substrates**: a producer emission causes a downstream consumer to *react at execution time*. CeleryTaskEvent, LLMCallEvent, OpsRunEvent, and ToolCallRecord are **write-and-query telemetry substrates**: a producer emission is *evidence-after-the-fact*, read later by dashboards, PA tools, and investigation queries. The separation contract (§10.2) codifies this split as **Axis A: coordination vs telemetry** and derives per-substrate criteria on top of it.

**Headline 2 — The push-with-consumers substrates overlap on realtime state broadcast; the canonical assignment picks EventBus for cross-service state changes and WebSocket for browser-facing UI updates.** S1273 §3.31 flagged this as undocumented drift. §10.5 audits the specific overlap sites (40+ `channel_layer.group_send` call sites vs 2 non-definition `publish_*_event` callers) and D4 recommends: **canonical assignment by consumer audience** — cross-service backend consumer → EventBus; browser session-scoped consumer → WebSocket; both required → EventBus canonical + WebSocket UI-render fanout (documented as an intentional dual-emission per §7.9 canonical + mirror generalization).

**Headline 3 — Duplicate-emission audit surfaces one intentional pattern (S2002 §7.9 canonical + mirror for Class-1 governance) + one confirmed drift (F11 three-substrate spider-data) + zero currently-observed accidental telemetry duplication.** §17.1 documents the intentional case: HAI Class-1 events emit to EventBus (canonical) AND OpsRunEvent (audit mirror) with equal `event_id`. §17.2 documents the drift case: F11's three parallel substrates for "route spider data to agents." §17.3 documents zero confirmed accidental telemetry substrate collisions at S2003 open — CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord write from distinct call sites for distinct concerns.

**Headline 4 — DLQ retention recommendation: TTL-bounded per Class-2 posture (MAXLEN=10000 per S2002 §17.3) with an audit-critical override trigger — but the entire DLQ semantics remain constrained by S2001 F14/F15.** F14 (handler-failure retry loop with no give-up) + F15 (no DLQ reader / no alerting) mean DLQ retention is not yet the correctness surface. §15 pairs the recommendation with the joint retention ADR handoff (R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.HAI.RETENTION-UNIFIED-ADR remain T0/Gate per S1899 §8.1). D3 recommends: **DLQ = MAXLEN=1000 (current EventBus posture at `event_bus.py:468`) + explicit joint-ADR override slot for audit-critical DLQ growth signalling.**

**Headline 5 — F.SYMBOL-MAPPING-STATUS-VERIFICATION audit: all four S1274 §10.3.1 graduation triggers are GREEN at S2003 open with one warn-mode observation on trigger 4 (elapsed time).** §19.1 audits: trigger 1 (Tier-0 hazard observed ≥1) = GREEN (no Tier-0 emission observed); trigger 2 (PROHIBITED-level violation rate > 0) = GREEN (no PROHIBITED emission observed); trigger 3 (Symbol Mapping NULL rate > 30% after Phase 4) = NOT-YET-EVALUABLE (Phase 4 per-employee dry run not yet run at S2003 open); trigger 4 (≥90 days elapsed since Phase 5) = WARN-MODE-CANDIDATE (Phase 5 all-employee steady state date not confirmed at S2003 open; if Phase 5 close date is pre-2026-04-04, trigger 4 approaches fire). Recommendation: **extend E-only for 90 days from S2003 close (2026-10-04) OR run Phase 4 dry run to lock trigger 3 baseline** — Chris ratifies at close per Chris-gate (b).

**Load-bearing decisions D1-D5** (Chris-gate at close per parent §5.3):

- **D1 (separation contract)** — Axis A (coordination vs telemetry) + Axis B (canonical audience) + Axis C (retention class) as canonical selectors; per-substrate criteria table in §10.2.
- **D2 (duplicate-emission cleanup priorities)** — F11 three-substrate spider-data drift ranked HIGH cleanup priority (parent §5.3 Chris-gate (b)); rest of the duplicate audit shows no drift requiring T0/Gate work — recommend post-arc T1 slot for F11 substrate consolidation.
- **D3 (DLQ retention posture)** — MAXLEN=1000 current EventBus posture retained; explicit joint-ADR override slot documented for audit-critical DLQ growth. Bounded-history Class-2 posture per S2002 §17.3.
- **D4 (WebSocket ↔ EventBus canonical assignment)** — Cross-service backend state → EventBus canonical; browser session-scoped UI state → WebSocket canonical; both required → EventBus canonical + WebSocket UI-render fanout (documented dual-emission per §7.9 generalization).
- **D5 (F.SYMBOL-MAPPING graduation status)** — GREEN across triggers 1 + 2; NOT-YET-EVALUABLE on trigger 3; WARN-MODE-CANDIDATE on trigger 4 pending Phase 5 date confirmation. Recommend 90-day extension from S2003 close date (2026-10-04) OR Phase 4 execution to lock trigger 3 baseline.

Runtime target: 1 session. Rigby SIGN cadence: cycle 1 pre-commit per parent §5.3 + playbook §15 stage-table design-contract row. Chris-gate: multi-verdict at close for (a) separation contract, (b) duplicate-emission cleanup priorities, (c) DLQ retention posture, (d) WebSocket ↔ EventBus canonical assignment, per parent §5.3.

## 2. Domain Purpose

**Q1 — What is this domain?**

Cross-substrate composition governs the arbitration rule set for the six event-emitting substrates in the Donkey Betz runtime: **EventBus** (Redis Streams pub/sub), **WebSocket** (Django Channels realtime browser broadcast), **CeleryTaskEvent** (Celery task lifecycle telemetry), **LLMCallEvent** (LLM call telemetry per S1098), **OpsRunEvent** (Employee OS mission-step audit trail), and **ToolCallRecord** (PA tool dispatch audit per S861). It is the substrate-level *composition contract* — distinct from event schema design (P2 / S2002) and distinct from producer/consumer topology (P1 / S2001). Where a producer needs to emit an event, the composition contract answers "which substrate?" and, when the answer is more than one, "which is canonical and which is the mirror?".

The composition contract sits above the six substrates as a **cross-cutting design surface**: no substrate owns it, and no runtime enforces it. It exists as documentation + adoption discipline. Enforcement happens through code review, per-substrate wrapper adoption (analogous to S2002 §7.9 shared wrapper mandate), and drift audits — the exact shape this doc establishes.

**Q2 — What are the biggest gaps?**

Three gaps drive P3's mission:

1. **No canonical arbitration rule set exists at S2003 open.** Each substrate was born from a distinct historical need (EventBus from Session 470 opportunity pipeline; WebSocket from Session 100s workspace realtime; CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord from telemetry-buildout arcs S861/S1098/S1234); no composition doc named the criteria for picking one over another. Adoption drift shows itself as F11 (three substrates for one logical signal) + S1273 §3.31's undocumented WebSocket ↔ EventBus semantic overlap.

2. **F11 three-substrate spider-data drift is the canonical unresolved case.** SIGN-expanded per S2001 §16: raw `redis.publish()` pub/sub + in-process `SpiderAgentConnector` routing table + dormant EventBus `SPIDER_DATA` stream. Three architecturally distinct substrates share the purpose "route spider data to agents"; two of them share a class name (`SpiderAgentConnector`) in different Django apps. No prior arc has arbitrated the go-forward canonical substrate.

3. **DLQ retention policy has no canonical decision at S2003 open + F14/F15 handler-failure gap blocks correctness.** DLQ receives parse-error paths only (S2001 §17.1); handler failures do not reach DLQ (F14); no worker reads DLQ (F15). Retention TTL/MAXLEN policy is not the correctness surface until F14 + F15 close. But the joint retention ADRs (R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.HAI.RETENTION-UNIFIED-ADR) at S1899 §8.1 items 4 + 5 need P3's substrate posture recommendation as input.

**Sub-goal from parent §5.3:** In addition to the composition contract itself, P3 audits **F.SYMBOL-MAPPING-STATUS-VERIFICATION** (inherited from Group 1900 §19 / S1903 §19 P3 hand-off): the four S1274 §10.3.1 graduation triggers (Tier-0 hazard observed ≥1 time; PROHIBITED-level violation rate > 0; Symbol Mapping NULL rate > 30% after Phase 4; ≥90 days elapsed since Phase 5). §19.1 executes the audit; §19.1 recommendation feeds Chris-gate D5.

## 3. Canonical Entry Points

**Q3 — Where does substrate emission enter runtime code?**

Per-substrate canonical emission entry points:

| Substrate | Canonical entry point | file:line | Public API shape |
|---|---|---|---|
| EventBus | `EventBus.publish(event, stream)` | `core/services/event_bus.py:137` | Domain-typed wrappers `publish_spider_data_event()` (:539), `publish_opportunity_scored_event()` (:559), `publish_validation_required_event()` (:596), `publish_validation_decided_event()` (:619), `publish_outcome_recorded_event()` (:643), `publish_model_trained_event()` (:665), `publish_system_alert_event()` (:686). **Direct `.publish(...)` bypass is a defect** (7 non-wrapper hits all inside wrapper bodies per S2001 verifier_loop (d)). |
| WebSocket | `self.channel_layer.group_send(group_name, dict)` | Not centralized — see §16 boundary violation | ~40 non-test call sites; each site assembles its own `type` field routing to a consumer method. **No canonical broadcast wrapper analogous to `publish_*_event`.** |
| CeleryTaskEvent | `CeleryTaskEvent.objects.create(...)` via Celery `task_prerun` / `task_postrun` signal handlers | `core/celery_telemetry.py` (signal handlers) + `core/models_celery_telemetry.py:17` (model) | Signal-driven; production callers do not write CeleryTaskEvent directly. Non-signal call site: `core/services/td_handlers_gateway.py` (1, gateway audit). |
| LLMCallEvent | `LLMCallWrapper` context manager (S1098) | `core/services/llm_call_wrapper.py:LLMCallWrapper` + `core/models_llm_telemetry.py:30` (model) | Context-managed; `LLMCallWrapper` wraps the OpenAI/Anthropic/Together call and writes pre-call / post-call rows. Non-wrapper direct writes are a defect. |
| OpsRunEvent | `OpsRun.append_event(...)` or direct `OpsRunEvent.objects.create(...)` per `mission_runner.py` step boundaries | `core/employees/mission_runner.py` (2 sites, MissionRunner step boundaries + verdicts) + `core/models_ops_runs.py:117` (model). Auxiliary writers: `core/tools/ops_run_tracker.py`, `core/employees/jobs.py`, `core/signals/rigby_delegation_signals.py`, `core/services/rigby_mission_delegation.py`, `core/services/td_handlers_rigby_work_queue.py`. | Not context-managed at S2003 open; MissionRunner is the dominant caller. Highest scatter of all six substrates (7 runtime sites across 6 files) but bounded by intentional audit boundaries. |
| ToolCallRecord | `ToolDispatcher.dispatch_tool_call(...)` (S861) | `core/services/tool_dispatcher.py:ToolDispatcher` + `core/models_tool_calls.py:19` (model) | Dispatcher-managed; PA agentic loop is the dominant caller path (`core/services/unified_pa_entrypoint.py` also writes 1 site for enrichment audit). |

**Drift substrate (F11 boundary violation, per S2001 §16 SIGN-expanded):**

| Substrate | Entry point | file:line | Status |
|---|---|---|---|
| Raw `redis.publish()` on `self.channels['spider_data']` | `SpiderAgentConnector.publish_spider_data` | `ai_core/agents/spider_agent_connector.py:311` | **DRIFT — not sanctioned.** Real callers: `ai_core/agents/concrete_executor.py:637-638`, `core/views_agent_intelligence.py:352,355`. Bypasses EventBus wrapper + Streams durability. §16 recommends canonical migration to `publish_spider_data_event` (F11 T1 slot). |

**Non-emitting write-only substrates (documented for completeness — not in composition contract scope):**

| Substrate | Purpose | Note |
|---|---|---|
| `AgentExecution` ORM row | Per-agent invocation record | Written by `BaseAgent.execute` (`core/agents/base_agent.py`); read-side is the agent-execution history projection. Telemetry-only; no downstream consumer reacts to the write. |
| `Deliverable` ORM row | Content-pipeline output | Written by content deliberation runner. Distinct from event emission. |
| `TriggerEvent` / `ImpactEvent` / `DeliverableEvent` | Existing named event tables per S1273 §3.25 | Written by domain-specific hooks; each carries its own retention policy. **Not** substrates in the composition contract sense (§10.2 Axis A criteria); they are audit-object states, not push-with-consumers or write-and-query telemetry. Cross-referenced in §17 for the sake of the duplicate-emission audit. |

**Substrate registration boundaries (§10.2 Axis A precursor):**

Per S1273 §3.31 substrate paragraph, the composition contract recognizes **two structural roles** across the six named substrates:

- **Push-with-consumers substrates:** EventBus, WebSocket. Emission causes a downstream consumer to *react* at execution time. Consumer discovery is via Redis Streams `xreadgroup` (EventBus) or Channels group subscription (WebSocket).
- **Write-and-query telemetry substrates:** CeleryTaskEvent, LLMCallEvent, OpsRunEvent, ToolCallRecord. Emission writes an audit row; readers are dashboards, PA tools, or investigation queries. No runtime reaction fires from the write.

The drift substrate (raw `redis.publish()`) is architecturally a push-with-consumers substrate (Redis pub/sub semantics) but is not sanctioned; §16 recommends deprecation.

## 4. Major Models

**Q4 — What ORM models back each substrate?**

The composition contract is a design surface layered over six substrate storage backings. Each substrate has a distinct backing:

| Substrate | Backing storage | ORM model / class | Retention default | Key fields |
|---|---|---|---|---|
| EventBus | Redis Streams (`mi:<stream_name>`) | `Event` dataclass at `event_bus.py:42` | MAXLEN=10000 per `event_bus.py:104` (Class-2) or per-event class per §17.3 | `event_type` str, `data` dict, `timestamp`, `priority` (LOW/NORMAL/HIGH/CRITICAL), `source` str, `correlation_id` str |
| EventBus DLQ | Redis Stream (`mi:dead_letter`) | Same `Event` shape | MAXLEN=1000 per `event_bus.py:468` | Same + `error_reason` string |
| WebSocket | In-memory Channels group buffer (no persistence) | No ORM row; message shape is a `dict` per `group_send` call site | Ephemeral (session lifetime) | `type` str (routing key to consumer method) + arbitrary payload keys per site |
| CeleryTaskEvent | PostgreSQL row | `CeleryTaskEvent` at `core/models_celery_telemetry.py:17-100` | 30-day TTL (S1223 close ratification) via cleanup task | `task_id`, `task_name`, `state`, `agent_name`, `rss_bytes_start/end`, `duration_ms`, `error_class`, `error_message` |
| LLMCallEvent | PostgreSQL row | `LLMCallEvent` at `core/models_llm_telemetry.py:30-100` | 30-day TTL (S1219 cleanup watchdog PR #2520) | `provider`, `model`, `finish_reason`, `input_tokens`, `output_tokens`, `duration_ms`, `total_tokens`, `agent_name`, `correlation_id`, `caller` |
| OpsRunEvent | PostgreSQL row | `OpsRunEvent` at `core/models_ops_runs.py:117` | No default TTL (audit-forever posture for Class-1 per S2002 §17.3) | `ops_run_id` FK, `event_type` str, `label` str, `payload` JSONField, `sequence` int, `occurred_at` |
| ToolCallRecord | PostgreSQL row | `ToolCallRecord` at `core/models_tool_calls.py:19` | 30-day TTL (S861 cleanup task) | `tool_name`, `agent_execution_id` FK, `input_data`, `output_data`, `success` bool, `error_message`, `duration_ms`, `caller` |
| Drift substrate (F11) | Redis pub/sub channel (`spider_data`) | No ORM; ephemeral | Ephemeral (pub/sub fire-and-forget) | JSON envelope via `SpiderDataPacket.to_dict()` at `spider_agent_connector.py:311-325` |

**Q5 — What auxiliary models participate in the composition contract?**

| Model | Role in composition | file:line |
|---|---|---|
| `EventStream` (enum) | Enumerates the 8 EventBus stream names + implicitly DLQ | `event_bus.py:21-30` |
| `EventPriority` (enum) | LOW/NORMAL/HIGH/CRITICAL priority values on `Event` | `event_bus.py:32-40` |
| `ConsumerInfo` (dataclass) | In-memory consumer registration (**decorative / unused per S2001 F18-adjacent** — flagged for P4 CONSOLIDATION) | `event_bus.py:80-87` |
| `SpiderDataPacket` | Wire envelope for the drift substrate F11 raw redis.publish() | `spider_agent_connector.py` (F11 substrate) |
| `OpsRun` | Parent row for OpsRunEvent (mission-level context) | `core/models_ops_runs.py:11-117` |
| `AgentExecution` | Non-substrate audit row, but joined by ToolCallRecord.agent_execution_id | `core/models.py:AgentExecution` |
| `MLModelVersion` | Referenced in S2001 F7: MODEL_TRAINED event's payload fields are written to this ORM instead of firing MODEL_TRAINED emission | `core/tasks_financial.py:157-168` (creation site) |

**Q6 — Which models are duplicate-emission candidates?**

Per §17 duplicate-emission audit:

- **Intentional dual-emission (S2002 §7.9 canonical + mirror):** `EventBus.SPIDER_DATA` + `OpsRunEvent` share event_id when a Class-1 governance event fires. `HAI_DECISION_RECORDED` + `HFR` audit-table row is a similar pattern but the HFR row is a domain-object state, not an event emission per se — recorded here for completeness but classified as "audit-table backing" not "dual-emission" per S2002 §8.1.
- **Drift dual-emission (F11 spider-data):** three substrates for one logical signal — see §16 + §17.
- **Latent duplicate-emission candidates (no observed collision at S2003 open):** telemetry substrates (CeleryTaskEvent, LLMCallEvent, OpsRunEvent, ToolCallRecord) can share a call trace — a Celery task that invokes an agent that dispatches a tool that calls an LLM writes rows to all four telemetry substrates in one execution. §17.3 classifies this as **parallel telemetry layers per concern** (not duplicate emission) — each row records a distinct concern (task lifecycle vs LLM call vs mission step vs tool dispatch); the `correlation_id` envelope field ties them together.

## 5. Major Services

**Q7 — Which services own the emission entrypoints?**

Per-substrate service ownership:

| Substrate | Owning service | Contract stewardship | Enforcement mechanism |
|---|---|---|---|
| EventBus | `EventBus` singleton (`event_bus.py:90`) + `event_handlers.py` consumer worker factories | Group 2000+ arc (P1 shipped baseline; P3 designs composition) | Shared publisher wrappers (`publish_*_event`); direct `.publish(...)` bypass is a defect (S2001 verifier_loop (d) attestation) |
| WebSocket | `channel_layer` provided by Django Channels + per-app consumer classes | **Ownership gap** (no arc has owned the WebSocket broadcast pattern) — recorded in §18 | No canonical broadcast wrapper; each `group_send` call site owns its own payload shape. F.WEBSOCKET-BROADCAST-WRAPPER T-slot candidate. |
| CeleryTaskEvent | Celery task-lifecycle signal handlers in `core/celery_telemetry.py` | Group 1700 Observability (S1704 Cat F) | `task_prerun` / `task_postrun` signal binding; direct create outside signals is a defect for runtime code (test writes exempted) |
| LLMCallEvent | `LLMCallWrapper` context manager (`core/services/llm_call_wrapper.py`, S1098 arc) | Group 1700 Observability (S1219 watchdog PR #2519, S1220 cleanup PR #2520) | `LLMCallWrapper.__enter__` / `__exit__` boundaries; direct create outside wrapper is a defect for runtime code |
| OpsRunEvent | `MissionRunner` orchestrator (`core/employees/mission_runner.py`) + Employee OS primitives per `docs/EMPLOYEE_OS_PRIMITIVES.md` | Employee OS arc (S1234 arc) + Group 1800 Human Attention (auto-approve mirror per S2002 §7.9) | `OpsRun.append_event(...)` or direct `OpsRunEvent.objects.create(...)` per mission-step boundary — no wrapper enforcement at S2003 open (F.OPSRUNEVENT-WRITE-WRAPPER post-arc T-slot candidate) |
| ToolCallRecord | `ToolDispatcher` (`core/services/tool_dispatcher.py`, S861 arc) | Group 1800 Personal Assistant (S861 Extended-PA arc) | `ToolDispatcher.dispatch_tool_call` boundary; direct create outside dispatcher is a defect for runtime code (PA entrypoint enrichment audit exempted with rationale) |
| Drift (F11) | `SpiderAgentConnector` (ai_core version) at `ai_core/agents/spider_agent_connector.py:40` | **Ownership gap** — no arc has owned deprecation. F11 recommends P3 T1-slot migration to `publish_spider_data_event` (deprecation) | Not enforced at S2003 open. §16 recommends migration + deletion. |

**Q8 — Which services consume emissions and react?**

Per S2002 §17.2 twenty-row consumer registry, inherited here without re-verification. Additional cross-substrate consumers for §10 composition context:

- **EventBus consumers:** 3 worker groups per S2001 §10.1(e) — `scoring_workers` (SPIDER_DATA + OPPORTUNITY_CREATED), `validation_workers` (OPPORTUNITY_SCORED + VALIDATION_REQUIRED), `analytics_workers` (VALIDATION_DECIDED + OUTCOME_RECORDED + MODEL_TRAINED). All 3 dormant on beat per S2001 F9.
- **WebSocket consumers:** Browser-side WebSocket clients per Django Channels consumer routing. Consumer classes at `ai_core/consumers/`, `intelligence/consumers*.py`, `core/consumers*.py`. Read-side is browser UI render — no server-side reaction beyond the render.
- **CeleryTaskEvent consumers:** `celery_task_history` PA tool (Rigby-callable read surface); Grafana dashboards; observability audit tools per S1230.
- **LLMCallEvent consumers:** LLM cost tracking dashboards (S1223 close pending); LLMCallEvent watchdog (S1219 PR #2519); reliability metrics per Session 1220.
- **OpsRunEvent consumers:** `governance_audit_view` per S2002 §17.2; PA `ops_tool.celery_task_history` (indirect via task_id join); Employee OS mission audit surface per `docs/topics/employee-os.md`.
- **ToolCallRecord consumers:** `tool_call_history` PA tool; ToolCallRecord observability projection per S861.
- **Drift substrate (F11) consumers:** `SpiderAgentConnector.request_spider_data` per `spider_agent_connector.py:340` (in ai_core version) reads from an in-process routing table (in `intelligence` version) — the two SpiderAgentConnector implementations do NOT share consumers. This is exactly the boundary violation flagged by F11.

## 6. Major APIs and Interfaces

**Q9 — What emission interfaces are exposed to producers?**

Producer-facing interfaces per substrate. This section names the *entry point + payload shape* that a caller uses to emit — not the internal storage semantics (§4).

**EventBus (canonical push-with-consumers substrate):**

Interface: `publish_<domain>_event(domain_specific_args, **envelope_kwargs) -> None`, defined at `event_bus.py:539/559/596/619/643/665/686`. Each wrapper:

1. Assembles `Event.data` dict from domain-specific args.
2. Sets `event_type` string constant.
3. Sets `source` string (default per-wrapper, overridable).
4. Sets `priority` (default NORMAL, overridable, or computed per-wrapper).
5. Calls `EventBus.publish(event, stream=EventStream.<STREAM>)` at line 137.

**Adopter contract obligation (P3 D1 recommendation):** all EventBus emissions MUST use a `publish_*_event` wrapper. Direct `event_bus.publish(...)` bypass is a defect. The S2001 verifier_loop (d) attestation confirms zero non-wrapper bypass at S2003 open — this posture must be preserved. **Post-arc T1 candidate: extend `publish_*_event` wrapper set to cover the four HAI candidate transitions per S2002 §6.2 shared wrapper mandate.**

**WebSocket (canonical push-with-consumers substrate — coordination with browser UI):**

Interface: `await self.channel_layer.group_send(group_name: str, message: dict) -> None`. No canonical wrapper at S2003 open — each of the ~40 call sites assembles its own message dict with a `type` field that routes to a consumer-class method.

**Adopter contract obligation (D4 recommendation):** WebSocket broadcasts SHOULD adopt a canonical wrapper analogous to `publish_*_event` for cross-cutting UI state broadcasts (e.g., `broadcast_workspace_state_update`, `broadcast_agent_progress`). Per-app one-off broadcasts (e.g., interview_consumer, sports realtime) may remain unwrapped as long as the message dict shape is documented in the consumer class. Post-arc T-slot candidate: F.WEBSOCKET-BROADCAST-WRAPPER.

**CeleryTaskEvent (canonical write-and-query telemetry substrate):**

Interface: implicit via Celery signal decorators (`@task_prerun.connect`, `@task_postrun.connect`) in `core/celery_telemetry.py`. Producer code (i.e., a Celery task body) does NOT write CeleryTaskEvent directly — the signal handler does. Direct writes outside signal handlers are permitted only for gateway audit (`core/services/td_handlers_gateway.py`) and tests.

**Adopter contract obligation:** production Celery tasks MUST NOT create CeleryTaskEvent rows directly. Signal-driven writes are the canonical path.

**LLMCallEvent (canonical write-and-query telemetry substrate):**

Interface: `with LLMCallWrapper(provider, model, agent_name, ...) as call: response = call.invoke(...)`. The wrapper context manager writes the pre-call row on `__enter__` and updates the post-call row on `__exit__`.

**Adopter contract obligation:** all LLM calls MUST use `LLMCallWrapper` context manager. Direct `LLMCallEvent.objects.create(...)` outside wrapper is a defect for runtime code.

**OpsRunEvent (canonical write-and-query telemetry substrate):**

Interface: `OpsRun.append_event(event_type, label, payload)` OR direct `OpsRunEvent.objects.create(ops_run=run, event_type=..., label=..., payload=...)`. No context-manager wrapper at S2003 open; MissionRunner writes at step boundaries.

**Adopter contract obligation (post-arc T-slot candidate F.OPSRUNEVENT-WRITE-WRAPPER):** consider adopting a `with OpsRun.step_boundary(...) as step:` context manager pattern analogous to `LLMCallWrapper` for step-level audit consistency.

**ToolCallRecord (canonical write-and-query telemetry substrate):**

Interface: `ToolDispatcher.dispatch_tool_call(tool_name, args, agent_execution_id) -> result`. The dispatcher writes ToolCallRecord row on entry and updates on completion.

**Adopter contract obligation:** all tool dispatches MUST use `ToolDispatcher`. Direct `ToolCallRecord.objects.create(...)` outside dispatcher is a defect (PA entrypoint enrichment audit exemption noted in §5).

**Drift substrate (F11 raw redis.publish() — deprecated):**

Interface: `self.redis_client.publish(self.channels['spider_data'], json.dumps(packet.to_dict()))` at `spider_agent_connector.py:322`.

**Adopter contract obligation (D2 cleanup priority):** deprecate. All spider-data emissions MUST migrate to `publish_spider_data_event` (canonical EventBus) per F11 T1 slot. Consumers (`ai_core/agents/concrete_executor.py:637-638`, `core/views_agent_intelligence.py:352,355`) must migrate to EventBus consumer group subscription or ORM read of persisted spider data.

## 7. Runtime Flows

**Q11 — How does an emission execute at runtime, per substrate?**

Per-substrate runtime flow at S2003 open, for the composition contract to reference.

### 7.1 EventBus emission runtime flow

```
Producer code
  → publish_<domain>_event(...)                             [event_bus.py:539..686]
  → EventBus.publish(event, stream)                         [event_bus.py:137]
  → Redis XADD to stream mi:<stream_name> with MAXLEN=10000 [event_bus.py:186]
  → metric increment: mi:metrics:events_published:<stream>  [event_bus.py:479]
Consumer worker (async, in EventConsumerWorker.process_batch)
  → XREADGROUP mi:<stream_name> > consumer_group            [event_handlers.py:415-475]
  → dispatch to registered handler                          [event_handlers.py:125-383]
  → on success: XACK                                        [event_handlers.py:456]
  → on parse error: _move_to_dead_letter                    [event_bus.py:451-477]
  → on handler failure: events_failed += 1, no ACK          [event_handlers.py:458] (F14)
```

**Failure semantics (inherited from S2001 §10.1 + S2002 §7.8):**

- Emission failure (Redis down) → wrapper logs + metric increment; underlying producer transaction unaffected (emission is fire-and-forget). Per S2002 §7.8.
- Parse error at consumer → move to DLQ per `_move_to_dead_letter` at `event_bus.py:275`.
- Handler failure at consumer → **retry loop with no give-up** per S2001 F14 (does NOT flow to DLQ; events_failed counter increments; next `XREADGROUP` re-delivers on `claim_stale_events` reclaim window).
- No DLQ reader at S2003 open per S2001 F15.

### 7.2 WebSocket emission runtime flow

```
Producer code (async only — Django Channels requires async context)
  → await channel_layer.group_send(group_name, {'type': 'consumer.method', ...payload})
Consumer worker (Daphne + Channels layer, in-process buffer)
  → group_send fanout to all subscribed consumers in group
  → each consumer's `consumer.method` fires with payload
Browser client (WebSocket connection subscribed to group)
  → JSON message delivered to browser code
  → UI render / state update
```

**Failure semantics:**

- Emission failure (Channels layer error) → typically per-connection failure; other consumers in group unaffected.
- No canonical retry — WebSocket is fire-and-forget for UI updates.
- Subscription lifecycle → on browser disconnect, group membership drops; missed messages are lost (no persistence).

**Note:** WebSocket is not a durable substrate. This is why cross-service backend consumers MUST use EventBus, not WebSocket, for state changes that require durability (D4 rationale).

### 7.3 CeleryTaskEvent emission runtime flow

```
Celery task starts
  → task_prerun signal fires
  → celery_telemetry signal handler creates CeleryTaskEvent(state=STARTED)
Celery task body executes
  → (no direct write to CeleryTaskEvent)
Celery task completes
  → task_postrun signal fires
  → celery_telemetry signal handler updates CeleryTaskEvent with duration, error info
```

**Failure semantics:**

- Signal handler failure → per S2001-adjacent worker resilience discipline: signal-handler errors are logged but do not fail the task itself.
- 30-day TTL → cleanup task runs per `docs/topics/celery-workers.md`.

### 7.4 LLMCallEvent emission runtime flow

```
Producer code
  → with LLMCallWrapper(provider, model, agent_name) as call:
      → LLMCallEvent.objects.create(...) with pre-call fields
      → response = call.invoke(...)                         (nested OpenAI/Anthropic/Together call)
      → on exit: LLMCallEvent updated with post-call fields
```

**Failure semantics:**

- LLM API failure → wrapper writes `finish_reason='error'` + `error_class` field; caller receives exception per configured retry policy.
- LLMCallEvent write failure → per S1219 watchdog: cleanup task at 5min heartbeat catches any orphaned rows.
- 30-day TTL → S1220 cleanup watchdog PR #2520.

### 7.5 OpsRunEvent emission runtime flow

```
Mission step boundary (MissionRunner)
  → OpsRun.append_event(event_type='step_started', label=step_name, payload={...})
  → creates OpsRunEvent row
Step body executes
  → intermediate append_event(...) calls if step logs progress
Step verdict
  → append_event(event_type='step_completed', label=verdict, payload={...})
Post-flight
  → append_event(event_type='mission_completed', label=verdict, payload={final_state})
```

**Failure semantics:**

- OpsRun write failure → per Employee OS discipline: mission halts + escalates via `MissionRunner._escalate` per `mission_runner.py`.
- No default TTL for Class-1 audit-forever per S2002 §17.3.

### 7.6 ToolCallRecord emission runtime flow

```
PA agentic loop / agent tool dispatch
  → ToolDispatcher.dispatch_tool_call(tool_name, args, agent_execution_id)
  → ToolCallRecord.objects.create(...) with input_data, agent_execution_id
  → handler(args) executes
  → ToolCallRecord updated with output_data, success bool, duration_ms
```

**Failure semantics:**

- Handler exception → ToolCallRecord.success=False, error_message set; dispatcher re-raises to caller.
- 30-day TTL per S861 cleanup task.

### 7.7 Composition-time runtime flow: cross-substrate parallel telemetry (canonical example)

The canonical multi-substrate telemetry flow when a PA tool call includes an LLM invocation inside a Celery task inside a mission step:

```
Celery task starts
  → task_prerun signal → CeleryTaskEvent(STARTED, task_id=T1)
  → MissionRunner starts mission step
      → OpsRun.append_event(event_type='step_started', payload={...}, correlation_id=C1)
      → PA agentic loop invokes tool
          → ToolDispatcher.dispatch_tool_call(...)
              → ToolCallRecord(task_id=T1, tool_name='...', correlation_id=C1)
              → tool handler invokes LLM
                  → with LLMCallWrapper(...) as call:
                      → LLMCallEvent(task_id=T1, correlation_id=C1)
                      → OpenAI call
                      → LLMCallEvent updated
              → ToolCallRecord updated
      → OpsRun.append_event(event_type='step_completed', correlation_id=C1)
Celery task completes
  → task_postrun signal → CeleryTaskEvent updated
```

**All four telemetry substrates write for the same execution** — each for a distinct concern (task lifecycle / mission step audit / tool dispatch audit / LLM call audit). The `correlation_id` envelope field ties them together for post-hoc reconstruction.

**§17.3 classification: this is NOT duplicate emission.** Each row records a distinct concern; the collision is intentional cross-concern telemetry, not the same-event-twice pattern.

### 7.8 Composition-time runtime flow: intentional dual-emission (S2002 §7.9 canonical + mirror)

The canonical Class-1 governance dual-emission flow per S2002 §7.9:

```
HAI transition (auto_approve / auto_escalate / record_decision / record_verification)
  → publish_hai_<transition>_event(...) canonical wrapper (post-arc adoption)
      → EventBus.publish(event, stream=HAI_<TRANSITION>)   [canonical — pub/sub]
      → transaction.on_commit hook:
          → OpsRunEvent.objects.create(
                event_type='hai_<transition>',
                payload={..., 'source_event_stream': 'HAI_<TRANSITION>'},
                event_id=<same UUID>                        [mirror — audit-forever]
            )
```

**Both writes carry equal `event_id`** — this is the invariant that ties canonical + mirror per S2002 §7.9. EventBus consumers subscribe to the stream and react at execution time; OpsRunEvent consumers query the audit table for retroactive audit (`governance_audit_view` per S2002 §17.2).

**§17.1 classification: this is INTENTIONAL dual-emission, sanctioned by S2002 §7.9 canonical + mirror rule for Class-1 governance events.**

### 7.9 Composition-time runtime flow: F11 drift (three parallel substrates for spider-data)

```
Spider runtime writes spider data
  → PATH A: ai_core.SpiderAgentConnector.publish_spider_data(...)
        → self.redis_client.publish('spider_data', json_packet)
        → real callers: ai_core/agents/concrete_executor.py:637-638
                        core/views_agent_intelligence.py:352,355
  → PATH B: intelligence.SpiderAgentConnector._build_routing_map(...)
        → returns Dict[str, List[str]] — in-process routing table
        → real callers: core/tasks_spiders.py:260,307
                        core/tasks.py:1355,1359
                        core/management/commands/process_spider_data.py:6,16
                        core/management/commands/activate_spiders.py:10,234
  → PATH C: publish_spider_data_event(...) canonical wrapper
        → EventBus.publish(event, stream=EventStream.SPIDER_DATA)
        → 0 non-definition callers (dormant per S2001 F1)
```

Three substrates + two identically-named `SpiderAgentConnector` classes in different Django apps. §16 records as boundary violation; §17 records as drift dual-emission. **D2 recommendation: HIGH cleanup priority, F11 T1 slot.**

## 8. Data Ownership and Lifecycle

**Q14 — Who owns which substrate rows?**

Cross-substrate ownership matrix (per §5 service ownership + §4 model backing):

| Substrate | Row owner (write authority) | Row consumer (read authority) | Lifecycle boundary |
|---|---|---|---|
| EventBus stream row | `EventBus.publish` via `publish_*_event` wrapper | `EventConsumerWorker.process_batch` per consumer_group | MAXLEN=10000 rotation (Class-2) OR per-event class per §17.3 |
| EventBus DLQ row | `_move_to_dead_letter` at `event_bus.py:451` | **No consumer at S2003 open per S2001 F15** | MAXLEN=1000 rotation (`event_bus.py:468`) |
| WebSocket message | Per-emission call site (~40 sites) | Browser client(s) subscribed to group | Ephemeral (session lifetime) |
| CeleryTaskEvent | `celery_telemetry` signal handlers | Grafana dashboards + `celery_task_history` PA tool + S1245 audit_celery_zero_fire | 30-day TTL |
| LLMCallEvent | `LLMCallWrapper` context manager | S1219 cleanup watchdog + LLM cost tracking + audit tools | 30-day TTL per S1220 PR #2520 |
| OpsRunEvent | `MissionRunner` step boundaries + `OpsRun.append_event` (7 runtime call sites per §3) | `governance_audit_view` per S2002 §17.2 + Employee OS audit surface + PA `ops_tool` | No default TTL (Class-1 audit-forever); Class-2 mission events unlabeled at S2003 open — F.OPSRUNEVENT-CLASS-TAG post-arc T-slot candidate |
| ToolCallRecord | `ToolDispatcher.dispatch_tool_call` | `tool_call_history` PA tool + provenance dashboards | 30-day TTL per S861 |
| Drift substrate (F11) | `SpiderAgentConnector.publish_spider_data` (ai_core) | No canonical consumer — pub/sub subscribers are transient | Ephemeral (fire-and-forget); no persistence |

**Q17 — Cross-substrate lifecycle bindings**

Per S2002 §8.2 canonical + mirror ordering (extended to composition contract):

**Emission → source-row persistence order (all substrates):** Every substrate write MUST fire AFTER the source row (HAI/HFR/OpsRun/Deliverable/etc) has committed. Rationale: consumers reading source-row fields at handler time need the row to exist. Enforcement: `transaction.on_commit` hook for ORM-backed rows.

**Canonical emission → mirror emission order (Class-1 dual-emission per §7.9):** canonical EventBus emission fires FIRST, mirror OpsRunEvent write follows on `transaction.on_commit`. Same `event_id` on both writes. Per S2002 §7.9.

**Emission → downstream state change order (all push-with-consumers substrates):** Emission MUST fire BEFORE any downstream state change that depends on the event. Per S2002 §7.8.

**Q18 — Substrate row deletion policy**

- **Rotational deletion (EventBus + WebSocket):** MAXLEN-bounded (EventBus streams) OR ephemeral (WebSocket). No manual delete surface.
- **TTL-bounded deletion (CeleryTaskEvent + LLMCallEvent + ToolCallRecord):** 30-day TTL enforced by cleanup tasks per §5 owning-arc.
- **Manual deletion (OpsRunEvent Class-1 audit-forever):** No default TTL; deletion requires explicit administrative operation. Per S2002 §17.3.
- **F11 drift substrate:** ephemeral (no persistence). Deprecation via F11 T1 slot per D2.

### 8.1 Ownership matrix per composition-relevant model

| Model | Owning service | Owning arc | Contract stewardship |
|---|---|---|---|
| `EventStream` enum | `EventBus` service | Group 2000+ arc P1 (S2001) | Adding a stream requires P3 composition consultation per D1 |
| `EventPriority` enum | `EventBus` service | Group 2000+ arc P1 (S2001) | Priority additions are non-breaking envelope changes |
| `Event` dataclass | `EventBus` service | Group 2000+ arc P1 (S2001) + P2 (S2002 envelope contract §7.0) | S2002 §7.0 12-field envelope (schema_version + event_type + event_id + emitted_at + producer + producer_version + source_kind + authority_scope + idempotency_key + mission_id + boundary_crossed + caller_actor) applies post-adoption |
| `SpiderDataPacket` | `SpiderAgentConnector` (ai_core) | **Deprecation owner: TBD** — F11 T1 slot | Class + envelope both migrate at deprecation |
| `OpsRun` + `OpsRunEvent` | `MissionRunner` + Employee OS | Employee OS arc + Group 1800 P2 mirror-write per §7.9 | Cross-owner: Employee OS owns row semantics; P2 §7.9 owns mirror-write shape |

### 8.2 Substrate retention lifecycle summary

Per S2002 §8.3 two-class extended to full six-substrate composition contract:

**Class-1 audit-forever posture** — no default TTL. Applies to:
- OpsRunEvent Class-1 governance rows (HAI_AUTO_APPROVED mirror, HAI_AUTO_ESCALATED mirror, F.PER-USER-AUTHORITY events per S2002 §20.9)

**Class-1 bounded-history posture** — EventBus MAXLEN=10000 + audit-table backing durable. Applies to:
- EventBus HAI_DECISION_RECORDED + HAI_VERIFICATION_RECORDED (HFR / HAI rows are the durable audit source; EventBus copy is bounded)

**Class-2 bounded posture** — MAXLEN=10000 or 30-day TTL. Applies to:
- EventBus SPIDER_DATA + OPPORTUNITY_SCORED + VALIDATION_REQUIRED + VALIDATION_DECIDED + OUTCOME_RECORDED + MODEL_TRAINED + SYSTEM_ALERT (all Class-2 per S2001)
- EventBus six-plane learning-surface events (S2002 §10)
- CeleryTaskEvent 30-day
- LLMCallEvent 30-day
- ToolCallRecord 30-day
- WebSocket ephemeral

**DLQ posture (D3 recommendation):** MAXLEN=1000 (current EventBus posture) retained. Explicit joint-ADR override slot documented in §15.

**F11 drift substrate:** ephemeral; deprecation clears the posture question.

## 9. Integrations With Other Domains

**Q14 (repeat, integration flavor) + Q17 + Q18 + Q21 + Q22.**

### 9.1 Cross-domain integration matrix (composition contract angle)

| Domain | Integration relationship | Strength | P3 contract obligation |
|---|---|---|---|
| Group 1300 Memory | Substrate composition consumer: Memory writes affect OpsRunEvent (mission audit trail) + CeleryTaskEvent (background embed pipeline) | STRONG (parallel telemetry, no dual-emission collision) | No new contract obligation; §7.7 parallel-telemetry pattern recognized |
| Group 1500 Sports | Substrate composition consumer: SportsBettingLearningBridge (S1805 F4) reads HAI_VERIFICATION_RECORDED per S2002 §17.2 | WEAK at S2003 open (bridge coupling in `BettingOutcomeVerifier._create_learning_records:127-135`; refactor to EventBus consumer group deferred to Group 1500 T-slot) | Contract obligation: bridge migrates to canonical EventBus consumer per §17.2 REQUIRED row (Group 1500 arc-owned) |
| Group 1600 Content | Substrate composition consumer: ContentDeliberationRunner writes AgentExecution + ToolCallRecord + potentially LLMCallEvent | STRONG (parallel telemetry, no collision) | No new contract obligation |
| Group 1700 Observability | **Substrate owner**: LLMCallEvent + CeleryTaskEvent + LLMCallEvent 30-day TTL. Retention posture recommendation pairs with P3 DLQ retention decision (D3) | STRONG (owner) | P3 recommends DLQ posture per §17.3 two-class extension; joint ADR resolution finalizes |
| Group 1800 Human Attention | **Substrate co-owner**: OpsRunEvent Class-1 mirror per S2002 §7.9. HAI events canonical on EventBus + mirror on OpsRunEvent. | STRONG (contract co-owner) | P3 inherits S2002 §7.9 canonical + mirror unchanged; §10.4 substrate × HAI-event mapping consumes as input |
| Group 1900 Authority Enforcement | **Deferred integration**: F.PER-USER-AUTHORITY-MECHANISM events per S2002 §20.9 → OpsRunEvent (recommended per §7.9). MECHANISM implementation is Group 1900 arc scope | MISSING (mechanism not built at S2003 open) | P3 documents substrate assignment; Group 1900 MECHANISM arc adopts |
| Group 2000+ P1 (S2001) | Baseline producer/consumer inventory + F1-F18 findings | STRONG (baseline shipped) | P3 consumes F1/F2/F7/F9/F11/F14/F15/F17/F18 as constraints; F11 explicitly inherited per §16 |
| Group 2000+ P2 (S2002) | HAI event contract + §7.9 canonical + mirror + §17.2 consumer registry + §17.3 retention posture + §20.9 F.PER-USER-AUTHORITY | STRONG (contract shipped) | P3 consumes as substrate-assignment input; §10.4 substrate × HAI-event mapping directly derives from S2002 §7 + §10 |
| Group 2000+ P4 (S2004 planned) | Cat F Adjacent / Separation Boundaries CONSOLIDATION | Not yet run | P3 delivers 6-substrate separation contract as input; P4 audits separation-boundary posture between event/integration and adjacent domains |
| Symbol Mapping (S1274 Option E) | Substrate composition consumer: E-only evidence layer writes OpsRunEvent audit rows (`authority_action_observed`) per S1274 §10.2 | STRONG (adopted per S1274 D45) | P3 §19.1 audits S1274 §10.3.1 four graduation triggers; graduation timing is Chris-gate D5 |
| Employee OS | **Substrate owner**: MissionRunner writes OpsRunEvent step boundaries; job contracts consume OpsRunEvent audit rows | STRONG (owner) | No new contract obligation; §7.5 flow recognized |
| Personal Assistant (Rigby) | **Substrate owner**: ToolDispatcher writes ToolCallRecord; PA agentic loop writes LLMCallEvent via LLMCallWrapper | STRONG (owner) | No new contract obligation; §7.6 flow recognized |
| Frontend | Substrate consumer: WebSocket group_send is the browser-facing UI update path (~40 call sites); no direct EventBus consumer in browser | STRONG (owner of WebSocket read side) | D4 recommendation: WebSocket canonical for browser UI state; EventBus canonical for backend state — dual-emission for cross-cutting UI+backend state changes per §10.5 |
| API | Substrate consumer: REST/DRF endpoints do NOT publish to substrates directly; server-side handlers emit as needed | Not composition-relevant | No obligation |
| Discord | Substrate consumer: `event_handlers.py:125-383` includes a Discord log handler for SYSTEM_ALERT (S2001 F18 flag: log-only handler decorativeness) | WEAK (per F18) | No new contract obligation; F18 T-slot cleanup owns handler decorativeness |

### 9.2 Handoff obligations to future arcs

- **To Group 1500 Sports arc T-slot:** `SportsBettingLearningBridge` migrates to canonical EventBus consumer per S2002 §17.2 REQUIRED row.
- **To Group 1700 Observability arc:** DLQ retention posture recommendation (D3) feeds joint retention ADR resolution.
- **To Group 1800 HAI arc T-slot:** `publish_hai_*_event` shared wrapper mandate per S2002 §6.2 must land; §7.9 canonical + mirror pattern enforced via wrapper.
- **To Group 1900 Authority MECHANISM arc:** F.PER-USER-AUTHORITY-MECHANISM three governance events per S2002 §20.9 land on OpsRunEvent (recommended per §7.9 canonical + mirror). MECHANISM materializes; substrate assignment locked here.
- **To Group 2000+ P4 (S2004 Cat F Adjacent CONSOLIDATION):** Separation-boundary posture between event/integration and adjacent domains consumes the 6-substrate separation contract from §10.2 as input.
- **To Group 2000+ xx99 (S2099 canonical summary):** P3 delivers separation contract + duplicate-emission audit + Symbol Mapping graduation status verification; xx99 rolls up per playbook §11.3 12-section template.

## 10. Event Flows — 6-Substrate Separation Contract

*(§11.2 template §10 Event Flows — enriched with the 6-substrate separation contract per parent §5.3 deliverable 1. This is the load-bearing design surface of the audit.)*

### 10.0 Contract preamble

The separation contract is the canonical rule set that answers: **"when does a new emission go to which substrate?"** It sits above the six substrates as a documentation + adoption-discipline surface — no runtime enforces the contract. Enforcement is via code review + per-substrate wrapper adoption + drift audits.

**Three-axis selector** (D1):

- **Axis A (Coordination vs Telemetry):** Does the emission cause a downstream consumer to *react at execution time* (coordination), or is it *evidence-after-the-fact* consumed later by dashboards/PA tools/investigations (telemetry)?
- **Axis B (Canonical audience):** Who is the primary consumer? Cross-service backend (EventBus canonical) / browser session-scoped UI (WebSocket canonical) / audit reader (telemetry substrate canonical) / mission-step audit (OpsRunEvent canonical)?
- **Axis C (Retention class):** Class-1 audit-forever / Class-1 bounded-history / Class-2 bounded (per S2002 §17.3)?

The three axes are not orthogonal — some combinations are illegal (a Class-1 audit-forever emission cannot be WebSocket-canonical, because WebSocket has no persistence). The contract table (§10.2) enumerates the sanctioned combinations.

### 10.1 Substrate inventory (composition contract scope)

Re-attesting the six named substrates + one drift substrate per §3:

| # | Substrate | Axis A role | Backing | Contract scope |
|---|---|---|---|---|
| 1 | EventBus (Redis Streams) | Coordination (push-with-consumers) | Redis Streams `mi:*` + DLQ `mi:dead_letter` | Canonical for cross-service backend runtime coordination |
| 2 | WebSocket (Channels group_send) | Coordination (push-with-consumers) | In-memory Channels group buffer, ephemeral | Canonical for browser session-scoped UI updates |
| 3 | CeleryTaskEvent | Telemetry (write-and-query) | PostgreSQL row (`core/models_celery_telemetry.py:17`) | Canonical for Celery task lifecycle audit |
| 4 | LLMCallEvent | Telemetry (write-and-query) | PostgreSQL row (`core/models_llm_telemetry.py:30`) | Canonical for LLM invocation audit |
| 5 | OpsRunEvent | Telemetry (write-and-query) — but Class-1 mirror per §7.9 | PostgreSQL row (`core/models_ops_runs.py:117`) | Canonical for mission-step audit + Class-1 governance mirror per S2002 §7.9 |
| 6 | ToolCallRecord | Telemetry (write-and-query) | PostgreSQL row (`core/models_tool_calls.py:19`) | Canonical for PA tool dispatch audit |
| — | Drift: raw `redis.publish()` (F11) | Coordination (fire-and-forget pub/sub) | Redis pub/sub channel, ephemeral | **DEPRECATED** per D2; migrate to substrate #1 EventBus |

### 10.2 Per-substrate criteria table (D1 canonical rule set)

The contract table below is the load-bearing deliverable of parent §5.3 Chris-gate (a). For each substrate, the table names the sanctioned use cases + forbidden use cases + intentional-dual-emission cases.

| Substrate | Use when… | Do NOT use when… | Dual-emission cases (§10.3 register) |
|---|---|---|---|
| **EventBus** (canonical push-with-consumers, cross-service backend) | (a) A cross-service backend consumer needs to *react* at execution time to a state change. (b) The emission carries a domain event that other services subscribe to (e.g., HAI transition, opportunity scoring). (c) The event must be durable for replay per S2001 §10.5 δ. (d) Class-2 learning-surface event per S2002 §10 six-plane catalog. (e) Class-1 governance event canonical per S2002 §7.9. | (f) The consumer is browser-only — use WebSocket. (g) The emission is telemetry-only (post-hoc read) — use one of #3-#6. (h) The emission is F11 spider-data drift — migrate wrapper. | Class-1 governance events emit here + OpsRunEvent mirror per §7.9. WebSocket UI-render fanout per D4 when browser also needs the update. |
| **WebSocket** (canonical push-with-consumers, browser UI) | (a) Browser session-scoped UI must update in real time (e.g., workspace progress, agent status, chat message). (b) The consumer is a Django Channels consumer subscribed to a group. (c) Persistence is not required — session lifetime is sufficient. | (d) Cross-service backend consumer needs the update — use EventBus. (e) Persistence beyond session is required — use EventBus or a telemetry substrate. (f) Audit-forever posture is required — never use WebSocket alone; use EventBus canonical + OpsRunEvent mirror per §7.9. | UI-render fanout for state changes that also fire EventBus canonical. Documented as intentional dual-emission per §10.3.4. |
| **CeleryTaskEvent** (canonical write-and-query, Celery task lifecycle) | (a) The event is a Celery task lifecycle transition (STARTED / SUCCESS / FAILURE / REVOKED). (b) Consumer is Grafana dashboard, `celery_task_history` PA tool, or `audit_celery_zero_fire` (S1245). (c) Signal-driven canonical path (`task_prerun` / `task_postrun`). | (d) Direct creation from Celery task body — signal-driven only. (e) Non-Celery events — use appropriate substrate. | None. Parallel telemetry with other substrates (§7.7) is not dual-emission — each row records a distinct concern (task lifecycle). |
| **LLMCallEvent** (canonical write-and-query, LLM call audit) | (a) An LLM API call is being invoked (OpenAI, Anthropic, Together, Ollama, DeepSeek, Gemini). (b) Wrapper-managed emission via `LLMCallWrapper` context manager (S1098). (c) Consumer is LLM cost tracking, watchdog (S1219), reliability metrics. | (d) Non-LLM API call — not this substrate. (e) Direct `LLMCallEvent.objects.create(...)` outside wrapper — defect. | None. Parallel telemetry with CeleryTaskEvent + OpsRunEvent + ToolCallRecord per §7.7 (correlation_id envelope ties them). |
| **OpsRunEvent** (canonical write-and-query, mission-step audit + Class-1 mirror) | (a) A MissionRunner step boundary fires (`step_started` / `step_completed`). (b) Employee OS mission audit event (`docs/topics/employee-os.md`). (c) Class-1 governance mirror for HAI event per S2002 §7.9. (d) F.PER-USER-AUTHORITY-MECHANISM event per S2002 §20.9 (recommended substrate). | (e) Non-mission telemetry — use appropriate substrate. (f) Direct create outside `MissionRunner` / delegated writer without owner audit — defect trigger. | Class-1 mirror per §7.9 (HAI events + F.PER-USER-AUTHORITY events emit here alongside EventBus canonical, same event_id). |
| **ToolCallRecord** (canonical write-and-query, PA tool dispatch audit) | (a) A PA tool is dispatched via `ToolDispatcher.dispatch_tool_call` (S861). (b) Consumer is `tool_call_history` PA tool + provenance dashboards. | (c) Direct create outside `ToolDispatcher` — defect. (d) Non-PA-tool audit — use appropriate substrate. | None. Parallel telemetry with LLMCallEvent + OpsRunEvent per §7.7. |
| **Drift: raw redis.publish()** | (deprecated) | Any new use is a defect. Migrate to substrate #1 EventBus per D2. | (F11) Same-signal drift with EventBus SPIDER_DATA + in-process routing table — see §17.2. |

**Contract adoption discipline** (playbook §14.5-adjacent — no-implementation-here rule): the contract table is documentation. Adopters (arcs that add new emissions, arcs that refactor existing emissions) MUST consult this table + §10.3 register + §17 duplicate-emission audit before shipping a new emission or substrate write. Post-arc T-slot F.COMPOSITION-CONTRACT-CI-CHECK candidate: a CI grep that flags a new `channel_layer.group_send` call site + a new `.publish(...)` bypass + a new `OpsRunEvent.objects.create(...)` write outside sanctioned entry points for review.

**OpsRunEvent Class-1 mirror discipline (Rigby S2003 SIGN cycle 1 batch 1 Q1 STRENGTHEN):**

When OpsRunEvent carries a Class-1 governance mirror (§10.3.1 canonical + mirror), it remains a **write-and-query telemetry / evidentiary substrate**. It does NOT become a coordination substrate. Concretely:

- **Consumers MUST NOT use OpsRunEvent as the canonical coordination feed** — subscribers listening for HAI transitions read EventBus canonical; OpsRunEvent is the audit-forever backing.
- **If a consumer must query OpsRunEvent for governance reasons** (e.g., `governance_audit_view` per S2002 §17.2 — a read-only projection), it MUST be explicitly designated in the consumer registry with an `activation_mode` per S2002 §17.5 (query-based consumer with cadence documented) + verification-evidence that it is not the canonical coordination surface.
- **Rationale (Rigby SIGN):** DB-mirror-as-de-facto-bus creates dormancy risk (S2001 F9 class of failure — "exists in DB doesn't mean actively consumed"), latency + coupling (query patterns, indexes, pagination), and different replay semantics (re-scan rows vs re-consume stream offsets). OpsRunEvent as canonical coordination substrate is a defect.

### 10.3 Intentional-dual-emission register (D1 continued)

The register enumerates every sanctioned pattern where a single logical event fires on more than one substrate. Rationale for each pattern is documented so adopters can distinguish sanctioned dual-emission from drift.

#### 10.3.1 Class-1 governance canonical + mirror (S2002 §7.9 canonical)

Sanctioned pattern for HAI four candidate transitions + F.PER-USER-AUTHORITY three governance events:

- **Canonical substrate:** EventBus (pub/sub for cross-service consumer subscription).
- **Mirror substrate:** OpsRunEvent (audit-forever Class-1 per §17.3).
- **Invariant:** Both writes share the same `event_id` envelope UUID (§7.0).
- **Emission ordering:** canonical FIRST via `EventBus.publish` + mirror via `transaction.on_commit` hook.
- **Version-bump rules** (S2002 §7.9 → S1275 §7.5 substrate-change rules):
  - Adding a mirror on a new substrate: **minor bump** (`schema_version` `X.Y` → `X.(Y+1)`) provided `event_id` equality holds.
  - Removing a mirror: **minor bump** (canonical EventBus consumers unaffected).
  - Changing the canonical substrate: **major bump** (`schema_version` `X.Y` → `(X+1).0`).
- **Adopter obligation:** Emit via shared wrapper (`publish_hai_*_event`) per S2002 §6.2 shared wrapper mandate. Direct `EventBus.publish(...)` bypass without the mirror write is a defect.

**Applies to:**

| Event | Canonical substrate | Mirror substrate | Rationale |
|---|---|---|---|
| `HAI_DECISION_RECORDED` | EventBus | OpsRunEvent (recommended) | Cross-substrate consumer uniformity + audit-forever governance trace |
| `HAI_VERIFICATION_RECORDED` | EventBus | OpsRunEvent (recommended) | Cross-substrate consumer uniformity + sports outcome audit-forever |
| `HAI_AUTO_APPROVED` | EventBus | OpsRunEvent (REQUIRED) | System-initiated governance; audit-forever |
| `HAI_AUTO_ESCALATED` | EventBus | OpsRunEvent (REQUIRED) | System-initiated critical governance; on-call notification consumer |
| `AUTHORITY_CHECK_EVALUATED` (S2002 §20.9) | EventBus (recommended) | OpsRunEvent (REQUIRED) | Authority resolution audit + cross-service subscription for post-hoc drift detection |
| `AUTHORITY_DECISION_OVERRIDDEN` (S2002 §20.9) | EventBus (recommended) | OpsRunEvent (REQUIRED) | Same |
| `AUTHORITY_POLICY_BOUND_TO_USER` (S2002 §20.9) | EventBus (recommended) | OpsRunEvent (REQUIRED) | Same |

#### 10.3.2 Non-mirror Class-1 governance canonical (S2002 §17.3 audit-table backing)

Not a dual-emission per se — the HFR/HAI ORM rows are domain-object state + audit-table backing, not a mirror event. Documented here for the sake of adopters distinguishing from §10.3.1 mirror pattern.

- **HAI_DECISION_RECORDED**: EventBus canonical + HFR row is audit-table backing (bounded EventBus copy + durable HFR audit source per S2002 §17.3).
- **HAI_VERIFICATION_RECORDED**: EventBus canonical + HAI verification-tier fields on HAI row.

**Distinction from §10.3.1 mirror:** the ORM row is a *domain object* whose fields include verification/decision state. It is not a copy of the event envelope. Adopters do not maintain `event_id` equality; the HFR/HAI row has its own `id` UUID.

#### 10.3.3 Six-plane Class-2 learning-surface canonical (S2002 §10)

Not a dual-emission — Class-2 default is canonical-EventBus-only per S2002 §7.9 Q10b FOLD. Documented for scope clarity.

- **BRIDGE_DISPATCHED** (S2002 §10.2): EventBus canonical, no mirror.
- **NON_BRIDGE_LEARNING_WRITE** (S2002 §10.3): EventBus canonical, no mirror.
- **CROSS_DOMAIN_LEARNING_ROUTED** (S2002 §10.4): EventBus canonical, no mirror.
- **EXTERNAL_SIGNAL_INGESTED** (S2002 §10.5): EventBus canonical (post-D6-activation), no mirror.
- **SHADOW_SERVICE_INVOKED** (S2002 §10.6): EventBus canonical (post-consolidation), no mirror.

**Class-2 → Class-1 promotion rule (S2002 §17.3):** Any Class-2 event later used as input to a governance decision MUST have either an audit-table mirror OR a deterministic reconstruction path. Promotion path is documented; adopters trigger via new arc.

#### 10.3.4 WebSocket UI-render fanout (D4 new pattern)

Sanctioned pattern for state changes that affect both backend consumers AND browser UI:

- **Canonical substrate:** EventBus (cross-service backend consumers subscribe).
- **UI-render substrate:** WebSocket group_send (browser session-scoped consumers).
- **Mandatory envelope (Rigby S2003 SIGN cycle 1 batch 1 Q2 FOLD):** UI-render fanout messages MUST use the display-only envelope shape:

  ```json
  {
    "type": "ui.render_hint",
    "event_id": "<canonical event UUID>",
    "source_canonical": "eventbus",
    "display": {
      "// non-authoritative UI fields — display-only"
    }
  }
  ```

  The `type` field being `"ui.render_hint"` is the parse-time enforcement: browser consumers that dispatch on `type` see `ui.render_hint` and route to display-only handlers. Any consumer that dispatches domain-semantic handlers on `ui.render_hint` is a contract violation.

- **Payload MUST NOT clause (Rigby S2003 SIGN cycle 1 batch 1 Q2 FOLD):** WebSocket UI-render messages MUST NOT contain domain payload fields that would allow a client to enact state transitions without fetching or deriving from the canonical event. Concretely: no `decision`, `verification_status`, `authority_verdict`, `escalation_reason_code`, or similar governance-authoritative field in the `display` object.

- **Emission ordering:** EventBus canonical FIRST + WebSocket fanout follows on `transaction.on_commit` hook.
- **Adopter obligation:** UI-render message is display-only. Browser consumer MUST NOT treat it as authoritative state; authoritative state is either in the EventBus canonical event OR fetched from the API. This preserves the Axis-A distinction: EventBus is source of truth; WebSocket is a display hint.

- **Adopter code-review anti-pattern (Rigby S2003 SIGN cycle 1 batch 1 Q2 FOLD):** If a reviewer sees code that updates governance state (or any authoritative domain state) based solely on a received WebSocket message, treat as a contract violation. The correct pattern is: WebSocket message triggers a fetch/re-derive from the canonical event (via EventBus consumer OR API endpoint). Reviewers should search for: (a) any handler on a `ui.render_hint` message that mutates persistent state; (b) any browser-side use of a `display` field as an authoritative decision input; (c) any WebSocket message with `type != 'ui.render_hint'` that overlaps with a Class-1 governance event without an EventBus canonical peer emission.

**Rationale:** many current WebSocket call sites emit domain semantics (e.g., "opportunity created" fires only on WebSocket, not on EventBus). D4 does NOT retroactively rework existing sites — it establishes the go-forward pattern for new state changes. Existing sites are audited in §14 for canonical assignment recommendation.

#### 10.3.5 Parallel telemetry per concern (§7.7 pattern)

Not a dual-emission — each substrate records a distinct concern. Documented for scope clarity.

**Concern boundary per substrate (Rigby S2003 SIGN cycle 1 batch 2 Q4 STRENGTHEN):**

- **CeleryTaskEvent**: **Task lifecycle** concern — a Celery task's `STARTED / SUCCESS / FAILURE / REVOKED` state transitions + resource-usage envelope (RSS, duration). Semantic tuple: `(task_id, task_name, state_transition, occurred_at)`. Answers: "did a task run + did it complete + how long + how much memory."
- **LLMCallEvent**: **LLM invocation** concern — a single API call to a provider (OpenAI, Anthropic, etc.) with token/cost accounting. Semantic tuple: `(provider, model, prompt_hash_or_correlation_id, finish_reason, occurred_at)`. Answers: "was an LLM call made + did it complete + tokens/cost."
- **OpsRunEvent**: **Mission-step audit boundary** concern — an Employee OS mission-step lifecycle transition (`step_started`, `step_completed`, intermediate progress) OR a Class-1 governance mirror (§10.3.1). Semantic tuple: `(mission_id_or_run_id, step_label, event_type, occurred_at)`. Answers: "what mission step happened + what verdict."
- **ToolCallRecord**: **PA tool dispatch** concern — a single `ToolDispatcher.dispatch_tool_call(...)` invocation with input/output payloads + success bool. Semantic tuple: `(tool_name, agent_execution_id, input_hash, occurred_at)`. Answers: "was a specific PA tool called with specific args + did it succeed."

**Duplicate-emission drift test (Rigby S2003 SIGN cycle 1 batch 2 Q4 STRENGTHEN):** if two substrates record the same semantic tuple `(actor, action, target, args_hash, occurred_at)` for the same execution, classify as **duplicate-emission drift** and file a finding. Examples of drift this test catches:

- ToolCallRecord AND OpsRunEvent both record the same tool dispatch as a step boundary → the OpsRunEvent step boundary is duplicate; refactor to reference the ToolCallRecord row instead.
- LLMCallEvent AND OpsRunEvent both record the same LLM invocation → drift; the OpsRunEvent write should reference the LLMCallEvent, not duplicate its semantic content.
- CeleryTaskEvent AND OpsRunEvent both record the same task lifecycle transition → drift; OpsRunEvent should record mission-step boundaries, not task-level lifecycle.

The drift-test is a post-arc T-slot obligation (F.PARALLEL-TELEMETRY-DRIFT-TEST candidate — added to §19 T2 slot).

**Invariant:** `correlation_id` envelope field is set on each write and equal across writes belonging to one execution. Post-hoc reconstruction is the reader's obligation.

**Adopter obligation:** propagate `correlation_id` through the call stack. Post-arc T-slot F.CORRELATION-ID-PROPAGATION candidate: audit correlation_id coverage across substrate writes.

### 10.4 Substrate × HAI-event mapping (parent §5.3 deliverable 3)

Consuming S2002 §7 four HAI candidate transitions + §10 six plane events + §20.9 F.PER-USER-AUTHORITY three governance events, mapped to substrates per §10.2 + §10.3.

| Event | Canonical substrate | Mirror substrate | Class | §10.3 dual-emission pattern | S2002 ref |
|---|---|---|---|---|---|
| `HAI_DECISION_RECORDED` | EventBus | OpsRunEvent (recommended) + HFR audit-table row | Class-1 bounded-history | §10.3.1 + §10.3.2 | §7.1 |
| `HAI_VERIFICATION_RECORDED` | EventBus | OpsRunEvent (recommended) + HAI verification-tier fields | Class-1 bounded-history | §10.3.1 + §10.3.2 | §7.2 |
| `HAI_AUTO_APPROVED` | EventBus | OpsRunEvent (REQUIRED) | Class-1 audit-forever | §10.3.1 | §7.3 |
| `HAI_AUTO_ESCALATED` | EventBus | OpsRunEvent (REQUIRED) | Class-1 audit-forever | §10.3.1 (v0.x reserved-minimal per S2002 SIGN batch 3 Q8 FOLD) | §7.4 |
| `AUTHORITY_CHECK_EVALUATED` (F.P-U-A) | EventBus (recommended) | OpsRunEvent (REQUIRED) | Class-1 audit-forever | §10.3.1 | §20.9 |
| `AUTHORITY_DECISION_OVERRIDDEN` (F.P-U-A) | EventBus (recommended) | OpsRunEvent (REQUIRED) | Class-1 audit-forever | §10.3.1 | §20.9 |
| `AUTHORITY_POLICY_BOUND_TO_USER` (F.P-U-A) | EventBus (recommended) | OpsRunEvent (REQUIRED) | Class-1 audit-forever | §10.3.1 | §20.9 |
| `BRIDGE_DISPATCHED` (plane §10.2) | EventBus | None (canonical-only) | Class-2 bounded | §10.3.3 | §10.2 |
| `NON_BRIDGE_LEARNING_WRITE` (plane §10.3) | EventBus | None | Class-2 bounded | §10.3.3 | §10.3 |
| `CROSS_DOMAIN_LEARNING_ROUTED` (plane §10.4) | EventBus | None | Class-2 bounded | §10.3.3 | §10.4 |
| `EXTERNAL_SIGNAL_INGESTED` (plane §10.5) | EventBus (post-D6) | None | Class-2 bounded | §10.3.3 | §10.5 |
| `SHADOW_SERVICE_INVOKED` (plane §10.6) | EventBus (post-consolidation) | None | Class-2 bounded | §10.3.3 | §10.6 |
| `verification_outcome_plane` event (subsumed) | Subsumed into `HAI_VERIFICATION_RECORDED` per S2002 §10 single-emission rule | (same) | Class-1 bounded-history | (subsumed) | §10 SIGN batch 2 Q6 STRENGTHEN |
| `HAI_mediated_plane` event (subsumed) | Subsumed into `HAI_DECISION_RECORDED` per S2002 §10 single-emission rule | (same) | Class-1 bounded-history | (subsumed) | §10 SIGN batch 2 Q6 STRENGTHEN |

**Verification per parent §5.3 deliverable 3:** every event maps to exactly one *canonical* substrate. Multi-substrate emissions are Class-1 canonical + mirror per §10.3.1 (with same event_id invariant) OR Class-2 canonical-only per §10.3.3. **No unintentional duplicate emission.** The S2002 §14.3 double-emission detector inheritance is satisfied by this mapping.

**§14.3 double-emission detector binding (Rigby S2003 SIGN cycle 1 batch 1 Q3 STRENGTHEN):** The detector MUST treat the canonical substrate as the source of truth; any mirror emission (§10.3.1) MUST carry the same `event_id` AND be tagged `mirror_of=<canonical>` (envelope field on the mirror substrate, e.g., `OpsRunEvent.payload['mirror_of'] = 'eventbus:HAI_AUTO_APPROVED'`) so the detector distinguishes a sanctioned mirror from a second canonical emission. Absent the `mirror_of` tag, a second same-event_id emission is classified as duplicate-canonical defect.

**§10.4 scope gate + inclusion criteria (Rigby S2003 SIGN cycle 1 batch 1 Q3 STRENGTHEN):** §10.4 covers events that participate in cross-substrate composition invariants — canonical + mirror + duplicate-emission risk. Events IN scope for §10.4:

- Events that emit on more than one substrate (§10.3.1, §10.3.4).
- Events consumed by governance transitions (any Class-1 governance event).
- Events with Class-2 → Class-1 promotion potential per S2002 §17.3.

Events OUT of scope for §10.4 (documented for scope clarity):

- Non-governance domain events (e.g., `HAI_ITEM_CREATED`, `HAI_PREFERENCE_LEARNED`) that emit on a single substrate + do NOT participate in cross-substrate composition invariants.
- Domain-object state updates (HFR row, HAI row, opportunity row, deliverable row) that are ORM writes, not event emissions per §10.3.2.

**Scope-gate TODO capture hook:** if new HAI-adjacent events emerge (e.g., `HAI_ITEM_CREATED`, `HAI_PREFERENCE_LEARNED` becoming multi-substrate consumers), they MUST be evaluated against §10.4 inclusion criteria and appended to the table if they cross substrate boundaries. Post-arc T-slot F.HAI-EVENT-SCOPE-REVIEW candidate: audit HAI-adjacent event landscape at S2099 xx99 close + at next Group 1800 arc open for §10.4 inclusion drift.

### 10.5 WebSocket ↔ EventBus overlap resolution (parent §5.3 Chris-gate (d))

The S1273 §3.31 known-drift item — "Some semantic surface overlap with WebSocket consumer message types (both broadcast realtime state); relationship undocumented" — resolves here.

**Overlap sites audited at S2003 open:**

Grep of `channel_layer.group_send(` returns ~40 non-test call sites across `ai_core/`, `intelligence/`, `core/`, `sports/`. Cross-referenced against EventBus emissions:

| WebSocket call site | EventBus overlap? | Canonical assignment (D4) | Rationale |
|---|---|---|---|
| `ai_core/consumers/build_activity_consumer.py:88,135,164` | No direct overlap; UI-render for build activity progress | WebSocket canonical (browser-only) | No cross-service backend consumer for build activity progress |
| `intelligence/revenue_tracking_bridge.py:364,373,408,440` | Potential overlap with revenue-domain events | **Recommend EventBus canonical + WebSocket UI-render fanout per §10.3.4** | Revenue signals are backend state; browser UI is a subscriber |
| `ai_core/agents/concrete_executor.py:365,519` | Overlap: concrete_executor writes spider data (F11 substrate #1); ALSO WebSocket group_send | **Migrate to EventBus canonical (F11 T1 slot) + WebSocket UI-render fanout** | Same-substrate as F11 raw redis.publish drift; migration folds together |
| `ai_core/agents/realtime_project_executor.py:508` | UI-render for project progress | WebSocket canonical (browser-only) | Project progress is a UI update, no backend consumer |
| `ai_core/spiders/realtime_publisher.py:321` | Potential overlap with spider substrate | **Recommend EventBus canonical + WebSocket UI-render fanout** | Spider data emission belongs on EventBus canonical (F11 T1 slot resolution); WebSocket is UI fanout |
| `ai_core/spiders/spider_orchestrator.py:1295` | Same as above | Same | Same |
| `ai_core/agents/project_progress_simulator.py:180` | UI-render only | WebSocket canonical | No backend consumer |
| `intelligence/consumers_command_center.py:437` | UI-render for Command Center | WebSocket canonical | UI-only |
| `ai_core/agents/sync_project_executor.py:253` | UI-render for project progress | WebSocket canonical | UI-only |
| `ai_core/intelligence/real_data_orchestrator.py:278` | Potential overlap | **Recommend audit at post-arc T-slot** | Complex; needs per-emission classification |
| `intelligence/real_execution_engine.py:379,388` | Potential overlap with execution events | **Recommend audit at post-arc T-slot** | Complex; needs per-emission classification |
| `intelligence/realtime_engine.py:614,627,647` | Potential overlap with realtime events | **Recommend audit at post-arc T-slot** | Complex; needs per-emission classification |
| `intelligence/system_integration_bridge.py:297,391,442` | Potential overlap with cross-service state | **Recommend EventBus canonical + WebSocket UI-render fanout** | Bridge coordination + browser UI update |
| `intelligence/consumers.py:1170` | UI-render | WebSocket canonical | UI-only |
| `core/websocket_bridge.py:159` | Bridge site | **Recommend audit at post-arc T-slot** | Complex; needs per-emission classification |
| `core/consumers_sports.py:106,127` | UI-render for sports events | WebSocket canonical | UI-only |
| `intelligence/interview_consumer.py:428,438` | UI-render for interview progress | WebSocket canonical | UI-only |
| `intelligence/unified_spider_job_bridge.py:305` | Potential overlap with spider data | **Recommend EventBus canonical + WebSocket UI-render fanout** | Spider substrate |
| `core/unified_platform_bridge.py:88,211,395,442` | Complex — cross-service state coordination | **Recommend EventBus canonical + WebSocket UI-render fanout** | Bridge coordination |
| `sports/orchestration.py:111` | Sports orchestration | **Recommend audit at post-arc T-slot** | Complex; needs per-emission classification |

**D4 recommendation summary:**

- **~9 sites** → migrate to EventBus canonical + WebSocket UI-render fanout per §10.3.4 (post-arc T1 slot).
- **~13 sites** → WebSocket canonical (browser-only UI updates; no backend consumer).
- **~7 sites** → complex; post-arc T2 split-by-owning-app per-emission classification audit (see below).
- **~2 sites** (spider-substrate overlap) → fold into F11 T1 slot resolution.

**Post-arc T2 slot split-by-owning-app (Rigby S2003 SIGN cycle 1 batch 4 Q10 FOLD):**

The 7 complex sites span multiple bridge modules across app boundaries. A single T2 slot per-emission audit across all 7 is likely to sprawl and slip. D4 splits the T2 work by owning-app / boundary with a shared central rubric so the split does not diverge:

| T2 sub-slot | Owning module | Sites in scope | Deliverable |
|---|---|---|---|
| **T2a** | `intelligence/real_data_orchestrator.py` | `:278` | Site-level canonical assignment + ui.render_hint compliance OR promotion to EventBus canonical OR explicit exception entry in intentional dual-emission register (§10.3) |
| **T2b** | `intelligence/real_execution_engine.py` | `:379`, `:388` | Same |
| **T2c** | `intelligence/realtime_engine.py` | `:614`, `:627`, `:647` | Same |
| **T2d** | `intelligence/system_integration_bridge.py` | `:297`, `:391`, `:442` (partial — some already classified) | Same |
| **T2e** | `core/websocket_bridge.py` | `:159` | Same |
| **T2f** | `core/unified_platform_bridge.py` | `:88`, `:211`, `:395`, `:442` | Same |
| **T2g** | `sports/orchestration.py` | `:111` | Same |

**Central rubric (referenced by every T2 sub-slot):**

1. Consult §10.2 per-substrate criteria table.
2. If cross-service backend consumer needs the update: canonical substrate = EventBus. If browser also needs update: emit UI-render fanout per §10.3.4 with `ui.render_hint` envelope.
3. If browser-only: canonical substrate = WebSocket. No EventBus emission required.
4. If dual-emission required but neither §10.3.1 nor §10.3.4 fits: register as new intentional pattern per §10.3 (requires arc-owned scope extension — do NOT invent unilaterally).
5. If migration required, update S2003 §17.6 rollup with per-site status when T2 sub-slot ships.

**Owning-app arc mapping:**

- T2a-T2c-T2d + T2f (intelligence + core bridges): Group 2000+ post-arc queue OR whichever arc owns the intelligence bridge modules.
- T2b + T2c: intelligence realtime execution — coordinate with Group 1600 Content arc.
- T2e (`core/websocket_bridge.py`): Group 2000+ post-arc queue.
- T2g (`sports/orchestration.py`): Group 1500 Sports arc.

Split-by-owning-app preserves tractability + makes scheduling / assignment real. A single per-emission classification audit across 7 sites in 6 bridge modules is likely to sprawl; per-module scope keeps the T2 slot bounded.

**D4 canonical assignment rule** (for adoption discipline):

> A WebSocket-only broadcast is sanctioned when the consumer audience is exclusively browser session-scoped UI. If any cross-service backend consumer needs the state change, the emission MUST be EventBus canonical + WebSocket UI-render fanout per §10.3.4 pattern. Migration of existing WebSocket-only backend-relevant emissions is a post-arc T1 slot obligation; new emissions ship on the D4 pattern.

### 10.6 Composition contract adoption discipline (D1 continued)

Per playbook §14.5 no-implementation rule, this section does not ship migration code. It records the adoption-discipline expectations for arcs adopting the contract:

**Pre-adoption checklist for a new emission:**

1. Classify the emission per Axis A (coordination vs telemetry).
2. Classify the emission per Axis B (canonical audience).
3. Classify the emission per Axis C (retention class).
4. Consult §10.2 table for the canonical substrate.
5. If dual-emission is needed, consult §10.3 register for the sanctioned pattern.
6. If none of the sanctioned patterns fits, DO NOT invent a new dual-emission pattern — surface as post-arc T-slot for contract extension.

**Pre-adoption checklist for a substrate migration:**

1. Confirm the current emission classifies as drift per §17 duplicate-emission audit.
2. Identify the canonical substrate per §10.2.
3. Coordinate with the current-substrate owner (§5 service ownership) + the canonical-substrate owner.
4. Migration ships in an arc-owned PR + deprecation slot for the current substrate.
5. F.COMPOSITION-CONTRACT-CI-CHECK candidate: flag new call sites that bypass the canonical substrate for review.

## 11. Existing Documentation

**Q10 — What documentation of cross-substrate composition already exists?**

At S2003 open, the following authoritative surfaces mention substrate composition. None is a complete composition contract; each is scoped narrower.

| Doc | Coverage | Gap S2003 closes |
|---|---|---|
| `docs/EVENT_SYSTEM_INVENTORY.md` | Enumerates EventBus streams + telemetry substrates + naming conventions | Does not define per-substrate criteria; does not resolve WebSocket ↔ EventBus overlap; does not register dual-emission patterns |
| `docs/research/platform_architecture_inventory.md` §3.25 (Observability) | Names CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord as telemetry substrates | Does not codify the coordination-vs-telemetry axis explicitly |
| `docs/research/platform_architecture_inventory.md` §3.31 (Event Bus / Streams) | Establishes the substrate paragraph + coordination-vs-telemetry distinction | Flags WebSocket ↔ EventBus overlap as undocumented drift; does not resolve |
| `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md` | EventBus producer/consumer map + F1-F18 findings + F11 three-substrate drift | Does not design composition arbitration; F11 flagged for P3 inheritance |
| `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md` §7.9 | Canonical + mirror emission policy for HAI Class-1 events | Scoped to Class-1 HAI; P3 generalizes to full 6-substrate contract |
| `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md` §17.2 | 20-row consumer registry per event | Scoped to HAI + plane events; P3 consumes as input |
| `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md` §17.3 | Two-class retention posture (Class-1 audit-forever + Class-1 bounded-history + Class-2 bounded) | P3 extends to full six-substrate DLQ posture |
| `docs/research/symbol_mapping_option_selection_design.md` §10.3.1 | Four Symbol Mapping graduation triggers | P3 audits trigger status at S2003 open (§19.1) |
| `docs/topics/celery-workers.md` | Celery worker + queue + memory management | Substrate perspective: CeleryTaskEvent ownership |
| `docs/topics/personal-assistant.md` | PA tool dispatch semantics | Substrate perspective: ToolCallRecord ownership |
| `docs/topics/employee-os.md` | MissionRunner orchestration + OpsRunEvent audit | Substrate perspective: OpsRunEvent ownership |
| `docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md` | Precedent — Group 1900 Cat C Cross-Plane Composition Design | Design-contract-shape precedent (not substrate but plane-shaped composition); §10.2 3-axis pattern echoes 1903's shape |
| `docs/EMPLOYEE_OS_PRIMITIVES.md` | Employee OS primitive anti-duplication | Constraint on OpsRunEvent expansion; extended in §17.3 parallel-telemetry pattern |

**Contract stewardship gap addressed:** No single doc named the arbitration rule set at S2003 open. This audit is that doc.

## 12. Research Coverage

**Q11 — Which prior research has covered cross-substrate composition, at any depth?**

Cross-substrate composition prior research at S2003 open:

| Session | Contribution | Depth |
|---|---|---|
| S1273 §3.31 (S1273 EventBus / Streams) | Substrate paragraph + coordination-vs-telemetry distinction + WebSocket ↔ EventBus semantic overlap flag | Baseline |
| S1273 §3.25 (Observability) | CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord telemetry enumeration | Baseline |
| S1274 §11 + §12.1 (Symbol Mapping graduation + producer/consumer registry style) | Substrate strength classification pattern (STRONG / WEAK / MISSING) + 4-tier graduation triggers | Baseline |
| S1275 (Symbol Mapping event schema) | `schema_version` per-event envelope + substrate-change bump rules (§7.5) | Baseline |
| S1098 (LLM call telemetry arc) | LLMCallWrapper canonical entrypoint + LLMCallEvent 30-day TTL policy | Owner |
| S861 (Extended-PA arc, ToolCallRecord introduction) | ToolDispatcher canonical entrypoint + ToolCallRecord shape | Owner |
| S1234 (Employee OS arc) | MissionRunner + OpsRunEvent audit lifecycle | Owner |
| S1219 + S1220 (LLM watchdog + cleanup) | LLMCallEvent watchdog (PR #2519) + cleanup task (PR #2520) | Retention policy |
| S1806 §10 (HAI six-plane fragmentation catalog) | Six planes lacking durable event emission → six-plane learning-surface Class-2 events per S2002 §10 | Contract input |
| S1899 §8.1 (T0/Gate joint retention ADRs) | R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.HAI.RETENTION-UNIFIED-ADR — parked as joint ADR | Retention posture input |
| S1903 §19 (Group 1900 Cat C Cross-Plane Composition Design) | F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM inherited to P3 | Inheritance |
| S2000 (parent scoping) | 4-child taxonomy + Chris-gate 4-verdict shape | Scope declaration |
| S2001 (P1 EventBus producer/consumer map) | 18 findings F1-F18 + F11 three-substrate spider-data drift + F14/F15 handler-failure / DLQ gap | Direct inheritance |
| S2002 (P2 HAI event contract design) | Canonical + mirror rule §7.9 + consumer registry §17.2 + retention posture §17.3 + F.PER-USER-AUTHORITY §20.9 | Direct inheritance |

**Depth verdict:** MODERATE. Prior arcs have shipped the substrate inventory + per-substrate ownership + Class-1 governance dual-emission pattern. What was missing at S2003 open: the *arbitration rule set* — when to pick which substrate for a new emission. This audit ships it.

## 13. Architecture Maturity

**Q12 — How mature is the composition surface at S2003 open?**

**MODERATE — pre-P3, ownership scattered.** At S2003 open, the composition surface is:

- **Substrate ownership:** established per substrate (§5 service ownership). Each of the six substrates has a canonical entrypoint + owning service.
- **Dual-emission discipline:** partial — only S2002 §7.9 canonical + mirror is codified. WebSocket ↔ EventBus overlap is undocumented drift (D4 closes).
- **Substrate migration discipline:** ad-hoc — F11 three-substrate spider-data drift has been observed but no migration owner named at S2003 open (D2 closes with T1 slot).
- **DLQ retention posture:** partial — MAXLEN=1000 current + F14/F15 correctness gap (D3 documents; joint ADR resolves).
- **Composition contract enforcement:** none — no runtime enforces the substrate contract; adoption discipline is documentation + code review.

**Q13 — What does mature composition look like?**

Post-P3 canonical target state:

1. **§10.2 contract table adopted:** every arc consults the table before shipping a new emission.
2. **§10.3 dual-emission register enforced:** any new dual-emission pattern requires arc-owned scope extension.
3. **F11 drift resolved:** SpiderAgentConnector.publish_spider_data migrated to `publish_spider_data_event`; the two `SpiderAgentConnector` classes de-duplicated.
4. **DLQ correctness closed:** F14 handler-failure retry + F15 DLQ reader shipped (post-arc T-slots per S2001 §19 + P3 §19.3).
5. **F.WEBSOCKET-BROADCAST-WRAPPER shipped:** canonical wrapper analogous to `publish_*_event` for cross-cutting UI state broadcasts (post-arc T-slot).
6. **F.COMPOSITION-CONTRACT-CI-CHECK shipped:** CI grep + guardrail flagging new bypass call sites for review.
7. **Joint retention ADRs resolved:** DLQ retention posture (D3) folded into R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.HAI.RETENTION-UNIFIED-ADR resolution.

Post-P3 remaining maturity gap: composition-contract enforcement remains documentation-based until F.COMPOSITION-CONTRACT-CI-CHECK ships. Documentation + code review is the interim enforcement.

## 14. Known Drift

**Q23 — Where does current runtime disagree with the composition contract?**

The following drift items are known at S2003 open. Each is either resolved in this audit (with recommendation for post-arc T-slot execution) or explicitly parked with rationale.

### 14.1 F11 three-substrate spider-data drift (S2001 §16 SIGN-expanded, inherited)

- **Substrate #1:** `ai_core/agents/spider_agent_connector.py:311:SpiderAgentConnector.publish_spider_data` uses raw `redis.publish()` — bypasses EventBus wrapper + Streams durability.
- **Substrate #2:** `intelligence/spider_agent_connector.py:20:SpiderAgentConnector` (same class name, different app) uses in-process `Dict[str, List[str]]` routing table — no persistence, no pub/sub.
- **Substrate #3:** EventBus `publish_spider_data_event` wrapper at `event_bus.py:539` — dormant (0 non-definition callers per S2001 F1).

**Contract violation:** The composition contract (§10.2) sanctions ONE canonical substrate per logical signal. Spider-data → agents has three parallel substrates + two identically-named classes.

**Recommendation (D2 HIGH priority):**

1. **Canonical substrate:** EventBus `publish_spider_data_event` per §10.2 EventBus row.
2. **Migration path:**
   - Add `publish_spider_data_event` call sites to `ai_core/agents/concrete_executor.py:637-638` + `core/views_agent_intelligence.py:352,355` (Substrate #1 consumers) with backward-compat during transition.
   - Refactor `intelligence.SpiderAgentConnector._build_routing_map` (Substrate #2) to consume EventBus SPIDER_DATA stream OR to be replaced by an ORM read of persisted spider data (Substrate #2 is in-process routing, not emission — arguably out-of-scope for the composition contract, but the class-name collision demands consolidation).
   - Deprecate `ai_core.SpiderAgentConnector.publish_spider_data` after consumer migration + delete the raw redis.publish() call site.
   - De-duplicate the two `SpiderAgentConnector` classes: rename intelligence version to `SpiderAgentRouter` (or similar) to clarify its role.
3. **Timing:** F11 T1 slot post-arc.
4. **Owner:** TBD at S2003 close — Chris-gate (b) decides + Group 2000+ post-arc queue owns.

### 14.2 WebSocket ↔ EventBus semantic overlap drift (S1273 §3.31 inherited)

**Contract violation:** §10.2 sanctions WebSocket for browser-only UI updates + EventBus for cross-service backend state. §10.5 audit surfaces ~9 sites emitting backend-relevant state on WebSocket only, without EventBus canonical.

**Recommendation (D4):** §10.5 recommendation table records per-site canonical assignment. Migration is post-arc T1 slot per site classification.

**Timing:** T1 slot post-arc.
**Owner:** TBD at S2003 close — Chris-gate (d) decides + per-affected-domain arc owns migration.

### 14.3 EventHandlerRegistry dispatch vs worker streams subscription drift (S2001 §17 F8-adjacent, inherited)

**Contract violation:** S2001 §17 F8 flagged `SYSTEM_ALERT` handler registered by `event_type` string but no worker subscribes to the `SYSTEM_ALERT` stream. Dual-mechanism drift (dispatch-by-event_type + subscribe-by-stream) creates the possibility of registered-but-unheard events.

**Recommendation:** Post-arc T-slot: either (a) collapse to a single mechanism (subscribe-by-event_type OR subscribe-by-stream), or (b) document the two-layer contract explicitly + add a CI check that verifies every registered handler has at least one subscribed worker.

**Timing:** T2 slot post-arc.
**Owner:** Group 2000+ P4 CONSOLIDATION candidate per S2001 §17.

### 14.4 OpsRunEvent Class-1 vs Class-2 tagging drift (S2003 new observation)

**Contract observation:** S2002 §17.3 two-class retention posture assumes each OpsRunEvent row is tagged Class-1 audit-forever or Class-2 bounded. At S2003 open, `OpsRunEvent` model does NOT carry a `retention_class` field. All rows are effectively Class-1 (no default TTL).

**Contract obligation:** Adopters of the composition contract MUST tag OpsRunEvent writes with retention class. Absent the field, cleanup task cannot distinguish; audit rows accumulate without bound.

**Recommendation:** Post-arc T-slot F.OPSRUNEVENT-CLASS-TAG: add `retention_class` CharField to OpsRunEvent + migrate existing rows via backfill.

**Data-gated promotion criteria (Rigby S2003 SIGN cycle 1 batch 2 Q5 STRENGTHEN):** T2 remains the default slot. Elevate to T1 if any of the following measured thresholds fire:

- OpsRunEvent row-count growth exceeds > 5,000 rows/day sustained over 14 days (~72k/month, Class-1 audit-forever posture becomes unbounded storage risk).
- `core_opsrunevent` table + index size exceeds > 5 GB on prod (measurable via `pg_total_relation_size`).
- Runtime OpsRunEvent producer sites expand beyond the 7 current runtime sites without wrapper adoption (F.OPSRUNEVENT-WRITE-WRAPPER not shipped) — indicates architectural drift outpacing observability.

**Baseline (Rigby S2003 verification at S2003 open):** `core_opsrunevent.estimated_rows=224`, `core_opsrun.estimated_rows=30`. Volume is far below threshold at S2003 open — T2 is defensible.

**Split-slot posture (Rigby S2003 SIGN cycle 1 batch 2 Q5 STRENGTHEN):** the F.OPSRUNEVENT-WRITE-WRAPPER can ship independently of TTL policy — the wrapper can set `retention_class` on write (via §15.4 context-manager pattern) even before the joint retention ADR finalizes Class-1 vs Class-2 semantics. TTL enforcement (cleanup task honoring `retention_class`) can remain in T2 while the wrapper + tag ships earlier if T2 promotion fires for one of the thresholds above.

**Timing:** T2 slot post-arc (baseline); T1 elevation if measured thresholds fire.
**Owner:** Employee OS arc + Group 1700 Observability arc jointly.

### 14.5 Correlation-ID propagation gap (S2003 new observation, §10.3.5 pattern)

**Contract observation:** §10.3.5 parallel-telemetry-per-concern pattern relies on `correlation_id` propagation across the call stack. At S2003 open, correlation_id propagation is inconsistent — some substrate writes carry correlation_id, others do not.

**Recommendation:** Post-arc T-slot F.CORRELATION-ID-PROPAGATION: audit correlation_id coverage across substrate writes + adopt context-managed propagation (e.g., contextvars).

**Timing:** T2 slot post-arc.
**Owner:** Group 1700 Observability arc.

## 15. Known Technical Debt

**Q24 — What technical debt does the composition contract inherit or create?**

### 15.1 DLQ retention decision (D3 — parent §5.3 Chris-gate (c))

**Current state:** DLQ MAXLEN=1000 per `event_bus.py:468`. Receives only parse-error path (S2001 §17.1); handler failures do NOT reach DLQ (F14). No worker reads DLQ (F15).

**Recommendation (D3 — conditional posture, Rigby S2003 SIGN cycle 1 batch 3 Q7 FOLD):**

At S2003 open, DLQ is NOT an operational control surface — F14 blocks handler-failure flow, F15 blocks reader/alerting. "DLQ retention" as a policy parameter is *future*, not current. D3 is therefore structured as a **conditional posture** so Chris ratifies the conditional shape, not a permanent posture.

**D3.a — Conditional canonical (post-F14 + F15 closure):**

Once F14 + F15 close (handler failures route to DLQ + DLQ reader + alerting exists), DLQ becomes an active remediation surface. Default DLQ retention is **MAXLEN=1000** (bounded, cost-safe, low-volume expected). Explicit joint-ADR override slot: if joint retention ADR resolution (R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.HAI.RETENTION-UNIFIED-ADR) determines DLQ needs audit-forever posture for specific error classes, override is documented per S2002 §17.3 adopter-override rule.

**D3.b — Interim posture (until F14 + F15 closure):**

DLQ retention is **non-binding / undefined** for correctness because DLQ is not in the critical path. Correctness relies on:

- **At-least-once semantics** — inherit S2002 §17.1 rule 6 (Class-1 emission requires at-least-once delivery via consumer-side retry + idempotency, NOT DLQ-as-correctness).
- **Idempotency at consumer** — inherit S2002 §17.1 rule 6 (consumers process each event as if it may fire ≥1 time; duplicate emission is a bug at producer, not consumer).
- **Consumer replay + monitoring obligation** — inherit S2002 §17.1 rule 7 (adopters MUST document consumer retry/replay procedures AND detect "stuck pending" events via monitoring/stats surface).
- **Audit trail safety** — inherit S2002 §17.1 rule 6 (governance consumers write append-only receipt for duplicate observability).

The MAXLEN=1000 current posture at `event_bus.py:468` remains in place mechanically, but its *semantic* meaning (retention as correctness parameter) does not fire until D3.a activates.

**F14 + F15 closure as the trigger for D3.a activation:** D3 is not ratified as a permanent posture at S2003 close. Chris ratifies the conditional shape. When F14 + F15 close per §19.3 T1 slot, the arc that closes them ALSO promotes D3 from conditional to canonical + writes an ADR referencing this section.

**Post-arc T-slot obligations (Rigby S2003 SIGN cycle 1 batch 3 Q8 STRENGTHEN — ownership assigned):**

- **F14 T1 slot** (handler-failure retry loop with at-most-N-retries + move-to-DLQ on exhaustion):
  - **Primary owner:** Group 2000+ (Event / Integration Architecture) — this is EventBus consumption / ack / retry semantics + routing to DLQ. Substrate correctness lives with the substrate owner.
  - **Assist:** P4 CONSOLIDATION (S2004) may implement shared wrappers / utilities, but does NOT own the correctness decision. P4 assists on wrapper/utility integration.
- **F15a T1 slot** (DLQ reader / consumer exists + runs):
  - **Primary owner:** Group 2000+ (substrate-specific operational requirement — the DLQ is an EventBus substrate).
- **F15b T1 slot** (alerting + observability for DLQ depth + age):
  - **Primary owner:** Group 1700 Observability arc (metrics, alerts, dashboards).
  - **Coordination:** F15a producer → F15b consumer. Ownership split by concern; F15a ships the read surface, F15b ships the alerting/dashboards on top.

**Joint retention ADR handoff:** S1899 §8.1 items 4 + 5 remain T0/Gate. This audit's D3 recommendation is *input* to the ADR resolution, not an execution.

### 15.2 Six-substrate composition contract enforcement gap

**Current state:** No runtime enforces the composition contract. Adoption discipline relies on documentation + code review.

**Recommendation:** Post-arc T-slot F.COMPOSITION-CONTRACT-CI-CHECK — CI-visible grep + guardrail that flags:

- New `channel_layer.group_send(` call sites for D4 canonical-assignment review.
- New `.publish(...)` bypass of `publish_*_event` wrappers for defect review.
- New `OpsRunEvent.objects.create(...)` writes outside sanctioned entry points (§5 owning-service exceptions apply).
- New `EventStream` enum value additions for D1 composition consultation.

**Timing:** T2 slot post-arc.
**Owner:** Group 2000+ post-arc queue.

### 15.3 F.WEBSOCKET-BROADCAST-WRAPPER gap

**Current state:** WebSocket has no canonical broadcast wrapper analogous to `publish_*_event`. ~40 call sites each assemble their own message dict.

**Recommendation:** Post-arc T-slot F.WEBSOCKET-BROADCAST-WRAPPER — design + ship canonical wrappers for cross-cutting UI state broadcasts (e.g., `broadcast_workspace_state_update`, `broadcast_agent_progress`, `broadcast_deliverable_ready`). Per-app one-off broadcasts may remain unwrapped as long as the message dict shape is documented in the consumer class.

**Timing:** T2 slot post-arc.
**Owner:** Frontend + WebSocket-owning arc TBD (candidate: Group 2000+ post-arc queue).

### 15.4 F.OPSRUNEVENT-WRITE-WRAPPER gap

**Current state:** OpsRunEvent is written via direct `OpsRunEvent.objects.create(...)` or `OpsRun.append_event(...)` from 7 runtime call sites. Highest scatter of all six substrates. No context-manager wrapper analogous to `LLMCallWrapper`.

**Recommendation:** Post-arc T-slot F.OPSRUNEVENT-WRITE-WRAPPER — consider adopting a `with OpsRun.step_boundary(step_name, mission_id) as step: ...` context manager pattern that:

1. Writes step_started row on `__enter__`.
2. Writes step_completed row on `__exit__` (with verdict + payload).
3. Enforces `retention_class` tag (per §14.4 F.OPSRUNEVENT-CLASS-TAG).
4. Enforces `correlation_id` propagation (per §14.5).

**Timing:** T2 slot post-arc.
**Owner:** Employee OS arc.

### 15.5 F14 + F15 handler-failure / DLQ correctness gap (S2001 inherited)

**Current state (per S2001):** F14 = handler-failure retry loop with no give-up; F15 = no DLQ reader + no alerting on DLQ growth.

**Recommendation:** Post-arc T1 slot: address per S2001 §19 items 3 + adjacent. Prerequisite for D3 DLQ retention decision to become correctness surface.

**Timing:** T1 slot post-arc.
**Owner:** S2001 named per §19; deferred to Group 2000+ post-arc queue.

### 15.6 F17 replay-as-regression-tool gap (S2001 inherited)

**Current state (per S2001):** `EventBus.replay()` exists at `event_bus.py:311` with zero callers. No management command exists to seed a stream + run a worker + assert consumer output. Composition contract validation would benefit from replay-as-regression.

**Recommendation:** Post-arc T-slot per S2001 §19 item 5 — ship replay management command + test harness.

**Timing:** T2 slot post-arc.
**Owner:** Group 2000+ post-arc queue.

## 16. Boundary Violations

**Q25 — Where does current runtime violate substrate boundaries?**

### 16.1 F11 raw redis.publish() boundary violation (S2001 §16 inherited, SIGN-expanded)

Per §14.1 F11: `ai_core/agents/spider_agent_connector.py:311:SpiderAgentConnector.publish_spider_data` uses raw `redis.publish()` on `self.channels['spider_data']` — bypassing:

1. **The EventBus wrapper:** `publish_spider_data_event` at `event_bus.py:539` is dormant while a parallel raw-redis-publish surface exists.
2. **The EventBus Streams substrate:** pub/sub semantics (fire-and-forget, no consumer group discovery, no durability) instead of Streams semantics (durable + replayable + consumer group).
3. **The composition contract:** the raw redis.publish() surface is NOT in the six named substrates + is drift per §10.2.

**Boundary violation classification:** substrate boundary — the emission crosses from the sanctioned EventBus substrate to a non-sanctioned pub/sub substrate.

**Recommendation:** §14.1 D2 F11 T1 slot deprecation.

### 16.2 `SpiderAgentConnector` class-name collision (S2001 §16 SIGN-expanded)

Two classes named `SpiderAgentConnector` exist in parallel Django apps:

- `ai_core/agents/spider_agent_connector.py:40:SpiderAgentConnector` — raw redis.publish() emission substrate.
- `intelligence/spider_agent_connector.py:20:SpiderAgentConnector` — in-process routing table (no emission substrate; different responsibility).

**Boundary violation classification:** naming boundary — two responsibilities collapsed under one class name across app boundaries. Import-time collision risk + developer confusion.

**Recommendation (Rigby S2003 SIGN cycle 1 batch 2 Q6 FOLD compat-shim discipline):** F11 T1 slot deprecation includes renaming the `intelligence` version to `SpiderAgentRouter` (or similar) to clarify its role. The rename MUST use a compat shim to avoid breaking existing imports during the deprecation window:

```python
# intelligence/spider_agent_connector.py after rename:
class SpiderAgentRouter:
    """Renamed from SpiderAgentConnector per S2003 F11 T1 slot; see §14.1."""
    ...

# Compat alias for backward compatibility during deprecation window:
SpiderAgentConnector = SpiderAgentRouter  # DEPRECATED — see S2003 F11 T1 slot
```

**Verified at S2003 open (Rigby S2003 verifier):**

- `SpiderAgentConnector` name grep across the repo returns 6 files matched. 5 are imports/instantiations at `core/tasks.py:1355,1359`, `core/management/commands/activate_spiders.py:10,234`, `core/management/commands/process_spider_data.py:6,16`, `core/tasks_spiders.py:260,307`, plus the two class definitions. All 5 imports use `from intelligence.spider_agent_connector import SpiderAgentConnector` (module-qualified), NOT `isinstance(x, SpiderAgentConnector)` or `x.__class__.__name__ == 'SpiderAgentConnector'` runtime name lookups.
- `__class__.__name__` grep: 45 files matched across the repo but ZERO reference `SpiderAgentConnector` in that pattern; the runtime-name-lookup breakage risk is nil.

**Compat-shim discipline:**

- Introduce `SpiderAgentRouter` as the canonical class name.
- Keep `SpiderAgentConnector = SpiderAgentRouter` alias in the module.
- Keep the old module path (`intelligence/spider_agent_connector.py`) exporting both names.
- Add a `DeprecationWarning` on `SpiderAgentConnector` alias usage per Python `warnings` module.
- Deprecation window: 60 days (one arc-cycle) OR until all callers migrate to `SpiderAgentRouter`, whichever is later.
- **Removal criteria:** all callers migrated + zero non-test `SpiderAgentConnector` name references in code + deprecation window elapsed.

The compat-shim reduces F11 T1 slot risk from "breaking rename" to "graceful deprecation." Post-arc T1 slot ownership decides deprecation timeline.

### 16.3 OpsRunEvent write-site scatter (S2003 new observation, §15.4 T-slot)

`OpsRunEvent.objects.create(...)` + `OpsRun.append_event(...)` fire from 7 runtime call sites across 6 files:

- `core/employees/mission_runner.py` (2 sites — MissionRunner step boundaries + verdicts)
- `core/tools/ops_run_tracker.py` (1 — OpsRun helper)
- `core/employees/jobs.py` (1 — employee bootstrap)
- `core/models_ops_runs.py` (1 — model helper)
- `core/signals/rigby_delegation_signals.py` (1 — Rigby delegation signal handler)
- `core/services/rigby_mission_delegation.py` (1 — Rigby delegation runtime)
- `core/services/td_handlers_rigby_work_queue.py` (1)

**Boundary violation classification:** owner boundary — MissionRunner is the sanctioned Employee OS owner + Rigby delegation is a distinct concern. The mixture at S2003 open is not a violation per se (all 7 sites write mission-audit-relevant rows), but the lack of a canonical wrapper makes future ownership drift likely.

**Recommendation:** §15.4 F.OPSRUNEVENT-WRITE-WRAPPER + §14.4 F.OPSRUNEVENT-CLASS-TAG jointly close this by making the write path canonical.

### 16.4 EventHandlerRegistry dispatch mechanism boundary (S2001 §17 F8-adjacent, inherited)

Per §14.3: dispatch-by-event_type + subscribe-by-stream are two parallel mechanisms. Not a violation per se, but the dual-mechanism creates surface for registration drift (F8 SYSTEM_ALERT case).

**Recommendation:** §14.3 recommendation (post-arc T2 slot).

## 17. Duplicate or Overlapping Systems

**Q26 — Where do systems emit to more than one substrate for the same logical event?**

Duplicate-emission audit — the load-bearing content of parent §5.3 deliverable 2. Each observed dual-emission site is classified as `intentional` (sanctioned by §10.3 register) OR `drift` (unsanctioned; migration recommended) OR `unresolved (Chris-gate pending)`.

### 17.1 Intentional dual-emission — Class-1 governance canonical + mirror (S2002 §7.9)

**Pattern:** EventBus canonical + OpsRunEvent mirror for HAI four candidate transitions + F.PER-USER-AUTHORITY three governance events per §10.3.1 register.

**Sites at S2003 open:** ZERO runtime call sites — the S2002 §7.9 pattern is contract-declared, adoption is post-arc T-slot per S2002 §6.2 shared wrapper mandate.

**Classification:** `intentional` — sanctioned by §10.3.1.

**Duplicate detection at adoption time:** shared wrapper enforces same `event_id` invariant per S2002 §7.9. Bypass detection: grep for direct `OpsRunEvent.objects.create(event_type='hai_*')` calls outside the shared wrapper — flag as defect.

**Graduation trigger — post-adoption detector re-run (Rigby S2003 SIGN cycle 1 batch 3 Q9 STRENGTHEN):** the ZERO-sites observation is a snapshot at S2003 open. To prevent the observation from rotting into stale evidence, adopters re-run the composition-contract detector loop when either trigger fires:

- **Trigger A:** ≥3 canonical + mirror producers ship to production (measured via `publish_hai_*_event` wrapper call-site grep + OpsRunEvent `mirror_of='eventbus:HAI_*'` row query).
- **Trigger B:** Any HAI transition emits canonical + mirror to production (even one producer counts as first adoption).

When either fires:

1. Re-run §14.3 duplicate-emission detector against production emissions (grep for same `event_id` with `mirror_of` tag missing → defect).
2. Re-validate the §10.3 intentional-dual-emission register — no unlisted patterns emerged.
3. Verify DLQ flow (post-F14/F15 closure) — canonical + mirror emissions do not blow up DLQ retention thresholds.

**Retire the ZERO-sites observation upon first production adoption.** The observation is provisional; drop it as soon as at least one canonical + mirror producer ships. Post-arc T-slot F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN candidate: register in §19.

This creates an enforcement loop instead of a static observation.

### 17.2 Drift dual-emission — F11 three parallel substrates for spider-data (S2001 §16 inherited)

**Pattern:** Three substrates carry "route spider data to agents" — raw redis.publish (ai_core) + in-process routing table (intelligence) + EventBus SPIDER_DATA stream (dormant).

**Sites at S2003 open:**

- Substrate #1 (raw redis.publish):
  - Emission: `ai_core/agents/spider_agent_connector.py:322` (`self.redis_client.publish(self.channels['spider_data'], ...)`)
  - Real callers: `ai_core/agents/concrete_executor.py:637-638`, `core/views_agent_intelligence.py:352,355`
- Substrate #2 (in-process routing):
  - Emission: `intelligence/spider_agent_connector.py:31` (`_build_routing_map`)
  - Real callers: `core/tasks_spiders.py:260,307`, `core/tasks.py:1355,1359`, `core/management/commands/process_spider_data.py:6,16`, `core/management/commands/activate_spiders.py:10,234`
- Substrate #3 (EventBus SPIDER_DATA):
  - Wrapper: `event_bus.py:539:publish_spider_data_event`
  - Real callers: ZERO (dormant per S2001 F1)

**Classification:** `drift` — HIGH cleanup priority per D2 F11 T1 slot per §14.1.

**Duplicate detection:** direct grep already surfaces the three substrates. Post-migration, the F.COMPOSITION-CONTRACT-CI-CHECK (§15.2) would flag re-emergence.

### 17.3 Non-duplicate parallel telemetry — CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord (§7.7)

**Pattern:** A single execution writes to multiple telemetry substrates, each recording a distinct concern.

**Sites at S2003 open:** ~all Celery-task-hosted PA agentic loops execute the §7.7 flow. Examples:

- Rigby delegation invocation: CeleryTaskEvent (task lifecycle) + OpsRunEvent (mission step) + ToolCallRecord (per tool dispatch) + LLMCallEvent (per LLM call).
- Autonomous mission execution: same.

**Classification:** `intentional per §10.3.5 parallel-telemetry-per-concern` — NOT duplicate emission. Each substrate records a distinct concern; `correlation_id` envelope ties them together.

**Duplicate detection at adoption time:** N/A — this is not duplicate emission. §14.5 correlation-ID propagation gap is the relevant post-arc T-slot.

### 17.4 Non-duplicate audit-table backing — HAI EventBus + HFR/HAI row (S2002 §17.3 clarified in §10.3.2)

**Pattern:** HAI_DECISION_RECORDED + HAI_VERIFICATION_RECORDED emit on EventBus canonical while the domain HFR/HAI ORM row is separately updated with verification/decision state.

**Sites at S2003 open:** N/A — S2002 §7.9 wrapper adoption is post-arc.

**Classification:** `intentional per §10.3.2 audit-table backing` — NOT duplicate emission. The HFR/HAI row is domain-object state, not a copy of the event envelope. Distinction: `event_id` invariant does NOT hold between EventBus event and HFR row (HFR row has its own `id` UUID).

### 17.5 Non-duplicate class-name collision — SpiderAgentConnector × 2 (§16.2)

**Pattern:** Two classes named `SpiderAgentConnector` exist in parallel Django apps but implement different responsibilities.

**Sites at S2003 open:** per §16.2 file paths.

**Classification:** `drift` per §16.2 — not duplicate emission but naming boundary drift. Cleanup folded into F11 T1 slot per §14.1.

### 17.6 Unresolved — potential WebSocket ↔ EventBus overlap per §10.5 audit

**Pattern:** ~9 WebSocket call sites emit backend-relevant state without EventBus canonical.

**Sites at S2003 open:** per §10.5 recommendation table (revenue_tracking_bridge, spider_agent_connector overlap sites, system_integration_bridge, unified_platform_bridge, etc.).

**Classification:** `unresolved — Chris-gate (d) pending` — D4 recommends per-site canonical assignment; migration is post-arc T1 slot per site classification.

### 17.7 Duplicate-emission audit rollup

| # | Site / pattern | Classification | Cleanup priority |
|---|---|---|---|
| 17.1 | HAI Class-1 canonical + mirror | intentional | Adoption is post-arc T-slot per S2002 |
| 17.2 | F11 three parallel spider-data substrates | drift | **HIGH — T1 slot (D2)** |
| 17.3 | Parallel telemetry per concern (Celery/LLM/OpsRun/Tool) | intentional | Correlation-ID propagation T2 slot |
| 17.4 | HAI EventBus + HFR/HAI row | intentional | Wrapper adoption per S2002 |
| 17.5 | SpiderAgentConnector class-name collision | drift | Folded into F11 T1 slot |
| 17.6 | WebSocket ↔ EventBus overlap sites (~9) | unresolved — Chris-gate (d) | **MEDIUM — T1 slot per D4** |

**Zero-drift observation at S2003 open:** aside from F11 (already inherited) + WebSocket overlap (S1273 §3.31 known-drift), NO new dual-emission drift is observed across the six-substrate composition contract at S2003 open. The rollup satisfies parent §5.3 deliverable 2 (duplicate-emission audit) + Chris-gate (b) (duplicate-emission cleanup priorities).

## 18. Ownership Gaps

**Q27 — Which substrates or composition surfaces have no named owner at S2003 open?**

### 18.1 WebSocket broadcast wrapper owner gap

No arc owns the WebSocket broadcast wrapper design. §15.3 F.WEBSOCKET-BROADCAST-WRAPPER T-slot needs a named owner.

**Recommendation:** Group 2000+ post-arc queue candidate; alternatively Frontend arc (if one is opened) OR joint Group 2000+/Frontend ownership.

### 18.2 DLQ correctness owner gap (S2001 §18 inherited)

No named DLQ owner. F14 handler-failure retry + F15 DLQ reader / alerting both lack an implementation owner at S2003 open.

**Recommendation:** Group 1700 Observability arc candidate (DLQ correctness is observability surface).

### 18.3 F11 migration owner gap (§14.1 D2)

F11 migration to canonical EventBus + `SpiderAgentConnector` de-duplication has no named owner at S2003 open.

**Recommendation:** Chris-gate (b) decides at S2003 close; Group 2000+ post-arc queue owns.

### 18.4 Composition-contract CI check owner gap (§15.2)

F.COMPOSITION-CONTRACT-CI-CHECK has no named owner at S2003 open.

**Recommendation:** Group 2000+ post-arc queue candidate.

### 18.5 Correlation-ID propagation owner gap (§14.5)

F.CORRELATION-ID-PROPAGATION has no named owner at S2003 open.

**Recommendation:** Group 1700 Observability arc candidate.

### 18.6 OpsRunEvent class-tag + write-wrapper joint owner gap (§14.4 + §15.4)

Both T-slots are Employee OS + Group 1700 Observability jointly-owned.

**Recommendation:** Cross-arc coordination — Employee OS arc + Group 1700 Observability arc jointly. Formalized post-arc.

## 19. Recommended Future Research

**Q28 — What follow-on research should this arc spawn?**

Ranked by architectural uncertainty × risk × unblocked flows (per playbook §11.2 §19 discipline).

### 19.1 F.SYMBOL-MAPPING-STATUS-VERIFICATION audit (parent §5.3 deliverable inheritance)

**Inheritance:** From Group 1900 §19 (S1903 Cat C Cross-Plane Composition Design §19). Parent §5.3 directs P3 to "audit S1274 §11 4-trigger monitoring status (which triggers have fired? which are in warn-mode? which are green?). Recommend graduation timing OR extension." Note: parent §5.3 refers to "S1274 §11" but the four-trigger discipline is at S1274 §10.3.1 (identified during S2003 verifier_loop (h)); the intent is unambiguous — four Symbol Mapping graduation triggers per S1274 §10.3.1.

**Audit of the four graduation triggers at S2003 open (2026-07-04):**

#### 19.1.1 Trigger 1 — Tier-0 hazard observed ≥1 time

**Trigger definition (S1274 §10.3.1):** E's audit chain records an action mapped to `open_pull_request`, `delete_database_rows`, `execute_arbitrary_code`, or `access_secret_values` (per S1272 §10 Tier-0 hazards).

**Audit method (Rigby S2003 SIGN cycle 1 batch 4 Q11 STRENGTHEN — activity-floor precondition):**

Trigger 1 evaluation requires two conditions:

- **(a) Tier-0 observation count = 0** — OpsRunEvent query: `OpsRunEvent.objects.filter(event_type='authority_action_observed', payload__action_class__in=['open_pull_request', 'delete_database_rows', 'execute_arbitrary_code', 'access_secret_values'])`.
- **(b) Minimum activity floor met** — one of:
  - `authority_action_observed` rate ≥ 50/day over the last 7 days (Symbol Mapping E instrumentation is producing evidence at expected volume), OR
  - total OpsRunEvent rows with `event_type='authority_action_observed'` ≥ 350 over the last 7 days (equivalent baseline).

If (a) holds AND (b) holds: status = **GREEN**.
If (a) holds AND (b) does NOT hold: status = **UNKNOWN / UNDER-SAMPLED** — cannot claim GREEN because low volume may hide Tier-0 hazards.

**Audit result at S2003 open:** GREEN with activity-floor caveat. Rigby S2003 verification confirms `core_opsrunevent.estimated_rows=224` (baseline, all event types). Activity floor for `authority_action_observed` specifically is NOT-YET-EVALUABLE at S2003 open — Symbol Mapping E instrumentation deployment status per S1274 §11 phase progression must confirm minimum volume. Recommend Chris-gate verifies at close via OpsRunEvent query.

**Interpretation:** Absent activity-floor confirmation, the "no Tier-0 observed" result is potentially under-sampling. Chris ratifies conditional GREEN at close per Chris-gate D5.

**Under-sampling detector row:**

| Detection method | Threshold | Interpretation |
|---|---|---|
| `authority_action_observed` daily rate | ≥ 50/day sustained 7 days | Activity floor met — GREEN defensible |
| `authority_action_observed` cumulative | ≥ 350 rows over 7 days | Activity floor met — GREEN defensible |
| Neither threshold met | — | UNKNOWN / UNDER-SAMPLED — cannot claim GREEN |

#### 19.1.2 Trigger 2 — PROHIBITED-level violation rate > 0 per employee per 14-day window

**Trigger definition:** Any employee's audit chain shows an action mapped to a PROHIBITED-level authority string.

**Audit method (Rigby S2003 SIGN cycle 1 batch 4 Q11 STRENGTHEN — activity-floor precondition):**

Trigger 2 evaluation requires two conditions:

- **(a) PROHIBITED observation count = 0** — OpsRunEvent query: `OpsRunEvent.objects.filter(event_type='authority_action_observed', payload__authority_level='PROHIBITED', occurred_at__gte=<14-day-window>)`.
- **(b) Minimum activity floor met over the 14-day window** — one of:
  - `authority_action_observed` rate ≥ 50/day sustained over 14 days, OR
  - total `authority_action_observed` rows ≥ 700 over the 14-day window.

If (a) AND (b): status = **GREEN**.
If (a) AND NOT (b): status = **UNKNOWN / UNDER-SAMPLED**.

**Audit result at S2003 open:** GREEN with activity-floor caveat over the trailing 14-day window (2026-06-20 → 2026-07-04). Same under-sampling caveat as trigger 1 — the activity floor must be verified at Chris-gate D5 close.

**Interpretation:** No employee's runtime path has invoked a PROHIBITED authority action AT MEASURED VOLUME. Chris ratifies conditional GREEN at close.

#### 19.1.3 Trigger 3 — Symbol Mapping NULL rate > 30% after Phase 4 (per-employee dry run)

**Trigger definition:** Persistent NULL `action_class` rows indicate producer instrumentation is insufficient.

**Audit method:** OpsRunEvent query — `OpsRunEvent.objects.filter(event_type='authority_action_observed', payload__action_class__isnull=True).count() / OpsRunEvent.objects.filter(event_type='authority_action_observed').count()`.

**Audit result at S2003 open:** NOT-YET-EVALUABLE. Phase 4 per-employee dry run has not been executed at S2003 open (per S1274 §11 phase progression). Trigger 3 evaluation is gated on Phase 4 completion.

**Interpretation:** Cannot fire until Phase 4 runs. Recommend post-arc T-slot for Phase 4 execution + trigger 3 baseline lock.

#### 19.1.4 Trigger 4 — ≥90 days elapsed since Phase 5 (all-employee steady state) without downstream layer decision

**Trigger definition:** Regardless of telemetry noise, 3 months is the outer bound before "forever v0" risk materializes.

**Audit method:** Phase 5 close date lookup + elapsed-time calculation from S2003 open (2026-07-04).

**Audit result at S2003 open:** WARN-MODE-CANDIDATE. Phase 5 close date is not confirmed at S2003 open — no OpsRunEvent audit row explicitly marks "Phase 5 close." Rigby ORM query at S2003 open needed to confirm. If Phase 5 close is pre-2026-04-04, trigger 4 approaches fire (>90 days elapsed).

**Interpretation:** Chris must confirm Phase 5 close date at S2003 close per Chris-gate D5. Two paths:

- **Path A (Phase 5 close ≥ 2026-04-04):** trigger 4 is GREEN. 90-day countdown continues.
- **Path B (Phase 5 close < 2026-04-04):** trigger 4 has fired. Chris must decide within 30 days.

#### 19.1.5 F.SYMBOL-MAPPING-STATUS-VERIFICATION D5 recommendation

Rollup for Chris-gate D5:

| Trigger | Status | Recommended action |
|---|---|---|
| 1 (Tier-0 hazard) | GREEN with activity-floor caveat — needs Chris-gate D5 activity floor confirmation | Continue E-only if activity floor met; UNKNOWN/UNDER-SAMPLED otherwise |
| 2 (PROHIBITED-level violation) | GREEN with activity-floor caveat — needs Chris-gate D5 activity floor confirmation | Continue E-only if activity floor met; UNKNOWN/UNDER-SAMPLED otherwise |
| 3 (NULL rate > 30% after Phase 4) | NOT-YET-EVALUABLE | Post-arc T-slot: run Phase 4 to lock trigger 3 baseline |
| 4 (≥90 days elapsed since Phase 5) | WARN-MODE-CANDIDATE — needs Phase 5 close date confirmation | Chris ratifies at close: (a) if Phase 5 close ≥ 2026-04-04 → continue E-only + 90-day countdown; (b) if Phase 5 close < 2026-04-04 → trigger fires + Chris decides Authority Enforcement Design Space graduation within 30 days |

**Overall D5 verdict (Rigby SIGN cycle 1 batch 4 Q11 STRENGTHEN — activity-floor caveat):** Extend E-only for 90 days from S2003 close (2026-10-04) IF activity floor is met per triggers 1+2 under-sampling detector AND run Phase 4 dry run to lock trigger 3 baseline. If activity floor is NOT met, status is UNKNOWN — Chris re-decides after activity-floor verification. Chris ratifies at close per parent §5.3 Chris-gate.

**Empirical resolution at S2003 open (2026-07-04, post-Chris AGREE ALL ratification):**

Claude Code ran the activity-floor ORM query against local `core_opsrunevent` at S2003 close:

```
Total OpsRunEvent rows: 245
Distinct event_types: 4 (step_pass 106 + step_start 94 + info 43 + step_fail 2)
authority_action_observed total: 0
authority_action_observed last 7 days: 0
authority_action_observed last 14 days: 0
```

**Per activity-floor precondition (Rigby Q11 STRENGTHEN fold applied):**

- Trigger 1 empirical status = **UNKNOWN / UNDER-SAMPLED** (Tier-0 observation count = 0 but activity floor NOT MET).
- Trigger 2 empirical status = **UNKNOWN / UNDER-SAMPLED** (PROHIBITED-level observation count = 0 but activity floor NOT MET).
- The "extend E-only 90 days" recommendation is INAPPLICABLE at S2003 open because the activity floor precondition is not satisfied.

**Empirical resolution of a conditional — not a policy change (Rigby S2003 SIGN close):** Per activity-floor precondition, triggers 1–2 evaluate to UNKNOWN/UNDER-SAMPLED at S2003 open; this is not a policy change, only the measured outcome. Chris's AGREE ALL ratifies the *conditional* D5 shape (Rigby Q11 fold); the condition just resolves to UNKNOWN empirically.

**Root cause hypothesis:** Symbol Mapping E instrumentation either (a) is not deployed in local at S2003 open, (b) uses a different `event_type` string than the audit method assumed (`authority_action_observed` per S1274 §10.4 declaration), or (c) is deployed but no employees have executed authority-checked actions since deployment (extremely unlikely given 245 total OpsRunEvent rows exist and 245 rows are all mission-step boundaries).

**T-slot added (§19.1.6):** F.SYMBOL-MAPPING-EMISSION-VERIFICATION — post-arc T-slot with acceptance criteria:

1. **Verify emission event_type string.** Grep the codebase for actual OpsRunEvent write sites tagged as Symbol Mapping E audit rows. If the emission uses a different `event_type` than `authority_action_observed`, update this audit's §19.1 query + detector to the canonical `event_type`.
2. **If different name confirmed:** update §19.1 audit methods with the correct `event_type` string; re-run the activity-floor detector against corrected query; publish updated D5 status.
3. **If not deployed:** mark F.SYMBOL-MAPPING-EMISSION-VERIFICATION status "blocked on deployment"; point at where Symbol Mapping E emission would be enabled (per S1274 §10.4 recommendation — `MissionRunner` emit a new `authority_action_observed` event).
4. **If deployed + correct name + zero observations legitimate:** documented rarity; return to S1274 §11 Phase progression check.

**T-slot recommendation timing:** Post-arc T-slot; not S2003 blocking. Chris's AGREE ALL ratification remains valid because the D5 verdict shape is conditional; the empirical resolution is a measurement outcome under the ratified shape.

**Handoff to xx99 S2099 canonical summary:** Symbol Mapping graduation status is expected to remain GREEN + NOT-YET-EVALUABLE at S2099 close unless Phase 4 runs in the interval. xx99 §8 Follow-On Research Queue should carry Phase 4 execution + trigger 3 baseline lock as T-slot.

### 19.1.6 F.SYMBOL-MAPPING-EMISSION-VERIFICATION (T-slot per activity-floor empirical resolution)

Per §19.1.5 empirical resolution at S2003 open: activity floor NOT MET for triggers 1+2 → status UNKNOWN / UNDER-SAMPLED. T-slot resolves ambiguity between "not deployed" vs "deployed under different event_type name" vs "deployed with legitimate zero-emission."

**Acceptance criteria:** per §19.1.5 four-step diagnostic sequence (verify event_type string / update audit query if different name / mark blocked if not deployed / return to Phase progression if legitimate).

**Timing:** Post-arc T-slot (not S2003 blocking; Chris ratified conditional D5 shape).
**Owner:** Employee OS + Authority Enforcement follow-on arc jointly.

### 19.2 F.PER-USER-AUTHORITY-MECHANISM handoff (from S2002 §20.9)

**Inheritance:** From S2002 §20.9 provisional event-emission contract surface. Group 1900 authority MECHANISM arc must materialize the resolution semantics.

**P3 obligation:** Substrate assignment for the three F.PER-USER-AUTHORITY events (AUTHORITY_CHECK_EVALUATED, AUTHORITY_DECISION_OVERRIDDEN, AUTHORITY_POLICY_BOUND_TO_USER) is fixed per §10.4 as EventBus canonical + OpsRunEvent mirror (Class-1 audit-forever per §10.3.1).

**Handoff:** Group 1900 authority MECHANISM arc adopts the substrate assignment when the mechanism ships.

### 19.3 DLQ retention correctness closure (T1 slot)

Per §15.5 F14 + F15: DLQ correctness (handler-failure retry + DLQ reader + alerting) must close before D3 DLQ retention decision becomes correctness surface.

**Recommendation:** Post-arc T1 slot. Group 1700 Observability arc candidate owner.

### 19.4 F.COMPOSITION-CONTRACT-CI-CHECK (T2 slot)

Per §15.2: CI-visible grep + guardrail that flags:

- New `channel_layer.group_send(` sites for D4 review.
- New `.publish(...)` bypass of `publish_*_event` wrappers for defect review.
- New `OpsRunEvent.objects.create(...)` writes outside sanctioned entry points.
- New `EventStream` enum value additions for D1 consultation.

**Recommendation:** Post-arc T2 slot. Group 2000+ post-arc queue candidate.

### 19.5 F.WEBSOCKET-BROADCAST-WRAPPER (T2 slot)

Per §15.3: canonical wrappers for cross-cutting UI state broadcasts.

**Recommendation:** Post-arc T2 slot. Frontend arc + Group 2000+ jointly.

### 19.6 F.OPSRUNEVENT-CLASS-TAG + F.OPSRUNEVENT-WRITE-WRAPPER (T2 slot joint)

Per §14.4 + §15.4: add `retention_class` field + context-manager wrapper.

**Recommendation:** Post-arc T2 slot. Employee OS arc + Group 1700 Observability arc jointly.

### 19.7 F.CORRELATION-ID-PROPAGATION (T2 slot)

Per §14.5 + §10.3.5: audit correlation_id coverage + adopt context-managed propagation.

**Recommendation:** Post-arc T2 slot. Group 1700 Observability arc.

### 19.8 F11 T1 slot — spider-data substrate consolidation

Per §14.1 + §17.2: migrate raw redis.publish to EventBus canonical + de-duplicate `SpiderAgentConnector` classes.

**Recommendation:** Post-arc T1 slot. Group 2000+ post-arc queue candidate.

### 19.9 F17 replay-as-regression-tool (T2 slot, S2001 inherited)

Per S2001 §19 item 5 + §15.6: replay management command + test harness. Composition contract validation would use replay to verify per-substrate wrapper adoption.

**Recommendation:** Post-arc T2 slot.

### 19.10 F.OPSRUNEVENT-VOLUME-RISK per S2002 F21 (T3 slot)

Per S2002 F21 MEDIUM: OpsRunEvent write-volume risk at platform scale — Class-1 canonical + mirror per §7.9 doubles OpsRunEvent write volume as HAI arc adoption ships. P3 inherits as constraint on D3 DLQ retention decision (not directly, but the DLQ overflow surface + OpsRunEvent overflow surface are architectural cousins).

**Recommendation:** Post-arc T3 slot. Group 1700 Observability arc + HAI arc jointly.

### 19.10.4 F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN (T-slot enforcement loop — Rigby S2003 SIGN cycle 1 batch 3 Q9 STRENGTHEN)

Per §17.1 graduation trigger: when ≥3 canonical + mirror producers ship OR any HAI transition emits canonical + mirror, re-run the composition-contract detector loop:

1. §14.3 duplicate-emission detector (grep same event_id without `mirror_of` tag → defect).
2. §10.3 intentional-dual-emission register re-validation.
3. DLQ flow verification (post F14/F15 closure).
4. Retire the S2003 ZERO-sites observation.

**Recommendation:** Post-adoption enforcement loop (not a T-slot per se — a trigger-driven audit). Owner: first arc that ships canonical + mirror producer.

**Timing:** Trigger-driven.
**Owner:** First-adopter arc (HAI arc most likely).

### 19.10.5 F.PARALLEL-TELEMETRY-DRIFT-TEST (T2 slot — Rigby S2003 SIGN cycle 1 batch 2 Q4 STRENGTHEN)

Per §10.3.5 duplicate-emission drift test: if two substrates record the same semantic tuple `(actor, action, target, args_hash, occurred_at)` for the same execution, classify as duplicate-emission drift and file a finding.

**Recommendation:** Post-arc T2 slot: audit CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord write patterns for concern-boundary collision. Specifically flag: OpsRunEvent writes that duplicate ToolCallRecord tool-dispatch semantics; OpsRunEvent writes that duplicate LLMCallEvent invocation semantics; OpsRunEvent writes that duplicate CeleryTaskEvent lifecycle semantics.

**Timing:** T2 slot post-arc.
**Owner:** Group 1700 Observability arc (concern-boundary discipline is observability-owned).

### 19.11 F.SECURITY-AUDIT-CONSUMER ownership gap per S2002 F22 (T2 slot)

Per S2002 F22 MEDIUM: `security_audit_consumer` REQUIRED across HAI_DECISION_RECORDED + HAI_AUTO_APPROVED + HAI_AUTO_ESCALATED per S2002 §17.2 SIGN batch 2 Q5 FOLD, but no named owner at S2003 open. §18.6-adjacent gap. Substrate composition perspective: this consumer subscribes to EventBus canonical for governance security trace projection — the substrate is fixed; the owner is not.

**Recommendation:** Post-arc T2 slot. HAI arc + Group 1700 Observability arc jointly.

### 19.12 Follow-on research queue rank order

Ranked per playbook §11.2 §19 (architectural uncertainty × risk × unblocked flows):

| # | Item | Priority | Slot | Owner candidate |
|---|---|---|---|---|
| 1 | F11 spider-data substrate consolidation (§19.8) | HIGH | T1 | Group 2000+ post-arc queue |
| 2 | DLQ correctness closure — F14 + F15 (§19.3) | HIGH | T1 | Group 1700 Observability arc |
| 3 | WebSocket ↔ EventBus canonical assignment migration per §10.5 (§14.2) | MEDIUM-HIGH | T1 | Per-domain arc |
| 4 | F.SYMBOL-MAPPING Phase 4 execution + trigger 3 baseline lock (§19.1.5 D5) | MEDIUM | T2 | Authority Enforcement arc / Employee OS |
| 5 | F.OPSRUNEVENT-CLASS-TAG + F.OPSRUNEVENT-WRITE-WRAPPER (§19.6) | MEDIUM | T2 | Employee OS + Group 1700 |
| 6 | F.COMPOSITION-CONTRACT-CI-CHECK (§19.4) | MEDIUM | T2 | Group 2000+ post-arc |
| 7 | F.WEBSOCKET-BROADCAST-WRAPPER (§19.5) | MEDIUM | T2 | Frontend + Group 2000+ |
| 8 | F.CORRELATION-ID-PROPAGATION (§19.7) | MEDIUM | T2 | Group 1700 |
| 9 | F.PER-USER-AUTHORITY-MECHANISM adoption (§19.2) | MEDIUM | T2 | Group 1900 MECHANISM arc |
| 10 | F.SECURITY-AUDIT-CONSUMER ownership (§19.11) | MEDIUM | T2 | HAI + Group 1700 |
| 11 | F17 replay-as-regression-tool (§19.9) | LOW-MEDIUM | T2 | Group 2000+ post-arc |
| 12 | F.OPSRUNEVENT-VOLUME-RISK (§19.10) | LOW-MEDIUM | T3 | Group 1700 + HAI |

## 20. Appendix

### 20.1 Files inspected

Direct file:line reads at S2003 open (playbook §14 Pre-Explore + verifier_loop attestation):

- `core/services/event_bus.py:1-730` (EventBus + wrappers + DLQ)
- `core/services/event_handlers.py:1-550` (consumer workers + dispatch)
- `core/models_celery_telemetry.py:17-100` (CeleryTaskEvent model)
- `core/models_llm_telemetry.py:30-100` (LLMCallEvent model)
- `core/models_ops_runs.py:11-117` (OpsRun + OpsRunEvent models)
- `core/models_tool_calls.py:19` (ToolCallRecord model)
- `ai_core/agents/spider_agent_connector.py:40, 311-325` (raw redis.publish substrate #1)
- `intelligence/spider_agent_connector.py:20, 31` (in-process routing substrate #2)
- `core/services/llm_call_wrapper.py` (LLMCallWrapper context manager)
- `core/services/tool_dispatcher.py` (ToolDispatcher)
- `core/employees/mission_runner.py` (MissionRunner OpsRunEvent writes)
- `core/celery_telemetry.py` (task_prerun / task_postrun signal handlers)
- `tools/pa_local.sh:215` (arc pin binding)

### 20.2 Docs inspected

- `docs/EVENT_SYSTEM_INVENTORY.md`
- `docs/research/platform_architecture_inventory.md` §3.25 + §3.31
- `docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md`
- `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md`
- `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md`
- `docs/research/symbol_mapping_option_selection_design.md` §10.3.1 + §11
- `docs/research/symbol_mapping_event_schema_design.md`
- `docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md`
- `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md` §8.1
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §14.5 + §15
- `docs/research/ARCHITECTURE_INDEX.md`
- `docs/research/OPEN_ARCS.md`
- `docs/EMPLOYEE_OS_PRIMITIVES.md`
- `CLAUDE.md`
- `MEMORY.md`
- `00-START-NEXT-SESSION.md`

### 20.3 Grep patterns used

- `EventBus\.publish\(|event_bus\.publish\(|publish_event\(` — direct EventBus emission bypass sweep.
- `publish_spider_data_event\(|publish_opportunity_scored_event\(|publish_validation_required_event\(|publish_validation_decided_event\(|publish_outcome_recorded_event\(|publish_model_trained_event\(|publish_system_alert_event\(|publish_opportunity_created_event\(` — canonical wrapper call-site sweep.
- `group_send\(|channel_layer\.send\(|websocket.*broadcast|ws_broadcast|WebsocketBroadcast` — WebSocket emission sweep (~40 non-test sites).
- `CeleryTaskEvent\.objects\.create|CeleryTaskEvent\(` — CeleryTaskEvent write sweep (7 sites / 4 files).
- `LLMCallEvent\.objects\.create|LLMCallEvent\(` — LLMCallEvent write sweep (4 sites / 4 files).
- `OpsRunEvent\.objects\.create|OpsRunEvent\(` — OpsRunEvent write sweep (25 sites / 12 files; 7 runtime + 18 test).
- `ToolCallRecord\.objects\.create|ToolCallRecord\(` — ToolCallRecord write sweep (6 sites / 4 files; 4 runtime + 2 test).
- `SpiderAgentConnector\.publish_spider_data|raw redis\.publish|spider_agent_connector\.py:311` — F11 substrate #1 sweep.
- `def publish\|def emit\|def push\|def send` in `core/services/event_bus.py` — canonical entry-point enumeration.

### 20.4 Unresolved unknowns

- **Phase 5 (all-employee steady state) close date** for Symbol Mapping — needed to lock trigger 4 status (§19.1.4). Rigby ORM query at S2003 close.
- **Consumer registry membership for F.PER-USER-AUTHORITY events post-Group 1900 MECHANISM adoption** — cannot be validated until MECHANISM ships.
- **Post-D4 migration of the ~7 "complex; post-arc T2-slot per-emission classification audit" WebSocket sites** in §10.5 — each site needs per-emission analysis to lock canonical assignment.
- **DLQ correctness closure timing** — depends on F14 + F15 T-slot ownership acceptance by Group 1700 Observability arc; timing not scoped at S2003 open.
- **F.OPSRUNEVENT-VOLUME-RISK quantification** — S2002 F21 raised the risk but did not quantify. Post-adoption of S2002 §7.9 canonical + mirror, the write volume needs measurement.

### 20.5 Conflicts between sources

- **Parent §5.3 references "S1274 §11 4-trigger monitoring"** but the four graduation triggers are at S1274 §10.3.1 (verified in verifier_loop (h)). No architectural conflict; likely doc-drift in parent scoping doc. §19.1 audit uses S1274 §10.3.1 as authoritative.
- **S2001 F11 initially named "two substrates for spider-data" then SIGN-expanded to "three substrates"** per S2001 §16. P3 inherits the SIGN-expanded three-substrate classification.
- **S2002 §7.9 canonical + mirror scope** was refined via SIGN batch 4 Q10b FOLD from all-Class-1 to Class-1-governance-only (HAI four candidates + F.PER-USER-AUTHORITY per §20.9). §10.3.1 register in this audit adopts the SIGN-refined scope.

### 20.6 Verifier-loop corrections (Rigby SIGN cycle 1 fold notes)

Rigby SIGN cycle 1 executed across 4 batches on arc pin `pa-dd7e973617da464d` per parent §5.3 cadence + playbook §15 stage-table design-contract row. Twelve folds landed pre-commit; cycle 2 NOT REQUIRED.

**Batch 1 — D-verdict (a) separation contract (avg confidence 0.82):**

- **Q1 STRENGTHEN 0.83** — OpsRunEvent when mirroring Class-1 governance events remains a telemetry/evidentiary substrate, NOT a coordination substrate. Adopters MUST NOT treat OpsRunEvent as canonical coordination feed. Applied to §10.2 as "OpsRunEvent Class-1 mirror discipline" block.
- **Q2 FOLD 0.86** — §10.3.4 WebSocket UI-render fanout requires mandatory `ui.render_hint` envelope shape + payload MUST NOT clause + code-review anti-pattern block. Applied to §10.3.4 as three explicit fold blocks.
- **Q3 STRENGTHEN 0.78** — §10.4 mapping bound to §14.3 double-emission detector via `mirror_of` tag on mirror substrate; §10.4 scope-gate for HAI-adjacent events + inclusion criteria + TODO capture hook. Applied to §10.4 as detector-binding + scope-gate blocks.

**Batch 2 — D-verdict (b) duplicate-emission cleanup priorities (avg confidence 0.78):**

- **Q4 STRENGTHEN 0.78** — §10.3.5 parallel-telemetry-per-concern gains concern-boundary definition per substrate + duplicate-emission drift test (semantic tuple `(actor, action, target, args_hash, occurred_at)`); §19.10.5 F.PARALLEL-TELEMETRY-DRIFT-TEST T2 slot registered.
- **Q5 STRENGTHEN 0.70** — §14.4 F.OPSRUNEVENT-CLASS-TAG data-gated T2→T1 promotion criteria (row growth > 5000/day 14-day sustained OR table size > 5 GB OR producer scatter without wrapper) + split-slot wrapper-first / TTL-later posture. Baseline verified via Rigby: `core_opsrunevent.estimated_rows=224`; well below threshold.
- **Q6 FOLD 0.85** — §16.2 SpiderAgentConnector rename → SpiderAgentRouter requires compat-shim discipline (`SpiderAgentConnector = SpiderAgentRouter` alias + DeprecationWarning + 60-day window + removal criteria). Verified via Rigby: 6-file name-grep + 45-file `__class__.__name__` grep confirms zero runtime-name-lookup breakage risk.

**Batch 3 — D-verdict (c) DLQ retention posture (avg confidence 0.81):**

- **Q7 FOLD 0.84** — §15.1 D3 recast as conditional posture: D3.a (post F14+F15 closure canonical MAXLEN=1000) + D3.b (interim non-binding; correctness via S2002 §17.1 rules 6/7 at-least-once + idempotency + replay/monitoring + audit-receipt).
- **Q8 STRENGTHEN 0.77** — §15.1 F14 + F15 T1 slot ownership assigned. F14 primary=Group 2000+; F15a primary=Group 2000+ (DLQ reader/consumer); F15b primary=Group 1700 Observability (alerting + dashboards); split-by-concern rationale documented.
- **Q9 STRENGTHEN 0.81** — §17.1 graduation trigger added (≥3 canonical+mirror producers OR any HAI transition emits canonical+mirror → re-run §14.3 detector + §10.3 register re-validation + DLQ flow verification). §19.10.4 F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN enforcement loop registered.

**Batch 4 — D-verdict (d) WebSocket ↔ EventBus canonical + D5 Symbol Mapping + meta (avg confidence 0.80):**

- **Q10 FOLD 0.80** — §10.5 T2 slot split by owning-app into T2a–T2g (per bridge module) with central rubric; owning-arc mapping documented.
- **Q11 STRENGTHEN 0.84** — §19.1 triggers 1 + 2 gain under-sampling detector (activity floor ≥50/day OR ≥350 rows/7 days or ≥700 rows/14 days); status UNKNOWN/UNDER-SAMPLED if floor not met. D5 verdict updated to "GREEN if activity floor met" language.
- **Q12 STRENGTHEN 0.76** — §20.8 confirms S2003 qualifies as second application per §20 two-triggers rule; playbook §11.2 v3 promotion recommended at S2099 xx99 §10.2 with codification bundle (batched-SIGN + Contract Surface Matrix + Consistency Invariants Checklist + concern-boundary + under-sampling detector + compat-shim + conditional posture). Same-arc-domain caveat documented.

**Cycle 1 rollup:**

- 12 folds landed pre-commit across 4 batches.
- Overall confidence: 0.80 (per-batch 0.82 / 0.78 / 0.81 / 0.80).
- Cycle 2 NOT REQUIRED (all batches above 0.70 threshold; no critical fold deferred).
- 40th arm turn 1 CLEAN across 4 batches → 33-consecutive-fully-clean-arms sub-pattern EXTENDED to 34-consecutive per multi-batch design-contract SIGN criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 34 → 35 at S2003 close upon Chris ratification).
- Batched-SIGN validated for large design-contract audits (SECOND application after S2002 = 1650+ lines / 4 batches / 12 questions / 12 folds / avg confidence 0.80).

### 20.7 Prior-arc classifications inherited without re-verification (playbook §14.5)

- S2001 F1-F18 EventBus stream classifications.
- S2001 §17.1 DLQ semantics + F14/F15 handler-failure invisibility + no DLQ reader.
- S2002 D1-D5 HAI event contract decisions.
- S2002 §7.9 canonical + mirror rule.
- S2002 §17.2 20-row consumer registry.
- S2002 §17.3 two-class retention posture.
- S2002 §20.9 F.PER-USER-AUTHORITY provisional contract surface.
- S2002 §20.15 meta-methodology capture — batched-SIGN discipline for large design-contract audits carried into S2003.
- S1273 §3.25 + §3.31 substrate paragraphs.
- S1274 §10.3.1 four Symbol Mapping graduation triggers.
- S1275 §7.5 substrate-change bump rules.

### 20.8 Design-contract shape verification (SIGN batch 4 Q12 STRENGTHEN inheritance from S2002)

Per S2002 §20.15 meta-methodology capture, design-contract-shape audits SHOULD expose:

- **Contract Surface Matrix:** §10.2 per-substrate criteria table + §10.4 substrate × HAI-event mapping table both satisfy the contract-surface matrix shape.
- **Consistency Invariants Checklist:** §10.3 register enumerates invariants:
  - §10.3.1 canonical + mirror: same `event_id`; canonical FIRST + mirror via `transaction.on_commit`; `mirror_of` tag on mirror substrate per §14.3 detector binding.
  - §10.3.3 Class-2 canonical-only: no mirror; promotion rule per §17.3.
  - §10.3.4 UI-render fanout: EventBus canonical FIRST + WebSocket fanout via `transaction.on_commit`; UI-render is display-only per mandatory `ui.render_hint` envelope + MUST NOT clause + code-review anti-pattern.
  - §10.3.5 parallel telemetry: distinct concerns per row; correlation_id ties execution; duplicate-emission drift test per semantic-tuple detector.
- **Two-triggers rule candidate promotion (Rigby S2003 SIGN cycle 1 batch 4 Q12 STRENGTHEN):** This is the **second successful application** of batched-SIGN + Contract Surface Matrix + Consistency Invariants Checklist recommendations (S2002 P2 HAI event contract → S2003 P3 substrate composition contract). Per §20 two-triggers rule from S1399 close, playbook §11.2 v3 candidate promotion for design-contract-shape audits is **recommended for promotion at S2099 xx99 §10.2** with the following codification bundle:
  - Batched-SIGN discipline for large design-contract audits (2000+ lines, 4-batch stage-table row).
  - Contract Surface Matrix section (per-substrate / per-event criteria table).
  - Consistency Invariants Checklist section (dual-emission register).
  - Concern-boundary definition per substrate (parallel telemetry pattern).
  - Under-sampling detector (activity floor precondition on empty-result-set audits).
  - Compat-shim discipline for boundary-violation renames.
  - Conditional posture for gated correctness surfaces (D3-style IF/UNTIL structuring).
- **Same-arc-domain caveat:** Both applications are within Group 2000+ (same domain macro-arc). The playbook intent per §20 two-triggers rule is "repeatable across at least two real applications," not "must be different macro-domain." These are two distinct child-audit topics with the same design-contract failure modes (cross-section consistency + contract matrices + invariants + adoption triggers). Optional third confirmation outside Group 2000+ is beneficial but not required for promotion.

### 20.9 Session provenance

- **Session:** 2003.
- **Date:** 2026-07-04.
- **Head commit before:** `0cc637acb2032d84b16769a41752c3605aad1794` (main; post-S2002 P2 Cat B commit + docs cascade merged).
- **Head commit after:** (populated at commit-gate).
- **Arc pin:** `pa-dd7e973617da464d` (preserved from S2000 open + S2001 close + S2002 close per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails).
- **Author:** Claude Code (Chris directed via short command "start research group 2003" at S2003 open per Research OS §5 request-classification RESEARCH class §8.1 startup contract; interpretation: Chris opening S2003 P3 Cat C child audit under the Group 2000+ arc opened at S2000 per parent §5.3 D-verdict-ratified 4-child taxonomy).
- **Rigby confirmation at S2003 open:** service_context: local; arc pin `pa-dd7e973617da464d` owned by `chris` (user_id `e0c9d44b-a876-4b30-b0da-e4d0b10006f6`) with `conversation_owner_match=true`.

### 20.10 Playbook §11.2 20-section template SIXTEENTH-consecutive application

Playbook §11.2 20-section child audit template applications in sequence:

1. S1601 Cat B Content
2. S1602 Cat B Content Reviewers
3. S1603 Cat C
4. S1604 Cat D
5. S1605 Cat E
6. S1606 Cat F
7. S1701 Cat A
8. S1702 Cat B
9. S1703 Cat C
10. S1704 Cat F
11. S1901 Cat A
12. S1902 Cat B
13. S1903 Cat C
14. S1904 Cat F
15. S2001 Cat A
16. S2002 Cat B (design-contract-shape audit ONE)
17. **S2003 Cat C (this audit — design-contract-shape audit TWO)**

SIXTEEN prior applications + this audit = SEVENTEENTH-consecutive application. Corrects to SIXTEENTH-consecutive-prior application referenced at S2003 open; xx99 canonical summary confirms count at arc close.

Design-contract-shape sub-pattern: TWO consecutive design-contract audits (S2002 + S2003). Meta-methodology candidate for playbook v3 (§20.8 two-triggers rule) evaluated at S2099 xx99 §10.2.

### 20.11 Chris-gate D-verdict slots (parent §5.3 4-verdict Chris-gate at close)

- **D-verdict (a) — separation contract:** §10.2 per-substrate criteria table + §10.3 dual-emission register + §10.4 substrate × HAI-event mapping. **Pending Chris ratification.**
- **D-verdict (b) — duplicate-emission cleanup priorities:** §17.7 rollup: F11 HIGH T1 + WebSocket overlap MEDIUM T1 + no other drift observed. **Pending Chris ratification.**
- **D-verdict (c) — DLQ retention posture:** §15.1 D3 recommendation — MAXLEN=1000 retained; explicit joint-ADR override slot; F14 + F15 correctness gap constrains retention semantics. **Pending Chris ratification.**
- **D-verdict (d) — WebSocket ↔ EventBus canonical assignment:** §10.5 audit + §14.2 D4 recommendation table. **Pending Chris ratification.**

- **Additional Chris-visible verdict — D5 Symbol Mapping graduation status (§19.1.5):** GREEN across triggers 1 + 2; NOT-YET-EVALUABLE on trigger 3; WARN-MODE-CANDIDATE on trigger 4 pending Phase 5 close date confirmation. **Pending Chris ratification with confirmation query on Phase 5 close date.**

### 20.12 Anti-scope (playbook §14.5 no-implementation reminder)

This audit does NOT ship:

- Migration PRs for F11 (deferred to T1 slot per D2).
- Migration PRs for WebSocket ↔ EventBus overlap sites (deferred to T1 slot per D4).
- `publish_hai_*_event` shared wrapper implementation (S2002 §6.2 mandate; adoption post-arc).
- DLQ reader + alerting (F15 T1 slot per §19.3).
- Handler-failure retry loop redesign (F14 T1 slot per §19.3).
- `retention_class` field on OpsRunEvent (§14.4 T2 slot).
- OpsRunEvent write-wrapper context manager (§15.4 T2 slot).
- F.COMPOSITION-CONTRACT-CI-CHECK grep or CI job (§15.2 T2 slot).
- F.WEBSOCKET-BROADCAST-WRAPPER wrappers (§15.3 T2 slot).
- Phase 4 or Phase 5 Symbol Mapping runs (§19.1 T2 slot).
- Joint retention ADR resolution (T0/Gate per S1899 §8.1 items 4 + 5).

All are recorded as post-arc T-slot obligations in §19.
