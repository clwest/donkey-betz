"""
ToolDispatcher AgentHandlersMixin — extracted handler methods.
"""

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




class AgentHandlersMixin:
    """Mixin providing handler methods for ToolDispatcher."""

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
                    from content.models import ImageHistory
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

        elif action == 'delete':
            opp_id = payload.get('id', '') or payload.get('opportunity_id', '')
            if not opp_id:
                raise ValueError("'id' is required for delete action")
            opp = base_qs.filter(id=opp_id).first()
            if not opp:
                return {'action': 'delete', 'success': False, 'error': f'Opportunity {opp_id} not found'}
            title = opp.title
            # Count linked tasks before CASCADE deletes them
            from core.models_unified_system import OpportunityTask as _OT
            task_count = _OT.objects.filter(opportunity=opp).count()
            opp.delete()
            return {
                'action': 'delete', 'success': True,
                'id': str(opp_id), 'title': title,
                'tasks_deleted': task_count,
                'message': f"Deleted opportunity '{title}' and {task_count} linked task(s)",
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, get, stats, update_status, create, delete"
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

        elif action == 'delete':
            task_id = payload.get('id', '').strip()
            if not task_id:
                raise ValueError("'id' is required for delete action")
            task = base_qs.filter(id=task_id).first()
            if not task:
                return {'action': 'delete', 'success': False, 'error': f'Task {task_id} not found'}
            title = task.title
            task.delete()
            return {'action': 'delete', 'success': True, 'id': task_id, 'title': title, 'message': f"Deleted task '{title}'"}

        else:
            raise ValueError(f"Unknown action: {action}. Valid: list, stats, create, update, complete, delete")

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

        elif action == 'delete':
            from core.models_skin_layer import ProjectWorkspace

            ws_id = payload.get('id', '').strip()
            if not ws_id:
                raise ValueError("'id' is required for delete action")

            ws = ProjectWorkspace.objects.filter(id=ws_id).first()
            if not ws:
                return {'action': 'delete', 'success': False, 'error': f'Workspace {ws_id} not found'}

            # Safety: only allow deleting sandbox workspaces owned by user
            if ws.workspace_type != 'sandbox':
                return {'action': 'delete', 'success': False, 'error': 'Only sandbox workspaces can be deleted'}
            if user_id and ws.user_id and ws.user_id != user_id:
                return {'action': 'delete', 'success': False, 'error': 'Cannot delete another user\'s workspace'}

            name = ws.name
            ws.delete()
            return {'action': 'delete', 'success': True, 'name': name, 'message': f"Deleted workspace '{name}'"}

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: list, status, create, delete")

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
            """Apply category/agent/type/saved/status/date filters."""
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
            # Session 1101: Status filter (with aliases for LLM confusion)
            _STATUS_ALIASES = {'approved': 'ready', 'pending_review': 'ready', 'rejected': 'archived'}
            status = payload.get('status')
            if status:
                status = _STATUS_ALIASES.get(status, status)
                qs = qs.filter(status=status)
            # Session 1101: Date range filters
            created_before = payload.get('created_before')
            created_after = payload.get('created_after')
            if created_before:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(created_before)
                if dt:
                    qs = qs.filter(created_at__lt=dt)
            if created_after:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(created_after)
                if dt:
                    qs = qs.filter(created_at__gte=dt)
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

        # Session 1000B: Lookup item by title or ID
        elif action == 'lookup':
            item_id = payload.get('id', '')
            title_query = payload.get('title_query', '')

            # Session 1097: Direct ID lookup — fast path
            if item_id:
                item = HumanAttentionItem.objects.filter(id=item_id).first()
                if item:
                    return {
                        'action': 'lookup',
                        'found': True,
                        'item_type': 'attention',
                        'id': str(item.id),
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
                # Try decisions by ID
                decision = AgentDecisionSummary.objects.filter(id=item_id).first()
                if decision:
                    return {
                        'action': 'lookup',
                        'found': True,
                        'item_type': 'decision',
                        'id': str(decision.id),
                        'title': decision.topic,
                        'summary': decision.key_insights or '',
                        'decision_type': decision.decision_type or '',
                        'recommended_stance': decision.recommended_stance or '',
                        'impact_area': decision.impact_area or '',
                        'status': decision.status,
                        'created_at': decision.created_at.isoformat() if decision.created_at else '',
                    }
                return {'action': 'lookup', 'found': False, 'id': item_id, 'error': 'Item not found'}

            if not title_query:
                return {'action': 'lookup', 'found': False, 'error': 'Provide id or title_query'}

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

