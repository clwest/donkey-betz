#!/usr/bin/env python
"""
Debug GPT-5 content generation issue
"""

import os
import sys
import django
import openai

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_gpt5_directly():
    """Test GPT-5 directly with OpenAI client"""

    print("\n🔬 Testing GPT-5 Directly...")
    print("=" * 50)

    api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found!")
        return

    client = openai.OpenAI(api_key=api_key)

    # Test 1: Simple completion with max_completion_tokens
    print("\n📝 Test 1: Using max_completion_tokens...")
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a 3-step plan to learn Python programming."}
            ],
            max_completion_tokens=200
        )

        content = response.choices[0].message.content
        print(f"✅ Response received:")
        print(f"   Content: {content[:200] if content else 'None'}")
        print(f"   Length: {len(content) if content else 0} characters")
        print(f"   Full response: {response}")
    except Exception as e:
        print(f"❌ Error with max_completion_tokens: {e}")

    # Test 2: Without any token limit
    print("\n📝 Test 2: Without token limit...")
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a 3-step plan to learn Python programming."}
            ]
        )

        content = response.choices[0].message.content
        print(f"✅ Response received:")
        print(f"   Content: {content[:200] if content else 'None'}")
        print(f"   Length: {len(content) if content else 0} characters")
    except Exception as e:
        print(f"❌ Error without token limit: {e}")

    # Test 3: Try with temperature=0
    print("\n📝 Test 3: With temperature=0...")
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a 3-step plan to learn Python programming."}
            ],
            max_completion_tokens=200,
            temperature=0
        )

        content = response.choices[0].message.content
        print(f"✅ Response received:")
        print(f"   Content: {content[:200] if content else 'None'}")
        print(f"   Length: {len(content) if content else 0} characters")
    except Exception as e:
        print(f"❌ Error with temperature=0: {e}")

    # Test 4: Try the fallback to GPT-4
    print("\n📝 Test 4: Testing GPT-4o as comparison...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a 3-step plan to learn Python programming."}
            ],
            max_tokens=200
        )

        content = response.choices[0].message.content
        print(f"✅ GPT-4o Response received:")
        print(f"   Content: {content[:200] if content else 'None'}")
        print(f"   Length: {len(content) if content else 0} characters")
    except Exception as e:
        print(f"❌ Error with GPT-4o: {e}")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_gpt5_directly()