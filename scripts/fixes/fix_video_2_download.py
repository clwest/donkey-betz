#!/usr/bin/env python3
"""
Fix Video #2 - Download from Runway ML CDN and update database
"""

import os
import django
import requests
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import VideoHistory

# Get Video #2 (the one with CDN URL)
video = VideoHistory.objects.get(id='d605313d-2484-4277-9615-802241a45b66')

print(f"Video #2 Details:")
print(f"  UUID: {video.id}")
print(f"  Status: {video.status}")
print(f"  Prompt: {video.prompt}")
print(f"  Current URL: {video.video_url}")

# Download from CDN
if video.video_url and 'cloudfront.net' in video.video_url:
    print(f"\n📥 Downloading from Runway ML CDN...")

    try:
        response = requests.get(video.video_url, timeout=30)
        response.raise_for_status()

        # Create local directory
        project_id = str(video.project.id) if video.project else 'no_project'
        video_dir = Path(f'media/videos/{project_id}')
        video_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        filename = f"{video.id}.mp4"
        filepath = video_dir / filename

        with open(filepath, 'wb') as f:
            f.write(response.content)

        file_size = filepath.stat().st_size
        print(f"✅ Downloaded: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

        # Update database
        video.video_url = f"/media/videos/{project_id}/{filename}"
        video.file_size_bytes = file_size
        video.save(update_fields=['video_url', 'file_size_bytes'])

        print(f"✅ Database updated!")
        print(f"  New URL: {video.video_url}")
        print(f"\n🎉 Video #2 fixed! URL should now work in the UI.")

    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"\n⚠️ Video already has local URL: {video.video_url}")
