"""
Tool Dispatcher - Centralized Tool Execution with No Silent Failures
=====================================================================

Session 931: Created to solve the "tool exists != tool works" problem.

Every tool call goes through this dispatcher which:
1. Wraps execution in try/catch
2. Measures latency
3. Generates trace_id for debugging
4. Returns structured result (never fails silently)

Usage:
    from core.services.tool_dispatcher import get_tool_dispatcher
    dispatcher = get_tool_dispatcher()
    result = await dispatcher.execute(
        tool_name="human_decisions_tool",
        payload={"action": "list"},
        user_id=user.id
    )

    # Result is always structured:
    # {
    #     "ok": True/False,
    #     "tool": "human_decisions_tool",
    #     "latency_ms": 234,
    #     "error_code": None,
    #     "error_message": None,
    #     "trace_id": "abc123",
    #     "result": {...}
    # }
"""

import logging
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps

logger = logging.getLogger(__name__)


# ── Tool Call Metrics (Redis counters) ────────────────────────────────────
# Tracks per-tool call counts, latency, and status for observability.
# Keys: tool_metrics:{tool}:{action}:{status} → counter
#        tool_metrics:{tool}:{action}:latency_sum → cumulative ms
# Daily keys auto-expire after 48h.

# Session 1083 (Rigby audit): metrics-recorder health is observable at
# module level so every tool call can surface metrics_ok via dispatcher
# metadata, and failures get logged at most once per _METRIC_LOG_INTERVAL
# seconds instead of silently swallowing every Redis/import error.
_metric_recorder_ok = True
_last_metric_error_log = 0.0
_METRIC_LOG_INTERVAL = 60.0  # seconds — rate-limit to avoid log spam


def _record_tool_metric(tool_name: str, action: str, status: str, latency_ms: int):
    """Record a tool call metric in Redis. Fire-and-forget — never raises.

    Sets module-level _metric_recorder_ok to False on failure and rate-logs
    the first error at WARNING once per minute so Chris can see when
    observability is broken without drowning the logs if Redis goes down.
    """
    global _metric_recorder_ok, _last_metric_error_log
    try:
        from django.conf import settings
        import redis as redis_lib
        from datetime import date

        redis_url = getattr(settings, 'REDIS_URL', None)
        if not redis_url:
            _metric_recorder_ok = False
            return

        r = redis_lib.Redis.from_url(redis_url, decode_responses=True, socket_timeout=1)
        day = date.today().isoformat()
        prefix = f"tool_metrics:{day}"

        pipe = r.pipeline(transaction=False)
        pipe.hincrby(f"{prefix}:calls", f"{tool_name}:{action}:{status}", 1)
        pipe.hincrby(f"{prefix}:totals", tool_name, 1)
        pipe.hincrby(f"{prefix}:latency", f"{tool_name}:{action}", latency_ms)
        pipe.hincrby(f"{prefix}:calls", "_global_total", 1)
        for key in [f"{prefix}:calls", f"{prefix}:totals", f"{prefix}:latency"]:
            pipe.expire(key, 172800)
        pipe.execute()
        _metric_recorder_ok = True
    except Exception as e:
        _metric_recorder_ok = False
        now = time.monotonic()
        if now - _last_metric_error_log >= _METRIC_LOG_INTERVAL:
            _last_metric_error_log = now
            logger.warning(
                "tool_dispatcher metrics recorder failed — observability "
                "degraded (metrics_ok=False). tool=%s action=%s error=%s: %s",
                tool_name,
                action,
                type(e).__name__,
                e,
            )


def get_tool_metrics(day: str = None) -> Dict[str, Any]:
    """
    Read tool call metrics for a given day.

    Returns: {
        'date': '2026-03-15',
        'total_calls': 1234,
        'by_tool': {'bpaas_tool': 5, 'ops_tool': 42, ...},
        'by_call': {'bpaas_tool:get_schema:ok': 3, ...},
        'latency': {'bpaas_tool:get_schema': 150, ...},
    }
    """
    try:
        from django.conf import settings
        import redis as redis_lib
        from datetime import date as date_cls

        redis_url = getattr(settings, 'REDIS_URL', None)
        if not redis_url:
            return {'error': 'Redis not configured'}

        r = redis_lib.Redis.from_url(redis_url, decode_responses=True, socket_timeout=2)
        day = day or date_cls.today().isoformat()
        prefix = f"tool_metrics:{day}"

        calls = r.hgetall(f"{prefix}:calls") or {}
        totals = r.hgetall(f"{prefix}:totals") or {}
        latency = r.hgetall(f"{prefix}:latency") or {}

        # Build top tools sorted by call count
        sorted_tools = sorted(totals.items(), key=lambda x: int(x[1]), reverse=True)

        return {
            'date': day,
            'total_calls': int(calls.get('_global_total', 0)),
            'by_tool': {k: int(v) for k, v in sorted_tools},
            'by_call': {k: int(v) for k, v in calls.items() if k != '_global_total'},
            'latency': {k: int(v) for k, v in latency.items()},
        }
    except Exception as e:
        return {'error': str(e)}


# Error codes for structured failures
class ToolErrorCode:
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    TOOL_EXCEPTION = "TOOL_EXCEPTION"
    TOOL_INVALID_PAYLOAD = "TOOL_INVALID_PAYLOAD"
    TOOL_PERMISSION_DENIED = "TOOL_PERMISSION_DENIED"
    TOOL_DEPENDENCY_FAILED = "TOOL_DEPENDENCY_FAILED"
    AGENT_EXECUTION_FAILED = "AGENT_EXECUTION_FAILED"


@dataclass
class ToolResult:
    """Structured result from tool execution."""
    ok: bool
    tool: str
    latency_ms: int
    error_code: Optional[str]
    error_message: Optional[str]
    trace_id: str
    result: Optional[Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



from core.services.td_handlers_agents import AgentHandlersMixin
from core.services.td_handlers_content import ContentHandlersMixin
from core.services.td_handlers_ops import OpsHandlersMixin
from core.services.td_handlers_core import CoreHandlersMixin
from core.services.td_handlers_gateway import GatewayHandlersMixin
from core.services.td_handlers_codejobs import CodeJobHandlersMixin
from core.services.td_handlers_railway import RailwayToolMixin
from core.services.td_handlers_newsletter import NewsletterHandlersMixin
from core.services.pa_identity import PA_IDENTITY


class ToolDispatcher(AgentHandlersMixin, ContentHandlersMixin, OpsHandlersMixin, CoreHandlersMixin, GatewayHandlersMixin, CodeJobHandlersMixin, RailwayToolMixin, NewsletterHandlersMixin):
    """
    Centralized dispatcher for all PA tool executions.

    Guarantees:
    - Never fails silently
    - Always returns structured ToolResult
    - Logs all executions with trace_id
    - Measures latency
    """

    # Default timeout for tool execution (seconds)
    DEFAULT_TIMEOUT = 30

    # Session 1079: Removed tool → gateway replacement map.
    # Used by tool_migration_report to track straggler calls from agent-internal code.
    REMOVED_TOOL_ALIASES = {
        # work_tool absorbs initiative_tool
        'initiative_tool': ('work_tool', 'initiative_list'),
        # content_tool absorbs content_review_tool, generate_blog_tool, deliverables_tool
        'content_review_tool': ('content_tool', 'content_list'),
        'generate_blog_tool': ('content_tool', 'generate_blog'),
        'deliverables_tool': ('content_tool', 'deliverable_list'),
        # governance_tool absorbs boardroom_tool, human_decisions_tool
        'boardroom_tool': ('governance_tool', 'inbox'),
        'human_decisions_tool': ('governance_tool', 'decisions_list'),
        # intelligence_tool absorbs stock/sports/legislation/search tools
        'stock_intelligence_tool': ('intelligence_tool', 'stocks_alerts'),
        'sports_betting_tool': ('intelligence_tool', 'sports_predictions'),
        'legislation_tool': ('intelligence_tool', 'legislation_search'),
        'rag_query_tool': ('intelligence_tool', 'search'),
        'spider_data_tool': ('intelligence_tool', 'search'),
        'web_search': ('intelligence_tool', 'search'),
        # ops_tool absorbs system health tools
        'system_health_tool': ('ops_tool', 'slo_status'),
        'error_summary_tool': ('ops_tool', 'failure_signatures'),
    }

    # The 8 gateway tool names (+ 3 standalone primitives + 2 focused splits)
    GATEWAY_TOOLS = frozenset([
        'ops_tool', 'work_tool', 'content_tool',
        'deliverable_tool', 'blog_tool',  # Session 1077: focused splits
        'governance_tool', 'intelligence_tool', 'studio_tool',
        'cockpit_tool', 'narrative_tool', 'railway_tool',  # Session 1100
        # Session 1035-W2: 11 new gateway tools
        'proactive_tool', 'distribution_tool', 'calendar_tool',
        'experiment_tool', 'podcast_tool', 'campaign_tool',
        'audit_tool', 'conceptforge_tool', 'profile_tool',
        'self_awareness_tool', 'ats_tool',
    ])

    def __init__(self):
        self._tool_handlers: Dict[str, Callable] = {}
        self._execution_count = 0
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register handlers for all known tools."""
        # Creation tools
        self.register("image_generation_agent", self._handle_agent_tool)
        self.register("image_editing_agent", self._handle_agent_tool)
        self.register("video_generation_agent", self._handle_agent_tool)
        self.register("video_editing_agent", self._handle_agent_tool)
        self.register("resolve_agent", self._handle_agent_tool)
        self.register("audio_generation_agent", self._handle_agent_tool)
        self.register("three_d_generation_agent", self._handle_agent_tool)
        self.register("character_training_agent", self._handle_agent_tool)
        self.register("talking_character_agent", self._handle_agent_tool)

        # Research & Analysis agents
        self.register("web_search", self._handle_web_search)
        self.register("competitor_analysis_agent", self._handle_agent_tool)
        self.register("customer_research_agent", self._handle_agent_tool)
        self.register("brand_strategy_agent", self._handle_agent_tool)
        self.register("content_strategy_agent", self._handle_agent_tool)
        self.register("marketing_strategy_agent", self._handle_agent_tool)
        self.register("content_writer_agent", self._handle_agent_tool)
        self.register("research_agent", self._handle_agent_tool)
        self.register("trend_analysis_agent", self._handle_agent_tool)
        self.register("opportunity_scoring_agent", self._handle_agent_tool)
        self.register("market_intelligence_agent", self._handle_agent_tool)
        self.register("platform_audit_agent", self._handle_agent_tool)
        self.register("thinking_agent", self._handle_agent_tool)
        self.register("decision_enforcer_agent", self._handle_agent_tool)

        # Strategy & Content agents
        self.register("brand_identity_agent", self._handle_agent_tool)
        self.register("seo_optimizer_agent", self._handle_agent_tool)
        self.register("social_media_agent", self._handle_agent_tool)
        self.register("editor_agent", self._handle_agent_tool)
        self.register("content_audit_agent", self._handle_agent_tool)
        self.register("prompt_engineering_agent", self._handle_agent_tool)
        self.register("technical_document_agent", self._handle_agent_tool)
        self.register("creative_director_agent", self._handle_agent_tool)

        # Executive & Orchestration agents
        self.register("cto_agent", self._handle_agent_tool)
        self.register("coo_agent", self._handle_agent_tool)
        self.register("meeting_coordinator_agent", self._handle_agent_tool)
        self.register("campaign_orchestrator_agent", self._handle_agent_tool)
        self.register("opportunity_pipeline_agent", self._handle_agent_tool)
        self.register("content_executor_agent", self._handle_agent_tool)
        self.register("ai_series_workflow_agent", self._handle_agent_tool)

        # Stock & Markets agents
        self.register("stock_audit_coordinator", self._handle_agent_tool)
        self.register("stock_analyst_agent", self._handle_agent_tool)
        self.register("market_movement_monitor_agent", self._handle_agent_tool)
        self.register("institutional_watcher_agent", self._handle_agent_tool)
        self.register("market_anomaly_detector_agent", self._handle_agent_tool)
        self.register("bull_case_agent", self._handle_agent_tool)
        self.register("bear_case_agent", self._handle_agent_tool)
        self.register("signal_scanner_agent", self._handle_agent_tool)
        self.register("market_intelligence_coordinator", self._handle_agent_tool)

        # Sports & Betting agents
        self.register("prediction_market_analyst", self._handle_agent_tool)
        self.register("game_predictor", self._handle_agent_tool)
        self.register("line_movement_analyzer", self._handle_agent_tool)
        self.register("sharp_action_detector", self._handle_agent_tool)
        self.register("bookmaker_agent", self._handle_agent_tool)

        # Blockchain Audit agents
        self.register("blockchain_audit_coordinator", self._handle_agent_tool)
        self.register("smart_contract_auditor_agent", self._handle_agent_tool)
        self.register("transaction_monitor_agent", self._handle_agent_tool)
        self.register("whale_watcher_agent", self._handle_agent_tool)
        self.register("exploit_detector_agent", self._handle_agent_tool)

        # Narrative Drift agents
        self.register("narrative_drift_coordinator", self._handle_agent_tool)
        self.register("narrative_historian_agent", self._handle_agent_tool)
        self.register("trend_break_detector_agent", self._handle_agent_tool)
        self.register("cultural_impact_agent", self._handle_agent_tool)

        # Content Studio agents
        self.register("autonomous_content_studio_coordinator", self._handle_agent_tool)
        self.register("topic_miner_agent", self._handle_agent_tool)
        self.register("contrarian_agent", self._handle_agent_tool)
        self.register("performance_analyst_agent", self._handle_agent_tool)
        self.register("voice_critic_agent", self._handle_agent_tool)
        self.register("content_diversity_orchestrator", self._handle_agent_tool)
        self.register("distribution_agent", self._handle_agent_tool)

        # Podcast agents
        self.register("podcast_coordinator_agent", self._handle_agent_tool)
        self.register("debate_advocate_agent", self._handle_agent_tool)
        self.register("debate_skeptic_agent", self._handle_agent_tool)
        self.register("moderator_agent", self._handle_agent_tool)

        # Training & Security agents
        self.register("trained_creation_agent", self._handle_agent_tool)
        self.register("memory_isolation_agent", self._handle_agent_tool)
        self.register("security_agent", self._handle_agent_tool)

        # ML Pipeline tools
        self.register("opportunity_manager_tool", self._handle_opportunity_manager)
        self.register("task_manager_tool", self._handle_task_manager)
        self.register("pipeline_orchestrator_tool", self._handle_pipeline_orchestrator)
        self.register("revenue_tracker_tool", self._handle_revenue_tracker)
        self.register("ml_analysis", self._handle_ml_analysis)

        # Universal tools
        self.register("universal_agent_tool", self._handle_universal_agent)
        self.register("workspace_tool", self._handle_workspace)
        self.register("media_tool", self._handle_media)
        self.register("voice_clone_tool", self._handle_voice_clone)
        self.register("davinci_tool", self._handle_davinci)
        self.register("obs_tool", self._handle_obs)
        self.register("bpaas_tool", self._handle_bpaas)
        self.register("video_history_tool", self._handle_video_history)

        # Body system tools
        self.register("get_body_vitals", self._handle_body_vitals)
        self.register("check_resource_budget", self._handle_check_budget)
        self.register("get_system_alerts", self._handle_system_alerts)
        self.register("cost_telemetry_tool", self._handle_cost_telemetry)

        # Intelligence tools
        # predictions_tool: REMOVED — AgentPrediction deprecated (Session 284), handler was a no-op
        self.register("gates_tool", self._handle_gates)
        self.register("pilots_tool", self._handle_pilots)
        self.register("reasoning_engine_tool", self._handle_reasoning_engine)

        # Session 943: Brainstorm search tool for accessing Discussion/Panel insights
        self.register("brainstorm_tool", self._handle_brainstorm)

        # Session 1031: Dream browsing/approval via PA
        self.register("dream_tool", self._handle_dream)

        # Workflow tools
        self.register("workflow_orchestration_agent", self._handle_agent_tool)
        self.register("create_brand_video", self._handle_agent_tool)
        self.register("create_project_from_research", self._handle_agent_tool)
        self.register("strategic_review", self._handle_agent_tool)
        # coleadership_agent: REMOVED — CoLeadershipAgent class never existed

        # Intelligence agents — dispatch via Celery
        self.register("system_intelligence_agent", self._handle_agent_tool)

        # Legal tools — Session 1035: dedicated handler via AgentRouter (not registry stub)
        self.register("legal_doc_drafter_agent", self._handle_legal_agent)

        # Session 948: New PA enhancement tools
        self.register("execution_history_tool", self._handle_execution_history)
        self.register("learning_patterns_tool", self._handle_learning_patterns)
        self.register("feedback_tool", self._handle_feedback)

        # Session 969: Live telemetry tools for PA self-awareness
        self.register("recent_activity_tool", self._handle_recent_activity)

        # Session 970: Surgical moves verification tool
        self.register("surgical_moves_status_tool", self._handle_surgical_moves_status)

        # Session 973: Status snapshot for broad system overview
        self.register("status_snapshot_tool", self._handle_status_snapshot)

        # Session 1007: Agent introspection + scheduled tasks
        self.register("agent_introspection_tool", self._handle_agent_introspection)
        self.register("scheduled_tasks_tool", self._handle_scheduled_tasks)

        # Session 1034: Research-and-create — chains web search → LLM generation → Deliverable save
        self.register("research_and_create_tool", self._handle_research_and_create)

        # Session 1048: Task volume breakdown
        self.register("task_breakdown_tool", self._handle_task_breakdown)

        # Session 1071: Platform awareness + studio tools
        self.register("platform_awareness_tool", self._handle_platform_awareness)
        self.register("studio_tool", self._handle_studio)

        # Session 1088: Persona agents — 139 DB-only specialists
        self.register("persona_tool", self._handle_persona)

        # Session 1069: Platform config + DB health for PA self-awareness
        self.register("platform_config_tool", self._handle_platform_config)
        self.register("db_health_tool", self._handle_db_health)

        # HTTP smoke test for endpoint verification
        self.register("http_smoke_test", self._handle_http_smoke_test)

        # PA Learning Loop — insight management
        self.register("learning_tool", self._handle_learning)

        # Session G1: Competitor comparison — generate, status, list, detail
        self.register("competitor_comparison_tool", self._handle_competitor_comparison)
        self.register("workflow_run_tool", self._handle_workflow_run)

        # Conversation memory — cross-thread PA recall
        self.register("conversation_tool", self._handle_conversation)

        # Persistent memory — save/list/delete/search across sessions
        self.register("remember_tool", self._handle_remember)

        # Session 1078: Ops tool — version, SLO status, failure signatures
        self.register("ops_tool", self._handle_ops)

        # Session 1080: Agent control tool — block/unblock/list agents (DB-backed)
        self.register("agent_control_tool", self._handle_agent_control)

        # Session 1086: Active priority tool — priority-aware routing (initiative 2dcb79d7)
        self.register("active_priority_tool", self._handle_active_priority)

        # Session 1088: Governor tool — mission alignment + circuit breaker status
        self.register("governor_tool", self._handle_governor)

        # Session 1080: Ops Autopilot tool — status/history/run/config
        self.register("autopilot_tool", self._handle_autopilot)
        self.register("ops_digest_tool", self._handle_ops_digest)

        # Session 1078: Work tool — gateway for initiatives + action items
        self.register("work_tool", self._handle_work)

        # Session 1079: Content tool — gateway for content_review + blog generation + deliverables
        self.register("content_tool", self._handle_content)

        # Session 1077: Focused tool split — reduce GPT function-calling confusion
        self.register("deliverable_tool", self._handle_deliverable_direct)
        self.register("blog_tool", self._handle_blog_direct)

        # Session 1079: Governance tool — gateway for boardroom + human decisions
        self.register("governance_tool", self._handle_governance)

        # Session 1079: Intelligence tool — gateway for stocks, sports, legislation, search, KB
        self.register("intelligence_tool", self._handle_intelligence)

        # Session 1100: Cockpit tool — Celery beat schedule, worker health, queue depths
        self.register("cockpit_tool", self._handle_cockpit)

        # Railway platform tool — service status, logs, restart, redeploy
        self.register("railway_tool", self._handle_railway)

        # Session 1100: Narrative tool — narrative drift, shifts, evidence, alerts
        self.register("narrative_tool", self._handle_narrative)

        # Session 1035-W2: 11 new gateway tools
        self.register("proactive_tool", self._handle_proactive)
        self.register("distribution_tool", self._handle_distribution)
        self.register("calendar_tool", self._handle_calendar)
        self.register("experiment_tool", self._handle_experiment)
        self.register("podcast_tool", self._handle_podcast)
        self.register("campaign_tool", self._handle_campaign)
        self.register("audit_tool", self._handle_audit)
        self.register("conceptforge_tool", self._handle_conceptforge)
        self.register("profile_tool", self._handle_profile)
        self.register("self_awareness_tool", self._handle_self_awareness)
        self.register("ats_tool", self._handle_ats)

        # Newsletter publishing adapter — POC 1 Autopilot Ops
        self.register("newsletter_tool", self._handle_newsletter)

        # Codebase, analytics, Discord, and mobile introspection tools
        self.register("repo_tool", self._handle_repo)
        self.register("analytics_tool", self._handle_analytics)
        self.register("discord_tool", self._handle_discord)
        self.register("mobile_tool", self._handle_mobile)
        self.register("vip_invite_tool", self._handle_vip_invite)

        # Remote Code Worker
        self.register("code_job_tool", self._handle_code_job)

        # Claude Code Engineer — Rigby can spawn autonomous coding sessions
        self.register("claude_code_tool", self._handle_claude_code)

        # Session 1035-Audit: Platform access gap tools
        self.register("spider_status_tool", self._handle_spider_status)
        self.register("agent_memory_tool", self._handle_agent_memory)
        self.register("heartbeat_history_tool", self._handle_heartbeat_history)
        self.register("infra_health_tool", self._handle_infra_health)

        # R2-6: KB / embedding browsing
        self.register("kb_tool", self._handle_kb_browse)

        # In-app messaging between platform users
        self.register("messaging_tool", self._handle_messaging)

        # Session management (health check, create fresh, list recent)
        self.register("session_tool", self._handle_session)

        logger.info(f"ToolDispatcher: Registered {len(self._tool_handlers)} tool handlers")

    def register(self, tool_name: str, handler: Callable):
        """Register a handler for a tool."""
        self._tool_handlers[tool_name] = handler

    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID for this execution."""
        self._execution_count += 1
        return f"tool-{self._execution_count}-{uuid.uuid4().hex[:8]}"

    async def execute(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> ToolResult:
        """
        Execute a tool with full error handling.

        Args:
            tool_name: Name of the tool to execute
            payload: Tool-specific payload
            user_id: Optional user ID for context
            timeout: Optional timeout override (seconds)

        Returns:
            ToolResult with structured response (never raises)
        """
        trace_id = self._generate_trace_id()
        start_time = time.time()
        timeout = timeout or self.DEFAULT_TIMEOUT
        action = payload.get('action', '_default') if isinstance(payload, dict) else '_default'

        logger.info(f"[{trace_id}] Executing tool: {tool_name}")

        # Server-side tool access enforcement via AssistantProfile
        if user_id:
            try:
                from core.models_assistant_profile import AssistantProfile
                profile = AssistantProfile.objects.filter(user_id=user_id).first()
                if profile:
                    allowed = profile.get_allowed_tools()
                    if allowed is not None and tool_name not in allowed:
                        latency_ms = int((time.time() - start_time) * 1000)
                        logger.warning(
                            f"[{trace_id}] TOOL ACCESS DENIED: {tool_name} not in allowed_tools "
                            f"for user_id={user_id} (role={profile.role})"
                        )
                        _record_tool_metric(tool_name, action, 'denied', latency_ms)
                        return ToolResult(
                            ok=False, tool=tool_name, latency_ms=latency_ms,
                            error_code='TOOL_PERMISSION_DENIED',
                            error_message=f'Tool {tool_name} is not available for your account.',
                            trace_id=trace_id, result=None,
                        )
            except Exception as e:
                logger.debug(f"[{trace_id}] AssistantProfile check skipped: {e}")

        # Check if tool is registered
        if tool_name not in self._tool_handlers:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[{trace_id}] Tool not found: {tool_name}")
            return ToolResult(
                ok=False,
                tool=tool_name,
                latency_ms=latency_ms,
                error_code=ToolErrorCode.TOOL_NOT_FOUND,
                error_message=f"Tool '{tool_name}' is not registered",
                trace_id=trace_id,
                result=None
            )

        try:
            # Execute with timeout
            handler = self._tool_handlers[tool_name]

            # Check if handler is async
            if asyncio.iscoroutinefunction(handler):
                result = await asyncio.wait_for(
                    handler(tool_name, payload, user_id, trace_id),
                    timeout=timeout
                )
            else:
                # Run sync handler in thread pool
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: handler(tool_name, payload, user_id, trace_id)
                    ),
                    timeout=timeout
                )

            latency_ms = int((time.time() - start_time) * 1000)

            # Session 1085: Scrub PII/secrets from tool results
            if isinstance(result, dict):
                from core.services.data_scrubber import scrub_dict
                try:
                    result = scrub_dict(result, max_depth=5)
                except Exception as e:
                    logger.warning(f"[{trace_id}] PII scrub failed for {tool_name}: {e}")

            logger.info(f"[{trace_id}] Tool {tool_name} completed in {latency_ms}ms")

            # Session 1098: Emit ImpactEvent for PA tool completions.
            self._emit_pa_impact_event(tool_name, payload, user_id, trace_id)

            # Track tool call metrics in Redis
            _record_tool_metric(tool_name, action, 'ok', latency_ms)

            # Record as workspace operation (fire-and-forget).
            # Was 'except Exception: pass' which dropped op-recording
            # errors silently — every tool call's workspace operation
            # trace could vanish and the Ops Run timeline would have
            # holes with no visible cause.
            try:
                from core.services.operation_recorder import record_op
                record_op(
                    op_type='tool_call',
                    title=f"{tool_name}.{action}",
                    actor_type='system',
                    actor_id=PA_IDENTITY,
                    success=True,
                    execution_time_ms=latency_ms,
                    metadata={'tool': tool_name, 'action': action},
                    correlation_id=trace_id,
                )
            except Exception as e:
                logger.warning(
                    "tool_dispatcher: record_op failed for %s.%s "
                    "(%s: %s) — Ops Run timeline will be missing this entry",
                    tool_name, action, type(e).__name__, e,
                )

            return ToolResult(
                ok=True,
                tool=tool_name,
                latency_ms=latency_ms,
                error_code=None,
                error_message=None,
                trace_id=trace_id,
                result=result
            )

        except asyncio.TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[{trace_id}] Tool {tool_name} timed out after {timeout}s")
            _record_tool_metric(tool_name, action, 'timeout', latency_ms)
            return ToolResult(
                ok=False,
                tool=tool_name,
                latency_ms=latency_ms,
                error_code=ToolErrorCode.TOOL_TIMEOUT,
                error_message=f"Tool execution exceeded {timeout}s timeout",
                trace_id=trace_id,
                result=None
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[{trace_id}] Tool {tool_name} failed: {e}", exc_info=True)
            _record_tool_metric(tool_name, action, 'error', latency_ms)
            return ToolResult(
                ok=False,
                tool=tool_name,
                latency_ms=latency_ms,
                error_code=ToolErrorCode.TOOL_EXCEPTION,
                error_message=str(e),
                trace_id=trace_id,
                result=None
            )

    # ── PA Impact Event Emission ───────────────────────────────────────────
    # Session 1098: Record successful PA tool calls as ImpactEvents so the
    # ROI engine can attribute outcomes to PersonalAssistant.

    # Tools that represent meaningful user-facing outcomes (not internal plumbing)
    _IMPACT_WORTHY_TOOLS = frozenset({
        # Gateway tools — each successful call is a user-requested action
        'ops_tool', 'work_tool', 'content_tool',
        'governance_tool', 'intelligence_tool', 'studio_tool',
        # Agent dispatch tools — user-requested creative/research work
        'image_generation_agent', 'video_generation_agent',
        'audio_generation_agent', 'resolve_agent',
        'research_agent', 'customer_research_agent',
        'run_agent',
    })

    # Map tool names to ImpactEvent desk
    _TOOL_DESK_MAP = {
        'intelligence_tool': 'research',
        'content_tool': 'content',
        'studio_tool': 'content',
        'work_tool': 'career',
        'ops_tool': 'general',
        'governance_tool': 'general',
    }

    def _emit_pa_impact_event(
        self, tool_name: str, payload: dict,
        user_id: Optional[int], trace_id: str,
    ):
        """Emit an ImpactEvent for a successful PA tool completion."""
        if tool_name not in self._IMPACT_WORTHY_TOOLS:
            return
        try:
            from core.models_impact_events import ImpactEvent
            import uuid

            action = payload.get('action', '') if isinstance(payload, dict) else ''
            desk = self._TOOL_DESK_MAP.get(tool_name, 'general')

            ImpactEvent.objects.create(
                impact_type='content_action',
                desk=desk,
                value_usd=0,
                impact_points=ImpactEvent.points_for_type('content_action'),
                agent_name=PA_IDENTITY,
                source_object_type=f'pa_tool:{tool_name}',
                trace_id=uuid.UUID(trace_id) if trace_id and len(trace_id) == 36 else None,
                user_id=user_id,
                metadata={
                    'tool_name': tool_name,
                    'action': action,
                },
            )
        except Exception as e:
            logger.debug(f"[PA ImpactEvent] Skipped for {tool_name}: {e}")

    def execute_sync(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> ToolResult:
        """Synchronous version of execute for non-async contexts."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.execute(tool_name, payload, user_id, timeout)
            )
        finally:
            loop.close()

    # =========================================================================
    # TOOL HANDLERS
    # =========================================================================

    # Session 1090: Fields that should be promoted from the top-level
    # payload into context when GPT-5.2 puts them at the root level
    # instead of nesting inside the 'context' key.  Also catches fields
    # injected by the PA entrypoint (workspace_id, conversation_id).
    _CONTEXT_PROMOTE_KEYS = {
        'workspace_id', 'workspace', 'conversation_id',
        'content_type', 'tone', 'target_audience', 'word_count',
        'topic', 'keywords', 'blog_id', 'focus_areas',
        'content', 'research', 'research_summary',
    }

    def _handle_agent_tool(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Generic handler for agent-based tools — dispatches to Celery async.

        Session 1088: Converted from synchronous AgentRouter.route() to Celery
        async dispatch. All agent tools were timing out (30-60s) when called
        synchronously from the PA. Now returns task_id immediately.

        Session 1090: Promotes known context fields from the top-level payload
        into context['...'].  GPT-5.2 frequently puts structured data (content_type,
        tone, blog_id, workspace_id) at the payload root rather than nesting it
        inside the 'context' key.  The PA entrypoint also injects workspace_id
        and conversation_id at the root.  Without this promotion step, agents
        that rely on context fields (EditorAgent, ContentWriterAgent) fail with
        "missing content/blog_id" even though the data was sent.

        Deliverable lookup happens in execute_agent_task after completion.
        PA user assignment is handled via context['user_id'].
        """
        from core.tasks import execute_agent_task

        agent_name = self._tool_to_agent_name(tool_name)

        task_text = payload.get('task') or payload.get('prompt') or payload.get('query', '')
        context = payload.get('context') or {}
        if not isinstance(context, dict):
            context = {}

        # Session 1090: Promote known fields from payload root into context.
        for key in self._CONTEXT_PROMOTE_KEYS:
            if key in payload and key not in context:
                context[key] = payload[key]

        if user_id:
            context['user_id'] = str(user_id)

        # Session 1090: EditorAgent requires 'content' in context.  When the
        # PA dispatches it, Rigby typically references other deliverables by
        # name in the task text but doesn't include the actual content.
        # Fix: gather recent deliverables from the workspace and concatenate
        # them as the content to edit.
        if agent_name == 'EditorAgent' and 'content' not in context and 'blog_id' not in context:
            workspace_id = context.get('workspace_id') or context.get('workspace')
            gathered_content = self._gather_workspace_content_for_editor(workspace_id, task_text)
            if gathered_content:
                context['content'] = gathered_content
            else:
                # Last resort: use task text itself
                context['content'] = {
                    'title': task_text[:120],
                    'full_text': task_text,
                    'sections': [],
                }

        # Session 1088: Route to long_running (matches CELERY_TASK_ROUTES).
        # Was 'agents' queue which no worker consumes.
        celery_task = execute_agent_task.apply_async(args=[agent_name, task_text, context], queue='long_running')

        return {
            'task_id': str(celery_task.id),
            'mode': 'async',
            'agent': agent_name,
            'message': (
                f'{agent_name} dispatched (task {celery_task.id}). '
                f'Use job_status to check progress.'
            ),
        }

    def _gather_workspace_content_for_editor(
        self,
        workspace_id: Optional[str],
        task_text: str,
    ) -> Optional[Dict[str, Any]]:
        """Gather recent deliverables from a workspace as content for EditorAgent.

        Session 1090: When Rigby dispatches EditorAgent, she references other
        deliverables ("Incident Card + CTO brief + COO brief") but doesn't
        include the actual text.  This method fetches the most recent
        deliverables from the workspace and concatenates them into a
        structured content dict that EditorAgent can process.
        """
        if not workspace_id:
            return None
        try:
            from core.models_deliverables import Deliverable

            deliverables = (
                Deliverable.objects
                .filter(workspace_id=workspace_id)
                .exclude(title__startswith='EditorAgent:')  # Don't edit our own output
                .order_by('-created_at')[:6]
            )
            if not deliverables:
                return None

            sections = []
            titles = []
            for d in deliverables:
                body = d.content or ''
                if not body.strip():
                    continue
                title = d.title or 'Untitled'
                titles.append(title)
                sections.append({
                    'heading': title,
                    'content': body[:3000],  # Cap per section to avoid prompt bloat
                })

            if not sections:
                return None

            logger.info(
                "[EditorAgent dispatch] Gathered %d deliverables from workspace %s: %s",
                len(sections), workspace_id, ', '.join(titles),
            )
            return {
                'title': f"Executive Brief (synthesized from {len(sections)} sources)",
                'intro': f"This brief synthesizes {len(sections)} workspace deliverables.",
                'sections': sections,
                'conclusion': '',
            }
        except Exception as e:
            logger.warning("Failed to gather workspace content for EditorAgent: %s", e)
            return None


def _redact_secrets(text: str) -> str:
    """Redact API keys, tokens, and secrets from memory content."""
    import re
    patterns = [
        (r'(sk-[a-zA-Z0-9]{20,})', '[REDACTED_API_KEY]'),
        (r'(ghp_[a-zA-Z0-9]{36,})', '[REDACTED_GITHUB_TOKEN]'),
        (r'(xoxb-[a-zA-Z0-9\-]+)', '[REDACTED_SLACK_TOKEN]'),
        (r'(eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,})', '[REDACTED_JWT]'),
        (r'(AKIA[A-Z0-9]{16})', '[REDACTED_AWS_KEY]'),
        (r'(key-[a-zA-Z0-9]{32,})', '[REDACTED_KEY]'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


# Singleton instance
_tool_dispatcher: Optional[ToolDispatcher] = None


def get_tool_dispatcher() -> ToolDispatcher:
    """Get the singleton ToolDispatcher instance."""
    global _tool_dispatcher
    if _tool_dispatcher is None:
        _tool_dispatcher = ToolDispatcher()
    return _tool_dispatcher


def reset_tool_dispatcher():
    """Reset the singleton so the next call to get_tool_dispatcher() creates a fresh instance.
    Session 1080: Used by PA schema live-reload to pick up new tool handlers."""
    global _tool_dispatcher
    _tool_dispatcher = None
