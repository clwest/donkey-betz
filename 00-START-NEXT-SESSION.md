# Session 970 - Start Here

**Previous Session:** 969b (PA Live Telemetry Tools)
**Date:** February 8, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** (cleaned from 568) | **Risk-Aware RAG: COMPLETE** | **Doc Classification: 562 DOCS** | **Boardroom ML: ACTIVE** | **Unified PA: ANALYTICAL ADVISOR** | **Voice System: COMPLETE** | **Learning Loop: REFINED** | **Agent Provenance: 26+ AGENTS** | **RAG Observability UI: COMPLETE** | **PA Intelligence Enrichment: ACTIVE** | **Phase 0-4 Deliberation: COMPLETE** | **Content Deliberation Pipeline: ACTIVE** | **Insight De-dup Bundling: ACTIVE** | **Orchestration Enrichment: ACTIVE** | **Blog Diversity: ACTIVE** | **PA Live Telemetry: ACTIVE**

---

## Session 969b Summary (Just Completed)

### PA Live Telemetry Tools (PR #974)
Closed the PA self-awareness gap discovered in Session 968. Added 3 new tools so the PA can answer system status questions with real data instead of hallucinating:

- **`recent_activity_tool`** — "What's been going on?" — queries Celery tasks, SpiderData, HiveMindSession, SelfBlog, Initiative, SignalCluster within configurable time window (default 2h)
- **`system_health_tool`** — "How's the system?" — aggregates HeartBeat, ComponentStatus, Celery success rate, ToolCallAggregate, Spider freshness with computed `overall_assessment` (healthy/degraded/critical)
- **`error_summary_tool`** — "Any errors?" — queries FailureSignature, FailureDetection, failed ToolCallRecord, failed Celery tasks with computed `severity` (none/low/moderate/high)

Intent routing with 30+ natural language phrases, hours extraction from messages ("last 6 hours" -> `hours=6`). Verified on Railway production — all tools returning real data.

### Session 969 Summary (Earlier Same Day)

- **Orchestration Tab Enrichment** (PR #971) — Wired up existing APIs: metrics bar, execution cost, full output in modals, HiveMind sessions
- **ORM Fix** (PR #972) — `LearningPattern.times_successful` -> `success_when_applied`
- **Blog Diversity** (PR #972) — 10 diverse fallback topics replacing hardcoded AI ecosystem topic

---

## Current System State

| Metric | Count |
|--------|-------|
| Agents | 76 (49 routable, 25 non-routable, 26+ provenance-tracked) |
| Spiders | 77 (72 working, 5 need API keys) |
| Advisors | 25 |
| Active Initiatives | 52 (cleaned from 568 in Session 961c) |
| Database Models | 386+ |
| Services | 134 |
| Celery Tasks | 261 |
| Content Pipeline | v1 (direct) + v2 (deliberation) — with diverse fallbacks |
| PA Tools | 89 (was 86, +3 telemetry) |
| Tool Dispatcher Handlers | 47 |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |

---

## Known Issues / Open Items

### Agent Dream: Intent-Driven Highlights Engine (Session 969)
FullStackDeveloperAgent dreamed about an "editing intent capture" layer for content highlight generation. Researched and rated 7/10 on market grounding:
- Real gap: no competitor captures creator intent during recording for highlight ML
- Academic research validates context signals beat raw ML for highlights
- Most viable as recording-first platform feature, not standalone product

---

## What Could Come Next

### PA Response Formatting for Telemetry
The PA's LLM prompt builder could use intent-specific directives for telemetry tools (e.g., "Summarize the activity concisely, highlight anything unusual"). Currently the tools return structured data that the PA formats generically.

### Phase 5 Possibilities (from Surgical Moves Audit)
1. **Frontend Deliberation Viewer** — React component showing deliberation replay in Content Studio
2. **Claim Citation Scoring** — Score blog posts based on percentage of claims cited vs unsourced
3. **Auto-Revision Loop** — If REVISE decision, loop through reviewer feedback automatically
4. **ClaimsPack Enrichment** — Add semantic similarity search to claims (pgvector)
5. **Review Panel Metrics** — Track reviewer agreement rates, decision distribution over time

### Other Ideas
- Wire v2 pipeline into auto-blog Celery Beat schedule alongside v1
- Add deliberation metadata to frontend blog cards (review verdicts, claim count)
- Expose claims data in PA for "how was this blog reviewed?" queries
- Celery Beat schedule monitoring in `system_health_tool`
- Trend comparison (current vs previous period) in `recent_activity_tool`
- Auto-surface telemetry warnings in PA greeting

---

## Critical Patterns & Gotchas

**Django settings module:** `core.settings` (NOT `config.settings`). Always use `DJANGO_SETTINGS_MODULE=core.settings`.

**PA entrypoint (`unified_pa_entrypoint.py`):**
- Intent routing: `_detect_intent_and_route(message)` returns `(intent, tool_name)` tuple
- Order matters: new intent blocks must go BEFORE existing ones that share keywords (e.g., "system" overlap)
- `import re` inside elif branches: Python function-level scoping means each branch that uses `re` must have its own `import re`
- Tool results: `ToolResult` dataclass with `.ok`, `.result`, `.trace_id`
- Enrichment map: maps intent -> list of enrichment services (empty list = pure data, no LLM overlay)

**Tool dispatcher (`tool_dispatcher.py`):**
- Registration: `self.register("name", self._handle_method)` in `__init__`
- Handler signature: `(tool_name, payload, user_id, trace_id) -> Dict`
- Singleton: `get_tool_dispatcher()` at file end
- Each data source wrapped in try/except for graceful degradation

**Model field gotchas (verified):**
- `LearningPattern`: use `success_when_applied` (NOT `times_successful`)
- `FailureDetection`: use `detected_at` (NOT `created_at`)
- `SignalCluster`: use `detected_at`, `strength`, `status`
- `AgentDecisionSummary`: does NOT have a `confidence` field
- `SelfBlog`: `quality_score`, `novelty_score`, `structure_score`, `publish_ready`, `gate_notes`
- `Initiative`: `updated_at`, `last_activity_at`, `impact_score`, `urgency`, `confidence`, `revenue_potential`

**Git workflow:** Pre-commit hook blocks direct commits to `main`. Must use feature branches, PRs, then merge.

**Railway deployment:** `railway up --detach` or auto-deploys from main. Verify with `railway run python -c "..."`. Logs: `railway logs -n 30`.

---

## Key Files Reference

### Session 969b Files
| File | Purpose |
|------|---------|
| `core/services/tool_dispatcher.py` | 3 telemetry tool handlers (recent_activity, system_health, error_summary) |
| `core/services/unified_pa_entrypoint.py` | Intent routing, enrichment map, aliases, payload builders for telemetry |

### Session 969 Files
| File | Purpose |
|------|---------|
| `frontend/src/pages/workspace/tabs/OrchestrationTab.tsx` | Metrics bar, cost, HiveMind sessions, execution detail overhaul |
| `core/services/tool_dispatcher.py` | ORM field fix: `times_successful` -> `success_when_applied` |
| `core/tasks.py` | Diversified blog fallback topics (v1 + v2) |

### PA Tool System
| File | Purpose |
|------|---------|
| `core/services/unified_pa_entrypoint.py` | 89 PA tools, intent routing, enrichment pipeline |
| `core/services/pa_intelligence_enricher.py` | 5 enrichment services wired to PA |

---

## Recent Session History

| Session | Focus | PRs |
|---------|-------|-----|
| **969b** | PA Live Telemetry — 3 tools for real-time system self-awareness | #974 |
| **969** | Orchestration enrichment, execution detail fix, ORM fix, blog diversity | #971, #972 |
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

**Session 970 Focus: Your choice! See "What Could Come Next" above.**
