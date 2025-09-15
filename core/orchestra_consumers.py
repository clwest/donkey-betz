"""
WebSocket consumers for Orchestra and Control interfaces
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class OrchestraConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Orchestra interface"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'orchestra'
        self.room_group_name = f'orchestra_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Orchestra WebSocket connected: {self.channel_name}")

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Orchestra'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Orchestra WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                # Respond to ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))

            elif message_type == 'agent_status':
                # Send agent status update
                await self.send(text_data=json.dumps({
                    'type': 'agent_status',
                    'agents': self.get_agent_status()
                }))

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    def get_agent_status(self):
        """Get current agent status"""
        # Placeholder for agent status
        return {
            'total': 36,
            'active': 12,
            'idle': 24,
            'error': 0
        }

    async def agent_update(self, event):
        """Handle agent update events"""
        await self.send(text_data=json.dumps({
            'type': 'agent_update',
            'agent': event.get('agent'),
            'status': event.get('status'),
            'message': event.get('message')
        }))


class ControlConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Control Panel interface"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'control'
        self.room_group_name = f'control_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Control Panel WebSocket connected: {self.channel_name}")

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Control Panel'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Control Panel WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                # Respond to ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))

            elif message_type == 'system_status':
                # Send system status
                await self.send(text_data=json.dumps({
                    'type': 'system_status',
                    'status': self.get_system_status()
                }))

            elif message_type == 'command':
                # Handle control commands
                command = data.get('command')
                result = await self.handle_command(command, data.get('params', {}))
                await self.send(text_data=json.dumps({
                    'type': 'command_result',
                    'command': command,
                    'result': result
                }))

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    def get_system_status(self):
        """Get current system status"""
        return {
            'services': {
                'api': 'online',
                'websocket': 'online',
                'celery': 'online',
                'redis': 'online',
                'database': 'online'
            },
            'metrics': {
                'active_connections': 5,
                'requests_per_minute': 120,
                'cpu_usage': 45.2,
                'memory_usage': 62.8
            }
        }

    async def handle_command(self, command, params):
        """Handle control commands"""
        if command == 'restart_service':
            service = params.get('service')
            logger.info(f"Restarting service: {service}")
            return {'status': 'success', 'message': f'Service {service} restarted'}

        elif command == 'clear_cache':
            logger.info("Clearing cache")
            return {'status': 'success', 'message': 'Cache cleared'}

        elif command == 'trigger_backup':
            logger.info("Triggering backup")
            return {'status': 'success', 'message': 'Backup triggered'}

        else:
            return {'status': 'error', 'message': f'Unknown command: {command}'}

    async def system_update(self, event):
        """Handle system update events"""
        await self.send(text_data=json.dumps({
            'type': 'system_update',
            'component': event.get('component'),
            'status': event.get('status'),
            'metrics': event.get('metrics')
        }))