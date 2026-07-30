# `stock_audit_coordinator` — Validation Report (S3045 Batch 3)

**Tool:** `stock_audit_coordinator`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="StockAuditCoordinator")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `stock_audit_coordinator` → `StockAuditCoordinator` (`core/services/td_handlers_agents.py:134`)
**AGENT_MAP entry:** `StockAuditCoordinator` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 3)
**Ship shape:** Doc + live-dispatch smoke with **fanout-guard smoke prompt** — fanout-guard FAILED (cross-agent aggregation observed in output)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 3 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** unsafe_workspace_write_side_effect

---

## 1. Purpose / when-to-use

Stock audit coordinator — orchestrates stock-analysis audit across multiple downstream agents (StockAnalystAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, MarketAnomalyDetectorAgent). Aggregates their outputs into unified audit report with alert count + provenance. **Fanout-risk class** — smoke observed cross-agent data-source aggregation.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="StockAuditCoordinator")`.
- **Expected inputs:** free-form `task` text; coordinator queries downstream agents inline.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Fanout-guard smoke prompt used:** SINGLE STEP ONLY (see Batch 2 close artifact for full text).
- **Side-effect note:** wrote 1 file to workspace during Batch 3 smoke.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 3 live dispatch

**Dispatch:** `task_id=703953eb-5109-46aa-9104-7a0d03b78f21` · `execution_id=924b5ef5-e3de-47a9-8b5d-6d8e7f6ae682` · terminal `completed` in 145,136ms (~2.4min).

**Output preview:** `## Report Provenance ... Data Sources: StockAnalystAgent (1 record), MarketMovementMonitorAgent (1 record), InstitutionalWatcherAgent (1 record), MarketAnomalyDetectorAgent (1 record). Total: 4. Publishable: Yes. Stock audit complete. 0 alerts generated. 📁 Wrote 1 file to workspace 'Donkey Betz'.`

**5-criteria PASS:** all met. **PASS-with-finding.**

**Fanout-guard verdict: NOT CLEAN.** Output explicitly lists 4 downstream agents as Data Sources (StockAnalystAgent + MarketMovementMonitorAgent + InstitutionalWatcherAgent + MarketAnomalyDetectorAgent). Whether this is TRUE cross-agent dispatch (spawned child AgentExecutions) or CACHED aggregation (reading prior downstream agent outputs from a data store) is not verifiable from the poll surface (no child-task trace surface currently). Rigby T0 SIGN Q4 conservative language: **"cross-agent aggregation observed in output; single execution_id but Data Sources list is sufficient evidence of coordination scope beyond single-step."**

**Comparison to blockchain_audit_coordinator (Batch 3 clean):** blockchain_audit_coordinator produced smoke-shape output without Data Sources block or downstream agent references — genuine single-step behavior. Stock/market coordinator family exhibits different pattern (provenance-header-with-Data-Sources shape).

**Side-effect finding:** wrote workspace file — same class as `bear_case_agent` (Batch 3) and `market_intelligence_coordinator` (Batch 3).

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:134`).
- **4.3 Envelope shape:** PASS.
- **4.4 Fanout-guard behavior:** **FAIL** (cross-agent aggregation evidence in output).

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Fanout-guard class siblings (Batch 3): `market_intelligence_coordinator` (also FAIL), `blockchain_audit_coordinator` (PASS).
- Coordinator-provenance-fanout finding class: see Batch 3 close artifact §Findings.
- Batch 3 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_3_close_artifact.md`.
