"""
Agent-Spider Data Bridge
Connects spider data streams to AI agents for processing and action
"""
import asyncio
import json
import redis
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SpiderDataPacket:
    """Standardized data packet from spiders to agents"""
    spider_name: str
    spider_type: str
    timestamp: datetime
    data: Dict[str, Any]
    confidence: float
    ttl: int = 3600

    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class AgentRequest:
    """Request from an agent for specific data"""
    agent_name: str
    data_types: List[str]
    filters: Dict[str, Any]
    callback_channel: str


class SpiderAgentConnector:
    """Main bridge between spider data and AI agents"""

    def __init__(self):
        self.redis_client = None
        self.redis_pubsub = None
        self.initialized = False
        self._background_tasks = []

        # Routing table: spider categories -> interested agents
        # Session 219: Updated for AI Content Creation platform
        self.routing_table = {
            # Creative Assets (Envato, CreativeMarket, AdobeStock, Shutterstock, Canva)
            'creative_assets': [
                'image_generation_agent',
                'design_assistant_agent',
                'brand_identity_agent',
                'template_curator_agent',
                'content_studio_integration'
            ],

            # AI Creative Tools (Midjourney, CivitAI, RunwayML, Replicate)
            'ai_creative': [
                'image_generation_agent',
                'video_generation_agent',
                'style_discovery_agent',
                'prompt_engineering_agent',
                'model_recommender_agent',
                'content_studio_integration'
            ],

            # Digital Products (Etsy, LemonSqueezy, Sellfy, AppSumo, Gumroad)
            'digital_products': [
                'product_idea_agent',
                'marketplace_analyst_agent',
                'pricing_strategy_agent',
                'template_builder_agent',
                'content_strategy_agent'
            ],

            # Content Creation (ConvertKit, Notion, Figma)
            'content_creation': [
                'content_strategy_agent',
                'design_system_agent',
                'productivity_agent',
                'newsletter_agent',
                'template_curator_agent'
            ],

            # Tech/Innovation (HackerNews, DevTo, GitHub, ProductHunt)
            'tech': [
                'trend_analysis_agent',
                'research_agent',
                'tool_discovery_agent',
                'innovation_scout_agent'
            ],

            # Innovation (arXiv, TechCrunch, VentureBeat)
            'innovation': [
                'trend_analysis_agent',
                'research_agent',
                'innovation_scout_agent',
                'ai_news_agent'
            ],

            # News (General news sources)
            'news': [
                'trend_analysis_agent',
                'content_strategy_agent',
                'news_aggregator_agent'
            ],

            # Financial (CoinGecko, Yahoo Finance, SeekingAlpha)
            'financial': [
                'market_analysis_agent',
                'trend_analysis_agent',
                'financial_insights_agent'
            ],

            # Freelance (Upwork, Freelancer, Fiverr, etc.)
            'freelance': [
                'opportunity_scanner_agent',
                'skill_matcher_agent',
                'pricing_strategy_agent'
            ],

            # Design (Dribbble, Behance, Awwwards)
            'design': [
                'design_assistant_agent',
                'style_discovery_agent',
                'trend_analysis_agent',
                'inspiration_agent'
            ],

            # Remote Work (WeWorkRemotely, RemoteOK)
            'remote_work': [
                'opportunity_scanner_agent',
                'job_matcher_agent'
            ],

            # Education (Coursera, Udemy, Skillshare)
            'education': [
                'skill_development_agent',
                'learning_path_agent',
                'content_strategy_agent'
            ],

            # Legal (USPTO, CourtListener)
            'legal': [
                'research_agent',
                'patent_analyzer_agent'
            ],

            # Sports Betting (legacy support)
            'sports_betting': [
                'sports_analytics_agent',
                'odds_calculator_agent'
            ]
        }

        # Agent registry (will be populated from concrete_executor)
        self.active_agents = {}

        # Data pipeline channels
        self.channels = {
            'spider_data': 'spider:data:stream',
            'agent_requests': 'agent:request:stream',
            'agent_responses': 'agent:response:stream',
            'orchestration': 'orchestration:command:stream'
        }

    async def initialize(self):
        """Initialize the connector and start listening"""
        if self.initialized:
            return

        logger.info("Initializing Spider-Agent Connector...")

        # Initialize Redis connections
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.redis_pubsub = self.redis_client.pubsub()

        # Subscribe to spider data stream
        self.redis_pubsub.subscribe(self.channels['spider_data'])

        # Load active agents from registry
        await self._load_agent_registry()

        self.initialized = True

        # Start routing engine
        asyncio.create_task(self._routing_engine())

        logger.info(f"Connector initialized with {len(self.active_agents)} agents")

    async def _load_agent_registry(self):
        """Load available agents from the system"""
        try:
            # Import concrete executor to get agent list
            from ai_core.agents.concrete_executor import get_concrete_executor
            executor = get_concrete_executor()

            if hasattr(executor, 'agent_registry'):
                for agent_name, agent_class in executor.agent_registry.items():
                    self.active_agents[agent_name] = {
                        'class': agent_class,
                        'instance': None,
                        'capabilities': getattr(agent_class, 'capabilities', []),
                        'data_interests': getattr(agent_class, 'data_interests', [])
                    }

            logger.info(f"Loaded {len(self.active_agents)} agents from registry")

        except ImportError as e:
            logger.error(f"Failed to load agent registry: {e}")

    async def _routing_engine(self):
        """Main routing engine that distributes spider data to agents"""
        logger.info("Starting routing engine...")

        while True:
            try:
                # Check for new spider data
                message = self.redis_pubsub.get_message()

                if message and message['type'] == 'message':
                    await self._process_spider_data(message['data'])

                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Routing engine error: {e}")
                await asyncio.sleep(1)

    async def _process_spider_data(self, data_str: str):
        """Process incoming spider data and route to agents"""
        try:
            data = json.loads(data_str)
            packet = SpiderDataPacket(**data)

            # Determine which agents should receive this data
            interested_agents = self._get_interested_agents(packet)

            # Send data to each interested agent
            for agent_name in interested_agents:
                await self._send_to_agent(agent_name, packet)

            logger.debug(f"Routed {packet.spider_type} data to {len(interested_agents)} agents")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid spider data format: {e}")
        except Exception as e:
            logger.error(f"Error processing spider data: {e}")

    def _get_interested_agents(self, packet: SpiderDataPacket) -> List[str]:
        """Determine which agents should receive this data"""
        interested = []

        # Check routing table for spider type
        spider_type = packet.spider_type.lower()

        for category, agents in self.routing_table.items():
            if category in spider_type or spider_type in category:
                interested.extend(agents)

        # Also check agent-specific interests
        for agent_name, agent_info in self.active_agents.items():
            interests = agent_info.get('data_interests', [])

            if any(interest in packet.spider_type for interest in interests):
                if agent_name not in interested:
                    interested.append(agent_name)

        return interested

    async def _send_to_agent(self, agent_name: str, packet: SpiderDataPacket):
        """Send data packet to a specific agent"""
        try:
            if agent_name not in self.active_agents:
                logger.warning(f"Agent {agent_name} not found in registry")
                return

            # Store data in agent-specific queue
            queue_key = f"agent:queue:{agent_name}"

            self.redis_client.lpush(
                queue_key,
                json.dumps(packet.to_dict())
            )

            # Set TTL on queue
            self.redis_client.expire(queue_key, packet.ttl)

            # Publish notification to agent channel
            agent_channel = f"agent:notify:{agent_name}"
            self.redis_client.publish(
                agent_channel,
                json.dumps({
                    'type': 'new_data',
                    'spider': packet.spider_name,
                    'timestamp': packet.timestamp.isoformat()
                })
            )

        except Exception as e:
            logger.error(f"Failed to send data to {agent_name}: {e}")

    async def publish_spider_data(self, spider_name: str, spider_type: str,
                                 data: Dict[str, Any], confidence: float = 1.0):
        """Publish spider data to the stream (called by spiders)"""
        packet = SpiderDataPacket(
            spider_name=spider_name,
            spider_type=spider_type,
            timestamp=datetime.now(),
            data=data,
            confidence=confidence
        )

        self.redis_client.publish(
            self.channels['spider_data'],
            json.dumps(packet.to_dict())
        )

    async def get_agent_data(self, agent_name: str, limit: int = 10) -> List[Dict]:
        """Get queued data for a specific agent"""
        queue_key = f"agent:queue:{agent_name}"

        data_items = []
        for _ in range(limit):
            item = self.redis_client.rpop(queue_key)
            if not item:
                break
            data_items.append(json.loads(item))

        return data_items

    async def request_spider_data(self, agent_name: str, spider_types: List[str],
                                 filters: Optional[Dict] = None):
        """Allow agents to request specific spider data"""
        request = AgentRequest(
            agent_name=agent_name,
            data_types=spider_types,
            filters=filters or {},
            callback_channel=f"agent:callback:{agent_name}"
        )

        # Publish request to spider orchestrator
        self.redis_client.publish(
            self.channels['agent_requests'],
            json.dumps(asdict(request))
        )

    async def enable_agent_collaboration(self, agent1: str, agent2: str,
                                       task: Dict[str, Any]):
        """Enable two agents to collaborate on a task"""
        collaboration_id = f"collab:{agent1}:{agent2}:{datetime.now().timestamp()}"

        # Create collaboration channel
        collab_data = {
            'id': collaboration_id,
            'agents': [agent1, agent2],
            'task': task,
            'status': 'initiated',
            'timestamp': datetime.now().isoformat()
        }

        # Notify both agents
        for agent in [agent1, agent2]:
            self.redis_client.publish(
                f"agent:notify:{agent}",
                json.dumps({
                    'type': 'collaboration_request',
                    'collaboration': collab_data
                })
            )

        return collaboration_id

    def get_connector_stats(self) -> Dict[str, Any]:
        """Get statistics about the connector"""
        stats = {
            'active_agents': len(self.active_agents),
            'routing_table_size': sum(len(v) for v in self.routing_table.values()),
            'timestamp': datetime.now().isoformat()
        }

        # Get queue sizes for each agent
        queue_sizes = {}
        for agent_name in self.active_agents:
            queue_key = f"agent:queue:{agent_name}"
            queue_sizes[agent_name] = self.redis_client.llen(queue_key)

        stats['agent_queues'] = queue_sizes

        return stats


# Singleton instance
spider_agent_connector = SpiderAgentConnector()


# Integration functions for easy use
async def connect_spiders_to_agents():
    """Initialize the spider-agent connection system"""
    await spider_agent_connector.initialize()
    logger.info("Spider-Agent connection established")


async def send_spider_data_to_agents(spider_name: str, spider_type: str,
                                    data: Dict[str, Any]):
    """Send spider data into the agent ecosystem"""
    await spider_agent_connector.publish_spider_data(
        spider_name=spider_name,
        spider_type=spider_type,
        data=data
    )


async def get_data_for_agent(agent_name: str) -> List[Dict]:
    """Get pending data for a specific agent"""
    return await spider_agent_connector.get_agent_data(agent_name)


def get_connection_stats() -> Dict[str, Any]:
    """Get current connection statistics"""
    return spider_agent_connector.get_connector_stats()