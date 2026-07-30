# `content_audit_agent` — Validation Report (S3045 Batch 1)

**Tool:** `content_audit_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="ContentAuditAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Register site:** `core/services/tool_dispatcher.py`
**Mapping (`_tool_to_agent_name`):** `content_audit_agent` → `ContentAuditAgent` (`core/services/td_handlers_agents.py:107`)
**AGENT_MAP entry:** `ContentAuditAgent` present in `core/agent_router.py` `AGENT_MAP`.
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

Bias, safety, and ethics guardian — audits prompts + generated outputs for bias/stereotypes, NSFW/violence/safety risks, and inclusion gaps. Emits risk flags, safer rewrites, and transparency summaries. **Does NOT publish, message, or enforce refusals** (guardian-shape, not gatekeeper). Rigby routes here for pre-publish audit passes.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="ContentAuditAgent")` — LLM meta-tool dispatch through `_handle_universal_agent`.
- **Expected inputs:** free-form `task` text describing the content to audit; optional `content` payload key.
- **Dispatch queue:** `long_running` (Celery async).
- **Envelope shape:** `{task_id, mode='async', agent='ContentAuditAgent', ...}` — per `_handle_universal_agent`.

## Covered actions

This tool has no schema action-enum decomposition — it dispatches the agent as a single unit via `run_agent(agent_name='ContentAuditAgent')`. Coverage is unit-level.

## 3. Evidence — S3045 Batch 1 live dispatch

**PASS criteria (per S3045 D-verdict):** 1) no substitution 2) AgentExecution row 3) class match 4) terminal completed 5) output non-empty.

**Batch 1 dispatch record:**
- `task_id`: `6e532086-808a-4dda-87fb-f3c35ce0b523`
- `execution_id`: `802974a2-0d50-41d7-adc4-4f3af466e3da`
- Terminal status: `completed` in 7,157ms
- `output_preview` (first 150 chars): `- **Define the role scope in one sentence:** Identify the agent identity ("ContentAuditAgent, Bias & Ethics Guardian"), the content surfaces covered...`
- All 5 PASS criteria: **PASS**.

**Smoke prompt used:** RaaS validation smoke with no-publish / no-post / no-media guard. Output followed 3-bullet plan + paragraph shape.

## 4. Contract ↔ Implementation Consistency

### 4.1 AGENT_MAP entry

**PASS.** `AgentRouter.AGENT_MAP` contains `ContentAuditAgent`.

### 4.2 Mapping resolution

**PASS.** `_tool_to_agent_name('content_audit_agent')` returns `ContentAuditAgent` per `td_handlers_agents.py:107`.

### 4.3 Envelope shape

**PASS.** Live dispatch envelope matches `_handle_universal_agent` contract.

## Related

- **Shared handler:** `_handle_universal_agent` at `core/services/td_handlers_agents.py:1924`.
- **Shared mapping:** `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83-163`.
- **Category promotion:** `pa_tools_gap_map.classify_tool` at `core/services/pa_tools_gap_map.py:527-547` (S3045 substrate branch).
- **S3045 Batch 1 close artifact:** `docs/audits/pa_tools/substrate/S3045_batch_1_close_artifact.md`.
