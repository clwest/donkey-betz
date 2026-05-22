# Current Handoff Pointer

> Stable pointer so future sessions don't have to lex-sort 600+ files to find the latest handoff.

**Latest strategy docs (Session 1116 — read for current state):**
- [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) (v1) — brand pivot Donkey Betz → 24/7 Global AI, soft-cut architecture
- [`docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`](../247_LIVE_INTELLIGENCE_PANEL_SKETCH.md) — first u-d-b → 247globalai.com integration; **shipped** this session
- [`docs/COST_SURVIVAL_AUDIT.md`](../COST_SURVIVAL_AUDIT.md) — Phase 0 gating constraints (still pending)

**Character OS merge — parked:**
- [`docs/MERGE_PROPOSAL_CHARACTER_OS.md`](../MERGE_PROPOSAL_CHARACTER_OS.md) (sidecar) and [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](../MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) (native) stay in tree as v2 backlog. Unpark only if a paying customer asks for an avatar.

**Latest handoff:** [`SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md`](SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md)
(3 PRs merged: #2123 Docker runtime metadata block added to each of the 7 fleet repo profiles + register_external_repo markdown serializer patched to surface it. #2124 fleet_health rollup — mgmt command + `fleet_health` PA tool, shared probe function. #2125 Phase 1 agent-specific consult routing — `config/fleet_agent_routing.json` + `core/services/fleet_routing.py:resolve()` + PA chat accepts/emits structured `routing` block. METADATA pipeline only; Phase 2 wires `resolved_agent` into PA's deliberation router + updates 7 fleet brain_clients. Workspaces already existed from Session 1119. Rigby co-designed all three.)

**Previous:** [`SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md`](SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md)

## How to update

When a new session writes a handoff, update **only** the "Latest" line above and shift the prior entry into "Previous." Keep this file at exactly two pointer entries — the full history lives in the lex-sorted handoffs directory.

## Source-of-truth reminders

- **Counts:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) is canonical.
- **Narrative:** [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md).
- **Audit workspace:** [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md).
- **PA route:** `POST /api/pa/chat/` (canonical). `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.

---

*Established: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 5.*
