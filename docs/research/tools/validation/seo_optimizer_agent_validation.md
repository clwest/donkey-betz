# `seo_optimizer_agent` — Validation Report (S3045 Batch 1)

**Tool:** `seo_optimizer_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="SEOOptimizerAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Register site:** `core/services/tool_dispatcher.py`
**Mapping (`_tool_to_agent_name`):** `seo_optimizer_agent` → `SEOOptimizerAgent` (`core/services/td_handlers_agents.py:104`)
**AGENT_MAP entry:** `SEOOptimizerAgent` present in `core/agent_router.py` `AGENT_MAP`.
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

Content optimizer for search + social discovery. Produces hashtags, SEO titles/descriptions, metadata/alt text, keyword targets (intent-based), and structured recommendations. Rigby routes here after content generation, not before. Does NOT create content — only optimizes.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="SEOOptimizerAgent")` — LLM meta-tool dispatch through `_handle_universal_agent`.
- **Expected inputs:** free-form `task` text describing content to optimize; optional `content` payload key.
- **Dispatch queue:** `long_running` (Celery async).
- **Envelope shape:** `{task_id, mode='async', agent='SEOOptimizerAgent', ...}` — per `_handle_universal_agent`.

## Covered actions

This tool has no schema action-enum decomposition — it dispatches the agent as a single unit via `run_agent(agent_name='SEOOptimizerAgent')`. Coverage is unit-level.

## 3. Evidence — S3045 Batch 1 live dispatch

**PASS criteria (per S3045 D-verdict):** 1) no substitution 2) AgentExecution row 3) class match 4) terminal completed 5) output non-empty.

**Batch 1 dispatch record:**
- `task_id`: `ee809742-fed3-4253-917c-33446b98970f`
- `execution_id`: `ced1cbbb-9360-40bf-a802-b139e6073d65`
- Terminal status: `completed` in 12,327ms
- `output_preview` (first 150 chars): `- **Define the role in one sentence (scope + outcome):** State the job title/function and the measurable value delivered (discoverability, search rankings...`
- All 5 PASS criteria: **PASS**.

**Smoke prompt used:** RaaS validation smoke with no-publish / no-post / no-media guard. Output followed 3-bullet plan + paragraph shape as requested.

## 4. Contract ↔ Implementation Consistency

### 4.1 AGENT_MAP entry

**PASS.** `AgentRouter.AGENT_MAP` contains `SEOOptimizerAgent`.

### 4.2 Mapping resolution

**PASS.** `_tool_to_agent_name('seo_optimizer_agent')` returns `SEOOptimizerAgent` per `td_handlers_agents.py:104`.

### 4.3 Envelope shape

**PASS.** Live dispatch envelope matches `_handle_universal_agent` contract.

## Related

- **Shared handler:** `_handle_universal_agent` at `core/services/td_handlers_agents.py:1924`.
- **Shared mapping:** `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83-163`.
- **Category promotion:** `pa_tools_gap_map.classify_tool` at `core/services/pa_tools_gap_map.py:527-547` (S3045 substrate branch).
- **S3045 Batch 1 close artifact:** `docs/audits/pa_tools/substrate/S3045_batch_1_close_artifact.md`.
