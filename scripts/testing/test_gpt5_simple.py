#!/usr/bin/env python3
"""
Test GPT-5-mini with very simple prompts to isolate the compatibility issue
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.ai_providers import AIProviderManager

def test_simple_gpt5():
    """Test GPT-5-mini with progressively simple prompts"""

    ai_manager = AIProviderManager()
    provider = ai_manager.get_provider('openai')

    if not provider:
        print("❌ OpenAI provider not available")
        return

    # Test 1: Very simple prompt with GPT-4
    print("🧪 Test 1: Very simple prompt (GPT-4)")
    try:
        result1 = provider.generate_content(
            model='gpt-4o-mini',
            system_prompt="You are a helpful assistant.",
            user_prompt="Please write a simple business plan for selling digital templates.",
            config={'max_completion_tokens': 200}
        )

        if result1.success:
            print("✅ Test 1 SUCCESS")
            print(f"Content: {result1.content[:200]}...")
        else:
            print(f"❌ Test 1 FAILED: {result1.error_message}")
    except Exception as e:
        print(f"❌ Test 1 EXCEPTION: {e}")

    print()

    # Test 2: No system prompt
    print("🧪 Test 2: No system prompt (GPT-4)")
    try:
        result2 = provider.generate_content(
            model='gpt-4o-mini',
            system_prompt="",
            user_prompt="Please write a simple business plan for selling digital templates.",
            config={'max_completion_tokens': 200}
        )

        if result2.success:
            print("✅ Test 2 SUCCESS")
            print(f"Content: {result2.content[:200]}...")
        else:
            print(f"❌ Test 2 FAILED: {result2.error_message}")
    except Exception as e:
        print(f"❌ Test 2 EXCEPTION: {e}")

    print()

    # Test 3: Platform awareness but simple
    print("🧪 Test 3: Simple platform awareness (GPT-4)")
    try:
        result3 = provider.generate_content(
            model='gpt-4o-mini',
            system_prompt="You work for a platform with AI Content Studio and specialized agents.",
            user_prompt="How should someone create digital templates using our platform tools?",
            config={'max_completion_tokens': 200}
        )

        if result3.success:
            print("✅ Test 3 SUCCESS")
            print(f"Content: {result3.content[:200]}...")
        else:
            print(f"❌ Test 3 FAILED: {result3.error_message}")
    except Exception as e:
        print(f"❌ Test 3 EXCEPTION: {e}")

if __name__ == "__main__":
    print("🚀 Testing GPT-5-mini Compatibility")
    print("="*50)
    test_simple_gpt5()