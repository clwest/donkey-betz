# Session 969 - Start Here

**Previous Session:** 968 (Insight De-dup Bundling + Frontend Data Plumbing)
**Date:** February 7, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** (cleaned from 568) | **Risk-Aware RAG: COMPLETE** | **Doc Classification: 562 DOCS** | **Boardroom ML: ACTIVE** | **Unified PA: ANALYTICAL ADVISOR** | **Voice System: COMPLETE** | **Learning Loop: REFINED** | **Agent Provenance: 26+ AGENTS** | **RAG Observability UI: COMPLETE** | **PA Intelligence Enrichment: ACTIVE** | **Phase 0-4 Deliberation: COMPLETE** | **Content Deliberation Pipeline: ACTIVE** | **Insight De-dup Bundling: ACTIVE**

---

## Session 968 Summary (Just Completed)

### Phase 5A — Review Insight De-dup / Bundling - COMPLETE

Memory Palace now bundles duplicate insight memories from the same conversation into a single expandable card.

**Problem:** `ConversationOrchestrator.create_conversation_memories()` creates one `AgentMemory(memory_type='insight')` per participant. A 2-agent review = 2 near-identical cards in Memory Palace.

**Solution:** Bundle by `source_id` (conversation UUID) — no migration, no new model fields.

#### Backend (`core/views_memory_palace.py`, +3 lines)
- Added `source_id` to `get_agent_memories()` serialization
- Added `source_id` + `tags` to `list_all_memories()` serialization

#### Frontend (`frontend/src/pages/MemoryPalacePage.tsx`, ~75 lines)
- `bundleInsights()` utility groups insight memories by `source_id`
- `InsightBundleCard` component: collapsed = title + "N agents" badge; expanded = individual cards
- `isBundle()` type guard for render branching

### Also in Session 968
- **remarkGfm import fix** — `ContentStudioTab` was missing the import (commit `72e802b5`)
- **Frontend data plumbing audit** — PR #970, unwired visibility layer

---

## Current System State

| Metric | Count |
|--------|-------|
| Active Initiatives | 52 |
| Services | 134 |
| Celery Tasks | 261 |
| Content Pipeline | v1 (direct) + v2 (deliberation) |
| PA Tools | 86 |

---

## PA Self-Awareness Gap (Discovered Session 968)

The PA was asked "what's been going on the last 2 hours?" and correctly admitted it lacks live telemetry access. However, it then:
- **Hallucinated agent count** (said 215, actual is 76)
- **Invented tech stack** (Prometheus, Grafana, ELK, PagerDuty — none exist)
- **Proposed massive over-engineering** (6-step enterprise observability plan)
- **Was unaware of its own 86 tools** already in `unified_pa_entrypoint.py`

**What's actually needed:** 2-3 simple PA tools that query recent activity via Django ORM:
1. `get_recent_activity(hours=2)` — recent Celery task results, spider runs, errors
2. `get_system_health()` — aggregate body system heartbeats (already exist)
3. `get_recent_errors(hours=2)` — recent log entries or failed tasks

These would be simple additions to the existing PA tool infrastructure, not a new observability platform.

---

## What Could Come Next

### PA Live Telemetry Tools (from PA self-awareness gap)
1. **PA Recent Activity Tool** — Simple Django ORM query for recent Celery results, spider data, initiative changes
2. **PA System Health Tool** — Aggregate existing body system heartbeats into a single health snapshot
3. **PA Error Summary Tool** — Query recent failed tasks and errors

### Phase 5 Possibilities (from Surgical Moves Audit)
1. **Frontend Deliberation Viewer** — React component showing deliberation replay (turns, evidence, claims) in Content Studio
2. **Claim Citation Scoring** — Score blog posts based on percentage of claims cited vs unsourced assertions
3. **Auto-Revision Loop** — If REVISE decision, loop through reviewer feedback automatically (currently does 1 pass)
4. **ClaimsPack Enrichment** — Add semantic similarity search to claims (pgvector) instead of keyword matching
5. **Review Panel Metrics** — Track reviewer agreement rates, common issue types, decision distribution over time

### Other Ideas
- Wire v2 pipeline into the auto-blog Celery Beat schedule alongside v1
- Add deliberation metadata to frontend blog cards (show review verdicts, claim count)
- Expose claims data in the PA for "how was this blog reviewed?" queries

---

## Key Files Reference

### Session 968 Files
| File | Purpose |
|------|---------|
| `core/views_memory_palace.py` | Added `source_id` to list API serializers |
| `frontend/src/pages/MemoryPalacePage.tsx` | `bundleInsights()` + `InsightBundleCard` |

### Phase 4 Files
| File | Purpose |
|------|---------|
| `core/services/content_claims.py` | SpiderClaim + ClaimsPack dataclasses |
| `core/services/claims_pack_builder.py` | ClaimsPackBuilder singleton |
| `core/services/content_review_panel_v2.py` | 3 reviewers + validate_review_payload() |
| `core/services/content_deliberation_runner.py` | ContentDeliberationRunner.run_blog() |

### PA Tool System
| File | Purpose |
|------|---------|
| `core/services/unified_pa_entrypoint.py` | 86 PA tools, intent routing, enrichment pipeline |
| `core/services/pa_intelligence_enricher.py` | 5 enrichment services wired to PA |

---

## Recent Session History

| Session | Focus | PRs |
|---------|-------|-----|
| **968** | Insight De-dup Bundling + remarkGfm fix + frontend data plumbing | #970 |
| **964** | Phase 4 Content Deliberation Pipeline - ClaimsPack, 3-reviewer panel, DecisionEnforcer, v2 blog API | - |
| **961c** | PA Initiative Audit + Cleanup - audit action, merged 94 dupes, archived 420 noise | #960 |
| **961b** | PA Initiative Display Fix - raised limits, total count, full names | #959 |
| **960** | Phase 0 Connectors - SourceInfo/Claim extensions, doc tracking, DecisionEnforcer fallback | - |
| **959** | PA Intelligence Upgrade - Analytical advisor with enrichment pipeline | #954 |
| **957** | RAG Observability Frontend - Complete UI dashboard | #943 |
| **954-956** | Doc Classification + Boardroom ML + Initiative Cleanup + Learning Loop + RAG Observability | #935-#942 |
| **953** | Agent Provenance Expansion - 18 agents with provenance tracking | - |

---

**Session 969 Focus: Your choice! See "What Could Come Next" above.**
