# `image_editing_agent` — Validation Report (S2928)

**Tool:** `image_editing_agent`
**Schema:** `core/services/pa_tool_schemas.py:1674`
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:313`
**Session:** S2928 (Slice 5 batch 4 — FINAL pair with `content_writer_agent`; CLOSES Slice 5 at 14/14)
**HEAD at validation:** `596e2620b` (2026-07-24 — post S2927 close-cascade amendment)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Receipt-verify only (per Rigby T0 SIGN Q1 verdict — last media-family tool in Slice 5; completion-verify representative is `content_writer_agent` for batch 4).
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2928 T0 SIGN Q1 verdict — pair approved (fork A doc-only close, Chris D-verdict); no per-tool completion-verify because ImageEditingAgent invokes sub-tools (upscale / remove_background / recolor / etc.) that require actual Cloudinary image assets to exercise — completion-verify without a real image_id would exercise the tool-error path, not the golden path.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`image_editing_agent` dispatches `ImageEditingAgent` (`core/agents/image_editing_agent.py:58`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. `ImageEditingAgent` is a **media-editing agent** specialized for modifying existing images — it CANNOT create new images (that is `image_generation_agent → ImageAgent`), CANNOT generate video/audio, and CANNOT search the web (`image_editing_agent.py:68-73`). Available operations (`:116-193`): `upscale` (2x/4x with optional creative AI detail), `remove_background`, `create_variations` (style variations), `recolor` (change colors), `search_replace` (find + replace objects), `process_image` (general-purpose PIL: resize, center_crop, circular_mask, enhance, format convert — supports chained operations for badge/thumbnail creation flows).

Distinct from `image_generation_agent` (image creation) and `character_training_agent` (LoRA training) — this tool is the **last remaining media-family tool** in the Slice 5 corpus (batch 4 CLOSES Slice 5 at 14/14). Prior Slice 5 media-family tools validated: `three_d_generation_agent` (S2926 batch 2), `video_editing_agent` (S2926 batch 2), `character_training_agent` (S2926 batch 2), `create_brand_video` (S2926 batch 2 — WorkflowAgent-mapped media orchestrator).

## Covered actions

`image_editing_agent` is an agent-forwarding tool — the caller passes `task` (edit description) + optional `context` dict (typically containing `image_url` / `edit_type` / operation parameters per schema); the tool dispatches `ImageEditingAgent.execute(task, context)` asynchronously. There are no per-tool `action` enum values — the agent internally picks which sub-tool (upscale / remove_background / etc.) to invoke based on the task text.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'ImageEditingAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'ImageEditingAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Completion-verify is **out of scope this batch** — exercising the golden path requires a real Cloudinary image asset (image_id or URL) that the agent's sub-tools can actually operate on. Without a real image, the completion path exercises tool-error handling (image-not-found), not the intended sub-tool operation. Documented for future Slice 6+ or dedicated media-verify session.

## 3. Schema notes

Identical shared shape as all Slice 5 agent-forwarding tools:

- **Required:** `task` (per schema `required: ['task']` at `pa_tool_schemas.py:1692`). Handler still accepts `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict). Schema hints `image_url`, `edit_type`, `parameters` (`pa_tool_schemas.py:1689`). Root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194` — none of the promoted keys are media-specific (no `image_url` or `image_id` in the promotion list); media identifiers must be nested under `context` explicitly.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `tool_dispatcher.py:1234-1235` when `user_id` present.
- **Sub-tool selection:** ImageEditingAgent parses the task text via GPT and picks one of `upscale` / `remove_background` / `create_variations` / `recolor` / `search_replace` / `process_image`. Each sub-tool has its own required parameters (e.g. `upscale` requires `image_id`, `scale_factor ∈ [2, 4]`; see `image_editing_agent.py:117-143`).
- **Image identifier flexibility:** the system prompt at `:98` explicitly accepts UUID, sequential number, or full Cloudinary URL — the resolver behind the sub-tools normalizes these.
- **Tool_name is NOT propagated to ImageEditingAgent** — the wrapper resolves tool_name → agent class name via `_tool_to_agent_name` at `td_handlers_agents.py:88` and dispatches `execute_agent_task.apply_async(args=['ImageEditingAgent', task_text, context], queue='long_running')`. Any operation differentiation must come from the caller's task text or explicit sub-tool parameters in `context`.

## 4. Golden-path examples

**Example 1 — remove background (simplest single-step operation):**
```json
{"task": "Remove the background from image abc123", "context": {"image_id": "abc123", "workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "ImageEditingAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "ImageEditingAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Completion (out-of-scope this batch, documented for reference): AgentResult with `data.tool_used = 'remove_background'`, `data.image_id`, `data.output_url` (Cloudinary URL of the background-removed image), `data.operation = 'remove_background'`.

**Example 2 — chained badge creation (multi-step process_image):**
```json
{"task": "Create a circular badge from headshot xyz789 with brightness enhancement", "context": {"image_id": "xyz789", "workspace_id": "<uuid>"}}
```
Expected: identical envelope shape to Example 1. Agent internally chains `remove_background` → `process_image` with `center_crop + circular_mask + enhance` per system prompt guidance (`image_editing_agent.py:111`).

## 5. Failure / empty-state / pagination notes

- **Missing task text:** `task_text` reaches ImageEditingAgent as empty string; the agent's LLM sub-tool selection has no signal to route on → returns `success=False` with error text.
- **Missing image_id / invalid image_id:** sub-tool resolution fails (Cloudinary lookup returns 404) → sub-tool returns error; agent returns `success=False` with error surfaced.
- **Unsupported operation request:** if task text asks for creation ("draw an image of X") — the agent's system prompt at `:113-114` explicitly redirects: "You CANNOT create new images... If asked to create something new, explain you can only edit existing images." The agent returns `success=True` with an explanatory message rather than dispatching a sub-tool.
- **Cloudinary API failure:** sub-tool HTTP failure → surface as sub-tool error → agent returns `success=False`.
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit; envelope surfaces `error_code` distinct from `AGENT_EXECUTION_FAILED`.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, the S1178 auto-wake subscription will NOT fire.
- **Sub-tool timeout:** upscale + creative_upscale operations can be slow (multi-second Cloudinary AI enhancement). No explicit `llm_timeout` override in ImageEditingAgent — inherits BaseAgent default. Long operations may hit the outer Celery task timeout.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`image_editing_agent` is classified `external` when scored end-to-end, and **amplified** by media provider egress (Cloudinary API) — the primary side effect is remote image asset creation/mutation.

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`ImageEditingAgent` + Celery task + Cloudinary egress) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; LLMCallLog rows per LLM planning call; **remote Cloudinary asset creation** (new derived image on Cloudinary — external mutation, not tracked in local DB unless explicitly persisted); potentially `Image` model row INSERT if the sub-tool persists the derived asset | `spreading` (downstream, amplified — external mutation surface) |
| Signal cascade | None | Agent lifecycle signals; optionally Image post_save if the derived asset is persisted; potential AgentFollowupSubscription INSERT | `spreading` (downstream) |
| Network egress | None | LLM provider HTTP (sub-tool selection); **Cloudinary API HTTP** (sub-tool image operations — upscale/remove_background/recolor/etc.); potentially additional egress for `create_variations` (Cloudinary AI features) | `external` (amplified — media provider is the dominant egress) |

**End-to-end classification:** `external`. Amplification factor is bounded by the sub-tool count invoked per task (typically 1 for single-operation tasks; up to ~3 for chained flows like badge creation per system prompt guidance). Per Rigby S2925 Q2 authoring guidance: Slice 5 tools MUST be classified end-to-end; media provider egress remains the distinct §5a axis flagged in prior batches (S2926 Ledger candidate — no 2nd instance yet formalized as Fold).

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('image_editing_agent')` → `'ImageEditingAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:88` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['ImageEditingAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`) → `ImageEditingAgent.execute` (`core/agents/image_editing_agent.py`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). **Secondary media identifier NOT surfaced until completion:** the Cloudinary URL of the derived image only appears in the completed AgentResult's `data.output_url` — the initial receipt envelope contains no media pointer.
  - (b) **Polling endpoint(s):** `job_status` PA tool for parent completion.
  - (c) **Idempotency stance:** `none`. Repeat dispatches on the same source image_id = independent Celery tasks + independent Cloudinary asset creations + independent AgentExecution rows.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `ImageEditingAgent.execute`):
  - Parent AgentExecution INSERT + status transitions.
  - LLM sub-tool selection call (LLMCallLog INSERT).
  - Sub-tool invocation → Cloudinary API HTTP request(s) → **remote asset mutation** (Cloudinary namespace).
  - Parent AgentResult INSERT (post-run) with sub-tool-specific data keys (`tool_used`, `image_id`, `output_url`, `operation`).
  - Potentially an `Image` model row INSERT if the derived asset is persisted (Slice 5 doc-only sweep does not verify this path — Slice 6+ or dedicated media session should verify).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** parent AgentExecution + AgentResult keyed on parent `celery_task_id`. `job_status` surfaces the parent composite view via `_get_agent_execution_output` deep extraction (`td_handlers_agents.py:171-172` documents `ImageAgent: metadata.images[*].url` extraction — ImageEditingAgent likely follows the same shape, unverified in this batch).
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)` on the parent halts the Celery task. If revoke fires AFTER Cloudinary API returns (asset created) but BEFORE AgentResult persistence, the Cloudinary asset persists remotely without a local reference — compensating cleanup required manually. No auto-rollback.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:88`; `execute_agent_task` routing; ImageEditingAgent sub-tool definitions at `image_editing_agent.py:116-193`; Cloudinary API contract changes; media-provider-egress §5a axis promotion (if 2nd instance of "media provider egress as distinct §5a downstream axis" Fold candidate surfaces in Slice 6+).

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `image_editing_agent` with a minimal task string via PA (e.g. `"remove background from this image"` — no real image_id needed for receipt verification). Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'ImageEditingAgent', auto_followup, follow_up_will_fire, message}`. **Critical: confirm `agent` field is `'ImageEditingAgent'`** (mapping verification per S2927 PR #3487 pattern).
2. Do NOT poll `job_status` for completion — completion path without a real image asset exercises the tool-error branch (image-not-found), which is not the intended validation surface. Receipt-verify only.
3. (Optional forensic) if the completion is polled anyway, expect `success=False` with an image-lookup error surfaced — not a failure of this validation.

## Related

- **Adjacent tool (same Slice 5 batch 4):** `content_writer_agent` (content-tier; receipt-verify + completion-verify representative).
- **Sibling media-family tools (Slice 5):** `three_d_generation_agent` (S2926 batch 2 — ThreeDAgent), `video_editing_agent` (S2926 batch 2 — VideoEditingAgent), `character_training_agent` (S2926 batch 2 — CharacterTrainingAgent), `create_brand_video` (S2926 batch 2 — WorkflowAgent-mapped media orchestrator).
- **Sibling image tools (outside Slice 5 — registered in other slices or via other handler paths):** `image_generation_agent` (`ImageAgent`) — the creation counterpart to this editing tool. Both are `_handle_agent_tool`-registered in `tool_dispatcher.py`.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 2 untested pre-batch-4).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925 Slice 5 batch 1 quartet; S2926 Slice 5 batch 2 quartet; S2927 Slice 5 batch 3 quartet (advanced Slice 5 to 12/14).
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-163`; ImageEditingAgent implementation at `core/agents/image_editing_agent.py` (~450 lines including sub-tool schemas). Media provider egress (Cloudinary) is the distinct §5a downstream axis — 1st documented instance in this doc; if a 2nd instance surfaces in Slice 6+, promote as a distinct §5a facet in the taxonomy.
- **Ledger rows relevant to this ship:**
  - **Media provider egress as distinct §5a downstream axis** — Fold candidate at 1st documented instance (S2926 create_brand_video documented it initially; this doc corroborates the shape). If a 2nd media-family tool in Slice 6+ surfaces the same distinct external mutation surface, promote.
  - **Sub-tool selection asymmetry** — ImageEditingAgent uses LLM to pick from 6 sub-tools; different from single-purpose Slice 5 agents. 1st documented instance of "agent-with-internal-sub-tool-selection" in the Slice 5 corpus; watch for 2nd in Slice 6+ (candidate: ImageAgent, VideoAgent — likely also multi-sub-tool internally).
