# Current Handoff Pointer

> Stable pointer so future sessions don't have to lex-sort 600+ files to find the latest handoff.

**Latest strategy docs (Session 1116 — read for current state):**
- [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) (v1) — brand pivot Donkey Betz → 24/7 Global AI, soft-cut architecture
- [`docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`](../247_LIVE_INTELLIGENCE_PANEL_SKETCH.md) — first u-d-b → 247globalai.com integration; **shipped** this session
- [`docs/COST_SURVIVAL_AUDIT.md`](../COST_SURVIVAL_AUDIT.md) — Phase 0 gating constraints (still pending)

**Character OS merge — parked:**
- [`docs/MERGE_PROPOSAL_CHARACTER_OS.md`](../MERGE_PROPOSAL_CHARACTER_OS.md) (sidecar) and [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](../MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) (native) stay in tree as v2 backlog. Unpark only if a paying customer asks for an avatar.

**Latest handoff:** [`SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md`](SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md)
(~25 PRs across 9 repos. Dockerized all 7 FastAPI+React fleet apps on `fleet-net`. Brain bridge (`POST /api/brain/ask` + frontend Brain page) live across all 7 — each app now proxies questions to u-d-b's PA in 4.7-9s. New private repo `github.com/clwest/infra` with `make up` launcher. u-d-b PGDATA fix #2121 — postgres data was in a subdir, missing env caused crash-loop. Defang sweep replaced `POSTGRES_PASSWORD=<repo>` antipattern with `change-me-in-production` (GitGuardian-clean). signal-studio backend port moved 8080→8007. ai-content-studio Docker foundation PR #2 open but parked. Behavior layer validation: Rigby invoked the no-claims-verification rule unprompted during testing.)

**Previous:** [`SESSION_1124_DOCTOR_WARNINGS_CLEARANCE.md`](SESSION_1124_DOCTOR_WARNINGS_CLEARANCE.md)

## How to update

When a new session writes a handoff, update **only** the "Latest" line above and shift the prior entry into "Previous." Keep this file at exactly two pointer entries — the full history lives in the lex-sorted handoffs directory.

## Source-of-truth reminders

- **Counts:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) is canonical.
- **Narrative:** [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md).
- **Audit workspace:** [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md).
- **PA route:** `POST /api/pa/chat/` (canonical). `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.

---

*Established: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 5.*
