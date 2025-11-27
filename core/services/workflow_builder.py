"""
Workflow Builder Service
========================

Session 212: Service for creating, managing, and executing custom workflows.

This service provides:
- Create/update/delete custom workflows
- Execute custom workflows using WorkflowOrchestrationAgent
- Track workflow execution history
- Manage workflow scheduling
"""

import logging
from typing import Any, Dict, List, Optional
from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction

logger = logging.getLogger(__name__)


class WorkflowBuilderService:
    """
    Service for managing custom workflows.

    Session 212: Enables users to create their own workflow templates
    by combining available agents into custom pipelines.
    """

    # Available agents that can be used in custom workflows
    AVAILABLE_AGENTS = [
        {
            'id': 'web_search',
            'name': 'Web Search',
            'description': 'Research a topic on the web',
            'category': 'research',
            'icon': 'search',
            'config_schema': {
                'query_template': {'type': 'string', 'description': 'Custom search query template'}
            }
        },
        {
            'id': 'coleadership_agent',
            'name': 'Executive Team Review',
            'description': 'Get creative direction from AI executive team',
            'category': 'planning',
            'icon': 'users',
            'config_schema': {}
        },
        {
            'id': 'image_generation_agent',
            'name': 'Image Generation',
            'description': 'Generate images using AI',
            'category': 'creation',
            'icon': 'image',
            'config_schema': {
                'width': {'type': 'integer', 'description': 'Image width', 'default': 1024},
                'height': {'type': 'integer', 'description': 'Image height', 'default': 1024},
                'count': {'type': 'integer', 'description': 'Number of images', 'default': 4},
                'style': {'type': 'string', 'description': 'Style preset'}
            }
        },
        {
            'id': 'video_generation_agent',
            'name': 'Video Generation',
            'description': 'Generate videos from images',
            'category': 'creation',
            'icon': 'video',
            'config_schema': {
                'duration': {'type': 'integer', 'description': 'Video duration in seconds', 'default': 5}
            }
        },
        {
            'id': 'audio_generation_agent',
            'name': 'Audio Generation',
            'description': 'Generate audio/sound effects',
            'category': 'creation',
            'icon': 'volume-2',
            'config_schema': {}
        },
        {
            'id': 'image_selection',
            'name': 'Image Selection',
            'description': 'Select an image for further processing',
            'category': 'utility',
            'icon': 'check-square',
            'config_schema': {}
        },
        {
            'id': 'image_variation_agent',
            'name': 'Image Variations',
            'description': 'Create platform-specific variations of images',
            'category': 'creation',
            'icon': 'copy',
            'config_schema': {
                'platforms': {'type': 'array', 'description': 'Platforms to create variations for'}
            }
        },
        {
            'id': 'create_project_from_research',
            'name': 'Create Project',
            'description': 'Organize all content into a project',
            'category': 'organization',
            'icon': 'folder-plus',
            'config_schema': {}
        }
    ]

    def __init__(self, user=None):
        """Initialize the service."""
        self.user = user
        self._workflow_model = None
        self._step_model = None
        self._execution_model = None

    @property
    def WorkflowModel(self):
        """Lazy load CustomWorkflow model."""
        if self._workflow_model is None:
            from core.models_unified_system import CustomWorkflow
            self._workflow_model = CustomWorkflow
        return self._workflow_model

    @property
    def StepModel(self):
        """Lazy load CustomWorkflowStep model."""
        if self._step_model is None:
            from core.models_unified_system import CustomWorkflowStep
            self._step_model = CustomWorkflowStep
        return self._step_model

    @property
    def ExecutionModel(self):
        """Lazy load WorkflowExecution model."""
        if self._execution_model is None:
            from core.models_unified_system import WorkflowExecution
            self._execution_model = WorkflowExecution
        return self._execution_model

    # =========================================================================
    # WORKFLOW CRUD OPERATIONS
    # =========================================================================

    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents for workflow building."""
        return self.AVAILABLE_AGENTS

    def list_workflows(
        self,
        include_public: bool = True,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """
        List all workflows accessible to the user.

        Args:
            include_public: Include public workflows from other users
            status: Filter by status (draft, active, archived)

        Returns:
            List of workflow dictionaries
        """
        from django.db.models import Q

        query = Q(created_by=self.user)
        if include_public:
            query |= Q(is_public=True)

        workflows = self.WorkflowModel.objects.filter(query)

        if status:
            workflows = workflows.filter(status=status)

        return [self._workflow_to_dict(w) for w in workflows]

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get a single workflow by ID."""
        try:
            workflow = self.WorkflowModel.objects.get(id=workflow_id)

            # Check access
            if workflow.created_by != self.user and not workflow.is_public:
                return None

            return self._workflow_to_dict(workflow, include_steps=True)
        except self.WorkflowModel.DoesNotExist:
            return None

    @transaction.atomic
    def create_workflow(
        self,
        name: str,
        description: str = '',
        content_type: str = 'custom',
        category: str = 'custom',
        steps: List[Dict] = None,
        config: Dict = None,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new custom workflow.

        Args:
            name: Workflow name
            description: Workflow description
            content_type: Type of content produced
            category: Workflow category
            steps: List of step definitions
            config: Global workflow configuration
            is_public: Whether to share publicly

        Returns:
            Created workflow dictionary
        """
        # Generate unique slug
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while self.WorkflowModel.objects.filter(
            created_by=self.user, slug=slug
        ).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        workflow = self.WorkflowModel.objects.create(
            created_by=self.user,
            name=name,
            slug=slug,
            description=description,
            content_type=content_type,
            category=category,
            config=config or {},
            is_public=is_public,
            status='draft'
        )

        # Create steps if provided
        if steps:
            for i, step_def in enumerate(steps, 1):
                self.StepModel.objects.create(
                    workflow=workflow,
                    order=i,
                    name=step_def.get('name', f'Step {i}'),
                    description=step_def.get('description', ''),
                    agent=step_def['agent'],
                    config=step_def.get('config', {}),
                    condition=step_def.get('condition', {}),
                    is_required=step_def.get('is_required', True),
                    retry_count=step_def.get('retry_count', 0)
                )

        logger.info(f"Created custom workflow: {workflow.name} (id={workflow.id})")
        return self._workflow_to_dict(workflow, include_steps=True)

    @transaction.atomic
    def update_workflow(
        self,
        workflow_id: str,
        **updates
    ) -> Optional[Dict[str, Any]]:
        """Update an existing workflow."""
        try:
            workflow = self.WorkflowModel.objects.get(
                id=workflow_id,
                created_by=self.user
            )
        except self.WorkflowModel.DoesNotExist:
            return None

        # Update basic fields
        for field in ['name', 'description', 'content_type', 'category',
                      'config', 'is_public', 'status']:
            if field in updates:
                setattr(workflow, field, updates[field])

        # Update slug if name changed
        if 'name' in updates:
            workflow.slug = slugify(updates['name'])

        workflow.save()

        # Update steps if provided
        if 'steps' in updates:
            # Delete existing steps
            workflow.steps.all().delete()

            # Create new steps
            for i, step_def in enumerate(updates['steps'], 1):
                self.StepModel.objects.create(
                    workflow=workflow,
                    order=i,
                    name=step_def.get('name', f'Step {i}'),
                    description=step_def.get('description', ''),
                    agent=step_def['agent'],
                    config=step_def.get('config', {}),
                    condition=step_def.get('condition', {}),
                    is_required=step_def.get('is_required', True),
                    retry_count=step_def.get('retry_count', 0)
                )

        logger.info(f"Updated workflow: {workflow.name}")
        return self._workflow_to_dict(workflow, include_steps=True)

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        try:
            workflow = self.WorkflowModel.objects.get(
                id=workflow_id,
                created_by=self.user
            )
            workflow.delete()
            logger.info(f"Deleted workflow: {workflow_id}")
            return True
        except self.WorkflowModel.DoesNotExist:
            return False

    def duplicate_workflow(self, workflow_id: str, new_name: str = None) -> Optional[Dict[str, Any]]:
        """Create a copy of an existing workflow."""
        original = self.get_workflow(workflow_id)
        if not original:
            return None

        # Create new workflow with copied data
        return self.create_workflow(
            name=new_name or f"{original['name']} (Copy)",
            description=original['description'],
            content_type=original['content_type'],
            category=original['category'],
            steps=original.get('steps', []),
            config=original.get('config', {}),
            is_public=False  # Copies start private
        )

    # =========================================================================
    # WORKFLOW EXECUTION
    # =========================================================================

    def execute_workflow(
        self,
        workflow_id: str,
        topic: str,
        parameters: Dict = None,
        async_execution: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a custom workflow.

        Args:
            workflow_id: ID of workflow to execute
            topic: Topic/subject for the workflow
            parameters: Additional parameters
            async_execution: If True, return immediately with execution ID

        Returns:
            Execution result or status
        """
        workflow_data = self.get_workflow(workflow_id)
        if not workflow_data:
            return {'success': False, 'error': 'Workflow not found'}

        # Create execution record
        execution = self.ExecutionModel.objects.create(
            workflow_type='custom',
            workflow_name=workflow_data['name'],
            custom_workflow_id=workflow_id,
            executed_by=self.user,
            topic=topic,
            parameters=parameters or {}
        )

        try:
            # Get the workflow model for the orchestration agent
            workflow = self.WorkflowModel.objects.get(id=workflow_id)
            workflow_def = workflow.to_workflow_definition()

            # Execute using WorkflowOrchestrationAgent
            from agents.workflow_orchestration_agent import WorkflowOrchestrationAgent

            agent = WorkflowOrchestrationAgent(
                user=self.user,
                project_id=parameters.get('project_id') if parameters else None
            )

            # Execute the custom workflow
            result = agent.execute_custom_workflow(
                workflow_def=workflow_def,
                topic=topic,
                style=parameters.get('style') if parameters else None,
                count=parameters.get('count', 4) if parameters else 4
            )

            # Update execution record
            execution.status = 'completed' if result.get('success') else 'failed'
            execution.step_results = result.get('steps', [])
            execution.error_message = result.get('error', '')
            execution.completed_at = timezone.now()
            execution.duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()

            if result.get('project_id'):
                execution.project_id = result['project_id']
            if result.get('image_ids'):
                execution.image_ids = result['image_ids']

            execution.save()

            # Update workflow use count
            workflow.use_count += 1
            workflow.save()

            return {
                'success': result.get('success', False),
                'execution_id': str(execution.id),
                'workflow_name': workflow_data['name'],
                **result
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()
            execution.save()

            return {
                'success': False,
                'execution_id': str(execution.id),
                'error': str(e)
            }

    def get_execution_history(
        self,
        workflow_id: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get workflow execution history."""
        executions = self.ExecutionModel.objects.filter(
            executed_by=self.user
        )

        if workflow_id:
            executions = executions.filter(custom_workflow_id=workflow_id)

        executions = executions.order_by('-started_at')[:limit]

        return [self._execution_to_dict(e) for e in executions]

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get a single execution by ID."""
        try:
            execution = self.ExecutionModel.objects.get(
                id=execution_id,
                executed_by=self.user
            )
            return self._execution_to_dict(execution, include_steps=True)
        except self.ExecutionModel.DoesNotExist:
            return None

    # =========================================================================
    # BUILT-IN WORKFLOW HELPERS
    # =========================================================================

    def list_builtin_workflows(self) -> List[Dict[str, Any]]:
        """Get list of built-in workflows from WorkflowOrchestrationAgent."""
        from agents.workflow_orchestration_agent import WorkflowOrchestrationAgent

        workflows = []
        for name, data in WorkflowOrchestrationAgent.WORKFLOWS.items():
            workflows.append({
                'id': name,
                'name': name.replace('_', ' ').title(),
                'description': data['description'],
                'content_type': data['content_type'],
                'step_count': len(data['steps']),
                'is_builtin': True
            })

        return workflows

    def execute_builtin_workflow(
        self,
        workflow_name: str,
        topic: str,
        style: str = None,
        count: int = 4,
        project_id: str = None
    ) -> Dict[str, Any]:
        """Execute a built-in workflow."""
        # Create execution record
        execution = self.ExecutionModel.objects.create(
            workflow_type='builtin',
            workflow_name=workflow_name,
            executed_by=self.user,
            topic=topic,
            parameters={'style': style, 'count': count, 'project_id': project_id}
        )

        try:
            from agents.workflow_orchestration_agent import WorkflowOrchestrationAgent

            agent = WorkflowOrchestrationAgent(
                user=self.user,
                project_id=project_id
            )

            result = agent.execute(
                workflow=workflow_name,
                topic=topic,
                style=style,
                count=count
            )

            # Update execution record
            execution.status = 'completed' if result.success else 'failed'
            execution.step_results = [
                {'step': s.step_number, 'name': s.step_name, 'success': s.success}
                for s in result.step_results
            ]
            execution.error_message = result.error or ''
            execution.completed_at = timezone.now()
            execution.duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()

            if hasattr(result, 'project_id') and result.project_id:
                execution.project_id = result.project_id

            execution.save()

            return {
                'success': result.success,
                'execution_id': str(execution.id),
                'summary': result.summary,
                'steps': execution.step_results,
                'project_id': str(execution.project_id) if execution.project_id else None
            }

        except Exception as e:
            logger.error(f"Built-in workflow execution failed: {e}")
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()

            return {
                'success': False,
                'execution_id': str(execution.id),
                'error': str(e)
            }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _workflow_to_dict(
        self,
        workflow,
        include_steps: bool = False
    ) -> Dict[str, Any]:
        """Convert workflow model to dictionary."""
        data = {
            'id': str(workflow.id),
            'name': workflow.name,
            'slug': workflow.slug,
            'description': workflow.description,
            'content_type': workflow.content_type,
            'category': workflow.category,
            'is_public': workflow.is_public,
            'is_featured': workflow.is_featured,
            'use_count': workflow.use_count,
            'status': workflow.status,
            'config': workflow.config,
            'created_by': workflow.created_by.username,
            'is_owner': workflow.created_by == self.user,
            'is_scheduled': workflow.is_scheduled,
            'schedule_cron': workflow.schedule_cron,
            'created_at': workflow.created_at.isoformat(),
            'updated_at': workflow.updated_at.isoformat(),
        }

        if include_steps:
            data['steps'] = [
                {
                    'id': str(step.id),
                    'order': step.order,
                    'name': step.name,
                    'description': step.description,
                    'agent': step.agent,
                    'config': step.config,
                    'condition': step.condition,
                    'is_required': step.is_required,
                    'retry_count': step.retry_count
                }
                for step in workflow.steps.all().order_by('order')
            ]
            data['step_count'] = len(data['steps'])
        else:
            data['step_count'] = workflow.steps.count()

        return data

    def _execution_to_dict(
        self,
        execution,
        include_steps: bool = False
    ) -> Dict[str, Any]:
        """Convert execution model to dictionary."""
        data = {
            'id': str(execution.id),
            'workflow_type': execution.workflow_type,
            'workflow_name': execution.workflow_name,
            'topic': execution.topic,
            'status': execution.status,
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'duration_seconds': execution.duration_seconds,
            'project_id': str(execution.project_id) if execution.project_id else None,
            'image_count': len(execution.image_ids) if execution.image_ids else 0,
            'video_count': len(execution.video_ids) if execution.video_ids else 0,
        }

        if include_steps:
            data['step_results'] = execution.step_results
            data['error_message'] = execution.error_message
            data['parameters'] = execution.parameters
            data['image_ids'] = execution.image_ids
            data['video_ids'] = execution.video_ids

        return data


# Singleton instance
_workflow_builder_instance = None

def get_workflow_builder(user) -> WorkflowBuilderService:
    """Get a WorkflowBuilderService instance for a user."""
    return WorkflowBuilderService(user=user)
