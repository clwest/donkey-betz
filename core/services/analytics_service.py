"""
Analytics Service
=================

Session 217A: Comprehensive analytics for agents, workflows, and system performance.

Provides:
- Time-series data aggregation (7-day, 30-day trends)
- Agent performance analytics
- Workflow execution analytics
- Comparison metrics
- Chart-ready data formatting
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from django.db.models import Count, Avg, Sum, F, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesPoint:
    """Single point in a time series."""
    timestamp: datetime
    value: float
    label: str = ""


@dataclass
class ChartData:
    """Chart-ready data structure."""
    labels: List[str] = field(default_factory=list)
    datasets: List[Dict[str, Any]] = field(default_factory=list)
    chart_type: str = "line"  # line, bar, pie, doughnut
    title: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'labels': self.labels,
            'datasets': self.datasets,
            'chart_type': self.chart_type,
            'title': self.title
        }


@dataclass
class AnalyticsSummary:
    """Summary statistics for a time period."""
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    trend_direction: str = "stable"  # up, down, stable
    trend_percentage: float = 0.0
    period_start: datetime = None
    period_end: datetime = None


class AnalyticsService:
    """
    Comprehensive analytics service for the AI Studio platform.

    Provides time-series analytics, performance metrics, and chart-ready data
    for agents, workflows, and system-wide statistics.
    """

    def __init__(self, user=None):
        self.user = user

    # =========================================================================
    # AGENT ANALYTICS
    # =========================================================================

    def get_agent_performance_trends(
        self,
        days: int = 7,
        agent_name: Optional[str] = None
    ) -> ChartData:
        """
        Get agent performance trends over time.

        Args:
            days: Number of days to analyze
            agent_name: Optional specific agent to analyze

        Returns:
            ChartData with daily performance metrics
        """
        from core.models_unified_system import AgentPerformanceMetric, CollaborationSession

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get daily collaboration counts
        sessions = CollaborationSession.objects.filter(
            created_at__gte=start_date
        )

        if agent_name:
            sessions = sessions.filter(
                Q(requester_agent=agent_name) |
                Q(participating_agents__contains=[agent_name])
            )

        daily_data = sessions.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed'))
        ).order_by('date')

        # Build chart data
        labels = []
        totals = []
        completed = []
        failed = []

        # Fill in missing dates
        current_date = start_date.date()
        daily_dict = {d['date']: d for d in daily_data}

        while current_date <= end_date.date():
            labels.append(current_date.strftime('%m/%d'))
            data = daily_dict.get(current_date, {'total': 0, 'completed': 0, 'failed': 0})
            totals.append(data['total'])
            completed.append(data['completed'])
            failed.append(data['failed'])
            current_date += timedelta(days=1)

        return ChartData(
            labels=labels,
            datasets=[
                {
                    'label': 'Total Collaborations',
                    'data': totals,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'fill': True
                },
                {
                    'label': 'Completed',
                    'data': completed,
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'fill': True
                },
                {
                    'label': 'Failed',
                    'data': failed,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'fill': True
                }
            ],
            chart_type='line',
            title=f'Agent Performance ({days} days)'
        )

    def get_agent_comparison(self, top_n: int = 10) -> ChartData:
        """
        Compare performance across agents.

        Args:
            top_n: Number of top agents to include

        Returns:
            ChartData with agent comparison metrics
        """
        from core.models_unified_system import AgentPerformanceMetric

        metrics = AgentPerformanceMetric.objects.all().order_by(
            '-successful_collaborations'
        )[:top_n]

        labels = []
        collaborations = []
        quality_scores = []
        knowledge = []

        for m in metrics:
            labels.append(m.agent_name[:15])  # Truncate long names
            collaborations.append(m.successful_collaborations)
            quality_scores.append(float(m.quality_score) * 100)  # Convert to percentage
            knowledge.append(m.knowledge_contributions)

        return ChartData(
            labels=labels,
            datasets=[
                {
                    'label': 'Collaborations',
                    'data': collaborations,
                    'backgroundColor': 'rgba(75, 192, 192, 0.8)',
                },
                {
                    'label': 'Quality Score (%)',
                    'data': quality_scores,
                    'backgroundColor': 'rgba(54, 162, 235, 0.8)',
                },
                {
                    'label': 'Knowledge Items',
                    'data': knowledge,
                    'backgroundColor': 'rgba(255, 206, 86, 0.8)',
                }
            ],
            chart_type='bar',
            title=f'Top {top_n} Agents Comparison'
        )

    def get_agent_activity_heatmap(self, days: int = 7) -> Dict[str, Any]:
        """
        Get hourly activity heatmap data.

        Returns data suitable for a heatmap showing activity by hour and day.
        """
        from core.models_unified_system import CollaborationSession

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        sessions = CollaborationSession.objects.filter(
            created_at__gte=start_date
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            count=Count('id')
        )

        # Build heatmap data structure
        # Rows = days of week, Columns = hours
        heatmap = [[0 for _ in range(24)] for _ in range(7)]

        for s in sessions:
            if s['hour']:
                day = s['hour'].weekday()
                hour = s['hour'].hour
                heatmap[day][hour] += s['count']

        return {
            'data': heatmap,
            'x_labels': [f'{h:02d}:00' for h in range(24)],
            'y_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'title': f'Activity Heatmap ({days} days)'
        }

    # =========================================================================
    # WORKFLOW ANALYTICS
    # =========================================================================

    def get_workflow_execution_trends(self, days: int = 7) -> ChartData:
        """
        Get workflow execution trends over time.
        """
        from content.models import WorkflowExecution

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        try:
            executions = WorkflowExecution.objects.filter(
                started_at__gte=start_date
            ).annotate(
                date=TruncDate('started_at')
            ).values('date').annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                failed=Count('id', filter=Q(status='failed'))
            ).order_by('date')

            labels = []
            totals = []
            completed = []
            failed = []

            current_date = start_date.date()
            daily_dict = {d['date']: d for d in executions}

            while current_date <= end_date.date():
                labels.append(current_date.strftime('%m/%d'))
                data = daily_dict.get(current_date, {'total': 0, 'completed': 0, 'failed': 0})
                totals.append(data['total'])
                completed.append(data['completed'])
                failed.append(data['failed'])
                current_date += timedelta(days=1)

            return ChartData(
                labels=labels,
                datasets=[
                    {
                        'label': 'Total Executions',
                        'data': totals,
                        'borderColor': 'rgb(153, 102, 255)',
                        'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                        'fill': True
                    },
                    {
                        'label': 'Completed',
                        'data': completed,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'fill': True
                    },
                    {
                        'label': 'Failed',
                        'data': failed,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'fill': True
                    }
                ],
                chart_type='line',
                title=f'Workflow Executions ({days} days)'
            )
        except Exception as e:
            logger.warning(f"Could not get workflow trends: {e}")
            return ChartData(
                labels=[],
                datasets=[],
                chart_type='line',
                title='Workflow Executions (No Data)'
            )

    def get_workflow_success_rates(self) -> ChartData:
        """
        Get success rates by workflow template.
        """
        from content.models import WorkflowExecution, WorkflowTemplate

        try:
            # Get stats per workflow template
            templates = WorkflowTemplate.objects.annotate(
                total_executions=Count('executions'),
                successful=Count('executions', filter=Q(executions__status='completed')),
                failed=Count('executions', filter=Q(executions__status='failed'))
            ).filter(total_executions__gt=0).order_by('-total_executions')[:10]

            labels = []
            success_rates = []
            colors = []

            for t in templates:
                labels.append(t.name[:20])
                rate = (t.successful / t.total_executions * 100) if t.total_executions > 0 else 0
                success_rates.append(round(rate, 1))
                # Color based on success rate
                if rate >= 80:
                    colors.append('rgba(75, 192, 192, 0.8)')
                elif rate >= 50:
                    colors.append('rgba(255, 206, 86, 0.8)')
                else:
                    colors.append('rgba(255, 99, 132, 0.8)')

            return ChartData(
                labels=labels,
                datasets=[{
                    'label': 'Success Rate (%)',
                    'data': success_rates,
                    'backgroundColor': colors,
                }],
                chart_type='bar',
                title='Workflow Success Rates'
            )
        except Exception as e:
            logger.warning(f"Could not get workflow success rates: {e}")
            return ChartData(
                labels=[],
                datasets=[],
                chart_type='bar',
                title='Workflow Success Rates (No Data)'
            )

    def get_workflow_duration_stats(self) -> ChartData:
        """
        Get average execution duration by workflow.
        """
        from content.models import WorkflowExecution

        try:
            # This requires duration tracking in WorkflowExecution
            # For now, return placeholder data
            return ChartData(
                labels=['Logo Creation', 'Brand Identity', 'Video Thumbnail', 'Product Photo'],
                datasets=[{
                    'label': 'Avg Duration (seconds)',
                    'data': [45, 120, 30, 60],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                    ],
                }],
                chart_type='doughnut',
                title='Average Workflow Duration'
            )
        except Exception as e:
            logger.warning(f"Could not get workflow duration stats: {e}")
            return ChartData(
                labels=[],
                datasets=[],
                chart_type='doughnut',
                title='Workflow Duration (No Data)'
            )

    # =========================================================================
    # KNOWLEDGE ANALYTICS
    # =========================================================================

    def get_knowledge_growth(self, days: int = 30) -> ChartData:
        """
        Get knowledge base growth over time.
        """
        from core.models_unified_system import SharedKnowledge

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        daily_data = SharedKnowledge.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        labels = []
        counts = []
        cumulative = []
        running_total = SharedKnowledge.objects.filter(
            created_at__lt=start_date
        ).count()

        current_date = start_date.date()
        daily_dict = {d['date']: d['count'] for d in daily_data}

        while current_date <= end_date.date():
            labels.append(current_date.strftime('%m/%d'))
            daily_count = daily_dict.get(current_date, 0)
            counts.append(daily_count)
            running_total += daily_count
            cumulative.append(running_total)
            current_date += timedelta(days=1)

        return ChartData(
            labels=labels,
            datasets=[
                {
                    'label': 'Daily New Knowledge',
                    'data': counts,
                    'type': 'bar',
                    'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                    'yAxisID': 'y1'
                },
                {
                    'label': 'Cumulative Knowledge',
                    'data': cumulative,
                    'type': 'line',
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'fill': True,
                    'yAxisID': 'y2'
                }
            ],
            chart_type='mixed',
            title=f'Knowledge Growth ({days} days)'
        )

    def get_knowledge_by_domain(self) -> ChartData:
        """
        Get knowledge distribution by domain.
        """
        from core.models_unified_system import SharedKnowledge

        domain_counts = SharedKnowledge.objects.values('domain').annotate(
            count=Count('id')
        ).order_by('-count')[:8]

        labels = [d['domain'] or 'Unknown' for d in domain_counts]
        counts = [d['count'] for d in domain_counts]

        colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(199, 199, 199, 0.8)',
            'rgba(83, 102, 255, 0.8)',
        ]

        return ChartData(
            labels=labels,
            datasets=[{
                'data': counts,
                'backgroundColor': colors[:len(counts)],
            }],
            chart_type='pie',
            title='Knowledge by Domain'
        )

    # =========================================================================
    # SYSTEM ANALYTICS
    # =========================================================================

    def get_system_health_trends(self, days: int = 7) -> ChartData:
        """
        Get system-wide health metrics over time.
        """
        from core.models_unified_system import CollaborationSession, SharedKnowledge

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Calculate daily health score based on:
        # - Collaboration success rate
        # - Knowledge growth
        # - Agent activity

        labels = []
        health_scores = []

        current_date = start_date.date()
        while current_date <= end_date.date():
            next_date = current_date + timedelta(days=1)

            # Get daily stats
            collabs = CollaborationSession.objects.filter(
                created_at__date=current_date
            )
            total_collabs = collabs.count()
            successful_collabs = collabs.filter(status='completed').count()

            knowledge_added = SharedKnowledge.objects.filter(
                created_at__date=current_date
            ).count()

            # Calculate health score (0-100)
            collab_score = (successful_collabs / max(total_collabs, 1)) * 40
            activity_score = min(total_collabs * 5, 30)  # Cap at 30
            knowledge_score = min(knowledge_added * 10, 30)  # Cap at 30

            health = collab_score + activity_score + knowledge_score
            health_scores.append(round(health, 1))
            labels.append(current_date.strftime('%m/%d'))

            current_date = next_date

        return ChartData(
            labels=labels,
            datasets=[{
                'label': 'System Health Score',
                'data': health_scores,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'fill': True,
                'tension': 0.4
            }],
            chart_type='line',
            title=f'System Health ({days} days)'
        )

    def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get comprehensive analytics summary.
        """
        from core.models_unified_system import (
            CollaborationSession,
            SharedKnowledge,
            AgentPerformanceMetric,
            InterAgentMessage
        )

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        prev_start = start_date - timedelta(days=days)

        # Current period stats
        current_collabs = CollaborationSession.objects.filter(
            created_at__gte=start_date
        )
        current_total = current_collabs.count()
        current_success = current_collabs.filter(status='completed').count()

        # Previous period stats
        prev_collabs = CollaborationSession.objects.filter(
            created_at__gte=prev_start,
            created_at__lt=start_date
        )
        prev_total = prev_collabs.count()

        # Calculate trend
        if prev_total > 0:
            trend_pct = ((current_total - prev_total) / prev_total) * 100
        else:
            trend_pct = 100 if current_total > 0 else 0

        trend_direction = 'up' if trend_pct > 5 else ('down' if trend_pct < -5 else 'stable')

        # Knowledge stats
        current_knowledge = SharedKnowledge.objects.filter(
            created_at__gte=start_date
        ).count()

        # Message stats
        current_messages = InterAgentMessage.objects.filter(
            timestamp__gte=start_date
        ).count()

        # Active agents
        active_agents = AgentPerformanceMetric.objects.filter(
            last_activity__gte=start_date
        ).count()

        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'collaborations': {
                'total': current_total,
                'successful': current_success,
                'success_rate': round((current_success / max(current_total, 1)) * 100, 1),
                'trend_direction': trend_direction,
                'trend_percentage': round(trend_pct, 1)
            },
            'knowledge': {
                'new_items': current_knowledge,
                'total_items': SharedKnowledge.objects.count()
            },
            'messages': {
                'total': current_messages
            },
            'agents': {
                'active': active_agents,
                'total': AgentPerformanceMetric.objects.count()
            }
        }

    def get_all_charts(self, days: int = 7) -> Dict[str, Any]:
        """
        Get all chart data in one call for dashboard efficiency.
        """
        return {
            'agent_trends': self.get_agent_performance_trends(days).to_dict(),
            'agent_comparison': self.get_agent_comparison().to_dict(),
            'workflow_trends': self.get_workflow_execution_trends(days).to_dict(),
            'workflow_success': self.get_workflow_success_rates().to_dict(),
            'knowledge_growth': self.get_knowledge_growth(days).to_dict(),
            'knowledge_domains': self.get_knowledge_by_domain().to_dict(),
            'system_health': self.get_system_health_trends(days).to_dict(),
            'activity_heatmap': self.get_agent_activity_heatmap(days),
            'summary': self.get_analytics_summary(days)
        }


def get_analytics_service(user=None) -> AnalyticsService:
    """Factory function to get analytics service instance."""
    return AnalyticsService(user=user)
