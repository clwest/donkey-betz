# Personal Assistant (PA) System

The PA is the platform's conversational interface — a single `UnifiedPAEntrypoint` that routes user queries through 36 intents to 50 tools, enriches responses with 6 intelligence services, and returns structured data + LLM analysis.

## Architecture

Two files handle everything:
- `core/services/unified_pa_entrypoint.py` — Intent detection, enrichment orchestration, response formatting
- `core/services/tool_dispatcher.py` — 50 tool handlers with guaranteed structured responses

## Intent Routing

`_detect_intent_and_route(message)` checks keywords top-to-bottom and returns `(intent, tool_name)`. Order matters — earlier intents take priority.

| Priority | Intent | Routes To | Triggers |
|----------|--------|-----------|----------|
| 1 | boardroom | boardroom_tool | decision, attention, approve, triage |
| 2 | recent_activity | recent_activity_tool | what's been going on, catch me up |
| 3 | system_health_check | system_health_tool | how's the system, anything down |
| 4 | surgical_moves_status | surgical_moves_status_tool | deliberation status, verification |
| 5 | error_summary | error_summary_tool | any errors, what failed |
| 6 | system_overview | status_snapshot_tool | how is everything, executive summary |
| 7 | system_health | get_body_vitals | body vitals, organ health |
| 8 | predictions | predictions_tool | predict, forecast |
| 9 | pilots / gates | pilots_tool / gates_tool | experiment, pilot, gates |
| 10 | user_feedback | (direct response) | not working, broken, bug |
| 11 | reasoning | reasoning_engine_tool | analyze deeply, reflect on |
| 12 | opportunities | opportunity_manager_tool | opportunity, job, gig, income |
| 13 | content_review | content_review_tool | show blogs, blog titled, blog accuracy |
| 14 | brainstorming | brainstorm_tool | brainstorm, panel, think tank |
| 15 | image/video creation | agent tools | create image, generate video |
| 16 | content_writing | content_writer_agent | write, draft, compose |
| 17 | research | web_search | search, find, research, trending |
| 18 | agent_execution | universal_agent_tool | run agent, execute agent |
| 19 | initiatives | initiative_tool | initiative, project, pipeline (runs BEFORE boardroom) |
| 20 | crypto_price | spider_data_tool | btc, bitcoin, ethereum, crypto, coin price, how much is |
| 21 | stock_intelligence | stock_intelligence_tool | stock, market brief, SEC filing |
| 22 | spider_data | spider_data_tool | spider, crawled, news feed |
| 23 | execution_history | execution_history_tool | agent history, agents been doing, agent conversations, deliberations |
| 24 | learning_patterns | learning_patterns_tool | learning, patterns |
| 25 | feedback | feedback_tool | feedback queue, bug reports |
| 26 | revenue | revenue_tracker_tool | revenue, earnings, financial |
| 27 | task_management | task_manager_tool | my tasks, task list |
| 28 | workspace | workspace_tool | workspace, workspace files |
| 29 | budget | check_resource_budget | budget, token usage, api cost |
| 30 | system_alerts | get_system_alerts | active alerts, warnings |
| 31 | ml_analysis | ml_analysis | ml status, decision pattern |
| 32 | pipeline_status | pipeline_orchestrator_tool | pipeline status, stage breakdown |
| 33 | capabilities | (direct response) | what can you do, your capabilities (narrowed in 988) |
| 34 | general | (direct LLM response) | fallback for everything else |

## Enrichment Pipeline

Eight intelligence services inject context before the LLM generates analysis. Each intent maps to specific services:

| Service | Source | Fires For |
|---------|--------|-----------|
| intelligence_enricher | PAIntelligenceEnricher | initiatives, boardroom, system_health, reasoning, pilots, gates, system_overview |
| blog_performance | BlogPerformanceContextBuilder | content_review |
| domain_context | DomainContentContextBuilder (9 domains) | content_review, opportunities, predictions, stock_intelligence, spider_data |
| spider_trends | SpiderContextBuilder | content_review, opportunities, predictions, learning_patterns, stock_intelligence |
| advisor | AdvisorContextBuilder (25 advisors) | opportunities, reasoning |
| strategic_memory | StrategicMemoryService | initiatives, boardroom, execution_history, reasoning |
| proactive_intelligence | ProactiveIntelligenceService | content_review, opportunities, stock_intelligence, system_overview |
| platform_briefing | PlatformIntelligenceBriefingService | system_overview, execution_history |

**Relevance gating:** Content-related intents skip the gate. All others require 15% keyword overlap to avoid irrelevant injection.

**Enrichment caps:** Each section is truncated (300-600 chars) to control token usage. `proactive_intelligence` and `platform_briefing` capped at 500 chars.

## Async Processing (Celery)

PA queries run asynchronously to avoid Railway's ~30s proxy timeout:

1. `POST /api/pa/chat/` dispatches `process_pa_chat_task` to the dedicated `pa` queue
2. Returns `{task_id}` immediately
3. Frontend polls `GET /api/pa/chat/status/<task_id>/` every 2s
4. Celery task runs with `time_limit=300s`, `soft_time_limit=280s`
5. Uses `new_event_loop()` + `run_until_complete()` (not `async_to_sync`, which deadlocks)

**Timeouts:** 15s enrichment pipeline, 60s per LLM call.

**Production latency:** "hello" 3s, errors 3.4s, health 12.7s, overview 18.2s, blogs 46.6s, initiatives 64s.

## Response Format

1. **Structured data first** — Always shown, contains IDs for user action
2. **LLM analysis second** — Max 3-5 bullets of insight, not data repetition
3. **Intent-specific directives** — Each intent has a specialized analytical prompt (e.g., boardroom focuses on triage strategy, content_review on quality scores)

## Conversation History

`ChatConversation` model with `conversation_id`, `session_title`, auto-title generation via LLM on first message. ChatGPT-style sidebar in GlobalPADock and CommandCenterPage.

## Key Tool Actions

**boardroom_tool:** stats (top 10 critical/high items), list_attention, list_decisions, approve/ignore/promote/reject
**content_review_tool:** list (by status/type), read (full blog + accuracy analysis), publish, archive, revise (blog revision via EditorAgent + PublishGate re-score). Publish/archive/revise actions record feedback to the originating agent via `_record_content_feedback()` → AgentMemory + UserAgentLearning (Session 990).
**initiative_tool:** list, stats, detail, audit (Jaccard similarity clustering), create
**stock_intelligence_tool:** overview, briefs, alerts, predictions, sec_filings
**spider_data_tool:** recent, by_type, summary

## Triage Mode

Interactive bulk review: "triage attention" activates step-by-step item review with approve/ignore/skip/promote/reject commands and final summary stats.
