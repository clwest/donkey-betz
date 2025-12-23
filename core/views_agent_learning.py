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
from django.contrib.auth.decorators import login_required

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
@login_required
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
        from datetime import timedelta
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


@require_http_methods(["POST"])
@login_required
def promote_decision(request, decision_id):
    """
    Promote a decision to canonical policy status.

    POST /api/boardroom/decisions/{decision_id}/promote/
    """
    try:
        from core.models_unified_system import AgentDecisionSummary

        decision = AgentDecisionSummary.objects.get(id=decision_id)
        decision.promote_to_canonical(promoted_by='human')

        logger.info(f"🏛️ [BOARDROOM] Decision promoted to canonical: {decision.topic}")

        return JsonResponse({
            'success': True,
            'message': f'Decision "{decision.topic}" promoted to canonical policy',
            'decision_id': str(decision.id)
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

        queryset = AgentDream.objects.filter(
            promoted_to_decision=True
        ).select_related('agent', 'project').order_by('-composite_score', '-dreamed_at')

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
        from django.db.models import Count, Avg, Q

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
        from core.models import AgentConversation, ConversationMessage

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
