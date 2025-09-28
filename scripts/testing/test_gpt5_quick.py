#!/usr/bin/env python
"""Quick test of GPT-5 with fixed configuration"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.ai_providers import AIProviderManager

print("\n🧪 Testing GPT-5 with Income Builder configuration...")

ai_manager = AIProviderManager()

# Test with the exact configuration used in Income Builder
result = ai_manager.generate_content(
    provider='openai',
    model='gpt-5',
    system_prompt="You are an expert business consultant and income generation specialist.",
    user_prompt="Create a 3-step plan to start freelance writing",
    config={'max_completion_tokens': 1500}
)

if result.success:
    print(f"✅ Success! Generated {len(result.content)} characters")
    print(f"Preview: {result.content[:500]}...")
    print(f"Cost: ${result.cost:.4f}")
else:
    print(f"❌ Failed: {result.error_message}")

print("\nDone!")