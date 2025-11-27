"""
Workflow Analytics API Views
============================

Session 217C: REST API endpoints for workflow execution analytics.

Provides endpoints for:
- Execution history and trends
- Success/failure analysis
- Performance metrics and comparisons
- Step-level analytics
- Activity heatmaps
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.services.workflow_analytics import get_workflow_analytics_service

logger = logging.getLogger(__name__)


# =============================================================================
# EXECUTION HISTORY
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_execution_history(request):
    """
    GET /api/workflow-analytics/history/

    Get workflow execution history.

    Query params:
        days: Number of days to look back (default: 30)
        workflow_id: Filter by workflow ID
        status: Filter by status (pending, processing, completed, failed)
        limit: Maximum results (default: 100)
    """
    days = int(request.GET.get('days', 30))
    workflow_id = request.GET.get('workflow_id')
    status_filter = request.GET.get('status')
    limit = int(request.GET.get('limit', 100))

    if workflow_id:
        workflow_id = int(workflow_id)

    service = get_workflow_analytics_service(request.user)
    history = service.get_execution_history(
        days=days,
        workflow_id=workflow_id,
        status=status_filter,
        limit=limit
    )

    return Response({
        'history': history,
        'total': len(history),
        'days': days
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_execution_trends(request):
    """
    GET /api/workflow-analytics/trends/

    Get execution trends over time for Chart.js visualization.

    Query params:
        days: Number of days (default: 30)
    """
    days = int(request.GET.get('days', 30))

    service = get_workflow_analytics_service(request.user)
    trends = service.get_execution_trends(days)

    return Response(trends)


# =============================================================================
# SUCCESS/FAILURE ANALYSIS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_success_failure_analysis(request):
    """
    GET /api/workflow-analytics/success-failure/

    Get success/failure analysis with breakdown by workflow.

    Query params:
        days: Number of days (default: 30)
    """
    days = int(request.GET.get('days', 30))

    service = get_workflow_analytics_service(request.user)
    analysis = service.get_success_failure_analysis(days)

    return Response(analysis)


# =============================================================================
# PERFORMANCE METRICS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_performance_metrics(request):
    """
    GET /api/workflow-analytics/performance/

    Get detailed performance metrics for all workflows.

    Query params:
        days: Number of days (default: 30)
    """
    days = int(request.GET.get('days', 30))

    service = get_workflow_analytics_service(request.user)
    metrics = service.get_workflow_performance_metrics(days)

    return Response({
        'metrics': metrics,
        'total': len(metrics),
        'days': days
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_performance_comparison(request):
    """
    GET /api/workflow-analytics/performance-comparison/

    Get performance comparison chart data.

    Query params:
        days: Number of days (default: 30)
    """
    days = int(request.GET.get('days', 30))

    service = get_workflow_analytics_service(request.user)
    comparison = service.get_performance_comparison_chart(days)

    return Response(comparison)


# =============================================================================
# WORKFLOW COMPARISON
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compare_workflows(request):
    """
    GET /api/workflow-analytics/compare/

    Compare specific workflows side by side.

    Query params:
        workflow_ids: Comma-separated list of workflow IDs
        days: Number of days (default: 30)
    """
    workflow_ids_str = request.GET.get('workflow_ids', '')
    days = int(request.GET.get('days', 30))

    if not workflow_ids_str:
        return Response(
            {'error': 'workflow_ids parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        workflow_ids = [int(wid.strip()) for wid in workflow_ids_str.split(',')]
    except ValueError:
        return Response(
            {'error': 'Invalid workflow_ids format'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = get_workflow_analytics_service(request.user)
    comparison = service.compare_workflows(workflow_ids, days)

    return Response(comparison)


# =============================================================================
# STEP-LEVEL ANALYTICS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_step_performance(request, workflow_id):
    """
    GET /api/workflow-analytics/steps/{workflow_id}/

    Get step-level performance metrics for a specific workflow.

    Query params:
        days: Number of days (default: 30)
    """
    days = int(request.GET.get('days', 30))

    service = get_workflow_analytics_service(request.user)
    performance = service.get_step_performance(workflow_id, days)

    if 'error' in performance:
        return Response(performance, status=status.HTTP_404_NOT_FOUND)

    return Response(performance)


# =============================================================================
# ACTIVITY HEATMAP
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_execution_heatmap(request):
    """
    GET /api/workflow-analytics/heatmap/

    Get activity heatmap data for workflow executions.

    Query params:
        days: Number of days (default: 30)
    """
    days = int(request.GET.get('days', 30))

    service = get_workflow_analytics_service(request.user)
    heatmap = service.get_execution_heatmap(days)

    return Response(heatmap)


# =============================================================================
# DASHBOARD
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_summary(request):
    """
    GET /api/workflow-analytics/summary/

    Get analytics summary for the dashboard header.

    Query params:
        days: Number of days (default: 30)
    """
    days = int(request.GET.get('days', 30))

    service = get_workflow_analytics_service(request.user)
    summary = service.get_analytics_summary(days)

    return Response(summary)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_dashboard(request):
    """
    GET /api/workflow-analytics/dashboard/

    Get all analytics data for the workflow analytics dashboard.

    Query params:
        days: Number of days (default: 30)
    """
    days = int(request.GET.get('days', 30))

    service = get_workflow_analytics_service(request.user)
    dashboard_data = service.get_all_dashboard_data(days)

    return Response(dashboard_data)
