# `campaign_orchestrator_agent` — Validation Report (S3045 Batch 4)

**Tool:** `campaign_orchestrator_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="CampaignOrchestratorAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `campaign_orchestrator_agent` → `CampaignOrchestratorAgent` (`core/services/td_handlers_agents.py:120`)
**AGENT_MAP entry:** `CampaignOrchestratorAgent` present in `core/agent_router.py:440`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4)
**Ship shape:** Doc + live-dispatch smoke with **fanout-guard tightened smoke prompt**
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Campaign orchestrator — converts a client brief into complete ready-to-run marketing campaign package covering research, strategy, creation, and final packaging. Coordinates specialized agents/tools; tracks progress by phase; enforces consistency/quality; ships structured deliverables. Rigby routes here for end-to-end campaign creation.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="CampaignOrchestratorAgent")`.
- **Expected inputs:** free-form `task` text (brief).
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 4 live dispatch

**Dispatch:** `task_id=c720835f-d974-4596-9dac-9ec4f4cc0328` · `execution_id=31cdd38d-f9e8-43c5-8e01-dc00a0ba02e9` · terminal `completed` in 7,845ms.

**Output preview:** `- **Define scope (role → output):** State that CampaignOrchestratorAgent converts a client brief into a complete, ready-to-run marketing campaign package... CampaignOrchestratorAgent is the master coordinator that turns a client brie[f]...`

**5-criteria PASS:** all met. **PASS.**

**Fanout-guard verdict:** **HELD.** Single execution_id; no delegation; no file writes; no Data Sources block.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (`agent_router.py:440`).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:120`).
- **4.3 Envelope shape:** PASS.
- **4.4 Fanout-guard behavior:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
