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
                        "list_unclassified", "classify_suggest",
                        "classify_apply", "classify_apply_batch",
                    ],
                    "description": "Boardroom action to perform",
                },
                "id": {"type": "string", "description": "UUID of item to act on (for approve/ignore/promote/reject)"},
                "artifact_id": {"type": "string", "description": "UUID of artifact (for classify_suggest/classify_apply)"},
                "classification": {"type": "object", "description": "Classification fields for classify_apply: what_is_this, who_is_it_for, data_allowed, phase_approved"},
                "items": {"type": "array", "description": "For classify_apply_batch: list of {artifact_id, classification} objects", "items": {"type": "object"}},
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
                    "enum": ["list", "stats", "details", "action_items", "stage_document", "promote", "start_action_item", "complete_action_item"],
                    "description": "Initiative action to perform. Use 'stage_document' to read the full content of a stage document. Use 'promote' to move a TRIAGE or ON_HOLD initiative to ACTIVE. Use 'start_action_item' or 'complete_action_item' with an item id.",
                },
                "id": {"type": "string", "description": "Initiative identifier: human ID (e.g., INIT-000012), seq number (e.g., 12), or UUID"},
                "name": {"type": "string", "description": "Search initiative by name (partial match)"},
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
            "Search and list brainstorm sessions: discussion panels, multi-agent debates, "
            "and collaborative insights. Use 'list' for bulk paginated export, 'search' "
            "for keyword search, 'details' for a single session, 'stats' for activity stats."
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
                "limit": {"type": "integer", "description": "Max items (default 50 for list, 10 for search)"},
                "offset": {"type": "integer", "description": "Pagination offset for list action (default 0)"},
                "days": {"type": "integer", "description": "Days back to search (default 30)"},
                "type": {"type": "string", "description": "Filter by type: 'discussion' or 'panel'"},
                "status": {"type": "string", "description": "Filter by conversation status"},
                "include_transcript": {"type": "boolean", "description": "Include full message transcript (default false)"},
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
                    "description": (
                        "overview: dashboard summary (latest brief, alert counts, prediction accuracy). "
                        "briefs: recent market intelligence briefs. "
                        "alerts: stock alerts (filterable by ticker). "
                        "predictions: prediction outcomes with accuracy stats (filterable by ticker). "
                        "sec_filings: SEC Edgar filings from spider."
                    ),
                },
                "ticker": {"type": "string", "description": "Stock ticker symbol to filter alerts/predictions (e.g. 'AAPL')"},
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
                    "enum": ["overview", "trending", "search", "status", "summary", "ask"],
                    "description": (
                        "overview: dashboard stats (total bills, top topics, status breakdown). "
                        "trending: most recently active bills. "
                        "search: find bills by keyword (requires query). "
                        "status: status of a specific bill (requires bill_number). "
                        "summary: plain-English explanation of a bill (requires bill_number or query). "
                        "ask: RAG-powered Q&A about legislation (requires query)."
                    ),
                },
                "query": {"type": "string", "description": "Search query or question about legislation"},
                "bill_number": {"type": "string", "description": "Bill number for status/summary (e.g. 'HR 1234')"},
                "limit": {"type": "integer", "description": "Max items (default 10, max 20)"},
            },
            "required": ["action"],
        },
    },

    # ── Sports Betting ──────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "sports_betting_tool",
        "description": (
            "Access sports betting intelligence: predictions, arbitrage, odds, "
            "sharp action, and wager tracking. Use when the user asks about "
            "sports, betting, predictions, games, odds, or ML model performance."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["overview", "predictions", "accuracy", "arbs", "sharp_action", "line_movements", "wagers", "live_odds", "brief"],
                    "description": (
                        "overview: dashboard summary (wager counts, arb opps, recent odds). "
                        "predictions: ML game predictions with confidence. "
                        "accuracy: prediction accuracy stats and win/loss record. "
                        "arbs: active arbitrage opportunities. "
                        "sharp_action: sharp betting signals. "
                        "line_movements: detected line movements. "
                        "wagers: user's placed wagers and results. "
                        "live_odds: current odds from spider network. "
                        "brief: full betting brief from coordinator."
                    ),
                },
                "sport": {"type": "string", "description": "Sport type filter (nba, nfl, mlb, nhl)"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
                "days": {"type": "integer", "description": "Lookback period in days (default 30, used by accuracy action)"},
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
                    "enum": ["stats", "list"],
                    "description": "Revenue action: stats (totals by source/status), list (recent revenue records)",
                },
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
                    "enum": ["summary", "model_performance", "feature_importance"],
                    "description": "ML analysis action",
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
                    "enum": ["recent", "by_agent", "stats", "failures"],
                    "description": "Execution history action: recent (latest runs), by_agent (filter by agent), stats (aggregates), failures (recent errors)",
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
            "Covers failure signatures, tool call failures (with error messages), "
            "Celery task failures, and agent timeout breakdowns by agent name. "
            "Use when the user asks about errors, failures, what went wrong, "
            "timeouts, or error logs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["summary", "detailed"],
                    "description": "summary=counts only, detailed=include individual error messages (default summary)"
                },
                "hours": {"type": "integer", "description": "Look back N hours (default 24, use 72 or 168 for wider view)"},
                "limit": {"type": "integer", "description": "Max items per category (default 20)"},
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
            "List development workspaces and check status. "
            "Use when the user asks about their active workspace or project worktrees."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "status"],
                    "description": "Workspace action",
                },
                "id": {"type": "string", "description": "UUID of workspace to act on"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
            "required": ["action"],
        },
    },

    # ── Deliverables Library ──────────────────────────────────────────────
    {
        "type": "function",
        "name": "deliverables_tool",
        "description": (
            "Full CRUD access to the Deliverables Library. "
            "Supported actions: list, search, detail, save, unsave, stats, create, update, delete, cleanup. "
            "Use 'create' to save new content (scripts, plans, notes, etc.). "
            "Use 'update' to change a deliverable's title, content, type, format, or tags. "
            "Use 'delete' to permanently remove a single deliverable. "
            "Use 'cleanup' to bulk-remove duplicates or orphans (use dry_run=true first to preview). "
            "Use 'list'/'search' to browse (supports offset for pagination), 'detail' to read full content, "
            "'save'/'unsave' to bookmark, 'stats' for aggregate counts by type/category/agent."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "search", "detail", "save", "unsave", "stats", "create", "update", "delete", "cleanup"],
                    "description": "list=browse, search=find by query, detail=full content, save/unsave=bookmark, stats=counts, create=new, update=edit, delete=remove one, cleanup=bulk remove duplicates/orphans.",
                },
                "id": {"type": "string", "description": "UUID of deliverable. For detail/save/unsave/update/delete you can pass EITHER id OR title — title lookup is supported so users don't need to copy UUIDs."},
                "query": {"type": "string", "description": "Search query for title matching"},
                "type": {"type": "string", "description": "Filter by or set deliverable type (document, image, report, analysis, script, plan, etc.)"},
                "category": {"type": "string", "description": "Filter by category (e.g. 'Finance', 'Research', 'PA Created')"},
                "agent": {"type": "string", "description": "Filter by agent_name (e.g. 'StockAnalystAgent', 'ResearchAgent')"},
                "title": {"type": "string", "description": "Title for create or update"},
                "content": {"type": "string", "description": "Full content for create or update"},
                "content_format": {"type": "string", "enum": ["markdown", "text", "html", "json"], "description": "Content format (default: markdown)"},
                "tags": {"type": "string", "description": "Comma-separated tags for update (e.g. 'finance, report, q1')"},
                "saved": {"type": "boolean", "description": "Filter to saved items only"},
                "limit": {"type": "integer", "description": "Max items to return (default 10, max 50)"},
                "offset": {"type": "integer", "description": "Skip first N items for pagination (default 0). Use with limit to page through results."},
                "strategy": {
                    "type": "string",
                    "enum": ["duplicates", "orphans", "low_quality"],
                    "description": "Cleanup strategy: duplicates=keep newest per title, delete rest. orphans=delete deliverables with no user. low_quality=delete items with quality_score < 0.5.",
                },
                "dry_run": {"type": "boolean", "description": "If true, cleanup returns what WOULD be deleted without actually deleting. Always use dry_run=true first."},
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

    # ── Agent Delegation (generic) ──────────────────────────────────────────
    {
        "type": "function",
        "name": "run_agent",
        "description": (
            "Delegate a task to a specialized agent. Use when the user asks to "
            "generate images, create videos, edit videos (trim/effects/speed/concat), "
            "render or color-grade videos via DaVinci Resolve, generate audio, "
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
                        "resolve_agent",
                        "audio_generation_agent", "three_d_generation_agent",
                        "character_training_agent", "talking_character_agent",
                        "competitor_analysis_agent", "customer_research_agent",
                        "brand_strategy_agent", "content_strategy_agent",
                        "marketing_strategy_agent", "content_writer_agent",
                        "workflow_orchestration_agent", "coleadership_agent",
                        "strategic_review",
                        "create_brand_video", "create_project_from_research",
                    ],
                    "description": (
                        "Which agent to run. resolve_agent = DaVinci Resolve rendering & color grading. "
                        "video_editing_agent = ffmpeg trim/effects/speed/concat. "
                        "video_generation_agent = Runway ML text/image-to-video."
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
                        "list_api_dependencies",
                    ],
                    "description": (
                        "get_manifest: full manifest (routes, studios, capabilities). "
                        "list_routes: filter routes by category or auth. "
                        "check_route: verify a specific route exists. "
                        "system_overview: summary counts. "
                        "verify_deploy: run deploy health checks (admin only). "
                        "list_api_dependencies: list API endpoints a route depends on."
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
                        "generate_talking_video",
                        "job_status", "list_jobs",
                    ],
                    "description": (
                        "generate_image: create an AI image from prompt. "
                        "generate_video: create a video from prompt/image. "
                        "generate_audio: text-to-speech audio. "
                        "generate_talking_video: create a talking-head video from character image + script (TTS + animation + lip sync). "
                        "job_status: check status of a generation job. "
                        "list_jobs: recent generation history."
                    ),
                },
                "prompt": {"type": "string", "description": "Generation prompt / text to speak"},
                "style": {"type": "string", "description": "Visual style or mood (for image/video)"},
                "model": {"type": "string", "description": "Specific model to use (e.g. dall-e-3, stability-ai)"},
                "width": {"type": "integer", "description": "Image width in pixels"},
                "height": {"type": "integer", "description": "Image height in pixels"},
                "duration": {"type": "integer", "enum": [4, 5, 6, 8, 10], "description": "Video duration in seconds"},
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
                "mode": {"type": "string", "enum": ["loop", "multi_clip"], "description": "Video mode for generate_talking_video: loop (fast/cheap, visible seams) or multi_clip (unique clips, no loops, 3-6x cost)"},
                "sync_mode": {"type": "string", "enum": ["loop", "cut_off", "bounce"], "description": "Lip sync mode for generate_talking_video"},
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

    # ── Co-Leadership Assessment ─────────────────────────────────────────────
    {
        "type": "function",
        "name": "coleadership_agent",
        "description": (
            "Co-leadership and organizational assessment: team dynamics, "
            "leadership evaluation, organizational health, collaboration patterns. "
            "Use when the user asks about team leadership, organizational "
            "assessment, team dynamics, or leadership strategy."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Leadership assessment task",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context: team, organization, focus_area",
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
                    "enum": ["overview", "migrations", "tables", "pgvector"],
                    "description": (
                        "overview=connection + migration summary (default), "
                        "migrations=list unapplied migrations, "
                        "tables=row counts for key tables, "
                        "pgvector=vector extension status and embedding counts"
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
            "'pa_tools_smoke' (14 checks across boardroom, initiatives, celery, spiders, manifest)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "suite": {
                    "type": "string",
                    "enum": ["cockpit_health", "cockpit_incidents_crud", "pa_tools_smoke"],
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
            },
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
    'coleadership_agent': ['intelligence_enricher', 'strategic_memory'],
    'strategic_review': ['domain_context', 'strategic_memory'],
    'create_brand_video': ['intelligence_enricher'],
    'create_project_from_research': ['domain_context', 'spider_trends'],
    'http_smoke_test': [],
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
    'coleadership_agent': 'agent_execution',
    'strategic_review': 'agent_execution',
    'create_brand_video': 'agent_execution',
    'create_project_from_research': 'agent_execution',
    'http_smoke_test': 'verification',
}
