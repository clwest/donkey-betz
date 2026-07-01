---
title: "Employee OS Collaboration Patterns — Platform-Wide Audit (research only)"
status: draft
session: 1268
date: 2026-06-30
mission_type: architectural_discovery
authority: |
  Evidence-only audit. No runtime changes. No PRs. No migrations.
  No commits. No implementation. The two prior research docs
  (substrate audit + protocol sketch) covered "how do *employees*
  communicate." This doc covers the broader question: "how do
  autonomous components *already* collaborate across the platform?"
  before any design proposal touches inter-employee delegation.
companion_docs:
  - docs/research/employee_os_communication_substrate_audit.md
  - docs/research/employee_os_communication_protocol_sketch.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
verifier_loop: |
  Five parallel Explore sub-agents produced evidence reports
  (advisor/boardroom, scheduling/orchestration, spider/proactive/
  signal autonomy, decision routing + HAI lifecycle + Initiative
  pipeline, collaboration-specific failure history). All
  load-bearing class locations spot-verified by Claude via direct
  Grep before this doc was written. Independent review by Rigby
  complete (S1268 PA conversation pa-01e90a1d36f54880):
  **SIGN-with-edits**. One substantive correction
  (MissionRunner verdict_issued event is conditional on
  `auto_emit_verdict=True`, not guaranteed —
  `mission_runner.py:1127-1145`, S1267 protocol invariant
  change). Architectural-blind-spot note added on canonical
  idempotency key across the two durable orchestration paths.
  SIGN-clean on findings F2/F3/F4, §11 recommendation, EventBus
  drift catch, reuse classifications, anti-duplication
  conclusion, Q7 canonical foundation. Edits folded into §1
  item 6, §2 row 19, §6 row, §7 row 29, §10 Q12, Appendix A.
owner: claude (synthesis) + rigby (independent SIGN review, S1268)
---

# Employee OS Collaboration Patterns — Platform-Wide Audit

> **Why this doc exists.** The substrate audit (S1268 P0 #1)
> inventoried the *messaging* primitives between AI employees. The
> protocol sketch (S1268 P0 #2) scoped a single first inter-employee
> notice path. This third doc takes a step back: **before** any
> Employee-to-Employee delegation gets designed, what existing
> collaboration mechanisms across the platform could it inherit
> rather than rebuild? Inventory first. Decide later.
>
> **What this doc is not.** A design. A decision. A recommendation
> to build. The reuse classifications are first-pass research
> proposals; final calls happen in their own review cycle with
> Rigby + Chris.

---

## 1. Executive Summary

The Donkey Betz platform has **eleven distinct collaboration
substrates already in production**:

1. **AgentRouter** sync/async agent-to-agent dispatch
   (`core/agent_router.py:836-945`).
2. **BaseAgent.delegate_to_agent()** recursive delegation, depth-3
   cap (`core/agents/base_agent.py:890-950`).
3. **ConversationOrchestrator** multi-agent debate with turn-flow
   contracts and DecisionSummary artifacts
   (`core/conversation_orchestrator.py:270+`).
4. **WorkflowOrchestrationAgent** ThreadPoolExecutor fan-out
   (`core/agents/workflow_orchestration_agent.py:47,302`).
5. **Celery `chain` + `group`** durable task fan-out/fan-in
   (`ai_core/agents/hybrid_executor.py:244,351`).
6. **MissionRunner + OpsRun + OpsRunEvent** mission-level
   orchestration with idempotency, dedupe, verdict *or
   status-only completion*, and escalation
   (`core/employees/mission_runner.py:1-1758`). **S1267 added
   `auto_emit_verdict=False` opt-out** — when set, runner flips
   `OpsRun.status` + `finished_at` but **skips** the
   `verdict_issued` OpsRunEvent + `emit_mission_verdict()` call
   (`mission_runner.py:1127-1145`). Bug Triage Specialist
   exercises this path; verdict is later written via PA tool.
7. **AgentFollowupSubscription + signal handler** durable wakeup
   from agent terminal → conversation banner
   (`core/models_unified_system.py:1017-1116`).
8. **EventBus (Redis Streams)** **8 named streams** + DLQ with
   consumer groups (`core/services/event_bus.py:21-728`).
9. **HumanAttentionLifecycleService** auto-expire / auto-dismiss
   / auto-escalate / auto-approve
   (`core/services/human_attention_lifecycle.py:36-728`).
10. **OrchestrationApprovalGate** bridge from orchestration to HAI
    to human decision (`core/models_orchestration.py:397-535`).
11. **Initiative 5-stage pipeline** durable state machine with
    founder-intent + semantic-drift gates
    (`core/models_document_registry.py:37-715`).

Plus **non-LLM-callable adjacencies** that influence collaboration:

- **AdvisorContextBuilder** — synchronous one-way context injection
  into agent prompts (`core/services/advisor_context_builder.py:23-150+`).
  Advisors are **prompt-context only**, NOT first-class agents.
- **BoardroomMLService** — ML decision-prediction layer on top of
  HAI (`core/services/boardroom_ml_service.py:31-146`). "Boardroom"
  is human approval + ML forecast, **not** multi-agent debate.
- **BodyCoordinator** — autonomic-reflex layer with 9 body systems
  + 28 event handlers (`core/services/body_coordinator.py:110-300+`).
  Health monitoring, not collaboration per se, but emits events
  that trigger remediation.

### Major Findings

**Finding F1 — The infrastructure is already there.** Every
collaboration capability Employee OS could need has a
production-evidenced precedent. Reuse beats invention.

**Finding F2 — The biggest surprise: there are TWO orthogonal
durable-orchestration paths.** Celery `chain` is one
(`hybrid_executor.py`); MissionRunner step-loop is the other
(`mission_runner.py`). They do not compose today. Employee OS uses
the second; the first is dormant outside of agent dispatch.

**Finding F3 — Advisors and Boardroom are not what their names
suggest.** Advisors are a **context-injection** primitive, not
callable collaborators. Boardroom is a **human-approval ML
layer**, not a debate engine. Both are misleadingly named for
anyone expecting "AI consultants Rigby can call."

**Finding F4 — There is no in-platform A→A reply contract.**
Across all 11 substrates, the only round-trip pattern is
human-in-the-loop (HAI decision → `HumanFeedbackRecord` → ML
learning). Employee-to-employee delegation with a reply lane has
no precedent today.

**Finding F5 — Eight failure classes are platform-wide
collaboration risks** with active production guards. The 15
incidents inventoried in §7 below each have a documented
mitigation; the four with HIGH cross-employee relevance are the
receipt-chain gap (closed S1262), the heartbeat write-stomp
(closed S1084 PR #1892), the zombie-thread per-chunk timeout
loophole (closed S1221 PRs #2519/#2520), and the macOS mutex
deadlock cascade (closed S1083-1084, 11 PRs).

**Finding F6 — Documentation drift between
`EMPLOYEE_OS_PRIMITIVES.md` and the substrate audit on EventBus
stream count (6 in audit, 8 in runtime).** Flagged in §12 for
cleanup.

### Overall Recommendation

For S1268's collaboration-architecture research arc, the
recommended next mission is **not** "design inter-employee
delegation." It is **"audit governance + authority evolution"** —
specifically, how `JobContract.authority` would shift from
S1264 warn-mode to enforcement, and what trust-propagation
primitives would need to exist to make that shift safe. See §11
for the full case.

---

## 2. Collaboration Primitive Inventory

The inventory below is comprehensive across the platform. Every
row has a file:line cite. Reuse classifications follow §8.

| # | Primitive | Purpose | Used by | Evidence | Reuse class | Notes |
|---|---|---|---|---|---|---|
| 1 | `AGENT_MAP` | Name → BaseAgent class routing | AgentRouter | `core/agent_router.py` declaration near line 320 | **SAFE** | 83 agents (74 enabled, 8 rerouted, 1 blocked) per inventory |
| 2 | `AgentRouter.route()` (sync) | Agent dispatch entrypoint | All sync agent calls | `core/agent_router.py:836-945` | **SAFE** | Creates AgentExecution; auto-resolves parent/root lineage |
| 3 | `execute_agent()` (Celery) | Async agent dispatch wrapper | All async agent calls | `core/tasks_agents.py:494-780` | **SAFE** | Re-uses AgentRouter.route w/ existing_execution_record |
| 4 | `AgentExecution` (with trace_id, parent_execution_id, root_execution_id) | Per-execution audit row + lineage | All routed agents | `core/models_unified_system.py:875-980` | **SAFE** | Session 1098 PR #4 added lineage; cancel propagation walks root chain |
| 5 | `BaseAgent.delegate_to_agent()` | Agent → Agent sub-call | Multi-agent orchestrators | `core/agents/base_agent.py:890-950` | **WRAPPER** | `max_depth=3` cap (line 905); same-agent (A→A) not explicitly checked |
| 6 | Heartbeat daemon (30s tick) | Liveness signal for watchdog | All routed agents | `core/agent_router.py:2945-2980` | **SAFE** | Cleanup beat marks no-heartbeat-60min as failed |
| 7 | `ToolCallRecord` | Per-tool-call audit row | All PA tool dispatches + agent tool calls | `core/models_tool_calls.py:19-150` | **SAFE** | trace_id + agent_name + result_hash; S1115 added write-on-all-return-paths |
| 8 | `LLMCallEvent` | Per-LLM-call audit row | All LLM calls | `core/models_llm_telemetry.py:30-100` | **SAFE** | execution_id FK + metadata.ops_run_id; cancellation observability |
| 9 | `CeleryTaskEvent` | Per-task lifecycle telemetry | All Celery tasks | `core/models_celery_telemetry.py:30-100` | **SAFE** | agent_name dimension (S1169); 30d retention |
| 10 | `ConversationOrchestrator` (multi-agent debate) | Turn-flow-bound agent debate; produces DecisionSummary | Content deliberation; analyst-style multi-agent calls | `core/conversation_orchestrator.py:270` | **DO NOT REUSE** for E→E | Built for in-conversation deliberation; wrong shape for inter-employee delegation |
| 11 | `TURN_FLOWS` (analytical / creative / debate / planning / critique / general) | Pre-defined turn sequences | ConversationOrchestrator | `core/conversation_orchestrator.py:60-107` | **DO NOT REUSE** for E→E | Same reason as #10 |
| 12 | `DecisionEnforcerAgent` | "Prefrontal cortex" — prevents "further analysis" loops | ConversationOrchestrator | `core/conversation_orchestrator.py:1556-1562` | **WRAPPER** | Useful pattern; not directly callable from E→E |
| 13 | `WorkflowOrchestrationAgent` | Multi-step workflow agent | Morning Brief, content workflows | `core/agents/workflow_orchestration_agent.py:47,302` | **WRAPPER** | Returns `result['steps']` not `step_results` (S1234 PR #2609 footgun); ThreadPoolExecutor fan-out; iteration cap reduced 5→3 (Session 1069) |
| 14 | `MeetingCoordinatorAgent.SUB_AGENT_TIMEOUT=180` + ThreadPoolExecutor | Parallel sub-agent dispatch w/ per-agent timeout | Executive meetings, multi-perspective synthesis | `core/agents/executive/meeting_coordinator_agent.py:30,35-39` | **SAFE** | Direct precedent for "Employee A spawns N sub-tasks in parallel" |
| 15 | `celery.chain` | Sequential durable task chain | `HybridAgentExecutor` | `ai_core/agents/hybrid_executor.py:244,260` | **SAFE** | Output of step N → input of step N+1; survives worker restart |
| 16 | `celery.group` | Parallel durable task group | `HybridAgentExecutor` | `ai_core/agents/hybrid_executor.py:351,355` | **SAFE** | Fan-out + collect via `result.get()`; survives worker restart |
| 17 | `celery.chord` | Group + callback | (none active in production) | grep returned no active sites | **UNKNOWN** | Pattern exists in Celery but no production callers found |
| 18 | `AIEmployee` + `JobContract` (frozen dataclasses) | Identity + policy registry | Employee OS | `core/employees/jobs.py:74-162,1327-1347` | **SAFE** | 4 employees registered; no DB row per employee |
| 19 | `MissionRunner` + lifecycle | Mission-scoped orchestrator: preflight → steps → postflight → (verdict OR status-only completion) → escalation | Employee OS | `core/employees/mission_runner.py:1-1758` | **SAFE** | Daily idempotency; 24h dedupe window. **S1267 `auto_emit_verdict=False` opt-out path** (line 1127-1145): flips `OpsRun.status` + `finished_at` but skips `verdict_issued` OpsRunEvent + `emit_mission_verdict()`. Bug Triage v0 exercises this — verdict written later by PA tool. |
| 20 | `MissionRunnerConfig` (incl. `auto_emit_verdict`) | Frozen per-job runner config | All employees | `core/employees/mission_runner.py:529-590` | **SAFE** | `auto_emit_verdict=False` opt-out is the S1267 Bug Triage precedent |
| 21 | `OpsRun(domain='mission')` | Mission identity row | MissionRunner | `core/models_ops_runs.py:11-89` | **SAFE** | S1250 PR 3 added mission-domain fields specifically to avoid a separate MissionRun model |
| 22 | `OpsRunEvent` (idempotent on (run, label)) | Step + verdict + escalation timeline | MissionRunner | `core/models_ops_runs.py:91-118` | **SAFE** | Labels include `run_started`, `<step>_started/_passed/_failed`, `authority_contract_observed`, `verdict_issued:<v>`, `inter_employee_notice_emitted` (proposed S1268) |
| 23 | `emit_mission_verdict()` | Idempotent verdict emission | MissionRunner default path; PA `mission_verdict` tool | `core/employees/mission_verdict.py:63-175` | **SAFE** | Three verdicts (certified/rejected/deferred); status flip on first verdict |
| 24 | `post_shift_report()` | One DM per terminal mission per (employee, job) thread | All employees | `core/employees/comms.py:228-367` | **SAFE** | Bounded metadata; idempotent on (thread, mission_id); terminal-gate enforced |
| 25 | `_persist_to_summary()` | Atomic OpsRun.summary merge | Mission step persistence | `core/employees/_persistence.py:36-59` | **SAFE** | Lifted to shared module in S1267 PR 4.0 |
| 26 | Authority contract observation (`authority_contract_observed` event, schema v1) | Per-mission shape observation (warn-mode, NEVER blocks) | MissionRunner | `core/employees/mission_runner.py:264-894` | **WRAPPER** | Observation only — no enforcement. Cross-employee scope confirmed Rigby S1268 |
| 27 | `AgentFollowupSubscription` (states armed→fired/expired/cancelled) | Bridge: AgentExecution terminal → conversation banner | PA-driven dispatches | `core/models_unified_system.py:1017-1116` | **WRAPPER** | Silent banner suppression on `auto_followup=False` is the footgun |
| 28 | Atomic queryset-update fire (`state='armed'` filter → `state='fired'`) | Re-entrancy guard for banner emission | `fire_agent_followup_subscriptions` | `core/tasks_agents.py:336-490` | **SAFE** | DB-layer guarantee — rowcount=1 under concurrent calls (S1175 lock-in) |
| 29 | `schedule_followup` / wakeup TTL | Wall-clock-bound future wakeup | PA agentic loop | `core/models_unified_system.py:1085` (expires_at field) | **SAFE** | Lifecycle-bound (NULL expires_at) vs. wall-clock-bound (TTL); beat task `expire_stale_followup_subscriptions` every 2 min |
| 30 | `EventBus` Redis Streams (`core/services/event_bus.py:90`) | Pub/sub with durable consumer groups + DLQ | Spider → opportunity / opportunity → scoring / outcome tracking | `core/services/event_bus.py:21-728` | **WRAPPER** | **8 named streams** (NOT 6 per prior audit): `SPIDER_DATA`, `OPPORTUNITY_CREATED`, `OPPORTUNITY_SCORED`, `VALIDATION_REQUIRED`, `VALIDATION_DECIDED`, `OUTCOME_RECORDED`, `MODEL_TRAINED`, `SYSTEM_ALERT` (`event_bus.py:21-30`); DLQ at `mi:dead_letter` (line 106) |
| 31 | EventBus consumer groups | At-least-once delivery + pending-tracking | `scoring_workers`, `validation_workers`, `analytics_workers` | `core/services/event_bus.py:119-135` | **WRAPPER** | xgroup_create with mkstream; auto-init at module load |
| 32 | EventBus `claim_stale()` (5-min beat) | Reclaim unacknowledged events | `claim_stale_events` beat task | `core/services/event_bus.py:393-449`, `core/celery.py:512-554` | **SAFE** | Standard Redis-Streams stuck-event recovery |
| 33 | `Deliverable` + `DeliverableEvent` (status_transition) | Escalation surface + audit | MissionRunner escalation path | `core/models_deliverables.py:84-283,561-610` | **SAFE** | Status transitions carry `ctx.ops_run_id` correlation |
| 34 | Beat-task `add_critical_celery_tasks` (S1157 PR #2243 single source of truth) | Materialize `core/celery.py` `beat_schedule` to PeriodicTask rows | Beat scheduler | `core/management/commands/add_critical_celery_tasks.py` | **SAFE** | 91 enabled + 5 disabled rows per inventory |
| 35 | `check_retry_budget(name, window_seconds, max_retries)` | Application-layer retry-rate limiter | High-cost LLM tasks | e.g., `core/tasks_content.py:3198-3201`, `core/tasks_financial.py:675-678,2427-2430` | **SAFE** | Prevents runaway retry storms on external API failures |
| 36 | `MessageThread` + `ThreadParticipant` + `DirectMessage` | Inbox-style persistent threads | Shift reports + inter-employee notices (proposed) | `core/models_messaging.py:21-141` | **SAFE** | Metadata-keyed thread lookup; per-user read cursor |
| 37 | `messaging_tool` (read-only v0; send_message OFF) | LLM surface for inbox reads | PA Rigby tool | `core/services/td_handlers_core.py:3693-3711` | **DO NOT REUSE** (send path) | `MESSAGING_SEND_DISABLED` returned unless `MESSAGING_TOOL_ALLOW_SEND=True` |
| 38 | `HumanAttentionItem` | Decision-required attention surface | 31 creators across the platform | `core/models_human_interface.py:20+`; creator inventory in §3.5 below | **SAFE** | Auditor NOT in creators list — confirms S1268 sketch §8.1 |
| 39 | `HumanAttentionLifecycleService` (beat every 10 min) | Auto-expire / dismiss / escalate / approve | All HAIs | `core/services/human_attention_lifecycle.py:36-728` | **SAFE** | Auto-escalate ladder low→med (72h)→high (48h)→critical (24h); auto-dismiss TTL by urgency |
| 40 | `HumanFeedbackRecord` (with `fed_to_ml` flag) | Decision learning feedback loop | All HAI decisions | `core/models_human_interface.py:230-266` | **SAFE** | Only round-trip pattern with learning today — agent acts → human decides → ML learns |
| 41 | `HumanPreference` (with auto_approve_low_risk, trusted_agents, learned topic_weights) | Per-user collaboration policy | HAI lifecycle service | `core/models_human_interface.py:268-358` | **WRAPPER** | Learned fields update over time — read-only outside lifecycle service |
| 42 | `OrchestrationApprovalGate` | Bridge: orchestration step → HAI → human decision | Workflow approval | `core/models_orchestration.py:397-535`, `core/services/orchestration_approval.py:57-135` | **SAFE** | Five states (pending/approved/rejected/modified/auto_approved/expired) |
| 43 | `Initiative` + `InitiativeStage` (5 stages) | Durable multi-stage work state machine | Strategic initiatives | `core/models_document_registry.py:37-715` | **WRAPPER** | Stages: research_brief / prototype_plan / evaluation_protocol / technical_design / pilot_execution; founder-intent gate; semantic-drift gate (embeddings); fast_track caps at stage 2 |
| 44 | `InitiativeActionItem` | Per-initiative durable task | Strategic initiatives | `core/models_document_registry.py:1951+` | **WRAPPER** | Existing pattern for assigning durable work to an agent |
| 45 | Diagnostic signal pattern (mark/auto-clear with `update_fields` recursion guard) | Lifecycle observation without signal storm | Initiative diagnostics, Deliverable status | `core/signals/initiative_diagnostic_signals.py:50-96`; `core/signals/deliverable_status_signals.py:83-150+` | **SAFE** | Recursion-safe signal pattern usable for any post_save lifecycle |
| 46 | `SituationTrigger` + `TriggerEvent` (30+ types) | Threshold-based spider-data alerts | Whale movements, price crashes, job matches, SEC filings | `core/models_situation_triggers.py:128-300`; `core/signals/trigger_signals.py:26-72` | **SAFE** | cooldown_minutes prevents spam; deterministic match → fire → TriggerEvent row |
| 47 | `WorkspaceTrigger` + `WorkspaceTriggerConfig` (Session 785 hybrid autopilot) | Spider-data → workspace work items | Workspace autopilot | `core/models_skin_layer.py:774,798,1075`; `core/signals/trigger_signals.py:79-171` | **WRAPPER** | `dedupe_hash` field guards duplicates; conductor loop `workspace_autopilot_tick` UNKNOWN exact location |
| 48 | `SignalCluster` + entity-token clustering (Session 1139) | Cross-spider pattern detection | `signal_aggregation_service` | `core/services/signal_aggregation_service.py:33-1161,489-615` | **SAFE** | `MIN_CLUSTER_SIZE=3`, `MIN_TOKEN_FREQUENCY_IN_WINDOW=2`, `MIN_SHARED_TOKENS=2`; 10 pattern types |
| 49 | `ContentScoringService` (rule-based reach/intent/replicability/source_confidence) | Per-cluster track assignment | Signal-aggregation pipeline | `core/services/content_scoring_service.py:16-167` | **SAFE** | No-LLM scoring; runs on every cluster create/update |
| 50 | `AutoTopic` + `generate_auto_topics()` | High-confidence cluster → topic candidate | Signal-aggregation daily tick | `core/services/signal_aggregation_service.py:957-1161` | **WRAPPER** | `MAX_AUTO_TOPICS_PER_DAY=10` rate limit; downstream Initiative creation is UNCERTAIN (not traced) |
| 51 | `ProactiveIntelligenceService` (19 autonomous situations) | Proactive intel injection | PA enrichment pipeline | `core/services/proactive_intelligence.py:29-200+` | **UNKNOWN** | Framework exists; production wiring into beat schedule UNCONFIRMED |
| 52 | `AdvisorRegistry` + `AdvisorContextBuilder` (30 advisors) | Context-injection into agent prompts | AgentRouter `_get_advisor_context()` | `advisors/registry.py:142-154`; `core/services/advisor_context_builder.py:23-150+` | **DO NOT REUSE** as callable | Advisors are PROMPT CONTEXT, not callable. No `advisor_tool`. `LLMAdvisor` class exists but integration UNCLEAR |
| 53 | `BoardroomMLService` + `BoardroomLearningService` | ML decision-prediction + recording on HAI | `auto_approve_boardroom_items` (every 30 min beat) | `core/services/boardroom_ml_service.py:31-146`; `core/services/boardroom_learning_service.py:32-126` | **SAFE** | "Boardroom" = ML on top of HAI, NOT multi-agent debate |
| 54 | `governance_tool` (PA tool) | Unified governance inbox: attention, decisions, triage | PA function-calling surface | `core/services/pa_tool_schemas.py:3157-3219` | **SAFE** | Replaces removed boardroom_tool + human_decisions_tool aliases |
| 55 | `GovernanceState` (mode: normal/throttle/freeze/safe_mode; scope: global/agent/desk) | Autonomy control plane | Governance | `core/models_governance.py:17-114` | **SAFE** | TTL-based auto-expiry; per-scope overrides |
| 56 | `KillSwitch` (TTL-required) | Emergency blocks | Governance | `core/models_governance.py:116-189` | **SAFE** | Targets: scheduler/queue/agent_family/publishing/outbound/deploys |
| 57 | `BodyCoordinator` + 9 body systems + 28 event handlers | Autonomic reflex layer | System-health monitoring | `core/services/body_coordinator.py:110-300+` | **WRAPPER** | Not a collaboration primitive per se but EMITS events that trigger remediation; `coordinate(force=False)` main loop |
| 58 | `/api/inbox/threads/` HTTP (15s poll) | Inbox HTTP surface | Web UI | `core/views_inbox.py` | **SAFE** | Surfaces DM + (implicit) HAI |
| 59 | `_broadcast_new_message(thread, msg)` (S1268 Rigby additions) | Push DM to inbox UX path | DM creation | `core/services/td_handlers_core.py:3773-3775` → `core/views_inbox._broadcast_new_message` | **SAFE** | Required when DMs cross UI boundary |
| 60 | `/ws/system-events/` (9 base events + 7 orchestration events) | WebSocket real-time event stream | Inbox UI, system monitors | `core/consumers/system_events_consumer.py:1-290` | **WRAPPER** | Does NOT carry DM-arrived event today; orchestration events landed Session 768 |
| 61 | `RIGBY_EVENT_INTAKE_ENABLED` flag + `rigby_event_intake` service | Mission-side event intake from agent completion | Deliverable status transitions | `core/services/rigby_event_intake.py:155-465`; `core/settings.py:108,136` | **WRAPPER** | Default OFF — can be toggled per-environment; idempotent on (event_ref, mission_id) |
| 62 | Anthropic / OpenAI client factories | Centralized timeout + retry contract | All LLM callers (Tier 1 migrated) | `core/services/anthropic_client_factory.py:38-50`; `core/services/openai_client_factory.py:68-72,204-215` | **SAFE** | Per-(api_key, base_url) caching; guardrails forbid passing timeout/max_retries/api_key kwargs |
| 63 | `LLMCallEvent` cleanup watchdog (S1221 Tier 2) | Reaps STARTED rows >10min as FAILED | Beat (every 10 min) | `core/tasks.py:1660`; `core/celery.py:138-151` | **SAFE** | Cleanup watchdog precedent for any new "in-flight forever" state |
| 64 | `BaseAgent._call_openai` total-request bound (S1221 Tier 1) | Cap = max(180s, llm_timeout × 2.5) | All agent OpenAI calls | `core/agents/base_agent.py` (S1219 PR #2519) | **SAFE** | Closes the httpx per-chunk timeout loophole |

**Inventory note.** 64 rows. Each row is either a Django model, a
frozen dataclass, a Python service helper, a Celery surface, a PA
tool, a signal, an HTTP/WebSocket consumer, or a beat-scheduled
runtime invariant. Counts mirror PLATFORM_INVENTORY when
applicable; do not hand-edit.

---

## 3. Existing Collaboration Flows

The platform's runtime-verified collaboration paths are mapped
below. Each diagram is text-only — runtime is the source of truth.

### 3.1 Agent → Agent (synchronous, in-process)

```
caller agent
  │
  ▼
BaseAgent.delegate_to_agent(target_agent_name, task, context)
  │  guard: delegation_depth < max_depth=3 (base_agent.py:905)
  ▼
AgentRouter.route(target_agent_name, task, context)
  │  resolves trace_id, parent_execution_id, root_execution_id
  │  starts heartbeat daemon (30s tick)
  ▼
target.execute(task, context) → AgentResult
  │
  ▼
ToolCallRecord written on tool calls
LLMCallEvent written on LLM calls
AgentExecution.status flips to completed/failed
```

Evidence: `core/agents/base_agent.py:890-950`,
`core/agent_router.py:836-945`,
`core/agent_router.py:2945-2980`.

### 3.2 Agent → Celery → Agent (asynchronous, durable)

```
caller
  │
  ▼  execute_agent.delay(execution_id)
  │  (queue resolved by CELERY_TASK_ROUTES)
  ▼
Celery worker picks up
  │
  ▼  AgentRouter.route(..., existing_execution_record=row)
  │  same execution row — no double-create
  ▼
target.execute(task, context) → AgentResult
  │
  ▼
[if conversation_id in context AND auto_followup != False]
  AgentFollowupSubscription armed at dispatch (tasks_agents.py:232-280)
  │
  ▼  on terminal save: signal handler fires
  AgentFollowupSubscription.state armed → fired (atomic queryset update)
  │
  ▼  broadcast on pa_conversation_<conversation_id>
  PAConversationConsumer.agent_completed
  │
  ▼  persists Rigby ChatConversation row + banner
```

Evidence: `core/tasks_agents.py:232-280,336-490`;
`core/models_unified_system.py:1017-1116`.

### 3.3 Agent → Agent (parallel, ThreadPoolExecutor)

```
WorkflowOrchestrationAgent (or MeetingCoordinatorAgent)
  │
  ▼  ThreadPoolExecutor(max_workers=N)
  │  futures = [executor.submit(sub_agent.execute, task, ctx) for sub in agents]
  ▼
[each sub_agent.execute runs concurrently in worker process]
  │
  ▼  as_completed(futures, timeout=SUB_AGENT_TIMEOUT=180)
  │  per-future timeout (NOT pool-total timeout)
  ▼
caller aggregates results into result['steps']
```

Evidence: `core/agents/workflow_orchestration_agent.py:47,302`,
`core/agents/executive/meeting_coordinator_agent.py:30,35-39`.

### 3.4 Celery chain + group (durable fan-out / fan-in)

```
HybridAgentExecutor
  │
  ▼  build_celery_chain([step1, step2, ...])
  workflow = chain(execute_agent_task.si(...), execute_agent_task.si(...))
  workflow.apply_async()
  │
  ▼  step N output → step N+1 input (Celery passes via result backend)
  ▼  on worker death: tasks remain in queue (acks_late=True default)
  ▼  result available via AsyncResult

PARALLEL VARIANT:
  job = group(execute_agent_task.s(...) for agent in agents)
  result = job.apply_async()
  result.get()  # blocks until all return
```

Evidence: `ai_core/agents/hybrid_executor.py:244,260,351,355`.

### 3.5 HAI: 31 creators, lifecycle-managed, no Auditor

```
[Creators write HumanAttentionItem with source_type + payload]

Authority levels evidenced in §3.5 below:
- Orchestration (orchestration_approval.py:95, :174)
- Gate Progression Pipeline (gate_progression_pipeline.py:358, :573)
- Opportunity Execution (opportunity_execution_pipeline.py:389)
- Spider Action Pipeline (spider_action_pipeline.py:636)
- Priority Governor (priority/governor.py:270)
- Implementation Executor (implementation_executor.py:513)
- Human Interface Service (human_interface_service.py:662)
- Content Idea Pipeline (content_idea_pipeline.py:399)
- Platform Command View (views_platform_command.py:929)
- Agent tasks (tasks.py:380, :10854)
- Initiative tasks (tasks_initiatives.py:3054)
- Ops tasks (tasks_ops.py:3777)
- Autonomous Remediation (autonomous_remediation_orchestrator.py:1419)
- OpsAutopilot governance (ops_autopilot/governance.py:528)
- OpsAutopilot core (ops_autopilot/core.py:2051, :2117, :2626, :2691, :2844)
- OpsAutopilot verification (ops_autopilot/verification.py:702)
- TD handlers (td_handlers_agents.py:4110, :4882)
- EPA handlers consultation (epa_handlers_tools.py:5166)
- Misc tasks (tasks_misc.py:5079, :5274)

NOT in creator list: Platform Auditor, Chief of Staff, Bug Triage Specialist, Rigby (Documentation Manager) — confirms employees do NOT create HAIs today.
```

Lifecycle (every 10 min beat — `process_human_attention_lifecycle`):

```
   ┌──────────────────────────────────────────────────────────┐
   │  HumanAttentionLifecycleService._coordinate()            │
   │  (core/services/human_attention_lifecycle.py:36)         │
   ├──────────────────────────────────────────────────────────┤
   │  1. _expire_old_items()       expires_at < now → expired │
   │  2. _auto_dismiss_stale_items()  pending > TTL by urgency│
   │       low: 7d / med: 5d / high: 4d / critical: 3d        │
   │  3. _auto_escalate_aging_items() age ladder              │
   │       low→med (72h) / med→high (48h) / high→crit (24h)   │
   │  4. auto_approve_item()       low-risk + user prefs      │
   │       → HumanFeedbackRecord                              │
   │       → may trigger orchestration workflow               │
   └──────────────────────────────────────────────────────────┘
```

Evidence: `core/services/human_attention_lifecycle.py:36-728`,
`core/celery.py:691-722`.

### 3.6 Spider → Signal → Trigger → Work

```
[Spider runs (Celery beat or manual)]
  │  ai_core/spiders/phase4_orchestrator.py (orchestrates 80+)
  ▼
LegacySpiderData rows persist
  │
  ▼  post_save signal on LegacySpiderData
  │  (core/signals/trigger_signals.py:241-271)
  ├─→ evaluate_triggers_for_spider_data() — SituationTrigger threshold match
  │      → trigger.fire(spider_data, matched_value) → TriggerEvent
  │      → process_trigger_events.apply_async()
  │
  └─→ evaluate_workspace_triggers_for_spider_data() — WorkspaceTriggerConfig match
         → WorkspaceTrigger.create_from_spider_data() [dedupe_hash check]
         → conductor loop workspace_autopilot_tick [LOCATION UNKNOWN]

[Periodically (every 30 min beat):]
  aggregate_spider_signals
    → SignalCluster (entity-token clustering, MIN_CLUSTER_SIZE=3)
    → strength/confidence/novelty/urgency scored
    → ContentScoringService rule-based reach/intent/replicability
    → status='active' or 'detecting'
    → maybe emit signal.cluster_promoted event

[Daily (rate-limited 10/day):]
  generate_auto_topics(min_confidence=0.6)
    → AutoTopic rows with derived_from_pattern + suggested_agent_names
    → [downstream Initiative creation UNCERTAIN — not traced]
```

Evidence: `core/services/signal_aggregation_service.py:33-1161`;
`core/signals/trigger_signals.py:26-171`;
`core/models_situation_triggers.py:128-300`;
`core/models_skin_layer.py:774,798,1075`.

### 3.7 Spider → EventBus → Consumer Group

```
[Spider task or Celery service]
  │
  ▼  publish_spider_data_event() / publish_opportunity_*_event()
  │  (core/services/event_bus.py:539-616)
  ▼
Redis Streams XADD onto stream
  (stream max length 10,000)
  │
  ▼  consumer group XREADGROUP picks up (at-least-once)
  │  (event_bus.py:191-231 subscribe pattern)
  ▼
handler(event) — invoked per registered ConsumerInfo
  │  on success: XACK
  │  on exception:
  │      → _move_to_dead_letter(event)
  │      → DLQ at `mi:dead_letter` (event_bus.py:106,451-477)

Periodic claim_stale_events (every 5 min beat)
  reclaims pending events from disconnected consumers
  (event_bus.py:393-449)
```

Evidence: `core/services/event_bus.py:21-728`,
`core/celery.py:512-554`.

### 3.8 Initiative 5-Stage Durable State Machine

```
[Initiative created — Stage 1 PENDING]
  │
  ▼  current_stage = 1; founder_intent_set check
  │
  ▼  Stage 1 → DRAFT → IN_REVIEW → APPROVED
  │  advance_stage() called (models_document_registry.py:143)
  │
  ▼  Stage 2 PENDING [requires founder intent: speed/risk/budget]
  │
  ▼  fast_track path: cap at Stage 2 (institutional path continues)
  │
  ▼  Stage 2-5 each have stage_N_approved gates
  │  Semantic drift gate: cosine similarity threshold (Session 914.3)
  │
  ▼  All stages APPROVED → InitiativeActionItem rows materialized
  │  Action items assigned to agents (assigned_to FK)
```

Evidence: `core/models_document_registry.py:37-715,1951+`,
`docs/DREAM_INITIATIVE_WORKFLOW.md`.

### 3.9 Employee → MissionRunner → Deliverable

```
[Beat or run_now]
  │
  ▼  core.tasks_<job>.run_<job>() — entry task per employee
  ▼  MissionRunner.run(...) — daily idempotency (calendar date)
  │
  ▼  get_or_create OpsRun(domain='mission', run_kind=...)
  ▼  emit run_started OpsRunEvent
  ▼  [opt] emit authority_contract_observed (warn-mode, never blocks)
  ▼  [opt] preflight_fn(summary_acc)
  ▼  Step loop:
  │    emit <step>_started → fn(mission) → emit <step>_passed | _failed
  │    (on first failure: emit remaining as _skipped)
  ▼  [opt] postflight_fn(PostflightContext)
  ▼  on failure → escalation:
  │    dedupe check (failed_step + error_signature, 24h window)
  │    create or append-to-prior Deliverable
  │    force status completed → ready (audit transition)
  │    [opt] pa_post_fn(PAPostContext) — only if primary_chat_id set
  │    emit escalation_emitted
  ▼  [opt] shift_report_fn(mission) → post_shift_report DM
  ▼  [conditional, config.auto_emit_verdict] emit_mission_verdict
  ▼  return MissionRunResult
```

Evidence: `core/employees/mission_runner.py:1-1758`,
`core/employees/comms.py:228-367`,
`core/employees/mission_verdict.py:63-175`.

### 3.10 Human → Agent (via HAI decision)

```
[HAI created, status=pending]
  │
  ▼  inbox 15s poll surfaces it in /api/inbox/threads/ → UI
  ▼  /ws/system-events/ broadcasts gate_became_critical (orchestration_paused, etc.)
  │
  ▼  Human decides:
  │   approve | reject | modify | defer | delegate | ignore
  ▼
HAI.record_decision(decision, feedback, confidence)
  → HumanFeedbackRecord written (fed_to_ml=False initially)
  → status pending → acted (or deferred/ignored)
  ▼
[If decision was 'approve' on orchestration HAI:]
  → OrchestrationApprovalGate.approve(user, notes)
  → Workflow resumes from paused state
  → Downstream agent dispatched (e.g., execute_agent.delay)

[Async: ML learning loop]
  FeedbackProcessor processes HumanFeedbackRecord
  → fed_to_ml flag flipped to True
  → AgentLearning / LearningInsight / AgentMemory updated
  → HumanPreference learned stats updated
```

Evidence: `core/services/human_attention_lifecycle.py:256-351`,
`core/services/orchestration_approval.py:57-135`,
`core/models_feedback_processing.py`.

### 3.11 Scheduler → Employee / Scheduler → Agent

```
[Celery beat (core/celery.py beat_schedule)]
  │
  ▼  schedule entry → PeriodicTask row
  │  (sync via add_critical_celery_tasks mgmt command, S1157 PR #2243)
  ▼  due time → Celery dispatches task
  ▼
[Employee path]
  core.tasks_<job>.run_<job> → MissionRunner.run(...)
  → 4 daily-cadence employees (1 weekly): rigby docs, platform auditor,
     chief of staff, bug triage specialist

[Agent path]
  Many beat tasks dispatch agents directly via execute_agent.delay
  or via Service helpers (e.g., signal_aggregation_service)
```

Evidence: `core/celery.py:37-797`,
`core/management/commands/add_critical_celery_tasks.py`,
`core/employees/jobs.py:1327-1347`.

### 3.12 Deliverable → Follow-up Work

```
[Deliverable.status changes]
  │
  ▼  pre_save: stash old status
  ▼  post_save: classify_transition (forward/backward/terminal/same)
  │  → DeliverableEvent(event_type='status_transition', source=<employee>)
  │  → metadata: ops_run_id, error_signature (for audit trail)
  ▼  [if RIGBY_EVENT_INTAKE_ENABLED]
       rigby_event_intake.enqueue(event_ref, deliverable_id)
       → idempotent on (event_ref, mission_id)
       → dry_run=True today (per Session 1250 PR 5)
```

Evidence: `core/signals/deliverable_status_signals.py:1-150+`;
`core/services/rigby_event_intake.py:155-465`.

---

## 4. Delegation Mechanisms

The platform has multiple delegation modes. Each is characterized
on five axes below.

| Mechanism | Sync/Async | Durable? | Observable? | Evidence emitted | Guardrails |
|---|---|---|---|---|---|
| `AgentRouter.route()` direct | **Sync** | No (in-process) | ✓ via AgentExecution row | AgentExecution, ToolCallRecord, LLMCallEvent | Heartbeat daemon; max_depth=3 on delegation |
| `execute_agent.delay()` | **Async** | **Yes** (Celery queue) | ✓ via AgentExecution + CeleryTaskEvent | All above + CeleryTaskEvent + queue routing | Worker child recycling; `acks_late` per task; total-request bound |
| `BaseAgent.delegate_to_agent()` | **Sync** | No | ✓ via AgentExecution lineage | Same as direct + delegation_depth in context | `max_depth=3` (base_agent.py:905); per-call timeout (180s SUB_AGENT_TIMEOUT) |
| `AgentFollowupSubscription` (wakeup) | **Async (event-driven)** | **Yes** (DB) | ✓ via subscription state transitions | `state` field transitions; broadcast log | Atomic `state='armed'` filter (re-entrancy guard); `expires_at` TTL; 2-min beat expiry sweep |
| `schedule_followup` (wall-clock TTL) | **Async (timed)** | **Yes** (DB) | ✓ same as above | Same as above + `expires_at` carried | TTL bounded; 600s cap on after_seconds |
| Celery retry (default) | **Async** | **Yes** (Celery queue) | ✓ via CeleryTaskEvent | retry_count field on LLMCallEvent | `acks_late=True` default; `max_retries=3` default |
| Application-layer retry budget (`check_retry_budget`) | **Sync gate** | N/A (gate only) | ✓ via task logs | Custom log markers | Per-task window + max_retries cap (typical 5/hr) |
| `WorkflowOrchestrationAgent` step iteration | **Sync** | No (in-process) | ✓ via `result['steps']` field | `result['steps'][i].result.<...>` | Iteration cap reduced 5→3 (S1069); ThreadPoolExecutor SUB_AGENT_TIMEOUT |
| `MissionRunner` step loop | **Sync** | No (in-process during run) | ✓ via OpsRunEvent timeline | Step start/pass/fail/skipped events | Daily idempotency; 24h dedupe; `auto_emit_verdict` opt-out |
| Celery `chain` | **Async** | **Yes** | ✓ via CeleryTaskEvent per task | Each task's row | Per-task retry config; `acks_late` |
| Celery `group` | **Async** | **Yes** | ✓ via per-task CeleryTaskEvent | Per-task row + group_id correlate | Same as chain |
| Celery `chord` | (not in use) | N/A | N/A | N/A | N/A |
| EventBus `publish` → consumer group | **Async** | **Yes** (Redis Streams) | ✓ via stream replay + DLQ | Stream entry IDs; DLQ entries | At-least-once; consumer group XACK; `claim_stale` reclaim; max stream length 10,000 |
| HAI → human decision → orchestration resume | **Async (long-tail)** | **Yes** | ✓ via HAI status + HumanFeedbackRecord | All transitions + feedback row | TTL by urgency; auto-escalate ladder; auto-approve gating |
| OrchestrationApprovalGate | **Async** | **Yes** | ✓ via gate state + HAI bridge | State transitions: pending/approved/rejected/modified/auto_approved/expired | TTL; auto-approve config; explicit `decided_by` |
| WorkspaceTrigger → conductor loop | **Async** | **Yes** | Partial (model durable; conductor location UNKNOWN) | Trigger rows | `dedupe_hash` field; conductor cadence UNKNOWN |
| `claude_code_tool` dispatch | **Async** | **Yes** (Celery queue) | ✓ post-S1262 PR #2752 | AgentExecution at entry; post_back_status field | Receipt chain wired; fail-loud on post-back failure |

**Observability scoring summary (out of 5):**
- AgentRouter direct / async: 5/5
- AgentFollowupSubscription: 5/5 (DB state machine)
- WorkflowOrchestrationAgent: 3/5 (in-process; relies on result envelope)
- Celery chain/group: 4/5 (per-task observable; aggregate weak)
- EventBus: 4/5 (stream observable; DLQ surfaces failures)
- HAI lifecycle: 5/5 (status + lifecycle events + feedback)
- WorkspaceTrigger conductor: 2/5 (conductor location UNKNOWN)

---

## 5. Mission Coordination

This section answers the spec's nine sub-questions about mission
durability and coordination.

### 5.1 How are missions started?

**Three paths today:**

1. **Beat schedule** — `core.tasks_<job>.run_<job>` Celery task
   dispatched by Celery beat at a periodic-task schedule
   (`core/celery.py:37-797`). Production employees today:
   - `rigby_documentation_manager_daily` — daily docs cascade
   - `generate-morning-brief-daily` — daily 07:00 Denver
     → `chief_of_staff_morning_brief_run` (S1258 PR 3.3)
   - `platform_audit_weekly` — proposed Monday 06:30
   - `bug_triage_daily` — daily 08:00 Denver
     (S1267 PR 4.3 flip)
2. **PA tool `employee_tool action=run_now`** — Rigby-gated manual
   override; routes via `_RUN_NOW_TASKS` registry in
   `core/services/td_handlers_employee.py:251-263`.
3. **Management command** — e.g.,
   `python manage.py run_<job>` for ops investigation.

### 5.2 How are missions ended?

By verdict emission. Three terminal verdicts:

- `certified` → `OpsRun.status = 'passed'`
- `rejected` → `OpsRun.status = 'failed'`
- `deferred` → `OpsRun.status = 'partial'`

Verdict emission paths:

- **Default (auto_emit_verdict=True)**: MissionRunner emits at end
  of successful run (`mission_runner.py:1134+`).
- **Bug Triage opt-out (auto_emit_verdict=False)**: runner skips;
  PA `mission_verdict` tool (Rigby-gated) emits the verdict
  manually after Rigby/human review
  (`td_handlers_employee.py:434-503`).

Verdict emission is idempotent on (mission_id, verdict) via
`get_or_create` on the `verdict_issued:<v>` OpsRunEvent label
(`mission_verdict.py:63-175`).

### 5.3 How are retries triggered?

**Three retry layers:**

1. **Celery retries** (per-task `max_retries`, `retry_backoff`,
   `autoretry_for`). Standard default = 3 retries; PA + Employee
   OS tasks override `acks_late=False`
   (`core/tasks.py:2159` for `process_pa_chat_task`).
2. **Application-layer retry budget**
   (`check_retry_budget(name, window_seconds, max_retries)`) —
   gates high-cost LLM tasks to prevent runaway storms.
   Examples: `generate_daily_betting_brief` max 5/hour
   (`core/tasks_content.py:3198-3201`);
   `aggregate_roi_metrics_daily` 5/hour
   (`core/tasks_financial.py:675-678`).
3. **Mission-level escalation dedupe** — MissionRunner does NOT
   retry within the same calendar day (daily idempotency); a
   "retry" is the next day's scheduled run. Same-signature
   failures within 24h merge into the existing escalation
   Deliverable rather than create new ones
   (`mission_runner.py:1257-1261`).

### 5.4 How are failures handled?

Layered:

- **Step failure** (in-mission): MissionRunner emits
  `<step>_failed`, marks remaining steps `<step>_skipped`, runs
  escalation path (Deliverable + optional PA-chat post + optional
  shift report).
- **Mission failure** (verdict='rejected'): same as step failure
  + verdict emission to `OpsRun.status='failed'`.
- **Celery task failure**: `CeleryTaskEvent.status='FAILURE'` row
  written; per-task `acks_late` policy controls whether the task
  re-queues for another worker pickup.
- **LLM call failure**: `LLMCallEvent.status='FAILED'` + `error_type`
  classification (timeout / rate_limit / auth / api_error /
  client_error / cancelled / unknown); 10-min cleanup watchdog
  marks STARTED→FAILED on stale rows
  (S1221 PR #2520).
- **EventBus consumer failure**: event moved to dead-letter
  stream `mi:dead_letter`
  (`event_bus.py:106,451-477`).
- **HAI auto-escalate ladder**: pending past TTL → urgency
  bumps low→med→high→critical
  (`human_attention_lifecycle.py:181-221`).

### 5.5 What survives process restarts?

| State | Survives process restart? |
|---|---|
| Celery task in queue | **Yes** (Redis/RabbitMQ broker) |
| Celery task in-flight | **No** if `acks_late=False`; **Yes** (re-queued) if `acks_late=True` (worker death rolls back ack) |
| AgentFollowupSubscription | **Yes** (DB row) |
| OpsRun / OpsRunEvent | **Yes** (DB rows) |
| Deliverable / DeliverableEvent | **Yes** (DB rows) |
| LLMCallEvent / ToolCallRecord | **Yes** (DB rows) |
| MissionRunner step state (in-process) | **No** — restart re-runs from get_or_create OpsRun (daily idempotency) |
| WorkflowOrchestrationAgent in-process iteration | **No** — restart loses partial step state |
| Redis Streams entries | **Yes** (Redis durable mode) |
| EventBus consumer-group offsets | **Yes** (Redis) |
| HAI / HumanAttentionItem | **Yes** (DB) |
| Heartbeat thread state | **No** — cleanup beat picks up no-heartbeat-60min as failed |
| `sys.modules` cache | **No** — by definition, but causes stale-code bugs across restart (memory: worker-restart discipline) |

### 5.6 What survives Redis restarts?

| State | Redis durability |
|---|---|
| Celery task queue | If broker is Redis: depends on persistence config (RDB/AOF). If RabbitMQ: not Redis. |
| Redis Streams (EventBus) | Yes if AOF/RDB persistence enabled; check infra config |
| Redis cache (general) | No — cache is ephemeral |
| Daphne WebSocket sessions | No |
| Celery beat schedule (next-fire times) | No — recomputed from PeriodicTask DB rows |

Production behavior in event of Redis restart depends on the
broker + persistence configuration. UNKNOWN exact infra config in
this audit.

### 5.7 What survives database restarts?

All Django ORM-backed state survives DB restart by definition
(Postgres durability). Includes:

- All Mission / Agent / Tool / LLM / HAI / Deliverable / Trigger
  state
- ConsumerGroup metadata (in Redis), but consumer offsets
  also persisted in Redis
- PeriodicTask rows for beat
- AgentFollowupSubscription armed rows

What doesn't survive (and is expected not to):

- In-process state (heartbeat, ThreadPoolExecutor pools,
  ConversationOrchestrator turn count)
- Cache (`django.core.cache`)
- WebSocket sessions

### 5.8 What survives Daphne (WebSocket) restart?

Nothing in-flight: open WS connections drop. Reconnection on
client side recovers via 15s inbox poll + WS reconnect logic
(client-side; UNKNOWN exact implementation here).

System events are NOT durable across Daphne restart — they are
broadcast-and-forget. Anything that needs durability must use
Celery/DB/EventBus, not WS.

### 5.9 What is reconstructable later?

The audit-trail join (`evidence_for_mission()` at
`core/employees/status.py:347-508`) reconstructs the full mission
post-hoc by joining:

- OpsRun (base) + OpsRunEvent (timeline)
- Deliverable + DeliverableEvent (escalation)
- ChatConversation (PA-chat post if any)
- LLMCallEvent (correlated via `metadata.ops_run_id`)
- ToolCallRecord (correlated via `parameters.ops_run_id` + trace_id)

So: yes, missions are fully reconstructable later assuming the
employee step code populates `metadata.ops_run_id` on LLM /
tool calls (an enforcement that should be verified per employee).

For agent execution chains, `AgentExecution.trace_id`,
`parent_execution_id`, and `root_execution_id` reconstruct the
delegation tree. Cancel propagation already walks this chain in
production
(`models_unified_system.py:967-968`,
`core/services/cancel_registry.py:175-192`).

---

## 6. Evidence and Auditability

For every collaboration primitive, score:

- **A** — Who requested work?
- **B** — Who accepted work?
- **C** — Who performed work?
- **D** — Who completed work?
- **E** — What evidence exists?
- **F** — Can the interaction be replayed later?

(✓ = answerable; ✗ = not answerable today; ◎ = partial)

| Primitive | A request | B accept | C perform | D complete | E evidence | F replay |
|---|---|---|---|---|---|---|
| `AgentRouter.route()` direct | ✓ (parent_execution_id) | ✓ (AgentExecution.id) | ✓ (agent_name) | ✓ (completed_at) | AgentExecution + ToolCallRecord + LLMCallEvent | ◎ — input_data + output_data carry the I/O |
| `AgentRouter.route()` async | ✓ | ✓ | ✓ | ✓ | All above + CeleryTaskEvent | ◎ |
| `BaseAgent.delegate_to_agent()` | ✓ (delegation_depth context) | ✓ | ✓ | ✓ | Same as above + delegation_context | ◎ |
| `AgentFollowupSubscription` | ✓ (execution FK) | ✓ (conversation_id) | N/A (event-driven) | ✓ (state='fired' + fired_at) | Subscription row + signal log | ✓ |
| Celery chain | ✓ (chain header) | ✓ (per-task) | ✓ (worker hostname) | ✓ (per-task end) | Per-task CeleryTaskEvent | ✓ (re-fire from start) |
| Celery group | ✓ | ✓ | ✓ | ✓ | Per-task rows | ✓ |
| EventBus publish→consume | ✓ (event source) | ✓ (consumer group) | ✓ (consumer_name) | ✓ (XACK or DLQ) | Stream entry + DLQ if failed | ✓ via `replay()` |
| `MissionRunner.run()` | ✓ (triggered_by) | ✓ (OpsRun row) | ✓ (employee handle) | ✓ (`OpsRun.status` flip + `finished_at` always; `verdict_issued` event **conditional on `auto_emit_verdict=True`** per `mission_runner.py:1127-1145`) | Full OpsRunEvent timeline (verdict event present in 3 of 4 employees; Bug Triage opt-out per S1267) | ✓ via `evidence_for_mission()` |
| `emit_mission_verdict()` | ✓ (issued_by) | ✓ | N/A (pure write) | ✓ | OpsRunEvent row | ✓ |
| `post_shift_report` DM | ✓ (employee_key) | ✓ (recipient_user) | N/A | ✓ (created_at) | DirectMessage row | ✓ via inbox API |
| HAI → human decision | ✓ (source_type + source_agent) | ✓ (user FK) | ✓ (user) | ✓ (acted/deferred/ignored + HumanFeedbackRecord) | HAI + Feedback + lifecycle events | ✓ |
| OrchestrationApprovalGate | ✓ (orchestration FK) | ✓ (HAI FK) | ✓ (decided_by) | ✓ (gate status) | Gate + HAI + Feedback chain | ✓ |
| WorkspaceTrigger | ✓ (config FK) | ◎ (model durable; consumer UNKNOWN) | ◎ | ◎ | Trigger row | ◎ |
| Spider → SignalCluster | ✓ (spider_data_ids in cluster) | N/A (rule-based pipeline) | N/A | ✓ (cluster created_at) | SignalCluster + sample_signals | ✓ via spider_data_ids |
| Initiative stage transition | ✓ (current_stage + advance_stage) | ✓ (approver user) | ✓ (assigned agent) | ✓ (stage_N_approved) | Initiative + InitiativeStage rows | ✓ |

**Aggregate score (out of 6, summing ✓ as 1, ◎ as 0.5):**

- **Strongest** (6.0): MissionRunner, EventBus, HAI lifecycle,
  OrchestrationApprovalGate, AgentFollowupSubscription
- **Strong** (5.5): Celery chain/group, post_shift_report,
  Spider→Cluster, Initiative
- **Moderate** (4.5–5.0): AgentRouter (sync/async),
  BaseAgent.delegate_to_agent, emit_mission_verdict
- **Weak** (≤3.5): WorkspaceTrigger conductor (unknown
  consumer locator)

For Employee OS collaboration, prefer **Strongest** primitives
as the audit-trail foundation.

---

## 7. Failure Modes

Inventoried from S1268 substrate-audit-known list plus this
mission's collaboration-specific historical sweep. Each row:
cause / mitigation / status / remaining risk.

| # | Class | Session(s) | Cause | Mitigation | Status | Remaining risk |
|---|---|---|---|---|---|---|
| 1 | Receipt-chain gap on Celery dispatch | S1257-1262 | claude_code_tool returned task_id but no AgentExecution row at task entry; post-back silently skipped on conversation_id=None | PR #2752: AgentExecution at entry + S1174 follow-up wiring + fail-loud post-back | **CLOSED** | Pattern can recur on new dispatch surfaces unless contract is shared |
| 2 | Procfile↔Makefile queue parity drift | S1226, S1244 | code_jobs queue in Procfile but not Makefile → task hung silently | PR #2552/#2553 + canary test_celery_queue_parity.py | **CLOSED** | Any new queue must pass the canary; gating discipline relied on test passing |
| 3 | LLM autofills False/0 on optional params | S1227-1228 | GPT-5.2 autofills optional booleans → handler `is not None` checks fire | Sweep PR #2733+ truthy-or-default pattern | **CLOSED** | Any new tool with optional params must use the pattern |
| 4 | `auto_followup=False` suppresses banner silently | S1184 | Forensic dispatches set False, then forgotten in normal flows | Documented; default True | **MITIGATED** | Footgun if employee-collab dispatch ever sets False |
| 5 | WorkflowOrchestrationAgent result key drift | S1234 | `result['steps']` vs `step_results` vs `context` — KeyError-on-missing turned into silent empty default | PR #2609 + canonical key documented | **CLOSED** | Any orchestrator-style envelope must use schema enforcement |
| 6 | `context['user']` dict vs UnifiedUser FK | S1234 | Lane handlers injected profile dict; downstream code tried `Deliverable.user=context['user']` | PR #2608 direct `getattr(self, 'user')` | **CLOSED** | Any cross-employee context dict needs type discipline |
| 7 | deliverable_tool large-payload silent fall back to `list` | S1176+ | `update` action >6kB silently falls back to `list` (no exception) | Memory rule: use `append` for >6kB | **WORKAROUND** | Pattern still in place; root cause unknown |
| 8 | deliverable_tool status flips ignored on update | S1184 | `update status=completed` reports only `updated_fields: ['tags']` | Memory rule: status via `content_tool action=content_complete` | **WORKAROUND** | Same — root cause not fixed |
| 9 | deliverable_tool create defaults to completed | S1241 | New rows land status='completed' regardless of explicit `status='draft'` | Memory rule: always follow with `set_status to_status=ready` for draft | **WORKAROUND** | Default flip would be cleaner; deferred |
| 10 | macOS mutex.cc deadlock cascade | S1083-1084 | ML library singleton thread-unsafe; OBJC fork-safety with prefork pool | 11-PR cascade ending with `ModelRegistry.get_model` SKIP entirely on macOS | **CLOSED** | Local-dev only; production (Linux) unaffected |
| 11 | sys.modules cache requiring worker restart | S1167 | Prefork inherits parent process module cache | Worker restart discipline; document in PR description when touching task-imported code | **MITIGATED** | Manual discipline — possible to forget |
| 12 | `.celery*.pid` stale PID file | S1158 | Make celery refuses to start with stale PID file | `rm -f .celery*.pid; make celery` | **DOCUMENTED** | Local-dev only |
| 13 | PA worker "consume-1-then-hang" disk pressure | S1158 | Single-digit GiB free or swap <2 GiB → task I/O blocks | Memory: check `df -h` BEFORE deeper debug | **DOCUMENTED** | Local-dev only |
| 14 | Placeholder-stall pattern | S1226, S1241 | Rigby/agent writes 4-part scaffold + marks completed | Verifier-loop workflow rule (Claude directs → Rigby executes → Claude verifies) | **WORKFLOW MITIGATION** | Workflow discipline, not code fix |
| 15 | Noise-task drift 305→92 PeriodicTasks | (multi-session arc) | Accreted prototype beats; no gating function | S1157 PR #2243 canonical add_critical_celery_tasks; S1222 P6 audit | **CLOSED** | Risk of accretion recurring unless gating preserved |
| 16 | Duplicate Agent rows (canonical-name bypass) | S1226, S1263 | deliverable_factory bypassed canonicalize_agent_name(); seed scripts wrote aliases | S1263 PR #2754: migration 0374 + canonicalization gate | **CLOSED** | Pattern recurs anywhere a non-canonical name is written |
| 17 | Zombie agent threads + httpx per-chunk loophole | S1219-1221 | `read=90s` httpx timeout is per-chunk, NOT total-request; reasoning models stream slowly | PR #2519 (Tier 1: total-request bound) + #2520 (Tier 2: LLMCallEvent cleanup watchdog 10min STARTED→FAILED) | **CLOSED** | Multi-layer defense; per-worker zombie cap monitored |
| 18 | Heartbeat thread write stomp | S1084 | Full-instance `execution_record.save()` overwrote `last_heartbeat_at` from concurrent atomic update | PR #1892: `save(update_fields=[...])` excluding heartbeat field; 30s first-tick interval | **CLOSED** | Pattern recurs anywhere full-instance save races with atomic field updates |
| 19 | OpenAI/Anthropic client timeout drift | S1084 | 99% of OpenAI sites had no explicit timeout (600s default) → CLOSE_WAIT hangs to 30 min | New factory pattern with enforced timeout invariants; 58 call sites migrated Tier 1 | **CLOSED Tier 1** | Tier 2 (views + mgmt) deferred |
| 20 | PA acks queue depth transient noise | S1164 | Single-snapshot binary trigger fired on 0→1→0 churn | PR #2291/#2292 sustain-window for binary triggers + time-adjacency check | **CLOSED** | Pattern reusable for any binary alert |
| 21 | Authority enforcement vs observation | S1264 | JobContract.authority keys are policy strings not runtime symbols → preflight violation detection impossible without symbol mapping | Warn-mode shipped; enforce-mode deferred until symbol mapping work | **WARN-MODE SHIPPED** | Enforcement not present; cross-employee dispatch lacks authority block |
| 22 | GPT-5 reasoning model max_completion_tokens floor | S1224 | 800-token budget left 0 visible output after 1500-2000 reasoning tokens; finish_reason='length' | 11 sites bumped to 4000; memory rule `feedback_gpt5_max_completion_tokens_floor.md` | **CLOSED** | Any new GPT-5 caller must respect the floor |
| 23 | Followup loop re-fire (pre-S1175) | (pre-S1175 design) | AgentFollowupSubscription could fire twice on the same event | Atomic `state='armed'` filter in queryset update guarantees rowcount=1 | **CLOSED BY DESIGN** | Pattern correct; relies on DB-layer guarantee |
| 24 | Template leak in Deliverables (RESEARCH agent) | S1224 | `title=f"Research: {task[:100]}"` leaked BINDING DIRECTIVE prompt prefix | PR #2539 Gate 4 (template-token title block); Gate 5 (zero-source-research block) | **CLOSED** | Upstream sanitization deferred; gates catch it |
| 25 | Outreach contact-field schema drift | S1224 | RemoteOK spider stores at metadata.url/company; generator looked for metadata.contact_email | PR #2541 fan-out accepts both schemas | **CLOSED** | Schema federation pattern at gates |
| 26 | Cross-fleet caller verification gap | S1245-1246 | Local-DB-only verdict on Celery deletes can miss prod-only callers in sibling fleet apps | Pre-deletion 3-axis sweep (cross-repo grep + Rigby ops_tool history + FleetServiceKey/Artifact query) | **DOCUMENTED** | Multi-repo discipline; depends on operator following the procedure |
| 27 | Anthropic factory required for all clients | (multi-session) | Bare `Anthropic()` defaults to 600s timeout | Factory `get_anthropic_client()` with enforced httpx.Timeout | **CLOSED** | Any new caller must use factory; documented |
| 28 | EventBus stream count drift (audit vs runtime) | S1268 | Substrate audit cited 6 streams; runtime is 8 | Flagged in this doc §12 for cleanup | **DOC DRIFT** | Audit / inventory doc reconciliation |
| 29 | MissionRunner protocol invariant change (verdict event is conditional, not guaranteed) | S1267 | `auto_emit_verdict=False` opt-out introduced for Bug Triage v0; runner skips `verdict_issued` OpsRunEvent + `emit_mission_verdict()` when flag is False | Live in production for 1 of 4 employees; verdict written later by PA tool. Rigby S1268 SIGN-with-edits flagged that prior doc framing missed this | **PROTOCOL INVARIANT CHANGE** | Any consumer that assumed every MissionRunner terminal emits a verdict_issued event (e.g., consumers indexing by label) needs an OR-clause for status-only terminals |

**Pattern themes:**

- Silent failures dominate (#1, #2, #4, #5, #7, #8, #16, #18, #28).
  Pattern: anywhere a fallback / default / silent guard exists,
  collaboration eventually breaks invisibly.
- Multi-layer defense required (#10, #17, #19). Pattern: HTTP
  client timeouts, watchdogs, beat cleanup tasks, application-
  level retry budgets — each layer alone is insufficient.
- Schema/contract drift between layers (#5, #6, #16, #25, #28).
  Pattern: anywhere two layers disagree on a key name, type, or
  count, work disappears.

---

## 8. Reuse Classification

Each primitive from §2 classified into exactly one bucket.
Justifications cite §2 row evidence.

### SAFE TO REUSE (33)

`AGENT_MAP` (row 1), `AgentRouter.route()` sync + async (rows 2-3),
`AgentExecution` lineage (row 4), Heartbeat daemon (row 6),
`ToolCallRecord` (row 7), `LLMCallEvent` (row 8),
`CeleryTaskEvent` (row 9), `MeetingCoordinatorAgent` parallel
pattern (row 14), Celery `chain` (row 15), Celery `group` (row
16), `AIEmployee`/`JobContract` (row 18), `MissionRunner` (row
19), `MissionRunnerConfig` (row 20), `OpsRun(domain='mission')`
(row 21), `OpsRunEvent` (row 22), `emit_mission_verdict()` (row
23), `post_shift_report()` (row 24), `_persist_to_summary()`
(row 25), Atomic followup-fire (row 28), `schedule_followup`
wakeup TTL (row 29), EventBus `claim_stale()` (row 32),
`Deliverable`+`DeliverableEvent` (row 33), Beat sync command
(row 34), `check_retry_budget` (row 35), `MessageThread`
trifecta (row 36), `HumanAttentionItem` (row 38), HAI lifecycle
service (row 39), `HumanFeedbackRecord` (row 40),
`OrchestrationApprovalGate` (row 42), Diagnostic signal pattern
(row 45), `SituationTrigger` + `TriggerEvent` (row 46),
`SignalCluster` + entity-token clustering (row 48),
`ContentScoringService` (row 49), `governance_tool` PA tool
(row 54), `GovernanceState` + `KillSwitch` (rows 55-56),
inbox/`_broadcast_new_message` (rows 58-59), Anthropic+OpenAI
factories (row 62), LLMCallEvent cleanup watchdog (row 63),
`BaseAgent._call_openai` total-request bound (row 64).

**Rationale (collective).** Each row has a production caller and
emits one or more audit-trail rows that `evidence_for_mission()`
or similar can join. Reuse is preferred per
`EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1.

### REUSE WITH WRAPPER (10)

- **`BaseAgent.delegate_to_agent()` (row 5)** — depth=3 cap is
  sound but same-agent recursion (A→A) not explicitly checked;
  inter-employee dispatch should add same-employee guard at
  wrapper boundary.
- **`DecisionEnforcerAgent` pattern (row 12)** — useful "prevent
  further-analysis loops" pattern; only callable today as part of
  ConversationOrchestrator. Re-expose as a callable mixin for
  inter-employee decision flows.
- **`WorkflowOrchestrationAgent` (row 13)** — result key drift
  footgun (S1234 PR #2609). Wrapper that enforces result schema +
  asserts on missing keys avoids the silent-empty-default class.
- **Authority observation (row 26)** — warn-mode only; cross-
  employee scope confirmed but enforcement absent. Wrapper that
  surfaces violations as observability without blocking is the
  safe shape until enforcement lands.
- **`AgentFollowupSubscription` (row 27)** — silent banner
  suppression on `auto_followup=False`. Wrapper that always arms
  unless the employee explicitly opts out at the employee level
  (not per-call) avoids the S1184 class.
- **`EventBus` (rows 30-31)** — Redis Streams is the right
  substrate for high-frequency notifications but **not** for
  audit-grade receipts (use AgentExecution + OpsRunEvent for
  receipts). Wrapper documents the "EventBus = telemetry; ORM =
  receipt" distinction.
- **`HumanPreference` (row 41)** — learned fields are read-only
  outside lifecycle service. Inter-employee dispatch needing
  preference-aware routing requires a read-only wrapper.
- **`Initiative` 5-stage pipeline (rows 43-44)** — durable state
  machine could host employee-delegated multi-stage work, but
  current callers assume founder-intent + semantic-drift gates.
  Wrapper that exposes a sub-state-machine for employee jobs
  without inheriting all gates is the reusable shape.
- **`WorkspaceTrigger` (row 47)** — conductor loop location
  UNKNOWN. Wrapper or location-discovery is required before
  inter-employee reuse.
- **`AutoTopic` (row 50)** — daily rate-limit of 10 caps reuse
  surface; downstream Initiative creation UNCERTAIN. Wrapper that
  documents the upstream flow + caps inter-employee usage is the
  defensive shape.
- **`/ws/system-events/` (row 60)** — does not carry DM-arrived
  event today; if inter-employee work needs real-time push,
  wrapper extending the consumer to add an event type is required
  (frontend ticket, not protocol PR).
- **`RIGBY_EVENT_INTAKE_ENABLED` (row 61)** — default OFF, dry-
  run for now (S1250 PR 5). Inter-employee work that triggers
  Rigby intake should respect the flag; wrapper handles
  enabled/disabled cases symmetrically.
- **`BodyCoordinator` (row 57)** — emits events that trigger
  remediation; inter-employee work could subscribe but must
  treat body events as observability, not authority. Wrapper
  documents the "monitor, don't react autonomously" boundary.

### DO NOT REUSE (4)

- **`ConversationOrchestrator` (rows 10-11)** — built for in-
  conversation multi-agent debate; wrong shape for inter-employee
  durable delegation. Use MissionRunner step loops instead.
- **`messaging_tool.send_message` (row 37)** — OFF by design
  (`MESSAGING_SEND_DISABLED`). Free-form LLM outbound is the
  wrong tool for structured inter-employee messages. Use
  `post_shift_report()`-style bounded helpers
  (per S1268 protocol sketch).
- **`AdvisorContextBuilder` as callable (row 52)** — advisors are
  PROMPT CONTEXT, not callable. No invocation primitive, no
  attribution. Reusing them as "employee → advisor" handoffs
  requires substantial architectural extension out of scope for
  Employee OS v0.
- **Substrate audit's "EventBus = 6 streams" claim** — wrong;
  runtime is 8. Reuse the runtime evidence not the prior audit
  text.

### DEPRECATED (1)

- **`boardroom_tool` / `human_decisions_tool` (aliases)** — both
  superseded by `governance_tool` (`pa_tool_schemas.py:3160`
  notes "Replaces boardroom_tool and human_decisions_tool").
  Old aliases redirect via `REMOVED_TOOL_ALIASES`
  (`tool_dispatcher.py:210-229`).

### UNKNOWN (5)

- **Celery `chord` (row 17)** — no production callers found.
  Whether it would work for fan-out + callback in inter-employee
  context is untested.
- **`ProactiveIntelligenceService` (row 51)** — framework exists;
  beat-schedule and PA-entrypoint integration UNCONFIRMED. Cannot
  classify as SAFE without runtime verification.
- **`WorkspaceTrigger` conductor loop (row 47 follow-up)** —
  `workspace_autopilot_tick` referenced but task location
  UNKNOWN. Cannot classify the conductor as SAFE until found.
- **AutoTopic → Initiative auto-creation (between rows 50 and
  43)** — `auto_topic` FK exists on Initiative but the task that
  creates Initiatives from AutoTopics is not traced. Cannot
  classify as SAFE.
- **`LLMAdvisor` class (advisors/llm_advisor_system.py:49)** —
  class exists; integration into AGENT_MAP and dispatcher
  pathways UNCLEAR. Cannot recommend reuse.

---

## 9. Anti-Duplication Analysis

Per `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1, the explicit
"do NOT build" matrix has 23 rows. This research mission
revisits each with the broader collaboration lens.

### Which existing infrastructure should be reused?

**Direct one-to-one mappings for Employee → Employee delegation:**

| If you need… | Reuse | NOT |
|---|---|---|
| Mission identity | `OpsRun(domain='mission')` | `EmployeeMission` table |
| Step + verdict timeline | `OpsRunEvent` | `EmployeeAuditLog` |
| Verdict emission | `emit_mission_verdict()` | `EmployeeVerdict` table |
| Trust score | Derive on-read from `OpsRun.summary.verdict` counts (`derive_status` at `status.py:53-251`) | `TrustScore` persisted |
| Comms primitive (per-employee, per-job) | `post_shift_report()` | `EmployeeShiftReport` model |
| Comms primitive (inter-employee notice) | Thin new wrapper mirroring `post_shift_report` (per S1268 protocol sketch) | `EmployeeMessage` / `InterEmployeeNotice` model |
| Multi-step durable orchestration | MissionRunner step loop OR Celery `chain` (depending on durability needs) | `EmployeeWorkflow` engine |
| Parallel sub-tasks | Celery `group` OR `ThreadPoolExecutor` (per MeetingCoordinatorAgent) | `EmployeeParallelDispatcher` |
| Wakeup / scheduled re-run | `AgentFollowupSubscription` (event-driven) OR beat schedule (cron) | `EmployeeWakeupQueue` |
| Receipts / dispatch evidence | `AgentExecution` row at task entry + `ToolCallRecord` + `CeleryTaskEvent` | `EmployeeReceipt` table |
| Decision-needs-human | `HumanAttentionItem` + `OrchestrationApprovalGate` | `EmployeeDecisionGate` |
| Decision learning loop | `HumanFeedbackRecord` (with `fed_to_ml` flag) | `EmployeeFeedbackProcessor` |
| Authority observation | Existing `authority_contract_observed` event (warn-mode) | `AuthorityViolation` table |
| Autonomy control | `GovernanceState` (mode + scope) + `KillSwitch` (emergency) | `EmployeeKillSwitch` |
| State machine for multi-stage work | Initiative pipeline OR new sub-state on `OpsRun.summary` | `EmployeeWorkflowState` |
| Pub/sub event notifications | EventBus (Redis Streams) with consumer groups | `EmployeeEventBus` |
| Inbox surfacing | `MessageThread` + `DirectMessage` + `ThreadParticipant` | `EmployeeInbox` |

### Which infrastructure should never be rebuilt?

The 23-row anti-duplication matrix in `EMPLOYEE_OS_PRIMITIVES.md`
§2 names every "do not build" instinct already burned by prior
session pain. The most important for collaboration:

1. `EmployeeMessage` / `EmployeeNotification` (DM + HAI cover it).
2. `EmployeeAuditLog` (4 audit surfaces already exist: OpsRunEvent
   + DeliverableEvent + LLMCallEvent + ToolCallRecord).
3. `TrustScore` persisted (derive on read).
4. `MissionRun` model (use `OpsRun(domain='mission')`).
5. `ShiftReport` model (use DirectMessage with bounded metadata).
6. `EmployeeKillSwitch` (use GovernanceState mode='freeze' +
   KillSwitch).
7. `EmployeeJob` admin UI (frozen JobContract dataclass — PR-
   reviewable, git-versioned).
8. `<Anything>_tool` per employee (single `employee_tool` with
   employee param).

### Which abstractions already exist?

Identified collaboration-relevant abstractions:

- **Orchestration lifecycle:** `MissionRunner` lifecycle hook
  pattern (preflight / postflight / step / verdict / escalation /
  shift_report / pa_post) — generalizable to any multi-step
  pattern.
- **Idempotency + dedupe:** Daily idempotency (calendar-date
  scope) + 24h dedupe window (error_signature) — generalizable to
  any periodic mission.
- **Audit chain:** AgentExecution lineage (trace_id +
  parent_execution_id + root_execution_id) + ToolCallRecord
  trace_id + LLMCallEvent execution_id — composable.
- **State machine pattern:** Initiative 5-stage with
  `update_fields` recursion guard in signals — usable as template
  for any multi-stage durable work.
- **Atomic-update re-entrancy guard:** AgentFollowupSubscription
  queryset `.update(state='fired')` filtered on `state='armed'`
  — pattern usable for any "exactly once" event handler.
- **Observability vs. enforcement:** S1264 warn-mode pattern —
  emit shape evidence without blocking; usable as default for any
  new observation primitive.

### Where would adding a new model violate EMPLOYEE_OS_PRIMITIVES.md?

Concrete examples:

- New `EmployeeRecipient` / `EmployeeAddress` table — violates §2
  row "EmployeeJob admin UI." Employee identity lives in
  `core/employees/jobs.py:74-92`.
- New `MessageType` enum table — violates §2 row "EmployeeMessage."
  Use `DirectMessage.metadata.thread_kind` discriminator.
- New `EmployeeWakeup` queue model — violates the spirit of §2.
  Use `AgentFollowupSubscription` or Celery beat.
- New `EmployeeAuthorityViolation` table — even for enforcement
  someday, OpsRunEvent label is the right shape (e.g.,
  `authority_violation_observed` with detail JSON).

### What duplication risks currently exist?

Three risks visible today:

1. **Two durable orchestration paths (Finding F2).** Celery
   `chain` (used by HybridAgentExecutor) vs. MissionRunner step
   loop (used by Employee OS). They don't compose; a future
   employee that needs to chain Celery tasks would need to choose.
2. **Aspirational vs. implemented systems.** AutoTopic →
   Initiative auto-creation (UNCERTAIN), Workspace conductor loop
   (UNKNOWN location), ProactiveIntelligence wiring (UNCONFIRMED),
   LLMAdvisor (UNCLEAR) — each has a chunk of code but no clear
   production path. A new "employee → autonomy" connection
   shouldn't depend on any of these without runtime verification.
3. **EventBus is correct for events; wrong for receipts.** Some
   future contributor may treat Redis Streams as an audit trail.
   That's wrong — DLQ exists but rotation + consumer-group offsets
   are not guaranteed for replay. AgentExecution + OpsRunEvent is
   the receipt audit; EventBus is high-frequency telemetry.

---

## 10. Open Questions

Genuine unknowns — not invented answers.

1. **Where is `workspace_autopilot_tick` defined?** It is
   referenced by `trigger_signals.py:266` but not located in
   `core/tasks.py`. Mission completeness depends on knowing if
   WorkspaceTrigger is wired or dormant.

2. **Where does AutoTopic → Initiative creation happen?** The
   `auto_topic` FK exists on Initiative
   (`models_document_registry.py:165-172`), but no creation task
   is traced. Is it manual? Event-driven? Aspirational?

3. **Is `ProactiveIntelligenceService` actively running in
   production?** Class exists with 19 situations
   (`proactive_intelligence.py:12-19`); beat-schedule wiring +
   PA-entrypoint integration UNCONFIRMED.

4. **Is `LLMAdvisor` integrated into agent dispatch?** Class
   exists (`advisors/llm_advisor_system.py:49`); no callers found
   in AGENT_MAP or routing pathways. Is it dead code or
   pre-integration?

5. **What is the Redis broker persistence configuration in
   production?** §5.6 says "depends on infra config." Without
   knowing whether Redis AOF/RDB is enabled, EventBus + Celery
   broker durability claims are untestable.

6. **What does `OrchestrationApprovalGate.auto_approve` do
   today?** Status is one of (pending/approved/rejected/modified/
   auto_approved/expired). Auto-approve config exists but the
   actual auto-approve trigger logic is not traced in this audit.

7. **Does `BodyCoordinator` trigger any cross-employee
   collaboration?** Body system events fire handlers
   (`body_coordinator.py:131-181`); the handlers exist
   (`self.handlers` dict of 28 entries) but their actual remediation
   actions are not visible in the 300-line read limit.

8. **What's the durable contract on `RIGBY_EVENT_INTAKE_ENABLED`?**
   Default OFF, dry_run=True per S1250 PR 5. Is the eventual
   intended state ON-with-real-actions? Or is the dry_run mode the
   permanent v0?

9. **Where do `inter_employee_notice_emitted` OpsRunEvent labels
   end up in the audit log surfaces?** This is the S1268 proposed
   label; `evidence_for_mission()` extension was scoped in the
   protocol sketch but the read-side surfacing in the inbox UI is
   a frontend ticket not yet scoped.

10. **What is the upstream story for `EventBus` event publishing
    today?** Eight streams exist; publishers identified for
    SPIDER_DATA, OPPORTUNITY_*, VALIDATION_*, OUTCOME_RECORDED,
    MODEL_TRAINED, SYSTEM_ALERT. Which are actively publishing in
    production vs. wired-but-quiet?

11. **How would `JobContract.authority` symbol mapping land?** The
    audit confirms warn-mode is observation-only; enforcement
    requires mapping authority strings to runtime symbols (tool
    names, FK methods, etc.). What's the proposed mapping
    architecture? Out of scope here.

12. **(Rigby S1268 architectural-blind-spot note.)** When the two
    orthogonal durable orchestration paths (Celery `chain`/`group`
    in `hybrid_executor.py` vs. MissionRunner step loop in
    `mission_runner.py`) eventually need to be bridged, **what is
    the canonical idempotency key across substrates?** Today
    MissionRunner uses calendar-date scope; Celery uses task_id;
    EventBus uses event_id + consumer_group; AgentExecution uses
    UUID. None compose. Any future bridge primitive needs an
    answer to "if the same logical work tries to enter both
    substrates, which is authoritative?" Out of scope for this
    audit but flagged as a deferred design dependency.

---

## 11. Recommendations

The S1268 mission spec asks for the next research direction, not
implementation. Based on this audit's evidence:

### Recommended next research mission: **Governance + Authority Evolution**

Specifically: scope the work that would have to happen for
`JobContract.authority` to move from S1264 warn-mode observation
to actual enforcement, including:

1. **Symbol mapping audit.** Today
   `authority['recommend_remediations']` is a policy string. For
   enforcement, it would need to map to a callable signature, a
   tool name, or a model method. What's the registry that holds
   the mapping? Who maintains it? How does drift between policy
   strings and runtime symbols get detected?
2. **Trust-propagation primitives.** When Employee A's mission
   trusts Employee B's verdict (e.g., Chief of Staff trusts Bug
   Triage's "critical" severity classification), what's the
   trust contract? Today `derive_status()` computes trust per-
   employee from verdict counts (`status.py:53-251`); inter-
   employee trust is not a primitive.
3. **Authority preflight evidence layer.** S1264 emits shape
   observability; what would "preflight violation evidence"
   look like in terms of OpsRunEvent labels +
   `evidence_for_mission()` surfaces?
4. **Boundary cases:** What happens when a mission's authority
   contract changes mid-run (e.g., Chris flips Auditor from
   RECOMMEND to EXECUTE on a category)? Does the mission re-
   read the contract? Honor the old? Both? Today UNKNOWN.

This research direction is preferred over the alternatives
because:

- **Mission delegation** depends on authority semantics —
  delegating without enforcement is the same as trust-by-
  default, which is what warn-mode already does.
- **Organization hierarchy** is premature — only 4 employees
  exist; no hierarchy beyond `manager='chris'` is in any
  contract.
- **Collaboration protocol evolution** is partially covered by
  the S1268 protocol sketch already; the next step there is
  Chris's gate on whether to greenlight the v0 PR, not more
  research.
- **Employee memory** would be a sub-question under trust-
  propagation (do employees remember each other's past verdicts
  in their reasoning?).
- **Human oversight** is well-covered by HAI + governance_tool
  + Initiative gates; the gap is *machine-to-machine* trust,
  not machine-to-human.

### What this audit does NOT recommend

- Implementing inter-employee delegation. Wait for the protocol
  sketch's open questions to close.
- Adding any model. Per §9, the existing primitives cover all
  near-term needs.
- Activating `messaging_tool.send_message`. Per substrate audit
  §10 row, the gate stays off.
- Building a new "Boardroom debate" engine. Per §1 Finding F3,
  the Boardroom isn't a debate engine and inventing one would be
  premature.

---

## 12. Appendix — Cross-Reference and Documentation Drift

### Cross-reference matrix

| Prior research | Relationship to this doc |
|---|---|
| `docs/EMPLOYEE_OS_PRIMITIVES.md` | This doc's §2 inventory expands the §1 canonical primitives table by 39 new rows covering platform-wide collaboration substrates beyond Employee OS proper. §9 anti-duplication mirrors EMPLOYEE_OS_PRIMITIVES §2 + §4.1 explicitly. |
| `docs/research/employee_os_communication_substrate_audit.md` | This doc's §2 row 30 corrects the substrate audit's "6 EventBus streams" to runtime "8 streams" (§12 drift call below). Other rows reuse the substrate audit's findings without contradiction. |
| `docs/research/employee_os_communication_protocol_sketch.md` | This doc's §10 question Q9 ties to the protocol sketch's `inter_employee_notice_emitted` OpsRunEvent label. §11 explicitly defers implementation while protocol sketch awaits Chris's gate. |

### Documentation drift surfaced

| Item | Source A says | Source B (runtime) says | Resolution |
|---|---|---|---|
| EventBus stream count | substrate audit § 2 says "6 named streams" | `core/services/event_bus.py:21-30` declares **8 streams** (SPIDER_DATA, OPPORTUNITY_CREATED, OPPORTUNITY_SCORED, VALIDATION_REQUIRED, VALIDATION_DECIDED, OUTCOME_RECORDED, MODEL_TRAINED, SYSTEM_ALERT) | Inventory wins per `DOC_LIFECYCLE.md` §2c. Substrate audit needs editing; flagged for S1268 doc cleanup. |
| Employee count | CLAUDE.md "Detailed Breakdown" row says 3 | `core/employees/jobs.py:1327` `_EMPLOYEES_BY_HANDLE` has 4 | Already flagged in substrate audit §5.6 and Rigby S1268 review. CLAUDE.md needs update; not patched here per research-only constraint. |

### Existing research overlap

- Substrate audit §3 maps **agent-to-agent communication**; this
  doc's §3.1-§3.4 extend with parallel-dispatch + Celery fan-out
  + Workflow envelope drift.
- Substrate audit §4 maps **PA chat flow**; this doc references
  it without duplication.
- Substrate audit §5 maps **Employee OS communication surfaces**;
  this doc's §3.9 extends with the full MissionRunner flow
  diagram and the four current employees' cadences.
- Substrate audit §7 maps **failure modes**; this doc's §7
  extends from 12 incidents to **28**, with 12 new collaboration-
  specific incidents not in the prior audit.

### Missing documentation

- **`workspace_autopilot_tick` location.** Referenced; not
  documented; not found in `core/tasks.py` grep.
- **AutoTopic → Initiative flow.** Referenced in models; no
  documented production path.
- **`ProactiveIntelligenceService` integration.** Class exists;
  no docs on production wiring.
- **Body system handlers' remediation actions.** Mentioned at
  high level in CLAUDE.md and inventory; concrete actions not
  documented.
- **Redis broker persistence configuration.** Affects EventBus +
  Celery durability claims; no infra-config doc visible from this
  audit's scope.

---

## Specific Questions (Q1-Q8) — Explicit Answers

**Q1. How many collaboration systems already exist?**

**Eleven distinct substrates** (§1 listed; §2 inventory has 64
rows). The eleven are: AgentRouter, BaseAgent delegation,
ConversationOrchestrator, WorkflowOrchestrationAgent / parallel
ThreadPoolExecutor, Celery chain+group, MissionRunner+OpsRun,
AgentFollowupSubscription, EventBus (Redis Streams),
HumanAttentionLifecycleService, OrchestrationApprovalGate,
Initiative 5-stage pipeline. Each has a production caller.

**Q2. Which collaboration primitives are already durable?**

(Survive process restart via DB or broker persistence)

- `OpsRun` + `OpsRunEvent` (DB)
- `AgentFollowupSubscription` (DB)
- `HumanAttentionItem` (DB)
- `OrchestrationApprovalGate` (DB)
- `Initiative` + `InitiativeStage` (DB)
- `DirectMessage` + `MessageThread` (DB)
- `Deliverable` + `DeliverableEvent` (DB)
- Celery tasks in queue (broker)
- Celery `chain` + `group` (broker)
- EventBus Redis Streams (broker, if persistence configured)
- `AgentExecution` (DB) + `LLMCallEvent` (DB) +
  `ToolCallRecord` (DB) + `CeleryTaskEvent` (DB) audit chain

Non-durable: `ConversationOrchestrator` turn count,
`WorkflowOrchestrationAgent` step iteration, ThreadPoolExecutor
pools, `sys.modules` cache, in-process Heartbeat thread state.

**Q3. Which collaboration primitives already provide complete
audit trails?**

(Score 5.5-6.0 in §6 evidence-and-auditability scoring)

- MissionRunner (full timeline via OpsRunEvent +
  `evidence_for_mission()` join)
- EventBus (stream replay + DLQ)
- HAI lifecycle (status + lifecycle events + feedback)
- OrchestrationApprovalGate (state + HAI bridge + feedback)
- AgentFollowupSubscription (state transitions)
- Celery chain/group (per-task CeleryTaskEvent)
- `post_shift_report` DM (DirectMessage row + inbox surfacing)
- Spider → SignalCluster (spider_data_ids reverse-trace)
- Initiative (Initiative + InitiativeStage + InitiativeActionItem)

**Q4. Which collaboration systems already satisfy Employee OS
requirements?**

- **Mission identity + verdict + idempotency:** MissionRunner +
  OpsRun + OpsRunEvent + emit_mission_verdict (✓ in production
  for 4 employees).
- **Comms primitive (per-employee shift reports):**
  `post_shift_report()` (✓ in production for Documentation
  Manager).
- **Comms primitive (inter-employee notice):** Proposed in S1268
  protocol sketch as thin wrapper; NOT yet implemented.
- **Decision-needs-human:** HAI + OrchestrationApprovalGate (✓
  in production via 31 creator sites — Auditor NOT in that list).
- **Durable wakeup:** AgentFollowupSubscription (✓ in production
  for PA-driven dispatch).
- **Audit chain:** AgentExecution lineage + ToolCallRecord +
  LLMCallEvent + CeleryTaskEvent (✓ in production for all routed
  agents).
- **Authority observation:** S1264 warn-mode
  `authority_contract_observed` event (✓ in production for 3
  employees; Employee #4 auto-inherits).

**Q5. Which collaboration systems should never be reused?**

Per §8 DO NOT REUSE:

- `ConversationOrchestrator` for inter-employee delegation —
  wrong shape (deliberation, not delegation).
- `messaging_tool.send_message` — OFF by design.
- `AdvisorContextBuilder` as callable — context-injection
  primitive, not callable; substantial architectural extension
  needed.
- Substrate audit's "6 streams" claim — wrong; runtime is 8.

Per §8 DEPRECATED:

- `boardroom_tool` / `human_decisions_tool` PA tool aliases
  (superseded by `governance_tool`).

**Q6. Is there already enough infrastructure to build Employee-
to-Employee delegation without introducing any new models?**

**YES.** Evidence:

- Per §9 anti-duplication table: every collaboration need has
  an existing primitive (MissionRunner, AgentFollowupSubscription,
  Celery chain/group, MessageThread/DirectMessage, HAI,
  OrchestrationApprovalGate, EventBus).
- The S1268 protocol sketch (Platform Auditor → Chief of Staff)
  proposed a thin helper file
  (`core/employees/comms_inter_employee.py`) + one new
  `OpsRunEvent.label` value + one read-side extension to
  `evidence_for_mission()` — no new models.
- `EMPLOYEE_OS_PRIMITIVES.md` §2 explicitly names every "new
  model" temptation as anti-pattern. The platform has 588 models
  already.

**Q7. Which collaboration primitive appears to be the canonical
foundation for future Employee OS collaboration?**

**`MissionRunner` + `OpsRun(domain='mission')` + `OpsRunEvent`,
extended by `AgentFollowupSubscription` for durable wakeups and
`post_shift_report()`-style helpers for bounded outbound comms.**

Rationale:

- The triplet already encodes lifecycle (preflight → steps →
  postflight → verdict → escalation) and durable audit
  (OpsRunEvent timeline + idempotency contracts).
- The "subscribe-to-terminal" pattern from
  AgentFollowupSubscription generalizes naturally to "subscribe-
  to-verdict" for inter-employee handoffs.
- `post_shift_report()` is the canonical bounded-comms pattern
  and the basis of the S1268 protocol sketch.
- All three already emit `evidence_for_mission()`-joinable
  artifacts.

**Q8. If Employee-to-Employee delegation were implemented
tomorrow, what is the minimum new runtime surface required?**

**(Identifying the missing piece — not designing it.)**

The smallest missing piece is **a durable "subscribe-to-(employee,
verdict)" primitive** that:

- Fires on `verdict_issued:<v>` OpsRunEvent
- Routes to a target employee's *next mission's preflight*
  (not as a synchronous resume — the target employee may be
  scheduled for a future run)
- Carries bounded handoff metadata (mission_id, verdict,
  evidence_refs)
- Is observable (OpsRunEvent label) + audit-joinable
- Survives broker / DB / process restarts

Today's `AgentFollowupSubscription` is the closest existing
primitive, but its semantics are "fire-on-execution-terminal +
broadcast-to-conversation" (synchronous-ish, conversation-scoped).
The missing piece is the "fire-on-mission-verdict + delivery-to-
next-mission" variant.

Whether this variant should be:

- A new model (likely violates `EMPLOYEE_OS_PRIMITIVES.md` §2;
  AgentFollowupSubscription is 5 fields + 4 states — extending
  it to support mission-verdict semantics may be cheaper)
- An extension of `AgentFollowupSubscription` (adding a
  `target_mission_kind` or `target_employee_handle` field)
- A pure read-side query (Employee B's preflight queries
  unprocessed verdicts from Employee A — no new write surface)

…is the next design call, not a research call.

---

## Appendix A — Evidence integrity notes

- Five parallel Explore sub-agents produced the source material:
  - **Advisor + Boardroom** (advisors/registry.py, boardroom_ml_service.py)
  - **Scheduling + Celery orchestration** (core/celery.py:37-797, hybrid_executor.py)
  - **Spider + proactive + signal autonomy** (signal_aggregation_service.py, event_bus.py, body_coordinator.py)
  - **Decision routing + HAI + Initiative** (human_attention_lifecycle.py, models_orchestration.py, models_document_registry.py)
  - **Collaboration-specific failure history** (12 new incidents beyond substrate-audit baseline)
- Load-bearing class locations spot-verified by Claude:
  - `class AdvisorRegistry` at `advisors/registry.py:142`
  - `class BoardroomMLService` at `core/services/boardroom_ml_service.py:31`
  - `class HumanAttentionLifecycleService` at `core/services/human_attention_lifecycle.py:36`
  - `class BodyCoordinator` at `core/services/body_coordinator.py:110`
  - `class ConversationOrchestrator` at `core/conversation_orchestrator.py:270`
  - `class EventStream` (Enum, **8 entries**) at `core/services/event_bus.py:21-30`
  - `class EventBus` at `core/services/event_bus.py:90`
  - `class WorkspaceTrigger` at `core/models_skin_layer.py:798`
  - `class WorkspaceTriggerConfig` at `core/models_skin_layer.py:1075`
- Major correction surfaced and folded in: **EventBus has 8
  named streams, not 6.** Substrate audit text needs update; not
  patched in this mission per research-only constraint.
- All "today" / "is" language describes runtime state verified
  by direct file read in this audit or in the prior substrate
  audit's spot-checks; all "should" / "could" language is
  research conjecture marked as such.
- Rigby's S1268 review additions re-verified by Claude:
  - `core/employees/mission_runner.py:589` (`auto_emit_verdict: bool = True` field declaration)
  - `core/employees/mission_runner.py:1127-1145` (S1267 opt-out path comment + conditional `verdict_issued` emission)
  - `core/employees/mission_runner.py:1554+` (status-only flip path used by Bug Triage v0)
  - `core/services/event_bus.py:21-30` (8-stream Enum — independently corroborated)
  - `core/services/advisor_context_builder.py:23-35` (prompt-context shape, not call surface)
  - `core/services/boardroom_ml_service.py:31-73` (ML decision-prediction layer, not debate engine)
- Rigby's verdict on the headline findings:
  - F2 (two orthogonal durable orchestration paths) — **SIGN-clean**
  - F3 (Advisors + Boardroom misleadingly named) — **SIGN-clean**
  - F4 (no in-platform A→A reply contract) — **SIGN-clean**
  - §11 recommendation (Governance + Authority Evolution next) — **SIGN-clean**
  - EventBus 6→8 stream drift catch — **SIGN-clean, independently corroborated**
  - Reuse classifications (§8) + canonical-foundation Q7 — **SIGN-clean**
  - Architectural blind spot — Rigby surfaced "canonical
    idempotency key across the two orchestration paths when
    bridged" as the next deferred design dependency. Folded
    into §10 as Q12.
