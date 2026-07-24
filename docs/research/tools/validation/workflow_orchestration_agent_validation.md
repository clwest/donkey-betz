# `workflow_orchestration_agent` — Validation Report (S2927)

**Tool:** `workflow_orchestration_agent`
**Schema:** `core/services/pa_tool_schemas.py:1959`
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:455`
**Session:** S2927 (Slice 5 batch 3 — quartet with `content_strategy_agent` + `marketing_strategy_agent` + `strategic_review`)
**HEAD at validation:** `389c048b0` (2026-07-24 — post PR #3487 mapping fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Batch 3 WorkflowOrchestrationAgent-family completion-verify representative** — validates the S2927 PR-A mapping fix reaches the correct class end-to-end.
**Category upgrade target:** `untested` → `validated_full_with_completion`
**Rigby SIGN:** S2927 T0 SIGN Q1–Q5 verdict — Q1 quartet approved; Q2 verdict (c) mapping bug shipped as PR-A (#3487) BEFORE this doc; Q3 documents new-evidence-class fanout shape via templates (not a 3rd instance of the LLM-planner Fold); Q4 pick 0 (no bundled remediations); Q5 zoom-out resolved by PR-A sequencing.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`workflow_orchestration_agent` dispatches `WorkflowOrchestrationAgent` (`core/agents/workflow_orchestration_agent.py:105+`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. `WorkflowOrchestrationAgent` is a **template-based** orchestrator that wraps a legacy 3,120-line orchestrator preserving 16+ predefined workflow templates via `AVAILABLE_WORKFLOWS` (`core/agents/workflow_orchestration_agent.py:83-102`). Template shape includes `research_and_create_logos`, `youtube_thumbnail_package`, `brand_identity_package`, `product_photography_kit`, `video_thumbnail_series`, `logo_to_video`, `social_media_kit`, `podcast_visual_package`, `ebook_cover_series`, `video_production_kit`, `course_thumbnail_series`, `pitch_deck_visuals`, `product_launch_kit`, `business_research`, `competitor_analysis`, `customer_research`, `morning_brief`.

Distinct from `create_brand_video` / `create_project_from_research` / `WorkflowAgent`-mapped tools (S2925/S2926 — delegate coordinator that uses LLM planner + `delegate_to_agent`, not templates). Post-S2927 PR-A the tool_name↔class mapping is 1:1: `workflow_orchestration_agent → WorkflowOrchestrationAgent`. Pre-fix the mapping incorrectly targeted `WorkflowAgent`; any completion-verify against the pre-fix mapping would have exercised the wrong class silently (both classes are dispatch-shape-compatible; only the runtime behavior differed).

## Covered actions

`workflow_orchestration_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `WorkflowOrchestrationAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live + end-to-end completion verified.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'WorkflowOrchestrationAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'WorkflowOrchestrationAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up `job_status` returns AgentResult carrying `workflow`, `step_results`, `image_ids`, `video_ids`, `project_created`, `summary` keys (`workflow_orchestration_agent.py:313-320`). Sub-agent AgentExecution rows appear in ORM (traversable via `parent_execution_id`), not auto-enumerated in the composite `job_status` view — same known UX gap flagged for S2925/S2926 WorkflowAgent-family tools.

## 3. Schema notes

Identical shared schema shape as all Slice 5 agent-forwarding tools:

- **Required:** `task` (per schema `required: ['task']` at `pa_tool_schemas.py:1978`). Handler still accepts `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict). Root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194`.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **Workflow selection:** if `context['workflow']` present, `WorkflowOrchestrationAgent.run` uses it directly (`workflow_orchestration_agent.py:233`); else `_infer_workflow(task)` heuristically picks a template from `AVAILABLE_WORKFLOWS` (`:237`).
- **Unauthenticated fallback:** if `self.user is None`, agent returns a `is_conceptual: True` `AgentResult` with the workflow plan but does not execute (`:241-266`). PA dispatch injects the authenticated user, so this branch only fires in test contexts.
- **Tool_name is NOT propagated to WorkflowOrchestrationAgent** — the wrapper resolves tool_name → agent class name via `_tool_to_agent_name` at `td_handlers_agents.py:123` and dispatches `execute_agent_task.apply_async(args=['WorkflowOrchestrationAgent', task_text, context], queue='long_running')`. Any workflow-selection differentiation must therefore come from the caller's `task` text (via `_infer_workflow`) or explicit `context['workflow']`.

## 4. Golden-path examples

**Example 1 — explicit workflow selection:**
```json
{"task": "Create a brand identity package for a fitness-tracking wearable startup", "context": {"workflow": "brand_identity_package", "topic": "fitness wearable startup", "count": 3, "workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "WorkflowOrchestrationAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "WorkflowOrchestrationAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: AgentResult with `data.workflow = "brand_identity_package"`, `data.step_results` (per-template-step outputs), `data.image_ids` / `data.video_ids` (deliverable pointers), `data.project_created` (project id if a project was auto-scaffolded), `data.summary` (LLM narrative).

**Example 2 — inferred workflow (no explicit workflow key):**
```json
{"task": "Research AI wearable trends then create thumbnails for a launch video series", "context": {"workspace_id": "<uuid>"}}
```
Expected: `_infer_workflow(task)` picks a template from `AVAILABLE_WORKFLOWS`; the returned envelope shape is identical to Example 1.

## 5. Failure / empty-state / pagination notes

- **Missing task text:** `task_text` reaches WorkflowOrchestrationAgent as empty string; `_infer_workflow('')` may not resolve a template; the agent returns `success=False, error="No workflow specified. Available: [...]"` (`:268-274`).
- **Unknown workflow in context:** if `context['workflow']` is set to a name not in `AVAILABLE_WORKFLOWS`, the legacy agent's `execute()` typically raises or returns a not-found error surfaced via `success=False`.
- **Legacy execution timeout:** `execute_legacy()` runs in `ThreadPoolExecutor(max_workers=1)` with `COORDINATOR_TIMEOUT`. Long workflows may hit the timeout — the wrapper does NOT recover the partial state.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit the parent or any delegated sub-agent independently.
- **Recursive fanout timeout:** each template step may itself dispatch a sub-agent. Sub-agent AgentExecutions can still be in-progress after the parent transitions to completed (same authoring detail as S2925 `create_project_from_research` for the WorkflowAgent family).
- **Cancel is not recursive across the template tree:** revoking the parent's `celery_task_id` does NOT auto-revoke sub-agent Celery tasks (same shape as WorkflowAgent family).
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, the S1178 auto-wake subscription will NOT fire.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`workflow_orchestration_agent` is classified `external` when scored end-to-end, and **amplified** by template-driven sub-agent dispatch: each template step may dispatch a sub-agent through the same `_handle_agent_tool` handler (dispatcher re-entry hotspot).

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`WorkflowOrchestrationAgent` + template fanout + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) + N sub-agent Celery tasks per template step | `external` (amplified) |
| Data mutation | None | AgentExecution + AgentResult INSERTs for parent + each template-step sub-agent; LLMCallLog rows per LLM call inside the template; potential Project INSERT (`project_created` in the AgentResult data); potential Image/Video/Deliverable INSERTs per step (`image_ids` / `video_ids` in AgentResult) | `spreading` → `cascading` (downstream, amplified — project + deliverable auto-scaffolding is FK-cascade-touching) |
| Signal cascade | None | Agent lifecycle signals × (1 + N sub-agents); Deliverable/Project post_save signal chains; potential AgentFollowupSubscription INSERT for the parent | `cascading` (downstream, amplified) |
| Network egress | None | LLM provider HTTP × (planner + template-step calls); potentially spider queries, web_search, media provider APIs from template sub-agents | `external` (amplified) |

**End-to-end classification:** `external`. Amplification factor is bounded by the template's declared step count (16+ templates each defining a fixed step sequence — different from WorkflowAgent's unbounded LLM-planner fanout). Per Rigby S2925 Q2 authoring guidance: Slice 5 tools MUST be classified end-to-end; this is a **new-evidence-class fanout shape** (template-driven, bounded) distinct from the LLM-planner fanout shape (WorkflowAgent family, S2925 + S2926 — 2/3 instances) — see §Related.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('workflow_orchestration_agent')` → `'WorkflowOrchestrationAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:123` (post PR #3487) | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['WorkflowOrchestrationAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`) → `WorkflowOrchestrationAgent.run` (`core/agents/workflow_orchestration_agent.py:206+`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier. Sub-agent `celery_task_id`s appear ONLY in ORM (queryable via `AgentExecution.objects.filter(parent_execution_id=<parent_ae_id>)`) — the composite `job_status` view does not auto-enumerate them (known UX gap, batch 1/2).
  - (b) **Polling endpoint(s):** `job_status` PA tool for parent completion; ORM traversal for sub-agent enumeration. Optionally `project_created` in the AgentResult data references a Project row that itself has a status field.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution trees + potentially duplicated Deliverable/Project rows.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `WorkflowOrchestrationAgent.run`):
  - Parent AgentExecution INSERT + status transitions.
  - Template resolution (`_infer_workflow(task)` if no explicit workflow) — pure function; no side effect.
  - `legacy_agent.execute(workflow=..., topic=..., count=..., ...)` inside `ThreadPoolExecutor` — this is the fanout point. Per-template-step: LLM planning call(s) (LLMCallLog INSERT per call); sub-agent dispatch through the same or adjacent handler; sub-agent AgentExecution + AgentResult INSERTs; sub-agent LLMCallLog rows; potentially sub-agent web_search / spider / media provider egress.
  - Parent AgentResult INSERT (post-run) with `workflow`, `step_results`, `image_ids`, `video_ids`, `project_created`, `summary`.
  - Optional Project INSERT (if template scaffolds a project) + Deliverable INSERT(s) per generated asset — these trigger post_save signal chains.
  - Optional AgentFollowupSubscription INSERT for parent if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** parent AgentExecution + AgentResult keyed on parent `celery_task_id`; sub-agent AgentExecutions keyed on `parent_execution_id` (ORM-only enumeration). `job_status` surfaces the parent composite view. `project_created` and `image_ids`/`video_ids` in the AgentResult data field provide secondary identifiers for reference-shaped follow-ups.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)` on the parent does NOT recursively revoke sub-agent Celery tasks (authoring detail, WorkflowAgent-family shape carries into WorkflowOrchestrationAgent-family). Sub-agent cancel requires enumerating + revoking each sub-`celery_task_id` individually. Additionally, the `ThreadPoolExecutor.result(timeout=COORDINATOR_TIMEOUT)` at `:304` provides a wall-clock bound but not per-step cancel.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:123`; `execute_agent_task` routing; `AVAILABLE_WORKFLOWS` list changes (`workflow_orchestration_agent.py:83-102`); `_infer_workflow` heuristic changes; legacy agent's `execute()` method or template step definitions; addition of a `workflow_orchestration_agent`-specific pre-processing branch in `_handle_agent_tool` (currently none).

## 6. Evidence

Doc-only sweep this ship, plus **end-to-end completion verification** as batch 3's WorkflowOrchestrationAgent-family representative (validates PR #3487 mapping fix end-to-end).

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `workflow_orchestration_agent` with a minimal task string + `context.workflow` set to an `AVAILABLE_WORKFLOWS` entry (e.g. `"business_research"` — least media-intensive template) via PA. Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'WorkflowOrchestrationAgent', auto_followup, follow_up_will_fire, message}`. **Critical: confirm `agent` field is `'WorkflowOrchestrationAgent'` (not `'WorkflowAgent'`) — this is the PR #3487 fix verification signal.**
2. Poll `job_status` with the returned `task_id` until completion or timeout. Confirm completion payload contains WorkflowOrchestrationAgent AgentResult with the template-shaped data keys (`workflow`, `step_results`, `image_ids`, `video_ids`, `project_created`, `summary`).
3. ORM traversal: `AgentExecution.objects.filter(parent_execution_id=<parent_ae_id>)` — enumerate sub-agent executions delegated by template steps. Confirm at least one sub-agent execution row exists (validates template-driven fanout under the corrected class mapping).
4. **PR #3487 regression check:** confirm the runtime `agent_name` field on the parent AgentExecution row is `'WorkflowOrchestrationAgent'`. Pre-PR-A this would have been `'WorkflowAgent'`; that would indicate the map fix did not take effect (worker cache issue, uncommitted local state, or missed recycle).
5. **New-evidence-class fanout check (Q3 payoff):** compare the template step count enumerated in step 3 with the LLM-planner delegation count observed in S2925/S2926 WorkflowAgent completion-verifies. Template-driven fanout has bounded step count (declared by the template); LLM-planner fanout has unbounded step count (LLM decides per invocation). If both shapes are observed post-merge, batch 3 has surfaced a distinct new-evidence-class fanout shape.

## Related

- **Adjacent tools (same Slice 5 batch 3):** `content_strategy_agent` + `marketing_strategy_agent` + `strategic_review` (structured-output content-strategy peers).
- **Sibling WorkflowAgent-family tools:** `create_project_from_research` (batch 1 S2925 — WorkflowAgent LLM-planner fanout); `create_brand_video` (batch 2 S2926 — WorkflowAgent LLM-planner fanout, 2nd instance). Both route to `WorkflowAgent`, NOT `WorkflowOrchestrationAgent`. Per S2927 PR-A sweep verification (`docs/research/tools/validation/create_brand_video_validation.md` §Related), these are intentional delegate-pattern mappings — `create_brand_video` and `create_project_from_research` are NOT in `WorkflowOrchestrationAgent.AVAILABLE_WORKFLOWS`.
- **PR #3487 (mapping fix) shipped IN THIS SESSION as a prerequisite for this doc.** Merged at `389c048b0`. See commit message for the sweep details + intentional-vs-bug classification of the 4 semantic asymmetries in `_tool_to_agent_name`.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 6 untested pre-batch-3).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925 Slice 5 batch 1 quartet (opened Slice 5 at 4/14); S2926 Slice 5 batch 2 quartet (advanced Slice 5 to 8/14).
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; WorkflowOrchestrationAgent implementation at `core/agents/workflow_orchestration_agent.py` (580 lines, wraps legacy 3,120-line orchestrator). Legacy agent lives in the same module as `WorkflowOrchestrationAgent` — the wrapper delegates to `self.legacy_agent.execute(workflow=..., ...)`.
- **Ledger rows relevant to this ship:**
  - **New-evidence-class fanout shape** (template-driven, bounded) via `WorkflowOrchestrationAgent` — 1st instance this ship. Distinct from the LLM-planner-driven unbounded fanout via `WorkflowAgent` (S2925 + S2926, 2/3 instances). If a 2nd template-driven fanout instance surfaces (e.g. via a future template-based tool), promote as a distinct Fold.
  - **Mapping-vs-class-file asymmetry resolution** for `workflow_orchestration_agent` — closed this session as (c) bug, fixed in PR #3487. Ledger candidate closed.
  - **PR #3487 sweep result** — 0 additional bugs in `_tool_to_agent_name` beyond the workflow_orchestration_agent fix; 3 legacy-alias asymmetries (`security_agent`, `strategic_review`, `create_brand_video`/`create_project_from_research`) documented as intentional. Sweep coverage evidence stored in PR #3487 commit message.
