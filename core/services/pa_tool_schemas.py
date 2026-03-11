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

    # ── Brainstorm Search ───────────────────────────────────────────────────
    {
        "type": "function",
        "name": "brainstorm_tool",
        "description": (
            "Search and list brainstorm sessions: discussion panels, multi-agent debates, "
            "and collaborative insights. Use 'list' for bulk paginated export, 'search' "
            "for keyword search, 'details' for a single session, 'stats' for activity stats."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "recent", "details", "by_category", "stats", "create"],
                    "description": "Brainstorm action: list, search, recent summaries, details of conversation, by_category, stats, or create new brainstorm",
                },
                "id": {"type": "string", "description": "UUID of brainstorm session (alias: conversation_id)"},
                "conversation_id": {"type": "string", "description": "UUID of brainstorm conversation for details action"},
                "query": {"type": "string", "description": "Search query for brainstorm content"},
                "category": {"type": "string", "description": "Category filter for by_category action"},
                "topic": {"type": "string", "description": "Topic/prompt for create action — kicks off a new brainstorm discussion"},
                "limit": {"type": "integer", "description": "Max items (default 50 for list, 10 for search)"},
                "offset": {"type": "integer", "description": "Pagination offset for list action (default 0)"},
                "days": {"type": "integer", "description": "Days back to search (default 30)"},
                "days_back": {"type": "integer", "description": "Alias for days"},
                "type": {"type": "string", "description": "Filter by type: 'discussion' or 'panel'"},
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
            "opportunities, or wants to track/update an opportunity."
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
            "related to opportunities."
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
                "opportunity_id": {"type": "string", "description": "Link to opportunity UUID (for create)"},
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
            "Invoke the reasoning engine for complex analysis: multi-step reasoning, "
            "strategic thinking, trade-off analysis. Use when the user asks for "
            "deep analysis, strategic advice, or complex reasoning."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The question or topic to reason about"},
                "reasoning_type": {"type": "string", "description": "Type of reasoning (strategic, analytical, creative)"},
            },
            "required": ["query"],
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
            "Use action=detail with id or agent_name to get full output_data."
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
            "View learning patterns: feedback loops, improvement trends, "
            "agent learning metrics. Use when the user asks about learning, "
            "patterns, feedback, improvement, or agent self-improvement."
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
                "limit": {"type": "integer", "description": "Max items (default 10, for list)"},
            },
            "required": ["action"],
        },
    },

    # ── Recent Activity (Live Telemetry) ────────────────────────────────────
    {
        "type": "function",
        "name": "recent_activity_tool",
        "description": (
            "View recent platform activity: latest agent executions, Celery tasks, "
            "spider runs, and system events. Use when the user asks 'what's happening', "
            "'what just ran', 'recent activity', or 'what's going on'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max items (default 20)"},
                "minutes": {"type": "integer", "description": "Look back N minutes (default 60)"},
            },
        },
    },

    # ── Surgical Moves Status ───────────────────────────────────────────────
    {
        "type": "function",
        "name": "surgical_moves_status_tool",
        "description": (
            "Check status of deliberation pipeline and content verification. "
            "Use when the user asks about deliberation status, surgical moves, "
            "or content pipeline verification."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "verbose": {"type": "boolean", "description": "Include detailed breakdown"},
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

    # ── Workspace ───────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "workspace_tool",
        "description": (
            "Manage development workspaces: list, check status, or create new ones. "
            "Use when the user asks about their workspaces, project worktrees, "
            "or wants to create a new workspace to organize work."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "status", "create", "delete"],
                    "description": "Workspace action. Use 'create' to make a new workspace, 'delete' to remove a sandbox workspace by id.",
                },
                "id": {"type": "string", "description": "UUID of workspace to act on"},
                "name": {"type": "string", "description": "Name for new workspace (for create action)"},
                "description": {"type": "string", "description": "Description/notes for the workspace (for create action)"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
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
            "Run any of 72 specialized agents across 12 domains: "
            "media creation/editing, research & analysis, strategy & content, "
            "executive & orchestration, stock & markets, sports & betting, "
            "blockchain audit, narrative drift, content studio, podcast, "
            "training & security, and system intelligence."
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
                        "market_intelligence_agent", "platform_audit_agent",
                        "thinking_agent", "decision_enforcer_agent",
                        # ── Strategy & Content ──
                        "brand_identity_agent", "seo_optimizer_agent",
                        "social_media_agent", "editor_agent",
                        "content_audit_agent", "prompt_engineering_agent",
                        "technical_document_agent", "creative_director_agent",
                        # ── Business Research ──
                        "competitor_analysis_agent", "customer_research_agent",
                        "brand_strategy_agent", "content_strategy_agent",
                        "marketing_strategy_agent", "content_writer_agent",
                        # ── Executive & Orchestration ──
                        "cto_agent", "coo_agent",
                        "meeting_coordinator_agent",
                        "campaign_orchestrator_agent",
                        "opportunity_pipeline_agent", "content_executor_agent",
                        "ai_series_workflow_agent",
                        "workflow_orchestration_agent",
                        "system_intelligence_agent",
                        "strategic_review",
                        "create_brand_video", "create_project_from_research",
                        # ── Stock & Markets ──
                        "stock_audit_coordinator", "stock_analyst_agent",
                        "market_movement_monitor_agent",
                        "institutional_watcher_agent",
                        "market_anomaly_detector_agent",
                        "bull_case_agent", "bear_case_agent",
                        "signal_scanner_agent",
                        "market_intelligence_coordinator",
                        # ── Sports & Betting ──
                        "prediction_market_analyst",
                        "game_predictor", "line_movement_analyzer",
                        "sharp_action_detector", "bookmaker_agent",
                        # ── Blockchain Audit ──
                        "blockchain_audit_coordinator",
                        "smart_contract_auditor_agent",
                        "transaction_monitor_agent",
                        "whale_watcher_agent", "exploit_detector_agent",
                        # ── Narrative Drift ──
                        "narrative_drift_coordinator",
                        "narrative_historian_agent",
                        "trend_break_detector_agent",
                        "cultural_impact_agent",
                        # ── Content Studio ──
                        "autonomous_content_studio_coordinator",
                        "topic_miner_agent", "contrarian_agent",
                        "performance_analyst_agent", "voice_critic_agent",
                        "content_diversity_orchestrator",
                        # ── Podcast ──
                        "podcast_coordinator_agent",
                        "debate_advocate_agent", "debate_skeptic_agent",
                        "moderator_agent",
                        # ── Training & Security ──
                        "trained_creation_agent", "memory_isolation_agent", "security_agent",
                    ],
                    "description": (
                        "Which agent to run. 72 agents across 12 domains. "
                        "Media: image/video/audio/3D generation & editing, resolve (DaVinci). "
                        "Research: research, trend analysis, opportunity scoring, thinking. "
                        "Strategy: brand identity, SEO, social media, content audit, prompt engineering. "
                        "Markets: stock analyst, bull/bear case, signal scanner, market anomaly. "
                        "Sports: game predictor, line movement, sharp action, bookmaker. "
                        "Blockchain: smart contract auditor, transaction monitor, whale watcher. "
                        "Narrative: drift coordinator, historian, trend break, cultural impact. "
                        "Studio: topic miner, contrarian, performance analyst, voice critic. "
                        "Podcast: coordinator, debate advocate/skeptic, moderator. "
                        "system_intelligence_agent = platform health reports."
                    ),
                },
                "task": {"type": "string", "description": "Task description for the agent"},
                "context": {"type": "object", "description": "Additional context"},
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
                    "type": "boolean",
                    "description": "Filter routes by auth requirement (for list_routes)",
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
                        "generate_talking_video", "create_talking_video",
                        "job_status", "list_jobs",
                    ],
                    "description": (
                        "generate_image: create an AI image from prompt. "
                        "generate_video: create a video from prompt/image. "
                        "generate_audio: text-to-speech audio. "
                        "generate_talking_video: create a talking-head video from character image + script — requires existing image_url. "
                        "create_talking_video: generate a character image from prompt AND create talking video in one step — use when user has NO existing image. Provide 'prompt' for image description and 'script' for dialogue. "
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
                "context": {
                    "type": "object",
                    "description": "Additional context: content_type, tone, audience, word_count, keywords",
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
                    "description": "Target environment (default: railway_prod)",
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
                        "initiative_list", "initiative_detail", "initiative_create",
                        "initiative_promote", "initiative_update_status",
                        "action_item_list", "action_item_start", "action_item_complete",
                        "action_item_cleanup",
                        "agent_conversations", "workflows",
                    ],
                    "description": (
                        "initiative_list: list initiatives (filters: status, owner, stage). "
                        "initiative_detail: full details of one initiative (by id, human_id, seq_id, or name). "
                        "initiative_create: create a new initiative (name, description). "
                        "initiative_promote: move TRIAGE/ON_HOLD → ACTIVE. "
                        "initiative_update_status: change initiative status (id + status: ACTIVE/TRIAGE/ON_HOLD/COMPLETED/ARCHIVED). Auto-cancels pending action items on COMPLETED/ARCHIVED. "
                        "action_item_list: list action items (filters: status, priority, initiative_id). "
                        "action_item_start: mark an action item as in_progress. "
                        "action_item_complete: mark an action item as completed. "
                        "action_item_cleanup: find/cancel junk action items (dry_run default true). "
                        "agent_conversations: browse multi-agent conversations. "
                        "workflows: recent workflow/orchestration executions."
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
                    "description": "For action_item_cleanup: true to preview, false to execute (default true).",
                },
                "limit": {"type": "integer", "description": "Max results (default 50)."},
                "offset": {"type": "integer", "description": "Skip first N results for pagination."},
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
                        "version", "slo_status", "failure_signatures",
                        "tool_migration_report", "timeout_config_read", "proof_bundle",
                        "noise_metrics", "conversation_metrics",
                        "focus_mode_status", "focus_mode_update",
                        "celery_task_history", "execution_detail", "execution_search",
                    ],
                    "description": (
                        "version: build/deploy metadata (git SHA, branch, Railway deployment, uptime). "
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
                        "Returns list with heartbeat info."
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
                    "description": "For celery_task_history: filter by task name (substring match, e.g. 'cleanup_stale'). Omit for all tasks.",
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
                    "enum": ["status", "history", "run", "config", "dry_run_report", "drift_scan", "tuning_report", "budget_report", "roi_report", "scheduler_report", "portfolio_report", "backfill_impacts", "attribution_debt_report", "experiment_report", "experiment_create", "experiment_start", "decision_ledger_report", "timeout_ladder_report", "deliberation_pipeline_report", "backfill_failure_reasons", "backlog_report", "goal_report", "goal_set_weights", "attribution_report", "policy_conflict_report", "release_report", "release_freeze", "release_unfreeze", "revenue_pipeline_report", "prospecting_queue", "lead_source_report", "outreach_inbox", "outreach_approve", "outreach_reject", "outreach_metrics_report", "close_pack_generate", "close_pack_inbox", "close_pack_approve", "close_pack_metrics_report", "engagement_inbox", "engagement_classify", "engagement_draft_reply", "engagement_approve_reply", "engagement_disqualify", "engagement_metrics_report", "meeting_create", "meeting_inbox", "meeting_brief", "meeting_recap", "meeting_metrics_report", "governance_status", "governance_set_mode", "governance_kill_switch", "governance_deactivate_switch", "governance_throttle_report", "governance_audit", "revenue_full_pipeline", "revenue_funnel", "revenue_forecast", "knowledge_health", "knowledge_citation_report", "knowledge_source_report", "knowledge_staleness_report", "close_pack_followup_queue", "close_pack_risk_report", "close_pack_velocity", "engagement_sla_queue", "engagement_meeting_suggestions", "engagement_conversion_report", "growth_candidates", "growth_schedule", "growth_channel_report", "growth_funnel", "capacity_forecast", "capacity_bottleneck_report", "capacity_throttle_plan", "capacity_budget_envelope", "security_permission_drift", "security_abuse_queue", "security_containment_plan", "security_secrets_scan", "compliance_pii_scan", "compliance_retention_report", "compliance_access_audit", "compliance_report", "integrity_quality_report", "integrity_null_spike_scan", "integrity_duplicate_report", "integrity_reliability_scores", "value_events_report", "value_outcome_rates", "value_usage_gaps", "value_realization_summary"],
                    "description": (
                        "status: current config, last cycle timestamp, and pending actions. "
                        "history: recent autopilot actions (blocks, attention items, dry runs). "
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
                    "description": "For 'run' action: evaluate policies but don't actually block/unblock (default false).",
                },
                "limit": {
                    "type": "integer",
                    "description": "For 'history': max entries to return (default 20, max 100).",
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
                        "inbox",
                        "attention_list", "attention_detail", "attention_approve", "attention_ignore", "attention_lookup",
                        "decision_list", "decision_promote", "decision_reject",
                        "decisions_list", "decisions_stats", "decision_create", "decision_decide",
                        "triage_batch",
                        "failure_signatures", "remediation_tasks",
                    ],
                    "description": (
                        "inbox: combined overview with counts + top items. "
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
                        "signal_clusters: signal aggregation patterns. "
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
                "query": {"type": "string", "description": "Search query for search/legislation_search/legislation_summary"},
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
            "Use content_approve/content_reject to publish or archive content. "
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
                        "content_approve", "content_reject",
                        "generate_blog", "bulk_archive", "bulk_archive_published", "run_cleanup",
                        "deliverable_list", "deliverable_detail",
                        "deliverable_search", "deliverable_save",
                        "deliverable_create", "deliverable_stats",
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
                        "generate_blog: create a new blog post via deliberation pipeline. "
                        "bulk_archive: archive multiple deliverables by filter (dry_run preview by default). "
                        "bulk_archive_published: admin-only — archive published deliverables by category (requires categories + created_before + confirm). "
                        "run_cleanup: trigger cleanup_stale_content Celery task (async, returns task_id). "
                        "deliverable_list: browse deliverables library (supports status/type/category/date filters). "
                        "deliverable_detail: full content of a deliverable. "
                        "deliverable_search: search deliverables by title. "
                        "deliverable_save: bookmark a deliverable. "
                        "deliverable_create: create a new deliverable. "
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
                "statuses": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive: list of statuses to target (default: ['ready', 'draft']). Cannot include published/archived."},
                "categories": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive_published: required list of categories to target (e.g. ['initiative_completion', 'PA Created'])."},
                "confirm": {"type": "boolean", "description": "For bulk_archive_published: must be true when dry_run=false to actually execute."},
                "types": {"type": "array", "items": {"type": "string"}, "description": "For bulk_archive_published: optional deliverable_type filter. 'blog' is blocked."},
                "created_before": {"type": "string", "description": "ISO-8601 datetime. Only items created before this date (e.g. '2026-02-28T00:00:00Z')."},
                "created_after": {"type": "string", "description": "ISO-8601 datetime. Only items created after this date."},
                "dry_run": {"type": "boolean", "description": "For bulk_archive: preview without executing (default: true). Set false to actually archive."},
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
            "Cannot modify files — read-only access only."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["tree", "read_file", "search", "git_info"],
                    "description": "tree: list directory contents. read_file: read file contents. search: grep/search code. git_info: branch, recent commits, status.",
                },
                "path": {"type": "string", "description": "Relative path from project root (e.g. 'core/agents/', 'mobile/src/screens/')"},
                "depth": {"type": "integer", "description": "Directory depth for tree action (default 2, max 4)"},
                "query": {"type": "string", "description": "Search query/regex for search action"},
                "start_line": {"type": "integer", "description": "Line number to start reading from (0-based, default 0). Use with max_lines to read specific sections."},
                "max_lines": {"type": "integer", "description": "Max lines to return for read_file (default 200, max 500)"},
                "file_type": {"type": "string", "description": "File extension filter for search (e.g. 'py', 'tsx', 'ts')"},
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
                        "recent_failures", "queue_lengths", "trigger_task", "help",
                    ],
                    "description": (
                        "beat_schedule: list all periodic tasks with intervals and last run. "
                        "task_status: check a specific Celery task by ID. "
                        "worker_health: active workers, queues, concurrency. "
                        "recent_failures: failed tasks with error messages. "
                        "queue_lengths: current depth of all queues. "
                        "trigger_task: manually dispatch an allowlisted Celery task (use task_name param). "
                        "help: list all actions."
                    ),
                },
                "task_id": {
                    "type": "string",
                    "description": "Celery task ID (for task_status action)",
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
                        "list: per-spider stats (items_24h, items_7d, age_hours, active/stale). "
                        "history: item history for a specific spider. "
                        "detail: fetch full raw_data/processed_data for a SpiderData item by ID. "
                        "search: search spider data by query, data_type, or spider_name."
                    ),
                },
                "spider_name": {"type": "string", "description": "Spider name filter (for history, list, or search)"},
                "item_id": {"type": "string", "description": "SpiderData UUID (for detail action)"},
                "query": {"type": "string", "description": "Text search in embedding_text/source_url (for search action)"},
                "data_type": {"type": "string", "description": "Filter by data_type (for search action)"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
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
                    "enum": ["stats", "documents", "chunks", "search_embeddings"],
                    "description": (
                        "stats: overall KB metrics (doc count, embedding counts by type). "
                        "documents: list documents with chunk counts. "
                        "chunks: view chunks for a specific document. "
                        "search_embeddings: text search across unified embeddings."
                    ),
                },
                "document_id": {"type": "string", "description": "Document UUID (for chunks action)"},
                "query": {"type": "string", "description": "Search term for documents or embeddings"},
                "content_type": {"type": "string", "description": "Filter unified embeddings by content_type (e.g. agent_knowledge, spider_data, document_chunk)"},
                "limit": {"type": "integer", "description": "Max results (default 20, max 50)"},
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
    'agent_memory_tool': [],
    'heartbeat_history_tool': [],
    'infra_health_tool': [],
    'kb_tool': [],
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
    # Session 1035-Audit: 4 new tools
    'spider_status_tool': 'system_overview',
    'agent_memory_tool': 'agent_introspection',
    'heartbeat_history_tool': 'system_health',
    'infra_health_tool': 'system_health',
    'kb_tool': 'knowledge_base',
}


# ── Schema version — changes when tools are added/removed ────────────────────
# Used by _run_agentic_loop to detect stale cached schemas and force reload.

def _compute_schema_version() -> str:
    """Hash of all tool names — changes when any tool is added or removed."""
    names = sorted(s.get('name', '') for s in PA_TOOL_SCHEMAS if isinstance(s, dict))
    return hashlib.md5('|'.join(names).encode()).hexdigest()[:12]


SCHEMA_VERSION = _compute_schema_version()
