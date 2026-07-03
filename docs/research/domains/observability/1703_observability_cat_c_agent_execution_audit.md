---
title: "S1703 Group 1700 Cat C — Agent Execution Telemetry (AgentExecution) Child Audit"
status: active (Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-03 on arc pin pa-e7fbacc996b34b44 [S1600/S1700/S1701/S1702 parent-scoping precedent: arc pin doubles as SIGN pin; fresh SIGN isolation pin pa-f1a30b7ed5bb4042 minted per playbook §15 was routed-around by tools/pa_local.sh:128 wrapper hard-code — retire owed at S1703 close per §16]; F1-F4 folds landed pre-commit; Chris ratified P3 kickoff via "Start research group 1703" short command per playbook §21 short-command intent — interpreted as S1703 child under Group 1700 per parent D72 P3 slot)
authority: child-audit for Category C per parent §5 D72 sequence + THIRD child under Group 1700; applies D48 preemptive stability-probe gate 20th arm on arc pin per playbook §15 stage-table child row
category: child_audit
session: 1703
child_slot: P3
domain_slug: observability
research_group: 1700
date: 2026-07-03
head_commit: 9612ea95
parent_scoping: 1700_observability_domain_scoping.md (§3.C Cat C lines 473-526)
sibling_prior:
  - 1701_observability_cat_a_celery_task_event_audit.md (Cat A CeleryTaskEvent; SIGN-with-edits at High confidence 2026-07-03)
  - 1702_observability_cat_b_llm_call_event_audit.md (Cat B LLMCallEvent; SIGN-with-edits at Medium-High confidence 2026-07-03)
delegates_to: []  # child audits do not delegate; xx99 resolves posture
promotes_to: 1799_observability_canonical_summary.md (D74 axis evidence contribution; F1 3-class landmine resolution; F9 correlation-primitives box execution_id + trace_id + input_data['celery_task_id'] rows)
---

# S1703 Group 1700 Cat C — AgentExecution Child Audit

> **Third child audit under Group 1700 (Observability arc).** Playbook §11.2 20-section template THIRD application under Group 1700 arc (first was S1701 Cat A CeleryTaskEvent; second was S1702 Cat B LLMCallEvent). 6-parallel-Explore sweep + parent-Claude verifier-loop applied pre-Explore and post-Explore. Rigby SIGN cycle 1 delivered SIGN-with-edits at Medium-High confidence via single-batch 4-question pattern (D48 20th arm HOLDING CLEAN); F1-F4 folds landed pre-commit.

---

## 1. Executive Summary

**Cat C (Agent Execution Telemetry) owns the AgentExecution model at `core/models_unified_system.py:882-1014` and the `AgentRouter._create_execution_record()` writer at `core/agent_router.py:2787-2960`.** Per parent §3.C boundary rule, Cat C stops at the router's `route()` post-execute hook and does NOT own tool-call telemetry (Cat D) or per-LLM-call telemetry (Cat B).

**Nine load-bearing findings drive this audit's §14/§15/§17/§19 sections and the D74 axis contribution to xx99:**

- **F1 (CRITICAL, §17) — 3-class landmine resolves as 1-alive + 2-dead at HEAD.** Parent §3.C catalogued three `class AgentExecution` bodies (`core/models_unified_system.py:882` + `intelligence/models.py:587` + `intelligence/models/agent_execution.py:11`). Verifier-loop via Django app registry (`apps.get_app_config('intelligence').get_models()`) shows **ONLY `core.AgentExecution` is registered at runtime**. Both intelligence-side class bodies are **unreachable dead code**: (a) `intelligence/models.py:587` is package-shadowed (Python resolves `intelligence.models` as the `intelligence/models/` package, not the `.py` file); (b) `intelligence/models/agent_execution.py:11` is not re-exported from `intelligence/models/__init__.py` (the __init__ only re-exports `ActionPlanExecution` from `action_plan.py`). **The intelligence-side canonical is `intelligence.ActionPlanExecution`** — renamed from `intelligence.AgentExecution` in S1243 via migration `0003_session_1243_rename_agentexecution_to_actionplanexecution.py` (RenameModel; 0 rows at rename time; docstring: "Table is empty so the rename is data-safe"). The two orphaned class bodies were left in place as source-file dead code.
- **F2 (CRITICAL, §14) — S287 deprecation notice is stale and reversed.** Docstring at `core/models_unified_system.py:882-887` says "DEPRECATED: Use agents.models.AgentExecution instead. This model is deprecated as of Session 287." Runtime reality: `agents/models.py` is a compatibility shim (per S391 comment "These models have been migrated to `core/models/agents_registry/`") and the target class was renamed to `AgentTaskExecution` per S1244 PR #2685 (commit `2d65b44f`, "rename core.AgentChannel + agents.AgentExecution — Cat 2 cross-app duplicates 9 → 0"). No `AgentExecution` class exists under `agents.models` at HEAD. **The correct override is in the same file at lines 993-1014 (S1084 audit block, commit `0d0afd1d docs(models): retire misleading AgentExecution deprecation warning`)** — "The warning was causing real confusion... `core_agentexecution` (this model) is the canonical, actively-written live table... `agents_agentexecution` (the 'new' model the warning pointed to) was EMPTY." The `.save()` deprecation warning was removed in S1084; the class docstring at :882-887 was not.
- **F3 (MEDIUM, §14, wording drift) — Parent §3.C mislocates the write path.** Parent scoping says "BaseAgent's `route()` wrapper" and asks "which class does BaseAgent's `route()` wrapper write to." Runtime reality: `BaseAgent` has NO `route()` method; it delegates via `self.agent_router.route(...)` at `core/agents/base_agent.py:948` (property accessor at :848-856 returns an `AgentRouter` instance). The canonical write path is `AgentRouter.route() → _create_execution_record()` at `core/agent_router.py:2787-2960` with the lazy import `from core.models_unified_system import Agent, AgentExecution` at `:2814` and `AgentExecution.objects.create(**_create_kwargs)` at `:2921`. §7.4 anchor-update owed by xx99.
- **F4 (CRITICAL, §14) — PA path AgentExecution coverage is ZERO.** `core/services/unified_pa_entrypoint.py` has ONE `AgentExecution` reference at line 6050 which is a **comment only** ("Session 989: AgentExecution.agent is FK — handler returns agent__name"). No imports, no writes. The PA GPT-5.2 function-calling agentic loop generates 1-20 LLM calls per user message (per S1702 F2) and dispatches tools that may invoke agents via `run_agent`, but **the PA path itself writes zero AgentExecution rows unless the invoked agent goes through `AgentRouter.route()`**. Analog to S1702 Cat B F2. This is the largest single coverage gap in Cat C's telemetry surface.
- **F5 (MEDIUM, §15) — Retention posture is stuck-cleanup, not date-based.** `core/tasks_agents.py:1554-1654` implements `cleanup_stale_agent_executions` (Session 925; 30-min beat cadence) which sweeps rows in `('running', 'in_progress')` status older than 60 min (`last_heartbeat_at` fallback to `created_at`) and marks them `status='failed'` with error message "Task timed out after {N} minutes (no heartbeat)". **This is a stuck-STARTED-row watchdog, NOT date-based retention.** No analog exists to `CELERY_TASK_EVENT_RETENTION_DAYS` (Cat A) or the sibling `cleanup_llm_call_logs` (`core/tasks.py:4408`, 30-day retention on `LLMCallLog`). AgentExecution rows accumulate unbounded post-completion. Row-count monitoring absent. `cleanup_stuck_executions` management command (`core/management/commands/cleanup_stuck_executions.py`, Session 866) is a manual-invocation utility with `--apply` + `--hours` flags; not scheduled.
- **F6 (HIGH, §17) — Cat D (ToolCallRecord) has NO `execution_id` field.** `core/models_tool_calls.py:19-131` — the model has `trace_id` (UUIDField, nullable, `db_index=True`), `conversation_id` (UUIDField, nullable, `db_index=True`), `agent_name` (CharField, `db_index=True`), `tool_name`, `parameters`, `result_summary`, `result_hash`, `full_result`, `result_size_bytes`, `success`, `error_message`, `error_type`, `latency_ms`, `task_summary`, `created_at` (Meta.indexes: 4 composite indexes). **No `execution_id` column at HEAD** (verifier-loop grep for `execution_id|ForeignKey.*AgentExecution|agent_execution_id` in this file → 0 hits). Correlation to Cat C is via `trace_id` semantic match only (both models have UUID `trace_id` indexed on the same-shaped key, but no schema-enforced FK or shared join contract). Parent §3.D F3 fold names `tool_call_id` as dedup key with Cat B; that column also does not exist. **Cross-cat correlation Cat D ↔ Cat C is loose-coupled by trace string, not FK.**
- **F7 (MEDIUM, §9 + §14) — `input_data['celery_task_id']` JSON-path is unindexed at HEAD.** `core/tasks_agents.py:2274, 2280` write `'celery_task_id': str(self.request.id)` into `AgentExecution.input_data` (JSONField). No GIN index on the JSON path (`intelligence/migrations/` + `core/migrations/*.py` grep for `GinIndex` returns 10 hits, none on `AgentExecution.input_data`). Callers relying on the 3-hop `CeleryTaskEvent.task_id → AgentExecution.input_data['celery_task_id'] → downstream` chain (S1701 §9 + S1702 F9 correlation-chain) do **JSON-path scan** at query time. Session 1701 §9 U4 candidate confirmed applicable.
- **F8 (MEDIUM, §10) — 4 `post_save` receivers on `core.AgentExecution` at HEAD.** (i) `core/signals/rigby_delegation_signals.py:131` (`sender="core.AgentExecution"` string; writes OpsRunEvent lifecycle rows: `agent_assigned` on create + `agent_completed` + `verification_started` + `verification_completed` on terminal status; gated by `settings.RIGBY_DELEGATION_ENABLED`; idempotent via `_has_event` check); (ii) `core/learning_bridges/agent_execution_bridge.py:317` (learning loop update via `AgentExecutionLearningLoop.process_event()`; fires on terminal status); (iii) `core/services/experiment_linker.py:256` (`sender=AgentExecution` import; links execution to experiment); (iv) `core/services/human_attention_bridge.py:578` (`sender='core.AgentExecution'` string; human-attention triggering). Fan-out is unmonitored — no signal-handler duration telemetry beyond LLMCallEvent+ToolCallRecord writes that may happen inside handlers.
- **F9 (D74 axis contribution, §9) — Cat C owns TWO cross-model spine primitives: `execution_id` (i.e., `AgentExecution.id`) and `trace_id`.** `execution_id` is Cat C's PK singleton; Cat B (`LLMCallEvent.execution_id` UUIDField non-FK indexed) and 6+ additional models carry it as scalar downstream reference (`OrchestrationExecution.execution_id` at `core/models_orchestration.py:270`; `OrchestrationStepExecution.execution_id` at `:626`; `SkinLayerModel.execution_id` at `core/models_skin_layer.py:930`; `UserAgentLearning.execution_id` at `core/models_user_learning.py:34`; `DeliverableAppend.execution_id` at `core/models_deliverable_appends.py:83`; plus internal self-references `parent_execution_id` + `root_execution_id`). `trace_id` is Cat C's S843 orchestration-contract field (UUIDField nullable indexed at `:906-909`), populated via `TraceAttachmentService.resolve_trace_id(context)` at `agent_router.py:2850` and written at `:2910`; also carried on `ToolCallRecord.trace_id` (`models_tool_calls.py:47-50`, indexed) and `LLMCallLog.trace_id` (S697 sibling of Cat B F1 model). **Cat C is the natural home of the D74 arc-wide spine candidate** — but coverage is per-route-path (F4 PA-path uncovered) and correlation contract is schema-loose (F6 ToolCallRecord no execution_id FK; F7 JSON-path celery_task_id unindexed).

**Coverage-completeness posture.** For dispatches that go through `AgentRouter.route()` (both direct-route and Celery-wrapped `execute_agent_task` paths), Cat C coverage is complete: `_create_execution_record()` writes STARTED (`status='in_progress'`) + heartbeat thread touches `last_heartbeat_at` every 120s (daemon spawned at `agent_router.py:3021`) + `_complete_execution()` writes terminal (`status='completed' | 'failed' | 'cancelled'`) at `:3039-3150`. For the **PA path**, Cat C coverage is **zero** (F4). For **managed agents / orchestration agents**, Cat C coverage funnels through `AgentRouter.route()` (verified: no separate write path; `WorkflowOrchestrationAgent` writes 0 AgentExecution rows directly; orchestration outcome is the parent router-created row). For **detached agent invocations** (tests, scripts, PA tools not routed through `run_agent`), Cat C coverage is zero.

**Boundary posture (§16).** Six boundary-violation candidates all classified LEGITIMATE — no cross-cat writes from `_create_execution_record()` (writes only `AgentExecution` + `Agent.get_or_create`); no direct `AgentExecution.objects.create` outside `agent_router.py:2921`, `agent_execution_wrapper.py:34` (DEAD CODE, F5.b), and `tasks_agents.py:2311+` (Celery task wrapper's own `_impl_execute_agent_task` writer path — companion to `_create_execution_record`; per S1084 audit block "both `tasks_agents._impl_execute_agent_task` and `agent_router._create_execution_record` write here"). Rigby delegation signal handler is a legitimate post_save consumer that writes cross-cat to `OpsRunEvent` (Cat E), documented under Employee OS primitives. No Cat C analog to S1219 P1 `on_agent_task_failure_bridge` cross-cat exception — that exception is Cat A → Cat C direction (celery_telemetry.py writes AgentExecution row on SoftTimeLimitExceeded per S1701 F4).

**Maturity STABLE for router-covered surface + PARTIAL overall + Risk HIGH.** Router path is coherent (heartbeat thread + lineage tracking + cancel propagation via S1098 PR #4 parent_execution_id/root_execution_id + 5-state status enum with S1098 PR #3 `cancelled` addition); 172 files import the canonical class from `core.models_unified_system`; test coverage exists (`test_cancel_ancestor_propagation.py`, `test_cancel_token_e2e.py`, `test_celery_failure_agentexecution_bridge.py`); Django admin registration ABSENT (verifier-loop grep found no `AgentExecutionAdmin` registration). PARTIAL because F4 PA-path uncovered + F5 no date-based retention + F6 Cat D correlation gap + F1/F2 landmine + stale-docstring drift combine to make Cat C **not yet a canonical arc-wide observability spine**.

**§19 R1 (HIGH) — F4 PA path coverage** and **R2 (HIGH) — F2 stale-docstring cleanup + F1 dead-code removal (3-class landmine)** are the two most consequential follow-ons owed to xx99 (S1799). Both are Cat C-scoped but downstream posture decisions (deprecation ADR + PA-path AgentExecution write contract) belong to xx99 per D73 posture-framing discipline + parent §6.3 T-slot deferral.

---

## 2. Domain Purpose

**Q1 + Q2 from §9: What is Cat C, and why does it exist?**

Cat C (Agent Execution Telemetry) is the observability layer for agent-boundary dispatch. Its purpose is to answer three questions:

1. **Who dispatched what agent to do what task?** — per-execution provenance (`id`, `agent` FK, `user` FK nullable, `task` text, `input_data` JSONField, `owner_agent` string, `experiment` FK nullable, `project` FK nullable, `trace_id` orchestration UUID, `tenant` FK nullable, `parent_object_type`/`parent_object_id`, `conversation_id` from S1174 PA-follow-up flow). One `AgentExecution` row per logical dispatch.
2. **What was the outcome?** — 5-state lifecycle (`pending → in_progress → completed | failed | cancelled`) + `output_data` JSONField + `error_message` TextField + `execution_time_ms` IntegerField + `tokens_used` IntegerField + `cost` DecimalField(8,4) + `completed_at` DateTimeField.
3. **Did the execution stay alive across long-running work?** — `last_heartbeat_at` DateTimeField (indexed; S1100 field). Router spawns a daemon thread (`agent_router.py:2963-3019`) that updates `last_heartbeat_at` every 120s so the stuck-watchdog (`cleanup_stale_agent_executions` at `tasks_agents.py:1554-1654`, 30-min cadence) can distinguish "still alive" from "truly stuck" per the S1083 pattern.

Cat C exists because before the S641 Agent Performance Dashboard scaffolding + S843 orchestration contract + S1098 PR #4 lineage, agent-level intent + outcome + duration + parent/child ancestry were operator lore, not queryable data. The `AgentRouter._create_execution_record()` helper introduced write-side ownership; downstream models (LLMCallEvent, ToolCallRecord, OrchestrationExecution, etc.) tag `execution_id` for cross-model correlation. S1098 PR #4 added `parent_execution_id` + `root_execution_id` UUIDField pair so nested-dispatch cancel + budget checks can walk the ancestry chain (`core/services/cancel_registry.py`).

**What Cat C does NOT own** (parent §3.C boundary rule):

- **Cat D (ToolCallRecord) — per-tool-call telemetry.** Tool calls made from inside an agent execution remain Cat D per parent §3.D boundary rule (S970 `BaseAgent.__init_subclass__()` auto-wrap; S1115 all-return-path fix). Cat C does not own tool-call schema.
- **Cat B (LLMCallEvent) — per-LLM-call telemetry.** LLM calls made from inside an agent execution remain Cat B per parent §3.B boundary rule (S1098 wrapper). Cat C tags `execution_id` on the wrapper metadata; Cat B stores it as nullable non-FK (S1702 F9).
- **Cat A (CeleryTaskEvent) — Celery task lifecycle.** Cat C does not read or write Cat A telemetry. Cross-cat correlation Cat C ↔ Cat A is via `AgentExecution.input_data['celery_task_id']` string scalar (F7 JSON-path unindexed) written by `tasks_agents.py:2274, 2280`. Fire-alarm reverse write from Cat A → Cat C exists per S1701 F4 (`on_agent_task_failure_bridge` at `celery_telemetry.py:240-286` marks `AgentExecution.status='failed'` on `SoftTimeLimitExceeded`).
- **Cat E (OpsRun / OpsRunEvent) — mission / ops telemetry.** MissionRunner + Ops Autopilot pipelines own the mission execution; the Rigby delegation signal handler bridges Cat C → Cat E by writing `OpsRunEvent` lifecycle rows on Cat C `post_save` (`rigby_delegation_signals.py:131-265`).
- **`AgentRouter` dispatch policy.** The router owns routing decisions, priority policy, semaphore control, timeouts, and workflow interception. Cat C is the observability trail of what the router did, not the router itself.
- **`BaseAgent` execution semantics.** BaseAgent (5962 lines per S1703 Explore 2) owns the agent-side execution shape (`execute()` / `execute_with_workspace()` methods). Cat C does not own the LLM prompt loop or the tool-invocation semantics.

---

## 3. Canonical Entry Points

**Q3: File:line for the entry points that write / read AgentExecution.**

### Writer entry points (in priority order)

| Rank | Entry point | File:Line | Semantics |
|---|---|---|---|
| 1 | `AgentRouter._create_execution_record` | `core/agent_router.py:2787-2960` | Primary writer for router-dispatched agents. Caller passes `agent_name` + `task` + `context_summary`; helper resolves `trace_id` via `TraceAttachmentService`, resolves `parent_execution_id`/`root_execution_id` from caller context, calls `AgentExecution.objects.create(**_create_kwargs)` at `:2921` with status='in_progress'. Fallback retry at `:2928` (without optional S1098 PR #4 lineage + S1100 heartbeat fields) for un-migrated envs. |
| 2 | `AgentRouter._complete_execution` | `core/agent_router.py:3039-3150` | Terminal writer. Sets `execution_record.status = 'completed' if success else 'failed'` at `:3064` + `completed_at = timezone.now()` at `:3066` + `execution_time_ms` computed from wall clock + `output_data`. Persists via `execution_record.save(update_fields=[...])` at `:3078-3081` per feedback_router_heartbeat_not_dead memory rule. |
| 3 | `AgentRouter.route` LLMCallCancelled handler | `core/agent_router.py:1795-1798` | Cancel-path terminal writer. Lazy imports AgentExecution + calls `.objects.filter(id=execution_record.id).update(status='cancelled')` — queryset update pattern (not instance save) for thread safety. |
| 4 | `AgentRouter.route` wall-clock timeout early-save | `core/agent_router.py:1677-1688` | Timeout-path terminal writer. Sets `execution_record.status='failed'` + `save(update_fields=[...])` before `_complete_execution` runs — Phase 2 fail-open. |
| 5 | `_impl_execute_agent_task` (Celery wrapper path) | `core/tasks_agents.py:1820, 2068, 2114-2320` | Companion writer to `_create_execution_record`. Per S1084 audit block (`models_unified_system.py:1006-1008`): "both `tasks_agents._impl_execute_agent_task` and `agent_router._create_execution_record` write here." Also writes `input_data['celery_task_id'] = str(self.request.id)` at `:2274, 2280`. Lazy import at `:2114` (with `noqa` marker documenting circular-import dodge). |
| 6 | Heartbeat daemon thread | `core/agent_router.py:2963-3019` (loop) + spawned at `:3021` | 120s cadence `AgentExecution.objects.filter(id=_execution_id).update(last_heartbeat_at=timezone.now())` at `:2989-2991`. Not a create; keeps existing row alive per S1083 pattern. |
| 7 | `cleanup_stale_agent_executions` beat task | `core/tasks_agents.py:1554-1654` | 30-min cadence sweeper (S925). Filters rows in `('running', 'in_progress')` older than 60-min threshold (`last_heartbeat_at` fallback to `created_at`) and `.update(status='failed', error_message='Task timed out after N minutes (no heartbeat)')`. Cross-cat exception NONE — pure Cat C write. |
| 8 | `cleanup_stuck_executions` mgmt cmd | `core/management/commands/cleanup_stuck_executions.py:66-70` | Manual utility (S866). `--apply` + `--hours N` + `--delete-cleaned` flags. Same status-flip semantics as F7 beat task but ad-hoc invocation. |

### Non-router write sites (fire-alarm cross-cat exception)

**One S1701 F4 documented exception:** `core/celery_telemetry.py:240-286` (`on_agent_task_failure_bridge`) writes `AgentExecution.status='failed'` on `SoftTimeLimitExceeded` via Cat A telemetry signal. This is the same S1219 P1 cross-cat exception that S1701 §16 catalogued from the Cat A side; from the Cat C side it appears as an inbound cross-cat write.

### Reader entry points

| Reader | File:Line | Cardinality | Purpose |
|---|---|---|---|
| PA `_get_agent_execution_output` handler | `core/services/td_handlers_agents.py:163-294` | Direct UUID + `input_data__celery_task_id` fallback (per S1703 Explore 3) | Enrichment tool; surfaces `agent__name`, `execution_id`, `output_data`, metadata, media URLs. Not a first-class PA `execution_history_tool` (F4 gap). |
| PA `schedule_followup` handler | `core/services/td_handlers_agents.py:5133-5246` | Resolves execution via `execution_id` or `task_id`; creates `AgentFollowupSubscription` row | S1174 PR-2a follow-up wake path. Reads AgentExecution + writes subscription row. |
| REST `execution_detail` view | `core/views_agent_execution.py:466` | Direct UUID | GET `/api/v1/agents/execution/<execution_id>/` — returns full execution record. |
| REST `cancel_agent_execution` view | `core/views_agent_execution.py:945` | Direct UUID | POST `/api/v1/agents/execution/<execution_id>/cancel/` — writes cancel signal via CancelTokenRegistry (not direct row mutation). |
| REST `get_agent_execution_cancel_state` view | `core/views_agent_execution.py:1033` | Direct UUID | GET `/api/v1/agents/execution/<execution_id>/cancel-state/` — reads CancelTokenRegistry state. |
| Analytics view surfaces | `core/views_analytics.py` + `core/views_analytics_real.py` + `core/views_agent_analytics.py` + `core/views_agent_dashboard.py` + `core/views_agent_learning.py` | 9+ filter/count/aggregate sites | Dashboard aggregations (per-agent throughput, error rate, latency percentiles). |
| Trace viewer | `core/views_trace_viewer.py:61` | `AgentExecution.objects.filter(trace_id=trace_id)` | S843 trace-based drill-down. |
| WebSocket `AgentExecutionConsumer` | `core/consumers_agents.py:87-230` | `subscribe_to_execution` + `get_execution_logs` + `cancel_execution` | Real-time subscription via `execution_{execution_id}` channel group. |
| `post_save` signal receivers (4) | See §10 Event Flows | Full instance passed | See F8. |
| Learning bridges | `core/learning_bridges/agent_execution_bridge.py:317` | Instance | S1115 learning-loop update on terminal status. |
| Rigby delegation signal handler | `core/signals/rigby_delegation_signals.py:102-259` | Reads `execution.id` + counts `LLMCallEvent.objects.filter(execution_id=execution.id, status="SUCCESS")` at `:102-104` | Writes `OpsRunEvent` lifecycle rows to bridge Cat C → Cat E. |
| Discord bot | `core/services/discord_bot.py` (per S1206 comment; ~1240) | `AgentExecution.objects.filter(user=web_user).count()` + reads `execution_time_ms` | Per-user execution counts + Discord embed footer. |
| Test fixtures | `tests/services/test_celery_failure_agentexecution_bridge.py` + `core/tests/test_cancel_*.py` + `core/tests/test_execution_history_reverse_link.py` + `core/tests/test_claude_code_task_receipts_s1262.py` | Test-scoped | Not production consumers. |

### Reader gap (§18 candidate)

**No dedicated PA `execution_history_tool` reads AgentExecution directly.** `_get_agent_execution_output` is an enrichment helper (called from other handlers), not a first-class Rigby query surface with pagination + filtering. Compared to Cat A (`task_breakdown_tool` per S1701 §11) and Cat B (`cost_telemetry_tool` per S1702 F1 — even though it reads LLMCallLog not LLMCallEvent), Cat C has **no first-class PA read surface**. This is F4-adjacent: Rigby cannot introspect agent execution history without going through analytics REST views + trace_viewer. §19 R4 candidate.

**No Django admin registration.** Verifier-loop grep for `AgentExecutionAdmin` returned 0 hits. Cat C rows are not readable in `/admin/`. Cross-cat comparison: Cat A + Cat B have no admin either (S1701 + S1702 pattern); Cat C matches. Not a drift, but a consistent doc-gap: no `/admin/` read surface for any of the observability-arc telemetry.

### Retention entry point

`cleanup_stale_agent_executions` (F7 above) is a **stuck-watchdog, not retention** — it status-flips rows past a heartbeat-staleness threshold. `cleanup_stuck_executions` mgmt cmd (F8 above) has an optional `--delete-cleaned` flag but is manually invoked. **No scheduled date-based retention exists** (F5 debt).

Sibling models compared: Cat A has 30-day retention via `CELERY_TASK_EVENT_RETENTION_DAYS`; Cat B's F1 sibling `LLMCallLog` has 30-day retention via `cleanup_llm_call_logs` (`core/tasks.py:4408`); Cat C has neither. Cat C rows accumulate unbounded post-completion.

---

## 4. Major Models

**Q4 + Q5 + Q6 + Q7: Models owned, FK graph, retention, overlaps.**

### `AgentExecution` — `core/models_unified_system.py:882-1014`

Introduced **Session 0006** (migration `core/migrations/0006_advisor_agent_agentcategory_spiderdata_and_more.py:252-306`). Extended across S642, S841, S843, S1039, S1084, S1098 PR #3 + PR #4, S1100, S1174 PR-1.

**Full field inventory (23 persistent fields + PK; NOT counting inherited Model fields):**

| Field | Line | Type | Nullability | Index | Default | Purpose |
|---|---|---|---|---|---|---|
| `id` | :891 | UUIDField (PK, editable=False) | N | PK | `uuid.uuid4` | Primary key (per-execution singleton). |
| `agent` | :892 | ForeignKey(Agent, on_delete=CASCADE, related_name='executions') | N | Y (FK) | — | Owning agent record (Session 0006). |
| `user` | :894 | ForeignKey(AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True) | Y | Y (FK) | NULL | Nullable since S642 to allow Celery task executions without user context. |
| `experiment` | :896-903 | ForeignKey(core.Experiment, on_delete=SET_NULL, related_name='agent_executions') | Y | Y (FK) | NULL | S841: Experiment scoping for error-rate metrics. |
| `trace_id` | :906-909 | UUIDField, db_index=True | Y | Y | NULL | **S843: orchestration contract field.** Populated by `TraceAttachmentService.resolve_trace_id(context)` at `agent_router.py:2850`. |
| `project` | :910-915 | ForeignKey(core.PartnershipProject, on_delete=SET_NULL, related_name='agent_executions') | Y | Y (FK) | NULL | S843: project this execution belongs to. |
| `parent_object_type` | :916-919 | CharField(50) | Y (blank='') | N | `''` | S843: kind of parent that triggered (conversation, orchestration, gate). |
| `parent_object_id` | :920-923 | UUIDField, db_index=True | Y | Y | NULL | S843: ID of parent that triggered this execution. |
| `owner_agent` | :924-927 | CharField(100), db_index=True | Y (blank='') | Y | `''` | S843: agent name that owns/created this execution (denormalized string). |
| `task` | :929 | TextField | N | N | — | Task description (truncated to 500 chars at write time per `agent_router.py:2905`). |
| `status` | :930-938 | CharField(20, choices=STATUS_CHOICES) | N | N (no db_index on the field itself; §9 no composite index either) | `'pending'` | **5-state enum:** `pending`, `in_progress`, `completed`, `failed`, `cancelled` (S1098 PR #3 added `cancelled`). |
| `input_data` | :941 | JSONField | N (default=dict) | N | `{}` | Router writes `{'task': task, 'context_injected': context_summary, 'context': raw_ctx}` at `:2832-2837`. Celery wrapper writes `{'celery_task_id': str(self.request.id), ...}` at `tasks_agents.py:2274, 2280`. **F7 debt: no GIN index on JSON paths.** |
| `output_data` | :942 | JSONField | N (default=dict) | N | `{}` | Terminal `_complete_execution` writes result payload. |
| `error_message` | :943 | TextField | Y (blank='') | N | `''` | Truncated per caller. |
| `tenant` | :946-949 | ForeignKey(core.Tenant, on_delete=SET_NULL, related_name='agent_executions') | Y | Y (FK) | NULL | S1039: multi-tenant cost attribution. |
| `execution_time_ms` | :952 | IntegerField | Y | N | NULL | Wall-clock elapsed ms. |
| `tokens_used` | :953 | IntegerField | N | N | `0` | Denormalized token sum (writer is `_complete_execution`; **no live aggregation task recomputes**). |
| `cost` | :954 | DecimalField(max_digits=8, decimal_places=4) | N | N | `Decimal('0.00')` | Denormalized cost (writer semantics UNKNOWN — F4 in §20 Appendix — no confirmed live writer). |
| `created_at` | :956 | DateTimeField (auto_now_add=True) | N | N (declared) | — | Wall-clock creation. Retention key candidate (§15). |
| `completed_at` | :957 | DateTimeField | Y | N | NULL | Terminal-row timestamp. |
| `last_heartbeat_at` | :961 | DateTimeField, db_index=True | Y | Y | NULL | S1100 heartbeat; 120s cadence from router daemon thread. Watchdog key. |
| `parent_execution_id` | :967 | UUIDField, db_index=True | Y | Y | NULL | S1098 PR #4: parent-dispatch pointer. |
| `root_execution_id` | :968 | UUIDField, db_index=True | Y | Y | NULL | S1098 PR #4: top-of-chain ancestor. |
| `conversation_id` | :977-979 | CharField(64), db_index=True | Y | Y | NULL | S1174 PR-1: PA conversation ID gating agent-follow-up wake. |

**Meta (lines 981-982):**
- `app_label='core'`
- **Zero declared indexes / unique constraints / ordering in Meta.** All indexes are via `db_index=True` on individual fields.

**Migration lineage (8 migrations at HEAD):**

- `core/migrations/0006_advisor_agent_agentcategory_spiderdata_and_more.py:252-306` (Session ~0006) — CreateModel.
- `core/migrations/0140_session_642_agentexecution_user_nullable.py:15-24` (S642) — AlterField (user nullable).
- `core/migrations/0191_add_experiment_fk_to_agent_execution.py:14-26` (S841) — AddField (experiment FK).
- `core/migrations/0192_session_843_orchestration_contract.py:38-87` (S843) — AddField ×5 (trace_id, project, owner_agent, parent_object_type, parent_object_id).
- `core/migrations/0249_session_1039_tenant_model_and_customer_access.py` (S1039) — AddField (tenant FK).
- `core/migrations/0301_agentexecution_last_heartbeat_at.py:13-17` (S1100) — AddField (last_heartbeat_at).
- `core/migrations/0335_agentexecution_cancelled_status.py:19-33` (S1098 PR #3) — AlterField (status choices, add `cancelled`).
- `core/migrations/0336_agentexecution_parent_root_lineage.py:28-56` (S1098 PR #4) — AddField ×2 (parent_execution_id, root_execution_id).
- `core/migrations/0357_session_1174_agentexecution_conversation_id.py:22-29` (S1174 PR-1) — AddField (conversation_id).

### FK graph

- **Outbound FKs from AgentExecution (5):** `agent` → Agent (CASCADE); `user` → AUTH_USER_MODEL (CASCADE nullable); `experiment` → core.Experiment (SET_NULL nullable); `project` → core.PartnershipProject (SET_NULL nullable); `tenant` → core.Tenant (SET_NULL nullable). All FK cascade choices consistent with the "detach on parent delete" pattern except `agent` + `user` (CASCADE).
- **Inbound FKs to AgentExecution:** ZERO. No model at HEAD declares `ForeignKey(AgentExecution)` (verifier-loop grep for `ForeignKey.*AgentExecution` returned 0 hits in `models*.py`).
- **Reverse-relation names (from FK related_name):** `Agent.executions`, `Experiment.agent_executions`, `PartnershipProject.agent_executions`, `Tenant.agent_executions`. `User.agentexecution_set` (default related_name).
- **Scalar downstream references (Cat A `celery_task_id` analog):** 6 models at HEAD carry `execution_id` as scalar UUIDField (NOT FK):
  - `core/models_llm_telemetry.py:54` (`LLMCallEvent.execution_id`, nullable, db_index=True) — S1702 F9.
  - `core/models_orchestration.py:270` (`OrchestrationExecution.execution_id`).
  - `core/models_orchestration.py:626` (`OrchestrationStepExecution.execution_id`, nullable, indexed).
  - `core/models_skin_layer.py:930` (`SkinLayerModel.execution_id`).
  - `core/models_user_learning.py:34` (`UserAgentLearning.execution_id`).
  - `core/models_deliverable_appends.py:83` (`DeliverableAppend.execution_id`).
  - Plus internal self-references `parent_execution_id` + `root_execution_id` on AgentExecution itself.

### Overlap flags vs Cat A/B/D/E/F + 3-class landmine

**F1 landmine resolution:** The `intelligence` app has two dead-code class bodies (`intelligence/models.py:587` package-shadowed + `intelligence/models/agent_execution.py:11` not re-exported). Django app registry lists only `intelligence.ActionPlanExecution` (renamed via migration 0003 per S1243). **No live `AgentExecution` class exists in `intelligence` app.** No live `AgentExecution` class exists in `agents` app either (renamed to `AgentTaskExecution` per S1244 PR #2685; 0 rows).

**Cross-cat overlap matrix:**

| Cat | Overlap direction | Field / column | Status |
|---|---|---|---|
| Cat A (CeleryTaskEvent) | Cat A → Cat C reverse write | `on_agent_task_failure_bridge` sets `AgentExecution.status='failed'` on SoftTimeLimitExceeded | LEGITIMATE cross-cat exception (S1701 F4). |
| Cat A (CeleryTaskEvent) | Cat C → Cat A correlation | `AgentExecution.input_data['celery_task_id']` (JSON scalar) | F7: JSON-path unindexed. |
| Cat B (LLMCallEvent) | Cat B → Cat C correlation | `LLMCallEvent.execution_id` UUIDField nullable non-FK | S1702 F9. |
| Cat D (ToolCallRecord) | Cat D → Cat C correlation | **NO execution_id field** on ToolCallRecord | F6: trace_id-only semantic join. |
| Cat E (OpsRunEvent) | Cat C → Cat E fanout | Rigby delegation signal handler writes OpsRunEvent lifecycle rows on Cat C `post_save` | LEGITIMATE (§10 + §16); documented under Employee OS. |
| Cat E (OpsRun) | Cat E → Cat C via detail JSON | `OpsRunEvent.detail['execution_id']` string (S1703 Explore 4 verified) | Loose semantic bridge. |
| Cat F (Heartbeat / systems) | No interaction | — | Passive telemetry sinks don't cross. |

---

## 5. Major Services

**Q8 + Q9: Services owned, dependency chains.**

### `core/agent_router.py` (3,493 lines) — Cat C production surface (primary writer)

Public API:
- `AgentRouter.route()` at `:836-888` (signature includes `create_execution_record: bool = True`, `existing_execution_record: Optional[Any] = None`, `trigger_source: Optional[str] = None`).
- `AgentRouter._create_execution_record()` at `:2787-2960` (start writer).
- `AgentRouter._complete_execution()` at `:3039-3150` (terminal writer).
- `AgentRouter._router_heartbeat_loop()` at `:2963-3019` (daemon-thread body).
- Cancel writer inside `route()` exception handler at `:1795-1798`.
- Wall-clock timeout early-save at `:1677-1688`.

Dependency chain (from S1703 Explore 2):
1. `TraceAttachmentService.resolve_trace_id(context)` and `resolve_project_id(context, user)` at `:2850-2851`.
2. `Agent.objects.get_or_create(name=agent_name, defaults={...})` at `:2818-2826` (side-effect: auto-creates Agent row for stats tracking).
3. `AgentExecution.objects.create(**_create_kwargs)` at `:2921` (retry-without-optionals fallback at `:2928`).
4. Daemon `threading.Thread(target=_router_heartbeat_loop, args=(execution.id,), daemon=True).start()` at `:3021`.

**God-service verdict:** 3,493 lines with extensive cross-domain imports (base_agent, image_agent, video_agent, context_tracing, priority, semaphore, timeouts, trace_attachment_service, tool_dispatcher, llm_router, workflow_orchestration, cancel_registry). **Exceeds 3,000-line threshold per playbook §13 Agent 2 god-service check.** Strong extraction candidate: heartbeat thread + trace resolution + lineage walk are self-contained concerns. Not new debt for Cat C — this is a router-scope concern surfaced by parent §5 D72 baseline; already registered on Group 1900 backlog per parent D74 axis discipline.

### `core/agents/base_agent.py` (5,962 lines) — Cat C indirect surface (delegation to router)

Public API relevant to Cat C:
- `@property def agent_router(self)` at `:848-856` returns `AgentRouter` instance.
- `delegate_to_specialist(...)` at `:948` calls `self.agent_router.route(specialist_agent, task, context=delegation_ctx)`.

**No `route()` method on BaseAgent.** F3 wording drift from parent §3.C. All agent-execution telemetry writes route through `AgentRouter`, not BaseAgent.

**God-service verdict:** 5,962 lines — well above 3,000 threshold. Not net-new Cat C debt (BaseAgent scope, not Cat C scope).

### `core/tasks_agents.py` (6,293 lines) — Cat C companion writer (Celery wrapper path)

Public API relevant to Cat C:
- `execute_agent_task` Celery task (`@shared_task`) which lazy-imports AgentExecution at `:2114` and writes via `_impl_execute_agent_task` at `:2311+`.
- `cleanup_stale_agent_executions` Celery task at `:1554-1654` (30-min cadence beat; S925).
- `cleanup_stale_llm_calls` at `:1659+` (Cat B watchdog; S1221 P2 Tier 2 — not Cat C).

Writes `input_data['celery_task_id'] = str(self.request.id)` at `:2274, 2280`.

Per S1084 audit block (models_unified_system.py:1006-1008): **both `tasks_agents._impl_execute_agent_task` and `agent_router._create_execution_record` write to `core.AgentExecution`**. The two paths coexist; no de-dup or write-boundary discipline enforces one canonical write path. Session 1083 audit added heartbeat sync between them.

**God-service verdict:** 6,293 lines. Same as BaseAgent — router-domain / task-domain concern; already registered.

### `core/agent_execution_wrapper.py` (97 lines) — DEAD CODE

Public API: `class AgentExecutionTracker` (context manager) + `def track_agent_execution()` factory. Writes `AgentExecution.objects.create()` at `:34`. Imports from `core.models_unified_system` at `:4`.

**Verifier-loop callers audit:** Zero production callers of `core.agent_execution_wrapper.track_agent_execution` or `AgentExecutionTracker`. All 20+ `track_agent_execution(` grep hits at HEAD resolve to a DIFFERENT tracker (`ai_core/agents/execution_tracker.py:27` — Redis-based, not DB). Docs archive references (`docs/archive/sessions/SESSION_37-A_*.md`) predate the router path introduction and are historical.

**Dead-code candidate confirmed** per feedback_verify_before_deleting_dead_code memory rule (all-caller-audit clean). §15 Debt-8. Post-arc T-slot cleanup candidate.

### `ai_core/agents/execution_tracker.py` (660 lines) — REDIS TRACKER, NOT Cat C

Public API: `class AgentExecutionTracker` with `track_agent_execution()`, `track_file_creation()`, `get_active_agent_count()`, etc. **All writes are to Redis via `self.redis_client.hincrby()`, `lpush()`, etc. NO DB writes to `AgentExecution` model.** Imports `UnifiedAgentTemplate` at `:599` for counting agents. Not part of Cat C schema; belongs to `ai_core` observability lens (Group 1900 candidate).

Naming collision with dead `core/agent_execution_wrapper.py:AgentExecutionTracker` is confusing but not a Cat C boundary issue.

### `core/services/execution_tracker.py` — DOES NOT EXIST

Parent §3.C references "`core/services/execution_tracker.py`" but verifier-loop confirms **this file does not exist at HEAD**. Parent scoping drift; xx99 anchor-update owed. The intended reference may be `ai_core/agents/execution_tracker.py` (Redis tracker; see above) or `core/agent_execution_wrapper.py` (dead code).

---

## 6. Major APIs and Interfaces

**Q10 + Q11 + Q12 + Q13: External-facing surface.**

### REST endpoints (mounted under `core/urls*.py`)

- **GET `/api/v1/agents/execution/<execution_id>/`** — `execution_detail` view at `core/views_agent_execution.py:466`. Returns full record.
- **POST `/api/v1/agents/execution/<execution_id>/cancel/`** — `cancel_agent_execution` at `:945`. Writes cancel signal via CancelTokenRegistry.
- **GET `/api/v1/agents/execution/<execution_id>/cancel-state/`** — `get_agent_execution_cancel_state` at `:1033`. Reads CancelTokenRegistry state.
- Analytics endpoints in `views_analytics.py` + `views_analytics_real.py` + `views_agent_analytics.py` + `views_agent_dashboard.py` + `views_agent_learning.py` (9+ filter/count sites; per-agent throughput, error rate, latency).
- **GET `/api/agent-analytics/executions/`** — recent execution logs.
- **GET `/api/agent-analytics/stats/`** — aggregate stats.
- **Trace endpoints** in `views_trace_viewer.py` filter by `trace_id`.

### WebSocket

- **`AgentExecutionConsumer`** at `core/consumers_agents.py:87-230`. Messages: `subscribe_execution` (line 188), `get_execution_logs` (:192), `cancel_execution` (:196). Channel group naming: `execution_{execution_id}`.

### PA tools

- **`_get_agent_execution_output`** at `core/services/td_handlers_agents.py:163-294` — enrichment helper (called from other handlers). READ-only. Direct UUID + `input_data__celery_task_id` fallback.
- **`schedule_followup`** at `:5133-5246` — reads AgentExecution, writes AgentFollowupSubscription (S1174 PR-2a).
- **`cancel_agent_execution`** at `:945` — writes cancel signal via CancelTokenRegistry (not direct row mutation).

**NO dedicated `execution_history_tool` / `execution_query_tool` / `execution_tool` action set** in `pa_tool_schemas.py`. F4-adjacent gap; §19 R4 candidate.

### Celery tasks (beat schedule)

- **`cleanup_stale_agent_executions`** at `core/tasks_agents.py:1554-1654`. Beat cadence: every 30 min (verified via `core/celery.py:138-142` per S1703 Explore 3). Purpose: stuck-heartbeat watchdog.
- **`cleanup_old_executions`** at `core/tasks_agents.py:812-828`. Writes to `AgentTaskExecution` (agents_registry canonical per S1244 rename). **NOT Cat C** (0-row target table).

### Management commands

- **`cleanup_stuck_executions`** at `core/management/commands/cleanup_stuck_executions.py`. S866. `--apply` + `--hours` + `--delete-cleaned` flags. Manual utility.
- No dedicated `audit_agent_execution` / `dedupe_agent_execution` command at HEAD.

### Signals emitted / received on Cat C

See §10 Event Flows. **4 `post_save` receivers on `core.AgentExecution` at HEAD.**

---

## 7. Runtime Flows

**Q14 + Q15: Flow diagrams.**

### Flow 1: Router-dispatched agent (direct, non-Celery)

```
Caller (PA tool, view, script)
     │
     ▼
AgentRouter.route(agent_name, task, context)                    [agent_router.py:836]
     │
     ├── Wall-clock timeout wrapper (Phase 2 fail-open)          [:1616-1688]
     │
     ├── if create_execution_record: True (default)
     │      │
     │      ▼
     │   _create_execution_record()                              [:2787-2960]
     │      │
     │      ├── LAZY IMPORT: from core.models_unified_system     [:2814]
     │      │       import Agent, AgentExecution
     │      │
     │      ├── Agent.objects.get_or_create(name=agent_name)     [:2818-2826]
     │      │
     │      ├── trace_id  = TraceAttachmentService.resolve_trace_id(context)  [:2850]
     │      ├── project_id = TraceAttachmentService.resolve_project_id(...)   [:2851]
     │      │
     │      ├── Resolve parent_execution_id / root_execution_id  [:2872-2900]
     │      │       (walks parent row for existing root)
     │      │
     │      ├── AgentExecution.objects.create(                   [:2921]
     │      │       agent=agent_record,
     │      │       user=self.user,          # nullable since S642
     │      │       task=task[:500],
     │      │       status='in_progress',
     │      │       input_data={'task': task, 'context_injected': ctx_summary,
     │      │                   'context': raw_ctx (if dict)},
     │      │       experiment=experiment,   # S841
     │      │       trace_id=trace_id,       # S843
     │      │       project_id=project_id,
     │      │       owner_agent=agent_name,
     │      │       parent_object_type=ctx.get('parent_object_type', ''),
     │      │       parent_object_id=ctx.get('parent_object_id'),
     │      │       last_heartbeat_at=timezone.now(),           # S1100
     │      │       parent_execution_id=resolved_parent_id,     # S1098 PR #4
     │      │       root_execution_id=resolved_root_id,         # S1098 PR #4
     │      │   )
     │      │       → fallback retry without optional fields    [:2928]
     │      │
     │      ├── Backfill root_execution_id = self.id for root-of-tree  [:2933-…]
     │      │
     │      └── Spawn daemon heartbeat thread                    [:3021]
     │             → 120s cadence loop `.update(last_heartbeat_at=now)` [:2989-2991]
     │
     ├── context['execution_id'] = execution_record.id           [:1528-1529]
     │      (threads execution_id into downstream Cat B llm_call_span metadata)
     │
     ├── agent.execute(task, context)                            [:1587-1609]
     │      │
     │      ├── Cat B writes: llm_call_span(execution_id=...)   [wrapper writes LLMCallEvent]
     │      │
     │      └── Cat D writes: ToolCallRecord.record(trace_id=...) [wrapper writes ToolCallRecord]
     │             (NOTE: ToolCallRecord has NO execution_id field — F6)
     │
     └── _complete_execution(execution_record, agent_name, success, ...)  [:3039-3150]
            │
            ├── execution_record.status = 'completed' if success else 'failed'  [:3064]
            ├── execution_record.completed_at = timezone.now()                  [:3066]
            ├── execution_record.execution_time_ms = <computed>
            ├── execution_record.output_data = <result>
            └── execution_record.save(update_fields=[...])                      [:3078-3081]
                    → fires post_save signal → §10 Event Flows

Cancel path (LLMCallCancelled exception in agent.execute):
     ▼
     LAZY IMPORT + AgentExecution.objects.filter(id=…).update(status='cancelled') [:1795-1798]
Wall-clock timeout path (Phase 2 fail-open):
     ▼
     execution_record.status = 'failed' + save(update_fields=[...])              [:1680-1688]
```

**One row per logical call.** Heartbeat updates existing row; retries do not create new rows. Cancel + timeout paths write terminal early; `_complete_execution` runs after normal path only.

### Flow 2: Celery-wrapped agent (execute_agent_task path)

Same shape as Flow 1, but wrapped in a `@shared_task` and the writer path is `_impl_execute_agent_task` at `core/tasks_agents.py:2114+2311` instead of `_create_execution_record`. Companion writer per S1084 audit block. Injects `input_data['celery_task_id'] = str(self.request.id)` at `:2274, 2280` in addition to the router-set fields. Downstream `post_save` receivers fire the same as Flow 1.

### Flow 3: Cat A fire-alarm reverse write (S1701 F4)

```
Celery task fails with SoftTimeLimitExceeded
     ▼
Cat A signal: task_failure fires
     ▼
core/celery_telemetry.py:240-286 (on_agent_task_failure_bridge)
     ▼
Looks up CeleryTaskEvent (Cat A row) → finds AgentExecution by execution_id or task_id correlation
     ▼
AgentExecution.objects.filter(id=…).update(status='failed', error_message=<sig>)
     ▼
Cat C row is marked failed even though the router/task never completed the row
```

This is the S1219 P1 cross-cat exception documented in S1701 §16 + inherited by Cat C at §16 below.

### Flow 4: PA path (F4 uncovered)

```
PA user message
     ▼
core/services/unified_pa_entrypoint.py (GPT-5.2 function-calling loop)
     ▼
LLM decides to invoke a tool
     ▼
Tool dispatcher runs the tool
     │
     ├── Tool is a wrapped agent invocation (e.g., run_agent)
     │       ▼
     │   AgentRouter.route(...) → Flow 1 or Flow 2 → Cat C row written
     │
     └── Tool is a direct action (e.g., deliverable_tool, session_tool)
             ▼
         NO Cat C row is written
         Cat B LLMCallEvent (from wrapper-adopted callers) has execution_id=NULL
         Cat D ToolCallRecord may still write via S970 __init_subclass__ wrapper (trace_id-only)
```

**F4 CRITICAL**: The PA path is the platform's primary user surface (per PLATFORM_WHAT_IT_IS narrative — Rigby chat + Command Center + all Workspace tabs route through PA). Every PA turn without a `run_agent` tool call is invisible to Cat C. This is the single largest coverage gap.

### Flow 5: Watchdog cleanup

```
Beat scheduler fires cleanup_stale_agent_executions (30 min cadence)
     ▼
core/tasks_agents.py:1554-1654
     ▼
Filter: AgentExecution.objects.filter(
    status__in=('running', 'in_progress'),
    last_heartbeat_at__lt=now - 60min  # or created_at__lt for pre-S1100 rows
)
     ▼
.update(status='failed', error_message='Task timed out after 60 minutes (no heartbeat)')
     ▼
post_save fires on each updated row → §10 Event Flows
```

**Retention gap:** Rows in terminal states (completed/failed/cancelled) accumulate unbounded. No date-based sweep exists.

---

## 8. Data Ownership and Lifecycle

**Q16 + Q17: Ownership + lifecycle.**

**Owner:** `AgentRouter` (`core/agent_router.py`) with companion writer `_impl_execute_agent_task` (`core/tasks_agents.py`). Both write to `core.AgentExecution` at `models_unified_system.py:882-1014`.

**Lifecycle states:**

| State | Trigger | Writer | File:Line |
|---|---|---|---|
| `pending` | Never (schema default; no writer path emits pending rows at runtime) | — | (default value only) |
| `in_progress` | `_create_execution_record` / `_impl_execute_agent_task` create | AgentRouter, tasks_agents | agent_router.py:2906; tasks_agents.py:2311+ |
| `completed` | `_complete_execution` with success=True | AgentRouter | agent_router.py:3064 |
| `failed` | `_complete_execution` with success=False OR wall-clock early-save OR cleanup_stale_agent_executions OR Cat A fire-alarm reverse write | Multiple | agent_router.py:3064, :1680; tasks_agents.py:1554; celery_telemetry.py:240 |
| `cancelled` | LLMCallCancelled exception path | AgentRouter | agent_router.py:1795-1798 |

**Idempotency:** Watchdog uses queryset update pattern (thread-safe). Router create is idempotent (each dispatch creates new row; no upsert). Fire-alarm reverse write uses filter+update (idempotent per row).

**Data retention:** **NONE at date level.** Watchdog only status-flips stuck rows; does not delete. §15 Debt-2.

**Deletion:** No production deletion path. `cleanup_stuck_executions` mgmt cmd has optional `--delete-cleaned` flag but is manually invoked.

**Cascade behavior on parent delete:** `AgentExecution.agent` (CASCADE) — deleting an `Agent` deletes its executions. `AgentExecution.user` (CASCADE) — deleting a `User` deletes their executions. `AgentExecution.experiment` (SET_NULL nullable). `AgentExecution.project` (SET_NULL nullable). `AgentExecution.tenant` (SET_NULL nullable). CASCADE on agent + user is aggressive — deleting a User cascades all their execution history including tokens/cost aggregates. Debt-9 candidate: soft-delete or SET_NULL on user might be more archive-friendly, but out of scope for P3 per parent §3.C boundary discipline.

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22: Cross-domain integration matrix + primitives.**

### Cross-cat correlation matrix (D74 axis contribution)

| Source model | Field pointing at AgentExecution | Class variant | FK or scalar | Index | Notes |
|---|---|---|---|---|---|
| Cat A `CeleryTaskEvent` | None (task_id in Cat A) + reverse write bridge | — | scalar (via reverse) | — | Cat A → Cat C: `on_agent_task_failure_bridge` writes `AgentExecution.status='failed'` on SoftTimeLimitExceeded (S1701 F4). Cat C → Cat A: `AgentExecution.input_data['celery_task_id']` (F7 unindexed). |
| Cat B `LLMCallEvent` | `execution_id` UUIDField | core.AgentExecution | scalar UUID | `db_index=True` (models_llm_telemetry.py:54-61) | S1702 F9: Intentional non-FK ("telemetry survives execution deletion" + "NULL for detached calls"). |
| Cat D `ToolCallRecord` | **NO execution_id field** | — | trace_id semantic match only | `db_index=True` on trace_id | **F6 gap.** ToolCallRecord.trace_id ↔ AgentExecution.trace_id semantic join; no schema-enforced correlation. |
| Cat E `OpsRunEvent` | `detail['execution_id']` string in JSON | — | scalar (in JSON) | — | Rigby delegation signal writes OpsRunEvent lifecycle rows on Cat C post_save; execution_id lives in `OpsRunEvent.detail` JSONField. Not a queryable column. |
| `OrchestrationExecution` | `execution_id` UUIDField | core.AgentExecution | scalar UUID | — | S1703 Explore 1: `core/models_orchestration.py:270`. |
| `OrchestrationStepExecution` | `execution_id` UUIDField | core.AgentExecution | scalar UUID nullable | Yes | `core/models_orchestration.py:626`. |
| `SkinLayerModel` | `execution_id` UUIDField | core.AgentExecution | scalar UUID | — | `core/models_skin_layer.py:930`. |
| `UserAgentLearning` | `execution_id` UUIDField | core.AgentExecution | scalar UUID | — | `core/models_user_learning.py:34`. |
| `DeliverableAppend` | `execution_id` UUIDField | core.AgentExecution | scalar UUID | — | `core/models_deliverable_appends.py:83`. |
| `ActionPlan` | `agent_executions` reverse FK | intelligence.ActionPlanExecution (not core.AgentExecution) | reverse FK | — | S1243 rename — ActionPlanExecution.action_plan is the FK; core.AgentExecution has no ActionPlan FK. Different scope. |

**Cross-model spine posture (D74 axis input from Cat C):**

Cat C owns TWO cross-model spine primitives:

1. **`execution_id`** (i.e., `AgentExecution.id`). Downstream carriers: 6 models above (LLMCallEvent + 5 orchestration/learning/deliverable models). All are non-FK UUIDField scalars per the "survive deletion" rationale (S1098 wrapper docstring at models_llm_telemetry.py:56-60). Coverage per-route-path; F4 PA-path uncovered.

2. **`trace_id`** (S843 orchestration UUID). Downstream carriers: `ToolCallRecord.trace_id` (`models_tool_calls.py:47`, indexed) + `LLMCallLog.trace_id` (F1 sibling from S1702; S697 field). Also on `AgentExecution` itself (indexed). Populated by `TraceAttachmentService.resolve_trace_id(context)` at write time; nullable when `context` has no trace ancestor.

**trace_id writer-of-record + propagation expectations (Rigby SIGN cycle 1 F1 fold).** Verifier-loop confirmed the single production writer of `AgentExecution.trace_id` is the router path — `AgentRouter._create_execution_record()` at `core/agent_router.py:2850-2851` (calls `TraceAttachmentService.resolve_trace_id(context)` + `resolve_project_id(context, user)`) and writes into the create kwargs at `:2910`. The companion Celery-wrapper writer path (`_impl_execute_agent_task` in `core/tasks_agents.py:2114+`) was verifier-loop-checked and does NOT thread trace_id into its create kwargs at HEAD (grep for `trace_id=` in `core/tasks_agents.py` returned no create-site hits; only per-context inheritance for downstream calls). **Consequence:** router-direct dispatches ensure trace_id propagation from the resolver; Celery-wrapper dispatches leave trace_id=NULL unless the caller pre-populates context. **Best-effort, not always present.** For the PA path (F4 CRITICAL), trace_id is never written because no AgentExecution row is created at all. Downstream: LLMCallEvent has NO `trace_id` field per S1702 §4 field inventory; ToolCallRecord carries `trace_id` via S970 `__init_subclass__` wrapper at write time but is NOT tied to the router's trace_id (Cat D writers set trace_id from their own context resolution). **xx99 posture-implication:** Option B (trace_id as canonical arc-wide spine) requires closing the Celery-wrapper writer gap + closing PA-path coverage + adding trace_id to LLMCallEvent — three separate changes vs Option A (execution_id) which requires only PA-path coverage + ToolCallRecord.execution_id addition. Option A is the smaller lift at schema level; Option B is closer to S843 orchestration semantics if the propagation gaps are closed.

**Choice-point for xx99:** Between `execution_id` and `trace_id`, which is the D74 canonical spine?
- `execution_id` covers Cat B (LLMCallEvent) directly but NOT Cat D (ToolCallRecord; F6).
- `trace_id` covers Cat D (ToolCallRecord) + Cat B sibling (LLMCallLog) but has NULL-ratio uncertainty for PA-path executions (S1703 Appendix UNK-1). Cat B `LLMCallEvent` does NOT have `trace_id` (per S1702 §4 field inventory; verified).
- **Neither spine covers Cat A (CeleryTaskEvent)** at schema level. Cat A ↔ Cat C requires `AgentExecution.input_data['celery_task_id']` string JSON-path (F7). Cat A ↔ Cat B and Cat A ↔ Cat D require walking through Cat C first.
- **Cat C's spine candidates are `execution_id` + `trace_id`; Cat A's spine is `task_id`** (S1701 §9 spine claim; 8 downstream models carry `celery_task_id` scalar per S1701). Cat C does NOT lack a spine — it offers two candidates — but neither of Cat C's candidates covers Cat A's row-id domain at schema level; the correlation goes through Cat C's `input_data['celery_task_id']` JSON-path (F7) instead. `task_id` is a third arc-wide spine candidate that lives on the Cat A side, not the Cat C side (Rigby SIGN cycle 1 F3 fold — wording tightening).

**xx99 posture options for D74 axis (Cat C contribution):**

- **Option A: `execution_id` as arc-wide canonical spine.** Requires closing F6 gap (add ToolCallRecord.execution_id) + closing F4 gap (PA path writes AgentExecution row). Preserves the "non-FK / survive deletion" property per S1702 wrapper contract.
- **Option B: `trace_id` as arc-wide canonical spine.** Requires closing Cat B `LLMCallEvent.trace_id` gap (add field or read from LLMCallLog sibling) + closing NULL-ratio uncertainty via mandatory `TraceAttachmentService` population. Preserves S843 orchestration semantics.
- **Option C: Retain per-cat primitives** (`task_id` + `execution_id` + `trace_id` + `mission_id`) and build a **shared correlation view** at query time (Postgres materialized view or Redis lookup table). No schema changes; adds join-service layer. Matches S1702 F9 option (e.ii) "shared correlation-view / join contract."
- **Option D: Hybrid** — canonical spine at telemetry-write level (`execution_id`) + trace_id as arc-wide breadcrumb for user-visible drilldowns.

**Recommended per parent §6.3 T-slot boundary:** xx99 decides among A/B/C/D. P3 does NOT design the spine; P3 catalogs.

### Ownership of `input_data['celery_task_id']` correlation

**Writers:** `core/tasks_agents.py:2274, 2280` (Celery wrapper path only). Router-direct dispatches do NOT write `celery_task_id`. Test fixtures at `tests/services/test_celery_failure_agentexecution_bridge.py:91, 36`. `core/services/claude_code_engineer.py:118` (S1262 pattern).

**Readers:** `core/tests/test_claude_code_task_receipts_s1262.py` verifies `input_data.get('celery_task_id')` at `:113`. **No production reader implements the 3-hop chain** `CeleryTaskEvent.task_id → AgentExecution.input_data['celery_task_id'] → downstream` (theoretical only per S1702 F9 correlation-chain claim). This is a **coverage gap for cross-cat observability queries**; §19 R5.

---

## 10. Event Flows

**Q19 + Q20: Event emission + consumption.**

### `post_save` receivers on `core.AgentExecution` (4 at HEAD)

| Receiver | File:Line | Sender declaration | Purpose | Gating |
|---|---|---|---|---|
| `on_delegation_lifecycle` | `core/signals/rigby_delegation_signals.py:131-265` | `sender="core.AgentExecution"` (string; avoids circular import) | Writes `OpsRunEvent` lifecycle rows (`agent_assigned` on create; `agent_completed` + `verification_started` + `verification_completed` on terminal status). Counts `LLMCallEvent.objects.filter(execution_id=execution.id, status='SUCCESS')` at `:102-104` to derive verdict. | `settings.RIGBY_DELEGATION_ENABLED` (default False in production) |
| `on_agent_execution_completed` | `core/learning_bridges/agent_execution_bridge.py:317` | `sender=AgentExecution` (direct import) | Learning-loop update via `AgentExecutionLearningLoop.process_event()`. Fires on terminal status. | Status in {'completed', 'failed'} |
| Experiment linker | `core/services/experiment_linker.py:256` | `sender=AgentExecution` (direct import) | Links execution to experiment (S841 pattern). Idempotent. | Experiment ID present in context |
| Human attention bridge | `core/services/human_attention_bridge.py:578` | `sender='core.AgentExecution'` (string) | Human-attention trigger heuristics. | Session-specific gate |

**Fan-out characteristics:**
- Signal fires on **every save**, including watchdog updates (F5) and cancel-path queryset updates (`.filter().update()` bypasses signals BUT `.save()` does not). Cancel + timeout paths use `.update()` which does NOT fire post_save; only success/failure via `.save()` triggers. **Watchdog uses `.update()`** — signals DO NOT fire on watchdog-flipped rows. Cancel path also bypasses signals. This is a **partial silence**: rigby delegation signal misses cancelled + watchdog-timeout terminal states.
- No signal-handler duration telemetry beyond what individual handlers write (LLMCallEvent inside the learning bridge chain, OpsRunEvent inside rigby delegation). No orchestrated observability for the fan-out itself.

### Cat C emit → Cat E consume bridge (Rigby delegation)

Detailed in §9 above. Writes `OpsRunEvent.detail['execution_id']` string (not a queryable column). Cat E → Cat C reverse-query requires JSON-path scan.

### Cat C emit → learning-loop consume

`AgentExecutionLearningLoop.process_event()` receives the AgentExecution instance and updates learning bridges. Downstream writes include `AgentLearning` XP + pattern detection + `AgentKnowledgeSource` shared knowledge (per PLATFORM_WHAT_IT_IS.md lines 162-163 narrative).

### Explicit event contract absence

Cat C does NOT emit domain events on an EventBus surface (per parent §5 D72 "post-EventBus dormant" observation). All fan-out is via Django signals. No pub/sub, no Kafka topic, no WebSocket broadcast except the per-execution channel group `execution_{execution_id}` (S1703 Explore 3).

---

## 11. Existing Documentation

**Q10-Q13 anchor: research coverage classification per playbook §12.**

### Topic docs

- **`docs/topics/agent-system.md`** — mentions AgentExecution in the "post-execution outcome recording" list (line 162-163) and ToolCallRecord's `__init_subclass__` auto-wrap (S970, lines 107-113). **Does NOT mention the 3-class landmine, the write path (router vs BaseAgent), or the correlation contract.**
- **`docs/topics/employee-os.md`** — Employee OS join surface list at `:64-65` names OpsRun + OpsRunEvent + LLMCallEvent + ToolCallRecord for `evidence_for_mission`. **Conspicuously omits AgentExecution from this join.** Cross-doc gap.
- **`docs/topics/celery-workers.md`** — CeleryTaskEvent scope only; correctly stays out of Cat C.
- **`docs/topics/personal-assistant.md`** — no AgentExecution mention; no explicit note that PA path writes zero rows (F4 gap surfaced by this audit).

### Handoff anchors

- **S641** — Agent Performance Dashboard (canonical anchor for `_create_execution_record` addition).
- **S843** — Orchestration Contract (`trace_id`, `project`, `parent_object_type`, `parent_object_id`, `owner_agent`).
- **S970** — BaseAgent `__init_subclass__` (auto-wrap ToolCallRecord; not AgentExecution).
- **S1039** — Multi-tenant cost attribution (tenant FK).
- **S1083** — Rigby audit: heartbeat sync between router path + tasks_agents path.
- **S1084** — Retired misleading deprecation warning (commit `0d0afd1d`; text preserved in the same class body at :993-1014).
- **S1098 PR #3** — 5th status `cancelled` addition.
- **S1098 PR #4** — Lineage fields `parent_execution_id` + `root_execution_id`.
- **S1100** — `last_heartbeat_at` addition.
- **S1115** — LearningBridge ABC refactor; AgentExecutionLearningLoop migrated.
- **S1174 PR-1** — `conversation_id` field (agent-follow-up wake).
- **S1174 PR-2a** — `AgentFollowupSubscription` model (S1703 Explore 3).
- **S1206** — BaseAgent `.run()` writes AgentExecution telemetry row (Layer 1 audit; per Discord bot comment).
- **S1209** — URC v0.1 envelope; router persists `context` under `input_data['context']` (agent_router.py:2831-2837).
- **S1243** — `intelligence.AgentExecution` → `ActionPlanExecution` rename (migration 0003).
- **S1244** — `agents.AgentExecution` → `agents.AgentTaskExecution` rename (commit `2d65b44f`; PR #2685).
- **S1262** — Claude Code task receipts pattern uses `input_data['celery_task_id']`.
- **S1701 Cat A audit** — Cat A ↔ Cat C fire-alarm reverse-write bridge (F4 in S1701).
- **S1702 Cat B audit** — F9 execution_id correlation posture (D74 axis contribution from Cat B).

### Research library

- **`docs/research/domains/observability/1700_observability_domain_scoping.md`** — parent §3.C (lines 473-526) catalogues 3-class landmine + boundary rule + load-bearing questions.
- **`docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md`** — Cat A audit; §9 U4 candidate (JSON-path unindexed) resurfaces here as F7.
- **`docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md`** — F9 correlation-chain claim inherited by this audit; 3-hop chain claim refined below.

### ARCHITECTURE_INDEX

No dedicated §1.N entry for "AgentExecution as subject" prior to S1703; the model appears as a correlation primitive in prior Cat B + Cat A audit entries. S1703 will register at §1.49 per line-6 v46 bump.

### CLAUDE.md

Lists `AgentExecution` under Key Files → `core/agent_router.py`. Does not explicitly name it as Cat C or reference the 3-class landmine.

### PLATFORM_INVENTORY

Lists `AgentExecution` + `AgentExecutionMemory` under core models. **No per-class row count. No differentiation between the 3 class bodies (F1) or between `core.AgentExecution` (live) + `agents.AgentTaskExecution` (0 rows) + `intelligence.ActionPlanExecution` (0 rows at S1243 rename time).** §7 anchor-update owed by xx99.

### PLATFORM_WHAT_IT_IS

Narrative anchor at lines 373-376 names Family: Agents → AgentExecution, AgentMemory, etc. under `core.models_unified_system`. Correctly identifies canonical location but does NOT mention landmine.

---

## 12. Research Coverage

Per playbook §12 taxonomy (NONE / LIGHT / MODERATE / DEEP / CANONICAL):

**Cat C research coverage at HEAD: LIGHT-MODERATE**

Rationale:
- Parent scoping (S1700 §3.C) is comprehensive on the landmine + boundary rule + load-bearing Qs.
- Prior integration points exist across multiple handoffs (S641/S843/S970/S1083/S1084/S1098/S1100/S1174/S1206/S1209/S1243/S1244/S1262) but no consolidated audit prior to S1703.
- Sibling audits (S1701 Cat A + S1702 Cat B) established correlation contract from their side; Cat C's own contract was inferred, not documented.
- Topic docs partial: mention wrapper but not write path, not 3-class landmine, not PA path coverage.
- PA surface: NONE (zero query tools) — F4-adjacent.
- Cross-doc disagreement (`employee-os.md` omits AgentExecution from `evidence_for_mission` join).

**S1703 is the FIRST dedicated Cat C audit.** Upgrades coverage to MODERATE (single-audit + parent + sibling triangulation + verifier-loop).

---

## 13. Architecture Maturity

**Cat C architecture maturity at HEAD: PARTIAL + STABLE for router-covered surface**

**Risk: HIGH**

Evidence for maturity verdict:
- Router-path telemetry contract is coherent: STARTED create + heartbeat + terminal write; lineage + cancel + retention watchdog + 5-state status enum + S1174 conversation_id gate.
- Test coverage exists across 8+ test files (`test_cancel_ancestor_propagation`, `test_cancel_token_e2e`, `test_celery_failure_agentexecution_bridge`, `test_execution_history_reverse_link`, `test_claude_code_task_receipts_s1262`, `test_base_agent_provenance_wiring`, `test_provenance_*`, `test_spider_context_instrumentation`).
- 172 files import the canonical class from `core.models_unified_system` — deep production embedment.
- **PARTIAL** because:
  - F1 3-class landmine (2 dead-code source files not cleaned up)
  - F2 stale docstring (S287 deprecation notice against runtime reality)
  - F3 parent scope wording drift (`BaseAgent.route()` doesn't exist)
  - F4 PA path zero coverage (largest single gap)
  - F5 no date-based retention
  - F6 Cat D correlation gap (ToolCallRecord no execution_id)
  - F7 JSON-path unindexed on celery_task_id
  - F8 4 unmonitored post_save receivers; watchdog + cancel paths use `.update()` bypassing signals
  - Django admin registration ABSENT (matches Cat A + Cat B pattern; consistent gap)

Evidence for risk verdict:
- **F2 CRITICAL drift** (stale docstring) actively misleads readers.
- **F4 CRITICAL PA coverage gap** (primary user surface leaves no execution telemetry trail).
- **F6 HIGH cross-cat correlation gap** (ToolCallRecord loose-coupled by trace_id semantic match only).

---

## 14. Known Drift

### D1 — S287 deprecation notice reversed (F2 CRITICAL)

**Claim:** Docstring at `core/models_unified_system.py:882-887` — "DEPRECATED: Use `agents.models.AgentExecution` instead. This model is deprecated as of Session 287."

**Runtime reality:**
- `agents/models.py` is a compatibility shim per S391 comment (points at `core/models/agents_registry/` which contains `AgentTaskExecution`, not `AgentExecution`).
- `agents.AgentExecution` was renamed to `agents.AgentTaskExecution` in S1244 (commit `2d65b44f`, PR #2685). AgentTaskExecution table: 0 rows (never had a writer wired).
- `core.AgentExecution` is the LIVE canonical (S1084 audit block at :993-1014: "58 rows in last 2h in local, all reads by `ops_tool` come from here").
- The `.save()` deprecation warning was removed in S1084 (commit `0d0afd1d`); docstring at :882-887 was NOT updated.

**Severity: CRITICAL.** Actively misleads new contributors. §7.4 anchor-update owed by xx99.

### D2 — Parent scoping "BaseAgent's `route()` wrapper" (F3 MEDIUM)

**Claim:** Parent §3.C at 1700_observability_domain_scoping.md line 480+ — "Which of the 3 `AgentExecution` classes is written to by BaseAgent's `route()` wrapper, and via which import path."

**Runtime reality:** BaseAgent has NO `route()` method. Delegation is via `self.agent_router.route(...)` at `core/agents/base_agent.py:948` (property accessor at :848-856). The canonical write path is `AgentRouter._create_execution_record()` at `core/agent_router.py:2787-2960` (lazy import at :2814; create call at :2921).

**Severity: MEDIUM.** Parent scoping wording drift; correct write-path identification is preserved (canonical import path resolved by this audit). §7.4 anchor-update owed by xx99.

### D3 — Parent §3.C "core/services/execution_tracker.py" file does not exist (MEDIUM)

**Claim:** Parent §3.C at line 508 — "Wrappers: `core/agent_execution_wrapper.py` + `core/services/execution_tracker.py`."

**Runtime reality:** `core/services/execution_tracker.py` does NOT exist at HEAD (verifier-loop). The `ai_core/agents/execution_tracker.py` file exists but is a Redis-based tracker with NO DB writes to AgentExecution (see §5).

**Severity: MEDIUM.** §7.4 anchor-update owed by xx99.

### D4 — Parent §3.C 3-class landmine misclassifies dead code (HIGH — Rigby SIGN cycle 1 F2 fold escalated MEDIUM → HIGH)

**Claim:** Parent §3.C at 1700_observability_domain_scoping.md lines 173-181 + 490-506 — three `class AgentExecution` bodies at HEAD.

**Runtime reality:** Only `core.AgentExecution` is registered with the Django app registry (verifier-loop via `apps.get_app_config('intelligence').get_models()`). The two intelligence-side class bodies are **dead code**: `intelligence/models.py:587` is package-shadowed; `intelligence/models/agent_execution.py:11` is not re-exported from `intelligence/models/__init__.py`. The intelligence-side canonical is `intelligence.ActionPlanExecution` (renamed via migration `0003_session_1243_rename_agentexecution_to_actionplanexecution.py`).

**Severity: HIGH.** Parent scoping identified the class bodies correctly but did not resolve their runtime status. **This drift risks remediation against unreachable classes, not just documentation confusion** — a future contributor reading parent §3.C could migrate the wrong class, write migrations against a dead-code definition, or write callers that import the unreachable class name and be surprised at runtime. Escalated from MEDIUM per Rigby SIGN cycle 1 F2 fold: dead-code misclassification is worse than mere wording drift because it can misdirect remediation work. §7.4 anchor-update owed by xx99. The deprecation ADR is still post-arc T-slot per parent §6.3 boundary discipline — but the scope is now cleanup of 2 dead source files, not merge-of-3-live-classes.

### D5 — Employee OS `evidence_for_mission` join omits AgentExecution (MEDIUM)

**Claim:** `docs/topics/employee-os.md:64-65` — evidence_for_mission joins OpsRun + OpsRunEvent + LLMCallEvent + ToolCallRecord.

**Runtime reality:** The Rigby delegation signal handler explicitly reads AgentExecution + counts LLMCallEvent per execution (`rigby_delegation_signals.py:102-104`). Employee OS mission evidence would benefit from AgentExecution join for `owner_agent` + `trace_id` + `input_data.task`.

**Severity: MEDIUM.** Doc gap; §7.4 anchor-update owed by xx99 (or Employee OS doc PR).

### D6 — PLATFORM_INVENTORY no per-class row count (LOW)

**Claim:** PLATFORM_INVENTORY lists `AgentExecution` without differentiating `core.AgentExecution` (live) vs `agents.AgentTaskExecution` (0 rows) vs `intelligence.ActionPlanExecution` (0 rows at rename).

**Severity: LOW.** Inventory captures ORM-registered models; the 0-row entries are correctly listed but the "which one is live" question isn't surfaced. Chris ratification post-arc for whether inventory should annotate live-vs-dormant. §7.1 anchor-update candidate.

---

## 15. Known Technical Debt

### Debt-1 (HIGH) — F1 dead-code cleanup: 2 orphaned class bodies

`intelligence/models.py:587-652` (`class AgentExecution`, package-shadowed) + `intelligence/models/agent_execution.py:1-80` (`class AgentExecution`, not re-exported). Both dead per §14 D4.

**Post-arc T-slot cleanup** per parent §3.C + §6.3. Safe deletion (verifier-loop: 0 imports of either at HEAD; both are unreachable at Python import time). Blocked pending Chris ratification per parent boundary discipline.

### Debt-2 (HIGH) — F2 docstring cleanup: retire S287 deprecation notice

`core/models_unified_system.py:882-887` still says "DEPRECATED: Use agents.models.AgentExecution instead" but this direction is reversed (§14 D1). S1084 removed the runtime warning; docstring not updated. Safe edit (docstring-only). Post-arc T-slot cleanup per parent boundary discipline.

### Debt-3 (HIGH) — F4 PA-path AgentExecution coverage

PA agentic loop writes zero AgentExecution rows unless the tool being dispatched is a router-registered agent invoked via `run_agent`. Analog to S1702 Cat B F2. xx99 R1 candidate.

### Debt-4 (MEDIUM) — F5 no date-based retention

`cleanup_stale_agent_executions` is a stuck-heartbeat watchdog, not retention. AgentExecution rows accumulate unbounded post-completion. Cat A has 30-day `CELERY_TASK_EVENT_RETENTION_DAYS` retention; Cat B sibling `LLMCallLog` has 30-day retention via `cleanup_llm_call_logs`. Cat C has neither. Row-count monitoring absent. xx99 R2 or T2 candidate.

### Debt-5 (HIGH) — F6 Cat D correlation gap (ToolCallRecord no execution_id)

ToolCallRecord (`core/models_tool_calls.py:19-131`) has `trace_id` + `conversation_id` + `agent_name` but NO `execution_id`. Cross-cat correlation to Cat C is trace_id semantic match only. Deletion of AgentExecution row orphans ToolCallRecord rows at the correlation level (no FK; no schema enforcement). Two posture options for xx99: (a) add `ToolCallRecord.execution_id` UUIDField (nullable non-FK; matches LLMCallEvent posture); (b) formalize `trace_id` as canonical spine + close NULL-ratio uncertainty. xx99 R3 candidate.

### Debt-6 (MEDIUM) — F7 JSON-path unindexed on celery_task_id

`AgentExecution.input_data['celery_task_id']` is JSON scalar with no GIN or functional index. Callers relying on the 3-hop CeleryTaskEvent ↔ Cat C chain scan the JSON at query time. S1701 §9 U4 confirmed applicable. xx99 T3 candidate.

### Debt-7 (MEDIUM) — F8 4 unmonitored post_save receivers; signal-fan-out semi-silent

Watchdog cleanup (`.update()`) + cancel path (`.update()`) do NOT fire post_save signals; only success/failure via `.save()` triggers. Rigby delegation lifecycle events therefore MISS watchdog-timeout terminals + cancelled terminals. §19 R4 candidate for either (a) instrumenting `.update()` paths or (b) documenting the partial silence as intentional.

### Debt-8 (LOW) — `core/agent_execution_wrapper.py` (97 lines) is dead code

Zero production callers (verifier-loop; §5). Naming collision with `ai_core/agents/execution_tracker.py:AgentExecutionTracker` (Redis-based). Post-arc T-slot cleanup candidate per feedback_verify_before_deleting_dead_code memory rule (all-caller audit clean).

### Debt-9 (LOW) — Agent + User CASCADE on delete

`AgentExecution.agent` (CASCADE) + `AgentExecution.user` (CASCADE) delete execution history including tokens/cost aggregates. Consideration: soft-delete or SET_NULL for archive-friendliness. Post-arc T-slot per parent §3.C.

### Debt-10 (LOW) — No dedicated PA `execution_history_tool` / `execution_query_tool`

Rigby cannot introspect execution history without going through analytics REST views + trace_viewer. §19 R4 candidate.

### Debt-11 (LOW) — No Django admin registration

Verifier-loop grep for `AgentExecutionAdmin` returned 0 hits. Matches Cat A + Cat B pattern; consistent gap across observability arc. §19 T-slot candidate.

---

## 16. Boundary Violations

**Q23-Q27: Cross-cat writes, orphans, dead code.**

### Writer boundary discipline

| Writer | Target | Cat | Classification |
|---|---|---|---|
| `agent_router._create_execution_record` at `:2921` | AgentExecution (Cat C) | C→C | LEGITIMATE (primary writer) |
| `agent_router._complete_execution` at `:3078-3081` | AgentExecution (Cat C) | C→C | LEGITIMATE (terminal writer) |
| `agent_router.route` cancel path at `:1795-1798` | AgentExecution (Cat C) | C→C | LEGITIMATE (cancel writer) |
| `agent_router.route` timeout early-save at `:1680-1688` | AgentExecution (Cat C) | C→C | LEGITIMATE (Phase 2 fail-open) |
| `agent_router._router_heartbeat_loop` at `:2989-2991` | AgentExecution.last_heartbeat_at (Cat C) | C→C | LEGITIMATE (S1083 pattern) |
| `tasks_agents._impl_execute_agent_task` at `:2311+` | AgentExecution (Cat C) | C→C | LEGITIMATE (companion writer per S1084 audit) |
| `tasks_agents.cleanup_stale_agent_executions` at `:1554-1654` | AgentExecution.status (Cat C) | C→C | LEGITIMATE (watchdog) |
| `management/commands/cleanup_stuck_executions` | AgentExecution.status (Cat C) | C→C | LEGITIMATE (manual utility) |
| `celery_telemetry.on_agent_task_failure_bridge` at `:240-286` | AgentExecution.status (Cat C) | **A → C** | **LEGITIMATE CROSS-CAT EXCEPTION** (S1701 F4; S1219 P1 fire-alarm) |
| `rigby_delegation_signals.on_delegation_lifecycle` at `:131-265` | OpsRunEvent (Cat E) | **C → E** | LEGITIMATE (documented Employee OS bridge; C-scope signal writer with E-scope side effect) |
| `agent_execution_bridge.on_agent_execution_completed` at `:317` | AgentLearning + AgentKnowledgeSource (Learning) | C → Learning | LEGITIMATE (S1115 bridge) |
| `experiment_linker` at `:256` | Experiment side effects | C → Experiment | LEGITIMATE (S841 pattern) |
| `human_attention_bridge` at `:578` | HumanAttentionEvent (or equivalent) | C → Attention | LEGITIMATE (session-specific) |

**No undocumented boundary violations detected.**

### Non-wrapper direct writes (would-be violations)

Grep for `AgentExecution.objects.create` at HEAD returns:
- `core/agent_router.py:2921` (primary writer; LEGITIMATE)
- `core/tasks_agents.py:2311+` (companion writer; LEGITIMATE per S1084)
- `core/agent_execution_wrapper.py:34` (DEAD CODE; §15 Debt-8)
- test fixtures across `core/tests/` + `tests/services/` (test-scoped; LEGITIMATE)

**Cat C write-boundary discipline is intact for production code.** One dead-code writer file remains as cleanup candidate.

### Orphan candidates

- **`core/agent_execution_wrapper.py`** — DEAD CODE (§15 Debt-8; §5 all-caller-audit clean).
- **`intelligence/models.py:587`** — DEAD CODE (§15 Debt-1; package-shadowed).
- **`intelligence/models/agent_execution.py`** — DEAD CODE (§15 Debt-1; not re-exported).
- **`AgentTaskExecution` in `core/models/agents_registry/models.py:434`** — 0 rows since S1244 rename per S1244 handoff. Not Cat C scope (renamed away from Cat C); belongs to `agents` app scope. Ownership currently ambiguous per parent D74 axis discipline — post-arc T-slot for `agents_registry` scope decision.

---

## 17. Duplicate or Overlapping Systems

### 3-class landmine (F1)

Resolved above:
- `core.AgentExecution` at `core/models_unified_system.py:882` — LIVE canonical.
- `intelligence/models.py:587` — DEAD (package-shadowed).
- `intelligence/models/agent_execution.py:11` — DEAD (not re-exported).
- `intelligence.ActionPlanExecution` at `intelligence/models/action_plan.py` — LIVE (S1243 rename; 0 rows at rename time; different scope than Cat C — ActionPlan-scoped step execution).
- `agents.AgentTaskExecution` at `core/models/agents_registry/models.py:434` — LIVE (S1244 rename target; 0 rows; different scope — rich per-task record).

### Denormalized aggregation surfaces

- `AgentExecution.tokens_used` (IntegerField, default 0) — writer semantics: `_complete_execution` may set from agent context (per S1703 Explore 3 assertion; not verified in verifier-loop). Analog to Cat B `LLMCallEvent.tokens_in + tokens_out`. If tokens_used is set at completion time only, it is NOT a live rollup of Cat B rows for the execution; it's a snapshot the agent computed. No production Celery task recomputes `tokens_used` from LLMCallEvent (verifier-loop: 0 hits for `LLMCallEvent.objects.filter(execution_id=x).aggregate(Sum('tokens_in') + Sum('tokens_out'))` at HEAD).
- `AgentExecution.cost` (Decimal, default 0.00) — same posture; writer semantics UNKNOWN per §20 Appendix UNK-4.

**Debt-adjacent gap:** If Cat B is the authoritative token/cost source, Cat C denorm fields either duplicate or drift. xx99 posture question.

### Third-store overlap (per S1702 F1)

S1702 F1 identified `CostTracking` at `core/models_unified_system.py:6665` as third LLM-cost store (surfaced by Rigby SIGN cycle 1). Cat C's `tokens_used` + `cost` denorm fields are a FOURTH overlap surface — per-execution rollup at Cat C, per-call at Cat B (LLMCallEvent + LLMCallLog), aggregate at CostTracking. Full triangulation is xx99 (S1799) scope per S1702 R2 HIGH.

---

## 18. Ownership Gaps

**Q25: Named owner per subsystem.**

**Owner:** `AgentRouter` (single owner class; primary writer + terminal writer + cancel writer + heartbeat writer).

**Co-owners** (per S1084 audit block): `_impl_execute_agent_task` in `core/tasks_agents.py` (companion writer for Celery-wrapped executions).

**Governance:** No documented team / person owner in CLAUDE.md, PLATFORM_WHAT_IT_IS, or topic docs. Git blame shows mixed authorship between clwest and Chris West (S1703 Explore 6). No documented ratification path for AgentExecution schema changes.

**F4 ownership gap:** PA path lacks a designated Cat C writer. Unclear whether the PA path SHOULD write AgentExecution rows (and what the fields would be), or whether PA orchestration deserves its own telemetry model. xx99 R1 posture question.

**F6 ownership gap:** ToolCallRecord (Cat D) and AgentExecution (Cat C) have no shared correlation contract. Owner-side responsibility: unclear whether Cat C or Cat D should add the FK / scalar. xx99 R3 posture question.

**Reader-side ownership:** No first-class PA read surface. `_get_agent_execution_output` is an enrichment helper, not a dedicated `execution_history_tool`. §19 R4.

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows (per playbook §12 rule).

### R1 (HIGH) — F4 PA-path AgentExecution coverage

**Question:** Should the PA agentic loop write AgentExecution rows for each user turn? Or does PA deserve its own telemetry model? What fields would populate?

**Blocks:** Full arc-wide observability of user-triggered work. Downstream drilldowns (Rigby introspection tools, execution history, cost attribution per PA session) cannot span PA turns.

**Analog:** S1702 F2 (LLMCallEvent PA coverage; also uncovered).

**xx99 scope:** Frame posture — new model vs extended AgentExecution write path vs status quo (no coverage). Choose per D73 posture-framing discipline.

### R2 (HIGH) — F1 + F2 landmine + docstring cleanup ADR (xx99 evidence-plan / decision framing only)

**Question:** Cleanup path for (a) 2 dead source files (`intelligence/models.py:587` + `intelligence/models/agent_execution.py:11`); (b) stale S287 docstring at `core/models_unified_system.py:882-887`.

**Blocks:** Reader confusion. New contributor onboarding cost. Every code review that touches the file eats the confusion.

**xx99 scope:** Chris-ratified ADR to delete 2 files + rewrite docstring. Not designed by P3 per parent §3.C + §6.3 boundary discipline. **Boundary guard (Rigby SIGN cycle 1 F4 fold):** No deprecation ADR authored in Cat C; xx99 owns consolidation direction. R2 remains "posture decision + evidence-plan needed" and does NOT authorize model deletion or migration merge at S1703 close.

### R3 (HIGH) — F6 ToolCallRecord ↔ AgentExecution correlation posture

**Question:** Should ToolCallRecord get an `execution_id` UUIDField (nullable non-FK per LLMCallEvent posture)? Or is `trace_id` semantic join the canonical contract?

**Blocks:** Cat D + Cat C join contract for xx99 D74 axis. Employee OS `evidence_for_mission` reliability.

**xx99 scope:** Choose between option (a) add execution_id + backfill (b) formalize trace_id as canonical + close NULL-ratio gap (c) shared correlation-view (S1702 F9 option e.ii).

### R4 (MEDIUM) — Dedicated PA `execution_history_tool` + admin registration + `.update()` signal instrumentation

**Question:** Should Rigby have a first-class `execution_tool` (list / detail / cancel / lineage) matching Cat A `task_breakdown_tool` shape? Should Django admin register AgentExecution? Should watchdog + cancel `.update()` paths fire post_save signals?

**Blocks:** Rigby introspection surface. Ops observability. Rigby delegation lifecycle coverage on watchdog-terminated rows.

**xx99 scope:** Prioritize per user-visibility × ops-cost tradeoff.

### R5 (MEDIUM) — 3-hop correlation chain implementation

**Question:** Is the theoretical 3-hop chain `CeleryTaskEvent.task_id → AgentExecution.input_data['celery_task_id'] → downstream` implemented anywhere in production? Should it be? Alternatives (shared view; JSONField-lookup helper)?

**Blocks:** Cross-cat observability queries (Cat A ↔ Cat B, Cat A ↔ Cat D via Cat C intermediary).

**xx99 scope:** Choose between (a) add GIN index on `AgentExecution.input_data->>'celery_task_id'` (F7 debt); (b) formalize a shared correlation view; (c) status quo (theoretical chain, JSON-path scan when needed).

### R6 (MEDIUM) — Retention policy for AgentExecution

**Question:** What is the target retention window for post-completion AgentExecution rows? 30 days (Cat A / LLMCallLog analog)? 90 days? Never?

**Blocks:** Storage bloat. Ops query performance on large tables.

**xx99 scope:** Chris-ratified retention policy + `AGENT_EXECUTION_RETENTION_DAYS` env var + beat task.

### R7 (LOW) — CASCADE vs SET_NULL on Agent + User FKs (Debt-9)

**Question:** Should deleting a User cascade-delete their execution history? Or should the execution row survive with `user=NULL`?

**xx99 scope:** Archive-friendliness vs GDPR-alignment tradeoff.

### R8 (LOW) — tokens_used + cost denorm reconciliation (§17)

**Question:** Are the denormalized `tokens_used` + `cost` fields on AgentExecution consistent with per-call Cat B rollups? What is the writer semantics? Is there drift?

**xx99 scope:** Choose between (a) authoritative source is Cat C snapshot + reconcile at write time; (b) authoritative source is Cat B + recompute at read time; (c) status quo (potentially drifting).

### R9 (LOW) — Dead-code sweep for `core/agent_execution_wrapper.py`

**Question:** Delete the 97-line dead file per §15 Debt-8.

**xx99 scope:** Post-arc T-slot cleanup.

### R10 (LOW) — `AgentTaskExecution` (0 rows since S1244) posture

**Question:** Delete, migrate, or accept as latent-optional per S1244 rename posture. NOT Cat C scope; belongs to `agents_registry` scope but touches the "3-class landmine" narrative.

**xx99 scope:** Chris-gated cross-arc handoff to `agents_registry` audit surface if opened.

---

## 20. Appendix

### 20.1 Files inspected

Direct file reads by parent-Claude verifier-loop:
- `core/models_unified_system.py` (:880-1015)
- `intelligence/models/agent_execution.py` (:1-80)
- `intelligence/models.py` (:580-660)
- `intelligence/models/__init__.py` (full)
- `intelligence/migrations/0003_session_1243_rename_agentexecution_to_actionplanexecution.py` (full)
- `core/models_tool_calls.py` (:1-140)
- `core/agent_router.py` (:2787-2960)
- `docs/handoffs/SESSION_1702_OBSERVABILITY_CAT_B_LLM_CALL_EVENT_AUDIT.md` (:1-200 for template)
- `docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md` (:1-200)
- `docs/research/domains/observability/1700_observability_domain_scoping.md` (:460-600 for Cat C scope)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (:879-1170 for template + evidence rules)
- `docs/PLATFORM_INVENTORY.md` (partial preview via context-kit orient)
- `docs/PLATFORM_WHAT_IT_IS.md` (partial preview via context-kit orient)

### 20.2 Grep patterns used (verifier-loop)

- `from core\.models_unified_system import.*AgentExecution|models_unified_system.*AgentExecution` (172 hits; production embedment count)
- `from intelligence\.models\.agent_execution` (0 hits; dead-code confirmation)
- `execution_id|ForeignKey.*AgentExecution|agent_execution_id` in `models_tool_calls.py` (0 hits; F6 verification)
- `AgentExecution` in `unified_pa_entrypoint.py` (1 hit; comment-only line 6050 = F4 verification)
- `from core\.agent_execution_wrapper|AgentExecutionTracker\(|track_agent_execution\(` (all-caller audit for §15 Debt-8; 0 production callers of `core.agent_execution_wrapper`)
- `post_save.*core\.AgentExecution|sender=.*AgentExecution|receiver.*AgentExecution` (F8 fan-out inventory; 4 hits)
- `celery_task_id` in `core/tasks_agents.py` (F7 verification; 2 writer lines at :2274, 2280)
- Django app registry: `apps.get_app_config('intelligence').get_models()` (F1 landmine resolution)

### 20.3 Docs inspected

Per §11.

### 20.4 Unresolved unknowns

- **UNK-1 (F4-adjacent):** Percentage of `LLMCallEvent` rows at HEAD with `execution_id = NULL` (i.e., PA-path or script-path calls). Requires live-DB query beyond verifier-loop scope. xx99 evidence gathering.
- **UNK-2 (F9-adjacent):** Percentage of `AgentExecution` rows at HEAD with `trace_id = NULL`. Requires live-DB query. xx99 evidence gathering.
- **UNK-3 (§17 denorm):** Writer semantics for `AgentExecution.cost` (DecimalField). No verified writer at HEAD via verifier-loop grep. Possibly written by Celery wrapper path at `tasks_agents.py:2311+` (S1703 Explore 3 asserted; not verified line-by-line).
- **UNK-4 (§10):** Are watchdog `.update()` + cancel `.update()` paths intentional signal-silence or accidental gap? No handoff explicitly states intent.
- **UNK-5 (§4):** `AgentExecution.status` has no `db_index=True` on the field itself and no composite index in Meta. Analytics view `AgentExecution.objects.filter(status='in_progress')` scans without index. Query-cost UNKNOWN at HEAD. §15 Debt-adjacent latent.
- **UNK-6 (§9):** `LLMCallEvent.trace_id` not in Cat B schema per S1702 §4 (verified). But some LLMCallEvent metadata JSONField writes may carry `trace_id` key as a workaround. Cross-cat trace-based join reliability UNKNOWN.

### 20.5 Conflicts between sources

- **Sub-agent 1 vs Sub-agent 4** (S1703 Explore) — Explore 1 said intelligence/models.py:587 and intelligence/models/agent_execution.py:11 are "IDENTICAL CLASS BODIES (true duplicate)"; Explore 4 said "TWO CLASSES, DIFFERENT SCOPES." Parent-Claude verifier-loop resolved: **both files are dead code; runtime status is neither** (Django app registry has no `intelligence.AgentExecution` entry). The two source files differ in field count (agent_execution.py adds 3 success-tracking fields) but neither is registered at import time.
- **Parent §3.C vs runtime** — parent said 3 live classes; runtime has 1 live + 2 dead + 1 renamed (ActionPlanExecution) + 1 renamed cross-app (AgentTaskExecution).
- **Parent §3.C vs code** — parent said "BaseAgent's route() wrapper"; runtime has AgentRouter.route() wrapper (BaseAgent delegates via property).

### 20.6 Rigby SIGN cycle 1 fold notes

Single-batch 4-question pattern per S1701 + S1702 D48 20th-arm precedent (arc pin `pa-e7fbacc996b34b44`; fresh SIGN pin `pa-f1a30b7ed5bb4042` routed-around by wrapper hard-code at `tools/pa_local.sh:128`). Overall verdict: **SIGN-with-edits at Medium-High confidence**. Four folds landed pre-commit.

- **F1 (Medium) — trace_id writer-of-record + propagation expectations** — Added to §9 D74 axis contribution section (paragraph immediately after the `trace_id` spine-candidate bullet). Documents that router path writes trace_id via `TraceAttachmentService.resolve_trace_id(context)` at `agent_router.py:2850-2851, :2910`; Celery-wrapper writer path does NOT thread trace_id; PA path writes nothing. **Consequence:** xx99 posture Option B (trace_id canonical spine) requires 3 gap-closures (Celery-wrapper writer + PA path + LLMCallEvent.trace_id addition) vs Option A (execution_id) which requires 2 (PA path + ToolCallRecord.execution_id). Option A is smaller schema-level lift; Option B is closer to S843 orchestration semantics.
- **F2 (Low) — D4 severity escalation MEDIUM → HIGH** — §14 D4 severity updated with Rigby's rationale: "dead-code misclassification risks wrong remediation, not just documentation confusion." Escalated because a future contributor reading parent §3.C could migrate the wrong class body, write migrations against a dead-code definition, or import an unreachable class name.
- **F3 (Low) — §9 spine-candidate wording clarified** — Replaced ambiguous "Cat C does NOT own a Cat A-style task_id-analog cross-model spine" with "Cat C's spine candidates are execution_id + trace_id; Cat A's spine is task_id" + explicit reassurance that Cat C offers TWO spine candidates (does not lack a spine).
- **F4 (optional Low) — R2 boundary guard** — §19 R2 marked as "xx99 evidence-plan / decision framing only" with explicit guard: "No deprecation ADR authored in Cat C; xx99 owns consolidation direction. R2 remains posture decision + evidence-plan needed and does NOT authorize model deletion or migration merge at S1703 close."

**Rigby CONFIRM verdicts (no folds required beyond F1-F4):**
- **Q1 coverage-completeness Medium-High** — F1-F9 set correct; F5/F7/F8 are the right "risk texture" items.
- **Q2 drift-severity Medium** — D1 CRITICAL agree, D2 MEDIUM agree, D3 MEDIUM agree, D5 MEDIUM acceptable (unless evidence_for_mission is authoritative for ops/mission audits — then HIGH). Only D4 needed escalation (F2 fold above).
- **Q3 D74 axis correctness High** — F9 correct; two spine candidates + A/B/C/D posture options at the right altitude for xx99. Two clarity notes folded (F1 + F3 above).
- **Q4 R1-R10 ranking + xx99 scope discipline Medium-High** — Ordering defensible. R6 retention could bump HIGH if volume evidence surfaces (kept MEDIUM absent quantified volume). No T-slot boundary violation. F4 fold added optional guard.

### 20.7 Verifier-loop history

Pre-Explore verifier-loop (parent-Claude): read parent §3.C in full; read playbook §11.2 template; read S1702 template for shape; noted F3 wording drift candidate (BaseAgent.route()).

Post-Explore verifier-loop (parent-Claude): read `core/models_unified_system.py:880-1015` (verified S287 docstring vs S1084 override); read `intelligence/models/agent_execution.py` (verified field set differs from intelligence/models.py:587 by 3 success-tracking fields); read `intelligence/models.py:580-660` (verified same-name class body); read `intelligence/models/__init__.py` (verified only ActionPlanExecution re-exported); read `intelligence/migrations/0003` (verified S1243 RenameModel to ActionPlanExecution); read `core/models_tool_calls.py:1-140` (verified no execution_id field); read `core/agent_router.py:2787-2960` (verified write path); ran Django `apps.get_app_config('intelligence').get_models()` (verified F1 landmine resolves to 1-alive + 2-dead).

### 20.8 Session context

- Fresh SIGN isolation pin: `pa-f1a30b7ed5bb4042` (routed-around by wrapper hard-code at `tools/pa_local.sh:128` per S1600/S1700/S1701/S1702 precedent; arc pin `pa-e7fbacc996b34b44` receives SIGN traffic).
- Arc pin: `pa-e7fbacc996b34b44` (Group 1700 arc pin; in service through S1799 close).
- D48 preemptive stability-probe gate: 20th arm start on arc pin (S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702 CONFIRMED 14-consecutive-fully-clean-arms sub-pattern per S1702 close).
- Playbook version: v2 §11.2 20-section child audit template (THIRD application under Group 1700; SECOND child under this arc since S1701 + S1702).

---

*End of S1703 Group 1700 Cat C — AgentExecution Child Audit*
