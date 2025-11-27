"""
Session 227: Phase 3 - Team Power API Endpoints
Multi-agent collaboration for complex creative tasks
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


# =============================================================================
# AGENT ROLES API
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_agent_roles(request):
    """
    GET /api/teams/roles/
    List all available agent roles.
    """
    try:
        from core.models_unified_system import AgentRole

        roles = AgentRole.objects.filter(is_active=True).order_by('-priority', 'name')

        return JsonResponse({
            'success': True,
            'roles': [{
                'id': str(role.id),
                'name': role.name,
                'role_type': role.role_type,
                'description': role.description,
                'capabilities': role.capabilities,
                'available_tools': role.available_tools,
                'priority': role.priority,
            } for role in roles]
        })

    except Exception as e:
        logger.error(f"Error listing roles: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_agent_role(request):
    """
    POST /api/teams/roles/
    Create a new agent role.
    """
    try:
        from core.models_unified_system import AgentRole

        data = json.loads(request.body) if request.body else {}

        role = AgentRole.objects.create(
            name=data.get('name', 'New Role'),
            role_type=data.get('role_type', 'custom'),
            description=data.get('description', ''),
            capabilities=data.get('capabilities', []),
            available_tools=data.get('available_tools', []),
            constraints=data.get('constraints', {}),
            role_prompt=data.get('role_prompt', ''),
            priority=data.get('priority', 5),
        )

        return JsonResponse({
            'success': True,
            'message': f'Role "{role.name}" created',
            'role': {
                'id': str(role.id),
                'name': role.name,
                'role_type': role.role_type,
            }
        })

    except Exception as e:
        logger.error(f"Error creating role: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# AGENT TEAMS API
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_teams(request):
    """
    GET /api/teams/
    List all agent teams.
    """
    try:
        from core.models_unified_system import AgentTeam

        teams = AgentTeam.objects.filter(is_active=True).prefetch_related('memberships__agent', 'memberships__role')

        return JsonResponse({
            'success': True,
            'teams': [{
                'id': str(team.id),
                'name': team.name,
                'description': team.description,
                'team_type': team.team_type,
                'member_count': team.memberships.count(),
                'lead_agent': {
                    'id': str(team.lead_agent.id),
                    'name': team.lead_agent.name
                } if team.lead_agent else None,
                'members': [{
                    'agent_id': str(m.agent.id),
                    'agent_name': m.agent.name,
                    'role': m.role.name if m.role else None,
                    'is_lead': m.is_lead,
                } for m in team.memberships.all()],
                'created_at': team.created_at.isoformat(),
            } for team in teams]
        })

    except Exception as e:
        logger.error(f"Error listing teams: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_team(request):
    """
    POST /api/teams/
    Create a new agent team.

    Request body:
    {
        "name": "Creative Team Alpha",
        "description": "Logo and branding specialists",
        "team_type": "creative",
        "members": [
            {"agent_id": "uuid", "role_id": "uuid", "is_lead": true},
            {"agent_id": "uuid", "role_id": "uuid"}
        ]
    }
    """
    try:
        from core.models_unified_system import AgentTeam, AgentTeamMembership, Agent, AgentRole

        data = json.loads(request.body) if request.body else {}

        # Create team
        team = AgentTeam.objects.create(
            name=data.get('name', 'New Team'),
            description=data.get('description', ''),
            team_type=data.get('team_type', 'custom'),
            settings=data.get('settings', {}),
        )

        # Add members
        members_data = data.get('members', [])
        lead_agent = None

        for member_info in members_data:
            agent = Agent.objects.get(id=member_info['agent_id'])
            role = AgentRole.objects.get(id=member_info['role_id']) if member_info.get('role_id') else None

            membership = AgentTeamMembership.objects.create(
                team=team,
                agent=agent,
                role=role,
                is_lead=member_info.get('is_lead', False),
                can_delegate=member_info.get('can_delegate', False),
            )

            if membership.is_lead:
                lead_agent = agent

        # Set team lead
        if lead_agent:
            team.lead_agent = lead_agent
            team.save()

        return JsonResponse({
            'success': True,
            'message': f'Team "{team.name}" created with {len(members_data)} members',
            'team': {
                'id': str(team.id),
                'name': team.name,
                'team_type': team.team_type,
                'member_count': len(members_data),
            }
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except AgentRole.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Role not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_team(request, team_id):
    """
    GET /api/teams/<team_id>/
    Get team details with all members and their roles.
    """
    try:
        from core.models_unified_system import AgentTeam

        team = AgentTeam.objects.prefetch_related(
            'memberships__agent', 'memberships__role', 'workflows'
        ).get(id=team_id)

        return JsonResponse({
            'success': True,
            'team': {
                'id': str(team.id),
                'name': team.name,
                'description': team.description,
                'team_type': team.team_type,
                'settings': team.settings,
                'lead_agent': {
                    'id': str(team.lead_agent.id),
                    'name': team.lead_agent.name
                } if team.lead_agent else None,
                'members': [{
                    'membership_id': str(m.id),
                    'agent': {
                        'id': str(m.agent.id),
                        'name': m.agent.name,
                        'category': m.agent.category.name if m.agent.category else None,
                    },
                    'role': {
                        'id': str(m.role.id),
                        'name': m.role.name,
                        'role_type': m.role.role_type,
                        'capabilities': m.role.capabilities,
                    } if m.role else None,
                    'is_lead': m.is_lead,
                    'can_delegate': m.can_delegate,
                    'joined_at': m.joined_at.isoformat(),
                } for m in team.memberships.all()],
                'active_workflows': team.workflows.filter(status='active').count(),
                'completed_workflows': team.workflows.filter(status='completed').count(),
                'created_at': team.created_at.isoformat(),
            }
        })

    except AgentTeam.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Team not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting team: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_team_member(request, team_id):
    """
    POST /api/teams/<team_id>/members/
    Add a member to a team.
    """
    try:
        from core.models_unified_system import AgentTeam, AgentTeamMembership, Agent, AgentRole

        team = AgentTeam.objects.get(id=team_id)
        data = json.loads(request.body) if request.body else {}

        agent = Agent.objects.get(id=data['agent_id'])
        role = AgentRole.objects.get(id=data['role_id']) if data.get('role_id') else None

        # Check if already a member
        if AgentTeamMembership.objects.filter(team=team, agent=agent).exists():
            return JsonResponse({
                'success': False,
                'error': f'{agent.name} is already a member of this team'
            }, status=400)

        membership = AgentTeamMembership.objects.create(
            team=team,
            agent=agent,
            role=role,
            is_lead=data.get('is_lead', False),
            can_delegate=data.get('can_delegate', False),
        )

        return JsonResponse({
            'success': True,
            'message': f'{agent.name} added to {team.name}',
            'membership': {
                'id': str(membership.id),
                'agent_name': agent.name,
                'role': role.name if role else None,
            }
        })

    except AgentTeam.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Team not found'}, status=404)
    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error adding team member: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# AGENT MESSAGES API
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def send_agent_message(request):
    """
    POST /api/teams/messages/
    Send a message from one agent to another.
    """
    try:
        from core.models_unified_system import AgentMessage, Agent
        import uuid as uuid_lib

        data = json.loads(request.body) if request.body else {}

        sender = Agent.objects.get(id=data['sender_agent_id'])
        receiver = Agent.objects.get(id=data['receiver_agent_id'])

        # Create thread ID if not provided (new conversation)
        thread_id = data.get('thread_id') or uuid_lib.uuid4()

        # Get parent message if replying
        parent_message = None
        if data.get('parent_message_id'):
            parent_message = AgentMessage.objects.get(id=data['parent_message_id'])
            thread_id = parent_message.thread_id

        message = AgentMessage.objects.create(
            sender_agent=sender,
            receiver_agent=receiver,
            message_type=data.get('message_type', 'notification'),
            subject=data.get('subject', 'No subject'),
            content=data.get('content', ''),
            attachments=data.get('attachments', []),
            parent_message=parent_message,
            thread_id=thread_id,
            task_context=data.get('task_context', {}),
            priority=data.get('priority', 5),
        )

        return JsonResponse({
            'success': True,
            'message': f'Message sent from {sender.name} to {receiver.name}',
            'agent_message': {
                'id': str(message.id),
                'thread_id': str(message.thread_id),
                'message_type': message.message_type,
                'subject': message.subject,
                'status': message.status,
            }
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except AgentMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Parent message not found'}, status=404)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_agent_messages(request, agent_id):
    """
    GET /api/teams/messages/<agent_id>/
    Get messages for an agent (inbox).
    """
    try:
        from core.models_unified_system import AgentMessage, Agent

        agent = Agent.objects.get(id=agent_id)

        # Get inbox (received messages)
        inbox = request.GET.get('inbox', 'true').lower() == 'true'
        status_filter = request.GET.get('status')
        limit = int(request.GET.get('limit', 50))

        if inbox:
            queryset = AgentMessage.objects.filter(receiver_agent=agent)
        else:
            queryset = AgentMessage.objects.filter(sender_agent=agent)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        messages = queryset.select_related('sender_agent', 'receiver_agent')[:limit]

        return JsonResponse({
            'success': True,
            'agent': {'id': str(agent.id), 'name': agent.name},
            'inbox': inbox,
            'messages': [{
                'id': str(msg.id),
                'thread_id': str(msg.thread_id),
                'message_type': msg.message_type,
                'subject': msg.subject,
                'content': msg.content[:200] + '...' if len(msg.content) > 200 else msg.content,
                'sender': {'id': str(msg.sender_agent.id), 'name': msg.sender_agent.name},
                'receiver': {'id': str(msg.receiver_agent.id), 'name': msg.receiver_agent.name},
                'status': msg.status,
                'priority': msg.priority,
                'created_at': msg.created_at.isoformat(),
                'has_attachments': len(msg.attachments) > 0,
            } for msg in messages],
            'total': queryset.count(),
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_message_thread(request, thread_id):
    """
    GET /api/teams/messages/thread/<thread_id>/
    Get all messages in a conversation thread.
    """
    try:
        from core.models_unified_system import AgentMessage

        messages = AgentMessage.objects.filter(thread_id=thread_id).select_related(
            'sender_agent', 'receiver_agent', 'parent_message'
        ).order_by('created_at')

        return JsonResponse({
            'success': True,
            'thread_id': str(thread_id),
            'message_count': messages.count(),
            'messages': [{
                'id': str(msg.id),
                'message_type': msg.message_type,
                'subject': msg.subject,
                'content': msg.content,
                'sender': {'id': str(msg.sender_agent.id), 'name': msg.sender_agent.name},
                'receiver': {'id': str(msg.receiver_agent.id), 'name': msg.receiver_agent.name},
                'parent_id': str(msg.parent_message.id) if msg.parent_message else None,
                'attachments': msg.attachments,
                'status': msg.status,
                'created_at': msg.created_at.isoformat(),
            } for msg in messages]
        })

    except Exception as e:
        logger.error(f"Error getting thread: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# TEAM WORKFLOWS API
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def create_team_workflow(request):
    """
    POST /api/teams/workflows/
    Create a new collaborative workflow for a team.
    """
    try:
        from core.models_unified_system import TeamWorkflow, TeamWorkflowStep, AgentTeam, Opportunity, AgentRole

        data = json.loads(request.body) if request.body else {}

        team = AgentTeam.objects.get(id=data['team_id'])

        # Get opportunity if provided
        opportunity = None
        if data.get('opportunity_id'):
            opportunity = Opportunity.objects.get(id=data['opportunity_id'])

        # Create workflow
        workflow = TeamWorkflow.objects.create(
            name=data.get('name', f'{team.name} Workflow'),
            description=data.get('description', ''),
            team=team,
            opportunity=opportunity,
            workflow_template=data.get('workflow_template', ''),
            steps=data.get('steps', []),
            user=request.user if request.user.is_authenticated else None,
        )

        # Create step execution records
        for i, step_def in enumerate(data.get('steps', [])):
            required_role = None
            if step_def.get('role_type'):
                required_role = AgentRole.objects.filter(role_type=step_def['role_type']).first()

            TeamWorkflowStep.objects.create(
                workflow=workflow,
                step_number=i + 1,
                step_name=step_def.get('name', f'Step {i + 1}'),
                action=step_def.get('action', ''),
                required_role=required_role,
                input_data=step_def.get('input', {}),
            )

        return JsonResponse({
            'success': True,
            'message': f'Workflow "{workflow.name}" created with {len(data.get("steps", []))} steps',
            'workflow': {
                'id': str(workflow.id),
                'name': workflow.name,
                'team': team.name,
                'status': workflow.status,
                'step_count': workflow.step_executions.count(),
            }
        })

    except AgentTeam.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Team not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def start_team_workflow(request, workflow_id):
    """
    POST /api/teams/workflows/<workflow_id>/start/
    Start executing a team workflow.
    """
    try:
        from core.models_unified_system import TeamWorkflow, TeamWorkflowStep, AgentMessage

        workflow = TeamWorkflow.objects.get(id=workflow_id)

        if workflow.status != 'draft':
            return JsonResponse({
                'success': False,
                'error': f'Workflow is already {workflow.status}'
            }, status=400)

        # Update workflow status
        workflow.status = 'active'
        workflow.started_at = timezone.now()
        workflow.current_step = 1
        workflow.save()

        # Get first step and assign agent
        first_step = workflow.step_executions.filter(step_number=1).first()
        if first_step:
            # Find an agent with the required role in the team
            if first_step.required_role:
                membership = workflow.team.memberships.filter(role=first_step.required_role).first()
                if membership:
                    first_step.assigned_agent = membership.agent
                    first_step.status = 'assigned'
                    first_step.save()

                    # Send notification to assigned agent
                    if workflow.team.lead_agent and membership.agent != workflow.team.lead_agent:
                        AgentMessage.objects.create(
                            sender_agent=workflow.team.lead_agent,
                            receiver_agent=membership.agent,
                            message_type='request',
                            subject=f'New task: {first_step.step_name}',
                            content=f'You have been assigned step {first_step.step_number} in workflow "{workflow.name}".',
                            task_context={
                                'workflow_id': str(workflow.id),
                                'step_id': str(first_step.id),
                            },
                            priority=7,
                        )

        return JsonResponse({
            'success': True,
            'message': f'Workflow "{workflow.name}" started',
            'workflow': {
                'id': str(workflow.id),
                'status': workflow.status,
                'current_step': workflow.current_step,
                'first_step_assigned_to': first_step.assigned_agent.name if first_step and first_step.assigned_agent else None,
            }
        })

    except TeamWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Workflow not found'}, status=404)
    except Exception as e:
        logger.error(f"Error starting workflow: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_team_workflow(request, workflow_id):
    """
    GET /api/teams/workflows/<workflow_id>/
    Get workflow details with all steps.
    """
    try:
        from core.models_unified_system import TeamWorkflow

        workflow = TeamWorkflow.objects.prefetch_related(
            'step_executions__assigned_agent',
            'step_executions__required_role',
            'step_executions__reviewer_agent',
        ).select_related('team', 'opportunity', 'current_agent').get(id=workflow_id)

        return JsonResponse({
            'success': True,
            'workflow': {
                'id': str(workflow.id),
                'name': workflow.name,
                'description': workflow.description,
                'team': {
                    'id': str(workflow.team.id),
                    'name': workflow.team.name,
                },
                'opportunity': {
                    'id': str(workflow.opportunity.id),
                    'title': workflow.opportunity.title,
                } if workflow.opportunity else None,
                'status': workflow.status,
                'progress': workflow.progress,
                'current_step': workflow.current_step,
                'current_agent': {
                    'id': str(workflow.current_agent.id),
                    'name': workflow.current_agent.name,
                } if workflow.current_agent else None,
                'steps': [{
                    'id': str(step.id),
                    'step_number': step.step_number,
                    'step_name': step.step_name,
                    'action': step.action,
                    'status': step.status,
                    'assigned_agent': {
                        'id': str(step.assigned_agent.id),
                        'name': step.assigned_agent.name,
                    } if step.assigned_agent else None,
                    'required_role': step.required_role.name if step.required_role else None,
                    'review_score': step.review_score,
                    'review_feedback': step.review_feedback,
                    'started_at': step.started_at.isoformat() if step.started_at else None,
                    'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                } for step in workflow.step_executions.all()],
                'results': workflow.results,
                'errors': workflow.errors,
                'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
                'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
            }
        })

    except TeamWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Workflow not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def complete_workflow_step(request, workflow_id, step_id):
    """
    POST /api/teams/workflows/<workflow_id>/steps/<step_id>/complete/
    Mark a workflow step as completed and advance to next step.
    """
    try:
        from core.models_unified_system import TeamWorkflow, TeamWorkflowStep, AgentMessage

        workflow = TeamWorkflow.objects.get(id=workflow_id)
        step = TeamWorkflowStep.objects.get(id=step_id, workflow=workflow)

        data = json.loads(request.body) if request.body else {}

        # Update step
        step.status = 'completed'
        step.completed_at = timezone.now()
        step.output_data = data.get('output', {})
        step.save()

        # Check if there's a next step
        next_step = workflow.step_executions.filter(step_number=step.step_number + 1).first()

        if next_step:
            # Advance workflow
            workflow.current_step = next_step.step_number
            workflow.progress = int((step.step_number / workflow.step_executions.count()) * 100)

            # Auto-assign next step if role is defined
            if next_step.required_role:
                membership = workflow.team.memberships.filter(role=next_step.required_role).first()
                if membership:
                    next_step.assigned_agent = membership.agent
                    next_step.status = 'assigned'
                    next_step.input_data = step.output_data  # Pass output as input to next step
                    next_step.save()

                    # Notify next agent
                    if step.assigned_agent:
                        AgentMessage.objects.create(
                            sender_agent=step.assigned_agent,
                            receiver_agent=membership.agent,
                            message_type='handoff',
                            subject=f'Handoff: {next_step.step_name}',
                            content=f'Step {step.step_number} is complete. You are now assigned to step {next_step.step_number}.',
                            task_context={
                                'workflow_id': str(workflow.id),
                                'step_id': str(next_step.id),
                                'previous_output': step.output_data,
                            },
                            priority=7,
                        )

            workflow.save()

            return JsonResponse({
                'success': True,
                'message': f'Step {step.step_number} completed, advancing to step {next_step.step_number}',
                'workflow': {
                    'id': str(workflow.id),
                    'status': workflow.status,
                    'progress': workflow.progress,
                    'current_step': workflow.current_step,
                },
                'next_step': {
                    'id': str(next_step.id),
                    'step_name': next_step.step_name,
                    'assigned_to': next_step.assigned_agent.name if next_step.assigned_agent else None,
                }
            })
        else:
            # Workflow complete
            workflow.status = 'completed'
            workflow.progress = 100
            workflow.completed_at = timezone.now()
            workflow.save()

            return JsonResponse({
                'success': True,
                'message': f'Workflow "{workflow.name}" completed!',
                'workflow': {
                    'id': str(workflow.id),
                    'status': workflow.status,
                    'progress': workflow.progress,
                    'completed_at': workflow.completed_at.isoformat(),
                }
            })

    except TeamWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Workflow not found'}, status=404)
    except TeamWorkflowStep.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Step not found'}, status=404)
    except Exception as e:
        logger.error(f"Error completing step: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# TEAM STATISTICS API
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def team_stats(request):
    """
    GET /api/teams/stats/
    Get overall team collaboration statistics.
    """
    try:
        from core.models_unified_system import AgentTeam, AgentRole, AgentMessage, TeamWorkflow

        return JsonResponse({
            'success': True,
            'stats': {
                'teams': {
                    'total': AgentTeam.objects.filter(is_active=True).count(),
                    'by_type': list(AgentTeam.objects.filter(is_active=True).values('team_type').annotate(count=Count('id'))),
                },
                'roles': {
                    'total': AgentRole.objects.filter(is_active=True).count(),
                    'by_type': list(AgentRole.objects.filter(is_active=True).values('role_type').annotate(count=Count('id'))),
                },
                'messages': {
                    'total': AgentMessage.objects.count(),
                    'pending': AgentMessage.objects.filter(status='sent').count(),
                    'processed': AgentMessage.objects.filter(status='processed').count(),
                },
                'workflows': {
                    'total': TeamWorkflow.objects.count(),
                    'active': TeamWorkflow.objects.filter(status='active').count(),
                    'completed': TeamWorkflow.objects.filter(status='completed').count(),
                    'failed': TeamWorkflow.objects.filter(status='failed').count(),
                },
            }
        })

    except Exception as e:
        logger.error(f"Error getting team stats: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SEED DEFAULT ROLES
# =============================================================================

def seed_default_roles():
    """
    Create default agent roles for team collaboration.
    Call this from a management command or migration.
    """
    from core.models_unified_system import AgentRole

    default_roles = [
        {
            'name': 'Lead Designer',
            'role_type': 'designer',
            'description': 'Creates visual content including logos, graphics, and UI elements',
            'capabilities': ['image_generation', 'style_transfer', 'logo_design', 'brand_identity', 'color_theory'],
            'available_tools': ['stability_ai', 'runway_ml', 'midjourney'],
            'priority': 8,
            'role_prompt': 'You are a creative lead designer specializing in visual content creation.',
        },
        {
            'name': 'Research Specialist',
            'role_type': 'researcher',
            'description': 'Gathers market intelligence, trends, and competitive analysis',
            'capabilities': ['web_search', 'trend_analysis', 'market_research', 'competitive_analysis'],
            'available_tools': ['web_search', 'news_api', 'spider_network'],
            'priority': 7,
            'role_prompt': 'You are a research specialist focused on gathering actionable intelligence.',
        },
        {
            'name': 'Quality Reviewer',
            'role_type': 'reviewer',
            'description': 'Reviews and provides feedback on work quality',
            'capabilities': ['quality_assessment', 'feedback_generation', 'brand_compliance', 'style_consistency'],
            'available_tools': [],
            'priority': 6,
            'role_prompt': 'You are a quality reviewer ensuring all outputs meet professional standards.',
        },
        {
            'name': 'Content Writer',
            'role_type': 'writer',
            'description': 'Creates written content including copy, descriptions, and documentation',
            'capabilities': ['copywriting', 'seo_writing', 'description_generation', 'documentation'],
            'available_tools': ['gpt', 'claude'],
            'priority': 7,
            'role_prompt': 'You are a skilled content writer creating compelling copy.',
        },
        {
            'name': 'Data Analyst',
            'role_type': 'analyst',
            'description': 'Analyzes data, metrics, and trends to inform decisions',
            'capabilities': ['data_analysis', 'trend_detection', 'metrics_tracking', 'reporting'],
            'available_tools': ['analytics_api', 'spider_network'],
            'priority': 6,
            'role_prompt': 'You are a data analyst providing insights from metrics and trends.',
        },
        {
            'name': 'Strategy Lead',
            'role_type': 'strategist',
            'description': 'Plans and coordinates team efforts, sets priorities',
            'capabilities': ['planning', 'coordination', 'prioritization', 'resource_allocation'],
            'available_tools': [],
            'priority': 9,
            'role_prompt': 'You are a strategy lead coordinating team efforts for maximum impact.',
        },
        {
            'name': 'Optimization Specialist',
            'role_type': 'optimizer',
            'description': 'Improves and refines existing content and processes',
            'capabilities': ['optimization', 'a_b_testing', 'performance_improvement', 'iteration'],
            'available_tools': ['stability_ai', 'analytics_api'],
            'priority': 5,
            'role_prompt': 'You are an optimization specialist focused on continuous improvement.',
        },
        {
            'name': 'Communications Lead',
            'role_type': 'communicator',
            'description': 'Handles messaging, notifications, and team communications',
            'capabilities': ['messaging', 'notification_management', 'status_updates', 'reporting'],
            'available_tools': ['messaging_api'],
            'priority': 4,
            'role_prompt': 'You are a communications lead ensuring smooth information flow.',
        },
    ]

    created_count = 0
    for role_data in default_roles:
        role, created = AgentRole.objects.get_or_create(
            name=role_data['name'],
            defaults=role_data
        )
        if created:
            created_count += 1

    return created_count


# =============================================================================
# SESSION 228: WORKFLOW ENGINE API
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_workflow_templates(request):
    """
    GET /api/teams/workflows/templates/
    List all available workflow templates.
    """
    try:
        from core.team_workflow_engine import workflow_engine

        templates = workflow_engine.list_templates()

        return JsonResponse({
            'success': True,
            'templates': templates,
        })

    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def execute_workflow(request, workflow_id):
    """
    POST /api/teams/workflows/<workflow_id>/execute/
    Execute a workflow using the workflow engine.
    Initializes from template and starts execution.
    """
    try:
        from core.models_unified_system import TeamWorkflow
        from core.team_workflow_engine import workflow_engine

        workflow = TeamWorkflow.objects.get(id=workflow_id)

        # Initialize workflow from template
        workflow_engine.initialize_workflow(workflow)

        # Start the workflow
        result = workflow_engine.start_workflow(workflow)

        return JsonResponse({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'workflow': workflow_engine.get_workflow_status(workflow),
        })

    except TeamWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Workflow not found'}, status=404)
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def execute_workflow_step(request, workflow_id, step_id):
    """
    POST /api/teams/workflows/<workflow_id>/steps/<step_id>/execute/
    Execute a specific workflow step.
    """
    try:
        from core.models_unified_system import TeamWorkflow, TeamWorkflowStep
        from core.team_workflow_engine import workflow_engine

        workflow = TeamWorkflow.objects.get(id=workflow_id)
        step = TeamWorkflowStep.objects.get(id=step_id, workflow=workflow)

        data = json.loads(request.body) if request.body else {}

        result = workflow_engine.execute_step(step, data)

        return JsonResponse({
            'success': result.get('success', False),
            'result': result.get('result'),
            'error': result.get('error'),
            'workflow': workflow_engine.get_workflow_status(workflow),
        })

    except TeamWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Workflow not found'}, status=404)
    except TeamWorkflowStep.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Step not found'}, status=404)
    except Exception as e:
        logger.error(f"Error executing step: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def workflow_status(request, workflow_id):
    """
    GET /api/teams/workflows/<workflow_id>/status/
    Get detailed workflow status with step progress.
    """
    try:
        from core.models_unified_system import TeamWorkflow
        from core.team_workflow_engine import workflow_engine

        workflow = TeamWorkflow.objects.select_related('team').get(id=workflow_id)

        return JsonResponse({
            'success': True,
            'workflow': workflow_engine.get_workflow_status(workflow),
        })

    except TeamWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Workflow not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_full_workflow(request, workflow_id):
    """
    POST /api/teams/workflows/<workflow_id>/run/
    Execute entire workflow automatically (all steps).
    This runs all steps sequentially for demo/testing purposes.
    """
    try:
        from core.models_unified_system import TeamWorkflow
        from core.team_workflow_engine import workflow_engine

        workflow = TeamWorkflow.objects.get(id=workflow_id)

        # Initialize if needed
        if not workflow.step_executions.exists():
            workflow_engine.initialize_workflow(workflow)

        # Start the workflow
        start_result = workflow_engine.start_workflow(workflow)
        if not start_result.get('success'):
            return JsonResponse(start_result, status=400)

        # Execute all steps automatically
        executed_steps = []
        for step in workflow.step_executions.order_by('step_number'):
            # Skip if already completed
            if step.status == 'completed':
                continue

            # Execute step
            result = workflow_engine.execute_step(step)
            executed_steps.append({
                'step_name': step.step_name,
                'status': step.status,
                'success': result.get('success'),
            })

            # Stop if step failed
            if not result.get('success'):
                break

        # Get final status
        workflow.refresh_from_db()

        return JsonResponse({
            'success': workflow.status == 'completed',
            'message': f'Workflow {"completed" if workflow.status == "completed" else "in progress"}',
            'executed_steps': executed_steps,
            'workflow': workflow_engine.get_workflow_status(workflow),
        })

    except TeamWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Workflow not found'}, status=404)
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_active_workflows(request):
    """
    GET /api/teams/workflows/active/
    List all currently active workflows.
    """
    try:
        from core.models_unified_system import TeamWorkflow
        from core.team_workflow_engine import workflow_engine

        workflows = TeamWorkflow.objects.filter(
            status__in=['active', 'draft']
        ).select_related('team').order_by('-created_at')[:20]

        return JsonResponse({
            'success': True,
            'workflows': [
                workflow_engine.get_workflow_status(wf) for wf in workflows
            ],
            'total': workflows.count(),
        })

    except Exception as e:
        logger.error(f"Error listing active workflows: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
