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


class ToolDispatcher:
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

    # The 8 gateway tool names (+ 3 standalone primitives)
    GATEWAY_TOOLS = frozenset([
        'ops_tool', 'work_tool', 'content_tool',
        'governance_tool', 'intelligence_tool', 'studio_tool',
        'cockpit_tool', 'narrative_tool',  # Session 1100
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
        self.register("davinci_tool", self._handle_davinci)
        self.register("obs_tool", self._handle_obs)
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

        # Session 1080: Ops Autopilot tool — status/history/run/config
        self.register("autopilot_tool", self._handle_autopilot)
        self.register("ops_digest_tool", self._handle_ops_digest)

        # Session 1078: Work tool — gateway for initiatives + action items
        self.register("work_tool", self._handle_work)

        # Session 1079: Content tool — gateway for content_review + blog generation + deliverables
        self.register("content_tool", self._handle_content)

        # Session 1079: Governance tool — gateway for boardroom + human decisions
        self.register("governance_tool", self._handle_governance)

        # Session 1079: Intelligence tool — gateway for stocks, sports, legislation, search, KB
        self.register("intelligence_tool", self._handle_intelligence)

        # Session 1100: Cockpit tool — Celery beat schedule, worker health, queue depths
        self.register("cockpit_tool", self._handle_cockpit)

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

        # Codebase, analytics, Discord, and mobile introspection tools
        self.register("repo_tool", self._handle_repo)
        self.register("analytics_tool", self._handle_analytics)
        self.register("discord_tool", self._handle_discord)
        self.register("mobile_tool", self._handle_mobile)
        self.register("vip_invite_tool", self._handle_vip_invite)

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

        logger.info(f"[{trace_id}] Executing tool: {tool_name}")

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
            # This gives PersonalAssistant measurable outcomes for ROI
            # attribution — without this, PA shows 0 outcomes and gets
            # flagged as low-QROI despite being user-facing.
            self._emit_pa_impact_event(tool_name, payload, user_id, trace_id)

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
                agent_name='PersonalAssistant',
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

        Deliverable lookup happens in execute_agent_task after completion.
        PA user assignment is handled via context['user_id'].
        """
        from core.tasks import execute_agent_task

        agent_name = self._tool_to_agent_name(tool_name)

        task_text = payload.get('task') or payload.get('prompt') or payload.get('query', '')
        context = payload.get('context', {})
        if user_id:
            context['user_id'] = str(user_id)

        celery_task = execute_agent_task.apply_async(args=[agent_name, task_text, context], queue='agents')

        return {
            'task_id': str(celery_task.id),
            'mode': 'async',
            'agent': agent_name,
            'message': (
                f'{agent_name} dispatched (task {celery_task.id}). '
                f'Use job_status to check progress.'
            ),
        }

    def _tool_to_agent_name(self, tool_name: str) -> str:
        """Map tool name to agent class name."""
        mappings = {
            # ── Media Creation & Editing ──
            'image_generation_agent': 'ImageAgent',
            'image_editing_agent': 'ImageEditingAgent',
            'video_generation_agent': 'VideoAgent',
            'video_editing_agent': 'VideoEditingAgent',
            'resolve_agent': 'ResolveAgent',
            'audio_generation_agent': 'AudioAgent',
            'three_d_generation_agent': 'ThreeDAgent',
            'character_training_agent': 'CharacterTrainingAgent',
            'talking_character_agent': 'TalkingCharacterAgent',
            # ── Research & Analysis ──
            'research_agent': 'ResearchAgent',
            'trend_analysis_agent': 'TrendAnalysisAgent',
            'opportunity_scoring_agent': 'OpportunityScoringAgent',
            'market_intelligence_agent': 'MarketIntelligenceAgent',
            'platform_audit_agent': 'PlatformAuditAgent',
            'thinking_agent': 'ThinkingAgent',
            'decision_enforcer_agent': 'DecisionEnforcerAgent',
            # ── Strategy & Content ──
            'brand_identity_agent': 'BrandIdentityAgent',
            'seo_optimizer_agent': 'SEOOptimizerAgent',
            'social_media_agent': 'SocialMediaAgent',
            'editor_agent': 'EditorAgent',
            'content_audit_agent': 'ContentAuditAgent',
            'prompt_engineering_agent': 'PromptEngineeringAgent',
            'technical_document_agent': 'TechnicalDocumentAgent',
            'creative_director_agent': 'CreativeDirectorAgent',
            # ── Business Research ──
            'competitor_analysis_agent': 'CompetitorAnalysisAgent',
            'customer_research_agent': 'CustomerResearchAgent',
            'brand_strategy_agent': 'BrandStrategyAgent',
            'content_strategy_agent': 'ContentStrategyAgent',
            'marketing_strategy_agent': 'MarketingStrategyAgent',
            'content_writer_agent': 'ContentWriterAgent',
            # ── Executive & Orchestration ──
            'cto_agent': 'CTOAgent',
            'coo_agent': 'COOAgent',
            'meeting_coordinator_agent': 'MeetingCoordinatorAgent',
            'campaign_orchestrator_agent': 'CampaignOrchestratorAgent',
            'opportunity_pipeline_agent': 'OpportunityPipelineAgent',
            'content_executor_agent': 'ContentExecutorAgent',
            'ai_series_workflow_agent': 'AISeriesWorkflowAgent',
            'workflow_orchestration_agent': 'WorkflowAgent',
            'create_brand_video': 'WorkflowAgent',
            'create_project_from_research': 'WorkflowAgent',
            'strategic_review': 'ContentStrategyAgent',  # Session 1068: StrategyAgent doesn't exist
            'system_intelligence_agent': 'SystemIntelligenceAgent',
            # ── Stock & Markets ──
            'stock_audit_coordinator': 'StockAuditCoordinator',
            'stock_analyst_agent': 'StockAnalystAgent',
            'market_movement_monitor_agent': 'MarketMovementMonitorAgent',
            'institutional_watcher_agent': 'InstitutionalWatcherAgent',
            'market_anomaly_detector_agent': 'MarketAnomalyDetectorAgent',
            'bull_case_agent': 'BullCaseAgent',
            'bear_case_agent': 'BearCaseAgent',
            'signal_scanner_agent': 'SignalScannerAgent',
            'market_intelligence_coordinator': 'MarketIntelligenceCoordinator',
            # ── Sports & Betting ──
            'prediction_market_analyst': 'PredictionMarketAnalyst',
            'game_predictor': 'GamePredictor',
            'line_movement_analyzer': 'LineMovementAnalyzer',
            'sharp_action_detector': 'SharpActionDetector',
            'bookmaker_agent': 'BookmakerAgent',
            # ── Blockchain Audit ──
            'blockchain_audit_coordinator': 'BlockchainAuditCoordinator',
            'smart_contract_auditor_agent': 'SmartContractAuditorAgent',
            'transaction_monitor_agent': 'TransactionMonitorAgent',
            'whale_watcher_agent': 'WhaleWatcherAgent',
            'exploit_detector_agent': 'ExploitDetectorAgent',
            # ── Narrative Drift ──
            'narrative_drift_coordinator': 'NarrativeDriftCoordinator',
            'narrative_historian_agent': 'NarrativeHistorianAgent',
            'trend_break_detector_agent': 'TrendBreakDetectorAgent',
            'cultural_impact_agent': 'CulturalImpactAgent',
            # ── Content Studio ──
            'autonomous_content_studio_coordinator': 'AutonomousContentStudioCoordinator',
            'topic_miner_agent': 'TopicMinerAgent',
            'contrarian_agent': 'ContrarianAgent',
            'performance_analyst_agent': 'PerformanceAnalystAgent',
            'voice_critic_agent': 'VoiceCriticAgent',
            'content_diversity_orchestrator': 'ContentDiversityOrchestrator',
            # ── Podcast ──
            'podcast_coordinator_agent': 'PodcastCoordinatorAgent',
            'debate_advocate_agent': 'DebateAdvocateAgent',
            'debate_skeptic_agent': 'DebateSkepticAgent',
            'moderator_agent': 'ModeratorAgent',
            # ── Training & Security ──
            'trained_creation_agent': 'TrainedCreationAgent',
            'memory_isolation_agent': 'MemoryIsolationAgent',
            'security_agent': 'MemoryIsolationAgent',
            # ── Legal ──
            'legal_doc_drafter_agent': 'LegalDocDrafterAgent',
        }
        return mappings.get(tool_name, tool_name.replace('_agent', '').title() + 'Agent')

    def _get_agent_execution_output(self, celery_task_id: str, execution_id: str = None) -> Dict[str, Any]:
        """Enrich job_status with AgentExecution output data — full content, media URLs, deliverables.

        Session 1088: Bridge between Celery task IDs and rich agent outputs.
        Session 1089: Deep extraction for all agent types:
          - ContentWriterAgent: metadata.content.full_text (or metadata.full_text)
          - ImageAgent: metadata.images[*].url
          - VideoAgent/AudioAgent/TalkingCharacterAgent: metadata media URLs
          - Generic: output.content as fallback
        """
        extras: Dict[str, Any] = {}
        try:
            from core.models_unified_system import AgentExecution
            from datetime import timedelta

            execution = None
            if execution_id:
                execution = AgentExecution.objects.filter(id=execution_id).first()
            if not execution:
                execution = AgentExecution.objects.filter(
                    input_data__celery_task_id=celery_task_id,
                ).order_by('-created_at').first()

            if not execution:
                return extras

            extras['agent'] = extras.get('agent') or execution.agent.name
            extras['execution_id'] = str(execution.id)

            output = execution.output_data or {}
            metadata = output.get('metadata', {}) or {}
            if not isinstance(metadata, dict):
                metadata = {}

            # --- Content extraction (deep) ---
            # Priority: metadata.content.full_text > metadata.full_text > output.content
            full_text = ''

            # ContentWriterAgent: result.data = {'content': {'full_text': '...', 'sections': [...]}}
            meta_content = metadata.get('content')
            if isinstance(meta_content, dict):
                full_text = meta_content.get('full_text', '')
            elif isinstance(meta_content, str) and meta_content:
                full_text = meta_content

            # Some agents put full_text directly in metadata
            if not full_text:
                full_text = metadata.get('full_text', '')

            # Fallback: output['content'] (result.message — usually a summary)
            if not full_text:
                full_text = output.get('content', '') or ''

            if full_text:
                extras['content'] = full_text[:3000]
                extras['content_preview'] = full_text[:500]

            # --- Image extraction ---
            images = metadata.get('images', [])
            if isinstance(images, list) and images:
                image_urls = [img.get('url', '') for img in images if isinstance(img, dict) and img.get('url')]
                if image_urls:
                    extras['image_urls'] = image_urls
                    extras['image_url'] = image_urls[0]
                    extras['image_count'] = len(image_urls)

            # --- Direct media URL keys ---
            for key in ('image_url', 'video_url', 'audio_url', 'thumbnail_url',
                        'file_url', 'cloudinary_url', 'final_video_url'):
                val = metadata.get(key)
                if val and key not in extras:
                    extras[key] = val

            # --- Deliverable info from metadata ---
            if metadata.get('deliverable_id'):
                extras['deliverable_id'] = metadata['deliverable_id']
            if metadata.get('deliverable_title'):
                extras['deliverable_title'] = metadata['deliverable_title']

            # --- Deliverable lookup by agent + time window ---
            if not extras.get('deliverable_id'):
                try:
                    from core.models_deliverables import Deliverable
                    end_time = (execution.completed_at or execution.created_at) + timedelta(seconds=30)
                    recent_del = Deliverable.objects.filter(
                        agent_name=execution.agent.name,
                        created_at__gte=execution.created_at - timedelta(seconds=10),
                        created_at__lte=end_time,
                    ).order_by('-created_at').first()
                    if recent_del:
                        extras['deliverable_id'] = str(recent_del.id)
                        extras['deliverable_title'] = recent_del.title
                        # If no content yet, pull from deliverable
                        if not extras.get('content') and recent_del.content:
                            extras['content'] = recent_del.content[:3000]
                            extras['content_preview'] = recent_del.content[:500]
                except Exception:
                    pass

            # --- Image history fallback ---
            if not extras.get('image_url'):
                try:
                    from core.models import ImageHistory
                    recent_img = ImageHistory.objects.filter(
                        created_at__gte=execution.created_at,
                    ).order_by('-created_at').first()
                    if recent_img and hasattr(recent_img, 'file_path') and recent_img.file_path:
                        if recent_img.file_path.startswith('http'):
                            extras['image_url'] = recent_img.file_path
                            if hasattr(recent_img, 'prompt') and recent_img.prompt:
                                extras['image_prompt'] = recent_img.prompt[:200]
                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"_get_agent_execution_output failed: {e}")
        return extras

    def _handle_legal_agent(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1035: Handle legal assistant via AgentRouter.route().
        Session 1062: Made async — dispatches to Celery task to avoid PA tool timeout.
        """
        task_description = payload.get('task') or payload.get('query', '')
        context = payload.get('context', {})

        from core.tasks import draft_legal_document_task
        # Session 1069: Wrap .delay() to handle Redis/broker connection failures gracefully
        try:
            task = draft_legal_document_task.delay(
                task_description=task_description,
                context=context,
                user_id=user_id,
            )
        except Exception as e:
            logger.error(f"[LEGAL] Failed to dispatch Celery task: {e}")
            return {
                'agent': 'LegalDocDrafterAgent',
                'action': 'draft_legal_document',
                'success': False,
                'error': f'Task queue unavailable: {type(e).__name__}. Please try again in a few minutes.',
            }

        return {
            'agent': 'LegalDocDrafterAgent',
            'action': 'draft_legal_document',
            'mode': 'async',
            'task': task_description,
            'task_id': str(task.id),
            'message': (
                'Legal document drafting has been queued. This typically takes '
                '1-3 minutes. Use task_breakdown_tool to check progress.'
            ),
        }

    def _handle_web_search(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle web search tool — synchronous via Serper API."""
        from core.tools.web_search import WebSearchTool

        query = payload.get('query', '')
        search_tool = WebSearchTool()
        result = search_tool.execute(query=query, max_results=5, search_type='text')

        if result.get('success'):
            data = result.get('data', {})
            results = data.get('results', [])
            return {
                'query': query,
                'results': results,
                'total_results': len(results),
                'search_methods_used': data.get('search_methods_used', []),
            }
        return {
            'query': query,
            'results': [],
            'error': result.get('error', 'Search failed'),
        }

    def _handle_opportunity_manager(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle opportunity manager tool.

        NOTE: Session 933 audit - Fixed field names:
        - category → opportunity_type
        - score → match_score
        """
        from core.models_unified_system import Opportunity

        action = payload.get('action', 'list')

        # Build base queryset - filter by user if available
        base_qs = Opportunity.objects.all()
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)

        if action == 'list':
            status = payload.get('status')
            limit = payload.get('limit', 20)

            qs = base_qs
            if status:
                qs = qs.filter(status=status)

            opportunities = list(qs.order_by('-created_at')[:limit].values(
                'id', 'title', 'status', 'opportunity_type', 'match_score', 'created_at'
            ))

            # Session 987: Serialize UUIDs and datetimes for clean display
            for opp in opportunities:
                opp['id'] = str(opp['id'])
                if opp.get('created_at'):
                    opp['created_at'] = opp['created_at'].isoformat()

            return {'action': 'list', 'count': len(opportunities), 'opportunities': opportunities}

        elif action == 'get':
            opp_id = payload.get('opportunity_id') or payload.get('id')
            if not opp_id:
                raise ValueError("opportunity_id is required for get action")
            opp = base_qs.filter(id=opp_id).first()
            if not opp:
                raise ValueError(f"Opportunity {opp_id} not found")
            return {'action': 'get', 'opportunity': {
                'id': str(opp.id), 'title': opp.title, 'status': opp.status,
                'description': opp.description, 'opportunity_type': opp.opportunity_type,
                'match_score': opp.match_score, 'potential_revenue': str(opp.potential_revenue),
            }}

        elif action == 'stats':
            from django.db.models import Count, Sum
            by_status = dict(base_qs.values('status').annotate(c=Count('id')).values_list('status', 'c'))
            by_type = dict(base_qs.values('opportunity_type').annotate(c=Count('id')).values_list('opportunity_type', 'c'))
            total_potential = base_qs.aggregate(total=Sum('potential_revenue'))['total'] or 0
            return {
                'action': 'stats',
                'total': sum(by_status.values()),
                'by_status': by_status,
                'by_type': by_type,
                'total_potential_revenue': str(total_potential),
            }

        # Session 993: Update opportunity status
        elif action == 'update_status':
            opp_id = payload.get('id') or payload.get('opportunity_id')
            new_status = payload.get('status', '')
            valid_statuses = ['active', 'pending', 'applied', 'accepted', 'rejected', 'expired']

            if not opp_id:
                raise ValueError("id is required for update_status action")
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status '{new_status}'. Valid: {', '.join(valid_statuses)}")

            opp = base_qs.filter(id=opp_id).first()
            if not opp:
                raise ValueError(f"Opportunity {opp_id} not found")

            old_status = opp.status
            opp.status = new_status
            opp.save(update_fields=['status'])

            return {
                'action': 'update_status',
                'id': str(opp.id),
                'title': opp.title,
                'old_status': old_status,
                'new_status': new_status,
                'success': True,
            }

        elif action == 'create':
            title = payload.get('title', '').strip()
            if not title:
                raise ValueError("'title' is required for create action")
            if not user_id:
                raise ValueError("User context required to create an opportunity")

            from decimal import Decimal, InvalidOperation
            pot_rev = payload.get('potential_revenue', 0)
            try:
                potential_revenue = Decimal(str(pot_rev))
            except (InvalidOperation, TypeError):
                potential_revenue = Decimal('0')

            opp = Opportunity.objects.create(
                user_id=user_id,
                title=title,
                description=payload.get('description', ''),
                opportunity_type=payload.get('opportunity_type', 'general'),
                source=payload.get('source', 'pa'),
                potential_revenue=potential_revenue,
                status='active',
            )
            return {
                'action': 'create',
                'id': str(opp.id),
                'title': opp.title,
                'opportunity_type': opp.opportunity_type,
                'potential_revenue': str(opp.potential_revenue),
                'status': opp.status,
                'success': True,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, get, stats, update_status, create"
            )

    def _handle_task_manager(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle task manager tool for opportunity-linked tasks."""
        from core.models_unified_system import OpportunityTask

        action = payload.get('action', 'list')

        # Build base queryset - filter by user if available
        base_qs = OpportunityTask.objects.all()
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)

        if action == 'list':
            status = payload.get('status')
            priority = payload.get('priority')
            limit = payload.get('limit', 20)

            qs = base_qs
            if status:
                qs = qs.filter(status=status)
            if priority:
                qs = qs.filter(priority=priority)

            tasks = list(qs.order_by('-created_at')[:limit].values(
                'id', 'title', 'status', 'priority', 'created_at', 'opportunity_id'
            ))

            # Session 987: Serialize UUIDs and datetimes
            for t in tasks:
                t['id'] = str(t['id'])
                if t.get('opportunity_id'):
                    t['opportunity_id'] = str(t['opportunity_id'])
                if t.get('created_at'):
                    t['created_at'] = t['created_at'].isoformat()

            return {'action': 'list', 'count': len(tasks), 'tasks': tasks}

        elif action == 'stats':
            from django.db.models import Count
            by_status = dict(base_qs.values('status').annotate(c=Count('id')).values_list('status', 'c'))
            by_priority = dict(base_qs.values('priority').annotate(c=Count('id')).values_list('priority', 'c'))
            return {
                'action': 'stats',
                'total': sum(by_status.values()),
                'by_status': by_status,
                'by_priority': by_priority,
            }

        elif action == 'create':
            if not user_id:
                raise ValueError("User context required to create a task")
            title = payload.get('title', '').strip()
            if not title:
                raise ValueError("'title' is required for create action")

            opp_id = payload.get('opportunity_id')
            opp = None
            if opp_id:
                from core.models_unified_system import Opportunity
                opp = Opportunity.objects.filter(id=opp_id).first()
                if not opp:
                    raise ValueError(f"Opportunity {opp_id} not found")

            if not opp:
                # Create a standalone opportunity to satisfy the required FK
                from core.models_unified_system import Opportunity
                from decimal import Decimal as _TDecimal
                opp = Opportunity.objects.create(
                    user_id=user_id,
                    title=title,
                    description=payload.get('description', ''),
                    opportunity_type='task',
                    source='pa',
                    potential_revenue=_TDecimal('0'),
                    status='active',
                )

            task = OpportunityTask.objects.create(
                user_id=user_id,
                opportunity=opp,
                title=title,
                description=payload.get('description', ''),
                priority=payload.get('priority', 'medium'),
                status='pending',
            )
            return {
                'action': 'create',
                'id': str(task.id),
                'title': task.title,
                'priority': task.priority,
                'opportunity_id': str(opp.id),
                'success': True,
            }

        elif action == 'update':
            task_id = payload.get('id')
            if not task_id:
                raise ValueError("'id' is required for update action")
            task = base_qs.filter(id=task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")

            update_fields = []
            if payload.get('status'):
                task.status = payload['status']
                update_fields.append('status')
            if payload.get('priority'):
                task.priority = payload['priority']
                update_fields.append('priority')
            if payload.get('title'):
                task.title = payload['title']
                update_fields.append('title')
            if payload.get('description') is not None:
                task.description = payload['description']
                update_fields.append('description')

            if update_fields:
                task.save(update_fields=update_fields)

            return {
                'action': 'update',
                'id': str(task.id),
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'updated_fields': update_fields,
                'success': True,
            }

        elif action == 'complete':
            task_id = payload.get('id')
            if not task_id:
                raise ValueError("'id' is required for complete action")
            task = base_qs.filter(id=task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")

            old_status = task.status
            task.status = 'won'
            task.save(update_fields=['status'])

            return {
                'action': 'complete',
                'id': str(task.id),
                'title': task.title,
                'old_status': old_status,
                'new_status': 'won',
                'success': True,
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid: list, stats, create, update, complete")

    def _handle_pipeline_orchestrator(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle pipeline orchestrator tool.

        NOTE: Session 933 audit - This is a status-only stub.
        The actual pipeline orchestration happens via Celery tasks and
        the Initiative pipeline (5 stages). This tool provides status visibility.
        """
        from core.models import Initiative
        from django.db.models import Count

        action = payload.get('action', 'status')

        if action == 'status':
            # Get real pipeline stats from Initiative model
            # Initiative.status uses UPPERCASE values ('ACTIVE' not 'active')
            total = Initiative.objects.count()
            by_stage = {}
            for stage in range(1, 6):
                by_stage[f'stage_{stage}'] = Initiative.objects.filter(current_stage=stage).count()
            active = Initiative.objects.filter(current_stage__lt=5, status='ACTIVE').count()

            # Add status breakdown for visibility
            by_status = dict(
                Initiative.objects.values('status')
                .annotate(count=Count('id'))
                .values_list('status', 'count')
            )

            return {
                'action': 'status',
                'pipeline': 'operational',
                'initiatives_total': total,
                'initiatives_active': active,
                'by_stage': by_stage,
                'by_status': by_status,
            }

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_revenue_tracker(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle revenue tracker tool.

        NOTE: Session 933 audit - Wired to real Revenue model in core/models.py
        """
        from core.models import Revenue
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'stats')

        # Build base queryset - filter by user if available
        base_qs = Revenue.objects.all()
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)

        if action == 'stats':
            # Get total revenue
            total = base_qs.aggregate(total=Sum('amount'))['total'] or 0

            # Get by source
            by_source = dict(
                base_qs.values('source_type').annotate(
                    total=Sum('amount')
                ).values_list('source_type', 'total')
            )

            # Get by status
            by_status = dict(
                base_qs.values('status').annotate(
                    c=Count('id')
                ).values_list('status', 'c')
            )

            # Get recent (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_total = base_qs.filter(
                created_at__gte=thirty_days_ago
            ).aggregate(total=Sum('amount'))['total'] or 0

            return {
                'action': 'stats',
                'total_revenue': str(total),
                'revenue_last_30_days': str(recent_total),
                'by_source': {k: str(v) for k, v in by_source.items()},
                'by_status': by_status,
                'record_count': base_qs.count(),
            }

        elif action == 'list':
            limit = payload.get('limit', 20)
            revenues = list(base_qs.order_by('-created_at')[:limit].values(
                'id', 'amount', 'source_type', 'status', 'created_at', 'description'
            ))

            # Session 987: Serialize UUIDs and datetimes
            for r in revenues:
                r['id'] = str(r['id'])
                if r.get('created_at'):
                    r['created_at'] = r['created_at'].isoformat()

            return {'action': 'list', 'count': len(revenues), 'revenues': revenues}

        elif action == 'create':
            if not user_id:
                raise ValueError("User context required to create revenue record")

            from decimal import Decimal, InvalidOperation
            try:
                amount = Decimal(str(payload.get('amount', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("'amount' must be a valid number")
            if amount <= 0:
                raise ValueError("'amount' must be positive")

            source_type = payload.get('source', payload.get('source_type', 'other')).strip()
            description = payload.get('description', '').strip()
            status = payload.get('status', 'confirmed')

            rev = Revenue.objects.create(
                user_id=user_id,
                amount=amount,
                source_type=source_type,
                description=description,
                status=status,
            )
            return {
                'action': 'create',
                'id': str(rev.id),
                'amount': str(rev.amount),
                'source_type': rev.source_type,
                'status': rev.status,
                'success': True,
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: stats, list, create")

    def _handle_ml_analysis(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle ML analysis tool.

        NOTE: Session 933 audit - MLEngine doesn't have generic 'analyze' method.
        Available actions: status, decision_pattern, detect_opportunity
        """
        from ml.core.ml_engine import MLEngine

        action = payload.get('action', 'status')

        engine = MLEngine()

        if action == 'status':
            # Get ML engine system health
            health = engine.get_system_health()
            return {
                'action': 'status',
                'engine': 'MLEngine',
                'health': health,
            }

        elif action == 'decision_pattern':
            # Analyze user decision pattern
            decision_data = payload.get('data', {})
            if not decision_data:
                raise ValueError("data is required for decision_pattern analysis")
            confidence = engine.analyze_user_decision_pattern(decision_data)
            return {
                'action': 'decision_pattern',
                'confidence': confidence,
                'data': decision_data,
            }

        elif action == 'detect_opportunity':
            # Detect cross-domain opportunities
            market_data = payload.get('data', {})
            if not market_data:
                raise ValueError("data (market_data) is required for detect_opportunity")
            opportunities = engine.detect_cross_domain_opportunity(market_data)
            return {
                'action': 'detect_opportunity',
                'opportunities': [o.__dict__ for o in opportunities] if opportunities else [],
                'count': len(opportunities) if opportunities else 0,
            }

        else:
            # Return available actions
            return {
                'action': action,
                'error': f"Unknown action: {action}",
                'available_actions': ['status', 'decision_pattern', 'detect_opportunity'],
            }

    def _handle_universal_agent(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle universal agent tool - invoke agent by name or auto-route.

        Session 1088: Converted to Celery async dispatch (same pattern as
        _handle_agent_tool) to eliminate 60s PA timeouts.
        """
        from core.tasks import execute_agent_task
        from core.agent_router import AgentRouter

        agent_name = payload.get('agent_name', '')
        task_text = payload.get('task', '')
        context = payload.get('context', {})

        if not task_text:
            raise ValueError("task is required")

        # GPT often passes tool names (snake_case) instead of agent class names
        if agent_name and '_' in agent_name:
            agent_name = self._tool_to_agent_name(agent_name)

        # Auto-route to best agent when no name given
        if not agent_name:
            router = AgentRouter()
            for name in router.AGENT_MAP:
                if name.lower() in task_text.lower():
                    agent_name = name
                    break
            if not agent_name:
                agent_name = 'ResearchAgent'

        if user_id:
            context['user_id'] = str(user_id)

        celery_task = execute_agent_task.apply_async(args=[agent_name, task_text, context], queue='agents')

        return {
            'task_id': str(celery_task.id),
            'mode': 'async',
            'agent': agent_name,
            'auto_routed': not payload.get('agent_name'),
            'message': (
                f'{agent_name} dispatched (task {celery_task.id}). '
                f'Use job_status to check progress.'
            ),
        }

    def _handle_workspace(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle workspace tool."""
        from core.services.workspace_manager import get_workspace_manager
        from django.contrib.auth import get_user_model

        action = payload.get('action', 'list')
        User = get_user_model()
        user = User.objects.filter(id=user_id).first() if user_id else None
        manager = get_workspace_manager(user)

        if action == 'list':
            workspaces = manager.list_workspaces()
            serialized = []
            for ws in workspaces:
                serialized.append({
                    'id': str(ws.id),
                    'name': ws.name,
                    'description': ws.description or '',
                    'workspace_type': ws.workspace_type,
                    'root_path': ws.root_path,
                    'is_active': ws.is_active,
                    'current_branch': ws.current_branch or '',
                    'total_operations': ws.total_operations,
                    'last_operation_at': ws.last_operation_at.isoformat() if ws.last_operation_at else None,
                })
            return {'action': 'list', 'workspaces': serialized, 'count': len(serialized)}

        elif action == 'status':
            workspaces = manager.list_workspaces()
            active = [ws for ws in workspaces if ws.is_active]
            return {
                'action': 'status',
                'total_workspaces': len(workspaces),
                'active_workspace': {
                    'id': str(active[0].id),
                    'name': active[0].name,
                    'root_path': active[0].root_path,
                    'current_branch': active[0].current_branch or '',
                } if active else None,
            }

        elif action == 'create':
            from core.models_skin_layer import ProjectWorkspace
            import os

            name = payload.get('name', '').strip()
            if not name:
                raise ValueError("'name' is required for create action")

            description = payload.get('description', '')

            # Check for duplicate name
            existing = ProjectWorkspace.objects.filter(user_id=user_id, name=name).first()
            if existing:
                return {
                    'action': 'create',
                    'created': False,
                    'id': str(existing.id),
                    'name': existing.name,
                    'message': f"Workspace '{name}' already exists",
                }

            # Create sandbox workspace (no filesystem path required)
            base_dir = os.environ.get('WORKSPACE_BASE_DIR', '/app/workspaces')
            root_path = os.path.join(base_dir, name.lower().replace(' ', '-'))

            workspace = ProjectWorkspace.objects.create(
                user_id=user_id,
                name=name,
                description=description,
                workspace_type='sandbox',
                root_path=root_path,
                is_active=True,
            )

            return {
                'action': 'create',
                'created': True,
                'id': str(workspace.id),
                'name': workspace.name,
                'description': workspace.description,
                'workspace_type': workspace.workspace_type,
                'message': f"Created workspace '{name}'",
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: list, status, create")

    def _handle_deliverables(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle deliverables library tool."""
        from core.models_deliverables import Deliverable
        from django.db.models import Count

        action = payload.get('action', 'list')
        limit = min(payload.get('limit', 10), 50)
        offset = max(payload.get('offset', 0), 0)

        # Build base queryset scoped to user
        # Session 1075: Include user-owned AND unowned (user=NULL) deliverables.
        # Agents in Celery create deliverables with user=NULL (or the real user
        # after the _save_to_deliverable fix). Include both so PA can always
        # find agent-created content.
        from django.db.models import Q
        base_qs = Deliverable.objects.all()
        if user_id:
            base_qs = base_qs.filter(Q(user_id=user_id) | Q(user__isnull=True))

        def _apply_common_filters(qs):
            """Apply category/agent/type/saved filters."""
            dtype = payload.get('type')
            if dtype:
                qs = qs.filter(deliverable_type=dtype)
            cat = payload.get('category')
            if cat:
                qs = qs.filter(category__iexact=cat)
            agent = payload.get('agent')
            if agent:
                qs = qs.filter(agent_name__iexact=agent)
            if payload.get('saved'):
                qs = qs.filter(is_saved=True)
            return qs

        _LIST_FIELDS = (
            'id', 'title', 'deliverable_type', 'category',
            'agent_name', 'quality_score', 'is_saved', 'created_at',
        )

        def _sanitize_deliverable(d: dict) -> dict:
            """Fill empty deliverable fields with sensible defaults."""
            if not (d.get('title') or '').strip():
                d['title'] = 'Untitled Deliverable'
            if not (d.get('agent_name') or '').strip():
                d['agent_name'] = 'System'
            if not (d.get('category') or '').strip():
                d['category'] = 'General'
            if not (d.get('deliverable_type') or '').strip():
                d['deliverable_type'] = 'document'
            return d

        def _resolve_deliverable(qs, payload, action_name):
            """Resolve a deliverable by id OR title. Returns (obj, None) or (None, error_dict)."""
            did = payload.get('id')
            if did:
                obj = qs.filter(id=did).first()
                if not obj:
                    raise ValueError(f"Deliverable {did} not found")
                return obj, None

            # Fallback: resolve by title
            title_q = payload.get('title', '').strip() or payload.get('query', '').strip()
            if not title_q:
                raise ValueError(f"id or title required for {action_name} action")

            # Try exact match first, then partial
            matches = qs.filter(title__iexact=title_q)
            if not matches.exists():
                matches = qs.filter(title__icontains=title_q)

            count = matches.count()
            if count == 0:
                raise ValueError(f'No deliverable found matching "{title_q}"')
            if count == 1:
                return matches.first(), None
            # Multiple matches — return disambiguation list
            items = list(
                matches.order_by('-created_at')[:10]
                .values('id', 'title', 'deliverable_type', 'created_at')
            )
            return None, {
                'action': action_name,
                'error': 'multiple_matches',
                'message': f'Found {count} deliverables matching "{title_q}". Please specify which one by id or a more specific title.',
                'matches': items,
            }

        if action == 'list':
            qs = _apply_common_filters(base_qs)
            total = qs.count()

            items = [
                _sanitize_deliverable(d) for d in
                qs.order_by('-created_at')[offset:offset + limit].values(*_LIST_FIELDS)
            ]
            return {
                'action': 'list', 'total': total, 'offset': offset,
                'limit': limit, 'count': len(items), 'items': items,
            }

        elif action == 'search':
            query = payload.get('query', '')
            if not query:
                raise ValueError("query parameter required for search action")

            qs = _apply_common_filters(base_qs.filter(title__icontains=query))
            total = qs.count()

            items = [
                _sanitize_deliverable(d) for d in
                qs.order_by('-created_at')[offset:offset + limit].values(*_LIST_FIELDS)
            ]
            return {
                'action': 'search', 'query': query, 'total': total,
                'offset': offset, 'limit': limit, 'count': len(items), 'items': items,
            }

        elif action == 'detail':
            obj, disambiguation = _resolve_deliverable(base_qs, payload, 'detail')
            if disambiguation:
                return disambiguation

            # Emit view event for dashboard tracking
            try:
                from core.models_deliverables import DeliverableEvent
                DeliverableEvent.objects.create(
                    deliverable=obj,
                    event_type='synthesis_viewed',
                    source='pa_tool',
                    metadata={'trace_id': trace_id},
                )
            except Exception:
                pass  # fire-and-forget

            # Session 1086: Return full content so the PA can read
            # deliverables completely. Cap at 8000 chars to stay within
            # reasonable tool-result size for the LLM context window.
            full_content = obj.content or ''
            return _sanitize_deliverable({
                'action': 'detail',
                'id': str(obj.id),
                'title': obj.title,
                'deliverable_type': obj.deliverable_type,
                'category': obj.category,
                'agent_name': obj.agent_name,
                'content_format': obj.content_format,
                'content': full_content[:8000],
                'content_truncated': len(full_content) > 8000,
                'content_preview': full_content[:500],
                'quality_score': obj.quality_score,
                'is_saved': obj.is_saved,
                'is_template': obj.is_template,
                'status': obj.status,
                'tags': obj.tags or [],
                'created_at': obj.created_at.isoformat() if obj.created_at else None,
            })

        elif action == 'save':
            obj, disambiguation = _resolve_deliverable(base_qs, payload, 'save')
            if disambiguation:
                return disambiguation
            obj.is_saved = True
            obj.save(update_fields=['is_saved'])
            try:
                from core.models_deliverables import DeliverableEvent
                DeliverableEvent.objects.create(
                    deliverable=obj, event_type='deliverable_saved',
                    source='pa_tool', metadata={'trace_id': trace_id},
                )
            except Exception:
                pass
            return {'action': 'save', 'id': str(obj.id), 'title': obj.title, 'saved': True}

        elif action == 'unsave':
            obj, disambiguation = _resolve_deliverable(base_qs, payload, 'unsave')
            if disambiguation:
                return disambiguation
            obj.is_saved = False
            obj.save(update_fields=['is_saved'])
            return {'action': 'unsave', 'id': str(obj.id), 'title': obj.title, 'saved': False}

        elif action == 'create':
            # Session 1065: Allow PA to save arbitrary content to Deliverables
            title = payload.get('title', '').strip()
            content = payload.get('content', '').strip()
            if not title or not content:
                raise ValueError("title and content are required for create action")

            import uuid as _d_uuid
            from django.utils.text import slugify as _d_slugify

            content_format = payload.get('content_format', 'markdown')
            dtype = payload.get('type', 'document')
            slug = f"{_d_slugify(title[:100])}-{_d_uuid.uuid4().hex[:8]}"

            # Resolve user
            resolved_user = None
            if user_id:
                from django.contrib.auth import get_user_model
                _DUser = get_user_model()
                try:
                    resolved_user = _DUser.objects.get(id=user_id)
                except _DUser.DoesNotExist:
                    pass

            preview = content[:500]
            if len(content) > 500:
                preview += '...'

            obj = Deliverable.objects.create(
                title=title[:255],
                slug=slug,
                deliverable_type=dtype,
                category='PA Created',
                tags=['pa-created'],
                content=content,
                content_format=content_format,
                preview_content=preview,
                agent_name='PersonalAssistantAgent',
                user=resolved_user,
                quality_score=0.7,
                confidence_score=0.8,
                is_saved=True,
                status='ready',
                metadata={'source': 'pa_deliverables_tool', 'trace_id': trace_id},
            )
            return {
                'action': 'create',
                'id': str(obj.id),
                'title': obj.title,
                'deliverable_type': obj.deliverable_type,
                'saved': True,
                'message': f'Created and saved "{obj.title}" to your Deliverables library.',
            }

        elif action == 'update':
            obj, disambiguation = _resolve_deliverable(base_qs, payload, 'update')
            if disambiguation:
                return disambiguation

            update_fields = []
            if 'title' in payload:
                obj.title = payload['title'].strip()[:255]
                update_fields.append('title')

            # Support prepend/append without requiring full content
            prepend_text = payload.get('prepend', '').strip()
            append_text = payload.get('append', '').strip()
            if prepend_text or append_text:
                current = obj.content or ''
                if prepend_text:
                    current = prepend_text + '\n\n' + current
                if append_text:
                    current = current + '\n\n' + append_text
                obj.content = current
                preview = current[:500]
                if len(current) > 500:
                    preview += '...'
                obj.preview_content = preview
                update_fields.extend(['content', 'preview_content'])
            elif 'content' in payload:
                obj.content = payload['content']
                preview = payload['content'][:500]
                if len(payload['content']) > 500:
                    preview += '...'
                obj.preview_content = preview
                update_fields.extend(['content', 'preview_content'])

            if 'type' in payload:
                obj.deliverable_type = payload['type']
                update_fields.append('deliverable_type')
            if 'content_format' in payload:
                obj.content_format = payload['content_format']
                update_fields.append('content_format')
            if 'tags' in payload:
                obj.tags = [t.strip() for t in payload['tags'].split(',') if t.strip()]
                update_fields.append('tags')

            if not update_fields:
                raise ValueError("update requires at least one of: title, content, prepend, append, type, content_format, tags")

            obj.save(update_fields=update_fields)
            return {
                'action': 'update',
                'id': str(obj.id),
                'title': obj.title,
                'updated_fields': update_fields,
                'message': f'Updated "{obj.title}" ({", ".join(update_fields)}).',
            }

        elif action == 'delete':
            obj, disambiguation = _resolve_deliverable(base_qs, payload, 'delete')
            if disambiguation:
                return disambiguation

            title = obj.title
            del_id = str(obj.id)
            obj.delete()
            return {
                'action': 'delete',
                'id': del_id,
                'title': title,
                'message': f'Permanently deleted "{title}" from your Deliverables library.',
            }

        elif action == 'export_pdf':
            obj, disambiguation = _resolve_deliverable(base_qs, payload, 'export_pdf')
            if disambiguation:
                return disambiguation
            from core.services.pdf_export_service import export_deliverable_to_pdf
            result = export_deliverable_to_pdf(str(obj.id), user_id)
            return result

        elif action == 'stats':
            total = base_qs.count()
            saved = base_qs.filter(is_saved=True).count()
            templates = base_qs.filter(is_template=True).count()
            with_user = base_qs.filter(user__isnull=False).count()
            orphans = base_qs.filter(user__isnull=True).count()
            by_type = dict(
                base_qs.values('deliverable_type')
                .annotate(count=Count('id'))
                .values_list('deliverable_type', 'count')
            )
            by_category = dict(
                base_qs.values('category')
                .annotate(count=Count('id'))
                .order_by('-count')
                .values_list('category', 'count')[:10]
            )
            by_agent = dict(
                base_qs.values('agent_name')
                .annotate(count=Count('id'))
                .order_by('-count')
                .values_list('agent_name', 'count')[:10]
            )
            # Count duplicate excess
            dupe_groups = list(
                base_qs.values('title')
                .annotate(count=Count('id'))
                .filter(count__gt=1)
                .order_by('-count')[:5]
            )
            dupe_excess = sum(d['count'] - 1 for d in dupe_groups)
            return {
                'action': 'stats',
                'total': total,
                'saved': saved,
                'templates': templates,
                'with_user': with_user,
                'orphans': orphans,
                'duplicate_excess': dupe_excess,
                'by_type': by_type,
                'by_category': by_category,
                'by_agent': by_agent,
                'top_duplicates': [
                    {'title': d['title'][:100], 'count': d['count']}
                    for d in dupe_groups
                ],
            }

        elif action == 'cleanup':
            strategy = payload.get('strategy', 'duplicates')
            dry_run = payload.get('dry_run', True)

            if strategy == 'duplicates':
                # Find all titles that appear more than once
                from django.db.models import Max
                dupe_titles = (
                    base_qs.values('title')
                    .annotate(count=Count('id'), newest=Max('created_at'))
                    .filter(count__gt=1)
                )
                # For each duplicate title, keep the newest, mark rest for deletion
                to_delete_ids = []
                summary = []
                for group in dupe_titles:
                    title = group['title']
                    newest_dt = group['newest']
                    # Keep the newest one, delete the rest
                    dupes = list(
                        base_qs.filter(title=title)
                        .exclude(created_at=newest_dt)
                        .values_list('id', flat=True)
                    )
                    # If multiple share the same newest timestamp, keep just one
                    if not dupes:
                        all_ids = list(
                            base_qs.filter(title=title)
                            .order_by('-created_at')
                            .values_list('id', flat=True)
                        )
                        dupes = all_ids[1:]  # keep first (newest), delete rest
                    to_delete_ids.extend(dupes)
                    if len(summary) < 10:
                        summary.append({'title': title[:100], 'deleting': len(dupes), 'keeping': 1})

                if dry_run:
                    return {
                        'action': 'cleanup', 'strategy': 'duplicates', 'dry_run': True,
                        'would_delete': len(to_delete_ids),
                        'sample': summary,
                        'message': f'Would delete {len(to_delete_ids)} duplicate deliverables. Set dry_run=false to execute.',
                    }
                else:
                    deleted_count = Deliverable.objects.filter(id__in=to_delete_ids).delete()[0]
                    return {
                        'action': 'cleanup', 'strategy': 'duplicates', 'dry_run': False,
                        'deleted': deleted_count,
                        'sample': summary,
                        'message': f'Deleted {deleted_count} duplicate deliverables.',
                    }

            elif strategy == 'orphans':
                orphan_qs = base_qs.filter(user__isnull=True, is_saved=False)
                count = orphan_qs.count()
                sample = list(
                    orphan_qs.order_by('-created_at')[:10]
                    .values('id', 'title', 'agent_name', 'category')
                )
                if dry_run:
                    return {
                        'action': 'cleanup', 'strategy': 'orphans', 'dry_run': True,
                        'would_delete': count,
                        'sample': [{'title': s['title'][:100], 'agent': s['agent_name'], 'category': s['category']} for s in sample],
                        'message': f'Would delete {count} orphan deliverables (no user, not saved). Set dry_run=false to execute.',
                    }
                else:
                    deleted_count = orphan_qs.delete()[0]
                    return {
                        'action': 'cleanup', 'strategy': 'orphans', 'dry_run': False,
                        'deleted': deleted_count,
                        'message': f'Deleted {deleted_count} orphan deliverables.',
                    }

            elif strategy == 'low_quality':
                lq_qs = base_qs.filter(quality_score__lt=0.5, is_saved=False)
                count = lq_qs.count()
                sample = list(
                    lq_qs.order_by('quality_score')[:10]
                    .values('id', 'title', 'quality_score', 'agent_name')
                )
                if dry_run:
                    return {
                        'action': 'cleanup', 'strategy': 'low_quality', 'dry_run': True,
                        'would_delete': count,
                        'sample': [{'title': s['title'][:100], 'quality': s['quality_score'], 'agent': s['agent_name']} for s in sample],
                        'message': f'Would delete {count} low-quality deliverables (score < 0.5, not saved). Set dry_run=false to execute.',
                    }
                else:
                    deleted_count = lq_qs.delete()[0]
                    return {
                        'action': 'cleanup', 'strategy': 'low_quality', 'dry_run': False,
                        'deleted': deleted_count,
                        'message': f'Deleted {deleted_count} low-quality deliverables.',
                    }

            else:
                raise ValueError(f"Unknown cleanup strategy: {strategy}. Use 'duplicates', 'orphans', or 'low_quality'.")

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_media(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle media library tool (images, videos, audio)."""
        from content.models import ImageHistory, VideoHistory, AudioHistory
        from django.db.models import Count

        action = payload.get('action', 'list')
        media_type = payload.get('media_type', 'all')
        limit = min(payload.get('limit', 10), 50)

        # Helper to build per-model querysets scoped to user
        def _qs(model):
            qs = model.objects.all()
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs

        if action == 'list':
            content_type = payload.get('content_type')
            items = []

            if media_type in ('image', 'all'):
                qs = _qs(ImageHistory)
                if content_type:
                    qs = qs.filter(image_type=content_type)
                for obj in qs.order_by('-created_at')[:limit]:
                    items.append({
                        'id': str(obj.id), 'media_type': 'image',
                        'filename': obj.filename,
                        'image_type': obj.image_type,
                        'prompt': (obj.prompt or '')[:200],
                        'file_path': obj.file_path,
                        'url': obj.get_full_url(),
                        'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    })

            if media_type in ('video', 'all'):
                qs = _qs(VideoHistory)
                if content_type:
                    qs = qs.filter(video_type=content_type)
                for obj in qs.order_by('-created_at')[:limit]:
                    items.append({
                        'id': str(obj.id), 'media_type': 'video',
                        'video_type': obj.video_type,
                        'prompt': (obj.prompt or '')[:200],
                        'video_url': obj.video_url or '',
                        'thumbnail_url': obj.thumbnail_url or '',
                        'duration': obj.duration,
                        'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    })

            if media_type in ('audio', 'all'):
                qs = _qs(AudioHistory)
                if content_type:
                    qs = qs.filter(audio_type=content_type)
                for obj in qs.order_by('-created_at')[:limit]:
                    items.append({
                        'id': str(obj.id), 'media_type': 'audio',
                        'filename': obj.filename,
                        'audio_type': obj.audio_type,
                        'prompt': (obj.prompt or '')[:200],
                        'voice_name': obj.voice_name or '',
                        'file_path': obj.file_path,
                        'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    })

            # Sort combined results by created_at descending, take limit
            items.sort(key=lambda x: x.get('created_at') or '', reverse=True)
            items = items[:limit]
            return {'action': 'list', 'count': len(items), 'items': items}

        elif action == 'detail':
            mid = payload.get('id')
            if not mid:
                raise ValueError("id parameter required for detail action")

            # Search across all three models
            for model, mtype, extra_fields in [
                (ImageHistory, 'image', lambda o: {
                    'filename': o.filename, 'image_type': o.image_type,
                    'file_path': o.file_path, 'url': o.get_full_url(),
                    'model_used': o.model_used,
                    'style': o.style, 'prompt': o.prompt or '',
                }),
                (VideoHistory, 'video', lambda o: {
                    'video_type': o.video_type, 'video_url': o.video_url or '',
                    'thumbnail_url': o.thumbnail_url or '',
                    'duration': o.duration, 'ratio': o.ratio,
                    'video_width': o.video_width, 'video_height': o.video_height,
                    'model_used': o.model_used, 'prompt': o.prompt or '',
                }),
                (AudioHistory, 'audio', lambda o: {
                    'filename': o.filename, 'audio_type': o.audio_type,
                    'file_path': o.file_path,
                    'url': o.get_full_url() if hasattr(o, 'get_full_url') else o.file_path,
                    'voice_id': o.voice_id,
                    'voice_name': o.voice_name or '', 'prompt': o.prompt or '',
                }),
            ]:
                obj = _qs(model).filter(id=mid).first()
                if obj:
                    result = {
                        'action': 'detail', 'id': str(obj.id),
                        'media_type': mtype,
                        'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    }
                    result.update(extra_fields(obj))
                    return result

            raise ValueError(f"Media asset {mid} not found")

        elif action == 'stats':
            counts = {}
            if media_type in ('image', 'all'):
                counts['images'] = _qs(ImageHistory).count()
            if media_type in ('video', 'all'):
                counts['videos'] = _qs(VideoHistory).count()
            if media_type in ('audio', 'all'):
                counts['audio'] = _qs(AudioHistory).count()
            counts['total'] = sum(counts.values())
            return {'action': 'stats', **counts}

        elif action == 'delete':
            mid = payload.get('id')
            if not mid:
                raise ValueError("id parameter required for delete action")

            for model, mtype in [
                (ImageHistory, 'image'),
                (VideoHistory, 'video'),
                (AudioHistory, 'audio'),
            ]:
                obj = _qs(model).filter(id=mid).first()
                if obj:
                    info = getattr(obj, 'filename', '') or getattr(obj, 'video_url', '') or str(mid)
                    obj.delete()
                    return {
                        'action': 'delete', 'id': str(mid),
                        'media_type': mtype, 'message': f'Deleted {mtype} asset: {info}',
                    }

            raise ValueError(f"Media asset {mid} not found")

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_davinci(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle DaVinci Resolve control surface tool."""
        from core.agents.resolve_agent import ResolveNodeClient

        client = ResolveNodeClient()
        action = payload.get('action', 'health')

        if action == 'health':
            result = client.health_check()
            return {'action': 'health', **result}

        elif action == 'render':
            clip_paths = payload.get('clip_paths')
            if not clip_paths:
                raise ValueError("clip_paths required for render action")
            template = payload.get('template', 'default_mp4')
            timeline_name = payload.get('timeline_name')
            result = client.start_render(
                clip_paths=clip_paths,
                template=template,
                timeline_name=timeline_name,
            )
            return {'action': 'render', **result}

        elif action == 'status':
            job_id = payload.get('job_id')
            if not job_id:
                raise ValueError("job_id required for status action")
            result = client.get_status(job_id)
            return {'action': 'status', **result}

        elif action == 'result':
            job_id = payload.get('job_id')
            if not job_id:
                raise ValueError("job_id required for result action")
            url = client.get_result_url(job_id)
            return {'action': 'result', 'job_id': job_id, 'download_url': url}

        elif action == 'jobs':
            result = client.list_jobs()
            return {'action': 'jobs', **result}

        elif action == 'grades':
            from resolve_node.color_grades import COLOR_GRADE_PRESETS
            grades = [
                {'name': name, 'description': g.get('description', ''), 'use_case': g.get('use_case', '')}
                for name, g in COLOR_GRADE_PRESETS.items()
            ]
            return {'action': 'grades', 'count': len(grades), 'grades': grades}

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_obs(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle OBS recording control tool via platform proxy endpoints."""
        from core.views_obs import _obs_enabled, _obs_bridge_request

        action = payload.get('action', 'health')

        if not _obs_enabled():
            return {'ok': False, 'action': action, 'error': {'code': 'OBS_DISABLED', 'message': 'OBS integration is not enabled'}}

        action_map = {
            'health':      ('GET',  '/health', None, 5),
            'status':      ('GET',  '/v1/recording/status', None, 15),
            'start':       ('POST', '/v1/recording/start', None, 15),
            'stop':        ('POST', '/v1/recording/stop', None, 15),
            'last':        ('GET',  '/v1/recording/last', None, 15),
        }

        if action == 'upload_last':
            body = {}
            if payload.get('stopIfRecording'):
                body['stopIfRecording'] = True
            if payload.get('title'):
                body['title'] = payload['title']
            if payload.get('tags'):
                body['tags'] = payload['tags']
            status_code, data, latency = _obs_bridge_request(
                'POST', '/v1/recording/upload_last',
                body=body if body else None,
                timeout=60,
            )
        elif action in action_map:
            method, path, body, timeout = action_map[action]
            status_code, data, latency = _obs_bridge_request(method, path, body, timeout)
        else:
            raise ValueError(f"Unknown obs_tool action: {action}")

        if status_code == 0:
            return {'ok': False, 'action': action, 'bridgeReachable': False,
                    'error': {'code': 'BRIDGE_UNREACHABLE', 'message': data.get('error', 'Bridge unreachable')}}
        if status_code == 401:
            return {'ok': False, 'action': action, 'bridgeReachable': True,
                    'error': {'code': 'BRIDGE_AUTH_FAILED', 'message': 'Bridge rejected token'}}

        return {
            'ok': data.get('ok', True),
            'action': action,
            'bridgeReachable': True,
            'latency_ms': latency,
            'result': data,
        }

    def _handle_video_history(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle video history tool — list, search, detail."""
        from content.models import VideoHistory
        from django.db.models import Q

        action = payload.get('action', 'list')
        limit = min(payload.get('limit', 10), 50)

        def _qs():
            qs = VideoHistory.objects.all()
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs

        def _serialize(v):
            return {
                'id': str(v.id),
                'sequential_number': v.get_sequential_number(),
                'title': (v.prompt or '')[:200],
                'original_filename': v.original_filename or '',
                'video_url': v.video_url or '',
                'thumbnail_url': v.thumbnail_url or '',
                'video_type': v.video_type or '',
                'source_type': getattr(v, 'source_type', ''),
                'status': v.status or '',
                'duration': v.duration,
                'resolution': f"{v.video_width}x{v.video_height}" if v.video_width else None,
                'file_size_bytes': v.file_size_bytes,
                'created_at': v.created_at.isoformat() if v.created_at else None,
            }

        if action == 'list':
            qs = _qs()
            if payload.get('video_type'):
                qs = qs.filter(video_type=payload['video_type'])
            if payload.get('status'):
                qs = qs.filter(status=payload['status'])
            else:
                qs = qs.filter(status='completed')
            videos = [_serialize(v) for v in qs.order_by('-created_at')[:limit]]
            return {'action': 'list', 'count': len(videos), 'videos': videos}

        elif action == 'search':
            query = payload.get('query', '')
            if not query:
                raise ValueError("query parameter required for search action")
            qs = _qs().filter(
                Q(prompt__icontains=query) | Q(original_filename__icontains=query)
            ).filter(status='completed')
            videos = [_serialize(v) for v in qs.order_by('-created_at')[:limit]]
            return {'action': 'search', 'query': query, 'count': len(videos), 'videos': videos}

        elif action == 'detail':
            vid = payload.get('id')
            seq = payload.get('sequential_number')
            if not vid and not seq:
                raise ValueError("id or sequential_number required for detail action")
            if vid:
                v = _qs().filter(id=vid).first()
            else:
                # sequential_number is computed, not a DB field — get all user videos ordered by created_at and index
                all_videos = list(_qs().order_by('created_at').values_list('id', flat=True))
                if seq and 1 <= seq <= len(all_videos):
                    v = _qs().filter(id=all_videos[seq - 1]).first()
                else:
                    v = None
            if not v:
                raise ValueError("Video not found")
            detail = _serialize(v)
            detail.update({
                'model_used': v.model_used or '',
                'tags': v.tags,
                'user_notes': v.user_notes or '',
                'is_favorite': v.is_favorite,
                'view_count': v.view_count,
                'download_count': v.download_count,
                'fps': v.fps,
                'codec': v.codec,
                'ratio': v.ratio,
                'view_url': '/video-studio',
            })
            return {'action': 'detail', 'video': detail}

        elif action == 'resolve':
            from core.video_resolver import resolve_video
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id) if user_id else None
            ref = {}
            if payload.get('id'):
                ref['id'] = payload['id']
            elif payload.get('sequential_number'):
                ref['sequential_number'] = payload['sequential_number']
            elif payload.get('query'):
                ref['url'] = payload['query']
            if not ref:
                raise ValueError("Provide id, sequential_number, or query (URL) for resolve")
            resolved = resolve_video(ref, user=user)
            if not resolved:
                raise ValueError("Video not found")
            return {'action': 'resolve', 'video': resolved.to_dict()}

        elif action == 'transcribe':
            from content.models import VideoTranscript
            from core.video_resolver import resolve_video
            from core.tasks import transcribe_video_task
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id) if user_id else None
            ref = {}
            if payload.get('id'):
                ref['id'] = payload['id']
            elif payload.get('sequential_number'):
                ref['sequential_number'] = payload['sequential_number']
            if not ref:
                raise ValueError("Provide id or sequential_number to transcribe")
            resolved = resolve_video(ref, user=user)
            if not resolved:
                raise ValueError("Video not found")
            video = _qs().get(id=resolved.id)
            # Check existing
            existing = VideoTranscript.objects.filter(
                video=video, status__in=['queued', 'running']
            ).first()
            if existing:
                return {'action': 'transcribe', 'transcript_id': str(existing.id),
                        'status': existing.status, 'message': 'Already in progress'}
            transcript = VideoTranscript.objects.create(
                video=video, language=payload.get('language', 'en'), status='queued')
            transcribe_video_task.delay(str(transcript.id))
            return {'action': 'transcribe', 'transcript_id': str(transcript.id),
                    'status': 'queued', 'video_title': resolved.title}

        elif action == 'transcript_status':
            from content.models import VideoTranscript
            tid = payload.get('transcript_id')
            if not tid:
                # Get latest for a video
                ref = {}
                if payload.get('id'):
                    ref['id'] = payload['id']
                elif payload.get('sequential_number'):
                    ref['sequential_number'] = payload['sequential_number']
                if ref:
                    from core.video_resolver import resolve_video
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id) if user_id else None
                    resolved = resolve_video(ref, user=user)
                    if resolved:
                        t = VideoTranscript.objects.filter(video_id=resolved.id).order_by('-created_at').first()
                        if t:
                            tid = str(t.id)
                if not tid:
                    raise ValueError("Provide transcript_id, or id/sequential_number of the video")
            t = VideoTranscript.objects.get(id=tid)
            result = {
                'action': 'transcript_status',
                'transcript_id': str(t.id),
                'status': t.status,
                'language': t.language,
                'error': t.error or None,
            }
            if t.status == 'completed':
                result['text'] = t.text[:3000]
                result['text_length'] = len(t.text)
                result['segment_count'] = len(t.segments_json) if t.segments_json else 0
                result['duration_seconds'] = t.duration_seconds
                if len(t.text) > 3000:
                    result['truncated'] = True
            return result

        elif action == 'content_pack':
            from content.models import VideoTranscript
            from core.video_resolver import resolve_video
            from core.tasks import generate_video_content_pack_task
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id) if user_id else None
            ref = {}
            if payload.get('id'):
                ref['id'] = payload['id']
            elif payload.get('sequential_number'):
                ref['sequential_number'] = payload['sequential_number']
            if not ref:
                raise ValueError("Provide id or sequential_number for content_pack")
            resolved = resolve_video(ref, user=user)
            if not resolved:
                raise ValueError("Video not found")
            # Verify transcript exists
            has_transcript = VideoTranscript.objects.filter(
                video_id=resolved.id, status='completed'
            ).exists()
            if not has_transcript:
                raise ValueError("No completed transcript. Transcribe the video first.")
            task = generate_video_content_pack_task.delay(
                resolved.id, str(user_id), payload.get('language', 'en')
            )
            return {
                'action': 'content_pack',
                'task_id': str(task.id),
                'status': 'queued',
                'video_title': resolved.title,
                'message': 'Content pack generation started. Check task status for results.',
            }

        else:
            raise ValueError(f"Unknown video_history_tool action: {action}")

    def _handle_body_vitals(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle body vitals tool."""
        from core.services.body_vitals import get_body_vitals_service

        systems = payload.get('systems', ['all'])
        include_details = payload.get('include_details', False)

        vitals = get_body_vitals_service()

        if 'all' in systems:
            result = vitals.get_all_vitals(include_details=include_details)
        else:
            # get_system_vitals takes one system at a time
            result = {}
            for system_name in systems:
                result[system_name] = vitals.get_system_vitals(
                    system_name, include_details=include_details
                )

        return {
            'systems_requested': systems,
            'vitals': result,
        }

    def _handle_check_budget(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle budget check tool."""
        from core.services.body_vitals import get_body_vitals_service

        estimated_tokens = payload.get('estimated_tokens', 0)
        estimated_cost = payload.get('estimated_cost', 0)

        vitals = get_body_vitals_service()
        budget = vitals.check_budget(estimated_tokens, estimated_cost)

        return {
            'estimated_tokens': estimated_tokens,
            'estimated_cost': estimated_cost,
            'budget_status': budget.get('status', 'unknown'),
            'oxygen_level': budget.get('oxygen_level', 0),
            'can_proceed': budget.get('can_proceed', True),
            'warning': budget.get('warning'),
            'recommendation': budget.get('recommendation'),
        }

    def _handle_system_alerts(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle system alerts tool."""
        from core.services.body_vitals import get_body_vitals_service

        severity_threshold = payload.get('severity_threshold', 'warning')

        vitals = get_body_vitals_service()
        all_vitals = vitals.get_all_vitals()

        alerts = all_vitals.get('alerts', [])

        # Filter by severity
        severity_order = ['info', 'warning', 'critical']
        threshold_idx = severity_order.index(severity_threshold) if severity_threshold in severity_order else 0

        filtered_alerts = [
            a for a in alerts
            if severity_order.index(a.get('severity', 'info')) >= threshold_idx
        ]

        return {
            'severity_threshold': severity_threshold,
            'alert_count': len(filtered_alerts),
            'alerts': filtered_alerts,
        }

    def _handle_cost_telemetry(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1036: Cost telemetry tool — real spend data from LLMCallLog.

        Returns last 24h spend, top agents by cost, cost by task type, trend.
        """
        from core.models_llm_routing import LLMCallLog
        from django.db.models import Sum, Count, Avg, F, Q
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'summary')
        hours = payload.get('hours', 24)
        limit = min(payload.get('limit', 10), 50)

        now = timezone.now()
        cutoff = now - timedelta(hours=hours)

        base_qs = LLMCallLog.objects.filter(created_at__gte=cutoff)

        if action == 'summary':
            # Overall spend summary
            totals = base_qs.aggregate(
                total_cost=Sum('cost'),
                total_calls=Count('id'),
                total_tokens=Sum('total_tokens'),
                avg_latency=Avg('latency_ms'),
                failed_calls=Count('id', filter=Q(success=False)),
            )

            # Cost by provider
            by_provider = list(
                base_qs.values('provider', 'model_id')
                .annotate(
                    spend=Sum('cost'),
                    calls=Count('id'),
                    tokens=Sum('total_tokens'),
                )
                .order_by('-spend')[:10]
            )

            # Cost by task type
            by_task_type = list(
                base_qs.values('task_type')
                .annotate(
                    spend=Sum('cost'),
                    calls=Count('id'),
                )
                .order_by('-spend')[:10]
            )

            # Trend: compare current period to previous same-length period
            prev_cutoff = cutoff - timedelta(hours=hours)
            prev_totals = LLMCallLog.objects.filter(
                created_at__gte=prev_cutoff,
                created_at__lt=cutoff,
            ).aggregate(
                total_cost=Sum('cost'),
                total_calls=Count('id'),
            )

            current_cost = float(totals['total_cost'] or 0)
            prev_cost = float(prev_totals['total_cost'] or 0)
            cost_change_pct = (
                round((current_cost - prev_cost) / prev_cost * 100, 1)
                if prev_cost > 0 else None
            )

            return {
                'action': 'summary',
                'period_hours': hours,
                'total_cost_usd': round(current_cost, 4),
                'total_calls': totals['total_calls'] or 0,
                'total_tokens': totals['total_tokens'] or 0,
                'avg_latency_ms': round(float(totals['avg_latency'] or 0), 0),
                'failed_calls': totals['failed_calls'] or 0,
                'by_provider': [
                    {
                        'provider': r['provider'],
                        'model': r['model_id'],
                        'spend_usd': round(float(r['spend'] or 0), 4),
                        'calls': r['calls'],
                        'tokens': r['tokens'] or 0,
                    }
                    for r in by_provider
                ],
                'by_task_type': [
                    {
                        'task_type': r['task_type'] or 'unknown',
                        'spend_usd': round(float(r['spend'] or 0), 4),
                        'calls': r['calls'],
                    }
                    for r in by_task_type
                ],
                'trend': {
                    'previous_period_cost_usd': round(prev_cost, 4),
                    'cost_change_pct': cost_change_pct,
                },
                'generated_at': now.isoformat(),
            }

        elif action == 'top_agents':
            # Top N agents by cost
            top_agents = list(
                base_qs.values('agent_name')
                .annotate(
                    spend=Sum('cost'),
                    calls=Count('id'),
                    tokens=Sum('total_tokens'),
                    avg_latency=Avg('latency_ms'),
                    failures=Count('id', filter=Q(success=False)),
                )
                .order_by('-spend')[:limit]
            )

            return {
                'action': 'top_agents',
                'period_hours': hours,
                'agents': [
                    {
                        'agent_name': r['agent_name'],
                        'spend_usd': round(float(r['spend'] or 0), 4),
                        'calls': r['calls'],
                        'tokens': r['tokens'] or 0,
                        'avg_latency_ms': round(float(r['avg_latency'] or 0), 0),
                        'failures': r['failures'],
                    }
                    for r in top_agents
                ],
                'generated_at': now.isoformat(),
            }

        elif action == 'recent_calls':
            # Most recent N calls (for debugging)
            recent = list(
                base_qs.order_by('-created_at')
                .values(
                    'agent_name', 'provider', 'model_id', 'task_type',
                    'total_tokens', 'cost', 'latency_ms', 'success',
                    'error_message', 'created_at',
                )[:limit]
            )

            return {
                'action': 'recent_calls',
                'period_hours': hours,
                'calls': [
                    {
                        'agent': r['agent_name'],
                        'provider': r['provider'],
                        'model': r['model_id'],
                        'task_type': r['task_type'],
                        'tokens': r['total_tokens'],
                        'cost_usd': round(float(r['cost'] or 0), 6),
                        'latency_ms': r['latency_ms'],
                        'success': r['success'],
                        'error': r['error_message'][:200] if r['error_message'] else None,
                        'at': r['created_at'].isoformat() if r['created_at'] else None,
                    }
                    for r in recent
                ],
                'generated_at': now.isoformat(),
            }

        else:
            return {'error': f'Unknown action: {action}. Supported: summary, top_agents, recent_calls'}

    def _handle_predictions(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle predictions tool.

        NOTE: AgentPrediction model is DEPRECATED (Session 284).
        This handler returns deprecation notice instead of querying dead model.
        """
        action = payload.get('action', 'list')

        # Return deprecation notice for all actions
        return {
            'action': action,
            'deprecated': True,
            'message': (
                'AgentPrediction is deprecated (Session 284). '
                'No predictions have ever been recorded. '
                'Use HumanAttentionItem for tracking opportunities and decisions instead.'
            ),
            'count': 0,
            'predictions': [],
        }

    def _handle_gates(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle gates tool.

        NOTE: Session 933 audit - PilotReadinessGate has no 'name' field.
        Uses 'summary' and 'decision__topic' instead.
        """
        from core.models_pilot_readiness import PilotReadinessGate

        action = payload.get('action', 'list')
        # Session G3: Alias 'details' -> 'detail'
        ACTION_ALIASES = {'details': 'detail'}
        action = ACTION_ALIASES.get(action, action)
        limit = payload.get('limit', 10)  # Session 1057: Reduced from 20 to match schema

        if action == 'list':
            gates = list(
                PilotReadinessGate.objects.select_related('decision').order_by('-created_at')[:limit].values(
                    'id', 'summary', 'status', 'risk_level', 'created_at', 'decision__topic'
                )
            )
            # Flatten decision__topic to topic for cleaner response
            # Session 987: Serialize UUIDs and datetimes for clean display
            # Session 1057: Truncate summary to prevent GPT-5.2 rendering failure on large results
            for gate in gates:
                gate['topic'] = gate.pop('decision__topic', '')
                gate['id'] = str(gate['id'])
                if gate.get('created_at'):
                    gate['created_at'] = gate['created_at'].isoformat()
                if gate.get('summary') and len(gate['summary']) > 200:
                    gate['summary'] = gate['summary'][:200] + '...'
            return {'action': 'list', 'count': len(gates), 'gates': gates}

        elif action == 'detail':
            gate_id = payload.get('id', '')
            if not gate_id:
                raise ValueError("id is required for detail action")
            gate = PilotReadinessGate.objects.select_related('decision').filter(id=gate_id).first()
            if not gate:
                return {'action': 'detail', 'found': False, 'id': gate_id}
            return {
                'action': 'detail', 'found': True,
                'gate': {
                    'id': str(gate.id),
                    'summary': gate.summary,
                    'status': gate.status,
                    'risk_level': gate.risk_level,
                    'created_at': gate.created_at.isoformat() if gate.created_at else None,
                    'topic': gate.decision.topic if gate.decision else '',
                },
            }

        elif action == 'stats':
            from django.db.models import Count
            total = PilotReadinessGate.objects.count()
            by_status = dict(
                PilotReadinessGate.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')
            )
            by_risk = dict(
                PilotReadinessGate.objects.values('risk_level').annotate(c=Count('id')).values_list('risk_level', 'c')
            )
            return {'action': 'stats', 'total': total, 'by_status': by_status, 'by_risk_level': by_risk}

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_pilots(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle pilots tool - track pilot executions and outcomes."""
        from core.models_pilot_readiness import PilotExecution

        action = payload.get('action', 'list')
        # Session G3: Alias 'details' -> 'detail'
        ACTION_ALIASES = {'details': 'detail'}
        action = ACTION_ALIASES.get(action, action)
        limit = payload.get('limit', 10)  # Session 1057: Reduced from 20 to match schema

        if action == 'detail':
            pilot_id = payload.get('id', '')
            if not pilot_id:
                raise ValueError("id is required for detail action")
            pilot = PilotExecution.objects.filter(id=pilot_id).first()
            if not pilot:
                return {'action': 'detail', 'found': False, 'id': pilot_id}
            return {
                'action': 'detail', 'found': True,
                'pilot': {
                    'id': str(pilot.id),
                    'name': pilot.name,
                    'status': pilot.status,
                    'outcome': pilot.outcome,
                    'created_at': pilot.created_at.isoformat() if pilot.created_at else None,
                },
            }

        elif action == 'list':
            pilots = list(
                PilotExecution.objects.order_by('-created_at')[:limit].values(
                    'id', 'name', 'status', 'outcome', 'created_at'
                )
            )
            # Session 987: Serialize UUIDs and datetimes for clean display
            # Session 1057: Truncate name to prevent GPT-5.2 rendering failure
            for pilot in pilots:
                pilot['id'] = str(pilot['id'])
                if pilot.get('created_at'):
                    pilot['created_at'] = pilot['created_at'].isoformat()
                if pilot.get('name') and len(pilot['name']) > 150:
                    pilot['name'] = pilot['name'][:150] + '...'
            return {'action': 'list', 'count': len(pilots), 'pilots': pilots}

        elif action == 'running':
            pilots = list(
                PilotExecution.objects.filter(status='running').values(
                    'id', 'name', 'status', 'created_at'
                )
            )
            # Session 987: Serialize UUIDs and datetimes for clean display
            for pilot in pilots:
                pilot['id'] = str(pilot['id'])
                if pilot.get('created_at'):
                    pilot['created_at'] = pilot['created_at'].isoformat()
                if pilot.get('name') and len(pilot['name']) > 150:
                    pilot['name'] = pilot['name'][:150] + '...'
            return {'action': 'running', 'count': len(pilots), 'pilots': pilots}

        elif action == 'stats':
            from django.db.models import Count
            total = PilotExecution.objects.count()
            by_status = dict(
                PilotExecution.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')
            )
            by_outcome = dict(
                PilotExecution.objects.values('outcome').annotate(c=Count('id')).values_list('outcome', 'c')
            )
            return {'action': 'stats', 'total': total, 'by_status': by_status, 'by_outcome': by_outcome}

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_human_decisions(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle human decisions tool.

        NOTE: Session 933 audit - Uses HumanAttentionItem (not HumanDecisionItem which doesn't exist).
        Field mappings: description → summary, feedback → decision_feedback
        """
        from core.models_human_interface import HumanAttentionItem

        action = payload.get('action', 'list')
        limit = payload.get('limit', 10)

        # Build base queryset - filter by user if available
        base_qs = HumanAttentionItem.objects
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)

        if action == 'list':
            items = list(
                base_qs.filter(
                    status__in=['pending', 'viewed']
                ).order_by('-priority_score', '-created_at')[:limit].values(
                    'id', 'title', 'summary', 'urgency', 'item_type', 'created_at',
                    'source_agent', 'ml_recommendation'
                )
            )
            return {'action': 'list', 'count': len(items), 'items': items}

        elif action == 'stats':
            from django.db.models import Count
            total = base_qs.count()
            pending = base_qs.filter(status__in=['pending', 'viewed']).count()
            by_urgency = dict(
                base_qs.filter(status__in=['pending', 'viewed']).values('urgency').annotate(
                    c=Count('id')
                ).values_list('urgency', 'c')
            )
            by_type = dict(
                base_qs.filter(status__in=['pending', 'viewed']).values('item_type').annotate(
                    c=Count('id')
                ).values_list('item_type', 'c')
            )
            return {
                'action': 'stats',
                'total': total,
                'pending': pending,
                'by_urgency': by_urgency,
                'by_type': by_type,
            }

        elif action == 'decide':
            item_id = payload.get('item_id')
            decision = payload.get('decision')
            feedback = payload.get('feedback', '')

            if not item_id or not decision:
                raise ValueError("item_id and decision are required")

            item = base_qs.filter(id=item_id).first()
            if not item:
                raise ValueError(f"Attention item {item_id} not found")

            # Use the model's record_decision method for proper status handling
            item.record_decision(
                decision=decision,
                feedback=feedback,
            )

            return {
                'action': 'decide',
                'item_id': str(item_id),
                'decision': decision,
                'new_status': item.status,
                'success': True,
            }

        elif action == 'create':
            if not user_id:
                raise ValueError("User context required to create a decision request")

            title = payload.get('title', '').strip()
            if not title:
                raise ValueError("'title' is required for create action")

            summary = payload.get('summary', '').strip() or title
            item_type = payload.get('item_type', 'decision')
            urgency = payload.get('urgency', 'medium')

            item = HumanAttentionItem.objects.create(
                user_id=user_id,
                title=title[:200],
                summary=summary,
                item_type=item_type,
                urgency=urgency,
                source_type='pa',
                source_agent='PersonalAssistant',
                status='pending',
            )
            return {
                'action': 'create',
                'id': str(item.id),
                'title': item.title,
                'item_type': item.item_type,
                'urgency': item.urgency,
                'success': True,
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid: list, stats, decide, create")

    def _handle_reasoning_engine(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle reasoning engine tool."""
        from core.agents.registry import get_agent_registry

        action = payload.get('action', 'status')

        if action == 'status':
            return {
                'action': 'status',
                'engine': 'ThinkingAgent',
                'status': 'operational',
            }

        elif action == 'thoughts':
            limit = payload.get('limit', 10)
            # Get recent thought cycles from AgentExecution
            from core.models import AgentExecution
            thoughts = list(
                AgentExecution.objects.filter(
                    agent_name='ThinkingAgent'
                ).order_by('-created_at')[:limit].values(
                    'id', 'task', 'success', 'created_at'
                )
            )
            # Session 987: Serialize UUIDs and datetimes for clean display
            for thought in thoughts:
                thought['id'] = str(thought['id'])
                if thought.get('created_at'):
                    thought['created_at'] = thought['created_at'].isoformat()
            return {'action': 'thoughts', 'count': len(thoughts), 'thoughts': thoughts}

        elif action == 'trigger':
            # Trigger a new thinking cycle
            # Session 948: Use execute_agent instead of calling .run() on metadata dict
            registry = get_agent_registry()
            agent_metadata = registry.get_agent('ThinkingAgent')
            if agent_metadata:
                task_data = {'task': "Reflect on recent system activity and generate insights"}
                result = registry.execute_agent('ThinkingAgent', task_data)
                return {
                    'action': 'trigger',
                    'triggered': True,
                    'output': result if result else 'Thinking cycle triggered',
                }
            else:
                return {'action': 'trigger', 'triggered': False, 'error': 'ThinkingAgent not found'}

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_boardroom(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 940: Comprehensive boardroom tool for PA to act on pending items.

        Actions:
        - stats: Get overall boardroom statistics
        - list_attention: List pending attention items
        - list_decisions: List draft decisions
        - approve_attention: Approve an attention item (id required)
        - ignore_attention: Ignore an attention item (id required)
        - promote_decision: Promote a draft decision to canonical (id required)
        - reject_decision: Reject a draft decision (id required)
        """
        from core.models_human_interface import HumanAttentionItem
        from core.models_unified_system import AgentDecisionSummary
        from django.db.models import Count

        action = payload.get('action', 'stats')
        limit = payload.get('limit', 10)
        item_type_filter = payload.get('item_type')
        decision_type_filter = payload.get('decision_type')
        urgency_filter = payload.get('urgency')

        # Build base querysets - filter by user if available
        attention_qs = HumanAttentionItem.objects.filter(status='pending')
        if user_id:
            attention_qs = attention_qs.filter(user_id=user_id)

        decisions_qs = AgentDecisionSummary.objects.filter(status='draft')

        if action == 'stats':
            # Get attention item stats
            attention_count = attention_qs.count()
            attention_by_urgency = dict(
                attention_qs.values('urgency')
                .annotate(count=Count('id'))
                .values_list('urgency', 'count')
            )
            attention_by_type = dict(
                attention_qs.values('item_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('item_type', 'count')
            )

            # Session 985: Fetch top critical/high items so PA can reference
            # actual items instead of just counts
            top_items = list(
                attention_qs.filter(urgency__in=['critical', 'high'])
                .order_by('-priority_score', '-created_at')[:10]
                .values(
                    'id', 'title', 'summary', 'urgency', 'item_type',
                    'source_agent', 'priority_score', 'created_at'
                )
            )

            # Get decision stats
            decision_count = decisions_qs.count()
            decisions_by_type = dict(
                decisions_qs.values('decision_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('decision_type', 'count')
            )

            return {
                'action': 'stats',
                'total_pending': attention_count + decision_count,
                'attention_items': {
                    'count': attention_count,
                    'by_urgency': attention_by_urgency,
                    'by_type': attention_by_type,
                },
                'draft_decisions': {
                    'count': decision_count,
                    'by_type': decisions_by_type,
                },
                'top_items': top_items,
            }

        # Session 1000B: Lookup item by title (for "tell me more about" clicks)
        elif action == 'lookup':
            title_query = payload.get('title_query', '')
            if not title_query:
                return {'action': 'lookup', 'found': False, 'error': 'No title provided'}

            # Search attention items first (most common source of "tell me more")
            item = (
                HumanAttentionItem.objects
                .filter(title__icontains=title_query[:80])
                .order_by('-created_at')
                .first()
            )
            if not item:
                # Broaden: try first few significant words
                words = [w for w in title_query.split() if len(w) > 3][:4]
                if words:
                    from django.db.models import Q
                    q = Q()
                    for w in words:
                        q &= Q(title__icontains=w)
                    item = (
                        HumanAttentionItem.objects
                        .filter(q)
                        .order_by('-created_at')
                        .first()
                    )

            if item:
                return {
                    'action': 'lookup',
                    'found': True,
                    'item_type': 'attention',
                    'title': item.title,
                    'summary': item.summary or '',
                    'urgency': item.urgency or 'medium',
                    'status': item.status,
                    'source_agent': item.source_agent or '',
                    'item_category': item.item_type or '',
                    'created_at': item.created_at.isoformat() if item.created_at else '',
                    'priority_score': item.priority_score,
                    'ml_recommendation': getattr(item, 'ml_recommendation', '') or '',
                    'impact_estimate': getattr(item, 'impact_estimate', '') or '',
                    'payload': item.payload if isinstance(item.payload, dict) else {},
                }

            # Try decisions
            decision = (
                AgentDecisionSummary.objects
                .filter(topic__icontains=title_query[:80])
                .order_by('-created_at')
                .first()
            )
            if decision:
                return {
                    'action': 'lookup',
                    'found': True,
                    'item_type': 'decision',
                    'title': decision.topic,
                    'summary': decision.key_insights or '',
                    'decision_type': decision.decision_type or '',
                    'recommended_stance': decision.recommended_stance or '',
                    'impact_area': decision.impact_area or '',
                    'status': decision.status,
                    'created_at': decision.created_at.isoformat() if decision.created_at else '',
                }

            return {'action': 'lookup', 'found': False, 'query': title_query}

        elif action == 'list_attention':
            # Apply filters
            qs = attention_qs
            if item_type_filter:
                qs = qs.filter(item_type=item_type_filter)
            if urgency_filter:
                qs = qs.filter(urgency=urgency_filter)

            items = list(
                qs.order_by('-priority_score', '-created_at')[:limit].values(
                    'id', 'title', 'summary', 'urgency', 'item_type',
                    'created_at', 'source_agent', 'ml_recommendation',
                    'priority_score', 'ml_confidence', 'impact_estimate'
                )
            )
            return {
                'action': 'list_attention',
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'item_type': item_type_filter,
                    'urgency': urgency_filter,
                }
            }

        elif action == 'list_decisions':
            # Apply filters
            qs = decisions_qs
            if decision_type_filter:
                qs = qs.filter(decision_type=decision_type_filter)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'topic', 'decision_type', 'impact_area',
                    'recommended_stance', 'key_insights', 'created_at'
                )
            )
            return {
                'action': 'list_decisions',
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'decision_type': decision_type_filter,
                }
            }

        elif action == 'approve_attention':
            item_id = payload.get('id')
            feedback = payload.get('feedback', 'Approved via PA')

            if not item_id:
                raise ValueError("id is required for approve_attention")

            item = attention_qs.filter(id=item_id).first()
            if not item:
                raise ValueError(f"Attention item {item_id} not found or not pending")

            # Use the model's record_decision method
            item.record_decision(
                decision='approved',
                feedback=feedback,
            )

            # Session 940: Record for learning
            if user_id:
                try:
                    from core.services.boardroom_learning_service import get_boardroom_learning_service
                    learning_service = get_boardroom_learning_service()
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    learning_service.record_attention_decision(
                        user=user,
                        item_id=str(item_id),
                        decision='approved',
                        source_agent=item.source_agent or 'Unknown',
                        item_type=item.item_type or 'unknown',
                        urgency=item.urgency or 'medium',
                        via='PA'
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning: {e}")

            # Session 1031: Dream approval -> triggers existing signal chain
            if item.source_type == 'dream_pipeline' and item.payload and item.payload.get('dream_id'):
                try:
                    from core.models_unified_system import AgentDream
                    dream = AgentDream.objects.get(id=item.payload['dream_id'])
                    dream.decision_outcome = 'approved'
                    dream.user_reaction = 'loved'
                    dream.user_feedback = feedback
                    dream.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])
                    # post_save signal (dream_signals.py:47) fires automatically:
                    #   1. promote_to_initiative() -> Initiative + Stage 1
                    #   2. execute_single_dream.delay() -> PartnershipProject + workflow
                except Exception as e:
                    logger.warning(f"Dream approval hook failed: {e}")

            return {
                'action': 'approve_attention',
                'id': str(item_id),
                'title': item.title,
                'new_status': item.status,
                'success': True,
            }

        elif action == 'ignore_attention':
            item_id = payload.get('id')
            feedback = payload.get('feedback', 'Ignored via PA')

            if not item_id:
                raise ValueError("id is required for ignore_attention")

            item = attention_qs.filter(id=item_id).first()
            if not item:
                # Session 1075: Idempotent — if item exists but already acted, return success
                already_acted = HumanAttentionItem.objects.filter(id=item_id).first()
                if already_acted:
                    return {
                        'action': 'ignore_attention',
                        'id': str(item_id),
                        'title': already_acted.title,
                        'new_status': already_acted.status,
                        'success': True,
                        'no_op': True,
                        'note': f'Already {already_acted.status}',
                    }
                raise ValueError(f"Attention item {item_id} not found")

            # Use the model's record_decision method
            item.record_decision(
                decision='ignored',
                feedback=feedback,
            )

            # Session 940: Record for learning
            if user_id:
                try:
                    from core.services.boardroom_learning_service import get_boardroom_learning_service
                    learning_service = get_boardroom_learning_service()
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    learning_service.record_attention_decision(
                        user=user,
                        item_id=str(item_id),
                        decision='ignored',
                        source_agent=item.source_agent or 'Unknown',
                        item_type=item.item_type or 'unknown',
                        urgency=item.urgency or 'medium',
                        via='PA'
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning: {e}")

            # Session 1031: Dream dismiss
            if item.source_type == 'dream_pipeline' and item.payload and item.payload.get('dream_id'):
                try:
                    from core.models_unified_system import AgentDream
                    dream = AgentDream.objects.get(id=item.payload['dream_id'])
                    dream.decision_outcome = 'rejected'
                    dream.user_reaction = 'dismissed'
                    dream.user_feedback = feedback
                    dream.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])
                except Exception as e:
                    logger.warning(f"Dream dismiss hook failed: {e}")

            return {
                'action': 'ignore_attention',
                'id': str(item_id),
                'title': item.title,
                'new_status': item.status,
                'success': True,
            }

        elif action == 'promote_decision':
            decision_id = payload.get('id')
            promoted_by = payload.get('promoted_by', 'PA')

            if not decision_id:
                raise ValueError("id is required for promote_decision")

            decision = decisions_qs.filter(id=decision_id).first()
            if not decision:
                raise ValueError(f"Draft decision {decision_id} not found")

            # Promote to canonical
            decision.promote_to_canonical(promoted_by=promoted_by)

            # Session 940: Record for learning
            if user_id:
                try:
                    from core.services.boardroom_learning_service import get_boardroom_learning_service
                    learning_service = get_boardroom_learning_service()
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    learning_service.record_decision_action(
                        user=user,
                        decision_id=str(decision_id),
                        action='promoted',
                        decision_type=decision.decision_type or 'unknown',
                        impact_area=decision.impact_area or 'unknown',
                        via='PA'
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning: {e}")

            return {
                'action': 'promote_decision',
                'id': str(decision_id),
                'topic': decision.topic,
                'new_status': decision.status,
                'is_canonical': decision.is_canonical,
                'success': True,
            }

        elif action == 'reject_decision':
            decision_id = payload.get('id')
            reason = payload.get('reason', 'Rejected via PA')

            if not decision_id:
                raise ValueError("id is required for reject_decision")

            decision = decisions_qs.filter(id=decision_id).first()
            if not decision:
                raise ValueError(f"Draft decision {decision_id} not found")

            # Reject the decision
            decision.status = 'rejected'
            decision.save()

            # Session 940: Record for learning
            if user_id:
                try:
                    from core.services.boardroom_learning_service import get_boardroom_learning_service
                    learning_service = get_boardroom_learning_service()
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    learning_service.record_decision_action(
                        user=user,
                        decision_id=str(decision_id),
                        action='rejected',
                        decision_type=decision.decision_type or 'unknown',
                        impact_area=decision.impact_area or 'unknown',
                        via='PA'
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning: {e}")

            return {
                'action': 'reject_decision',
                'id': str(decision_id),
                'topic': decision.topic,
                'new_status': decision.status,
                'reason': reason,
                'success': True,
            }

        elif action == 'get_triage_batch':
            # Session 940: Get items for triage mode
            from django.db.models import Case, When, IntegerField

            triage_type = payload.get('triage_type', 'attention')
            batch_size = payload.get('batch_size', 5)

            if triage_type == 'attention':
                # Prioritize critical/high urgency
                qs = attention_qs.order_by(
                    Case(
                        When(urgency='critical', then=0),
                        When(urgency='high', then=1),
                        When(urgency='medium', then=2),
                        default=3,
                        output_field=IntegerField()
                    ),
                    '-priority_score',
                    '-created_at'
                )[:batch_size]

                items = []
                for item in qs:
                    items.append({
                        'id': str(item.id),
                        'title': item.title,
                        'summary': item.summary or '',
                        'urgency': item.urgency,
                        'item_type': item.item_type,
                        'source_agent': item.source_agent or 'System',
                        'ml_recommendation': item.ml_recommendation,
                        'created_at': item.created_at.isoformat() if item.created_at else None,
                    })

                return {
                    'action': 'get_triage_batch',
                    'triage_type': 'attention',
                    'count': len(items),
                    'total_remaining': attention_qs.count(),
                    'items': items,
                }

            elif triage_type == 'decisions':
                qs = decisions_qs.order_by('-created_at')[:batch_size]

                items = []
                for item in qs:
                    items.append({
                        'id': str(item.id),
                        'topic': item.topic,
                        'decision_type': item.decision_type,
                        'impact_area': item.impact_area,
                        'recommended_stance': item.recommended_stance[:200] if item.recommended_stance else '',
                        'key_insights': item.key_insights[:3] if item.key_insights else [],
                        'created_at': item.created_at.isoformat() if item.created_at else None,
                    })

                return {
                    'action': 'get_triage_batch',
                    'triage_type': 'decisions',
                    'count': len(items),
                    'total_remaining': decisions_qs.count(),
                    'items': items,
                }

            else:
                raise ValueError(f"Invalid triage_type: {triage_type}. Use 'attention' or 'decisions'")

        # Session 1070: Decision gate actions
        elif action == 'list_unclassified':
            from core.models_conversation_artifacts import ExtractedArtifact
            artifacts = ExtractedArtifact.objects.filter(
                status='pending',
                classified=False,
                composite_score__gte=0.4,
            ).order_by('-composite_score')[:limit]

            items = []
            for a in artifacts:
                items.append({
                    'id': str(a.id),
                    'title': a.title,
                    'type': a.artifact_type,
                    'description': a.description[:200],
                    'composite_score': a.composite_score,
                    'source_agent': a.source_agent.name if a.source_agent else None,
                    'extracted_at': a.extracted_at.isoformat() if a.extracted_at else None,
                })

            return {
                'action': 'list_unclassified',
                'count': len(items),
                'items': items,
                'note': 'These artifacts need classification before they can be approved. '
                        'Each needs: what_is_this, who_is_it_for, data_allowed, phase_approved.',
            }

        elif action == 'classify_suggest':
            from core.models_conversation_artifacts import ExtractedArtifact
            artifact_id = payload.get('artifact_id') or payload.get('id')
            if not artifact_id:
                raise ValueError("artifact_id is required for classify_suggest")

            artifact = ExtractedArtifact.objects.select_related('source_agent').get(id=artifact_id)
            title_lower = artifact.title.lower()
            desc_lower = artifact.description.lower()

            # Deterministic heuristic for what_is_this
            if artifact.artifact_type == 'risk':
                what_is_this = 'risk_flag'
            elif artifact.artifact_type == 'insight':
                what_is_this = 'informational'
            elif artifact.artifact_type in ('proposal', 'action_item'):
                what_is_this = 'actionable_recommendation'
            elif artifact.artifact_type == 'experiment':
                what_is_this = 'research_finding'
            elif any(w in title_lower for w in ['scope', 'expand', 'pivot', 'redesign']):
                what_is_this = 'scope_change'
            else:
                what_is_this = 'research_finding'

            # who_is_it_for heuristic
            if any(w in desc_lower for w in ['user', 'customer', 'subscriber']):
                who_is_it_for = 'end_users'
            elif any(w in desc_lower for w in ['platform', 'system', 'infra', 'celery', 'redis']):
                who_is_it_for = 'platform'
            elif any(w in desc_lower for w in ['agent', 'spider', 'ml ']):
                who_is_it_for = 'agents'
            else:
                who_is_it_for = 'founder'

            # data_allowed heuristic
            if any(w in desc_lower for w in ['user data', 'personal', 'private']):
                data_allowed = 'user_data'
            elif any(w in desc_lower for w in ['api', 'external']):
                data_allowed = 'api_data'
            elif any(w in desc_lower for w in ['internal', 'ops']):
                data_allowed = 'internal_ops'
            else:
                data_allowed = 'public_only'

            # phase_approved heuristic
            if artifact.composite_score >= 0.8:
                phase_approved = 'pilot'
            elif artifact.composite_score >= 0.6:
                phase_approved = 'prototype'
            else:
                phase_approved = 'research'

            return {
                'action': 'classify_suggest',
                'artifact_id': str(artifact.id),
                'artifact_title': artifact.title,
                'suggestions': {
                    'what_is_this': what_is_this,
                    'who_is_it_for': who_is_it_for,
                    'data_allowed': data_allowed,
                    'phase_approved': phase_approved,
                },
                'note': 'These are AI suggestions based on heuristics. '
                        'Human must confirm before applying.',
            }

        elif action == 'classify_apply':
            from core.models_conversation_artifacts import ExtractedArtifact
            artifact_id = payload.get('artifact_id') or payload.get('id')
            if not artifact_id:
                raise ValueError("artifact_id is required for classify_apply")

            classification = payload.get('classification', {})
            valid_keys = {'what_is_this', 'who_is_it_for', 'data_allowed', 'phase_approved'}
            filtered = {k: v for k, v in classification.items() if k in valid_keys}
            if not filtered:
                raise ValueError("classification must contain at least one of: what_is_this, who_is_it_for, data_allowed, phase_approved")

            artifact = ExtractedArtifact.objects.get(id=artifact_id)

            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(id=user_id).first() if user_id else None

            artifact.classify(filtered, user=user)

            return {
                'action': 'classify_apply',
                'artifact_id': str(artifact.id),
                'artifact_title': artifact.title,
                'classification': filtered,
                'classified': True,
                'success': True,
            }

        elif action == 'classify_apply_batch':
            from core.models_conversation_artifacts import ExtractedArtifact

            items = payload.get('items', [])
            if not items:
                raise ValueError("items is required: list of {artifact_id, classification}")

            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(id=user_id).first() if user_id else None

            valid_keys = {'what_is_this', 'who_is_it_for', 'data_allowed', 'phase_approved'}
            results = []
            for item in items[:50]:  # Cap at 50 per call
                aid = item.get('artifact_id') or item.get('id')
                classification = item.get('classification', {})
                filtered = {k: v for k, v in classification.items() if k in valid_keys}
                if not aid or not filtered:
                    continue
                try:
                    artifact = ExtractedArtifact.objects.get(id=aid)
                    artifact.classify(filtered, user=user)
                    results.append({'id': str(artifact.id), 'ok': True})
                except ExtractedArtifact.DoesNotExist:
                    results.append({'id': str(aid), 'ok': False, 'error': 'not found'})

            return {
                'action': 'classify_apply_batch',
                'classified_count': sum(1 for r in results if r['ok']),
                'total': len(results),
                'results': results,
                'success': True,
            }

        elif action == 'create_attention':
            if not user_id:
                raise ValueError("User context required to create attention item")

            title = payload.get('title', '').strip()
            if not title:
                raise ValueError("'title' is required for create_attention")

            summary = payload.get('summary', '').strip() or title
            item_type = payload.get('item_type', 'decision')
            urgency = payload.get('urgency', 'medium')

            item = HumanAttentionItem.objects.create(
                user_id=user_id,
                title=title[:200],
                summary=summary,
                item_type=item_type,
                urgency=urgency,
                source_type='pa',
                source_agent='PersonalAssistant',
                status='pending',
            )
            return {
                'action': 'create_attention',
                'id': str(item.id),
                'title': item.title,
                'item_type': item.item_type,
                'urgency': item.urgency,
                'success': True,
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: stats, lookup, list_attention, list_decisions, approve_attention, ignore_attention, promote_decision, reject_decision, get_triage_batch, list_unclassified, classify_suggest, classify_apply, classify_apply_batch, create_attention")

    def _handle_brainstorm(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 943: Brainstorm search tool for accessing Discussion/Panel insights.

        Allows PA and Boardroom to search through past brainstorming conversations
        without creating pending action items.

        Actions:
        - search: Search brainstorming content by query
        - recent: Get recent brainstorming summaries
        - details: Get details of a specific conversation
        - by_category: Get ideas filtered by category
        - stats: Get brainstorming activity statistics
        """
        from core.services.brainstorm_search_service import brainstorm_search_service

        action = payload.get('action', 'search')

        if action == 'search':
            query = payload.get('query', '')
            if not query:
                raise ValueError("query is required for search action")

            days_back = payload.get('days_back', 30)
            limit = payload.get('limit', 10)
            conv_type = payload.get('type')  # 'discussion', 'panel', or None

            result = brainstorm_search_service.search(
                query=query,
                days_back=days_back,
                limit=limit,
                conversation_type=conv_type
            )
            return {'action': 'search', **result}

        elif action == 'recent':
            days = payload.get('days', 7)
            limit = payload.get('limit', 20)

            result = brainstorm_search_service.get_recent_summaries(
                days=days,
                limit=limit
            )
            return {'action': 'recent', **result}

        elif action == 'details':
            conversation_id = payload.get('conversation_id')
            if not conversation_id:
                raise ValueError("conversation_id is required for details action")

            include_full = payload.get('include_full_content', False)

            result = brainstorm_search_service.get_conversation_insights(
                conversation_id=conversation_id,
                include_full_content=include_full
            )
            return {'action': 'details', **result}

        elif action == 'by_category':
            category = payload.get('category', '')
            if not category:
                raise ValueError("category is required for by_category action")

            days_back = payload.get('days_back', 30)
            limit = payload.get('limit', 10)

            result = brainstorm_search_service.get_ideas_by_category(
                category=category,
                days_back=days_back,
                limit=limit
            )
            return {'action': 'by_category', **result}

        elif action == 'list':
            days_back = payload.get('days', 30)
            offset = payload.get('offset', 0)
            limit = min(payload.get('limit', 50), 200)  # cap at 200
            conv_type = payload.get('type')
            status = payload.get('status')
            include_transcript = payload.get('include_transcript', False)

            result = brainstorm_search_service.list_conversations(
                days_back=days_back,
                offset=offset,
                limit=limit,
                conversation_type=conv_type,
                status=status,
                include_transcript=include_transcript,
            )
            return {'action': 'list', **result}

        elif action == 'stats':
            days = payload.get('days', 30)

            result = brainstorm_search_service.get_stats(days=days)
            return {'action': 'stats', **result}

        elif action == 'create':
            topic = payload.get('topic', payload.get('query', '')).strip()
            if not topic:
                raise ValueError("'topic' is required for create action")

            # Dispatch brainstorm via ConversationOrchestrator as a Celery task
            from core.tasks import execute_agent_task
            task = execute_agent_task.apply_async(
                args=['ThinkingAgent', f'Brainstorm and discuss: {topic}',
                      {'user_id': str(user_id) if user_id else None, 'topic': topic}],
                queue='agents',
            )

            return {
                'action': 'create',
                'topic': topic,
                'task_id': str(task.id),
                'mode': 'async',
                'message': f'Brainstorm discussion on "{topic}" dispatched. Use job_status to check progress.',
                'success': True,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, search, recent, details, by_category, stats, create"
            )

    def _record_content_feedback(self, agent_name, action, details, user_id=None):
        """Record PA review outcome as agent feedback for the content feedback loop.

        Creates AgentMemory (type='feedback') so agents see PA decisions
        in future executions, and updates UserAgentLearning for per-user
        personalization.
        """
        try:
            from core.models_unified_system import AgentMemory, Agent, UserAgentLearning
            from django.contrib.auth import get_user_model

            agent = Agent.objects.filter(name=agent_name).first()
            if not agent:
                return

            valence_map = {'publish': 'positive', 'archive': 'negative', 'revise': 'neutral'}
            valence = valence_map.get(action, 'neutral')

            outcome_map = {'publish': 'success', 'archive': 'failure', 'revise': 'partial'}
            outcome = outcome_map.get(action, 'unknown')

            AgentMemory.objects.create(
                agent=agent,
                title=f"PA review: {action} — {details.get('title', 'content')}"[:200],
                content=details.get('feedback_summary', f"Content was {action}ed by the PA."),
                memory_type='feedback',
                valence=valence,
                memory_outcome=outcome,
                importance_score=0.7,
                source_type='task',
                tags=['pa_review', f'action_{action}'],
                safety_class='approved',
            )

            if user_id and action in ('publish', 'archive'):
                User = get_user_model()
                user = User.objects.filter(id=user_id).first()
                if user:
                    learning, _ = UserAgentLearning.objects.get_or_create(
                        user=user,
                        agent_name=agent_name,
                        learning_domain='content_creation',
                    )
                    if action == 'publish':
                        learning.record_success()
                    else:
                        learning.record_failure()

        except Exception as e:
            logger.warning(f"Failed to record content feedback for {agent_name}: {e}")

    def _handle_content_review(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 943: Content review tool for accessing Deliverables awaiting human review.

        Provides PA access to blogs, reports, and other content in 'ready' status.

        Actions:
        - list: List content ready for review
        - stats: Get content review statistics
        - details: Get details of a specific deliverable
        - publish: Mark content as published
        - archive: Archive content (reject)
        """
        from core.models_deliverables import Deliverable
        from django.db.models import Count

        action = payload.get('action', 'list')
        # Session 1075: GPT-5.2 often calls approve/reject instead of publish/archive
        ACTION_ALIASES = {'approve': 'publish', 'reject': 'archive', 'get': 'details'}
        action = ACTION_ALIASES.get(action, action)
        limit = payload.get('limit', 10)
        content_type = payload.get('type')  # blog, document, report, analysis, etc.
        category = payload.get('category')  # Marketing, Development, etc.

        # Session 958: If type is 'blog', query SelfBlog model instead of Deliverable
        # SelfBlog contains actual blog posts (773+ in production)
        if content_type == 'blog':
            return self._handle_blog_query(action, limit, category, payload, user_id)

        # Build base queryset - filter by user if available
        # Session 1075: Include unowned deliverables (same fix as deliverables_tool)
        from django.db.models import Q as _Qcr
        base_qs = Deliverable.objects.all()
        if user_id:
            base_qs = base_qs.filter(_Qcr(user_id=user_id) | _Qcr(user__isnull=True))

        if action == 'list':
            # List content in 'ready' status awaiting review
            qs = base_qs.filter(status='ready')

            if content_type:
                qs = qs.filter(deliverable_type=content_type)
            if category:
                qs = qs.filter(category__icontains=category)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'deliverable_type', 'category',
                    'agent_name', 'quality_score', 'created_at', 'status'
                )
            )

            return {
                'action': 'list',
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'type': content_type,
                    'category': category,
                    'status': 'ready',
                }
            }

        elif action == 'recent':
            # Session 948: List recently created content (any status)
            # For "what content has been created?" type queries
            from django.utils import timezone
            from datetime import timedelta

            period_days = payload.get('days', 7)
            since = timezone.now() - timedelta(days=period_days)

            qs = base_qs.filter(created_at__gte=since)

            if content_type:
                qs = qs.filter(deliverable_type=content_type)
            if category:
                qs = qs.filter(category__icontains=category)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'deliverable_type', 'category',
                    'agent_name', 'quality_score', 'created_at', 'status'
                )
            )

            # Get counts by status
            status_counts = {}
            for item in items:
                s = item.get('status', 'unknown')
                status_counts[s] = status_counts.get(s, 0) + 1

            return {
                'action': 'recent',
                'count': len(items),
                'items': items,
                'period_days': period_days,
                'by_status': status_counts,
            }

        elif action == 'search':
            # Session 1042: Search deliverables + blogs by title keyword
            query = payload.get('query', '')
            if not query:
                raise ValueError("query parameter required for search action")

            # Search Deliverables
            deliverable_items = list(
                base_qs.filter(title__icontains=query)
                .order_by('-created_at')[:limit]
                .values('id', 'title', 'deliverable_type', 'category',
                        'agent_name', 'quality_score', 'created_at', 'status')
            )

            # Also search SelfBlog (where most content lives)
            from core.models_unified_system import SelfBlog
            blog_items = list(
                SelfBlog.objects.filter(title__icontains=query)
                .order_by('-created_at')[:limit]
                .values('id', 'title', 'author', 'category', 'status', 'created_at',
                        'quality_score', 'word_count', 'tone')
            )

            return {
                'action': 'search',
                'query': query,
                'deliverables': {'count': len(deliverable_items), 'items': deliverable_items},
                'blogs': {'count': len(blog_items), 'items': blog_items},
                'total_found': len(deliverable_items) + len(blog_items),
            }

        elif action == 'stats':
            # Get statistics on content requiring review
            ready_count = base_qs.filter(status='ready').count()
            draft_count = base_qs.filter(status='draft').count()
            published_count = base_qs.filter(status='published').count()

            # Session 1030: Also include SelfBlog counts for complete picture
            try:
                from core.models_unified_system import SelfBlog
                blog_total = SelfBlog.objects.filter(category='blog').count()
                blog_published = SelfBlog.objects.filter(category='blog', status='published').count()
                blog_ready = SelfBlog.objects.filter(category='blog', publish_ready=True, status__in=['approved', 'pending_review']).count()
                blog_draft = SelfBlog.objects.filter(category='blog', status='draft').count()
            except Exception:
                blog_total = blog_published = blog_ready = blog_draft = 0

            by_type = dict(
                base_qs.filter(status='ready')
                .values('deliverable_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('deliverable_type', 'count')
            )

            by_category = dict(
                base_qs.filter(status='ready')
                .values('category')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('category', 'count')
            )

            return {
                'action': 'stats',
                'ready_for_review': ready_count,
                'drafts': draft_count,
                'published': published_count,
                'by_type': by_type,
                'by_category': by_category,
                # Session 1030: SelfBlog counts (blogs are in SelfBlog, not Deliverable)
                'blogs': {
                    'total': blog_total,
                    'published': blog_published,
                    'publish_ready': blog_ready,
                    'drafts': blog_draft,
                },
            }

        elif action == 'details':
            deliverable_id = payload.get('id')
            if not deliverable_id:
                raise ValueError("id is required for details action")

            deliverable = base_qs.filter(id=deliverable_id).first()
            if not deliverable:
                return {
                    'action': 'details',
                    'error': f'Deliverable {deliverable_id} not found — it may have been deleted',
                    'status': 'gone',
                }

            return {
                'action': 'details',
                'id': str(deliverable.id),
                'title': deliverable.title,
                'type': deliverable.deliverable_type,
                'category': deliverable.category,
                'status': deliverable.status,
                'agent_name': deliverable.agent_name,
                'quality_score': deliverable.quality_score,
                'confidence_score': deliverable.confidence_score,
                'content_preview': (deliverable.content or '')[:1000],
                'tags': deliverable.tags or [],
                'created_at': deliverable.created_at.isoformat() if deliverable.created_at else None,
            }

        elif action == 'publish':
            deliverable_id = payload.get('id')
            if not deliverable_id:
                raise ValueError("id is required for publish action")

            deliverable = base_qs.filter(id=deliverable_id, status='ready').first()
            if not deliverable:
                raise ValueError(f"Deliverable {deliverable_id} not found or not in ready status")

            deliverable.status = 'published'
            deliverable.save(update_fields=['status', 'updated_at'])

            self._record_content_feedback(
                agent_name=deliverable.agent_name,
                action='publish',
                details={
                    'title': deliverable.title,
                    'feedback_summary': 'Content published — quality met standards.',
                },
                user_id=user_id,
            )

            return {
                'action': 'publish',
                'id': str(deliverable_id),
                'title': deliverable.title,
                'new_status': 'published',
                'success': True,
            }

        elif action == 'archive':
            deliverable_id = payload.get('id')
            feedback = payload.get('feedback', 'Archived via PA')

            if not deliverable_id:
                raise ValueError("id is required for archive action")

            deliverable = base_qs.filter(id=deliverable_id).first()
            if not deliverable:
                raise ValueError(f"Deliverable {deliverable_id} not found")

            deliverable.status = 'archived'
            if deliverable.metadata is None:
                deliverable.metadata = {}
            deliverable.metadata['archive_reason'] = feedback
            deliverable.save(update_fields=['status', 'metadata', 'updated_at'])

            self._record_content_feedback(
                agent_name=deliverable.agent_name,
                action='archive',
                details={
                    'title': deliverable.title,
                    'feedback_summary': f'Content archived — reason: {feedback}',
                },
                user_id=user_id,
            )

            return {
                'action': 'archive',
                'id': str(deliverable_id),
                'title': deliverable.title,
                'new_status': 'archived',
                'success': True,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, details, publish, archive (aliases: approve=publish, reject=archive)"
            )

    def _handle_blog_query(
        self,
        action: str,
        limit: int,
        category: Optional[str],
        payload: Dict[str, Any],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Session 958: Query SelfBlog model for actual blog content.

        SelfBlog contains:
        - 773+ blog posts in production
        - Categories: blog, audit, technical_document, research_brief, etc.
        - Status: draft, pending_review, approved, published

        This allows the PA to answer "What blogs have been written?" accurately.
        """
        from core.models_unified_system import SelfBlog
        from django.db.models import Count

        # Build base queryset for blogs
        base_qs = SelfBlog.objects.filter(category='blog')

        if action == 'list':
            # List blogs ready for review
            qs = base_qs.filter(status__in=['pending_review', 'approved'])
            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'author', 'category', 'status', 'created_at',
                    'quality_score', 'novelty_score', 'structure_score',
                    'content_type', 'publish_ready', 'word_count', 'tone'
                )
            )

            return {
                'action': 'list',
                'source': 'SelfBlog',
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'type': 'blog',
                    'status': 'pending_review or approved',
                }
            }

        elif action == 'recent':
            # Session 958: List recently created blogs (any status)
            from django.utils import timezone
            from datetime import timedelta

            period_days = payload.get('days', 30)
            since = timezone.now() - timedelta(days=period_days)

            qs = base_qs.filter(created_at__gte=since)
            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'author', 'category', 'status', 'created_at',
                    'quality_score', 'novelty_score', 'structure_score',
                    'content_type', 'publish_ready', 'word_count', 'tone'
                )
            )

            # Get counts by status
            status_counts = {}
            for item in items:
                s = item.get('status', 'unknown')
                status_counts[s] = status_counts.get(s, 0) + 1

            # Session 959: Aggregate quality analytics
            from django.db.models import Avg
            aggregates = base_qs.filter(
                created_at__gte=since, quality_score__isnull=False
            ).aggregate(
                avg_quality=Avg('quality_score'),
                avg_novelty=Avg('novelty_score'),
                avg_structure=Avg('structure_score'),
            )
            publish_ready_count = base_qs.filter(
                created_at__gte=since, publish_ready=True
            ).count()

            return {
                'action': 'recent',
                'source': 'SelfBlog',
                'count': len(items),
                'items': items,
                'period_days': period_days,
                'by_status': status_counts,
                'avg_quality': aggregates.get('avg_quality'),
                'avg_novelty': aggregates.get('avg_novelty'),
                'avg_structure': aggregates.get('avg_structure'),
                'publish_ready_count': publish_ready_count,
            }

        elif action == 'search':
            # Session 1042: Search blogs by title keyword (any status)
            query = payload.get('query', '')
            if not query:
                raise ValueError("query parameter required for search action")

            from django.db.models import Q
            status_filter = payload.get('status')
            qs = base_qs.filter(title__icontains=query)
            if status_filter:
                qs = qs.filter(status=status_filter)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'author', 'category', 'status', 'created_at',
                    'quality_score', 'novelty_score', 'structure_score',
                    'content_type', 'publish_ready', 'word_count', 'tone'
                )
            )

            return {
                'action': 'search',
                'source': 'SelfBlog',
                'query': query,
                'count': len(items),
                'items': items,
            }

        elif action == 'stats':
            # Get blog statistics
            from django.db.models import Avg
            total = base_qs.count()
            draft_count = base_qs.filter(status='draft').count()
            pending_count = base_qs.filter(status='pending_review').count()
            approved_count = base_qs.filter(status='approved').count()
            published_count = base_qs.filter(status='published').count()
            publish_ready_count = base_qs.filter(publish_ready=True).count()

            # Session 959: Aggregate quality averages
            quality_aggs = base_qs.filter(quality_score__isnull=False).aggregate(
                avg_quality=Avg('quality_score'),
                avg_novelty=Avg('novelty_score'),
                avg_structure=Avg('structure_score'),
            )

            return {
                'action': 'stats',
                'source': 'SelfBlog',
                'total_blogs': total,
                'by_status': {
                    'draft': draft_count,
                    'pending_review': pending_count,
                    'approved': approved_count,
                    'published': published_count,
                },
                'ready_for_review': pending_count + approved_count,
                'publish_ready_count': publish_ready_count,
                'avg_quality': quality_aggs.get('avg_quality'),
                'avg_novelty': quality_aggs.get('avg_novelty'),
                'avg_structure': quality_aggs.get('avg_structure'),
            }

        elif action == 'details':
            # Get specific blog details
            blog_id = payload.get('id')
            if not blog_id:
                raise ValueError("Blog ID required for details action")

            blog = base_qs.filter(id=blog_id).first()
            if not blog:
                raise ValueError(f"Blog {blog_id} not found")

            # Get content preview (first 500 chars) - SelfBlog uses 'full_text' field
            content_preview = (blog.full_text or '')[:500]
            if len(blog.full_text or '') > 500:
                content_preview += '...'

            blog_detail = {
                'id': str(blog.id),
                'title': blog.title,
                'author': blog.author,
                'status': blog.status,
                'category': blog.category,
                'content_type': blog.content_type,
                'quality_score': blog.quality_score,
                'novelty_score': blog.novelty_score,
                'structure_score': blog.structure_score,
                'publish_ready': blog.publish_ready,
                'gate_notes': blog.gate_notes or '',
                'tone': blog.tone or '',
                'created_at': blog.created_at.isoformat() if blog.created_at else None,
                'content_preview': content_preview,
                'word_count': blog.word_count or 0,
            }

            # Session 1080: Deliberation traceability — surface provenance
            # for blogs created by the ContentDeliberation pipeline
            delib = (blog.stats_snapshot or {}).get('deliberation')
            if delib:
                blog_detail['deliberation'] = {
                    'session_id': delib.get('session_id'),
                    'decision': delib.get('decision'),
                    'claims_count': delib.get('claims_count', 0),
                    'sources_count': delib.get('sources_count', 0),
                    'reviewers': delib.get('reviewers', []),
                    'review_verdicts': delib.get('review_verdicts', []),
                }
                # Gate result is stored on blog fields, not in stats_snapshot
                if blog.quality_score is not None:
                    blog_detail['deliberation']['gate'] = {
                        'quality': blog.quality_score,
                        'novelty': blog.novelty_score,
                        'structure': blog.structure_score,
                        'decision': 'publish' if blog.publish_ready else (
                            'enhance' if blog.status == 'needs_enhancement' else 'internal_only'
                        ),
                        'notes': blog.gate_notes or '',
                    }

            return {
                'action': 'details',
                'source': 'SelfBlog',
                'blog': blog_detail,
            }

        elif action == 'related':
            # Session 971: Find related blogs by initiative, tags, or title keywords
            blog_id = payload.get('id')
            if not blog_id:
                raise ValueError("Blog ID required for related action")

            source = base_qs.filter(id=blog_id).first()
            if not source:
                # Try all categories, not just blog
                source = SelfBlog.objects.filter(id=blog_id).first()
            if not source:
                raise ValueError(f"Blog {blog_id} not found")

            import re as _re

            STOP_WORDS = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'is', 'it', 'its', 'are', 'was', 'were',
                'be', 'been', 'has', 'had', 'have', 'how', 'what', 'when', 'where',
                'who', 'why', 'this', 'that', 'these', 'those', 'not', 'can', 'will',
                'just', 'more', 'also', 'than', 'into', 'over', 'such', 'our', 'your',
            }

            def _title_keywords(title):
                words = _re.findall(r'[a-z]+', (title or '').lower())
                return {w for w in words if len(w) >= 4 and w not in STOP_WORDS}

            from django.db.models import Q
            scored = {}

            # Signal 1: Same initiative
            if source.initiative_id:  # type: ignore[attr-defined]
                siblings = SelfBlog.objects.filter(
                    initiative_id=source.initiative_id  # type: ignore[attr-defined]
                ).exclude(id=blog_id)[:20]
                for b in siblings:
                    scored[b.id] = (1.0, 'same_initiative', b)

            # Signal 2: Tag overlap (Jaccard > 0.3)
            source_tags = set(source.tags or [])
            if source_tags:
                tag_q = Q()
                for tag in source_tags:
                    tag_q |= Q(tags__contains=[tag])
                for b in SelfBlog.objects.filter(tag_q).exclude(id=blog_id).exclude(id__in=scored.keys())[:50]:
                    b_tags = set(b.tags or [])
                    if b_tags:
                        jaccard = len(source_tags & b_tags) / len(source_tags | b_tags)
                        if jaccard > 0.3:
                            scored[b.id] = (jaccard * 0.8, 'tag_overlap', b)

            # Signal 3: Title keyword overlap
            src_kw = _title_keywords(source.title)
            if src_kw:
                kw_q = Q()
                for kw in list(src_kw)[:5]:
                    kw_q |= Q(title__icontains=kw)
                for b in SelfBlog.objects.filter(kw_q).exclude(id=blog_id).exclude(id__in=scored.keys())[:50]:
                    b_kw = _title_keywords(b.title)
                    if b_kw:
                        ratio = len(src_kw & b_kw) / len(src_kw | b_kw)
                        if ratio > 0.15:
                            scored[b.id] = (ratio * 0.5, 'title_keywords', b)

            top = sorted(scored.values(), key=lambda x: x[0], reverse=True)[:limit]

            related = []
            for score, reason, b in top:
                related.append({
                    'id': str(b.id),
                    'title': b.title,
                    'category': getattr(b, 'category', 'blog'),
                    'status': getattr(b, 'status', 'draft'),
                    'word_count': b.word_count or 0,
                    'created_at': b.created_at.isoformat() if b.created_at else None,
                    'quality_score': b.quality_score,
                    'relatedness_score': round(score, 3),
                    'relatedness_reason': reason,
                })

            return {
                'action': 'related',
                'source': 'SelfBlog',
                'blog_id': str(source.id),
                'blog_title': source.title,
                'count': len(related),
                'related': related,
            }

        elif action == 'read':
            # Session 986: Read full blog content by title for analysis
            title = payload.get('title', '')
            section_filter = payload.get('section', '')

            if not title:
                return {
                    'action': 'read',
                    'error': 'No blog title provided. Try: "read the blog titled \'Your Title Here\'"',
                }

            # Search by title (case-insensitive contains)
            blog = base_qs.filter(title__icontains=title).first()
            if not blog:
                # Fall back to all SelfBlog categories, not just 'blog'
                blog = SelfBlog.objects.filter(title__icontains=title).first()
            if not blog:
                return {
                    'action': 'read',
                    'error': f'No blog found matching "{title}".',
                }

            # Build content from structured fields
            sections_data = blog.sections or []  # list of {header, content}
            intro = blog.intro or ''
            conclusion = blog.conclusion or ''

            if section_filter:
                # Extract a specific section
                matched_section = None
                for sec in sections_data:
                    header = sec.get('header', '') or sec.get('title', '')
                    if section_filter.lower() in header.lower():
                        matched_section = sec
                        break

                if matched_section:
                    header = matched_section.get('header', '') or matched_section.get('title', '')
                    content = matched_section.get('content', '')
                    return {
                        'action': 'read',
                        'source': 'SelfBlog',
                        'blog': {
                            'id': str(blog.id),
                            'title': blog.title,
                            'status': blog.status,
                            'quality_score': blog.quality_score,
                            'word_count': blog.word_count or 0,
                            'created_at': blog.created_at.isoformat() if blog.created_at else None,
                        },
                        'section': {
                            'header': header,
                            'content': content,
                        },
                        'total_sections': len(sections_data),
                    }
                else:
                    # Section not found — return available headers
                    headers = [
                        s.get('header', '') or s.get('title', '')
                        for s in sections_data if s.get('header') or s.get('title')
                    ]
                    return {
                        'action': 'read',
                        'source': 'SelfBlog',
                        'blog': {
                            'id': str(blog.id),
                            'title': blog.title,
                        },
                        'error': f'Section "{section_filter}" not found.',
                        'available_sections': headers,
                    }
            else:
                # Return full blog content (all sections)
                full_sections = []
                if intro:
                    full_sections.append({'header': 'Introduction', 'content': intro})
                for sec in sections_data:
                    header = sec.get('header', '') or sec.get('title', '')
                    content = sec.get('content', '')
                    full_sections.append({'header': header, 'content': content})
                if conclusion:
                    full_sections.append({'header': 'Conclusion', 'content': conclusion})

                # Cap total content at ~4000 chars
                total_chars = sum(len(s['content']) for s in full_sections)
                if total_chars > 4000:
                    # Truncate last sections to fit
                    budget = 4000
                    for sec in full_sections:
                        if budget <= 0:
                            sec['content'] = '[truncated]'
                        elif len(sec['content']) > budget:
                            sec['content'] = sec['content'][:budget] + '...'
                            budget = 0
                        else:
                            budget -= len(sec['content'])

                return {
                    'action': 'read',
                    'source': 'SelfBlog',
                    'blog': {
                        'id': str(blog.id),
                        'title': blog.title,
                        'status': blog.status,
                        'quality_score': blog.quality_score,
                        'novelty_score': blog.novelty_score,
                        'structure_score': blog.structure_score,
                        'word_count': blog.word_count or 0,
                        'created_at': blog.created_at.isoformat() if blog.created_at else None,
                    },
                    'sections': full_sections,
                    'total_sections': len(full_sections),
                }

        elif action == 'revise':
            # Session 987: Revise blog using EditorAgent + re-score with PublishGate
            blog_id = payload.get('id')
            if not blog_id:
                raise ValueError("Blog ID required for revise action")

            blog = base_qs.filter(id=blog_id).first()
            if not blog:
                blog = SelfBlog.objects.filter(id=blog_id).first()
            if not blog:
                raise ValueError(f"Blog {blog_id} not found")

            # Capture before scores
            before = {
                'quality': blog.quality_score,
                'novelty': blog.novelty_score,
                'structure': blog.structure_score,
                'publish_ready': blog.publish_ready,
            }

            # If no gate_notes yet, run PublishGate first to generate editorial guidance
            from core.services.publish_gate import PublishGate
            gate = PublishGate()
            if not blog.gate_notes:
                gate.apply_to_blog(blog, save=True)
                blog.refresh_from_db()
                # Update before scores with freshly computed values
                before = {
                    'quality': blog.quality_score,
                    'novelty': blog.novelty_score,
                    'structure': blog.structure_score,
                    'publish_ready': blog.publish_ready,
                }

            # Map gate_notes into EditorAgent focus_areas
            notes_lower = (blog.gate_notes or '').lower()
            focus_areas = []
            if any(kw in notes_lower for kw in ['hook', 'opening', 'intro', 'engagement']):
                focus_areas.append('hooks')
            if any(kw in notes_lower for kw in ['header', 'heading', 'structure', 'section']):
                focus_areas.append('headers')
            if any(kw in notes_lower for kw in ['conclusion', 'cta', 'call to action', 'ending']):
                focus_areas.append('conclusion')
            if any(kw in notes_lower for kw in ['engagement', 'readability', 'audience']):
                focus_areas.append('engagement')
            if not focus_areas:
                focus_areas = ['hooks', 'headers', 'engagement', 'structure', 'conclusion']

            # Run EditorAgent
            from core.agents.editor_agent import EditorAgent
            editor = EditorAgent()
            result = editor.execute(
                task=f"Revise blog based on editorial feedback: {blog.gate_notes}",
                context={
                    'blog_id': str(blog.id),
                    'focus_areas': focus_areas,
                    'save': True,
                },
                scifi_context={},
                spider_context={},
            )

            if not result.success:
                return {
                    'action': 'revise',
                    'error': f"EditorAgent failed: {result.error}",
                    'blog_id': str(blog.id),
                    'title': blog.title,
                }

            # Re-score with PublishGate
            blog.refresh_from_db()
            gate.apply_to_blog(blog, save=True)
            blog.refresh_from_db()

            after = {
                'quality': blog.quality_score,
                'novelty': blog.novelty_score,
                'structure': blog.structure_score,
                'publish_ready': blog.publish_ready,
            }

            self._record_content_feedback(
                agent_name='ContentWriterAgent',
                action='revise',
                details={
                    'title': blog.title,
                    'feedback_summary': (
                        f"Blog revised — before: quality={before.get('quality')}, "
                        f"structure={before.get('structure')}; "
                        f"after: quality={after.get('quality')}, "
                        f"structure={after.get('structure')}. "
                        f"Focus areas: {', '.join(focus_areas)}."
                    ),
                },
                user_id=user_id,
            )

            return {
                'action': 'revise',
                'blog_id': str(blog.id),
                'title': blog.title,
                'before': before,
                'after': after,
                'changes_made': result.data.get('changes_made', []),
                'focus_areas': focus_areas,
                'gate_notes': blog.gate_notes,
                'status': blog.status,
            }

        elif action == 'needs_work':
            # Session 987: List blogs flagged as needing enhancement
            qs = SelfBlog.objects.filter(status='needs_enhancement')
            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'status', 'created_at',
                    'quality_score', 'novelty_score', 'structure_score',
                    'gate_notes', 'word_count',
                )
            )
            return {
                'action': 'needs_work',
                'source': 'SelfBlog',
                'count': len(items),
                'total': qs.count(),
                'items': items,
            }

        elif action == 'batch_enhance':
            # Session 987: Trigger batch enhancement on all needs_enhancement blogs
            from core.agents.editor_agent import enhance_all_needing_enhancement
            results = enhance_all_needing_enhancement(save=True)
            succeeded = [r for r in results if r.get('success')]
            failed = [r for r in results if not r.get('success')]
            return {
                'action': 'batch_enhance',
                'total_processed': len(results),
                'succeeded': len(succeeded),
                'failed': len(failed),
                'details': [
                    {
                        'title': r.get('title', 'Untitled'),
                        'success': r.get('success', False),
                        'changes': r.get('changes', []),
                        'error': r.get('error'),
                    }
                    for r in results[:10]
                ],
            }

        # Session 993: Bulk blog triage — summarize ALL blogs grouped by quality tier
        elif action == 'triage':
            from django.utils import timezone
            from datetime import timedelta

            thirty_days_ago = timezone.now() - timedelta(days=30)

            # Tier 1: Publish-ready — passed gate AND in reviewable status
            tier1_qs = base_qs.filter(
                publish_ready=True,
                status__in=['approved', 'pending_review'],
            ).order_by('-quality_score')
            tier1 = list(tier1_qs.values(
                'id', 'title', 'status', 'quality_score', 'publish_ready',
                'created_at', 'tone', 'word_count',
            ))

            # Tier 2: Needs revision — draft/needs_enhancement, not publish-ready
            tier2_qs = base_qs.filter(
                status__in=['needs_enhancement', 'draft'],
                publish_ready=False,
            ).order_by('-quality_score')
            tier2 = list(tier2_qs.values(
                'id', 'title', 'status', 'quality_score', 'publish_ready',
                'created_at', 'tone', 'word_count',
            ))

            # Tier 3: Archive candidates — old drafts with low quality
            from django.db.models import Q as _Q
            tier3_qs = base_qs.filter(
                status='draft',
                created_at__lt=thirty_days_ago,
            ).filter(
                _Q(quality_score__lt=0.4) | _Q(quality_score__isnull=True)
            ).order_by('quality_score')
            tier3 = list(tier3_qs.values(
                'id', 'title', 'status', 'quality_score', 'publish_ready',
                'created_at', 'tone', 'word_count',
            ))

            # Serialize UUIDs / datetimes
            for tier_list in (tier1, tier2, tier3):
                for item in tier_list:
                    item['id'] = str(item['id'])
                    if item.get('created_at'):
                        item['created_at'] = item['created_at'].isoformat()

            from django.db.models import Avg
            avg_q = base_qs.filter(quality_score__isnull=False).aggregate(avg=Avg('quality_score'))

            return {
                'action': 'triage',
                'source': 'SelfBlog',
                'publish_ready': {'count': len(tier1), 'items': tier1},
                'needs_revision': {'count': len(tier2), 'items': tier2},
                'archive_candidates': {'count': len(tier3), 'items': tier3},
                'avg_quality': round(avg_q['avg'] or 0, 3),
            }

        # Session 993: Publish a single SelfBlog
        elif action == 'publish':
            blog_id = payload.get('id') or payload.get('blog_id')
            if not blog_id:
                raise ValueError("id is required for publish action")

            # Session 998: Enforce PublishGate — only publish_ready blogs
            blog = base_qs.filter(id=blog_id, status__in=['approved', 'pending_review'], publish_ready=True).first()
            if not blog:
                # Check if blog exists but isn't publish-ready
                unpublishable = base_qs.filter(id=blog_id).first()
                if unpublishable and not unpublishable.publish_ready:
                    return {
                        'action': 'publish',
                        'success': False,
                        'error': 'Blog has not passed PublishGate quality checks.',
                        'gate_notes': unpublishable.gate_notes or 'Not yet evaluated',
                        'id': str(unpublishable.id),
                        'title': unpublishable.title,
                        'status': unpublishable.status,
                    }
                raise ValueError(f"Blog {blog_id} not found or not in approved/pending_review status")

            blog.status = 'published'
            blog.save(update_fields=['status'])

            self._record_content_feedback(
                agent_name='BlogWriter',
                action='publish',
                details={
                    'title': blog.title,
                    'feedback_summary': 'Blog published via PA — quality met standards.',
                },
                user_id=user_id,
            )

            return {
                'action': 'publish',
                'id': str(blog.id),
                'title': blog.title,
                'new_status': 'published',
                'success': True,
            }

        # Session 993: Archive a single SelfBlog (sets to draft — safe, reversible)
        elif action == 'archive':
            blog_id = payload.get('id') or payload.get('blog_id')
            feedback = payload.get('feedback', 'Archived via PA')
            if not blog_id:
                raise ValueError("id is required for archive action")

            blog = base_qs.filter(id=blog_id).first()
            if not blog:
                raise ValueError(f"Blog {blog_id} not found")

            blog.status = 'draft'
            blog.publish_ready = False
            blog.save(update_fields=['status', 'publish_ready'])

            self._record_content_feedback(
                agent_name='BlogWriter',
                action='archive',
                details={
                    'title': blog.title,
                    'feedback_summary': f'Blog archived (→draft) via PA — reason: {feedback}',
                },
                user_id=user_id,
            )

            return {
                'action': 'archive',
                'id': str(blog.id),
                'title': blog.title,
                'new_status': 'draft',
                'success': True,
            }

        # Session 993: Batch publish all publish-ready blogs
        elif action == 'batch_publish':
            publish_qs = base_qs.filter(
                publish_ready=True,
                status__in=['approved', 'pending_review'],
            )[:50]

            published = []
            for blog in publish_qs:
                blog.status = 'published'
                blog.save(update_fields=['status'])
                self._record_content_feedback(
                    agent_name='BlogWriter',
                    action='publish',
                    details={
                        'title': blog.title,
                        'feedback_summary': 'Batch-published via PA.',
                    },
                    user_id=user_id,
                )
                published.append({'id': str(blog.id), 'title': blog.title})

            return {
                'action': 'batch_publish',
                'published_count': len(published),
                'items': published,
                'success': True,
            }

        # Session 993: Batch archive old low-quality drafts
        elif action == 'batch_archive':
            from django.utils import timezone
            from datetime import timedelta

            days_old = payload.get('days_old', 30)
            max_quality = payload.get('max_quality', 0.4)
            cutoff = timezone.now() - timedelta(days=days_old)

            from django.db.models import Q as _Q2
            archive_qs = base_qs.filter(
                status='draft',
                created_at__lt=cutoff,
            ).filter(
                _Q2(quality_score__lt=max_quality) | _Q2(quality_score__isnull=True)
            )[:50]

            archived = []
            for blog in archive_qs:
                blog.publish_ready = False
                blog.save(update_fields=['publish_ready'])
                self._record_content_feedback(
                    agent_name='BlogWriter',
                    action='archive',
                    details={
                        'title': blog.title,
                        'feedback_summary': f'Batch-archived via PA (age>{days_old}d, quality<{max_quality}).',
                    },
                    user_id=user_id,
                )
                archived.append({'id': str(blog.id), 'title': blog.title})

            return {
                'action': 'batch_archive',
                'archived_count': len(archived),
                'criteria': {'days_old': days_old, 'max_quality': max_quality},
                'items': archived,
                'success': True,
            }

        else:
            raise ValueError(
                f"Unknown action for blog query: {action}. "
                f"Valid actions: list, recent, stats, details, related, read, revise, "
                f"needs_work, batch_enhance, triage, publish, archive, batch_publish, batch_archive"
            )

    def _handle_generate_blog(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 993: Generate a blog through the V2 deliberation pipeline.
        Session 1057: Always async — blog generation takes 60-300s which exceeds
        the PA tool timeout. Dispatch to Celery and return immediately.
        """
        topic = payload.get('topic')
        tone = payload.get('tone', 'enthusiastic')

        if topic:
            # Session 1057: Dispatch topic-specific blog to Celery
            from core.tasks import generate_blog_with_topic_task
            task = generate_blog_with_topic_task.delay(topic=topic, tone=tone)  # type: ignore[union-attr]

            return {
                'action': 'generate_blog',
                'mode': 'async',
                'topic': topic,
                'tone': tone,
                'task_id': str(task.id),
                'message': f'Blog generation for "{topic}" queued via deliberation pipeline. '
                           f'This typically takes 2-5 minutes. Use task_breakdown_tool to check progress.',
            }
        else:
            # Async — dispatch to Celery for background generation
            from core.tasks import generate_self_blog_deliberation_task
            task = generate_self_blog_deliberation_task.delay(tone=tone)  # type: ignore[union-attr]

            return {
                'action': 'generate_blog',
                'mode': 'async',
                'tone': tone,
                'task_id': str(task.id),
                'message': 'Blog generation queued via deliberation pipeline. '
                           'This typically takes 2-5 minutes. Use task_breakdown_tool to check progress.',
            }

    def _handle_initiative(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 943: Initiative tool for PA access to project pipeline.

        Provides visibility into the 5-stage initiative pipeline.

        Actions:
        - list: List initiatives (with filters for status, stage, purpose, program)
        - stats: Get pipeline overview statistics
        - details: Get full details of a specific initiative
        - action_items: List pending action items across initiatives
        """
        from core.models_document_registry import Initiative, InitiativeActionItem
        from django.db.models import Count, Q

        action = payload.get('action', 'list')
        limit = payload.get('limit', 50)
        offset = payload.get('offset', 0)  # Session 1076: pagination support

        if action == 'list':
            # Build queryset with filters
            qs = Initiative.objects.all()

            # Filter by status (default to ACTIVE)
            status_filter = payload.get('status', 'ACTIVE')
            if status_filter and status_filter != 'all':
                qs = qs.filter(status=status_filter.upper())

            # Filter by stage
            stage_filter = payload.get('stage')
            if stage_filter:
                qs = qs.filter(current_stage=int(stage_filter))

            # Filter by purpose/program — enums removed from schema to stop GPT
            # auto-filling defaults. Apply only when value looks intentional.
            _IGNORED_PURPOSE = ('all', '', 'maintenance')
            _IGNORED_PROGRAM = ('all', '', 'uncategorized')
            purpose_filter = payload.get('purpose', '').strip().lower()
            purpose_applied = purpose_filter not in _IGNORED_PURPOSE
            if purpose_applied:
                qs = qs.filter(purpose=purpose_filter)

            program_filter = payload.get('program', '').strip().lower()
            program_applied = program_filter not in _IGNORED_PROGRAM
            if program_applied:
                qs = qs.filter(program=program_filter)

            # Session 996: Filter by owner
            owner_filter = payload.get('owner')
            if owner_filter:
                if owner_filter == 'me':
                    qs = qs.filter(owner_id=user_id)
                elif owner_filter == 'unowned':
                    qs = qs.filter(owner__isnull=True, owner_agent='')
                else:
                    qs = qs.filter(owner_agent__icontains=owner_filter)

            # Order by priority score (impact*0.4 + urgency*0.2 + confidence*0.2 + revenue*0.2)
            total_count = qs.count()
            items = list(
                qs.order_by('-impact_score', '-urgency', '-created_at')[:limit].values(
                    'id', 'name', 'description', 'status', 'current_stage',
                    'purpose', 'program', 'impact_score', 'urgency',
                    'confidence', 'revenue_potential', 'created_at',
                    'updated_at', 'last_activity_at',
                    'owner_id', 'owner_agent',
                    'human_id', 'seq_id',
                )
            )

            # Session 996: Resolve owner_ids to usernames in bulk
            owner_ids = [i['owner_id'] for i in items if i.get('owner_id')]
            owner_map = {}
            if owner_ids:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                owner_map = dict(
                    User.objects.filter(id__in=owner_ids).values_list('id', 'username')
                )

            # Add action item counts (including critical) + serialize
            for item in items:
                # Session 1065: Trim description in list view — full text via 'details' action
                desc = item.get('description') or ''
                if len(desc) > 200:
                    item['description'] = desc[:200] + '...'
                item['pending_actions'] = InitiativeActionItem.objects.filter(
                    initiative_id=item['id'],
                    status='pending'
                ).count()
                item['critical_actions'] = InitiativeActionItem.objects.filter(
                    initiative_id=item['id'],
                    status='pending',
                    priority='critical'
                ).count()
                # Session 996: Resolve owner to display name
                item['owner'] = (
                    owner_map.get(item.pop('owner_id'))
                    or item.pop('owner_agent', '')
                    or None
                )
                # Session 987: Serialize UUIDs and datetimes
                item['id'] = str(item['id'])
                for dt_field in ('created_at', 'updated_at', 'last_activity_at'):
                    if item.get(dt_field):
                        item[dt_field] = item[dt_field].isoformat()

            return {
                'action': 'list',
                'count': len(items),
                'total_count': total_count,
                'items': items,
                'filters_applied': {
                    'status': status_filter,
                    'stage': stage_filter or '',
                    'purpose': purpose_filter if purpose_applied else '',
                    'program': program_filter if program_applied else '',
                    'owner': owner_filter or '',
                }
            }

        elif action == 'audit':
            from datetime import timedelta
            from django.utils import timezone
            from core.management.commands.consolidate_duplicate_initiatives import (
                find_duplicate_clusters,
            )

            audit_qs = Initiative.objects.all()
            status_filter = payload.get('status', 'all')
            if status_filter and status_filter != 'all':
                audit_qs = audit_qs.filter(status=status_filter.upper())

            total = audit_qs.count()
            cutoff = timezone.now() - timedelta(days=14)

            init_list = list(audit_qs.only(
                'id', 'name', 'status', 'current_stage',
                'last_activity_at', 'created_at', 'purpose', 'program'
            ))

            # Duplicate clustering via Jaccard similarity + BFS (Session 906)
            clusters = find_duplicate_clusters(init_list, threshold=0.6)
            duplicate_ids = set()
            for cluster in clusters:
                for init in cluster[1:]:
                    duplicate_ids.add(init.id)

            # Classify
            real, stalled, noise = [], [], []
            for init in init_list:
                if init.current_stage > 1 or init.last_activity_at:
                    real.append(init)
                elif init.created_at < cutoff:
                    stalled.append(init)
                else:
                    noise.append(init)

            return {
                'action': 'audit',
                'total': total,
                'classification': {
                    'real': {
                        'count': len(real),
                        'items': [{'human_id': i.human_id, 'name': i.name, 'stage': i.current_stage,
                                   'purpose': i.purpose} for i in real[:10]]
                    },
                    'stalled': {
                        'count': len(stalled),
                        'items': [{'human_id': i.human_id, 'name': i.name, 'created_at': str(i.created_at)[:10],
                                   'purpose': i.purpose} for i in stalled[:5]]
                    },
                    'noise': {
                        'count': len(noise),
                        'items': [{'human_id': i.human_id, 'name': i.name} for i in noise[:5]]
                    },
                    'duplicates': {
                        'count': len(duplicate_ids),
                        'cluster_count': len(clusters),
                        'clusters': [
                            {
                                'primary': cluster[0].name,
                                'count': len(cluster),
                                'examples': [c.name[:80] for c in cluster[1:3]]
                            }
                            for cluster in clusters[:10]
                        ]
                    }
                }
            }

        elif action == 'stats':
            # Get pipeline overview
            total = Initiative.objects.count()
            active = Initiative.objects.filter(status='ACTIVE').count()
            triage = Initiative.objects.filter(status='TRIAGE').count()
            completed = Initiative.objects.filter(status='COMPLETED').count()
            on_hold = Initiative.objects.filter(status='ON_HOLD').count()

            # By stage
            by_stage = {}
            for stage in range(1, 6):
                by_stage[f'stage_{stage}'] = Initiative.objects.filter(
                    status='ACTIVE',
                    current_stage=stage
                ).count()

            # By purpose
            by_purpose = dict(
                Initiative.objects.filter(status='ACTIVE')
                .values('purpose')
                .annotate(count=Count('id'))
                .values_list('purpose', 'count')
            )

            # By program
            by_program = dict(
                Initiative.objects.filter(status='ACTIVE')
                .values('program')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
                .values_list('program', 'count')
            )

            # Action items
            pending_actions = InitiativeActionItem.objects.filter(status='pending').count()
            critical_actions = InitiativeActionItem.objects.filter(
                status='pending',
                priority='critical'
            ).count()

            return {
                'action': 'stats',
                'total': total,
                'active': active,
                'triage': triage,
                'completed': completed,
                'on_hold': on_hold,
                'by_stage': by_stage,
                'by_purpose': by_purpose,
                'by_program': by_program,
                'pending_action_items': pending_actions,
                'critical_action_items': critical_actions,
            }

        elif action == 'details':
            initiative_id = payload.get('id')
            name_query = payload.get('name')

            if not initiative_id and not name_query:
                raise ValueError("id or name is required for details action")

            # Session 1043: Support lookup by human_id (INIT-000001) or seq_id number
            if initiative_id:
                id_str = str(initiative_id).strip()
                # Session 1075: Catch non-UUID strings like "pipeline_health"
                if id_str.lower() in ('pipeline_health', 'pipeline-health', 'health'):
                    return {
                        'action': 'details',
                        'error': 'Use pipeline_orchestrator_tool(action="status") for pipeline health',
                        'hint': 'initiative_tool is for individual initiatives, not pipeline overview',
                    }
                if id_str.upper().startswith('INIT-'):
                    initiative = Initiative.objects.filter(human_id__iexact=id_str).first()
                elif id_str.isdigit():
                    initiative = Initiative.objects.filter(seq_id=int(id_str)).first()
                else:
                    try:
                        initiative = Initiative.objects.filter(id=initiative_id).first()
                    except (ValueError, Exception):
                        # Invalid UUID — try name search fallback
                        initiative = Initiative.objects.filter(name__icontains=id_str).first()
            else:
                initiative = Initiative.objects.filter(name__icontains=name_query).first()

            if not initiative:
                raise ValueError(f"Initiative not found")

            # Get action items (Session 1058: include source_stage)
            action_items = list(
                InitiativeActionItem.objects.filter(initiative=initiative)
                .order_by('-priority', 'status', '-created_at')[:10]
                .values('id', 'title', 'status', 'priority', 'due_date', 'assigned_agent', 'source_stage__stage')
            )

            # Session 987: Serialize UUIDs and datetimes
            for ai in action_items:
                ai['id'] = str(ai['id'])
                if ai.get('due_date'):
                    ai['due_date'] = ai['due_date'].isoformat()

            # Get stage info — Session 1021: fixed field names (stage, not stage_number)
            stages = list(
                initiative.stages.all()  # type: ignore[attr-defined]
                .order_by('stage')
                .values('stage', 'status', 'approved_at', 'document_id')
            )

            stage_labels = {1: 'Research Brief', 2: 'Prototype Plan', 3: 'Evaluation Protocol', 4: 'Technical Design', 5: 'Pilot Execution'}
            for s in stages:
                s['stage_name'] = stage_labels.get(s['stage'], f"Stage {s['stage']}")
                if s.get('approved_at'):
                    s['approved_at'] = s['approved_at'].isoformat()
                # Session 1021: Include stage document preview
                if s.get('document_id'):
                    try:
                        from core.models_unified_system import SelfBlog
                        doc = SelfBlog.objects.filter(id=s['document_id']).first()
                        if doc:
                            s['document_title'] = doc.title
                            s['document_preview'] = (doc.full_text or '')[:300]
                            s['document_length'] = len(doc.full_text or '')
                    except Exception:
                        pass
                s['document_id'] = str(s['document_id']) if s.get('document_id') else None

            # Session 996: Resolve owner
            owner_display = initiative.owner_agent or None
            if initiative.owner_id:  # type: ignore[attr-defined]
                owner_display = initiative.owner.username if initiative.owner else None

            return {
                'action': 'details',
                'id': str(initiative.id),
                'human_id': initiative.human_id or None,
                'name': initiative.name,
                'description': initiative.description,
                'status': initiative.status,
                'current_stage': initiative.current_stage,
                'purpose': initiative.purpose,
                'program': initiative.program,
                'impact_score': initiative.impact_score,
                'urgency': initiative.urgency,
                'confidence': initiative.confidence,
                'revenue_potential': initiative.revenue_potential,
                'created_at': initiative.created_at.isoformat() if initiative.created_at else None,
                'owner': owner_display,
                'owner_agent': initiative.owner_agent,
                'stages': stages,
                'action_items': action_items,
                'action_item_count': len(action_items),
            }

        elif action == 'action_items':
            # List pending action items across all initiatives
            # Session 1076: Added priority filter to schema, fixed ordering
            status_filter = payload.get('item_status', 'pending')
            priority_filter = payload.get('priority')

            qs = InitiativeActionItem.objects.select_related('initiative', 'source_stage')

            if status_filter and status_filter != 'all':
                qs = qs.filter(status=status_filter)

            if priority_filter:
                qs = qs.filter(priority=priority_filter)

            # Order by priority (critical > high > medium > low), then newest
            from django.db.models import Case, When, Value, IntegerField
            priority_order = Case(
                When(priority='critical', then=Value(0)),
                When(priority='high', then=Value(1)),
                When(priority='medium', then=Value(2)),
                When(priority='low', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )

            # Session 1076: Total count for pagination
            total_count = qs.count()

            items = []
            for item in qs.annotate(priority_rank=priority_order).order_by('priority_rank', '-created_at')[offset:offset + limit]:
                items.append({
                    'id': str(item.id),
                    'title': item.title,
                    'status': item.status,
                    'priority': item.priority,
                    'due_date': item.due_date.isoformat() if item.due_date else None,
                    'assigned_agent': item.assigned_agent,
                    'initiative_id': str(item.initiative_id),  # type: ignore[attr-defined]
                    'initiative_name': item.initiative.name if item.initiative else 'Unknown',
                    'source_stage': item.source_stage.stage if item.source_stage else None,
                })

            return {
                'action': 'action_items',
                'count': len(items),
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'items': items,
                'filters_applied': {
                    'status': status_filter,
                    'priority': priority_filter,
                }
            }

        # Session 1076: Cleanup junk action items (section headings, labels)
        elif action == 'cleanup_action_items':
            dry_run = payload.get('dry_run', True)
            from core.services.action_item_parser import ActionItemParser

            junk_qs = InitiativeActionItem.objects.filter(status='pending')
            junk_ids = []
            junk_titles = []
            for item in junk_qs.only('id', 'title'):
                if ActionItemParser._is_junk_title(item.title):
                    junk_ids.append(item.id)
                    junk_titles.append(item.title)

            cancelled = 0
            if not dry_run and junk_ids:
                cancelled = InitiativeActionItem.objects.filter(
                    id__in=junk_ids
                ).update(status='cancelled')

            return {
                'action': 'cleanup_action_items',
                'dry_run': dry_run,
                'junk_found': len(junk_ids),
                'cancelled': cancelled,
                'sample_titles': junk_titles[:20],
            }

        # Session 1040: Fetch full stage document content
        elif action == 'stage_document':
            initiative_id = payload.get('id') or payload.get('initiative_id')
            document_id = payload.get('document_id')
            stage_num = payload.get('stage')

            if not initiative_id and not document_id:
                raise ValueError("id (initiative UUID) or document_id is required")

            from core.models_unified_system import SelfBlog

            if document_id:
                doc = SelfBlog.objects.filter(id=document_id).first()
                if not doc:
                    raise ValueError(f"Document {document_id} not found")
            elif initiative_id and stage_num:
                from core.models_document_registry import InitiativeStage as IS
                stage = IS.objects.filter(
                    initiative_id=initiative_id, stage=int(stage_num)
                ).select_related('document').first()
                if not stage:
                    raise ValueError(f"Stage {stage_num} not found for initiative {initiative_id}")
                if not stage.document:
                    raise ValueError(f"Stage {stage_num} has no document attached")
                doc = stage.document
            else:
                raise ValueError("Provide document_id, or both id + stage")

            return {
                'action': 'stage_document',
                'document_id': str(doc.id),
                'title': doc.title,
                'word_count': doc.word_count,
                'status': doc.status,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'intro': doc.intro or '',
                'full_text': doc.full_text or '',
                'sections': doc.sections or [],
                'tags': doc.tags or [],
                'quality_score': doc.quality_score,
                'tone': doc.tone,
            }

        # Session 993: Write actions for initiatives
        elif action == 'update_status':
            initiative_id = payload.get('id') or payload.get('initiative_id')
            new_status = payload.get('status', '').upper()
            valid_statuses = ['ACTIVE', 'TRIAGE', 'ON_HOLD', 'COMPLETED', 'ARCHIVED']

            if not initiative_id:
                raise ValueError("id is required for update_status action")
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status '{new_status}'. Valid: {', '.join(valid_statuses)}")

            initiative = Initiative.objects.filter(id=initiative_id).first()
            if not initiative:
                raise ValueError(f"Initiative {initiative_id} not found")

            old_status = initiative.status
            initiative.status = new_status
            initiative.save(update_fields=['status'])

            # Session 1076: Auto-cancel orphaned action items when initiative is completed
            cancelled_items = 0
            if new_status in ('COMPLETED', 'ARCHIVED') and old_status not in ('COMPLETED', 'ARCHIVED'):
                cancelled_items = InitiativeActionItem.objects.filter(
                    initiative=initiative,
                    status='pending',
                ).update(status='cancelled')
                if cancelled_items:
                    logger.info(f"Auto-cancelled {cancelled_items} pending action items for {new_status} initiative {initiative.name}")

            return {
                'action': 'update_status',
                'id': str(initiative.id),
                'name': initiative.name,
                'old_status': old_status,
                'new_status': new_status,
                'success': True,
                'auto_cancelled_action_items': cancelled_items,
            }

        elif action == 'advance':
            initiative_id = payload.get('id') or payload.get('initiative_id')
            if not initiative_id:
                raise ValueError("id is required for advance action")

            initiative = Initiative.objects.filter(id=initiative_id).first()
            if not initiative:
                raise ValueError(f"Initiative {initiative_id} not found")

            old_stage = initiative.current_stage
            initiative.advance_stage()
            initiative.refresh_from_db()

            return {
                'action': 'advance',
                'id': str(initiative.id),
                'name': initiative.name,
                'old_stage': old_stage,
                'new_stage': initiative.current_stage,
                'success': initiative.current_stage != old_stage,
                'message': (
                    f"Advanced from stage {old_stage} to {initiative.current_stage}"
                    if initiative.current_stage != old_stage
                    else f"Cannot advance — stage {old_stage} is not approved or already at stage 5"
                ),
            }

        elif action == 'start_action_item':
            item_id = payload.get('item_id') or payload.get('id')
            if not item_id:
                raise ValueError("item_id is required for start_action_item action")
            item = InitiativeActionItem.objects.filter(id=item_id).first()
            if not item:
                raise ValueError(f"Action item {item_id} not found")
            item.start(by='human_pa')
            return {
                'action': 'start_action_item',
                'id': str(item.id),
                'title': item.title,
                'status': item.status,
            }

        elif action == 'complete_action_item':
            item_id = payload.get('item_id') or payload.get('id')
            notes = payload.get('notes', '')
            if not item_id:
                raise ValueError("item_id is required for complete_action_item action")

            item = InitiativeActionItem.objects.filter(id=item_id).first()
            if not item:
                raise ValueError(f"Action item {item_id} not found")

            item.complete(by='PA', notes=notes)

            return {
                'action': 'complete_action_item',
                'id': str(item.id),
                'title': item.title,
                'new_status': 'completed',
                'initiative_name': item.initiative.name if item.initiative else 'Unknown',
                'success': True,
            }

        elif action == 'assign_owner':
            # Session 996: Assign ownership of an initiative
            initiative_id = payload.get('id') or payload.get('initiative_id')
            agent_name = payload.get('agent_name', '')
            user_name = payload.get('user_name', '')

            if not initiative_id:
                raise ValueError("id is required for assign_owner action")

            initiative = Initiative.objects.filter(id=initiative_id).first()
            if not initiative:
                raise ValueError(f"Initiative {initiative_id} not found")

            old_owner = initiative.owner_agent or (initiative.owner.username if initiative.owner else None) or 'unowned'

            if agent_name:
                initiative.owner_agent = agent_name
                initiative.owner = None
                initiative.save(update_fields=['owner_agent', 'owner'])
                new_owner = agent_name
            elif user_name:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if user_name == 'me':
                    user = User.objects.filter(id=user_id).first() if user_id else None
                else:
                    user = User.objects.filter(username__iexact=user_name).first()
                if not user:
                    raise ValueError(f"User '{user_name}' not found")
                initiative.owner = user
                initiative.owner_agent = ''
                initiative.save(update_fields=['owner', 'owner_agent'])
                new_owner = user.username  # type: ignore[attr-defined]
            else:
                raise ValueError("agent_name or user_name is required for assign_owner")

            return {
                'action': 'assign_owner',
                'id': str(initiative.id),
                'name': initiative.name,
                'old_owner': old_owner,
                'new_owner': new_owner,
                'success': True,
            }

        elif action == 'promote':
            # Session 1058: Human-in-the-loop promotion from TRIAGE/ON_HOLD → ACTIVE
            initiative_id = payload.get('id') or payload.get('initiative_id')
            if not initiative_id:
                raise ValueError("id is required for promote action")

            # Reuse human_id / seq_id lookup from details action
            id_str = str(initiative_id).strip()
            if id_str.upper().startswith('INIT-'):
                initiative = Initiative.objects.filter(human_id__iexact=id_str).first()
            elif id_str.isdigit():
                initiative = Initiative.objects.filter(seq_id=int(id_str)).first()
            else:
                initiative = Initiative.objects.filter(id=initiative_id).first()

            if not initiative:
                raise ValueError(f"Initiative {initiative_id} not found")

            promotable = {'TRIAGE', 'ON_HOLD'}
            if initiative.status not in promotable:
                raise ValueError(
                    f"Cannot promote: status is {initiative.status}. "
                    f"Only {', '.join(sorted(promotable))} initiatives can be promoted to ACTIVE."
                )

            old_status = initiative.status
            initiative.status = 'ACTIVE'
            initiative.save(update_fields=['status'])

            return {
                'action': 'promote',
                'id': str(initiative.id),
                'human_id': initiative.human_id or None,
                'name': initiative.name,
                'old_status': old_status,
                'new_status': 'ACTIVE',
                'success': True,
                'message': f"Promoted '{initiative.name}' from {old_status} to ACTIVE",
            }

        elif action == 'flow_metrics':
            # Session 994: Initiative pipeline health metrics
            from django.utils import timezone
            from datetime import timedelta
            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)

            # Creation rate
            created_24h = Initiative.objects.filter(created_at__gte=last_24h).count()
            created_7d = Initiative.objects.filter(created_at__gte=last_7d).count()

            # Triage backlog
            triage_count = Initiative.objects.filter(status='TRIAGE').count()
            active_count = Initiative.objects.filter(status='ACTIVE').count()

            # No-activity count (created but never worked on)
            no_activity = Initiative.objects.filter(
                status__in=['ACTIVE', 'TRIAGE'],
                last_activity_at__isnull=True,
            ).count()

            # Stage progression (active initiatives by stage)
            stage_dist = {}
            for stage in range(1, 6):
                stage_dist[f'stage_{stage}'] = Initiative.objects.filter(
                    status='ACTIVE', current_stage=stage
                ).count()

            # Circuit breaker status
            from core.services.initiative_circuit_breaker import get_backlog_status
            breaker = get_backlog_status()

            # Completion rate
            completed_7d = Initiative.objects.filter(
                status='COMPLETED',
                updated_at__gte=last_7d,
            ).count()

            return {
                'action': 'flow_metrics',
                'creation_rate': {
                    'last_24h': created_24h,
                    'last_7d': created_7d,
                },
                'backlog': {
                    'triage': triage_count,
                    'active': active_count,
                    'no_activity': no_activity,
                },
                'stage_distribution': stage_dist,
                'circuit_breaker': {
                    'can_create': breaker['can_create'],
                    'pending': breaker['pending_count'],
                    'threshold': breaker['threshold'],
                    'utilization_pct': breaker['utilization_pct'],
                    'paused': breaker['paused_by_env'] or breaker['paused_by_db'] or breaker['paused_by_backlog'],
                },
                'completed_last_7d': completed_7d,
            }

        elif action == 'bulk_auto_assign':
            # Session 1000C: Auto-assign agents to unowned initiatives by keyword
            from core.agent_router import AgentRouter

            # Keyword → agent mapping for initiative content routing
            KEYWORD_AGENT_MAP = {
                'research': 'ResearchAgent',
                'competitor': 'CompetitorAnalysisAgent',
                'customer': 'CustomerResearchAgent',
                'content': 'ContentStrategyAgent',
                'blog': 'ContentStrategyAgent',
                'seo': 'SEOOptimizerAgent',
                'brand': 'BrandIdentityAgent',
                'social media': 'SocialMediaAgent',
                'image': 'ImageAgent',
                'video': 'VideoAgent',
                'audio': 'AudioAgent',
                'trend': 'TrendAnalysisAgent',
                'opportunit': 'OpportunityScoringAgent',
                'financial': 'ResearchAgent',
                'market': 'TrendAnalysisAgent',
                'stock': 'ResearchAgent',
                'prediction': 'PredictionMarketAnalyst',
                'sport': 'SportsOddsAnalyst',
                'betting': 'SportsOddsAnalyst',
                'security': 'MemoryIsolationAgent',
                'cyber': 'MemoryIsolationAgent',
                'pipeline': 'CTOAgent',
                'infrastructure': 'CTOAgent',
                'operation': 'COOAgent',
                'risk': 'COOAgent',
                'creative': 'CreativeDirectorAgent',
                'signal': 'TrendAnalysisAgent',
                'enhancement': 'ResearchAgent',
            }

            dry_run = payload.get('dry_run', False)
            limit_count = payload.get('limit', 50)

            qs = Initiative.objects.filter(status='ACTIVE').order_by('-impact_score', '-created_at')[:limit_count]
            assignments = []
            skipped = 0

            for init in qs:
                name_lower = init.name.lower()
                matched_agent = None
                for keyword, agent in KEYWORD_AGENT_MAP.items():
                    if keyword in name_lower:
                        matched_agent = agent
                        break

                if not matched_agent:
                    matched_agent = 'ResearchAgent'  # default fallback

                # Skip if already assigned to a real agent (not just creator)
                if init.owner_agent and init.owner_agent not in ('DecisionExtractor', 'ThinkingAgent', 'auto_populate', ''):
                    skipped += 1
                    continue

                if not dry_run:
                    init.owner_agent = matched_agent
                    init.save(update_fields=['owner_agent'])

                assignments.append({
                    'id': str(init.id),
                    'name': init.name[:80],
                    'agent': matched_agent,
                })

            result = {
                'action': 'bulk_auto_assign',
                'assigned': len(assignments),
                'skipped': skipped,
                'dry_run': dry_run,
                'assignments': assignments[:25],  # show first 25
            }

            # Session 1000C: Combined auto-assign + cleanup
            if payload.get('also_cleanup'):
                cleanup_result = self._handle_initiative(
                    tool_name, {**payload, 'action': 'bulk_cleanup'}, user_id, trace_id
                )
                result['cleanup'] = cleanup_result

            return result

        elif action == 'bulk_cleanup':
            # Session 1000C: Archive stalled, noise, and duplicate initiatives
            from datetime import timedelta
            from django.utils import timezone
            from core.management.commands.consolidate_duplicate_initiatives import (
                find_duplicate_clusters,
            )

            dry_run = payload.get('dry_run', False)
            cutoff = timezone.now() - timedelta(days=14)

            init_list = list(Initiative.objects.filter(
                status__in=['ACTIVE', 'TRIAGE']
            ).only('id', 'name', 'status', 'current_stage', 'last_activity_at', 'created_at'))

            # Classify
            stalled = [i for i in init_list if i.current_stage <= 1 and not i.last_activity_at and i.created_at < cutoff]
            noise = [i for i in init_list if i.current_stage <= 1 and not i.last_activity_at and i.created_at >= cutoff and (timezone.now() - i.created_at).days >= 7]

            # Duplicates
            clusters = find_duplicate_clusters(init_list, threshold=0.6)
            duplicate_ids = set()
            for cluster in clusters:
                for init in cluster[1:]:
                    duplicate_ids.add(init.id)

            archived_stalled = []
            archived_noise = []
            archived_dupes = []

            if not dry_run:
                for init in stalled:
                    init.status = 'ARCHIVED'
                    init.save(update_fields=['status'])
                    archived_stalled.append(init.name[:60])

                for init in noise:
                    init.status = 'ARCHIVED'
                    init.save(update_fields=['status'])
                    archived_noise.append(init.name[:60])

                for init in init_list:
                    if init.id in duplicate_ids:
                        init.status = 'ARCHIVED'
                        init.save(update_fields=['status'])
                        archived_dupes.append(init.name[:60])
            else:
                archived_stalled = [i.name[:60] for i in stalled]
                archived_noise = [i.name[:60] for i in noise]
                archived_dupes = [i.name[:60] for i in init_list if i.id in duplicate_ids]

            return {
                'action': 'bulk_cleanup',
                'dry_run': dry_run,
                'stalled': {'count': len(archived_stalled), 'items': archived_stalled[:10]},
                'noise': {'count': len(archived_noise), 'items': archived_noise[:10]},
                'duplicates': {'count': len(archived_dupes), 'items': archived_dupes[:10], 'cluster_count': len(clusters)},
                'total_cleaned': len(archived_stalled) + len(archived_noise) + len(archived_dupes),
            }

        elif action == 'create':
            from core.services.initiative_integration_service import (
                InitiativeIntegrationService,
                InitiativeCreationBlocked,
            )

            name = payload.get('name', '').strip()
            if not name:
                raise ValueError("'name' is required for create action")

            description = payload.get('description', '')
            purpose = payload.get('purpose', 'learning')
            program = payload.get('program', 'uncategorized')

            try:
                svc = InitiativeIntegrationService()
                # Bypass circuit breaker for explicit human-initiated creation via PA.
                # The breaker exists to prevent autonomous/auto-spawned initiatives from
                # piling up, but when a human explicitly asks the PA to create one, honour it.
                initiative, created = svc.get_or_create_initiative(
                    topic=name,
                    description=description,
                    created_by='human_pa',
                    bypass_circuit_breaker=True,
                )
            except InitiativeCreationBlocked as e:
                return {'action': 'create', 'error': str(e), 'blocked': True}

            # Apply extra fields from payload
            update_fields = []
            for field, default in [
                ('purpose', 'learning'), ('program', 'uncategorized'),
                ('impact_score', 0.5), ('urgency', 0.5),
                ('revenue_potential', 0.0), ('execution_speed', 'balanced'),
            ]:
                val = payload.get(field)
                if val is not None:
                    if field in ('impact_score', 'urgency', 'revenue_potential'):
                        val = max(0.0, min(1.0, float(val)))
                    setattr(initiative, field, val)
                    update_fields.append(field)
            if update_fields:
                initiative.save(update_fields=update_fields)

            return {
                'action': 'create',
                'created': created,
                'id': str(initiative.id),
                'human_id': initiative.human_id,
                'name': initiative.name,
                'status': initiative.status,
                'purpose': initiative.purpose,
                'program': initiative.program,
                'current_stage': initiative.current_stage,
                'message': (
                    f"Created initiative '{initiative.name}' ({initiative.human_id})"
                    if created else
                    f"Found existing initiative '{initiative.name}' ({initiative.human_id}) — no duplicate created"
                ),
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, details, "
                f"action_items, flow_metrics, update_status, advance, start_action_item, "
                f"complete_action_item, assign_owner, bulk_auto_assign, bulk_cleanup, create"
            )

    # =========================================================================
    # Session 948: New PA Enhancement Tools
    # =========================================================================

    def _handle_spider_data(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 948: Spider data tool for querying collected intelligence.

        Provides PA access to data collected by the 77 spiders.

        Actions:
        - recent: Get recent spider data (default)
        - by_spider: Get data from a specific spider
        - by_category: Get data by spider category
        - search: Search spider data by keyword
        - stats: Get spider collection statistics
        """
        from core.models_unified_system import SpiderData
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'recent')
        limit = payload.get('limit', 20)
        spider_name = payload.get('spider_name')
        category = payload.get('category')
        keyword = payload.get('keyword', payload.get('query', ''))
        days = payload.get('days', 7)

        cutoff = timezone.now() - timedelta(days=days)

        if action == 'recent':
            # Get recent spider data across all spiders
            # Session 989: Use actual SpiderData fields (no title/url/category/content)
            qs = SpiderData.objects.filter(created_at__gte=cutoff)

            if spider_name:
                qs = qs.filter(spider_name__icontains=spider_name)
            if category:
                qs = qs.filter(data_type__icontains=category)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'spider_name', 'data_type', 'source_url',
                    'relevance_score', 'created_at'
                )
            )

            return {
                'action': 'recent',
                'count': len(items),
                'items': items,
                'days_back': days,
            }

        elif action == 'by_spider':
            if not spider_name:
                # List available spiders with counts
                spider_counts = dict(
                    SpiderData.objects.filter(created_at__gte=cutoff)
                    .values('spider_name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:30]
                    .values_list('spider_name', 'count')
                )
                return {
                    'action': 'by_spider',
                    'available_spiders': spider_counts,
                    'message': 'Specify spider_name to get data from a specific spider'
                }

            # Session 989: Use actual SpiderData fields
            # Session 1030: Include processed_data for first 3 items (crypto prices live there)
            qs = SpiderData.objects.filter(
                spider_name__icontains=spider_name,
                created_at__gte=cutoff
            ).order_by('-created_at')[:limit]

            items = list(qs.values(
                'id', 'spider_name', 'data_type', 'source_url',
                'embedding_text', 'relevance_score', 'created_at'
            ))

            # Include processed_data for first 3 items only (keeps payload manageable)
            detailed_items = list(qs[:3].values(
                'id', 'processed_data'
            ))
            detail_map = {str(d['id']): d.get('processed_data') for d in detailed_items}
            for item in items[:3]:
                item['processed_data'] = detail_map.get(str(item['id']))

            return {
                'action': 'by_spider',
                'spider_name': spider_name,
                'count': len(items),
                'items': items,
            }

        elif action == 'by_category':
            if not category:
                # Session 989: Use data_type (not category) — actual SpiderData field
                category_counts = dict(
                    SpiderData.objects.filter(created_at__gte=cutoff)
                    .values('data_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:20]
                    .values_list('data_type', 'count')
                )
                return {
                    'action': 'by_category',
                    'available_categories': category_counts,
                    'message': 'Specify category to get data from that category'
                }

            # Session 989: Use data_type (not category)
            items = list(
                SpiderData.objects.filter(
                    data_type__icontains=category,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'spider_name', 'data_type', 'source_url',
                    'relevance_score', 'created_at'
                )
            )

            return {
                'action': 'by_category',
                'category': category,
                'count': len(items),
                'items': items,
            }

        elif action == 'search':
            if not keyword:
                return {
                    'action': 'search',
                    'error': 'keyword is required for search',
                }

            # Session 989: Use actual SpiderData fields (embedding_text, raw_data)
            from django.db.models import Q
            qs = SpiderData.objects.filter(
                Q(embedding_text__icontains=keyword) |
                Q(source_url__icontains=keyword),
                created_at__gte=cutoff
            )

            if spider_name:
                qs = qs.filter(spider_name__icontains=spider_name)

            items = list(
                qs.order_by('-relevance_score', '-created_at')[:limit].values(
                    'id', 'spider_name', 'data_type', 'source_url',
                    'embedding_text', 'relevance_score', 'created_at'
                )
            )

            return {
                'action': 'search',
                'keyword': keyword,
                'count': len(items),
                'items': items,
            }

        elif action == 'stats':
            total = SpiderData.objects.filter(created_at__gte=cutoff).count()
            by_spider = dict(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .values('spider_name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('spider_name', 'count')
            )
            # Session 989: Use data_type (not category)
            by_data_type = dict(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .values('data_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('data_type', 'count')
            )

            return {
                'action': 'stats',
                'total_items': total,
                'days_back': days,
                'by_spider': by_spider,
                'by_data_type': by_data_type,
            }

        # Session 993: Trigger spider run by category or name
        elif action == 'trigger':
            category = payload.get('category')
            spider_name = payload.get('spider_name')

            if not category and not spider_name:
                raise ValueError("category or spider_name is required for trigger action")

            from core.tasks import run_spider_by_category
            target = category or spider_name
            task = run_spider_by_category.delay(category=target)  # type: ignore[union-attr]

            return {
                'action': 'trigger',
                'target': target,
                'task_id': str(task.id),
                'message': f'Spider run queued for "{target}". Check execution history for results.',
                'success': True,
            }

        else:
            logger.warning(f"Unknown spider_data action '{action}', defaulting to 'recent'")
            payload['action'] = 'recent'
            return self._handle_spider_data(tool_name, payload, user_id, trace_id)

    def _handle_execution_history(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 948: Execution history tool for viewing agent activity.

        Provides PA access to recent agent executions.

        Actions:
        - recent: Get recent executions (default)
        - by_agent: Get executions for a specific agent
        - stats: Get execution statistics
        - failures: Get recent failures for debugging
        """
        from core.models import AgentExecution
        from core.models_deliberation import DeliberationSession
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'recent')
        limit = payload.get('limit', 20)
        agent_name = payload.get('agent_name')
        hours = payload.get('hours', 24)

        cutoff = timezone.now() - timedelta(hours=hours)

        # Session 989: AgentExecution.agent is FK to Agent — use agent__name
        # AgentExecution has no 'success' field — use status='completed'/'failed'

        if action == 'recent':
            qs = AgentExecution.objects.filter(created_at__gte=cutoff)

            if agent_name:
                qs = qs.filter(agent__name__icontains=agent_name)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'agent__name', 'task', 'status',
                    'execution_time_ms', 'created_at'
                )
            )

            # Session 988: Also include agent conversations (DeliberationSessions)
            conversations = list(
                DeliberationSession.objects.filter(
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'objective', 'participants', 'status', 'created_at'
                )
            )

            return {
                'action': 'recent',
                'count': len(items),
                'items': items,
                'conversation_count': len(conversations),
                'conversations': conversations,
                'hours_back': hours,
            }

        elif action == 'by_agent':
            if not agent_name:
                # List active agents with execution counts
                agent_counts = dict(
                    AgentExecution.objects.filter(created_at__gte=cutoff)
                    .values('agent__name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:30]
                    .values_list('agent__name', 'count')
                )
                return {
                    'action': 'by_agent',
                    'active_agents': agent_counts,
                    'message': 'Specify agent_name to see executions for a specific agent'
                }

            items = list(
                AgentExecution.objects.filter(
                    agent__name__icontains=agent_name,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'agent__name', 'task', 'status',
                    'execution_time_ms', 'error_message', 'created_at'
                )
            )

            # Calculate success rate for this agent
            total = AgentExecution.objects.filter(
                agent__name__icontains=agent_name,
                created_at__gte=cutoff
            ).count()
            successes = AgentExecution.objects.filter(
                agent__name__icontains=agent_name,
                created_at__gte=cutoff,
                status='completed'
            ).count()

            return {
                'action': 'by_agent',
                'agent_name': agent_name,
                'count': len(items),
                'items': items,
                'success_rate': successes / total if total > 0 else 0,
            }

        elif action == 'stats':
            total = AgentExecution.objects.filter(created_at__gte=cutoff).count()
            successes = AgentExecution.objects.filter(
                created_at__gte=cutoff, status='completed'
            ).count()
            failures = AgentExecution.objects.filter(
                created_at__gte=cutoff, status='failed'
            ).count()

            by_agent = list(
                AgentExecution.objects.filter(created_at__gte=cutoff)
                .values('agent__name')
                .annotate(
                    count=Count('id'),
                    avg_time=Avg('execution_time_ms')
                )
                .order_by('-count')[:15]
            )

            # Session 988: Include deliberation session stats
            conv_total = DeliberationSession.objects.filter(
                created_at__gte=cutoff
            ).count()
            conv_completed = DeliberationSession.objects.filter(
                created_at__gte=cutoff, status='completed'
            ).count()

            return {
                'action': 'stats',
                'total_executions': total,
                'successes': successes,
                'failures': failures,
                'success_rate': successes / total if total > 0 else 0,
                'total_conversations': conv_total,
                'completed_conversations': conv_completed,
                'hours_back': hours,
                'by_agent': by_agent,
            }

        elif action == 'failures':
            items = list(
                AgentExecution.objects.filter(
                    created_at__gte=cutoff,
                    status='failed'
                ).order_by('-created_at')[:limit].values(
                    'id', 'agent__name', 'task', 'status', 'error_message',
                    'created_at'
                )
            )

            return {
                'action': 'failures',
                'count': len(items),
                'items': items,
                'hours_back': hours,
            }

        elif action == 'detail':
            exec_id = payload.get('id')
            if not exec_id:
                # No ID — return the most recent execution (optionally filtered by agent)
                qs = AgentExecution.objects.all()
                if agent_name:
                    qs = qs.filter(agent__name__icontains=agent_name)
                execution = qs.order_by('-created_at').first()
                if not execution:
                    return {'action': 'detail', 'error': 'No executions found'}
            else:
                execution = AgentExecution.objects.filter(id=exec_id).first()
                if not execution:
                    return {'action': 'detail', 'error': f'Execution {exec_id} not found'}

            output = execution.output_data or {}
            # Truncate very large output to avoid token explosion
            import json
            output_str = json.dumps(output, default=str)
            if len(output_str) > 8000:
                # Keep message/error/summary and truncate data
                truncated = {
                    'message': output.get('message', '')[:3000],
                    'error': output.get('error'),
                    'data': {k: v for k, v in (output.get('data') or {}).items()
                             if k in ('info_count', 'warning_count', 'critical_count',
                                      'items_count', 'execution_time', 'pipeline_steps',
                                      'final_video_url', 'type', 'summary',
                                      'result_preview')},
                    'result_preview': output.get('result_preview', '')[:2000],
                    'tool_calls': output.get('tool_calls', [])[:5],
                    '_truncated': True,
                    '_full_size_bytes': len(output_str),
                }
            else:
                truncated = output

            return {
                'action': 'detail',
                'id': str(execution.id),
                'agent_name': execution.agent.name if execution.agent else None,
                'task': execution.task,
                'status': execution.status,
                'error_message': execution.error_message,
                'execution_time_ms': execution.execution_time_ms,
                'created_at': execution.created_at,
                'completed_at': getattr(execution, 'completed_at', None),
                'output_data': truncated,
                'input_data_keys': list((execution.input_data or {}).keys()),
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: recent, by_agent, stats, failures, detail"
            )

    def _handle_learning_patterns(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 948: Learning patterns tool for viewing system learnings.

        Provides PA access to patterns the system has learned from execution data.

        Actions:
        - list: List active learning patterns (default)
        - by_type: Get patterns by type (tool_reliability, agent_performance, etc.)
        - stats: Get learning statistics
        """
        from core.models_unified_system import LearningPattern
        from django.db.models import Count

        action = payload.get('action', 'list')
        limit = payload.get('limit', 20)
        pattern_type = payload.get('pattern_type')
        min_confidence = payload.get('min_confidence', 0.5)

        if action == 'list':
            qs = LearningPattern.objects.filter(
                is_active=True,
                confidence__gte=min_confidence
            )

            if pattern_type:
                qs = qs.filter(pattern_type=pattern_type)

            items = list(
                qs.order_by('-confidence', '-updated_at')[:limit].values(
                    'id', 'pattern_type', 'description', 'confidence',
                    'pattern_data', 'applies_to_agents', 'times_applied',
                    'success_when_applied', 'updated_at'
                )
            )

            # Calculate effectiveness for each
            for item in items:
                applied = item.get('times_applied', 0)
                successful = item.get('success_when_applied', 0)
                item['effectiveness'] = successful / applied if applied > 0 else 0

            return {
                'action': 'list',
                'count': len(items),
                'items': items,
                'min_confidence': min_confidence,
            }

        elif action == 'by_type':
            if not pattern_type:
                # List available pattern types
                type_counts = dict(
                    LearningPattern.objects.filter(is_active=True)
                    .values('pattern_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                    .values_list('pattern_type', 'count')
                )
                return {
                    'action': 'by_type',
                    'available_types': type_counts,
                    'message': 'Specify pattern_type to filter by type'
                }

            items = list(
                LearningPattern.objects.filter(
                    is_active=True,
                    pattern_type=pattern_type,
                    confidence__gte=min_confidence
                ).order_by('-confidence')[:limit].values(
                    'id', 'pattern_type', 'description', 'confidence',
                    'pattern_data', 'applies_to_agents', 'times_applied',
                    'success_when_applied', 'updated_at'
                )
            )

            return {
                'action': 'by_type',
                'pattern_type': pattern_type,
                'count': len(items),
                'items': items,
            }

        elif action == 'stats':
            total = LearningPattern.objects.filter(is_active=True).count()
            by_type = dict(
                LearningPattern.objects.filter(is_active=True)
                .values('pattern_type')
                .annotate(count=Count('id'))
                .order_by('-count')
                .values_list('pattern_type', 'count')
            )

            # Top performing patterns
            top_patterns = list(
                LearningPattern.objects.filter(
                    is_active=True,
                    times_applied__gt=0
                ).order_by('-confidence')[:5].values(
                    'description', 'confidence', 'pattern_type'
                )
            )

            return {
                'action': 'stats',
                'total_patterns': total,
                'by_type': by_type,
                'top_patterns': top_patterns,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, by_type, stats"
            )

    def _handle_feedback(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 948: Handle user feedback viewing and management.
        Session 1061: Fixed handler signature (was old-style, caused crash).

        Actions:
        - list: List feedback items (optionally filtered by status)
        - stats: Get feedback statistics
        - submit: Submit new feedback
        - update: Update feedback status (admin only)
        """
        from core.models_user_feedback import UserFeedback

        action = payload.get('action', 'list')
        status_filter = payload.get('status')
        limit = payload.get('limit', 20)

        if action == 'list':
            qs = UserFeedback.objects.all()
            if status_filter:
                qs = qs.filter(status=status_filter)
            else:
                # Default to open items
                qs = qs.filter(status='open')

            items = list(qs[:limit].values(
                'id', 'feedback_type', 'message', 'status',
                'created_at', 'trace_id'
            ))

            # Session 987: Serialize UUIDs and datetimes
            for item in items:
                item['id'] = str(item['id'])
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()

            return {
                'action': 'list',
                'status_filter': status_filter or 'open',
                'count': len(items),
                'items': items,
            }

        elif action == 'stats':
            summary = UserFeedback.get_feedback_summary()
            return {
                'action': 'stats',
                'total_open': summary['total_open'],
                'by_type': summary['by_type'],
                'by_status': summary['by_status'],
            }

        elif action == 'submit':
            from django.contrib.auth import get_user_model
            User = get_user_model()

            comment = payload.get('comment', '')
            target_type = payload.get('target_type', 'general')

            if not comment:
                return {'error': 'comment is required for submit'}

            user = User.objects.filter(id=user_id).first() if user_id else None
            if not user:
                user = User.objects.first()

            feedback = UserFeedback.objects.create(
                user=user,
                feedback_type=target_type if target_type in (
                    'ui_ux_issue', 'bug', 'feature_request', 'feedback'
                ) else 'feedback',
                message=comment,
                status='open',
                trace_id=trace_id if trace_id and not trace_id.startswith('pa-') else '',
            )

            return {
                'action': 'submit',
                'id': str(feedback.id),
                'success': True,
                'message': 'Feedback submitted successfully',
            }

        elif action == 'update':
            feedback_id = payload.get('id')
            new_status = payload.get('new_status')
            notes = payload.get('notes', '')

            if not feedback_id or not new_status:
                raise ValueError("Update requires 'id' and 'new_status'")

            try:
                feedback = UserFeedback.objects.get(id=feedback_id)
                feedback.status = new_status
                if notes:
                    feedback.resolution_notes = notes
                feedback.save()

                return {
                    'action': 'update',
                    'id': feedback_id,
                    'new_status': new_status,
                    'success': True,
                }
            except UserFeedback.DoesNotExist:
                raise ValueError(f"Feedback item {feedback_id} not found")

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, submit, update"
            )


    # ------------------------------------------------------------------ #
    # Session 969: Live telemetry tools for PA self-awareness             #
    # ------------------------------------------------------------------ #

    def _handle_recent_activity(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 969: Recent activity tool — comprehensive activity snapshot.

        Answers "What's been going on?" across all major subsystems.

        Actions:
        - summary: High-level counts and latest items (default)
        - detailed: Same but with more items per section
        """
        from django.utils import timezone
        from django.db.models import Count
        from datetime import timedelta

        action = payload.get('action', 'summary')
        hours = payload.get('hours', 2)
        cutoff = timezone.now() - timedelta(hours=hours)
        item_limit = 5 if action == 'summary' else 15

        sections = {}

        # 1. Celery tasks — Session 983: use CeleryTaskEvent (our own
        # telemetry) instead of TaskResult (empty when backend=redis)
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            task_qs = CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
            by_status = dict(
                task_qs.values('status')
                .annotate(n=Count('id'))
                .values_list('status', 'n')
            )
            sections['celery_tasks'] = {
                'total': sum(by_status.values()),
                'by_status': by_status,
            }
        except Exception as e:
            sections['celery_tasks'] = {'error': str(e)}

        # 2. Spider data
        try:
            from core.models_unified_system import SpiderData
            spider_qs = SpiderData.objects.filter(created_at__gte=cutoff)
            total_spider = spider_qs.count()
            distinct_spiders = spider_qs.values('spider_name').distinct().count()
            top_spiders = list(
                spider_qs.values('spider_name')
                .annotate(n=Count('id'))
                .order_by('-n')[:item_limit]
                .values_list('spider_name', 'n')
            )
            sections['spider_data'] = {
                'total_items': total_spider,
                'distinct_spiders': distinct_spiders,
                'top_spiders': dict(top_spiders),
            }
        except Exception as e:
            sections['spider_data'] = {'error': str(e)}

        # 3. Conversations (HiveMindSession)
        try:
            from core.models_unified_system import HiveMindSession
            conv_qs = HiveMindSession.objects.filter(created_at__gte=cutoff)
            by_status = dict(
                conv_qs.values('status')
                .annotate(n=Count('id'))
                .values_list('status', 'n')
            )
            latest = list(
                conv_qs.order_by('-created_at')[:item_limit]
                .values('question', 'status', 'created_at')
            )
            for item in latest:
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()
                # Truncate long questions
                q = item.get('question', '')
                if len(q) > 120:
                    item['question'] = q[:120] + '...'
            sections['conversations'] = {
                'total': sum(by_status.values()),
                'by_status': by_status,
                'latest': latest,
            }
        except Exception as e:
            sections['conversations'] = {'error': str(e)}

        # 4. Blogs (SelfBlog)
        try:
            from core.models_unified_system import SelfBlog
            blog_qs = SelfBlog.objects.filter(created_at__gte=cutoff)
            total_blogs = blog_qs.count()
            published = blog_qs.filter(status='published').count()
            draft = blog_qs.filter(status='draft').count()
            latest = list(
                blog_qs.order_by('-created_at')[:item_limit]
                .values('title', 'status', 'created_at')
            )
            for item in latest:
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()
            sections['blogs'] = {
                'total': total_blogs,
                'published': published,
                'draft': draft,
                'latest': latest,
            }
        except Exception as e:
            sections['blogs'] = {'error': str(e)}

        # 5. Initiative changes
        try:
            from core.models_document_registry import Initiative
            init_qs = Initiative.objects.filter(
                updated_at__gte=cutoff,
                status='ACTIVE'
            )
            total_updated = init_qs.count()
            latest = list(
                init_qs.order_by('-updated_at')[:item_limit]
                .values('name', 'updated_at')
            )
            for item in latest:
                if item.get('updated_at'):
                    item['updated_at'] = item['updated_at'].isoformat()
            sections['initiatives'] = {
                'recently_updated': total_updated,
                'latest': latest,
            }
        except Exception as e:
            sections['initiatives'] = {'error': str(e)}

        # 6. Signal clusters
        try:
            from core.models_signal_intelligence import SignalCluster
            sig_qs = SignalCluster.objects.filter(
                detected_at__gte=cutoff,
                status='active'
            )
            total_signals = sig_qs.count()
            top_signals = list(
                sig_qs.order_by('-strength')[:item_limit]
                .values('name', 'strength', 'pattern_type')
            )
            sections['signals'] = {
                'active_clusters': total_signals,
                'top_by_strength': top_signals,
            }
        except Exception as e:
            sections['signals'] = {'error': str(e)}

        return {
            'action': action,
            'hours_back': hours,
            'sections': sections,
        }

    # _handle_system_health and _handle_error_summary deleted (Session 1079 PR2).
    # ops_tool.slo_status and ops_tool.failure_signatures replace them.

    def _handle_surgical_moves_status(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 970: Surgical moves status tool — deliberation session verification.

        Answers "surgical moves status" / "what deliberations happened" with
        session details, contract counts, evidence stats, and verdicts.

        Actions:
        - summary: Recent sessions with key stats (default)
        - detailed: Full session details including contracts and evidence
        """
        import json as _json
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'summary')
        hours = payload.get('hours', 24)
        session_id = payload.get('session_id')
        cutoff = timezone.now() - timedelta(hours=hours)
        limit = 5 if action == 'summary' else 20

        try:
            from core.models_deliberation import (
                DeliberationSession,
                DeliberationTurn,
                ContractRecord,
            )
        except ImportError:
            return {
                'action': action,
                'error': 'Deliberation models not available',
            }

        try:
            if session_id:
                sessions = DeliberationSession.objects.filter(id=session_id)
            else:
                sessions = DeliberationSession.objects.filter(
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit]

            runs = []
            for s in sessions:
                turns = DeliberationTurn.objects.filter(session=s)
                contracts = ContractRecord.objects.filter(session=s)
                turn_count = turns.count()
                ep = s.evidence_pack or {}

                contract_info = []
                verdict = None
                for c in contracts:
                    cdata = c.contract_data or {}
                    data_size = len(_json.dumps(cdata))
                    contract_info.append({
                        'type': c.contract_type,
                        'data_size': data_size,
                    })
                    if c.contract_type == 'execution':
                        verdict = cdata.get('chosen_path', cdata.get('decision', ''))
                        if isinstance(verdict, str):
                            verdict = verdict[:200]

                runs.append({
                    'session_id': str(s.id),
                    'objective': (s.objective or '')[:120],
                    'status': s.status,
                    'created_at': s.created_at.isoformat() if s.created_at else None,
                    'turn_count': turn_count,
                    'contract_count': len(contract_info),
                    'contracts': contract_info,
                    'decision_verdict': verdict,
                    'evidence_stats': {
                        'sources': len(ep.get('sources', [])),
                        'claims': len(ep.get('claims', [])),
                        'contradictions': len(ep.get('contradictions', [])),
                        'internal_refs': len(ep.get('internal_refs', [])),
                    },
                })

            return {
                'action': action,
                'hours_back': hours,
                'total_sessions': len(runs),
                'runs': runs,
            }
        except Exception as e:
            logger.error(f"[Session 970] Surgical moves status error: {e}")
            return {
                'action': action,
                'hours_back': hours,
                'total_sessions': 0,
                'runs': [],
                'error': str(e),
            }


    def _handle_stock_intelligence(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 979: Stock intelligence tool for PA access to market data.

        Surfaces MarketIntelligenceBrief, StockMarketAlert, PredictionOutcome,
        and SEC Edgar filings — the same data as the /stocks dashboard.

        Actions:
        - overview: Dashboard summary (default)
        - briefs: Recent market briefs
        - alerts: Stock alerts
        - predictions: Prediction outcomes with accuracy
        - sec_filings: SEC Edgar spider data
        """
        from core.models_unified_system import MarketIntelligenceBrief, PredictionOutcome, SpiderData
        from core.models_autonomous_alerts import StockMarketAlert
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'overview')
        limit = payload.get('limit', 10)

        if action == 'overview':
            # Mirrors views_stock_intelligence.stock_dashboard
            latest_brief = MarketIntelligenceBrief.objects.first()
            latest_brief_data = None
            if latest_brief:
                latest_brief_data = {
                    'id': str(latest_brief.id),
                    'brief_date': latest_brief.brief_date.isoformat(),
                    'executive_summary': latest_brief.executive_summary[:300],
                    'total_stocks_analyzed': latest_brief.total_stocks_analyzed,
                    'debate_zone_count': latest_brief.debate_zone_count,
                    'situation_health': latest_brief.situation_health,
                }

            alert_counts = dict(
                StockMarketAlert.objects.values_list('alert_type')
                .annotate(count=Count('id'))
                .values_list('alert_type', 'count')
            )
            total_alerts = sum(alert_counts.values())

            predictions_eval = PredictionOutcome.objects.filter(was_correct_7_days__isnull=False)
            total_predictions = predictions_eval.count()
            correct_7d = predictions_eval.filter(was_correct_7_days=True).count()
            accuracy_7d = round((correct_7d / total_predictions) * 100, 1) if total_predictions > 0 else None

            predictions_30d = PredictionOutcome.objects.filter(was_correct_30_days__isnull=False)
            total_30d = predictions_30d.count()
            correct_30d = predictions_30d.filter(was_correct_30_days=True).count()
            accuracy_30d = round((correct_30d / total_30d) * 100, 1) if total_30d > 0 else None

            sec_count = SpiderData.objects.filter(spider_name='sec_edgar').count()
            total_briefs = MarketIntelligenceBrief.objects.count()

            return {
                'action': 'overview',
                'latest_brief': latest_brief_data,
                'total_briefs': total_briefs,
                'total_alerts': total_alerts,
                'alert_counts_by_type': alert_counts,
                'prediction_accuracy_7d': accuracy_7d,
                'prediction_accuracy_30d': accuracy_30d,
                'total_predictions': total_predictions,
                'sec_filings_count': sec_count,
            }

        elif action == 'briefs':
            qs = MarketIntelligenceBrief.objects.all()
            total = qs.count()
            briefs = qs[:limit]
            items = []
            for b in briefs:
                items.append({
                    'id': str(b.id),
                    'brief_date': b.brief_date.isoformat(),
                    'brief_type': b.brief_type,
                    'executive_summary': b.executive_summary[:300],
                    'total_stocks_analyzed': b.total_stocks_analyzed,
                    'debate_zone_count': b.debate_zone_count,
                    'situation_health': b.situation_health,
                })
            return {'action': 'briefs', 'items': items, 'total': total}

        elif action == 'alerts':
            qs = StockMarketAlert.objects.all()
            # Session 1062: Filter by ticker if provided
            ticker = payload.get('ticker', '')
            if ticker:
                qs = qs.filter(symbol__iexact=ticker)
            total = qs.count()
            alerts = qs[:limit]
            items = []
            for a in alerts:
                items.append({
                    'id': str(a.id),
                    'alert_type': a.alert_type,
                    'symbol': a.symbol,
                    'company_name': a.company_name,
                    'title': a.title,
                    'summary': a.summary[:200],
                    'confidence_score': float(a.confidence_score),
                    'bull_score': a.bull_score,
                    'bear_score': a.bear_score,
                    'recommended_action': a.recommended_action,
                    'detected_at': a.detected_at.isoformat() if a.detected_at else None,
                })
            return {'action': 'alerts', 'items': items, 'total': total}

        elif action == 'predictions':
            qs = PredictionOutcome.objects.all()
            # Session 1062: Filter by ticker if provided
            ticker = payload.get('ticker', '')
            if ticker:
                qs = qs.filter(ticker__iexact=ticker)
            total = qs.count()
            predictions = qs[:limit]
            items = []
            for p in predictions:
                items.append({
                    'id': str(p.id),
                    'ticker': p.ticker,
                    'prediction_type': p.prediction_type,
                    'conviction_level': p.conviction_level,
                    'predicted_move': float(p.predicted_move),
                    'prediction_date': p.prediction_date.isoformat(),
                    'was_correct_7_days': p.was_correct_7_days,
                    'was_correct_30_days': p.was_correct_30_days,
                })

            evaluated = qs.filter(was_correct_7_days__isnull=False)
            eval_count = evaluated.count()
            correct_7d = evaluated.filter(was_correct_7_days=True).count()
            correct_30d = evaluated.filter(was_correct_30_days=True).count()
            stats = {
                'evaluated_count': eval_count,
                'accuracy_7d_pct': round((correct_7d / eval_count) * 100, 1) if eval_count else None,
                'accuracy_30d_pct': round((correct_30d / eval_count) * 100, 1) if eval_count else None,
            }
            return {'action': 'predictions', 'items': items, 'total': total, 'stats': stats}

        elif action == 'sec_filings':
            qs = SpiderData.objects.filter(spider_name='sec_edgar').order_by('-created_at')
            total = qs.count()
            filings = qs[:limit]
            items = []
            for f in filings:
                items.append({
                    'id': str(f.id),
                    'source_url': f.source_url,
                    'data_type': f.data_type,
                    'relevance_score': f.relevance_score,
                    'created_at': f.created_at.isoformat() if f.created_at else None,
                })
            return {'action': 'sec_filings', 'items': items, 'total': total}

        else:
            logger.warning(f"Unknown stock_intelligence action '{action}', defaulting to overview")
            payload['action'] = 'overview'
            return self._handle_stock_intelligence(tool_name, payload, user_id, trace_id)

    def _handle_sports_betting(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 995B: Sports betting intelligence tool for PA.

        Surfaces wagers, arbitrage, predictions, sharp action, line movements,
        and full betting briefs — the same data as the /betting dashboard.

        Actions:
        - overview: Dashboard summary (default)
        - arbs: Active arbitrage opportunities
        - predictions: Game predictions
        - sharp_action: Sharp action signals
        - line_movements: Detected line movements
        - wagers: User's placed wagers
        - live_odds: Current odds from TheOddsSpider
        - brief: Full betting brief from coordinator
        """
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'overview')
        limit = payload.get('limit', 10)

        if action == 'overview':
            from core.models_betting import PlacedWager, BettingStats
            from core.models_human_interface import HumanAttentionItem

            pending = PlacedWager.objects.filter(status='pending').count()
            settled = PlacedWager.objects.filter(status__in=['won', 'lost', 'push']).count()

            arb_count = HumanAttentionItem.objects.filter(
                item_type='arbitrage',
                status='watching',
            ).count()

            # Recent sharp signals from SpiderData
            from core.models_unified_system import SpiderData
            cutoff = timezone.now() - timedelta(hours=12)
            recent_odds = SpiderData.objects.filter(
                spider_name='theodds',
                created_at__gte=cutoff,
            ).count()

            # Active sports from recent odds data
            active_sports = list(
                SpiderData.objects.filter(
                    spider_name='theodds',
                    created_at__gte=cutoff,
                ).values_list('data_type', flat=True).distinct()[:10]
            )

            return {
                'action': 'overview',
                'pending_wagers': pending,
                'settled_wagers': settled,
                'active_arb_opps': arb_count,
                'hot_sharp_signals': 0,  # populated by agent runs
                'recent_odds_records': recent_odds,
                'active_sports': active_sports,
            }

        elif action == 'arbs':
            from core.models_human_interface import HumanAttentionItem
            qs = HumanAttentionItem.objects.filter(
                item_type='arbitrage',
                status='watching',
            ).order_by('-created_at')
            total = qs.count()
            items = []
            for item in qs[:limit]:
                p = item.payload or {}
                items.append({
                    'id': str(item.id),
                    'matchup': p.get('matchup', p.get('event', '')),
                    'sport': p.get('sport', ''),
                    'profit_pct': p.get('profit_pct', 0),
                    'rating': p.get('rating', ''),
                    'home_book': p.get('home_book', ''),
                    'away_book': p.get('away_book', ''),
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                })
            return {'action': 'arbs', 'items': items, 'total': total}

        elif action == 'predictions':
            try:
                from sports.models import MLPrediction
                qs = MLPrediction.objects.order_by('-created_at')
                total = qs.count()
                items = []
                for p in qs[:limit]:
                    # MLPrediction: game FK (home_team/away_team on Game), predicted_winner FK to Team
                    game = getattr(p, 'game', None)
                    if game:
                        matchup = f"{getattr(game.away_team, 'abbreviation', game.away_team)} @ {getattr(game.home_team, 'abbreviation', game.home_team)}"
                    else:
                        matchup = str(p)
                    winner = getattr(p, 'predicted_winner', None)
                    items.append({
                        'id': str(p.id),
                        'matchup': matchup,
                        'predicted_winner': str(winner) if winner else '',
                        'confidence': getattr(p, 'confidence', 0),
                        'sport_type': getattr(p, 'sport_type', ''),
                        'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None,
                    })
                return {'action': 'predictions', 'items': items, 'total': total}
            except Exception as e:
                logger.warning(f"MLPrediction query failed: {e}")
                return {'action': 'predictions', 'items': [], 'total': 0, 'error': str(e)}

        elif action == 'accuracy':
            try:
                from sports.models import MLPrediction
                from core.models_betting import PlacedWager
                from django.db.models import Sum, Count, Q, Avg

                sport = payload.get('sport', None)
                days = payload.get('days', 30)

                # Overall accuracy from MLPrediction.calculate_accuracy
                overall = MLPrediction.calculate_accuracy(sport_type=sport, days=days)

                # Per-sport breakdown
                from django.utils import timezone as tz
                from datetime import timedelta
                cutoff = tz.now() - timedelta(days=days)
                sport_qs = MLPrediction.objects.filter(
                    created_at__gte=cutoff,
                    was_correct__isnull=False,
                )
                if sport:
                    sport_qs = sport_qs.filter(sport_type=sport)

                by_sport = []
                for row in sport_qs.values('sport_type').annotate(
                    total=Count('id'),
                    correct=Count('id', filter=Q(was_correct=True)),
                    avg_confidence=Avg('confidence'),
                ).order_by('-total'):
                    total_s = row['total']
                    by_sport.append({
                        'sport': row['sport_type'],
                        'total': total_s,
                        'correct': row['correct'],
                        'accuracy_pct': round((row['correct'] / total_s) * 100, 2) if total_s else 0,
                        'avg_confidence': round(row['avg_confidence'] or 0, 2),
                    })

                # Wager win/loss/push stats
                wager_qs = PlacedWager.objects.filter(placed_at__gte=cutoff)
                if user_id:
                    wager_qs = wager_qs.filter(user_id=user_id)
                agg = wager_qs.aggregate(
                    total=Count('id'),
                    won=Count('id', filter=Q(status='won')),
                    lost=Count('id', filter=Q(status='lost')),
                    push=Count('id', filter=Q(status='push')),
                    pending=Count('id', filter=Q(status='pending')),
                    total_staked=Sum('stake'),
                    total_pnl=Sum('result_amount'),
                )
                total_staked = float(agg['total_staked'] or 0)
                total_pnl = float(agg['total_pnl'] or 0)
                wager_stats = {
                    'total_wagers': agg['total'],
                    'won': agg['won'],
                    'lost': agg['lost'],
                    'push': agg['push'],
                    'pending': agg['pending'],
                    'win_rate_pct': round((agg['won'] / (agg['won'] + agg['lost'])) * 100, 2) if (agg['won'] + agg['lost']) > 0 else 0,
                    'total_staked': total_staked,
                    'total_pnl': total_pnl,
                    'roi_pct': round((total_pnl / total_staked) * 100, 2) if total_staked > 0 else 0,
                }

                return {
                    'action': 'accuracy',
                    'overall': overall,
                    'by_sport': by_sport,
                    'wager_stats': wager_stats,
                    'days': days,
                }
            except Exception as e:
                logger.warning(f"Accuracy query failed: {e}")
                return {'action': 'accuracy', 'overall': {}, 'by_sport': [], 'wager_stats': {}, 'days': payload.get('days', 30), 'error': str(e)}

        elif action == 'sharp_action':
            # Session 1075: Dispatch async — SharpActionDetector can exceed 30s tool timeout
            from core.tasks import execute_agent_task
            celery_task = execute_agent_task.apply_async(
                args=['SharpActionDetector', 'Identify sharp betting action and stale lines',
                      {'user_id': str(user_id) if user_id else None, 'limit': limit}],
                queue='agents',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'action': 'sharp_action',
                'message': f'Sharp action analysis dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        elif action == 'line_movements':
            # Session 1075: Dispatch async — LineMovementAnalyzer can exceed 30s tool timeout
            from core.tasks import execute_agent_task
            celery_task = execute_agent_task.apply_async(
                args=['LineMovementAnalyzer', 'Detect sharp money line movements',
                      {'user_id': str(user_id) if user_id else None, 'limit': limit}],
                queue='agents',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'action': 'line_movements',
                'message': f'Line movement analysis dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        elif action == 'wagers':
            from core.models_betting import PlacedWager
            qs = PlacedWager.objects.all().order_by('-placed_at')
            if user_id:
                qs = qs.filter(user_id=user_id)
            total = qs.count()
            items = []
            for w in qs[:limit]:
                items.append({
                    'id': str(w.id),
                    'description': w.description if hasattr(w, 'description') else str(w),  # type: ignore[attr-defined]
                    'status': w.status,
                    'stake': float(w.stake) if hasattr(w, 'stake') and w.stake else 0,
                    'potential_payout': float(w.potential_payout) if hasattr(w, 'potential_payout') and w.potential_payout else 0,
                    'placed_at': w.placed_at.isoformat() if w.placed_at else None,
                })
            return {'action': 'wagers', 'items': items, 'total': total}

        elif action == 'record_wager':
            from core.models_betting import PlacedWager
            from decimal import Decimal, InvalidOperation

            description = payload.get('description', '').strip()
            if not description:
                raise ValueError("'description' is required for record_wager")

            try:
                stake = Decimal(str(payload.get('stake', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("'stake' must be a valid number")
            if stake <= 0:
                raise ValueError("'stake' must be positive")

            try:
                odds = Decimal(str(payload.get('odds', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("'odds' must be a valid number")

            # Compute potential payout (American odds)
            if odds > 0:
                potential_payout = stake * (odds / Decimal('100'))
            elif odds < 0:
                potential_payout = stake * (Decimal('100') / abs(odds))
            else:
                potential_payout = stake  # even money fallback

            # PlacedWager has no 'description' field — use 'notes' instead
            wager_kwargs = {
                'notes': description,
                'stake': stake,
                'odds': int(odds),  # PlacedWager.odds is IntegerField
                'potential_payout': potential_payout,
                'status': 'pending',
            }
            if user_id:
                wager_kwargs['user_id'] = user_id

            extra_notes = payload.get('notes', '').strip()
            if extra_notes:
                wager_kwargs['notes'] = f"{description} | {extra_notes}"
            wager_type = payload.get('wager_type', '').strip()
            if hasattr(PlacedWager, 'wager_type') and wager_type:
                wager_kwargs['wager_type'] = wager_type

            wager = PlacedWager.objects.create(**wager_kwargs)
            return {
                'action': 'record_wager',
                'id': str(wager.id),
                'description': wager.notes,
                'stake': str(wager.stake),
                'odds': float(odds),
                'potential_payout': str(wager.potential_payout),
                'status': wager.status,
                'success': True,
            }

        elif action in ('brief', 'live_odds'):
            # Session 1088: Dispatch to Celery async — generate_brief() is slow
            # and was causing 30s TOOL_TIMEOUT in the PA.
            from core.tasks import execute_agent_task
            celery_task = execute_agent_task.apply_async(
                args=['GamePredictor', f'Generate a full betting brief ({action})',
                      {'user_id': str(user_id) if user_id else None, 'action': action}],
                queue='agents',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'action': action,
                'message': f'Betting brief dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        else:
            logger.warning(f"Unknown sports_betting action '{action}', defaulting to overview")
            payload['action'] = 'overview'
            return self._handle_sports_betting(tool_name, payload, user_id, trace_id)

    def _handle_status_snapshot(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 973: Cheap system status snapshot for broad overview questions.
        9 count() queries, cached 60s.
        """
        from django.core.cache import cache

        cache_key = 'pa:status_snapshot'
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"[{trace_id}] Status snapshot served from cache")
            return cached

        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        snapshot = {}

        # 1. Initiatives
        try:
            from core.models import Initiative
            active = Initiative.objects.filter(status='ACTIVE').count()
            updated_24h = Initiative.objects.filter(updated_at__gte=last_24h).count()
            snapshot['initiatives'] = {'active': active, 'updated_24h': updated_24h}
        except Exception as e:
            snapshot['initiatives'] = {'error': str(e)}

        # 2. Tool calls (24h)
        try:
            from core.models import ToolCallRecord
            total = ToolCallRecord.objects.filter(created_at__gte=last_24h).count()
            failed = ToolCallRecord.objects.filter(created_at__gte=last_24h, success=False).count()
            snapshot['tool_calls_24h'] = {'total': total, 'failed': failed}
        except Exception as e:
            snapshot['tool_calls_24h'] = {'error': str(e)}

        # 3. Health (latest heartbeat)
        try:
            from core.models_heart import HeartBeat
            hb = HeartBeat.objects.order_by('-recorded_at').first()
            if hb:
                age_min = (now - hb.recorded_at).total_seconds() / 60
                snapshot['health'] = {
                    'status': getattr(hb, 'overall_status', 'unknown'),
                    'score': getattr(hb, 'health_score', None),
                    'age_minutes': round(age_min, 1),
                }
            else:
                snapshot['health'] = {'status': 'no_data'}
        except Exception as e:
            snapshot['health'] = {'error': str(e)}

        # 4. Spiders (24h)
        try:
            from core.models_unified_system import SpiderData
            items = SpiderData.objects.filter(created_at__gte=last_24h).count()
            distinct_spiders = SpiderData.objects.filter(created_at__gte=last_24h).values('spider_name').distinct().count()
            snapshot['spiders_24h'] = {'items': items, 'active_spiders': distinct_spiders}
        except Exception as e:
            snapshot['spiders_24h'] = {'error': str(e)}

        # 5. Conversations (24h)
        try:
            from core.models import HiveMindSession
            convos = HiveMindSession.objects.filter(created_at__gte=last_24h).count()
            snapshot['conversations_24h'] = {'count': convos}
        except Exception as e:
            snapshot['conversations_24h'] = {'error': str(e)}

        # 6. Signal clusters (active)
        try:
            from core.models import SignalCluster
            active_clusters = SignalCluster.objects.filter(status='active').count()
            snapshot['signal_clusters'] = {'active': active_clusters}
        except Exception as e:
            snapshot['signal_clusters'] = {'error': str(e)}

        # 7. Celery tasks (24h) — Session 983: query CeleryTaskEvent instead
        # of django_celery_results.TaskResult (which stays empty when
        # CELERY_RESULT_BACKEND is Redis, not django-db).
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            total = CeleryTaskEvent.objects.filter(started_at__gte=last_24h).count()
            failed = CeleryTaskEvent.objects.filter(started_at__gte=last_24h, status='FAILURE').count()
            snapshot['celery_24h'] = {'total': total, 'failed': failed}
        except Exception as e:
            snapshot['celery_24h'] = {'error': str(e)}

        # 8. Errors (24h)
        try:
            from core.models_diagnostic_pipeline import FailureDetection
            errors = FailureDetection.objects.filter(detected_at__gte=last_24h).count()
            snapshot['errors_24h'] = {'count': errors}
        except Exception as e:
            snapshot['errors_24h'] = {'error': str(e)}

        # 9. Blogs (24h)
        try:
            from core.models import SelfBlog
            total_blogs = SelfBlog.objects.filter(created_at__gte=last_24h).count()
            published = SelfBlog.objects.filter(created_at__gte=last_24h, publish_ready=True).count()
            snapshot['blogs_24h'] = {'total': total_blogs, 'published': published}
        except Exception as e:
            snapshot['blogs_24h'] = {'error': str(e)}

        # 10. Session 983: Actuator score — did the system actually DO things?
        # Sensors (spiders, signals) ingest data; actuators turn it into outputs.
        try:
            from core.models import Initiative, SelfBlog as _SB, HumanAttentionItem
            actuators = {}

            # Initiatives promoted to active in last 24h
            actuators['initiatives_activated'] = Initiative.objects.filter(
                status='active', updated_at__gte=last_24h
            ).count()

            # Publish-ready blog content (available for promotion)
            actuators['blogs_publish_ready'] = _SB.objects.filter(publish_ready=True).count()

            # Human decisions made (items triaged in boardroom)
            actuators['decisions_made'] = HumanAttentionItem.objects.filter(
                decided_at__gte=last_24h
            ).count()

            # Deliverables produced
            try:
                from core.models import Deliverable
                actuators['deliverables_created'] = Deliverable.objects.filter(
                    created_at__gte=last_24h
                ).count()
            except Exception:
                actuators['deliverables_created'] = 0

            snapshot['actuators_24h'] = actuators
        except Exception as e:
            snapshot['actuators_24h'] = {'error': str(e)}

        snapshot['generated_at'] = now.isoformat()

        # Session 1078: Lightweight ops pointer (SLO breach count + version SHA)
        try:
            import os
            sha = os.environ.get('RAILWAY_GIT_COMMIT_SHA', 'dev')
            snapshot['ops'] = {
                'version_sha_short': sha[:8] if len(sha) > 8 else sha,
            }
            # Quick breach check: just celery + agent task success
            celery_total = snapshot.get('celery_24h', {}).get('total', 0)
            celery_failed = snapshot.get('celery_24h', {}).get('failed', 0)
            if celery_total > 0 and (celery_total - celery_failed) / celery_total < 0.999:
                snapshot['ops']['slo_breaches'] = 1
            else:
                snapshot['ops']['slo_breaches'] = 0
        except Exception:
            pass

        cache.set(cache_key, snapshot, 60)
        logger.info(f"[{trace_id}] Status snapshot generated and cached")
        return snapshot

    def _handle_agent_introspection(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1007: Agent introspection — describe what an agent can do.

        Searches the Agent DB model and agent classes for capabilities,
        description, tools, and recent execution stats.
        """
        from core.models_unified_system import Agent, AgentExecution
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'inspect')
        # Session G3: Normalize aliases
        ACTION_ALIASES = {'detail': 'details', 'inspect': 'details'}
        action = ACTION_ALIASES.get(action, action)
        agent_query = payload.get('agent_name', '').strip().lower()

        # Session 1035-W2: List all PA tool schemas
        if action == 'tools':
            from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
            tools_list = []
            for schema in PA_TOOL_SCHEMAS:
                if not isinstance(schema, dict):
                    continue
                name = schema.get('name', '')
                desc = schema.get('description', '')[:120]
                params = schema.get('parameters', {}).get('properties', {})
                actions_enum = params.get('action', {}).get('enum', [])
                tools_list.append({
                    'name': name,
                    'description': desc,
                    'actions': actions_enum,
                    'param_count': len(params),
                })
            return {
                'action': 'tools',
                'total_tool_schemas': len(tools_list),
                'tools': tools_list,
            }

        # Session 1036+: Support list/stats actions without requiring agent_name
        if action in ('list', 'stats') or (not agent_query and action not in ('details', 'capabilities')):
            all_agents = Agent.objects.filter(is_active=True)
            total = all_agents.count()

            by_agent_type = {}
            for a in all_agents.values('agent_type').distinct():
                atype = a['agent_type'] or 'unknown'
                by_agent_type[atype] = all_agents.filter(agent_type=atype).count()

            # Get agents with recent activity (last 7 days)
            now = timezone.now()
            active_ids = set(
                AgentExecution.objects.filter(
                    created_at__gte=now - timedelta(days=7),
                ).values_list('agent_id', flat=True)
            )

            # Router breakdown: routable, blocked, non-specialist
            # Router breakdown: disjoint categories that reconcile cleanly
            # router_routable_total = blocked + rerouted + fully_enabled
            router_routable_total = 0
            blocked_agents: list = []
            rerouted_agents: list = []
            try:
                from core.agent_router import AgentRouter
                from core.models_unified_system import AgentControlEntry
                router_routable_total = len(AgentRouter.AGENT_MAP)
                # Session 1080: DB-backed blocked list
                _BLOCKED = AgentControlEntry.get_blocked_names()
                # Non-specialist: tasks get rerouted to specialist agents
                _NON_SPECIALIST = frozenset({
                    'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
                    'FullStackDeveloperAgent', 'CodeReviewAgent', 'ContentDistributionAgent',
                    'COOAgent', 'CTOAgent', 'AudioAgent',
                })
                # Make disjoint: rerouted = non_specialist minus blocked
                blocked_agents = sorted(_BLOCKED)
                rerouted_agents = sorted(_NON_SPECIALIST - _BLOCKED)
            except Exception:
                pass

            blocked_count = len(blocked_agents)
            rerouted_count = len(rerouted_agents)
            fully_enabled = router_routable_total - blocked_count - rerouted_count

            result: Dict[str, Any] = {
                'requested_action': action,
                'effective_action': action,
                'total_agents_db': total,
                'active_last_7d': len(active_ids),
                'router_routable_total': router_routable_total,
                'blocked_count': blocked_count,
                'blocked_agents': blocked_agents,
                'rerouted_count': rerouted_count,
                'rerouted_agents': rerouted_agents,
                'fully_enabled_count': fully_enabled,
                'reconciliation': f'{blocked_count} blocked + {rerouted_count} rerouted + {fully_enabled} fully_enabled = {router_routable_total} total',
                'by_agent_type': by_agent_type,
            }

            # 'list' includes the top-50 agent preview; 'stats' is aggregates only
            if action == 'list':
                agent_list = list(
                    all_agents.values('name', 'agent_type', 'specialization', 'effectiveness_score')
                    .order_by('-effectiveness_score', 'name')[:50]
                )
                result['agents'] = agent_list

            return result

        # Search by name (fuzzy)
        agents = Agent.objects.filter(name__icontains=agent_query, is_active=True)
        if not agents.exists():
            # Try without "agent" suffix
            clean_query = agent_query.replace('agent', '').strip()
            if clean_query:
                agents = Agent.objects.filter(name__icontains=clean_query, is_active=True)

        if not agents.exists():
            # List available agents as suggestions
            all_agents = list(
                Agent.objects.filter(is_active=True)
                .values_list('name', flat=True)
                .order_by('name')[:20]
            )
            return {
                'found': False,
                'query': agent_query,
                'message': f'No agent found matching "{agent_query}".',
                'suggestions': all_agents,
            }

        agent = agents.first()
        now = timezone.now()

        # Get recent execution stats
        recent_executions = AgentExecution.objects.filter(
            agent=agent,
            created_at__gte=now - timedelta(days=7),
        )
        total_recent = recent_executions.count()
        successful_recent = recent_executions.filter(status='completed').count()

        # Try to get the agent class for system_prompt and tools
        agent_class_info = {}
        try:
            from core.agent_router import get_agent_router
            router = get_agent_router()
            agent_class = router.get_agent_class(agent.name)
            if agent_class:
                agent_class_info['system_prompt'] = getattr(agent_class, 'system_prompt', '')[:500]
                tools = getattr(agent_class, 'tools', [])
                if tools:
                    agent_class_info['tools'] = [
                        t.get('function', {}).get('name', 'unknown')
                        for t in tools if isinstance(t, dict)
                    ]
        except Exception:
            pass

        return {
            'found': True,
            'agent': {
                'name': agent.name,
                'type': agent.agent_type,
                'description': agent.description,
                'specialization': agent.specialization,
                'capabilities': agent.capabilities,
                'effectiveness_score': agent.effectiveness_score,
                'total_executions': agent.total_executions,
            },
            'recent_7d': {
                'total': total_recent,
                'successful': successful_recent,
                'success_rate': f"{(successful_recent / total_recent * 100):.0f}%" if total_recent > 0 else 'N/A',
            },
            'class_info': agent_class_info,
        }

    def _handle_scheduled_tasks(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1007: Scheduled tasks visibility — list Celery Beat periodic tasks.

        Shows what tasks are scheduled, their intervals, and last run times.
        """
        from django_celery_beat.models import PeriodicTask
        from django.db.models import Q

        filter_keyword = payload.get('filter', '') or payload.get('search', '')
        limit = min(payload.get('limit', 50), 100)
        offset = payload.get('offset', 0)

        tasks = PeriodicTask.objects.filter(enabled=True).order_by('name')
        total_enabled = tasks.count()

        if filter_keyword:
            tasks = tasks.filter(
                Q(name__icontains=filter_keyword) | Q(task__icontains=filter_keyword)
            )

        filtered_count = tasks.count()
        page = tasks[offset:offset + limit]

        results = []
        for task in page:
            schedule_info = ''
            if task.crontab:
                c = task.crontab
                schedule_info = f"cron({c.minute} {c.hour} {c.day_of_week} {c.day_of_month} {c.month_of_year})"
            elif task.interval:
                i = task.interval
                schedule_info = f"every {i.every} {i.period}"

            results.append({
                'name': task.name,
                'task': task.task,
                'schedule': schedule_info,
                'queue': task.queue or 'default',
                'last_run': task.last_run_at.isoformat() if task.last_run_at else None,
                'total_runs': task.total_run_count,
            })

        return {
            'total_enabled': total_enabled,
            'filtered': filtered_count,
            'showing': len(results),
            'offset': offset,
            'filter': filter_keyword or 'all',
            'tasks': results,
        }


    def _handle_legislation(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1014: Legislation tool — congressional bill tracking via SpiderData.

        Actions:
        - search: Find bills by keyword
        - status: Status of a specific bill
        - summary: Plain-English explanation of a bill
        - trending: Most recently active bills
        - overview: Dashboard stats
        """
        from core.models_unified_system import SpiderData
        from django.db.models import Q
        import json

        action = payload.get('action', 'search')
        # Session 1062: Alias old schema actions to real handler actions
        _ACTION_ALIASES = {'list': 'trending', 'stats': 'overview', 'details': 'status'}
        action = _ACTION_ALIASES.get(action, action)
        query = payload.get('query', '')
        bill_number = payload.get('bill_number', '') or payload.get('id', '')
        limit = min(payload.get('limit', 10), 20)

        def _bills_from_row(item):
            """Session 1075: Extract bill dicts from a SpiderData row.

            Spider stores data as {'items': [...], 'source': ..., 'dedup_stats': ...}.
            Each element in 'items' is a bill dict with bill_number, topics, state, etc.
            Falls back to treating raw_data itself as a single bill for legacy rows.
            """
            raw = item.raw_data if isinstance(item.raw_data, dict) else {}
            # Primary format: envelope with items array
            if isinstance(raw.get('items'), list):
                return [b for b in raw['items'] if isinstance(b, dict)]
            # Legacy: raw_data is the bill itself
            if raw.get('bill_number'):
                return [raw]
            # Legacy: nested raw_data wrapper
            inner = raw.get('raw_data')
            if isinstance(inner, dict) and inner.get('bill_number'):
                return [inner]
            return []

        qs = SpiderData.objects.filter(spider_name='legislation').order_by('-created_at')
        total_tracked = qs.count()

        if action == 'overview':
            # Dashboard: total bills, top topics, recent activity
            recent = qs[:50]
            topic_counts: Dict[str, int] = {}
            states: set = set()
            status_counts: Dict[str, int] = {}
            bill_count = 0
            for item in recent:
                for bill in _bills_from_row(item):
                    bill_count += 1
                    for t in bill.get('topics', []):
                        topic_counts[t] = topic_counts.get(t, 0) + 1
                    state = bill.get('state', '')
                    if state:
                        states.add(state)
                    st = bill.get('status', '')
                    if st:
                        status_counts[st] = status_counts.get(st, 0) + 1

            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            return {
                'action': 'overview',
                'total_tracked': total_tracked,
                'total_bills': bill_count,
                'recent_rows_scanned': len(recent),
                'top_topics': [{'topic': t, 'count': c} for t, c in top_topics],
                'states_covered': sorted(states),
                'status_breakdown': status_counts,
            }

        elif action == 'trending':
            items = []
            for item in qs[:limit * 2]:  # scan extra rows since each has multiple bills
                for bill in _bills_from_row(item):
                    items.append({
                        'bill_number': bill.get('bill_number', ''),
                        'title': bill.get('title', ''),
                        'state': bill.get('state', ''),
                        'status': bill.get('status', ''),
                        'last_action': bill.get('last_action', ''),
                        'last_action_date': bill.get('last_action_date', ''),
                        'sponsor_count': bill.get('sponsor_count', 0),
                        'url': bill.get('url', ''),
                    })
                    if len(items) >= limit:
                        break
                if len(items) >= limit:
                    break
            return {'action': 'trending', 'items': items, 'total': total_tracked}

        elif action == 'status' and bill_number:
            # Search embedding_text first (most reliable), then scan items arrays
            matches = qs.filter(Q(embedding_text__icontains=bill_number))[:10]
            raw = None
            for m in matches:
                for bill in _bills_from_row(m):
                    if bill_number.lower() in (bill.get('bill_number', '') or '').lower():
                        raw = bill
                        break
                if raw:
                    break
            if not raw:
                return {'action': 'status', 'found': False, 'bill_number': bill_number}
            sponsors = raw.get('sponsors', [])
            return {
                'action': 'status',
                'found': True,
                'bill_number': raw.get('bill_number', bill_number),
                'title': raw.get('title', ''),
                'state': raw.get('state', ''),
                'status': raw.get('status', ''),
                'status_date': raw.get('status_date', ''),
                'last_action': raw.get('last_action', ''),
                'last_action_date': raw.get('last_action_date', ''),
                'sponsors': [s.get('name', '') for s in sponsors[:5]],
                'sponsor_count': raw.get('sponsor_count', 0),
                'committee': raw.get('committee', ''),
                'url': raw.get('url', ''),
            }

        elif action == 'summary':
            target = bill_number or query
            if not target:
                return {'action': 'summary', 'error': 'Provide a bill_number or query'}
            matches = qs.filter(Q(embedding_text__icontains=target))[:10]
            raw = None
            for m in matches:
                for bill in _bills_from_row(m):
                    bn = (bill.get('bill_number', '') or '').lower()
                    ti = (bill.get('title', '') or '').lower()
                    if target.lower() in bn or target.lower() in ti:
                        raw = bill
                        break
                if raw:
                    break
            if not raw:
                return {'action': 'summary', 'found': False, 'query': target}
            return {
                'action': 'summary',
                'found': True,
                'bill_number': raw.get('bill_number', ''),
                'title': raw.get('title', ''),
                'state': raw.get('state', ''),
                'status': raw.get('status', ''),
                'description': raw.get('description', ''),
                'plain_summary': raw.get('plain_summary', ''),
                'sponsors': [s.get('name', '') for s in raw.get('sponsors', [])[:5]],
                'committee': raw.get('committee', ''),
                'topics': raw.get('topics', []),
                'url': raw.get('url', ''),
                'congress_gov_url': raw.get('congress_gov_url', ''),
            }

        elif action == 'ask':
            # Session 1015: RAG-powered "Ask A Bill" — semantic search + LLM answer
            question = query or payload.get('question', '')
            if not question:
                return {'action': 'ask', 'error': 'Provide a question about legislation'}

            source_bills = []
            context_parts = []

            # Try embedding-based semantic search first
            try:
                from core.rag_integration import create_embedding
                import numpy as np

                q_embedding = create_embedding(question)
                if q_embedding:
                    embedded_bills = qs.filter(embedding__isnull=False)[:200]
                    scored = []
                    q_vec = np.array(q_embedding, dtype=np.float32)
                    q_norm = np.linalg.norm(q_vec)
                    if q_norm > 0:
                        q_vec = q_vec / q_norm

                    for item in embedded_bills:
                        try:
                            b_vec = np.array(item.embedding, dtype=np.float32)
                            b_norm = np.linalg.norm(b_vec)
                            if b_norm > 0:
                                b_vec = b_vec / b_norm
                            sim = float(np.dot(q_vec, b_vec))
                            if sim >= 0.25:
                                scored.append((sim, item))
                        except Exception:
                            continue

                    scored.sort(key=lambda x: x[0], reverse=True)
                    for sim, item in scored[:5]:
                        for raw in _bills_from_row(item):
                            bn = raw.get('bill_number', '')
                            title = raw.get('title', '')
                            desc = raw.get('description', '')
                            plain = raw.get('plain_summary', '')
                            sponsors = raw.get('sponsors', [])
                            topics = raw.get('topics', [])
                            sponsor_names = [s.get('name', '') for s in sponsors[:3]] if sponsors else []

                            bill_ctx = f"Bill: {bn} — {title}\n"
                            if desc:
                                bill_ctx += f"Description: {desc}\n"
                            if plain:
                                bill_ctx += f"Summary: {plain}\n"
                            if sponsor_names:
                                bill_ctx += f"Sponsors: {', '.join(sponsor_names)}\n"
                            if topics:
                                bill_ctx += f"Topics: {', '.join(topics[:5])}\n"
                            context_parts.append(bill_ctx)
                            source_bills.append({
                                'bill_number': bn,
                                'title': title,
                                'score': round(sim, 3),
                                'url': raw.get('url', ''),
                            })
            except Exception as e:
                logger.warning(f"Embedding search failed for ask action: {e}")

            # Fallback: keyword search if no embedding results
            if not source_bills:
                import re as _re
                # Extract meaningful keywords (strip stopwords)
                stopwords = {'what', 'which', 'how', 'does', 'will', 'are', 'is', 'the',
                             'a', 'an', 'in', 'on', 'about', 'any', 'do', 'can', 'to',
                             'of', 'for', 'and', 'or', 'this', 'that', 'my', 'me', 'us',
                             'being', 'been', 'bills', 'bill', 'legislation', 'congress',
                             'congressional', 'affect', 'impact', 'explain', 'tell'}
                words = _re.findall(r'[a-zA-Z]+', question.lower())
                keywords = [w for w in words if w not in stopwords and len(w) > 1]
                # Build Q filter from keywords
                q_filter = Q()
                for kw in keywords[:4]:
                    q_filter |= Q(embedding_text__icontains=kw) | Q(raw_data__title__icontains=kw)
                if not q_filter:
                    q_filter = Q(embedding_text__icontains=question[:20])
                kw_matches = qs.filter(q_filter)[:5]
                for item in kw_matches:
                    for raw in _bills_from_row(item):
                        bn = raw.get('bill_number', '')
                        title = raw.get('title', '')
                        desc = raw.get('description', '')
                        plain = raw.get('plain_summary', '')
                        bill_ctx = f"Bill: {bn} — {title}\n"
                        if desc:
                            bill_ctx += f"Description: {desc}\n"
                        if plain:
                            bill_ctx += f"Summary: {plain}\n"
                        context_parts.append(bill_ctx)
                        source_bills.append({
                            'bill_number': bn,
                            'title': title,
                            'score': 0,
                            'url': raw.get('url', ''),
                        })

            if not source_bills:
                # If we have legislation data but no matches, say so specifically
                if total_tracked > 0:
                    no_match_msg = (
                        f"I searched {total_tracked} tracked bills but couldn't find any "
                        f"matching your question. Try asking about specific topics like "
                        f"healthcare, immigration, education, environment, or technology."
                    )
                else:
                    no_match_msg = (
                        "No legislation data is available yet. The legislation spider "
                        "may not have run yet."
                    )
                return {
                    'action': 'ask',
                    'question': question,
                    'answer': no_match_msg,
                    'source_bills': [],
                    'sources_count': 0,
                }

            # Build RAG prompt and call LLM
            bill_context = "\n---\n".join(context_parts)
            system_prompt = (
                "You are a nonpartisan legislative analyst. Answer the user's question based ONLY "
                "on the bill text provided below. Quote specific bill numbers when referencing legislation. "
                "Explain in plain language that anyone can understand. Be factual and nonpartisan. "
                "If the provided bills do not address the question, say so honestly.\n\n"
                f"BILLS:\n{bill_context}"
            )

            try:
                from core.llm_enforcer import LLMEnforcer
                enforcer = LLMEnforcer()
                result = enforcer.enforce_real_ai(
                    prompt=question,
                    context=system_prompt,
                    agent_name="AskABill",
                    task_type="legislation_rag",
                    max_tokens=1500,
                )
                answer = result.get('content', '') if isinstance(result, dict) else str(result)
            except Exception as e:
                logger.error(f"LLM call failed for Ask A Bill: {e}")
                answer = f"I found {len(source_bills)} relevant bill(s) but could not generate an AI analysis right now. Please try again."

            return {
                'action': 'ask',
                'question': question,
                'answer': answer,
                'source_bills': source_bills,
                'sources_count': len(source_bills),
            }

        else:
            # Default: search by keyword
            if not query:
                return {'action': 'search', 'error': 'Provide a search query'}
            matches = qs.filter(
                Q(embedding_text__icontains=query) |
                Q(raw_data__title__icontains=query)
            )[:limit]
            items = []
            for item in matches:
                for raw in _bills_from_row(item):
                    items.append({
                        'bill_number': raw.get('bill_number', ''),
                        'title': raw.get('title', ''),
                        'state': raw.get('state', ''),
                        'status': raw.get('status', ''),
                        'sponsor_count': raw.get('sponsor_count', 0),
                        'last_action_date': raw.get('last_action_date', ''),
                        'url': raw.get('url', ''),
                    })
            return {
                'action': 'search',
                'query': query,
                'items': items,
                'total': len(items),
            }


    # =========================================================================
    # Session 1031: Dream Tool — browse, approve, dismiss dreams via PA
    # =========================================================================

    def _handle_dream(self, tool_name, payload, user_id, trace_id) -> Dict:
        """Handle dream browsing and approval actions."""
        from core.models_unified_system import AgentDream
        from django.db.models import Avg, Count, Q

        action = payload.get('action', 'list_top')
        dream_id = payload.get('id')

        if action == 'list_top':
            limit = payload.get('limit', 10)
            dreams = (
                AgentDream.objects
                .filter(composite_score__gte=0.5)
                .select_related('agent')
                .order_by('-composite_score', '-dreamed_at')[:limit]
            )
            return {
                'action': 'list_top',
                'dreams': [
                    {
                        'id': str(d.id),
                        'title': d.title,
                        'content_preview': d.content[:200],
                        'dream_type': d.dream_type,
                        'agent_name': d.agent.name if d.agent else 'Unknown',
                        'composite_score': d.composite_score,
                        'creativity_score': d.creativity_score,
                        'actionability_score': d.actionability_score,
                        'relevance_score': d.relevance_score,
                        'decision_outcome': d.decision_outcome or 'none',
                        'dreamed_at': d.dreamed_at.isoformat(),
                    }
                    for d in dreams
                ],
                'count': len(dreams),
            }

        elif action == 'details':
            if not dream_id:
                raise ValueError("id is required for dream details")
            dream = AgentDream.objects.select_related('agent').get(id=dream_id)
            return {
                'action': 'details',
                'dream': {
                    'id': str(dream.id),
                    'title': dream.title,
                    'content': dream.content,
                    'dream_type': dream.dream_type,
                    'agent_name': dream.agent.name if dream.agent else 'Unknown',
                    'origin': dream.origin,
                    'inspiration_source': dream.inspiration_source,
                    'related_topics': dream.related_topics,
                    'composite_score': dream.composite_score,
                    'creativity_score': dream.creativity_score,
                    'actionability_score': dream.actionability_score,
                    'relevance_score': dream.relevance_score,
                    'vividness_score': dream.vividness_score,
                    'promoted_to_decision': dream.promoted_to_decision,
                    'decision_outcome': dream.decision_outcome or 'none',
                    'user_reaction': dream.user_reaction,
                    'shown_to_user': dream.shown_to_user,
                    'initiative_id': str(dream.initiative_id) if dream.initiative_id else None,  # type: ignore[attr-defined]
                    'dreamed_at': dream.dreamed_at.isoformat(),
                },
            }

        elif action == 'approve':
            if not dream_id:
                raise ValueError("id is required to approve a dream")
            dream = AgentDream.objects.get(id=dream_id)
            dream.decision_outcome = 'approved'
            dream.user_reaction = 'loved'
            dream.user_feedback = payload.get('feedback', 'Approved via PA')
            dream.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])
            # post_save signal fires: promote_to_initiative() + execute_single_dream.delay()
            return {
                'action': 'approve',
                'id': str(dream.id),
                'title': dream.title,
                'success': True,
                'message': 'Dream approved — initiative creation and execution triggered.',
            }

        elif action == 'dismiss':
            if not dream_id:
                raise ValueError("id is required to dismiss a dream")
            dream = AgentDream.objects.get(id=dream_id)
            dream.decision_outcome = 'rejected'
            dream.user_reaction = 'dismissed'
            dream.user_feedback = payload.get('feedback', 'Dismissed via PA')
            dream.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])
            return {
                'action': 'dismiss',
                'id': str(dream.id),
                'title': dream.title,
                'success': True,
            }

        elif action == 'create':
            title = payload.get('title', '').strip()
            content = payload.get('content', '').strip()
            dream_type = payload.get('dream_type', 'user_request')
            if not title:
                raise ValueError("'title' is required for create action")

            # Resolve PA agent as the dreaming agent
            from core.models_unified_system import Agent
            pa_agent = Agent.objects.filter(name__icontains='personal assistant').first()
            if not pa_agent:
                pa_agent = Agent.objects.filter(is_active=True).first()
            if not pa_agent:
                raise ValueError("No active agent found to attribute dream to")

            dream = AgentDream.objects.create(
                agent=pa_agent,
                title=title,
                content=content or title,
                dream_type=dream_type,
                shown_to_user=True,
            )
            return {
                'action': 'create',
                'id': str(dream.id),
                'title': dream.title,
                'dream_type': dream.dream_type,
                'success': True,
            }

        elif action == 'stats':
            total = AgentDream.objects.count()
            by_outcome = dict(
                AgentDream.objects
                .exclude(decision_outcome='')
                .values_list('decision_outcome')
                .annotate(c=Count('id'))
                .values_list('decision_outcome', 'c')
            )
            shown_count = AgentDream.objects.filter(shown_to_user=True).count()
            with_initiative = AgentDream.objects.filter(initiative__isnull=False).count()
            avg_scores = AgentDream.objects.aggregate(
                avg_composite=Avg('composite_score'),
                avg_creativity=Avg('creativity_score'),
                avg_actionability=Avg('actionability_score'),
                avg_relevance=Avg('relevance_score'),
            )
            return {
                'action': 'stats',
                'total_dreams': total,
                'by_outcome': by_outcome,
                'shown_to_user': shown_count,
                'with_initiative': with_initiative,
                'avg_scores': {
                    k: round(v, 3) if v else 0
                    for k, v in avg_scores.items()
                },
            }

        else:
            raise ValueError(f"Unknown dream action: {action}")

    # ── Session 1034: Research-and-Create ──────────────────────────────

    def _handle_research_and_create(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1034: Chain web search → LLM content generation → Deliverable save.

        User says something like "Research Clawbot and create a comparison for a YouTube video".
        This handler:
        1. Runs web search on the research topic
        2. Sends research results + user's creation request to LLM
        3. Saves the generated content as a Deliverable
        4. Returns the content + deliverable link
        """
        from core.tools.web_search import WebSearchTool
        from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest
        from core.models_deliverables import Deliverable
        from django.utils.text import slugify
        import uuid as _uuid

        message = payload.get('query', '')
        research_topic = payload.get('research_topic', message)
        output_type = payload.get('output_type', 'content')
        output_type_label = payload.get('output_type_label', 'Content')

        # Step 1: Web search
        search_tool = WebSearchTool()
        search_result = search_tool.execute(query=research_topic, max_results=8, search_type='text')

        search_data = []
        if search_result.get('success'):
            raw_results = search_result.get('data', {}).get('results', [])
            for r in raw_results[:8]:
                search_data.append({
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'snippet': r.get('snippet', ''),
                })

        # Build research context for LLM
        research_text = ""
        for i, item in enumerate(search_data, 1):
            research_text += f"\n{i}. **{item['title']}**\n   URL: {item['url']}\n   {item['snippet']}\n"

        if not research_text:
            research_text = "(No search results found. Generate content based on general knowledge.)"

        # Step 2: LLM generation
        # Import platform identity for context
        from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint
        platform_identity = UnifiedPAEntrypoint._get_platform_identity()

        system_prompt = f"""You are a professional content creator for the Donkey Betz Unified AI Platform.

{platform_identity}

TASK: The user asked: "{message}"

Based on the research data below, create the requested content. Follow these rules:
- Ground all claims in the research data provided — cite sources with URLs where relevant
- Be comprehensive but well-structured with clear sections
- Use markdown formatting (headers, bullet points, bold text)
- If creating a YouTube script, include: Hook, Introduction, Main Segments, Call to Action, Outro
- If creating a comparison, use a structured format with clear categories
- If creating a report/analysis, include Executive Summary, Key Findings, Recommendations
- Make the content ready to use — not a draft outline, but complete content
- Length: 800-2000 words depending on complexity

RESEARCH DATA:
{research_text}"""

        try:
            registry = get_llm_provider_registry()
            llm_response = registry.complete(
                provider='openai',
                model_id='gpt-4.1-mini',
                request=LLMRequest(
                    prompt=f'Create the {output_type_label} now. Make it complete and ready to use.',
                    system_prompt=system_prompt,
                    max_tokens=4000,
                    temperature=0.7,
                )
            )
            generated_content = llm_response.content if llm_response and llm_response.success and llm_response.content else ''
        except Exception as e:
            logger.error(f"[{trace_id}] Research-and-create LLM failed: {e}")
            generated_content = ''

        if not generated_content:
            return {
                'success': False,
                'error': 'Content generation failed. Research results were gathered but LLM could not generate the content.',
                'search_results': search_data,
            }

        # Step 3: Save as Deliverable
        # Use the extracted research_topic for a clean title
        import re as _rc_re
        clean_topic = research_topic[:100].strip()
        if clean_topic:
            title = f"{output_type_label}: {clean_topic[0].upper() + clean_topic[1:]}"
        else:
            title = f"{output_type_label}: Research Output"

        slug_base = slugify(title)[:250]
        slug = f"{slug_base}-{_uuid.uuid4().hex[:6]}"

        # Determine deliverable_type from output_type
        type_map = {
            'script': 'script',
            'comparison': 'analysis',
            'report': 'report',
            'analysis': 'analysis',
            'outline': 'plan',
            'summary': 'document',
            'brief': 'document',
            'guide': 'document',
            'plan': 'plan',
            'proposal': 'strategy',
        }
        deliverable_type = type_map.get(output_type, 'document')

        try:
            # Session 1065: Resolve user so deliverable shows as "You"
            resolved_user = None
            if user_id:
                from django.contrib.auth import get_user_model
                _User = get_user_model()
                try:
                    resolved_user = _User.objects.get(id=user_id)
                except _User.DoesNotExist:
                    pass

            deliverable = Deliverable.objects.create(
                title=title,
                slug=slug,
                deliverable_type=deliverable_type,
                category='PA Research & Create',
                tags=['pa-created', 'research-and-create', output_type],
                content=generated_content,
                content_format='markdown',
                agent_name='PersonalAssistantAgent',
                user=resolved_user,
                quality_score=0.7,
                confidence_score=0.7,
                metadata={
                    'research_query': research_topic,
                    'search_results_count': len(search_data),
                    'output_type': output_type,
                    'source': 'pa_research_and_create',
                    'trace_id': trace_id,
                },
            )
            deliverable_id = str(deliverable.id)
            logger.info(f"[{trace_id}] Research-and-create saved deliverable: {deliverable_id}")
        except Exception as e:
            logger.error(f"[{trace_id}] Failed to save deliverable: {e}")
            deliverable_id = None

        return {
            'success': True,
            'content': generated_content,
            'title': title,
            'output_type': output_type,
            'output_type_label': output_type_label,
            'deliverable_id': deliverable_id,
            'search_results_count': len(search_data),
            'search_results': search_data[:3],  # Include top 3 for reference
        }


    # ── Session 1048: Task Volume Breakdown ────────────────────────────────

    def _handle_task_breakdown(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1048: Celery task volume breakdown.

        action='summary': aggregated task volume with totals, by_task, by_agent
        action='drilldown': recent executions for a specific task_name
        """
        from datetime import timedelta
        from django.db.models import Count, Q, Avg
        from django.utils import timezone
        from core.models_celery_telemetry import CeleryTaskEvent

        WINDOW_MAP = {
            '15m': 15,
            '60m': 60,
            '2h': 120,
            '6h': 360,
            '24h': 1440,
        }

        action = payload.get('action', 'summary')
        window = payload.get('window', '60m')
        minutes = WINDOW_MAP.get(window, 60)
        cutoff = timezone.now() - timedelta(minutes=minutes)

        if action == 'drilldown':
            task_name = payload.get('task_name', '')
            if not task_name:
                return {'error': 'task_name is required for drilldown'}

            limit = min(int(payload.get('limit', 50)), 200)
            status = payload.get('status', '')
            qs = CeleryTaskEvent.objects.filter(task_name=task_name, started_at__gte=cutoff)
            if status:
                qs = qs.filter(status=status.upper())
            rows = qs.order_by('-started_at')[:limit]

            executions = []
            for r in rows:
                dur_ms = round(r.duration_seconds * 1000) if r.duration_seconds else None
                executions.append({
                    'task_id': r.task_id,
                    'started_at': r.started_at.isoformat() if r.started_at else None,
                    'finished_at': r.finished_at.isoformat() if r.finished_at else None,
                    'duration_ms': dur_ms,
                    'status': r.status,
                    'queue': r.queue or 'default',
                    'worker': r.worker,
                    'error_type': r.error_type or None,
                    'error_message': (r.error_message or '')[:500] or None,
                })

            return {
                'action': 'drilldown',
                'task_name': task_name,
                'window': window,
                'count': len(executions),
                'executions': executions,
            }

        # ── Summary ──
        limit = min(int(payload.get('limit', 25)), 50)
        qs = CeleryTaskEvent.objects.filter(started_at__gte=cutoff)

        totals = qs.aggregate(
            tasks=Count('id'),
            success=Count('id', filter=Q(status='SUCCESS')),
            failure=Count('id', filter=Q(status='FAILURE')),
            started=Count('id', filter=Q(status='STARTED')),
        )

        by_task_qs = (
            qs.values('task_name')
            .annotate(
                count_total=Count('id'),
                count_success=Count('id', filter=Q(status='SUCCESS')),
                count_failure=Count('id', filter=Q(status='FAILURE')),
                avg_duration=Avg('duration_seconds'),
            )
            .order_by('-count_total')[:limit]
        )

        top_task_names = [row['task_name'] for row in by_task_qs]

        # Percentiles
        def _percentile(sorted_list, p):
            if not sorted_list:
                return 0
            k = (len(sorted_list) - 1) * p
            f = int(k)
            return sorted_list[f]

        duration_rows = (
            qs.filter(task_name__in=top_task_names, duration_seconds__isnull=False)
            .values_list('task_name', 'duration_seconds')
        )
        durations_by_task: Dict[str, list] = {}
        for tn, dur in duration_rows:
            durations_by_task.setdefault(tn, []).append(dur)
        for v in durations_by_task.values():
            v.sort()

        # Queue breakdown
        queue_rows = (
            qs.filter(task_name__in=top_task_names)
            .values('task_name', 'queue')
            .annotate(count=Count('id'))
        )
        queues_by_task: Dict[str, list] = {}
        for row in queue_rows:
            queues_by_task.setdefault(row['task_name'], []).append(
                {'queue': row['queue'] or 'default', 'count': row['count']}
            )

        by_task = []
        for row in by_task_qs:
            tn = row['task_name']
            ct = row['count_total']
            cf = row['count_failure']
            durs = durations_by_task.get(tn, [])
            avg_dur = row['avg_duration'] or 0
            by_task.append({
                'task_name': tn,
                'count_total': ct,
                'count_success': row['count_success'],
                'count_failure': cf,
                'failure_rate': round(cf / ct, 3) if ct else 0,
                'avg_duration_ms': round(avg_dur * 1000),
                'p50_ms': round(_percentile(durs, 0.5) * 1000),
                'p95_ms': round(_percentile(durs, 0.95) * 1000),
                'top_queues': sorted(
                    queues_by_task.get(tn, []),
                    key=lambda q: q['count'], reverse=True
                )[:3],
            })

        # By agent
        from core.models import AgentExecution
        by_agent_raw = list(
            AgentExecution.objects.filter(created_at__gte=cutoff)
            .values('agent__name')
            .annotate(
                execution_count=Count('id'),
                count_failure=Count('id', filter=Q(status='failed')),
            )
            .order_by('-execution_count')[:limit]
        )
        by_agent = []
        for row in by_agent_raw:
            ec = row['execution_count']
            cf = row['count_failure']
            by_agent.append({
                'agent_name': row['agent__name'],
                'execution_count': ec,
                'count_failure': cf,
                'failure_rate': round(cf / ec, 3) if ec else 0,
            })

        return {
            'action': 'summary',
            'window': window,
            'generated_at': timezone.now().isoformat(),
            'totals': totals,
            'by_task': by_task,
            'by_agent': by_agent,
        }


    # ── Session 1071: Platform Awareness ─────────────────────────────────────

    def _handle_platform_awareness(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Platform awareness: manifest, routes, capabilities, deploy verification."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from core.views_app_manifest import get_manifest_data

        action = payload.get('action', 'get_manifest')

        # Resolve user object for RBAC filtering
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        if action == 'verify_deploy':
            # Admin-only deploy verification
            if user and (user.is_superuser or user.is_staff):
                from core.views_deploy_verify import run_verification
                import os
                base_url = os.getenv(
                    'DEPLOY_BASE_URL',
                    'https://donkey-betz-platform-production.up.railway.app'
                )
                from rest_framework.authtoken.models import Token
                token_obj = Token.objects.filter(user=user).first()
                token = token_obj.key if token_obj else None
                return run_verification(base_url, token=token)
            return {'error': 'Admin access required for deploy verification'}

        if not user:
            # If no user, return unfiltered manifest
            from core.views_app_manifest import _load_manifest
            manifest = _load_manifest()
        else:
            manifest = get_manifest_data(user)

        routes = manifest.get('routes', [])

        if action == 'get_manifest':
            return manifest

        if action == 'list_routes':
            category = payload.get('category')
            auth_required = payload.get('auth_required')
            filtered = routes
            if category:
                filtered = [r for r in filtered if r.get('category') == category]
            if auth_required is not None:
                filtered = [r for r in filtered if r.get('authRequired') == auth_required]
            return {
                'count': len(filtered),
                'routes': filtered,
            }

        if action == 'check_route':
            path = payload.get('path', '')
            match = next((r for r in routes if r.get('path') == path), None)
            if match:
                return {'exists': True, 'route': match}
            return {'exists': False, 'path': path}

        if action == 'system_overview':
            categories = {}
            for r in routes:
                cat = r.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            studios = manifest.get('studios', {})
            capabilities = manifest.get('capabilities', {})
            api_deps = manifest.get('api_dependencies', {})
            return {
                'route_count': len(routes),
                'routes_by_category': categories,
                'studio_count': sum(1 for s in studios.values() if isinstance(s, dict) and s.get('enabled')),
                'studios': list(studios.keys()),
                'capability_count': sum(1 for v in capabilities.values() if v),
                'capabilities': capabilities,
                'build_sha': manifest.get('build_sha', 'unknown'),
                'api_dependency_routes': len(api_deps),
                'api_dependency_total_endpoints': sum(len(v) for v in api_deps.values() if isinstance(v, list)),
            }

        if action == 'list_api_dependencies':
            api_deps = manifest.get('api_dependencies', {})
            path = payload.get('path')
            writes_only = payload.get('writes_only', False)
            if path:
                deps = api_deps.get(path, [])
                if not isinstance(deps, list):
                    deps = []
                if writes_only:
                    deps = [d for d in deps if isinstance(d, dict) and d.get('writes')]
                return {'route': path, 'endpoint_count': len(deps), 'endpoints': deps}
            else:
                result = {}
                for rp, rp_deps in api_deps.items():
                    if not isinstance(rp_deps, list):
                        continue
                    filtered = rp_deps
                    if writes_only:
                        filtered = [d for d in rp_deps if isinstance(d, dict) and d.get('writes')]
                    result[rp] = {'endpoint_count': len(filtered), 'endpoints': filtered}
                return {'route_count': len(result), 'routes': result}

        if action == 'tool_registry':
            from core.views_app_manifest import _summarize_tool_schemas
            tools = _summarize_tool_schemas()
            return {'action': 'tool_registry', 'tools': tools, 'count': len(tools)}

        return {'error': f'Unknown action: {action}'}

    # ── Session 1071: Studio Tool ────────────────────────────────────────────

    def _handle_studio(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Unified creative studio: generate images, videos, audio, check jobs."""
        action = payload.get('action', 'list_jobs')

        if action == 'generate_image':
            # Session 1088: Dispatch to Celery async to avoid PA/Railway proxy timeout
            from core.tasks import execute_agent_task
            raw_prompt = payload.get('prompt', '')
            # Prefix with "Generate image:" so _is_media_task_blocked() recognizes it
            task_text = f'Generate image: {raw_prompt}' if not raw_prompt.lower().startswith(('generat', 'creat', 'make', 'design', 'draw', 'render', 'produc')) else raw_prompt
            context = {}
            if payload.get('style'):
                context['style'] = payload['style']
            if payload.get('model'):
                context['model'] = payload['model']
            if payload.get('width'):
                context['width'] = payload['width']
            if payload.get('height'):
                context['height'] = payload['height']
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = execute_agent_task.apply_async(
                args=['ImageAgent', task_text, context], queue='agents',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'ImageAgent',
                'message': f'Image generation dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        if action == 'generate_video':
            # Session 1077: Dispatch to Celery async to avoid PA tool timeout
            from core.tasks import execute_agent_task
            raw_prompt = payload.get('prompt', '')
            task_text = f'Generate video: {raw_prompt}' if not raw_prompt.lower().startswith(('generat', 'creat', 'make', 'produc', 'render')) else raw_prompt
            context = {}
            if payload.get('style'):
                context['style'] = payload['style']
            if payload.get('duration'):
                context['duration'] = payload['duration']
            if payload.get('ratio'):
                context['ratio'] = payload['ratio']
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = execute_agent_task.apply_async(
                args=['VideoAgent', task_text, context], queue='agents',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'VideoAgent',
                'message': f'Video generation dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        if action == 'generate_talking_video':
            # Dispatch to Celery async — pipeline is long-running (TTS + video + lip sync)
            from core.tasks import execute_agent_task
            raw_script = payload.get('script') or payload.get('prompt', '')
            task_text = f'Generate talking character video: {raw_script}'
            context = {
                'image_url': payload.get('image_url', ''),
                'script': raw_script,
                'voice': payload.get('voice', 'Rachel'),
                'duration': payload.get('duration', 10),
                'lipsync_model': payload.get('lipsync_model', 'auto'),
                'mode': payload.get('mode', 'multi_clip'),
                'sync_mode': payload.get('sync_mode', 'cut_off'),
                'color_grade': payload.get('color_grade'),
            }
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = execute_agent_task.apply_async(
                args=['TalkingCharacterAgent', task_text, context], queue='agents',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'TalkingCharacterAgent',
                'message': f'Talking character video dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        if action == 'create_talking_video':
            # Pipeline: generate character image → talking video in one task
            from core.tasks import create_talking_video_task
            image_prompt = payload.get('prompt', '')
            script = payload.get('script', '')
            if not image_prompt:
                return {'error': 'prompt is required (image description for the character)'}
            if not script:
                return {'error': 'script is required (what the character should say)'}
            context = {
                'voice': payload.get('voice', 'Rachel'),
                'duration': payload.get('duration', 10),
                'lipsync_model': payload.get('lipsync_model', 'auto'),
                'mode': payload.get('mode', 'multi_clip'),
                'sync_mode': payload.get('sync_mode', 'cut_off'),
                'color_grade': payload.get('color_grade'),
            }
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = create_talking_video_task.apply_async(
                args=[image_prompt, script, context], queue='agents',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'ImageAgent → TalkingCharacterAgent',
                'message': (
                    f'Talking video pipeline dispatched (task {celery_task.id}). '
                    f'Will generate character image then create talking video. '
                    f'Use job_status to check progress.'
                ),
            }

        if action == 'generate_audio':
            # Session 1088: Dispatch to Celery async (matches video/image pattern)
            from core.tasks import execute_agent_task
            raw_prompt = payload.get('prompt', '')
            task_text = f'Generate audio: {raw_prompt}' if not raw_prompt.lower().startswith(('generat', 'creat', 'make', 'produc', 'render')) else raw_prompt
            context = {}
            if payload.get('voice'):
                context['voice'] = payload['voice']
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = execute_agent_task.apply_async(
                args=['AudioAgent', task_text, context], queue='agents',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'AudioAgent',
                'message': f'Audio generation dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        if action == 'job_status':
            job_id = payload.get('job_id')
            if not job_id:
                return {'error': 'job_id is required for job_status'}

            # 1. Check CeleryTaskEvent (completed tasks with telemetry)
            try:
                from core.models_celery_telemetry import CeleryTaskEvent
                event = CeleryTaskEvent.objects.filter(task_id=job_id).first()
                if event:
                    result = {
                        'job_id': job_id,
                        'status': event.status,
                        'started_at': event.started_at.isoformat() if event.started_at else None,
                        'finished_at': event.finished_at.isoformat() if event.finished_at else None,
                        'duration_ms': round(event.duration_seconds * 1000) if event.duration_seconds else None,
                    }
                    # Enrich with AgentExecution output if available
                    result.update(self._get_agent_execution_output(job_id))
                    return result
            except Exception:
                pass

            # 2. Check Celery AsyncResult (in-flight or recently completed)
            try:
                from celery.result import AsyncResult
                async_result = AsyncResult(job_id)
                state = async_result.state  # PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
                result = {
                    'job_id': job_id,
                    'status': state.lower(),
                }
                if state == 'SUCCESS':
                    task_return = async_result.result or {}
                    if isinstance(task_return, dict):
                        result['status'] = 'completed'
                        result['success'] = task_return.get('success', True)
                        result['agent'] = task_return.get('agent_name', '')
                        result['execution_time_ms'] = task_return.get('execution_time_ms')
                        # Enrich with full content/media from AgentExecution
                        exec_id = task_return.get('execution_id')
                        if exec_id:
                            result.update(self._get_agent_execution_output(job_id, exec_id))
                        # Fallback: use content from task return if enrichment found nothing
                        if not result.get('content'):
                            result['content'] = task_return.get('content', '')
                elif state == 'FAILURE':
                    result['status'] = 'failed'
                    result['error'] = str(async_result.result)[:500] if async_result.result else 'Unknown error'
                elif state == 'STARTED':
                    result['status'] = 'running'
                elif state == 'PENDING':
                    result['status'] = 'queued'
                return result
            except Exception as e:
                logger.debug(f"AsyncResult check failed for {job_id}: {e}")

            return {'job_id': job_id, 'status': 'unknown'}

        if action == 'list_jobs':
            limit = min(int(payload.get('limit', 10)), 50)
            jobs = []
            try:
                from core.models import ImageHistory
                for img in ImageHistory.objects.order_by('-created_at')[:limit]:
                    jobs.append({
                        'id': str(img.id),
                        'type': 'image',
                        'prompt': getattr(img, 'prompt', '')[:100] if getattr(img, 'prompt', '') else '',
                        'created_at': img.created_at.isoformat() if hasattr(img, 'created_at') and img.created_at else None,
                    })
            except Exception:
                pass
            try:
                from core.models import VideoHistory
                for vid in VideoHistory.objects.order_by('-created_at')[:limit]:
                    jobs.append({
                        'id': str(vid.id),
                        'type': 'video',
                        'prompt': getattr(vid, 'prompt', '')[:100] if getattr(vid, 'prompt', '') else '',
                        'created_at': vid.created_at.isoformat() if hasattr(vid, 'created_at') and vid.created_at else None,
                    })
            except Exception:
                pass
            try:
                from core.models import AudioHistory
                for aud in AudioHistory.objects.order_by('-created_at')[:limit]:
                    jobs.append({
                        'id': str(aud.id),
                        'type': 'audio',
                        'prompt': getattr(aud, 'text', '')[:100] if getattr(aud, 'text', '') else '',
                        'created_at': aud.created_at.isoformat() if hasattr(aud, 'created_at') and aud.created_at else None,
                    })
            except Exception:
                pass
            # Sort by created_at descending
            jobs.sort(key=lambda j: j.get('created_at') or '', reverse=True)
            return {
                'count': len(jobs[:limit]),
                'jobs': jobs[:limit],
            }

        return {'error': f'Unknown studio action: {action}'}

    def _handle_persona(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Session 1088: Browse and invoke 139 DB-only persona agents."""
        from core.models_unified_system import Agent as AgentModel
        from core.agent_router import AgentRouter

        action = payload.get('action', 'list')

        if action == 'list':
            category = payload.get('category')
            qs = AgentModel.objects.filter(is_active=True)

            # Exclude AGENT_MAP agents so we only show DB-only personas
            map_names = set(AgentRouter.AGENT_MAP.keys())
            qs = qs.exclude(name__in=map_names)

            if category:
                qs = qs.filter(agent_type=category)

            personas = list(
                qs.order_by('agent_type', 'name')
                .values('name', 'agent_type', 'specialization', 'description',
                        'effectiveness_score', 'total_executions')[:50]
            )

            # Truncate descriptions for LLM context
            for p in personas:
                if p.get('description') and len(p['description']) > 150:
                    p['description'] = p['description'][:147] + '...'

            # Category summary
            from collections import Counter
            all_types = list(
                AgentModel.objects.filter(is_active=True)
                .exclude(name__in=map_names)
                .values_list('agent_type', flat=True)
            )
            categories = dict(Counter(all_types).most_common())

            return {
                'action': 'list',
                'filter': category,
                'count': len(personas),
                'personas': personas,
                'categories': categories,
            }

        if action == 'invoke':
            persona_name = payload.get('persona_name')
            task = payload.get('task')
            if not persona_name:
                return {'error': 'persona_name is required for invoke action'}
            if not task:
                return {'error': 'task is required for invoke action'}

            # Verify persona exists and is active
            agent_obj = AgentModel.objects.filter(
                name=persona_name, is_active=True
            ).first()
            if not agent_obj:
                return {'error': f'Persona "{persona_name}" not found or inactive'}

            # Route through AgentRouter (DynamicPersonaAgent fallback)
            router = AgentRouter()
            result = router.route(persona_name, task, context=payload.get('context', {}))

            response = {
                'action': 'invoke',
                'persona': persona_name,
                'success': result.success if result else False,
                'output': result.message if result else 'Persona execution failed',
            }
            if result and result.data:
                response['data'] = result.data
            return response

        return {'error': f'Unknown persona action: {action}'}

    # ── Session 1069: Platform Config ─────────────────────────────────────────

    def _handle_platform_config(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1069: Platform config introspection — runtime settings, LLM providers,
        env vars (secrets masked), and feature flags.
        """
        import os
        from django.conf import settings as django_settings

        action = payload.get('action', 'overview')

        SECRET_PATTERNS = (
            'KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'CREDENTIAL',
            'DSN', 'DATABASE_URL', 'REDIS_URL', 'BROKER_URL',
        )

        def _mask(key, value):
            """Mask secret values, show first 8 chars + ..."""
            if not value:
                return value
            val = str(value)
            for pat in SECRET_PATTERNS:
                if pat in key.upper():
                    return val[:8] + '...' if len(val) > 8 else '***'
            return val

        if action == 'overview':
            return {
                'action': 'overview',
                'service_context': os.environ.get('RAILWAY_SERVICE_NAME', 'local'),
                'platform': getattr(django_settings, 'PLATFORM_NAME', 'unknown'),
                'debug': django_settings.DEBUG,
                'allowed_hosts': getattr(django_settings, 'ALLOWED_HOSTS', []),
                'default_llm_provider': getattr(django_settings, 'LLM_DEFAULT_PROVIDER', 'unknown'),
                'database_engine': django_settings.DATABASES.get('default', {}).get('ENGINE', 'unknown'),
                'database_name': django_settings.DATABASES.get('default', {}).get('NAME', 'unknown'),
                'redis_url': _mask('REDIS_URL', os.environ.get('REDIS_URL', 'not set')),
                'celery_broker': _mask('BROKER_URL', getattr(django_settings, 'CELERY_BROKER_URL', 'not set')),
                'cors_allow_all': getattr(django_settings, 'CORS_ALLOW_ALL_ORIGINS', False),
                'csrf_trusted_origins': getattr(django_settings, 'CSRF_TRUSTED_ORIGINS', []),
                'frontend_url': getattr(django_settings, 'FRONTEND_URL', 'not set'),
                'backend_url': getattr(django_settings, 'BACKEND_URL', 'not set'),
                'railway_environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
                'railway_service': os.environ.get('RAILWAY_SERVICE_NAME', 'local'),
            }

        elif action == 'web_config':
            # Fetch config from the web service via its internal API
            # so the PA can compare web vs celery-pa environments
            import urllib.request
            import json as _json
            web_url = os.environ.get(
                'WEB_SERVICE_URL',
                'https://donkey-betz-platform-production.up.railway.app'
            )
            try:
                req = urllib.request.Request(
                    f'{web_url}/api/v1/health/',
                    headers={'Accept': 'application/json'},
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    health_data = _json.loads(resp.read())
            except Exception as e:
                health_data = {'error': str(e)}

            try:
                req2 = urllib.request.Request(
                    f'{web_url}/api/internal/config-snapshot/',
                    headers={'Accept': 'application/json'},
                )
                with urllib.request.urlopen(req2, timeout=5) as resp:
                    web_config = _json.loads(resp.read())
            except Exception as e:
                web_config = {'error': str(e), 'note': 'config-snapshot endpoint may not be deployed yet'}

            return {
                'action': 'web_config',
                'service_context': 'web (remote)',
                'web_service_url': web_url,
                'health': health_data,
                'config': web_config,
            }

        elif action == 'llm_providers':
            providers = {}
            # OpenAI
            openai_key = os.environ.get('OPENAI_API_KEY', '')
            providers['openai'] = {
                'configured': bool(openai_key),
                'key_prefix': openai_key[:8] + '...' if openai_key else 'not set',
            }
            # Anthropic
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
            providers['anthropic'] = {
                'configured': bool(anthropic_key),
                'key_prefix': anthropic_key[:8] + '...' if anthropic_key else 'not set',
            }
            # Together AI
            together_key = os.environ.get('TOGETHER_AI_API_KEY', '') or os.environ.get('TOGETHER_API_KEY', '')
            providers['together_ai'] = {
                'configured': bool(together_key),
                'key_prefix': together_key[:8] + '...' if together_key else 'not set',
            }
            # DeepSeek
            deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')
            providers['deepseek'] = {
                'configured': bool(deepseek_key),
                'key_prefix': deepseek_key[:8] + '...' if deepseek_key else 'not set',
            }
            # Gemini
            gemini_key = os.environ.get('GEMINI_API_KEY', os.environ.get('GOOGLE_API_KEY', ''))
            providers['gemini'] = {
                'configured': bool(gemini_key),
                'key_prefix': gemini_key[:8] + '...' if gemini_key else 'not set',
            }
            # Ollama
            ollama_url = os.environ.get('OLLAMA_BASE_URL', getattr(django_settings, 'OLLAMA_BASE_URL', ''))
            providers['ollama'] = {
                'configured': bool(ollama_url),
                'base_url': ollama_url or 'not set',
            }
            return {
                'action': 'llm_providers',
                'default_provider': getattr(django_settings, 'LLM_DEFAULT_PROVIDER', 'unknown'),
                'providers': providers,
            }

        elif action == 'env_vars':
            # Show all env vars with secrets masked
            env_snapshot = {}
            for key in sorted(os.environ.keys()):
                # Skip overly noisy system vars
                if key.startswith(('__', 'npm_', 'LESS_', 'LS_')):
                    continue
                env_snapshot[key] = _mask(key, os.environ[key])
            return {
                'action': 'env_vars',
                'count': len(env_snapshot),
                'variables': env_snapshot,
            }

        elif action == 'feature_flags':
            flags = {}
            flag_attrs = [
                'LUNGS_ENFORCE_HARD_LIMIT',
                'CELERY_TASK_EVENT_RETENTION_DAYS',
                'LLM_CALL_LOG_RETENTION_DAYS',
                'BODY_THROTTLE_MAX_DELAY_SECONDS',
                'CONTENT_AUTO_PUBLISH',
                'SPIDER_ENABLED',
                'DREAM_ENABLED',
            ]
            for attr in flag_attrs:
                flags[attr] = getattr(django_settings, attr, 'not set')
            return {
                'action': 'feature_flags',
                'flags': flags,
            }

        return {'error': f'Unknown platform_config action: {action}'}

    # ── Session 1069: DB Health ───────────────────────────────────────────────

    def _handle_db_health(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1069: Database health — connection status, migration state,
        table row counts, and pgvector extension status.
        """
        from django.db import connection

        action = payload.get('action', 'overview')

        if action == 'overview':
            result = {'action': 'overview'}

            # Connection check
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    row = cursor.fetchone()
                    result['postgres_version'] = row[0] if row else 'unknown'
                    result['connected'] = True
            except Exception as e:
                result['connected'] = False
                result['connection_error'] = str(e)
                return result

            # Database name and size
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT current_database(), pg_size_pretty(pg_database_size(current_database()))")
                    row = cursor.fetchone()
                    if row:
                        result['database_name'] = row[0]
                        result['database_size'] = row[1]
            except Exception as e:
                result['db_size_error'] = str(e)

            # Migration summary
            try:
                from django.core.management import call_command
                from io import StringIO
                out = StringIO()
                call_command('showmigrations', '--plan', stdout=out)
                lines = out.getvalue().strip().split('\n')
                applied = sum(1 for l in lines if l.strip().startswith('[X]'))
                unapplied = sum(1 for l in lines if l.strip().startswith('[ ]'))
                result['migrations'] = {
                    'applied': applied,
                    'unapplied': unapplied,
                    'status': 'up_to_date' if unapplied == 0 else f'{unapplied}_pending',
                }
                if unapplied > 0:
                    result['migrations']['pending'] = [
                        l.strip()[4:] for l in lines if l.strip().startswith('[ ]')
                    ][:20]
            except Exception as e:
                result['migrations'] = {'error': str(e)}

            # pgvector check
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                    row = cursor.fetchone()
                    result['pgvector'] = {
                        'installed': bool(row),
                        'version': row[0] if row else None,
                    }
            except Exception as e:
                result['pgvector'] = {'error': str(e)}

            return result

        elif action == 'migrations':
            try:
                from django.core.management import call_command
                from io import StringIO
                out = StringIO()
                call_command('showmigrations', '--plan', stdout=out)
                lines = out.getvalue().strip().split('\n')
                unapplied = [l.strip()[4:] for l in lines if l.strip().startswith('[ ]')]
                applied_count = sum(1 for l in lines if l.strip().startswith('[X]'))
                return {
                    'action': 'migrations',
                    'applied_count': applied_count,
                    'unapplied_count': len(unapplied),
                    'unapplied': unapplied[:50],
                    'status': 'up_to_date' if not unapplied else 'pending',
                }
            except Exception as e:
                return {'action': 'migrations', 'error': str(e)}

        elif action == 'tables':
            try:
                key_tables = [
                    'core_chatconversation', 'core_agentexecution',
                    'core_toolcallrecord', 'core_initiative',
                    'core_spiderdata', 'core_deliverable',
                    'core_failuresignature', 'core_failuredetection',
                    'core_celerytaskevent', 'core_llmcalllog',
                    'core_selfblog', 'core_heartbeat',
                    'core_signalcluster', 'core_agentdream',
                    'core_humanattentionitem', 'core_mlprediction',
                    'core_imagehistory', 'core_videohistory',
                    'core_audiohistory',
                ]
                table_counts = {}
                with connection.cursor() as cursor:
                    for table in key_tables:
                        try:
                            cursor.execute(
                                "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                                [table]
                            )
                            row = cursor.fetchone()
                            table_counts[table] = row[0] if row else 0
                        except Exception:
                            table_counts[table] = 'error'
                return {
                    'action': 'tables',
                    'table_count': len(table_counts),
                    'row_counts': table_counts,
                    'note': 'Row counts are estimates from pg_class.reltuples (fast, updated by ANALYZE)',
                }
            except Exception as e:
                return {'action': 'tables', 'error': str(e)}

        elif action == 'verify_table':
            table_name = payload.get('table_name', '')
            if not table_name:
                return {'error': 'table_name is required'}
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'public' AND table_name = %s",
                        [table_name]
                    )
                    exists = cursor.fetchone() is not None
                    result = {'action': 'verify_table', 'table_name': table_name, 'exists': exists}
                    if exists:
                        cursor.execute(
                            "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                            [table_name]
                        )
                        row = cursor.fetchone()
                        result['row_count'] = row[0] if row else 0
                        cursor.execute(
                            "SELECT column_name, data_type FROM information_schema.columns "
                            "WHERE table_schema = 'public' AND table_name = %s "
                            "ORDER BY ordinal_position",
                            [table_name]
                        )
                        result['columns'] = [
                            {'name': r[0], 'type': r[1]} for r in cursor.fetchall()
                        ]
                    return result
            except Exception as e:
                return {'action': 'verify_table', 'error': str(e)}

        elif action == 'search_tables':
            prefix = payload.get('prefix', 'core_')
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT c.relname, c.reltuples::bigint "
                        "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                        "WHERE n.nspname = 'public' AND c.relkind = 'r' "
                        "AND c.relname LIKE %s ORDER BY c.relname",
                        [prefix + '%']
                    )
                    tables = [{'name': r[0], 'estimated_rows': r[1]} for r in cursor.fetchall()]
                    return {'action': 'search_tables', 'prefix': prefix, 'tables': tables, 'count': len(tables)}
            except Exception as e:
                return {'action': 'search_tables', 'error': str(e)}

        elif action == 'pgvector':
            result = {'action': 'pgvector'}
            try:
                with connection.cursor() as cursor:
                    # Extension status
                    cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                    row = cursor.fetchone()
                    result['installed'] = bool(row)
                    result['version'] = row[0] if row else None

                    if row:
                        # Count vector columns
                        cursor.execute("""
                            SELECT table_name, column_name
                            FROM information_schema.columns
                            WHERE udt_name = 'vector'
                            ORDER BY table_name
                        """)
                        vector_cols = cursor.fetchall()
                        result['vector_columns'] = [
                            {'table': r[0], 'column': r[1]} for r in vector_cols
                        ]
                        result['vector_column_count'] = len(vector_cols)

                        # Count rows with embeddings in key table
                        try:
                            cursor.execute("""
                                SELECT reltuples::bigint FROM pg_class
                                WHERE relname = 'core_spiderdata'
                            """)
                            row = cursor.fetchone()
                            result['spider_data_rows'] = row[0] if row else 0
                        except Exception:
                            pass

                        # Vector indexes
                        cursor.execute("""
                            SELECT indexname, tablename
                            FROM pg_indexes
                            WHERE indexdef LIKE '%%vector%%' OR indexdef LIKE '%%ivfflat%%' OR indexdef LIKE '%%hnsw%%'
                        """)
                        indexes = cursor.fetchall()
                        result['vector_indexes'] = [
                            {'index': r[0], 'table': r[1]} for r in indexes
                        ]
            except Exception as e:
                result['error'] = str(e)
            return result

        return {'error': f'Unknown db_health action: {action}'}

    def _handle_http_smoke_test(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Run HTTP smoke tests against cockpit API endpoints."""
        from core.tools.http_smoke_test import run_smoke_test
        from core.tools.ops_run_tracker import OpsRunTracker

        suite = payload.get('suite', 'default')
        with OpsRunTracker(f'Smoke: {suite}', 'smoke_test', 'pa_tool') as tracker:
            result = tracker.step(suite, lambda: run_smoke_test(payload))
            tracker.set_summary(result if isinstance(result, dict) else {})

        if isinstance(result, dict):
            result['ops_run_id'] = tracker.ops_run_id
        return result

    def _handle_learning(self, tool_name, payload, user_id, trace_id):
        """Manage PA tool-usage insights (learning loop)."""
        from core.models_tool_calls import PAToolInsight

        action = payload.get('action', 'stats')
        limit = min(payload.get('limit', 10), 50)
        filter_tool = payload.get('tool_name')

        _fields = (
            'id', 'tool_name', 'insight_type', 'prompt_snippet',
            'evidence_count', 'confidence', 'expires_at', 'created_at',
        )

        if action == 'list_candidates':
            qs = PAToolInsight.objects.filter(safety_class='candidate')
            if filter_tool:
                qs = qs.filter(tool_name=filter_tool)
            items = list(qs.order_by('-evidence_count', '-confidence')[:limit].values(*_fields))
            return {'candidates': items, 'count': len(items)}

        elif action == 'list_approved':
            qs = PAToolInsight.objects.filter(safety_class='approved')
            if filter_tool:
                qs = qs.filter(tool_name=filter_tool)
            items = list(qs.order_by('-confidence', '-evidence_count')[:limit].values(*_fields))
            return {'approved': items, 'count': len(items)}

        elif action == 'list_expired':
            from django.utils import timezone as _tz
            now = _tz.now()
            qs = PAToolInsight.objects.filter(expires_at__isnull=False, expires_at__lte=now)
            if filter_tool:
                qs = qs.filter(tool_name=filter_tool)
            items = list(qs.order_by('-expires_at')[:limit].values(*_fields, 'safety_class'))
            return {'expired': items, 'count': len(items)}

        elif action == 'approve':
            insight_id = payload.get('id')
            if not insight_id:
                return {'error': 'id is required for approve action'}
            updated = PAToolInsight.objects.filter(
                id=insight_id, safety_class='candidate'
            ).update(safety_class='approved')
            return {'approved': bool(updated), 'id': insight_id}

        elif action == 'reject':
            insight_id = payload.get('id')
            if not insight_id:
                return {'error': 'id is required for reject action'}
            updated = PAToolInsight.objects.filter(
                id=insight_id, safety_class='candidate'
            ).update(safety_class='rejected')
            return {'rejected': bool(updated), 'id': insight_id}

        elif action == 'stats':
            from django.db.models import Count
            stats = list(
                PAToolInsight.objects.values('safety_class', 'insight_type')
                .annotate(count=Count('id'))
                .order_by('safety_class', 'insight_type')
            )
            totals = {
                'candidate': 0, 'approved': 0, 'rejected': 0,
            }
            for s in stats:
                totals[s['safety_class']] = totals.get(s['safety_class'], 0) + s['count']
            return {'stats': stats, 'totals': totals}

        return {'error': f'Unknown action: {action}'}

    def _handle_rag_query(self, tool_name, payload, user_id, trace_id):
        """Search RAG knowledge base and get embedding stats."""
        action = payload.get('action', 'search')

        if action == 'search':
            query = payload.get('query', '').strip()
            if not query:
                return {'error': 'query is required for search action'}

            top_k = min(payload.get('top_k', 5), 20)
            threshold = payload.get('similarity_threshold', 0.3)
            doc_filter = payload.get('document_id')

            from content.embeddings import rag_system
            results = rag_system.semantic_search_sync(
                query=query,
                limit=top_k,
                similarity_threshold=threshold,
            )

            items = []
            for r in results:
                if doc_filter and r.document_id != doc_filter:
                    continue
                items.append({
                    'document_id': r.document_id,
                    'document_title': r.document_title,
                    'document_type': r.document_type,
                    'chunk_index': r.chunk_index,
                    'chunk_text': r.chunk_text[:1000],
                    'similarity_score': round(r.similarity_score, 4),
                    'source_type': getattr(r, 'source_type', 'unknown'),
                })

            return {
                'action': 'search',
                'query': query,
                'count': len(items),
                'results': items,
            }

        elif action == 'stats':
            from content.models import Document, DocumentEmbedding
            from django.db.models import Count

            total_embeddings = DocumentEmbedding.objects.count()
            total_docs = Document.objects.filter(status='processed').count()

            recent = list(
                Document.objects.filter(status='processed')
                .annotate(chunk_count=Count('embeddings'))
                .order_by('-created_at')[:5]
                .values('id', 'title', 'document_type', 'chunk_count', 'created_at')
            )
            for doc in recent:
                doc['id'] = str(doc['id'])
                doc['created_at'] = str(doc['created_at'])

            return {
                'action': 'stats',
                'total_documents': total_docs,
                'total_embeddings': total_embeddings,
                'recent_documents': recent,
            }

        elif action == 'list_documents':
            from content.models import Document
            from django.db.models import Count

            limit = min(payload.get('limit', 20), 50)
            doc_type = payload.get('document_type')

            qs = Document.objects.filter(status='processed')
            if doc_type:
                qs = qs.filter(document_type__icontains=doc_type)

            docs = list(
                qs.annotate(chunk_count=Count('embeddings'))
                .order_by('-created_at')[:limit]
                .values('id', 'title', 'document_type', 'chunk_count', 'created_at', 'source_url')
            )
            for doc in docs:
                doc['id'] = str(doc['id'])
                doc['created_at'] = str(doc['created_at'])

            return {
                'action': 'list_documents',
                'count': len(docs),
                'documents': docs,
            }

        elif action == 'ingest':
            url = payload.get('url', '').strip()
            if not url:
                raise ValueError("'url' is required for ingest action")

            # Dispatch URL ingestion as async task
            from core.tasks import process_url_async
            task = process_url_async.delay(url=url, generate_embeddings=True)

            return {
                'action': 'ingest',
                'url': url,
                'task_id': str(task.id),
                'mode': 'async',
                'message': f'URL "{url}" queued for RAG ingestion. Use job_status to check progress.',
                'success': True,
            }

        elif action == 'promote':
            document_id = payload.get('document_id', '').strip()
            if not document_id:
                return {'error': 'document_id is required for promote action'}

            from content.models import Document
            try:
                doc = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                return {'error': f'Document {document_id} not found'}

            old_status = doc.promotion_status
            doc.promotion_status = 'promoted'
            doc.save(update_fields=['promotion_status', 'updated_at'])
            return {
                'action': 'promote',
                'document_id': str(doc.id),
                'title': doc.title,
                'old_status': old_status,
                'new_status': 'promoted',
                'message': f'Document "{doc.title}" promoted — now retrievable via RAG.',
            }

        elif action == 'staged':
            from content.models import Document
            limit = min(payload.get('limit', 20), 50)
            docs = list(
                Document.objects.filter(promotion_status='staged')
                .order_by('-created_at')[:limit]
                .values('id', 'title', 'document_type', 'source', 'created_at')
            )
            for d in docs:
                d['id'] = str(d['id'])
                d['created_at'] = str(d['created_at'])
            return {
                'action': 'staged',
                'count': len(docs),
                'documents': docs,
            }

        return {'error': f'Unknown action: {action}. Valid: search, stats, list_documents, ingest, promote, staged'}

    # ── Session G1: Competitor Comparison ────────────────────────────────────

    def _handle_competitor_comparison(self, tool_name, payload, user_id, trace_id):
        """Generate, check status, list, or view competitor comparisons."""
        action = payload.get('action', 'list')

        if action == 'generate':
            competitor_name = payload.get('competitor_name', '').strip()
            if not competitor_name:
                return {'error': 'competitor_name is required for generate action'}

            from core.models_competitor_comparison import CompetitorComparison
            from core.tasks import generate_competitor_comparison_task

            source_document_id = payload.get('source_document_id')
            focus_areas = payload.get('focus_areas')
            auto_research = payload.get('auto_research', True)

            comparison = CompetitorComparison.objects.create(
                competitor_name=competitor_name,
                source_document_id=source_document_id,
                generated_by='PA',
                user_id=user_id,
            )

            task = generate_competitor_comparison_task.delay(
                comparison_id=str(comparison.id),
                source_document_id=str(source_document_id) if source_document_id else None,
                competitor_name=competitor_name,
                focus_areas=focus_areas,
                auto_research=auto_research,
            )

            return {
                'action': 'generate',
                'comparison_id': str(comparison.id),
                'task_id': str(task.id),
                'message': f'Competitor comparison for "{competitor_name}" started',
            }

        elif action == 'status':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for status action'}

            from core.models_competitor_comparison import CompetitorComparison
            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            result = {
                'action': 'status',
                'comparison_id': str(c.id),
                'competitor_name': c.competitor_name,
                'status': c.status,
                'quality_score': c.quality_score,
            }
            if c.status == 'complete':
                result['summary'] = c.summary[:500]
                result['completed_at'] = c.completed_at.isoformat() if c.completed_at else None
                result['executive_summary'] = c.executive_summary_json
            elif c.status == 'needs_sources':
                result['error_message'] = c.error_message[:500]
                result['recommended_queries'] = (c.metadata or {}).get('recommended_queries', [])
            elif c.status == 'failed':
                result['error_message'] = c.error_message[:500]
            return result

        elif action == 'list':
            from core.models_competitor_comparison import CompetitorComparison

            limit = min(int(payload.get('limit', 10)), 50)
            qs = CompetitorComparison.objects.order_by('-created_at')[:limit]

            return {
                'action': 'list',
                'count': len(qs),
                'comparisons': [
                    {
                        'id': str(c.id),
                        'competitor_name': c.competitor_name,
                        'status': c.status,
                        'quality_score': c.quality_score,
                        'evidence_count': len(c.evidence_json) if isinstance(c.evidence_json, list) else 0,
                        'summary': (c.summary[:200] if c.summary else ''),
                        'created_at': c.created_at.isoformat(),
                    }
                    for c in qs
                ],
            }

        elif action == 'detail':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for detail action'}

            from core.models_competitor_comparison import CompetitorComparison
            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            return {
                'action': 'detail',
                'comparison': {
                    'id': str(c.id),
                    'competitor_name': c.competitor_name,
                    'status': c.status,
                    'quality_score': c.quality_score,
                    'executive_summary': c.executive_summary_json,
                    'quality_rubric': c.quality_rubric_json,
                    'sources': c.sources_json,
                    'review': c.review_json,
                    'comparison_table': c.comparison_table_json,
                    'gap_backlog': c.gap_backlog_json,
                    'tools_stack': c.tools_stack_json,
                    'evidence_count': len(c.evidence_json) if isinstance(c.evidence_json, list) else 0,
                    'summary': c.summary,
                    'created_at': c.created_at.isoformat(),
                    'completed_at': c.completed_at.isoformat() if c.completed_at else None,
                    'metadata': c.metadata,
                },
            }

        elif action == 'delete':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for delete action'}

            from core.models_competitor_comparison import CompetitorComparison
            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            name = c.competitor_name
            c.delete()
            return {
                'action': 'delete',
                'deleted': True,
                'competitor_name': name,
                'message': f'Comparison for "{name}" deleted',
            }

        elif action == 'regenerate':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for regenerate action'}

            from core.models_competitor_comparison import CompetitorComparison
            from core.tasks import generate_competitor_comparison_task

            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            # Reset and re-dispatch
            c.status = 'pending'
            c.error_message = ''
            c.save(update_fields=['status', 'error_message', 'updated_at'])

            task = generate_competitor_comparison_task.delay(
                comparison_id=str(c.id),
                source_document_id=str(c.source_document_id) if c.source_document_id else None,
                competitor_name=c.competitor_name,
            )

            return {
                'action': 'regenerate',
                'comparison_id': str(c.id),
                'task_id': str(task.id),
                'message': f'Regenerating comparison for "{c.competitor_name}"',
            }

        elif action == 'create_initiative_from_gap':
            comparison_id = payload.get('comparison_id')
            gap_index = payload.get('gap_index', 0)
            if not comparison_id:
                return {'error': 'comparison_id is required for create_initiative_from_gap action'}

            from core.models_competitor_comparison import CompetitorComparison
            from core.models_document_registry import Initiative

            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            if c.status != 'complete':
                return {'error': f'Comparison must be complete (current: {c.status})'}

            gaps = c.gap_backlog_json if isinstance(c.gap_backlog_json, list) else c.gap_backlog_json.get('gaps', [])
            if not gaps:
                return {'error': 'No gaps found in this comparison'}
            if gap_index >= len(gaps):
                return {'error': f'gap_index {gap_index} out of range (0-{len(gaps)-1})'}

            gap = gaps[gap_index]
            gap_title = gap.get('gap', gap.get('title', f'Gap #{gap_index + 1}'))
            effort = gap.get('effort', 'M')
            impact = gap.get('impact', 'medium')
            acceptance = gap.get('acceptance_test', gap.get('acceptance_criteria', ''))
            evidence_refs = gap.get('evidence_refs', [])

            # Map effort to purpose
            purpose = 'expansion' if impact == 'high' else 'learning'
            urgency_score = {'high': 0.8, 'medium': 0.5, 'low': 0.3}.get(impact, 0.5)

            name = f"[Competitive] {gap_title}"
            if Initiative.objects.filter(name=name).exists():
                return {
                    'error': f'Initiative "{name}" already exists',
                    'action': 'create_initiative_from_gap',
                }

            description_parts = [
                f"**Source:** Competitor comparison vs {c.competitor_name}",
                f"**Gap:** {gap_title}",
                f"**Effort:** {effort} | **Impact:** {impact}",
            ]
            if acceptance:
                description_parts.append(f"**Acceptance Criteria:** {acceptance}")
            if evidence_refs:
                description_parts.append(f"**Evidence:** {', '.join(evidence_refs)}")

            initiative = Initiative.objects.create(
                name=name,
                description='\n'.join(description_parts),
                status='ACTIVE',
                purpose=purpose,
                program='growth_intelligence',
                urgency=urgency_score,
                impact_score=urgency_score,
                confidence=c.quality_score,
                created_by='competitor_comparison',
                parent_topic=c.competitor_name,
            )

            return {
                'action': 'create_initiative_from_gap',
                'initiative_id': str(initiative.id),
                'initiative_name': initiative.name,
                'gap_title': gap_title,
                'message': f'Initiative created from gap: "{gap_title}"',
            }

        elif action == 'export_markdown':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for export_markdown action'}

            from core.models_competitor_comparison import CompetitorComparison

            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            if c.status != 'complete':
                return {'error': f'Comparison must be complete (current: {c.status})'}

            lines = [f"# Competitor Analysis: {c.competitor_name}", ""]

            # Executive summary
            exec_sum = c.executive_summary_json or {}
            if exec_sum.get('verdict'):
                lines += [f"## Executive Summary", "", exec_sum['verdict'], ""]
                if exec_sum.get('top_advantages'):
                    lines += ["### Top Advantages"]
                    for adv in exec_sum['top_advantages']:
                        lines.append(f"- {adv}")
                    lines.append("")
                if exec_sum.get('top_gaps'):
                    lines += ["### Top Gaps"]
                    for gap in exec_sum['top_gaps']:
                        lines.append(f"- {gap}")
                    lines.append("")

            # Comparison table
            table_data = c.comparison_table_json
            rows = table_data if isinstance(table_data, list) else table_data.get('rows', [])
            if rows:
                lines += ["## Side-by-Side Comparison", ""]
                lines.append("| Feature | Competitor | Donkey Betz | Evidence |")
                lines.append("|---------|-----------|-------------|----------|")
                for row in rows:
                    feature = row.get('feature', row.get('area', ''))
                    comp = row.get('competitor', row.get('them', ''))
                    us = row.get('donkey_betz', row.get('us', ''))
                    refs = ', '.join(row.get('evidence_refs', []))
                    lines.append(f"| {feature} | {comp} | {us} | {refs} |")
                lines.append("")

            # Gap backlog
            gaps = c.gap_backlog_json if isinstance(c.gap_backlog_json, list) else c.gap_backlog_json.get('gaps', [])
            if gaps:
                lines += ["## Gap Backlog", ""]
                for i, gap in enumerate(gaps):
                    title = gap.get('gap', gap.get('title', f'Gap #{i+1}'))
                    effort = gap.get('effort', '?')
                    impact = gap.get('impact', '?')
                    acceptance = gap.get('acceptance_test', gap.get('acceptance_criteria', ''))
                    refs = ', '.join(gap.get('evidence_refs', []))
                    lines.append(f"### {i+1}. {title}")
                    lines.append(f"- **Effort:** {effort} | **Impact:** {impact}")
                    if acceptance:
                        lines.append(f"- **Acceptance:** {acceptance}")
                    if refs:
                        lines.append(f"- **Evidence:** {refs}")
                    lines.append("")

            # Tools/Stack
            tools = c.tools_stack_json
            tools_list = tools if isinstance(tools, list) else tools.get('tools', [])
            if tools_list:
                lines += ["## Tools & Stack", ""]
                for t in tools_list:
                    if isinstance(t, str):
                        lines.append(f"- {t}")
                    else:
                        lines.append(f"- **{t.get('name', t.get('tool', ''))}**: {t.get('category', t.get('purpose', ''))}")
                lines.append("")

            # Sources
            sources = c.sources_json or []
            if sources:
                lines += ["## Sources", ""]
                for s in sources:
                    if isinstance(s, dict):
                        lines.append(f"- {s.get('title', 'Unknown')} ({s.get('source_type', '')})")
                    else:
                        lines.append(f"- {s}")
                lines.append("")

            # Quality rubric
            rubric = c.quality_rubric_json or {}
            if rubric:
                lines += ["## Quality Rubric", ""]
                lines.append(f"- **Overall Score:** {c.quality_score:.2f}")
                for key, val in rubric.items():
                    if key != 'composite_score':
                        lines.append(f"- **{key.replace('_', ' ').title()}:** {val}")
                lines.append("")

            lines.append(f"---\n*Generated {c.created_at.strftime('%Y-%m-%d %H:%M')} UTC*")

            markdown_content = '\n'.join(lines)

            # Save as Deliverable
            save_as_deliverable = payload.get('save', True)
            deliverable_id = None
            if save_as_deliverable:
                from core.models_deliverables import Deliverable
                from django.utils.text import slugify
                slug_base = slugify(f"competitor-{c.competitor_name}")[:250]
                slug = slug_base
                counter = 1
                while Deliverable.objects.filter(slug=slug).exists():
                    slug = f"{slug_base}-{counter}"
                    counter += 1

                d = Deliverable.objects.create(
                    title=f"Competitor Analysis: {c.competitor_name}",
                    slug=slug,
                    deliverable_type='document',
                    category='Competitive Intelligence',
                    tags=['competitor', 'analysis', c.competitor_name.lower()],
                    agent_name='competitor_comparison_tool',
                    agent_task=f'Export comparison {c.id}',
                    content=markdown_content,
                    content_format='markdown',
                    preview_content=markdown_content[:500],
                    quality_score=c.quality_score,
                    confidence_score=c.quality_score,
                    user_id=user_id,
                )
                deliverable_id = str(d.id)

            return {
                'action': 'export_markdown',
                'comparison_id': str(c.id),
                'competitor_name': c.competitor_name,
                'markdown': markdown_content,
                'deliverable_id': deliverable_id,
                'message': f'Exported comparison for "{c.competitor_name}" as Markdown' + (' (saved as Deliverable)' if deliverable_id else ''),
            }

        return {'error': f'Unknown action: {action}'}

    # ── Workflow Run Tool ────────────────────────────────────────────────
    def _handle_workflow_run(self, tool_name, payload, user_id, trace_id):
        """Start, poll, list, detail, or cancel multi-step workflow runs."""
        action = payload.get('action', 'list')

        if action == 'start':
            workflow_key = payload.get('workflow_key', 'source_pack_comparison')
            competitor_name = payload.get('competitor_name', '').strip()
            if not competitor_name:
                return {'error': 'competitor_name is required to start a workflow'}

            from core.models_workflow_run import WorkflowRun
            from core.tasks import run_source_pack_workflow

            run = WorkflowRun.objects.create(
                workflow_key=workflow_key,
                user_id=user_id,
                input_json={
                    'competitor_name': competitor_name,
                    'queries': payload.get('queries', []),
                    'target_count': payload.get('target_count', 8),
                    'comparison_id': payload.get('comparison_id'),
                    'focus_areas': payload.get('focus_areas'),
                },
            )

            logger.info(f"[WORKFLOW] Dispatching run_source_pack_workflow for run={run.id}")
            task = run_source_pack_workflow.apply_async(
                kwargs={'run_id': str(run.id)},
                queue='content',
            )
            logger.info(f"[WORKFLOW] Dispatched task_id={task.id} to queue=content for run={run.id}")
            run.celery_task_id = str(task.id)
            run.save(update_fields=['celery_task_id', 'updated_at'])

            return {
                'action': 'start',
                'run_id': str(run.id),
                'task_id': str(task.id),
                'workflow_key': workflow_key,
                'message': f'Source pack workflow started for "{competitor_name}"',
            }

        elif action == 'status':
            run_id = payload.get('run_id')
            if not run_id:
                return {'error': 'run_id is required for status action'}

            from core.models_workflow_run import WorkflowRun
            try:
                run = WorkflowRun.objects.get(id=run_id)
            except WorkflowRun.DoesNotExist:
                return {'error': f'Workflow run {run_id} not found'}

            result = {
                'action': 'status',
                'run_id': str(run.id),
                'workflow_key': run.workflow_key,
                'status': run.status,
                'stage': run.stage,
                'percent': run.percent,
                'stage_detail': run.stage_detail,
            }
            if run.status == 'complete':
                result['output'] = run.output_json
                result['completed_at'] = run.completed_at.isoformat() if run.completed_at else None
            elif run.status == 'failed':
                result['error_message'] = run.error_message[:500]
                result['output'] = run.output_json
            # Include recent events
            events = run.events_json if isinstance(run.events_json, list) else []
            result['recent_events'] = events[-5:]
            return result

        elif action == 'list':
            from core.models_workflow_run import WorkflowRun

            limit = min(int(payload.get('limit', 10)), 50)
            qs = WorkflowRun.objects.all()
            if user_id:
                qs = qs.filter(user_id=user_id)
            qs = qs.order_by('-created_at')[:limit]

            return {
                'action': 'list',
                'count': len(qs),
                'runs': [
                    {
                        'id': str(r.id),
                        'workflow_key': r.workflow_key,
                        'status': r.status,
                        'stage': r.stage,
                        'percent': r.percent,
                        'created_at': r.created_at.isoformat(),
                        'competitor_name': (r.input_json or {}).get('competitor_name', ''),
                    }
                    for r in qs
                ],
            }

        elif action == 'detail':
            run_id = payload.get('run_id')
            if not run_id:
                return {'error': 'run_id is required for detail action'}

            from core.models_workflow_run import WorkflowRun
            try:
                run = WorkflowRun.objects.get(id=run_id)
            except WorkflowRun.DoesNotExist:
                return {'error': f'Workflow run {run_id} not found'}

            return {
                'action': 'detail',
                'run': {
                    'id': str(run.id),
                    'workflow_key': run.workflow_key,
                    'status': run.status,
                    'stage': run.stage,
                    'percent': run.percent,
                    'stage_detail': run.stage_detail,
                    'input': run.input_json,
                    'output': run.output_json,
                    'events': run.events_json,
                    'error_message': run.error_message,
                    'celery_task_id': run.celery_task_id,
                    'created_at': run.created_at.isoformat(),
                    'started_at': run.started_at.isoformat() if run.started_at else None,
                    'completed_at': run.completed_at.isoformat() if run.completed_at else None,
                    'metadata': run.metadata,
                },
            }

        elif action == 'cancel':
            run_id = payload.get('run_id')
            if not run_id:
                return {'error': 'run_id is required for cancel action'}

            from core.models_workflow_run import WorkflowRun
            try:
                run = WorkflowRun.objects.get(id=run_id)
            except WorkflowRun.DoesNotExist:
                return {'error': f'Workflow run {run_id} not found'}

            if run.status in ('complete', 'failed', 'cancelled'):
                return {'error': f'Cannot cancel a workflow in {run.status} state'}

            # Revoke celery task
            if run.celery_task_id:
                from core.celery import app as celery_app
                celery_app.control.revoke(run.celery_task_id, terminate=True)

            run.mark_cancelled()
            run.save()

            return {
                'action': 'cancel',
                'run_id': str(run.id),
                'message': 'Workflow cancelled',
            }

        return {'error': f'Unknown action: {action}'}

    # ── Conversation Memory ──────────────────────────────────────────────────

    def _handle_conversation(self, tool_name, payload, user_id, trace_id):
        """Handle conversation memory tool — cross-thread PA recall."""
        from core.models import ChatConversation, ConversationMemory
        from django.db.models import Q
        from datetime import timedelta
        from django.utils import timezone

        action = payload.get('action', 'search')
        limit = min(payload.get('limit', 10), 50)

        if action == 'get':
            cid = payload.get('conversation_id')
            if not cid:
                return {'error': 'conversation_id required for get action'}

            # Session 1086: Support pagination via offset so the PA can
            # reach later turns in long conversations.
            offset = max(payload.get('offset', 0), 0)
            page_size = min(limit, 30)  # max 30 turns per page
            # Content cap per turn — 1000 chars gives more context than 500
            content_cap = 1000

            total = ChatConversation.objects.filter(conversation_id=cid).count()
            if total == 0:
                return {'action': 'get', 'conversation_id': cid, 'turns': [], 'message': 'No conversation found'}

            turns = list(
                ChatConversation.objects.filter(conversation_id=cid)
                .order_by('created_at')
                .values('user_message', 'assistant_response', 'created_at', 'source', 'session_title')
                [offset:offset + page_size]
            )

            return {
                'action': 'get',
                'conversation_id': cid,
                'session_title': turns[0].get('session_title', '') if turns else '',
                'turn_count': total,
                'offset': offset,
                'page_size': page_size,
                'has_more': (offset + page_size) < total,
                'turns': [
                    {
                        'role_user': t['user_message'][:content_cap],
                        'role_assistant': t['assistant_response'][:content_cap],
                        'timestamp': t['created_at'].isoformat() if t['created_at'] else None,
                    }
                    for t in turns
                ],
            }

        elif action == 'search':
            query = payload.get('query', '')
            days_back = payload.get('days_back')
            if not query:
                return {'error': 'query required for search action'}

            results = []

            # Primary: pgvector semantic search on ConversationMemory
            try:
                from pgvector.django import CosineDistance
                from core.services.embedding_service import EmbeddingService
                emb_svc = EmbeddingService()
                emb_result = emb_svc.create_embedding(query, agent_name='conversation_tool')
                vector = emb_result.embedding

                cm_qs = ConversationMemory.objects.exclude(embedding__isnull=True)
                if user_id:
                    cm_qs = cm_qs.filter(user_id=user_id)
                if days_back:
                    cm_qs = cm_qs.filter(created_at__gte=timezone.now() - timedelta(days=days_back))

                semantic_hits = list(
                    cm_qs.annotate(distance=CosineDistance('embedding', vector))
                    .order_by('distance')[:limit]
                    .values('id', 'message', 'response', 'created_at', 'distance')
                )
                for hit in semantic_hits:
                    results.append({
                        'source': 'semantic',
                        'score': round(1.0 - (hit['distance'] or 1.0), 3),
                        'user_message': hit['message'][:300],
                        'assistant_response': hit['response'][:300],
                        'timestamp': hit['created_at'].isoformat() if hit['created_at'] else None,
                    })
            except Exception as e:
                logger.warning(f"[CONVERSATION] Semantic search failed: {e}")

            # Fallback/supplement: keyword search on ChatConversation
            kw_qs = ChatConversation.objects.filter(
                Q(user_message__icontains=query) | Q(assistant_response__icontains=query)
            )
            if user_id:
                kw_qs = kw_qs.filter(user_id=user_id)
            if days_back:
                kw_qs = kw_qs.filter(created_at__gte=timezone.now() - timedelta(days=days_back))

            kw_hits = list(
                kw_qs.order_by('-created_at')[:limit]
                .values('conversation_id', 'user_message', 'assistant_response', 'created_at', 'session_title')
            )

            # Dedupe: skip keyword hits already covered by semantic
            seen_snippets = {r['user_message'][:100] for r in results}
            for hit in kw_hits:
                snippet = hit['user_message'][:100]
                if snippet not in seen_snippets:
                    seen_snippets.add(snippet)
                    results.append({
                        'source': 'keyword',
                        'score': 0.5,
                        'conversation_id': hit['conversation_id'],
                        'session_title': hit.get('session_title', ''),
                        'user_message': hit['user_message'][:300],
                        'assistant_response': hit['assistant_response'][:300],
                        'timestamp': hit['created_at'].isoformat() if hit['created_at'] else None,
                    })

            # Sort by score desc
            results.sort(key=lambda r: r['score'], reverse=True)
            results = results[:limit]

            return {
                'action': 'search',
                'query': query,
                'count': len(results),
                'results': results,
            }

        elif action == 'summary':
            cid = payload.get('conversation_id')
            if not cid:
                return {'error': 'conversation_id required for summary action'}

            from core.tasks import summarize_conversation_task
            task = summarize_conversation_task.delay(
                conversation_id=cid,
                user_id=user_id,
            )
            return {
                'action': 'summary',
                'mode': 'async',
                'task_id': str(task.id),
                'message': f'Summarizing conversation {cid}...',
            }

        elif action == 'pin_memory':
            pin_title = payload.get('pin_title', '').strip()
            pin_content = payload.get('pin_content', '').strip()
            if not pin_title or not pin_content:
                return {'error': 'pin_title and pin_content required for pin_memory action'}

            pin_tags = payload.get('pin_tags') or ['pa-memory']

            from core.models_deliverables import Deliverable
            d = Deliverable.objects.create(
                title=pin_title,
                content=pin_content,
                category='Memory',
                deliverable_type='document',
                is_pinned=True,
                is_saved=True,
                agent_name='PersonalAssistant',
                content_format='markdown',
                tags=pin_tags,
                metadata={'source': 'conversation_tool', 'pinned_by': 'pa'},
                user_id=user_id,
            )

            # Also embed for future semantic search
            try:
                from core.services.embedding_service import EmbeddingService
                emb_svc = EmbeddingService()
                emb_result = emb_svc.create_embedding(pin_content, agent_name='conversation_tool')
                if user_id:
                    ConversationMemory.objects.create(
                        user_id=user_id,
                        message=f"[PINNED] {pin_title}",
                        response=pin_content,
                        intent='pin_memory',
                        embedding=emb_result.embedding,
                    )
            except Exception as e:
                logger.warning(f"[CONVERSATION] Embedding for pinned memory failed: {e}")

            return {
                'action': 'pin_memory',
                'deliverable_id': str(d.id),
                'title': pin_title,
                'message': f'Pinned memory: "{pin_title}"',
            }

        elif action == 'recent':
            # List most recent PA conversations with IDs + timestamps.
            # Enables cross-channel discovery (find UI conversation from CLI).
            qs = ChatConversation.objects.filter(
                conversation_id__startswith='pa-',
            ).order_by('-created_at')

            if user_id:
                qs = qs.filter(user_id=user_id)

            # Distinct conversation IDs with latest timestamp
            from django.db.models import Max
            convos = list(
                qs.values('conversation_id', 'source')
                .annotate(last_activity=Max('created_at'))
                .order_by('-last_activity')[:limit]
            )

            return {
                'action': 'recent',
                'count': len(convos),
                'conversations': [
                    {
                        'conversation_id': c['conversation_id'],
                        'source': c['source'] or 'unknown',
                        'last_activity': c['last_activity'].isoformat() if c['last_activity'] else None,
                    }
                    for c in convos
                ],
            }

        return {'error': f'Unknown action: {action}'}

    def _handle_remember(self, tool_name, payload, user_id, trace_id):
        """Handle remember_tool: save/list/delete/search persistent memories."""
        import os
        import re
        import hashlib
        from django.contrib.auth import get_user_model
        from core.models import UserMemoryContext, EnhancedUserProfile
        from core.services.memory_context_service import get_memory_context_service

        User = get_user_model()
        action = payload.get('action', 'save')

        if not user_id:
            return {'error': 'User context required for memory operations'}
        user = User.objects.get(id=user_id)

        if action == 'save':
            content = (payload.get('content') or '').strip()
            if not content:
                return {'error': 'content is required for save action'}

            # Secret redaction
            content = _redact_secrets(content)

            memory_type = payload.get('memory_type', 'preference')
            importance = min(max(payload.get('importance', 7), 1), 10)
            tags = payload.get('tags') or []

            # Env-var cap check
            max_items = int(os.environ.get('MEMORY_MAX_ITEMS', '200'))
            current_count = UserMemoryContext.objects.filter(user=user).count()
            if current_count >= max_items:
                return {
                    'error': f'Memory limit reached ({max_items} items). Delete old memories first.',
                    'current_count': current_count,
                    'max_items': max_items,
                }

            # Deduplication: hash of normalized content + memory_type
            content_hash = hashlib.sha256(
                f"{content.lower().strip()}:{memory_type}".encode()
            ).hexdigest()[:16]

            existing = UserMemoryContext.objects.filter(
                user=user,
                memory_type=memory_type,
                context_metadata__content_hash=content_hash,
            ).first()
            if existing:
                # Update importance if higher, bump timestamp
                if importance > existing.importance:
                    existing.importance = importance
                    existing.save(update_fields=['importance'])
                return {
                    'action': 'save',
                    'status': 'duplicate_updated',
                    'memory_id': existing.id,
                    'message': f'Memory already exists (updated importance to {max(importance, existing.importance)})',
                }

            # Save
            profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)
            memory = UserMemoryContext.objects.create(
                user=user,
                profile=profile,
                memory_type=memory_type,
                content=content[:500],
                importance=importance,
                source='remember_tool',
                tags=tags,
                context_metadata={
                    'content_hash': content_hash,
                    'trace_id': trace_id,
                },
            )

            # Clear memory context cache
            svc = get_memory_context_service()
            svc.clear_cache(user)

            # OpsRun event
            from core.tools.ops_run_tracker import get_active_tracker
            tracker = get_active_tracker()
            if tracker:
                tracker.info('memory_saved', {
                    'memory_id': memory.id,
                    'memory_type': memory_type,
                    'importance': importance,
                })

            return {
                'action': 'save',
                'memory_id': memory.id,
                'memory_type': memory_type,
                'importance': importance,
                'message': f'Remembered: "{content[:80]}"',
            }

        elif action == 'list':
            memories = UserMemoryContext.objects.filter(user=user).order_by('-importance', '-created_at')[:20]
            return {
                'action': 'list',
                'count': UserMemoryContext.objects.filter(user=user).count(),
                'memories': [
                    {
                        'id': m.id,
                        'type': m.memory_type,
                        'content': m.content[:200],
                        'importance': m.importance,
                        'tags': m.tags,
                        'created_at': m.created_at.isoformat(),
                    }
                    for m in memories
                ],
            }

        elif action == 'delete':
            memory_id = payload.get('memory_id')
            if not memory_id:
                return {'error': 'memory_id required for delete action'}
            deleted, _ = UserMemoryContext.objects.filter(user=user, id=memory_id).delete()
            if deleted:
                svc = get_memory_context_service()
                svc.clear_cache(user)
            return {
                'action': 'delete',
                'deleted': deleted > 0,
                'message': 'Memory deleted' if deleted else 'Memory not found',
            }

        elif action == 'search':
            query = (payload.get('query') or '').strip()
            if not query:
                return {'error': 'query required for search action'}
            results = UserMemoryContext.objects.filter(
                user=user,
                content__icontains=query,
            ).order_by('-importance')[:10]
            return {
                'action': 'search',
                'query': query,
                'count': len(results),
                'memories': [
                    {
                        'id': m.id,
                        'type': m.memory_type,
                        'content': m.content[:200],
                        'importance': m.importance,
                    }
                    for m in results
                ],
            }

        return {'error': f'Unknown action: {action}'}


    # ── Session 1078: Work Tool (Gateway) ──────────────────────────────────────
    def _handle_work(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1078: Work gateway — thin dispatcher over initiative_tool.
        Translates work_tool actions to initiative_tool actions and delegates.
        """
        action = payload.get('action', 'initiative_list')

        # Action name mapping: work_tool action → initiative_tool action + payload overrides
        ACTION_MAP = {
            'initiative_list': ('list', {}),
            'initiative_detail': ('details', {}),
            'initiative_create': ('create', {}),
            'initiative_promote': ('promote', {}),
            'action_item_list': ('action_items', {}),
            'action_item_start': ('start_action_item', {}),
            'action_item_complete': ('complete_action_item', {}),
            'action_item_cleanup': ('cleanup_action_items', {}),
        }

        # ── Session 1100: Direct data actions (not delegated to initiative_tool) ──
        if action == 'agent_conversations':
            try:
                from core.models_unified_system import AgentConversation
                limit = min(int(payload.get('limit', 10)), 30)
                convs = AgentConversation.objects.select_related('initiator').prefetch_related('participants').order_by('-started_at')[:limit]
                return {
                    'gateway': 'work_tool', 'action': action,
                    'count': len(convs),
                    'conversations': [{
                        'id': str(c.id),
                        'topic': c.topic,
                        'initiator': c.initiator.name if c.initiator else 'unknown',
                        'participants': [p.name for p in c.participants.all()[:5]],
                        'status': c.status,
                        'message_count': c.message_count,
                        'conclusion': (c.conclusion or '')[:200],
                        'started_at': c.started_at.isoformat() if c.started_at else None,
                    } for c in convs],
                }
            except Exception as e:
                return {'gateway': 'work_tool', 'action': action, 'error': str(e)}

        if action == 'workflows':
            try:
                from core.models_unified_system import AgentExecution
                limit = min(int(payload.get('limit', 10)), 30)
                execs = AgentExecution.objects.filter(
                    agent__name__in=['WorkflowAgent', 'WorkflowOrchestrationAgent',
                                     'CampaignOrchestratorAgent', 'AISeriesWorkflowAgent']
                ).select_related('agent').order_by('-created_at')[:limit]
                return {
                    'gateway': 'work_tool', 'action': action,
                    'count': len(execs),
                    'workflows': [{
                        'id': str(e.id),
                        'agent': e.agent.name if e.agent else 'unknown',
                        'status': e.status,
                        'task': (e.input_data or {}).get('task', '')[:150],
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    } for e in execs],
                }
            except Exception as e:
                return {'gateway': 'work_tool', 'action': action, 'error': str(e)}

        mapping = ACTION_MAP.get(action)
        if not mapping:
            extra_actions = ['agent_conversations', 'workflows']
            all_acts = sorted(list(ACTION_MAP) + extra_actions)
            return {'error': f'Unknown work_tool action: {action}. Valid: {", ".join(all_acts)}'}

        initiative_action, overrides = mapping

        # Build the initiative_tool payload
        initiative_payload = dict(payload)
        initiative_payload['action'] = initiative_action
        initiative_payload.update(overrides)

        # Translate work_tool param names → initiative_tool param names
        # action_item_list: status → item_status (initiative_tool uses item_status for action items)
        if action == 'action_item_list':
            if 'status' in initiative_payload and 'item_status' not in initiative_payload:
                initiative_payload['item_status'] = initiative_payload.pop('status')

        # action_item_start / action_item_complete: id → item_id
        if action in ('action_item_start', 'action_item_complete'):
            if 'id' in initiative_payload and 'item_id' not in initiative_payload:
                initiative_payload['item_id'] = initiative_payload.get('id')

        # Delegate to existing initiative handler
        result = self._handle_initiative('initiative_tool', initiative_payload, user_id, trace_id)

        # Normalize the response action name to the work_tool action
        if isinstance(result, dict):
            result['gateway'] = 'work_tool'
            result['action'] = action

        return result

    # ── Session 1079: Intelligence Tool (gateway) ────────────────────────────────
    def _handle_intelligence(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1079: Intelligence gateway — unified desk for stocks, sports,
        legislation, search (KB/spider/web), and ML analytics.
        Wraps stock_intelligence_tool, sports_betting_tool, legislation_tool,
        rag_query_tool, spider_data_tool, web_search.
        """
        action = payload.get('action', 'overview')

        def _tag(result):
            if isinstance(result, dict):
                result['gateway'] = 'intelligence_tool'
                result['action'] = action
            return result

        # ── Composite: overview (merge 3 desk overviews) ──
        if action == 'overview':
            combined = {'desks': {}}
            for desk, tool, handler in [
                ('stocks', 'stock_intelligence_tool', self._handle_stock_intelligence),
                ('sports', 'sports_betting_tool', self._handle_sports_betting),
                ('legislation', 'legislation_tool', self._handle_legislation),
            ]:
                try:
                    desk_result = handler(tool, {'action': 'overview'}, user_id, trace_id)
                    combined['desks'][desk] = desk_result
                except Exception as e:
                    combined['desks'][desk] = {'error': str(e)}
            return _tag(combined)

        # ── Composite: briefs (desk param selects source) ──
        if action == 'briefs':
            desk = payload.get('desk', 'all')
            limit = payload.get('limit', 5)
            briefs_result = {'briefs': {}}
            desk_map = {
                'stocks': ('stock_intelligence_tool', self._handle_stock_intelligence, 'briefs'),
                'sports': ('sports_betting_tool', self._handle_sports_betting, 'brief'),
                'legislation': ('legislation_tool', self._handle_legislation, 'trending'),
            }
            desks_to_query = desk_map.keys() if desk == 'all' else [desk] if desk in desk_map else []
            for d in desks_to_query:
                tool_name_inner, handler, inner_action = desk_map[d]
                try:
                    r = handler(tool_name_inner, {'action': inner_action, 'limit': limit}, user_id, trace_id)
                    briefs_result['briefs'][d] = r
                except Exception as e:
                    briefs_result['briefs'][d] = {'error': str(e)}
            if not desks_to_query:
                briefs_result['error'] = f'Unknown desk: {desk}. Valid: stocks, sports, legislation, all'
            return _tag(briefs_result)

        # ── Composite: search (source param selects backend) ──
        if action == 'search':
            source = payload.get('source', 'kb')
            query = payload.get('query', '')
            limit = payload.get('limit', 10)
            if source == 'kb':
                result = self._handle_rag_query('rag_query_tool', {'action': 'search', 'query': query, 'limit': limit}, user_id, trace_id)
            elif source == 'spider':
                result = self._handle_spider_data('spider_data_tool', {'action': 'search', 'query': query, 'limit': limit}, user_id, trace_id)
            elif source == 'web':
                result = self._handle_web_search('web_search', {'query': query}, user_id, trace_id)
            else:
                result = {'error': f'Unknown source: {source}. Valid: kb, spider, web'}
            return _tag(result)

        # ── Stocks desk ──
        STOCKS_MAP = {
            'stocks_alerts': 'alerts',
            'stocks_predictions': 'predictions',
            'stocks_sec_filings': 'sec_filings',
        }
        if action in STOCKS_MAP:
            sp = dict(payload)
            sp['action'] = STOCKS_MAP[action]
            return _tag(self._handle_stock_intelligence('stock_intelligence_tool', sp, user_id, trace_id))

        # ── Sports desk ──
        SPORTS_MAP = {
            'sports_predictions': 'predictions',
            'sports_arbs': 'arbs',
            'sports_wagers': 'wagers',
            'sports_record_wager': 'record_wager',
        }
        if action in SPORTS_MAP:
            sp = dict(payload)
            sp['action'] = SPORTS_MAP[action]
            return _tag(self._handle_sports_betting('sports_betting_tool', sp, user_id, trace_id))

        # ── Legislation desk ──
        LEGISLATION_MAP = {
            'legislation_search': 'search',
            'legislation_summary': 'summary',
        }
        if action in LEGISLATION_MAP:
            lp = dict(payload)
            lp['action'] = LEGISLATION_MAP[action]
            return _tag(self._handle_legislation('legislation_tool', lp, user_id, trace_id))

        # ── KB ──
        if action == 'kb_ingest':
            return _tag(self._handle_rag_query('rag_query_tool', {'action': 'ingest', 'url': payload.get('url', '')}, user_id, trace_id))

        # ── Session 1100: Stock/market intelligence briefs ──
        if action == 'stock_briefs':
            try:
                from core.models_unified_system import MarketIntelligenceBrief
                briefs = MarketIntelligenceBrief.objects.order_by('-brief_date')[:limit]
                return _tag({
                    'action': 'stock_briefs',
                    'count': len(briefs),
                    'briefs': [{
                        'id': str(b.id),
                        'brief_date': str(b.brief_date),
                        'brief_type': b.brief_type,
                        'executive_summary': (b.executive_summary or '')[:300],
                        'high_conviction_count': len(b.high_conviction_opportunities or []),
                        'debate_zone_count': len(b.debate_zone) if hasattr(b, 'debate_zone') and b.debate_zone else 0,
                    } for b in briefs],
                })
            except Exception as e:
                return _tag({'action': 'stock_briefs', 'error': str(e)})

        # ── Session 1100: ML predictions ──
        if action == 'ml_predictions':
            try:
                from sports.models import MLPrediction
                limit = min(int(payload.get('limit', 10)), 30)
                preds = MLPrediction.objects.select_related('game', 'predicted_winner').order_by('-created_at')[:limit]
                total = MLPrediction.objects.count()
                evaluated = MLPrediction.objects.filter(evaluated_at__isnull=False).count()
                return _tag({
                    'action': 'ml_predictions',
                    'total': total,
                    'evaluated': evaluated,
                    'predictions': [{
                        'id': str(p.id),
                        'game': str(p.game) if p.game else None,
                        'predicted_winner': str(p.predicted_winner) if p.predicted_winner else None,
                        'confidence': p.confidence if hasattr(p, 'confidence') else None,
                        'correct': p.correct if hasattr(p, 'correct') else None,
                        'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None,
                    } for p in preds],
                })
            except Exception as e:
                return _tag({'action': 'ml_predictions', 'error': str(e)})

        # ── Session 1100: Signal clusters ──
        if action == 'signal_clusters':
            try:
                from core.models import SignalCluster
                limit = min(int(payload.get('limit', 10)), 30)
                clusters = SignalCluster.objects.order_by('-detected_at')[:limit]
                return _tag({
                    'action': 'signal_clusters',
                    'count': len(clusters),
                    'clusters': [{
                        'id': str(c.id),
                        'name': c.name,
                        'pattern_type': c.pattern_type,
                        'signal_count': c.signal_count if hasattr(c, 'signal_count') else None,
                        'confidence': c.confidence if hasattr(c, 'confidence') else None,
                        'detected_at': c.detected_at.isoformat() if c.detected_at else None,
                    } for c in clusters],
                })
            except Exception as e:
                return _tag({'action': 'signal_clusters', 'error': str(e)})

        all_actions = [
            'overview', 'briefs', 'search',
            'stocks_alerts', 'stocks_predictions', 'stocks_sec_filings',
            'sports_predictions', 'sports_arbs', 'sports_wagers', 'sports_record_wager',
            'legislation_search', 'legislation_summary',
            'kb_ingest',
            'stock_briefs', 'ml_predictions', 'signal_clusters',
        ]
        return {'error': f'Unknown intelligence_tool action: {action}. Valid: {", ".join(all_actions)}'}

    # ── Session 1079: Governance Tool (gateway) ──────────────────────────────────
    def _handle_governance(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1079: Governance gateway — unified human-in-the-loop inbox.
        Wraps boardroom_tool and human_decisions_tool into one surface.
        """
        action = payload.get('action', 'inbox')

        # ── boardroom_tool actions ──
        BOARDROOM_MAP = {
            'inbox': 'stats',
            'attention_list': 'list_attention',
            'attention_approve': 'approve_attention',
            'attention_ignore': 'ignore_attention',
            'attention_lookup': 'lookup',
            'decision_list': 'list_decisions',
            'decision_promote': 'promote_decision',
            'decision_reject': 'reject_decision',
            'triage_batch': 'get_triage_batch',
        }

        if action in BOARDROOM_MAP:
            br_payload = dict(payload)
            br_payload['action'] = BOARDROOM_MAP[action]
            result = self._handle_boardroom('boardroom_tool', br_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'governance_tool'
                result['action'] = action
            return result

        # ── human_decisions_tool actions ──
        DECISIONS_MAP = {
            'decisions_list': 'list',
            'decisions_stats': 'stats',
            'decision_create': 'create',
            'decision_decide': 'decide',
        }

        if action in DECISIONS_MAP:
            hd_payload = dict(payload)
            hd_payload['action'] = DECISIONS_MAP[action]
            # Translate param: id → item_id for decide action
            if action == 'decision_decide':
                if 'id' in hd_payload and 'item_id' not in hd_payload:
                    hd_payload['item_id'] = hd_payload.get('id')
            result = self._handle_human_decisions('human_decisions_tool', hd_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'governance_tool'
                result['action'] = action
            return result

        # ── Session 1100: Failure signatures (read-only) ──
        if action == 'failure_signatures':
            try:
                from core.models_diagnostic_pipeline import FailureSignature
                limit = min(int(payload.get('limit', 10)), 30)
                sigs = FailureSignature.objects.order_by('-last_seen_at')[:limit]
                return {
                    'gateway': 'governance_tool', 'action': action,
                    'count': len(sigs),
                    'signatures': [{
                        'id': str(s.id),
                        'category': s.category,
                        'signature_hash': s.signature_hash[:16] if hasattr(s, 'signature_hash') else '',
                        'occurrence_count': s.occurrence_count if hasattr(s, 'occurrence_count') else 0,
                        'description': (s.description or '')[:200] if hasattr(s, 'description') else '',
                        'last_seen_at': s.last_seen_at.isoformat() if s.last_seen_at else None,
                    } for s in sigs],
                }
            except Exception as e:
                return {'gateway': 'governance_tool', 'action': action, 'error': str(e)}

        # ── Session 1100: Remediation tasks (read-only) ──
        if action == 'remediation_tasks':
            try:
                from core.models_audit_tracking import AuditRemediationTask
                limit = min(int(payload.get('limit', 10)), 30)
                tasks = AuditRemediationTask.objects.select_related('finding').order_by('-id')[:limit]
                return {
                    'gateway': 'governance_tool', 'action': action,
                    'count': len(tasks),
                    'tasks': [{
                        'id': str(t.id),
                        'title': t.title,
                        'status': t.status,
                        'assigned_agent': t.assigned_agent or '',
                        'finding': t.finding.title if t.finding else '',
                    } for t in tasks],
                }
            except Exception as e:
                return {'gateway': 'governance_tool', 'action': action, 'error': str(e)}

        extra_actions = ['failure_signatures', 'remediation_tasks']
        all_actions = sorted(list(BOARDROOM_MAP) + list(DECISIONS_MAP) + extra_actions)
        return {'error': f'Unknown governance_tool action: {action}. Valid: {", ".join(all_actions)}'}

    # ── Session 1079: Content Tool (gateway) ─────────────────────────────────────
    def _handle_content(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1079: Content gateway — thin dispatcher over content_review_tool,
        generate_blog_tool, and deliverables_tool.

        Consolidates 3 content tools into one surface:
        - content_* actions → content_review_tool
        - generate_blog → generate_blog_tool
        - deliverable_* actions → deliverables_tool
        """
        action = payload.get('action', 'content_stats')

        # ── content_review_tool actions ──
        CONTENT_REVIEW_MAP = {
            'content_stats': 'stats',
            'content_list': 'list',
            'content_detail': 'details',
            'content_search': 'search',
            'content_recent': 'recent',
            'content_approve': 'approve',
            'content_reject': 'reject',
        }

        if action in CONTENT_REVIEW_MAP:
            review_payload = dict(payload)
            review_payload['action'] = CONTENT_REVIEW_MAP[action]
            result = self._handle_content_review('content_review_tool', review_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'content_tool'
                result['action'] = action
            return result

        # ── generate_blog_tool ──
        if action == 'generate_blog':
            blog_payload = dict(payload)
            # generate_blog_tool expects 'topic' and optional 'tone'
            result = self._handle_generate_blog('generate_blog_tool', blog_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'content_tool'
                result['action'] = action
            return result

        # ── deliverables_tool actions ──
        DELIVERABLE_MAP = {
            'deliverable_list': 'list',
            'deliverable_detail': 'detail',
            'deliverable_search': 'search',
            'deliverable_save': 'save',
            'deliverable_create': 'create',
            'deliverable_stats': 'stats',
            'deliverable_export_pdf': 'export_pdf',
        }

        if action in DELIVERABLE_MAP:
            del_payload = dict(payload)
            del_payload['action'] = DELIVERABLE_MAP[action]
            result = self._handle_deliverables('deliverables_tool', del_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'content_tool'
                result['action'] = action
            return result

        # ── Session 1100: Podcast episodes ──
        if action == 'podcasts':
            try:
                from core.models_unified_system import AgentExecution
                limit = min(int(payload.get('limit', 10)), 30)
                eps = AgentExecution.objects.filter(
                    agent__name='PodcastCoordinatorAgent', status='completed'
                ).order_by('-created_at')[:limit]
                return {
                    'gateway': 'content_tool', 'action': action,
                    'count': len(eps),
                    'episodes': [{
                        'id': str(e.id),
                        'topic': (e.input_data or {}).get('task', '')[:150],
                        'status': e.status,
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    } for e in eps],
                }
            except Exception as e:
                return {'gateway': 'content_tool', 'action': action, 'error': str(e)}

        # ── Session 1100: AI Series workflows ──
        if action == 'series':
            try:
                from core.models_unified_system import AgentExecution
                limit = min(int(payload.get('limit', 10)), 30)
                series = AgentExecution.objects.filter(
                    agent__name='AISeriesWorkflowAgent'
                ).order_by('-created_at')[:limit]
                return {
                    'gateway': 'content_tool', 'action': action,
                    'count': len(series),
                    'series': [{
                        'id': str(s.id),
                        'topic': (s.input_data or {}).get('task', '')[:150],
                        'status': s.status,
                        'created_at': s.created_at.isoformat() if s.created_at else None,
                    } for s in series],
                }
            except Exception as e:
                return {'gateway': 'content_tool', 'action': action, 'error': str(e)}

        # ── Session 1100: Content Studio stats ──
        if action == 'content_studio':
            try:
                from core.models_unified_system import AgentExecution
                from django.db.models import Count
                studio_agents = [
                    'AutonomousContentStudioCoordinator', 'TopicMinerAgent',
                    'ContrarianAgent', 'PerformanceAnalystAgent',
                    'VoiceCriticAgent', 'ContentDiversityOrchestrator',
                ]
                stats = list(AgentExecution.objects.filter(
                    agent__name__in=studio_agents
                ).values('agent__name', 'status').annotate(count=Count('id')))
                return {
                    'gateway': 'content_tool', 'action': action,
                    'stats': stats,
                }
            except Exception as e:
                return {'gateway': 'content_tool', 'action': action, 'error': str(e)}

        all_actions = sorted(
            list(CONTENT_REVIEW_MAP) + ['generate_blog'] + list(DELIVERABLE_MAP)
            + ['podcasts', 'series', 'content_studio']
        )
        return {'error': f'Unknown content_tool action: {action}. Valid: {", ".join(all_actions)}'}

    # ── Session 1078: Ops Tool ─────────────────────────────────────────────────
    def _handle_ops(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1078: Production ops surface — version, SLO status, failure signatures.
        Separate from status_snapshot_tool to keep snapshot cheap and fast.
        """
        action = payload.get('action', 'version')

        if action == 'version':
            return self._ops_version(trace_id)
        elif action == 'slo_status':
            window = payload.get('window', '24h')
            include_breakdowns = payload.get('include_breakdowns', False)
            since = payload.get('since')  # Session 1080: ISO-8601 override
            return self._ops_slo_status(window, include_breakdowns, trace_id, since=since)
        elif action == 'failure_signatures':
            window = payload.get('window', '24h')
            limit = min(int(payload.get('limit', 10)), 25)
            since = payload.get('since')  # Session 1080: ISO-8601 override
            return self._ops_failure_signatures(window, limit, trace_id, since=since)
        elif action == 'tool_migration_report':
            window = payload.get('window', '7d')
            return self._ops_tool_migration_report(window, trace_id)

        elif action == 'timeout_config_read':
            # Session 1098: Read agent wall-clock timeout config (code defaults + DB overrides)
            agent_names = payload.get('agent_names', [])
            return self._ops_timeout_config_read(agent_names, trace_id)

        elif action == 'proof_bundle':
            # Session 1098: Verification mode — returns timeout config + audit log
            # for specified agents in a single call. Read-only, no mutations.
            agent_names = payload.get('agent_names', [])
            initiative_id = payload.get('initiative_id')
            return self._ops_proof_bundle(agent_names, initiative_id, trace_id)

        elif action == 'beat_schedule':
            # Session 1100: Proxy to cockpit_tool for beat schedule
            return self._handle_cockpit('cockpit_tool', {'action': 'beat_schedule', 'limit': payload.get('limit', 20)}, user_id, trace_id)

        elif action == 'noise_metrics':
            # Session 1077: North Star coverage + run noise breakdown
            from core.services.noise_metrics import compute_runs_metrics
            window = payload.get('window', '24h')
            hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
            return compute_runs_metrics(hours=hours)

        elif action == 'conversation_metrics':
            # Session 1077: Topic clustering + zombie rate
            from core.services.noise_metrics import compute_conversation_metrics
            window = payload.get('window', '24h')
            hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
            return compute_conversation_metrics(hours=hours)

        elif action == 'focus_mode_status':
            # Session 1077: Read Focus Mode config
            from core.services.focus_mode import get_status
            return {'action': 'focus_mode_status', **get_status()}

        elif action == 'focus_mode_update':
            # Session 1077: Update Focus Mode config
            from core.services.focus_mode import set_config, get_status
            config_updates = payload.get('config_updates', {})
            if not config_updates:
                return {'error': 'config_updates dict required'}
            set_config(config_updates)
            return {'action': 'focus_mode_update', 'applied': list(config_updates.keys()), **get_status()}

        else:
            return {'error': f'Unknown ops_tool action: {action}'}

    def _ops_version(self, trace_id: str) -> Dict[str, Any]:
        """Return build/deploy metadata for the running process."""
        import os
        import time
        import django
        from datetime import timedelta

        _boot_time = getattr(self, '_boot_time', None)
        if not _boot_time:
            self._boot_time = time.time()
            _boot_time = self._boot_time

        from django.utils import timezone

        now = timezone.now()
        uptime_seconds = time.time() - _boot_time

        return {
            'action': 'version',
            'service': os.environ.get('RAILWAY_SERVICE_NAME', 'unknown'),
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
            'git': {
                'sha': os.environ.get('RAILWAY_GIT_COMMIT_SHA', 'dev'),
                'branch': os.environ.get('RAILWAY_GIT_BRANCH', 'unknown'),
            },
            'railway': {
                'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
            },
            'runtime': {
                'started_at': (now - timedelta(seconds=uptime_seconds)).isoformat(),
                'uptime_seconds': round(uptime_seconds),
            },
            'app': {
                'django_version': django.get_version(),
            },
        }

    def _ops_slo_status(self, window: str, include_breakdowns: bool, trace_id: str, since: str = None) -> Dict[str, Any]:
        """Compute 8 SLOs for the given time window."""
        from django.utils import timezone
        from django.core.cache import cache
        from django.db.models import Count
        from datetime import timedelta, datetime

        # Session 1080: since_timestamp overrides window
        if since:
            cache_key = f'pa:ops_slo:since:{since}:{include_breakdowns}'
        else:
            cache_key = f'pa:ops_slo:{window}:{include_breakdowns}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Parse window (Session 1080: added 1h + since_timestamp)
        now = timezone.now()
        if since:
            try:
                cutoff = datetime.fromisoformat(since.replace('Z', '+00:00'))
                if timezone.is_naive(cutoff):
                    cutoff = timezone.make_aware(cutoff)
                window = f'since:{since}'
            except (ValueError, TypeError):
                window_hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
                cutoff = now - timedelta(hours=window_hours)
        else:
            window_hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
            cutoff = now - timedelta(hours=window_hours)

        slos = []

        # SLO 1: Celery task success rate (≥99.9%)
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            total = CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status__in=['SUCCESS', 'FAILURE']).count()
            failed = CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status='FAILURE').count()
            rate = (total - failed) / total if total > 0 else 1.0
            slo = {
                'key': 'celery_task_success_rate',
                'name': 'Celery task success rate',
                'target': 0.999,
                'current': round(rate, 6),
                'breach': rate < 0.999,
                'numerator': total - failed,
                'denominator': total,
            }
            if include_breakdowns and failed > 0:
                top_failing = list(
                    CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status='FAILURE')
                    .values('task_name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                )
                slo['top_failures'] = top_failing
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'celery_task_success_rate', 'error': str(e)})

        # SLO 2: execute_agent_task success rate (≥99.95%)
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            agent_total = CeleryTaskEvent.objects.filter(
                started_at__gte=cutoff, task_name='core.tasks.execute_agent_task',
                status__in=['SUCCESS', 'FAILURE']
            ).count()
            agent_failed = CeleryTaskEvent.objects.filter(
                started_at__gte=cutoff, task_name='core.tasks.execute_agent_task',
                status='FAILURE'
            ).count()
            agent_rate = (agent_total - agent_failed) / agent_total if agent_total > 0 else 1.0
            slo = {
                'key': 'agent_task_success_rate',
                'name': 'execute_agent_task success rate',
                'target': 0.9995,
                'current': round(agent_rate, 6),
                'breach': agent_rate < 0.9995,
                'numerator': agent_total - agent_failed,
                'denominator': agent_total,
            }
            if include_breakdowns and agent_failed > 0:
                from core.models_unified_system import AgentExecution
                top_agents = list(
                    AgentExecution.objects.filter(
                        created_at__gte=cutoff, status='failed'
                    ).values('agent__name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                )
                slo['top_failing_agents'] = top_agents
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'agent_task_success_rate', 'error': str(e)})

        # SLO 3: Agent wall-clock timeout rate (≤0.2%)
        try:
            from core.models_unified_system import AgentExecution
            total_execs = AgentExecution.objects.filter(created_at__gte=cutoff).count()
            timeout_execs = AgentExecution.objects.filter(
                created_at__gte=cutoff, status='failed',
                error_message__icontains='timed out'
            ).count()
            timeout_rate = timeout_execs / total_execs if total_execs > 0 else 0.0
            slo = {
                'key': 'agent_timeout_rate',
                'name': 'Agent wall-clock timeout rate',
                'target_max': 0.002,
                'current': round(timeout_rate, 6),
                'breach': timeout_rate > 0.002,
                'numerator': timeout_execs,
                'denominator': total_execs,
            }
            if include_breakdowns and timeout_execs > 0:
                top_timeout = list(
                    AgentExecution.objects.filter(
                        created_at__gte=cutoff, status='failed',
                        error_message__icontains='timed out'
                    ).values('agent__name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                )
                slo['top_timeout_agents'] = top_timeout
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'agent_timeout_rate', 'error': str(e)})

        # SLO 4: Deliberation zero-turn rate (0%)
        # Session 1075: Exclude ZOMBIE_REAPED — those are legitimate reaper cleanups
        # (stuck sessions cleaned up by reap_zombie_work), not pipeline bugs.
        try:
            from core.models_deliberation import DeliberationSession
            total_sessions = DeliberationSession.objects.filter(created_at__gte=cutoff).count()
            zero_turn = DeliberationSession.objects.filter(
                created_at__gte=cutoff, status='failed'
            ).exclude(
                failure_reason_code='ZOMBIE_REAPED'
            ).annotate(
                turn_count=Count('turns')
            ).filter(turn_count=0).count()
            zt_rate = zero_turn / total_sessions if total_sessions > 0 else 0.0
            zombie_reaped = DeliberationSession.objects.filter(
                created_at__gte=cutoff, status='failed',
                failure_reason_code='ZOMBIE_REAPED'
            ).count()
            slo = {
                'key': 'deliberation_zero_turn_rate',
                'name': 'Deliberation zero-turn failure rate',
                'target_max': 0.001,
                'current': round(zt_rate, 6),
                'breach': zt_rate > 0.001,
                'numerator': zero_turn,
                'denominator': total_sessions,
                'zombie_reaped': zombie_reaped,
            }
            # Include failure reason breakdown if any failed sessions exist
            if include_breakdowns:
                reason_breakdown = list(
                    DeliberationSession.objects.filter(
                        created_at__gte=cutoff, status='failed'
                    ).exclude(failure_reason_code='').values('failure_reason_code')
                    .annotate(count=Count('id')).order_by('-count')
                )
                if reason_breakdown:
                    slo['failure_reasons'] = reason_breakdown
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'deliberation_zero_turn_rate', 'error': str(e)})

        # SLO 5: Content publish conversion (≥40%)
        # Session 1080: Scoped to deliberation-sourced blogs only. Other SelfBlog
        # creators (initiative pipeline, research briefs, audit reports) have no
        # path to PublishGate and were inflating the denominator.
        try:
            from core.models_unified_system import SelfBlog
            delib_filter = {'created_at__gte': cutoff, 'author': 'ContentDeliberation'}
            blogs_created = SelfBlog.objects.filter(**delib_filter).count()
            blogs_published = SelfBlog.objects.filter(
                **delib_filter, status__in=['approved', 'published']
            ).count()
            pub_rate = blogs_published / blogs_created if blogs_created > 0 else None
            slos.append({
                'key': 'content_publish_conversion',
                'name': 'Content publish conversion rate',
                'target': 0.40,
                'current': round(pub_rate, 4) if pub_rate is not None else None,
                'breach': pub_rate < 0.40 if pub_rate is not None else False,
                'numerator': blogs_published,
                'denominator': blogs_created,
                'status': 'no_data' if blogs_created == 0 else ('ok' if pub_rate >= 0.40 else 'breach'),
            })
        except Exception as e:
            slos.append({'key': 'content_publish_conversion', 'error': str(e)})

        # SLO 6: Publish-ready backlog age p95 (≤72h)
        try:
            from core.models_unified_system import SelfBlog
            ready_blogs = SelfBlog.objects.filter(
                publish_ready=True, status__in=['approved', 'pending_review']
            ).order_by('created_at')
            ages_hours = []
            for blog in ready_blogs[:100]:
                age = (now - blog.created_at).total_seconds() / 3600
                ages_hours.append(age)
            if ages_hours:
                ages_hours.sort()
                p95_idx = int(len(ages_hours) * 0.95)
                p95_age = ages_hours[min(p95_idx, len(ages_hours) - 1)]
            else:
                p95_age = 0.0
            slos.append({
                'key': 'publish_ready_age_p95',
                'name': 'Publish-ready backlog age (p95 hours)',
                'target_max': 72.0,
                'current': round(p95_age, 1),
                'breach': p95_age > 72.0,
                'backlog_count': len(ages_hours),
            })
        except Exception as e:
            slos.append({'key': 'publish_ready_age_p95', 'error': str(e)})

        # SLO 7: PA tool success rate (≥99.9%)
        try:
            from core.models import ToolCallRecord
            pa_total = ToolCallRecord.objects.filter(created_at__gte=cutoff).count()
            pa_failed = ToolCallRecord.objects.filter(created_at__gte=cutoff, success=False).count()
            pa_rate = (pa_total - pa_failed) / pa_total if pa_total > 0 else 1.0
            slo = {
                'key': 'pa_tool_success_rate',
                'name': 'PA tool call success rate',
                'target': 0.999,
                'current': round(pa_rate, 6),
                'breach': pa_rate < 0.999,
                'numerator': pa_total - pa_failed,
                'denominator': pa_total,
            }
            if include_breakdowns and pa_failed > 0:
                top_pa_fail = list(
                    ToolCallRecord.objects.filter(created_at__gte=cutoff, success=False)
                    .values('tool_name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                )
                slo['top_failing_tools'] = top_pa_fail
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'pa_tool_success_rate', 'error': str(e)})

        # SLO 8: External HTTP failure rate (informational, ≤5%)
        try:
            from core.models_diagnostic_pipeline import FailureDetection
            http_errors = FailureDetection.objects.filter(
                detected_at__gte=cutoff, source_type='http_request'
            ).count()
            # Approximate total from celery + tool calls as proxy
            from core.models_celery_telemetry import CeleryTaskEvent
            approx_total = CeleryTaskEvent.objects.filter(started_at__gte=cutoff).count()
            http_rate = http_errors / approx_total if approx_total > 0 else 0.0
            slos.append({
                'key': 'external_http_failure_rate',
                'name': 'External HTTP failure rate (informational)',
                'target_max': 0.05,
                'current': round(http_rate, 6),
                'breach': http_rate > 0.05,
                'numerator': http_errors,
                'denominator': approx_total,
                'note': 'Denominator is approx (total celery tasks as proxy)',
            })
        except Exception as e:
            slos.append({'key': 'external_http_failure_rate', 'error': str(e)})

        breaches = sum(1 for s in slos if s.get('breach'))
        result = {
            'action': 'slo_status',
            'window': window,
            'generated_at': now.isoformat(),
            'total_slos': len(slos),
            'breaches': breaches,
            'all_clear': breaches == 0,
            'slos': slos,
        }

        cache.set(cache_key, result, 120)  # 2-min cache
        return result

    def _ops_failure_signatures(self, window: str, limit: int, trace_id: str, since: str = None) -> Dict[str, Any]:
        """Top failure signatures in the given window, deduped and actionable."""
        from django.utils import timezone
        from datetime import timedelta, datetime
        from django.db.models import Count, Max

        now = timezone.now()
        if since:
            try:
                cutoff = datetime.fromisoformat(since.replace('Z', '+00:00'))
                if timezone.is_naive(cutoff):
                    cutoff = timezone.make_aware(cutoff)
                window = f'since:{since}'
            except (ValueError, TypeError):
                window_hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
                cutoff = now - timedelta(hours=window_hours)
        else:
            window_hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
            cutoff = now - timedelta(hours=window_hours)

        signatures = []

        try:
            from core.models_diagnostic_pipeline import FailureSignature, FailureDetection

            # Get signatures with recent detections in window
            from django.db.models import Q as _Q
            sig_qs = FailureSignature.objects.filter(
                status='active',
                detections__detected_at__gte=cutoff,
            ).annotate(
                window_count=Count('detections', filter=_Q(detections__detected_at__gte=cutoff)),
                last_detection=Max('detections__detected_at'),
            ).order_by('-window_count')[:limit]

            for sig in sig_qs:
                # Get sample detections for context
                samples = list(
                    FailureDetection.objects.filter(
                        signature=sig, detected_at__gte=cutoff
                    ).order_by('-detected_at')
                    .values('source_type', 'source_name', 'detected_at')[:3]
                )
                for s in samples:
                    s['detected_at'] = s['detected_at'].isoformat()

                signatures.append({
                    'signature': sig.signature,
                    'category': sig.category,
                    'provider': sig.provider or '',
                    'description': sig.description[:200] if sig.description else '',
                    'window_count': sig.window_count,
                    'total_count': sig.occurrence_count,
                    'last_seen': sig.last_detection.isoformat() if sig.last_detection else '',
                    'status': sig.status,
                    'samples': samples,
                })
        except Exception as e:
            return {'action': 'failure_signatures', 'error': str(e)}

        # Also get top Celery task failures (in case not captured by diagnostic pipeline)
        celery_failures = []
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            top_celery = list(
                CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status='FAILURE')
                .values('task_name', 'error_type')
                .annotate(count=Count('id'), last_seen=Max('started_at'))
                .order_by('-count')[:5]
            )
            for cf in top_celery:
                cf['last_seen'] = cf['last_seen'].isoformat() if cf['last_seen'] else ''
            celery_failures = top_celery
        except Exception:
            pass

        return {
            'action': 'failure_signatures',
            'window': window,
            'generated_at': timezone.now().isoformat(),
            'signatures': signatures,
            'celery_task_failures': celery_failures,
            'total_signatures': len(signatures),
        }


    # ── Session 1080: Agent Control Tool ────────────────────────────────────

    def _handle_agent_control(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1080: Centralized agent block/unblock/list.
        Replaces hardcoded frozensets across tasks.py, agent_router.py, tool_dispatcher.py.
        """
        from core.models_unified_system import AgentControlEntry
        from django.utils import timezone

        action = payload.get('action', 'list')

        if action == 'list':
            entries = list(
                AgentControlEntry.objects.all()
                .order_by('-updated_at')
                .values('agent_name', 'status', 'reason', 'blocked_at',
                        'blocked_by', 'ttl_hours', 'updated_at')
            )
            for e in entries:
                if e.get('blocked_at'):
                    e['blocked_at'] = e['blocked_at'].isoformat()
                if e.get('updated_at'):
                    e['updated_at'] = e['updated_at'].isoformat()

            # Also show currently blocked set (includes TTL expiry check)
            blocked_now = sorted(AgentControlEntry.get_blocked_names())

            return {
                'action': 'list',
                'blocked_now': blocked_now,
                'total_entries': len(entries),
                'entries': entries,
            }

        elif action == 'block':
            agent_name = payload.get('agent_name', '').strip()
            if not agent_name:
                raise ValueError("agent_name required for block action")
            reason = payload.get('reason', 'Blocked via PA')
            ttl_hours = payload.get('ttl_hours')
            blocked_by = payload.get('blocked_by', 'rigby')

            now = timezone.now()
            entry, created = AgentControlEntry.objects.update_or_create(
                agent_name=agent_name,
                defaults={
                    'status': 'blocked',
                    'reason': reason[:255],
                    'blocked_at': now,
                    'blocked_by': blocked_by[:100],
                    'ttl_hours': ttl_hours,
                }
            )

            return {
                'action': 'block',
                'agent_name': agent_name,
                'status': 'blocked',
                'reason': reason,
                'ttl_hours': ttl_hours,
                'blocked_by': blocked_by,
                'created': created,
                'success': True,
            }

        elif action == 'unblock':
            agent_name = payload.get('agent_name', '').strip()
            if not agent_name:
                raise ValueError("agent_name required for unblock action")
            reason = payload.get('reason', 'Unblocked via PA')

            updated = AgentControlEntry.objects.filter(
                agent_name=agent_name, status='blocked'
            ).update(status='enabled', reason=reason[:255])

            return {
                'action': 'unblock',
                'agent_name': agent_name,
                'status': 'enabled',
                'was_blocked': updated > 0,
                'success': True,
            }

        elif action == 'audit_log':
            # Show recent changes — uses updated_at ordering
            limit = min(int(payload.get('limit', 20)), 50)
            entries = list(
                AgentControlEntry.objects.all()
                .order_by('-updated_at')[:limit]
                .values('agent_name', 'status', 'reason', 'blocked_at',
                        'blocked_by', 'ttl_hours', 'updated_at')
            )
            for e in entries:
                if e.get('blocked_at'):
                    e['blocked_at'] = e['blocked_at'].isoformat()
                if e.get('updated_at'):
                    e['updated_at'] = e['updated_at'].isoformat()

            return {
                'action': 'audit_log',
                'count': len(entries),
                'entries': entries,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. "
                f"Valid: list, block, unblock, audit_log"
            )

    # ── Session 1080: Ops Autopilot Tool ──────────────────────────────────

    def _handle_autopilot(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1080: Autopilot visibility — status, history, run, config.
        Lets Rigby inspect and trigger the Ops Autopilot.
        """
        from core.models_diagnostic_pipeline import AutopilotAction
        from core.services.ops_autopilot import OpsAutopilot, AutopilotConfig
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'status')

        # Guard: AutopilotAction table may not exist yet on Railway
        def _safe_autopilot_query(fn, default=None):
            try:
                return fn()
            except Exception:
                return default

        if action == 'status':
            # Current config + last cycle info
            last_action = _safe_autopilot_query(
                lambda: AutopilotAction.objects.first()
            )
            last_cycle = None
            if last_action:
                last_cycle = {
                    'action_type': last_action.action_type,
                    'agent_name': last_action.agent_name,
                    'policy': last_action.policy,
                    'dry_run': last_action.dry_run,
                    'created_at': last_action.created_at.isoformat(),
                    'deploy_sha': last_action.deploy_sha,
                }

            total_actions = _safe_autopilot_query(
                lambda: AutopilotAction.objects.count(), 0
            )
            blocks_24h = _safe_autopilot_query(
                lambda: AutopilotAction.objects.filter(
                    action_type='block_agent',
                    dry_run=False,
                    created_at__gte=timezone.now() - timedelta(hours=24),
                ).count(), 0
            )

            return {
                'action': 'status',
                'config': {
                    'timeout_spike_threshold': AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD,
                    'timeout_spike_window_minutes': AutopilotConfig.TIMEOUT_SPIKE_WINDOW_MINUTES,
                    'timeout_block_ttl_minutes': AutopilotConfig.TIMEOUT_BLOCK_TTL_MINUTES,
                    'max_blocks_per_agent_per_hour': AutopilotConfig.MAX_BLOCKS_PER_AGENT_PER_HOUR,
                    'max_total_blocks_per_cycle': AutopilotConfig.MAX_TOTAL_BLOCKS_PER_CYCLE,
                    'stale_block_hours': AutopilotConfig.STALE_BLOCK_HOURS,
                    'dry_run': AutopilotConfig.DRY_RUN,
                },
                'last_action': last_cycle,
                'total_actions_ever': total_actions,
                'blocks_last_24h': blocks_24h,
                'beat_schedule': 'every 10 minutes',
            }

        elif action == 'history':
            limit = min(int(payload.get('limit', 20)), 100)
            actions = _safe_autopilot_query(
                lambda: list(
                    AutopilotAction.objects.all()[:limit].values(
                        'id', 'created_at', 'action_type', 'agent_name',
                        'policy', 'dry_run', 'deploy_sha',
                    )
                ), []
            )
            for a in actions:
                a['created_at'] = a['created_at'].isoformat()

            return {
                'action': 'history',
                'count': len(actions),
                'actions': actions,
            }

        elif action == 'run':
            dry_run = payload.get('dry_run', False)
            try:
                autopilot = OpsAutopilot(dry_run=dry_run)
                summary = autopilot.run()
            except Exception as e:
                return {
                    'action': 'run',
                    'error': f'Autopilot run failed (table may not exist yet): {str(e)[:200]}',
                }
            return {
                'action': 'run',
                'dry_run': dry_run,
                'summary': summary,
            }

        elif action == 'config':
            return {
                'action': 'config',
                'timeout_spike_threshold': AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD,
                'timeout_spike_window_minutes': AutopilotConfig.TIMEOUT_SPIKE_WINDOW_MINUTES,
                'timeout_block_ttl_minutes': AutopilotConfig.TIMEOUT_BLOCK_TTL_MINUTES,
                'max_blocks_per_agent_per_hour': AutopilotConfig.MAX_BLOCKS_PER_AGENT_PER_HOUR,
                'max_total_blocks_per_cycle': AutopilotConfig.MAX_TOTAL_BLOCKS_PER_CYCLE,
                'stale_block_hours': AutopilotConfig.STALE_BLOCK_HOURS,
                'dry_run': AutopilotConfig.DRY_RUN,
                'note': (
                    'Config is currently code-level. '
                    'Changing thresholds requires a deploy.'
                ),
            }

        elif action == 'dry_run_report':
            # Run autopilot in dry-run mode and return human-readable report
            autopilot = OpsAutopilot(dry_run=True)
            summary = autopilot.run()

            # Also fetch current SLO status for context
            slo_data = self._ops_slo_status(
                window='24h', include_breakdowns=True, trace_id=trace_id,
            )
            breaches = [
                s for s in slo_data.get('slos', [])
                if s.get('breach', False)
            ]

            report_lines = ['## Autopilot Dry-Run Report\n']
            report_lines.append(f"**Mode:** DRY RUN (no actions taken)")
            report_lines.append(f"**Deploy SHA:** {summary.get('deploy_sha', 'unknown')}\n")

            # SLO breaches section
            if breaches:
                report_lines.append(f"### SLO Breaches ({len(breaches)})")
                for b in breaches:
                    report_lines.append(
                        f"- **{b.get('name', b.get('key'))}**: "
                        f"current={b.get('current')} "
                        f"(target {'<=' if 'target_max' in b else '>='} "
                        f"{b.get('target_max', b.get('target', '?'))})"
                    )
            else:
                report_lines.append('### SLO Breaches: None')

            # Timeout spike section
            ts = summary.get('timeout_spike', {})
            agents_checked = ts.get('agents_checked', {})
            if agents_checked:
                report_lines.append(f"\n### Timeout Spike Analysis")
                for agent, count in agents_checked.items():
                    would_block = count >= AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD
                    report_lines.append(
                        f"- {agent}: {count} timeouts "
                        f"{'→ WOULD BLOCK' if would_block else '(below threshold)'}"
                    )
            else:
                report_lines.append(f"\n### Timeout Spike Analysis: No timeouts detected")

            # Blocked agent hygiene
            hygiene = summary.get('blocked_hygiene', {})
            stale = hygiene.get('stale_blocks', [])
            if stale:
                report_lines.append(f"\n### Stale Blocks ({len(stale)})")
                for s in stale:
                    report_lines.append(
                        f"- {s['agent_name']}: blocked {s['blocked_hours']}h "
                        f"({s['reason']}) — consider adding TTL or unblocking"
                    )
            else:
                report_lines.append(f"\n### Stale Blocks: None")

            # Deliberation retry section
            delib = summary.get('deliberation_retry', {})
            retried = delib.get('retried', 0)
            skipped = delib.get('skipped', 0)
            if retried > 0 or skipped > 0:
                report_lines.append(f"\n### Deliberation Retry")
                report_lines.append(f"- Would retry: {retried} failed sessions")
                if skipped:
                    report_lines.append(f"- Skipped: {skipped} (already retried or no valid topic)")
            else:
                report_lines.append(f"\n### Deliberation Retry: No retryable failures")

            # Content sweep section
            content = summary.get('content_sweep', {})
            enhance = content.get('kicked_enhance', 0)
            review = content.get('kicked_review', 0)
            if enhance or review:
                report_lines.append(f"\n### Content Pipeline Sweep")
                if enhance:
                    report_lines.append(f"- Would kick {enhance} stuck needs_enhancement blogs")
                if review:
                    report_lines.append(f"- Would kick {review} unscored pending_review blogs")
            else:
                report_lines.append(f"\n### Content Pipeline Sweep: No stuck content")

            # Attention auto-resolve section
            attn = summary.get('attention_resolve', {})
            resolved = attn.get('resolved', 0)
            if resolved:
                report_lines.append(f"\n### Attention Auto-Resolve")
                report_lines.append(f"- Would auto-resolve: {resolved} stale ops alerts")
            else:
                report_lines.append(f"\n### Attention Auto-Resolve: No stale alerts")

            # Governance auto-decision section
            gov = summary.get('governance_auto', {})
            gov_approved = gov.get('auto_approved', 0)
            gov_dismissed = gov.get('auto_dismissed', 0)
            gov_skipped = gov.get('skipped', 0)
            if gov_approved or gov_dismissed:
                report_lines.append(f"\n### Governance Auto-Decision")
                if gov_approved:
                    report_lines.append(f"- Would auto-approve: {gov_approved} low-risk items")
                if gov_dismissed:
                    report_lines.append(f"- Would auto-dismiss: {gov_dismissed} low-risk items")
                if gov_skipped:
                    report_lines.append(f"- Skipped (high blast radius): {gov_skipped}")
            else:
                report_lines.append(f"\n### Governance Auto-Decision: No eligible items")

            # Actions proposed
            proposed = summary.get('actions', [])
            if proposed:
                report_lines.append(f"\n### Proposed Actions ({len(proposed)})")
                for a in proposed:
                    target = a.get('agent_name', a.get('session_id', a.get('blog_id', a.get('attention_item_id', '?'))))
                    if isinstance(target, str) and len(target) > 20:
                        target = target[:20]
                    report_lines.append(f"- {a.get('type', '?')}: {target} — {a.get('reason', a.get('governance_action', a.get('action', '')))}")
            else:
                report_lines.append(f"\n### Proposed Actions: None (system healthy)")

            # Verification + rollback stats (last 24h)
            try:
                from core.models_diagnostic_pipeline import AutopilotAction
                from django.utils import timezone as tz
                from datetime import timedelta
                day_cutoff = tz.now() - timedelta(hours=24)
                recent_actions = AutopilotAction.objects.filter(
                    created_at__gte=day_cutoff,
                    dry_run=False,
                )
                verif_pending = recent_actions.filter(verification_state='pending').count()
                verif_passed = recent_actions.filter(verification_state='passed').count()
                verif_failed = recent_actions.filter(verification_state='failed').count()
                rolled_back = recent_actions.filter(rolled_back=True).count()
                remediations = recent_actions.filter(action_type='remediate').count()
                report_lines.append(f"\n### Verification & Safety (24h)")
                report_lines.append(f"- Verified passed: {verif_passed}")
                report_lines.append(f"- Pending verification: {verif_pending}")
                report_lines.append(f"- Failed verification: {verif_failed}")
                report_lines.append(f"- Auto-rolled back: {rolled_back}")
                report_lines.append(f"- Auto-remediations applied: {remediations}")
            except Exception:
                pass

            # Remediation playbook stats
            try:
                from core.models_diagnostic_pipeline import RemediationPlaybook
                playbook_count = RemediationPlaybook.objects.filter(enabled=True).count()
                if playbook_count > 0:
                    top_playbook = RemediationPlaybook.objects.filter(
                        enabled=True, times_applied__gte=1,
                    ).order_by('-success_rate').first()
                    report_lines.append(f"\n### Remediation Playbook")
                    report_lines.append(f"- Active entries: {playbook_count}")
                    if top_playbook:
                        report_lines.append(
                            f"- Top entry: {top_playbook.signature_pattern} → "
                            f"{top_playbook.remediation_type} "
                            f"({top_playbook.success_rate:.0%} success, "
                            f"{top_playbook.times_applied}x applied)"
                        )
            except Exception:
                pass

            # Self-tuning status
            try:
                from core.services.ops_autopilot import PolicyOptimizer
                optimizer = PolicyOptimizer()
                tuning_eval = optimizer.evaluate()
                recs = tuning_eval.get('recommendations', [])
                if recs:
                    report_lines.append(f"\n### Self-Tuning Recommendations ({len(recs)})")
                    for r in recs:
                        report_lines.append(
                            f"- **{r['param']}**: {r['old_value']} → "
                            f"{r['new_value']} ({r['confidence']})\n"
                            f"  _{r['reason']}_"
                        )
                else:
                    report_lines.append('\n### Self-Tuning: All parameters optimal')

                overrides = AutopilotConfig._override_cache
                if overrides:
                    report_lines.append(f"\n### Active Config Overrides ({len(overrides)})")
                    for param, val in overrides.items():
                        report_lines.append(f"- {param}: {val}")
            except Exception:
                pass

            # QROI attribution section
            try:
                from core.services.ops_autopilot import ROIEnforcer
                enforcer = ROIEnforcer()
                roi_data = enforcer.compute_roi_scores(tz.now(), window_hours=24)
                if roi_data.get('agents'):
                    report_lines.append(f"\n### QROI Attribution (24h)")
                    report_lines.append(
                        f"Total spend: ${roi_data['total_spend']:.2f} — "
                        f"{roi_data['total_outcomes']} outcomes"
                    )
                    for a in roi_data['agents'][:5]:
                        report_lines.append(
                            f"- **{a['agent_name']}**: "
                            f"QROI {a.get('qroi', a['roi']):.1%} "
                            f"(ROI {a['roi']:.1%} × "
                            f"Q {a.get('quality_weight', 0.5):.2f}) — "
                            f"${a['cost']:.4f}, {a['outcomes']} outcomes"
                        )
                    recs = enforcer.get_throttle_recommendations(tz.now())
                    if recs:
                        report_lines.append(
                            f"\n**Would throttle {len(recs)} agents** "
                            f"under budget pressure"
                        )
            except Exception:
                pass

            return {
                'action': 'dry_run_report',
                'report': '\n'.join(report_lines),
                'summary': summary,
                'slo_breaches': len(breaches),
                'proposed_actions': len(proposed),
            }

        elif action == 'drift_scan':
            # Run contract/schema drift detection on demand
            from core.services.contract_monitor import ContractMonitor
            monitor = ContractMonitor()
            report = monitor.full_scan()
            summary_text = monitor.summary_for_governance(report)
            return {
                'action': 'drift_scan',
                'critical': report['critical'],
                'warning': report['warning'],
                'info': report['info'],
                'total': report['total'],
                'checks_run': report['checks_run'],
                'summary': summary_text,
                'findings': report['findings'],
            }

        elif action == 'tuning_report':
            # Show current tuning state, overrides, and recent changes
            from core.services.ops_autopilot import PolicyOptimizer
            AutopilotConfig.load_overrides()
            optimizer = PolicyOptimizer()

            # Evaluate recommendations (read-only)
            evaluation = optimizer.evaluate()
            tuning_status = optimizer.get_tuning_report()

            report_lines = ['## Policy Self-Tuning Report\n']

            # Active overrides
            overrides = tuning_status.get('overrides_active', {})
            if overrides:
                report_lines.append(f'### Active Overrides ({len(overrides)})')
                for param, value in overrides.items():
                    spec = PolicyOptimizer.TUNABLES.get(param, {})
                    default = spec.get('default', '?')
                    report_lines.append(
                        f'- **{param}**: {value} (default: {default})'
                    )
            else:
                report_lines.append('### Active Overrides: None (all defaults)')

            # Current recommendations
            recs = evaluation.get('recommendations', [])
            if recs:
                report_lines.append(f'\n### Recommendations ({len(recs)})')
                for r in recs:
                    report_lines.append(
                        f'- **{r["param"]}**: {r["old_value"]} → '
                        f'{r["new_value"]} ({r["confidence"]} confidence)\n'
                        f'  {r["reason"]}'
                    )
            else:
                report_lines.append('\n### Recommendations: None (all params optimal)')

            # Recent changes
            changes = tuning_status.get('recent_changes', [])
            if changes:
                report_lines.append(f'\n### Recent Changes (7d)')
                for c in changes[:5]:
                    report_lines.append(
                        f'- **{c["param"]}**: {c["old_value"]} → '
                        f'{c["new_value"]} @ {c["when"][:16]}'
                    )

            # Policy metrics
            pm = evaluation.get('policy_metrics', {})
            if pm:
                report_lines.append('\n### Policy Effectiveness (7d)')
                for policy, m in pm.items():
                    if m.get('error'):
                        continue
                    report_lines.append(
                        f'- **{policy}**: {m.get("action_count", 0)} actions, '
                        f'rollback rate {m.get("rollback_rate", 0):.0%}, '
                        f'verify pass {m.get("verification_pass_rate", 0):.0%}'
                    )

            return {
                'action': 'tuning_report',
                'report': '\n'.join(report_lines),
                'overrides': overrides,
                'recommendations': recs,
                'recent_changes': changes,
                'capped': evaluation.get('capped', False),
                'changes_today': evaluation.get('changes_today', 0),
            }

        elif action == 'budget_report':
            # Show current budget status, spend, and enforcement mode
            from core.services.ops_autopilot import BudgetController
            from django.utils import timezone as tz
            controller = BudgetController()
            try:
                report = controller.get_budget_report(tz.now())
            except Exception as e:
                return {
                    'action': 'budget_report',
                    'error': f'Budget report failed: {str(e)[:200]}',
                }

            report_lines = ['## Budget Report\n']
            report_lines.append(
                f'**Mode:** {report["mode"].upper()}'
            )
            report_lines.append(
                f'**Daily:** ${report["daily_spend"]:.2f} / '
                f'${report["daily_cap"]:.2f} '
                f'({report["daily_utilization"]:.0%}) — '
                f'{report["daily_calls"]} calls'
            )
            report_lines.append(
                f'**Hourly:** ${report["hourly_spend"]:.2f} / '
                f'${report["hourly_cap"]:.2f} '
                f'({report["hourly_utilization"]:.0%}) — '
                f'{report["hourly_calls"]} calls'
            )

            if report.get('top_agents'):
                report_lines.append('\n### Top Spenders (24h)')
                for a in report['top_agents']:
                    report_lines.append(
                        f'- **{a["agent_name"]}**: '
                        f'${a["total_cost"]:.4f} '
                        f'({a["call_count"]} calls)'
                    )

            if report.get('top_models'):
                report_lines.append('\n### Top Models (24h)')
                for m in report['top_models']:
                    report_lines.append(
                        f'- **{m["provider"]}/{m["model_id"]}**: '
                        f'${m["total_cost"]:.4f} '
                        f'({m["call_count"]} calls)'
                    )

            report_lines.append(
                f'\n**Soft limit:** {report["soft_limit_pct"]:.0%} '
                f'→ model downgrade'
            )
            report_lines.append(
                f'**Hard limit:** {report["hard_limit_pct"]:.0%} '
                f'→ freeze non-critical'
            )

            return {
                'action': 'budget_report',
                'report': '\n'.join(report_lines),
                **report,
            }

        elif action == 'roi_report':
            # Show ROI attribution per agent and active throttles
            from core.services.ops_autopilot import ROIEnforcer
            from django.utils import timezone as tz
            enforcer = ROIEnforcer()
            try:
                report = enforcer.get_roi_report(tz.now())
            except Exception as e:
                return {
                    'action': 'roi_report',
                    'error': f'ROI report failed: {str(e)[:200]}',
                }

            report_lines = ['## QROI Attribution Report\n']
            report_lines.append(
                f'**Window:** {report["window_hours"]}h — '
                f'**Total spend:** ${report["total_spend"]:.2f} — '
                f'**Outcomes:** {report["total_outcomes"]}'
            )
            report_lines.append(
                f'**Active throttles:** {report["active_throttles"]} — '
                f'**Budget pressure:** '
                f'{"YES" if report["budget_pressure"] else "No"}'
            )

            # Quality summary
            qs = report.get('quality_summary', {})
            if qs:
                report_lines.append(
                    f'**Avg quality weight:** {qs.get("avg_quality_weight", 0):.3f} — '
                    f'**Agents with quality data:** '
                    f'{qs.get("agents_with_quality_data", 0)}'
                    f'/{qs.get("total_agents", 0)}'
                )

            if report.get('agents'):
                report_lines.append('\n### Agent QROI (worst → best)')
                for a in report['agents'][:10]:
                    detail = a.get('outcome_detail', {})
                    report_lines.append(
                        f'- **{a["agent_name"]}**: '
                        f'QROI {a.get("qroi", a["roi"]):.1%} '
                        f'(ROI {a["roi"]:.1%} × '
                        f'Q {a.get("quality_weight", 0.5):.2f}) — '
                        f'${a["cost"]:.4f} / {a["calls"]} calls → '
                        f'{a["outcomes"]} outcomes '
                        f'(exec: {detail.get("executions", 0)}, '
                        f'content: {detail.get("content", 0)}, '
                        f'impacts: {detail.get("impacts", 0)})'
                    )

            if report.get('throttle_recommendations'):
                report_lines.append('\n### Throttle Recommendations (by QROI)')
                for r in report['throttle_recommendations'][:5]:
                    report_lines.append(
                        f'- **{r["agent_name"]}**: '
                        f'{r["cooldown_minutes"]}min cooldown — '
                        f'{r["reason"]}'
                    )

            return {
                'action': 'roi_report',
                'report': '\n'.join(report_lines),
                **report,
            }

        elif action == 'scheduler_report':
            # Show budget-aware scheduling state
            from core.services.ops_autopilot import BudgetAwareScheduler
            from django.utils import timezone as tz
            scheduler = BudgetAwareScheduler()
            try:
                report = scheduler.get_scheduler_report(tz.now())
            except Exception as e:
                return {
                    'action': 'scheduler_report',
                    'error': f'Scheduler report failed: {str(e)[:200]}',
                }

            report_lines = ['## Budget-Aware Scheduler Report\n']
            report_lines.append(
                f'**Budget:** {report["budget_pct"]:.0%} — '
                f'**Pressure:** {report["pressure"].upper()}'
            )
            report_lines.append(
                f'**Last 24h:** {report["defers_24h"]} deferred, '
                f'{report["downscopes_24h"]} downscoped'
            )
            report_lines.append(
                f'**Task tiers:** '
                f'Tier 1 (cheap): {report["tier_counts"].get(1, 0)}, '
                f'Tier 2 (moderate): {report["tier_counts"].get(2, 0)}, '
                f'Tier 3 (expensive): {report["tier_counts"].get(3, 0)}'
            )
            report_lines.append(
                f'**Deferable tasks:** {report["deferable_tasks"]} — '
                f'**Downscope-capable:** {report["downscope_tasks"]}'
            )

            if report.get('active_overrides'):
                report_lines.append('\n### Active Knob Overrides')
                for key, val in report['active_overrides'].items():
                    report_lines.append(f'- {key}: {val}')

            return {
                'action': 'scheduler_report',
                'report': '\n'.join(report_lines),
                **report,
            }

        elif action == 'portfolio_report':
            # Show IQROI per desk and portfolio allocations
            from core.services.ops_autopilot import PortfolioAllocator
            from django.utils import timezone as tz
            allocator = PortfolioAllocator()
            try:
                report = allocator.get_portfolio_report(tz.now())
            except Exception as e:
                return {
                    'action': 'portfolio_report',
                    'error': f'Portfolio report failed: {str(e)[:200]}',
                }

            report_lines = ['## Portfolio Allocation Report\n']
            report_lines.append(
                f'**Window:** {report["window_hours"]}h — '
                f'**Total impact:** ${report["total_impact_usd"]:.2f} — '
                f'**Total cost:** ${report["total_cost_usd"]:.2f} — '
                f'**Events:** {report["total_events"]}'
            )

            if report.get('desks'):
                report_lines.append('\n### Desk IQROI (best → worst)')
                for desk, data in report['desks'].items():
                    report_lines.append(
                        f'- **{desk}**: '
                        f'IQROI {data["iqroi"]:.2f} — '
                        f'allocation {data["allocation"]}x — '
                        f'${data["impact_usd"]:.2f} impact + '
                        f'{data["impact_points"]} pts / '
                        f'${data["cost_usd"]:.4f} cost — '
                        f'{data["events"]} events'
                    )

            if report.get('active_allocations'):
                report_lines.append('\n### Active Allocations')
                for desk, alloc in report['active_allocations'].items():
                    report_lines.append(
                        f'- **{desk}**: '
                        f'{alloc.get("allocation", 1.0)}x '
                        f'(IQROI {alloc.get("iqroi", 0):.2f})'
                    )

            return {
                'action': 'portfolio_report',
                'report': '\n'.join(report_lines),
                **report,
            }

        elif action == 'backfill_impacts':
            # Backfill ImpactEvents from historical wagers, deliverables, revenue
            from core.services.ops_autopilot import ImpactCollector
            days = payload.get('days', 14)
            days = min(max(int(days), 1), 90)  # Clamp 1-90

            collector = ImpactCollector()
            try:
                result = collector.backfill(days=days)
            except Exception as e:
                return {
                    'action': 'backfill_impacts',
                    'error': f'Backfill failed: {str(e)[:200]}',
                }

            return {
                'action': 'backfill_impacts',
                'message': (
                    f"Backfilled {result['total_created']} impact events "
                    f"over {days} days: "
                    f"{result['wagers']} wagers, "
                    f"{result['deliverable_events']} deliverable events, "
                    f"{result['revenues']} revenues"
                ),
                **result,
            }

        elif action == 'attribution_debt_report':
            # Show attribution debt metrics — unattributed LLM spend
            from core.services.ops_autopilot import AttributionDebtController
            from django.utils import timezone as tz

            ctrl = AttributionDebtController()
            try:
                report = ctrl.get_debt_report(tz.now())
            except Exception as e:
                return {
                    'action': 'attribution_debt_report',
                    'error': f'Debt report failed: {str(e)[:200]}',
                }

            d24 = report['last_24h']
            d72 = report['last_72h']
            lines = [
                '## Attribution Debt Report\n',
                f'**Status:** {report["status"].upper()} — '
                f'**Mapped agents:** {report["mapped_agents"]} — '
                f'**Reallocation:** '
                f'{"BLOCKED" if report["reallocation_blocked"] else "allowed"} — '
                f'**Smoothing α:** {report["smoothing_alpha"]}',
                f'\n### Last 24h',
                f'- Total spend: ${d24["total_spend"]:.2f}',
                f'- Attributed: ${d24["attributed_spend"]:.2f}',
                f'- **Unattributed (debt): ${d24["unattributed_spend"]:.2f} '
                f'({d24["debt_pct"]:.1f}%)**',
            ]

            if d24.get('desk_breakdown'):
                lines.append('\n**Desk breakdown (attributed):**')
                for desk, cost in d24['desk_breakdown'].items():
                    lines.append(f'  - {desk}: ${cost:.4f}')

            if d24.get('top_unattributed'):
                lines.append('\n**Top unattributed agents:**')
                for u in d24['top_unattributed'][:10]:
                    lines.append(
                        f'  - {u["agent"]}: ${u["cost_usd"]:.4f}'
                    )

            lines.append(f'\n### Last 72h')
            lines.append(
                f'- Total: ${d72["total_spend"]:.2f} — '
                f'Debt: ${d72["unattributed_spend"]:.2f} '
                f'({d72["debt_pct"]:.1f}%)'
            )

            lines.append(
                f'\n### Thresholds'
                f'\n- Warning: {report["thresholds"]["warning_pct"]}%'
                f'\n- Critical (blocks reallocation): '
                f'{report["thresholds"]["critical_pct"]}%'
                f'\n- USD floor: ${report["thresholds"]["usd_floor"]}'
            )

            return {
                'action': 'attribution_debt_report',
                'report': '\n'.join(lines),
                **report,
            }

        elif action == 'experiment_report':
            # Show active and recent experiments
            from core.services.ops_autopilot import ExperimentEngine
            from django.utils import timezone as tz

            engine = ExperimentEngine()
            try:
                report = engine.get_experiments_report(tz.now())
            except Exception as e:
                return {
                    'action': 'experiment_report',
                    'error': f'Report failed: {str(e)[:200]}',
                }

            lines = ['## Experiment Engine Report\n']
            lines.append(
                f'**Supported policies:** '
                f'{", ".join(report["supported_policies"])}'
            )
            lines.append(
                f'**Supported metrics:** '
                f'{", ".join(report["supported_metrics"])}'
            )

            if report['active_experiments']:
                lines.append('\n### Active Experiments')
                for exp in report['active_experiments']:
                    lines.append(
                        f'- **{exp["policy_name"]}**: '
                        f'{exp.get("description", "")[:80]} '
                        f'(metric: {exp["success_metric"]}, '
                        f'started: {exp.get("started_at", "N/A")})'
                    )
            else:
                lines.append('\n*No active experiments.*')

            if report['recent_decisions']:
                lines.append('\n### Recent Decisions')
                for exp in report['recent_decisions']:
                    lines.append(
                        f'- {exp["policy_name"]}: '
                        f'**{exp["status"]}** — '
                        f'{exp.get("decision_reason", "")[:100]}'
                    )

            return {
                'action': 'experiment_report',
                'report': '\n'.join(lines),
                **report,
            }

        elif action == 'experiment_create':
            # Create a new experiment
            from core.services.ops_autopilot import ExperimentEngine

            policy = payload.get('policy_name', '')
            treatment = payload.get('treatment_params', {})
            metric = payload.get('success_metric', 'avg_desk_iqroi')
            desc = payload.get('description', '')

            if not policy or not treatment:
                return {
                    'action': 'experiment_create',
                    'error': (
                        'Required: policy_name and treatment_params. '
                        'Example: policy_name="portfolio_allocator", '
                        'treatment_params={"ALLOCATION_CEILING": 2.0}'
                    ),
                }

            engine = ExperimentEngine()
            result = engine.create_experiment(
                policy_name=policy,
                treatment_params=treatment,
                success_metric=metric,
                description=desc,
                created_by='PA',
            )
            return {'action': 'experiment_create', **result}

        elif action == 'experiment_start':
            # Start a draft experiment
            from core.services.ops_autopilot import ExperimentEngine

            exp_id = payload.get('experiment_id', '')
            if not exp_id:
                return {
                    'action': 'experiment_start',
                    'error': 'Required: experiment_id',
                }

            engine = ExperimentEngine()
            result = engine.start_experiment(exp_id)
            return {'action': 'experiment_start', **result}

        elif action == 'decision_ledger_report':
            # Query decision ledger entries
            from core.models_decision_ledger import DecisionLedgerEntry

            policy_filter = payload.get('policy_name', '')
            decision_filter = payload.get('decision_type', '')
            days = int(payload.get('days', 1))
            limit = min(int(payload.get('limit', 50)), 200)

            cutoff = timezone.now() - timedelta(days=days)
            qs = DecisionLedgerEntry.objects.filter(cycle_ts__gte=cutoff)

            if policy_filter:
                qs = qs.filter(policy=policy_filter)
            if decision_filter:
                qs = qs.filter(decision_type=decision_filter)

            entries = list(
                qs.order_by('-cycle_ts').values(
                    'cycle_id', 'cycle_ts', 'policy', 'decision_type',
                    'decision_summary', 'duration_ms', 'experiment_id',
                )[:limit]
            )

            # Serialize
            for e in entries:
                for k, v in e.items():
                    if hasattr(v, 'isoformat'):
                        e[k] = v.isoformat()
                    elif hasattr(v, 'hex'):
                        e[k] = str(v)

            # Summary stats
            from django.db.models import Count, Avg
            stats = dict(
                qs.values('decision_type').annotate(
                    count=Count('id'),
                    avg_ms=Avg('duration_ms'),
                ).values_list('decision_type', 'count')
            )

            # Distinct cycles
            cycle_count = qs.values('cycle_id').distinct().count()

            return {
                'action': 'decision_ledger_report',
                'period_days': days,
                'total_entries': len(entries),
                'cycles': cycle_count,
                'decision_type_counts': stats,
                'entries': entries,
            }

        elif action == 'timeout_ladder_report':
            # Show agents currently on the timeout remediation ladder
            from core.services.ops_autopilot import TimeoutRemediationPlaybook

            playbook = TimeoutRemediationPlaybook()
            report = playbook.get_ladder_report()

            # Add recent ladder actions
            recent_actions = list(
                AutopilotAction.objects.filter(
                    policy='timeout_remediation_playbook',
                ).order_by('-created_at').values(
                    'agent_name', 'action_type', 'evidence', 'created_at',
                )[:10]
            )
            for a in recent_actions:
                if hasattr(a['created_at'], 'isoformat'):
                    a['created_at'] = a['created_at'].isoformat()

            return {
                'action': 'timeout_ladder_report',
                **report,
                'recent_actions': recent_actions,
            }

        elif action == 'deliberation_pipeline_report':
            # Show deliberation pipeline health + remediation ladder state
            from core.services.ops_autopilot import DeliberationRemediationPlaybook

            playbook = DeliberationRemediationPlaybook()
            report = playbook.get_pipeline_report(timezone.now())
            return {
                'action': 'deliberation_pipeline_report',
                **report,
            }

        elif action == 'backlog_report':
            # Show deliverable backlog health + governor state
            from core.services.ops_autopilot import BacklogGovernor

            governor = BacklogGovernor()
            report = governor.get_backlog_report(timezone.now())
            return {
                'action': 'backlog_report',
                **report,
            }

        elif action == 'goal_report':
            # Show goal-aware allocation state — weights, metrics, desk scores
            from core.services.ops_autopilot import GoalAwareAllocator

            allocator = GoalAwareAllocator()
            report = allocator.get_goal_report(timezone.now())
            return {
                'action': 'goal_report',
                **report,
            }

        elif action == 'goal_set_weights':
            # Update goal objective weights
            from core.services.ops_autopilot import GoalAwareAllocator

            goal_weights = payload.get('goal_weights')
            if not goal_weights or not isinstance(goal_weights, dict):
                return {
                    'action': 'goal_set_weights',
                    'error': 'goal_weights dict required (e.g., {"sports_profit": 0.3, "confirmed_revenue": 0.3, ...})',
                }

            allocator = GoalAwareAllocator()
            result = allocator.set_weights(goal_weights)
            return {
                'action': 'goal_set_weights',
                **result,
            }

        elif action == 'attribution_report':
            # Multi-touch attribution report across desks
            from django.utils import timezone as tz
            from core.services.ops_autopilot import MultiTouchAttributor

            attributor = MultiTouchAttributor()
            report = attributor.get_attribution_report(tz.now())
            return {
                'action': 'attribution_report',
                **report,
            }

        elif action == 'policy_conflict_report':
            # Policy arbitrator conflict detection
            from django.utils import timezone as tz
            from core.services.ops_autopilot import PolicyArbitrator

            arbitrator = PolicyArbitrator()
            report = arbitrator.get_conflict_report(
                tz.now(),
                knob=payload.get('knob', ''),
                policy=payload.get('policy_filter', ''),
            )
            return {
                'action': 'policy_conflict_report',
                **report,
            }

        elif action == 'release_report':
            # Deploy/release status report
            from django.utils import timezone as tz
            from core.services.ops_autopilot import ReleaseGovernor

            governor = ReleaseGovernor()
            report = governor.get_release_report(tz.now())
            return {
                'action': 'release_report',
                **report,
            }

        elif action == 'release_freeze':
            # Manually freeze deploys
            from core.services.ops_autopilot import ReleaseGovernor

            governor = ReleaseGovernor()
            result = governor.set_freeze(True, reason='manual PA freeze')
            return {
                'action': 'release_freeze',
                **result,
            }

        elif action == 'release_unfreeze':
            # Manually unfreeze deploys
            from core.services.ops_autopilot import ReleaseGovernor

            governor = ReleaseGovernor()
            result = governor.set_freeze(False, reason='manual PA unfreeze')
            return {
                'action': 'release_unfreeze',
                **result,
            }

        elif action == 'revenue_pipeline_report':
            # Revenue pipeline health report
            from django.utils import timezone as tz
            from core.services.ops_autopilot import RevenuePipelineAutomator

            automator = RevenuePipelineAutomator()
            report = automator.get_pipeline_report(tz.now())
            return {
                'action': 'revenue_pipeline_report',
                **report,
            }

        elif action == 'prospecting_queue':
            # Outbound lead engine — top scored leads
            from django.utils import timezone as tz
            from core.services.ops_autopilot import OutboundLeadEngine

            engine = OutboundLeadEngine()
            report = engine.get_prospecting_queue(tz.now())
            return {'action': 'prospecting_queue', **report}

        elif action == 'lead_source_report':
            # Which spider sources produce leads
            from django.utils import timezone as tz
            from core.services.ops_autopilot import OutboundLeadEngine

            engine = OutboundLeadEngine()
            report = engine.get_lead_source_report(tz.now())
            return {'action': 'lead_source_report', **report}

        elif action == 'outreach_inbox':
            # Outreach drafts pending approval
            from core.services.ops_autopilot import OutreachSequencer
            from django.utils import timezone as tz

            sequencer = OutreachSequencer()
            report = sequencer.get_inbox(tz.now())
            return {'action': 'outreach_inbox', **report}

        elif action == 'outreach_approve':
            # Approve a draft for sending
            from core.services.ops_autopilot import OutreachSequencer

            draft_id = payload.get('draft_id', '')
            edited_text = payload.get('edited_text', '')
            if not draft_id:
                return {'error': 'draft_id is required'}
            sequencer = OutreachSequencer()
            result = sequencer.approve_draft(draft_id, edited_text)
            return {'action': 'outreach_approve', **result}

        elif action == 'outreach_reject':
            # Reject a draft
            from core.services.ops_autopilot import OutreachSequencer

            draft_id = payload.get('draft_id', '')
            reason = payload.get('reason', '')
            if not draft_id:
                return {'error': 'draft_id is required'}
            sequencer = OutreachSequencer()
            result = sequencer.reject_draft(draft_id, reason)
            return {'action': 'outreach_reject', **result}

        elif action == 'outreach_metrics_report':
            # Outreach conversion funnel
            from core.services.ops_autopilot import OutreachSequencer
            from django.utils import timezone as tz

            sequencer = OutreachSequencer()
            report = sequencer.get_metrics_report(tz.now())
            return {'action': 'outreach_metrics_report', **report}

        elif action == 'close_pack_generate':
            # Generate a close pack (proposal + contract + invoice)
            from core.services.ops_autopilot import CloseTheDealEngine

            opportunity_id = payload.get('opportunity_id', '')
            offer_key = payload.get('offer_key', 'consulting')
            price = payload.get('price')
            timeline_days = payload.get('timeline_days', 14)

            if not price:
                return {'error': 'price is required for close_pack_generate'}

            engine = CloseTheDealEngine()
            result = engine.generate_pack(
                opportunity_id=opportunity_id,
                offer_key=offer_key,
                price=float(price),
                timeline_days=int(timeline_days),
            )
            return {'action': 'close_pack_generate', **result}

        elif action == 'close_pack_inbox':
            # Pending close packs for approval
            from core.services.ops_autopilot import CloseTheDealEngine
            from django.utils import timezone as tz

            engine = CloseTheDealEngine()
            inbox = engine.get_inbox(tz.now())
            return {'action': 'close_pack_inbox', **inbox}

        elif action == 'close_pack_approve':
            # Approve a close pack
            from core.services.ops_autopilot import CloseTheDealEngine

            pack_id = payload.get('pack_id')
            if not pack_id:
                return {'error': 'pack_id is required for close_pack_approve'}

            engine = CloseTheDealEngine()
            result = engine.approve_pack(pack_id)
            return {'action': 'close_pack_approve', **result}

        elif action == 'close_pack_metrics_report':
            # Deal metrics — win rate, revenue, etc.
            from core.services.ops_autopilot import CloseTheDealEngine
            from django.utils import timezone as tz

            engine = CloseTheDealEngine()
            report = engine.get_metrics_report(tz.now())
            return {'action': 'close_pack_metrics_report', **report}

        elif action == 'engagement_inbox':
            # Inbound engagement events
            from core.services.ops_autopilot import EngagementEngine
            from django.utils import timezone as tz

            status_filter = payload.get('status_filter', 'unread')
            engine = EngagementEngine()
            inbox = engine.get_inbox(tz.now(), status_filter=status_filter)
            return {'action': 'engagement_inbox', **inbox}

        elif action == 'engagement_classify':
            # Classify engagement intent
            from core.services.ops_autopilot import EngagementEngine

            event_id = payload.get('event_id')
            intent = payload.get('intent')
            if not event_id or not intent:
                return {'error': 'event_id and intent are required'}

            engine = EngagementEngine()
            result = engine.classify_event(
                event_id=event_id,
                intent=intent,
                summary=payload.get('summary', ''),
            )
            return {'action': 'engagement_classify', **result}

        elif action == 'engagement_draft_reply':
            # Draft a reply for approval
            from core.services.ops_autopilot import EngagementEngine

            event_id = payload.get('event_id')
            reply_text = payload.get('reply_text')
            if not event_id or not reply_text:
                return {'error': 'event_id and reply_text are required'}

            engine = EngagementEngine()
            result = engine.draft_reply(event_id=event_id, reply_text=reply_text)
            return {'action': 'engagement_draft_reply', **result}

        elif action == 'engagement_approve_reply':
            # Approve a draft reply
            from core.services.ops_autopilot import EngagementEngine

            event_id = payload.get('event_id')
            if not event_id:
                return {'error': 'event_id is required'}

            engine = EngagementEngine()
            result = engine.approve_reply(
                event_id=event_id,
                edited_text=payload.get('edited_text', ''),
            )
            return {'action': 'engagement_approve_reply', **result}

        elif action == 'engagement_disqualify':
            # Disqualify an engagement
            from core.services.ops_autopilot import EngagementEngine

            event_id = payload.get('event_id')
            if not event_id:
                return {'error': 'event_id is required'}

            engine = EngagementEngine()
            result = engine.disqualify(
                event_id=event_id,
                reason=payload.get('reason', ''),
            )
            return {'action': 'engagement_disqualify', **result}

        elif action == 'engagement_metrics_report':
            # Engagement funnel metrics
            from core.services.ops_autopilot import EngagementEngine
            from django.utils import timezone as tz

            engine = EngagementEngine()
            report = engine.get_metrics_report(tz.now())
            return {'action': 'engagement_metrics_report', **report}

        elif action == 'meeting_create':
            # Create a new meeting
            from core.services.ops_autopilot import MeetingEngine

            scheduled_at = payload.get('scheduled_at')
            if not scheduled_at:
                return {'error': 'scheduled_at is required (ISO datetime)'}

            engine = MeetingEngine()
            result = engine.create_meeting(
                opportunity_id=payload.get('opportunity_id', ''),
                scheduled_at=scheduled_at,
                title=payload.get('title', ''),
                channel=payload.get('channel', 'zoom'),
                duration_minutes=int(payload.get('duration_minutes', 30)),
                meeting_link=payload.get('meeting_link', ''),
                prospect_name=payload.get('prospect_name', ''),
                prospect_company=payload.get('prospect_company', ''),
            )
            return {'action': 'meeting_create', **result}

        elif action == 'meeting_inbox':
            # Meeting inbox by filter
            from core.services.ops_autopilot import MeetingEngine
            from django.utils import timezone as tz

            filter_type = payload.get('filter_type', 'upcoming')
            engine = MeetingEngine()
            inbox = engine.get_inbox(tz.now(), filter_type=filter_type)
            return {'action': 'meeting_inbox', **inbox}

        elif action == 'meeting_brief':
            # Generate pre-call brief
            from core.services.ops_autopilot import MeetingEngine

            meeting_id = payload.get('meeting_id')
            if not meeting_id:
                return {'error': 'meeting_id is required'}

            engine = MeetingEngine()
            result = engine.generate_brief(meeting_id=meeting_id)
            return {'action': 'meeting_brief', **result}

        elif action == 'meeting_recap':
            # Add post-meeting recap
            from core.services.ops_autopilot import MeetingEngine

            meeting_id = payload.get('meeting_id')
            if not meeting_id:
                return {'error': 'meeting_id is required'}

            engine = MeetingEngine()
            result = engine.add_recap(
                meeting_id=meeting_id,
                notes=payload.get('notes', ''),
                outcome=payload.get('outcome', ''),
                next_steps=payload.get('next_steps', ''),
            )
            return {'action': 'meeting_recap', **result}

        elif action == 'meeting_metrics_report':
            # Meeting pipeline metrics
            from core.services.ops_autopilot import MeetingEngine
            from django.utils import timezone as tz

            engine = MeetingEngine()
            report = engine.get_metrics_report(tz.now())
            return {'action': 'meeting_metrics_report', **report}

        # ── Governance & Safe-Mode Controls (Policy 30) ──

        elif action == 'governance_status':
            from core.services.ops_autopilot import GovernanceEngine

            engine = GovernanceEngine()
            status = engine.get_status()
            return {'action': 'governance_status', **status}

        elif action == 'governance_set_mode':
            from core.services.ops_autopilot import GovernanceEngine

            mode = payload.get('mode', '')
            if not mode:
                return {'error': 'mode is required (normal/throttle/freeze/safe_mode)'}

            engine = GovernanceEngine()
            result = engine.set_mode(
                mode=mode,
                reason=payload.get('reason', ''),
                scope=payload.get('scope', 'global'),
                scope_target=payload.get('scope_target', ''),
                ttl_hours=payload.get('ttl_hours'),
                set_by='pa_tool',
            )
            return {'action': 'governance_set_mode', **result}

        elif action == 'governance_kill_switch':
            from core.services.ops_autopilot import GovernanceEngine

            target = payload.get('target', '')
            if not target:
                return {'error': 'target is required (scheduler/queue/agent_family/publishing/outbound/deploys)'}

            engine = GovernanceEngine()
            result = engine.activate_kill_switch(
                target=target,
                reason=payload.get('reason', ''),
                target_detail=payload.get('target_detail', ''),
                ttl_hours=payload.get('ttl_hours'),
                activated_by='pa_tool',
            )
            return {'action': 'governance_kill_switch', **result}

        elif action == 'governance_deactivate_switch':
            from core.services.ops_autopilot import GovernanceEngine

            switch_id = payload.get('switch_id', '')
            if not switch_id:
                return {'error': 'switch_id is required'}

            engine = GovernanceEngine()
            result = engine.deactivate_kill_switch(switch_id)
            return {'action': 'governance_deactivate_switch', **result}

        elif action == 'governance_throttle_report':
            from core.services.ops_autopilot import GovernanceEngine

            engine = GovernanceEngine()
            report = engine.get_throttle_report()
            return {'action': 'governance_throttle_report', **report}

        elif action == 'governance_audit':
            from core.services.ops_autopilot import GovernanceEngine

            engine = GovernanceEngine()
            audit = engine.get_audit_log(limit=payload.get('limit', 20))
            return {'action': 'governance_audit', **audit}

        # ── Revenue Pipeline Orchestrator (Policy 31) ──

        elif action == 'revenue_full_pipeline':
            from core.services.ops_autopilot import RevenueOrchestrator

            engine = RevenueOrchestrator()
            pipeline = engine.get_full_pipeline()
            return {'action': 'revenue_full_pipeline', **pipeline}

        elif action == 'revenue_funnel':
            from core.services.ops_autopilot import RevenueOrchestrator

            days = int(payload.get('days', 30))
            engine = RevenueOrchestrator()
            funnel = engine.get_conversion_funnel(days=days)
            return {'action': 'revenue_funnel', **funnel}

        elif action == 'revenue_forecast':
            from core.services.ops_autopilot import RevenueOrchestrator

            engine = RevenueOrchestrator()
            forecast = engine.get_revenue_forecast()
            return {'action': 'revenue_forecast', **forecast}

        # ── Knowledge & Citation Engine (Policy 32) ──────────────
        elif action == 'knowledge_health':
            from core.services.ops_autopilot import KnowledgeEngine

            engine = KnowledgeEngine()
            health = engine.get_health()
            return {'action': 'knowledge_health', **health}

        elif action == 'knowledge_citation_report':
            from core.services.ops_autopilot import KnowledgeEngine

            days = int(payload.get('days', 7))
            engine = KnowledgeEngine()
            report = engine.get_citation_report(days=days)
            return {'action': 'knowledge_citation_report', **report}

        elif action == 'knowledge_source_report':
            from core.services.ops_autopilot import KnowledgeEngine

            engine = KnowledgeEngine()
            report = engine.get_source_report()
            return {'action': 'knowledge_source_report', **report}

        elif action == 'knowledge_staleness_report':
            from core.services.ops_autopilot import KnowledgeEngine

            engine = KnowledgeEngine()
            report = engine.get_staleness_report()
            return {'action': 'knowledge_staleness_report', **report}

        # ── Close Pack Autonomy (Policy 33) ──────────────────────
        elif action == 'close_pack_followup_queue':
            from core.services.ops_autopilot import ClosePackAutonomyEngine

            engine = ClosePackAutonomyEngine()
            queue = engine.get_followup_queue()
            return {'action': 'close_pack_followup_queue', **queue}

        elif action == 'close_pack_risk_report':
            from core.services.ops_autopilot import ClosePackAutonomyEngine

            engine = ClosePackAutonomyEngine()
            report = engine.get_risk_report()
            return {'action': 'close_pack_risk_report', **report}

        elif action == 'close_pack_velocity':
            from core.services.ops_autopilot import ClosePackAutonomyEngine

            engine = ClosePackAutonomyEngine()
            report = engine.get_velocity_report()
            return {'action': 'close_pack_velocity', **report}

        # ── Engagement Autonomy (Policy 34) ──────────────────────
        elif action == 'engagement_sla_queue':
            from core.services.ops_autopilot import EngagementAutonomyEngine

            engine = EngagementAutonomyEngine()
            queue = engine.get_sla_queue()
            return {'action': 'engagement_sla_queue', **queue}

        elif action == 'engagement_meeting_suggestions':
            from core.services.ops_autopilot import EngagementAutonomyEngine

            engine = EngagementAutonomyEngine()
            suggestions = engine.get_meeting_suggestions()
            return {'action': 'engagement_meeting_suggestions', **suggestions}

        elif action == 'engagement_conversion_report':
            from core.services.ops_autopilot import EngagementAutonomyEngine

            days = int(payload.get('days', 30))
            engine = EngagementAutonomyEngine()
            report = engine.get_conversion_report(days=days)
            return {'action': 'engagement_conversion_report', **report}

        # ── Growth & Distribution (Policy 35) ──
        elif action == 'growth_candidates':
            from core.services.ops_autopilot import GrowthEngine

            limit = int(payload.get('limit', 20))
            engine = GrowthEngine()
            candidates = engine.get_candidates(limit=limit)
            return {'action': 'growth_candidates', **candidates}

        elif action == 'growth_schedule':
            from core.services.ops_autopilot import GrowthEngine

            days = int(payload.get('days', 7))
            engine = GrowthEngine()
            schedule = engine.get_schedule(days=days)
            return {'action': 'growth_schedule', **schedule}

        elif action == 'growth_channel_report':
            from core.services.ops_autopilot import GrowthEngine

            engine = GrowthEngine()
            report = engine.get_channel_report()
            return {'action': 'growth_channel_report', **report}

        elif action == 'growth_funnel':
            from core.services.ops_autopilot import GrowthEngine

            days = int(payload.get('days', 30))
            engine = GrowthEngine()
            funnel = engine.get_funnel(days=days)
            return {'action': 'growth_funnel', **funnel}

        # ── Capacity Planning (Policy 36) ──
        elif action == 'capacity_forecast':
            from core.services.ops_autopilot import CapacityEngine

            hours = int(payload.get('hours', 24))
            engine = CapacityEngine()
            forecast = engine.get_capacity_forecast(hours=hours)
            return {'action': 'capacity_forecast', **forecast}

        elif action == 'capacity_bottleneck_report':
            from core.services.ops_autopilot import CapacityEngine

            hours = int(payload.get('hours', 24))
            engine = CapacityEngine()
            report = engine.get_bottleneck_report(hours=hours)
            return {'action': 'capacity_bottleneck_report', **report}

        elif action == 'capacity_throttle_plan':
            from core.services.ops_autopilot import CapacityEngine

            engine = CapacityEngine()
            plan = engine.get_throttle_plan()
            return {'action': 'capacity_throttle_plan', **plan}

        elif action == 'capacity_budget_envelope':
            from core.services.ops_autopilot import CapacityEngine

            days = int(payload.get('days', 7))
            engine = CapacityEngine()
            envelope = engine.get_budget_envelope(days=days)
            return {'action': 'capacity_budget_envelope', **envelope}

        # ── Security & Abuse (Policy 37) ──
        elif action == 'security_permission_drift':
            from core.services.ops_autopilot import SecurityEngine

            hours = int(payload.get('hours', 24))
            engine = SecurityEngine()
            report = engine.get_permission_drift_report(hours=hours)
            return {'action': 'security_permission_drift', **report}

        elif action == 'security_abuse_queue':
            from core.services.ops_autopilot import SecurityEngine

            hours = int(payload.get('hours', 24))
            limit = int(payload.get('limit', 50))
            engine = SecurityEngine()
            queue = engine.get_abuse_risk_queue(hours=hours, limit=limit)
            return {'action': 'security_abuse_queue', **queue}

        elif action == 'security_containment_plan':
            from core.services.ops_autopilot import SecurityEngine

            dry_run = payload.get('dry_run', True)
            engine = SecurityEngine()
            plan = engine.get_containment_plan(dry_run=dry_run)
            return {'action': 'security_containment_plan', **plan}

        elif action == 'security_secrets_scan':
            from core.services.ops_autopilot import SecurityEngine

            days = int(payload.get('days', 7))
            engine = SecurityEngine()
            scan = engine.get_secrets_scan(days=days)
            return {'action': 'security_secrets_scan', **scan}

        elif action == 'compliance_pii_scan':
            from core.services.ops_autopilot import ComplianceEngine

            days = int(payload.get('days', 7))
            limit = int(payload.get('limit', 50))
            engine = ComplianceEngine()
            scan = engine.get_pii_scan(days=days, limit=limit)
            return {'action': 'compliance_pii_scan', **scan}

        elif action == 'compliance_retention_report':
            from core.services.ops_autopilot import ComplianceEngine

            engine = ComplianceEngine()
            report = engine.get_retention_report()
            return {'action': 'compliance_retention_report', **report}

        elif action == 'compliance_access_audit':
            from core.services.ops_autopilot import ComplianceEngine

            hours = int(payload.get('hours', 24))
            engine = ComplianceEngine()
            audit = engine.get_access_audit(hours=hours)
            return {'action': 'compliance_access_audit', **audit}

        elif action == 'compliance_report':
            from core.services.ops_autopilot import ComplianceEngine

            engine = ComplianceEngine()
            report = engine.get_compliance_report()
            return {'action': 'compliance_report', **report}

        elif action == 'integrity_quality_report':
            from core.services.ops_autopilot import DataIntegrityEngine

            hours = int(payload.get('hours', 24))
            engine = DataIntegrityEngine()
            report = engine.get_quality_report(hours=hours)
            return {'action': 'integrity_quality_report', **report}

        elif action == 'integrity_null_spike_scan':
            from core.services.ops_autopilot import DataIntegrityEngine

            hours = int(payload.get('hours', 24))
            engine = DataIntegrityEngine()
            scan = engine.get_null_spike_scan(hours=hours)
            return {'action': 'integrity_null_spike_scan', **scan}

        elif action == 'integrity_duplicate_report':
            from core.services.ops_autopilot import DataIntegrityEngine

            hours = int(payload.get('hours', 24))
            engine = DataIntegrityEngine()
            report = engine.get_duplicate_report(hours=hours)
            return {'action': 'integrity_duplicate_report', **report}

        elif action == 'integrity_reliability_scores':
            from core.services.ops_autopilot import DataIntegrityEngine

            engine = DataIntegrityEngine()
            scores = engine.get_reliability_scores()
            return {'action': 'integrity_reliability_scores', **scores}

        elif action == 'value_events_report':
            from core.services.ops_autopilot import ValueRealizationEngine

            days = int(payload.get('days', 7))
            engine = ValueRealizationEngine()
            report = engine.get_value_events_report(days=days)
            return {'action': 'value_events_report', **report}

        elif action == 'value_outcome_rates':
            from core.services.ops_autopilot import ValueRealizationEngine

            days = int(payload.get('days', 30))
            engine = ValueRealizationEngine()
            rates = engine.get_outcome_rates(days=days)
            return {'action': 'value_outcome_rates', **rates}

        elif action == 'value_usage_gaps':
            from core.services.ops_autopilot import ValueRealizationEngine

            days = int(payload.get('days', 7))
            engine = ValueRealizationEngine()
            gaps = engine.get_usage_gaps(days=days)
            return {'action': 'value_usage_gaps', **gaps}

        elif action == 'value_realization_summary':
            from core.services.ops_autopilot import ValueRealizationEngine

            engine = ValueRealizationEngine()
            summary = engine.get_realization_summary()
            return {'action': 'value_realization_summary', **summary}

        elif action == 'backfill_failure_reasons':
            # Re-classify sessions that have UNKNOWN or empty failure_reason_code
            from core.models_deliberation import DeliberationSession, classify_failure_reason
            from django.db.models import Q

            sessions = DeliberationSession.objects.filter(
                status='failed',
            ).filter(
                Q(failure_reason_code='') | Q(failure_reason_code='UNKNOWN')
            )
            updated = 0
            for s in sessions:
                detail = getattr(s, 'failure_detail', '') or ''
                if not detail:
                    continue
                new_code = classify_failure_reason(detail)
                if new_code != 'UNKNOWN':
                    s.failure_reason_code = new_code
                    s.save(update_fields=['failure_reason_code'])
                    updated += 1

            return {
                'action': 'backfill_failure_reasons',
                'scanned': sessions.count() + updated,  # approximate
                'reclassified': updated,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. "
                f"Valid: status, history, run, config, dry_run_report, drift_scan, "
                f"tuning_report, budget_report, roi_report, scheduler_report, "
                f"backfill_failure_reasons"
            )

    def _handle_ops_digest(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Autonomous ops digest — aggregates live system data into a
        structured summary that can be posted into a conversation.
        """
        from django.utils import timezone
        from datetime import timedelta
        from core.models_diagnostic_pipeline import AutopilotAction
        from core.models_unified_system import AgentControlEntry

        action = payload.get('action', 'generate')
        window = payload.get('window', '1h')
        now = timezone.now()

        window_map = {'10m': 10, '1h': 60, '6h': 360, '24h': 1440}
        window_minutes = window_map.get(window, 60)
        cutoff = now - timedelta(minutes=window_minutes)

        # ── Gather data ──────────────────────────────────────────────
        # Deploy SHA
        import os
        sha = os.environ.get('RAILWAY_GIT_COMMIT_SHA', '')
        if not sha:
            try:
                import subprocess
                sha = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD'],
                    stderr=subprocess.DEVNULL,
                ).decode().strip()[:12]
            except Exception:
                sha = 'unknown'
        sha = sha[:12]

        # Autopilot status
        autopilot_last = 'never'
        total_cycles = 0
        blocks_24h = 0
        try:
            last_cycle = AutopilotAction.objects.filter(
                policy='cycle_evaluation',
            ).first()
            autopilot_last = last_cycle.created_at.isoformat() if last_cycle else 'never'
            total_cycles = AutopilotAction.objects.filter(policy='cycle_evaluation').count()
            blocks_24h = AutopilotAction.objects.filter(
                action_type='block_agent', dry_run=False,
                created_at__gte=now - timedelta(hours=24),
            ).count()
        except Exception:
            pass

        # Blocked agents
        blocked_names = []
        try:
            blocked_names = sorted(AgentControlEntry.get_blocked_names())
        except Exception:
            pass

        # Recent activity (agent executions + celery tasks in window)
        agent_runs = 0
        task_events = 0
        task_failures = 0
        try:
            from core.models_unified_system import AgentExecution
            from core.models_celery_telemetry import CeleryTaskEvent
            agent_runs = AgentExecution.objects.filter(created_at__gte=cutoff).count()
            task_events = CeleryTaskEvent.objects.filter(started_at__gte=cutoff).count()
            task_failures = CeleryTaskEvent.objects.filter(
                started_at__gte=cutoff, status='FAILURE',
            ).count()
        except Exception:
            pass

        # Failure signatures (top 3 in window)
        top_failures = []
        try:
            from core.models_diagnostic_pipeline import FailureSignature
            from django.db.models import Count
            sigs = list(
                FailureSignature.objects.filter(
                    detections__detected_at__gte=cutoff,
                ).annotate(
                    hit_count=Count('detections'),
                ).order_by('-hit_count')[:3].values(
                    'category', 'pattern_hash', 'hit_count',
                )
            )
            top_failures = sigs
        except Exception:
            pass

        # ── Build digest ─────────────────────────────────────────────
        digest = {
            'timestamp': now.isoformat(),
            'window': window,
            'deploy_sha': sha,
            'autopilot': {
                'status': 'running',
                'last_cycle': autopilot_last,
                'total_cycles': total_cycles,
                'blocks_24h': blocks_24h,
            },
            'blocked_agents': blocked_names,
            'activity': {
                'agent_runs': agent_runs,
                'celery_tasks': task_events,
                'task_failures': task_failures,
            },
            'top_failures': top_failures,
        }

        # Render markdown
        fa_lines = []
        for f in top_failures:
            fa_lines.append(f"  - {f['category']}/{f['pattern_hash'][:8]}: {f['hit_count']} hits")

        md = (
            f"## Ops Digest — {now.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**SHA:** `{sha}` | **Window:** {window}\n\n"
            f"**Autopilot:** running (last cycle: {autopilot_last[:19]}Z) | "
            f"cycles: {total_cycles} | blocks 24h: {blocks_24h}\n\n"
            f"**Blocked agents:** {', '.join(blocked_names) if blocked_names else 'none'}\n\n"
            f"**Activity ({window}):** {agent_runs} agent runs, "
            f"{task_events} tasks, {task_failures} failures\n\n"
        )
        if fa_lines:
            md += "**Top failures:**\n" + '\n'.join(fa_lines) + "\n"
        else:
            md += "**Top failures:** none\n"

        digest['markdown'] = md

        if action == 'generate':
            return {'action': 'generate', 'digest': digest}

        elif action == 'post':
            conversation_id = payload.get('conversation_id')
            if not conversation_id:
                return {'error': 'conversation_id required for post action'}

            from core.models import ChatConversation
            from django.contrib.auth import get_user_model
            User = get_user_model()

            user = None
            if user_id:
                user = User.objects.filter(id=user_id).first()
            if not user:
                user = User.objects.filter(is_superuser=True).first()

            ChatConversation.objects.create(
                user=user,
                conversation_id=conversation_id,
                user_message='[Autonomous Ops Digest]',
                assistant_response=md,
                platform='api',
                source='ops_digest',
                metadata={'digest': digest, 'trace_id': trace_id},
            )

            return {
                'action': 'post',
                'conversation_id': conversation_id,
                'posted_at': now.isoformat(),
                'digest': digest,
            }

        return {'error': f'Unknown action: {action}'}

    def _ops_timeout_config_read(self, agent_names: list, trace_id: str) -> Dict[str, Any]:
        """
        Session 1098: Read agent wall-clock timeout config.
        Returns code defaults from _AGENT_TIMEOUT_SECONDS + any DB overrides
        from SystemConfiguration(key='agent_timeout_override:{name}').
        Strictly read-only.
        """
        from core.models.system import SystemConfiguration

        # Code defaults from tasks.py
        code_defaults = {
            'AudioAgent': 300, 'ImageAgent': 300, 'VideoAgent': 600,
            'ThreeDAgent': 300, 'ImageEditingAgent': 300, 'VideoEditingAgent': 600,
            'TalkingCharacterAgent': 600, 'ResolveAgent': 600,
            'ResearchAgent': 1500, 'SystemIntelligenceAgent': 600,
            'MarketingStrategyAgent': 600, 'CustomerResearchAgent': 1500,
            'CharacterTrainingAgent': 600, 'ContentWriterAgent': 600,
            'CompetitorAnalysisAgent': 600, 'BrandStrategyAgent': 600,
            'ContentStrategyAgent': 600, 'WhaleWatcherAgent': 1500,
            'StockAuditCoordinator': 900, 'WorkflowOrchestrationAgent': 900,
        }
        global_default = 1200  # 20 min fallback

        # Filter to requested agents (or show all if none specified)
        if agent_names:
            names = agent_names
        else:
            names = sorted(code_defaults.keys())

        # DB overrides
        override_keys = [f'agent_timeout_override:{n}' for n in names]
        db_overrides = dict(
            SystemConfiguration.objects.filter(
                key__in=override_keys,
            ).values_list('key', 'value')
        )

        agents = []
        for name in names:
            override_key = f'agent_timeout_override:{name}'
            db_val = db_overrides.get(override_key)
            code_val = code_defaults.get(name, global_default)
            effective = int(db_val) if db_val is not None else code_val
            agents.append({
                'agent_name': name,
                'code_default_seconds': code_val,
                'db_override_seconds': int(db_val) if db_val is not None else None,
                'effective_seconds': effective,
                'source': 'db_override' if db_val is not None else 'code_default',
            })

        return {
            'action': 'timeout_config_read',
            'agents': agents,
            'global_default_seconds': global_default,
            'watchdog_threshold_minutes': 35,
        }

    def _ops_proof_bundle(self, agent_names: list, initiative_id: str, trace_id: str) -> Dict[str, Any]:
        """
        Session 1098: Verification proof bundle — returns timeout config +
        agent control audit + initiative audit in one read-only call.
        Designed for "verification mode" where the user asks to confirm
        what changed and what's configured.
        """
        # Part A: Timeout config
        timeout_config = self._ops_timeout_config_read(agent_names, trace_id)

        # Part B: Agent control audit log (block/unblock history)
        audit_entries = []
        try:
            from core.models_unified_system import AgentControlEntry
            qs = AgentControlEntry.objects.all().order_by('-updated_at')
            if agent_names:
                qs = qs.filter(agent_name__in=agent_names)
            entries = list(qs[:30].values(
                'agent_name', 'status', 'reason', 'blocked_at',
                'blocked_by', 'ttl_hours', 'updated_at',
            ))
            for e in entries:
                for k in ('blocked_at', 'updated_at'):
                    if e.get(k):
                        e[k] = e[k].isoformat()
            audit_entries = entries
        except Exception as exc:
            audit_entries = [{'error': str(exc)}]

        # Part C: Initiative audit (if initiative_id provided)
        initiative_info = None
        if initiative_id:
            try:
                from core.models import Initiative
                from core.models_document_registry import InitiativeStage
                ini = Initiative.objects.filter(id=initiative_id).values(
                    'id', 'name', 'status', 'current_stage', 'created_at', 'updated_at',
                ).first()
                if ini:
                    for k in ('created_at', 'updated_at'):
                        if ini.get(k):
                            ini[k] = ini[k].isoformat()
                    ini['id'] = str(ini['id'])
                    stages = list(InitiativeStage.objects.filter(
                        initiative_id=initiative_id,
                    ).values(
                        'stage', 'status', 'created_at',
                    ).order_by('stage'))
                    for s in stages:
                        if s.get('created_at'):
                            s['created_at'] = s['created_at'].isoformat()
                    ini['stages'] = stages
                    initiative_info = ini
                else:
                    initiative_info = {'error': f'Initiative {initiative_id} not found'}
            except Exception as exc:
                initiative_info = {'error': str(exc)}

        return {
            'action': 'proof_bundle',
            'timeout_config': timeout_config['agents'],
            'global_default_seconds': timeout_config['global_default_seconds'],
            'watchdog_threshold_minutes': timeout_config['watchdog_threshold_minutes'],
            'agent_control_audit': audit_entries,
            'initiative': initiative_info,
            'note': 'Read-only verification bundle. No mutations performed.',
        }

    def _ops_tool_migration_report(self, window: str, trace_id: str) -> Dict[str, Any]:
        """
        Session 1079 Phase 2: Gateway migration telemetry report.

        Queries ToolCallRecord to show:
        - Legacy vs gateway tool call counts
        - Top legacy tools still being used
        - Deprecation readiness per legacy tool
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Max

        window_hours = {'6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 168)
        cutoff = timezone.now() - timedelta(hours=window_hours)

        try:
            from core.models_tool_calls import ToolCallRecord

            removed_names = set(self.REMOVED_TOOL_ALIASES.keys())
            gateway_names = self.GATEWAY_TOOLS

            # Total tool calls in window
            all_calls = ToolCallRecord.objects.filter(created_at__gte=cutoff)
            total = all_calls.count()

            # Count by tool name
            tool_counts = dict(
                all_calls.values('tool_name')
                .annotate(count=Count('id'), last_used=Max('created_at'))
                .order_by('-count')
                .values_list('tool_name', 'count')
            )

            # Classify
            removed_calls = []
            gateway_calls = []
            other_calls = []

            for tool_name, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
                entry = {'tool': tool_name, 'count': count}
                if tool_name in removed_names:
                    gw, suggested_action = self.REMOVED_TOOL_ALIASES[tool_name]
                    entry['suggested_gateway'] = gw
                    entry['suggested_action'] = suggested_action
                    removed_calls.append(entry)
                elif tool_name in gateway_names:
                    gateway_calls.append(entry)
                else:
                    other_calls.append(entry)

            removed_total = sum(e['count'] for e in removed_calls)
            gateway_total = sum(e['count'] for e in gateway_calls)

            # Split removed-tool calls into PA-originated vs agent-internal
            pa_removed = dict(
                all_calls.filter(tool_name__in=removed_names, agent_name='PersonalAssistant')
                .values('tool_name')
                .annotate(count=Count('id'))
                .values_list('tool_name', 'count')
            )
            pa_removed_total = sum(pa_removed.values())
            agent_removed_total = removed_total - pa_removed_total

            # Tools with 0 calls — fully silent
            silent_tools = [
                tool_name for tool_name in removed_names
                if tool_counts.get(tool_name, 0) == 0
            ]

            # Failure comparison: removed vs gateway success rates
            removed_failures = all_calls.filter(
                tool_name__in=removed_names, success=False
            ).count()
            gateway_failures = all_calls.filter(
                tool_name__in=gateway_names, success=False
            ).count()

            return {
                'action': 'tool_migration_report',
                'window': window,
                'generated_at': timezone.now().isoformat(),
                'summary': {
                    'total_tool_calls': total,
                    'removed_tool_calls': removed_total,
                    'pa_removed_calls': pa_removed_total,
                    'agent_removed_calls': agent_removed_total,
                    'gateway_calls': gateway_total,
                    'other_calls': total - removed_total - gateway_total,
                    'migration_pct': round(gateway_total / max(gateway_total + pa_removed_total, 1) * 100, 1),
                },
                'removed_tools_referenced': removed_calls[:15],
                'pa_removed_breakdown': [
                    {'tool': t, 'count': c, 'suggested_gateway': self.REMOVED_TOOL_ALIASES[t][0]}
                    for t, c in sorted(pa_removed.items(), key=lambda x: -x[1])
                ] if pa_removed else [],
                'gateway_tools': gateway_calls,
                'silent_removed_tools': sorted(silent_tools),
                'failure_comparison': {
                    'removed_failures': removed_failures,
                    'removed_failure_rate': round(removed_failures / max(removed_total, 1) * 100, 2),
                    'gateway_failures': gateway_failures,
                    'gateway_failure_rate': round(gateway_failures / max(gateway_total, 1) * 100, 2),
                },
                'recommendation': (
                    f'{len(silent_tools)} removed tools had zero calls in {window}. '
                    f'{len(removed_calls)} removed tools still referenced '
                    f'({pa_removed_total} PA-originated, {agent_removed_total} agent-internal).'
                    if removed_calls else
                    f'All {len(removed_names)} removed tools silent in {window}. '
                    f'Gateway adoption at {round(gateway_total / max(gateway_total + pa_removed_total, 1) * 100, 1)}%.'
                ),
            }
        except Exception as e:
            return {'action': 'tool_migration_report', 'error': str(e)}


    # ── Codebase introspection ─────────────────────────────────────────────

    def _handle_repo(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Read-only codebase introspection: tree, read_file, search, git_info."""
        import os
        import subprocess

        action = payload.get('action', 'tree')
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Security: block reading secrets
        BLOCKED_FILES = {'.env', '.env.local', '.env.production', 'credentials.json', 'secrets.yaml'}
        BLOCKED_DIRS = {'.git/objects', '.git/refs', 'node_modules', '.venv', '__pycache__'}

        def _safe_path(rel_path: str) -> str:
            """Resolve path and ensure it's within project root."""
            if not rel_path:
                return project_root
            full = os.path.normpath(os.path.join(project_root, rel_path))
            if not full.startswith(project_root):
                raise ValueError('Path outside project root')
            basename = os.path.basename(full)
            if basename in BLOCKED_FILES:
                raise ValueError(f'Access denied: {basename}')
            for bd in BLOCKED_DIRS:
                if bd in full:
                    raise ValueError(f'Access denied: {bd}')
            return full

        try:
            if action == 'tree':
                rel_path = payload.get('path', '')
                depth = min(payload.get('depth', 2), 4)
                full_path = _safe_path(rel_path)
                if not os.path.isdir(full_path):
                    return {'error': f'Not a directory: {rel_path}'}

                entries = []
                for root, dirs, files in os.walk(full_path):
                    # Calculate depth relative to full_path
                    rel = os.path.relpath(root, full_path)
                    level = 0 if rel == '.' else rel.count(os.sep) + 1
                    if level >= depth:
                        dirs.clear()
                        continue
                    # Skip blocked dirs
                    dirs[:] = sorted([d for d in dirs if d not in {'.git', 'node_modules', '.venv', '__pycache__', 'dist', '.next'}])
                    display_root = os.path.relpath(root, project_root)
                    for d in dirs:
                        entries.append(f'{display_root}/{d}/')
                    for f in sorted(files)[:50]:  # cap files per dir
                        if f not in BLOCKED_FILES:
                            entries.append(f'{display_root}/{f}')
                    if len(entries) > 500:
                        entries.append('... (truncated at 500 entries)')
                        break

                return {'action': 'tree', 'path': rel_path or '.', 'depth': depth, 'entries': entries, 'count': len(entries)}

            elif action == 'read_file':
                rel_path = payload.get('path', '')
                if not rel_path:
                    return {'error': 'path is required for read_file'}
                max_lines = min(payload.get('max_lines', 200), 500)
                full_path = _safe_path(rel_path)
                if not os.path.isfile(full_path):
                    return {'error': f'File not found: {rel_path}'}

                size = os.path.getsize(full_path)
                if size > 500_000:
                    return {'error': f'File too large: {size} bytes. Use search instead.'}

                with open(full_path, 'r', errors='replace') as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            break
                        lines.append(line.rstrip('\n'))

                total_lines = sum(1 for _ in open(full_path, 'r', errors='replace'))
                return {
                    'action': 'read_file',
                    'path': rel_path,
                    'lines': len(lines),
                    'total_lines': total_lines,
                    'truncated': total_lines > max_lines,
                    'content': '\n'.join(lines),
                }

            elif action == 'search':
                query = payload.get('query', '')
                if not query:
                    return {'error': 'query is required for search'}
                search_path = payload.get('path', '')
                file_type = payload.get('file_type', '')
                full_path = _safe_path(search_path)

                cmd = ['grep', '-rn', '--include=*', '-l', query, full_path]
                if file_type:
                    cmd = ['grep', '-rn', f'--include=*.{file_type}', '-l', query, full_path]

                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd=project_root)
                    files = [os.path.relpath(f, project_root) for f in result.stdout.strip().split('\n') if f]
                    files = [f for f in files if not any(bd in f for bd in BLOCKED_DIRS) and os.path.basename(f) not in BLOCKED_FILES]

                    # Get matching lines from first few files
                    matches = []
                    for fpath in files[:10]:
                        cmd2 = ['grep', '-n', query, os.path.join(project_root, fpath)]
                        r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=5)
                        for line in r2.stdout.strip().split('\n')[:5]:
                            if line:
                                matches.append(f'{fpath}:{line}')

                    return {
                        'action': 'search',
                        'query': query,
                        'files_matched': len(files),
                        'files': files[:30],
                        'sample_matches': matches[:30],
                    }
                except subprocess.TimeoutExpired:
                    return {'error': 'Search timed out (10s limit)'}

            elif action == 'git_info':
                result = {}
                try:
                    r = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, cwd=project_root, timeout=5)
                    result['branch'] = r.stdout.strip()
                except Exception:
                    result['branch'] = 'unknown'

                try:
                    r = subprocess.run(['git', 'log', '--oneline', '-10'], capture_output=True, text=True, cwd=project_root, timeout=5)
                    result['recent_commits'] = r.stdout.strip().split('\n')
                except Exception:
                    result['recent_commits'] = []

                try:
                    r = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True, cwd=project_root, timeout=5)
                    lines = r.stdout.strip().split('\n') if r.stdout.strip() else []
                    result['modified_files'] = len(lines)
                    result['status'] = lines[:20]
                except Exception:
                    result['modified_files'] = 0
                    result['status'] = []

                return {'action': 'git_info', **result}

            return {'error': f'Unknown repo_tool action: {action}'}

        except ValueError as e:
            return {'error': str(e)}
        except Exception as e:
            return {'error': f'repo_tool error: {str(e)}'}

    # ── Analytics / Event Queries ────────────────────────────────────────────

    def _handle_analytics(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Query DeliverableEvents and ATR-24h metrics."""
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Count, Min, Q

        action = payload.get('action', 'events_summary')

        try:
            from core.models_deliverables import Deliverable, DeliverableEvent

            if action == 'events_summary':
                days = payload.get('days', 7)
                since = timezone.now() - timedelta(days=days)

                events = DeliverableEvent.objects.filter(created_at__gte=since)
                by_type = list(events.values('event_type').annotate(count=Count('id')).order_by('-count'))
                by_source = list(events.values('source').annotate(count=Count('id')).order_by('-count'))
                total = events.count()

                return {
                    'action': 'events_summary',
                    'days': days,
                    'total_events': total,
                    'by_type': by_type,
                    'by_source': by_source,
                }

            elif action == 'atr_dashboard':
                # Reuse the stage3_dashboard view logic
                from core.views_deliverables import stage3_dashboard
                from django.test import RequestFactory
                from django.contrib.auth.models import AnonymousUser

                rf = RequestFactory()
                request = rf.get('/api/deliverables/stage3-dashboard/')
                request.user = AnonymousUser()
                response = stage3_dashboard(request)

                import json
                data = json.loads(response.content)
                return {'action': 'atr_dashboard', **data.get('dashboard', {})}

            elif action == 'events_query':
                days = payload.get('days', 7)
                limit = min(payload.get('limit', 50), 200)
                since = timezone.now() - timedelta(days=days)

                qs = DeliverableEvent.objects.filter(created_at__gte=since)

                event_type = payload.get('event_type')
                if event_type:
                    qs = qs.filter(event_type=event_type)

                deliverable_id = payload.get('deliverable_id')
                if deliverable_id:
                    qs = qs.filter(deliverable_id=deliverable_id)

                qs = qs.order_by('-created_at')[:limit]
                events = [
                    {
                        'id': str(e.id),
                        'event_type': e.event_type,
                        'deliverable_id': str(e.deliverable_id),
                        'deliverable_title': e.deliverable.title if e.deliverable else None,
                        'source': e.source,
                        'created_at': e.created_at.isoformat(),
                        'metadata': e.metadata or {},
                    }
                    for e in qs.select_related('deliverable')
                ]
                return {'action': 'events_query', 'count': len(events), 'events': events}

            return {'error': f'Unknown analytics_tool action: {action}'}

        except Exception as e:
            return {'error': f'analytics_tool error: {str(e)}'}

    # ── Discord Bot Introspection ────────────────────────────────────────────

    def _handle_discord(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Inspect Discord bot: commands, cogs, slot usage."""
        import os
        import re

        action = payload.get('action', 'status')
        bot_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'core', 'services', 'discord_bot.py'
        )

        try:
            if not os.path.isfile(bot_file):
                return {'error': 'discord_bot.py not found'}

            with open(bot_file, 'r') as f:
                content = f.read()

            if action == 'status':
                # Extract slot usage from comments
                slot_match = re.search(r'(\d+)\s*slots?\s*used', content)
                slots_used = int(slot_match.group(1)) if slot_match else None

                # Count cogs
                cog_classes = re.findall(r'class\s+(\w+)\(commands\.Cog\)', content)

                # Count app_commands
                slash_commands = re.findall(r'@app_commands\.command\(name=["\'](\w+)', content)
                groups = re.findall(r'app_commands\.Group\(name=["\'](\w+)', content)
                subcommands = re.findall(r'@(\w+)\.command\(name=["\'](\w+)', content)

                # Guild ID
                guild_match = re.search(r'GUILD_ID\s*=\s*(\d+)', content)
                guild_id = guild_match.group(1) if guild_match else None

                return {
                    'action': 'status',
                    'file': 'core/services/discord_bot.py',
                    'file_lines': content.count('\n') + 1,
                    'slots_used': slots_used,
                    'slots_limit': 100,
                    'slots_remaining': (100 - slots_used) if slots_used else None,
                    'sync_mode': 'guild_only',
                    'guild_id': guild_id,
                    'cog_count': len(cog_classes),
                    'top_level_commands': len(slash_commands),
                    'command_groups': len(groups),
                    'subcommands': len(subcommands),
                }

            elif action == 'commands':
                # Extract all slash commands
                slash_commands = re.findall(r'@app_commands\.command\(name=["\'](\w+)["\'](?:,\s*description=["\']([^"\']*)["\'])?\)', content)
                groups = re.findall(r'(\w+)\s*=\s*app_commands\.Group\(name=["\'](\w+)["\'](?:,\s*description=["\']([^"\']*)["\'])?\)', content)

                # Build group -> subcommands map
                group_vars = {g[0]: g[1] for g in groups}
                subcommands = re.findall(r'@(\w+)\.command\(name=["\'](\w+)["\']', content)
                group_subs = {}
                for var, sub_name in subcommands:
                    group_name = group_vars.get(var, var)
                    if group_name not in group_subs:
                        group_subs[group_name] = []
                    group_subs[group_name].append(sub_name)

                top_level = [{'name': f'/{c[0]}', 'description': c[1] if len(c) > 1 else ''} for c in slash_commands]
                grouped = [
                    {'group': f'/{g[1]}', 'description': g[2] if len(g) > 2 else '', 'subcommands': group_subs.get(g[1], [])}
                    for g in groups
                ]

                return {
                    'action': 'commands',
                    'top_level': top_level,
                    'top_level_count': len(top_level),
                    'groups': grouped,
                    'groups_count': len(grouped),
                    'total_subcommands': sum(len(g['subcommands']) for g in grouped),
                }

            elif action == 'cogs':
                cog_classes = re.findall(r'class\s+(\w+)\(commands\.Cog\)', content)
                return {'action': 'cogs', 'cogs': cog_classes, 'count': len(cog_classes)}

            return {'error': f'Unknown discord_tool action: {action}'}

        except Exception as e:
            return {'error': f'discord_tool error: {str(e)}'}

    # ── Mobile App Introspection ─────────────────────────────────────────────

    def _handle_mobile(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Inspect the React Native / Expo mobile app."""
        import os
        import json as json_mod

        action = payload.get('action', 'project_status')
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        mobile_root = os.path.join(project_root, 'mobile')

        try:
            if not os.path.isdir(mobile_root):
                return {'error': 'No mobile/ directory found in project root'}

            if action == 'project_status':
                result = {'action': 'project_status', 'path': 'mobile/'}

                # Read package.json
                pkg_path = os.path.join(mobile_root, 'package.json')
                if os.path.isfile(pkg_path):
                    with open(pkg_path, 'r') as f:
                        pkg = json_mod.load(f)
                    result['name'] = pkg.get('name', 'unknown')
                    result['version'] = pkg.get('version', 'unknown')
                    deps = pkg.get('dependencies', {})
                    result['expo_version'] = deps.get('expo', 'not found')
                    result['react_native_version'] = deps.get('react-native', 'not found')
                    result['navigation'] = 'react-navigation' if '@react-navigation/native' in deps else 'expo-router' if 'expo-router' in deps else 'unknown'
                    result['total_dependencies'] = len(deps)

                # Read app.config.ts or app.json
                for cfg_name in ['app.config.ts', 'app.config.js', 'app.json']:
                    cfg_path = os.path.join(mobile_root, cfg_name)
                    if os.path.isfile(cfg_path):
                        result['config_file'] = cfg_name
                        break

                # Check EAS config
                eas_path = os.path.join(mobile_root, 'eas.json')
                if os.path.isfile(eas_path):
                    with open(eas_path, 'r') as f:
                        eas = json_mod.load(f)
                    result['eas_profiles'] = list(eas.get('build', {}).keys())

                return result

            elif action == 'screens':
                screens_dir = os.path.join(mobile_root, 'src', 'screens')
                if not os.path.isdir(screens_dir):
                    return {'error': 'No src/screens/ directory found'}

                screens = []
                for f in sorted(os.listdir(screens_dir)):
                    if f.endswith('.tsx') or f.endswith('.ts'):
                        fpath = os.path.join(screens_dir, f)
                        size = os.path.getsize(fpath)
                        # Check if it's a placeholder
                        with open(fpath, 'r') as fh:
                            first_500 = fh.read(500)
                        is_placeholder = 'Placeholder' in first_500 or 'Coming soon' in first_500.lower()
                        screens.append({
                            'file': f,
                            'name': f.replace('.tsx', '').replace('.ts', ''),
                            'size_bytes': size,
                            'status': 'placeholder' if is_placeholder else 'implemented',
                        })

                # Also check screen registry
                registry_path = os.path.join(mobile_root, 'src', 'navigation', 'screenRegistry.ts')
                routes = []
                if os.path.isfile(registry_path):
                    with open(registry_path, 'r') as f:
                        import re
                        reg_content = f.read()
                    route_matches = re.findall(r"'(/[^']*)'.*?:\s*(\w+)", reg_content)
                    routes = [{'route': r[0], 'component': r[1]} for r in route_matches]

                return {
                    'action': 'screens',
                    'screens': screens,
                    'count': len(screens),
                    'implemented': sum(1 for s in screens if s['status'] == 'implemented'),
                    'placeholders': sum(1 for s in screens if s['status'] == 'placeholder'),
                    'routes': routes,
                }

            elif action == 'api_modules':
                api_dir = os.path.join(mobile_root, 'src', 'api')
                if not os.path.isdir(api_dir):
                    return {'error': 'No src/api/ directory found'}

                modules = []
                for f in sorted(os.listdir(api_dir)):
                    if f.endswith('.ts') or f.endswith('.tsx'):
                        fpath = os.path.join(api_dir, f)
                        size = os.path.getsize(fpath)
                        modules.append({'file': f, 'size_bytes': size})

                return {'action': 'api_modules', 'modules': modules, 'count': len(modules)}

            elif action == 'dependencies':
                pkg_path = os.path.join(mobile_root, 'package.json')
                if not os.path.isfile(pkg_path):
                    return {'error': 'No package.json found'}
                with open(pkg_path, 'r') as f:
                    pkg = json_mod.load(f)
                deps = pkg.get('dependencies', {})
                dev_deps = pkg.get('devDependencies', {})
                # Return key deps only
                key_packages = [
                    'expo', 'react-native', 'react', '@react-navigation/native',
                    '@react-navigation/drawer', 'expo-router', 'zustand',
                    'axios', '@sentry/react-native', 'expo-notifications',
                    'expo-secure-store', '@react-native-async-storage/async-storage',
                ]
                key_deps = {k: deps.get(k, dev_deps.get(k, 'not installed')) for k in key_packages}
                return {
                    'action': 'dependencies',
                    'total_deps': len(deps),
                    'total_dev_deps': len(dev_deps),
                    'key_packages': key_deps,
                }

            return {'error': f'Unknown mobile_tool action: {action}'}

        except Exception as e:
            return {'error': f'mobile_tool error: {str(e)}'}

    def _handle_vip_invite(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Manage VIP magic-link invites for demo viewers."""
        from django.contrib.auth import get_user_model
        from core.models_vip_invite import VIPInvite
        from django.conf import settings as django_settings

        User = get_user_model()
        action = payload.get('action', 'list')

        try:
            if action == 'list':
                invites = VIPInvite.objects.select_related('created_by', 'redeemed_by').all()[:20]
                return {
                    'action': 'list',
                    'total': VIPInvite.objects.count(),
                    'invites': [{
                        'id': str(inv.id),
                        'label': inv.label,
                        'is_valid': inv.is_valid,
                        'token_expires_at': inv.token_expires_at.isoformat(),
                        'redeemed_by': inv.redeemed_by.username if inv.redeemed_by else None,
                        'revoked': inv.revoked_at is not None,
                        'created_by': inv.created_by.username,
                    } for inv in invites],
                }

            elif action == 'create':
                label = payload.get('label', '')
                admin_user = User.objects.filter(is_superuser=True).first()
                if not admin_user:
                    return {'error': 'No admin user found to create invite'}

                invite = VIPInvite.objects.create(created_by=admin_user, label=label)
                base_url = getattr(django_settings, 'FRONTEND_URL', 'https://donkey-betz-platform-production.up.railway.app')
                accept_url = f"{base_url.rstrip('/')}/vip/accept?token={invite.token}"

                return {
                    'action': 'create',
                    'id': str(invite.id),
                    'token': invite.token,
                    'accept_url': accept_url,
                    'token_expires_at': invite.token_expires_at.isoformat(),
                    'account_expires_at': invite.account_expires_at.isoformat(),
                    'label': invite.label,
                }

            elif action == 'revoke':
                invite_id = payload.get('id', '')
                if not invite_id:
                    return {'error': 'Provide invite id to revoke'}
                try:
                    invite = VIPInvite.objects.get(id=invite_id)
                except VIPInvite.DoesNotExist:
                    return {'error': f'Invite {invite_id} not found'}
                if invite.revoked_at:
                    return {'error': 'Already revoked'}

                from django.utils import timezone
                invite.revoked_at = timezone.now()
                invite.save(update_fields=['revoked_at'])
                if invite.redeemed_by:
                    invite.redeemed_by.is_active = False
                    invite.redeemed_by.save(update_fields=['is_active'])

                return {'action': 'revoke', 'id': str(invite.id), 'status': 'revoked'}

            else:
                return {'error': f'Unknown action: {action}. Use list, create, or revoke.'}

        except Exception as e:
            logger.error(f"[VIP_INVITE] Error: {e}", exc_info=True)
            return {'error': str(e)}


    # ── Session 1100: Cockpit Tool — Celery ops dashboard ───────────────────────
    def _handle_cockpit(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Celery ops cockpit: beat schedule, task status, worker health, queue depths, failures."""
        action = payload.get('action', 'help')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            if action == 'help':
                return {
                    'tool': 'cockpit_tool',
                    'actions': [
                        'beat_schedule — list all Celery Beat periodic tasks',
                        'task_status — check a specific task by ID',
                        'worker_health — active workers, queues, concurrency',
                        'recent_failures — failed tasks with errors',
                        'queue_lengths — current queue depths',
                    ],
                }

            if action == 'beat_schedule':
                from django_celery_beat.models import PeriodicTask
                tasks = PeriodicTask.objects.select_related(
                    'interval', 'crontab'
                ).order_by('name')[:limit]
                return {
                    'action': 'beat_schedule',
                    'total': PeriodicTask.objects.count(),
                    'tasks': [{
                        'name': t.name,
                        'task': t.task,
                        'enabled': t.enabled,
                        'schedule': str(t.interval or t.crontab or 'custom'),
                        'last_run_at': t.last_run_at.isoformat() if t.last_run_at else None,
                        'total_run_count': t.total_run_count,
                        'queue': t.queue or 'default',
                    } for t in tasks],
                }

            if action == 'task_status':
                task_id = payload.get('task_id', '')
                if not task_id:
                    return {'error': 'Provide task_id to check status'}
                from core.models_celery_telemetry import CeleryTaskEvent
                event = CeleryTaskEvent.objects.filter(
                    task_id=task_id
                ).order_by('-started_at').first()
                if not event:
                    return {'error': f'No CeleryTaskEvent found for task_id {task_id}'}
                return {
                    'action': 'task_status',
                    'task_id': task_id,
                    'task_name': event.task_name,
                    'status': event.status,
                    'started_at': event.started_at.isoformat() if event.started_at else None,
                    'finished_at': event.finished_at.isoformat() if event.finished_at else None,
                    'duration_seconds': event.duration_seconds,
                    'worker': event.worker,
                    'queue': event.queue,
                    'error_message': event.error_message,
                    'rss_mb_start': event.rss_mb_start,
                    'rss_mb_end': event.rss_mb_end,
                }

            if action == 'worker_health':
                from core.celery import app as celery_app
                inspector = celery_app.control.inspect(timeout=5)
                active = inspector.active() or {}
                stats = inspector.stats() or {}
                workers = []
                for worker_name, worker_stats in stats.items():
                    pool = worker_stats.get('pool', {})
                    workers.append({
                        'name': worker_name,
                        'active_tasks': len(active.get(worker_name, [])),
                        'concurrency': pool.get('max-concurrency', 'unknown'),
                        'pool': pool.get('implementation', 'unknown'),
                        'prefetch_count': worker_stats.get('prefetch_count', 0),
                    })
                return {'action': 'worker_health', 'workers': workers}

            if action == 'recent_failures':
                from core.models_celery_telemetry import CeleryTaskEvent
                qs = CeleryTaskEvent.objects.filter(status='FAILURE').order_by('-started_at')
                queue_filter = payload.get('queue')
                if queue_filter:
                    qs = qs.filter(queue=queue_filter)
                failures = qs[:limit]
                return {
                    'action': 'recent_failures',
                    'count': len(failures),
                    'failures': [{
                        'task_name': f.task_name,
                        'task_id': f.task_id,
                        'started_at': f.started_at.isoformat() if f.started_at else None,
                        'error_type': f.error_type,
                        'error_message': (f.error_message or '')[:300],
                        'queue': f.queue,
                        'worker': f.worker,
                        'duration_seconds': f.duration_seconds,
                    } for f in failures],
                }

            if action == 'queue_lengths':
                from core.celery import app as celery_app
                inspector = celery_app.control.inspect(timeout=5)
                active = inspector.active() or {}
                reserved = inspector.reserved() or {}
                queues = {}
                for worker_name in set(list(active) + list(reserved)):
                    for task in active.get(worker_name, []):
                        q = task.get('delivery_info', {}).get('routing_key', 'unknown')
                        queues.setdefault(q, {'active': 0, 'reserved': 0})
                        queues[q]['active'] += 1
                    for task in reserved.get(worker_name, []):
                        q = task.get('delivery_info', {}).get('routing_key', 'unknown')
                        queues.setdefault(q, {'active': 0, 'reserved': 0})
                        queues[q]['reserved'] += 1
                return {'action': 'queue_lengths', 'queues': queues}

            return {'error': f'Unknown cockpit_tool action: {action}'}

        except Exception as e:
            logger.error(f"[COCKPIT] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1100: Narrative Tool — drift, shifts, evidence, alerts ─────────
    def _handle_narrative(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Narrative drift analysis: narratives, shifts, evidence, alerts."""
        action = payload.get('action', 'help')
        limit = min(int(payload.get('limit', 10)), 30)
        domain = payload.get('category') or payload.get('domain')  # accept both, model field is 'domain'

        try:
            if action == 'help':
                return {
                    'tool': 'narrative_tool',
                    'actions': [
                        'narratives — list tracked narratives',
                        'shifts — recent narrative shifts/drift detections',
                        'evidence — evidence items for a specific narrative',
                        'alerts — narrative alerts (Discord notifications)',
                    ],
                }

            from core.models_narrative_drift import (
                Narrative, NarrativeShift, NarrativeEvidence, NarrativeAlert,
            )

            if action == 'narratives':
                qs = Narrative.objects.all().order_by('-updated_at')
                if domain:
                    qs = qs.filter(domain=domain)
                narratives = qs[:limit]
                return {
                    'action': 'narratives',
                    'total': qs.count(),
                    'narratives': [{
                        'id': str(n.id),
                        'title': n.title,
                        'domain': n.domain,
                        'status': n.status,
                        'confidence': float(n.confidence) if n.confidence else None,
                        'evidence_count': NarrativeEvidence.objects.filter(narrative=n).count(),
                        'updated_at': n.updated_at.isoformat() if hasattr(n, 'updated_at') and n.updated_at else None,
                    } for n in narratives],
                }

            if action == 'shifts':
                qs = NarrativeShift.objects.select_related('old_narrative').order_by('-detected_at')
                if domain:
                    qs = qs.filter(domain=domain)
                shifts = qs[:limit]
                return {
                    'action': 'shifts',
                    'count': len(shifts),
                    'shifts': [{
                        'id': str(s.id),
                        'narrative': s.old_narrative.title if s.old_narrative else 'Unknown',
                        'domain': s.domain,
                        'shift_summary': (s.shift_summary or '')[:200],
                        'confidence': float(s.confidence) if s.confidence else None,
                        'importance': float(s.importance) if s.importance else None,
                        'trend_break_analysis': (s.trend_break_analysis or '')[:200],
                        'cultural_impact_analysis': (s.cultural_impact_analysis or '')[:200],
                        'detected_at': s.detected_at.isoformat() if s.detected_at else None,
                    } for s in shifts],
                }

            if action == 'evidence':
                narrative_id = payload.get('narrative_id', '')
                if not narrative_id:
                    return {'error': 'Provide narrative_id for evidence lookup'}
                evidence = NarrativeEvidence.objects.filter(
                    narrative_id=narrative_id
                ).order_by('-created_at')[:limit]
                return {
                    'action': 'evidence',
                    'narrative_id': narrative_id,
                    'count': len(evidence),
                    'evidence': [{
                        'id': str(e.id),
                        'source_title': e.source_title or '',
                        'source_url': e.source_url or '',
                        'source_type': e.source_type or '',
                        'sentiment': e.sentiment,
                        'strength': float(e.strength) if e.strength else None,
                        'excerpt': (e.excerpt or '')[:200],
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    } for e in evidence],
                }

            if action == 'alerts':
                alerts = NarrativeAlert.objects.order_by('-created_at')[:limit]
                return {
                    'action': 'alerts',
                    'count': len(alerts),
                    'alerts': [{
                        'id': str(a.id),
                        'title': a.title or '',
                        'alert_type': a.alert_type,
                        'summary': (a.summary or a.message or '')[:200],
                        'sent_to_discord': a.sent_to_discord,
                        'created_at': a.created_at.isoformat() if a.created_at else None,
                    } for a in alerts],
                }

            return {'error': f'Unknown narrative_tool action: {action}'}

        except Exception as e:
            logger.error(f"[NARRATIVE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Proactive Tool ──────────────────────────────────────
    def _handle_proactive(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Proactive alerts, notifications, suggestions, automations."""
        action = payload.get('action', 'dashboard')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_unified_system import (
                ProactiveAlert, ProactiveNotification, SmartSuggestion, AutomatedAction,
            )

            if action == 'alerts':
                alerts = ProactiveAlert.objects.filter(is_active=True).order_by('-last_triggered', '-created_at')[:limit]
                return {
                    'action': 'alerts',
                    'count': len(alerts),
                    'alerts': [{
                        'id': str(a.id),
                        'name': a.name,
                        'alert_type': a.alert_type,
                        'condition': a.condition,
                        'is_active': a.is_active,
                        'trigger_count': a.trigger_count,
                        'last_triggered': a.last_triggered.isoformat() if a.last_triggered else None,
                        'check_frequency': a.check_frequency,
                    } for a in alerts],
                }

            if action == 'notifications':
                qs = ProactiveNotification.objects.order_by('-created_at')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                notifs = qs[:limit]
                return {
                    'action': 'notifications',
                    'count': len(notifs),
                    'notifications': [{
                        'id': str(n.id),
                        'title': n.title,
                        'message': (n.message or '')[:200],
                        'notification_type': n.notification_type,
                        'priority': n.priority,
                        'is_read': n.is_read,
                        'delivery_status': n.delivery_status,
                        'created_at': n.created_at.isoformat() if n.created_at else None,
                    } for n in notifs],
                }

            if action == 'suggestions':
                qs = SmartSuggestion.objects.filter(status='pending').order_by('-confidence_score')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                suggestions = qs[:limit]
                return {
                    'action': 'suggestions',
                    'count': len(suggestions),
                    'suggestions': [{
                        'id': str(s.id),
                        'title': s.title,
                        'suggestion_type': s.suggestion_type,
                        'category': s.category,
                        'confidence_score': float(s.confidence_score) if s.confidence_score else None,
                        'estimated_revenue_impact': float(s.estimated_revenue_impact) if s.estimated_revenue_impact else None,
                        'effort_level': s.effort_level,
                        'status': s.status,
                    } for s in suggestions],
                }

            if action == 'automations':
                automations = AutomatedAction.objects.filter(is_active=True).order_by('-last_executed')[:limit]
                return {
                    'action': 'automations',
                    'count': len(automations),
                    'automations': [{
                        'id': str(a.id),
                        'name': a.name,
                        'action_type': a.action_type,
                        'trigger_type': a.trigger_type,
                        'is_active': a.is_active,
                        'total_executions': a.total_executions,
                        'successful_executions': a.successful_executions,
                        'last_executed': a.last_executed.isoformat() if a.last_executed else None,
                    } for a in automations],
                }

            if action == 'dashboard':
                unread = ProactiveNotification.objects.filter(is_read=False)
                if user_id:
                    unread = unread.filter(user_id=user_id)
                return {
                    'action': 'dashboard',
                    'unread_notifications': unread.count(),
                    'active_alerts': ProactiveAlert.objects.filter(is_active=True).count(),
                    'pending_suggestions': SmartSuggestion.objects.filter(status='pending').count(),
                    'active_automations': AutomatedAction.objects.filter(is_active=True).count(),
                }

            return {'error': f'Unknown proactive_tool action: {action}'}

        except Exception as e:
            logger.error(f"[PROACTIVE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Distribution Tool ───────────────────────────────────
    def _handle_distribution(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Content distribution platforms, listings, revenue."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_unified_system import DistributionPlatform, ContentDistribution
            from django.db.models import Sum, Count

            if action == 'platforms':
                platforms = DistributionPlatform.objects.filter(is_active=True).order_by('name')[:limit]
                return {
                    'action': 'platforms',
                    'count': len(platforms),
                    'platforms': [{
                        'id': str(p.id),
                        'name': p.name,
                        'platform_type': p.platform_type,
                        'commission_percent': float(p.commission_percent) if p.commission_percent else None,
                        'is_active': p.is_active,
                    } for p in platforms],
                }

            if action == 'listings':
                qs = ContentDistribution.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                if user_id:
                    qs = qs.filter(user_id=user_id)
                listings = qs[:limit]
                return {
                    'action': 'listings',
                    'count': len(listings),
                    'listings': [{
                        'id': str(d.id),
                        'title': d.title or '',
                        'platform_account': str(d.platform_account) if d.platform_account else '',
                        'content_type': d.content_type,
                        'status': d.status,
                        'price': float(d.price) if d.price else None,
                        'revenue': float(d.revenue) if d.revenue else 0,
                        'sales': d.sales or 0,
                        'views': d.views or 0,
                        'listed_at': d.listed_at.isoformat() if d.listed_at else None,
                    } for d in listings],
                }

            if action == 'revenue':
                qs = ContentDistribution.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                revenue_by_platform = list(
                    qs.values('platform_account')
                    .annotate(total_revenue=Sum('revenue'), total_sales=Sum('sales'))
                    .order_by('-total_revenue')
                )
                return {
                    'action': 'revenue',
                    'platforms': [{
                        'platform': str(r['platform_account'] or 'Unknown'),
                        'total_revenue': float(r['total_revenue'] or 0),
                        'total_sales': r['total_sales'] or 0,
                    } for r in revenue_by_platform],
                }

            if action == 'stats':
                qs = ContentDistribution.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                agg = qs.aggregate(
                    total_revenue=Sum('revenue'),
                    total_sales=Sum('sales'),
                    total_views=Sum('views'),
                )
                status_counts = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                return {
                    'action': 'stats',
                    'total_listings': qs.count(),
                    'total_revenue': float(agg['total_revenue'] or 0),
                    'total_sales': agg['total_sales'] or 0,
                    'total_views': agg['total_views'] or 0,
                    'by_status': status_counts,
                    'active_platforms': DistributionPlatform.objects.filter(is_active=True).count(),
                }

            return {'error': f'Unknown distribution_tool action: {action}'}

        except Exception as e:
            logger.error(f"[DISTRIBUTION] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Calendar Tool ───────────────────────────────────────
    def _handle_calendar(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Content channels and episodes."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_autonomous_studio import ContentChannel, ChannelEpisode
            from django.db.models import Count
            from django.utils import timezone

            if action == 'channels':
                qs = ContentChannel.objects.order_by('-total_episodes_created')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                channels = qs[:limit]
                return {
                    'action': 'channels',
                    'count': len(channels),
                    'channels': [{
                        'id': str(c.id),
                        'name': c.name,
                        'topic_domain': (c.topic_domain or '')[:100],
                        'content_frequency': c.content_frequency,
                        'platform': c.platform,
                        'status': getattr(c, 'status', 'active'),
                        'total_episodes_created': c.total_episodes_created or 0,
                        'next_content_due': c.next_content_due.isoformat() if getattr(c, 'next_content_due', None) else None,
                    } for c in channels],
                }

            if action == 'episodes':
                qs = ChannelEpisode.objects.select_related('channel').order_by('-created_at')
                channel_id = payload.get('channel_id')
                if channel_id:
                    qs = qs.filter(channel_id=channel_id)
                episodes = qs[:limit]
                return {
                    'action': 'episodes',
                    'count': len(episodes),
                    'episodes': [{
                        'id': str(e.id),
                        'title': e.title or '',
                        'topic': e.topic or '',
                        'channel': e.channel.name if e.channel else '',
                        'intent_type': getattr(e, 'intent_type', ''),
                        'performance_score': float(e.performance_score) if e.performance_score else None,
                        'created_at': e.created_at.isoformat() if hasattr(e, 'created_at') and e.created_at else None,
                    } for e in episodes],
                }

            if action == 'upcoming':
                now = timezone.now()
                upcoming = ContentChannel.objects.filter(
                    next_content_due__gt=now
                ).order_by('next_content_due')[:limit]
                return {
                    'action': 'upcoming',
                    'count': len(upcoming),
                    'upcoming': [{
                        'id': str(c.id),
                        'name': c.name,
                        'platform': c.platform,
                        'next_content_due': c.next_content_due.isoformat() if c.next_content_due else None,
                    } for c in upcoming],
                }

            if action == 'stats':
                channels = ContentChannel.objects.all()
                if user_id:
                    channels = channels.filter(user_id=user_id)
                episodes = ChannelEpisode.objects.all()
                platform_counts = dict(channels.values_list('platform').annotate(c=Count('id')).values_list('platform', 'c'))
                return {
                    'action': 'stats',
                    'total_channels': channels.count(),
                    'total_episodes': episodes.count(),
                    'by_platform': platform_counts,
                }

            return {'error': f'Unknown calendar_tool action: {action}'}

        except Exception as e:
            logger.error(f"[CALENDAR] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Experiment Tool ─────────────────────────────────────
    def _handle_experiment(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """A/B tests and experiment results."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_unified_system import ABTest, ABTestVariant
            from django.db.models import Count

            if action == 'tests':
                qs = ABTest.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                if user_id:
                    qs = qs.filter(user_id=user_id)
                tests = qs[:limit]
                return {
                    'action': 'tests',
                    'count': len(tests),
                    'tests': [{
                        'id': str(t.id),
                        'name': t.name,
                        'test_type': t.test_type,
                        'status': t.status,
                        'primary_metric': t.primary_metric,
                        'start_date': t.start_date.isoformat() if t.start_date else None,
                        'statistical_significance': float(t.statistical_significance) if t.statistical_significance else None,
                    } for t in tests],
                }

            if action == 'results':
                test_id = payload.get('test_id', '')
                if not test_id:
                    return {'error': 'Provide test_id for results'}
                test = ABTest.objects.filter(id=test_id).first()
                if not test:
                    return {'error': f'ABTest {test_id} not found'}
                variants = ABTestVariant.objects.filter(test=test).order_by('created_at')
                return {
                    'action': 'results',
                    'test': {
                        'id': str(test.id),
                        'name': test.name,
                        'test_type': test.test_type,
                        'status': test.status,
                        'hypothesis': test.hypothesis or '',
                        'primary_metric': test.primary_metric,
                        'conclusion': test.conclusion or '',
                        'statistical_significance': float(test.statistical_significance) if test.statistical_significance else None,
                    },
                    'variants': [{
                        'id': str(v.id),
                        'name': v.name,
                        'is_control': v.is_control,
                        'traffic_percentage': float(v.traffic_percentage) if v.traffic_percentage else None,
                        'config': v.config,
                    } for v in variants],
                }

            if action == 'stats':
                qs = ABTest.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                status_counts = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                type_counts = dict(qs.values_list('test_type').annotate(c=Count('id')).values_list('test_type', 'c'))
                return {
                    'action': 'stats',
                    'total_tests': qs.count(),
                    'by_status': status_counts,
                    'by_type': type_counts,
                }

            return {'error': f'Unknown experiment_tool action: {action}'}

        except Exception as e:
            logger.error(f"[EXPERIMENT] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Podcast Tool ────────────────────────────────────────
    def _handle_podcast(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Podcast shows, episodes, scripts."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_podcast_studio import PodcastShow, PodcastEpisode
            from django.db.models import Sum, Count

            if action == 'shows':
                qs = PodcastShow.objects.order_by('-episode_count')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                shows = qs[:limit]
                return {
                    'action': 'shows',
                    'count': len(shows),
                    'shows': [{
                        'id': str(s.id),
                        'name': s.name,
                        'format': s.format,
                        'participant_count': s.participant_count or 0,
                        'episode_count': s.episode_count or 0,
                        'total_listens': s.total_listens or 0,
                    } for s in shows],
                }

            if action == 'episodes':
                qs = PodcastEpisode.objects.select_related('show').order_by('-created_at')
                show_id = payload.get('show_id')
                if show_id:
                    qs = qs.filter(show_id=show_id)
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                episodes = qs[:limit]
                return {
                    'action': 'episodes',
                    'count': len(episodes),
                    'episodes': [{
                        'id': str(e.id),
                        'title': e.title or '',
                        'topic': e.topic or '',
                        'show': e.show.name if e.show else '',
                        'status': e.status,
                        'progress_percent': e.progress_percent or 0,
                        'audio_duration_seconds': e.audio_duration_seconds,
                        'listen_count': e.listen_count or 0,
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    } for e in episodes],
                }

            if action == 'scripts':
                episode_id = payload.get('episode_id', '')
                if not episode_id:
                    return {'error': 'Provide episode_id for scripts'}
                ep = PodcastEpisode.objects.filter(id=episode_id).first()
                if not ep:
                    return {'error': f'PodcastEpisode {episode_id} not found'}
                return {
                    'action': 'scripts',
                    'episode_id': str(ep.id),
                    'title': ep.title or '',
                    'script': (ep.script or '')[:3000],
                }

            if action == 'stats':
                shows = PodcastShow.objects.all()
                episodes = PodcastEpisode.objects.all()
                if user_id:
                    shows = shows.filter(user_id=user_id)
                    episodes = episodes.filter(user_id=user_id)
                agg = episodes.aggregate(total_listens=Sum('listen_count'))
                status_counts = dict(episodes.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                return {
                    'action': 'stats',
                    'total_shows': shows.count(),
                    'total_episodes': episodes.count(),
                    'total_listens': agg['total_listens'] or 0,
                    'by_status': status_counts,
                }

            return {'error': f'Unknown podcast_tool action: {action}'}

        except Exception as e:
            logger.error(f"[PODCAST] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Campaign Tool ───────────────────────────────────────
    def _handle_campaign(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Campaigns and deliverables."""
        action = payload.get('action', 'list')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_campaign import Campaign, CampaignDeliverable
            from django.db.models import Count

            if action == 'list':
                qs = Campaign.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                if user_id:
                    qs = qs.filter(user_id=user_id)
                campaigns = qs[:limit]
                return {
                    'action': 'list',
                    'count': len(campaigns),
                    'campaigns': [{
                        'id': str(c.id),
                        'name': c.name,
                        'status': c.status,
                        'budget_tier': c.budget_tier,
                        'client_name': c.client_name or '',
                        'product_name': c.product_name or '',
                        'progress_percent': c.progress_percent or 0,
                        'created_at': c.created_at.isoformat() if c.created_at else None,
                    } for c in campaigns],
                }

            if action == 'detail':
                campaign_id = payload.get('campaign_id', '')
                if not campaign_id:
                    return {'error': 'Provide campaign_id for detail'}
                campaign = Campaign.objects.filter(id=campaign_id).first()
                if not campaign:
                    return {'error': f'Campaign {campaign_id} not found'}
                deliverables = CampaignDeliverable.objects.filter(campaign=campaign).order_by('created_at')
                return {
                    'action': 'detail',
                    'campaign': {
                        'id': str(campaign.id),
                        'name': campaign.name,
                        'status': campaign.status,
                        'budget_tier': campaign.budget_tier,
                        'client_name': campaign.client_name or '',
                        'product_name': campaign.product_name or '',
                        'progress_percent': campaign.progress_percent or 0,
                    },
                    'deliverables': [{
                        'id': str(d.id),
                        'name': d.name,
                        'deliverable_type': d.deliverable_type,
                        'status': d.status,
                        'platform': d.platform or '',
                    } for d in deliverables],
                }

            if action == 'stats':
                qs = Campaign.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                status_counts = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                tier_counts = dict(qs.values_list('budget_tier').annotate(c=Count('id')).values_list('budget_tier', 'c'))
                return {
                    'action': 'stats',
                    'total_campaigns': qs.count(),
                    'by_status': status_counts,
                    'by_budget_tier': tier_counts,
                }

            return {'error': f'Unknown campaign_tool action: {action}'}

        except Exception as e:
            logger.error(f"[CAMPAIGN] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Audit Tool ──────────────────────────────────────────
    def _handle_audit(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Audit findings, wiring defects, citation violations."""
        action = payload.get('action', 'findings')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            if action == 'findings' or action == 'p0_summary':
                from core.models_audit_tracking import AuditFinding
                qs = AuditFinding.objects.order_by('-created_at')
                if action == 'p0_summary':
                    qs = qs.filter(priority__in=['P0', 'P1']).exclude(status='resolved')
                else:
                    priority_filter = payload.get('priority')
                    if priority_filter:
                        qs = qs.filter(priority=priority_filter)
                    status_filter = payload.get('status')
                    if status_filter:
                        qs = qs.filter(status=status_filter)
                findings = qs[:limit]
                return {
                    'action': action,
                    'count': len(findings),
                    'findings': [{
                        'id': str(f.id),
                        'finding_id': f.finding_id or '',
                        'title': f.title,
                        'priority': f.priority,
                        'category': f.category,
                        'status': f.status,
                        'impact': (f.impact or '')[:200],
                        'assigned_agent': f.assigned_agent or '',
                    } for f in findings],
                }

            if action == 'wiring_defects':
                from core.models_orchestration import WiringDefect
                qs = WiringDefect.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter == 'resolved':
                    qs = qs.filter(is_resolved=True)
                elif status_filter == 'unresolved':
                    qs = qs.filter(is_resolved=False)
                defects = qs[:limit]
                return {
                    'action': 'wiring_defects',
                    'count': len(defects),
                    'defects': [{
                        'id': str(d.id),
                        'defect_type': d.defect_type,
                        'agent_name': d.agent_name or '',
                        'object_type': d.object_type or '',
                        'is_resolved': d.is_resolved,
                        'created_at': d.created_at.isoformat() if d.created_at else None,
                    } for d in defects],
                }

            if action == 'citations':
                from core.models_orchestration import CitationViolation
                qs = CitationViolation.objects.order_by('-created_at')
                defects = qs[:limit]
                return {
                    'action': 'citations',
                    'count': len(defects),
                    'violations': [{
                        'id': str(v.id),
                        'violation_type': v.violation_type,
                        'agent_name': v.agent_name or '',
                        'provided_sources': v.provided_sources or 0,
                        'required_sources': v.required_sources or 0,
                        'was_blocked': v.was_blocked,
                        'is_resolved': v.is_resolved,
                        'created_at': v.created_at.isoformat() if v.created_at else None,
                    } for v in defects],
                }

            return {'error': f'Unknown audit_tool action: {action}'}

        except Exception as e:
            logger.error(f"[AUDIT] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: ConceptForge Tool ───────────────────────────────────
    def _handle_conceptforge(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """ConceptForge pipeline runs, stages, artifacts."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_conceptforge import ConceptForgeRun, ConceptForgeStageRun, ConceptForgeArtifact
            from django.db.models import Count, Avg

            if action == 'runs':
                qs = ConceptForgeRun.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                runs = qs[:limit]
                return {
                    'action': 'runs',
                    'count': len(runs),
                    'runs': [{
                        'id': str(r.id),
                        'source_type': r.source_type,
                        'source_title': (r.source_title or '')[:100],
                        'domain': r.domain or '',
                        'status': r.status,
                        'quality_score': float(r.quality_score) if r.quality_score else None,
                        'duration_ms': r.duration_ms,
                        'created_at': r.created_at.isoformat() if r.created_at else None,
                    } for r in runs],
                }

            if action == 'run_detail':
                run_id = payload.get('run_id', '')
                if not run_id:
                    return {'error': 'Provide run_id for run_detail'}
                run = ConceptForgeRun.objects.filter(id=run_id).first()
                if not run:
                    return {'error': f'ConceptForgeRun {run_id} not found'}
                stages = ConceptForgeStageRun.objects.filter(run=run).order_by('stage_order')
                artifacts = ConceptForgeArtifact.objects.filter(run=run).order_by('created_at')
                return {
                    'action': 'run_detail',
                    'run': {
                        'id': str(run.id),
                        'source_type': run.source_type,
                        'source_title': run.source_title or '',
                        'domain': run.domain or '',
                        'status': run.status,
                        'quality_score': float(run.quality_score) if run.quality_score else None,
                        'duration_ms': run.duration_ms,
                    },
                    'stages': [{
                        'stage_name': s.stage_name,
                        'agent_used': s.agent_used or '',
                        'status': s.status,
                        'duration_ms': s.duration_ms,
                    } for s in stages],
                    'artifacts': [{
                        'id': str(a.id),
                        'name': a.name,
                        'kind': a.kind,
                        'is_primary': a.is_primary,
                    } for a in artifacts],
                }

            if action == 'stats':
                qs = ConceptForgeRun.objects.all()
                agg = qs.aggregate(avg_quality=Avg('quality_score'))
                status_counts = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                source_counts = dict(qs.values_list('source_type').annotate(c=Count('id')).values_list('source_type', 'c'))
                return {
                    'action': 'stats',
                    'total_runs': qs.count(),
                    'avg_quality_score': float(agg['avg_quality'] or 0),
                    'by_status': status_counts,
                    'by_source_type': source_counts,
                }

            return {'error': f'Unknown conceptforge_tool action: {action}'}

        except Exception as e:
            logger.error(f"[CONCEPTFORGE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Profile Tool ────────────────────────────────────────
    def _handle_profile(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Extended user profile and skills."""
        action = payload.get('action', 'profile')

        try:
            if action == 'profile':
                from core.models import ExtendedUserProfile
                profile = ExtendedUserProfile.objects.filter(user_id=user_id).first() if user_id else None
                if not profile:
                    return {'action': 'profile', 'profile': None, 'message': 'No extended profile found'}
                return {
                    'action': 'profile',
                    'profile': {
                        'full_name': profile.full_name or '',
                        'location': profile.location or '',
                        'timezone': profile.timezone or '',
                        'current_title': profile.current_title or '',
                        'years_experience': profile.years_experience,
                        'experience_level': profile.experience_level or '',
                        'skills': profile.skills or [],
                        'certifications': profile.certifications or [],
                        'remote_preference': profile.remote_preference or '',
                        'profile_completeness': profile.profile_completeness or 0,
                    },
                }

            if action == 'skills':
                from core.models_user_learning import UserSkill
                qs = UserSkill.objects.order_by('-confidence', '-last_demonstrated')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                skills = qs[:50]
                return {
                    'action': 'skills',
                    'count': len(skills),
                    'skills': [{
                        'id': str(s.id),
                        'skill_name': s.skill_name,
                        'category': s.category or '',
                        'proficiency_level': s.proficiency_level or '',
                        'evidence_count': s.evidence_count or 0,
                        'confidence': float(s.confidence) if s.confidence else None,
                        'last_demonstrated': s.last_demonstrated.isoformat() if s.last_demonstrated else None,
                    } for s in skills],
                }

            if action == 'learning_summary':
                from core.models_user_learning import UserSkill
                from django.db.models import Count, Avg
                qs = UserSkill.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                agg = qs.aggregate(avg_proficiency=Avg('confidence'))
                category_counts = dict(qs.values_list('category').annotate(c=Count('id')).values_list('category', 'c'))
                return {
                    'action': 'learning_summary',
                    'total_skills': qs.count(),
                    'avg_confidence': float(agg['avg_proficiency'] or 0),
                    'by_category': category_counts,
                }

            return {'error': f'Unknown profile_tool action: {action}'}

        except Exception as e:
            logger.error(f"[PROFILE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Self-Awareness Tool ─────────────────────────────────
    def _handle_self_awareness(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """System self-awareness metrics, reports, evolution."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 10)), 30)

        try:
            from self_awareness.models import SystemMetrics, SelfAnalysisReport, SystemEvolution

            if action == 'metrics':
                latest = SystemMetrics.objects.order_by('-timestamp').first()
                if not latest:
                    return {'action': 'metrics', 'metrics': None, 'message': 'No metrics recorded yet'}
                return {
                    'action': 'metrics',
                    'metrics': {
                        'timestamp': latest.timestamp.isoformat() if latest.timestamp else None,
                        'cpu_usage': float(latest.cpu_usage) if latest.cpu_usage else None,
                        'memory_usage': float(latest.memory_usage) if latest.memory_usage else None,
                        'active_agents': latest.active_agents,
                        'pending_tasks': latest.pending_tasks,
                        'error_count': latest.error_count,
                        'self_analysis_score': float(latest.self_analysis_score) if latest.self_analysis_score else None,
                    },
                }

            if action == 'reports':
                reports = SelfAnalysisReport.objects.order_by('-timestamp')[:limit]
                return {
                    'action': 'reports',
                    'count': len(reports),
                    'reports': [{
                        'id': str(r.id) if hasattr(r, 'id') else str(r.timestamp),
                        'analysis_type': r.analysis_type,
                        'score': float(r.score) if r.score else None,
                        'critical_issues': r.critical_issues,
                        'warning_issues': r.warning_issues,
                        'confidence': float(r.confidence) if r.confidence else None,
                        'timestamp': r.timestamp.isoformat() if r.timestamp else None,
                    } for r in reports],
                }

            if action == 'evolution':
                evolutions = SystemEvolution.objects.order_by('-timestamp')[:limit]
                return {
                    'action': 'evolution',
                    'count': len(evolutions),
                    'evolutions': [{
                        'id': str(e.id) if hasattr(e, 'id') else str(e.timestamp),
                        'evolution_type': e.evolution_type,
                        'status': e.status,
                        'title': e.title or '',
                        'confidence_score': float(e.confidence_score) if e.confidence_score else None,
                        'priority': e.priority or '',
                        'timestamp': e.timestamp.isoformat() if e.timestamp else None,
                    } for e in evolutions],
                }

            if action == 'stats':
                reports = SelfAnalysisReport.objects.all()
                evolutions = SystemEvolution.objects.all()
                latest_metrics = SystemMetrics.objects.order_by('-timestamp').first()
                return {
                    'action': 'stats',
                    'total_reports': reports.count(),
                    'total_evolutions': evolutions.count(),
                    'latest_self_analysis_score': float(latest_metrics.self_analysis_score) if latest_metrics and latest_metrics.self_analysis_score else None,
                }

            return {'error': f'Unknown self_awareness_tool action: {action}'}

        except Exception as e:
            logger.error(f"[SELF_AWARENESS] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: ATS Tool ────────────────────────────────────────────
    def _handle_ats(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """ATS keyword mappings, resume optimizations, templates."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_ats_optimization import ATSKeywordMapping, ResumeOptimizationLog, PersonaResumeTemplate
            from django.db.models import Sum, Avg, Count

            if action == 'keywords':
                qs = ATSKeywordMapping.objects.order_by('-job_frequency')
                category_filter = payload.get('category')
                if category_filter:
                    qs = qs.filter(category=category_filter)
                keywords = qs[:limit]
                return {
                    'action': 'keywords',
                    'count': len(keywords),
                    'keywords': [{
                        'id': str(k.id),
                        'canonical': k.canonical,
                        'category': k.category or '',
                        'variations': (k.variations or [])[:3],
                        'resume_frequency': float(k.resume_frequency) if k.resume_frequency else None,
                        'job_frequency': float(k.job_frequency) if k.job_frequency else None,
                        'interview_correlation': float(k.interview_correlation) if k.interview_correlation else None,
                    } for k in keywords],
                }

            if action == 'optimizations':
                qs = ResumeOptimizationLog.objects.order_by('-created_at')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                opts = qs[:limit]
                return {
                    'action': 'optimizations',
                    'count': len(opts),
                    'optimizations': [{
                        'id': str(o.id),
                        'job_title_target': o.job_title_target or '',
                        'industry': o.industry or '',
                        'initial_ats_score': float(o.initial_ats_score) if o.initial_ats_score else None,
                        'final_ats_score': float(o.final_ats_score) if o.final_ats_score else None,
                        'current_stage': o.current_stage or '',
                        'revenue_cents': o.revenue_cents or 0,
                    } for o in opts],
                }

            if action == 'templates':
                templates = PersonaResumeTemplate.objects.filter(is_active=True).order_by('name')[:limit]
                return {
                    'action': 'templates',
                    'count': len(templates),
                    'templates': [{
                        'id': str(t.id),
                        'name': t.name,
                        'industry': t.industry or '',
                        'experience_level': t.experience_level or '',
                        'template_type': t.template_type or '',
                        'price_cents': t.price_cents or 0,
                        'avg_ats_score_improvement': float(t.avg_ats_score_improvement) if t.avg_ats_score_improvement else None,
                    } for t in templates],
                }

            if action == 'stats':
                keywords = ATSKeywordMapping.objects.all()
                opts = ResumeOptimizationLog.objects.all()
                if user_id:
                    opts = opts.filter(user_id=user_id)
                agg = opts.aggregate(
                    total_revenue=Sum('revenue_cents'),
                    avg_init=Avg('initial_ats_score'),
                    avg_final=Avg('final_ats_score'),
                )
                avg_init = agg['avg_init']
                avg_final = agg['avg_final']
                avg_improvement = float((avg_final or 0) - (avg_init or 0)) if avg_init and avg_final else None
                return {
                    'action': 'stats',
                    'total_keywords': keywords.count(),
                    'total_optimizations': opts.count(),
                    'avg_score_improvement': avg_improvement,
                    'total_revenue_cents': agg['total_revenue'] or 0,
                    'active_templates': PersonaResumeTemplate.objects.filter(is_active=True).count(),
                }

            return {'error': f'Unknown ats_tool action: {action}'}

        except Exception as e:
            logger.error(f"[ATS] {action} error: {e}", exc_info=True)
            return {'error': str(e)}


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
