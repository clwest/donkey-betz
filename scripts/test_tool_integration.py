#!/usr/bin/env python
"""
Test Tool Integration for Agents

Tests that agents with tool_integrations configured actually use those tools
during execution.
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_core.agents.universal_agent_loader import get_all_agent_classes
from agents.models import UnifiedAgentTemplate


async def test_agent_with_tools():
    """Test an agent configured with tools"""
    print("=" * 80)
    print("🧪 TOOL INTEGRATION TEST")
    print("=" * 80)

    # Get the content-creator agent (we just configured it with web_search)
    try:
        agent_classes = get_all_agent_classes()

        if 'content_creator' not in agent_classes:
            print("❌ content_creator agent not found in agent classes")
            print(f"Available content agents: {[k for k in agent_classes.keys() if 'content' in k.lower()]}")
            return

        # Create instance (note: registry uses underscore, database uses hyphen)
        ContentAgent = agent_classes['content_creator']
        agent = ContentAgent()

        print(f"\n✅ Agent loaded: content-creator")
        print(f"   Specialization: {agent.specialization}")
        print(f"   Tool config: {json.dumps(agent.config.get('tool_integrations', {}), indent=4)}")

        # Test task
        task = "Find trending AI topics for blog posts"
        print(f"\n📝 Task: {task}")
        print(f"\n⏳ Executing agent with tools...")

        # Execute (synchronous call to async method)
        result = await agent.execute(task=task)

        print(f"\n✅ Execution complete!")
        print(f"   Success: {result.get('success')}")
        print(f"   Tools used: {result.get('tools_used', [])}")
        print(f"   Tool enhanced: {result.get('tool_enhanced', False)}")

        if result.get('tool_enhanced'):
            print(f"\n🎉 SUCCESS! Agent used tools: {', '.join(result['tools_used'])}")
        else:
            print(f"\n⚠️  Agent did not use any tools (config may not be loaded)")

        print(f"\n📄 Agent output (first 500 chars):")
        print("-" * 80)
        print(result.get('output', 'No output')[:500])
        print("-" * 80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_tool_registry():
    """Test that tools are registered and available"""
    print("\n" + "=" * 80)
    print("🔧 TOOL REGISTRY TEST")
    print("=" * 80)

    try:
        from core.tools import ToolRegistry

        tools = ToolRegistry.list_tools()
        print(f"\n✅ Available tools ({len(tools)}):")
        for tool_name in tools:
            tool = ToolRegistry.get_tool(tool_name)
            if tool:
                print(f"   - {tool_name}: ✓")
            else:
                print(f"   - {tool_name}: ✗ (failed to instantiate)")

        # Test web_search specifically
        print(f"\n🔍 Testing web_search tool directly...")
        web_search = ToolRegistry.get_tool('web_search')
        if web_search:
            print(f"   ✅ web_search tool loaded")
            print(f"   Configured: {web_search.is_configured}")

            # Try a simple search
            result = web_search.execute(query="AI agents 2025", max_results=3)
            if result.get('success'):
                print(f"   ✅ Search successful: {len(result.get('data', []))} results")
            else:
                print(f"   ⚠️  Search failed: {result.get('error')}")
        else:
            print(f"   ❌ web_search tool not available")

    except Exception as e:
        print(f"\n❌ Tool registry test failed: {e}")
        import traceback
        traceback.print_exc()


def check_configured_agents():
    """Check which agents have tools configured"""
    print("\n" + "=" * 80)
    print("📊 CONFIGURED AGENTS")
    print("=" * 80)

    agents_with_tools = UnifiedAgentTemplate.objects.exclude(
        tool_integrations={}
    ).values('name', 'tool_integrations')

    print(f"\n✅ Found {agents_with_tools.count()} agents with tool configurations:")
    for agent in agents_with_tools:
        print(f"\n   🤖 {agent['name']}")
        print(f"      {json.dumps(agent['tool_integrations'], indent=6)}")


if __name__ == '__main__':
    print("\n🚀 Starting Tool Integration Tests\n")

    # Check configured agents
    check_configured_agents()

    # Test tool registry
    asyncio.run(test_tool_registry())

    # Test agent with tools
    asyncio.run(test_agent_with_tools())

    print("\n✅ All tests complete!")
