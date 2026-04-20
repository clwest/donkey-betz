#!/usr/bin/env python3
"""
Fix Stuck Video - Session 135

Manually poll Runway ML for a stuck video and update its status.
"""

import os
import sys
import django
import requests
from pathlib import Path

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import VideoHistory, ImageHistory
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

VIDEO_ID = 'b8bd9d2f-d310-49c4-9377-7e27774baf02'

def fix_stuck_video():
    """Fix the stuck video by manually polling Runway ML."""
    print("=" * 80)
    print("🔧 Fixing Stuck Video - Session 135")
    print("=" * 80)
    print()

    # Get the video
    try:
        video = VideoHistory.objects.get(id=VIDEO_ID)
    except VideoHistory.DoesNotExist:
        print(f"❌ Video {VIDEO_ID} not found")
        return

    print(f"📹 Video #{video.get_sequential_number()}")
    print(f"   ID: {video.id}")
    print(f"   Status: {video.status}")
    print(f"   Runway Task ID: {video.video_id}")
    print(f"   Created: {video.created_at}")
    print()

    # Get Runway ML API key
    api_key = settings.EXTERNAL_API_KEYS.get('RUNWAY_API_KEY')
    if not api_key:
        print("❌ RUNWAY_API_KEY not found in settings")
        return

    # Poll Runway ML for status
    print(f"🔍 Polling Runway ML for task {video.video_id}...")
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'X-Runway-Version': '2024-11-06'  # Required by Runway ML API
    }

    try:
        response = requests.get(
            f'https://api.dev.runwayml.com/v1/tasks/{video.video_id}',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        task_data = response.json()

        print(f"   Runway Status: {task_data.get('status')}")
        print(f"   Progress: {task_data.get('progress', 0) * 100:.1f}%")
        print()

        # Check if completed
        if task_data.get('status') == 'SUCCEEDED':
            print("✅ Video generation completed on Runway ML!")
            print()

            # Get video URL
            artifacts = task_data.get('output', [])
            if not artifacts:
                print("❌ No artifacts found in task output")
                return

            video_url = artifacts[0]
            print(f"📥 Downloading video from: {video_url[:80]}...")

            # Download video
            video_response = requests.get(video_url, timeout=60)
            video_response.raise_for_status()

            # Save video file
            filename = f"video-{video.id}.mp4"
            file_path = f"generated/videos/{filename}"

            content_file = ContentFile(video_response.content)
            saved_path = default_storage.save(file_path, content_file)

            print(f"💾 Saved to: {saved_path}")
            print()

            # Update video record
            video.status = 'completed'
            video.video_url = saved_path
            video.save()

            print("✅ Video record updated!")
            print()
            print(f"   Status: {video.status}")
            print(f"   Video URL: {video.video_url}")
            print()

            print("🎉 Video should now appear in the gallery!")

        elif task_data.get('status') == 'FAILED':
            print("❌ Video generation failed on Runway ML")
            error_msg = task_data.get('failure', {}).get('message', 'Unknown error')
            print(f"   Error: {error_msg}")

            # Update video to failed status
            video.status = 'failed'
            video.save()

        elif task_data.get('status') in ['PENDING', 'RUNNING']:
            print(f"⏳ Video still processing (progress: {task_data.get('progress', 0) * 100:.1f}%)")
            print("   Wait a bit longer and try again")

        else:
            print(f"❓ Unknown status: {task_data.get('status')}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error polling Runway ML: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")

    print()
    print("=" * 80)

if __name__ == "__main__":
    fix_stuck_video()
