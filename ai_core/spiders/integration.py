"""
Spider Army Integration with Unified Donkey Betz Platform
=========================================================

This module provides integration between the Spider Army intelligence network
and the existing Unified Donkey Betz Platform, including agents and advisors.

Features:
- Agent-Spider communication
- Advisor intelligence feeds
- Intelligence routing to existing systems
- Performance monitoring integration
- Django model integration
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import redis
from django.core.cache import cache
from django.db import transaction

# Import existing models
from intelligence.models import ActionPlanExecution
from core.models_unified_system import Agent as UnifiedAgentTemplate  # W002 fix: Agent model used as alias
from advisors.registry import get_advisor_registry, AdvisorProfile

# Import spider components

logger = logging.getLogger(__name__)


class SpiderPlatformIntegration:
    """
    Integration layer between Spider Army and Unified Donkey Betz Platform.

    This class bridges the spider intelligence network with the existing
    agent and advisor systems, ensuring seamless data flow and coordination.
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        """Initialize the integration layer"""
        self.redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}
        self.redis_client = redis.Redis(**self.redis_config)

        # Get existing registries
        self.advisor_registry = get_advisor_registry()

        # Integration state
        self.is_running = False
        self.active_subscriptions: Dict[str, str] = {}  # subscriber_id -> channel

        self.logger = logging.getLogger(__name__)

    async def start_integration(self):
        """Start the platform integration"""
        try:
            self.is_running = True
            self.logger.info("🔗 Starting Spider Army Platform Integration...")

            # Start integration tasks
            tasks = [
                asyncio.create_task(self._intelligence_subscriber()),
                asyncio.create_task(self._agent_intelligence_router()),
                asyncio.create_task(self._advisor_intelligence_router()),
                asyncio.create_task(self._performance_bridge()),
                asyncio.create_task(self._health_sync())
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"Integration startup failed: {e}")
        finally:
            self.is_running = False

    async def _intelligence_subscriber(self):
        """Subscribe to intelligence channels and route to platform"""
        while self.is_running:
            try:
                # Subscribe to general intelligence channels
                pubsub = self.redis_client.pubsub()

                # Subscribe to relevant channels
                channels = [
                    'intelligence:general:*',
                    'intelligence:agent:*',
                    'intelligence:advisor:*',
                    'intelligence:alert:*'
                ]

                for channel in channels:
                    pubsub.psubscribe(channel)

                # Process messages
                for message in pubsub.listen():
                    if message['type'] == 'pmessage':
                        await self._process_intelligence_message(message)

                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Error in intelligence subscriber: {e}")
                await asyncio.sleep(5)

    async def _process_intelligence_message(self, message):
        """Process incoming intelligence message"""
        try:
            channel = message['channel'].decode('utf-8')
            data = json.loads(message['data'])

            # Route based on channel type
            if 'agent:' in channel:
                await self._route_to_agent(channel, data)
            elif 'advisor:' in channel:
                await self._route_to_advisor(channel, data)
            elif 'alert:' in channel:
                await self._route_alert(channel, data)
            else:
                await self._route_general_intelligence(channel, data)

        except Exception as e:
            self.logger.error(f"Error processing intelligence message: {e}")

    async def _route_to_agent(self, channel: str, intelligence_data: Dict[str, Any]):
        """Route intelligence to specific agent"""
        try:
            # Extract agent ID from channel
            agent_id = channel.split(':')[-1]

            # Get agent template
            try:
                agent_template = UnifiedAgentTemplate.objects.get(name=agent_id, is_active=True)
            except UnifiedAgentTemplate.DoesNotExist:
                self.logger.warning(f"Agent {agent_id} not found in database")
                return

            # Create agent execution with intelligence data
            with transaction.atomic():
                execution = ActionPlanExecution.objects.create(
                    template=agent_template,
                    input_data={
                        'intelligence': intelligence_data,
                        'source': 'spider_army',
                        'data_type': intelligence_data.get('data_type', 'general'),
                        'quality_score': intelligence_data.get('quality_score', 0.0),
                        'timestamp': intelligence_data.get('timestamp'),
                        'spider_id': intelligence_data.get('spider_id')
                    },
                    priority='normal',
                    status='pending'
                )

                # Cache for quick access
                cache.set(
                    f'agent_intelligence:{agent_id}:{execution.id}',
                    intelligence_data,
                    timeout=3600  # 1 hour
                )

                self.logger.debug(f"Routed intelligence to agent {agent_id} (execution {execution.id})")

        except Exception as e:
            self.logger.error(f"Error routing intelligence to agent {agent_id}: {e}")

    async def _route_to_advisor(self, channel: str, intelligence_data: Dict[str, Any]):
        """Route intelligence to specific advisor"""
        try:
            # Extract advisor ID from channel
            advisor_id = channel.split(':')[-1]

            # Get advisor profile
            advisor = self.advisor_registry.get_advisor(advisor_id)
            if not advisor:
                self.logger.warning(f"Advisor {advisor_id} not found in registry")
                return

            # Create advisor intelligence record
            intelligence_record = {
                'advisor_id': advisor_id,
                'intelligence_id': intelligence_data.get('id'),
                'data_type': intelligence_data.get('data_type'),
                'content': intelligence_data.get('content'),
                'quality_score': intelligence_data.get('quality_score', 0.0),
                'relevance_tags': intelligence_data.get('relevance_tags', []),
                'source_url': intelligence_data.get('source_url'),
                'timestamp': intelligence_data.get('timestamp'),
                'spider_id': intelligence_data.get('spider_id'),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }

            # Store in advisor's intelligence feed
            feed_key = f'advisor_intelligence:{advisor_id}'
            self.redis_client.lpush(feed_key, json.dumps(intelligence_record))
            self.redis_client.ltrim(feed_key, 0, 999)  # Keep last 1000 items

            # Update advisor's intelligence metrics
            metrics_key = f'advisor_metrics:{advisor_id}'
            metrics = self.redis_client.get(metrics_key)

            if metrics:
                metrics_data = json.loads(metrics)
            else:
                metrics_data = {
                    'total_intelligence': 0,
                    'avg_quality': 0.0,
                    'last_update': None
                }

            # Update metrics
            metrics_data['total_intelligence'] += 1
            quality_score = intelligence_data.get('quality_score', 0.0)

            if metrics_data['total_intelligence'] == 1:
                metrics_data['avg_quality'] = quality_score
            else:
                # Running average
                total = metrics_data['total_intelligence']
                current_avg = metrics_data['avg_quality']
                metrics_data['avg_quality'] = ((current_avg * (total - 1)) + quality_score) / total

            metrics_data['last_update'] = datetime.now(timezone.utc).isoformat()

            # Store updated metrics
            self.redis_client.setex(
                metrics_key,
                86400,  # 24 hours
                json.dumps(metrics_data)
            )

            self.logger.debug(f"Routed intelligence to advisor {advisor_id}")

        except Exception as e:
            self.logger.error(f"Error routing intelligence to advisor {advisor_id}: {e}")

    async def _route_alert(self, channel: str, intelligence_data: Dict[str, Any]):
        """Route high-priority alerts"""
        try:
            alert_type = channel.split(':')[-1]

            # Create alert record
            alert_record = {
                'type': 'spider_intelligence',
                'subtype': alert_type,
                'message': f"High-priority intelligence: {intelligence_data.get('data_type', 'Unknown')}",
                'data': intelligence_data,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'priority': 'high',
                'source': 'spider_army'
            }

            # Store in alerts feed
            self.redis_client.lpush('platform_alerts', json.dumps(alert_record))
            self.redis_client.ltrim('platform_alerts', 0, 99)  # Keep last 100 alerts

            # Notify via cache for immediate access
            cache.set(
                f'spider_alert:{intelligence_data.get("id")}',
                alert_record,
                timeout=3600
            )

            self.logger.info(f"Routed high-priority alert: {alert_type}")

        except Exception as e:
            self.logger.error(f"Error routing alert: {e}")

    async def _route_general_intelligence(self, channel: str, intelligence_data: Dict[str, Any]):
        """Route general intelligence to platform feeds"""
        try:
            category = channel.split(':')[-1]

            # Store in general intelligence feed
            feed_key = f'general_intelligence:{category}'
            self.redis_client.lpush(feed_key, json.dumps(intelligence_data))
            self.redis_client.ltrim(feed_key, 0, 4999)  # Keep last 5000 items

            # Update platform intelligence metrics
            metrics_key = 'platform_intelligence_metrics'

            # Increment category counter
            self.redis_client.hincrby(metrics_key, f'{category}_count', 1)
            self.redis_client.hset(metrics_key, 'last_update', datetime.now(timezone.utc).isoformat())

            self.logger.debug(f"Routed general intelligence to category {category}")

        except Exception as e:
            self.logger.error(f"Error routing general intelligence: {e}")

    async def _agent_intelligence_router(self):
        """Route intelligence specifically for agents"""
        while self.is_running:
            try:
                # Get active agents from database
                active_agents = UnifiedAgentTemplate.objects.filter(is_active=True)

                for agent in active_agents:
                    # Check if agent has intelligence preferences
                    preferences = self._get_agent_preferences(agent)

                    if preferences:
                        # Subscribe agent to relevant intelligence channels
                        await self._subscribe_agent_to_intelligence(agent, preferences)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in agent intelligence router: {e}")
                await asyncio.sleep(60)

    def _get_agent_preferences(self, agent: UnifiedAgentTemplate) -> Dict[str, Any]:
        """Get agent's intelligence preferences"""
        try:
            # Extract preferences from agent configuration
            preferences = {
                'data_types': [],
                'keywords': [],
                'quality_threshold': 0.7,
                'max_intelligence_per_hour': 100
            }

            # Map agent specialization to data types
            specialization = agent.specialization

            if 'financial' in specialization.lower():
                preferences['data_types'].extend(['financial_news', 'market_data', 'sec_filing'])
                preferences['keywords'].extend(['earnings', 'revenue', 'financial'])

            if 'crypto' in specialization.lower():
                preferences['data_types'].extend(['crypto_market_data', 'blockchain_news'])
                preferences['keywords'].extend(['bitcoin', 'ethereum', 'crypto'])

            if 'social' in specialization.lower():
                preferences['data_types'].extend(['social_sentiment', 'social_trends'])
                preferences['keywords'].extend(['social', 'sentiment', 'trending'])

            # Add keywords from routing keywords
            if agent.routing_keywords:
                preferences['keywords'].extend(agent.routing_keywords)

            return preferences

        except Exception as e:
            self.logger.error(f"Error getting agent preferences for {agent.name}: {e}")
            return {}

    async def _subscribe_agent_to_intelligence(self, agent: UnifiedAgentTemplate, preferences: Dict[str, Any]):
        """Subscribe agent to relevant intelligence channels"""
        try:
            # Create subscription record
            subscription_key = f'agent_subscription:{agent.name}'
            subscription_data = {
                'agent_id': agent.name,
                'preferences': preferences,
                'subscribed_at': datetime.now(timezone.utc).isoformat(),
                'active': True
            }

            self.redis_client.setex(
                subscription_key,
                3600,  # 1 hour expiry
                json.dumps(subscription_data)
            )

            self.active_subscriptions[agent.name] = subscription_key

        except Exception as e:
            self.logger.error(f"Error subscribing agent {agent.name} to intelligence: {e}")

    async def _advisor_intelligence_router(self):
        """Route intelligence specifically for advisors"""
        while self.is_running:
            try:
                # Get all advisors from registry
                advisors = self.advisor_registry.list_advisors()

                for advisor in advisors:
                    # Route intelligence based on advisor domain and specializations
                    await self._route_advisor_intelligence(advisor)

                await asyncio.sleep(120)  # Check every 2 minutes

            except Exception as e:
                self.logger.error(f"Error in advisor intelligence router: {e}")
                await asyncio.sleep(120)

    async def _route_advisor_intelligence(self, advisor: AdvisorProfile):
        """Route intelligence for specific advisor"""
        try:
            # Get advisor's specializations and map to intelligence types
            specializations = advisor.specializations

            relevant_channels = []

            for specialization in specializations:
                if 'value' in specialization or 'fundamental' in specialization:
                    relevant_channels.extend(['intelligence:general:financial', 'intelligence:general:earnings'])

                if 'innovation' in specialization or 'disruptive' in specialization:
                    relevant_channels.extend(['intelligence:general:research', 'intelligence:general:innovation'])

                if 'crypto' in specialization or 'blockchain' in specialization:
                    relevant_channels.append('intelligence:general:crypto')

            # Subscribe advisor to relevant channels
            for channel in relevant_channels:
                subscription_key = f'advisor_channel_subscription:{advisor.id}:{channel}'
                self.redis_client.setex(subscription_key, 7200, 'active')  # 2 hours

        except Exception as e:
            self.logger.error(f"Error routing intelligence for advisor {advisor.id}: {e}")

    async def _performance_bridge(self):
        """Bridge spider performance data with platform metrics"""
        while self.is_running:
            try:
                # Collect spider army performance metrics
                spider_metrics = await self._collect_spider_metrics()

                if spider_metrics:
                    # Store in platform format
                    platform_metrics = {
                        'spider_army': spider_metrics,
                        'updated_at': datetime.now(timezone.utc).isoformat(),
                        'integration_status': 'active'
                    }

                    # Store in cache for Django access
                    cache.set('spider_army_metrics', platform_metrics, timeout=300)

                    # Store in Redis for long-term access
                    self.redis_client.setex(
                        'platform:spider_metrics',
                        300,
                        json.dumps(platform_metrics)
                    )

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error in performance bridge: {e}")
                await asyncio.sleep(300)

    async def _collect_spider_metrics(self) -> Optional[Dict[str, Any]]:
        """Collect comprehensive spider metrics"""
        try:
            # Get metrics from various sources
            metrics = {}

            # Army status
            army_status = self.redis_client.get('spider_army:status')
            if army_status:
                metrics['army_status'] = json.loads(army_status)

            # Pipeline metrics
            pipeline_metrics = self.redis_client.get('pipeline:metrics')
            if pipeline_metrics:
                metrics['pipeline_metrics'] = json.loads(pipeline_metrics)

            # Health metrics
            health_data = self.redis_client.get('command_center:spider_health')
            if health_data:
                metrics['health_metrics'] = json.loads(health_data)

            return metrics if metrics else None

        except Exception as e:
            self.logger.error(f"Error collecting spider metrics: {e}")
            return None

    async def _health_sync(self):
        """Sync spider army health with platform health monitoring"""
        while self.is_running:
            try:
                # Get spider army health status
                health_status = await self._get_spider_health_status()

                if health_status:
                    # Update platform health monitoring
                    health_record = {
                        'component': 'spider_army',
                        'status': health_status.get('overall_status', 'unknown'),
                        'details': health_status,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }

                    # Store in platform health monitoring
                    cache.set('health:spider_army', health_record, timeout=600)

                    # Store in Redis
                    self.redis_client.setex(
                        'platform:health:spider_army',
                        600,
                        json.dumps(health_record)
                    )

                await asyncio.sleep(180)  # Check every 3 minutes

            except Exception as e:
                self.logger.error(f"Error in health sync: {e}")
                await asyncio.sleep(180)

    async def _get_spider_health_status(self) -> Optional[Dict[str, Any]]:
        """Get overall spider army health status"""
        try:
            # Collect health data from various sources
            health_data = {}

            # Spider health
            spider_health = self.redis_client.get('command_center:spider_health')
            if spider_health:
                health_data['spider_health'] = json.loads(spider_health)

            # Pipeline health
            pipeline_health = self.redis_client.get('pipeline:health')
            if pipeline_health:
                health_data['pipeline_health'] = json.loads(pipeline_health)

            # System resources
            system_resources = self.redis_client.get('command_center:system_resources')
            if system_resources:
                health_data['system_resources'] = json.loads(system_resources)

            # Determine overall status
            overall_status = self._calculate_overall_health(health_data)
            health_data['overall_status'] = overall_status

            return health_data

        except Exception as e:
            self.logger.error(f"Error getting spider health status: {e}")
            return None

    def _calculate_overall_health(self, health_data: Dict[str, Any]) -> str:
        """Calculate overall health status"""
        try:
            # Health scoring
            health_score = 100

            # Spider health impact
            spider_health = health_data.get('spider_health', {})
            spider_score = spider_health.get('health_score', 100)
            health_score = min(health_score, spider_score)

            # System resources impact
            system_resources = health_data.get('system_resources', {})
            cpu_percent = system_resources.get('cpu_percent', 0)
            memory_percent = system_resources.get('memory_percent', 0)

            if cpu_percent > 90 or memory_percent > 90:
                health_score = min(health_score, 50)
            elif cpu_percent > 75 or memory_percent > 75:
                health_score = min(health_score, 75)

            # Determine status
            if health_score >= 90:
                return 'excellent'
            elif health_score >= 75:
                return 'good'
            elif health_score >= 50:
                return 'fair'
            else:
                return 'poor'

        except Exception as e:
            self.logger.error(f"Error calculating overall health: {e}")
            return 'unknown'

    async def shutdown(self):
        """Shutdown the integration"""
        try:
            self.is_running = False
            self.logger.info("🛑 Spider Army Platform Integration shutdown")

        except Exception as e:
            self.logger.error(f"Error during integration shutdown: {e}")

    def get_agent_intelligence_feed(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get intelligence feed for a specific agent"""
        try:
            feed_key = f'agent_intelligence_feed:{agent_id}'
            feed_items = self.redis_client.lrange(feed_key, 0, limit - 1)

            return [json.loads(item) for item in feed_items]

        except Exception as e:
            self.logger.error(f"Error getting agent intelligence feed: {e}")
            return []

    def get_advisor_intelligence_feed(self, advisor_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get intelligence feed for a specific advisor"""
        try:
            feed_key = f'advisor_intelligence:{advisor_id}'
            feed_items = self.redis_client.lrange(feed_key, 0, limit - 1)

            return [json.loads(item) for item in feed_items]

        except Exception as e:
            self.logger.error(f"Error getting advisor intelligence feed: {e}")
            return []

    def get_platform_intelligence_metrics(self) -> Dict[str, Any]:
        """Get platform-wide intelligence metrics"""
        try:
            metrics_key = 'platform_intelligence_metrics'
            metrics = self.redis_client.hgetall(metrics_key)

            # Convert bytes to strings
            return {k.decode('utf-8'): v.decode('utf-8') for k, v in metrics.items()}

        except Exception as e:
            self.logger.error(f"Error getting platform intelligence metrics: {e}")
            return {}


# Global integration instance
_integration_instance = None

def get_spider_integration(redis_config: Dict[str, Any] = None) -> SpiderPlatformIntegration:
    """Get the global spider integration instance"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = SpiderPlatformIntegration(redis_config)
    return _integration_instance