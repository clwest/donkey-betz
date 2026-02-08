# Session 971 - Start Here

**Previous Session:** 970 (Surgical Moves Verification + ToolCallRecord Activation + Attention Coverage)
**Date:** February 8, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **52 ACTIVE INITIATIVES** (cleaned from 568) | **Risk-Aware RAG: COMPLETE** | **Doc Classification: 562 DOCS** | **Boardroom ML: ACTIVE** | **Unified PA: ANALYTICAL ADVISOR** | **Voice System: COMPLETE** | **Learning Loop: REFINED** | **Agent Provenance: 26+ AGENTS** | **RAG Observability UI: COMPLETE** | **PA Intelligence Enrichment: ACTIVE** | **Phase 0-4 Deliberation: COMPLETE** | **Content Deliberation Pipeline: ACTIVE** | **Insight De-dup Bundling: ACTIVE** | **Orchestration Enrichment: ACTIVE** | **Blog Diversity: ACTIVE** | **PA Live Telemetry: ACTIVE** | **Surgical Moves Verification: ACTIVE** | **ToolCallRecord: LIVE** | **Attention Coverage: 7 SECTIONS**

---

## Session 970 Summary (Just Completed)

### Surgical Moves Verification + Visibility (PR #977)
Made Sessions 960-963 Surgical Moves Phases 0-3 visible, testable, and demoable:

- **Management command** `verify_surgical_moves` — runs real 4-turn debate then prints structured pass/warn/fail report; `--mode=report-only` checks existing sessions without LLM spend
- **PA tool** `surgical_moves_status_tool` — intent routing for "deliberation status", "what deliberations", etc. Returns structured session/contract/evidence data
- **API endpoint** `GET /api/deliberation/sessions/<uuid>/verification-report/` — enriched JSON with checks array
- **Frontend** `SurgicalMovesPanel` + `VerificationReportModal` in Orchestration Monitor tab

### ToolCallRecord Activation (PR #978)
Fixed the wiring gap where `_execute_and_record_tool_call()` existed since Session 861 but was never called by any agent.

- **`__init_subclass__`** in BaseAgent auto-wraps every subclass's `_execute_tool_call` with recording
- **Zero agent files touched** — all 50+ agents now produce audit trail automatically
- **Verified on Railway:** 6 rows in first 3 minutes (ResearchAgent: web_search, spider_query, analyze_trends, reddit_search; SystemIntelligenceAgent: get_system_attention x2)

### Expanded Attention Coverage (PR #978)
Added 2 new sections to SystemStateAggregator (now 7 total):

- **Deliberation health** — stuck sessions (>1h in_progress), contractless completions
- **Signal cluster freshness** — stale active clusters (>48h), untriggered high-strength clusters

### Production System Review
Verified SystemIntelligenceAgent report against Railway production DB:
- 549 stale suggestions (accurate)
- Celery running (48,543+ periodic task runs, results in Redis by design)
- 47 completed DeliberationSessions, 87 ContractRecords
- 18 SignalClusters, 615 fresh SpiderData/24h, 240 SelfBlogs/24h

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
| PA Tools | 90 (was 89, +surgical_moves_status) |
| Tool Dispatcher Handlers | 48 |
| Attention Sections | 7 (command_center, autonomous, research, pending_review, body_systems, deliberation, signal_clusters) |
| LLM Providers | 6 (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini) |

---

## Known Issues / Open Items

### ToolCallRecord Now Populating
Data is flowing but no analytics dashboard exists yet. Consider building tool usage reports: by agent, latency percentiles, error rates, most-used tools.

### Celery Result Backend = Redis (Intentional)
`CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'` — results are NOT in `django_celery_results_taskresult`. This is by design. Only switch to `django-db` if task result visibility in Django admin is needed.

### FailureSignature Table Empty
The diagnostic pipeline (Session 856) has FailureSignature/FailureDetection models but 0 records in production. May need activation similar to the ToolCallRecord fix.

---

## What Could Come Next

### ToolCallRecord Analytics
Now that data flows, build dashboards: tool usage by agent, latency percentiles, error rates, most-used tools. Could be a PA tool or frontend panel.

### Initiative Staleness Check
Add `_get_initiative_items()` to SystemStateAggregator for initiatives with no activity in 7+ days. 125 active in production — some may be stale.

### FailureSignature Activation
Investigate why FailureSignature has 0 records. The diagnostic pipeline (Session 856) may have the same "defined but never called" pattern as ToolCallRecord did.

### PA Response Formatting for Telemetry
Intent-specific LLM directives for telemetry tools (e.g., "Summarize concisely, highlight anomalies"). Currently tools return structured data formatted generically.

### Auto-Revision Loop
If deliberation pipeline returns REVISE verdict, loop through reviewer feedback automatically instead of requiring manual re-trigger.

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

**BaseAgent `__init_subclass__` (Session 970):**
- Auto-wraps `_execute_tool_call` in subclasses with ToolCallRecord recording
- Uses `_orig` default arg to capture original method per-class (avoids closure bug)
- Recording in `finally` with bare `except: pass` — can never break agent execution
- Base class method is NOT wrapped (only subclasses that define `_execute_tool_call` in their `__dict__`)

**Model field gotchas (verified):**
- `SignalCluster`: in `core.models_signal_intelligence` (NOT `models_unified_system`), use `detected_at` (NOT `updated_at`)
- `LearningPattern`: use `success_when_applied` (NOT `times_successful`)
- `FailureDetection`: use `detected_at` (NOT `created_at`)
- `AgentDecisionSummary`: does NOT have a `confidence` field
- `SelfBlog`: `quality_score`, `novelty_score`, `structure_score`, `publish_ready`, `gate_notes`
- `Initiative`: `updated_at`, `last_activity_at`, `impact_score`, `urgency`, `confidence`, `revenue_potential`

**Git workflow:** Pre-commit hook blocks direct commits to `main`. Must use feature branches, PRs, then merge.

**Railway deployment:** Auto-deploys from main. Verify with `railway deployment list`. Logs: `railway logs -n 50`.

---

## Key Files Reference

### Session 970 Files
| File | Purpose |
|------|---------|
| `core/management/commands/verify_surgical_moves.py` | CLI verification of Surgical Moves Phases 0-3 |
| `core/agents/base_agent.py` | `__init_subclass__` ToolCallRecord recording wrapper |
| `core/services/system_state_aggregator.py` | 2 new attention sections (deliberation + signal clusters) |
| `core/services/tool_dispatcher.py` | `surgical_moves_status_tool` handler |
| `core/services/unified_pa_entrypoint.py` | Intent routing for surgical moves status |
| `core/views_deliberation.py` | Verification report API endpoint |
| `frontend/src/pages/workspace/tabs/OrchestrationTab.tsx` | SurgicalMovesPanel + VerificationReportModal |

### PA Tool System
| File | Purpose |
|------|---------|
| `core/services/unified_pa_entrypoint.py` | 90 PA tools, intent routing, enrichment pipeline |
| `core/services/pa_intelligence_enricher.py` | 5 enrichment services wired to PA |

---

## Recent Session History

| Session | Focus | PRs |
|---------|-------|-----|
| **970** | Surgical Moves Verification + ToolCallRecord activation + Attention Coverage | #977, #978 |
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

**Session 971 Focus: Your choice! See "What Could Come Next" above.**
