#!/usr/bin/env python
"""
Quick test to verify spiders fetch REAL data from APIs
"""
import asyncio
import sys
import os
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from intelligence.income_spider_orchestrator import income_spider_orchestrator
from intelligence.income_builder import UserProfile, SkillLevel


async def test_real_spiders():
    """Test that spiders actually fetch real data"""
    print("🕷️ Testing REAL spider network...")
    print("=" * 60)

    # Create test user profile
    test_profile = UserProfile(
        id='test_user',
        current_balance=0.0,
        skills=['python', 'django', 'javascript', 'ai', 'machine learning'],
        skill_level=SkillLevel.INTERMEDIATE,
        available_hours_per_week=20
    )

    print(f"\n📋 Test Profile:")
    print(f"   Skills: {', '.join(test_profile.skills)}")
    print(f"   Level: {test_profile.skill_level.value}")
    print(f"   Hours/week: {test_profile.available_hours_per_week}")

    print(f"\n🌐 Fetching from REAL APIs (HackerNews, RemoteOK, Freelancer)...")
    print("   This may take 10-30 seconds...\n")

    # Fetch real opportunities
    result = await income_spider_orchestrator.discover_opportunities_for_user(
        test_profile,
        use_real_data=True,  # REAL DATA!
        max_opportunities=10
    )

    print("=" * 60)
    print(f"✅ RESULTS:")
    print(f"   Total opportunities found: {len(result.opportunities)}")
    print(f"   Spider sources: {', '.join(result.spider_sources)}")
    print(f"   Discovery time: {result.discovery_time:.2f}s")
    print(f"   Filtered from: {result.filtered_count} total")
    print("=" * 60)

    if result.opportunities:
        print(f"\n📋 Sample Opportunities (first 3):\n")
        for i, opp in enumerate(result.opportunities[:3], 1):
            print(f"{i}. {opp.title}")
            print(f"   Platform: {opp.platform}")
            print(f"   Source: {opp.spider_source}")
            print(f"   Skills: {', '.join(opp.skills_required[:5])}")
            print(f"   Quality Score: {opp.quality_score:.2f}")
            print(f"   URL: {opp.raw_data.get('url', 'N/A') if opp.raw_data else 'N/A'}")
            print()
    else:
        print("\n⚠️  No opportunities found!")
        print("   This could mean:")
        print("   - APIs are rate-limited")
        print("   - No jobs match the profile")
        print("   - Network issues")

    return result


if __name__ == '__main__':
    result = asyncio.run(test_real_spiders())
    sys.exit(0 if result.opportunities else 1)
