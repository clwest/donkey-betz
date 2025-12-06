"""
Workflow Analytics Service
==========================

Session 217C: Comprehensive analytics for workflow executions.

Provides:
- Execution history with detailed metrics
- Success/failure analysis
- Performance metrics per workflow
- Workflow comparison tools
- Step-level performance tracking
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypedDict
from collections import defaultdict

from django.db.models import Avg, Count, Sum, F, Q
from django.db.models.functions import TruncDate, TruncHour, ExtractHour, ExtractWeekDay
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class WorkflowMetrics(TypedDict):
    """Metrics for a single workflow"""
    workflow_id: int
    workflow_name: str
    total_executions: int
    success_rate: float
    failure_rate: float
    avg_execution_time: float
    total_execution_time: float
    pending_count: int
    processing_count: int
    completed_count: int
    failed_count: int


class ExecutionDetail(TypedDict):
    """Detailed execution information"""
    id: int
    workflow_name: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    execution_time: Optional[float]
    progress: int
    step_count: int
    current_step: int


class WorkflowAnalyticsService:
    """
    Service for workflow execution analytics.

    Provides comprehensive analytics including:
    - Execution history and trends
    - Success/failure analysis
    - Performance comparisons
    - Step-level metrics
    """

    def __init__(self, user=None):
        # Only store user if it's a real authenticated user (not AnonymousUser)
        from django.contrib.auth.models import AnonymousUser
        self.user = user if user and not isinstance(user, AnonymousUser) else None

    def _get_workflow_execution_model(self):
        """Get WorkflowExecution model lazily to avoid import issues"""
        from content.models import WorkflowExecution
        return WorkflowExecution

    def _get_content_workflow_model(self):
        """Get ContentWorkflow model lazily to avoid import issues"""
        from content.models import ContentWorkflow
        return ContentWorkflow

    def _get_base_queryset(self):
        """Get base queryset filtered by user if applicable"""
        WorkflowExecution = self._get_workflow_execution_model()
        if self.user:
            return WorkflowExecution.objects.filter(user=self.user)
        return WorkflowExecution.objects.all()

    # =========================================================================
    # EXECUTION HISTORY
    # =========================================================================

    def get_execution_history(
        self,
        days: int = 30,
        workflow_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[ExecutionDetail]:
        """
        Get detailed execution history.

        Args:
            days: Number of days to look back
            workflow_id: Filter by specific workflow
            status: Filter by status (pending, processing, completed, failed)
            limit: Maximum number of records to return

        Returns:
            List of execution details sorted by most recent
        """
        cutoff = timezone.now() - timedelta(days=days)

        qs = self._get_base_queryset().filter(
            created_at__gte=cutoff
        ).select_related('workflow')

        if workflow_id:
            qs = qs.filter(workflow_id=workflow_id)

        if status:
            qs = qs.filter(status=status)

        executions = qs.order_by('-created_at')[:limit]

        return [
            {
                'id': ex.id,
                'workflow_id': ex.workflow_id,
                'workflow_name': ex.workflow.name if ex.workflow else 'Unknown',
                'status': ex.status,
                'started_at': ex.started_at.isoformat() if ex.started_at else None,
                'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
                'execution_time': ex.execution_time_seconds,
                'progress': ex.progress_percentage,
                'step_count': len(ex.workflow.workflow_steps) if ex.workflow else 0,
                'current_step': ex.current_step,
                'created_at': ex.created_at.isoformat() if ex.created_at else None,
            }
            for ex in executions
        ]

    def get_execution_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get execution counts by day for trend visualization.

        Returns data formatted for Chart.js line chart.
        """
        cutoff = timezone.now() - timedelta(days=days)

        qs = self._get_base_queryset().filter(
            created_at__gte=cutoff
        ).annotate(
            date=TruncDate('created_at')
        ).values('date', 'status').annotate(
            count=Count('id')
        ).order_by('date')

        # Organize by date and status
        dates_data = defaultdict(lambda: {'completed': 0, 'failed': 0, 'pending': 0, 'processing': 0})

        for item in qs:
            date_str = item['date'].strftime('%Y-%m-%d') if item['date'] else 'Unknown'
            status = item['status'] or 'pending'
            dates_data[date_str][status] = item['count']

        # Sort dates
        sorted_dates = sorted(dates_data.keys())

        return {
            'type': 'line',
            'title': 'Workflow Execution Trends',
            'labels': sorted_dates,
            'datasets': [
                {
                    'label': 'Completed',
                    'data': [dates_data[d]['completed'] for d in sorted_dates],
                    'borderColor': '#28a745',
                    'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                    'fill': True,
                },
                {
                    'label': 'Failed',
                    'data': [dates_data[d]['failed'] for d in sorted_dates],
                    'borderColor': '#dc3545',
                    'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                    'fill': True,
                },
                {
                    'label': 'Processing',
                    'data': [dates_data[d]['processing'] for d in sorted_dates],
                    'borderColor': '#ffc107',
                    'backgroundColor': 'rgba(255, 193, 7, 0.1)',
                    'fill': True,
                },
            ]
        }

    # =========================================================================
    # SUCCESS/FAILURE ANALYSIS
    # =========================================================================

    def get_success_failure_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze success and failure rates across all workflows.

        Returns:
            - Overall success rate
            - Failure breakdown by workflow
            - Common failure patterns
        """
        cutoff = timezone.now() - timedelta(days=days)

        qs = self._get_base_queryset().filter(created_at__gte=cutoff)

        # Overall stats
        total = qs.count()
        completed = qs.filter(status='completed').count()
        failed = qs.filter(status='failed').count()

        success_rate = (completed / total * 100) if total > 0 else 0
        failure_rate = (failed / total * 100) if total > 0 else 0

        # Per-workflow analysis
        workflow_stats = qs.values(
            'workflow__name', 'workflow_id'
        ).annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed')),
        ).order_by('-total')[:10]

        workflow_analysis = []
        for ws in workflow_stats:
            wf_total = ws['total']
            wf_success = (ws['completed'] / wf_total * 100) if wf_total > 0 else 0
            wf_failure = (ws['failed'] / wf_total * 100) if wf_total > 0 else 0

            workflow_analysis.append({
                'workflow_id': ws['workflow_id'],
                'workflow_name': ws['workflow__name'] or 'Unknown',
                'total_executions': wf_total,
                'success_rate': round(wf_success, 1),
                'failure_rate': round(wf_failure, 1),
            })

        return {
            'overall': {
                'total_executions': total,
                'completed': completed,
                'failed': failed,
                'success_rate': round(success_rate, 1),
                'failure_rate': round(failure_rate, 1),
            },
            'by_workflow': workflow_analysis,
            'chart_data': {
                'type': 'doughnut',
                'title': 'Execution Status Distribution',
                'labels': ['Completed', 'Failed', 'In Progress', 'Pending'],
                'datasets': [{
                    'data': [
                        completed,
                        failed,
                        qs.filter(status='processing').count(),
                        qs.filter(status='pending').count(),
                    ],
                    'backgroundColor': ['#28a745', '#dc3545', '#ffc107', '#6c757d'],
                }]
            }
        }

    # =========================================================================
    # PERFORMANCE METRICS
    # =========================================================================

    def get_workflow_performance_metrics(self, days: int = 30) -> List[WorkflowMetrics]:
        """
        Get detailed performance metrics for each workflow.

        Returns metrics including execution time, success rates, etc.
        """
        cutoff = timezone.now() - timedelta(days=days)

        qs = self._get_base_queryset().filter(
            created_at__gte=cutoff
        ).values(
            'workflow_id', 'workflow__name'
        ).annotate(
            total_executions=Count('id'),
            completed_count=Count('id', filter=Q(status='completed')),
            failed_count=Count('id', filter=Q(status='failed')),
            pending_count=Count('id', filter=Q(status='pending')),
            processing_count=Count('id', filter=Q(status='processing')),
            avg_execution_time=Avg('execution_time_seconds', filter=Q(execution_time_seconds__isnull=False)),
            total_execution_time=Sum('execution_time_seconds', filter=Q(execution_time_seconds__isnull=False)),
        ).order_by('-total_executions')

        metrics = []
        for wf in qs:
            total = wf['total_executions']
            completed = wf['completed_count']
            failed = wf['failed_count']

            success_rate = (completed / total * 100) if total > 0 else 0
            failure_rate = (failed / total * 100) if total > 0 else 0

            metrics.append({
                'workflow_id': wf['workflow_id'],
                'workflow_name': wf['workflow__name'] or 'Unknown',
                'total_executions': total,
                'success_rate': round(success_rate, 1),
                'failure_rate': round(failure_rate, 1),
                'avg_execution_time': round(wf['avg_execution_time'] or 0, 2),
                'total_execution_time': round(wf['total_execution_time'] or 0, 2),
                'pending_count': wf['pending_count'],
                'processing_count': wf['processing_count'],
                'completed_count': completed,
                'failed_count': failed,
            })

        return metrics

    def get_performance_comparison_chart(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate performance comparison chart data.

        Compares workflows by execution time and success rate.
        """
        metrics = self.get_workflow_performance_metrics(days)[:10]  # Top 10

        return {
            'type': 'bar',
            'title': 'Workflow Performance Comparison',
            'labels': [m['workflow_name'][:20] for m in metrics],
            'datasets': [
                {
                    'label': 'Avg Execution Time (s)',
                    'data': [m['avg_execution_time'] for m in metrics],
                    'backgroundColor': '#007bff',
                    'yAxisID': 'y',
                },
                {
                    'label': 'Success Rate (%)',
                    'data': [m['success_rate'] for m in metrics],
                    'backgroundColor': '#28a745',
                    'yAxisID': 'y1',
                },
            ],
            'options': {
                'scales': {
                    'y': {'type': 'linear', 'position': 'left', 'title': {'text': 'Execution Time (s)'}},
                    'y1': {'type': 'linear', 'position': 'right', 'title': {'text': 'Success Rate (%)'}},
                }
            }
        }

    # =========================================================================
    # WORKFLOW COMPARISON
    # =========================================================================

    def compare_workflows(
        self,
        workflow_ids: List[int],
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Compare specific workflows side by side.

        Args:
            workflow_ids: List of workflow IDs to compare
            days: Number of days to analyze

        Returns:
            Comparison data for the specified workflows
        """
        cutoff = timezone.now() - timedelta(days=days)

        qs = self._get_base_queryset().filter(
            created_at__gte=cutoff,
            workflow_id__in=workflow_ids
        )

        ContentWorkflow = self._get_content_workflow_model()
        workflows = {
            wf.id: wf.name
            for wf in ContentWorkflow.objects.filter(id__in=workflow_ids)
        }

        comparison = {}
        for wf_id in workflow_ids:
            wf_qs = qs.filter(workflow_id=wf_id)
            total = wf_qs.count()
            completed = wf_qs.filter(status='completed').count()
            failed = wf_qs.filter(status='failed').count()

            avg_time = wf_qs.filter(
                execution_time_seconds__isnull=False
            ).aggregate(
                avg=Avg('execution_time_seconds')
            )['avg'] or 0

            comparison[wf_id] = {
                'workflow_id': wf_id,
                'workflow_name': workflows.get(wf_id, 'Unknown'),
                'total_executions': total,
                'completed': completed,
                'failed': failed,
                'success_rate': round((completed / total * 100) if total > 0 else 0, 1),
                'avg_execution_time': round(avg_time, 2),
            }

        # Generate comparison chart
        wf_names = [comparison[wf_id]['workflow_name'] for wf_id in workflow_ids]

        return {
            'workflows': comparison,
            'chart_data': {
                'type': 'radar',
                'title': 'Workflow Comparison',
                'labels': ['Executions', 'Success Rate', 'Avg Time (s)', 'Completed', 'Failed'],
                'datasets': [
                    {
                        'label': comparison[wf_id]['workflow_name'],
                        'data': [
                            comparison[wf_id]['total_executions'],
                            comparison[wf_id]['success_rate'],
                            comparison[wf_id]['avg_execution_time'],
                            comparison[wf_id]['completed'],
                            comparison[wf_id]['failed'],
                        ],
                    }
                    for wf_id in workflow_ids
                ]
            }
        }

    # =========================================================================
    # STEP-LEVEL ANALYTICS
    # =========================================================================

    def get_step_performance(self, workflow_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get performance metrics for each step of a workflow.

        Analyzes which steps are slowest and have highest failure rates.
        """
        cutoff = timezone.now() - timedelta(days=days)

        ContentWorkflow = self._get_content_workflow_model()
        try:
            workflow = ContentWorkflow.objects.get(id=workflow_id)
        except ContentWorkflow.DoesNotExist:
            return {'error': 'Workflow not found'}

        # Get executions with step results
        executions = self._get_base_queryset().filter(
            workflow_id=workflow_id,
            created_at__gte=cutoff,
            status__in=['completed', 'failed']
        )

        step_names = [
            step.get('name', f'Step {i+1}')
            for i, step in enumerate(workflow.workflow_steps)
        ]

        step_metrics = {
            name: {'total': 0, 'success': 0, 'times': []}
            for name in step_names
        }

        for ex in executions:
            step_results = ex.step_results or []
            for i, result in enumerate(step_results):
                if i < len(step_names):
                    name = step_names[i]
                    step_metrics[name]['total'] += 1
                    if result.get('success', result.get('status') == 'completed'):
                        step_metrics[name]['success'] += 1
                    if result.get('execution_time'):
                        step_metrics[name]['times'].append(result['execution_time'])

        # Calculate averages
        step_analysis = []
        for name, data in step_metrics.items():
            total = data['total']
            success_rate = (data['success'] / total * 100) if total > 0 else 0
            avg_time = sum(data['times']) / len(data['times']) if data['times'] else 0

            step_analysis.append({
                'step_name': name,
                'executions': total,
                'success_rate': round(success_rate, 1),
                'avg_time': round(avg_time, 2),
            })

        return {
            'workflow_name': workflow.name,
            'steps': step_analysis,
            'chart_data': {
                'type': 'bar',
                'title': f'Step Performance: {workflow.name}',
                'labels': [s['step_name'] for s in step_analysis],
                'datasets': [
                    {
                        'label': 'Success Rate (%)',
                        'data': [s['success_rate'] for s in step_analysis],
                        'backgroundColor': '#28a745',
                    },
                    {
                        'label': 'Avg Time (s)',
                        'data': [s['avg_time'] for s in step_analysis],
                        'backgroundColor': '#007bff',
                    },
                ]
            }
        }

    # =========================================================================
    # ACTIVITY HEATMAP
    # =========================================================================

    def get_execution_heatmap(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate heatmap of workflow execution activity by hour and day.

        Returns data suitable for Chart.js heatmap visualization.
        """
        cutoff = timezone.now() - timedelta(days=days)

        qs = self._get_base_queryset().filter(
            created_at__gte=cutoff
        ).annotate(
            hour=ExtractHour('created_at'),
            weekday=ExtractWeekDay('created_at')
        ).values('hour', 'weekday').annotate(
            count=Count('id')
        )

        # Initialize heatmap data (7 days x 24 hours)
        heatmap = [[0 for _ in range(24)] for _ in range(7)]

        for item in qs:
            weekday = item['weekday'] - 1  # Django: 1=Sunday, convert to 0=Sunday
            hour = item['hour']
            if 0 <= weekday < 7 and 0 <= hour < 24:
                heatmap[weekday][hour] = item['count']

        days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        hours = [f'{h:02d}:00' for h in range(24)]

        # Flatten for Chart.js matrix
        data_points = []
        for day_idx, day_data in enumerate(heatmap):
            for hour_idx, count in enumerate(day_data):
                data_points.append({
                    'x': hour_idx,
                    'y': day_idx,
                    'v': count
                })

        return {
            'type': 'matrix',
            'title': 'Workflow Execution Activity',
            'labels': {
                'x': hours,
                'y': days_of_week
            },
            'data': data_points,
            'heatmap': heatmap,
            'max_value': max(max(row) for row in heatmap) if any(any(row) for row in heatmap) else 0
        }

    # =========================================================================
    # DASHBOARD SUMMARY
    # =========================================================================

    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive analytics summary for dashboard.
        """
        cutoff = timezone.now() - timedelta(days=days)
        qs = self._get_base_queryset().filter(created_at__gte=cutoff)

        total = qs.count()
        completed = qs.filter(status='completed').count()
        failed = qs.filter(status='failed').count()
        processing = qs.filter(status='processing').count()

        avg_time = qs.filter(
            execution_time_seconds__isnull=False
        ).aggregate(avg=Avg('execution_time_seconds'))['avg'] or 0

        # Find most used workflow
        most_used = qs.values('workflow__name').annotate(
            count=Count('id')
        ).order_by('-count').first()

        # Find fastest workflow
        fastest = qs.filter(
            status='completed',
            execution_time_seconds__isnull=False
        ).values('workflow__name').annotate(
            avg_time=Avg('execution_time_seconds')
        ).order_by('avg_time').first()

        return {
            'period_days': days,
            'total_executions': total,
            'completed': completed,
            'failed': failed,
            'processing': processing,
            'pending': qs.filter(status='pending').count(),
            'success_rate': round((completed / total * 100) if total > 0 else 0, 1),
            'failure_rate': round((failed / total * 100) if total > 0 else 0, 1),
            'avg_execution_time': round(avg_time, 2),
            'most_used_workflow': most_used['workflow__name'] if most_used else None,
            'most_used_count': most_used['count'] if most_used else 0,
            'fastest_workflow': fastest['workflow__name'] if fastest else None,
            'fastest_time': round(fastest['avg_time'], 2) if fastest else None,
        }

    def get_all_dashboard_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Get all analytics data for the workflow analytics dashboard.
        """
        return {
            'summary': self.get_analytics_summary(days),
            'execution_trends': self.get_execution_trends(days),
            'success_failure': self.get_success_failure_analysis(days),
            'performance_comparison': self.get_performance_comparison_chart(days),
            'heatmap': self.get_execution_heatmap(days),
            'recent_executions': self.get_execution_history(days, limit=20),
            'workflow_metrics': self.get_workflow_performance_metrics(days)[:10],
        }


def get_workflow_analytics_service(user=None) -> WorkflowAnalyticsService:
    """Factory function to get WorkflowAnalyticsService instance."""
    return WorkflowAnalyticsService(user)
