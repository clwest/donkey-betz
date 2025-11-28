"""
Agent Conversation WebSocket Consumer
=====================================

Session 244: Real-time streaming of agent-to-agent conversations.
Session 261: Upgraded to use ConversationOrchestrator for outcome-driven conversations.

Agents chat in real-time via WebSocket - messages stream as they're generated
by GPT-4o-mini. This creates a "Slack for AI agents" experience.

Session 261 Improvements:
- Constructive tension (no empty agreement)
- Platform grounding (metrics and systems referenced)
- Structured outputs (DecisionSummary with insights and features)
- Role-specific prompts for each agent type
"""

import json
import asyncio
import logging
import random
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class AgentConversationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time agent conversations.

    Features:
    - Stream agent messages as they're generated
    - Multiple concurrent conversations
    - User can watch agents think and respond
    - Typing indicators between messages
    """

    async def connect(self):
        """Accept connection and join conversation broadcast group."""
        self.room_group_name = 'agent_conversations'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Agent Conversation WebSocket connected: {self.channel_name}")

        # Send recent conversations on connect
        await self.send_recent_conversations()

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'Connected to Agent Conversations stream',
            'timestamp': timezone.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """Leave group on disconnect."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Agent Conversation WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming messages from client."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'start_conversation':
                # User requested a new conversation
                topic = data.get('topic', 'general discussion')
                await self.start_live_conversation(topic)

            elif message_type == 'get_recent':
                # User wants recent conversations
                await self.send_recent_conversations()

            elif message_type == 'ping':
                # Keep-alive
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

    async def send_recent_conversations(self):
        """Send recent conversations to the client."""
        conversations = await self.get_recent_conversations()
        await self.send(text_data=json.dumps({
            'type': 'recent_conversations',
            'conversations': conversations,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_recent_conversations(self):
        """Fetch recent conversations from database."""
        from core.models import AgentConversation

        conversations = AgentConversation.objects.select_related(
            'initiator'
        ).prefetch_related(
            'participants', 'messages__agent'
        ).order_by('-started_at')[:10]

        result = []
        for conv in conversations:
            messages = []
            for msg in conv.messages.all()[:10]:
                messages.append({
                    'agent': msg.agent.name,
                    'content': msg.content,
                    'type': msg.message_type,
                    'sequence': msg.sequence_number,
                    'timestamp': msg.created_at.isoformat()
                })

            result.append({
                'id': str(conv.id),
                'topic': conv.topic,
                'type': conv.conversation_type,
                'status': conv.status,
                'initiator': conv.initiator.name,
                'participants': [p.name for p in conv.participants.all()],
                'message_count': conv.message_count,
                'conclusion': conv.conclusion,
                'started_at': conv.started_at.isoformat(),
                'messages': messages
            })

        return result

    async def start_live_conversation(self, topic=None):
        """Start a new live conversation and stream it."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_starting',
            'message': 'Starting new agent conversation...',
            'timestamp': timezone.now().isoformat()
        }))

        # Run the conversation generator
        try:
            result = await self.generate_live_conversation(topic)
            await self.send(text_data=json.dumps({
                'type': 'conversation_complete',
                'result': result,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error generating conversation: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Conversation generation failed: {str(e)}'
            }))

    @database_sync_to_async
    def generate_live_conversation(self, topic=None):
        """
        Generate a conversation using the Session 261 ConversationOrchestrator.

        This upgraded version ensures:
        - Constructive tension (no empty agreement)
        - Platform grounding (metrics and systems referenced)
        - Structured outputs (DecisionSummary with insights and features)
        """
        from core.models import (
            Agent, AgentConversation, ConversationMessage,
            AgentKnowledgeSource
        )
        from core.conversation_orchestrator import ConversationOrchestrator

        # Get agents with knowledge
        agents_list = list(Agent.objects.filter(
            is_active=True,
            knowledge_sources__isnull=False
        ).distinct()[:20])

        if len(agents_list) < 2:
            # Fallback to any active agents
            agents_list = list(Agent.objects.filter(is_active=True)[:20])
            if len(agents_list) < 2:
                return {'status': 'error', 'reason': 'Not enough agents available'}

        # Prefer strategic agent pairings for better conversations
        # Priority 1: ContentStrategyAgent + ResearchAgent (the recommended pair)
        content_agents = [a for a in agents_list if 'Content' in a.name or 'Strategy' in a.name]
        research_agents = [a for a in agents_list if 'Research' in a.name]

        # Priority 2: CreativeDirector + any analytical agent
        creative_agents = [a for a in agents_list if 'Creative' in a.name or 'Director' in a.name]
        analytical_agents = [a for a in agents_list if any(x in a.name for x in ['SEO', 'Trend', 'Analysis', 'Research'])]

        if content_agents and research_agents:
            initiator = random.choice(content_agents)
            responder = random.choice(research_agents)
            logger.info("Using preferred pairing: ContentStrategy + Research")
        elif creative_agents and analytical_agents:
            initiator = random.choice(creative_agents)
            responder = random.choice(analytical_agents)
            logger.info("Using secondary pairing: Creative + Analytical")
        else:
            # Random pairing as fallback
            initiator = random.choice(agents_list)
            possible_responders = [a for a in agents_list if a.id != initiator.id]
            responder = random.choice(possible_responders)
            logger.info(f"Using random pairing: {initiator.name} + {responder.name}")

        # Pick conversation type - weighted toward strategic types
        conversation_types = [
            ('brainstorm', 3),      # Strategic brainstorming
            ('analysis', 2),        # Deep analysis
            ('planning', 2),        # Implementation planning
            ('critique', 1),        # Constructive critique
            ('synthesis', 1),       # Knowledge synthesis
            ('consultation', 1),    # Expert consultation
        ]
        conv_type = random.choices(
            [t[0] for t in conversation_types],
            weights=[t[1] for t in conversation_types]
        )[0]

        # Get topic from knowledge if not provided
        if not topic:
            knowledge = AgentKnowledgeSource.objects.filter(
                agent=initiator
            ).order_by('-last_updated_at').first()

            if knowledge:
                clean_title = knowledge.title
                clean_title = re.sub(r'^\[.*?\]\s*', '', clean_title)
                if len(clean_title) > 60:
                    clean_title = clean_title[:57] + "..."
                topic = clean_title
            else:
                # Strategic topics that encourage good conversations
                topics = [
                    "Optimizing Content Engagement Through Data-Driven Insights",
                    "Building a Pacing Score System for Long-Form Content",
                    "Measuring and Improving User Retention Metrics",
                    "Creating an Authority vs Virality Framework",
                    "Designing Dashboard Widgets for Creator Analytics",
                    "Leveraging Spider Data for Content Recommendations",
                    "Building Embedding-Based Content Quality Scoring",
                    "A/B Testing Strategies for Creative Content",
                ]
                topic = random.choice(topics)

        # Create conversation record
        conversation = AgentConversation.objects.create(
            topic=topic,
            conversation_type=conv_type,
            trigger_type='user_triggered',
            initiator=initiator,
            status='active'
        )
        conversation.participants.add(initiator, responder)

        # Use the new ConversationOrchestrator (Session 261)
        try:
            orchestrator = ConversationOrchestrator()

            result = orchestrator.generate_conversation(
                agent1={
                    'name': initiator.name,
                    'type': initiator.agent_type,
                    'specialization': initiator.specialization or 'AI assistance'
                },
                agent2={
                    'name': responder.name,
                    'type': responder.agent_type,
                    'specialization': responder.specialization or 'AI assistance'
                },
                topic=topic,
                conversation_type=conv_type,
                num_turns=6,
                max_retries=2
            )

            # Save messages to database
            for msg_data in result['messages']:
                agent = initiator if msg_data['agent'] == initiator.name else responder
                ConversationMessage.objects.create(
                    conversation=conversation,
                    agent=agent,
                    content=msg_data['content'],
                    message_type=msg_data['type'],
                    sequence_number=msg_data['sequence']
                )

            # Update conversation
            conversation.message_count = len(result['messages'])
            conversation.status = 'concluded'

            # Build conclusion from decision summary
            decision_summary = result.get('decision_summary')
            if decision_summary:
                conclusion_parts = []
                if decision_summary.get('proposed_feature', {}).get('name'):
                    conclusion_parts.append(f"Proposed: {decision_summary['proposed_feature']['name']}")
                if decision_summary.get('insights'):
                    conclusion_parts.append(f"{len(decision_summary['insights'])} key insights identified")
                if decision_summary.get('next_steps'):
                    conclusion_parts.append(f"{len(decision_summary['next_steps'])} action items defined")
                conversation.conclusion = ". ".join(conclusion_parts) if conclusion_parts else "Strategic discussion completed with actionable outcomes."
            else:
                conversation.conclusion = "Strategic discussion completed."

            conversation.ended_at = timezone.now()
            conversation.save()

            # Return enhanced result
            return {
                'status': 'success',
                'conversation_id': str(conversation.id),
                'topic': topic,
                'conversation_type': conv_type,
                'participants': [initiator.name, responder.name],
                'messages': result['messages'],
                'decision_summary': decision_summary,
                'validation': result.get('validation', {}),
                'quality_score': result.get('validation', {}).get('score', 0),
                'conclusion': conversation.conclusion
            }

        except Exception as e:
            logger.error(f"ConversationOrchestrator failed: {e}", exc_info=True)
            conversation.status = 'failed'
            conversation.conclusion = f"Conversation generation failed: {str(e)}"
            conversation.save()
            return {
                'status': 'error',
                'conversation_id': str(conversation.id),
                'reason': str(e)
            }

    # Group message handlers
    async def conversation_message(self, event):
        """Handle a new conversation message from the group."""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'conversation_id': event.get('conversation_id'),
            'agent': event.get('agent'),
            'content': event.get('content'),
            'message_type': event.get('message_type'),
            'sequence': event.get('sequence'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def conversation_started(self, event):
        """Handle conversation started notification."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_started',
            'conversation_id': event.get('conversation_id'),
            'topic': event.get('topic'),
            'participants': event.get('participants'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def conversation_ended(self, event):
        """Handle conversation ended notification."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_ended',
            'conversation_id': event.get('conversation_id'),
            'conclusion': event.get('conclusion'),
            'message_count': event.get('message_count'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def typing_indicator(self, event):
        """Handle typing indicator."""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'conversation_id': event.get('conversation_id'),
            'agent': event.get('agent'),
            'timestamp': timezone.now().isoformat()
        }))


# Helper function to broadcast messages from tasks
def broadcast_conversation_message(conversation_id, agent_name, content, message_type, sequence):
    """Broadcast a conversation message to all connected clients."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'agent_conversations',
        {
            'type': 'conversation_message',
            'conversation_id': str(conversation_id),
            'agent': agent_name,
            'content': content,
            'message_type': message_type,
            'sequence': sequence,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_conversation_started(conversation_id, topic, participants):
    """Broadcast that a conversation has started."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'agent_conversations',
        {
            'type': 'conversation_started',
            'conversation_id': str(conversation_id),
            'topic': topic,
            'participants': participants,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_typing_indicator(conversation_id, agent_name):
    """Broadcast typing indicator."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'agent_conversations',
        {
            'type': 'typing_indicator',
            'conversation_id': str(conversation_id),
            'agent': agent_name,
            'timestamp': timezone.now().isoformat()
        }
    )
