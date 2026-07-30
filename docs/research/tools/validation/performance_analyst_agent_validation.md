# `performance_analyst_agent` — Validation Report (S3045 Batch 2)

**Tool:** `performance_analyst_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="PerformanceAnalystAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `performance_analyst_agent` → `PerformanceAnalystAgent` (`core/services/td_handlers_agents.py:152`)
**AGENT_MAP entry:** `PerformanceAnalystAgent` present in `core/agent_router.py:420`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 2)
**Ship shape:** Doc + live-dispatch smoke (RaaS bar per S3045 D-verdict — Option D)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 2 T0 SIGN follows. Rigby T1 pre-batch prediction ("might need `content=`") did NOT surface — permissive input schema.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Performance analyst — pulls historical channel/podcast performance data, extracts repeatable success patterns, converts into decisions (produce/stop/test recommendations). Evidence-based with explicit blockers ("BLOCKED ON: missing X"). Rigby routes here for content-performance retrospective analysis.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="PerformanceAnalystAgent")`.
- **Expected inputs:** free-form `task` text; agent pulls performance data inline. **Not** `content=`-dependent (unlike sibling `voice_critic_agent`).
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 2 live dispatch

**Dispatch:** `task_id=d110ff60-4ec3-4c9c-bb4a-6bf8972474eb` · `execution_id=47a93feb-92de-4bc6-955b-030a296c1802` · terminal `completed` in 8,278ms.

**Output preview:** `- Identify the core scope of the role (Performance Analyst Agent)... Result paragraph: I am the Performance Analyst Agent: I pull real channel/podcast performance da...`

**5-criteria PASS:** all met. **PASS.**

**Rigby T1 prediction outcome:** predicted `content=` blob might be required (mirroring VoiceCritic input contract) — NOT confirmed. PerformanceAnalyst has a more permissive input schema; free-form task text sufficient.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (`agent_router.py:420`).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:152`).
- **4.3 Envelope shape:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Class sibling (input-contract FAIL): `voice_critic_agent` (Batch 2).
- Autonomous content studio family: `topic_miner_agent`, `contrarian_agent`, `voice_critic_agent`.
- Batch 2 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_2_close_artifact.md`.
