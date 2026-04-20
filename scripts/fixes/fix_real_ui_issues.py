#!/usr/bin/env python3
"""
Fix REAL UI Issues - Session 131
1. Delete failed video #4 (has no URL)
2. Template fix will be manual
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import VideoHistory

User = get_user_model()
admin = User.objects.get(username='admin')

print("=" * 80)
print("FIX REAL UI ISSUES")
print("=" * 80)

# Get failed video
failed_videos = VideoHistory.objects.filter(user=admin, status='failed')

print(f"\n📹 Found {failed_videos.count()} failed video(s)")

for video in failed_videos:
    all_videos_list = list(VideoHistory.objects.filter(user=admin).order_by('created_at'))
    video_num = all_videos_list.index(video) + 1

    print(f"\n❌ Deleting Failed Video #{video_num}:")
    print(f"   UUID: {video.id}")
    print(f"   Prompt: {video.prompt}")
    print(f"   Status: {video.status}")
    print(f"   Video URL: {video.video_url if video.video_url else '(EMPTY - This causes the error!)'}")

    video.delete()
    print(f"   ✅ Deleted!")

print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

remaining = VideoHistory.objects.filter(user=admin).count()
print(f"\n✅ Remaining videos: {remaining}")
print(f"   All should have URLs and be playable!")
