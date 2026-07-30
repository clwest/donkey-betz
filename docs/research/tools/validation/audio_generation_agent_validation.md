# `audio_generation_agent` — Validation Report (S3045 Batch 4, doc-only skiplist)

**Tool:** `audio_generation_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="AudioAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `audio_generation_agent` → `AudioAgent` (`core/services/td_handlers_agents.py:92`)
**AGENT_MAP entry:** `AudioAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4 skiplist)
**Ship shape:** **Doc-only + mitigation note** — skiplisted per S3045 D-verdict (long-running + expensive)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** analyzed
**Mutation safety:** external_side_effect_deferred

---

## 1. Purpose / when-to-use

Audio generation agent — produces audio (TTS / music / sound) via external audio-generation model API. Rigby routes here for on-demand audio creation (podcast episodes, voiceovers, sound effects).

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="AudioAgent")`.
- **Expected inputs:** prompt + audio parameters (voice, style, duration).
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Cost signature:** external API call + audio-file output.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Skiplist rationale

Same as sibling media-generation tools — external API cost + long runtime + smoke-shape prompt would waste an audio generation. Doc-only validation; dedicated media-batch handles live re-validation.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (inspection).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:92`).
- **4.3 Envelope shape:** PASS by inspection.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Skiplist siblings: `resolve_agent`, `video_generation_agent`, `image_generation_agent`, `talking_character_agent`.
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
