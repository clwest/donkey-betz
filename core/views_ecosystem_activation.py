"""
Ecosystem Activation Views
=========================

API endpoints to activate and manage the real data ecosystem.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from ai_core.intelligence.real_data_orchestrator import (
    real_data_orchestrator,
    activate_ecosystem_sync,
    process_opportunity_sync
)
from ai_core.spiders.live_job_scraper import scrape_jobs_sync
import json
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def activate_ecosystem(request):
    """Activate the full AI ecosystem with real data"""
    try:
        # Run the activation
        result = activate_ecosystem_sync()

        return Response({
            'success': True,
            'data': result,
            'message': 'AI Ecosystem activated successfully!'
        })
    except Exception as e:
        logger.error(f"Ecosystem activation failed: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to activate ecosystem'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def ecosystem_status(request):
    """Get current ecosystem status"""
    try:
        # Get cached status
        status = cache.get('ecosystem_status', {})

        # Get component statuses
        active_spiders = cache.get('active_spiders', [])
        connected_agents = cache.get('connected_agents', [])
        active_advisors = cache.get('active_advisors', [])
        revenue_tracker = cache.get('revenue_tracker', {})
        live_opportunities = cache.get('live_opportunities', [])

        return Response({
            'success': True,
            'data': {
                'status': status.get('status', 'inactive'),
                'timestamp': status.get('timestamp'),
                'components': {
                    'spiders': {
                        'active': len(active_spiders),
                        'data_collected': sum(s.get('data_collected', 0) for s in active_spiders)
                    },
                    'agents': {
                        'connected': len(connected_agents),
                        'processing_capacity': sum(a.get('processing_rate', 0) for a in connected_agents)
                    },
                    'advisors': {
                        'active': len(active_advisors),
                        'guidance_provided': sum(a.get('guidance_provided', 0) for a in active_advisors)
                    },
                    'opportunities': {
                        'live': len(live_opportunities),
                        'sources': list(set(o.get('source', 'unknown') for o in live_opportunities))
                    },
                    'revenue': revenue_tracker
                }
            }
        })
    except Exception as e:
        logger.error(f"Failed to get ecosystem status: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_live_opportunities(request):
    """Get real-time opportunities from spiders"""
    try:
        # Get fresh opportunities
        opportunities = scrape_jobs_sync()

        # Cache them
        cache.set('live_opportunities', opportunities, 1800)

        return Response({
            'success': True,
            'data': {
                'opportunities': opportunities,
                'total': len(opportunities),
                'sources': list(set(o.get('source', 'unknown') for o in opportunities))
            }
        })
    except Exception as e:
        logger.error(f"Failed to get live opportunities: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def process_opportunity(request):
    """Process an opportunity through the full AI pipeline"""
    try:
        opportunity_id = request.data.get('opportunity_id')
        user_profile = request.data.get('user_profile', {})

        if not opportunity_id:
            return Response({
                'success': False,
                'error': 'opportunity_id is required'
            }, status=400)

        # Process through the pipeline
        result = process_opportunity_sync(opportunity_id, user_profile)

        return Response({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Failed to process opportunity: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_agent_status(request):
    """Get status of all connected agents"""
    try:
        connected_agents = cache.get('connected_agents', [])

        # Group by type
        agent_groups = {}
        for agent in connected_agents:
            agent_type = agent.get('agent_type', 'unknown')
            if agent_type not in agent_groups:
                agent_groups[agent_type] = []
            agent_groups[agent_type].append(agent)

        return Response({
            'success': True,
            'data': {
                'total_agents': len(connected_agents),
                'agent_groups': agent_groups,
                'total_processing_capacity': sum(a.get('processing_rate', 0) for a in connected_agents)
            }
        })
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_advisor_network(request):
    """Get status of advisor network"""
    try:
        active_advisors = cache.get('active_advisors', [])

        return Response({
            'success': True,
            'data': {
                'total_advisors': len(active_advisors),
                'advisors': active_advisors,
                'total_guidance': sum(a.get('guidance_provided', 0) for a in active_advisors),
                'average_success_rate': sum(a.get('success_rate', 0) for a in active_advisors) / max(len(active_advisors), 1)
            }
        })
    except Exception as e:
        logger.error(f"Failed to get advisor network: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_revenue_tracking(request):
    """Get revenue tracking data"""
    try:
        revenue_tracker = cache.get('revenue_tracker', {})
        recent_decisions = cache.get('recent_decisions', [])

        # Calculate decision stats
        total_decisions = len(recent_decisions)
        applied = len([d for d in recent_decisions if d.get('decision') == 'apply'])
        skipped = len([d for d in recent_decisions if d.get('decision') == 'skip'])

        return Response({
            'success': True,
            'data': {
                'revenue': revenue_tracker,
                'decisions': {
                    'total': total_decisions,
                    'applied': applied,
                    'skipped': skipped,
                    'apply_rate': applied / max(total_decisions, 1)
                },
                'recent_decisions': recent_decisions[:10]
            }
        })
    except Exception as e:
        logger.error(f"Failed to get revenue tracking: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)