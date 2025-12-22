"""
Opportunity Pipeline Agent - Clean Architecture Wrapper
========================================================

Session 393: Refactored to use BaseAgent while preserving legacy orchestrator.

This module provides a clean architecture adapter for the legacy OpportunityPipelineOrchestrator.
It wraps the existing async orchestrator to work with the synchronous BaseAgent pattern
while preserving all its sophisticated pipeline functionality.

Key Features Preserved:
    - Multi-stage pipeline orchestration (DISCOVERY → ANALYSIS → EXECUTION → OPTIMIZATION)
    - Dynamic agent selection with memory-enhanced scoring
    - Compound value multiplication through stages
    - Cross-platform opportunity management
    - Real-time performance monitoring
    - Adaptive workflow optimization

Why a Wrapper?
    The legacy OpportunityPipelineOrchestrator has complex async logic for:
    - Parallel stage execution
    - Memory-enhanced agent selection
    - Embedding-based similar opportunity search
    - Value multiplication calculations
    - Pipeline tracking and reporting

    Instead of rewriting, we wrap it to gain:
    - TimeTravelMixin for decision tracking
    - Consistent AgentResult interface
    - Clean architecture compatibility
    - Synchronous execute() signature

Usage:
    from core.agents.opportunity_pipeline_agent import OpportunityPipelineAgent

    agent = OpportunityPipelineAgent(user=request.user)
    result = agent.execute(
        task="Process freelance opportunity",
        context={'opportunity': {...}},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, List, Optional
from asgiref.sync import async_to_sync

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


# Pipeline stages for reference
PIPELINE_STAGES = [
    'DISCOVERY',   # Research and market intelligence
    'ANALYSIS',    # Financial and risk assessment
    'EXECUTION',   # Strategy and implementation
    'OPTIMIZATION', # Performance tuning
    'MONITORING',  # Ongoing performance tracking
]


class OpportunityPipelineAgent(BaseAgent):
    """
    Clean architecture wrapper for the legacy OpportunityPipelineOrchestrator.

    This agent orchestrates multi-stage opportunity execution workflows where
    each stage adds compound value before passing to the next specialist.

    Pipeline Stages:
        1. DISCOVERY - Research, competitive intelligence, opportunity validation
        2. ANALYSIS - Financial analysis, risk assessment, data analysis
        3. EXECUTION - Business strategy, content creation, marketing execution
        4. OPTIMIZATION - Performance tuning, financial optimization, monitoring

    Value Multiplication:
        Each successful stage multiplies the opportunity's value:
        - Discovery: 1.2x
        - Analysis: 1.5x
        - Execution: 2.0x
        - Optimization: 2.5x

    Agents Used Per Stage:
        - Discovery: reddit-scout-agent, market-research-agent, competitive-intelligence-agent
        - Analysis: financial-analyst-agent, risk-assessment-agent, data-analyst
        - Execution: business-strategy-agent, content-creator, marketing-growth-agent
        - Optimization: financial-agent, operations-agent, performance-optimizer
    """

    name = "OpportunityPipelineAgent"

    system_prompt = """You are OpportunityPipelineAgent, a specialist in multi-stage opportunity orchestration.

Your job is to take opportunities from discovery through optimization, maximizing value at each stage.

Pipeline Stages:
1. DISCOVERY - Find and validate opportunities via spider network and research
2. ANALYSIS - Analyze financial viability and risk factors
3. EXECUTION - Execute strategies to capture the opportunity
4. OPTIMIZATION - Optimize performance and maximize returns

Each successful stage multiplies the opportunity's value:
- Discovery: 1.2x
- Analysis: 1.5x
- Execution: 2.0x
- Optimization: 2.5x

You orchestrate these stages, selecting the best agents for each phase based on:
- Stage requirements
- Agent capabilities and success rates
- Previous stage recommendations
- Memory-enhanced scoring from past executions

You produce comprehensive pipeline reports with value calculations and recommendations."""

    tools = []  # No GPT tools - pipeline is executed programmatically

    def __init__(self, user=None):
        """Initialize the pipeline agent."""
        super().__init__(user)
        self._legacy_orchestrator = None

    @property
    def legacy_orchestrator(self):
        """Lazy-load the legacy OpportunityPipelineOrchestrator."""
        if self._legacy_orchestrator is None:
            from agents.opportunity_pipeline_orchestrator import OpportunityPipelineOrchestrator
            self._legacy_orchestrator = OpportunityPipelineOrchestrator()
        return self._legacy_orchestrator

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute an opportunity through the pipeline.

        Args:
            task: Description of the opportunity processing task
            context: Must contain 'opportunity' key with opportunity data.
                     Can also contain: pipeline_config, base_value, etc.
            scifi_context: Sci-fi features context (mood, memory, evolution)
            spider_context: Spider intelligence context (trends, market data)

        Returns:
            AgentResult with pipeline execution results
        """
        start_time = time.time()
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        with self.time_travel_session("opportunity_pipeline", task, input_data=context):
            try:
                # Extract opportunity from context
                opportunity = context.get('opportunity')

                if not opportunity:
                    return AgentResult(
                        success=False,
                        error="No 'opportunity' provided in context. Expected opportunity data dict.",
                        agent_name=self.name
                    )

                # Ensure opportunity has required fields
                if not isinstance(opportunity, dict):
                    opportunity = {'title': str(opportunity), 'base_value': 100}

                if 'base_value' not in opportunity:
                    opportunity['base_value'] = context.get('base_value', 100)

                if 'title' not in opportunity:
                    opportunity['title'] = task

                self.record_decision(
                    decision_type="pipeline_start",
                    action=f"Starting pipeline for: {opportunity.get('title', 'Unknown')[:50]}",
                    reasoning=f"Base value: ${opportunity.get('base_value', 100)}",
                    alternatives=["skip_pipeline", "manual_processing"],
                    confidence=0.9
                )

                # Get pipeline config from context
                pipeline_config = context.get('pipeline_config')

                # Execute pipeline via legacy orchestrator (async to sync)
                legacy_result = async_to_sync(
                    self.legacy_orchestrator.orchestrate_opportunity_pipeline
                )(opportunity, pipeline_config)

                execution_time = int((time.time() - start_time) * 1000)

                # Convert legacy result to AgentResult
                if legacy_result.get('success'):
                    value_mult = legacy_result.get('value_multiplication', 1.0)
                    final_value = legacy_result.get('final_value', opportunity.get('base_value', 100))

                    result = AgentResult(
                        success=True,
                        message=f"Pipeline completed with {value_mult:.1f}x value multiplication. Final value: ${final_value:.2f}",
                        data={
                            'pipeline_id': legacy_result.get('pipeline_id'),
                            'final_value': final_value,
                            'value_multiplication': value_mult,
                            'stages_executed': legacy_result.get('stages_executed', 0),
                            'stage_results': legacy_result.get('stage_results', []),
                            'pipeline_report': legacy_result.get('pipeline_report'),
                            'optimized_opportunity': legacy_result.get('optimized_opportunity'),
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=[]
                    )

                    self.mark_decision_outcome(
                        success=True,
                        result_summary=f"Pipeline achieved {value_mult:.1f}x value multiplication"
                    )

                    # Learning hooks
                    self._record_learning_outcome(
                        result, task, context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )

                    if value_mult > 1.5:
                        self._create_execution_memory(result, task, "success", 0.9)
                        self._share_knowledge(
                            knowledge_type='technique',
                            title=f"High-value pipeline: {value_mult:.1f}x",
                            knowledge_value={
                                'opportunity_type': opportunity.get('type', 'unknown'),
                                'value_multiplication': value_mult,
                                'stages_executed': legacy_result.get('stages_executed', 0),
                                'execution_time_ms': execution_time
                            },
                            confidence=min(0.95, 0.5 + value_mult * 0.1)
                        )
                    else:
                        self._create_execution_memory(result, task, "success", 0.6)

                    return result

                else:
                    result = AgentResult(
                        success=False,
                        error=legacy_result.get('error', 'Pipeline execution failed'),
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        data={
                            'partial_results': legacy_result.get('partial_results', []),
                        }
                    )

                    self.mark_decision_outcome(
                        success=False,
                        result_summary="Pipeline failed"
                    )

                    self._record_learning_outcome(result, task, context)
                    self._create_execution_memory(result, task, "failure", 0.7)

                    return result

            except Exception as e:
                logger.error(f"OpportunityPipelineAgent error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        This agent doesn't use GPT tools - pipeline is executed programmatically.

        Returns:
            Error dict since tools shouldn't be called
        """
        return {
            'success': False,
            'error': f"OpportunityPipelineAgent uses programmatic pipeline execution. "
                    f"Pass 'opportunity' in context instead."
        }

    def get_value_multipliers(self) -> Dict[str, float]:
        """
        Get the value multipliers for each pipeline stage.

        Returns:
            Dict mapping stage names to multipliers
        """
        return {
            'DISCOVERY': 1.2,
            'ANALYSIS': 1.5,
            'EXECUTION': 2.0,
            'OPTIMIZATION': 2.5,
        }

    def get_stage_agents(self) -> Dict[str, List[str]]:
        """
        Get the agents used for each pipeline stage.

        Returns:
            Dict mapping stage names to agent lists
        """
        return self.legacy_orchestrator.stage_agents

    @classmethod
    def get_pipeline_stages(cls) -> List[str]:
        """Return list of pipeline stages."""
        return PIPELINE_STAGES.copy()


# Factory function for backwards compatibility
def get_opportunity_pipeline_agent(user=None) -> OpportunityPipelineAgent:
    """
    Factory function to create an OpportunityPipelineAgent.

    Args:
        user: Django User object

    Returns:
        OpportunityPipelineAgent instance
    """
    return OpportunityPipelineAgent(user=user)
