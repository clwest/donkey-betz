"""
Frontend Stub Endpoints - Session 745

Provides stub/placeholder endpoints for frontend pages that were created
before their backend implementations. These return sensible defaults so
the pages can load without errors.

TODO: Replace these stubs with real implementations as features are built.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


# =============================================================================
# BILLING / STRIPE STUBS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_plans(request):
    """GET /api/stripe/plans/ - Available subscription plans"""
    return Response({
        'plans': [
            {'id': 'free', 'name': 'Free', 'price': 0, 'interval': 'month', 'features': ['Basic access', '5 agent calls/day']},
            {'id': 'pro', 'name': 'Pro', 'price': 29, 'interval': 'month', 'features': ['Unlimited agents', 'Priority support', 'API access']},
            {'id': 'enterprise', 'name': 'Enterprise', 'price': 99, 'interval': 'month', 'features': ['Everything in Pro', 'Custom integrations', 'Dedicated support']},
        ]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_payment_methods(request):
    """GET /api/stripe/payment-methods/ - User's payment methods"""
    return Response({'payment_methods': [], 'default_payment_method': None})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_add_payment_method(request):
    """POST /api/stripe/payment-methods/ - Add payment method"""
    return Response({'success': True, 'message': 'Payment method added (stub)'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def stripe_remove_payment_method(request, payment_method_id):
    """DELETE /api/stripe/payment-methods/<id>/ - Remove payment method"""
    return Response({'success': True, 'message': 'Payment method removed (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_set_default_payment_method(request, payment_method_id):
    """POST /api/stripe/payment-methods/<id>/default/ - Set default"""
    return Response({'success': True, 'message': 'Default payment method set (stub)'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_invoices(request):
    """GET /api/stripe/invoices/ - User's invoices"""
    return Response({'invoices': [], 'has_more': False})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_invoice_detail(request, invoice_id):
    """GET /api/stripe/invoices/<id>/ - Invoice detail"""
    return Response({'error': 'Invoice not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_upcoming_invoice(request):
    """GET /api/stripe/upcoming-invoice/ - Preview next invoice"""
    return Response({'upcoming_invoice': None, 'message': 'No upcoming invoice'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_usage(request):
    """GET /api/stripe/usage/ - Current usage metrics"""
    return Response({
        'usage': {
            'agent_calls': 0,
            'api_requests': 0,
            'storage_mb': 0,
            'period_start': None,
            'period_end': None,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_subscribe(request):
    """POST /api/stripe/subscribe/ - Subscribe to a plan"""
    return Response({'success': True, 'message': 'Subscription created (stub)', 'subscription_id': None})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_cancel_subscription(request):
    """POST /api/stripe/cancel-subscription/ - Cancel subscription"""
    return Response({'success': True, 'message': 'Subscription cancelled (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_resume_subscription(request):
    """POST /api/stripe/resume-subscription/ - Resume cancelled subscription"""
    return Response({'success': True, 'message': 'Subscription resumed (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_billing_portal(request):
    """POST /api/stripe/billing-portal/ - Get Stripe billing portal URL"""
    return Response({'url': None, 'message': 'Billing portal not configured (stub)'})


# =============================================================================
# LEARNING JOURNEY STUBS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_journeys_list(request):
    """GET /api/learning/journeys/ - List user's learning journeys"""
    return Response({'journeys': [], 'total': 0})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_journeys_active(request):
    """GET /api/learning/journeys/active/ - Active journeys"""
    return Response({'journeys': [], 'total': 0})


@api_view(['GET'])
@permission_classes([AllowAny])
def learning_templates(request):
    """GET /api/learning/templates/ - Available journey templates"""
    return Response({
        'templates': [
            {'id': 'agent-basics', 'name': 'Agent Basics', 'description': 'Learn to work with AI agents', 'steps': 5, 'duration_hours': 2},
            {'id': 'content-creation', 'name': 'Content Creation', 'description': 'Master content generation', 'steps': 8, 'duration_hours': 4},
            {'id': 'automation', 'name': 'Workflow Automation', 'description': 'Automate your workflows', 'steps': 6, 'duration_hours': 3},
        ]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_achievements(request):
    """GET /api/learning/achievements/ - User's achievements"""
    return Response({'achievements': [], 'total_points': 0})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_journey_start(request):
    """POST /api/learning/journeys/start/ - Start a journey"""
    return Response({'success': True, 'journey_id': None, 'message': 'Journey started (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_journey_pause(request, journey_id):
    """POST /api/learning/journeys/<id>/pause/ - Pause journey"""
    return Response({'success': True, 'message': 'Journey paused (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_journey_resume(request, journey_id):
    """POST /api/learning/journeys/<id>/resume/ - Resume journey"""
    return Response({'success': True, 'message': 'Journey resumed (stub)'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_journey_analytics(request):
    """GET /api/learning/journeys/analytics/ - Learning analytics"""
    return Response({
        'total_completed': 0,
        'total_in_progress': 0,
        'total_points': 0,
        'streak_days': 0,
    })


# =============================================================================
# AUTONOMOUS SYSTEM STUBS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def autonomous_status(request):
    """GET /api/autonomous/status/ - System status"""
    return Response({
        'status': 'idle',
        'is_running': False,
        'last_run': None,
        'active_situations': 0,
        'pending_triggers': 0,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def autonomous_situations(request):
    """GET /api/autonomous/situations/ - List situations"""
    return Response({'situations': [], 'total': 0})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def autonomous_triggers(request):
    """GET /api/autonomous/triggers/ - List triggers"""
    return Response({'triggers': [], 'total': 0})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def autonomous_start(request):
    """POST /api/autonomous/start/ - Start autonomous system"""
    return Response({'success': True, 'message': 'Autonomous system started (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def autonomous_pause(request):
    """POST /api/autonomous/pause/ - Pause system"""
    return Response({'success': True, 'message': 'System paused (stub)'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def autonomous_analytics_summary(request):
    """GET /api/autonomous/analytics/summary/ - Analytics summary"""
    return Response({
        'total_executions': 0,
        'success_rate': 0,
        'avg_duration_seconds': 0,
        'situations_triggered': 0,
    })


# =============================================================================
# REASONING ENGINE STUBS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reasoning_dashboard(request):
    """GET /api/reasoning/dashboard/ - Dashboard overview"""
    return Response({
        'active_thoughts': 0,
        'pending_actions': 0,
        'resolved_concerns': 0,
        'total_reasoning_chains': 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reasoning_thoughts(request):
    """GET /api/reasoning/thoughts/ - List reasoning thoughts"""
    return Response({'thoughts': [], 'total': 0})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reasoning_actions(request):
    """GET /api/reasoning/actions/ - List actions"""
    return Response({'actions': [], 'total': 0})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reasoning_pending_actions(request):
    """GET /api/reasoning/pending-actions/ - Pending actions"""
    return Response({'actions': [], 'total': 0})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reasoning_concerns(request):
    """GET /api/reasoning/concerns/ - Active concerns"""
    return Response({'concerns': [], 'total': 0})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reasoning_approve_action(request, action_id):
    """POST /api/reasoning/actions/<id>/approve/ - Approve action"""
    return Response({'success': True, 'message': 'Action approved (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reasoning_reject_action(request, action_id):
    """POST /api/reasoning/actions/<id>/reject/ - Reject action"""
    return Response({'success': True, 'message': 'Action rejected (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reasoning_resolve_concern(request, concern_id):
    """POST /api/reasoning/concerns/<id>/resolve/ - Resolve concern"""
    return Response({'success': True, 'message': 'Concern resolved (stub)'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reasoning_trigger(request):
    """POST /api/reasoning/trigger/ - Trigger reasoning chain"""
    return Response({'success': True, 'chain_id': None, 'message': 'Reasoning triggered (stub)'})


# =============================================================================
# ANALYTICS STUBS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """GET /api/analytics/overview/ - Analytics overview"""
    return Response({
        'total_agents': 72,
        'total_executions': 0,
        'total_content_pieces': 0,
        'total_revenue': 0,
        'period': '30d',
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_summary(request):
    """GET /api/analytics/summary/ - Summary metrics"""
    period = request.GET.get('period', '30d')
    return Response({
        'period': period,
        'metrics': {
            'agent_calls': 0,
            'content_generated': 0,
            'spiders_run': 0,
            'collaborations': 0,
        },
        'trends': {
            'agent_calls_change': 0,
            'content_change': 0,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_reports_list(request):
    """GET /api/analytics/reports/ - List reports"""
    return Response({'reports': [], 'total': 0})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analytics_reports_generate(request):
    """POST /api/analytics/reports/generate/ - Generate report"""
    return Response({'success': True, 'report_id': None, 'message': 'Report generation started (stub)'})
