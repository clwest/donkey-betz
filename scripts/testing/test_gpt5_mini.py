#!/usr/bin/env python
"""Quick test of GPT-5-mini for Income Builder"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.ai_providers import AIProviderManager

print("\n🧪 Testing GPT-5-mini for Income Builder...")

ai_manager = AIProviderManager()

# Test with Income Builder configuration
result = ai_manager.generate_content(
    provider='openai',
    model='gpt-5-mini',
    system_prompt="You are an expert business consultant and income generation specialist.",
    user_prompt="Create a 3-step plan to start freelance writing. Be specific and actionable.",
    config={'max_completion_tokens': 1500}
)

if result.success:
    print(f"✅ Success with GPT-5-mini!")
    print(f"   Generated: {len(result.content)} characters")
    print(f"   Cost: ${result.cost:.4f} (vs ~$20 for GPT-5)")
    print(f"   Preview: {result.content[:500]}...")
else:
    print(f"❌ Failed: {result.error_message}")

print("\nDone!")