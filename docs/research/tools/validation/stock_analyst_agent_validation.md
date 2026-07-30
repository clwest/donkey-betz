# `stock_analyst_agent` — Validation Report (S3045 Batch 3)

**Tool:** `stock_analyst_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="StockAnalystAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `stock_analyst_agent` → `StockAnalystAgent` (`core/services/td_handlers_agents.py:135`)
**AGENT_MAP entry:** `StockAnalystAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 3: stock/betting/blockchain family)
**Ship shape:** Doc + live-dispatch smoke (RaaS bar per S3045 D-verdict — Option D)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 3 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Stock analyst — pulls role charter + recent deliverables + SEC filings + sample analyses; produces role-shaped report with explicit provenance (Data Window / Sources / Publishable flag / Blockers). Rigby routes here for stock-analysis briefs with audit trail. Same provenance-header contract as `market_intelligence_agent` (Batch 1) and `trend_analysis_agent` (Batch 1).

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="StockAnalystAgent")`.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Provenance header contract:** `## Report Provenance` block with Data Sources + Publishable flag + explicit Blockers when data missing.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 3 live dispatch

**Dispatch:** `task_id=9f679e3a-c818-4142-92e3-e75a9f89b5ad` · `execution_id=ee4c0712-132f-4e44-826f-d8b61b2fd9d3` · terminal `completed` in 24,224ms.

**Output preview:** `## Report Provenance ... Data Sources: No data sources tracked. Total Records: 0. Publishable: No. Blockers: No data source provenance / No data records to analyze`

**5-criteria PASS:** all met. **PASS-with-finding** — agent honestly reported empty state via provenance block + Blockers list rather than fabricating output. Same honest-empty pattern as `market_intelligence_agent` (Batch 1).

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:135`).
- **4.3 Envelope shape + provenance header:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Sibling with same provenance-header contract: `market_intelligence_agent`, `trend_analysis_agent`, `bear_case_agent` (all Batch 3 or Batch 1).
- Batch 3 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_3_close_artifact.md`.
