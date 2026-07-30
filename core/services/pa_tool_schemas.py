"""
PA Tool Schemas - OpenAI Function Calling Schemas for ToolDispatcher
====================================================================

Session 1036: Created for LLM-driven function calling to replace keyword routing.

Each schema maps 1:1 to a ToolDispatcher handler. The LLM sees these schemas
and decides which tool(s) to call based on the user's message.

Design rules:
- Action-based tools use a single schema with `action` enum
- Agent-delegation tools use `run_agent` with `agent_name` enum
- Description is the routing signal -- must contain natural language patterns
- Only `action` is required where applicable; everything else optional

Session 1080: Added SCHEMA_VERSION for live-reload detection. When tools are
added/removed, the version changes and running processes can detect the change
and reload schemas without a process restart.
"""
import hashlib

# ── Tool Schemas for OpenAI Responses API function calling ──────────────────

PA_TOOL_SCHEMAS = [
    # ── Dream Browsing ──────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "dream_tool",
        "description": (
            "Browse and act on agent dreams: list top-scored dreams, view details, "
            "approve or dismiss. Use when the user asks about dreams, agent ideas, "
            "creative proposals, or wants to approve/dismiss a dream."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list_top", "details", "approve", "dismiss", "stats", "create"],
                    "description": "Dream action. Use 'create' to add a new dream/idea manually.",
                },
                "id": {"type": "string", "description": "UUID of dream"},
                "title": {"type": "string", "description": "Title for new dream (for create action)"},
                "content": {"type": "string", "description": "Dream content/description (for create action)"},
                "dream_type": {"type": "string", "enum": ["creative_idea", "what_if", "mashup", "prediction", "improvement", "observation", "wild_thought"], "description": "Type of dream (for create, default creative_idea)"},
                "feedback": {"type": "string", "description": "Optional feedback when approving/dismissing"},
                "limit": {"type": "integer", "description": "Max dreams to return (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Brainstorm Search + Async Single-Agent Dispatch ─────────────────────
    {
        "type": "function",
        "name": "brainstorm_tool",
        "description": (
            "Search historical brainstorm/panel/discussion conversations, OR dispatch a "
            "single-agent async reasoning pass on a topic. "
            "READ actions (list/search/recent/details/by_category/stats): query the archive "
            "of past brainstorming — this archive may include historical multi-agent panels "
            "and discussions from earlier system versions. "
            "CREATE action: dispatches ONE ThinkingAgent asynchronously on the given topic "
            "and returns a task_id — this is NOT a live multi-participant panel/debate. "
            "Poll progress with agent_job_status. Multi-agent panel dispatch is not yet "
            "implemented; a distinct create_panel action is on the roadmap when needed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "recent", "details", "by_category", "stats", "create"],
                    "description": (
                        "READ: list, search, recent, details, by_category, stats. "
                        "WRITE (dispatch): create — kicks off a single ThinkingAgent async run "
                        "(NOT a multi-agent panel)."
                    ),
                },
                "id": {"type": "string", "description": "UUID of brainstorm session (alias: conversation_id)"},
                "conversation_id": {"type": "string", "description": "UUID of brainstorm conversation for details action"},
                "query": {"type": "string", "description": "Search query for brainstorm content"},
                "category": {"type": "string", "description": "Category filter for by_category action"},
                "topic": {
                    "type": "string",
                    "description": (
                        "Topic/prompt for create action — dispatches a single ThinkingAgent async. "
                        "Returns task_id; poll with agent_job_status."
                    ),
                },
                "limit": {"type": "integer", "description": "Max items (default 50 for list, 10 for search)"},
                "offset": {"type": "integer", "description": "Pagination offset for list action (default 0)"},
                "days": {"type": "integer", "description": "Days back to search (default 30)"},
                "days_back": {"type": "integer", "description": "Alias for days"},
                "type": {
                    "type": "string",
                    "description": (
                        "Filter historical results by conversation type: 'discussion' or 'panel'. "
                        "Applies to READ actions only — does NOT change create-action behavior "
                        "(create always dispatches a single ThinkingAgent)."
                    ),
                },
                "status": {"type": "string", "description": "Filter by conversation status"},
                "include_transcript": {"type": "boolean", "description": "Include full message transcript (default false)"},
                "include_full_content": {"type": "boolean", "description": "Include full content in details (default false)"},
            },
            "required": ["action"],
        },
    },

    # ── Opportunity Manager ─────────────────────────────────────────────────
    {
        "type": "function",
        "name": "opportunity_manager_tool",
        "description": (
            "Manage opportunities: list, view details, get stats, create, or update status. "
            "Use when the user asks about opportunities, job listings, income "
            "opportunities, or wants to track/update an opportunity. "
            "SCOPE: Results are filtered to the calling user's opportunities when a "
            "user is authenticated (the 'your pipeline' view, typically ~tens of rows). "
            "The platform-wide spider-ingested lead pool (~thousands of unattributed "
            "Opportunity rows owned by the system user) is visible only via "
            "autopilot_tool.dry_run_report → revenue_pipeline.total_active. "
            "Session 1222 P4 (audit C1) clarified this distinction."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "get", "stats", "update_status", "create", "delete"],
                    "description": "Opportunity action. Use 'create' to add, 'delete' to remove (also deletes linked tasks).",
                },
                "id": {"type": "string", "description": "UUID of opportunity"},
                "title": {"type": "string", "description": "Title for new opportunity (for create)"},
                "description": {"type": "string", "description": "Description (for create)"},
                "opportunity_type": {"type": "string", "description": "Type: freelance, consulting, job, gig, etc. (for create)"},
                "source": {"type": "string", "description": "Where found: web_search, spider, manual, referral (for create)"},
                "potential_revenue": {"type": "number", "description": "Estimated revenue in dollars (for create)"},
                "status": {"type": "string", "description": "Filter by or set status (active, pending, applied, accepted, rejected, expired)"},
                "limit": {"type": "integer", "description": "Max items (default 20)"},
                "scope": {
                    "type": "string",
                    "enum": ["mine", "all"],
                    "description": (
                        "For list / stats actions only. Default 'mine' filters to the caller's "
                        "opportunities (the safe-by-default 'your pipeline' view). Pass 'all' to "
                        "see the platform-wide pool — useful for surfacing the spider-ingested "
                        "lead pool (system-user-owned rows) when the user asks 'what leads has "
                        "the platform discovered?'. Session 1222 P4 (audit C1)."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Task Manager ────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "task_manager_tool",
        "description": (
            "Manage tasks linked to opportunities: list tasks, view stats. "
            "Use when the user asks about tasks, to-do items, or work items "
            "related to opportunities. "
            "HIDDEN MUTATION: `create` without `opportunity_id` implicitly "
            "creates a standalone Opportunity row to satisfy the required FK "
            "(handler creates opportunity_type='task', source='pa', "
            "potential_revenue=0). To avoid silent parent-row accretion, "
            "pass `opportunity_id` explicitly when linking to an existing "
            "opportunity."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "stats", "create", "update", "complete", "delete"],
                    "description": "Task action: list, stats, create new task, update existing, mark complete (sets status='won' which means accepted/done), or delete",
                },
                "status": {"type": "string", "description": "Filter by task status or new status for update. Values: pending, accepted, in_progress, applied, waiting, won (=completed), lost, expired, cancelled"},
                "priority": {"type": "string", "description": "Filter by priority (low/medium/high/urgent) or set priority for create/update"},
                "limit": {"type": "integer", "description": "Max items (default 20)"},
                "id": {"type": "string", "description": "Task UUID (required for update/complete)"},
                "title": {"type": "string", "description": "Task title (required for create)"},
                "description": {"type": "string", "description": "Task description"},
                "opportunity_id": {"type": "string", "description": "Link to opportunity UUID (for create). WARNING: omitting this triggers implicit standalone Opportunity creation — pass explicitly when the intent is to link to an existing opportunity."},
            },
            "required": ["action"],
        },
    },

    # ── Pipeline Orchestrator ───────────────────────────────────────────────
    {
        "type": "function",
        "name": "pipeline_orchestrator_tool",
        "description": (
            "Get pipeline orchestration status and initiative stage breakdown. "
            "Use when the user asks about pipeline status or orchestration."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status"],
                    "description": "Pipeline action",
                },
            },
            "required": ["action"],
        },
    },

    # ── Revenue Tracker ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "revenue_tracker_tool",
        "description": (
            "Track revenue metrics, income progress, and record new revenue. "
            "Use when the user asks about revenue, earnings, income, financial "
            "progress, or wants to record a new revenue event."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["stats", "list", "create"],
                    "description": "Revenue action: stats (totals by source/status), list (recent records), create (record new revenue)",
                },
                "amount": {"type": "number", "description": "Revenue amount in dollars (for create)"},
                "source": {"type": "string", "enum": ["quick_apply", "freelance", "consulting", "ai_project", "content", "trading", "sports_betting", "affiliate", "other"], "description": "Revenue source (for create, default 'other')"},
                "description": {"type": "string", "description": "Description of revenue (for create)"},
                "status": {"type": "string", "enum": ["potential", "pending", "received", "cancelled"], "description": "Revenue status (for create, default 'potential')"},
                "limit": {"type": "integer", "description": "Max items for list action (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── ML Analysis ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "ml_analysis",
        "description": (
            "Run ML analysis on platform data: prediction models, feature importance, "
            "model accuracy. Use when the user asks about machine learning, model "
            "performance, predictions accuracy, or data analysis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "decision_pattern", "detect_opportunity"],
                    "description": "ML analysis action: status = system health, decision_pattern = analyze user decisions, detect_opportunity = cross-domain opportunities",
                },
                "model_type": {"type": "string", "description": "Specific model to analyze"},
            },
            "required": ["action"],
        },
    },

    # ── Predictions ─────────────────────────────────────────────────────────
    # REMOVED (Session 1062): predictions_tool schema removed — AgentPrediction
    # model deprecated (Session 284). Sports predictions → sports_betting_tool,
    # stock predictions → stock_intelligence_tool.

    # ── Gates ───────────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "gates_tool",
        "description": (
            "Access quality gates: list gates, check gate status, view pass/fail "
            "history. Use when the user asks about gates, quality checks, "
            "or publish gates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "stats", "detail"],
                    "description": "Gates action",
                },
                "id": {"type": "string", "description": "UUID of gate"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Pilots / Experiments ────────────────────────────────────────────────
    {
        "type": "function",
        "name": "pilots_tool",
        "description": (
            "Access experiments and pilots: A/B tests, feature experiments, "
            "pilot results. Use when the user asks about experiments, pilots, "
            "A/B tests, or experimental features."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "stats", "detail"],
                    "description": "Pilots action",
                },
                "id": {"type": "string", "description": "UUID of pilot"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Reasoning Engine ────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "reasoning_engine_tool",
        "description": (
            "Query or trigger the ThinkingAgent reasoning engine. "
            "Actions: status (engine health), thoughts (recent AgentExecution rows "
            "for ThinkingAgent), trigger (invoke a new thinking cycle — MUTATION, "
            "runs a real LLM-backed reflection over recent system activity)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "thoughts", "trigger"],
                    "description": "Reasoning engine action: status = engine health, thoughts = recent thinking cycle history, trigger = kick off a new thinking cycle (LLM cost)",
                },
                "limit": {"type": "integer", "description": "Max items for thoughts action (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Web Search ──────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "web_search",
        "description": (
            "Search the web for current information. Use when the user asks "
            "about current events, recent news, or information you don't have."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        },
    },

    # ── Web Fetch (raw HTTP) — Rigby Tool Gap Ledger #15 (S2865) ───────────
    {
        "type": "function",
        "name": "web_fetch_tool",
        "description": (
            "Raw HTTP GET/POST to a URL, returning status_code, headers, "
            "and body (parsed JSON when content-type is application/json). "
            "Use this when you need to verify what an API actually returns — "
            "e.g., inspecting a JSON endpoint, checking a local /api/... "
            "response, or confirming a service is reachable. Not a browser: "
            "no JS execution, no cookies, no bot-protection bypass. Response "
            "body capped at 500KB by default (max 2MB). Timeout capped at "
            "60s. Only http:// and https:// URLs allowed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL to fetch (http:// or https:// only).",
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST"],
                    "description": "HTTP method (default GET).",
                },
                "headers": {
                    "type": "object",
                    "description": (
                        "Optional request headers as a {name: value} object. "
                        "Authorization values are not logged, but body content is "
                        "returned in the tool result — do not fetch URLs whose "
                        "response would leak secrets you don't want visible."
                    ),
                },
                "params": {
                    "type": "object",
                    "description": (
                        "Optional querystring parameters merged into the URL. "
                        "Prefer this over hand-constructing the URL — safer "
                        "escaping and repeated-key handling."
                    ),
                },
                "json_body": {
                    "type": "object",
                    "description": "Optional JSON body (POST only; ignored for GET).",
                },
                "timeout_seconds": {
                    "type": "number",
                    "description": "Read timeout in seconds (default 15, max 60).",
                },
                "max_bytes": {
                    "type": "integer",
                    "description": (
                        "Truncate response body after this many bytes "
                        "(default 500000 = 500KB, max 2000000 = 2MB). "
                        "truncated=true in response indicates the cap was hit."
                    ),
                },
                "allow_private_networks": {
                    "type": "boolean",
                    "description": (
                        "Allow loopback / RFC1918 hosts (default true for "
                        "current single-tenant pre-prod context). Flip to "
                        "false to lock down egress if platform ever becomes "
                        "multi-tenant."
                    ),
                },
                "use_user_auth": {
                    "type": "boolean",
                    "description": (
                        "Inject the calling user's DRF Token as "
                        "`Authorization: Token <key>` so authenticated "
                        "internal endpoints (e.g. /api/repo/...) return 200 "
                        "instead of 401. Default false. Ignored when the "
                        "caller already supplied an Authorization header. "
                        "If the user has no Token row, the request proceeds "
                        "unauthenticated and the endpoint's 401 is returned "
                        "as-is (fail-open). S3000 v2 item #5."
                    ),
                },
            },
            "required": ["url"],
        },
    },

    # ── ORM Row Inspector (read-only) — Rigby Tool Gap Ledger #3 / b5a22ea7 (S2866) ──
    {
        "type": "function",
        "name": "orm_inspect_tool",
        "description": (
            "Read-only, allowlisted Django ORM row inspection. Use this when "
            "you need to verify what's actually persisted in the database — "
            "e.g., 'do rows with source_breakdown.huggingface exist?', 'what "
            "status is Deliverable X in?', 'how many AutopilotAction rows "
            "fired today?'. Complements web_fetch_tool (external endpoint "
            "verify → this = internal DB verify). Closes the S2845-class "
            "false-negative gap where a tool surface reports 'no data' but "
            "the rows are actually there under a different filter path. "
            "NOT a write surface — no create/update/delete. NOT a general "
            "Django-shell tool — only allowlisted models. Sensitive field "
            "names (password/secret/token/authorization/etc.) always redacted; "
            "JSONField values for high-sensitivity models excluded by default."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list_models", "describe_model", "get", "filter", "count_by"],
                    "description": (
                        "list_models = enumerate the allowlist. "
                        "describe_model = return field types for one model. "
                        "get = fetch one row by pk. "
                        "filter = fetch N rows by filter_kwargs (default 20, max 200). "
                        "count_by = group-by aggregate counts on a field with "
                        "optional filter_kwargs (returns [{value, count}, ...] "
                        "sorted desc, default limit 50, max 500). Auto-buckets "
                        "DateTimeField by day."
                    ),
                },
                "model": {
                    "type": "string",
                    "description": (
                        "Model name (case-sensitive, e.g., 'SignalCluster'). "
                        "Required for describe_model/get/filter. Must be in the "
                        "allowlist (call list_models to see it)."
                    ),
                },
                "pk": {
                    "type": "string",
                    "description": (
                        "Primary key value for 'get' action. String form works "
                        "for both UUID and integer PKs."
                    ),
                },
                "filter_kwargs": {
                    "type": "object",
                    "description": (
                        "Dict of {field_or_field__lookup: value} for 'filter' "
                        "action. Allowed lookups: exact, iexact, isnull, gt, "
                        "gte, lt, lte, contains, icontains, startswith, "
                        "istartswith, in, has_key, has_keys. FK traversal "
                        "beyond one __ chain rejected. 'in' list capped at 100. "
                        "Example: {'source_breakdown__has_key': 'huggingface', "
                        "'signal_count__gte': 3}."
                    ),
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional explicit field projection. Default returns "
                        "all fields on the model minus sensitive-name matches "
                        "(and minus JSONFields for high-sensitivity models "
                        "unless include_json_fields=true)."
                    ),
                },
                "order_by": {
                    "type": "string",
                    "description": (
                        "Order field for 'filter' action. Allowed: id, "
                        "created_at, updated_at, detected_at, started_at, "
                        "first_seen, last_seen (only those that exist on the "
                        "model). Prefix with '-' for descending. Default '-id'."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Max rows returned for 'filter' (default 20, max 200). "
                        "For 'count_by', max distinct group values returned "
                        "(default 50, max 500). truncated=true in response "
                        "indicates the cap was hit."
                    ),
                },
                "include_json_fields": {
                    "type": "boolean",
                    "description": (
                        "Include JSONField values in the response. Default "
                        "true for normal models, false for high-sensitivity "
                        "models (LLMCallLog, AutopilotAction, OpsRun). When "
                        "included, values are recursively scanned and any key "
                        "matching the redaction denylist (token/api_key/"
                        "authorization/cookie/secret/credential/password/etc.) "
                        "is replaced with '<redacted>'."
                    ),
                },
                "field": {
                    "type": "string",
                    "description": (
                        "Group-by field name for 'count_by' action. Must exist "
                        "on the model, must not be sensitive-by-name, must not "
                        "be a JSONField, and must not be listed in the model's "
                        "expensive_text_fields. FK fields group on <field>_id. "
                        "DateTimeField auto-buckets to day (TruncDate)."
                    ),
                },
                "order_by_count": {
                    "type": "string",
                    "enum": ["desc", "asc"],
                    "description": (
                        "Order the returned groups by count. Default 'desc' "
                        "(highest count first). Ties break by value ascending "
                        "for stable output. Only applies to 'count_by' action."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Research and Create ─────────────────────────────────────────────────
    {
        "type": "function",
        "name": "research_and_create_tool",
        "description": (
            "Research a topic via web search and create content (blog post, "
            "comparison, script, analysis). Use when the user asks to research "
            "something AND create content from that research."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The full user request"},
                "research_topic": {"type": "string", "description": "Topic to research via web search"},
                "output_type": {"type": "string", "description": "Type of content to create (blog, script, analysis, comparison)"},
                "output_type_label": {"type": "string", "description": "Human-readable label for content type"},
            },
            "required": ["query", "research_topic"],
        },
    },

    # ── Execution History ───────────────────────────────────────────────────
    {
        "type": "function",
        "name": "execution_history_tool",
        "description": (
            "View agent execution history: recent runs, success/failure rates, "
            "execution details, and full output data. Use when the user asks about "
            "what agents have done, execution logs, agent activity, run history, "
            "or wants to see the full output/report/result from a specific agent run. "
            "Use action=detail with id or agent_name to get full output_data. "
            "The detail response also includes a `deliverables` field listing up to "
            "25 deliverables produced by the execution (reverse-link pivot to "
            "deliverable_tool.detail provenance)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["recent", "by_agent", "stats", "failures", "detail"],
                    "description": "Execution history action: recent (latest runs), by_agent (filter by agent), stats (aggregates), failures (recent errors), detail (full output_data for a specific execution by id)",
                },
                "agent_name": {"type": "string", "description": "Filter by agent name"},
                "id": {"type": "string", "description": "UUID of execution for detail action"},
                "status": {"type": "string", "description": "Filter by status (completed, failed)"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Learning Patterns ───────────────────────────────────────────────────
    {
        "type": "function",
        "name": "learning_patterns_tool",
        "description": (
            "View mined LearningPattern telemetry (tool reliability, agent tool "
            "effectiveness, spider data value, etc.). Use when the user asks about "
            "what patterns the system has learned, best-performing tools, or "
            "improvement trends. action=list returns active patterns above "
            "min_confidence; action=by_type filters by pattern_type (or returns "
            "available types if omitted); action=stats returns aggregate counts + "
            "top patterns."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "by_type", "stats"],
                    "description": "Learning patterns action: list (active patterns), by_type (filter by pattern_type), stats (aggregate statistics)",
                },
                "pattern_type": {"type": "string", "description": "Filter by pattern type (e.g. tool_reliability, agent_performance)"},
                "min_confidence": {"type": "number", "description": "Minimum confidence threshold (default 0.5)"},
                "limit": {"type": "integer", "description": "Max items (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Feedback ────────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "feedback_tool",
        "description": (
            "Submit or view feedback on agent outputs, content quality, "
            "or platform features. Use when the user wants to give feedback, "
            "rate something, or view past feedback."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["submit", "list", "stats", "update"],
                    "description": (
                        "submit: create new feedback. "
                        "list: view feedback items. "
                        "stats: feedback statistics. "
                        "update: change feedback status."
                    ),
                },
                "target_type": {"type": "string", "description": "What the feedback is about (for submit)"},
                "target_id": {"type": "string", "description": "UUID of the item being rated (for submit)"},
                "rating": {"type": "integer", "description": "Rating 1-5 (for submit)"},
                "comment": {"type": "string", "description": "Feedback comment (required for submit)"},
                "id": {"type": "string", "description": "Feedback UUID (for update)"},
                "new_status": {"type": "string", "description": "New status (for update): open, acknowledged, in_progress, addressed, wont_fix"},
                "notes": {"type": "string", "description": "Resolution notes (for update)"},
                "limit": {"type": "integer", "description": "Max items (default 10, for list)"},
                "dry_run": {
                    "type": "boolean",
                    "description": (
                        "S2942 Ledger #38 MVP: For submit/update, preview the mutation without writing. "
                        "Returns a would_* envelope (dry_run=true, would_action, current_status/would_change_to, "
                        "no_writes=true). Zero DB writes when true. Default false."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Recent Activity (Live Telemetry) ────────────────────────────────────
    {
        "type": "function",
        "name": "recent_activity_tool",
        "description": (
            "View recent platform activity across 6 subsystems in one call: "
            "Celery tasks, spider data, HiveMind conversations, blogs, initiatives, "
            "and signal clusters. Use when the user asks about what is happening, "
            "what just ran, recent activity, or what is going on. "
            "action=summary returns compact per-section rollups (5 items each); "
            "action=detailed returns the same shape with 15 items per section."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["summary", "detailed"],
                    "description": "summary: 5 items per section (default). detailed: 15 items per section.",
                },
                "hours": {"type": "integer", "description": "Lookback window in hours (default 2)"},
                "limit": {"type": "integer", "description": "DEPRECATED S2935 - handler ignores this. Use action=detailed for larger lists."},
                "minutes": {"type": "integer", "description": "DEPRECATED S2935 - handler ignores this. Use hours instead."},
            },
        },
    },

    # ── Surgical Moves Status ───────────────────────────────────────────────
    {
        "type": "function",
        "name": "surgical_moves_status_tool",
        "description": (
            "Check status of the DeliberationSession pipeline (multi-agent surgical-moves "
            "debates that decide publish/revise/kill on content). Returns per-session "
            "status, turn counts, contract counts, evidence stats, and decision verdicts. "
            "Use when the user asks about surgical moves status, deliberations, or whether "
            "the deliberator finished. action=summary returns up to 5 sessions; "
            "action=detailed returns up to 20. Pass session_id to inspect a specific "
            "session (bypasses time window)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["summary", "detailed"],
                    "description": "summary: up to 5 sessions (default). detailed: up to 20 sessions.",
                },
                "hours": {"type": "integer", "description": "Lookback window in hours (default 24)"},
                "session_id": {"type": "string", "description": "UUID of a specific DeliberationSession to inspect (bypasses time window)"},
                "verbose": {"type": "boolean", "description": "DEPRECATED S2935 - handler ignores this. Use action=detailed instead."},
            },
        },
    },

    # ── Body Vitals ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "get_body_vitals",
        "description": (
            "Get body system vitals: HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, "
            "DIGESTIVE, MUSCULAR, BRAIN, SKIN health scores. Use when the user "
            "asks about body systems, vitals, organism health, or body status."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },

    # ── Resource Budget ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "check_resource_budget",
        "description": (
            "Check resource budgets: API costs, token usage, compute limits. "
            "Use when the user asks about costs, budget, API spending, or resource usage."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "estimated_tokens": {
                    "type": "integer",
                    "description": "Estimated token usage for a planned operation",
                },
                "estimated_cost": {
                    "type": "number",
                    "description": "Estimated cost in USD for a planned operation",
                },
            },
        },
    },

    # ── Cost Telemetry ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "cost_telemetry_tool",
        "description": (
            "Get real API cost and spend data from LLM call logs. Use when the user "
            "asks about actual costs, spending, most expensive agents, cost trends, "
            "cost breakdown, or wants a ranked list of agents by spend. This returns "
            "real dollar amounts, not budget gates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["summary", "top_agents", "recent_calls"],
                    "description": (
                        "summary: total spend, by provider, by task type, trend. "
                        "top_agents: ranked list of agents by cost. "
                        "recent_calls: last N individual LLM calls for debugging."
                    ),
                },
                "hours": {
                    "type": "integer",
                    "description": "Lookback period in hours (default 24)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max items to return (default 10, max 50)",
                },
            },
            "required": ["action"],
        },
    },

    # ── System Alerts ───────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "get_system_alerts",
        "description": (
            "Get active system alerts and warnings. Use when the user asks about "
            "alerts, warnings, or system notifications."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"], "description": "Filter by severity"},
                "limit": {"type": "integer", "description": "Max alerts (default 10)"},
            },
        },
    },

    # ── Status Snapshot ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "status_snapshot_tool",
        "description": (
            "Get a broad system overview snapshot: agents, spiders, initiatives, "
            "health scores, recent activity. Use when the user asks for an overview, "
            "executive summary, 'how is the system doing', or 'give me a summary'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific sections to include (agents, spiders, initiatives, health, activity)",
                },
            },
        },
    },

    # ── Agent Introspection ─────────────────────────────────────────────────
    {
        "type": "function",
        "name": "agent_introspection_tool",
        "description": (
            "Introspect agents: list registered agents, view capabilities, "
            "check which agents are available. Use when the user asks about "
            "agents, what agents exist, agent capabilities, or agent details."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "stats", "details", "capabilities", "tools"],
                    "description": "Introspection action: list/stats for agent overview, details/capabilities for a specific agent, tools to list all PA tool schemas",
                },
                "agent_name": {"type": "string", "description": "Specific agent name"},
                "limit": {"type": "integer", "description": "Max agents (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Scheduled Tasks ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "scheduled_tasks_tool",
        "description": (
            "View and manage scheduled Celery tasks: list beat entries, enable/disable schedules. "
            "Use when the user asks about scheduled tasks, cron jobs, what runs automatically, "
            "or Celery beat. Supports search, pagination, and enable/disable management."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "enable", "disable"],
                    "description": (
                        "list: view scheduled tasks (default). "
                        "enable: enable a disabled beat entry. "
                        "disable: disable a beat entry."
                    ),
                },
                "name": {"type": "string", "description": "Beat entry name (for enable/disable actions)"},
                "task_id": {"type": "string", "description": "Numeric ID or exact name of beat entry (for enable/disable)"},
                "search": {
                    "type": "string",
                    "description": "Filter tasks by name or task path (case-insensitive substring match)",
                },
                "show_disabled": {"type": "boolean", "description": "Include disabled tasks in list (default false)"},
                "limit": {"type": "integer", "description": "Max items per page (default 50, max 100)"},
                "offset": {"type": "integer", "description": "Skip N items for pagination (default 0)"},
            },
            "required": [],
        },
    },

    # ── Universal Agent ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "universal_agent_tool",
        "description": (
            "Route a task to a specific agent or auto-route to the best-fit agent. "
            "Use when the user wants a specific agent to run, or when no other "
            "specialized tool fits the request."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description for the agent to execute"},
                "agent_name": {"type": "string", "description": "Specific agent name (e.g. 'ContentStrategyAgent'). If omitted, auto-routes to best-fit agent."},
                "context": {"type": "object", "description": "Additional context for the agent"},
            },
            "required": ["task"],
        },
    },

    # ── Active repo (multi-repo v0 — Session 1119 carryover #4) ─────────────
    {
        "type": "function",
        "name": "fleet_health",
        "description": (
            "Read-only rollup of every Dockerized fleet app's /api/health "
            "endpoint. Use this to answer 'what's broken in the fleet right "
            "now?' or 'is mentorforge up?'. Returns overall_status "
            "(healthy/degraded/empty), a per-app rows array with "
            "{slug, status, ok, latency_ms, detail}, and counts. Probes the "
            "7 registered Docker fleet apps (mentorforge, contract-concierge, "
            "pitchdeckforge, sellerpilot, dealflowtracker, signal-studio, "
            "compliancesentinel) by default. Source of truth: each app's "
            "docker.base_urls.api_url + docker.healthchecks.api.path from "
            "the registered Repo Profile."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": (
                        "Optional. Probe a single repo by slug (e.g. "
                        "'mentorforge'). When omitted, probes all 7."
                    ),
                },
                "timeout_seconds": {
                    "type": "number",
                    "description": "Per-app HTTP timeout in seconds. Default 3.",
                },
                "include_healthy": {
                    "type": "boolean",
                    "description": (
                        "Default true. When false, the apps array only "
                        "includes degraded/unreachable apps (concise output "
                        "for status pings)."
                    ),
                },
            },
            "required": [],
        },
    },

    # ── Paid-interest trigger state (Session 1138 — Decision 13) ─────────────
    {
        "type": "function",
        "name": "paid_interest_status",
        "description": (
            "Return the Decision 13 demand-gate trigger state for a fleet "
            "app's paid-interest signal. Use this to answer 'is signal-studio "
            "ready for paid launch / legal review yet?' or 'how many paid-"
            "interest signups do we have?'. Returns total_signals, "
            "last_90d_signals, has_high_value_signal, count_threshold, "
            "high_value_threshold_usd, trigger_state "
            "(not_yet|ready|manually_overridden), and last_signal_at. The "
            "trigger flips to 'ready' when (last_90d_signals >= "
            "count_threshold) OR has_high_value_signal is true."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "app_slug": {
                    "type": "string",
                    "description": (
                        "Fleet app to evaluate. Defaults to 'signal-studio' "
                        "(the first app on the demand-gate per Decision 13). "
                        "Other registered apps: see APP_TRIGGER_CONFIG in "
                        "core.services.fleet_paid_interest."
                    ),
                },
                "manual_override": {
                    "type": "boolean",
                    "description": (
                        "When true, the response reports "
                        "trigger_state='manually_overridden' regardless of "
                        "signal counts. Use when Jessica is asking 'what "
                        "would the override look like'. Default false."
                    ),
                },
            },
            "required": [],
        },
    },

    # ── Signal-studio judge stats (Session 1140) ────────────────────────────
    # Intentionally evergreen description — no SLO numbers, baselines,
    # or acceptance thresholds. Those belong in handoff docs / runbooks
    # so they don't bias the model toward a stale target. See Rigby's
    # design review on PR #2169 for the rationale.
    {
        "type": "function",
        "name": "signal_studio_judge_stats",
        "description": (
            "Return signal-studio's LLM auto-summarizer judge stats over "
            "the last N days: counts of clusters accepted (summarized) "
            "vs rejected as incoherent, with rejection_rate broken down "
            "by cluster_method and pattern_type. Used to validate "
            "clustering-quality changes and answer 'how is the current "
            "clusterer performing?'. Calls signal-studio's auth-less "
            "/api/judge-stats endpoint over the configured base URL."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": (
                        "Lookback window in days. Default 7. Range 1-90. "
                        "Use 1 for 'today only', 7 for a week's signal, 30 "
                        "to include slower-moving categories."
                    ),
                    "minimum": 1,
                    "maximum": 90,
                },
            },
            "required": [],
        },
    },

    {
        "type": "function",
        "name": "active_repo_tool",
        "description": (
            "Persist or read the 'currently working in repo X' pointer for the "
            "user, so multi-repo workflows don't need to re-state context every "
            "turn. Per-user state, 7-day TTL. Actions: set | get | clear. "
            "When set, downstream tools (workspace_tool, deliverable_tool, "
            "agent dispatch) can scope to this repo's ProjectWorkspace via "
            "its workspace_id. Use 'set' with the repo's workspace name to "
            "scope a conversation to that repo; 'get' to check current scope; "
            "'clear' when done. The pointer never affects Donkey Betz "
            "(u-d-b's own workspace stays the global active workspace)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["set", "get", "clear"],
                    "description": (
                        "set: scope this user to repo X for ~7 days. "
                        "get: return the currently scoped repo (or null). "
                        "clear: drop the pointer."
                    ),
                },
                "repo": {
                    "type": "string",
                    "description": (
                        "For set: workspace name / repo_id "
                        "(e.g. 'character-os', 'mentorforge'). Must match "
                        "a ProjectWorkspace that has been registered via "
                        "register_external_repo."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Workspace ───────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "workspace_tool",
        "description": (
            "Manage workspaces and workspace-scoped operations. "
            "Use it to list, look up, activate, create, or delete workspaces, and to scan, read, write, "
            "inspect git status, create branches/commits, review operations, and roll back changes. "
            "Workspace file actions are always scoped to the active workspace or an explicit workspace_id."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "list", "get", "status", "create", "update", "delete",
                        "scan", "read", "write", "git_status", "git_commit", "git_branch",
                        "operations", "rollback",
                    ],
                    "description": (
                        "list: list all workspaces (optional name filter). "
                        "get: get workspace details by ID or name. "
                        "status: quick status of active workspace. "
                        "create: make a new workspace. "
                        "update: mutate workspace attributes (root_path / new_name / description / workspace_type / business_status). Requires workspace_id. "
                        "delete: remove a sandbox workspace. "
                        "scan: rescan workspace structure and stats. "
                        "read: read a file within the workspace root. "
                        "write: write a file within the workspace root. "
                        "git_status: inspect git status for the workspace. "
                        "git_commit: create a git commit. "
                        "git_branch: create a git branch. "
                        "operations: list recent workspace operations. "
                        "rollback: roll back an operation (requires confirm_rollback=true)."
                    ),
                },
                "workspace_id": {"type": "string", "description": "Workspace UUID (preferred for workspace-scoped actions, get, delete, scan, read, write, git, operations, rollback, update)"},
                "name": {"type": "string", "description": "Workspace name — for search (list), lookup (get/set_active), creation (create/register), or delete"},
                "new_name": {"type": "string", "description": "For update: new workspace name (distinct from 'name' which is used for lookup/create/delete)"},
                "description": {"type": "string", "description": "Description/notes (for create/register/update)"},
                "root_path": {"type": "string", "description": "For update: new root_path (must exist on disk; validated at write time)"},
                "workspace_type": {"type": "string", "description": "For update: new workspace_type (e.g. 'sandbox', 'local')"},
                "business_status": {"type": "string", "description": "For update: new business_status (on config; e.g. 'active', 'paused', 'archived')"},
                "path": {"type": "string", "description": "For scan/register/read/write: project root path or file path, depending on action"},
                "content": {"type": "string", "description": "For write: file content to save"},
                "message": {"type": "string", "description": "For git_commit: commit message"},
                "branch_name": {"type": "string", "description": "For git_branch: branch name"},
                "operation_id": {"type": "string", "description": "For rollback: workspace operation UUID"},
                "confirm_rollback": {"type": "boolean", "description": "For rollback: must be true to confirm the destructive revert"},
                "agent_name": {"type": "string", "description": "Optional agent name for audit trail"},
                "offset": {"type": "integer", "description": "Pagination offset for list/operations (default 0)"},
                "limit": {"type": "integer", "description": "Max items for list/operations (default 50). Use with offset for pagination."},
            },
            "required": ["action"],
        },
    },

    # ── Media Library (images, videos, audio) ─────────────────────────────
    {
        "type": "function",
        "name": "media_tool",
        "description": (
            "Browse the user's media library: AI-generated images, videos, and audio files. "
            "Supported actions: list, detail, stats, delete. "
            "Use 'list' to browse media (filter by media_type, content_type, limit). "
            "Use 'detail' to get full metadata for one asset. "
            "Use 'stats' for aggregate counts by type. "
            "Use 'delete' to remove a media asset."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "detail", "stats", "delete"],
                    "description": "list=browse media, detail=full metadata, stats=counts, delete=remove asset.",
                },
                "id": {"type": "string", "description": "UUID of media asset (required for detail, delete)"},
                "media_type": {
                    "type": "string",
                    "enum": ["image", "video", "audio", "all"],
                    "description": "Filter by media type (default: all)",
                },
                "content_type": {"type": "string", "description": "Filter by content subtype (e.g. 'generated', 'uploaded', 'text_to_video', 'tts')"},
                "limit": {"type": "integer", "description": "Max items to return (default 10, max 50)"},
            },
            "required": ["action"],
        },
    },

    # ── Voice Clone & Marketplace ─────────────────────────────────────────
    {
        "type": "function",
        "name": "voice_clone_tool",
        "description": (
            "Manage voice cloning and the voice marketplace. "
            "Actions: list (user's cloned voices), detail (voice info by id), "
            "clone_requests (clone request history), marketplace (browse public voices), "
            "stats (voice counts and revenue). "
            "Voice cloning from audio files is done via the web UI at /workspace > Voice Marketplace > Clone Voice. "
            "Discord users can clone via /voice clone command."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "detail", "clone_requests", "marketplace", "stats"],
                    "description": "list=my voices, detail=voice info, clone_requests=history, marketplace=browse public, stats=counts.",
                },
                "id": {"type": "string", "description": "UUID of voice profile (for detail action)"},
                "search": {"type": "string", "description": "Search query for marketplace action"},
                "limit": {"type": "integer", "description": "Max items to return (default 10, max 30)"},
            },
            "required": ["action"],
        },
    },

    # ── DaVinci Resolve Control Surface ────────────────────────────────────
    {
        "type": "function",
        "name": "davinci_tool",
        "description": (
            "Direct control surface for DaVinci Resolve rendering and color grading. "
            "Supported actions: health, render, status, result, jobs, grades. "
            "Use 'health' to check if the render node is online. "
            "Use 'render' to start a professional render job (requires clip_paths). "
            "Use 'status' to check render job progress (requires job_id). "
            "Use 'result' to get the download URL for a completed render (requires job_id). "
            "Use 'jobs' to list all render jobs. "
            "Use 'grades' to get available color grade presets matching current trends."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["health", "render", "status", "result", "jobs", "grades"],
                    "description": "health=check node, render=start job, status=check progress, result=get download URL, jobs=list all, grades=trending presets.",
                },
                "job_id": {"type": "string", "description": "Render job ID (required for status, result)"},
                "clip_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of video file paths or URLs to render (required for render)",
                },
                "template": {
                    "type": "string",
                    "enum": ["default_mp4", "high_quality"],
                    "description": "Render template (default: default_mp4)",
                },
                "timeline_name": {"type": "string", "description": "Optional name for the timeline"},
                "color_grade": {"type": "string", "description": "Color grade preset (e.g. cinematic_warm, cyberpunk_neon, vintage_film)"},
            },
            "required": ["action"],
        },
    },

    # ── OBS Recording Control ──────────────────────────────────────────────
    {
        "type": "function",
        "name": "obs_tool",
        "description": (
            "Control OBS Studio recording via the local bridge. "
            "Actions: health (check bridge), status (recording state + timecode), "
            "start (begin recording), stop (stop recording), "
            "last (newest recording file info), upload_last (upload latest recording to platform). "
            "For upload_last, set stopIfRecording=true to auto-stop before uploading."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["health", "status", "start", "stop", "last", "upload_last"],
                    "description": "health=check bridge, status=recording state, start/stop=control recording, last=newest file, upload_last=upload to platform.",
                },
                "stopIfRecording": {
                    "type": "boolean",
                    "description": "For upload_last: stop recording first if active (default false).",
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the uploaded video.",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for the uploaded video.",
                },
            },
            "required": ["action"],
        },
    },

    # ── Video History ────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "video_history_tool",
        "description": (
            "Search, browse, and process the user's videos (VideoHistory model). "
            "Actions: list (recent videos, filterable by type/status), "
            "search (find videos by title/filename substring), "
            "detail (full metadata for one video by UUID or sequential number), "
            "resolve (normalize any video reference to full metadata), "
            "transcribe (kick off Whisper transcription — async, returns transcript_id), "
            "transcript_status (check transcription progress and get text when done), "
            "content_pack (generate titles/summary/chapters/YT description from transcript — async, returns task_id)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "detail", "resolve", "transcribe", "transcript_status", "content_pack"],
                    "description": "list/search/detail=browse videos, resolve=normalize ref, transcribe=start Whisper, transcript_status=check progress, content_pack=generate content pack.",
                },
                "query": {
                    "type": "string",
                    "description": "Search term matching video title (prompt) or original filename. Required for search.",
                },
                "id": {
                    "type": "string",
                    "description": "Video UUID (for detail action).",
                },
                "sequential_number": {
                    "type": "integer",
                    "description": "Video sequential number (for detail action, alternative to id).",
                },
                "video_type": {
                    "type": "string",
                    "description": "Filter by type: uploaded, text_to_video, image_to_video, etc.",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (default: completed).",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max items to return (default 10, max 50).",
                },
                "transcript_id": {
                    "type": "string",
                    "description": "Transcript UUID (for transcript_status action).",
                },
                "language": {
                    "type": "string",
                    "description": "Language code for transcription (default: en).",
                },
            },
            "required": ["action"],
        },
    },

    # ── Agent Delegation (generic) ──────────────────────────────────────────
    {
        "type": "function",
        "name": "run_agent",
        "description": (
            "Delegate a task to a specialized agent. Use when the user asks to "
            "Run any of 58 specialized agents across 10 domains: "
            "media creation/editing, research & analysis, strategy & content, "
            "executive & orchestration, stock & markets, sports & betting, "
            "blockchain audit, content studio, podcast, and training & security. "
            "(Session 1218 P2: 22 zero-execution agents trimmed from the enum.)"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "agent_name": {
                    "type": "string",
                    "enum": [
                        # ── Media Creation & Editing ──
                        "image_generation_agent", "image_editing_agent",
                        "video_generation_agent", "video_editing_agent",
                        "resolve_agent",
                        "audio_generation_agent", "three_d_generation_agent",
                        "character_training_agent", "talking_character_agent",
                        # ── Research & Analysis ──
                        "research_agent",
                        "trend_analysis_agent", "opportunity_scoring_agent",
                        "platform_audit_agent",
                        "thinking_agent",
                        # ── Strategy & Content ──
                        "brand_identity_agent", "seo_optimizer_agent",
                        "social_media_agent", "editor_agent",
                        "content_audit_agent",
                        "creative_director_agent",
                        # ── Business Research ──
                        "competitor_analysis_agent", "customer_research_agent",
                        "brand_strategy_agent", "content_strategy_agent",
                        "marketing_strategy_agent", "content_writer_agent",
                        # ── Executive & Orchestration ──
                        "cto_agent", "coo_agent",
                        "meeting_coordinator_agent",
                        "campaign_orchestrator_agent",
                        "opportunity_pipeline_agent",
                        "ai_series_workflow_agent",
                        "workflow_orchestration_agent",
                        "system_intelligence_agent",
                        "strategic_review",
                        "create_brand_video", "create_project_from_research",
                        # ── Development (Session 1093 P3) ──
                        "code_review_agent",
                        # ── Stock & Markets ──
                        "stock_audit_coordinator", "stock_analyst_agent",
                        "bear_case_agent",
                        "market_intelligence_agent",
                        "market_intelligence_coordinator",
                        # ── Sports & Betting ──
                        "prediction_market_analyst",
                        "game_predictor", "line_movement_analyzer",
                        "sharp_action_detector",
                        # ── Blockchain Audit ──
                        "blockchain_audit_coordinator",
                        "whale_watcher_agent",
                        # ── Content Studio ──
                        "autonomous_content_studio_coordinator",
                        "topic_miner_agent", "contrarian_agent",
                        "performance_analyst_agent", "voice_critic_agent",
                        "content_diversity_orchestrator",
                        # ── Podcast ──
                        "podcast_coordinator_agent",
                        # ── Training & Security ──
                        "trained_creation_agent", "memory_isolation_agent", "security_agent",
                    ],
                    "description": (
                        "Which agent to run. 58 agents across 10 domains. "
                        "Media: image/video/audio/3D generation & editing, resolve (DaVinci). "
                        "Research: research, trend analysis, opportunity scoring, thinking. "
                        "Strategy: brand identity, SEO, social media, content audit, editor, creative director. "
                        "Markets: stock analyst, bear case, market intelligence coordinator. "
                        "Sports: game predictor, line movement, sharp action, prediction market analyst. "
                        "Blockchain: blockchain audit coordinator, whale watcher. "
                        "Studio: topic miner, contrarian, performance analyst, voice critic, content diversity orchestrator. "
                        "Podcast: coordinator. "
                        "system_intelligence_agent = platform health reports."
                    ),
                },
                "task": {"type": "string", "description": "Task description for the agent"},
                "workspace_id": {
                    "type": "string",
                    "description": (
                        "UUID of the workspace this agent should operate in. "
                        "Any deliverables the agent produces will be saved into "
                        "this workspace. Pass this as a structured parameter — "
                        "mentioning it inside the `task` text is not enough; "
                        "the dispatcher only reads it from here or from "
                        "`context.workspace_id`. When omitted, the router falls "
                        "back to the user's active workspace, then to the "
                        "System Autonomous Workspace (orphan-producing path)."
                    ),
                },
                "content": {
                    "type": "string",
                    "description": (
                        "Raw content the agent should operate on. Use for "
                        "agents that score / critique / edit a blob of text "
                        "(VoiceCriticAgent, EditorAgent, etc.) where the "
                        "content itself is the subject, not a task "
                        "description. Session 1094: added so Rigby can "
                        "structurally pass content to critique/edit agents "
                        "without packing it into `task` text where GPT-5.2 "
                        "may strip or truncate it. Mirrors the #1974 "
                        "workspace_id pattern. When provided, it is promoted "
                        "to `context.content` before dispatch."
                    ),
                },
                "context": {
                    "type": "object",
                    "description": (
                        "Additional context. May include workspace_id (prefer "
                        "the top-level param above instead), conversation_id, "
                        "content_type, tone, blog_id, research, etc."
                    ),
                },
                "auto_followup": {
                    "type": "boolean",
                    "description": (
                        "Session 1178 Phase 2 — control the implicit "
                        "completion-banner subscription. Defaults to true: "
                        "every PA dispatch auto-creates an armed "
                        "AgentFollowupSubscription so the user sees a banner "
                        "and Rigby-authored chat bubble when the agent "
                        "finishes (within a 30s TTL window). Pass false to "
                        "suppress the implicit subscription — useful for "
                        "test-harness dispatches, sub-tasks that are part of "
                        "a larger orchestrated flow, or any case where the "
                        "completion event would be noise. The explicit "
                        "schedule_followup tool can still be called to "
                        "override after_seconds or schedule a delayed wake."
                    ),
                    "default": True,
                },
            },
            "required": ["agent_name", "task"],
        },
    },

    # ── Persona Agents (DB-only specialists) ─────────────────────────────────
    {
        "type": "function",
        "name": "persona_tool",
        "description": (
            "Access 139 specialized AI persona agents across 14 categories: "
            "income generation, career development, job search, content creation, "
            "marketing, finance, investment, AI/ML, business strategy, analytics, "
            "creative design, automation, consulting, and research. "
            "Use 'list' to browse available personas by category. "
            "Use 'invoke' to delegate a task to a specific persona. "
            "Use when the user asks for help with income, careers, job hunting, "
            "freelancing, budgeting, resume writing, interview prep, marketing "
            "campaigns, data analysis, business planning, or any specialized skill "
            "not covered by the core creative/research agents."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "invoke"],
                    "description": "list = browse personas by category; invoke = run a specific persona",
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "income", "career", "job_search", "content", "marketing",
                        "finance", "investment", "ai_ml", "business", "analytics",
                        "creative", "automation", "consulting", "research",
                    ],
                    "description": "Filter personas by category (for list action)",
                },
                "persona_name": {
                    "type": "string",
                    "description": "Exact name of the persona to invoke (from list results)",
                },
                "task": {
                    "type": "string",
                    "description": "Task description for the persona to execute",
                },
            },
            "required": ["action"],
        },
    },

    # ── Legal Doc Drafter ───────────────────────────────────────────────────
    {
        "type": "function",
        "name": "legal_doc_drafter_agent",
        "description": (
            "Draft legal documents: contracts, agreements, legal letters, "
            "compliance documents. Use when the user asks about legal documents, "
            "contracts, legal drafting, or compliance."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Legal document task description"},
                "document_type": {"type": "string", "description": "Type of legal document"},
                "context": {"type": "object", "description": "Additional context"},
            },
            "required": ["task"],
        },
    },

    # ── Platform Awareness ─────────────────────────────────────────────────
    {
        "type": "function",
        "name": "platform_awareness_tool",
        "description": (
            "Enumerate platform capabilities: UI routes, studios, feature flags, "
            "and deploy verification. Use when the user asks what pages exist, "
            "what features are available, what the app can do, about routes, "
            "capabilities, studios, or wants to verify a deployment."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "get_manifest", "list_routes", "check_route",
                        "system_overview", "verify_deploy",
                        "list_api_dependencies", "tool_registry",
                    ],
                    "description": (
                        "get_manifest: full manifest (routes, studios, capabilities). "
                        "list_routes: filter routes by category or auth. "
                        "check_route: verify a specific route exists. "
                        "system_overview: summary counts. "
                        "verify_deploy: run deploy health checks (admin only). "
                        "list_api_dependencies: list API endpoints a route depends on. "
                        "tool_registry: list all PA tools with names, descriptions, and actions."
                    ),
                },
                "category": {
                    "type": "string",
                    "enum": ["command", "studio", "intelligence", "domain", "reference", "admin", "auth"],
                    "description": "Filter routes by category (for list_routes)",
                },
                "path": {
                    "type": "string",
                    "description": "Route path to check (for check_route) or filter (for list_api_dependencies), e.g. '/governance'",
                },
                "auth_required": {
                    "type": ["string", "boolean"],
                    "description": (
                        "Filter routes by auth requirement (for list_routes). OMIT unless explicitly filtering. "
                        "Pass true → auth-required routes only. Pass the STRING 'false' → public routes only. "
                        "Python boolean false is treated as LLM autofill and ignored (Session 1228 PR-A, mirrors "
                        "deliverable_tool has_initiative semantics from Session 1227)."
                    ),
                },
                "writes_only": {
                    "type": "boolean",
                    "description": "If true, only return mutation (write) endpoints (for list_api_dependencies)",
                },
            },
            "required": ["action"],
        },
    },

    # ── Studio Tool (unified generation) ─────────────────────────────────────
    {
        "type": "function",
        "name": "studio_tool",
        "description": (
            "Unified creative studio: generate images, videos, and audio. "
            "Use when the user asks to create or generate media content — "
            "'generate an image', 'create a video', 'make audio', 'TTS'. "
            "Also check job status and list recent media jobs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "generate_image", "generate_video", "generate_audio",
                        "create_talking_video",
                        "job_status", "list_jobs",
                    ],
                    "description": (
                        "generate_image: create an AI image from prompt. "
                        "generate_video: create a video from prompt/image. "
                        "generate_audio: text-to-speech audio. "
                        "create_talking_video: generate a character image from prompt AND create talking video in one step — provide 'prompt' for image description and 'script' for dialogue. "
                        "(Session 1222 P2: removed 'generate_talking_video' — the existing-image entry point — because TalkingCharacterAgent had zero AgentExecution rows all-time.) "
                        "job_status: check status of a generation job. "
                        "list_jobs: recent generation history."
                    ),
                },
                "prompt": {"type": "string", "description": "Generation prompt / text to speak"},
                "style": {"type": "string", "description": "Visual style or mood (for image/video)"},
                "model": {"type": "string", "description": "Specific model to use (e.g. dall-e-3, stability-ai)"},
                "width": {"type": "integer", "description": "Image width in pixels"},
                "height": {"type": "integer", "description": "Image height in pixels"},
                "duration": {"type": "integer", "enum": [4, 5, 6, 8, 10], "description": "Video duration in seconds (default: 10 for talking videos)"},
                "ratio": {"type": "string", "enum": ["1920:1080", "1080:1920", "1280:720", "720:1280"], "description": "Video aspect ratio"},
                "image_url": {"type": "string", "description": "URL of character image to animate (for generate_talking_video)"},
                "script": {"type": "string", "description": "Text script for the character to speak (for generate_talking_video)"},
                "voice": {
                    "type": "string",
                    "enum": [
                        "Rachel", "Drew", "Clyde", "Paul", "Aria", "Domi",
                        "Dave", "Antoni", "Sarah", "Josh", "Bella", "Charlotte",
                    ],
                    "description": (
                        "ElevenLabs voice for TTS. "
                        "Female: Rachel (warm), Aria (professional), Domi (energetic), Sarah (soft), Bella (storyteller), Charlotte (clear). "
                        "Male: Drew (clear), Clyde (deep/authoritative), Paul (friendly), Dave (casual), Antoni (narrator), Josh (upbeat)."
                    ),
                },
                "mode": {"type": "string", "enum": ["loop", "multi_clip"], "description": "Video mode for generate_talking_video (default: multi_clip). loop = fast/cheap but visible seams; multi_clip = unique clips, no loops, 3-6x cost"},
                "sync_mode": {"type": "string", "enum": ["loop", "cut_off", "bounce"], "description": "Lip sync mode for generate_talking_video (default: cut_off)"},
                "lipsync_model": {"type": "string", "enum": ["auto", "latentsync", "sync_labs"], "description": "Lip sync model for generate_talking_video"},
                "color_grade": {
                    "type": "string",
                    "enum": [
                        "cinematic_warm", "cinematic_cool", "cyberpunk_neon",
                        "vintage_film", "moody_dark", "natural_vibrant",
                        "sunset_golden", "nordic_cool", "pastel_soft",
                    ],
                    "description": (
                        "DaVinci Resolve color grade applied after lip sync. "
                        "Suggest to the user when generating talking videos — adds professional polish. "
                        "cinematic_warm/cool for professional, cyberpunk_neon for tech/futuristic, "
                        "vintage_film for retro, moody_dark for dramatic."
                    ),
                },
                "job_id": {"type": "string", "description": "Job/task ID for status check"},
                "limit": {"type": "integer", "description": "Max items for list_jobs (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1048: Task Volume Breakdown ──────────────────────────────────
    {
        "type": "function",
        "name": "task_breakdown_tool",
        "description": (
            "Celery task volume breakdown and load analysis. Use when the user "
            "asks about task load, what's driving Celery load, top tasks, "
            "failing tasks, task execution stats, task volume, task breakdown, "
            "Celery performance, or worker utilization."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["summary", "drilldown"],
                    "description": (
                        "summary: aggregated task volume with totals, top tasks, "
                        "percentiles, and agent breakdown. "
                        "drilldown: recent executions for a specific task name."
                    ),
                },
                "window": {
                    "type": "string",
                    "enum": ["15m", "60m", "2h", "6h", "24h"],
                    "description": "Time window (default 60m)",
                },
                "task_name": {
                    "type": "string",
                    "description": "Full task name for drilldown (e.g. core.tasks.execute_agent_task)",
                },
                "status": {
                    "type": "string",
                    "enum": ["SUCCESS", "FAILURE", "STARTED"],
                    "description": "Filter drilldown executions by status (e.g. FAILURE to see only failures)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max items to return (default 25 for summary, 50 for drilldown)",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1088: Individual Agent Schemas ──────────────────────────────
    # These give the LLM direct routing signals instead of going through
    # the generic `run_agent` meta-tool. Each maps 1:1 to a ToolDispatcher
    # handler registered via _handle_agent_tool.

    # ── Image Editing ────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "image_editing_agent",
        "description": (
            "Edit an existing image: upscale, remove background, apply filters, "
            "crop, resize, add text overlay, style transfer, inpainting, outpainting. "
            "Use when the user wants to modify, enhance, or transform an existing image."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "What to do with the image (e.g. 'remove background from this image', 'upscale 4x')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: image_url, edit_type, parameters",
                },
            },
            "required": ["task"],
        },
    },

    # ── Video Editing ────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "video_editing_agent",
        "description": (
            "Edit an existing video: trim, cut, speed change, add effects, "
            "concatenate clips, add text overlay, transitions, reverse. "
            "Use when the user wants to modify, trim, speed up, slow down, "
            "or combine existing video clips. Uses ffmpeg."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "What to do with the video (e.g. 'trim to first 10 seconds', 'speed up 2x', 'add fade transition')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: video_url, edit_type, start_time, end_time, speed_factor",
                },
            },
            "required": ["task"],
        },
    },

    # ── 3D Generation ────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "three_d_generation_agent",
        "description": (
            "Generate 3D models from text descriptions or images. "
            "Use when the user asks to create a 3D model, 3D object, "
            "3D scene, or convert an image to 3D."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Description of the 3D model to generate",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: style, format, reference_image_url",
                },
            },
            "required": ["task"],
        },
    },

    # ── Character Training ───────────────────────────────────────────────────
    {
        "type": "function",
        "name": "character_training_agent",
        "description": (
            "Train a custom character model from reference images for consistent "
            "character generation. Use when the user wants to create a character, "
            "train a character model, upload character reference images, or create "
            "a consistent character identity."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Character training task (e.g. 'train a character named Alex from these reference images')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: character_name, reference_image_urls, style, description",
                },
            },
            "required": ["task"],
        },
    },

    # ── Competitor Analysis ──────────────────────────────────────────────────
    {
        "type": "function",
        "name": "competitor_analysis_agent",
        "description": (
            "Analyze competitors: market positioning, strengths, weaknesses, "
            "product comparison, pricing analysis, market share. Use when the "
            "user asks about competitors, competitive landscape, market analysis, "
            "or wants to compare products/services against rivals."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Competitor analysis task (e.g. 'analyze top competitors in the AI writing space')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: industry, competitors, focus_areas",
                },
            },
            "required": ["task"],
        },
    },

    # ── Customer Research ────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "customer_research_agent",
        "description": (
            "Research target customers: demographics, pain points, buying behavior, "
            "user personas, customer journey mapping, needs analysis. Use when the "
            "user asks about target audience, customer segments, user research, "
            "or wants to understand their customers better."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Customer research task (e.g. 'create user personas for a SaaS productivity tool')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: product, industry, target_market",
                },
            },
            "required": ["task"],
        },
    },

    # ── Brand Strategy ───────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "brand_strategy_agent",
        "description": (
            "Develop brand strategy: positioning, messaging, voice, identity, "
            "brand architecture, differentiation. Use when the user asks about "
            "branding, brand positioning, brand identity, messaging strategy, "
            "or brand differentiation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Brand strategy task (e.g. 'create a brand positioning statement for our AI platform')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: company, product, target_audience, competitors",
                },
            },
            "required": ["task"],
        },
    },

    # ── Content Strategy ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "content_strategy_agent",
        "description": (
            "Develop content strategy: editorial calendar, content pillars, "
            "distribution plan, SEO strategy, content audit. Use when the "
            "user asks about content planning, editorial strategy, content "
            "calendar, content distribution, or content optimization."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Content strategy task (e.g. 'create a 3-month content calendar for our tech blog')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: audience, topics, channels, goals",
                },
            },
            "required": ["task"],
        },
    },

    # ── Marketing Strategy ───────────────────────────────────────────────────
    {
        "type": "function",
        "name": "marketing_strategy_agent",
        "description": (
            "Develop marketing strategy: campaign planning, channel strategy, "
            "go-to-market plan, growth strategy, marketing funnel optimization. "
            "Use when the user asks about marketing plans, campaigns, growth "
            "strategies, go-to-market, or marketing channels."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Marketing strategy task (e.g. 'create a go-to-market plan for our new product launch')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: product, budget, timeline, target_market",
                },
            },
            "required": ["task"],
        },
    },

    # ── Content Writer ───────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "content_writer_agent",
        "description": (
            "Write content: blog posts, articles, marketing copy, social media "
            "posts, email newsletters, product descriptions, whitepapers, case "
            "studies. Use when the user asks to write, draft, or create any "
            "written content. Saves output to Deliverables library."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Writing task (e.g. 'write a blog post about AI trends in 2026')",
                },
                # Session 1184 PR-D: promoted content_type to an explicit enum
                # at the tool-call level. Previously it was buried inside the
                # freeform `context` dict, which let GPT-5.2 pick invalid
                # values (e.g. "deliverable" — the container, not a type).
                # An invalid value failed the dispatch hard and broke
                # provenance forensic runs. Now the enum constrains selection
                # to the seven types ContentWriterAgent actually knows how to
                # produce. Note: "internal_document" covers diagnostic/handoff
                # docs, technical specs, planning notes — anything that's not
                # one of the other six.
                "content_type": {
                    "type": "string",
                    "enum": [
                        "blog_post",
                        "podcast_script",
                        "video_script",
                        "article",
                        "social_thread",
                        "newsletter",
                        "internal_document",
                    ],
                    "description": (
                        "Content format to produce. Use 'internal_document' for "
                        "diagnostics, handoffs, planning notes, or any doc that "
                        "isn't externally publishable."
                    ),
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: tone, audience, word_count, keywords",
                },
            },
            "required": ["task"],
        },
    },

    # ── Workflow Orchestration ────────────────────────────────────────────────
    {
        "type": "function",
        "name": "workflow_orchestration_agent",
        "description": (
            "Orchestrate multi-step workflows that chain multiple agents together. "
            "Use when the user wants a complex workflow: research then write, "
            "analyze then create, or any multi-agent pipeline that requires "
            "coordinating several agents in sequence."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Workflow description (e.g. 'research AI trends then write a blog post about the findings')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: steps, agents, output_format",
                },
            },
            "required": ["task"],
        },
    },

    # ── Strategic Review ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "strategic_review",
        "description": (
            "Conduct a strategic review: evaluate strategy, assess market position, "
            "review business model, SWOT analysis, strategic recommendations. "
            "Use when the user asks for a strategic review, strategy evaluation, "
            "SWOT analysis, or strategic assessment."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Strategic review task (e.g. 'conduct a SWOT analysis of our content platform')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: company, industry, focus_areas",
                },
            },
            "required": ["task"],
        },
    },

    # ── Create Brand Video (compound workflow) ───────────────────────────────
    {
        "type": "function",
        "name": "create_brand_video",
        "description": (
            "Create a brand video by orchestrating multiple agents: script writing, "
            "image generation, video generation, and editing. Use when the user "
            "wants to create a complete brand video, promotional video, or "
            "marketing video from scratch."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Brand video description (e.g. 'create a 30-second promotional video for our AI platform')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: brand, style, duration, target_audience, key_messages",
                },
            },
            "required": ["task"],
        },
    },

    # ── Create Project from Research (compound workflow) ─────────────────────
    {
        "type": "function",
        "name": "create_project_from_research",
        "description": (
            "Create a full project from research: web research, analysis, "
            "project planning, deliverable creation. Use when the user wants "
            "to research a topic and create a complete project or initiative "
            "from the findings."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Research-to-project task (e.g. 'research the AI agent market and create a project plan')",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: topic, scope, output_format, depth",
                },
            },
            "required": ["task"],
        },
    },


    # ── Session 1069: Platform Config — runtime environment introspection ────
    {
        "type": "function",
        "name": "platform_config_tool",
        "description": (
            "Inspect runtime platform configuration: active LLM providers, "
            "environment variables (secrets masked), Django settings, feature flags, "
            "and Railway service info. Use when the user asks about configuration, "
            "what provider is active, environment setup, what settings are in use, "
            "or debugging 'works locally but not on Railway' issues."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["overview", "llm_providers", "env_vars", "feature_flags", "web_config"],
                    "description": (
                        "overview=key settings summary from this service (default), "
                        "llm_providers=active LLM provider details, "
                        "env_vars=all env vars with secrets masked, "
                        "feature_flags=platform feature flags and toggles, "
                        "web_config=fetch config from the web service (compare vs celery-pa)"
                    ),
                },
            },
        },
    },

    # ── Session 1069: DB Health — migration status and schema introspection ──
    {
        "type": "function",
        "name": "db_health_tool",
        "description": (
            "Check database health: migration status, table row counts, "
            "PostgreSQL connection info, pgvector extension status, and schema "
            "validation. Use when the user asks about database health, pending "
            "migrations, table sizes, pgvector status, or database issues."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["overview", "migrations", "tables", "pgvector", "verify_table", "search_tables", "learning_stats"],
                    "description": (
                        "overview=connection + migration summary (default), "
                        "migrations=list unapplied migrations, "
                        "tables=row counts for key tables, "
                        "pgvector=vector extension status and embedding counts, "
                        "verify_table=check if a specific table exists with columns and row count, "
                        "search_tables=find tables by prefix (default core_), "
                        "learning_stats=learning feedback loop metrics (readback events, consultation rates, UserAgentLearning counts)"
                    ),
                },
                "table_name": {
                    "type": "string",
                    "description": "Table name to verify (for verify_table action)",
                },
                "prefix": {
                    "type": "string",
                    "description": "Table name prefix to search (for search_tables, default 'core_')",
                },
                "env": {
                    "type": "string",
                    "enum": ["local", "prod"],
                    "description": (
                        "Target environment. 'local' (default) queries the local DB. "
                        "'prod' delegates to /api/db-health-rpc/ on the configured prod URL — "
                        "requires PA_DB_HEALTH_RPC_URL and PA_DB_HEALTH_RPC_CLIENT_TOKEN env "
                        "vars. Returned dict always carries an 'env' tag so cross-env "
                        "comparisons are unambiguous."
                    ),
                },
            },
        },
    },

    # ── HTTP Smoke Test ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "http_smoke_test",
        "description": (
            "Run HTTP smoke tests against platform API endpoints. "
            "Verifies endpoints return correct status codes and response shapes. "
            "Supports multi-step flows with variable capture (e.g., create incident then verify). "
            "Use when asked to verify endpoints, check if deploys succeeded, "
            "or run health checks. Built-in suites: 'cockpit_health' (18 cockpit GETs), "
            "'cockpit_incidents_crud' (8-step CRUD lifecycle), "
            "'pa_tools_smoke' (14 checks across boardroom, initiatives, celery, spiders, manifest), "
            "'auth_regression' (5 checks verifying permission classes on protected endpoints), "
            "'deploy_verify' (5 post-deploy sanity checks)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "suite": {
                    "type": "string",
                    "enum": ["cockpit_health", "cockpit_incidents_crud", "pa_tools_smoke", "auth_regression", "deploy_verify"],
                    "description": "Run a built-in test suite instead of custom steps",
                },
                "environment": {
                    "type": "string",
                    "enum": ["railway_prod", "local"],
                    "description": (
                        "Target environment. If omitted, auto-detects from the "
                        "running process's RAILWAY_ENVIRONMENT env var: set ⇒ "
                        "railway_prod, absent ⇒ local. Only pass this explicitly "
                        "when you need to override the running context (e.g., "
                        "smoke-test prod from local PA)."
                    ),
                },
                "steps": {
                    "type": "array",
                    "description": (
                        "Custom test steps (ignored if suite is set). Each step: "
                        "{name, method, path, body?, assert?: [{check, expected, key?, path?, operator?}], "
                        "capture?: [{json_path, as}]}"
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                            "path": {"type": "string"},
                            "body": {"type": "object"},
                        },
                    },
                },
                "fail_fast": {
                    "type": "boolean",
                    "description": "Stop on first failure (default true)",
                },
                "return_body": {
                    "type": "boolean",
                    "description": "Include full JSON response body in results (default false). Use for debugging endpoint responses.",
                },
                "max_body_bytes": {
                    "type": "integer",
                    "description": "Max response body size in bytes when return_body=true (default 50000, max 250000)",
                },
            },
        },
    },

    # ── Learning Loop ───────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "learning_tool",
        "description": (
            "Manage the PA's learned tool-usage insights. Use when the user "
            "asks about what the PA has learned, wants to review pending "
            "insights, or wants to approve/reject learned patterns."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list_candidates", "list_approved", "list_expired", "approve", "reject", "stats"],
                    "description": "Action to perform on tool insights",
                },
                "id": {"type": "string", "description": "UUID of insight to approve/reject"},
                "tool_name": {"type": "string", "description": "Filter by tool name"},
                "limit": {"type": "integer", "description": "Max items to return (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Competitor Comparison (Session G1) ─────────────────────────────────────
    {
        "type": "function",
        "name": "competitor_comparison_tool",
        "description": (
            "Generate, check status, list, view, delete, or regenerate competitor comparisons. "
            "Produces a structured side-by-side analysis between a competitor "
            "and Donkey Betz using RAG evidence from ingested documents. "
            "Use when the user asks to compare competitors, do competitive "
            "analysis, or review a competitor's platform."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["generate", "status", "list", "detail", "delete", "regenerate", "create_initiative_from_gap", "export_markdown"],
                    "description": "Action to perform",
                },
                "competitor_name": {
                    "type": "string",
                    "description": "Name of the competitor to compare against (required for generate)",
                },
                "source_document_id": {
                    "type": "string",
                    "description": "UUID of the source document to extract evidence from",
                },
                "comparison_id": {
                    "type": "string",
                    "description": "UUID of an existing comparison (for status/detail/delete/regenerate/create_initiative_from_gap/export_markdown)",
                },
                "focus_areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional search queries to focus the comparison",
                },
                "gap_index": {
                    "type": "integer",
                    "description": "Index of the gap to create an initiative from (0-based, for create_initiative_from_gap)",
                },
                "save": {
                    "type": "boolean",
                    "description": "Whether to save the markdown export as a Deliverable (default true, for export_markdown)",
                },
                "auto_research": {
                    "type": "boolean",
                    "description": "Auto-discover and ingest competitor sources before comparing (default true, skipped if source_document_id provided)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results for list action (default 10)",
                },
            },
            "required": ["action"],
        },
    },
    # ── Workflow Run Tool (multi-step orchestration) ────────────────────
    {
        "type": "function",
        "name": "workflow_run_tool",
        "description": (
            "Start, poll, list, detail, or cancel multi-step workflow runs. "
            "Currently supports 'source_pack_comparison': auto-collect competitor "
            "sources from web search + spiders, ingest as Documents, embed, "
            "generate RAG-powered comparison, and export as Deliverable. "
            "Use when the user asks for a full source-pack comparison workflow."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["start", "status", "list", "detail", "cancel"],
                    "description": "Action to perform",
                },
                "workflow_key": {
                    "type": "string",
                    "enum": ["source_pack_comparison"],
                    "description": "Workflow type (default: source_pack_comparison)",
                },
                "competitor_name": {
                    "type": "string",
                    "description": "Competitor name (required for start)",
                },
                "queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Custom search queries (auto-generated if omitted)",
                },
                "target_count": {
                    "type": "integer",
                    "description": "Max URLs to ingest (default 8)",
                },
                "comparison_id": {
                    "type": "string",
                    "description": "Existing comparison UUID to reuse",
                },
                "run_id": {
                    "type": "string",
                    "description": "UUID of a workflow run (for status/detail/cancel)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results for list action (default 10)",
                },
            },
            "required": ["action"],
        },
    },

    # ── Persistent Memory ────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "remember_tool",
        "description": (
            "Save something to persistent memory so you remember it across sessions. "
            "Use when the user says 'remember this', 'save this preference', 'note that I...', "
            "'keep in mind', 'always do X', 'never do Y', 'I prefer...', or similar. "
            "Also use proactively when the user shares important preferences, goals, constraints, "
            "or corrections that should persist."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["save", "list", "delete", "search"],
                },
                "content": {
                    "type": "string",
                    "description": "What to remember (for save action)",
                },
                "memory_type": {
                    "type": "string",
                    "enum": [
                        "preference", "goal", "constraint", "instruction",
                        "decision", "context", "skill", "project",
                    ],
                    "description": "Category of memory (default: preference)",
                },
                "importance": {
                    "type": "integer",
                    "description": "1-10 importance level (default: 7)",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization",
                },
                "memory_id": {
                    "type": "integer",
                    "description": "Memory ID for delete action",
                },
                "query": {
                    "type": "string",
                    "description": "Search query for search action",
                },
            },
            "required": ["action"],
        },
    },

    # ── Conversation Memory ──────────────────────────────────────────────────
    {
        "type": "function",
        "name": "conversation_tool",
        "description": (
            "Search and retrieve past PA conversations. Use to recall previous "
            "discussions, find decisions made, or summarize conversation threads. "
            "Use when the user asks 'what did we discuss', 'do you remember', "
            "'what did I say about', or references a past conversation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get", "search", "summary", "pin_memory", "recent"],
                    "description": (
                        "get: retrieve full conversation by conversation_id. "
                        "search: semantic + keyword search across all conversations. "
                        "summary: dispatch async LLM summarization of a conversation. "
                        "pin_memory: save a decision/fact as durable memory. "
                        "recent: list most recent conversations with IDs and timestamps."
                    ),
                },
                "conversation_id": {"type": "string", "description": "Conversation ID (e.g. 'pa-33e4d55d31b6')"},
                "query": {"type": "string", "description": "Search query for finding past conversations"},
                "days_back": {"type": "integer", "description": "Limit search to last N days"},
                "limit": {"type": "integer", "description": "Max results/turns to return (default 10)"},
                "offset": {"type": "integer", "description": "Skip first N turns (for pagination with get action)"},
                "pin_title": {"type": "string", "description": "Title for the pinned memory"},
                "pin_content": {"type": "string", "description": "Content to pin as durable memory"},
                "pin_tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags for the pinned memory",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1078: Work Tool — gateway for initiatives + action items ────────
    {
        "type": "function",
        "name": "work_tool",
        "description": (
            "Work execution gateway: manage initiatives and action items. "
            "List, detail, create, and promote initiatives; list, start, complete, "
            "and clean up action items. Use this instead of initiative_tool for all "
            "initiative and action item operations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "initiative_list", "initiative_detail", "initiative_deliverables",
                        "initiative_create",
                        "initiative_promote", "initiative_update_status",
                        "initiative_update", "initiative_link",
                        "action_item_list", "action_item_start", "action_item_complete",
                        "action_item_cleanup", "bulk_cleanup",
                        "agent_conversations", "workflows",
                        "stats",
                    ],
                    "description": (
                        "initiative_list: list initiatives (filters: status, owner, stage). "
                        "initiative_detail: full details of one initiative (by id, human_id, seq_id, or name). "
                        "initiative_deliverables: paginated reverse projection — list deliverables linked to a given initiative_id (Session 1194 Plan B). Use this when answering 'what work product belongs to initiative X?'. "
                        "initiative_create: create a new initiative (name, description). "
                        "initiative_promote: move TRIAGE/ON_HOLD → ACTIVE. "
                        "initiative_update_status: change initiative status (id + status: ACTIVE/TRIAGE/ON_HOLD/COMPLETED/ARCHIVED). Auto-cancels pending action items on COMPLETED/ARCHIVED. "
                        "initiative_update: patch field(s) on an initiative — bind target_workspace_id, edit description, or set kind (project/recurring_artifact/investigation/spec_backlog). Idempotent: no-op write returns updated_fields=[]. Session 1202 §A.1. "
                        "initiative_link: write bidirectional related_initiatives entry between parent_id and child_id with relation (spawns | spawned_from). Mirror direction is computed automatically per §6.4. Idempotent: re-running same (parent, child, relation) is a no-op. Session 1202 §A.1. "
                        "action_item_list: list action items (filters: status, priority, initiative_id). "
                        "action_item_start: mark an action item as in_progress. "
                        "action_item_complete: mark an action item as completed. "
                        "action_item_cleanup: find/cancel junk action items (dry_run default true). "
                        "bulk_cleanup: archive stalled, noise, and duplicate initiatives (dry_run default true). "
                        "agent_conversations: browse multi-agent conversations. "
                        "workflows: recent workflow/orchestration executions. "
                        "stats: aggregate counts across initiatives, action items, "
                        "workflows, and agent conversations — use this for a platform "
                        "status snapshot instead of listing everything."
                    ),
                },
                "id": {
                    "type": "string",
                    "description": "Initiative or action item ID (UUID, INIT-000001, or seq number).",
                },
                "name": {
                    "type": "string",
                    "description": "Search by name (for initiative_detail) or initiative title (for initiative_create).",
                },
                "description": {
                    "type": "string",
                    "description": "Description for initiative_create.",
                },
                "status": {
                    "type": "string",
                    "description": (
                        "For initiative_list: ACTIVE/TRIAGE/ON_HOLD/COMPLETED/ARCHIVED/all. "
                        "For action_item_list: pending/in_progress/completed/blocked/cancelled/all."
                    ),
                },
                "priority": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"],
                    "description": "Filter action items by priority.",
                },
                "initiative_id": {
                    "type": "string",
                    "description": "Filter action items by initiative ID.",
                },
                "owner": {
                    "type": "string",
                    "description": "Filter initiatives by owner (me/unowned/agent_name).",
                },
                "notes": {
                    "type": "string",
                    "description": "Completion notes for action_item_complete.",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": (
                        "For action_item_cleanup / bulk_cleanup / bulk_auto_assign: "
                        "true to preview (DEFAULT for all three), false to execute. "
                        "Session 1228 PR-A — writes require BOTH dry_run=false AND "
                        "confirm=true (belt-and-suspenders against LLM autofill: "
                        "GPT-5.2 autofills declared optional booleans with False, so "
                        "the second-factor confirm gate prevents silent flips to "
                        "write mode). OMIT unless explicitly invoking write mode."
                    ),
                },
                "confirm": {
                    "type": "boolean",
                    "description": (
                        "For action_item_cleanup / bulk_cleanup / bulk_auto_assign: "
                        "explicit second-factor confirmation required (along with "
                        "dry_run=false) to actually apply writes. Defaults to false. "
                        "Session 1228 PR-A. Pass true ONLY when the caller has "
                        "previewed and is committing to the write."
                    ),
                },
                "limit": {"type": "integer", "description": "Max results (default 50)."},
                "offset": {"type": "integer", "description": "Skip first N results for pagination."},
                # ── Session 1202 — Connectivity Roadmap §A.1 params ────────────
                "target_workspace_id": {
                    "type": "string",
                    "description": "For initiative_update: UUID of ProjectWorkspace to bind. OMIT entirely (or pass empty string / null) to leave the current binding unchanged. Unbinding via this action is not supported — use a future explicit sentinel if you need it.",
                },
                "kind": {
                    "type": "string",
                    "enum": ["project", "recurring_artifact", "investigation", "spec_backlog"],
                    "description": "For initiative_update: semantic kind (orthogonal to status) per INITIATIVES_FIRST_BACKBONE.md §6.4. OMIT (or pass empty string / null) to leave the current kind unchanged.",
                },
                "parent_id": {
                    "type": "string",
                    "description": "For initiative_link: UUID of the upstream Initiative (the one that has `relation` written first).",
                },
                "child_id": {
                    "type": "string",
                    "description": "For initiative_link: UUID of the downstream Initiative. Must differ from parent_id.",
                },
                "relation": {
                    "type": "string",
                    "enum": ["spawns", "spawned_from"],
                    "description": "For initiative_link: direction written on parent. `spawns` = parent led to child (downstream); `spawned_from` = parent was produced by child (upstream). Mirror written automatically.",
                },
                "note": {
                    "type": "string",
                    "description": "For initiative_link: optional context attached to both link entries.",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1202 §A.2: Diagnostics Tool — per-subsystem audit telemetry ─
    {
        "type": "function",
        "name": "diagnostics_tool",
        "description": (
            "Audit/inventory telemetry for subsystem health checks (Session 1202 §A.2). "
            "Distinct from ops_tool (which is SRE/SLO-focused on production reliability): "
            "diagnostics_tool surfaces per-component invocation counts and inventory state "
            "so Rigby can grade whether registered components are actually being used "
            "(advisors, LLM providers, beat schedules, workspaces). Read-only — no mutations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "advisor_invocations", "provider_calls",
                        "beat_schedule_health", "workspace_metrics",
                        "schema_handler_diff", "learning_bridge_writes",
                        "discord_health",
                    ],
                    "description": (
                        "advisor_invocations: per-advisor N-day invocation count from "
                        "AgentExecution log. Surfaces zero-invocation advisors so dead "
                        "personas are visible. Window via `window` (1d/7d/14d/30d/90d, default 7d). "
                        "provider_calls: per-LLM-provider call count + success/cost rollup "
                        "over the requested window. Flags registered providers that saw "
                        "zero calls. Source: LLMCallLog. "
                        "beat_schedule_health: PeriodicTask sorted by last_run_at ASC "
                        "(stalest first, NULLs first). Reports zero-run + zero-run-enabled "
                        "counts. Pagination via offset/limit. "
                        "workspace_metrics: per-ProjectWorkspace last_operation_at + "
                        "deliverable_count + is_active + allow_autonomous_writes. "
                        "Pagination via offset/limit. "
                        "schema_handler_diff: [PR-2 placeholder — not yet implemented]. "
                        "Programmatic schema-vs-handler gap detection. "
                        "learning_bridge_writes: [PR-2 placeholder — not yet implemented]. "
                        "Per-bridge 30d write counts. "
                        "discord_health: [PR-2 placeholder — not yet implemented]. "
                        "Bot uptime + 7d invocation counts + error rate."
                    ),
                },
                "window": {
                    "type": "string",
                    "enum": ["1d", "7d", "14d", "30d", "90d"],
                    "description": (
                        "Time window for advisor_invocations and provider_calls. "
                        "Default 7d. Ignored by other actions."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Max rows returned (beat_schedule_health, workspace_metrics). Default 50, max 200.",
                },
                "offset": {
                    "type": "integer",
                    "description": "Pagination offset (beat_schedule_health, workspace_metrics). Default 0.",
                },
                "include_disabled": {
                    "type": "boolean",
                    "description": "For beat_schedule_health: include disabled PeriodicTask rows (default true).",
                },
                "include_inactive": {
                    "type": "boolean",
                    "description": "For workspace_metrics: include inactive workspaces (default true).",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1078: Ops Tool — version, SLO status, failure signatures ──────
    {
        "type": "function",
        "name": "ops_tool",
        "description": (
            "Production operations surface: check deployment version/build info, "
            "monitor SLO compliance (task success rates, timeout rates, publish conversion), "
            "view top failure signatures, read agent timeout config/overrides, and run "
            "verification proof bundles (config + audit in one call). Use when asked about "
            "SLOs, ops health, deployment version, what's failing, production reliability, "
            "agent timeout config, timeout overrides, or verification/audit of agent settings."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "overview",
                        "version", "slo_status", "failure_signatures",
                        "tool_migration_report", "timeout_config_read", "proof_bundle",
                        "noise_metrics", "conversation_metrics",
                        "focus_mode_status", "focus_mode_update",
                        "celery_task_history", "execution_detail", "execution_search",
                        "memory_pressure", "top_consumers", "zombie_thread_rate",
                        "tenant_boundary_violations",
                        "staleness_warnings",
                        "recent_recycles",
                        "recent_bridge_calls",
                        "bridge_activity_digest",
                    ],
                    "description": (
                        "overview: one-shot ops snapshot — version + slo_status + top failure_signatures "
                        "+ noise_metrics in a single call. Use this when asked for an ops/platform "
                        "overview, system health, or a general 'how's production doing' question. "
                        "Default window 24h. "
                        "version: build/deploy metadata (git SHA, branch, Railway deployment, uptime) "
                        "PLUS S2759 staleness verdict — compares Daphne + Celery worker process start "
                        "times against git HEAD commit time. Returns staleness_verdict (FRESH / "
                        "STALE_DAPHNE / STALE_CELERY / STALE_BOTH / UNKNOWN) + head_commit_sha + "
                        "per-process ages. Use to answer 'is my running stack fresh?' at close of "
                        "any session touching ASGI-served or Celery-served code. Fix path (when "
                        "verdict != FRESH): `make recycle-all`. "
                        "slo_status: compute 8 SLOs with breach detection (task success, agent timeouts, "
                        "deliberation failures, publish conversion, PA tool success, HTTP errors). "
                        "failure_signatures: top error signatures by frequency with samples. "
                        "tool_migration_report: legacy vs gateway tool usage, deprecation readiness. "
                        "timeout_config_read: read agent wall-clock timeout config (code defaults + DB overrides). "
                        "proof_bundle: verification mode — returns timeout config + agent control audit log "
                        "+ initiative details in ONE read-only call. Use when user asks to verify or audit "
                        "agent config, timeout overrides, or initiative state. "
                        "noise_metrics: North Star coverage — how many runs hit revenue/content/sports paths vs noise. "
                        "Includes by-agent breakdown, trigger types, importance distribution, artifact types. "
                        "conversation_metrics: topic clustering, zombie rate, by-agent conversation counts. "
                        "focus_mode_status: read current Focus Mode config (enabled, mode, blocked topics, caps). "
                        "focus_mode_update: update Focus Mode config. Pass config_updates dict with keys to change "
                        "(enabled, mode, blocked_topics_autonomous, max_conversations_per_agent_per_hour, etc.). "
                        "celery_task_history: recent Celery task runs (success + failure) for a task name. "
                        "Pass task_name to filter (e.g. 'cleanup_stale'), window, limit, status. "
                        "execution_detail: look up a single AgentExecution by ID, includes last_heartbeat_at "
                        "and seconds_since_heartbeat. Pass execution_id. "
                        "execution_search: search recent AgentExecutions by agent_name/status/window. "
                        "Returns list with heartbeat info. "
                        "memory_pressure: per-worker RSS vs --max-memory-per-child cap, with "
                        "sustained-pressure CRIT detection and a soft downshift recommendation "
                        "(no auto Procfile edits). Reads the latest snapshot from "
                        "logs/worker_memory/*.jsonl. Use when asked about worker memory, OOM kills, "
                        "concurrency tuning, --max-memory-per-child, or pressure near caps. "
                        "top_consumers: per-task_name aggregation over CeleryTaskEvent for one "
                        "window. Returns count, total_seconds, mean_seconds, max_seconds, "
                        "p95_seconds (p95 computed server-side via PostgreSQL percentile_cont). "
                        "Single SQL aggregate query per call. Use when asked which task is eating "
                        "workers / hogging wall-clock / top by duration. Default window 24h, "
                        "default limit 20 (max 50). "
                        "zombie_thread_rate: per-agent, per-hour breakdown of wall-clock-timeout "
                        "spawns (Session 1219 P3 / 1220 P1 monitor). Each entry is a thread that "
                        "kept running after the agent's wall-clock fired because ThreadPoolExecutor "
                        "can't kill threads — bounded by --max-tasks-per-child recycling. Use when "
                        "asked about agent hangs, timeout rates, upstream-provider degradation. "
                        "Pass hours (default 24, max 168) and optional agent_name to filter. "
                        "Alert at >5/hour for any single agent. "
                        "staleness_warnings: query OpsRunEvent for S2759 staleness_warning "
                        "envelopes emitted by the check_process_staleness Beat task (30 min "
                        "cadence). Returns total_count + by_verdict + by_head_commit_sha "
                        "aggregates + sample_events (most-recent) with process detail preserved. "
                        "Optional filters: verdict (STALE_DAPHNE / STALE_CELERY / STALE_BOTH), "
                        "limit (default 20, max 100). Empty state includes a diagnostic note "
                        "cross-referencing ops_tool.version. Use to inspect accumulated stale-"
                        "process warnings — especially post-merge to verify make recycle-all was "
                        "run, or to audit which HEAD commits historically triggered warnings. "
                        "tenant_boundary_violations: query OpsRunEvent for I-0303 "
                        "tenant_boundary_violation envelopes (Phase 3 REPORT-ONLY substrate). "
                        "Returns total_count + by_task_name + by_failure_kind + by_task_and_kind "
                        "aggregates + sample_events (most-recent). Optional filters: task_name "
                        "(substring match), failure_kind (one of missing_row_id/row_not_found/"
                        "missing_acting_identity/acting_user_not_found/unregistered_model/"
                        "predicate_rejected), limit (default 20, max 100). Empty state includes "
                        "a diagnostic note. Use when asked about tenant boundary violations, "
                        "cross-tenant reports, I-0303 findings, or which tasks are surfacing "
                        "report-only warn violations. "
                        "recent_recycles: read the tail of logs/recycle_events.jsonl — the "
                        "first-party timeline of `make recycle-all` invocations. Each event "
                        "carries timestamp + git SHA + label + seconds_ago. Complements "
                        "ops_tool.version (live snapshot) and ops_tool.staleness_warnings "
                        "(post-hoc detection) with an operator-action timeline. Use when asked "
                        "'when did we last recycle?', 'which SHAs was the stack bounced at?', "
                        "or to trace a stale-Daphne diagnosis back to a specific merge. "
                        "Limit param (default 10, max 50). Fail-soft: returns empty list with "
                        "diagnostic note when the log file is missing. "
                        "recent_bridge_calls: S2890 — read recent ChatConversation rows whose "
                        "source starts with 'character-os-' (bridge tools consult_engine / "
                        "query_spider_data / agent_consult calling u-d-b's /api/pa/chat/). "
                        "Answers 'what bridge calls hit u-d-b in the last N minutes?' while "
                        "Chris explores character-os UI. Each item includes tool_name (parsed "
                        "from source suffix), question preview + truncation flag, "
                        "answer_preview + truncation flag, latency_ms (from response_time_ms), "
                        "conversation_id, workspace_id, user, agents_used, created_at. "
                        "Returns total_count + by_tool aggregate + items (capped at limit). "
                        "Payload: limit (default 20, max 100), since (ISO-8601), window "
                        "(1h/6h/24h/7d/30d), bridge_tool_name (optional: consult_engine / "
                        "query_spider_data / agent_consult to filter), workspace_id "
                        "(optional). Scoped to the requesting user unless the user is staff. "
                        "Fail-soft: empty items + diagnostic note when zero rows match. "
                        "bridge_activity_digest: S2891 — casual plain-English summary of "
                        "the same recent_bridge_calls data. Use when the operator asks "
                        "'what has character-os been up to?' and doesn't want the raw "
                        "items[] envelope. Returns narrative (one-sentence server-side "
                        "template) + structured_facts (total_count, by_tool, most_recent "
                        "{tool_name, question_preview, minutes_ago, latency_ms, user, "
                        "workspace_id, conversation_id}, median_latency_ms defined over "
                        "returned items only, window). No error_count field: "
                        "ChatConversation has no dedicated error/status column and "
                        "metadata.error is not a stable bridge-caller contract. Same "
                        "payload params + same scoping as recent_bridge_calls (delegates "
                        "internally). Fail-soft: 'No character-os bridge calls in the "
                        "last {window}.' narrative + empty structured_facts."
                    ),
                },
                "window": {
                    "type": "string",
                    "enum": ["1h", "6h", "24h", "7d", "30d"],
                    "description": "Time window for SLO, failure signature, and migration report computation (default 24h).",
                },
                "since": {
                    "type": "string",
                    "description": "ISO-8601 timestamp cutoff (overrides window). Use for precise time ranges, e.g. '2026-03-02T18:00:00Z'.",
                },
                "include_breakdowns": {
                    "type": "boolean",
                    "description": "For slo_status: include per-agent/per-task breakdowns on breached SLOs (default false).",
                },
                "limit": {
                    "type": "integer",
                    "description": "For failure_signatures (max 25), celery_task_history (max 100), execution_search (max 50): max results to return.",
                },
                "task_name": {
                    "type": "string",
                    "description": "For celery_task_history and tenant_boundary_violations: filter by task name (substring match, e.g. 'cleanup_stale', 'summarize_conversation'). Omit for all tasks.",
                },
                "failure_kind": {
                    "type": "string",
                    "enum": [
                        "missing_row_id", "row_not_found", "missing_acting_identity",
                        "acting_user_not_found", "unregistered_model", "predicate_rejected",
                    ],
                    "description": "For tenant_boundary_violations: filter by failure_kind discriminator (one of the 6 I-0303 Phase 2 failure kinds). Omit for all kinds.",
                },
                "execution_id": {
                    "type": "string",
                    "description": "For execution_detail: UUID of the AgentExecution to look up.",
                },
                "agent_name": {
                    "type": "string",
                    "description": "For execution_search: filter by agent name (substring match, e.g. 'WorkflowAgent').",
                },
                "status": {
                    "type": "string",
                    "description": "For celery_task_history: filter by status (SUCCESS/FAILURE). For execution_search: filter by status (in_progress/completed/failed).",
                },
                "agent_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "For timeout_config_read/proof_bundle: agent names to query (e.g. ['ResearchAgent', 'CustomerResearchAgent']). Omit for all.",
                },
                "initiative_id": {
                    "type": "string",
                    "description": "For proof_bundle: UUID of initiative to include in audit (optional).",
                },
                "config_updates": {
                    "type": "object",
                    "description": (
                        "For focus_mode_update: dict of config keys to change. "
                        "Valid keys: enabled (bool), mode ('gentle'/'strict'), "
                        "blocked_topics_autonomous (list of strings), "
                        "max_conversations_per_agent_per_hour (int), "
                        "max_total_conversations_per_hour (int), "
                        "require_north_star_for_autonomous (bool)."
                    ),
                },
                "bridge_tool_name": {
                    "type": "string",
                    "enum": ["consult_engine", "query_spider_data", "agent_consult"],
                    "description": (
                        "For recent_bridge_calls: filter to a single character-os "
                        "bridge tool. Omit for all three. The value is matched "
                        "against the ChatConversation.source suffix "
                        "(source == 'character-os-<bridge_tool_name>')."
                    ),
                },
                "workspace_id": {
                    "type": "string",
                    "description": (
                        "For recent_bridge_calls: filter to a single workspace UUID. "
                        "Omit for all workspaces visible to the requesting user. "
                        "Non-staff callers are always scoped to their own rows regardless."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── S2780 N22 v3: Zoom-Out Tool — governance ledger read surface ─────────
    # Factored out from ops_tool per S2779 V6 fold (scope creep) after S2780
    # V7 Fold B firing (first non-Rigby consumer). Dedicated home for the
    # PLAYBOOK-6.10.8 zoom-out concern ledger, keeping ops_tool focused on
    # runtime ops signal.
    {
        "type": "function",
        "name": "zoom_out_tool",
        "description": (
            "Read the Rigby SIGN zoom-out concern ledger — "
            "logs/zoom_out_classifications.jsonl. Advisory pattern evidence "
            "(NOT gates) per PLAYBOOK-6.10.8, constitutional at Playbook v0.7.0. "
            "Response embeds `advisory` header + `is_gate: false` + `semantics: "
            "\"advisory_pattern_evidence\"` to prevent advisory→gate drift. "
            "Use during joint SIGN loops to consult prior zoom-out folds before "
            "repeating them, or to answer 'what did we surface last time on this arc?'. "
            "Optional `include=aggregations` returns arc/rule-target counts for "
            "drill-down triage (S2791 UI parity); aggregations are advisory "
            "summaries, not gates or standalone proposals — cite underlying "
            "rows when making recommendations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list"],
                    "description": (
                        "list: read tail of logs/zoom_out_classifications.jsonl. "
                        "Filters: session (int, exact match), since_session/"
                        "until_session (int, inclusive window on originating "
                        "session; S2793 N22 v2), classification "
                        "(same_pr_actionable / same_pr_mitigatable / future_trigger), "
                        "arc (substring), limit (default 20, max 100). Response "
                        "includes `total_rows` + `counts_by_classification` "
                        "aggregates over the FULL ledger, plus filtered `items` "
                        "tail-window. Fail-soft: returns empty list with diagnostic "
                        "note when the log file is missing. Pass `include=aggregations` "
                        "to add a `aggregations` block with `top_arcs_by_count`, "
                        "`future_trigger_rule_targets` (PLAYBOOK-x.y[.z] regex hits "
                        "over future_trigger rows only), and `sessions_covered`."
                    ),
                },
                "session": {
                    "type": "integer",
                    "description": "Filter by originating session number (exact match, e.g. 2778). Omit for all sessions.",
                },
                "since_session": {
                    "type": "integer",
                    "description": (
                        "Inclusive lower bound on originating session number "
                        "(e.g. 2777). Combine with until_session for a "
                        "session-int window (e.g. since_session=2780, "
                        "until_session=2792 returns rows from S2780-S2792). "
                        "ADVISORY POSTURE: window narrows `items[]` only — the "
                        "`aggregations` block (when include=aggregations) still "
                        "computes over ALL rows to preserve longitudinal-signal "
                        "semantics. See test_zoom_out_time_window_2793 contract "
                        "6 for the locked invariant. Zero or negative treated as "
                        "'no filter' (autofill guard)."
                    ),
                },
                "until_session": {
                    "type": "integer",
                    "description": (
                        "Inclusive upper bound on originating session number "
                        "(e.g. 2792). Same advisory posture as since_session — "
                        "narrows items[] only; aggregations stay global. Zero "
                        "or negative treated as 'no filter'."
                    ),
                },
                "classification": {
                    "type": "string",
                    "enum": [
                        "same_pr_actionable",
                        "same_pr_mitigatable",
                        "future_trigger",
                    ],
                    "description": "Filter by fold classification enum (one of the 3 PLAYBOOK-6.10.8 categories). Omit for all classifications.",
                },
                "arc": {
                    "type": "string",
                    "description": "Filter by arc slug (substring match, e.g. 'ops_urlconf' matches 'ops_urlconf_lambda_cleanup'). Omit for all arcs.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 20, max 100).",
                },
                "include": {
                    "type": "string",
                    "description": (
                        "Comma-separated opt-in expansions. Currently supports "
                        "'aggregations' — adds an `aggregations` block with "
                        "`top_arcs_by_count` (top 20 arcs by row count), "
                        "`future_trigger_rule_targets` (PLAYBOOK-x.y[.z] regex "
                        "hits parsed from concern_text of future_trigger rows "
                        "only, aggregated across the FULL ledger not the "
                        "filtered tail), and `sessions_covered` (sorted list of "
                        "distinct integer session numbers). ADVISORY POSTURE: "
                        "the aggregations block embeds `is_gate:false` + "
                        "`semantics:advisory_pattern_evidence`; rule_target counts "
                        "are pattern evidence, NOT rule-codification proposals. "
                        "Any downstream workflow acting on rule_target counts "
                        "must also retrieve + quote the underlying future_trigger "
                        "rows via `classification=future_trigger` — Chris D-verdict "
                        "remains the explicit gate for any codification or "
                        "policy-change decision. Omit for pure filter-tail response."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1080: Agent Control Tool ─────────────────────────────────────
    {
        "type": "function",
        "name": "agent_control_tool",
        "description": (
            "Manage blocked/enabled agents. Use 'list' to see which agents are blocked. "
            "Use 'block' to disable an agent (with reason and optional TTL). "
            "Use 'unblock' to re-enable. Use 'audit_log' for recent changes. "
            "This is the single source of truth — changes apply to all dispatch paths."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "block", "unblock", "audit_log"],
                    "description": (
                        "list: show all agent control entries and currently blocked agents. "
                        "block: disable an agent (requires agent_name, optional reason/ttl_hours). "
                        "unblock: re-enable a blocked agent (requires agent_name). "
                        "audit_log: recent control changes."
                    ),
                },
                "agent_name": {
                    "type": "string",
                    "description": "Agent name (e.g. 'AudioAgent', 'CodeGeneratorAgent'). Required for block/unblock.",
                },
                "reason": {
                    "type": "string",
                    "description": "Why blocking/unblocking (stored for audit trail).",
                },
                "ttl_hours": {
                    "type": "integer",
                    "description": "Auto-unblock after N hours. Omit for permanent block.",
                },
                "blocked_by": {
                    "type": "string",
                    "description": "Who is blocking (default 'rigby'). E.g. 'rigby', 'chris', 'system'.",
                },
                "limit": {
                    "type": "integer",
                    "description": "For audit_log: max entries to return (default 20, max 50).",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1086: Active Priority Tool (initiative 2dcb79d7) ──────────────
    {
        "type": "function",
        "name": "active_priority_tool",
        "description": (
            "Manage Rigby's active priorities for priority-aware routing. "
            "Each active priority represents a current focus (e.g. 'Platform "
            "hardening', 'Newsletter Issue 2 ship'); beat tasks and autonomous "
            "dispatches will check alignment before running (PR 3). Use 'list' "
            "to see current priorities. Use 'set' to create a new priority "
            "with tags/whitelist/TTL. Use 'update' to edit an existing one. "
            "Use 'archive' to soft-delete (kept for audit). Use 'test_match' "
            "to preview whether a given agent would match (stubbed until PR 2). "
            "Use 'history' for the full audit list including archived/expired. "
            "TTL bounds enforced here: min 10min (anti-flap), max 7 days "
            "(anti-zombie), default 24h."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "set", "update", "archive", "test_match", "history"],
                    "description": (
                        "list: show currently-active priorities (auto-expires TTL). "
                        "set: create a new priority (requires name; optional tags, "
                        "agent_whitelist, agent_blacklist, description, priority_rank, "
                        "ttl_hours, enable_keyword_match, owner). "
                        "update: edit an existing priority (requires priority_id; "
                        "accepts any of the set fields). "
                        "archive: soft-delete a priority (requires priority_id). "
                        "test_match: preview match decision for (agent_name, task) — "
                        "stubbed until PR 2 delivers PriorityRouter. "
                        "history: full list including archived/expired (optional limit)."
                    ),
                },
                "priority_id": {
                    "type": "string",
                    "description": "UUID of the priority row. Required for update/archive.",
                },
                "name": {
                    "type": "string",
                    "description": "Short human label (<=120 chars). Required for set.",
                },
                "description": {
                    "type": "string",
                    "description": "Free-form intent. What is this priority trying to accomplish?",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "List of tag strings matched against derived agent tags. "
                        "Primary automatic matching mechanism. Example: "
                        "['platform','ops','routing']."
                    ),
                },
                "agent_whitelist": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Agent names that ALWAYS match (highest precedence).",
                },
                "agent_blacklist": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Agent names that NEVER match this priority.",
                },
                "enable_keyword_match": {
                    "type": "boolean",
                    "description": (
                        "Opt-in substring keyword match. Off by default — "
                        "keyword matching creates false positives, only enable "
                        "when the tag list is explicitly narrow."
                    ),
                },
                "priority_rank": {
                    "type": "integer",
                    "description": "Lower = higher priority. Default 100.",
                },
                "owner": {
                    "type": "string",
                    "description": "Who owns this priority ('rigby', 'chris', 'system'). Default 'rigby'.",
                },
                "ttl_hours": {
                    "type": "number",
                    "description": (
                        "Hours until auto-expire. Default 24. Clamped to "
                        "[10/60, 7*24] per design contract. Accepts floats "
                        "(e.g. 0.5 for 30min)."
                    ),
                },
                "agent_name": {
                    "type": "string",
                    "description": "For test_match: the agent to preview.",
                },
                "task": {
                    "type": "string",
                    "description": "For test_match: the task description to preview.",
                },
                "limit": {
                    "type": "integer",
                    "description": "For history: max entries to return (default 30, max 100).",
                },
                "enabled": {
                    "type": "boolean",
                    "description": (
                        "Per-mission pause toggle. When false, mission is paused "
                        "(agents only matching this mission will be skipped). "
                        "Used in set/update actions."
                    ),
                },
                "max_daily_executions": {
                    "type": "integer",
                    "description": (
                        "Daily execution budget for this mission. When set, "
                        "the governor will skip dispatches once the cap is reached. "
                        "NULL/omit for unlimited. Used in set/update actions."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1088: Governor Tool ───────────────────────────────────────────
    {
        "type": "function",
        "name": "governor_tool",
        "description": (
            "Beat Task Governor — controls which autonomous agent dispatches "
            "are allowed to run based on mission alignment and circuit breaker "
            "state. Use 'status' to see governor state, active missions, and "
            "tripped circuit breakers. Use 'test' to check if a specific agent "
            "would be dispatched. Use 'reset_breaker' to manually clear a "
            "tripped circuit breaker. Use 'coverage' to see all agents and "
            "their alignment status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "test", "reset_breaker", "coverage"],
                    "description": (
                        "status: governor state, missions, tripped breakers. "
                        "test: check if agent_name would be dispatched (requires agent_name). "
                        "reset_breaker: clear a tripped circuit breaker (requires agent_name). "
                        "coverage: all agents and their alignment status."
                    ),
                },
                "agent_name": {
                    "type": "string",
                    "description": "For test/reset_breaker: the agent name to check or reset.",
                },
                "trigger_source": {
                    "type": "string",
                    "description": "For test: simulate trigger source (default 'schedule').",
                },
                "task": {
                    "type": "string",
                    "description": "For test: optional task description for keyword matching.",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1080: Ops Autopilot ──────────────────────────────────────────
    {
        "type": "function",
        "name": "autopilot_tool",
        "description": (
            "Monitor and configure the Ops Autopilot — automated incident response "
            "with governance guardrails. Use 'status' for current config and last cycle. "
            "Use 'history' for recent autopilot actions. Use 'run' to trigger an "
            "immediate evaluation cycle. Use 'config' to view/update thresholds. "
            "Use 'dry_run_report' for a human-readable report of what autopilot would do."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "history", "run", "config", "dry_run_report", "drift_scan", "tuning_report", "budget_report", "roi_report", "scheduler_report", "portfolio_report", "backfill_impacts", "attribution_debt_report", "experiment_report", "experiment_create", "experiment_start", "decision_ledger_report", "timeout_ladder_report", "deliberation_pipeline_report", "backfill_failure_reasons", "backlog_report", "goal_report", "goal_set_weights", "attribution_report", "policy_conflict_report", "latest_overrides_snapshot", "release_report", "release_freeze", "release_unfreeze", "revenue_pipeline_report", "prospecting_queue", "lead_source_report", "outreach_inbox", "outreach_approve", "outreach_reject", "outreach_metrics_report", "outreach_generate", "close_pack_generate", "close_pack_inbox", "close_pack_approve", "close_pack_metrics_report", "engagement_inbox", "engagement_classify", "engagement_draft_reply", "engagement_approve_reply", "engagement_disqualify", "engagement_metrics_report", "meeting_create", "meeting_inbox", "meeting_brief", "meeting_recap", "meeting_metrics_report", "governance_status", "governance_set_mode", "governance_kill_switch", "governance_deactivate_switch", "governance_throttle_report", "governance_audit", "revenue_full_pipeline", "revenue_funnel", "revenue_forecast", "knowledge_health", "knowledge_citation_report", "knowledge_source_report", "knowledge_staleness_report", "close_pack_followup_queue", "close_pack_risk_report", "close_pack_velocity", "engagement_sla_queue", "engagement_meeting_suggestions", "engagement_conversion_report", "growth_candidates", "growth_schedule", "growth_channel_report", "growth_funnel", "capacity_forecast", "capacity_bottleneck_report", "capacity_throttle_plan", "capacity_budget_envelope", "security_permission_drift", "security_abuse_queue", "security_containment_plan", "security_secrets_scan", "compliance_pii_scan", "compliance_retention_report", "compliance_access_audit", "compliance_report", "integrity_quality_report", "integrity_null_spike_scan", "integrity_duplicate_report", "integrity_reliability_scores", "value_events_report", "value_outcome_rates", "value_usage_gaps", "value_realization_summary"],
                    "description": (
                        "status: current config, last cycle timestamp, and pending actions. "
                        "history: recent autopilot actions (blocks, attention items, dry runs). "
                        "Pass include_evidence=true to also surface each row's evidence + result "
                        "JSON (trigger, actor_user_id, reason, etc.). "
                        "Pair with selected_fields=[\"evidence.<key>\", \"result.<key>\"] to "
                        "trim the returned JSON to only specific top-level keys. "
                        "run: trigger an immediate autopilot evaluation cycle. "
                        "config: view current thresholds (timeout spike, block TTL, etc.). "
                        "dry_run_report: evaluate all policies in dry-run mode and return a "
                        "human-readable report with SLO breaches, timeout spikes, stale blocks, "
                        "and proposed actions. "
                        "drift_scan: scan for contract/schema drift — mismatches between PA tool schemas, "
                        "handler registrations, agent registry, and Celery beat schedule. "
                        "tuning_report: show current self-tuning state — active config overrides, "
                        "pending recommendations, recent changes, and per-policy effectiveness metrics. "
                        "budget_report: show current LLM spend vs budget caps, top spenders by agent "
                        "and model, enforcement mode (normal/downgrade/freeze), and utilization percentages. "
                        "roi_report: show ROI attribution per agent — spend vs outcomes (completed executions, "
                        "published content), active throttles, and cooldown recommendations. "
                        "scheduler_report: show budget-aware scheduling state — which tasks get deferred "
                        "or downscoped under budget pressure, recent decisions, active knob overrides. "
                        "portfolio_report: show IQROI per desk — impact vs cost across sports/content/research/career "
                        "desks, portfolio allocations (budget headroom multipliers), and collected impact events. "
                        "backfill_impacts: scan historical wager settlements, deliverable events, and confirmed revenue "
                        "to create ImpactEvent records for past activity (default 14 days, max 90). Idempotent. "
                        "attribution_debt_report: show how much LLM spend can't be attributed to a desk — "
                        "unattributed cost amounts, top offending agents, desk breakdown, and whether portfolio "
                        "reallocation is blocked due to high debt. "
                        "experiment_report: show active and recent A/B experiments on policy parameters — "
                        "which policies are being tested, what metrics are tracked, recent promote/rollback decisions. "
                        "experiment_create: create a new experiment (requires policy_name and treatment_params). "
                        "experiment_start: activate a draft experiment by experiment_id — applies treatment params. "
                        "decision_ledger_report: query the decision ledger — every policy evaluation is recorded with "
                        "structured inputs, outputs, decision type, timing, and experiment context. Filter by policy_name, "
                        "decision_type (no_op/action_taken/blocked/skipped), and days. Shows cycle count and decision type stats. "
                        "timeout_ladder_report: show agents currently on the timeout remediation ladder — levels (L0-L3), "
                        "escalation history, timeout overrides, batch reductions, and blocks. Graduated: L1=timeout increase, "
                        "L2=batch reduction, L3=temporary block. Auto-de-escalates after recovery. "
                        "deliberation_pipeline_report: show deliberation pipeline health — failure rate, breakdown by reason code, "
                        "remediation ladder state (L1=panel reduced, L2=model fallback, L3=single-reviewer bypass), active overrides. "
                        "backfill_failure_reasons: re-classify UNKNOWN failure codes using expanded patterns. "
                        "backlog_report: show deliverable backlog health — ready/draft counts, p95 age, conversion rate, "
                        "governor level (L1=throttle, L2=governance batch, L3=auto-archive), protected vs archivable items. "
                        "goal_report: show goal-aware allocation state — objective weights, current metrics (sports profit, "
                        "revenue, engagement, quality, freshness), desk utility scores, and active goal multipliers. "
                        "goal_set_weights: update goal objective weights (provide goal_weights dict, e.g. "
                        "{'sports_profit': 0.3, 'confirmed_revenue': 0.3, 'content_engagement': 0.2, 'quality': 0.1, 'freshness': 0.1}). "
                        "Weights are auto-normalized to sum=1.0. "
                        "attribution_report: show multi-touch attribution state — credited impact by desk (last-touch vs assist), "
                        "attributed vs unattributed events, upstream credit flows. "
                        "policy_conflict_report: detect conflicts when multiple policies write the same knob, "
                        "flap detection (3+ changes in 24h), hold-time violations. Optional filters: knob, policy. "
                        "latest_overrides_snapshot: return a PolicyArbitrator snapshot — cycle_id, cycle_ts, "
                        "row_created_at, and the knobs dict (key → value/owner/priority). Without `at`, returns the "
                        "latest snapshot. With `at` (ISO 8601 datetime), returns the snapshot active at that time "
                        "via filter(cycle_ts__lte=at).order_by('-cycle_ts').first(). Time-travel queries are "
                        "bounded by the 90-day retention window. Session 1163 B-style storage: append-only "
                        "per-cycle rows in FinalAppliedOverrides — see Disclosure L §14.7. "
                        "release_report: current deploy status — governor level, deploy rate, error rate, freeze state, "
                        "last deploy SHA and timestamp, recovery progress. "
                        "release_freeze: manually freeze all deploys (safety override). "
                        "release_unfreeze: manually unfreeze deploys. "
                        "revenue_pipeline_report: opportunity pipeline health — active/stale/critical counts, "
                        "high-value opportunities, follow-up suggestions by priority. "
                        "prospecting_queue: outbound lead engine — top scored leads from spider data, "
                        "ready for human outreach review. Shows lead scores, sources, and age. "
                        "lead_source_report: which spider sources produce leads — 30-day source breakdown, "
                        "7-day vs 30-day trend, data type distribution. "
                        "outreach_inbox: pending outreach drafts for approval — lead details, scores, draft text, "
                        "remaining daily approval capacity. "
                        "outreach_approve: approve a draft for sending (requires draft_id, optional edited_text). "
                        "Schedules next follow-up in the sequence automatically. "
                        "outreach_reject: reject a draft (requires draft_id, optional reason). Prevents re-queue. "
                        "outreach_metrics_report: outreach conversion funnel — by status/channel/offer, reply rate. "
                        "outreach_generate: generate touch=1 OutreachDrafts from contactable Opportunity rows "
                        "(scope=all|mine, optional limit, optional offers list). Respects DAILY_GENERATE_CAP=5. "
                        "Round-robins across ai_automation/content_engine/consulting offers. "
                        "close_pack_generate: generate a close pack (proposal, contract, invoice) for an opportunity "
                        "(requires opportunity_id, offer_key, price; optional timeline_days). "
                        "close_pack_inbox: pending close packs for approval — offer details, price, pipeline value. "
                        "close_pack_approve: approve a close pack (requires pack_id). Schedules follow-up automatically. "
                        "close_pack_metrics_report: deal metrics — win rate, revenue, avg deal size, funnel by status/offer. "
                        "engagement_inbox: inbound engagement events (replies, meetings, form fills) — "
                        "filterable by status (unread, needs_reply, classified, all). Shows intent, prospect info. "
                        "engagement_classify: classify an engagement event's intent (requires event_id, intent: "
                        "positive/neutral/objection/meeting/unsubscribe). Auto-suppresses unsubscribes. "
                        "engagement_draft_reply: set a draft reply for an engagement (requires event_id, reply_text). "
                        "engagement_approve_reply: approve a draft reply (requires event_id, optional edited_text). "
                        "engagement_disqualify: disqualify an engagement (requires event_id, optional reason). "
                        "engagement_metrics_report: engagement funnel — by status/intent/channel, conversion rate. "
                        "meeting_create: schedule a meeting (requires scheduled_at ISO datetime; optional: "
                        "opportunity_id, title, channel, duration_minutes, meeting_link, prospect_name, prospect_company). "
                        "meeting_inbox: upcoming meetings, needs_brief, or past_needs_followup (filter_type param). "
                        "meeting_brief: generate a pre-call brief for a meeting (requires meeting_id). "
                        "meeting_recap: add post-meeting notes and recap draft (requires meeting_id; optional: notes, outcome, next_steps). "
                        "meeting_metrics_report: meeting pipeline metrics — show rate, upcoming count, by status/outcome. "
                        "governance_status: full governance status — global mode, per-agent/desk overrides, active kill switches, "
                        "budget flags, throttle counts. "
                        "governance_set_mode: set autonomy mode (normal/throttle/freeze/safe_mode) globally or per-agent/desk. "
                        "Optional ttl_hours for auto-expiry. Syncs budget flags automatically. "
                        "governance_kill_switch: activate emergency kill switch (scheduler/queue/agent_family/publishing/outbound/deploys). "
                        "Requires target; optional target_detail, ttl_hours (default 4h, max 72h). "
                        "governance_deactivate_switch: deactivate a kill switch by switch_id. "
                        "governance_throttle_report: diagnostic 'why are we throttled?' report — spend vs cap, budget flags, "
                        "active ROI throttles, diagnosis with plain-English explanations. "
                        "governance_audit: recent governance changes — state changes and kill switch activations. "
                        "revenue_full_pipeline: unified pipeline view — outreach, engagement, meetings, close packs, "
                        "opportunities by status + items needing attention. "
                        "revenue_funnel: conversion funnel from leads to won deals — rates at each stage over N days. "
                        "revenue_forecast: weighted revenue forecast from current pipeline items, "
                        "won revenue total, and pipeline value. "
                        "knowledge_health: overall knowledge system health — citation violations, spider data freshness, "
                        "research status, active spiders, and health issues. "
                        "knowledge_citation_report: citation violation trends over N days — by type, by agent, "
                        "block rate, resolution rate, daily trend. Optional days param (default 7). "
                        "knowledge_source_report: spider source coverage — top spiders by volume, data type distribution, "
                        "unique domains, research source rates. "
                        "knowledge_staleness_report: stale data detection — which data types are overdue for refresh, "
                        "dormant spiders, freshness thresholds, and actionable recommendations. "
                        "close_pack_followup_queue: close packs needing follow-up — due/overdue packs with "
                        "draft follow-up messages, overdue hours, upcoming follow-ups in next 48h. "
                        "close_pack_risk_report: risk assessment of active close packs — pricing below minimums, "
                        "short timelines, missing opportunity links, severity breakdown. "
                        "close_pack_velocity: pipeline velocity — time-to-close for won deals, velocity by offer type, "
                        "current pipeline age, deal count and revenue. "
                        "engagement_sla_queue: SLA-aware reply queue — events ranked by urgency "
                        "(ok/warning/critical/breach), time since receipt, intent and status. "
                        "engagement_meeting_suggestions: events with positive/meeting intent that should "
                        "be converted to meetings — shows which need booking vs already booked. "
                        "engagement_conversion_report: engagement→meeting→deal conversion funnel over N days — "
                        "reply rate, meeting conversion, deal conversion, avg response time. Optional days param. "
                        "growth_candidates: distribution-ready content ranked by freshness + quality — "
                        "published deliverables and blogs that passed quality gate, with rank scores. "
                        "growth_schedule: distribution schedule — recent exports by format, today's rate "
                        "usage, timeline of distributed content. Optional days param (default 7). "
                        "growth_channel_report: channel-level distribution stats — formats used, engagement "
                        "events, content type breakdown, quality averages, unused format gaps. "
                        "growth_funnel: distribution funnel — candidates→exported→engaged→actions taken, "
                        "with conversion rates at each stage. Optional days param (default 30). "
                        "capacity_forecast: forecast task volume, latency p50/p95, memory usage, and "
                        "spend projections for the next N hours. Optional hours param (default 24). "
                        "capacity_bottleneck_report: identify top bottlenecks — slowest tasks, highest "
                        "failure rates, memory hogs. Optional hours param (default 24). "
                        "capacity_throttle_plan: current capacity state (tasks/hour, failure rate, p95, "
                        "governance mode) with throttle recommendations (reduce concurrency, pause, defer). "
                        "capacity_budget_envelope: per-queue task volume, spend tracking, budget utilization, "
                        "and projected monthly cost. Optional days param (default 7). "
                        "security_permission_drift: check for permission anomalies — audit log spikes, "
                        "config churn, governance changes, stale kill switches. Optional hours param. "
                        "security_abuse_queue: flag suspicious patterns — high-activity users/IPs, "
                        "failed operation spikes. Optional hours and limit params. "
                        "security_containment_plan: risk assessment with containment recommendations — "
                        "expired switch cleanup, rate limiting, investigation flags. dry_run param. "
                        "security_secrets_scan: scan recent deliverables and blogs for exposed API keys, "
                        "tokens, and secrets. Optional days param (default 7). "
                        "compliance_pii_scan: scan recent deliverables and blogs for PII patterns "
                        "(SSN, credit cards, emails, phone numbers). Optional days and limit params. "
                        "compliance_retention_report: check data retention compliance across key tables "
                        "(AgentExecution, AuditLog, SpiderData, ConversationMemory) against TTL thresholds. "
                        "compliance_access_audit: audit agent data access patterns for anomalies — "
                        "high-frequency agents, bulk data operations. Optional hours param. "
                        "compliance_report: comprehensive compliance summary combining PII, retention, "
                        "and access audits with overall risk level assessment. "
                        "integrity_quality_report: overall data quality report across spider feeds — "
                        "null rates, volume drops, per-source stats. Optional hours param. "
                        "integrity_null_spike_scan: scan spider feeds for null/empty data spikes "
                        "by field (raw_data, processed_data, embedding_text). Optional hours param. "
                        "integrity_duplicate_report: detect duplicate URL explosions in spider feeds "
                        "with per-spider breakdown. Optional hours param. "
                        "integrity_reliability_scores: per-source reliability scores (A/B/C/F grades) "
                        "based on completeness and freshness over 7 days. "
                        "value_events_report: report on value-generating events — agent completions, "
                        "deliverables created, revenue generated, engagement events. Optional days param. "
                        "value_outcome_rates: compute outcome/conversion rates — agent success rate, "
                        "deliverable quality rate, outreach-to-meeting conversion. Optional days param. "
                        "value_usage_gaps: detect areas with high usage but low outcomes — high failure "
                        "agents, low quality content. Optional days param. "
                        "value_realization_summary: comprehensive value realization summary combining "
                        "events, outcome rates, and usage gaps with overall health assessment."
                    ),
                },
                "dry_run": {
                    "type": "boolean",
                    "description": (
                        "For 'run' action: evaluate policies but don't actually block/unblock (default false). "
                        "For 'security_containment_plan': preview the containment plan without applying it "
                        "(DEFAULT true; writes require BOTH dry_run=false AND confirm=true per Session 1228 "
                        "PR-A belt-and-suspenders against LLM autofill)."
                    ),
                },
                "confirm": {
                    "type": "boolean",
                    "description": (
                        "For 'security_containment_plan': explicit second-factor confirmation required "
                        "(along with dry_run=false) to actually execute the containment plan. Defaults "
                        "to false. Session 1228 PR-A — defends against GPT-5.2 autofilling dry_run=False "
                        "and silently flipping a preview into a live containment action."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "For 'history': max entries to return (default 20, max 100).",
                },
                "include_evidence": {
                    "type": "boolean",
                    "description": (
                        "For 'history' action: when true, each returned row includes the "
                        "raw `evidence` and `result` JSON fields from AutopilotAction (e.g., "
                        "`evidence.trigger`, `evidence.actor_user_id`, `result.reason`, "
                        "`result.cap`). Defaults to false (preserves prior shape). Use when "
                        "you need to know WHY an action fired or WHO triggered it without "
                        "dropping to Django shell. Pair with `selected_fields` to trim the "
                        "returned JSON to only specific top-level keys."
                    ),
                },
                "selected_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "For 'history' action: project the returned `evidence` and `result` "
                        "JSON to only the specified top-level keys. Use dot-notation with "
                        "`evidence.<key>` or `result.<key>` prefixes (e.g., "
                        "[\"evidence.actor_user_id\", \"evidence.trigger\", \"result.reason\", "
                        "\"result.cap\"]). Returns the top-level key's value verbatim — "
                        "nested dicts/lists are returned whole (v1 does not deep-project). "
                        "Missing keys silently omitted; invalid prefixes silently ignored. "
                        "Max 20 paths (extras truncated). Ignored unless `include_evidence=true`. "
                        "When set, BOTH `evidence` and `result` are projected to their "
                        "respective selections (an empty selection for one prefix returns "
                        "`{}` for that field). Response echoes the server-applied list "
                        "(post-validation, post-cap). S2896 (Ledger Row C): response also "
                        "echoes `selected_fields_dropped` (paths per-item validation rejected) "
                        "and `selected_fields_received_count` (list length as the handler saw "
                        "it pre-truncation — NOT end-to-end proof of what the caller sent). "
                        "Narrow use: if `selected_fields=[]` with "
                        "`selected_fields_received_count>0` and `selected_fields_dropped=[]`, "
                        "the list was wiped between the caller and the handler — retry with a "
                        "shorter list to isolate."
                    ),
                },
                "days": {
                    "type": "integer",
                    "description": "For 'backfill_impacts': how many days back to scan (default 14, max 90). For 'decision_ledger_report': how many days to query (default 1).",
                },
                "decision_type": {
                    "type": "string",
                    "description": "For 'decision_ledger_report': filter by decision type (no_op, action_taken, blocked, skipped).",
                },
                "policy_name": {
                    "type": "string",
                    "description": "For 'experiment_create': which policy to test (portfolio_allocator, roi_throttle, budget_controller). For 'decision_ledger_report': filter by policy name.",
                },
                "treatment_params": {
                    "type": "object",
                    "description": "For 'experiment_create': dict of param name → new value (e.g., {\"ALLOCATION_CEILING\": 2.0}).",
                },
                "success_metric": {
                    "type": "string",
                    "description": "For 'experiment_create': metric to evaluate (avg_desk_iqroi, attribution_debt_pct, total_impact_usd, publish_pass_rate, error_rate). Default: avg_desk_iqroi.",
                },
                "experiment_id": {
                    "type": "string",
                    "description": "For 'experiment_start': UUID of the experiment to activate.",
                },
                "description": {
                    "type": "string",
                    "description": "For 'experiment_create': human-readable description of the experiment.",
                },
                "goal_weights": {
                    "type": "object",
                    "description": "For 'goal_set_weights': dict of objective weights (e.g., {'sports_profit': 0.3, 'confirmed_revenue': 0.3, 'content_engagement': 0.2, 'quality': 0.1, 'freshness': 0.1}). Auto-normalized to sum=1.0.",
                },
                "knob": {
                    "type": "string",
                    "description": "For 'policy_conflict_report': filter conflicts by knob name (substring match).",
                },
                "policy_filter": {
                    "type": "string",
                    "description": "For 'policy_conflict_report': filter conflicts by policy name.",
                },
                "at": {
                    "type": "string",
                    "description": "For 'latest_overrides_snapshot': ISO 8601 datetime to time-travel to (e.g., '2026-05-26T20:30:00+00:00'). Returns the snapshot active at that time. Bounded by the 90-day retention window. If omitted, returns the most recent snapshot.",
                },
                "draft_id": {
                    "type": "string",
                    "description": "For 'outreach_approve' / 'outreach_reject': UUID of the draft to act on.",
                },
                "edited_text": {
                    "type": "string",
                    "description": "For 'outreach_approve': optionally edited message text to use instead of the original draft.",
                },
                "reason": {
                    "type": "string",
                    "description": "For 'outreach_reject': reason for rejecting the draft.",
                },
                "opportunity_id": {
                    "type": "string",
                    "description": "For 'close_pack_generate': UUID of the Opportunity to create a close pack for.",
                },
                "offer_key": {
                    "type": "string",
                    "description": "For 'close_pack_generate': offer template — ai_automation, content_engine, analytics_dashboard, consulting.",
                },
                "price": {
                    "type": "number",
                    "description": "For 'close_pack_generate': quoted price in USD.",
                },
                "timeline_days": {
                    "type": "integer",
                    "description": "For 'close_pack_generate': delivery timeline in days (default 14).",
                },
                "pack_id": {
                    "type": "string",
                    "description": "For 'close_pack_approve': UUID of the close pack to approve.",
                },
                "event_id": {
                    "type": "string",
                    "description": "For engagement actions: UUID of the engagement event.",
                },
                "intent": {
                    "type": "string",
                    "description": "For 'engagement_classify': intent classification — positive, neutral, objection, meeting, unsubscribe.",
                },
                "reply_text": {
                    "type": "string",
                    "description": "For 'engagement_draft_reply': draft reply text for approval.",
                },
                "status_filter": {
                    "type": "string",
                    "description": "For 'engagement_inbox': filter by status — unread (default), needs_reply, classified, actioned, all.",
                },
                "meeting_id": {
                    "type": "string",
                    "description": "For 'meeting_brief' / 'meeting_recap': UUID of the meeting.",
                },
                "scheduled_at": {
                    "type": "string",
                    "description": "For 'meeting_create': ISO datetime for the meeting (e.g. '2026-03-10T14:00:00Z').",
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "For 'meeting_create': meeting duration in minutes (default 30).",
                },
                "meeting_link": {
                    "type": "string",
                    "description": "For 'meeting_create': video call link (Zoom, Meet, etc.).",
                },
                "prospect_name": {
                    "type": "string",
                    "description": "For 'meeting_create': prospect's name.",
                },
                "prospect_company": {
                    "type": "string",
                    "description": "For 'meeting_create': prospect's company.",
                },
                "notes": {
                    "type": "string",
                    "description": "For 'meeting_recap': meeting notes / outcome summary.",
                },
                "next_steps": {
                    "type": "string",
                    "description": "For 'meeting_recap': agreed next steps from the meeting.",
                },
                "filter_type": {
                    "type": "string",
                    "description": "For 'meeting_inbox': filter — upcoming (default), needs_brief, past_needs_followup, all.",
                },
                "mode": {
                    "type": "string",
                    "description": "For 'governance_set_mode': autonomy mode — normal, throttle, freeze, safe_mode.",
                },
                "scope": {
                    "type": "string",
                    "description": "For 'governance_set_mode': scope — global (default), agent, desk.",
                },
                "scope_target": {
                    "type": "string",
                    "description": "For 'governance_set_mode': agent name or desk name (required for agent/desk scope).",
                },
                "ttl_hours": {
                    "type": "number",
                    "description": "For 'governance_set_mode' / 'governance_kill_switch': auto-expire after N hours (max 72).",
                },
                "target": {
                    "type": "string",
                    "description": "For 'governance_kill_switch': what to kill — scheduler, queue, agent_family, publishing, outbound, deploys.",
                },
                "target_detail": {
                    "type": "string",
                    "description": "For 'governance_kill_switch': queue name, agent tag, etc.",
                },
                "switch_id": {
                    "type": "string",
                    "description": "For 'governance_deactivate_switch': UUID of the kill switch to deactivate.",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 2847 A1 W1 Phase 3 + Session 2848 A1 W1.5 downgrade tier ────
    # ── Session 2849 A1 W2 #2a: defaults + backfill for per-workspace caps ──
    {
        "type": "function",
        "name": "workspace_budget_tool",
        "description": (
            "Manage per-workspace LLM spend caps, downgrade state, and freeze state "
            "(A1 W1 Phase 3 + W1.5 + W2 #2a). Complements autopilot_tool.budget_report "
            "(global spend) and llm_enforcer's per-workspace freeze + downgrade hooks: "
            "caps are stored in SystemConfiguration under 'workspace_daily_cap:<uuid>' "
            "and enforced by BudgetController against the last-24h LLMCallLog spend for "
            "that workspace (sliding window, NOT calendar day — spend at 09:15 today is "
            "measured against 09:15 yesterday). Two enforcement tiers: at 70% of cap the "
            "workspace is DOWNGRADED (routed to BUDGET_DOWNGRADE_MODEL, currently "
            "gpt-5-mini) with hysteresis auto-clear at 60%; at 100% of cap the workspace "
            "is FROZEN (non-critical LLM calls blocked). Freeze wins over downgrade. "
            "S2849 W2 #2a adds a global default cap (workspace_default_daily_cap in "
            "SystemConfiguration) that surfaces via get_status/list_caps as an effective "
            "cap when the workspace has no explicit row; because autopilot enforcement "
            "iterates only workspaces with explicit caps, 'backfill_defaults' writes the "
            "default to unconfigured workspaces so enforcement actually fires. "
            "NOTE: workspace caps apply only to workspace-attributed LLMCallLog rows "
            "(currently the PA path); the NULL-bucket (agents, spiders, embeddings, "
            "background tasks) is governed by GLOBAL budget controls, not per-workspace. "
            "Actions: 'set_cap' writes a per-workspace cap; 'get_status' returns cap + "
            "spend + freeze + downgrade + cap_source for one workspace; 'clear_freeze' "
            "removes an active freeze flag; 'clear_downgrade' removes an active downgrade "
            "flag; 'list_caps' shows configured caps (or all workspaces with effective "
            "caps when include_defaults=true); 'clear_cap' removes an explicit cap; "
            "'get_default_cap' returns the current global default; 'set_default_cap' "
            "writes/updates the global default (staff only); 'backfill_defaults' writes "
            "the default to all/selected workspaces missing an explicit cap. "
            "MUTATIONS (set_cap, clear_cap, clear_freeze, clear_downgrade, "
            "set_default_cap, backfill_defaults) require caller to own the workspace OR "
            "be staff (default-cap + backfill require staff), and are logged as "
            "AutopilotAction rows with policy='workspace_budget_tool' for symmetric "
            "visibility with the automatic enforce_workspace_freeze + "
            "enforce_workspace_downgrade audit trail. Use this tool when asked to "
            "set/change/clear a workspace budget cap, unfreeze or un-downgrade a "
            "workspace, check a workspace's spend vs cap, inventory configured caps, or "
            "roll out a default cap across workspaces."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "set_cap",
                        "get_status",
                        "clear_freeze",
                        "clear_downgrade",
                        "list_caps",
                        "clear_cap",
                        "get_default_cap",
                        "set_default_cap",
                        "backfill_defaults",
                        "enforcement_report",
                        "simulate_enforcement",
                    ],
                    "description": (
                        "set_cap: write/update a per-workspace daily cap ($ USD). "
                        "Requires workspace_id + daily_cap_usd > 0. Idempotent — same "
                        "value returns changed=false. S2850: immediately evaluates "
                        "enforcement against last-24h spend — freezes at 100% of cap, "
                        "downgrades at 70% (with 60% hysteresis clear), and returns "
                        "'enforcement_fired' with any freeze/downgrade action dicts "
                        "written this call (null when threshold not crossed). Response "
                        "still warns when the target workspace is currently frozen and "
                        "the new cap now exceeds 24h spend (operator should call "
                        "clear_freeze to resume). "
                        "get_status: return {cap, effective_cap, cap_source, "
                        "default_cap, spend, is_frozen, is_downgraded, "
                        "enforcement_tier} for one workspace. cap is null when no "
                        "explicit row exists; cap_source is 'explicit'|'default'|"
                        "'unset'; effective_cap is what an operator surface should "
                        "display. spend is a sliding 24h + 1h window over LLMCallLog. "
                        "clear_freeze: delete the workspace_freeze_active:<uuid> flag. "
                        "Idempotent — no-op if the workspace isn't currently frozen. "
                        "S2858 PR#1 — response embeds a status_context block "
                        "{daily_total, effective_cap, cap_source, spend_pct_of_cap, "
                        "re_flag_likely, re_flag_reason, refire_threshold, "
                        "refire_threshold_pct_of_cap, enforcement_note} so operators "
                        "don't have to re-call get_status to know whether the freeze "
                        "will immediately re-fire. re_flag_likely is computed against "
                        "the EXPLICIT cap only (enforcer ignores default fallback); "
                        "when cap_source != 'explicit', re_flag_likely is False + "
                        "reason explains that enforcement won't re-fire until an "
                        "explicit cap is set. "
                        "clear_downgrade: delete the workspace_downgrade_active:<uuid> "
                        "flag. Idempotent. Autopilot may re-flag on next cycle if "
                        "spend still above 70% (hysteresis clears at 60%). "
                        "S2858 PR#1 — response embeds the same status_context block "
                        "as clear_freeze (see above), with refire_threshold set to "
                        "70% of explicit cap (the downgrade soft-limit trigger). "
                        "list_caps: return every workspace with a configured explicit "
                        "cap by default. When include_defaults=true, returns every "
                        "ProjectWorkspace with its effective cap + cap_source so "
                        "'default'/'unset' workspaces are visible alongside explicit "
                        "ones. Enriched with current 24h spend + freeze + downgrade. "
                        "S2852 — auto-scoped to caller's owned workspaces for "
                        "non-staff; staff sees all workspaces; unauthenticated "
                        "callers get an empty list + scope_note. Response includes "
                        "top-level scope_note describing which policy applied. "
                        "clear_cap: delete the workspace_daily_cap:<uuid> row. Does "
                        "NOT clear an existing freeze or downgrade. "
                        "get_default_cap: return {default_cap} for the global default "
                        "(null if unset). Read-only; no auth. "
                        "set_default_cap: write/update the global default cap. "
                        "Requires daily_cap_usd > 0. STAFF ONLY. Idempotent. Does NOT "
                        "backfill existing workspaces — call backfill_defaults to "
                        "apply. "
                        "backfill_defaults: write the default cap to workspaces "
                        "without an explicit cap. STAFF ONLY. Defaults to dry_run=true "
                        "(returns plan only); pass dry_run=false to actually write. "
                        "force=false (default) skips workspaces that already have an "
                        "explicit cap; force=true overwrites them. Optional "
                        "include_workspace_ids / exclude_workspace_ids allowlist. "
                        "Fail-soft per-workspace — one bad row doesn't abort the "
                        "batch. Returns per-workspace details + counts. "
                        "enforcement_report: fleet auditability over time — for "
                        "each in-scope workspace, returns per-workspace cap + "
                        "effective_cap + cap_source + freeze/downgrade state + "
                        "enforcement_events_count + last_enforcement_at over a "
                        "sliding window. Enforcement events counted = "
                        "AutopilotAction rows with action_type in "
                        "{workspace_budget_freeze, workspace_freeze_cleared, "
                        "workspace_downgrade_set, workspace_downgrade_cleared} "
                        "and created_at within `window`. Optional include_spend "
                        "adds per-workspace attributed spend + calls in the "
                        "same window. Optional include_null_bucket adds the "
                        "null-workspace bucket (system tasks, embeddings, "
                        "background — spend that workspace caps don't govern). "
                        "Optional include_downgrade_savings adds per-workspace "
                        "and top-level downgrade-model usage + estimated "
                        "savings vs pre-downgrade gpt-5.2 rates (diagnostic "
                        "estimate — over-reports because natively-mini calls "
                        "cannot yet be distinguished from enforcer-forced). "
                        "READ-ONLY. Auto-scoped to caller's owned workspaces "
                        "for non-staff; staff sees all workspaces. Optional "
                        "workspace_id narrows to a single workspace (must be "
                        "in scope). NOTE on attribution: workspace_id is "
                        "extracted from AutopilotAction.evidence JSON (no FK "
                        "column) — best-effort. Report is diagnostic; the "
                        "point-of-action trust surface is `set_cap`'s inline "
                        "enforcement_fired payload (S2850 #3.0a). "
                        "S2857 include_simulated (default false) filters out "
                        "rows written by simulate_enforcement so operator/"
                        "autopilot counts stay clean. "
                        "simulate_enforcement: fire the freeze + downgrade "
                        "enforcer hot-path against a SYNTHETIC daily-spend "
                        "value without needing to make real LLM calls from "
                        "a non-PA agent. Motivation: Rigby's calling agent "
                        "is always 'PersonalAssistant' which bypasses "
                        "freeze (core/llm_enforcer.py:271 _critical_agents), "
                        "so operators/customer demos had to drop to Django "
                        "shell to see enforcement fire. Requires "
                        "workspace_id + simulated_daily_spend_usd (float "
                        "≥ 0). dry_run defaults to true — returns the "
                        "freeze + downgrade decisions (would_freeze / "
                        "would_set_downgrade / would_clear_downgrade / "
                        "no_op variants) + computed thresholds (cap, "
                        "downgrade_set_threshold, downgrade_clear_threshold, "
                        "currently_frozen, currently_downgraded) without "
                        "writing state. Pass dry_run=false to actually "
                        "invoke enforce_workspace_freeze + "
                        "enforce_workspace_downgrade — real SystemConfig "
                        "flags are written and llm_enforcer WILL block or "
                        "downgrade real workspace calls until "
                        "clear_freeze / clear_downgrade is called. "
                        "AutopilotAction rows carry "
                        "evidence.simulated=True + trigger="
                        "'simulate_enforcement' + actor_user_id — "
                        "excluded from enforcement_report by default. "
                        "Requires caller to own the workspace OR be staff "
                        "(both dry_run and mutation paths — dry_run "
                        "reveals cap + thresholds so is still a sensitive "
                        "read). Errors when the workspace has no explicit "
                        "cap set (enforcer only runs against explicit-"
                        "cap workspaces)."
                    ),
                },
                "workspace_id": {
                    "type": "string",
                    "description": (
                        "UUID of the ProjectWorkspace being managed. Required for "
                        "set_cap, get_status, clear_freeze, clear_downgrade, "
                        "clear_cap, simulate_enforcement. Optional narrowing "
                        "filter for enforcement_report (must be in caller's "
                        "scope). Ignored for list_caps, get_default_cap, "
                        "set_default_cap, backfill_defaults."
                    ),
                },
                "window": {
                    "type": "string",
                    "enum": ["24h", "7d", "30d"],
                    "description": (
                        "For enforcement_report: sliding time window for "
                        "counting enforcement events and (if include_spend) "
                        "aggregating attributed spend. Defaults to '24h'."
                    ),
                },
                "include_spend": {
                    "type": "boolean",
                    "description": (
                        "For enforcement_report: when true, per-workspace rows "
                        "include attributed_spend_usd + calls for the window "
                        "(from LLMCallLog joined by workspace FK). Defaults to "
                        "false (enforcement-forward — the report's primary "
                        "answer is whether/when enforcement fired, not how "
                        "much was spent). Attributed spend is a subset — the "
                        "null-workspace bucket is reported separately when "
                        "include_null_bucket=true."
                    ),
                },
                "include_null_bucket": {
                    "type": "boolean",
                    "description": (
                        "For enforcement_report: when true (default), the "
                        "response's null_bucket field reports spend_usd + "
                        "calls for LLMCallLog rows with workspace=NULL in the "
                        "window. This is the substrate that per-workspace "
                        "caps do NOT govern (governed by global budget "
                        "controls instead). Pass false to omit."
                    ),
                },
                "include_downgrade_savings": {
                    "type": "boolean",
                    "description": (
                        "For enforcement_report: when true, per-workspace "
                        "rows gain downgrade_model_calls_count, "
                        "downgrade_model_actual_cost_usd, "
                        "downgrade_model_would_have_cost_usd, and "
                        "downgrade_model_estimated_savings_usd — actual "
                        "cost of in-window calls that ran on the downgrade "
                        "model (currently gpt-5-mini) versus what those "
                        "calls would have cost at pre-downgrade gpt-5.2 "
                        "uncached rates. Response also gains "
                        "downgrade_model_totals aggregate + explanatory "
                        "downgrade_savings_note. S2856 (PR #3328): filter "
                        "is now LLMCallLog.was_downgraded=True, so counts "
                        "only enforcer-forced downgrades; natively-mini "
                        "agents (PersonalAssistantAgent, orchestration "
                        "coordinators) are excluded. Rows created before "
                        "the S2856 deploy default to was_downgraded=False "
                        "and are excluded, so windows straddling that "
                        "boundary UNDER-report until enough post-deploy "
                        "traffic accrues. Diagnostic estimate; LLMCallLog."
                        "cost remains the authoritative per-call cost "
                        "ledger. Defaults to false."
                    ),
                },
                "daily_cap_usd": {
                    "type": "number",
                    "description": (
                        "For set_cap and set_default_cap: the new cap in USD. Must be "
                        "> 0. Applied against the sliding last-24h spend from "
                        "LLMCallLog. For backfill_defaults, if omitted, reads the "
                        "currently-configured global default; if passed, uses that "
                        "value for the run without changing the stored default."
                    ),
                },
                "include_defaults": {
                    "type": "boolean",
                    "description": (
                        "For list_caps: when true, include every ProjectWorkspace "
                        "with its effective cap (explicit or default) and cap_source. "
                        "Defaults to false (explicit-only, preserving legacy shape)."
                    ),
                },
                "dry_run": {
                    "type": "boolean",
                    "description": (
                        "For backfill_defaults: when true (default), plan only — no "
                        "writes. Response includes the per-workspace 'would_write' "
                        "list. Pass false to actually write. "
                        "For simulate_enforcement: when true (default), returns the "
                        "freeze + downgrade decisions without writing state. Pass "
                        "false to actually invoke the enforcer methods — real "
                        "SystemConfiguration flags are written and llm_enforcer will "
                        "block/downgrade real workspace calls until clear_freeze / "
                        "clear_downgrade is called."
                    ),
                },
                "simulated_daily_spend_usd": {
                    "type": "number",
                    "description": (
                        "For simulate_enforcement: the synthetic daily spend value "
                        "(USD, ≥ 0) to pass through the enforcer decision logic. "
                        "Required. When dry_run=false the enforcer receives a "
                        "synthetic spend dict {daily_total: <this>, daily_calls: 0, "
                        "hourly_total: 0.0, hourly_calls: 0} — real 24h spend is "
                        "not queried, and any freeze/downgrade flags written "
                        "reflect this simulated value."
                    ),
                },
                "include_simulated": {
                    "type": "boolean",
                    "description": (
                        "For enforcement_report: when true, include rows where "
                        "evidence.simulated=True (written by simulate_enforcement). "
                        "Defaults to false so demo/verification traffic doesn't "
                        "pollute operator_events_count / auto_events_count. The "
                        "response's `note` field records which mode was applied."
                    ),
                },
                "force": {
                    "type": "boolean",
                    "description": (
                        "For backfill_defaults: when true, overwrite workspaces that "
                        "already have an explicit cap. Defaults to false (skip "
                        "existing)."
                    ),
                },
                "include_workspace_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "For backfill_defaults: optional allowlist of workspace UUIDs. "
                        "When omitted, considers all workspaces."
                    ),
                },
                "exclude_workspace_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "For backfill_defaults: optional skiplist of workspace UUIDs "
                        "(applied after include_workspace_ids filter)."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1079: Governance Gateway ──────────────────────────────────────
    {
        "type": "function",
        "name": "governance_tool",
        "description": (
            "Unified governance inbox — attention items, decisions, and triage. "
            "Replaces boardroom_tool and human_decisions_tool. "
            "Use 'inbox' for a combined overview of pending attention items and draft decisions. "
            "Use attention_* actions to list/approve/ignore items. "
            "Use decision_* actions to list/create/decide/promote/reject decisions. "
            "Use triage_batch to get items for batch processing."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "inbox", "stats",
                        "attention_list", "attention_detail", "attention_approve", "attention_ignore", "attention_lookup",
                        "decision_list", "decision_promote", "decision_reject",
                        "decisions_list", "decisions_stats", "decision_create", "decision_decide",
                        "triage_batch",
                        "failure_signatures", "remediation_tasks",
                    ],
                    "description": (
                        "inbox: combined overview with counts + top items. "
                        "stats: bundled governance snapshot (inbox + decisions + failure_signatures + remediation tasks counts) "
                        "— use this for general 'governance status?' questions instead of chaining multiple calls. "
                        "attention_list: list pending attention items. "
                        "attention_detail: get full detail for an item by id. "
                        "attention_approve: approve an attention item by id. "
                        "attention_ignore: ignore an attention item by id. "
                        "attention_lookup: find an item by title or id. "
                        "decision_list: list draft decision summaries. "
                        "decision_promote: promote a draft decision to canonical. "
                        "decision_reject: reject a draft decision. "
                        "decisions_list: list pending human decisions. "
                        "decisions_stats: decision statistics. "
                        "decision_create: create a new decision request. "
                        "decision_decide: make a decision (approve/reject/defer/watch). "
                        "triage_batch: get items for batch triage. "
                        "failure_signatures: FailureSignature patterns (read-only). "
                        "remediation_tasks: AuditRemediationTask status (read-only)."
                    ),
                },
                "id": {"type": "string", "description": "UUID of attention item or decision"},
                "title": {"type": "string", "description": "Title for new decision or lookup query"},
                "title_query": {"type": "string", "description": "Title search for attention_lookup"},
                "summary": {"type": "string", "description": "Summary for decision_create"},
                "decision": {"type": "string", "description": "Decision value for decision_decide (approve/reject/defer/watch)"},
                "feedback": {"type": "string", "description": "Feedback for approve/ignore/reject actions"},
                "reason": {"type": "string", "description": "Reason for decision_reject"},
                "urgency": {"type": "string", "enum": ["critical", "high", "medium", "low"], "description": "Urgency filter or value"},
                "item_type": {"type": "string", "description": "Filter by item type"},
                "decision_type": {"type": "string", "description": "Filter by decision type"},
                "triage_type": {"type": "string", "enum": ["attention", "decisions"], "description": "Type for triage_batch"},
                "batch_size": {"type": "integer", "description": "Number of items in triage batch (default 5)"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1079: Intelligence Gateway ────────────────────────────────────
    {
        "type": "function",
        "name": "intelligence_tool",
        "description": (
            "Unified intelligence desk — stocks, sports betting, legislation, search, and KB. "
            "Replaces stock_intelligence_tool, sports_betting_tool, legislation_tool, "
            "rag_query_tool, spider_data_tool, and web_search for intelligence queries. "
            "Use 'overview' for a combined dashboard across all desks. "
            "Use 'briefs' with desk param for desk-specific briefings. "
            "Use 'search' with source=kb/spider/web for unified search."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "overview", "briefs", "search",
                        "stocks_alerts", "stocks_predictions", "stocks_sec_filings",
                        "sports_predictions", "sports_arbs", "sports_wagers", "sports_record_wager",
                        "sports_sharp_signals",
                        "legislation_search", "legislation_summary",
                        "congress_members", "legislation_tracked",
                        "kb_ingest",
                        "stock_briefs", "ml_predictions", "signal_clusters",
                    ],
                    "description": (
                        "overview: combined dashboard from all 3 desks. "
                        "briefs: desk-specific briefings (use desk param). "
                        "search: unified search (use source param: kb/spider/web). "
                        "stocks_*: stock alerts, predictions, SEC filings. "
                        "stock_briefs: latest stock brief summaries. "
                        "ml_predictions: ML model predictions with accuracy. "
                        "signal_clusters: signal aggregation patterns. Supports query (keyword match on name+keywords), pattern_type, min_confidence, source_spider (spider name filter on source_breakdown JSONField, e.g. 'hackernews' / 'huggingface' / 'devto'), window_hours. "
                        "sports_*: predictions, arbs, wagers, record_wager. "
                        "sports_sharp_signals: sharp money/line movement signals. "
                        "legislation_*: search bills, get summaries. "
                        "congress_members: list/search congress members. "
                        "legislation_tracked: tracked bills with embedding status. "
                        "kb_ingest: ingest a URL into the knowledge base."
                    ),
                },
                "desk": {"type": "string", "enum": ["stocks", "sports", "legislation", "all"], "description": "Desk for briefs action (default: all)"},
                "source": {"type": "string", "enum": ["kb", "spider", "web"], "description": "Search source for search action (default: kb)"},
                "source_spider": {"description": "Spider name filter for signal_clusters (matches source_breakdown JSONField key, e.g. 'hackernews', 'huggingface', 'devto', 'producthunt', 'techcrunch_startups'). Distinct from `source` which is enum-restricted for the search action. S2869 Ledger #4: accepts a single string (has_key match) OR a list of strings (has_any_keys union match) — use the list form to fetch clusters across multiple spiders in one call instead of looping.", "anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]},
                "query": {"type": "string", "description": "Search query for search/legislation_search/legislation_summary/signal_clusters (signal_clusters: keyword match against cluster name + keywords)"},
                "pattern_type": {"anyOf": [{"type": "string", "enum": ["demand_spike", "trend_emergence", "sentiment_shift", "opportunity_window", "knowledge_gap", "competitive_signal", "market_movement", "skill_demand", "content_gap", "user_need"]}, {"type": "null"}], "description": "OPTIONAL filter for signal_clusters. Omit entirely or pass null when the operator did NOT explicitly request filtering by a specific pattern type. Do not default-fill (e.g. 'demand_spike') — that over-filters to zero. S2870 Ledger #20: anyOf-null shape added to give GPT-5.2 a proper 'no filter' path."},
                "min_confidence": {"type": "number", "description": "OPTIONAL filter for signal_clusters (confidence >= this value, 0.0-1.0). Omit entirely when the operator did NOT explicitly request a confidence threshold. Do not default-fill (e.g. 0.6) — that over-filters to zero. Pass 0 or omit for no filter."},
                "window_hours": {"type": "integer", "description": "OPTIONAL time window for signal_clusters (detected_at within last N hours). Omit entirely when the operator did NOT explicitly request a time window. Do not default-fill (e.g. 168) — that over-filters to zero. Pass 0 or omit for no filter."},
                "ticker": {"type": "string", "description": "Stock ticker symbol for stocks_* actions"},
                "sport": {"type": "string", "description": "Sport filter for sports_* actions"},
                "bill_number": {"type": "string", "description": "Bill number for legislation_summary"},
                "url": {"type": "string", "description": "URL for kb_ingest"},
                "stake": {"type": "number", "description": "Stake amount for sports_record_wager"},
                "odds": {"type": "number", "description": "Odds for sports_record_wager"},
                "description": {"type": "string", "description": "Description for sports_record_wager"},
                "wager_type": {"type": "string", "description": "Type for sports_record_wager"},
                "state": {"type": "string", "description": "2-letter state code for congress_members (e.g. CO, CA, TX)"},
                "chamber": {"type": "string", "enum": ["house", "senate"], "description": "Chamber filter for congress_members"},
                "party": {"type": "string", "description": "Party filter for congress_members (e.g. Republican, Democrat)"},
                "hours": {"type": "integer", "description": "Hours window for sports_sharp_signals (default 48)"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1079: Content Gateway ─────────────────────────────────────────
    {
        "type": "function",
        "name": "content_tool",
        "description": (
            "Unified content gateway — blogs, deliverables, publishing, and editorial. "
            "Replaces content_review_tool, generate_blog_tool, and deliverables_tool. "
            "Use content_stats for a full content pipeline overview. "
            "Use content_list/content_search/content_detail to browse blogs and deliverables. "
            "Use content_approve/content_reject/content_complete to publish, archive, or mark-completed content. "
            "Use generate_blog to create a new blog via the deliberation pipeline. "
            "Use deliverable_* actions for the deliverables library (documents, scripts, plans)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "content_stats", "content_list", "content_detail",
                        "content_search", "content_recent",
                        "content_approve", "content_reject", "content_complete",
                        "generate_blog", "generate_newsletter",
                        "bulk_archive", "bulk_archive_published", "run_cleanup",
                        "deliverable_list", "deliverable_detail",
                        "deliverable_search", "deliverable_save",
                        "deliverable_create", "deliverable_update",
                        "deliverable_append", "deliverable_stats",
                        "deliverable_export_pdf",
                        "podcasts", "series", "content_studio",
                        "initiative_doc",
                    ],
                    "description": (
                        "content_stats: pipeline overview (blogs + deliverables counts). "
                        "content_list: list content by status (default: ready). Use status param to filter. "
                        "content_detail: full details of a deliverable/blog by id. "
                        "content_search: search by title keyword across blogs + deliverables. "
                        "content_recent: recently created content (any status). "
                        "content_approve: publish a ready deliverable. "
                        "content_reject: archive a deliverable with feedback. "
                        "content_complete: mark a deliverable completed with feedback — terminal state for one-shot analyses (ops snapshots, daily diagnostics) you want to keep as historical reference, NOT for content meant to be published externally. "
                        "generate_blog: create a new blog post via deliberation pipeline. "
                        "generate_newsletter: generate an Operator Edge newsletter from recent signal clusters (supports dry_run=true for preview). "
                        "bulk_archive: archive multiple deliverables by filter (dry_run preview by default). "
                        "bulk_archive_published: admin-only — archive published deliverables by category (requires categories + created_before + confirm). "
                        "run_cleanup: trigger cleanup_stale_content Celery task (async, returns task_id). "
                        "deliverable_list: browse deliverables library (supports status/type/category/date filters). "
                        "deliverable_detail: content of a deliverable (default 8K chars; pass full=true for uncapped, or content_offset+content_limit to paginate). "
                        "deliverable_search: search deliverables by title. "
                        "deliverable_save: bookmark a deliverable. "
                        "deliverable_create: create a new deliverable (supports category, tags, workspace_id, data_sensitivity, is_pinned, agent_name). "
                        "deliverable_update: update an existing deliverable by id (supports content, title, category, tags, workspace_id, data_sensitivity). "
                        "deliverable_append: append text to an existing deliverable's content (pass content or text with the text to add — never overwrites existing content). "
                        "deliverable_stats: aggregate counts by type/category/agent. "
                        "deliverable_export_pdf: generate a downloadable PDF from a deliverable (returns CDN URL). "
                        "podcasts: list completed podcast episodes. "
                        "series: AI Series workflow history. "
                        "content_studio: autonomous content studio execution stats. "
                        "initiative_doc: fetch initiative stage documents by document_id, stage_id, or initiative name."
                    ),
                },
                "id": {"type": "string", "description": "UUID of deliverable or blog"},
                "query": {"type": "string", "description": "Title search term for search actions"},
                "type": {"type": "string", "description": "Content type filter (e.g. 'edited_content', 'blog', 'document')"},
                "category": {"type": "string", "description": "Category filter (e.g. 'Finance', 'Research', 'Content Editing')"},
                "agent": {"type": "string", "description": "Filter by agent_name (e.g. 'EditorAgent', 'ContentWriterAgent')"},
                "status": {"type": "string", "description": "Filter by status: draft, ready, published, archived. Default varies by action."},
                "statuses": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive: list of statuses to target (default: ['ready', 'draft', 'completed']). Cannot include published/archived."},
                "agent_names": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive: archive only items by these agent names (e.g., ['StockAnalystAgent', 'MarketMovementMonitorAgent'])"},
                "title_prefixes": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive: archive items whose title starts with any of these prefixes (e.g., ['Stock Analysis:', 'Market Movement:'])"},
                "protected_categories": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive: exclude these categories from archiving (e.g., ['Patent Disclosures', 'Platform Diagnostics'])"},
                "categories": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive_published: required list of categories to target (e.g. ['initiative_completion', 'PA Created'])."},
                "confirm": {"type": "boolean", "description": "For bulk_archive / bulk_archive_published: must be true when dry_run=false to actually execute. Session 1228 PR-A extended the existing bulk_archive_published gate to bulk_archive (belt-and-suspenders against LLM autofill of dry_run=False)."},
                "types": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive_published: optional deliverable_type filter. 'blog' is blocked."},
                "created_before": {"type": "string", "description": "ISO-8601 datetime. Only items created before this date (e.g. '2026-02-28T00:00:00Z')."},
                "created_after": {"type": "string", "description": "ISO-8601 datetime. Only items created after this date."},
                "dry_run": {"type": "boolean", "description": "For bulk_archive / bulk_archive_published / generate_newsletter / run_cleanup: preview without executing (DEFAULT: true). Set dry_run=false AND confirm=true to execute (Session 1228 PR-A belt-and-suspenders). S2945 Ledger #38 batch 4: run_cleanup dry_run response returns `no_writes:true` + `would_action:'dispatch_celery'` + `would_archive_count` + top_by_type/category preview via shared `_gather_cleanup_preview` helper (single source of truth with actual archive filter). Content_tool now 100% mutation-aligned. Builds on S2944 (bulk_archive + generate_newsletter) + S2943 (bulk_archive_published) + S2942 blog_tool/feedback_tool."},
                "cutoff_days": {"type": "integer", "description": "For run_cleanup: archive items older than N days (default: 7)"},
                "cap": {"type": "integer", "description": "For run_cleanup/bulk_archive: max items per run (default: 500, max: 2000)"},
                "protected_types": {"type": "array", "items": {"type": "string"}, "description": "For run_cleanup: deliverable_types to skip"},
                "topic": {"type": "string", "description": "Blog topic for generate_blog action"},
                "tone": {"type": "string", "description": "Tone for generate_blog action (default: enthusiastic)"},
                "title": {"type": "string", "description": "Title for deliverable_create"},
                "content": {"type": "string", "description": "Content for deliverable_create"},
                "document_id": {"type": "string", "description": "UUID of a document (SelfBlog) for initiative_doc action"},
                "stage_id": {"type": "string", "description": "UUID of an InitiativeStage for initiative_doc action"},
                "initiative": {"type": "string", "description": "Initiative name to list all stage documents (for initiative_doc action)"},
                "feedback": {"type": "string", "description": "Feedback when rejecting content"},
                "days": {"type": "integer", "description": "Lookback days for content_recent (default 30)"},
                "limit": {"type": "integer", "description": "Max items (default 10, for bulk_archive: max items to archive, default 500)"},
                "offset": {"type": "integer", "description": "Pagination offset (default 0)"},
                "full": {"type": "boolean", "description": "For deliverable_detail: return full content without 8K char cap (default false)"},
                "content_offset": {"type": "integer", "description": "For deliverable_detail: start reading content from this char position"},
                "content_limit": {"type": "integer", "description": "For deliverable_detail: max chars to return (default 8000)"},
                "workspace_id": {"type": "string", "description": "For deliverable_create/update: workspace UUID to link deliverable to"},
                "agent_name": {"type": "string", "description": "For deliverable_create: agent name (default Rigby)"},
                "data_sensitivity": {"type": "string", "description": "For deliverable_create/update: public, internal, confidential, restricted"},
                "is_pinned": {"type": "boolean", "description": "For deliverable_create: pin to prevent auto-cleanup"},
                "prepend": {"type": "string", "description": "For deliverable_update: text to prepend to existing content"},
                "append": {"type": "string", "description": "For deliverable_update: text to append to existing content"},
            },
            "required": ["action"],
        },
    },
    # ── Session 1077: Focused deliverable_tool (split from content_tool) ────────
    {
        "type": "function",
        "name": "deliverable_tool",
        "description": (
            "Manage the deliverables library — create, read, update, search, save, export, and archive deliverables. "
            "Use this tool (NOT content_tool) for ALL deliverable operations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "detail", "create", "update", "append", "search", "save", "unsave", "stats", "duplicates", "set_status", "normalize", "export_pdf", "bulk_archive", "delete", "link_initiative", "unlink_initiative", "clear_diagnostic"],
                    "description": (
                        "list: browse deliverables (supports status/type/category/date/workspace filters). "
                        "detail: get full content of a deliverable (pass full=true for uncapped content). "
                        "create: create a new deliverable (title + content required). "
                        "update: update an existing deliverable by id. NOTE: cannot set status='completed' via update — completed is a lifecycle terminal state (returns a typed error pointing at content_tool.content_complete or deliverable_tool.set_status status='completed'; see F-D-7 Session 2728). "
                        "append: append text to a deliverable (never overwrites). "
                        "search: search deliverables by title keyword. "
                        "save/unsave: bookmark or unbookmark a deliverable. "
                        "stats: aggregate counts by type/category/agent. "
                        "duplicates: surface duplicate groups (audit-style) — returns rows with count/first_created_at/last_created_at/last_7d_count/agent_name_distribution/status_distribution. Use group_by, min_count, window_days, exclude_archived, limit to tune. "
                        "set_status: surgical, audited status flip — ONLY supports completed↔ready (other transitions go through update). Pass id + status + reason. Reason is REQUIRED on completed→ready. Records actor + trace_id + reason in a DeliverableEvent. "
                        "normalize: dry-run alias-map sweep — preview rows whose `agent_name` (v1) would be canonicalized via the canonical alias map (e.g., 'rigby'→'Rigby', 'ClaudeCode'→'claude-code'). Defaults to dry_run=true; writes require BOTH dry_run=false AND confirm=true. Workspace-scoped by default; show_all=true sweeps globally. "
                        "export_pdf: generate a downloadable PDF. "
                        "bulk_archive: archive multiple deliverables by filter (dry_run=true by default). "
                        "delete: PERMANENTLY delete a single deliverable by id. IRREVERSIBLE — cascades to DeliverableExport / DeliverableEvent (audit trail is also erased) / ContentPacketItem (may break content packets). Prefer set_status='archived' or bulk_archive for reversible cleanup. Defaults to dry_run=true (safe preview showing cascade counts). Writes require BOTH dry_run=false AND confirm=true. Rejects status='published' rows unless allow_published=true AND a non-empty reason is provided. Pre-delete WARNING log line records deliverable_id + user_id + trace_id + reason + cascade counts (DeliverableEvent cannot be relied on for audit because it cascades). "
                        "link_initiative: link a deliverable to an initiative (pass deliverable_id + initiative_id). "
                        "unlink_initiative: remove initiative link from a deliverable (pass deliverable_id). "
                        "clear_diagnostic: manually clear a `missing_initiative_id` diagnostic (S2868 Ledger #7/#17/#18). Sets diagnostic_status='cleared' (a sticky sentinel — distinct from NULL) so subsequent updates on this row do NOT re-fire the same diagnostic while the underlying alignment condition remains. Preserves prior diagnostic_code + marked_at as audit residue in diagnostic_payload alongside {manually_cleared_at, manual_clear_reason, user_id, trace_id}. Requires id + non-empty reason. Rejects if the row is not currently `diagnostic`. Only suppresses missing_initiative_id re-marks; workspace_mismatch (a stronger integrity signal) still fires on transition."
                    ),
                },
                "id": {"type": "string", "description": "UUID of the deliverable (also used as deliverable_id for link/unlink)"},
                "initiative_id": {"type": "string", "description": "UUID of initiative — for link_initiative action OR as a list filter (return only deliverables attached to this initiative). Combine with `agent` to ask 'which of agent X's deliverables belong to initiative Y'."},
                "has_initiative": {"type": ["string", "boolean"], "description": "For list: OMIT unless explicitly filtering by initiative-attachment. Pass true to return only deliverables WITH an initiative. To filter for deliverables WITHOUT an initiative, pass the STRING 'false' (not the boolean — boolean false is treated as autofill and ignored to avoid silent hidden filtering, see Session 1227 PR)."},
                "title": {"type": "string", "description": "Title for create/update"},
                "content": {"type": "string", "description": "Content for create/update/append"},
                "query": {"type": "string", "description": "Search term for search action"},
                "category": {"type": "string", "description": "Category filter or value for create/update"},
                "type": {"type": "string", "description": "Deliverable type filter (document, analysis, etc.)"},
                "status": {"type": "string", "description": "Status filter: ready, completed, draft, published"},
                "agent": {"type": "string", "description": "Filter by agent_name"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for create/update"},
                "workspace_id": {"type": "string", "description": "Workspace UUID to scope or link"},
                "orphans": {"type": "boolean", "description": "For list: OMIT unless explicitly filtering for orphans. Pass true to return only deliverables with no workspace assignment (workspace_id IS NULL); the response also surfaces is_orphan on every row. Boolean false is treated as no-filter (autofill safety, Session 1227)."},
                "show_all": {"type": "boolean", "description": "For list/search: when true, bypass the optional filters that LLMs tend to autofill (has_initiative, orphans, saved, status). Useful when the caller wants the broadest possible result set scoped only to workspace/agent/category/type. Response always echoes `applied_filters` so the caller can see exactly which filters fired."},
                "full_by_agent": {"type": "boolean", "description": "For stats: when true, return the full agent_name long tail instead of the default top-10. Response sets by_agent_truncated=false. Use for cross-agent audits (Session 1226 audit §4.6 (C))."},
                "group_by": {"type": "array", "items": {"type": "string"}, "description": "For duplicates: which fields to group by. Allowed: ['title'] (default), ['title','agent_name'], or ['title','category']. v1 keeps the set narrow to preserve index usage."},
                "min_count": {"type": "integer", "description": "For duplicates: minimum group size to surface (default 2). Use 3+ to focus on the heaviest dupes."},
                "window_days": {"type": "integer", "description": "For duplicates: rolling window in days for last_Nd_count (default 7)."},
                "exclude_archived": {"type": "boolean", "description": "For duplicates: when true, drop archived rows before grouping. Default false (include archived — useful for hygiene audits). Truthy-only check; Python bool false is treated as autofill and ignored."},
                "reason": {"type": "string", "description": "For set_status: free-text explanation of why the status was flipped. REQUIRED when flipping completed→ready (the unblock direction); optional on ready→completed. Trimmed; max 500 chars. Persisted under DeliverableEvent.metadata.ctx.reason. For clear_diagnostic (S2868): also REQUIRED — persisted under diagnostic_payload.manual_clear_reason as the durable justification for the operator's manual clear."},
                "field": {"type": "string", "description": "For normalize: which field to canonicalize. v1 supports 'agent_name' only."},
                "full": {"type": "boolean", "description": "For detail: return full content without 8K cap"},
                "content_offset": {"type": "integer", "description": "For detail: start reading from this char position"},
                "content_limit": {"type": "integer", "description": "For detail: max chars to return"},
                "data_sensitivity": {"type": "string", "description": "For create/update: public, internal, confidential, restricted"},
                "is_pinned": {"type": "boolean", "description": "For create: pin to prevent auto-cleanup"},
                "agent_name": {"type": "string", "description": "For create: agent name"},
                "return_detail": {"type": "boolean", "description": "For create: when true, run a follow-up `detail` fetch and embed the sanitized dict under a `detail` key in the response, plus `detail_included: bool`. Closes the verify-then-set_status round-trip for callers who need the full provenance/content_preview/initiative/workspace block immediately. Note: `status` is ALWAYS echoed at top level regardless of this flag — use return_detail only when you need the full sanitized detail block."},
                "dry_run": {"type": "boolean", "description": "For bulk_archive / cleanup / normalize: preview without executing (DEFAULT true). Writes require BOTH dry_run='false' AND confirm=true (Session 1227 PR4 normalize precedent, extended to bulk_archive/cleanup by Session 1228 PR-A). Belt-and-suspenders against LLM autofill — GPT-5.2 autofills declared optional booleans with False."},
                "confirm": {"type": "boolean", "description": "For bulk_archive / cleanup / normalize / delete: explicit second-factor confirmation required (along with dry_run=false) to actually apply writes. Defaults to false. Session 1228 PR-A extended the existing normalize gate to bulk_archive + cleanup; S2860 extended to single-row delete."},
                "allow_published": {"type": "boolean", "description": "For delete: escape hatch to allow deletion of a deliverable with status='published'. Defaults to false (published rows rejected). When true, a non-empty `reason` is also REQUIRED. Autofill-safe: Python False is treated as not-set."},
                "cap": {"type": "integer", "description": "For bulk_archive: max items per run"},
                "title_prefixes": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive: title prefix filter"},
                "agent_names": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive: agent name filter"},
                "protected_categories": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive: categories to exclude"},
                "limit": {"type": "integer", "description": "Max items to return (default 10)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
            "required": ["action"],
        },
    },
    # ── Session 1077: Focused blog_tool (split from content_tool) ────────────
    {
        "type": "function",
        "name": "blog_tool",
        "description": (
            "Manage the blog/content pipeline — stats, list, approve, reject, generate. "
            "Use this tool for blog operations. Use deliverable_tool for deliverables."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["stats", "list", "detail", "search", "recent", "approve", "reject", "generate"],
                    "description": (
                        "stats: pipeline overview (blogs + deliverables counts). "
                        "list: list blogs by status. "
                        "detail: full blog content by id. "
                        "search: search blogs by title. "
                        "recent: recently created content. "
                        "approve: publish a ready blog. "
                        "reject: archive a blog with feedback. "
                        "generate: create a new blog via deliberation pipeline."
                    ),
                },
                "id": {"type": "string", "description": "UUID of the blog"},
                "query": {"type": "string", "description": "Search term"},
                "status": {"type": "string", "description": "Status filter"},
                "type": {"type": "string", "description": "Content type filter (e.g. 'blog' routes through SelfBlog path)"},
                "topic": {"type": "string", "description": "Blog topic for generate action"},
                "tone": {"type": "string", "description": "Tone for generate (default: enthusiastic)"},
                "feedback": {"type": "string", "description": "Feedback when rejecting"},
                "days": {"type": "integer", "description": "Lookback days for recent (default 30)"},
                "limit": {"type": "integer", "description": "Max items"},
                "dry_run": {
                    "type": "boolean",
                    "description": (
                        "S2942 Ledger #38 MVP: For approve/reject/generate, preview the mutation without writing. "
                        "Returns a would_* envelope (dry_run=true, would_action=publish/archive/dispatch_celery, "
                        "current_status/would_change_to for approve/reject; would_task for generate). Zero DB writes "
                        "and zero Celery enqueues when true. Default false."
                    ),
                },
            },
            "required": ["action"],
        },
    },
    # ── Newsletter publishing adapter — POC 1 Autopilot Ops ─────────────
    {
        "type": "function",
        "name": "newsletter_tool",
        "description": (
            "Newsletter publishing pipeline — prepare issues for Substack/Beehiiv, "
            "generate outlines, validate against Template v1, track metrics. "
            "Use when the user asks about newsletter, Autopilot Ops, publishing an issue, "
            "newsletter metrics, or newsletter config."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["prepare", "outline", "validate", "metrics", "list_issues", "config", "sources"],
                    "description": (
                        "prepare: transform an issue deliverable into publish-ready markdown/HTML + checklist. "
                        "outline: generate a Template v1 outline for a new issue number. "
                        "validate: check a draft against Template v1 section completeness & length targets. "
                        "metrics: compute or update metrics (word count, links, opens, clicks) for an issue. "
                        "list_issues: list newsletter deliverables (outlines, drafts, published). "
                        "config: view or update newsletter config (provider, subscribe_url, sponsor_email). "
                        "sources: view the source pack (curated list of feeds/sites for each section)."
                    ),
                },
                "id": {"type": "string", "description": "UUID of the issue deliverable (for prepare/validate/metrics)"},
                "deliverable_id": {"type": "string", "description": "Alias for id"},
                "issue_number": {"type": "integer", "description": "Issue number (for outline action)"},
                "provider": {"type": "string", "enum": ["substack_manual", "beehiiv", "buttondown"], "description": "Publishing provider (default: substack_manual)"},
                "subscribe_url": {"type": "string", "description": "Publication subscribe URL"},
                "sponsor_email": {"type": "string", "description": "Sponsor inquiry email"},
                "publication_name": {"type": "string", "description": "Newsletter name (for config)"},
                "publication_slug": {"type": "string", "description": "Substack slug (for config)"},
                "workspace_id": {"type": "string", "description": "Workspace to scope deliverables"},
                "initiative_id": {"type": "string", "description": "Initiative to link deliverables"},
                "source_pack_id": {"type": "string", "description": "Source pack deliverable ID (for outline)"},
                "artifact_type": {"type": "string", "enum": ["outline", "draft", "publish_ready_markdown", "publish_ready_html", "publish_checklist"], "description": "Filter by artifact type (for list_issues)"},
                "send_date": {"type": "string", "description": "ISO date when issue was sent (for metrics)"},
                "opens": {"type": "integer", "description": "Manual open count (for metrics)"},
                "clicks": {"type": "integer", "description": "Manual click count (for metrics)"},
                "unsubscribes": {"type": "integer", "description": "Unsubscribe count (for metrics)"},
                "new_subscribers": {"type": "integer", "description": "New subscriber count (for metrics)"},
                "limit": {"type": "integer", "description": "Max items to return (default 20)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
            "required": ["action"],
        },
    },
    # ── rigby_shift_brief_tool (Session 1251 PR 12A) ─────────────────────
    {
        "type": "function",
        "name": "rigby_shift_brief_tool",
        "description": (
            "Rigby's operator shift brief — a one-minute pulse for Chris at "
            "the start of a session. Bundles ops_digest, cockpit "
            "worker_health + queue_lengths, session health, audit findings, "
            "and recent activity into one structured 6-section response: "
            "top priority, platform health, active risks, what changed, "
            "what NOT to work on, suggested next action. Read-only; no "
            "state mutation. Distinct from the heavier morning_brief content "
            "workflow — this is operational status, not narrative."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["generate"],
                    "description": "Always 'generate' for v0. Reserved for future actions.",
                },
                "conversation_id": {
                    "type": "string",
                    "description": (
                        "Optional pinned conversation_id for the session "
                        "health-check sub-section. Falls back to the current "
                        "PA conversation if omitted."
                    ),
                },
                "window": {
                    "type": "string",
                    "enum": ["10m", "1h", "6h", "24h"],
                    "description": "Lookback window for activity counts (default: 24h).",
                },
            },
            "required": ["action"],
        },
    },

    # ── ops_digest_tool ──────────────────────────────────────────────────
    {
        "type": "function",
        "name": "ops_digest_tool",
        "description": (
            "Generate or post an autonomous ops digest summarizing system health, "
            "autopilot status, blocked agents, and recent activity. "
            "Use 'generate' to build a digest, 'post' to write it into a conversation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["generate", "post"],
                    "description": (
                        "generate: build an ops digest and return it. "
                        "post: generate and write the digest into a conversation as a visible message."
                    ),
                },
                "conversation_id": {
                    "type": "string",
                    "description": "Target conversation ID for 'post' action (e.g. 'pa-9eee6fe61173')",
                },
                "window": {
                    "type": "string",
                    "enum": ["10m", "1h", "6h", "24h"],
                    "description": "Lookback window for activity counts (default: 1h)",
                },
            },
            "required": ["action"],
        },
    },

    # ── Codebase Introspection ───────────────────────────────────────────────
    {
        "type": "function",
        "name": "repo_tool",
        "description": (
            "Read-only codebase introspection: browse file tree, read file contents, "
            "search/grep across code, and check git status/log. "
            "Use this when you need to answer questions about what code exists, "
            "how features are implemented, file structure, or recent commits. "
            "Cannot modify files — read-only access only. "
            "S2887: pass repo_id to target a sibling repo (character-os, context-kit, "
            "fleet apps); omit to read this repo (u-d-b). Call action='list_repos' "
            "to discover which siblings are registered."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["tree", "read_file", "search", "git_info", "list_repos"],
                    "description": "tree: list directory contents. read_file: read file contents. search: grep/search code. git_info: branch, recent commits, status. list_repos: enumerate registered external_repos profiles + on-disk existence.",
                },
                "path": {"type": "string", "description": "Relative path from project root (e.g. 'core/agents/', 'mobile/src/screens/'). When repo_id is set, path is resolved against that sibling's root_path."},
                "depth": {"type": "integer", "description": "Directory depth for tree action (default 2, max 4)"},
                "query": {"type": "string", "description": "Search query/regex for search action"},
                "start_line": {"type": "integer", "description": "Line number to start reading from (0-based, default 0). Use with max_lines to read specific sections."},
                "max_lines": {"type": "integer", "description": "Max lines to return for read_file (default 200, max 500)"},
                "allow_large": {"type": "boolean", "description": "read_file only: opt in to reading files above the 500KB soft cap. start_line + max_lines still apply; total_lines is skipped over the soft max (returns total_lines_known=false). Default false — the tool returns error_code='file_too_large' with a narrowing_hint pointing at this flag."},
                "file_type": {"type": "string", "description": "File extension filter for search (e.g. 'py', 'tsx', 'ts')"},
                "repo_id": {"type": "string", "description": "Optional sibling repo slug (e.g. 'character-os', 'context-kit', 'mentorforge'). Must match a config/external_repos/<slug>.json profile. Omit to read u-d-b. Use action='list_repos' to discover valid slugs."},
            },
            "required": ["action"],
        },
    },

    # ── Analytics / Event Queries ────────────────────────────────────────────
    {
        "type": "function",
        "name": "analytics_tool",
        "description": (
            "Query behavioral analytics: DeliverableEvent counts, ATR-24h metrics, "
            "event breakdowns by type/role/time. Use this to check pilot metrics, "
            "verify event instrumentation, or answer 'how many actions today?' questions. "
            "Replaces needing to write SQL or hit the dashboard endpoint manually."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["events_summary", "atr_dashboard", "events_query"],
                    "description": "events_summary: counts by event type + time window. atr_dashboard: full Stage 3 ATR-24h metrics. events_query: flexible event query with filters.",
                },
                "days": {"type": "integer", "description": "Lookback window in days (default 7)"},
                "event_type": {"type": "string", "description": "Filter by event type (e.g. action_taken, synthesis_viewed)"},
                "deliverable_id": {"type": "string", "description": "Filter events for a specific deliverable UUID"},
                "role": {"type": "string", "description": "Filter by role tag (manager, recruiter, developer)"},
                "limit": {"type": "integer", "description": "Max events to return for events_query (default 50)"},
            },
            "required": ["action"],
        },
    },

    # ── Discord Bot Introspection ────────────────────────────────────────────
    {
        "type": "function",
        "name": "discord_tool",
        "description": (
            "Inspect the Discord bot: list registered commands, check slot usage, "
            "view cog structure, and verify bot configuration. "
            "Use this when asked about Discord commands, limits, or integration status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "commands", "cogs"],
                    "description": "status: bot config + slot usage summary. commands: list all registered commands with groups. cogs: list loaded cog classes.",
                },
            },
            "required": ["action"],
        },
    },

    # ── Mobile App Introspection ─────────────────────────────────────────────
    {
        "type": "function",
        "name": "mobile_tool",
        "description": (
            "Inspect the React Native / Expo mobile app: project config, "
            "implemented screens, API modules, dependencies. "
            "Use this when asked about the mobile app status, what screens exist, "
            "or what's been built vs what's still a placeholder."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["project_status", "screens", "api_modules", "dependencies"],
                    "description": "project_status: Expo config + build info. screens: list all screens with implementation status. api_modules: list API client files. dependencies: key package versions.",
                },
            },
            "required": ["action"],
        },
    },

    # ── VIP Invite Management ────────────────────────────────────────────────
    {
        "type": "function",
        "name": "vip_invite_tool",
        "description": (
            "Manage VIP magic-link invites for demo viewers. "
            "Create invite links, list existing invites, revoke access. "
            "Use when asked to create a demo link, VIP invite, magic link, "
            "or manage demo viewer access."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "create", "revoke"],
                    "description": "list: show all invites. create: generate new magic link. revoke: disable an invite and deactivate its user.",
                },
                "label": {
                    "type": "string",
                    "description": "Internal label for the invite (e.g. 'Austin demo Mar-2026'). Used with create action.",
                },
                "id": {
                    "type": "string",
                    "description": "Invite UUID to revoke. Used with revoke action.",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1100: Cockpit Tool — Celery ops dashboard ─────────────────────
    {
        "type": "function",
        "name": "cockpit_tool",
        "description": (
            "System operations cockpit for Celery infrastructure. "
            "View beat schedule (all periodic tasks), check task status by ID, "
            "inspect worker health and queue depths, review recent failures. "
            "Use when Chris asks about scheduled tasks, worker status, queue backlogs, "
            "or task failures."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "beat_schedule", "task_status", "worker_health",
                        "recent_failures", "queue_lengths", "trigger_task",
                        "revoke_task", "help",
                    ],
                    "description": (
                        "beat_schedule: list all periodic tasks with intervals and last run. "
                        "task_status: check a specific Celery task by ID. "
                        "worker_health: active workers, queues, concurrency. "
                        "recent_failures: failed tasks with error messages. "
                        "queue_lengths: broker depth + active/reserved counts per queue, plus per-queue state (GREEN/YELLOW/RED/CRITICAL) with reasons, and system-level overall_state + overall_reasons (top 3 offenders). Sample-based oldest_age_seconds when messages carry a timestamp header (otherwise null + parse_error=no_timestamp_field, classification falls back to depth-only). "
                        "trigger_task: manually dispatch an allowlisted Celery task (use task_name param). "
                        "revoke_task: cancel/revoke a running or queued task by task_id (optionally terminate running tasks). "
                        "help: list all actions."
                    ),
                },
                "task_id": {
                    "type": "string",
                    "description": "Celery task ID (for task_status or revoke_task actions)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default 20)",
                },
                "queue": {
                    "type": "string",
                    "description": "Filter by queue name (for recent_failures) or target queue (for trigger_task, default: long_running)",
                },
                "task_name": {
                    "type": "string",
                    "description": "Fully-qualified Celery task name for trigger_task (e.g. core.tasks.sync_congress_data)",
                },
                "task_kwargs": {
                    "type": "object",
                    "description": "Keyword arguments to pass to the triggered task (e.g. {\"dry_run\": true}). Used with trigger_task.",
                },
                "terminate": {
                    "type": "boolean",
                    "description": "For revoke_task: if true, send SIGTERM to kill a running task. Default false (just removes from queue).",
                },
            },
            "required": ["action"],
        },
    },

    # ── Railway Platform Tool — service management ─────────────────────────────
    {
        "type": "function",
        "name": "railway_tool",
        "description": (
            "Railway platform infrastructure management. List services and their "
            "deployment status, view deploy logs, restart or redeploy services, "
            "check service metrics, and inspect environment variables. "
            "Use when Chris asks about Railway services, deploys, restarts, "
            "service health, or infrastructure status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "services", "logs", "restart", "redeploy",
                        "metrics", "variables", "help",
                    ],
                    "description": (
                        "services: list all Railway services with deployment status. "
                        "logs: view recent deploy logs (requires service_name). "
                        "restart: restart a service (requires service_name). "
                        "redeploy: trigger fresh build + deploy (requires service_name). "
                        "metrics: get service details and deployment info (requires service_name). "
                        "variables: list env vars for a service, masked (requires service_name). "
                        "help: list all actions."
                    ),
                },
                "service_name": {
                    "type": "string",
                    "description": (
                        "Railway service name (e.g. 'celery-long-running', 'donkey-betz-platform', "
                        "'celery-pa', 'celery-worker', 'celery-content', 'celery-broadcast', "
                        "'celery-beat', 'celery-long-running-2', 'code-worker', 'resolve-node')"
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Max log lines to return (default 50, max 200)",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1100: Narrative Tool — Narrative drift & cultural analysis ────
    {
        "type": "function",
        "name": "narrative_tool",
        "description": (
            "Access narrative drift analysis, trend break detection, and cultural "
            "impact assessments. Browse tracked narratives, view shifts and evidence, "
            "check alerts. Use when Chris asks about narratives, cultural shifts, "
            "trend breaks, or second-order effects of world events."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "narratives", "shifts", "evidence",
                        "alerts", "help",
                    ],
                    "description": (
                        "narratives: list tracked narratives with status. "
                        "shifts: recent narrative shifts/drift detections. "
                        "evidence: evidence items for a narrative. "
                        "alerts: narrative alerts sent to Discord. "
                        "help: list all actions."
                    ),
                },
                "narrative_id": {
                    "type": "string",
                    "description": "Narrative UUID (for evidence action)",
                },
                "domain": {
                    "type": "string",
                    "enum": [
                        "politics", "markets", "tech", "culture",
                        "geopolitics", "crypto", "climate", "health",
                    ],
                    "description": "Filter narratives by domain",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 10)",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Proactive Tool ──────────────────────────────────────
    {
        "type": "function",
        "name": "proactive_tool",
        "description": (
            "View proactive alerts, notifications, smart suggestions, and automated "
            "actions generated by the system. Use when the user asks about alerts, "
            "notifications, suggestions, automations, or wants a proactive dashboard."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["alerts", "notifications", "suggestions", "automations", "dashboard", "mark_read", "bulk_ack", "dismiss"],
                    "description": (
                        "alerts: active system alerts. "
                        "notifications: recent/unread notifications. "
                        "suggestions: pending smart suggestions. "
                        "automations: active automated actions. "
                        "dashboard: aggregate counts. "
                        "mark_read: mark a single notification as read (requires notification_id). "
                        "bulk_ack: mark multiple notifications as read (optional priority/notification_type filter). "
                        "dismiss: permanently dismiss a notification (requires notification_id)."
                    ),
                },
                "notification_id": {"type": "string", "description": "UUID of notification (for mark_read/dismiss)"},
                "priority": {"type": "string", "description": "Filter by priority for bulk_ack (e.g. 'low', 'medium', 'high')"},
                "notification_type": {"type": "string", "description": "Filter by type for bulk_ack (e.g. 'action_required', 'info')"},
                "max_items": {"type": "integer", "description": "Max notifications to ack in bulk_ack (default 50, max 200)"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Distribution Tool ───────────────────────────────────
    {
        "type": "function",
        "name": "distribution_tool",
        "description": (
            "View content distribution platforms, listings, revenue, and stats. "
            "Use when the user asks about content distribution, platform listings, "
            "sales, or revenue from distributed content."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["platforms", "listings", "revenue", "stats"],
                    "description": (
                        "platforms: available distribution platforms. "
                        "listings: content listings across platforms. "
                        "revenue: revenue breakdown by platform. "
                        "stats: aggregate distribution stats."
                    ),
                },
                "status": {"type": "string", "description": "Filter listings by status"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Calendar Tool ───────────────────────────────────────
    {
        "type": "function",
        "name": "calendar_tool",
        "description": (
            "View content channels, episodes, and upcoming schedule. "
            "Use when the user asks about content calendar, channels, episodes, "
            "publishing schedule, or upcoming content."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["channels", "episodes", "upcoming", "stats"],
                    "description": (
                        "channels: list content channels. "
                        "episodes: list channel episodes. "
                        "upcoming: next due episodes. "
                        "stats: aggregate channel/episode stats."
                    ),
                },
                "channel_id": {"type": "string", "description": "Filter episodes by channel UUID"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Experiment Tool ─────────────────────────────────────
    {
        "type": "function",
        "name": "experiment_tool",
        "description": (
            "View A/B tests, experiment results, and stats. "
            "Use when the user asks about experiments, A/B tests, variants, "
            "statistical significance, or test results."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["tests", "results", "stats"],
                    "description": (
                        "tests: list A/B tests. "
                        "results: detail of a specific test + variants. "
                        "stats: aggregate test stats."
                    ),
                },
                "test_id": {"type": "string", "description": "UUID of specific test (for results action)"},
                "status": {"type": "string", "description": "Filter tests by status"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Podcast Tool ────────────────────────────────────────
    {
        "type": "function",
        "name": "podcast_tool",
        "description": (
            "View podcast shows, episodes, scripts, and stats. "
            "Use when the user asks about podcasts, shows, episodes, scripts, "
            "listen counts, or podcast production."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["shows", "episodes", "scripts", "stats"],
                    "description": (
                        "shows: list podcast shows. "
                        "episodes: list episodes (filterable by show). "
                        "scripts: get episode script text. "
                        "stats: aggregate podcast stats."
                    ),
                },
                "show_id": {"type": "string", "description": "Filter episodes by show UUID"},
                "episode_id": {"type": "string", "description": "Episode UUID (for scripts action)"},
                "status": {"type": "string", "description": "Filter episodes by status"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Campaign Tool ───────────────────────────────────────
    {
        "type": "function",
        "name": "campaign_tool",
        "description": (
            "View campaigns, campaign deliverables, and stats. "
            "Use when the user asks about campaigns, campaign status, deliverables, "
            "budgets, or client projects."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "detail", "stats"],
                    "description": (
                        "list: list all campaigns. "
                        "detail: campaign + its deliverables. "
                        "stats: aggregate campaign stats."
                    ),
                },
                "campaign_id": {"type": "string", "description": "Campaign UUID (for detail action)"},
                "status": {"type": "string", "description": "Filter campaigns by status"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Audit Tool ──────────────────────────────────────────
    {
        "type": "function",
        "name": "audit_tool",
        "description": (
            "View audit findings, wiring defects, citation violations, and P0 summary. "
            "Use when the user asks about audits, findings, wiring defects, citation "
            "violations, compliance, or system quality."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["findings", "wiring_defects", "citations", "p0_summary"],
                    "description": (
                        "findings: list audit findings. "
                        "wiring_defects: list wiring defects. "
                        "citations: list citation violations. "
                        "p0_summary: P0+P1 unresolved findings only."
                    ),
                },
                "priority": {"type": "string", "description": "Filter findings by priority (P0, P1, P2, P3)"},
                "status": {"type": "string", "description": "Filter by status"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: ConceptForge Tool ───────────────────────────────────
    {
        "type": "function",
        "name": "conceptforge_tool",
        "description": (
            "View ConceptForge pipeline runs, stages, artifacts, and stats. "
            "Use when the user asks about concept forge, pipeline runs, creative "
            "artifacts, or concept generation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["runs", "run_detail", "stats"],
                    "description": (
                        "runs: list pipeline runs. "
                        "run_detail: run + stages + artifacts. "
                        "stats: aggregate run stats."
                    ),
                },
                "run_id": {"type": "string", "description": "Run UUID (for run_detail action)"},
                "status": {"type": "string", "description": "Filter runs by status"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Profile Tool ────────────────────────────────────────
    {
        "type": "function",
        "name": "profile_tool",
        "description": (
            "View extended user profile, tracked skills, and learning summary. "
            "Use when the user asks about their profile, skills, expertise, "
            "learning progress, or capabilities."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["profile", "skills", "learning_summary", "preferences", "update_preferences", "desk_preferences"],
                    "description": (
                        "profile: extended user profile. "
                        "skills: tracked skills with proficiency. "
                        "learning_summary: skill aggregates. "
                        "preferences: structured user preferences (goals, routines, risk_tolerance, interests). "
                        "update_preferences: update a preference field (use field + value params). "
                        "desk_preferences: scoped preferences for a desk (use desk param: sports/stocks/content/general)."
                    ),
                },
                "field": {"type": "string", "description": "Preference field to update (for update_preferences). Allowed: long_term_goals, current_projects, quarterly_objectives, learning_style, communication_style, decision_framework, current_learning_goals, personal_values, delegation_preferences, work_schedule, time_zone, privacy_level"},
                "value": {"type": "string", "description": "New value for the preference field (for update_preferences)"},
                "desk": {"type": "string", "enum": ["sports", "stocks", "content", "general"], "description": "Desk scope for desk_preferences action"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: Self-Awareness Tool ─────────────────────────────────
    {
        "type": "function",
        "name": "self_awareness_tool",
        "description": (
            "View system self-awareness metrics, analysis reports, and evolution history. "
            "Use when the user asks about system self-awareness, introspection, "
            "self-analysis, system evolution, or meta-cognition."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["metrics", "reports", "evolution", "stats", "collect"],
                    "description": (
                        "metrics: latest system metrics snapshot. "
                        "reports: recent self-analysis reports. "
                        "evolution: system evolution history. "
                        "stats: aggregate self-awareness stats. "
                        "collect: gather live metrics from agents/tasks and record a new snapshot."
                    ),
                },
                "limit": {"type": "integer", "description": "Max results (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-W2: ATS Tool ────────────────────────────────────────────
    {
        "type": "function",
        "name": "ats_tool",
        "description": (
            "View ATS keyword mappings, resume optimization logs, persona templates, "
            "and stats. Use when the user asks about ATS optimization, keywords, "
            "resume scoring, or job application optimization."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["keywords", "optimizations", "templates", "stats"],
                    "description": (
                        "keywords: ATS keyword mappings. "
                        "optimizations: resume optimization logs. "
                        "templates: persona resume templates. "
                        "stats: aggregate ATS stats."
                    ),
                },
                "category": {"type": "string", "description": "Filter keywords by category"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Remote Code Worker ────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "code_job_tool",
        "description": (
            "Submit, monitor, and manage remote code jobs. "
            "A code job clones a repo, implements changes via AI, runs tests, "
            "pushes a branch, and opens a PR. Supports dry_run mode (no git ops). "
            "Use when Chris asks to submit a coding task, check job progress, "
            "view job logs, cancel a job, or list past code jobs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["submit", "status", "logs", "cancel", "list", "list_repos", "add_repo"],
                    "description": (
                        "submit: create a new code job for a repo. "
                        "status: check progress and results of a job. "
                        "logs: stream log lines from a running or completed job. "
                        "cancel: cancel a running job. "
                        "list: list recent code jobs with optional filters. "
                        "list_repos: list all registered repos in the allowlist. "
                        "add_repo: add a new GitHub repo to the allowlist (requires repo_url)."
                    ),
                },
                "repo_slug": {
                    "type": "string",
                    "description": "Repository slug (e.g. 'clwest/donkey-betz-platform'). Required for submit.",
                },
                "task_prompt": {
                    "type": "string",
                    "description": "Description of the coding task to implement. Required for submit.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["dry_run", "real"],
                    "description": "Execution mode: dry_run (no git ops, default) or real (full pipeline with push+PR).",
                },
                "ref": {
                    "type": "string",
                    "description": "Branch to clone from (default: repo default branch). Used with submit.",
                },
                "base_branch": {
                    "type": "string",
                    "description": "Branch to target for PR (default: repo default branch). Used with submit.",
                },
                "acceptance_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of acceptance criteria the implementation must meet. Used with submit.",
                },
                "test_command": {
                    "type": "string",
                    "description": "Override test command (must be in allowlist). Used with submit.",
                },
                "job_id": {
                    "type": "string",
                    "description": "Job UUID. Required for status, logs, cancel.",
                },
                "after_sequence": {
                    "type": "integer",
                    "description": "Return log lines after this sequence number (cursor pagination). Used with logs.",
                },
                "status_filter": {
                    "type": "string",
                    "description": "Filter jobs by status (e.g. 'running', 'succeeded'). Used with list.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default 20). Used with list and logs.",
                },
                "repo_url": {
                    "type": "string",
                    "description": "GitHub repo URL (e.g. 'https://github.com/owner/repo'). Required for add_repo.",
                },
                "name": {
                    "type": "string",
                    "description": "Human-readable repo name. Auto-derived from URL if omitted. Used with add_repo.",
                },
                "default_branch": {
                    "type": "string",
                    "description": "Default base branch (default: 'main'). Used with add_repo.",
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1189 Item 3: SpiderData Aggregation Tool ───────────────────────
    {
        "type": "function",
        "name": "spider_data_aggregation_tool",
        "description": (
            "Group-by counts of SpiderData rows by data_type over a windowed "
            "time range, with optional spider_name + data_type filters and "
            "top contributors per bucket. Use to verify spider supply per "
            "category (e.g., 'how many actionable ai_ml items in the last "
            "30d?'), to validate Session 1188 AC watches, or to drive "
            "PR-3B retuning decisions. v1 is counts-only — no per-row "
            "samples, no text search, no source-domain breakdowns."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["aggregate"],
                    "description": "v1 supports only 'aggregate'.",
                },
                "days_back": {
                    "type": "integer",
                    "description": "Lookback window in days. Default 30, min 1, max 90.",
                },
                "actionable_only": {
                    "type": "boolean",
                    "description": (
                        "When true (default), the response counts and "
                        "sorts by is_actionable=True rows. total_count is "
                        "still returned for every bucket either way."
                    ),
                },
                "data_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional whitelist of SpiderData.data_type values "
                        "to include (e.g., ['ai_ml', 'design']). Null/omitted "
                        "= aggregate across every data_type seen in-window."
                    ),
                },
                "spider_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional whitelist of spider_name values to "
                        "include. Useful for debugging a single feed."
                    ),
                },
                "include_top_spiders": {
                    "type": "boolean",
                    "description": (
                        "When true (default), each data_type bucket includes "
                        "a top_spiders array ranked by the same actionable "
                        "filter as the parent."
                    ),
                },
                "top_spiders_limit": {
                    "type": "integer",
                    "description": "Max spiders per bucket. Default 5, min 1, max 25.",
                },
                "include_totals": {
                    "type": "boolean",
                    "description": (
                        "When true (default), the response includes a "
                        "top-level totals block (actionable_count, "
                        "total_count, distinct_data_types, distinct_spiders)."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-Audit: Spider Status Tool ─────────────────────────────────
    {
        "type": "function",
        "name": "spider_status_tool",
        "description": (
            "View individual spider health and activity. Use when the user asks "
            "about spider status, which spiders are active/stale, spider item counts, "
            "or spider data history."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "history", "detail", "search"],
                    "description": (
                        "list: per-spider stats (items_24h, items_7d, age_hours, active/stale/never_run). Paginated (S2868 Ledger #1): response includes total/has_more/offset/limit. Canonical iteration pattern: start with offset=0, then advance offset += limit until has_more=false. Default union with the spider registry so never-run spiders are visible with status='never_run' (toggle via include_registry=false). Legacy orphan spider_names visible by default (toggle via include_orphans=false). Each row also carries an in_registry boolean for triage (true = current class in ai_core.spiders.spider_registry). "
                        "history: item history for a specific spider. "
                        "detail: fetch full raw_data/processed_data for a SpiderData item by ID. "
                        "search: search spider data by query, data_type, or spider_name."
                    ),
                },
                "spider_name": {"type": "string", "description": "Spider name filter (for history, list, or search)"},
                "item_id": {"type": "string", "description": "SpiderData UUID (for detail action)"},
                "query": {"type": "string", "description": "Text search in embedding_text/source_url (for search action). S2869 Ledger #2: preview field now falls back to raw_data['items'][0].{title|name|id} when embedding_text is empty — items previously returning empty preview strings now surface a best-effort title. Preview is best-effort (not schema); do not rely on raw_data structure for downstream logic."},
                "data_type": {"type": "string", "description": "Filter by data_type (for search action)"},
                "limit": {"type": "integer", "description": "Max results (default 30 for list, 20 elsewhere). List cap 500; history/search cap 100."},
                "offset": {"type": "integer", "description": "Pagination offset for list action (S2868). Combine with limit + response has_more to iterate the full spider inventory."},
                "include_registry": {"type": "boolean", "description": "For list (default true): union LegacySpiderData rows with the runtime spider registry so never-run spiders are visible with status='never_run'. Pass false to scope strictly to spiders that have written data."},
                "include_orphans": {"type": "boolean", "description": "For list (default true): keep legacy spider_names present in LegacySpiderData but absent from the current registry. Pass false to filter down to registry-known spiders only."},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-Audit: Agent Memory Tool ──────────────────────────────────
    {
        "type": "function",
        "name": "agent_memory_tool",
        "description": (
            "Browse agent memories and knowledge sources. Use when the user asks "
            "about what agents remember, agent knowledge, memory entries, or agent "
            "learning history."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "knowledge", "stats"],
                    "description": (
                        "list: agent memories with optional search query. "
                        "knowledge: knowledge sources for a specific agent. "
                        "stats: aggregate memory stats (counts, types, avg importance)."
                    ),
                },
                "agent_name": {"type": "string", "description": "Agent name filter (supports snake_case)"},
                "query": {"type": "string", "description": "Search query for list action"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-Audit: Heartbeat History Tool ─────────────────────────────
    {
        "type": "function",
        "name": "heartbeat_history_tool",
        "description": (
            "View heartbeat history and trends. Use when the user asks about "
            "system heartbeat history, health trends over time, uptime, or "
            "historical system status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["recent", "trends"],
                    "description": (
                        "recent: last N heartbeats with scores. "
                        "trends: aggregate stats over N hours (status distribution, avg score)."
                    ),
                },
                "limit": {"type": "integer", "description": "Max heartbeats for recent (default 20)"},
                "hours": {"type": "integer", "description": "Hours back for trends (default 24)"},
            },
            "required": ["action"],
        },
    },

    # ── Session 1035-Audit: Infra Health Tool ──────────────────────────────────
    {
        "type": "function",
        "name": "infra_health_tool",
        "description": (
            "Deep infrastructure health checks — Redis, PostgreSQL, dependencies, "
            "and runtime metrics. Use when the user asks about Redis health, database "
            "performance, dependency status, memory usage, or infrastructure diagnostics."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["redis_health", "db_perf", "dependency_matrix", "runtime_metrics"],
                    "description": (
                        "redis_health: Redis ping, memory, clients, evictions, hit rate. "
                        "db_perf: PostgreSQL connections, cache hit ratio, tuple stats, deadlocks. "
                        "dependency_matrix: checks web/postgres/redis/celery/pgvector/spiders/storage. "
                        "runtime_metrics: process RSS/VMS/CPU/threads, system RAM/disk, Railway env."
                    ),
                },
            },
            "required": ["action"],
        },
    },
    # ── Session 1142: Semantic-ish doc search over .rag/corpus.jsonl ────────
    # ── Session 1145 P2: optional originating_session filter via docs/_provenance.json
    {
        "type": "function",
        "name": "search_docs",
        "description": (
            "Search the /docs/ corpus and return ranked chunks with inline "
            "citations. Use when the user asks 'where in the docs does it say X?', "
            "'find the passage about X', or needs an answer grounded in specific "
            "doc passages. Complements kb_tool (which browses the Document table); "
            "search_docs is for finding the literal text. Powered by "
            "`core.rag.build_docs_context` over `.rag/corpus.jsonl` "
            "(19K+ chunks across 2K+ files). Returns [docs/path#chunk_id] citations. "
            "Session 1145 P2: optional originating_session filter restricts results "
            "to docs whose origin session matches (per docs/_provenance.json)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language question or keywords to search.",
                },
                "k": {
                    "type": "integer",
                    "description": "Top-K chunks to return (default 8, max 20).",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Cap on total chars across returned chunks (default 6000, max 12000).",
                },
                "originating_session": {
                    "type": "integer",
                    "description": (
                        "Optional. Restrict results to chunks from docs whose "
                        "originating session matches (per docs/_provenance.json). "
                        "Use when the user asks 'what did Session N produce?' or "
                        "'find the docs born in Session N'. Docs without provenance "
                        "are excluded when this filter is active."
                    ),
                },
            },
            "required": ["query"],
        },
    },
    # ── R2-6: KB / Embedding browsing tool ──────────────────────────────────
    {
        "type": "function",
        "name": "kb_tool",
        "description": (
            "Browse the knowledge base — documents, embedding collections, chunk counts, "
            "and text search across all embedded content. Use when the user asks about "
            "KB content, embeddings, document chunks, what's been embedded, or RAG sources."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["stats", "documents", "chunks", "search_embeddings", "semantic_search"],
                    "description": (
                        "stats: overall KB metrics (doc count, embedding counts by type). "
                        "documents: list documents with chunk counts + Session 1234 D9/D10 enrichment "
                        "(category, document_class, is_pinned, tags, retrieval_boost); supports "
                        "filters category / document_class / is_pinned / min_session / include_superseded. "
                        "chunks: view chunks for a specific document. "
                        "search_embeddings: text search across unified embeddings (legacy). "
                        "semantic_search: Session 1234 D13 — native pgvector cosine similarity over "
                        "DocumentEmbedding (16k+ chunks). Returns ranked chunks with [docs/path#chunk] "
                        "citations, supports the same D9/D10 filter set as documents action + a "
                        "similarity_threshold knob. Use this when the user asks 'find the passage about X' "
                        "or 'where does the corpus mention Y' — it's the highest-signal retrieval surface."
                    ),
                },
                "document_id": {"type": "string", "description": "Document UUID (for chunks action)"},
                "query": {"type": "string", "description": "Search term for documents or embeddings (title icontains)"},
                "content_type": {"type": "string", "description": "Filter unified embeddings by content_type (e.g. agent_knowledge, spider_data, document_chunk) — search_embeddings action only"},
                # Session 1234 D11 — Document filter params (documents action)
                "category": {"type": "string", "description": "Filter documents by category (e.g. 'handoffs', 'specs', 'narratives', 'audits', 'topics', 'architecture'). documents action only."},
                "document_class": {"type": "string", "description": "Filter documents by document_class (e.g. 'handoff', 'spec', 'narrative', 'audit', 'guide', 'architecture', 'plan'). documents action only."},
                "is_pinned": {"type": "boolean", "description": "When true, return only pinned docs (active narratives/specs/indexes/guides/architecture). documents action only."},
                "min_session": {"type": "integer", "description": "Filter handoffs to session-N tag >= this threshold (e.g. 1200 → only Session 1200+ handoffs). documents action only."},
                "include_superseded": {"type": "boolean", "description": "When true, include archived/superseded docs in results. Default false. documents action only."},
                "limit": {"type": "integer", "description": "Max results (default 20, max 50)"},
                # Cycle 1A KFI-3 (ADR-0130) — authority-aware retrieval.
                "canonical_authority": {
                    "type": "string",
                    "enum": ["workspace_canonical", "repo_canonical", "derived"],
                    "description": (
                        "Filter by source-tier classification. "
                        "'workspace_canonical' surfaces ratified workspace "
                        "Deliverable mirrors (governance/research canonical). "
                        "'repo_canonical' surfaces /docs/-ingested content. "
                        "'derived' surfaces API/spider-imported content. "
                        "semantic_search action only."
                    ),
                },
                "authority_weighted": {
                    "type": "boolean",
                    "description": (
                        "When true, re-rank results by weighted_score = "
                        "similarity * authority_weight (workspace_canonical=2.0, "
                        "repo_canonical=1.5, derived=1.0), tie-broken by "
                        "updated_at DESC then id ASC. Default false preserves "
                        "cosine-similarity ranking. semantic_search action only."
                    ),
                },
            },
            "required": ["action"],
        },
    },
    # ── BPaaS: Build Packet as a Service ─────────────────────────────────
    {
        "type": "function",
        "name": "bpaas_tool",
        "description": (
            "Build Packet as a Service — create client projects from structured build packets. "
            "Actions: create_project (creates workspace project + repos + preview env + magic link from a build packet), "
            "generate_close_pack (generates SOW + delivery checklist + proposal from a build packet), "
            "get_schema (returns the build packet JSON schema), "
            "get_example (returns the Norman Handyman MVP example packet)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create_project", "generate_close_pack", "get_schema", "get_example"],
                    "description": (
                        "create_project: create full project from build packet (needs workspace_id + packet). "
                        "generate_close_pack: generate SOW/checklist/proposal (needs packet). "
                        "get_schema: return the build packet JSON schema. "
                        "get_example: return the Norman Handyman example build packet."
                    ),
                },
                "workspace_id": {"type": "string", "description": "Workspace UUID (required for create_project)"},
                "packet": {"type": "object", "description": "Build packet object (required for create_project and generate_close_pack)"},
            },
            "required": ["action"],
        },
    },
    # ── Claude Code Engineer — Rigby can spawn autonomous coding sessions ──
    {
        "type": "function",
        "name": "claude_code_tool",
        "description": "Spawn an autonomous Claude Code engineering session that can read files, write code, create branches, and open PRs. Use when you need code changes, bug fixes, new features, or technical investigation that requires reading/modifying the codebase. Use request_mode='answer' for readonly Q&A about the codebase (no PR created); 'change' for code modifications; default 'auto' picks based on task verbs.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Detailed description of what Claude Code should do. Be specific about files, functions, or features involved.",
                },
                "conversation_id": {
                    "type": "string",
                    "description": "Conversation ID to post results back to (optional — defaults to current conversation).",
                },
                "workspace_id": {
                    "type": "string",
                    "description": (
                        "Session 2967 Slice 7 — workspace UUID whose root_path becomes the engineer's "
                        "working tree. If omitted, resolves to the currently-active workspace "
                        "(is_active=True). If neither an explicit workspace_id nor an active workspace "
                        "can be resolved, the dispatch falls back to the Railway /tmp clone path "
                        "(engineer will report 'no repo detected' on local dev). Response envelope echoes "
                        "workspace_id_resolved + resolved_from ('explicit' | 'active_workspace' | 'fallback')."
                    ),
                },
                "request_mode": {
                    "type": "string",
                    "enum": ["auto", "answer", "change"],
                    "description": (
                        "Session 1230 P4. 'answer' = readonly codebase Q&A; "
                        "engineer must produce the requested output shape, "
                        "no branches/PRs, no clarification. 'change' = code "
                        "modification; engineer reads, edits, creates a "
                        "branch + PR. 'auto' (default) = dispatcher infers "
                        "from task verbs (add/fix/refactor/etc → change; "
                        "everything else → answer). Set explicitly when the "
                        "verb heuristic would misclassify."
                    ),
                },
                "max_iterations": {
                    "type": "integer",
                    "description": (
                        "Session 2967 Slice 7 PR-1. Hard cap on the engineer's "
                        "LLM tool-use loop. Null / omitted uses the engine "
                        "default (150). Bump for wide-scope arc dispatches; "
                        "keep low for tight tasks. When the cap fires, the "
                        "envelope returns status='budget_exceeded' with "
                        "partial results — not an error."
                    ),
                },
                "max_cost_usd": {
                    "type": "number",
                    "description": (
                        "Session 2967 Slice 7 PR-1. Hard cap on cumulative "
                        "Anthropic spend for this dispatch (input + output + "
                        "cache-read + cache-write tokens, priced against "
                        "sonnet-4-6 rates). Null / omitted uses the engine "
                        "default ($5). Openai fallback path ignores this and "
                        "uses iteration cap only. When the cap fires, envelope "
                        "returns status='budget_exceeded' with partial results."
                    ),
                },
                "engine_mode": {
                    "type": "string",
                    "enum": ["v1", "v2"],
                    "description": (
                        "Session 2968 PR-A. Selects the engineer implementation: "
                        "'v1' (default) runs the homegrown LLM loop with 5 primitive "
                        "tools; 'v2' subprocess-dispatches to the `claude` CLI (real "
                        "coding tools + auto-CLAUDE.md read + resumable sessions). "
                        "Omit to use the CLAUDE_CODE_ENGINE_MODE env default. Explicitly "
                        "set 'v2' to A/B test the new path on a single dispatch. NOTE: "
                        "v2 refuses max_cost_usd < $0.25 (CLI startup cache alone burns "
                        "~$0.13); v2 caps max_iterations at 50 until PR-D validation."
                    ),
                },
                "deliverable_id": {
                    "type": "string",
                    "description": (
                        "Session 2968 PR-B. UUID of a Deliverable (typically "
                        "deliverable_type='engineering_spec') whose content becomes "
                        "the spec for this dispatch. When provided, the handler "
                        "resolves the Deliverable and constructs the engineer's task "
                        "from its title + content — Chris can review the spec in the "
                        "workspace UI BEFORE dispatch (catches scope creep + $-runaway "
                        "risk at spec-review time). When BOTH `task` and "
                        "`deliverable_id` are set, deliverable_id wins (spec beats "
                        "free-form). When ONLY `deliverable_id` is set, `task` may be "
                        "omitted. Not-found + workspace-mismatch return error envelopes "
                        "without dispatch."
                    ),
                },
            },
            # S2968 PR-B: `task` is no longer strictly required — `deliverable_id`
            # can satisfy the "give me work to do" gate. The dispatcher enforces
            # at least one is present (see td_handlers_codejobs._handle_claude_code).
            "required": [],
        },
    },

    # ── In-App Messaging — read-only v0 (Session 1253 PR 4) ────────────────
    # send_message was previously in this enum but was removed per Rigby's
    # PR 4 SIGN-WITH-EDITS: the LLM must not free-form send DMs to other
    # users. Programmatic shift-report writes go directly to the ORM via
    # `core.employees.comms.post_shift_report` (only path that creates a
    # DM today). The underlying `_handle_messaging` handler in
    # td_handlers_core.py still implements `send_message` for any
    # non-PA caller, but the LLM cannot see or call it from this schema.
    {
        "type": "function",
        "name": "messaging_tool",
        "description": (
            "Read-only access to in-app messaging threads. Use when a "
            "user asks 'check my messages', 'any new messages?', or "
            "'show thread X'. Actions: list_threads (list the user's "
            "message threads), get_thread (read messages in a thread), "
            "unread_count (total unread). Outbound message sending is "
            "not exposed via this tool surface in v0 — Rigby posts "
            "shift reports programmatically from her job tasks."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list_threads", "get_thread", "unread_count"],
                    "description": (
                        "list_threads: list all message threads. "
                        "get_thread: get messages in a specific thread "
                        "(requires thread_id). "
                        "unread_count: get total unread message count."
                    ),
                },
                "thread_id": {
                    "type": "string",
                    "description": "Thread ID (for get_thread).",
                },
            },
            "required": ["action"],
        },
    },
    # ── Session tool: conversation health + fresh session creation ──
    {
        "type": "function",
        "name": "session_tool",
        "description": (
            "Manage conversation sessions: check conversation health/freshness, "
            "create a fresh conversation, or list recent conversations. Use when "
            "asked about session health, context drift, whether to start fresh, "
            "creating a new conversation, or listing past conversations. Also use "
            "proactively when you notice the conversation is getting long or drifting."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "health_check", "create_fresh", "list_recent", "whoami",
                        "retire", "set_active", "seed",
                    ],
                    "description": (
                        "health_check: analyze current conversation freshness "
                        "(score 0-100, recommendation, reasons, auto-summary, starter prompt). "
                        "create_fresh: create a new conversation and return its ID + starter prompt. "
                        "list_recent: list recent conversations with titles and message counts. "
                        "whoami: return the authenticated user's identity (username/email/id/is_staff) "
                        "plus whether the current (or supplied) conversation_id belongs to that user. "
                        "Use to confirm 'I am operating as <username>' before scope-sensitive work, "
                        "or to verify conversation ownership when scope=mine workflows depend on it. "
                        "retire: mark a conversation as retired (session_active=False on all rows), "
                        "blocking the conversation_action_dispatcher from firing stale agent "
                        "dispatches into it (Session 1212 ~$3.60/day waste fix). Requires "
                        "conversation_id. If retiring the currently-bound thread, requires "
                        "force=true. "
                        "set_active: un-retire a conversation (session_active=True on all rows). "
                        "Inverse of retire; idempotent. Requires conversation_id. "
                        "seed: append a [SYSTEM SEED] message into an existing conversation "
                        "to backfill starter context. Requires conversation_id + non-empty "
                        "content (empty seeds are rejected at the handler edge)."
                    ),
                },
                "conversation_id": {
                    "type": "string",
                    "description": (
                        "Conversation ID to target. Used by health_check, retire, set_active, "
                        "seed, and the fallback summary lookup in create_fresh. Defaults to "
                        "the current conversation for read-only actions; required for retire / "
                        "set_active / seed."
                    ),
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the new conversation (create_fresh).",
                },
                "carry_forward_summary": {
                    "type": "string",
                    "description": "Summary text to carry into the new conversation (create_fresh).",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of recent conversations to return (list_recent, default 10).",
                },
                "force": {
                    "type": "boolean",
                    "description": (
                        "retire only: required (true) when retiring the currently-bound "
                        "thread. Default false — refuses to silently retire the chat the "
                        "request arrived through. Cross-thread retires don't need this."
                    ),
                },
                "content": {
                    "type": "string",
                    "description": (
                        "seed only: REQUIRED non-empty seed text. Will be prefixed with "
                        "`[SYSTEM SEED]` and stored as a real ChatConversation row with "
                        "source='pa' so it's visible in conversation history. Whitespace "
                        "and empty strings are rejected."
                    ),
                },
            },
            "required": ["action"],
        },
    },

    # ── Session 1174 PR-2b-1: Follow-up subscription ────────────────────────
    {
        "type": "function",
        "name": "schedule_followup",
        "description": (
            "Subscribe THIS conversation to a completion notification for a previously "
            "dispatched async agent task. Call this RIGHT AFTER you dispatch a long-running "
            "agent (run_agent / workflow_orchestration_agent / etc.) so the user gets an "
            "automatic 'agent finished' message in this same conversation when the task "
            "completes — instead of you going silent until the user manually asks. "
            "Pass `execution_id` (UUID returned by execution_history_tool) when you have it, "
            "or `task_id` (Celery task_id returned by the dispatch tool) as a convenience "
            "lookup. after_seconds is a TTL — if the agent hasn't finished in that window, "
            "the subscription quietly expires. Cap 600s. If the agent is already done at "
            "subscribe time, the notification fires immediately. Safe to call multiple times "
            "with the same IDs — a unique constraint dedupes per (execution, conversation)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "execution_id": {
                    "type": "string",
                    "description": "Canonical UUID of the AgentExecution row (from execution_history_tool detail/recent).",
                },
                "task_id": {
                    "type": "string",
                    "description": "Celery task_id from the dispatch tool (e.g. run_agent's task_id). Used as fallback lookup if execution_id isn't known yet.",
                },
                "after_seconds": {
                    "type": "integer",
                    "description": "TTL window in seconds (default 60, max 600). Subscription auto-expires if no completion in this window.",
                },
            },
            "required": [],
        },
    },
    # ── S2951: agent_job_status — poll dispatched agent tasks ───────────
    # S3046: extended with lineage + fanout fields (parent_execution_id,
    # root_execution_id, child_count, subtree_count, children, fanout_available).
    {
        "type": "function",
        "name": "agent_job_status",
        "description": (
            "Poll status + output preview for an agent job dispatched via run_agent "
            "(or any tool that returns a Celery task_id). Sibling to schedule_followup — "
            "same lookup shape (task_id OR execution_id) — but returns an immediate "
            "status snapshot instead of subscribing to a completion notification. "
            "Use to poll long-running dispatches when you don't want to wait for the "
            "follow-up banner. Returns: status (queued|in_progress|completed|failed), "
            "agent_name, duration_ms, error_message, output_preview (first 800 chars of "
            "output_data.message). Also returns lineage + fanout: parent_execution_id, "
            "root_execution_id, child_count (direct children dispatched by this run), "
            "subtree_count (all descendants under the same root, excluding self), "
            "children (list capped at 20 with execution_id/agent_name/status/timestamps), "
            "children_truncated (bool: true if child_count > 20), and fanout_available "
            "(bool: false on pending/unknown/missing-lookup branches where no AgentExecution "
            "row exists yet). Fanout counts reflect recorded lineage only — legacy rows and "
            "coordinator dispatch paths that don't thread parent_execution_id at dispatch "
            "time may undercount."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Celery task_id from dispatch response (e.g. run_agent's task_id).",
                },
                "execution_id": {
                    "type": "string",
                    "description": "Canonical UUID of AgentExecution row (from execution_history_tool detail/recent). Preferred if known.",
                },
            },
            "required": [],
        },
    },
    # ── Session 1250 PR 7: Rigby internal work-queue review tools ───────
    {
        "type": "function",
        "name": "rigby_work_item",
        "description": (
            "Rigby's internal operational work queue. Read and transition "
            "RigbyWorkItem rows produced by Rigby Event Intake. NO human "
            "notification, NO agent dispatch — internal queue only. Gated "
            "by RIGBY_WORK_QUEUE_REVIEW_ENABLED; when disabled, returns "
            "a 'tools disabled' response instead of acting."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "acknowledge", "resolve", "ignore", "delegate"],
                    "description": (
                        "list: paginated read (filters: status, decision, "
                        "priority_min, since, limit, offset). "
                        "acknowledge: transition open → acknowledged. "
                        "Idempotent on already-acknowledged. Optional note. "
                        "resolve: transition to resolved. Requires "
                        "outcome ∈ {acted, delegated_externally, "
                        "no_action_needed}. Optional note. Sets resolved_at. "
                        "ignore: transition to ignored. Requires non-empty "
                        "reason. "
                        "delegate: dispatch the work item to an agent via "
                        "Rigby Mission Delegation. v0 routes 'monitor' "
                        "decisions to TrendAnalysisAgent; 'notify' is not "
                        "delegatable. Re-delegation is rejected while a "
                        "non-terminal AgentExecution exists for the item. "
                        "Gated by RIGBY_DELEGATION_ENABLED."
                    ),
                },
                "work_item_id": {
                    "type": "string",
                    "description": "UUID of the RigbyWorkItem (for acknowledge / resolve / ignore).",
                },
                "id": {
                    "type": "string",
                    "description": "Alias for work_item_id.",
                },
                "status": {
                    "type": "string",
                    "enum": ["open", "acknowledged", "resolved", "ignored"],
                    "description": "For list: filter by status.",
                },
                "decision": {
                    "type": "string",
                    "enum": ["monitor", "notify"],
                    "description": "For list: filter by intake decision class.",
                },
                "priority_min": {
                    "type": "integer",
                    "description": "For list: minimum priority (inclusive). Higher = sooner.",
                },
                "since": {
                    "type": "string",
                    "description": "For list: ISO-8601 datetime; only items created at or after this time.",
                },
                "limit": {
                    "type": "integer",
                    "description": "For list: max rows (default 25, max 100).",
                },
                "offset": {
                    "type": "integer",
                    "description": "For list: pagination offset (default 0).",
                },
                "outcome": {
                    "type": "string",
                    "enum": ["acted", "delegated_externally", "no_action_needed"],
                    "description": "For resolve: closed-vocab outcome.",
                },
                "note": {
                    "type": "string",
                    "description": "Optional note for acknowledge / resolve.",
                },
                "reason": {
                    "type": "string",
                    "description": "Required non-empty reason for ignore.",
                },
            },
            "required": ["action"],
        },
    },

    # ── AI Employee framework v0 (Session 1252 PR 1 + PR 2) ───────────────
    {
        "type": "function",
        "name": "employee_tool",
        "description": (
            "Inspect or dispatch jobs on the AI Employee registry. "
            "Actions in v0: (1) describe — read-only profile + job "
            "contract for an employee. (2) run_now (Session 1252 PR 2) — "
            "Rigby-only dispatch of an assigned job's task immediately. "
            "(3) status (Session 1253 PR 3) — read-only daily-read "
            "trust/timing/drift summary over a 7d/30d/90d window. "
            "(4) evidence_for_mission (PR 3) — per-mission join across "
            "OpsRun + OpsRunEvent + Deliverable + DeliverableEvent + "
            "LLMCallEvent + ToolCallRecord. Use describe for contract "
            "questions; run_now to kick off the docs cascade on demand; "
            "status for the morning health check; evidence_for_mission "
            "for postmortem on a specific mission_id."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "describe",
                        "run_now",
                        "status",
                        "evidence_for_mission",
                    ],
                    "description": (
                        "describe / run_now (Rigby-only) / status "
                        "(read-only) / evidence_for_mission (read-only)."
                    ),
                },
                "employee": {
                    "type": "string",
                    "description": "Employee handle (lowercase). v0: 'rigby'.",
                },
                "job": {
                    "type": "string",
                    "description": (
                        "Job key. For describe it scopes the response; for "
                        "run_now / status it selects which job. v0 known "
                        "keys: 'docs_manager'."
                    ),
                },
                "wait_for_result": {
                    "type": "boolean",
                    "description": (
                        "run_now only: when true, polls up to 90s for the "
                        "mission to reach a terminal status before "
                        "returning. Default false (immediate return)."
                    ),
                },
                "window": {
                    "type": "string",
                    "enum": ["7d", "30d", "90d"],
                    "description": (
                        "status only: rollup window. Default '7d'. "
                        "Note: trust_status='under_review' threshold "
                        "always uses the last 7 days regardless of "
                        "window — it's a trip-wire, not a lens."
                    ),
                },
                "mission_id": {
                    "type": "string",
                    "description": (
                        "evidence_for_mission: UUID of the OpsRun to "
                        "dump. status: optional pointer hint — when "
                        "supplied, the status response carries a "
                        "requested_mission_pointer redirecting to "
                        "evidence_for_mission (status does NOT inline "
                        "evidence)."
                    ),
                },
                "verbose": {
                    "type": "boolean",
                    "description": (
                        "evidence_for_mission only. Default false: "
                        "error_tail is summarized as error_tail_preview "
                        "(last 30 lines) + has_full_error_tail flag. "
                        "true: full error_tail returned."
                    ),
                },
            },
            "required": ["action", "employee"],
        },
    },
    {
        "type": "function",
        "name": "mission_verdict",
        "description": (
            "Rigby-only: certify, reject, or defer a MissionRun. Writes one "
            "OpsRunEvent (label='verdict_issued:<verdict>') and flips "
            "OpsRun.status to passed/failed/partial. Idempotent — calling "
            "twice with the same (mission_id, verdict) is a no-op. Use after "
            "you have inspected the mission's evidence (OpsRunEvents, "
            "LLMCallEvents, ToolCallRecords) and reached a verdict. "
            "Rejected callers receive TOOL_PERMISSION_DENIED."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["certify", "reject", "defer"],
                    "description": (
                        "certify → status=passed; reject → status=failed; "
                        "defer → status=partial."
                    ),
                },
                "mission_id": {
                    "type": "string",
                    "description": "UUID of the OpsRun (domain='mission') row.",
                },
                "confidence": {
                    "type": "number",
                    "description": "Optional 0.0-1.0 confidence; clamped to range.",
                },
                "evidence_refs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional pointer strings, e.g. "
                        "['llm_call:<uuid>', 'deliverable:<uuid>']."
                    ),
                },
                "notes": {
                    "type": "string",
                    "description": "Optional free-form note.",
                },
            },
            "required": ["action", "mission_id"],
        },
    },
    # ── S2953: agent_capability_drift_tool — Rigby-callable audit surface ──
    {
        "type": "function",
        "name": "agent_capability_drift_tool",
        "description": (
            "Run the agent capability drift scanner (read-only). Checks four invariants: "
            "(1) every AGENT_MAP entry has a matching Agent DB row; (2) every non-internal "
            "agent has enum + mapping + dispatcher-handler coverage; (3) every 'supported'-tier "
            "agent has ≥1 successful execution in the recent window (default 30 days). "
            "Exceptions allowlist (capabilities_exceptions.yaml) can suppress findings per "
            "tier: internal-only / legacy / rerouted / experimental. Same codepath as the "
            "`scan_agent_capability_drift` management command — one source of truth. Use to "
            "answer 'do we know what agents we have and whether they still work?' before "
            "answering a customer question."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["scan", "summary"],
                    "description": (
                        "scan → full report (all findings + suppressed). "
                        "summary → totals only (agent_map_entries, active_findings, suppressed_findings, has_active_failures)."
                    ),
                },
                "recent_window_days": {
                    "type": "integer",
                    "description": "Days back to check recent-execution invariant (default 30).",
                },
                "invariant": {
                    "type": "string",
                    "enum": ["all", "agent_map_to_db", "exposure_completeness", "recent_execution"],
                    "description": "Filter findings to one invariant. Default 'all'.",
                },
            },
            "required": ["action"],
        },
    },
]

# ── Startup validation: every tool must have name, description, parameters ──
for _i, _tool in enumerate(PA_TOOL_SCHEMAS):
    for _field in ('name', 'description', 'parameters'):
        assert _field in _tool, (
            f"PA_TOOL_SCHEMAS[{_i}] missing '{_field}'. "
            f"Keys present: {list(_tool.keys())}. "
            f"Did you use Chat Completions format (nested 'function') instead of Responses API (flat)?"
        )


# ── Tool-to-Enrichment Mapping ──────────────────────────────────────────────
# Maps tool names back to enrichment services for the intelligence pipeline.
# Migrated from UnifiedPAEntrypoint.INTENT_ENRICHMENT_MAP.

TOOL_ENRICHMENT_MAP = {
    'boardroom_tool': ['intelligence_enricher', 'strategic_memory'],
    'initiative_tool': ['intelligence_enricher', 'strategic_memory'],
    'content_review_tool': ['blog_performance', 'domain_context', 'spider_trends', 'strategic_memory', 'proactive_intelligence'],
    'dream_tool': [],
    'brainstorm_tool': ['intelligence_enricher', 'strategic_memory'],
    'generate_blog_tool': ['blog_performance', 'domain_context', 'spider_trends'],
    'stock_intelligence_tool': ['domain_context', 'spider_trends', 'proactive_intelligence'],
    'legislation_tool': ['domain_context', 'spider_trends'],
    'sports_betting_tool': ['spider_trends', 'domain_context'],
    'opportunity_manager_tool': ['spider_trends', 'domain_context', 'advisor', 'proactive_intelligence'],
    'task_manager_tool': ['intelligence_enricher'],
    'pipeline_orchestrator_tool': ['intelligence_enricher'],
    'revenue_tracker_tool': ['intelligence_enricher', 'proactive_intelligence'],
    'ml_analysis': ['spider_trends', 'domain_context'],
    # predictions_tool removed (Session 1062) — deprecated AgentPrediction model
    'gates_tool': ['intelligence_enricher'],
    'pilots_tool': ['intelligence_enricher'],
    'human_decisions_tool': ['intelligence_enricher', 'strategic_memory'],
    'reasoning_engine_tool': ['intelligence_enricher', 'advisor', 'strategic_memory'],
    'web_search': ['domain_context'],
    'research_and_create_tool': ['domain_context', 'spider_trends'],
    'spider_data_tool': ['domain_context'],
    'execution_history_tool': ['intelligence_enricher', 'strategic_memory', 'platform_briefing'],
    'learning_patterns_tool': ['spider_trends'],
    'feedback_tool': [],
    'recent_activity_tool': [],
    'system_health_tool': [],
    'error_summary_tool': [],
    'surgical_moves_status_tool': [],
    'get_body_vitals': [],
    'check_resource_budget': [],
    'cost_telemetry_tool': ['intelligence_enricher', 'platform_briefing'],
    'get_system_alerts': [],
    'status_snapshot_tool': ['intelligence_enricher', 'proactive_intelligence', 'platform_briefing'],
    'agent_introspection_tool': [],
    'scheduled_tasks_tool': [],
    'universal_agent_tool': ['intelligence_enricher'],
    'workspace_tool': [],
    'deliverables_tool': ['intelligence_enricher'],
    'run_agent': ['intelligence_enricher'],
    'legal_doc_drafter_agent': ['domain_context'],
    'task_breakdown_tool': [],
    'platform_awareness_tool': [],
    'platform_config_tool': [],
    'paid_interest_status': [],
    'signal_studio_judge_stats': [],
    'db_health_tool': [],
    'studio_tool': ['intelligence_enricher'],
    'persona_tool': ['domain_context', 'spider_trends'],
    # Session 1088: Individual agent schemas
    'image_editing_agent': ['intelligence_enricher'],
    'video_editing_agent': ['intelligence_enricher'],
    'three_d_generation_agent': ['intelligence_enricher'],
    'character_training_agent': ['intelligence_enricher'],
    'competitor_analysis_agent': ['domain_context', 'spider_trends', 'strategic_memory'],
    'customer_research_agent': ['domain_context', 'spider_trends'],
    'brand_strategy_agent': ['domain_context', 'strategic_memory'],
    'content_strategy_agent': ['domain_context', 'spider_trends', 'strategic_memory'],
    'marketing_strategy_agent': ['domain_context', 'spider_trends', 'strategic_memory'],
    'content_writer_agent': ['domain_context', 'spider_trends'],
    'workflow_orchestration_agent': ['intelligence_enricher'],
    'strategic_review': ['domain_context', 'strategic_memory'],
    'create_brand_video': ['intelligence_enricher'],
    'create_project_from_research': ['domain_context', 'spider_trends'],
    'http_smoke_test': [],
    'learning_tool': [],
    'rag_query_tool': [],
    'competitor_comparison_tool': [],
    'workflow_run_tool': [],
    'conversation_tool': ['strategic_memory'],
    'remember_tool': [],
    'ops_tool': ['intelligence_enricher', 'platform_briefing'],
    'agent_control_tool': [],
    'active_priority_tool': [],
    'governor_tool': [],
    'autopilot_tool': [],
    'ops_digest_tool': ['platform_briefing'],
    'work_tool': ['intelligence_enricher', 'strategic_memory'],
    'content_tool': ['blog_performance', 'domain_context', 'spider_trends', 'strategic_memory', 'proactive_intelligence'],
    'governance_tool': ['intelligence_enricher', 'strategic_memory'],
    'intelligence_tool': ['domain_context', 'spider_trends', 'proactive_intelligence'],
    # Session 1035-W2: 11 new gateway tools
    'proactive_tool': ['proactive_intelligence'],
    'distribution_tool': [],
    'calendar_tool': [],
    'experiment_tool': [],
    'podcast_tool': [],
    'campaign_tool': [],
    'audit_tool': [],
    'conceptforge_tool': [],
    'profile_tool': [],
    'self_awareness_tool': [],
    'ats_tool': [],
    'code_job_tool': [],
    # Session 1035-Audit: 4 new tools
    'spider_status_tool': [],
    'spider_data_aggregation_tool': [],
    'agent_memory_tool': [],
    'heartbeat_history_tool': [],
    'infra_health_tool': [],
    'kb_tool': [],
    'search_docs': [],
    'session_tool': [],
}

# Reverse map: tool name -> canonical intent name for enrichment pipeline
TOOL_TO_INTENT_MAP = {
    'boardroom_tool': 'boardroom',
    'initiative_tool': 'initiatives',
    'content_review_tool': 'content_review',
    'dream_tool': 'dreams',
    'brainstorm_tool': 'boardroom',
    'generate_blog_tool': 'content_review',
    'stock_intelligence_tool': 'stock_intelligence',
    'legislation_tool': 'legislation',
    'sports_betting_tool': 'predictions',
    'opportunity_manager_tool': 'opportunities',
    'task_manager_tool': 'opportunities',
    'pipeline_orchestrator_tool': 'initiatives',
    'revenue_tracker_tool': 'opportunities',
    'ml_analysis': 'predictions',
    # predictions_tool removed (Session 1062)
    'gates_tool': 'gates',
    'pilots_tool': 'pilots',
    'human_decisions_tool': 'boardroom',
    'reasoning_engine_tool': 'reasoning',
    'web_search': 'web_search',
    'research_and_create_tool': 'research_and_create',
    'spider_data_tool': 'spider_data',
    'execution_history_tool': 'execution_history',
    'learning_patterns_tool': 'learning_patterns',
    'feedback_tool': 'user_feedback',
    'recent_activity_tool': 'recent_activity',
    'system_health_tool': 'system_health_check',
    'error_summary_tool': 'error_summary',
    'surgical_moves_status_tool': 'surgical_moves_status',
    'get_body_vitals': 'system_health',
    'check_resource_budget': 'system_health',
    'cost_telemetry_tool': 'system_health',
    'get_system_alerts': 'system_health',
    'status_snapshot_tool': 'system_overview',
    'agent_introspection_tool': 'agent_introspection',
    'scheduled_tasks_tool': 'scheduled_tasks',
    'universal_agent_tool': 'agent_execution',
    'workspace_tool': 'workspace',
    'deliverables_tool': 'deliverables',
    'run_agent': 'agent_execution',
    'legal_doc_drafter_agent': 'legal_assistance',
    'task_breakdown_tool': 'task_breakdown',
    'platform_awareness_tool': 'platform_awareness',
    'platform_config_tool': 'system_health',
    'paid_interest_status': 'system_health',
    'signal_studio_judge_stats': 'system_health',
    'db_health_tool': 'system_health',
    'studio_tool': 'studio',
    'persona_tool': 'agent_execution',
    # Session 1088: Individual agent schemas
    'image_editing_agent': 'agent_execution',
    'video_editing_agent': 'agent_execution',
    'three_d_generation_agent': 'agent_execution',
    'character_training_agent': 'agent_execution',
    'competitor_analysis_agent': 'agent_execution',
    'customer_research_agent': 'agent_execution',
    'brand_strategy_agent': 'agent_execution',
    'content_strategy_agent': 'agent_execution',
    'marketing_strategy_agent': 'agent_execution',
    'content_writer_agent': 'agent_execution',
    'workflow_orchestration_agent': 'agent_execution',
    'strategic_review': 'agent_execution',
    'create_brand_video': 'agent_execution',
    'create_project_from_research': 'agent_execution',
    'http_smoke_test': 'verification',
    'learning_tool': 'system_health',
    'rag_query_tool': 'rag',
    'competitor_comparison_tool': 'rag',
    'workflow_run_tool': 'rag',
    'conversation_tool': 'memory_recall',
    'remember_tool': 'memory',
    'ops_tool': 'system_overview',
    'agent_control_tool': 'system_overview',
    'active_priority_tool': 'system_overview',
    'governor_tool': 'system_overview',
    'autopilot_tool': 'system_overview',
    'ops_digest_tool': 'system_overview',
    'work_tool': 'initiatives',
    'content_tool': 'content_review',
    'governance_tool': 'boardroom',
    'intelligence_tool': 'stock_intelligence',
    'repo_tool': 'codebase',
    'analytics_tool': 'analytics',
    'discord_tool': 'discord',
    'mobile_tool': 'mobile',
    # Session 1035-W2: 11 new gateway tools
    'proactive_tool': 'system_overview',
    'distribution_tool': 'content_review',
    'calendar_tool': 'content_review',
    'experiment_tool': 'analytics',
    'podcast_tool': 'content_review',
    'campaign_tool': 'content_review',
    'audit_tool': 'system_overview',
    'conceptforge_tool': 'content_review',
    'profile_tool': 'user_profile',
    'self_awareness_tool': 'system_overview',
    'ats_tool': 'opportunities',
    'code_job_tool': 'codebase',
    'newsletter_tool': 'content_review',
    # Session 1035-Audit: 4 new tools
    'spider_status_tool': 'system_overview',
    'spider_data_aggregation_tool': 'system_overview',
    'agent_memory_tool': 'agent_introspection',
    'heartbeat_history_tool': 'system_health',
    'infra_health_tool': 'system_health',
    'kb_tool': 'knowledge_base',
    'search_docs': 'knowledge_base',
    'bpaas_tool': 'workspace',
    'claude_code_tool': 'codebase',
    'session_tool': 'session_management',
}


# ── Schema version — changes when tools are added/removed ────────────────────
# Used by _run_agentic_loop to detect stale cached schemas and force reload.

def _compute_schema_version() -> str:
    """Hash of all tool names AND parameter shapes.

    Session 1091: Previously hashed only tool names, which meant adding,
    removing, or changing parameters on an existing tool (e.g. adding the
    new ``orphans`` filter to ``deliverable_tool``) did not bump the
    version, so live workers kept serving stale schemas to GPT-5.2 until
    something forced a process restart. Now includes a deterministic JSON
    dump of each tool's parameters so any schema change triggers reload.
    """
    import json as _json
    parts = []
    for s in PA_TOOL_SCHEMAS:
        if not isinstance(s, dict):
            continue
        name = s.get('name', '')
        params = s.get('parameters', {})
        try:
            params_dump = _json.dumps(params, sort_keys=True, default=str)
        except (TypeError, ValueError):
            params_dump = repr(params)
        parts.append(f"{name}::{params_dump}")
    parts.sort()
    return hashlib.md5('|'.join(parts).encode()).hexdigest()[:12]


SCHEMA_VERSION = _compute_schema_version()
