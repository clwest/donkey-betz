# `strategic_review` — Validation Report (S2927)

**Tool:** `strategic_review`
**Schema:** `core/services/pa_tool_schemas.py:1985`
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:458`
**Session:** S2927 (Slice 5 batch 3 — quartet with `workflow_orchestration_agent` + `content_strategy_agent` + `marketing_strategy_agent`)
**HEAD at validation:** `389c048b0` (2026-07-24 — post PR #3487 mapping fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Receipt-verify only. **Alias tool** (see §1 + §Related): shares runtime class with `content_strategy_agent`.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2927 T0 SIGN Q1 quartet — content-strategy tier tool #3. Also relevant to PR #3487 sweep: `strategic_review → ContentStrategyAgent` is a **legacy alias** (Session 1068 comment: "StrategyAgent doesn't exist"), documented as intentional (not a bug) in the PR #3487 sweep result.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`strategic_review` dispatches `ContentStrategyAgent` (`core/agents/strategy/content_strategy_agent.py:44+`) asynchronously via Celery `execute_agent_task` on the `long_running` queue — **the SAME runtime class as `content_strategy_agent`**. The mapping `strategic_review → ContentStrategyAgent` at `td_handlers_agents.py:131` is a **legacy alias**: the tool_name preserves a semantic surface ("strategic review, SWOT analysis, business-model evaluation") that the schema description advertises, but no dedicated `StrategyReviewAgent` or `StrategicReviewAgent` class exists in the codebase (Session 1068 code comment: "StrategyAgent doesn't exist").

**Consequence:** at the runtime layer, `strategic_review` and `content_strategy_agent` are semantic aliases — the same class receives the same shared context + task string via the same dispatcher path. The differentiation happens ONLY at the LLM caller side (Rigby's PA planner shapes the `task` string differently based on which tool_name it selected). `ContentStrategyAgent`'s `system_prompt` is content-strategy-focused, not SWOT/strategic-review-focused — so `strategic_review` dispatches produce content-strategy-shaped outputs regardless of the user-facing framing.

Distinct from `content_strategy_agent` (SAME class, different tool_name/description at schema layer); from `content_writer_agent` (creates actual content, not strategy); from `marketing_strategy_agent` (broader marketing-plan focus, different class `MarketingStrategyAgent`).

## Covered actions

`strategic_review` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `ContentStrategyAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'ContentStrategyAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'ContentStrategyAgent dispatched (task <uuid>). Use job_status to check progress.'}`. **Note the envelope `agent` field is `'ContentStrategyAgent'` — NOT `'StrategyReviewAgent'` — reflecting the underlying class routing.**

## 3. Schema notes

Identical shared schema shape as all Slice 5 agent-forwarding tools:

- **Required:** `task` (per schema `required: ['task']` at `pa_tool_schemas.py:2004`). Handler still accepts `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict). Root-level promotable keys per `_CONTEXT_PROMOTE_KEYS`. Documented context fields: company, industry, focus_areas.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **Alias mapping:** `td_handlers_agents.py:131` (`'strategic_review': 'ContentStrategyAgent'`) — comment declares Session 1068 rationale ("StrategyAgent doesn't exist"). Any future addition of a dedicated `StrategyReviewAgent` class would require updating both this mapping AND `agent_router.AGENT_MAP` to register the new class.

## 4. Golden-path examples

**Example — SWOT-style dispatch:**
```json
{"task": "Conduct a SWOT analysis of our fitness-tracking wearable platform, focusing on competitive positioning and Q1 2027 launch readiness", "context": {"company": "Donkey Betz Fitness", "industry": "consumer_wearables", "focus_areas": ["competitive_positioning", "launch_readiness"], "workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "ContentStrategyAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "ContentStrategyAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

**Envelope-layer alias verification:** if the user compares this envelope to a `content_strategy_agent` dispatch envelope side-by-side (same context dict, differently-worded task), the `agent` field is identical (`'ContentStrategyAgent'`) and the dispatch shape is indistinguishable. Only the caller's task-text shaping distinguishes the two invocations.

## 5. Failure / empty-state / pagination notes

- **Semantic-mismatch risk (HIGH):** because `ContentStrategyAgent`'s `system_prompt` is content-strategy-focused (recommending content types, editorial calendars, distribution plans), a SWOT-style task may produce a content-strategy-shaped output rather than a business-strategy-shaped output. **This is not a bug — it's the alias behavior surfacing at the output layer.** Any caller expecting SWOT structure from `strategic_review` will observe drift.
- **Content-shape FAIL risk:** shares the S2926 content-shape FAIL candidate class with peer content-strategy tools (see `content_strategy_agent_validation.md` §5 + `marketing_strategy_agent_validation.md` §5). If completion-verify surfaces a "concept too vague" response under thin dispatches, that counts as a 2nd content-shape FAIL instance for Fold promotion.
- **Missing task text:** identical shape to `content_strategy_agent` — `task_text` reaches ContentStrategyAgent as empty string; LLM may return generic recommendation.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, the S1178 auto-wake subscription will NOT fire.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`strategic_review` shares the exact end-to-end classification as `content_strategy_agent` — same class, same downstream side-effect boundary.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`ContentStrategyAgent` + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; LLMCallLog rows | `spreading` (downstream) |
| Signal cascade | None | Agent lifecycle signals; potential AgentFollowupSubscription INSERT | `cascading` (downstream) |
| Network egress | None | LLM provider HTTP; potentially spider queries | `external` |

**End-to-end classification:** `external`. Non-amplified. **Identical shape to `content_strategy_agent`** — see `content_strategy_agent_validation.md` §5a for the same-class classification rationale.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('strategic_review')` → `'ContentStrategyAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:131` | Name resolution; no side effect. Alias resolution — different tool_name than `content_strategy_agent` but same RHS class. |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['ContentStrategyAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — identical to `content_strategy_agent`. |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

Identical to `content_strategy_agent` — see `content_strategy_agent_validation.md` §5b Appendix A for full A1–A5 fields. The only alias-specific consideration is A5(c) revisit triggers below.

- **A5(c) Revisit triggers (alias-specific):** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:131`; ContentStrategyAgent's `system_prompt` / tool inventory (shared with `content_strategy_agent`); **addition of a dedicated `StrategyReviewAgent` class** — this would decouple the alias and require re-classification of this tool as a distinct-class dispatch.

## 6. Evidence

Doc-only sweep this ship; receipt-verify only.

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `strategic_review` with a minimal SWOT-style task string via PA (e.g. `"Conduct a SWOT analysis of our content platform"`). Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'ContentStrategyAgent', auto_followup, follow_up_will_fire, message}`. **Critical: confirm the `agent` field is `'ContentStrategyAgent'` — this validates the alias mapping.**
2. Confirm ORM row created: `AgentExecution.objects.filter(celery_task_id='<task_id>').exists()` returns True. Receipt-verify complete at this point.
3. **Alias-shape verification (2nd instance of multi-tool-single-class pattern):** compare the AgentExecution.agent_name / AgentResult data shape between this `strategic_review` dispatch and a peer `content_strategy_agent` dispatch (batch 3 receipt-verify #1 above). If shape is indistinguishable, that confirms the alias behavior and provides the 2nd instance of the multi-tool-single-class asymmetry pattern (1st = documented in `content_strategy_agent_validation.md` §Related). For Fold promotion of this pattern, a 3rd instance in a future batch would trigger amendment.
4. (Deferred / follow-up — same as `content_strategy_agent` completion-verify) Poll `job_status` for structured-output-shape check. Content-shape FAIL 2nd-instance watch applies here too.

## Related

- **Adjacent tools (same Slice 5 batch 3):** `workflow_orchestration_agent` + `content_strategy_agent` + `marketing_strategy_agent`.
- **Alias sibling (SAME class):** `content_strategy_agent` — see `content_strategy_agent_validation.md`. `strategic_review` + `content_strategy_agent` both route to the SAME `ContentStrategyAgent` instance path per invocation (different Celery tasks, but same class runtime).
- **Prior semantic-alias precedent:** `security_agent → MemoryIsolationAgent` at `td_handlers_agents.py:156` — another legacy alias documented in the PR #3487 sweep result. If `security_agent` receives a validation doc in a future batch, that would be the 2nd corroborating instance of the multi-tool-single-class pattern.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`; `docs/audits/PA_TOOLS_GAP_MAP.md`.
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925/S2926 Slice 5 batches 1+2.
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; alias mapping at `td_handlers_agents.py:131` (Session 1068 comment); ContentStrategyAgent implementation at `core/agents/strategy/content_strategy_agent.py`.
- **Ledger rows relevant to this ship:**
  - **Multi-tool-single-class asymmetry:** 2nd instance this ship (1st = `content_strategy_agent` doc §Related). Pattern requires 3rd instance for Fold promotion — potential 3rd via `security_agent` when it validates.
  - **Alias semantic-mismatch risk:** if the S2927 dispatch's AgentResult output shape does NOT match the schema description's SWOT/business-model framing (i.e., the LLM produces content-strategy recommendations instead), that IS the documented alias behavior — not a bug. Not a new Ledger candidate; documented in-doc.
  - **Content-shape FAIL 2nd-instance watch:** same as `content_strategy_agent` + `marketing_strategy_agent` peers.
