# `brand_strategy_agent` — Validation Report (S2925)

**Tool:** `brand_strategy_agent`
**Schema:** `core/services/pa_tool_schemas.py` (agent-tool shape — see §3 schema notes)
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:331`
**Session:** S2925 (Slice 5 batch 1 — first `tool_dispatcher.py` batch; quartet with `competitor_analysis_agent` + `customer_research_agent` + `create_project_from_research`)
**HEAD at validation:** `c70ff84fe` (2026-07-23 — post PR #3481 Ledger #33 fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Per Rigby micro-edit at S2925 T0 SIGN: this tool is receipt-verified in-scope; end-to-end job_status completion validated for `customer_research_agent` (business-family representative) + `create_project_from_research` (WorkflowAgent-family representative). `brand_strategy_agent` receipt-verified in this batch; completion-verify batched with a business-family tool in Slice 5 batch 2.
**Category upgrade target:** `untested` → `validated_full` (receipt-shape verified) — `validated_full_with_completion` deferred to batch 2
**Rigby SIGN:** S2925 T0 SIGN AGREE with 2 micro-edits — Slice 5 shape confirmed (all 14 tools dispatch through single `_handle_agent_tool`); 10 `repo_tool` receipts covering `_handle_agent_tool`, `_tool_to_agent_name`, `execute_agent_task`, `_impl_execute_agent_task`, BrandStrategyAgent class. Q2 verdict: §5a classification target = wrapper pre-processing + mapped agent behavior (end-to-end, NOT wrapper-only).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`brand_strategy_agent` dispatches `BrandStrategyAgent` (`core/agents/business/brand_strategy_agent.py:70`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. The agent synthesizes existing project research (competitor + customer insights) into a comprehensive brand strategy report covering brand positioning, target audience alignment, and actionable recommendations. Use it when Chris asks "what's our brand strategy for X?" / "given the competitor + customer research, position the brand" / "draft a brand strategy report."

Distinct from `brand_identity_agent` (visual identity — logos, colors — a different agent class); from `create_brand_video` (WorkflowAgent orchestrating video creation, not strategy analysis); from `content_strategy_agent` (content plan, downstream of brand strategy); from `marketing_strategy_agent` (go-to-market plan, also downstream). This tool is the strategic-foundation step in a brand workflow.

## Covered actions

`brand_strategy_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `BrandStrategyAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values (unlike Slice 4 multi-action gateway tools).

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live; completion-verify deferred to batch 2.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'BrandStrategyAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'BrandStrategyAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up completion via `job_status` tool with the returned `task_id`.

## 3. Schema notes

- **Required:** none strictly required by handler — `task`/`prompt`/`query` (string; agent's task text) defaults to empty string via `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict; agent execution context — must be dict-typed else replaced with `{}` at `:1226-1227`); `workspace_id` / `workspace` / `conversation_id` / `content_type` / `tone` / `target_audience` / `word_count` / `topic` / `keywords` / `blog_id` / `focus_areas` / `content` / `research` / `research_summary` / `auto_followup` — all root-level keys promoted into `context` at `:1230-1232` per `_CONTEXT_PROMOTE_KEYS` set.
- **User scoping:** if `user_id` is present, `context['user_id'] = str(user_id)` is injected at `:1234-1235`. Otherwise no user context is attached.
- **BrandStrategyAgent is NOT subject to the Editor synthesis reroute or workspace-content gather** (those apply to EditorAgent + ContentWriterAgent only at `:1267-1317`). BrandStrategyAgent's own logic is responsible for pulling any project research it needs.

## 4. Golden-path examples

**Example 1 — brand strategy from existing project research:**
```json
{"task": "Draft brand strategy for the new fitness-tracking wearable", "context": {"workspace_id": "<uuid>"}}
```
Expected envelope (immediate dispatch receipt): `{"task_id": "<celery-uuid>", "mode": "async", "agent": "BrandStrategyAgent", "auto_followup": true, "follow_up_will_fire": <bool depending on conversation_id in context>, "message": "BrandStrategyAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion: call `job_status` tool with the returned `task_id` — completion returns the agent's `AgentResult` including brand positioning, audience alignment, and recommendations sections.

## 5. Failure / empty-state / pagination notes

Because dispatch is asynchronous, most failure modes surface at the downstream `_impl_execute_agent_task` (`core/tasks_agents.py:2077+`), not at the tool call itself. The tool call returns success (receipt) even when the agent will subsequently fail.

- **Missing task text:** `task_text` is empty string. Agent receives empty task and either fails-loud in its own validation or produces a low-quality output. Not surfaced at dispatch time.
- **Blocked agent:** if `BrandStrategyAgent` is on the ops-blocked list (see `_impl_execute_agent_task` blocked-agent gate), the Celery task returns early with a blocked-status message. Surfaces via `job_status`, not the dispatch envelope.
- **Focus mode / demo mode:** downstream gates can also short-circuit execution — see `_impl_execute_agent_task` for the full precedence.
- **Circuit breaker open:** agent-level circuit breaker (per BaseAgent) may block execution.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup` was explicitly `False`, the S1178 auto-wake `AgentFollowupSubscription` will NOT fire — no completion banner will appear in Rigby's chat. Documented per S2728 F-RA-1 dispatch surfacing.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy amended S2921; Slice 5 classification per Rigby S2925 Q2 = end-to-end wrapper + mapped agent behavior)

`brand_strategy_agent` is classified `external` when scored end-to-end: the wrapper's first-hop is `execute_agent_task.apply_async(..., queue='long_running')` — a Celery fan-out that leaves the process. Downstream, `BrandStrategyAgent.run` performs LLM calls (OpenAI/Anthropic per LLMProviderRegistry), may query workspace deliverables (ORM READ), and writes AgentExecution + AgentResult rows (ORM WRITE) on completion. Full downstream side-effect enumeration in §5b Appendix A below.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`BrandStrategyAgent` + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running` queue) | `external` |
| Data mutation | None (pass-through dispatch) | AgentExecution row INSERT + AgentResult row INSERT on completion | `spreading` (downstream only) |
| Signal cascade | None | Agent lifecycle signals + LLMCallLog INSERT + potential auto_followup subscription | `cascading` (downstream only) |
| Network egress | None | LLM provider HTTP + potentially web_search sub-tool | `external` (downstream) |

**End-to-end classification:** `external`. Wrapper alone would be `contained`; the mapped agent's behavior is what drives the tier up. Per Rigby S2925 Q2 verdict: Slice 5 tools MUST be classified end-to-end because the wrapper is a launchpad into a mutating agent ecosystem.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('brand_strategy_agent')` → `'BrandStrategyAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:112` | Pure name-resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict mutation; no persistence |
| `reroute_synthesis_to_content_writer(agent_name, task_text, context)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; returns unchanged for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Filters context dict; no persistence |
| `execute_agent_task.apply_async(args=['BrandStrategyAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) is a thin Celery shim that delegates to `_impl_execute_agent_task` (`core/tasks_agents.py:2077`). Handler sees only `celery_task.id`; the actual agent class resolution + execution happens Celery-side.
- **A2. Queue name(s) + priority:** `long_running` queue (single value at `tool_dispatcher.py:1330`). Priority: not set. Consumed by the long-running worker per `Procfile`.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier (unlike some Slice 4 hybrid tools).
  - (b) **Polling endpoint(s):** `job_status` PA tool with the returned `task_id`. Also queryable via `AsyncResult(task_id)` from ORM contexts, or via the AgentExecution row keyed on `celery_task_id`.
  - (c) **Idempotency stance:** `none`. Repeat dispatches create independent Celery tasks + AgentExecution rows. No dedup key.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` at `core/tasks_agents.py:2077+`):
  - AgentExecution row INSERT (pre-run) + status transitions.
  - LLM provider HTTP call(s) via BaseAgent (OpenAI/Anthropic/etc.); LLMCallLog INSERT per call.
  - Optional web_search sub-tool dispatch (via BaseAgent tool surface) — potential dispatcher re-entry into `tool_dispatcher._handle_web_search`.
  - AgentResult row INSERT (post-run).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` is set and `auto_followup` is not `False` — auto-wake banner delivery.
  - Blocked-agent gate + circuit breaker + focus-mode + demo-mode gates all fire pre-run at `_impl_execute_agent_task`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** authoritative source is the AgentExecution + AgentResult row pair (keyed on `celery_task_id`). `job_status` surfaces the composite view. `CeleryTaskEvent` rows are best-effort supplementary telemetry.
  - (b) **Cancel semantics:** revoke via `celery.control.revoke(task_id, terminate=False)`; also settable via AgentExecution.status. Explicit revoke API not surfaced through the dispatch envelope.
  - (c) **Revisit triggers:** changes to `_handle_agent_tool`, `_tool_to_agent_name` mapping (especially the `brand_strategy_agent` row at `td_handlers_agents.py:112`), `execute_agent_task` Celery routing, or BrandStrategyAgent's own logic. Also revisit if a new pre-processing branch is added to `_handle_agent_tool` for BrandStrategyAgent specifically (currently only EditorAgent + ContentWriterAgent get special handling at `:1267-1317`).

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification (receipt-shape only per Rigby micro-edit at S2925 T0 SIGN): dispatch `brand_strategy_agent` with a minimal task string, confirm envelope shape matches `{task_id, mode: 'async', agent: 'BrandStrategyAgent', auto_followup, follow_up_will_fire, message}`, confirm the `agent` field resolves to `'BrandStrategyAgent'` (validates the `_tool_to_agent_name` mapping).

End-to-end completion verification deferred to Slice 5 batch 2 (bundled with a second business-family tool per Rigby micro-edit).

## Related

- **Adjacent tools (same Slice 5 batch):** `competitor_analysis_agent` (upstream research feed) + `customer_research_agent` (upstream research feed) + `create_project_from_research` (WorkflowAgent — orchestrates end-to-end project creation from research).
- **Other Slice 5 tools (deferred):** `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `character_training_agent`, `image_editing_agent`, `video_editing_agent`, `three_d_generation_agent`, `create_brand_video`, `workflow_orchestration_agent` (10 remaining after batch 1).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 14 untested).
- **Prior ratifications:** S2892 Path B open (PA tools sweep); S2917 Slice 3 CLOSE (22/22); S2924 Slice 4 CLOSE (17/17); S2921 §5a 4-tier taxonomy.
- **Shared infrastructure notes:** `_handle_agent_tool` at `tool_dispatcher.py:1196` is shared across all 14 Slice 5 tools — a single point of failure per Rigby S2925 Q5(i). Mapping drift risk in `_tool_to_agent_name` (`td_handlers_agents.py:83-160`) affects all Slice 5 dispatches.
- **Ledger rows relevant to this ship:**
  - Slice 5 single-shared-handler pattern (all 14 tools) — first exercise this ship; documented for future Slice-5 authoring.
  - End-to-end §5a classification for agent-forwarding wrappers (Rigby S2925 Q2 authoring guidance) — first exercise this ship.
