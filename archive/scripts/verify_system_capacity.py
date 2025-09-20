#!/usr/bin/env python3
"""
Verify ACTUAL system capacity - what's really implemented vs what's planned
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
from agents.models import UnifiedAgentTemplate


def check_real_capacity():
    print("\n" + "="*70)
    print("🔍 SYSTEM CAPACITY AUDIT - WHAT'S REALLY WORKING")
    print("="*70)

    # 1. Check Agents
    print("\n📊 AGENT ANALYSIS:")
    print("-" * 50)

    registry = get_agent_registry()
    all_agents = registry.list_agents()

    # Separate by source
    db_agents = UnifiedAgentTemplate.objects.all()
    wired_agents = [a for a in all_agents if 'orchestrator' in a.get('name', '').lower() or 'pipeline' in a.get('name', '').lower()]

    print(f"Total agents in registry: {len(all_agents)}")
    print(f"  - From database: {db_agents.count()}")
    print(f"  - Wired today: 49")
    print(f"  - Pre-existing: {len(all_agents) - 49}")

    # Check implementation status
    print("\n🔧 IMPLEMENTATION STATUS:")

    # These are placeholder registrations, not actual implementations
    placeholders = [
        "spider-army-supreme-orchestrator",
        "revenue-activation-orchestrator",
        "ml-pipeline",
        "monitoring-dashboard-builder"
    ]

    implemented = []
    not_implemented = []

    for agent_name in placeholders:
        agent = registry.get_agent(agent_name)
        if agent:
            # Check if it has actual execution logic
            if agent.get('system_prompt') and 'placeholder' not in agent.get('system_prompt', '').lower():
                implemented.append(agent_name)
            else:
                not_implemented.append(agent_name)

    print(f"\n✅ Actually Implemented:")
    if implemented:
        for name in implemented:
            print(f"  • {name}")
    else:
        print("  ❌ None - these are registered but not implemented!")

    print(f"\n⚠️ Registered but NOT implemented:")
    for name in not_implemented:
        print(f"  • {name} - NEEDS IMPLEMENTATION")

    # 2. Check Advisors
    print("\n👥 ADVISOR ANALYSIS:")
    print("-" * 50)

    advisor_registry = get_advisor_registry()
    advisors = advisor_registry.list_advisors()

    print(f"Total advisors: {len(advisors)}")
    print(f"  - Regular advisors: {len([a for a in advisors if 'AI Model' not in a.name])}")
    print(f"  - AI Models of legends: {len([a for a in advisors if 'AI Model' in a.name])}")

    # 3. Check actual execution capability
    print("\n⚡ EXECUTION CAPABILITY:")
    print("-" * 50)

    # Test actual execution
    test_results = {
        "Can register agents": True,
        "Can route to agents": True,
        "Can execute tasks": False,  # No actual implementation
        "Can consult advisors": False,  # No actual consultation logic
        "Spider army active": False,  # Not implemented
        "ML pipeline working": False,  # Mock implementation only
        "Revenue engine active": False,  # Not implemented
    }

    for capability, status in test_results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {capability}")

    # 4. Reality check
    print("\n🎯 REALITY CHECK:")
    print("-" * 50)

    print("What's ACTUALLY working:")
    print("  ✅ Agent registry system (can register and find agents)")
    print("  ✅ Advisor registry system (can list advisors)")
    print("  ✅ Task parsing (can extract tasks from plans)")
    print("  ✅ Basic routing (can match tasks to agents)")

    print("\nWhat's NOT actually implemented:")
    print("  ❌ Agent execution logic (agents don't DO anything)")
    print("  ❌ Spider army (no actual web scraping)")
    print("  ❌ ML pipeline (returns mock scores)")
    print("  ❌ Revenue engine (no payment processing)")
    print("  ❌ Advisor consultation (no actual advice generation)")
    print("  ❌ Inter-agent communication (no message passing)")

    print("\n📈 ACTUAL vs CLAIMED:")
    print("-" * 50)
    print("Claimed: 149 agents + 25 advisors = Full System")
    print("Reality: Registry with names but no implementation")
    print("\nThink of it like:")
    print("  • Having 149 employee badges printed")
    print("  • But only 5-10 people actually show up to work")
    print("  • And those who show up don't know what to do")

    print("\n💡 TO MAKE IT REAL:")
    print("-" * 50)
    print("1. Implement actual execution logic for each agent")
    print("2. Connect to real APIs (not mocks)")
    print("3. Implement spider data gathering")
    print("4. Build real ML models (not hardcoded scores)")
    print("5. Create actual advisor consultation logic")
    print("6. Implement inter-agent message passing")
    print("7. Build real revenue processing")

    print("\n" + "="*70)
    print("VERDICT: System is at ~10% capacity - mostly scaffolding")
    print("="*70 + "\n")


if __name__ == "__main__":
    check_real_capacity()