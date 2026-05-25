---
originating_session: 1143
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1143 — Docs Corpus Audit + Cleanup (113 archived, 457 handoffs archived, 6 Phase 5 execution PRs)

**Date:** 2026-05-25
**Branch state at close:** All 14 Session 1143 PRs merged to main. 1 parked (#2190 mission refresh). Two new audit deliverables live in `docs/audit/` + Phase 5 execution plan + Session 1143 handoff (this doc).

---

## TL;DR

Chris opened Session 1143 asking for a deep audit of `/docs/`. The result was 13 merged PRs + 1 parked across the session, with a Phase 5 execution sprint that landed every disposition Chris greenlit from the decision packet. Highlights:

1. **Methodology lock** — `docs/00-START-HERE/DOC_LIFECYCLE.md` with V1/V2 pointer headers, runtime-coupled paths inventory (§2b), sole-counts-source rule (§2c), and root-stability rule (§3). The corpus now has a shared vocabulary for "moved" vs "stale" vs "superseded" vs "deprecated."
2. **Root cleanup** — 39 Cat-B frozen docs moved to `docs/archive/superseded-2026-05/` with V2-Moved stubs. 6 V1 stale-but-canonical banners on root-stable cited docs. Loose-top-level count dropped from 92 → ~52.
3. **Subdir consolidation** — 9 frozen subdirs (`agents/`, `apis/`, `body/`, `features/`, `guides/`, `pre-launch/`, `integrations/`, `workflows/`, `BUGS/`) archived (72 files) + 6 single-file folds + roadmap merge.
4. **Self-correction caught mid-flight:** `docs/AUDIT_INDEX.md` (Session 1101) explicitly defines `audit/` = current, `audit-2026/` = April historical dossier, `audits/` = pre-2026 archive — a deliberate cycle taxonomy, NOT redundancy. Phase 2A reversed the planned audit consolidation; the Session 1143 audit doc itself was moved from `audit-2026/` to `audit/`.
5. **Abandoned-features audit** — 113 archived docs analyzed + 14 high-signal code-verify checks. Most archived docs describe features still present in code. **One genuine "shipped + regressed" case surfaced:** Decision Command (React frontend removed; backend `AIIncomeBuilder` skeleton remains in 5 files).
6. **DaVinci Resolve sunset** — Chris's call. V2-Deprecated headers on 5 docs + `.. deprecated::` docstring markers on `content/davinci_provider.py`, `core/views_davinci.py`, `content/davinci_bridge_client.py`.
7. **Reality-score cluster retired** — 18 docs claiming various reality scores (10% → 100%) V2-Superseded. New `DOC_LIFECYCLE.md §2c` locks `PLATFORM_INVENTORY.md` + `docs/INDEX.md` as the sole authoritative counts going forward.
8. **`docs/handoffs/` 62% reduction** — 457 pre-Session-800 handoffs archived to `docs/archive/handoffs-pre-800/` with V2-Moved stubs at original paths. Active handoffs dropped from 726 → 273. RAG corpus rebuilt: 19,993 chunks across 2,602 files.

Chris also explicitly **paused all business/GTM/market framing** mid-session, refocusing on docs-only hygiene. Mission refresh draft (#2190) parked.

---

## What landed — 13 merged PRs

### Audit + methodology pipeline (5 PRs)

| PR | Title | What |
|---|---|---|
| **#2183** | Phase 0 — corpus audit + DOC-POINTER-V2 lifecycle spec | Master audit doc + methodology lock. V1/V2 pointer headers, status enum, stub-redirect pattern, root-stability rule. |
| **#2186** | Phase 1 — 39 Cat-B archived + V1/V2 pointers + runtime-coupled paths inventory | 39 root-level docs → archive with V2 stubs. 6 V1 banners on root-stable cited docs (API_PATH_POLICY, DREAM_INITIATIVE_WORKFLOW, WIREMAP, canon/INDEX, governance/SYSTEM_OWNER, missions/CURRENT_MISSION). Added §2b runtime-coupled paths inventory. |
| **#2187** | Phase 2A — folds + roadmap merge + audit-doc placement fix | 6 single-file dir folds (case-studies/discord/mobile/operations/verification/context-packets). Merged `roadmaps/` into `roadmap/`. Mid-flight correction: moved `SESSION_1143_DOCS_AUDIT.md` from `audit-2026/` to `audit/` per AUDIT_INDEX.md cycle taxonomy. |
| **#2188** | Phase 2B-1 — archive 9 frozen subdirs (72 files) with V2 stubs | `agents/`, `apis/`, `body/`, `features/`, `guides/`, `pre-launch/`, `integrations/`, `workflows/`, `BUGS/` → archive. 11 Python comment refs updated in same PR. |
| **#2189** | Phase 2B-2 — docs/ops/ clarification + docs/tools/ V1 banners | `docs/ops/` confirmed runtime-coupled (celery_inspect_report.py output dir) — kept + clarifying README. `docs/tools/` PA manifest/routing-guide V1-Stale banners. Both reclassified from "delete/fold" to "KEEP." |

### Decision-prep deliverables (3 PRs)

| PR | Title | What |
|---|---|---|
| **#2191** | Abandoned-features audit on 113 archived docs | Direct answer to Chris's "are these unfinished features" question. Bulk-tag + 14 code-verify checks. Most archived docs describe still-shipped features. DaVinci flagged for sunset decision. |
| **#2192** | Phase 4 — redundancy hunt (non-destructive map across 82 docs) | 7 clusters covering 38 docs. Biggest cluster: 18 "reality score" docs. Tiered for decision (Tier 1 auto-exec / Tier 2 reality-score retire / Tier 3 code-verify / Tier 4 wait-on-DaVinci). |
| **#2193** | Phase 3 — handoffs retention memo + Phase 5 execution plan | Decision-prep memo. 3 options (A keep / B archive / C hybrid) for handoffs. Pre-execution plan for all 6 Phase 5 PRs. |

### Phase 5 execution (6 PRs — all merged per Chris's decision packet)

Chris answered: **Q1=A, Q2=Y, Q3=Y, Q4=Y, Q5=Y, Q6=B.**

| PR | Title | Chris Q |
|---|---|---|
| **#2194** | DaVinci Resolve sunset | Q1=A |
| **#2195** | Tier 1 redundancy disposition | Q3=Y |
| **#2196** | BACKEND_INVENTORY V1 stale banner | Q4 follow-up |
| **#2197** | Tier 2 redundancy — reality-score retire + agent-count V1-Stale + sole-counts-source lock | Q4=Y |
| **#2198** | Tier 3 code-verify + NEW finding: Decision Command REGRESSED | Q5=Y |
| **#2199** | Handoffs Option B — 457 pre-Session-800 archived + RAG rebuild | Q6=B |

### Parked (1 PR)

| PR | Title | Reason |
|---|---|---|
| **#2190** | Mission refresh DRAFT — 24/7 Global AI Suite framing | Chris's mid-session directive: pause all business/GTM framing, refocus on docs-only. Branch preserved for when Chris reopens GTM work. |

---

## Key findings + decisions

### Decision Command regressed (NEW abandoned-features finding)

The Phase 5 Tier 3 code-verify (PR #2198) confirmed Decision Command shipped (per `DECISION_COMMAND_INTEGRATION_COMPLETE.md` Sep 2025) then REGRESSED:

- No `DecisionCommand.tsx` in `frontend/src/`
- No `decision-command` route in `App.tsx`
- Backend `AIIncomeBuilder` skeleton remains in 5 Python files

**Backend cleanup is out of Session 1143 scope** — flagged for future consideration as the first genuine "shipped + regressed" case from the audit. Both Decision Command report docs carry V2-Superseded banners with explicit REGRESSED notes.

### Reality-score cluster — retired

18 docs across `reports/` + `architecture/` each claimed different reality scores (10% / 50-60% / 75% / 87% / 88% / 92% / 96% / 99.7% / 99.9% / 100%) across various sessions. All V2-Superseded in PR #2197. New `DOC_LIFECYCLE.md §2c`:

> **`PLATFORM_INVENTORY.md` + `docs/INDEX.md` are the ONLY authoritative counts going forward.**

Every other count is a snapshot. Reality-score claims are explicitly retired. New docs write conceptual narrative ("agent layer routes via AGENT_MAP") not numeric claims ("83 agents"). Verifier flags exceptions.

### Audit-dir cycle taxonomy preserved (self-correction)

Phase 2A almost consolidated `audit/` → `audit-2026/`. Mid-flight read of `docs/AUDIT_INDEX.md` (Session 1101) revealed:

- `audit/` = **CURRENT** audit workspace (active truth-propagation cycle)
- `audit-2026/` = **HISTORICAL** April 2026 dossier series (closed)
- `audits/` = pre-2026 archive

Deliberate cycle taxonomy, NOT duplication. Phase 2A reversed the planned consolidation. `SESSION_1143_DOCS_AUDIT.md` was mis-placed in `audit-2026/` during Phase 0; corrected to `audit/` with V2-Moved stub at the old path.

### DaVinci Resolve — sunset locked (Chris Q1=A)

Per `UNDERUTILIZED_FEATURES.md` (Session 412): $300+ Studio license, never used, $0 ROI. PR #2194 applied:

- V2-Deprecated banners on `docs/DAVINCI_RESOLVE.md`, `docs/archive/superseded-2026-05/DAVINCI_RESOLVE.md`, `apis/DAVINCI_RESOLVE_FFMPEG.md`, `architecture/DAVINCI_AGENT_ARCHITECTURE.md`
- `.. deprecated:: Session 1143` docstring markers on `content/davinci_provider.py`, `core/views_davinci.py`, `content/davinci_bridge_client.py`

Code preserved (no deletion). Future PR may remove routes from `core/urls.py` if Chris wants.

### handoffs/ retention — Option B executed (Chris Q6=B)

457 files moved from `docs/handoffs/` to `docs/archive/handoffs-pre-800/`:
- 450 SESSION_NNN_*.md where NNN ≤ 799
- 7 HANDOFF_NN_*.md early structured plans

457 V2-Moved stubs at original paths. `docs/handoffs/` active count: 726 → 273 (62% reduction). RAG corpus rebuilt: 19,993 chunks / 2,602 files in `.rag/corpus.jsonl`.

**Citation-identity caveat:** prior `[docs/handoffs/SESSION_NNN_*.md#chunk_K]` chunk_ids reset; mitigated by RAG rebuild.

---

## Methodology landed (in `docs/00-START-HERE/DOC_LIFECYCLE.md`)

| Section | Content |
|---|---|
| §1. DOC-POINTER-V1 + V2 | Two pointer-header types with full status enum + stub-redirect pattern + citation-identity caveat |
| §2b | Runtime-coupled doc paths inventory (5 paths: canon/INDEX, governance/SYSTEM_OWNER, missions/CURRENT_MISSION, decisions/ADR-*, docs/ops/) |
| §2c | Sole-counts-source rule (Rigby's lock) — PLATFORM_INVENTORY + docs/INDEX only |
| §3. Root-stability rule | Anything cited from CLAUDE.md / 00-START-NEXT-SESSION.md / *_AUDIT.md stays at root |
| §4-6 | Loose-vs-subdir heuristic + before-you-move checklist + Phase 2A pre-flight checklist |

---

## Deliverable docs landed in `docs/audit/`

- [`SESSION_1143_DOCS_AUDIT.md`](../audit/SESSION_1143_DOCS_AUDIT.md) — master audit, 6 pathologies, per-subdir verdict table, 4-phase action queue
- [`SESSION_1143_ABANDONED_FEATURES_AUDIT.md`](../audit/SESSION_1143_ABANDONED_FEATURES_AUDIT.md) — direct answer to Chris's question
- [`SESSION_1143_REDUNDANCY_HUNT.md`](../audit/SESSION_1143_REDUNDANCY_HUNT.md) — Phase 4 non-destructive map
- [`SESSION_1143_HANDOFFS_RETENTION_OPTIONS.md`](../audit/SESSION_1143_HANDOFFS_RETENTION_OPTIONS.md) — Phase 3 decision-prep memo (Option B chosen by Chris)
- [`SESSION_1143_PHASE5_EXECUTION_PLAN.md`](../audit/SESSION_1143_PHASE5_EXECUTION_PLAN.md) — Phase 5 plan (all 6 PRs executed per Chris's decision packet)

---

## Disposition counts (final state of main)

- **Active root docs (docs/*.md):** ~52 (down from 92)
- **archived/superseded-2026-05/:** 113 files (39 Cat-B + 72 frozen-subdir + 2 misc)
- **archived/handoffs-pre-800/:** 457 files
- **V2-Moved stubs at original paths:** ~520 (covers all Phase 1, 2A, 2B-1, 2B-2, and Phase 5 Handoffs B moves)
- **V1-Stale banners applied:** 14 (3 root-stable cited + 3 Python-load-bearing + 6 stale-but-canonical including BACKEND_INVENTORY + 2 from Tier 2)
- **V2-Superseded:** 21 (Tier 2 reality-score cluster + Tier 3 Decision Command/Neural Orchestra)
- **V2-Deprecated:** 11 (DaVinci docs + 5 GPT-5 migration + 2 endpoint trace empty)
- **V2-Archived:** 9 (Tier 1 dispositions)

---

## Open carryovers for future sessions

### High-priority (action queue, Chris-only)

1. **Decision Command backend cleanup** — `AIIncomeBuilder` skeleton in 5 Python files describes a regressed feature. Frontend removed; backend bones useless. Future PR could remove the routes + the `AIIncomeBuilder` class. Chris-only call.
2. **DaVinci route cleanup** — `core/urls.py` still routes to `core/views_davinci.py` (now `.. deprecated::`). Commenting out or removing the routes is a small follow-up if Chris wants.
3. **Mission refresh (#2190 branch)** — preserved for when Chris reopens GTM/business framing. Currently parked.

### Medium-priority

4. **Naming convention pass** — Rigby's question #7 from the audit (singular vs plural dirs like `roadmap/roadmaps`, `audit/audits`). Roadmap merge handled the worst case in Phase 2A; other naming inconsistencies are minor.
5. **Refresh missions/CURRENT_MISSION.md content** — file is runtime-coupled, currently still says "Q1 2026 / $10K MRR." V1 banner makes the staleness visible but the content drives every agent prompt. Needs a refresh when Chris reopens mission work.
6. **`handoffs/CURRENT.md` had been stale** — was pointing at Session 1126 before this session updated it to 1143. The "How to update" instruction says to maintain Latest + Previous; Sessions 1127-1142 skipped this. Worth establishing a session-close discipline.

### Low-priority / informational

7. **The 9 frozen Cat-B archive dirs are now navigable** but their contents are still un-refreshed. If Chris wants any of them un-frozen (e.g., refresh `agents/README.md` for current 83-AGENT_MAP state), that's a separate effort.
8. **The 273 active handoffs in `docs/handoffs/`** still benefit from a `docs/handoffs/INDEX.md` for navigation. Option A from Phase 3 memo proposed this; Option B was chosen instead, but the INDEX would still help.

---

## What changed in the corpus (numerically)

| Metric | Before Session 1143 | After Session 1143 |
|---|---|---|
| Loose root docs | 92 | ~52 |
| Active handoffs | 726 | 273 |
| Total `docs/archive/` size | 11 MB | ~18 MB |
| RAG corpus chunks | 19,305 (2,017 files) | 19,993 (2,602 files) |
| DOC_LIFECYCLE.md sections | 0 | 6 (V1 + V2 + §2b + §2c + §3 + checklists) |
| Runtime-coupled paths documented | 0 | 5 (canon, governance, missions, decisions, ops) |
| Reality-score claims in active docs | ~18 | 0 (all V2-Superseded) |

---

## Cross-references

- Methodology spec: [`docs/00-START-HERE/DOC_LIFECYCLE.md`](../00-START-HERE/DOC_LIFECYCLE.md)
- Master audit: [`docs/audit/SESSION_1143_DOCS_AUDIT.md`](../audit/SESSION_1143_DOCS_AUDIT.md)
- Per-PR audit summaries inline above (#2183 through #2199)
- AUDIT_INDEX.md updated to surface all 5 Session 1143 audit deliverables
- Previous session: [`SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md`](SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md)

---

**Authors:** Claude Code (Session 1143) + Rigby (PA conversation `pa-d19c1674b936`). 13 merged PRs + 1 parked (#2190) across the session. End-to-end docs-only work per Chris's mid-session directive to "curb anything about business or going to market."
