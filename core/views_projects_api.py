"""
Project Management API Views
Phase 3: Frontend Reality Fix - AI Production Hub

Provides REST API endpoints for project management in AI Production Hub.
These endpoints connect the frontend UI to real PartnershipProject data.

Created: September 30, 2025
"""

import logging
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
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
            # Look for recent unlinked research that might match
            recent_research = BusinessResearchResult.objects.filter(
                project__isnull=True,
                created_at__gte=datetime.now() - timedelta(hours=1)
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

        return Response({
            'success': True,
            'message': f'Research added to project',
            'articles_added': len(new_articles),
            'total_articles': len(merged_articles)
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
