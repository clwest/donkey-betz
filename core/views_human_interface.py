"""
Human Interface Layer - API Views
=================================

Session 686: REST API endpoints for the Human Interface Layer.
Session 763: Added Mission Control execute endpoint.

Endpoints:
- GET  /api/human/attention/         - Get attention stream
- POST /api/human/attention/{id}/decide/  - Record decision
- POST /api/human/attention/{id}/defer/   - Defer item
- POST /api/human/attention/{id}/verify/  - Record verification outcome
- POST /api/human/attention/{id}/execute/ - Execute Mission Control action (Session 763)
- GET  /api/human/attention/stats/   - Get attention statistics
- GET  /api/human/control/           - Get system control state
- POST /api/human/control/pause/     - Pause an agent
- POST /api/human/control/resume/    - Resume an agent
- POST /api/human/control/quiet/     - Set quiet mode
- POST /api/human/control/review/    - Set review mode
- POST /api/human/control/threshold/ - Adjust ML threshold
- GET  /api/human/preferences/       - Get preferences
- PUT  /api/human/preferences/       - Update preferences
"""

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from dateutil.parser import parse as parse_datetime

from core.services.human_interface_service import get_human_interface_service

logger = logging.getLogger(__name__)

# S2785 Fold 4 decision-approve audit — staff-only gate for /api/human/*
# endpoints. Mirrors _platform_staff_only (S2784) + _governance_staff_only
# (S2780) per S2772 N16 Rigby-ratified contract: every governance endpoint
# MUST be @login_required AND staff-only.
_human_staff_only = user_passes_test(
    lambda u: u.is_authenticated and u.is_staff,
)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class AttentionStreamView(View):
    """Get the prioritized attention stream."""

    def get(self, request):
        """GET /api/human/attention/"""
        service = get_human_interface_service(request.user)

        # Parse query params
        limit = int(request.GET.get('limit', 20))
        urgency_filter = request.GET.getlist('urgency')
        status_filter = request.GET.getlist('status')

        items = service.get_attention_stream(
            limit=limit,
            urgency_filter=urgency_filter if urgency_filter else None,
            status_filter=status_filter if status_filter else None,
        )

        # Session 988: Include last_visited_at for "NEW" badge support
        from core.models.users.models import UserPreference
        last_visited_pref = UserPreference.objects.filter(
            user=request.user, key='boardroom_last_visited'
        ).first()
        last_visited_at = last_visited_pref.value if last_visited_pref else None

        return JsonResponse({
            'success': True,
            'items': items,
            'count': len(items),
            'last_visited_at': last_visited_at,
        })

    def post(self, request):
        """POST /api/human/attention/ — Session 988: Record boardroom visit timestamp."""
        from core.models.users.models import UserPreference
        UserPreference.objects.update_or_create(
            user=request.user, key='boardroom_last_visited',
            defaults={'value': timezone.now().isoformat()}
        )
        return JsonResponse({'success': True})


@method_decorator([login_required, _human_staff_only], name='dispatch')
class AttentionDetailView(View):
    """
    Session 843: Get detail for a single attention item.
    Used by DecisionDetailModal for inline viewing.
    """

    def get(self, request, item_id):
        """GET /api/human/attention/{id}/"""
        from core.models_human_interface import HumanAttentionItem

        try:
            item = HumanAttentionItem.objects.get(id=item_id, user=request.user)
        except HumanAttentionItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

        # Mark as viewed
        item.mark_viewed()

        return JsonResponse({
            'success': True,
            'item': {
                'id': str(item.id),
                'title': item.title,
                'summary': item.summary,
                'urgency': item.urgency,
                'status': item.status,
                'item_type': item.item_type,
                'source_type': item.source_type,
                'source_agent': item.source_agent,
                'source_id': item.source_id,
                'payload': item.payload,
                'priority_score': item.priority_score,
                'impact_estimate': item.impact_estimate,
                'ml_prediction': item.ml_prediction,
                'ml_confidence': item.ml_confidence,
                'ml_recommendation': item.ml_recommendation,
                'decision': item.decision,
                'decision_feedback': item.decision_feedback,
                'decision_confidence': item.decision_confidence,
                'decided_at': item.decided_at.isoformat() if item.decided_at else None,
                'human_overrode_ml': item.human_overrode_ml,
                'override_reason': item.override_reason,
                'deferred_until': item.deferred_until.isoformat() if item.deferred_until else None,
                'created_at': item.created_at.isoformat(),
                'viewed_at': item.viewed_at.isoformat() if item.viewed_at else None,
                'expires_at': item.expires_at.isoformat() if item.expires_at else None,
                'verification_outcome': item.verification_outcome,
                'verified_at': item.verified_at.isoformat() if item.verified_at else None,
                'verification_profit': item.verification_profit,
                'verification_notes': item.verification_notes,
            }
        })


@method_decorator([login_required, _human_staff_only], name='dispatch')
class AttentionStatsView(View):
    """Get attention statistics."""

    def get(self, request):
        """GET /api/human/attention/stats/"""
        service = get_human_interface_service(request.user)
        stats = service.get_attention_stats()

        return JsonResponse({
            'success': True,
            'stats': stats,
        })


@method_decorator([login_required, _human_staff_only], name='dispatch')
class AttentionDecideView(View):
    """Record a decision on an attention item."""

    def post(self, request, item_id):
        """POST /api/human/attention/{id}/decide/"""
        service = get_human_interface_service(request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        decision = data.get('decision')
        if not decision:
            return JsonResponse({'success': False, 'error': 'Decision required'}, status=400)

        feedback = data.get('feedback', '')
        confidence = data.get('confidence')

        result = service.record_decision(
            item_id=item_id,
            decision=decision,
            feedback=feedback,
            confidence=confidence,
        )

        status_code = 200 if result.get('success') else 404
        return JsonResponse(result, status=status_code)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class AttentionDeferView(View):
    """Defer an attention item."""

    def post(self, request, item_id):
        """POST /api/human/attention/{id}/defer/"""
        service = get_human_interface_service(request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        remind_at_str = data.get('remind_at')
        if not remind_at_str:
            return JsonResponse({'success': False, 'error': 'remind_at required'}, status=400)

        try:
            remind_at = parse_datetime(remind_at_str)
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid datetime format'}, status=400)

        result = service.defer_item(item_id=item_id, remind_at=remind_at)

        status_code = 200 if result.get('success') else 404
        return JsonResponse(result, status=status_code)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class AttentionVerifyView(View):
    """Record verification outcome for a watched attention item (Session 746)."""

    def post(self, request, item_id):
        """POST /api/human/attention/{id}/verify/"""
        from core.models_human_interface import HumanAttentionItem

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        outcome = data.get('outcome')
        if not outcome:
            return JsonResponse({'success': False, 'error': 'Outcome required'}, status=400)

        profit = data.get('profit')
        notes = data.get('notes', '')

        try:
            item = HumanAttentionItem.objects.get(id=item_id)
        except HumanAttentionItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

        # Only allow verifying items that are being watched
        if item.status != HumanAttentionItem.STATUS_WATCHING:
            return JsonResponse({
                'success': False,
                'error': f'Item is not in watching status (current: {item.status})'
            }, status=400)

        # Record the verification
        item.record_verification(outcome=outcome, profit=profit, notes=notes)

        return JsonResponse({
            'success': True,
            'message': 'Verification recorded',
            'item': {
                'id': str(item.id),
                'status': item.status,
                'verification_outcome': item.verification_outcome,
                'verification_profit': item.verification_profit,
                'verified_at': item.verified_at.isoformat() if item.verified_at else None,
            }
        })


@method_decorator([login_required, _human_staff_only], name='dispatch')
class AttentionExecuteActionView(View):
    """
    Session 763: Execute an action from Mission Control.

    Instead of just recording a decision, this endpoint actually executes
    the action (publish, set_alert, queue research, etc.).
    """

    def post(self, request, item_id):
        """POST /api/human/attention/{id}/execute/"""
        from core.models_human_interface import HumanAttentionItem
        from core.services.mission_control_executor import mission_control_executor

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        action = data.get('action')
        if not action:
            return JsonResponse({'success': False, 'error': 'Action required'}, status=400)

        feedback = data.get('feedback', '')
        extra_data = data.get('extra_data', {})

        try:
            item = HumanAttentionItem.objects.get(id=item_id)
        except HumanAttentionItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

        # Execute the action
        result = mission_control_executor.execute(
            action_id=action,
            attention_item=item,
            user=request.user,
            feedback=feedback,
            extra_data=extra_data
        )

        return JsonResponse({
            'success': result.status.value == 'success',
            'action': result.action_id,
            'status': result.status.value,
            'message': result.message,
            'data': result.data or {},
            'next_action': result.next_action,
        })


@method_decorator([login_required, _human_staff_only], name='dispatch')
class SystemControlView(View):
    """Get and manage system control state."""

    def get(self, request):
        """GET /api/human/control/"""
        service = get_human_interface_service(request.user)
        state = service.get_system_state()

        return JsonResponse({
            'success': True,
            'state': state,
        })


@method_decorator([login_required, _human_staff_only], name='dispatch')
class PauseAgentView(View):
    """Pause a specific agent."""

    def post(self, request):
        """POST /api/human/control/pause/"""
        service = get_human_interface_service(request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        agent_name = data.get('agent')
        if not agent_name:
            return JsonResponse({'success': False, 'error': 'Agent name required'}, status=400)

        reason = data.get('reason', '')
        result = service.pause_agent(agent_name, reason)

        return JsonResponse(result)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class ResumeAgentView(View):
    """Resume a specific agent."""

    def post(self, request):
        """POST /api/human/control/resume/"""
        service = get_human_interface_service(request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        agent_name = data.get('agent')
        if not agent_name:
            return JsonResponse({'success': False, 'error': 'Agent name required'}, status=400)

        reason = data.get('reason', '')
        result = service.resume_agent(agent_name, reason)

        return JsonResponse(result)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class QuietModeView(View):
    """Set quiet mode."""

    def post(self, request):
        """POST /api/human/control/quiet/"""
        service = get_human_interface_service(request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        enabled = data.get('enabled', True)
        duration_minutes = data.get('duration_minutes')

        result = service.set_quiet_mode(enabled, duration_minutes)

        return JsonResponse(result)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class ReviewModeView(View):
    """Set review mode."""

    def post(self, request):
        """POST /api/human/control/review/"""
        service = get_human_interface_service(request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        enabled = data.get('enabled', True)
        result = service.set_review_mode(enabled)

        return JsonResponse(result)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class MLThresholdView(View):
    """Adjust ML confidence threshold."""

    def post(self, request):
        """POST /api/human/control/threshold/"""
        service = get_human_interface_service(request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        threshold = data.get('threshold')
        if threshold is None:
            return JsonResponse({'success': False, 'error': 'Threshold required'}, status=400)

        result = service.adjust_ml_threshold(float(threshold))

        status_code = 200 if result.get('success') else 400
        return JsonResponse(result, status=status_code)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class PreferencesView(View):
    """Get and update user preferences."""

    def get(self, request):
        """GET /api/human/preferences/"""
        service = get_human_interface_service(request.user)
        prefs = service.get_preferences()

        return JsonResponse({
            'success': True,
            'preferences': prefs,
        })

    def put(self, request):
        """PUT /api/human/preferences/"""
        service = get_human_interface_service(request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        result = service.update_preferences(data)

        return JsonResponse(result)


@method_decorator([login_required, _human_staff_only], name='dispatch')
class BulkAttentionDecideView(View):
    """
    Session 942: Bulk decide multiple attention items at once.
    Supports deciding by specific IDs or by filter criteria.
    """

    def post(self, request):
        """POST /api/human/attention/bulk-decide/"""
        from core.models_human_interface import HumanAttentionItem

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        decision = data.get('decision')
        if not decision or decision not in ['approved', 'ignored', 'rejected']:
            return JsonResponse({
                'success': False,
                'error': 'Valid decision required (approved, ignored, rejected)'
            }, status=400)

        item_ids = data.get('item_ids', [])
        item_type = data.get('item_type')
        urgency = data.get('urgency')

        # Build query
        queryset = HumanAttentionItem.objects.filter(
            user=request.user,
            status='pending'
        )

        # Filter by IDs if provided
        if item_ids:
            queryset = queryset.filter(id__in=item_ids)
        else:
            # Or filter by type/urgency
            if item_type:
                queryset = queryset.filter(item_type=item_type)
            if urgency:
                queryset = queryset.filter(urgency=urgency)

        # Execute bulk update
        now = timezone.now()
        count = queryset.count()

        if count == 0:
            return JsonResponse({
                'success': True,
                'count': 0,
                'message': 'No matching items found'
            })

        # Update all matching items
        queryset.update(
            status=decision,
            decision=decision,
            handled_at=now
        )

        logger.info(f"[Session 942] Bulk decided {count} attention items as '{decision}' for user {request.user.id}")

        return JsonResponse({
            'success': True,
            'count': count,
            'decision': decision,
            'message': f'{count} items {decision}'
        })


# URL patterns for easy import
def get_human_interface_urls():
    """Return URL patterns for the Human Interface API."""
    from django.urls import path

    return [
        # Attention Stream
        path('api/human/attention/', AttentionStreamView.as_view(), name='human-attention'),
        path('api/human/attention/stats/', AttentionStatsView.as_view(), name='human-attention-stats'),
        # Session 942: Bulk decide endpoint
        path('api/human/attention/bulk-decide/', BulkAttentionDecideView.as_view(), name='human-attention-bulk-decide'),
        # Session 843: Detail endpoint for inline modal viewing
        path('api/human/attention/<uuid:item_id>/', AttentionDetailView.as_view(), name='human-attention-detail'),
        path('api/human/attention/<uuid:item_id>/decide/', AttentionDecideView.as_view(), name='human-attention-decide'),
        path('api/human/attention/<uuid:item_id>/defer/', AttentionDeferView.as_view(), name='human-attention-defer'),
        path('api/human/attention/<uuid:item_id>/verify/', AttentionVerifyView.as_view(), name='human-attention-verify'),
        path('api/human/attention/<uuid:item_id>/execute/', AttentionExecuteActionView.as_view(), name='human-attention-execute'),

        # Control Panel
        path('api/human/control/', SystemControlView.as_view(), name='human-control'),
        path('api/human/control/pause/', PauseAgentView.as_view(), name='human-control-pause'),
        path('api/human/control/resume/', ResumeAgentView.as_view(), name='human-control-resume'),
        path('api/human/control/quiet/', QuietModeView.as_view(), name='human-control-quiet'),
        path('api/human/control/review/', ReviewModeView.as_view(), name='human-control-review'),
        path('api/human/control/threshold/', MLThresholdView.as_view(), name='human-control-threshold'),

        # Preferences
        path('api/human/preferences/', PreferencesView.as_view(), name='human-preferences'),
    ]
