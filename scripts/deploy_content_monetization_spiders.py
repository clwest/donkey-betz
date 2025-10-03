#!/usr/bin/env python
"""
Phase 2: Content Monetization Spider Deployment
===============================================

Deploy content platform spiders to feed content agents:
- Medium, Gumroad, Substack, Patreon, Ko-fi

Target agents: content-creator, content-agent, ai-content-studio, etc.
"""

import os
import sys
import time
import asyncio
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from ai_core.spiders.base_spider import SpiderTarget
from ai_core.spiders.spider_registry import spider_registry
from persistence.models import SpiderData
from asgiref.sync import sync_to_async

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def deploy_content_spiders(count_per_platform=4, duration_minutes=120):
    """Deploy Phase 2 content monetization spiders"""

    print("=" * 80)
    print("🚀 PHASE 2: CONTENT MONETIZATION SPIDER DEPLOYMENT")
    print("=" * 80)
    print(f"\n📊 Configuration:")
    print(f"   Spiders per platform: {count_per_platform}")
    print(f"   Duration: {duration_minutes} minutes")
    print(f"   Platforms: Medium, Gumroad, Substack, Patreon, Ko-fi")

    redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}
    initial_count = await sync_to_async(SpiderData.objects.count)()

    # Platform configurations
    platforms = {
        'medium': {
            'targets': [
                SpiderTarget("https://medium.com/tag/technology", rate_limit=3.0),
                SpiderTarget("https://medium.com/tag/startup", rate_limit=3.0),
                SpiderTarget("https://medium.com/tag/ai", rate_limit=3.0),
            ],
            'agents': ['content-creator', 'content-agent', 'ai-content-studio']
        },
        'gumroad': {
            'targets': [
                SpiderTarget("https://gumroad.com/discover", rate_limit=3.0),
            ],
            'agents': ['content-creator', 'digital_product_creator']
        },
        'substack': {
            'targets': [
                SpiderTarget("https://substack.com/discover", rate_limit=3.0),
            ],
            'agents': ['content-creator', 'content-strategy-agent']
        },
        'patreon': {
            'targets': [
                SpiderTarget("https://www.patreon.com/explore", rate_limit=3.0),
            ],
            'agents': ['content-creator', 'creator_economy_expert']
        },
        'kofi': {
            'targets': [
                SpiderTarget("https://ko-fi.com/explore", rate_limit=3.0),
            ],
            'agents': ['content-creator']
        },
    }

    # Deploy spiders
    all_spiders = []
    for platform, config in platforms.items():
        spider_class = spider_registry.get_spider_class(platform)
        if not spider_class:
            logger.warning(f"Spider for {platform} not found, skipping")
            continue

        for i in range(count_per_platform):
            spider_id = f"{platform}_content_{i+1:03d}_{int(time.time())}"
            spider = spider_class(
                spider_id=spider_id,
                targets=config['targets'],
                subscribers=config['agents'],
                redis_config=redis_config
            )
            all_spiders.append(spider)

        logger.info(f"✅ Deployed {count_per_platform} {platform} spiders")

    print(f"\n✅ Total spiders deployed: {len(all_spiders)}")
    print(f"\n🎯 Target Agents for Content Learning:")
    print(f"   • content-creator")
    print(f"   • content-agent")
    print(f"   • ai-content-studio")
    print(f"   • content-strategy-agent")
    print(f"   • digital_product_creator")

    # Start all spiders
    print(f"\n🚀 Starting all spiders for {duration_minutes} minutes...")
    print("   Press Ctrl+C to stop early\n")

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
        logger.info("\n⚠️ Interrupted by user, stopping spiders...")
        for spider in all_spiders:
            await spider.stop()
        for task in spider_tasks:
            task.cancel()
        await asyncio.gather(*spider_tasks, return_exceptions=True)

    # Final stats
    final_count = await sync_to_async(SpiderData.objects.count)()
    total_collected = final_count - initial_count

    print("\n" + "=" * 80)
    print("📊 PHASE 2 COMPLETE")
    print("=" * 80)
    print(f"   New entries: {total_collected}")
    print(f"   Rate: {total_collected / max(duration_minutes, 1):.1f} entries/min")

    from core.models_unified_system import UserAgentLearning

    @sync_to_async
    def get_content_learning():
        return UserAgentLearning.objects.filter(
            learning_source__startswith='spider:',
            agent_name__icontains='content'
        ).count()

    content_learning = await get_content_learning()
    print(f"   🧠 Content learning entries: {content_learning}")

    print("\n✅ Content agents now learning from monetization platforms!")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('duration', type=int, help='Duration in minutes')
    parser.add_argument('--count', type=int, default=4)
    args = parser.parse_args()

    asyncio.run(deploy_content_spiders(args.count, args.duration))
