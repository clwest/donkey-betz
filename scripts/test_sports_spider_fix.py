#!/usr/bin/env python
"""
Test Sports Sentiment Spider PRAW Fix
======================================

Quick test to verify PRAW authentication and fetch loop work correctly.
"""

import os
import sys
import asyncio
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from ai_core.spiders.base_spider import SpiderTarget
from ai_core.spiders.spider_registry import spider_registry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_single_spider():
    """Test a single sports sentiment spider"""
    logger.info("=" * 80)
    logger.info("SPORTS SENTIMENT SPIDER PRAW FIX TEST")
    logger.info("=" * 80)

    # Get the spider class
    SpiderClass = spider_registry.get_spider_class('social_sentiment')
    if not SpiderClass:
        logger.error("SocialSentimentSpider not found!")
        return False

    # Create test target (single sports subreddit)
    targets = [
        SpiderTarget("https://www.reddit.com/r/sportsbook/", rate_limit=2.0, priority=1)
    ]

    # Create spider
    spider = SpiderClass(
        spider_id="test_sports_sentiment_001",
        targets=targets,
        subscribers=["sports-betting-agent"],
        redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
    )

    logger.info(f"✅ Created spider: {spider.spider_id}")
    logger.info(f"   Reddit API: {'Authenticated' if spider.reddit else 'NOT CONFIGURED'}")

    if not spider.reddit:
        logger.error("❌ PRAW not configured! Check .env for REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        return False

    logger.info("\n🚀 Starting spider for 30 seconds...")

    try:
        # Start spider
        spider_task = asyncio.create_task(spider.start())

        # Run for 30 seconds
        await asyncio.sleep(30)

        # Stop spider
        logger.info("\n⏰ Time's up, stopping spider...")
        await spider.stop()
        spider_task.cancel()

        try:
            await spider_task
        except asyncio.CancelledError:
            pass

        # Check metrics
        metrics = spider.get_metrics()
        logger.info("\n" + "=" * 80)
        logger.info("TEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"Data points collected: {metrics.data_points_collected}")
        logger.info(f"Successful requests: {metrics.successful_requests}")
        logger.info(f"Failed requests: {metrics.failed_requests}")
        logger.info(f"Avg response time: {metrics.avg_response_time:.2f}s")
        logger.info(f"Rate limit hits: {metrics.rate_limit_hits}")

        if metrics.data_points_collected > 0:
            logger.info("\n✅ SUCCESS! Spider is collecting data using PRAW API")
            return True
        else:
            logger.warning("\n⚠️  No data collected. Check logs above for errors.")
            return False

    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        return False


async def main():
    """Main execution"""
    try:
        success = await test_single_spider()

        if success:
            logger.info("\n" + "🎉" * 40)
            logger.info("PRAW FIX SUCCESSFUL!")
            logger.info("Sports sentiment spiders are now fetching real Reddit data")
            logger.info("🎉" * 40)
            sys.exit(0)
        else:
            logger.error("\n⚠️  TEST INCOMPLETE")
            sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
