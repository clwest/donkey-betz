# `create_brand_video` — Validation Report (S2926)

**Tool:** `create_brand_video`
**Schema:** `core/services/pa_tool_schemas.py` (agent-tool shape — see §3 schema notes)
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:455`
**Session:** S2926 (Slice 5 batch 2 — quartet with `video_editing_agent` + `three_d_generation_agent` + `character_training_agent`)
**HEAD at validation:** `cea3f9215` (2026-07-24 — post PR #3484 AgentTaskExecution heartbeat wrong-model fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Per Rigby S2926 T0 SIGN Q3 verdict: `create_brand_video` is the batch 2 **WorkflowAgent-family completion-verify representative** — validates whether the tool_name (vs `create_project_from_research`) drives different WorkflowAgent behavior when the internal `execute_tool` loop is tool_name-agnostic (`workflow_agent.py:606–622` branches only on `delegate_to_agent`).
**Category upgrade target:** `untested` → `validated_full_with_completion`
**Rigby SIGN:** S2926 T0 SIGN + turn 2 grounded verify (11+ `repo_tool` + `execution_history_tool` receipts). Q3 verdict: cover ONE WorkflowAgent-family tool in batch 2 (`create_brand_video`); defer `workflow_orchestration_agent` to batch 3 pending mapping-vs-class-file asymmetry investigation (see §Related).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`create_brand_video` dispatches `WorkflowAgent` (`core/agents/workflow_agent.py`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. WorkflowAgent is a generalist orchestrator that uses `delegate_to_agent` (its sole `execute_tool` branch) to fan out subtasks to specialized agents. When invoked via `create_brand_video`, the intent surfaced by the tool_name is video-focused brand asset creation — typical fanout would delegate to `BrandStrategyAgent` / `BrandIdentityAgent` / `VideoAgent` in sequence.

Distinct from `create_project_from_research` (batch 1, S2925 — general project-scaffolding intent through the same `WorkflowAgent`); from `workflow_orchestration_agent` (also maps to `WorkflowAgent` per current mapping — see §Related for the class-file asymmetry with `WorkflowOrchestrationAgent`); from `video_generation_agent` / `video_editing_agent` (single-purpose media agents, not orchestrators).

## Covered actions

`create_brand_video` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `WorkflowAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live + end-to-end completion verified.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'WorkflowAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'WorkflowAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up `job_status` returns AgentResult with the orchestration output; sub-agent AgentExecution rows appear in ORM (traversable via `parent_execution_id`), not auto-enumerated in the composite `job_status` view — same known UX gap flagged for `create_project_from_research` at S2925.

## 3. Schema notes

Identical shared schema as all Slice 5 agent-forwarding tools:

- **Required:** none — `task`/`prompt`/`query` defaults to `''` via `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict); root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194`.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **Tool_name is NOT propagated to WorkflowAgent** — the wrapper resolves tool_name → agent class name via `_tool_to_agent_name` at `td_handlers_agents.py:127` and dispatches `execute_agent_task.apply_async(args=['WorkflowAgent', task_text, context], ...)`. WorkflowAgent receives ONLY the caller's `task` string and `context` dict — not the originating tool_name. Any differentiation between `create_brand_video` / `create_project_from_research` / `workflow_orchestration_agent` behavior must therefore come from the caller's task-text shaping (e.g., an LLM caller that constructs different task strings per tool_name).

## 4. Golden-path examples

**Example 1 — video-focused brand asset workflow:**
```json
{"task": "Create a brand video package for a fitness-tracking wearable — logo, tagline, 15s promotional video script + storyboard", "context": {"workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "WorkflowAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "WorkflowAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: AgentResult contains the orchestration plan + delegated agent outputs (recursive fanout — sub-agent AgentExecutions appear in ORM keyed on `parent_execution_id`, but the composite `job_status` view does NOT auto-enumerate them; batch 1 flagged this as a UX gap for `create_project_from_research`).

## 5. Failure / empty-state / pagination notes

- **Missing task text:** `task_text` reaches WorkflowAgent as empty string; WorkflowAgent's LLM planner may attempt a generic plan or fail-loud in its own validation.
- **Unknown execute_tool call by planner:** if WorkflowAgent's LLM planner emits a tool_call other than `delegate_to_agent`, `execute_tool` at `workflow_agent.py:619-622` returns `{'error': f"Unknown tool: {tool_name}. WorkflowAgent only supports delegate_to_agent."}` and the sub-call is dropped.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit the parent or any delegated sub-agent independently.
- **Recursive fanout timeout:** WorkflowAgent's LLM planning loop uses the standard 3-min LLM timeout; long fanouts may hit that per-step. Sub-agent AgentExecutions can still be in-progress after the parent transitions to completed if delegates are dispatched async (batch 1 create_project_from_research observed a subsequent CompetitorAnalysisAgent execution still in-progress at session close).
- **Cancel is not recursive across the WorkflowAgent tree:** revoking the parent's `celery_task_id` does NOT auto-revoke sub-agent Celery tasks (batch 1 authoring detail; documented for `create_project_from_research`).
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, the S1178 auto-wake subscription will NOT fire.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`create_brand_video` is classified `external` when scored end-to-end, and **amplified** by recursive fanout (same as batch 1's `create_project_from_research`): the WorkflowAgent's LLM planner may delegate to any registered agent, which in turn may dispatch further sub-tools.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`WorkflowAgent` + recursive fanout + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) + N sub-agent Celery tasks | `external` (amplified) |
| Data mutation | None | AgentExecution + AgentResult INSERTs for parent + each delegated sub-agent; LLMCallLog rows for planner + each sub-agent | `spreading` (downstream, amplified) |
| Signal cascade | None | Agent lifecycle signals × (1 + N delegates); potential AgentFollowupSubscription INSERT for the parent | `cascading` (downstream, amplified) |
| Network egress | None | LLM provider HTTP × (1 planner + N delegates); potentially spider queries, web_search, media provider APIs from delegates | `external` (amplified) |

**End-to-end classification:** `external`. Amplification factor is dynamic — depends on what the LLM planner delegates to. Per Rigby S2925 Q2 authoring guidance: Slice 5 tools MUST be classified end-to-end; recursive fanout is documented as an authoring detail (1st corroborating instance beyond batch 1's `create_project_from_research`; still gated from Fold promotion per S2925 forbidden entry, requires 2 more instances).

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('create_brand_video')` → `'WorkflowAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:127` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['WorkflowAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier. Sub-agent `celery_task_id`s appear ONLY in ORM (queryable via `AgentExecution.objects.filter(parent_execution_id=<parent_ae_id>)`) — the composite `job_status` view does not auto-enumerate them (known UX gap, batch 1).
  - (b) **Polling endpoint(s):** `job_status` PA tool for parent completion; ORM traversal for sub-agent enumeration.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution trees.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `WorkflowAgent.run`):
  - Parent AgentExecution INSERT + status transitions.
  - WorkflowAgent LLM planning call(s) (`core/agents/workflow_agent.py:405+`); LLMCallLog INSERT per call.
  - For each `delegate_to_agent` tool_call emitted by the planner: sub-agent dispatch through the same or adjacent handler; sub-agent AgentExecution + AgentResult INSERTs; sub-agent LLMCallLog rows; potentially sub-agent web_search / spider / media provider egress.
  - Parent AgentResult INSERT (post-run).
  - Optional AgentFollowupSubscription INSERT for parent if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** parent AgentExecution + AgentResult keyed on parent `celery_task_id`; sub-agent AgentExecutions keyed on `parent_execution_id` (ORM-only enumeration). `job_status` surfaces the parent composite view.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)` on the parent does NOT recursively revoke sub-agent Celery tasks (authoring detail, batch 1). Sub-agent cancel requires enumerating + revoking each sub-`celery_task_id` individually.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:127`; `execute_agent_task` routing; WorkflowAgent's planning loop or `execute_tool` branching (`workflow_agent.py:606-622` — currently only handles `delegate_to_agent`); addition of a `create_brand_video`-specific pre-processing branch in `_handle_agent_tool` (currently none).

## 6. Evidence

Doc-only sweep this ship, plus **end-to-end completion verification** as batch 2's WorkflowAgent-family representative (Rigby Q3 verdict).

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `create_brand_video` with a minimal task string via PA. Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'WorkflowAgent', auto_followup, follow_up_will_fire, message}`. Confirm `agent` field resolves to `'WorkflowAgent'` (validates `_tool_to_agent_name` mapping at `td_handlers_agents.py:127`).
2. Poll `job_status` with the returned `task_id` until completion or timeout. Confirm completion payload contains WorkflowAgent AgentResult; capture the tool_calls list emitted by the planner.
3. ORM traversal: `AgentExecution.objects.filter(parent_execution_id=<parent_ae_id>)` — enumerate sub-agent executions delegated by the planner. Confirm at least one sub-agent execution row exists (validates recursive fanout under a distinct tool_name from batch 1's `create_project_from_research`).
4. **Semantic-alias check (Q3 payoff):** compare the planner's `tool_calls` list from `create_brand_video` dispatch vs the S2925 `create_project_from_research` dispatch (parent execution `9035879f-c816-4689-95d0-146db6eeb642`). If the delegation patterns differ meaningfully by tool_name — even though tool_name is not propagated — that means the CALLER (Rigby LLM) is shaping the task string differently per tool_name. If patterns are identical, `create_brand_video` and `create_project_from_research` are semantic aliases at the platform layer.

## Related

- **Adjacent tools (same Slice 5 batch):** `video_editing_agent` + `three_d_generation_agent` + `character_training_agent` (media-family peers).
- **Sibling WorkflowAgent-mapped tools:** `create_project_from_research` (batch 1 S2925 — the first WorkflowAgent completion-verify); `workflow_orchestration_agent` (deferred to batch 3 pending investigation — mapping at `td_handlers_agents.py:123-127` routes tool_name to `WorkflowAgent` even though a `WorkflowOrchestrationAgent` class exists at `core/agents/workflow_orchestration_agent.py:105+` with 16+ built-in workflow templates. Whether this is an intentional wrapper strategy or a stale mapping is TBD).
- **Other Slice 5 tools (deferred to batches 3+):** `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `image_editing_agent`, `workflow_orchestration_agent` (6 remaining after batch 2).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 10 untested pre-batch-2).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925 Slice 5 batch 1 quartet (opened Slice 5 at 4/14).
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; WorkflowAgent implementation at `core/agents/workflow_agent.py` (753 lines, `execute_tool` only branches on `delegate_to_agent`).
- **Ledger rows relevant to this ship:**
  - Second corroborating instance of WorkflowAgent recursive fanout topology (1st = batch 1 `create_project_from_research`; still gated from Fold promotion per S2925 forbidden entry requiring 3+ instances).
  - Semantic-alias check for `create_brand_video` vs `create_project_from_research` — first exercise this ship; result documented in evidence §6 step 4 post-verify.
  - Mapping-vs-class-file asymmetry for `workflow_orchestration_agent` — surfaced this session, deferred to batch 3.
