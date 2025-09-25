#!/usr/bin/env python3
"""
Test Learning Pipeline with Real API Data
Uses Bluesky, Reddit, and Polygon APIs for real data
"""

import asyncio
import aiohttp
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the real API spider
from backend.spiders.real_api_spider import RealAPISpider
from backend.intelligence.data_transformation_pipeline import DataTransformationPipeline, RawSpiderData
from backend.intelligence.agent_learning_engine import AgentLearningEngine


class RealLearningPipelineTest:
    """Test the learning pipeline with real API data"""

    def __init__(self):
        self.spiders = []
        self.data_transformer = DataTransformationPipeline()
        self.learning_engine = AgentLearningEngine()
        self.stats = {
            'data_collected': 0,
            'signals_generated': 0,
            'agents_learned': 0,
            'api_calls': {
                'bluesky': 0,
                'reddit': 0,
                'polygon': 0
            }
        }

    async def initialize(self):
        """Initialize the test with real spiders"""
        logger.info("🚀 Initializing real learning pipeline test...")

        # Initialize components
        await self.data_transformer.initialize()
        await self.learning_engine.initialize()

        # Create real API spiders
        spider_configs = [
            ('financial_spider_1', 'financial', 'financial'),
            ('social_spider_1', 'social', 'social'),
            ('news_spider_1', 'news', 'news'),
            ('tech_spider_1', 'tech', 'tech'),
        ]

        for spider_id, spider_type, category in spider_configs:
            spider = RealAPISpider(spider_id, spider_type, category)
            await spider.start()
            self.spiders.append(spider)

        logger.info(f"✅ Initialized {len(self.spiders)} real API spiders")

    async def collect_and_learn(self, duration: int = 30):
        """Collect real data and feed to learning engine"""
        logger.info(f"📡 Starting real data collection for {duration} seconds...")

        start_time = datetime.now()
        cycle = 0

        while (datetime.now() - start_time).total_seconds() < duration:
            cycle += 1
            print(f"\n{'='*60}")
            print(f"Cycle #{cycle} - Real Data Collection")
            print(f"{'='*60}")

            for spider in self.spiders:
                try:
                    # Fetch real data
                    data = await spider.fetch_data()

                    if data:
                        self.stats['data_collected'] += 1

                        # Track which API was used
                        if 'bluesky' in str(data).lower() or 'bsky' in str(data).lower():
                            self.stats['api_calls']['bluesky'] += 1
                            api_source = "Bluesky"
                        elif 'reddit' in str(data).lower() or 'subreddit' in str(data).lower():
                            self.stats['api_calls']['reddit'] += 1
                            api_source = "Reddit"
                        elif 'polygon' in str(data).lower() or 'ticker' in str(data).lower():
                            self.stats['api_calls']['polygon'] += 1
                            api_source = "Polygon"
                        else:
                            api_source = "Unknown"

                        print(f"  🕷️ {spider.spider_id} fetched from {api_source}")

                        # Transform to learning signal
                        raw_spider_data = RawSpiderData(
                            spider_id=spider.spider_id,
                            spider_type=spider.category,
                            source_url=api_source,
                            timestamp=datetime.now(timezone.utc),
                            raw_content=data,
                            metadata={'real_data': True},
                            quality_score=0.9
                        )

                        # Process through pipeline
                        signals = await self.data_transformer.transform(raw_spider_data)
                        self.stats['signals_generated'] += len(signals)

                        if signals:
                            print(f"    → Generated {len(signals)} learning signals")

                            # Feed to learning engine
                            for signal in signals:
                                result = await self.learning_engine.process_learning_signal(signal)
                                if result.get('agents_learned'):
                                    agents = result['agents_learned']
                                    self.stats['agents_learned'] += len(agents)
                                    print(f"    ✅ {len(agents)} agents learned: {', '.join(agents[:3])}")

                except Exception as e:
                    logger.error(f"Error with spider {spider.spider_id}: {e}")

            # Show running stats
            print(f"\n📊 Running Stats:")
            print(f"  • Data collected: {self.stats['data_collected']}")
            print(f"  • Signals generated: {self.stats['signals_generated']}")
            print(f"  • Agent learning events: {self.stats['agents_learned']}")

            # Wait before next cycle (to respect rate limits)
            await asyncio.sleep(5)

    async def cleanup(self):
        """Clean up spiders"""
        for spider in self.spiders:
            await spider.stop()

    async def show_results(self):
        """Show final results"""
        print("\n" + "="*80)
        print("REAL LEARNING PIPELINE RESULTS")
        print("="*80)

        print(f"\n📊 Overall Statistics:")
        print(f"  • Total data collected: {self.stats['data_collected']}")
        print(f"  • Total signals generated: {self.stats['signals_generated']}")
        print(f"  • Total agent learning events: {self.stats['agents_learned']}")

        print(f"\n🌐 API Usage:")
        for api, count in self.stats['api_calls'].items():
            if count > 0:
                print(f"  • {api.capitalize()}: {count} calls")

        # Get learning metrics
        metrics = await self.learning_engine.get_learning_metrics()
        if metrics:
            print(f"\n🧠 Learning Effectiveness:")
            print(f"  • Agents with learning: {len([a for a in metrics['agent_metrics'] if metrics['agent_metrics'][a]['items_learned'] > 0])}")
            print(f"  • Average learning rate: {metrics.get('average_learning_rate', 0):.2f}")

            # Show top learners
            top_agents = sorted(
                metrics['agent_metrics'].items(),
                key=lambda x: x[1]['items_learned'],
                reverse=True
            )[:5]

            if top_agents:
                print(f"\n🏆 Top Learning Agents:")
                for agent_id, data in top_agents:
                    if data['items_learned'] > 0:
                        print(f"  • {agent_id}: {data['items_learned']} items learned")

        print(f"\n✅ Real data pipeline test complete!")


async def main():
    """Main test function"""

    print("\n" + "="*80)
    print("REAL LEARNING PIPELINE TEST")
    print("Using: Bluesky, Reddit, and Polygon APIs")
    print("="*80 + "\n")

    test = RealLearningPipelineTest()

    try:
        # Initialize
        await test.initialize()

        # Run collection and learning
        await test.collect_and_learn(duration=30)

        # Show results
        await test.show_results()

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")

    finally:
        await test.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")