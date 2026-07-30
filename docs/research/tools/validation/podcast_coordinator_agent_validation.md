# `podcast_coordinator_agent` — Validation Report (S3045 Batch 4)

**Tool:** `podcast_coordinator_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="PodcastCoordinatorAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `podcast_coordinator_agent` → `PodcastCoordinatorAgent` (`core/services/td_handlers_agents.py:156`)
**AGENT_MAP entry:** `PodcastCoordinatorAgent` present in `core/agent_router.py:431`.
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

Podcast coordinator — turns a topic into a balanced debate question, defines 2-3 perspectives, assigns standard roles/voices (Host/Advocate/Skeptic/Analyst), shapes into a structured podcast-ready script (intro/segments/outro) for downstream TTS. Rigby routes here to prepare podcast episode scripts.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="PodcastCoordinatorAgent")`.
- **Expected inputs:** free-form `task` text (topic).
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 4 live dispatch

**Dispatch:** `task_id=bce46970-870e-463e-94cd-f79551045e12` · `execution_id=9c95a8e3-449d-424f-aefd-d1d334961818` · terminal `completed` in 11,226ms.

**Output preview:** `- Clarify the deliverable and constraints: confirm it's a **single-paragraph** description of the **Podcast Coordinator Agent** role... I'm the Podcast Coordinator Agent...`

**5-criteria PASS:** all met. **PASS.**

**Fanout-guard verdict:** **HELD.** Clean single-step behavior; no delegation; no file writes; no Data Sources block.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (`agent_router.py:431`).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:156`).
- **4.3 Envelope shape:** PASS.
- **4.4 Fanout-guard behavior:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Fanout-guard class siblings (Batch 4): all 4 coordinators PASSED with tightened prompt.
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
