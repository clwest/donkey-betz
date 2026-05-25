<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For the runtime-verified PA tool registry see [`docs/PA_TOOL_AUDIT.md`](/docs/PA_TOOL_AUDIT.md) (autogen via `python manage.py build_pa_tool_audit`).
> **Note:** content may be stale (last refreshed 2026-03-01) — this guide is canonical for "WHEN user says X, use tool Y" routing patterns. The HOW (action names, params) may have shifted; verify against current code or `PA_TOOL_AUDIT.md` before relying on specifics.

# PA Tool Routing Guide (1-page)

**v1.1 — 2026-03-01**
**Canonical location:** `docs/tools/pa-tool-routing-guide.md`

When the user says... → use this tool → with this action → key params

> **Rule:** If a tool has `actions = null`, call it directly with its parameters, or delegate via `run_agent` / `universal_agent_tool` / `persona_tool` (for specialist agents/personas).

## Governance / Approvals
- "What needs my attention?" → `boardroom_tool` → `list_attention` → optional `urgency`, `item_type`
- "Approve attention item X" → `boardroom_tool` → `approve_attention` → `id`
- "Ignore attention item X" → `boardroom_tool` → `ignore_attention` → `id`
- "List pending decisions" → `boardroom_tool` → `list_decisions` → optional `decision_type`
- "Promote decision X" → `boardroom_tool` → `promote_decision` → `id`
- "Reject decision X" → `boardroom_tool` → `reject_decision` → `id`
- "Pending human decision items" → `human_decisions_tool` → `list` → optional `limit`
- "Decide on human decision item X" → `human_decisions_tool` → `decide` → `id`, `decision`

## Initiatives / Projects
- "Show initiatives" → `initiative_tool` → `list` → optional `status`, `owner`, `limit`
- "Create an initiative" → `initiative_tool` → `create` → `name`, `description`
- "Initiative details" → `initiative_tool` → `details` → `id`
- "Action items for INIT-42" → `initiative_tool` → `action_items` → `id`
- "Break down initiative X" → `task_breakdown_tool` → `summary` → initiative id
- "Promote initiative to active" → `initiative_tool` → `promote` → `id`

## Deliverables / Library
- "Show my saved deliverables" → `deliverables_tool` → `list` → optional `is_saved=true`
- "Search deliverables for X" → `deliverables_tool` → `search` → `query`
- "Save this as a deliverable" → `deliverables_tool` → `create` → `title`, `content`
- "Clean up duplicate deliverables" → `deliverables_tool` → `cleanup` → `strategy='duplicates'`, `dry_run=true`

## RAG / Docs / Ingestion
- "Search knowledge base for X" → `rag_query_tool` → `search` → `query`
- "Search only internal docs" → `rag_query_tool` → `search` → `query`, `source_filter='internal_only'`
- "Ingest this URL" → `rag_query_tool` → `ingest` → `url`
- "Show staged documents" → `rag_query_tool` → `staged`
- "Promote document X" → `rag_query_tool` → `promote` → `document_id`
- "How many docs/embeddings?" → `rag_query_tool` → `stats`

## Spiders / External Data
- "Recent spider data" → `spider_data_tool` → `recent`
- "Search spider data for X" → `spider_data_tool` → `search` → `query`
- "Compare us to competitor X" → `competitor_comparison_tool` → `compare` → `competitor_name`, `auto_research=true`

## Agent Execution / Health
- "Recent agent runs" → `execution_history_tool` → `recent`
- "Agent errors" → `error_summary_tool` → `summary`
- "What has agent X learned?" → `learning_patterns_tool` → `recent` → `agent_name`
- "Run the content writer" → `run_agent` → `agent_name='content_writer'`
- "What agents exist?" → `agent_introspection_tool` → `list`

## Markets / Sports / Revenue
- "Stock brief" → `stock_intelligence_tool` → `brief`
- "Today's game predictions" → `sports_betting_tool` → `predictions`
- "Record a wager" → `sports_betting_tool` → `record_wager` → game, amount, pick
- "Revenue this month" → `revenue_tracker_tool` → `summary`
- "ML model performance" → `ml_analysis` → `stats`

## Creative Studio
- "Generate an image of X" → `studio_tool` → `generate_image` → `prompt`
- "Generate a video" → `studio_tool` → `generate_video` → `prompt`
- "Check job status" → `studio_tool` → `job_status` → `job_id`
- "List my media" → `media_tool` → `list`
- "Render in DaVinci" → `davinci_tool` → `render`

## Workspaces
- "List workspaces" → `workspace_tool` → `list`
- "Create a workspace" → `workspace_tool` → `create` → `name`

## Cost / Budget
- "API costs this week" → `cost_telemetry_tool` → `summary`
- "Cost by model" → `cost_telemetry_tool` → `by_model`
- "Am I over budget?" → `check_resource_budget`

## Platform / Ops
- "System health" → `system_health_tool` → (direct call, no action)
- "Body vitals" → `get_body_vitals`
- "Quick status" → `status_snapshot_tool` → `summary`
- "Active alerts" → `get_system_alerts`
- "Scheduled tasks" → `scheduled_tasks_tool` → `list`
- "Smoke test endpoints" → `http_smoke_test`
- "DB health" → `db_health_tool` → `overview`
- "What routes exist?" → `platform_awareness_tool` → `list_routes`

## Ideas / Strategy
- "Brainstorm about X" → `brainstorm_tool` → `start` → `topic`
- "Show agent dreams" → `dream_tool` → `list`
- "Deep analysis of X" → `reasoning_engine_tool` → `analyze`
- "Research X and create a plan" → `research_and_create_tool` → `research`

## Legal / Legislation
- "Track legislation about X" → `legislation_tool` → `search` → `query`
- "Draft a legal doc" → `legal_doc_drafter_agent` (async — returns task_id)

## Conversations / Learning
- "Show recent conversations" → `conversation_tool` → `search`
- "Platform activity feed" → `recent_activity_tool` → (direct call) → `limit`
- "Store this learning" → `learning_tool` → `store`
