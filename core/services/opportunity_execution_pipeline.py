"""
Opportunity Execution Pipeline
==============================

Session 766: Connects high-scoring opportunities to the Orchestration Layer.

This service bridges the gap between opportunity discovery and execution:
1. Finds high-scoring opportunities that haven't been acted upon
2. Creates a PartnershipProject from the opportunity
3. Generates a CustomWorkflow based on opportunity type
4. Triggers the Orchestration Engine

Solves Dead End #7: 6,709 opportunities discovered, 0% actioned.

Usage:
    from core.services.opportunity_execution_pipeline import opportunity_execution_pipeline

    # Execute a high-scoring opportunity
    result = opportunity_execution_pipeline.execute_opportunity(opportunity)

    # Or process all high-scoring unexecuted opportunities
    results = opportunity_execution_pipeline.process_high_scoring_opportunities()
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class OpportunityExecutionPipeline:
    """
    Pipeline that converts high-scoring opportunities into executed workflows.

    Solves Dead End #7: Opportunities are discovered and scored but never acted upon.
    """

    # Minimum score threshold for auto-execution
    MIN_SCORE_THRESHOLD = 70  # Only execute opportunities scoring >= 70

    # Map opportunity types to workflow templates
    OPPORTUNITY_TYPE_WORKFLOWS = {
        'job': [
            ('ResearchAgent', 'Research the job requirements and company'),
            ('ContentWriterAgent', 'Prepare application materials'),
            ('ContentStrategyAgent', 'Develop application strategy'),
        ],
        'gig': [
            ('ResearchAgent', 'Research the gig requirements'),
            ('ContentWriterAgent', 'Prepare proposal'),
        ],
        'freelance': [
            ('ResearchAgent', 'Research client and project scope'),
            ('ContentWriterAgent', 'Create proposal and portfolio materials'),
            ('ContentStrategyAgent', 'Plan delivery approach'),
        ],
        'content': [
            ('ResearchAgent', 'Research content topic and audience'),
            ('ContentStrategyAgent', 'Develop content strategy'),
            ('ContentWriterAgent', 'Create content'),
        ],
        'investment': [
            ('ResearchAgent', 'Deep research on investment opportunity'),
            ('MarketIntelligenceAgent', 'Analyze market conditions'),
        ],
        'trend': [
            ('TrendAnalysisAgent', 'Analyze the trend deeply'),
            ('ContentStrategyAgent', 'Develop trend capitalization strategy'),
            ('ContentWriterAgent', 'Create trend-based content'),
        ],
        'product': [
            ('ResearchAgent', 'Research product demand and competition'),
            ('ContentStrategyAgent', 'Develop product launch strategy'),
        ],
        'default': [
            ('ResearchAgent', 'Research the opportunity'),
            ('ContentStrategyAgent', 'Develop action plan'),
            ('ContentWriterAgent', 'Create deliverables'),
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

    def execute_opportunity(
        self,
        opportunity,
        user=None,
        async_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a high-scoring opportunity through the full pipeline.

        Args:
            opportunity: Opportunity instance (must have high match_score)
            user: User triggering execution (defaults to opportunity owner)
            async_mode: Run orchestration in background (default True)

        Returns:
            Dict with project, workflow, and execution details
        """
        # Validate opportunity score
        score = opportunity.match_score or opportunity.overall_score or 0
        if score < self.MIN_SCORE_THRESHOLD:
            return {
                'success': False,
                'opportunity_id': str(opportunity.id),
                'error': f"Score {score} below threshold {self.MIN_SCORE_THRESHOLD}",
            }

        # Validate opportunity status (scored = ready to act on)
        if opportunity.status not in ('active', 'pending', 'scored'):
            return {
                'success': False,
                'opportunity_id': str(opportunity.id),
                'error': f"Opportunity status '{opportunity.status}' not eligible for execution",
            }

        # Get user for ownership
        if user is None:
            user = opportunity.user
        if not user:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.first()
            except Exception as e:
                logger.error(f"Could not determine user for opportunity execution: {e}")
                return {
                    'success': False,
                    'opportunity_id': str(opportunity.id),
                    'error': "No user available for opportunity execution",
                }

        logger.info(f"Executing opportunity: {opportunity.id} - {opportunity.title[:50]}")

        try:
            with transaction.atomic():
                # Step 1: Create project from opportunity
                project = self._create_project_from_opportunity(opportunity, user)
                logger.info(f"Created project: {project.project_name} (ID: {project.id})")

                # Step 2: Create workflow from opportunity
                workflow = self._create_workflow_from_opportunity(opportunity, project, user)
                logger.info(f"Created workflow: {workflow.name} (ID: {workflow.id})")

                # Step 3: Link opportunity to project and update status
                opportunity.project = project
                opportunity.status = 'applied'  # Mark as being worked on
                opportunity.acted_on_at = timezone.now()
                opportunity.save(update_fields=['project', 'status', 'acted_on_at'])

                # Step 4: Create OpportunityAction record
                self._create_action_record(opportunity, user, project, workflow)

                # Step 5: Execute workflow via orchestration
                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=user,
                    input_data={
                        'opportunity_id': str(opportunity.id),
                        'title': opportunity.title,
                        'description': opportunity.description,
                        'opportunity_type': opportunity.opportunity_type,
                        'source': opportunity.source,
                        'potential_revenue': str(opportunity.potential_revenue),
                        'match_score': opportunity.match_score,
                        'overall_score': opportunity.overall_score,
                        'requirements': opportunity.requirements,
                        'keywords': opportunity.keywords,
                        'project_id': str(project.id),
                    },
                    async_mode=async_mode
                )
                logger.info(f"Started orchestration execution: {execution.id}")

                return {
                    'success': True,
                    'opportunity_id': str(opportunity.id),
                    'project_id': str(project.id),
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                    'message': f"Opportunity '{opportunity.title[:50]}' is now being executed",
                }

        except Exception as e:
            logger.error(f"Failed to execute opportunity {opportunity.id}: {e}")
            return {
                'success': False,
                'opportunity_id': str(opportunity.id),
                'error': str(e),
            }

    def _create_project_from_opportunity(self, opportunity, user) -> 'PartnershipProject':
        """Create a PartnershipProject from opportunity."""
        from core.models_partnership import PartnershipProject

        # Determine project type based on opportunity type
        opp_type = opportunity.opportunity_type or 'default'
        project_type_map = {
            'job': 'job_application',
            'gig': 'freelance',
            'freelance': 'freelance',
            'content': 'content_creation',
            'investment': 'research',
            'trend': 'content_creation',
            'product': 'product_development',
        }
        project_type = project_type_map.get(opp_type, 'consulting')

        # Create descriptive project name
        title_preview = opportunity.title[:80] if opportunity.title else 'Opportunity'

        project = PartnershipProject.objects.create(
            user=user,
            project_name=f"Opportunity: {title_preview}",
            project_type=project_type,
            description=f"""
Project created from high-scoring opportunity.

## Opportunity Details
- **Title:** {opportunity.title}
- **Type:** {opportunity.opportunity_type}
- **Source:** {opportunity.source}
- **Potential Revenue:** ${opportunity.potential_revenue}
- **Match Score:** {opportunity.match_score}/100
- **Overall Score:** {opportunity.overall_score}/100

## Description
{opportunity.description}

## Requirements
{', '.join(opportunity.requirements) if opportunity.requirements else 'N/A'}

## Keywords
{', '.join(opportunity.keywords) if opportunity.keywords else 'N/A'}

## Scores
- Profit Potential: {opportunity.profit_potential}/100
- Competition Level: {opportunity.competition_level}/100
- Effort Required: {opportunity.effort_required}/100
- Time Sensitivity: {opportunity.time_sensitivity}/100
            """.strip(),
            status='active',
            ai_contribution_percent=80,  # AI-driven opportunity execution
            human_contribution_percent=20,
        )

        return project

    def _create_workflow_from_opportunity(self, opportunity, project, user) -> 'CustomWorkflow':
        """Create a CustomWorkflow based on opportunity type."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep

        # Get workflow template for this opportunity type
        opp_type = opportunity.opportunity_type or 'default'
        workflow_template = self.OPPORTUNITY_TYPE_WORKFLOWS.get(
            opp_type,
            self.OPPORTUNITY_TYPE_WORKFLOWS['default']
        )

        # Create workflow
        title_slug = slugify(opportunity.title[:30]) if opportunity.title else 'opportunity'
        workflow = CustomWorkflow.objects.create(
            created_by=user,
            name=f"Opportunity Execution: {opportunity.title[:80]}",
            slug=f"opportunity-{title_slug}-{str(opportunity.id)[:8]}",
            description=f"Workflow generated to capitalize on opportunity",
            content_type='opportunity_execution',
            category='auto_generated',
            status='active',
            execution_mode='sequential',
            max_retries=2,
            timeout_seconds=3600,  # 1 hour
            require_approval_on_error=True,
            config={
                'source': 'opportunity_execution_pipeline',
                'opportunity_id': str(opportunity.id),
                'project_id': str(project.id),
                'opportunity_type': opportunity.opportunity_type,
                'potential_revenue': str(opportunity.potential_revenue),
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

Context from Opportunity:
- Title: {opportunity.title[:300]}
- Type: {opportunity.opportunity_type}
- Source: {opportunity.source}
- Revenue: ${opportunity.potential_revenue}
- Score: {opportunity.match_score}
                """.strip(),
                agent=agent_name,
                config={
                    'opportunity_context': {
                        'title': opportunity.title,
                        'description': opportunity.description[:500] if opportunity.description else '',
                        'type': opportunity.opportunity_type,
                        'source': opportunity.source,
                        'potential_revenue': str(opportunity.potential_revenue),
                        'requirements': opportunity.requirements,
                        'keywords': opportunity.keywords,
                    }
                },
                timeout_seconds=600,  # 10 minutes per step
                requires_approval=False,
            )

        return workflow

    def _create_action_record(self, opportunity, user, project, workflow):
        """Create an OpportunityAction record to track this execution."""
        from core.models_unified_system import OpportunityAction

        OpportunityAction.objects.create(
            opportunity=opportunity,
            user=user,
            action_type='started',
            workflow_used=workflow.slug,
            notes=f"Automatically executed via Opportunity Execution Pipeline. Project: {project.id}",
        )

    def process_high_scoring_opportunities(
        self,
        limit: int = 5,
        min_score: int = None,
        user=None
    ) -> List[Dict[str, Any]]:
        """
        Process high-scoring opportunities that haven't been executed yet.

        Args:
            limit: Maximum number of opportunities to process
            min_score: Minimum score threshold (defaults to MIN_SCORE_THRESHOLD)
            user: User for project/workflow ownership

        Returns:
            List of execution results
        """
        from core.models_unified_system import Opportunity

        if min_score is None:
            min_score = self.MIN_SCORE_THRESHOLD

        # Find high-scoring opportunities that haven't been linked to projects
        from django.db import models as db_models
        high_scoring = Opportunity.objects.filter(
            project__isnull=True,  # Not yet linked to a project
            status__in=['active', 'pending', 'scored'],  # Still actionable (scored = ready to act)
        ).filter(
            # Either match_score or overall_score >= threshold
            db_models.Q(match_score__gte=min_score) | db_models.Q(overall_score__gte=min_score)
        ).order_by('-match_score', '-overall_score', '-potential_revenue')[:limit]

        results = []
        for opportunity in high_scoring:
            result = self.execute_opportunity(opportunity, user=user)
            results.append(result)

            if result['success']:
                logger.info(f"Successfully executed opportunity: {opportunity.id}")
            else:
                logger.warning(
                    f"Failed to execute opportunity: {opportunity.id} - {result.get('error')}"
                )

        return results

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about opportunity execution pipeline."""
        from core.models_unified_system import Opportunity, OpportunityAction
        from core.models_orchestration import OrchestrationExecution
        from django.db import models as db_models

        total = Opportunity.objects.count()
        high_scoring = Opportunity.objects.filter(
            db_models.Q(match_score__gte=self.MIN_SCORE_THRESHOLD) |
            db_models.Q(overall_score__gte=self.MIN_SCORE_THRESHOLD)
        ).count()
        with_projects = Opportunity.objects.filter(project__isnull=False).count()
        actions_total = OpportunityAction.objects.count()
        active = Opportunity.objects.filter(status='active').count()

        # Get orchestration stats for opportunity executions
        opportunity_executions = OrchestrationExecution.objects.filter(
            workflow__category='auto_generated',
            workflow__config__source='opportunity_execution_pipeline'
        ).count()

        return {
            'total_opportunities': total,
            'high_scoring_count': high_scoring,
            'opportunities_with_projects': with_projects,
            'opportunities_executed': opportunity_executions,
            'total_actions': actions_total,
            'active_opportunities': active,
            'pending_execution': high_scoring - with_projects,
            'execution_rate': (
                (with_projects / high_scoring * 100) if high_scoring > 0 else 0
            ),
        }


# Singleton instance
opportunity_execution_pipeline = OpportunityExecutionPipeline()


def get_opportunity_execution_pipeline() -> OpportunityExecutionPipeline:
    """Get the singleton opportunity execution pipeline instance."""
    return opportunity_execution_pipeline
