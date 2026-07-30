# `system_intelligence_agent` — Validation Report (S3045 Batch 4)

**Tool:** `system_intelligence_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="SystemIntelligenceAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `system_intelligence_agent` → `SystemIntelligenceAgent` (`core/services/td_handlers_agents.py:132`)
**AGENT_MAP entry:** `SystemIntelligenceAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4)
**Ship shape:** Doc + live-dispatch smoke — **PASS-w/-finding (4th workspace-side-effect class instance — tightened smoke prompt INSUFFICIENT)**
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** unsafe_workspace_write_side_effect

---

## 1. Purpose / when-to-use

System Intelligence monitor — extracts 3-4 core functions from platform state: (1) monitor platform health across body systems, (2) aggregate + prioritize system attention items by severity, (3) explain metrics in plain English, (4) identify blockers + assign owners with directives. Rigby routes here for platform-health briefs backed by body-systems telemetry.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="SystemIntelligenceAgent")`.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Side-effect note (workspace persistence):** agent auto-creates a "System Intelligence Report" deliverable in the active workspace as part of its normal flow — persists regardless of smoke prompt clauses. See §3 finding.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 4 live dispatch

**Dispatch:** `task_id=b24d5658-f0c7-4c53-b4ba-e18d3d0826a0` · terminal `completed`.

**Output preview:** `- Identify scope and top responsibilities: extract the role's 3-4 core functions (monitor platform health, aggregate attention items, explain metrics in plain English, recommend actions and owners)... SystemIntelligenceAgent monitors platform health across the platform's body systems...`

**5-criteria PASS:** all met. **PASS-with-finding.**

**FINDING — 4th workspace-side-effect class instance. Tightened smoke prompt INSUFFICIENT.**

Agent created deliverable `a9468cf3-82f5-44d2-b64a-534c19ae1ee9` ("System Intelligence Report: RaaS validation smoke: return a 3-bullet plan for how you would approach the tas...") in workspace `b4503364-2573-4401-9e28-61a739e0ce50` at 18:59:25 UTC despite the tightened smoke prompt explicitly saying: **"Do NOT write, create, modify, or delete any files. Do NOT persist output anywhere (workspace, KB, deliverables, external stores). Return results ONLY in the chat response."**

**Class instances (4 total):** bear_case_agent (Batch 3) · stock_audit_coordinator (Batch 3) · market_intelligence_coordinator (Batch 3) · system_intelligence_agent (Batch 4, **created deliverable despite tightened prompt**).

**Escalation:** the workspace-side-effect class ledger row (`bacd97ee-23db-438f-8e72-1ccc166a186a`) should be updated to note tightened prompt Option A **INSUFFICIENT** at 4-instance ladder. Escalate to Option B (per-agent `smoke_mode=true` context flag) OR Option C (ephemeral smoke workspace routing). Ledger append candidate: mark Option A insufficient + concrete 4-instance evidence.

**Why the smoke prompt didn't hold:** SystemIntelligenceAgent's normal flow includes deliverable creation via `deliverable_tool` as an internal implementation step — it doesn't inspect smoke-prompt context to skip that. The prompt is instruction-level, but the agent's tool-use behavior is code-path-level. Instruction can't stop a code path it doesn't reach.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:132`).
- **4.3 Envelope shape:** PASS.
- **4.4 Smoke-prompt-guardrail compliance:** **FAIL** (workspace-side-effect class 4th instance).

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Workspace-side-effect class ledger row: `bacd97ee-23db-438f-8e72-1ccc166a186a`. Sibling instances: `bear_case_agent`, `stock_audit_coordinator`, `market_intelligence_coordinator` (all Batch 3).
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
