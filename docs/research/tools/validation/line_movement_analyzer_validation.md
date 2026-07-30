# `line_movement_analyzer` — Validation Report (S3045 Batch 3)

**Tool:** `line_movement_analyzer`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="LineMovementAnalyzer")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `line_movement_analyzer` → `LineMovementAnalyzer` (`core/services/td_handlers_agents.py:142`)
**AGENT_MAP entry:** `LineMovementAnalyzer` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 3)
**Ship shape:** Doc + live-dispatch smoke — **Runtime-failure PASS-with-mitigation** (Odds API absent; Chris directive: back burner)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 3 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Line movement analyst — tracks betting line movement across bookmakers to detect steam moves, reverse line movement, and sharp money signals. **Odds-API-dependent** — currently blocked by missing API key.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="LineMovementAnalyzer")`.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Infra dependency:** TheOddsSpider (currently no API key).

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 3 live dispatch

**Dispatch:** `task_id=f4a45419-ae16-437d-8943-7e52497b2fc3` · `execution_id=bd3cad51-debe-4120-9102-a457bdf11522` · terminal **`failed`** in 1,297ms.

**Error:** `TheOddsSpider returned no events`. **Output preview:** `No current odds data available`

**Verdict: Runtime-failure PASS-with-mitigation.** RaaS wiring/dispatch validated; agent-level runtime infra unavailable. See sibling `game_predictor` validation doc §3 for full class framing. Substrate ledger row: `e2d0c1a1-e75d-495c-b518-78360256264f`.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:142`).
- **4.3 Envelope shape:** PASS. Structured failure envelope.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Class siblings (Odds-API-blocked): `game_predictor`, `sharp_action_detector`.
- Non-Odds-dependent sibling: `prediction_market_analyst` (Kalshi).
- Batch 3 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_3_close_artifact.md`.
