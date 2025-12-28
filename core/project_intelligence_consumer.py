"""
Project Intelligence Hub WebSocket Consumer
============================================

Session 332: Unified real-time streaming for all Project Intelligence Hub tabs:
- Learning (knowledge sources, feedback, transfers)
- Conversations (agent-to-agent chats)
- Dreams (agent creative thoughts)
- Boardroom (decisions and policies)

This brings the Agent/Social tab experience to the project level.
Each project has its own WebSocket group for scoped updates.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProjectIntelligenceConsumer(AsyncWebsocketConsumer):
    """
    Unified WebSocket consumer for all Project Intelligence Hub tabs.

    Features:
    - Project-scoped updates only
    - Learning feed (knowledge transfers, sources)
    - Conversations (real-time agent chat)
    - Dreams (agent creative thoughts)
    - Boardroom (decisions and policies)
    - Live status indicators
    """

    async def connect(self):
        """Accept connection and join project intelligence group."""
        self.project_id = self.scope['url_route']['kwargs'].get('project_id')

        if not self.project_id:
            await self.close()
            return

        # Create unique group for this project's intelligence feed
        self.room_group_name = f'project_intelligence_{self.project_id}'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Project Intelligence WebSocket connected: {self.channel_name} for project {self.project_id}")

        # Send initial data for all tabs
        await self.send_initial_data()

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'project_id': self.project_id,
            'message': 'Connected to Project Intelligence Hub',
            'timestamp': timezone.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """Leave group on disconnect."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"Project Intelligence WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming messages from client."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'get_learning':
                await self.send_learning_data()

            elif message_type == 'get_conversations':
                await self.send_conversations_data()

            elif message_type == 'get_dreams':
                await self.send_dreams_data()

            elif message_type == 'get_boardroom':
                await self.send_boardroom_data()

            elif message_type == 'start_conversation':
                topic = data.get('topic', 'project discussion')
                await self.trigger_conversation(topic)

            elif message_type == 'trigger_dream':
                await self.trigger_dream()

            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))

        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_initial_data(self):
        """Send initial data for all tabs on connect."""
        await self.send_learning_data()
        await self.send_conversations_data()
        await self.send_dreams_data()
        await self.send_boardroom_data()

    # =========================================================================
    # Learning Tab
    # =========================================================================

    async def send_learning_data(self):
        """Send learning activity for this project."""
        try:
            data = await self.get_learning_data()
            await self.send(text_data=json.dumps({
                'type': 'learning_data',
                'project_id': self.project_id,
                **data,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending learning data: {e}")

    @database_sync_to_async
    def get_learning_data(self):
        """Fetch learning activity for this project."""
        from core.models_partnership import PartnershipProject
        from core.models_unified_system import AgentKnowledgeSource, ProjectResearchFeedback
        from core.models import KnowledgeTransfer
        from django.db.models import Avg

        try:
            project = PartnershipProject.objects.get(id=self.project_id)
        except PartnershipProject.DoesNotExist:
            return {'knowledge': [], 'transfers': [], 'stats': {}}

        # Get knowledge sources for this project
        knowledge = AgentKnowledgeSource.objects.filter(
            source_project=project
        ).select_related('agent').order_by('-first_discovered_at')[:20]

        # Get feedback for this project
        feedback = ProjectResearchFeedback.objects.filter(
            project=project
        ).order_by('-created_at')[:10]

        # Get knowledge transfers involving project agents
        # Note: Must get distinct agent_ids before slicing
        agent_ids = list(set(AgentKnowledgeSource.objects.filter(
            source_project=project
        ).values_list('agent_id', flat=True)))
        transfers = KnowledgeTransfer.objects.filter(
            connection__teacher_agent_id__in=agent_ids
        ).select_related(
            'connection__teacher_agent',
            'connection__student_agent'
        ).order_by('-created_at')[:15]

        # Stats
        avg_confidence = knowledge.aggregate(avg=Avg('confidence_score'))['avg'] or 0.0

        knowledge_data = []
        for k in knowledge:
            knowledge_data.append({
                'id': str(k.id),
                'agent_name': k.agent.name if k.agent else 'Unknown',
                'title': k.title,
                'knowledge_type': k.knowledge_type,
                'confidence': round(k.confidence_score or 0.0, 2),
                'summary': k.summary[:150] if k.summary else '',
                'created_at': k.first_discovered_at.isoformat() if k.first_discovered_at else None,
            })

        transfers_data = []
        for t in transfers:
            teacher = t.connection.teacher_agent
            student = t.connection.student_agent
            transfers_data.append({
                'id': str(t.id),
                'teacher': teacher.name if teacher else 'Unknown',
                'student': student.name if student else 'Unknown',
                'summary': t.transfer_summary[:100] if t.transfer_summary else 'Knowledge shared',
                'was_useful': t.was_useful,
                'created_at': t.created_at.isoformat() if t.created_at else None,
            })

        feedback_data = []
        for f in feedback:
            feedback_data.append({
                'id': str(f.id),
                'feedback_type': f.feedback_type,
                'rating': f.rating,
                'applied': f.applied_to_knowledge,
                'created_at': f.created_at.isoformat() if f.created_at else None,
            })

        return {
            'knowledge': knowledge_data,
            'transfers': transfers_data,
            'feedback': feedback_data,
            'stats': {
                'knowledge_count': len(knowledge_data),
                'transfer_count': len(transfers_data),
                'feedback_count': len(feedback_data),
                'avg_confidence': round(avg_confidence, 2),
            }
        }

    # =========================================================================
    # Conversations Tab
    # =========================================================================

    async def send_conversations_data(self):
        """Send conversations for this project."""
        try:
            data = await self.get_conversations_data()
            await self.send(text_data=json.dumps({
                'type': 'conversations_data',
                'project_id': self.project_id,
                **data,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending conversations data: {e}")

    @database_sync_to_async
    def get_conversations_data(self):
        """Fetch conversations for this project."""
        from core.models import AgentConversation

        conversations = AgentConversation.objects.filter(
            project_id=self.project_id
        ).select_related(
            'initiator'
        ).prefetch_related(
            'participants', 'messages__agent'
        ).order_by('-started_at')[:10]

        result = []
        for conv in conversations:
            messages = []
            for msg in conv.messages.all().order_by('sequence_number')[:20]:
                messages.append({
                    'agent': msg.agent.name if msg.agent else 'Unknown',
                    'agent_id': str(msg.agent.id) if msg.agent else None,
                    'content': msg.content,
                    'type': msg.message_type,
                    'sequence': msg.sequence_number,
                    'timestamp': msg.created_at.isoformat() if msg.created_at else None
                })

            result.append({
                'id': str(conv.id),
                'topic': conv.topic,
                'type': conv.conversation_type,
                'status': conv.status,
                'initiator': conv.initiator.name if conv.initiator else None,
                'participants': [p.name for p in conv.participants.all()],
                'message_count': conv.message_count or len(messages),
                'conclusion': conv.conclusion,
                'quality_score': conv.quality_score,
                'started_at': conv.started_at.isoformat() if conv.started_at else None,
                'messages': messages
            })

        return {
            'conversations': result,
            'count': len(result)
        }

    async def trigger_conversation(self, topic):
        """Trigger a new project conversation via Celery task."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_starting',
            'project_id': self.project_id,
            'topic': topic,
            'message': 'Starting new agent conversation...',
            'timestamp': timezone.now().isoformat()
        }))

        try:
            result = await self.start_conversation_task(topic)
            await self.send(text_data=json.dumps({
                'type': 'conversation_triggered',
                'project_id': self.project_id,
                'task_id': result,
                'topic': topic,
                'message': 'Agents are now discussing. Watch for live messages!',
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error triggering conversation: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to start conversation: {str(e)}'
            }))

    @database_sync_to_async
    def start_conversation_task(self, topic):
        """Start the Celery task for project conversation."""
        from core.tasks import run_project_conversation
        result = run_project_conversation.delay(self.project_id, topic)
        return str(result.id)

    # =========================================================================
    # Dreams Tab
    # =========================================================================

    async def send_dreams_data(self):
        """Send dreams for this project."""
        try:
            data = await self.get_dreams_data()
            await self.send(text_data=json.dumps({
                'type': 'dreams_data',
                'project_id': self.project_id,
                **data,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending dreams data: {e}")

    @database_sync_to_async
    def get_dreams_data(self):
        """Fetch dreams for this project."""
        from core.models_partnership import PartnershipProject
        from core.models import AgentDream

        try:
            project = PartnershipProject.objects.get(id=self.project_id)
        except PartnershipProject.DoesNotExist:
            return {'dreams': [], 'count': 0}

        dreams = AgentDream.objects.filter(
            project=project
        ).select_related('agent').order_by('-dreamed_at')[:15]

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
                'dreamed_at': dream.dreamed_at.isoformat() if dream.dreamed_at else None,
            })

        return {
            'dreams': dreams_data,
            'count': len(dreams_data)
        }

    async def trigger_dream(self):
        """Trigger dream generation for this project."""
        await self.send(text_data=json.dumps({
            'type': 'dream_generating',
            'project_id': self.project_id,
            'message': 'Asking agents to dream about this project...',
            'timestamp': timezone.now().isoformat()
        }))

        try:
            result = await self.start_dream_task()
            await self.send(text_data=json.dumps({
                'type': 'dream_triggered',
                'project_id': self.project_id,
                'task_id': result,
                'message': 'Agents are dreaming. New ideas will appear soon!',
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error triggering dream: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to trigger dream: {str(e)}'
            }))

    @database_sync_to_async
    def start_dream_task(self):
        """Start the Celery task for project dreams."""
        from core.tasks import generate_agent_dreams
        result = generate_agent_dreams.delay(max_dreamers=3, dreams_per_agent=1)
        return str(result.id)

    # =========================================================================
    # Boardroom Tab
    # =========================================================================

    async def send_boardroom_data(self):
        """Send boardroom decisions for this project."""
        try:
            data = await self.get_boardroom_data()
            await self.send(text_data=json.dumps({
                'type': 'boardroom_data',
                'project_id': self.project_id,
                **data,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending boardroom data: {e}")

    @database_sync_to_async
    def get_boardroom_data(self):
        """Fetch boardroom decisions for this project."""
        from core.models_partnership import PartnershipProject
        from core.models_unified_system import AgentDecisionSummary

        try:
            project = PartnershipProject.objects.get(id=self.project_id)
        except PartnershipProject.DoesNotExist:
            return {'decisions': [], 'count': 0, 'canonical_count': 0}

        # Get base queryset for stats
        base_qs = AgentDecisionSummary.objects.filter(project=project)
        canonical_count = base_qs.filter(is_canonical=True).count()

        # Get decisions
        decisions = base_qs.select_related('conversation').order_by('-created_at')[:20]

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
                'created_at': d.created_at.isoformat() if d.created_at else None,
            })

        return {
            'decisions': decisions_data,
            'count': len(decisions_data),
            'canonical_count': canonical_count
        }

    # =========================================================================
    # Group Message Handlers (broadcasts from Celery tasks)
    # =========================================================================

    # Conversation handlers
    async def conversation_started(self, event):
        """Handle conversation started notification."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_started',
            'conversation_id': event.get('conversation_id'),
            'project_id': event.get('project_id'),
            'topic': event.get('topic'),
            'participants': event.get('participants'),
            'conversation_type': event.get('conversation_type'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def typing_indicator(self, event):
        """Handle typing indicator."""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'conversation_id': event.get('conversation_id'),
            'agent': event.get('agent'),
            'agent_id': event.get('agent_id'),
            'timestamp': timezone.now().isoformat()
        }))

    async def new_message(self, event):
        """Handle new conversation message."""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'conversation_id': event.get('conversation_id'),
            'agent': event.get('agent'),
            'agent_id': event.get('agent_id'),
            'content': event.get('content'),
            'message_type': event.get('message_type'),
            'sequence': event.get('sequence'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def conversation_ended(self, event):
        """Handle conversation ended."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_ended',
            'conversation_id': event.get('conversation_id'),
            'conclusion': event.get('conclusion'),
            'message_count': event.get('message_count'),
            'quality_score': event.get('quality_score'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    # Learning handlers
    async def learning_event(self, event):
        """Handle new learning event."""
        await self.send(text_data=json.dumps({
            'type': 'learning_event',
            'event_type': event.get('event_type'),
            'agent': event.get('agent'),
            'title': event.get('title'),
            'summary': event.get('summary'),
            'confidence': event.get('confidence'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def knowledge_transfer(self, event):
        """Handle knowledge transfer between agents."""
        await self.send(text_data=json.dumps({
            'type': 'knowledge_transfer',
            'teacher': event.get('teacher'),
            'student': event.get('student'),
            'summary': event.get('summary'),
            'was_useful': event.get('was_useful'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    # Dream handlers
    async def new_dream(self, event):
        """Handle new dream generated."""
        await self.send(text_data=json.dumps({
            'type': 'new_dream',
            'dream_id': event.get('dream_id'),
            'agent': event.get('agent'),
            'title': event.get('title'),
            'content': event.get('content'),
            'dream_type': event.get('dream_type'),
            'creativity_score': event.get('creativity_score'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    # Boardroom handlers
    async def new_decision(self, event):
        """Handle new boardroom decision."""
        await self.send(text_data=json.dumps({
            'type': 'new_decision',
            'decision_id': event.get('decision_id'),
            'topic': event.get('topic'),
            'decision_type': event.get('decision_type'),
            'key_insights': event.get('key_insights'),
            'is_canonical': event.get('is_canonical'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def decision_promoted(self, event):
        """Handle decision promoted to canonical."""
        await self.send(text_data=json.dumps({
            'type': 'decision_promoted',
            'decision_id': event.get('decision_id'),
            'topic': event.get('topic'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))


# =============================================================================
# Helper functions to broadcast from Celery tasks
# =============================================================================

def broadcast_project_learning_event(project_id, event_type, agent, title, summary, confidence=None):
    """Broadcast a learning event for a project."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'learning_event',
            'event_type': event_type,
            'agent': agent,
            'title': title,
            'summary': summary,
            'confidence': confidence,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_knowledge_transfer(project_id, teacher, student, summary, was_useful=True):
    """Broadcast a knowledge transfer for a project."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'knowledge_transfer',
            'teacher': teacher,
            'student': student,
            'summary': summary,
            'was_useful': was_useful,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_dream(project_id, dream_id, agent, title, content, dream_type, creativity_score):
    """Broadcast a new dream for a project."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'new_dream',
            'dream_id': str(dream_id),
            'agent': agent,
            'title': title,
            'content': content,
            'dream_type': dream_type,
            'creativity_score': creativity_score,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_decision(project_id, decision_id, topic, decision_type, key_insights, is_canonical=False):
    """Broadcast a new boardroom decision for a project."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'new_decision',
            'decision_id': str(decision_id),
            'topic': topic,
            'decision_type': decision_type,
            'key_insights': key_insights,
            'is_canonical': is_canonical,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_decision_promoted(project_id, decision_id, topic):
    """Broadcast that a decision was promoted to canonical."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'decision_promoted',
            'decision_id': str(decision_id),
            'topic': topic,
            'timestamp': timezone.now().isoformat()
        }
    )


# Re-export conversation broadcasts for backward compatibility
def broadcast_project_conversation_started(project_id, conversation_id, topic, participants, conversation_type):
    """Broadcast that a project conversation has started."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'conversation_started',
            'conversation_id': str(conversation_id),
            'project_id': str(project_id),
            'topic': topic,
            'participants': participants,
            'conversation_type': conversation_type,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_typing_indicator(project_id, conversation_id, agent_name, agent_id=None):
    """Broadcast typing indicator for a project conversation."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'typing_indicator',
            'conversation_id': str(conversation_id),
            'agent': agent_name,
            'agent_id': str(agent_id) if agent_id else None,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_conversation_message(project_id, conversation_id, agent_name, agent_id, content, message_type, sequence):
    """Broadcast a new message in a project conversation."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'new_message',
            'conversation_id': str(conversation_id),
            'agent': agent_name,
            'agent_id': str(agent_id) if agent_id else None,
            'content': content,
            'message_type': message_type,
            'sequence': sequence,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_conversation_ended(project_id, conversation_id, conclusion, message_count, quality_score=None):
    """Broadcast that a project conversation has ended."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_intelligence_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'conversation_ended',
            'conversation_id': str(conversation_id),
            'conclusion': conclusion,
            'message_count': message_count,
            'quality_score': quality_score,
            'timestamp': timezone.now().isoformat()
        }
    )
