"""
Agent Monitoring Dashboard Views
Provides API endpoints for monitoring agent performance
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from datetime import datetime, timedelta
from django.utils import timezone

from agents.monitoring import (
    PerformanceAnalyzer,
    get_agent_metrics_summary,
    METRICS_CONFIG
)
from core.api_responses import api_success, api_error

import logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_metrics_dashboard(request):
    """
    Get comprehensive agent metrics for dashboard display
    """
    try:
        # Get time period from query params
        period = request.GET.get('period', '24h')
        
        # Convert period to timedelta
        period_map = {
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30)
        }
        
        time_period = period_map.get(period, timedelta(hours=24))
        
        # Get metrics summary
        summary = get_agent_metrics_summary()
        
        # Get system metrics
        system_metrics = PerformanceAnalyzer.get_system_metrics()
        
        # Combine data
        dashboard_data = {
            'summary': summary,
            'system': system_metrics.get('system', {}),
            'cache': system_metrics.get('cache', {}),
            'agents': system_metrics.get('agents', {}),
            'period': period,
            'last_updated': datetime.now().isoformat(),
            'monitoring_enabled': METRICS_CONFIG['enable_monitoring']
        }
        
        return api_success(
            data=dashboard_data,
            message='Agent metrics retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error getting agent metrics: {e}")
        return api_error(
            message='Failed to retrieve agent metrics',
            error_code='metrics_error'
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_performance_detail(request, agent_name):
    """
    Get detailed performance metrics for a specific agent
    """
    try:
        # Get time period
        period = request.GET.get('period', '24h')
        period_map = {
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30)
        }
        time_period = period_map.get(period, timedelta(hours=24))
        
        # Get agent statistics
        stats = PerformanceAnalyzer.get_agent_stats(agent_name, time_period)
        
        if not stats:
            return api_error(
                message=f'No metrics found for agent: {agent_name}',
                error_code='agent_not_found'
            )
        
        # Get recent executions
        from core.models.agents_registry import AgentTaskExecution
        
        recent_executions = AgentTaskExecution.objects.filter(
            template__name=agent_name,
            created_at__gte=timezone.now() - time_period
        ).order_by('-created_at')[:10]
        
        # Format execution history
        execution_history = []
        for execution in recent_executions:
            execution_history.append({
                'id': str(execution.id),
                'status': execution.status,
                'execution_time': execution.execution_time,
                'created_at': execution.created_at.isoformat(),
                'error': execution.error_message if execution.status == 'failed' else None
            })
        
        # Compile detailed metrics
        detail_data = {
            'agent_name': agent_name,
            'statistics': stats,
            'recent_executions': execution_history,
            'period': period,
            'performance_grade': _calculate_performance_grade(stats),
            'recommendations': _generate_agent_recommendations(stats)
        }
        
        return api_success(
            data=detail_data,
            message=f'Performance details for {agent_name}'
        )
        
    except Exception as e:
        logger.error(f"Error getting agent performance detail: {e}")
        return api_error(
            message='Failed to retrieve agent performance details',
            error_code='performance_error'
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def performance_report(request):
    """
    Generate comprehensive performance report (admin only)
    """
    try:
        # Get report period
        period = request.GET.get('period', '7d')
        period_map = {
            '1d': timedelta(days=1),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30),
            '90d': timedelta(days=90)
        }
        time_period = period_map.get(period, timedelta(days=7))
        
        # Generate report
        report = PerformanceAnalyzer.generate_performance_report(time_period)
        
        return api_success(
            data=report,
            message='Performance report generated successfully'
        )
        
    except Exception as e:
        logger.error(f"Error generating performance report: {e}")
        return api_error(
            message='Failed to generate performance report',
            error_code='report_error'
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def real_time_metrics(request):
    """
    Get real-time metrics for active agent executions
    """
    try:
        from django.core.cache import cache
        
        # Get all active agent metrics from cache
        active_metrics = []
        
        # Scan cache for agent metrics (in production, use Redis SCAN)
        for i in range(100):  # Check last 100 execution IDs
            cache_key = f"agent_metrics:exec_{i}"
            metrics = cache.get(cache_key)
            
            if metrics:
                # Check if still running (no end_timestamp)
                if 'end_timestamp' not in metrics:
                    active_metrics.append({
                        'execution_id': f"exec_{i}",
                        'agent_name': metrics.get('agent_name', 'Unknown'),
                        'duration': time.time() - metrics.get('start_time', time.time()),
                        'steps_completed': len(metrics.get('steps', [])),
                        'errors': len(metrics.get('errors', [])),
                        'warnings': len(metrics.get('warnings', []))
                    })
        
        return api_success(
            data={
                'active_executions': active_metrics,
                'count': len(active_metrics),
                'timestamp': datetime.now().isoformat()
            },
            message='Real-time metrics retrieved'
        )
        
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        return api_error(
            message='Failed to retrieve real-time metrics',
            error_code='realtime_error'
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def clear_metrics_cache(request):
    """
    Clear metrics cache (admin only)
    """
    try:
        from django.core.cache import cache
        
        # Clear metrics cache
        cache.clear()
        
        return api_success(
            message='Metrics cache cleared successfully'
        )
        
    except Exception as e:
        logger.error(f"Error clearing metrics cache: {e}")
        return api_error(
            message='Failed to clear metrics cache',
            error_code='cache_error'
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_status(request):
    """
    Get current alert status for agent performance
    """
    try:
        alerts = []
        
        # Check for performance alerts
        summary = get_agent_metrics_summary()
        
        # High error rate alert
        if summary['error_rate'] > 0.1:
            alerts.append({
                'level': 'warning',
                'type': 'high_error_rate',
                'message': f"System error rate is {summary['error_rate']:.1%}",
                'threshold': '10%',
                'timestamp': datetime.now().isoformat()
            })
        
        # Slow execution alert
        if summary['average_execution_time'] > 30:
            alerts.append({
                'level': 'warning',
                'type': 'slow_execution',
                'message': f"Average execution time is {summary['average_execution_time']:.1f}s",
                'threshold': '30s',
                'timestamp': datetime.now().isoformat()
            })
        
        # Agents needing attention
        for agent in summary.get('needs_attention', []):
            alerts.append({
                'level': 'error',
                'type': 'agent_failure',
                'message': f"Agent '{agent['agent']}' has {agent['error_rate']:.1%} error rate",
                'agent': agent['agent'],
                'timestamp': datetime.now().isoformat()
            })
        
        return api_success(
            data={
                'alerts': alerts,
                'alert_count': len(alerts),
                'status': 'critical' if any(a['level'] == 'error' for a in alerts) else 
                         'warning' if alerts else 'healthy',
                'timestamp': datetime.now().isoformat()
            },
            message='Alert status retrieved'
        )
        
    except Exception as e:
        logger.error(f"Error getting alert status: {e}")
        return api_error(
            message='Failed to retrieve alert status',
            error_code='alert_error'
        )


# Helper functions
def _calculate_performance_grade(stats):
    """Calculate performance grade based on statistics"""
    if not stats:
        return 'N/A'
    
    score = 100
    
    # Deduct points for high execution time
    avg_time = stats.get('avg_execution_time', 0)
    if avg_time > 60:
        score -= 30
    elif avg_time > 30:
        score -= 20
    elif avg_time > 10:
        score -= 10
    
    # Deduct points for failures
    failure_rate = stats.get('failure_rate', 0)
    score -= int(failure_rate * 50)
    
    # Grade assignment
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


def _generate_agent_recommendations(stats):
    """Generate recommendations based on agent statistics"""
    recommendations = []
    
    if not stats:
        return recommendations
    
    # Check execution time
    avg_time = stats.get('avg_execution_time', 0)
    if avg_time > 60:
        recommendations.append({
            'type': 'performance',
            'severity': 'high',
            'message': 'Consider breaking down this agent into smaller tasks',
            'metric': f'Average execution time: {avg_time:.1f}s'
        })
    elif avg_time > 30:
        recommendations.append({
            'type': 'performance',
            'severity': 'medium',
            'message': 'Review agent logic for optimization opportunities',
            'metric': f'Average execution time: {avg_time:.1f}s'
        })
    
    # Check failure rate
    failure_rate = stats.get('failure_rate', 0)
    if failure_rate > 0.2:
        recommendations.append({
            'type': 'reliability',
            'severity': 'high',
            'message': 'High failure rate detected. Review error logs and add error handling',
            'metric': f'Failure rate: {failure_rate:.1%}'
        })
    elif failure_rate > 0.1:
        recommendations.append({
            'type': 'reliability',
            'severity': 'medium',
            'message': 'Moderate failure rate. Consider adding retry logic',
            'metric': f'Failure rate: {failure_rate:.1%}'
        })
    
    # Check execution count
    total_executions = stats.get('total_executions', 0)
    if total_executions < 10:
        recommendations.append({
            'type': 'usage',
            'severity': 'low',
            'message': 'Low usage detected. Consider if this agent is still needed',
            'metric': f'Total executions: {total_executions}'
        })
    
    return recommendations


import time  # Add this import at the top of the file
