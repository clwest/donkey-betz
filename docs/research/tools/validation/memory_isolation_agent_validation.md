# `memory_isolation_agent` — Validation Report (S3045 Batch 2)

**Tool:** `memory_isolation_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="MemoryIsolationAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `memory_isolation_agent` → `MemoryIsolationAgent` (`core/services/td_handlers_agents.py:159`) — **twin of `security_agent` alias** (Batch 1 finding; both tool names resolve to the same class).
**AGENT_MAP entry:** `MemoryIsolationAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 2)
**Ship shape:** Doc + live-dispatch smoke — validates alias behavior from the direct-name side (Batch 1 validated via alias name `security_agent`)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 2 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Memory isolation operations — the actual behavioral semantics behind BOTH the `memory_isolation_agent` (direct) tool name AND the `security_agent` alias (Batch 1 semantic-mismatch finding). Returns canned "Memory isolation operation completed" for smoke-shaped dispatches.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="MemoryIsolationAgent")` OR `run_agent(agent_name="security_agent")` — both resolve to `MemoryIsolationAgent` class per mapping lines 159-160.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 2 live dispatch

**Dispatch:** `task_id=30938b99-77d0-4728-9c47-d32a93b013fc` · `execution_id=58c8fd19-d6ef-430a-93bf-6f9db2698fcd` · terminal `completed` in 4,379ms.

**Output preview:** `Memory isolation operation completed`

**5-criteria PASS:** all met. **PASS.**

**Alias symmetry verified:** identical canned output to `security_agent` (Batch 1) `task_id=a9511c64-…` (4,251ms → 4,379ms; both ~4s; both return the same "Memory isolation operation completed" string). Confirms the alias behaves symmetrically — dispatching by either tool name produces the same behavior. Reinforces the semantic-mismatch finding for `security_agent` from Batch 1: `security_agent` name expectation ≠ `MemoryIsolationAgent` behavior. Substrate ledger row `[S3045] agent_via_run_agent alias semantic mismatch` (deliverable `6981cd08-30bc-4ed9-8f02-29d1f6086deb`) applies.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:159`).
- **4.3 Envelope shape:** PASS.
- **4.4 Alias symmetry (bi-directional):** PASS. Both tool names produce equivalent AgentExecution shape + output + latency.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Alias sibling: `security_agent` (Batch 1) — same class target; semantic-mismatch finding lives there.
- Substrate ledger row: `6981cd08-30bc-4ed9-8f02-29d1f6086deb` (workspace `b4503364-2573-4401-9e28-61a739e0ce50`).
- Batch 2 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_2_close_artifact.md`.
