"""
Session 744: Celery Health API Endpoints

Provides REST API endpoints for monitoring Celery infrastructure health.

Endpoints:
- GET /api/celery/status/ - Full health status
- GET /api/celery/quick/ - Quick health check
- GET /api/celery/workers/ - Worker details
- GET /api/celery/queues/ - Queue depths
- GET /api/celery/tasks/ - Recent task stats
- GET /api/celery/schedule/ - Scheduled task list
- GET /api/celery/breakdown/ - Task volume aggregation (Session 1048)
- GET /api/celery/breakdown/task/ - Task drill-down (Session 1048)
"""

import logging
from datetime import timedelta

from django.db.models import Count, Q, Avg
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from core.services.celery_health import get_celery_health_service

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class CeleryStatusView(View):
    """Full Celery health status."""

    def get(self, request):
        """
        GET /api/celery/status/

        Returns comprehensive Celery health including:
        - Overall status and health score
        - Worker status
        - Beat scheduler status
        - Queue depths
        - Recent task execution stats
        - Active alerts
        """
        try:
            service = get_celery_health_service()
            status = service.get_full_status()
            return JsonResponse(status)
        except Exception as e:
            logger.error(f"Error getting Celery status: {e}")
            return JsonResponse({
                'error': str(e),
                'overall_status': 'error',
                'is_healthy': False,
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CeleryQuickStatusView(View):
    """Quick Celery health check."""

    def get(self, request):
        """
        GET /api/celery/quick/

        Fast health check - just workers and beat status.
        Use for frequent polling.
        """
        try:
            service = get_celery_health_service()
            status = service.get_quick_status()
            return JsonResponse(status)
        except Exception as e:
            logger.error(f"Error getting quick Celery status: {e}")
            return JsonResponse({
                'error': str(e),
                'is_healthy': False,
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CeleryWorkersView(View):
    """Celery worker details."""

    def get(self, request):
        """
        GET /api/celery/workers/

        Returns detailed worker information:
        - Worker count and names
        - Active tasks per worker
        - Pool type and concurrency
        """
        try:
            service = get_celery_health_service()
            workers = service._check_workers()
            return JsonResponse(workers)
        except Exception as e:
            logger.error(f"Error getting Celery workers: {e}")
            return JsonResponse({
                'error': str(e),
                'count': 0,
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CeleryQueuesView(View):
    """Celery queue status."""

    def get(self, request):
        """
        GET /api/celery/queues/

        Returns queue depth information:
        - Total depth across all queues
        - Per-queue depth and status
        """
        try:
            service = get_celery_health_service()
            queues = service._check_queues()
            return JsonResponse(queues)
        except Exception as e:
            logger.error(f"Error getting Celery queues: {e}")
            return JsonResponse({
                'error': str(e),
                'total_depth': 0,
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CeleryTasksView(View):
    """Recent task execution stats."""

    def get(self, request):
        """
        GET /api/celery/tasks/

        Returns recent task execution statistics:
        - Tasks in last hour/24 hours
        - Success/failure rates
        - Top failing tasks
        """
        try:
            service = get_celery_health_service()
            tasks = service._check_recent_tasks()
            return JsonResponse(tasks)
        except Exception as e:
            logger.error(f"Error getting Celery tasks: {e}")
            return JsonResponse({
                'error': str(e),
                'total_1h': 0,
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CeleryScheduleView(View):
    """Scheduled periodic tasks."""

    def get(self, request):
        """
        GET /api/celery/schedule/

        Returns list of all scheduled periodic tasks:
        - Task name and schedule type
        - Last run time
        - Total run count
        """
        try:
            service = get_celery_health_service()
            schedule = service.get_task_schedule()
            return JsonResponse({
                'count': len(schedule),
                'tasks': schedule,
            })
        except Exception as e:
            logger.error(f"Error getting Celery schedule: {e}")
            return JsonResponse({
                'error': str(e),
                'count': 0,
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CeleryPingView(View):
    """Ping Celery workers."""

    def get(self, request):
        """
        GET /api/celery/ping/

        Ping all workers and return response map.
        Useful for quick connectivity check.
        """
        try:
            service = get_celery_health_service()
            ping_results = service.ping_workers()
            return JsonResponse({
                'workers_responding': sum(1 for v in ping_results.values() if v),
                'workers_total': len(ping_results),
                'results': ping_results,
            })
        except Exception as e:
            logger.error(f"Error pinging Celery workers: {e}")
            return JsonResponse({
                'error': str(e),
                'workers_responding': 0,
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CeleryStaleTasks(View):
    """Check for stale critical tasks."""

    def get(self, request):
        """
        GET /api/celery/stale/

        Returns tasks that haven't run in their expected timeframe.
        """
        try:
            service = get_celery_health_service()
            stale = service._check_stale_tasks()
            return JsonResponse(stale)
        except Exception as e:
            logger.error(f"Error checking stale tasks: {e}")
            return JsonResponse({
                'error': str(e),
                'count': 0,
            }, status=500)


# ── Session 1048: Task Volume Breakdown ──────────────────────────────────────

WINDOW_MAP = {
    '15m': 15,
    '60m': 60,
    '2h': 120,
    '6h': 360,
    '24h': 1440,
}


def _percentile(sorted_list, p):
    """Compute p-th percentile from a pre-sorted list."""
    if not sorted_list:
        return 0
    k = (len(sorted_list) - 1) * p
    f = int(k)
    return sorted_list[f]


@method_decorator(csrf_exempt, name='dispatch')
class TaskBreakdownView(View):
    """Task volume aggregation breakdown."""

    def get(self, request):
        """
        GET /api/celery/breakdown/?window=60m&limit=25

        Returns task volume breakdown: totals, by_task (with percentiles),
        by_agent. Queries CeleryTaskEvent and AgentExecution.
        """
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            from core.models import AgentExecution

            window = request.GET.get('window', '60m')
            minutes = WINDOW_MAP.get(window, 60)
            limit = min(int(request.GET.get('limit', 25)), 50)
            cutoff = timezone.now() - timedelta(minutes=minutes)

            qs = CeleryTaskEvent.objects.filter(started_at__gte=cutoff)

            # ── Totals ──
            totals = qs.aggregate(
                tasks=Count('id'),
                success=Count('id', filter=Q(status='SUCCESS')),
                failure=Count('id', filter=Q(status='FAILURE')),
                started=Count('id', filter=Q(status='STARTED')),
            )

            # ── By task name ──
            by_task_qs = (
                qs.values('task_name')
                .annotate(
                    count_total=Count('id'),
                    count_success=Count('id', filter=Q(status='SUCCESS')),
                    count_failure=Count('id', filter=Q(status='FAILURE')),
                    avg_duration=Avg('duration_seconds'),
                )
                .order_by('-count_total')[:limit]
            )

            top_task_names = [row['task_name'] for row in by_task_qs]

            # Percentiles: fetch raw durations for top tasks in one query
            duration_rows = (
                qs.filter(task_name__in=top_task_names, duration_seconds__isnull=False)
                .values_list('task_name', 'duration_seconds')
            )
            durations_by_task = {}
            for task_name, dur in duration_rows:
                durations_by_task.setdefault(task_name, []).append(dur)
            for v in durations_by_task.values():
                v.sort()

            # Queue breakdown for top tasks
            queue_rows = (
                qs.filter(task_name__in=top_task_names)
                .values('task_name', 'queue')
                .annotate(count=Count('id'))
            )
            queues_by_task = {}
            for row in queue_rows:
                queues_by_task.setdefault(row['task_name'], []).append(
                    {'queue': row['queue'] or 'default', 'count': row['count']}
                )

            by_task = []
            for row in by_task_qs:
                tn = row['task_name']
                ct = row['count_total']
                cf = row['count_failure']
                durs = durations_by_task.get(tn, [])
                avg_dur = row['avg_duration'] or 0
                by_task.append({
                    'task_name': tn,
                    'count_total': ct,
                    'count_success': row['count_success'],
                    'count_failure': cf,
                    'failure_rate': round(cf / ct, 3) if ct else 0,
                    'avg_duration_ms': round(avg_dur * 1000),
                    'p50_ms': round(_percentile(durs, 0.5) * 1000),
                    'p95_ms': round(_percentile(durs, 0.95) * 1000),
                    'top_queues': sorted(
                        queues_by_task.get(tn, []),
                        key=lambda q: q['count'], reverse=True
                    )[:3],
                })

            # ── By agent ──
            by_agent = list(
                AgentExecution.objects.filter(created_at__gte=cutoff)
                .values('agent__name')
                .annotate(
                    execution_count=Count('id'),
                    count_failure=Count('id', filter=Q(status='failed')),
                )
                .order_by('-execution_count')[:limit]
            )
            for row in by_agent:
                row['agent_name'] = row.pop('agent__name')
                ec = row['execution_count']
                cf = row['count_failure']
                row['failure_rate'] = round(cf / ec, 3) if ec else 0

            return JsonResponse({
                'window': window,
                'generated_at': timezone.now().isoformat(),
                'totals': totals,
                'by_task': by_task,
                'by_agent': by_agent,
            })

        except Exception as e:
            logger.error(f"Error in task breakdown: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TaskBreakdownDetailView(View):
    """Drill-down into a specific task name."""

    def get(self, request):
        """
        GET /api/celery/breakdown/task/?task_name=core.tasks.xyz&window=60m&limit=50

        Returns recent executions for a specific task name.
        """
        try:
            from core.models_celery_telemetry import CeleryTaskEvent

            task_name = request.GET.get('task_name', '')
            if not task_name:
                return JsonResponse({'error': 'task_name is required'}, status=400)

            window = request.GET.get('window', '60m')
            minutes = WINDOW_MAP.get(window, 60)
            limit = min(int(request.GET.get('limit', 50)), 200)
            status = request.GET.get('status', '')
            cutoff = timezone.now() - timedelta(minutes=minutes)

            qs = CeleryTaskEvent.objects.filter(task_name=task_name, started_at__gte=cutoff)
            if status:
                qs = qs.filter(status=status.upper())
            rows = qs.order_by('-started_at')[:limit]

            executions = []
            for r in rows:
                dur_ms = round(r.duration_seconds * 1000) if r.duration_seconds else None
                executions.append({
                    'task_id': r.task_id,
                    'started_at': r.started_at.isoformat() if r.started_at else None,
                    'finished_at': r.finished_at.isoformat() if r.finished_at else None,
                    'duration_ms': dur_ms,
                    'status': r.status,
                    'queue': r.queue or 'default',
                    'worker': r.worker,
                    'error_type': r.error_type or None,
                    'error_message': (r.error_message or '')[:500] or None,
                })

            return JsonResponse({
                'task_name': task_name,
                'window': window,
                'count': len(executions),
                'executions': executions,
            })

        except Exception as e:
            logger.error(f"Error in task breakdown detail: {e}")
            return JsonResponse({'error': str(e)}, status=500)
