# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test Real-Time Content Creation
================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.api_settings import get_openai_client, OPENAI_CONFIG
import redis
import json
from datetime import datetime

def test_content_creation():
    """
    Test content creation with real API
    """
    print("\n🧪 Testing Real-Time Content Creation")
    print("-" * 40)

    # Test OpenAI connection
    print("1. Testing OpenAI API...")
    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model=OPENAI_CONFIG['model'],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API working' in 3 words."}
            ],
            max_tokens=10
        )

        result = response.choices[0].message.content
        print(f"   ✅ OpenAI Response: {result}")

    except Exception as e:
        print(f"   ❌ OpenAI Error: {e}")
        return False

    # Test Redis
    print("\n2. Testing Redis...")
    try:
        r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
        r.ping()
        print("   ✅ Redis connected")

        # Store test content
        r.set('test:content', json.dumps({
            'status': 'working',
            'timestamp': datetime.now().isoformat()
        }))
        print("   ✅ Redis write successful")

    except Exception as e:
        print(f"   ❌ Redis Error: {e}")
        return False

    print("\n✅ All systems operational!")
    print("   Ready for real-time content creation")

    return True

if __name__ == "__main__":
    success = test_content_creation()