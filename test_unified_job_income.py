#!/usr/bin/env python3
"""
Test the unified AI Job Tracker + Income Builder integration
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from intelligence.job_income_bridge import JobIncomeBridge
from django.core.cache import cache
import json

def test_unified_integration():
    """Test the unified job-income bridge"""

    print("🔄 Testing Unified AI Job Tracker + Income Builder Integration")
    print("="*60)

    # Create some test job data
    test_jobs = [
        {
            'id': 'job_001',
            'title': 'Senior AI Engineer - Remote',
            'company': 'TechCorp AI',
            'salary': '$8,000/month',
            'description': 'Build cutting-edge AI systems using GPT-4 and Claude',
            'aiScore': 0.92,
            'tags': ['Python', 'AI', 'Machine Learning', 'Remote'],
            'source': 'linkedin',
            'url': 'https://linkedin.com/jobs/123'
        },
        {
            'id': 'job_002',
            'title': 'Freelance Content Strategist',
            'company': 'Digital Agency',
            'salary': '$4,500/month',
            'description': 'Create AI-powered content strategies for Fortune 500 clients',
            'aiScore': 0.88,
            'tags': ['Content', 'Strategy', 'AI', 'Marketing'],
            'source': 'upwork',
            'url': 'https://upwork.com/job/456'
        },
        {
            'id': 'job_003',
            'title': 'Blockchain Developer',
            'company': 'CryptoStartup',
            'salary': '$12,000/month',
            'description': 'Build DeFi protocols and smart contracts',
            'aiScore': 0.75,
            'tags': ['Blockchain', 'Solidity', 'DeFi', 'Web3'],
            'source': 'remoteok',
            'url': 'https://remoteok.com/job/789'
        }
    ]

    # Store jobs in cache (simulating AI Job Tracker)
    print("\n📝 Simulating AI Job Tracker data...")
    cache.set('live_jobs', test_jobs, 3600)
    print(f"   ✅ Cached {len(test_jobs)} jobs")

    # Sync to Income Builder
    print("\n🔗 Syncing to Income Builder...")
    JobIncomeBridge.sync_to_income_builder(test_jobs)
    print("   ✅ Jobs synced to Income Builder")

    # Get unified opportunities
    print("\n🎯 Getting Unified Opportunities...")
    unified_data = JobIncomeBridge.get_unified_opportunities()

    opportunities = unified_data['opportunities']
    stats = unified_data['stats']

    print(f"\n📊 Statistics:")
    print(f"   • Total Opportunities: {stats['total_opportunities']}")
    print(f"   • Real Jobs: {stats['real_jobs']}")
    print(f"   • Income Streams: {stats['income_streams']}")
    print(f"   • Avg Monthly Potential: ${stats['avg_monthly_potential']:,.0f}")
    print(f"   • Top Category: {stats['top_category']}")
    print(f"   • Avg Success Rate: {stats['success_rate']:.1f}%")

    print(f"\n🎯 Top 5 Unified Opportunities:")
    for i, opp in enumerate(opportunities[:5], 1):
        is_job = opp.get('is_real_job', False)
        type_emoji = "💼" if is_job else "💡"

        print(f"\n{i}. {type_emoji} {opp['title']}")
        print(f"   Type: {opp['stream_type']}")
        print(f"   Potential: {opp['potential_monthly']}")
        print(f"   Success Rate: {opp.get('success_rate', 0):.0f}%")

        if is_job:
            print(f"   Company: {opp.get('company', 'Unknown')}")
            print(f"   Source: {opp.get('source', 'Unknown')}")

        print(f"   Match Reasons: {', '.join(opp['match_reasons'][:2])}")

    # Test personalized opportunities
    print("\n\n🎯 Testing Personalized Opportunities...")
    user_profile = {
        'skills': ['Python', 'AI', 'Machine Learning', 'Content'],
        'experience_level': 'intermediate',
        'available_hours': 40
    }

    personalized = JobIncomeBridge.get_personalized_opportunities(user_profile)

    print(f"   Profile Skills: {', '.join(user_profile['skills'])}")
    print(f"\n   Top 3 Personalized Matches:")

    for i, opp in enumerate(personalized[:3], 1):
        skill_match = opp.get('skill_match', 0) * 100
        print(f"\n   {i}. {opp['title']}")
        print(f"      Skill Match: {skill_match:.0f}%")
        print(f"      Required Skills: {', '.join(opp.get('required_skills', [])[:3])}")

    print("\n" + "="*60)

    # Check if integration is working
    if stats['total_opportunities'] > 0 and stats['real_jobs'] > 0:
        print("✅ SUCCESS: AI Job Tracker and Income Builder are UNIFIED!")
        print(f"   • {stats['real_jobs']} real jobs integrated")
        print(f"   • {stats['income_streams']} income streams added")
        print(f"   • {stats['total_opportunities']} total opportunities available")
    else:
        print("⚠️  WARNING: Integration may not be working fully")

    print("="*60)

if __name__ == "__main__":
    test_unified_integration()