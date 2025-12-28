"""
Agent Intelligence API Endpoints
=================================

Session 219: API endpoints for accessing agent intelligence feeds.
These endpoints expose spider-collected data that has been routed
to AI Content Creation agents.

Endpoints:
- GET /api/agent-intelligence/agents/ - List all registered agents
- GET /api/agent-intelligence/feed/{agent_name}/ - Get agent's intelligence feed
- GET /api/agent-intelligence/trends/ - Get current trends across all agents
- GET /api/agent-intelligence/suggestions/ - Get content suggestions
- GET /api/agent-intelligence/stats/ - Get routing and agent statistics
- GET /api/agent-intelligence/categories/ - Get spider categories and their agents
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from core.services.ai_content_agents import (
    get_agent,
    get_all_agents,
    get_agents_by_capability,
    get_agents_for_spider_category,
    get_agent_stats,
    agent_intelligence_service,
    AgentCapability
)

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@login_required
def list_agents(request):
    """
    List all registered AI Content Creation agents.

    GET /api/agent-intelligence/agents/

    Response:
    {
        "success": true,
        "agents": [
            {
                "name": "image_generation_agent",
                "description": "...",
                "capabilities": ["image_generation", "style_analysis"],
                "data_interests": ["creative_assets", "ai_creative"],
                "priority": 10,
                "is_active": true
            },
            ...
        ],
        "total": 14
    }
    """
    try:
        agents = get_all_agents()

        agent_list = [
            {
                'name': agent.name,
                'description': agent.description,
                'capabilities': [cap.value for cap in agent.capabilities],
                'data_interests': agent.data_interests,
                'priority': agent.priority,
                'is_active': agent.is_active
            }
            for agent in agents.values()
        ]

        # Sort by priority
        agent_list.sort(key=lambda x: x['priority'], reverse=True)

        return JsonResponse({
            'success': True,
            'agents': agent_list,
            'total': len(agent_list)
        })

    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_agent_feed(request, agent_name: str):
    """
    Get the intelligence feed for a specific agent.

    GET /api/agent-intelligence/feed/{agent_name}/

    Query params:
    - limit: Number of items to return (default 20, max 100)

    Response:
    {
        "success": true,
        "agent": {
            "name": "image_generation_agent",
            "description": "..."
        },
        "feed": [
            {
                "spider_name": "midjourney_spider",
                "data_type": "trending_styles",
                "content": {...},
                "quality_score": 0.85,
                "received_at": "2025-11-26T..."
            },
            ...
        ],
        "count": 20
    }
    """
    try:
        agent = get_agent(agent_name)
        if not agent:
            return JsonResponse({
                'success': False,
                'error': f'Agent "{agent_name}" not found'
            }, status=404)

        limit = min(int(request.GET.get('limit', 20)), 100)

        feed = agent_intelligence_service.get_intelligence(agent_name, limit=limit)

        return JsonResponse({
            'success': True,
            'agent': {
                'name': agent.name,
                'description': agent.description,
                'capabilities': [cap.value for cap in agent.capabilities],
                'data_interests': agent.data_interests
            },
            'feed': feed,
            'count': len(feed)
        })

    except Exception as e:
        logger.error(f"Error getting agent feed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_trends(request):
    """
    Get current trending topics across all agents.

    GET /api/agent-intelligence/trends/

    Query params:
    - limit: Number of trending items (default 20, max 50)
    - category: Filter by spider category (optional)

    Response:
    {
        "success": true,
        "trends": [
            {
                "title": "Cyberpunk style trending",
                "source": "midjourney_spider",
                "category": "ai_creative",
                "received_at": "2025-11-26T..."
            },
            ...
        ],
        "count": 20
    }
    """
    try:
        limit = min(int(request.GET.get('limit', 20)), 50)
        category = request.GET.get('category')

        trends = agent_intelligence_service.get_trending_topics(limit=limit)

        # Filter by category if specified
        if category:
            trends = [t for t in trends if t.get('spider_category') == category]

        return JsonResponse({
            'success': True,
            'trends': trends,
            'count': len(trends)
        })

    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_suggestions(request):
    """
    Get actionable content suggestions based on current intelligence.

    GET /api/agent-intelligence/suggestions/

    Query params:
    - type: Suggestion type (image, video, product, content) - optional
    - limit: Number of suggestions (default 10, max 30)

    Response:
    {
        "success": true,
        "suggestions": [
            {
                "type": "image_prompt",
                "title": "Try this trending style",
                "suggestion": "Cyberpunk cityscape with neon lights...",
                "source_agent": "prompt_engineering_agent",
                "confidence": 0.85
            },
            ...
        ],
        "count": 10
    }
    """
    try:
        suggestion_type = request.GET.get('type')
        limit = min(int(request.GET.get('limit', 10)), 30)

        # Get trends and transform into suggestions
        trends = agent_intelligence_service.get_trending_topics(limit=50)

        suggestions = []
        for trend in trends[:limit]:
            # Determine suggestion type based on source
            spider_cat = trend.get('spider_category', '')
            data = trend.get('data', {})

            if spider_cat in ['ai_creative', 'design', 'creative_assets']:
                stype = 'image_prompt'
            elif spider_cat in ['digital_products']:
                stype = 'product_idea'
            elif spider_cat in ['content_creation', 'news']:
                stype = 'content_topic'
            else:
                stype = 'general'

            # Filter by type if specified
            if suggestion_type and stype != suggestion_type:
                continue

            suggestions.append({
                'type': stype,
                'title': data.get('title', trend.get('spider_name', 'Unknown')),
                'suggestion': data.get('description', data.get('summary', '')),
                'source_agent': trend.get('agent_name', 'trend_analysis_agent'),
                'source_spider': trend.get('spider_name', ''),
                'link': data.get('link', ''),
                'confidence': trend.get('quality_score', 0.7),
                'received_at': trend.get('received_at', '')
            })

        return JsonResponse({
            'success': True,
            'suggestions': suggestions[:limit],
            'count': len(suggestions[:limit])
        })

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_stats(request):
    """
    Get statistics about agents and intelligence routing.

    GET /api/agent-intelligence/stats/

    Response:
    {
        "success": true,
        "stats": {
            "total_agents": 14,
            "active_agents": 14,
            "capability_distribution": {...},
            "interest_distribution": {...},
            "intelligence_cache_size": 150,
            "agents_by_priority": [...]
        }
    }
    """
    try:
        stats = get_agent_stats()

        # Add intelligence cache stats
        cache_size = sum(
            len(items)
            for items in agent_intelligence_service.intelligence_cache.values()
        )
        stats['intelligence_cache_size'] = cache_size
        stats['agents_with_intelligence'] = len(agent_intelligence_service.intelligence_cache)

        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_categories(request):
    """
    Get spider categories and the agents that receive their data.

    GET /api/agent-intelligence/categories/

    Response:
    {
        "success": true,
        "categories": {
            "creative_assets": {
                "spiders": ["envato", "creativemarket", ...],
                "agents": ["image_generation_agent", ...]
            },
            ...
        }
    }
    """
    try:
        from ai_core.agents.spider_agent_connector import spider_agent_connector

        categories = {}
        for category, agents in spider_agent_connector.routing_table.items():
            # Get agents interested in this category
            interested_agents = get_agents_for_spider_category(category)

            categories[category] = {
                'routed_to': agents,
                'interested_agents': [a.name for a in interested_agents],
                'agent_count': len(agents)
            }

        return JsonResponse({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_capabilities(request):
    """
    Get all available agent capabilities.

    GET /api/agent-intelligence/capabilities/

    Response:
    {
        "success": true,
        "capabilities": [
            {"name": "image_generation", "agent_count": 5},
            ...
        ]
    }
    """
    try:
        capabilities = []
        for cap in AgentCapability:
            agents = get_agents_by_capability(cap)
            capabilities.append({
                'name': cap.value,
                'agent_count': len(agents),
                'agents': [a.name for a in agents]
            })

        return JsonResponse({
            'success': True,
            'capabilities': capabilities,
            'total': len(capabilities)
        })

    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_bridge_status(request):
    """
    Get the spider intelligence service status.

    GET /api/agent-intelligence/bridge/

    Response:
    {
        "success": true,
        "bridge": {
            "is_running": true,
            "spider_count": 72,
            "data_records": 20000,
            ...
        }
    }

    NOTE: Session 497 - Deprecated spider_intelligence_bridge removed.
    Now uses SpiderIntelligenceService instead.
    """
    try:
        from core.services.spider_intelligence import get_spider_intelligence_service
        from core.models_unified_system import SpiderData

        service = get_spider_intelligence_service()
        spider_count = len(service.get_available_categories())
        data_count = SpiderData.objects.count()

        return JsonResponse({
            'success': True,
            'bridge': {
                'is_running': True,
                'service': 'SpiderIntelligenceService',
                'spider_categories': spider_count,
                'data_records': data_count,
                'note': 'Legacy bridge deprecated - using SpiderIntelligenceService'
            }
        })

    except Exception as e:
        logger.error(f"Error getting intelligence status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def inject_test_data(request):
    """
    Inject test intelligence data for development/testing.

    POST /api/agent-intelligence/test/

    Body:
    {
        "spider_name": "midjourney_trends",
        "category": "ai_creative",
        "data": {
            "title": "Test trend",
            "description": "Test description"
        }
    }

    Response:
    {
        "success": true,
        "message": "Injected test data"
    }

    NOTE: Session 497 - Updated to use SpiderData model directly.
    """
    try:
        import json
        from django.utils import timezone
        from core.models_unified_system import SpiderData

        body = json.loads(request.body)

        spider_name = body.get('spider_name', 'test_spider')
        category = body.get('category', 'ai_creative')
        data = body.get('data', {
            'title': 'Test Intelligence Data',
            'description': 'Injected via API for testing'
        })

        # Create SpiderData record directly
        spider_data = SpiderData.objects.create(
            spider_name=spider_name,
            category=category,
            title=data.get('title', 'Test Data'),
            description=data.get('description', 'Test description'),
            source_url=data.get('url', 'https://test.local/'),
            data=data,
            quality_score=0.5,  # Test data gets low quality score
            created_at=timezone.now()
        )

        return JsonResponse({
            'success': True,
            'message': f'Injected test data from {spider_name} ({category})',
            'id': str(spider_data.id)
        })

    except Exception as e:
        logger.error(f"Error injecting test data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# URL patterns to add to core/urls.py:
"""
from core.views_agent_intelligence import (
    list_agents,
    get_agent_feed,
    get_trends,
    get_suggestions,
    get_stats,
    get_categories,
    get_capabilities,
    get_bridge_status,
    inject_test_data
)

urlpatterns += [
    path('api/agent-intelligence/agents/', list_agents, name='ai_agents_list'),
    path('api/agent-intelligence/feed/<str:agent_name>/', get_agent_feed, name='ai_agent_feed'),
    path('api/agent-intelligence/trends/', get_trends, name='ai_trends'),
    path('api/agent-intelligence/suggestions/', get_suggestions, name='ai_suggestions'),
    path('api/agent-intelligence/stats/', get_stats, name='ai_stats'),
    path('api/agent-intelligence/categories/', get_categories, name='ai_categories'),
    path('api/agent-intelligence/capabilities/', get_capabilities, name='ai_capabilities'),
    path('api/agent-intelligence/bridge/', get_bridge_status, name='ai_bridge_status'),
    path('api/agent-intelligence/test/', inject_test_data, name='ai_inject_test'),
]
"""
