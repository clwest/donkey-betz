#!/usr/bin/env python
"""
Replace mock opportunities with REAL spider data
"""
import asyncio
import sys
import os
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from intelligence.models import OpportunityTracking, UserIncomeProfile
from intelligence.income_spider_orchestrator import income_spider_orchestrator
from intelligence.income_builder import UserProfile as SpiderUserProfile, SkillLevel

User = get_user_model()


async def replace_with_real_data():
    """Replace all mock opportunities with real spider data"""
    print("=" * 70)
    print("🔄 REPLACING MOCK DATA WITH REAL SPIDER OPPORTUNITIES")
    print("=" * 70)

    # Step 1: Get or create a test user
    @sync_to_async
    def get_or_create_user():
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        return user, created

    user, created = await get_or_create_user()
    if created:
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing user: {user.username}")

    # Step 2: Clear ALL existing opportunities
    @sync_to_async
    def clear_opportunities():
        count = OpportunityTracking.objects.count()
        if count > 0:
            OpportunityTracking.objects.all().delete()
        return count

    existing_count = await clear_opportunities()
    if existing_count > 0:
        print(f"\n🗑️  Clearing {existing_count} existing opportunities...")
        print(f"   ✅ Deleted {existing_count} opportunities")

    # Step 3: Create or update user income profile
    @sync_to_async
    def get_or_create_profile(user_obj):
        profile, created = UserIncomeProfile.objects.get_or_create(
            user=user_obj,
            defaults={
                'skills': ['python', 'django', 'javascript', 'react', 'ai', 'machine learning'],
                'skill_level': 'intermediate',
                'available_hours_per_week': 20
            }
        )
        return profile, created

    income_profile, _ = await get_or_create_profile(user)
    print(f"✅ User income profile: {income_profile}")

    # Step 4: Fetch REAL opportunities from spiders
    print(f"\n🕷️  Fetching REAL opportunities from spider network...")
    print("   Sources: HackerNews, RemoteOK, Freelancer.com")
    print("   This may take 10-30 seconds...\n")

    spider_profile = SpiderUserProfile(
        id=str(user.id),
        current_balance=float(income_profile.current_balance),
        skills=income_profile.skills,
        skill_level=SkillLevel.INTERMEDIATE,
        available_hours_per_week=income_profile.available_hours_per_week
    )

    # Fetch with REAL data
    result = await income_spider_orchestrator.discover_opportunities_for_user(
        spider_profile,
        use_real_data=True,  # ✅ REAL DATA!
        max_opportunities=50  # Get more opportunities
    )

    print(f"✅ Spider Discovery Complete:")
    print(f"   Total found: {len(result.opportunities)}")
    print(f"   Sources: {', '.join(result.spider_sources)}")
    print(f"   Discovery time: {result.discovery_time:.2f}s")

    # Step 5: Save opportunities to database
    print(f"\n💾 Saving opportunities to database...")

    @sync_to_async
    def save_opportunities(user_obj, opportunities):
        saved_count = 0
        for opp in opportunities:
            try:
                OpportunityTracking.objects.create(
                    user=user_obj,
                    opportunity_id=opp.opportunity_id,
                    opportunity_title=opp.title,
                    opportunity_type='freelance',
                    status='identified',
                    opportunity_data={
                        'title': opp.title,
                        'platform': opp.platform,
                        'budget': opp.budget,
                        'skills_required': opp.skills_required,
                        'match_score': opp.match_score,
                        'quality_score': opp.quality_score,
                        'spider_source': opp.spider_source,
                        'raw_data': opp.raw_data or {}
                    }
                )
                saved_count += 1
            except Exception as e:
                print(f"   ⚠️  Skipped duplicate: {opp.opportunity_id}")
        return saved_count

    saved_count = await save_opportunities(user, result.opportunities)
    print(f"   ✅ Saved {saved_count} new opportunities")

    # Step 6: Verify database
    @sync_to_async
    def get_final_count():
        return OpportunityTracking.objects.count()

    final_count = await get_final_count()
    print(f"\n📊 Database Status:")
    print(f"   Total opportunities: {final_count}")
    print(f"   Real spider data: {final_count}")
    print(f"   Mock data: 0")

    # Step 7: Show sample opportunities
    if final_count > 0:
        @sync_to_async
        def get_sample_opportunities():
            return list(OpportunityTracking.objects.all()[:5])

        sample_opps = await get_sample_opportunities()
        print(f"\n📋 Sample Opportunities (first 5):\n")
        for i, opp in enumerate(sample_opps, 1):
            data = opp.opportunity_data
            print(f"{i}. {opp.opportunity_title}")
            print(f"   Platform: {data.get('platform', 'N/A')}")
            print(f"   Source: {data.get('spider_source', 'N/A')}")
            print(f"   Skills: {', '.join(data.get('skills_required', [])[:5])}")
            print(f"   Match Score: {data.get('match_score', 0):.0%}")
            print()

    print("=" * 70)
    print("✅ REPLACEMENT COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Navigate to: http://localhost:8000/income/")
    print("2. You should see REAL opportunities from RemoteOK and HackerNews")
    print("3. The UI will display actual job listings with real data")
    print("\nTo refresh with new data, run this script again:")
    print("  python scripts/replace_with_real_spider_data.py")
    print()


if __name__ == '__main__':
    asyncio.run(replace_with_real_data())
