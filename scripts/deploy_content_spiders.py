#!/usr/bin/env python
"""
Deploy Phase 2: Content Monetization Spiders
============================================

Deploys content platform spiders to feed intelligence to content agents:
- Medium (articles, partner program)
- Gumroad (digital products)
- Substack (newsletters)
- Patreon (creator monetization)
- Ko-fi (creator tips)

Target Agents:
- content-creator
- content-agent
- content-strategy-agent
- ai-content-studio
- content_creator_agent
- content_workflow_orchestrator
- documentation-writer
- sports_content_creator
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timezone

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from ai_core.spiders.spider_registry import SpiderRegistry
from ai_core.spiders.base_spider import SpiderTarget
from persistence.models import SpiderData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def deploy_content_spiders(count_per_platform: int = 5, duration_minutes: int = 120):
    """
    Deploy content monetization spiders

    Args:
        count_per_platform: Number of spiders to deploy per platform
        duration_minutes: How long to run (0 = run once)
    """

    print("=" * 80)
    print("🚀 PHASE 2: CONTENT MONETIZATION SPIDER DEPLOYMENT")
    print("=" * 80)
    print(f"\n📊 Configuration:")
    print(f"   Spiders per platform: {count_per_platform}")
    print(f"   Duration: {duration_minutes} minutes")
    print(f"   Target: Content agents (8 agents)")
    print(f"   Platforms: Medium, Gumroad, Substack, Patreon, Ko-fi")

    # Get spider registry
    registry = SpiderRegistry()

    # Define content platforms and their targets
    platform_configs = {
        'medium': [
            'https://medium.com/tag/technology',
            'https://medium.com/tag/startup',
            'https://medium.com/tag/ai',
            'https://medium.com/tag/programming',
            'https://medium.com/tag/business',
        ],
        'gumroad': [
            'https://gumroad.com/discover?query=template',
            'https://gumroad.com/discover?query=course',
            'https://gumroad.com/discover?query=ebook',
            'https://gumroad.com/discover?query=design',
            'https://gumroad.com/discover?query=software',
        ],
        'substack': [
            'https://substack.com/discover/technology',
            'https://substack.com/discover/business',
            'https://substack.com/discover/startup',
            'https://substack.com/discover/ai',
            'https://substack.com/discover/newsletter',
        ],
        'patreon': [
            'https://www.patreon.com/explore/technology',
            'https://www.patreon.com/explore/education',
            'https://www.patreon.com/explore/business',
            'https://www.patreon.com/explore/writing',
            'https://www.patreon.com/explore/podcasts',
        ],
        'kofi': [
            'https://ko-fi.com/explore/art',
            'https://ko-fi.com/explore/writing',
            'https://ko-fi.com/explore/education',
            'https://ko-fi.com/explore/technology',
            'https://ko-fi.com/explore/business',
        ],
    }

    # Check initial state
    initial_count = SpiderData.objects.count()
    print(f"\n📈 Initial State:")
    print(f"   Total spider data entries: {initial_count}")

    # Deploy spiders
    deployed_spiders = []

    for platform, urls in platform_configs.items():
        print(f"\n🕷️ Deploying {platform.upper()} spiders...")

        for i in range(count_per_platform):
            spider_id = f"{platform}_content_{i+1}_{int(datetime.now().timestamp())}"

            # Create targets for this spider
            targets = [
                SpiderTarget(
                    url=urls[i % len(urls)],  # Rotate through URLs
                    crawl_depth=2,
                    pattern_match=None,
                    frequency_seconds=3600  # Check hourly
                )
            ]

            # Get spider class
            spider_class = registry.get(platform)
            if not spider_class:
                logger.warning(f"Spider for {platform} not found, skipping")
                continue

            # Create spider instance
            redis_config = {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', 6379)),
                'db': 0
            }

            spider = spider_class(
                spider_id=spider_id,
                targets=targets,
                subscribers=[],  # Will use agent routing from base spider
                redis_config=redis_config
            )

            deployed_spiders.append((platform, spider))
            print(f"   ✅ Deployed: {spider_id}")

    print(f"\n✅ Total spiders deployed: {len(deployed_spiders)}")

    # Run spiders
    if duration_minutes > 0:
        print(f"\n⏱️ Running spiders for {duration_minutes} minutes...")
        print("   (This will collect content monetization intelligence)")

        start_time = datetime.now(timezone.utc)
        end_time = start_time.timestamp() + (duration_minutes * 60)

        iteration = 0
        while datetime.now(timezone.utc).timestamp() < end_time:
            iteration += 1
            elapsed = int((datetime.now(timezone.utc) - start_time).total_seconds() / 60)

            print(f"\n🔄 Iteration {iteration} ({elapsed}/{duration_minutes} min elapsed)")

            # Run each spider
            for platform, spider in deployed_spiders:
                try:
                    # Run spider (it will handle data collection and persistence)
                    await spider.run()
                except Exception as e:
                    logger.error(f"Error running {platform} spider: {e}")

            # Show progress
            current_count = SpiderData.objects.count()
            new_entries = current_count - initial_count
            print(f"   📊 New entries collected: {new_entries}")

            # Check learning activity
            from core.models_unified_system import UserAgentLearning
            content_learning = UserAgentLearning.objects.filter(
                learning_source__startswith='spider:',
                learning_domain='content_creation'
            ).count()
            print(f"   🧠 Content learning entries: {content_learning}")

            # Sleep between iterations
            if datetime.now(timezone.utc).timestamp() < end_time:
                await asyncio.sleep(60)  # Wait 1 minute between iterations

    else:
        # Single run
        print(f"\n⏱️ Single run mode...")
        for platform, spider in deployed_spiders:
            try:
                await spider.run()
                print(f"   ✅ {platform} spider complete")
            except Exception as e:
                logger.error(f"Error running {platform} spider: {e}")

    # Final statistics
    final_count = SpiderData.objects.count()
    total_collected = final_count - initial_count

    print("\n" + "=" * 80)
    print("📊 DEPLOYMENT COMPLETE")
    print("=" * 80)
    print(f"\n   Initial entries: {initial_count}")
    print(f"   Final entries: {final_count}")
    print(f"   New entries collected: {total_collected}")
    print(f"   Collection rate: {total_collected / max(duration_minutes, 1):.1f} entries/min")

    # Check learning
    from core.models_unified_system import UserAgentLearning
    content_learning = UserAgentLearning.objects.filter(
        learning_source__startswith='spider:'
    ).count()
    print(f"\n   🧠 Total learning entries from spiders: {content_learning}")

    # Show content-specific learning
    content_agents = ['content-creator', 'content-agent', 'content-strategy-agent',
                     'ai-content-studio', 'content_creator_agent', 'documentation-writer']

    for agent in content_agents:
        agent_learning = UserAgentLearning.objects.filter(
            agent_name=agent,
            learning_source__startswith='spider:'
        ).count()
        if agent_learning > 0:
            print(f"   - {agent}: {agent_learning} learning entries")

    print("\n✅ Phase 2 deployment complete!")
    print("   Content agents are now learning from monetization platforms!")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Deploy Phase 2 Content Spiders')
    parser.add_argument('duration', type=int, help='Duration in minutes (0 for single run)')
    parser.add_argument('--count', type=int, default=5, help='Spiders per platform (default: 5)')

    args = parser.parse_args()

    asyncio.run(deploy_content_spiders(args.count, args.duration))
