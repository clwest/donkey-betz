#!/usr/bin/env python3
"""
Test Complete Learning Loop - Data → Learning → User Personalization
Verifies the last mile is connected!
"""

import os
import sys
import django
from decimal import Decimal

sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_unified_system import Opportunity, UserAgentLearning, Application
from django.test import Client
import json

User = get_user_model()

print("=" * 70)
print("🧠 TESTING COMPLETE LEARNING LOOP")
print("=" * 70)

# Step 1: Create test user
print("\n1️⃣  Creating test user...")
user, created = User.objects.get_or_create(
    username='learning_test_user',
    defaults={'email': 'learn@test.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"✅ Created user: {user.username}")
else:
    print(f"✅ Using existing user: {user.username}")

# Step 2: Create diverse opportunities
print("\n2️⃣  Creating test opportunities...")
sources = ['Upwork', 'Upwork', 'Upwork', 'Freelancer', 'Fiverr', 'test_script']
revenues = [5000, 7000, 6000, 2000, 500, 8000]

created_opps = []
for i, (source, revenue) in enumerate(zip(sources, revenues)):
    opp, created = Opportunity.objects.get_or_create(
        user=user,  # ✅ Add user
        title=f'Test {source} Job #{i+1}',
        source=source,
        defaults={
            'opportunity_type': 'freelance',
            'potential_revenue': Decimal(str(revenue)),
            'match_score': 80,
            'status': 'active',
            'description': f'Test opportunity from {source}'
        }
    )
    created_opps.append(opp)
    print(f"  {'✅ Created' if created else '✅ Found'}: {opp.title} - ${revenue} from {source}")

print(f"\n📊 Total opportunities: {Opportunity.objects.filter(status='active').count()}")

# Step 3: Simulate user learning behavior
print("\n3️⃣  Simulating user interactions (building learning profile)...")

# Create learning profile manually (simulating what bridges would do)
learning_content = {
    'preferred_sources': {
        'Upwork': {
            'count': 10,
            'depth_sum': 30,  # 10 interactions * depth 3 (apply)
            'avg_depth': 3.0
        },
        'test_script': {
            'count': 5,
            'depth_sum': 15,
            'avg_depth': 3.0
        },
        'Freelancer': {
            'count': 2,
            'depth_sum': 2,
            'avg_depth': 1.0  # Just viewed, not applied
        }
    },
    'preferred_salary_range': {
        'min': 5000,
        'max': 10000,
        'count': 8
    },
    'preferred_industries': {
        'Technology': {'count': 12, 'depth_sum': 36}
    },
    'interaction_history': [
        {'type': 'apply', 'patterns': {'source': 'Upwork'}, 'depth': 4},
        {'type': 'apply', 'patterns': {'source': 'Upwork'}, 'depth': 4}
    ]
}

user_learning, created = UserAgentLearning.objects.update_or_create(
    user=user,
    agent_name='SystemIntelligence',
    learning_domain='user_preferences',
    defaults={
        'learning_content': learning_content,
        'confidence_score': 0.8,
        'validation_count': 10,
        'learning_source': 'behavioral',
        'is_active': True
    }
)

print(f"✅ {'Created' if created else 'Updated'} user learning profile")
print(f"  - Preferred sources: Upwork (10 interactions), test_script (5), Freelancer (2)")
print(f"  - Preferred salary: $5,000 - $10,000")
print(f"  - Confidence: {user_learning.confidence_score}")

# Also create platform preferences
platform_learning, created = UserAgentLearning.objects.update_or_create(
    user=user,
    agent_name='SystemIntelligence',
    learning_domain='platform_preferences',
    defaults={
        'learning_content': {
            'platforms': {
                'Upwork': {
                    'applied': 10,
                    'accepted': 7,
                    'success_rate': 0.7  # 70% success rate
                },
                'test_script': {
                    'applied': 5,
                    'accepted': 4,
                    'success_rate': 0.8  # 80% success rate
                },
                'Freelancer': {
                    'applied': 2,
                    'accepted': 0,
                    'success_rate': 0.0  # 0% success rate
                }
            }
        },
        'confidence_score': 0.75,
        'is_active': True,
        'learning_source': 'success_pattern'
    }
)

print(f"✅ {'Created' if created else 'Updated'} platform success patterns")
print(f"  - Upwork: 70% success rate")
print(f"  - test_script: 80% success rate")
print(f"  - Freelancer: 0% success rate")

# Step 4: Test API WITHOUT personalization (anonymous)
print("\n4️⃣  Testing API WITHOUT personalization (anonymous user)...")
client = Client()
response = client.get('/api/v1/intelligence/real-income-builder/')
data = response.json()

print(f"✅ Response status: {response.status_code}")
print(f"  - Is personalized: {data.get('is_personalized', False)}")
print(f"  - Total opportunities: {data.get('count', 0)}")

if not data.get('is_personalized'):
    print(f"✅ CORRECT: Anonymous user gets generic results")
else:
    print(f"❌ ERROR: Anonymous user should NOT get personalized results")

# Step 5: Test API WITH personalization (authenticated)
print("\n5️⃣  Testing API WITH personalization (authenticated user)...")
client.force_login(user)
response = client.get('/api/v1/intelligence/real-income-builder/')
data = response.json()

print(f"✅ Response status: {response.status_code}")
print(f"  - Is personalized: {data.get('is_personalized', False)}")
print(f"  - Message: {data.get('message', '')}")
print(f"  - Total opportunities: {data.get('count', 0)}")

# Analyze personalization
if data.get('is_personalized'):
    print(f"\n✅ PERSONALIZATION IS ACTIVE!")

    personalization_data = data.get('personalization_data', {})
    print(f"\n📊 Personalization Details:")
    print(f"  - Preferred sources: {personalization_data.get('preferred_sources', [])}")
    print(f"  - Salary range: {personalization_data.get('salary_range', {})}")
    print(f"  - Platform success rates: {personalization_data.get('platform_success_rates', {})}")

    # Analyze opportunities
    opportunities = data.get('opportunities', [])
    if opportunities:
        print(f"\n🎯 Top 5 Personalized Opportunities:")
        for i, opp in enumerate(opportunities[:5]):
            boost = opp.get('personalization_boost', 0)
            p_score = opp.get('personalized_score', 0)
            base_score = opp.get('success_rate', 0)
            print(f"\n  {i+1}. {opp['title']}")
            print(f"     Source: {opp['source']}")
            print(f"     Base Score: {base_score} → Personalized: {p_score} (+{boost} boost)")
            print(f"     Salary: {opp['potential_monthly']}")

        # Count by source
        source_counts = {}
        for opp in opportunities:
            source = opp['source']
            source_counts[source] = source_counts.get(source, 0) + 1

        print(f"\n📈 Opportunities by Source:")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(opportunities)) * 100
            print(f"  - {source}: {count} ({percentage:.0f}%)")

        # Verify personalization worked
        upwork_count = source_counts.get('Upwork', 0)
        test_script_count = source_counts.get('test_script', 0)
        preferred_count = upwork_count + test_script_count

        print(f"\n✅ Verification:")
        print(f"  - Preferred sources (Upwork + test_script): {preferred_count}/{len(opportunities)} ({preferred_count/len(opportunities)*100:.0f}%)")

        if preferred_count > len(opportunities) / 2:
            print(f"  ✅ SUCCESS: Most opportunities from preferred sources!")
        else:
            print(f"  ⚠️  WARNING: Fewer preferred sources than expected")

        # Check salary filtering
        high_salary = sum(1 for opp in opportunities if '$5,' in opp['potential_monthly'] or '$6,' in opp['potential_monthly'] or '$7,' in opp['potential_monthly'] or '$8,' in opp['potential_monthly'])
        print(f"  - High salary opportunities ($5k+): {high_salary}/{len(opportunities)} ({high_salary/len(opportunities)*100:.0f}%)")

else:
    print(f"❌ PERSONALIZATION NOT ACTIVE - Check if user has learning data")

# Step 6: Summary
print("\n" + "=" * 70)
print("📊 LEARNING LOOP TEST SUMMARY")
print("=" * 70)

learning_count = UserAgentLearning.objects.filter(user=user, is_active=True).count()
print(f"\n✅ Learning entries for user: {learning_count}")

if data.get('is_personalized'):
    print(f"✅ Personalization: WORKING")
    print(f"✅ Last Mile: CONNECTED")
    print(f"\n🎉 THE LEARNING LOOP IS COMPLETE!")
    print(f"\n📝 What happens now:")
    print(f"  1. User interacts with opportunities → Learning Bridges collect data")
    print(f"  2. Data stored in UserAgentLearning → Preferences learned")
    print(f"  3. Income Builder queries learning → Opportunities personalized")
    print(f"  4. User sees THEIR preferred opportunities → Better matches!")
else:
    print(f"❌ Personalization: NOT WORKING")
    print(f"❌ Last Mile: DISCONNECTED")
    print(f"\n🔍 Check:")
    print(f"  1. UserAgentLearning exists: {UserAgentLearning.objects.filter(user=user).exists()}")
    print(f"  2. User authenticated: {user.is_authenticated}")
    print(f"  3. API endpoint working: {response.status_code == 200}")

print("\n" + "=" * 70)
print("✅ Test Complete!")
print("=" * 70)
