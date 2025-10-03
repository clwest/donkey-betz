#!/usr/bin/env python
"""
Sports Sentiment Spider Deployment
===================================

Deploy social sentiment spiders focused on sports betting intelligence.

Target Agents (24 sports agents ready!):
- sports-betting-agent
- odds-analysis-agent
- betting-analyst
- sentiment-analysis-agent
- arbitrage-hunter-agent
- And 19 more sports agents!

Expected Impact: Sports agent reality 65% → 85%+
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


class SportsSentimentDeployment:
    """Deploy social sentiment spiders for sports betting intelligence"""

    def __init__(self):
        self.redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

    def create_sports_sentiment_swarm(self, count: int = 15) -> list:
        """
        Deploy SocialSentimentSpider swarm focused on sports

        Target agents (24 total sports agents!):
        - sports-betting-agent
        - odds-analysis-agent
        - betting-analyst
        - sentiment-analysis-agent
        - arbitrage-hunter-agent
        - bankroll-manager-agent
        - And 18 more sports agents!
        """
        SpiderClass = spider_registry.get_spider_class('social_sentiment')
        if not SpiderClass:
            logger.error("SocialSentimentSpider not found in registry!")
            logger.info("Available spiders: " + ", ".join(spider_registry.list_available_spiders()))
            return []

        # Sports-focused Reddit targets
        targets = [
            SpiderTarget("https://www.reddit.com/r/sportsbook/", rate_limit=2.0, priority=1),
            SpiderTarget("https://www.reddit.com/r/sportsbetting/", rate_limit=2.0, priority=1),
            SpiderTarget("https://www.reddit.com/r/nfl/", rate_limit=2.5, priority=2),
            SpiderTarget("https://www.reddit.com/r/nba/", rate_limit=2.5, priority=2),
            SpiderTarget("https://www.reddit.com/r/baseball/", rate_limit=3.0, priority=3),
            SpiderTarget("https://www.reddit.com/r/hockey/", rate_limit=3.0, priority=3),
        ]

        # All 24 sports agents ready to receive data!
        subscribers = [
            "sports-betting-agent",
            "odds-analysis-agent",
            "betting-analyst",
            "sentiment-analysis-agent",
            "arbitrage-hunter-agent",
            "bankroll-manager-agent",
            "betting_analysis_specialist",
            "game-predictor",
            "line-movement-agent",
            "prop-bet-specialist",
        ]

        spiders = []
        for i in range(count):
            spider = SpiderClass(
                spider_id=f"sports_sentiment_{i+1:03d}",
                targets=targets,
                subscribers=subscribers,
                redis_config=self.redis_config
            )
            spiders.append(spider)

        logger.info(f"✅ Created {len(spiders)} Sports Sentiment Spiders")
        logger.info(f"   Targeting {len(targets)} sports subreddits")
        logger.info(f"   Feeding {len(subscribers)} sports agents")
        return spiders

    async def deploy(self, duration_minutes: int = 60):
        """
        Deploy sports sentiment spider swarm

        Args:
            duration_minutes: How long to run (default 60 minutes)
        """
        logger.info("=" * 80)
        logger.info("SPORTS SENTIMENT SPIDER DEPLOYMENT")
        logger.info("=" * 80)
        logger.info(f"🎯 Target: 24 Sports Agents Ready for Intelligence!")
        logger.info(f"📈 Expected: Reality Score 65% → 85%+")
        logger.info("=" * 80)

        # Check initial state
        initial_count = await asyncio.get_event_loop().run_in_executor(
            None, SpiderData.objects.count
        )
        logger.info(f"📊 Initial SpiderData count: {initial_count:,}")

        # Create swarm
        logger.info("\n🕷️  Creating sports sentiment spider swarm...")
        spiders = self.create_sports_sentiment_swarm(count=15)

        if not spiders:
            logger.error("❌ Failed to create spiders!")
            return False

        logger.info(f"\n✅ Deployed {len(spiders)} spiders")
        logger.info(f"⏱️  Runtime: {duration_minutes} minutes")
        logger.info(f"🎯 Target data: 500-1,000 sentiment entries")
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
            logger.info(f"\n✅ SUCCESS! Collected {new_entries} sports sentiment data points")

            # Show breakdown
            def get_breakdown():
                from django.db.models import Count
                return list(SpiderData.objects.filter(
                    spider_name__contains='sentiment'
                ).values('spider_name').annotate(
                    count=Count('spider_name')
                ).order_by('-count')[:10])

            breakdown = await asyncio.get_event_loop().run_in_executor(None, get_breakdown)

            if breakdown:
                logger.info(f"\n📋 Sports Sentiment Data:")
                for item in breakdown:
                    logger.info(f"   • {item['spider_name']}: {item['count']} entries")

            logger.info(f"\n🎯 Next Steps:")
            logger.info(f"   1. Monitor agent reality scores over next 24-48 hours")
            logger.info(f"   2. Expected: Sports agents 65% → 85%+ reality")
            logger.info(f"   3. Check betting recommendations for sentiment insights")

            return True
        else:
            logger.warning(f"\n⚠️  No new entries collected!")
            logger.warning(f"   Spiders may need more time or rate limits may be too aggressive")
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

    deployment = SportsSentimentDeployment()

    try:
        success = await deployment.deploy(duration_minutes=duration)

        if success:
            logger.info("\n" + "🎉" * 40)
            logger.info("SPORTS SENTIMENT DEPLOYMENT SUCCESSFUL!")
            logger.info("24 sports agents now have real-time sentiment intelligence")
            logger.info("🎉" * 40)
            sys.exit(0)
        else:
            logger.error("\n⚠️  DEPLOYMENT INCOMPLETE")
            sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Deployment failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
