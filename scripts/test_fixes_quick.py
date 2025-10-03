#!/usr/bin/env python
"""
Quick test to verify overnight learning test fixes
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import asyncio
from django.contrib.auth import get_user_model
from ai_core.spiders.spider_registry import spider_registry
from ai_core.spiders.base_spider import SpiderTarget
from ai_core.agents.concrete_executor import execute_agent_sync

User = get_user_model()

async def test_spider_instantiation():
    """Test that spiders can be instantiated with proper parameters"""
    print("\n" + "="*60)
    print("TEST 1: Spider Instantiation")
    print("="*60)

    spider_type = 'financial'
    try:
        spider_class = spider_registry.get_spider_class(spider_type)
        if not spider_class:
            print(f"❌ Spider '{spider_type}' not found in registry")
            return False

        # Create spider with proper parameters
        spider_id = f"{spider_type}_test"
        targets = [
            SpiderTarget(
                url="https://example.com/test",
                rate_limit=1.0,
                priority=1,
                retry_count=3,
                timeout=30
            )
        ]
        subscribers = []
        redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

        spider = spider_class(
            spider_id=spider_id,
            targets=targets,
            subscribers=subscribers,
            redis_config=redis_config
        )

        print(f"✅ Spider '{spider_type}' instantiated successfully")
        print(f"   Spider ID: {spider.spider_id}")
        print(f"   Targets: {len(spider.targets)}")
        return True

    except Exception as e:
        print(f"❌ Spider instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_lookup():
    """Test that agents can be found in the registry"""
    print("\n" + "="*60)
    print("TEST 2: Agent Registry Lookup")
    print("="*60)

    from ai_core.agents.universal_agent_loader import get_all_agent_classes

    try:
        agent_classes = get_all_agent_classes()
        print(f"✅ Loaded {len(agent_classes)} agent classes")

        # Test specific agent names from overnight test
        test_agents = [
            'business_agent',
            'content_creator',
            'seo_specialist_agent'
        ]

        found = 0
        for agent_name in test_agents:
            if agent_name in agent_classes:
                print(f"   ✅ Found: {agent_name}")
                found += 1
            else:
                print(f"   ❌ Missing: {agent_name}")

        print(f"\nFound {found}/{len(test_agents)} test agents")
        return found == len(test_agents)

    except Exception as e:
        print(f"❌ Agent lookup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_execution():
    """Test that an agent can be executed"""
    print("\n" + "="*60)
    print("TEST 3: Agent Execution")
    print("="*60)

    try:
        user = User.objects.get(username='chris')
        print(f"✅ User found: {user.username}")

        # Try executing a simple agent
        agent_name = 'content_creator'
        task = "Generate a brief test message"

        print(f"   Executing agent: {agent_name}")
        result = execute_agent_sync(agent_name, task, None, user)

        if result.get('success') is False:
            print(f"❌ Agent execution failed: {result.get('error')}")
            if 'available_agents' in result:
                print(f"   Available agents (first 10):")
                for agent in list(result['available_agents'])[:10]:
                    print(f"     - {agent}")
            return False
        else:
            print(f"✅ Agent executed successfully")
            print(f"   Execution time: {result.get('execution_time', 0):.2f}s")
            return True

    except User.DoesNotExist:
        print("❌ User 'chris' not found - create user first")
        return False
    except Exception as e:
        print(f"❌ Agent execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OVERNIGHT LEARNING TEST FIXES - VALIDATION")
    print("="*60)

    results = []

    # Test 1: Spider instantiation
    results.append(await test_spider_instantiation())

    # Test 2: Agent lookup
    results.append(test_agent_lookup())

    # Test 3: Agent execution
    results.append(test_agent_execution())

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All fixes validated successfully!")
        print("   Ready to run overnight learning test")
    else:
        print("\n⚠️  Some tests failed - review errors above")

    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
