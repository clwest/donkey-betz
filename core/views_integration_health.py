"""
Integration Health & Observability Views
Session 758: Comprehensive observability for the integration layer.

Provides:
1. Health Check API - Status of all 6 context sources
2. Context Injection Metrics - Success rates and trends
3. Alert Log - Silent failures tracked
4. Execution Quality Scores - Context vs outcome correlation
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_GET
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncHour, TruncDay

logger = logging.getLogger(__name__)


# =============================================================================
# 1. HEALTH CHECK API
# =============================================================================

@require_GET
def integration_health(request):
    """
    GET /api/integration/health/

    Returns health status of all 6 integration context sources.
    Session 758: Primary observability endpoint.
    """
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    health_data = {
        'timestamp': now.isoformat(),
        'overall_status': 'healthy',
        'components': {},
        'metrics': {},
    }

    issues = []

    # 1. Spider Data Health
    try:
        from core.models_unified_system import SpiderData
        spider_total = SpiderData.objects.count()
        spider_24h = SpiderData.objects.filter(created_at__gte=last_24h).count()
        spider_7d = SpiderData.objects.filter(created_at__gte=last_7d).count()
        last_spider = SpiderData.objects.order_by('-created_at').first()

        spider_status = 'healthy'
        if spider_24h == 0:
            spider_status = 'degraded'
            issues.append('No spider data in last 24 hours')
        elif spider_24h < 50:
            spider_status = 'warning'
            issues.append(f'Low spider activity: only {spider_24h} records in 24h')

        health_data['components']['spider_data'] = {
            'status': spider_status,
            'total_records': spider_total,
            'last_24h': spider_24h,
            'last_7d': spider_7d,
            'last_capture': last_spider.created_at.isoformat() if last_spider else None,
            'last_spider': last_spider.spider_name if last_spider else None,
        }
    except Exception as e:
        health_data['components']['spider_data'] = {'status': 'error', 'error': str(e)}
        issues.append(f'Spider data error: {e}')

    # 2. Learning Patterns Health
    try:
        from core.models_unified_system import AgentLearning
        learning_total = AgentLearning.objects.count()
        learning_7d = AgentLearning.objects.filter(created_at__gte=last_7d).count()
        teaching_agents = AgentLearning.objects.filter(
            learning_type='teaching',
            created_at__gte=last_7d
        ).values('teacher_agent').distinct().count()

        learning_status = 'healthy' if learning_7d > 100 else 'warning' if learning_7d > 0 else 'degraded'

        health_data['components']['learning_patterns'] = {
            'status': learning_status,
            'total_patterns': learning_total,
            'last_7d': learning_7d,
            'active_teaching_agents': teaching_agents,
        }
    except Exception as e:
        health_data['components']['learning_patterns'] = {'status': 'error', 'error': str(e)}
        issues.append(f'Learning patterns error: {e}')

    # 3. Advisor System Health
    try:
        from core.services.advisor_context_builder import get_advisor_context_builder
        builder = get_advisor_context_builder()
        advisor_count = len(builder.ADVISOR_WISDOM)  # Count advisors with wisdom defined
        agent_mappings = len(builder.AGENT_ADVISOR_MAPPINGS)

        health_data['components']['advisor_system'] = {
            'status': 'healthy',
            'registered_advisors': advisor_count,
            'agent_mappings': agent_mappings,
        }
    except Exception as e:
        health_data['components']['advisor_system'] = {'status': 'error', 'error': str(e)}
        issues.append(f'Advisor system error: {e}')

    # 4. Feedback Loop Health
    try:
        from core.models_unified_system import AgentExecution
        executions_7d = AgentExecution.objects.filter(created_at__gte=last_7d).count()
        successful_7d = AgentExecution.objects.filter(
            created_at__gte=last_7d,
            status='completed'
        ).count()

        success_rate = (successful_7d / executions_7d * 100) if executions_7d > 0 else 0
        feedback_status = 'healthy' if success_rate >= 80 else 'warning' if success_rate >= 50 else 'degraded'

        health_data['components']['feedback_loop'] = {
            'status': feedback_status,
            'executions_7d': executions_7d,
            'success_rate': round(success_rate, 1),
        }
    except Exception as e:
        health_data['components']['feedback_loop'] = {'status': 'error', 'error': str(e)}
        issues.append(f'Feedback loop error: {e}')

    # 5. Sci-Fi Context Health
    try:
        from core.models_unified_system import AgentMood, AgentEvolution
        moods_set = AgentMood.objects.filter(last_updated__gte=last_7d).count()
        evolutions = AgentEvolution.objects.count()

        scifi_status = 'healthy' if moods_set > 0 or evolutions > 0 else 'warning'

        health_data['components']['scifi_context'] = {
            'status': scifi_status,
            'active_moods': moods_set,
            'evolution_records': evolutions,
        }
    except Exception as e:
        health_data['components']['scifi_context'] = {'status': 'error', 'error': str(e)}
        issues.append(f'Sci-Fi context error: {e}')

    # 6. Context Injection Rate (from execution records)
    # Session 758: Tracking was added on 2026-01-15, so only count tracked executions
    try:
        from core.models_unified_system import AgentExecution
        from datetime import datetime

        # Tracking started when context_injected field was added
        tracking_start = timezone.make_aware(datetime(2026, 1, 15, 0, 0, 0))

        recent_execs = AgentExecution.objects.filter(created_at__gte=last_24h).order_by('-created_at')
        total_recent = recent_execs.count()

        # Count executions WITH tracking (have context_injected key)
        tracked_execs = 0
        with_context = 0

        for ex in recent_execs[:100]:  # Sample last 100
            input_data = ex.input_data or {}
            # Check if this execution has tracking data
            if 'context_injected' in input_data:
                tracked_execs += 1
                context_injected = input_data.get('context_injected', {})
                if context_injected.get('spider_data'):
                    with_context += 1

        # Calculate rate based on TRACKED executions only
        injection_rate = (with_context / tracked_execs * 100) if tracked_execs > 0 else 0

        health_data['metrics']['context_injection_rate'] = round(injection_rate, 1)
        health_data['metrics']['executions_24h'] = total_recent
        health_data['metrics']['tracked_executions'] = tracked_execs
        health_data['metrics']['with_context'] = with_context
        health_data['metrics']['tracking_started'] = tracking_start.isoformat()
        health_data['metrics']['tracking_note'] = (
            'Context tracking was added Session 758. Rate shows tracked executions only.'
            if tracked_execs < total_recent else None
        )

    except Exception as e:
        health_data['metrics']['context_injection_rate'] = 0
        health_data['metrics']['error'] = str(e)

    # Overall status
    component_statuses = [c.get('status', 'unknown') for c in health_data['components'].values()]
    if 'error' in component_statuses:
        health_data['overall_status'] = 'error'
    elif 'degraded' in component_statuses:
        health_data['overall_status'] = 'degraded'
    elif 'warning' in component_statuses:
        health_data['overall_status'] = 'warning'
    else:
        health_data['overall_status'] = 'healthy'

    health_data['issues'] = issues

    return JsonResponse(health_data)


# =============================================================================
# 2. CONTEXT INJECTION METRICS
# =============================================================================

@require_GET
def context_injection_metrics(request):
    """
    GET /api/integration/metrics/

    Returns detailed context injection metrics over time.
    Session 758: For dashboard visualization.
    """
    from core.models_unified_system import AgentExecution

    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # Get hourly breakdown for last 24h
    hourly_data = []
    for hour_offset in range(24):
        hour_start = now - timedelta(hours=hour_offset + 1)
        hour_end = now - timedelta(hours=hour_offset)

        execs = AgentExecution.objects.filter(
            created_at__gte=hour_start,
            created_at__lt=hour_end
        )

        total = execs.count()
        with_spider = 0
        with_learning = 0
        with_advisor = 0

        for ex in execs[:50]:  # Sample
            ctx = (ex.input_data or {}).get('context_injected', {})
            if ctx.get('spider_data'):
                with_spider += 1
            if ctx.get('learning_patterns'):
                with_learning += 1
            if ctx.get('advisor_insights'):
                with_advisor += 1

        hourly_data.append({
            'hour': hour_end.isoformat(),
            'total_executions': total,
            'with_spider_context': with_spider,
            'with_learning_context': with_learning,
            'with_advisor_context': with_advisor,
        })

    # Get per-agent breakdown
    agent_metrics = AgentExecution.objects.filter(
        created_at__gte=last_7d
    ).values('agent__name').annotate(
        total=Count('id'),
        avg_time=Avg('execution_time_ms'),
    ).order_by('-total')[:20]

    return JsonResponse({
        'timestamp': now.isoformat(),
        'hourly_breakdown': list(reversed(hourly_data)),
        'agent_metrics': list(agent_metrics),
    })


# =============================================================================
# 3. ALERT LOG MODEL AND VIEW
# =============================================================================

class IntegrationAlertView(View):
    """
    GET /api/integration/alerts/

    Returns recent integration alerts/failures.
    Session 758: For monitoring silent failures.
    """

    def get(self, request):
        from core.models_unified_system import AgentExecution

        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        alerts = []

        # Check for executions without context
        # Session 758: Only count executions that HAVE tracking (context_injected key exists)
        no_context_execs = []
        untracked_count = 0
        recent_execs = AgentExecution.objects.filter(
            created_at__gte=last_24h
        ).order_by('-created_at')[:100]

        for ex in recent_execs:
            input_data = ex.input_data or {}
            # Only alert on executions that have tracking but missing context
            if 'context_injected' in input_data:
                ctx = input_data.get('context_injected', {})
                if not ctx.get('spider_data') and not ctx.get('learning_patterns'):
                    no_context_execs.append({
                        'agent': ex.agent.name if ex.agent else 'Unknown',
                        'time': ex.created_at.isoformat(),
                        'task': ex.task[:100] if ex.task else '',
                    })
            else:
                # Execution from before tracking was added
                untracked_count += 1

        if no_context_execs:
            alerts.append({
                'type': 'missing_context',
                'severity': 'warning',
                'message': f'{len(no_context_execs)} tracked executions without context in last 24h',
                'details': no_context_execs[:10],  # Show first 10
            })

        # Info about untracked executions (not an alert, just info)
        if untracked_count > 0:
            alerts.append({
                'type': 'untracked_executions',
                'severity': 'info',
                'message': f'{untracked_count} executions from before tracking was added (Session 758)',
            })

        # Check for failed executions
        failed_execs = AgentExecution.objects.filter(
            created_at__gte=last_24h,
            status='failed'
        ).count()

        if failed_execs > 0:
            alerts.append({
                'type': 'execution_failures',
                'severity': 'error' if failed_execs > 10 else 'warning',
                'message': f'{failed_execs} failed executions in last 24h',
            })

        # Check spider data freshness
        try:
            from core.models_unified_system import SpiderData
            last_spider = SpiderData.objects.order_by('-created_at').first()
            if last_spider:
                hours_since = (now - last_spider.created_at).total_seconds() / 3600
                if hours_since > 6:
                    alerts.append({
                        'type': 'stale_spider_data',
                        'severity': 'warning' if hours_since < 24 else 'error',
                        'message': f'No spider data captured in {hours_since:.1f} hours',
                        'last_capture': last_spider.created_at.isoformat(),
                    })
        except Exception as e:
            alerts.append({
                'type': 'spider_check_error',
                'severity': 'error',
                'message': str(e),
            })

        return JsonResponse({
            'timestamp': now.isoformat(),
            'alert_count': len(alerts),
            'alerts': alerts,
        })


# =============================================================================
# 4. EXECUTION QUALITY SCORE
# =============================================================================

@require_GET
def execution_quality_analysis(request):
    """
    GET /api/integration/quality/

    Analyzes correlation between context injection and execution quality.
    Session 758: Proves value of integration.
    """
    from core.models_unified_system import AgentExecution

    now = timezone.now()
    last_7d = now - timedelta(days=7)

    # Analyze executions with vs without context
    recent_execs = AgentExecution.objects.filter(
        created_at__gte=last_7d
    ).order_by('-created_at')[:500]

    with_context = {'total': 0, 'success': 0, 'avg_time': 0, 'times': []}
    without_context = {'total': 0, 'success': 0, 'avg_time': 0, 'times': []}

    for ex in recent_execs:
        ctx = (ex.input_data or {}).get('context_injected', {})
        has_context = ctx.get('spider_data') or ctx.get('learning_patterns')

        target = with_context if has_context else without_context
        target['total'] += 1
        if ex.status == 'completed':
            target['success'] += 1
        if ex.execution_time_ms:
            target['times'].append(ex.execution_time_ms)

    # Calculate averages
    if with_context['times']:
        with_context['avg_time'] = sum(with_context['times']) / len(with_context['times'])
    if without_context['times']:
        without_context['avg_time'] = sum(without_context['times']) / len(without_context['times'])

    # Calculate success rates
    with_rate = (with_context['success'] / with_context['total'] * 100) if with_context['total'] > 0 else 0
    without_rate = (without_context['success'] / without_context['total'] * 100) if without_context['total'] > 0 else 0

    # Context quality score by agent
    agent_quality = {}
    for ex in recent_execs:
        agent_name = ex.agent.name if ex.agent else 'Unknown'
        if agent_name not in agent_quality:
            agent_quality[agent_name] = {
                'total': 0,
                'with_context': 0,
                'success_with': 0,
                'success_without': 0
            }

        ctx = (ex.input_data or {}).get('context_injected', {})
        has_ctx = ctx.get('spider_data') or ctx.get('learning_patterns')

        agent_quality[agent_name]['total'] += 1
        if has_ctx:
            agent_quality[agent_name]['with_context'] += 1
            if ex.status == 'completed':
                agent_quality[agent_name]['success_with'] += 1
        else:
            if ex.status == 'completed':
                agent_quality[agent_name]['success_without'] += 1

    # Sort by total executions
    top_agents = sorted(
        agent_quality.items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )[:15]

    return JsonResponse({
        'timestamp': now.isoformat(),
        'period': '7 days',
        'with_context': {
            'executions': with_context['total'],
            'success_rate': round(with_rate, 1),
            'avg_execution_time_ms': round(with_context['avg_time'], 0),
        },
        'without_context': {
            'executions': without_context['total'],
            'success_rate': round(without_rate, 1),
            'avg_execution_time_ms': round(without_context['avg_time'], 0),
        },
        'context_benefit': {
            'success_rate_improvement': round(with_rate - without_rate, 1),
            'time_difference_ms': round(with_context['avg_time'] - without_context['avg_time'], 0),
        },
        'agent_breakdown': [
            {
                'agent': name,
                'total': data['total'],
                'context_rate': round(data['with_context'] / data['total'] * 100, 1) if data['total'] > 0 else 0,
            }
            for name, data in top_agents
        ],
    })
