#!/usr/bin/env python
"""Test what GPT models are actually available"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from content.ai_providers import AIProviderManager
import openai
from django.conf import settings

print("\n🔍 Testing Model Availability...")

# Test with direct OpenAI client
try:
    client = openai.OpenAI(api_key=settings.AI_PROVIDERS['OPENAI_API_KEY'])

    # List available models
    print("\n📋 Available models from OpenAI API:")
    models = client.models.list()
    gpt_models = [model.id for model in models.data if 'gpt' in model.id.lower()]
    for model in sorted(gpt_models):
        print(f"  - {model}")

    # Test each model we think exists
    test_models = ['gpt-5-mini', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-mini', 'gpt-5', 'gpt-5-nano']

    print(f"\n🧪 Testing each model with minimal request:")
    for model in test_models:
        print(f"\nTesting {model}:")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_completion_tokens=10
            )
            content = response.choices[0].message.content
            print(f"  ✅ Success: '{content}'")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

except Exception as e:
    print(f"❌ Could not connect to OpenAI: {e}")

print("\nDone!")