#!/usr/bin/env python
"""Test Income Builder with fixed GPT-5-mini implementation"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.ai_providers import AIProviderManager

print("\n💰 Testing Income Builder with Fixed GPT-5-mini...")

ai_manager = AIProviderManager()

# Test optimized prompts for Income Builder
tests = [
    {
        "name": "Simple Action Steps",
        "system": "",
        "user": "List 3 steps to start freelance writing.",
        "tokens": 200
    },
    {
        "name": "Business Plan",
        "system": "You are a business consultant.",
        "user": "How can someone earn $500/month from content writing?",
        "tokens": 300
    },
    {
        "name": "Specific Guidance",
        "system": "Business advisor.",
        "user": "What platforms should a new freelance writer use? List top 3.",
        "tokens": 250
    }
]

for i, test in enumerate(tests, 1):
    print(f"\n{i}. Testing: {test['name']}")

    result = ai_manager.generate_content(
        provider='openai',
        model='gpt-5-mini',
        system_prompt=test['system'],
        user_prompt=test['user'],
        config={'max_completion_tokens': test['tokens']}
    )

    if result.success:
        if len(result.content) > 100 and not result.content.startswith("GPT-5-mini Error"):
            print(f"✅ Success! Generated: {len(result.content)} chars")
            print(f"   Cost: ${result.cost:.4f}")
            print(f"   Preview: {result.content[:150]}...")
        else:
            print(f"⚠️  Generated response but may be error message")
            print(f"   Content: {result.content}")
    else:
        print(f"❌ Failed: {result.error_message}")

print("\n💡 Summary:")
print("- GPT-5-mini works but is very sensitive to prompt patterns")
print("- Avoid single words like 'Hi' - use complete sentences")
print("- Keep system prompts short or empty")
print("- Use specific, clear questions")

print("\nDone!")