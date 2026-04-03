"""
Agent Slack WebSocket Consumer
==============================

Session 319: Multi-agent channel communication system.

This creates an internal Slack-like experience where:
- Agents can join topic-based channels
- Multiple agents can collaborate on projects
- @mentions invite specific agents to respond
- Agents use their learned knowledge in responses
- Real-time streaming via WebSocket
"""

import json
import asyncio
import logging
import re
from typing import List, Dict, Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class AgentSlackConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Agent Slack channels.

    Features:
    - Join/leave channels
    - Send messages with @mentions
    - Multiple agents respond to mentions
    - Thread support
    - Presence indicators
    - Knowledge-aware responses
    """

    async def connect(self):
        """Accept connection and set up channel groups."""
        # Get channel_id from URL route (default to 'general')
        self.channel_id = self.scope['url_route']['kwargs'].get('channel_id', 'general')
        self.room_group_name = f'agent_slack_{self.channel_id}'

        # Join the channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Agent Slack WebSocket connected: {self.channel_name} to #{self.channel_id}")

        # Send channel info on connect
        await self.send_channel_info()

        # Session 321: Also send member list and channel list on connect
        await self.send_member_list()
        await self.send_channel_list()

    async def disconnect(self, close_code):
        """Leave channel group on disconnect."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Agent Slack WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming messages from client."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'message':
                # User/agent is sending a message
                await self.handle_message(data)

            elif message_type == 'join_channel':
                # Join a different channel
                channel_id = data.get('channel_id')
                if channel_id:
                    await self.switch_channel(channel_id)

            elif message_type == 'get_channels':
                # Get list of available channels
                await self.send_channel_list()

            elif message_type == 'get_members':
                # Get channel members
                await self.send_member_list()

            elif message_type == 'get_history':
                # Get message history
                limit = data.get('limit', 50)
                await self.send_message_history(limit)

            elif message_type == 'create_channel':
                # Create a new channel
                await self.create_channel(data)

            elif message_type == 'add_reaction':
                # Add reaction to a message
                await self.handle_reaction(data)

            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))

        except Exception as e:
            logger.error(f"Error in Agent Slack receive: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_channel_info(self):
        """Send current channel info to the client."""
        channel_info = await self.get_channel_info()
        recent_messages = await self.get_recent_messages(50)

        await self.send(text_data=json.dumps({
            'type': 'channel_info',
            'channel': channel_info,
            'messages': recent_messages,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_channel_list(self):
        """Send list of all available channels."""
        channels = await self.get_all_channels()
        await self.send(text_data=json.dumps({
            'type': 'channel_list',
            'channels': channels,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_member_list(self):
        """Send list of channel members."""
        members = await self.get_channel_members()
        await self.send(text_data=json.dumps({
            'type': 'member_list',
            'members': members,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_message_history(self, limit: int):
        """Send message history for current channel."""
        messages = await self.get_recent_messages(limit)
        await self.send(text_data=json.dumps({
            'type': 'message_history',
            'messages': messages,
            'timestamp': timezone.now().isoformat()
        }))

    async def handle_message(self, data: Dict):
        """
        Handle a new message in the channel.

        Parses @mentions and triggers agent responses.
        """
        content = data.get('content', '')
        sender_type = data.get('sender_type', 'user')  # 'user' or 'agent'
        sender_id = data.get('sender_id')
        sender_name = data.get('sender_name', 'User')
        thread_parent_id = data.get('thread_parent_id')
        message_type = data.get('message_type', 'message')

        # Save message to database
        message_data = await self.save_message(
            content=content,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            thread_parent_id=thread_parent_id,
            message_type=message_type
        )

        # Broadcast to all channel members
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'channel_message',
                'message': message_data
            }
        )

        # Parse @mentions and trigger agent responses
        mentioned_agents = self.parse_mentions(content)
        if mentioned_agents:
            # Queue agent responses
            asyncio.create_task(
                self.trigger_agent_responses(mentioned_agents, message_data)
            )

    async def trigger_agent_responses(self, agent_names: List[str], trigger_message: Dict):
        """
        Have mentioned agents respond to the message.

        Each agent:
        1. Shows typing indicator
        2. Fetches their knowledge
        3. Generates a contextual response
        4. Posts to the channel
        """
        for agent_name in agent_names:
            try:
                # Send typing indicator
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'agent_name': agent_name
                    }
                )

                # Small delay for natural feel
                await asyncio.sleep(0.5)

                # Generate and send agent response
                response = await self.generate_agent_response(agent_name, trigger_message)

                if response:
                    # Save and broadcast the response
                    message_data = await self.save_message(
                        content=response['content'],
                        sender_type='agent',
                        sender_id=response['agent_id'],
                        sender_name=agent_name,
                        thread_parent_id=trigger_message.get('id'),
                        message_type=response.get('message_type', 'message')
                    )

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'channel_message',
                            'message': message_data
                        }
                    )

            except Exception as e:
                logger.error(f"Error triggering response from {agent_name}: {e}", exc_info=True)

    def parse_mentions(self, content: str) -> List[str]:
        """Parse @agent mentions from message content."""
        mentions = re.findall(r'@(\w+)', content)
        return list(set(mentions))  # Unique mentions

    async def switch_channel(self, new_channel_id: str):
        """Switch to a different channel."""
        # Leave current channel group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Update channel
        self.channel_id = new_channel_id
        self.room_group_name = f'agent_slack_{new_channel_id}'

        # Join new channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Send new channel info
        await self.send_channel_info()

    async def handle_reaction(self, data: Dict):
        """Handle adding/removing a reaction."""
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        agent_name = data.get('agent_name')
        action = data.get('action', 'add')  # 'add' or 'remove'

        result = await self.update_reaction(message_id, emoji, agent_name, action)

        if result:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'reaction_update',
                    'message_id': message_id,
                    'reactions': result
                }
            )

    async def create_channel(self, data: Dict):
        """Create a new channel."""
        name = data.get('name')
        description = data.get('description', '')
        channel_type = data.get('channel_type', 'topic')
        creator_agent_name = data.get('creator_agent')

        result = await self.create_new_channel(
            name=name,
            description=description,
            channel_type=channel_type,
            creator_agent_name=creator_agent_name
        )

        await self.send(text_data=json.dumps({
            'type': 'channel_created',
            'channel': result,
            'timestamp': timezone.now().isoformat()
        }))

    # =========================================================================
    # Group message handlers
    # =========================================================================

    async def channel_message(self, event):
        """Handle a new message broadcast."""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'timestamp': timezone.now().isoformat()
        }))

    async def typing_indicator(self, event):
        """Handle typing indicator."""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'agent_name': event['agent_name'],
            'timestamp': timezone.now().isoformat()
        }))

    async def reaction_update(self, event):
        """Handle reaction update."""
        await self.send(text_data=json.dumps({
            'type': 'reaction_update',
            'message_id': event['message_id'],
            'reactions': event['reactions'],
            'timestamp': timezone.now().isoformat()
        }))

    async def member_joined(self, event):
        """Handle member join notification."""
        await self.send(text_data=json.dumps({
            'type': 'member_joined',
            'agent': event['agent'],
            'timestamp': timezone.now().isoformat()
        }))

    async def member_left(self, event):
        """Handle member leave notification."""
        await self.send(text_data=json.dumps({
            'type': 'member_left',
            'agent_name': event['agent_name'],
            'timestamp': timezone.now().isoformat()
        }))

    # =========================================================================
    # Database operations
    # =========================================================================

    @database_sync_to_async
    def get_channel_info(self) -> Dict:
        """Get current channel information."""
        from core.models import AgentChannel

        try:
            channel = AgentChannel.objects.get(name=self.channel_id)
            return {
                'id': str(channel.id),
                'name': channel.name,
                'description': channel.description,
                'channel_type': channel.channel_type,
                'topic': channel.topic,
                'message_count': channel.message_count,
                'member_count': channel.member_count,
                'is_archived': channel.is_archived,
                'created_at': channel.created_at.isoformat()
            }
        except AgentChannel.DoesNotExist:
            # Create the channel if it doesn't exist (e.g., 'general')
            channel = AgentChannel.objects.create(
                name=self.channel_id,
                description=f"#{self.channel_id} channel",
                channel_type='topic'
            )
            return {
                'id': str(channel.id),
                'name': channel.name,
                'description': channel.description,
                'channel_type': channel.channel_type,
                'topic': '',
                'message_count': 0,
                'member_count': 0,
                'is_archived': False,
                'created_at': channel.created_at.isoformat()
            }

    @database_sync_to_async
    def get_all_channels(self) -> List[Dict]:
        """Get list of all channels."""
        from core.models import AgentChannel

        channels = AgentChannel.objects.filter(is_archived=False).order_by('-last_activity', '-created_at')[:50]

        return [{
            'id': str(ch.id),
            'name': ch.name,
            'description': ch.description,
            'channel_type': ch.channel_type,
            'message_count': ch.message_count,
            'member_count': ch.member_count,
            'last_activity': ch.last_activity.isoformat() if ch.last_activity else None
        } for ch in channels]

    @database_sync_to_async
    def get_channel_members(self) -> List[Dict]:
        """Get channel members."""
        from core.models import AgentChannel, ChannelMembership

        try:
            channel = AgentChannel.objects.get(name=self.channel_id)
            memberships = ChannelMembership.objects.filter(
                channel=channel,
                is_active=True
            ).select_related('agent')

            return [{
                'id': str(m.agent.id),
                'name': m.agent.name,
                'type': m.agent.agent_type,
                'role': m.role,
                'presence': m.presence_status,
                'last_posted': m.last_posted_at.isoformat() if m.last_posted_at else None
            } for m in memberships]
        except AgentChannel.DoesNotExist:
            return []

    @database_sync_to_async
    def get_recent_messages(self, limit: int) -> List[Dict]:
        """Get recent messages for the channel."""
        from core.models import AgentChannel, ChannelMessage

        try:
            channel = AgentChannel.objects.get(name=self.channel_id)
            messages = ChannelMessage.objects.filter(
                channel=channel,
                thread_parent__isnull=True  # Only top-level messages
            ).select_related('agent').prefetch_related('mentioned_agents').order_by('-created_at')[:limit]

            result = []
            for msg in reversed(messages):  # Oldest first
                result.append({
                    'id': str(msg.id),
                    'agent_id': str(msg.agent.id) if msg.agent else None,
                    'agent_name': msg.agent.name if msg.agent else 'System',
                    'content': msg.content,
                    'message_type': msg.message_type,
                    'reactions': msg.reactions,
                    'reply_count': msg.reply_count,
                    'is_pinned': msg.is_pinned,
                    'mentions': [a.name for a in msg.mentioned_agents.all()],
                    'created_at': msg.created_at.isoformat()
                })
            return result
        except AgentChannel.DoesNotExist:
            return []

    @database_sync_to_async
    def save_message(
        self,
        content: str,
        sender_type: str,
        sender_id: Optional[str],
        sender_name: str,
        thread_parent_id: Optional[str],
        message_type: str
    ) -> Dict:
        """Save a message to the database."""
        from core.models import Agent, AgentChannel, ChannelMessage, ChannelMembership

        # Get or create channel
        channel, _ = AgentChannel.objects.get_or_create(
            name=self.channel_id,
            defaults={
                'description': f"#{self.channel_id} channel",
                'channel_type': 'topic'
            }
        )

        # Get agent if this is an agent message
        agent = None
        if sender_type == 'agent':
            if sender_id:
                agent = Agent.objects.filter(id=sender_id).first()
            if not agent:
                agent = Agent.objects.filter(name=sender_name).first()

        if not agent and sender_type == 'agent':
            # Create a placeholder agent for system messages
            agent = Agent.objects.filter(name='SystemAgent').first()
            if not agent:
                agent = Agent.objects.create(
                    name='SystemAgent',
                    agent_type='system',
                    specialization='System messages and notifications'
                )

        # For user messages, we use a special User agent
        if sender_type == 'user' and not agent:
            agent = Agent.objects.filter(name='UserProxy').first()
            if not agent:
                agent = Agent.objects.create(
                    name='UserProxy',
                    agent_type='proxy',
                    specialization='Represents human users in agent channels'
                )

        # Get thread parent if specified
        thread_parent = None
        if thread_parent_id:
            thread_parent = ChannelMessage.objects.filter(id=thread_parent_id).first()

        # Create the message
        message = ChannelMessage.objects.create(
            channel=channel,
            agent=agent,
            content=content,
            message_type=message_type,
            thread_parent=thread_parent
        )

        # Parse and link mentions
        message.parse_mentions()

        # Ensure agent is a channel member
        if agent:
            ChannelMembership.objects.get_or_create(
                channel=channel,
                agent=agent,
                defaults={'role': 'member'}
            )

        return {
            'id': str(message.id),
            'agent_id': str(agent.id) if agent else None,
            'agent_name': agent.name if agent else sender_name,
            'content': content,
            'message_type': message_type,
            'reactions': {},
            'reply_count': 0,
            'is_pinned': False,
            'mentions': [a.name for a in message.mentioned_agents.all()],
            'created_at': message.created_at.isoformat()
        }

    @database_sync_to_async
    def generate_agent_response(self, agent_name: str, trigger_message: Dict) -> Optional[Dict]:
        """
        Generate a knowledge-aware response from an agent.

        Uses the agent's learned knowledge and memories to respond.
        """
        from core.models import Agent, AgentKnowledgeSource, AgentMemory
        from openai import OpenAI
        import os

        # Get the agent
        agent = Agent.objects.filter(name=agent_name).first()
        if not agent:
            logger.warning(f"Agent {agent_name} not found")
            return None

        # Get agent's knowledge
        knowledge_context = []

        # Recent knowledge sources
        sources = AgentKnowledgeSource.objects.filter(
            agent=agent
        ).order_by('-last_updated_at')[:5]

        for source in sources:
            if source.summary:
                knowledge_context.append(f"[Knowledge] {source.title}: {source.summary[:200]}")

        # Recent memories
        memories = AgentMemory.objects.filter(
            agent=agent
        ).order_by('-created_at')[:5]

        for memory in memories:
            if memory.content:
                knowledge_context.append(f"[Memory] {memory.memory_type}: {memory.content[:200]}")

        # Build the prompt
        knowledge_str = "\n".join(knowledge_context) if knowledge_context else "No specific knowledge loaded."

        system_prompt = f"""You are {agent_name}, a specialized AI agent with the following profile:
- Type: {agent.agent_type}
- Specialization: {agent.specialization or 'General AI assistance'}

Your Recent Knowledge and Memories:
{knowledge_str}

You are in an Agent Slack channel responding to a mention. Be:
- Concise (2-3 sentences max)
- Use your specific knowledge when relevant
- Be collaborative and helpful
- Reference specific insights you've learned

IMPORTANT: Respond naturally to the message. Don't just repeat statistics or generic information.
Draw from your actual learned knowledge to provide valuable insights."""

        user_prompt = f"""Someone mentioned you in this message:

"{trigger_message.get('content', '')}"

Posted by: {trigger_message.get('agent_name', 'User')}

Respond helpfully and concisely, drawing on your specialized knowledge."""

        try:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            response = client.responses.create(
                model="gpt-5.2",
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_output_tokens=500
            )

            content = response.output_text.strip() if response.output_text else None

            if content:
                return {
                    'agent_id': str(agent.id),
                    'content': content,
                    'message_type': 'message'
                }

        except Exception as e:
            logger.error(f"Error generating response for {agent_name}: {e}", exc_info=True)

        return None

    @database_sync_to_async
    def update_reaction(self, message_id: str, emoji: str, agent_name: str, action: str) -> Optional[Dict]:
        """Update reactions on a message."""
        from core.models import Agent, ChannelMessage

        try:
            message = ChannelMessage.objects.get(id=message_id)
            agent = Agent.objects.filter(name=agent_name).first()

            if not agent:
                return None

            if action == 'add':
                message.add_reaction(agent, emoji)
            else:
                message.remove_reaction(agent, emoji)

            return message.reactions

        except ChannelMessage.DoesNotExist:
            return None

    @database_sync_to_async
    def create_new_channel(
        self,
        name: str,
        description: str,
        channel_type: str,
        creator_agent_name: Optional[str]
    ) -> Dict:
        """Create a new channel."""
        from core.models import Agent, AgentChannel

        creator = None
        if creator_agent_name:
            creator = Agent.objects.filter(name=creator_agent_name).first()

        channel = AgentChannel.objects.create(
            name=name,
            description=description,
            channel_type=channel_type,
            created_by=creator
        )

        # Add creator as owner
        if creator:
            channel.add_member(creator, role='owner')

        return {
            'id': str(channel.id),
            'name': channel.name,
            'description': channel.description,
            'channel_type': channel.channel_type,
            'created_at': channel.created_at.isoformat()
        }


# =============================================================================
# Helper functions for external use
# =============================================================================

def broadcast_to_channel(channel_name: str, message_type: str, data: Dict):
    """Broadcast a message to all clients in a channel."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'agent_slack_{channel_name}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'channel_message',
            'message': {
                'type': message_type,
                **data,
                'timestamp': timezone.now().isoformat()
            }
        }
    )


def notify_agent_mention(channel_name: str, agent_name: str, message_content: str):
    """Notify when an agent is mentioned in a channel."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'agent_slack_{channel_name}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'typing_indicator',
            'agent_name': agent_name
        }
    )
