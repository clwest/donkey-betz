"""
WebSocket consumers for real-time communication.
Migrated from DBAO tools-manifest WebSocket capabilities and ai-content-studio.
"""

import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class SafeWebSocketMixin:
    """Mixin for safe WebSocket send operations"""
    
    async def safe_send(self, data):
        """Safely send data, handling closed connections"""
        try:
            await self.send(text_data=json.dumps(data))
        except Exception:
            # Connection closed, ignore
            pass
class AgentProgressConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real-time agent execution progress and status updates.
    Migrated from DBAO tools-manifest.
    """
    
    async def connect(self):
        self.instance_id = self.scope['url_route']['kwargs'].get('instance_id', 'all')
        self.room_group_name = f'agent_progress_{self.instance_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection established message
        await self.safe_send({
            'type': 'connection_established',
            'data': {
                'message': 'Connected to agent progress updates',
                'instance_id': self.instance_id,
                'timestamp': datetime.now().isoformat()
            },
            'channel_name': self.channel_name
        })
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')
            
            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            elif message_type == 'subscribe_agent':
                instance_id = text_data_json.get('instance_id')
                # Handle agent subscription
                await self.safe_send({
                    'type': 'subscribed',
                    'data': {
                        'instance_id': instance_id,
                        'status': 'subscribed'
                    }
                })
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })
    
    async def agent_progress(self, event):
        """Send agent progress update to WebSocket"""
        await self.safe_send({
            'type': 'agent_progress',
            'data': event['data']
        })
    
    async def agent_completed(self, event):
        """Send agent completion notification"""
        await self.safe_send({
            'type': 'agent_completed',
            'data': event['data']
        })
    
    async def agent_failed(self, event):
        """Send agent failure notification"""
        await self.safe_send({
            'type': 'agent_failed',
            'data': event['data']
        })


class DashboardConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real-time dashboard metrics and system-wide updates.
    Migrated from DBAO tools-manifest.
    """
    
    async def connect(self):
        self.room_group_name = 'dashboard_updates'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard data
        await self.safe_send({
            'type': 'dashboard_data',
            'data': {
                'stats': {
                    'active_agents': 5,
                    'total_requests': 1247,
                    'success_rate': 94.2,
                    'current_cost': 45.67
                },
                'recent_activity': [
                    'Agent execution completed: Business Strategy Analysis',
                    'New odds calculation request',
                    'Content generation started'
                ],
                'timestamp': datetime.now().isoformat()
            }
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'refresh_dashboard')
        
        if message_type == 'refresh_dashboard':
            # Send updated dashboard data
            await self.safe_send({
                'type': 'dashboard_update',
                'data': {
                    'stats': {
                        'active_agents': 3,
                        'total_requests': 1253,
                        'success_rate': 94.4,
                        'current_cost': 46.12
                    },
                    'timestamp': datetime.now().isoformat()
                }
            })
    
    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.safe_send({
            'type': 'dashboard_update',
            'data': event['data']
        })
    
    async def system_alert(self, event):
        """Send system alert to WebSocket"""
        await self.safe_send({
            'type': 'system_alert',
            'data': event['data']
        })


class LiveSportsConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real-time sports data and betting opportunities.
    """
    
    async def connect(self):
        self.room_group_name = 'live_sports'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'subscribe')
        
        if message_type == 'subscribe_sport':
            sport = text_data_json.get('sport', 'all')
            await self.safe_send({
                'type': 'subscribed',
                'sport': sport,
                'timestamp': datetime.now().isoformat()
            })
    
    async def live_odds_update(self, event):
        """Send live odds update"""
        await self.safe_send({
            'type': 'live_odds_update',
            'data': event['data']
        })
    
    async def betting_opportunity(self, event):
        """Send new betting opportunity"""
        await self.safe_send({
            'type': 'betting_opportunity',
            'data': event['data']
        })


class ArbitrageConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real-time arbitrage opportunity notifications.
    """
    
    async def connect(self):
        self.room_group_name = 'arbitrage_opportunities'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def arbitrage_opportunity(self, event):
        """Send arbitrage opportunity alert"""
        await self.safe_send({
            'type': 'arbitrage_opportunity',
            'data': event['data']
        })


class AssistantChatConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    AI Assistant chat WebSocket for real-time conversation.
    Migrated from ai-content-studio.
    """
    
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        
        # Allow connection but track authentication status
        self.is_authenticated = not isinstance(self.user, AnonymousUser)
            
        # Use a generic room for anonymous users
        user_id = self.user.id if self.is_authenticated else 'anonymous'
        self.room_group_name = f'assistant_chat_{user_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send authentication status
        await self.safe_send({
            'type': 'connection_established',
            'data': {
                'authenticated': self.is_authenticated,
                'user': self.user.username if self.is_authenticated else 'anonymous',
                'timestamp': datetime.now().isoformat()
            }
        })
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json.get('message', '')
            
            # Echo back for demo (in real implementation, this would process with AI)
            await self.safe_send({
                'type': 'assistant_response',
                'data': {
                    'message': f'Assistant response to: {message}',
                    'timestamp': datetime.now().isoformat()
                }
            })
    
    async def assistant_response(self, event):
        """Send assistant response to WebSocket"""
        await self.safe_send({
            'type': 'assistant_response',
            'data': event['data']
        })


class OrchestrationConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Multi-agent orchestration updates.
    """
    
    async def connect(self):
        self.orchestration_id = self.scope['url_route']['kwargs']['orchestration_id']
        self.room_group_name = f'orchestration_{self.orchestration_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def orchestration_update(self, event):
        """Send orchestration progress update"""
        await self.safe_send({
            'type': 'orchestration_update',
            'data': event['data']
        })


class NotificationConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    System notifications and alerts.
    """
    
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        self.is_authenticated = not isinstance(self.user, AnonymousUser)
        
        # Use a generic room for anonymous users
        user_id = self.user.id if self.is_authenticated else 'anonymous'
        self.room_group_name = f'notifications_{user_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def notification(self, event):
        """Send notification to user"""
        await self.safe_send({
            'type': 'notification',
            'data': event['data']
        })


class AgentChannelsConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Agent Channels WebSocket Consumer - "Slack for AI Agents"
    
    Provides real-time agent communication viewing, similar to Slack channels
    where users can watch agents think, collaborate, and work together.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = None
        self.channel_group_name = None
        self.user = None
        self.active_channels = set()
        
    async def connect(self):
        """Handle WebSocket connection"""
        # Get channel ID from URL (optional - can join multiple channels)
        self.channel_id = self.scope['url_route']['kwargs'].get('channel_id')
        
        # Get user from scope
        self.user = self.scope.get('user', AnonymousUser())
        
        # Check if user is authenticated
        if not self.user or isinstance(self.user, AnonymousUser):
            # In development, allow anonymous connections
            import os
            if os.getenv('DJANGO_ENV') == 'development':
                # Create a mock user for development
                self.user = type('MockUser', (), {
                    'id': 1,
                    'username': 'dev_user',
                    'is_authenticated': True,
                    'email': 'dev@unified-donkey-betz.com'
                })()
            else:
                await self.close(code=4001)  # Unauthorized
                return
        
        # Accept connection
        await self.accept()
        
        # If specific channel requested, join it
        if self.channel_id:
            await self.join_channel(self.channel_id)
        
        # Send connection success
        await self.safe_send({
            'type': 'connection_established',
            'user_id': str(self.user.id) if hasattr(self.user, 'id') else None,
            'username': getattr(self.user, 'username', 'dev_user'),
            'timestamp': datetime.now().isoformat()
        })
        
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave all active channels
        for channel_id in self.active_channels:
            channel_group_name = f'agent_channel_{channel_id}'
            await self.channel_layer.group_discard(
                channel_group_name,
                self.channel_name
            )
            
            # Notify channel of user leaving (only if user exists)
            if self.user:
                await self.channel_layer.group_send(
                    channel_group_name,
                    {
                        'type': 'user_presence',
                        'user_id': str(self.user.id) if hasattr(self.user, 'id') else None,
                        'username': getattr(self.user, 'username', 'dev_user'),
                        'status': 'offline'
                    }
                )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'unknown')
            
            if message_type == 'join_channel':
                await self.handle_join_channel(text_data_json)
            elif message_type == 'leave_channel':
                await self.handle_leave_channel(text_data_json)
            elif message_type == 'send_message':
                await self.handle_send_message(text_data_json)
            elif message_type == 'subscribe_channel':
                # Handle channel subscription
                channel_id = text_data_json.get('channel_id')
                if channel_id:
                    await self.join_channel(channel_id)
            elif message_type == 'get_channels':
                # Send list of available channels
                await self.handle_get_channels()
            elif message_type == 'get_channel_messages':
                # Send messages for a specific channel
                await self.handle_get_channel_messages(text_data_json)
            elif message_type == 'ping':
                # Handle ping message with pong response
                await self.safe_send({'type': 'pong', 'timestamp': datetime.now().isoformat()})
            else:
                await self.safe_send({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'message': 'Invalid JSON format'
            })
    
    async def handle_join_channel(self, content):
        """Handle joining a channel"""
        channel_id = content.get('channel_id')
        if not channel_id:
            await self.safe_send({
                'type': 'error',
                'message': 'channel_id required'
            })
            return
        
        await self.join_channel(channel_id)
    
    async def join_channel(self, channel_id):
        """Join a specific channel"""
        # Verify channel exists and user has access
        channel = await self.get_channel(channel_id)
        if not channel:
            await self.safe_send({
                'type': 'error',
                'message': f'Channel {channel_id} not found'
            })
            return
        
        # Add to channel group
        channel_group_name = f'agent_channel_{channel_id}'
        await self.channel_layer.group_add(
            channel_group_name,
            self.channel_name
        )
        
        self.active_channels.add(channel_id)
        
        # Send join confirmation
        await self.safe_send({
            'type': 'joined_channel',
            'channel_id': channel_id,
            'channel_name': channel['display_name']
        })
        
        # Notify others of user joining
        await self.channel_layer.group_send(
            channel_group_name,
            {
                'type': 'user_presence',
                'user_id': str(self.user.id) if hasattr(self.user, 'id') else None,
                'username': getattr(self.user, 'username', 'dev_user'),
                'status': 'online',
                'channel_id': channel_id
            }
        )
    
    async def handle_leave_channel(self, content):
        """Handle leaving a channel"""
        channel_id = content.get('channel_id')
        if not channel_id or channel_id not in self.active_channels:
            return
        
        # Remove from channel group
        channel_group_name = f'agent_channel_{channel_id}'
        await self.channel_layer.group_discard(
            channel_group_name,
            self.channel_name
        )
        
        self.active_channels.remove(channel_id)
        
        # Send leave confirmation
        await self.safe_send({
            'type': 'left_channel',
            'channel_id': channel_id
        })
    
    async def handle_send_message(self, content):
        """Handle sending a message to a channel"""
        channel_id = content.get('channel_id')
        message_content = content.get('content')
        message_type = content.get('message_type', 'user_message')
        
        if not channel_id or not message_content:
            await self.safe_send({
                'type': 'error',
                'message': 'channel_id and content required'
            })
            return
        
        # Create message in database
        message = await self.create_user_message(channel_id, message_content, message_type)
        if not message:
            return
        
        # Broadcast to channel
        channel_group_name = f'agent_channel_{channel_id}'
        await self.channel_layer.group_send(
            channel_group_name,
            {
                'type': 'channel_message',
                'message': message
            }
        )
    
    async def handle_get_channels(self):
        """Send list of available channels to client"""
        channels = await self.get_all_channels()
        await self.safe_send({
            'type': 'channels_list',
            'channels': channels
        })
    
    async def handle_get_channel_messages(self, content):
        """Send messages for a specific channel to client"""
        channel_id = content.get('channel_id')
        if not channel_id:
            await self.safe_send({
                'type': 'error',
                'message': 'channel_id required'
            })
            return
        
        messages = await self.get_channel_messages(channel_id)
        await self.safe_send({
            'type': 'channel_messages',
            'channel_id': channel_id,
            'messages': messages
        })
    
    # Channel layer message handlers
    async def channel_message(self, event):
        """Send message to WebSocket"""
        await self.safe_send({
            'type': 'channel_message',
            'data': event['message']
        })
    
    async def agent_message(self, event):
        """Handle agent messages from agents"""
        await self.safe_send({
            'type': 'agent_message',
            'channel_id': event.get('channel_id'),
            'agent_id': event.get('agent_id'),
            'agent_name': event.get('agent_name'),
            'message': event.get('message'),
            'content': event.get('content'),
            'timestamp': event.get('timestamp'),
            'rich_content': event.get('rich_content', {})
        })
    
    async def user_presence(self, event):
        """Send user presence update"""
        await self.safe_send({
            'type': 'user_presence',
            'user_id': event['user_id'],
            'username': event['username'],
            'status': event['status'],
            'channel_id': event.get('channel_id')
        })
    
    # Database helper methods
    @database_sync_to_async
    def get_channel(self, channel_id):
        """Get channel from database"""
        try:
            from agents.models import AgentChannel
            
            # Support both numeric IDs and string names
            if str(channel_id).isdigit():
                channel = AgentChannel.objects.get(id=channel_id, is_active=True)
            else:
                channel = AgentChannel.objects.get(name=channel_id, is_active=True)
            
            return {
                'id': channel.id,
                'name': channel.name,
                'display_name': channel.display_name,
                'description': channel.description,
                'channel_type': channel.channel_type,
                'is_active': channel.is_active,
            }
        except Exception:
            return None
    
    @database_sync_to_async
    def get_all_channels(self):
        """Get all active channels"""
        try:
            from agents.models import AgentChannel, AgentChannelMessage
            
            channels = AgentChannel.objects.filter(is_active=True).order_by('-created_at')
            channel_data = []
            
            for channel in channels:
                # Count messages
                message_count = AgentChannelMessage.objects.filter(channel=channel).count()
                
                # Extract orchestration_id from metadata
                orchestration_id = None
                if channel.metadata and 'orchestration_id' in channel.metadata:
                    orchestration_id = channel.metadata.get('orchestration_id')
                elif channel.orchestration_id:
                    orchestration_id = channel.orchestration_id
                
                channel_data.append({
                    'id': channel.id,
                    'name': channel.name,
                    'display_name': channel.display_name,
                    'description': channel.description,
                    'channel_type': channel.channel_type,
                    'is_active': channel.is_active,
                    'created_at': channel.created_at.isoformat(),
                    'message_count': message_count,
                    'orchestration_id': orchestration_id,
                    'active_agents': len(channel.active_agents) if channel.active_agents else 0
                })
            
            return channel_data
        except Exception as e:
            print(f"Error getting channels: {e}")
            return []
    
    @database_sync_to_async
    def get_channel_messages(self, channel_id):
        """Get messages for a specific channel"""
        try:
            from agents.models import AgentChannel, AgentChannelMessage
            
            # Get the channel
            if str(channel_id).isdigit():
                channel = AgentChannel.objects.get(id=channel_id, is_active=True)
            else:
                channel = AgentChannel.objects.get(name=channel_id, is_active=True)
            
            # Get messages for this channel
            messages = AgentChannelMessage.objects.filter(
                channel=channel
            ).order_by('-timestamp')[:50]  # Get last 50 messages
            
            # Serialize messages
            message_data = []
            for msg in reversed(messages):  # Reverse to show oldest first
                msg_dict = {
                    'id': msg.id,
                    'channel': msg.channel.id,
                    'message_type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'rich_content': msg.rich_content,
                    'reactions': msg.reactions,
                    'thread_id': msg.thread_id
                }
                
                # Add agent info if present
                if msg.agent_instance:
                    msg_dict['agent_instance'] = {
                        'id': msg.agent_instance.id,
                        'template': {
                            'name': msg.agent_instance.template.name if msg.agent_instance.template else 'Unknown Agent'
                        }
                    }
                
                # Add user info if present
                if msg.user:
                    msg_dict['user'] = {
                        'id': msg.user.id,
                        'username': msg.user.username
                    }
                
                message_data.append(msg_dict)
            
            return message_data
            
        except Exception as e:
            print(f"Error getting channel messages: {e}")
            return []
    
    @database_sync_to_async
    def create_user_message(self, channel_id, content, message_type):
        """Create user message in database"""
        try:
            from agents.models import AgentChannel, AgentChannelMessage
            
            # Get channel
            if str(channel_id).isdigit():
                channel = AgentChannel.objects.get(id=channel_id, is_active=True)
            else:
                channel = AgentChannel.objects.get(name=channel_id, is_active=True)
            
            # Create message
            message = AgentChannelMessage.objects.create(
                channel=channel,
                user=self.user if hasattr(self.user, 'id') else None,
                content=content,
                message_type=message_type
            )
            
            return {
                'id': message.id,
                'channel': message.channel.id,
                'message_type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'user': {
                    'id': self.user.id if hasattr(self.user, 'id') else 1,
                    'username': getattr(self.user, 'username', 'dev_user')
                }
            }
            
        except Exception as e:
            print(f"Error creating user message: {e}")
            return None


class TestEchoConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Test echo consumer for WebSocket testing.
    """
    
    async def connect(self):
        await self.accept()
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Test echo WebSocket connected',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data):
        # Echo back the received message
        await self.safe_send({
            'type': 'echo',
            'data': text_data,
            'timestamp': datetime.now().isoformat()
        })


class ContentProcessingConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Content processing WebSocket for real-time updates.
    """
    
    async def connect(self):
        self.room_group_name = 'content_processing'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Connected to content processing updates',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')
            
            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            # Silently handle closed connection errors
            pass
    
    async def processing_update(self, event):
        """Send processing update to WebSocket"""
        try:
            await self.safe_send({
                'type': 'processing_update',
                'data': event['data']
            })
        except Exception as e:
            # Silently handle closed connection errors
            pass


class ContentAnalyticsConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Content analytics WebSocket for real-time metrics.
    """
    
    async def connect(self):
        self.room_group_name = 'content_analytics'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Connected to content analytics',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def analytics_update(self, event):
        """Send analytics update to WebSocket"""
        await self.safe_send({
            'type': 'analytics_update',
            'data': event['data']
        })


class AgentExecutionConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Agent execution WebSocket for real-time execution updates.
    """
    
    async def connect(self):
        self.room_group_name = 'agent_execution'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Connected to agent execution updates',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def execution_update(self, event):
        """Send execution update to WebSocket"""
        await self.safe_send({
            'type': 'execution_update',
            'data': event['data']
        })


class AgentOrchestrationConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Agent orchestration WebSocket for multi-agent coordination.
    """
    
    async def connect(self):
        self.room_group_name = 'agent_orchestration'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Connected to agent orchestration',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def orchestration_update(self, event):
        """Send orchestration update to WebSocket"""
        await self.safe_send({
            'type': 'orchestration_update',
            'data': event['data']
        })


class MythologyConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Mythology/Content Review WebSocket Consumer
    
    Provides real-time notifications for content flagging and review updates.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user')
        
        # Allow anonymous users for now (you can restrict this later)
        # Just log if user is not authenticated
        if not self.user or self.user == AnonymousUser():
            print("Warning: Anonymous user connecting to mythology WebSocket")
            
        # Join mythology notifications group
        self.room_group_name = 'mythology_notifications'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection established message
        await self.safe_send({
            'type': 'connection_established',
            'data': {
                'message': 'Connected to mythology notifications',
                'timestamp': datetime.now().isoformat()
            }
        })
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
                
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })
    
    async def mythology_notification(self, event):
        """Send mythology notification to client"""
        await self.safe_send({
            'type': 'mythology_notification',
            'notification': event['notification']
        })

class SportsArbitrageConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Sports arbitrage WebSocket for real-time arbitrage opportunities.
    """
    
    async def connect(self):
        self.room_group_name = 'sports_arbitrage'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Log connection with user info
        user = self.scope.get('user', AnonymousUser())
        if not isinstance(user, AnonymousUser):
            print(f"INFO WebSocket connected: {user.username}")
        else:
            print("INFO WebSocket connected: anonymous user")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("INFO WebSocket disconnected: ")
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def arbitrage_update(self, event):
        """Send arbitrage update to WebSocket"""
        await self.safe_send({
            'type': 'arbitrage_update',
            'data': event['data']
        })


class SportsRecommendationConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Sports recommendation WebSocket for betting suggestions.
    """
    
    async def connect(self):
        self.room_group_name = 'sports_recommendations'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Log connection with user info
        user = self.scope.get('user', AnonymousUser())
        if not isinstance(user, AnonymousUser):
            print(f"INFO WebSocket connected: {user.username}")
        else:
            print("INFO WebSocket connected: anonymous user")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("INFO WebSocket disconnected: ")
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def recommendation_update(self, event):
        """Send recommendation update to WebSocket"""
        await self.safe_send({
            'type': 'recommendation_update',
            'data': event['data']
        })


class SportsDashboardConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Sports dashboard WebSocket for live dashboard updates.
    """
    
    async def connect(self):
        self.room_group_name = 'sports_dashboard'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Log connection with user info
        user = self.scope.get('user', AnonymousUser())
        if not isinstance(user, AnonymousUser):
            print(f"INFO WebSocket connected: {user.username}")
        else:
            print("INFO WebSocket connected: anonymous user")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("INFO WebSocket disconnected: ")
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.safe_send({
            'type': 'dashboard_update',
            'data': event['data']
        })