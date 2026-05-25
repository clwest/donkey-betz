# Current Handoff Pointer

> Stable pointer so future sessions don't have to lex-sort 600+ files to find the latest handoff.

**Latest strategy docs (Session 1116 — read for current state):**
- [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) (v1) — brand pivot Donkey Betz → 24/7 Global AI, soft-cut architecture
- [`docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`](../247_LIVE_INTELLIGENCE_PANEL_SKETCH.md) — first u-d-b → 247globalai.com integration; **shipped** this session
- [`docs/COST_SURVIVAL_AUDIT.md`](../COST_SURVIVAL_AUDIT.md) — Phase 0 gating constraints (still pending)

**Character OS merge — parked:**
- [`docs/MERGE_PROPOSAL_CHARACTER_OS.md`](../MERGE_PROPOSAL_CHARACTER_OS.md) (sidecar) and [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](../MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) (native) stay in tree as v2 backlog. Unpark only if a paying customer asks for an avatar.

**Latest handoff:** [`SESSION_1148_P35_ROUND2_AND_SYSTEM_OWNER_DRIFT_LABEL.md`](SESSION_1148_P35_ROUND2_AND_SYSTEM_OWNER_DRIFT_LABEL.md)
(**2 PRs open**, fourth back-to-back session today, closed clean. Rigby-specced quick-wins-only (option c) after three docs-cleanup sessions: **#2223** P3.5 round 2 — backfill next 75 handoffs (handoffs-only this round, cap 75 raised from round 1's 50); range SESSION_1146 → SESSION_891; index regenerated post-backfill to 2056 docs / HIGH=1273; 521 more handoffs eligible for round 3 (76 files, +903/-216). **#2224** SYSTEM_OWNER.md drift-label refresh — added "Last reviewed for drift labeling: Session 1148" + spot-check finding that §3 emergency commands (`skin_lock`, `quarantine_agent`, `list_quarantined`) don't exist in `core/management/commands/`; flagged in banner, no body rewrite per Rigby "keep it a labeling pass"; real `skin_lock` behavior still in `WorkspaceOperation` model just no CLI entry point (1 file, +7/-2). 9 follow-ups queued for Session 1149: P3.5 r3 (521 left), older topics sweep, counts-hygiene on bannered topics, exists_on_disk flag, beat-schedule regens, build_learning_bridge_audit fix, Redis pooling, SYSTEM_OWNER §3 emergency-procedures rewrite (NEW), reports/patents recon. Merge preference: #2223 → #2224.)

**Previous:** [`SESSION_1147_P35_BACKFILL_PLUS_APPS_AND_TOPICS_SWEEPS.md`](SESSION_1147_P35_BACKFILL_PLUS_APPS_AND_TOPICS_SWEEPS.md)

## How to update

When a new session writes a handoff, update **only** the "Latest" line above and shift the prior entry into "Previous." Keep this file at exactly two pointer entries — the full history lives in the lex-sorted handoffs directory.

## Source-of-truth reminders

- **Counts:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) is canonical.
- **Narrative:** [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md).
- **Audit workspace:** [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md).
- **PA route:** `POST /api/pa/chat/` (canonical). `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.

---

*Established: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 5.*
