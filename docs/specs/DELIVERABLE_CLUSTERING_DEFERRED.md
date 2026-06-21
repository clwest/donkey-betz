---
title: "Deliverable Clustering Recon — deferred until backbone wiring lands"
status: deferred
session: 1194
generated: 2026-06-21
last_reviewed: 2026-06-21
author: claude (pointer doc capturing Session 1193 carryover + 1194 pivot)
companion_docs:
  - INITIATIVES_FIRST_BACKBONE.md                                           # what's happening instead
  - ../handoffs/SESSION_1193_DELIVERABLE_TAGGING_AND_PROJECT_CLUSTERING_INSIGHT.md  # original plan + 8-cluster list
---

# Deliverable Clustering Recon — DEFERRED

## Why this doc exists

Session 1193 surfaced a strategic insight: the flat-deliverable model isn't capturing natural project clusters. ~164 Donkey Betz deliverables; at least 8 obvious project shapes hiding in them. Chris asked for **fresh threads for Session 1194** to do the clustering recon and decide per-cluster: real Initiatives (5-stage arc) vs Collections/Folders (per spec `ae5251f1-…`).

Mid-Session-1194, Chris pivoted: **Initiatives-first backbone wiring** is the real blocker. The platform currently can't enforce "no orphan output" because deliverable↔initiative linkage isn't first-class in the read APIs and isn't enforced on write paths.

The clustering recon is **not abandoned** — it becomes a one-time *migration / cleanup* exercise once the backbone lands. This doc preserves the original plan so it isn't lost.

## What's preserved

The Session 1193 handoff is the source of truth. Read it for full context:
- [`docs/handoffs/SESSION_1193_DELIVERABLE_TAGGING_AND_PROJECT_CLUSTERING_INSIGHT.md`](../handoffs/SESSION_1193_DELIVERABLE_TAGGING_AND_PROJECT_CLUSTERING_INSIGHT.md)

Two sections matter most:
1. **The 8 visible clusters** (Session 1193 §"Chris's late-session insight").
2. **The 4 natural relationship patterns**: time-bounded engineering projects, recurring artifacts, investigation workstreams, product specs that need execution.

### 8 visible clusters (copied here for one-click reference)

1. **Session 1171 — ML Queue + Auth Middleware Triage** (4 deliverables, PR #2328)
2. **Session 1184 — Provenance Linkage** (5+ deliverables, PRs #2362/#2364/#2365)
3. **Session 1187/1188/1189 — Spider Context Utilization** (6 Axis recon + 4 PRs + retune list)
4. **Session 1192 — Workspace Consolidation Follow-ups** (4 P2/P3 deliverables)
5. **COO Operations Diagnostics** (5 daily COO Analysis runs — should be ONE recurring artifact)
6. **Orchestration Control Plane Mapping** (CTO ×3 + DevOps ×4 + COO ×1 + Research ×3 = 11 parallel runs on the SAME investigation)
7. **Track Business News in June 2026** (3-4 ContentWriterAgent blog variants)
8. **MLB Run Line Desk v1** (product spec — real Initiative-shape)

## When to revive

Revive the clustering recon **after** these gates pass:
- AC1-AC6 of [`INITIATIVES_FIRST_BACKBONE.md`](INITIATIVES_FIRST_BACKBONE.md) — the read API surfaces `initiative_id` on deliverables, write paths reject orphans, backfill mgmt command exists.
- Backfill command runs on Donkey Betz historical data — produces `attached / unmatched / ambiguous` counts.

At that point, clustering recon becomes:
1. Walk the `unmatched` and `ambiguous` deliverables from the backfill report.
2. For each cluster (8 above + new ones surfaced by the recon), decide: create an Initiative (5-stage arc) OR mark as recurring-artifact / one-off / archival.
3. Attach historical deliverables to their new initiatives.
4. Decide whether Collections/Folders (spec `ae5251f1-…`) is needed as a second-tier organizing layer beneath Initiatives.

## Carryover deliverables (still filed, not yet executed)

These were filed pre-pivot and remain valid post-backbone:

| Deliverable ID | Title | Status |
|---|---|---|
| `ae5251f1-4863-4319-9c82-a82b6cfc52c2` | Initiative populate redesign (TRIAGE candidates + Collections/Folders option) | P2, partially subsumed by backbone §3.B/C |
| `780a8d15-9ca0-4d91-970f-6934a24fc08d` | Producer reroute fix for `_ensure_system_workspace` regression vector | P2, still valid |
| `c2bac9c0-…` | PA LLM iteration cap silent failure | P2, orthogonal to backbone |
| `c942274b-…` | `deliverable_tool` tooling improvements (tags_add/remove + bulk) | P3, useful for clustering migration step |
| `e17950d8-…` | COO Backlog #4 — Prefetch normalization | P3, unrelated |
| `bebd6794-…` | COO Backlog #9 — Tool-call telemetry rollup | P3, useful for tool-migration Initiative |

## Pointer rule

If someone asks "what happened to the clustering recon?" — point them at this doc + the Session 1193 handoff + `INITIATIVES_FIRST_BACKBONE.md`. The work isn't dead, it's downstream.
