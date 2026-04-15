"""
Status Overview API — Platform health + deploy info for frontend dashboard.

GET /api/status/overview/ — Returns backend SHA, uptime, worker health,
queue depths, last deploy timestamp, and key metrics.
"""

import logging
import os
import time
from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

logger = logging.getLogger(__name__)

_PROCESS_START = time.time()


@api_view(["GET"])
def status_overview(request):
    """Platform status overview for dashboard display."""
    from django_celery_beat.models import PeriodicTask

    # Deploy info
    build_sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "dev")[:8]
    deploy_id = os.environ.get("RAILWAY_DEPLOYMENT_ID", "local")
    service = os.environ.get("RAILWAY_SERVICE_NAME", "local")

    # Uptime
    uptime_seconds = int(time.time() - _PROCESS_START)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {secs}s"

    # Worker + queue health (lightweight — no celery inspect call).
    # Session 1103c: each of the four 'except Exception: ...' blocks
    # below was silently masking real DB / import / schema failures
    # and returning a "perfectly clean zero state" to status callers.
    # The /status/ endpoint feeds dashboards + automated monitors; a
    # silent zero looks identical to "system idle" and breaks
    # incident detection. Each block now logs WARNING with the
    # subsystem name + exception type while keeping the safe
    # zero-default behavior so the endpoint never 500s.
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        last_24h = timezone.now() - timedelta(hours=24)
        task_stats = CeleryTaskEvent.objects.filter(
            started_at__gte=last_24h
        ).values("status").annotate(count=Count("id"))
        tasks_24h = {s["status"]: s["count"] for s in task_stats}
    except Exception as e:
        logger.warning(
            "views_status_api: CeleryTaskEvent 24h stats failed "
            "(%s: %s) — returning empty tasks_24h",
            type(e).__name__, e,
        )
        tasks_24h = {}

    # Active beat tasks
    try:
        beat_count = PeriodicTask.objects.filter(enabled=True).count()
    except Exception as e:
        logger.warning(
            "views_status_api: PeriodicTask count failed "
            "(%s: %s) — returning beat_count=0",
            type(e).__name__, e,
        )
        beat_count = 0

    # Revenue snapshot
    try:
        from core.models import Revenue, Opportunity
        from django.db.models import Sum, Count
        total_revenue = Revenue.objects.filter(status="confirmed").aggregate(
            total=Sum("amount")
        )["total"] or 0
        opportunity_counts = {
            "total": Opportunity.objects.count(),
            "new": Opportunity.objects.filter(status="new").count(),
        }
    except Exception as e:
        logger.warning(
            "views_status_api: Revenue/Opportunity snapshot failed "
            "(%s: %s) — returning zero revenue + zero opportunities",
            type(e).__name__, e,
        )
        total_revenue = 0
        opportunity_counts = {"total": 0, "new": 0}

    # Preview system
    try:
        from core.models_preview_system import PreviewEnvironment, WorkspaceProject
        project_count = WorkspaceProject.objects.count()
        active_envs = PreviewEnvironment.objects.filter(
            status__in=["provisioning", "ready"]
        ).count()
    except Exception as e:
        logger.warning(
            "views_status_api: Preview system snapshot failed "
            "(%s: %s) — returning zero projects + zero active envs",
            type(e).__name__, e,
        )
        project_count = 0
        active_envs = 0

    return Response({
        "deploy": {
            "sha": build_sha,
            "deployment_id": deploy_id,
            "service": service,
            "uptime": uptime_str,
            "uptime_seconds": uptime_seconds,
        },
        "celery": {
            "tasks_24h": tasks_24h,
            "beat_schedules": beat_count,
        },
        "revenue": {
            "total_confirmed": float(total_revenue),
            "opportunities": opportunity_counts,
        },
        "preview_system": {
            "projects": project_count,
            "active_environments": active_envs,
        },
        "timestamp": timezone.now().isoformat(),
    })


@api_view(["GET"])
def tool_metrics(request):
    """Tool call metrics from Redis counters. Optional ?date=YYYY-MM-DD param."""
    from core.services.tool_dispatcher import get_tool_metrics
    day = request.query_params.get("date")
    return Response(get_tool_metrics(day))
