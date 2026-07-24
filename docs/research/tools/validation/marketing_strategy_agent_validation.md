# `marketing_strategy_agent` — Validation Report (S2927)

**Tool:** `marketing_strategy_agent`
**Schema:** `core/services/pa_tool_schemas.py:1880`
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:332`
**Session:** S2927 (Slice 5 batch 3 — quartet with `workflow_orchestration_agent` + `content_strategy_agent` + `strategic_review`)
**HEAD at validation:** `389c048b0` (2026-07-24 — post PR #3487 mapping fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Receipt-verify only (batch 3 completion-verify representative is `workflow_orchestration_agent`).
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2927 T0 SIGN Q1 quartet — content-strategy tier tool #2. Also relevant to Q5(A): `MarketingStrategyAgent` inherits `BaseBusinessResearchAgent` (same base class as CompetitorAnalysisAgent — the S2926 content-shape FAIL surface). Doc explicitly flags the shared-base-class risk in §5 + §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`marketing_strategy_agent` dispatches `MarketingStrategyAgent` (`core/agents/business/marketing_strategy_agent.py:60+`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. `MarketingStrategyAgent` inherits from `BaseBusinessResearchAgent` and analyzes existing research + trends to produce comprehensive marketing plans (channel strategies, campaign ideas, budget allocation, go-to-market plans, growth strategies, funnel optimization).

Distinct from `content_strategy_agent` (content planning/editorial focus, not campaign-level); from `brand_strategy_agent` (brand positioning, prerequisite for MarketingStrategyAgent's workflow); from `campaign_orchestrator_agent` (campaign execution + coordination, not planning).

**Key behavioral difference vs peers:** `create_deliverable_on_schedule = True` (`marketing_strategy_agent.py:64`, fixed Session 1077 — was previously False, causing outputs to be lost in AgentExecution). Every successful invocation auto-creates a Deliverable row.

## Covered actions

`marketing_strategy_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `MarketingStrategyAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'MarketingStrategyAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'MarketingStrategyAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up `job_status` returns AgentResult with marketing plan + auto-created Deliverable id.

## 3. Schema notes

Identical shared schema shape as all Slice 5 agent-forwarding tools:

- **Required:** `task` (per schema `required: ['task']` at `pa_tool_schemas.py:1899`). Handler still accepts `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict). Root-level promotable keys per `_CONTEXT_PROMOTE_KEYS`. Documented context fields: product, budget, timeline, target_market.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **Auto-Deliverable:** `create_deliverable_on_schedule = True` on the agent class. On successful `run`, the base agent scheduler creates a Deliverable row with `research_type='marketing_strategy'` (from `marketing_strategy_agent.py:63`). Repeat invocations create additional Deliverable rows — no dedupe.

## 4. Golden-path examples

**Example — go-to-market plan:**
```json
{"task": "Create a go-to-market plan for a fitness-tracking wearable launch in Q1 2027", "context": {"product": "fitness_wearable_v1", "timeline": "Q1_2027", "target_market": "consumer_health_enthusiasts", "workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "MarketingStrategyAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "MarketingStrategyAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: AgentResult with marketing plan sections (channel strategy, campaign ideas, budget allocation, funnel optimization). Auto-created Deliverable row visible via `deliverable_tool.list` with `research_type='marketing_strategy'`.

## 5. Failure / empty-state / pagination notes

- **Missing task text:** `task_text` reaches MarketingStrategyAgent as empty string. Per `BaseBusinessResearchAgent` inheritance, the agent's `run` workflow starts by calling `get_project_research` for context — if no context, the LLM planner may return a generic recommendation.
- **Content-shape FAIL risk — HIGH:** `MarketingStrategyAgent` inherits from `BaseBusinessResearchAgent`, the SAME base class as `CompetitorAnalysisAgent` which surfaced the S2926 content-shape FAIL (returning `status='completed'` with generic "concept too vague" note under thin dispatches — deliverable `5703a6c8-...`). This tool is a **candidate 2nd instance** for content-shape FAIL Fold promotion. Completion-verify against structured-output shape (channel strategy present? budget allocation present? funnel stages present?) is the recommended next step in a follow-up session.
- **Duplicate Deliverable rows:** repeat invocations with similar task strings produce multiple Deliverable rows (no dedupe). Manual cleanup or a future `deliverable_tool.merge` action would be required.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit; a short-circuited invocation does NOT create a Deliverable row.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, the S1178 auto-wake subscription will NOT fire.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`marketing_strategy_agent` is classified `external` when scored end-to-end — LLM egress + potential spider/web_search egress + auto-Deliverable INSERT is a mutation cascade with post_save signal chain.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`MarketingStrategyAgent` + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; LLMCallLog rows; **Deliverable INSERT (auto-scheduled)** | `cascading` (downstream — Deliverable post_save chain) |
| Signal cascade | None | Agent lifecycle signals; **Deliverable post_save receivers** (indexing, notification, workspace-visibility signals); potential AgentFollowupSubscription INSERT | `cascading` (downstream) |
| Network egress | None | LLM provider HTTP; spider queries (per `BaseBusinessResearchAgent` — "77 data sources"); web_search API calls | `external` (amplified) |

**End-to-end classification:** `external`. The auto-Deliverable INSERT + spider/web_search integration lifts this above pure ContentStrategyAgent-tier — MarketingStrategyAgent has a richer downstream surface (spider fetch + web_search + Deliverable auto-create). Not amplified via sub-agent delegation (unlike WorkflowAgent-family).

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('marketing_strategy_agent')` → `'MarketingStrategyAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:114` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['MarketingStrategyAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`) → `MarketingStrategyAgent.run` (inherited from `BaseBusinessResearchAgent`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). **Secondary domain identifier: Deliverable id** — reachable via `Deliverable.objects.filter(source_agent_execution_id=<parent_ae_id>).values_list('id', flat=True)` after completion.
  - (b) **Polling endpoint(s):** `job_status` PA tool; `deliverable_tool.list` for auto-created Deliverable rows.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution rows + additional Deliverable rows.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `MarketingStrategyAgent.run` inherited from `BaseBusinessResearchAgent`):
  - AgentExecution INSERT + status transitions.
  - `get_project_research` call (reads existing project context — no mutation).
  - Spider queries (reads spider intelligence — no mutation, but egress).
  - `web_search` tool call (network egress).
  - LLM planning call(s); LLMCallLog INSERT per call.
  - AgentResult INSERT (post-run).
  - **Deliverable INSERT (auto-scheduled per `create_deliverable_on_schedule = True`)** — triggers Deliverable post_save receiver chain (indexing, workspace visibility, notification).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** AgentExecution + AgentResult keyed on `celery_task_id`; `job_status` PA tool; Deliverable row queryable by `source_agent_execution_id` — surfaces auto-created marketing-strategy deliverables in Deliverables library.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)` on the task. If revoked mid-run, no Deliverable row is created (creation is post-`run` success). If revoked post-run before Deliverable creation completes, a partial row may exist — inspect via ORM.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:114`; `MarketingStrategyAgent.research_type` change (`marketing_strategy_agent.py:63`); `create_deliverable_on_schedule` flag flip; `BaseBusinessResearchAgent.run` workflow changes (base-class inheritance point); spider integration path changes.

## 6. Evidence

Doc-only sweep this ship; receipt-verify only.

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `marketing_strategy_agent` with a minimal task string via PA (e.g. `"Create a go-to-market plan for a fitness wearable launch"`). Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'MarketingStrategyAgent', auto_followup, follow_up_will_fire, message}`.
2. Confirm ORM row created: `AgentExecution.objects.filter(celery_task_id='<task_id>').exists()` returns True. Receipt-verify complete at this point.
3. (Deferred / follow-up — Rigby Q5(A) 2nd-instance watch) Completion-verify: poll `job_status` until `status='completed'`; inspect AgentResult content for structured marketing-plan shape (channel strategy present? campaign ideas present? budget allocation present?). If AgentResult reports success but content is generic (mirrors CompetitorAnalysisAgent's "concept too vague" note under thin dispatch), that IS the 2nd instance of content-shape FAIL (1st = S2926 CompetitorAnalysisAgent, deliverable `5703a6c8-...`) and triggers Fold promotion per S2926 forbidden entry. Also confirm auto-created Deliverable row: `Deliverable.objects.filter(source_agent_execution_id=<parent_ae_id>, deliverable_type='marketing_strategy').first()`.

## Related

- **Adjacent tools (same Slice 5 batch 3):** `workflow_orchestration_agent` + `content_strategy_agent` + `strategic_review`.
- **Sibling BaseBusinessResearchAgent tools** (share content-shape FAIL risk class): `competitor_analysis_agent` (1st content-shape FAIL instance, S2926); `customer_research_agent` (S2925 batch 1); `brand_strategy_agent` (S2925 batch 1). Batch 3 completion-verify on `marketing_strategy_agent` would provide the natural 2nd-instance datapoint for Fold promotion.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`; `docs/audits/PA_TOOLS_GAP_MAP.md`.
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925/S2926 Slice 5 batches 1+2.
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; MarketingStrategyAgent implementation at `core/agents/business/marketing_strategy_agent.py`; `BaseBusinessResearchAgent` at `core/agents/business/base_business_research_agent.py`.
- **Ledger rows relevant to this ship:**
  - **Content-shape FAIL 2nd-instance candidate:** highest-risk tool in batch 3 for surfacing the pattern. Follow-up completion-verify recommended.
  - **Auto-Deliverable side-effect** (Session 1077 fix pointer) — noted as authoring detail; not a new Ledger candidate.
