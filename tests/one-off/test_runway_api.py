#!/usr/bin/env python3
"""
Test Runway ML API connectivity and discover current endpoints
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

# Get API key from settings
API_KEY = getattr(settings, 'RUNWAY_API_KEY', '')

if not API_KEY:
    print("❌ No Runway ML API key found in settings!")
    sys.exit(1)

print(f"✅ API Key found: {API_KEY[:20]}...")

# Test different possible endpoints
test_configs = [
    {
        "name": "Text-to-Video veo3.1 (v1/text_to_video)",
        "url": "https://api.dev.runwayml.com/v1/text_to_video",
        "method": "POST",
        "payload": {
            "model": "veo3.1",
            "promptText": "A serene lake at sunset, calm water reflecting golden sky",
            "duration": 4,
            "ratio": "1280:720"
        }
    },
    {
        "name": "Text-to-Video veo3.1_fast (v1/text_to_video)",
        "url": "https://api.dev.runwayml.com/v1/text_to_video",
        "method": "POST",
        "payload": {
            "model": "veo3.1_fast",
            "promptText": "A serene lake at sunset, calm water reflecting golden sky",
            "duration": 4,
            "ratio": "1920:1080"
        }
    },
    {
        "name": "Image-to-Video gen4_turbo with base64 (v1/image_to_video)",
        "url": "https://api.dev.runwayml.com/v1/image_to_video",
        "method": "POST",
        "payload": {
            "model": "gen4_turbo",
            "promptImage": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
            "promptText": "Camera slowly pans across the mountain landscape",
            "duration": 5,
            "ratio": "1280:720"
        }
    }
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-Runway-Version": "2024-11-06"
}

print("\n" + "="*60)
print("TESTING RUNWAY ML API ENDPOINTS")
print("="*60 + "\n")

for config in test_configs:
    print(f"\n🧪 Testing: {config['name']}")
    print(f"   URL: {config['url']}")
    print(f"   Payload: {json.dumps(config['payload'], indent=2)}")

    try:
        response = requests.request(
            method=config['method'],
            url=config['url'],
            headers=headers,
            json=config['payload'],
            timeout=30
        )

        print(f"\n   Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"   ✅ SUCCESS!")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
        elif response.status_code == 401:
            print(f"   ❌ Authentication failed - Invalid API key or headers")
            print(f"   Response: {response.text[:500]}")
        elif response.status_code == 404:
            print(f"   ⚠️  Endpoint not found - May be deprecated or wrong path")
            print(f"   Response: {response.text[:500]}")
        elif response.status_code == 400:
            print(f"   ⚠️  Bad request - Invalid parameters")
            print(f"   Response: {response.text[:500]}")
        else:
            print(f"   ⚠️  Unexpected status code")
            print(f"   Response: {response.text[:500]}")

    except requests.exceptions.Timeout:
        print(f"   ⏱️  Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")

# Test if we can access the API at all
print("\n" + "="*60)
print("BASIC CONNECTIVITY TEST")
print("="*60)

try:
    # Try to access the API base
    response = requests.get(
        "https://api.dev.runwayml.com/",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=10
    )
    print(f"\n✅ Base API accessible (Status: {response.status_code})")
    if response.text:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"\n❌ Base API not accessible: {str(e)}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
