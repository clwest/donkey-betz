#!/usr/bin/env python
"""Debug with exact same parameters that worked directly"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from content.ai_providers import AIProviderManager

print("\n🔬 Testing with exact parameters that worked directly...")

ai_manager = AIProviderManager()

# Test the exact same prompt that worked in direct test
print("\n1. Testing: 'Say hello.'")
result = ai_manager.generate_content(
    provider='openai',
    model='gpt-5-mini',
    system_prompt="",  # Empty system prompt
    user_prompt="Say hello.",
    config={'max_completion_tokens': 100}
)

print(f"Success: {result.success}")
print(f"Content: '{result.content}'")
print(f"Content length: {len(result.content) if result.content else 0}")

# Test even simpler
print("\n2. Testing: 'Hi'")
result = ai_manager.generate_content(
    provider='openai',
    model='gpt-5-mini',
    system_prompt="",
    user_prompt="Hi",
    config={'max_completion_tokens': 50}
)

print(f"Success: {result.success}")
print(f"Content: '{result.content}'")
print(f"Content length: {len(result.content) if result.content else 0}")

print("\nDone!")