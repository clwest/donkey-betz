#!/usr/bin/env python
"""Investigate GPT-5 response structure in detail"""

import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import openai
from django.conf import settings

print("\n🔍 Investigating GPT-5 Response Structure...")

client = openai.OpenAI(api_key=settings.AI_PROVIDERS['OPENAI_API_KEY'])

print(f"\n🧪 Testing gpt-5-mini response structure:")
try:
    response = client.chat.completions.create(
        model='gpt-5-mini',
        messages=[{"role": "user", "content": "Say hello."}],
        max_completion_tokens=100
    )

    print("Full response object:")
    print(f"  Type: {type(response)}")
    print(f"  Dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")

    print("\nChoices structure:")
    choice = response.choices[0]
    print(f"  Choice type: {type(choice)}")
    print(f"  Choice dir: {[attr for attr in dir(choice) if not attr.startswith('_')]}")

    print("\nMessage structure:")
    message = choice.message
    print(f"  Message type: {type(message)}")
    print(f"  Message dir: {[attr for attr in dir(message) if not attr.startswith('_')]}")
    print(f"  Content: '{message.content}'")
    print(f"  Role: '{message.role}'")

    # Check if there are other fields
    if hasattr(message, 'tool_calls'):
        print(f"  Tool calls: {message.tool_calls}")
    if hasattr(message, 'function_call'):
        print(f"  Function call: {message.function_call}")

    print("\nUsage details:")
    usage = response.usage
    print(f"  Reasoning tokens: {usage.completion_tokens_details.reasoning_tokens}")
    print(f"  Accepted prediction tokens: {usage.completion_tokens_details.accepted_prediction_tokens}")
    print(f"  Rejected prediction tokens: {usage.completion_tokens_details.rejected_prediction_tokens}")

    # Try to convert to dict to see all fields
    print("\nResponse as dict:")
    response_dict = response.model_dump()
    print(json.dumps(response_dict, indent=2))

except Exception as e:
    print(f"❌ Failed: {e}")

print("\nDone!")