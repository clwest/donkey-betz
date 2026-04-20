#!/usr/bin/env python3
"""
Download the generated video to local storage
"""
import os
import sys
import django
import requests

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.video_provider import runway_provider

# Task ID from successful generation
task_id = "db317b6b-28f3-46b9-91c2-ebb4975aa62a"

print("🎬 Downloading generated video...")
print(f"   Task ID: {task_id}")

# Get status and video URL
status_result = runway_provider.check_status(task_id)

if status_result.status == 'completed' and status_result.video_url:
    video_url = status_result.video_url
    print(f"\n✅ Video URL found")
    print(f"   URL: {video_url[:100]}...")

    # Download the video
    output_path = "/Users/donkeyking/development/unified-donkey-betz/media/generated_videos/eagle_test_video.mp4"

    print(f"\n📥 Downloading video...")
    response = requests.get(video_url, stream=True, timeout=60)

    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = os.path.getsize(output_path)
        file_size_mb = file_size / (1024 * 1024)

        print(f"\n✅ Video downloaded successfully!")
        print(f"   Path: {output_path}")
        print(f"   Size: {file_size_mb:.2f} MB")
        print(f"\n💡 You can now open the video:")
        print(f"   open {output_path}")
    else:
        print(f"\n❌ Download failed: HTTP {response.status_code}")
        print(f"   Response: {response.text[:200]}")
else:
    print(f"\n❌ Video not ready or URL not available")
    print(f"   Status: {status_result.status}")
    print(f"   Error: {status_result.error_message}")
