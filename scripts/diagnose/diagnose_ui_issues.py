#!/usr/bin/env python3
"""
Diagnose UI display issues - Session 131
1. Images not showing up (data URIs vs file paths)
2. Video #4 pending status
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory, VideoHistory

User = get_user_model()
admin = User.objects.get(username='admin')

print("=" * 80)
print("ISSUE #1: IMAGE DISPLAY PROBLEM")
print("=" * 80)

images = ImageHistory.objects.filter(user=admin).order_by('-created_at')[:10]
print(f"\n📊 Total admin images: {ImageHistory.objects.filter(user=admin).count()}")
print(f"\n📸 Last 10 images (checking for data URIs):")

data_uri_count = 0
file_path_count = 0

for img in images:
    is_data_uri = img.file_path.startswith('data:')
    if is_data_uri:
        data_uri_count += 1
        print(f"\n❌ #{img.get_sequential_number()}: DATA URI (won't show in gallery!)")
    else:
        file_path_count += 1
        print(f"\n✅ #{img.get_sequential_number()}: FILE PATH (should show)")

    print(f"   UUID: {img.id}")
    print(f"   Prompt: {img.prompt[:60] if img.prompt else 'No prompt'}...")
    if is_data_uri:
        print(f"   File path: data:image/png;base64,... (TRUNCATED - {len(img.file_path)} chars)")
    else:
        print(f"   File path: {img.file_path}")
    print(f"   Created: {img.created_at.strftime('%H:%M:%S')}")

print(f"\n📊 Summary:")
print(f"   ✅ Images with file paths: {file_path_count}")
print(f"   ❌ Images with data URIs: {data_uri_count}")

if data_uri_count > 0:
    print(f"\n⚠️  PROBLEM: {data_uri_count} image(s) have data URIs instead of file paths!")
    print(f"   These won't display in the gallery UI properly.")

print("\n" + "=" * 80)
print("ISSUE #2: VIDEO #4 PENDING STATUS")
print("=" * 80)

videos = VideoHistory.objects.filter(user=admin).order_by('created_at')
print(f"\n📊 Total admin videos: {videos.count()}")

if videos.count() >= 4:
    video4 = list(videos)[3]
    print(f"\n🎬 Video #4 Details:")
    print(f"   UUID: {video4.id}")
    print(f"   Prompt: {video4.prompt}")
    print(f"   Status: {video4.status}")
    print(f"   Video URL: {video4.video_url if video4.video_url else '(empty)'}")
    print(f"   Thumbnail URL: {video4.thumbnail_url if video4.thumbnail_url else '(empty)'}")
    print(f"   Created: {video4.created_at}")
    print(f"   Updated: {video4.updated_at}")

    if hasattr(video4, 'runway_task_id'):
        print(f"   Runway Task ID: {video4.runway_task_id}")

    if video4.status == 'pending':
        print(f"\n❌ PROBLEM: Video is stuck in 'pending' status!")
        print(f"   This means the video generation was initiated but never completed.")
        print(f"   The frontend can't play a video that doesn't have a URL yet.")
        print(f"\n   Need to either:")
        print(f"   1. Poll Runway ML to get the completed video URL")
        print(f"   2. Or mark as failed if it's been too long")
    elif video4.status == 'completed' and not video4.video_url:
        print(f"\n❌ PROBLEM: Video status is 'completed' but no URL!")
    elif video4.status == 'completed' and video4.video_url:
        print(f"\n✅ Video should be playable (status=completed, has URL)")
    elif video4.status == 'failed':
        print(f"\n⚠️  Video generation failed")
else:
    print(f"\n❌ Only {videos.count()} videos found, Video #4 does not exist")

# Check all pending videos
pending_videos = VideoHistory.objects.filter(user=admin, status='pending').order_by('created_at')
if pending_videos.exists():
    print(f"\n⚠️  FOUND {pending_videos.count()} PENDING VIDEO(S):")
    for vid in pending_videos:
        seq_num = list(VideoHistory.objects.filter(user=admin).order_by('created_at')).index(vid) + 1
        print(f"   Video #{seq_num}: {vid.prompt[:60]}... (created {vid.created_at.strftime('%H:%M:%S')})")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

if data_uri_count > 0:
    print(f"\n1. IMAGE DATA URI FIX:")
    print(f"   - Find where images are being saved with data URIs")
    print(f"   - Ensure Stability AI responses save actual file paths")
    print(f"   - Check image_generation.py or views_image.py")

if pending_videos.exists():
    print(f"\n2. PENDING VIDEO FIX:")
    print(f"   - Run video status polling to update pending videos")
    print(f"   - Check if check_video_status.py exists and run it")
    print(f"   - Or manually poll Runway ML for these video statuses")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
