# `video_generation_agent` — Validation Report (S3045 Batch 4, doc-only skiplist)

**Tool:** `video_generation_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="VideoAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `video_generation_agent` → `VideoAgent` (`core/services/td_handlers_agents.py:89`)
**AGENT_MAP entry:** `VideoAgent` present in `core/agent_router.py` `AGENT_MAP`.
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

Video generation agent — produces videos via external video-generation model API (long-running + LLM/media cost). Rigby routes here for on-demand short-form video creation.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="VideoAgent")`.
- **Expected inputs:** prompt + video parameters.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Cost signature:** external API call + potentially minutes-long generation.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Skiplist rationale

Per D-verdict infra-heavy skiplist policy: skiplisted from live dispatch because:
- Video generation via external API is expensive (per-render cost).
- Runtime is long (minutes) which serializes the `long_running` Celery worker for other Batch 4 tools.
- Smoke-shape prompt would either (a) generate a real video (wasteful) or (b) trigger input-contract failure (agent needs actual prompt, not a role-summary smoke).

**Mitigation:** doc-only validation. Wiring/mapping/envelope validated by inspection + shared-handler contract already confirmed via 30 other live dispatches this session.

**Re-validation trigger:** dedicated media-batch with tailored smoke prompts + cost-budget allocation.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (inspection).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:89`).
- **4.3 Envelope shape:** PASS by inspection.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Skiplist siblings: `resolve_agent`, `audio_generation_agent`, `image_generation_agent`, `talking_character_agent`.
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
