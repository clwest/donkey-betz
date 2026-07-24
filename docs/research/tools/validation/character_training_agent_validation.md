# `character_training_agent` — Validation Report (S2926)

**Tool:** `character_training_agent`
**Schema:** `core/services/pa_tool_schemas.py` (agent-tool shape — see §3 schema notes)
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:319`
**Session:** S2926 (Slice 5 batch 2 — quartet with `create_brand_video` + `video_editing_agent` + `three_d_generation_agent`)
**HEAD at validation:** `cea3f9215` (2026-07-24 — post PR #3484 heartbeat wrong-model fix)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. Per Rigby S2926 T0 SIGN: `character_training_agent` is the batch 2 **media-family completion-verify representative** — validates the shared handler → Replicate FLUX LoRA training path (external + long-running via `check_status` polling shape).
**Category upgrade target:** `untested` → `validated_full_with_completion`
**Rigby SIGN:** S2926 T0 SIGN + turn 2 grounded verify. Media-family completion-verify representative for batch 2.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`character_training_agent` dispatches `CharacterTrainingAgent` (`core/agents/training/character_training_agent.py:60`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. The agent trains custom character/style FLUX LoRA models via Replicate. Three tools: `create_character` (create a new character with training images), `submit_training` (submit character for training), `check_status` (poll training status). Requires 5–20 training images per Replicate FLUX LoRA minimums. ML analysis (`analyze_training_data_with_ml`, Session 280) routes text+clustering models for training-data quality inspection.

Distinct from `image_generation_agent` (uses trained characters, doesn't train them); from `three_d_generation_agent` (3D geometry, not 2D FLUX LoRA); from a hypothetical `TrainedCreationAgent` (referenced in class docstring as the consumer of trained characters).

## Covered actions

`character_training_agent` is an agent-forwarding tool — the caller passes a `task`/`prompt`/`query` string + optional `context` dict; the tool dispatches `CharacterTrainingAgent.run(task, context)` asynchronously. The AGENT itself exposes three sub-tools (`create_character` / `submit_training` / `check_status`); which one runs is decided by the agent's LLM planner from the caller's task text — the wrapper does not surface these at the tool schema level.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live + end-to-end completion verified.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'CharacterTrainingAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'CharacterTrainingAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up `job_status` returns AgentResult containing training job id / status / (post-completion) LoRA model URL.

## 3. Schema notes

Identical shared schema as all Slice 5 agent-forwarding tools:

- **Required:** none — `task`/`prompt`/`query` defaults to `''` via `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional:** `context` (dict); root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194`. Class docstring example uses `context={'name': 'mychar', 'trigger_word': 'MYCHAR'}` — these are consumed by CharacterTrainingAgent internally, not by the wrapper.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `:1234-1235` when `user_id` present.
- **CharacterTrainingAgent is NOT subject to the Editor synthesis reroute or workspace-content gather.**

## 4. Golden-path examples

**Example 1 — create character (setup only, no training submit):**
```json
{"task": "Create a new character named 'mychar' with trigger word 'MYCHAR'", "context": {"workspace_id": "<uuid>", "name": "mychar", "trigger_word": "MYCHAR"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "CharacterTrainingAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "CharacterTrainingAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up `job_status`: AgentResult contains character creation confirmation + validation of training-image count (min 5, target 20).

**Example 2 — submit training (long-running external):**
```json
{"task": "Submit training for character 'mychar' with images from workspace", "context": {"workspace_id": "<uuid>", "name": "mychar"}}
```
`submit_training` returns a Replicate prediction ID; actual training runs asynchronously on Replicate infrastructure (typically 15–60 minutes). Follow up with `check_status`.

## 5. Failure / empty-state / pagination notes

- **Missing task text:** empty `task_text` reaches CharacterTrainingAgent; agent's LLM planner may attempt a generic plan or fail-loud.
- **Insufficient training images:** `create_character` / `submit_training` will fail-loud if fewer than 5 images per FLUX LoRA minimum (system_prompt guidance at `character_training_agent.py:76+`).
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit.
- **Replicate provider failure:** training submission is external HTTP — network failure / auth error / quota exceeded surfaces as agent error in AgentResult.
- **Training-in-progress state:** `submit_training` returns immediately with a Replicate prediction id; the actual training runs OUT-OF-BAND on Replicate (not tracked by our Celery task). `check_status` is the only way to observe training progress; the parent AgentExecution completes long before training finishes.
- **ML analysis failure:** `analyze_training_data_with_ml` at `character_training_agent.py:37-55` wraps ML routing in try/except; failure produces `{'ml_used': False, 'reason': ...}` and does NOT block the training submission.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, no auto-wake banner fires.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`character_training_agent` is classified `external` when scored end-to-end. Media-family peer with an additional characteristic: **long-running out-of-band Replicate training jobs** that persist beyond the parent AgentExecution's completion. Cost implication: submitting training is billable on Replicate (typically $2–$5 per FLUX LoRA training run).

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`CharacterTrainingAgent` + Celery task + out-of-band Replicate training) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) + external Replicate training instance | `external` (with out-of-band tail) |
| Data mutation | None | AgentExecution + AgentResult INSERTs; persistent Replicate prediction / model rows outside our DB | `spreading` (downstream + external persistence) |
| Signal cascade | None | Agent lifecycle signals; potential AgentFollowupSubscription INSERT | `cascading` (downstream) |
| Network egress | None | LLM provider HTTP (planning); Replicate HTTP (create + submit + status); billable Replicate compute | `external` (downstream, billable) |

**End-to-end classification:** `external`. Cost/side-effect note: `submit_training` initiates real billable Replicate compute; a completion-verify with a test dispatch string should avoid actually submitting a training job. Recommended test-dispatch path exercises `create_character` (setup only, no Replicate compute) rather than `submit_training`.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('character_training_agent')` → `'CharacterTrainingAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:94` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` | `read` | `tool_dispatcher.py:1230-1232` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; no-op for non-Editor agents |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['CharacterTrainingAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). No secondary domain identifier at the wrapper. Downstream `submit_training` returns a **Replicate prediction id** in AgentResult — a THIRD identifier tier beyond our AgentExecution / celery_task_id.
  - (b) **Polling endpoint(s):** `job_status` for parent Celery/Agent completion; agent-side `check_status` sub-tool for Replicate training progress (post-parent-completion).
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks; `submit_training` calls stack up billable Replicate training runs.
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `CharacterTrainingAgent.run`):
  - AgentExecution row INSERT + status transitions.
  - LLM provider HTTP for planning (which sub-tool to run); LLMCallLog INSERT per call.
  - `analyze_training_data_with_ml` ML routing call (`character_training_agent.py:37-55`).
  - Replicate HTTP (create character / submit training / check status).
  - AgentResult row INSERT (post-run) with Replicate prediction id / training status / (post-completion) LoRA model URL.
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
  - **Out-of-band Replicate training compute** (billable, minutes to hours) — persists beyond parent AgentExecution.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** parent AgentExecution + AgentResult keyed on `celery_task_id`; Replicate training progress via CharacterTrainingAgent's `check_status` sub-tool (agent-level, not platform-level).
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)` at the parent affects only the wrapper Celery task; out-of-band Replicate training is NOT auto-cancelled (billable compute continues). Replicate's own cancellation API not currently surfaced through this agent.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:94`; `execute_agent_task` routing; CharacterTrainingAgent's tool set (`create_character`, `submit_training`, `check_status`) or Replicate FLUX LoRA integration; Replicate pricing changes (cost surface impact).

## 6. Evidence

Doc-only sweep this ship, plus **end-to-end completion verification** as batch 2's media-family representative.

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `character_training_agent` with a minimal task string via PA. **Test-dispatch scope note:** the task string should exercise `create_character` (setup only, no Replicate compute) — NOT `submit_training` (initiates billable Replicate FLUX LoRA training). Example task text: `"Create a new character named 'test_dispatch_char' with trigger word 'TDC' (do not submit training)"`.
2. Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'CharacterTrainingAgent', auto_followup, follow_up_will_fire, message}`. Confirm `agent` field resolves to `'CharacterTrainingAgent'` (validates `_tool_to_agent_name` mapping at `td_handlers_agents.py:94`).
3. Poll `job_status` with the returned `task_id` until completion or timeout. Confirm completion payload contains AgentResult; verify NO Replicate prediction id was returned (confirms `create_character`-only path, no billable submit_training).
4. Confirm heartbeat writes are advancing during long-running dispatch (validates PR #3484 AgentTaskExecution → AgentExecution heartbeat wrong-model fix landed cleanly).

## Related

- **Adjacent tools (same Slice 5 batch):** `create_brand_video` (WorkflowAgent, may delegate to CharacterTrainingAgent) + `video_editing_agent` + `three_d_generation_agent`.
- **Sibling media agents:** `image_generation_agent`, `image_editing_agent`, `video_generation_agent`, `audio_generation_agent`, `talking_character_agent`, `resolve_agent`.
- **Other Slice 5 tools (deferred to batches 3+):** `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `image_editing_agent`, `workflow_orchestration_agent`.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 10 untested pre-batch-2).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925 Slice 5 batch 1 quartet.
- **Shared infrastructure notes:** shared `_handle_agent_tool`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-160`; CharacterTrainingAgent at `core/agents/training/character_training_agent.py` (Session 280 clean architecture unification).
- **Ledger rows relevant to this ship:**
  - First Slice 5 media-family end-to-end completion-verify — establishes the media-family completion pattern for batches 3+.
  - Third-tier identifier surface (Replicate prediction id in AgentResult, beyond AgentExecution / celery_task_id) — documented as an authoring detail; first exercise this ship.
  - Out-of-band billable-compute cost surface (Replicate FLUX LoRA training) — documented as a cost consideration for completion-verify scheduling in future media-agent batches.
  - Cross-batch verify: heartbeat writes should now advance cleanly via PR #3484 AgentExecution fix (this batch's completion-verify is the first opportunity to confirm the fix landed).
