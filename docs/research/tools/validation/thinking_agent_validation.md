# `thinking_agent` — Validation Report (S3045 Batch 1)

**Tool:** `thinking_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="ThinkingAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Register site:** `core/services/tool_dispatcher.py:1120` (`_IMPACT_WORTHY_TOOLS` bucket)
**Mapping (`_tool_to_agent_name`):** `thinking_agent` → `ThinkingAgent` (`core/services/td_handlers_agents.py:101`)
**AGENT_MAP entry:** `ThinkingAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 1: customer-facing analysis)
**HEAD at validation:** post-S3044 (2026-07-30)
**Ship shape:** Doc + live-dispatch smoke (RaaS bar per S3045 D-verdict — Option D substrate + reframed goal)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** S3045 T1 SIGN AGREE (multi-turn tool_runs; see §Related).
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Deep reasoning agent — analyzes platform state, diagnoses inconsistency between collected signals and downstream conversion (experiments / knowledge transfers / conversations / dreams), and prescribes concrete follow-up dispatches. Rigby routes here when a request needs synthesis across multiple platform surfaces rather than data retrieval.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="ThinkingAgent")` — LLM meta-tool dispatch through `_handle_universal_agent`.
- **Expected inputs:** free-form `task` text describing what to reason about; optional `context` payload keys promoted via `run_agent` handler (`workspace_id`, `conversation_id`).
- **Dispatch queue:** `long_running` (Celery async).
- **Envelope shape:** `{task_id, mode='async', agent='ThinkingAgent', auto_followup, follow_up_will_fire, message}` — per `_handle_universal_agent` at `td_handlers_agents.py:1924+`.

## Covered actions

This tool has no schema action-enum decomposition — it dispatches the agent as a single unit via `run_agent(agent_name='ThinkingAgent')`. Coverage is unit-level (dispatch succeeds → agent completes → envelope populated), not per-action.

## 3. Evidence — S3045 Batch 1 live dispatch

**Dispatched via:** `bash tools/pa_local.sh` (PA agentic loop → `run_agent`) — Rigby executed under Claude direction per `feedback_claude_directs_rigby_then_verifies`.

**PASS criteria (per S3045 D-verdict):**
1. `agent_substituted=false` — dispatch envelope `agent` field matched requested class.
2. `AgentExecution` row present and linked to Celery `task_id`.
3. `agent_name_effective == expected_class` (`ThinkingAgent`).
4. Terminal `status='completed'` (or documented FAIL with typed reason).
5. `output_preview` non-empty.

**Batch 1 dispatch record:**
- `task_id`: `220e883a-7fd3-4359-9454-32d193404aee`
- `execution_id`: `a8e22591-f697-43b3-9e5b-4cc100d3abaf`
- Terminal status: `completed` in 70,133ms
- `output_preview` (first 150 chars): `YOUR DATA SHOWS active spider ingestion (Spider Data is 801 across Active Spiders is 81) while experimental and learning pipelines are idle...`
- All 5 PASS criteria: **PASS**.

**Smoke prompt used:** RaaS validation smoke — 3-bullet plan for "summarize what your role does in one paragraph" with explicit no-publish / no-post / no-media guard (S3045 D-verdict smoke prompt rule).

## 4. Contract ↔ Implementation Consistency

### 4.1 AGENT_MAP entry exists and dispatches correctly

**PASS.** `AgentRouter.AGENT_MAP` contains `ThinkingAgent`.

### 4.2 Mapping in `_tool_to_agent_name` resolves correctly

**PASS.** `_tool_to_agent_name('thinking_agent')` returns `ThinkingAgent` per `td_handlers_agents.py:101`.

### 4.3 Envelope shape matches shared-handler contract

**PASS.** Live dispatch produced envelope `{task_id, mode='async', agent='ThinkingAgent', ...}` — matches `_handle_universal_agent` contract.

## Related

- **Shared handler:** `_handle_universal_agent` at `core/services/td_handlers_agents.py:1924`.
- **Shared mapping:** `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83-163`.
- **Category promotion:** `pa_tools_gap_map.classify_tool` at `core/services/pa_tools_gap_map.py:527-547` (S3045 substrate branch).
- **S3045 Batch 1 close artifact:** `docs/audits/pa_tools/substrate/S3045_batch_1_close_artifact.md`.
- **Slice 5 CLOSE artifact:** `docs/audits/pa_tools/substrate/slice_5_close_artifact.md` (analogous shared-handler shape).
