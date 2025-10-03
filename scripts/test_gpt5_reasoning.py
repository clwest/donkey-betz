#!/usr/bin/env python
"""
Test GPT-5 Reasoning Models Integration
Tests the updated agent_llm_integration with proper Responses API usage
"""

import os
import sys
import django
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_core.agents.agent_llm_integration import agent_llm_integration


async def test_gpt5_reasoning():
    """Test GPT-5 reasoning models with different configurations"""

    print("\n🧪 Testing GPT-5 Reasoning Models Integration\n")
    print("=" * 70)

    # Test 1: Simple task with minimal reasoning (gpt-5-nano)
    print("\n📝 Test 1: Simple Classification (gpt-5-nano, minimal reasoning)")
    print("-" * 70)

    result1 = await agent_llm_integration.generate_for_agent(
        agent_name="TestClassifier",
        prompt="Classify this text as positive, negative, or neutral: 'I love this product!'",
        model="gpt-5-nano",
        reasoning_effort="minimal",
        verbosity="low",
        max_output_tokens=50
    )

    if result1['success']:
        print(f"✅ Response: {result1['response']}")
        if result1.get('usage'):
            usage = result1['usage']
            print(f"📊 Tokens - Input: {usage.get('input_tokens')}, Output: {usage.get('output_tokens')}, Reasoning: {usage.get('reasoning_tokens', 0)}")
    else:
        print(f"❌ Error: {result1.get('error')}")

    # Test 2: Standard task with low reasoning (gpt-5-mini)
    print("\n\n📝 Test 2: Content Analysis (gpt-5-mini, low reasoning)")
    print("-" * 70)

    result2 = await agent_llm_integration.generate_for_agent(
        agent_name="TestAnalyzer",
        prompt="Write a haiku about artificial intelligence",
        model="gpt-5-mini",
        reasoning_effort="low",
        verbosity="medium",
        max_output_tokens=200
    )

    if result2['success']:
        print(f"✅ Response:\n{result2['response']}")
        if result2.get('usage'):
            usage = result2['usage']
            print(f"\n📊 Tokens - Input: {usage.get('input_tokens')}, Output: {usage.get('output_tokens')}, Reasoning: {usage.get('reasoning_tokens', 0)}")
    else:
        print(f"❌ Error: {result2.get('error')}")

    # Test 3: Complex task with medium reasoning (gpt-5-mini)
    print("\n\n📝 Test 3: Strategic Planning (gpt-5-mini, medium reasoning)")
    print("-" * 70)

    result3 = await agent_llm_integration.generate_for_agent(
        agent_name="TestStrategist",
        prompt="Create a 3-step plan to acquire freelance clients for a web development service",
        model="gpt-5-mini",
        reasoning_effort="medium",
        verbosity="medium",
        max_output_tokens=500
    )

    if result3['success']:
        print(f"✅ Response:\n{result3['response']}")
        if result3.get('usage'):
            usage = result3['usage']
            print(f"\n📊 Tokens - Input: {usage.get('input_tokens')}, Output: {usage.get('output_tokens')}, Reasoning: {usage.get('reasoning_tokens', 0)}")
    else:
        print(f"❌ Error: {result3.get('error')}")

    # Test 4: Multi-turn conversation with chain of thought
    print("\n\n📝 Test 4: Multi-turn with Chain of Thought (gpt-5-mini)")
    print("-" * 70)

    # First turn
    result4a = await agent_llm_integration.generate_for_agent(
        agent_name="TestConversation",
        prompt="What's the capital of France?",
        model="gpt-5-mini",
        reasoning_effort="minimal",
        verbosity="low",
        max_output_tokens=100
    )

    if result4a['success']:
        print(f"Turn 1 - Response: {result4a['response']}")
        response_id = result4a.get('response_id')

        if response_id:
            # Second turn with chain of thought
            result4b = await agent_llm_integration.generate_for_agent(
                agent_name="TestConversation",
                prompt="What's a famous landmark there?",
                model="gpt-5-mini",
                reasoning_effort="minimal",
                verbosity="low",
                max_output_tokens=100,
                previous_response_id=response_id  # Pass chain of thought!
            )

            if result4b['success']:
                print(f"Turn 2 - Response: {result4b['response']}")
                print(f"✅ Chain of thought maintained! (response_id: {response_id[:20]}...)")
            else:
                print(f"❌ Turn 2 Error: {result4b.get('error')}")
        else:
            print("⚠️  No response_id returned for chain of thought")
    else:
        print(f"❌ Turn 1 Error: {result4a.get('error')}")

    # Display usage statistics
    print("\n\n📊 Overall Usage Statistics")
    print("=" * 70)

    stats = agent_llm_integration.get_usage_stats()
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Total Input Tokens: {stats['total_tokens_in']}")
    print(f"Total Output Tokens: {stats['total_tokens_out']}")
    print(f"Total Cost: ${stats['total_cost']:.6f}")

    print("\n📈 By Agent:")
    for agent_name, agent_stats in stats['by_agent'].items():
        print(f"\n  {agent_name}:")
        print(f"    Requests: {agent_stats['requests']}")
        print(f"    Input tokens: {agent_stats['tokens_in']}")
        print(f"    Output tokens: {agent_stats['tokens_out']}")
        print(f"    Reasoning tokens: {agent_stats.get('reasoning_tokens', 0)}")
        print(f"    Cost: ${agent_stats['cost']:.6f}")

    print("\n" + "=" * 70)
    print("\n✅ GPT-5 Reasoning Integration Test Complete!\n")


if __name__ == "__main__":
    asyncio.run(test_gpt5_reasoning())
