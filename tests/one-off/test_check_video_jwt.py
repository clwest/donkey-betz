#!/usr/bin/env python3
"""
Check the JWT token in the video URL and inspect the API response
"""

import os
import sys
import django
import base64
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.video_provider import runway_provider

# The task ID from our successful generation
task_id = "db317b6b-28f3-46b9-91c2-ebb4975aa62a"

print("="*70)
print("🔍 CHECKING VIDEO JWT AND API RESPONSE")
print("="*70)

# Get the full status response
import requests

headers = {
    "Authorization": f"Bearer {runway_provider.api_key}",
    "Content-Type": "application/json",
    "X-Runway-Version": "2024-11-06"
}

print(f"\n📡 Fetching task status for: {task_id}")
response = requests.get(
    f"{runway_provider.api_base}/tasks/{task_id}",
    headers=headers,
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Response received (Status: {response.status_code})")
    print(f"\n📦 Full Response JSON:")
    print(json.dumps(data, indent=2))

    # Check if there's an output field
    if 'output' in data:
        output = data['output']
        print(f"\n🎬 Output field type: {type(output)}")
        print(f"   Output value: {output[:200] if isinstance(output, str) else output}...")

        # Try to decode JWT if it's in the URL
        if isinstance(output, str) and '?_jwt=' in output:
            jwt_token = output.split('?_jwt=')[1]
            print(f"\n🔑 JWT Token found in URL")

            # Decode JWT payload (middle part)
            try:
                # JWT format: header.payload.signature
                parts = jwt_token.split('.')
                if len(parts) == 3:
                    payload_encoded = parts[1]
                    # Add padding if needed
                    padding = 4 - len(payload_encoded) % 4
                    if padding != 4:
                        payload_encoded += '=' * padding

                    payload_decoded = base64.b64decode(payload_encoded)
                    payload_json = json.loads(payload_decoded)

                    print(f"\n📋 JWT Payload:")
                    print(json.dumps(payload_json, indent=2))

                    if 'exp' in payload_json:
                        exp_timestamp = payload_json['exp']
                        exp_datetime = datetime.fromtimestamp(exp_timestamp)
                        now = datetime.now()

                        print(f"\n⏰ Token Expiration:")
                        print(f"   Expires at: {exp_datetime}")
                        print(f"   Current time: {now}")
                        print(f"   Time remaining: {exp_datetime - now}")

                        if exp_datetime < now:
                            print(f"   ❌ TOKEN IS EXPIRED!")
                        else:
                            print(f"   ✅ Token is still valid")
            except Exception as e:
                print(f"   ⚠️  Could not decode JWT: {str(e)}")

    # Check for alternative download methods
    print(f"\n🔍 Checking for alternative access methods...")

    # Try direct HEAD request to the video URL
    if 'output' in data and isinstance(data['output'], str):
        print(f"\n📥 Testing direct video URL access...")
        try:
            video_response = requests.head(data['output'], timeout=10)
            print(f"   Status: {video_response.status_code}")
            print(f"   Headers: {dict(video_response.headers)}")

            if video_response.status_code == 200:
                print(f"   ✅ Video is accessible!")
            elif video_response.status_code in [401, 403]:
                print(f"   ❌ Authentication required")
            else:
                print(f"   ⚠️  Unexpected status")

        except Exception as e:
            print(f"   ❌ Error accessing video: {str(e)}")

else:
    print(f"\n❌ Failed to get task status: {response.status_code}")
    print(f"   Response: {response.text}")

print("\n" + "="*70)
print("🔍 INSPECTION COMPLETE")
print("="*70)
