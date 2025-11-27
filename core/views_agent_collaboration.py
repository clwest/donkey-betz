"""
Agent Collaboration API Endpoints
=================================

Session 219 Phase B: API endpoints for agent collaboration features.

Endpoints:
- POST /api/agent-collab/message/ - Send message between agents
- GET /api/agent-collab/messages/{agent}/ - Get messages for agent
- POST /api/agent-collab/collaborate/ - Initiate collaboration
- POST /api/agent-collab/consult/ - Quick expert consultation
- POST /api/agent-collab/consensus/ - Start consensus request
- POST /api/agent-collab/vote/ - Submit vote
- GET /api/agent-collab/consensus/{id}/ - Get consensus status
- POST /api/agent-collab/knowledge/ - Share knowledge
- GET /api/agent-collab/knowledge/ - Query knowledge base
- GET /api/agent-collab/stats/ - Get collaboration statistics
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from core.services.agent_collaboration_hub import (
    get_collaboration_hub,
    MessageType,
    CollaborationProtocol
)

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@login_required
def send_message(request):
    """
    Send a message between agents.

    POST /api/agent-collab/message/

    Body:
    {
        "sender": "image_generation_agent",
        "recipient": "style_discovery_agent",
        "message_type": "request",
        "protocol": "consult",
        "subject": "Need style advice",
        "content": {"question": "What colors work for cyberpunk?"},
        "priority": 6,
        "requires_response": true
    }
    """
    try:
        body = json.loads(request.body)

        hub = get_collaboration_hub()
        message = hub.send_message(
            sender=body.get('sender'),
            recipient=body.get('recipient'),
            message_type=MessageType(body.get('message_type', 'request')),
            protocol=CollaborationProtocol(body.get('protocol', 'inform')),
            subject=body.get('subject', 'Message'),
            content=body.get('content', {}),
            priority=body.get('priority', 5),
            requires_response=body.get('requires_response', False),
            parent_message_id=body.get('parent_message_id')
        )

        return JsonResponse({
            'success': True,
            'message': message.to_dict()
        })

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_messages(request, agent_name: str):
    """
    Get messages for an agent.

    GET /api/agent-collab/messages/{agent_name}/

    Query params:
    - limit: Number of messages (default 50)
    """
    try:
        limit = int(request.GET.get('limit', 50))

        hub = get_collaboration_hub()
        messages = hub.get_messages(agent_name, limit=limit)

        return JsonResponse({
            'success': True,
            'agent': agent_name,
            'messages': messages,
            'count': len(messages)
        })

    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def initiate_collaboration(request):
    """
    Initiate a collaboration between agents.

    POST /api/agent-collab/collaborate/

    Body:
    {
        "initiator": "content_strategy_agent",
        "collaborators": ["trend_analysis_agent", "design_assistant_agent"],
        "protocol": "collaborate",
        "task": {
            "title": "Create viral content strategy",
            "description": "Develop content plan based on current trends"
        }
    }
    """
    try:
        body = json.loads(request.body)

        hub = get_collaboration_hub()
        session_id = hub.initiate_collaboration(
            initiator=body.get('initiator'),
            collaborators=body.get('collaborators', []),
            protocol=CollaborationProtocol(body.get('protocol', 'collaborate')),
            task=body.get('task', {})
        )

        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'initiator': body.get('initiator'),
            'collaborators': body.get('collaborators')
        })

    except Exception as e:
        logger.error(f"Error initiating collaboration: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def consult_expert(request):
    """
    Quick consultation with an expert agent.

    POST /api/agent-collab/consult/

    Body:
    {
        "requester": "image_generation_agent",
        "expert": "prompt_engineering_agent",
        "question": "How do I improve this prompt for better results?",
        "context": {"prompt": "A beautiful sunset"}
    }
    """
    try:
        body = json.loads(request.body)

        hub = get_collaboration_hub()
        message = hub.consult_expert(
            requester=body.get('requester'),
            expert=body.get('expert'),
            question=body.get('question', ''),
            context=body.get('context')
        )

        return JsonResponse({
            'success': True,
            'consultation': message.to_dict()
        })

    except Exception as e:
        logger.error(f"Error consulting expert: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def request_consensus(request):
    """
    Request consensus from multiple agents.

    POST /api/agent-collab/consensus/

    Body:
    {
        "requester": "trend_analysis_agent",
        "voters": ["image_generation_agent", "style_discovery_agent", "design_assistant_agent"],
        "topic": "Best style for Q4 2025",
        "options": ["cyberpunk", "minimalist", "retro"],
        "context": {"season": "winter", "trend_data": {...}},
        "threshold": 0.6
    }
    """
    try:
        body = json.loads(request.body)

        hub = get_collaboration_hub()
        consensus_id = hub.request_consensus(
            requester=body.get('requester'),
            voters=body.get('voters', []),
            topic=body.get('topic', ''),
            options=body.get('options', []),
            context=body.get('context'),
            threshold=body.get('threshold', 0.6)
        )

        return JsonResponse({
            'success': True,
            'consensus_id': consensus_id,
            'topic': body.get('topic'),
            'voters': body.get('voters')
        })

    except Exception as e:
        logger.error(f"Error requesting consensus: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def submit_vote(request):
    """
    Submit a vote in a consensus request.

    POST /api/agent-collab/vote/

    Body:
    {
        "consensus_id": "cons_20251126...",
        "agent_name": "image_generation_agent",
        "vote": "cyberpunk",
        "reasoning": "Based on trending data, cyberpunk is most popular",
        "confidence": 0.85
    }
    """
    try:
        body = json.loads(request.body)

        hub = get_collaboration_hub()
        result = hub.submit_vote(
            consensus_id=body.get('consensus_id'),
            agent_name=body.get('agent_name'),
            vote=body.get('vote'),
            reasoning=body.get('reasoning', ''),
            confidence=body.get('confidence', 0.8)
        )

        return JsonResponse({
            'success': True,
            **result
        })

    except Exception as e:
        logger.error(f"Error submitting vote: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_consensus_status(request, consensus_id: str):
    """
    Get status of a consensus request.

    GET /api/agent-collab/consensus/{consensus_id}/
    """
    try:
        hub = get_collaboration_hub()
        status = hub.get_consensus_status(consensus_id)

        return JsonResponse({
            'success': True,
            **status
        })

    except Exception as e:
        logger.error(f"Error getting consensus status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def share_knowledge(request):
    """
    Share knowledge with other agents.

    POST /api/agent-collab/knowledge/

    Body:
    {
        "agent_name": "trend_analysis_agent",
        "category": "style_trends",
        "title": "Cyberpunk trending in AI art",
        "content": {
            "trend": "cyberpunk",
            "growth_rate": 0.35,
            "peak_platforms": ["midjourney", "civitai"]
        },
        "confidence": 0.9,
        "tags": ["cyberpunk", "ai_art", "trends"]
    }
    """
    try:
        body = json.loads(request.body)

        hub = get_collaboration_hub()
        knowledge_id = hub.share_knowledge(
            agent_name=body.get('agent_name'),
            category=body.get('category', 'general'),
            title=body.get('title', 'Knowledge'),
            content=body.get('content', {}),
            confidence=body.get('confidence', 0.8),
            tags=body.get('tags', [])
        )

        return JsonResponse({
            'success': True,
            'knowledge_id': knowledge_id,
            'title': body.get('title')
        })

    except Exception as e:
        logger.error(f"Error sharing knowledge: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def query_knowledge(request):
    """
    Query the knowledge base.

    GET /api/agent-collab/knowledge/

    Query params:
    - category: Filter by category
    - tags: Comma-separated tags
    - source_agent: Filter by source agent
    - min_confidence: Minimum confidence (0-1)
    - limit: Max results (default 20)
    """
    try:
        category = request.GET.get('category')
        tags_str = request.GET.get('tags')
        tags = tags_str.split(',') if tags_str else None
        source_agent = request.GET.get('source_agent')
        min_confidence = float(request.GET.get('min_confidence', 0))
        limit = int(request.GET.get('limit', 20))

        hub = get_collaboration_hub()
        results = hub.query_knowledge(
            category=category,
            tags=tags,
            source_agent=source_agent,
            min_confidence=min_confidence,
            limit=limit
        )

        return JsonResponse({
            'success': True,
            'knowledge': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Error querying knowledge: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_collaboration_stats(request):
    """
    Get collaboration hub statistics.

    GET /api/agent-collab/stats/
    """
    try:
        hub = get_collaboration_hub()
        stats = hub.get_stats()

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
def get_agent_activity(request, agent_name: str):
    """
    Get activity summary for an agent.

    GET /api/agent-collab/activity/{agent_name}/
    """
    try:
        hub = get_collaboration_hub()
        activity = hub.get_agent_activity(agent_name)

        return JsonResponse({
            'success': True,
            'activity': activity
        })

    except Exception as e:
        logger.error(f"Error getting agent activity: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# URL patterns to add to core/urls.py:
"""
from core.views_agent_collaboration import (
    send_message as collab_send_message,
    get_messages as collab_get_messages,
    initiate_collaboration as collab_initiate,
    consult_expert as collab_consult,
    request_consensus as collab_request_consensus,
    submit_vote as collab_submit_vote,
    get_consensus_status as collab_consensus_status,
    share_knowledge as collab_share_knowledge,
    query_knowledge as collab_query_knowledge,
    get_collaboration_stats as collab_stats,
    get_agent_activity as collab_agent_activity
)

urlpatterns += [
    path('api/agent-collab/message/', collab_send_message, name='collab-send-message'),
    path('api/agent-collab/messages/<str:agent_name>/', collab_get_messages, name='collab-get-messages'),
    path('api/agent-collab/collaborate/', collab_initiate, name='collab-initiate'),
    path('api/agent-collab/consult/', collab_consult, name='collab-consult'),
    path('api/agent-collab/consensus/', collab_request_consensus, name='collab-request-consensus'),
    path('api/agent-collab/vote/', collab_submit_vote, name='collab-submit-vote'),
    path('api/agent-collab/consensus/<str:consensus_id>/', collab_consensus_status, name='collab-consensus-status'),
    path('api/agent-collab/knowledge/', collab_share_knowledge, name='collab-share-knowledge'),
    path('api/agent-collab/knowledge/', collab_query_knowledge, name='collab-query-knowledge'),
    path('api/agent-collab/stats/', collab_stats, name='collab-stats'),
    path('api/agent-collab/activity/<str:agent_name>/', collab_agent_activity, name='collab-agent-activity'),
]
"""
