#!/usr/bin/env python
"""
Test the Personal Assistant endpoint with real AI
"""
import requests
import json

# Security fix: Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# API configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8001")
TOKEN = os.getenv("TEST_AUTH_TOKEN", "")
if not TOKEN:
    print("WARNING: No TEST_AUTH_TOKEN found. Please set it in .env file.")
    import sys
    sys.exit(1)

# Headers
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Test message
data = {
    "message": "Hello! Can you tell me about the Unified Donkey Betz platform?",
    "conversation_id": "test-123"
}

# Make the request
print("Testing Personal Assistant endpoint...")
print(f"URL: {BASE_URL}/api/v1/assistant/chat/")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/assistant/chat/",
        headers=headers,
        json=data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Personal Assistant is working with real AI!")
        print(f"\nProvider: {result.get('provider', 'unknown')}")
        print(f"Model: {result.get('model', 'unknown')}")
        print(f"\nAssistant Response:\n{result.get('message', 'No message')}")
        
        if result.get('token_usage'):
            print(f"\nToken Usage: {result.get('token_usage')}")
        if result.get('generation_time_ms'):
            print(f"Generation Time: {result.get('generation_time_ms')}ms")
    else:
        print(f"\n❌ Error Response:")
        print(json.dumps(response.json(), indent=2))
        
except Exception as e:
    print(f"\n❌ Request failed: {e}")