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
        self.register("resolve_agent", self._handle_agent_tool)
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
        self.register("deliverables_tool", self._handle_deliverables)
        self.register("media_tool", self._handle_media)
        self.register("davinci_tool", self._handle_davinci)

        # Body system tools
        self.register("get_body_vitals", self._handle_body_vitals)
        self.register("check_resource_budget", self._handle_check_budget)
        self.register("get_system_alerts", self._handle_system_alerts)
        self.register("cost_telemetry_tool", self._handle_cost_telemetry)

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

        # Session 1031: Dream browsing/approval via PA
        self.register("dream_tool", self._handle_dream)

        # Workflow tools
        self.register("workflow_orchestration_agent", self._handle_agent_tool)
        self.register("create_brand_video", self._handle_agent_tool)
        self.register("create_project_from_research", self._handle_agent_tool)
        self.register("strategic_review", self._handle_agent_tool)
        self.register("coleadership_agent", self._handle_agent_tool)

        # Legal tools — Session 1035: dedicated handler via AgentRouter (not registry stub)
        self.register("legal_doc_drafter_agent", self._handle_legal_agent)

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

        # Session 1014: Legislation tool for congressional bill tracking
        self.register("legislation_tool", self._handle_legislation)

        # Session 995B: Sports betting intelligence tool
        self.register("sports_betting_tool", self._handle_sports_betting)

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

        # RAG query — semantic search + stats
        self.register("rag_query_tool", self._handle_rag_query)

        # Session G1: Competitor comparison — generate, status, list, detail
        self.register("competitor_comparison_tool", self._handle_competitor_comparison)

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
            'image_generation_agent': 'ImageAgent',
            'image_editing_agent': 'ImageEditingAgent',
            'video_generation_agent': 'VideoAgent',
            'video_editing_agent': 'VideoEditingAgent',
            'resolve_agent': 'ResolveAgent',
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
            'strategic_review': 'ContentStrategyAgent',  # Session 1068: StrategyAgent doesn't exist
            'coleadership_agent': 'CoLeadershipAgent',
            'legal_doc_drafter_agent': 'LegalDocDrafterAgent',
            'system_intelligence_agent': 'SystemIntelligenceAgent',
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

        else:
            raise ValueError(f"Unknown action: {action}")

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

            items = list(
                qs.order_by('-created_at')[offset:offset + limit].values(*_LIST_FIELDS)
            )
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

            items = list(
                qs.order_by('-created_at')[offset:offset + limit].values(*_LIST_FIELDS)
            )
            return {
                'action': 'search', 'query': query, 'total': total,
                'offset': offset, 'limit': limit, 'count': len(items), 'items': items,
            }

        elif action == 'detail':
            obj, disambiguation = _resolve_deliverable(base_qs, payload, 'detail')
            if disambiguation:
                return disambiguation

            return {
                'action': 'detail',
                'id': str(obj.id),
                'title': obj.title,
                'deliverable_type': obj.deliverable_type,
                'category': obj.category,
                'agent_name': obj.agent_name,
                'content_format': obj.content_format,
                'content_preview': (obj.content or '')[:500],
                'quality_score': obj.quality_score,
                'is_saved': obj.is_saved,
                'is_template': obj.is_template,
                'status': obj.status,
                'tags': obj.tags or [],
                'created_at': obj.created_at.isoformat() if obj.created_at else None,
            }

        elif action == 'save':
            obj, disambiguation = _resolve_deliverable(base_qs, payload, 'save')
            if disambiguation:
                return disambiguation
            obj.is_saved = True
            obj.save(update_fields=['is_saved'])
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
            if 'content' in payload:
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
                raise ValueError("update requires at least one of: title, content, type, content_format, tags")

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
        limit = payload.get('limit', 10)  # Session 1057: Reduced from 20 to match schema

        if action == 'list':
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

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: stats, lookup, list_attention, list_decisions, approve_attention, ignore_attention, promote_decision, reject_decision, get_triage_batch, list_unclassified, classify_suggest, classify_apply, classify_apply_batch")

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

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, search, recent, details, by_category, stats"
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

            return {
                'action': 'details',
                'source': 'SelfBlog',
                'blog': {
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
            status_filter = payload.get('item_status', 'pending')
            priority_filter = payload.get('priority')

            qs = InitiativeActionItem.objects.select_related('initiative', 'source_stage')

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
                    'initiative_id': str(item.initiative_id),  # type: ignore[attr-defined]
                    'initiative_name': item.initiative.name if item.initiative else 'Unknown',
                    'source_stage': item.source_stage.stage if item.source_stage else None,
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

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, details, "
                f"action_items, flow_metrics, update_status, advance, start_action_item, "
                f"complete_action_item, assign_owner, bulk_auto_assign, bulk_cleanup"
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
                health['components']['details'] = components  # type: ignore[index]
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

        # 6. Queue depths (live Redis LLEN)
        try:
            from core.views_diagnostics import get_redis_client, CELERY_QUEUE_NAMES
            r = get_redis_client()
            if r:
                depths = {}
                total_pending = 0
                for qname in CELERY_QUEUE_NAMES:
                    try:
                        length = r.llen(qname)
                    except Exception:
                        length = 0
                    depths[qname] = length
                    total_pending += length
                health['queue_depths'] = {
                    'total_pending': total_pending,
                    'per_queue': depths,
                }
            else:
                health['queue_depths'] = {'error': 'Redis unavailable'}
        except Exception as e:
            health['queue_depths'] = {'error': str(e)}

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

        qd = health.get('queue_depths', {})
        total_pending = qd.get('total_pending', 0)
        if total_pending > 5000:
            assessment = 'degraded' if assessment != 'critical' else 'critical'
            reasons.append(f"Queue backlog: {total_pending} pending tasks")
        elif total_pending > 1000:
            if assessment == 'healthy':
                assessment = 'degraded'
            reasons.append(f"Queue backlog: {total_pending} pending tasks")

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
            # Session 1068: Include individual rows so PA can see error messages
            if action == 'detailed' or hours >= 24:
                detail_rows = list(
                    failed_tc.order_by('-created_at')[:item_limit]
                    .values('created_at', 'agent_name', 'tool_name',
                            'error_type', 'error_message', 'latency_ms',
                            'task_summary')
                )
                for row in detail_rows:
                    if row.get('created_at'):
                        row['created_at'] = row['created_at'].isoformat()
                    if row.get('error_message'):
                        row['error_message'] = row['error_message'][:500]
                errors['failed_tool_calls']['details'] = detail_rows
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

        # 5. Session 1068: Agent timeout breakdown (top timeout-prone agents)
        try:
            from core.models_unified_system import AgentExecution
            timeout_qs = AgentExecution.objects.filter(
                created_at__gte=cutoff,
                status='failed',
                error_message__icontains='timed out after 45 minutes'
            )
            timeout_by_agent = list(
                timeout_qs.values('agent__name')
                .annotate(timeouts=Count('id'))
                .order_by('-timeouts')[:10]
            )
            errors['agent_timeouts'] = {
                'total': timeout_qs.count(),
                'by_agent': timeout_by_agent,
            }
            total_errors += timeout_qs.count()

            # Include recent non-timeout agent failures with error messages
            if action == 'detailed' or hours >= 24:
                recent_failures = list(
                    AgentExecution.objects.filter(
                        created_at__gte=cutoff,
                        status='failed',
                    ).exclude(
                        error_message__icontains='timed out after 45 minutes'
                    ).order_by('-created_at')[:item_limit]
                    .values('agent__name', 'task', 'error_message',
                            'created_at', 'execution_time_ms')
                )
                for row in recent_failures:
                    if row.get('created_at'):
                        row['created_at'] = row['created_at'].isoformat()
                    if row.get('error_message'):
                        row['error_message'] = row['error_message'][:500]
                    if row.get('task'):
                        row['task'] = row['task'][:200]
                errors['agent_failures_detail'] = recent_failures
        except Exception as e:
            errors['agent_timeouts'] = {'error': str(e)}

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
            qs = PlacedWager.objects.all().order_by('-created_at')
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
                    'created_at': w.created_at.isoformat() if hasattr(w, 'created_at') and w.created_at else None,  # type: ignore[attr-defined]
                })
            return {'action': 'wagers', 'items': items, 'total': total}

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
        agent_query = payload.get('agent_name', '').strip().lower()

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
                router_routable_total = len(AgentRouter.AGENT_MAP)
                # Hard-blocked: won't execute at all on Railway
                _BLOCKED = frozenset({
                    'CodeGeneratorAgent',  # No codebase access in Railway sandbox
                    'AudioAgent',          # TTS quota exhausted
                })
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

        filter_keyword = payload.get('filter', '')
        tasks = PeriodicTask.objects.filter(enabled=True).order_by('name')

        if filter_keyword:
            tasks = tasks.filter(name__icontains=filter_keyword)

        results = []
        for task in tasks[:50]:
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
            'total_enabled': PeriodicTask.objects.filter(enabled=True).count(),
            'showing': len(results),
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
            together_key = os.environ.get('TOGETHER_API_KEY', '')
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
        return run_smoke_test(payload)

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

        return {'error': f'Unknown action: {action}'}

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
            }
            if c.status == 'complete':
                result['summary'] = c.summary[:500]
                result['completed_at'] = c.completed_at.isoformat() if c.completed_at else None
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

        return {'error': f'Unknown action: {action}'}


# Singleton instance
_tool_dispatcher: Optional[ToolDispatcher] = None


def get_tool_dispatcher() -> ToolDispatcher:
    """Get the singleton ToolDispatcher instance."""
    global _tool_dispatcher
    if _tool_dispatcher is None:
        _tool_dispatcher = ToolDispatcher()
    return _tool_dispatcher
