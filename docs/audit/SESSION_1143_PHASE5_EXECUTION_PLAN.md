---
title: "Session 1143 — Phase 5 execution plan (queued, gated on Chris's per-PR picks)"
status: active
authority: pre-execution-plan
session: 1143
date: 2026-05-25
authors: Claude Code (Session 1143), Rigby (PA conversation pa-d19c1674b936)
last_verified: 2026-05-25
---

# Session 1143 — Phase 5 Execution Plan

> **This is the ready-to-execute checklist for after Chris answers the decision packet.** Each section lists the exact PR I'd open + the work inside. No files moved by this doc itself — it's a pre-execution plan only.

## Gating

Phase 5 starts ONLY after Chris answers these from the four open audit deliverables:

| PR | Question to Chris |
|---|---|
| #2191 abandoned-features audit | DaVinci: sunset / revive / dormant? Mobile cockpit: confirm status quo (no action)? |
| #2192 Phase 4 redundancy hunt | Tier 1 auto-exec (GPT-5 migration + API key + empty endpoint trace docs)? Tier 2 (reality-score retire + agent-count V1 banners)? Tier 3 (Decision Command / Neural Orchestra code verify)? |
| #2193 Phase 3 handoffs retention | Option A / B / C? |
| (closed) #2190 | Stays parked; no action |

Once Chris answers each one, the corresponding PR below gets opened. If Chris answers all of them in one shot, this turns into a multi-PR Phase 5 sprint.

## PR queue — what gets opened for each Chris answer

### From #2191 abandoned-features audit

**If DaVinci = sunset:**
- PR title: `docs(session-1143-phase5): DaVinci Resolve sunset — V2-Deprecated headers + code-side flagging`
- Scope:
  - V2-Deprecated headers on `content/davinci_provider.py` + `core/views_davinci.py` + `content/davinci_bridge_client.py` (code-side annotation, not deletion)
  - V2-Deprecated header on already-archived `DAVINCI_RESOLVE.md` + `apis/DAVINCI_RESOLVE_FFMPEG.md` (upgrade their V2-Moved → V2-Deprecated)
  - V2-Deprecated header on the active `architecture/DAVINCI_AGENT_ARCHITECTURE.md`
  - Optionally: remove DaVinci routes from `core/urls.py` (commented out, not deleted) — Chris flag

**If DaVinci = revive:** I write a 1-page revive scope (concrete use case, target session) — separate decision-prep doc. No code changes.

**If DaVinci = dormant:** V1-Stale banners on the in-place code + docs (visible warning without removal). Minimal PR.

**Mobile cockpit:** no PR needed (already correctly archived).

### From #2192 Phase 4 redundancy hunt

**Tier 1 auto-exec (assuming Chris says yes — safe):**
- PR title: `docs(session-1143-phase5): Tier 1 redundancy disposition — GPT-5 migration + API keys + empty endpoint trace`
- Scope: V2-Archived headers on 9 docs:
  - `reports/GPT5_MIGRATION_ANALYSIS.md`
  - `architecture/GPT5_AGENT_CONFIGURATION_PATTERNS.md`
  - `architecture/GPT5_REASONING_MODELS_GUIDE.md`
  - `architecture/QUICK_FIX_GUIDE_SESSION_25.md`
  - `architecture/PROMPTING_SYSTEM_COMPREHENSIVE_AUDIT.md`
  - `reports/API_KEY_FINAL_STATUS.md`
  - `reports/API_KEY_STATUS_REPORT.md`
- V2-Deprecated headers on 2 empty docs:
  - `reports/endpoint_trace_report.md`
  - `reports/endpoint_trace_report_detailed.md`

**Tier 2 (assuming Chris says yes — bigger):**
- PR title: `docs(session-1143-phase5): Tier 2 redundancy disposition — reality-score V2-Superseded + agent-count V1-Stale`
- Scope: V2-Superseded headers on 18 system-overview docs (Cluster 1). V1-Stale banners on 6 agent-count docs (Cluster 2).
- Also: add Rigby's PLATFORM_INVENTORY + docs/INDEX paragraph to `DOC_LIFECYCLE.md` so the reality-score cluster can't regenerate.

**Tier 3 (assuming Chris says yes — needs code verify first):**
- Pre-PR: code-check Decision Command + Neural Orchestra. Verify both still exist in `frontend/src/` + backend.
- If both still working → PR: `docs(session-1143-phase5): Tier 3 redundancy disposition — Decision Command + Neural Orchestra V2-Superseded`. V2-Superseded the "incomplete" doc per pair.
- If either regressed → flag as new abandoned-features finding; no V2 banner.

**Tier 4 DaVinci:** rolls into the DaVinci sunset/revive/dormant PR above.

### From #2193 Phase 3 handoffs retention

**If Chris picks A (keep):**
- PR title: `docs(session-1143-phase5): handoffs Option A — V1 banners on pre-800 + INDEX.md navigation`
- Scope:
  - Add V1 stale-banner one-liner to each of 453 pre-Session-800 handoffs (`# Last Updated: Session ≤800` + banner)
  - Hand-build (or autogen) `docs/handoffs/INDEX.md` grouping handoffs into 100-session buckets

**If Chris picks B (archive pre-800):**
- PR title: `docs(session-1143-phase5): handoffs Option B — archive pre-800 with V2 stubs + reindex`
- Scope:
  - `git mv docs/handoffs/SESSION_*_*.md (where session ≤800)` to `docs/archive/handoffs-pre-800/`
  - V2-Moved stubs at all 453 original paths
  - Rebuild `docs/INDEX.md` + regen `search_docs` corpus (`.rag/corpus.jsonl`) + reindex `kb_tool`
  - Verify `CURRENT.md` unaffected

**If Chris picks C (hybrid):**
- PR 1: `docs(session-1143-phase5a): handoffs Option C part 1 — archive pre-2026 to handoffs-2025/`
- PR 2: `docs(session-1143-phase5b): handoffs Option C part 2 — archive early-2026 + lock naming convention`
- Scope (combined): split pre-Session-500 → `docs/archive/handoffs-2025/`, Session 501-799 → `docs/archive/handoffs-early-2026/`. Add `SESSION_NNNN_*` naming-convention spec to `DOC_LIFECYCLE.md`. Full re-index.

### Follow-up — stale canonical V1 banners

**Gated on Chris approving Phase 4 Tier 2 (reality-score retire):**
- PR title: `docs(session-1143-phase5): root canonical V1 stale banners — WIREMAP + BACKEND_INVENTORY`
- Scope: V1 stale-but-canonical banners on root docs with stale reality-score language: `WIREMAP.md`, `BACKEND_INVENTORY.md`. Both currently lack the banner. Tiny PR.

## Estimated effort per PR

| PR | Files touched | Effort estimate | Risk |
|---|---|---|---|
| DaVinci sunset | ~8 files | 30 min | Low (annotation only) |
| Tier 1 redundancy | 11 files | 30 min | Low |
| Tier 2 redundancy | 24 files | 1 hr | Medium (touches 18 high-traffic docs) |
| Tier 3 code-verify + redundancy | ~2 docs after code check | 45 min | Medium (depends on code state) |
| Handoffs Option A | 453 banner edits + 1 INDEX | 1-2 hrs | Low |
| Handoffs Option B | 453 moves + 453 stubs + reindex | 2-3 hrs | Medium (RAG identity churn) |
| Handoffs Option C | Same as B + 1 naming-spec doc | 3-4 hrs | Medium |
| Root V1 banners follow-up | 2 files | 15 min | Low |

## Order of execution (recommended)

If Chris approves multiple items:

1. **DaVinci sunset/revive/dormant** (closes the abandoned-features loop)
2. **Tier 1 redundancy** (zero-risk auto-exec)
3. **Root V1 banners follow-up** (tiny, gates on Tier 2 approval)
4. **Tier 2 redundancy** (the big one — 18 + 6 docs)
5. **Tier 3 code-verify + Decision Command / Neural Orchestra** (could surface new findings)
6. **Handoffs retention** (whichever option Chris picked — biggest churn)

Each becomes its own PR for review-ability.

## What this doc is NOT

- **Not execution.** No file moves performed.
- **Not committed decisions.** Each tier above is contingent on Chris's per-PR pick.
- **Not exhaustive.** New findings from Tier 3 code-verify or DaVinci revive scoping may surface follow-up work.

---

**Authors:** Claude Code (Session 1143) + Rigby (PA conversation `pa-d19c1674b936`). Prepared per Rigby's "draft Phase 5 execution plan as a checklist" recommendation so once Chris answers the decision packet, execution can start immediately.
