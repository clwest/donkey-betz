"""
Intelligence Hub API Endpoints
Handles spider network data, intelligence feeds, and activity monitoring
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from core.models_unified_system import SpiderData, Opportunity, AgentExecution

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def intelligence_activity_feed(request):
    """
    Get real-time intelligence activity feed

    GET /api/v1/intelligence/activity/

    Returns: {
        "success": true,
        "activities": [...]
    }
    """
    try:
        activities = []
        now = timezone.now()

        # Get recent spider data (last 10 items)
        recent_spider_data = SpiderData.objects.all().order_by('-created_at')[:10]

        for item in recent_spider_data:
            # Make spider name more readable
            spider_display = item.spider_name.replace('_', ' ').title() if item.spider_name else 'Spider'
            data_type_display = item.data_type.replace('_', ' ').title() if item.data_type else 'data'

            # Extract domain from source URL for cleaner display
            source_display = 'Unknown'
            if item.source_url:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(item.source_url)
                    source_display = parsed.netloc or item.source_url[:50]
                except Exception:
                    source_display = item.source_url[:50]

            activities.append({
                'type': 'spider',
                'title': f'🕷️ {spider_display}',
                'description': f'Collected {data_type_display} from {source_display}',
                'timestamp': item.created_at.isoformat(),
                'metadata': {
                    'spider': item.spider_name,
                    'data_type': item.data_type,
                    'source': source_display,
                }
            })

        # Get recent opportunities (last 5 items)
        recent_opportunities = Opportunity.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        for opp in recent_opportunities:
            # Format earnings nicely
            earnings_text = ""
            if opp.potential_revenue:
                earnings_text = f" • Est. ${opp.potential_revenue:,.0f}"

            # Get match score if available
            match_text = ""
            if hasattr(opp, 'match_score') and opp.match_score:
                match_text = f" • {opp.match_score}% match"

            # Create description
            description = f"Source: {opp.source}{earnings_text}{match_text}"

            activities.append({
                'type': 'opportunity',
                'title': f'💰 {opp.title}',
                'description': description,
                'timestamp': opp.created_at.isoformat(),
                'metadata': {
                    'source': opp.source,
                    'estimated_earnings': str(opp.potential_revenue) if opp.potential_revenue else None,
                    'url': opp.url if hasattr(opp, 'url') else None,
                }
            })

        # Get recent agent executions (last 10 items)
        recent_executions = AgentExecution.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]

        for execution in recent_executions:
            # Get agent name
            agent_name = execution.template.name if execution.template else "Unknown Agent"

            # Format task description (truncate if too long)
            task = execution.task_description[:100] if execution.task_description else "Performed task"

            # Create user-friendly title based on task type and status
            if execution.status == 'completed':
                status_icon = '✅'
                status_text = 'Completed'
            elif execution.status == 'failed':
                status_icon = '❌'
                status_text = 'Failed'
            elif execution.status == 'running':
                status_icon = '🔄'
                status_text = 'Running'
            else:
                status_icon = '⏳'
                status_text = execution.status.title()

            # Create readable description
            description_parts = []
            if execution.task_type:
                description_parts.append(f"Task: {execution.task_type}")
            if execution.execution_time_seconds:
                description_parts.append(f"Duration: {execution.execution_time_seconds}s")
            if execution.result and isinstance(execution.result, dict):
                # Try to extract meaningful result
                if 'summary' in execution.result:
                    description_parts.append(f"Result: {execution.result['summary'][:100]}")
                elif 'message' in execution.result:
                    description_parts.append(f"Result: {execution.result['message'][:100]}")

            description = " • ".join(description_parts) if description_parts else task

            activities.append({
                'type': 'agent',
                'title': f'{status_icon} {agent_name}',
                'description': description,
                'timestamp': execution.created_at.isoformat(),
                'metadata': {
                    'agent_id': str(execution.template.id) if execution.template else None,
                    'status': execution.status,
                    'task_type': execution.task_type or 'general',
                    'execution_time': execution.execution_time_seconds,
                }
            })

        # Sort all activities by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        # Limit to last 20 items
        activities = activities[:20]

        return JsonResponse({
            'success': True,
            'count': len(activities),
            'activities': activities
        })

    except Exception as e:
        logger.error(f"Error in intelligence_activity_feed: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve activity feed'
        }, status=500)


@require_http_methods(["GET"])
def spider_network_status(request):
    """
    Get spider network status and statistics
    Session 687: Removed @login_required - public endpoint for Dashboard

    GET /api/v1/intelligence/spider-status/

    Returns: {
        "success": true,
        "spider_count": 46,
        "active_spiders": [...],
        "total_data_points": 1000,
        "last_24h_data": 50
    }
    """
    try:
        from ai_core.spiders.spider_registry import spider_registry

        # Get spider list
        spider_list = spider_registry.list_spiders()

        # Get data statistics
        total_data = SpiderData.objects.count()
        last_24h = SpiderData.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()

        # Get active spiders (those that have recent data)
        active_spiders = SpiderData.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).values('spider_name').distinct()

        return JsonResponse({
            'success': True,
            'spider_count': len(spider_list),
            'total_spiders': spider_list,
            'active_spiders': [s['spider_name'] for s in active_spiders],
            'total_data_points': total_data,
            'last_24h_data': last_24h,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in spider_network_status: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve spider network status'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def intelligence_data_quality(request):
    """
    Get intelligence data quality metrics

    GET /api/v1/intelligence/data-quality/

    Returns: {
        "success": true,
        "quality_score": 0.85,
        "total_items": 1000,
        "valid_items": 850,
        "recent_items_24h": 50
    }
    """
    try:
        total_items = SpiderData.objects.count()

        # Get items from last 24 hours
        recent_items = SpiderData.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()

        # Calculate quality score (simplified - can be enhanced with real metrics)
        # For now, assume all data is valid
        valid_items = total_items
        quality_score = (valid_items / total_items) if total_items > 0 else 0.0

        return JsonResponse({
            'success': True,
            'quality_score': round(quality_score, 2),
            'total_items': total_items,
            'valid_items': valid_items,
            'recent_items_24h': recent_items,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in intelligence_data_quality: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve data quality metrics'
        }, status=500)
