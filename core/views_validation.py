"""
Validation Queue API Endpoints
Session 470: Market Intelligence Architecture - Phase 3

API endpoints for Human-in-the-Loop validation workflow.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import json

from core.services.hitl_validation import get_hitl_validation_service

logger = logging.getLogger(__name__)
User = get_user_model()


@csrf_exempt
@require_http_methods(["GET"])
def validation_queue(request):
    """
    GET /api/validation/queue/

    List pending validation requests.

    Query params:
        - status: 'pending', 'assigned', or 'all' (default: 'all')
        - limit: Max items to return (default: 50, max: 200)

    Returns:
        List of validation requests with opportunity details
    """
    try:
        hitl_service = get_hitl_validation_service()

        # Get query params
        status = request.GET.get('status', 'all')
        limit = min(int(request.GET.get('limit', 50)), 200)

        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None

        # Get pending queue
        queue = hitl_service.get_pending_queue(
            user=user,
            status=status,
            limit=limit
        )

        return JsonResponse({
            'success': True,
            'count': len(queue),
            'queue': queue
        })

    except Exception as e:
        logger.error(f"Error getting validation queue: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validation_approve(request, validation_id):
    """
    POST /api/validation/{id}/approve/

    Approve a validation request.

    Body:
        - reasoning: Optional explanation for approval
        - reasoning_tags: Optional list of tags
        - override_score: Optional score override (requires reasoning)

    Returns:
        Decision result
    """
    try:
        hitl_service = get_hitl_validation_service()

        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        # Parse body
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = {}

        reasoning = body.get('reasoning', '')
        reasoning_tags = body.get('reasoning_tags', [])
        override_score = body.get('override_score')

        # Determine decision type
        decision = 'approve_with_changes' if override_score else 'approve'

        result = hitl_service.make_decision(
            validation_request_id=validation_id,
            decision=decision,
            user=request.user,
            override_score=override_score,
            reasoning=reasoning,
            reasoning_tags=reasoning_tags
        )

        if result.success:
            return JsonResponse({
                'success': True,
                'decision': result.decision,
                'validation_request_id': result.validation_request_id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error
            }, status=400)

    except Exception as e:
        logger.error(f"Error approving validation {validation_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validation_reject(request, validation_id):
    """
    POST /api/validation/{id}/reject/

    Reject a validation request.

    Body:
        - reasoning: Required explanation for rejection
        - reasoning_tags: Optional list of tags

    Returns:
        Decision result
    """
    try:
        hitl_service = get_hitl_validation_service()

        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        # Parse body
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = {}

        reasoning = body.get('reasoning', '')
        reasoning_tags = body.get('reasoning_tags', [])

        # Rejection should have reasoning
        if not reasoning:
            return JsonResponse({
                'success': False,
                'error': 'Reasoning is required for rejection'
            }, status=400)

        result = hitl_service.make_decision(
            validation_request_id=validation_id,
            decision='reject',
            user=request.user,
            reasoning=reasoning,
            reasoning_tags=reasoning_tags
        )

        if result.success:
            return JsonResponse({
                'success': True,
                'decision': result.decision,
                'validation_request_id': result.validation_request_id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error
            }, status=400)

    except Exception as e:
        logger.error(f"Error rejecting validation {validation_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validation_escalate(request, validation_id):
    """
    POST /api/validation/{id}/escalate/

    Escalate a validation request for higher-level review.

    Body:
        - reasoning: Required explanation for escalation

    Returns:
        Decision result
    """
    try:
        hitl_service = get_hitl_validation_service()

        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        # Parse body
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = {}

        reasoning = body.get('reasoning', '')

        if not reasoning:
            return JsonResponse({
                'success': False,
                'error': 'Reasoning is required for escalation'
            }, status=400)

        result = hitl_service.make_decision(
            validation_request_id=validation_id,
            decision='escalate',
            user=request.user,
            reasoning=reasoning,
            reasoning_tags=['escalated']
        )

        if result.success:
            return JsonResponse({
                'success': True,
                'decision': result.decision,
                'validation_request_id': result.validation_request_id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error
            }, status=400)

    except Exception as e:
        logger.error(f"Error escalating validation {validation_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validation_defer(request, validation_id):
    """
    POST /api/validation/{id}/defer/

    Defer a validation request for later review.

    Body:
        - reasoning: Optional explanation

    Returns:
        Decision result
    """
    try:
        hitl_service = get_hitl_validation_service()

        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        # Parse body
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = {}

        reasoning = body.get('reasoning', 'Deferred for later review')

        result = hitl_service.make_decision(
            validation_request_id=validation_id,
            decision='defer',
            user=request.user,
            reasoning=reasoning,
            reasoning_tags=['deferred']
        )

        if result.success:
            return JsonResponse({
                'success': True,
                'decision': result.decision,
                'validation_request_id': result.validation_request_id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error
            }, status=400)

    except Exception as e:
        logger.error(f"Error deferring validation {validation_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def validation_stats(request):
    """
    GET /api/validation/stats/

    Get validation statistics.

    Returns:
        Thresholds, queue status, decision counts, ML agreement rate
    """
    try:
        hitl_service = get_hitl_validation_service()

        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None

        stats = hitl_service.get_stats(user)

        return JsonResponse({
            'success': True,
            **stats
        })

    except Exception as e:
        logger.error(f"Error getting validation stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def validation_detail(request, validation_id):
    """
    GET /api/validation/{id}/

    Get details of a specific validation request.

    Returns:
        Full validation request details including opportunity and explanation
    """
    try:
        from core.models_unified_system import ValidationRequest

        try:
            req = ValidationRequest.objects.select_related(
                'opportunity', 'scoring_explanation', 'assigned_to'
            ).get(id=validation_id)
        except ValidationRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Validation request {validation_id} not found'
            }, status=404)

        # Build response
        data = {
            'id': str(req.id),
            'status': req.status,
            'ml_score': req.ml_score,
            'rule_score': req.rule_score,
            'hybrid_score': req.hybrid_score,
            'confidence': req.confidence,
            'priority': req.priority,
            'priority_label': req.get_priority_display(),
            'request_reason': req.request_reason,
            'request_source': req.request_source,
            'assigned_to': req.assigned_to.username if req.assigned_to else None,
            'assigned_at': req.assigned_at.isoformat() if req.assigned_at else None,
            'deadline': req.deadline.isoformat() if req.deadline else None,
            'escalate_after': req.escalate_after.isoformat() if req.escalate_after else None,
            'is_overdue': req.is_overdue,
            'needs_escalation': req.needs_escalation,
            'created_at': req.created_at.isoformat(),
            'completed_at': req.completed_at.isoformat() if req.completed_at else None,
            'opportunity': {
                'id': str(req.opportunity.id),
                'title': req.opportunity.title,
                'description': req.opportunity.description[:500] if req.opportunity.description else '',
                'category': req.opportunity.category,
                'source': req.opportunity.source,
                'url': req.opportunity.url,
            }
        }

        # Add scoring explanation if available
        if req.scoring_explanation:
            data['explanation'] = {
                'top_positive_features': req.scoring_explanation.top_positive_features,
                'top_negative_features': req.scoring_explanation.top_negative_features,
                'shap_values': req.scoring_explanation.shap_values[:10],  # Top 10
                'feature_names': req.scoring_explanation.feature_names[:10],
            }

        # Add decision if exists
        if hasattr(req, 'decision'):
            decision = req.decision
            data['decision'] = {
                'decision': decision.decision,
                'decided_by': decision.decided_by.username if decision.decided_by else 'auto',
                'override_score': decision.override_score,
                'reasoning': decision.reasoning,
                'reasoning_tags': decision.reasoning_tags,
                'agreement_with_ml': decision.agreement_with_ml,
                'decision_time_seconds': decision.decision_time_seconds,
                'created_at': decision.created_at.isoformat(),
            }

        return JsonResponse({
            'success': True,
            'validation': data
        })

    except Exception as e:
        logger.error(f"Error getting validation detail {validation_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validation_assign(request, validation_id):
    """
    POST /api/validation/{id}/assign/

    Assign a validation request to a user.

    Body:
        - user_id: ID of user to assign to (omit for self-assignment)

    Returns:
        Updated assignment info
    """
    try:
        from core.models_unified_system import ValidationRequest

        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        try:
            req = ValidationRequest.objects.get(id=validation_id)
        except ValidationRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Validation request {validation_id} not found'
            }, status=404)

        # Parse body
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = {}

        user_id = body.get('user_id')

        if user_id:
            # Assign to specified user (requires admin)
            if not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Admin access required to assign to other users'
                }, status=403)

            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'User {user_id} not found'
                }, status=404)
        else:
            # Self-assignment
            target_user = request.user

        # Perform assignment
        req.assign_to(target_user)

        return JsonResponse({
            'success': True,
            'validation_id': str(req.id),
            'assigned_to': target_user.username,
            'assigned_at': req.assigned_at.isoformat()
        })

    except Exception as e:
        logger.error(f"Error assigning validation {validation_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validation_unassign(request, validation_id):
    """
    POST /api/validation/{id}/unassign/

    Unassign a validation request.

    Returns:
        Updated status
    """
    try:
        from core.models_unified_system import ValidationRequest

        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        try:
            req = ValidationRequest.objects.get(id=validation_id)
        except ValidationRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Validation request {validation_id} not found'
            }, status=404)

        # Check permission
        if req.assigned_to != request.user and not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Can only unassign your own validations'
            }, status=403)

        # Unassign
        req.assigned_to = None
        req.assigned_at = None
        req.status = 'pending'
        req.save()

        return JsonResponse({
            'success': True,
            'validation_id': str(req.id),
            'status': 'pending'
        })

    except Exception as e:
        logger.error(f"Error unassigning validation {validation_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
