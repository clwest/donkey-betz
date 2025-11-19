#!/usr/bin/env python3
"""
Check video URLs in database - Session 131
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
print("VIDEO URL CHECK")
print("=" * 80)

videos = VideoHistory.objects.filter(user=admin).order_by('created_at')

print(f"\n📹 Total videos: {videos.count()}\n")

for video in videos:
    all_videos_list = list(VideoHistory.objects.filter(user=admin).order_by('created_at'))
    video_num = all_videos_list.index(video) + 1

    print(f"Video #{video_num}:")
    print(f"   UUID: {video.id}")
    print(f"   Status: {video.status}")
    print(f"   Prompt: {video.prompt[:60] if video.prompt else '(none)'}...")
    print(f"   Video URL: {video.video_url[:80] if video.video_url else '(EMPTY!)'}...")
    print(f"   Thumbnail URL: {video.thumbnail_url[:80] if video.thumbnail_url else '(EMPTY!)'}...")
    print(f"   Created: {video.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    if not video.video_url:
        print(f"   ❌ NO VIDEO URL - This will cause the error!")
    else:
        print(f"   ✅ Has video URL")
    print()

# Summary
has_url = videos.exclude(video_url='').count()
no_url = videos.filter(video_url='').count()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\n✅ Videos WITH URLs: {has_url}")
print(f"❌ Videos WITHOUT URLs: {no_url}")

if no_url > 0:
    print(f"\n⚠️  {no_url} video(s) have no URL - these will show 'Video URL not found' error!")
