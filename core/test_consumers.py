"""
Test WebSocket consumers for connectivity verification
"""

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class EchoTestConsumer(AsyncWebsocketConsumer):
    """Simple echo consumer for testing WebSocket connectivity without authentication"""
    
    async def connect(self):
        """Accept WebSocket connection without authentication"""
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'WebSocket echo test connection established',
            'info': 'This is a test endpoint for verifying WebSocket connectivity'
        }))
    
    async def disconnect(self, close_code):
        """Handle disconnect"""
        pass
    
    async def receive(self, text_data):
        """Echo back any received message"""
        try:
            data = json.loads(text_data)
            
            # Handle ping specially
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp'),
                    'server_response': 'Test server pong'
                }))
            else:
                # Echo back the message
                await self.send(text_data=json.dumps({
                    'type': 'echo',
                    'original_message': data,
                    'echo_timestamp': data.get('timestamp', 'no timestamp'),
                    'server_info': 'Message echoed successfully'
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON received',
                'received_data': text_data
            }))
        
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }))