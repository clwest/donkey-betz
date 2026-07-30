# `platform_audit_agent` — Validation Report (S3045 Batch 2)

**Tool:** `platform_audit_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="PlatformAuditAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `platform_audit_agent` → `PlatformAuditAgent` (`core/services/td_handlers_agents.py:100`)
**AGENT_MAP entry:** `PlatformAuditAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 2)
**Ship shape:** Doc + live-dispatch smoke (RaaS bar per S3045 D-verdict — Option D)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 2 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Internal platform auditor — reviews documentation / environment config / integrations & key status / database model counts to spot anomalies. Privacy/security-aware (masks secrets). Outputs actionable findings, often as structured JSON reports. Rigby routes here for internal platform-state audits. Distinct from the Employee OS Platform Auditor mission (`core/employees/jobs.py` — MissionRunner-orchestrated); the agent here is the AGENT_MAP entry usable via direct dispatch.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="PlatformAuditAgent")`.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Constraint:** no external web research; internal tools only.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 2 live dispatch

**Dispatch:** `task_id=83fcbb56-1dab-4617-8a26-71d16319346e` · `execution_id=29649b19-56e6-40ae-ad75-84520551531a` · terminal `completed` in 6,305ms.

**Output preview:** `- Identify the core scope: internal platform auditing of components/config/integrations; no external web research; use provided internal tools only when needed... I am PlatformAuditAgent, responsible for auditing internal platform components...`

**5-criteria PASS:** all met. **PASS.**

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:100`).
- **4.3 Envelope shape:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Employee OS sibling: PlatformAuditor mission via MissionRunner (`core/employees/jobs.py`) — separate orchestration surface with the same underlying agent class.
- Batch 2 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_2_close_artifact.md`.
