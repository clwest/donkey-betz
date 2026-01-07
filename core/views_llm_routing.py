"""
LLM Routing API Views - Session 699

Real API endpoints for the LLM routing system that connect to the database models.
Provides frontend access to:
- LLM Providers (6 providers)
- LLM Models (17 models)
- Agent LLM Configs (64 agent-model mappings)
- LLM Call Logs (cost tracking and analytics)
"""

import os
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import TruncDate, TruncHour
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from core.models_llm_routing import LLMProvider, LLMModel, AgentLLMConfig, LLMCallLog

logger = logging.getLogger(__name__)


def _check_api_key(env_var_name: str) -> bool:
    """Check if an API key environment variable is set and not empty."""
    if not env_var_name:
        return False
    value = os.getenv(env_var_name, '')
    return bool(value and value not in ['', 'your-key-here', 'not-set'])


@api_view(['GET'])
@permission_classes([AllowAny])
def llm_routing_status(request):
    """
    Get overall LLM routing system status.
    Shows provider health, model counts, and recent activity.
    """
    try:
        # Get provider stats
        providers = LLMProvider.objects.all()
        provider_stats = []

        for provider in providers:
            models = LLMModel.objects.filter(provider=provider)
            recent_calls = LLMCallLog.objects.filter(
                provider=provider.name,
                created_at__gte=timezone.now() - timedelta(hours=24)
            )

            provider_stats.append({
                'id': str(provider.id),
                'name': provider.name,
                'display_name': provider.display_name,
                'is_active': provider.is_active,
                'has_api_key': _check_api_key(provider.api_key_env_var),
                'api_key_env_var': provider.api_key_env_var,
                'model_count': models.count(),
                'calls_24h': recent_calls.count(),
                'cost_24h': float(recent_calls.aggregate(total=Sum('cost'))['total'] or 0),
                'success_rate_24h': _calculate_success_rate(recent_calls),
            })

        # Get agent config stats
        total_agents = AgentLLMConfig.objects.count()
        agents_by_model = AgentLLMConfig.objects.values('primary_model__model_id').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # Get recent call summary
        recent_calls = LLMCallLog.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        )

        return Response({
            'success': True,
            'status': {
                'providers': {
                    'total': providers.count(),
                    'active': providers.filter(is_active=True).count(),
                    'with_keys': sum(1 for p in providers if _check_api_key(p.api_key_env_var)),
                    'details': provider_stats,
                },
                'models': {
                    'total': LLMModel.objects.count(),
                    'active': LLMModel.objects.filter(is_active=True).count(),
                },
                'agent_configs': {
                    'total': total_agents,
                    'top_models': [
                        {'model': item['primary_model__model_id'], 'agent_count': item['count']}
                        for item in agents_by_model
                    ],
                },
                'activity_24h': {
                    'total_calls': recent_calls.count(),
                    'successful_calls': recent_calls.filter(success=True).count(),
                    'total_cost': float(recent_calls.aggregate(total=Sum('cost'))['total'] or 0),
                    'total_tokens': recent_calls.aggregate(total=Sum('total_tokens'))['total'] or 0,
                },
            },
            'last_updated': timezone.now().isoformat(),
        })
    except Exception as e:
        logger.error(f"Error getting LLM routing status: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def llm_providers_list(request):
    """
    List all LLM providers with their configuration.
    """
    try:
        providers = LLMProvider.objects.all().order_by('name')

        data = []
        for provider in providers:
            models = LLMModel.objects.filter(provider=provider)
            data.append({
                'id': str(provider.id),
                'name': provider.name,
                'display_name': provider.display_name,
                'base_url': provider.base_url,
                'api_key_env_var': provider.api_key_env_var,
                'is_active': provider.is_active,
                'is_available': provider.is_available,
                'has_api_key': _check_api_key(provider.api_key_env_var),
                'supports_streaming': provider.supports_streaming,
                'supports_tools': provider.supports_tools,
                'supports_vision': provider.supports_vision,
                'last_health_check': provider.last_health_check.isoformat() if provider.last_health_check else None,
                'model_count': models.count(),
                'models': [
                    {
                        'id': str(m.id),
                        'model_id': m.model_id,
                        'display_name': m.display_name,
                        'is_active': m.is_active,
                    }
                    for m in models
                ],
                'created_at': provider.created_at.isoformat() if provider.created_at else None,
            })

        return Response({
            'success': True,
            'count': len(data),
            'providers': data,
        })
    except Exception as e:
        logger.error(f"Error listing LLM providers: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def llm_models_list(request):
    """
    List all LLM models with their capabilities and costs.
    Supports filtering by provider.
    """
    try:
        provider_filter = request.GET.get('provider')
        capability_filter = request.GET.get('capability')

        models = LLMModel.objects.select_related('provider').all()

        if provider_filter:
            models = models.filter(provider__name=provider_filter)

        if capability_filter:
            models = models.filter(specializations__contains=[capability_filter])

        data = []
        for model in models.order_by('provider__name', 'display_name'):
            data.append({
                'id': str(model.id),
                'model_id': model.model_id,
                'display_name': model.display_name,
                'category': model.category,
                'provider': {
                    'name': model.provider.name,
                    'display_name': model.provider.display_name,
                },
                'is_active': model.is_active,
                'is_recommended': model.is_recommended,
                'context_window': model.context_window,
                'max_output_tokens': model.max_output_tokens,
                'cost_per_1m_input': float(model.cost_per_1m_input) if model.cost_per_1m_input else None,
                'cost_per_1m_output': float(model.cost_per_1m_output) if model.cost_per_1m_output else None,
                'specializations': model.specializations,
                'supports_streaming': model.supports_streaming,
                'supports_tools': model.supports_tools,
                'supports_vision': model.supports_vision,
                'quality_rating': model.quality_rating,
                'speed_rating': model.speed_rating,
                'default_temperature': float(model.default_temperature) if model.default_temperature else None,
                'default_max_tokens': model.default_max_tokens,
            })

        return Response({
            'success': True,
            'count': len(data),
            'models': data,
            'filters_applied': {
                'provider': provider_filter,
                'capability': capability_filter,
            },
        })
    except Exception as e:
        logger.error(f"Error listing LLM models: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def agent_llm_configs_list(request):
    """
    List all agent-to-model configurations.
    Shows which model each agent is configured to use.
    """
    try:
        agent_filter = request.GET.get('agent')
        model_filter = request.GET.get('model')

        configs = AgentLLMConfig.objects.select_related(
            'primary_model', 'primary_model__provider',
            'fallback_model', 'fallback_model__provider'
        ).all()

        if agent_filter:
            configs = configs.filter(agent_name__icontains=agent_filter)

        if model_filter:
            configs = configs.filter(primary_model__model_id__icontains=model_filter)

        data = []
        for config in configs.order_by('agent_name'):
            data.append({
                'id': str(config.id),
                'agent_name': config.agent_name,
                'agent_category': config.agent_category,
                'is_active': config.is_active,
                'primary_model': {
                    'model_id': config.primary_model.model_id,
                    'display_name': config.primary_model.display_name,
                    'provider': config.primary_model.provider.name,
                } if config.primary_model else None,
                'fallback_model': {
                    'model_id': config.fallback_model.model_id,
                    'display_name': config.fallback_model.display_name,
                    'provider': config.fallback_model.provider.name,
                } if config.fallback_model else None,
                'temperature': float(config.temperature) if config.temperature else None,
                'max_tokens': config.max_tokens,
                'task_overrides': config.task_overrides,
                'use_auto_selection': config.use_auto_selection,
                'total_calls': config.total_calls,
                'total_cost': float(config.total_cost) if config.total_cost else 0,
                'notes': config.notes,
            })

        # Group by model for summary
        model_summary = {}
        for config in configs:
            if config.primary_model:
                model_id = config.primary_model.model_id
                if model_id not in model_summary:
                    model_summary[model_id] = {
                        'model_id': model_id,
                        'provider': config.primary_model.provider.name,
                        'agent_count': 0,
                        'agents': [],
                    }
                model_summary[model_id]['agent_count'] += 1
                model_summary[model_id]['agents'].append(config.agent_name)

        return Response({
            'success': True,
            'count': len(data),
            'configs': data,
            'summary_by_model': list(model_summary.values()),
            'filters_applied': {
                'agent': agent_filter,
                'model': model_filter,
            },
        })
    except Exception as e:
        logger.error(f"Error listing agent LLM configs: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def llm_call_logs_list(request):
    """
    List LLM call logs with filtering and pagination.
    Shows all API calls made through the routing system.
    """
    try:
        # Filters
        agent_filter = request.GET.get('agent')
        provider_filter = request.GET.get('provider')
        model_filter = request.GET.get('model')
        success_filter = request.GET.get('success')
        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))

        logs = LLMCallLog.objects.all()

        # Apply time filter
        logs = logs.filter(created_at__gte=timezone.now() - timedelta(hours=hours))

        if agent_filter:
            logs = logs.filter(agent_name__icontains=agent_filter)

        if provider_filter:
            logs = logs.filter(provider=provider_filter)

        if model_filter:
            logs = logs.filter(model_id__icontains=model_filter)

        if success_filter is not None:
            logs = logs.filter(success=success_filter.lower() == 'true')

        total_count = logs.count()
        logs = logs.order_by('-created_at')[offset:offset + limit]

        data = []
        for log in logs:
            data.append({
                'id': str(log.id),
                'agent_name': log.agent_name,
                'provider': log.provider,
                'model_id': log.model_id,
                'success': log.success,
                'was_fallback': log.was_fallback,
                'task_type': log.task_type,
                'prompt_tokens': log.prompt_tokens,
                'completion_tokens': log.completion_tokens,
                'total_tokens': log.total_tokens,
                'latency_ms': log.latency_ms,
                'cost': float(log.cost) if log.cost else 0,
                'error_type': log.error_type,
                'error_message': log.error_message[:200] if log.error_message else None,
                'created_at': log.created_at.isoformat() if log.created_at else None,
            })

        return Response({
            'success': True,
            'count': len(data),
            'total_count': total_count,
            'logs': data,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count,
            },
            'filters_applied': {
                'agent': agent_filter,
                'provider': provider_filter,
                'model': model_filter,
                'success': success_filter,
                'hours': hours,
            },
        })
    except Exception as e:
        logger.error(f"Error listing LLM call logs: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def llm_cost_analytics(request):
    """
    Get cost analytics and usage statistics.
    Aggregates data from LLMCallLog for dashboards.
    """
    try:
        hours = int(request.GET.get('hours', 168))  # Default 7 days

        logs = LLMCallLog.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=hours)
        )

        # Overall stats
        overall = logs.aggregate(
            total_calls=Count('id'),
            successful_calls=Count('id', filter=F('success')),
            total_cost=Sum('cost'),
            total_tokens=Sum('total_tokens'),
            avg_latency=Avg('latency_ms'),
        )

        # Stats by provider
        by_provider = logs.values('provider').annotate(
            calls=Count('id'),
            cost=Sum('cost'),
            tokens=Sum('total_tokens'),
            avg_latency=Avg('latency_ms'),
            success_rate=Count('id', filter=F('success')) * 100.0 / Count('id'),
        ).order_by('-cost')

        # Stats by model
        by_model = logs.values('model_id', 'provider').annotate(
            calls=Count('id'),
            cost=Sum('cost'),
            tokens=Sum('total_tokens'),
            avg_latency=Avg('latency_ms'),
        ).order_by('-cost')[:10]

        # Stats by agent
        by_agent = logs.values('agent_name').annotate(
            calls=Count('id'),
            cost=Sum('cost'),
            tokens=Sum('total_tokens'),
        ).order_by('-cost')[:10]

        # Daily breakdown
        daily = logs.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            calls=Count('id'),
            cost=Sum('cost'),
            tokens=Sum('total_tokens'),
        ).order_by('date')

        # Hourly breakdown (last 24h)
        hourly = logs.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            calls=Count('id'),
            cost=Sum('cost'),
        ).order_by('hour')

        return Response({
            'success': True,
            'time_range_hours': hours,
            'analytics': {
                'overall': {
                    'total_calls': overall['total_calls'] or 0,
                    'successful_calls': overall['successful_calls'] or 0,
                    'success_rate': (overall['successful_calls'] or 0) / max(overall['total_calls'] or 1, 1) * 100,
                    'total_cost': float(overall['total_cost'] or 0),
                    'total_tokens': overall['total_tokens'] or 0,
                    'avg_latency_ms': float(overall['avg_latency'] or 0),
                },
                'by_provider': [
                    {
                        'provider': item['provider'],
                        'calls': item['calls'],
                        'cost': float(item['cost'] or 0),
                        'tokens': item['tokens'] or 0,
                        'avg_latency_ms': float(item['avg_latency'] or 0),
                        'success_rate': float(item['success_rate'] or 0),
                    }
                    for item in by_provider
                ],
                'by_model': [
                    {
                        'model_id': item['model_id'],
                        'provider': item['provider'],
                        'calls': item['calls'],
                        'cost': float(item['cost'] or 0),
                        'tokens': item['tokens'] or 0,
                        'avg_latency_ms': float(item['avg_latency'] or 0),
                    }
                    for item in by_model
                ],
                'by_agent': [
                    {
                        'agent_name': item['agent_name'],
                        'calls': item['calls'],
                        'cost': float(item['cost'] or 0),
                        'tokens': item['tokens'] or 0,
                    }
                    for item in by_agent
                ],
                'daily_breakdown': [
                    {
                        'date': item['date'].isoformat() if item['date'] else None,
                        'calls': item['calls'],
                        'cost': float(item['cost'] or 0),
                        'tokens': item['tokens'] or 0,
                    }
                    for item in daily
                ],
                'hourly_breakdown': [
                    {
                        'hour': item['hour'].isoformat() if item['hour'] else None,
                        'calls': item['calls'],
                        'cost': float(item['cost'] or 0),
                    }
                    for item in hourly
                ],
            },
            'generated_at': timezone.now().isoformat(),
        })
    except Exception as e:
        logger.error(f"Error getting LLM cost analytics: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_agent_llm_config(request, agent_name):
    """
    Update an agent's LLM configuration.
    Allows changing the model assignment for an agent.
    """
    try:
        import json
        data = json.loads(request.body or b'{}')

        config = AgentLLMConfig.objects.filter(agent_name=agent_name).first()
        if not config:
            return Response({
                'success': False,
                'error': f'No config found for agent: {agent_name}'
            }, status=404)

        # Update fields if provided
        if 'primary_model_id' in data:
            model = LLMModel.objects.filter(model_id=data['primary_model_id']).first()
            if model:
                config.primary_model = model

        if 'fallback_model_id' in data:
            model = LLMModel.objects.filter(model_id=data['fallback_model_id']).first()
            if model:
                config.fallback_model = model

        if 'temperature' in data:
            config.temperature = data['temperature']

        if 'max_tokens' in data:
            config.max_tokens = data['max_tokens']

        if 'is_active' in data:
            config.is_active = data['is_active']

        config.save()

        return Response({
            'success': True,
            'message': f'Updated config for {agent_name}',
            'config': {
                'agent_name': config.agent_name,
                'primary_model': config.primary_model.model_id if config.primary_model else None,
                'fallback_model': config.fallback_model.model_id if config.fallback_model else None,
                'temperature': float(config.temperature) if config.temperature else None,
                'max_tokens': config.max_tokens,
                'is_active': config.is_active,
            },
        })
    except Exception as e:
        logger.error(f"Error updating agent LLM config: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


def _calculate_success_rate(queryset):
    """Calculate success rate for a queryset of logs."""
    total = queryset.count()
    if total == 0:
        return 100.0
    success = queryset.filter(success=True).count()
    return round(success / total * 100, 2)
