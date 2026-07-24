# `competitor_analysis_agent` — Validation Report (S2925)

**Tool:** `competitor_analysis_agent`
**Schema:** `core/services/pa_tool_schemas.py` (agent-tool shape — see §3 schema notes)
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:328`
**Session:** S2925 (Slice 5 batch 1 — quartet with `brand_strategy_agent` + `customer_research_agent` + `create_project_from_research`)
**HEAD at validation:** `c70ff84fe` (2026-07-23 — post PR #3481 Ledger #33 fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Per Rigby S2925 T0 SIGN micro-edit: `competitor_analysis_agent` is receipt-verified in-scope; end-to-end job_status completion validated for `customer_research_agent` (business-family representative) + `create_project_from_research` (WorkflowAgent-family representative). This tool is receipt-verified in this batch; completion-verify batched with a second business-family tool in Slice 5 batch 2.
**Category upgrade target:** `untested` → `validated_full` (receipt-shape verified) — `validated_full_with_completion` deferred to batch 2
**Rigby SIGN:** S2925 T0 SIGN AGREE — same joint SIGN cycle as `brand_strategy_agent` (Slice 5 batch 1 quartet ratified as unit).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`competitor_analysis_agent` dispatches `CompetitorAnalysisAgent` (`core/agents/business/competitor_analysis_agent.py`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. The agent identifies key competitors in a given market/industry using web search + spider data (unified intelligence per Session 303) + ML entity analysis (GNN+Text per Session 683), producing feature/pricing/positioning breakdowns + SWOT analysis. Mythology validation (Session 354) prevents unrealistic claims in output. Use it when Chris asks "who are the competitors for X?" / "SWOT the market for Y" / "compare product Z to its rivals."

Distinct from `customer_research_agent` (customer segments + pain points — the demand side); from `market_intelligence_coordinator` (macro market movements, not per-competitor); from `brand_strategy_agent` (uses competitor analysis as input to synthesize brand positioning). Typical workflow: competitor + customer research feed into brand strategy.

## Covered actions

`competitor_analysis_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `CompetitorAnalysisAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live; completion-verify deferred to batch 2.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'CompetitorAnalysisAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'CompetitorAnalysisAgent dispatched (task <uuid>). Use job_status to check progress.'}`.

## 3. Schema notes

Identical shared schema shape as all Slice 5 agent-forwarding tools:

- **Required:** none strictly required by handler — `task`/`prompt`/`query` (string) defaults to `''` via `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict); root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194` (`workspace_id`, `workspace`, `conversation_id`, `content_type`, `tone`, `target_audience`, `word_count`, `topic`, `keywords`, `blog_id`, `focus_areas`, `content`, `research`, `research_summary`, `auto_followup`).
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` is present.
- **CompetitorAnalysisAgent is NOT subject to the Editor synthesis reroute or the workspace-content gather** (those apply to EditorAgent + ContentWriterAgent only at `:1267-1317`).

## 4. Golden-path examples

**Example 1 — competitor scan for a market:**
```json
{"task": "Analyze competitors for AI-powered fitness coaching apps", "context": {"workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "CompetitorAnalysisAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "CompetitorAnalysisAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: agent returns `AgentResult` containing identified competitors, feature/pricing matrices, positioning notes, SWOT analysis, and mythology-validated claim set.

## 5. Failure / empty-state / pagination notes

Dispatch-time failures are minimal because the handler is a thin async wrapper. Substantive failure modes surface at `_impl_execute_agent_task` (`core/tasks_agents.py:2077+`), not at the tool call.

- **Missing task text:** empty `task_text` reaches CompetitorAnalysisAgent; agent's own validation determines behavior (typically low-quality or fail-loud output).
- **Blocked agent:** ops-blocked list gate short-circuits execution — status surfaced via `job_status`.
- **Focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit; visible via `job_status`.
- **Web search / spider data failures:** CompetitorAnalysisAgent uses unified intelligence search; per-source failures degrade the output but don't block the run.
- **Mythology validation rejection (Session 354):** if the agent's output contains unrealistic claims, mythology validation removes them; the AgentResult is still returned (partial content).
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, no auto-wake banner fires — per S2728 F-RA-1.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`competitor_analysis_agent` is classified `external` when scored end-to-end. Wrapper first-hop is `apply_async` (out-of-process); downstream CompetitorAnalysisAgent performs LLM calls, spider-network queries, web_search sub-tool dispatch (potential dispatcher re-entry), and ML entity analysis.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`CompetitorAnalysisAgent` + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; potential SpiderItemHash updates on fresh spider runs; LLMCallLog rows | `spreading` (downstream) |
| Signal cascade | None | Agent lifecycle signals; potential AgentFollowupSubscription INSERT | `cascading` (downstream) |
| Network egress | None | LLM provider HTTP; potential web_search sub-tool HTTP; spider HTTP refreshes | `external` (downstream) |

**End-to-end classification:** `external`. Same tier as `brand_strategy_agent` in this batch — driven by the shared `apply_async` + downstream LLM + web_search pattern.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('competitor_analysis_agent')` → `'CompetitorAnalysisAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:110` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['CompetitorAnalysisAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`). Handler sees only `celery_task.id`.
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier.
  - (b) **Polling endpoint(s):** `job_status` PA tool; also `AsyncResult(task_id)` and AgentExecution row keyed on `celery_task_id`.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution rows.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task`):
  - AgentExecution row INSERT + status transitions.
  - LLM provider HTTP call(s); LLMCallLog INSERT per call.
  - Web search sub-tool dispatch — **dispatcher re-entry hotspot** (calls back into `tool_dispatcher._handle_web_search`).
  - Potential spider refresh (unified intelligence search).
  - ML entity analysis (GNN+Text per Session 683) — may load models into worker memory.
  - Mythology validation pass (Session 354).
  - AgentResult row INSERT (post-run).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** AgentExecution + AgentResult (keyed on `celery_task_id`); `job_status` surfaces the composite view.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)`; also settable via AgentExecution.status.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` mapping row at `td_handlers_agents.py:110`; `execute_agent_task` routing; CompetitorAnalysisAgent's own logic (especially the spider-network / web_search integration + ML integration path).

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification (receipt-shape only): dispatch `competitor_analysis_agent` with a minimal task string, confirm envelope shape matches the shared `{task_id, mode: 'async', agent: 'CompetitorAnalysisAgent', auto_followup, follow_up_will_fire, message}` shape, confirm `agent` field resolves to `'CompetitorAnalysisAgent'`.

End-to-end completion verification deferred to Slice 5 batch 2 (bundled with a second business-family tool per Rigby micro-edit).

## Related

- **Adjacent tools (same Slice 5 batch):** `brand_strategy_agent` (downstream consumer of competitor analysis) + `customer_research_agent` (demand-side counterpart) + `create_project_from_research` (WorkflowAgent — orchestrates end-to-end project creation).
- **Other Slice 5 tools (deferred to batches 2+):** `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `character_training_agent`, `image_editing_agent`, `video_editing_agent`, `three_d_generation_agent`, `create_brand_video`, `workflow_orchestration_agent`.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 14 untested).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE (22/22); S2924 Slice 4 CLOSE (17/17); S2921 §5a 4-tier taxonomy.
- **Shared infrastructure notes:** `_handle_agent_tool` at `tool_dispatcher.py:1196` shared across all 14 Slice 5 tools — single point of failure per Rigby S2925 Q5(i). `_tool_to_agent_name` at `td_handlers_agents.py:83-160` — mapping drift risk affects all Slice 5 dispatches.
- **Ledger rows relevant to this ship:**
  - Web-search dispatcher-re-entry hotspot from CompetitorAnalysisAgent — not new to this ship (existed pre-S2924) but documented as an audit surface for Slice 5.
  - ML per-invocation model load (S2907 harness-substrate item) — CompetitorAnalysisAgent's GNN+Text integration is a potential hit for this cost pattern; worth measuring during completion-verify in batch 2.
