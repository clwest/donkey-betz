# `trained_creation_agent` — Validation Report (S3045 Batch 4)

**Tool:** `trained_creation_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="TrainedCreationAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `trained_creation_agent` → `TrainedCreationAgent` (`core/services/td_handlers_agents.py:158`)
**AGENT_MAP entry:** `TrainedCreationAgent` present in `core/agent_router.py` `AGENT_MAP`.
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

LoRA Generation Specialist — generates images using trained character/style LoRA models on FLUX. Does NOT train models (CharacterTrainingAgent handles training). Pipeline: (1) resolve model (name/trigger/ID) → (2) extract prompt + params → (3) generate → (4) return results. Rigby routes here for LoRA-based image gen with pre-trained character/style.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="TrainedCreationAgent")`.
- **Expected inputs:** `task` text + model resolution details (name/trigger/ID) + prompt + generation params. Under normal use, would generate images. Under smoke prompt (this batch), agent honored "return results only in chat" and did NOT generate/persist images.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 4 live dispatch

**Dispatch:** `task_id=c3afa8b1-f5ff-47b0-a178-a4006a7b1815` · `execution_id=c1adc6ff-67c9-4ef0-99f8-fef51a76c9b8` · terminal `completed` in 10,058ms.

**Output preview:** `- Define scope + constraints as FACTS: I am **TrainedCreationAgent (LoRA Generation Specialist)**... I avoid any external posting/persistence... BLOCKED ON: missing model ID/trigger or missing prompt/params. I am TrainedCreationAgent, the LoRA generation specialist: I produce images using trained char[acter]...`

**5-criteria PASS:** all met. **PASS.** Agent explicitly acknowledged the smoke-prompt "no external posting/persistence" constraint in its output. Named blockers (missing model ID/prompt) rather than fabricating results — good honest signal for image-gen-shape agent under smoke.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:158`).
- **4.3 Envelope shape:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Related media/training agents (Batch 4 skiplist, doc-only): `image_generation_agent`, `talking_character_agent`.
- Related training class (Slice 5 already validated): `character_training_agent` (LoRA training partner).
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
