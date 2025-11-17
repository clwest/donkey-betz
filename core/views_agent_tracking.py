"""
Agent Tracking API Views
Session 120: Track which agents contributed to which content

Provides REST API endpoints for querying agent contributions to projects.
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from content.models import CreativeProject
from agents.models import AgentContribution
from agents.services import AgentContributionService

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_agents(request, project_id):
    """
    Get all agents that contributed to a project with stats.

    GET /api/projects/{project_id}/agents/

    Returns:
    {
        "success": true,
        "data": {
            "agents": [
                {
                    "agent_id": "uuid",
                    "agent_name": "Creative Director Agent",
                    "agent_description": "...",
                    "contribution_count": 5,
                    "total_percentage": 500,
                    "avg_execution_time": 12.5,
                    "total_tokens": 15000,
                    "avg_rating": 4.5,
                    "type_breakdown": {
                        "generation": 3,
                        "editing": 2
                    }
                }
            ],
            "stats": {
                "total_contributions": 5,
                "unique_agents": 2,
                "total_tokens_used": 15000,
                "total_execution_time": 62.5,
                "average_rating": 4.5,
                "contribution_types": {
                    "generation": 3,
                    "editing": 2
                }
            }
        }
    }
    """
    try:
        project = get_object_or_404(CreativeProject, id=project_id, user=request.user)
        service = AgentContributionService()

        # Get agents and stats
        agents = service.get_project_agents(project)
        stats = service.get_contribution_stats(project)

        return Response({
            'success': True,
            'data': {
                'agents': agents,
                'stats': stats
            }
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting project agents: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_timeline(request, project_id):
    """
    Get chronological timeline of agent contributions.

    GET /api/projects/{project_id}/agents/timeline/
    Query params:
        - limit: int (default 50)

    Returns:
    {
        "success": true,
        "data": {
            "timeline": [
                {
                    "id": "contribution-uuid",
                    "timestamp": "2025-11-17T03:22:00Z",
                    "agent_name": "Creative Director Agent",
                    "agent_id": "agent-uuid",
                    "contribution_type": "generation",
                    "contribution_role": "Primary Creator",
                    "content_reference": {
                        "type": "image",
                        "id": "image-uuid",
                        "number": 1
                    },
                    "task_description": "Generated logo design",
                    "execution_time_seconds": 12.5,
                    "tokens_used": 3000,
                    "user_rating": 5,
                    "user_selected": true
                }
            ]
        }
    }
    """
    try:
        project = get_object_or_404(CreativeProject, id=project_id, user=request.user)
        service = AgentContributionService()

        # Get limit from query params
        limit = int(request.GET.get('limit', 50))

        # Get timeline
        timeline = service.get_agent_timeline(project, limit=limit)

        return Response({
            'success': True,
            'data': {
                'timeline': timeline
            }
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting agent timeline: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_contribution(request, contribution_id):
    """
    Rate an agent's contribution (1-5 stars).

    POST /api/agent-contributions/{contribution_id}/rate/
    Body: {"rating": 5}

    Returns:
    {
        "success": true,
        "data": {
            "contribution_id": "uuid",
            "rating": 5,
            "message": "Rating saved successfully"
        }
    }
    """
    try:
        # Verify contribution belongs to user's project
        contribution = get_object_or_404(AgentContribution, id=contribution_id)
        if contribution.project.user != request.user:
            return Response({
                'success': False,
                'error': 'Unauthorized'
            }, status=403)

        # Get rating from request
        rating = request.data.get('rating')
        if not rating:
            return Response({
                'success': False,
                'error': 'Rating is required'
            }, status=400)

        # Validate and save rating
        service = AgentContributionService()
        contribution = service.rate_contribution(contribution_id, int(rating))

        return Response({
            'success': True,
            'data': {
                'contribution_id': str(contribution.id),
                'rating': contribution.user_rating,
                'message': 'Rating saved successfully'
            }
        })

    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)
    except AgentContribution.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Contribution not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error rating contribution: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_contribution_selected(request, contribution_id):
    """
    Mark/unmark a contribution as selected/favorite.

    POST /api/agent-contributions/{contribution_id}/select/
    Body: {"selected": true}

    Returns:
    {
        "success": true,
        "data": {
            "contribution_id": "uuid",
            "selected": true,
            "message": "Selection saved successfully"
        }
    }
    """
    try:
        # Verify contribution belongs to user's project
        contribution = get_object_or_404(AgentContribution, id=contribution_id)
        if contribution.project.user != request.user:
            return Response({
                'success': False,
                'error': 'Unauthorized'
            }, status=403)

        # Get selected from request
        selected = request.data.get('selected', True)

        # Save selection
        service = AgentContributionService()
        contribution = service.mark_contribution_selected(
            contribution_id,
            selected=bool(selected)
        )

        return Response({
            'success': True,
            'data': {
                'contribution_id': str(contribution.id),
                'selected': contribution.user_selected,
                'message': 'Selection saved successfully'
            }
        })

    except AgentContribution.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Contribution not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error marking contribution: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
