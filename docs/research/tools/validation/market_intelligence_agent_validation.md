# `market_intelligence_agent` — Validation Report (S3045 Batch 1)

**Tool:** `market_intelligence_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="MarketIntelligenceAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Register site:** `core/services/tool_dispatcher.py`
**Mapping (`_tool_to_agent_name`):** `market_intelligence_agent` → `MarketIntelligenceAgent` (`core/services/td_handlers_agents.py:138`)
**AGENT_MAP entry:** `MarketIntelligenceAgent` present in `core/agent_router.py` `AGENT_MAP`.
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

Market intelligence report generator — produces provenance-headed reports on market state, competitive intel, SEC filings context. Includes freshness guard (24h) and explicit "Publishable" flag with blockers when data is missing. Rigby routes here for market-context research with audit trail.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="MarketIntelligenceAgent")` — LLM meta-tool dispatch through `_handle_universal_agent`.
- **Expected inputs:** free-form `task` text; optional `context` with `focus_areas` / `keywords`.
- **Dispatch queue:** `long_running` (Celery async).
- **Envelope shape:** `{task_id, mode='async', agent='MarketIntelligenceAgent', ...}` — per `_handle_universal_agent`.
- **Provenance header contract:** same shape as `trend_analysis_agent` — `## Report Provenance` block with data-source records + freshness + publishable flag + blockers.

## Covered actions

This tool has no schema action-enum decomposition — it dispatches the agent as a single unit via `run_agent(agent_name='MarketIntelligenceAgent')`. Coverage is unit-level.

## 3. Evidence — S3045 Batch 1 live dispatch

**PASS criteria (per S3045 D-verdict):** 1) no substitution 2) AgentExecution row 3) class match 4) terminal completed 5) output non-empty.

**Batch 1 dispatch record:**
- `task_id`: `902a80e5-cd18-4f55-bc72-b8bacae547d5`
- `execution_id`: `2b2dae2c-3c21-48b1-b6d3-52ffde853949`
- Terminal status: `completed` in 22,725ms
- `output_preview` (first 150 chars): `---\n## Report Provenance\n\n**Generated:** 2026-07-30 11:44:19 (UTC: 2026-07-30 17:44:19 UTC)\n**Agent:** MarketIntelligenceAgent v1.0\n**Data Window:** ...`
- All 5 PASS criteria: **PASS**.

**Smoke prompt used:** RaaS validation smoke with no-publish / no-post / no-media guard.

**Observation:** agent honestly reported `Publishable: ❌ No / Blockers: No data records to analyze` — smoke prompt didn't provide market data, agent flagged the gap rather than fabricating a report. Correct honest behavior; smoke PASS on wiring + envelope + agent decisiveness.

## 4. Contract ↔ Implementation Consistency

### 4.1 AGENT_MAP entry

**PASS.** `AgentRouter.AGENT_MAP` contains `MarketIntelligenceAgent`.

### 4.2 Mapping resolution

**PASS.** `_tool_to_agent_name('market_intelligence_agent')` returns `MarketIntelligenceAgent` per `td_handlers_agents.py:138`.

### 4.3 Envelope shape + provenance header

**PASS.** Live dispatch envelope matches `_handle_universal_agent` contract. Output includes standard provenance header + blockers path.

## Related

- **Shared handler:** `_handle_universal_agent` at `core/services/td_handlers_agents.py:1924`.
- **Shared mapping:** `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83-163`.
- **Category promotion:** `pa_tools_gap_map.classify_tool` at `core/services/pa_tools_gap_map.py:527-547` (S3045 substrate branch).
- **Sibling agent:** `market_intelligence_coordinator` (fanout-risk group; separate ship).
- **S3045 Batch 1 close artifact:** `docs/audits/pa_tools/substrate/S3045_batch_1_close_artifact.md`.
