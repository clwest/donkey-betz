"""
Project Management API Views
Phase 3: Frontend Reality Fix - AI Production Hub

Provides REST API endpoints for project management in AI Production Hub.
These endpoints connect the frontend UI to real PartnershipProject data.

Created: September 30, 2025
"""

import logging
from django.db.models import Q, Count, Avg
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from core.models_partnership import PartnershipProject
from agents.models import UnifiedAgentTemplate, AgentExecution

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def projects_list(request):
    """
    List all projects for the authenticated user

    GET /api/projects/

    Returns:
    {
        "success": true,
        "data": {
            "projects": [
                {
                    "id": "project-uuid",
                    "name": "Project Name",
                    "type": "content_creation",
                    "status": "in_progress",
                    "progress": 65,
                    "description": "Project description",
                    "target_audience": "Developers",
                    "agents_used": ["Agent 1", "Agent 2"],
                    "files": 12,
                    "created_at": "2025-09-30T...",
                    "updated_at": "2025-09-30T...",
                    "ai_contribution": 45,
                    "human_contribution": 55
                }
            ],
            "total_count": 10,
            "stats": {
                "completed": 5,
                "in_progress": 3,
                "building": 2,
                "total_files": 120
            }
        }
    }
    """
    try:
        user = request.user

        # Get all projects for user
        projects = PartnershipProject.objects.filter(user=user).order_by('-updated_at')

        # Calculate stats
        total_count = projects.count()
        completed_count = projects.filter(status='completed').count()
        in_progress_count = projects.filter(status='in_progress').count()
        building_count = projects.filter(status='building').count()

        # Serialize projects
        projects_data = []
        total_files = 0

        for project in projects:
            # Extract agents from ai_contributions
            agents_used = []
            if project.ai_contributions:
                agents_used = list(set([
                    contrib.get('agent', 'Unknown Agent')
                    for contrib in project.ai_contributions
                ]))

            # Estimate file count from workflow steps or default
            file_count = len(project.workflow_steps) * 2 if project.workflow_steps else 5
            total_files += file_count

            projects_data.append({
                'id': str(project.id),
                'name': project.project_name,
                'type': project.project_type,
                'status': project.status,
                'progress': project.human_contribution_percent,
                'description': project.description[:200] if project.description else '',
                'target_audience': project.project_type.replace('_', ' ').title(),
                'agents_used': agents_used,
                'files': file_count,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'ai_contribution': project.ai_contribution_percent,
                'human_contribution': project.human_contribution_percent
            })

        logger.info(f"📋 Loaded {total_count} projects for {user.username}")

        return Response({
            'success': True,
            'data': {
                'projects': projects_data,
                'total_count': total_count,
                'stats': {
                    'completed': completed_count,
                    'in_progress': in_progress_count,
                    'building': building_count,
                    'total_files': total_files
                }
            }
        })

    except Exception as e:
        logger.error(f"❌ Error loading projects: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_detail(request, project_id):
    """
    Get detailed information about a specific project

    GET /api/projects/<project_id>/

    Returns:
    {
        "success": true,
        "data": {
            "project": {
                "id": "uuid",
                "name": "Project Name",
                "status": "in_progress",
                "progress": 65,
                "description": "Full description",
                "target_audience": "Developers",
                "agents_used": ["Agent 1", "Agent 2"],
                "key_features": ["Feature 1", "Feature 2"],
                "workflow_steps": [...],
                "ai_contributions": [...],
                "human_contributions": [...],
                "testable_components": {
                    "is_complete": true,
                    "has_features": true,
                    "feature_count": 5,
                    "agent_count": 3
                }
            }
        }
    }
    """
    try:
        user = request.user

        # Get project
        project = PartnershipProject.objects.get(id=project_id, user=user)

        # Extract agents from ai_contributions
        agents_used = []
        if project.ai_contributions:
            agents_used = list(set([
                contrib.get('agent', 'Unknown Agent')
                for contrib in project.ai_contributions
            ]))

        # Extract key features from workflow steps or deliverable
        key_features = []
        if project.workflow_steps:
            key_features = [
                step.get('step', 'Unnamed step')
                for step in project.workflow_steps[:5]
            ]
        elif project.deliverable_description:
            # Simple feature extraction from description
            features_text = project.deliverable_description.split('.')[:3]
            key_features = [f.strip() for f in features_text if f.strip()]

        # Testable components analysis
        is_complete = project.status == 'completed'
        has_features = len(key_features) > 0

        project_data = {
            'id': str(project.id),
            'name': project.project_name,
            'status': project.status,
            'progress': project.human_contribution_percent,
            'description': project.description,
            'target_audience': project.project_type.replace('_', ' ').title(),
            'agents_used': agents_used,
            'key_features': key_features,
            'workflow_steps': project.workflow_steps,
            'ai_contributions': project.ai_contributions[:10],  # Last 10
            'human_contributions': project.human_contributions[:10],  # Last 10
            'ai_contribution_percent': project.ai_contribution_percent,
            'human_contribution_percent': project.human_contribution_percent,
            'quality_score': project.quality_score,
            'deliverable_url': project.deliverable_url,
            'testable_components': {
                'is_complete': is_complete,
                'has_features': has_features,
                'feature_count': len(key_features),
                'agent_count': len(agents_used)
            }
        }

        logger.info(f"📄 Loaded project details: {project.project_name}")

        return Response({
            'success': True,
            'data': {
                'project': project_data
            }
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error loading project detail: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_agents(request, project_id):
    """
    Get available agents for a project

    GET /api/projects/<project_id>/agents/

    Query params:
    - mode: 'fix' or 'enhance' (default: 'enhance')

    Returns:
    {
        "success": true,
        "data": {
            "available_agents": [
                {
                    "id": "agent-uuid",
                    "name": "Agent Name",
                    "specialization": "backend_development",
                    "description": "Agent description",
                    "success_rate": 0.92,
                    "avg_execution_time": 45.5,
                    "total_executions": 120,
                    "is_active": true,
                    "recommended": true
                }
            ],
            "total_agent_registry": 151,
            "recommendation": "Based on your project type, we recommend..."
        }
    }
    """
    try:
        user = request.user
        mode = request.GET.get('mode', 'enhance')

        # Verify project exists and belongs to user
        project = PartnershipProject.objects.get(id=project_id, user=user)

        # Get all active agents
        agents = UnifiedAgentTemplate.objects.filter(is_active=True).annotate(
            execution_count=Count('executions'),
            avg_exec_time=Avg('executions__execution_time_seconds')
        ).order_by('-execution_count')

        # Recommend agents based on project type
        recommended_specializations = {
            'content_creation': ['content_creation', 'writing', 'marketing'],
            'data_analysis': ['data_analysis', 'research', 'analytics'],
            'research': ['research', 'data_analysis', 'content_creation'],
            'development': ['backend_development', 'frontend_development', 'full_stack'],
            'design': ['ui_design', 'branding', 'creative'],
            'consulting': ['advisory', 'strategy', 'business_analysis'],
            'writing': ['writing', 'content_creation', 'editing'],
            'marketing': ['marketing', 'social_media', 'seo'],
            'technical_writing': ['technical_writing', 'documentation', 'content_creation']
        }

        preferred_specs = recommended_specializations.get(
            project.project_type,
            ['general', 'advisory']
        )

        # Serialize agents
        agents_data = []
        for agent in agents[:20]:  # Top 20 agents
            # Calculate success rate
            total_execs = agent.execution_count or 0
            successful_execs = agent.executions.filter(status='completed').count()
            success_rate = successful_execs / total_execs if total_execs > 0 else 0.0

            # Check if recommended for this project type
            is_recommended = agent.specialization in preferred_specs

            agents_data.append({
                'id': str(agent.id),
                'name': agent.name,
                'specialization': agent.specialization,
                'description': agent.description[:150] if agent.description else 'No description',
                'success_rate': round(success_rate, 2),
                'avg_execution_time': round(float(agent.avg_exec_time or 0), 1),
                'total_executions': total_execs,
                'is_active': agent.is_active,
                'recommended': is_recommended
            })

        # Sort recommended agents first
        agents_data.sort(key=lambda x: (not x['recommended'], -x['success_rate']))

        total_registry = UnifiedAgentTemplate.objects.count()

        recommendation_text = f"Based on your {project.project_type.replace('_', ' ')} project, we recommend agents specialized in {', '.join(preferred_specs[:2])}."

        logger.info(f"🤖 Loaded {len(agents_data)} agents for project {project.project_name}")

        return Response({
            'success': True,
            'data': {
                'available_agents': agents_data,
                'total_agent_registry': total_registry,
                'recommendation': recommendation_text,
                'mode': mode
            }
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error loading agents: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_agent_to_project(request, project_id):
    """
    Assign an agent to work on a project

    POST /api/projects/<project_id>/assign-agent/

    Body:
    {
        "agent_id": "agent-uuid",
        "improvement_type": "fix" | "enhance",
        "task_description": "Optional task description"
    }

    Returns:
    {
        "success": true,
        "data": {
            "message": "Agent assigned successfully",
            "real_execution": true,
            "agent_registry_size": 151,
            "execution_details": {
                "agent_name": "Agent Name",
                "specialization": "backend_development",
                "estimated_time": 30,
                "verification": {
                    "using_real_agent": true,
                    "agent_id": "uuid",
                    "execution_created": true
                }
            }
        }
    }
    """
    try:
        user = request.user
        data = request.data

        agent_id = data.get('agent_id')
        improvement_type = data.get('improvement_type', 'enhance')
        task_description = data.get('task_description', '')

        if not agent_id:
            return Response({
                'success': False,
                'error': 'agent_id is required'
            }, status=400)

        # Verify project exists and belongs to user
        project = PartnershipProject.objects.get(id=project_id, user=user)

        # Verify agent exists
        agent = UnifiedAgentTemplate.objects.get(id=agent_id, is_active=True)

        # Create agent execution record
        execution = AgentExecution.objects.create(
            template=agent,
            user=user,
            execution_id=f"{agent.name}_{project_id}_{int(datetime.now().timestamp())}",
            task_description=f"{improvement_type.title()}: {task_description or 'Project enhancement'}",
            task_type=improvement_type,
            input_data={
                'project_id': str(project_id),
                'project_name': project.project_name,
                'improvement_type': improvement_type,
                'task_description': task_description
            },
            status='pending'
        )

        # Add to project's AI contributions
        contribution = {
            'agent': agent.name,
            'agent_id': str(agent.id),
            'task': f"{improvement_type.title()}: {task_description or 'Project enhancement'}",
            'timestamp': execution.created_at.isoformat(),
            'execution_id': str(execution.id),
            'time_saved': 0,  # Will be updated when execution completes
            'output': 'Execution in progress...'
        }

        if not project.ai_contributions:
            project.ai_contributions = []
        project.ai_contributions.append(contribution)
        project.save()

        # Calculate estimated time based on agent's average
        avg_time = AgentExecution.objects.filter(
            template=agent,
            status='completed'
        ).aggregate(Avg('execution_time_seconds'))

        estimated_time = int(avg_time['execution_time_seconds__avg'] or 30)

        logger.info(f"🤖 Assigned {agent.name} to project {project.project_name}")

        return Response({
            'success': True,
            'data': {
                'message': f'Agent {agent.name} assigned successfully',
                'real_execution': True,
                'agent_registry_size': UnifiedAgentTemplate.objects.count(),
                'execution_details': {
                    'agent_name': agent.name,
                    'specialization': agent.specialization,
                    'estimated_time': estimated_time,
                    'execution_id': str(execution.id),
                    'verification': {
                        'using_real_agent': True,
                        'agent_id': str(agent.id),
                        'execution_created': True,
                        'execution_status': 'pending'
                    }
                }
            }
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except UnifiedAgentTemplate.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Agent not found or inactive'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error assigning agent: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project_from_research(request):
    """
    Create a new project from business research data.

    Session 302: Direct API endpoint that bypasses GPT routing.
    This allows the Create Project button to work reliably without
    being misrouted to WorkflowAgent.

    POST /api/projects/from-research/

    Body:
    {
        "project_name": "Coffee Shop Analysis",
        "research_summary": "Competitive analysis of the coffee shop market...",
        "research_type": "competitor_analysis" | "customer_research" | "business_research"
    }

    Returns:
    {
        "success": true,
        "data": {
            "project_id": "uuid",
            "project_name": "Coffee Shop Analysis",
            "message": "Project created successfully with research data"
        }
    }
    """
    try:
        user = request.user
        data = request.data

        project_name = data.get('project_name', 'Business Research')
        research_summary = data.get('research_summary', '')
        research_type = data.get('research_type', 'business_research')

        # Create the project
        project = PartnershipProject.objects.create(
            user=user,
            project_name=project_name,
            project_type=research_type,
            description=research_summary or f"Business research project: {project_name}",
            status='in_progress',
            ai_contribution_percent=80,
            human_contribution_percent=20,
            ai_contributions=[{
                'agent': 'Business Research Agent',
                'task': f'{research_type.replace("_", " ").title()} analysis',
                'timestamp': datetime.now().isoformat(),
                'output': research_summary[:500] if research_summary else 'Research data saved'
            }],
            workflow_steps=[{
                'step': 'Research Analysis',
                'status': 'completed',
                'description': research_summary[:200] if research_summary else 'Initial research gathered'
            }]
        )

        logger.info(f"📁 Created project from research: {project_name} (ID: {project.id})")

        return Response({
            'success': True,
            'data': {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'message': f'Project "{project_name}" created successfully with research data. You can now continue adding research or create content for this project.'
            }
        })

    except Exception as e:
        logger.error(f"❌ Error creating project from research: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
