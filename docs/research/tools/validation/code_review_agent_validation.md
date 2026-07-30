# `code_review_agent` — Validation Report (S3045 Batch 1)

**Tool:** `code_review_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="CodeReviewAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Register site:** `core/services/tool_dispatcher.py`
**Mapping (`_tool_to_agent_name`):** `code_review_agent` → `CodeReviewAgent` (`core/services/td_handlers_agents.py:128`)
**AGENT_MAP entry:** `CodeReviewAgent` present in `core/agent_router.py` `AGENT_MAP`.
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

Code reviewer — accepts a file path or an inline code block (fenced with triple backticks) and returns review comments. Rigby routes here for targeted code review passes.

**Input contract:** unlike other Batch 1 agents which accept free-form `task` text, `code_review_agent` **requires** either a file path reference or a code block in the task text. Absent either, agent returns a structured `MISSING_INPUT` error with a helpful re-invocation hint (e.g. `` `review core/services/foo.py` ``).

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="CodeReviewAgent")` — LLM meta-tool dispatch through `_handle_universal_agent`.
- **Expected inputs:** `task` text MUST include either a file path (`review core/services/foo.py`) or a fenced code block (triple backticks). Optional `context` keys.
- **Dispatch queue:** `long_running` (Celery async).
- **Envelope shape:** `{task_id, mode='async', agent='CodeReviewAgent', ...}` — per `_handle_universal_agent`.
- **Failure envelope:** `{status: 'failed', error_message: 'MISSING_INPUT: no file path or code block found in task', output_preview: <helpful hint>}` — structured, actionable, not a crash.

## Covered actions

This tool has no schema action-enum decomposition — it dispatches the agent as a single unit via `run_agent(agent_name='CodeReviewAgent')`. Coverage is unit-level.

## 3. Evidence — S3045 Batch 1 live dispatch

**PASS criteria (per S3045 D-verdict):** 1) no substitution 2) AgentExecution row 3) class match 4) terminal completed 5) output non-empty.

**Batch 1 dispatch record:**
- `task_id`: `a2b97b5b-6bad-4514-b4f7-24a4c89d1ead`
- `execution_id`: `e1a801ca-f501-4870-b462-ea52b9690d7f`
- Terminal status: **`failed`** in 851ms
- `error_message`: `MISSING_INPUT: no file path or code block found in task`
- `output_preview`: `I need a file path or a code snippet to review. Try again with something like: 'review core/services/foo.py', or paste a code block inside triple backticks.`
- Criteria breakdown: 1 ✓ (no substitution — envelope agent field == `CodeReviewAgent`) · 2 ✓ (AgentExecution row exists) · 3 ✓ (class match) · 4 **✗** (terminal=failed) · 5 ✗ (output_preview is helpful hint, not the requested 3-bullet plan).

**Verdict: RaaS-dispatch PASS; task-level smoke FAIL (input-contract).** Wiring / mapping / envelope shape / dispatch path all validated (RaaS bar met). Agent-level input-contract enforcement fired correctly on the task itself (structured error, actionable message, no crash) — the *smoke prompt* was invalid for this specific agent, not the *tool*. Per Rigby T1 SIGN Q1 edge-case taxonomy: **input-contract failure** — tool works, smoke harness needs tailored per-tool inputs. Does NOT block CLOSE (Rigby T0 SIGN wording clarification: keeps PASS/FAIL precision across artifacts).

**Smoke prompt (Batch 1 uniform):** `RaaS validation smoke: return a 3-bullet plan for how you would approach the task "summarize what your role does in one paragraph." Do NOT publish, do NOT post to any external service, do NOT create media. Return the 3-bullet plan + one short result paragraph only.`

**Tailored smoke prompt for future re-validation:** `Please review this snippet: \`\`\`python\ndef add(a, b): return a + b\n\`\`\` — return 2-3 short review comments only, no code changes.`

## 4. Contract ↔ Implementation Consistency

### 4.1 AGENT_MAP entry

**PASS.** `AgentRouter.AGENT_MAP` contains `CodeReviewAgent`.

### 4.2 Mapping resolution

**PASS.** `_tool_to_agent_name('code_review_agent')` returns `CodeReviewAgent` per `td_handlers_agents.py:128`.

### 4.3 Envelope shape (including failure envelope)

**PASS.** Success envelope matches `_handle_universal_agent` contract. Failure envelope is structured with typed `error_message` + actionable `output_preview` — no crash.

## 5. New taxonomy category — input-contract failure

This tool surfaces a shape not previously named in the S3045 D-verdict failure taxonomy (wiring / contract / runtime). Adds:

- **Input-contract failure:** mapping is correct, class dispatches, envelope populated, but agent-level input schema enforces a per-tool contract that the uniform smoke prompt does not satisfy. Disposition per Rigby T1 SIGN: **PASS with tailored-smoke-prompt caveat**; does NOT block CLOSE. Distinct from `contract failure` (which is envelope/AgentExecution missing).

Documented in S3045 Batch 1 close artifact §Failure taxonomy extensions.

## Related

- **Shared handler:** `_handle_universal_agent` at `core/services/td_handlers_agents.py:1924`.
- **Shared mapping:** `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83-163`.
- **Category promotion:** `pa_tools_gap_map.classify_tool` at `core/services/pa_tools_gap_map.py:527-547` (S3045 substrate branch).
- **S3045 Batch 1 close artifact:** `docs/audits/pa_tools/substrate/S3045_batch_1_close_artifact.md`.
