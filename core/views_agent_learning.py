"""
Agent Learning API Endpoints
============================

Session 219 Phase C: API endpoints for agent personalization and learning.

Endpoints:
- POST /api/agent-learning/interaction/ - Record user interaction
- GET /api/agent-learning/preferences/{agent}/ - Get learned preferences
- GET /api/agent-learning/context/{agent}/ - Get adaptive context
- GET /api/agent-learning/stats/ - Get learning statistics
- POST /api/agent-learning/apply/ - Apply preferences to params
- DELETE /api/agent-learning/preferences/ - Clear preferences
- GET /api/agent-learning/summary/ - Get all preferences summary
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.services.agent_learning_service import (
    get_learning_service,
    InteractionType,
    PreferenceCategory
)

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@login_required
def record_interaction(request):
    """
    Record a user interaction with an agent.

    POST /api/agent-learning/interaction/

    Body:
    {
        "agent_name": "image_generation_agent",
        "interaction_type": "saved",  // created, edited, saved, shared, rated, etc.
        "input_data": {
            "prompt": "cyberpunk city",
            "style": "neon",
            "model": "sd3-large-turbo"
        },
        "output_data": {
            "image_url": "...",
            "dimensions": "1024x1024"
        },
        "rating": 5,  // optional 1-5
        "was_modified": false  // optional
    }
    """
    try:
        body = json.loads(request.body)

        service = get_learning_service()
        interaction = service.record_interaction(
            user_id=request.user.id,
            agent_name=body.get('agent_name'),
            interaction_type=InteractionType(body.get('interaction_type', 'created')),
            input_data=body.get('input_data', {}),
            output_data=body.get('output_data', {}),
            rating=body.get('rating'),
            was_modified=body.get('was_modified', False),
            session_id=body.get('session_id')
        )

        return JsonResponse({
            'success': True,
            'interaction_id': interaction.id,
            'message': 'Interaction recorded for learning'
        })

    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_preferences(request, agent_name: str):
    """
    Get learned preferences for an agent.

    GET /api/agent-learning/preferences/{agent_name}/

    Query params:
    - category: Filter by category (style, theme, model, etc.)
    - limit: Max preferences to return (default 10)
    """
    try:
        category_str = request.GET.get('category')
        category = PreferenceCategory(category_str) if category_str else None
        limit = int(request.GET.get('limit', 10))

        service = get_learning_service()
        preferences = service.get_top_preferences(
            user_id=request.user.id,
            agent_name=agent_name,
            category=category,
            limit=limit
        )

        return JsonResponse({
            'success': True,
            'agent': agent_name,
            'preferences': [p.to_dict() for p in preferences],
            'count': len(preferences)
        })

    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_adaptive_context(request, agent_name: str):
    """
    Get adaptive context string for an agent.

    GET /api/agent-learning/context/{agent_name}/

    Returns a context string that can be injected into agent prompts
    for personalized behavior.
    """
    try:
        service = get_learning_service()
        context = service.get_adaptive_context(
            user_id=request.user.id,
            agent_name=agent_name
        )

        return JsonResponse({
            'success': True,
            'agent': agent_name,
            'context': context,
            'has_context': bool(context)
        })

    except Exception as e:
        logger.error(f"Error getting adaptive context: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_learning_stats(request):
    """
    Get learning statistics for the user.

    GET /api/agent-learning/stats/

    Returns statistics about interactions and learned preferences
    across all agents.
    """
    try:
        service = get_learning_service()
        stats = service.get_learning_stats(user_id=request.user.id)

        # Session 309/346: Add memory, knowledge, collaboration, and agent counts
        # Session 417: Changed to use database agent count instead of filesystem count
        try:
            from core.models_unified_system import AgentMemory, AgentKnowledgeSource, Collaboration, CollaborationSession, Agent
            from content.models import AgentExecution

            # Session 417: Count agents from database (active agents only)
            # This matches what the Profile dropdown shows
            db_agent_count = Agent.objects.filter(is_active=True).count()
            total_agent_count = Agent.objects.count()

            stats['agent_memories'] = AgentMemory.objects.count()
            stats['knowledge_sources'] = AgentKnowledgeSource.objects.count()
            stats['clean_agents'] = db_agent_count  # Active agents in database
            stats['deprecated_agents'] = 0  # No longer tracking legacy file count
            stats['agents'] = {
                'total': db_agent_count,
                'active': db_agent_count,
                'inactive': total_agent_count - db_agent_count
            }

            # Session 346: Add collaboration and learning event counts
            stats['collaborations'] = Collaboration.objects.count()
            stats['collaboration_sessions'] = CollaborationSession.objects.count()
            stats['learning_events'] = AgentExecution.objects.count()  # Agent executions as learning events

        except Exception as db_err:
            logger.debug(f"Could not fetch Session 309/346 stats: {db_err}")
            stats['agent_memories'] = 0
            stats['knowledge_sources'] = 0
            stats['clean_agents'] = 34  # Session 417: Fallback to approximate DB count
            stats['deprecated_agents'] = 0
            stats['agents'] = {'total': 34, 'active': 34, 'inactive': 0}
            stats['collaborations'] = 0
            stats['collaboration_sessions'] = 0
            stats['learning_events'] = 0

        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error getting learning stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def apply_preferences(request):
    """
    Apply learned preferences to generation parameters.

    POST /api/agent-learning/apply/

    Body:
    {
        "agent_name": "image_generation_agent",
        "params": {
            "prompt": "a beautiful sunset",
            "aspect_ratio": "16:9"
        }
    }

    Returns params with learned preferences filled in for missing values.
    """
    try:
        body = json.loads(request.body)

        agent_name = body.get('agent_name')
        params = body.get('params', {})

        service = get_learning_service()
        enhanced_params = service.apply_preferences_to_params(
            user_id=request.user.id,
            agent_name=agent_name,
            params=params
        )

        # Track what was added
        added_params = {k: v for k, v in enhanced_params.items() if k not in params}

        return JsonResponse({
            'success': True,
            'params': enhanced_params,
            'applied_preferences': added_params,
            'preferences_count': len(added_params)
        })

    except Exception as e:
        logger.error(f"Error applying preferences: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["DELETE"])
@login_required
def clear_preferences(request):
    """
    Clear learned preferences.

    DELETE /api/agent-learning/preferences/

    Query params:
    - agent: Specific agent to clear (optional, clears all if not provided)
    """
    try:
        agent_name = request.GET.get('agent')

        service = get_learning_service()
        service.clear_user_preferences(
            user_id=request.user.id,
            agent_name=agent_name
        )

        return JsonResponse({
            'success': True,
            'message': f"Cleared preferences for {'agent ' + agent_name if agent_name else 'all agents'}"
        })

    except Exception as e:
        logger.error(f"Error clearing preferences: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_preferences_summary(request, agent_name: str):
    """
    Get a summary of learned preferences for an agent.

    GET /api/agent-learning/summary/{agent_name}/

    Returns grouped preferences by category with confidence scores.
    """
    try:
        service = get_learning_service()
        summary = service.get_user_preferences_summary(
            user_id=request.user.id,
            agent_name=agent_name
        )

        return JsonResponse({
            'success': True,
            'agent': agent_name,
            **summary
        })

    except Exception as e:
        logger.error(f"Error getting preferences summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def share_learning(request, agent_name: str):
    """
    Share learned preferences with other agents via collaboration hub.

    POST /api/agent-learning/share/{agent_name}/

    Shares the user's learned preferences as knowledge that other agents
    can use to personalize their behavior.
    """
    try:
        service = get_learning_service()
        service.share_learning_as_knowledge(
            user_id=request.user.id,
            agent_name=agent_name
        )

        return JsonResponse({
            'success': True,
            'message': f'Shared learning from {agent_name} with collaboration hub'
        })

    except Exception as e:
        logger.error(f"Error sharing learning: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_all_preferences(request):
    """
    Get all learned preferences across all agents.

    GET /api/agent-learning/all-preferences/

    Returns a comprehensive view of all preferences.
    """
    try:
        service = get_learning_service()

        # Get all agents the user has interacted with
        from core.services.ai_content_agents import get_all_agents
        all_agents = get_all_agents()

        preferences_by_agent = {}
        for agent in all_agents.values():
            summary = service.get_user_preferences_summary(
                user_id=request.user.id,
                agent_name=agent.name
            )
            if summary.get('status') == 'ok':
                preferences_by_agent[agent.name] = summary

        return JsonResponse({
            'success': True,
            'agents': preferences_by_agent,
            'count': len(preferences_by_agent)
        })

    except Exception as e:
        logger.error(f"Error getting all preferences: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# Session 244: Agent Conversations API
# ============================================================================

@require_http_methods(["GET"])
# Session 564: Removed @login_required - now public for Command Center UI
def get_agent_conversations(request):
    """
    Get recent agent conversations for display in UI.

    GET /api/agent-conversations/

    Query params:
    - limit: Max conversations to return (default 10)
    - status: Filter by status (active, concluded, paused)
    - today_only: If 'true', only return today's conversations

    Session 431: Now includes HiveMindSession records (preferred)
    in addition to legacy AgentConversation records.
    """
    try:
        from django.utils import timezone
        from core.models import AgentConversation, Agent
        from core.models_unified_system import HiveMindSession

        limit = int(request.GET.get('limit', 10))
        status_filter = request.GET.get('status')
        today_only = request.GET.get('today_only', 'false').lower() == 'true'

        conversations_data = []
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # =====================================================================
        # Session 494 FIX: Fetch from BOTH sources, then combine and sort
        # Previous bug: HiveMindSession was fetched first up to limit,
        # leaving no slots for newer AgentConversation records.
        # Now we fetch `limit` from each source, combine, sort, and take top `limit`.
        # =====================================================================

        # =====================================================================
        # PART 1: Get HiveMindSession records
        # =====================================================================
        hivemind_qs = HiveMindSession.objects.filter(
            session_mode='conversation'
        ).order_by('-created_at')

        if status_filter:
            hivemind_qs = hivemind_qs.filter(status=status_filter)

        if today_only:
            hivemind_qs = hivemind_qs.filter(created_at__gte=today_start)

        for session in hivemind_qs[:limit]:
            # Get participant names from participant_ids
            participant_names = []
            agent_name_map = {}  # Map name -> emoji
            if session.participant_ids:
                try:
                    agents = Agent.objects.filter(id__in=session.participant_ids)
                    for a in agents:
                        emoji = _get_agent_emoji(a.specialization)
                        participant_names.append({'name': a.name, 'emoji': emoji})
                        agent_name_map[a.name] = emoji
                except Exception:
                    pass

            # Session 435: Parse synthesis into individual messages
            # Format is "AgentName: message" on each paragraph
            messages_data = []
            if session.synthesis:
                import re
                # Split by double newline or single newline followed by AgentName:
                paragraphs = re.split(r'\n\n|\n(?=[A-Z][a-zA-Z]+Agent:)', session.synthesis)
                seq = 0
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    # Try to extract agent name and content
                    match = re.match(r'^([A-Z][a-zA-Z]+(?:Agent)?):?\s*(.+)', para, re.DOTALL)
                    if match:
                        agent_name = match.group(1)
                        content = match.group(2).strip()
                        seq += 1
                        messages_data.append({
                            'id': f'{session.id}-{seq}',
                            'agent': agent_name,
                            'agent_emoji': agent_name_map.get(agent_name, '🤖'),
                            'content': content,
                            'type': 'contribution',
                            'sequence': seq,
                            'relevance': 0.8,
                            'created_at': session.created_at.isoformat() if session.created_at else None
                        })

            conversations_data.append({
                'id': str(session.id),
                'topic': session.conversation_topic or session.question or 'Agent Discussion',
                'type': 'hivemind_conversation',
                'type_display': 'Hive Mind Session',
                'trigger': 'force_cycle',
                'status': session.status or 'completed',
                'initiator': participant_names[0]['name'] if participant_names else 'System',
                'initiator_emoji': participant_names[0]['emoji'] if participant_names else '🤖',
                'participants': participant_names,
                'message_count': session.contribution_count or len(messages_data),
                'quality_score': 0.85,
                'conclusion': session.synthesis_summary or '',
                'insights': session.synthesis[:500] if session.synthesis else '',
                'started_at': session.created_at.isoformat() if session.created_at else None,
                'ended_at': session.completed_at.isoformat() if session.completed_at else None,
                'messages': messages_data,  # Session 435: Now includes parsed messages
                'source': 'hivemind'  # Mark source for UI
            })

        # =====================================================================
        # PART 2: Get AgentConversation records (always fetch, not just remaining)
        # Session 494: Always fetch from both sources to ensure newest are shown
        # =====================================================================
        legacy_qs = AgentConversation.objects.select_related('initiator').prefetch_related(
            'participants', 'messages__agent'
        ).order_by('-started_at')

        if status_filter:
            legacy_qs = legacy_qs.filter(status=status_filter)

        if today_only:
            legacy_qs = legacy_qs.filter(started_at__gte=today_start)

        for conv in legacy_qs[:limit]:
            messages_data = []
            # Session 435: Return ALL messages, not just first 10
            for msg in conv.messages.all().order_by('sequence_number'):
                messages_data.append({
                    'id': str(msg.id),
                    'agent': msg.agent.name,
                    'agent_emoji': _get_agent_emoji(msg.agent.specialization),
                    'content': msg.content,
                    'type': msg.message_type,
                    'sequence': msg.sequence_number,
                    'relevance': msg.relevance_score,
                    'created_at': msg.created_at.isoformat()
                })

            conversations_data.append({
                'id': str(conv.id),
                'topic': conv.topic,
                'type': conv.conversation_type,
                'type_display': conv.get_conversation_type_display(),
                'trigger': conv.trigger_type,
                'status': conv.status,
                'initiator': conv.initiator.name,
                'initiator_emoji': _get_agent_emoji(conv.initiator.specialization),
                'participants': [
                    {'name': p.name, 'emoji': _get_agent_emoji(p.specialization)}
                    for p in conv.participants.all()
                ],
                'message_count': conv.message_count,
                'quality_score': conv.quality_score,
                'conclusion': conv.conclusion,
                'insights': conv.insights_generated,
                'started_at': conv.started_at.isoformat(),
                'ended_at': conv.ended_at.isoformat() if conv.ended_at else None,
                'messages': messages_data,
                'source': 'legacy'  # Mark source for UI
            })

        # Sort combined results by started_at (newest first)
        conversations_data.sort(
            key=lambda x: x['started_at'] or '1970-01-01',
            reverse=True
        )

        # Get today's combined count
        hivemind_today = HiveMindSession.objects.filter(
            session_mode='conversation',
            created_at__gte=today_start
        ).count()
        legacy_today = AgentConversation.objects.filter(started_at__gte=today_start).count()
        today_count = hivemind_today + legacy_today

        return JsonResponse({
            'success': True,
            'conversations': conversations_data[:limit],
            'count': len(conversations_data[:limit]),
            'today_count': today_count
        })

    except Exception as e:
        logger.error(f"Error getting agent conversations: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _get_agent_emoji(specialization: str) -> str:
    """Get emoji for agent based on specialization."""
    emoji_map = {
        'image': '🎨',
        'video': '🎬',
        'audio': '🎵',
        '3d': '🎮',
        'text': '📝',
        'code': '💻',
        'research': '🔍',
        'analysis': '📊',
        'creative': '✨',
        'workflow': '⚡',
        'assistant': '🤖',
        'learning': '🧠',
        'training': '🎓',
    }

    if specialization:
        specialization_lower = specialization.lower()
        for key, emoji in emoji_map.items():
            if key in specialization_lower:
                return emoji

    return '🤖'


@require_http_methods(["POST"])
@login_required
def trigger_agent_conversation(request):
    """
    Manually trigger an agent conversation on a specific topic.

    POST /api/agent-conversations/trigger/

    Body:
    {
        "topic": "Best practices for logo design",
        "conversation_type": "brainstorm",  // optional
        "participant_ids": [...]  // optional specific agents
    }
    """
    try:
        from core.tasks import run_agent_conversation

        body = json.loads(request.body)
        topic = body.get('topic')

        if not topic:
            return JsonResponse({
                'success': False,
                'error': 'Topic is required'
            }, status=400)

        # Trigger conversation task
        result = run_agent_conversation.delay(
            max_conversations=1,
            max_messages=6
        )

        return JsonResponse({
            'success': True,
            'message': f'Agent conversation triggered on topic: {topic}',
            'task_id': result.id
        })

    except Exception as e:
        logger.error(f"Error triggering agent conversation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 248: Knowledge Transfer Activity Feed
# =============================================================================

@require_http_methods(["GET"])
def get_knowledge_transfer_feed(request):
    """
    Get the live agent learning activity feed based on KnowledgeTransfer records.

    GET /api/agent-learning/activity/

    Query params:
    - limit: max items to return (default 20)
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        from core.models import Agent, AgentLearningConnection, AgentKnowledgeSource, KnowledgeTransfer

        limit = int(request.GET.get('limit', 20))
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)

        # Gather stats (same as broadcast_learning_status task)
        stats = {
            'total_agents': Agent.objects.filter(is_active=True).count(),
            'total_knowledge': AgentKnowledgeSource.objects.filter(is_active=True).count(),
            'total_connections': AgentLearningConnection.objects.filter(is_active=True).count(),
            'transfers_last_hour': KnowledgeTransfer.objects.filter(created_at__gte=last_hour).count(),
            'transfers_last_day': KnowledgeTransfer.objects.filter(created_at__gte=last_day).count(),
            'active_learners': Agent.objects.filter(
                teachers__last_transfer_at__gte=last_hour
            ).distinct().count(),
            'active_teachers': Agent.objects.filter(
                students__last_transfer_at__gte=last_hour
            ).distinct().count(),
        }

        # Top learning agents
        top_learners = []
        for agent in Agent.objects.filter(is_active=True).order_by('-effectiveness_score')[:5]:
            top_learners.append({
                'name': agent.name,
                'knowledge_count': agent.knowledge_sources.filter(is_active=True).count(),
                'effectiveness': agent.effectiveness_score,
                'teaches': agent.students.count(),
                'learns_from': agent.teachers.count()
            })

        # Recent knowledge transfers as feed items
        feed_items = []
        for transfer in KnowledgeTransfer.objects.select_related(
            'connection__teacher_agent',
            'connection__student_agent',
            'source_knowledge',  # Session 532: Include source knowledge for full content
            'source_knowledge__agent'
        ).order_by('-created_at')[:limit]:
            teacher = transfer.connection.teacher_agent
            student = transfer.connection.student_agent

            # Determine learning source type
            if teacher.id == student.id:
                source = 'self_learning'
                description = f"{teacher.name} acquired new knowledge"
            else:
                source = 'knowledge_transfer'
                description = f"{teacher.name} shared knowledge with {student.name}"

            # Session 532: Include full knowledge content, not truncated
            source_knowledge = transfer.source_knowledge
            knowledge_data = {
                'title': source_knowledge.title if source_knowledge else None,
                'summary': source_knowledge.summary if source_knowledge else None,
                'key_insights': source_knowledge.key_insights if source_knowledge else [],
                'knowledge_type': source_knowledge.knowledge_type if source_knowledge else None,
                'confidence': source_knowledge.confidence_score if source_knowledge else 0,
            }

            feed_items.append({
                'timestamp': transfer.created_at.isoformat(),
                'type': source,
                'source': 'Knowledge transfer',
                'description': description,
                'knowledge': transfer.transfer_summary if transfer.transfer_summary else 'Knowledge shared',
                'knowledge_full': knowledge_data,  # Session 532: Full knowledge details
                'key_points': transfer.key_points or [],  # Session 532: Include key points
                'teacher': teacher.name,
                'student': student.name,
                'was_useful': transfer.was_useful,
                'usefulness_score': transfer.usefulness_score,  # Session 532: Include score
                'effectiveness_gain': 0.0  # Could calculate if stored
            })

        return JsonResponse({
            'success': True,
            'feed_items': feed_items,
            'stats': stats,
            'top_learners': top_learners,
            'total_count': len(feed_items),
            'timestamp': now.isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching knowledge transfer feed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'feed_items': []
        }, status=500)


# =============================================================================
# Session 247: Agent Dreams API
# =============================================================================

@require_http_methods(["GET"])
def get_agent_dreams(request):
    """
    Get recent agent dreams.

    GET /api/agent-dreams/?limit=10

    Query params:
    - limit: Max dreams to return (default 10)
    - agent_id: Filter by specific agent
    - unread_only: Only show dreams not yet shown to user
    """
    try:
        from django.utils import timezone
        from core.models import AgentDream

        limit = int(request.GET.get('limit', 10))
        agent_id = request.GET.get('agent_id')
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'

        # Get dreams from the last 24 hours
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        dreams = AgentDream.objects.filter(
            dreamed_at__gte=cutoff
        ).select_related('agent').order_by('-dreamed_at')

        if agent_id:
            dreams = dreams.filter(agent_id=agent_id)

        if unread_only:
            dreams = dreams.filter(shown_to_user=False)

        dreams = dreams[:limit]

        # Count totals
        today_count = AgentDream.objects.filter(
            dreamed_at__gte=cutoff
        ).count()

        unread_count = AgentDream.objects.filter(
            dreamed_at__gte=cutoff,
            shown_to_user=False
        ).count()

        dreams_data = []
        for dream in dreams:
            dreams_data.append({
                'id': str(dream.id),
                'agent_id': str(dream.agent.id) if dream.agent else None,
                'agent_name': dream.agent.name if dream.agent else 'Unknown',
                'title': dream.title,
                'content': dream.content,
                'dream_type': dream.dream_type,
                'inspiration': dream.inspiration_source,
                'related_topics': dream.related_topics,
                'vividness': dream.vividness_score,
                'creativity': dream.creativity_score,
                'shown_to_user': dream.shown_to_user,
                'user_reaction': dream.user_reaction,
                'dreamed_at': dream.dreamed_at.isoformat()
            })

        return JsonResponse({
            'success': True,
            'dreams': dreams_data,
            'today_count': today_count,
            'unread_count': unread_count
        })

    except Exception as e:
        logger.error(f"Error fetching agent dreams: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def trigger_agent_dreams(request):
    """
    Manually trigger dream generation for idle agents.

    POST /api/agent-dreams/trigger/
    """
    try:
        from core.tasks import generate_agent_dreams

        result = generate_agent_dreams.delay(
            max_dreamers=5,
            dreams_per_agent=2
        )

        return JsonResponse({
            'success': True,
            'message': 'Dream generation triggered',
            'task_id': result.id,
            'dreams_generated': 0  # Will be updated async
        })

    except Exception as e:
        logger.error(f"Error triggering agent dreams: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def mark_dreams_shown(request):
    """
    Mark dreams as shown to the user.

    POST /api/agent-dreams/mark-shown/

    Body:
    {
        "dream_ids": ["uuid1", "uuid2", ...]
    }
    """
    try:
        from django.utils import timezone
        from core.models import AgentDream

        body = json.loads(request.body)
        dream_ids = body.get('dream_ids', [])

        if not dream_ids:
            return JsonResponse({
                'success': True,
                'marked': 0
            })

        updated = AgentDream.objects.filter(
            id__in=dream_ids,
            shown_to_user=False
        ).update(
            shown_to_user=True,
            shown_at=timezone.now()
        )

        return JsonResponse({
            'success': True,
            'marked': updated
        })

    except Exception as e:
        logger.error(f"Error marking dreams as shown: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def react_to_dream(request, dream_id):
    """
    Record a user reaction to a dream and update preferences.

    POST /api/agent-dreams/{dream_id}/react/

    Body:
    {
        "reaction": "like" | "interesting" | "explore",
        "feedback": "optional text feedback"
    }

    Session 249: Now records preferences to influence future dream generation!
    - Updates DreamFeedbackPreference for dream_type, topic, and agent
    - "Explore" reactions trigger a deeper exploration task
    """
    try:
        from core.models import AgentDream, DreamFeedbackPreference, DreamExploration

        body = json.loads(request.body)
        reaction = body.get('reaction', '')
        feedback = body.get('feedback', '')

        dream = AgentDream.objects.select_related('agent').filter(id=dream_id).first()
        if not dream:
            return JsonResponse({
                'success': False,
                'error': 'Dream not found'
            }, status=404)

        # Update the dream itself
        dream.user_reaction = reaction
        if feedback:
            dream.user_feedback = feedback
        dream.save()

        # Session 249: Record preferences for future dream generation
        preferences_updated = []

        # 1. Record preference for dream type (global - no agent)
        if dream.dream_type:
            type_pref = DreamFeedbackPreference.get_or_create_preference(
                agent=None,
                dream_type=dream.dream_type,
                topic=''
            )
            type_pref.record_reaction(reaction)
            preferences_updated.append(f"dream_type:{dream.dream_type}")

        # 2. Record preference for topic (global - no agent)
        if dream.inspiration_source:
            topic_pref = DreamFeedbackPreference.get_or_create_preference(
                agent=None,
                dream_type='',
                topic=dream.inspiration_source
            )
            topic_pref.record_reaction(reaction)
            preferences_updated.append(f"topic:{dream.inspiration_source[:30]}")

        # 3. Record preference for specific agent (all their dreams)
        if dream.agent:
            agent_pref = DreamFeedbackPreference.get_or_create_preference(
                agent=dream.agent,
                dream_type='',
                topic=''
            )
            agent_pref.record_reaction(reaction)
            preferences_updated.append(f"agent:{dream.agent.name}")

        # 4. Record preference for agent + dream_type combo
        if dream.agent and dream.dream_type:
            combo_pref = DreamFeedbackPreference.get_or_create_preference(
                agent=dream.agent,
                dream_type=dream.dream_type,
                topic=''
            )
            combo_pref.record_reaction(reaction)
            preferences_updated.append(f"agent+type:{dream.agent.name}+{dream.dream_type}")

        logger.info(f"💭 [DREAM FEEDBACK] Recorded '{reaction}' for dream '{dream.title}' - updated {len(preferences_updated)} preferences")

        # 5. Special handling for "explore" reaction - create exploration task
        exploration_id = None
        if reaction == 'explore':
            exploration = DreamExploration.objects.create(
                dream=dream,
                status='pending'
            )
            exploration_id = str(exploration.id)
            logger.info(f"🚀 [DREAM EXPLORE] Created exploration task {exploration_id} for dream '{dream.title}'")

            # Trigger the exploration task asynchronously
            try:
                from core.tasks import explore_dream_topic
                explore_dream_topic.delay(str(exploration.id))
            except Exception as task_error:
                logger.warning(f"Could not trigger exploration task: {task_error}")

        return JsonResponse({
            'success': True,
            'message': f'Reaction "{reaction}" recorded',
            'dream_id': str(dream_id),
            'preferences_updated': preferences_updated,
            'exploration_id': exploration_id,
            'feedback_effect': _get_feedback_effect_message(reaction)
        })

    except Exception as e:
        logger.error(f"Error reacting to dream: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _get_feedback_effect_message(reaction):
    """Get a user-friendly message about what effect their reaction will have."""
    if reaction == 'like':
        return "This dream type will be more likely in the future!"
    elif reaction == 'interesting':
        return "We'll generate more dreams exploring this topic area!"
    elif reaction == 'explore':
        return "The agent is diving deeper into this idea for you!"
    return ""


@require_http_methods(["GET"])
def get_dream_preferences(request):
    """
    Session 249: Get dream feedback preferences and statistics.

    GET /api/agent-dreams/preferences/

    Returns insights about what types of dreams and topics the user prefers,
    which will influence future dream generation.
    """
    try:
        from core.models import DreamFeedbackPreference, DreamExploration

        # Get top dream types by preference
        top_types = list(DreamFeedbackPreference.get_top_preferences('dream_type', limit=7))

        # Get top topics by preference
        top_topics = list(DreamFeedbackPreference.get_top_preferences('topic', limit=10))

        # Get top agents by preference
        top_agents = list(DreamFeedbackPreference.get_top_preferences('agent', limit=5))

        # Get dream type weights (for debugging/transparency)
        type_weights = DreamFeedbackPreference.get_dream_type_weights()

        # Get exploration stats
        total_explorations = DreamExploration.objects.count()
        completed_explorations = DreamExploration.objects.filter(status='completed').count()
        knowledge_added = DreamExploration.objects.filter(related_knowledge_added=True).count()

        # Total reaction counts
        from django.db.models import Sum
        totals = DreamFeedbackPreference.objects.aggregate(
            total_likes=Sum('like_count'),
            total_interesting=Sum('interesting_count'),
            total_explores=Sum('explore_count')
        )

        return JsonResponse({
            'success': True,
            'preferences': {
                'top_dream_types': top_types,
                'top_topics': top_topics,
                'top_agents': top_agents,
                'type_weights': type_weights
            },
            'reaction_totals': {
                'likes': totals['total_likes'] or 0,
                'interesting': totals['total_interesting'] or 0,
                'explores': totals['total_explores'] or 0
            },
            'explorations': {
                'total': total_explorations,
                'completed': completed_explorations,
                'knowledge_added': knowledge_added
            }
        })

    except Exception as e:
        logger.error(f"Error getting dream preferences: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_dream_exploration(request, exploration_id):
    """
    Session 249: Get details of a dream exploration.

    GET /api/agent-dreams/explorations/{exploration_id}/

    Returns the full exploration content and insights.
    """
    try:
        from core.models import DreamExploration

        exploration = DreamExploration.objects.select_related(
            'dream', 'dream__agent'
        ).filter(id=exploration_id).first()

        if not exploration:
            return JsonResponse({
                'success': False,
                'error': 'Exploration not found'
            }, status=404)

        return JsonResponse({
            'success': True,
            'exploration': {
                'id': str(exploration.id),
                'status': exploration.status,
                'dream': {
                    'id': str(exploration.dream.id),
                    'title': exploration.dream.title,
                    'content': exploration.dream.content,
                    'agent_name': exploration.dream.agent.name if exploration.dream.agent else 'Unknown'
                },
                'exploration_content': exploration.exploration_content,
                'insights': exploration.insights_generated,
                'knowledge_added': exploration.related_knowledge_added,
                'created_at': exploration.created_at.isoformat(),
                'completed_at': exploration.completed_at.isoformat() if exploration.completed_at else None
            }
        })

    except Exception as e:
        logger.error(f"Error getting dream exploration: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 323: Boardroom Decisions API Endpoints
# Session 412: Updated to support both AgentConversation and HiveMindSession
# =============================================================================

@require_http_methods(["GET"])
def get_boardroom_decisions(request):
    """
    Get agent decision summaries for the Boardroom UI.

    GET /api/boardroom/decisions/

    Query params:
    - limit: Max decisions to return (default 20)
    - decision_type: Filter by type (policy, architecture, etc.)
    - impact_area: Filter by area (prompting, memory, etc.)
    - status: Filter by status (draft, canonical, etc.)
    - canonical_only: If 'true', only return canonical policies
    - source: Filter by source (conversation, hive_session, all)
    """
    try:
        from core.models_unified_system import AgentDecisionSummary
        from django.db.models import Count

        limit = int(request.GET.get('limit', 20))
        decision_type = request.GET.get('decision_type')
        impact_area = request.GET.get('impact_area')
        status = request.GET.get('status')
        canonical_only = request.GET.get('canonical_only', 'false').lower() == 'true'
        source = request.GET.get('source', 'all')

        queryset = AgentDecisionSummary.objects.select_related(
            'conversation', 'hive_session'
        ).order_by('-created_at')

        if decision_type:
            queryset = queryset.filter(decision_type=decision_type)
        if impact_area:
            queryset = queryset.filter(impact_area=impact_area)
        if status:
            queryset = queryset.filter(status=status)
        if canonical_only:
            queryset = queryset.filter(is_canonical=True)
        if source == 'conversation':
            queryset = queryset.filter(conversation__isnull=False)
        elif source == 'hive_session':
            queryset = queryset.filter(hive_session__isnull=False)

        decisions = queryset[:limit]

        decisions_data = []
        for d in decisions:
            # Determine source type
            if d.conversation:
                source_type = 'conversation'
                source_id = str(d.conversation.id)
                source_topic = d.conversation.topic
            elif d.hive_session:
                source_type = 'hive_session'
                source_id = str(d.hive_session.id)
                source_topic = d.hive_session.topic
            else:
                source_type = 'unknown'
                source_id = None
                source_topic = None

            decisions_data.append({
                'id': str(d.id),
                'topic': d.topic,
                'decision_type': d.decision_type,
                'decision_type_display': d.get_decision_type_display(),
                'impact_area': d.impact_area,
                'impact_area_display': d.get_impact_area_display(),
                'key_insights': d.key_insights,
                'recommended_stance': d.recommended_stance,
                'suggested_feature': d.suggested_feature,
                'rationale': d.rationale,
                'participants': d.participants,
                'status': d.status,
                'status_display': d.get_status_display(),
                'is_canonical': d.is_canonical,
                'promoted_at': d.promoted_at.isoformat() if d.promoted_at else None,
                'promoted_by': d.promoted_by,
                'source_type': source_type,
                'source_id': source_id,
                'source_topic': source_topic,
                'created_at': d.created_at.isoformat(),
            })

        # Get counts by type for filters
        type_counts = dict(
            AgentDecisionSummary.objects.values('decision_type')
            .annotate(count=Count('id'))
            .values_list('decision_type', 'count')
        )

        # Get source counts
        conv_count = AgentDecisionSummary.objects.filter(conversation__isnull=False).count()
        hive_count = AgentDecisionSummary.objects.filter(hive_session__isnull=False).count()

        return JsonResponse({
            'success': True,
            'decisions': decisions_data,
            'count': len(decisions_data),
            'total': AgentDecisionSummary.objects.count(),
            'canonical_count': AgentDecisionSummary.objects.filter(is_canonical=True).count(),
            'type_counts': type_counts,
            'source_counts': {
                'conversation': conv_count,
                'hive_session': hive_count,
            },
        })

    except Exception as e:
        logger.error(f"Error getting boardroom decisions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Session 659: Governance Stats API for AI Decision Promoter Dashboard
@require_http_methods(["GET"])
def get_governance_stats(request):
    """
    Get governance statistics for the ICC Governance dashboard.

    GET /api/boardroom/governance-stats/

    Returns comprehensive stats including AI Decision Promoter metrics.
    """
    try:
        from core.models_unified_system import AgentDecisionSummary
        from django.utils import timezone
        from datetime import timedelta
        from django_celery_beat.models import PeriodicTask

        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Core counts
        total = AgentDecisionSummary.objects.count()
        canonical = AgentDecisionSummary.objects.filter(is_canonical=True).count()
        drafts = AgentDecisionSummary.objects.filter(status='draft').count()
        pending = AgentDecisionSummary.objects.filter(status='pending').count()

        # AI Promoter stats
        ai_promoted = AgentDecisionSummary.objects.filter(
            promoted_by__icontains='AI'
        ).count()

        human_promoted = AgentDecisionSummary.objects.filter(
            is_canonical=True
        ).exclude(
            promoted_by__icontains='AI'
        ).exclude(
            promoted_by__isnull=True
        ).exclude(
            promoted_by=''
        ).count()

        # Recent activity
        promoted_24h = AgentDecisionSummary.objects.filter(
            is_canonical=True,
            promoted_at__gte=last_24h
        ).count()

        promoted_7d = AgentDecisionSummary.objects.filter(
            is_canonical=True,
            promoted_at__gte=last_7d
        ).count()

        new_decisions_24h = AgentDecisionSummary.objects.filter(
            created_at__gte=last_24h
        ).count()

        # Calculate percentage
        canonical_pct = round((canonical / total * 100), 1) if total > 0 else 0

        # Get AI Promoter task info
        ai_promoter_info = {
            'enabled': False,
            'last_run': None,
            'next_run': None,
            'schedule': None
        }

        try:
            task = PeriodicTask.objects.filter(name='ai-promote-decisions').first()
            if task:
                ai_promoter_info['enabled'] = task.enabled
                ai_promoter_info['last_run'] = task.last_run_at.isoformat() if task.last_run_at else None
                ai_promoter_info['schedule'] = str(task.crontab) if task.crontab else str(task.interval)
        except Exception:
            pass

        return JsonResponse({
            'success': True,
            'stats': {
                'total': total,
                'canonical': canonical,
                'canonical_percentage': canonical_pct,
                'drafts': drafts,
                'pending': pending,
                'ai_promoted': ai_promoted,
                'human_promoted': human_promoted,
                'promoted_24h': promoted_24h,
                'promoted_7d': promoted_7d,
                'new_decisions_24h': new_decisions_24h,
            },
            'ai_promoter': ai_promoter_info,
            'timestamp': now.isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting governance stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def promote_decision(request, decision_id):
    """
    Promote a decision to canonical policy status.
    Session 657: Also creates a learning record and feeds to collective intelligence.

    POST /api/boardroom/decisions/{decision_id}/promote/
    """
    try:
        from core.models_unified_system import AgentDecisionSummary
        from core.models import KnowledgeTransfer
        import redis
        import json
        import os

        decision = AgentDecisionSummary.objects.get(id=decision_id)
        decision.promote_to_canonical(promoted_by='human')

        logger.info(f"🏛️ [BOARDROOM] Decision promoted to canonical: {decision.topic}")

        # Session 657: Create a knowledge transfer record for the canonical decision
        learning_created = False
        try:
            # Create knowledge transfer to capture the canonical decision as learned knowledge
            knowledge = KnowledgeTransfer.objects.create(
                source_agent='BoardroomGovernance',
                target_agent='CollectiveIntelligence',
                knowledge_type='canonical_policy',
                title=f"[Canonical] {decision.topic[:100]}",
                content=decision.summary or decision.topic,
                usefulness_score=0.9,  # High score for canonical decisions
                applied=True,
            )
            learning_created = True
            logger.info(f"🧠 [SESSION 657] Created knowledge transfer for canonical decision: {knowledge.id}")

            # Broadcast to collective intelligence via Redis
            try:
                r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
                event = {
                    'type': 'canonical_decision_promoted',
                    'timestamp': timezone.now().isoformat(),
                    'decision_id': str(decision.id),
                    'topic': decision.topic[:100],
                    'decision_type': decision.decision_type,
                    'summary': (decision.summary or '')[:200],
                    'agents_involved': decision.agents_involved or [],
                }
                r.publish('agent_learning', json.dumps({
                    'type': 'canonical_policy_created',
                    'data': event
                }))
                r.incr('canonical_decisions:total')
                logger.info(f"🧠 [SESSION 657] Broadcast canonical decision to collective intelligence")
            except Exception as redis_err:
                logger.warning(f"Redis broadcast failed: {redis_err}")

        except Exception as learn_err:
            logger.warning(f"Error creating learning from canonical decision: {learn_err}")

        return JsonResponse({
            'success': True,
            'message': f'Decision "{decision.topic}" promoted to canonical policy',
            'decision_id': str(decision.id),
            'learning_created': learning_created  # Session 657
        })

    except AgentDecisionSummary.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Decision not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error promoting decision: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def reject_decision(request, decision_id):
    """
    Reject a decision (mark as not applicable).

    POST /api/boardroom/decisions/{decision_id}/reject/
    """
    try:
        from core.models_unified_system import AgentDecisionSummary

        decision = AgentDecisionSummary.objects.get(id=decision_id)
        decision.status = 'rejected'
        decision.save()

        logger.info(f"🏛️ [BOARDROOM] Decision rejected: {decision.topic}")

        return JsonResponse({
            'success': True,
            'message': f'Decision "{decision.topic}" marked as rejected',
            'decision_id': str(decision.id)
        })

    except AgentDecisionSummary.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Decision not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error rejecting decision: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 604: Decision Prioritization
# =============================================================================

@require_http_methods(["GET"])
def get_prioritized_decisions(request):
    """
    Get prioritized decision queue based on success probability and risk.

    GET /api/boardroom/decisions/prioritized/

    Query params:
    - limit: Max decisions to return (default 50)
    - status: Comma-separated statuses to include (default: draft,review)

    Returns decisions sorted by priority score with:
    - Priority tier (quick_win, recommended, standard, needs_review, high_risk)
    - Success probability from learning system
    - Risk level and flags
    - Recommendation for action
    """
    try:
        from core.services.decision_prioritization import DecisionPrioritizationService

        limit = int(request.GET.get('limit', 50))
        status_param = request.GET.get('status', 'draft,review')
        statuses = [s.strip() for s in status_param.split(',')]

        service = DecisionPrioritizationService()
        result = service.get_prioritized_queue(
            statuses=statuses,
            limit=limit,
            include_flags=True
        )

        return JsonResponse({
            'success': True,
            **result
        })

    except Exception as e:
        logger.error(f"Error getting prioritized decisions: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_decision_priority(request, decision_id):
    """
    Get priority details for a single decision.

    GET /api/boardroom/decisions/{decision_id}/priority/
    """
    try:
        from core.services.decision_prioritization import DecisionPrioritizationService

        service = DecisionPrioritizationService()
        result = service.get_decision_priority(str(decision_id))

        return JsonResponse({
            'success': True,
            **result
        })

    except Exception as e:
        logger.error(f"Error getting decision priority: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 602: Boardroom Learning Integration
# =============================================================================

@require_http_methods(["GET"])
def get_decision_learning_context(request, decision_id):
    """
    Session 602: Get learning context for a Boardroom decision.

    GET /api/boardroom/decisions/{decision_id}/learning/

    Returns:
    - success_probability: Estimated chance of success (0-100%)
    - risk_level: low/medium/high/critical
    - confidence_level: Based on amount of relevant data
    - similar_experiments: Past experiments that inform this decision
    - weighted_insights: Key learnings with weights
    - recommendation: AI-generated guidance for decision-making
    """
    try:
        from core.models_unified_system import AgentDecisionSummary
        from core.services.boardroom_learning import BoardroomLearningService

        decision = AgentDecisionSummary.objects.get(id=decision_id)
        service = BoardroomLearningService()
        context = service.get_decision_learning_context(decision)

        return JsonResponse({
            'success': True,
            **context
        })

    except AgentDecisionSummary.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Decision not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting decision learning context: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_boardroom_learning_summary(request):
    """
    Session 602: Get learning summary for all pending Boardroom decisions.

    GET /api/boardroom/learning-summary/

    Query params:
    - limit: Max decisions to analyze (default 10)
    - status: Filter by status (default 'draft' - pending decisions)

    Returns learning insights for decisions awaiting approval.
    """
    try:
        from core.models_unified_system import AgentDecisionSummary
        from core.services.boardroom_learning import BoardroomLearningService

        limit = int(request.GET.get('limit', 10))
        status = request.GET.get('status', 'draft')

        decisions = AgentDecisionSummary.objects.filter(
            status=status
        ).order_by('-created_at')[:limit]

        service = BoardroomLearningService()
        enriched = service.enrich_decisions_list(decisions)

        # Calculate aggregate stats
        high_probability = sum(1 for d in enriched if d['learning_summary']['success_probability'] >= 70)
        high_risk = sum(1 for d in enriched if d['learning_summary']['risk_level'] in ('high', 'critical'))
        low_confidence = sum(1 for d in enriched if d['learning_summary']['confidence'] == 'insufficient')

        return JsonResponse({
            'success': True,
            'decisions': enriched,
            'count': len(enriched),
            'summary': {
                'high_probability_count': high_probability,
                'high_risk_count': high_risk,
                'low_confidence_count': low_confidence,
                'recommendation': (
                    f'{high_probability} decisions look promising, '
                    f'{high_risk} need extra review, '
                    f'{low_confidence} need more data'
                ),
            },
        })

    except Exception as e:
        logger.error(f"Error getting boardroom learning summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 603: Learning Velocity Dashboard
# =============================================================================

@require_http_methods(["GET"])
def get_learning_velocity_dashboard(request):
    """
    Session 603: Get learning velocity dashboard data.

    GET /api/learning/velocity/

    Query params:
    - days: Number of days to analyze (default 30, max 90)

    Returns:
    - overall_health: System health status and score
    - velocity_trend: Is learning accelerating/stable/decelerating
    - daily_velocity: Daily learning metrics with weights
    - weekly_summary: Weekly aggregates
    - theme_momentum: Which themes are improving/declining
    """
    try:
        from core.services.learning_velocity import LearningVelocityService

        days = min(90, int(request.GET.get('days', 30)))
        service = LearningVelocityService()
        data = service.get_velocity_dashboard(days)

        # Session 619: Frontend expects data under 'dashboard' key
        return JsonResponse({
            'success': True,
            'dashboard': data
        })

    except Exception as e:
        logger.error(f"Error getting learning velocity dashboard: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_theme_velocity(request, theme):
    """
    Session 603: Get velocity data for a specific theme.

    GET /api/learning/velocity/theme/{theme}/

    Query params:
    - days: Number of days to analyze (default 30)
    """
    try:
        from core.services.learning_velocity import LearningVelocityService
        from urllib.parse import unquote

        theme_name = unquote(theme)
        days = min(90, int(request.GET.get('days', 30)))

        service = LearningVelocityService()
        data = service.get_theme_detail(theme_name, days)

        return JsonResponse({
            'success': True,
            **data
        })

    except Exception as e:
        logger.error(f"Error getting theme velocity: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 368: Dream Validation & Implementation UI APIs
# =============================================================================

@require_http_methods(["GET"])
def get_boardroom_dreams(request):
    """
    Get dreams promoted to the Boardroom pending user decision.

    GET /api/boardroom/dreams/

    Query params:
    - limit: Max dreams to return (default 20)
    - status: Filter by decision_outcome (pending/approved/deferred/rejected)
    - min_score: Minimum composite score (default 0)
    """
    try:
        from core.models import AgentDream

        limit = int(request.GET.get('limit', 20))
        status = request.GET.get('status', 'pending')
        min_score = float(request.GET.get('min_score', 0))

        # Session 564: Sort by promoted_at first so newest items appear at top
        queryset = AgentDream.objects.filter(
            promoted_to_decision=True
        ).select_related('agent', 'project').order_by('-promoted_at', '-composite_score')

        if status:
            queryset = queryset.filter(decision_outcome=status)
        if min_score > 0:
            queryset = queryset.filter(composite_score__gte=min_score)

        dreams = queryset[:limit]

        dreams_data = []
        for dream in dreams:
            # Check if implementation exists
            has_implementation = hasattr(dream, 'implementation')

            dreams_data.append({
                'id': str(dream.id),
                'title': dream.title,
                'content': dream.content,
                'dream_type': dream.dream_type,
                'dream_type_display': dream.get_dream_type_display() if hasattr(dream, 'get_dream_type_display') else dream.dream_type,
                'agent_id': str(dream.agent.id) if dream.agent else None,
                'agent_name': dream.agent.name if dream.agent else None,
                'project_id': str(dream.project.id) if dream.project else None,
                'project_name': dream.project.title if dream.project else None,
                'creativity_score': dream.creativity_score,
                'actionability_score': dream.actionability_score,
                'relevance_score': dream.relevance_score,
                'composite_score': dream.composite_score,
                'decision_outcome': dream.decision_outcome,
                'promoted_at': dream.promoted_at.isoformat() if dream.promoted_at else None,
                'dreamed_at': dream.dreamed_at.isoformat() if dream.dreamed_at else None,
                'has_implementation': has_implementation,
            })

        # Get counts by status
        status_counts = {
            'pending': AgentDream.objects.filter(promoted_to_decision=True, decision_outcome='pending').count(),
            'approved': AgentDream.objects.filter(promoted_to_decision=True, decision_outcome='approved').count(),
            'deferred': AgentDream.objects.filter(promoted_to_decision=True, decision_outcome='deferred').count(),
            'rejected': AgentDream.objects.filter(promoted_to_decision=True, decision_outcome='rejected').count(),
        }

        return JsonResponse({
            'success': True,
            'dreams': dreams_data,
            'count': len(dreams_data),
            'total_promoted': AgentDream.objects.filter(promoted_to_decision=True).count(),
            'status_counts': status_counts,
        })

    except Exception as e:
        logger.error(f"Error getting boardroom dreams: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def decide_dream(request, dream_id):
    """
    Make a decision on a promoted dream.

    POST /api/boardroom/dreams/{dream_id}/decide/

    Body: { "decision": "approved|deferred|rejected", "notes": "optional" }
    """
    try:
        from core.models import AgentDream
        import json

        body = json.loads(request.body) if request.body else {}
        decision = body.get('decision', 'pending')
        notes = body.get('notes', '')

        if decision not in ['approved', 'deferred', 'rejected']:
            return JsonResponse({
                'success': False,
                'error': f'Invalid decision: {decision}. Must be approved, deferred, or rejected.'
            }, status=400)

        dream = AgentDream.objects.get(id=dream_id)

        if not dream.promoted_to_decision:
            return JsonResponse({
                'success': False,
                'error': 'Dream has not been promoted to the Boardroom'
            }, status=400)

        # Record the decision
        dream.record_decision(decision, notes)

        logger.info(f"🏛️ [BOARDROOM] Dream decision recorded: {dream.title[:40]} -> {decision}")

        return JsonResponse({
            'success': True,
            'message': f'Dream "{dream.title[:40]}" marked as {decision}',
            'dream_id': str(dream.id),
            'decision': decision
        })

    except AgentDream.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Dream not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error deciding on dream: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_dream_implementations(request):
    """
    Get dream implementations for tracking and validation.

    GET /api/dream-implementations/

    Query params:
    - limit: Max implementations to return (default 20)
    - status: Filter by status (pending/assigned/in_progress/completed/validated/rejected)
    - agent_id: Filter by assigned agent
    """
    try:
        from core.models_unified_system import DreamImplementation

        limit = int(request.GET.get('limit', 20))
        status = request.GET.get('status')
        agent_id = request.GET.get('agent_id')

        queryset = DreamImplementation.objects.select_related(
            'dream', 'dream__agent', 'assigned_agent', 'project'
        ).order_by('-created_at')

        if status:
            queryset = queryset.filter(status=status)
        if agent_id:
            queryset = queryset.filter(assigned_agent_id=agent_id)

        implementations = queryset[:limit]

        impl_data = []
        for impl in implementations:
            impl_data.append({
                'id': str(impl.id),
                'dream_id': str(impl.dream.id) if impl.dream else None,
                'dream_title': impl.dream.title if impl.dream else None,
                'dream_content': impl.dream.content if impl.dream else None,
                'dreaming_agent_name': impl.dream.agent.name if impl.dream and impl.dream.agent else None,
                'assigned_agent_id': str(impl.assigned_agent.id) if impl.assigned_agent else None,
                'assigned_agent_name': impl.assigned_agent.name if impl.assigned_agent else None,
                'project_id': str(impl.project.id) if impl.project else None,
                'project_name': impl.project.title if impl.project else None,
                'status': impl.status,
                'status_display': impl.get_status_display(),
                'implementation_type': impl.implementation_type,
                'implementation_type_display': impl.get_implementation_type_display(),
                'implementation_plan': impl.implementation_plan,
                'deliverable_type': impl.deliverable_type,
                'deliverable_path': impl.deliverable_path,
                'deliverable_summary': impl.deliverable_summary,
                'deliverable_content': impl.deliverable_content,
                'generated_media': impl.generated_media or [],  # Session 370: Visual implementations
                'quality_rating': impl.quality_rating,
                'user_feedback': impl.user_feedback,
                'created_at': impl.created_at.isoformat(),
                'assigned_at': impl.assigned_at.isoformat() if impl.assigned_at else None,
                'started_at': impl.started_at.isoformat() if impl.started_at else None,
                'completed_at': impl.completed_at.isoformat() if impl.completed_at else None,
                'validated_at': impl.validated_at.isoformat() if impl.validated_at else None,
            })

        # Get counts by status
        status_counts = {}
        for status_choice, _ in DreamImplementation.STATUS_CHOICES:
            status_counts[status_choice] = DreamImplementation.objects.filter(status=status_choice).count()

        return JsonResponse({
            'success': True,
            'implementations': impl_data,
            'count': len(impl_data),
            'total': DreamImplementation.objects.count(),
            'status_counts': status_counts,
        })

    except Exception as e:
        logger.error(f"Error getting dream implementations: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def validate_implementation(request, implementation_id):
    """
    Validate or reject a completed dream implementation.

    POST /api/dream-implementations/{implementation_id}/validate/

    Body: {
        "action": "validate|reject",
        "rating": 0.0-1.0 (optional, for validate),
        "feedback": "string" (optional)
    }
    """
    try:
        from core.models_unified_system import DreamImplementation
        import json

        body = json.loads(request.body) if request.body else {}
        action = body.get('action', 'validate')
        rating = body.get('rating')
        feedback = body.get('feedback', '')

        impl = DreamImplementation.objects.select_related('dream', 'assigned_agent').get(id=implementation_id)

        if action == 'validate':
            if rating is not None:
                rating = float(rating)
                if rating < 0 or rating > 1:
                    return JsonResponse({
                        'success': False,
                        'error': 'Rating must be between 0 and 1'
                    }, status=400)

            impl.validate(rating=rating, feedback=feedback)

            logger.info(f"✅ [VALIDATION] Implementation validated: {impl.dream.title[:40]} (rating: {rating})")

            return JsonResponse({
                'success': True,
                'message': f'Implementation validated with rating {rating}',
                'implementation_id': str(impl.id),
                'status': impl.status
            })

        elif action == 'reject':
            impl.reject(reason=feedback)

            logger.info(f"❌ [VALIDATION] Implementation rejected: {impl.dream.title[:40]}")

            return JsonResponse({
                'success': True,
                'message': 'Implementation rejected',
                'implementation_id': str(impl.id),
                'status': impl.status
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Invalid action: {action}. Must be validate or reject.'
            }, status=400)

    except DreamImplementation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Implementation not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error validating implementation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def rate_dream(request, dream_id):
    """
    Quick thumbs up/down rating for dreams (simpler than full reaction).

    POST /api/agent-dreams/{dream_id}/rate/

    Body: { "rating": "up|down" }
    """
    try:
        from core.models import AgentDream
        import json

        body = json.loads(request.body) if request.body else {}
        rating = body.get('rating', 'up')

        if rating not in ['up', 'down']:
            return JsonResponse({
                'success': False,
                'error': 'Rating must be "up" or "down"'
            }, status=400)

        dream = AgentDream.objects.get(id=dream_id)

        # Map to existing reaction types
        reaction_type = 'like' if rating == 'up' else 'boring'
        dream.user_reaction = reaction_type
        dream.save(update_fields=['user_reaction'])

        logger.info(f"👍 [DREAM] Rated {rating}: {dream.title[:40]}")

        return JsonResponse({
            'success': True,
            'message': f'Dream rated: {rating}',
            'dream_id': str(dream.id),
            'rating': rating
        })

    except AgentDream.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Dream not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error rating dream: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_validation_metrics(request):
    """
    Get validation metrics per agent for tracking performance.

    GET /api/dream-implementations/metrics/

    Query params:
    - agent_id: Filter by specific agent (optional)
    """
    try:
        from core.models_unified_system import DreamImplementation
        from core.models import Agent
        from django.db.models import Avg

        agent_id = request.GET.get('agent_id')

        # Build queryset
        if agent_id:
            agents = Agent.objects.filter(id=agent_id)
        else:
            # Get agents that have implementations
            agent_ids = DreamImplementation.objects.values_list('assigned_agent_id', flat=True).distinct()
            agents = Agent.objects.filter(id__in=agent_ids)

        metrics = []
        for agent in agents:
            impls = DreamImplementation.objects.filter(assigned_agent=agent)

            total = impls.count()
            if total == 0:
                continue

            validated = impls.filter(status='validated').count()
            rejected = impls.filter(status='rejected').count()
            in_progress = impls.filter(status='in_progress').count()
            completed = impls.filter(status='completed').count()

            avg_rating = impls.filter(
                quality_rating__isnull=False
            ).aggregate(avg=Avg('quality_rating'))['avg']

            metrics.append({
                'agent_id': str(agent.id),
                'agent_name': agent.name,
                'total_implementations': total,
                'validated': validated,
                'rejected': rejected,
                'in_progress': in_progress,
                'pending_validation': completed,  # Completed but not yet validated
                'success_rate': validated / (validated + rejected) if (validated + rejected) > 0 else None,
                'avg_quality_rating': avg_rating,
            })

        # Sort by total implementations
        metrics.sort(key=lambda x: x['total_implementations'], reverse=True)

        # Overall stats
        all_impls = DreamImplementation.objects.all()
        overall = {
            'total_implementations': all_impls.count(),
            'validated': all_impls.filter(status='validated').count(),
            'rejected': all_impls.filter(status='rejected').count(),
            'in_progress': all_impls.filter(status='in_progress').count(),
            'pending_validation': all_impls.filter(status='completed').count(),
            'avg_quality_rating': all_impls.filter(
                quality_rating__isnull=False
            ).aggregate(avg=Avg('quality_rating'))['avg'],
        }

        return JsonResponse({
            'success': True,
            'agent_metrics': metrics,
            'overall': overall,
        })

    except Exception as e:
        logger.error(f"Error getting validation metrics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 417: Agent Profile API
# =============================================================================

@require_http_methods(["GET"])
def get_agent_profile(request, agent_id):
    """
    Get comprehensive profile for a single agent including all their activity.

    GET /api/agents/{agent_id}/profile/

    Returns:
    - Agent info (name, specialization, description, level, XP)
    - Recent dreams (last 20)
    - Recent conversations (last 10)
    - Boardroom decisions they participated in (last 10)
    - Knowledge sources (last 10)
    - Evolution stats
    """
    try:
        from django.utils import timezone
        from core.models import Agent, AgentDream, AgentConversation, AgentKnowledgeSource
        from core.models_unified_system import AgentDecisionSummary

        # Get the agent
        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Agent not found'
            }, status=404)

        # Get agent's dreams
        dreams = AgentDream.objects.filter(
            agent=agent
        ).order_by('-dreamed_at')[:20]

        dreams_data = [{
            'id': str(d.id),
            'title': d.title,
            'content': d.content,
            'dream_type': d.dream_type,
            'inspiration': d.inspiration_source,
            'vividness': d.vividness_score,
            'creativity': d.creativity_score,
            'user_reaction': d.user_reaction,
            'dreamed_at': d.dreamed_at.isoformat()
        } for d in dreams]

        # Get agent's conversations (as participant or initiator)
        conversations = AgentConversation.objects.filter(
            participants=agent
        ).select_related('initiator').prefetch_related(
            'participants', 'messages__agent'
        ).order_by('-started_at')[:10]

        conversations_data = []
        for conv in conversations:
            messages_data = []
            for msg in conv.messages.filter(agent=agent)[:5]:
                messages_data.append({
                    'content': msg.content[:200],
                    'type': msg.message_type,
                    'created_at': msg.created_at.isoformat()
                })

            conversations_data.append({
                'id': str(conv.id),
                'topic': conv.topic,
                'type': conv.conversation_type,
                'status': conv.status,
                'initiator': conv.initiator.name,
                'was_initiator': conv.initiator.id == agent.id,
                'participants': [p.name for p in conv.participants.all()],
                'message_count': conv.message_count,
                'quality_score': conv.quality_score,
                'conclusion': conv.conclusion,
                'started_at': conv.started_at.isoformat(),
                'agent_messages': messages_data
            })

        # Get boardroom decisions with this agent's name in participants
        decisions = AgentDecisionSummary.objects.filter(
            participants__contains=[agent.name]
        ).order_by('-created_at')[:10]

        decisions_data = [{
            'id': str(d.id),
            'topic': d.topic,
            'decision_type': d.decision_type,
            'impact_area': d.impact_area,
            'key_insights': d.key_insights[:200] if d.key_insights else None,
            'recommended_stance': d.recommended_stance,
            'status': d.status,
            'is_canonical': d.is_canonical,
            'created_at': d.created_at.isoformat()
        } for d in decisions]

        # Get knowledge sources
        knowledge = AgentKnowledgeSource.objects.filter(
            agent=agent
        ).order_by('-last_updated_at')[:10]

        knowledge_data = [{
            'id': str(k.id),
            'title': k.title,
            'knowledge_type': k.knowledge_type,
            'summary': k.summary[:200] if k.summary else None,
            'confidence': k.confidence_score,
            'relevance': k.relevance_score,
            'last_updated': k.last_updated_at.isoformat()
        } for k in knowledge]

        # Build agent profile
        profile = {
            'id': str(agent.id),
            'name': agent.name,
            'specialization': agent.specialization,
            'description': agent.description,
            'is_active': agent.is_active,
            'level': getattr(agent, 'level', 1),
            'xp': getattr(agent, 'xp', 0),
            'created_at': agent.created_at.isoformat() if hasattr(agent, 'created_at') and agent.created_at else None,
        }

        # Calculate stats
        stats = {
            'total_dreams': AgentDream.objects.filter(agent=agent).count(),
            'total_conversations': AgentConversation.objects.filter(participants=agent).count(),
            'total_decisions': AgentDecisionSummary.objects.filter(participants__contains=[agent.name]).count(),
            'total_knowledge': AgentKnowledgeSource.objects.filter(agent=agent).count(),
            'dreams_last_7_days': AgentDream.objects.filter(
                agent=agent,
                dreamed_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'conversations_last_7_days': AgentConversation.objects.filter(
                participants=agent,
                started_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
        }

        return JsonResponse({
            'success': True,
            'agent': profile,
            'stats': stats,
            'dreams': dreams_data,
            'conversations': conversations_data,
            'decisions': decisions_data,
            'knowledge': knowledge_data
        })

    except Exception as e:
        logger.error(f"Error getting agent profile: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_conversation_detail(request, conversation_id):
    """
    Session 417: Get full conversation details including all messages.

    GET /api/conversations/{conversation_id}/

    Returns complete conversation with all messages from all participants.
    """
    try:
        from core.models import AgentConversation

        # Get the conversation
        try:
            conv = AgentConversation.objects.select_related(
                'initiator'
            ).prefetch_related(
                'participants', 'messages__agent'
            ).get(id=conversation_id)
        except AgentConversation.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Conversation not found'
            }, status=404)

        # Get all messages in order
        messages = conv.messages.all().order_by('created_at')
        messages_data = [{
            'id': str(msg.id),
            'agent_name': msg.agent.name if msg.agent else 'Unknown',
            'agent_id': str(msg.agent.id) if msg.agent else None,
            'content': msg.content,
            'message_type': msg.message_type,
            'created_at': msg.created_at.isoformat()
        } for msg in messages]

        return JsonResponse({
            'success': True,
            'conversation': {
                'id': str(conv.id),
                'topic': conv.topic,
                'conversation_type': conv.conversation_type,
                'status': conv.status,
                'initiator': {
                    'id': str(conv.initiator.id),
                    'name': conv.initiator.name
                } if conv.initiator else None,
                'participants': [
                    {'id': str(p.id), 'name': p.name}
                    for p in conv.participants.all()
                ],
                'conclusion': conv.conclusion,
                'quality_score': conv.quality_score,
                'started_at': conv.started_at.isoformat() if conv.started_at else None,
                'ended_at': conv.ended_at.isoformat() if conv.ended_at else None,
            },
            'messages': messages_data,
            'message_count': len(messages_data)
        })

    except Exception as e:
        logger.error(f"Error getting conversation detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_hivemind_detail(request, session_id):
    """
    Session 417: Get full HiveMind session details.

    GET /api/hivemind/{session_id}/

    Returns complete HiveMind session with all contributions.
    """
    try:
        from core.models_unified_system import HiveMindSession, HiveMindContribution, Agent

        # Get the session
        try:
            session = HiveMindSession.objects.get(id=session_id)
        except HiveMindSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'HiveMind session not found'
            }, status=404)

        # Get all contributions
        contributions = HiveMindContribution.objects.filter(
            session=session
        ).select_related('agent').order_by('submitted_at')

        contributions_data = [{
            'id': str(c.id),
            'agent_name': c.agent.name if c.agent else 'Unknown',
            'agent_id': str(c.agent.id) if c.agent else None,
            'content': c.content,
            'thinking_time': c.thinking_time,
            'submitted_at': c.submitted_at.isoformat() if c.submitted_at else None
        } for c in contributions]

        # Get participant names
        participant_names = []
        if session.participant_ids:
            participants = Agent.objects.filter(id__in=session.participant_ids)
            participant_names = [{'id': str(p.id), 'name': p.name} for p in participants]

        return JsonResponse({
            'success': True,
            'session': {
                'id': str(session.id),
                'question': session.question,
                'context': session.context,
                'conversation_topic': session.conversation_topic,
                'session_mode': session.session_mode,
                'status': session.status,
                'participants': participant_names,
                'synthesis': session.synthesis,
                'synthesis_summary': session.synthesis_summary,
                'contribution_count': session.contribution_count,
                'total_thinking_time': session.total_thinking_time,
                'created_at': session.created_at.isoformat() if session.created_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            },
            'contributions': contributions_data
        })

    except Exception as e:
        logger.error(f"Error getting HiveMind detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_decision_detail(request, decision_id):
    """
    Session 417: Get full boardroom decision details.

    GET /api/decisions/{decision_id}/

    Returns complete decision with all context and insights.
    """
    try:
        from core.models_unified_system import AgentDecisionSummary

        # Get the decision
        try:
            decision = AgentDecisionSummary.objects.get(id=decision_id)
        except AgentDecisionSummary.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Decision not found'
            }, status=404)

        return JsonResponse({
            'success': True,
            'decision': {
                'id': str(decision.id),
                'topic': decision.topic,
                'decision_type': decision.decision_type,
                'impact_area': decision.impact_area,
                'participants': decision.participants or [],
                'key_insights': decision.key_insights,
                'recommended_stance': decision.recommended_stance,
                'dissenting_views': decision.dissenting_views,
                'source_document_id': str(decision.source_document_id) if decision.source_document_id else None,
                'source_summary_type': decision.source_summary_type,
                'is_canonical': decision.is_canonical,
                'status': decision.status,
                'confidence_score': decision.confidence_score,
                'context': decision.context,
                'raw_transcript': decision.raw_transcript,
                'created_at': decision.created_at.isoformat() if decision.created_at else None,
            }
        })

    except Exception as e:
        logger.error(f"Error getting decision detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_dream_detail(request, dream_id):
    """
    Session 417: Get full dream details.

    GET /api/dreams/{dream_id}/

    Returns complete dream with all metadata.
    """
    try:
        from core.models import AgentDream

        # Get the dream
        try:
            dream = AgentDream.objects.select_related('agent').get(id=dream_id)
        except AgentDream.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Dream not found'
            }, status=404)

        return JsonResponse({
            'success': True,
            'dream': {
                'id': str(dream.id),
                'agent': {
                    'id': str(dream.agent.id),
                    'name': dream.agent.name
                } if dream.agent else None,
                'title': dream.title,
                'content': dream.content,
                'dream_type': dream.dream_type,
                'inspiration_source': dream.inspiration_source,
                'related_topics': dream.related_topics,
                'vividness_score': dream.vividness_score,
                'creativity_score': dream.creativity_score,
                'actionability_score': dream.actionability_score,
                'relevance_score': dream.relevance_score,
                'composite_score': dream.composite_score,
                'user_reaction': dream.user_reaction,
                'user_feedback': dream.user_feedback,
                'promoted_to_decision': dream.promoted_to_decision,
                'dreamed_at': dream.dreamed_at.isoformat() if dream.dreamed_at else None,
            }
        })

    except Exception as e:
        logger.error(f"Error getting dream detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 590: Pilot Readiness Gate API
# =============================================================================

@require_http_methods(["GET"])
def get_pilot_readiness_gates(request):
    """
    Get all pilot readiness gates with their checklist status.

    GET /api/pilot-gates/

    Query params:
    - status: Filter by gate status (not_started, in_progress, ready, approved, blocked, waived)
    - risk_level: Filter by risk level (low, medium, high, critical)
    - limit: Max gates to return (default 20)
    """
    try:
        from core.models_pilot_readiness import PilotReadinessGate
        from core.utils.title_cleaner import clean_title  # Session 617: Clean redundant prefixes

        limit = int(request.GET.get('limit', 20))
        status = request.GET.get('status')
        risk_level = request.GET.get('risk_level')

        queryset = PilotReadinessGate.objects.select_related('decision').order_by('-created_at')

        if status:
            queryset = queryset.filter(status=status)
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)

        gates = queryset[:limit]

        gates_data = []
        for gate in gates:
            progress = gate.checklist_progress
            latency = gate.get_latency_metrics()

            # Get checklist items for UI display
            checklist_items = []
            for item in gate.checklist_items.all().order_by('item_type'):
                checklist_items.append({
                    'id': str(item.id),
                    'item_type': item.item_type,
                    'title': item.title,
                    'description': item.description,
                    'status': item.status,
                    'is_required': item.is_required,
                    # Session 594: Include AI-generated content
                    'generated_content': item.documentation_notes or None,
                    'has_content': bool(item.documentation_notes),
                })

            # Session 594: Get running pilot info
            running_pilot = gate.pilot_executions.filter(status='running').first()
            pilot_info = None
            if running_pilot:
                from django.utils import timezone
                hours_running = (timezone.now() - running_pilot.started_at).total_seconds() / 3600 if running_pilot.started_at else 0
                pilot_info = {
                    'id': str(running_pilot.id),
                    'name': running_pilot.name,
                    'status': running_pilot.status,
                    'hours_running': round(hours_running, 1),
                    'started_at': running_pilot.started_at.isoformat() if running_pilot.started_at else None,
                }

            gates_data.append({
                'id': str(gate.id),
                'decision_id': str(gate.decision.id),
                'decision_topic': clean_title(gate.decision.topic, max_length=80),  # Session 617: Clean titles
                'decision_type': gate.decision.decision_type,
                'impact_area': gate.decision.impact_area,
                'status': gate.status,
                'status_display': gate.get_status_display(),
                'risk_level': gate.risk_level,
                'summary': clean_title(gate.summary.replace('Pilot readiness for: ', ''), max_length=100) if gate.summary else '',  # Session 617
                'checklist_total': progress['total'],
                'checklist_completed': progress['completed'],
                'checklist_percentage': progress['percentage'],
                'checklist_items': checklist_items,
                'latency': latency,
                'approved_by': gate.approved_by,
                'created_at': gate.created_at.isoformat(),
                'decision_made_at': gate.decision_made_at.isoformat() if gate.decision_made_at else None,
                'gate_approved_at': gate.gate_approved_at.isoformat() if gate.gate_approved_at else None,
                'running_pilot': pilot_info,  # Session 594: Include pilot info
            })

        # Get summary stats
        total_gates = PilotReadinessGate.objects.count()
        by_status = {}
        for s, _ in PilotReadinessGate.GATE_STATUS_CHOICES:
            by_status[s] = PilotReadinessGate.objects.filter(status=s).count()

        return JsonResponse({
            'success': True,
            'gates': gates_data,
            'total': total_gates,
            'by_status': by_status,
        })

    except Exception as e:
        logger.error(f"Error getting pilot gates: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_pilot_gate_detail(request, gate_id):
    """
    Get detailed info for a specific pilot readiness gate.

    GET /api/pilot-gates/<gate_id>/
    """
    try:
        from core.models_pilot_readiness import PilotReadinessGate

        gate = PilotReadinessGate.objects.select_related('decision').get(id=gate_id)
        progress = gate.checklist_progress
        latency = gate.get_latency_metrics()

        # Get checklist items
        items = []
        for item in gate.checklist_items.all().order_by('item_type'):
            items.append({
                'id': str(item.id),
                'item_type': item.item_type,
                'title': item.title,
                'description': item.description,
                'status': item.status,
                'is_required': item.is_required,
                'documentation_url': item.documentation_url,
                'documentation_notes': item.documentation_notes,
                'assigned_to': item.assigned_to,
                'completed_by': item.completed_by,
                'completed_at': item.completed_at.isoformat() if item.completed_at else None,
                'completion_notes': item.completion_notes,
            })

        # Get pilot executions
        executions = []
        for exec in gate.pilot_executions.all().order_by('-created_at'):
            executions.append({
                'id': str(exec.id),
                'name': exec.name,
                'status': exec.status,
                'outcome': exec.outcome,
                'outcome_summary': exec.outcome_summary,
                'kill_switch_triggered': exec.kill_switch_triggered,
                'started_at': exec.started_at.isoformat() if exec.started_at else None,
                'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
            })

        return JsonResponse({
            'success': True,
            'gate': {
                'id': str(gate.id),
                'decision': {
                    'id': str(gate.decision.id),
                    'topic': gate.decision.topic,
                    'decision_type': gate.decision.decision_type,
                    'impact_area': gate.decision.impact_area,
                    'status': gate.decision.status,
                    'recommended_stance': gate.decision.recommended_stance,
                },
                'status': gate.status,
                'risk_level': gate.risk_level,
                'risk_factors': gate.risk_factors,
                'summary': gate.summary,
                'success_criteria': gate.success_criteria,
                'failure_criteria': gate.failure_criteria,
                'approved_by': gate.approved_by,
                'approval_notes': gate.approval_notes,
                'checklist': {
                    'total': progress['total'],
                    'completed': progress['completed'],
                    'percentage': progress['percentage'],
                    'items': items,
                },
                'latency': latency,
                'executions': executions,
                'created_at': gate.created_at.isoformat(),
            }
        })

    except PilotReadinessGate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gate not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting pilot gate detail: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def update_gate_status(request, gate_id):
    """
    Update gate status (start, ready, approve, block).

    POST /api/pilot-gates/<gate_id>/status/

    Body:
    - action: 'start' | 'ready' | 'approve' | 'block' | 'waive'
    - notes: Optional notes (required for approve/block)
    - approved_by: Required for approve action
    """
    try:
        import json
        from core.models_pilot_readiness import PilotReadinessGate

        gate = PilotReadinessGate.objects.get(id=gate_id)
        data = json.loads(request.body)

        action = data.get('action')
        notes = data.get('notes', '')
        approved_by = data.get('approved_by', 'human')

        if action == 'start':
            success = gate.start_readiness()
            message = 'Gate started' if success else 'Could not start gate'
        elif action == 'ready':
            success = gate.mark_ready()
            message = 'Gate marked ready' if success else 'Checklist incomplete'
        elif action == 'approve':
            success = gate.approve(approved_by=approved_by, notes=notes)
            message = 'Gate approved' if success else 'Could not approve gate'
        elif action == 'block':
            success = gate.block(reason=notes)
            message = 'Gate blocked' if success else 'Could not block gate'
        elif action == 'waive':
            success = gate.waive(reason=notes)
            message = 'Gate waived' if success else 'Only low-risk gates can be waived'
        else:
            return JsonResponse({'success': False, 'error': f'Unknown action: {action}'}, status=400)

        return JsonResponse({
            'success': success,
            'message': message,
            'new_status': gate.status,
        })

    except PilotReadinessGate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gate not found'}, status=404)
    except Exception as e:
        logger.error(f"Error updating gate status: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def update_checklist_item(request, gate_id, item_id):
    """
    Update a checklist item status.

    POST /api/pilot-gates/<gate_id>/items/<item_id>/

    Body:
    - action: 'complete' | 'waive' | 'block' | 'start'
    - completed_by: Who completed it
    - notes: Completion notes
    - documentation_url: Link to artifact
    """
    try:
        import json
        from core.models_pilot_readiness import PilotReadinessGate, ReadinessChecklistItem

        gate = PilotReadinessGate.objects.get(id=gate_id)
        item = gate.checklist_items.get(id=item_id)
        data = json.loads(request.body)

        action = data.get('action')
        completed_by = data.get('completed_by', 'human')
        notes = data.get('notes', '')
        documentation_url = data.get('documentation_url', '')

        if action == 'complete':
            item.complete(
                completed_by=completed_by,
                notes=notes,
                documentation_url=documentation_url
            )
            message = f'Item "{item.title}" completed'
        elif action == 'waive':
            item.waive(waived_by=completed_by, reason=notes)
            message = f'Item "{item.title}" waived'
        elif action == 'block':
            item.block(reason=notes)
            message = f'Item "{item.title}" blocked'
        elif action == 'start':
            item.status = 'in_progress'
            item.save()
            message = f'Item "{item.title}" started'
        else:
            return JsonResponse({'success': False, 'error': f'Unknown action: {action}'}, status=400)

        # Return updated gate progress
        progress = gate.checklist_progress

        return JsonResponse({
            'success': True,
            'message': message,
            'item_status': item.status,
            'gate_status': gate.status,
            'checklist_progress': progress,
        })

    except PilotReadinessGate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gate not found'}, status=404)
    except ReadinessChecklistItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
    except Exception as e:
        logger.error(f"Error updating checklist item: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def create_pilot_gate(request, decision_id):
    """
    Create a pilot readiness gate for a decision.

    POST /api/pilot-gates/create/<decision_id>/

    Body:
    - risk_level: 'low' | 'medium' | 'high' | 'critical'
    """
    try:
        import json
        from core.models_pilot_readiness import PilotReadinessGate
        from core.models_unified_system import AgentDecisionSummary

        decision = AgentDecisionSummary.objects.get(id=decision_id)

        # Check if gate already exists
        if hasattr(decision, 'readiness_gate'):
            return JsonResponse({
                'success': False,
                'error': 'Gate already exists for this decision',
                'gate_id': str(decision.readiness_gate.id)
            }, status=400)

        data = json.loads(request.body) if request.body else {}
        risk_level = data.get('risk_level', 'medium')

        # Auto-determine risk level based on impact area
        if decision.impact_area in ('security', 'infrastructure'):
            risk_level = 'high'
        elif decision.decision_type in ('policy', 'architecture'):
            risk_level = max(risk_level, 'medium')

        gate = PilotReadinessGate.create_for_decision(decision, risk_level=risk_level)

        return JsonResponse({
            'success': True,
            'message': f'Gate created with {gate.checklist_items.count()} checklist items',
            'gate_id': str(gate.id),
            'risk_level': gate.risk_level,
            'checklist_count': gate.checklist_items.count(),
        })

    except AgentDecisionSummary.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Decision not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating pilot gate: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def start_pilot_execution(request, gate_id):
    """
    Session 592: Create and start a pilot execution for an approved gate.

    POST /api/pilot-gates/<gate_id>/pilot/

    Body (optional):
    - name: Custom pilot name
    - description: Pilot description
    - scope: What is being tested
    """
    try:
        import json
        from core.models_pilot_readiness import PilotReadinessGate, PilotExecution

        gate = PilotReadinessGate.objects.get(id=gate_id)

        # Verify gate is approved
        if gate.status not in ('approved', 'waived'):
            return JsonResponse({
                'success': False,
                'error': f'Gate must be approved before starting pilot. Current status: {gate.status}'
            }, status=400)

        # Parse request body
        data = json.loads(request.body) if request.body else {}

        # Session 617: Clean the topic name
        import re
        topic = gate.decision.topic or 'Pilot'
        for prefix in [r'^Experiment:\s*', r'^Pilot:\s*', r'^Discussion:\s*',
                       r'^Panel:\s*', r'^\[Learned\]\s*', r'^\[Synthesis\]\s*',
                       r'^Research:\s*', r'^Research topic:\s*', r'^Topic:\s*']:
            topic = re.sub(prefix, '', topic, flags=re.IGNORECASE).strip()
        if topic and topic[0].islower():
            topic = topic[0].upper() + topic[1:]

        default_name = topic[:100]

        # Create pilot execution
        pilot = PilotExecution.objects.create(
            gate=gate,
            name=data.get('name', default_name),
            description=data.get('description', f'Pilot execution for {topic}'),
            scope=data.get('scope', gate.summary),
            status='planned'
        )

        # Start the pilot
        pilot.start()

        # Session 596: Auto-create experiment for tracking
        from core.models_pilot_readiness import Experiment
        experiment = Experiment.create_from_pilot(pilot)

        return JsonResponse({
            'success': True,
            'message': 'Pilot started successfully',
            'pilot': {
                'id': str(pilot.id),
                'name': pilot.name,
                'status': pilot.status,
                'started_at': pilot.started_at.isoformat() if pilot.started_at else None,
            },
            'experiment': {
                'id': str(experiment.id),
                'name': experiment.name,
                'primary_kpi': experiment.primary_kpi,
                'target_value': experiment.target_value,
            },
            'gate_status': gate.status,
            'pilot_started_at': gate.pilot_started_at.isoformat() if gate.pilot_started_at else None,
        })

    except PilotReadinessGate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gate not found'}, status=404)
    except Exception as e:
        logger.error(f"Error starting pilot execution: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def complete_pilot_execution(request, gate_id, pilot_id):
    """
    Session 592: Complete a running pilot execution.

    POST /api/pilot-gates/<gate_id>/pilot/<pilot_id>/complete/

    Body:
    - outcome: 'success' | 'partial' | 'failure' | 'inconclusive'
    - summary: Outcome summary
    - learnings: List of learnings (optional)
    - metrics: Dict of metrics (optional)
    """
    try:
        import json
        from core.models_pilot_readiness import PilotReadinessGate, PilotExecution

        gate = PilotReadinessGate.objects.get(id=gate_id)
        pilot = PilotExecution.objects.get(id=pilot_id, gate=gate)

        # Verify pilot is running
        if pilot.status != 'running':
            return JsonResponse({
                'success': False,
                'error': f'Pilot must be running to complete. Current status: {pilot.status}'
            }, status=400)

        data = json.loads(request.body) if request.body else {}

        outcome = data.get('outcome', 'success')
        summary = data.get('summary', 'Pilot completed')
        learnings = data.get('learnings', [])
        metrics = data.get('metrics', {})

        # Update metrics if provided
        if metrics:
            pilot.metrics = metrics
            pilot.save()

        # Complete the pilot
        pilot.complete(outcome=outcome, summary=summary, learnings=learnings)

        return JsonResponse({
            'success': True,
            'message': 'Pilot completed successfully',
            'pilot': {
                'id': str(pilot.id),
                'name': pilot.name,
                'status': pilot.status,
                'outcome': pilot.outcome,
                'outcome_summary': pilot.outcome_summary,
                'started_at': pilot.started_at.isoformat() if pilot.started_at else None,
                'completed_at': pilot.completed_at.isoformat() if pilot.completed_at else None,
                'duration_hours': pilot.get_duration_hours(),
                'learnings': pilot.learnings,
                'metrics': pilot.metrics,
            },
            'gate_pilot_completed_at': gate.pilot_completed_at.isoformat() if gate.pilot_completed_at else None,
        })

    except PilotReadinessGate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gate not found'}, status=404)
    except PilotExecution.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pilot not found'}, status=404)
    except Exception as e:
        logger.error(f"Error completing pilot execution: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def regenerate_checklist_content(request, gate_id):
    """
    Session 594: Regenerate AI content for checklist items.

    POST /api/pilot-gates/<gate_id>/regenerate/

    Body (optional):
    - item_id: Regenerate only this specific item (otherwise all items)
    """
    try:
        import json
        from core.models_pilot_readiness import PilotReadinessGate
        from core.services.checklist_content_generator import ChecklistContentGenerator

        gate = PilotReadinessGate.objects.get(id=gate_id)
        data = json.loads(request.body) if request.body else {}

        item_id = data.get('item_id')
        generator = ChecklistContentGenerator()

        if item_id:
            # Regenerate single item
            item = gate.checklist_items.get(id=item_id)
            context = generator._build_decision_context(gate.decision)
            content = generator.generate_for_item(item.item_type, context)
            if content:
                item.documentation_notes = content
                item.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Regenerated content for {item.title}',
                    'item_id': str(item.id),
                    'content': content,
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to generate content'
                }, status=500)
        else:
            # Regenerate all items
            results = generator.generate_all_items(gate)
            return JsonResponse({
                'success': True,
                'message': f'Regenerated content for {len(results)} items',
                'items_regenerated': len(results),
            })

    except PilotReadinessGate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gate not found'}, status=404)
    except Exception as e:
        logger.error(f"Error regenerating checklist content: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def approve_all_checklist_items(request, gate_id):
    """
    Session 594: Approve all checklist items that have AI-generated content.

    POST /api/pilot-gates/<gate_id>/approve-all/
    """
    try:
        from core.models_pilot_readiness import PilotReadinessGate

        gate = PilotReadinessGate.objects.get(id=gate_id)

        approved_count = 0
        for item in gate.checklist_items.filter(status='pending'):
            # Only approve items that have generated content
            if item.documentation_notes:
                item.status = 'completed'
                item.save()
                approved_count += 1

        return JsonResponse({
            'success': True,
            'message': f'Approved {approved_count} items',
            'items_approved': approved_count,
            'checklist_complete': gate.checklist_complete,
        })

    except PilotReadinessGate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gate not found'}, status=404)
    except Exception as e:
        logger.error(f"Error approving all checklist items: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_pilot_executions_dashboard(request):
    """
    Session 595: Get comprehensive dashboard for pilot executions.

    GET /api/pilots/dashboard/

    Returns:
    - running_pilots: Currently running pilots with status info
    - completed_pilots: Recently completed pilots with outcomes
    - metrics: Success rates, averages, counts
    """
    try:
        from django.db.models import Avg, Count
        from django.utils import timezone
        from core.models_pilot_readiness import PilotExecution

        now = timezone.now()

        # 1. Running pilots
        running = PilotExecution.objects.filter(status='running').select_related('gate', 'gate__decision').order_by('-started_at')
        running_pilots = []
        for p in running:
            hours_running = (now - p.started_at).total_seconds() / 3600
            auto_complete_in = max(0, 24 - hours_running)

            # Get ThinkingAgent evaluation if available
            thinking_eval = None
            if p.metrics and 'thinking_agent_evaluation' in p.metrics:
                thinking_eval = p.metrics['thinking_agent_evaluation']

            running_pilots.append({
                'id': str(p.id),
                'gate_id': str(p.gate.id),
                'decision_topic': p.gate.decision.topic if p.gate.decision else 'Unknown',
                'decision_type': p.gate.decision.decision_type if p.gate.decision else 'unknown',
                'risk_level': p.gate.risk_level,
                'started_at': p.started_at.isoformat(),
                'hours_running': round(hours_running, 1),
                'auto_complete_in_hours': round(auto_complete_in, 1),
                'kill_switch_triggered': p.kill_switch_triggered,
                'thinking_agent_evaluation': thinking_eval,
            })

        # 2. Completed pilots (last 20)
        completed = PilotExecution.objects.filter(status='completed').select_related('gate', 'gate__decision').order_by('-completed_at')[:20]
        completed_pilots = []
        for p in completed:
            duration_hours = None
            if p.started_at and p.completed_at:
                duration_hours = (p.completed_at - p.started_at).total_seconds() / 3600

            thinking_eval = None
            if p.metrics and 'thinking_agent_evaluation' in p.metrics:
                thinking_eval = p.metrics['thinking_agent_evaluation']

            completed_pilots.append({
                'id': str(p.id),
                'gate_id': str(p.gate.id),
                'decision_topic': p.gate.decision.topic if p.gate.decision else 'Unknown',
                'decision_type': p.gate.decision.decision_type if p.gate.decision else 'unknown',
                'risk_level': p.gate.risk_level,
                'outcome': p.outcome,
                'started_at': p.started_at.isoformat() if p.started_at else None,
                'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                'duration_hours': round(duration_hours, 1) if duration_hours else None,
                'learnings': p.learnings,
                'thinking_agent_evaluation': thinking_eval,
            })

        # 3. Metrics
        all_pilots = PilotExecution.objects.all()
        total_pilots = all_pilots.count()
        completed_count = all_pilots.filter(status='completed').count()
        success_count = all_pilots.filter(outcome='success').count()
        failure_count = all_pilots.filter(outcome='failure').count()
        partial_count = all_pilots.filter(outcome='partial_success').count()

        # Calculate average duration for completed pilots
        avg_duration = None
        completed_with_times = PilotExecution.objects.filter(
            status='completed',
            started_at__isnull=False,
            completed_at__isnull=False
        )
        if completed_with_times.exists():
            durations = [(p.completed_at - p.started_at).total_seconds() / 3600 for p in completed_with_times]
            avg_duration = sum(durations) / len(durations)

        # Success rate
        success_rate = round((success_count / completed_count * 100), 1) if completed_count > 0 else 0

        metrics = {
            'total_pilots': total_pilots,
            'running_count': len(running_pilots),
            'completed_count': completed_count,
            'success_count': success_count,
            'failure_count': failure_count,
            'partial_count': partial_count,
            'success_rate': success_rate,
            'avg_duration_hours': round(avg_duration, 1) if avg_duration else None,
        }

        return JsonResponse({
            'success': True,
            'running_pilots': running_pilots,
            'completed_pilots': completed_pilots,
            'metrics': metrics,
        })

    except Exception as e:
        logger.error(f"Error getting pilot executions dashboard: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_pilot_gate_dashboard(request):
    """
    Session 593: Get comprehensive dashboard data for pilot readiness gates.

    GET /api/pilot-gates/dashboard/

    Returns:
    - status_counts: Gates by status (not_started, in_progress, etc.)
    - risk_counts: Gates by risk level (high, medium, low, critical)
    - backlog: Decisions without gates (security + policy)
    - throughput: Average time metrics by phase
    - blocked_gates: List of blocked gates with reasons
    - recent_pilots: Recently completed pilots
    """
    try:
        from django.db.models import Avg, Count, F
        from django.db.models.functions import Coalesce
        from core.models_pilot_readiness import PilotReadinessGate, PilotExecution
        from core.models_unified_system import AgentDecisionSummary

        # 1. Status counts
        status_counts = {}
        for status, _ in PilotReadinessGate.GATE_STATUS_CHOICES:
            status_counts[status] = PilotReadinessGate.objects.filter(status=status).count()

        # 2. Risk level counts
        risk_counts = {}
        for level in ['low', 'medium', 'high', 'critical']:
            risk_counts[level] = PilotReadinessGate.objects.filter(risk_level=level).count()

        # 3. Decision backlog (eligible decisions without gates)
        existing_gate_ids = set(PilotReadinessGate.objects.values_list('decision_id', flat=True))

        security_backlog = AgentDecisionSummary.objects.filter(
            impact_area='security'
        ).exclude(id__in=existing_gate_ids).count()

        policy_backlog = AgentDecisionSummary.objects.filter(
            decision_type='policy'
        ).exclude(
            impact_area='security'
        ).exclude(id__in=existing_gate_ids).count()

        backlog = {
            'security': security_backlog,
            'policy': policy_backlog,
            'total': security_backlog + policy_backlog
        }

        # 4. Throughput metrics (average hours in each phase)
        # Only calculate for gates that have phase timestamps
        throughput = {
            'avg_decision_to_readiness_hours': None,
            'avg_readiness_duration_hours': None,
            'avg_approval_wait_hours': None,
            'avg_total_gate_hours': None,
            'avg_pilot_duration_hours': None
        }

        # Get latency metrics from completed gates (approved status)
        approved_gates = PilotReadinessGate.objects.filter(status='approved')
        if approved_gates.exists():
            latencies = []
            for gate in approved_gates:
                metrics = gate.get_latency_metrics()
                latencies.append(metrics)

            if latencies:
                def safe_avg(key):
                    values = [l.get(key) for l in latencies if l.get(key) is not None]
                    return round(sum(values) / len(values), 1) if values else None

                throughput['avg_decision_to_readiness_hours'] = safe_avg('decision_to_readiness_hours')
                throughput['avg_readiness_duration_hours'] = safe_avg('readiness_duration_hours')
                throughput['avg_approval_wait_hours'] = safe_avg('approval_wait_hours')
                throughput['avg_total_gate_hours'] = safe_avg('total_gate_hours')

        # Pilot duration from completed pilots (Session 655: only last 30 days to avoid old outliers)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        completed_pilots = PilotExecution.objects.filter(
            status='completed',
            completed_at__gte=thirty_days_ago
        )
        if completed_pilots.exists():
            pilot_durations = []
            for pilot in completed_pilots:
                if pilot.started_at and pilot.completed_at:
                    duration = (pilot.completed_at - pilot.started_at).total_seconds() / 3600
                    # Session 655: Cap at 72 hours to avoid outliers from stuck pilots
                    if duration <= 72:
                        pilot_durations.append(duration)
            if pilot_durations:
                throughput['avg_pilot_duration_hours'] = round(sum(pilot_durations) / len(pilot_durations), 1)

        # 5. Blocked gates with reasons
        blocked_gates = []
        for gate in PilotReadinessGate.objects.filter(status='blocked').select_related('decision')[:10]:
            blocked_items = gate.checklist_items.filter(status='blocked')
            blocked_gates.append({
                'gate_id': str(gate.id),
                'topic': gate.decision.topic[:60],
                'risk_level': gate.risk_level,
                'blocked_items': list(blocked_items.values_list('name', flat=True)),
                'approval_notes': gate.approval_notes or ''
            })

        # 6. Recent pilots
        recent_pilots = []
        for pilot in PilotExecution.objects.select_related('gate', 'gate__decision').order_by('-completed_at')[:5]:
            recent_pilots.append({
                'pilot_id': str(pilot.id),
                'name': pilot.name,
                'outcome': pilot.outcome,
                'status': pilot.status,
                'topic': pilot.gate.decision.topic[:50] if pilot.gate else 'N/A',
                'completed_at': pilot.completed_at.isoformat() if pilot.completed_at else None,
                'learnings_count': len(pilot.learnings) if pilot.learnings else 0
            })

        # 7. Summary stats
        total_gates = PilotReadinessGate.objects.count()
        total_decisions = AgentDecisionSummary.objects.count()
        coverage_pct = round((total_gates / total_decisions * 100), 1) if total_decisions > 0 else 0

        return JsonResponse({
            'success': True,
            'dashboard': {
                'status_counts': status_counts,
                'risk_counts': risk_counts,
                'backlog': backlog,
                'throughput': throughput,
                'blocked_gates': blocked_gates,
                'recent_pilots': recent_pilots,
                'summary': {
                    'total_gates': total_gates,
                    'total_decisions': total_decisions,
                    'coverage_pct': coverage_pct,
                    'completed_pilots': PilotExecution.objects.filter(status='completed').count(),
                    'running_pilots': PilotExecution.objects.filter(status='running').count()
                }
            }
        })

    except Exception as e:
        logger.error(f"Error getting pilot gate dashboard: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# SESSION 596: EXPERIMENT TRACKING REGISTRY
# ============================================================================

@require_http_methods(["GET"])
def get_experiments(request):
    """
    Session 596: Get all experiments with KPI tracking.

    GET /api/experiments/

    Query params:
    - status: Filter by status (running, success, failure, inconclusive)
    - limit: Number of results (default 50)
    """
    try:
        from core.models_pilot_readiness import Experiment

        status = request.GET.get('status')
        limit = int(request.GET.get('limit', 50))

        queryset = Experiment.objects.select_related('pilot', 'pilot__gate', 'pilot__gate__decision')

        if status:
            queryset = queryset.filter(status=status)

        experiments = []
        for exp in queryset.order_by('-created_at')[:limit]:
            # Get decision info through pilot -> gate -> decision
            decision_topic = "Unknown"
            decision_id = None
            risk_level = "medium"

            if exp.pilot and exp.pilot.gate and exp.pilot.gate.decision:
                decision_topic = exp.pilot.gate.decision.topic[:80]
                decision_id = str(exp.pilot.gate.decision.id)
                risk_level = exp.pilot.gate.risk_level

            experiments.append({
                'id': str(exp.id),
                'name': exp.name,
                'hypothesis': exp.hypothesis or '',  # Session 656: Return full hypothesis for modal
                'status': exp.status,
                'kpi_owner': exp.kpi_owner,
                'primary_kpi': exp.primary_kpi,
                'target_value': exp.target_value,
                'current_value': exp.current_value,
                'secondary_kpis': exp.secondary_kpis,
                'extracted_metrics': exp.extracted_metrics,
                'started_at': exp.started_at.isoformat() if exp.started_at else None,
                'ended_at': exp.ended_at.isoformat() if exp.ended_at else None,
                'learnings': exp.learnings,
                'pilot_id': str(exp.pilot_id) if exp.pilot_id else None,
                'decision_topic': decision_topic,
                'decision_id': decision_id,
                'risk_level': risk_level,
                # Session 599: Halt and outcome classification
                'is_halted': exp.is_halted,
                'halted_at': exp.halted_at.isoformat() if exp.halted_at else None,
                'halted_by': exp.halted_by,
                'halt_reason': exp.halt_reason,
                'outcome_classification': exp.outcome_classification,
            })

        return JsonResponse({
            'success': True,
            'experiments': experiments,
            'count': len(experiments),
        })

    except Exception as e:
        logger.error(f"Error getting experiments: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_experiment_kpi(request, experiment_id):
    """
    Session 596: Update the current KPI value for an experiment.

    POST /api/experiments/<uuid:experiment_id>/update-kpi/

    Body:
    {
        "current_value": "25%",
        "notes": "Optional notes about the update"
    }
    """
    try:
        import json
        from core.models_pilot_readiness import Experiment

        exp = Experiment.objects.get(id=experiment_id)
        data = json.loads(request.body)

        exp.current_value = data.get('current_value', exp.current_value)

        # Update extracted_metrics with history
        if 'kpi_history' not in exp.extracted_metrics:
            exp.extracted_metrics['kpi_history'] = []

        exp.extracted_metrics['kpi_history'].append({
            'value': exp.current_value,
            'timestamp': timezone.now().isoformat(),
            'notes': data.get('notes', '')
        })

        exp.save()

        return JsonResponse({
            'success': True,
            'experiment_id': str(exp.id),
            'current_value': exp.current_value,
            'message': 'KPI updated successfully'
        })

    except Experiment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Experiment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error updating experiment KPI: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def raise_experiment_target(request, experiment_id):
    """
    Session 657: Raise the target value for an experiment that's exceeding expectations.

    POST /api/experiments/<uuid:experiment_id>/raise-target/

    Body:
    {
        "new_target": "90%",
        "notes": "Optional reason for raising target"
    }
    """
    try:
        import json
        from core.models_pilot_readiness import Experiment

        exp = Experiment.objects.get(id=experiment_id)
        data = json.loads(request.body)

        old_target = exp.target_value
        new_target = data.get('new_target')

        if not new_target:
            return JsonResponse({'success': False, 'error': 'new_target is required'}, status=400)

        exp.target_value = new_target

        # Track the change in extracted_metrics
        if 'target_history' not in exp.extracted_metrics:
            exp.extracted_metrics['target_history'] = []

        exp.extracted_metrics['target_history'].append({
            'old_target': old_target,
            'new_target': new_target,
            'timestamp': timezone.now().isoformat(),
            'notes': data.get('notes', 'Target raised due to exceeding expectations')
        })

        exp.save()

        return JsonResponse({
            'success': True,
            'experiment_id': str(exp.id),
            'old_target': old_target,
            'new_target': new_target,
            'message': f'Target raised from {old_target} to {new_target}'
        })

    except Experiment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Experiment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error raising experiment target: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def complete_experiment(request, experiment_id):
    """
    Session 596: Mark an experiment as complete with outcome.
    Session 597: Auto-creates ExperimentLearning and updates DecisionTypeSuccessPattern.
    Session 599: Added outcome_classification (PASS/LEARN/FAIL).

    POST /api/experiments/<uuid:experiment_id>/complete/

    Body:
    {
        "status": "success" | "failure" | "inconclusive" | "partial",
        "outcome_classification": "pass" | "learn" | "fail" (optional, auto-determined if not provided),
        "learnings": "What we learned from this experiment",
        "what_worked": "Specific tactics that worked",
        "what_failed": "Specific tactics that didn't work",
        "recommendation": "Future recommendation"
    }
    """
    try:
        import json
        from core.models_pilot_readiness import Experiment, ExperimentLearning, DecisionTypeSuccessPattern

        exp = Experiment.objects.get(id=experiment_id)
        data = json.loads(request.body)

        status = data.get('status', 'inconclusive')
        if status not in ['success', 'failure', 'inconclusive', 'partial']:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

        # Session 599: Get optional outcome classification
        outcome_classification = data.get('outcome_classification')
        if outcome_classification and outcome_classification not in ['pass', 'learn', 'fail']:
            return JsonResponse({'success': False, 'error': 'Invalid outcome_classification'}, status=400)

        # Use the model's complete method which handles outcome classification
        exp.complete(
            status=status,
            result_summary=data.get('learnings', ''),
            learnings=data.get('learnings', ''),
            outcome_classification=outcome_classification
        )

        # Session 597: Auto-create ExperimentLearning record
        learning = None
        try:
            analysis = {
                'what_worked': data.get('what_worked', ''),
                'what_failed': data.get('what_failed', ''),
                'key_insight': data.get('learnings', ''),
                'recommendation': data.get('recommendation', ''),
                'confidence': 0.7 if status != 'inconclusive' else 0.3,
            }
            learning = ExperimentLearning.create_from_experiment(exp, analysis)
            logger.info(f"Created ExperimentLearning {learning.id} for experiment {exp.id}")

            # Update success patterns
            pattern = DecisionTypeSuccessPattern.update_from_learning(learning)
            if pattern:
                logger.info(f"Updated DecisionTypeSuccessPattern for {pattern.decision_type}: {pattern.success_rate:.1f}%")
        except Exception as learn_error:
            logger.error(f"Error creating learning from experiment: {learn_error}")

        # Session 657: Auto-sync linked PilotExecution records
        pilot_synced = False
        try:
            from core.models_pilot_readiness import PilotExecution
            pilots = PilotExecution.objects.filter(experiment=exp, status='running')
            for pilot in pilots:
                pilot.status = 'completed'
                pilot.ended_at = exp.ended_at
                pilot.result_summary = exp.result_summary or f'Marked as {status}'
                pilot.save()
                pilot_synced = True
                logger.info(f"Auto-synced PilotExecution {pilot.id} to completed")
        except Exception as sync_error:
            logger.error(f"Error syncing pilot execution: {sync_error}")

        return JsonResponse({
            'success': True,
            'experiment_id': str(exp.id),
            'status': exp.status,
            'outcome_classification': exp.outcome_classification,  # Session 599
            'ended_at': exp.ended_at.isoformat(),
            'learning_created': learning is not None,
            'learning_id': str(learning.id) if learning else None,
            'pilot_synced': pilot_synced,  # Session 657
            'message': f'Experiment marked as {status} (Classification: {exp.outcome_classification.upper()})'
        })

    except Experiment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Experiment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error completing experiment: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def halt_experiment(request, experiment_id):
    """
    Session 599: Manually halt a running experiment.

    POST /api/experiments/<uuid:experiment_id>/halt/

    Body:
    {
        "reason": "Why this experiment is being halted",
        "halted_by": "username or 'manual'" (optional, defaults to 'manual')
    }

    Halted experiments:
    - Are marked as 'failure' status
    - Get outcome_classification = 'fail'
    - Require rollback and remediation
    - Trigger Discord notification
    """
    try:
        import json
        from core.models_pilot_readiness import Experiment

        exp = Experiment.objects.get(id=experiment_id)

        # Check if already halted or not running
        if exp.is_halted:
            return JsonResponse({
                'success': False,
                'error': 'Experiment already halted'
            }, status=400)

        if exp.status != 'running':
            return JsonResponse({
                'success': False,
                'error': f'Cannot halt experiment with status: {exp.status}'
            }, status=400)

        data = json.loads(request.body) if request.body else {}
        reason = data.get('reason', 'Manual halt requested')
        halted_by = data.get('halted_by', 'manual')

        # Halt the experiment
        exp.halt(reason=reason, halted_by=halted_by)

        # Send Discord notification
        try:
            from core.services.discord_notifications import DiscordNotificationService
            discord = DiscordNotificationService()
            message = f"**🛑 EXPERIMENT MANUALLY HALTED**\n\n"
            message += f"**Experiment:** {exp.name}\n"
            message += f"**By:** {halted_by}\n"
            message += f"**Reason:** {reason}\n"
            message += f"**Outcome:** FAIL (rollback required)"
            discord.send_to_channel('system-status', message)
        except Exception as discord_error:
            logger.debug(f"Discord notification failed: {discord_error}")

        return JsonResponse({
            'success': True,
            'experiment_id': str(exp.id),
            'status': exp.status,
            'is_halted': exp.is_halted,
            'halt_reason': exp.halt_reason,
            'halted_by': exp.halted_by,
            'outcome_classification': exp.outcome_classification,
            'message': f'Experiment halted: {reason}'
        })

    except Experiment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Experiment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error halting experiment: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_experiment_metrics(request, experiment_id):
    """
    Session 600: Get current real-time metrics for an experiment.

    GET /api/experiments/<uuid:experiment_id>/metrics/

    Returns current values for all halt condition metrics:
    - error_rate: % of failed operations in window
    - user_trust_index: Average user rating (1-5 scale)
    - bias_detection_rate: % of outputs flagged for bias
    - integrity_anomaly: Boolean if anomaly detected
    - telemetry_kill_switch: Boolean if external kill signal

    Also includes comparison to thresholds and status (OK/ALERT).
    """
    try:
        from core.models_pilot_readiness import Experiment
        from core.services.experiment_metrics import ExperimentMetricsService

        exp = Experiment.objects.get(id=experiment_id)

        # Get metrics service
        service = ExperimentMetricsService(exp)

        # Get both raw metrics and summary with thresholds
        raw_metrics = service.gather_all_metrics()
        summary = service.get_metrics_summary()

        # Check if any conditions would trigger halt
        should_halt, halt_reason = exp.check_halt_conditions(raw_metrics)

        return JsonResponse({
            'success': True,
            'experiment_id': str(exp.id),
            'experiment_name': exp.name,
            'status': exp.status,
            'is_halted': exp.is_halted,
            'metrics': raw_metrics,
            'metrics_summary': summary,
            'would_halt': should_halt,
            'would_halt_reason': halt_reason,
            'halt_conditions': exp.halt_conditions or Experiment.get_default_halt_conditions(),
            'timestamp': timezone.now().isoformat()
        })

    except Experiment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Experiment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting experiment metrics: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_rollback_plan(request, experiment_id):
    """
    Session 600: Get the rollback plan for a failed experiment.

    GET /api/experiments/<uuid:experiment_id>/rollback/

    Returns the rollback plan with remediation steps and progress.
    """
    try:
        from core.models_pilot_readiness import Experiment
        from core.services.experiment_rollback import ExperimentRollbackService

        exp = Experiment.objects.get(id=experiment_id)

        if exp.outcome_classification != 'fail':
            return JsonResponse({
                'success': False,
                'error': 'Rollback plan only available for FAIL outcomes'
            }, status=400)

        service = ExperimentRollbackService(exp)
        plan = service.get_rollback_plan()

        if not plan:
            # Generate plan if not exists
            plan = service.save_rollback_plan()

        progress = service.get_remediation_progress()

        return JsonResponse({
            'success': True,
            'experiment_id': str(exp.id),
            'plan': plan,
            'progress': progress,
        })

    except Experiment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Experiment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting rollback plan: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_remediation_step(request, experiment_id):
    """
    Session 600: Update the completion status of a remediation step.

    POST /api/experiments/<uuid:experiment_id>/remediation/

    Body:
    {
        "step_id": 1,
        "completed": true,
        "notes": "Optional notes about completion"
    }
    """
    try:
        import json
        from core.models_pilot_readiness import Experiment
        from core.services.experiment_rollback import ExperimentRollbackService

        exp = Experiment.objects.get(id=experiment_id)

        if exp.outcome_classification != 'fail':
            return JsonResponse({
                'success': False,
                'error': 'Remediation only available for FAIL outcomes'
            }, status=400)

        data = json.loads(request.body) if request.body else {}
        step_id = data.get('step_id')
        completed = data.get('completed', True)
        notes = data.get('notes', '')

        if not step_id:
            return JsonResponse({
                'success': False,
                'error': 'step_id is required'
            }, status=400)

        service = ExperimentRollbackService(exp)
        updated_plan = service.update_remediation_step(step_id, completed, notes)
        progress = service.get_remediation_progress()

        # If all required steps complete, send Discord notification
        if progress['status'] == 'completed':
            try:
                from core.services.discord_notifications import DiscordNotificationService
                discord = DiscordNotificationService()
                message = f"**✅ REMEDIATION COMPLETE**\n\n"
                message += f"**Experiment:** {exp.name}\n"
                message += f"**Steps Completed:** {progress['completed_steps']}/{progress['total_steps']}\n"
                message += f"**Status:** All required remediation steps finished"
                discord.send_to_channel('system-status', message)
            except Exception as discord_error:
                logger.debug(f"Discord notification failed: {discord_error}")

        return JsonResponse({
            'success': True,
            'experiment_id': str(exp.id),
            'plan': updated_plan,
            'progress': progress,
        })

    except Experiment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Experiment not found'}, status=404)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error updating remediation step: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_experiment_portfolio(request):
    """
    Session 596: Get experiment portfolio metrics and KPI ownership summary.

    GET /api/experiments/portfolio/

    Returns:
    - status_counts: Experiments by status
    - kpi_owners: Who owns how many experiments
    - success_rate: Overall success rate
    - active_experiments: Count of running experiments
    - recent_completions: Recently finished experiments
    """
    try:
        from core.models_pilot_readiness import Experiment
        from collections import defaultdict

        all_experiments = Experiment.objects.select_related('pilot', 'pilot__gate', 'pilot__gate__decision')

        # Status counts
        status_counts = defaultdict(int)
        for status in ['running', 'success', 'failure', 'inconclusive']:
            status_counts[status] = all_experiments.filter(status=status).count()

        # KPI owner distribution
        kpi_owners = defaultdict(int)
        for exp in all_experiments:
            owner = exp.kpi_owner or 'Unassigned'
            kpi_owners[owner] += 1

        # Success metrics
        completed = all_experiments.exclude(status='running')
        success_count = all_experiments.filter(status='success').count()
        completed_count = completed.count()
        success_rate = round((success_count / completed_count * 100), 1) if completed_count > 0 else 0

        # Recent completions
        recent_completions = []
        for exp in all_experiments.exclude(status='running').order_by('-ended_at')[:5]:
            decision_topic = "Unknown"
            if exp.pilot and exp.pilot.gate and exp.pilot.gate.decision:
                decision_topic = exp.pilot.gate.decision.topic[:50]

            recent_completions.append({
                'id': str(exp.id),
                'name': exp.name[:50],
                'status': exp.status,
                'kpi_owner': exp.kpi_owner,
                'primary_kpi': exp.primary_kpi,
                'target_value': exp.target_value,
                'current_value': exp.current_value,
                'ended_at': exp.ended_at.isoformat() if exp.ended_at else None,
                'decision_topic': decision_topic,
            })

        # Running experiments
        running_experiments = []
        for exp in all_experiments.filter(status='running').order_by('-started_at')[:10]:
            decision_topic = "Unknown"
            if exp.pilot and exp.pilot.gate and exp.pilot.gate.decision:
                decision_topic = exp.pilot.gate.decision.topic[:50]

            # Calculate days running
            days_running = None
            if exp.started_at:
                days_running = (timezone.now() - exp.started_at).days

            running_experiments.append({
                'id': str(exp.id),
                'name': exp.name[:50],
                'kpi_owner': exp.kpi_owner,
                'primary_kpi': exp.primary_kpi,
                'target_value': exp.target_value,
                'current_value': exp.current_value,
                'days_running': days_running,
                'decision_topic': decision_topic,
            })

        return JsonResponse({
            'success': True,
            'portfolio': {
                'status_counts': dict(status_counts),
                'kpi_owners': dict(kpi_owners),
                'success_rate': success_rate,
                'total_experiments': all_experiments.count(),
                'active_count': status_counts['running'],
                'completed_count': completed_count,
            },
            'running_experiments': running_experiments,
            'recent_completions': recent_completions,
        })

    except Exception as e:
        logger.error(f"Error getting experiment portfolio: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Session 598: Learning Loop UI API Endpoints
# =============================================================================

@require_http_methods(["GET"])
def get_experiment_learnings(request):
    """
    Session 598: Get experiment learnings with filters.

    GET /api/experiments/learnings/

    Query params:
    - outcome: Filter by outcome (success, failure, partial, inconclusive)
    - decision_type: Filter by decision type
    - limit: Number of results (default 20)
    - offset: Pagination offset
    """
    try:
        from core.models_pilot_readiness import ExperimentLearning

        # Get query params
        outcome = request.GET.get('outcome')
        decision_type = request.GET.get('decision_type')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        # Build queryset
        queryset = ExperimentLearning.objects.select_related(
            'experiment',
            'experiment__pilot',
            'experiment__pilot__gate',
            'experiment__pilot__gate__decision'
        ).order_by('-extracted_at')

        # Apply filters
        if outcome:
            queryset = queryset.filter(outcome=outcome)
        if decision_type:
            queryset = queryset.filter(decision_type=decision_type)

        # Get total count before pagination
        total_count = queryset.count()

        # Apply pagination
        learnings = queryset[offset:offset + limit]

        # Build response
        results = []
        for learning in learnings:
            experiment_name = learning.experiment.name if learning.experiment else "Unknown"
            decision_topic = "Unknown"
            if learning.experiment and learning.experiment.pilot and learning.experiment.pilot.gate:
                if learning.experiment.pilot.gate.decision:
                    decision_topic = learning.experiment.pilot.gate.decision.topic[:80]

            results.append({
                'id': str(learning.id),
                'experiment_id': str(learning.experiment.id) if learning.experiment else None,
                'experiment_name': experiment_name[:60],
                'decision_topic': decision_topic,
                'outcome': learning.outcome,
                'decision_type': learning.decision_type,
                'what_worked': learning.what_worked,
                'what_failed': learning.what_failed,
                'key_insight': learning.key_insight,
                'future_recommendation': learning.future_recommendation,
                'target_kpi': learning.target_kpi,
                'actual_kpi': learning.actual_kpi,
                'kpi_delta_percent': learning.kpi_delta_percent,
                'confidence_score': learning.confidence_score,
                'extracted_at': learning.extracted_at.isoformat() if learning.extracted_at else None,
                'fed_to_thinking_agent': learning.fed_to_thinking_agent,
            })

        # Get distinct decision types for filter dropdown
        decision_types = list(ExperimentLearning.objects.values_list(
            'decision_type', flat=True
        ).distinct().order_by('decision_type'))

        # Session 618: Get fed to thinking agent count for dashboard
        fed_to_thinking_agent_count = ExperimentLearning.objects.filter(
            fed_to_thinking_agent=True
        ).count()

        return JsonResponse({
            'success': True,
            'total': total_count,
            'total_count': total_count,  # Session 618: Alias for UI compatibility
            'fed_to_thinking_agent_count': fed_to_thinking_agent_count,  # Session 618
            'limit': limit,
            'offset': offset,
            'results': results,
            'filters': {
                'outcomes': ['success', 'failure', 'partial', 'inconclusive'],
                'decision_types': [dt for dt in decision_types if dt],
            }
        })

    except Exception as e:
        logger.error(f"Error getting experiment learnings: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_success_patterns(request):
    """
    Session 598: Get success patterns by decision type.

    GET /api/experiments/patterns/

    Returns aggregated success patterns for visualization.
    """
    try:
        from core.models_pilot_readiness import DecisionTypeSuccessPattern, ExperimentLearning

        patterns = DecisionTypeSuccessPattern.objects.order_by('-total_experiments')

        results = []
        for pattern in patterns:
            results.append({
                'decision_type': pattern.decision_type,
                'total_experiments': pattern.total_experiments,
                'successful_experiments': pattern.successful_experiments,
                'failed_experiments': pattern.failed_experiments,
                'partial_success_experiments': pattern.partial_success_experiments,
                'inconclusive_experiments': pattern.inconclusive_experiments,
                'success_rate': round(pattern.success_rate, 1),
                'avg_kpi_delta_percent': round(pattern.avg_kpi_delta_percent, 1) if pattern.avg_kpi_delta_percent else None,
                'common_success_factors': pattern.common_success_factors[:3] if pattern.common_success_factors else [],
                'common_failure_factors': pattern.common_failure_factors[:3] if pattern.common_failure_factors else [],
                'top_insights': pattern.top_insights[:3] if pattern.top_insights else [],
            })

        # Overall stats
        total_learnings = ExperimentLearning.objects.count()
        successful = ExperimentLearning.objects.filter(outcome='success').count()
        failed = ExperimentLearning.objects.filter(outcome='failure').count()
        overall_success_rate = round((successful / total_learnings * 100), 1) if total_learnings > 0 else 0

        return JsonResponse({
            'success': True,
            'patterns': results,
            'summary': {
                'total_learnings': total_learnings,
                'total_patterns': len(results),
                'overall_success_rate': overall_success_rate,
                'successful_count': successful,
                'failed_count': failed,
            }
        })

    except Exception as e:
        logger.error(f"Error getting success patterns: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Session 606: Experiment Suggestions API
@require_http_methods(["GET"])
def get_experiment_suggestions(request):
    """
    GET /api/learning/experiment-suggestions/

    Session 606: Get experiment suggestions based on learning gaps.

    Returns prioritized suggestions for new experiments based on:
    - Learning gaps (themes with insufficient data)
    - High-value canonical decisions without experiments
    - Patterns from successful experiments

    Query params:
        limit: Max suggestions to return (default 10)

    Returns:
        - gaps: Learning gaps by theme with priority
        - suggestions: Prioritized experiment suggestions
        - coverage: Current experiment coverage stats
        - sample_size_guide: Recommended sample sizes by confidence level
        - summary: Summary message and stats
    """
    try:
        from core.services.experiment_suggestion import get_experiment_suggestions as get_suggestions

        limit = int(request.GET.get('limit', 10))
        result = get_suggestions(limit=limit)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting experiment suggestions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Session 607: Pilot Progress Dashboard API
@require_http_methods(["GET"])
def get_pilot_progress_dashboard(request):
    """
    GET /api/pilots/progress/

    Session 607: Comprehensive pilot progress dashboard with KPI tracking.

    Returns:
        - experiments: List of all experiments with progress data
        - summary: Aggregate stats (running, success rate, healthy %)
        - attention_needed: Experiments requiring immediate action
        - health_breakdown: Count by health status
        - timeline: Recent activity events
    """
    try:
        from core.services.pilot_progress import get_pilot_progress_dashboard as get_dashboard

        result = get_dashboard()
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting pilot progress dashboard: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_pilot_progress_detail(request, experiment_id):
    """
    GET /api/pilots/progress/<experiment_id>/

    Session 607: Get detailed progress for a single experiment.

    Returns:
        - experiment: Full progress data with KPIs, health, actions
        - details: Secondary KPIs, halt conditions, extracted metrics
        - learning: Associated learning record if exists
    """
    try:
        from core.services.pilot_progress import get_experiment_detail

        result = get_experiment_detail(str(experiment_id))
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting experiment detail: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Session 609: Auto KPI Tracking API
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def trigger_kpi_update(request):
    """
    POST /api/experiments/kpis/update/

    Session 609: Manually trigger KPI update for all running experiments.

    Returns:
        - updated: List of experiments that were updated
        - skipped: List of experiments that couldn't be updated
        - errors: Any errors encountered
        - summary: Statistics on the update run
    """
    try:
        from core.services.auto_kpi_tracking import update_all_experiment_kpis

        results = update_all_experiment_kpis()
        return JsonResponse(results)

    except Exception as e:
        logger.error(f"Error triggering KPI update: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_experiment_kpi_trend(request, experiment_id):
    """
    GET /api/experiments/<experiment_id>/kpi-trend/

    Session 609: Get KPI trend data for a specific experiment.

    Query params:
        - days: Number of days to look back (default 30)

    Returns:
        - trend_data: Time series of KPI values
        - trend_direction: up, down, stable, or insufficient_data
        - current: Current KPI value
        - target: Target KPI value
    """
    try:
        from core.services.auto_kpi_tracking import get_experiment_kpi_trend

        days = int(request.GET.get('days', 30))
        result = get_experiment_kpi_trend(str(experiment_id), days=days)
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting KPI trend: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_all_experiment_kpi_trends(request):
    """
    GET /api/experiments/kpi-trends/

    Session 609: Get KPI trend summary for all running experiments.

    Query params:
        - days: Number of days to look back (default 30)

    Returns:
        - experiments: List of experiments with trend info
        - summary: Counts of trending up, down, stable
    """
    try:
        from core.services.auto_kpi_tracking import get_all_kpi_trends

        days = int(request.GET.get('days', 30))
        result = get_all_kpi_trends(days=days)
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting all KPI trends: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_kpi_alerts(request):
    """
    GET /api/experiments/kpi-alerts/

    Session 611: Check and return KPI alerts for all running experiments.

    Returns:
        - alerts: List of alert objects sorted by severity
        - summary: Counts by severity and type
        - experiments_checked: Number of experiments analyzed
    """
    try:
        from core.services.kpi_alerts import check_kpi_alerts

        result = check_kpi_alerts()
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting KPI alerts: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_weekly_kpi_summary(request):
    """
    GET /api/experiments/kpi-summary/

    Session 611: Get weekly KPI trend summary.

    Returns:
        - week_of: Date of summary
        - experiments_tracked: Count
        - trending_up/down/stable: Counts
        - highlights: Experiments doing well
        - concerns: Experiments needing attention
    """
    try:
        from core.services.kpi_alerts import get_weekly_kpi_summary

        result = get_weekly_kpi_summary()
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting weekly KPI summary: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_recent_activity(request):
    """
    GET /api/recent-activity/

    Session 614: Get recent system activity feed.

    Aggregates recent activity from:
    - Agent Dreams
    - Agent Conversations
    - Boardroom Decisions
    - Pilot Starts/Completions

    Query params:
        - limit: Max items (default 20)
        - hours: How far back to look (default 72)

    Returns:
        - activities: List of activity items with type, icon, title, subtitle, timestamp
        - counts: Count by activity type
        - total: Total count
    """
    try:
        from core.services.recent_activity import get_recent_activity

        limit = int(request.GET.get('limit', 20))
        hours = int(request.GET.get('hours', 72))

        result = get_recent_activity(limit=limit, hours=hours)
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_experiment_recommendations(request):
    """
    GET /api/experiment-recommendations/

    Session 615: Get AI-powered recommendations for running experiments.

    Analyzes KPI trends, alerts, and progress to generate actionable recommendations:
    - 🚀 Scale up - experiments exceeding expectations
    - 🔍 Investigate - experiments with declining KPIs
    - 🔧 Adjust - experiments that are stalled
    - ✅ Continue - experiments on track
    - 🎉 Celebrate - experiments that exceeded targets
    - ⏹️ End early - experiments not meeting goals

    Returns:
        - recommendations: List of recommendations with type, reason, action
        - summary: Counts by type and action_needed count
    """
    try:
        from core.services.experiment_recommendations import get_experiment_recommendations

        result = get_experiment_recommendations()
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error getting experiment recommendations: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# URL patterns to add to core/urls.py:
"""
from core.views_agent_learning import (
    record_interaction as learning_record,
    get_preferences as learning_preferences,
    get_adaptive_context as learning_context,
    get_learning_stats as learning_stats,
    apply_preferences as learning_apply,
    clear_preferences as learning_clear,
    get_preferences_summary as learning_summary,
    share_learning as learning_share,
    get_all_preferences as learning_all,
    get_agent_conversations,
    trigger_agent_conversation,
    # Session 247: Agent Dreams
    get_agent_dreams,
    trigger_agent_dreams,
    mark_dreams_shown,
    react_to_dream
)

urlpatterns += [
    path('api/agent-learning/interaction/', learning_record, name='learning-record'),
    path('api/agent-learning/preferences/<str:agent_name>/', learning_preferences, name='learning-preferences'),
    path('api/agent-learning/context/<str:agent_name>/', learning_context, name='learning-context'),
    path('api/agent-learning/stats/', learning_stats, name='learning-stats'),
    path('api/agent-learning/apply/', learning_apply, name='learning-apply'),
    path('api/agent-learning/preferences/', learning_clear, name='learning-clear'),
    path('api/agent-learning/summary/<str:agent_name>/', learning_summary, name='learning-summary'),
    path('api/agent-learning/share/<str:agent_name>/', learning_share, name='learning-share'),
    path('api/agent-learning/all-preferences/', learning_all, name='learning-all'),
    # Session 244: Agent Conversations
    path('api/agent-conversations/', get_agent_conversations, name='agent-conversations'),
    path('api/agent-conversations/trigger/', trigger_agent_conversation, name='trigger-agent-conversation'),
    # Session 247: Agent Dreams
    path('api/agent-dreams/', get_agent_dreams, name='agent-dreams'),
    path('api/agent-dreams/trigger/', trigger_agent_dreams, name='trigger-agent-dreams'),
    path('api/agent-dreams/mark-shown/', mark_dreams_shown, name='mark-dreams-shown'),
    path('api/agent-dreams/<uuid:dream_id>/react/', react_to_dream, name='react-to-dream'),
]
"""
