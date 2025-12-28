"""
Real-Time WebSocket Publisher
Phase 3: Broadcasting Spider Intelligence to All Connected Clients

This module handles real-time broadcasting of spider discoveries,
agent processing, and advisor insights via WebSockets.
"""

import logging
import asyncio
import json
from typing import Dict
from datetime import datetime
from channels.layers import get_channel_layer
from django.core.cache import cache
from django_redis import get_redis_connection
import hashlib

logger = logging.getLogger(__name__)


class RealtimePublisher:
    """
    Manages real-time broadcasting of spider intelligence through WebSockets
    """

    # Broadcasting channels
    CHANNELS = {
        'spider_discoveries': 'spider.discoveries',
        'agent_processing': 'agent.processing',
        'advisor_insights': 'advisor.insights',
        'opportunity_alerts': 'opportunity.alerts',
        'revenue_updates': 'revenue.updates',
        'system_metrics': 'system.metrics'
    }

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.active_connections = set()
        self.broadcast_stats = {
            'messages_sent': 0,
            'bytes_transmitted': 0,
            'active_subscribers': 0,
            'channels_active': len(self.CHANNELS)
        }
        self.message_queue = asyncio.Queue(maxsize=1000)
        self.deduplication_cache = {}

    async def publish_spider_discovery(self, spider_type: str, data: Dict) -> bool:
        """
        Publish a new discovery from a spider

        Args:
            spider_type: Type of spider that made the discovery
            data: The discovered data

        Returns:
            True if published successfully
        """
        try:
            # Prepare message
            message = {
                'type': 'spider_discovery',
                'spider_type': spider_type,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'id': self._generate_message_id(data)
            }

            # Check for duplicates
            if self._is_duplicate(message['id']):
                logger.debug(f"🔄 Skipping duplicate: {message['id']}")
                return False

            # Add to deduplication cache
            self._add_to_dedup_cache(message['id'])

            # Broadcast to spider discoveries channel
            await self._broadcast_to_group(
                'spider_discoveries',
                message
            )

            # Also send to specific spider channel
            await self._broadcast_to_group(
                f'spider_{spider_type}',
                message
            )

            # Queue for agent routing
            await self._queue_for_agents(spider_type, data)

            logger.info(f"🕷️ Published discovery from {spider_type}")
            return True

        except Exception as e:
            logger.error(f"❌ Error publishing spider discovery: {e}")
            return False

    async def publish_agent_update(self, agent_name: str, update: Dict) -> bool:
        """
        Publish an update from an agent

        Args:
            agent_name: Name of the agent
            update: The agent's processing update

        Returns:
            True if published successfully
        """
        try:
            message = {
                'type': 'agent_update',
                'agent': agent_name,
                'update': update,
                'timestamp': datetime.now().isoformat(),
                'status': update.get('status', 'processing')
            }

            # Broadcast to agent processing channel
            await self._broadcast_to_group(
                'agent_processing',
                message
            )

            # Also send to specific agent channel
            await self._broadcast_to_group(
                f'agent_{agent_name}',
                message
            )

            logger.debug(f"🤖 Published update from {agent_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error publishing agent update: {e}")
            return False

    async def publish_advisor_insight(self, advisor_name: str, insight: Dict) -> bool:
        """
        Publish an insight from a legendary advisor

        Args:
            advisor_name: Name of the advisor
            insight: The advisor's insight

        Returns:
            True if published successfully
        """
        try:
            message = {
                'type': 'advisor_insight',
                'advisor': advisor_name,
                'insight': insight,
                'timestamp': datetime.now().isoformat(),
                'confidence': insight.get('confidence', 0.5),
                'action': insight.get('action', 'review')
            }

            # Broadcast to advisor insights channel
            await self._broadcast_to_group(
                'advisor_insights',
                message
            )

            # Send to specific advisor channel
            await self._broadcast_to_group(
                f'advisor_{advisor_name.replace(" ", "_")}',
                message
            )

            # High confidence insights go to alerts
            if message['confidence'] > 0.8:
                await self.publish_alert({
                    'type': 'high_confidence_insight',
                    'advisor': advisor_name,
                    'insight': insight
                })

            logger.info(f"💡 Published insight from {advisor_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error publishing advisor insight: {e}")
            return False

    async def publish_alert(self, alert: Dict) -> bool:
        """
        Publish a high-priority alert

        Args:
            alert: Alert data

        Returns:
            True if published successfully
        """
        try:
            message = {
                'type': 'alert',
                'alert': alert,
                'timestamp': datetime.now().isoformat(),
                'priority': alert.get('priority', 'medium')
            }

            # Broadcast to opportunity alerts channel
            await self._broadcast_to_group(
                'opportunity_alerts',
                message
            )

            # Store in cache for retrieval
            cache.set(f"alert_{message['timestamp']}", message, 86400)

            logger.warning(f"🚨 Published alert: {alert.get('type', 'unknown')}")
            return True

        except Exception as e:
            logger.error(f"❌ Error publishing alert: {e}")
            return False

    async def publish_revenue_update(self, revenue_data: Dict) -> bool:
        """
        Publish revenue generation updates

        Args:
            revenue_data: Revenue information

        Returns:
            True if published successfully
        """
        try:
            message = {
                'type': 'revenue_update',
                'amount': revenue_data.get('amount', 0),
                'source': revenue_data.get('source', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'cumulative': revenue_data.get('cumulative', 0)
            }

            # Broadcast to revenue updates channel
            await self._broadcast_to_group(
                'revenue_updates',
                message
            )

            # Cache for dashboard
            cache.set('latest_revenue', message, 3600)

            logger.info(f"💰 Published revenue update: ${message['amount']}")
            return True

        except Exception as e:
            logger.error(f"❌ Error publishing revenue update: {e}")
            return False

    async def publish_metrics(self) -> bool:
        """
        Publish system metrics

        Returns:
            True if published successfully
        """
        try:
            # Gather metrics from various sources
            from .agent_router import get_router_stats
            from .advisor_feed import get_advisor_stats

            router_stats = get_router_stats()
            advisor_stats = get_advisor_stats()

            # Get spider stats from cache
            active_spiders = cache.get('active_spiders', [])

            metrics = {
                'type': 'system_metrics',
                'timestamp': datetime.now().isoformat(),
                'spiders': {
                    'active': len(active_spiders),
                    'discoveries': cache.get('total_discoveries', 0)
                },
                'agents': {
                    'active': router_stats.get('active_agents', 0),
                    'total': router_stats.get('total_agents', 0),
                    'average_load': router_stats.get('average_load', 0)
                },
                'advisors': {
                    'active': advisor_stats.get('active_advisors', 0),
                    'total': advisor_stats.get('total_advisors', 0),
                    'insights': advisor_stats.get('total_updates', 0)
                },
                'broadcasting': self.broadcast_stats
            }

            # Broadcast to system metrics channel
            await self._broadcast_to_group(
                'system_metrics',
                metrics
            )

            logger.debug("📊 Published system metrics")
            return True

        except Exception as e:
            logger.error(f"❌ Error publishing metrics: {e}")
            return False

    async def _broadcast_to_group(self, group_name: str, message: Dict):
        """
        Broadcast a message to a WebSocket group

        Args:
            group_name: Name of the WebSocket group
            message: Message to broadcast
        """
        if not self.channel_layer:
            logger.warning("⚠️ Channel layer not available")
            return

        try:
            # Send message to group
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'websocket.send',
                    'text': json.dumps(message)
                }
            )

            # Update statistics
            self.broadcast_stats['messages_sent'] += 1
            self.broadcast_stats['bytes_transmitted'] += len(json.dumps(message))

        except Exception as e:
            logger.error(f"❌ Error broadcasting to {group_name}: {e}")

    async def _queue_for_agents(self, spider_type: str, data: Dict):
        """Queue spider data for agent processing"""
        try:
            redis_conn = get_redis_connection("default")

            # Add to processing queue
            queue_item = {
                'spider_type': spider_type,
                'data': data,
                'queued_at': datetime.now().isoformat()
            }

            redis_conn.rpush(
                'spider_processing_queue',
                json.dumps(queue_item)
            )

            # Trigger agent router
            from .agent_router import route_spider_data
            asyncio.create_task(route_spider_data(spider_type, data))

        except Exception as e:
            logger.error(f"❌ Error queuing for agents: {e}")

    def _generate_message_id(self, data: Dict) -> str:
        """Generate unique message ID for deduplication"""
        # Create hash from data content
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _is_duplicate(self, message_id: str) -> bool:
        """Check if message is duplicate"""
        return message_id in self.deduplication_cache

    def _add_to_dedup_cache(self, message_id: str):
        """Add message ID to deduplication cache"""
        # Keep cache size limited
        if len(self.deduplication_cache) > 10000:
            # Remove oldest entries
            oldest_ids = list(self.deduplication_cache.keys())[:1000]
            for old_id in oldest_ids:
                del self.deduplication_cache[old_id]

        self.deduplication_cache[message_id] = datetime.now()

    async def start_metrics_publisher(self):
        """Start periodic metrics publishing"""
        while True:
            try:
                await self.publish_metrics()
                await asyncio.sleep(10)  # Publish every 10 seconds
            except Exception as e:
                logger.error(f"❌ Metrics publisher error: {e}")
                await asyncio.sleep(30)

    def add_connection(self, connection_id: str):
        """Register a new WebSocket connection"""
        self.active_connections.add(connection_id)
        self.broadcast_stats['active_subscribers'] = len(self.active_connections)
        logger.info(f"➕ New connection: {connection_id} (Total: {len(self.active_connections)})")

    def remove_connection(self, connection_id: str):
        """Remove a WebSocket connection"""
        self.active_connections.discard(connection_id)
        self.broadcast_stats['active_subscribers'] = len(self.active_connections)
        logger.info(f"➖ Removed connection: {connection_id} (Total: {len(self.active_connections)})")

    def get_stats(self) -> Dict:
        """Get broadcasting statistics"""
        return {
            **self.broadcast_stats,
            'dedup_cache_size': len(self.deduplication_cache),
            'channels': list(self.CHANNELS.keys())
        }


# Singleton instance
publisher = RealtimePublisher()


# Public API functions
async def broadcast_spider_discovery(spider_type: str, data: Dict) -> bool:
    """Broadcast a spider discovery"""
    return await publisher.publish_spider_discovery(spider_type, data)


async def broadcast_agent_update(agent_name: str, update: Dict) -> bool:
    """Broadcast an agent update"""
    return await publisher.publish_agent_update(agent_name, update)


async def broadcast_advisor_insight(advisor_name: str, insight: Dict) -> bool:
    """Broadcast an advisor insight"""
    return await publisher.publish_advisor_insight(advisor_name, insight)


async def broadcast_alert(alert: Dict) -> bool:
    """Broadcast an alert"""
    return await publisher.publish_alert(alert)


async def broadcast_revenue(revenue_data: Dict) -> bool:
    """Broadcast revenue update"""
    return await publisher.publish_revenue_update(revenue_data)


def register_connection(connection_id: str):
    """Register a new WebSocket connection"""
    publisher.add_connection(connection_id)


def unregister_connection(connection_id: str):
    """Unregister a WebSocket connection"""
    publisher.remove_connection(connection_id)


def get_broadcast_stats() -> Dict:
    """Get broadcasting statistics"""
    return publisher.get_stats()