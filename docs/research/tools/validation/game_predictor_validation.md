# `game_predictor` — Validation Report (S3045 Batch 3)

**Tool:** `game_predictor`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="GamePredictor")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `game_predictor` → `GamePredictor` (`core/services/td_handlers_agents.py:141`)
**AGENT_MAP entry:** `GamePredictor` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 3)
**Ship shape:** Doc + live-dispatch smoke — **Runtime-failure PASS-with-mitigation** (Odds API absent; Chris directive: back burner until API key restored)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 3 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Sports game outcome predictor — pulls odds data via TheOddsSpider, produces game-outcome predictions with confidence scoring. **Odds-API-dependent** — currently blocked by missing API key (Chris directive 2026-07-30: Odds-dependent work on back burner). Rigby routes here when odds infra is operational; currently returns structured "no odds" failure envelope.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="GamePredictor")`.
- **Expected inputs:** free-form `task` text; agent pulls TheOddsSpider inline.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Infra dependency:** TheOddsSpider (currently no Odds API key; S3040 periodic tasks disabled).

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 3 live dispatch

**Dispatch:** `task_id=fe7ef69a-1e97-4b1b-aa94-332f0434c1a3` · `execution_id=7342f5cf-9a06-4b34-b903-ed2d53784876` · terminal **`failed`** in 985ms.

**Error:** `TheOddsSpider returned no events`. **Output preview:** `No odds data available for predictions`

**Verdict: Runtime-failure PASS-with-mitigation.** Wiring / mapping / envelope shape / dispatch path all validated (RaaS bar met). Agent-level runtime dependency (TheOddsSpider) unavailable due to known S3040 infra state — no Odds API key. Failure envelope is structured, actionable, no crash. Per S3045 D-verdict conditional-skip disposition for known infra absence: **does NOT block CLOSE**.

**Root cause (per Chris directive 2026-07-30):** Odds API on back burner; no active API key. See substrate ledger row `[S3045] Infra-runtime failure class — upstream odds feed empty (TheOddsSpider)` (deliverable `e2d0c1a1-e75d-495c-b518-78360256264f`, workspace `b4503364-2573-4401-9e28-61a739e0ce50`).

**Re-validation trigger:** when Odds API key restored + TheOddsSpider periodic tasks re-enabled, re-dispatch this tool to confirm operational path.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:141`).
- **4.3 Envelope shape (including failure envelope):** PASS. Structured with typed `error_message`; no crash.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Infra-runtime failure class ledger row: `e2d0c1a1-e75d-495c-b518-78360256264f`.
- Sibling Odds-dependent tools (all Batch 3, all runtime-failure): `line_movement_analyzer`, `sharp_action_detector`.
- Non-Odds-dependent betting sibling: `prediction_market_analyst` (Kalshi-based, PASS).
- Batch 3 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_3_close_artifact.md`.
