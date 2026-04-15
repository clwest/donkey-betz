"""
Session 327: Project-Scoped Agent Intelligence API Views

API endpoints for viewing agent intelligence (learning, conversations, dreams,
boardroom decisions) filtered by project. This enables each project to have
its own intelligence hub.
"""
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import models

logger = logging.getLogger(__name__)


# =============================================================================
# Session 327: Project-Scoped Learning Activity
# =============================================================================

@require_http_methods(["GET"])
@login_required
def get_project_learning(request, project_id):
    """
    Get agent learning activity scoped to a specific project.

    GET /api/projects/<project_id>/intelligence/learning/

    Returns learning stats, knowledge sources, and recent activity
    for this project only.
    """
    try:
        from core.models_partnership import PartnershipProject
        from core.models_unified_system import (
            AgentKnowledgeSource,
            ProjectResearchFeedback,
        )

        project = PartnershipProject.objects.get(id=project_id)

        # Get knowledge sources linked to this project
        knowledge = AgentKnowledgeSource.objects.filter(
            source_project=project
        ).select_related('agent').order_by('-first_discovered_at')[:20]

        # Get feedback for this project
        feedback = ProjectResearchFeedback.objects.filter(
            project=project
        ).order_by('-created_at')[:10]

        # Stats
        knowledge_count = knowledge.count()
        feedback_count = feedback.count()

        # Confidence distribution
        avg_confidence = knowledge.aggregate(
            avg=models.Avg('confidence_score')
        )['avg'] or 0.0

        knowledge_data = []
        for k in knowledge:
            knowledge_data.append({
                'id': str(k.id),
                'agent_name': k.agent.name if k.agent else 'Unknown',
                'topic': k.title,
                'source_type': k.knowledge_type,
                'confidence': round(k.confidence_score or 0.0, 2),
                'created_at': k.first_discovered_at.isoformat(),
            })

        feedback_data = []
        for f in feedback:
            feedback_data.append({
                'id': str(f.id),
                'feedback_type': f.feedback_type,
                'rating': f.rating,
                'applied_to_knowledge': f.applied_to_knowledge,
                'created_at': f.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'project_id': str(project_id),
            'project_name': getattr(project, 'project_name', '') or getattr(project, 'name', ''),
            'stats': {
                'knowledge_sources': knowledge_count,
                'feedback_given': feedback_count,
                'avg_confidence': round(avg_confidence, 2),
            },
            'knowledge': knowledge_data,
            'feedback': feedback_data,
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting project learning: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 327: Project-Scoped Conversations
# =============================================================================

@require_http_methods(["GET"])
@login_required
def get_project_conversations(request, project_id):
    """
    Get agent conversations scoped to a specific project.

    GET /api/projects/<project_id>/intelligence/conversations/

    Returns conversations that have been linked to this project,
    plus any HiveMindSession conversations for this project.
    """
    try:
        from core.models_partnership import PartnershipProject
        from core.models_unified_system import HiveMindSession, HiveMindContribution
        from core.models import AgentConversation

        project = PartnershipProject.objects.get(id=project_id)
        limit = int(request.GET.get('limit', 10))

        # Get HiveMind sessions with conversation mode for this project
        hive_sessions = HiveMindSession.objects.filter(
            project=project,
            session_mode='conversation'
        ).order_by('-created_at')[:limit]

        # Also get legacy AgentConversation for this project
        legacy_convos = AgentConversation.objects.filter(
            project=project
        ).select_related('initiator').prefetch_related(
            'participants', 'messages__agent'
        ).order_by('-started_at')[:limit]

        conversations_data = []

        # Format HiveMind sessions
        for session in hive_sessions:
            # Session 329: Fetch the actual contribution messages
            contributions = HiveMindContribution.objects.filter(
                session=session
            ).select_related('agent').order_by('created_at')

            messages_data = []
            for contrib in contributions:
                if contrib.contribution:  # Only include if there's actual content
                    messages_data.append({
                        'agent': contrib.agent.name,
                        'agent_id': str(contrib.agent.id),
                        'content': contrib.contribution,
                        'status': contrib.status,
                        'created_at': contrib.created_at.isoformat() if contrib.created_at else None,
                    })

            conversations_data.append({
                'id': str(session.id),
                'type': 'hive_mind',
                'topic': session.conversation_topic or session.question[:100],
                'status': session.status,
                'participant_count': len(session.participant_ids) if session.participant_ids else contributions.count(),
                'contribution_count': contributions.filter(status='completed').count(),
                'pending_count': contributions.filter(status='pending').count(),
                'synthesis_summary': session.synthesis_summary,
                'created_at': session.created_at.isoformat(),
                'messages': messages_data,  # Session 329: Include the actual messages!
            })

        # Session 330: Format AgentConversation with ALL multi-turn messages
        # These are now the primary project conversations (like Agent/Social tab)
        for conv in legacy_convos:
            messages_data = []
            # Get ALL messages in sequence order for full multi-turn display
            for msg in conv.messages.all().order_by('sequence_number'):
                messages_data.append({
                    'agent': msg.agent.name if msg.agent else 'Unknown',
                    'agent_id': str(msg.agent.id) if msg.agent else None,
                    'content': msg.content,  # Full content for proper display
                    'type': msg.message_type,
                    'sequence': msg.sequence_number,
                    'created_at': msg.created_at.isoformat() if msg.created_at else None,
                })

            conversations_data.append({
                'id': str(conv.id),
                'type': 'multi_turn',  # Session 330: Distinguish from hive_mind
                'topic': conv.topic,
                'conversation_type': conv.conversation_type,  # brainstorm, debate, etc.
                'status': conv.status,
                'initiator': conv.initiator.name if conv.initiator else None,
                'participants': [p.name for p in conv.participants.all()],
                'participant_count': conv.participants.count(),
                'message_count': conv.message_count or len(messages_data),
                'quality_score': conv.quality_score,
                'conclusion': conv.conclusion,
                'created_at': conv.started_at.isoformat(),
                'messages': messages_data,
            })

        # Sort by date
        conversations_data.sort(key=lambda x: x['created_at'], reverse=True)

        return JsonResponse({
            'success': True,
            'project_id': str(project_id),
            'project_name': getattr(project, 'project_name', '') or getattr(project, 'name', ''),
            'count': len(conversations_data),
            'conversations': conversations_data[:limit],
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting project conversations: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 327: Project-Scoped Dreams
# =============================================================================

@require_http_methods(["GET"])
def get_project_dreams(request, project_id):
    """
    Get agent dreams scoped to a specific project.

    GET /api/projects/<project_id>/intelligence/dreams/
    """
    try:
        from core.models_partnership import PartnershipProject
        from core.models import AgentDream

        project = PartnershipProject.objects.get(id=project_id)
        limit = int(request.GET.get('limit', 10))

        dreams = AgentDream.objects.filter(
            project=project
        ).select_related('agent').order_by('-dreamed_at')[:limit]

        dreams_data = []
        for dream in dreams:
            dreams_data.append({
                'id': str(dream.id),
                'agent_name': dream.agent.name if dream.agent else 'Unknown',
                'title': dream.title,
                'content': dream.content,
                'dream_type': dream.dream_type,
                'inspiration': dream.inspiration_source,
                'creativity_score': dream.creativity_score,
                'shown_to_user': dream.shown_to_user,
                'user_reaction': dream.user_reaction,
                'dreamed_at': dream.dreamed_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'project_id': str(project_id),
            'project_name': getattr(project, 'project_name', '') or getattr(project, 'name', ''),
            'count': len(dreams_data),
            'dreams': dreams_data,
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting project dreams: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 327: Project-Scoped Boardroom Decisions
# =============================================================================

@require_http_methods(["GET"])
@login_required
def get_project_boardroom(request, project_id):
    """
    Get boardroom decisions scoped to a specific project.

    GET /api/projects/<project_id>/intelligence/boardroom/
    """
    try:
        from core.models_partnership import PartnershipProject
        from core.models_unified_system import AgentDecisionSummary

        project = PartnershipProject.objects.get(id=project_id)
        limit = int(request.GET.get('limit', 20))

        # Session 519: AgentDecisionSummary doesn't have direct project field
        # Filter through linked conversation.project or hive_session.project
        from django.db.models import Q
        base_qs = AgentDecisionSummary.objects.filter(
            Q(conversation__project=project) | Q(hive_session__project=project)
        )
        canonical_count = base_qs.filter(is_canonical=True).count()

        # Now get the limited results
        decisions = base_qs.select_related('conversation', 'hive_session').order_by('-created_at')[:limit]

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
                'participants': d.participants,
                'status': d.status,
                'status_display': d.get_status_display(),
                'is_canonical': d.is_canonical,
                'created_at': d.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'project_id': str(project_id),
            'project_name': getattr(project, 'project_name', '') or getattr(project, 'name', ''),
            'count': len(decisions_data),
            'canonical_count': canonical_count,
            'decisions': decisions_data,
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting project boardroom: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 327: Project Intelligence Overview
# =============================================================================

@require_http_methods(["GET"])
@login_required
def get_project_intelligence_overview(request, project_id):
    """
    Get an overview of all agent intelligence for a project.

    GET /api/projects/<project_id>/intelligence/

    Returns aggregated stats and recent activity across:
    - Learning (knowledge sources, feedback)
    - Conversations (hive mind, agent-to-agent)
    - Dreams
    - Boardroom decisions
    """
    try:
        from core.models_partnership import PartnershipProject
        from core.models_unified_system import (
            AgentKnowledgeSource,
            ProjectResearchFeedback,
            HiveMindSession,
            AgentDecisionSummary,
        )
        from core.models import AgentConversation, AgentDream
        from django.db.models import Avg

        project = PartnershipProject.objects.get(id=project_id)

        # Learning stats
        knowledge_count = AgentKnowledgeSource.objects.filter(
            source_project=project
        ).count()
        feedback_count = ProjectResearchFeedback.objects.filter(
            project=project
        ).count()
        avg_confidence = AgentKnowledgeSource.objects.filter(
            source_project=project
        ).aggregate(avg=Avg('confidence_score'))['avg'] or 0.0

        # Conversation stats
        hive_count = HiveMindSession.objects.filter(
            project=project,
            session_mode='conversation'
        ).count()
        legacy_conv_count = AgentConversation.objects.filter(
            project=project
        ).count()

        # Dream stats
        dream_count = AgentDream.objects.filter(
            project=project
        ).count()

        # Boardroom stats - Session 519: Filter through linked models
        from django.db.models import Q
        decision_qs = AgentDecisionSummary.objects.filter(
            Q(conversation__project=project) | Q(hive_session__project=project)
        )
        decision_count = decision_qs.count()
        canonical_count = decision_qs.filter(is_canonical=True).count()

        # Recent activity timestamps
        recent_knowledge = AgentKnowledgeSource.objects.filter(
            source_project=project
        ).order_by('-first_discovered_at').first()
        recent_conv = HiveMindSession.objects.filter(
            project=project
        ).order_by('-created_at').first()
        recent_decision = decision_qs.order_by('-created_at').first()

        return JsonResponse({
            'success': True,
            'project_id': str(project_id),
            'project_name': getattr(project, 'project_name', '') or getattr(project, 'name', ''),
            'learning': {
                'knowledge_sources': knowledge_count,
                'feedback_given': feedback_count,
                'avg_confidence': round(avg_confidence, 2),
                'last_activity': recent_knowledge.first_discovered_at.isoformat() if recent_knowledge else None,
            },
            'conversations': {
                'hive_sessions': hive_count,
                'agent_conversations': legacy_conv_count,
                'total': hive_count + legacy_conv_count,
                'last_activity': recent_conv.created_at.isoformat() if recent_conv else None,
            },
            'dreams': {
                'total': dream_count,
            },
            'boardroom': {
                'total_decisions': decision_count,
                'canonical_policies': canonical_count,
                'last_activity': recent_decision.created_at.isoformat() if recent_decision else None,
            },
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting project intelligence overview: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 327: Trigger Project-Scoped Agent Conversation
# =============================================================================

@require_http_methods(["POST"])
@login_required
def trigger_project_conversation(request, project_id):
    """
    Trigger a new multi-turn agent conversation about a project topic.

    Session 330: Now uses AgentConversation model with multi-turn messages
    (like Agent/Social tab) instead of HiveMind parallel responses.

    POST /api/projects/<project_id>/intelligence/conversations/trigger/

    Request Body:
    {
        "topic": "What marketing strategy should we use?"
    }
    """
    import json

    try:
        from core.models_partnership import PartnershipProject

        project = PartnershipProject.objects.get(id=project_id)
        data = json.loads(request.body)

        topic = data.get('topic', f"Discussion about {project.project_name}")

        # Session 330: Use the new run_project_conversation task
        # This creates AgentConversation with multi-turn ConversationMessage records
        # (like Agent/Social tab conversations)
        from core.tasks import run_project_conversation
        result = run_project_conversation.delay(str(project_id), topic)

        logger.info(f"Project conversation triggered: {topic} (task: {result.id})")

        return JsonResponse({
            'success': True,
            'task_id': str(result.id),
            'topic': topic,
            'message': f"Conversation started about: {topic}. Agents are now discussing...",
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error triggering project conversation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 328: Project-Scoped Spider Network
# =============================================================================

@require_http_methods(["GET"])
@login_required
def get_project_spiders(request, project_id):
    """
    Get spider network data scoped to a specific project.

    GET /api/projects/<project_id>/intelligence/spiders/

    Returns:
    - Spider priority weights for this project
    - Recent spider data relevant to project topics
    - Spider activity related to project research
    """
    try:
        from core.models_partnership import PartnershipProject
        from core.models_unified_system import (
            SpiderData,
            ProjectSpiderPriority,
        )
        from core.services.spider_priority_engine import get_spider_priority_engine

        project = PartnershipProject.objects.get(id=project_id)

        # Get spider priorities for this project
        priorities = ProjectSpiderPriority.objects.filter(
            project=project
        ).select_related('spider_category').order_by('-priority_weight')

        # Get topics from project for matching spider data
        engine = get_spider_priority_engine()
        project_name = getattr(project, 'project_name', '') or getattr(project, 'name', '') or ''
        text = f"{project_name} {project.description or ''}"
        topics = engine.detect_topics(text)

        # Get recent spider data matching project topics
        spider_data = []
        if topics:
            # Build query to find matching spider data
            from django.db.models import Q
            query = Q()
            for topic in topics:
                query |= Q(spider_name__icontains=topic)
                query |= Q(raw_data__icontains=topic)

            # Session 807: Defer embedding fields to reduce egress costs
            recent_data = SpiderData.objects.filter(query).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:20]
            for sd in recent_data:
                spider_data.append({
                    'id': str(sd.id),
                    'spider_name': sd.spider_name,
                    'data_type': sd.data_type,
                    'summary': (sd.raw_data or {}).get('summary', '')[:200] if sd.raw_data else '',
                    'url': (sd.raw_data or {}).get('url', '') if sd.raw_data else '',
                    'created_at': sd.created_at.isoformat(),
                })

        # Format priority data
        priority_data = []
        for p in priorities:
            priority_data.append({
                'category': p.spider_category.name if p.spider_category else 'Unknown',
                'category_slug': p.spider_category.slug if p.spider_category else '',
                'weight': round(p.priority_weight, 2),
                'matched_keywords': p.matched_keywords or [],
                'effectiveness': round(p.effectiveness_score, 2),
                'data_used_count': p.data_used_count,
            })

        # Get overall spider stats
        try:
            from ai_core.spiders.spider_registry import SpiderRegistry
            registry = SpiderRegistry()
            spider_count = len(registry.list_spiders())
        except Exception:
            spider_count = 77  # Default fallback - Session 589 updated

        return JsonResponse({
            'success': True,
            'project_id': str(project_id),
            'project_name': project_name,
            'stats': {
                'total_spiders': spider_count,
                'priority_categories': len(priority_data),
                'matched_topics': topics,
                'relevant_data_count': len(spider_data),
            },
            'priorities': priority_data,
            'spider_data': spider_data,
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting project spiders: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def refresh_project_spiders(request, project_id):
    """
    Trigger spider refresh for a specific project.

    POST /api/projects/<project_id>/intelligence/spiders/refresh/

    This will:
    1. Recalculate spider priorities for the project
    2. Trigger high-priority spiders to run
    """
    try:
        from core.models_partnership import PartnershipProject
        from core.services.spider_priority_engine import get_spider_priority_engine
        from core.tasks import execute_single_spider

        project = PartnershipProject.objects.get(id=project_id)

        # Update spider priorities
        engine = get_spider_priority_engine()
        result = engine.update_project_priorities(project)

        # Trigger some spiders based on priorities
        from core.models_unified_system import ProjectSpiderPriority
        top_priorities = ProjectSpiderPriority.objects.filter(
            project=project
        ).order_by('-priority_weight')[:3]

        triggered = []
        for priority in top_priorities:
            if priority.spider_category:
                # Try to find a spider in this category
                try:
                    from ai_core.spiders.spider_registry import SpiderRegistry
                    registry = SpiderRegistry()
                    all_spiders = registry.list_spiders()

                    for spider_name, spider_info in all_spiders.items():
                        config = spider_info.get('config', {})
                        if config.get('category') == priority.spider_category.slug:
                            execute_single_spider.delay(spider_name)
                            triggered.append(spider_name)
                            break
                except Exception as e:
                    logger.warning(f"Could not trigger spider for category {priority.spider_category.slug}: {e}")

        return JsonResponse({
            'success': True,
            'project_id': str(project_id),
            'priorities_updated': result['categories_matched'],
            'spiders_triggered': triggered,
            'message': f"Updated {result['categories_matched']} priorities, triggered {len(triggered)} spiders"
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error refreshing project spiders: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 328: Project-Scoped Agent Slack
# =============================================================================

@require_http_methods(["GET"])
@login_required
def get_project_slack_channel(request, project_id):
    """
    Get or create a dedicated Agent Slack channel for a project.

    GET /api/projects/<project_id>/intelligence/slack/

    Returns:
    - Project channel info
    - Recent messages
    - Online agents
    """
    try:
        from core.models_partnership import PartnershipProject
        from core.models import Agent, AgentChannel, ChannelMessage, ChannelMembership

        project = PartnershipProject.objects.get(id=project_id)
        project_name = getattr(project, 'project_name', '') or getattr(project, 'name', '') or ''

        # Create channel name from project (slug format)
        import re
        channel_name = re.sub(r'[^a-z0-9-]', '-', project_name.lower())
        channel_name = re.sub(r'-+', '-', channel_name).strip('-')[:50]
        if not channel_name:
            channel_name = f"project-{str(project_id)[:8]}"

        # Get or create the channel
        channel, created = AgentChannel.objects.get_or_create(
            name=channel_name,
            defaults={
                'description': f"Discussion channel for: {project_name}",
                'channel_type': 'project',
                'topic': project.description[:200] if project.description else '',
            }
        )

        # Get recent messages
        messages = ChannelMessage.objects.filter(
            channel=channel,
            thread_parent__isnull=True
        ).select_related('agent').order_by('-created_at')[:30]

        messages_data = []
        for msg in reversed(list(messages)):
            messages_data.append({
                'id': str(msg.id),
                'agent_id': str(msg.agent.id) if msg.agent else None,
                'agent_name': msg.agent.name if msg.agent else 'System',
                'content': msg.content,
                'message_type': msg.message_type,
                'reactions': msg.reactions or {},
                'created_at': msg.created_at.isoformat()
            })

        # Get channel members (online agents)
        memberships = ChannelMembership.objects.filter(
            channel=channel,
            is_active=True
        ).select_related('agent')

        members_data = []
        for m in memberships:
            if m.agent:
                members_data.append({
                    'id': str(m.agent.id),
                    'name': m.agent.name,
                    'type': m.agent.agent_type,
                    'role': m.role,
                    'presence': m.presence_status,
                })

        # If no members yet, add some default agents (use ALL agents including legacy)
        if not members_data:
            active_agents = Agent.objects.all().order_by('?')[:5]
            for agent in active_agents:
                ChannelMembership.objects.get_or_create(
                    channel=channel,
                    agent=agent,
                    defaults={'role': 'member', 'presence_status': 'online'}
                )
                members_data.append({
                    'id': str(agent.id),
                    'name': agent.name,
                    'type': agent.agent_type,
                    'role': 'member',
                    'presence': 'online',
                })

        return JsonResponse({
            'success': True,
            'project_id': str(project_id),
            'project_name': project_name,
            'channel': {
                'id': str(channel.id),
                'name': channel.name,
                'description': channel.description,
                'channel_type': channel.channel_type,
                'topic': channel.topic,
                'message_count': channel.message_count,
                'is_new': created,
            },
            'messages': messages_data,
            'members': members_data,
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting project slack channel: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def post_project_slack_message(request, project_id):
    """
    Post a message to a project's Agent Slack channel.

    POST /api/projects/<project_id>/intelligence/slack/message/

    Request Body:
    {
        "content": "Hello @AgentName, what do you think about...",
        "sender_name": "User"
    }
    """
    import json

    try:
        from core.models_partnership import PartnershipProject
        from core.models import Agent, AgentChannel, ChannelMessage
        import re

        project = PartnershipProject.objects.get(id=project_id)
        data = json.loads(request.body)

        content = data.get('content', '')
        sender_name = data.get('sender_name', 'User')

        if not content:
            return JsonResponse({
                'success': False,
                'error': 'Message content required'
            }, status=400)

        project_name = getattr(project, 'project_name', '') or getattr(project, 'name', '') or ''

        # Get channel name
        channel_name = re.sub(r'[^a-z0-9-]', '-', project_name.lower())
        channel_name = re.sub(r'-+', '-', channel_name).strip('-')[:50]
        if not channel_name:
            channel_name = f"project-{str(project_id)[:8]}"

        # Get or create channel
        channel, _ = AgentChannel.objects.get_or_create(
            name=channel_name,
            defaults={
                'description': f"Discussion channel for: {project_name}",
                'channel_type': 'project',
            }
        )

        # Get or create UserProxy agent
        user_agent, _ = Agent.objects.get_or_create(
            name='UserProxy',
            defaults={
                'agent_type': 'proxy',
                'specialization': 'Represents human users in agent channels'
            }
        )

        # Create the message
        message = ChannelMessage.objects.create(
            channel=channel,
            agent=user_agent,
            content=content,
            message_type='message'
        )

        # Parse mentions and queue agent responses
        mentions = re.findall(r'@(\w+)', content)
        agent_responses = []

        if mentions:
            for agent_name in set(mentions):
                agent = Agent.objects.filter(name=agent_name).first()
                if agent:
                    # Generate a quick response (in production this would be async via WebSocket)
                    response_content = await_agent_response(agent, content, project_name)
                    if response_content:
                        response_msg = ChannelMessage.objects.create(
                            channel=channel,
                            agent=agent,
                            content=response_content,
                            message_type='message',
                            thread_parent=message
                        )
                        agent_responses.append({
                            'id': str(response_msg.id),
                            'agent_name': agent.name,
                            'content': response_content,
                            'created_at': response_msg.created_at.isoformat()
                        })

        return JsonResponse({
            'success': True,
            'message': {
                'id': str(message.id),
                'content': content,
                'sender_name': sender_name,
                'created_at': message.created_at.isoformat()
            },
            'agent_responses': agent_responses,
        })

    except PartnershipProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error posting project slack message: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def await_agent_response(agent, trigger_content: str, project_name: str) -> str:
    """
    Generate a synchronous agent response for project slack.
    Uses agent's knowledge and project context.
    """
    from core.models import AgentKnowledgeSource, AgentMemory
    from core.services.openai_client_factory import get_openai_client
    import os

    # Get agent's knowledge
    knowledge_context = []

    sources = AgentKnowledgeSource.objects.filter(
        agent=agent
    ).order_by('-last_updated_at')[:3]

    for source in sources:
        if source.summary:
            knowledge_context.append(f"[Knowledge] {source.title}: {source.summary[:150]}")

    memories = AgentMemory.objects.filter(
        agent=agent
    ).order_by('-created_at')[:3]

    for memory in memories:
        if memory.content:
            knowledge_context.append(f"[Memory] {memory.memory_type}: {memory.content[:150]}")

    knowledge_str = "\n".join(knowledge_context) if knowledge_context else "No specific knowledge loaded."

    system_prompt = f"""You are {agent.name}, a specialized AI agent.
Type: {agent.agent_type}
Specialization: {agent.specialization or 'General AI assistance'}

Current Project Context: {project_name}

Your Knowledge:
{knowledge_str}

Respond helpfully and concisely (2-3 sentences max).
Use your knowledge when relevant. Be collaborative."""

    user_prompt = f"""Message in the project channel:
"{trigger_content}"

Respond helpfully about this project."""

    try:
        client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.responses.create(
            model="gpt-5-mini",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_output_tokens=300
        )

        return response.output_text.strip() if response.output_text else None

    except Exception as e:
        logger.error(f"Error generating agent response: {e}")
        return None
