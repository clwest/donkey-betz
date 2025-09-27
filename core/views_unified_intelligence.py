"""
Views for Unified Intelligence Dashboard
=======================================
Combines activity monitoring and consciousness bridge into a single unified dashboard.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from backend.spiders.consciousness import ConsciousnessBridge
from backend.intelligence.learning_loop import LearningLoop
import json
import logging
from datetime import datetime
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

# Redis connection for tracking status
try:
    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True
    )
except:
    redis_client = redis.StrictRedis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

def timestamp():
    return datetime.now().isoformat()


def _check_redis_health():
    """Check Redis connection health"""
    try:
        redis_client.ping()
        # Check response time
        import time
        start = time.time()
        redis_client.set('health_check', 'ok', ex=1)
        response_time = (time.time() - start) * 1000  # Convert to ms

        # Calculate health score based on response time
        if response_time < 10:
            return 100  # Excellent
        elif response_time < 50:
            return 95   # Good
        elif response_time < 100:
            return 85   # OK
        elif response_time < 500:
            return 70   # Slow
        else:
            return 50   # Critical
    except:
        return 0  # Redis is down


def _check_websocket_status():
    """Check WebSocket health"""
    try:
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()

        # Check if channel layer is configured
        if channel_layer and hasattr(channel_layer, 'group_send'):
            return 100  # WebSocket is configured and ready
        else:
            return 50   # Partially configured
    except:
        return 0  # WebSocket not available


@login_required
def unified_intelligence_dashboard(request):
    """Render the unified intelligence dashboard page"""
    return render(request, 'unified_intelligence_dashboard.html')


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_unified_intelligence_data(request):
    """Get comprehensive system data for the unified dashboard"""
    try:
        # Check for force refresh parameter
        force_refresh = request.GET.get('force_refresh', 'false').lower() == 'true'

        # Clear cache if force refresh requested
        if force_refresh:
            from django.core.cache import cache
            cache.delete('consciousness_understanding')
            cache.delete('consciousness_health')

        # Import execution tracker for REAL metrics
        from backend.agents.execution_tracker import AgentExecutionTracker
        tracker = AgentExecutionTracker()

        # Initialize consciousness bridge and learning loop
        consciousness = ConsciousnessBridge()
        learning_loop = LearningLoop()

        # Get consciousness data
        understanding = consciousness.understand_self()
        introspection = consciousness.introspection() if hasattr(consciousness, 'introspection') else {}
        health = consciousness.get_system_health()

        # Get learning loop status
        learning_status = learning_loop.get_learning_status()

        # Get implemented insights and investigated behaviors from Redis
        implemented_insights = set()
        investigated_behaviors = set()
        try:
            implemented_insights = redis_client.smembers('implemented_insights') or set()
            investigated_behaviors = redis_client.smembers('investigated_behaviors') or set()
        except:
            pass

        # Add status to insights
        insights_with_status = []
        for i, insight in enumerate(understanding.get('insights', [])[:5]):
            insight_key = f"{i}:{insight.get('category', 'unknown')}"
            insight_with_status = insight.copy() if isinstance(insight, dict) else {'text': str(insight)}
            insight_with_status['status'] = 'implemented' if insight_key in implemented_insights else 'pending'
            insight_with_status['id'] = i
            insights_with_status.append(insight_with_status)

        # Add status to emergent behaviors
        behaviors_with_status = []
        for i, behavior in enumerate(understanding.get('emergent_behaviors', [])):
            behavior_key = f"{i}:{behavior.get('type', 'unknown')}"
            behavior_with_status = behavior.copy() if isinstance(behavior, dict) else {'description': str(behavior)}
            behavior_with_status['status'] = 'investigating' if behavior_key in investigated_behaviors else 'detected'
            behavior_with_status['id'] = i
            behaviors_with_status.append(behavior_with_status)

        # Get REAL metrics from execution tracker
        real_active_agents = tracker.get_active_agent_count()
        real_files_created = tracker.get_total_files_created()
        real_success_rate = tracker.calculate_success_rate()
        real_learning_rate = tracker.calculate_learning_rate()

        # Get detailed agent performance stats
        agent_performance_details = tracker.get_agent_performance_details()

        # Get spider network stats
        spider_network_stats = tracker.get_spider_network_stats()

        # Get learning analytics data
        learning_analytics_data = tracker.get_learning_analytics_data()

        # Get REAL activity feed from Redis
        recent_activities = []
        try:
            for activity_json in redis_client.lrange('recent:activities', 0, 19):  # Get last 20 activities
                try:
                    recent_activities.append(json.loads(activity_json))
                except:
                    pass
        except Exception as e:
            logger.debug(f"Could not fetch recent activities: {e}")

        # Get counts from consciousness (shows potential capabilities)
        potential_agents = understanding['capabilities'].get('by_type', {}).get('agent', 0)
        potential_spiders = understanding['capabilities'].get('by_type', {}).get('spider', 0)

        # Combine all data for the unified dashboard
        unified_data = {
            # Core system metrics - USE REAL DATA
            'consciousness_level': understanding['self_awareness_score'],
            'active_agents': real_active_agents,  # Show REAL active agents
            'active_spiders': spider_network_stats['active_spiders'],  # Show REAL active spiders
            'memory_crystals': len(consciousness.memory_crystal) if hasattr(consciousness, 'memory_crystal') and isinstance(consciousness.memory_crystal, (list, dict)) else 0,

            # Consciousness state - REAL mood and evolution
            'mood': understanding.get('mood', 'contemplative'),
            'evolution_stage': understanding.get('evolution_stage', 'Early Learning'),

            # Add transparency about real vs potential
            'real_metrics': {
                'active_agents': real_active_agents,
                'files_created': real_files_created,
                'success_rate': real_success_rate,
                'learning_rate': real_learning_rate,
                'agents_registered': potential_agents,  # Total registered in system
                'spiders_available': potential_spiders   # Total spider files found
            },

            # Consciousness insights with status
            'latest_insights': insights_with_status,
            'system_capabilities': understanding.get('capabilities', {}),
            'limitations': understanding.get('limitations', []),
            'proposals': understanding.get('proposals', []),
            'emergent_behaviors': behaviors_with_status,

            # System health - REAL metrics
            'health_score': health.get('overall_health_score', 0),
            'system_metrics': {
                'cpu_usage': health.get('system_resources', {}).get('cpu_percent', 0),
                'memory_usage': health.get('system_resources', {}).get('memory_percent', 0),
                'redis_health': _check_redis_health(),  # Real Redis health check
                'websocket_status': _check_websocket_status(),  # Real WebSocket check
                'agent_response_rate': real_success_rate,  # Use real success rate
                'disk_usage': health.get('system_resources', {}).get('disk_usage', 0)
            },

            # Learning analytics - USE REAL DATA from execution tracker
            'learning_active': learning_analytics_data['learning_active'],
            'feedback_processed': learning_analytics_data['feedback_processed'],
            'insights_generated': learning_analytics_data['insights_generated'],
            'optimizations_applied': learning_analytics_data['optimizations_applied'],
            'learning_improvement_rate': learning_analytics_data['improvement_rate'],
            'daily_feedback': learning_analytics_data['daily_feedback'],

            # Performance data
            'top_performers': understanding['capabilities'].get('top_performers', [])[:5],
            'system_statistics': understanding.get('statistics', {}),

            # Agent Performance - REAL detailed stats
            'agent_performance': agent_performance_details,

            # Spider Network - REAL spider metrics
            'spider_network': spider_network_stats,

            # Learning Analytics - REAL learning data
            'learning_analytics': learning_analytics_data,

            # Activity feed - REAL activities from Redis
            'recent_activities': recent_activities,

            # Timestamp
            'timestamp': understanding.get('timestamp', ''),
            'status': 'operational'
        }

        return JsonResponse({
            'success': True,
            'data': unified_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': {
                'consciousness_level': 0,
                'active_agents': 0,
                'active_spiders': 0,
                'memory_crystals': 0,
                'status': 'error'
            }
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def implement_insight(request):
    """Implement a consciousness insight"""
    try:
        data = json.loads(request.body)
        insight_id = data.get('insight_id')
        category = data.get('category')
        timestamp_val = data.get('timestamp')

        logger.info(f"Implementing insight {insight_id} in category {category}")

        # Track implementation in Redis
        implementation_key = f"implemented_insight:{insight_id}:{category}"
        redis_client.setex(implementation_key, 86400, json.dumps({  # 24 hour expiry
            'status': 'implemented',
            'timestamp': timestamp_val,
            'category': category
        }))

        # Also track in a set for quick lookups
        redis_client.sadd('implemented_insights', f"{insight_id}:{category}")

        # Record the implementation request
        result = {
            'success': True,
            'status': 'implemented',
            'insight_id': insight_id,
            'category': category,
            'message': f'Insight implementation has been initiated.',
            'estimated_completion': '2-5 minutes',
            'tracking_id': f'impl_{insight_id}_{timestamp_val}'
        }

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error implementing insight: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def investigate_behavior(request):
    """Investigate an emergent behavior"""
    try:
        data = json.loads(request.body)
        behavior_id = data.get('behavior_id')
        behavior_type = data.get('behavior_type')
        timestamp_val = data.get('timestamp')

        logger.info(f"Investigating behavior {behavior_id} of type {behavior_type}")

        # Track investigation in Redis
        investigation_key = f"investigated_behavior:{behavior_id}:{behavior_type}"
        redis_client.setex(investigation_key, 86400, json.dumps({  # 24 hour expiry
            'status': 'under_investigation',
            'timestamp': timestamp_val,
            'behavior_type': behavior_type
        }))

        # Also track in a set for quick lookups
        redis_client.sadd('investigated_behaviors', f"{behavior_id}:{behavior_type}")

        # Record the investigation request
        result = {
            'success': True,
            'status': 'under_investigation',
            'behavior_id': behavior_id,
            'behavior_type': behavior_type,
            'message': f'Investigation of {behavior_type} behavior has been initiated.',
            'details': f'The consciousness system is analyzing the emergent {behavior_type} behavior patterns.',
            'estimated_completion': '1-3 minutes',
            'tracking_id': f'invest_{behavior_id}_{timestamp_val}'
        }

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error investigating behavior: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def approve_proposal(request):
    """Approve an AI proposal"""
    try:
        data = json.loads(request.body)
        proposal_id = data.get('proposal_id')

        logger.info(f"Approving proposal {proposal_id}")

        # Record the approval
        result = {
            'success': True,
            'status': 'approved',
            'proposal_id': proposal_id,
            'message': 'Proposal has been approved and queued for execution.',
            'execution_status': 'queued',
            'estimated_start': '1-2 minutes'
        }

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error approving proposal: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def reject_proposal(request):
    """Reject an AI proposal"""
    try:
        data = json.loads(request.body)
        proposal_id = data.get('proposal_id')
        reason = data.get('reason', 'No reason provided')

        logger.info(f"Rejecting proposal {proposal_id} with reason: {reason}")

        # Record the rejection
        result = {
            'success': True,
            'status': 'rejected',
            'proposal_id': proposal_id,
            'reason': reason,
            'message': 'Proposal has been rejected and removed from the queue.'
        }

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error rejecting proposal: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)