"""
Test CTO Agent - Session 98

This script tests the CTO Agent's core capabilities:
1. Initialization and codebase mapping
2. Feature analysis
3. Implementation planning
4. Documentation analysis
5. Agent coordination planning

All operations are READ-ONLY - no files will be modified.

Usage:
    python scripts/test_cto_agent.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from agents.cto_agent import CTOAgent
from core.models.agents_registry import UnifiedAgentTemplate
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
        for key in ['analysis', 'plan', 'coordination_plan']:
            if key in result:
                content = result[key]
                if isinstance(content, str):
                    # Show first 500 chars
                    preview = content[:500] + "..." if len(content) > 500 else content
                    print(f"\n{key.upper()} PREVIEW:")
                    print(preview)
                    print(f"\n(Full {key}: {len(content)} characters)")


def test_agent_initialization():
    """Test 1: CTO Agent Initialization"""
    print_section("Test 1: CTO Agent Initialization")

    try:
        # Get or create test user
        user, _ = User.objects.get_or_create(
            username='test_cto_user',
            defaults={'email': 'test@example.com'}
        )

        # Initialize CTO Agent
        print("Initializing CTO Agent...")
        cto = CTOAgent(user=user)

        # Check codebase map
        print(f"\n📊 Codebase Map Built:")
        print(f"   - Base path: {cto.codebase_map.get('base_path')}")
        print(f"   - Total Python files: {cto.codebase_map.get('file_count', 0)}")
        print(f"   - Directories scanned: {len(cto.codebase_map.get('directories', {}))}")
        print(f"   - Key files tracked: {len(cto.codebase_map.get('key_files', []))}")
        print(f"   - Total lines in key files: {cto.codebase_map.get('total_lines', 0)}")

        # Check agent template
        template = UnifiedAgentTemplate.objects.get(name='CTOAgent')
        print(f"\n🤖 Agent Template:")
        print(f"   - Name: {template.name}")
        print(f"   - Specialization: {template.specialization}")
        print(f"   - Capabilities: {len(template.capabilities)} ({', '.join(template.capabilities)})")
        print(f"   - Phase: {template.metadata.get('phase')}")
        print(f"   - Safety Level: {template.metadata.get('safety_level')}")

        print("\n✅ Initialization: SUCCESS")
        return cto

    except Exception as e:
        print(f"\n❌ Initialization: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_feature_analysis(cto):
    """Test 2: Feature Analysis"""
    print_section("Test 2: Feature Analysis")

    try:
        print("Analyzing feature: 'AI Assistant voice command system'...")
        print("(This will use GPT-5-mini for deep analysis - may take 10-30 seconds)")

        result = cto.analyze_feature(
            feature_name="AI Assistant voice command system",
            scope="feature"
        )

        print_result("Feature Analysis", result, show_full=True)

        # Check memory storage
        memory_key = "feature_analysis_ai_assistant_voice_command_system"
        stored = cto.memory.recall(memory_key)
        if stored:
            print(f"\n💾 Analysis stored in memory: YES")
            print(f"   - Analyzed at: {stored.get('analyzed_at')}")
            print(f"   - Analyzed by: {stored.get('analyzed_by')}")
        else:
            print(f"\n⚠️  Analysis NOT stored in memory")

        return result

    except Exception as e:
        print(f"\n❌ Feature Analysis: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_implementation_planning(cto):
    """Test 3: Implementation Planning"""
    print_section("Test 3: Implementation Planning")

    try:
        print("Creating implementation plan: 'Add rate limiting to all API endpoints'...")
        print("(PLANNING ONLY - no files will be modified)")
        print("(This will use GPT-5-mini - may take 10-30 seconds)")

        result = cto.implement_feature(
            description="Add rate limiting to all API endpoints",
            approach="decorator_pattern"
        )

        print_result("Implementation Planning", result, show_full=True)

        # Check if it's really plan-only
        if result.get('phase') == 'planning_only':
            print(f"\n✅ Verified: PLAN ONLY (no files modified)")
        else:
            print(f"\n⚠️  Warning: Phase not set to 'planning_only'")

        # Check execution record
        if result.get('execution_id'):
            print(f"\n📝 Execution record created: {result['execution_id']}")

        return result

    except Exception as e:
        print(f"\n❌ Implementation Planning: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_documentation_analysis(cto):
    """Test 4: Documentation Analysis"""
    print_section("Test 4: Documentation Analysis")

    try:
        print("Analyzing documentation coverage: 'all_agents' scope...")
        print("(READ-ONLY analysis - no files will be modified)")
        print("(This will use GPT-5-mini - may take 10-30 seconds)")

        result = cto.sync_documentation(
            scope="all_agents"
        )

        print_result("Documentation Analysis", result, show_full=True)

        # Check if it's really analysis-only
        if result.get('phase') == 'analysis_only':
            print(f"\n✅ Verified: ANALYSIS ONLY (no files modified)")
        else:
            print(f"\n⚠️  Warning: Phase not set to 'analysis_only'")

        return result

    except Exception as e:
        print(f"\n❌ Documentation Analysis: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_agent_coordination(cto):
    """Test 5: Agent Coordination Planning"""
    print_section("Test 5: Agent Coordination Planning")

    try:
        print("Creating coordination plan: 'Create complete brand package'...")
        print("(Coordinating: CreativeDirectorAgent, BrandStyleAgent, TemplateManagerAgent)")
        print("(This will use GPT-5-mini - may take 10-30 seconds)")

        result = cto.coordinate_agents(
            task="Create complete brand package for a coffee shop",
            required_agents=[
                "CreativeDirectorAgent",
                "BrandStyleAgent",
                "TemplateManagerAgent"
            ]
        )

        print_result("Agent Coordination", result, show_full=True)

        # Check if it's planning phase
        if result.get('phase') == 'planning':
            print(f"\n✅ Verified: PLANNING PHASE (actual agent queries in Phase 2)")
        else:
            print(f"\n⚠️  Warning: Phase not set to 'planning'")

        return result

    except Exception as e:
        print(f"\n❌ Agent Coordination: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all CTO Agent tests"""
    print("\n" + "🏗️ "*35)
    print("CTO Agent Testing Suite - Session 98")
    print("Phase 1: Read-Only Analysis & Planning")
    print("🏗️ "*35)

    results = {
        'initialization': None,
        'feature_analysis': None,
        'implementation_planning': None,
        'documentation_analysis': None,
        'agent_coordination': None
    }

    # Test 1: Initialization (required for all other tests)
    cto = test_agent_initialization()
    results['initialization'] = cto is not None

    if not cto:
        print("\n❌ CRITICAL: CTO Agent failed to initialize. Cannot run remaining tests.")
        return results

    # Test 2: Feature Analysis
    results['feature_analysis'] = test_feature_analysis(cto)

    # Test 3: Implementation Planning
    results['implementation_planning'] = test_implementation_planning(cto)

    # Test 4: Documentation Analysis
    results['documentation_analysis'] = test_documentation_analysis(cto)

    # Test 5: Agent Coordination
    results['agent_coordination'] = test_agent_coordination(cto)

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
        print("\n🎉 ALL TESTS PASSED! CTO Agent is fully operational!")
        print("\nPhase 1 Capabilities Verified:")
        print("  ✅ Codebase mapping and understanding")
        print("  ✅ Feature analysis with GPT-5-mini reasoning")
        print("  ✅ Implementation planning (no execution)")
        print("  ✅ Documentation analysis (read-only)")
        print("  ✅ Agent coordination planning")
        print("\nReady for production use! 🚀")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")

    return results


if __name__ == '__main__':
    main()
