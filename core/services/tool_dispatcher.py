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

        # Workflow tools
        self.register("workflow_orchestration_agent", self._handle_agent_tool)
        self.register("create_brand_video", self._handle_agent_tool)
        self.register("create_project_from_research", self._handle_agent_tool)
        self.register("strategic_review", self._handle_agent_tool)
        self.register("coleadership_agent", self._handle_agent_tool)

        # Legal tools
        self.register("legal_doc_drafter_agent", self._handle_agent_tool)

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
        agent = registry.get_agent(agent_name)

        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found for tool '{tool_name}'")

        # Extract task from payload
        task = payload.get('task') or payload.get('prompt') or payload.get('query', '')
        context = payload.get('context', {})

        # Execute agent
        result = agent.run(task=task, context=context)

        return {
            'agent': agent_name,
            'output': result.output if hasattr(result, 'output') else str(result),
            'success': result.success if hasattr(result, 'success') else True,
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
        agent = registry.get_agent('ResearchAgent')

        query = payload.get('query', '')
        result = agent.run(task=f"Search for: {query}")

        return {
            'query': query,
            'results': result.output if hasattr(result, 'output') else str(result),
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
        agent = registry.get_agent(agent_name)

        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        result = agent.run(task=task, context=context)

        return {
            'agent': agent_name,
            'output': result.output if hasattr(result, 'output') else str(result),
            'success': result.success if hasattr(result, 'success') else True,
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
            registry = get_agent_registry()
            agent = registry.get_agent('ThinkingAgent')
            if agent:
                result = agent.run(task="Reflect on recent system activity and generate insights")
                return {
                    'action': 'trigger',
                    'triggered': True,
                    'output': result.output if hasattr(result, 'output') else str(result),
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
                    'created_at', 'source_agent', 'ml_recommendation'
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

            return {
                'action': 'reject_decision',
                'id': str(decision_id),
                'topic': decision.topic,
                'new_status': decision.status,
                'reason': reason,
                'success': True,
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: stats, list_attention, list_decisions, approve_attention, ignore_attention, promote_decision, reject_decision")


# Singleton instance
_tool_dispatcher: Optional[ToolDispatcher] = None


def get_tool_dispatcher() -> ToolDispatcher:
    """Get the singleton ToolDispatcher instance."""
    global _tool_dispatcher
    if _tool_dispatcher is None:
        _tool_dispatcher = ToolDispatcher()
    return _tool_dispatcher
