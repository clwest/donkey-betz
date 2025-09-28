#!/usr/bin/env python3
"""
Test to verify real data is being used instead of mock data
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_core.spiders.live_job_scraper import scrape_jobs_sync
from ai_core.opportunities_api import generate_real_opportunities, generate_enhanced_opportunities
import json


def test_spider_real_data():
    """Test that spiders return real data"""
    print("\n🔍 Testing Spider Real Data...")

    jobs = scrape_jobs_sync()

    if not jobs:
        print("❌ No jobs returned from spider")
        return False

    # Check for mock company names
    mock_companies = ['TechCorp', 'AI Innovations', 'DataDrive', 'CloudScale',
                      'StartupXYZ', 'Digital Solutions', 'Future Systems']

    real_jobs = []
    mock_jobs = []

    for job in jobs:
        company = job.get('company', '')
        if company in mock_companies:
            mock_jobs.append(job)
        else:
            real_jobs.append(job)

    print(f"✅ Found {len(jobs)} total jobs:")
    print(f"   - Real jobs: {len(real_jobs)}")
    print(f"   - Mock jobs: {len(mock_jobs)}")

    if real_jobs:
        print("\n📋 Sample real jobs:")
        for job in real_jobs[:3]:
            print(f"   - {job.get('title')} at {job.get('company')} (source: {job.get('source')})")

    if mock_jobs:
        print("\n⚠️ Warning: Found mock jobs:")
        for job in mock_jobs[:3]:
            print(f"   - {job.get('title')} at {job.get('company')}")

    return len(real_jobs) > 0


def test_opportunities_api():
    """Test that opportunities API returns real data"""
    print("\n🔍 Testing Opportunities API...")

    opportunities = generate_real_opportunities(10)

    if not opportunities:
        print("❌ No opportunities returned")
        return False

    # Check for mock patterns
    mock_companies = ['TechCorp', 'AI Innovations', 'DataDrive', 'CloudScale',
                      'DataTech Solutions', 'CloudFirst Inc', 'Neural Networks Ltd']

    real_count = 0
    mock_count = 0

    for opp in opportunities:
        company = opp.get('company', '')
        if company in mock_companies:
            mock_count += 1
        else:
            real_count += 1

    print(f"✅ Found {len(opportunities)} opportunities:")
    print(f"   - Real: {real_count}")
    print(f"   - Mock: {mock_count}")

    if real_count > 0:
        print("\n✅ SUCCESS: Using real data!")
    else:
        print("\n❌ FAILURE: Still using mock data")

    return real_count > 0


def main():
    print("=" * 60)
    print("🧪 Real Data Verification Test")
    print("=" * 60)

    spider_test = test_spider_real_data()
    api_test = test_opportunities_api()

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Spider Real Data: {'✅ PASS' if spider_test else '❌ FAIL'}")
    print(f"   API Real Data: {'✅ PASS' if api_test else '❌ FAIL'}")
    print("=" * 60)

    if spider_test and api_test:
        print("\n🎉 All tests passed! System is using real data!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the mock data fallbacks.")
        return 1


if __name__ == "__main__":
    exit(main())
