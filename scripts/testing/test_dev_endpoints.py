#!/usr/bin/env python
"""
Test the development endpoints
"""

import requests
import json

print("\n" + "=" * 60)
print("Testing Development Endpoints (No Auth)")
print("=" * 60 + "\n")

# Test context endpoint
print("1. Testing /api/assistant/dev/context/")
print("-" * 40)
try:
    response = requests.get("http://localhost:8000/api/assistant/dev/context/")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Context loaded successfully")
        if 'context' in data:
            context = data['context']
            print(f"  - User: {context.get('first_name', 'Unknown')}")
            print(f"  - Skills: {len(context.get('skills', {}).get('top_skills', []))} skills")
    else:
        print(f"❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"❌ Connection error: {e}")

# Test chat endpoint
print("\n2. Testing /api/assistant/dev/chat/")
print("-" * 40)
try:
    response = requests.post(
        "http://localhost:8000/api/assistant/dev/chat/",
        json={
            "message": "Hello, what can you help me with?",
            "context": {}
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Chat response received")
        if 'data' in data:
            response_data = data['data']
            print(f"  - Response: {response_data.get('response', '')[:100]}...")
            print(f"  - AI Generated: {response_data.get('ai_generated', False)}")
            print(f"  - Model: {response_data.get('model', 'Unknown')}")
            if 'debug_info' in response_data:
                debug = response_data['debug_info']
                print(f"  - User: {debug.get('user', 'Unknown')}")
                print(f"  - Authenticated: {debug.get('authenticated', False)}")
    else:
        print(f"❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"❌ Connection error: {e}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)