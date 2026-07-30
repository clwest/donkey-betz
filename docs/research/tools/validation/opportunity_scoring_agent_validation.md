# `opportunity_scoring_agent` — Validation Report (S3045 Batch 4)

**Tool:** `opportunity_scoring_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="OpportunityScoringAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `opportunity_scoring_agent` → `OpportunityScoringAgent` (`core/services/td_handlers_agents.py:99`)
**AGENT_MAP entry:** `OpportunityScoringAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4)
**Ship shape:** Doc + live-dispatch smoke (standard tightened smoke prompt)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Opportunity Engine — converts raw spider/network signals into scored, monetizable opportunities. Factor scoring: profit potential (1-100) · competition level · effort required · time sensitivity. Produces recommended content types, revenue/effort estimates, explicit blockers/limitations. Rigby routes here for opportunity scoring at the front of the pipeline.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="OpportunityScoringAgent")`.
- **Expected inputs:** free-form `task` text (more permissive than sibling `opportunity_pipeline_agent`).
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 4 live dispatch

**Dispatch:** `task_id=855a1812-b62f-4550-9e49-74518929e1cb` · `execution_id=1a81f4ae-eff4-40b7-be66-8f3ebd669914` · terminal `completed` in 7,209ms.

**Output preview:** `- Define the role in one sentence (identity + mission): "OpportunityScoringAgent = the Opportunity Engine that turns raw spider/network signals into scored, monetizable opportunities."... I am OpportunityScoringAgent, the Opportunity Engine...`

**5-criteria PASS:** all met. **PASS.**

**Sibling contrast:** `opportunity_pipeline_agent` (Batch 4) has strict `context['opportunity']` input contract and FAILED smoke; this sibling has more permissive input schema and passed. Different tools, different contracts.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:99`).
- **4.3 Envelope shape:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Sibling with stricter input contract: `opportunity_pipeline_agent` (Batch 4 input-contract FAIL).
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
