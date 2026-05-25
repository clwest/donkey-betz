# Current Handoff Pointer

> Stable pointer so future sessions don't have to lex-sort 600+ files to find the latest handoff.

**Latest strategy docs (Session 1116 — read for current state):**
- [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) (v1) — brand pivot Donkey Betz → 24/7 Global AI, soft-cut architecture
- [`docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`](../247_LIVE_INTELLIGENCE_PANEL_SKETCH.md) — first u-d-b → 247globalai.com integration; **shipped** this session
- [`docs/COST_SURVIVAL_AUDIT.md`](../COST_SURVIVAL_AUDIT.md) — Phase 0 gating constraints (still pending)

**Character OS merge — parked:**
- [`docs/MERGE_PROPOSAL_CHARACTER_OS.md`](../MERGE_PROPOSAL_CHARACTER_OS.md) (sidecar) and [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](../MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) (native) stay in tree as v2 backlog. Unpark only if a paying customer asks for an avatar.

**Latest handoff:** [`SESSION_1147_P35_BACKFILL_PLUS_APPS_AND_TOPICS_SWEEPS.md`](SESSION_1147_P35_BACKFILL_PLUS_APPS_AND_TOPICS_SWEEPS.md)
(**3 PRs open**, third back-to-back session, closed clean. Rigby-specced 3-step docs cleanup: P3.5 backfill → apps light-touch → topics pragmatic. **#2219** P3.5 frontmatter backfill (50 handoffs FM-tagged + filename override upstream in build_docs_provenance — catches SESSION_998 git-attributed-to-997 cases; HIGH 1122→1274, MEDIUM 422→292, UNKNOWN 511→489; 53 files +1416/-747). **#2220** docs/apps/ light touch — Rigby called it: BRIEFs already well-curated against products.ts canon, V1/V2 banners would be noise; just renamed `session:` → `originating_session:` across 9 files + parked colorado_family_law's status (9 files, +10/-10). **#2221** docs/topics/ pragmatic sweep — V1 banners on 5 highest-traffic recent unbannered docs (README, obs-remote-control, multi-repo-management, fleet-doc-verifier-rollout, content-pipeline) + new "Where current truth lives" paragraph in topics/README explaining §2c routing (5 files, +35/-4). 9 follow-ups queued for Session 1148: P3.5 round 2 with 548 more handoffs eligible, older topics sweep, exists_on_disk flag, beat-schedule regens, build_learning_bridge_audit generator fix, Redis pooling, governance staleness check, reports/patents recon, counts-hygiene on already-bannered topic docs. Merge preference: #2219 → #2221 → #2220.)

**Previous:** [`SESSION_1146_ROOT_AUDITS_SWEEP.md`](SESSION_1146_ROOT_AUDITS_SWEEP.md)

## How to update

When a new session writes a handoff, update **only** the "Latest" line above and shift the prior entry into "Previous." Keep this file at exactly two pointer entries — the full history lives in the lex-sorted handoffs directory.

## Source-of-truth reminders

- **Counts:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) is canonical.
- **Narrative:** [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md).
- **Audit workspace:** [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md).
- **PA route:** `POST /api/pa/chat/` (canonical). `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.

---

*Established: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 5.*
