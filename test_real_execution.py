#!/usr/bin/env python
"""TEST REAL AGENT EXECUTION"""
import os
import sys
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.agents.concrete_executor import ConcreteAgentExecutor
from backend.agents.concrete_executor import execute_agent_directly

async def test_agents():
    print("\n" + "="*60)
    print("🧪 TESTING REAL AGENT EXECUTION")
    print("="*60)

    # Test content creator agent
    result = await execute_agent_directly(
        agent_name="content_creator",
        task={
            "description": "Write a short paragraph about the benefits of AI agents",
            "type": "content_generation"
        }
    )

    print("\n📋 Content Creator Result:")
    if result.get('success'):
        print(f"✅ SUCCESS!")
        output = result.get('result', '')
        if isinstance(output, str):
            print(f"Generated: {output[:200]}")
        else:
            print(f"Result: {str(output)[:200]}")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown')}")

    # Test another agent
    result2 = await execute_agent_directly(
        agent_name="code_analyzer",
        task={
            "description": "Analyze the complexity of this codebase",
            "type": "analysis"
        }
    )

    print("\n📋 Code Analyzer Result:")
    if result2.get('success'):
        print(f"✅ SUCCESS!")
        print(f"Analysis: {str(result2.get('result', ''))[:200]}")
    else:
        print(f"❌ FAILED: {result2.get('error', 'Unknown')}")

    print("\n" + "="*60)
    print("✨ REALITY CHECK:")
    
    # Check if results contain real data
    if result.get('success') and len(str(result.get('result', ''))) > 50:
        print("✅ Agents are generating REAL content!")
    else:
        print("⚠️  Agents may be returning mock data")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_agents())
