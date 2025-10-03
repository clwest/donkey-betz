#!/usr/bin/env python
"""
Deploy Medium + Gumroad Spiders (Working Implementations)

These are the only content spiders with concrete implementations ready.
"""
import os
import sys
import asyncio
import logging

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


async def deploy_working_content_spiders(duration_minutes=30):
    """Deploy Medium + Gumroad spiders (the only working implementations)"""

    print("=" * 80)
    print("🚀 CONTENT SPIDER DEPLOYMENT (Medium + Gumroad)")
    print("=" * 80)
    print(f"\n📊 Configuration:")
    print(f"   Duration: {duration_minutes} minutes")
    print(f"   Spiders: Medium (3), Gumroad (3)")
    print(f"   Target agents: content-creator, content-agent, ai-content-studio")

    redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}
    initial_count = await sync_to_async(SpiderData.objects.count)()

    # Medium spiders
    medium_class = spider_registry.get_spider_class('medium')
    gumroad_class = spider_registry.get_spider_class('gumroad')

    all_spiders = []

    # Deploy Medium spiders
    if medium_class:
        medium_targets = [
            SpiderTarget("https://medium.com/tag/technology", rate_limit=3.0),
            SpiderTarget("https://medium.com/tag/startup", rate_limit=3.0),
            SpiderTarget("https://medium.com/tag/ai", rate_limit=3.0),
        ]
        medium_agents = ['content-creator', 'content-agent', 'ai-content-studio']

        for i in range(3):
            import time
            spider = medium_class(
                spider_id=f"medium_{i+1:03d}_{int(time.time())}",
                targets=medium_targets,
                subscribers=medium_agents,
                redis_config=redis_config
            )
            all_spiders.append(spider)
        logger.info("✅ Deployed 3 Medium spiders")

    # Deploy Gumroad spiders
    if gumroad_class:
        gumroad_targets = [
            SpiderTarget("https://gumroad.com/discover", rate_limit=3.0),
        ]
        # Use actual agent names from database (with hyphens)
        gumroad_agents = ['content-creator', 'content-agent', 'ai-content-studio']

        for i in range(3):
            import time
            spider = gumroad_class(
                spider_id=f"gumroad_{i+1:03d}_{int(time.time())}",
                targets=gumroad_targets,
                subscribers=gumroad_agents,
                redis_config=redis_config
            )
            all_spiders.append(spider)
        logger.info("✅ Deployed 3 Gumroad spiders")

    print(f"\n✅ Total spiders deployed: {len(all_spiders)}")

    # Start spiders
    print(f"\n🚀 Starting spiders for {duration_minutes} minutes...")

    try:
        spider_tasks = [asyncio.create_task(spider.start()) for spider in all_spiders]
        await asyncio.sleep(duration_minutes * 60)

        logger.info("\n⏰ Time limit reached, stopping spiders...")
        for spider in all_spiders:
            await spider.stop()
        for task in spider_tasks:
            task.cancel()
        await asyncio.gather(*spider_tasks, return_exceptions=True)

    except KeyboardInterrupt:
        logger.info("\n⚠️ Interrupted, stopping spiders...")
        for spider in all_spiders:
            await spider.stop()
        for task in spider_tasks:
            task.cancel()
        await asyncio.gather(*spider_tasks, return_exceptions=True)

    # Final stats
    final_count = await sync_to_async(SpiderData.objects.count)()
    total_collected = final_count - initial_count

    print("\n" + "=" * 80)
    print("📊 DEPLOYMENT COMPLETE")
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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('duration', type=int, default=30, nargs='?', help='Duration in minutes')
    args = parser.parse_args()

    asyncio.run(deploy_working_content_spiders(args.duration))
