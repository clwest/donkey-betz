#!/usr/bin/env python
"""
Production Spider Deployment - Session 4
==========================================

Deploy specialized spiders with real data sources:
- SocialSentimentSpider (Reddit, Bluesky, StockTwits)
- FinancialIntelligenceSpider (Yahoo Finance, Polygon, SEC)
- NewsHarvesterSpider (Bloomberg, Reuters, CNBC)
- MarketDataSpider (Market data sources)
- InnovationTrackingSpider (Tech/innovation sources)

This script deploys spiders in swarms and routes data to advisors/agents.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from ai_core.spiders.base_spider import SpiderTarget
from ai_core.spiders.spider_registry import spider_registry
from persistence.models import SpiderData

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionSpiderDeployment:
    """Manages production spider deployment"""

    def __init__(self):
        self.active_spiders = []
        self.redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

    def create_social_sentiment_swarm(self, count: int = 10) -> List:
        """
        Deploy SocialSentimentSpider swarm

        Target subscribers:
        - sentiment_analysis_agent
        - social_trend_agent
        - warren_buffett (advisor)
        - crypto_expert (advisor)
        """
        SpiderClass = spider_registry.get_spider_class('social_sentiment')
        if not SpiderClass:
            logger.error("SocialSentimentSpider not found in registry!")
            return []

        targets = [
            SpiderTarget("https://www.reddit.com/r/wallstreetbets/", rate_limit=2.0, priority=1),
            SpiderTarget("https://www.reddit.com/r/investing/", rate_limit=2.0, priority=2),
            SpiderTarget("https://www.reddit.com/r/stocks/", rate_limit=2.0, priority=2),
            SpiderTarget("https://www.reddit.com/r/CryptoCurrency/", rate_limit=2.0, priority=3),
        ]

        subscribers = [
            "sentiment_analysis_agent",
            "social_trend_agent",
            "warren_buffett",
            "crypto_expert",
            "marketing_strategist"
        ]

        spiders = []
        for i in range(count):
            spider = SpiderClass(
                spider_id=f"social_sentiment_{i+1:03d}",
                targets=targets,
                subscribers=subscribers,
                redis_config=self.redis_config
            )
            spiders.append(spider)

        logger.info(f"✅ Created {len(spiders)} SocialSentimentSpiders")
        return spiders

    def create_financial_intelligence_swarm(self, count: int = 10) -> List:
        """
        Deploy FinancialIntelligenceSpider swarm

        Target subscribers:
        - financial_analysis_agent
        - warren_buffett (advisor)
        - ray_dalio (advisor)
        """
        SpiderClass = spider_registry.get_spider_class('financial')
        if not SpiderClass:
            logger.error("FinancialIntelligenceSpider not found in registry!")
            return []

        targets = [
            SpiderTarget("https://finance.yahoo.com/trending-tickers", rate_limit=3.0, priority=1),
            SpiderTarget("https://finance.yahoo.com/markets/stocks", rate_limit=3.0, priority=1),
            SpiderTarget("https://www.sec.gov/cgi-bin/browse-edgar", rate_limit=5.0, priority=2),
        ]

        subscribers = [
            "financial_analysis_agent",
            "market_intelligence_agent",
            "warren_buffett",
            "ray_dalio",
            "investment_strategist"
        ]

        spiders = []
        for i in range(count):
            spider = SpiderClass(
                spider_id=f"financial_intel_{i+1:03d}",
                targets=targets,
                subscribers=subscribers,
                redis_config=self.redis_config
            )
            spiders.append(spider)

        logger.info(f"✅ Created {len(spiders)} FinancialIntelligenceSpiders")
        return spiders

    def create_news_harvester_swarm(self, count: int = 8) -> List:
        """
        Deploy NewsHarvesterSpider swarm

        Target subscribers:
        - news_analysis_agent
        - market_intelligence_agent
        """
        SpiderClass = spider_registry.get_spider_class('news_harvester')
        if not SpiderClass:
            logger.error("NewsHarvesterSpider not found in registry!")
            return []

        targets = [
            SpiderTarget("https://www.reuters.com/markets/", rate_limit=3.0, priority=1),
            SpiderTarget("https://www.cnbc.com/markets/", rate_limit=3.0, priority=1),
            SpiderTarget("https://www.bloomberg.com/markets", rate_limit=4.0, priority=2),
        ]

        subscribers = [
            "news_analysis_agent",
            "market_intelligence_agent",
            "content_strategist"
        ]

        spiders = []
        for i in range(count):
            spider = SpiderClass(
                spider_id=f"news_harvester_{i+1:03d}",
                targets=targets,
                subscribers=subscribers,
                redis_config=self.redis_config
            )
            spiders.append(spider)

        logger.info(f"✅ Created {len(spiders)} NewsHarvesterSpiders")
        return spiders

    def create_market_data_swarm(self, count: int = 8) -> List:
        """
        Deploy MarketDataSpider swarm
        """
        SpiderClass = spider_registry.get_spider_class('market_data')
        if not SpiderClass:
            logger.error("MarketDataSpider not found in registry!")
            return []

        targets = [
            SpiderTarget("https://finance.yahoo.com/quote/SPY", rate_limit=2.0, priority=1),
            SpiderTarget("https://finance.yahoo.com/quote/QQQ", rate_limit=2.0, priority=1),
            SpiderTarget("https://finance.yahoo.com/quote/DIA", rate_limit=2.0, priority=2),
        ]

        subscribers = [
            "market_intelligence_agent",
            "warren_buffett",
            "ray_dalio"
        ]

        spiders = []
        for i in range(count):
            spider = SpiderClass(
                spider_id=f"market_data_{i+1:03d}",
                targets=targets,
                subscribers=subscribers,
                redis_config=self.redis_config
            )
            spiders.append(spider)

        logger.info(f"✅ Created {len(spiders)} MarketDataSpiders")
        return spiders

    def create_innovation_tracking_swarm(self, count: int = 5) -> List:
        """
        Deploy InnovationTrackingSpider swarm
        """
        SpiderClass = spider_registry.get_spider_class('innovation')
        if not SpiderClass:
            logger.error("InnovationTrackingSpider not found in registry!")
            return []

        targets = [
            SpiderTarget("https://techcrunch.com/", rate_limit=3.0, priority=1),
            SpiderTarget("https://www.wired.com/", rate_limit=3.0, priority=2),
            SpiderTarget("https://arstechnica.com/", rate_limit=3.0, priority=2),
        ]

        subscribers = [
            "innovation_tracker_agent",
            "technology_analyst",
            "elon_musk"
        ]

        spiders = []
        for i in range(count):
            spider = SpiderClass(
                spider_id=f"innovation_tracker_{i+1:03d}",
                targets=targets,
                subscribers=subscribers,
                redis_config=self.redis_config
            )
            spiders.append(spider)

        logger.info(f"✅ Created {len(spiders)} InnovationTrackingSpiders")
        return spiders

    async def deploy_all(self, duration_minutes: int = 60):
        """
        Deploy all spider swarms and run for specified duration

        Args:
            duration_minutes: How long to run spiders (default 60 minutes)
        """
        logger.info("=" * 80)
        logger.info("PRODUCTION SPIDER DEPLOYMENT - SESSION 4")
        logger.info("=" * 80)

        # Check initial database state
        initial_count = await asyncio.get_event_loop().run_in_executor(
            None, SpiderData.objects.count
        )
        logger.info(f"📊 Initial SpiderData count: {initial_count}")

        # Create all swarms
        logger.info("\n🕷️  Creating spider swarms...")

        social_spiders = self.create_social_sentiment_swarm(count=10)
        financial_spiders = self.create_financial_intelligence_swarm(count=10)
        news_spiders = self.create_news_harvester_swarm(count=8)
        market_spiders = self.create_market_data_swarm(count=8)
        innovation_spiders = self.create_innovation_tracking_swarm(count=5)

        all_spiders = (
            social_spiders +
            financial_spiders +
            news_spiders +
            market_spiders +
            innovation_spiders
        )

        logger.info(f"\n✅ Total spiders deployed: {len(all_spiders)}")
        logger.info(f"   • Social Sentiment: {len(social_spiders)}")
        logger.info(f"   • Financial Intelligence: {len(financial_spiders)}")
        logger.info(f"   • News Harvester: {len(news_spiders)}")
        logger.info(f"   • Market Data: {len(market_spiders)}")
        logger.info(f"   • Innovation Tracking: {len(innovation_spiders)}")

        # Start all spiders
        logger.info(f"\n🚀 Starting all spiders for {duration_minutes} minutes...")
        logger.info("   Press Ctrl+C to stop early\n")

        try:
            # Create tasks for all spiders
            spider_tasks = [asyncio.create_task(spider.start()) for spider in all_spiders]

            # Run for specified duration
            duration_seconds = duration_minutes * 60
            await asyncio.sleep(duration_seconds)

            logger.info("\n⏰ Time limit reached, stopping spiders...")

            # Stop all spiders
            for spider in all_spiders:
                await spider.stop()

            # Cancel tasks
            for task in spider_tasks:
                task.cancel()

            # Wait for tasks to finish cancelling
            await asyncio.gather(*spider_tasks, return_exceptions=True)

        except KeyboardInterrupt:
            logger.info("\n🛑 Interrupted by user, stopping spiders...")
            for spider in all_spiders:
                await spider.stop()

        # Give database a moment to catch up
        await asyncio.sleep(2)

        # Check final database state
        logger.info("\n" + "=" * 80)
        logger.info("DEPLOYMENT RESULTS")
        logger.info("=" * 80)

        final_count = await asyncio.get_event_loop().run_in_executor(
            None, SpiderData.objects.count
        )
        logger.info(f"📊 Final SpiderData count: {final_count}")

        new_entries = final_count - initial_count
        logger.info(f"✨ New entries created: {new_entries}")

        if new_entries > 0:
            logger.info(f"\n✅ SUCCESS! Spiders collected and persisted {new_entries} data points")

            # Show data breakdown by spider type
            def get_type_breakdown():
                from django.db.models import Count
                return list(SpiderData.objects.values('spider_name').annotate(
                    count=Count('spider_name')
                ).order_by('-count')[:10])

            breakdown = await asyncio.get_event_loop().run_in_executor(None, get_type_breakdown)

            logger.info(f"\n📋 Top Spider Types by Data Collected:")
            for item in breakdown:
                logger.info(f"   • {item['spider_name']}: {item['count']} entries")

            # Show aggregate metrics
            logger.info(f"\n📈 Spider Army Metrics:")
            for spider in all_spiders[:5]:  # Show first 5 as sample
                metrics = spider.get_metrics()
                logger.info(f"   • {spider.spider_id}:")
                logger.info(f"      - Data points: {metrics.data_points_collected}")
                logger.info(f"      - Success rate: {metrics.successful_requests}/{metrics.successful_requests + metrics.failed_requests}")

            return True
        else:
            logger.warning(f"\n⚠️  No new entries created!")
            logger.warning(f"   Spiders may need more time or rate limits may be too aggressive")
            return False


async def main():
    """Main execution"""
    logger.info("\n🕷️  Production Spider Deployment\n")
    logger.info("This will deploy 41 specialized spiders to collect real intelligence.\n")
    logger.info("Default runtime: 60 minutes (1 hour)\n")

    deployment = ProductionSpiderDeployment()

    try:
        # Deploy for 60 minutes by default
        success = await deployment.deploy_all(duration_minutes=60)

        if success:
            logger.info("\n" + "🎉" * 40)
            logger.info("DEPLOYMENT SUCCESSFUL!")
            logger.info("Spider army is now collecting real intelligence data")
            logger.info("🎉" * 40)
            sys.exit(0)
        else:
            logger.error("\n" + "⚠️ " * 40)
            logger.error("DEPLOYMENT INCOMPLETE: Limited data collected")
            logger.error("⚠️ " * 40)
            sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Deployment failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Can customize runtime with command line argument
    import sys
    if len(sys.argv) > 1:
        try:
            runtime_minutes = int(sys.argv[1])
            logger.info(f"Custom runtime: {runtime_minutes} minutes")
        except ValueError:
            logger.error("Invalid runtime argument, using default 60 minutes")

    asyncio.run(main())
