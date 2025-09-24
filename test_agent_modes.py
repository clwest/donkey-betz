"""
Test script to verify both demo and real mode work for agent execution
"""

import os
import json
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.views_deployment_execute_improved import execute_agents_improved
from agents.proper_agent_executor import execute_agents_properly
from core.models import GeneratedProject


def test_real_mode():
    """Test real mode with actual LLM calls"""
    print("\n=== Testing REAL Mode (LLM-Powered) ===")

    # Create test project synchronously
    project = GeneratedProject.objects.create(
        name="Test Real Mode Project",
        project_type="ecommerce",
        description="Test real agent execution",
        status='generating',
        agents_used=['Business Agent']
    )

    task_config = {
        'project_type': 'ecommerce',
        'ml_features': ['recommendations'],
        'requirements': {
            'target_market': 'Small businesses',
            'budget': '10000',
            'timeline': '3 months'
        }
    }

    try:
        # Use the synchronous wrapper function
        results = execute_agents_properly(['Business Agent'], project, task_config)

        for result in results:
            if result['success']:
                print(f"✅ Success: {result['agent']} executed task: {result['task']}")
                print(f"   Created: {result.get('file_created', 'N/A')}")
                print(f"   Size: {result.get('content_length', 0)} bytes")

                # Check if it's actual business strategy, not just code
                if result.get('file_created', '').endswith('.md'):
                    print("   ✅ Generated business strategy document (not Python code)")
                elif result.get('file_created', '').endswith('.json'):
                    print("   ✅ Generated structured data (not Python code)")
                else:
                    print("   ⚠️  Check output format")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_demo_mode():
    """Test demo mode with pre-generated templates"""
    print("\n=== Testing DEMO Mode (Pre-generated) ===")

    from agents.real_code_generator import RealCodeGenerator

    try:
        result = RealCodeGenerator.generate_code_by_agent(
            'Business Agent', 'ecommerce', ['recommendations']
        )

        print(f"✅ Generated: {result['filename']}")
        print(f"   Size: {len(result['code'])} bytes")
        print(f"   Language: {result['language']}")

        # Check if it's just Python code
        if result['filename'].endswith('.py'):
            print("   ⚠️  Demo mode generates Python code (not business docs)")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests"""
    print("Testing Agent Execution Modes")
    print("=" * 50)

    # Test demo mode
    test_demo_mode()

    # Test real mode
    test_real_mode()

    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nSummary:")
    print("- Demo Mode: Fast, generates Python code templates")
    print("- Real Mode: Uses LLM to generate actual deliverables (strategies, schemas, etc.)")


if __name__ == "__main__":
    main()