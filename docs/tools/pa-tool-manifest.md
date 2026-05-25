<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For the runtime-verified PA tool registry see [`docs/PA_TOOL_AUDIT.md`](/docs/PA_TOOL_AUDIT.md) (autogen via `python manage.py build_pa_tool_audit`).
> **Note:** content may be stale (last refreshed 2026-03-01) — this manifest covers WHAT tools exist; the autogen `PA_TOOL_AUDIT.md` is the runtime-verified registry. Tools added since 2026-03-01 may be missing here. Refresh by syncing against the autogen audit.

# PA Tool Manifest (Canonical)

**Manifest v2 — Last updated: 2026-03-01**
**Canonical location:** `docs/tools/pa-tool-manifest.md`

This is the canonical reference for what tools the PA (and other platform agents) can call on the Donkey Betz Unified AI Platform.

## How to use this manifest
- Pick the tool that matches the user intent.
- Choose the appropriate **action** (if the tool is action-based).
- Provide parameters exactly as required by the tool schema.

## Important constraints
- **Do not rely on in-chat tool enumeration** (it can truncate). Treat this document as canonical.
- If you suspect a tool is missing/out-of-date, ask the PA to refresh via `platform_awareness_tool(action='tool_registry')` and update this manifest.

## How to interpret tools where `actions = null`
Some tools do not expose an `action` enum. This is normal and does **not** mean the tool is incomplete.

### Pattern 1: Single-purpose tools (no action router)
These tools do one thing and are called directly with their required parameters.
- Examples: `web_search(query)`, `generate_blog_tool(topic, style)`, `get_body_vitals()`.

### Pattern 2: Agent delegation tools (the "action" is the agent/persona + task)
These tools dispatch work to a specialist; you provide *who* + *what to do*.
- `run_agent(agent_name, task)` — delegate to a named specialist agent.
- `universal_agent_tool(task, agent_name?)` — route to best-fit agent (or specify one).
- `persona_tool(action='invoke', persona_name, task)` — invoke a specific persona.

### Pattern 3: Utility / wrappers
Some tools may appear with `actions=null` in one view but still have structured parameters. Always follow the schema.

**Best practice:** If `actions` is present → choose from the enum. If `actions` is null → read the parameter schema and call directly.

---

## A) Governance & Human-in-the-loop

### `boardroom_tool`
**For:** pending attention items, draft decisions, approvals/rejections.
**Actions:** `stats`, `list_attention`, `list_decisions`, `approve_attention`, `ignore_attention`, `promote_decision`, `reject_decision`, `get_triage_batch`, `list_unclassified`, `classify_suggest`, `classify_apply`, `classify_apply_batch`, `lookup`, `create_attention`.

### `human_decisions_tool`
**For:** items requiring explicit human decision.
**Actions:** `list`, `stats`, `decide`, `create`.

---

## B) Initiatives / Projects

### `initiative_tool`
**For:** initiative pipeline (5-stage) listing, details, action items, promotion, creating initiatives.
**Actions:** `list`, `stats`, `details`, `action_items`, `stage_document`, `promote`, `start_action_item`, `complete_action_item`, `create`.

### `workspace_tool`
**For:** dev/work organization workspaces.
**Actions:** `list`, `status`, `create`.

### `task_manager_tool`
**For:** task/opportunity tracking linked to initiatives.
**Actions:** `list`, `stats`, `detail`, `create`, `update`, `delete`, `assign`.

### `task_breakdown_tool`
**For:** AI-powered initiative decomposition into subtasks.
**Actions:** `summary`, `drilldown`.

---

## C) Content, Deliverables, Blogs

### `deliverables_tool`
**For:** CRUD + bookmarking deliverables.
**Actions:** `list`, `search`, `detail`, `save`, `unsave`, `stats`, `create`, `update`, `delete`, `cleanup`.
**Notes:** `cleanup` supports `duplicates|orphans|low_quality` and should be run with `dry_run=true` first.

### `content_review_tool`
**For:** review/approve/reject deliverables/blogs.
**Actions:** `list`, `search`, `recent`, `details`, `approve`, `reject`, `stats`.

### `generate_blog_tool`
**For:** generate a blog post via deliberation pipeline.
**Params:** `topic`, `style`. Async — returns task_id.

---

## D) RAG / Knowledge Base

### `rag_query_tool`
**For:** semantic search, ingestion, staged doc review, promotion.
**Actions:** `search`, `stats`, `list_documents`, `ingest`, `promote`, `staged`.
**Notes:** `search` supports `source_filter` (all/internal_only/external_only). `promote` moves staged→promoted. `staged` lists docs awaiting review.

### `conversation_tool`
**For:** search/retrieve/summarize past PA conversations; pin durable memories.
**Actions:** `get`, `search`, `summary`, `pin_memory`.

### `learning_tool`
**For:** platform learning & knowledge base storage.
**Actions:** `query`, `store`, `list`, `stats`.

---

## E) Spiders / External Data

### `spider_data_tool`
**For:** browse/search spider-collected datasets.
**Actions:** `recent`, `search`, `stats`, `by_spider`, `by_category`, `trigger`.

### `competitor_comparison_tool`
**For:** run competitor comparison reports.
**Actions:** `compare`, `list`, `detail`.
**Notes:** Async — dispatches to celery-long-running. Supports `auto_research=true`.

---

## F) Agents & Workflow Delegation

### `run_agent`
**For:** delegate a task to a specialized agent (creative, strategy, research, etc.).
**Params:** `agent_name`, `task`. Available agents include: content_writer, legal_doc_drafter, competitor_analysis, customer_research, brand_strategy, content_strategy, marketing_strategy, image_editing, video_editing, three_d_generation, character_training, workflow_orchestration, coleadership, resolve_agent.

### `persona_tool`
**For:** invoke one of 139+ specialized personas across categories.
**Actions:** `list`, `invoke`.

### `universal_agent_tool`
**For:** route an arbitrary task to a specific agent or auto-route.
**Actions:** `run`, `status`, `list`.

### `pipeline_orchestrator_tool`
**For:** multi-stage pipeline execution.
**Actions:** `status`, `run`, `history`, `cancel`.

### `workflow_run_tool`
**For:** run/monitor workflow instances.
**Actions:** `start`, `status`, `list`, `cancel`.

---

## G) Platform Observability / Reliability

### `execution_history_tool`
**For:** view agent execution history + full outputs.
**Actions:** `recent`, `by_agent`, `stats`, `failures`, `detail`.

### `error_summary_tool`
**For:** error counts and detailed errors.
**Actions:** `summary`, `detailed`.

### `system_health_tool`
**For:** platform system health (body systems, workers, DB).
**Params:** `verbose` (boolean).

### `get_body_vitals`
**For:** 9 body-system health scores (HEART, LUNGS, etc.).
**Params:** none.

### `status_snapshot_tool`
**For:** quick platform snapshot for briefings.
**Actions:** `full`, `summary`.

### `get_system_alerts`
**For:** active alerts and warnings.
**Params:** none.

### `scheduled_tasks_tool`
**For:** Celery Beat schedule and task status.
**Actions:** `list`, `status`, `history`, `upcoming`.

### `db_health_tool`
**For:** database health and stats.
**Actions:** `overview`, `table_sizes`, `slow_queries`, `connections`.

### `http_smoke_test`
**For:** HTTP endpoint smoke tests.
**Params:** suite/routes to test.

### `surgical_moves_status_tool`
**For:** track surgical improvement moves.
**Actions:** `list`, `detail`, `stats`.

### `recent_activity_tool`
**For:** recent platform activity feed.
**Params:** `limit`, `minutes`.

### `agent_introspection_tool`
**For:** inspect agent config/capabilities.
**Actions:** `list`, `detail`, `capabilities`, `performance`.

---

## H) Markets, Sports, Revenue

### `stock_intelligence_tool`
**For:** stock dashboards, briefs, alerts, predictions.
**Actions:** `brief`, `alerts`, `predictions`, `watchlist`, `sector`.

### `sports_betting_tool`
**For:** betting analysis, wagers, results.
**Actions:** `upcoming`, `analyze`, `record_wager`, `results`, `stats`, `predictions`, `bankroll`.

### `ml_analysis`
**For:** ML model performance and predictions.
**Actions:** `list`, `stats`, `detail`, `evaluate`, `compare`.

### `opportunity_manager_tool`
**For:** revenue opportunity tracking.
**Actions:** `list`, `stats`, `detail`, `create`, `update`, `assess`.

### `revenue_tracker_tool`
**For:** revenue tracking and reporting.
**Actions:** `summary`, `list`, `detail`, `create`, `goals`, `by_source`.

---

## I) Creative Studio & Media

### `studio_tool`
**For:** generate images/video/audio/talking video.
**Actions:** `generate_image`, `generate_video`, `generate_audio`, `generate_talking_video`, `create_talking_video`, `job_status`, `list_jobs`.

### `media_tool`
**For:** browse/manage generated media.
**Actions:** `list`, `detail`, `stats`, `delete`.

### `davinci_tool`
**For:** DaVinci Resolve rendering.
**Actions:** `health`, `render`, `status`, `result`, `jobs`, `grades`.

---

## J) Cost & Budget

### `cost_telemetry_tool`
**For:** token usage and API cost tracking.
**Actions:** `summary`, `by_model`, `by_agent`, `daily`, `budget_check`, `trends`.

### `check_resource_budget`
**For:** quick budget gate check.
**Params:** none.

---

## K) Platform Awareness & Config

### `platform_awareness_tool`
**For:** system manifest, routes, deploys, tool registry.
**Actions:** `get_manifest`, `list_routes`, `check_route`, `system_overview`, `verify_deploy`, `list_api_dependencies`, `tool_registry`.

### `platform_config_tool`
**For:** read/update platform configuration.
**Actions:** `get`, `set`, `list`, `reset`.

---

## L) Ideas, Strategy, Reasoning

### `dream_tool`
**For:** agent dreams and creative ideation.
**Actions:** `list`, `stats`, `detail`, `create`.

### `brainstorm_tool`
**For:** structured brainstorming sessions.
**Actions:** `start`, `continue`, `list`, `detail`.

### `reasoning_engine_tool`
**For:** deep reasoning and analysis.
**Actions:** `analyze`, `compare`, `evaluate`.

### `pilots_tool`
**For:** experiment/pilot tracking.
**Actions:** `list`, `stats`, `detail`, `create`, `update`.

### `gates_tool`
**For:** quality/publish gates for content pipeline.
**Actions:** `list`, `stats`, `detail`, `approve`, `reject`.

---

## M) Legal & Legislation

### `legislation_tool`
**For:** legal/regulatory monitoring.
**Actions:** `list`, `search`, `detail`, `stats`, `alerts`.

### `legal_doc_drafter_agent`
**For:** draft legal documents. Async via Celery — returns task_id.

---

## N) Research & Web

### `web_search`
**For:** live web search.
**Params:** `query`.

### `research_and_create_tool`
**For:** research a topic and create a deliverable.
**Actions:** `research`, `create`.

---

## How to request missing tools
If this manifest is incomplete, ask the PA:
> "Run `platform_awareness_tool(action='tool_registry')` and provide the missing tools for category X."

The PA will append new entries and bump the version.
