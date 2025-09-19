"""
Generic WebSocket consumer for testing and basic connections
"""

from channels.generic.websocket import AsyncWebsocketConsumer
import json


class GenericWebSocketConsumer(AsyncWebsocketConsumer):
    """
    Generic WebSocket consumer that handles basic connections
    This allows /ws/ to work without a specific endpoint
    """
    
    async def connect(self):
        """Accept WebSocket connection"""
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'WebSocket connected successfully',
            'endpoint': self.scope['path'],
            'status': 'ready'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        pass
    
    async def receive(self, text_data):
        """Echo back any received messages"""
        try:
            # Parse incoming message
            message = json.loads(text_data)
            
            # Echo back with confirmation
            await self.send(text_data=json.dumps({
                'type': 'echo',
                'received': message,
                'status': 'ok'
            }))
            
        except json.JSONDecodeError:
            # If not JSON, just echo the text
            await self.send(text_data=json.dumps({
                'type': 'echo',
                'message': text_data,
                'status': 'ok'
            }))
