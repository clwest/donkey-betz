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
from django.contrib.auth import get_user_model

from core.services.research_orchestrator import get_research_orchestrator
from core.services.creative_orchestrator import get_creative_orchestrator

logger = logging.getLogger(__name__)
User = get_user_model()


def get_user_from_request(request):
    """Get authenticated user or default user for development."""
    if request.user.is_authenticated:
        return request.user

    # Session 343: For development, prefer 'admin' user specifically
    try:
        # Try to get 'admin' user first
        user = User.objects.filter(username='admin').first()
        if not user:
            # Fallback to any superuser
            user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        return user
    except Exception as _e:
        logger.warning(
            "views_business_ideas.get_user_from_request: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
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

        # Session 394: Extract brand choices from Human-in-the-Loop review
        brand_choices = data.get('brand_choices', {})

        # Session 339: Use CreativeOrchestrator for asset generation
        logger.info(f"Starting asset generation for project: {project_id}")
        if brand_choices:
            logger.info(f"Using user brand choices: style={brand_choices.get('style')}, "
                       f"palette={brand_choices.get('palette')}, logo={brand_choices.get('logoDirection')}")

        orchestrator = get_creative_orchestrator(user=user)
        result = orchestrator.execute_asset_generation(
            project_id=str(project_id),
            asset_types=asset_types,
            brand_choices=brand_choices
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


@csrf_exempt
@require_http_methods(["GET"])
def pipeline_stats(request):
    """
    Session 343: Get pipeline statistics for the Pipeline UI.

    GET /api/business-ideas/stats/

    Returns counts for today's completed pipelines (in local timezone MST).
    Optionally filters by authenticated user, or shows all if no auth.
    """
    try:
        from core.models_partnership import PartnershipProject
        from django.utils import timezone

        # Get today's start in local timezone (MST/America/Denver)
        now = timezone.localtime(timezone.now())
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Base queryset - filter by source
        base_qs = PartnershipProject.objects.filter(
            metadata__source='research_orchestrator'
        )

        # Try to get user from session/request for user-specific stats
        user = get_user_from_request(request)
        if user:
            base_qs = base_qs.filter(user=user)
            user_filter = user.username
        else:
            # No auth - show all projects (for demo/dev)
            user_filter = 'all'

        # Count projects created today
        completed_today = base_qs.filter(
            metadata__research_completed=True,
            created_at__gte=today_start
        ).count()

        # Total all-time
        total_completed = base_qs.filter(
            metadata__research_completed=True
        ).count()

        # Recent projects (last 5)
        recent_projects = base_qs.order_by('-created_at')[:5]

        recent = []
        for p in recent_projects:
            recent.append({
                'id': str(p.id),
                'name': p.project_name[:50],
                'status': p.status,
                'created_at': timezone.localtime(p.created_at).isoformat(),
                'has_research_summaries': 'research_summaries' in (p.metadata or {})
            })

        return JsonResponse({
            'success': True,
            'completed_today': completed_today,
            'total_completed': total_completed,
            'recent_projects': recent,
            'local_time': now.isoformat(),
            'timezone': str(timezone.get_current_timezone()),
            'user_filter': user_filter
        })

    except Exception as e:
        logger.error(f"Failed to get pipeline stats: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_brand_recommendations(request):
    """
    Session 394: Get brand style recommendations for a business idea.

    GET /api/brand-recommendations/?idea=AI-powered podcast platform

    Returns style options, color palettes, and logo directions based on
    detected industry.
    """
    try:
        from core.services.style_library import get_brand_recommendations

        idea = request.GET.get('idea', '')

        if not idea:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameter: idea'
            }, status=400)

        recommendations = get_brand_recommendations(idea)

        return JsonResponse({
            'success': True,
            **recommendations
        })

    except Exception as e:
        logger.error(f"Failed to get brand recommendations: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
