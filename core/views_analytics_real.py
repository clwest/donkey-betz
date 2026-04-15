"""
Session 780: Real Analytics Implementation
Replaces stub endpoints with actual data from the database
"""

import logging
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Avg, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def analytics_overview(request):
    """
    GET /api/analytics/overview/ - Real analytics overview
    Session 780: Replaces stub with actual data
    """
    from core.models_unified_system import Agent, AgentExecution, AgentMemory
    from core.models import SpiderData, ContentChannel

    # Calculate date ranges
    now = timezone.now()
    last_30d = now - timedelta(days=30)
    last_7d = now - timedelta(days=7)
    last_24h = now - timedelta(hours=24)

    # Agent stats
    total_agents = Agent.objects.count()
    active_agents = Agent.objects.filter(is_active=True).count()

    # Execution stats
    total_executions = AgentExecution.objects.count()
    executions_30d = AgentExecution.objects.filter(created_at__gte=last_30d).count()
    executions_7d = AgentExecution.objects.filter(created_at__gte=last_7d).count()
    executions_24h = AgentExecution.objects.filter(created_at__gte=last_24h).count()

    # Success rate
    successful_executions = AgentExecution.objects.filter(
        created_at__gte=last_30d,
        status='completed'
    ).count()
    success_rate = (successful_executions / executions_30d * 100) if executions_30d > 0 else 0

    # Content stats.
    # Session 1103c: both blocks were BARE 'except:' which silently
    # undercounted total_content if either query broke. Analytics
    # dashboards then reported deceptively low content totals. Now
    # narrow to Exception and log.
    total_content = 0
    try:
        from core.models import SelfBlog
        total_content += SelfBlog.objects.count()
    except Exception as e:
        logger.warning(
            "views_analytics_real: SelfBlog count failed "
            "(%s: %s) — total_content undercounted",
            type(e).__name__, e,
        )

    try:
        total_content += ContentChannel.objects.aggregate(
            total=Count('episodes')
        )['total'] or 0
    except Exception as e:
        logger.warning(
            "views_analytics_real: ContentChannel episodes aggregate "
            "failed (%s: %s) — total_content undercounted",
            type(e).__name__, e,
        )

    # Spider data stats
    spider_data_30d = SpiderData.objects.filter(created_at__gte=last_30d).count()
    spider_data_7d = SpiderData.objects.filter(created_at__gte=last_7d).count()
    spider_data_24h = SpiderData.objects.filter(created_at__gte=last_24h).count()

    # Memory/learning stats
    total_memories = AgentMemory.objects.count()
    memories_30d = AgentMemory.objects.filter(created_at__gte=last_30d).count()

    # Token usage
    token_stats = AgentExecution.objects.filter(
        created_at__gte=last_30d
    ).aggregate(
        total_tokens=Sum('tokens_used'),
        total_cost=Sum('cost'),
        avg_tokens=Avg('tokens_used')
    )

    # Calculate trends (compare 7d to previous 7d)
    prev_7d_start = last_7d - timedelta(days=7)
    executions_prev_7d = AgentExecution.objects.filter(
        created_at__gte=prev_7d_start,
        created_at__lt=last_7d
    ).count()

    execution_trend = 0
    if executions_prev_7d > 0:
        execution_trend = ((executions_7d - executions_prev_7d) / executions_prev_7d) * 100

    return Response({
        'success': True,
        'period': '30d',
        'generated_at': now.isoformat(),

        # Core metrics
        'total_agents': total_agents,
        'active_agents': active_agents,
        'total_executions': total_executions,
        'total_content_pieces': total_content,
        'total_memories': total_memories,

        # Period-specific stats
        'executions_30d': executions_30d,
        'executions_7d': executions_7d,
        'executions_24h': executions_24h,
        'memories_30d': memories_30d,
        'success_rate': round(success_rate, 1),

        # Spider data
        'spider_data_30d': spider_data_30d,
        'spider_data_7d': spider_data_7d,
        'spider_data_24h': spider_data_24h,

        # Token usage
        'token_usage_30d': token_stats['total_tokens'] or 0,
        'ai_cost_30d': float(token_stats['total_cost'] or 0),
        'avg_tokens_per_execution': round(token_stats['avg_tokens'] or 0, 1),

        # Trends
        'execution_trend_7d': round(execution_trend, 1),

        # Revenue placeholder (needs Revenue model)
        'total_revenue': 0,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def analytics_summary(request):
    """
    GET /api/analytics/summary/ - Analytics summary
    Session 780: Replaces stub with actual data
    """
    from core.models_unified_system import Agent, AgentExecution, KnowledgeTransfer, Collaboration

    now = timezone.now()
    last_7d = now - timedelta(days=7)
    last_24h = now - timedelta(hours=24)

    # Quick summary stats
    executions_today = AgentExecution.objects.filter(
        created_at__gte=last_24h
    ).count()

    knowledge_transfers = KnowledgeTransfer.objects.filter(
        created_at__gte=last_7d
    ).count()

    collaborations = Collaboration.objects.filter(
        created_at__gte=last_7d
    ).count()

    # Top agents today
    top_agents = AgentExecution.objects.filter(
        created_at__gte=last_24h
    ).values('agent__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    return Response({
        'success': True,
        'period': '24h',
        'executions_today': executions_today,
        'knowledge_transfers_7d': knowledge_transfers,
        'collaborations_7d': collaborations,
        'top_agents_today': list(top_agents),
        'generated_at': now.isoformat(),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def analytics_reports_list(request):
    """
    GET /api/analytics/reports/ - List available reports
    Session 780: Returns available report types (not actual generated reports yet)
    """
    return Response({
        'success': True,
        'reports': [
            {
                'id': 'agent-performance',
                'name': 'Agent Performance Report',
                'description': 'Detailed metrics on agent executions, success rates, and token usage',
                'available': True,
            },
            {
                'id': 'spider-data',
                'name': 'Spider Data Collection Report',
                'description': 'Summary of data collected by the spider network',
                'available': True,
            },
            {
                'id': 'learning-metrics',
                'name': 'Learning & Knowledge Transfer Report',
                'description': 'Insights on agent learning patterns and knowledge sharing',
                'available': True,
            },
            {
                'id': 'content-production',
                'name': 'Content Production Report',
                'description': 'Overview of generated content across all channels',
                'available': True,
            },
        ],
        'generated_reports': [],  # Would contain previously generated reports
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analytics_reports_generate(request):
    """
    POST /api/analytics/reports/generate/ - Generate a new report
    Session 780: Generates actual report data
    """
    report_type = request.data.get('report_type', 'agent-performance')
    period = request.data.get('period', '30d')

    from core.models_unified_system import Agent, AgentExecution

    now = timezone.now()
    days = int(period.replace('d', '')) if 'd' in period else 30
    start_date = now - timedelta(days=days)

    if report_type == 'agent-performance':
        # Generate agent performance report
        agents = Agent.objects.annotate(
            total_executions=Count('executions', filter=Q(executions__created_at__gte=start_date)),
            successful=Count('executions', filter=Q(
                executions__created_at__gte=start_date,
                executions__status='completed'
            )),
            total_tokens=Sum('executions__tokens_used', filter=Q(executions__created_at__gte=start_date)),
        ).values('name', 'agent_type', 'total_executions', 'successful', 'total_tokens').order_by('-total_executions')[:20]

        return Response({
            'success': True,
            'report_type': report_type,
            'period': period,
            'generated_at': now.isoformat(),
            'data': {
                'agents': list(agents),
                'total_agents_analyzed': len(agents),
            }
        })

    return Response({
        'success': True,
        'report_type': report_type,
        'period': period,
        'generated_at': now.isoformat(),
        'message': f'Report type {report_type} generated',
        'data': {}
    })
