#!/usr/bin/env python
"""
Test Script for Real Data Flow Verification
===========================================

This script tests:
1. Profile data persistence between sessions
2. Real AI responses from LLM APIs
3. Real job scraping from live sources
"""

import os
import sys
import django
import json
import asyncio
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.contrib.auth.models import User
from django.test.client import Client
from core.models import EnhancedUserProfile
from core.llm_enforcer import get_llm_enforcer, verify_llm_availability
from ai_core.spiders.live_job_scraper import scrape_jobs_sync
from django.core.cache import cache


def test_profile_persistence():
    """Test 1: Profile Data Persistence"""
    print("\n" + "="*60)
    print("TEST 1: PROFILE DATA PERSISTENCE")
    print("="*60)

    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )

        if created:
            user.set_password('testpass123')
            user.save()
            print("✅ Created test user")
        else:
            print("✅ Using existing test user")

        # Create or update profile
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)

        # Update profile fields
        profile.full_name = "John Test Developer"
        profile.professional_summary = "Experienced AI developer with 5 years in ML"
        profile.skills = ["Python", "Machine Learning", "Django", "React"]
        profile.years_experience = 5
        profile.save()

        print(f"✅ Profile saved to database")
        print(f"   - Name: {profile.full_name}")
        print(f"   - Skills: {', '.join(profile.skills)}")

        # Simulate session storage (what happens in the view)
        client = Client()
        client.force_login(user)

        # Make a request to trigger session storage
        response = client.get('/api/v1/enhanced-profile/')

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile retrieved via API")
            print(f"   - Completeness: {data.get('profile', {}).get('profile_completeness', 0)}%")
        else:
            print(f"⚠️ API returned status {response.status_code}")

        # Test persistence by fetching again
        profile_reload = EnhancedUserProfile.objects.get(user=user)
        if profile_reload.full_name == "John Test Developer":
            print("✅ Profile data persisted correctly in database")
            return True
        else:
            print("❌ Profile data not persisted")
            return False

    except Exception as e:
        print(f"❌ Profile test failed: {e}")
        return False


def test_llm_integration():
    """Test 2: Real LLM API Integration"""
    print("\n" + "="*60)
    print("TEST 2: REAL LLM API INTEGRATION")
    print("="*60)

    try:
        # Check if LLM is available
        if not verify_llm_availability():
            print("⚠️ No LLM API keys configured")
            print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY in environment")
            return False

        print("✅ LLM API available")

        # Test real AI generation
        enforcer = get_llm_enforcer()
        stats = enforcer.get_usage_stats()

        print(f"   - OpenAI: {'✅' if stats['openai_available'] else '❌'}")
        print(f"   - Anthropic: {'✅' if stats['anthropic_available'] else '❌'}")

        # Generate test content
        print("\nGenerating test content...")
        result = enforcer.enforce_real_ai(
            prompt="Generate a brief job application introduction for a Python developer. Keep it under 50 words.",
            agent_name="TestScript",
            task_type="test",
            max_tokens=100,
            temperature=0.7
        )

        if result and 'content' in result:
            print("✅ Real AI response received:")
            print(f"   \"{result['content'][:100]}...\"")
            print(f"   - Tokens used: {result.get('tokens', 0)}")
            print(f"   - Cost: ${result.get('cost', 0):.4f}")
            return True
        else:
            print("❌ No content in AI response")
            return False

    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


def test_job_scraping():
    """Test 3: Real Job Scraping"""
    print("\n" + "="*60)
    print("TEST 3: REAL JOB SCRAPING")
    print("="*60)

    try:
        print("Starting job scraping (this may take 10-20 seconds)...")

        # Clear cache to force fresh scrape
        cache.delete('live_jobs')

        # Scrape jobs
        jobs = scrape_jobs_sync()

        if not jobs:
            print("⚠️ No jobs scraped (APIs might be down)")
            return False

        print(f"✅ Scraped {len(jobs)} jobs from live sources")

        # Analyze sources
        sources = {}
        for job in jobs:
            source = job.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1

        print("\nJobs by source:")
        for source, count in sources.items():
            print(f"   - {source}: {count} jobs")

        # Show sample jobs
        print("\nSample jobs found:")
        for job in jobs[:3]:
            print(f"\n   📌 {job['title']}")
            print(f"      Company: {job['company']}")
            print(f"      Salary: {job.get('salary', 'Not specified')}")
            print(f"      AI Score: {job.get('aiScore', 0):.2%}")
            print(f"      Source: {job['source']}")

        # Check if jobs have real URLs
        real_urls = sum(1 for job in jobs if job.get('url', '').startswith('http'))
        print(f"\n✅ Jobs with real URLs: {real_urls}/{len(jobs)}")

        # Cache the jobs for other tests
        cache.set('live_jobs', jobs, 1800)

        return len(jobs) > 0

    except Exception as e:
        print(f"❌ Job scraping test failed: {e}")
        return False


def test_api_endpoints():
    """Test 4: API Endpoints with Real Data"""
    print("\n" + "="*60)
    print("TEST 4: API ENDPOINTS")
    print("="*60)

    client = Client()

    # Test spider endpoint
    print("\n1. Testing Spider Endpoint...")
    response = client.get('/api/v1/ai-jobs/spiders/')

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Spider endpoint working")
        print(f"   - Total spiders: {data.get('total', 0)}")
        print(f"   - Active spiders: {data.get('active', 0)}")
    else:
        print(f"❌ Spider endpoint failed: {response.status_code}")

    # Test jobs endpoint
    print("\n2. Testing Jobs Endpoint...")
    response = client.get('/api/v1/ai-jobs/opportunities/')

    if response.status_code == 200:
        data = response.json()
        jobs = data.get('jobs', [])
        stats = data.get('stats', {})

        print(f"✅ Jobs endpoint working")
        print(f"   - Jobs returned: {len(jobs)}")
        print(f"   - Data source: {stats.get('dataSource', 'unknown')}")
        print(f"   - AI suitable: {stats.get('aiSuitable', 0)}")

        # Check if jobs are real (not default)
        if jobs and jobs[0].get('source') != 'default':
            print("   ✅ Using REAL scraped data!")
        else:
            print("   ⚠️ Using cached/default data")

        return True
    else:
        print(f"❌ Jobs endpoint failed: {response.status_code}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("UNIFIED DONKEY BETZ - REAL DATA FLOW VERIFICATION")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")

    results = {
        'Profile Persistence': test_profile_persistence(),
        'LLM Integration': test_llm_integration(),
        'Job Scraping': test_job_scraping(),
        'API Endpoints': test_api_endpoints()
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Real data is flowing!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)