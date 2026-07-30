# `image_generation_agent` — Validation Report (S3045 Batch 4, doc-only skiplist)

**Tool:** `image_generation_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="ImageAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `image_generation_agent` → `ImageAgent` (`core/services/td_handlers_agents.py:87`)
**AGENT_MAP entry:** `ImageAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4 skiplist)
**Ship shape:** **Doc-only + mitigation note** — skiplisted per S3045 D-verdict (external API + cost)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** analyzed
**Mutation safety:** external_side_effect_deferred

---

## 1. Purpose / when-to-use

Image generation agent — produces images via external image-generation model API (FLUX or similar). Rigby routes here for on-demand image creation.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="ImageAgent")`.
- **Expected inputs:** prompt + image parameters (size, count, style).
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Cost signature:** external API call + image-file outputs.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Skiplist rationale

Same as sibling media-generation tools. Doc-only validation. `trained_creation_agent` (Batch 4 live-dispatch PASS) is the LoRA-based sibling that WAS live-dispatched — its behavior evidence transfers partially to `image_generation_agent` since both go through the same shared handler + envelope contract, though the underlying agent classes differ.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (inspection).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:87`).
- **4.3 Envelope shape:** PASS by inspection.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Skiplist siblings: `resolve_agent`, `video_generation_agent`, `audio_generation_agent`, `talking_character_agent`.
- Related live-dispatched sibling: `trained_creation_agent` (Batch 4, LoRA-based image gen — PASS).
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
