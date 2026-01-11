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
"""

import logging
from django.http import JsonResponse
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
