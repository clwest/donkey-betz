"""
Spider Data Receiver Mixin - Real-Time Intelligence Integration for Agents
==========================================================================

This module provides a mixin class that can be easily integrated into any existing agent
to enable real-time spider intelligence reception and processing. The mixin adds spider
data capabilities without requiring major changes to existing agent code.

Features:
- Easy integration with existing agents (just inherit the mixin)
- Automatic spider data subscription based on agent type
- Real-time data processing and filtering
- Performance monitoring and error handling
- Flexible configuration and customization

Usage:
    class YourAgent(SpiderDataMixin):
        def __init__(self):
            super().__init__()
            self.setup_spider_data_receiver('your_agent_id', 'your_agent_type')

        def process_spider_intelligence(self, data):
            # Your custom processing logic here
            return self.analyze_intelligence_data(data)
"""

import asyncio
import json
import logging
import redis
from redis import asyncio as aioredis
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from abc import ABC, abstractmethod
import uuid

from ai_core.spiders.agent_data_receiver import (
    AgentSpiderDataReceiver, IntelligenceData, AgentDataSubscription,
    ProcessingMetrics, DataProcessingPriority, ProcessingStatus
)

logger = logging.getLogger(__name__)


@dataclass
class SpiderDataConfig:
    """Configuration for spider data integration"""
    agent_id: str
    agent_type: str
    enabled: bool = True
    auto_start: bool = True
    quality_threshold: float = 0.7
    max_queue_size: int = 1000
    processing_timeout: int = 300
    custom_keywords: List[str] = None
    custom_data_types: List[str] = None


class SpiderDataMixin:
    """
    Mixin class that adds spider data receiving capabilities to any agent.

    This mixin provides:
    - Real-time spider data subscription
    - Intelligent data filtering and routing
    - Performance monitoring
    - Error handling and recovery
    - Easy integration with existing agent code
    """

    def __init__(self, *args, **kwargs):
        """Initialize the spider data mixin"""
        super().__init__(*args, **kwargs)

        # Spider data configuration
        self._spider_data_config: Optional[SpiderDataConfig] = None
        self._spider_data_receiver: Optional[AgentSpiderDataReceiver] = None
        self._spider_data_enabled = False
        self._spider_data_task: Optional[asyncio.Task] = None

        # Data processing
        self._processed_intelligence: Dict[str, Any] = {}
        self._intelligence_queue: List[IntelligenceData] = []
        self._processing_callbacks: List[Callable] = []

        # Redis configuration (can be overridden)
        self._redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

        # Performance tracking
        self._spider_metrics = {
            'total_received': 0,
            'total_processed': 0,
            'processing_errors': 0,
            'last_data_time': None
        }

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def setup_spider_data_receiver(self, agent_id: str, agent_type: str, **config_kwargs):
        """
        Setup spider data receiver for this agent.

        Args:
            agent_id: Unique identifier for this agent
            agent_type: Type of agent (financial, content, job, etc.)
            **config_kwargs: Additional configuration options
        """
        try:
            self.logger.info(f"🔗 Setting up spider data receiver for agent: {agent_id}")

            # Create configuration
            self._spider_data_config = SpiderDataConfig(
                agent_id=agent_id,
                agent_type=agent_type,
                **config_kwargs
            )

            # Create specialized data receiver
            self._spider_data_receiver = self._create_specialized_receiver()

            # Enable spider data
            self._spider_data_enabled = True

            # Auto-start if configured
            if self._spider_data_config.auto_start:
                asyncio.create_task(self.start_spider_data_receiver())

            self.logger.info(f"✅ Spider data receiver setup complete for {agent_id}")

        except Exception as e:
            self.logger.error(f"Failed to setup spider data receiver: {e}")
            raise

    def _create_specialized_receiver(self) -> AgentSpiderDataReceiver:
        """Create a specialized data receiver based on agent type"""

        agent_type = self._spider_data_config.agent_type.lower()
        agent_id = self._spider_data_config.agent_id

        # Create a custom receiver class for this agent
        class AgentCustomDataReceiver(AgentSpiderDataReceiver):
            def __init__(self, parent_agent):
                super().__init__(agent_id, parent_agent._redis_config)
                self.parent_agent = parent_agent

            async def _initialize_agent_subscriptions(self):
                """Initialize subscriptions based on agent type"""
                # Get configuration from parent agent
                config = self.parent_agent._spider_data_config

                # Determine data types and keywords based on agent type
                data_types, keywords = self._get_agent_specific_filters(config.agent_type)

                # Use custom types/keywords if provided
                if config.custom_data_types:
                    data_types.extend(config.custom_data_types)
                if config.custom_keywords:
                    keywords.extend(config.custom_keywords)

                # Create subscription
                subscription = AgentDataSubscription(
                    agent_id=agent_id,
                    channel_pattern="intelligence:agent:*",
                    data_types=data_types,
                    keywords=keywords,
                    quality_threshold=config.quality_threshold,
                    max_queue_size=config.max_queue_size,
                    processing_timeout_seconds=config.processing_timeout
                )

                self.add_subscription(subscription)
                self.parent_agent.logger.info(f"Created subscription: types={data_types}, keywords={keywords}")

            def _get_agent_specific_filters(self, agent_type: str) -> tuple:
                """Get data types and keywords specific to agent type"""

                filters = {
                    'job_application': (
                        ['job_posting', 'freelance_opportunity', 'remote_job', 'gig_work'],
                        ['job', 'hiring', 'freelance', 'contract', 'remote', 'work', 'opportunity']
                    ),
                    'content_marketing': (
                        ['content_opportunity', 'marketplace_listing', 'writing_gig', 'design_contest'],
                        ['content', 'writing', 'design', 'creative', 'marketing', 'blog', 'article']
                    ),
                    'financial': (
                        ['financial_news', 'market_data', 'earnings_report', 'sec_filing'],
                        ['financial', 'market', 'earnings', 'revenue', 'profit', 'investment']
                    ),
                    'income_generation': (
                        ['income_opportunity', 'passive_income', 'revenue_stream', 'monetization'],
                        ['income', 'revenue', 'earning', 'money', 'profit', 'monetize', 'passive']
                    ),
                    'content_creation': (
                        ['content_trend', 'viral_content', 'engagement_data', 'platform_algorithm'],
                        ['content', 'viral', 'trending', 'engagement', 'social', 'platform']
                    ),
                    'job_matching': (
                        ['job_posting', 'skill_demand', 'salary_data', 'market_trend'],
                        ['job', 'skill', 'talent', 'hiring', 'salary', 'demand', 'market']
                    )
                }

                return filters.get(agent_type, ([], []))  # Default to empty filters

            async def process_intelligence_data(self, data: IntelligenceData) -> Dict[str, Any]:
                """Process intelligence data using parent agent's logic"""
                try:
                    # Update parent agent metrics
                    self.parent_agent._spider_metrics['total_received'] += 1
                    self.parent_agent._spider_metrics['last_data_time'] = datetime.now(timezone.utc)

                    # Add to parent's intelligence queue
                    self.parent_agent._intelligence_queue.append(data)

                    # Call parent agent's processing method
                    result = await self.parent_agent.process_spider_intelligence(data)

                    # Update processing metrics
                    self.parent_agent._spider_metrics['total_processed'] += 1

                    # Store processed result
                    self.parent_agent._processed_intelligence[data.id] = {
                        'data': data,
                        'result': result,
                        'processed_at': datetime.now(timezone.utc)
                    }

                    # Call registered callbacks
                    for callback in self.parent_agent._processing_callbacks:
                        try:
                            await callback(data, result)
                        except Exception as e:
                            self.parent_agent.logger.error(f"Callback error: {e}")

                    return result

                except Exception as e:
                    self.parent_agent._spider_metrics['processing_errors'] += 1
                    self.parent_agent.logger.error(f"Error processing spider intelligence: {e}")
                    return {'error': str(e)}

        return AgentCustomDataReceiver(self)

    async def start_spider_data_receiver(self):
        """Start the spider data receiver"""
        if not self._spider_data_enabled or not self._spider_data_receiver:
            self.logger.warning("Spider data receiver not enabled or not configured")
            return

        try:
            self.logger.info(f"🚀 Starting spider data receiver for {self._spider_data_config.agent_id}")

            # Start the data receiver in background
            self._spider_data_task = asyncio.create_task(
                self._spider_data_receiver.start_data_receiver()
            )

            self.logger.info("✅ Spider data receiver started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start spider data receiver: {e}")
            raise

    async def stop_spider_data_receiver(self):
        """Stop the spider data receiver"""
        try:
            if self._spider_data_task:
                self._spider_data_task.cancel()
                try:
                    await self._spider_data_task
                except asyncio.CancelledError:
                    pass

            if self._spider_data_receiver:
                await self._spider_data_receiver.shutdown()

            self.logger.info("✅ Spider data receiver stopped")

        except Exception as e:
            self.logger.error(f"Error stopping spider data receiver: {e}")

    async def process_spider_intelligence(self, data: IntelligenceData) -> Dict[str, Any]:
        """
        Process spider intelligence data.

        This method should be overridden by the implementing agent to provide
        custom intelligence processing logic.

        Args:
            data: Intelligence data from spiders

        Returns:
            Processing result dictionary
        """
        # Default processing - can be overridden by implementing agents
        return {
            'agent_id': self._spider_data_config.agent_id if self._spider_data_config else 'unknown',
            'data_type': data.data_type,
            'quality_score': data.quality_score,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'processing_method': 'default_mixin_processing',
            'insights': f"Processed {data.data_type} data with quality {data.quality_score:.2f}"
        }

    def add_intelligence_callback(self, callback: Callable):
        """
        Add a callback function to be called when intelligence is processed.

        Args:
            callback: Async function that takes (data, result) parameters
        """
        self._processing_callbacks.append(callback)

    def get_spider_data_metrics(self) -> Dict[str, Any]:
        """Get spider data processing metrics"""
        if self._spider_data_receiver:
            receiver_metrics = self._spider_data_receiver.get_processing_metrics()
            return {
                'agent_metrics': self._spider_metrics,
                'receiver_metrics': {
                    'total_received': receiver_metrics.total_received,
                    'total_processed': receiver_metrics.total_processed,
                    'total_failed': receiver_metrics.total_failed,
                    'avg_processing_time_ms': receiver_metrics.avg_processing_time_ms,
                    'avg_quality_score': receiver_metrics.avg_quality_score,
                    'queue_size': receiver_metrics.queue_size,
                    'error_rate': receiver_metrics.error_rate
                },
                'config': {
                    'agent_id': self._spider_data_config.agent_id if self._spider_data_config else None,
                    'agent_type': self._spider_data_config.agent_type if self._spider_data_config else None,
                    'enabled': self._spider_data_enabled
                }
            }
        else:
            return {
                'agent_metrics': self._spider_metrics,
                'receiver_metrics': None,
                'config': {
                    'enabled': self._spider_data_enabled
                }
            }

    def get_recent_intelligence(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently processed intelligence data"""
        recent_items = []

        # Sort by processed time and get most recent
        sorted_items = sorted(
            self._processed_intelligence.items(),
            key=lambda x: x[1]['processed_at'],
            reverse=True
        )

        for item_id, item_data in sorted_items[:limit]:
            recent_items.append({
                'id': item_id,
                'spider_id': item_data['data'].spider_id,
                'data_type': item_data['data'].data_type,
                'quality_score': item_data['data'].quality_score,
                'processed_at': item_data['processed_at'].isoformat(),
                'result_summary': self._summarize_processing_result(item_data['result'])
            })

        return recent_items

    def _summarize_processing_result(self, result: Dict[str, Any]) -> str:
        """Create a summary of processing result"""
        if 'error' in result:
            return f"Error: {result['error']}"
        elif 'insights' in result:
            return result['insights']
        elif 'processing_method' in result:
            return f"Processed via {result['processing_method']}"
        else:
            return "Processed successfully"

    def configure_redis(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """Configure Redis connection settings"""
        self._redis_config = {'host': host, 'port': port, 'db': db}

    @property
    def spider_data_enabled(self) -> bool:
        """Check if spider data is enabled"""
        return self._spider_data_enabled

    @property
    def spider_data_active(self) -> bool:
        """Check if spider data receiver is actively running"""
        return (self._spider_data_enabled and
                self._spider_data_receiver and
                self._spider_data_receiver.is_running)

    def __del__(self):
        """Cleanup when agent is destroyed"""
        if self._spider_data_enabled and self._spider_data_task:
            try:
                asyncio.create_task(self.stop_spider_data_receiver())
            except Exception:
                pass  # Ignore cleanup errors


# Example usage with existing agents
class ExampleJobAgent(SpiderDataMixin):
    """Example of how to integrate spider data with a job application agent"""

    def __init__(self, agent_id: str = "example_job_agent"):
        super().__init__()

        # Setup spider data receiver for job-related intelligence
        self.setup_spider_data_receiver(
            agent_id=agent_id,
            agent_type='job_application',
            quality_threshold=0.8,
            custom_keywords=['python', 'developer', 'remote', 'contractor']
        )

        # Add custom processing callback
        self.add_intelligence_callback(self._on_job_intelligence_received)

    async def process_spider_intelligence(self, data: IntelligenceData) -> Dict[str, Any]:
        """Custom processing for job-related intelligence"""
        content = data.content

        # Extract job-specific information
        job_insights = {
            'agent_id': 'example_job_agent',
            'data_type': data.data_type,
            'quality_score': data.quality_score,
            'job_analysis': {
                'has_remote_option': 'remote' in str(content).lower(),
                'has_python_requirement': 'python' in str(content).lower(),
                'estimated_urgency': 'urgent' if data.quality_score > 0.9 else 'normal'
            },
            'processing_timestamp': datetime.now(timezone.utc).isoformat(),
            'recommended_actions': []
        }

        # Add recommendations based on analysis
        if job_insights['job_analysis']['has_remote_option']:
            job_insights['recommended_actions'].append('Consider for remote application')

        if job_insights['job_analysis']['has_python_requirement']:
            job_insights['recommended_actions'].append('Highlight Python skills in application')

        return job_insights

    async def _on_job_intelligence_received(self, data: IntelligenceData, result: Dict[str, Any]):
        """Callback when job intelligence is received"""
        self.logger.info(f"🎯 New job intelligence: {data.data_type} with {len(result.get('recommended_actions', []))} recommendations")


class ExampleContentAgent(SpiderDataMixin):
    """Example of how to integrate spider data with a content creation agent"""

    def __init__(self, agent_id: str = "example_content_agent"):
        super().__init__()

        # Setup spider data receiver for content-related intelligence
        self.setup_spider_data_receiver(
            agent_id=agent_id,
            agent_type='content_creation',
            quality_threshold=0.75,
            custom_keywords=['viral', 'trending', 'engagement', 'algorithm']
        )

    async def process_spider_intelligence(self, data: IntelligenceData) -> Dict[str, Any]:
        """Custom processing for content-related intelligence"""
        content = data.content
        content_text = str(content).lower()

        # Analyze content trends
        trend_analysis = {
            'agent_id': 'example_content_agent',
            'data_type': data.data_type,
            'quality_score': data.quality_score,
            'trend_indicators': {
                'viral_potential': 'viral' in content_text or 'trending' in content_text,
                'engagement_focused': 'engagement' in content_text or 'interaction' in content_text,
                'algorithm_relevant': 'algorithm' in content_text or 'reach' in content_text
            },
            'content_strategy': [],
            'processing_timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Generate strategy recommendations
        if trend_analysis['trend_indicators']['viral_potential']:
            trend_analysis['content_strategy'].append('Create content around viral trends')

        if trend_analysis['trend_indicators']['engagement_focused']:
            trend_analysis['content_strategy'].append('Focus on engagement-driving content formats')

        return trend_analysis


# Helper function to easily add spider data to existing agents
def enable_spider_data_for_agent(agent_instance, agent_id: str, agent_type: str, **config):
    """
    Helper function to enable spider data for an existing agent instance.

    This function monkey-patches spider data capabilities onto existing agents.

    Args:
        agent_instance: Existing agent instance
        agent_id: Unique identifier for the agent
        agent_type: Type of agent
        **config: Additional configuration options
    """
    try:
        # Create a mixin instance
        mixin = SpiderDataMixin()

        # Copy mixin methods to the agent instance
        for attr_name in dir(mixin):
            if not attr_name.startswith('_') and callable(getattr(mixin, attr_name)):
                setattr(agent_instance, attr_name, getattr(mixin, attr_name))

        # Copy mixin attributes
        for attr_name in ['_spider_data_config', '_spider_data_receiver', '_spider_data_enabled',
                         '_spider_data_task', '_processed_intelligence', '_intelligence_queue',
                         '_processing_callbacks', '_redis_config', '_spider_metrics']:
            setattr(agent_instance, attr_name, getattr(mixin, attr_name))

        # Setup spider data receiver
        agent_instance.setup_spider_data_receiver(agent_id, agent_type, **config)

        logger.info(f"✅ Spider data capabilities added to existing agent: {agent_id}")

        return True

    except Exception as e:
        logger.error(f"Failed to enable spider data for agent {agent_id}: {e}")
        return False