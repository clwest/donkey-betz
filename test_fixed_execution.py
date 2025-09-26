#!/usr/bin/env python
"""Test Fixed Agent Execution"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.agents.sync_executor import SyncAgentExecutor

def test_execution():
    print("\n" + "="*60)
    print("🧪 TESTING FIXED AGENT EXECUTION")
    print("="*60)

    executor = SyncAgentExecutor()

    # Test 1: Content Creator
    print("\n📝 Test 1: Content Creator Agent")
    result = executor.execute(
        agent_name="content_creator",
        task_description="Write a 3-sentence description of AI agents",
        context={"test": True}
    )

    if result.get('success'):
        print("✅ SUCCESS!")
        result_text = str(result.get('result', ''))
        print(f"Generated: {result_text[:200]}...")
    else:
        print(f"❌ Failed: {result.get('error')}")

    # Test 2: Code Analyzer
    print("\n💻 Test 2: Code Analyzer Agent")
    result = executor.execute(
        agent_name="code_analyzer",
        task_description="Analyze the complexity of this project",
        context={"test": True}
    )

    if result.get('success'):
        print("✅ SUCCESS!")
        result_text = str(result.get('result', ''))
        print(f"Analysis: {result_text[:200]}...")
    else:
        print(f"❌ Failed: {result.get('error')}")

    # Test 3: Market Analyst
    print("\n📊 Test 3: Market Analyst Agent")
    result = executor.execute(
        agent_name="market_analyst",
        task_description="Analyze current AI market trends",
        context={"test": True}
    )

    if result.get('success'):
        print("✅ SUCCESS!")
        result_text = str(result.get('result', ''))
        print(f"Analysis: {result_text[:200]}...")
    else:
        print(f"❌ Failed: {result.get('error')}")

    print("\n" + "="*60)
    print("✨ Execution tests complete!")
    print("="*60)

if __name__ == "__main__":
    test_execution()