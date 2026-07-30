# `research_agent` — Validation Report (S3045 Batch 1)

**Tool:** `research_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="ResearchAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Register site:** `core/services/tool_dispatcher.py:1120` (`_IMPACT_WORTHY_TOOLS` bucket) — also the `run_agent` default fallback per handler substitution logic at `td_handlers_agents.py:2007`.
**Mapping (`_tool_to_agent_name`):** `research_agent` → `ResearchAgent` (`core/services/td_handlers_agents.py:97`)
**AGENT_MAP entry:** `ResearchAgent` present in `core/agent_router.py` `AGENT_MAP`.
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

Evidence-backed research synthesis — pulls from retrieval corpus, produces confidence-scored findings with citations. Also the **default fallback agent** when `run_agent` cannot map the caller's requested `agent_name` (see substitution logic at `td_handlers_agents.py:2007`) — so this tool's reliability is load-bearing for the whole `agent_via_run_agent` bucket.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="ResearchAgent")` — LLM meta-tool dispatch through `_handle_universal_agent`.
- **Expected inputs:** free-form `task` text; optional `context` payload keys (`workspace_id`, `conversation_id`); optional `research`/`research_summary` for follow-up chaining.
- **Dispatch queue:** `long_running` (Celery async).
- **Envelope shape:** `{task_id, mode='async', agent='ResearchAgent', auto_followup=true, follow_up_will_fire=true, message}` — per `_handle_universal_agent`.
- **Fallback note:** `run_agent` substitutes unknown `agent_name` values to `ResearchAgent` (see `td_handlers_agents.py:2007`). Validated dispatch here doubles as validation of the fallback path.

## Covered actions

This tool has no schema action-enum decomposition — it dispatches the agent as a single unit via `run_agent(agent_name='ResearchAgent')`. Coverage is unit-level (dispatch succeeds → agent completes → envelope populated), not per-action.

## 3. Evidence — S3045 Batch 1 live dispatch

**Dispatched via:** `bash tools/pa_local.sh` (PA agentic loop → `run_agent`) — Rigby executed under Claude direction per `feedback_claude_directs_rigby_then_verifies`.

**PASS criteria (per S3045 D-verdict):**
1. `agent_substituted=false` — dispatch envelope `agent` field matched requested class.
2. `AgentExecution` row present and linked to Celery `task_id`.
3. `agent_name_effective == expected_class` (`ResearchAgent`).
4. Terminal `status='completed'`.
5. `output_preview` non-empty.

**Batch 1 dispatch record:**
- `task_id`: `1840eb3f-1aae-4c30-840a-3963278ef669`
- `execution_id`: `4d53c52d-7b95-4b84-aee3-6672de55a047`
- Terminal status: `completed` in 63,778ms
- `output_preview` (first 150 chars): `## Executive summary\nYour request is a smoke-test prompt: produce a minimal, compliant response... Confidence: 80% that this satisfies the intent...`
- All 5 PASS criteria: **PASS**.

**Smoke prompt used:** RaaS validation smoke — 3-bullet plan for "summarize what your role does in one paragraph" with explicit no-publish / no-post / no-media guard.

## 4. Contract ↔ Implementation Consistency

### 4.1 AGENT_MAP entry exists and dispatches correctly

**PASS.** `AgentRouter.AGENT_MAP` contains `ResearchAgent`.

### 4.2 Mapping in `_tool_to_agent_name` resolves correctly

**PASS.** `_tool_to_agent_name('research_agent')` returns `ResearchAgent` per `td_handlers_agents.py:97`.

### 4.3 Envelope shape matches shared-handler contract

**PASS.** Live dispatch produced envelope `{task_id, mode='async', agent='ResearchAgent', ...}` — matches `_handle_universal_agent` contract.

### 4.4 Default-fallback path exercised implicitly

Load-bearing: `research_agent` reliability guards the substitution fallback for unknown `agent_name` requests. Batch 1 dispatch also serves as evidence that the fallback target itself is healthy.

## 5. Prior loose-stem match note

The gap-map stem-matcher (`pa_tools_gap_map.find_matching_doc_stem`) previously matched `research_agent` to `customer_research_agent_validation.md` via loose containment (strategy 3 — `_research_agent` substring). This dedicated file supersedes that match: `find_matching_doc_stem` will now hit strategy 1 (exact match on tool name → `research_agent` stem) before falling through to loose containment. Same class as S3044 substrate ledger row 1 (`workspace_tool` / `kb_tool` rescues); 3rd trigger of that class — see S3045 Batch 1 close artifact for Option B lint escalation trigger evaluation.

## Related

- **Shared handler:** `_handle_universal_agent` at `core/services/td_handlers_agents.py:1924`.
- **Shared mapping:** `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83-163`.
- **Category promotion:** `pa_tools_gap_map.classify_tool` at `core/services/pa_tools_gap_map.py:527-547` (S3045 substrate branch).
- **Substitution fallback:** `td_handlers_agents.py:2007`.
- **S3045 Batch 1 close artifact:** `docs/audits/pa_tools/substrate/S3045_batch_1_close_artifact.md`.
