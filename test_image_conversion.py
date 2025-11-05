#!/usr/bin/env python3
"""Test image conversion for Runway ML"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.video_provider import runway_provider

# Test URLs (both full URL and relative path)
test_urls = [
    "http://localhost:8000/media/generated_images/erased_2f6327b8.png",  # Full URL
    "/media/generated_images/erased_2f6327b8.png"  # Relative path (what gallery returns)
]

print(f"🧪 Testing image conversion...")
print()

for i, test_url in enumerate(test_urls, 1):
    print(f"Test {i}: {test_url}")
    try:
        result = runway_provider._prepare_image(test_url)

        if result.startswith('data:image'):
            print(f"✅ SUCCESS! Converted to base64 data URI")
            print(f"   Starts with: {result[:50]}...")
            print(f"   Total length: {len(result)} characters")
        else:
            print(f"❌ FAILED! Result doesn't start with 'data:image'")
            print(f"   Result: {result[:100]}")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print()
