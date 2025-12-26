"""
Session 555 - Phase B: Artifact Execution Service

Routes approved artifacts to appropriate agents for execution.
Tracks execution attempts and updates artifact status upon completion.
"""

import logging
import time
from typing import Dict, Any, Optional, List

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class ArtifactExecutionService:
    """
    Routes approved ExtractedArtifacts to appropriate agents for execution.

    Flow:
    1. Find approved artifacts without completed executions
    2. Select appropriate agent based on artifact type
    3. Route task via AgentRouter
    4. Track execution result
    5. Update artifact status to 'implemented' on success
    """

    # Map artifact types to default agents
    DEFAULT_AGENTS = {
        'proposal': 'CTOAgent',
        'experiment': 'ResearchAgent',
        'action_item': 'WorkflowAgent',
        'risk': 'COOAgent',
        'question': 'PersonalAssistantAgent',
        'data_spec': 'FullStackDeveloperAgent',
        'insight': 'ContentStrategyAgent',
    }

    # Agent specializations for smarter routing
    AGENT_SPECIALIZATIONS = {
        # Code-related artifacts
        'code': ['FullStackDeveloperAgent', 'CodeGeneratorAgent', 'CodeReviewAgent'],
        'api': ['FullStackDeveloperAgent', 'DevOpsAgent'],
        'database': ['FullStackDeveloperAgent', 'DevOpsAgent'],

        # Content-related artifacts
        'content': ['ContentStrategyAgent', 'BrandIdentityAgent'],
        'marketing': ['SocialMediaAgent', 'SEOOptimizerAgent', 'ContentStrategyAgent'],
        'brand': ['BrandIdentityAgent', 'CreativeDirectorAgent'],

        # Research-related artifacts
        'research': ['ResearchAgent', 'TrendAnalysisAgent'],
        'analysis': ['ResearchAgent', 'CompetitorAnalysisAgent'],
        'market': ['CustomerResearchAgent', 'CompetitorAnalysisAgent'],

        # Creative artifacts
        'image': ['ImageAgent', 'ImageEditingAgent'],
        'video': ['VideoAgent', 'VideoEditingAgent'],
        'audio': ['AudioAgent'],
    }

    def execute_approved_artifacts(self, limit: int = 10) -> Dict[str, Any]:
        """
        Process all approved artifacts waiting for execution.

        Returns dict with processing results.
        """
        from core.models_conversation_artifacts import ExtractedArtifact

        # Find approved artifacts without successful executions
        approved = ExtractedArtifact.objects.filter(
            status='approved'
        ).exclude(
            executions__status='completed'
        ).order_by('-composite_score')[:limit]

        results = {
            'processed': 0,
            'succeeded': 0,
            'failed': 0,
            'skipped': 0,
            'executions': []
        }

        for artifact in approved:
            try:
                execution = self.execute_artifact(artifact)
                if execution.status == 'completed':
                    results['succeeded'] += 1
                else:
                    results['failed'] += 1
                results['executions'].append({
                    'artifact_id': str(artifact.id),
                    'execution_id': str(execution.id),
                    'status': execution.status,
                    'agent': execution.agent_name,
                })
            except Exception as e:
                logger.error(f"Failed to execute artifact {artifact.id}: {e}")
                results['failed'] += 1
                results['executions'].append({
                    'artifact_id': str(artifact.id),
                    'error': str(e),
                })

            results['processed'] += 1

        logger.info(
            f"Artifact execution batch: {results['succeeded']}/{results['processed']} succeeded"
        )
        return results

    def execute_artifact(self, artifact) -> 'ArtifactExecution':
        """
        Execute a single approved artifact.

        1. Select appropriate agent
        2. Create execution record
        3. Route via AgentRouter
        4. Update statuses based on result
        """
        from core.models_conversation_artifacts import ArtifactExecution

        # Validate artifact is approved
        if artifact.status != 'approved':
            raise ValueError(f"Artifact {artifact.id} is not approved (status: {artifact.status})")

        # Determine which agent should handle this
        agent_name = self._select_agent(artifact)
        task_description = self._build_task(artifact)

        # Create execution record
        execution = ArtifactExecution.objects.create(
            artifact=artifact,
            agent_name=agent_name,
            task_description=task_description,
            context={
                'artifact_id': str(artifact.id),
                'artifact_type': artifact.artifact_type,
                'source_conversation': str(artifact.conversation_id),
                'from_chief_of_staff': True,
            }
        )

        start_time = time.time()

        try:
            # Mark as running
            execution.status = 'running'
            execution.started_at = timezone.now()
            execution.save()

            # Route to agent
            result = self._route_to_agent(agent_name, artifact, execution)

            # Mark as completed
            execution.status = 'completed'
            execution.result = result
            execution.completed_at = timezone.now()
            execution.execution_time_ms = int((time.time() - start_time) * 1000)
            execution.save()

            # Update artifact status
            artifact.status = 'implemented'
            artifact.save()

            logger.info(
                f"Artifact {artifact.id} executed successfully via {agent_name} "
                f"in {execution.execution_time_ms}ms"
            )

        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.execution_time_ms = int((time.time() - start_time) * 1000)
            execution.save()

            logger.error(f"Artifact {artifact.id} execution failed: {e}")
            raise

        return execution

    def _select_agent(self, artifact) -> str:
        """
        Select the best agent for this artifact.

        Priority:
        1. Source agent (if the proposing agent can handle it)
        2. Keyword-based specialization matching
        3. Default by artifact type
        """
        # Option 1: Use source agent if available
        if artifact.source_agent:
            return artifact.source_agent.name

        # Option 2: Check for keyword matches in title/description
        text = f"{artifact.title} {artifact.description}".lower()
        for keyword, agents in self.AGENT_SPECIALIZATIONS.items():
            if keyword in text:
                return agents[0]  # Use first matching specialized agent

        # Option 3: Default by artifact type
        return self.DEFAULT_AGENTS.get(
            artifact.artifact_type,
            'PersonalAssistantAgent'
        )

    def _build_task(self, artifact) -> str:
        """Build a task description from the artifact."""
        # Format based on artifact type
        type_prefixes = {
            'proposal': 'Implement this proposal',
            'experiment': 'Design and set up this experiment',
            'action_item': 'Complete this action item',
            'risk': 'Develop mitigation strategy for this risk',
            'question': 'Provide analysis and recommendation for',
            'data_spec': 'Implement this technical specification',
            'insight': 'Create actionable recommendations from this insight',
        }

        prefix = type_prefixes.get(artifact.artifact_type, 'Execute')

        task = f"{prefix}: {artifact.title}\n\n"
        task += f"Description: {artifact.description}\n"

        # Add details if present
        if artifact.details:
            task += f"\nAdditional Details:\n"
            for key, value in artifact.details.items():
                task += f"- {key}: {value}\n"

        return task

    def _route_to_agent(self, agent_name: str, artifact, execution) -> Dict[str, Any]:
        """
        Route the task to the specified agent via AgentRouter.
        """
        from core.agent_router import AgentRouter

        router = AgentRouter()

        try:
            result = router.route(
                agent_name=agent_name,
                task=execution.task_description,
                context={
                    'artifact_id': str(artifact.id),
                    'artifact_type': artifact.artifact_type,
                    'details': artifact.details,
                    'from_chief_of_staff': True,
                    'conversation_id': str(artifact.conversation_id),
                }
            )

            # Extract execution time if available
            if hasattr(result, 'execution_time_ms'):
                execution.execution_time_ms = result.execution_time_ms

            return {
                'success': result.success,
                'message': result.message,
                'data': result.data if hasattr(result, 'data') else {},
                'agent_name': agent_name,
            }

        except Exception as e:
            logger.error(f"Agent routing failed for {agent_name}: {e}")
            raise

    def get_execution_stats(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get execution statistics for the specified time period."""
        from core.models_conversation_artifacts import ArtifactExecution
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(hours=hours_back)

        recent = ArtifactExecution.objects.filter(queued_at__gte=cutoff)

        stats = {
            'period_hours': hours_back,
            'total': recent.count(),
            'by_status': {
                'queued': recent.filter(status='queued').count(),
                'running': recent.filter(status='running').count(),
                'completed': recent.filter(status='completed').count(),
                'failed': recent.filter(status='failed').count(),
                'cancelled': recent.filter(status='cancelled').count(),
            },
            'success_rate': 0.0,
            'avg_execution_time_ms': 0,
        }

        completed = recent.filter(status='completed')
        if completed.exists():
            from django.db.models import Avg
            stats['avg_execution_time_ms'] = completed.aggregate(
                avg=Avg('execution_time_ms')
            )['avg'] or 0

        total_finished = stats['by_status']['completed'] + stats['by_status']['failed']
        if total_finished > 0:
            stats['success_rate'] = stats['by_status']['completed'] / total_finished

        return stats


# Singleton instance
execution_service = ArtifactExecutionService()
