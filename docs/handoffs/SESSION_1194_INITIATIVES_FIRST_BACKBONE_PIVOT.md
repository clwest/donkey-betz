# Session 1194 — Initiatives-First Backbone pivot + Plans A + B shipped

**Status:** Wrapped clean. **3 PRs merged-ready** (1 docs/spec + 2 code), 3 spine Initiatives persisted + backfilled to Donkey Betz, AC1+AC2+AC3+AC4 of `INITIATIVES_FIRST_BACKBONE.md` closed. Two real diagnostics surfaced by the new read API.
**Date:** 2026-06-21
**Active conversation:** `pa-e11847db632a4ee8` (fresh thread for both Claude AND Rigby per Chris's request after Session 1193 wrap).
**Prior session:** [`SESSION_1193_DELIVERABLE_TAGGING_AND_PROJECT_CLUSTERING_INSIGHT.md`](./SESSION_1193_DELIVERABLE_TAGGING_AND_PROJECT_CLUSTERING_INSIGHT.md).

## TL;DR

Session 1194 opened with project-clustering recon as P1 (Session 1193 carryover). **Chris pivoted mid-thread** to a deeper structural fix: make Initiatives the spine of the platform — agents/schedules/deliverables must attach to an Initiative to count as real work. Rigby and Claude collaborated on the wiring-break diagnosis; the result is `docs/specs/INITIATIVES_FIRST_BACKBONE.md` (the spec PR) + Plans A and B implemented end-to-end. Plans C (write-path enforcement) and D (governor gating) are scoped + open-ratified, sized for follow-on sessions. The flat-deliverable clustering plan is preserved in `docs/specs/DELIVERABLE_CLUSTERING_DEFERRED.md` and gated on AC1-AC6 passing — exactly what Plans A+B+C deliver.

## PRs shipped

| PR | Branch | Theme | Closes |
|---|---|---|---|
| **#2397** | `docs/session-1194-initiatives-first-pivot` | Pivot spec + deferred clustering pointer | n/a (foundation) |
| **#2398** | `feat/session-1194-initiatives-backbone-a-audit-gap` | Plan A — close audit gap: field shape + workspace_id filter convergence + `audit_deliverable_endpoints` mgmt command | **AC1** |
| **#2399** | `feat/session-1194-initiatives-backbone-b-read-api-linkage` | Plan B — read-path initiative linkage + paginated `initiative_deliverables` action (stacked on #2398) | **AC2, AC3, AC4** |

**Stacked-PR footgun reminder:** #2399's base is currently #2398's branch. Retarget #2399 to `main` BEFORE merging #2398 (per Session 1188 #2381 incident memory `feedback_stacked_pr_base_deletion_footgun.md`).

## 3 spine Initiatives — persisted + backfilled

Rigby persisted these via `work_tool initiative_create` at 2026-06-21 ~23:14 UTC; Claude backfilled `target_workspace_id` → Donkey Betz at session close.

| # | Name | UUID | target_workspace |
|---|---|---|---|
| 1 | Initiatives-First Wiring + No-Orphan Output | `6941372d-b13c-4631-91c8-749fa65c55a0` | Donkey Betz (b4503364-…) |
| 2 | Agent Capability Map + Router Contracts | `2071a9c6-986f-4528-be90-8cccaa595f1e` | Donkey Betz (b4503364-…) |
| 3 | Tool Migration Hardening (web_search → intelligence_tool) | `7e23d621-4d0c-409a-a680-4fd2e015d04b` | Donkey Betz (b4503364-…) |

## What's now true

**Read-path:**
- `deliverable_tool.list` and `content_tool.content_recent` agree on shape + count + workspace scoping (AC1).
- Every deliverable read-API response includes `initiative_id` + `initiative_name` + workspace fields (AC2). Round-trip `initiative ↔ deliverable` resolvable in one PA tool call.
- Every initiative read-API response includes `target_workspace_id` + `target_workspace_name` + `deliverable_count` (AC3).
- NEW `work_tool action=initiative_deliverables` — paginated reverse projection. Optional `workspace_id` filter for cross-workspace scoping (AC4).

**Diagnostics:**
- New `audit_deliverable_endpoints` mgmt command supports `--workspace`, `--days`, `--json`, `--fail-on-drift`. Drift band ±5 rows. Currently exits 0 on Donkey Betz.
- `content_tool.content_recent` adds `total` field (parity gap Rigby flagged in Plan A verification).

## Open ratifications (carry into Session 1195+)

Captured in `INITIATIVES_FIRST_BACKBONE.md` §6:
- **§6.1 RATIFIED Session 1194** — Phase 1 mark-diagnostic + `[ORPHAN-DELIVERABLE]` log → Phase 2 hard-reject after 7d zero-emission window.
- **§6.2 OPEN** — Inference rule for initiative attachment when payload omits `initiative_id`. Defer until Plan A audit data shapes the rule.
- **§6.3 RATIFIED Session 1194** — Separate paginated `initiative_deliverables` action + `deliverable_count` summary on `initiative_detail` (chose over embedded list — would blow up for high-volume initiatives like the deferred COO Diagnostics cluster).

## Diagnostics surfaced by Plan B verification

Plan B's new read API made two real diagnostics observable for the first time:

1. **Spine Initiatives created without target_workspace.** All 3 had `target_workspace_id=null` after Rigby's `initiative_create` call. **Backfilled at session close** via ORM update — all 3 now bound to Donkey Betz. Real fix: the `initiative_create` write path should require or infer `target_workspace_id`. Sized as a small Plan C side-quest.
2. **Cross-workspace deliverable linkage from producer-reroute bug.** A `ResearchAgent` deliverable (`41172258-…`) was linked to spine Initiative #2 but lives in **System Autonomous Workspace** instead of Donkey Betz — the producer-reroute bug from Session 1192 (`780a8d15-…`) made visible for the first time. **Plan C's no-orphan enforcement on the write path is exactly what fixes this.** Plan B's optional `workspace_id` filter on `initiative_deliverables` lets read-path callers scope around it today.

## What's next (Session 1195 candidates)

| Item | Priority | Status |
|---|---|---|
| **Plan C — write-path enforcement** | **P1** | Phased per §6.1: Phase 1 mark-diagnostic + `[ORPHAN-DELIVERABLE]` log; Phase 2 hard-reject after 7d clean window. Add `backfill_deliverable_initiative_links` mgmt command. AC5a/b/c + AC6. |
| **Plan C side-quest — `initiative_create` requires target_workspace_id** | P2 | Carry-over from spine Initiative diagnostic. Should be folded into Plan C since both are write-path enforcement. |
| **Plan D — governor gating** | P2 | Scheduler skips dispatch when no ACTIVE Initiative matches. `[GOVERNOR-SKIP]` log lines. AC7. Independent of Plan C; can land in parallel. |
| **AC8 round-trip traceability test** | P3 | Unit test from §4.1 of the spec. Small follow-up. |
| **AC9/AC10 — Tool Migration Hardening** | P2 | Initiative #3's owned scope. `web_search` → `intelligence_tool.search` audit + gateway retry/backoff. ~50% failure rate to investigate. |
| **Deliverable clustering recon** | DEFERRED | `docs/specs/DELIVERABLE_CLUSTERING_DEFERRED.md`. Revive after backbone AC1-AC6 pass (Plan C closes AC5+AC6). |

## Pinned conversation

`pa-e11847db632a4ee8` — Session 1194 thread, healthy at pause. Rigby has full backbone context loaded.

## Memory candidates (assess at next session-open review)

1. **`feedback_rebase_stacked_prs_when_string_search_fails.md`** — when Edit tool can't find expected anchor text in a feature branch, it usually means the branch was cut from the wrong base. Plan B's `total`-field edit failed twice until I rebased onto Plan A's branch. Pattern: if you're editing code that builds on a prior PR's changes and the anchor text isn't there, rebase the child branch onto the parent BEFORE re-attempting.
2. **`feedback_data_drift_revealed_by_new_observability.md`** — new read APIs that surface previously-hidden joins reveal real data drift the moment they ship. Plan B's `initiative_deliverables` surfaced the producer-reroute bug + the spine-Initiative target_workspace=null bug as separate findings on first call. Pattern: when shipping observability over a graph, expect 1-2 "wait, that's wrong" data findings per new edge surfaced — and budget for filing them as separate deliverables.

## Quick summary for the next AI

Read `docs/specs/INITIATIVES_FIRST_BACKBONE.md` end-to-end. The spec is the operating contract. Plans A+B are merged-ready in PRs #2398 + #2399 (stacked). Plan C is the next P1 — start at §3.C of the spec, treat §6.1's phased rollout as ratified, and decide §6.2 (inference rule) once the backfill mgmt command runs against real Donkey Betz data. The 3 spine Initiatives are bound to Donkey Betz and ready to be referenced.

The clustering recon from Session 1193 is **not abandoned**, just downstream of the backbone. `docs/specs/DELIVERABLE_CLUSTERING_DEFERRED.md` is the pointer.
