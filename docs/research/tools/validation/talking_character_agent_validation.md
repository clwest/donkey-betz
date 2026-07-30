# `talking_character_agent` — Validation Report (S3045 Batch 4, doc-only skiplist)

**Tool:** `talking_character_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="TalkingCharacterAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `talking_character_agent` → `TalkingCharacterAgent` (`core/services/td_handlers_agents.py:95`)
**AGENT_MAP entry:** `TalkingCharacterAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4 skiplist)
**Ship shape:** **Doc-only + mitigation note** — skiplisted per S3045 D-verdict (multi-stage media pipeline)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** analyzed
**Mutation safety:** external_side_effect_deferred

---

## 1. Purpose / when-to-use

Talking-character video agent — produces videos of a character talking (voice + lip-sync + character rendering). Multi-stage pipeline (character trained via CharacterTrainingAgent → voice via AudioAgent → assembled via internal pipeline). Rigby routes here for character-anchored short-form video with dialogue.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="TalkingCharacterAgent")`.
- **Expected inputs:** character selection + script + voice parameters.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Cost signature:** multi-stage media generation (character render + voice synth + assembly).

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Skiplist rationale

Skiplisted per D-verdict. Cost: multi-stage media generation, brittle downstream dependencies. Smoke-shape prompt would waste a talking-character video generation. Doc-only validation; dedicated media-batch handles live re-validation.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (inspection).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:95`).
- **4.3 Envelope shape:** PASS by inspection.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Skiplist siblings: `resolve_agent`, `video_generation_agent`, `audio_generation_agent`, `image_generation_agent`.
- Related training siblings: `character_training_agent` (Slice 5 validated — LoRA training partner).
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
