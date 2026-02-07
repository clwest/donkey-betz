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

        return {
            'query': query,
            'results': result if result else 'No results found',
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

        else:
            raise ValueError(f"Unknown action: {action}")

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
            for gate in gates:
                gate['topic'] = gate.pop('decision__topic', '')
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
            return {'action': 'list', 'count': len(pilots), 'pilots': pilots}

        elif action == 'running':
            pilots = list(
                PilotExecution.objects.filter(status='running').values(
                    'id', 'name', 'status', 'created_at'
                )
            )
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
                .order_by('-count')[:5]
                .values_list('item_type', 'count')
            )

            # Get decision stats
            decision_count = decisions_qs.count()
            decisions_by_type = dict(
                decisions_qs.values('decision_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
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
                    logger.debug(f"Failed to record learning: {e}")

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
                    logger.debug(f"Failed to record learning: {e}")

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
                    logger.debug(f"Failed to record learning: {e}")

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
                    logger.debug(f"Failed to record learning: {e}")

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

        else:
            raise ValueError(
                f"Unknown action for blog query: {action}. Valid actions: list, recent, stats, details"
            )

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

            # Order by priority score (impact*0.4 + urgency*0.2 + confidence*0.2 + revenue*0.2)
            total_count = qs.count()
            items = list(
                qs.order_by('-impact_score', '-urgency', '-created_at')[:limit].values(
                    'id', 'name', 'description', 'status', 'current_stage',
                    'purpose', 'program', 'impact_score', 'urgency',
                    'confidence', 'revenue_potential', 'created_at',
                    'updated_at', 'last_activity_at'
                )
            )

            # Add action item counts (including critical)
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
                }
            }

        elif action == 'stats':
            # Get pipeline overview
            total = Initiative.objects.count()
            active = Initiative.objects.filter(status='ACTIVE').count()
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

            # Get stage info
            stages = list(
                initiative.stages.all()
                .order_by('stage_number')
                .values('stage_number', 'status', 'completed_at')
            )

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

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, details, action_items"
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
            qs = SpiderData.objects.filter(created_at__gte=cutoff)

            if spider_name:
                qs = qs.filter(spider_name__icontains=spider_name)
            if category:
                qs = qs.filter(category__icontains=category)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'spider_name', 'category', 'title', 'url',
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

            items = list(
                SpiderData.objects.filter(
                    spider_name__icontains=spider_name,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'spider_name', 'category', 'title', 'url',
                    'content', 'relevance_score', 'created_at'
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
                # List available categories
                category_counts = dict(
                    SpiderData.objects.filter(created_at__gte=cutoff)
                    .values('category')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:20]
                    .values_list('category', 'count')
                )
                return {
                    'action': 'by_category',
                    'available_categories': category_counts,
                    'message': 'Specify category to get data from that category'
                }

            items = list(
                SpiderData.objects.filter(
                    category__icontains=category,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'spider_name', 'category', 'title', 'url',
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

            from django.db.models import Q
            items = list(
                SpiderData.objects.filter(
                    Q(title__icontains=keyword) | Q(content__icontains=keyword),
                    created_at__gte=cutoff
                ).order_by('-relevance_score', '-created_at')[:limit].values(
                    'id', 'spider_name', 'category', 'title', 'url',
                    'relevance_score', 'created_at'
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
            by_category = dict(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .values('category')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('category', 'count')
            )

            return {
                'action': 'stats',
                'total_items': total,
                'days_back': days,
                'by_spider': by_spider,
                'by_category': by_category,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: recent, by_spider, by_category, search, stats"
            )

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
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'recent')
        limit = payload.get('limit', 20)
        agent_name = payload.get('agent_name')
        hours = payload.get('hours', 24)

        cutoff = timezone.now() - timedelta(hours=hours)

        if action == 'recent':
            qs = AgentExecution.objects.filter(created_at__gte=cutoff)

            if agent_name:
                qs = qs.filter(agent_name__icontains=agent_name)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'agent_name', 'task', 'status', 'success',
                    'execution_time_ms', 'created_at'
                )
            )

            return {
                'action': 'recent',
                'count': len(items),
                'items': items,
                'hours_back': hours,
            }

        elif action == 'by_agent':
            if not agent_name:
                # List active agents with execution counts
                agent_counts = dict(
                    AgentExecution.objects.filter(created_at__gte=cutoff)
                    .values('agent_name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:30]
                    .values_list('agent_name', 'count')
                )
                return {
                    'action': 'by_agent',
                    'active_agents': agent_counts,
                    'message': 'Specify agent_name to see executions for a specific agent'
                }

            items = list(
                AgentExecution.objects.filter(
                    agent_name__icontains=agent_name,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'agent_name', 'task', 'status', 'success',
                    'execution_time_ms', 'error_message', 'created_at'
                )
            )

            # Calculate success rate for this agent
            total = AgentExecution.objects.filter(
                agent_name__icontains=agent_name,
                created_at__gte=cutoff
            ).count()
            successes = AgentExecution.objects.filter(
                agent_name__icontains=agent_name,
                created_at__gte=cutoff,
                success=True
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
                created_at__gte=cutoff, success=True
            ).count()
            failures = total - successes

            by_agent = list(
                AgentExecution.objects.filter(created_at__gte=cutoff)
                .values('agent_name')
                .annotate(
                    count=Count('id'),
                    avg_time=Avg('execution_time_ms')
                )
                .order_by('-count')[:15]
            )

            return {
                'action': 'stats',
                'total_executions': total,
                'successes': successes,
                'failures': failures,
                'success_rate': successes / total if total > 0 else 0,
                'hours_back': hours,
                'by_agent': by_agent,
            }

        elif action == 'failures':
            items = list(
                AgentExecution.objects.filter(
                    created_at__gte=cutoff,
                    success=False
                ).order_by('-created_at')[:limit].values(
                    'id', 'agent_name', 'task', 'status', 'error_message',
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
                    'times_successful', 'updated_at'
                )
            )

            # Calculate effectiveness for each
            for item in items:
                applied = item.get('times_applied', 0)
                successful = item.get('times_successful', 0)
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
                    'times_successful', 'updated_at'
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

            for item in items:
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


# Singleton instance
_tool_dispatcher: Optional[ToolDispatcher] = None


def get_tool_dispatcher() -> ToolDispatcher:
    """Get the singleton ToolDispatcher instance."""
    global _tool_dispatcher
    if _tool_dispatcher is None:
        _tool_dispatcher = ToolDispatcher()
    return _tool_dispatcher
