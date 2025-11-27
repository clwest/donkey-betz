"""
Spider Intelligence Bridge for AI Content Creation
===================================================

Session 219: Bridges spider data streams to AI Content Creation agents.
This service listens to spider data published via Redis and routes it
to the appropriate AI Content agents based on spider categories.

The bridge:
1. Subscribes to spider intelligence Redis channels
2. Matches spider data to interested AI Content agents
3. Routes data to AgentIntelligenceService for consumption
4. Tracks routing statistics and data quality
"""

import asyncio
import json
import logging
import redis
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from threading import Thread
import time

from core.services.ai_content_agents import (
    agent_intelligence_service,
    get_agents_for_spider_category,
    get_all_agents,
    AI_CONTENT_AGENTS
)

logger = logging.getLogger(__name__)


class SpiderIntelligenceBridge:
    """
    Bridges spider data to AI Content Creation agents.

    This service creates the real-time connection between 67 spiders
    and 14 AI Content agents by:
    - Subscribing to Redis spider intelligence channels
    - Routing data based on spider categories
    - Feeding data to AgentIntelligenceService
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        self.redis_config = redis_config or {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }

        self.redis_client = None
        self.pubsub = None
        self.is_running = False
        self._listener_thread = None

        # Statistics
        self.stats = {
            'messages_received': 0,
            'messages_routed': 0,
            'routing_errors': 0,
            'start_time': None,
            'last_message_time': None,
            'agents_fed': {},
            'spider_sources': {}
        }

        # Spider category to agent mapping (mirrors spider_agent_connector.py)
        self.category_mapping = {
            # Creative Assets (Envato, CreativeMarket, AdobeStock, Shutterstock, Canva)
            'creative_assets': [
                'image_generation_agent',
                'design_assistant_agent',
                'brand_identity_agent',
                'template_curator_agent'
            ],

            # AI Creative Tools (Midjourney, CivitAI, RunwayML, Replicate)
            'ai_creative': [
                'image_generation_agent',
                'video_generation_agent',
                'style_discovery_agent',
                'prompt_engineering_agent',
                'model_recommender_agent'
            ],

            # Digital Products (Etsy, LemonSqueezy, Sellfy, AppSumo, Gumroad)
            'digital_products': [
                'product_idea_agent',
                'content_strategy_agent',
                'trend_analysis_agent'
            ],

            # Content Creation (ConvertKit, Notion, Figma)
            'content_creation': [
                'content_strategy_agent',
                'design_assistant_agent',
                'template_curator_agent'
            ],

            # Tech/Innovation (HackerNews, DevTo, GitHub, ProductHunt)
            'tech': [
                'trend_analysis_agent',
                'research_agent',
                'innovation_scout_agent'
            ],

            # Innovation (arXiv, TechCrunch, VentureBeat)
            'innovation': [
                'trend_analysis_agent',
                'research_agent',
                'innovation_scout_agent'
            ],

            # News (General news sources)
            'news': [
                'trend_analysis_agent',
                'content_strategy_agent'
            ],

            # Design (Dribbble, Behance, Awwwards)
            'design': [
                'design_assistant_agent',
                'style_discovery_agent',
                'trend_analysis_agent',
                'brand_identity_agent'
            ],

            # Freelance (Upwork, Freelancer, Fiverr)
            'freelance': [
                'opportunity_scanner_agent'
            ],

            # Remote Work (WeWorkRemotely, RemoteOK)
            'remote_work': [
                'opportunity_scanner_agent'
            ],

            # Education (Coursera, Udemy, Skillshare)
            'education': [
                'research_agent',
                'content_strategy_agent'
            ],

            # Financial (CoinGecko, Yahoo Finance, SeekingAlpha)
            'financial': [
                'trend_analysis_agent',
                'research_agent'
            ],

            # Legal (USPTO, CourtListener)
            'legal': [
                'research_agent'
            ]
        }

        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(**self.redis_config)
            self.redis_client.ping()
            self.logger.info("Connected to Redis for spider intelligence bridge")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return False

    def start(self):
        """Start the bridge in a background thread"""
        if self.is_running:
            self.logger.warning("Bridge is already running")
            return

        if not self.connect():
            self.logger.error("Cannot start bridge - Redis connection failed")
            return

        self.is_running = True
        self.stats['start_time'] = datetime.now(timezone.utc).isoformat()

        # Start listener thread
        self._listener_thread = Thread(target=self._run_listener, daemon=True)
        self._listener_thread.start()

        self.logger.info("Spider Intelligence Bridge started")

    def stop(self):
        """Stop the bridge"""
        self.is_running = False

        if self.pubsub:
            try:
                self.pubsub.unsubscribe()
                self.pubsub.close()
            except:
                pass

        self.logger.info("Spider Intelligence Bridge stopped")

    def _run_listener(self):
        """Main listener loop"""
        try:
            self.pubsub = self.redis_client.pubsub()

            # Subscribe to all spider intelligence channels
            channels = [
                'spider:data:stream',           # Main spider data channel
                'intelligence:general:*',        # General intelligence feeds
                'spider_intelligence:*',         # Spider intelligence pattern
                'agent:queue:*'                  # Agent queue updates
            ]

            # Subscribe to pattern channels
            self.pubsub.psubscribe('intelligence:*')
            self.pubsub.psubscribe('spider:*')
            self.pubsub.psubscribe('spider_intelligence:*')

            self.logger.info(f"Subscribed to spider intelligence channels")

            # Listen for messages
            while self.is_running:
                try:
                    message = self.pubsub.get_message(timeout=1.0)

                    if message and message['type'] in ('message', 'pmessage'):
                        self._process_message(message)

                    time.sleep(0.01)  # Small delay to prevent CPU spinning

                except Exception as e:
                    self.logger.error(f"Error in listener loop: {e}")
                    time.sleep(1)

        except Exception as e:
            self.logger.error(f"Listener thread failed: {e}")
        finally:
            self.is_running = False

    def _process_message(self, message: Dict[str, Any]):
        """Process incoming spider message"""
        try:
            self.stats['messages_received'] += 1
            self.stats['last_message_time'] = datetime.now(timezone.utc).isoformat()

            # Parse message data
            data = message.get('data')
            if isinstance(data, bytes):
                data = data.decode('utf-8')

            if not data or data == '1':  # Skip subscription confirmations
                return

            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                self.logger.debug(f"Non-JSON message received: {data[:100]}")
                return

            # Extract spider info
            spider_name = parsed_data.get('spider_name', parsed_data.get('spider_id', 'unknown'))
            spider_type = parsed_data.get('spider_type', self._infer_spider_type(spider_name))

            # Track spider source
            if spider_name not in self.stats['spider_sources']:
                self.stats['spider_sources'][spider_name] = 0
            self.stats['spider_sources'][spider_name] += 1

            # Route to appropriate agents
            self._route_to_agents(spider_name, spider_type, parsed_data)

        except Exception as e:
            self.stats['routing_errors'] += 1
            self.logger.error(f"Error processing message: {e}")

    def _infer_spider_type(self, spider_name: str) -> str:
        """Infer spider type/category from spider name"""
        spider_name_lower = spider_name.lower()

        # Map spider names to categories
        category_keywords = {
            'creative_assets': ['envato', 'creativemarket', 'adobe', 'shutterstock', 'canva', 'stock'],
            'ai_creative': ['midjourney', 'civitai', 'runway', 'replicate', 'stability', 'dalle', 'ai_art'],
            'digital_products': ['etsy', 'lemon', 'sellfy', 'appsumo', 'gumroad', 'product'],
            'content_creation': ['convertkit', 'notion', 'figma', 'content'],
            'tech': ['hackernews', 'hacker', 'devto', 'github', 'producthunt', 'tech'],
            'innovation': ['arxiv', 'techcrunch', 'venturebeat', 'innovation'],
            'news': ['news', 'reuters', 'bloomberg', 'axios'],
            'design': ['dribbble', 'behance', 'awwwards', 'design'],
            'freelance': ['upwork', 'freelancer', 'fiverr', 'toptal', 'guru'],
            'remote_work': ['weworkremotely', 'remoteok', 'remote', 'flexjobs'],
            'education': ['coursera', 'udemy', 'skillshare', 'teachable'],
            'financial': ['coingecko', 'yahoo', 'seekingalpha', 'finance', 'crypto', 'opensea'],
            'legal': ['uspto', 'courtlistener', 'findlaw', 'justia', 'legal']
        }

        for category, keywords in category_keywords.items():
            if any(kw in spider_name_lower for kw in keywords):
                return category

        return 'general'

    def _route_to_agents(self, spider_name: str, spider_type: str, data: Dict[str, Any]):
        """Route spider data to interested agents"""
        try:
            # Get agents interested in this spider category
            interested_agents = self.category_mapping.get(spider_type, [])

            # Also check for agents with matching data interests
            for agent in get_all_agents().values():
                if spider_type in agent.data_interests:
                    if agent.name not in interested_agents:
                        interested_agents.append(agent.name)

            if not interested_agents:
                self.logger.debug(f"No agents interested in {spider_type} from {spider_name}")
                return

            # Prepare intelligence data
            intelligence_item = {
                'spider_name': spider_name,
                'spider_type': spider_type,
                'spider_category': spider_type,
                'data_type': data.get('data_type', 'general'),
                'data': data.get('content', data.get('data', data)),
                'quality_score': data.get('quality_score', data.get('confidence', 0.7)),
                'timestamp': data.get('timestamp', datetime.now(timezone.utc).isoformat())
            }

            # Route to each interested agent
            for agent_name in interested_agents:
                try:
                    agent_intelligence_service.add_intelligence(agent_name, intelligence_item)

                    # Track statistics
                    if agent_name not in self.stats['agents_fed']:
                        self.stats['agents_fed'][agent_name] = 0
                    self.stats['agents_fed'][agent_name] += 1

                    self.stats['messages_routed'] += 1

                except Exception as e:
                    self.logger.error(f"Failed to route to agent {agent_name}: {e}")

            self.logger.debug(f"Routed {spider_name} data to {len(interested_agents)} agents")

        except Exception as e:
            self.stats['routing_errors'] += 1
            self.logger.error(f"Error routing to agents: {e}")

    def inject_spider_data(self, spider_name: str, spider_type: str, data: Dict[str, Any]):
        """
        Manually inject spider data into the bridge.
        Useful for testing or direct integration without Redis.
        """
        self._route_to_agents(spider_name, spider_type, data)

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        return {
            **self.stats,
            'is_running': self.is_running,
            'uptime_seconds': self._calculate_uptime(),
            'agents_registered': len(AI_CONTENT_AGENTS),
            'categories_mapped': len(self.category_mapping)
        }

    def _calculate_uptime(self) -> float:
        """Calculate uptime in seconds"""
        if not self.stats['start_time']:
            return 0

        try:
            start = datetime.fromisoformat(self.stats['start_time'])
            return (datetime.now(timezone.utc) - start).total_seconds()
        except:
            return 0


# Global bridge instance
_bridge_instance: Optional[SpiderIntelligenceBridge] = None


def get_spider_bridge() -> SpiderIntelligenceBridge:
    """Get the global spider intelligence bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = SpiderIntelligenceBridge()
    return _bridge_instance


def start_spider_bridge():
    """Start the global spider intelligence bridge"""
    bridge = get_spider_bridge()
    bridge.start()
    return bridge


def stop_spider_bridge():
    """Stop the global spider intelligence bridge"""
    global _bridge_instance
    if _bridge_instance:
        _bridge_instance.stop()


def inject_test_intelligence(spider_name: str = "test_spider",
                              category: str = "ai_creative",
                              data: Dict[str, Any] = None):
    """
    Inject test intelligence data for development/testing.

    Example usage:
        from core.services.spider_intelligence_bridge import inject_test_intelligence
        inject_test_intelligence(
            spider_name="midjourney_trends",
            category="ai_creative",
            data={
                "title": "Cyberpunk style trending",
                "description": "Neon-lit cityscapes with rain effects",
                "style_tags": ["cyberpunk", "neon", "rain", "city"],
                "popularity_score": 0.95
            }
        )
    """
    bridge = get_spider_bridge()

    test_data = data or {
        'title': 'Test Intelligence Data',
        'description': 'This is test data for development',
        'quality_score': 0.85,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    bridge.inject_spider_data(spider_name, category, {
        'content': test_data,
        'data_type': 'trend_data',
        'quality_score': test_data.get('quality_score', 0.8),
        'timestamp': test_data.get('timestamp', datetime.now(timezone.utc).isoformat())
    })

    logger.info(f"Injected test intelligence: {spider_name} -> {category}")
