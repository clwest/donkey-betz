# `contrarian_agent` — Validation Report (S3045 Batch 2)

**Tool:** `contrarian_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="ContrarianAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `contrarian_agent` → `ContrarianAgent` (`core/services/td_handlers_agents.py:151`)
**AGENT_MAP entry:** `ContrarianAgent` present in `core/agent_router.py:419`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 2)
**Ship shape:** Doc + live-dispatch smoke (RaaS bar per S3045 D-verdict — Option D)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 2 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Contrarian analyst in autonomous content pipeline — measures topic saturation via real-time spider/tool data, challenges copycat choices, proposes differentiated/debate-sparking angles. Rigby routes here for contrarian angle-of-attack passes on content ideation.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="ContrarianAgent")`.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 2 live dispatch

**Dispatch:** `task_id=c4add12f-6598-471e-b165-973c427c73a5` · `execution_id=ed7beb1a-4e11-4c5c-91cc-c0709756209d` · terminal `completed` in 7,921ms.

**Output preview:** `- Identify the role's core mandate in one sentence (what I optimize for, what I defend against), and enforce decisive phrasing... Result paragraph: I operate as the Contrarian Agent in an autonomous content pipeline...`

**5-criteria PASS:** all met. **PASS.** Output followed 3-bullet plan + result-paragraph shape as requested.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (`agent_router.py:419`).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:151`).
- **4.3 Envelope shape:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Autonomous content studio family siblings: `topic_miner_agent` (Batch 1 PASS), `performance_analyst_agent` (Batch 2), `voice_critic_agent` (Batch 2 input-contract FAIL).
- Batch 2 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_2_close_artifact.md`.
