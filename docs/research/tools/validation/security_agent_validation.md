# `security_agent` — Validation Report (S3045 Batch 1)

**Tool:** `security_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="MemoryIsolationAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Register site:** `core/services/tool_dispatcher.py`
**Mapping (`_tool_to_agent_name`):** `security_agent` → `MemoryIsolationAgent` (`core/services/td_handlers_agents.py:160`) — **ALIAS: 2nd tool name resolving to the same class**. Sibling entry `memory_isolation_agent` → `MemoryIsolationAgent` at line 159.
**AGENT_MAP entry:** `MemoryIsolationAgent` present in `core/agent_router.py` `AGENT_MAP`.
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

**Alias mapping — semantic mismatch flagged.** Rigby (and downstream LLM callers) route to `security_agent` expecting security-review behavior (vulnerability scan, threat model, auth review, etc.), but the mapping resolves to `MemoryIsolationAgent` which returns a canned "Memory isolation operation completed" response. The tool works mechanically but the *semantics don't match the tool name*.

This is the 3rd instance of the multi-tool → single-class alias pattern documented in `slice_5_close_artifact.md §1` (candidate 3rd instance was called out there; S3045 Batch 1 confirms).

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="MemoryIsolationAgent")` OR `run_agent(agent_name="security_agent")` — LLM meta-tool dispatch through `_handle_universal_agent`. The mapping normalizes tool-name suffix if `security_agent` is passed directly.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running` (Celery async).
- **Envelope shape:** `{task_id, mode='async', agent='MemoryIsolationAgent', ...}` — per `_handle_universal_agent`. **The `agent` field always reflects the resolved class (`MemoryIsolationAgent`), not the requested tool name (`security_agent`)**, so envelope-based receipt verification correctly surfaces the alias resolution.

## Covered actions

This tool has no schema action-enum decomposition — it dispatches the agent as a single unit via `run_agent(agent_name='MemoryIsolationAgent')`. Coverage is unit-level.

## 3. Evidence — S3045 Batch 1 live dispatch

**PASS criteria (per S3045 D-verdict):** 1) no substitution 2) AgentExecution row 3) class match 4) terminal completed 5) output non-empty.

**Batch 1 dispatch record:**
- `task_id`: `a9511c64-4c00-4f6b-b478-390285ed7580`
- `execution_id`: `bf06ab08-1e1f-4b6b-8c55-2404c4be03f5`
- Terminal status: `completed` in 4,251ms
- `output_preview`: `Memory isolation operation completed`
- Criteria breakdown: 1 ✓ (no substitution — envelope `agent`=`MemoryIsolationAgent` == mapping target) · 2 ✓ (AgentExecution row exists) · 3 ✓ (class match against MAPPING TARGET, not against tool-name semantic) · 4 ✓ (terminal=completed) · 5 ✓ (output non-empty, though canned).

**Verdict: PASS w/ FINDING.** All 5 wiring/contract criteria PASS. But semantic-mismatch finding logged: `security_agent` tool name does not behave as its name suggests (user expects security review; gets memory-isolation completion signal). See §5 for substrate ledger row.

**Smoke prompt (Batch 1 uniform):** RaaS validation smoke with no-publish / no-post / no-media guard.

## 4. Contract ↔ Implementation Consistency

### 4.1 AGENT_MAP entry

**PASS.** `AgentRouter.AGENT_MAP` contains `MemoryIsolationAgent`.

### 4.2 Mapping resolution + alias behavior

**PASS (mechanical) / FINDING (semantic).** `_tool_to_agent_name('security_agent')` returns `MemoryIsolationAgent` per `td_handlers_agents.py:160`. The alias is intentional (2nd tool routing to same class per slice_5 pattern). Envelope `agent` field correctly reflects the resolved target — so integrity signal (S2927 PR #3487 regression class) holds.

### 4.3 Envelope shape

**PASS.** Live dispatch envelope matches `_handle_universal_agent` contract.

## 5. Substrate ledger row (proposed for Rigby Tool Gap Ledger)

**Row title:** `[S3045] agent_via_run_agent alias semantic mismatch — security_agent → MemoryIsolationAgent`

**Class:** Multi-tool → single-class alias where tool name creates user-expectation mismatch with actual agent behavior. 3rd class instance overall (after `content_strategy_agent` / `strategic_review` intentional alias at slice_5 close, and `create_brand_video` / `create_project_from_research` intentional WorkflowAgent alias). Distinct from those in that this alias creates confusion rather than reflecting a delegate pattern.

**Mitigation options (3):**

- **A. Doc note only (current mitigation).** This validation doc names the mismatch; Rigby's response synthesis can surface the alias to callers. Cheapest; risk = future callers don't read the doc.
- **B. Rename alias to eliminate expectation.** Remove `security_agent` mapping OR rename to `security_agent_stub`. Requires audit of downstream callers using the old name. Higher effort.
- **C. Author dedicated `SecurityAgent` class.** New agent class implementing genuine security-review behavior (vuln scan / threat model / auth review). Renames mapping target from `MemoryIsolationAgent` → `SecurityAgent`. Highest effort; also highest fit for future customer-facing RaaS use.

**Trigger threshold:** open Option C if a 2nd real semantic-mismatch surface hits (per PLAYBOOK-6.10.8 fold-class instance ladder).

## Related

- **Shared handler:** `_handle_universal_agent` at `core/services/td_handlers_agents.py:1924`.
- **Shared mapping:** `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83-163`.
- **Sibling doc:** future `memory_isolation_agent_validation.md` (same target class, different tool name).
- **Slice 5 CLOSE §1:** multi-tool-single-class instances (`slice_5_close_artifact.md`) — S3045 confirms candidate 3rd instance.
- **Category promotion:** `pa_tools_gap_map.classify_tool` at `core/services/pa_tools_gap_map.py:527-547` (S3045 substrate branch).
- **S3045 Batch 1 close artifact:** `docs/audits/pa_tools/substrate/S3045_batch_1_close_artifact.md`.
