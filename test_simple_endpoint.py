#!/usr/bin/env python
"""
Simple test to isolate the pickle issue
"""
import requests
import json

# Test 1: Simple message
try:
    response = requests.post(
        'http://localhost:8000/api/assistant/dev/chat/',
        json={'message': 'hello'},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")

# Test 2: Check what the assistant returns directly in shell
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

User = get_user_model()
user, created = User.objects.get_or_create(username='test_user', defaults={'email': 'test@example.com'})
print(f"\nDirect test with user: {user}")

try:
    assistant = EnhancedPersonalAIAssistant(user)
    response = assistant.process_message("hello")
    print(f"Response type: {type(response)}")
    print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'not dict'}")

    # Test JSON serialization
    import json
    json.dumps(response)
    print("Direct response is JSON serializable!")

except Exception as e:
    print(f"Direct test failed: {e}")
    import traceback
    traceback.print_exc()