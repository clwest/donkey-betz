# `bear_case_agent` — Validation Report (S3045 Batch 3)

**Tool:** `bear_case_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="BearCaseAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `bear_case_agent` → `BearCaseAgent` (`core/services/td_handlers_agents.py:136`)
**AGENT_MAP entry:** `BearCaseAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 3)
**Ship shape:** Doc + live-dispatch smoke (RaaS bar per S3045 D-verdict — Option D)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 3 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** unsafe_workspace_write_side_effect

---

## 1. Purpose / when-to-use

Bearish stock case analyst — pulls MarketDataService records, analyzes for bear-case indicators, tags HIGH/MEDIUM/LOW risk per stock, produces provenance-headed report. Rigby routes here for downside/risk exposure analysis on stock portfolios.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="BearCaseAgent")`.
- **Expected inputs:** free-form `task` text; agent pulls MarketDataService inline.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Provenance header contract:** same as stock/market family.
- **Side-effect note (workspace write):** agent wrote 1 file to workspace 'Donkey Betz' during Batch 3 smoke — see §3 finding.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 3 live dispatch

**Dispatch:** `task_id=559fd396-5085-409d-9fb1-fd3a9ffe6b2e` · `execution_id=cac90616-43b6-42cc-beef-55958ea1ad7b` · terminal `completed` in 172,004ms (~2.9min).

**Output preview:** `## Report Provenance ... Data Sources: MarketDataService: 7 records ... Publishable: Yes. Analyzed 7 stocks. HIGH risk: 2, MEDIUM: 2, LOW: 3. Top risks: GOOGL, TSLA. 📁 Wrote 1 files to workspace 'Donkey Betz'`

**5-criteria PASS:** all met. **PASS-with-finding.**

**Finding — workspace side-effect:** agent wrote 1 file to workspace 'Donkey Betz' despite smoke prompt's "Do NOT publish, do NOT post to any external service, do NOT create media." The smoke prompt's guardrails were interpreted narrowly (publish/post/media) and did NOT block workspace file writes. Per Batch 3 close artifact §Findings: this is a **workspace-write side-effect class** (3 concrete instances in Batch 3: `bear_case_agent`, `stock_audit_coordinator`, `market_intelligence_coordinator`). Future smoke prompts should add explicit "Do NOT write any files to any workspace" clause. Ledger row candidate — see Batch 3 close artifact §Findings.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:136`).
- **4.3 Envelope shape:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Sibling stock/analysis agents with provenance-header contract: `stock_analyst_agent`, `market_intelligence_agent`.
- Batch 3 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_3_close_artifact.md`.
