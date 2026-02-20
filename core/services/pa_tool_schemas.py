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
"""

# ── Tool Schemas for OpenAI Responses API function calling ──────────────────

PA_TOOL_SCHEMAS = [
    # ── Boardroom ───────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "boardroom_tool",
        "description": (
            "Access the boardroom: pending attention items, draft decisions, "
            "and approval/rejection actions. Use when the user asks about what "
            "needs their attention, pending approvals, decisions to make, or "
            "wants to approve/ignore/promote/reject items."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "stats", "list_attention", "list_decisions",
                        "approve_attention", "ignore_attention",
                        "promote_decision", "reject_decision",
                        "get_triage_batch",
                    ],
                    "description": "Boardroom action to perform",
                },
                "id": {"type": "string", "description": "UUID of item to act on (for approve/ignore/promote/reject)"},
                "urgency": {"type": "string", "enum": ["critical", "high", "medium", "low"], "description": "Filter by urgency level"},
                "item_type": {"type": "string", "description": "Filter attention items by type"},
                "decision_type": {"type": "string", "description": "Filter decisions by type"},
                "limit": {"type": "integer", "description": "Max items to return (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Initiative Pipeline ─────────────────────────────────────────────────
    {
        "type": "function",
        "name": "initiative_tool",
        "description": (
            "Access the initiative pipeline: list projects, get stats, view "
            "details, and check action items. Use when the user asks about "
            "initiatives, projects, pipeline status, action items, or project progress."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "stats", "details", "action_items", "stage_document"],
                    "description": "Initiative action to perform. Use 'stage_document' to read the full content of a stage document.",
                },
                "id": {"type": "string", "description": "UUID of initiative for details or stage_document"},
                "document_id": {"type": "string", "description": "UUID of document (for stage_document action)"},
                "status": {"type": "string", "description": "Filter by status (ACTIVE, PAUSED, COMPLETED, ARCHIVED, all)"},
                "stage": {"type": "string", "description": "Filter by pipeline stage (1-5). For stage_document: which stage to fetch."},
                "purpose": {"type": "string", "description": "Filter by purpose"},
                "program": {"type": "string", "description": "Filter by program"},
                "owner": {"type": "string", "description": "Filter by owner ('me', 'unowned', or agent name)"},
                "limit": {"type": "integer", "description": "Max items to return (default 50)"},
            },
            "required": ["action"],
        },
    },

    # ── Content Review ──────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "content_review_tool",
        "description": (
            "Review content deliverables and blogs: list items awaiting review, "
            "search by title, get recent content, approve, reject, or get details. "
            "Use when the user asks about content, blogs, deliverables, articles, "
            "or content awaiting review. Set type='blog' to query blogs specifically."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "recent", "details", "approve", "reject", "stats"],
                    "description": "Content review action. 'search' finds blogs by title keyword.",
                },
                "id": {"type": "string", "description": "UUID of deliverable or blog"},
                "query": {"type": "string", "description": "Title search term for 'search' action"},
                "type": {"type": "string", "description": "Content type filter. Use 'blog' for blog posts."},
                "status": {"type": "string", "description": "Filter by status (draft, pending_review, approved, published)"},
                "days": {"type": "integer", "description": "Lookback period in days for 'recent' action (default 30)"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

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
                    "enum": ["list_top", "details", "approve", "dismiss", "stats"],
                    "description": "Dream action to perform",
                },
                "id": {"type": "string", "description": "UUID of dream"},
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
            "Search brainstorm sessions: discussion panels, multi-agent debates, "
            "and collaborative insights. Use when the user asks about brainstorms, "
            "discussions, panels, debates, or collaborative agent sessions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "details", "stats"],
                    "description": "Brainstorm action",
                },
                "id": {"type": "string", "description": "UUID of brainstorm session"},
                "query": {"type": "string", "description": "Search query for brainstorm content"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Blog Generation ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "generate_blog_tool",
        "description": (
            "Generate a blog post via the deliberation pipeline. Use when the "
            "user explicitly asks to write, generate, or create a blog post or article."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Blog topic to write about"},
                "style": {"type": "string", "description": "Writing style or tone"},
            },
            "required": ["topic"],
        },
    },

    # ── Stock Intelligence ──────────────────────────────────────────────────
    {
        "type": "function",
        "name": "stock_intelligence_tool",
        "description": (
            "Access market intelligence: stock dashboards, market briefs, alerts, "
            "prediction accuracy, and SEC filings. Use when the user asks about "
            "stocks, markets, trading, investments, SEC filings, or market predictions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["overview", "briefs", "alerts", "predictions", "sec_filings"],
                    "description": "Stock intelligence action",
                },
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Legislation ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "legislation_tool",
        "description": (
            "Track congressional bills and legislation. Use when the user asks "
            "about bills, legislation, congress, laws, or government policy."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "details", "stats"],
                    "description": "Legislation action",
                },
                "query": {"type": "string", "description": "Search query for bills"},
                "id": {"type": "string", "description": "Bill ID for details"},
                "status": {"type": "string", "description": "Filter by bill status"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Sports Betting ──────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "sports_betting_tool",
        "description": (
            "Access sports betting intelligence: predictions, model accuracy, "
            "upcoming games, and betting analytics. Use when the user asks about "
            "sports, betting, predictions, games, odds, or ML model performance."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["overview", "predictions", "upcoming", "accuracy", "history"],
                    "description": "Sports betting action",
                },
                "sport": {"type": "string", "description": "Sport type filter (nba, nfl, mlb, nhl)"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Opportunity Manager ─────────────────────────────────────────────────
    {
        "type": "function",
        "name": "opportunity_manager_tool",
        "description": (
            "Manage opportunities: list, view details, get stats, or update status. "
            "Use when the user asks about opportunities, job listings, income "
            "opportunities, or wants to track/update an opportunity."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "get", "stats", "update_status"],
                    "description": "Opportunity action",
                },
                "id": {"type": "string", "description": "UUID of opportunity"},
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
                    "enum": ["list", "stats"],
                    "description": "Task action",
                },
                "status": {"type": "string", "description": "Filter by task status"},
                "priority": {"type": "string", "description": "Filter by priority"},
                "limit": {"type": "integer", "description": "Max items (default 20)"},
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
            "Track revenue metrics and income progress. Use when the user asks "
            "about revenue, earnings, income, or financial progress."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["summary", "breakdown", "history"],
                    "description": "Revenue action",
                },
                "period": {"type": "string", "description": "Time period (week, month, quarter, year)"},
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
                    "enum": ["summary", "model_performance", "feature_importance"],
                    "description": "ML analysis action",
                },
                "model_type": {"type": "string", "description": "Specific model to analyze"},
            },
            "required": ["action"],
        },
    },

    # ── Predictions ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "predictions_tool",
        "description": (
            "Access ML predictions: list recent predictions, accuracy stats, "
            "model performance. Use when the user asks about predictions, "
            "forecasts, or prediction accuracy."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "stats", "details"],
                    "description": "Predictions action",
                },
                "id": {"type": "string", "description": "UUID of prediction"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

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
                    "enum": ["list", "stats", "details"],
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
                    "enum": ["list", "stats", "details"],
                    "description": "Pilots action",
                },
                "id": {"type": "string", "description": "UUID of pilot"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Human Decisions ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "human_decisions_tool",
        "description": (
            "Access items requiring human decision: pending approvals, reviews, "
            "manual actions. Use when the user asks about pending decisions, "
            "what needs approval, or human-in-the-loop items."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "stats", "decide"],
                    "description": "Human decisions action",
                },
                "id": {"type": "string", "description": "UUID of decision item"},
                "decision": {"type": "string", "description": "Decision value (approve/reject)"},
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

    # ── Spider Data ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "spider_data_tool",
        "description": (
            "Access data collected by spiders: scraped content, crawl results, "
            "data feeds. Use when the user asks about spider data, crawled content, "
            "data sources, or specific spider outputs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "stats", "by_spider"],
                    "description": "Spider data action",
                },
                "query": {"type": "string", "description": "Search query for spider data"},
                "spider_name": {"type": "string", "description": "Filter by specific spider"},
                "data_type": {"type": "string", "description": "Filter by data type"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Execution History ───────────────────────────────────────────────────
    {
        "type": "function",
        "name": "execution_history_tool",
        "description": (
            "View agent execution history: recent runs, success/failure rates, "
            "execution details. Use when the user asks about what agents have done, "
            "execution logs, agent activity, or run history."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["recent", "by_agent", "stats", "details"],
                    "description": "Execution history action",
                },
                "agent_name": {"type": "string", "description": "Filter by agent name"},
                "id": {"type": "string", "description": "UUID of execution for details"},
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
                    "enum": ["summary", "by_agent", "trends"],
                    "description": "Learning patterns action",
                },
                "agent_name": {"type": "string", "description": "Filter by agent"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
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
                    "enum": ["submit", "list", "stats"],
                    "description": "Feedback action",
                },
                "target_type": {"type": "string", "description": "What the feedback is about"},
                "target_id": {"type": "string", "description": "UUID of the item being rated"},
                "rating": {"type": "integer", "description": "Rating (1-5)"},
                "comment": {"type": "string", "description": "Feedback comment"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
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

    # ── System Health ───────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "system_health_tool",
        "description": (
            "Check platform system health: service status, database connectivity, "
            "Redis, Celery workers, body system scores. Use when the user asks about "
            "system health, is everything working, platform status, or service health."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "verbose": {"type": "boolean", "description": "Include detailed breakdown (default false)"},
            },
        },
    },

    # ── Error Summary ───────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "error_summary_tool",
        "description": (
            "Get a summary of recent errors and failures across the platform. "
            "Use when the user asks about errors, failures, what went wrong, "
            "or error logs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hours": {"type": "integer", "description": "Look back N hours (default 24)"},
                "limit": {"type": "integer", "description": "Max errors (default 20)"},
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
                    "enum": ["list", "stats", "details", "capabilities"],
                    "description": "Introspection action: list/stats for overview, details/capabilities for a specific agent",
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
            "View scheduled Celery tasks: cron schedules, beat entries, "
            "next run times. Use when the user asks about scheduled tasks, "
            "cron jobs, what runs automatically, or Celery beat."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "details"],
                    "description": "Scheduled tasks action",
                },
                "limit": {"type": "integer", "description": "Max items (default 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Universal Agent ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "universal_agent_tool",
        "description": (
            "Route a task to the best-fit agent automatically. Use when the "
            "user wants a specific agent task done but you're not sure which "
            "specialized tool to use."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description to route to best agent"},
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
            "Manage workspace items: notes, bookmarks, saved items. "
            "Use when the user asks about their workspace, saved items, or notes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "create", "delete"],
                    "description": "Workspace action",
                },
                "content": {"type": "string", "description": "Content for new item"},
                "id": {"type": "string", "description": "UUID of item to act on"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
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
            "generate images, create videos, edit images/videos, generate audio, "
            "create 3D models, train characters, do competitor analysis, customer "
            "research, brand strategy, content strategy, marketing strategy, "
            "content writing, or workflow orchestration."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "agent_name": {
                    "type": "string",
                    "enum": [
                        "image_generation_agent", "image_editing_agent",
                        "video_generation_agent", "video_editing_agent",
                        "audio_generation_agent", "three_d_generation_agent",
                        "character_training_agent", "talking_character_agent",
                        "competitor_analysis_agent", "customer_research_agent",
                        "brand_strategy_agent", "content_strategy_agent",
                        "marketing_strategy_agent", "content_writer_agent",
                        "workflow_orchestration_agent", "coleadership_agent",
                        "strategic_review",
                    ],
                    "description": "Which agent to run",
                },
                "task": {"type": "string", "description": "Task description for the agent"},
                "context": {"type": "object", "description": "Additional context"},
            },
            "required": ["agent_name", "task"],
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
]


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
    'predictions_tool': ['spider_trends', 'domain_context'],
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
    'run_agent': ['intelligence_enricher'],
    'legal_doc_drafter_agent': ['domain_context'],
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
    'predictions_tool': 'predictions',
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
    'workspace_tool': 'general',
    'run_agent': 'agent_execution',
    'legal_doc_drafter_agent': 'legal_assistance',
}
