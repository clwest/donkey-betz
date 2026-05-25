<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Personal Assistant (PA) System

The PA is the platform's conversational interface — a single `UnifiedPAEntrypoint` that handles all user queries. **Session 1036: Replaced keyword routing with GPT-5.2 function calling.** The LLM now sees **106 tool schemas** and **171 registered handlers**, enabling multi-tool turns and natural follow-ups. The current runtime inventory is the source of truth for counts. Session 1100: `run_agent` expanded to 77 agents across 12 domains; added `cockpit_tool` (Celery ops) and `narrative_tool` (drift analysis); expanded intelligence/work/content/governance gateways. Session 1035-W2: added proactive_tool, distribution_tool, calendar_tool, experiment_tool, podcast_tool, campaign_tool, audit_tool, conceptforge_tool, profile_tool, self_awareness_tool, ats_tool.

## Architecture

Three files handle everything:
- `core/services/unified_pa_entrypoint.py` — Agentic loop, context building, enrichment orchestration
- `core/services/tool_dispatcher.py` — 171 tool handlers with guaranteed structured responses (ToolResult)
- `core/services/pa_tool_schemas.py` — 101 OpenAI function-calling tool schemas + enrichment map

Rigby now has explicit `global` and `workspace` modes. Workspace mode activates only from explicit workspace context (`workspace_id`, `AssistantProfile.workspace`, or workspace-aware UI context). Do not infer workspace scope from the message text alone.

### Flow (Function Calling — Active)

```
message -> _build_context() [profile, knowledge, stats, docs — each with 5s timeout]
        -> _build_messages_array() [system prompt + conversation history + user msg]
        -> GPT-5.2 Responses API with 106 tool schemas
           -> if tool_call(s): execute via ToolDispatcher -> feed result back -> loop (max 5 iterations)
           -> if text response: done
        -> enrichment (intent inferred from tool names via TOOL_TO_INTENT_MAP)
        -> return PAResponse
```

**Feature flag:** `PA_USE_FUNCTION_CALLING=true` (env var, enabled on Railway). When `false`, falls back to the legacy keyword router.

### Flow (Legacy Keyword Router — Fallback)

```
message -> _detect_intent_and_route() [506 lines of if/elif keyword matching]
        -> _build_tool_payload() [590 lines intent-specific extraction]
        -> ToolDispatcher.execute()
        -> enrichment (15s timeout)
        -> LLM formats response
```

## Tool Schemas (pa_tool_schemas.py)

`PA_TOOL_SCHEMAS` is a list of OpenAI function-calling tool definitions. Each tool has:
- `name` — matches ToolDispatcher handler name (e.g., `agent_introspection_tool`)
- `description` — natural language routing signal (GPT-5.2 uses this to decide when to call)
- `parameters` — JSON schema with action enums, optional filters, limits

`TOOL_TO_INTENT_MAP` maps tool names back to canonical intents for the enrichment pipeline.

**Key tools (6 gateways — Session 1079 consolidation):**
- `governance_tool` — boardroom, attention items, decisions, triage (absorbs `boardroom_tool`, `human_decisions_tool`)
- `work_tool` — initiatives, stages, action items (absorbs `initiative_tool`)
- `content_tool` — content review, blog generation, deliverables (absorbs `content_review_tool`, `generate_blog_tool`, `deliverables_tool`)
- `intelligence_tool` — stocks, sports, legislation, RAG/KB, spiders (absorbs `stock_intelligence_tool`, `sports_betting_tool`, `legislation_tool`, `rag_query_tool`, `spider_data_tool`)
- `ops_tool` — SLO status, failure signatures, version, migration report (absorbs `system_health_tool`, `error_summary_tool`)
- `studio_tool` — media management (images, video, audio)
- Agent delegation: `run_agent` meta-tool with `agent_name` enum → routes to actual agent tool
- Telemetry: `agent_introspection_tool`, `status_snapshot_tool`, `check_resource_budget`, `pipeline_orchestrator_tool`, `task_breakdown_tool` (summary/drilldown with configurable time window)
- Other: `brainstorm_tool` (4 actions: list/search/details/stats — `list` supports offset/limit pagination up to 200 for bulk export)

## Enrichment Pipeline

Eight intelligence services inject context before the LLM generates analysis. Each intent maps to specific services:

| Service | Source | Fires For |
|---------|--------|-----------|
| intelligence_enricher | PAIntelligenceEnricher | work_tool, governance_tool, ops_tool, reasoning, pilots, gates, system_overview |
| blog_performance | BlogPerformanceContextBuilder | content_tool |
| domain_context | DomainContentContextBuilder (9 domains) | content_tool, opportunities, predictions, intelligence_tool |
| spider_trends | SpiderContextBuilder | content_tool, opportunities, predictions, learning_patterns, intelligence_tool |
| advisor | AdvisorContextBuilder (25 advisors) | opportunities, reasoning |
| strategic_memory | StrategicMemoryService | work_tool, governance_tool, execution_history, reasoning |
| proactive_intelligence | ProactiveIntelligenceService | content_tool, opportunities, intelligence_tool, system_overview |
| platform_briefing | PlatformIntelligenceBriefingService | system_overview, execution_history |

**Relevance gating:** Content-related intents skip the gate. All others require 15% keyword overlap to avoid irrelevant injection.

**Enrichment caps (Session 1006):** 1500-2000 chars per section. Raised from 300-600 which was discarding 85-95% of data.

## Context Building (_build_context)

Session 1035: All DB-touching steps have `asyncio.wait_for` timeouts to prevent Postgres connection hangs (134s observed on Railway):

| Step | Timeout | Graceful degradation |
|------|---------|---------------------|
| Profile load (ExtendedUserProfile) | 5s | PA works without profile context |
| Knowledge injection | 3s | PA works without system knowledge |
| System stats | 5s | PA uses hardcoded defaults |
| Docs context (RAG) | 5s | PA works without document context |
| Conversation history (sync, __init__) | 5s | `SET LOCAL statement_timeout` |

## Async Processing (Celery)

PA queries run asynchronously to avoid Railway's ~30s proxy timeout:

1. `POST /api/pa/chat/` dispatches `process_pa_chat_task` to the dedicated `pa` queue
2. Returns `{task_id}` immediately
3. Frontend polls `GET /api/pa/chat/status/<task_id>/` every 2s
4. Celery task runs with `time_limit=300s`, `soft_time_limit=280s`
5. Uses `new_event_loop()` + `run_until_complete()` (not `async_to_sync`, which deadlocks)

**Production latency (function calling):** Single tool ~6s, 5-tool operator report ~16s, multi-turn follow-up ~6s (cached input discount).

**Compatibility note:** `POST /api/pa/chat/` is the canonical web entrypoint. `/api/assistant/chat/` and `/api/v1/assistant/chat/` are legacy compatibility shims only.

## Conversation History

`ChatConversation` model with `conversation_id`, `session_title`, auto-title generation via LLM on first message.

Workspace context is injected explicitly, not guessed. When workspace mode is active, `workspace_id` is promoted into the PA request context so workspace-scoped tools and history stay aligned with the selected workspace.

**Session 1030: DB-backed memory.** `_load_conversation_history_from_db()` loads last 10 `ChatConversation` rows on PA init, so conversation context survives Celery worker recycling (`max_tasks_per_child`).

**Session 1036: Tool call metadata.** `ChatConversation.metadata` now stores `tool_calls` (list of `{name, arguments, call_id, ok}`) and `response_id` (for GPT-5.2 `previous_response_id` caching). History reconstruction includes these for multi-turn function calling context.

## Cost (GPT-5.2)

| Component | Tokens | Cost/turn |
|-----------|--------|-----------|
| Tool schemas (50+) | ~5,000 input | $0.009 |
| System prompt | ~2,500 input | $0.004 |
| Conversation history (10 turns) | ~3,000 input | $0.005 |
| Tool results (1-2 calls) | ~1,000 input | $0.002 |
| Output | ~500 output | $0.007 |
| **Total (1-tool turn, first msg)** | **~12K** | **~$0.027** |
| **Total (follow-up, cached)** | **~12K** | **~$0.009** |

With `previous_response_id`, follow-up turns hit the 90% cached input discount ($0.18/1M vs $1.75/1M).

## Key Tool Actions

**governance_tool:** inbox, attention_list, attention_approve, attention_ignore, attention_lookup, decisions_list, decisions_stats, decision_create, decision_decide, decision_promote, decision_reject, triage_batch
**work_tool:** initiative_list, initiative_detail, initiative_create, initiative_promote, stage_detail, stage_approve, action_item_list, action_item_update
**content_tool:** content_stats, content_list, content_detail, content_search, content_recent, content_approve, content_reject, generate_blog, deliverable_list, deliverable_detail, deliverable_search, deliverable_save, deliverable_create, deliverable_stats
**intelligence_tool:** overview, briefs, search (source=kb/spider), stocks_alerts, stocks_predictions, stocks_sec_filings, sports_predictions, sports_arbs, sports_wagers, sports_record_wager, legislation_search, legislation_summary, kb_ingest
**ops_tool:** version, slo_status, failure_signatures, tool_migration_report
**studio_tool:** media_list, media_stats
**agent_introspection_tool:** stats (aggregates + disjoint taxonomy), list (top-50 preview), details, capabilities
**pipeline_orchestrator_tool:** status (initiatives by stage + by_status breakdown)
**http_smoke_test:** Run endpoint smoke tests against Railway prod or localhost. Three built-in suites: `cockpit_health` (18 GET checks), `cockpit_incidents_crud` (8-step CRUD lifecycle with negative tests, dependency tracking, and variable capture), `pa_tools_smoke` (20 checks across boardroom, initiatives, celery, agents, spiders, learning patterns, manifest, deliverables, opportunities, pilots, Redis queues, and media — with initiative detail chaining). Runner features: `test_run_id` auto-injected per run for tracing, `depends_on` step dependencies with skip semantics, early-fail on unresolved `{{vars}}`, per-step `headers` support. Assertions: `status`, `has_key`, `json_path` (eq/gte/exists), `type`. Auth via `PA_API_TOKEN` env var on celery-pa. Safety: SSRF allowlist (*.railway.app, localhost), 50-step cap, 1MB response cap, 20s timeout. Code: `core/tools/http_smoke_test.py`.

## Agent Introspection Taxonomy (Session 1035)

Disjoint categories that sum to `router_routable_total`:
- `blocked_agents` (2): AudioAgent, CodeGeneratorAgent — hard-blocked, tasks rejected
- `rerouted_agents` (8): COOAgent, CTOAgent, etc. — tasks redirected to specialists
- `fully_enabled_count` (72): everything else
- `reconciliation`: "2 blocked + 8 rerouted + 72 fully_enabled = 82 total"
