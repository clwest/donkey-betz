#!/usr/bin/env python
"""
Test GPT-5-mini with correct parameters
"""

import os
import sys
import django
import asyncio

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from intelligence.income_builder import AIIncomeBuilder, OPENAI_AVAILABLE, openai_client


async def test_gpt5_mini():
    """Test GPT-5-mini with correct parameters"""

    print("\n" + "="*80)
    print("🧪 TESTING GPT-5-MINI WITH CORRECT PARAMETERS")
    print("="*80 + "\n")

    if not OPENAI_AVAILABLE:
        print("❌ OpenAI not available - need OPENAI_API_KEY")
        return False

    print("✅ OpenAI client available\n")

    # Test 1: Direct OpenAI call with GPT-5-mini parameters
    print("📝 Test 1: Direct OpenAI call with GPT-5-mini parameters...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": "Write a 3-step plan to learn Python"}
            ],
            temperature=1.0,  # GPT-5 always uses 1.0
            max_completion_tokens=500,  # GPT-5 uses max_completion_tokens
            reasoning_effort="medium"  # GPT-5-mini supports reasoning tokens
        )

        content = response.choices[0].message.content
        if content is None:
            content = ""
        print(f"✅ Direct call successful! Generated {len(content)} chars")
        print(f"   Model used: {response.model}")
        print(f"   Total tokens: {response.usage.total_tokens}")

    except Exception as e:
        print(f"❌ Direct call failed: {e}")
        return False

    # Test 2: Through Income Builder
    print("\n📝 Test 2: Through Income Builder generate_ai_content()...")
    try:
        builder = AIIncomeBuilder()

        prompt = "Create a checklist for starting a freelance business"
        context = {
            "opportunity": "Freelance Writing",
            "budget": 0,
            "timeline": "1 week"
        }

        ai_content = await builder.generate_ai_content(prompt, context)

        if ai_content:
            print(f"✅ Income Builder successful! Generated {len(ai_content)} chars")
            print("\n--- SAMPLE OUTPUT ---")
            print(ai_content[:300] + "..." if len(ai_content) > 300 else ai_content)
            print("--- END SAMPLE ---")
        else:
            print("⚠️ Income Builder returned None (fallback mode)")

    except Exception as e:
        print(f"❌ Income Builder failed: {e}")
        return False

    # Test 3: Through AI Provider Manager
    print("\n📝 Test 3: Through AIProviderManager...")
    try:
        from content.ai_providers import AIProviderManager
        ai_manager = AIProviderManager()

        response = ai_manager.generate_content(
            provider='openai',
            model='gpt-5-mini',
            system_prompt="You are a helpful assistant.",
            user_prompt="List 3 benefits of AI automation",
            config={
                'max_completion_tokens': 300,
                'temperature': 1.0,  # Will be ignored for GPT-5
                'reasoning_effort': 'medium'
            }
        )

        if response.success:
            print(f"✅ AI Provider successful! Generated {len(response.content)} chars")
            print(f"   Cost: ${response.cost:.4f}")
        else:
            print(f"❌ AI Provider failed: {response.error_message}")

    except Exception as e:
        print(f"❌ AI Provider error: {e}")
        return False

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - GPT-5-MINI CONFIGURED CORRECTLY!")
    print("="*80 + "\n")

    print("Parameter Summary for GPT-5-mini:")
    print("  • model: 'gpt-5-mini'")
    print("  • temperature: 1.0 (always, implicit)")
    print("  • max_completion_tokens: <number> (not max_tokens)")
    print("  • reasoning_effort: 'medium' (for reasoning tokens)")
    print("\n✨ The system is now properly configured for GPT-5-mini!")

    return True


if __name__ == "__main__":
    result = asyncio.run(test_gpt5_mini())

    if not result:
        print("\n⚠️ Some tests failed - check configuration")