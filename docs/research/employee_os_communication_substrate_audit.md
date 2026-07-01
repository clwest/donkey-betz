---
title: "Employee OS Communication Substrate — Audit (research only)"
status: draft
session: 1268
date: 2026-06-30
mission_type: research
authority: |
  Evidence-only audit. No runtime changes. No PRs. No new architecture.
  No Employee Collaboration design yet. Reuse classifications are
  proposals, not decisions.
companion_docs:
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/topics/employee-os.md
  - docs/topics/agent-system.md
  - docs/topics/personal-assistant.md
  - docs/handoffs/SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md
verifier_loop: |
  Five parallel Explore sub-agents produced evidence reports
  (agent-to-agent, PA chat, employee OS, governance/safety, failure
  history). All load-bearing file:line citations re-verified by
  Claude via direct Grep/Read before this doc was written.
  Independent review by Rigby complete (S1268 PA conversation
  pa-01e90a1d36f54880): confirmed all three highlighted reuse
  classifications, confirmed the 3-vs-4 employee drift, clarified
  S1264 warn-mode scope, named first inter-employee write
  candidate, and added two missing primitives to the inventory.
  Her additions are folded into §2.1, §5.5, §9 Q4, and §10.
owner: claude (synthesis) + rigby (independent review, S1268)
---

# Employee OS Communication Substrate — Audit

> **Purpose.** Before we design Employee-to-Employee collaboration we
> need an honest inventory of every primitive Donkey Betz already
> ships for AI-to-AI, AI-to-human, and human-to-AI messaging. This
> doc is the inventory + a first-pass reuse classification. **No
> design here.** Anything that looks like a recommendation in §10
> is "next research step," not "next build step."

---

## 1. Executive Summary

Donkey Betz has **three operational comms substrates** and a fourth
that is partially-built and load-bearing for any future
employee-collaboration work:

1. **Agent-to-agent dispatch** — `AgentRouter.route()` +
   `AgentExecution` + `BaseAgent.delegate_to_agent()`. Recursion is
   capped at depth=3 (`base_agent.py:905`). Heartbeat watchdog at
   `agent_router.py:2945-2980`. Cost telemetry via `LLMCallEvent`.
   No native message-passing semantics — all inter-agent comms
   travel through the `context` dict on the `route()` call.
2. **PA / chat substrate** — `ChatConversation` model
   (`core/models/conversations/models.py:59-251`) + Daphne
   WebSocket consumer (`PAConversationConsumer`) + Celery `pa`
   queue. The "source" field distinguishes web / mobile / discord /
   api / claude-code / pa. `AgentFollowupSubscription`
   (`models_unified_system.py:1017`) is the bridge that turns an
   `AgentExecution` terminal save into a chat banner.
3. **Employee OS substrate** — `MissionRunner`
   (`core/employees/mission_runner.py`) orchestrates frozen
   `AIEmployee` + `JobContract` dataclasses (`core/employees/jobs.py`)
   into mission runs recorded as `OpsRun(domain='mission')` +
   `OpsRunEvent` (`core/models_ops_runs.py`). Inter-employee
   visibility today is **read-only** via `OpsRun` joins and
   `post_shift_report()` direct-messages.
4. **Inbox / DirectMessage / MessageThread**
   (`core/models_messaging.py`) — already documented as the
   substrate for shift reports
   (`EMPLOYEE_OS_PRIMITIVES.md` row 10) but the WebSocket consumer
   `/ws/system-events/` does **not yet** broadcast a "DM arrived"
   event (`EMPLOYEE_OS_PRIMITIVES.md` row 22, v0 design choice).

**Headline finding.** Every primitive an employee-to-employee
protocol could need already exists — the gap is a *contract*, not
a missing data layer. Reuse is preferred; new models are
explicitly an anti-pattern (`EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1).

**Headline risk.** Three failure classes are directly relevant to
multi-employee collaboration and are NOT structurally prevented
today:

- Receipt-chain gap in dispatched tools (`claude_code_tool`
  pattern — closed by PR #2752 S1262 but the pattern can recur for
  any new dispatch surface).
- Queue parity drift between Procfile and Makefile (silent
  task-stall failure mode — caught by canary
  `test_celery_queue_parity.py` post-S1244).
- Silent-coercion of LLM optional params (`False` / `0` autofill)
  on any tool dispatched between employees.

---

## 2. Existing Communication Primitives

### 2.1 Tabular inventory

This table is the substrate map. It is **not** a recommendation —
classifications in §8 propose reuse/avoidance. Counts mirror
`PLATFORM_INVENTORY.md`; do not hand-edit.

| # | Primitive | Surface | Canonical file:line | Carries |
|---|---|---|---|---|
| 1 | `AGENT_MAP` | Module-level dict | `core/agent_router.py` (declaration near line 320) | Deterministic name → `BaseAgent` subclass routing |
| 2 | `AgentRouter.route()` | Sync entry point | `core/agent_router.py:836-945` | Agent dispatch + execution-record creation |
| 3 | `AgentExecution` | Django model | `core/models_unified_system.py:875-980` | trace_id, parent_execution_id, root_execution_id, conversation_id, last_heartbeat_at |
| 4 | `BaseAgent.delegate_to_agent()` | Method | `core/agents/base_agent.py:890-950` | Sub-agent call w/ depth-3 cap (`max_depth = 3`, line 905) |
| 5 | `conversation_orchestrator` | Multi-agent flow | `core/conversation_orchestrator.py` | TURN_FLOWS (lines 60-107); ConversationState (lines 110-130) |
| 6 | `WorkflowOrchestrationAgent` | BaseAgent subclass | `core/agents/workflow_orchestration_agent.py:105-150` | result['steps'] envelope (NOT 'step_results') |
| 7 | `AgentFollowupSubscription` | Django model | `core/models_unified_system.py:1017-1116` | Bridge: AgentExecution terminal → chat banner |
| 8 | `ToolCallRecord` | Django model | `core/models_tool_calls.py:19-150` | trace_id, agent_name, tool_name, parameters, result_hash |
| 9 | `ChatConversation` | Django model | `core/models/conversations/models.py:59-251` | source enum, workspace FK, agents_used, agent_results |
| 10 | `unified_pa_chat` HTTP | API view | `core/views_personal_assistant.py:267-504` | POST `/api/pa/chat/` → task_id |
| 11 | `process_pa_chat_task` | Celery task | `core/tasks.py:11907-11914` | acks_late=False; queue=`pa`; soft=280s/hard=300s |
| 12 | `UnifiedPAEntrypoint` | Service | `core/services/unified_pa_entrypoint.py:1-375` | GPT-5.2 agentic loop; enrichment fan-out |
| 13 | `tool_dispatcher.execute()` | Async dispatcher | `core/services/tool_dispatcher.py:584-650+` | ToolResult envelope (ok, latency_ms, error_code, trace_id) |
| 14 | `pa_tool_schemas.py` | Schema registry | `core/services/pa_tool_schemas.py` (5324 lines) | 119 function-calling schemas (cf. 156 handlers) |
| 15 | `AIEmployee` + `JobContract` | Frozen dataclasses | `core/employees/jobs.py:74-162` | Identity + policy (no DB row per employee) |
| 16 | `_EMPLOYEES_BY_HANDLE` / `_JOBS_BY_EMPLOYEE` | Module-level dicts | `core/employees/jobs.py:1327-1347` | 4 employees registered (Rigby, Platform Auditor, Chief of Staff, Bug Triage Specialist) |
| 17 | `MissionRunner` | Orchestrator class | `core/employees/mission_runner.py:595` | preflight → steps → postflight → verdict → escalation |
| 18 | `MissionRunnerConfig` | Frozen dataclass | `core/employees/mission_runner.py:529-590` | Includes `auto_emit_verdict: bool = True` (S1267 addition, line 589) |
| 19 | `OpsRun(domain='mission')` | Django model | `core/models_ops_runs.py:11-89` | One row per mission run; mission_id, run_kind, status, summary JSONField |
| 20 | `OpsRunEvent` | Django model | `core/models_ops_runs.py:91-118` | Step timeline; idempotent on (run, label) via get_or_create |
| 21 | `emit_mission_verdict()` | Pure helper | `core/employees/mission_verdict.py:63-175` | certified / rejected / deferred; idempotent on (mission, verdict) |
| 22 | `post_shift_report()` | Pure helper | `core/employees/comms.py:228-367` | One DM per terminal mission per persistent (employee, job) thread |
| 23 | `_persist_to_summary()` | Pure helper | `core/employees/_persistence.py:36-59` | Atomic OpsRun.summary merge (lifted to shared S1267 PR 4.0) |
| 24 | `employee_tool` | PA tool | `core/services/td_handlers_employee.py:100-430` | describe / run_now / status / evidence_for_mission |
| 25 | `mission_verdict` tool | PA tool | `core/services/td_handlers_employee.py:434-503` | Rigby-gated certify / reject / defer |
| 26 | `messaging_tool` (read-only v0) | PA tool | `core/services/td_handlers_core.py` | list_threads / get_thread / unread_count; send_message gated by `settings.MESSAGING_TOOL_ALLOW_SEND` |
| 27 | `DirectMessage` + `MessageThread` + `ThreadParticipant` | Django models | `core/models_messaging.py` | Inbox-style persistent threads, per-user read cursor, metadata-keyed lookup |
| 28 | `HumanAttentionItem` | Django model | `core/models_human_interface.py` | Decision funnel (approve/reject) with auto-expire/auto-approve |
| 29 | `LLMCallEvent` | Django model | `core/models_llm_telemetry.py` | Per-call audit; execution_id FK; cancelled flag; metadata.ops_run_id correlates to mission |
| 30 | `CeleryTaskEvent` | Django model | `core/models_celery_telemetry.py` | task lifecycle; agent_name dimension (S1169); 30d default retention |
| 31 | `EventBus` (Redis Streams) | Service | `core/services/event_bus.py` | 6 named streams + DLQ (`mi:dead_letter`, line 106) |
| 32 | `/ws/system-events/` | Daphne consumer | `core/consumers_*.py` (multiple) | 9 typed events; does NOT yet carry DM-arrived event (per `EMPLOYEE_OS_PRIMITIVES.md` row 22) |
| 33 | `Deliverable` | Django model | `core/models_deliverables.py:84-283` | publish_intent enum; status workflow; escalation surface used by MissionRunner |
| 34 | `DeliverableEvent` | Django model | `core/models_deliverables.py:561-610` | status_transition rows with `ctx.ops_run_id` correlation |
| 35 | `messaging_tool` send-guard | Defense in depth | `core/services/td_handlers_core.py:3694-3711` | `send_message` is OFF — handler returns `MESSAGING_SEND_DISABLED` unless `settings.MESSAGING_TOOL_ALLOW_SEND=True`; absent from schema **and** runtime-gated (Rigby S1268 review) |
| 36 | `_broadcast_new_message(thread, msg)` | Inbox delivery hook | `core/services/td_handlers_core.py:3773-3775` → `core/views_inbox` | Called when a DM is created; pushes the new-message event to the inbox UX path (Rigby S1268 review addition) |

### 2.2 Why this matters for collaboration

Three observations from the inventory:

1. The platform composes employee work from **primitives, not
   a model-per-feature** — `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1
   call this out explicitly. The 23-row anti-duplication matrix
   names every "do not build" instinct that has already cost
   operator hours. Adding `EmployeeMessage`, `EmployeeNotification`,
   `MissionRun`, `ShiftReport`, `EmployeeAuditLog` etc. is named
   as an anti-pattern.
2. **The substrate is read-rich, write-thin.** Employees today
   produce evidence (OpsRun, OpsRunEvent, Deliverable, DM) but
   only Rigby ever *sends* a programmatic message
   (`post_shift_report`). Free-form LLM-driven outbound
   `messaging_tool.send_message` is **OFF by default**
   (`EMPLOYEE_OS_PRIMITIVES.md` §4.7).
3. **Inter-employee references already exist** as joins, not
   as a protocol. Bug Triage Specialist (Employee #4, S1267)
   reads `OpsRun` rows from the other three employees and produces
   a clustered failure-pattern report. That's the only existing
   "employee reads another employee's work" path.

---

## 3. Agent-to-Agent Flow

### 3.1 Dispatch path

Two paths, same router:

```
Sync:    caller → AgentRouter.route(name, task, context)
                  → BaseAgent.execute(task, context)
                  → AgentResult
Async:   caller → AgentExecution.objects.create(status='pending')
                  → execute_agent.delay(execution_id)
                  → AgentRouter.route(..., existing_execution_record=row)
                  → BaseAgent.execute(...)
                  → execution.mark_completed(result=...)
```

Evidence: `core/agent_router.py:836-945` (sync), `core/tasks_agents.py:494-780` (async).

### 3.2 Delegation (sub-agent)

`BaseAgent.delegate_to_agent()` is the canonical "agent A invokes
agent B" path. Recursion guard at depth=3 (`max_depth = 3`,
`core/agents/base_agent.py:905-913`). Same-agent (A→A) detection
is **not** explicit — depth cap is the only guard.

### 3.3 Lineage

`AgentExecution` carries three lineage fields:

- `trace_id` (`models_unified_system.py:906`) — links execution
  to a broader workflow (Session 843).
- `parent_execution_id` (`models_unified_system.py:967`) —
  immediate parent (Session 1098 PR #4).
- `root_execution_id` (`models_unified_system.py:968`) —
  top-of-tree ancestor for cancel-propagation.

Resolution at `core/agent_router.py:2866-2942`. Every execution
can walk back to root; cancel + budget checks use this chain.

### 3.4 Heartbeat + cleanup

Daemon thread updates `AgentExecution.last_heartbeat_at` every
30s (`agent_router.py:2945-2980`, Session 1083). Cleanup beat
(Session 1100) marks executions with no heartbeat for 60 min as
failed. Pre-fix evidence: `ResearchAgent` had 0/11 success on
long-running calls; post-fix lineage is healthy.

### 3.5 Workspace-aware sub-class

20 agents in `WORKSPACE_AWARE_AGENTS` constant
(`core/epa_handlers_tools.py:3873-3907`). When called with
`workspace_id`, they route through
`execute_with_workspace(...)` instead of `execute()`
(`core/epa_handlers_tools.py:3909-3920`).

### 3.6 Multi-agent conversations

`core/conversation_orchestrator.py` runs structured turn-flows
(lines 60-107: analytical / creative / debate / planning /
critique / general). ConversationState tracks tension_count,
empty_agreement_count, question_count vs. substantive_count
(lines 110-130). DecisionEnforcerAgent forces decision at
`_enforce_decision_via_enforcer()` (lines 1556-1562).

**UNKNOWN.** No explicit global `max_turns` constant found in
`conversation_orchestrator.py`. Termination appears to be
driven by (a) TURN_FLOWS implicit 4-8 turn patterns, (b)
per-agent Celery timeouts, (c) parent-execution cancel
propagation from Session 1098 PR #4.

### 3.7 Result envelope (Workflow agent)

`WorkflowOrchestrationAgent._compile_final_result()` returns
`result['steps']`, **not** `result['step_results']`, and does
**not** expose `result['context']`
(`feedback_workflow_result_steps_not_step_results.md`; closed
PR #2609 S1234). Anything assuming the older key gets silent
empty defaults. Pattern is canonical for orchestrator-style
agents — see `narrative_drift_coordinator.py:1280-1320` for the
same shape.

---

## 4. PA / Chat Flow

### 4.1 End-to-end path

```
client → POST /api/pa/chat/                            (views_personal_assistant.py:267-504)
       → process_pa_chat_task.delay(...)               (tasks.py:11907)
       → UnifiedPAEntrypoint().process(...)            (unified_pa_entrypoint.py)
       → ToolDispatcher.execute(tool_name, payload)    (tool_dispatcher.py:584+)
       → handler returns ToolResult
       → AgentFollowupSubscription armed if context['auto_followup']!=False
client polls GET /api/pa/chat/status/<task_id>/        (views_personal_assistant.py:785-827)
       ↳ Celery AsyncResult lookup
agent terminal save fires signal → fire_agent_followup_subscriptions(execution)
       → atomic queryset update STATE_ARMED → STATE_FIRED
       → broadcast on pa_conversation_<conversation_id>
       → PAConversationConsumer.agent_completed
       → persists Rigby ChatConversation row + banner
```

### 4.2 `ChatConversation` model — what it actually carries

`core/models/conversations/models.py:59-251`. Highlights:

- `source` enum (line 89-95): `web`, `mobile`, `discord`, `api`,
  `claude-code`, `pa`. **`source='claude-code'` routes the
  message to intent `claude_code_coordination`**, which (per
  audit) skips the standard function-calling enrichment path.
- `workspace` FK (line 146-154) — set when conversation is
  opened from a workspace; otherwise null.
- `agents_used` (JSONField, line 166) + `agent_results`
  (JSONField, line 167) — denormalized snapshots from the turn.
- Discord triple (`discord_user_id`, `discord_channel_id`,
  `discord_guild_id`, lines 113-131).

### 4.3 Pinning + rotation

- Pinned conversation is configured per session by Rigby via
  `session_tool.create_fresh` (`core/services/td_handlers_core.py:3881-3928`).
- Carry-forward: `payload['carry_forward_summary']`, falls back
  to `session_health_service.get_session_health(old).starter_prompt`.
- Pre-S1247 bug: carry-forward was always empty because lookup
  read `self._current_conversation_id` which is never assigned
  anywhere — fixed S1247.

### 4.4 Tool-dispatch contract

`tool_dispatcher.py:584-650+` defines `async execute(...)
-> ToolResult`. `ToolResult` (lines 162-174) carries `ok`,
`tool`, `latency_ms`, `error_code`, `error_message`,
`trace_id`, `result`. Structured error codes (lines 152-159):
`TOOL_NOT_FOUND`, `TOOL_TIMEOUT`, `TOOL_EXCEPTION`,
`TOOL_INVALID_PAYLOAD`, `TOOL_PERMISSION_DENIED`,
`TOOL_DEPENDENCY_FAILED`, `AGENT_EXECUTION_FAILED`.

156 handlers vs. 119 schemas — **delta is 37 handlers
without an explicit LLM-callable schema.** Likely a mix of
internal-only handlers and removed-but-still-registered
aliases (`REMOVED_TOOL_ALIASES`, lines 210-229). Explicit
schema/handler reconciliation is UNKNOWN here; flagged in §9.

### 4.5 Banner pipeline — `AgentFollowupSubscription`

Model: `core/models_unified_system.py:1017-1116`.

- States: `armed`, `fired`, `expired`, `cancelled`. STATE_ARMED at line 1044; STATE_FIRED at 1045.
- Arming: `tasks_agents.py:232-280` creates a subscription right
  after `AgentExecution.create`, gated on `context.get('auto_followup', True)`.
  `unique_together = [('execution', 'conversation_id')]` dedups.
- Firing: `tasks_agents.py:336-490` atomic update fires the
  subscription on terminal-state save; broadcast lands in
  `pa_conversation_<conversation_id>` channel.
- **Known suppression vector:** `context['auto_followup']=False`
  on the dispatch suppresses the banner (line 263). Rigby
  inherited this on `run_agent` to avoid completion banners on
  forensic dispatches; same flag silently kills banners in
  normal flows if mis-set
  (`feedback_auto_followup_false_suppresses_banner.md`).

### 4.6 `claude_code_tool` receipt path

`core/services/td_handlers_codejobs.py:330-378`. Dispatches
`claude_code_engineer_task.delay(...)` and returns
`{status: 'dispatched', task_id, request_mode, message}`.
S1262 PR #2752 closed the receipt gap:

- Now creates `AgentExecution` row at task entry (was
  on-completion).
- Wires S1174 follow-up wake stack (was never wired).
- `_post_to_conversation` is fail-loud (was silent on error).
- `output_data['post_back_status']='failed'` + `record.status='failed'` are the late-binding markers if post-back ever fails.

### 4.7 Source-based intent gates

- `source='claude-code'` → intent `claude_code_coordination`,
  short-circuits the standard enrichment fan-out. Tools still
  callable; just no enrichment-services bundle is injected.
- Pre-S1249 bug (`tools/pa_chat.py:38`): bare CLI invocation
  defaulted to PROD. S1249 PR #2712 flipped default to local;
  `--env prod` opts in. The `PA_API_TOKEN` in `.env` is still
  the prod token — local invocation needs explicit override
  (`tools/pa_local.sh` is the wrapper).

### 4.8 Worker config

```
Procfile:26   celery-pa: ... -c 1 --max-tasks-per-child=10
                         --max-memory-per-child=200000 -Q pa
```

PA queue is isolated. Concurrency=1 (serial); 200MB child cap;
10-task recycle (Session 1068 — enrichment caused 4GB
spikes at higher concurrency). `PA_USE_FUNCTION_CALLING=true`
must be set in the worker env or `source='claude-code'`
messages text-respond without tool dispatch
(`feedback_pa_worker_function_calling_env.md`).

---

## 5. Employee OS Communication Surfaces

### 5.1 What an employee actually emits

Per mission, in evidence-only terms:

| Surface | Where | When | Bounded |
|---|---|---|---|
| `OpsRun(domain='mission')` row | `core/models_ops_runs.py:11-89` | One per mission day (daily idempotency, `mission_runner.py:100`) | Yes |
| `OpsRunEvent` rows | `core/models_ops_runs.py:91-118` | Per step boundary; verdict; escalation; `authority_contract_observed` | Yes (label + detail JSON) |
| `Deliverable` (escalation) | `core/models_deliverables.py:84-283` | On step failure, gated by 24h dedupe window | Yes; full error tail goes here |
| `DeliverableEvent(event_type='status_transition')` | `core/models_deliverables.py:561-610` | When MissionRunner flips completed→ready | Yes |
| `DirectMessage` (shift report) | `core/employees/comms.py:228-367` | One per terminal mission per persistent (employee, job) thread | Yes; metadata bounded — NEVER full error tail (`EMPLOYEE_OS_PRIMITIVES.md` §4.5) |
| `LLMCallEvent` + `ToolCallRecord` | `core/models_llm_telemetry.py`, `core/models_tool_calls.py` | During mission steps | Yes |
| **PA-chat post (optional)** | Via `pa_post_fn` hook in MissionRunner | On escalation only; only if employee has `primary_chat_id` set | Yes |

### 5.2 What an employee does NOT do today

- **Employees do not send messages to each other.** There is no
  active "send-to-employee" handler. `messaging_tool.send_message`
  is gated OFF by `settings.MESSAGING_TOOL_ALLOW_SEND`
  (`EMPLOYEE_OS_PRIMITIVES.md` row 20 + §4.7).
- **No employee-to-employee dispatch primitive.** `employee_tool
  action=run_now` is Rigby-gated (the caller's user_id must
  resolve to `runs_as_username`); it's a Rigby/operator surface,
  not an inter-employee surface.
- **No shared scratch / blackboard.** Mission data flows via
  `OpsRun.summary` (JSONField) + escalation `Deliverable` —
  read by downstream consumers; never modified by them.
- **No "mission output → next mission input" handoff
  protocol.** The single existing composition pattern is Bug
  Triage Specialist (Employee #4, jobs.py:972-1322) reading
  OpsRun rows from the other three employees as evidence.

### 5.3 MissionRunner lifecycle (per `mission_runner.py:1-230`)

```
1.  get_or_create OpsRun(domain='mission', run_kind=...)    (daily idempotency)
2.  emit run_started (event_type='info')
3.  [opt] emit authority_contract_observed                  (warn-mode, S1264 lines 264-894)
4.  [opt] preflight_fn(summary_acc)
5.  For each Step:
        emit <step>_started → fn(mission) → emit <step>_passed | <step>_failed
        (on first failure: emit remaining as <step>_skipped)
6.  [opt] postflight_fn(PostflightContext)                  (PR 1.3 dual-sig dispatch)
7.  [on failure] Escalation:
        - dedupe check (failed_step + error_signature, 24h window)
        - create or append-to-prior Deliverable
        - force status completed→ready (audit transition)
        - [opt] pa_post_fn (chat escalation)
        - emit escalation_emitted
8.  [opt] shift_report_fn(mission) → post_shift_report DM
9.  [conditional] emit_mission_verdict(...)
        - default: auto-emit on success
        - S1267 Bug Triage: auto_emit_verdict=False, runner skips, Rigby/human emits via PA tool
10. return MissionRunResult envelope
```

### 5.4 `_persist_to_summary()` — shared write helper

`core/employees/_persistence.py:36-59` (lifted from
docs/morning-brief/audit job modules in S1267 PR 4.0).
Steps merge job-specific keys into `OpsRun.summary` atomically;
MissionRunner later merges runner-level keys without
overwriting step keys (no nested envelope, per Rigby
S1257 SIGN-WITH-EDITS lock #2).

### 5.5 Authority contract observation

`mission_runner.py:264-894`. Emits one
`authority_contract_observed` OpsRunEvent per mission with
detail: schema_version=1, employee_handle, contract_title,
contract_version_tag (16-char SHA-256 of sorted authority +
prohibited_actions), authority_entries_total,
authority_level_counts (execute/observe/recommend/prohibited
counts), prohibited_actions_count, mode='warn'.

**Status: warn-mode only — never blocks.** Malformed
contracts log ERROR and set `degraded_evidence=True` but the
mission continues. No symbol mapping yet; no actual violation
detection. `JobContract.authority` is *advisory*, not
enforced.

**Rigby S1268 review clarification on scope.** S1264 warn-mode
was **not** scoped as "single-employee only." It is defined as
observational telemetry that **never blocks any mission**
(`core/employees/mission_runner.py:258-275`, comments + the
`_AuthorityContractMalformedError` handling). Implication for
this audit: cross-employee actions *can* be observed under the
same warn-mode event today, but **enforcement semantics are
not present yet**. Any inter-employee write path is the first
real test of whether warn must flip to enforce.

### 5.6 The four current employees

| # | Employee | jobs.py lines | primary_chat_id | mission_run_kind | Note |
|---|---|---|---|---|---|
| 1 | RIGBY (Documentation Manager) | 167-382 | `pa-3901b70e61934df7` | `docs_cascade` | Production S1253+ |
| 2 | PLATFORM_AUDITOR | 388-656 | `None` | `platform_audit` | S1257 PR 2.1+; reports via Deliverable + DM |
| 3 | CHIEF_OF_STAFF | 662-966 | `None` | `morning_brief` | S1257 PR 3.1+; brief itself is the visibility |
| 4 | BUG_TRIAGE_SPECIALIST | 972-1322 | `None` | `bug_triage_daily` | S1267 PR 4.1+; `auto_emit_verdict=False` (line 1048-1050) |

**CLAUDE.md drift note.** CLAUDE.md still says 3 employees in
the Detailed Breakdown row. Code says 4
(`_EMPLOYEES_BY_HANDLE` at `jobs.py:1327` has four entries
incl. `BUG_TRIAGE_SPECIALIST`). Inventory wins per
`DOC_LIFECYCLE.md` §2c — flagged for S1268 doc cleanup.

---

## 6. Auditability and Evidence

### 6.1 Five evidence tables, one correlation key

Across the agent + employee + PA layers there are five audit
tables. The correlation key in the employee layer is
`OpsRun.mission_id`.

| Table | File | Joins to mission via |
|---|---|---|
| `OpsRun` | `core/models_ops_runs.py:11-89` | self (id) |
| `OpsRunEvent` | `core/models_ops_runs.py:91-118` | FK `run_id` |
| `LLMCallEvent` | `core/models_llm_telemetry.py` | `metadata.ops_run_id` (loose join) + `execution_id` (FK to AgentExecution) |
| `ToolCallRecord` | `core/models_tool_calls.py:19-150` | `parameters.ops_run_id` (loose join) + `trace_id` |
| `AgentExecution` | `core/models_unified_system.py:875-980` | `trace_id` + `parent_execution_id` + `root_execution_id` |
| `Deliverable` + `DeliverableEvent` | `core/models_deliverables.py` | `ctx.ops_run_id` in DeliverableEvent.metadata |
| `CeleryTaskEvent` | `core/models_celery_telemetry.py` | `task_name` + `agent_name` dimension; no direct mission link today |
| `ChatConversation` | `core/models/conversations/models.py:59-251` | `conversation_id` only; PA-post escalation is correlated only via `metadata` |

### 6.2 `evidence_for_mission()` is the canonical join

`core/employees/status.py:347-508` (also exposed via
`employee_tool action=evidence_for_mission`). Joins OpsRun +
OpsRunEvent + Deliverable + DeliverableEvent + ChatConversation
+ LLMCallEvent + ToolCallRecord. Returns either a 30-line
error_tail preview (default) or full tail (verbose=True).

This is **already** the answer to "given a mission, what did
the employee actually do." Any future employee-to-employee
collaboration design should not invent a parallel evidence
join — extend this one.

### 6.3 Telemetry contract: best-effort, never masks

`core/services/llm_call_wrapper.py:26-28`: "Telemetry save must
never mask the real LLM response or exception." This is the
fail-loud-first principle in code form. Any new layer that
records inter-employee traffic must inherit the same contract.

### 6.4 ChatConversation has no post_save signal

`core/consumers_pa_conversation.py:128`: "ChatConversation has
zero post_save signals, so turns are NOT automatically
persisted to the chat log on save." Logging is *implicit via
assignment*. A future collab layer that wants automatic
audit-on-write cannot rely on a signal here without adding
one.

---

## 7. Known Risks and Failure Modes

Each row below is a documented incident with an active or
deferred mitigation. Relevance scoring is for future
employee-to-employee collaboration design.

### 7.1 Receipt-chain gap

- **Pattern.** Dispatcher tool returns `task_id` but no
  `AgentExecution` row is created at task entry; if the task
  later fails before posting back, the conversation has no
  receipt to follow up on.
- **Specific instance.** `claude_code_tool` — closed by S1262
  PR #2752. `AgentExecution` row now created at task entry;
  post-back failures populate `post_back_status='failed'` and
  flip the execution to status='failed'.
- **Generalization (memory note).** Filed as
  `project_employee_os_ux_gap_task_receipts.md`. Any new
  dispatch surface inherits this risk unless the receipt is
  wired before execution.
- **Relevance: HIGH** for inter-employee dispatch. Trust between
  employees presumes "did the work start?" is verifiable.

### 7.2 Procfile ↔ Makefile queue parity drift

- **Pattern.** New queue declared in `app.conf.task_routes` but
  worker fleet not updated (Procfile or Makefile, or both).
  Dispatched tasks sit in Redis with zero telemetry (no
  CeleryTaskEvent row), no error — silent stall.
- **Specific instance.** `claude_code_tool` routed to
  `code_jobs` queue; Procfile had `code-worker -Q code_jobs`
  but Makefile didn't — every local dispatch silently
  queued forever for months. Fixed S1226 PR #2552/#2553.
- **Canary.** S1244 PR #2687 added
  `core/tests/test_celery_queue_parity.py` (3 assertions
  checking declared ↔ Procfile ↔ Makefile parity in both
  directions).
- **Relevance: P1 CRITICAL.** Any new collab queue must
  go through the same parity check.

### 7.3 LLM autofills optional bool/int params

- **Pattern.** GPT-5.2 in function-calling mode autofills
  declared optional booleans with `False` and integers with
  `0` when the user didn't ask for them. Handlers using
  `if x is not None:` checks silently apply the
  filter/limit.
- **Specific instances.** `deliverable_tool.list` with
  `has_initiative=False` autofill returned 180 of 300 rows
  for months (S1227). `deliverable_tool.duplicates` with
  `limit=0` returned nothing (S1227).
- **Memory note.**
  `feedback_llm_autofills_boolean_params_with_false.md`.
  Sweep landed S1228 across `content_tool`, `work_tool`,
  `initiative_tool`, `governance_tool`.
- **Relevance: HIGH.** Any employee-callable tool with
  optional params must use truthy-only or
  falsy-or-default checks, not `is not None`.

### 7.4 `auto_followup=False` suppresses banner silently

- **Pattern.** When `context['auto_followup']=False`, no
  `AgentFollowupSubscription` row is armed; the terminal-save
  signal has nothing to fire; no banner reaches the chat UI.
- **Specific incidence.** S1184 lost ~30 min hunting WS /
  daphne / consumer for a "missing banner" report; the cause
  was a Rigby-side `auto_followup=False` on the forensic
  dispatch.
- **Memory.** `feedback_auto_followup_false_suppresses_banner.md`.
- **Relevance: MEDIUM.** Default is True; only matters
  for explicit opt-out paths. If employee-to-employee
  protocol ever sets `auto_followup=False`, it loses the
  banner without notice.

### 7.5 Placeholder-stall pattern

- **Pattern.** Rigby (or another agent) writes a 4-part
  scaffold and marks `Deliverable.status='completed'`
  without actually filling sections. Looks done in UI;
  contains no substance.
- **Memory.** `feedback_rigby_deliverable_content.md`,
  `feedback_verifier_loop_pattern.md`.
- **Workflow mitigation (already in CLAUDE.md).** Claude
  directs → Rigby executes → Claude verifies (via ORM /
  file read / build). Quantitative claims and file paths
  re-verified before they ship.
- **Relevance: HIGH.** Inter-employee collab amplifies this
  risk because the consumer employee may treat upstream
  `status='completed'` as "content is real."

### 7.6 Result-key contract drift

- **Pattern.** `WorkflowOrchestrationAgent` returns
  `result['steps']`. Callers expecting `result['step_results']`
  or `result['context']` get silent empty defaults; downstream
  introspection sees None on every field; no exception.
- **Memory.** `feedback_workflow_result_steps_not_step_results.md`.
- **Relevance: HIGH.** Any inter-employee protocol that
  passes structured results between mission steps inherits
  this risk if there's no schema enforcement on the result
  dict.

### 7.7 `context['user']` is profile dict, not User instance

- **Pattern.** Lane handlers serialize user profile into
  `context['user']` for prompt injection. Downstream code
  doing `Deliverable.user = context.get('user') or
  getattr(self, 'user', None)` short-circuits on the truthy
  dict; Django raises "must be a UnifiedUser instance."
- **Closed.** S1234 PR #2608.
- **Memory.** `feedback_context_user_is_profile_dict_not_user_instance.md`.
- **Relevance: MEDIUM.** Cross-employee context-passing
  inherits the same risk if a profile dict is reused as a
  FK source.

### 7.8 `deliverable_tool` gotchas

- `update` above ~6kB silently falls back to `list` (S1176).
  Workaround: `append` for large payloads.
- `update status=completed` silently ignores status field;
  use `content_tool action=content_complete` (S1184).
- `create` defaults new rows to `status='completed'` even when
  caller passes `status='draft'` (S1241). Workaround: follow
  `create` with `set_status to_status=ready`.
- **Memories.** `feedback_deliverable_tool_use_append_for_large_payloads.md`,
  `feedback_deliverable_status_via_content_complete.md`,
  `feedback_deliverable_create_defaults_to_completed.md`.
- **Relevance: MEDIUM.** Any inter-employee collab that
  writes to deliverables inherits these.

### 7.9 macOS Celery stall (mutex.cc) + sys.modules cache

- **Pattern.** Darwin fork-safety on Objective-C locks
  deadlocks prefork workers when ML modules load at module
  level. `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` + `--pool=solo`
  or `threads` is the workaround.
- **sys.modules.** Prefork workers inherit module cache;
  code edits don't take effect until full worker restart.
  `rm -f .celery*.pid; make celery` is the canonical restart.
- **Relevance: LOW for production (Linux), MEDIUM for local
  dev.** Affects iteration speed, not correctness.

### 7.10 PA worker "consume-1-then-hang" — disk pressure

- **Pattern.** PA worker processes one task, returns silent.
  Symptom is Celery hang; root cause is OS-level disk/swap
  pressure blocking subsequent task I/O.
- **Memory.** `feedback_pa_hang_from_disk_pressure.md`.
  Diagnostic: `df -h /System/Volumes/Data` +
  `sysctl vm.swapusage` BEFORE deeper Celery debugging.
  Do **not** restart Docker (unified-postgres lives there).
- **Relevance: LOW.** Infrastructure issue; not a
  collaboration-design constraint.

### 7.11 Noise-task drift (PeriodicTasks 305 → 92)

- **Pattern.** Beat schedules accreted as features came and
  went; 305 PeriodicTask rows before S1157 cleanup; 92 after.
- **Memory.** "Agent noise rule" + S1115 multi-batch audit;
  `docs/AUDIT_FINDINGS.md` §12 is the canonical Celery
  deferred-by-policy list.
- **Relevance: MEDIUM.** If employee collaboration ever
  spawns recurring schedules, the same accretion can recur.

### 7.12 Fleet-caller blind spot (cross-app)

- **Pattern.** Local-DB-only verdicts before deleting Celery
  surfaces may miss prod-only callers in sibling fleet
  apps (`donkey_betz_platform`, character-os, etc.).
- **Memory.** `feedback_fleet_caller_verification_before_celery_deletes.md`.
- **Relevance: LOW unless** the future protocol crosses
  fleet boundaries.

---

## 8. Reuse Classification Table

Classifications below are research proposals, **not
decisions**. The scale:

- **SAFE TO REUSE** — primitive exists, contract is honored
  across callers, no architectural change needed.
- **REUSE WITH WRAPPER** — primitive exists but exposes
  rough edges (silent failures, optional-param autofill, etc.)
  that a wrapper should bound.
- **DO NOT USE DIRECTLY** — primitive exists but the failure
  mode is severe enough that any inter-employee use should
  go through a deliberate intermediary.
- **DEPRECATED / LEGACY** — primitive is in the codebase but
  superseded; not recommended.
- **UNKNOWN** — could not verify in the budget allocated.

| Primitive | Class | Rationale |
|---|---|---|
| `OpsRun(domain='mission')` | **SAFE TO REUSE** | Already the canonical mission identity. S1250 PR 3 added mission-domain fields specifically to avoid a separate model. |
| `OpsRunEvent` | **SAFE TO REUSE** | Idempotent on (run, label). Cross-mission queries already work (e.g., `label='authority_contract_observed'`). |
| `emit_mission_verdict()` | **SAFE TO REUSE** | Idempotent on (mission, verdict). Already used by 3 employees + 1 opt-out path. |
| `post_shift_report()` | **SAFE TO REUSE** | Bounded metadata, persistent (employee, job) thread, idempotent on (thread, mission_id). Sole programmatic outbound channel for employees today. |
| `DirectMessage` + `MessageThread` + `ThreadParticipant` | **SAFE TO REUSE** | Already the substrate for shift reports; metadata-keyed lookup supports any (employee, employee, topic) addressing scheme. |
| `Deliverable` + `DeliverableEvent` | **SAFE TO REUSE** | Established escalation surface; status-transition events carry `ctx.ops_run_id` for cross-employee correlation. |
| `HumanAttentionItem` | **SAFE TO REUSE** | When inter-employee work needs human gating, this is the funnel. |
| `LLMCallEvent` + `ToolCallRecord` + `CeleryTaskEvent` | **SAFE TO REUSE** | Telemetry layer. Best-effort contract — never masks the call. |
| `AgentExecution` (trace_id, parent_execution_id, root_execution_id) | **SAFE TO REUSE** | Lineage fields already support cross-employee dispatch chains. Cancel propagation walks the root chain. |
| `_persist_to_summary()` | **SAFE TO REUSE** | Shared atomic write helper — exactly the right granularity. |
| `evidence_for_mission()` (read API) | **SAFE TO REUSE** | The 7-table join. Extend, don't duplicate. |
| `AgentRouter.route()` (sync) | **REUSE WITH WRAPPER** | Recursion guard is depth-based (max=3), not same-agent. Inter-employee dispatch is "agent-to-agent" — a thin wrapper that tags the call with the employee handle (not just agent name) would let evidence joins find it without re-walking AgentExecution lineage manually. |
| `BaseAgent.delegate_to_agent()` | **REUSE WITH WRAPPER** | Depth-3 cap is sound; explicit same-agent (A→A) guard absent. Wrapper or assertion at the inter-employee boundary would close this. |
| `AgentFollowupSubscription` | **REUSE WITH WRAPPER** | Silent banner suppression on `auto_followup=False` is the footgun. Wrapper that always arms unless explicitly opted out at the *employee level* (not per-call) avoids the S1184 class. |
| `ChatConversation` (per-employee primary_chat_id) | **REUSE WITH WRAPPER** | 4-of-4 employees can have a pinned conversation, but only Rigby uses it. If inter-employee comms ever surface in chat, the wrapper needs to suppress noise or route through `HumanAttentionItem` instead. |
| `tool_dispatcher.execute()` | **REUSE WITH WRAPPER** | ToolResult is well-shaped, but error_code coverage is partial across handlers. Wrapper that asserts on missing fields gives the receiving employee a stable contract. |
| `EventBus` (Redis Streams) | **REUSE WITH WRAPPER** | Already has DLQ. Naming + consumer-group discipline is the wrapper's job. Suitable for high-frequency notifications; **not** for receipts where Celery + AgentExecution is the right tool. |
| `conversation_orchestrator` (multi-agent turns) | **DO NOT USE DIRECTLY** for employee-to-employee | Built for analyst-style multi-agent debate inside a single conversation. Repurposing it as an inter-employee protocol would conflate "deliberation" (its job) with "mission delegation" (employee-to-employee). Keep separate. |
| `messaging_tool.send_message` (with `MESSAGING_TOOL_ALLOW_SEND=True`) | **DO NOT USE DIRECTLY** | `EMPLOYEE_OS_PRIMITIVES.md` §4.7 explicitly OFFs this. Free-form LLM outbound is the wrong tool for structured inter-employee messages. `post_shift_report()` is the right tool; if a new bounded channel is needed, write a thin helper like `comms_<job>.py`. |
| `claude_code_tool` dispatch pattern | **DO NOT USE DIRECTLY** as a template | The receipt-chain gap (S1262) is closed but the pattern is fragile: if a future inter-employee dispatch copies it without copying the AgentExecution-at-entry fix, the gap recurs silently. |
| Any new `EmployeeMessage` / `EmployeeNotification` / `ShiftReport` / `EmployeeAuditLog` model | **DEPRECATED before it exists** | `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1 name these as anti-patterns. Existing primitives cover all of these surfaces. |
| Inter-employee dispatch action on `employee_tool` | **UNKNOWN** | Today `employee_tool action=run_now` is Rigby-gated by user_id. An inter-employee action would need a service-token / employee-handle auth model that does not yet exist. Flagged in §9. |
| Shared scratch / blackboard model | **UNKNOWN** | No such primitive exists today. Whether one is needed at all is an open question — `OpsRun.summary` + `Deliverable.content` + DM metadata may already be sufficient. Flagged in §9. |
| `JobContract.authority` enforcement (vs. warn-mode observation) | **UNKNOWN** | Today it's *observed*, not enforced (`mission_runner.py:264-894`). Whether the warn-mode event is sufficient telemetry for cross-employee actions is an open question. |

---

## 9. Open Questions Before Designing Employee Collaboration

The questions below are intended to be routed through Rigby
+ Chris before any design work starts.

1. **Is there a problem to solve?** Bug Triage Specialist
   reads OpsRun rows from the other three employees today
   (read-only composition). Is there a *write* path that's
   actually needed (employee A produces input → employee B
   consumes it as a job step), or is read-only composition
   the right ceiling for v0?

2. **If write-direction is needed, what does an
   inter-employee dispatch look like?** Specifically:
   - Does it go through `employee_tool action=<new>` (Rigby
     gateway) or through a new service-token surface?
   - Does it create a fresh `OpsRun` for the downstream
     employee, or attach as a step in the upstream mission?
   - How does authority interact? Today
     `authority_contract_observed` is warn-mode only.

3. **What's the receipt contract for inter-employee
   dispatch?** Given the `claude_code_tool` history
   (S1262), any new dispatch must (a) create
   `AgentExecution` at entry, (b) wire follow-up wake,
   (c) be fail-loud on post-back. Should this be enforced
   by a shared dispatcher helper rather than a per-employee
   convention?

4. **Should authority shift from warn to enforce before any
   inter-employee write path lands?** Today `JobContract.authority`
   is *advisory*. Inter-employee dispatch is the first
   case where the *caller* employee is acting on the
   *callee* employee's behalf — that asymmetry is what
   authority levels exist for. **Rigby S1268 review answer:**
   her S1264 warn-mode design was scoped as observational
   telemetry that *never* blocks any mission, single-employee
   or cross-employee. So warn-mode covers cross-employee
   observability today; **enforcement** semantics are still
   absent. The open question becomes: is the first
   inter-employee write path also the trigger to land
   enforcement (warn → enforce), or do we ship the protocol
   under warn first and add enforcement separately?

5. **How does the existing `LLM autofills False/0` risk
   apply to new optional params on an inter-employee tool?**
   If the LLM driving employee A autofills an optional
   `priority`, `wait_for_result`, `force` boolean — what's
   the safe default?

6. **What is the visibility model for Chris?**
   `feedback_chris_discoverability_visibility.md`: every
   in-flight build that needs Chris's attention must
   surface as a deliverable. Should inter-employee dispatch
   chains surface as a single combined Deliverable, one per
   employee, or one per "conversation"? `evidence_for_mission()`
   today returns one mission's evidence — what's the
   equivalent for a multi-mission collaboration?

7. **Does an inter-employee protocol need to cross fleet
   boundaries?** Today's four employees all run inside
   `donkey-betz`. If a future employee lives in
   `character-os` or another fleet app, the queue parity +
   fleet-caller verification rules (§7.2, §7.12) apply.

8. **Is `EventBus` (Redis Streams) the right substrate for
   inter-employee notifications, or only for low-stakes
   telemetry?** It already has a DLQ. But for receipts that
   must survive worker restart and need replayability,
   `OpsRunEvent` is sturdier. Confirm placement before
   building.

9. **What's the dedupe surface for inter-employee
   conversations?** MissionRunner dedupes failures by
   (failed_step + error_signature, 24h). Per memory rule
   (`feedback_audit_findings_12_canonical_celery_deferred_list.md`),
   deferred-by-policy task lists need a canonical entry.
   An inter-employee message bus needs the same: a single
   table or convention that says "this is the dedupe key."

10. **Schema/handler count drift on PA tools (156 vs.
    119).** Before adding any inter-employee tool, the
    handler/schema reconciliation should be either fixed
    or explicitly classified (internal-only vs.
    LLM-callable). Otherwise adding a 157th handler
    perpetuates the drift.

---

## 10. Recommended Next Research Step

This audit is research only. Rigby's S1268 independent review
narrowed three of the §9 questions to concrete next steps. The
recommended next research step is **scoping the first
inter-employee write candidate**:

- **Named candidate (Rigby S1268).** Platform Auditor →
  (Rigby and/or Chief of Staff) **structured DM /
  action-request** via an *allowlisted comms helper* in the
  shape of `post_shift_report()` — explicitly **not**
  `messaging_tool.send_message` (which is OFF by design,
  `td_handlers_core.py:3694-3711`). The pattern would mirror
  `core/employees/comms_docs_manager.py:39-122` — a thin
  job-specific wrapper that calls the generic
  `post_shift_report()` with a bounded set of metadata keys.
- **Higher-risk candidate to defer.** Bug Triage
  creating/altering governance items or
  `HumanAttentionItem` rows — needs an inter-employee
  authority model first; revisit only after warn-mode flips
  to enforce or after a deliberate per-action carve-out.
- **Open scope questions to route through Rigby + Chris
  before any sketch:**
  1. Does the Platform Auditor → Chief of Staff message
     need to *trigger* downstream work (i.e., it shows up
     in the Chief of Staff's morning brief as a recognized
     input), or is "DM in the inbox" sufficient v0?
  2. Does the inter-employee DM get its own thread per
     (sender, recipient, topic), or does it ride the
     existing per-(employee, job) shift-report thread? The
     metadata-keyed lookup in `MessageThread` already
     supports both shapes (`EMPLOYEE_OS_PRIMITIVES.md`
     row 10).
  3. Does the receiving employee respond via the same
     thread (round-trip), or is v0 strictly fire-and-forget?
- **Output of next step.** A short protocol sketch doc
  (`employee_os_communication_protocol_sketch.md`) for a
  Platform-Auditor-→-Chief-of-Staff allowlisted DM, with
  reuse claims tied directly to §8's SAFE-TO-REUSE rows
  and explicit "do NOT build" callouts to
  `EMPLOYEE_OS_PRIMITIVES.md` §2. **Still no PR. Still no
  model. Still no schema for `messaging_tool.send_message`.**
  Design only after Chris signs off on the candidate scope.

Rigby's review is on PA-chat thread
`pa-01e90a1d36f54880` (S1268 fresh pin).

---

## Appendix A — Evidence integrity notes

- Five parallel Explore sub-agents produced the source
  material for §3–§7 (`agent-to-agent`, `PA chat`, `Employee
  OS comms`, `governance/safety`, `failure history`).
- Load-bearing file:line citations were re-verified by Claude
  with direct `Grep`/`Read` before this doc was written:
  - `core/employees/jobs.py:1327` (`_EMPLOYEES_BY_HANDLE`)
  - `core/employees/jobs.py:972` (`BUG_TRIAGE_SPECIALIST` =
    Employee #4, NOT in CLAUDE.md's 3-employee table)
  - `core/employees/mission_runner.py:529` (`MissionRunnerConfig`)
  - `core/employees/mission_runner.py:589` (`auto_emit_verdict` field)
  - `core/employees/mission_runner.py:595` (`MissionRunner`)
  - `core/employees/comms.py:228` (`post_shift_report`)
  - `core/employees/_persistence.py:36` (`_persist_to_summary`)
  - `core/models_unified_system.py:1017` (`AgentFollowupSubscription`)
  - `core/models_unified_system.py:1044-1045` (STATE_ARMED, STATE_FIRED)
  - `core/tasks_agents.py:263` (`auto_followup` opt-out branch)
  - `docs/EMPLOYEE_OS_PRIMITIVES.md:1-80` (anti-duplication matrix
    + canonical primitives table)
- Rigby's S1268 additions were re-verified by Claude:
  - `core/services/td_handlers_core.py:3710` (`MESSAGING_SEND_DISABLED`)
  - `core/services/td_handlers_core.py:3701` (`MESSAGING_TOOL_ALLOW_SEND`
    settings gate)
  - `core/services/td_handlers_core.py:3774-3775`
    (`_broadcast_new_message(thread, msg)` inbox hook)
- The single material drift surfaced during verification is
  **Employee count: CLAUDE.md says 3, code says 4** (Rigby
  S1268 review pinned the doc-side line at `CLAUDE.md:95-96`).
  The inventory wins per `DOC_LIFECYCLE.md` §2c. Flagged in §5.6.
