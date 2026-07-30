# `prediction_market_analyst` — Validation Report (S3045 Batch 3)

**Tool:** `prediction_market_analyst`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="PredictionMarketAnalyst")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `prediction_market_analyst` → `PredictionMarketAnalyst` (`core/services/td_handlers_agents.py:140`)
**AGENT_MAP entry:** `PredictionMarketAnalyst` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 3)
**Ship shape:** Doc + live-dispatch smoke (RaaS bar per S3045 D-verdict — Option D)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 3 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Kalshi prediction-market analyst — identifies mispricings, momentum, and arbitrage across Kalshi prediction markets. Combines market prices, volume/liquidity signals, event fundamentals, and category-specific expertise (economics, politics, tech, finance, weather). Rigby routes here for prediction-market opportunity analysis. Distinct from `game_predictor` / `line_movement_analyzer` / `sharp_action_detector` (those are sports-odds-dependent; this is Kalshi/prediction-market).

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="PredictionMarketAnalyst")`.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 3 live dispatch

**Dispatch:** `task_id=b67d4598-31a3-4a95-a7c4-c138264e5198` · `execution_id=a3633afd-fcbc-4d99-b653-a5c982bd725b` · terminal `completed` in 22,662ms.

**Output preview:** `RaaS validation smoke — 3‑bullet plan\n- Draft: Read the prompt and constraints, then write a single, clear paragraph... Result paragraph: I analyze Kalshi prediction markets to identify mispricings, momentum, and arbitrage by combining market prices, volume/liquidity signals...`

**5-criteria PASS:** all met. **PASS.** Output followed 3-bullet plan + result-paragraph shape exactly as requested. No workspace side-effects.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:140`).
- **4.3 Envelope shape:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Sibling betting-family agents (Batch 3, Odds-API-blocked): `game_predictor`, `line_movement_analyzer`, `sharp_action_detector`. Kalshi-based (this tool) is NOT Odds-API-dependent — operational.
- Batch 3 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_3_close_artifact.md`.
