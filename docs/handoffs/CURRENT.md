# Current Handoff Pointer

> Stable pointer so future sessions don't have to lex-sort 600+ files to find the latest handoff.

**Latest planning docs (Session 1116 — pick one):**
- [`docs/MERGE_PROPOSAL_CHARACTER_OS.md`](../MERGE_PROPOSAL_CHARACTER_OS.md) — sidecar architecture (new `spokesperson/` Django app, isolated, easy rollback)
- [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](../MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) — native integration (extend `Advisor` + `VideoHistory`, finishing layers as general-purpose video ops, faster long-term but harder rollback)

Both proposals plan to fold Character OS (`runway-hackathon`) into u-d-b. Read both before deciding. The native proposal includes a comparison table in Appendix A.

**Latest handoff:** [`SESSION_1115_CODE_HEALTH_REFACTORS.md`](SESSION_1115_CODE_HEALTH_REFACTORS.md)

**Previous:** [`SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md`](SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md)
(early-phase companion of the same session — read both for complete 1115 context)

## How to update

When a new session writes a handoff, update **only** the "Latest" line above and shift the prior entry into "Previous." Keep this file at exactly two pointer entries — the full history lives in the lex-sorted handoffs directory.

## Source-of-truth reminders

- **Counts:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) is canonical.
- **Narrative:** [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md).
- **Audit workspace:** [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md).
- **PA route:** `POST /api/pa/chat/` (canonical). `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.

---

*Established: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 5.*
