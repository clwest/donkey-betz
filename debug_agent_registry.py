#!/usr/bin/env python
"""
Debug script to test agent registry initialization in different contexts
"""
import os
import django
import asyncio

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_agent_registry_sync():
    print("🔍 Testing Agent Registry Initialization (Sync Context)")
    print("=" * 60)

    # Test 1: Direct ConcreteAgentExecutor
    print("\n1️⃣ Testing ConcreteAgentExecutor directly:")
    try:
        from backend.agents.concrete_executor import ConcreteAgentExecutor
        executor = ConcreteAgentExecutor()
        print(f"   ✅ ConcreteAgentExecutor agents: {len(executor.agent_classes)}")
        if len(executor.agent_classes) > 0:
            print(f"   📋 Sample agents: {sorted(list(executor.agent_classes.keys()))[:5]}")
        else:
            print("   ❌ No agents loaded!")
    except Exception as e:
        print(f"   ❌ Failed to create ConcreteAgentExecutor: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: ProperAgentExecutor
    print("\n2️⃣ Testing ProperAgentExecutor:")
    try:
        from agents.proper_agent_executor import ProperAgentExecutor
        proper_executor = ProperAgentExecutor()
        print(f"   ✅ ProperAgentExecutor agents: {len(proper_executor.executor.agent_classes)}")
        if len(proper_executor.executor.agent_classes) > 0:
            print(f"   📋 Sample agents: {sorted(list(proper_executor.executor.agent_classes.keys()))[:5]}")
        else:
            print("   ❌ No agents loaded!")
    except Exception as e:
        print(f"   ❌ Failed to create ProperAgentExecutor: {e}")
        import traceback
        traceback.print_exc()

async def test_agent_registry_async():
    print("\n🔄 Testing Agent Registry Initialization (Async Context)")
    print("=" * 60)

    # Test 1: Direct ConcreteAgentExecutor in async
    print("\n1️⃣ Testing ConcreteAgentExecutor in async:")
    try:
        from backend.agents.concrete_executor import ConcreteAgentExecutor
        executor = ConcreteAgentExecutor()
        print(f"   ✅ ConcreteAgentExecutor agents: {len(executor.agent_classes)}")
        if len(executor.agent_classes) > 0:
            print(f"   📋 Sample agents: {sorted(list(executor.agent_classes.keys()))[:5]}")
        else:
            print("   ❌ No agents loaded!")
    except Exception as e:
        print(f"   ❌ Failed to create ConcreteAgentExecutor: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: ProperAgentExecutor in async
    print("\n2️⃣ Testing ProperAgentExecutor in async:")
    try:
        from agents.proper_agent_executor import ProperAgentExecutor
        proper_executor = ProperAgentExecutor()
        print(f"   ✅ ProperAgentExecutor agents: {len(proper_executor.executor.agent_classes)}")
        if len(proper_executor.executor.agent_classes) > 0:
            print(f"   📋 Sample agents: {sorted(list(proper_executor.executor.agent_classes.keys()))[:5]}")
        else:
            print("   ❌ No agents loaded!")
    except Exception as e:
        print(f"   ❌ Failed to create ProperAgentExecutor: {e}")
        import traceback
        traceback.print_exc()

    # Test 3: Database query in async context
    print("\n3️⃣ Testing database query in async:")
    try:
        from django.db import connection
        from agents.models import UnifiedAgentTemplate
        from asgiref.sync import sync_to_async

        # Test sync database query in async context
        templates = await sync_to_async(UnifiedAgentTemplate.objects.all().count)()
        print(f"   ✅ Database agent templates (async): {templates}")

    except Exception as e:
        print(f"   ❌ Failed to query database in async: {e}")
        import traceback
        traceback.print_exc()

    # Test 4: Simulate the exact testing system context
    print("\n4️⃣ Testing AgentTestingSystem context:")
    try:
        from agents.agent_testing_system import AgentTestingSystem
        testing_system = AgentTestingSystem()
        registry_info = testing_system.get_registry_status()
        print(f"   ✅ Testing system registry: {registry_info['total_agents']} agents")
        if registry_info['total_agents'] > 0:
            print(f"   📋 Available agents: {registry_info['available_agents'][:5]}")
        else:
            print(f"   ❌ No agents in testing system registry! Error: {registry_info.get('error', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Failed to create AgentTestingSystem: {e}")
        import traceback
        traceback.print_exc()

async def main():
    # Test sync context first
    test_agent_registry_sync()

    # Test async context
    await test_agent_registry_async()

if __name__ == "__main__":
    asyncio.run(main())