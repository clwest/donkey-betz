#!/usr/bin/env python
"""
Deploy Legal Spiders
====================

Test and deploy the 4 legal spiders:
1. CourtListener - Free legal opinions API
2. Justia - Legal news and case summaries
3. FindLaw - Legal blogs and articles
4. LII - Supreme Court opinions and U.S. Code

Then route data to legal agents:
- legal-doc-drafter
- legal-document-drafter
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_core.spiders.spider_registry import SpiderRegistry
from persistence.models import SpiderData
from django.db import transaction
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create registry instance
registry = SpiderRegistry()


def test_spider(spider_name: str) -> tuple:
    """
    Test a spider and return results

    Returns:
        (success: bool, count: int, sample_data: dict)
    """
    try:
        logger.info(f"\n{'='*80}\nTesting {spider_name} spider\n{'='*80}")

        spider_class = registry.get_spider_class(spider_name)
        if not spider_class:
            logger.error(f"Spider {spider_name} not found in registry!")
            return False, 0, None

        spider = spider_class()
        data = spider.fetch_data(max_results=10)  # Test with small batch

        if data:
            logger.info(f"✅ {spider_name}: Fetched {len(data)} items")
            logger.info(f"   Sample: {data[0].get('title', 'N/A')[:80]}...")
            return True, len(data), data[0]
        else:
            logger.warning(f"⚠️  {spider_name}: No data fetched")
            return False, 0, None

    except Exception as e:
        logger.error(f"❌ {spider_name}: Error - {e}")
        return False, 0, None


def deploy_legal_spiders():
    """Deploy all 4 legal spiders and route data to legal agents"""

    print("=" * 80)
    print("LEGAL SPIDERS DEPLOYMENT")
    print("=" * 80)

    spiders_to_test = ['courtlistener', 'justia', 'findlaw', 'lii']
    results = {}

    # Test each spider
    for spider_name in spiders_to_test:
        success, count, sample = test_spider(spider_name)
        results[spider_name] = {'success': success, 'count': count, 'sample': sample}

    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print("=" * 80)

    successful_spiders = [name for name, res in results.items() if res['success']]
    failed_spiders = [name for name, res in results.items() if not res['success']]

    print(f"\n✅ Successful: {len(successful_spiders)}/{len(spiders_to_test)}")
    for name in successful_spiders:
        print(f"   - {name}: {results[name]['count']} items")

    if failed_spiders:
        print(f"\n❌ Failed: {len(failed_spiders)}")
        for name in failed_spiders:
            print(f"   - {name}")

    if not successful_spiders:
        print("\n⚠️  No spiders succeeded. Deployment aborted.")
        return

    # Ask for full deployment
    response = input("\n\nDeploy legal spiders with full data collection? (yes/no): ").strip().lower()

    if response != 'yes':
        print("\n❌ Deployment cancelled")
        return

    # Deploy with full collection
    print("\n" + "=" * 80)
    print("DEPLOYING LEGAL SPIDERS - FULL COLLECTION")
    print("=" * 80)

    total_collected = 0
    legal_agents = [
        'legal-doc-drafter',
        'legal-document-drafter',
        'contract-analyzer',
        'legal-research-specialist',
        'compliance-advisor',
        'litigation-strategist'
    ]

    with transaction.atomic():
        for spider_name in successful_spiders:
            try:
                logger.info(f"\nDeploying {spider_name} spider (50 items)...")

                spider_class = registry.get_spider_class(spider_name)
                spider = spider_class()
                data = spider.fetch_data(max_results=50)

                # Save data with routing to legal agents
                for item in data:
                    SpiderData.objects.create(
                        spider_name=spider_name,
                        title=item.get('title', 'Untitled'),
                        source_url=item.get('url', ''),
                        source_platform='other',
                        data_type=item.get('data_type', 'legal_content'),
                        content=item.get('summary', item.get('description', '')),
                        structured_data=item,
                        routed_to_agents=legal_agents,
                        tags=item.get('tags', [])
                    )

                total_collected += len(data)
                logger.info(f"   ✅ Saved {len(data)} items from {spider_name}")

            except Exception as e:
                logger.error(f"   ❌ Error deploying {spider_name}: {e}")
                continue

    print(f"\n{'='*80}")
    print("DEPLOYMENT COMPLETE")
    print("=" * 80)
    print(f"\n📊 Statistics:")
    print(f"   Total items collected: {total_collected}")
    print(f"   Spiders deployed: {len(successful_spiders)}")
    print(f"   Legal agents receiving data: {len(legal_agents)}")

    # Verify legal agents have data
    from core.models.agents_registry import UnifiedAgentTemplate
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT unnest(routed_to_agents) as agent_name
            FROM persistence_spiderdata
            WHERE routed_to_agents IS NOT NULL AND routed_to_agents != '{}'
        """)
        agents_with_data = {row[0] for row in cursor.fetchall()}

    legal_agents_with_data = [a for a in legal_agents if a in agents_with_data]

    print(f"\n✅ Legal agents with data: {len(legal_agents_with_data)}/{len(legal_agents)}")
    for agent in legal_agents_with_data:
        count = SpiderData.objects.filter(routed_to_agents__contains=[agent]).count()
        print(f"   - {agent}: {count:,} entries")

    # Final coverage
    total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
    total_with_data = len(agents_with_data)

    print(f"\n📈 Overall System Coverage:")
    print(f"   Agents with data: {total_with_data} / {total_agents} ({total_with_data/total_agents*100:.1f}%)")


if __name__ == '__main__':
    deploy_legal_spiders()
