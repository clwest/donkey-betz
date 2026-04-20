#!/usr/bin/env python3
"""
Fix Video URL - Session 135 Follow-up

Fix Video #4's URL to use the correct /media/ prefix.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import VideoHistory

VIDEO_ID = 'b8bd9d2f-d310-49c4-9377-7e27774baf02'

def fix_video_url():
    """Fix the video URL to use correct /media/ prefix."""
    print("=" * 80)
    print("🔧 Fixing Video URL - Session 135")
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
    print(f"   Current URL: {video.video_url}")
    print()

    # Check if URL needs fixing
    if video.video_url.startswith('/media/'):
        print("✅ URL already has correct /media/ prefix")
        print()
        print("=" * 80)
        return

    # Fix the URL
    old_url = video.video_url

    # If it starts with 'generated/', prepend '/media/'
    if old_url.startswith('generated/'):
        new_url = f'/media/{old_url}'
    else:
        # Otherwise, just ensure it has /media/ prefix
        new_url = f'/media/{old_url}' if not old_url.startswith('/') else f'/media{old_url}'

    print(f"🔧 Updating video URL...")
    print(f"   Old: {old_url}")
    print(f"   New: {new_url}")
    print()

    # Update the video
    video.video_url = new_url
    video.save()

    print("✅ Video URL updated!")
    print()
    print(f"   Video should now be accessible at:")
    print(f"   http://localhost:8000{new_url}")
    print()
    print("=" * 80)

if __name__ == "__main__":
    fix_video_url()
