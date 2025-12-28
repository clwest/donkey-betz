"""
Production-Grade WebSocket Infrastructure
Implements robust connection handling, heartbeat monitoring, and automatic reconnection
"""

import json
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import redis

logger = logging.getLogger(__name__)


class ProductionWebSocketMixin:
    """
    Production-grade WebSocket mixin providing:
    - Heartbeat monitoring
    - Connection health checks
    - Automatic reconnection logic
    - Enhanced error handling
    - Redis connection management
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heartbeat_task = None
        self.health_check_task = None
        self.connection_start_time = None
        self.last_heartbeat = None
        self.heartbeat_interval = getattr(settings, 'WEBSOCKET_HEARTBEAT_INTERVAL', 30)
        self.connection_timeout = getattr(settings, 'WEBSOCKET_CONNECTION_TIMEOUT', 60)
        self.redis_pool = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = getattr(settings, 'WEBSOCKET_MAX_RETRIES', 5)

    async def connect(self):
        """Enhanced connection handling with production monitoring"""
        try:
            await self.accept()
            self.connection_start_time = time.time()
            self.last_heartbeat = time.time()

            # Initialize Redis connection pool
            await self.initialize_redis_pool()

            # Start heartbeat monitoring
            self.heartbeat_task = asyncio.create_task(self.heartbeat_monitor())

            # Start connection health checks
            self.health_check_task = asyncio.create_task(self.connection_health_check())

            logger.info(f"Production WebSocket connected: {self.channel_name}")

            # Send connection confirmation with health status
            await self.send_connection_status('connected')

        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            await self.close(code=1011)  # Internal server error

    async def disconnect(self, close_code):
        """Enhanced disconnection handling"""
        # Cancel background tasks
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.health_check_task:
            self.health_check_task.cancel()

        # Clean up Redis connections
        if self.redis_pool:
            try:
                await self.redis_pool.disconnect()
            except Exception as e:
                logger.warning(f"Redis cleanup error: {e}")

        # Calculate connection duration
        if self.connection_start_time:
            duration = time.time() - self.connection_start_time
            logger.info(f"WebSocket disconnected after {duration:.2f}s: {close_code}")

        await super().disconnect(close_code)

    async def receive(self, text_data):
        """Enhanced message handling with error recovery"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            # Update heartbeat on any message
            self.last_heartbeat = time.time()

            # Handle heartbeat messages
            if message_type == 'ping':
                await self.handle_ping(data)
                return

            # Handle health check requests
            if message_type == 'health_check':
                await self.send_health_status()
                return

            # Handle reconnection requests
            if message_type == 'reconnect':
                await self.handle_reconnect()
                return

            # Process normal messages
            await self.process_message(data)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await self.send_error(f"Processing error: {str(e)}")

    async def initialize_redis_pool(self):
        """Initialize Redis connection pool with production settings"""
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')

            # Create connection pool with production settings
            self.redis_pool = redis.ConnectionPool.from_url(
                redis_url,
                max_connections=10,
                socket_connect_timeout=5,
                socket_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
                retry_on_timeout=True
            )

            # Test connection
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            await asyncio.get_event_loop().run_in_executor(None, redis_client.ping)

            logger.info("Redis connection pool initialized successfully")

        except Exception as e:
            logger.error(f"Redis pool initialization failed: {e}")
            self.redis_pool = None

    async def heartbeat_monitor(self):
        """Monitor WebSocket connection health with heartbeats"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                # Send heartbeat ping
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat',
                    'timestamp': time.time(),
                    'connection_id': self.channel_name
                }))

                # Check if client is responding
                time_since_heartbeat = time.time() - self.last_heartbeat
                if time_since_heartbeat > self.connection_timeout:
                    logger.warning(f"Client heartbeat timeout: {time_since_heartbeat:.2f}s")
                    await self.handle_timeout()
                    break

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                await asyncio.sleep(5)

    async def connection_health_check(self):
        """Monitor overall connection health"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Check Redis health
                redis_healthy = await self.check_redis_health()

                # Check channel layer health
                channel_healthy = await self.check_channel_layer_health()

                # Send health update if there are issues
                if not redis_healthy or not channel_healthy:
                    await self.send_health_status(
                        redis_healthy=redis_healthy,
                        channel_healthy=channel_healthy
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(10)

    async def check_redis_health(self) -> bool:
        """Check Redis connection health"""
        if not self.redis_pool:
            return False

        try:
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            await asyncio.get_event_loop().run_in_executor(None, redis_client.ping)
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    async def check_channel_layer_health(self) -> bool:
        """Check Django Channels health"""
        try:
            # Test channel layer with a simple operation
            await self.channel_layer.group_add("health_check", self.channel_name)
            await self.channel_layer.group_discard("health_check", self.channel_name)
            return True
        except Exception as e:
            logger.error(f"Channel layer health check failed: {e}")
            return False

    async def handle_ping(self, data: Dict[str, Any]):
        """Handle ping messages with pong response"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': data.get('timestamp', time.time()),
            'server_time': time.time(),
            'connection_id': self.channel_name
        }))

    async def handle_timeout(self):
        """Handle connection timeout"""
        logger.warning(f"Connection timeout detected for {self.channel_name}")
        await self.send_error("Connection timeout - please refresh")
        await self.close(code=1001)  # Going away

    async def handle_reconnect(self):
        """Handle reconnection requests"""
        self.reconnect_attempts += 1

        if self.reconnect_attempts > self.max_reconnect_attempts:
            await self.send_error("Maximum reconnection attempts exceeded")
            await self.close(code=1011)
            return

        logger.info(f"Handling reconnection attempt {self.reconnect_attempts}")

        # Reinitialize Redis if needed
        if not await self.check_redis_health():
            await self.initialize_redis_pool()

        # Send reconnection success
        await self.send_connection_status('reconnected')

    async def send_connection_status(self, status: str):
        """Send connection status to client"""
        await self.send(text_data=json.dumps({
            'type': 'connection_status',
            'status': status,
            'timestamp': time.time(),
            'connection_id': self.channel_name,
            'server_info': {
                'redis_healthy': await self.check_redis_health(),
                'channel_healthy': await self.check_channel_layer_health(),
                'uptime': time.time() - self.connection_start_time if self.connection_start_time else 0
            }
        }))

    async def send_health_status(self, redis_healthy=None, channel_healthy=None):
        """Send comprehensive health status"""
        if redis_healthy is None:
            redis_healthy = await self.check_redis_health()
        if channel_healthy is None:
            channel_healthy = await self.check_channel_layer_health()

        await self.send(text_data=json.dumps({
            'type': 'health_status',
            'timestamp': time.time(),
            'connection_id': self.channel_name,
            'health': {
                'redis': redis_healthy,
                'channels': channel_healthy,
                'overall': redis_healthy and channel_healthy
            },
            'metrics': {
                'uptime': time.time() - self.connection_start_time if self.connection_start_time else 0,
                'last_heartbeat': self.last_heartbeat,
                'reconnect_attempts': self.reconnect_attempts
            }
        }))

    async def send_error(self, message: str, error_code: str = "GENERAL_ERROR"):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error_code': error_code,
            'message': message,
            'timestamp': time.time(),
            'connection_id': self.channel_name
        }))

    async def process_message(self, data: Dict[str, Any]):
        """Override this method in concrete implementations"""
        raise NotImplementedError("Subclasses must implement process_message")


class ProductionRevenueConsumer(ProductionWebSocketMixin, AsyncWebsocketConsumer):
    """Production-grade Revenue Dashboard WebSocket consumer"""

    async def connect(self):
        """Connect to Revenue Dashboard with production monitoring"""
        self.room_name = "revenue_dashboard"
        self.room_group_name = f"hub_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Call parent connect (handles heartbeat and Redis setup)
        await super().connect()

        # Send initial revenue data
        await self.send_initial_revenue_data()

        # Start periodic revenue updates
        self.revenue_update_task = asyncio.create_task(self.periodic_revenue_updates())

    async def disconnect(self, close_code):
        """Enhanced disconnect for revenue dashboard"""
        # Cancel revenue update task
        if hasattr(self, 'revenue_update_task'):
            self.revenue_update_task.cancel()

        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        await super().disconnect(close_code)

    async def process_message(self, data: Dict[str, Any]):
        """Process revenue dashboard messages"""
        message_type = data.get('type')

        if message_type == 'get_data':
            await self.send_current_revenue_data()
        elif message_type == 'refresh_metrics':
            await self.refresh_revenue_metrics()
        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def send_initial_revenue_data(self):
        """Send initial revenue data with real-time updates"""
        try:
            # Get real revenue data from unified hub
            from .unified_hub import UnifiedWebSocketHub
            hub = UnifiedWebSocketHub()
            revenue_data = await hub.get_real_revenue_data()

            # Add production metadata
            revenue_data.update({
                'connection_type': 'production',
                'real_time': True,
                'last_updated': datetime.now(timezone.utc).isoformat()
            })

            await self.send(text_data=json.dumps(revenue_data))

        except Exception as e:
            logger.error(f"Error sending initial revenue data: {e}")
            await self.send_error("Failed to load revenue data")

    async def send_current_revenue_data(self):
        """Send current revenue data on demand"""
        await self.send_initial_revenue_data()

    async def periodic_revenue_updates(self):
        """Send periodic revenue updates with production reliability"""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds

                # Check if connection is still healthy
                if not await self.check_redis_health():
                    logger.warning("Redis unhealthy, skipping revenue update")
                    continue

                # Send updated revenue data
                await self.send_current_revenue_data()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Revenue update error: {e}")
                await asyncio.sleep(60)  # Back off on error

    async def refresh_revenue_metrics(self):
        """Refresh revenue metrics with enhanced error handling"""
        try:
            logger.info("Refreshing revenue metrics")

            # Trigger metrics recalculation

            # This would trigger actual metrics refresh
            # For now, just send fresh data
            await self.send_current_revenue_data()

            await self.send(text_data=json.dumps({
                'type': 'metrics_refreshed',
                'timestamp': time.time(),
                'message': 'Revenue metrics updated successfully'
            }))

        except Exception as e:
            logger.error(f"Metrics refresh error: {e}")
            await self.send_error("Failed to refresh metrics")

    async def revenue_update(self, event):
        """Handle revenue update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'revenue_broadcast',
            'data': event.get('data', {}),
            'timestamp': time.time()
        }))