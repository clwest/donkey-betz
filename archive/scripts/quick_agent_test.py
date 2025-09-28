#!/usr/bin/env python3
"""
Quick Agent Test - Verify Working Execution

This script quickly tests that our agent executors are working properly
after the bug fixes.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

import django
django.setup()

from agents.executor_registry import execute_agent_by_name, ExecutionPriority


async def test_income_builder():
    """Test Income Builder with simple task"""
    print("🔍 Testing Income Builder...")

    task_data = {
        'task_type': 'analyze_opportunities',
        'user_profile': {
            'id': 'quick_test_user',
            'current_balance': 0.0,
            'skills': ['python', 'writing'],
            'skill_level': 'beginner',
            'available_hours_per_week': 10
        }
    }

    try:
        result = await execute_agent_by_name(
            'income_builder',
            task_data,
            user_id='quick_test',
            priority=ExecutionPriority.HIGH
        )

        if result.status.value == 'completed':
            print(f"   ✅ SUCCESS: {len(result.files_created)} files created")
            print(f"   💰 Cost: ${result.total_cost}")
            print(f"   ⏱️  Time: {result.execution_time_ms}ms")
            print(f"   🛠️  Tools: {', '.join(result.tools_used)}")
            return True
        else:
            print(f"   ❌ FAILED: {result.error_message}")
            return False

    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False


async def test_content_creator():
    """Test Content Creator with simple task"""
    print("\n✍️  Testing Content Creator...")

    task_data = {
        'content_type': 'blog_post',
        'topic': 'Quick test post',
        'target_audience': 'general',
        'word_count': 300
    }

    try:
        result = await execute_agent_by_name(
            'content_creator',
            task_data,
            user_id='quick_test',
            priority=ExecutionPriority.HIGH
        )

        if result.status.value == 'completed':
            print(f"   ✅ SUCCESS: {result.output.get('word_count', 0)} words generated")
            print(f"   📄 Files: {len(result.files_created)}")
            print(f"   💰 Cost: ${result.total_cost}")
            print(f"   🤖 Tokens: {result.tokens_used.get('total', 0)}")
            return True
        else:
            print(f"   ❌ FAILED: {result.error_message}")
            return False

    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False


async def test_payment_processor():
    """Test Payment Processor with simple task"""
    print("\n💳 Testing Payment Processor...")

    task_data = {
        'task_type': 'create_invoice',
        'invoice_type': 'one_time_service',
        'client_info': {
            'name': 'Quick Test Client',
            'email': 'test@example.com'
        },
        'amount': 100.0
    }

    try:
        result = await execute_agent_by_name(
            'payment_processor',
            task_data,
            user_id='quick_test',
            priority=ExecutionPriority.NORMAL
        )

        if result.status.value == 'completed':
            print(f"   ✅ SUCCESS: Invoice {result.output.get('invoice_id')} created")
            print(f"   💰 Amount: ${result.output.get('total_amount', 0):.2f}")
            print(f"   📄 Files: {len(result.files_created)}")
            return True
        else:
            print(f"   ❌ FAILED: {result.error_message}")
            return False

    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False


async def main():
    """Run quick tests"""
    print("🚀 Quick Agent Execution Test")
    print("=" * 40)

    results = []

    # Test each agent
    results.append(await test_income_builder())
    results.append(await test_content_creator())
    results.append(await test_payment_processor())

    # Show summary
    successful = sum(results)
    total = len(results)

    print(f"\n📊 RESULTS: {successful}/{total} agents working")

    if successful == total:
        print("🎉 ALL AGENTS ARE WORKING!")
        print("✅ System is ready for production use")
    else:
        print("⚠️  Some agents need attention")

    return successful == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)