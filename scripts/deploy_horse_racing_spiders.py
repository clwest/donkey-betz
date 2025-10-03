#!/usr/bin/env python
"""
Horse Racing Spider Deployment
===============================

Deploy horse racing spiders for betting intelligence.

Target Agents:
- horse-racing-specialist (to be created)
- betting-analyst
- value-betting-agent
- bankroll-manager-agent

Expected Impact: Complete horse racing coverage for betting analysis
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

from ai_core.spiders.base_spider import SpiderTarget
from ai_core.spiders.spider_registry import spider_registry
from persistence.models import SpiderData

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HorseRacingDeployment:
    """Deploy horse racing spiders"""

    def __init__(self):
        self.redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

    def create_horse_racing_swarm(self, count: int = 5) -> list:
        """
        Deploy HorseRacingSpider swarm

        Target agents:
        - horse-racing-specialist (primary)
        - betting-analyst
        - value-betting-agent
        - bankroll-manager-agent
        """
        SpiderClass = spider_registry.get_spider_class('horse_racing')
        if not SpiderClass:
            logger.error("HorseRacingSpider not found in registry!")
            logger.info("Available spiders: " + ", ".join(spider_registry.list_available_spiders()))
            return []

        # Horse racing data sources
        targets = [
            SpiderTarget("https://www.reddit.com/r/horseracing/", rate_limit=2.0, priority=1),
        ]

        # Target agents for horse racing intelligence
        subscribers = [
            "horse-racing-specialist",
            "betting-analyst",
            "value-betting-agent",
            "bankroll-manager-agent",
        ]

        spiders = []
        for i in range(count):
            spider = SpiderClass(
                spider_id=f"horse_racing_{i+1:03d}",
                targets=targets,
                subscribers=subscribers,
                redis_config=self.redis_config
            )
            spiders.append(spider)

        logger.info(f"✅ Created {len(spiders)} Horse Racing Spiders")
        logger.info(f"   Targeting {len(targets)} sources")
        logger.info(f"   Feeding {len(subscribers)} betting agents")
        return spiders

    async def deploy(self, duration_minutes: int = 60):
        """
        Deploy horse racing spider swarm

        Args:
            duration_minutes: How long to run (default 60 minutes)
        """
        logger.info("=" * 80)
        logger.info("HORSE RACING SPIDER DEPLOYMENT")
        logger.info("=" * 80)
        logger.info(f"🐎 Target: Horse Racing Betting Intelligence")
        logger.info(f"📈 Expected: 1,000+ entries/day")
        logger.info("=" * 80)

        # Check initial state
        initial_count = await asyncio.get_event_loop().run_in_executor(
            None, SpiderData.objects.count
        )
        logger.info(f"📊 Initial SpiderData count: {initial_count:,}")

        # Create swarm
        logger.info("\n🕷️  Creating horse racing spider swarm...")
        spiders = self.create_horse_racing_swarm(count=5)

        if not spiders:
            logger.error("❌ Failed to create spiders!")
            return False

        logger.info(f"\n✅ Deployed {len(spiders)} spiders")
        logger.info(f"⏱️  Runtime: {duration_minutes} minutes")
        logger.info(f"🎯 Target data: 500-1,000 racing intelligence entries")
        logger.info("\n🚀 Starting spiders... (Press Ctrl+C to stop early)\n")

        try:
            # Start all spiders
            spider_tasks = [asyncio.create_task(spider.start()) for spider in spiders]

            # Run for duration
            duration_seconds = duration_minutes * 60
            await asyncio.sleep(duration_seconds)

            logger.info("\n⏰ Time limit reached, stopping spiders...")

            # Stop gracefully
            for spider in spiders:
                await spider.stop()

            # Cancel tasks
            for task in spider_tasks:
                task.cancel()

            await asyncio.gather(*spider_tasks, return_exceptions=True)

        except KeyboardInterrupt:
            logger.info("\n🛑 Interrupted by user, stopping spiders...")
            for spider in spiders:
                await spider.stop()

        # Give database time to catch up
        await asyncio.sleep(2)

        # Results
        logger.info("\n" + "=" * 80)
        logger.info("DEPLOYMENT RESULTS")
        logger.info("=" * 80)

        final_count = await asyncio.get_event_loop().run_in_executor(
            None, SpiderData.objects.count
        )
        new_entries = final_count - initial_count

        logger.info(f"📊 Final SpiderData count: {final_count:,}")
        logger.info(f"✨ New entries collected: {new_entries:,}")

        if new_entries > 0:
            logger.info(f"\n✅ SUCCESS! Collected {new_entries} horse racing data points")

            # Show breakdown
            def get_breakdown():
                from django.db.models import Count
                return list(SpiderData.objects.filter(
                    spider_name__contains='horse_racing'
                ).values('spider_name').annotate(
                    count=Count('spider_name')
                ).order_by('-count')[:10])

            breakdown = await asyncio.get_event_loop().run_in_executor(None, get_breakdown)

            if breakdown:
                logger.info(f"\n📋 Horse Racing Data:")
                for item in breakdown:
                    logger.info(f"   • {item['spider_name']}: {item['count']} entries")

            logger.info(f"\n🎯 Next Steps:")
            logger.info(f"   1. Create 'horse-racing-specialist' agent if not exists")
            logger.info(f"   2. Monitor betting recommendations for horse racing insights")
            logger.info(f"   3. Connect to odds aggregators for value betting")

            return True
        else:
            logger.warning(f"\n⚠️  No new entries collected!")
            logger.warning(f"   Spiders may need more time or check Reddit API credentials")
            return False


async def main():
    """Main execution"""
    import sys

    duration = 60  # Default 60 minutes
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
            logger.info(f"Custom runtime: {duration} minutes")
        except ValueError:
            logger.error("Invalid runtime argument, using default 60 minutes")

    deployment = HorseRacingDeployment()

    try:
        success = await deployment.deploy(duration_minutes=duration)

        if success:
            logger.info("\n" + "🐎" * 40)
            logger.info("HORSE RACING DEPLOYMENT SUCCESSFUL!")
            logger.info("Horse racing betting intelligence now operational")
            logger.info("🐎" * 40)
            sys.exit(0)
        else:
            logger.error("\n⚠️  DEPLOYMENT INCOMPLETE")
            sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Deployment failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
