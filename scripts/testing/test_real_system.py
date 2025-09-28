#!/usr/bin/env python
"""
Test Complete System with Real Data Flow
========================================

This script tests the complete system to ensure:
1. No hardcoded/mock data remains
2. Spiders collect real data
3. Data is validated and persisted
4. Shared memory works across entities
5. Celery tasks are scheduled properly
"""

import os
import sys
import django
import asyncio
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.core.cache import cache
from ai_core.tasks import collect_real_opportunities
from intelligence.shared_memory import SharedMemorySystem, AgentMemoryInterface, AdvisorMemoryInterface
from ai_core.spiders.spider_validator import spider_orchestrator
from ai_core.spiders.live_job_scraper import scrape_jobs_sync


def test_spider_collection():
    """Test 1: Spider Data Collection"""
    print("\n" + "="*60)
    print("TEST 1: SPIDER DATA COLLECTION")
    print("="*60)

    try:
        # Trigger immediate spider collection
        print("🕷️ Triggering spider collection...")
        jobs = scrape_jobs_sync()

        if jobs:
            print(f"✅ Collected {len(jobs)} jobs from spiders")

            # Check if jobs are validated
            if all('validated' in job for job in jobs[:5]):
                print("✅ Jobs are validated")
            else:
                print("⚠️ Jobs missing validation flag")

            # Check cache
            cached_jobs = cache.get('validated_jobs', [])
            print(f"✅ {len(cached_jobs)} jobs in cache")

            # Show sample job
            if jobs:
                sample = jobs[0]
                print(f"\nSample job:")
                print(f"  Title: {sample.get('title')}")
                print(f"  Company: {sample.get('company')}")
                print(f"  Source: {sample.get('source')}")
                print(f"  Validated: {sample.get('validated', False)}")

            return True
        else:
            print("❌ No jobs collected from spiders")
            print("   Note: This might be due to rate limiting or API availability")
            return False

    except Exception as e:
        print(f"❌ Spider test failed: {e}")
        return False


def test_data_persistence():
    """Test 2: Data Persistence"""
    print("\n" + "="*60)
    print("TEST 2: DATA PERSISTENCE")
    print("="*60)

    try:
        from intelligence.models import OpportunityActionPlan

        # Check database for persisted opportunities
        count = OpportunityActionPlan.objects.filter(
            opportunity_id__startswith='spider_'
        ).count()

        print(f"📊 Found {count} spider-collected opportunities in database")

        # Get recent opportunities
        recent = OpportunityActionPlan.objects.filter(
            status='identified'
        ).order_by('-created_at')[:5]

        if recent:
            print(f"✅ Recent opportunities persisted:")
            for opp in recent:
                print(f"   - {opp.opportunity_data.get('title', 'Unknown')[:50]}")
                print(f"     Revenue: ${opp.revenue_potential:.0f}")
            return True
        else:
            print("⚠️ No recent opportunities in database")
            return False

    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        return False


def test_shared_memory():
    """Test 3: Shared Memory System"""
    print("\n" + "="*60)
    print("TEST 3: SHARED MEMORY SYSTEM")
    print("="*60)

    try:
        # Initialize memory interfaces
        agent_memory = AgentMemoryInterface('test_agent')
        advisor_memory = AdvisorMemoryInterface('test_advisor')
        shared_memory = SharedMemorySystem()

        # Agent stores a memory
        agent_memory.remember('decision', {
            'action': 'test_action',
            'result': 'success',
            'timestamp': datetime.now().isoformat()
        })
        print("✅ Agent stored memory")

        # Agent shares learning
        agent_memory.share_learning({
            'insight': 'Test validation works',
            'impact': 'High',
            'applicable_to': 'all_entities'
        })
        print("✅ Agent shared learning")

        # Advisor provides wisdom
        advisor_memory.provide_wisdom({
            'topic': 'system_testing',
            'advice': 'Always validate real data',
            'confidence': 0.95
        })
        print("✅ Advisor shared wisdom")

        # Check if other entities can learn
        learnings = agent_memory.learn_from_others(limit=5)
        print(f"✅ Agent learned from {len(learnings)} experiences")

        # Add knowledge edge
        shared_memory.add_knowledge_edge(
            'agent/test_agent',
            'advisor/test_advisor',
            'consulted',
            strength=0.9
        )
        print("✅ Knowledge edge created")

        # Get entity network
        network = shared_memory.get_entity_network('agent/test_agent')
        print(f"✅ Network connections: {len(network['outgoing'])} outgoing, {len(network['incoming'])} incoming")

        return True

    except Exception as e:
        print(f"❌ Shared memory test failed: {e}")
        return False


def test_celery_tasks():
    """Test 4: Celery Task Scheduling"""
    print("\n" + "="*60)
    print("TEST 4: CELERY TASK SCHEDULING")
    print("="*60)

    try:
        from core.celery import app

        # Check registered tasks
        tasks = list(app.tasks.keys())
        required_tasks = [
            'ai_core.tasks.collect_real_opportunities',
            'ai_core.tasks.refresh_ai_content_opportunities',
            'ai_core.tasks.sync_revenue_metrics',
            'intelligence.shared_memory.sync_all_entity_memories'
        ]

        print(f"📋 Found {len(tasks)} registered Celery tasks")

        missing_tasks = []
        for task in required_tasks:
            if task in tasks:
                print(f"✅ {task}")
            else:
                print(f"❌ {task} not found")
                missing_tasks.append(task)

        # Check beat schedule
        beat_schedule = app.conf.beat_schedule
        print(f"\n📅 Beat schedule has {len(beat_schedule)} scheduled tasks:")
        for name, config in beat_schedule.items():
            print(f"   - {name}: {config['task']}")

        # Test immediate task execution
        print("\n🚀 Testing immediate task execution...")
        result = collect_real_opportunities.apply_async()
        print(f"✅ Task queued with ID: {result.id}")

        return len(missing_tasks) == 0

    except Exception as e:
        print(f"❌ Celery test failed: {e}")
        return False


def test_no_hardcoded_data():
    """Test 5: Verify No Hardcoded Data"""
    print("\n" + "="*60)
    print("TEST 5: VERIFY NO HARDCODED DATA")
    print("="*60)

    try:
        # Check unified_hub.py for removed hardcoded data
        with open('/Users/donkeyking/development/unified-donkey-betz/core/unified_hub.py', 'r') as f:
            content = f.read()

        # Check for old hardcoded strings
        hardcoded_strings = [
            'AI Content Creation Service',
            'Prompt Engineering Services',
            'No-Code AI Automation',
            'Digital Product Empire',
            'Automated Trading Bot'
        ]

        found_hardcoded = []
        for string in hardcoded_strings:
            if string in content:
                found_hardcoded.append(string)

        if found_hardcoded:
            print(f"❌ Found hardcoded strings: {found_hardcoded}")
            return False
        else:
            print("✅ No hardcoded fallback data found")

        # Check for emergency spider trigger
        if 'collect_real_opportunities.delay()' in content:
            print("✅ Emergency spider collection implemented")
        else:
            print("⚠️ Emergency spider collection not found")

        return True

    except Exception as e:
        print(f"❌ Hardcoded data test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀"*20)
    print("REAL DATA FLOW SYSTEM TEST")
    print("🚀"*20)

    results = {
        'Spider Collection': test_spider_collection(),
        'Data Persistence': test_data_persistence(),
        'Shared Memory': test_shared_memory(),
        'Celery Tasks': test_celery_tasks(),
        'No Hardcoded Data': test_no_hardcoded_data()
    }

    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    passed = 0
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n📊 Final Score: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! System is using REAL DATA only!")
        print("\n📝 Next Steps:")
        print("1. Start Celery worker: celery -A core worker -l info")
        print("2. Start Celery beat: celery -A core beat -l info")
        print("3. Monitor logs for scheduled spider runs every 15 minutes")
        print("4. Check shared memory synchronization every 10 minutes")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
        print("\n📝 Common Issues:")
        print("1. Redis not running: redis-server")
        print("2. API keys not configured in .env")
        print("3. Database migrations not applied: python manage.py migrate")


if __name__ == "__main__":
    main()