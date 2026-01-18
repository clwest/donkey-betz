"""
Dream Execution Pipeline
=========================

Session 766: Connects approved dreams to the Orchestration Layer.

This service bridges the gap between dream generation and actual execution:
1. When a dream is approved (decision_outcome = 'approved')
2. Creates a PartnershipProject from the dream content
3. Generates a CustomWorkflow for execution
4. Triggers the Orchestration Engine

This is the first step in solving the "Data Flow Dead Ends" problem where
7,990 dreams were generated but 0 were ever executed.

Usage:
    from core.services.dream_execution_pipeline import dream_execution_pipeline

    # Execute an approved dream
    result = dream_execution_pipeline.execute_dream(dream)

    # Or process all approved dreams
    results = dream_execution_pipeline.process_approved_dreams()
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class DreamExecutionPipeline:
    """
    Pipeline that converts approved dreams into executed workflows.

    Solves Dead End #1: Dreams generate but never execute.
    """

    # Map dream types to project types
    DREAM_TO_PROJECT_TYPE = {
        'creative_idea': 'content_creation',
        'what_if': 'research',
        'mashup': 'content_creation',
        'prediction': 'research',
        'improvement': 'development',
        'observation': 'research',
        'wild_thought': 'content_creation',
    }

    # Map dream types to workflow templates
    DREAM_TO_WORKFLOW = {
        'creative_idea': [
            ('ResearchAgent', 'Research the idea'),
            ('ContentStrategyAgent', 'Develop content strategy'),
            ('ContentWriterAgent', 'Create content draft'),
        ],
        'what_if': [
            ('ResearchAgent', 'Research the scenario'),
            ('TrendAnalysisAgent', 'Analyze trends'),
            ('ContentWriterAgent', 'Write analysis report'),
        ],
        'mashup': [
            ('ResearchAgent', 'Research both components'),
            ('CreativeDirectorAgent', 'Develop mashup concept'),
            ('ContentWriterAgent', 'Create mashup content'),
        ],
        'prediction': [
            ('ResearchAgent', 'Gather supporting data'),
            ('TrendAnalysisAgent', 'Analyze patterns'),
            ('ContentWriterAgent', 'Write prediction report'),
        ],
        'improvement': [
            ('ResearchAgent', 'Research current state'),
            ('ContentStrategyAgent', 'Develop improvement plan'),
            ('CodeGeneratorAgent', 'Implement improvements'),
        ],
        'observation': [
            ('ResearchAgent', 'Deep dive research'),
            ('TrendAnalysisAgent', 'Pattern analysis'),
            ('ContentWriterAgent', 'Write observation report'),
        ],
        'wild_thought': [
            ('ResearchAgent', 'Explore feasibility'),
            ('CreativeDirectorAgent', 'Develop concept'),
            ('ContentWriterAgent', 'Create exploration document'),
        ],
    }

    def __init__(self):
        self._orchestration_engine = None

    @property
    def orchestration_engine(self):
        """Lazy-load orchestration engine."""
        if self._orchestration_engine is None:
            from core.services.orchestration_engine import orchestration_engine
            self._orchestration_engine = orchestration_engine
        return self._orchestration_engine

    def execute_dream(
        self,
        dream,
        user=None,
        async_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Execute an approved dream through the full pipeline.

        Args:
            dream: AgentDream instance (must have decision_outcome='approved')
            user: User triggering execution (defaults to dream.agent.user if available)
            async_mode: Run orchestration in background (default True)

        Returns:
            Dict with project, workflow, and execution details
        """
        from core.models_unified_system import AgentDream

        # Validate dream is approved
        if dream.decision_outcome != 'approved':
            raise ValueError(
                f"Dream must be approved to execute. Current status: {dream.decision_outcome}"
            )

        # Get user for ownership
        if user is None:
            # Try to get user from agent or use system user
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.first()
            except Exception as e:
                logger.error(f"Could not determine user for dream execution: {e}")
                raise ValueError("No user available for dream execution")

        logger.info(f"Executing approved dream: {dream.title} (ID: {dream.id})")

        try:
            with transaction.atomic():
                # Step 1: Create project from dream
                project = self._create_project_from_dream(dream, user)
                logger.info(f"Created project: {project.project_name} (ID: {project.id})")

                # Step 2: Create workflow from dream
                workflow = self._create_workflow_from_dream(dream, project, user)
                logger.info(f"Created workflow: {workflow.name} (ID: {workflow.id})")

                # Step 3: Link dream to project
                dream.project = project
                dream.save(update_fields=['project'])

                # Step 4: Execute workflow via orchestration
                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=user,
                    input_data={
                        'dream_id': str(dream.id),
                        'dream_title': dream.title,
                        'dream_content': dream.content,
                        'dream_type': dream.dream_type,
                        'project_id': str(project.id),
                    },
                    async_mode=async_mode
                )
                logger.info(f"Started orchestration execution: {execution.id}")

                return {
                    'success': True,
                    'dream_id': str(dream.id),
                    'project_id': str(project.id),
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                    'message': f"Dream '{dream.title}' is now being executed",
                }

        except Exception as e:
            logger.error(f"Failed to execute dream {dream.id}: {e}")
            return {
                'success': False,
                'dream_id': str(dream.id),
                'error': str(e),
            }

    def _create_project_from_dream(self, dream, user) -> 'PartnershipProject':
        """Create a PartnershipProject from dream content."""
        from core.models_partnership import PartnershipProject

        # Determine project type from dream type
        project_type = self.DREAM_TO_PROJECT_TYPE.get(dream.dream_type, 'other')

        # Create project
        project = PartnershipProject.objects.create(
            user=user,
            project_name=f"Dream: {dream.title[:100]}",
            project_type=project_type,
            description=f"""
Project created from approved dream.

## Dream Title
{dream.title}

## Dream Content
{dream.content}

## Dream Type
{dream.dream_type}

## Inspiration
{dream.inspiration_source or 'N/A'}

## Scores
- Creativity: {dream.creativity_score:.2f}
- Actionability: {dream.actionability_score:.2f}
- Relevance: {dream.relevance_score:.2f}
- Composite: {dream.composite_score:.2f}
            """.strip(),
            status='active',
            ai_contribution_percent=80,
            human_contribution_percent=20,
        )

        return project

    def _create_workflow_from_dream(self, dream, project, user) -> 'CustomWorkflow':
        """Create a CustomWorkflow based on dream type."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep

        # Get workflow template for this dream type
        workflow_template = self.DREAM_TO_WORKFLOW.get(
            dream.dream_type,
            self.DREAM_TO_WORKFLOW['creative_idea']  # Default template
        )

        # Create workflow
        base_slug = slugify(dream.title[:50])
        workflow = CustomWorkflow.objects.create(
            created_by=user,
            name=f"Execute: {dream.title[:100]}",
            slug=f"{base_slug}-{str(dream.id)[:8]}",
            description=f"Workflow generated from approved dream: {dream.title}",
            content_type='dream_execution',
            category='auto_generated',
            status='active',
            execution_mode='sequential',
            max_retries=2,
            timeout_seconds=3600,  # 1 hour
            require_approval_on_error=True,
            config={
                'source': 'dream_execution_pipeline',
                'dream_id': str(dream.id),
                'project_id': str(project.id),
            }
        )

        # Create workflow steps
        for order, (agent_name, step_description) in enumerate(workflow_template, start=1):
            CustomWorkflowStep.objects.create(
                workflow=workflow,
                order=order,
                name=f"Step {order}: {step_description}",
                description=f"""
{step_description}

Context from dream:
- Title: {dream.title}
- Content: {dream.content[:500]}...
- Type: {dream.dream_type}
                """.strip(),
                agent=agent_name,
                config={
                    'dream_context': {
                        'title': dream.title,
                        'content': dream.content,
                        'type': dream.dream_type,
                        'topics': dream.related_topics,
                    }
                },
                timeout_seconds=600,  # 10 minutes per step
                requires_approval=False,  # Auto-execute steps
            )

        return workflow

    def process_approved_dreams(
        self,
        limit: int = 10,
        user=None
    ) -> List[Dict[str, Any]]:
        """
        Process all approved dreams that haven't been executed yet.

        Args:
            limit: Maximum number of dreams to process
            user: User for project/workflow ownership

        Returns:
            List of execution results
        """
        from core.models_unified_system import AgentDream

        # Find approved dreams without projects (not yet executed)
        approved_dreams = AgentDream.objects.filter(
            decision_outcome='approved',
            project__isnull=True,  # Not yet linked to a project
        ).order_by('-composite_score')[:limit]

        results = []
        for dream in approved_dreams:
            result = self.execute_dream(dream, user=user)
            results.append(result)

            if result['success']:
                logger.info(f"Successfully executed dream: {dream.title}")
            else:
                logger.warning(f"Failed to execute dream: {dream.title} - {result.get('error')}")

        return results

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about dream execution pipeline."""
        from core.models_unified_system import AgentDream
        from core.models_orchestration import OrchestrationExecution
        from core.models_partnership import PartnershipProject

        total_dreams = AgentDream.objects.count()
        approved_dreams = AgentDream.objects.filter(decision_outcome='approved').count()
        dreams_with_projects = AgentDream.objects.filter(
            decision_outcome='approved',
            project__isnull=False
        ).count()

        # Get orchestration stats for dream executions
        dream_executions = OrchestrationExecution.objects.filter(
            workflow__category='auto_generated',
            workflow__config__source='dream_execution_pipeline'
        ).count()

        return {
            'total_dreams': total_dreams,
            'approved_dreams': approved_dreams,
            'dreams_with_projects': dreams_with_projects,
            'dreams_executed': dream_executions,
            'pending_execution': approved_dreams - dreams_with_projects,
            'execution_rate': (
                (dreams_with_projects / approved_dreams * 100)
                if approved_dreams > 0 else 0
            ),
        }


# Singleton instance
dream_execution_pipeline = DreamExecutionPipeline()


def get_dream_execution_pipeline() -> DreamExecutionPipeline:
    """Get the singleton dream execution pipeline instance."""
    return dream_execution_pipeline
