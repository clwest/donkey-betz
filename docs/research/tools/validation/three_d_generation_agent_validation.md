# `three_d_generation_agent` — Validation Report (S2926)

**Tool:** `three_d_generation_agent`
**Schema:** `core/services/pa_tool_schemas.py` (agent-tool shape — see §3 schema notes)
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:318`
**Session:** S2926 (Slice 5 batch 2 — quartet with `create_brand_video` + `video_editing_agent` + `character_training_agent`)
**HEAD at validation:** `cea3f9215` (2026-07-24 — post PR #3484 heartbeat wrong-model fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Receipt-shape verified live; end-to-end completion-verify deferred to a later batch (per Rigby Q5(i) hold at 2 completion-verifies per batch).
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2926 T0 SIGN + turn 2 grounded verify. Media-family sample.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`three_d_generation_agent` dispatches `ThreeDAgent` (`core/agents/three_d_agent.py:52`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. The agent ONLY creates 3D models — it has two tools (`convert_to_3d` for 2D→3D and `generate_3d_scene` for text→3D). It CANNOT generate images / video / audio, and has no web search. Uses Replicate API for 3D conversion. ML analysis (`analyze_3d_prompt_with_ml`, Session 268/304) enhances geometry/style routing but doesn't gate execution.

Distinct from `image_generation_agent` (2D image, not 3D); from `video_generation_agent` (video, not 3D); from `character_training_agent` (trains FLUX LoRA style/character models, not 3D geometry).

## Covered actions

`three_d_generation_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `ThreeDAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values at the wrapper.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'ThreeDAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'ThreeDAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up completion via `job_status` deferred to a later batch.

## 3. Schema notes

Identical shared schema as all Slice 5 agent-forwarding tools:

- **Required:** none — `task`/`prompt`/`query` defaults to `''` via `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict); root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194`.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **ThreeDAgent is NOT subject to the Editor synthesis reroute or workspace-content gather.**

## 4. Golden-path examples

**Example 1 — text-to-3D scene:**
```json
{"task": "Generate a low-poly 3D scene of a cyberpunk city at night with neon signage", "context": {"workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "ThreeDAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "ThreeDAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: AgentResult contains the Replicate output URL for the 3D asset (typically `.glb` / `.obj` / `.usdz` depending on the model).

**Example 2 — 2D image to 3D conversion:**
```json
{"task": "Convert the workspace image to a 3D model", "context": {"workspace_id": "<uuid>", "image_url": "<https-url>"}}
```

## 5. Failure / empty-state / pagination notes

- **Missing task text:** empty `task_text` reaches ThreeDAgent; agent's own validation determines behavior.
- **Missing source image (for convert_to_3d):** ThreeDAgent will fail-loud with a "no source image" error in AgentResult.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit.
- **Replicate provider failure:** 3D conversion is external HTTP — network failure / rate limit / model unavailable surfaces as agent error.
- **ML analysis failure:** `analyze_3d_prompt_with_ml` at `three_d_agent.py:32-50` wraps ML routing in try/except; failure produces `{'ml_used': False, 'reason': ...}` and does NOT block the 3D run.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, no auto-wake banner fires.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`three_d_generation_agent` is classified `external` when scored end-to-end. Same shape as its media-family peers in batch 2; the specific external dependency is **Replicate** (3D model providers) in addition to LLM providers.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`ThreeDAgent` + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; potential storage writes for generated 3D asset URLs | `spreading` (downstream) |
| Signal cascade | None | Agent lifecycle signals; potential AgentFollowupSubscription INSERT | `cascading` (downstream) |
| Network egress | None | LLM provider HTTP (planning); Replicate HTTP (3D generation) | `external` (downstream) |

**End-to-end classification:** `external`. Consistent with the media-family peers.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('three_d_generation_agent')` → `'ThreeDAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:93` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['ThreeDAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier.
  - (b) **Polling endpoint(s):** `job_status` PA tool; `AsyncResult(task_id)`; AgentExecution row keyed on `celery_task_id`.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution rows.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `ThreeDAgent.run`):
  - AgentExecution row INSERT + status transitions.
  - LLM provider HTTP for 3D-prompt planning; LLMCallLog INSERT per call.
  - `analyze_3d_prompt_with_ml` ML routing call (`three_d_agent.py:32-50`) — may load ML models into worker memory.
  - Replicate HTTP for 3D generation (long-running external — can take minutes).
  - AgentResult row INSERT (post-run) with 3D asset URL(s).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** AgentExecution + AgentResult keyed on `celery_task_id`; `job_status` for composite view.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)`. Replicate jobs already in-flight are NOT auto-cancelled by revoke — Replicate has its own cancellation API not currently surfaced.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:93`; `execute_agent_task` routing; ThreeDAgent's tool set (`convert_to_3d`, `generate_3d_scene`) or Replicate integration.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch receipt verification: dispatch `three_d_generation_agent` with a minimal task string, confirm envelope shape matches `{task_id, mode: 'async', agent: 'ThreeDAgent', auto_followup, follow_up_will_fire, message}`, confirm the `agent` field resolves to `'ThreeDAgent'` (validates the `_tool_to_agent_name` mapping at `td_handlers_agents.py:93`).

End-to-end completion verification deferred to a later batch (completion-verify budget held at 2/batch per Rigby Q5(i); this batch's slots go to `create_brand_video` + `character_training_agent`). Note: completion-verify of ThreeDAgent would exercise a **long-running Replicate call** (multiple minutes) — worth scheduling into a batch that can absorb the wait or defer to a targeted 3D-agent quality slate.

## Related

- **Adjacent tools (same Slice 5 batch):** `create_brand_video` + `video_editing_agent` + `character_training_agent`.
- **Sibling media agents:** `image_generation_agent`, `image_editing_agent`, `video_generation_agent`, `audio_generation_agent`, `talking_character_agent`, `resolve_agent`.
- **Other Slice 5 tools (deferred to batches 3+):** `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `image_editing_agent`, `workflow_orchestration_agent`.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 10 untested pre-batch-2).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925 Slice 5 batch 1 quartet.
- **Shared infrastructure notes:** shared `_handle_agent_tool`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; ThreeDAgent at `core/agents/three_d_agent.py` (Replicate-backed, 3D-only tool set enforced by design).
- **Ledger rows relevant to this ship:**
  - Second Slice 5 media-family receipt-verify sample (paired with `video_editing_agent`).
  - Replicate provider as a long-running external dependency; documented for batch 3+ completion-verify scheduling.
