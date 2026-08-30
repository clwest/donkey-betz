"""
Base Spider Class for Intelligence Army
Provides foundational capabilities for all specialized spiders
"""

import scrapy
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

import django
import os
import sys

# Add the project directory to the Python path
sys.path.append('/Users/donkeyking/Donkey_Betz/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

# Setup Django
django.setup()

from intelligence.models import SpiderIntelligenceNode


class BaseIntelligenceSpider(scrapy.Spider, ABC):
    """
    Base class for all intelligence gathering spiders in the army

    Features:
    - Automatic data persistence to IntelligenceNode
    - Agent subscription management
    - Real-time data distribution
    - Error handling and monitoring
    - Performance metrics
    """

    name = 'base_intelligence_spider'

    # Spider configuration
    allowed_domains = []
    start_urls = []

    # Intelligence configuration
    intelligence_type = 'general'
    confidence_threshold = 0.7
    data_freshness_hours = 24

    # Agent targeting
    target_agents = []  # List of agent names that should receive this data
    target_advisors = []  # List of advisor personalities

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup logging
        self.logger = logging.getLogger(f'spider_army.{self.name}')

        # Performance tracking
        self.start_time = datetime.now()
        self.items_scraped = 0
        self.errors_encountered = 0

        # Data distribution tracking
        self.data_distributed = 0
        self.agents_notified = 0

        # Initialize Redis connection for real-time distribution
        self.setup_redis_connection()

        self.logger.info(f"🕷️ {self.name} spider initialized for intelligence army")

    def setup_redis_connection(self):
        """Setup Redis connection for real-time data distribution"""
        try:
            import redis
            from django.conf import settings

            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.redis_available = True
            self.logger.info("✅ Redis connection established for real-time distribution")
        except Exception as e:
            self.logger.warning(f"⚠️ Redis not available: {e}")
            self.redis_available = False

    def start_requests(self):
        """Generate initial requests"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    'spider_start_time': self.start_time,
                    'intelligence_type': self.intelligence_type
                }
            )

    @abstractmethod
    def parse(self, response):
        """
        Parse response and extract intelligence data
        Must be implemented by subclasses
        """

    def extract_intelligence(self, response, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw scraped data into standardized intelligence format

        Args:
            response: Scrapy response object
            raw_data: Raw extracted data

        Returns:
            Standardized intelligence data
        """
        intelligence = {
            'source_url': response.url,
            'spider_name': self.name,
            'intelligence_type': self.intelligence_type,
            'timestamp': datetime.now().isoformat(),
            'confidence_score': self.calculate_confidence_score(raw_data),
            'data': raw_data,
            'metadata': {
                'response_status': response.status,
                'content_length': len(response.body),
                'processing_time': (datetime.now() - self.start_time).total_seconds()
            }
        }

        return intelligence

    def calculate_confidence_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the extracted data
        Override in subclasses for domain-specific scoring
        """
        base_score = 0.5

        # Basic scoring based on data completeness
        if data:
            completeness = len([v for v in data.values() if v is not None]) / len(data)
            base_score = 0.3 + (completeness * 0.7)

        return min(1.0, max(0.0, base_score))

    def store_intelligence(self, intelligence_data: Dict[str, Any]) -> Optional[SpiderIntelligenceNode]:
        """
        Store intelligence data in the database
        """
        try:
            node = SpiderIntelligenceNode.objects.create(
                spider_name=self.name,
                spider_run_id=f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                intelligence_type=self.intelligence_type,
                source_url=intelligence_data['source_url'],
                source_platform=intelligence_data.get('platform', 'unknown'),
                raw_data=intelligence_data['data'],
                confidence_score=intelligence_data['confidence_score'],
                processing_metadata={
                    'spider_name': self.name,
                    'processing_timestamp': intelligence_data['timestamp'],
                    'metadata': intelligence_data['metadata']
                }
            )

            self.logger.info(f"💾 Stored intelligence node {node.id} from {self.name}")
            return node

        except Exception as e:
            self.logger.error(f"❌ Failed to store intelligence: {e}")
            self.errors_encountered += 1
            return None

    def distribute_to_agents(self, intelligence_data: Dict[str, Any], node_id: Optional[int] = None):
        """
        Distribute intelligence data to subscribed agents and advisors
        """
        try:
            # Prepare distribution data
            distribution_data = {
                'spider_name': self.name,
                'intelligence_type': self.intelligence_type,
                'timestamp': intelligence_data['timestamp'],
                'confidence_score': intelligence_data['confidence_score'],
                'data': intelligence_data['data'],
                'source_url': intelligence_data['source_url'],
                'node_id': node_id
            }

            # Distribute to target agents
            for agent_name in self.target_agents:
                self.send_to_agent(agent_name, distribution_data)

            # Distribute to target advisors
            for advisor_name in self.target_advisors:
                self.send_to_advisor(advisor_name, distribution_data)

            self.data_distributed += 1

        except Exception as e:
            self.logger.error(f"❌ Failed to distribute intelligence: {e}")
            self.errors_encountered += 1

    def send_to_agent(self, agent_name: str, data: Dict[str, Any]):
        """Send intelligence data to specific agent"""
        try:
            if self.redis_available:
                # Real-time distribution via Redis
                channel = f"agent_intel:{agent_name}"
                self.redis_client.publish(channel, json.dumps(data))

                # Also store in agent's intelligence queue
                queue_key = f"agent_queue:{agent_name}"
                self.redis_client.lpush(queue_key, json.dumps(data))
                self.redis_client.expire(queue_key, 86400)  # 24 hour TTL

                self.agents_notified += 1
                self.logger.debug(f"📡 Sent intelligence to agent: {agent_name}")

        except Exception as e:
            self.logger.error(f"❌ Failed to send data to agent {agent_name}: {e}")

    def send_to_advisor(self, advisor_name: str, data: Dict[str, Any]):
        """Send intelligence data to specific advisor personality"""
        try:
            if self.redis_available:
                # Real-time distribution via Redis
                channel = f"advisor_intel:{advisor_name}"
                self.redis_client.publish(channel, json.dumps(data))

                # Store in advisor's specialized queue
                queue_key = f"advisor_queue:{advisor_name}"
                self.redis_client.lpush(queue_key, json.dumps(data))
                self.redis_client.expire(queue_key, 86400)  # 24 hour TTL

                self.logger.debug(f"📈 Sent intelligence to advisor: {advisor_name}")

        except Exception as e:
            self.logger.error(f"❌ Failed to send data to advisor {advisor_name}: {e}")

    def process_item(self, item_data: Dict[str, Any], response):
        """
        Process a single scraped item through the intelligence pipeline
        """
        try:
            # Transform to intelligence format
            intelligence = self.extract_intelligence(response, item_data)

            # Only process if confidence meets threshold
            if intelligence['confidence_score'] >= self.confidence_threshold:
                # Store in database
                node = self.store_intelligence(intelligence)

                # Distribute to agents and advisors
                self.distribute_to_agents(intelligence, node.id if node else None)

                self.items_scraped += 1

                return intelligence
            else:
                self.logger.debug(f"⚠️ Intelligence below confidence threshold: {intelligence['confidence_score']}")

        except Exception as e:
            self.logger.error(f"❌ Failed to process item: {e}")
            self.errors_encountered += 1

        return None

    def closed(self, reason):
        """
        Spider closing callback - generate performance report
        """
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()

        performance_report = {
            'spider_name': self.name,
            'execution_time_seconds': total_time,
            'items_scraped': self.items_scraped,
            'data_distributed': self.data_distributed,
            'agents_notified': self.agents_notified,
            'errors_encountered': self.errors_encountered,
            'success_rate': (self.items_scraped / max(1, self.items_scraped + self.errors_encountered)),
            'items_per_second': self.items_scraped / max(1, total_time),
            'end_reason': reason
        }

        self.logger.info(f"🏁 {self.name} spider completed: {json.dumps(performance_report, indent=2)}")

        # Store performance metrics
        if self.redis_available:
            metrics_key = f"spider_metrics:{self.name}:{end_time.strftime('%Y%m%d_%H%M%S')}"
            self.redis_client.setex(
                metrics_key,
                7 * 24 * 3600,  # 7 days TTL
                json.dumps(performance_report)
            )


class FinancialIntelligenceSpider(BaseIntelligenceSpider):
    """
    Base class for financial intelligence spiders
    Specialized for Warren Buffett, Ray Dalio, and other financial advisors
    """

    intelligence_type = 'financial'

    target_advisors = [
        'warren_buffett',
        'ray_dalio',
        'charlie_munger',
        'cathie_wood',
        'peter_lynch'
    ]

    target_agents = [
        'financial_analysis_agent',
        'value_investing_agent',
        'market_research_agent',
        'risk_assessment_agent'
    ]

    def calculate_confidence_score(self, data: Dict[str, Any]) -> float:
        """Financial data specific confidence scoring"""
        base_score = super().calculate_confidence_score(data)

        # Boost confidence for financial indicators
        financial_indicators = ['price', 'volume', 'market_cap', 'pe_ratio', 'revenue', 'profit']
        found_indicators = sum(1 for indicator in financial_indicators if indicator in str(data).lower())

        indicator_boost = min(0.3, found_indicators * 0.05)

        return min(1.0, base_score + indicator_boost)


class JobOpportunitySpider(BaseIntelligenceSpider):
    """
    Base class for job opportunity spiders
    Specialized for income building and career development
    """

    intelligence_type = 'job_opportunity'

    target_agents = [
        'income_builder',
        'career_development_agent',
        'opportunity_analyzer',
        'freelance_scout_agent'
    ]

    def calculate_confidence_score(self, data: Dict[str, Any]) -> float:
        """Job opportunity specific confidence scoring"""
        base_score = super().calculate_confidence_score(data)

        # Check for key job opportunity fields
        required_fields = ['title', 'budget', 'description']
        field_completeness = sum(1 for field in required_fields if data.get(field))
        completeness_boost = (field_completeness / len(required_fields)) * 0.3

        return min(1.0, base_score + completeness_boost)


class ContentOpportunitySpider(BaseIntelligenceSpider):
    """
    Base class for content monetization spiders
    """

    intelligence_type = 'content_opportunity'

    target_agents = [
        'content_creator_agent',
        'social_media_agent',
        'monetization_agent',
        'trend_analyzer_agent'
    ]


class MarketIntelligenceSpider(BaseIntelligenceSpider):
    """
    Base class for market intelligence spiders
    Real-time market data for trading agents
    """

    intelligence_type = 'market_data'

    target_agents = [
        'trading_agent_1',
        'trading_agent_2',
        'trading_agent_3',
        'arbitrage_agent',
        'options_agent'
    ]

    target_advisors = [
        'paul_tudor_jones',
        'stan_druckenmiller',
        'george_soros'
    ]