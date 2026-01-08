"""
Advanced Workflow Orchestration System.

Session 735: UPDATED to use REAL orchestration execution!
No more mock data - connects to AgentOrchestration and real agent execution.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import json
import uuid
import logging

from core.models.agents_registry import (
    AgentOrchestration, AgentExecution, UnifiedAgentTemplate, AgentStatus
)
from core.tasks_agents import execute_orchestration

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_advanced_workflow(request):
    """
    Create advanced multi-step workflow with conditional logic.
    Session 735: Now creates a REAL AgentOrchestration in the database.
    """
    user = request.user
    data = json.loads(request.body or b"{}")

    workflow_name = data.get('name', 'Untitled Workflow')
    description = data.get('description', '')
    steps = data.get('steps', [])
    execution_strategy = data.get('execution_strategy', 'sequential')

    # Build agent sequence from steps
    agent_sequence = []
    for step in steps:
        agent_name = step.get('agent_type', step.get('name', 'ResearchAgent'))
        # Normalize agent name
        if not agent_name.endswith('Agent'):
            agent_name = f"{agent_name.title()}Agent"
        agent_sequence.append(agent_name)

    # If no steps provided, use a default research workflow
    if not agent_sequence:
        agent_sequence = ['ResearchAgent', 'ContentWriterAgent']

    # Create REAL orchestration in database
    orchestration = AgentOrchestration.objects.create(
        name=workflow_name,
        description=description,
        user=user,
        agent_sequence=agent_sequence,
        execution_strategy=execution_strategy,
        workflow_definition={
            'type': 'advanced_workflow',
            'domain': 'general',
            'steps': steps,
            'triggers': data.get('triggers', []),
            'conditions': data.get('conditions', []),
            'notifications': data.get('notifications', {}),
        },
        status='pending'
    )

    logger.info(f"Created REAL advanced workflow: {orchestration.name} ({orchestration.id})")

    return Response({
        'success': True,
        'workflow': {
            'id': str(orchestration.id),
            'name': orchestration.name,
            'description': orchestration.description,
            'status': orchestration.status,
            'agent_sequence': orchestration.agent_sequence,
            'execution_strategy': orchestration.execution_strategy,
            'created_at': orchestration.created_at.isoformat(),
            'estimated_duration': f'{len(agent_sequence) * 30}-{len(agent_sequence) * 60} seconds',
            'complexity_score': min(10, len(agent_sequence)),
            'version': 1,
            'is_template': False
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_advanced_workflow(request):
    """
    Execute advanced workflow with real-time monitoring.
    Session 735: Now triggers REAL agent execution via Celery task!
    """
    user = request.user
    data = json.loads(request.body or b"{}")

    workflow_id = data.get('workflow_id', '')
    input_parameters = data.get('input_parameters', {})
    execution_mode = data.get('execution_mode', 'async')

    try:
        # Get the orchestration
        orchestration = AgentOrchestration.objects.get(id=workflow_id, user=user)
    except AgentOrchestration.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Workflow {workflow_id} not found'
        }, status=404)

    # Check if already running
    if orchestration.status == 'running':
        return Response({
            'success': False,
            'error': 'Workflow is already running'
        }, status=400)

    # Update workflow definition with input parameters
    if input_parameters:
        workflow_def = orchestration.workflow_definition or {}
        workflow_def['prompt'] = input_parameters.get('prompt', workflow_def.get('prompt', ''))
        workflow_def['input_parameters'] = input_parameters
        orchestration.workflow_definition = workflow_def

    # Reset and start execution
    orchestration.status = 'running'
    orchestration.current_agent_index = 0
    orchestration.progress_percentage = 0
    orchestration.intermediate_results = []
    orchestration.save()

    # Queue REAL execution via Celery
    execute_orchestration.delay(orchestration_id=str(orchestration.id))

    logger.info(f"🚀 Started REAL workflow execution: {orchestration.name} ({orchestration.id})")

    return Response({
        'success': True,
        'execution': {
            'id': str(orchestration.id),
            'workflow_id': str(orchestration.id),
            'status': 'running',
            'progress': {
                'current_step': 0,
                'total_steps': len(orchestration.agent_sequence),
                'completed_steps': 0,
                'progress_percentage': 0
            },
            'input_parameters': input_parameters,
            'execution_mode': execution_mode,
            'started_at': timezone.now().isoformat(),
            'estimated_completion': (timezone.now() + timedelta(seconds=len(orchestration.agent_sequence) * 40)).isoformat(),
            'step_results': [],
            'logs': [
                {
                    'timestamp': timezone.now().isoformat(),
                    'level': 'info',
                    'message': f'REAL workflow execution initiated with {len(orchestration.agent_sequence)} agents',
                    'step_id': None
                }
            ],
            'resource_usage': {
                'tokens_used': 0,
                'cost_incurred': 0.0,
                'execution_time_seconds': 0
            }
        },
        'monitoring': {
            'websocket_channel': f'workflow_execution_{orchestration.id}',
            'status_endpoint': f'/api/workflows/execution/{orchestration.id}/status/',
            'logs_endpoint': f'/api/workflows/execution/{orchestration.id}/logs/'
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workflow_execution_status(request, execution_id):
    """
    Get real-time workflow execution status.
    Session 735: Returns REAL status from AgentOrchestration!
    """
    user = request.user

    try:
        orchestration = AgentOrchestration.objects.get(id=execution_id)
    except AgentOrchestration.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Workflow execution {execution_id} not found'
        }, status=404)

    # Build step results from intermediate_results
    step_results = []
    total_tokens = 0
    total_cost = 0.0
    total_time = 0.0

    for i, result in enumerate(orchestration.intermediate_results or []):
        agent_name = result.get('agent', f'Step {i+1}')
        result_data = result.get('result', {})
        execution_time_ms = result_data.get('execution_time_ms', 0) or 0

        step_results.append({
            'step_id': f'step_{i+1}',
            'name': agent_name,
            'status': 'completed' if result_data.get('success') else 'failed',
            'result': result_data.get('message', '')[:500] if result_data.get('message') else 'Completed',
            'execution_time_seconds': execution_time_ms / 1000,
            'tokens_used': 0,  # Would need token tracking in agent execution
            'cost': 0.0
        })
        total_time += execution_time_ms / 1000

    # Add current running step if in progress
    current_idx = orchestration.current_agent_index or 0
    if orchestration.status == 'running' and current_idx < len(orchestration.agent_sequence):
        current_agent = orchestration.agent_sequence[current_idx]
        if isinstance(current_agent, dict):
            current_agent = current_agent.get('name', current_agent.get('agent', f'Step {current_idx+1}'))

        step_results.append({
            'step_id': f'step_{current_idx+1}',
            'name': current_agent,
            'status': 'running',
            'result': None,
            'execution_time_seconds': 0,
            'tokens_used': 0,
            'cost': 0.0
        })

    status = {
        'id': str(orchestration.id),
        'status': orchestration.status,
        'progress': {
            'current_step': (orchestration.current_agent_index or 0) + 1,
            'total_steps': len(orchestration.agent_sequence),
            'completed_steps': len(orchestration.intermediate_results or []),
            'progress_percentage': orchestration.progress_percentage or 0,
            'current_step_name': orchestration.agent_sequence[orchestration.current_agent_index] if orchestration.current_agent_index and orchestration.current_agent_index < len(orchestration.agent_sequence) else None,
            'current_step_progress': 50 if orchestration.status == 'running' else 100
        },
        'step_results': step_results,
        'resource_usage': {
            'total_tokens_used': total_tokens,
            'total_cost_incurred': float(orchestration.total_cost or 0),
            'total_execution_time_seconds': orchestration.total_execution_time or total_time
        },
        'started_at': orchestration.created_at.isoformat(),
        'updated_at': orchestration.updated_at.isoformat(),
        'estimated_completion': None
    }

    return Response({
        'success': True,
        'execution_status': status
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflow_templates(request):
    """
    Get available workflow templates from REAL orchestrations.
    Session 735: Returns templates based on actual system orchestrations.
    """
    user = request.user
    category = request.GET.get('category', 'all')

    # Get predefined orchestrations as templates
    from core.management.commands.sync_orchestrations import ORCHESTRATIONS

    templates = []
    for orch in ORCHESTRATIONS:
        workflow_def = orch.get('workflow_definition', {})
        domain = workflow_def.get('domain', 'general')

        # Map domains to categories
        category_map = {
            'blockchain': 'technical',
            'stocks': 'business',
            'markets': 'business',
            'culture': 'creative',
            'content': 'marketing',
            'media': 'creative',
        }
        orch_category = category_map.get(domain, 'business')

        if category != 'all' and orch_category != category:
            continue

        templates.append({
            'id': orch['name'].lower().replace(' ', '_'),
            'name': orch['name'],
            'description': orch['description'],
            'category': orch_category,
            'steps': orch['agent_sequence'],
            'execution_strategy': orch['execution_strategy'],
            'estimated_duration': f'{len(orch["agent_sequence"]) * 30}-{len(orch["agent_sequence"]) * 60} seconds',
            'complexity': 'high' if len(orch['agent_sequence']) > 4 else 'medium',
            'usage_count': AgentOrchestration.objects.filter(name=orch['name']).count(),
            'rating': 4.5,
            'last_updated': timezone.now().isoformat()
        })

    # Also include any user-created orchestrations as templates
    user_orchestrations = AgentOrchestration.objects.filter(
        user=user, status='completed'
    ).order_by('-created_at')[:5]

    for orch in user_orchestrations:
        templates.append({
            'id': str(orch.id),
            'name': orch.name,
            'description': orch.description or 'User-created workflow',
            'category': 'custom',
            'steps': orch.agent_sequence,
            'execution_strategy': orch.execution_strategy,
            'estimated_duration': f'{orch.total_execution_time:.0f} seconds' if orch.total_execution_time else 'Unknown',
            'complexity': 'high' if len(orch.agent_sequence) > 4 else 'medium',
            'usage_count': 1,
            'rating': 5.0,
            'last_updated': orch.updated_at.isoformat()
        })

    return Response({
        'success': True,
        'templates': templates,
        'total_templates': len(templates),
        'categories': ['business', 'marketing', 'technical', 'creative', 'custom'],
        'popular_templates': sorted(templates, key=lambda x: x['usage_count'], reverse=True)[:3]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_workflow_from_template(request):
    """
    Create workflow from template with customization.
    Session 735: Creates REAL AgentOrchestration from template.
    """
    user = request.user
    data = json.loads(request.body or b"{}")

    template_id = data.get('template_id', '')
    customizations = data.get('customizations', {})
    workflow_name = data.get('name', 'Workflow from Template')

    # Find the template
    from core.management.commands.sync_orchestrations import ORCHESTRATIONS

    template = None
    for orch in ORCHESTRATIONS:
        if orch['name'].lower().replace(' ', '_') == template_id or orch['name'] == template_id:
            template = orch
            break

    # Also check user orchestrations
    if not template:
        try:
            existing = AgentOrchestration.objects.get(id=template_id, user=user)
            template = {
                'name': existing.name,
                'description': existing.description,
                'agent_sequence': existing.agent_sequence,
                'execution_strategy': existing.execution_strategy,
                'workflow_definition': existing.workflow_definition,
            }
        except (AgentOrchestration.DoesNotExist, ValueError):
            pass

    if not template:
        return Response({
            'success': False,
            'error': f'Template {template_id} not found'
        }, status=404)

    # Create new orchestration from template
    orchestration = AgentOrchestration.objects.create(
        name=workflow_name,
        description=template.get('description', ''),
        user=user,
        agent_sequence=customizations.get('agent_sequence', template['agent_sequence']),
        execution_strategy=customizations.get('execution_strategy', template['execution_strategy']),
        workflow_definition={
            **template.get('workflow_definition', {}),
            'from_template': template_id,
            'customizations': customizations,
        },
        status='pending'
    )

    logger.info(f"Created workflow from template: {orchestration.name} ({orchestration.id})")

    return Response({
        'success': True,
        'workflow': {
            'id': str(orchestration.id),
            'name': orchestration.name,
            'template_id': template_id,
            'status': 'pending',
            'customizations_applied': customizations,
            'agent_sequence': orchestration.agent_sequence,
            'execution_strategy': orchestration.execution_strategy,
            'created_at': orchestration.created_at.isoformat()
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_workflows(request):
    """
    List all workflows for the current user.
    Session 735: Returns REAL orchestrations from database.
    """
    user = request.user
    status_filter = request.GET.get('status', None)

    queryset = AgentOrchestration.objects.filter(user=user).order_by('-created_at')

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    workflows = []
    for orch in queryset[:50]:
        workflows.append({
            'id': str(orch.id),
            'name': orch.name,
            'description': orch.description,
            'status': orch.status,
            'agent_sequence': orch.agent_sequence,
            'execution_strategy': orch.execution_strategy,
            'progress_percentage': orch.progress_percentage,
            'total_execution_time': orch.total_execution_time,
            'total_cost': float(orch.total_cost) if orch.total_cost else None,
            'created_at': orch.created_at.isoformat(),
            'updated_at': orch.updated_at.isoformat(),
            'steps_completed': len(orch.intermediate_results or []),
            'total_steps': len(orch.agent_sequence)
        })

    return Response({
        'success': True,
        'workflows': workflows,
        'total_count': queryset.count()
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_workflow(request, workflow_id):
    """
    Delete a workflow.
    Session 735: Deletes REAL orchestration from database.
    """
    user = request.user

    try:
        orchestration = AgentOrchestration.objects.get(id=workflow_id, user=user)
    except AgentOrchestration.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Workflow {workflow_id} not found'
        }, status=404)

    if orchestration.status == 'running':
        return Response({
            'success': False,
            'error': 'Cannot delete a running workflow'
        }, status=400)

    name = orchestration.name
    orchestration.delete()

    logger.info(f"Deleted workflow: {name} ({workflow_id})")

    return Response({
        'success': True,
        'message': f'Workflow "{name}" deleted successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workflow_output(request, execution_id):
    """
    Session 735: Get full orchestration output including all agent results.

    Returns the complete intermediate_results and final_result for viewing
    what each agent actually produced.
    """
    user = request.user

    try:
        orchestration = AgentOrchestration.objects.get(id=execution_id)
    except AgentOrchestration.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Workflow execution {execution_id} not found'
        }, status=404)

    # Get all agent executions for this orchestration
    executions = AgentExecution.objects.filter(
        parent_orchestration=orchestration
    ).order_by('created_at')

    agent_outputs = []
    for exec in executions:
        result = exec.result or {}
        agent_outputs.append({
            'agent_name': exec.template.name if exec.template else 'Unknown',
            'execution_id': exec.execution_id,
            'status': exec.status,
            'task_description': exec.task_description,
            'full_output': result.get('message', ''),
            'data': result.get('data'),
            'execution_time_ms': result.get('execution_time_ms', 0),
            'cost': result.get('cost', 0.0),
            'tokens_used': result.get('tokens_used', 0),
            'created_at': exec.created_at.isoformat(),
            'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
        })

    return Response({
        'success': True,
        'orchestration': {
            'id': str(orchestration.id),
            'name': orchestration.name,
            'status': orchestration.status,
            'total_execution_time': orchestration.total_execution_time,
            'total_cost': float(orchestration.total_cost) if orchestration.total_cost else 0.0,
            'created_at': orchestration.created_at.isoformat(),
        },
        'agent_outputs': agent_outputs,
        'intermediate_results': orchestration.intermediate_results or [],
        'final_result': orchestration.final_result,
        'raw_output_count': len(agent_outputs),
    })
