#!/usr/bin/env python
"""Emergency script to rescue son's videos from last night"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from content.models import VideoHistory

# The 6 videos from last night
video_ids = [
    'b538a1ca-6a2d-4500-a571-17a27fa27a9c',  # Cat dancing
    '3abd5188-f2e2-4e3e-aac4-8e27558e35bb',  # Robot snowboarding lava
    '0d9bd780-e07f-4697-9541-62fd6a07b5c2',  # Elephant dancing
    'edc2ca8a-92d2-4753-ae56-76aabe580b29',  # Tree dancing
    '6d3cf1d7-15cf-481f-91a0-184f4b57cee6',  # Robot Nicholas
    '07ce8937-4e96-4b60-838f-086d6be197d1',  # Skydiver
]

print("=" * 70)
print("🚨 EMERGENCY RESCUE: SON'S VIDEOS FROM LAST NIGHT")
print("=" * 70)

rescued = 0
failed = 0

for video_id in video_ids:
    try:
        video = VideoHistory.objects.get(id=video_id)
        print(f"\n📹 {video.prompt[:60]}...")
        print(f"   Trying to download...")

        # Try to download from CDN
        response = requests.get(video.video_url, timeout=120, stream=True)

        if response.status_code == 200:
            # Download successful!
            video_content = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    video_content += chunk

            # Save to local storage
            filename = f"rescued_videos/{video.id}.mp4"
            file_path = default_storage.save(filename, ContentFile(video_content))

            # Update database
            video.video_url = default_storage.url(file_path)
            video.save()

            size_mb = len(video_content) / (1024 * 1024)
            print(f"   ✅ RESCUED! ({size_mb:.1f} MB) -> {file_path}")
            rescued += 1
        else:
            print(f"   ❌ Download failed: HTTP {response.status_code}")
            failed += 1

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        failed += 1

print("\n" + "=" * 70)
print(f"✅ Rescued: {rescued} videos")
print(f"❌ Failed: {failed} videos")
print("=" * 70)
