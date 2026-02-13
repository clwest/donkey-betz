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
        self.register("audio_generation_agent", self._handle_agent_tool)
        self.register("three_d_generation_agent", self._handle_agent_tool)
        self.register("character_training_agent", self._handle_agent_tool)
        self.register("talking_character_agent", self._handle_agent_tool)

        # Research tools
        self.register("web_search", self._handle_web_search)
        self.register("competitor_analysis_agent", self._handle_agent_tool)
        self.register("customer_research_agent", self._handle_agent_tool)
        self.register("brand_strategy_agent", self._handle_agent_tool)
        self.register("content_strategy_agent", self._handle_agent_tool)
        self.register("marketing_strategy_agent", self._handle_agent_tool)
        self.register("content_writer_agent", self._handle_agent_tool)

        # ML Pipeline tools
        self.register("opportunity_manager_tool", self._handle_opportunity_manager)
        self.register("task_manager_tool", self._handle_task_manager)
        self.register("pipeline_orchestrator_tool", self._handle_pipeline_orchestrator)
        self.register("revenue_tracker_tool", self._handle_revenue_tracker)
        self.register("ml_analysis", self._handle_ml_analysis)

        # Universal tools
        self.register("universal_agent_tool", self._handle_universal_agent)
        self.register("workspace_tool", self._handle_workspace)

        # Body system tools
        self.register("get_body_vitals", self._handle_body_vitals)
        self.register("check_resource_budget", self._handle_check_budget)
        self.register("get_system_alerts", self._handle_system_alerts)

        # Intelligence tools
        self.register("predictions_tool", self._handle_predictions)
        self.register("gates_tool", self._handle_gates)
        self.register("pilots_tool", self._handle_pilots)
        self.register("human_decisions_tool", self._handle_human_decisions)
        self.register("reasoning_engine_tool", self._handle_reasoning_engine)

        # Session 940: Boardroom tools for PA to act on pending items
        self.register("boardroom_tool", self._handle_boardroom)

        # Session 943: Brainstorm search tool for accessing Discussion/Panel insights
        self.register("brainstorm_tool", self._handle_brainstorm)

        # Session 943: Content review tool for accessing Deliverables awaiting human review
        self.register("content_review_tool", self._handle_content_review)

        # Session 993: Blog generation via deliberation pipeline
        self.register("generate_blog_tool", self._handle_generate_blog)

        # Session 943: Initiative tool for PA access to project pipeline
        self.register("initiative_tool", self._handle_initiative)

        # Workflow tools
        self.register("workflow_orchestration_agent", self._handle_agent_tool)
        self.register("create_brand_video", self._handle_agent_tool)
        self.register("create_project_from_research", self._handle_agent_tool)
        self.register("strategic_review", self._handle_agent_tool)
        self.register("coleadership_agent", self._handle_agent_tool)

        # Legal tools
        self.register("legal_doc_drafter_agent", self._handle_agent_tool)

        # Session 948: New PA enhancement tools
        self.register("spider_data_tool", self._handle_spider_data)
        self.register("execution_history_tool", self._handle_execution_history)
        self.register("learning_patterns_tool", self._handle_learning_patterns)
        self.register("feedback_tool", self._handle_feedback)

        # Session 969: Live telemetry tools for PA self-awareness
        self.register("recent_activity_tool", self._handle_recent_activity)
        self.register("system_health_tool", self._handle_system_health)
        self.register("error_summary_tool", self._handle_error_summary)

        # Session 970: Surgical moves verification tool
        self.register("surgical_moves_status_tool", self._handle_surgical_moves_status)

        # Session 979: Stock intelligence tool for PA access to market data
        self.register("stock_intelligence_tool", self._handle_stock_intelligence)

        # Session 995B: Sports betting intelligence tool
        self.register("sports_betting_tool", self._handle_sports_betting)

        # Session 973: Status snapshot for broad system overview
        self.register("status_snapshot_tool", self._handle_status_snapshot)

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

            logger.info(f"[{trace_id}] Tool {tool_name} completed in {latency_ms}ms")

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
        """Generic handler for agent-based tools."""
        from core.agents.registry import get_agent_registry

        # Map tool name to agent name
        agent_name = self._tool_to_agent_name(tool_name)

        registry = get_agent_registry()
        agent_metadata = registry.get_agent(agent_name)

        if not agent_metadata:
            raise ValueError(f"Agent '{agent_name}' not found for tool '{tool_name}'")

        # Extract task from payload
        task = payload.get('task') or payload.get('prompt') or payload.get('query', '')
        context = payload.get('context', {})

        # Session 948: Use registry.execute_agent() which properly handles agent instantiation
        # The old code incorrectly called .run() on metadata dict
        task_data = {
            'task': task,
            'context': context,
        }
        result = registry.execute_agent(agent_name, task_data)

        return {
            'agent': agent_name,
            'output': result if result else 'Agent execution completed',
            'success': True if result else False,
        }

    def _tool_to_agent_name(self, tool_name: str) -> str:
        """Map tool name to agent class name."""
        mappings = {
            'image_generation_agent': 'ImageAgent',
            'image_editing_agent': 'ImageEditingAgent',
            'video_generation_agent': 'VideoAgent',
            'video_editing_agent': 'VideoEditingAgent',
            'audio_generation_agent': 'AudioAgent',
            'three_d_generation_agent': 'ThreeDAgent',
            'character_training_agent': 'CharacterTrainingAgent',
            'talking_character_agent': 'TalkingCharacterAgent',
            'competitor_analysis_agent': 'CompetitorAnalysisAgent',
            'customer_research_agent': 'CustomerResearchAgent',
            'brand_strategy_agent': 'BrandStrategyAgent',
            'content_strategy_agent': 'ContentStrategyAgent',
            'marketing_strategy_agent': 'MarketingStrategyAgent',
            'content_writer_agent': 'ContentWriterAgent',
            'workflow_orchestration_agent': 'WorkflowAgent',
            'create_brand_video': 'WorkflowAgent',
            'create_project_from_research': 'WorkflowAgent',
            'strategic_review': 'StrategyAgent',
            'coleadership_agent': 'CoLeadershipAgent',
            'legal_doc_drafter_agent': 'LegalDocDrafterAgent',
        }
        return mappings.get(tool_name, tool_name.replace('_agent', '').title() + 'Agent')

    def _handle_web_search(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle web search tool."""
        from core.agents.registry import get_agent_registry

        registry = get_agent_registry()
        query = payload.get('query', '')

        # Session 948: Use execute_agent instead of calling .run() on metadata dict
        task_data = {'task': f"Search for: {query}"}
        result = registry.execute_agent('ResearchAgent', task_data)

        if result:
            return {
                'query': query,
                'results': f'Research task queued (execution ID: {result}). '
                           f'The ResearchAgent will process this asynchronously.',
                'execution_id': result,
            }
        return {
            'query': query,
            'results': 'ResearchAgent is not available. Try rephrasing your question '
                       'for a direct answer.',
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
            opp_id = payload.get('opportunity_id')
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

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, get, stats, update_status"
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

        else:
            raise ValueError(f"Unknown action: {action}")

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
        from core.models_unified_system import Initiative

        action = payload.get('action', 'status')

        if action == 'status':
            # Get real pipeline stats from Initiative model
            total = Initiative.objects.count()
            by_stage = {}
            for stage in range(1, 6):
                by_stage[f'stage_{stage}'] = Initiative.objects.filter(stage=stage).count()
            active = Initiative.objects.filter(stage__lt=5, status='active').count()

            return {
                'action': 'status',
                'pipeline': 'operational',
                'initiatives_total': total,
                'initiatives_active': active,
                'by_stage': by_stage,
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
                base_qs.values('source').annotate(
                    total=Sum('amount')
                ).values_list('source', 'total')
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
                'id', 'amount', 'source', 'status', 'created_at', 'description'
            ))

            # Session 987: Serialize UUIDs and datetimes
            for r in revenues:
                r['id'] = str(r['id'])
                if r.get('created_at'):
                    r['created_at'] = r['created_at'].isoformat()

            return {'action': 'list', 'count': len(revenues), 'revenues': revenues}

        else:
            raise ValueError(f"Unknown action: {action}")

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
        """Handle universal agent tool - invoke any agent by name."""
        from core.agents.registry import get_agent_registry

        agent_name = payload.get('agent_name')
        task = payload.get('task', '')
        context = payload.get('context', {})

        if not agent_name:
            raise ValueError("agent_name is required")

        registry = get_agent_registry()
        agent_metadata = registry.get_agent(agent_name)

        if not agent_metadata:
            raise ValueError(f"Agent '{agent_name}' not found")

        # Session 948: Use execute_agent instead of calling .run() on metadata dict
        task_data = {'task': task, 'context': context}
        result = registry.execute_agent(agent_name, task_data)

        return {
            'agent': agent_name,
            'output': result if result else 'Agent execution completed',
            'success': True if result else False,
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

        action = payload.get('action', 'list')
        manager = get_workspace_manager()

        if action == 'list':
            workspaces = manager.list_workspaces()
            return {'action': 'list', 'workspaces': workspaces}

        elif action == 'status':
            status = manager.get_status()
            return {'action': 'status', 'status': status}

        else:
            raise ValueError(f"Unknown action: {action}")

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
            result = vitals.get_all_vitals()
        else:
            result = vitals.get_vitals_for_systems(systems)

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
        lungs = vitals.get_vitals_for_systems(['lungs'])

        return {
            'estimated_tokens': estimated_tokens,
            'estimated_cost': estimated_cost,
            'budget_status': lungs.get('lungs', {}).get('status', 'unknown'),
            'approved': True,  # For now, always approve
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
        limit = payload.get('limit', 20)

        if action == 'list':
            gates = list(
                PilotReadinessGate.objects.select_related('decision').order_by('-created_at')[:limit].values(
                    'id', 'summary', 'status', 'risk_level', 'created_at', 'decision__topic'
                )
            )
            # Flatten decision__topic to topic for cleaner response
            # Session 987: Serialize UUIDs and datetimes for clean display
            for gate in gates:
                gate['topic'] = gate.pop('decision__topic', '')
                gate['id'] = str(gate['id'])
                if gate.get('created_at'):
                    gate['created_at'] = gate['created_at'].isoformat()
            return {'action': 'list', 'count': len(gates), 'gates': gates}

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
        limit = payload.get('limit', 20)

        if action == 'list':
            pilots = list(
                PilotExecution.objects.order_by('-created_at')[:limit].values(
                    'id', 'name', 'status', 'outcome', 'created_at'
                )
            )
            # Session 987: Serialize UUIDs and datetimes for clean display
            for pilot in pilots:
                pilot['id'] = str(pilot['id'])
                if pilot.get('created_at'):
                    pilot['created_at'] = pilot['created_at'].isoformat()
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

        else:
            raise ValueError(f"Unknown action: {action}")

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
                raise ValueError(f"Attention item {item_id} not found or not pending")

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

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: stats, list_attention, list_decisions, approve_attention, ignore_attention, promote_decision, reject_decision, get_triage_batch")

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

        elif action == 'stats':
            days = payload.get('days', 30)

            result = brainstorm_search_service.get_stats(days=days)
            return {'action': 'stats', **result}

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: search, recent, details, by_category, stats"
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
        limit = payload.get('limit', 10)
        content_type = payload.get('type')  # blog, document, report, analysis, etc.
        category = payload.get('category')  # Marketing, Development, etc.

        # Session 958: If type is 'blog', query SelfBlog model instead of Deliverable
        # SelfBlog contains actual blog posts (773+ in production)
        if content_type == 'blog':
            return self._handle_blog_query(action, limit, category, payload, user_id)

        # Build base queryset - filter by user if available
        base_qs = Deliverable.objects.all()
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)

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

        elif action == 'stats':
            # Get statistics on content requiring review
            ready_count = base_qs.filter(status='ready').count()
            draft_count = base_qs.filter(status='draft').count()
            published_count = base_qs.filter(status='published').count()

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
            }

        elif action == 'details':
            deliverable_id = payload.get('id')
            if not deliverable_id:
                raise ValueError("id is required for details action")

            deliverable = base_qs.filter(id=deliverable_id).first()
            if not deliverable:
                raise ValueError(f"Deliverable {deliverable_id} not found")

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
                f"Unknown action: {action}. Valid actions: list, stats, details, publish, archive"
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
                    'id', 'title', 'category', 'status', 'created_at',
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
                    'id', 'title', 'category', 'status', 'created_at',
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

            return {
                'action': 'details',
                'source': 'SelfBlog',
                'blog': {
                    'id': str(blog.id),
                    'title': blog.title,
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
            if source.initiative_id:
                siblings = SelfBlog.objects.filter(
                    initiative_id=source.initiative_id
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

            blog = base_qs.filter(id=blog_id, status__in=['approved', 'pending_review']).first()
            if not blog:
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

        If a topic is provided, runs ContentDeliberationRunner.run_blog() synchronously.
        If no topic, dispatches the Celery task for background generation.
        """
        topic = payload.get('topic')
        tone = payload.get('tone', 'enthusiastic')

        if topic:
            # Synchronous — run the full deliberation pipeline
            from core.services.content_deliberation_runner import ContentDeliberationRunner
            runner = ContentDeliberationRunner()
            result = runner.run_blog(topic, voice=tone)

            return {
                'action': 'generate_blog',
                'mode': 'synchronous',
                'topic': topic,
                'tone': tone,
                'status': result.get('status', 'unknown'),
                'decision': result.get('decision', 'unknown'),
                'selfblog_id': str(result['selfblog_id']) if result.get('selfblog_id') else None,
                'deliberation_session_id': str(result['deliberation_session_id']) if result.get('deliberation_session_id') else None,
                'summary': result.get('summary', {}),
            }
        else:
            # Async — dispatch to Celery for background generation
            from core.tasks import generate_self_blog_deliberation_task
            task = generate_self_blog_deliberation_task.delay(tone=tone)

            return {
                'action': 'generate_blog',
                'mode': 'async',
                'tone': tone,
                'task_id': str(task.id),
                'message': 'Blog generation queued via deliberation pipeline. Check back shortly.',
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

            # Filter by purpose
            purpose_filter = payload.get('purpose')
            if purpose_filter:
                qs = qs.filter(purpose=purpose_filter.lower())

            # Filter by program
            program_filter = payload.get('program')
            if program_filter:
                qs = qs.filter(program=program_filter.lower())

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
                    'stage': stage_filter,
                    'purpose': purpose_filter,
                    'program': program_filter,
                    'owner': owner_filter,
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
                        'items': [{'name': i.name, 'stage': i.current_stage,
                                   'purpose': i.purpose} for i in real[:10]]
                    },
                    'stalled': {
                        'count': len(stalled),
                        'items': [{'name': i.name, 'created_at': str(i.created_at)[:10],
                                   'purpose': i.purpose} for i in stalled[:5]]
                    },
                    'noise': {
                        'count': len(noise),
                        'items': [{'name': i.name} for i in noise[:5]]
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

            if initiative_id:
                initiative = Initiative.objects.filter(id=initiative_id).first()
            else:
                initiative = Initiative.objects.filter(name__icontains=name_query).first()

            if not initiative:
                raise ValueError(f"Initiative not found")

            # Get action items
            action_items = list(
                InitiativeActionItem.objects.filter(initiative=initiative)
                .order_by('-priority', 'status', '-created_at')[:10]
                .values('id', 'title', 'status', 'priority', 'due_date', 'assigned_agent')
            )

            # Session 987: Serialize UUIDs and datetimes
            for ai in action_items:
                ai['id'] = str(ai['id'])
                if ai.get('due_date'):
                    ai['due_date'] = ai['due_date'].isoformat()

            # Get stage info
            stages = list(
                initiative.stages.all()
                .order_by('stage_number')
                .values('stage_number', 'status', 'completed_at')
            )

            for s in stages:
                if s.get('completed_at'):
                    s['completed_at'] = s['completed_at'].isoformat()

            # Session 996: Resolve owner
            owner_display = initiative.owner_agent or None
            if initiative.owner_id:
                owner_display = initiative.owner.username if initiative.owner else None

            return {
                'action': 'details',
                'id': str(initiative.id),
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
            status_filter = payload.get('item_status', 'pending')
            priority_filter = payload.get('priority')

            qs = InitiativeActionItem.objects.select_related('initiative')

            if status_filter and status_filter != 'all':
                qs = qs.filter(status=status_filter)

            if priority_filter:
                qs = qs.filter(priority=priority_filter)

            items = []
            for item in qs.order_by('-priority', '-created_at')[:limit]:
                items.append({
                    'id': str(item.id),
                    'title': item.title,
                    'status': item.status,
                    'priority': item.priority,
                    'due_date': item.due_date.isoformat() if item.due_date else None,
                    'assigned_agent': item.assigned_agent,
                    'initiative_id': str(item.initiative_id),
                    'initiative_name': item.initiative.name if item.initiative else 'Unknown',
                })

            return {
                'action': 'action_items',
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'status': status_filter,
                    'priority': priority_filter,
                }
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

            return {
                'action': 'update_status',
                'id': str(initiative.id),
                'name': initiative.name,
                'old_status': old_status,
                'new_status': new_status,
                'success': True,
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
                new_owner = user.username
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

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, details, "
                f"action_items, flow_metrics, update_status, advance, complete_action_item, assign_owner"
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
            items = list(
                SpiderData.objects.filter(
                    spider_name__icontains=spider_name,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'spider_name', 'data_type', 'source_url',
                    'embedding_text', 'relevance_score', 'created_at'
                )
            )

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
            task = run_spider_by_category.delay(category=target)

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

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: recent, by_agent, stats, failures"
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
        payload: Dict[str, Any],
        user: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Session 948: Handle user feedback viewing and management.

        Actions:
        - list: List feedback items (optionally filtered by status)
        - stats: Get feedback statistics
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
                f"Unknown action: {action}. Valid actions: list, stats, update"
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

    def _handle_system_health(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 969: System health tool — aggregate health snapshot.

        Answers "How's the system?" with heartbeat, component, celery, and spider freshness data.

        Actions:
        - overview: High-level health assessment (default)
        - components: Detailed per-component breakdown
        """
        from django.utils import timezone
        from django.db.models import Count
        from datetime import timedelta, date

        action = payload.get('action', 'overview')
        now = timezone.now()

        health = {}

        # 1. Latest heartbeat
        try:
            from core.models_heart import HeartBeat
            hb = HeartBeat.objects.order_by('-recorded_at').first()
            if hb:
                age_seconds = (now - hb.recorded_at).total_seconds()
                health['heartbeat'] = {
                    'overall_status': hb.overall_status,
                    'health_score': hb.health_score,
                    'recorded_at': hb.recorded_at.isoformat(),
                    'age_seconds': int(age_seconds),
                    'is_alive': hb.is_alive,
                }
            else:
                health['heartbeat'] = {'status': 'no_data'}
        except Exception as e:
            health['heartbeat'] = {'error': str(e)}

        # 2. Component statuses
        try:
            from core.models_heart import ComponentStatus
            components = list(
                ComponentStatus.objects.all().values(
                    'component', 'display_name', 'status', 'is_healthy',
                    'last_check', 'last_error'
                )
            )
            for c in components:
                if c.get('last_check'):
                    c['last_check'] = c['last_check'].isoformat()
            healthy_count = sum(1 for c in components if c.get('is_healthy'))
            health['components'] = {
                'total': len(components),
                'healthy': healthy_count,
                'unhealthy': len(components) - healthy_count,
            }
            if action == 'components':
                health['components']['details'] = components
        except Exception as e:
            health['components'] = {'error': str(e)}

        # 3. Celery health (last 1 hour) — Session 983: CeleryTaskEvent
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            one_hour_ago = now - timedelta(hours=1)
            task_qs = CeleryTaskEvent.objects.filter(started_at__gte=one_hour_ago)
            by_status = dict(
                task_qs.values('status')
                .annotate(n=Count('id'))
                .values_list('status', 'n')
            )
            total = sum(by_status.values())
            successes = by_status.get('SUCCESS', 0)
            success_rate = (successes / total * 100) if total > 0 else None
            health['celery'] = {
                'last_hour_total': total,
                'by_status': by_status,
                'success_rate_pct': round(success_rate, 1) if success_rate is not None else None,
            }
        except Exception as e:
            health['celery'] = {'error': str(e)}

        # 4. Tool call health (today)
        try:
            from core.models_tool_calls import ToolCallAggregate
            today = date.today()
            aggs = ToolCallAggregate.objects.filter(date=today)
            total_calls = sum(a.total_calls for a in aggs)
            success_calls = sum(a.success_calls for a in aggs)
            tc_rate = (success_calls / total_calls * 100) if total_calls > 0 else None
            health['tool_calls'] = {
                'today_total': total_calls,
                'today_success': success_calls,
                'success_rate_pct': round(tc_rate, 1) if tc_rate is not None else None,
            }
        except Exception as e:
            health['tool_calls'] = {'error': str(e)}

        # 5. Spider freshness (last 2 hours)
        try:
            from core.models_unified_system import SpiderData
            two_hours_ago = now - timedelta(hours=2)
            recent_count = SpiderData.objects.filter(created_at__gte=two_hours_ago).count()
            latest = SpiderData.objects.order_by('-created_at').first()
            health['spider_freshness'] = {
                'items_last_2h': recent_count,
                'latest_at': latest.created_at.isoformat() if latest else None,
            }
        except Exception as e:
            health['spider_freshness'] = {'error': str(e)}

        # Compute overall assessment
        assessment = 'healthy'
        reasons = []

        hb_data = health.get('heartbeat', {})
        if hb_data.get('status') == 'no_data' or hb_data.get('error'):
            assessment = 'critical'
            reasons.append('No heartbeat data')
        elif hb_data.get('age_seconds', 0) > 600:  # >10 min stale
            assessment = 'degraded'
            reasons.append(f"Heartbeat stale ({hb_data['age_seconds']}s ago)")
        elif hb_data.get('overall_status') not in ('healthy', 'HEALTHY', None):
            assessment = 'degraded'
            reasons.append(f"Heartbeat status: {hb_data.get('overall_status')}")

        celery_data = health.get('celery', {})
        celery_rate = celery_data.get('success_rate_pct')
        if celery_rate is not None and celery_rate < 80:
            assessment = 'degraded' if assessment != 'critical' else 'critical'
            reasons.append(f"Celery success rate low ({celery_rate}%)")

        comp_data = health.get('components', {})
        if comp_data.get('unhealthy', 0) > 0:
            if comp_data['unhealthy'] >= comp_data.get('total', 1) / 2:
                assessment = 'critical'
            elif assessment == 'healthy':
                assessment = 'degraded'
            reasons.append(f"{comp_data['unhealthy']} unhealthy components")

        health['overall_assessment'] = assessment
        health['assessment_reasons'] = reasons if reasons else ['All systems nominal']

        return {
            'action': action,
            'health': health,
        }

    def _handle_error_summary(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 969: Error summary tool — recent failures and patterns.

        Answers "Any errors?" with failure signatures, detections, failed tool calls, and celery failures.

        Actions:
        - summary: High-level error counts and top patterns (default)
        - detailed: Full error details with individual items
        """
        from django.utils import timezone
        from django.db.models import Count
        from datetime import timedelta

        action = payload.get('action', 'summary')
        hours = payload.get('hours', 4)
        cutoff = timezone.now() - timedelta(hours=hours)
        item_limit = 5 if action == 'summary' else 20

        errors = {}
        total_errors = 0

        # 1. Active failure signatures
        try:
            from core.models_diagnostic_pipeline import FailureSignature
            sigs = list(
                FailureSignature.objects.filter(
                    status='active',
                    last_seen_at__gte=cutoff
                ).order_by('-occurrence_count')[:item_limit]
                .values('signature', 'occurrence_count', 'last_seen_at', 'description')
            )
            for item in sigs:
                if item.get('last_seen_at'):
                    item['last_seen_at'] = item['last_seen_at'].isoformat()
            errors['failure_signatures'] = {
                'count': len(sigs),
                'items': sigs,
            }
            total_errors += len(sigs)
        except Exception as e:
            errors['failure_signatures'] = {'error': str(e)}

        # 2. Failure detections grouped by source_type
        try:
            from core.models_diagnostic_pipeline import FailureDetection
            det_qs = FailureDetection.objects.filter(detected_at__gte=cutoff)
            by_source = dict(
                det_qs.values('source_type')
                .annotate(n=Count('id'))
                .values_list('source_type', 'n')
            )
            det_total = sum(by_source.values())
            errors['failure_detections'] = {
                'total': det_total,
                'by_source_type': by_source,
            }
            total_errors += det_total
        except Exception as e:
            errors['failure_detections'] = {'error': str(e)}

        # 3. Failed tool calls grouped by agent+tool
        try:
            from core.models_tool_calls import ToolCallRecord
            failed_tc = ToolCallRecord.objects.filter(
                success=False,
                created_at__gte=cutoff
            )
            by_agent_tool = list(
                failed_tc.values('agent_name', 'tool_name')
                .annotate(n=Count('id'))
                .order_by('-n')[:item_limit]
            )
            tc_total = failed_tc.count()
            errors['failed_tool_calls'] = {
                'total': tc_total,
                'by_agent_tool': by_agent_tool,
            }
            total_errors += tc_total
        except Exception as e:
            errors['failed_tool_calls'] = {'error': str(e)}

        # 4. Failed Celery tasks grouped by task name — Session 983: CeleryTaskEvent
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            failed_tasks = CeleryTaskEvent.objects.filter(
                status='FAILURE',
                started_at__gte=cutoff,
            )
            by_task = dict(
                failed_tasks.values('task_name')
                .annotate(n=Count('id'))
                .order_by('-n')[:item_limit]
                .values_list('task_name', 'n')
            )
            ft_total = failed_tasks.count()
            errors['failed_celery_tasks'] = {
                'total': ft_total,
                'by_task_name': by_task,
            }
            total_errors += ft_total
        except Exception as e:
            errors['failed_celery_tasks'] = {'error': str(e)}

        # Compute severity
        if total_errors == 0:
            severity = 'none'
        elif total_errors <= 5:
            severity = 'low'
        elif total_errors <= 20:
            severity = 'moderate'
        else:
            severity = 'high'

        return {
            'action': action,
            'hours_back': hours,
            'total_errors': total_errors,
            'severity': severity,
            'errors': errors,
        }

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
                    items.append({
                        'id': str(p.id),
                        'matchup': f"{p.away_team} @ {p.home_team}" if hasattr(p, 'home_team') else str(p),
                        'predicted_winner': p.predicted_winner if hasattr(p, 'predicted_winner') else '',
                        'confidence': p.confidence if hasattr(p, 'confidence') else 0,
                        'sport_name': p.sport_name if hasattr(p, 'sport_name') else '',
                        'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None,
                    })
                return {'action': 'predictions', 'items': items, 'total': total}
            except Exception as e:
                logger.warning(f"MLPrediction query failed: {e}")
                return {'action': 'predictions', 'items': [], 'total': 0, 'error': str(e)}

        elif action == 'sharp_action':
            try:
                from core.agents.markets.sharp_action_detector import SharpActionDetector
                agent = SharpActionDetector()
                result = agent.execute(
                    task="Identify sharp betting action and stale lines",
                    context={}
                )
                if result.success:
                    signals = result.data.get('signals', [])
                    return {
                        'action': 'sharp_action',
                        'items': signals[:limit],
                        'total': len(signals),
                    }
                return {'action': 'sharp_action', 'items': [], 'total': 0, 'error': result.error}
            except Exception as e:
                logger.warning(f"SharpActionDetector failed: {e}")
                return {'action': 'sharp_action', 'items': [], 'total': 0, 'error': str(e)}

        elif action == 'line_movements':
            try:
                from core.agents.markets.line_movement_analyzer import LineMovementAnalyzer
                agent = LineMovementAnalyzer()
                result = agent.execute(
                    task="Detect sharp money line movements",
                    context={}
                )
                if result.success:
                    movements = result.data.get('movements', [])
                    return {
                        'action': 'line_movements',
                        'items': movements[:limit],
                        'total': len(movements),
                    }
                return {'action': 'line_movements', 'items': [], 'total': 0, 'error': result.error}
            except Exception as e:
                logger.warning(f"LineMovementAnalyzer failed: {e}")
                return {'action': 'line_movements', 'items': [], 'total': 0, 'error': str(e)}

        elif action == 'wagers':
            from core.models_betting import PlacedWager
            qs = PlacedWager.objects.all().order_by('-created_at')
            if user_id:
                qs = qs.filter(user_id=user_id)
            total = qs.count()
            items = []
            for w in qs[:limit]:
                items.append({
                    'id': str(w.id),
                    'description': w.description if hasattr(w, 'description') else str(w),
                    'status': w.status,
                    'stake': float(w.stake) if hasattr(w, 'stake') and w.stake else 0,
                    'potential_payout': float(w.potential_payout) if hasattr(w, 'potential_payout') and w.potential_payout else 0,
                    'created_at': w.created_at.isoformat() if hasattr(w, 'created_at') and w.created_at else None,
                })
            return {'action': 'wagers', 'items': items, 'total': total}

        elif action in ('brief', 'live_odds'):
            try:
                from core.services.sports_betting_coordinator import SportsBettingCoordinator
                coordinator = SportsBettingCoordinator()
                brief = coordinator.generate_brief()
                return {
                    'action': action,
                    'executive_summary': brief.get('executive_summary', ''),
                    'top_plays': brief.get('top_plays', []),
                    'agents_run': brief.get('agents_run', []),
                    'generation_time_seconds': brief.get('generation_time_seconds', 0),
                }
            except Exception as e:
                logger.warning(f"SportsBettingCoordinator failed: {e}")
                return {'action': action, 'top_plays': [], 'error': str(e)}

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

        cache.set(cache_key, snapshot, 60)
        logger.info(f"[{trace_id}] Status snapshot generated and cached")
        return snapshot


# Singleton instance
_tool_dispatcher: Optional[ToolDispatcher] = None


def get_tool_dispatcher() -> ToolDispatcher:
    """Get the singleton ToolDispatcher instance."""
    global _tool_dispatcher
    if _tool_dispatcher is None:
        _tool_dispatcher = ToolDispatcher()
    return _tool_dispatcher
