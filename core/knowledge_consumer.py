"""
WebSocket consumer for real-time knowledge base updates
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class KnowledgeConsumer(AsyncWebsocketConsumer):
    """Handle real-time knowledge base updates via WebSocket"""
    
    async def connect(self):
        """Accept WebSocket connection and join knowledge group"""
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            # Join user-specific knowledge group
            self.knowledge_group = f"knowledge_{self.user.id}"
            await self.channel_layer.group_add(
                self.knowledge_group,
                self.channel_name
            )
            await self.accept()
            
            # Send initial connection confirmation
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to knowledge base updates'
            }))
            logger.info(f"User {self.user.id} connected to knowledge updates")
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Leave knowledge group on disconnect"""
        if hasattr(self, 'knowledge_group'):
            await self.channel_layer.group_discard(
                self.knowledge_group,
                self.channel_name
            )
            logger.info(f"User {self.user.id} disconnected from knowledge updates")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            elif message_type == 'request_stats':
                # Send updated stats
                stats = await self.get_user_stats()
                await self.send(text_data=json.dumps({
                    'type': 'stats_update',
                    'stats': stats
                }))
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def knowledge_added(self, event):
        """Send notification when new knowledge is added"""
        await self.send(text_data=json.dumps({
            'type': 'knowledge_added',
            'knowledge': event['knowledge']
        }))
    
    async def knowledge_deleted(self, event):
        """Send notification when knowledge is deleted"""
        await self.send(text_data=json.dumps({
            'type': 'knowledge_deleted',
            'id': event['id']
        }))
    
    async def stats_update(self, event):
        """Send updated statistics"""
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': event['stats']
        }))
    
    @database_sync_to_async
    def get_user_stats(self):
        """Get current statistics for the user"""
        # This would query the database for current stats
        # For now, return placeholder
        return {
            'total_entries': 0,
            'total_words': 0,
            'categories': [],
            'total_embeddings': 0
        }


def broadcast_knowledge_update(user_id, update_type, data):
    """
    Broadcast knowledge updates to connected clients
    
    Args:
        user_id: User ID to send update to
        update_type: Type of update ('added', 'deleted', 'stats')
        data: Data to send
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    group_name = f"knowledge_{user_id}"
    
    try:
        if update_type == 'added':
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'knowledge_added',
                    'knowledge': data
                }
            )
        elif update_type == 'deleted':
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'knowledge_deleted',
                    'id': data
                }
            )
        elif update_type == 'stats':
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'stats_update',
                    'stats': data
                }
            )
        logger.info(f"Broadcast {update_type} update to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to broadcast knowledge update: {e}")