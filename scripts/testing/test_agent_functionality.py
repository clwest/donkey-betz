#!/usr/bin/env python
"""
Comprehensive Agent Functionality Test
======================================
This script tests that agents are not just registered but fully functional with:
1. Tool access and integration
2. Inter-agent communication
3. Knowledge sharing capabilities
4. Persistence of learnings
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
import django
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
from core.agents.registry import AgentRegistry
from core.tools import ToolRegistry
from intelligence.shared_memory import SharedMemorySystem
from agents.executors.base_executor import BaseAgentExecutor
from agents.platform_capabilities import get_platform_awareness_prompt

# Configuration
API_TOKEN = '<redacted-0fb2390d-2026-04-20>'
BASE_URL = 'http://localhost:8000'

print("=" * 80)
print("🤖 COMPREHENSIVE AGENT FUNCTIONALITY TEST")
print("=" * 80)

# Test 1: Verify Agents are Loaded
print("\n📋 TEST 1: Agent Registration")
print("-" * 40)
try:
    agent_registry = AgentRegistry()
    all_agents = agent_registry.get_all_agents()
    print(f"✅ {len(all_agents)} agents loaded in registry")

    # Sample a few agents
    sample_agents = list(all_agents.values())[:3]
    for agent in sample_agents:
        print(f"   - {agent['name']}: {len(agent.get('required_tools', []))} required tools")
except Exception as e:
    print(f"❌ Agent registry error: {e}")

# Test 2: Verify Tool Registry
print("\n🔧 TEST 2: Tool Registry & Integration")
print("-" * 40)
try:
    available_tools = ToolRegistry.list_tools()
    print(f"✅ {len(available_tools)} tools available:")
    for tool_name in available_tools:
        tool = ToolRegistry.get_tool(tool_name)
        if tool:
            print(f"   - {tool_name}: {'✓ Initialized' if tool else '✗ Failed'}")
except Exception as e:
    print(f"❌ Tool registry error: {e}")

# Test 3: Check Agent-Tool Mapping
print("\n🔗 TEST 3: Agent-Tool Mapping")
print("-" * 40)
try:
    # Check if agents have their required tools available
    agents_with_tools = UnifiedAgentTemplate.objects.filter(active=True)[:5]
    for agent in agents_with_tools:
        required = agent.required_tools or []
        available = [t for t in required if t in available_tools]
        missing = [t for t in required if t not in available_tools]
        print(f"   {agent.name}:")
        print(f"      Required: {len(required)} | Available: {len(available)} | Missing: {len(missing)}")
        if missing:
            print(f"      ⚠️  Missing tools: {missing}")
except Exception as e:
    print(f"❌ Agent-tool mapping error: {e}")

# Test 4: Shared Memory System
print("\n🧠 TEST 4: Shared Memory & Learning System")
print("-" * 40)
try:
    memory_system = SharedMemorySystem()

    # Store a test memory
    test_memory = {
        'task': 'test_execution',
        'result': 'success',
        'learning': 'Test pattern identified'
    }

    success = memory_system.store_memory(
        entity_type='agent',
        entity_id='test_agent',
        memory_type='execution',
        content=test_memory
    )
    print(f"✅ Memory storage: {'Success' if success else 'Failed'}")

    # Share an experience
    test_experience = {
        'action': 'web_search',
        'outcome': 'found_relevant_data',
        'improvement': 'refined_query_patterns'
    }

    exp_success = memory_system.share_experience(
        entity_type='agent',
        entity_id='test_agent',
        experience=test_experience
    )
    print(f"✅ Experience sharing: {'Success' if exp_success else 'Failed'}")

    # Retrieve learnings
    learnings = memory_system.learn_from_experiences('agent', 'another_agent', limit=5)
    print(f"✅ Learning retrieval: {len(learnings)} experiences available")

except Exception as e:
    print(f"❌ Shared memory error: {e}")

# Test 5: Agent Execution Capabilities
print("\n⚡ TEST 5: Agent Execution System")
print("-" * 40)
try:
    # Test with a simple agent
    test_agent = UnifiedAgentTemplate.objects.filter(
        specialization='research'
    ).first()

    if test_agent:
        print(f"Testing execution with: {test_agent.name}")

        # Initialize executor
        executor = BaseAgentExecutor(
            agent_name=test_agent.name,
            config={'agent_id': test_agent.id}
        )

        # Check tool initialization
        print(f"   Tools initialized: {len(executor.tools)}")
        for tool_name, tool in executor.tools.items():
            print(f"      - {tool_name}: {'✓' if tool else '✗'}")

        # Check API client initialization
        print(f"   API clients: {len(executor.api_clients)}")
        for client_name in executor.api_clients.keys():
            print(f"      - {client_name}: ✓")

    else:
        print("⚠️  No research agent found for testing")

except Exception as e:
    print(f"❌ Execution system error: {e}")

# Test 6: Platform Integration
print("\n🏗️ TEST 6: Platform Integration")
print("-" * 40)
try:
    # Check if platform capabilities are injected
    platform_prompt = get_platform_awareness_prompt()
    print(f"✅ Platform awareness prompt: {len(platform_prompt)} characters")
    print(f"   Contains {platform_prompt.count('102+')} references to agent network")
    print(f"   Contains {platform_prompt.count('Content Studio')} references to AI Content Studio")

except Exception as e:
    print(f"❌ Platform integration error: {e}")

# Test 7: API Execution Endpoint
print("\n🚀 TEST 7: API Execution Test")
print("-" * 40)
try:
    headers = {
        'Authorization': f'Token {API_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Try to execute a simple task
    execution_data = {
        'agent_name': 'research-agent',
        'task': 'Test: What tools do you have access to?',
        'priority': 'normal'
    }

    response = requests.post(
        f'{BASE_URL}/api/v1/agents/execute/',
        headers=headers,
        json=execution_data,
        timeout=5
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Execution initiated: {result.get('execution_id', 'N/A')}")
        print(f"   Status: {result.get('status', 'Unknown')}")
    else:
        print(f"⚠️  Execution failed: Status {response.status_code}")

except requests.exceptions.Timeout:
    print("⚠️  API timeout - server may be processing")
except Exception as e:
    print(f"❌ API execution error: {e}")

# Test 8: Check Recent Executions
print("\n📊 TEST 8: Recent Executions Check")
print("-" * 40)
try:
    recent_executions = AgentExecution.objects.all().order_by('-created_at')[:5]

    if recent_executions:
        print(f"✅ Found {len(recent_executions)} recent executions:")
        for exec in recent_executions:
            print(f"   - {exec.agent_template.name}: {exec.status} ({exec.created_at.strftime('%Y-%m-%d %H:%M')})")
            if exec.result:
                result_preview = str(exec.result)[:100]
                print(f"     Result: {result_preview}...")
    else:
        print("⚠️  No recent executions found")

except Exception as e:
    print(f"❌ Execution history error: {e}")

# Summary
print("\n" + "=" * 80)
print("📈 FUNCTIONALITY VERIFICATION SUMMARY")
print("=" * 80)

functionality_checks = {
    "Agents Loaded": len(all_agents) > 100,
    "Tools Available": len(available_tools) > 5,
    "Shared Memory": 'success' in locals() and success,
    "Experience Sharing": 'exp_success' in locals() and exp_success,
    "Executor System": 'executor' in locals() and len(executor.tools) > 0,
    "Platform Integration": len(platform_prompt) > 1000,
}

working = sum(1 for v in functionality_checks.values() if v)
total = len(functionality_checks)

print(f"\n{'✅' if working == total else '⚠️ '} {working}/{total} systems functional\n")

for check, status in functionality_checks.items():
    print(f"  {'✅' if status else '❌'} {check}")

if working == total:
    print("\n🎉 ALL SYSTEMS OPERATIONAL! Your agents are ready to work!")
else:
    print(f"\n⚠️  {total - working} systems need attention")

print("\n💡 RECOMMENDATIONS:")
if 'missing' in locals() and missing:
    print("   1. Some agents are missing required tools - check tool installation")
if len(available_tools) < 5:
    print("   2. Limited tools available - verify tool imports and API keys")
if not recent_executions:
    print("   3. No recent executions - test with real tasks to verify execution flow")

print("\n" + "=" * 80)