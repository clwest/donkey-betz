#!/usr/bin/env python
"""
Test Script: Spider Database Persistence
=========================================

This script tests that spiders can successfully persist data to the SpiderData table.
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

from ai_core.spiders.base_spider import (
    BaseIntelligenceSpider,
    SpiderTarget,
    IntelligenceData,
    AdaptiveSpider
)
from persistence.models import SpiderData
from asgiref.sync import sync_to_async

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_spider_persistence():
    """Test that a spider can persist data to the database"""

    logger.info("=" * 80)
    logger.info("SPIDER PERSISTENCE TEST")
    logger.info("=" * 80)

    # Check initial database state
    initial_count = await sync_to_async(SpiderData.objects.count)()
    logger.info(f"📊 Initial SpiderData count: {initial_count}")

    # Create a test spider
    test_target = SpiderTarget(
        url="https://example.com/test",
        rate_limit=1.0,
        priority=1
    )

    spider = AdaptiveSpider(
        spider_id="test_spider_001",
        targets=[test_target],
        subscribers=["test_agent"],
        redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
    )

    logger.info(f"🕷️  Created test spider: {spider.spider_id}")

    # Create test intelligence data
    test_intelligence = IntelligenceData(
        spider_id="test_spider_001",
        source_url="https://example.com/test",
        data_type="test_data",
        content={
            'title': 'Test Data Entry',
            'description': 'This is a test to verify database persistence',
            'test_field': 'test_value',
            'timestamp': datetime.now(timezone.utc).isoformat()
        },
        metadata={
            'test': True,
            'purpose': 'verify_persistence',
            'version': '1.0'
        },
        quality_score=0.85,
        timestamp=datetime.now(timezone.utc),
        relevance_tags=['test', 'persistence', 'verification'],
        target_agents=['test_agent'],
        target_advisors=[]
    )

    logger.info("📦 Created test intelligence data")
    logger.info(f"   - Data type: {test_intelligence.data_type}")
    logger.info(f"   - Quality score: {test_intelligence.quality_score}")
    logger.info(f"   - Source URL: {test_intelligence.source_url}")

    # Test persistence
    try:
        logger.info("💾 Attempting to persist to database...")
        await spider._persist_to_database(test_intelligence)
        logger.info("✅ Persistence call completed without errors")

    except Exception as e:
        logger.error(f"❌ Persistence failed with error: {e}", exc_info=True)
        return False

    # Wait a moment for async operation to complete
    await asyncio.sleep(1)

    # Verify data was saved
    final_count = await sync_to_async(SpiderData.objects.count)()
    logger.info(f"📊 Final SpiderData count: {final_count}")

    if final_count > initial_count:
        new_entries = final_count - initial_count
        logger.info(f"✅ SUCCESS! {new_entries} new entry(ies) created")

        # Show the new entry
        latest = await sync_to_async(lambda: SpiderData.objects.order_by('-created_at').first())()
        if latest:
            logger.info("\n" + "=" * 80)
            logger.info("LATEST SPIDERDATA ENTRY:")
            logger.info("=" * 80)
            logger.info(f"ID: {latest.id}")
            logger.info(f"Spider Name: {latest.spider_name}")
            logger.info(f"Data Type: {latest.data_type}")
            logger.info(f"Source URL: {latest.source_url}")
            logger.info(f"Source Platform: {latest.source_platform}")
            logger.info(f"Title: {latest.title}")
            logger.info(f"Quality Score: {latest.quality_score}")
            logger.info(f"Is Processed: {latest.is_processed}")
            logger.info(f"Tags: {latest.tags}")
            logger.info(f"Created: {latest.created_at}")
            logger.info("=" * 80)

        return True
    else:
        logger.error(f"❌ FAILED! No new entries created")
        logger.error(f"   Expected: {initial_count + 1}")
        logger.error(f"   Actual: {final_count}")
        return False


async def main():
    """Main test execution"""
    try:
        success = await test_spider_persistence()

        if success:
            logger.info("\n" + "🎉" * 40)
            logger.info("TEST PASSED: Spider persistence is working!")
            logger.info("🎉" * 40)
            sys.exit(0)
        else:
            logger.error("\n" + "💥" * 40)
            logger.error("TEST FAILED: Spider persistence is broken!")
            logger.error("💥" * 40)
            sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Test execution failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
