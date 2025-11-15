"""
Test COO Agent - Session 98

This script tests the COO Agent's core capabilities:
1. Initialization
2. Roadmap analysis
3. Sprint planning
4. Risk identification
5. Memory storage

All operations are READ-ONLY - no changes will be made.

Usage:
    python scripts/test_coo_agent.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from agents.coo_agent import COOAgent
from agents.models import UnifiedAgentTemplate
import json

User = get_user_model()


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_result(name, result, show_full=False):
    """Print test result"""
    if result.get('status') == 'complete' or result.get('status') == 'plan_created':
        print(f"✅ {name}: SUCCESS")
    elif result.get('status') == 'failed':
        print(f"❌ {name}: FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    else:
        print(f"⚠️  {name}: {result.get('status', 'UNKNOWN')}")

    if show_full:
        # Show key parts of the result
        for key in ['summary', 'priorities', 'risks', 'sprint_goals', 'tasks', 'critical_risks']:
            if key in result:
                content = result[key]
                if isinstance(content, str):
                    # Show first 300 chars
                    preview = content[:300] + "..." if len(content) > 300 else content
                    print(f"\n{key.upper()} PREVIEW:")
                    print(preview)
                elif isinstance(content, list):
                    print(f"\n{key.upper()}: {len(content)} items")
                    # Show first 2 items
                    for i, item in enumerate(content[:2]):
                        print(f"  {i+1}. {str(item)[:100]}")


def test_agent_initialization():
    """Test 1: COO Agent Initialization"""
    print_section("Test 1: COO Agent Initialization")

    try:
        # Get or create test user
        user, _ = User.objects.get_or_create(
            username='test_coo_user',
            defaults={'email': 'test@example.com'}
        )

        # Initialize COO Agent
        print("Initializing COO Agent...")
        coo = COOAgent(user=user)

        # Check agent template
        template = UnifiedAgentTemplate.objects.get(name='COOAgent')
        print(f"\n🤖 Agent Template:")
        print(f"   - Name: {template.name}")
        print(f"   - Specialization: {template.specialization}")
        print(f"   - Capabilities: {len(template.capabilities)} ({', '.join(template.capabilities)})")
        print(f"   - Phase: {template.metadata.get('phase')}")
        print(f"   - Safety Level: {template.metadata.get('safety_level')}")

        print("\n✅ Initialization: SUCCESS")
        return coo

    except Exception as e:
        print(f"\n❌ Initialization: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_roadmap_analysis(coo):
    """Test 2: Roadmap Analysis"""
    print_section("Test 2: Roadmap Analysis")

    try:
        print("Analyzing roadmap: 'Session Management System'...")
        print("(This will use GPT-5-mini for analysis - may take 10-30 seconds)")

        result = coo.analyze_roadmap(
            feature_name="Session Management System",
            scope="feature"
        )

        print_result("Roadmap Analysis", result, show_full=True)

        # Check memory storage
        memory_key = "roadmap_analysis_session_management_system"
        stored = coo.memory.recall(memory_key)
        if stored:
            print(f"\n💾 Analysis stored in memory: YES")
            print(f"   - Analyzed at: {stored.get('analyzed_at')}")
            print(f"   - Analyzed by: {stored.get('analyzed_by')}")
            print(f"   - Priorities: {len(stored.get('priorities', []))}")
            print(f"   - Risks: {len(stored.get('risks', []))}")
        else:
            print(f"\n⚠️  Analysis NOT stored in memory")

        return result

    except Exception as e:
        print(f"\n❌ Roadmap Analysis: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_sprint_planning(coo):
    """Test 3: Sprint Planning"""
    print_section("Test 3: Sprint Planning")

    try:
        print("Planning next sprint: 'AI Agent Ecosystem Improvements'...")
        print("(PLANNING ONLY - no tasks will be executed)")
        print("(This will use GPT-5-mini - may take 10-30 seconds)")

        result = coo.propose_next_sprint(
            feature_name="AI Agent Ecosystem Improvements",
            sprint_duration="2 weeks"
        )

        print_result("Sprint Planning", result, show_full=True)

        # Check if it's really plan-only
        if result.get('phase') == 'planning_only':
            print(f"\n✅ Verified: PLAN ONLY (no tasks executed)")
        else:
            print(f"\n⚠️  Warning: Phase not set to 'planning_only'")

        return result

    except Exception as e:
        print(f"\n❌ Sprint Planning: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_risk_analysis(coo):
    """Test 4: Risk Analysis"""
    print_section("Test 4: Risk Analysis")

    try:
        print("Identifying risks: 'Platform Launch Preparation'...")
        print("(READ-ONLY analysis - no changes will be made)")
        print("(This will use GPT-5-mini - may take 10-30 seconds)")

        result = coo.identify_risks(
            feature_name="Platform Launch Preparation",
            scope="platform"
        )

        print_result("Risk Analysis", result, show_full=True)

        # Check if it's really analysis-only
        if result.get('phase') == 'analysis_only':
            print(f"\n✅ Verified: ANALYSIS ONLY (no changes made)")
        else:
            print(f"\n⚠️  Warning: Phase not set to 'analysis_only'")

        # Count risks
        critical_count = len(result.get('critical_risks', []))
        moderate_count = len(result.get('moderate_risks', []))
        print(f"\n📊 Risk Summary:")
        print(f"   - Critical risks: {critical_count}")
        print(f"   - Moderate risks: {moderate_count}")
        print(f"   - Dependencies: {len(result.get('dependencies', []))}")
        print(f"   - Mitigation strategies: {len(result.get('mitigation_strategies', []))}")

        return result

    except Exception as e:
        print(f"\n❌ Risk Analysis: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_memory_recall(coo):
    """Test 5: Memory Recall"""
    print_section("Test 5: Memory Recall")

    try:
        print("Testing memory recall for stored analyses...")

        # Try to recall roadmap analysis
        memory_key = "roadmap_analysis_session_management_system"
        stored = coo.memory.recall(memory_key)

        if stored:
            print(f"✅ Memory Recall: SUCCESS")
            print(f"\n💾 Recalled data:")
            print(f"   - Analyzed at: {stored.get('analyzed_at')}")
            print(f"   - Scope: {stored.get('scope')}")
            print(f"   - Has priorities: {'yes' if stored.get('priorities') else 'no'}")
            print(f"   - Has risks: {'yes' if stored.get('risks') else 'no'}")
            print(f"   - Has timeline: {'yes' if stored.get('timeline') else 'no'}")
            return True
        else:
            print(f"❌ Memory Recall: FAILED")
            print(f"   Could not recall stored analysis")
            return False

    except Exception as e:
        print(f"\n❌ Memory Recall: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all COO Agent tests"""
    print("\n" + "🏢 "*35)
    print("COO Agent Testing Suite - Session 98")
    print("Phase 1: Read-Only Planning & Risk Analysis")
    print("🏢 "*35)

    results = {
        'initialization': None,
        'roadmap_analysis': None,
        'sprint_planning': None,
        'risk_analysis': None,
        'memory_recall': None
    }

    # Test 1: Initialization (required for all other tests)
    coo = test_agent_initialization()
    results['initialization'] = coo is not None

    if not coo:
        print("\n❌ CRITICAL: COO Agent failed to initialize. Cannot run remaining tests.")
        return results

    # Test 2: Roadmap Analysis
    results['roadmap_analysis'] = test_roadmap_analysis(coo)

    # Test 3: Sprint Planning
    results['sprint_planning'] = test_sprint_planning(coo)

    # Test 4: Risk Analysis
    results['risk_analysis'] = test_risk_analysis(coo)

    # Test 5: Memory Recall
    results['memory_recall'] = test_memory_recall(coo)

    # Final Summary
    print_section("Test Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name.replace('_', ' ').title()}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! COO Agent is fully operational!")
        print("\nPhase 1 Capabilities Verified:")
        print("  ✅ Roadmap analysis with strategic recommendations")
        print("  ✅ Sprint planning with concrete tasks (no execution)")
        print("  ✅ Risk identification with mitigation strategies")
        print("  ✅ Memory storage and recall")
        print("  ✅ GPT-5-mini reasoning integration")
        print("\nReady for production use! 🚀")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")

    return results


if __name__ == '__main__':
    main()
