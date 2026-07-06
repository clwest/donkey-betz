---
title: "Implementation Debt Register — IOS §8.3 debt track"
status: active
authority: implementation-debt
session_added: 2700
generated: 2026-07-06
schema_ref: IOS §8.3 (v1) debt schema
companion_register: docs/research/implementation/BACKLOG.md
---

# Implementation Debt Register

Mirrors the Research Debt concept from Research OS §15. Debt accrues from:
- Intake items that don't survive first contact with implementation (`RETRACTED`).
- Intake items whose research prerequisites resurfaced mid-arc (`DEFERRED`).
- Arc work that partially discharged an intake (`PARTIAL_DISCHARGE`).
- Contract violations flagged during Stage 5 verification (`CONTRACT_VIOLATION`).
- Tech debt accrued during Stage 4 build (`TECH_DEBT_ACCRUED`).

See IOS `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` §8.3 for schema definition and §8.4 for retracted findings register discipline.

## Schema

| Field | Meaning |
|-------|---------|
| `debt_id` | `IDBT-NNNN` (numbered by creation order) |
| `origin_intake_id` | Which intake produced the debt (or N/A for pre-arc origin) |
| `origin_arc_ref` | Which arc surfaced the debt (or N/A for pre-arc origin) |
| `debt_type` | `RETRACTED` \| `DEFERRED` \| `PARTIAL_DISCHARGE` \| `TECH_DEBT_ACCRUED` \| `CONTRACT_VIOLATION` |
| `severity` | `LOW` \| `MEDIUM` \| `HIGH` |
| `description` | Free-text |
| `resolution_path` | What would discharge it (new research arc / new intake / redesign / ADR revision) |
| `status` | `ACTIVE` \| `RESOLVED` |
| `created` | ISO date |
| `resolved` | ISO date (populated on status flip to RESOLVED) |

Debt is paid down in dedicated arcs or piggybacked on adjacent arcs — same pattern as Research Debt.

## Active debt (as of 2026-07-06)

### `IDBT-0001` — PARTIAL_DISCHARGE HIGH — first-queue leaf tail unenumerated

| Field | Value |
|-------|-------|
| `debt_id` | `IDBT-0001` |
| `origin_intake_id` | N/A (arose during Part 11 Step 1 first execution, pre-arc) |
| `origin_arc_ref` | N/A (pre-arc; predates Arc I-0100) |
| `debt_type` | `PARTIAL_DISCHARGE` |
| `severity` | `HIGH` |
| `description` | Deep-late xx99 arcs (1699/1799/1899/1999/2099/2199/2299/2499/2599/2699) §8 tier bundles were under-enumerated at leaf granularity during Part 11 Step 1 first execution (2026-07-06). Both parallel Explore extractors ran token-partial on the tail; extractor 1 (xx99 side) claimed 347 rows and delivered ~40 explicit rows with tail counts inferred; extractor 2 (audit side) claimed 287 rows and delivered ~150 explicit rows with rich Pass B §14.7–§14.17 coverage but under-explicit CX-P surface enumeration for CX-P4. Estimated ~50 T1/T2/T3 leaf rows unenumerated across the tail. Chris ratified tier bands at v0-partial per 2026-07-06 record (`RATIFICATION_2026-07-06_first_queue.md`), explicitly accepting that band totals will climb modestly on full re-extraction. Consequence: `BACKLOG.md` is complete at tier-band totals + T0 + Arc I-0100 seed rows (`IB-1799-T1-01/02/03`) + Chris-visible representative T1 leaf rows + DEFER + cross-arc initiative rows, but incomplete at T1 tail + T2 leaf + T3 leaf. |
| `resolution_path` | Two discharge paths available: (1) Dedicated re-extraction session — third full pass on 1699/1799/1899/1999/2099/2199/2299/2499/2599/2699 §8 leaf detail, appending discovered rows to `BACKLOG.md` with `chris_gate: RATIFIED` inherited from band-level ratification. Estimated 1–2 sessions of focused extraction. (2) Arc-scoped incremental discharge — each arc's Stage 1 scoping re-extracts leaf rows for its target domain(s) before Stage 2 opens, appending discovered rows to `BACKLOG.md` at that time. This spreads discharge across ~10 arcs (one per xx99 domain touched); each Stage 1 discharges its arc's slice. Arc I-0100 Observability Spine Stage 1 discharges the 1799 slice first. Chris preference implicit at 2026-07-06 ratification (chose path 2 by proceeding to first-arc identity without requesting re-extraction) — path 1 remains available if arc-scoped discharge proves too slow. |
| `status` | `ACTIVE` |
| `created` | 2026-07-06 |
| `resolved` | (open) |

## Resolved debt

_(none yet)_

## Amendment discipline

- **Adding debt:** Assign next `IDBT-NNNN` id. Populate all Yes-required schema fields. Set `status: ACTIVE`. Cross-reference into `BACKLOG.md` intake row via `notes` field or PR body if origin_intake_id exists.
- **Resolving debt:** Flip `status: RESOLVED`, populate `resolved` date, add a resolution note (which arc / PR / ADR discharged). Do NOT delete resolved rows — the register is truth-history per IOS §8.4 pattern.
- **Grep queries:** `grep -E 'debt_type.*PARTIAL_DISCHARGE' IMPLEMENTATION_DEBT.md`, `grep -E 'severity.*HIGH' IMPLEMENTATION_DEBT.md`, `grep -E 'status.*ACTIVE' IMPLEMENTATION_DEBT.md`.
