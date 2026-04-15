"""
Session 744: Celery Health Service - Phase 1 Foundation

Monitors the health and status of Celery workers, beat scheduler,
task queues, and task execution metrics.

This is CRITICAL infrastructure - without healthy Celery workers,
150+ scheduled tasks cannot execute and the autonomous system is dormant.

Components Monitored:
- Workers: Are workers online and responsive?
- Beat: Is the beat scheduler running?
- Queues: What's the queue depth? Are tasks backing up?
- Tasks: What's the recent success/failure rate?
- Execution: Are scheduled tasks actually executing?

Usage:
    from core.services.celery_health import get_celery_health_service
    service = get_celery_health_service()
    status = service.get_full_status()
"""

import logging
import os
import time
from datetime import timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

# Singleton instance
_celery_health_instance: Optional['CeleryHealthService'] = None


def get_celery_health_service() -> 'CeleryHealthService':
    """Get the singleton CeleryHealthService instance."""
    global _celery_health_instance
    if _celery_health_instance is None:
        _celery_health_instance = CeleryHealthService()
    return _celery_health_instance


class CeleryHealthService:
    """
    Monitors Celery infrastructure health.

    Health Levels:
    - healthy: Workers online, tasks executing, queues normal
    - degraded: Some workers offline or high queue depth
    - critical: No workers or beat offline
    - offline: Cannot connect to broker
    """

    # Queue priority levels
    QUEUE_PRIORITIES = {
        'celery': 'default',
        'content': 'normal',
        'spiders': 'normal',
        'ml': 'low',
        'reports': 'low',
    }

    # Expected task execution intervals (for staleness detection)
    CRITICAL_TASKS = {
        'core.tasks.check_heart': timedelta(minutes=2),
        'core.tasks.check_circulatory': timedelta(minutes=2),
        'core.tasks.run_spider_network': timedelta(minutes=20),
        'core.tasks.check_content_diversity': timedelta(hours=13),  # Twice daily
    }

    def __init__(self):
        self._app = None
        self._initialized = False
        self._last_status: Optional[Dict] = None
        self._initialize()

    def _initialize(self):
        """Initialize Celery app reference."""
        if self._initialized:
            return

        try:
            from core.celery import app
            self._app = app
            self._initialized = True
            logger.info("🔧 CeleryHealthService initialized")
        except Exception as e:
            logger.error(f"Failed to initialize CeleryHealthService: {e}")

    def get_full_status(self) -> Dict[str, Any]:
        """
        Get comprehensive Celery health status.

        Returns dict with:
        - overall_status: healthy/degraded/critical/offline
        - health_score: 0-100
        - workers: Worker status details
        - beat: Beat scheduler status
        - queues: Queue depths and status
        - tasks: Recent task execution stats
        - alerts: Active alerts
        """
        start_time = time.time()

        # Gather all component statuses
        workers = self._check_workers()
        beat = self._check_beat()
        queues = self._check_queues()
        tasks = self._check_recent_tasks()
        stale_tasks = self._check_stale_tasks()

        # Calculate health score
        health_score = self._calculate_health_score(workers, beat, queues, tasks)

        # Determine overall status
        if workers['count'] == 0 or not beat['is_running']:
            overall_status = 'critical'
        elif health_score >= 80:
            overall_status = 'healthy'
        elif health_score >= 50:
            overall_status = 'degraded'
        else:
            overall_status = 'critical'

        # Generate alerts
        alerts = self._generate_alerts(workers, beat, queues, tasks, stale_tasks)

        check_duration_ms = int((time.time() - start_time) * 1000)

        status = {
            'overall_status': overall_status,
            'health_score': round(health_score, 1),
            'is_healthy': overall_status in ('healthy', 'degraded'),
            'check_duration_ms': check_duration_ms,
            'timestamp': timezone.now().isoformat(),
            'workers': workers,
            'beat': beat,
            'queues': queues,
            'tasks': tasks,
            'stale_tasks': stale_tasks,
            'alerts': alerts,
            'alerts_count': len(alerts),
        }

        self._last_status = status

        logger.info(
            f"🔧 Celery health: {overall_status.upper()} ({health_score:.1f}%) - "
            f"{workers['count']} workers, {tasks.get('total_24h', 0)} tasks/24h"
        )

        return status

    def _check_workers(self) -> Dict[str, Any]:
        """Check Celery worker status."""
        try:
            if not self._app:
                return {
                    'count': 0,
                    'status': 'offline',
                    'workers': [],
                    'error': 'Celery app not initialized'
                }

            # Inspect workers with timeout (Session 758: increased from 2s to 10s for busy workers)
            inspect = self._app.control.inspect(timeout=10.0)

            # Get active workers
            active = inspect.active() or {}
            stats = inspect.stats() or {}
            ping_response = inspect.ping() or {}

            workers = []
            for worker_name, worker_stats in stats.items():
                worker_info = {
                    'name': worker_name,
                    'status': 'online' if worker_name in ping_response else 'unresponsive',
                    'active_tasks': len(active.get(worker_name, [])),
                    'pool': worker_stats.get('pool', {}).get('implementation', 'unknown'),
                    'concurrency': worker_stats.get('pool', {}).get('max-concurrency', 0),
                    'processed': worker_stats.get('total', {}).get('tasks', 0),
                }
                workers.append(worker_info)

            total_active = sum(w['active_tasks'] for w in workers)

            # Session 758: Fallback for solo pool workers that can't respond when busy
            # Check for running celery worker processes if no workers responded
            if not workers:
                process_workers = self._check_worker_processes()
                if process_workers:
                    return {
                        'count': len(process_workers),
                        'status': 'busy',  # Workers exist but are busy
                        'total_active_tasks': len(process_workers),  # Assume 1 task per worker
                        'workers': process_workers,
                    }

            return {
                'count': len(workers),
                'status': 'online' if workers else 'offline',
                'total_active_tasks': total_active,
                'workers': workers,
            }

        except Exception as e:
            logger.warning(f"Error checking Celery workers: {e}")
            # Session 758: Try process fallback on exception too
            process_workers = self._check_worker_processes()
            if process_workers:
                return {
                    'count': len(process_workers),
                    'status': 'busy',
                    'total_active_tasks': len(process_workers),
                    'workers': process_workers,
                }
            return {
                'count': 0,
                'status': 'error',
                'workers': [],
                'error': str(e)
            }

    def _check_worker_processes(self) -> List[Dict[str, Any]]:
        """
        Session 758: Fallback to check for running celery worker processes.
        This handles solo pool workers that can't respond to control commands when busy.
        """
        import subprocess
        try:
            # Look for celery worker processes
            result = subprocess.run(
                ['pgrep', '-f', 'celery.*worker'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                workers = []
                for pid in pids:
                    workers.append({
                        'name': f'celery-worker-{pid}',
                        'status': 'busy',
                        'active_tasks': 1,
                        'pool': 'solo',
                        'concurrency': 1,
                        'processed': 0,
                        'pid': int(pid),
                    })
                return workers
        except Exception as e:
            logger.debug(f"Process check fallback failed: {e}")
        return []

    def _check_beat(self) -> Dict[str, Any]:
        """Check Celery beat scheduler status."""
        try:
            from django_celery_beat.models import PeriodicTask

            # Count enabled tasks
            enabled_tasks = PeriodicTask.objects.filter(enabled=True).count()
            total_tasks = PeriodicTask.objects.count()

            # Check for recent beat activity by looking at last_run_at
            recent_cutoff = timezone.now() - timedelta(minutes=5)
            recently_run = PeriodicTask.objects.filter(
                last_run_at__gte=recent_cutoff
            ).count()

            # Beat is "running" if tasks have executed recently
            is_running = recently_run > 0

            # Also check if beat PID file exists
            import os
            beat_pid_exists = os.path.exists('.celery-beat.pid')

            return {
                'is_running': is_running or beat_pid_exists,
                'status': 'running' if (is_running or beat_pid_exists) else 'stopped',
                'enabled_tasks': enabled_tasks,
                'total_tasks': total_tasks,
                'recently_executed': recently_run,
                'pid_file_exists': beat_pid_exists,
            }

        except Exception as e:
            logger.warning(f"Error checking Celery beat: {e}")
            return {
                'is_running': False,
                'status': 'error',
                'error': str(e)
            }

    def _check_queues(self) -> Dict[str, Any]:
        """Check queue depths and status."""
        try:
            import redis

            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

            queues = {}
            total_depth = 0

            for queue_name in self.QUEUE_PRIORITIES.keys():
                try:
                    # Celery uses lists for queues in Redis
                    depth = int(r.llen(queue_name) or 0)
                    queues[queue_name] = {
                        'depth': depth,
                        'priority': self.QUEUE_PRIORITIES.get(queue_name, 'normal'),
                        'status': 'normal' if depth < 100 else ('high' if depth < 500 else 'critical')
                    }
                    total_depth += depth
                except Exception:
                    queues[queue_name] = {'depth': 0, 'status': 'unknown'}

            return {
                'total_depth': total_depth,
                'status': 'normal' if total_depth < 500 else ('high' if total_depth < 2000 else 'critical'),
                'queues': queues,
            }

        except Exception as e:
            logger.warning(f"Error checking queues: {e}")
            return {
                'total_depth': 0,
                'status': 'error',
                'queues': {},
                'error': str(e)
            }

    def _check_recent_tasks(self) -> Dict[str, Any]:
        """Check recent task execution statistics."""
        try:
            from django_celery_results.models import TaskResult

            now = timezone.now()
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(hours=24)

            # Last hour stats
            hour_results = TaskResult.objects.filter(date_done__gte=hour_ago)
            hour_success = hour_results.filter(status='SUCCESS').count()
            hour_failure = hour_results.filter(status='FAILURE').count()
            hour_total = hour_results.count()

            # Last 24 hour stats
            day_results = TaskResult.objects.filter(date_done__gte=day_ago)
            day_success = day_results.filter(status='SUCCESS').count()
            day_failure = day_results.filter(status='FAILURE').count()
            day_total = day_results.count()

            # Success rate
            hour_rate = (hour_success / hour_total * 100) if hour_total > 0 else 0
            day_rate = (day_success / day_total * 100) if day_total > 0 else 0

            # Get most recent task
            latest = TaskResult.objects.order_by('-date_done').first()
            latest_info = None
            if latest:
                latest_info = {
                    'task_name': latest.task_name,
                    'status': latest.status,
                    'date_done': latest.date_done.isoformat() if latest.date_done else None,
                }

            # Get failure breakdown
            recent_failures = TaskResult.objects.filter(
                date_done__gte=hour_ago,
                status='FAILURE'
            ).values('task_name').annotate(
                count=models.Count('id')
            ).order_by('-count')[:5]

            return {
                'total_1h': hour_total,
                'success_1h': hour_success,
                'failure_1h': hour_failure,
                'success_rate_1h': round(hour_rate, 1),
                'total_24h': day_total,
                'success_24h': day_success,
                'failure_24h': day_failure,
                'success_rate_24h': round(day_rate, 1),
                'latest_task': latest_info,
                'top_failures': list(recent_failures) if recent_failures else [],
                'is_executing': hour_total > 0,
            }

        except Exception as e:
            logger.warning(f"Error checking recent tasks: {e}")
            return {
                'total_1h': 0,
                'total_24h': 0,
                'success_rate_1h': 0,
                'success_rate_24h': 0,
                'is_executing': False,
                'error': str(e)
            }

    def _check_stale_tasks(self) -> Dict[str, Any]:
        """Check for critical tasks that haven't run in expected timeframe."""
        try:
            from django_celery_beat.models import PeriodicTask

            now = timezone.now()
            stale = []

            for task_name, max_interval in self.CRITICAL_TASKS.items():
                try:
                    task = PeriodicTask.objects.filter(
                        task=task_name,
                        enabled=True
                    ).first()

                    if task:
                        if task.last_run_at:
                            time_since = now - task.last_run_at
                            is_stale = time_since > max_interval

                            if is_stale:
                                stale.append({
                                    'task': task_name,
                                    'last_run': task.last_run_at.isoformat(),
                                    'expected_interval': str(max_interval),
                                    'time_since': str(time_since),
                                })
                        else:
                            # Never run
                            stale.append({
                                'task': task_name,
                                'last_run': None,
                                'expected_interval': str(max_interval),
                                'status': 'never_run',
                            })
                except Exception as e:
                    logger.warning(f"Stale task check failed for task: {e}")

            return {
                'count': len(stale),
                'stale_tasks': stale,
                'is_healthy': len(stale) == 0,
            }

        except Exception as e:
            return {
                'count': 0,
                'stale_tasks': [],
                'error': str(e)
            }

    def _calculate_health_score(
        self,
        workers: Dict,
        beat: Dict,
        queues: Dict,
        tasks: Dict
    ) -> float:
        """Calculate overall health score (0-100)."""
        score = 0

        # Workers (40 points)
        worker_count = workers.get('count', 0)
        if worker_count >= 4:
            score += 40
        elif worker_count >= 2:
            score += 30
        elif worker_count >= 1:
            score += 20
        # 0 workers = 0 points

        # Beat scheduler (20 points)
        if beat.get('is_running'):
            score += 20

        # Queue health (20 points)
        queue_status = queues.get('status', 'error')
        if queue_status == 'normal':
            score += 20
        elif queue_status == 'high':
            score += 10
        # critical/error = 0 points

        # Task execution (20 points)
        if tasks.get('is_executing'):
            success_rate = tasks.get('success_rate_1h', 0)
            if success_rate >= 90:
                score += 20
            elif success_rate >= 70:
                score += 15
            elif success_rate >= 50:
                score += 10
            else:
                score += 5
        # Not executing = 0 points

        return score

    def _generate_alerts(
        self,
        workers: Dict,
        beat: Dict,
        queues: Dict,
        tasks: Dict,
        stale_tasks: Dict
    ) -> List[Dict]:
        """Generate alerts based on current status."""
        alerts = []

        # Critical: No workers
        if workers.get('count', 0) == 0:
            alerts.append({
                'severity': 'critical',
                'component': 'workers',
                'message': 'No Celery workers online - all scheduled tasks are blocked',
                'action': 'Run: make celery',
            })

        # Critical: Beat not running
        if not beat.get('is_running'):
            alerts.append({
                'severity': 'critical',
                'component': 'beat',
                'message': 'Celery Beat scheduler not running - no tasks will be triggered',
                'action': 'Run: celery -A core beat',
            })

        # Warning: High queue depth
        if queues.get('status') == 'critical':
            alerts.append({
                'severity': 'warning',
                'component': 'queues',
                'message': f"Queue depth critical: {queues.get('total_depth', 0)} tasks waiting",
                'action': 'Add more workers or investigate bottleneck',
            })

        # Warning: No recent task execution
        if not tasks.get('is_executing') and workers.get('count', 0) > 0:
            alerts.append({
                'severity': 'warning',
                'component': 'tasks',
                'message': 'No tasks executed in the last hour despite workers being online',
                'action': 'Check if beat is scheduling tasks correctly',
            })

        # Warning: High failure rate
        failure_rate = 100 - tasks.get('success_rate_1h', 100)
        if failure_rate > 20:
            alerts.append({
                'severity': 'warning',
                'component': 'tasks',
                'message': f"High task failure rate: {failure_rate:.1f}% in last hour",
                'action': 'Check logs for failing tasks',
            })

        # Warning: Stale critical tasks
        if stale_tasks.get('count', 0) > 0:
            for stale in stale_tasks.get('stale_tasks', [])[:3]:
                alerts.append({
                    'severity': 'warning',
                    'component': 'stale_tasks',
                    'message': f"Critical task hasn't run: {stale['task']}",
                    'action': f"Expected every {stale['expected_interval']}",
                })

        return alerts

    def get_quick_status(self) -> Dict[str, Any]:
        """Quick health check without full analysis."""
        try:
            workers = self._check_workers()
            beat = self._check_beat()

            is_healthy = workers.get('count', 0) > 0 and beat.get('is_running', False)

            return {
                'is_healthy': is_healthy,
                'workers_online': workers.get('count', 0),
                'beat_running': beat.get('is_running', False),
                'status': 'healthy' if is_healthy else 'critical',
            }
        except Exception as e:
            return {
                'is_healthy': False,
                'status': 'error',
                'error': str(e)
            }

    def ping_workers(self) -> Dict[str, bool]:
        """Ping all workers and return response map.

        Session 1103c: was 'except Exception: return {}' which silently
        returned empty when the broker auth/timeout/connection failed.
        Upstream health views interpreted "no workers" ambiguously
        (could be "actually no workers" or "ping itself broke") with
        no way to distinguish. Now logs the exception type so the
        cause is visible in monitoring.
        """
        try:
            if not self._app:
                return {}

            inspect = self._app.control.inspect(timeout=10.0)
            ping_response = inspect.ping() or {}

            return {
                worker: response.get('ok') == 'pong'
                for worker, response in ping_response.items()
            }
        except Exception as e:
            logger.warning(
                "celery_health.ping_workers: inspect.ping failed "
                "(%s: %s) — returning empty worker map. Upstream "
                "health view should treat this as 'unknown', not "
                "'no workers'.",
                type(e).__name__, e,
            )
            return {}

    def get_task_schedule(self) -> List[Dict]:
        """Get all scheduled periodic tasks."""
        try:
            from django_celery_beat.models import PeriodicTask

            tasks = PeriodicTask.objects.filter(enabled=True).order_by('name')

            return [
                {
                    'name': task.name,
                    'task': task.task,
                    'enabled': task.enabled,
                    'last_run_at': task.last_run_at.isoformat() if task.last_run_at else None,
                    'total_run_count': task.total_run_count,
                    'schedule_type': 'interval' if task.interval else ('crontab' if task.crontab else 'other'),
                }
                for task in tasks
            ]
        except Exception as e:
            return [{'error': str(e)}]


# Add missing import for models
from django.db import models
