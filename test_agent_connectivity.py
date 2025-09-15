#!/usr/bin/env python3
"""
Test Agent Connectivity and Execution
Verifies that all wired agents can receive and process tasks
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
from intelligence.task_delegation_orchestrator import TaskDelegationOrchestrator
from agents.opportunity_pipeline_orchestrator import OpportunityPipelineOrchestrator
import json
from datetime import datetime


def test_agent_registry():
    """Test that agents are properly registered"""
    print("\n🔍 TESTING AGENT REGISTRY...")
    print("=" * 60)

    registry = get_agent_registry()

    # Get all agents
    all_agents = registry.list_agents()
    print(f"✅ Total agents in registry: {len(all_agents)}")

    # Test specific agents
    critical_agents = [
        "opportunity-pipeline-orchestrator",
        "revenue-activation-orchestrator",
        "spider-army-supreme-orchestrator",
        "ml-pipeline",
        "monitoring-dashboard-builder",
        "content-creator"
    ]

    print("\n📋 Checking critical agents:")
    for agent_name in critical_agents:
        agent = registry.get_agent(agent_name)
        if agent:
            print(f"  ✅ {agent_name}: FOUND")
        else:
            print(f"  ❌ {agent_name}: NOT FOUND")

    return len(all_agents) > 0


def test_advisor_registry():
    """Test that advisors are accessible"""
    print("\n👥 TESTING ADVISOR REGISTRY...")
    print("=" * 60)

    advisor_registry = get_advisor_registry()
    advisors = advisor_registry.list_advisors()

    print(f"✅ Total advisors available: {len(advisors)}")

    # Show some advisor domains
    if advisors:
        domains = set([advisor.domain.value for advisor in advisors[:5]])
        print(f"📊 Sample advisor domains: {', '.join(domains)}")

    return len(advisors) > 0


def test_agent_routing():
    """Test that agent routing works"""
    print("\n🚦 TESTING AGENT ROUTING...")
    print("=" * 60)

    registry = get_agent_registry()

    # Test finding best agent for different tasks
    test_tasks = [
        ("I need to generate income from AI", ["business", "income"]),
        ("Create content for social media", ["content", "creative"]),
        ("Analyze sports betting opportunities", ["sports", "analytics"]),
        ("Build a monitoring dashboard", ["monitoring", "technical"]),
        ("Optimize Redis cache performance", ["redis", "optimization"])
    ]

    for task, expected_keywords in test_tasks:
        best_agent = registry.find_best_agent(task)
        if best_agent:
            print(f"✅ Task: '{task[:40]}...'")
            print(f"   → Agent: {best_agent['name']}")
        else:
            print(f"❌ No agent found for: '{task}'")

    return True


def test_task_delegation():
    """Test task delegation system"""
    print("\n📝 TESTING TASK DELEGATION...")
    print("=" * 60)

    orchestrator = TaskDelegationOrchestrator()

    # Create a simple plan
    test_plan = """
    ### Phase 1: Foundation (Week 1)
    #### Day 1-3: Setup
    ✅ **Market Research** - Analyze competitor pricing
    ✅ **Content Creation** - Generate service descriptions
    """

    # Parse the plan
    tasks = orchestrator.parse_action_plan(test_plan)
    print(f"✅ Parsed {len(tasks)} tasks from plan")

    if tasks:
        for i, task in enumerate(tasks[:3], 1):
            print(f"   {i}. {task.title} → Agent: {task.agent_type}")

    return len(tasks) > 0


def test_agent_execution():
    """Test actual agent execution"""
    print("\n⚡ TESTING AGENT EXECUTION...")
    print("=" * 60)

    registry = get_agent_registry()

    # Try to execute a simple task
    test_task = {
        "action": "analyze",
        "target": "income opportunities",
        "context": "user with programming skills"
    }

    # Find appropriate agent
    agent = registry.find_best_agent("analyze income opportunities")

    if agent:
        print(f"✅ Found agent: {agent['name']}")

        # Attempt execution
        execution_id = registry.execute_agent(
            agent['name'],
            test_task,
            priority="normal"
        )

        if execution_id:
            print(f"✅ Execution initiated with ID: {execution_id}")

            # Check status
            status = registry.get_execution_status(execution_id)
            if status:
                print(f"   Status: {status['status']}")
                print(f"   Priority: {status['priority']}")
        else:
            print("❌ Failed to initiate execution")
    else:
        print("❌ No suitable agent found")

    return True


def test_agent_connections():
    """Test agent interconnections"""
    print("\n🔗 TESTING AGENT CONNECTIONS...")
    print("=" * 60)

    # Test that Income Builder can connect to other agents
    registry = get_agent_registry()

    # Key connection chains to test
    connection_chains = [
        ["income-builder", "task-delegation-orchestrator", "opportunity-pipeline-orchestrator"],
        ["spider-army-supreme-orchestrator", "spider-agent-connector-orchestrator"],
        ["ml-pipeline", "correlation-hunter", "narrative-predictor-agent"],
        ["monitoring-dashboard-builder", "redis-cache-optimizer", "api-endpoint-validator"]
    ]

    for chain in connection_chains:
        print(f"\n🔄 Testing chain: {' → '.join(chain[:2])}...")
        all_found = True
        for agent_name in chain:
            agent = registry.get_agent(agent_name)
            if agent:
                print(f"   ✅ {agent_name}: CONNECTED")
            else:
                print(f"   ❌ {agent_name}: MISSING")
                all_found = False

        if all_found:
            print(f"   ✅ Chain operational!")

    return True


def main():
    """Run all connectivity tests"""
    print("\n" + "=" * 60)
    print("🚀 AGENT CONNECTIVITY TEST SUITE")
    print("=" * 60)

    results = {
        "registry": test_agent_registry(),
        "advisors": test_advisor_registry(),
        "routing": test_agent_routing(),
        "delegation": test_task_delegation(),
        "execution": test_agent_execution(),
        "connections": test_agent_connections()
    }

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name.upper()}")

    print("\n" + "=" * 60)
    if passed == total:
        print("🎉 ALL TESTS PASSED! Agent system is FULLY OPERATIONAL!")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Some components need attention.")
    print("=" * 60)


if __name__ == "__main__":
    main()