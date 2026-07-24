# `video_editing_agent` — Validation Report (S2926)

**Tool:** `video_editing_agent`
**Schema:** `core/services/pa_tool_schemas.py` (agent-tool shape — see §3 schema notes)
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:315`
**Session:** S2926 (Slice 5 batch 2 — quartet with `create_brand_video` + `three_d_generation_agent` + `character_training_agent`)
**HEAD at validation:** `cea3f9215` (2026-07-24 — post PR #3484 heartbeat wrong-model fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Receipt-shape verified live; end-to-end completion-verify deferred to a later batch (per Rigby Q5(i) hold at 2 completion-verifies per batch; slots used by `create_brand_video` + `character_training_agent`).
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2926 T0 SIGN + turn 2 grounded verify. Media-family sample; sibling to `three_d_generation_agent` + `character_training_agent`.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`video_editing_agent` dispatches `VideoEditingAgent` (`core/agents/video_editing_agent.py:59`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. The agent EDITS existing videos — trim, add text overlay, apply visual effects, extract a frame, concatenate multiple videos, change playback speed. It CANNOT generate videos (that's `video_generation_agent` → `VideoAgent`), and has no image / audio / web-search tools. Uses ML analysis (`agent_model_router`, Session 268/304) for edit-request routing. Session 856 wired an `actionable_config` with approve/revise/reject content-review actions.

Distinct from `video_generation_agent` (creates new video, not edit); from `image_editing_agent` (image, not video); from `create_brand_video` (WorkflowAgent orchestrator that may delegate TO VideoEditingAgent, not a peer edit tool).

## Covered actions

`video_editing_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `VideoEditingAgent.run(task, context)` asynchronously. There are no per-tool `action` enum values at the wrapper.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'VideoEditingAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'VideoEditingAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up completion via `job_status` deferred to a later batch (completion-verify budget held at 2/batch per Rigby Q5(i)).

## 3. Schema notes

Identical shared schema as all Slice 5 agent-forwarding tools:

- **Required:** none — `task`/`prompt`/`query` defaults to `''` via `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict); root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194`.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **VideoEditingAgent is NOT subject to the Editor synthesis reroute or workspace-content gather** (those apply to EditorAgent + ContentWriterAgent only at `tool_dispatcher.py:1267-1317`).

## 4. Golden-path examples

**Example 1 — trim + text overlay:**
```json
{"task": "Trim the workspace video to 15s and add title text 'DonkeyBetz — Beta Access'", "context": {"workspace_id": "<uuid>", "video_url": "<https-url-to-source>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "VideoEditingAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "VideoEditingAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: AgentResult contains the edited video URL + edit operation log + Session 856 content-review action (`approve` / `revise` / `reject` per `actionable_config`).

## 5. Failure / empty-state / pagination notes

- **Missing task text:** empty `task_text` reaches VideoEditingAgent; agent's own validation determines behavior.
- **Missing source video:** no source URL / file identifier in `context`; VideoEditingAgent will fail-loud with a clear "no source video" error in AgentResult.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit.
- **Media provider failures:** edit operations may depend on external media APIs (ffmpeg wrappers / Cloudinary / Replicate depending on operation); provider failures surface as agent errors in AgentResult.
- **ML analysis failure:** `analyze_video_edit_with_ml` at `video_editing_agent.py:37-55` wraps ML routing in try/except; failure produces `{'ml_used': False, 'reason': ...}` and does NOT block the edit.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, no auto-wake banner fires.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`video_editing_agent` is classified `external` when scored end-to-end. Media agents differ from business agents (batch 1) in one dimension: **media provider egress** (ffmpeg / Cloudinary / Replicate) in addition to LLM provider egress.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`VideoEditingAgent` + Celery task) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; potential Cloudinary/media-storage writes | `spreading` (downstream) |
| Signal cascade | None | Agent lifecycle signals; potential AgentFollowupSubscription INSERT; Session 856 content-review action side effects | `cascading` (downstream) |
| Network egress | None | LLM provider HTTP (planning); media provider HTTP (ffmpeg/Cloudinary/Replicate) | `external` (downstream) |

**End-to-end classification:** `external`. Consistent with the media-family peers in batch 2.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('video_editing_agent')` → `'VideoEditingAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:90` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['VideoEditingAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier.
  - (b) **Polling endpoint(s):** `job_status` PA tool; `AsyncResult(task_id)`; AgentExecution row keyed on `celery_task_id`.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution rows.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `VideoEditingAgent.run`):
  - AgentExecution row INSERT + status transitions.
  - LLM provider HTTP for edit-request planning; LLMCallLog INSERT per call.
  - `analyze_video_edit_with_ml` ML routing call (`video_editing_agent.py:37-55`) — may load ML models into worker memory.
  - Media provider HTTP (ffmpeg wrappers / Cloudinary / Replicate depending on edit operation).
  - AgentResult row INSERT (post-run); may include edited-video URL + Session 856 content-review payload.
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** AgentExecution + AgentResult keyed on `celery_task_id`; `job_status` for composite view.
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)`; AgentExecution.status settable.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:90`; `execute_agent_task` routing; VideoEditingAgent's tool set (trim / add_text / add_effects / extract_frame / concatenate / speed_change) or media provider wiring.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch receipt verification: dispatch `video_editing_agent` with a minimal task string, confirm envelope shape matches `{task_id, mode: 'async', agent: 'VideoEditingAgent', auto_followup, follow_up_will_fire, message}`, confirm the `agent` field resolves to `'VideoEditingAgent'` (validates the `_tool_to_agent_name` mapping at `td_handlers_agents.py:90`).

End-to-end completion verification deferred to a later Slice 5 batch (completion-verify budget held at 2/batch per Rigby Q5(i); this batch's slots go to `create_brand_video` + `character_training_agent`).

## Related

- **Adjacent tools (same Slice 5 batch):** `create_brand_video` (WorkflowAgent that may delegate to VideoEditingAgent) + `three_d_generation_agent` + `character_training_agent`.
- **Sibling media agents (broader Slice 5 media family):** `image_generation_agent`, `image_editing_agent`, `video_generation_agent`, `audio_generation_agent`, `talking_character_agent`, `resolve_agent` — same shared handler pattern.
- **Other Slice 5 tools (deferred to batches 3+):** `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `image_editing_agent`, `workflow_orchestration_agent`.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 10 untested pre-batch-2).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925 Slice 5 batch 1 quartet.
- **Shared infrastructure notes:** shared `_handle_agent_tool`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; VideoEditingAgent implementation at `core/agents/video_editing_agent.py` (Session 268/304/856 evolution).
- **Ledger rows relevant to this ship:**
  - First Slice 5 media-family receipt-verify sample.
  - Media provider egress documented as an additional §5a downstream axis for the batch 2 media agents (ffmpeg / Cloudinary / Replicate); first exercise this ship.
