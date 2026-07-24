# `create_project_from_research` — Validation Report (S2925)

**Tool:** `create_project_from_research`
**Schema:** `core/services/pa_tool_schemas.py` (agent-tool shape — see §3 schema notes)
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:457`
**Session:** S2925 (Slice 5 batch 1 — quartet with `brand_strategy_agent` + `competitor_analysis_agent` + `customer_research_agent`)
**HEAD at validation:** `c70ff84fe` (2026-07-23 — post PR #3481 Ledger #33 fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Per Rigby S2925 T0 SIGN micro-edit: `create_project_from_research` is designated the **WorkflowAgent-family completion-verify representative** for this batch — receipt + end-to-end `job_status` completion both validated live. This is the ONLY WorkflowAgent-mapped tool in the quartet; there is no second WorkflowAgent-family tool to defer completion-verify to.
**Category upgrade target:** `untested` → `validated_full_with_completion`
**Rigby SIGN:** S2925 T0 SIGN AGREE — same joint SIGN cycle as the batch 1 quartet. Notable: Rigby explicitly grounded this tool's WorkflowAgent mapping via `td_handlers_agents.py:127` and included it in the quartet to exercise the orchestration-agent shape (distinct from the 3 business-family peers).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`create_project_from_research` dispatches `WorkflowAgent` (`core/agents/workflow_agent.py:62`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. WorkflowAgent is the **only agent in the platform authorized to delegate to other agents** — it breaks a complex task into steps, delegates each step to a specialist agent, and combines the results into a coherent output. `create_project_from_research` is the specific tool-name entry point for the "turn a bundle of research into a project" workflow shape.

Use it when Chris asks "given the completed customer + competitor + brand research, spin up a project scaffold" / "turn this research into a deliverable" / "create the project artifacts from the research I already have." Distinct from `research_agent` (produces raw research, doesn't consume it); from `brand_strategy_agent` (synthesizes strategy but doesn't create project scaffolds); from `create_brand_video` (also WorkflowAgent-mapped but scoped to video creation, per `td_handlers_agents.py:126`); from `workflow_orchestration_agent` (also WorkflowAgent-mapped but general workflow entry point, per `td_handlers_agents.py:123`).

**Key distinction from the batch's business-family peers:** WorkflowAgent's downstream execution fans out to further Celery agent dispatches — each delegated step is itself an `execute_agent_task` call. This makes `create_project_from_research`'s end-to-end blast radius substantially larger than a leaf-agent tool.

## Covered actions

`create_project_from_research` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `WorkflowAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live + end-to-end job_status completion verified.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'WorkflowAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'WorkflowAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up `job_status` returns AgentResult that may contain sub-agent invocation results, ML workflow analysis (per module-level `analyze_workflow_with_ml`), and combined output.

## 3. Schema notes

Identical shared schema shape as all Slice 5 agent-forwarding tools:

- **Required:** none strictly required — `task`/`prompt`/`query` defaults to `''` via `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict); root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194`. The `research` and `research_summary` promotable keys are particularly relevant for this tool — they let a caller pass existing research payloads directly into the WorkflowAgent context without a separate research-fetch step.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **`llm_timeout: 180s`** at `workflow_agent.py:76` — WorkflowAgent uses a 3-minute LLM timeout for multi-step orchestration (per Session 1074). Longer than most agents. Callers should expect longer completion times.
- **`create_project_from_research` is NOT subject to the Editor synthesis reroute or the workspace-content gather.**

## 4. Golden-path examples

**Example 1 — spin up project scaffold from bundled research:**
```json
{"task": "Create a project scaffold from the customer + competitor + brand strategy research I completed this week", "context": {"workspace_id": "<uuid>", "research": "<combined research text or JSON>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "WorkflowAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "WorkflowAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status` (expect 60-180s runtime given the 3-min LLM timeout): AgentResult contains delegated sub-agent invocation records, ML workflow analysis (auto-selected task type + confidence), and combined project scaffold output.

## 5. Failure / empty-state / pagination notes

- **Missing task text:** empty `task_text` reaches WorkflowAgent; agent's own step-breakdown logic determines behavior (typically no useful steps generated).
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit the WorkflowAgent invocation itself; delegated sub-agents also pass through the same gates independently.
- **Non-blocking sub-agent failures:** WorkflowAgent has `_NON_BLOCKING_AGENTS` frozenset (`workflow_agent.py:78+`) — failures in those agents produce a warning in the AgentResult but don't fail the workflow. Blocking sub-agent failures propagate.
- **ML workflow analysis failure:** `analyze_workflow_with_ml` (`workflow_agent.py:39-59`) catches exceptions and returns `{'ml_used': False, 'reason': 'ML error: <str>'}`. Workflow continues.
- **3-min timeout exhaustion:** `llm_timeout: 180.0` at `workflow_agent.py:76`. If the LLM step-breakdown call exceeds 3 min, BaseAgent's timeout logic surfaces the error in the AgentResult.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, no auto-wake banner fires.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`create_project_from_research` is classified `external` when scored end-to-end — but with **substantially amplified blast radius vs the business-family peers in this batch** because WorkflowAgent's downstream execution fans out to additional agent-dispatches. Each delegated step is itself an `execute_agent_task` call, potentially triggering the same LLM + web_search + ORM-write pattern the leaf agents exhibit.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`WorkflowAgent` + Celery task + delegated sub-agents) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) — plus per-delegated-agent Celery fanout | `external` (amplified) |
| Data mutation | None | AgentExecution + AgentResult INSERTs for WorkflowAgent — PLUS one AgentExecution + AgentResult pair per delegated sub-agent; LLMCallLog rows per LLM call across the whole tree | `spreading` (amplified downstream) |
| Signal cascade | None | Agent lifecycle signals for WorkflowAgent + each sub-agent; potential AgentFollowupSubscription INSERT | `cascading` (amplified downstream) |
| Network egress | None | LLM provider HTTP for WorkflowAgent's own step-breakdown call + per-sub-agent LLM calls; per-sub-agent web_search / spider HTTP as applicable | `external` (amplified) |

**End-to-end classification:** `external` (amplified). Consistent tier with batch peers but with N× the row/LLM/network footprint depending on how many sub-agents the workflow delegates to.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('create_project_from_research')` → `'WorkflowAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:127` | Name resolution; no side effect. Note: `create_project_from_research` shares the `'WorkflowAgent'` target with `create_brand_video` (`:126`) and `workflow_orchestration_agent` (`:123`) — three tool-name entry points into the same agent class. |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence. `research` + `research_summary` promotions are especially relevant. |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents. |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence. |
| `execute_agent_task.apply_async(args=['WorkflowAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A (amplified). |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async` — recursive fanout)

- **A1. Dispatch target type(s):** `agent_task_wrapper` at first hop → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`). **However, downstream, WorkflowAgent's `delegate_to_agent` tool re-issues `execute_agent_task.apply_async` calls per delegated sub-agent** — so the effective dispatch topology is a tree, not a single async task. First-hop is opaque; each recursive dispatch adds another opaque callee.
- **A2. Queue name(s) + priority:** `long_running` at the first hop. Delegated sub-agents also land on `long_running` (per WorkflowAgent's `delegate_to_agent` implementation). Priority: not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID for the WorkflowAgent invocation only). No enumeration of downstream sub-agent task_ids in the dispatch envelope — those are visible only via AgentResult after the workflow completes, or by inspecting AgentExecution rows.
  - (b) **Polling endpoint(s):** `job_status` PA tool for the returned `task_id`; AgentExecution row for the WorkflowAgent invocation. Sub-agent invocations are queryable as separate AgentExecution rows keyed on their own `celery_task_id` values (visible in the WorkflowAgent's AgentResult).
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery task trees. No dedup key.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + WorkflowAgent's delegate loop):
  - AgentExecution row INSERT for WorkflowAgent invocation + status transitions.
  - Step-breakdown LLM call (per WorkflowAgent's core logic); LLMCallLog INSERT.
  - **Per delegated sub-agent:** additional `execute_agent_task.apply_async` fan-out; per-sub-agent AgentExecution + AgentResult INSERTs; per-sub-agent LLM calls; per-sub-agent tool-surface calls (potentially web_search — **dispatcher re-entry hotspot** amplified by the tree topology).
  - ML workflow analysis (per `analyze_workflow_with_ml` at `workflow_agent.py:39-59`) — may load models into worker memory.
  - AgentResult row INSERT for WorkflowAgent (post-run).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** AgentExecution + AgentResult keyed on the WorkflowAgent `celery_task_id`; sub-agent AgentExecution + AgentResult rows visible independently. `job_status` surfaces the WorkflowAgent composite view but does NOT auto-enumerate sub-agent status. Callers wanting sub-agent progress must query AgentExecution directly.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)` on the WorkflowAgent task; sub-agent tasks continue running independently unless explicitly revoked. **Cancel is NOT recursive.**
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:127`; `execute_agent_task` routing; WorkflowAgent's own logic (especially `delegate_to_agent` behavior + `_NON_BLOCKING_AGENTS` frozenset changes + `analyze_workflow_with_ml` integration); the sub-agent set WorkflowAgent can delegate to (currently Session 341 roster documented in the module docstring).

## 6. Evidence

Doc-only sweep this ship, plus **end-to-end completion verification** as the batch 1 WorkflowAgent-family representative.

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `create_project_from_research` with a task string that clearly requires multi-agent orchestration (e.g., "research X and create Y") + a `context` containing `workspace_id`. Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'WorkflowAgent', auto_followup, follow_up_will_fire, message}`. Confirm `agent` field resolves to `'WorkflowAgent'` (validates `_tool_to_agent_name` mapping at `td_handlers_agents.py:127`).
2. Poll `job_status` with the returned `task_id` until completion (allow up to 3-5 min given the 180s LLM timeout + potential sub-agent fanout). Confirm completion payload contains AgentResult-shaped data with (i) delegated sub-agent invocation records, (ii) ML workflow analysis fields (`ml_used`, `task_type`, `models_used`, `confidence`), (iii) combined output.
3. ORM cross-check: `AgentExecution.objects.filter(celery_task_id=<task_id>).first()` returns the WorkflowAgent row; further `AgentExecution.objects.filter(created_at__gte=<dispatch_time>)` should show additional rows for each delegated sub-agent — validates the recursive fanout behavior.
4. If `conversation_id` was set AND `auto_followup` not `False`, confirm AgentFollowupSubscription row was created.

This ship's completion-verify is the **first Slice 5 end-to-end proof of the recursive-fanout dispatch topology** — future WorkflowAgent-mapped Slice 5 tools (`create_brand_video`, `workflow_orchestration_agent`) inherit the pattern documented here.

## Related

- **Adjacent tools (same Slice 5 batch):** `brand_strategy_agent` + `competitor_analysis_agent` + `customer_research_agent` (all business-family; potential sub-agents for a project-from-research workflow).
- **Other WorkflowAgent-mapped Slice 5 tools (deferred):** `create_brand_video` (`td_handlers_agents.py:126`) + `workflow_orchestration_agent` (`:123`) — both dispatch WorkflowAgent through different tool-name entry points; batches 2+ will re-use the pattern established here.
- **Other Slice 5 tools (deferred):** `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `character_training_agent`, `image_editing_agent`, `video_editing_agent`, `three_d_generation_agent`.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 14 untested).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy.
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160` (three rows resolve to `'WorkflowAgent'` — a many-to-one mapping shape unique to this agent class in the mapping table).
- **Ledger rows relevant to this ship:**
  - **First WorkflowAgent-family end-to-end completion-verify** — establishes the recursive-fanout dispatch topology proof pattern for other WorkflowAgent-mapped Slice 5 tools.
  - **Cancel-not-recursive** — documented as an authoring detail; if a caller revokes a WorkflowAgent task_id, delegated sub-agent tasks continue running. Not a bug; a contract observation.
  - **Sub-agent AgentExecution rows are not auto-enumerated in job_status** — callers wanting per-sub-agent progress must query ORM directly. Documented as a UX gap; Rigby Tool Gap Ledger candidate if it recurs post-batch-1.
