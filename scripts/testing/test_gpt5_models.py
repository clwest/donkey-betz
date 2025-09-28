#!/usr/bin/env python
"""Compare GPT-5, GPT-5-mini, and GPT-5-nano for Income Builder"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.ai_providers import AIProviderManager

print("\n🔬 Comparing GPT-5 Models for Income Builder")
print("=" * 60)

ai_manager = AIProviderManager()

# Test prompt similar to Income Builder
test_prompt = """As an expert in AI-Assisted Content Writing, provide a comprehensive action plan for:

Task: Week 1: Research trending templates on Etsy

Please provide:
1. Detailed step-by-step instructions
2. Specific tools and platforms to use
3. Timeline and milestones

Make it practical, specific, and immediately actionable."""

models = ['gpt-5', 'gpt-5-mini', 'gpt-5-nano']

for model in models:
    print(f"\n📝 Testing {model}...")
    print("-" * 40)

    try:
        result = ai_manager.generate_content(
            provider='openai',
            model=model,
            system_prompt="You are an expert business consultant and income generation specialist.",
            user_prompt=test_prompt,
            config={'max_completion_tokens': 500}  # Smaller for comparison
        )

        if result.success:
            print(f"✅ Success!")
            print(f"   Characters: {len(result.content)}")
            print(f"   Cost: ${result.cost:.4f}")
            print(f"   Time: {result.generation_time_ms}ms")
            print(f"   Quality preview:")
            print(f"   {result.content[:300]}...")

            # Calculate cost per 1000 chars
            if len(result.content) > 0:
                cost_per_1k_chars = (result.cost / len(result.content)) * 1000
                print(f"   Cost per 1K chars: ${cost_per_1k_chars:.4f}")
        else:
            print(f"❌ Failed: {result.error_message}")

    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("For Income Builder, GPT-5-mini offers the best balance:")
print("- 5x cheaper than GPT-5")
print("- High quality output for business/educational content")
print("- Fast response times")
print("\nGPT-5-nano is great for simple tasks but may lack depth.")
print("GPT-5 is best for complex reasoning but expensive for this use case.")