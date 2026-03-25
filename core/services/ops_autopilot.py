"""
Ops Autopilot — automated system health monitoring and remediation.

Runs on a Celery beat schedule. Checks for common failure conditions
and takes corrective action:
- Stuck Celery tasks (STARTED but no finish for >30 min) → revoke
- Crashed Railway services → restart via railway_tool
- Queue saturation (>10 tasks waiting) → log alert
- Worker health degradation → log alert

All actions are logged and non-destructive (revoke is safe, restart
is safe). Never modifies data or code.
"""

import logging
from datetime import timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Thresholds
STUCK_TASK_MINUTES = 30
QUEUE_BACKLOG_THRESHOLD = 10
MAX_REVOKES_PER_RUN = 3


class OpsAutopilot:
    """Automated ops monitoring and lightweight remediation."""

    def run(self) -> Dict[str, Any]:
        """Run a full autopilot cycle. Returns summary of findings and actions."""
        actions: List[Dict[str, Any]] = []
        findings: List[str] = []

        # 1. Check for stuck tasks
        try:
            stuck_actions = self._check_stuck_tasks()
            actions.extend(stuck_actions)
            if stuck_actions:
                findings.append(f"Found and revoked {len(stuck_actions)} stuck task(s)")
        except Exception as e:
            logger.error(f"[OpsAutopilot] Stuck task check failed: {e}")
            findings.append(f"Stuck task check error: {e}")

        # 2. Check queue depths
        try:
            queue_findings = self._check_queue_health()
            findings.extend(queue_findings)
        except Exception as e:
            logger.error(f"[OpsAutopilot] Queue health check failed: {e}")
            findings.append(f"Queue health check error: {e}")

        # 3. Check Railway service health
        try:
            service_actions = self._check_railway_services()
            actions.extend(service_actions)
            if service_actions:
                findings.append(f"Restarted {len(service_actions)} crashed service(s)")
        except Exception as e:
            logger.debug(f"[OpsAutopilot] Railway check skipped: {e}")

        # 4. Check worker health
        try:
            worker_findings = self._check_worker_health()
            findings.extend(worker_findings)
        except Exception as e:
            logger.error(f"[OpsAutopilot] Worker health check failed: {e}")

        result = {
            'actions_taken': len(actions),
            'actions': actions,
            'findings': findings,
        }

        if actions:
            logger.info(f"[OpsAutopilot] Cycle complete: {len(actions)} actions taken, {len(findings)} findings")
        else:
            logger.debug(f"[OpsAutopilot] Cycle complete: no actions needed, {len(findings)} findings")

        return result

    def _check_stuck_tasks(self) -> List[Dict[str, Any]]:
        """Find and revoke tasks stuck in STARTED state for too long."""
        from core.models_celery_telemetry import CeleryTaskEvent
        from django.utils import timezone

        cutoff = timezone.now() - timedelta(minutes=STUCK_TASK_MINUTES)
        stuck = CeleryTaskEvent.objects.filter(
            status='STARTED',
            finished_at__isnull=True,
            started_at__lte=cutoff,
        ).order_by('started_at')[:MAX_REVOKES_PER_RUN]

        actions = []
        for event in stuck:
            age_min = (timezone.now() - event.started_at).total_seconds() / 60
            try:
                from core.celery import app as celery_app
                celery_app.control.revoke(event.task_id, terminate=True)
                event.status = 'REVOKED'
                event.save(update_fields=['status'])
                actions.append({
                    'type': 'revoke_stuck_task',
                    'task_id': event.task_id,
                    'task_name': event.task_name,
                    'queue': event.queue,
                    'age_minutes': round(age_min),
                    'worker': event.worker,
                })
                logger.warning(
                    f"[OpsAutopilot] Revoked stuck task {event.task_name} "
                    f"(age={age_min:.0f}min, worker={event.worker})"
                )
            except Exception as e:
                logger.error(f"[OpsAutopilot] Failed to revoke {event.task_id}: {e}")

        return actions

    def _check_queue_health(self) -> List[str]:
        """Check for queue saturation."""
        findings = []
        try:
            from core.celery import app as celery_app
            inspector = celery_app.control.inspect(timeout=5)
            active = inspector.active() or {}
            reserved = inspector.reserved() or {}

            # Count active + reserved per queue
            queue_load: Dict[str, int] = {}
            for worker_tasks in list(active.values()) + list(reserved.values()):
                for task in (worker_tasks or []):
                    q = task.get('delivery_info', {}).get('routing_key', 'unknown')
                    queue_load[q] = queue_load.get(q, 0) + 1

            for queue, count in sorted(queue_load.items(), key=lambda x: -x[1]):
                if count >= QUEUE_BACKLOG_THRESHOLD:
                    findings.append(f"Queue '{queue}' has {count} tasks (threshold: {QUEUE_BACKLOG_THRESHOLD})")
                    logger.warning(f"[OpsAutopilot] Queue saturation: {queue}={count}")

        except Exception as e:
            logger.debug(f"[OpsAutopilot] Queue inspection failed: {e}")

        return findings

    def _check_railway_services(self) -> List[Dict[str, Any]]:
        """Check for crashed Railway services and restart them."""
        actions = []
        try:
            from core.services.td_handlers_railway import list_services, restart_service

            result = list_services()
            if 'error' in result:
                return actions

            for svc in result.get('services', []):
                if svc.get('status') in ('CRASHED', 'FAILED'):
                    name = svc['name']
                    # Don't auto-restart databases or beat
                    if name in ('Redis', 'pgvector', 'celery-beat'):
                        logger.warning(f"[OpsAutopilot] {name} is {svc['status']} — skipping auto-restart (critical service)")
                        continue

                    restart_result = restart_service(name)
                    if 'error' not in restart_result:
                        actions.append({
                            'type': 'restart_crashed_service',
                            'service': name,
                            'previous_status': svc['status'],
                        })
                        logger.warning(f"[OpsAutopilot] Restarted crashed service: {name}")
                    else:
                        logger.error(f"[OpsAutopilot] Failed to restart {name}: {restart_result.get('error')}")

        except Exception as e:
            logger.debug(f"[OpsAutopilot] Railway service check failed: {e}")

        return actions

    def _check_worker_health(self) -> List[str]:
        """Check if expected workers are online."""
        findings = []
        try:
            from core.celery import app as celery_app
            inspector = celery_app.control.inspect(timeout=5)
            stats = inspector.stats() or {}

            worker_count = len(stats)
            # We expect at least 6 workers (worker, pa, content, long-running, broadcast, long-running-2)
            if worker_count < 6:
                findings.append(f"Only {worker_count} workers online (expected 6+)")
                logger.warning(f"[OpsAutopilot] Low worker count: {worker_count}")

        except Exception as e:
            logger.debug(f"[OpsAutopilot] Worker stats unavailable: {e}")

        return findings
