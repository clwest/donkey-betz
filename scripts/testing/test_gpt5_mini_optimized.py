#!/usr/bin/env python
"""Optimized test of GPT-5-mini with shorter prompts"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.ai_providers import AIProviderManager

print("\n🧪 Testing GPT-5-mini with Optimized Prompts...")

ai_manager = AIProviderManager()

# Test 1: Simple prompt
print("\n1. Simple prompt test:")
result = ai_manager.generate_content(
    provider='openai',
    model='gpt-5-mini',
    system_prompt="You are a business consultant.",
    user_prompt="List 3 steps to start freelance writing.",
    config={'max_completion_tokens': 200}
)

if result.success:
    print(f"✅ Success! Generated: {len(result.content)} characters")
    print(f"   Cost: ${result.cost:.4f}")
    print(f"   Content: {result.content}")
else:
    print(f"❌ Failed: {result.error_message}")

# Test 2: Slightly more complex
print("\n2. Medium complexity test:")
result = ai_manager.generate_content(
    provider='openai',
    model='gpt-5-mini',
    system_prompt="Business advisor.",
    user_prompt="How to earn $500/month writing? Give 3 specific steps.",
    config={'max_completion_tokens': 300}
)

if result.success:
    print(f"✅ Success! Generated: {len(result.content)} characters")
    print(f"   Cost: ${result.cost:.4f}")
    print(f"   Preview: {result.content[:200]}...")
else:
    print(f"❌ Failed: {result.error_message}")

print("\nDone!")