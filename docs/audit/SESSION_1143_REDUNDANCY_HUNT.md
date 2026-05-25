---
title: "Session 1143 — Phase 4 redundancy hunt (non-destructive map)"
status: active
authority: deliverable
session: 1143
date: 2026-05-25
authors: Claude Code (Session 1143), Rigby (PA conversation pa-d19c1674b936)
last_verified: 2026-05-25
---

# Session 1143 — Phase 4 Redundancy Hunt

> **Non-destructive map** of near-duplicate / redundant docs across `docs/reports/`, `docs/architecture/`, `docs/playbooks/`, `docs/topics/`. Per Rigby's Phase 4 spec: cluster by similarity, designate canonical target, recommend disposition — **without moving anything**.

## TL;DR

**~82 docs across the 4 scoped dirs (33 reports + 24 architecture + 6 playbooks + 19 topics).** Significant redundancy concentrated in a few patterns:

| Cluster | Docs affected | Canonical home | Disposition |
|---|---|---|---|
| **System-overview / reality-score / completeness** | 18 | `PLATFORM_INVENTORY.md` + `PLATFORM_WHAT_IT_IS.md` + `topics/*` | V2-Superseded |
| **Agent count / agent infrastructure** | 6 | `topics/agent-system.md` + `PLATFORM_INVENTORY.md` | V2-Superseded |
| **GPT-5 migration urgency (Oct 2025)** | 5 | Migration complete; no active canonical | V2-Archived |
| **Decision Command / Neural Orchestra feature reports** | 4 | Code + topics/ | V2-Superseded |
| **API Key Status (Nov 2025)** | 2 | `PLATFORM_INVENTORY.md` (runtime) | V2-Archived |
| **Endpoint Trace (empty reports)** | 2 | n/a — both "none found" | V2-Deprecated |
| **DaVinci architecture** | 1 | Already-archived `DAVINCI_RESOLVE.md` + sunset decision pending | V2-Superseded after Chris's DaVinci call |
| **Singleton actively-current docs** | ~44 | Themselves | KEEP (no action) |

**Total recommended dispositions: ~38 docs** to receive V2 pointers (Superseded / Archived / Deprecated). **No files moved in this PR** — this is a map for Chris to ratify before any Phase 5 execution.

## Method

Per Rigby's Phase 4 spec + Phase 2A pre-flight checklist §6:
- Bulk-extracted title + first ~8 substantive lines from 82 docs.
- Identified clusters by topic similarity + temporal pattern (older docs claiming X superseded by newer docs claiming Y).
- Cross-referenced against the live canonical chain (`PLATFORM_INVENTORY.md`, `topics/*`, `*_AUDIT.md` autogens).
- Recommended disposition only — no file moves performed.

`handoffs/` (726 files) explicitly excluded from this pass: handoffs are append-only session snapshots, redundancy is structural and intentional. Phase 3 (handoffs retention) is a separate audit.

## Cluster 1 — System-overview / reality-score / completeness docs (18 docs)

Every wave of major work has produced a "complete system map" or "reality score" report. The result: 18 overlapping descriptions of "the platform," with reality scores ranging from 10% to 100%.

| Doc | Date | Reality score claim | Disposition |
|---|---|---|---|
| `reports/COMPLETE_SYSTEM_STATUS_AND_NEXT_STEPS.md` | Sep 2025 | "600k+ embeddings, three-tier caching" | V2-Superseded |
| `reports/COMPREHENSIVE_ECOSYSTEM_DOCUMENTATION.md` | (Django 5.2 era) | "sophisticated AI-powered ecosystem" | V2-Superseded |
| `reports/FINAL_100_PERCENT_SYSTEM_REVIEW.md` | Sep 2025 | 87% complete, 92% production-ready | V2-Superseded |
| `reports/FINAL_AUTHENTICATED_REALITY_SCORE.md` | Oct 2025 | "PRODUCTION READY" | V2-Superseded |
| `reports/ACTUAL_REALITY_SCORE_HONEST_ASSESSMENT.md` | Oct 2025 | 50-60% (frontend mock data) | V2-Superseded |
| `reports/MARKET_READINESS_AUDIT.md` | Nov 2025 | 87% (claimed 99.9%) | V2-Superseded |
| `reports/MARKET_READY_VICTORY.md` | Nov 2025 | 96% (counter-claim to 87%) | V2-Superseded |
| `reports/SYSTEM_ACCOMPLISHMENTS.md` | (102 agents era) | "102 agents + 25 advisors" | V2-Superseded |
| `reports/SYSTEM_INTEGRATION_STATUS_REPORT.md` | Sep 2025 | 75% operational, 149 agents | V2-Superseded |
| `reports/IMPLEMENTATION_ROADMAP.md` | (early) | "10% Complete" | V2-Superseded |
| `reports/NEXT_AGENT_ROADMAP.md` | (post-launch) | "production-ready" | V2-Superseded |
| `architecture/COMPLETE_SYSTEM_MAP.md` | Nov 2025 | "99.9% Reality Score" | V2-Superseded |
| `architecture/COMPLETE_AUTONOMOUS_WORKFLOW_MAP.md` | Nov 2025 | "OPERATIONAL & ENHANCED" | V2-Superseded |
| `architecture/SYSTEM_MAP.md` | (early) | dir-listing format | V2-Deprecated |
| `architecture/SYSTEM_ARCHITECTURE_MAP.md` | (early) | "18-Month AI-Human Collaboration" | V2-Superseded |
| `architecture/UNIFIED_SYSTEM_MAP.md` | Nov 2025 | "99.9% Reality, 34/34 Features" | V2-Superseded |
| `architecture/PLATFORM_ARCHITECTURE_MAP.md` | Nov 2025 | "99.9% Reality, 100% Feature Complete" | V2-Superseded |
| `architecture/MONOREPO_STRUCTURE.md` | Nov 2025 | "Session 100 Part 13 Complete" | V2-Superseded |

**Canonical chain (current):**
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor
- `docs/PLATFORM_INVENTORY.md` — autogen runtime inventory (regenerable, source of truth)
- `docs/ARCHITECTURE.md` (V1 banner) — architecture overview, kept in place
- `docs/SYSTEM_OVERVIEW.md` (V1 banner) — high-level overview
- `docs/topics/*.md` — subsystem deep-dives, current state

**Recommended pattern:** V2-Superseded header on each of the 18 archived-candidates, pointing at the canonical chain. Reality-score claims should be retired entirely — per Chris's directive this session, "verifiable claims only" rule from Session 1142.

## Cluster 2 — Agent count / agent infrastructure docs (6 docs)

Agent count drift is endemic:

| Doc | Agent count claimed | Date |
|---|---|---|
| `reports/SYSTEM_INTEGRATION_STATUS_REPORT.md` | 149 agents | Sep 2025 |
| `reports/SYSTEM_ACCOMPLISHMENTS.md` | 102 agents + 25 advisors | (102 era) |
| `reports/AGENT_EXECUTION_ENGINE_COMPLETED.md` | 149 agents | (early) |
| `reports/NEURAL_ORCHESTRA_REALITY_CONNECTOR_REPORT.md` | 102+ agents | (102 era) |
| `architecture/AI_ASSISTANT_ARCHITECTURE.md` | 74 agents | Jan 2026 |
| `architecture/MULTI_AGENT_ARCHITECTURE.md` | (Session 128 pattern) | Nov 2025 |

**Canonical:** `topics/agent-system.md` (currently says 83 in AGENT_MAP + DB persona rows) + `PLATFORM_INVENTORY.md` autogen.

**Recommendation:** V1-Stale banner on each (these are largely still-canonical for their respective concepts, just with stale counts) pointing at `topics/agent-system.md` + `PLATFORM_INVENTORY.md`.

## Cluster 3 — GPT-5 migration urgency docs (5 docs, Oct 2025)

The GPT-5-mini migration was a major October 2025 push. All 5 docs are about that specific migration moment:

| Doc | Concern |
|---|---|
| `reports/GPT5_MIGRATION_ANALYSIS.md` | "Comprehensive analysis of GPT-5-mini implementation requirements" |
| `architecture/GPT5_AGENT_CONFIGURATION_PATTERNS.md` | "Quick reference for configuring each agent type" |
| `architecture/GPT5_REASONING_MODELS_GUIDE.md` | "Comprehensive guide to properly using GPT-5 reasoning models" |
| `architecture/QUICK_FIX_GUIDE_SESSION_25.md` | "🔴 URGENT — Fixes 100% of agents (196/196)" |
| `architecture/PROMPTING_SYSTEM_COMPREHENSIVE_AUDIT.md` | "🔴 CRITICAL — System incompatible with current LLM" |

Migration is complete. Current PA uses GPT-5.2 function calling per `topics/personal-assistant.md`.

**Canonical:** Migration is closed. No active canonical replacement — the historical docs can be V2-Archived.

**Recommendation:** V2-Archived (status = "historical, migration complete"). Don't try to keep them current; the work is done.

## Cluster 4 — Decision Command / Neural Orchestra feature reports (4 docs)

Each feature has TWO reports: "incomplete" and "complete":

| Pair | Earlier | Later |
|---|---|---|
| Decision Command | `reports/DECISION_COMMAND_IMPLEMENTATION_REPORT.md` ("partially implemented") | `reports/DECISION_COMMAND_INTEGRATION_COMPLETE.md` ("FULLY OPERATIONAL, Sep 2025") |
| Neural Orchestra | `reports/NEURAL_ORCHESTRA_IMPLEMENTATION_REPORT.md` ("incomplete integration") | `reports/NEURAL_ORCHESTRA_REALITY_CONNECTOR_REPORT.md` ("transformed from mock to reality") |

**Code reality check needed:** verify both Decision Command and Neural Orchestra still exist in the React frontend + backend. If yes → V2-Superseded on earlier docs. If features regressed → flag as part of the abandoned-features audit (PR #2191).

**Recommendation:** V2-Superseded on the "incomplete" doc in each pair. Quick code check before any disposition.

## Cluster 5 — API Key Status (2 docs, Nov 2025)

| Doc | Snapshot |
|---|---|
| `reports/API_KEY_STATUS_REPORT.md` | "9/19 valid (47%)" |
| `reports/API_KEY_FINAL_STATUS.md` | "12/19 validated" — later, supersedes |

**Canonical:** `PLATFORM_INVENTORY.md` runtime check + `.env` is the live state.

**Recommendation:** V2-Archived on both (snapshots from a single Nov 2025 audit moment).

## Cluster 6 — Endpoint Trace reports (2 docs, empty)

Both reports show "_none found_" across all sections:

| Doc | Content |
|---|---|
| `reports/endpoint_trace_report.md` | All sections "_none found_" |
| `reports/endpoint_trace_report_detailed.md` | All sections "_none_ / 0" |

These appear to be early scaffolding for an automated endpoint trace that was never wired up.

**Recommendation:** V2-Deprecated. Empty reports add noise.

## Cluster 7 — DaVinci architecture (1 active doc)

| Doc | Status |
|---|---|
| `architecture/DAVINCI_AGENT_ARCHITECTURE.md` | "Design Phase" Nov 2025 |

Already archived: `DAVINCI_RESOLVE.md`, `apis/DAVINCI_RESOLVE_FFMPEG.md`. Per abandoned-features audit (PR #2191): DaVinci is "shipped + unused, $0 ROI." Pending Chris's sunset / revive / dormant decision.

**Recommendation:** Hold this one until Chris answers the DaVinci question in #2191. If sunset → V2-Archived. If revive → KEEP (and update). If dormant → V1-Stale + "verify before use."

## Singletons — actively-current, no redundancy

These ~44 docs are the only doc on their topic, currently relevant, and don't need disposition. Examples:

- `reports/3D_GENERATION_VERIFICATION_REPORT.md` — specific verification snapshot
- `reports/CONSISTENCY_PROBLEM_AND_SOLUTIONS.md` — open architecture question
- `reports/CONTENT_STUDIO_SYSTEM_REVIEW.md` — content studio review (singleton)
- `reports/DATA_URI_INVESTIGATION.md` — historical resolved incident
- `reports/LOGIN_LOGOUT_FIX_SUMMARY.md` — historical fix
- `reports/REDDIT_AGENT_RESURRECTION_PLAN.md` — plan (status unclear)
- `reports/REPO_REVIEW.md` — local Ollama review
- `reports/donkey-betz-codex-audit.md` — case study (singleton; folded from `case-studies/` in Phase 2A)
- `reports/spider_inventory.md` — autogen-style inventory
- `reports/VERIFY_REPORT.md` — context-kit autogen
- `reports/WEBSOCKET_DIAGNOSTIC_REPORT.md` — historical WS diagnostic
- All `architecture/*` not in Cluster 1/3 (learning_system, ml_architecture, MEMORY_SYSTEM_ARCHITECTURE, partnership_model, PERFECT_WORKFLOW_DESIGN, sports_betting_integration, WORKFLOW_ORCHESTRATION_AGENT, PROMPTING_SYSTEM — has a `Historical note: this document predates Rigby unification` banner)
- All `playbooks/*` (6 files — DEMO_HAPPY_PATH, pa-claude-code-collaboration, + 4 in nested subdirs)
- All `topics/*` (19 files — these ARE the canonical chain; KEEP)

## Recommendations for Chris

### Tier 1 — safe to execute (no business judgment needed)

1. **Cluster 6 (endpoint trace, empty docs):** V2-Deprecated. Empty reports add noise. Trivial.
2. **Cluster 5 (API key status):** V2-Archived. Both are Nov-2025 snapshots; runtime is the source of truth now.
3. **Cluster 3 (GPT-5 migration urgency):** V2-Archived. Migration complete; docs are historical.

### Tier 2 — needs Chris greenlight (the big "reality score" cluster)

4. **Cluster 1 (18 system-overview docs):** V2-Superseded on all 18, pointing at the current canonical chain. Caveat: these docs contain interesting historical "we thought X% was reality" data. Some have white-paper-corpus value. Preserve via V2 stubs, don't delete.

5. **Cluster 2 (agent count drift):** V1-Stale banners pointing at `topics/agent-system.md`. These docs are still-canonical for their concepts; just stats are stale.

### Tier 3 — needs feature verification first

6. **Cluster 4 (Decision Command, Neural Orchestra):** Quick code check first. If features still exist → V2-Superseded on the "incomplete" doc per pair. If regressed → flag in abandoned-features audit instead.

### Tier 4 — wait for Chris's DaVinci call

7. **Cluster 7 (DaVinci architecture):** disposition depends on Chris's answer to the DaVinci sunset/revive/dormant question from PR #2191.

## What's NOT in scope for this audit

- **No file moves** (deliberate). This is a non-destructive map.
- **No content rewrites.** V2 banner application is its own future PR.
- **No `handoffs/` redundancy analysis.** Handoffs are append-only snapshots; redundancy is structural and intentional. Phase 3 (handoffs retention) is separate.
- **No code verification** of Decision Command / Neural Orchestra in this PR (Cluster 4) — that's Tier 3 follow-up before any V2 banners on those.
- **No "reality score" cleanup in canonical docs.** Some still-canonical docs at root (e.g., `WIREMAP.md`, `BACKEND_INVENTORY.md`) have stale reality-score language; that's V1-Stale banner work, not Phase 4 scope.

## Cross-reference to Session 1143 audit deliverables

- **Master audit:** [`docs/audit/SESSION_1143_DOCS_AUDIT.md`](SESSION_1143_DOCS_AUDIT.md) — 6 pathologies, per-subdir verdicts.
- **Abandoned-features audit:** [`docs/audit/SESSION_1143_ABANDONED_FEATURES_AUDIT.md`](SESSION_1143_ABANDONED_FEATURES_AUDIT.md) — Chris's question about archived docs describing finished features.
- **Methodology spec:** [`docs/00-START-HERE/DOC_LIFECYCLE.md`](../00-START-HERE/DOC_LIFECYCLE.md) — V1 / V2 pointer header conventions + root-stability rule.

---

**Authors:** Claude Code (Session 1143) + Rigby (PA conversation `pa-d19c1674b936`). Non-destructive map per Rigby's Phase 4 spec; ~38 V2-disposition candidates identified across 7 clusters. No files moved; awaiting Chris's per-cluster greenlight before any Phase 5 execution.
