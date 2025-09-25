#!/usr/bin/env python3
"""
Test Learning Pipeline - Local Testing Mode
Tests the spider-to-learning-loop pipeline without external API calls
"""

import asyncio
import logging
import json
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import pipeline components
from backend.intelligence.data_transformation_pipeline import DataTransformationPipeline, RawSpiderData
from backend.intelligence.agent_learning_engine import AgentLearningEngine
from backend.intelligence.unified_learning_pipeline import UnifiedLearningPipeline
from backend.intelligence.learning_metrics_dashboard import LearningMetricsDashboard


class MockSpider:
    """Mock spider that generates test data without external API calls"""

    def __init__(self, spider_type: str, category: str):
        self.spider_type = spider_type
        self.category = category
        self.data_templates = {
            'financial': [
                {'ticker': 'AAPL', 'price': 175.32, 'volume': 58392841, 'change': 2.3},
                {'ticker': 'GOOGL', 'price': 142.18, 'volume': 24839102, 'change': -0.8},
                {'ticker': 'MSFT', 'price': 378.91, 'volume': 31928473, 'change': 1.2},
            ],
            'freelance': [
                {'job': 'Full Stack Developer', 'rate': '$150/hr', 'skills': ['React', 'Python', 'AWS']},
                {'job': 'AI Engineer', 'rate': '$200/hr', 'skills': ['TensorFlow', 'PyTorch', 'MLOps']},
                {'job': 'Data Scientist', 'rate': '$175/hr', 'skills': ['Python', 'SQL', 'Spark']},
            ],
            'content': [
                {'topic': 'AI Trends 2025', 'engagement': 8234, 'platform': 'Medium'},
                {'topic': 'Prompt Engineering', 'engagement': 12893, 'platform': 'Dev.to'},
                {'topic': 'LLM Best Practices', 'engagement': 5672, 'platform': 'HackerNoon'},
            ],
            'tech': [
                {'innovation': 'Quantum Computing Breakthrough', 'impact': 'High', 'field': 'Computing'},
                {'innovation': 'New LLM Architecture', 'impact': 'Medium', 'field': 'AI'},
                {'innovation': 'Brain-Computer Interface', 'impact': 'High', 'field': 'Neuroscience'},
            ],
            'news': [
                {'headline': 'Tech Giants Report Earnings', 'sentiment': 0.7, 'category': 'Business'},
                {'headline': 'New AI Regulations Proposed', 'sentiment': -0.3, 'category': 'Policy'},
                {'headline': 'Breakthrough in Clean Energy', 'sentiment': 0.9, 'category': 'Science'},
            ]
        }

    async def fetch_data(self) -> Dict[str, Any]:
        """Generate mock data for testing"""
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate fetch delay

        templates = self.data_templates.get(self.category, [])
        if templates:
            data = random.choice(templates).copy()
            data['timestamp'] = datetime.now(timezone.utc).isoformat()
            data['source'] = f"mock_{self.spider_type}"
            return data
        return {'error': 'No data template for category'}


class TestLearningPipeline:
    """Test harness for the learning pipeline"""

    def __init__(self):
        self.pipeline = None
        self.mock_spiders = []
        self.test_results = {
            'spiders_deployed': 0,
            'data_collected': 0,
            'signals_generated': 0,
            'agents_learning': 0,
            'errors': []
        }

    async def initialize(self):
        """Initialize the test pipeline"""
        logger.info("🔬 Initializing test learning pipeline...")

        # Create pipeline
        self.pipeline = UnifiedLearningPipeline()
        await self.pipeline.initialize()

        # Create mock spiders
        spider_configs = [
            ('financial_spider', 'financial'),
            ('job_spider', 'freelance'),
            ('content_spider', 'content'),
            ('tech_spider', 'tech'),
            ('news_spider', 'news'),
        ]

        for spider_type, category in spider_configs:
            for i in range(5):  # Create 5 of each type
                spider = MockSpider(f"{spider_type}_{i}", category)
                self.mock_spiders.append(spider)

        self.test_results['spiders_deployed'] = len(self.mock_spiders)
        logger.info(f"✅ Deployed {len(self.mock_spiders)} mock spiders")

    async def run_spider_collection(self, duration: int = 30):
        """Run spider data collection for specified duration"""
        logger.info(f"🕷️ Running spider collection for {duration} seconds...")

        start_time = datetime.now()
        collection_tasks = []

        while (datetime.now() - start_time).total_seconds() < duration:
            # Select random spiders to fetch data
            active_spiders = random.sample(self.mock_spiders, min(10, len(self.mock_spiders)))

            for spider in active_spiders:
                task = asyncio.create_task(self._collect_and_process(spider))
                collection_tasks.append(task)

            # Wait a bit before next batch
            await asyncio.sleep(2)

        # Wait for remaining tasks
        if collection_tasks:
            await asyncio.gather(*collection_tasks, return_exceptions=True)

        logger.info(f"📊 Collection complete: {self.test_results['data_collected']} items collected")

    async def _collect_and_process(self, spider):
        """Collect data from spider and send to pipeline"""
        try:
            # Collect data
            data = await spider.fetch_data()
            if 'error' not in data:
                self.test_results['data_collected'] += 1

                # Create raw spider data
                raw_data = RawSpiderData(
                    spider_id=f"{spider.spider_type}_{datetime.now().timestamp()}",
                    spider_type=spider.category,
                    source_url=f"mock://{spider.spider_type}",
                    timestamp=datetime.now(timezone.utc),
                    raw_content=data,
                    metadata={'test_mode': True},
                    quality_score=random.uniform(0.6, 1.0)
                )

                # Process through pipeline
                if self.pipeline.data_transformer:
                    signals = await self.pipeline.data_transformer.transform(raw_data)
                    self.test_results['signals_generated'] += len(signals)

                    # Process signals through learning engine
                    if self.pipeline.learning_engine and signals:
                        for signal in signals:
                            result = await self.pipeline.learning_engine.process_learning_signal(signal)
                            if result.get('agents_learned'):
                                self.test_results['agents_learning'] += len(result['agents_learned'])

        except Exception as e:
            self.test_results['errors'].append(str(e))
            logger.error(f"Error in spider {spider.spider_type}: {e}")

    async def check_learning_metrics(self):
        """Check learning metrics from the pipeline"""
        logger.info("📈 Checking learning metrics...")

        if self.pipeline.metrics_dashboard:
            metrics = await self.pipeline.metrics_dashboard.get_learning_effectiveness()

            logger.info("Learning Effectiveness Metrics:")
            logger.info(f"  • Overall Score: {metrics['overall_score']:.1f}%")
            logger.info(f"  • Knowledge Retention: {metrics['knowledge_retention_rate']:.1f}%")
            logger.info(f"  • Agent Improvement: {metrics['agent_improvement_rate']:.1f}%")
            logger.info(f"  • Signal Quality: {metrics['signal_quality_score']:.1f}%")

            # Get top performing agents
            top_agents = await self.pipeline.metrics_dashboard.get_top_performing_agents(limit=5)
            if top_agents:
                logger.info("\nTop Learning Agents:")
                for agent in top_agents:
                    logger.info(f"  • {agent['agent_id']}: {agent['score']:.1f} (learned {agent['items_learned']} items)")

    async def run_test(self):
        """Run the complete test"""
        print("\n" + "="*80)
        print("LEARNING PIPELINE TEST - LOCAL MODE")
        print("Testing without external API calls")
        print("="*80 + "\n")

        try:
            # Initialize
            await self.initialize()

            # Start pipeline
            logger.info("🚀 Starting unified learning pipeline...")
            await self.pipeline.start()

            # Run spider collection
            await self.run_spider_collection(duration=30)

            # Check metrics
            await self.check_learning_metrics()

            # Print results
            print("\n" + "="*80)
            print("TEST RESULTS")
            print("="*80)
            print(f"✅ Spiders Deployed: {self.test_results['spiders_deployed']}")
            print(f"📦 Data Collected: {self.test_results['data_collected']}")
            print(f"🎯 Signals Generated: {self.test_results['signals_generated']}")
            print(f"🧠 Agent Learning Events: {self.test_results['agents_learning']}")
            print(f"❌ Errors: {len(self.test_results['errors'])}")

            if self.test_results['errors']:
                print("\nErrors encountered:")
                for error in self.test_results['errors'][:5]:
                    print(f"  • {error}")

            # Calculate success rate
            if self.test_results['data_collected'] > 0:
                success_rate = (self.test_results['signals_generated'] / self.test_results['data_collected']) * 100
                print(f"\n🎯 Signal Generation Rate: {success_rate:.1f}%")

            print("\n✅ Test completed successfully!")

        except Exception as e:
            logger.error(f"Test failed: {e}")
            print(f"\n❌ Test failed: {e}")

        finally:
            # Cleanup
            if self.pipeline:
                await self.pipeline.stop()
            logger.info("🧹 Cleanup complete")


async def main():
    """Main entry point"""
    test = TestLearningPipeline()
    await test.run_test()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")