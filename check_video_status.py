"""
Check video status in 'AI Content Generation Company' project
Diagnose why animated videos aren't showing up
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import CreativeProject, VideoHistory

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🎬 VIDEO STATUS DIAGNOSTIC")
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

# Get ALL videos for this user
all_videos = VideoHistory.objects.filter(user=user).order_by('-created_at')
print(f"\n📊 Total Videos: {all_videos.count()}")

if all_videos.count() == 0:
    print("\n⚠️  NO VIDEOS FOUND!")
    print("   Either:")
    print("   1. Videos were never created")
    print("   2. Videos were deleted")
    print("   3. Videos are in a different user account")
    sys.exit(0)

# Group by status
statuses = {}
for video in all_videos:
    status = video.status
    if status not in statuses:
        statuses[status] = []
    statuses[status].append(video)

print(f"\n📈 Videos by Status:")
for status, videos in statuses.items():
    print(f"   {status}: {len(videos)} videos")

# Show details for each status
for status, videos in statuses.items():
    print(f"\n" + "=" * 80)
    print(f"Status: {status.upper()}")
    print("=" * 80)

    for video in videos:
        seq_num = VideoHistory.objects.filter(user=user, created_at__lte=video.created_at).count()
        print(f"\nVideo #{seq_num}:")
        print(f"   ID: {video.id}")
        print(f"   Type: {video.video_type}")
        print(f"   Status: {video.status}")
        print(f"   Created: {video.created_at}")
        print(f"   In Project: {'YES' if video.project == project else 'NO'}")

        if video.prompt:
            print(f"   Prompt: {video.prompt[:80]}...")

        if video.video_url:
            print(f"   URL: {video.video_url}")
        else:
            print(f"   URL: None")

        if video.error_message:
            print(f"   ❌ Error: {video.error_message}")

        if video.task_id:
            print(f"   Task ID: {video.task_id}")

# Check for videos NOT in project
orphaned = all_videos.filter(project__isnull=True)
if orphaned.exists():
    print(f"\n" + "=" * 80)
    print(f"⚠️  ORPHANED VIDEOS (not in any project): {orphaned.count()}")
    print("=" * 80)
    for video in orphaned:
        seq_num = VideoHistory.objects.filter(user=user, created_at__lte=video.created_at).count()
        print(f"\nVideo #{seq_num}:")
        print(f"   ID: {video.id}")
        print(f"   Type: {video.video_type}")
        print(f"   Status: {video.status}")
        print(f"   Created: {video.created_at}")

print("\n" + "=" * 80)
print("💡 RECOMMENDATIONS")
print("=" * 80)

if statuses.get('pending', []) or statuses.get('processing', []):
    print("\n⏳ You have pending/processing videos!")
    print("   These might be stuck. Check:")
    print("   1. Runway ML API status")
    print("   2. Task polling is working")
    print("   3. Credits remaining")

if statuses.get('failed', []):
    print("\n❌ You have failed videos!")
    print("   Check error messages above for details")

if orphaned.exists():
    print(f"\n⚠️  {orphaned.count()} videos not in any project!")
    print("   These won't show up in project view")
    print("   Run fix script to associate them with project")

print("\n" + "=" * 80)
