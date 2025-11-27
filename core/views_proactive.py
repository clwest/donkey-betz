"""
Proactive System API Views - Phase 6 of Creative Intelligence Empire
Endpoints for alerts, notifications, suggestions, and automations.

Session 234: Complete proactive system API implementation
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal

logger = logging.getLogger(__name__)


def get_user(request):
    """Get user from request or default for development."""
    if request.user.is_authenticated:
        return request.user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.first()


# ============================================================
# Dashboard & Overview
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def proactive_dashboard(request):
    """Get complete proactive system dashboard data."""
    from .proactive_engine import ProactiveSystem

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        proactive = ProactiveSystem(user)
        data = proactive.get_dashboard_data(user)

        return JsonResponse({
            'success': True,
            **data
        })
    except Exception as e:
        logger.error(f"Error getting proactive dashboard: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_proactive_check(request):
    """Manually trigger a proactive system check."""
    from .proactive_engine import ProactiveSystem

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        proactive = ProactiveSystem(user)
        results = proactive.run_proactive_check(user)

        return JsonResponse({
            'success': True,
            'results': results
        })
    except Exception as e:
        logger.error(f"Error running proactive check: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================
# Alerts API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_alerts(request):
    """List all alerts for the user."""
    from .models_unified_system import ProactiveAlert

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        alerts = ProactiveAlert.objects.filter(user=user).order_by('-is_active', '-trigger_count')

        return JsonResponse({
            'success': True,
            'count': alerts.count(),
            'alerts': [
                {
                    'id': str(a.id),
                    'name': a.name,
                    'description': a.description,
                    'alert_type': a.alert_type,
                    'metric_name': a.metric_name,
                    'condition': a.condition,
                    'threshold_value': float(a.threshold_value) if a.threshold_value else None,
                    'threshold_percent': float(a.threshold_percent) if a.threshold_percent else None,
                    'platform': a.platform.name if a.platform else None,
                    'check_frequency': a.check_frequency,
                    'cooldown_hours': a.cooldown_hours,
                    'is_active': a.is_active,
                    'trigger_count': a.trigger_count,
                    'last_triggered': a.last_triggered.isoformat() if a.last_triggered else None,
                    'notification_channels': a.notification_channels,
                    'created_at': a.created_at.isoformat(),
                }
                for a in alerts
            ]
        })
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_alert(request):
    """Create a new alert."""
    from .models_unified_system import ProactiveAlert, DistributionPlatform

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        data = json.loads(request.body) if request.body else {}

        # Validate required fields
        required = ['name', 'alert_type', 'metric_name', 'condition']
        for field in required:
            if field not in data:
                return JsonResponse({'success': False, 'error': f'Missing required field: {field}'}, status=400)

        # Get platform if specified
        platform = None
        if data.get('platform'):
            platform = DistributionPlatform.objects.filter(name=data['platform']).first()

        alert = ProactiveAlert.objects.create(
            user=user,
            name=data['name'],
            description=data.get('description', ''),
            alert_type=data['alert_type'],
            metric_name=data['metric_name'],
            condition=data['condition'],
            threshold_value=Decimal(str(data['threshold_value'])) if data.get('threshold_value') else None,
            threshold_percent=Decimal(str(data['threshold_percent'])) if data.get('threshold_percent') else None,
            platform=platform,
            content_type=data.get('content_type', ''),
            category=data.get('category', ''),
            check_frequency=data.get('check_frequency', 'daily'),
            cooldown_hours=data.get('cooldown_hours', 24),
            notification_channels=data.get('notification_channels', ['in_app']),
            auto_actions=data.get('auto_actions', []),
        )

        return JsonResponse({
            'success': True,
            'alert_id': str(alert.id),
            'message': f"Alert '{alert.name}' created successfully"
        })
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def alert_detail(request, alert_id):
    """Get, update, or delete a specific alert."""
    from .models_unified_system import ProactiveAlert

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        alert = ProactiveAlert.objects.get(id=alert_id, user=user)
    except ProactiveAlert.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alert not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'alert': {
                'id': str(alert.id),
                'name': alert.name,
                'description': alert.description,
                'alert_type': alert.alert_type,
                'metric_name': alert.metric_name,
                'condition': alert.condition,
                'threshold_value': float(alert.threshold_value) if alert.threshold_value else None,
                'threshold_percent': float(alert.threshold_percent) if alert.threshold_percent else None,
                'platform': alert.platform.name if alert.platform else None,
                'content_type': alert.content_type,
                'category': alert.category,
                'check_frequency': alert.check_frequency,
                'cooldown_hours': alert.cooldown_hours,
                'is_active': alert.is_active,
                'trigger_count': alert.trigger_count,
                'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None,
                'notification_channels': alert.notification_channels,
                'auto_actions': alert.auto_actions,
                'created_at': alert.created_at.isoformat(),
                'updated_at': alert.updated_at.isoformat(),
            }
        })

    elif request.method == 'PUT':
        data = json.loads(request.body) if request.body else {}

        # Update fields
        if 'name' in data:
            alert.name = data['name']
        if 'description' in data:
            alert.description = data['description']
        if 'threshold_value' in data:
            alert.threshold_value = Decimal(str(data['threshold_value'])) if data['threshold_value'] else None
        if 'threshold_percent' in data:
            alert.threshold_percent = Decimal(str(data['threshold_percent'])) if data['threshold_percent'] else None
        if 'is_active' in data:
            alert.is_active = data['is_active']
        if 'check_frequency' in data:
            alert.check_frequency = data['check_frequency']
        if 'cooldown_hours' in data:
            alert.cooldown_hours = data['cooldown_hours']
        if 'notification_channels' in data:
            alert.notification_channels = data['notification_channels']

        alert.save()

        return JsonResponse({
            'success': True,
            'message': f"Alert '{alert.name}' updated successfully"
        })

    elif request.method == 'DELETE':
        name = alert.name
        alert.delete()
        return JsonResponse({
            'success': True,
            'message': f"Alert '{name}' deleted successfully"
        })


@csrf_exempt
@require_http_methods(["POST"])
def toggle_alert(request, alert_id):
    """Toggle alert active status."""
    from .models_unified_system import ProactiveAlert

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        alert = ProactiveAlert.objects.get(id=alert_id, user=user)
        alert.is_active = not alert.is_active
        alert.save()

        return JsonResponse({
            'success': True,
            'alert_id': str(alert.id),
            'is_active': alert.is_active,
            'message': f"Alert '{alert.name}' {'activated' if alert.is_active else 'deactivated'}"
        })
    except ProactiveAlert.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alert not found'}, status=404)
    except Exception as e:
        logger.error(f"Error toggling alert: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_alerts(request):
    """Manually check all alerts."""
    from .proactive_engine import AlertEngine

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        engine = AlertEngine(user)
        triggered = engine.check_all_alerts(user)

        return JsonResponse({
            'success': True,
            'triggered_count': len(triggered),
            'triggered_alerts': triggered
        })
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================
# Notifications API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_notifications(request):
    """List notifications for the user."""
    from .models_unified_system import ProactiveNotification

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        # Parse query params
        unread_only = request.GET.get('unread', 'false').lower() == 'true'
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))

        notifications = ProactiveNotification.objects.filter(user=user)

        if unread_only:
            notifications = notifications.filter(is_read=False, is_dismissed=False)

        notifications = notifications.order_by('-created_at')[offset:offset + limit]

        # Get counts
        total = ProactiveNotification.objects.filter(user=user).count()
        unread = ProactiveNotification.objects.filter(user=user, is_read=False, is_dismissed=False).count()

        return JsonResponse({
            'success': True,
            'total': total,
            'unread_count': unread,
            'notifications': [
                {
                    'id': str(n.id),
                    'type': n.notification_type,
                    'priority': n.priority,
                    'title': n.title,
                    'message': n.message,
                    'icon': n.icon,
                    'action_url': n.action_url,
                    'action_label': n.action_label,
                    'quick_actions': n.quick_actions,
                    'is_read': n.is_read,
                    'is_dismissed': n.is_dismissed,
                    'is_acted_upon': n.is_acted_upon,
                    'created_at': n.created_at.isoformat(),
                    'read_at': n.read_at.isoformat() if n.read_at else None,
                }
                for n in notifications
            ]
        })
    except Exception as e:
        logger.error(f"Error listing notifications: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    from .models_unified_system import ProactiveNotification

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        notification = ProactiveNotification.objects.get(id=notification_id, user=user)
        notification.mark_read()

        return JsonResponse({
            'success': True,
            'notification_id': str(notification.id),
            'message': 'Notification marked as read'
        })
    except ProactiveNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
    except Exception as e:
        logger.error(f"Error marking notification read: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def dismiss_notification(request, notification_id):
    """Dismiss a notification."""
    from .models_unified_system import ProactiveNotification

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        notification = ProactiveNotification.objects.get(id=notification_id, user=user)
        notification.is_dismissed = True
        notification.dismissed_at = timezone.now()
        notification.save()

        return JsonResponse({
            'success': True,
            'notification_id': str(notification.id),
            'message': 'Notification dismissed'
        })
    except ProactiveNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
    except Exception as e:
        logger.error(f"Error dismissing notification: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    from .models_unified_system import ProactiveNotification

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        updated = ProactiveNotification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return JsonResponse({
            'success': True,
            'updated_count': updated,
            'message': f'Marked {updated} notifications as read'
        })
    except Exception as e:
        logger.error(f"Error marking all read: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def notification_preferences(request):
    """Get or update notification preferences."""
    from .models_unified_system import UserNotificationPreference

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        prefs, created = UserNotificationPreference.objects.get_or_create(user=user)

        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'preferences': {
                    'email_enabled': prefs.email_enabled,
                    'push_enabled': prefs.push_enabled,
                    'sms_enabled': prefs.sms_enabled,
                    'in_app_enabled': prefs.in_app_enabled,
                    'alert_notifications': prefs.alert_notifications,
                    'suggestion_notifications': prefs.suggestion_notifications,
                    'insight_notifications': prefs.insight_notifications,
                    'celebration_notifications': prefs.celebration_notifications,
                    'warning_notifications': prefs.warning_notifications,
                    'digest_frequency': prefs.digest_frequency,
                    'quiet_hours_enabled': prefs.quiet_hours_enabled,
                    'quiet_hours_start': str(prefs.quiet_hours_start) if prefs.quiet_hours_start else None,
                    'quiet_hours_end': str(prefs.quiet_hours_end) if prefs.quiet_hours_end else None,
                    'timezone': prefs.timezone,
                    'min_priority_email': prefs.min_priority_email,
                    'min_priority_push': prefs.min_priority_push,
                }
            })

        elif request.method == 'PUT':
            data = json.loads(request.body) if request.body else {}

            # Update boolean fields
            bool_fields = [
                'email_enabled', 'push_enabled', 'sms_enabled', 'in_app_enabled',
                'alert_notifications', 'suggestion_notifications', 'insight_notifications',
                'celebration_notifications', 'warning_notifications', 'quiet_hours_enabled'
            ]
            for field in bool_fields:
                if field in data:
                    setattr(prefs, field, data[field])

            # Update string fields
            if 'digest_frequency' in data:
                prefs.digest_frequency = data['digest_frequency']
            if 'timezone' in data:
                prefs.timezone = data['timezone']
            if 'min_priority_email' in data:
                prefs.min_priority_email = data['min_priority_email']
            if 'min_priority_push' in data:
                prefs.min_priority_push = data['min_priority_push']

            # Update time fields
            if 'quiet_hours_start' in data and data['quiet_hours_start']:
                from datetime import time
                parts = data['quiet_hours_start'].split(':')
                prefs.quiet_hours_start = time(int(parts[0]), int(parts[1]))
            if 'quiet_hours_end' in data and data['quiet_hours_end']:
                from datetime import time
                parts = data['quiet_hours_end'].split(':')
                prefs.quiet_hours_end = time(int(parts[0]), int(parts[1]))

            prefs.save()

            return JsonResponse({
                'success': True,
                'message': 'Preferences updated successfully'
            })

    except Exception as e:
        logger.error(f"Error with notification preferences: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================
# Suggestions API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_suggestions(request):
    """List smart suggestions for the user."""
    from .models_unified_system import SmartSuggestion

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        status_filter = request.GET.get('status', 'pending')
        limit = int(request.GET.get('limit', 20))

        suggestions = SmartSuggestion.objects.filter(user=user)

        if status_filter != 'all':
            suggestions = suggestions.filter(status=status_filter)

        suggestions = suggestions.filter(is_still_relevant=True).order_by(
            '-priority_score', '-confidence_score'
        )[:limit]

        return JsonResponse({
            'success': True,
            'count': suggestions.count(),
            'suggestions': [
                {
                    'id': str(s.id),
                    'type': s.suggestion_type,
                    'category': s.category,
                    'title': s.title,
                    'description': s.description,
                    'detailed_rationale': s.detailed_rationale,
                    'action_steps': s.action_steps,
                    'current_state': s.current_state,
                    'suggested_state': s.suggested_state,
                    'estimated_impact': s.estimated_impact,
                    'estimated_revenue_impact': float(s.estimated_revenue_impact) if s.estimated_revenue_impact else None,
                    'confidence_score': float(s.confidence_score),
                    'priority_score': s.priority_score,
                    'effort_level': s.effort_level,
                    'status': s.status,
                    'created_at': s.created_at.isoformat(),
                }
                for s in suggestions
            ]
        })
    except Exception as e:
        logger.error(f"Error listing suggestions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_suggestions(request):
    """Generate new suggestions for the user."""
    from .proactive_engine import SuggestionEngine

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        data = json.loads(request.body) if request.body else {}
        max_suggestions = data.get('max_suggestions', 10)

        engine = SuggestionEngine(user)
        suggestions = engine.generate_suggestions(user, max_suggestions=max_suggestions)

        return JsonResponse({
            'success': True,
            'generated_count': len(suggestions),
            'suggestions': suggestions
        })
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def suggestion_detail(request, suggestion_id):
    """Get suggestion detail or take action on it."""
    from .models_unified_system import SmartSuggestion

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        suggestion = SmartSuggestion.objects.get(id=suggestion_id, user=user)
    except SmartSuggestion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Suggestion not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'suggestion': {
                'id': str(suggestion.id),
                'type': suggestion.suggestion_type,
                'category': suggestion.category,
                'title': suggestion.title,
                'description': suggestion.description,
                'detailed_rationale': suggestion.detailed_rationale,
                'supporting_patterns': suggestion.supporting_patterns,
                'supporting_data': suggestion.supporting_data,
                'similar_successes': suggestion.similar_successes,
                'action_steps': suggestion.action_steps,
                'current_state': suggestion.current_state,
                'suggested_state': suggestion.suggested_state,
                'estimated_impact': suggestion.estimated_impact,
                'estimated_revenue_impact': float(suggestion.estimated_revenue_impact) if suggestion.estimated_revenue_impact else None,
                'confidence_score': float(suggestion.confidence_score),
                'priority_score': suggestion.priority_score,
                'effort_level': suggestion.effort_level,
                'status': suggestion.status,
                'user_feedback': suggestion.user_feedback,
                'implemented_at': suggestion.implemented_at.isoformat() if suggestion.implemented_at else None,
                'actual_impact': suggestion.actual_impact,
                'created_at': suggestion.created_at.isoformat(),
            }
        })

    elif request.method == 'POST':
        data = json.loads(request.body) if request.body else {}
        action = data.get('action')

        if action == 'accept':
            suggestion.accept()
            message = 'Suggestion accepted'
        elif action == 'reject':
            reason = data.get('reason', '')
            suggestion.reject(reason)
            message = 'Suggestion rejected'
        elif action == 'implement':
            suggestion.mark_implemented()
            message = 'Suggestion marked as implemented'
        elif action == 'feedback':
            suggestion.user_feedback = data.get('feedback', '')
            suggestion.save()
            message = 'Feedback recorded'
        else:
            return JsonResponse({'success': False, 'error': f'Unknown action: {action}'}, status=400)

        return JsonResponse({
            'success': True,
            'suggestion_id': str(suggestion.id),
            'status': suggestion.status,
            'message': message
        })


# ============================================================
# Automations API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_automations(request):
    """List automated actions for the user."""
    from .models_unified_system import AutomatedAction

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        automations = AutomatedAction.objects.filter(user=user).order_by('-is_active', '-total_executions')

        return JsonResponse({
            'success': True,
            'count': automations.count(),
            'automations': [
                {
                    'id': str(a.id),
                    'name': a.name,
                    'description': a.description,
                    'action_type': a.action_type,
                    'trigger_type': a.trigger_type,
                    'trigger_schedule': a.trigger_schedule,
                    'action_params': a.action_params,
                    'conditions': a.conditions,
                    'is_active': a.is_active,
                    'is_paused': a.is_paused,
                    'pause_reason': a.pause_reason,
                    'total_executions': a.total_executions,
                    'successful_executions': a.successful_executions,
                    'failed_executions': a.failed_executions,
                    'success_rate': (a.successful_executions / a.total_executions * 100) if a.total_executions > 0 else 0,
                    'last_executed': a.last_executed.isoformat() if a.last_executed else None,
                    'created_at': a.created_at.isoformat(),
                }
                for a in automations
            ]
        })
    except Exception as e:
        logger.error(f"Error listing automations: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_automation(request):
    """Create a new automated action."""
    from .models_unified_system import AutomatedAction, ProactiveAlert

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        data = json.loads(request.body) if request.body else {}

        # Validate required fields
        required = ['name', 'action_type', 'trigger_type']
        for field in required:
            if field not in data:
                return JsonResponse({'success': False, 'error': f'Missing required field: {field}'}, status=400)

        # Get trigger alert if specified
        trigger_alert = None
        if data.get('trigger_alert_id'):
            trigger_alert = ProactiveAlert.objects.filter(
                id=data['trigger_alert_id'], user=user
            ).first()

        automation = AutomatedAction.objects.create(
            user=user,
            name=data['name'],
            description=data.get('description', ''),
            action_type=data['action_type'],
            trigger_type=data['trigger_type'],
            trigger_alert=trigger_alert,
            trigger_schedule=data.get('trigger_schedule', ''),
            trigger_event=data.get('trigger_event', ''),
            action_params=data.get('action_params', {}),
            conditions=data.get('conditions', []),
            platform_scope=data.get('platform_scope', []),
            content_type_scope=data.get('content_type_scope', []),
            max_executions_per_day=data.get('max_executions_per_day', 10),
            max_price_change_percent=Decimal(str(data.get('max_price_change_percent', 25))),
            requires_confirmation=data.get('requires_confirmation', False),
            dry_run_first=data.get('dry_run_first', True),
        )

        return JsonResponse({
            'success': True,
            'automation_id': str(automation.id),
            'message': f"Automation '{automation.name}' created successfully"
        })
    except Exception as e:
        logger.error(f"Error creating automation: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def automation_detail(request, automation_id):
    """Get, update, or delete an automation."""
    from .models_unified_system import AutomatedAction

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        automation = AutomatedAction.objects.get(id=automation_id, user=user)
    except AutomatedAction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Automation not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'automation': {
                'id': str(automation.id),
                'name': automation.name,
                'description': automation.description,
                'action_type': automation.action_type,
                'trigger_type': automation.trigger_type,
                'trigger_alert_id': str(automation.trigger_alert.id) if automation.trigger_alert else None,
                'trigger_schedule': automation.trigger_schedule,
                'trigger_event': automation.trigger_event,
                'action_params': automation.action_params,
                'conditions': automation.conditions,
                'platform_scope': automation.platform_scope,
                'content_type_scope': automation.content_type_scope,
                'max_executions_per_day': automation.max_executions_per_day,
                'max_price_change_percent': float(automation.max_price_change_percent),
                'requires_confirmation': automation.requires_confirmation,
                'dry_run_first': automation.dry_run_first,
                'is_active': automation.is_active,
                'is_paused': automation.is_paused,
                'pause_reason': automation.pause_reason,
                'total_executions': automation.total_executions,
                'successful_executions': automation.successful_executions,
                'failed_executions': automation.failed_executions,
                'last_executed': automation.last_executed.isoformat() if automation.last_executed else None,
                'last_result': automation.last_result,
                'total_revenue_impact': float(automation.total_revenue_impact),
                'created_at': automation.created_at.isoformat(),
            }
        })

    elif request.method == 'PUT':
        data = json.loads(request.body) if request.body else {}

        # Update fields
        if 'name' in data:
            automation.name = data['name']
        if 'description' in data:
            automation.description = data['description']
        if 'action_params' in data:
            automation.action_params = data['action_params']
        if 'conditions' in data:
            automation.conditions = data['conditions']
        if 'is_active' in data:
            automation.is_active = data['is_active']
        if 'is_paused' in data:
            automation.is_paused = data['is_paused']
            automation.pause_reason = data.get('pause_reason', '')
        if 'max_executions_per_day' in data:
            automation.max_executions_per_day = data['max_executions_per_day']
        if 'max_price_change_percent' in data:
            automation.max_price_change_percent = Decimal(str(data['max_price_change_percent']))

        automation.save()

        return JsonResponse({
            'success': True,
            'message': f"Automation '{automation.name}' updated successfully"
        })

    elif request.method == 'DELETE':
        name = automation.name
        automation.delete()
        return JsonResponse({
            'success': True,
            'message': f"Automation '{name}' deleted successfully"
        })


@csrf_exempt
@require_http_methods(["POST"])
def execute_automation(request, automation_id):
    """Manually execute an automation."""
    from .models_unified_system import AutomatedAction
    from .proactive_engine import AutomationEngine

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        automation = AutomatedAction.objects.get(id=automation_id, user=user)

        data = json.loads(request.body) if request.body else {}
        context = data.get('context', {})

        engine = AutomationEngine(user)
        result = engine.execute_action(automation, context)

        return JsonResponse({
            'success': result.get('success', False),
            'automation_id': str(automation.id),
            'result': result
        })
    except AutomatedAction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Automation not found'}, status=404)
    except Exception as e:
        logger.error(f"Error executing automation: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_automation(request, automation_id):
    """Toggle automation active/paused status."""
    from .models_unified_system import AutomatedAction

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        automation = AutomatedAction.objects.get(id=automation_id, user=user)

        data = json.loads(request.body) if request.body else {}

        if 'pause' in data:
            automation.is_paused = data['pause']
            automation.pause_reason = data.get('reason', '')
        else:
            automation.is_active = not automation.is_active

        automation.save()

        return JsonResponse({
            'success': True,
            'automation_id': str(automation.id),
            'is_active': automation.is_active,
            'is_paused': automation.is_paused,
            'message': f"Automation '{automation.name}' updated"
        })
    except AutomatedAction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Automation not found'}, status=404)
    except Exception as e:
        logger.error(f"Error toggling automation: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def automation_logs(request, automation_id):
    """Get execution logs for an automation."""
    from .models_unified_system import AutomatedAction, AutomatedActionLog

    user = get_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'No user found'}, status=401)

    try:
        automation = AutomatedAction.objects.get(id=automation_id, user=user)
        limit = int(request.GET.get('limit', 50))

        logs = AutomatedActionLog.objects.filter(action=automation).order_by('-started_at')[:limit]

        return JsonResponse({
            'success': True,
            'automation_id': str(automation.id),
            'logs': [
                {
                    'id': str(log.id),
                    'trigger_type': log.trigger_type,
                    'trigger_source': log.trigger_source,
                    'status': log.status,
                    'error_message': log.error_message,
                    'items_affected': log.items_affected,
                    'revenue_impact': float(log.revenue_impact) if log.revenue_impact else None,
                    'started_at': log.started_at.isoformat(),
                    'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                    'duration_ms': log.duration_ms,
                    'can_rollback': log.can_rollback,
                    'was_rolled_back': log.was_rolled_back,
                }
                for log in logs
            ]
        })
    except AutomatedAction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Automation not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting automation logs: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
