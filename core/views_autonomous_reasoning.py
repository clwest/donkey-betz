"""
Autonomous Reasoning Engine API Views

Session 544: API endpoints for viewing and controlling the ThinkingAgent.
"""

import logging
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from celery.result import AsyncResult

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def thoughts_api(request):
    """
    Get recent thought records from the Autonomous Reasoning Engine.

    Returns the latest thoughts with insights, patterns, and actions.
    """
    try:
        from core.models_unified_system import ThoughtRecord

        limit = int(request.GET.get('limit', 10))
        thoughts = ThoughtRecord.objects.order_by('-started_at')[:limit]

        thought_list = []
        for thought in thoughts:
            thought_list.append({
                'id': str(thought.id),
                'cycle_number': thought.cycle_number,
                'cycle_type': thought.cycle_type,
                'context_summary': thought.context_summary,
                'reflection': thought.reflection[:500] if thought.reflection else '',
                'insights_count': len(thought.insights) if thought.insights else 0,
                'patterns_count': len(thought.patterns) if thought.patterns else 0,
                'opportunities_count': len(thought.opportunities) if thought.opportunities else 0,
                'concerns_count': len(thought.concerns) if thought.concerns else 0,
                'decisions_count': len(thought.decisions) if thought.decisions else 0,
                'actions_executed_count': len(thought.actions_executed) if thought.actions_executed else 0,
                'priority_score': thought.priority_score,
                'execution_status': thought.execution_status,
                'thinking_duration_seconds': thought.thinking_duration_seconds,
                'started_at': thought.started_at.isoformat(),
                'completed_at': thought.completed_at.isoformat() if thought.completed_at else None,
            })

        # Get stats
        total_thoughts = ThoughtRecord.objects.count()
        completed_thoughts = ThoughtRecord.objects.filter(execution_status='completed').count()
        total_insights = sum(
            len(t.insights) if t.insights else 0
            for t in ThoughtRecord.objects.all()
        )
        total_actions = sum(
            len(t.actions_executed) if t.actions_executed else 0
            for t in ThoughtRecord.objects.all()
        )

        return JsonResponse({
            'success': True,
            'thoughts': thought_list,
            'stats': {
                'total_thoughts': total_thoughts,
                'completed_thoughts': completed_thoughts,
                'total_insights': total_insights,
                'total_actions': total_actions,
            }
        })

    except Exception as e:
        logger.error(f"Error fetching thoughts: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def thought_detail_api(request, thought_id):
    """
    Get detailed information about a specific thought record.

    Includes full insights, patterns, decisions, and actions.
    """
    try:
        from core.models_unified_system import ThoughtRecord, AutonomousAction

        thought = ThoughtRecord.objects.get(id=thought_id)

        # Get associated actions
        actions = AutonomousAction.objects.filter(thought_record=thought).order_by('created_at')
        action_list = [
            {
                'id': str(a.id),
                'action_type': a.action_type,
                'action_name': a.action_name,
                'reasoning': a.reasoning,
                'priority': a.priority,
                'status': a.status,
                'result_summary': a.result_summary,
                'error_message': a.error_message,
                'created_at': a.created_at.isoformat(),
            }
            for a in actions
        ]

        return JsonResponse({
            'success': True,
            'thought': {
                'id': str(thought.id),
                'cycle_number': thought.cycle_number,
                'cycle_type': thought.cycle_type,
                'context_summary': thought.context_summary,
                'context_data': thought.context_data,
                'reflection': thought.reflection,
                'insights': thought.insights,
                'patterns': thought.patterns,
                'opportunities': thought.opportunities,
                'concerns': thought.concerns,
                'decisions': thought.decisions,
                'actions_planned': thought.actions_planned,
                'actions_executed': thought.actions_executed,
                'priority_score': thought.priority_score,
                'execution_status': thought.execution_status,
                'thinking_duration_seconds': thought.thinking_duration_seconds,
                'model_used': thought.model_used,
                'token_usage': thought.token_usage,
                'started_at': thought.started_at.isoformat(),
                'completed_at': thought.completed_at.isoformat() if thought.completed_at else None,
            },
            'actions': action_list,
        })

    except ThoughtRecord.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Thought record not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching thought detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def actions_api(request):
    """
    Get recent autonomous actions taken by the system.
    """
    try:
        from core.models_unified_system import AutonomousAction

        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status', None)

        actions = AutonomousAction.objects.select_related('thought_record')
        if status_filter:
            actions = actions.filter(status=status_filter)
        actions = actions.order_by('-created_at')[:limit]

        action_list = [
            {
                'id': str(a.id),
                'thought_cycle': a.thought_record.cycle_number,
                'action_type': a.action_type,
                'action_name': a.action_name,
                'reasoning': a.reasoning[:200] if a.reasoning else '',
                'priority': a.priority,
                'status': a.status,
                'result_summary': a.result_summary[:200] if a.result_summary else '',
                'created_at': a.created_at.isoformat(),
            }
            for a in actions
        ]

        # Get stats
        total_actions = AutonomousAction.objects.count()
        completed_actions = AutonomousAction.objects.filter(status='completed').count()
        failed_actions = AutonomousAction.objects.filter(status='failed').count()

        return JsonResponse({
            'success': True,
            'actions': action_list,
            'stats': {
                'total_actions': total_actions,
                'completed_actions': completed_actions,
                'failed_actions': failed_actions,
                'success_rate': round(completed_actions / total_actions * 100, 1) if total_actions > 0 else 0,
            }
        })

    except Exception as e:
        logger.error(f"Error fetching actions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_thinking_api(request):
    """
    Manually trigger a thinking cycle.

    This allows users to make the system think on-demand.
    """
    try:
        from core.tasks import run_autonomous_thinking_cycle

        cycle_type = request.data.get('cycle_type', 'manual')
        lookback_hours = int(request.data.get('lookback_hours', 24))

        # Queue the thinking task
        task = run_autonomous_thinking_cycle.delay(
            cycle_type=cycle_type,
            lookback_hours=lookback_hours
        )

        return JsonResponse({
            'success': True,
            'message': 'Thinking cycle initiated',
            'task_id': str(task.id),
        })

    except Exception as e:
        logger.error(f"Error triggering thinking: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def thinking_task_status_api(request, task_id):
    """
    Check the status of a thinking task.
    """
    try:
        result = AsyncResult(task_id)

        if result.ready():
            return JsonResponse({
                'success': True,
                'status': 'completed',
                'result': result.result,
            })
        elif result.failed():
            return JsonResponse({
                'success': False,
                'status': 'failed',
                'error': str(result.result),
            })
        else:
            return JsonResponse({
                'success': True,
                'status': 'pending',
                'state': result.state,
            })

    except Exception as e:
        logger.error(f"Error checking task status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def reasoning_config_api(request):
    """
    Get the current reasoning engine configuration.
    """
    try:
        from core.models_unified_system import ReasoningConfiguration

        config = ReasoningConfiguration.get_active_config()

        return JsonResponse({
            'success': True,
            'config': {
                'id': str(config.id),
                'is_active': config.is_active,
                'thinking_interval_minutes': config.thinking_interval_minutes,
                'min_insights_to_act': config.min_insights_to_act,
                'min_priority_to_act': config.min_priority_to_act,
                'max_actions_per_cycle': config.max_actions_per_cycle,
                'allowed_actions': config.allowed_actions,
                'require_approval_above_priority': config.require_approval_above_priority,
                'lookback_hours': config.lookback_hours,
                'updated_at': config.updated_at.isoformat(),
            }
        })

    except Exception as e:
        logger.error(f"Error fetching config: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_reasoning_config_api(request):
    """
    Update the reasoning engine configuration.
    """
    try:
        from core.models_unified_system import ReasoningConfiguration

        config = ReasoningConfiguration.get_active_config()

        # Update fields if provided
        if 'is_active' in request.data:
            config.is_active = request.data['is_active']
        if 'thinking_interval_minutes' in request.data:
            config.thinking_interval_minutes = int(request.data['thinking_interval_minutes'])
        if 'min_priority_to_act' in request.data:
            config.min_priority_to_act = float(request.data['min_priority_to_act'])
        if 'max_actions_per_cycle' in request.data:
            config.max_actions_per_cycle = int(request.data['max_actions_per_cycle'])
        if 'allowed_actions' in request.data:
            config.allowed_actions = request.data['allowed_actions']

        config.updated_by = 'api'
        config.save()

        return JsonResponse({
            'success': True,
            'message': 'Configuration updated',
        })

    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def reasoning_dashboard_api(request):
    """
    Get comprehensive dashboard data for the Autonomous Reasoning Engine.

    Returns stats, recent thoughts, insights summary, and action history.
    """
    try:
        from core.models_unified_system import ThoughtRecord, AutonomousAction, ReasoningConfiguration
        from datetime import timedelta

        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Get config status
        config = ReasoningConfiguration.get_active_config()

        # Get thought stats
        total_thoughts = ThoughtRecord.objects.count()
        thoughts_24h = ThoughtRecord.objects.filter(started_at__gte=last_24h).count()
        thoughts_7d = ThoughtRecord.objects.filter(started_at__gte=last_7d).count()

        # Get action stats
        total_actions = AutonomousAction.objects.count()
        actions_24h = AutonomousAction.objects.filter(created_at__gte=last_24h).count()
        actions_completed = AutonomousAction.objects.filter(status='completed').count()
        actions_failed = AutonomousAction.objects.filter(status='failed').count()

        # Get recent thoughts (last 5)
        recent_thoughts = list(ThoughtRecord.objects.order_by('-started_at')[:5].values(
            'id', 'cycle_number', 'cycle_type', 'context_summary', 'priority_score',
            'execution_status', 'started_at'
        ))

        # Get insight summary from all completed thoughts
        all_insights = []
        for thought in ThoughtRecord.objects.filter(execution_status='completed').order_by('-started_at')[:10]:
            if thought.insights:
                for insight in thought.insights[:3]:  # Top 3 from each
                    all_insights.append({
                        'cycle': thought.cycle_number,
                        'insight': insight.get('insight', str(insight))[:200],
                        'confidence': insight.get('confidence', 0.5),
                        'category': insight.get('category', 'unknown'),
                    })

        # Get action type breakdown
        from django.db.models import Count
        action_types = list(AutonomousAction.objects.values('action_type').annotate(
            count=Count('id')
        ).order_by('-count'))

        return JsonResponse({
            'success': True,
            'engine_status': {
                'is_active': config.is_active,
                'thinking_interval_minutes': config.thinking_interval_minutes,
                'min_priority_to_act': config.min_priority_to_act,
            },
            'thought_stats': {
                'total': total_thoughts,
                'last_24h': thoughts_24h,
                'last_7d': thoughts_7d,
            },
            'action_stats': {
                'total': total_actions,
                'last_24h': actions_24h,
                'completed': actions_completed,
                'failed': actions_failed,
                'success_rate': round(actions_completed / total_actions * 100, 1) if total_actions > 0 else 0,
            },
            'recent_thoughts': [
                {
                    'id': str(t['id']),
                    'cycle_number': t['cycle_number'],
                    'cycle_type': t['cycle_type'],
                    'context_summary': t['context_summary'][:100] if t['context_summary'] else '',
                    'priority_score': t['priority_score'],
                    'status': t['execution_status'],
                    'started_at': t['started_at'].isoformat(),
                }
                for t in recent_thoughts
            ],
            'top_insights': all_insights[:10],
            'action_breakdown': action_types[:10],
        })

    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
