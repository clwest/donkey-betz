---
title: "Governance + Authority Evolution — Architectural Discovery (research only)"
status: draft
session: 1269
date: 2026-06-30
mission_type: architectural_discovery
authority: |
  Evidence-only audit. No runtime changes. No PRs. No migrations.
  No model definitions. No proposed implementation. No contract
  changes. This doc inventories the governance + authority surface
  that exists today, identifies what's runtime-enforced vs.
  observational vs. documentation-only, surfaces the gaps, and
  recommends the next research mission.
companion_docs:
  - docs/research/employee_os_communication_substrate_audit.md
  - docs/research/employee_os_communication_protocol_sketch.md
  - docs/research/employee_os_collaboration_patterns.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md
verifier_loop: |
  Five parallel Explore sub-agents produced evidence reports
  (authority dicts + warn-mode internals, runtime enforcement
  points, GovernanceState + KillSwitch runtime consumers, human
  governance lifecycle deeper, governance-specific failure
  history). All load-bearing claims re-verified by Claude via
  direct Grep/Read before this doc was written. One sub-agent
  drift surfaced and corrected: Bug Triage authority dict is
  RUNTIME-VERIFIED, not ASPIRATIONAL — wired at
  `core/jobs/bug_triage.py:1169`. Independent SIGN review by
  Rigby complete (S1269 PA conversation pa-01e90a1d36f54880):
  **SIGN-with-edits**. Two must-fix edits folded (Exec Summary
  plane framing made consistent with F1's "four planes"; gate
  count corrected 34→35); two clarifications folded
  (DO-NOT-REUSE-for-enforcement framing on
  JobContract.authority; F4 budget-plane intent claim
  softened per "current behavior; don't assert design intent
  without a design note"). SIGN-clean on findings F2/F3/F6/F9,
  §11 Symbol Mapping Architecture recommendation, all
  enforcement-point findings, KillSwitch write-only finding,
  authority-convergence finding, throttle-mode-dead finding,
  top-3 open question priorities (Q1>Q3>Q2 per Rigby ranking).
owner: claude (drafted S1269) + rigby (independent SIGN review, S1269)
---

# Governance + Authority Evolution — Architectural Discovery

> **What this is.** The canonical research anchor for every future
> authority or governance discussion on this platform. Built from
> direct file:line evidence + five parallel sub-agent sweeps + spot
> verification. Recommended next research mission named at §11.
>
> **What this is not.** A design. A decision. A proposal to flip
> warn-mode to enforce-mode. A plan to add models. The reuse
> classifications in §7 are research proposals; final calls happen
> in their own review cycle.

---

## 1. Executive Summary

The platform has **four governance planes** that don't compose
today (Rigby S1268 SIGN-clean on this framing):

1. **Autonomy plane** — `GovernanceState`
   (`core/models_governance.py:17-114`) + `KillSwitch`
   (`core/models_governance.py:116-189`). Used to set modes
   (normal/throttle/freeze/safe_mode) and arm emergency blocks
   (TTL-required). Read by 4 production consumers; freeze/safe_mode
   actively enforced in spiders, signal aggregation, workspace
   pipelines.
2. **Authority plane** — `JobContract.authority` dict +
   `AuthorityLevel` enum (`core/employees/jobs.py:41-52`). 68
   authority entries across 4 employees. **OBSERVATION ONLY**
   today (S1264 warn-mode). NEVER blocks any mission.
3. **Budget plane** — `SystemConfiguration` with
   `budget_freeze_active` flag (`core/llm_enforcer.py:200-260`).
   Enforced at **LLM call-time** (not task dispatch-time, which
   is what differentiates it from the autonomy plane).
   *One-way synced* from `GovernanceState`; reverse-sync absent.
4. **Human governance plane** —
   `HumanAttentionItem` (`core/models_human_interface.py:20+`),
   `HumanFeedbackRecord` (`models_human_interface.py:230-266`),
   `HumanPreference` (`models_human_interface.py:268-358`),
   `OrchestrationApprovalGate` (`core/models_orchestration.py:397-535`).
   The only round-trip pattern with learning today.

### Major Findings

**F1 — Authority is observational, not enforced.**
`JobContract.authority` is a `dict[str, str]` mapping
**policy-description strings** (e.g., `"modify_docs_files"`,
`"open_pull_request"`) to `AuthorityLevel` values. The strings
are **not runtime symbols** — no tool name, no FK method, no
function signature binds to them. The only consumer of the
authority dict is `MissionRunner._emit_authority_contract_event()`
(`mission_runner.py:835-900`), which emits shape telemetry but
never blocks. There are **zero runtime readers** that gate an
action against the dict.

**F2 — The autonomy plane is partially wired.** `GovernanceState`
has 4 active production consumers that enforce `freeze`/`safe_mode`
(skip/cancel work). `KillSwitch` has full write paths +
TTL-expiry but **zero readers that block dispatch** before
scheduler/queue/agent_family/publishing/outbound/deploys actions
execute. `throttle` mode and per-(agent/desk) scopes are also
ASPIRATIONAL — model supports them, no consumer reads them.

**F3 — Enforcement is API-layer, not contract-layer.** All 35
documented runtime gates (§4) operate at the HTTP / middleware /
DRF / tool-handler boundary. There is **no enforcement primitive
that reads `JobContract.authority` before dispatching an
action.** The 4 AuthorityLevel members (OBSERVE / RECOMMEND /
EXECUTE / PROHIBITED) carry policy meaning in docs and contract
review; they don't carry runtime meaning yet.

**F4 — Two prerequisites block warn → enforce.** Per S1264
discovery (`handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`):
prereq #1 is **symbol mapping** (steps declare
`action_classes_invoked` OR tools carry an `action_class`
attribute mapping to the dict keys); prereq #2 is **≥14 days
clean telemetry on N≥4 employees**. Symbol mapping is the
hard blocker — it's a foundational design effort, not a beat
schedule.

**F5 — Human governance is the only round-trip with learning.**
HAI → human decision → HumanFeedbackRecord → FeedbackProcessor
signal handler → AgentLearning / LearningInsight / SharedKnowledge
is the only autonomous control loop today where machine action
gets graded by a human and the grade trains downstream behavior.
Employee → Employee authority *propagation* has no precedent here.

**F6 — Most governance UI controls exist as PA tools, not admin
endpoints.** `governance_tool` (`pa_tool_schemas.py:3157-3219`)
exposes `governance_status`, `governance_set_mode`,
`governance_kill_switch`, `governance_deactivate_switch`,
`governance_throttle_report`, `governance_audit`. The actual
Django admin gates only the `/api/v1/admin/` paths (`auth_middleware.py:610-614`)
with `is_staff` checks — there's no admin form for the autonomy
plane.

### Overall Recommendation

**The next research mission is not "design enforcement mode."**
It is **"Symbol Mapping Architecture"** — research-only — that
scopes the smallest viable mapping primitive between
`JobContract.authority` policy strings and runtime symbols. Without
that, enforcement is impossible regardless of any other
infrastructure. See §11.

---

## 2. Governance Primitive Inventory

Every governance-related primitive on the platform, organized by
plane. Counts mirror PLATFORM_INVENTORY when applicable; do not
hand-edit.

### 2.1 Autonomy plane

| # | Primitive | Purpose | Owner | Lifecycle | Evidence | Reuse class | Unknowns |
|---|---|---|---|---|---|---|---|
| 1 | `GovernanceState` model | Mode + scope state (normal/throttle/freeze/safe_mode × global/agent/desk) | Ops Autopilot | TTL-based auto-expiry; effective_mode returns 'normal' if expired | `core/models_governance.py:17-114` | **SAFE** (freeze/safe_mode wired) | throttle + per-(agent/desk) scopes unused |
| 2 | `KillSwitch` model | Emergency blocks (TTL required) on 6 targets: scheduler/queue/agent_family/publishing/outbound/deploys | Ops Autopilot | TTL-based auto-expiry via `auto_expire_governance_state()` (`governance.py:2494-2529`) | `core/models_governance.py:116-189` | **WRAPPER** (write+status only; no enforcement) | Zero dispatch consumers; target field unused at runtime |
| 3 | `GovernanceState.effective_mode` property | TTL-aware mode reader; returns 'normal' if expired | Ops Autopilot | Per-call evaluation | `core/models_governance.py:97-107` | **SAFE** | None |
| 4 | `GovernanceEngine` service | Read/write API for GovernanceState + KillSwitch | Ops Autopilot | Stateless service | `core/services/ops_autopilot/governance.py:2159-2529` | **SAFE** | None |
| 5 | Spider Network governance check | `freeze`/`safe_mode` → skip task | Spider system | Beat-task entry check | `core/tasks_spiders.py:381-398` | **SAFE** | Throttle mode not consumed |
| 6 | Signal Aggregation governance check | `freeze`/`safe_mode` → return empty | Signal pipeline | Method entry check | `core/services/signal_aggregation_service.py:207-227,968-971` | **SAFE** | Same |
| 7 | Workspace Pipeline governance check | `freeze`/`safe_mode` → cancel run + error_message | Workspace autopilot | Pipeline stage entry check | `core/services/workspace_pipeline_runner.py:43-49`; `core/models_workspace_templates.py:209-218` | **SAFE** | Same |
| 8 | `governance_tool` PA tool | LLM surface for status/set_mode/kill_switch/audit | PA | Synchronous | `core/services/pa_tool_schemas.py:3157-3219`; `core/services/td_handlers_ops.py:2760-3035` | **SAFE** | None |
| 9 | `GovernanceEngine._sync_budget_flags()` | One-way sync GovernanceState → SystemConfiguration | Ops Autopilot | On mode change | `core/services/ops_autopilot/governance.py:2271-2273` | **WRAPPER** | Reverse-sync missing |

### 2.2 Authority plane

| # | Primitive | Purpose | Owner | Lifecycle | Evidence | Reuse class | Unknowns |
|---|---|---|---|---|---|---|---|
| 10 | `AuthorityLevel` enum | 4 members: OBSERVE / RECOMMEND / EXECUTE / PROHIBITED (string values) | Employee OS | Module-level enum | `core/employees/jobs.py:41-52` | **SAFE** | None |
| 11 | `JobContract.authority` dict | Per-job mapping `action_class_string → AuthorityLevel.value` | Each employee job | Frozen dataclass field | `core/employees/jobs.py:95-162` (definition); per-employee at jobs.py:238-250 (Rigby), 488-505 (Auditor), 782-812 (Chief), 1102-1125 (Triage) | **WRAPPER** (no readers gate against it) | Symbol-mapping prereq blocks enforcement |
| 12 | `JobContract.prohibited_actions` tuple | Human-readable denial list (separate from dict) | Each employee job | Frozen | jobs.py:252-257 (Rigby), 507-517 (Auditor), 814-830 (Chief), 1127-1138 (Triage) | **SAFE** for audit; **WRAPPER** for enforcement | Same |
| 13 | `AUTHORITY_CONTRACT_OBSERVED_LABEL` constant | Stable OpsRunEvent label for warn-mode emissions | MissionRunner | Constant | `core/employees/mission_runner.py:264` | **SAFE** | None |
| 14 | `AUTHORITY_CONTRACT_SCHEMA_VERSION` constant | Version of event detail shape (currently 1, write-only) | MissionRunner | Constant; bump on detail schema change | `core/employees/mission_runner.py:265` | **SAFE** | No runtime branching consumers |
| 15 | `_hash_contract_shape()` helper | SHA-256[:16] of sorted authority + prohibited_actions; stable across reorderings | MissionRunner | Pure function | `core/employees/mission_runner.py:278-303` | **SAFE** | None |
| 16 | `_AuthorityContractMalformedError` exception | Raised on malformed contract; caught + logged + mission continues | MissionRunner | Internal exception | `core/employees/mission_runner.py:268-275` | **SAFE** | None |
| 17 | `MissionRunnerConfig.job_contract` field | Optional `JobContract` for warn-mode opt-in (default None) | MissionRunner | Frozen dataclass field | `core/employees/mission_runner.py:562-572` | **SAFE** | None |
| 18 | `_emit_authority_contract_event()` method | Emits one info-type OpsRunEvent per mission after `run_started` | MissionRunner | Per-mission | `core/employees/mission_runner.py:835-900` | **SAFE** | None |
| 19 | `authority_contract_observed` OpsRunEvent (label) | Warn-mode telemetry row, idempotent on (run, label) | MissionRunner write; Bug Triage reads | One row per mission run | Written at mission_runner.py:880-900; consumed at `core/jobs/bug_triage.py:396-453` | **SAFE** | Only one consumer today |
| 20 | Bug Triage authority telemetry collection | Step 4: query 24h `label='authority_contract_observed'` rows; aggregate by employee_handle | Bug Triage | Daily beat | `core/jobs/bug_triage.py:396-453` + `jobs.py:1037-1040,1075-1077,1209-1210` | **SAFE** | Only baseline accumulator today |

### 2.3 Budget / cost plane

| # | Primitive | Purpose | Owner | Lifecycle | Evidence | Reuse class | Unknowns |
|---|---|---|---|---|---|---|---|
| 21 | `SystemConfiguration.budget_freeze_active` flag | LLM-cost emergency freeze (blocks non-critical LLM calls) | LLMEnforcer | Toggled on mode change via GovernanceEngine sync | `core/llm_enforcer.py:200-260` | **WRAPPER** | One-way sync only |
| 22 | LLMEnforcer freeze gate | Returns blocked dict for non-critical LLM calls when frozen | LLMEnforcer | Per-LLM-call gate | `core/llm_enforcer.py:200-260` | **SAFE** | None |
| 23 | `check_retry_budget(name, window_seconds, max_retries, fingerprint)` | App-layer rate limiter to prevent retry storms | Per-task callers | Per-retry check | `core/services/retry_policy.py:141-200` | **SAFE** | None |

### 2.4 Human governance plane

| # | Primitive | Purpose | Owner | Lifecycle | Evidence | Reuse class | Unknowns |
|---|---|---|---|---|---|---|---|
| 24 | `HumanAttentionItem` model | Decision-needed-from-human surface | 31 creators across platform | Status: pending → viewed → acted/deferred/ignored/expired/watching/verified | `core/models_human_interface.py:20+` | **SAFE** | Multi-approver not supported |
| 25 | `HumanAttentionLifecycleService` | Auto-expire / dismiss / escalate / approve | Beat: `process_human_attention_lifecycle` every 10 min | Service | `core/services/human_attention_lifecycle.py:36-728` | **SAFE** | None |
| 26 | Auto-escalate ladder | LOW (72h) → MEDIUM (48h) → HIGH (24h) → CRITICAL (auto-dismiss after 3d) | Lifecycle service | Beat-driven | `core/services/human_attention_lifecycle.py:181-221` | **SAFE** | None |
| 27 | Auto-approve gating (7 conditions) | review_mode off + user pref + low urgency + 1h age + LOW_RISK source/type + ML confidence | Lifecycle service | Beat-driven | `core/services/human_attention_lifecycle.py:223-296` | **SAFE** | None |
| 28 | `HumanFeedbackRecord` model | Decision feedback with `fed_to_ml` flag + ML attribution | Auto-created by signal on HAI decision | One row per decision | `core/models_human_interface.py:230-266` | **SAFE** | `fed_to_ml` flag set manually; signal fires regardless |
| 29 | `FeedbackProcessor.process_human_feedback()` | Classifies positive/negative → creates AgentLearning + LearningInsight | Signal handler on HumanFeedbackRecord post_save | Per-decision | `core/models_feedback_processing.py:122-180,216-330,372-392` | **SAFE** | None |
| 30 | `HumanPreference` model | Per-user collab policy: auto_approve_low_risk + trusted_agents + learned topic_weights/source_weights | Lifecycle service writes learned stats | Per-decision update via `update_learned_stats()` (`models_human_interface.py:334-358`) | `core/models_human_interface.py:268-358` | **WRAPPER** | topic_weights/source_weights fields NEVER POPULATED |
| 31 | `OrchestrationApprovalGate` model | Workflow step → HAI bridge for human approval | Workflow orchestration | States: pending/approved/rejected/modified/auto_approved/expired | `core/models_orchestration.py:397-535` | **SAFE** | auto_approve trigger UNKNOWN |
| 32 | `gate.approve/reject/modify/auto_approve` methods | Status transitions with side effects | Workflow orchestration | Per-decision | `core/models_orchestration.py:475-508` | **SAFE** | None |
| 33 | `check_auto_approvals()` method | Loops expired pending gates with `auto_approve_on_timeout=True` | Orchestration approval | NOT in beat schedule | `core/services/orchestration_approval.py:214-262` | **UNKNOWN** | Call site not in beat or tasks.py |
| 34 | `HumanInterfaceService.record_decision()` | Main decision API: writes HAI + HumanFeedbackRecord + triggers ML feedback | HAI consumers | Synchronous | `core/services/human_interface_service.py:295-353` | **SAFE** | None |
| 35 | `HumanInterfaceService._update_preferences_from_decision()` | Updates HumanPreference.update_learned_stats() per decision | HAI service | Synchronous per decision | `core/services/human_interface_service.py:738` | **WRAPPER** | source_weights modification local-only, NOT saved |

### 2.5 Authentication + permission plane

| # | Primitive | Purpose | Owner | Lifecycle | Evidence | Reuse class | Unknowns |
|---|---|---|---|---|---|---|---|
| 36 | `UnifiedTokenAuthenticationMiddleware` | Global request gate (~108 PUBLIC_PATHS bypass; rest require auth) | Auth middleware | Per-request | `core/auth_middleware.py:563-681` | **SAFE** | None |
| 37 | Staff-required paths gate | `STAFF_REQUIRED_PATHS` → 403 if `is_staff=False` | Auth middleware | Per-request | `core/auth_middleware.py:541-544,610-614,661-664` | **SAFE** | None |
| 38 | Reviewer-blocked paths gate | `REVIEWER_BLOCKED_PATHS` → 403 if `is_reviewer=True` and write method | Auth middleware | Per-request | `core/auth_middleware.py:548-556,615-623,667-673` | **SAFE** | None |
| 39 | DRF `@permission_classes([IsAuthenticated])` | Per-view DRF gate (30+ PA endpoints) | Per-view decorator | Per-request | `core/views_personal_assistant.py` (30+ sites) | **SAFE** | None |
| 40 | `FleetSignatureAuthentication` | HMAC verification of `X-Fleet-Signature` header | Fleet auth | Per-request | `core/services/fleet_auth_drf.py:65-150` | **SAFE** | Permissive fallback (does not raise) |
| 41 | `FleetSignatureRequired` / `FleetCapabilityRequired` | DRF permission classes for fleet-only endpoints | Fleet auth | Per-request | `core/services/fleet_auth_drf.py:176-262` | **SAFE** | None |
| 42 | Service token: `PA_DB_HEALTH_RPC_TOKEN` | Prod DB diagnostic gate (404/401/403) | Health RPC view | Per-request | `core/views_db_health_rpc.py:39-116` | **SAFE** | Disabled by default (404 when unset) |
| 43 | Service token: `PUBLIC_INTEL_TOKEN` | 247globalai.com integration; default empty = disabled | Public intel view | Per-request | `core/views_public_intelligence.py:44` | **WRAPPER** | Default-off endpoint |
| 44 | VIP demo middleware | Read-only + workspace-scope for `vip_demo_viewer` role | VIP middleware | Per-request | `core/vip_middleware.py:50-105` | **SAFE** | None |
| 45 | VIP scope injection (PA chat) | Prompt-injection directives (NOT runtime gates) | views_personal_assistant | Per-request | `core/views_personal_assistant.py:316-346` | **WRAPPER** | Prompt-only enforcement; PA can ignore |

### 2.6 LLM + tool dispatch gates

| # | Primitive | Purpose | Owner | Lifecycle | Evidence | Reuse class | Unknowns |
|---|---|---|---|---|---|---|---|
| 46 | `messaging_tool.send_message` guard | Returns `MESSAGING_SEND_DISABLED` unless `MESSAGING_TOOL_ALLOW_SEND=True` | Tool dispatcher | Per-dispatch | `core/services/td_handlers_core.py:3693-3711` | **SAFE** | None |
| 47 | `REMOVED_TOOL_ALIASES` redirect | Maps deprecated tool names → gateway replacements | Tool dispatcher | Per-dispatch | `core/services/tool_dispatcher.py:210-229` | **WRAPPER** | Soft redirect, not hard block |
| 48 | OpenAI reasoning model guard | Forbidden kwargs (max_tokens/temperature/etc.) blocked on gpt-5.x | OpenAI factory | Per-call (via `OPENAI_REASONING_GUARD` env var: warn/strip/error) | `core/services/openai_client_factory.py:98-196` | **SAFE** | None |
| 49 | Anthropic factory forbidden-kwarg guard | Blocks timeout/max_retries/api_key kwargs | Anthropic factory | Per-call | `core/services/anthropic_client_factory.py:74-94` | **SAFE** | None |
| 50 | `_verify_rigby_caller` Rigby-gating | PA tool actions requiring `user_id` resolves to Rigby's `runs_as_username` | Tool dispatcher | Per-call | `core/services/td_handlers_employee.py` (per S1268 protocol sketch §1) | **SAFE** | None |

### 2.7 Feature flags (12 gates)

| # | Flag | Default | Purpose | Evidence | Reuse class |
|---|---|---|---|---|---|
| 51 | `MESSAGING_TOOL_ALLOW_SEND` | False | Gates `messaging_tool.send_message` | `core/services/td_handlers_core.py:3701` | **SAFE** |
| 52 | `RIGBY_EVENT_INTAKE_ENABLED` | False | Gates Deliverable post_save → rigby intake | `core/settings.py:111-113` + `core/signals/deliverable_status_signals.py:47` | **SAFE** |
| 53 | `RIGBY_INTERNAL_WORK_QUEUE_ENABLED` | False | Gates RigbyWorkItem row creation | `core/settings.py:120-122` | **SAFE** |
| 54 | `RIGBY_WORK_QUEUE_REVIEW_ENABLED` | False | Gates `rigby_work_item` PA tool | `core/settings.py:129-131` | **SAFE** |
| 55 | `RIGBY_DELEGATION_ENABLED` | False | Gates Rigby mission delegation action | `core/settings.py:138-140` | **SAFE** |
| 56 | `INITIATIVE_DIAGNOSTICS_ENABLED` | True | Gates diagnostic signal cascade | `core/signals/initiative_diagnostic_signals.py:47` | **SAFE** |
| 57 | `CTO_DIAGNOSTIC_ENABLED` | False | Gates CTO daily diagnostic task | `core/services/scheduled_diagnostic_runner.py:188` | **SAFE** |
| 58 | `CTO_DIAGNOSTIC_POSTING_ENABLED` | False | Gates CTO posting step (independent of execution) | Same runner | **SAFE** |
| 59 | `COO_DIAGNOSTIC_ENABLED` | False | Gates COO daily diagnostic task | Same runner | **SAFE** |
| 60 | `COO_DIAGNOSTIC_POSTING_ENABLED` | False | Gates COO posting step | Same runner | **SAFE** |
| 61 | `PA_USE_FUNCTION_CALLING` | False | Gates GPT-5.2 function-calling path in PA | `core/services/unified_pa_entrypoint.py:684,893` + `core/settings.py:1627` | **WRAPPER** | False causes claude-code source short-circuit per memory rule |
| 62 | `FLEET_AUTH_ENFORCE_ROUTING` | True | Gates routing claims from unsigned fleet requests | `core/views_personal_assistant.py:363-365` | **SAFE** |
| 63 | `OPENAI_REASONING_GUARD` | warn | Reasoning-model guard mode (warn/strip/error) | `core/services/openai_client_factory.py:85` | **SAFE** |

**Inventory totals.** 63 primitives across 7 planes. Of those: **48
SAFE TO REUSE**, **11 WRAPPER**, **0 DO-NOT-REUSE**, **0
DEPRECATED**, **3 UNKNOWN** (KillSwitch enforcement,
OrchestrationApprovalGate auto_approve trigger,
JobContract.authority enforcement readers).

---

## 3. Authority Lifecycle

Trace the path requested by Q2: **Human → Employee → MissionRunner
→ Tool → Evidence → Completion → Certification → Visibility.**

```
HUMAN (Chris)
  │
  │  Decides scope + contract + cadence (jobs.py JobContract dataclass)
  │  PR review gates contract changes
  │  ↑ ENFORCED via git (PR review, not runtime)
  ▼
EMPLOYEE (frozen AIEmployee + JobContract registry)
  │  
  │  4 employees registered in `_EMPLOYEES_BY_HANDLE` (jobs.py:1327-1347)
  │  Each carries: authority dict + prohibited_actions tuple + 
  │                what_chris_approves/handles/can_do_alone tuples
  │  ↑ DOCUMENTATION ONLY at this layer; no runtime enforcement
  ▼
DISPATCH (beat / employee_tool / management command)
  │  
  │  Beat scheduler picks up PeriodicTask row → fires
  │     `core.tasks_<job>.run_<job>` Celery task
  │  OR Rigby calls `employee_tool action=run_now` (Rigby-gated)
  │  OR `python manage.py run_<job>` (operator-gated)
  │  ↑ ENFORCED at dispatch (auth on PA tool; access on mgmt cmd)
  ▼
MISSION RUNNER (`core/employees/mission_runner.py:1-1758`)
  │  
  │  Construct MissionRunnerConfig(employee_handle, job_contract=<JOB>, ...)
  │  Call .run() → get_or_create OpsRun(domain='mission')  [daily idempotency]
  │  
  │  Emit `run_started` event
  │  Emit `authority_contract_observed` event   ← OBSERVATION (S1264)
  │      detail: schema_version, employee_handle, contract_title,
  │              contract_version_tag (16-char SHA),
  │              authority_entries_total, authority_level_counts,
  │              prohibited_actions_count, mode='warn'
  │  ↑ TELEMETRY ONLY; mission ALWAYS continues even if contract malformed
  ▼
STEP LOOP
  │  
  │  For each Step:
  │    emit <step>_started
  │    call step.fn(mission) → StepResult
  │    emit <step>_passed or <step>_failed
  │  
  │  ↑ NO authority check between dispatch and step execution
  │     Step code does whatever it does; runner has no visibility
  │     into which action_classes the step invoked.
  │     This is the SYMBOL-MAPPING GAP (F4 + §11 recommendation).
  ▼
TOOL CALLS (within steps)
  │  
  │  Steps invoke PA tools (governance_tool, deliverable_tool, etc.)
  │  via `ToolDispatcher.execute()`
  │  Tool handlers may have their own gates (messaging guard, 
  │     REMOVED_TOOL_ALIASES redirect, Rigby-gating)
  │  ↑ ENFORCED at TOOL level (not contract level)
  │     Gate is per-tool, not per-employee-authority
  ▼
EVIDENCE
  │  
  │  Each step writes: ToolCallRecord (per tool call)
  │                    LLMCallEvent (per LLM call)
  │                    AgentExecution (per agent invocation)
  │                    Step-specific summary keys to OpsRun.summary
  │  ↑ FULL audit chain; reconstructable via `evidence_for_mission()`
  │     (`core/employees/status.py:347-508`)
  ▼
COMPLETION (mission lifecycle terminal)
  │  
  │  postflight_fn (optional)
  │  if step failure: escalation (Deliverable + maybe PA chat post)
  │  if mission terminal: shift_report_fn → post_shift_report DM
  ▼
CERTIFICATION (verdict emission)
  │  
  │  IF config.auto_emit_verdict=True (3 of 4 employees):
  │     emit `verdict_issued:certified/rejected/deferred` OpsRunEvent
  │     flip OpsRun.status to passed/failed/partial
  │  IF auto_emit_verdict=False (Bug Triage v0, S1267):
  │     flip OpsRun.status + finished_at; SKIP verdict event
  │     Rigby/human emits verdict later via `mission_verdict` PA tool
  │  ↑ AUTHORITY: `certify_mission_run` is EXECUTE on 3 employees;
  │     Bug Triage opted out by design
  ▼
VISIBILITY
  │  
  │  Deliverable in workspace (FilesTab + Inbox)
  │  DirectMessage in (employee, job) thread (Inbox poll 15s)
  │  OpsRun + events queryable via `evidence_for_mission()`
  │  `/ws/system-events/` WebSocket broadcasts (9 base + 7 orchestration events)
  │  ↑ ENFORCED by view auth + workspace ownership; not by JobContract
```

### Where authority exists today

- **At git/PR review** (contract definitions live in code)
- **At dispatch surfaces** (auth middleware, DRF permissions,
  Rigby-gating on PA tools)
- **At tool boundaries** (messaging guard, reasoning guard,
  REMOVED_TOOL_ALIASES)
- **At telemetry level** (`authority_contract_observed`
  observation only)

### Where authority is only implied

- **Step bodies** — a step can technically invoke any tool, write
  any model, call any LLM. There is no contract-driven gate between
  the dispatched step function and its implementation.
- **`recommend_remediations`** entries (in Auditor / Chief /
  Triage / Rigby) imply that the employee should not act, only
  recommend — but no runtime check enforces this.
- **`prohibited_actions` tuples** — human-readable denials with
  no runtime symbol binding. Enforce by code review only.

### Where authority completely disappears

- **Between MissionRunner and step.fn execution.** The runner
  never asks "what action_classes is step X about to invoke?"
  and the step never declares them. Symbol mapping is the
  blocker (F4).
- **Across employees.** Employee A's authority does not
  propagate to Employee B. No cross-employee trust contract
  exists.
- **Inside ToolDispatcher.** Tool handlers don't read the calling
  agent's JobContract.authority. They check their own gates
  (messaging, reasoning guard, Rigby-gating) but not contract-
  level authority.

---

## 4. Runtime Enforcement Points

Every place where code actually **prevents** an action, organized
by enforcement layer. Each row marks honesty: **RUNTIME-VERIFIED**
(production gate), **ASPIRATIONAL** (gate exists but is
documentation-shaped), or **UNKNOWN** (couldn't fully verify).

### 4.1 Auth + permission gates (5 rows, all RUNTIME-VERIFIED)

| Gate | What it blocks | How | File:Line |
|---|---|---|---|
| Token middleware | 99% of `/api/` endpoints sans auth | 401/503 | `core/auth_middleware.py:563-681` |
| Staff-required paths | Non-staff hitting `/api/v1/admin/`, `/api/v1/system/`, `/api/v1/metrics/admin/` | 403 | `core/auth_middleware.py:541-544,610-614,661-664` |
| Reviewer-blocked paths | Reviewer-role writes to listed paths | 403 | `core/auth_middleware.py:548-556,615-623,667-673` |
| DRF `IsAuthenticated` | Unauthenticated PA-view requests | 403 | `core/views_personal_assistant.py` (30+ sites) |
| VIP demo middleware | VIP role writes anywhere except 3 allowed paths | 403 | `core/vip_middleware.py:50-105` |

### 4.2 Service-token gates (3 rows, mixed)

| Gate | What it blocks | How | File:Line | Honesty |
|---|---|---|---|---|
| PA DB Health RPC | Wrong/missing `PA_DB_HEALTH_RPC_TOKEN` | 404/401/403 | `core/views_db_health_rpc.py:39-116` | RUNTIME-VERIFIED |
| Fleet HMAC signature | Sets `fleet_identity=None` on bad sig (permissive fallback) | Audit log + degraded mode | `core/services/fleet_auth_drf.py:65-150,176-212` | RUNTIME-VERIFIED |
| `PUBLIC_INTEL_TOKEN` | All requests if unset (default empty) | Token compare | `core/views_public_intelligence.py:44` | RUNTIME-VERIFIED but disabled by default |

### 4.3 Tool dispatcher gates (4 rows, mixed)

| Gate | What it blocks | How | File:Line | Honesty |
|---|---|---|---|---|
| `messaging_tool.send_message` | Send unless `MESSAGING_TOOL_ALLOW_SEND=True` | Returns `MESSAGING_SEND_DISABLED` dict | `core/services/td_handlers_core.py:3693-3711` | RUNTIME-VERIFIED |
| `REMOVED_TOOL_ALIASES` | Soft redirect to gateway tool | Returns redirect advice, not block | `core/services/tool_dispatcher.py:210-229` | ASPIRATIONAL (advice) |
| Rigby-gating (`_verify_rigby_caller`) | Non-Rigby callers from `mission_verdict`, `employee_tool run_now` | Returns auth error | `core/services/td_handlers_employee.py` | RUNTIME-VERIFIED |
| OpenAI reasoning guard | Forbidden kwargs on gpt-5.x | Warn/strip/error per `OPENAI_REASONING_GUARD` | `core/services/openai_client_factory.py:98-196` | RUNTIME-VERIFIED |

### 4.4 Celery + task gates (2 rows, RUNTIME-VERIFIED)

| Gate | What it blocks | How | File:Line |
|---|---|---|---|
| `check_retry_budget` | Retry storms (Redis sliding counter) | Returns `(False, reason)` if over limit | `core/services/retry_policy.py:141-200` |
| `acks_late` per-task | Message requeue on task failure when False | Celery honors per-task config | `core/tasks.py:11911` (PA chat override) |

### 4.5 Feature-flag gates (12 rows, all RUNTIME-VERIFIED)

See §2.7 for full inventory. Default-OFF rails:
`MESSAGING_TOOL_ALLOW_SEND`, `RIGBY_EVENT_INTAKE_ENABLED`,
`RIGBY_INTERNAL_WORK_QUEUE_ENABLED`,
`RIGBY_WORK_QUEUE_REVIEW_ENABLED`, `RIGBY_DELEGATION_ENABLED`,
`CTO_DIAGNOSTIC_ENABLED`, `CTO_DIAGNOSTIC_POSTING_ENABLED`,
`COO_DIAGNOSTIC_ENABLED`, `COO_DIAGNOSTIC_POSTING_ENABLED`,
`PA_USE_FUNCTION_CALLING`. Default-ON rails:
`INITIATIVE_DIAGNOSTICS_ENABLED`, `FLEET_AUTH_ENFORCE_ROUTING`.

### 4.6 Autonomy plane gates (5 rows, mixed)

| Gate | What it blocks | How | File:Line | Honesty |
|---|---|---|---|---|
| Spider network governance check | `freeze`/`safe_mode` skips all spiders | Returns `skipped=True` early | `core/tasks_spiders.py:381-398` | RUNTIME-VERIFIED |
| Signal aggregation governance check | `freeze`/`safe_mode` skips aggregation + auto-topic | Returns empty list | `core/services/signal_aggregation_service.py:207-227,968-971` | RUNTIME-VERIFIED |
| Workspace pipeline governance check | `freeze`/`safe_mode` cancels run | Sets status='cancelled' + error_message | `core/services/workspace_pipeline_runner.py:43-49` | RUNTIME-VERIFIED |
| LLMEnforcer budget freeze | Non-critical LLM calls when `SystemConfiguration.budget_freeze_active=True` | Returns blocked dict; allows `governance`/`auth`/`incident_response`/`pa_chat` purposes + `PersonalAssistant` agent | `core/llm_enforcer.py:200-260` | RUNTIME-VERIFIED |
| KillSwitch dispatch check | NOTHING — no consumer checks `is_active` before target action | — | None | **UNKNOWN / NOT FOUND** |

### 4.7 Authority plane gates (1 row, ASPIRATIONAL)

| Gate | What it blocks | How | File:Line | Honesty |
|---|---|---|---|---|
| `JobContract.authority` enforcement | Nothing — observation only | Emits `authority_contract_observed` event; never blocks | `core/employees/mission_runner.py:835-900` | **ASPIRATIONAL** — zero readers gate against the dict |

### 4.8 Other gates (3 rows, mixed)

| Gate | What it blocks | How | File:Line | Honesty |
|---|---|---|---|---|
| Source-based intent routing | `source='claude-code'` skips keyword routing (deliberate) | Hardcoded short-circuit | `core/services/unified_pa_entrypoint.py:2673-2753` | RUNTIME-VERIFIED |
| Fleet routing enforce | Unsigned routing claims stripped + audited | If `FLEET_AUTH_ENFORCE_ROUTING=True` | `core/views_personal_assistant.py:347-366` | RUNTIME-VERIFIED |
| Workspace-aware agent dispatch | Non-WORKSPACE_AWARE agents from workspace writes | List membership check | `core/epa_handlers_tools.py:3873-3909` | RUNTIME-VERIFIED |

**Total: 35 gates. 29 RUNTIME-VERIFIED. 5 ASPIRATIONAL. 1 UNKNOWN
(KillSwitch).**

---

## 5. Human Governance

The human governance plane is the **only round-trip pattern with
learning** on the platform today (per collaboration audit §1 F4).

### 5.1 Decision flow (synchronous + async parts)

```
HAI created (one of 31 creators)
  │
  ▼  status='pending'
  
LIFECYCLE BEAT (every 10 min — `process_human_attention_lifecycle`)
  │
  ├─ _expire_old_items: expires_at < now → status='expired'
  ├─ _auto_dismiss_stale_items: pending past TTL by urgency → status='ignored', decision='auto_dismiss'
  ├─ _auto_escalate_aging_items: bumps urgency low→med (72h) → med→high (48h) → high→critical (24h)
  └─ _auto_approve_low_risk_items: 7-condition gate (see §2.4 row 27)
  
HUMAN VIEW + DECIDE
  │
  ├─ mark_viewed() sets viewed_at + status='viewed'
  │
  ▼  record_decision(decision, feedback, confidence)
  │  - SYNCHRONOUS write
  │  - Sets decided_at + decision + time_to_decision_ms
  │  - Sets human_overrode_ml if decision != ml_recommendation
  │  - status → 'acted' (or 'watching' if DECISION_WATCH)
  ▼

HumanInterfaceService.record_decision() writes:
  ├─ HumanAttentionItem.save() (per above)
  ├─ HumanFeedbackRecord.objects.create() ← triggers signal
  └─ HumanPreference.update_learned_stats()
     (approval_rate, total_decisions, avg_decision_time_ms)
  
SIGNAL CASCADE (auto, post_save on HumanFeedbackRecord)
  │
  ▼  FeedbackProcessor.process_human_feedback()
  ├─ Classifies positive (approve/approved/accept/publish/completed)
  ├─ Classifies negative (reject/rejected/decline/failed/needs_work)
  ▼
  ├─ _reinforce_positive(): AgentLearning('positive_feedback', confidence=0.8)
  │  + LearningInsight('positive_reinforcement')
  └─ _learn_from_negative(): AgentLearning('negative_feedback', confidence=0.9)
     + LearningInsight('improvement_needed', requires_attention=True)
```

### 5.2 What is human-driven vs. automated

| Stage | Driver | Automation level |
|---|---|---|
| Item creation | External systems (31 creators inventoried in S1268) | Automated |
| Item visibility | Human dashboard query | Manual |
| Mark viewed | Human UI button | Manual |
| Record decision | Human UI form | Manual + auto-feedback |
| Set override flag | Automatic on decision | Automated |
| HumanFeedbackRecord | Signal handler post_save | Automated |
| AgentLearning + LearningInsight | Signal handler | Automated |
| HumanPreference learned stats | Service call per decision | Automated |
| Auto-escalate | Beat task (10 min) | Automated |
| Auto-dismiss | Beat task (10 min) | Automated |
| Auto-approve | Beat task + conditions | Automated (gated) |
| Trigger orchestration on approve | Async | Automated |
| OrchestrationApprovalGate decisions | Human via Mission Control | Manual |
| Auto-approve gate (timeout) | `check_auto_approvals()` — UNKNOWN trigger | UNKNOWN |
| Mark verification (Watch & Verify) | Manual post-event | Manual |

### 5.3 Gaps in human governance

- `HumanPreference.topic_weights` field exists; **never
  populated** (no write path found).
- `HumanPreference.source_weights` field exists;
  `_update_preferences_from_decision()` modifies a local dict
  but **never saves** the result (`human_interface_service.py:732-736`).
- `OrchestrationApprovalGate.check_auto_approvals()` exists at
  `orchestration_approval.py:214-262` but is **NOT in beat
  schedule** (no callsite in `core/celery.py` or `core/tasks*.py`).
- `HumanPreference` notification rails (`quiet_hours_start/end`,
  `min_urgency_to_notify`, `preferred_channel`) are **defined
  but not consumed** by HAI notification senders.
- Multi-approver and decision-precedent tracking: **not
  implemented** (no model, no service).

### 5.4 Auto-approve criteria (full 7-condition gate)

From `human_attention_lifecycle.py:223-296`:

1. `HumanSystemState.review_mode == False`
2. User has `HumanPreference.auto_approve_low_risk == True`
3. Item `status == 'pending'`
4. Item `urgency == 'low'`
5. Item `created_at < now - 1 hour` (human had time)
6. `source_type in LOW_RISK_SOURCES` OR `item_type in AUTO_APPROVABLE_TYPES`
7. `ml_confidence >= user_pref.require_review_above_confidence`

Constants (`human_attention_lifecycle.py:63-78`):

```python
LOW_RISK_SOURCES = [
    'spider_insight', 'content_review', 'blog_review',
    'trend_analysis', 'observation',
]
AUTO_APPROVABLE_TYPES = [
    'content', 'insight', 'observation', 'analysis', 'suggestion',
]
```

---

## 6. Governance Failure Modes

12 governance-specific incidents documented. The 9 already covered
in the collaboration audit §7 are referenced by number; 3 NEW
governance-specific incidents are detailed here.

### 6.1 NEW incidents (3)

**I-G1: Authority symbol-mapping gap (S1264 discovery).**
S1260 Phase 2 planning proposed authority enforcement via
preflight hook. Discovery revealed the approach was infeasible:
`JobContract.authority` keys are policy-description strings,
not runtime symbols. Zero registry maps the strings to tool
names / function signatures / model methods. Steps don't
declare `action_classes_invoked`. Tools have no `action_class`
metadata. **Fix:** S1264 shipped warn-mode (observation only).
PR #2756. **Status:** Live for all 4 employees;
enforcement still blocked on symbol mapping. **Lesson:**
Authority enforcement requires a registry mapping policy
strings to runtime predicates. Mere observation of contract
shape is the honest baseline when runtime symbols are missing.
**Relevance:** **HIGHEST** — core architectural blocker.

**I-G2: Auth middleware silent error suppression (S1171).**
During ML queue flood investigation, Daphne returned 401
"Invalid authentication token" for every API call. Investigation
revealed auth middleware silently swallowing `OperationalError`
(Postgres `too many clients`) as if the token were invalid. The
real infrastructure error was masked. **Root cause:** bare
`except:` clause in `validate_token()` catching everything.
**Fix:** S1171 PR #2328 split into `TokenValidationInfrastructureError`
(503 `auth_backend_unavailable`) vs. `DoesNotExist` (401).
**Status:** Closed. Auth responses now distinguish "invalid
token" from "auth backend broken." **Lesson:** Silent
error suppression in authority infrastructure masks
infrastructure signals. **Relevance:** **HIGH** —
governance enforcement will depend on auth middleware being
correct.

**I-G3: HTTP API permission gate flip (S1265 pre-SIGN catch).**
New read-only Employee/Mission HTTP API initially shipped
with `@permission_classes([IsAuthenticated])`. Rigby
SIGN-WITH-EDITS decision: flip to `IsAdminUser`. Test matrix
added: anon 403, non-staff 403, staff 200. **Fix:** S1265 PR
#2760. **Status:** Closed pre-merge; five endpoints live as
`IsAdminUser`-gated. **Lesson:** Permission classes should
default to restrictive, not open. Pre-SIGN gate validation
prevents over-permission bugs at the doc-review boundary.
**Relevance:** **MEDIUM** — pattern reinforcement for any
future governance HTTP API.

### 6.2 Referenced incidents (already in collaboration audit §7)

| Ref | Class | Relevance to authority |
|---|---|---|
| §7 row 21 | Authority enforcement vs observation (S1264) | Same as I-G1 above |
| §7 row 16 | Duplicate Agent rows (S1263 PR #2754) | LOW — identity drift, not authority |
| §7 row 1 | Receipt-chain gap (claude_code_tool, S1262) | MEDIUM — receipts are evidence; receipts of authority-relevant tools matter |
| §7 row 29 | MissionRunner verdict event conditional on `auto_emit_verdict` (S1267) | MEDIUM — verdict authority is `certify_mission_run` in 3 employees; Bug Triage opted out by design |
| §7 row 3 | LLM autofills False/0 on optional params (S1227-1228) | MEDIUM — any new authority tool with optional params must use truthy-or-default |
| §7 row 14 | Placeholder-stall pattern (S1226, S1241) | LOW — workflow discipline, not governance |
| §7 rows 17-19 | Zombie threads, heartbeat stomp, OpenAI/Anthropic factory drift (S1083-1221) | MEDIUM — reliability layer governance depends on |
| §7 row 4 | `auto_followup=False` banner suppression (S1184) | LOW — UX, not governance |
| §7 row 28 | EventBus stream count drift (S1268) | LOW — doc drift |

---

## 7. Reuse Classification

Per the same shape as prior audits.

### SAFE TO REUSE (48)

All §2 rows classified as SAFE. Highlights for authority work
specifically:
- `AuthorityLevel` enum (row 10)
- `AUTHORITY_CONTRACT_OBSERVED_LABEL` (row 13)
- `_hash_contract_shape()` helper (row 15)
- `_AuthorityContractMalformedError` exception (row 16)
- `MissionRunnerConfig.job_contract` (row 17)
- `_emit_authority_contract_event()` (row 18)
- `authority_contract_observed` event (row 19) — single
  consumer pattern is reusable
- All 3 governance-plane consumers (rows 5-7)
- `GovernanceEngine` service (row 4)
- `governance_tool` PA tool (row 8)
- Full HAI lifecycle (rows 24-27, 31-34)
- Full feature-flag rail (rows 51-63)
- All auth + permission gates (rows 36-41, 44)

### REUSE WITH WRAPPER (11)

- **`KillSwitch` (row 2)** — write + status + TTL wired; **NO
  dispatch consumers** check `is_active` before
  scheduler/queue/agent_family/publishing/outbound/deploys
  actions. Wrapper must add an enforcement adapter before
  any reliance on the switch actually blocking work.
- **`JobContract.authority` dict (row 11)** — symbol-mapping
  prereq blocks all enforcement. Per Rigby S1269 SIGN
  clarification: **SAFE-TO-REUSE-as-telemetry**, but
  **DO-NOT-REUSE-for-enforcement** until symbol mapping
  exists. The dict drives the `authority_contract_observed`
  warn-mode telemetry today; that path is real and useful.
  Reuse for enforcement is the part that's blocked.
- **`JobContract.prohibited_actions` tuple (row 12)** — same
  framing as above: SAFE for audit / contract review,
  DO-NOT-REUSE-for-enforcement.
- **`GovernanceEngine._sync_budget_flags()` (row 9)** — one-way
  sync `GovernanceState` → `SystemConfiguration` only.
  Wrapper documents the unidirectional contract; reverse
  sync would need its own design.
- **`SystemConfiguration.budget_freeze_active` (row 21)** — separate
  control plane from GovernanceState. Wrapper documents
  the asymmetry until/unless the two planes get unified.
- **`HumanPreference` (row 30)** — `topic_weights` +
  `source_weights` fields exist but never populated.
  Wrapper documents which fields are reliable today
  (`approval_rate`, `total_decisions`, `avg_decision_time_ms`)
  vs. which are aspirational.
- **`HumanInterfaceService._update_preferences_from_decision()`
  (row 35)** — `source_weights` modification is local-only,
  not saved. Wrapper either fixes the save or documents the
  no-op.
- **`PUBLIC_INTEL_TOKEN` gate (row 43)** — default empty
  string = endpoint disabled. Wrapper documents the
  default-off-by-design semantic.
- **VIP scope injection (row 45)** — prompt-injection-only
  enforcement; PA can ignore directives. Wrapper documents
  the soft-enforcement boundary so consumers don't treat it
  as a hard gate.
- **`REMOVED_TOOL_ALIASES` (row 47)** — soft redirect, not
  hard block. Wrapper documents the migration-advice
  semantic.
- **`PA_USE_FUNCTION_CALLING` flag (row 61)** — False causes
  claude-code source short-circuit per memory rule. Wrapper
  documents the cross-flag dependency.

### DO NOT REUSE (0)

No governance primitive is so broken that it shouldn't be
reused. The 11 WRAPPER classifications cover all
known footguns.

### DEPRECATED (0)

No deprecated governance primitives identified at this
revision. Prior aliases (`boardroom_tool`, `human_decisions_tool`)
are already deprecated and absorbed into `governance_tool` per
`REMOVED_TOOL_ALIASES`.

### UNKNOWN (3)

- **`KillSwitch` enforcement at dispatch** (row 2 enforcement
  facet): no consumer found that reads `is_active` before
  acting on the target. Cannot classify until either a
  consumer ships or "no consumer by design" is documented.
- **`OrchestrationApprovalGate.check_auto_approvals()` trigger**
  (row 33): method exists at `orchestration_approval.py:214-262`
  but not in beat schedule. Caller unknown. Could be
  dormant or could be invoked by an undocumented site.
- **`JobContract.authority` runtime enforcement** (row 11
  enforcement facet): zero readers found. Cannot classify
  enforcement strategy until symbol mapping lands.

---

## 8. Architectural Findings

Synthesis of evidence into the canonical findings every future
authority discussion should start from.

### F1 — There are FOUR governance planes, not one

The platform has four distinct control planes that operate
mostly independently:

1. **Autonomy plane** — `GovernanceState` / `KillSwitch` /
   governance_tool / GovernanceEngine
2. **Authority plane** — `JobContract.authority` / `AuthorityLevel`
   / warn-mode `authority_contract_observed` event
3. **Budget plane** — `SystemConfiguration.budget_freeze_active`
   / LLMEnforcer / `check_retry_budget`
4. **Human governance plane** — `HumanAttentionItem` /
   `HumanFeedbackRecord` / `HumanPreference` /
   `OrchestrationApprovalGate` / lifecycle service

These planes do **not** compose today. Knowing this matters
because any future governance work has to declare which plane it
lives in. Cross-plane wiring is a deliberate design choice, not
a default.

### F2 — Authority enforcement is blocked on symbol mapping

S1264 warn-mode is the honest baseline given the gap. The
unblocking prereq is not a "feature flag flip" — it's
foundational design work to map policy-description strings
(e.g., `"modify_docs_files"`) to runtime symbols. Three options
exist per S1264 handoff:

1. **Steps self-declare:** add
   `Step.action_classes_invoked: tuple[str, ...]` so each
   step says what it might do; runner can cross-check vs.
   contract before invocation.
2. **Tool registry:** tools carry an `action_class` attribute;
   dispatcher emits `(tool, action_class)` evidence the
   runner can roll up.
3. **Hybrid:** both surfaces, with step declarations as
   authoritative and tool evidence as backstop.

Each has tradeoffs; **the choice is a design decision and is
out of scope for this research mission.**

### F3 — KillSwitch is write-only

The KillSwitch model + PA write actions + TTL expiry beat task
work. But **no consumer reads `KillSwitch.objects.filter(is_active=True, target=...)` before dispatching the targeted action.**
Spider tasks check governance mode but not kill switches.
Publishing surfaces don't check the `publishing` target.
Outbound HTTP doesn't check the `outbound` target. This is the
biggest "feature ships but doesn't work" gap in the autonomy
plane.

### F4 — Budget freeze is on a parallel rail

`SystemConfiguration.budget_freeze_active` is checked by
LLMEnforcer (`llm_enforcer.py:200-260`), allowing only
critical purposes (`governance`, `auth`, `incident_response`,
`pa_chat`) and the `PersonalAssistant` agent through during a
freeze. `GovernanceState.mode='freeze'` triggers one-way sync
to set `budget_freeze_active=True`
(`governance.py:2271-2273`), but **direct flips of
budget_freeze_active do NOT update GovernanceState.mode**.
Operators flipping the SystemConfiguration row by hand will
desync the two planes.

**Honesty note (Rigby S1269 SIGN clarification):** this is
current behavior; whether it is intentional vs. a bug is
outside this audit's scope to assert. The likely intent is
safety (LLM costs need a fast-path freeze that doesn't wait
for governance plumbing). The likely cost is an operator
footgun (the two planes can desync without observation).
A design call on whether the planes should converge is
flagged in §10.4 as future research.

### F5 — Human governance has the only learning loop

The post_save signal on `HumanFeedbackRecord` is the only
machine-learning feedback path that runs automatically per
decision. Positive feedback creates `AgentLearning` +
`LearningInsight` rows that downstream agents can query. Negative
feedback marks `requires_attention=True` for review. **No
equivalent path exists for inter-employee decisions** — when
Employee A's verdict shapes Employee B's behavior, there is no
training row created today (collaboration audit §1 F4 covers
this in detail).

### F6 — The 4 employees' authority dicts are converging on common patterns

Cross-employee analysis (from sub-agent #1) revealed:
- `open_pull_request` is **PROHIBITED across all 4 employees**
  (Rigby, Auditor, Chief, Triage)
- `recommend_remediations` is **RECOMMEND across 3 of 4**
  (Auditor, Chief, Triage)
- `modify_any_file` / `modify_docs_files` is **PROHIBITED across all 4**
- `delete_database_rows` is **PROHIBITED across 2 (Auditor, Triage)**
- `execute_arbitrary_code` is **PROHIBITED across 2 (Auditor, Triage)**
- `certify_mission_run` is **EXECUTE across 3 (Rigby, Auditor, Chief)**; **NOT declared in Triage** (Bug Triage uses `auto_emit_verdict=False`)

These common keys suggest a future shared-policy template
could lift cross-employee invariants out of per-job
duplication. But this is design work, not research, and is
flagged in §10 as a candidate sub-question for the symbol-
mapping mission.

### F7 — Schema version on the warn-mode event is dispatched write-only

`AUTHORITY_CONTRACT_SCHEMA_VERSION = 1` is emitted in every
event's detail but **no consumer branches on it**. This is
fine today (only one schema version exists), but means there's
no installed migration path when a future schema bump lands.
The downstream Bug Triage consumer would need to be updated
manually to honor newer schemas.

### F8 — Per-(agent/desk) governance scopes are aspirational

`GovernanceState.scope` supports `'global' | 'agent' | 'desk'`
but every production consumer reads `scope='global'` only.
Per-agent / per-desk overrides are model-supported but
runtime-absent. A future system that wants "freeze Rigby only,
not the platform" would need consumers to fall through global
→ agent overrides explicitly, which today they don't.

### F9 — `throttle` mode is dead

Three production consumers check for `freeze`/`safe_mode`; none
check for `throttle`. LLMEnforcer's "throttle" notion is on the
SystemConfiguration rail (`budget_downgrade_active`), not
GovernanceState. The throttle mode in GovernanceState is
documentation-only today.

### F10 — `HumanPreference.notification` rails are documentation-only

`quiet_hours_start/end`, `min_urgency_to_notify`,
`preferred_channel` are model fields with no consumers. HAI
notification senders use hardcoded channels (e.g., Discord
hardcoded channel IDs per Session 419) and don't filter by
recipient preferences.

---

## 9. Research Questions

Genuine open questions for future research. Not implementation
tasks. Not invented answers.

1. **Can authority become symbolic?**
   The S1264 discovery answered "not without prerequisite
   work." What is the smallest symbol-mapping primitive that
   would make authority enforceable? Three options named in
   F2; which is least invasive given the existing 68
   authority entries and 30 prohibited_actions?

2. **Can authority inherit?**
   If a "shared authority template" lifts cross-employee
   invariants (F6), should the per-employee dict carry only
   *deltas* from the template? Or should each employee
   continue to declare its full authority dict for review
   clarity at the cost of duplication?

3. **Should authority compose across employees?**
   If Employee A dispatches Employee B (the hypothetical
   inter-employee delegation that S1268 protocol sketch
   scopes), does Employee B inherit any of Employee A's
   authority, or does B's contract stand alone? Does the
   answer change if A is the *manager* of B (via
   `JobContract.manager` field)?

4. **How should delegation work in an authority model?**
   `JobContract` has a `manager` field set to `"chris"` for
   all 4 employees today. If a future employee has manager
   `"chief_of_staff"`, does Chief of Staff inherit any
   authority over that employee's mission? Or is `manager`
   purely a documentation field with no runtime effect?

5. **How should revocation work?**
   `GovernanceState.expires_at` and `KillSwitch.expires_at`
   are TTL-based. Authority dicts have no expiry. Should
   authority be time-bounded (e.g., a "temporary EXECUTE
   on `restart_worker` for the next 24h")? If so, what's
   the audit chain for grant + use + expiry?

6. **How should trust propagate?**
   `derive_status()` (`core/employees/status.py:53-251`)
   computes per-employee trust (certified/(certified+rejected))
   from OpsRun verdict counts. **Inter-employee trust** is
   not a primitive. If Bug Triage starts trusting Auditor's
   "critical" classifications, what's the trust contract?
   Hardcoded? Learned? Per-action-class?

7. **What happens to authority across multiple MissionRunners?**
   Today missions are isolated (daily idempotency, OpsRun
   per mission). If a single contract change should affect
   in-flight missions, what's the policy? Re-read on every
   step? Snapshot at mission start? Per-step?

8. **What survives restart, retry, replay?**
   `authority_contract_observed` events are `OpsRunEvent`
   rows — they survive DB restart by definition. But the
   *contract* itself is in code (frozen dataclasses), so a
   PR merge during an in-flight mission changes the
   contract mid-run. Is that intended? If not, what's the
   snapshot strategy?

9. **What does "authority drift" look like at scale?**
   Today 4 employees, 68 entries. At 20 employees and 300+
   entries, will drift become a problem? Should there be a
   diff tool? A migration framework?

10. **Should authority enforcement be opt-in per employee?**
    S1264 warn-mode is opt-in per
    `MissionRunnerConfig.job_contract is not None`. Future
    enforce-mode could keep the same opt-in shape (employees
    that haven't opted in stay unenforced). This is a
    backward-compat strategy that doesn't require a
    big-bang enforce flip.

11. **How does authority interact with feature flags?**
    The 12 feature flags (§2.7) are de facto authority
    gates ("you cannot do X unless flag is set"). Should
    flags be declared as authority entries with a special
    AuthorityLevel like `EXECUTE_IF_ENABLED('flag_name')`?
    Or are flags a separate layer?

12. **What's the right shape for cross-plane consistency?**
    F4 surfaces the GovernanceState ↔ SystemConfiguration
    one-way sync gap. Are these planes intended to converge
    or to stay deliberately separate? If converge: bidirectional
    sync. If separate: documented as parallel rails.

---

## 10. Future Research

Beyond the next research mission (§11), the following research
questions are likely to surface in later sessions. Listed in
priority order, no design content.

### 10.1 Symbol Mapping Architecture (P0 — recommended next, see §11)

### 10.2 Trust Propagation Model (P1)

If Employee A trusts Employee B's verdict, what's the contract?
Today `derive_status()` computes per-employee trust from
OpsRun verdict counts. Inter-employee trust is not a primitive.
This is named in the collaboration audit's §5.2 and §10 Q?,
but it deserves its own research doc once symbol mapping is
scoped.

### 10.3 Memory Architecture (P1)

How do employees remember each other's past verdicts? Today
they don't synthesize cross-employee memory (Bug Triage queries
OpsRun rows directly per run). A "cross-employee episodic
memory" layer would reuse `AgentMemory` / `AgentLearning` /
`LearningInsight` / `SharedKnowledge` — scope is research-only.

### 10.4 Cross-plane Consistency (P2)

The four governance planes (F1) don't compose. Research what
"compose" should mean and which planes should converge vs. stay
parallel. Tied to the F4 sync question.

### 10.5 Per-(agent/desk) Governance Activation (P2)

Per F8, the scope hierarchy is model-supported but runtime-
absent. If the platform grows to 20+ employees, per-employee
freeze ("pause Rigby but not the rest") will become useful.
Research what the minimum activation surface looks like.

### 10.6 Authority Expiry / Revocation (P3)

Per Q5: should authority be time-bounded? If yes, what's the
audit chain for grant + use + expiry? Tied to KillSwitch's
TTL-required design (F3) as the existing pattern.

### 10.7 HumanPreference Cleanup (P3)

`topic_weights` / `source_weights` / `notification` rails are
defined but not consumed. Research whether these should be
removed (deprecated) or wired up (activated).

### 10.8 Focus Mode Inventory (P? — flagged by Rigby S1269 review)

Rigby's S1269 review noted that **"focus mode"** is a
governance-like throttle that may live outside the
GovernanceState/KillSwitch plane. This audit did not scope
focus mode (wasn't part of the five evidence sweeps). A
follow-up scoping pass should determine whether focus mode
is a fifth governance plane, a sub-feature of one of the
existing four, or a distinct concept entirely. Priority
depends on whether Employee OS reasoning has any dependency
on focus mode state.

---

## 11. Recommendation

**The next research mission is: Symbol Mapping Architecture.**

### Why this one

Every other authority question depends on it:
- Authority enforcement is blocked (F2).
- Cross-employee authority propagation can't be defined without
  symbol-binding (Q3, Q4).
- Trust propagation requires per-action attribution, which
  requires symbols (Q6 + future research §10.2).
- Memory architecture for "what did Employee X try to do" needs
  the same symbol surface (future research §10.3).

Without symbol mapping, every other authority research mission
is academic.

### Scope of the recommended mission

**Research only.** The next doc should:

1. **Enumerate the design space.** Three known options from
   S1264 discovery (steps self-declare, tool registry,
   hybrid). Identify any other options that surface during
   research.
2. **For each option, document:**
   - What surfaces would need to declare what?
   - How would the runner cross-check?
   - Cost in code-review surface (e.g., does every step
     function gain a new declaration?)
   - Backward compatibility (can existing employees opt in
     gradually?)
   - Audit-chain impact (do OpsRunEvent labels change? does
     `evidence_for_mission()` need extension?)
3. **Inventory the action_class strings already in use.**
   68 entries across 4 employees (sub-agent #1's full
   enumeration). Surface the patterns from F6 (4-of-4
   shared keys, 3-of-4 shared keys, single-employee unique
   keys). Use this to scope the registry size.
4. **Identify the smallest viable v0.** Not full enforcement
   — the *smallest* shape that closes the symbol gap for *one*
   employee. The same "Auditor → Chief of Staff first
   inter-employee write path" pattern that drove the protocol
   sketch.
5. **Mark prerequisites.** What other research has to land
   first? (Probably nothing — symbol mapping is the prereq for
   everything else.)
6. **Recommend Rigby SIGN review areas** the same way prior
   missions did: design options, anti-duplication, gaps,
   architectural blind spots, canonical foundation.

### What this audit explicitly does NOT recommend

- Implementing authority enforcement. Wait for symbol mapping
  research to close first.
- Wiring KillSwitch enforcement. That's a separate design
  effort once the autonomy plane's contract is clearer (F3).
- Adding `topic_weights`/`source_weights` writers. F10
  observation; cleanup is P3.
- Cross-plane sync (`SystemConfiguration` ↔ `GovernanceState`).
  F4 observation; design is P2.
- Per-(agent/desk) consumer wiring. F8 observation; design is
  P2.

---

## 12. Appendix

### 12.1 Q1-Q12 explicit answers

**Q1 — What governance primitives already exist?**
63 inventoried in §2 across 7 sub-planes (autonomy, authority,
budget, human governance, auth + permission, tool dispatch,
feature flags). See §2.1-§2.7.

**Q2 — How does authority actually flow today?**
Trace in §3. Exists at git/PR, dispatch surfaces, tool
boundaries, telemetry. Implied at step bodies + recommend_*
declarations + prohibited_actions tuples. Disappears between
MissionRunner and step.fn execution (symbol-mapping gap), across
employees (no propagation), inside ToolDispatcher (no
contract-level read).

**Q3 — What does "authority" currently mean?**
Four levels (`AuthorityLevel`: OBSERVE, RECOMMEND, EXECUTE,
PROHIBITED). Used in 4 employees' `JobContract.authority` dicts
(68 total entries). Ignored at runtime (zero readers). Used at
code review (PR gates contract changes). Captured in warn-mode
telemetry (`authority_contract_observed` event). NOT runtime-
enforced (F2).

**Q4 — How does warn-mode actually behave?**
Per §3 mid-section and Finding #6 in sub-agent #1's report:
emits one `authority_contract_observed` info-type OpsRunEvent
per mission, right after `run_started`. Detail includes
schema_version=1, employee_handle, contract_title,
contract_version_tag (16-char SHA-256 prefix), counts by
AuthorityLevel, prohibited_actions_count, `mode='warn'`. NEVER
blocks; malformed contract sets `summary_acc.degraded_evidence=True`
and logs ERROR but mission continues. **What happens today if
authority is violated? NOTHING — there is no violation detection.
Steps invoke whatever they invoke; no runtime check compares
to the contract.**

**Q5 — Where are the enforcement boundaries?**
35 gates inventoried in §4. 29 RUNTIME-VERIFIED (auth
middleware, DRF permissions, service tokens, tool dispatcher
guards, feature flags, autonomy plane freeze/safe_mode,
LLMEnforcer budget, retry budget, source routing, fleet
routing, workspace-aware dispatch, OpenAI reasoning guard). 5
ASPIRATIONAL (REMOVED_TOOL_ALIASES soft redirect, VIP scope
prompt injection, PUBLIC_INTEL_TOKEN default-off,
JobContract.authority enforcement, OrchestrationApprovalGate
auto-approve trigger). 1 UNKNOWN (KillSwitch dispatch checks).

**Q6 — What would true enforcement require?**
Per F2 + §11 recommendation. Required concepts (not designs):

- **Authority symbol mapping** (action_class strings → runtime
  symbols)
- **Step-level declaration OR tool-level registry OR hybrid**
- **Pre-invocation check** (runner cross-checks declared vs.
  contract before dispatch)
- **Violation event taxonomy** (what OpsRunEvent label fires
  on detect? `authority_violation_observed`?)
- **Backward-compat opt-in** (employees that haven't opted in
  stay unenforced)
- **Failure mode** (block vs. surface attention vs. log only)

Plus the deferred concepts (Q5):

- **Authority expiration / TTL** (today none)
- **Cross-employee delegation contracts** (today none)
- **Inheritance / template** (today every dict is standalone)
- **Trust propagation** (today per-employee only)
- **Revocation** (today implicit via PR revert)
- **Composition** (today no compose primitive)

**Q7 — Human governance.**
Inventoried in §2.4 and §5. Auto-driven: lifecycle service
(escalate/dismiss/auto-approve), HumanFeedbackRecord signal
cascade (FeedbackProcessor → AgentLearning/LearningInsight),
HumanPreference.update_learned_stats. Human-driven: viewing,
decision recording, manual override, OrchestrationApprovalGate
decisions, verification outcome.

**Q8 — Authority propagation.**
Current (§3): Human → Employee → Mission → Tool. Authority
**TERMINATES** at the tool boundary: tools have their own
dispatch gates (messaging, reasoning, Rigby-gating) but don't
read `JobContract.authority`. Future unknowns named in §10
(Trust Propagation P1, Cross-plane Consistency P2).

**Q9 — Failure history.**
12 governance-specific incidents in §6: 3 NEW (authority
symbol-mapping gap S1264, auth middleware silent error S1171
PR #2328, HTTP API permission flip S1265 PR #2760); 9
referenced from collaboration audit §7 with relevance
scoring.

**Q10 — Reuse classification.**
Per §7: 48 SAFE, 11 WRAPPER, 0 DO-NOT-REUSE, 0 DEPRECATED, 3
UNKNOWN.

**Q11 — Open Questions.**
12 research questions in §9. Top three for the next mission:
Q1 (can authority become symbolic?), Q2 (can authority
inherit?), Q3 (should authority compose across employees?).

**Q12 — Recommendation.**
Symbol Mapping Architecture as the next research mission. Per
§11. Research-only. Scoped to the smallest viable v0 (one
employee, one action_class registry pattern). Pre-requisite
for every other authority research.

### 12.2 Cross-reference

| Prior research | Relationship |
|---|---|
| `docs/EMPLOYEE_OS_PRIMITIVES.md` row 17 | This doc's §2.1 row 1-2 expand the GovernanceState + KillSwitch entries with runtime consumer detail |
| `docs/research/employee_os_communication_substrate_audit.md` §4.7 (messaging guard) | Reused; classified SAFE TO REUSE at row 46 |
| `docs/research/employee_os_communication_protocol_sketch.md` §8.1 (Auditor has no HAI authority) | Reused as evidence that Auditor authority dict (row 11) does NOT include `create_human_attention_item` (confirmed by sub-agent enumeration of 15 entries) |
| `docs/research/employee_os_collaboration_patterns.md` §2 rows 55-56 (GovernanceState + KillSwitch SAFE classification) | This doc's §2.1 rows 1-2 sharpen the classification: GovernanceState SAFE for freeze/safe_mode; KillSwitch WRAPPER (write+status only, no enforcement) |
| `docs/research/ARCHITECTURE_INDEX.md` §5.1 (Governance + Authority Evolution P0 next) | This doc IS that mission. Index will need update per §10 of the index |

### 12.3 Documentation drift surfaced

| Item | Source A says | Source B (runtime) says | Resolution |
|---|---|---|---|
| Bug Triage `MissionRunnerConfig.job_contract` wiring | Sub-agent #1 said ASPIRATIONAL | `core/jobs/bug_triage.py:1169` passes `job_contract=BUG_TRIAGE_JOB` | RUNTIME-VERIFIED. Sub-agent #1 wrong. Bug Triage IS emitting `authority_contract_observed` per S1267 V13 verification (start-here doc references "first Bug Triage authority_contract_observed event extending S1264 prereq #2 baseline N=1→N=2"). Folded into §2.2 row 11 + §7 SAFE classification. |
| `OrchestrationApprovalGate.check_auto_approvals` caller | Sub-agent reports it's NOT in beat schedule | Confirmed via grep — `core/celery.py` has no entry for `check_auto_approvals` | UNKNOWN preserved. Flagged in §2.4 row 33 and §11 as not recommended for reuse until caller is identified. |
| `HumanPreference.topic_weights` / `source_weights` writers | Sub-agent #4 reports these fields are NEVER POPULATED | Confirmed — no `topic_weights =` assignment found; `source_weights` modified in local dict but not saved | RUNTIME-VERIFIED gap. Captured in F10 + Q11 as future research. |

### 12.4 Evidence integrity notes

- Five parallel Explore sub-agents produced the source material
  for §2-§6 (authority dicts deep-dive, runtime enforcement
  points inventory, GovernanceState + KillSwitch consumers,
  human governance lifecycle deeper, governance-specific
  failure history).
- Load-bearing claims re-verified by Claude with direct
  Grep/Read before this doc was written:
  - `core/jobs/bug_triage.py:1169` (`job_contract=BUG_TRIAGE_JOB`
    — corrects sub-agent #1 ASPIRATIONAL claim)
  - `core/jobs/docs_cascade.py:726` (`job_contract=DOCUMENTATION_MANAGER`)
  - `core/jobs/morning_brief.py:556` (`job_contract=MORNING_BRIEF_JOB`)
  - `core/jobs/platform_audit.py:930` (`job_contract=PLATFORM_AUDIT_JOB`)
  - All 4 employees confirmed wired to MissionRunner warn-mode
    emission path.
- No code changes made writing this doc.
- All "today" / "is" language describes runtime state verified
  by direct file read; all "should" / "could" language is
  research conjecture marked as such.
- Rigby's S1269 review additions re-verified by Claude:
  - Plane count consistency: §1 Exec Summary now matches F1's
    "four planes" framing (was "two parallel" + "Plus separate"
    + "And human governance plane" — confusing for future readers)
  - Gate count consistency: §1 F3 now reads "35" matching §4's
    table totals at the bottom of §4.8 (was "34" — off by 1)
  - JobContract.authority WRAPPER refinement: now explicit
    "SAFE-TO-REUSE-as-telemetry but DO-NOT-REUSE-for-enforcement"
    framing per Rigby's "don't label globally DO-NOT-REUSE
    because warn-mode telemetry is genuinely useful"
  - F4 budget-plane wording: now reads "current behavior;
    intent outside this audit's scope to assert" instead of
    implying the desync gap is a bug or a design choice
- Rigby's verdict on the headline findings (S1269 review):
  - F2 (symbol mapping as load-bearing blocker) — **SIGN-clean**
  - F3 (KillSwitch is write-only) — **SIGN-clean**, independently
    corroborated by Rigby's own grep showing KillSwitch
    consumers limited to model + ops_autopilot services (no
    worker/scheduler/spider/task hits)
  - F6 (authority dict convergence) — **SIGN-clean**, deferring
    shared-template design is appropriate for a research anchor
  - F9 (throttle mode is dead) — **SIGN-clean**
  - §11 Symbol Mapping Architecture as P0 next mission —
    **SIGN-clean**, with Rigby's specific Q1>Q3>Q2 priority
    ranking for the future research roadmap
  - Open-question priorities (§9) — Rigby refined the order:
    Q1 (symbolic) is true P0; Q3 (compose) second; Q2 (inherit)
    third. Rationale: everything waits on symbols, then
    composition is needed before inheritance is meaningful.
- Rigby also noted **focus mode** as a possible governance-like
  throttle that may live outside the GovernanceState/KillSwitch
  plane and could be worth surfacing in a future revision.
  Flagged in §10 as a candidate addition; not folded into §2
  this pass because focus mode wasn't part of the original five
  evidence sweeps and would require its own targeted research.
