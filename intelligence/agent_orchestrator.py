"""
Agent Orchestrator - Session 28 Core Component

Orchestrates multiple agents for complex tasks that require coordination.
Implements three coordination patterns: parallel, sequential, and hierarchical.

Features:
- Select best agents for tasks based on specialization and performance
- Execute multiple agents in parallel, sequential, or hierarchical mode
- Aggregate results from multiple agents
- Track orchestration performance
- Handle agent failures and retries
- Route tasks to specialist agents
"""

import logging
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from agents.models import (
    UnifiedAgentTemplate,
    AgentOrchestration,
    AgentExecution,
    AgentPerformanceMetrics,
    AgentStatus
)
from intelligence.agent_executor import AgentExecutor
from intelligence.agent_learning import AgentLearningSystem

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrate multiple agents for complex tasks

    Usage:
        orchestrator = AgentOrchestrator()

        # Select agents
        agents = orchestrator.select_agents_for_task(
            task='income_opportunity_discovery',
            domain='freelancing',
            required_capabilities=['job_search']
        )

        # Execute in parallel
        results = orchestrator.execute_multi_agent(
            agents=agents,
            task="Find freelance web development opportunities",
            coordination='parallel'
        )
    """

    def __init__(self):
        """Initialize orchestrator"""
        self.executor = AgentExecutor()
        logger.info("AgentOrchestrator initialized")

    def select_agents_for_task(
        self,
        task: str,
        domain: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
        sport_type: Optional[str] = None,
        max_agents: int = 5
    ) -> List[UnifiedAgentTemplate]:
        """
        Select best agents for a task

        Args:
            task: Task description or type
            domain: Domain tag to filter by
            required_capabilities: Required capabilities
            sport_type: Sport type for sports-related tasks
            max_agents: Maximum number of agents to select

        Returns:
            List of UnifiedAgentTemplate instances
        """
        logger.info(f"Selecting agents for task: {task}")
        logger.info(f"Domain: {domain}, Capabilities: {required_capabilities}, Sport: {sport_type}")

        # Start with all active agents
        agents = UnifiedAgentTemplate.objects.filter(is_active=True)

        # Filter by domain tags if provided
        if domain:
            agents = agents.filter(domain_tags__contains=[domain])

        # Filter by capabilities if provided
        if required_capabilities:
            for capability in required_capabilities:
                agents = agents.filter(capabilities__contains=[capability])

        # If sport type provided, prioritize agents with good performance in that sport
        if sport_type:
            # Get agents with performance metrics for this sport
            agents_with_metrics = AgentPerformanceMetrics.objects.filter(
                sport_type=sport_type,
                sport_predictions__gte=10,  # At least 10 predictions
                sport_accuracy__gte=0.50  # At least 50% accuracy
            ).select_related('agent').order_by('-sport_accuracy')

            # Extract agent IDs
            agent_ids = [m.agent.id for m in agents_with_metrics]

            # Filter and order by performance
            if agent_ids:
                agents = agents.filter(id__in=agent_ids)
                # Order by IDs to match performance order
                agents = sorted(agents, key=lambda a: agent_ids.index(a.id) if a.id in agent_ids else 999)

        # If no sport-specific filtering, order by general performance
        else:
            agents = agents.order_by('-success_rate', '-confidence_score', '-usage_count')

        # Limit to max_agents
        agents = list(agents[:max_agents])

        logger.info(f"Selected {len(agents)} agents: {[a.name for a in agents]}")

        return agents

    def execute_multi_agent(
        self,
        agents: List[UnifiedAgentTemplate],
        task: str,
        context: Optional[Dict[str, Any]] = None,
        coordination: str = 'parallel',
        user: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Execute multiple agents with coordination

        Args:
            agents: List of agents to execute
            task: Task description
            context: Task context
            coordination: Coordination mode ('parallel', 'sequential', 'hierarchical')
            user: User who initiated orchestration

        Returns:
            Dict with orchestration results
        """
        context = context or {}

        logger.info(f"Executing multi-agent orchestration: {coordination}")
        logger.info(f"Agents: {[a.name for a in agents]}")
        logger.info(f"Task: {task}")

        # Create orchestration record
        orchestration = AgentOrchestration.objects.create(
            name=f"orchestration_{coordination}_{int(time.time())}",
            description=task,
            workflow_definition={
                'agents': [a.name for a in agents],
                'coordination': coordination,
                'task': task,
                'context': context
            },
            agent_sequence=[a.name for a in agents],
            execution_strategy=coordination if coordination in ['sequential', 'parallel'] else 'sequential',
            status=AgentStatus.RUNNING,
            user=user
        )

        try:
            # Execute based on coordination mode
            if coordination == 'parallel':
                executions = self._execute_parallel(agents, task, context, orchestration, user)
            elif coordination == 'sequential':
                executions = self._execute_sequential(agents, task, context, orchestration, user)
            elif coordination == 'hierarchical':
                executions = self._execute_hierarchical(agents, task, context, orchestration, user)
            else:
                raise ValueError(f"Unsupported coordination mode: {coordination}")

            # Aggregate results
            aggregated_results = self._aggregate_results(executions)

            # Update orchestration
            orchestration.status = AgentStatus.COMPLETED
            orchestration.completed_at = timezone.now()
            orchestration.save()

            logger.info(f"Orchestration completed: {len(executions)} agents executed")

            return {
                'orchestration_id': orchestration.id,
                'status': 'completed',
                'agents_executed': len(executions),
                'executions': [
                    {
                        'agent': e.template.name,
                        'status': e.status,
                        'result': e.result
                    }
                    for e in executions
                ],
                'aggregated': aggregated_results,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}", exc_info=True)

            # Update orchestration with error
            orchestration.status = AgentStatus.FAILED
            orchestration.completed_at = timezone.now()
            orchestration.save()

            return {
                'orchestration_id': orchestration.id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _execute_parallel(
        self,
        agents: List[UnifiedAgentTemplate],
        task: str,
        context: Dict,
        orchestration: AgentOrchestration,
        user: Optional[Any]
    ) -> List[AgentExecution]:
        """Execute agents in parallel"""
        logger.info("Executing agents in parallel")

        executions = []

        for agent in agents:
            try:
                execution = self.executor.execute_agent(
                    agent=agent,
                    task=task,
                    context=context,
                    orchestration=orchestration,
                    user=user
                )
                executions.append(execution)

            except Exception as e:
                logger.error(f"Agent {agent.name} failed: {str(e)}")
                continue

        return executions

    def _execute_sequential(
        self,
        agents: List[UnifiedAgentTemplate],
        task: str,
        context: Dict,
        orchestration: AgentOrchestration,
        user: Optional[Any]
    ) -> List[AgentExecution]:
        """Execute agents sequentially"""
        logger.info("Executing agents sequentially")

        executions = []
        accumulated_context = context.copy()

        for agent in agents:
            try:
                # Execute agent
                execution = self.executor.execute_agent(
                    agent=agent,
                    task=task,
                    context=accumulated_context,
                    orchestration=orchestration,
                    user=user
                )
                executions.append(execution)

                # Add this agent's result to context for next agent
                if execution.status == AgentStatus.COMPLETED:
                    accumulated_context[f'previous_agent_{agent.name}'] = execution.result

            except Exception as e:
                logger.error(f"Agent {agent.name} failed: {str(e)}")
                # In sequential mode, failure stops the chain
                break

        return executions

    def _execute_hierarchical(
        self,
        agents: List[UnifiedAgentTemplate],
        task: str,
        context: Dict,
        orchestration: AgentOrchestration,
        user: Optional[Any]
    ) -> List[AgentExecution]:
        """
        Execute agents hierarchically (lead agent coordinates others)

        First agent is the lead, others are specialists
        """
        logger.info("Executing agents hierarchically")

        if not agents:
            return []

        executions = []

        # First agent is the lead
        lead_agent = agents[0]
        specialist_agents = agents[1:]

        # Execute specialists first
        specialist_results = []
        for specialist in specialist_agents:
            try:
                execution = self.executor.execute_agent(
                    agent=specialist,
                    task=task,
                    context=context,
                    orchestration=orchestration,
                    user=user
                )
                executions.append(execution)

                if execution.status == AgentStatus.COMPLETED:
                    specialist_results.append({
                        'agent': specialist.name,
                        'result': execution.result
                    })

            except Exception as e:
                logger.error(f"Specialist {specialist.name} failed: {str(e)}")
                continue

        # Lead agent synthesizes specialist results
        lead_context = context.copy()
        lead_context['specialist_results'] = specialist_results

        lead_task = f"{task}\n\nSynthesize results from {len(specialist_results)} specialists."

        try:
            lead_execution = self.executor.execute_agent(
                agent=lead_agent,
                task=lead_task,
                context=lead_context,
                orchestration=orchestration,
                user=user
            )
            executions.append(lead_execution)

        except Exception as e:
            logger.error(f"Lead agent {lead_agent.name} failed: {str(e)}")

        return executions

    def _aggregate_results(self, executions: List[AgentExecution]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agent executions

        Returns:
            Aggregated results dictionary
        """
        logger.info(f"Aggregating results from {len(executions)} executions")

        completed = [e for e in executions if e.status == AgentStatus.COMPLETED]
        failed = [e for e in executions if e.status == AgentStatus.FAILED]

        # Collect all results
        all_results = []
        for execution in completed:
            if execution.result:
                duration_ms = (execution.execution_time_seconds * 1000) if execution.execution_time_seconds else 0
                all_results.append({
                    'agent': execution.template.name,
                    'result': execution.result,
                    'tokens': execution.token_usage.get('total', 0) if execution.token_usage else 0,
                    'duration_ms': duration_ms
                })

        # Get token and duration totals
        total_tokens = 0
        total_duration = 0
        for e in executions:
            if e.token_usage:
                total_tokens += e.token_usage.get('total', 0)
            if e.execution_time_seconds:
                total_duration += e.execution_time_seconds * 1000  # Convert to ms

        return {
            'total_executions': len(executions),
            'agents_executed': len(executions),
            'completed': len(completed),
            'failed': len(failed),
            'success_rate': len(completed) / len(executions) if executions else 0,
            'aggregated': {
                'success_rate': len(completed) / len(executions) if executions else 0,
                'total_tokens': total_tokens,
                'total_duration_ms': total_duration
            },
            'results': all_results,
            'total_tokens': total_tokens,
            'total_duration_ms': total_duration
        }

    def route_task_to_specialist(
        self,
        task: str,
        domain: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to route a task to the best specialist

        Args:
            task: Task description
            domain: Domain (e.g., 'sports', 'freelancing', 'content')
            context: Optional context

        Returns:
            Execution result
        """
        # Select single best agent
        agents = self.select_agents_for_task(
            task=task,
            domain=domain,
            max_agents=1
        )

        if not agents:
            return {
                'status': 'failed',
                'error': f'No agents found for domain: {domain}'
            }

        # Execute single agent
        execution = self.executor.execute_agent(
            agent=agents[0],
            task=task,
            context=context
        )

        return {
            'status': execution.status,
            'agent': execution.template.name,
            'result': execution.result,
            'execution_id': execution.id
        }