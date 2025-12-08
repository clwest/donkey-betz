"""
Spider-to-Agent Routing System
Phase 3: Intelligent Routing & Distribution

This module connects the spider network to 151 specialized agents,
ensuring that collected data reaches the right processing units.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import json
from django.core.cache import cache
from django.db import transaction

logger = logging.getLogger(__name__)


class AgentRouter:
    """
    Routes spider-collected data to appropriate agents based on data type and agent specialization.
    """

    # Mapping of spider types to agent specializations
    SPIDER_TO_AGENT_MAP = {
        'job_spider': [
            'job_search_agent',
            'career_advisor_agent',
            'resume_optimizer_agent',
            'interview_prep_agent',
            'salary_negotiator_agent',
            'skill_matcher_agent',
            'remote_work_finder_agent'
        ],
        'financial_spider': [
            'investment_analyst_agent',
            'portfolio_manager_agent',
            'risk_assessor_agent',
            'market_predictor_agent',
            'crypto_analyst_agent',
            'options_trader_agent',
            'dividend_tracker_agent'
        ],
        'news_spider': [
            'news_aggregator_agent',
            'sentiment_analyzer_agent',
            'trend_detector_agent',
            'fact_checker_agent',
            'content_curator_agent',
            'breaking_news_agent'
        ],
        'social_spider': [
            'social_media_manager_agent',
            'influence_tracker_agent',
            'engagement_optimizer_agent',
            'content_creator_agent',
            'community_builder_agent'
        ],
        'real_estate_spider': [
            'property_evaluator_agent',
            'rental_finder_agent',
            'mortgage_calculator_agent',
            'market_analyzer_agent',
            'investment_property_agent'
        ],
        'freelance_spider': [
            'gig_finder_agent',
            'project_matcher_agent',
            'rate_optimizer_agent',
            'client_vetter_agent',
            'proposal_writer_agent'
        ],
        'business_spider': [
            'business_strategist_agent',
            'market_researcher_agent',
            'competitor_analyst_agent',
            'growth_hacker_agent',
            'partnership_finder_agent'
        ]
    }

    def __init__(self):
        self.active_routes = {}
        self.agent_load = {}  # Track load per agent
        self.routing_stats = {
            'total_routed': 0,
            'successful_routes': 0,
            'failed_routes': 0,
            'average_routing_time': 0
        }
        self._load_agents()

    def _load_agents(self):
        """Load all active agents from the database"""
        try:
            from core.models.agents_registry import UnifiedAgentTemplate

            # Get all active agents
            agents = UnifiedAgentTemplate.objects.filter(is_active=True)

            for agent in agents:
                # Initialize agent load tracking
                self.agent_load[agent.name] = {
                    'current_tasks': 0,
                    'max_capacity': 10,  # Configurable per agent
                    'specialization': agent.specialization or 'general',
                    'success_rate': float(agent.success_rate or 0.8)
                }

            logger.info(f"✅ Loaded {len(self.agent_load)} active agents")

        except Exception as e:
            logger.error(f"❌ Error loading agents: {e}")
            # Fall back to cached agent list
            self._load_cached_agents()

    def _load_cached_agents(self):
        """Load agents from cache if database is unavailable"""
        cached_agents = cache.get('active_agents')
        if cached_agents:
            for agent_name in cached_agents:
                self.agent_load[agent_name] = {
                    'current_tasks': 0,
                    'max_capacity': 10,
                    'specialization': 'general',
                    'success_rate': 0.8
                }
            logger.info(f"📦 Loaded {len(self.agent_load)} agents from cache")

    async def route_data(self, spider_type: str, data: Dict) -> Dict:
        """
        Route data from a spider to appropriate agents

        Args:
            spider_type: Type of spider that collected the data
            data: The collected data to route

        Returns:
            Routing result with agent assignments
        """
        start_time = datetime.now()
        routing_result = {
            'spider_type': spider_type,
            'data_id': data.get('id', 'unknown'),
            'routed_to': [],
            'timestamp': start_time.isoformat()
        }

        try:
            # Get agents for this spider type
            target_agents = self.SPIDER_TO_AGENT_MAP.get(spider_type, ['general_processor_agent'])

            # Find available agents with capacity
            available_agents = self._find_available_agents(target_agents)

            if not available_agents:
                logger.warning(f"⚠️ No available agents for {spider_type}")
                routing_result['status'] = 'queued'
                await self._queue_for_retry(spider_type, data)
                return routing_result

            # Route to selected agents
            for agent_name in available_agents[:3]:  # Max 3 agents per data point
                success = await self._route_to_agent(agent_name, data)
                if success:
                    routing_result['routed_to'].append(agent_name)
                    self.agent_load[agent_name]['current_tasks'] += 1

            # Update statistics
            self.routing_stats['total_routed'] += 1
            if routing_result['routed_to']:
                self.routing_stats['successful_routes'] += 1
                routing_result['status'] = 'success'
            else:
                self.routing_stats['failed_routes'] += 1
                routing_result['status'] = 'failed'

            # Calculate routing time
            routing_time = (datetime.now() - start_time).total_seconds()
            self._update_average_routing_time(routing_time)

            # Cache routing result
            cache.set(f"routing_{data.get('id')}", routing_result, 3600)

            logger.info(f"📡 Routed {spider_type} data to {len(routing_result['routed_to'])} agents")

        except Exception as e:
            logger.error(f"❌ Routing error: {e}")
            routing_result['status'] = 'error'
            routing_result['error'] = str(e)

        return routing_result

    def _find_available_agents(self, target_agents: List[str]) -> List[str]:
        """Find agents with available capacity"""
        available = []

        for agent_name in target_agents:
            if agent_name in self.agent_load:
                agent_info = self.agent_load[agent_name]
                if agent_info['current_tasks'] < agent_info['max_capacity']:
                    available.append(agent_name)

        # If no specific agents available, try general agents
        if not available:
            for agent_name, info in self.agent_load.items():
                if info['specialization'] == 'general' and \
                   info['current_tasks'] < info['max_capacity']:
                    available.append(agent_name)

        return available

    async def _route_to_agent(self, agent_name: str, data: Dict) -> bool:
        """
        Route data to a specific agent

        Args:
            agent_name: Name of the target agent
            data: Data to send to the agent

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare message for agent
            message = {
                'type': 'spider_data',
                'agent': agent_name,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'priority': self._calculate_priority(data)
            }

            # Send via Redis pub/sub
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            channel = f"agent:{agent_name}"
            redis_conn.publish(channel, json.dumps(message))

            # Log to agent's task queue
            queue_key = f"agent_queue:{agent_name}"
            redis_conn.rpush(queue_key, json.dumps(message))

            # Set expiry on queue (24 hours)
            redis_conn.expire(queue_key, 86400)

            logger.debug(f"✅ Routed data to {agent_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to route to {agent_name}: {e}")
            return False

    def _calculate_priority(self, data: Dict) -> int:
        """Calculate priority based on data characteristics"""
        priority = 5  # Default medium priority

        # High priority for time-sensitive data
        if data.get('time_sensitive'):
            priority = 9
        # High priority for high-value opportunities
        elif data.get('value', 0) > 10000:
            priority = 8
        # Low priority for historical data
        elif data.get('historical'):
            priority = 3

        return priority

    async def _queue_for_retry(self, spider_type: str, data: Dict):
        """Queue data for retry when agents are busy"""
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")

        retry_queue = f"retry_queue:{spider_type}"
        redis_conn.rpush(retry_queue, json.dumps({
            'data': data,
            'attempts': 1,
            'queued_at': datetime.now().isoformat()
        }))

        # Set expiry (1 hour)
        redis_conn.expire(retry_queue, 3600)

    def _update_average_routing_time(self, new_time: float):
        """Update rolling average of routing time"""
        current_avg = self.routing_stats['average_routing_time']
        total_routed = self.routing_stats['total_routed']

        if total_routed == 1:
            self.routing_stats['average_routing_time'] = new_time
        else:
            # Calculate new average
            self.routing_stats['average_routing_time'] = \
                (current_avg * (total_routed - 1) + new_time) / total_routed

    async def process_retry_queues(self):
        """Process retry queues for failed routings"""
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")

        # Get all retry queues
        retry_queues = redis_conn.keys("retry_queue:*")

        for queue_key in retry_queues:
            spider_type = queue_key.decode().split(":")[1]

            # Process up to 10 items from each queue
            for _ in range(10):
                item = redis_conn.lpop(queue_key)
                if not item:
                    break

                try:
                    retry_data = json.loads(item)
                    # Attempt to route again
                    await self.route_data(spider_type, retry_data['data'])
                except Exception as e:
                    logger.error(f"❌ Retry processing error: {e}")

    def get_routing_stats(self) -> Dict:
        """Get current routing statistics"""
        return {
            **self.routing_stats,
            'active_agents': len([a for a, info in self.agent_load.items()
                                 if info['current_tasks'] > 0]),
            'total_agents': len(self.agent_load),
            'average_load': sum(info['current_tasks'] for info in self.agent_load.values()) /
                          max(len(self.agent_load), 1)
        }

    async def rebalance_load(self):
        """Rebalance load across agents"""
        logger.info("♻️ Rebalancing agent load...")

        # Find overloaded and underloaded agents
        overloaded = []
        underloaded = []

        for agent_name, info in self.agent_load.items():
            load_percentage = info['current_tasks'] / info['max_capacity']
            if load_percentage > 0.8:
                overloaded.append(agent_name)
            elif load_percentage < 0.2:
                underloaded.append(agent_name)

        if overloaded and underloaded:
            logger.info(f"📊 Rebalancing: {len(overloaded)} overloaded, {len(underloaded)} underloaded")
            # Implementation for actual task migration would go here
            # For now, just log the intention

        return {
            'overloaded_agents': overloaded,
            'underloaded_agents': underloaded,
            'rebalanced': len(overloaded) > 0 and len(underloaded) > 0
        }


# Singleton instance
router = AgentRouter()


async def route_spider_data(spider_type: str, data: Dict) -> Dict:
    """
    Public interface for routing spider data to agents

    Args:
        spider_type: Type of spider that collected the data
        data: The collected data

    Returns:
        Routing result
    """
    return await router.route_data(spider_type, data)


def get_router_stats() -> Dict:
    """Get router statistics"""
    return router.get_routing_stats()