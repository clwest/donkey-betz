"""
SKIN Body System Service - Project Workspace Health Monitoring

The SKIN is the boundary layer where the AI system interfaces with actual
project workspaces. This service monitors workspace health, operation success
rates, and file activity.

Session: 723

Human Body Metaphor:
    Skin Surface    = Project workspaces
    Pores           = File write operations
    Touch/Sensation = File change detection
    Healing         = Rollback capability
    Skin Health     = Workspace integrity
    Irritation      = Failed writes, permission errors
    Sweating        = High activity/throughput
"""

import logging
import time
from datetime import timedelta
from typing import Dict, List, Optional

from django.db.models import Avg, Count, Sum, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone

logger = logging.getLogger(__name__)

# Singleton instance
_skin_instance: Optional['SkinService'] = None


def get_skin_service() -> 'SkinService':
    """Get the singleton SkinService instance."""
    global _skin_instance
    if _skin_instance is None:
        _skin_instance = SkinService()
    return _skin_instance


class SkinService:
    """
    SKIN Body System - Project Workspace Health Monitoring.

    Monitors the health and activity of project workspaces where
    agents write code and execute commands.
    """

    # Health thresholds
    HEALTHY_THRESHOLD = 80.0      # >= 80% = healthy
    ACTIVE_THRESHOLD = 60.0       # >= 60% = active
    IRRITATED_THRESHOLD = 40.0    # >= 40% = irritated
    DAMAGED_THRESHOLD = 20.0      # >= 20% = damaged
    # Below 20% = critical

    # Activity thresholds (operations per hour)
    DORMANT_OPS_PER_HOUR = 1
    LOW_OPS_PER_HOUR = 5
    NORMAL_OPS_PER_HOUR = 20
    HIGH_OPS_PER_HOUR = 50
    INTENSE_OPS_PER_HOUR = 100

    def __init__(self):
        """Initialize the SKIN service."""
        logger.info("🧴 SkinService initializing...")
        self._last_check = None
        logger.info("🧴 SkinService ready")

    def feel(self, force: bool = False) -> Dict:
        """
        Run a full skin health check - the main monitoring method.

        Args:
            force: If True, bypass any caching

        Returns:
            Dict with complete skin health status
        """
        from core.models_skin import SkinPulse, SkinStatus
        from core.models_skin_layer import ProjectWorkspace, WorkspaceOperation

        logger.info("🧴 Running skin health check...")
        start_time = time.time()

        now = timezone.now()
        past_24h = now - timedelta(hours=24)
        past_1h = now - timedelta(hours=1)

        # ===== Workspace Metrics =====
        total_workspaces = ProjectWorkspace.objects.count()
        active_workspaces = ProjectWorkspace.objects.filter(is_active=True).count()

        # ===== Operation Metrics (24h) =====
        ops_24h = WorkspaceOperation.objects.filter(created_at__gte=past_24h)

        total_ops_24h = ops_24h.count()
        successful_ops_24h = ops_24h.filter(success=True).count()
        failed_ops_24h = ops_24h.filter(success=False).count()

        success_rate_24h = (
            (successful_ops_24h / total_ops_24h * 100)
            if total_ops_24h > 0 else 100.0
        )

        # Operation breakdown
        files_created_24h = ops_24h.filter(operation_type='file_create').count()
        files_modified_24h = ops_24h.filter(operation_type='file_modify').count()
        files_deleted_24h = ops_24h.filter(operation_type='file_delete').count()
        commands_executed_24h = ops_24h.filter(operation_type='command_exec').count()
        git_operations_24h = ops_24h.filter(operation_type__startswith='git_').count()

        # Size metrics
        size_metrics = ops_24h.filter(success=True).aggregate(
            total_bytes=Coalesce(Sum('file_size_after'), 0),
            avg_time=Coalesce(Avg('execution_time_ms'), 0.0),
        )
        bytes_written_24h = size_metrics['total_bytes'] or 0
        avg_operation_time_ms = size_metrics['avg_time'] or 0.0

        # Lines changed (approximate)
        lines_changed_24h = 0
        for op in ops_24h.filter(operation_type__in=['file_create', 'file_modify']):
            before_lines = len(op.file_content_before.split('\n')) if op.file_content_before else 0
            after_lines = len(op.file_content_after.split('\n')) if op.file_content_after else 0
            lines_changed_24h += abs(after_lines - before_lines)

        # ===== Rollback & Review Metrics =====
        rollbacks_available = ops_24h.filter(can_rollback=True, rolled_back=False).count()
        rollbacks_performed_24h = ops_24h.filter(rolled_back=True).count()
        pending_reviews = ops_24h.filter(requires_review=True, reviewed_by_human=False).count()

        # ===== Agent Activity =====
        agent_ops = (
            ops_24h.values('agent_name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        agent_operation_counts = {a['agent_name']: a['count'] for a in agent_ops}
        active_agents = len(agent_operation_counts)
        most_active_agent = agent_ops[0]['agent_name'] if agent_ops else ''

        # ===== Recent Errors =====
        recent_errors = list(
            ops_24h.filter(success=False)
            .order_by('-created_at')[:5]
            .values('operation_type', 'file_path', 'error_message', 'agent_name', 'created_at')
        )
        # Convert datetime to string for JSON serialization
        for error in recent_errors:
            error['created_at'] = error['created_at'].isoformat() if error['created_at'] else None

        permission_denials = ops_24h.filter(
            error_message__icontains='permission'
        ).count()

        # ===== Activity Level =====
        ops_1h = WorkspaceOperation.objects.filter(created_at__gte=past_1h).count()
        operations_per_hour = ops_1h

        if operations_per_hour <= self.DORMANT_OPS_PER_HOUR:
            activity_level = 'dormant'
        elif operations_per_hour <= self.LOW_OPS_PER_HOUR:
            activity_level = 'low'
        elif operations_per_hour <= self.NORMAL_OPS_PER_HOUR:
            activity_level = 'normal'
        elif operations_per_hour <= self.HIGH_OPS_PER_HOUR:
            activity_level = 'high'
        else:
            activity_level = 'intense'

        # ===== Calculate Health Score =====
        health_score = self._calculate_health_score(
            success_rate_24h=success_rate_24h,
            total_ops_24h=total_ops_24h,
            failed_ops_24h=failed_ops_24h,
            permission_denials=permission_denials,
            pending_reviews=pending_reviews,
        )

        # ===== Determine Status =====
        status = self._determine_status(
            health_score=health_score,
            activity_level=activity_level,
            rollbacks_performed_24h=rollbacks_performed_24h,
            total_ops_24h=total_ops_24h,
        )

        is_healthy = health_score >= self.HEALTHY_THRESHOLD

        # ===== Last Activity Times =====
        last_op = ops_24h.order_by('-created_at').first()
        last_successful_op = ops_24h.filter(success=True).order_by('-created_at').first()
        last_error_op = ops_24h.filter(success=False).order_by('-created_at').first()

        last_operation_at = last_op.created_at if last_op else None
        last_successful_operation_at = last_successful_op.created_at if last_successful_op else None
        last_error_at = last_error_op.created_at if last_error_op else None

        # ===== Calculate Check Duration =====
        check_duration_ms = int((time.time() - start_time) * 1000)

        # ===== Record Pulse =====
        pulse = SkinPulse.objects.create(
            status=status,
            health_score=health_score,
            total_workspaces=total_workspaces,
            active_workspaces=active_workspaces,
            workspaces_with_errors=0,  # TODO: Calculate this
            operations_24h=total_ops_24h,
            successful_operations_24h=successful_ops_24h,
            failed_operations_24h=failed_ops_24h,
            success_rate_24h=success_rate_24h,
            files_created_24h=files_created_24h,
            files_modified_24h=files_modified_24h,
            files_deleted_24h=files_deleted_24h,
            commands_executed_24h=commands_executed_24h,
            git_operations_24h=git_operations_24h,
            bytes_written_24h=bytes_written_24h,
            lines_changed_24h=lines_changed_24h,
            avg_operation_time_ms=avg_operation_time_ms,
            rollbacks_available=rollbacks_available,
            rollbacks_performed_24h=rollbacks_performed_24h,
            pending_reviews=pending_reviews,
            active_agents=active_agents,
            most_active_agent=most_active_agent,
            agent_operation_counts=agent_operation_counts,
            recent_errors=recent_errors,
            permission_denials=permission_denials,
            check_duration_ms=check_duration_ms,
        )

        # ===== Update Cached Status =====
        skin_status = SkinStatus.get_current()
        skin_status.status = status
        skin_status.is_healthy = is_healthy
        skin_status.health_score = health_score
        skin_status.total_workspaces = total_workspaces
        skin_status.active_workspaces = active_workspaces
        skin_status.total_operations_all_time = WorkspaceOperation.objects.count()
        skin_status.operations_24h = total_ops_24h
        skin_status.success_rate_24h = success_rate_24h
        skin_status.files_touched_24h = files_created_24h + files_modified_24h + files_deleted_24h
        skin_status.bytes_written_24h = bytes_written_24h
        skin_status.activity_level = activity_level
        skin_status.operations_per_hour = operations_per_hour
        skin_status.error_rate_24h = 100 - success_rate_24h
        skin_status.avg_operation_time_ms = avg_operation_time_ms
        skin_status.rollbacks_available = rollbacks_available
        skin_status.pending_reviews = pending_reviews
        skin_status.last_operation_at = last_operation_at
        skin_status.last_successful_operation_at = last_successful_operation_at
        skin_status.last_error_at = last_error_at
        skin_status.save()

        self._last_check = now

        logger.info(f"🧴 Skin check complete: {status} ({health_score}%) - {check_duration_ms}ms")

        return {
            'timestamp': now.isoformat(),
            'status': status,
            'health_score': health_score,
            'is_healthy': is_healthy,
            'check_duration_ms': check_duration_ms,
            'workspaces': {
                'total': total_workspaces,
                'active': active_workspaces,
            },
            'operations_24h': {
                'total': total_ops_24h,
                'successful': successful_ops_24h,
                'failed': failed_ops_24h,
                'success_rate': round(success_rate_24h, 1),
            },
            'file_activity_24h': {
                'created': files_created_24h,
                'modified': files_modified_24h,
                'deleted': files_deleted_24h,
                'commands': commands_executed_24h,
                'git_ops': git_operations_24h,
                'bytes_written': bytes_written_24h,
                'lines_changed': lines_changed_24h,
            },
            'activity': {
                'level': activity_level,
                'ops_per_hour': operations_per_hour,
                'avg_op_time_ms': round(avg_operation_time_ms, 1),
            },
            'healing': {
                'rollbacks_available': rollbacks_available,
                'rollbacks_performed_24h': rollbacks_performed_24h,
                'pending_reviews': pending_reviews,
            },
            'agents': {
                'active_count': active_agents,
                'most_active': most_active_agent,
                'operation_counts': agent_operation_counts,
            },
            'issues': {
                'recent_errors': recent_errors,
                'permission_denials': permission_denials,
            },
            'timestamps': {
                'last_operation': last_operation_at.isoformat() if last_operation_at else None,
                'last_success': last_successful_operation_at.isoformat() if last_successful_operation_at else None,
                'last_error': last_error_at.isoformat() if last_error_at else None,
            },
        }

    def _calculate_health_score(
        self,
        success_rate_24h: float,
        total_ops_24h: int,
        failed_ops_24h: int,
        permission_denials: int,
        pending_reviews: int,
    ) -> float:
        """Calculate overall skin health score (0-100)."""

        # Base score from success rate (50% weight)
        score = success_rate_24h * 0.5

        # Penalty for failed operations (20% weight)
        if total_ops_24h > 0:
            failure_penalty = min(failed_ops_24h * 2, 20)  # Max 20 point penalty
            score += (20 - failure_penalty)
        else:
            score += 20  # No operations = no failures

        # Penalty for permission denials (15% weight)
        permission_penalty = min(permission_denials * 5, 15)  # Max 15 point penalty
        score += (15 - permission_penalty)

        # Penalty for pending reviews (15% weight)
        review_penalty = min(pending_reviews * 3, 15)  # Max 15 point penalty
        score += (15 - review_penalty)

        return max(0, min(100, score))

    def _determine_status(
        self,
        health_score: float,
        activity_level: str,
        rollbacks_performed_24h: int,
        total_ops_24h: int,
    ) -> str:
        """Determine the skin status based on metrics."""

        # If rollbacks are happening, we're healing
        if rollbacks_performed_24h > 0:
            return 'healing'

        # If no operations, we're dormant
        if total_ops_24h == 0:
            return 'dormant'

        # High activity with good health = sweating
        if activity_level in ['high', 'intense'] and health_score >= self.ACTIVE_THRESHOLD:
            return 'sweating'

        # Health-based status
        if health_score >= self.HEALTHY_THRESHOLD:
            return 'healthy' if activity_level in ['dormant', 'low', 'normal'] else 'active'
        elif health_score >= self.ACTIVE_THRESHOLD:
            return 'active'
        elif health_score >= self.IRRITATED_THRESHOLD:
            return 'irritated'
        elif health_score >= self.DAMAGED_THRESHOLD:
            return 'damaged'
        else:
            return 'damaged'

    def is_healthy(self) -> bool:
        """Quick check - is the skin healthy?"""
        from core.models_skin import SkinStatus

        status = SkinStatus.get_current()
        return status.is_healthy

    def get_vitals(self) -> Dict:
        """Get current skin vitals (cached status)."""
        from core.models_skin import SkinStatus

        status = SkinStatus.get_current()
        return {
            'status': status.status,
            'health_score': status.health_score,
            'is_healthy': status.is_healthy,
            'total_workspaces': status.total_workspaces,
            'active_workspaces': status.active_workspaces,
            'operations_24h': status.operations_24h,
            'success_rate_24h': status.success_rate_24h,
            'activity_level': status.activity_level,
            'ops_per_hour': status.operations_per_hour,
            'last_check': status.last_check.isoformat() if status.last_check else None,
            'last_operation': status.last_operation_at.isoformat() if status.last_operation_at else None,
        }

    def get_status(self) -> Dict:
        """Get current skin status with full details."""
        from core.models_skin import SkinStatus

        status = SkinStatus.get_current()
        return {
            'timestamp': timezone.now().isoformat(),
            'status': status.status,
            'health_score': status.health_score,
            'is_healthy': status.is_healthy,
            'workspaces': {
                'total': status.total_workspaces,
                'active': status.active_workspaces,
            },
            'operations': {
                'total_all_time': status.total_operations_all_time,
                'count_24h': status.operations_24h,
                'success_rate_24h': status.success_rate_24h,
                'error_rate_24h': status.error_rate_24h,
                'files_touched_24h': status.files_touched_24h,
                'bytes_written_24h': status.bytes_written_24h,
            },
            'activity': {
                'level': status.activity_level,
                'ops_per_hour': status.operations_per_hour,
                'avg_op_time_ms': status.avg_operation_time_ms,
            },
            'healing': {
                'rollbacks_available': status.rollbacks_available,
                'pending_reviews': status.pending_reviews,
            },
            'timestamps': {
                'last_check': status.last_check.isoformat() if status.last_check else None,
                'last_operation': status.last_operation_at.isoformat() if status.last_operation_at else None,
                'last_success': status.last_successful_operation_at.isoformat() if status.last_successful_operation_at else None,
                'last_error': status.last_error_at.isoformat() if status.last_error_at else None,
            },
        }

    def get_history(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get skin pulse history."""
        from core.models_skin import SkinPulse

        since = timezone.now() - timedelta(hours=hours)
        pulses = SkinPulse.objects.filter(recorded_at__gte=since).order_by('-recorded_at')[:limit]

        return [
            {
                'timestamp': p.recorded_at.isoformat(),
                'status': p.status,
                'health_score': p.health_score,
                'operations_24h': p.operations_24h,
                'success_rate_24h': p.success_rate_24h,
                'activity_level': 'high' if p.operations_24h > 50 else 'normal',
                'active_agents': p.active_agents,
            }
            for p in pulses
        ]

    def get_workspaces_summary(self) -> List[Dict]:
        """Get summary of all workspaces and their health."""
        from core.models_skin_layer import ProjectWorkspace, WorkspaceOperation

        workspaces = ProjectWorkspace.objects.all()
        past_24h = timezone.now() - timedelta(hours=24)

        summaries = []
        for ws in workspaces:
            ops = WorkspaceOperation.objects.filter(workspace=ws, created_at__gte=past_24h)
            total = ops.count()
            successful = ops.filter(success=True).count()
            success_rate = (successful / total * 100) if total > 0 else 100.0

            summaries.append({
                'id': str(ws.id),
                'name': ws.name,
                'root_path': ws.root_path,
                'is_active': ws.is_active,
                'workspace_type': ws.workspace_type,
                'operations_24h': total,
                'success_rate_24h': round(success_rate, 1),
                'total_operations': ws.total_operations,
                'last_operation': ws.last_operation_at.isoformat() if ws.last_operation_at else None,
            })

        return summaries
