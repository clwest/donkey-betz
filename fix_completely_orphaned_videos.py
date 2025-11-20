"""
Fix completely orphaned videos - no session AND no project
Associate them with the 'AI Content Generation Company' project
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
print("🔧 FIXING COMPLETELY ORPHANED VIDEOS")
print("=" * 80)

# Find the project
project = CreativeProject.objects.filter(
    user=user,
    name__icontains='Ai Content Generation Company'
).first()

if not project:
    print("❌ Project not found!")
    sys.exit(1)

print(f"\n📁 Target Project: {project.name}")
print(f"   ID: {project.id}")

# Get completely orphaned videos (no project, regardless of session)
orphaned_videos = VideoHistory.objects.filter(
    user=user,
    project__isnull=True  # No project association
).order_by('created_at')

count = orphaned_videos.count()
print(f"\n🔍 Found {count} videos with no project association")

if count == 0:
    print("✅ No orphaned videos! All videos are already in a project.")
    sys.exit(0)

# Show what we're about to fix
print(f"\n📋 Videos to associate with '{project.name}':")
for video in orphaned_videos:
    seq_num = VideoHistory.objects.filter(user=user, created_at__lte=video.created_at).count()
    has_session = "✓" if video.session else "✗"
    print(f"   Video #{seq_num} (ID: {str(video.id)[:8]}...)")
    print(f"      Type: {video.video_type}")
    print(f"      Status: {video.status}")
    print(f"      Session: {has_session}")
    if video.prompt:
        print(f"      Prompt: {video.prompt[:60]}...")

# Fix them
print(f"\n🔧 Associating {count} videos with '{project.name}'...")

fixed_count = 0
for video in orphaned_videos:
    seq_num = VideoHistory.objects.filter(user=user, created_at__lte=video.created_at).count()
    print(f"\n   Video #{seq_num}:")
    print(f"      Before: project = None")

    video.project = project
    video.save()

    print(f"      After: project = {project.name}")
    print(f"      ✅ Fixed!")
    fixed_count += 1

print("\n" + "=" * 80)
print("✅ FIX COMPLETE!")
print("=" * 80)
print(f"\n📊 Results:")
print(f"   Fixed: {fixed_count} videos")
print(f"   All videos now associated with '{project.name}'")
print(f"\n🎉 Videos should now appear in the project view!")
print("=" * 80)
