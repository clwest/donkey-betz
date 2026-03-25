"""
Agent extra endpoints — channels, tools, templates.
Replaces lambda stubs from Session 1036.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def agent_channels(request):
    """List communication channels agents use (conversations, webhooks, etc.)."""
    try:
        from core.models_unified_system import AgentConversation
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        # Recent multi-agent conversations as "channels"
        recent_convos = AgentConversation.objects.filter(
            started_at__gte=now - timedelta(days=7),
        ).order_by('-started_at')[:20]

        results = []
        for conv in recent_convos:
            participants = conv.participants.values_list('name', flat=True) if hasattr(conv, 'participants') else []
            results.append({
                'id': str(conv.id),
                'type': 'conversation',
                'topic': conv.topic or '',
                'participants': list(participants)[:5],
                'conclusion': (conv.conclusion or '')[:200],
                'started_at': conv.started_at.isoformat() if conv.started_at else None,
            })

        # Add static channels
        static_channels = [
            {'id': 'pa-chat', 'type': 'pa_chat', 'topic': 'PA Chat (Rigby)', 'participants': ['PersonalAssistant'], 'description': 'Main PA conversation channel'},
            {'id': 'discord', 'type': 'discord', 'topic': 'Discord Bot', 'participants': ['DonkeyBetzBot'], 'description': '112 commands across 12 notification channels'},
            {'id': 'celery-events', 'type': 'event_bus', 'topic': 'Celery Event Bus', 'participants': ['System'], 'description': 'Task lifecycle events + telemetry'},
        ]

        return JsonResponse({
            'results': static_channels + results,
            'count': len(static_channels) + len(results),
        })
    except Exception as e:
        logger.error(f"agent_channels error: {e}", exc_info=True)
        return JsonResponse({'results': [], 'count': 0, 'error': str(e)})


@require_GET
def agent_tools(request):
    """List tools available to agents (shared tools + per-agent tools)."""
    try:
        from core.models import ToolCallRecord
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta

        # Aggregate tool usage from ToolCallRecord (last 7 days)
        now = timezone.now()
        tool_stats = ToolCallRecord.objects.filter(
            created_at__gte=now - timedelta(days=7),
        ).values('tool_name').annotate(
            call_count=Count('id'),
            avg_latency_ms=Avg('latency_ms'),
            success_count=Count('id', filter=__import__('django').db.models.Q(success=True)),
        ).order_by('-call_count')[:50]

        results = []

        # Shared tools (available to all agents)
        shared_tools = [
            {'name': 'web_search', 'type': 'shared', 'description': 'Real-time web search via Tavily', 'available_to': 'all agents'},
            {'name': 'spider_query', 'type': 'shared', 'description': 'Query SpiderData via SpiderIntelligenceService', 'available_to': 'all agents'},
            {'name': 'delegate_to_specialist', 'type': 'shared', 'description': 'Route sub-tasks to any of 82 discoverable agents', 'available_to': 'all agents'},
        ]

        for tool in shared_tools:
            # Enrich with usage stats
            stat = next((s for s in tool_stats if s['tool_name'] == tool['name']), None)
            if stat:
                tool['calls_7d'] = stat['call_count']
                tool['avg_latency_ms'] = round(stat['avg_latency_ms'] or 0)
                tool['success_rate'] = round(stat['success_count'] / max(stat['call_count'], 1) * 100, 1)
            results.append(tool)

        # Per-agent tools from ToolCallRecord
        for stat in tool_stats:
            if stat['tool_name'] in ('web_search', 'spider_query', 'delegate_to_specialist'):
                continue
            results.append({
                'name': stat['tool_name'],
                'type': 'agent_tool',
                'calls_7d': stat['call_count'],
                'avg_latency_ms': round(stat['avg_latency_ms'] or 0),
                'success_rate': round(stat['success_count'] / max(stat['call_count'], 1) * 100, 1),
            })

        return JsonResponse({
            'results': results,
            'count': len(results),
        })
    except Exception as e:
        logger.error(f"agent_tools error: {e}", exc_info=True)
        return JsonResponse({'results': [], 'count': 0, 'error': str(e)})


@require_GET
def agent_templates(request):
    """List agent execution templates and patterns."""
    try:
        from core.agent_router import AgentRouter

        router = AgentRouter()
        agent_map = router.AGENT_MAP if hasattr(router, 'AGENT_MAP') else {}

        results = []
        for name, cls in sorted(agent_map.items()):
            doc = (cls.__doc__ or '').strip().split('\n')[0][:150] if cls.__doc__ else ''
            category = getattr(cls, 'CATEGORY', getattr(cls, 'category', 'general'))

            results.append({
                'name': name,
                'category': category,
                'description': doc,
                'module': cls.__module__,
                'has_tools': hasattr(cls, 'TOOLS') or hasattr(cls, 'get_tools'),
                'workspace_aware': hasattr(cls, '_write_files_to_workspace'),
            })

        return JsonResponse({
            'results': results,
            'count': len(results),
        })
    except Exception as e:
        logger.error(f"agent_templates error: {e}", exc_info=True)
        return JsonResponse({'results': [], 'count': 0, 'error': str(e)})
