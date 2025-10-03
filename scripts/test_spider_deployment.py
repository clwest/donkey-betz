#!/usr/bin/env python
"""
Test Spider Deployment with Database Persistence
=================================================

Deploy a small number of spiders to test that:
1. Spiders can start and run
2. Data is collected
3. Data is persisted to SpiderData table
4. No critical errors occur
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from ai_core.spiders.base_spider import AdaptiveSpider, SpiderTarget
from persistence.models import SpiderData

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_spiders():
    """Create a small set of test spiders"""

    test_targets = [
        # Test with example.com (safe, won't fail)
        SpiderTarget(
            url="https://example.com",
            rate_limit=2.0,  # Slow rate to be respectful
            priority=1
        ),
        SpiderTarget(
            url="https://example.org",
            rate_limit=2.0,
            priority=1
        ),
        SpiderTarget(
            url="https://example.net",
            rate_limit=2.0,
            priority=1
        ),
    ]

    spiders = []

    # Create 5 test spiders
    for i in range(5):
        spider = AdaptiveSpider(
            spider_id=f"test_adaptive_{i+1:03d}",
            targets=test_targets,
            subscribers=["test_agent"],
            redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
        )
        spiders.append(spider)

    return spiders


async def run_spider_test(duration_seconds=120):
    """
    Run spiders for a limited time period

    Args:
        duration_seconds: How long to run the test (default 2 minutes)
    """
    logger.info("=" * 80)
    logger.info("TEST SPIDER DEPLOYMENT")
    logger.info("=" * 80)

    # Check initial database state
    initial_count = await asyncio.get_event_loop().run_in_executor(
        None, SpiderData.objects.count
    )
    logger.info(f"📊 Initial SpiderData count: {initial_count}")

    # Create test spiders
    logger.info("\n🕷️  Creating test spiders...")
    spiders = create_test_spiders()
    logger.info(f"✅ Created {len(spiders)} test spiders")

    for spider in spiders:
        logger.info(f"   • {spider.spider_id} with {len(spider.targets)} targets")

    # Start spiders
    logger.info(f"\n🚀 Starting spiders for {duration_seconds} seconds...")
    logger.info("   Press Ctrl+C to stop early\n")

    try:
        # Create tasks for all spiders
        spider_tasks = [asyncio.create_task(spider.start()) for spider in spiders]

        # Run for specified duration
        await asyncio.sleep(duration_seconds)

        logger.info("\n⏰ Time limit reached, stopping spiders...")

        # Stop all spiders
        for spider in spiders:
            await spider.stop()

        # Cancel tasks
        for task in spider_tasks:
            task.cancel()

        # Wait for tasks to finish cancelling
        await asyncio.gather(*spider_tasks, return_exceptions=True)

    except KeyboardInterrupt:
        logger.info("\n🛑 Interrupted by user, stopping spiders...")
        for spider in spiders:
            await spider.stop()

    # Give database a moment to catch up
    await asyncio.sleep(2)

    # Check final database state
    logger.info("\n" + "=" * 80)
    logger.info("RESULTS")
    logger.info("=" * 80)

    final_count = await asyncio.get_event_loop().run_in_executor(
        None, SpiderData.objects.count
    )
    logger.info(f"📊 Final SpiderData count: {final_count}")

    new_entries = final_count - initial_count
    logger.info(f"✨ New entries created: {new_entries}")

    if new_entries > 0:
        logger.info(f"\n✅ SUCCESS! Spiders collected and persisted {new_entries} data points")

        # Show latest entries
        def get_latest():
            return list(SpiderData.objects.order_by('-created_at')[:min(5, new_entries)])

        latest_entries = await asyncio.get_event_loop().run_in_executor(None, get_latest)

        logger.info(f"\n📋 Latest entries:")
        for entry in latest_entries:
            logger.info(f"   • {entry.spider_name} | {entry.data_type} | Quality: {entry.quality_score:.2f}")

        # Show spider metrics
        logger.info(f"\n📈 Spider Metrics:")
        for spider in spiders:
            metrics = spider.get_metrics()
            logger.info(f"   • {spider.spider_id}:")
            logger.info(f"      - Data points: {metrics.data_points_collected}")
            logger.info(f"      - Successful requests: {metrics.successful_requests}")
            logger.info(f"      - Failed requests: {metrics.failed_requests}")
            logger.info(f"      - Avg response time: {metrics.avg_response_time:.2f}s")

        return True
    else:
        logger.warning(f"\n⚠️  No new entries created!")
        logger.warning(f"   Spiders may need more time or targets may be unreachable")

        # Show spider metrics anyway
        logger.info(f"\n📈 Spider Metrics:")
        for spider in spiders:
            metrics = spider.get_metrics()
            logger.info(f"   • {spider.spider_id}:")
            logger.info(f"      - Data points: {metrics.data_points_collected}")
            logger.info(f"      - Successful requests: {metrics.successful_requests}")
            logger.info(f"      - Failed requests: {metrics.failed_requests}")

        return False


async def main():
    """Main execution"""
    logger.info("\n🕷️  Spider Deployment Test\n")
    logger.info("This will run a small spider army for 2 minutes to test persistence.\n")

    try:
        success = await run_spider_test(duration_seconds=30)  # 30 seconds for quick test

        if success:
            logger.info("\n" + "🎉" * 40)
            logger.info("TEST SUCCESSFUL: Spiders are collecting and persisting data!")
            logger.info("🎉" * 40)
            sys.exit(0)
        else:
            logger.error("\n" + "⚠️ " * 40)
            logger.error("TEST INCOMPLETE: No data collected, may need longer runtime or different targets")
            logger.error("⚠️ " * 40)
            sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Test failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
