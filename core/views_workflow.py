"""
Workflow API Views
==================

Session 213: REST API endpoints for custom workflow management.

Endpoints:
- GET  /api/workflows/                     - List all workflows (built-in + custom)
- POST /api/workflows/                     - Create custom workflow
- GET  /api/workflows/{id}/                - Get workflow details
- PUT  /api/workflows/{id}/                - Update workflow
- DELETE /api/workflows/{id}/              - Delete workflow
- POST /api/workflows/{id}/execute/        - Execute workflow
- POST /api/workflows/{id}/duplicate/      - Duplicate workflow
- GET  /api/workflows/builtin/             - List built-in workflows only
- GET  /api/workflows/agents/              - List available agents for building
- GET  /api/workflows/executions/          - Get execution history
- GET  /api/workflows/executions/{id}/     - Get execution details
- POST /api/workflows/{id}/schedule/       - Schedule workflow
- DELETE /api/workflows/{id}/schedule/     - Remove schedule
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from core.services.workflow_builder import get_workflow_builder

logger = logging.getLogger(__name__)


# =============================================================================
# WORKFLOW CRUD ENDPOINTS
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def workflows_list_create(request):
    """
    GET: List all workflows (built-in + user's custom + public)
    POST: Create a new custom workflow
    """
    builder = get_workflow_builder(request.user)

    if request.method == 'GET':
        # Query parameters
        include_builtin = request.query_params.get('include_builtin', 'true').lower() == 'true'
        include_public = request.query_params.get('include_public', 'true').lower() == 'true'
        workflow_status = request.query_params.get('status')

        workflows = []

        # Add built-in workflows
        if include_builtin:
            builtin = builder.list_builtin_workflows()
            workflows.extend(builtin)

        # Add custom workflows
        custom = builder.list_workflows(
            include_public=include_public,
            status=workflow_status
        )
        workflows.extend(custom)

        return Response({
            'success': True,
            'count': len(workflows),
            'workflows': workflows
        })

    elif request.method == 'POST':
        # Create new custom workflow
        data = request.data

        if not data.get('name'):
            return Response({
                'success': False,
                'error': 'Workflow name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not data.get('steps') or len(data['steps']) == 0:
            return Response({
                'success': False,
                'error': 'At least one step is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            workflow = builder.create_workflow(
                name=data['name'],
                description=data.get('description', ''),
                content_type=data.get('content_type', 'custom'),
                category=data.get('category', 'custom'),
                steps=data['steps'],
                config=data.get('config', {}),
                is_public=data.get('is_public', False)
            )

            return Response({
                'success': True,
                'workflow': workflow
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def workflow_detail(request, workflow_id):
    """
    GET: Get workflow details
    PUT: Update workflow
    DELETE: Delete workflow
    """
    builder = get_workflow_builder(request.user)

    if request.method == 'GET':
        workflow = builder.get_workflow(workflow_id)
        if not workflow:
            return Response({
                'success': False,
                'error': 'Workflow not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'workflow': workflow
        })

    elif request.method == 'PUT':
        workflow = builder.update_workflow(workflow_id, **request.data)
        if not workflow:
            return Response({
                'success': False,
                'error': 'Workflow not found or not owned by you'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'workflow': workflow
        })

    elif request.method == 'DELETE':
        success = builder.delete_workflow(workflow_id)
        if not success:
            return Response({
                'success': False,
                'error': 'Workflow not found or not owned by you'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'message': 'Workflow deleted'
        })


# =============================================================================
# WORKFLOW EXECUTION ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_execute(request, workflow_id):
    """Execute a custom or built-in workflow."""
    builder = get_workflow_builder(request.user)
    data = request.data

    topic = data.get('topic')
    if not topic:
        return Response({
            'success': False,
            'error': 'Topic is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    parameters = {
        'style': data.get('style'),
        'count': data.get('count', 4),
        'project_id': data.get('project_id')
    }

    try:
        # Check if it's a built-in workflow
        builtin_workflows = [w['id'] for w in builder.list_builtin_workflows()]

        if workflow_id in builtin_workflows:
            # Execute built-in workflow
            result = builder.execute_builtin_workflow(
                workflow_name=workflow_id,
                topic=topic,
                style=parameters.get('style'),
                count=parameters.get('count', 4),
                project_id=parameters.get('project_id')
            )
        else:
            # Execute custom workflow
            result = builder.execute_workflow(
                workflow_id=workflow_id,
                topic=topic,
                parameters=parameters
            )

        return Response(result)

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_duplicate(request, workflow_id):
    """Duplicate an existing workflow."""
    builder = get_workflow_builder(request.user)
    new_name = request.data.get('name')

    workflow = builder.duplicate_workflow(workflow_id, new_name)
    if not workflow:
        return Response({
            'success': False,
            'error': 'Workflow not found or not accessible'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'workflow': workflow
    }, status=status.HTTP_201_CREATED)


# =============================================================================
# BUILT-IN WORKFLOWS & AGENTS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def builtin_workflows(request):
    """List all built-in workflow templates."""
    builder = get_workflow_builder(request.user)
    workflows = builder.list_builtin_workflows()

    return Response({
        'success': True,
        'count': len(workflows),
        'workflows': workflows
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_agents(request):
    """List all available agents for building custom workflows."""
    builder = get_workflow_builder(request.user)
    agents = builder.get_available_agents()

    return Response({
        'success': True,
        'count': len(agents),
        'agents': agents
    })


# =============================================================================
# EXECUTION HISTORY
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def execution_list(request):
    """Get workflow execution history."""
    builder = get_workflow_builder(request.user)

    workflow_id = request.query_params.get('workflow_id')
    limit = int(request.query_params.get('limit', 20))

    executions = builder.get_execution_history(
        workflow_id=workflow_id,
        limit=limit
    )

    return Response({
        'success': True,
        'count': len(executions),
        'executions': executions
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def execution_detail(request, execution_id):
    """Get details of a specific execution."""
    builder = get_workflow_builder(request.user)

    execution = builder.get_execution(execution_id)
    if not execution:
        return Response({
            'success': False,
            'error': 'Execution not found'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'execution': execution
    })


# =============================================================================
# WORKFLOW SCHEDULING
# =============================================================================

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def workflow_schedule(request, workflow_id):
    """
    POST: Schedule a workflow to run on a cron schedule
    DELETE: Remove schedule from workflow
    """
    from core.models_unified_system import CustomWorkflow, ScheduledWorkflow

    if request.method == 'POST':
        data = request.data

        cron_expression = data.get('cron_expression')
        if not cron_expression:
            return Response({
                'success': False,
                'error': 'cron_expression is required (e.g., "0 9 * * 1" for every Monday at 9am)'
            }, status=status.HTTP_400_BAD_REQUEST)

        default_topic = data.get('default_topic')
        if not default_topic:
            return Response({
                'success': False,
                'error': 'default_topic is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            workflow = CustomWorkflow.objects.get(
                id=workflow_id,
                created_by=request.user
            )
        except CustomWorkflow.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Workflow not found or not owned by you'
            }, status=status.HTTP_404_NOT_FOUND)

        # Create or update schedule
        schedule, created = ScheduledWorkflow.objects.update_or_create(
            custom_workflow=workflow,
            defaults={
                'cron_expression': cron_expression,
                'timezone': data.get('timezone', 'America/Denver'),
                'default_topic': default_topic,
                'default_parameters': data.get('default_parameters', {}),
                'is_active': True
            }
        )

        # Update workflow flags
        workflow.is_scheduled = True
        workflow.schedule_cron = cron_expression
        workflow.save()

        # TODO: Session 213 - Register with Celery Beat
        # This would require django-celery-beat integration

        return Response({
            'success': True,
            'message': 'Workflow scheduled' if created else 'Schedule updated',
            'schedule': {
                'id': str(schedule.id),
                'cron_expression': schedule.cron_expression,
                'timezone': schedule.timezone,
                'default_topic': schedule.default_topic,
                'is_active': schedule.is_active,
                'next_run_at': schedule.next_run_at.isoformat() if schedule.next_run_at else None
            }
        })

    elif request.method == 'DELETE':
        try:
            workflow = CustomWorkflow.objects.get(
                id=workflow_id,
                created_by=request.user
            )
        except CustomWorkflow.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Workflow not found or not owned by you'
            }, status=status.HTTP_404_NOT_FOUND)

        # Delete schedule
        ScheduledWorkflow.objects.filter(custom_workflow=workflow).delete()

        # Update workflow flags
        workflow.is_scheduled = False
        workflow.schedule_cron = ''
        workflow.save()

        return Response({
            'success': True,
            'message': 'Schedule removed'
        })


# =============================================================================
# WORKFLOW SHARING
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_share(request, workflow_id):
    """Make a workflow public or generate a share link."""
    from core.models_unified_system import CustomWorkflow

    try:
        workflow = CustomWorkflow.objects.get(
            id=workflow_id,
            created_by=request.user
        )
    except CustomWorkflow.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Workflow not found or not owned by you'
        }, status=status.HTTP_404_NOT_FOUND)

    # Make public
    workflow.is_public = True
    workflow.save()

    # Generate share URL
    share_url = f"/workflows/shared/{workflow.slug}"

    return Response({
        'success': True,
        'message': 'Workflow is now public',
        'share_url': share_url,
        'workflow_id': str(workflow.id),
        'slug': workflow.slug
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_unshare(request, workflow_id):
    """Make a workflow private."""
    from core.models_unified_system import CustomWorkflow

    try:
        workflow = CustomWorkflow.objects.get(
            id=workflow_id,
            created_by=request.user
        )
    except CustomWorkflow.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Workflow not found or not owned by you'
        }, status=status.HTTP_404_NOT_FOUND)

    workflow.is_public = False
    workflow.save()

    return Response({
        'success': True,
        'message': 'Workflow is now private'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def shared_workflow(request, slug):
    """Get a publicly shared workflow by slug."""
    from core.models_unified_system import CustomWorkflow

    try:
        workflow = CustomWorkflow.objects.get(
            slug=slug,
            is_public=True
        )
    except CustomWorkflow.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Workflow not found or not public'
        }, status=status.HTTP_404_NOT_FOUND)

    # Convert to dict
    data = {
        'id': str(workflow.id),
        'name': workflow.name,
        'slug': workflow.slug,
        'description': workflow.description,
        'content_type': workflow.content_type,
        'category': workflow.category,
        'use_count': workflow.use_count,
        'created_by': workflow.created_by.username,
        'steps': [
            {
                'order': step.order,
                'name': step.name,
                'description': step.description,
                'agent': step.agent
            }
            for step in workflow.steps.all().order_by('order')
        ],
        'step_count': workflow.steps.count()
    }

    return Response({
        'success': True,
        'workflow': data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_shared_workflow(request, slug):
    """Import a shared workflow to your own collection."""
    from core.models_unified_system import CustomWorkflow

    try:
        source_workflow = CustomWorkflow.objects.get(
            slug=slug,
            is_public=True
        )
    except CustomWorkflow.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Workflow not found or not public'
        }, status=status.HTTP_404_NOT_FOUND)

    # Duplicate to user's collection
    builder = get_workflow_builder(request.user)
    new_name = request.data.get('name', f"{source_workflow.name} (Imported)")

    workflow = builder.duplicate_workflow(str(source_workflow.id), new_name)

    if not workflow:
        return Response({
            'success': False,
            'error': 'Failed to import workflow'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Increment use count on source
    source_workflow.use_count += 1
    source_workflow.save()

    return Response({
        'success': True,
        'message': 'Workflow imported successfully',
        'workflow': workflow
    })


# =============================================================================
# PUBLIC WORKFLOW GALLERY
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def public_workflows(request):
    """Browse public workflows (gallery)."""
    from core.models_unified_system import CustomWorkflow

    category = request.query_params.get('category')
    sort_by = request.query_params.get('sort', 'popular')  # popular, recent, name
    limit = int(request.query_params.get('limit', 20))

    workflows = CustomWorkflow.objects.filter(is_public=True)

    if category:
        workflows = workflows.filter(category=category)

    if sort_by == 'popular':
        workflows = workflows.order_by('-use_count', '-created_at')
    elif sort_by == 'recent':
        workflows = workflows.order_by('-created_at')
    elif sort_by == 'name':
        workflows = workflows.order_by('name')

    workflows = workflows[:limit]

    data = [
        {
            'id': str(w.id),
            'name': w.name,
            'slug': w.slug,
            'description': w.description,
            'content_type': w.content_type,
            'category': w.category,
            'use_count': w.use_count,
            'created_by': w.created_by.username,
            'step_count': w.steps.count(),
            'created_at': w.created_at.isoformat()
        }
        for w in workflows
    ]

    return Response({
        'success': True,
        'count': len(data),
        'workflows': data
    })
