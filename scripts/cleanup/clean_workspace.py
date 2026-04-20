"""
Clean workspace - Delete everything NOT in "AI Content Generation Company" project
This will give us a clean slate to work with!
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import CreativeProject, ImageHistory, VideoHistory, AISession

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🧹 WORKSPACE CLEANUP - NUCLEAR OPTION")
print("=" * 80)

# Find the project we want to KEEP
project = CreativeProject.objects.filter(
    user=user,
    name__icontains='Ai Content Generation Company'
).first()

if not project:
    print("❌ Project 'AI Content Generation Company' not found!")
    sys.exit(1)

print(f"\n✅ Found project to KEEP: {project.name}")
print(f"   ID: {project.id}")

# Count what we have
all_images = ImageHistory.objects.filter(user=user)
all_videos = VideoHistory.objects.filter(user=user)
all_sessions = AISession.objects.filter(user=user)

project_images = ImageHistory.objects.filter(project=project)
project_videos = VideoHistory.objects.filter(project=project)
project_sessions = AISession.objects.filter(project=project)

print(f"\n📊 Current Counts:")
print(f"   Total Images: {all_images.count()}")
print(f"   Images in project: {project_images.count()}")
print(f"   Images to DELETE: {all_images.count() - project_images.count()}")
print(f"")
print(f"   Total Videos: {all_videos.count()}")
print(f"   Videos in project: {project_videos.count()}")
print(f"   Videos to DELETE: {all_videos.count() - project_videos.count()}")
print(f"")
print(f"   Total Sessions: {all_sessions.count()}")
print(f"   Sessions in project: {project_sessions.count()}")
print(f"   Sessions to DELETE: {all_sessions.count() - project_sessions.count()}")

# Ask for confirmation
print(f"\n⚠️  WARNING: This will DELETE everything NOT in '{project.name}'!")
print(f"   This action CANNOT be undone!")
response = input(f"\n   Type 'DELETE' to confirm: ")

if response != 'DELETE':
    print("\n❌ Cleanup cancelled.")
    sys.exit(0)

print(f"\n🗑️  Starting cleanup...")

# Delete images NOT in project
images_to_delete = ImageHistory.objects.filter(user=user).exclude(project=project)
image_count = images_to_delete.count()
if image_count > 0:
    images_to_delete.delete()
    print(f"   ✅ Deleted {image_count} images")
else:
    print(f"   No images to delete")

# Delete videos NOT in project
videos_to_delete = VideoHistory.objects.filter(user=user).exclude(project=project)
video_count = videos_to_delete.count()
if video_count > 0:
    videos_to_delete.delete()
    print(f"   ✅ Deleted {video_count} videos")
else:
    print(f"   No videos to delete")

# Delete sessions NOT in project
sessions_to_delete = AISession.objects.filter(user=user).exclude(project=project)
session_count = sessions_to_delete.count()
if session_count > 0:
    sessions_to_delete.delete()
    print(f"   ✅ Deleted {session_count} sessions")
else:
    print(f"   No sessions to delete")

# Final counts
print(f"\n" + "=" * 80)
print(f"✅ CLEANUP COMPLETE!")
print(f"=" * 80)

final_images = ImageHistory.objects.filter(user=user)
final_videos = VideoHistory.objects.filter(user=user)
final_sessions = AISession.objects.filter(user=user)

print(f"\n📊 Final Counts:")
print(f"   Images: {final_images.count()} (all in '{project.name}')")
print(f"   Videos: {final_videos.count()} (all in '{project.name}')")
print(f"   Sessions: {final_sessions.count()} (all in '{project.name}')")

print(f"\n🎉 Workspace is now CLEAN!")
print(f"   Everything you see belongs to '{project.name}'")
print(f"   Ready to debug and fix issues!")

print("\n" + "=" * 80)
