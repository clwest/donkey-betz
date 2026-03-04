"""
Agent Analytics API Views - Session 641

Provides endpoints for the Agent Performance Dashboard:
- /api/agent-analytics/stats/ - Overall statistics
- /api/agent-analytics/top-performers/ - Top performing agents
- /api/agent-analytics/needs-attention/ - Agents needing attention
- /api/agent-analytics/activity/ - Activity data for charts
- /api/agent-analytics/executions/ - Recent execution logs
- /api/system-health/ - System health check
- /api/agents/test/ - Test agent execution
"""

import json
import logging
import os
import redis
from datetime import timedelta
from decimal import Decimal

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count, Sum, Q, F
from django.db.models.functions import TruncDate, TruncHour

from core.models_unified_system import Agent, AgentExecution

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@cache_page(30)  # 30s — system-wide agent stats (8 queries)
def agent_analytics_stats(request):
    """
    GET /api/agent-analytics/stats/
    Returns overall agent statistics for the dashboard hero section.
    """
    try:
        agents = Agent.objects.all()
        total_agents = agents.count()
        active_agents = agents.filter(is_active=True).count()

        # Calculate overall stats
        total_executions = agents.aggregate(total=Sum('total_executions'))['total'] or 0
        successful_executions = agents.aggregate(total=Sum('successful_executions'))['total'] or 0

        # Calculate success rate
        success_rate = 0
        if total_executions > 0:
            success_rate = round((successful_executions / total_executions) * 100, 1)

        # Get execution time stats from AgentExecution model
        executions = AgentExecution.objects.filter(status='completed')
        avg_time = executions.aggregate(avg=Avg('execution_time_ms'))['avg'] or 0

        # Count agents active today
        today = timezone.now().date()
        active_today = agents.filter(last_active__date=today).count()

        # Count failed executions today
        failures_today = AgentExecution.objects.filter(
            status='failed',
            created_at__date=today
        ).count()

        return JsonResponse({
            'total_agents': total_agents,
            'active_agents': active_agents,
            'success_rate': success_rate,
            'total_executions': total_executions,
            'avg_execution_time_ms': round(avg_time, 0),
            'active_today': active_today,
            'failures_today': failures_today,
        })
    except Exception as e:
        logger.error(f"Error in agent_analytics_stats: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@cache_page(30)  # 30s — top performers change slowly
def agent_analytics_top_performers(request):
    """
    GET /api/agent-analytics/top-performers/
    Returns top performing agents by success rate and execution count.
    """
    try:
        limit = int(request.GET.get('limit', 5))

        # Get agents with executions, sorted by success rate
        agents = Agent.objects.filter(
            total_executions__gt=0
        ).order_by('-successful_executions', '-effectiveness_score')[:limit]

        top_performers = []
        for agent in agents:
            top_performers.append({
                'id': str(agent.id),
                'name': agent.name,
                'success_rate': round(agent.success_rate, 1),
                'total_executions': agent.total_executions,
                'effectiveness_score': agent.effectiveness_score,
                'agent_type': agent.agent_type,
            })

        # Session 641: Changed key to 'performers' to match frontend expectations
        return JsonResponse({'performers': top_performers})
    except Exception as e:
        logger.error(f"Error in agent_analytics_top_performers: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@cache_page(30)  # 30s — attention list is aggregate data
def agent_analytics_needs_attention(request):
    """
    GET /api/agent-analytics/needs-attention/
    Returns agents that need attention (low success rate, recent failures, inactive).
    """
    try:
        limit = int(request.GET.get('limit', 5))
        week_ago = timezone.now() - timedelta(days=7)

        needs_attention = []

        # Find agents with low effectiveness score
        low_effectiveness = Agent.objects.filter(
            effectiveness_score__lt=70,
            is_active=True
        ).order_by('effectiveness_score')[:limit]

        for agent in low_effectiveness:
            needs_attention.append({
                'id': str(agent.id),
                'name': agent.name,
                'agent': agent.name,  # Session 641: Frontend expects 'agent'
                'issue': 'Low effectiveness score',
                'value': agent.effectiveness_score,
                'agent_type': agent.agent_type,
            })

        # Find agents with recent failures
        recent_failures = AgentExecution.objects.filter(
            status='failed',
            created_at__gte=week_ago
        ).values('agent__id', 'agent__name', 'agent__agent_type').annotate(
            failure_count=Count('id')
        ).order_by('-failure_count')[:limit]

        for failure in recent_failures:
            if not any(a['id'] == str(failure['agent__id']) for a in needs_attention):
                needs_attention.append({
                    'id': str(failure['agent__id']),
                    'name': failure['agent__name'],
                    'agent': failure['agent__name'],  # Session 641: Frontend expects 'agent'
                    'issue': 'Recent failures',
                    'value': failure['failure_count'],
                    'agent_type': failure['agent__agent_type'],
                })

        # Find inactive agents (not used in 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        inactive = Agent.objects.filter(
            is_active=True,
            last_active__lt=month_ago
        ).order_by('last_active')[:limit]

        for agent in inactive:
            if not any(a['id'] == str(agent.id) for a in needs_attention):
                days_inactive = (timezone.now() - agent.last_active).days
                needs_attention.append({
                    'id': str(agent.id),
                    'name': agent.name,
                    'agent': agent.name,  # Session 641: Frontend expects 'agent'
                    'issue': 'Inactive',
                    'value': f'{days_inactive} days',
                    'agent_type': agent.agent_type,
                })

        # Session 641: Changed key to 'issues' to match frontend expectations
        return JsonResponse({'issues': needs_attention[:limit]})
    except Exception as e:
        logger.error(f"Error in agent_analytics_needs_attention: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@cache_page(30)  # 30s — chart data
def agent_analytics_activity(request):
    """
    GET /api/agent-analytics/activity/
    Returns activity data for charts (executions over time).
    """
    try:
        days = int(request.GET.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)

        # Get daily execution counts
        daily_data = AgentExecution.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed')),
        ).order_by('date')

        # Format for chart
        labels = []
        totals = []
        completed = []
        failed = []

        for item in daily_data:
            labels.append(item['date'].strftime('%b %d'))
            totals.append(item['total'])
            completed.append(item['completed'])
            failed.append(item['failed'])

        # If no data, generate empty days
        if not labels:
            for i in range(days):
                date = (timezone.now() - timedelta(days=days-i-1)).date()
                labels.append(date.strftime('%b %d'))
                totals.append(0)
                completed.append(0)
                failed.append(0)

        return JsonResponse({
            'labels': labels,
            'datasets': {
                'total': totals,
                'completed': completed,
                'failed': failed,
            }
        })
    except Exception as e:
        logger.error(f"Error in agent_analytics_activity: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@cache_page(15)  # 15s — execution logs refresh frequently
def agent_analytics_executions(request):
    """
    GET /api/agent-analytics/executions/
    Returns recent execution logs.
    """
    try:
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        status_filter = request.GET.get('status', None)
        agent_filter = request.GET.get('agent', None)

        executions = AgentExecution.objects.select_related('agent').order_by('-created_at')

        if status_filter:
            executions = executions.filter(status=status_filter)
        if agent_filter:
            executions = executions.filter(agent__name__icontains=agent_filter)

        total = executions.count()
        executions = executions[offset:offset + limit]

        results = []
        for exe in executions:
            # Calculate duration in seconds from milliseconds
            duration_seconds = (exe.execution_time_ms or 0) / 1000.0
            is_success = exe.status == 'completed'

            results.append({
                'id': str(exe.id),
                'agent_id': str(exe.agent.id),
                'agent_name': exe.agent.name,
                'agent_type': exe.agent.agent_type,
                'task': exe.task[:100] + '...' if len(exe.task) > 100 else exe.task,
                'status': exe.status,
                'execution_time_ms': exe.execution_time_ms,
                'tokens_used': exe.tokens_used,
                'cost': float(exe.cost) if exe.cost else 0,
                'created_at': exe.created_at.isoformat(),
                'completed_at': exe.completed_at.isoformat() if exe.completed_at else None,
                'error_message': exe.error_message[:200] if exe.error_message else None,
                # Session 641: Additional fields for frontend compatibility
                'agent': exe.agent.name,  # Frontend expects 'agent'
                'timestamp': exe.created_at.isoformat(),  # Frontend expects 'timestamp'
                'duration': duration_seconds,  # Frontend expects duration in seconds
                'success': is_success,  # Frontend expects boolean success
            })

        return JsonResponse({
            'total': total,
            'limit': limit,
            'offset': offset,
            'executions': results,
        })
    except Exception as e:
        logger.error(f"Error in agent_analytics_executions: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@cache_page(30)  # 30s — health check aggregates
def system_health_check(request):
    """
    GET /api/system-health/
    Returns system health status for the performance dashboard.
    """
    try:
        from django.db import connection
        from django.core.cache import cache
        import redis

        health = {
            'status': 'healthy',
            'checks': {},
            'timestamp': timezone.now().isoformat(),
        }

        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health['checks']['database'] = {'status': 'ok', 'message': 'Connected'}
        except Exception as e:
            health['checks']['database'] = {'status': 'error', 'message': str(e)}
            health['status'] = 'degraded'

        # Redis check
        try:
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
            r.ping()
            health['checks']['redis'] = {'status': 'ok', 'message': 'Connected'}
        except Exception as e:
            health['checks']['redis'] = {'status': 'error', 'message': str(e)}
            health['status'] = 'degraded'

        # Agent system check
        try:
            agent_count = Agent.objects.count()
            active_count = Agent.objects.filter(is_active=True).count()
            health['checks']['agents'] = {
                'status': 'ok',
                'message': f'{active_count}/{agent_count} agents active',
                'total': agent_count,
                'active': active_count,
            }
        except Exception as e:
            health['checks']['agents'] = {'status': 'error', 'message': str(e)}
            health['status'] = 'degraded'

        # Celery check
        try:
            from core.celery import app
            inspector = app.control.inspect()
            active = inspector.active()
            if active:
                worker_count = len(active)
                health['checks']['celery'] = {
                    'status': 'ok',
                    'message': f'{worker_count} workers active',
                    'workers': worker_count,
                }
            else:
                health['checks']['celery'] = {'status': 'warning', 'message': 'No active workers'}
        except Exception as e:
            health['checks']['celery'] = {'status': 'error', 'message': str(e)}

        return JsonResponse(health)
    except Exception as e:
        logger.error(f"Error in system_health_check: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_agent_execution(request):
    """
    POST /api/agents/test/
    Test execution of an agent with a sample task.
    """
    try:
        data = json.loads(request.body)
        # Accept both 'agent' and 'agent_name' for flexibility
        agent_name = data.get('agent_name') or data.get('agent')
        task = data.get('task', 'Test execution - health check')

        if not agent_name:
            return JsonResponse({'error': 'agent_name or agent required'}, status=400)

        # Get the agent
        try:
            agent = Agent.objects.get(name=agent_name)
        except Agent.DoesNotExist:
            return JsonResponse({'error': f'Agent {agent_name} not found'}, status=404)

        # Import the agent router and execute
        from core.agent_router import AgentRouter

        start_time = timezone.now()
        # Pass user to AgentRouter constructor (can be None for unauthenticated)
        router = AgentRouter(user=request.user if request.user.is_authenticated else None)

        try:
            # Route to the agent - pass agent_name and task as positional args
            result = router.route(agent_name, task, context={})

            execution_time = (timezone.now() - start_time).total_seconds() * 1000

            return JsonResponse({
                'success': True,
                'agent_name': agent_name,
                'task': task,
                'execution_time_ms': round(execution_time, 0),
                'result_preview': str(result)[:500] if result else None,
            })
        except Exception as e:
            execution_time = (timezone.now() - start_time).total_seconds() * 1000
            return JsonResponse({
                'success': False,
                'agent_name': agent_name,
                'task': task,
                'execution_time_ms': round(execution_time, 0),
                'error': str(e),
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in test_agent_execution: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def celery_status(request):
    """
    GET /api/celery/status/
    Returns comprehensive Celery worker and task status for monitoring.
    Session 642: Celery monitoring dashboard
    """
    try:
        from core.celery import app
        import redis

        status = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': 'healthy',
            'workers': [],
            'queues': [],
            'scheduled_tasks': [],
            'active_tasks': [],
            'stats': {
                'total_workers': 0,
                'total_queues': 0,
                'total_scheduled': 0,
                'total_active': 0,
            }
        }

        # Get Celery inspector
        inspector = app.control.inspect()

        # Check workers
        try:
            ping_results = inspector.ping()
            if ping_results:
                for worker_name, response in ping_results.items():
                    status['workers'].append({
                        'name': worker_name,
                        'status': 'online' if response.get('ok') == 'pong' else 'error',
                        'response': response,
                    })
                status['stats']['total_workers'] = len(ping_results)
            else:
                status['overall_status'] = 'degraded'
                status['workers'].append({
                    'name': 'No workers',
                    'status': 'offline',
                    'response': None,
                })
        except Exception as e:
            status['overall_status'] = 'error'
            status['workers'].append({
                'name': 'Error checking workers',
                'status': 'error',
                'response': str(e),
            })

        # Check active tasks
        try:
            active = inspector.active()
            if active:
                for worker_name, tasks in active.items():
                    for task in tasks:
                        status['active_tasks'].append({
                            'worker': worker_name,
                            'task_id': task.get('id', 'N/A'),
                            'task_name': task.get('name', 'Unknown'),
                            'args': str(task.get('args', []))[:100],
                            'started': task.get('time_start', 0),
                        })
                status['stats']['total_active'] = len(status['active_tasks'])
        except Exception as e:
            logger.warning(f"Error checking active tasks: {e}")

        # Check queues
        try:
            queues = inspector.active_queues()
            if queues:
                seen_queues = set()
                for worker_name, worker_queues in queues.items():
                    for q in worker_queues:
                        queue_name = q.get('name', 'default')
                        if queue_name not in seen_queues:
                            seen_queues.add(queue_name)
                            status['queues'].append({
                                'name': queue_name,
                                'routing_key': q.get('routing_key', ''),
                            })
                status['stats']['total_queues'] = len(seen_queues)
        except Exception as e:
            logger.warning(f"Error checking queues: {e}")

        # Get scheduled beat tasks from config
        try:
            beat_schedule = app.conf.beat_schedule or {}
            for task_name, task_config in list(beat_schedule.items())[:50]:  # Limit to 50
                schedule = task_config.get('schedule', 'Unknown')
                # Format schedule nicely
                if hasattr(schedule, 'run_every'):
                    schedule_str = f"Every {schedule.run_every}"
                elif hasattr(schedule, 'hour') and hasattr(schedule, 'minute'):
                    schedule_str = f"Cron: {schedule.minute} {schedule.hour} * * *"
                else:
                    schedule_str = str(schedule)[:50]

                status['scheduled_tasks'].append({
                    'name': task_name,
                    'task': task_config.get('task', 'Unknown'),
                    'schedule': schedule_str,
                })
            status['stats']['total_scheduled'] = len(beat_schedule)
        except Exception as e:
            logger.warning(f"Error checking beat schedule: {e}")

        # Check Redis queue lengths
        try:
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
            for queue in ['celery', 'default', 'long_running', 'broadcast']:
                length = r.llen(queue)
                if length > 0:
                    # Find existing queue entry or add new one
                    found = False
                    for q in status['queues']:
                        if q['name'] == queue:
                            q['pending'] = length
                            found = True
                            break
                    if not found:
                        status['queues'].append({
                            'name': queue,
                            'pending': length,
                        })
        except Exception as e:
            logger.warning(f"Error checking Redis queues: {e}")

        return JsonResponse(status)

    except Exception as e:
        logger.error(f"Error in celery_status: {e}")
        return JsonResponse({
            'timestamp': timezone.now().isoformat(),
            'overall_status': 'error',
            'error': str(e),
            'workers': [],
            'queues': [],
            'scheduled_tasks': [],
            'active_tasks': [],
            'stats': {'total_workers': 0, 'total_queues': 0, 'total_scheduled': 0, 'total_active': 0}
        })
