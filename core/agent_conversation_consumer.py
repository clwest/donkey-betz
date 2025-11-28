"""
Agent Conversation WebSocket Consumer
=====================================

Session 244: Real-time streaming of agent-to-agent conversations.

Agents chat in real-time via WebSocket - messages stream as they're generated
by GPT-4o-mini. This creates a "Slack for AI agents" experience.
"""

import json
import asyncio
import logging
import random
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
        """Generate a conversation and broadcast each message."""
        import openai
        import os
        from core.models import (
            Agent, AgentConversation, ConversationMessage,
            AgentKnowledgeSource, AgentLearningConnection
        )

        # Get agents with knowledge
        agents_list = list(Agent.objects.filter(
            is_active=True,
            knowledge_sources__isnull=False
        ).distinct()[:20])

        if len(agents_list) < 2:
            return {'status': 'error', 'reason': 'Not enough agents with knowledge'}

        # Pick two random agents
        initiator = random.choice(agents_list)
        possible_responders = [a for a in agents_list if a.id != initiator.id]
        responder = random.choice(possible_responders)

        # Pick a random conversation type for variety
        conversation_types = [
            'knowledge_sharing',
            'brainstorm',
            'consultation',
            'synthesis',
        ]
        conv_type = random.choice(conversation_types)

        # Get topic from knowledge if not provided - make it cleaner
        if not topic:
            knowledge = AgentKnowledgeSource.objects.filter(
                agent=initiator
            ).order_by('-last_updated_at').first()

            if knowledge:
                # Clean up the title - remove brackets and prefixes
                clean_title = knowledge.title
                # Remove common prefixes like "[Synthesis]", "[Analysis]", etc.
                import re
                clean_title = re.sub(r'^\[.*?\]\s*', '', clean_title)
                # Truncate if too long
                if len(clean_title) > 60:
                    clean_title = clean_title[:57] + "..."
                topic = clean_title
            else:
                # Random interesting topics if no knowledge found
                topics = [
                    "The Future of AI Creativity",
                    "Creative Tools & Innovation",
                    "AI-Human Collaboration",
                    "Emerging Tech Trends",
                    "Digital Content Creation",
                ]
                topic = random.choice(topics)

        # Create conversation
        conversation = AgentConversation.objects.create(
            topic=topic,
            conversation_type=conv_type,
            trigger_type='user_triggered',
            initiator=initiator,
            status='active'
        )
        conversation.participants.add(initiator, responder)

        # Initialize OpenAI
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        messages_generated = []
        conversation_context = []

        # Generate messages back and forth
        for i in range(6):  # 6 messages total
            current_agent = initiator if i % 2 == 0 else responder
            other_agent = responder if i % 2 == 0 else initiator

            # Build prompt
            if i == 0:
                prompt = f"""You are {current_agent.name}, an AI agent specializing in {current_agent.specialization or 'AI'}.

Start a thoughtful conversation with {other_agent.name} about: {topic}

Ask an insightful question or share an interesting observation. Keep it concise (2-3 sentences).

IMPORTANT: Do NOT prefix your response with your name. Just write your message directly."""
            else:
                context_str = "\n".join([f"{m['agent']}: {m['content']}" for m in conversation_context[-4:]])
                prompt = f"""You are {current_agent.name}, an AI agent specializing in {current_agent.specialization or 'AI'}.

Conversation so far:
{context_str}

Continue this conversation naturally. Respond to what was said, add your perspective, or ask a follow-up question. Keep it concise (2-3 sentences).

IMPORTANT: Do NOT prefix your response with your name. Just write your message directly."""

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.8
                )

                content = response.choices[0].message.content.strip()

                # Determine message type
                if '?' in content:
                    msg_type = 'question'
                elif i == 5:
                    msg_type = 'conclusion'
                elif any(word in content.lower() for word in ['agree', 'exactly', 'right']):
                    msg_type = 'agreement'
                elif any(word in content.lower() for word in ['however', 'but', 'disagree']):
                    msg_type = 'disagreement'
                else:
                    msg_type = 'statement'

                # Save message
                msg = ConversationMessage.objects.create(
                    conversation=conversation,
                    agent=current_agent,
                    content=content,
                    message_type=msg_type,
                    sequence_number=i + 1
                )

                msg_data = {
                    'agent': current_agent.name,
                    'content': content,
                    'type': msg_type,
                    'sequence': i + 1
                }

                messages_generated.append(msg_data)
                conversation_context.append(msg_data)

            except Exception as e:
                logger.error(f"Error generating message {i}: {e}")
                break

        # Update conversation
        conversation.message_count = len(messages_generated)
        conversation.status = 'concluded'

        # Generate conclusion
        if messages_generated:
            try:
                conclusion_prompt = f"""Summarize this agent conversation in one sentence:

{chr(10).join([f"{m['agent']}: {m['content']}" for m in messages_generated])}

Summary:"""

                conclusion_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": conclusion_prompt}],
                    max_tokens=100,
                    temperature=0.5
                )
                conversation.conclusion = conclusion_response.choices[0].message.content.strip()
            except:
                pass

        conversation.ended_at = timezone.now()
        conversation.save()

        return {
            'status': 'success',
            'conversation_id': str(conversation.id),
            'topic': topic,
            'participants': [initiator.name, responder.name],
            'messages': messages_generated,
            'conclusion': conversation.conclusion
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
