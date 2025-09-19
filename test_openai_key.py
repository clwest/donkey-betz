#!/usr/bin/env python3
"""Test if OpenAI API key is working"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup Django
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.conf import settings

print("=" * 60)
print("TESTING OPENAI API KEY")
print("=" * 60)

# Check if key is in settings
api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY', '')
if api_key:
    print(f"✅ Key found in settings: {api_key[:20]}...")
else:
    print("❌ No key in settings!")
    sys.exit(1)

# Test the actual API
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    # Simple test call
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": "Say 'API key works!'"}],
        max_completion_tokens=10
    )

    print(f"✅ API Response: {response.choices[0].message.content}")
    print("✅ OpenAI API key is working!")

except Exception as e:
    print(f"❌ API Error: {e}")
    if "401" in str(e) or "invalid" in str(e).lower():
        print("\n⚠️  The API key appears to be invalid or expired.")
        print("Please check that your key is correct and has active credits.")

print("=" * 60)