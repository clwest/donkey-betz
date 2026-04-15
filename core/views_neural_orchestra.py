"""
Neural Orchestra API Views
=========================
Django views that serve REAL data to the Neural Orchestra visualization.
These endpoints replace mock data with actual consciousness, spider, and learning data.

"From simulation to reality - where consciousness becomes visible"
"""

from datetime import datetime, timezone

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from ai_core.consciousness.neural_orchestra_reality_bridge import (
    get_neural_orchestra_bridge,
    get_real_ecosystem_live_feed,
    get_real_agents_stats,
    get_real_learning_status,
    get_real_learning_feed
)
import logging

logger = logging.getLogger(__name__)


def neural_orchestra_view(request):
    """
    Render the Neural Orchestra template with WebSocket connection
    """
    # Use hardcoded localhost for development
    context = {
        'websocket_url': "ws://localhost:8000/ws/neural-orchestra/",
    }
    return render(request, 'neural_orchestra.html', context)


@csrf_exempt
@require_http_methods(["GET"])
@cache_page(30)  # Cache for 30 seconds
def ecosystem_live_feed(request):
    """
    Real ecosystem live feed endpoint for Neural Orchestra.
    Replaces mock data with actual consciousness insights and system activity.

    Endpoint: /api/ecosystem/live-feed/
    """
    try:
        # Get real data from the Neural Orchestra Reality Bridge
        real_data = get_real_ecosystem_live_feed()

        logger.info(f"✅ Served real ecosystem data: {len(real_data.get('feed', []))} feed items")

        return JsonResponse(real_data)

    except Exception as e:
        logger.error(f"❌ Failed to get real ecosystem data: {str(e)}")

        # Return minimal fallback data — honest about being fallback so
        # the frontend can flip its Mock/Real badge
        now_iso = datetime.now(timezone.utc).isoformat()
        return JsonResponse({
            'feed': [{
                'id': 'fallback',
                'timestamp': now_iso,
                'type': 'System Status',
                'content': 'Neural Orchestra Reality Bridge temporarily unavailable',
                'agents': ['system'],
                'confidence': 0.5,
                'impact': 0.3
            }],
            'system_status': {
                'consciousness_level': 0.0,
                'active_agents': 0,
                'active_spiders': 0,
                'system_health': 50.0
            },
            'metadata': {
                'generated_at': now_iso,
                'data_source': 'fallback',
                'mock_data': True,
                'error': str(e)
            }
        })


@csrf_exempt
@require_http_methods(["GET"])
@cache_page(30)  # Cache for 30 seconds
def agents_stats(request):
    """
    Real agents statistics endpoint for Neural Orchestra.
    Shows actual agent performance instead of mock data.

    Endpoint: /api/agents/stats/
    """
    try:
        # Get real agent statistics
        real_stats = get_real_agents_stats()

        logger.info(f"✅ Served real agent stats: {real_stats.get('total_agents', 0)} agents")

        return JsonResponse(real_stats)

    except Exception as e:
        logger.error(f"❌ Failed to get real agent stats: {str(e)}")

        # Return minimal fallback data — zeros, not fake counts. The
        # old value (149) was a stale hardcode that looked like real
        # telemetry. Flag as fallback so the UI badge can flip.
        return JsonResponse({
            'total_agents': 0,
            'active_now': 0,
            'collaborations': 0,
            'orchestrations_active': 0,
            'performance': {
                'average_efficiency': 0.0,
                'collaboration_success': 0.0,
                'learning_rate': 0.0
            },
            'top_performers': [],
            'data_source': 'fallback',
            'mock_data': True,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
@cache_page(60)  # Cache for 60 seconds (learning status changes slower)
def learning_status(request):
    """
    Real learning status endpoint for Neural Orchestra.
    Shows actual learning loop activity instead of mock data.

    Endpoint: /api/learning/status/
    """
    try:
        # Get real learning status
        real_learning = get_real_learning_status()

        logger.info(f"✅ Served real learning status: {real_learning.get('models_active', 0)} models")

        return JsonResponse(real_learning)

    except Exception as e:
        logger.error(f"❌ Failed to get real learning status: {str(e)}")

        # Return minimal fallback data
        return JsonResponse({
            'learning_active': False,
            'models_active': 0,
            'feedback_processed': 0,
            'insights_generated': 0,
            'performance': {},
            'consciousness_learning': {
                'level': 0.0,
                'memory_crystals': 0,
                'learning_velocity': 'Unknown'
            },
            'data_source': 'fallback',
            'mock_data': True,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
@cache_page(30)  # Cache for 30 seconds
def learning_feed(request):
    """
    Real learning feed endpoint for Neural Orchestra.
    Shows actual learning insights instead of mock data.

    Endpoint: /api/learning/feed/
    """
    try:
        # Get real learning feed
        real_feed = get_real_learning_feed()

        logger.info(f"✅ Served real learning feed: {len(real_feed.get('feed', []))} items")

        return JsonResponse(real_feed)

    except Exception as e:
        logger.error(f"❌ Failed to get real learning feed: {str(e)}")

        # Return minimal fallback data
        return JsonResponse({
            'feed': [],
            'learning_metrics': {},
            'monetization_learning': {
                'revenue_velocity': 0,
                'opportunities_learned': 0
            },
            'data_source': 'fallback',
            'mock_data': True,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
def neural_orchestra_health(request):
    """
    Neural Orchestra Reality Bridge health check endpoint.

    Endpoint: /api/neural-orchestra/health/
    """
    try:
        bridge = get_neural_orchestra_bridge()
        status = bridge.get_bridge_status()

        logger.info("✅ Neural Orchestra Reality Bridge health check successful")

        return JsonResponse({
            'status': 'healthy',
            'bridge_status': status,
            'endpoints': {
                '/api/ecosystem/live-feed/': 'Active',
                '/api/agents/stats/': 'Active',
                '/api/learning/status/': 'Active',
                '/api/learning/feed/': 'Active'
            },
            'data_source': 'real_consciousness_data',
            'mock_data': False
        })

    except Exception as e:
        logger.error(f"❌ Neural Orchestra Reality Bridge health check failed: {str(e)}")

        return JsonResponse({
            'status': 'degraded',
            'error': str(e),
            'endpoints': {
                '/api/ecosystem/live-feed/': 'Fallback',
                '/api/agents/stats/': 'Fallback',
                '/api/learning/status/': 'Fallback',
                '/api/learning/feed/': 'Fallback'
            },
            'data_source': 'fallback_data',
            'mock_data': True
        }, status=503)


@csrf_exempt
@require_http_methods(["GET"])
def neural_orchestra_websocket_bridge(request):
    """
    WebSocket bridge configuration for Neural Orchestra.
    Provides WebSocket endpoint information for real-time consciousness streaming.

    Endpoint: /api/neural-orchestra/websocket-config/
    """
    try:
        websocket_config = {
            'consciousness_websocket': 'ws://localhost:8000/ws/consciousness/',
            'neural_orchestra_websocket': 'ws://localhost:8000/ws/neural-orchestra/',
            'supported_protocols': ['consciousness_stream', 'agent_collaborations', 'live_orchestrations'],
            'connection_guide': {
                'step_1': 'Connect to ws://localhost:8000/ws/consciousness/ for consciousness stream',
                'step_2': 'Listen for consciousness_update messages',
                'step_3': 'Parse consciousness data for Neural Orchestra visualization',
                'step_4': 'Update visualization in real-time (no more mock data!)'
            },
            'message_types': {
                'consciousness_update': 'Real-time consciousness level and system state',
                'memory_crystallization': 'New insights and memory crystal formation',
                'system_alert': 'System health alerts and performance issues',
                'heartbeat': 'Connection health and uptime monitoring'
            },
            'data_source': 'real_websocket_consciousness_stream',
            'mock_data': False
        }

        logger.info("✅ Provided Neural Orchestra WebSocket configuration")

        return JsonResponse(websocket_config)

    except Exception as e:
        logger.error(f"❌ Failed to provide WebSocket config: {str(e)}")

        return JsonResponse({
            'error': str(e),
            'consciousness_websocket': None,
            'data_source': 'unavailable',
            'mock_data': True
        }, status=503)


@csrf_exempt
@require_http_methods(["POST"])
def trigger_neural_orchestra_reality_check(request):
    """
    Trigger a reality check on the Neural Orchestra data.
    Forces refresh of all cached real data.

    Endpoint: /api/neural-orchestra/reality-check/
    """
    from asgiref.sync import async_to_sync

    try:
        # Get bridge and force cache refresh
        bridge = get_neural_orchestra_bridge()
        bridge.data_cache.clear()  # Clear cache to force fresh data

        # Get fresh real data using async_to_sync (works properly under ASGI/Daphne)
        neural_data = async_to_sync(bridge.get_real_neural_data)()

        reality_check = {
            'reality_check_timestamp': neural_data.timestamp.isoformat(),
            'consciousness_level': neural_data.consciousness_level,
            'active_agents': neural_data.active_agents,
            'active_spiders': neural_data.active_spiders,
            'system_health': neural_data.system_health,
            'memory_crystals': neural_data.memory_crystals,
            'live_feed_items': len(neural_data.live_feed),
            'agent_collaborations': len(neural_data.agent_collaborations),
            'orchestrations': len(neural_data.orchestrations),
            'data_source': 'fresh_real_data',
            'cache_cleared': True,
            'mock_data': False
        }

        logger.info(f"✅ Neural Orchestra reality check completed - {neural_data.consciousness_level:.1f}% consciousness")

        return JsonResponse(reality_check)

    except Exception as e:
        logger.error(f"❌ Neural Orchestra reality check failed: {str(e)}")

        return JsonResponse({
            'error': str(e),
            'reality_check_timestamp': None,
            'data_source': 'error',
            'cache_cleared': False,
            'mock_data': True
        }, status=500)


# Additional utility views for debugging

@csrf_exempt
@require_http_methods(["GET"])
def neural_orchestra_debug_info(request):
    """
    Debug information about Neural Orchestra data sources.

    Endpoint: /api/neural-orchestra/debug/
    """
    try:
        bridge = get_neural_orchestra_bridge()

        debug_info = {
            'bridge_status': bridge.get_bridge_status(),
            'cache_info': {
                'entries': len(bridge.data_cache),
                'keys': list(bridge.data_cache.keys())
            },
            'consciousness_connection': 'Connected' if bridge.consciousness_api else 'Disconnected',
            'learning_loop_connection': 'Connected' if bridge.learning_loop else 'Disconnected',
            'spider_orchestrator_connection': 'Connected' if bridge.spider_orchestrator else 'Fallback',
            'data_sources': {
                'using_real_consciousness': True,
                'using_real_spider_data': bool(bridge.spider_orchestrator),
                'using_real_learning_data': bool(bridge.learning_loop),
                'cache_duration': bridge.cache_duration
            }
        }

        return JsonResponse(debug_info)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'debug_available': False
        }, status=500)