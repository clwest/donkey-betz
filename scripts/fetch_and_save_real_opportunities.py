#!/usr/bin/env python
"""
Synchronous script to fetch real spider data and save to database
"""
import sys
import os

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from intelligence.models import OpportunityTracking, UserIncomeProfile
from intelligence.opportunity_storage import opportunity_storage

User = get_user_model()


def main():
    print("=" * 70)
    print("🔄 REPLACING MOCK DATA WITH REAL SPIDER OPPORTUNITIES")
    print("=" * 70)

    # Step 1: Get existing user
    try:
        user = User.objects.get(username='testuser')
        print(f"✅ Using existing user: {user.username}")
    except User.DoesNotExist:
        # Use make_password to avoid plaintext in code
        from django.contrib.auth.hashers import make_password
        user = User.objects.create(
            username='testuser',
            email='test@example.com',
            password=make_password('test123')  # Test password, not production
        )
        print(f"✅ Created test user: {user.username}")

    # Step 2: Clear ALL existing mock opportunities
    existing_count = OpportunityTracking.objects.count()
    if existing_count > 0:
        print(f"\n🗑️  Clearing {existing_count} existing opportunities...")
        OpportunityTracking.objects.all().delete()
        print(f"   ✅ Deleted {existing_count} opportunities")

    # Step 3: Create or update user income profile
    income_profile, created = UserIncomeProfile.objects.get_or_create(
        user=user,
        defaults={
            'skills': ['python', 'django', 'javascript', 'react', 'ai', 'machine learning'],
            'skill_level': 'intermediate',
            'available_hours_per_week': 20
        }
    )
    print(f"✅ User income profile: {income_profile}")

    # Step 4: Get opportunities from storage (spiders already populated these)
    print(f"\n📥 Fetching real opportunities from opportunity storage...")

    # Get opportunities from the opportunity_storage system
    opportunities = opportunity_storage.get_all_opportunities(limit=100)

    print(f"✅ Found {len(opportunities)} opportunities in storage")

    if len(opportunities) == 0:
        print("\n⚠️  No opportunities in storage!")
        print("   Run the spider test first to populate storage:")
        print("   python test_real_spiders.py")
        return

    # Step 5: Save to database
    print(f"\n💾 Saving opportunities to database...")
    saved_count = 0

    for opp_data in opportunities:
        try:
            OpportunityTracking.objects.create(
                user=user,
                opportunity_id=opp_data.get('opportunity_id', f"opp_{saved_count}"),
                opportunity_title=opp_data.get('title', 'Untitled Opportunity'),
                opportunity_type='freelance',
                status='identified',
                opportunity_data=opp_data  # Store the full opportunity data
            )
            saved_count += 1
        except Exception as e:
            print(f"   ⚠️  Error saving opportunity: {e}")

    print(f"   ✅ Saved {saved_count} new opportunities")

    # Step 6: Verify database
    final_count = OpportunityTracking.objects.count()
    print(f"\n📊 Database Status:")
    print(f"   Total opportunities: {final_count}")
    print(f"   Real spider data: {final_count}")
    print(f"   Mock data: 0")

    # Step 7: Show sample opportunities
    if final_count > 0:
        print(f"\n📋 Sample Opportunities (first 5):\n")
        for i, opp in enumerate(OpportunityTracking.objects.all()[:5], 1):
            data = opp.opportunity_data
            print(f"{i}. {opp.opportunity_title}")
            print(f"   Platform: {data.get('platform', 'N/A')}")
            print(f"   Source: {data.get('spider_source', 'N/A')}")
            skills = data.get('skills_required', [])
            if isinstance(skills, list):
                print(f"   Skills: {', '.join(skills[:5])}")
            print(f"   Match Score: {data.get('match_score', 0):.0%}")
            print()

    print("=" * 70)
    print("✅ REPLACEMENT COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Navigate to: http://localhost:8000/income/")
    print("2. You should see REAL opportunities from RemoteOK and HackerNews")
    print("3. The UI will display actual job listings with real data")
    print("\nTo refresh with new data:")
    print("1. Run: python test_real_spiders.py")
    print("2. Then run: python scripts/fetch_and_save_real_opportunities.py")
    print()


if __name__ == '__main__':
    main()
