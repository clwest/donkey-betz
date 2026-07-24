# `content_strategy_agent` — Validation Report (S2927)

**Tool:** `content_strategy_agent`
**Schema:** `core/services/pa_tool_schemas.py:1854`
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:331`
**Session:** S2927 (Slice 5 batch 3 — quartet with `workflow_orchestration_agent` + `marketing_strategy_agent` + `strategic_review`)
**HEAD at validation:** `389c048b0` (2026-07-24 — post PR #3487 mapping fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Receipt-verify only (batch 3 completion-verify representative is `workflow_orchestration_agent`).
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2927 T0 SIGN Q1 quartet — content-strategy tier tool #1.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`content_strategy_agent` dispatches `ContentStrategyAgent` (`core/agents/strategy/content_strategy_agent.py:44+`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. `ContentStrategyAgent` is a strategy-only recommender: it analyzes spider intelligence + trending topics and recommends what content the user should create next (editorial calendar, content pillars, distribution plan, SEO strategy, content audit). It does NOT generate content itself (that's `ContentWriterAgent`); it does NOT generate images/video/audio (those are the media agents).

Distinct from `content_writer_agent` (creates the actual content); from `marketing_strategy_agent` (broader campaign/GTM/growth planning, not content-specific); from `strategic_review` (SWOT / business-model evaluation via the SAME class — see §Related for the alias relationship).

## Covered actions

`content_strategy_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `ContentStrategyAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'ContentStrategyAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'ContentStrategyAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up `job_status` returns AgentResult with content-strategy recommendations (content types, timing, style, opportunity summary).

## 3. Schema notes

Identical shared schema shape as all Slice 5 agent-forwarding tools:

- **Required:** `task` (per schema `required: ['task']` at `pa_tool_schemas.py:1873`). Handler still accepts `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict). Root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194`. Documented context fields: audience, topics, channels, goals, `niche` (used by ContentStrategyAgent).
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **Import note:** AGENT_MAP registers `ContentStrategyAgent` from `core/agents/strategy/` (`agent_router.py:105-106` + `:345`). A second `ContentStrategyAgent` class exists at `core/agents/business/content_strategy_agent.py` — NOT imported by AGENT_MAP. Any future refactor that consolidates or reroutes must confirm the AGENT_MAP source-of-truth.

## 4. Golden-path examples

**Example — content strategy for a niche:**
```json
{"task": "What content should I create for a fitness-tracking wearable audience over the next 3 months?", "context": {"niche": "fitness_wearables", "channels": ["youtube", "instagram"], "workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "ContentStrategyAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "ContentStrategyAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: AgentResult contains content-strategy narrative + recommended content types (from ContentStrategyAgent's system_prompt: Logo Design, YouTube Thumbnails, Social Media Posts, Brand Identity Packages, Product Photography, Illustrations).

## 5. Failure / empty-state / pagination notes

- **Missing task text:** `task_text` reaches ContentStrategyAgent as empty string; the LLM planner may attempt a generic recommendation or fail-loud in its own validation.
- **Empty spider context:** ContentStrategyAgent relies on spider intelligence data. If no spider data is available for the requested niche, the agent may return generic recommendations rather than data-grounded ones. Not distinguishable from a rich response at the envelope layer.
- **Content-shape FAIL risk:** S2926 documented CompetitorAnalysisAgent (a `BaseBusinessResearchAgent` subclass) returning `status='completed'` with a generic "concept too vague" note under thin dispatches. ContentStrategyAgent inherits from `BaseAgent` (not `BaseBusinessResearchAgent`), so this specific failure shape does not directly carry over — but structured-output agents in general remain a Fold-candidate risk class. See §Related.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, the S1178 auto-wake subscription will NOT fire.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`content_strategy_agent` is classified `external` when scored end-to-end — strategy-only agent but still incurs LLM egress + potential spider intelligence egress + potentially AgentExecution + AgentResult INSERTs.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`ContentStrategyAgent` + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; LLMCallLog rows | `spreading` (downstream) |
| Signal cascade | None | Agent lifecycle signals; potential AgentFollowupSubscription INSERT | `cascading` (downstream) |
| Network egress | None | LLM provider HTTP; potentially spider queries + trending-data fetches | `external` |

**End-to-end classification:** `external`. Non-amplified — ContentStrategyAgent does NOT delegate to sub-agents (has no `execute_tool` branch for `delegate_to_agent` unlike WorkflowAgent). Bounded to LLM call + spider queries per invocation.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('content_strategy_agent')` → `'ContentStrategyAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:113` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['ContentStrategyAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`) → `ContentStrategyAgent.run`.
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier — ContentStrategyAgent does NOT auto-scaffold Deliverable/Project rows (unlike MarketingStrategyAgent — see `marketing_strategy_agent_validation.md`).
  - (b) **Polling endpoint(s):** `job_status` PA tool.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution rows.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `ContentStrategyAgent.run`):
  - AgentExecution INSERT + status transitions.
  - ContentStrategyAgent LLM planning call(s); LLMCallLog INSERT per call.
  - Optional spider queries via context integration.
  - AgentResult INSERT (post-run).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** AgentExecution + AgentResult keyed on `celery_task_id`; `job_status` PA tool.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)` on the task. No sub-agent recursion concern.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:113`; ContentStrategyAgent's `system_prompt` / tool inventory / spider-data integration path; if `ContentStrategyAgent` at `core/agents/strategy/` is replaced by the sibling class at `core/agents/business/content_strategy_agent.py`.

## 6. Evidence

Doc-only sweep this ship; receipt-verify only.

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `content_strategy_agent` with a minimal task string via PA (e.g. `"What content should I create for a tech audience this quarter?"`). Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'ContentStrategyAgent', auto_followup, follow_up_will_fire, message}`.
2. Confirm ORM row created: `AgentExecution.objects.filter(celery_task_id='<task_id>').exists()` returns True. Receipt-verify complete at this point.
3. (Deferred / follow-up) Completion-verify: poll `job_status` until `status='completed'`; inspect AgentResult content for structured-output shape (content-type recommendations, timing, style narrative). If AgentResult reports success but content is generic "concept too vague" or missing recommendation structure, that is the 2nd instance of the content-shape FAIL pattern (1st = CompetitorAnalysisAgent, S2926 deliverable `5703a6c8-...`) and triggers Fold promotion per S2926 forbidden entry.

## Related

- **Adjacent tools (same Slice 5 batch 3):** `workflow_orchestration_agent` + `marketing_strategy_agent` + `strategic_review`.
- **Alias tool (same class):** `strategic_review` also routes to `ContentStrategyAgent` per `td_handlers_agents.py:131` (Session 1068 comment: "StrategyAgent doesn't exist"). Distinct tool_name + description at the schema layer, single class at the runtime layer. See `strategic_review_validation.md` §Related for the alias-shape discussion.
- **Sibling class file NOT registered:** `core/agents/business/content_strategy_agent.py` exists but is not imported by AGENT_MAP. Historically unclear whether it's dead code or reserved for a future refactor. Any future consolidation MUST re-verify AGENT_MAP source-of-truth alignment.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md`.
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925/S2926 Slice 5 batches 1+2.
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; ContentStrategyAgent implementation at `core/agents/strategy/content_strategy_agent.py`.
- **Ledger rows relevant to this ship:**
  - **Content-shape FAIL watch:** 2nd-instance trigger deferred to completion-verify follow-up. Per S2926 forbidden entry, 2nd instance promotes the diagnostic pattern to Fold. This tool + `marketing_strategy_agent` + `strategic_review` are all structured-output candidates.
  - **Multi-tool-single-class asymmetry** (`content_strategy_agent` + `strategic_review` → same `ContentStrategyAgent`): 1st documented instance at S2927 batch 3; if a 2nd instance surfaces in future sweep batches (e.g. `security_agent` + `memory_isolation_agent` both → `MemoryIsolationAgent`), promote as an authoring pattern for alias-handling in validation docs.
