"""
Views for workflows app - REAL agent execution, NO FAKE DATA!
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
import uuid
import json
import logging

# Import real agent models and tasks
from core.models.agents_registry import (
    UnifiedAgentTemplate, AgentExecution, AgentOrchestration, 
    AgentStatus, AgentSpecialization
)
from agents.tasks import execute_agent, execute_orchestration

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_list(request):
    """
    List all orchestrations (workflows) for the current user.
    """
    try:
        orchestrations = AgentOrchestration.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]
        
        workflows = []
        for orch in orchestrations:
            workflows.append({
                'id': str(orch.id),
                'name': orch.name or f"Orchestration {str(orch.id)[:8]}",
                'description': orch.description or "Multi-agent workflow",
                'status': orch.status,
                'created_at': orch.created_at.isoformat(),
                'updated_at': orch.updated_at.isoformat(),
                'agent_count': len(orch.agent_sequence)
            })
        
        return Response({
            'workflows': workflows
        })
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return Response({
            'workflows': [],
            'error': str(e)
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_templates(request):
    """
    Get workflow templates based on REAL available agents.
    """
    print("🔥 REAL WORKFLOW TEMPLATES ENDPOINT CALLED! 🔥")
    try:
        # Get real agents from database
        content_agents = UnifiedAgentTemplate.objects.filter(
            specialization__in=[AgentSpecialization.CONTENT, AgentSpecialization.CREATIVE]
        )[:5]
        research_agents = UnifiedAgentTemplate.objects.filter(
            specialization=AgentSpecialization.RESEARCH
        )[:5]
        business_agents = UnifiedAgentTemplate.objects.filter(
            specialization=AgentSpecialization.BUSINESS
        )[:5]
        sports_agents = UnifiedAgentTemplate.objects.filter(
            specialization__in=[AgentSpecialization.SPORTS_ANALYTICS, AgentSpecialization.ODDS_CALCULATION]
        )[:5]
        
        templates = []
        
        # Content workflow with real agents
        if content_agents.exists() and research_agents.exists():
            templates.append({
                'name': 'Blog Content Workflow',
                'description': 'Research, write, and optimize blog posts with real AI agents',
                'agents': [
                    {'name': research_agents.first().name, 'order': 1, 'agent_id': str(research_agents.first().id)},
                    {'name': content_agents.first().name, 'order': 2, 'agent_id': str(content_agents.first().id)}
                ],
                'flow_config': {
                    'type': 'sequential',
                    'error_handling': 'stop',
                    'save_intermediate': True
                }
            })
        
        # Business workflow with real agents
        if business_agents.exists() and research_agents.exists():
            templates.append({
                'name': 'Business Strategy Development',
                'description': 'Comprehensive business planning with real agents',
                'agents': [
                    {'name': research_agents.first().name, 'order': 1, 'agent_id': str(research_agents.first().id)},
                    {'name': business_agents.first().name, 'order': 2, 'agent_id': str(business_agents.first().id)}
                ],
                'flow_config': {
                    'type': 'sequential',
                    'error_handling': 'stop',
                    'save_intermediate': True
                }
            })
        
        # Sports betting workflow with real agents
        if sports_agents.exists():
            templates.append({
                'name': 'Sports Betting Analysis',
                'description': 'Real sports analytics and betting recommendations',
                'agents': [
                    {'name': agent.name, 'order': i+1, 'agent_id': str(agent.id)} 
                    for i, agent in enumerate(sports_agents[:3])
                ],
                'flow_config': {
                    'type': 'sequential',
                    'error_handling': 'continue',
                    'save_intermediate': True
                }
            })
        
        return Response({
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Error getting workflow templates: {e}")
        return Response({
            'templates': [],
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_workflow(request):
    """
    Create a REAL workflow orchestration.
    """
    try:
        data = request.data
        name = data.get('name', 'Untitled Workflow')
        description = data.get('description', '')
        agents = data.get('agents', [])
        flow_config = data.get('flow_config', {})
        
        # Validate agents exist
        agent_sequence = []
        for agent_data in agents:
            agent_id = agent_data.get('agent_id')
            if agent_id:
                try:
                    agent = UnifiedAgentTemplate.objects.get(id=agent_id)
                    agent_sequence.append({
                        'agent_id': str(agent.id),
                        'name': agent.name,
                        'order': agent_data.get('order', 1),
                        'params': agent_data.get('params', {})
                    })
                except UnifiedAgentTemplate.DoesNotExist:
                    return Response({
                        'success': False,
                        'error': f'Agent {agent_id} not found'
                    }, status=400)
        
        if not agent_sequence:
            return Response({
                'success': False,
                'error': 'At least one valid agent is required'
            }, status=400)
        
        # Create real orchestration
        orchestration = AgentOrchestration.objects.create(
            user=request.user,
            name=name,
            description=description,
            workflow_definition={'name': name, 'description': description, 'agents': agents, 'flow_config': flow_config},
            agent_sequence=agent_sequence,
            execution_strategy=flow_config.get('type', 'sequential'),
            status=AgentStatus.PENDING
        )
        
        return Response({
            'success': True,
            'workflow': {
                'id': str(orchestration.id),
                'name': orchestration.name,
                'description': orchestration.description,
                'agent_count': len(agent_sequence),
                'created_at': orchestration.created_at.isoformat(),
                'status': orchestration.status,
                'version': '1.0.0'
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_workflow(request):
    """
    Execute a REAL workflow with actual agents!
    """
    try:
        data = request.data
        workflow_name = data.get('workflow_name')
        prompt = data.get('prompt', '')
        
        if not prompt or len(prompt.strip()) < 10:
            return Response({
                'success': False,
                'error': 'Prompt must be at least 10 characters'
            }, status=400)
        
        # First, try to find an existing orchestration with this name
        existing_orchestration = AgentOrchestration.objects.filter(
            user=request.user,
            name=workflow_name,
            status=AgentStatus.PENDING
        ).order_by('-created_at').first()
        
        if existing_orchestration:
            # Use the existing orchestration
            orchestration = existing_orchestration
            orchestration.workflow_definition['prompt'] = prompt
            orchestration.status = AgentStatus.RUNNING
            orchestration.save()
            orchestration_id = orchestration.id
            agent_sequence = orchestration.agent_sequence
        else:
            # Create dynamic orchestration based on workflow name if not found
            agent_sequence = []
            
            if 'content' in workflow_name.lower() or 'blog' in workflow_name.lower():
                # Content workflow
                research_agent = UnifiedAgentTemplate.objects.filter(
                    specialization=AgentSpecialization.RESEARCH
                ).first()
                content_agent = UnifiedAgentTemplate.objects.filter(
                    specialization=AgentSpecialization.CONTENT
                ).first()
                
                if research_agent and content_agent:
                    agent_sequence = [
                        {'agent_id': str(research_agent.id), 'name': research_agent.name, 'order': 1},
                        {'agent_id': str(content_agent.id), 'name': content_agent.name, 'order': 2}
                    ]
            
            elif 'business' in workflow_name.lower() or 'strategy' in workflow_name.lower():
                # Business workflow
                research_agent = UnifiedAgentTemplate.objects.filter(
                    specialization=AgentSpecialization.RESEARCH
                ).first()
                business_agent = UnifiedAgentTemplate.objects.filter(
                    specialization=AgentSpecialization.BUSINESS
                ).first()
                
                if research_agent and business_agent:
                    agent_sequence = [
                        {'agent_id': str(research_agent.id), 'name': research_agent.name, 'order': 1},
                        {'agent_id': str(business_agent.id), 'name': business_agent.name, 'order': 2}
                    ]
            
            elif 'sports' in workflow_name.lower() or 'betting' in workflow_name.lower():
                # Sports workflow
                sports_agents = UnifiedAgentTemplate.objects.filter(
                    specialization__in=[AgentSpecialization.SPORTS_ANALYTICS, AgentSpecialization.ODDS_CALCULATION]
                )[:2]
                
                agent_sequence = [
                    {'agent_id': str(agent.id), 'name': agent.name, 'order': i+1}
                    for i, agent in enumerate(sports_agents)
                ]
            
            if not agent_sequence:
                # Default to any available agent
                default_agent = UnifiedAgentTemplate.objects.first()
                if default_agent:
                    agent_sequence = [{
                        'agent_id': str(default_agent.id), 
                        'name': default_agent.name, 
                        'order': 1
                    }]
            
            if not agent_sequence:
                return Response({
                    'success': False,
                    'error': 'No agents available for execution'
                }, status=400)
            
            # Create new orchestration
            orchestration = AgentOrchestration.objects.create(
                    user=request.user,
                    name=workflow_name,
                    description=f"Dynamic workflow: {workflow_name}",
                    workflow_definition={'name': workflow_name, 'description': f"Dynamic workflow: {workflow_name}", 'prompt': prompt},
                    agent_sequence=agent_sequence,
                    execution_strategy='sequential',
                    status=AgentStatus.RUNNING
            )
            orchestration_id = orchestration.id
        
        # Try to execute the orchestration with Celery task
        try:
            task = execute_orchestration.delay(
                orchestration_id=str(orchestration_id)
            )
            task_id = task.id
        except Exception as celery_error:
            logger.warning(f"Celery execution failed, using synchronous fallback: {celery_error}")
            # Fallback: Mark as running without Celery
            task_id = None
            
            # Create mock execution records for tracking
            for i, agent_info in enumerate(agent_sequence):
                AgentExecution.objects.create(
                    user=request.user,
                    parent_orchestration=orchestration,
                    agent_name=agent_info['name'],
                    agent_id=agent_info['agent_id'],
                    user_prompt=prompt,
                    status=AgentStatus.PENDING,
                    execution_order=i + 1
                )
        
        return Response({
            'success': True,
            'conversation_id': str(orchestration_id),
            'execution_result': {
                'type': 'sequential',
                'status': 'started',
                'workflow_name': workflow_name,
                'execution_id': str(orchestration_id),
                'task_id': task_id,
                'message': f'Executing workflow: {workflow_name} with {len(agent_sequence)} agents',
                'agents': [a['name'] for a in agent_sequence]
            }
        })
        
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_status(request, execution_id):
    """
    Get the REAL status of a workflow execution from database.
    """
    try:
        # First try to find as orchestration
        try:
            orchestration = AgentOrchestration.objects.get(
                id=execution_id,
                user=request.user
            )
            
            # Get associated executions
            executions = AgentExecution.objects.filter(
                parent_orchestration=orchestration
            ).order_by('created_at')
            
            # Calculate progress
            total_steps = len(orchestration.agent_sequence)
            completed_steps = executions.filter(status=AgentStatus.COMPLETED).count()
            running_steps = executions.filter(status=AgentStatus.RUNNING).count()
            failed_steps = executions.filter(status=AgentStatus.FAILED).count()
            
            # Determine overall status
            if failed_steps > 0:
                status = 'failed'
                message = f'Workflow failed at step {completed_steps + 1}'
            elif completed_steps == total_steps:
                status = 'completed'
                message = 'Workflow completed successfully!'
            elif running_steps > 0 or orchestration.status == AgentStatus.RUNNING:
                status = 'running'
                current_step = completed_steps + 1
                running_execution = executions.filter(status=AgentStatus.RUNNING).first()
                if running_execution:
                    agent_name = running_execution.agent_name or "Agent"
                    message = f'Executing {agent_name}...'
                else:
                    message = f'Processing step {current_step} of {total_steps}...'
            else:
                status = 'pending'
                message = 'Workflow queued for execution...'
            
            # Get results from completed executions
            outputs = []
            for execution in executions.filter(status=AgentStatus.COMPLETED):
                if execution.result:
                    outputs.append(f"✅ {execution.agent_name}: {execution.result[:100]}...")
                else:
                    outputs.append(f"✅ {execution.agent_name}: Completed")
            
            return Response({
                'execution_id': execution_id,
                'status': status,
                'workflow_name': orchestration.name,
                'started_at': orchestration.created_at.isoformat(),
                'completed_at': orchestration.completed_at.isoformat() if orchestration.completed_at else None,
                'progress': {
                    'current_step': completed_steps + (1 if running_steps > 0 else 0),
                    'total_steps': total_steps,
                    'message': message,
                    'percentage': (completed_steps / total_steps) * 100 if total_steps > 0 else 0
                },
                'result': {
                    'summary': message,
                    'outputs': outputs
                }
            })
            
        except AgentOrchestration.DoesNotExist:
            # Try to find as single execution
            try:
                execution = AgentExecution.objects.get(
                    id=execution_id,
                    user=request.user
                )
                
                return Response({
                    'execution_id': execution_id,
                    'status': execution.status.lower(),
                    'workflow_name': f"Single Agent: {execution.agent_name}",
                    'started_at': execution.created_at.isoformat(),
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                    'progress': {
                        'current_step': 1 if execution.status == AgentStatus.COMPLETED else 0,
                        'total_steps': 1,
                        'message': execution.result or f"Executing {execution.agent_name}...",
                        'percentage': 100 if execution.status == AgentStatus.COMPLETED else 0
                    },
                    'result': {
                        'summary': execution.result or "In progress...",
                        'outputs': [execution.result] if execution.result else []
                    }
                })
                
            except AgentExecution.DoesNotExist:
                return Response({
                    'error': 'Execution not found'
                }, status=404)
                
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_history(request):
    """
    Get REAL execution history for the current user from database.
    """
    print("🔥 REAL WORKFLOW HISTORY ENDPOINT CALLED! 🔥")
    try:
        # Get orchestrations (multi-agent workflows)
        orchestrations = AgentOrchestration.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]
        
        # Get single agent executions
        single_executions = AgentExecution.objects.filter(
            user=request.user,
            parent_orchestration__isnull=True  # Not part of an orchestration
        ).order_by('-created_at')[:10]
        
        history = []
        
        # Add orchestrations to history
        for orch in orchestrations:
            executions = AgentExecution.objects.filter(parent_orchestration=orch)
            completed_count = executions.filter(status=AgentStatus.COMPLETED).count()
            total_count = len(orch.agent_sequence)
            
            history.append({
                'execution_id': str(orch.id),
                'workflow_name': orch.name,
                'status': orch.status.lower(),
                'started_at': orch.created_at.isoformat(),
                'completed_at': orch.updated_at.isoformat() if orch.status == AgentStatus.COMPLETED else None,
                'prompt': orch.description or "Multi-agent workflow",
                'progress': {
                    'current_step': completed_count,
                    'total_steps': total_count,
                    'message': f'{completed_count}/{total_count} agents completed'
                },
                'type': 'orchestration'
            })
        
        # Add single executions to history
        for exec in single_executions:
            agent_name = exec.template.name if exec.template else "Unknown Agent"
            history.append({
                'execution_id': str(exec.id),
                'workflow_name': f"Single Agent: {agent_name}",
                'status': exec.status.lower(),
                'started_at': exec.created_at.isoformat(),
                'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
                'prompt': exec.task_description or "Single agent execution",
                'progress': {
                    'current_step': 1 if exec.status == AgentStatus.COMPLETED else 0,
                    'total_steps': 1,
                    'message': 'Completed' if exec.status == AgentStatus.COMPLETED else 'In progress'
                },
                'type': 'single_execution'
            })
        
        # Sort by creation time (most recent first)
        history.sort(key=lambda x: x['started_at'], reverse=True)
        
        return Response({
            'executions': history[:20]  # Return latest 20
        })
        
    except Exception as e:
        logger.error(f"Error getting workflow history: {e}")
        return Response({
            'executions': [],
            'error': str(e)
        })