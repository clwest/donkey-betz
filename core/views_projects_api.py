"""
Project Management API Views
Phase 3: Frontend Reality Fix - AI Production Hub

Provides REST API endpoints for project management in AI Production Hub.
These endpoints connect the frontend UI to real PartnershipProject data.

Created: September 30, 2025
"""

import logging
from django.db.models import Count, Avg
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from core.models_partnership import PartnershipProject
from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution

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

            # Session 520: Calculate overdue status
            from django.utils import timezone
            is_overdue = False
            if project.deadline and project.deadline < timezone.now() and project.status not in ['completed', 'archived']:
                is_overdue = True

            # Session 520: Return CreativeProject-compatible format for UI
            projects_data.append({
                'id': str(project.id),
                'name': project.project_name,  # UI expects 'name'
                'type': project.project_type,
                'status': project.status,
                'description': project.description[:200] if project.description else '',
                'goal': project.goal or project.description[:100] if project.description else '',  # Session 520: UI expects 'goal'
                'category': project.category or project.project_type.replace('_', ' ').title(),  # Session 520: UI expects 'category'
                'colors': project.colors,  # Session 520: UI expects 'colors'
                'tags': project.tags or [],  # Session 520: UI expects 'tags' as array
                'deadline': project.deadline.isoformat() if project.deadline else None,  # Session 520: UI expects 'deadline'
                'is_overdue': is_overdue,  # Session 520: UI expects 'is_overdue'
                'progress_percentage': project.total_workflows and int((project.completed_workflows / project.total_workflows) * 100) or 0,  # Session 520
                'total_workflows': project.total_workflows,  # Session 520: UI expects this
                'completed_workflows': project.completed_workflows,  # Session 520: UI expects this
                'is_shared': project.is_shared,
                'is_quick_starts': project.is_quick_starts,
                'metadata': project.metadata,  # Session 520: UI needs this for written_content display
                'learning_enabled': project.learning_enabled,  # Session 520: For learning toggle
                'learning_frequency': project.learning_frequency,
                'last_learning_run': project.last_learning_run.isoformat() if project.last_learning_run else None,
                'next_learning_run': project.next_learning_run.isoformat() if project.next_learning_run else None,
                'learning_topics': project.learning_topics or [],
                'learning_history': project.learning_history or [],
                # Legacy fields for backwards compatibility
                'progress': project.human_contribution_percent,
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

        # Session 520: Calculate overdue status
        from django.utils import timezone
        is_overdue = False
        if project.deadline and project.deadline < timezone.now() and project.status not in ['completed', 'archived']:
            is_overdue = True

        # Session 520: Return CreativeProject-compatible format for UI
        project_data = {
            'id': str(project.id),
            'name': project.project_name,  # UI expects 'name'
            'type': project.project_type,
            'status': project.status,
            'description': project.description,
            'goal': project.goal or project.description[:100] if project.description else '',  # Session 520: UI expects 'goal'
            'category': project.category or project.project_type.replace('_', ' ').title(),  # Session 520: UI expects 'category'
            'colors': project.colors,  # Session 520: UI expects 'colors'
            'tags': project.tags or [],  # Session 520: UI expects 'tags' as array
            'deadline': project.deadline.isoformat() if project.deadline else None,  # Session 520: UI expects 'deadline'
            'is_overdue': is_overdue,  # Session 520: UI expects 'is_overdue'
            'progress_percentage': project.total_workflows and int((project.completed_workflows / project.total_workflows) * 100) or 0,  # Session 520
            'total_workflows': project.total_workflows,  # Session 520: UI expects this
            'completed_workflows': project.completed_workflows,  # Session 520: UI expects this
            'is_shared': project.is_shared,
            'is_quick_starts': project.is_quick_starts,
            'metadata': project.metadata,  # Session 520: UI needs this for written_content display
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            # Legacy fields for backwards compatibility
            'progress': project.human_contribution_percent,
            'target_audience': project.project_type.replace('_', ' ').title(),
            'agents_used': agents_used,
            'key_features': key_features,
            'workflow_steps': project.workflow_steps,
            'ai_contributions': project.ai_contributions[:10] if project.ai_contributions else [],  # Last 10
            'human_contributions': project.human_contributions[:10] if project.human_contributions else [],  # Last 10
            'ai_contribution_percent': project.ai_contribution_percent,
            'human_contribution_percent': project.human_contribution_percent,
            'quality_score': project.quality_score,
            'deliverable_url': project.deliverable_url,
            'testable_components': {
                'is_complete': is_complete,
                'has_features': has_features,
                'feature_count': len(key_features),
                'agent_count': len(agents_used)
            },
            # Session 354: Project Learning Loop
            'learning_enabled': project.learning_enabled,
            'learning_frequency': project.learning_frequency,
            'learning_topics': project.learning_topics or [],
            'last_learning_run': project.last_learning_run.isoformat() if project.last_learning_run else None,
            'next_learning_run': project.next_learning_run.isoformat() if project.next_learning_run else None,
            'learning_history': project.learning_history or [],
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


# Session 520: Added update_project endpoint for PartnershipProject
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_project(request, project_id):
    """
    Update an existing project
    Session 520: Added to support PartnershipProject updates from UI

    PUT/PATCH /api/projects/<project_id>/update/
    """
    try:
        user = request.user
        project = PartnershipProject.objects.get(id=project_id, user=user)

        # Update fields if provided
        if 'name' in request.data:
            project.project_name = request.data['name'].strip()

        if 'description' in request.data:
            project.description = request.data['description'].strip()

        if 'goal' in request.data:
            project.goal = request.data['goal'].strip()

        if 'status' in request.data:
            status = request.data['status']
            valid_statuses = ['planning', 'in_progress', 'review', 'completed', 'archived', 'building']
            if status in valid_statuses:
                project.status = status

        if 'deadline' in request.data:
            from django.utils.dateparse import parse_datetime
            deadline_str = request.data['deadline']
            if deadline_str:
                project.deadline = parse_datetime(deadline_str)
            else:
                project.deadline = None

        if 'category' in request.data:
            project.category = request.data['category']

        if 'colors' in request.data:
            project.colors = request.data['colors']

        if 'tags' in request.data:
            project.tags = request.data['tags']

        project.save()

        logger.info(f"✅ Updated project: {project.project_name}")

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.project_name,
                'status': project.status,
                'goal': project.goal,
                'description': project.description,
                'category': project.category,
                'colors': project.colors,
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
            }
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error updating project: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# Session 520: Added delete_project endpoint for PartnershipProject
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request, project_id):
    """
    Delete a project
    Session 520: Added to support PartnershipProject deletion from UI

    DELETE /api/projects/<project_id>/delete/
    """
    try:
        user = request.user
        project = PartnershipProject.objects.get(id=project_id, user=user)

        project_name = project.project_name
        project.delete()

        logger.info(f"🗑️ Deleted project: {project_name}")

        return Response({
            'success': True,
            'message': f'Project "{project_name}" deleted successfully'
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error deleting project: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# Session 520: Added create_project endpoint for PartnershipProject
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    """
    Create a new project
    Session 520: Added to support PartnershipProject creation from UI

    POST /api/projects/create/
    """
    try:
        user = request.user

        name = request.data.get('name', '').strip()
        if not name:
            return Response({
                'success': False,
                'error': 'Project name is required'
            }, status=400)

        from django.utils.dateparse import parse_datetime

        project = PartnershipProject.objects.create(
            user=user,
            project_name=name,
            project_type=request.data.get('category', 'general'),
            description=request.data.get('description', ''),
            goal=request.data.get('goal', ''),
            status=request.data.get('status', 'planning'),
            category=request.data.get('category', ''),
            colors=request.data.get('colors', ''),
            tags=request.data.get('tags', []),
            deadline=parse_datetime(request.data['deadline']) if request.data.get('deadline') else None,
        )

        logger.info(f"✅ Created project: {project.project_name}")

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.project_name,
                'status': project.status,
                'goal': project.goal,
                'description': project.description,
                'category': project.category,
                'colors': project.colors,
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'created_at': project.created_at.isoformat(),
            }
        })

    except Exception as e:
        logger.error(f"❌ Error creating project: {e}")
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
    Session 324: Enhanced to include full research data (articles, sources, etc.)

    POST /api/projects/from-research/

    Body:
    {
        "project_name": "Coffee Shop Analysis",
        "research_summary": "Competitive analysis of the coffee shop market...",
        "research_type": "competitor_analysis" | "customer_research" | "business_research",
        "research_id": "uuid" (optional - links to BusinessResearchResult),
        "research_articles": [...] (optional - raw articles/data points)
    }

    Returns:
    {
        "success": true,
        "data": {
            "project_id": "uuid",
            "project_name": "Coffee Shop Analysis",
            "message": "Project created successfully with research data",
            "research_included": {
                "articles_count": 5,
                "sources": ["reddit", "youtube"]
            }
        }
    }
    """
    try:
        from core.models_unified_system import BusinessResearchResult

        user = request.user
        data = request.data

        project_name = data.get('project_name', 'Business Research')
        research_summary = data.get('research_summary', '')
        research_type = data.get('research_type', 'business_research')
        research_id = data.get('research_id')
        research_articles = data.get('research_articles', [])
        research_query = data.get('research_query', '')  # Session 325: Store original query

        # Session 324: Try to get full research data from BusinessResearchResult
        research_data = None
        sources_used = []
        articles_count = 0

        if research_id:
            try:
                research_data = BusinessResearchResult.objects.get(id=research_id)
                sources_used = research_data.sources_used or []
                articles_count = research_data.data_points_analyzed or len(research_data.raw_data or [])
                research_summary = research_data.analysis or research_summary
                research_articles = research_data.raw_data or []
                logger.info(f"📊 Found research result {research_id} with {articles_count} articles")
            except BusinessResearchResult.DoesNotExist:
                logger.warning(f"⚠️ Research result {research_id} not found")

        # If no research_id but we have recent research, try to find it
        if not research_data and not research_articles:
            from django.utils import timezone
            # Look for recent unlinked research that might match
            recent_research = BusinessResearchResult.objects.filter(
                project__isnull=True,
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).order_by('-created_at').first()

            if recent_research:
                research_data = recent_research
                sources_used = recent_research.sources_used or []
                articles_count = recent_research.data_points_analyzed or len(recent_research.raw_data or [])
                research_articles = recent_research.raw_data or []
                logger.info(f"📊 Found recent unlinked research with {articles_count} articles")

        # Build rich metadata for the project
        project_metadata = {
            'research_sources': sources_used,
            'research_articles': research_articles[:20],  # Store up to 20 articles
            'articles_count': articles_count or len(research_articles),
            'research_type': research_type,
            'created_from': 'business_research',
        }

        # Session 325: Store full analysis in research_summaries (NOT in description)
        # This keeps the analysis in its own expandable section, not filling the description form
        if research_summary:
            project_metadata['research_summaries'] = [{
                'type': research_type,
                'summary': research_summary,
                'query': research_query,
                'timestamp': datetime.now().isoformat(),
                'data_points': articles_count or len(research_articles),
                'sources': sources_used
            }]

        # Add structured findings if available
        if research_data:
            if research_data.pain_points:
                project_metadata['pain_points'] = research_data.pain_points
            if research_data.personas:
                project_metadata['personas'] = research_data.personas
            if research_data.quotes:
                project_metadata['quotes'] = research_data.quotes[:10]  # Top 10 quotes
            if research_data.recommendations:
                project_metadata['recommendations'] = research_data.recommendations

        # Create the project with full research data
        # Session 325: Description is just a short summary, NOT the full analysis
        # The full analysis is in metadata.research_summaries for the Analysis dropdown
        research_type_display = research_type.replace('_', ' ').title()
        short_description = f"{research_type_display} project. See Analysis section for full report."

        project = PartnershipProject.objects.create(
            user=user,
            project_name=project_name,
            project_type=research_type,
            description=short_description,
            status='in_progress',
            ai_contribution_percent=80,
            human_contribution_percent=20,
            metadata=project_metadata,  # Session 324: Store full research data
            ai_contributions=[{
                'agent': 'Business Research Agent',
                'task': f'{research_type.replace("_", " ").title()} analysis',
                'timestamp': datetime.now().isoformat(),
                'output': research_summary[:500] if research_summary else 'Research data saved',
                'articles_analyzed': articles_count,
                'sources': sources_used
            }],
            workflow_steps=[{
                'step': 'Research Analysis',
                'status': 'completed',
                'description': f'Analyzed {articles_count} articles from {len(sources_used)} sources' if articles_count else 'Initial research gathered'
            }]
        )

        # Session 324: Link the research result to this project
        if research_data:
            research_data.project = project
            research_data.save(update_fields=['project'])
            logger.info(f"🔗 Linked research result {research_data.id} to project {project.id}")

        logger.info(f"📁 Created project from research: {project_name} (ID: {project.id}) with {articles_count} articles")

        return Response({
            'success': True,
            'data': {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'message': f'Project "{project_name}" created successfully with {articles_count} research articles from {len(sources_used)} sources.' if articles_count else f'Project "{project_name}" created successfully with research data.',
                'research_included': {
                    'articles_count': articles_count,
                    'sources': sources_used
                }
            }
        })

    except Exception as e:
        logger.error(f"❌ Error creating project from research: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_research_to_project(request, project_id):
    """
    Add research data to an existing project.

    Session 324: Allows adding research from embedded assistant to current project.

    POST /api/projects/<project_id>/add-research/

    Body:
    {
        "research_type": "competitor_analysis" | "customer_research",
        "research_summary": "Analysis text...",
        "research_articles": [...],
        "research_query": "original query",
        "data_points_analyzed": 15,
        "sources_used": ["reddit", "hackernews"]
    }
    """
    try:
        user = request.user
        data = request.data

        # Get the project
        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Extract research data
        research_type = data.get('research_type', 'business_research')
        research_summary = data.get('research_summary', '')
        research_articles = data.get('research_articles', [])
        research_query = data.get('research_query', '')
        data_points = data.get('data_points_analyzed', len(research_articles))
        sources_used = data.get('sources_used', [])

        # Get existing metadata or initialize
        metadata = project.metadata or {}

        # Merge new research articles with existing (avoid duplicates by URL)
        existing_articles = metadata.get('research_articles', [])
        existing_urls = {a.get('url') for a in existing_articles if a.get('url')}

        new_articles = [a for a in research_articles if a.get('url') not in existing_urls]
        merged_articles = existing_articles + new_articles[:20]  # Cap at 20 total

        # Update metadata
        metadata['research_articles'] = merged_articles[:20]
        metadata['articles_count'] = len(merged_articles)

        # Merge sources
        existing_sources = set(metadata.get('research_sources', []))
        metadata['research_sources'] = list(existing_sources.union(set(sources_used)))

        # Add research type if not present
        if 'research_type' not in metadata:
            metadata['research_type'] = research_type

        # Store the latest query
        metadata['last_research_query'] = research_query

        # Session 325: Store the research summary/analysis for display
        if research_summary:
            existing_summaries = metadata.get('research_summaries', [])
            existing_summaries.append({
                'type': research_type,
                'summary': research_summary,
                'query': research_query,
                'timestamp': datetime.now().isoformat(),
                'data_points': data_points,
                'sources': sources_used
            })
            # Keep last 5 summaries
            metadata['research_summaries'] = existing_summaries[-5:]

        # Save project
        project.metadata = metadata
        project.save(update_fields=['metadata'])

        # Add to AI contributions
        ai_contributions = project.ai_contributions or []
        ai_contributions.append({
            'agent': f'{research_type.replace("_", " ").title()} Agent',
            'task': research_query or f'Added {research_type.replace("_", " ")}',
            'timestamp': datetime.now().isoformat(),
            'output': research_summary[:500] if research_summary else f'Added {len(new_articles)} articles',
            'articles_analyzed': data_points,
            'sources': sources_used
        })
        project.ai_contributions = ai_contributions
        project.save(update_fields=['ai_contributions'])

        logger.info(f"📊 Added {len(new_articles)} research articles to project {project.project_name}")

        # Session 328: Create BusinessResearchResult and convert to AgentKnowledgeSource
        # This enables the project's Learning tab to auto-populate
        knowledge_created = 0
        try:
            from core.models_unified_system import BusinessResearchResult
            from core.services.project_research_bridge import get_project_research_bridge

            # Create the research result record - use correct field names
            # Map research_type to model choices
            type_map = {
                'competitor_analysis': 'competitor',
                'customer_research': 'customer',
                'market_research': 'market',
                'trend_analysis': 'trend',
            }
            model_research_type = type_map.get(research_type, 'market')

            research_result = BusinessResearchResult.objects.create(
                project=project,
                research_type=model_research_type,
                query=research_query or f"{project.project_name} research",
                market_topic=f"{research_type.replace('_', ' ').title()}: {project.project_name}",
                agent_name=f"{research_type.replace('_', ' ').title()} Agent",
                analysis=research_summary[:5000] if research_summary else "Research analysis pending",
                data_points_analyzed=data_points,
                sources_used=sources_used,
                raw_data=research_articles[:10],  # Store top 10 articles
                recommendations=[a.get('summary', a.get('title', ''))[:200] for a in research_articles[:5] if a.get('summary') or a.get('title')],
            )

            # Immediately convert to knowledge (populates Learning tab)
            bridge = get_project_research_bridge()
            knowledge_entries = bridge.research_to_knowledge(research_result.id)
            knowledge_created = len(knowledge_entries)

            logger.info(f"🧠 Created {knowledge_created} knowledge entries from research for project {project.project_name}")

        except Exception as ke:
            logger.warning(f"⚠️ Could not auto-create knowledge from research: {ke}")

        return Response({
            'success': True,
            'message': f'Research added to project',
            'articles_added': len(new_articles),
            'total_articles': len(merged_articles),
            'knowledge_created': knowledge_created,
        })

    except Exception as e:
        logger.error(f"❌ Error adding research to project: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_research_pdf(request, project_id):
    """
    Export research analysis as PDF.

    Session 325: Generate downloadable PDF from research data.

    GET /api/projects/<project_id>/export-research-pdf/
    Query params:
        - index: Research summary index (default: -1 for latest)
    """
    from django.http import HttpResponse
    from core.services.research_pdf_service import ResearchPDFService

    try:
        user = request.user
        research_index = int(request.GET.get('index', -1))

        # Verify project ownership
        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Generate PDF
        service = ResearchPDFService()
        result = service.generate_research_pdf(str(project_id), research_index)

        if not result.success:
            return Response({
                'success': False,
                'error': result.error
            }, status=400)

        # Return PDF as download
        response = HttpResponse(result.pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{result.filename}"'

        logger.info(f"📄 Research PDF exported for project {project.project_name}")

        return response

    except Exception as e:
        logger.error(f"❌ Error exporting research PDF: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_comprehensive_pdf(request, project_id):
    """
    Export ALL research analysis as a single comprehensive PDF.

    Session 352: Generate downloadable PDF containing all research summaries
    (Trend Analysis, Competitor Analysis, Customer Research) in one document.

    GET /api/projects/<project_id>/export-comprehensive-pdf/
    """
    from django.http import HttpResponse
    from core.services.research_pdf_service import ResearchPDFService

    try:
        user = request.user

        # Verify project ownership
        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Generate comprehensive PDF
        service = ResearchPDFService()
        result = service.generate_comprehensive_pdf(str(project_id))

        if not result.success:
            return Response({
                'success': False,
                'error': result.error
            }, status=400)

        # Return PDF as download
        response = HttpResponse(result.pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{result.filename}"'

        logger.info(f"📄 Comprehensive research PDF exported for project {project.project_name}")

        return response

    except Exception as e:
        logger.error(f"❌ Error exporting comprehensive research PDF: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_creative_content_to_project(request, project_id):
    """
    Add creative content (images, videos, audio) to an existing project.

    Session 334: Allows adding AI-generated content from agents to current project.
    Mirrors the "Add to Project" flow from research agents.

    POST /api/projects/<project_id>/add-creative-content/

    Body:
    {
        "image_ids": ["uuid1", "uuid2"],
        "video_ids": ["uuid1"],
        "audio_ids": ["uuid1"],
        "content_description": "Generated logos for brand identity"
    }

    Returns:
    {
        "success": true,
        "message": "Added 3 images, 1 video to project",
        "data": {
            "images_added": 3,
            "videos_added": 1,
            "audio_added": 0,
            "total_content": 4
        }
    }
    """
    try:
        from content.models import ImageHistory, VideoHistory, AudioHistory

        user = request.user
        data = request.data

        # Get the project
        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Extract content IDs
        image_ids = data.get('image_ids', [])
        video_ids = data.get('video_ids', [])
        audio_ids = data.get('audio_ids', [])
        content_description = data.get('content_description', '')

        # Get existing metadata or initialize
        metadata = project.metadata or {}

        # Initialize content arrays if not present
        if 'creative_content' not in metadata:
            metadata['creative_content'] = {
                'images': [],
                'videos': [],
                'audio': []
            }

        # Track what we add
        images_added = 0
        videos_added = 0
        audio_added = 0
        content_details = []

        # Add images
        for img_id in image_ids:
            try:
                image = ImageHistory.objects.get(id=img_id, user=user)
                # Avoid duplicates
                existing_ids = [i.get('id') for i in metadata['creative_content']['images']]
                if str(img_id) not in existing_ids:
                    metadata['creative_content']['images'].append({
                        'id': str(image.id),
                        'url': image.url or image.signed_url or '',
                        'prompt': image.prompt or '',
                        'style': image.style or '',
                        'created_at': image.created_at.isoformat() if image.created_at else None,
                        'added_at': datetime.now().isoformat()
                    })
                    images_added += 1
                    content_details.append(f"Image: {(image.prompt or 'Untitled')[:50]}")
            except ImageHistory.DoesNotExist:
                logger.warning(f"⚠️ Image {img_id} not found")

        # Add videos
        for vid_id in video_ids:
            try:
                video = VideoHistory.objects.get(id=vid_id, user=user)
                existing_ids = [v.get('id') for v in metadata['creative_content']['videos']]
                if str(vid_id) not in existing_ids:
                    metadata['creative_content']['videos'].append({
                        'id': str(video.id),
                        'url': video.video_url or '',
                        'prompt': video.prompt or '',
                        'duration': video.duration_seconds or 0,
                        'created_at': video.created_at.isoformat() if video.created_at else None,
                        'added_at': datetime.now().isoformat()
                    })
                    videos_added += 1
                    content_details.append(f"Video: {(video.prompt or 'Untitled')[:50]}")
            except VideoHistory.DoesNotExist:
                logger.warning(f"⚠️ Video {vid_id} not found")

        # Add audio
        for aud_id in audio_ids:
            try:
                audio = AudioHistory.objects.get(id=aud_id, user=user)
                existing_ids = [a.get('id') for a in metadata['creative_content']['audio']]
                if str(aud_id) not in existing_ids:
                    metadata['creative_content']['audio'].append({
                        'id': str(audio.id),
                        'url': audio.audio_url or '',
                        'text': audio.text or '',
                        'voice': audio.voice_id or '',
                        'duration': audio.duration_seconds or 0,
                        'created_at': audio.created_at.isoformat() if audio.created_at else None,
                        'added_at': datetime.now().isoformat()
                    })
                    audio_added += 1
                    content_details.append(f"Audio: {(audio.text or 'Untitled')[:50]}")
            except AudioHistory.DoesNotExist:
                logger.warning(f"⚠️ Audio {aud_id} not found")

        # Save project metadata
        project.metadata = metadata
        project.save(update_fields=['metadata'])

        # Add to AI contributions
        total_added = images_added + videos_added + audio_added
        if total_added > 0:
            ai_contributions = project.ai_contributions or []
            ai_contributions.append({
                'agent': 'Creative Agent',
                'task': content_description or f'Added {total_added} creative assets',
                'timestamp': datetime.now().isoformat(),
                'output': f'Added {images_added} images, {videos_added} videos, {audio_added} audio files',
                'content_count': total_added,
                'content_details': content_details[:5]  # First 5 items
            })
            project.ai_contributions = ai_contributions
            project.save(update_fields=['ai_contributions'])

        # Build message
        parts = []
        if images_added:
            parts.append(f"{images_added} image{'s' if images_added > 1 else ''}")
        if videos_added:
            parts.append(f"{videos_added} video{'s' if videos_added > 1 else ''}")
        if audio_added:
            parts.append(f"{audio_added} audio file{'s' if audio_added > 1 else ''}")

        message = f"Added {', '.join(parts)} to project" if parts else "No content added"

        logger.info(f"🎨 Added {total_added} creative assets to project {project.project_name}")

        return Response({
            'success': True,
            'message': message,
            'data': {
                'images_added': images_added,
                'videos_added': videos_added,
                'audio_added': audio_added,
                'total_content': total_added,
                'project_id': str(project.id),
                'project_name': project.project_name
            }
        })

    except Exception as e:
        logger.error(f"❌ Error adding creative content to project: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project_from_creative_content(request):
    """
    Create a new project from AI-generated creative content.

    Session 334: Direct API endpoint for creating projects with creative assets.
    Mirrors create_project_from_research but for images/videos/audio.

    POST /api/projects/from-creative-content/

    Body:
    {
        "project_name": "Brand Identity Package",
        "image_ids": ["uuid1", "uuid2"],
        "video_ids": ["uuid1"],
        "audio_ids": [],
        "content_description": "Logo variations and brand video"
    }

    Returns:
    {
        "success": true,
        "data": {
            "project_id": "uuid",
            "project_name": "Brand Identity Package",
            "message": "Project created with 3 images, 1 video",
            "content_included": {
                "images": 3,
                "videos": 1,
                "audio": 0
            }
        }
    }
    """
    try:
        from content.models import ImageHistory, VideoHistory, AudioHistory

        user = request.user
        data = request.data

        project_name = data.get('project_name', 'Creative Project')
        image_ids = data.get('image_ids', [])
        video_ids = data.get('video_ids', [])
        audio_ids = data.get('audio_ids', [])
        content_description = data.get('content_description', '')

        # Gather content details for the project
        creative_content = {
            'images': [],
            'videos': [],
            'audio': []
        }

        content_types = []
        content_details = []

        # Process images
        for img_id in image_ids:
            try:
                image = ImageHistory.objects.get(id=img_id, user=user)
                creative_content['images'].append({
                    'id': str(image.id),
                    'url': image.url or image.signed_url or '',
                    'prompt': image.prompt or '',
                    'style': image.style or '',
                    'created_at': image.created_at.isoformat() if image.created_at else None,
                    'added_at': datetime.now().isoformat()
                })
                content_details.append(f"Image: {(image.prompt or 'Untitled')[:50]}")
            except ImageHistory.DoesNotExist:
                pass

        if creative_content['images']:
            content_types.append('images')

        # Process videos
        for vid_id in video_ids:
            try:
                video = VideoHistory.objects.get(id=vid_id, user=user)
                creative_content['videos'].append({
                    'id': str(video.id),
                    'url': video.video_url or '',
                    'prompt': video.prompt or '',
                    'duration': video.duration_seconds or 0,
                    'created_at': video.created_at.isoformat() if video.created_at else None,
                    'added_at': datetime.now().isoformat()
                })
                content_details.append(f"Video: {(video.prompt or 'Untitled')[:50]}")
            except VideoHistory.DoesNotExist:
                pass

        if creative_content['videos']:
            content_types.append('videos')

        # Process audio
        for aud_id in audio_ids:
            try:
                audio = AudioHistory.objects.get(id=aud_id, user=user)
                creative_content['audio'].append({
                    'id': str(audio.id),
                    'url': audio.audio_url or '',
                    'text': audio.text or '',
                    'voice': audio.voice_id or '',
                    'duration': audio.duration_seconds or 0,
                    'created_at': audio.created_at.isoformat() if audio.created_at else None,
                    'added_at': datetime.now().isoformat()
                })
                content_details.append(f"Audio: {(audio.text or 'Untitled')[:50]}")
            except AudioHistory.DoesNotExist:
                pass

        if creative_content['audio']:
            content_types.append('audio')

        # Determine project type based on content
        if len(creative_content['images']) > 0 and 'logo' in (content_description or project_name).lower():
            project_type = 'brand_identity'
        elif len(creative_content['videos']) > 0:
            project_type = 'video_production'
        elif len(creative_content['audio']) > 0:
            project_type = 'audio_production'
        else:
            project_type = 'content_creation'

        # Build project metadata
        total_content = (len(creative_content['images']) +
                         len(creative_content['videos']) +
                         len(creative_content['audio']))

        project_metadata = {
            'creative_content': creative_content,
            'content_types': content_types,
            'total_assets': total_content,
            'created_from': 'creative_content',
        }

        # Create the project
        short_description = content_description or f"Creative project with {total_content} assets ({', '.join(content_types)})"

        project = PartnershipProject.objects.create(
            user=user,
            project_name=project_name,
            project_type=project_type,
            description=short_description[:500],
            status='in_progress',
            ai_contribution_percent=90,
            human_contribution_percent=10,
            metadata=project_metadata,
            ai_contributions=[{
                'agent': 'Creative Agent',
                'task': content_description or 'Generated creative assets',
                'timestamp': datetime.now().isoformat(),
                'output': f'Created project with {len(creative_content["images"])} images, '
                          f'{len(creative_content["videos"])} videos, '
                          f'{len(creative_content["audio"])} audio files',
                'content_count': total_content,
                'content_details': content_details[:5]
            }],
            workflow_steps=[{
                'step': 'Creative Asset Generation',
                'status': 'completed',
                'description': f'Generated {total_content} creative assets'
            }]
        )

        # Build message
        parts = []
        if creative_content['images']:
            parts.append(f"{len(creative_content['images'])} image{'s' if len(creative_content['images']) > 1 else ''}")
        if creative_content['videos']:
            parts.append(f"{len(creative_content['videos'])} video{'s' if len(creative_content['videos']) > 1 else ''}")
        if creative_content['audio']:
            parts.append(f"{len(creative_content['audio'])} audio file{'s' if len(creative_content['audio']) > 1 else ''}")

        message = f'Project "{project_name}" created with {", ".join(parts)}.' if parts else f'Project "{project_name}" created.'

        logger.info(f"🎨 Created project from creative content: {project_name} (ID: {project.id}) with {total_content} assets")

        return Response({
            'success': True,
            'data': {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'message': message,
                'content_included': {
                    'images': len(creative_content['images']),
                    'videos': len(creative_content['videos']),
                    'audio': len(creative_content['audio'])
                }
            }
        })

    except Exception as e:
        logger.error(f"❌ Error creating project from creative content: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 335: LIVING PROJECT API
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_feed(request, project_id):
    """
    Get the insight feed for a living project.

    GET /api/projects/<project_id>/feed/

    Query params:
        - limit: Number of insights (default 20)
        - status: Filter by status (new, seen, acted_on, dismissed)
        - type: Filter by insight type (spider_data, agent_insight, decision, etc.)

    Returns:
    {
        "success": true,
        "data": {
            "insights": [...],
            "stats": {
                "total_insights": 42,
                "new_insights": 5,
                "avg_relevance": 0.78
            },
            "config": {
                "is_active": true,
                "watch_topics": ["AI", "podcasting"],
                "min_relevance_score": 0.6
            }
        }
    }
    """
    try:
        from core.services.living_project_service import get_living_project_service

        project = PartnershipProject.objects.get(id=project_id, user=request.user)
        living_service = get_living_project_service()

        # Get query params
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')
        type_filter = request.GET.get('type')

        # Get feed
        insights = living_service.get_project_feed(
            project,
            limit=limit,
            status_filter=status_filter,
            type_filter=type_filter
        )

        # Get stats
        stats = living_service.get_project_stats(project)

        # Get config
        config_data = None
        try:
            config = project.living_config
            config_data = {
                'is_active': config.is_active,
                'watch_topics': config.watch_topics,
                'watch_competitors': config.watch_competitors,
                'watch_keywords': config.watch_keywords,
                'min_relevance_score': config.min_relevance_score,
            }
        except Exception:
            # No config yet - return defaults
            topics = list(living_service.get_project_topics(project))
            config_data = {
                'is_active': False,
                'watch_topics': topics,
                'watch_competitors': [],
                'watch_keywords': [],
                'min_relevance_score': 0.6,
            }

        return Response({
            'success': True,
            'data': {
                'insights': insights,
                'stats': stats,
                'config': config_data
            }
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting project feed: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_living_project(request, project_id):
    """
    Activate a project as a living project.

    POST /api/projects/<project_id>/activate-living/

    Optional body:
    {
        "watch_topics": ["AI", "podcasting"],
        "watch_competitors": ["Competitor A"],
        "watch_keywords": ["keyword1"],
        "min_relevance_score": 0.6
    }

    Returns:
    {
        "success": true,
        "data": {
            "message": "Project activated as living project",
            "config": {...},
            "detected_topics": ["topic1", "topic2"]
        }
    }
    """
    try:
        from core.services.living_project_service import get_living_project_service

        project = PartnershipProject.objects.get(id=project_id, user=request.user)
        living_service = get_living_project_service()

        # Activate the project
        config = living_service.activate_living_project(project)

        # Apply any custom settings from request
        data = request.data or {}
        if 'watch_topics' in data:
            config.watch_topics = list(set(config.watch_topics + data['watch_topics']))
        if 'watch_competitors' in data:
            config.watch_competitors = data['watch_competitors']
        if 'watch_keywords' in data:
            config.watch_keywords = data['watch_keywords']
        if 'min_relevance_score' in data:
            config.min_relevance_score = float(data['min_relevance_score'])
        config.save()

        logger.info(f"🟢 [LIVING] Activated project: {project.project_name}")

        return Response({
            'success': True,
            'data': {
                'message': f'Project "{project.project_name}" activated as living project',
                'config': {
                    'is_active': config.is_active,
                    'watch_topics': config.watch_topics,
                    'watch_competitors': config.watch_competitors,
                    'watch_keywords': config.watch_keywords,
                    'min_relevance_score': config.min_relevance_score,
                },
                'detected_topics': list(living_service.get_project_topics(project))
            }
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error activating living project: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_insight_status(request, project_id, insight_id):
    """
    Update the status of a project insight.

    POST /api/projects/<project_id>/insights/<insight_id>/status/

    Body:
    {
        "status": "seen" | "acted_on" | "dismissed" | "archived",
        "rating": 1-5,  # optional
        "notes": "User notes"  # optional
    }

    Returns:
    {
        "success": true,
        "data": {
            "insight_id": "uuid",
            "new_status": "acted_on"
        }
    }
    """
    try:
        from core.models_unified_system import ProjectInsight

        # Verify project belongs to user
        project = PartnershipProject.objects.get(id=project_id, user=request.user)

        # Get and update insight
        insight = ProjectInsight.objects.get(id=insight_id, project=project)

        data = request.data
        if 'status' in data:
            insight.status = data['status']
        if 'rating' in data:
            insight.user_rating = int(data['rating'])
        if 'notes' in data:
            insight.user_notes = data['notes']
        if 'is_pinned' in data:
            insight.is_pinned = bool(data['is_pinned'])

        insight.save()

        logger.info(f"📝 [LIVING] Updated insight {insight_id} to status: {insight.status}")

        return Response({
            'success': True,
            'data': {
                'insight_id': str(insight.id),
                'new_status': insight.status,
                'is_pinned': insight.is_pinned
            }
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except ProjectInsight.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Insight not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error updating insight status: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_living_config(request, project_id):
    """
    Update the living project configuration.

    POST /api/projects/<project_id>/living-config/

    Body:
    {
        "is_active": true,
        "watch_topics": ["AI", "podcasting"],
        "watch_competitors": ["Competitor A"],
        "watch_keywords": ["keyword1"],
        "min_relevance_score": 0.6
    }

    Returns:
    {
        "success": true,
        "data": {
            "config": {...}
        }
    }
    """
    try:
        from core.models_unified_system import LivingProjectConfig
        from core.services.living_project_service import get_living_project_service

        project = PartnershipProject.objects.get(id=project_id, user=request.user)
        living_service = get_living_project_service()

        # Get or create config
        config, created = LivingProjectConfig.objects.get_or_create(
            project=project,
            defaults={
                'watch_topics': list(living_service.get_project_topics(project))
            }
        )

        # Update fields
        data = request.data
        if 'is_active' in data:
            config.is_active = bool(data['is_active'])
        if 'watch_topics' in data:
            config.watch_topics = data['watch_topics']
        if 'watch_competitors' in data:
            config.watch_competitors = data['watch_competitors']
        if 'watch_keywords' in data:
            config.watch_keywords = data['watch_keywords']
        if 'min_relevance_score' in data:
            config.min_relevance_score = float(data['min_relevance_score'])

        config.save()

        logger.info(f"⚙️ [LIVING] Updated config for project: {project.project_name}")

        return Response({
            'success': True,
            'data': {
                'config': {
                    'is_active': config.is_active,
                    'watch_topics': config.watch_topics,
                    'watch_competitors': config.watch_competitors,
                    'watch_keywords': config.watch_keywords,
                    'min_relevance_score': config.min_relevance_score,
                }
            }
        })

    except PartnershipProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error updating living config: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# ==================== Session 353: Research → Creative Pipeline ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_brand_assets(request, project_id):
    """
    Generate a comprehensive brand asset pack from research.

    Session 353: Connects Research Pipeline to Creative Pipeline.
    Uses intelligent style selection from 78 available styles based on:
    - Brand personality detected in research
    - Industry vertical
    - Target audience demographics

    POST /api/projects/<project_id>/generate-brand-assets/

    Body:
    {
        "asset_types": ["logo", "social_media", "marketing", "mood_board"],
        "custom_styles": ["cyberpunk", "minimalist"],  // optional override
        "num_variations": 3
    }

    Returns:
    {
        "success": true,
        "data": {
            "total_assets": 12,
            "styles_used": ["minimalist", "digital_art", "vector"],
            "style_rationale": "Based on tech industry and professional tone...",
            "logos": [...],
            "social_media": [...],
            "marketing_materials": [...],
            "mood_board": [...]
        }
    }
    """
    try:
        from core.services.research_to_creative_pipeline import get_research_to_creative_pipeline

        user = request.user
        data = request.data

        # Verify project ownership
        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Get parameters
        asset_types = data.get('asset_types', ['logo', 'social_media', 'marketing'])
        custom_styles = data.get('custom_styles')
        num_variations = data.get('num_variations', 3)

        # Initialize pipeline connector
        pipeline = get_research_to_creative_pipeline(user=user)

        # Generate brand asset pack
        result = pipeline.generate_brand_asset_pack(
            project_id=str(project_id),
            asset_types=asset_types,
            custom_styles=custom_styles,
            num_variations=num_variations
        )

        if not result.success:
            return Response({
                'success': False,
                'error': result.error or 'Failed to generate brand assets'
            }, status=400)

        # Session 353: Save generated images to ImageHistory and link to project
        from content.models import ImageHistory
        saved_image_ids = []

        # Helper to save images from result
        def save_images_to_history(images_list, asset_type):
            """Save list of generated images to ImageHistory."""
            for item in images_list:
                if isinstance(item, dict) and 'images' in item:
                    for img in item['images']:
                        if isinstance(img, dict) and 'url' in img:
                            try:
                                # Create ImageHistory record
                                from core.services.workspace_resolver import get_active_workspace
                                image_record = ImageHistory.objects.create(
                                    user=user,
                                    project=project,
                                    prompt=img.get('prompt', f'{asset_type} for {project.project_name}'),
                                    style=img.get('style', 'custom'),
                                    image_url=img['url'],
                                    provider=img.get('provider', 'stability'),
                                    model_used=img.get('model', 'sd3-large'),
                                    width=int(img.get('size', '1024x1024').split('x')[0]) if img.get('size') else 1024,
                                    height=int(img.get('size', '1024x1024').split('x')[1]) if img.get('size') else 1024,
                                    metadata={
                                        'asset_type': asset_type,
                                        'brand_asset_pack': True,
                                        'generated_via': 'research_to_creative_pipeline'
                                    },
                                    workspace=get_active_workspace(user),
                                )
                                saved_image_ids.append(str(image_record.id))
                                logger.info(f"✅ Saved brand asset: {asset_type} ({image_record.id})")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to save image to history: {e}")

        # Save all asset types
        result_dict = result.to_dict()
        if result_dict.get('logos'):
            save_images_to_history(result_dict['logos'], 'logo')
        if result_dict.get('social_media'):
            save_images_to_history(result_dict['social_media'], 'social_media')
        if result_dict.get('marketing_materials'):
            save_images_to_history(result_dict['marketing_materials'], 'marketing')
        if result_dict.get('mood_board'):
            save_images_to_history(result_dict['mood_board'], 'mood_board')

        logger.info(f"💾 Saved {len(saved_image_ids)} images to project {project.project_name}")

        # Update project metadata with generated assets
        metadata = project.metadata or {}
        metadata['brand_assets_generated'] = True
        metadata['brand_asset_pack'] = {
            'styles_used': result.styles_used,
            'total_assets': result.total_assets,
            'saved_image_ids': saved_image_ids,
            'generated_at': datetime.now().isoformat()
        }
        project.metadata = metadata
        project.save(update_fields=['metadata'])

        # Add AI contribution
        ai_contributions = project.ai_contributions or []
        ai_contributions.append({
            'agent': 'Research→Creative Pipeline',
            'task': f'Generated {result.total_assets} brand assets using {len(result.styles_used)} styles',
            'timestamp': datetime.now().isoformat(),
            'output': result.style_rationale,
            'styles': result.styles_used[:5]
        })
        project.ai_contributions = ai_contributions
        project.save(update_fields=['ai_contributions'])

        logger.info(f"🎨 Generated {result.total_assets} brand assets for project {project.project_name}")

        return Response({
            'success': True,
            'data': result.to_dict()
        })

    except Exception as e:
        logger.error(f"❌ Error generating brand assets: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_brand_styles(request, project_id):
    """
    Analyze brand strategy research and recommend styles.

    Session 353: Preview which styles would be recommended before generating assets.

    GET /api/projects/<project_id>/analyze-brand-styles/

    Returns:
    {
        "success": true,
        "data": {
            "project_name": "My AI Startup",
            "personality_traits": ["innovative", "modern"],
            "industry": "ai",
            "target_audiences": ["entrepreneurs", "developers"],
            "recommended_styles": [
                {"style": "cyberpunk", "rationale": "...", "confidence": 0.9, "asset_type": "logo"},
                ...
            ],
            "style_rationale": "Based on innovative tech brand..."
        }
    }
    """
    try:
        from core.services.research_to_creative_pipeline import get_research_to_creative_pipeline

        user = request.user

        # Verify project ownership
        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Initialize pipeline connector
        pipeline = get_research_to_creative_pipeline(user=user)

        # Analyze brand strategy
        analysis = pipeline.analyze_brand_strategy(str(project_id))

        if analysis.get('error'):
            return Response({
                'success': False,
                'error': analysis['error']
            }, status=400)

        # Convert StyleRecommendation objects to dicts
        recommendations = []
        for rec in analysis.get('recommended_styles', []):
            if hasattr(rec, 'style'):
                recommendations.append({
                    'style': rec.style,
                    'rationale': rec.rationale,
                    'confidence': rec.confidence,
                    'asset_type': rec.asset_type
                })
            else:
                recommendations.append(rec)

        analysis['recommended_styles'] = recommendations

        logger.info(f"📊 Brand style analysis for {project.project_name}: {len(recommendations)} styles recommended")

        return Response({
            'success': True,
            'data': analysis
        })

    except Exception as e:
        logger.error(f"❌ Error analyzing brand styles: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_styles(request):
    """
    Get all available image styles grouped by category.

    Session 353: Returns the 78 available styles for style picker UI.

    GET /api/styles/available/

    Returns:
    {
        "success": true,
        "data": {
            "photography": ["photorealistic", "portrait", ...],
            "animation": ["anime", "pixar", "disney", ...],
            "artistic_movements": ["impressionist", "surreal", ...],
            ...
        }
    }
    """
    try:
        from core.services.research_to_creative_pipeline import get_research_to_creative_pipeline

        pipeline = get_research_to_creative_pipeline()
        styles = pipeline.get_available_styles()

        return Response({
            'success': True,
            'data': styles,
            'total_styles': sum(len(v) for v in styles.values())
        })

    except Exception as e:
        logger.error(f"❌ Error getting available styles: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 354: Project Learning Loop APIs
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_project_learning(request, project_id):
    """
    Enable/disable continuous learning for a project.

    Session 354: Projects can autonomously learn and track their domain over time.

    POST /api/projects/<project_id>/learning/toggle/

    Request Body:
    {
        "enabled": true,
        "frequency": "weekly",  // daily, weekly, biweekly, monthly
        "topics": ["coffee trends", "specialty drinks"]  // optional, auto-detected if empty
    }

    Returns:
    {
        "success": true,
        "learning_enabled": true,
        "learning_frequency": "weekly",
        "learning_topics": ["coffee trends"],
        "next_run": "2025-12-12T06:00:00Z"
    }
    """
    from django.utils import timezone
    from django.shortcuts import get_object_or_404
    from datetime import timedelta

    try:
        user = request.user
        project = get_object_or_404(PartnershipProject, id=project_id, user=user)

        enabled = request.data.get('enabled', False)
        frequency = request.data.get('frequency', 'weekly')
        topics = request.data.get('topics', [])

        # Validate frequency
        valid_frequencies = ['daily', 'weekly', 'biweekly', 'monthly']
        if frequency not in valid_frequencies:
            return Response({
                'success': False,
                'error': f'Invalid frequency. Must be one of: {valid_frequencies}'
            }, status=400)

        project.learning_enabled = enabled
        project.learning_frequency = frequency
        project.learning_topics = topics if topics else []

        if enabled and not project.next_learning_run:
            # Schedule first run based on frequency
            freq_map = {'daily': 1, 'weekly': 7, 'biweekly': 14, 'monthly': 30}
            days = freq_map.get(frequency, 7)
            project.next_learning_run = timezone.now() + timedelta(days=days)

        project.save()

        logger.info(f"🧠 Learning {'enabled' if enabled else 'disabled'} for project {project.project_name}")

        return Response({
            'success': True,
            'learning_enabled': project.learning_enabled,
            'learning_frequency': project.learning_frequency,
            'learning_topics': project.learning_topics,
            'next_run': project.next_learning_run.isoformat() if project.next_learning_run else None,
            'last_run': project.last_learning_run.isoformat() if project.last_learning_run else None
        })

    except Exception as e:
        logger.error(f"❌ Error toggling project learning: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_learning_status(request, project_id):
    """
    Get the learning status and history for a project.

    Session 354: View learning configuration and history.

    GET /api/projects/<project_id>/learning/status/

    Returns:
    {
        "success": true,
        "data": {
            "learning_enabled": true,
            "learning_frequency": "weekly",
            "learning_topics": ["coffee trends"],
            "last_run": "2025-12-05T06:00:00Z",
            "next_run": "2025-12-12T06:00:00Z",
            "history": [
                {
                    "date": "2025-12-05T06:00:00Z",
                    "findings_count": 15,
                    "new_trends": ["mushroom coffee", "oat milk"],
                    "deltas": {...}
                }
            ],
            "total_learning_runs": 5,
            "total_trends_discovered": 23
        }
    }
    """
    from django.shortcuts import get_object_or_404

    try:
        user = request.user
        project = get_object_or_404(PartnershipProject, id=project_id, user=user)

        # Calculate stats from history
        history = project.learning_history or []
        total_trends = sum(
            len(entry.get('new_trends', []))
            for entry in history
        )

        return Response({
            'success': True,
            'data': {
                'learning_enabled': project.learning_enabled,
                'learning_frequency': project.learning_frequency,
                'learning_topics': project.learning_topics,
                'last_run': project.last_learning_run.isoformat() if project.last_learning_run else None,
                'next_run': project.next_learning_run.isoformat() if project.next_learning_run else None,
                'history': history[-10:],  # Last 10 runs
                'total_learning_runs': len(history),
                'total_trends_discovered': total_trends
            }
        })

    except Exception as e:
        logger.error(f"❌ Error getting project learning status: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_project_learning(request, project_id):
    """
    Manually trigger a learning cycle for a project.

    Session 354: Run learning immediately instead of waiting for schedule.

    POST /api/projects/<project_id>/learning/trigger/

    Returns:
    {
        "success": true,
        "message": "Learning cycle queued",
        "task_id": "celery-task-id"
    }
    """
    from django.shortcuts import get_object_or_404

    try:
        user = request.user
        project = get_object_or_404(PartnershipProject, id=project_id, user=user)

        if not project.learning_enabled:
            return Response({
                'success': False,
                'error': 'Learning is not enabled for this project. Enable it first.'
            }, status=400)

        # Queue the learning task
        from core.tasks import run_single_project_learning
        result = run_single_project_learning.delay(str(project.id))

        logger.info(f"🧠 Manual learning cycle triggered for project {project.project_name}")

        return Response({
            'success': True,
            'message': 'Learning cycle queued',
            'task_id': result.id
        })

    except Exception as e:
        logger.error(f"❌ Error triggering project learning: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 521: Content Export API
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_written_content(request, project_id):
    """
    Export written content (blog posts, scripts, newsletters, etc.) from a project.

    Session 521: Download written content in various formats.

    POST /api/projects/<project_id>/export-content/

    Body:
    {
        "content_index": 0,           # Index of content in written_content array
        "format": "md"                # md, txt, docx, pdf
    }

    Returns: File download response
    """
    from django.http import HttpResponse
    from core.services.content_export import export_written_content as do_export

    try:
        user = request.user
        data = request.data

        content_index = int(data.get('content_index', 0))
        export_format = data.get('format', 'md').lower()

        # Validate format
        valid_formats = ['md', 'txt', 'docx', 'pdf']
        if export_format not in valid_formats:
            return Response({
                'success': False,
                'error': f'Invalid format. Must be one of: {valid_formats}'
            }, status=400)

        # Get project
        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Get written content from metadata
        metadata = project.metadata or {}
        written_content = metadata.get('written_content', [])

        if not written_content:
            return Response({
                'success': False,
                'error': 'No written content found in this project'
            }, status=404)

        if content_index >= len(written_content):
            return Response({
                'success': False,
                'error': f'Content index {content_index} out of range. Project has {len(written_content)} content items.'
            }, status=400)

        # Get the specific content
        content_item = written_content[content_index]
        content_type = content_item.get('content_type', 'blog_post')
        content_data = content_item.get('data', content_item)

        # Export the content
        file_bytes, filename, content_type_header = do_export(
            content_data=content_data,
            content_type=content_type,
            format=export_format
        )

        # Return file download
        response = HttpResponse(file_bytes, content_type=content_type_header)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        logger.info(f"📄 Exported written content from project {project.project_name} as {export_format}")

        return response

    except Exception as e:
        logger.error(f"❌ Error exporting written content: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_written_content(request, project_id):
    """
    Update written content (blog posts, scripts, newsletters, etc.) in a project.

    Session 521: Edit written content in-place.

    PATCH /api/projects/<project_id>/update-content/

    Body:
    {
        "content_index": 0,           # Index of content in written_content array
        "data": {
            "title": "New title",
            "meta_description": "...",
            "intro": "...",
            "sections": [{"header": "...", "content": "..."}],
            "conclusion": "...",
            "tags": ["tag1", "tag2"]
        }
    }

    Returns: Updated content data
    """
    try:
        user = request.user
        data = request.data

        content_index = int(data.get('content_index', 0))
        updated_data = data.get('data', {})

        if not updated_data:
            return Response({
                'success': False,
                'error': 'No data provided for update'
            }, status=400)

        # Get project
        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Get written content from metadata
        metadata = project.metadata or {}
        written_content = metadata.get('written_content', [])

        if not written_content:
            return Response({
                'success': False,
                'error': 'No written content found in this project'
            }, status=404)

        if content_index >= len(written_content):
            return Response({
                'success': False,
                'error': f'Content index {content_index} out of range. Project has {len(written_content)} content items.'
            }, status=400)

        # Update the content data
        content_item = written_content[content_index]

        # Ensure 'data' key exists
        if 'data' not in content_item:
            content_item['data'] = {}

        # Update fields that were provided
        for key in ['title', 'meta_description', 'intro', 'sections', 'conclusion', 'tags']:
            if key in updated_data:
                content_item['data'][key] = updated_data[key]

        # Also update top-level title if provided
        if 'title' in updated_data:
            content_item['title'] = updated_data['title']

        # Save back to project
        written_content[content_index] = content_item
        metadata['written_content'] = written_content
        project.metadata = metadata
        project.save()

        logger.info(f"✏️ Updated written content in project {project.project_name}")

        return Response({
            'success': True,
            'message': 'Content updated successfully',
            'content': content_item
        })

    except Exception as e:
        logger.error(f"❌ Error updating written content: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
