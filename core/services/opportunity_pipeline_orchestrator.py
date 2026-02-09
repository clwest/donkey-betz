"""
Opportunity Pipeline Orchestrator Agent

This agent creates multi-stage opportunity execution workflows that flow from
discovery → analysis → execution → optimization through different specialized
agents and advisors. It orchestrates complex value multiplication pipelines
where each stage adds compound value before passing to the next specialist.

Features:
- Multi-stage workflow orchestration
- Dynamic agent selection and routing
- Compound value multiplication
- Cross-platform opportunity management
- Real-time performance monitoring
- Adaptive workflow optimization

Session 306: Added learning infrastructure hooks for cross-agent knowledge sharing.
Session 727: Migrated from agents/opportunity_pipeline_orchestrator.py to core/services/opportunity_pipeline_orchestrator.py
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


# Session 392: Updated to use canonical import paths
try:
    from core.agents.registry import get_agent_registry
except ImportError:
    get_agent_registry = None

try:
    from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution, AgentOrchestration
except ImportError:
    UnifiedAgentTemplate = AgentExecution = AgentOrchestration = None

try:
    from intelligence.revenue_integration import RevenueIncomeIntegration
except ImportError:
    RevenueIncomeIntegration = None

try:
    from ai_core.spiders.spider_network import SpiderNetwork
except ImportError:
    # Create a simple mock if not available
    class SpiderNetwork:
        def get_new_opportunities(self):
            return []

try:
    from self_awareness.embeddings import CodebaseEmbeddingManager, SemanticCodeSearchEngine
except ImportError:
    CodebaseEmbeddingManager = SemanticCodeSearchEngine = None

logger = logging.getLogger(__name__)


class PipelineLearningMixin:
    """
    Learning infrastructure mixin for OpportunityPipelineOrchestrator.
    Session 306: Enables cross-agent knowledge sharing for pipeline orchestration.
    """

    _learning_loop = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(None)
            except ImportError:
                logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                logger.debug("MemoryEmbeddingService not available")
                return None
        return self._memory_service

    @property
    def agent_model(self):
        """Lazy-load or create Agent model instance."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                # Session 737: Use sync_to_async for Django ORM in async context
                from asgiref.sync import sync_to_async
                import asyncio

                def _get_or_create_agent():
                    return Agent.objects.get_or_create(
                        name='OpportunityPipelineOrchestrator',
                        defaults={
                            'agent_type': 'standalone',
                            'specialization': 'workflow_orchestration',
                            'description': 'Orchestrates multi-stage opportunity execution workflows.',
                            'is_active': True,
                        }
                    )

                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    # We're in async context - skip ORM (learning will be disabled)
                    logger.debug("Skipping Agent model in async context")
                    return None
                except RuntimeError:
                    # Not in async context - safe to use ORM
                    self._agent_model, _ = _get_or_create_agent()

            except ImportError:
                logger.debug("Agent model not available")
                return None
            except Exception as e:
                logger.debug(f"Agent model creation failed: {e}")
                return None
        return self._agent_model

    def _record_learning_outcome(
        self,
        result: Dict[str, Any],
        task: str,
        context: Dict[str, Any] = None,
        spider_data_used: bool = False
    ):
        """Record execution outcome for XP and pattern learning."""
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type='workflow',
                query_text=task,
                execution_mode='agent',
                agents_used=['OpportunityPipelineOrchestrator'],
                response=result.get('message', str(result)),
                execution_time_ms=int(result.get('execution_time', 0) * 1000),
                success=result.get('success', False),
                spider_data_used=spider_data_used,
                scifi_context_used=True,  # Pipeline uses memory insights
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            logger.warning(f"Failed to record learning outcome: {e}")
            return None

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """Create a memory from the pipeline execution."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"Pipeline: {task[:50]}...",
                content=str(result.get('pipeline_report', result)),
                memory_type=memory_type,
                valence="positive" if result.get('success') else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['pipeline', 'orchestration', 'success' if result.get('success') else 'failure']
            )
            return memory
        except Exception as e:
            logger.warning(f"Failed to create execution memory: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Dict[str, Any],
        confidence: float = 0.8
    ):
        """Share learned knowledge for cross-agent learning."""
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            type_mapping = {
                'pipeline': 'tool_discovery',
                'workflow': 'tool_discovery',
                'optimization': 'market',
                'agent_selection': 'tool_discovery',
            }
            mapped_type = type_mapping.get(knowledge_type, 'opportunity')

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title,
                knowledge_type=mapped_type,
                defaults={
                    'summary': json.dumps(knowledge_value),
                    'confidence_score': confidence,
                    'is_active': True,
                }
            )
            return knowledge
        except Exception as e:
            logger.warning(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge from other agents."""
        try:
            from core.models_unified_system import AgentKnowledgeSource

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                type_mapping = {
                    'pipeline': 'tool_discovery',
                    'workflow': 'tool_discovery',
                    'optimization': 'market',
                }
                mapped_type = type_mapping.get(knowledge_type, knowledge_type)
                queryset = queryset.filter(knowledge_type=mapped_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            return [
                {
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                }
                for ks in queryset.order_by('-confidence_score')[:10]
            ]
        except Exception as e:
            logger.warning(f"Failed to get shared knowledge: {e}")
            return []


class PipelineStage(Enum):
    """Pipeline execution stages"""
    DISCOVERY = "discovery"
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    OPTIMIZATION = "optimization"
    MONITORING = "monitoring"


@dataclass
class OpportunityContext:
    """Context for opportunity processing"""
    opportunity_id: str
    source_platform: str
    priority_level: str
    success_probability: float
    current_stage: PipelineStage
    metadata: Dict[str, Any]
    pipeline_config: Dict[str, Any]
    opportunity_embedding: Optional[List[float]] = None
    similar_opportunities: Optional[List[Dict[str, Any]]] = None
    memory_insights: Optional[Dict[str, Any]] = None


@dataclass
class StageResult:
    """Result from a pipeline stage"""
    stage: PipelineStage
    success: bool
    output_data: Dict[str, Any]
    agent_used: str
    execution_time: float
    quality_score: float
    next_stage_recommendations: List[str]


class OpportunityPipelineOrchestrator(PipelineLearningMixin):
    """
    Orchestrates multi-stage opportunity execution workflows

    Creates sophisticated pipelines that flow opportunities through specialized
    agents and advisors, with each stage adding compound value before passing
    to the next specialist.

    Session 306: Now includes learning infrastructure for cross-agent knowledge sharing.
    """

    def __init__(self):
        self.agent_registry = get_agent_registry() if get_agent_registry else None
        self.revenue_integration = RevenueIncomeIntegration() if RevenueIncomeIntegration else None
        self.spider_network = SpiderNetwork()

        # Memory and embeddings integration
        self.embedding_manager = CodebaseEmbeddingManager() if CodebaseEmbeddingManager else None
        self.search_engine = SemanticCodeSearchEngine() if SemanticCodeSearchEngine else None
        self.opportunity_memory = {}  # Cache for opportunity patterns

        # Session 306: Initialize learning mixin attributes
        self._learning_loop = None
        self._memory_service = None
        self._agent_model = None

        # Stage configuration - Session 737: Fixed to use actual agent names from AgentRouter
        self.stage_agents = {
            PipelineStage.DISCOVERY: [
                'ResearchAgent',
                'CompetitorAnalysisAgent',
                'TrendAnalysisAgent',
                'CustomerResearchAgent'
            ],
            PipelineStage.ANALYSIS: [
                'OpportunityScoringAgent',
                'MarketIntelligenceAgent',
                'StockAnalystAgent'
            ],
            PipelineStage.EXECUTION: [
                'BrandStrategyAgent',
                'MarketingStrategyAgent',
                'ContentStrategyAgent',
                'ContentWriterAgent'
            ],
            PipelineStage.OPTIMIZATION: [
                'COOAgent',
                'PerformanceAnalystAgent',
                'SEOOptimizerAgent'
            ]
        }

        # Value multiplication factors for each stage
        self.value_multipliers = {
            PipelineStage.DISCOVERY: 1.2,
            PipelineStage.ANALYSIS: 1.5,
            PipelineStage.EXECUTION: 2.0,
            PipelineStage.OPTIMIZATION: 2.5
        }

    async def orchestrate_opportunity_pipeline(
        self,
        opportunity: Dict[str, Any],
        pipeline_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate complete opportunity pipeline from discovery to optimization

        Args:
            opportunity: Raw opportunity data
            pipeline_config: Optional configuration for pipeline behavior

        Returns:
            Complete pipeline results with compound value calculations
        """
        try:
            logger.info(f"Starting pipeline orchestration for opportunity: {opportunity.get('title', 'Unknown')}")

            # Initialize pipeline context with memory and embeddings
            context = await self._initialize_pipeline_context_with_memory(opportunity, pipeline_config)

            # Track pipeline execution
            pipeline_id = await self._create_pipeline_tracking(context)

            # Execute pipeline stages sequentially
            stage_results = []
            current_value = opportunity.get('base_value', 100)

            for stage in PipelineStage:
                logger.info(f"Executing pipeline stage: {stage.value}")

                # Execute stage with compound value from previous stages
                stage_result = await self._execute_pipeline_stage(
                    stage,
                    context,
                    current_value,
                    stage_results
                )

                stage_results.append(stage_result)

                # Calculate compound value multiplication
                if stage_result.success:
                    multiplier = self.value_multipliers.get(stage, 1.0)
                    quality_bonus = stage_result.quality_score * 0.3
                    current_value *= (multiplier + quality_bonus)

                    logger.info(f"Stage {stage.value} multiplied value to: ${current_value:.2f}")
                else:
                    logger.warning(f"Stage {stage.value} failed, continuing with reduced confidence")

                # Update context for next stage
                context.current_stage = stage
                context.metadata[f'{stage.value}_result'] = stage_result.output_data

                # Adaptive decision: should we continue to next stage?
                if not await self._should_continue_pipeline(stage_result, context):
                    logger.info(f"Pipeline optimization decided to stop at stage: {stage.value}")
                    break

            # Generate final pipeline report with memory insights
            pipeline_report = await self._generate_pipeline_report_with_memory(
                context,
                stage_results,
                current_value,
                opportunity.get('base_value', 100)
            )

            # Update tracking
            await self._update_pipeline_tracking(pipeline_id, pipeline_report)

            success_result = {
                'success': True,
                'pipeline_id': pipeline_id,
                'final_value': current_value,
                'value_multiplication': current_value / opportunity.get('base_value', 100),
                'stages_executed': len(stage_results),
                'stage_results': [self._serialize_stage_result(r) for r in stage_results],
                'pipeline_report': pipeline_report,
                'optimized_opportunity': await self._create_optimized_opportunity(
                    opportunity, stage_results, current_value
                )
            }

            # Session 306: Learning Infrastructure Hooks
            task = f"Pipeline for: {opportunity.get('title', 'Unknown opportunity')}"

            # Record learning outcome (sync call in async context is fine for non-critical)
            self._record_learning_outcome(
                result=success_result,
                task=task,
                context={
                    'stages_executed': len(stage_results),
                    'final_value': current_value,
                    'value_multiplication': success_result['value_multiplication'],
                },
                spider_data_used=True  # Spider network is used
            )

            # Create high-importance memory for pipeline execution
            self._create_execution_memory(
                result=success_result,
                task=task,
                memory_type="success",
                importance=0.8  # High importance for successful pipelines
            )

            # Share pipeline pattern knowledge for cross-agent learning
            if success_result['value_multiplication'] > 1.5:
                agents_used = [r.agent_used for r in stage_results if r.success]
                self._share_knowledge(
                    knowledge_type='pipeline',
                    title=f"High-value pipeline: {success_result['value_multiplication']:.1f}x",
                    knowledge_value={
                        'opportunity_type': opportunity.get('type', 'unknown'),
                        'agents_used': agents_used,
                        'value_multiplication': success_result['value_multiplication'],
                        'stages_completed': len(stage_results),
                    },
                    confidence=min(0.9, 0.5 + success_result['value_multiplication'] * 0.1)
                )

            return success_result

        except Exception as e:
            logger.error(f"Pipeline orchestration failed: {str(e)}")

            error_result = {
                'success': False,
                'error': str(e),
                'partial_results': stage_results if 'stage_results' in locals() else []
            }

            # Session 306: Record failed pipeline for learning
            self._record_learning_outcome(
                result=error_result,
                task=f"Pipeline for: {opportunity.get('title', 'Unknown')}",
                context={'error': str(e)}
            )

            return error_result

    async def _execute_pipeline_stage(
        self,
        stage: PipelineStage,
        context: OpportunityContext,
        current_value: float,
        previous_results: List[StageResult]
    ) -> StageResult:
        """Execute a single pipeline stage with optimal agent selection"""

        start_time = datetime.now()

        try:
            # Select best agent for this stage
            best_agent = await self._select_optimal_agent_for_stage(
                stage, context, current_value, previous_results
            )

            if not best_agent:
                return StageResult(
                    stage=stage,
                    success=False,
                    output_data={'error': 'No suitable agent found'},
                    agent_used='none',
                    execution_time=0,
                    quality_score=0,
                    next_stage_recommendations=[]
                )

            # Prepare stage-specific task data
            task_data = await self._prepare_stage_task_data(
                stage, context, current_value, previous_results
            )

            # Session 737: Execute agent - use AgentRouter if agent came from there
            if best_agent.get('_from_router'):
                # Execute via AgentRouter
                from core.agent_router import AgentRouter
                agent_router = AgentRouter()

                # Prepare task string for router
                task_str = task_data.get('task', f"Execute {stage.value} stage")
                agent_name = best_agent.get('name', 'ResearchAgent')

                try:
                    router_result = agent_router.route(
                        agent_name=agent_name,
                        task=task_str,
                        context=task_data.get('context', {})
                    )

                    # AgentResult is a dataclass, access attributes directly
                    # Session 737: Ensure output_data is never None to prevent .get() failures
                    result = {
                        'success': router_result.success,
                        'output_data': router_result.data or {},  # Ensure dict, not None
                        'error': router_result.error,
                        'execution_time': router_result.execution_time_ms / 1000.0  # Convert ms to seconds
                    }
                except Exception as router_error:
                    result = {
                        'success': False,
                        'output_data': {},
                        'error': str(router_error),
                        'execution_time': 0
                    }
            else:
                # Execute via agent_registry (original path)
                execution_id = self.agent_registry.execute_agent(
                    best_agent['name'],
                    task_data
                ) if self.agent_registry else None

                if not execution_id:
                    raise Exception(f"Failed to execute agent {best_agent['name']}")

                # Monitor execution and get results
                result = await self._monitor_agent_execution(execution_id)

            # Calculate execution metrics
            execution_time = (datetime.now() - start_time).total_seconds()

            # Session 737: Debug logging for OPTIMIZATION stage
            if stage == PipelineStage.OPTIMIZATION:
                logger.debug(f"OPTIMIZATION result: success={result.get('success')}, output_data type={type(result.get('output_data'))}")

            quality_score = await self._calculate_stage_quality_score(
                stage, result, context
            )

            # Generate recommendations for next stage
            next_recommendations = await self._generate_next_stage_recommendations(
                stage, result, context, quality_score
            )

            # Session 737: Use `or {}` to ensure output_data is never None
            # Note: .get(key, default) only uses default if key is missing,
            # but returns None if key exists with None value
            return StageResult(
                stage=stage,
                success=result.get('success', False),
                output_data=result.get('output_data') or {},
                agent_used=best_agent['name'],
                execution_time=execution_time,
                quality_score=quality_score,
                next_stage_recommendations=next_recommendations
            )

        except Exception as e:
            logger.error(f"Stage {stage.value} execution failed: {str(e)}")
            return StageResult(
                stage=stage,
                success=False,
                output_data={'error': str(e)},
                agent_used='error',
                execution_time=(datetime.now() - start_time).total_seconds(),
                quality_score=0,
                next_stage_recommendations=[]
            )

    async def _select_optimal_agent_for_stage(
        self,
        stage: PipelineStage,
        context: OpportunityContext,
        current_value: float,
        previous_results: List[StageResult]
    ) -> Optional[Dict[str, Any]]:
        """Select the optimal agent for a specific pipeline stage using memory and embeddings"""

        # Use memory insights to enhance agent selection
        memory_recommended_agents = []
        if context.memory_insights and context.memory_insights.get('successful_agents'):
            # Session 737: Guard against None value in successful_agents dict
            successful_agents_dict = context.memory_insights['successful_agents']
            if successful_agents_dict is not None:
                memory_recommended_agents = successful_agents_dict.get(stage.value) or []

        # Get potential agents for this stage
        candidate_agents = self.stage_agents.get(stage, [])

        # Add memory-recommended agents to candidates
        candidate_agents.extend(memory_recommended_agents)
        candidate_agents = list(set(candidate_agents))  # Remove duplicates

        if not candidate_agents:
            # Use semantic search to find similar successful pipelines
            if self.search_engine and context.opportunity_embedding:
                similar_pipelines = await self._find_similar_successful_pipelines(context)
                if similar_pipelines:
                    for pipeline in similar_pipelines[:3]:  # Top 3 similar
                        # Session 737: Guard against None values
                        agents_used = pipeline.get('agents_used') or {}
                        stage_agents = agents_used.get(stage.value) or []
                        candidate_agents.extend(stage_agents)

            # Fallback to intelligent agent discovery
            if not candidate_agents:
                task_description = f"Stage {stage.value} processing for {context.opportunity_id}"
                return self.agent_registry.find_best_agent(task_description)

        # Score each candidate agent with memory-enhanced scoring
        agent_scores = []

        # Session 737: Import AgentRouter for fallback
        from core.agent_router import AgentRouter
        agent_router = AgentRouter()

        for agent_name in candidate_agents:
            agent = self.agent_registry.get_agent(agent_name) if self.agent_registry else None

            # Session 737: Fallback to AgentRouter if not in registry
            if not agent and agent_name in agent_router.AGENT_MAP:
                # Create minimal agent dict for scoring
                agent = {
                    'name': agent_name,
                    'specialization': 'general',
                    'capabilities': [],
                    'performance_metrics': {'success_rate': 0.7},
                    'is_verified': True,
                    '_from_router': True  # Flag to use AgentRouter for execution
                }

            if not agent:
                continue

            score = await self._score_agent_for_stage_with_memory(
                agent, stage, context, current_value, previous_results
            )

            agent_scores.append((agent, score))

        if not agent_scores:
            return None

        # Return the highest scoring agent
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        selected_agent = agent_scores[0][0]

        # Log selection reasoning for memory learning
        await self._log_agent_selection_reasoning(stage, selected_agent, agent_scores, context)

        return selected_agent

    async def _score_agent_for_stage(
        self,
        agent: Dict[str, Any],
        stage: PipelineStage,
        context: OpportunityContext,
        current_value: float,
        previous_results: List[StageResult]
    ) -> float:
        """Score an agent's suitability for a specific stage"""

        score = 0.0

        # Base specialization match
        # Session 737: Use `or ''` to handle None values
        specialization = agent.get('specialization') or ''
        if stage == PipelineStage.DISCOVERY and 'research' in specialization:
            score += 20.0
        elif stage == PipelineStage.ANALYSIS and 'analysis' in specialization:
            score += 20.0
        elif stage == PipelineStage.EXECUTION and 'business' in specialization:
            score += 20.0
        elif stage == PipelineStage.OPTIMIZATION and 'financial' in specialization:
            score += 20.0

        # Performance metrics
        # Session 737: Guard against None performance_metrics
        metrics = agent.get('performance_metrics') or {}
        score += metrics.get('success_rate', 0.5) * 15.0

        # Value handling capability (higher value = need more experienced agent)
        if current_value > 1000:
            if agent.get('is_verified', False):
                score += 10.0

        # Stage synergy with previous results
        if previous_results:
            last_result = previous_results[-1]
            if agent['name'] in last_result.next_stage_recommendations:
                score += 15.0

        # Capability match
        # Session 737: Guard against None capabilities
        required_caps = self._get_stage_required_capabilities(stage)
        agent_caps = set(agent.get('capabilities') or [])
        matching_caps = len(agent_caps.intersection(required_caps))
        score += matching_caps * 5.0

        return score

    def _get_stage_required_capabilities(self, stage: PipelineStage) -> set:
        """Get required capabilities for each stage"""
        capabilities = {
            PipelineStage.DISCOVERY: {'research', 'data_collection', 'market_analysis'},
            PipelineStage.ANALYSIS: {'financial_analysis', 'risk_assessment', 'data_analysis'},
            PipelineStage.EXECUTION: {'strategy', 'implementation', 'project_management'},
            PipelineStage.OPTIMIZATION: {'optimization', 'performance_tuning', 'monitoring'}
        }
        return capabilities.get(stage, set())

    async def _prepare_stage_task_data(
        self,
        stage: PipelineStage,
        context: OpportunityContext,
        current_value: float,
        previous_results: List[StageResult]
    ) -> Dict[str, Any]:
        """Prepare task data specific to each pipeline stage"""

        base_data = {
            'pipeline_stage': stage.value,
            'opportunity_id': context.opportunity_id,
            'current_value': current_value,
            'context': context.metadata,
            'previous_results': [r.output_data for r in previous_results]
        }

        # Stage-specific enhancements
        if stage == PipelineStage.DISCOVERY:
            base_data.update({
                'task': 'Discover and analyze new opportunities',
                'focus_areas': ['market_gaps', 'competitor_analysis', 'trend_identification'],
                'platforms': [context.source_platform]
            })
        elif stage == PipelineStage.ANALYSIS:
            base_data.update({
                'task': 'Analyze opportunity viability and potential',
                'analysis_types': ['financial', 'risk', 'market', 'technical'],
                'depth': 'comprehensive' if current_value > 1000 else 'standard'
            })
        elif stage == PipelineStage.EXECUTION:
            base_data.update({
                'task': 'Execute opportunity capture strategy',
                'execution_type': 'revenue_generation',
                'target_platforms': [context.source_platform],
                'resource_allocation': self._calculate_resource_allocation(current_value)
            })
        elif stage == PipelineStage.OPTIMIZATION:
            # Session 737: Ensure current_performance is never None
            base_data.update({
                'task': 'Optimize opportunity performance and ROI',
                'optimization_targets': ['conversion_rate', 'profit_margin', 'execution_speed'],
                'current_performance': (previous_results[-1].output_data or {}) if previous_results else {}
            })

        return base_data

    def _calculate_resource_allocation(self, current_value: float) -> Dict[str, Any]:
        """Calculate resource allocation based on opportunity value"""
        if current_value > 5000:
            return {'priority': 'high', 'budget': 'premium', 'timeline': 'expedited'}
        elif current_value > 1000:
            return {'priority': 'medium', 'budget': 'standard', 'timeline': 'normal'}
        else:
            return {'priority': 'low', 'budget': 'minimal', 'timeline': 'flexible'}

    async def _monitor_agent_execution(self, execution_id: str) -> Dict[str, Any]:
        """Monitor agent execution and return results"""

        # Poll for completion (simplified implementation)
        max_wait = 300  # 5 minutes
        poll_interval = 5
        waited = 0

        while waited < max_wait:
            status = self.agent_registry.get_execution_status(execution_id)

            if not status:
                break

            if status['status'] in ['completed', 'failed', 'error']:
                return {
                    'success': status['status'] == 'completed',
                    'output_data': status.get('output_data', {}),
                    'error': status.get('error_message'),
                    'execution_time': status.get('execution_time_ms', 0)
                }

            await asyncio.sleep(poll_interval)
            waited += poll_interval

        # Timeout
        return {
            'success': False,
            'output_data': {},
            'error': 'Execution timeout',
            'execution_time': max_wait * 1000
        }

    async def _calculate_stage_quality_score(
        self,
        stage: PipelineStage,
        result: Dict[str, Any],
        context: OpportunityContext
    ) -> float:
        """Calculate quality score for a stage result"""

        if not result.get('success', False):
            return 0.0

        score = 0.5  # Base score for success
        output_data = result.get('output_data', {})

        # Stage-specific quality metrics
        if stage == PipelineStage.DISCOVERY:
            # Quality based on number and depth of opportunities found
            opportunities_found = len(output_data.get('opportunities', []))
            score += min(opportunities_found * 0.1, 0.3)

        elif stage == PipelineStage.ANALYSIS:
            # Quality based on analysis completeness and confidence
            confidence = output_data.get('confidence_score', 0.5)
            completeness = len(output_data.get('analysis_dimensions', [])) / 4.0
            score += (confidence * 0.25) + (completeness * 0.25)

        elif stage == PipelineStage.EXECUTION:
            # Quality based on execution success rate and deliverables
            execution_rate = output_data.get('execution_success_rate', 0.5)
            deliverables = len(output_data.get('deliverables', []))
            score += (execution_rate * 0.3) + min(deliverables * 0.05, 0.2)

        elif stage == PipelineStage.OPTIMIZATION:
            # Quality based on improvement metrics
            improvement = output_data.get('performance_improvement', 0)
            roi_increase = output_data.get('roi_improvement', 0)
            score += min(improvement * 0.2, 0.25) + min(roi_increase * 0.1, 0.25)

        return min(score, 1.0)

    async def _generate_next_stage_recommendations(
        self,
        stage: PipelineStage,
        result: Dict[str, Any],
        context: OpportunityContext,
        quality_score: float
    ) -> List[str]:
        """Generate recommendations for next stage agent selection"""

        recommendations = []

        if not result.get('success', False):
            return recommendations

        output_data = result.get('output_data', {})

        # High-quality results enable premium agents
        if quality_score > 0.8:
            recommendations.extend(['financial-analyst-agent', 'business-strategy-agent'])

        # Stage-specific recommendations
        if stage == PipelineStage.DISCOVERY:
            if output_data.get('high_competition', False):
                recommendations.append('competitive-intelligence-agent')
            if output_data.get('financial_complexity', 'low') == 'high':
                recommendations.append('financial-analyst-agent')

        elif stage == PipelineStage.ANALYSIS:
            confidence = output_data.get('confidence_score', 0.5)
            if confidence > 0.8:
                recommendations.extend(['business-strategy-agent', 'marketing-growth-agent'])
            elif confidence < 0.6:
                recommendations.append('risk-assessment-agent')

        elif stage == PipelineStage.EXECUTION:
            success_rate = output_data.get('execution_success_rate', 0.5)
            if success_rate > 0.7:
                recommendations.append('financial-agent')  # For optimization
            else:
                recommendations.append('operations-agent')  # For improvement

        return recommendations

    async def _should_continue_pipeline(
        self,
        stage_result: StageResult,
        context: OpportunityContext
    ) -> bool:
        """Decide whether to continue to next pipeline stage"""

        # Always continue if stage was successful with good quality
        if stage_result.success and stage_result.quality_score > 0.6:
            return True

        # Stop if critical failure
        if not stage_result.success and stage_result.stage in [
            PipelineStage.DISCOVERY, PipelineStage.ANALYSIS
        ]:
            return False

        # Continue with caution if quality is moderate
        if stage_result.quality_score > 0.4:
            return True

        # Check if opportunity value justifies risk
        if context.metadata.get('current_value', 0) > 2000:
            return True  # High value opportunities worth pushing through

        return False

    async def _score_agent_for_stage_with_memory(
        self,
        agent: Dict[str, Any],
        stage: PipelineStage,
        context: OpportunityContext,
        current_value: float,
        previous_results: List[StageResult]
    ) -> float:
        """Enhanced agent scoring using memory and embeddings"""

        # Start with base scoring
        base_score = await self._score_agent_for_stage(agent, stage, context, current_value, previous_results)

        # Memory enhancement bonuses
        memory_bonus = 0.0

        # Check agent's historical performance on similar opportunities
        # Session 737: Guard against None values at each level
        if context.memory_insights and context.memory_insights.get('agent_performance'):
            perf_dict = context.memory_insights['agent_performance']
            agent_performance = (perf_dict.get(agent['name']) or {}) if perf_dict else {}
            success_rate = agent_performance.get('success_rate', 0.5) if agent_performance else 0.5
            avg_quality = agent_performance.get('avg_quality_score', 0.5) if agent_performance else 0.5

            # Bonus for proven performance
            memory_bonus += (success_rate - 0.5) * 10.0  # Up to 5 points bonus
            memory_bonus += (avg_quality - 0.5) * 10.0   # Up to 5 points bonus

        # Similarity bonus: agents that worked well on similar opportunities
        # Session 737: Guard against None at each level
        if context.similar_opportunities:
            for similar_opp in context.similar_opportunities[:3]:
                successful_agents = similar_opp.get('successful_agents') or {}
                if successful_agents.get(stage.value) == agent['name']:
                    similarity_weight = similar_opp.get('similarity', 0.7)
                    memory_bonus += similarity_weight * 8.0  # Up to 8 points bonus

        # Opportunity type matching bonus
        if context.opportunity_embedding and self.search_engine:
            # Find agent's best-performing opportunity types
            agent_specialties = await self._get_agent_opportunity_specialties(agent['name'])
            for specialty in agent_specialties:
                if specialty['similarity'] > 0.7:  # High similarity to current opportunity
                    memory_bonus += specialty['performance_score'] * 5.0

        return base_score + memory_bonus

    async def _find_similar_successful_pipelines(self, context: OpportunityContext) -> List[Dict[str, Any]]:
        """Find similar opportunities that had successful pipeline outcomes"""

        if not self.search_engine or not context.opportunity_embedding:
            return []

        # Search for similar opportunities in memory
        similar_opportunities = []

        # This would query a pipeline results database
        # For now, return cached results or mock data
        if context.opportunity_id in self.opportunity_memory:
            return self.opportunity_memory[context.opportunity_id].get('similar_pipelines', [])

        return similar_opportunities

    async def _get_agent_opportunity_specialties(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get agent's specialties based on past opportunity performance"""

        # This would analyze historical performance data
        # Return mock specialties for now
        specialties = [
            {
                'opportunity_type': 'content_creation',
                'similarity': 0.8,
                'performance_score': 0.9,
                'success_count': 12
            },
            {
                'opportunity_type': 'market_research',
                'similarity': 0.7,
                'performance_score': 0.85,
                'success_count': 8
            }
        ]

        return specialties

    async def _log_agent_selection_reasoning(
        self,
        stage: PipelineStage,
        selected_agent: Dict[str, Any],
        all_scores: List[Tuple[Dict[str, Any], float]],
        context: OpportunityContext
    ):
        """Log agent selection reasoning for future memory learning"""

        reasoning = {
            'stage': stage.value,
            'selected_agent': selected_agent['name'],
            'selection_score': all_scores[0][1] if all_scores else 0,
            'alternatives': [
                {'agent': agent['name'], 'score': score}
                for agent, score in all_scores[1:6]  # Top 5 alternatives
            ],
            'opportunity_context': {
                'platform': context.source_platform,
                'priority': context.priority_level,
                'value': context.metadata.get('current_value', 0)
            },
            'memory_factors': {
                'used_historical_data': bool(context.memory_insights),
                'found_similar_opportunities': bool(context.similar_opportunities),
                'embedding_available': bool(context.opportunity_embedding)
            },
            'timestamp': datetime.now().isoformat()
        }

        # Store reasoning for learning
        logger.info(f"Agent selection reasoning: {reasoning}")

        # Update opportunity memory cache
        if context.opportunity_id not in self.opportunity_memory:
            self.opportunity_memory[context.opportunity_id] = {}

        if 'agent_selections' not in self.opportunity_memory[context.opportunity_id]:
            self.opportunity_memory[context.opportunity_id]['agent_selections'] = []

        self.opportunity_memory[context.opportunity_id]['agent_selections'].append(reasoning)

    async def _initialize_pipeline_context_with_memory(
        self,
        opportunity: Dict[str, Any],
        pipeline_config: Optional[Dict]
    ) -> OpportunityContext:
        """Initialize pipeline context enhanced with memory and embeddings"""

        # Start with basic context
        context = OpportunityContext(
            opportunity_id=opportunity.get('id', f"opp_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            source_platform=opportunity.get('platform', 'unknown'),
            priority_level=opportunity.get('priority', 'medium'),
            success_probability=opportunity.get('success_probability', 0.5),
            current_stage=PipelineStage.DISCOVERY,
            metadata={
                'original_opportunity': opportunity,
                'pipeline_started': datetime.now().isoformat(),
                'config': pipeline_config or {}
            },
            pipeline_config=pipeline_config or {}
        )

        # Generate opportunity embedding for semantic analysis
        if self.embedding_manager:
            context.opportunity_embedding = await self._generate_opportunity_embedding(opportunity)

        # Find similar opportunities from memory
        if self.search_engine and context.opportunity_embedding:
            context.similar_opportunities = await self._find_similar_opportunities(context.opportunity_embedding)

        # Extract memory insights for this opportunity type
        context.memory_insights = await self._extract_memory_insights(opportunity, context)

        return context

    async def _generate_opportunity_embedding(self, opportunity: Dict[str, Any]) -> Optional[List[float]]:
        """Generate embedding vector for opportunity semantic analysis"""

        if not self.embedding_manager:
            return None

        try:
            # Create comprehensive opportunity description for embedding
            opportunity_text = self._prepare_opportunity_for_embedding(opportunity)

            # Generate embedding (adapting the existing embedding method)
            # This would be similar to the CodebaseEmbeddingManager approach
            from content.ai_providers import AIProviderManager
            ai_provider = AIProviderManager()

            response = ai_provider.generate_embeddings(
                texts=[opportunity_text],
                model='text-embedding-3-small'
            )

            if response and response.get('embeddings'):
                return response['embeddings'][0]

        except Exception as e:
            logger.error(f"Error generating opportunity embedding: {e}")

        return None

    def _prepare_opportunity_for_embedding(self, opportunity: Dict[str, Any]) -> str:
        """Prepare opportunity data for embedding generation"""

        parts = []

        # Basic opportunity info
        if opportunity.get('title'):
            parts.append(f"Title: {opportunity['title']}")

        if opportunity.get('description'):
            parts.append(f"Description: {opportunity['description']}")

        if opportunity.get('platform'):
            parts.append(f"Platform: {opportunity['platform']}")

        if opportunity.get('category'):
            parts.append(f"Category: {opportunity['category']}")

        if opportunity.get('skills_required'):
            skills = ', '.join(opportunity['skills_required'][:5])  # First 5 skills
            parts.append(f"Skills: {skills}")

        if opportunity.get('budget_range'):
            parts.append(f"Budget: {opportunity['budget_range']}")

        if opportunity.get('timeline'):
            parts.append(f"Timeline: {opportunity['timeline']}")

        # Opportunity context and characteristics
        parts.append(f"Type: Opportunity for pipeline processing")
        parts.append(f"Value potential: {opportunity.get('base_value', 'unknown')}")

        return '\n'.join(parts)

    async def _find_similar_opportunities(self, opportunity_embedding: List[float]) -> List[Dict[str, Any]]:
        """Find similar opportunities using semantic search"""

        # This would search a database of past opportunities and their embeddings
        # For now, return mock similar opportunities
        similar_opportunities = [
            {
                'opportunity_id': 'opp_20241201_001',
                'similarity': 0.85,
                'final_value': 2500,
                'success_rate': 0.9,
                'successful_agents': {
                    'discovery': 'market-research-agent',
                    'analysis': 'financial-analyst-agent',
                    'execution': 'business-strategy-agent',
                    'optimization': 'financial-agent'
                },
                'completion_time': 180,  # minutes
                'quality_score': 0.87
            },
            {
                'opportunity_id': 'opp_20241128_003',
                'similarity': 0.78,
                'final_value': 1800,
                'success_rate': 0.8,
                'successful_agents': {
                    'discovery': 'reddit-scout-agent',
                    'analysis': 'data-analyst',
                    'execution': 'content-creator',
                    'optimization': 'performance-optimizer'
                },
                'completion_time': 220,
                'quality_score': 0.82
            }
        ]

        return similar_opportunities

    async def _extract_memory_insights(
        self,
        opportunity: Dict[str, Any],
        context: OpportunityContext
    ) -> Dict[str, Any]:
        """Extract memory insights for opportunity processing optimization"""

        insights = {
            'successful_agents': {},
            'agent_performance': {},
            'optimization_patterns': {},
            'risk_factors': [],
            'success_predictors': []
        }

        # Analyze similar opportunities for pattern extraction
        if context.similar_opportunities:
            # Extract successful agent patterns
            stage_agent_success = {}
            agent_performance_data = {}

            for similar_opp in context.similar_opportunities:
                # Weight by similarity and success rate
                weight = similar_opp['similarity'] * similar_opp['success_rate']

                for stage, agent in similar_opp.get('successful_agents', {}).items():
                    if stage not in stage_agent_success:
                        stage_agent_success[stage] = {}
                    if agent not in stage_agent_success[stage]:
                        stage_agent_success[stage][agent] = 0
                    stage_agent_success[stage][agent] += weight

                    # Track agent performance
                    if agent not in agent_performance_data:
                        agent_performance_data[agent] = {
                            'total_weight': 0,
                            'success_weight': 0,
                            'quality_scores': []
                        }

                    agent_performance_data[agent]['total_weight'] += 1
                    agent_performance_data[agent]['success_weight'] += similar_opp['success_rate']
                    agent_performance_data[agent]['quality_scores'].append(similar_opp['quality_score'])

            # Convert to recommendations
            for stage, agents in stage_agent_success.items():
                best_agents = sorted(agents.items(), key=lambda x: x[1], reverse=True)
                insights['successful_agents'][stage] = [agent for agent, score in best_agents[:3]]

            # Calculate agent performance metrics
            for agent, data in agent_performance_data.items():
                if data['total_weight'] > 0:
                    insights['agent_performance'][agent] = {
                        'success_rate': data['success_weight'] / data['total_weight'],
                        'avg_quality_score': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0.5,
                        'experience_level': data['total_weight']
                    }

        # Extract optimization patterns
        if context.similar_opportunities:
            avg_completion_time = sum(opp['completion_time'] for opp in context.similar_opportunities) / len(context.similar_opportunities)
            avg_value_multiplier = sum(opp['final_value'] / opportunity.get('base_value', 100) for opp in context.similar_opportunities) / len(context.similar_opportunities)

            insights['optimization_patterns'] = {
                'expected_completion_time': avg_completion_time,
                'expected_value_multiplier': avg_value_multiplier,
                'optimal_pipeline_length': 4,  # discovery -> analysis -> execution -> optimization
                'resource_allocation': self._calculate_optimal_resource_allocation(context.similar_opportunities)
            }

        # Identify risk factors based on historical data
        insights['risk_factors'] = await self._identify_historical_risk_factors(opportunity, context)

        # Identify success predictors
        insights['success_predictors'] = await self._identify_success_predictors(opportunity, context)

        return insights

    async def _generate_pipeline_report_with_memory(
        self,
        context: OpportunityContext,
        stage_results: List[StageResult],
        final_value: float,
        initial_value: float
    ) -> Dict[str, Any]:
        """Generate comprehensive pipeline execution report with memory insights"""

        # Get base report
        base_report = await self._generate_pipeline_report(context, stage_results, final_value, initial_value)

        # Add memory-specific insights
        memory_analysis = {
            'memory_utilization': {
                'used_embeddings': bool(context.opportunity_embedding),
                'found_similar_opportunities': len(context.similar_opportunities) if context.similar_opportunities else 0,
                'applied_memory_insights': bool(context.memory_insights),
                'agent_selection_enhanced': True  # We always enhance now
            },
            'learning_outcomes': {
                'new_patterns_discovered': await self._identify_new_patterns(context, stage_results),
                'agent_performance_updates': await self._generate_agent_performance_updates(context, stage_results),
                'successful_strategies': await self._extract_successful_strategies(context, stage_results, final_value),
                'failure_learnings': await self._extract_failure_learnings(context, stage_results)
            },
            'prediction_accuracy': await self._assess_prediction_accuracy(context, stage_results, final_value),
            'optimization_recommendations': await self._generate_optimization_recommendations(context, stage_results),
            'memory_update_actions': await self._plan_memory_updates(context, stage_results, final_value)
        }

        # Combine reports
        enhanced_report = {**base_report, 'memory_analysis': memory_analysis}

        # Store this pipeline's results for future memory learning
        await self._store_pipeline_results_for_memory(context, stage_results, final_value, enhanced_report)

        return enhanced_report

    async def _identify_new_patterns(self, context: OpportunityContext, stage_results: List[StageResult]) -> List[str]:
        """Identify new patterns discovered in this pipeline execution"""

        patterns = []

        # Check for unusual success combinations
        successful_agents = [r.agent_used for r in stage_results if r.success]
        if len(successful_agents) >= 3:
            agent_combo = f"{successful_agents[0]} → {successful_agents[1]} → {successful_agents[2]}"
            patterns.append(f"Successful agent combination: {agent_combo}")

        # Check for unexpected performance
        for result in stage_results:
            if result.quality_score > 0.9:
                patterns.append(f"Exceptional performance by {result.agent_used} in {result.stage.value}")
            elif result.success and result.quality_score < 0.4:
                patterns.append(f"Low-quality success by {result.agent_used} - investigate efficiency")

        # Platform-specific patterns
        if context.source_platform and len(stage_results) > 2:
            avg_quality = sum(r.quality_score for r in stage_results) / len(stage_results)
            if avg_quality > 0.8:
                patterns.append(f"High-quality pipeline pattern for {context.source_platform} opportunities")

        return patterns

    async def _generate_agent_performance_updates(self, context: OpportunityContext, stage_results: List[StageResult]) -> Dict[str, Any]:
        """Generate agent performance updates for memory learning"""

        updates = {}

        for result in stage_results:
            agent_name = result.agent_used
            if agent_name not in updates:
                updates[agent_name] = {
                    'stage_performances': [],
                    'overall_metrics': {}
                }

            updates[agent_name]['stage_performances'].append({
                'stage': result.stage.value,
                'success': result.success,
                'quality_score': result.quality_score,
                'execution_time': result.execution_time,
                'opportunity_context': {
                    'platform': context.source_platform,
                    'priority': context.priority_level
                }
            })

        return updates

    async def _extract_successful_strategies(self, context: OpportunityContext, stage_results: List[StageResult], final_value: float) -> List[str]:
        """Extract successful strategies to remember for future pipelines"""

        strategies = []

        # Value multiplication strategies
        value_multiplier = final_value / context.metadata['original_opportunity'].get('base_value', 100)
        if value_multiplier > 3.0:
            successful_agents = [r.agent_used for r in stage_results if r.success]
            strategies.append(f"High value multiplication ({value_multiplier:.1f}x) achieved with agents: {' → '.join(successful_agents)}")

        # Time efficiency strategies
        total_time = sum(r.execution_time for r in stage_results)
        if total_time < 120:  # Less than 2 minutes
            strategies.append(f"Fast execution strategy completed in {total_time:.1f}s")

        # Quality consistency strategies
        quality_scores = [r.quality_score for r in stage_results if r.success]
        if quality_scores and min(quality_scores) > 0.7:
            strategies.append("High quality consistency maintained across all stages")

        return strategies

    async def _extract_failure_learnings(self, context: OpportunityContext, stage_results: List[StageResult]) -> List[str]:
        """Extract failure learnings to avoid in future pipelines"""

        learnings = []

        failed_stages = [r for r in stage_results if not r.success]
        for failure in failed_stages:
            learnings.append(f"Agent {failure.agent_used} failed in {failure.stage.value} stage - consider alternative agents")

        # Pattern analysis for prevention
        if len(failed_stages) > 1:
            learnings.append("Multiple stage failures - review pipeline complexity and agent compatibility")

        return learnings

    async def _assess_prediction_accuracy(self, context: OpportunityContext, stage_results: List[StageResult], final_value: float) -> Dict[str, Any]:
        """Assess how accurate our memory-based predictions were"""

        accuracy = {}

        if context.memory_insights and context.memory_insights.get('optimization_patterns'):
            predicted_value = context.memory_insights['optimization_patterns'].get('expected_value_multiplier', 1.0)
            actual_multiplier = final_value / context.metadata['original_opportunity'].get('base_value', 100)

            accuracy['value_prediction'] = {
                'predicted_multiplier': predicted_value,
                'actual_multiplier': actual_multiplier,
                'accuracy_score': 1.0 - abs(predicted_value - actual_multiplier) / max(predicted_value, actual_multiplier)
            }

            predicted_time = context.memory_insights['optimization_patterns'].get('expected_completion_time', 200)
            actual_time = sum(r.execution_time for r in stage_results)

            accuracy['time_prediction'] = {
                'predicted_time': predicted_time,
                'actual_time': actual_time,
                'accuracy_score': 1.0 - abs(predicted_time - actual_time) / max(predicted_time, actual_time)
            }

        return accuracy

    async def _generate_optimization_recommendations(self, context: OpportunityContext, stage_results: List[StageResult]) -> List[str]:
        """Generate optimization recommendations based on memory analysis"""

        recommendations = []

        # Agent optimization recommendations
        for result in stage_results:
            if result.execution_time > 60:  # Slow execution
                recommendations.append(f"Consider faster alternatives to {result.agent_used} for {result.stage.value} stage")

            if result.success and result.quality_score < 0.6:  # Low quality
                recommendations.append(f"Improve quality standards for {result.agent_used} in {result.stage.value} stage")

        # Pipeline optimization
        avg_quality = sum(r.quality_score for r in stage_results) / len(stage_results) if stage_results else 0
        if avg_quality < 0.7:
            recommendations.append("Overall pipeline quality below target - review agent selection criteria")

        # Memory utilization optimization
        if not context.opportunity_embedding:
            recommendations.append("Enable opportunity embedding generation for better agent selection")

        return recommendations

    async def _plan_memory_updates(self, context: OpportunityContext, stage_results: List[StageResult], final_value: float) -> List[str]:
        """Plan updates to memory based on pipeline results"""

        updates = []

        # Agent performance tracking updates
        for result in stage_results:
            updates.append(f"Update {result.agent_used} performance metrics for {result.stage.value} stage")

        # Pattern recognition updates
        if final_value > context.metadata['original_opportunity'].get('base_value', 100) * 2:
            updates.append("Add high-value pipeline pattern to successful strategies database")

        # Similarity updates
        if context.opportunity_embedding:
            updates.append("Update opportunity embedding similarity index with new successful pattern")

        return updates

    async def _store_pipeline_results_for_memory(
        self,
        context: OpportunityContext,
        stage_results: List[StageResult],
        final_value: float,
        report: Dict[str, Any]
    ):
        """Store pipeline results for future memory learning"""

        # Create comprehensive memory record
        memory_record = {
            'opportunity_id': context.opportunity_id,
            'opportunity_embedding': context.opportunity_embedding,
            'opportunity_characteristics': {
                'platform': context.source_platform,
                'priority': context.priority_level,
                'base_value': context.metadata['original_opportunity'].get('base_value', 100),
                'final_value': final_value,
                'value_multiplier': final_value / context.metadata['original_opportunity'].get('base_value', 100)
            },
            'pipeline_execution': {
                'stages_completed': len(stage_results),
                'successful_agents': {r.stage.value: r.agent_used for r in stage_results if r.success},
                'stage_quality_scores': {r.stage.value: r.quality_score for r in stage_results},
                'total_execution_time': sum(r.execution_time for r in stage_results),
                'overall_success_rate': len([r for r in stage_results if r.success]) / len(stage_results) if stage_results else 0
            },
            'success_metrics': {
                'pipeline_successful': len([r for r in stage_results if r.success]) >= 3,
                'high_quality': all(r.quality_score > 0.7 for r in stage_results if r.success),
                'efficient_execution': sum(r.execution_time for r in stage_results) < 180
            },
            'timestamp': datetime.now().isoformat()
        }

        # Store in opportunity memory cache
        self.opportunity_memory[context.opportunity_id]['pipeline_results'] = memory_record

        logger.info(f"Stored pipeline results for memory learning: {context.opportunity_id}")

    def _calculate_optimal_resource_allocation(self, similar_opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate optimal resource allocation based on historical patterns"""

        high_value_opps = [opp for opp in similar_opportunities if opp['final_value'] > 2000]

        if len(high_value_opps) > len(similar_opportunities) * 0.5:
            return {'priority': 'high', 'budget': 'premium', 'timeline': 'expedited'}
        else:
            return {'priority': 'medium', 'budget': 'standard', 'timeline': 'normal'}

    async def _identify_historical_risk_factors(
        self,
        opportunity: Dict[str, Any],
        context: OpportunityContext
    ) -> List[str]:
        """Identify potential risk factors based on historical patterns"""

        risk_factors = []

        # Platform-specific risks
        if opportunity.get('platform') == 'reddit':
            risk_factors.append('High competition on Reddit - ensure unique angle')
        elif opportunity.get('platform') == 'freelance':
            risk_factors.append('Client communication challenges common in freelance')

        # Value-based risks
        if opportunity.get('base_value', 0) > 5000:
            risk_factors.append('High-value opportunity - increased quality expectations')

        # Timeline risks
        if opportunity.get('timeline', '').lower() in ['urgent', 'asap', 'immediate']:
            risk_factors.append('Tight timeline - may require parallel processing')

        return risk_factors

    async def _identify_success_predictors(
        self,
        opportunity: Dict[str, Any],
        context: OpportunityContext
    ) -> List[str]:
        """Identify factors that predict pipeline success"""

        predictors = []

        # Positive indicators from similar opportunities
        if context.similar_opportunities:
            avg_success_rate = sum(opp['success_rate'] for opp in context.similar_opportunities) / len(context.similar_opportunities)
            if avg_success_rate > 0.8:
                predictors.append('High success rate for similar opportunities')

        # Opportunity characteristics
        if opportunity.get('skills_required'):
            if len(opportunity['skills_required']) <= 3:
                predictors.append('Focused skill requirements increase success probability')

        if opportunity.get('budget_range'):
            if 'negotiable' in opportunity['budget_range'].lower():
                predictors.append('Flexible budget indicates client commitment')

        return predictors

    async def _initialize_pipeline_context(
        self,
        opportunity: Dict[str, Any],
        pipeline_config: Optional[Dict]
    ) -> OpportunityContext:
        """Initialize pipeline execution context"""

        return OpportunityContext(
            opportunity_id=opportunity.get('id', f"opp_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            source_platform=opportunity.get('platform', 'unknown'),
            priority_level=opportunity.get('priority', 'medium'),
            success_probability=opportunity.get('success_probability', 0.5),
            current_stage=PipelineStage.DISCOVERY,
            metadata={
                'original_opportunity': opportunity,
                'pipeline_started': datetime.now().isoformat(),
                'config': pipeline_config or {}
            },
            pipeline_config=pipeline_config or {}
        )

    async def _create_pipeline_tracking(self, context: OpportunityContext) -> str:
        """Create pipeline tracking record"""
        # This would create a tracking record in the database
        # For now, return a generated ID
        pipeline_id = f"pipeline_{context.opportunity_id}_{int(datetime.now().timestamp())}"
        logger.info(f"Created pipeline tracking: {pipeline_id}")
        return pipeline_id

    async def _update_pipeline_tracking(self, pipeline_id: str, report: Dict[str, Any]):
        """Update pipeline tracking with final results"""
        logger.info(f"Updated pipeline tracking {pipeline_id} with results")
        # This would update the database record

    async def _generate_pipeline_report(
        self,
        context: OpportunityContext,
        stage_results: List[StageResult],
        final_value: float,
        initial_value: float
    ) -> Dict[str, Any]:
        """Generate comprehensive pipeline execution report"""

        successful_stages = [r for r in stage_results if r.success]
        total_execution_time = sum(r.execution_time for r in stage_results)
        avg_quality_score = sum(r.quality_score for r in stage_results) / len(stage_results) if stage_results else 0

        return {
            'pipeline_id': context.opportunity_id,
            'execution_summary': {
                'stages_completed': len(stage_results),
                'stages_successful': len(successful_stages),
                'success_rate': len(successful_stages) / len(stage_results) if stage_results else 0,
                'total_execution_time': total_execution_time,
                'avg_quality_score': avg_quality_score
            },
            'value_analysis': {
                'initial_value': initial_value,
                'final_value': final_value,
                'value_multiplier': final_value / initial_value if initial_value > 0 else 0,
                'roi_potential': (final_value - initial_value) / initial_value if initial_value > 0 else 0
            },
            'stage_performance': [
                {
                    'stage': r.stage.value,
                    'success': r.success,
                    'agent_used': r.agent_used,
                    'execution_time': r.execution_time,
                    'quality_score': r.quality_score
                }
                for r in stage_results
            ],
            'recommendations': {
                'next_actions': self._generate_final_recommendations(stage_results, final_value),
                'optimization_opportunities': self._identify_optimization_opportunities(stage_results),
                'risk_factors': self._identify_risk_factors(stage_results)
            },
            'generated_at': datetime.now().isoformat()
        }

    def _generate_final_recommendations(
        self,
        stage_results: List[StageResult],
        final_value: float
    ) -> List[str]:
        """Generate final action recommendations"""

        recommendations = []

        if final_value > 5000:
            recommendations.append("High-value opportunity - consider immediate execution")
        elif final_value > 1000:
            recommendations.append("Medium-value opportunity - proceed with standard process")
        else:
            recommendations.append("Low-value opportunity - consider batch processing")

        # Quality-based recommendations
        if stage_results:
            avg_quality = sum(r.quality_score for r in stage_results) / len(stage_results)
            if avg_quality > 0.8:
                recommendations.append("High quality pipeline - fast-track execution")
            elif avg_quality < 0.5:
                recommendations.append("Quality concerns - additional review recommended")

        return recommendations

    def _identify_optimization_opportunities(self, stage_results: List[StageResult]) -> List[str]:
        """Identify optimization opportunities"""
        opportunities = []

        for result in stage_results:
            if result.execution_time > 60:  # More than 1 minute
                opportunities.append(f"Optimize {result.stage.value} stage performance")
            if result.quality_score < 0.6:
                opportunities.append(f"Improve {result.stage.value} stage quality")

        return opportunities

    def _identify_risk_factors(self, stage_results: List[StageResult]) -> List[str]:
        """Identify risk factors"""
        risks = []

        failed_stages = [r for r in stage_results if not r.success]
        if failed_stages:
            risks.append(f"{len(failed_stages)} stage(s) failed - review pipeline health")

        low_quality_stages = [r for r in stage_results if r.quality_score < 0.4]
        if low_quality_stages:
            risks.append(f"{len(low_quality_stages)} stage(s) have low quality scores")

        return risks

    async def _create_optimized_opportunity(
        self,
        original_opportunity: Dict[str, Any],
        stage_results: List[StageResult],
        final_value: float
    ) -> Dict[str, Any]:
        """Create optimized opportunity based on pipeline results"""

        optimized = original_opportunity.copy()
        optimized.update({
            'optimized_value': final_value,
            'pipeline_enhanced': True,
            'quality_score': sum(r.quality_score for r in stage_results) / len(stage_results) if stage_results else 0,
            'success_probability': min(original_opportunity.get('success_probability', 0.5) * 1.5, 0.95),
            'pipeline_results': [r.output_data for r in stage_results if r.success],
            'optimized_at': datetime.now().isoformat()
        })

        return optimized

    def _serialize_stage_result(self, result: StageResult) -> Dict[str, Any]:
        """Serialize stage result for JSON output"""
        return {
            'stage': result.stage.value,
            'success': result.success,
            'agent_used': result.agent_used,
            'execution_time': result.execution_time,
            'quality_score': result.quality_score,
            'output_data': result.output_data,
            'next_stage_recommendations': result.next_stage_recommendations
        }

    # Public API methods for external integration

    async def quick_opportunity_assessment(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Quick assessment of opportunity potential without full pipeline"""

        # Run just discovery and analysis stages
        context = await self._initialize_pipeline_context(opportunity, {'mode': 'assessment'})

        discovery_result = await self._execute_pipeline_stage(
            PipelineStage.DISCOVERY, context, opportunity.get('base_value', 100), []
        )

        if not discovery_result.success:
            return {
                'success': False,
                'error': 'Discovery stage failed',
                'assessment': 'negative'
            }

        analysis_result = await self._execute_pipeline_stage(
            PipelineStage.ANALYSIS, context, opportunity.get('base_value', 100), [discovery_result]
        )

        # Generate assessment
        quality_avg = (discovery_result.quality_score + analysis_result.quality_score) / 2

        if quality_avg > 0.7:
            assessment = 'highly_positive'
        elif quality_avg > 0.5:
            assessment = 'positive'
        elif quality_avg > 0.3:
            assessment = 'neutral'
        else:
            assessment = 'negative'

        return {
            'success': True,
            'assessment': assessment,
            'quality_score': quality_avg,
            'estimated_value': opportunity.get('base_value', 100) * (1 + quality_avg),
            'recommendations': discovery_result.next_stage_recommendations + analysis_result.next_stage_recommendations
        }

    async def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get current status of a running pipeline"""
        # This would query the database for pipeline status
        # For now, return a mock status
        return {
            'pipeline_id': pipeline_id,
            'status': 'running',
            'current_stage': 'analysis',
            'progress': 0.4,
            'estimated_completion': (datetime.now() + timedelta(minutes=15)).isoformat()
        }

    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancel a running pipeline"""
        # This would cancel any running agents and update status
        logger.info(f"Cancelling pipeline: {pipeline_id}")
        return True

    async def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get overall pipeline performance metrics"""
        return {
            'total_pipelines_executed': 0,  # Would query database
            'average_value_multiplication': 2.1,
            'average_execution_time': 180,  # seconds
            'success_rate': 0.85,
            'top_performing_stages': ['analysis', 'execution'],
            'agent_utilization': {
                'discovery': 0.7,
                'analysis': 0.9,
                'execution': 0.8,
                'optimization': 0.6
            }
        }