"""
Agent Deployment Views for AI Building Products Integration

This module provides API endpoints for the agent deployment system
integrated with the AI Building Products interface.
"""

# PARTIAL — Session 1113 review (Session 1111 PR-B/PR-E queue).
# Classification: built but not URL-mounted.
# Why: every view in this module is reachable only through
# `agents/urls_deployment.py`, which is itself never `include()`-d from
# any active URLConf. Module imports cleanly; routes are dark.
# Decision pending: same as `agents/urls_deployment.py`.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.db import models
from core.models.agents_registry import (
    UnifiedAgentTemplate,
    AgentOrchestration
)
from core.models import GeneratedProject
from agents.project_deployment import ProjectAgentDeploymentManager
from agents.universal_integration import UniversalAgentIntegrator


@csrf_exempt
@require_http_methods(["GET"])
def list_available_agents(request):
    """
    List all available agents with filtering and categorization
    """
    try:
        # Get filter parameters
        category = request.GET.get('category', 'all')
        specialization = request.GET.get('specialization')
        search = request.GET.get('search', '')

        # Base queryset
        agents = UnifiedAgentTemplate.objects.filter(is_active=True)

        # Apply filters
        if specialization:
            agents = agents.filter(specialization=specialization)

        if search:
            agents = agents.filter(
                models.Q(name__icontains=search) |
                models.Q(display_name__icontains=search) |
                models.Q(description__icontains=search)
            )

        # Convert to list with relevant fields
        agent_list = []
        for agent in agents[:200]:  # Limit to 200 for performance
            agent_list.append({
                'id': str(agent.id),
                'name': agent.name,
                'display_name': agent.display_name or agent.name,
                'specialization': agent.specialization,
                'description': agent.description[:200],  # Truncate description
                'capabilities': agent.capabilities[:5],  # First 5 capabilities
                'success_rate': agent.success_rate,
                'usage_count': agent.usage_count,
                'avg_rating': agent.avg_user_rating,
                'estimated_cost': float(agent.estimated_cost_per_execution),
                'domain_tags': agent.domain_tags
            })

        # Categorize agents
        categories = {}
        for agent in agent_list:
            spec = agent['specialization']
            if spec not in categories:
                categories[spec] = []
            categories[spec].append(agent)

        return JsonResponse({
            'success': True,
            'total_agents': len(agent_list),
            'agents': agent_list,
            'categories': categories,
            'specializations': list(categories.keys())
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_agent_recommendations(request):
    """
    Get agent recommendations for a specific project
    """
    try:
        project_id = request.GET.get('project_id')
        project_type = request.GET.get('project_type', 'ecommerce')
        limit = int(request.GET.get('limit', 10))

        if project_id:
            # Get existing project
            try:
                project = GeneratedProject.objects.get(id=project_id)
            except GeneratedProject.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Project not found'
                }, status=404)
        else:
            # Create temporary project for recommendations
            project = GeneratedProject(
                name=f"Temp {project_type} project",
                project_type=project_type,
                description=request.GET.get('description', f"A {project_type} project")
            )

        # Get recommendations
        integrator = UniversalAgentIntegrator()
        compatible_agents = integrator.discover_compatible_agents(project)

        # Format recommendations
        recommendations = []

        # Add perfect matches
        for item in compatible_agents.get('perfect_match', [])[:limit//2]:
            agent = item['agent']
            recommendations.append({
                'id': str(agent.id),
                'name': agent.name,
                'display_name': agent.display_name or agent.name,
                'specialization': agent.specialization,
                'score': item['score'],
                'reason': item['reason'],
                'category': 'perfect_match'
            })

        # Add highly relevant
        remaining = limit - len(recommendations)
        for item in compatible_agents.get('highly_relevant', [])[:remaining]:
            agent = item['agent']
            recommendations.append({
                'id': str(agent.id),
                'name': agent.name,
                'display_name': agent.display_name or agent.name,
                'specialization': agent.specialization,
                'score': item['score'],
                'reason': item['reason'],
                'category': 'highly_relevant'
            })

        return JsonResponse({
            'success': True,
            'project_type': project_type,
            'recommendations': recommendations,
            'total_compatible': sum(len(agents) for agents in compatible_agents.values())
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def deploy_agents_to_project(request):
    """
    Deploy selected agents to a project
    """
    try:
        data = json.loads(request.body or b"{}")
        project_id = data.get('project_id')
        agent_names = data.get('agents', [])
        deployment_strategy = data.get('strategy', 'sequential')
        ml_features = data.get('ml_features', [])

        # Get or create project
        if project_id:
            try:
                project = GeneratedProject.objects.get(id=project_id)
            except GeneratedProject.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Project not found'
                }, status=404)
        else:
            # Create new project
            project = GeneratedProject.objects.create(
                name=data.get('project_name', 'New AI Project'),
                project_type=data.get('project_type', 'general'),
                description=data.get('description', 'AI-generated project'),
                status='generating',
                user=request.user if request.user.is_authenticated else None
            )

        # Deploy agents
        manager = ProjectAgentDeploymentManager()

        # Handle ML features for e-commerce projects
        if project.project_type == 'ecommerce' and ml_features:
            result = manager.deploy_ml_agents_to_ecommerce(
                project=project,
                ml_features=ml_features
            )
            orchestration = result['orchestration']
        else:
            # General agent deployment
            orchestration = manager.assign_agents_to_project(
                project=project,
                agent_names=agent_names,
                deployment_strategy=deployment_strategy
            )

        # Update project status
        project.status = 'completed'
        project.save()

        return JsonResponse({
            'success': True,
            'project_id': str(project.id),
            'orchestration_id': str(orchestration.id),
            'agents_deployed': len(agent_names),
            'strategy': deployment_strategy,
            'ml_features': ml_features,
            'message': f"Successfully deployed {len(agent_names)} agents to project"
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_deployment_status(request):
    """
    Get the status of an agent deployment/orchestration
    """
    try:
        orchestration_id = request.GET.get('orchestration_id')

        if not orchestration_id:
            return JsonResponse({
                'success': False,
                'error': 'Orchestration ID required'
            }, status=400)

        try:
            orchestration = AgentOrchestration.objects.get(id=orchestration_id)
        except AgentOrchestration.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Orchestration not found'
            }, status=404)

        # Get execution details
        executions = []
        for execution in orchestration.agent_executions.all()[:20]:  # Limit for performance
            executions.append({
                'id': execution.execution_id,
                'agent': execution.template.name,
                'status': execution.status,
                'progress': execution.progress_percentage,
                'current_step': execution.current_step,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None
            })

        return JsonResponse({
            'success': True,
            'orchestration': {
                'id': str(orchestration.id),
                'name': orchestration.name,
                'status': orchestration.status,
                'progress': orchestration.progress_percentage,
                'current_agent_index': orchestration.current_agent_index,
                'total_agents': len(orchestration.agent_sequence),
                'execution_strategy': orchestration.execution_strategy
            },
            'executions': executions
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_integration_plan(request):
    """
    Create an integration plan for agents and project
    """
    try:
        data = json.loads(request.body or b"{}")
        project_id = data.get('project_id')
        selected_agents = data.get('agents', [])
        integration_goals = data.get('goals', [])

        # Get project
        try:
            project = GeneratedProject.objects.get(id=project_id)
        except GeneratedProject.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Create integration plan
        integrator = UniversalAgentIntegrator()
        plan = integrator.create_agent_integration_plan(
            project=project,
            selected_agents=selected_agents,
            integration_goals=integration_goals
        )

        return JsonResponse({
            'success': True,
            'plan': plan
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_project_agents(request):
    """
    Get all agents assigned to a project
    """
    try:
        project_id = request.GET.get('project_id')

        if not project_id:
            return JsonResponse({
                'success': False,
                'error': 'Project ID required'
            }, status=400)

        try:
            project = GeneratedProject.objects.get(id=project_id)
        except GeneratedProject.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Get assigned agents
        manager = ProjectAgentDeploymentManager()
        agents = manager.get_project_agents(project)

        agent_list = []
        for agent in agents:
            agent_list.append({
                'id': str(agent.id),
                'name': agent.name,
                'display_name': agent.display_name or agent.name,
                'specialization': agent.specialization,
                'status': 'active' if agent.is_active else 'inactive',
                'usage_count': agent.usage_count,
                'success_rate': agent.success_rate
            })

        return JsonResponse({
            'success': True,
            'project_id': str(project.id),
            'project_name': project.name,
            'agents': agent_list,
            'total_agents': len(agent_list)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def execute_agent_on_project(request):
    """
    Execute a specific agent on a project task
    """
    try:
        data = json.loads(request.body or b"{}")
        project_id = data.get('project_id')
        agent_name = data.get('agent_name')
        task_description = data.get('task_description')
        context = data.get('context', {})

        # Get project
        try:
            project = GeneratedProject.objects.get(id=project_id)
        except GeneratedProject.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Execute agent
        manager = ProjectAgentDeploymentManager()
        execution = manager.execute_agent_for_project(
            project=project,
            agent_name=agent_name,
            task_description=task_description,
            context=context
        )

        # Start execution (in real system this would trigger actual work)
        execution.start_execution()

        return JsonResponse({
            'success': True,
            'execution_id': execution.execution_id,
            'agent': agent_name,
            'status': execution.status,
            'message': f"Agent '{agent_name}' started execution"
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_agent_categories(request):
    """
    Get all agent categories and specializations
    """
    try:
        from agents.universal_integration import UniversalAgentCategories

        categories = []
        for category in UniversalAgentCategories:
            categories.append({
                'value': category.value,
                'name': category.name,
                'display': category.value.replace('-', ' ').title()
            })

        # Also get specializations from the database
        specializations = UnifiedAgentTemplate.objects.filter(
            is_active=True
        ).values_list('specialization', flat=True).distinct()

        return JsonResponse({
            'success': True,
            'categories': categories,
            'specializations': list(specializations),
            'total_categories': len(categories)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)