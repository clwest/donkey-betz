#!/usr/bin/env python3
"""
Quick test of the job search functionality with only fast sources
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_core.unified_job_search import UnifiedJobSearch


async def quick_demo():
    """Quick demo of job search with user profile matching"""
    print("=" * 80)
    print("🔍 JOB SEARCH WITHOUT API KEYS - DEMO")
    print("=" * 80)

    search = UnifiedJobSearch()

    # Create a sample user profile
    user_profile = {
        'skills': {
            'primary': ['python', 'javascript', 'react'],
            'secondary': ['aws', 'docker', 'postgresql']
        },
        'experience_years': 3,
        'desired_salary': 100000,
        'salary_flexibility': 0.2,
        'location_preferences': {
            'remote_only': True
        },
        'industries': ['tech', 'startup', 'saas'],
        'company_size_preference': 'startup',
        'job_type_preference': 'full-time'
    }

    print("\n📝 Your Profile:")
    print(f"  • Primary Skills: {', '.join(user_profile['skills']['primary'])}")
    print(f"  • Experience: {user_profile['experience_years']} years")
    print(f"  • Target Salary: ${user_profile['desired_salary']:,}")
    print(f"  • Location: Remote only")

    print("\n🔍 Searching for jobs (this will take ~10-15 seconds)...")

    # Search with keywords
    results = await search.search_jobs(
        keywords=['python', 'javascript', 'remote', 'developer'],
        user_profile=user_profile,
        filters={
            'location': 'remote',
            'posted_within_days': 30
        },
        limit=20
    )

    print(f"\n✅ Found {results['total_found']} jobs!")

    # Show top matches
    print("\n🎯 TOP 5 MATCHES FOR YOU:")
    print("-" * 80)

    for i, job in enumerate(results['jobs'][:5], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Source: {job['source']}")
        print(f"   Location: {job.get('location', 'Not specified')}")

        # Show salary if available
        if job.get('salary_min'):
            print(f"   Salary: ${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}")
        elif job.get('salary'):
            print(f"   Salary: {job.get('salary')}")

        # Show match score if available
        if 'scoring' in job:
            score = job['scoring']['overall_score']
            reasons = job['scoring']['match_reasons']
            print(f"   Match Score: {score:.0%}")
            if reasons:
                print(f"   Why it matches: {', '.join(reasons[:2])}")

        # Show apply link
        apply_url = job.get('application_url', job.get('url', ''))
        if apply_url:
            print(f"   Apply: {apply_url[:60]}...")

    # Show analytics
    if 'analytics' in results and results['analytics']:
        print("\n📊 JOB MARKET INSIGHTS:")
        print("-" * 80)

        analytics = results['analytics']

        # Source distribution
        if 'source_distribution' in analytics:
            print("\nJobs by Source:")
            for source, count in list(analytics['source_distribution'].items())[:5]:
                print(f"  • {source}: {count} jobs")

        # Salary insights
        if 'salary_statistics' in analytics and analytics['salary_statistics']:
            stats = analytics['salary_statistics']
            print(f"\nSalary Range:")
            print(f"  • Average: ${stats.get('average', 0):,.0f}")
            print(f"  • Min: ${stats.get('min', 0):,.0f}")
            print(f"  • Max: ${stats.get('max', 0):,.0f}")

        # Top companies
        if 'top_hiring_companies' in analytics:
            print(f"\nTop Hiring Companies:")
            for company, count in list(analytics['top_hiring_companies'].items())[:5]:
                if company != 'Unknown' and company != 'Company':
                    print(f"  • {company}: {count} openings")

    print("\n" + "=" * 80)
    print("💡 WHAT YOU CAN DO WITH THIS:")
    print("=" * 80)
    print("1. ✅ Search jobs from 10+ free sources (no API keys needed!)")
    print("2. ✅ Get personalized matches based on your profile")
    print("3. ✅ Filter by location, salary, company size, etc.")
    print("4. ✅ See why each job matches your profile")
    print("5. ✅ Track job market trends and insights")
    print("\n🚀 All without Indeed or LinkedIn API keys!")

    # Close resources
    await search.spider.close()


if __name__ == "__main__":
    print("\n🚀 Starting Job Search Demo (No API Keys Required!)\n")
    asyncio.run(quick_demo())