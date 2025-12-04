"""
Business Ideas API - Entry Point for Autonomous Pipeline
=========================================================

Session 338: End-to-End Autonomous Business Idea Pipeline

This is THE entry point for the platform's core value proposition:
"I have a business idea" → Complete research → Business plan → Assets

Endpoints:
    POST /api/business-ideas/
        - Takes a raw business idea
        - Returns project with complete research

    GET /api/business-ideas/<id>/
        - Get status of a business idea research

    POST /api/business-ideas/<id>/generate-assets/
        - Trigger asset generation based on research

Usage:
    POST /api/business-ideas/
    {
        "idea": "AI-powered podcast platform",
        "constraints": {
            "budget": "$5k",
            "timeline": "3 months"
        }
    }

    Response:
    {
        "success": true,
        "project_id": "uuid",
        "business_plan": {...},
        "next_actions": [...],
        "phases_completed": [...]
    }
"""

import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from core.services.research_orchestrator import get_research_orchestrator
from core.services.creative_orchestrator import get_creative_orchestrator

logger = logging.getLogger(__name__)
User = get_user_model()


def get_user_from_request(request):
    """Get authenticated user or default user for development."""
    if request.user.is_authenticated:
        return request.user

    # For development: use first superuser or first user
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        return user
    except Exception:
        return None


@csrf_exempt
@require_http_methods(["POST"])
def create_business_idea(request):
    """
    Create a new business idea and run full research pipeline.

    POST /api/business-ideas/
    {
        "idea": "AI-powered podcast platform",
        "constraints": {
            "budget": "$5k",
            "timeline": "3 months"
        },
        "create_project": true  // optional, defaults to true
    }

    Returns:
    {
        "success": true,
        "project_id": "uuid",
        "business_idea": "...",
        "phases_completed": ["competitor_analysis", "customer_research", "brand_strategy", "synthesis"],
        "competitor_analysis": {...},
        "customer_research": {...},
        "brand_strategy": {...},
        "business_plan": {...},
        "next_actions": [...],
        "total_execution_time_ms": 45000
    }
    """
    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)

        # Validate required fields
        idea = data.get('idea', '').strip()
        if not idea:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: idea'
            }, status=400)

        if len(idea) < 10:
            return JsonResponse({
                'success': False,
                'error': 'Business idea must be at least 10 characters'
            }, status=400)

        # Get optional fields
        constraints = data.get('constraints', {})
        create_project = data.get('create_project', True)

        # Get user
        user = get_user_from_request(request)
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        logger.info(f"Starting business idea pipeline for: {idea[:50]}...")

        # Run the research orchestrator
        orchestrator = get_research_orchestrator(user=user)
        result = orchestrator.execute_full_research(
            business_idea=idea,
            constraints=constraints,
            create_project=create_project
        )

        # Return result
        return JsonResponse(result.to_dict())

    except Exception as e:
        logger.error(f"Business idea creation failed: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_business_idea(request, project_id):
    """
    Get the status and results of a business idea research.

    GET /api/business-ideas/<project_id>/

    Returns project with all research data.
    """
    try:
        from core.models_partnership import PartnershipProject

        user = get_user_from_request(request)
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Build response
        metadata = project.metadata or {}

        return JsonResponse({
            'success': True,
            'project_id': str(project.id),
            'project_name': project.project_name,
            'description': project.description,
            'status': project.status,
            'research_completed': metadata.get('research_completed', False),
            'phases_completed': metadata.get('phases_completed', []),
            'business_plan': metadata.get('business_plan', {}),
            'next_actions': metadata.get('next_actions', []),
            'research_time_ms': metadata.get('research_time_ms', 0),
            'created_at': project.created_at.isoformat(),
            'ai_contributions': project.ai_contributions,
        })

    except Exception as e:
        logger.error(f"Failed to get business idea: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_assets(request, project_id):
    """
    Generate assets (logo, thumbnails, etc.) based on completed research.

    POST /api/business-ideas/<project_id>/generate-assets/
    {
        "asset_types": ["logo", "thumbnail", "banner"]  // optional
    }

    Returns generated assets or task ID for async generation.
    """
    try:
        from core.models_partnership import PartnershipProject

        user = get_user_from_request(request)
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        try:
            project = PartnershipProject.objects.get(id=project_id, user=user)
        except PartnershipProject.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Check if research is complete
        metadata = project.metadata or {}
        if not metadata.get('research_completed'):
            return JsonResponse({
                'success': False,
                'error': 'Research not yet complete. Run research first.'
            }, status=400)

        # Parse request
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        asset_types = data.get('asset_types', ['logo'])

        # Session 339: Use CreativeOrchestrator for asset generation
        logger.info(f"Starting asset generation for project: {project_id}")

        orchestrator = get_creative_orchestrator(user=user)
        result = orchestrator.execute_asset_generation(
            project_id=str(project_id),
            asset_types=asset_types
        )

        return JsonResponse(result.to_dict())

    except Exception as e:
        logger.error(f"Asset generation failed: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_business_ideas(request):
    """
    List all business idea projects for the user.

    GET /api/business-ideas/

    Returns list of projects with research status.
    """
    try:
        from core.models_partnership import PartnershipProject

        user = get_user_from_request(request)
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        # Get projects created via research orchestrator
        projects = PartnershipProject.objects.filter(
            user=user,
            metadata__source='research_orchestrator'
        ).order_by('-created_at')[:20]

        items = []
        for project in projects:
            metadata = project.metadata or {}
            items.append({
                'project_id': str(project.id),
                'project_name': project.project_name,
                'status': project.status,
                'research_completed': metadata.get('research_completed', False),
                'phases_completed': metadata.get('phases_completed', []),
                'created_at': project.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'count': len(items),
            'items': items
        })

    except Exception as e:
        logger.error(f"Failed to list business ideas: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
