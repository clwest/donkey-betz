# Current Handoff Pointer

> Stable pointer so future sessions don't have to lex-sort 600+ files to find the latest handoff.

**Latest strategy docs (Session 1116 — read for current state):**
- [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) (v1) — brand pivot Donkey Betz → 24/7 Global AI, soft-cut architecture
- [`docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`](../247_LIVE_INTELLIGENCE_PANEL_SKETCH.md) — first u-d-b → 247globalai.com integration; **shipped** this session
- [`docs/COST_SURVIVAL_AUDIT.md`](../COST_SURVIVAL_AUDIT.md) — Phase 0 gating constraints (still pending)

**Character OS merge — parked:**
- [`docs/MERGE_PROPOSAL_CHARACTER_OS.md`](../MERGE_PROPOSAL_CHARACTER_OS.md) (sidecar) and [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](../MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) (native) stay in tree as v2 backlog. Unpark only if a paying customer asks for an avatar.

**Latest handoff:** [`SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md`](SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md)
(13 merged PRs + 1 parked. Deep `/docs/` audit + Phase 5 execution sprint. Methodology lock in [`DOC_LIFECYCLE.md`](../00-START-HERE/DOC_LIFECYCLE.md): V1/V2 pointer headers + §2b runtime-coupled paths inventory + §2c sole-counts-source rule. 39 Cat-B root docs archived + 72 frozen-subdir files archived + 457 pre-Session-800 handoffs archived. DaVinci Resolve sunset (Chris Q1=A). Reality-score cluster retired. NEW finding: Decision Command shipped then regressed — React frontend gone, backend `AIIncomeBuilder` skeleton remains. Mission refresh #2190 parked per Chris's mid-session directive to curb business/GTM framing. Active handoffs reduced 726 → 273. RAG corpus rebuilt: 19,993 chunks / 2,602 files.)

**Previous:** [`SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md`](SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md)

## How to update

When a new session writes a handoff, update **only** the "Latest" line above and shift the prior entry into "Previous." Keep this file at exactly two pointer entries — the full history lives in the lex-sorted handoffs directory.

## Source-of-truth reminders

- **Counts:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) is canonical.
- **Narrative:** [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md).
- **Audit workspace:** [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md).
- **PA route:** `POST /api/pa/chat/` (canonical). `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.

---

*Established: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 5.*
