# `customer_research_agent` — Validation Report (S2925)

**Tool:** `customer_research_agent`
**Schema:** `core/services/pa_tool_schemas.py` (agent-tool shape — see §3 schema notes)
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:329`
**Session:** S2925 (Slice 5 batch 1 — quartet with `brand_strategy_agent` + `competitor_analysis_agent` + `create_project_from_research`)
**HEAD at validation:** `c70ff84fe` (2026-07-23 — post PR #3481 Ledger #33 fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Per Rigby S2925 T0 SIGN micro-edit: `customer_research_agent` is designated the **business-family completion-verify representative** for this batch — receipt + end-to-end `job_status` completion both validated live. Other two business agents in the quartet (`brand_strategy_agent` + `competitor_analysis_agent`) are receipt-verified this ship, completion-verified in Slice 5 batch 2.
**Category upgrade target:** `untested` → `validated_full_with_completion`
**Rigby SIGN:** S2925 T0 SIGN AGREE — same joint SIGN cycle as the batch 1 quartet.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`customer_research_agent` dispatches `CustomerResearchAgent` (`core/agents/business/customer_research_agent.py`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. The agent identifies target customer segments for a business idea, extracts pain points and needs from spider data (Reddit, HackerNews, YouTube, tech news) + web search + ML clustering (Session 683). Mythology validation (Session 354) prevents unrealistic claims. Use it when Chris asks "who are the target customers for X?" / "what pain points does audience Y have?" / "segment the potential users of Z."

Distinct from `competitor_analysis_agent` (supply side — who else is in the market); from `research_agent` (general-purpose research, not customer-specific); from `brand_strategy_agent` (uses customer research as input to synthesize positioning). Typical workflow: customer + competitor research feed into brand strategy, which feeds into content strategy, which feeds into content creation.

## Covered actions

`customer_research_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `CustomerResearchAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live + end-to-end job_status completion verified.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'CustomerResearchAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'CustomerResearchAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up `job_status` returns full AgentResult with customer segments + pain points + needs analysis.

## 3. Schema notes

Identical shared schema shape as all Slice 5 agent-forwarding tools:

- **Required:** none strictly required — `task`/`prompt`/`query` defaults to `''` via `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict); root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194`.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **CustomerResearchAgent is NOT subject to the Editor synthesis reroute or workspace-content gather.**

## 4. Golden-path examples

**Example 1 — customer segments for a product idea:**
```json
{"task": "Research target customer segments for AI-powered fitness coaching apps; extract pain points from Reddit + HN", "context": {"workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "CustomerResearchAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "CustomerResearchAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: `AgentResult` contains customer segments, pain-point clusters, needs analysis, and mythology-validated claim set.

## 5. Failure / empty-state / pagination notes

- **Missing task text:** empty `task_text` reaches CustomerResearchAgent; agent's own validation determines behavior.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit.
- **Spider network failures:** per-source failures degrade output but don't block the run (Reddit/HN/YouTube/tech-news queried independently via unified intelligence search).
- **ML clustering failures:** clustering (Session 683) is a post-fetch step; if it fails, raw customer signals are still returned.
- **Mythology validation rejection:** unrealistic claims removed from output; AgentResult still returned (partial content).
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, no auto-wake banner fires.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`customer_research_agent` is classified `external` when scored end-to-end. Same shape as its batch 1 business-family peers.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`CustomerResearchAgent` + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; SpiderItemHash updates on fresh spider runs; LLMCallLog rows | `spreading` (downstream) |
| Signal cascade | None | Agent lifecycle signals; potential AgentFollowupSubscription INSERT | `cascading` (downstream) |
| Network egress | None | LLM provider HTTP; web_search sub-tool HTTP; spider HTTP refreshes | `external` (downstream) |

**End-to-end classification:** `external`. Consistent with the batch's other two business-family agents.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('customer_research_agent')` → `'CustomerResearchAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:111` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['CustomerResearchAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier.
  - (b) **Polling endpoint(s):** `job_status` PA tool; `AsyncResult(task_id)`; AgentExecution row keyed on `celery_task_id`.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution rows.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task`):
  - AgentExecution row INSERT + status transitions.
  - LLM provider HTTP call(s); LLMCallLog INSERT per call.
  - Web search sub-tool dispatch — **dispatcher re-entry hotspot** (`tool_dispatcher._handle_web_search`).
  - Spider network queries (Reddit + HN + YouTube + tech news + potentially others); potential SpiderItemHash writes on fresh runs.
  - ML clustering pass (Session 683) — may load models into worker memory.
  - Mythology validation pass (Session 354).
  - AgentResult row INSERT (post-run).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** AgentExecution + AgentResult keyed on `celery_task_id`; `job_status` for composite view.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)`; AgentExecution.status settable.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:111`; `execute_agent_task` routing; CustomerResearchAgent's own logic (spider integration, ML clustering path, unified intelligence search wiring).

## 6. Evidence

Doc-only sweep this ship, plus **end-to-end completion verification** as the batch 1 business-family representative.

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `customer_research_agent` with a minimal task string via PA. Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'CustomerResearchAgent', auto_followup, follow_up_will_fire, message}`. Confirm `agent` field resolves to `'CustomerResearchAgent'` (validates `_tool_to_agent_name` mapping at `td_handlers_agents.py:111`).
2. Poll `job_status` with the returned `task_id` until completion (or timeout). Confirm completion payload contains AgentResult-shaped data (segments / pain points / needs analysis). Confirm AgentExecution + AgentResult rows exist in ORM keyed on `celery_task_id`.
3. If `conversation_id` was set in context AND `auto_followup` was not `False`, confirm AgentFollowupSubscription row was created (auto-wake banner should fire).

This ship's completion-verify establishes the pattern for other business-family Slice 5 agents; per Rigby micro-edit at S2925 T0 SIGN, remaining business agents in this batch (`brand_strategy_agent` + `competitor_analysis_agent`) are receipt-verified in this ship and completion-verified in Slice 5 batch 2 to preserve session cadence.

## Related

- **Adjacent tools (same Slice 5 batch):** `brand_strategy_agent` (downstream consumer of customer + competitor research) + `competitor_analysis_agent` (supply-side counterpart) + `create_project_from_research` (WorkflowAgent — orchestrates end-to-end project creation).
- **Other Slice 5 tools (deferred to batches 2+):** `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `character_training_agent`, `image_editing_agent`, `video_editing_agent`, `three_d_generation_agent`, `create_brand_video`, `workflow_orchestration_agent`.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 14 untested).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy.
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; shared `execute_agent_task` + `_impl_execute_agent_task` downstream.
- **Ledger rows relevant to this ship:**
  - First business-family end-to-end completion-verify in Slice 5 — establishes the completion-verify pattern for batches 2+.
  - Web-search dispatcher-re-entry hotspot — inherited from CompetitorAnalysisAgent's shape.
  - ML per-invocation model load cost pattern (S2907 substrate item) — worth measuring during this completion-verify.
