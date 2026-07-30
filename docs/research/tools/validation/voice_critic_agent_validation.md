# `voice_critic_agent` — Validation Report (S3045 Batch 2)

**Tool:** `voice_critic_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="VoiceCriticAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `voice_critic_agent` → `VoiceCriticAgent` (`core/services/td_handlers_agents.py:153`)
**AGENT_MAP entry:** `VoiceCriticAgent` present in `core/agent_router.py:423`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 2)
**Ship shape:** Doc + live-dispatch smoke — **RaaS-dispatch PASS + task-level smoke FAIL** (2nd input-contract class instance after `code_review_agent` in Batch 1)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 2 T0 SIGN follows. Rigby T1 pre-batch prediction ("VoiceCritic/PerformanceAnalyst needing `content=` blobs") confirmed for VoiceCritic; NOT confirmed for PerformanceAnalyst (permissive input schema).
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Voice/tone critic — scores content against voice guidelines, surfaces tone inconsistencies, flags deviation from brand voice. Rigby routes here for pre-publish voice-consistency checks.

**Input contract:** VoiceCriticAgent **requires** `content=` payload key (content to score); it cannot operate on free-form `task` text alone. Absent `content`, agent returns structured `error_message='No content provided to score'` in 612ms — actionable, structured, no crash. Same shape as `code_review_agent` input-contract failure (task-level smoke FAIL / RaaS-dispatch PASS).

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="VoiceCriticAgent")`.
- **Expected inputs:** `content` payload key MUST be populated with the content to score. Optional `context` keys.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Failure envelope:** `{status='failed', error_message='No content provided to score', output_preview='No content provided to score'}` — structured, actionable.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 2 live dispatch

**Dispatch:** `task_id=e9bc113d-0d85-4afd-bbc5-aff603a124f6` · `execution_id=ff35b867-c485-48cc-8ef6-9a37e6496556` · terminal **`failed`** in 612ms.

**Error:** `No content provided to score`. **Output preview:** `No content provided to score`.

**Verdict: RaaS-dispatch PASS; task-level smoke FAIL (input-contract).** Wiring / mapping / envelope shape / dispatch path all validated (RaaS bar met). Agent-level input-contract enforcement fired correctly on the task itself — the *smoke prompt* was invalid for this specific agent (no `content=` key), not the *tool*. Does NOT block CLOSE.

**Tailored smoke prompt for future re-validation:** dispatch with `context={'content': '<sample paragraph to score>'}` in addition to task text.

**2nd class instance:** input-contract failure taxonomy first surfaced at Batch 1 (`code_review_agent`). Confirmed with 2nd instance here (`voice_critic_agent`). Class definition holds: mapping/envelope/dispatch healthy but uniform smoke prompt insufficient. See Batch 1 close artifact §3 for full taxonomy definition.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (`agent_router.py:423`).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:153`).
- **4.3 Envelope shape (including failure envelope):** PASS. Failure envelope is structured with typed `error_message` — no crash.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Class sibling (also input-contract): `code_review_agent` (Batch 1).
- Autonomous content studio family: `topic_miner_agent`, `contrarian_agent`, `performance_analyst_agent`.
- Batch 2 close artifact: `docs/audits/pa_tools/substrate/S3045_batch_2_close_artifact.md`.
