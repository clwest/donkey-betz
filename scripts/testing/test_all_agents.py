#!/usr/bin/env python
"""
Test ALL Real Agents
Verify that all agents are working with real implementations
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from intelligence.real_agents import AgentFactory
from intelligence.agent_execution_pipeline import AgentExecutionPipeline
from intelligence.models import ActionPlan


async def test_individual_agents():
    """Test each agent individually"""
    print("\n" + "="*80)
    print("🤖 TESTING INDIVIDUAL AGENTS")
    print("="*80)

    test_agents = [
        ('content-creator', 'Create a blog post about AI benefits'),
        ('ml-analytics', 'Analyze user engagement patterns'),
        ('image-generator', 'Create a hero image for our landing page'),
        ('publishing-automation', 'Schedule posts across all platforms'),
        ('data-analyst', 'Analyze conversion rates and user behavior'),
        ('seo-optimizer', 'Optimize our content for search engines'),
        ('email-marketer', 'Create an email campaign for product launch'),
        ('social-media-scheduler', 'Schedule week of social media posts'),
        ('market-researcher', 'Research competitors in AI space')
    ]

    results = {}

    for agent_type, test_action in test_agents:
        print(f"\n📌 Testing {agent_type}...")

        try:
            agent = AgentFactory.create_agent(agent_type)
            instruction = {
                'action': test_action,
                'parameters': {
                    'platforms': ['twitter', 'linkedin'],
                    'keywords': ['AI', 'automation']
                },
                'expected_outcome': 'High quality output'
            }

            result = await agent.execute(instruction)

            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
                results[agent_type] = 'failed'
            else:
                print(f"   ✅ Success!")
                if 'file_created' in result:
                    print(f"   📄 File: {result['file_created']}")
                results[agent_type] = 'success'

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results[agent_type] = 'error'

    return results


async def test_pipeline_integration():
    """Test the full pipeline with real agents"""
    print("\n" + "="*80)
    print("🔄 TESTING PIPELINE INTEGRATION")
    print("="*80)

    # Find or create a test plan
    try:
        plan = ActionPlan.objects.filter(status='completed').first()
        if plan:
            print(f"✅ Using existing plan: {plan.opportunity_title}")
        else:
            print("⚠️ No completed plans found, creating test plan...")
            plan = ActionPlan.objects.create(
                opportunity_title="Test Multi-Agent Execution",
                opportunity_type="test",
                status="completed",
                progress=100,
                generated_content="Test plan with multiple agents",
                results={}
            )
    except Exception as e:
        print(f"❌ Error with plan: {str(e)}")
        return

    # Test pipeline execution
    pipeline = AgentExecutionPipeline()

    # Create test instructions
    test_instructions = [
        {
            'agent_type': 'content-creator',
            'action': 'Generate content about AI automation',
            'parameters': {},
            'context': {'plan_id': str(plan.id)}
        },
        {
            'agent_type': 'ml-analytics',
            'action': 'Analyze performance metrics',
            'parameters': {},
            'context': {'plan_id': str(plan.id)}
        },
        {
            'agent_type': 'seo-optimizer',
            'action': 'Optimize for search engines',
            'parameters': {},
            'context': {'plan_id': str(plan.id)}
        }
    ]

    print("\n🚀 Executing agents through pipeline...")
    for instruction in test_instructions:
        agent_type = instruction['agent_type']
        print(f"\n   Testing {agent_type}...")

        agent = pipeline._create_mock_agent(agent_type)  # This now creates REAL agents!
        result = await agent.execute(instruction)

        if 'error' in result:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ✅ Success!")
            if 'file_created' in result:
                print(f"   📄 Output: {result['file_created']}")


async def main():
    """Main test function"""
    print("\n" + "🎯"*40)
    print("REAL AGENT SYSTEM TEST - THE MOMENT OF TRUTH!")
    print("🎯"*40)

    # Test individual agents
    agent_results = await test_individual_agents()

    # Test pipeline integration
    await test_pipeline_integration()

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    success_count = sum(1 for r in agent_results.values() if r == 'success')
    total_count = len(agent_results)

    print(f"\n✅ Successful Agents: {success_count}/{total_count}")
    for agent, status in agent_results.items():
        emoji = "✅" if status == "success" else "❌"
        print(f"   {emoji} {agent}: {status}")

    if success_count == total_count:
        print("\n🎉 ALL AGENTS OPERATIONAL!")
        print("💯 SYSTEM IS AT 100% CAPABILITY!")
    else:
        print(f"\n⚠️ {total_count - success_count} agents need attention")

    # Check for generated files
    if os.path.exists('agent_outputs'):
        files = os.listdir('agent_outputs')
        print(f"\n📁 Generated {len(files)} output files in agent_outputs/")


if __name__ == "__main__":
    asyncio.run(main())