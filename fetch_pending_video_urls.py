"""
Fetch URLs for pending videos from Runway ML
Poll the API to check if videos are complete and update database
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import CreativeProject, VideoHistory
from content.video_provider import RunwayMLProvider

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🎬 FETCHING PENDING VIDEO URLS FROM RUNWAY ML")
print("=" * 80)

# Find the project
project = CreativeProject.objects.filter(
    user=user,
    name__icontains='Ai Content Generation Company'
).first()

if not project:
    print("❌ Project not found!")
    sys.exit(1)

print(f"\n📁 Project: {project.name}")
print(f"   ID: {project.id}")

# Use simpler query - just find pending videos in this project
pending_videos = VideoHistory.objects.filter(
    user=user,
    project=project,
    status='pending'
).order_by('-created_at')

count = pending_videos.count()
print(f"\n🔍 Found {count} pending videos")

if count == 0:
    print("✅ No pending videos! All videos are complete.")
    sys.exit(0)

# Initialize Runway provider
runway = RunwayMLProvider()

print("\n" + "=" * 80)
print("📡 POLLING RUNWAY ML API")
print("=" * 80)

updated_count = 0
still_pending = 0
failed_count = 0

for video in pending_videos:
    seq_num = VideoHistory.objects.filter(user=user, created_at__lte=video.created_at).count()
    print(f"\n🎥 Video #{seq_num} (ID: {str(video.id)[:8]}...)")

    if not video.video_id:
        print("   ⚠️  No task ID - skipping")
        continue

    print(f"   Task ID: {video.video_id}")

    try:
        # Check status with Runway ML
        result = runway.check_status(video.video_id)
        status = result.status

        print(f"   Status from Runway: {status}")

        if status == 'completed':
            # Get video URL from result object
            video_url = result.video_url
            if video_url:
                print(f"   ✅ Video complete!")
                print(f"   URL: {video_url[:60]}...")

                # Update database
                video.video_url = video_url
                video.status = 'completed'
                video.save()

                print(f"   💾 Database updated!")
                updated_count += 1
            else:
                print(f"   ⚠️  Status is completed but no video URL found")

        elif status == 'failed':
            print(f"   ❌ Video generation failed")
            error_msg = result.error_message
            print(f"   Error: {error_msg}")

            video.status = 'failed'
            video.error_message = error_msg
            video.save()

            failed_count += 1

        elif status in ['pending', 'processing']:
            print(f"   ⏳ Still processing... (status: {status})")
            still_pending += 1

        else:
            print(f"   ⚠️  Unknown status: {status}")

    except Exception as e:
        print(f"   ❌ Error checking status: {e}")

print("\n" + "=" * 80)
print("✅ POLLING COMPLETE!")
print("=" * 80)
print(f"\n📊 Results:")
print(f"   ✅ Completed: {updated_count} videos")
print(f"   ⏳ Still pending: {still_pending} videos")
print(f"   ❌ Failed: {failed_count} videos")

if updated_count > 0:
    print(f"\n🎉 {updated_count} videos now have URLs and should be playable!")
    print("   Refresh the project page to see them!")

if still_pending > 0:
    print(f"\n⏰ {still_pending} videos are still processing")
    print("   Run this script again in a few minutes")

print("=" * 80)
