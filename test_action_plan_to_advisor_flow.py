#!/usr/bin/env python3
"""
Test the complete Action Plan to Advisor to Team flow

This script demonstrates:
1. Completing an Action Plan
2. Handing it off to an appropriate Advisor
3. Getting the Advisor's review and recommendations
4. Forming an execution team
5. Beginning execution
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Django setup
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from intelligence.action_plan_orchestrator import action_plan_orchestrator
from advisors.registry import advisor_registry
from agents.registry import agent_registry


async def test_complete_flow():
    """Test the complete flow from Action Plan to Team Execution"""

    print("\n" + "="*80)
    print(" ACTION PLAN → ADVISOR → TEAM FORMATION TEST ")
    print("="*80 + "\n")

    # Test different opportunity types
    opportunities = [
        "AI-Generated Digital Templates",
        "SaaS Micro-Product Development",
        "Freelance Content Writing Service",
        "Cryptocurrency Investment Strategy",
        "Real Estate Rental Income"
    ]

    for opportunity in opportunities:
        print(f"\n{'='*60}")
        print(f"Testing: {opportunity}")
        print('='*60)

        # Step 1: Get advisor recommendation
        print("\n1️⃣  Finding Best Advisor...")
        advisor_rec = await action_plan_orchestrator.get_advisor_recommendation_for_opportunity(opportunity)

        if advisor_rec["recommended_advisor"]:
            advisor = advisor_rec["recommended_advisor"]
            print(f"   ✅ Recommended: {advisor['name']} ({advisor['title']})")
            print(f"      - Expertise: {advisor['expertise_level']}")
            print(f"      - Experience: {advisor['years_experience']} years")
            print(f"      - Success Rate: {advisor['success_rate']:.0%}")
            print(f"      - Specializations: {', '.join(advisor['specializations'])}")

        # Step 2: Simulate the complete flow
        print("\n2️⃣  Processing Action Plan through Complete Flow...")
        result = await action_plan_orchestrator.simulate_complete_flow(opportunity)

        if result["status"] == "ready_for_execution":
            print("   ✅ Action Plan Processed Successfully!")

            # Show advisor review
            if "advisor_review" in result:
                review = result["advisor_review"]
                print(f"\n3️⃣  Advisor Review by {review['advisor']}:")
                print(f"   Budget Estimate: ${review['budget_estimate']:,.0f}")
                if review['timeline_adjustment']:
                    print(f"   Timeline Note: {review['timeline_adjustment']}")

                print("\n   Strengths Identified:")
                for strength in review["strengths"]:
                    print(f"   • {strength}")

                print("\n   Immediate Actions:")
                for i, action in enumerate(review["immediate_actions"], 1):
                    print(f"   {i}. {action}")

                print("\n   Success Metrics:")
                for metric in review["success_metrics"]:
                    print(f"   📊 {metric}")

            # Show team formation
            if "team" in result:
                team = result["team"]
                print(f"\n4️⃣  Team Formation:")
                print(f"   Team ID: {team['id']}")
                print(f"   Lead Agent: {team['lead']}")
                print(f"   Coordination: {team['coordination_model']}")
                print(f"   Execution Phases: {team['phases']}")

                print(f"\n   Core Agents ({len(team['core_agents'])}):")
                for agent in team["core_agents"][:5]:  # Show first 5
                    print(f"   • {agent}")

                if team["specialists"]:
                    print(f"\n   Specialist Agents ({len(team['specialists'])}):")
                    for agent in team["specialists"]:
                        print(f"   • {agent}")

            # Show execution status
            if "stages" in result and "execution_initiation" in result["stages"]:
                exec_stage = result["stages"]["execution_initiation"]
                print(f"\n5️⃣  Execution Status:")
                print(f"   Status: {exec_stage['execution_status']}")
                print(f"   Agents Activated: {len(exec_stage['agents_activated'])}")
                print(f"   Initial Tasks: {exec_stage['initial_tasks']}")

                if exec_stage['agents_activated']:
                    print(f"\n   Activated Agents:")
                    for agent in exec_stage['agents_activated'][:5]:  # Show first 5
                        print(f"   • {agent}")

        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

    # Summary
    print(f"\n\n{'='*80}")
    print(" FLOW TEST SUMMARY ")
    print('='*80)

    # Show active teams
    active_teams = action_plan_orchestrator.get_active_teams()
    print(f"\n📊 Active Teams: {len(active_teams)}")
    for team in active_teams:
        print(f"   • Team {team['team_id'][:20]}... (Plan: {team['plan_id'][:10]}...)")
        print(f"     Lead: {team['lead_agent']}, Size: {team['team_size']}, Phase: {team['current_phase']}")

    # Show advisor workload
    workload = action_plan_orchestrator.get_advisor_workload()
    if workload:
        print(f"\n👥 Advisor Workload:")
        for advisor_id, count in workload.items():
            advisor = advisor_registry.advisors.get(advisor_id)
            if advisor:
                print(f"   • {advisor.name}: {count} active review(s)")

    # System stats
    print(f"\n📈 System Statistics:")
    print(f"   Total Advisors Available: {len(advisor_registry.advisors)}")
    print(f"   Total Agents Available: {len(agent_registry.list_agents())}")
    print(f"   Active Plans: {len(action_plan_orchestrator.active_plans)}")
    print(f"   Plans in Execution: {len(action_plan_orchestrator.execution_status)}")

    print(f"\n✨ Complete flow test finished successfully!")


async def test_specific_advisor_matching():
    """Test advisor matching for specific scenarios"""

    print("\n" + "="*80)
    print(" ADVISOR MATCHING TEST ")
    print("="*80 + "\n")

    test_cases = [
        ("Cryptocurrency Trading Bot Development", "Should match crypto/tech advisors"),
        ("Real Estate Investment Trust Portfolio", "Should match real estate advisor"),
        ("AI Content Writing Service", "Should match content/AI advisors"),
        ("Options Trading Strategy Development", "Should match options trading advisor"),
        ("SaaS Platform for Small Businesses", "Should match tech/business advisors")
    ]

    for opportunity, expected in test_cases:
        print(f"\nOpportunity: {opportunity}")
        print(f"Expected: {expected}")

        rec = await action_plan_orchestrator.get_advisor_recommendation_for_opportunity(opportunity)

        if rec["recommended_advisor"]:
            print(f"Matched: {rec['recommended_advisor']['name']} ({rec['domain']})")
            print(f"Reasoning: {rec['reasoning']}")
        else:
            print("No advisor matched")


if __name__ == "__main__":
    print("\n🚀 Starting Action Plan → Advisor → Team Flow Test")
    print(f"   Timestamp: {datetime.now().isoformat()}")

    # Run the test
    asyncio.run(test_complete_flow())

    # Run advisor matching test
    asyncio.run(test_specific_advisor_matching())

    print("\n✅ All tests completed!")