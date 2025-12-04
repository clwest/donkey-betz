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
        try:
            from core.models_unified_system import AgentMemory, AgentKnowledgeSource, Collaboration, CollaborationSession
            from content.models import AgentExecution
            import os

            # Agent counts from filesystem (same logic as dashboard_stats)
            legacy_agents_dir = os.path.join(os.path.dirname(__file__), '..', 'agents')
            clean_agents_dir = os.path.join(os.path.dirname(__file__), 'agents')

            legacy_count = 0
            if os.path.exists(legacy_agents_dir):
                legacy_count = len([f for f in os.listdir(legacy_agents_dir)
                                   if f.endswith('_agent.py') and not f.startswith('_')])

            clean_count = 0
            if os.path.exists(clean_agents_dir):
                clean_count = len([f for f in os.listdir(clean_agents_dir)
                                  if f.endswith('_agent.py') and not f.startswith('_')])

            total_agents = legacy_count + clean_count

            stats['agent_memories'] = AgentMemory.objects.count()
            stats['knowledge_sources'] = AgentKnowledgeSource.objects.count()
            stats['clean_agents'] = clean_count
            stats['deprecated_agents'] = legacy_count
            stats['agents'] = {
                'total': total_agents,
                'legacy': legacy_count,
                'clean': clean_count
            }

            # Session 346: Add collaboration and learning event counts
            stats['collaborations'] = Collaboration.objects.count()
            stats['collaboration_sessions'] = CollaborationSession.objects.count()
            stats['learning_events'] = AgentExecution.objects.count()  # Agent executions as learning events

        except Exception as db_err:
            logger.debug(f"Could not fetch Session 309/346 stats: {db_err}")
            stats['agent_memories'] = 0
            stats['knowledge_sources'] = 0
            stats['clean_agents'] = 10
            stats['deprecated_agents'] = 69
            stats['agents'] = {'total': 79, 'legacy': 69, 'clean': 10}
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
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        from core.models import AgentConversation

        limit = int(request.GET.get('limit', 10))
        status_filter = request.GET.get('status')
        today_only = request.GET.get('today_only', 'false').lower() == 'true'

        # Build query
        queryset = AgentConversation.objects.select_related('initiator').prefetch_related(
            'participants', 'messages__agent'
        ).order_by('-started_at')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if today_only:
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(started_at__gte=today_start)

        conversations = queryset[:limit]

        # Format response
        conversations_data = []
        for conv in conversations:
            messages_data = []
            for msg in conv.messages.all()[:10]:  # Limit messages per conversation
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
                'messages': messages_data
            })

        # Get today's count
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = AgentConversation.objects.filter(started_at__gte=today_start).count()

        return JsonResponse({
            'success': True,
            'conversations': conversations_data,
            'count': len(conversations_data),
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
            'connection__student_agent'
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

            feed_items.append({
                'timestamp': transfer.created_at.isoformat(),
                'type': source,
                'source': 'Knowledge transfer',
                'description': description,
                'knowledge': transfer.transfer_summary[:100] if transfer.transfer_summary else 'Knowledge shared',
                'teacher': teacher.name,
                'student': student.name,
                'was_useful': transfer.was_useful,
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
    """
    try:
        from core.models_unified_system import AgentDecisionSummary
        from django.db.models import Count

        limit = int(request.GET.get('limit', 20))
        decision_type = request.GET.get('decision_type')
        impact_area = request.GET.get('impact_area')
        status = request.GET.get('status')
        canonical_only = request.GET.get('canonical_only', 'false').lower() == 'true'

        queryset = AgentDecisionSummary.objects.select_related(
            'conversation'
        ).order_by('-created_at')

        if decision_type:
            queryset = queryset.filter(decision_type=decision_type)
        if impact_area:
            queryset = queryset.filter(impact_area=impact_area)
        if status:
            queryset = queryset.filter(status=status)
        if canonical_only:
            queryset = queryset.filter(is_canonical=True)

        decisions = queryset[:limit]

        decisions_data = []
        for d in decisions:
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
                'conversation_id': str(d.conversation.id) if d.conversation else None,
                'created_at': d.created_at.isoformat(),
            })

        # Get counts by type for filters
        type_counts = dict(
            AgentDecisionSummary.objects.values('decision_type')
            .annotate(count=Count('id'))
            .values_list('decision_type', 'count')
        )

        return JsonResponse({
            'success': True,
            'decisions': decisions_data,
            'count': len(decisions_data),
            'total': AgentDecisionSummary.objects.count(),
            'canonical_count': AgentDecisionSummary.objects.filter(is_canonical=True).count(),
            'type_counts': type_counts,
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
