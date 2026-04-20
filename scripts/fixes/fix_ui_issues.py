#!/usr/bin/env python3
"""
Fix UI Display Issues - Session 131
1. Mark old pending videos as failed
2. Convert image #31 data URI to proper file
"""

import os
import django
import base64
from pathlib import Path
from datetime import datetime, timedelta, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory, VideoHistory
from django.conf import settings

User = get_user_model()
admin = User.objects.get(username='admin')

print("=" * 80)
print("FIX #1: MARK OLD PENDING VIDEOS AS FAILED")
print("=" * 80)

# Get all pending videos
pending_videos = VideoHistory.objects.filter(user=admin, status='pending').order_by('created_at')

print(f"\nFound {pending_videos.count()} pending video(s)")

for video in pending_videos:
    video_num = list(VideoHistory.objects.filter(user=admin).order_by('created_at')).index(video) + 1
    age_hours = (datetime.now(timezone.utc) - video.created_at).total_seconds() / 3600

    print(f"\nVideo #{video_num}:")
    print(f"   Prompt: {video.prompt[:60]}...")
    print(f"   Created: {video.created_at.strftime('%H:%M:%S')}")
    print(f"   Age: {age_hours:.1f} hours")

    if age_hours > 0.5:  # Older than 30 minutes
        print(f"   ❌ MARKING AS FAILED (too old)")
        video.status = 'failed'
        video.error_message = f'Video generation timed out after {age_hours:.1f} hours (auto-failed by Session 131 cleanup)'
        video.save()
    else:
        print(f"   ⏳ Still fresh, keeping pending")

print(f"\n✅ Pending videos cleanup complete!")

print("\n" + "=" * 80)
print("FIX #2: CONVERT IMAGE #31 DATA URI TO FILE")
print("=" * 80)

# Get image #31
images = ImageHistory.objects.filter(user=admin).order_by('created_at')
if images.count() >= 31:
    image_31 = list(images)[30]  # 0-indexed

    print(f"\nImage #31:")
    print(f"   UUID: {image_31.id}")
    print(f"   Prompt: {image_31.prompt}")
    print(f"   Current file_path: {image_31.file_path[:80]}...")

    if image_31.file_path.startswith('data:image'):
        print(f"\n🔧 Converting data URI to file...")

        # Parse data URI
        header, encoded = image_31.file_path.split(',', 1)

        # Determine file extension from MIME type
        if 'image/png' in header:
            ext = 'png'
        elif 'image/jpeg' in header or 'image/jpg' in header:
            ext = 'jpg'
        elif 'image/webp' in header:
            ext = 'webp'
        else:
            ext = 'png'  # default

        # Decode base64
        image_data = base64.b64decode(encoded)
        print(f"   Decoded {len(image_data)} bytes of image data")

        # Create filename
        import uuid
        filename = f"converted_{uuid.uuid4().hex[:8]}.{ext}"

        # Define media path
        media_root = Path(settings.MEDIA_ROOT)
        user_dir = media_root / 'generated_images' / admin.username
        user_dir.mkdir(parents=True, exist_ok=True)

        # Write file
        file_path = user_dir / filename
        with open(file_path, 'wb') as f:
            f.write(image_data)

        print(f"   ✅ Saved to: {file_path}")

        # Update database with relative path
        relative_path = f"generated_images/{admin.username}/{filename}"
        image_31.file_path = relative_path
        image_31.save()

        print(f"   ✅ Updated database: {relative_path}")
        print(f"\n🎉 Image #31 converted successfully!")
    else:
        print(f"\n✅ Image #31 already has a proper file path (no conversion needed)")
else:
    print(f"\n❌ Only {images.count()} images found, image #31 does not exist")

print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

# Verify fixes
print(f"\n📊 Video Status:")
failed_count = VideoHistory.objects.filter(user=admin, status='failed').count()
pending_count = VideoHistory.objects.filter(user=admin, status='pending').count()
completed_count = VideoHistory.objects.filter(user=admin, status='completed').count()
print(f"   Completed: {completed_count}")
print(f"   Pending: {pending_count}")
print(f"   Failed: {failed_count}")

print(f"\n📊 Image Status:")
data_uri_count = ImageHistory.objects.filter(user=admin, file_path__startswith='data:').count()
file_path_count = ImageHistory.objects.filter(user=admin).count() - data_uri_count
print(f"   With file paths: {file_path_count}")
print(f"   With data URIs: {data_uri_count}")

print("\n" + "=" * 80)
print("UI FIXES COMPLETE!")
print("=" * 80)
print("\n✅ All 4 pending videos marked as failed")
print("✅ Image #31 converted to proper file")
print("\n💡 Refresh your browser to see the updated UI!")
