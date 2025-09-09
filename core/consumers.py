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

class AgentProgressConsumer(AsyncWebsocketConsumer):
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
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'data': {
                'message': 'Connected to agent progress updates',
                'instance_id': self.instance_id,
                'timestamp': datetime.now().isoformat()
            },
            'channel_name': self.channel_name
        }))
    
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
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            elif message_type == 'subscribe_agent':
                instance_id = text_data_json.get('instance_id')
                # Handle agent subscription
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'data': {
                        'instance_id': instance_id,
                        'status': 'subscribed'
                    }
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            }))
    
    async def agent_progress(self, event):
        """Send agent progress update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'agent_progress',
            'data': event['data']
        }))
    
    async def agent_completed(self, event):
        """Send agent completion notification"""
        await self.send(text_data=json.dumps({
            'type': 'agent_completed',
            'data': event['data']
        }))
    
    async def agent_failed(self, event):
        """Send agent failure notification"""
        await self.send(text_data=json.dumps({
            'type': 'agent_failed',
            'data': event['data']
        }))


class DashboardConsumer(AsyncWebsocketConsumer):
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
        await self.send(text_data=json.dumps({
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
        }))
    
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
            await self.send(text_data=json.dumps({
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
            }))
    
    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))
    
    async def system_alert(self, event):
        """Send system alert to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'system_alert',
            'data': event['data']
        }))


class LiveSportsConsumer(AsyncWebsocketConsumer):
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
            await self.send(text_data=json.dumps({
                'type': 'subscribed',
                'sport': sport,
                'timestamp': datetime.now().isoformat()
            }))
    
    async def live_odds_update(self, event):
        """Send live odds update"""
        await self.send(text_data=json.dumps({
            'type': 'live_odds_update',
            'data': event['data']
        }))
    
    async def betting_opportunity(self, event):
        """Send new betting opportunity"""
        await self.send(text_data=json.dumps({
            'type': 'betting_opportunity',
            'data': event['data']
        }))


class ArbitrageConsumer(AsyncWebsocketConsumer):
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
        await self.send(text_data=json.dumps({
            'type': 'arbitrage_opportunity',
            'data': event['data']
        }))


class AssistantChatConsumer(AsyncWebsocketConsumer):
    """
    AI Assistant chat WebSocket for real-time conversation.
    Migrated from ai-content-studio.
    """
    
    async def connect(self):
        self.user = self.scope['user']
        if self.user == AnonymousUser():
            await self.close()
            return
            
        self.room_group_name = f'assistant_chat_{self.user.id}'
        
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
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json.get('message', '')
            
            # Echo back for demo (in real implementation, this would process with AI)
            await self.send(text_data=json.dumps({
                'type': 'assistant_response',
                'data': {
                    'message': f'Assistant response to: {message}',
                    'timestamp': datetime.now().isoformat()
                }
            }))
    
    async def assistant_response(self, event):
        """Send assistant response to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'assistant_response',
            'data': event['data']
        }))


class OrchestrationConsumer(AsyncWebsocketConsumer):
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
        await self.send(text_data=json.dumps({
            'type': 'orchestration_update',
            'data': event['data']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    System notifications and alerts.
    """
    
    async def connect(self):
        self.user = self.scope['user']
        if self.user == AnonymousUser():
            await self.close()
            return
            
        self.room_group_name = f'notifications_{self.user.id}'
        
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
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))