# Audit Workspace Index

> Top-level pointer so future sessions don't have to guess which `audit*` folder is current.

## Canonical (current)

| Workspace | Purpose | Start here |
|---|---|---|
| **`docs/audit/`** | **CURRENT.** Active audit + cleanup plan. | [`AUDIT_V1.md`](audit/AUDIT_V1.md) · [`CLEANUP_PLAN.md`](audit/CLEANUP_PLAN.md) · [`README.md`](audit/README.md) |

The current audit lives **only** in `docs/audit/`. New audit work goes there.

## Historical (preserve, do not cite as current truth)

| Workspace | Era | Notes |
|---|---|---|
| `docs/audit-2026/` | April 2026, time-bounded subsystem dossiers | 13-file series. Numbers and route examples may be stale. Index: [`00-AUDIT-PLAN.md`](audit-2026/00-AUDIT-PLAN.md). |
| `docs/audits/` | Pre-2026 session-numbered audit archive (~56 files) | Historical session sweeps. Route examples (e.g., `/api/assistant/chat/`) predate the `/api/pa/chat/` canonical convention — treat as legacy compat references. Index: [`INDEX.md`](audits/INDEX.md). |

## Rules of the road

- **Source-of-truth chain when stats disagree:** `docs/PLATFORM_INVENTORY.md` (runtime-derived) → `docs/PLATFORM_WHAT_IT_IS.md` (narrative) → everything else.
- **Canonical PA route:** `POST /api/pa/chat/`. Anything saying `/api/assistant/chat/` or `/api/v1/assistant/chat/` inside the historical workspaces is a legacy compatibility shim, not a recommendation.
- **Memory rule:** never delete historical audits. Add pointer headers, archive in place.
- **Live drift check:** `python manage.py verify_doc_claims --only-drift`.

---

*Created: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 3. Maintained alongside `docs/audit/README.md`.*
