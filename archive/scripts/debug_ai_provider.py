#!/usr/bin/env python
"""Debug the AI provider directly"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.ai_providers import AIProviderManager

print("\n🐛 Debugging AI Provider...")

ai_manager = AIProviderManager()

print("\n1. Testing AI Provider with minimal prompt:")
result = ai_manager.generate_content(
    provider='openai',
    model='gpt-5-mini',
    system_prompt="Assistant.",
    user_prompt="Hi",
    config={'max_completion_tokens': 50}
)

print(f"Success: {result.success}")
print(f"Content: '{result.content}'")
print(f"Error: {result.error_message}")
print(f"Content length: {len(result.content) if result.content else 0}")
print(f"Cost: ${result.cost:.4f}")

print("\nDone!")