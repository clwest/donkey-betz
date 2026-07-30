# `sharp_action_detector` — Validation Report (S3045 Batch 3)

**Tool:** `sharp_action_detector`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="SharpActionDetector")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `sharp_action_detector` → `SharpActionDetector` (`core/services/td_handlers_agents.py:143`)
**AGENT_MAP entry:** `SharpActionDetector` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 3)
**Ship shape:** Doc + live-dispatch smoke — **Runtime-failure PASS-with-mitigation** (Odds API absent; requires per-bookmaker odds data)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 3 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Sharp action detector — identifies "sharp money" signals by comparing odds across multiple bookmakers. **Odds-API-dependent** with an additional requirement: needs **per-bookmaker** odds (not just single-source). Currently blocked by missing Odds API key.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="SharpActionDetector")`.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Infra dependency:** TheOddsSpider + multi-bookmaker coverage (currently no API key).

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 3 live dispatch

**Dispatch:** `task_id=86a35c79-4c08-44d0-a24e-03c5159de1c7` · `execution_id=b3437450-4cb4-42cc-af5e-2ef5179f6914` · terminal **`failed`** in 1,024ms.

**Error:** `No events with per-bookmaker odds`. **Output preview:** `No multi-bookmaker odds data available`

**Verdict: Runtime-failure PASS-with-mitigation.** RaaS wiring/dispatch validated; agent-level runtime infra unavailable. Distinct error signal (`per-bookmaker`) vs siblings (`no events`) — this tool requires broader spider coverage. See substrate ledger row `e2d0c1a1-e75d-495c-b518-78360256264f`.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:143`).
- **4.3 Envelope shape:** PASS. Structured failure envelope.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Class siblings (Odds-API-blocked): `game_predictor`, `line_movement_analyzer`.
- Batch 3 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_3_close_artifact.md`.
