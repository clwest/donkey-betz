#!/usr/bin/env python3
"""
Complete test of Runway ML video generation pipeline
Generates a real video and polls until complete
"""

import os
import sys
import time
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.video_provider import runway_provider

print("="*70)
print("🎬 RUNWAY ML VIDEO GENERATION TEST")
print("="*70)

# Test 1: Text-to-Video
print("\n📹 Test 1: Text-to-Video Generation")
print("-"*70)

prompt = "A majestic eagle soaring over snow-capped mountains, cinematic drone shot, golden hour lighting"
print(f"Prompt: {prompt}")
print(f"Model: veo3.1_fast")
print(f"Duration: 4 seconds")
print(f"Ratio: 1920:1080 (landscape)")

print("\n🚀 Submitting generation request...")
result = runway_provider.text_to_video(
    prompt=prompt,
    duration=4,
    quality="veo3.1_fast",
    style="cinematic",
    enhance_prompt=True,
    enhancement_level="advanced",
    ratio="1920:1080"
)

if not result.success:
    print(f"❌ Generation failed: {result.error_message}")
    sys.exit(1)

print(f"✅ Generation started!")
print(f"   Task ID: {result.task_id}")
print(f"   Status: {result.status}")
print(f"   Estimated time: {result.estimated_time}s (~{result.estimated_time//60} minutes)")

# Poll for completion
print(f"\n⏳ Polling for completion (checking every 10 seconds)...")
task_id = result.task_id
max_attempts = 30  # 5 minutes max
attempt = 0

while attempt < max_attempts:
    time.sleep(10)
    attempt += 1

    status_result = runway_provider.check_status(task_id)

    elapsed = attempt * 10
    print(f"   [{elapsed}s] Status: {status_result.status.upper()} | Progress: {status_result.progress}%")

    if status_result.status == 'completed':
        print(f"\n🎉 VIDEO GENERATION COMPLETE!")
        print(f"   Video URL: {status_result.video_url}")
        if status_result.thumbnail_url:
            print(f"   Thumbnail: {status_result.thumbnail_url}")
        print(f"   Duration: {status_result.duration}s")
        print(f"   Total time: {elapsed}s")
        break

    elif status_result.status == 'failed':
        print(f"\n❌ Generation failed: {status_result.error_message}")
        sys.exit(1)

    elif attempt >= max_attempts:
        print(f"\n⚠️  Timeout after {elapsed}s - video may still be processing")
        print(f"   Check status manually with task ID: {task_id}")
        sys.exit(0)

# Test 2: Check if we can access the video
if status_result.status == 'completed' and status_result.video_url:
    print("\n🔗 Testing video URL accessibility...")
    import requests

    try:
        response = requests.head(status_result.video_url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Video URL is accessible!")
            content_length = response.headers.get('Content-Length', 'unknown')
            if content_length != 'unknown':
                size_mb = int(content_length) / (1024 * 1024)
                print(f"   📊 File size: {size_mb:.2f} MB")
        else:
            print(f"   ⚠️  Video URL returned status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Could not check video URL: {str(e)}")

print("\n" + "="*70)
print("✅ TEST COMPLETE!")
print("="*70)
print(f"\n📋 Summary:")
print(f"   Task ID: {task_id}")
print(f"   Final Status: {status_result.status}")
if status_result.status == 'completed':
    print(f"   Video URL: {status_result.video_url}")
    print(f"\n💡 You can now:")
    print(f"   1. Download the video from the URL above")
    print(f"   2. Test the frontend Video tab")
    print(f"   3. View the video in your browser")
else:
    print(f"   Note: Video is still processing or failed")

print()
