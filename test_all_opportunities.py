#!/usr/bin/env python
"""
Test that all 8 opportunities are returned by Income Builder
"""

import os
import sys
import django
import asyncio

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from intelligence.income_builder import AIIncomeBuilder, UserProfile, SkillLevel


async def test_all_opportunities():
    """Test that all opportunities are returned"""

    print("\n" + "="*80)
    print("📋 TESTING INCOME BUILDER OPPORTUNITIES")
    print("="*80 + "\n")

    # Create Income Builder
    builder = AIIncomeBuilder()

    # Check opportunities list
    print(f"✅ Total opportunities available: {len(builder.opportunities)}")
    print("\nAll opportunities:")
    for i, opp in enumerate(builder.opportunities, 1):
        print(f"  {i}. {opp.title} ({opp.stream_type.value})")

    # Test with user profile
    print("\n📊 Testing analyze_user_potential...")

    user_profile = UserProfile(
        id="test_user",
        current_balance=0.0,
        skills=["writing", "research"],
        skill_level=SkillLevel.BEGINNER,
        available_hours_per_week=10,
        interests=["technology", "education"]
    )

    analysis = await builder.analyze_user_potential(user_profile)

    opportunities_returned = len(analysis.get("top_opportunities", []))
    print(f"\n✅ Opportunities returned: {opportunities_returned}")

    if opportunities_returned == len(builder.opportunities):
        print("🎉 SUCCESS: All 8 opportunities are being returned!")
    else:
        print(f"⚠️ WARNING: Only {opportunities_returned} of {len(builder.opportunities)} opportunities returned")

    print("\nOpportunities returned (sorted by score):")
    for i, opp in enumerate(analysis["top_opportunities"], 1):
        print(f"  {i}. {opp['title']} - Score: {opp['score']:.2f}")

    return opportunities_returned == len(builder.opportunities)


if __name__ == "__main__":
    result = asyncio.run(test_all_opportunities())

    if result:
        print("\n✅ All opportunities are now available in Income Builder!")
    else:
        print("\n❌ Some opportunities are still missing")