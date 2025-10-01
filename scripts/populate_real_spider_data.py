#!/usr/bin/env python
"""
Fetch REAL spider data and populate the database
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


async def populate_real_data():
    """Fetch real spider data and populate database"""
    print("=" * 70)
    print("🕷️  FETCHING REAL SPIDER DATA AND POPULATING DATABASE")
    print("=" * 70)

    # Step 1: Get or create user (sync)
    @sync_to_async
    def setup_user():
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()

        # Get or create income profile
        profile, _ = UserIncomeProfile.objects.get_or_create(
            user=user,
            defaults={
                'skills': ['python', 'django', 'javascript', 'react', 'ai', 'machine learning'],
                'skill_level': 'intermediate',
                'available_hours_per_week': 20
            }
        )
        return user, profile

    user, income_profile = await setup_user()
    print(f"✅ User: {user.username}")
    print(f"✅ Profile: {income_profile.skills}")

    # Step 2: Clear existing opportunities
    @sync_to_async
    def clear_opportunities():
        count = OpportunityTracking.objects.count()
        if count > 0:
            OpportunityTracking.objects.all().delete()
        return count

    cleared = await clear_opportunities()
    if cleared > 0:
        print(f"\n🗑️  Cleared {cleared} old opportunities")

    # Step 3: Fetch REAL opportunities from spiders
    print(f"\n🌐 Fetching REAL opportunities from spider network...")
    print("   This queries live APIs: HackerNews, RemoteOK, Freelancer")
    print("   May take 10-30 seconds...\n")

    spider_profile = SpiderUserProfile(
        id=str(user.id),
        current_balance=float(income_profile.current_balance),
        skills=income_profile.skills,
        skill_level=SkillLevel.INTERMEDIATE,
        available_hours_per_week=income_profile.available_hours_per_week
    )

    result = await income_spider_orchestrator.discover_opportunities_for_user(
        spider_profile,
        use_real_data=True,  # ✅ FETCH REAL DATA
        max_opportunities=50
    )

    print(f"✅ Spider Discovery Complete:")
    print(f"   Total found: {len(result.opportunities)}")
    print(f"   Sources: {', '.join(result.spider_sources)}")
    print(f"   Discovery time: {result.discovery_time:.2f}s\n")

    # Step 4: Save each opportunity to database
    @sync_to_async
    def save_opportunity(user_obj, opp):
        try:
            # Build budget string
            if opp.budget_min and opp.budget_max:
                budget = f"${opp.budget_min:.0f}-${opp.budget_max:.0f}"
            elif opp.estimated_earnings:
                budget = f"${opp.estimated_earnings:.0f}"
            elif opp.hourly_rate:
                budget = f"${opp.hourly_rate:.0f}/hr"
            else:
                budget = "Negotiable"

            tracking = OpportunityTracking.objects.create(
                user=user_obj,
                opportunity_id=opp.id,  # ✅ Fixed: use .id not .opportunity_id
                opportunity_title=opp.title,
                opportunity_type=opp.opportunity_type or 'freelance',
                status='identified',
                opportunity_data={
                    'id': opp.id,
                    'title': opp.title,
                    'description': opp.description[:500] if opp.description else '',
                    'platform': opp.platform,
                    'spider_source': opp.spider_source,
                    'budget': budget,
                    'skills_required': opp.skills_required,
                    'quality_score': opp.quality_score,
                    'experience_level': opp.experience_level,
                    'urgency': opp.urgency,
                    'raw_data': opp.raw_data or {}
                }
            )
            return True, opp.title
        except Exception as e:
            return False, str(e)

    print(f"💾 Saving {len(result.opportunities)} opportunities to database...")
    saved_count = 0

    for opp in result.opportunities:
        success, info = await save_opportunity(user, opp)
        if success:
            saved_count += 1
        else:
            print(f"   ⚠️  Skipped: {info[:50]}")

    print(f"   ✅ Saved {saved_count}/{len(result.opportunities)} opportunities\n")

    # Step 5: Verify and display samples
    @sync_to_async
    def get_stats():
        total = OpportunityTracking.objects.count()
        samples = list(OpportunityTracking.objects.all()[:5])
        return total, samples

    total_count, samples = await get_stats()

    print(f"📊 Database Status:")
    print(f"   Total opportunities in database: {total_count}")
    print(f"   All from REAL spider data: ✅\n")

    if samples:
        print(f"📋 Sample Opportunities:\n")
        for i, opp in enumerate(samples, 1):
            data = opp.opportunity_data
            print(f"{i}. {opp.opportunity_title}")
            print(f"   Platform: {data.get('platform', 'Unknown')}")
            print(f"   Source: {data.get('spider_source', 'Unknown')}")
            skills = data.get('skills_required', [])
            if skills:
                print(f"   Skills: {', '.join(skills[:5])}")
            print(f"   Match: {data.get('match_score', 0):.0%}")
            print()

    print("=" * 70)
    print("✅ REAL SPIDER DATA POPULATED SUCCESSFULLY!")
    print("=" * 70)
    print("\n🎉 Next Steps:")
    print("   1. Navigate to: http://localhost:8000/income/")
    print("   2. You'll see REAL opportunities from RemoteOK & HackerNews")
    print("   3. These are actual job listings fetched from live APIs!")
    print("\n🔄 To refresh with new data, run this script again:")
    print("   python scripts/populate_real_spider_data.py\n")


if __name__ == '__main__':
    asyncio.run(populate_real_data())
