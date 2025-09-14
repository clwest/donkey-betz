#!/usr/bin/env python3
"""
Quick test to verify intelligence endpoint is accessible
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_intelligence_endpoint():
    client = Client()

    # Test the intelligence skynet status endpoint
    response = client.get('/api/v1/intelligence/skynet/status/')

    print(f"Response Status Code: {response.status_code}")

    if response.status_code == 200:
        import json
        data = response.json()
        print("Response Data:")
        print(json.dumps(data, indent=2))
        return True
    else:
        print(f"Error: Got status code {response.status_code}")
        print(f"Content: {response.content[:500].decode('utf-8')}")

        # Try to list available URLs
        from django.urls import get_resolver
        resolver = get_resolver()

        print("\nAvailable intelligence URLs:")
        for pattern in resolver.url_patterns:
            pattern_str = str(pattern.pattern)
            if 'intelligence' in pattern_str:
                print(f"  - {pattern_str}")

        return False

if __name__ == "__main__":
    success = test_intelligence_endpoint()
    sys.exit(0 if success else 1)