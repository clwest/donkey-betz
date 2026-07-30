# `opportunity_pipeline_agent` — Validation Report (S3045 Batch 4)

**Tool:** `opportunity_pipeline_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="OpportunityPipelineAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `opportunity_pipeline_agent` → `OpportunityPipelineAgent` (`core/services/td_handlers_agents.py:121`)
**AGENT_MAP entry:** `OpportunityPipelineAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4)
**Ship shape:** Doc + live-dispatch smoke — **RaaS-dispatch PASS + task-level smoke FAIL** (3rd input-contract class instance)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Opportunity pipeline processor — takes an `opportunity` data dict and processes it through the pipeline stages (score → route → execute). Rigby routes here when there's a specific opportunity object to advance through the pipeline.

**Input contract:** OpportunityPipelineAgent **requires** `context['opportunity']` payload key with an opportunity data dict. Absent, agent returns structured `error_message='No opportunity provided in context. Expected opportunity data dict.'` — no crash. **3rd instance of the input-contract failure class** (after `code_review_agent` in Batch 1 + `voice_critic_agent` in Batch 2). **Trigger threshold reached** per S3045 input-contract ledger row (`0988dcc4-d7dc-4015-84e0-b77a86df0aa7`) — opens Option B (per-tool tailored smoke prompt harness) for future re-validation.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="OpportunityPipelineAgent")`.
- **Expected inputs:** `task` text + **`context['opportunity']`** payload key with opportunity data dict.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Failure envelope:** `{status='failed', error_message='No opportunity provided in context. Expected opportunity data dict.', output_preview='No opportunity provided in context.'}` — structured, actionable, no crash.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 4 live dispatch

**Dispatch:** `task_id=7626db02-c117-4a08-97f5-4a781aa43b3c` · `execution_id=d8bb8094-c07b-4c9b-bde5-eaf5ad9e9d8a` · terminal **`failed`** in 982ms.

**Error:** `No 'opportunity' provided in context. Expected opportunity data dict.`

**Verdict: RaaS-dispatch PASS; task-level smoke FAIL (input-contract).** RaaS bar met (mapping + envelope + dispatch validated). Uniform smoke prompt lacks the required `context['opportunity']` key. Does NOT block CLOSE. Same class as `code_review_agent` + `voice_critic_agent`.

**Tailored smoke prompt for future re-validation:** dispatch with `context={'opportunity': {'id': 'test-1', 'source': 'smoke', 'signal_type': 'test', ...}}` in addition to task text.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:121`).
- **4.3 Envelope shape (including failure envelope):** PASS. Structured with typed `error_message`; no crash.

## 5. Input-contract class — 3rd instance / Option B trigger

Per S3045 ledger row `0988dcc4-d7dc-4015-84e0-b77a86df0aa7` mitigation options: **"3rd instance opens Option B implementation"** (per-tool tailored smoke prompt harness). Trigger threshold **REACHED**. Ledger update candidate (deferred to post-merge Rigby task): mark Option B as trigger-ready + note the 3 concrete instances (code_review_agent · voice_critic_agent · opportunity_pipeline_agent).

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Class siblings (input-contract): `code_review_agent` (Batch 1), `voice_critic_agent` (Batch 2). This is 3rd instance.
- Input-contract ledger row: `0988dcc4-d7dc-4015-84e0-b77a86df0aa7`.
- Related sibling: `opportunity_scoring_agent` (Batch 4 PASS — has more permissive input schema).
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
