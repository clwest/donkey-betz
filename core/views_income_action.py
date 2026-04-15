"""
Income Action API Views - Session 388
=====================================

API endpoints for the income action pipeline:
- Save opportunities from spider data
- Generate application materials
- Track application status
- Get statistics
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services.income_action_service import get_income_action_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def save_opportunity(request):
    """
    Save an opportunity from spider data.

    POST /api/income/save-opportunity/
    Body: {
        "title": "Job Title",
        "url": "https://...",
        "source": "reddit",
        "description": "...",
        "company": "Company Name",
        "location": "Remote",
        "category": "freelance"
    }
    """
    try:
        # Get or create anonymous user for demo
        user = _get_user(request)
        if not user:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

        data = json.loads(request.body) if request.body else {}

        if not data.get('title'):
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)

        service = get_income_action_service()
        result = service.save_opportunity(user, data)

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in save_opportunity: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_application(request):
    """
    Generate application materials (cover letter/proposal) for a saved opportunity.

    POST /api/income/generate-application/
    Body: {
        "opportunity_id": "uuid",
        "user_profile": {  // optional
            "skills": ["Python", "Django"],
            "experience_years": 5,
            "summary": "..."
        }
    }
    """
    try:
        user = _get_user(request)
        if not user:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

        data = json.loads(request.body) if request.body else {}

        opportunity_id = data.get('opportunity_id')
        if not opportunity_id:
            return JsonResponse({'success': False, 'error': 'opportunity_id is required'}, status=400)

        user_profile = data.get('user_profile')

        service = get_income_action_service()
        result = service.generate_application(opportunity_id, user_profile)

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in generate_application: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_status(request):
    """
    Update the status of a saved opportunity.

    POST /api/income/update-status/
    Body: {
        "opportunity_id": "uuid",
        "status": "applied",  // saved, materials_ready, applied, interview, accepted, rejected, no_response, withdrawn
        "notes": "Optional notes"
    }
    """
    try:
        user = _get_user(request)
        if not user:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

        data = json.loads(request.body) if request.body else {}

        opportunity_id = data.get('opportunity_id')
        new_status = data.get('status')
        notes = data.get('notes')

        if not opportunity_id or not new_status:
            return JsonResponse({'success': False, 'error': 'opportunity_id and status are required'}, status=400)

        service = get_income_action_service()
        result = service.update_status(opportunity_id, new_status, notes)

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in update_status: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_opportunities(request):
    """
    Get user's saved opportunities.

    GET /api/income/opportunities/?status=applied&limit=50
    """
    try:
        user = _get_user(request)
        if not user:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

        status_filter = request.GET.get('status')
        limit = int(request.GET.get('limit', 50))

        service = get_income_action_service()
        opportunities = service.get_user_opportunities(user, status_filter, limit)

        return JsonResponse({
            'success': True,
            'opportunities': opportunities,
            'count': len(opportunities)
        })

    except Exception as e:
        logger.error(f"Error in get_opportunities: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_statistics(request):
    """
    Get application statistics for the user.

    GET /api/income/statistics/
    """
    try:
        user = _get_user(request)
        if not user:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

        service = get_income_action_service()
        stats = service.get_statistics(user)

        return JsonResponse({
            'success': True,
            'statistics': stats
        })

    except Exception as e:
        logger.error(f"Error in get_statistics: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def quick_apply(request):
    """
    One-click save + generate materials flow.

    POST /api/income/quick-apply/
    Body: {
        "title": "Job Title",
        "url": "https://...",
        "source": "reddit",
        "description": "...",
        "company": "Company Name",
        "location": "Remote",
        "category": "freelance",
        "user_profile": {}  // optional
    }
    """
    try:
        user = _get_user(request)
        if not user:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

        data = json.loads(request.body) if request.body else {}

        if not data.get('title'):
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)

        service = get_income_action_service()

        # Step 1: Save the opportunity
        save_result = service.save_opportunity(user, data)

        if not save_result.get('success'):
            return JsonResponse(save_result)

        opportunity_id = save_result.get('opportunity_id')

        # Step 2: Generate application materials (if not duplicate)
        if not save_result.get('is_duplicate'):
            user_profile = data.get('user_profile')
            gen_result = service.generate_application(opportunity_id, user_profile)

            return JsonResponse({
                'success': True,
                'opportunity_id': opportunity_id,
                'message': 'Opportunity saved and application materials generated!',
                'cover_letter': gen_result.get('cover_letter'),
                'is_duplicate': False
            })
        else:
            return JsonResponse({
                'success': True,
                'opportunity_id': opportunity_id,
                'message': 'Opportunity already saved',
                'is_duplicate': True
            })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in quick_apply: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _get_user(request):
    """Get the authenticated user or create demo user."""
    if request.user.is_authenticated:
        return request.user

    # For demo/testing, use first superuser
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.filter(is_superuser=True).first()
    except Exception as _e:
        logger.warning(
            "views_income_action._get_user: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return None
