# `resolve_agent` — Validation Report (S3045 Batch 4, doc-only skiplist)

**Tool:** `resolve_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="ResolveAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `resolve_agent` → `ResolveAgent` (`core/services/td_handlers_agents.py:91`)
**AGENT_MAP entry:** `ResolveAgent` present in `core/agent_router.py:428`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4 skiplist)
**Ship shape:** **Doc-only + mitigation note** — skiplisted from live dispatch per S3045 D-verdict infra-heavy skiplist policy.
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** analyzed
**Mutation safety:** external_side_effect_deferred

---

## 1. Purpose / when-to-use

DaVinci Resolve automation agent — dispatches video edit/render operations to a locally-running Resolve node process. Rigby routes here for programmatic video-timeline manipulation via Resolve's scripting API.

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="ResolveAgent")`.
- **Expected inputs:** `task` text + Resolve-specific parameters (timeline path, edit operations).
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Infra dependency:** locally-running Resolve node process (see `resolve-node.py`). Not reliably available in every operator environment.

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Skiplist rationale (D-verdict mitigation)

Per S3045 D-verdict infra-heavy skiplist policy: this tool is skiplisted from live dispatch because Resolve node dependency is not reliably available in every operator environment. Dispatching would produce a runtime failure envelope ("Resolve node unavailable" or similar) even when the RaaS wiring is healthy — the failure would be about infra, not tool integrity.

**Mitigation:** doc-only validation with mitigation note. Wiring/mapping/envelope validated by inspection (AGENT_MAP entry + mapping row + shared handler contract confirmed). Live-dispatch re-validation deferred to a dedicated batch when Resolve node is reachable and operator confirms Resolve API contract stability.

**Re-validation trigger:** when a dedicated Resolve-live batch is opened + `resolve-node.py` process is confirmed running + operator has capacity to observe timeline mutations.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS (`agent_router.py:428`, inspection).
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:91`, inspection).
- **4.3 Envelope shape:** PASS by inspection (shared `_handle_universal_agent` contract per §4.3 of Slice 5 CLOSE artifact + Batch 1-3 live-dispatch confirmations of the shape).

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Infra-heavy skiplist siblings (Batch 4 doc-only): `video_generation_agent`, `audio_generation_agent`, `image_generation_agent`, `talking_character_agent`.
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
