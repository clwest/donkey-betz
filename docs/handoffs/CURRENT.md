# Current Handoff Pointer

> Stable pointer so future sessions don't have to lex-sort 600+ files to find the latest handoff.

**Latest strategy docs (Session 1116 — read for current state):**
- [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) (v1) — brand pivot Donkey Betz → 24/7 Global AI, soft-cut architecture
- [`docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`](../247_LIVE_INTELLIGENCE_PANEL_SKETCH.md) — first u-d-b → 247globalai.com integration; **shipped** this session
- [`docs/COST_SURVIVAL_AUDIT.md`](../COST_SURVIVAL_AUDIT.md) — Phase 0 gating constraints (still pending)

**Character OS merge — parked:**
- [`docs/MERGE_PROPOSAL_CHARACTER_OS.md`](../MERGE_PROPOSAL_CHARACTER_OS.md) (sidecar) and [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](../MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) (native) stay in tree as v2 backlog. Unpark only if a paying customer asks for an avatar.

**Latest handoff:** [`SESSION_1145_ARCHITECTURE_SWEEP_AND_PROVENANCE_PLAN_B.md`](SESSION_1145_ARCHITECTURE_SWEEP_AND_PROVENANCE_PLAN_B.md)
(**3 PRs open**, session closed clean. Architecture sweep + Provenance Plan B end-to-end. **#2211** `docs/architecture/{INDEX,README}.md` rewritten as folder-local nav — removed Session 85 "master architecture" + "99.9% Reality" + "34 features" + "20+ tools" + "Launch readiness 85%" claims (§2c violations); +53/-364. **#2212** V1/V2 banner sweep across 8 unbannered architecture docs — 3 V1-DriftWarning (PROMPTING_SYSTEM, WORKFLOW_ORCHESTRATION_AGENT, ml_architecture; Rigby overrode 2 V2→V1 to preserve still-useful design intent) + 5 V2-Deprecated (MEMORY_SYSTEM_ARCHITECTURE, PERFECT_WORKFLOW_DESIGN, learning_system, partnership_model, sports_betting_integration). After this session, 22 of 24 docs in `docs/architecture/` carry V1/V2 banners. **#2213** Provenance Plan B: P1 `build_docs_provenance` writes `docs/_provenance.json` (2052 docs / HIGH=1120 / MEDIUM=421 / UNKNOWN=511 / 6571 commits parsed with two-pass git log via ASCII US/RS delimiters); P2 `search_docs` PA tool gains optional `originating_session: int` filter — pure-function helper extracted, 6/6 unit tests pass, non-breaking; P3 `backfill_doc_provenance` command applied to 2 eligible HIGH-confidence docs (FLEET_MOVE_1_AND_2_SPEC + SESSION_1056 handoff). Three Rigby-greenlit follow-ups for next session: P3.5 broader backfill (handoffs+specs+canon, add new FM blocks, cap 50), `exists_on_disk: false` flag for 326 dead paths in index, weekly beat-schedule the regen. Clean session — no fires, no service restarts mid-work.)

**Previous:** [`SESSION_1144_DOCS_CLEANUP_PROVENANCE_AND_LEAK_FIX.md`](SESSION_1144_DOCS_CLEANUP_PROVENANCE_AND_LEAK_FIX.md)

## How to update

When a new session writes a handoff, update **only** the "Latest" line above and shift the prior entry into "Previous." Keep this file at exactly two pointer entries — the full history lives in the lex-sorted handoffs directory.

## Source-of-truth reminders

- **Counts:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) is canonical.
- **Narrative:** [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md).
- **Audit workspace:** [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md).
- **PA route:** `POST /api/pa/chat/` (canonical). `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.

---

*Established: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 5.*
