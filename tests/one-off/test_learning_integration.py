#!/usr/bin/env python
"""
Test Learning Integration - Priority 5
Session 462: Verify learning hooks are firing
"""

import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.agents.stocks.market_intelligence_coordinator import run_market_intelligence_desk
from core.models_unified_system import MarketIntelligenceBrief, CoordinatorOutcome, AgentMemory, Agent

def test_learning_integration():
    """Test that learning hooks fire and create outcomes + memories."""
    print("\n" + "="*80)
    print("🧪 TESTING LEARNING INTEGRATION - PRIORITY 5")
    print("="*80)

    # Clean up any existing brief for today
    today = date.today()
    MarketIntelligenceBrief.objects.filter(brief_date=today).delete()
    print(f"\n✅ Cleaned up any existing brief for {today}")

    # Get baseline counts
    try:
        coordinator_agent = Agent.objects.get(name="MarketIntelligenceCoordinator")
        initial_outcomes = CoordinatorOutcome.objects.filter(agents_used__contains=["MarketIntelligenceCoordinator"]).count()
        initial_memories = AgentMemory.objects.filter(agent=coordinator_agent).count()
        print(f"\n📊 Baseline Counts:")
        print(f"   CoordinatorOutcomes: {initial_outcomes}")
        print(f"   AgentMemories: {initial_memories}")
    except Agent.DoesNotExist:
        print(f"\n⚠️ MarketIntelligenceCoordinator agent not in database - will be created on first run")
        initial_outcomes = 0
        initial_memories = 0

    # Run the coordinator
    print("\n" + "="*80)
    print("🔵 Running Market Intelligence Desk...")
    print("="*80)

    result = run_market_intelligence_desk()

    if not result.get('success'):
        print(f"❌ ERROR: {result}")
        return

    print(f"\n✅ Market Intelligence Desk completed successfully")

    # Check if learning hooks fired
    print("\n" + "="*80)
    print("🔍 Checking Learning Integration:")
    print("="*80)

    try:
        coordinator_agent = Agent.objects.get(name="MarketIntelligenceCoordinator")
        final_outcomes = CoordinatorOutcome.objects.filter(agents_used__contains=["MarketIntelligenceCoordinator"]).count()
        final_memories = AgentMemory.objects.filter(agent=coordinator_agent).count()

        outcomes_created = final_outcomes - initial_outcomes
        memories_created = final_memories - initial_memories

        print(f"\n📈 After Execution:")
        print(f"   CoordinatorOutcomes: {final_outcomes} (+{outcomes_created})")
        print(f"   AgentMemories: {final_memories} (+{memories_created})")

        # Verify learning hooks fired
        success = True
        if outcomes_created < 1:
            print(f"\n❌ FAILED: No CoordinatorOutcome created")
            print(f"   Expected: At least 1 new outcome")
            print(f"   Got: {outcomes_created}")
            success = False
        else:
            print(f"\n✅ CoordinatorOutcome created: {outcomes_created}")
            # Get the latest outcome
            latest_outcome = CoordinatorOutcome.objects.filter(
                agents_used__contains=["MarketIntelligenceCoordinator"]
            ).order_by('-created_at').first()
            if latest_outcome:
                print(f"   Query Type: {latest_outcome.query_type}")
                print(f"   Outcome: {latest_outcome.outcome_type}")
                print(f"   Execution Time: {latest_outcome.execution_time_ms}ms")
                print(f"   Spider Data Used: {latest_outcome.spider_data_used}")

        if memories_created < 1:
            print(f"\n❌ FAILED: No AgentMemory created")
            print(f"   Expected: At least 1 new memory")
            print(f"   Got: {memories_created}")
            success = False
        else:
            print(f"\n✅ AgentMemory created: {memories_created}")
            # Get the latest memory
            latest_memory = AgentMemory.objects.filter(
                agent=coordinator_agent
            ).order_by('-created_at').first()
            if latest_memory:
                print(f"   Memory Type: {latest_memory.memory_type}")
                print(f"   Importance: {latest_memory.importance_score}")
                print(f"   Content: {latest_memory.content[:100]}...")

        # Summary
        print("\n" + "="*80)
        print("📊 PRIORITY 5 STATUS:")
        print("="*80)
        if success:
            print("   ✅ COMPLETE - Learning hooks are WORKING!")
            print(f"   - CoordinatorOutcome hook: ✅ Fired ({outcomes_created} created)")
            print(f"   - AgentMemory hook: ✅ Fired ({memories_created} created)")
        else:
            print("   ❌ FAILED - Learning hooks not firing correctly")
        print("="*80 + "\n")

    except Agent.DoesNotExist:
        print(f"\n❌ FAILED: MarketIntelligenceCoordinator agent not found in database")
        print("   Learning hooks may not be wired correctly")

if __name__ == '__main__':
    test_learning_integration()
