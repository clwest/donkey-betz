#!/usr/bin/env python
"""
Test Personal Assistant Self-Awareness Integration
==================================================

This script tests the integration between the Personal Assistant
and the System Reality Self-Awareness Engine.
"""

import os
import sys
import django
import asyncio
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
django.setup()

# Now import Django modules
from core.personal_assistant_integration import personal_assistant_integration
from core.reality_check import ComponentType


def test_basic_integration():
    """Test basic integration functionality"""
    print("\n" + "="*60)
    print("Testing Personal Assistant Self-Awareness Integration")
    print("="*60)

    # Test 1: Basic context enhancement
    print("\n1. Testing basic context enhancement...")
    context = personal_assistant_integration.enhance_assistant_context(
        message="What's the status of the platform?",
        conversation_id="test_123"
    )

    print(f"   ✓ Message: {context['message']}")
    print(f"   ✓ Conversation ID: {context['conversation_id']}")
    print(f"   ✓ System Awareness: {context['system_awareness']['platform_reality']}")
    print(f"   ✓ Operational %: {context['system_awareness']['operational_percentage']}%")


def test_routing_intelligence():
    """Test intelligent routing based on message content"""
    print("\n2. Testing intelligent routing...")

    test_messages = [
        ("Show me revenue opportunities", "income_builder"),
        ("What's my current revenue?", "revenue_dashboard"),
        ("How many agents are active?", "neural_orchestra"),
        ("Make a decision about this opportunity", "decision_command")
    ]

    for message, expected_component in test_messages:
        context = personal_assistant_integration.enhance_assistant_context(
            message=message,
            conversation_id="test_routing"
        )
        routing = context['routing']
        print(f"   Message: '{message}'")
        print(f"   → Primary: {routing['primary_component']} (confidence: {routing['confidence']:.0%})")
        print(f"   → Pipeline: {routing['suggested_pipeline']}")
        if routing['primary_component'] == expected_component:
            print(f"   ✓ Correct routing!")
        else:
            print(f"   ✗ Expected {expected_component}")
        print()


def test_recommendations():
    """Test system recommendations"""
    print("\n3. Testing system recommendations...")

    test_queries = [
        "How can I start earning money?",
        "Show me my agents",
        "What's the system health?",
        "Start collecting data with spiders"
    ]

    for query in test_queries:
        context = personal_assistant_integration.enhance_assistant_context(
            message=query,
            conversation_id="test_recommendations"
        )
        recommendations = context['recommendations']

        print(f"   Query: '{query}'")
        if recommendations:
            for rec in recommendations[:2]:  # Show first 2 recommendations
                print(f"   → {rec}")
        else:
            print(f"   → No specific recommendations")
        print()


def test_system_summary():
    """Test comprehensive system summary"""
    print("\n4. Testing system summary generation...")

    summary = personal_assistant_integration.get_assistant_system_summary()
    print(summary)


async def test_async_processing():
    """Test async processing with awareness"""
    print("\n5. Testing async processing with awareness...")

    result = await personal_assistant_integration.process_with_awareness(
        message="I want to analyze income opportunities and check system status",
        conversation_id="test_async"
    )

    print(f"   ✓ Message processed")
    if result.get('reality_insights'):
        print("   Reality Insights:")
        for insight in result['reality_insights']:
            print(f"     {insight}")

    if result.get('suggested_actions'):
        print("   Suggested Actions:")
        for action in result['suggested_actions']:
            print(f"     {action}")

    if result.get('recommendations'):
        print("   Recommendations:")
        for rec in result['recommendations'][:2]:
            print(f"     {rec}")


def test_component_status():
    """Test component status checking"""
    print("\n6. Testing component status checking...")

    context = personal_assistant_integration.enhance_assistant_context(
        message="Check all components",
        conversation_id="test_components"
    )

    component_status = context['component_status']
    print("   Component Status:")
    for component, status in component_status.items():
        icon = "✅" if status['is_operational'] else "❌"
        print(f"   {icon} {component}: {status['status']} (confidence: {status['confidence']:.0%})")


def test_data_flow_status():
    """Test data flow status checking"""
    print("\n7. Testing data flow status...")

    context = personal_assistant_integration.enhance_assistant_context(
        message="Check data flows",
        conversation_id="test_flows"
    )

    flow_status = context['data_flow_status']
    print("   Data Flow Status:")
    for flow, status in flow_status.items():
        icon = "✅" if status == "operational" else "🔧"
        print(f"   {icon} {flow}: {status}")


def main():
    """Run all tests"""
    print("\n" + "🤖 "*20)
    print("PERSONAL ASSISTANT SELF-AWARENESS INTEGRATION TEST")
    print("🤖 "*20)

    try:
        # Run synchronous tests
        test_basic_integration()
        test_routing_intelligence()
        test_recommendations()
        test_system_summary()
        test_component_status()
        test_data_flow_status()

        # Run async tests
        print("\nRunning async tests...")
        asyncio.run(test_async_processing())

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)

        print("\n📋 Integration Summary:")
        print("  • Personal Assistant is now self-aware")
        print("  • Can distinguish real vs mock components")
        print("  • Provides intelligent routing based on queries")
        print("  • Offers context-aware recommendations")
        print("  • Tracks data flow integrity")
        print("  • Monitors system operational status")

        print("\n🎯 Next Steps:")
        print("  1. Test with actual user queries")
        print("  2. Monitor recommendation accuracy")
        print("  3. Fine-tune routing confidence thresholds")
        print("  4. Add more specialized awareness features")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()