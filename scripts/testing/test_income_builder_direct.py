#!/usr/bin/env python
"""
Test Income Builder Directly
"""

import os
import sys
import django
import asyncio

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from intelligence.income_builder import income_builder, UserProfile, SkillLevel

async def test_income_builder():
    """Test income builder directly"""
    print("\n" + "="*60)
    print("Testing Income Builder Direct Analysis")
    print("="*60 + "\n")

    # Create test profile
    profile = UserProfile(
        id='test_user',
        current_balance=0.0,
        skills=['python', 'ai', 'automation', 'data analysis'],
        skill_level=SkillLevel.INTERMEDIATE,
        available_hours_per_week=20
    )

    print(f"Profile: {profile.id}")
    print(f"Skills: {', '.join(profile.skills)}")
    print(f"Level: {profile.skill_level.value}")
    print()

    # Analyze opportunities
    print("Analyzing opportunities...")
    analysis = await income_builder.analyze_user_potential(profile)

    print(f"\n✅ Analysis complete!")
    print(f"Top opportunities: {len(analysis.get('top_opportunities', []))} found")

    opportunities = analysis.get('top_opportunities', [])
    if opportunities:
        print("\nFirst 3 opportunities:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"\n{i}. {opp.get('title', 'Unknown')}")
            print(f"   Stream: {opp.get('stream_type', 'Unknown')}")
            print(f"   Score: {opp.get('score', 0):.2f}")
            print(f"   Potential: {opp.get('potential_monthly', 'Unknown')}")
            print(f"   Time to income: {opp.get('time_to_income', 'Unknown')}")
            if opp.get('match_reasons'):
                print(f"   Match reasons: {', '.join(opp['match_reasons'][:2])}")
    else:
        print("\n❌ No opportunities returned!")
        print("   The income_builder.analyze_user_potential() is returning empty")

    # Check earnings projection
    if analysis.get('earnings_projection'):
        print(f"\n💰 Earnings projection:")
        proj = analysis['earnings_projection']
        print(f"   Week 1: ${proj.get('week_1', 0):.2f}")
        print(f"   Month 1: ${proj.get('month_1', 0):.2f}")
        print(f"   Month 3: ${proj.get('month_3', 0):.2f}")

    return len(opportunities) > 0

if __name__ == "__main__":
    success = asyncio.run(test_income_builder())
    sys.exit(0 if success else 1)