#!/usr/bin/env python
"""Test GPT-5 models with correct parameters"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import openai
from django.conf import settings

print("\n🔧 Testing GPT-5 models with CORRECT parameters...")

client = openai.OpenAI(api_key=settings.AI_PROVIDERS['OPENAI_API_KEY'])

# Test GPT-5 models with correct parameters
test_models = ['gpt-5-mini', 'gpt-5', 'gpt-5-nano']

for model in test_models:
    print(f"\n🧪 Testing {model}:")
    try:
        # Use max_completion_tokens for GPT-5 models
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "List 3 ways to start freelance writing."}],
            max_completion_tokens=200  # Correct parameter for GPT-5
        )
        content = response.choices[0].message.content
        print(f"  ✅ Success!")
        print(f"  📝 Content: {content}")
        print(f"  📊 Usage: {response.usage}")

    except Exception as e:
        print(f"  ❌ Failed: {e}")

print("\nDone!")