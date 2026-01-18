"""
HiveMind Execution Pipeline
============================

Session 766: Connects HiveMind session syntheses to the Orchestration Layer.

This service bridges the gap between HiveMind collective intelligence and execution:
1. When a HiveMind session completes with synthesis
2. Extracts actionable recommendations from the synthesis
3. Creates a PartnershipProject from the session
4. Generates a CustomWorkflow for execution
5. Triggers the Orchestration Engine

Solves Dead End #4: 321 HiveMind sessions with 182 syntheses, 0 acted upon.

Usage:
    from core.services.hivemind_execution_pipeline import hivemind_execution_pipeline

    # Execute a completed HiveMind session
    result = hivemind_execution_pipeline.execute_session(session)

    # Or process all unexecuted sessions
    results = hivemind_execution_pipeline.process_completed_sessions()
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class HiveMindExecutionPipeline:
    """
    Pipeline that converts HiveMind syntheses into executed workflows.

    Solves Dead End #4: HiveMind sessions generate but never execute.
    """

    # Map session modes to workflow templates
    SESSION_MODE_WORKFLOWS = {
        'hive_mind': [
            ('ResearchAgent', 'Deep research on the collective insights'),
            ('ContentStrategyAgent', 'Develop action plan from synthesis'),
            ('ContentWriterAgent', 'Create implementation document'),
        ],
        'conversation': [
            ('ResearchAgent', 'Research conversation conclusions'),
            ('ContentWriterAgent', 'Summarize conversation outcomes'),
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

    def execute_session(
        self,
        session,
        user=None,
        async_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a completed HiveMind session through the full pipeline.

        Args:
            session: HiveMindSession instance (must have synthesis)
            user: User triggering execution (defaults to system user)
            async_mode: Run orchestration in background (default True)

        Returns:
            Dict with project, workflow, and execution details
        """
        # Validate session has synthesis
        if not session.synthesis:
            raise ValueError(
                f"Session must have synthesis to execute. Session ID: {session.id}"
            )

        # Validate session is completed
        if session.status != 'completed':
            raise ValueError(
                f"Session must be completed to execute. Current status: {session.status}"
            )

        # Get user for ownership
        if user is None:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.first()
            except Exception as e:
                logger.error(f"Could not determine user for session execution: {e}")
                raise ValueError("No user available for session execution")

        logger.info(f"Executing HiveMind session: {session.id}")

        try:
            with transaction.atomic():
                # Step 1: Create project from session
                project = self._create_project_from_session(session, user)
                logger.info(f"Created project: {project.project_name} (ID: {project.id})")

                # Step 2: Create workflow from session
                workflow = self._create_workflow_from_session(session, project, user)
                logger.info(f"Created workflow: {workflow.name} (ID: {workflow.id})")

                # Step 3: Link session to project
                session.project = project
                session.save(update_fields=['project'])

                # Step 4: Execute workflow via orchestration
                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=user,
                    input_data={
                        'session_id': str(session.id),
                        'question': session.question,
                        'synthesis': session.synthesis,
                        'synthesis_summary': session.synthesis_summary,
                        'session_mode': session.session_mode,
                        'contribution_count': session.contribution_count,
                        'project_id': str(project.id),
                    },
                    async_mode=async_mode
                )
                logger.info(f"Started orchestration execution: {execution.id}")

                return {
                    'success': True,
                    'session_id': str(session.id),
                    'project_id': str(project.id),
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                    'message': f"HiveMind session is now being executed",
                }

        except Exception as e:
            logger.error(f"Failed to execute HiveMind session {session.id}: {e}")
            return {
                'success': False,
                'session_id': str(session.id),
                'error': str(e),
            }

    def _create_project_from_session(self, session, user) -> 'PartnershipProject':
        """Create a PartnershipProject from HiveMind session."""
        from core.models_partnership import PartnershipProject

        # Determine project type based on session mode
        project_type = 'research' if session.session_mode == 'hive_mind' else 'content_creation'

        # Create descriptive project name
        question_preview = session.question[:80] if session.question else 'HiveMind Session'

        project = PartnershipProject.objects.create(
            user=user,
            project_name=f"HiveMind: {question_preview}",
            project_type=project_type,
            description=f"""
Project created from HiveMind collective intelligence session.

## Question/Topic
{session.question}

## Context
{session.context or 'N/A'}

## Collective Synthesis
{session.synthesis}

## Session Summary
{session.synthesis_summary or 'N/A'}

## Session Stats
- Mode: {session.session_mode}
- Participants: {len(session.participant_ids)}
- Contributions: {session.contribution_count}
- Thinking Time: {session.total_thinking_time:.1f}s
            """.strip(),
            status='active',
            ai_contribution_percent=90,  # HiveMind is heavily AI-driven
            human_contribution_percent=10,
        )

        return project

    def _create_workflow_from_session(self, session, project, user) -> 'CustomWorkflow':
        """Create a CustomWorkflow based on session mode."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep

        # Get workflow template for this session mode
        workflow_template = self.SESSION_MODE_WORKFLOWS.get(
            session.session_mode,
            self.SESSION_MODE_WORKFLOWS['hive_mind']  # Default template
        )

        # Create workflow
        question_slug = slugify(session.question[:30]) if session.question else 'hivemind'
        workflow = CustomWorkflow.objects.create(
            created_by=user,
            name=f"HiveMind Execution: {session.question[:80]}",
            slug=f"hivemind-{question_slug}-{str(session.id)[:8]}",
            description=f"Workflow generated from HiveMind session synthesis",
            content_type='hivemind_execution',
            category='auto_generated',
            status='active',
            execution_mode='sequential',
            max_retries=2,
            timeout_seconds=3600,  # 1 hour
            require_approval_on_error=True,
            config={
                'source': 'hivemind_execution_pipeline',
                'session_id': str(session.id),
                'project_id': str(project.id),
                'session_mode': session.session_mode,
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

Context from HiveMind Session:
- Question: {session.question[:300]}...
- Synthesis: {session.synthesis[:500]}...
- Mode: {session.session_mode}
                """.strip(),
                agent=agent_name,
                config={
                    'hivemind_context': {
                        'question': session.question,
                        'synthesis': session.synthesis,
                        'summary': session.synthesis_summary,
                        'mode': session.session_mode,
                        'contribution_count': session.contribution_count,
                    }
                },
                timeout_seconds=600,  # 10 minutes per step
                requires_approval=False,
            )

        return workflow

    def process_completed_sessions(
        self,
        limit: int = 5,
        user=None
    ) -> List[Dict[str, Any]]:
        """
        Process completed HiveMind sessions that haven't been executed yet.

        Args:
            limit: Maximum number of sessions to process
            user: User for project/workflow ownership

        Returns:
            List of execution results
        """
        from core.models_unified_system import HiveMindSession

        # Find completed sessions with synthesis that haven't been linked to projects
        completed_sessions = HiveMindSession.objects.filter(
            status='completed',
            project__isnull=True,  # Not yet linked to a project
        ).exclude(
            synthesis=''  # Must have synthesis
        ).order_by('-contribution_count', '-created_at')[:limit]

        results = []
        for session in completed_sessions:
            result = self.execute_session(session, user=user)
            results.append(result)

            if result['success']:
                logger.info(f"Successfully executed HiveMind session: {session.id}")
            else:
                logger.warning(
                    f"Failed to execute HiveMind session: {session.id} - {result.get('error')}"
                )

        return results

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about HiveMind execution pipeline."""
        from core.models_unified_system import HiveMindSession
        from core.models_orchestration import OrchestrationExecution
        from core.models_partnership import PartnershipProject

        total_sessions = HiveMindSession.objects.count()
        completed_sessions = HiveMindSession.objects.filter(status='completed').count()
        sessions_with_synthesis = HiveMindSession.objects.exclude(synthesis='').count()
        sessions_with_projects = HiveMindSession.objects.filter(
            status='completed',
            project__isnull=False
        ).count()

        # Get orchestration stats for HiveMind executions
        hivemind_executions = OrchestrationExecution.objects.filter(
            workflow__category='auto_generated',
            workflow__config__source='hivemind_execution_pipeline'
        ).count()

        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'sessions_with_synthesis': sessions_with_synthesis,
            'sessions_with_projects': sessions_with_projects,
            'sessions_executed': hivemind_executions,
            'pending_execution': sessions_with_synthesis - sessions_with_projects,
            'execution_rate': (
                (sessions_with_projects / sessions_with_synthesis * 100)
                if sessions_with_synthesis > 0 else 0
            ),
        }


# Singleton instance
hivemind_execution_pipeline = HiveMindExecutionPipeline()


def get_hivemind_execution_pipeline() -> HiveMindExecutionPipeline:
    """Get the singleton HiveMind execution pipeline instance."""
    return hivemind_execution_pipeline
