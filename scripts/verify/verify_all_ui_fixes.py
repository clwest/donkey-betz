#!/usr/bin/env python3
"""
Final Verification - All UI Fixes Complete - Session 131
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory, VideoHistory, MiniFigAsset, CreativeProject

User = get_user_model()
admin = User.objects.get(username='admin')

print("=" * 80)
print("SESSION 131 - FINAL VERIFICATION")
print("=" * 80)

# Get project
project = CreativeProject.objects.get(user=admin, name="AI Content Generation Company")

print("\n✅ ISSUE #1: IMAGE DATA URIS")
print("-" * 80)
images = ImageHistory.objects.filter(user=admin).order_by('created_at')
data_uri_count = images.filter(file_path__startswith='data:').count()
file_path_count = images.count() - data_uri_count

print(f"Total images: {images.count()}")
print(f"  ✅ With file paths: {file_path_count}")
print(f"  ❌ With data URIs: {data_uri_count}")
if data_uri_count == 0:
    print("  🎉 PASS: All images have proper file paths!")
else:
    print(f"  ⚠️  FAIL: {data_uri_count} image(s) still have data URIs")

print("\n✅ ISSUE #2: PENDING VIDEOS")
print("-" * 80)
videos = VideoHistory.objects.filter(user=admin).order_by('created_at')
pending_count = videos.filter(status='pending').count()
completed_count = videos.filter(status='completed').count()
failed_count = videos.filter(status='failed').count()

print(f"Total videos: {videos.count()}")
print(f"  ✅ Completed: {completed_count}")
print(f"  ⏳ Pending: {pending_count}")
print(f"  ❌ Failed: {failed_count}")
if pending_count == 0 or all(
    (datetime.now(timezone.utc) - v.created_at).total_seconds() / 3600 < 0.5
    for v in videos.filter(status='pending')
):
    print("  🎉 PASS: No old pending videos!")
else:
    from datetime import datetime, timezone
    old_pending = [
        v for v in videos.filter(status='pending')
        if (datetime.now(timezone.utc) - v.created_at).total_seconds() / 3600 > 0.5
    ]
    print(f"  ⚠️  FAIL: {len(old_pending)} old pending video(s)")

print("\n✅ ISSUE #3: ORPHANED IMAGES")
print("-" * 80)
orphaned_images = images.filter(project__isnull=True)
in_project_images = images.filter(project=project)

print(f"Total images: {images.count()}")
print(f"  ✅ In project: {in_project_images.count()}")
print(f"  ❌ Orphaned: {orphaned_images.count()}")
if orphaned_images.count() == 0:
    print("  🎉 PASS: All images in project!")
else:
    print(f"  ⚠️  FAIL: {orphaned_images.count()} orphaned image(s)")

print("\n✅ ISSUE #4: ORPHANED VIDEOS")
print("-" * 80)
orphaned_videos = videos.filter(project__isnull=True)
in_project_videos = videos.filter(project=project)

print(f"Total videos: {videos.count()}")
print(f"  ✅ In project: {in_project_videos.count()}")
print(f"  ❌ Orphaned: {orphaned_videos.count()}")
if orphaned_videos.count() == 0:
    print("  🎉 PASS: All videos in project!")
else:
    print(f"  ⚠️  FAIL: {orphaned_videos.count()} orphaned video(s)")

print("\n✅ ISSUE #5: 3D MODELS WITHOUT LOCAL FILES")
print("-" * 80)
models = MiniFigAsset.objects.filter(user=admin).order_by('created_at')
completed_models = models.filter(status='completed')

models_with_files = 0
models_without_files = 0

for model in completed_models:
    has_glb = bool(model.glb_file) and model.glb_file.name
    has_stl = bool(model.stl_file) and model.stl_file.name
    if has_glb and has_stl:
        models_with_files += 1
    else:
        models_without_files += 1

print(f"Total 3D models: {models.count()}")
print(f"  Completed: {completed_models.count()}")
print(f"    ✅ With local files: {models_with_files}")
print(f"    ❌ Without local files: {models_without_files}")
if models_without_files == 0:
    print("  🎉 PASS: All completed models have local files!")
else:
    print(f"  ⚠️  FAIL: {models_without_files} completed model(s) without local files")

print("\n" + "=" * 80)
print("OVERALL RESULT")
print("=" * 80)

all_pass = (
    data_uri_count == 0 and
    orphaned_images.count() == 0 and
    orphaned_videos.count() == 0 and
    models_without_files == 0
)

if all_pass:
    print("\n🎉🎉🎉 ALL TESTS PASS! 🎉🎉🎉")
    print("\n✅ All UI display issues have been resolved!")
    print("✅ All content is now visible in the UI!")
    print("✅ Platform ready for Session 132!")
else:
    print("\n⚠️  SOME ISSUES REMAIN")
    print("\nPlease review the failures above.")

print("\n" + "=" * 80)
print("CONTENT SUMMARY")
print("=" * 80)
print(f"\n📸 Images: {images.count()} total, {in_project_images.count()} in project")
print(f"🎬 Videos: {videos.count()} total, {in_project_videos.count()} in project")
print(f"🎨 3D Models: {models.count()} total, {models_with_files} completed & visible")
print(f"\n🏢 Project: \"{project.name}\"")
print(f"   Created: {project.created_at.strftime('%Y-%m-%d')}")
print(f"   Images: {in_project_images.count()}")
print(f"   Videos: {in_project_videos.count()}")
print(f"   3D Models: {models.filter(project=project).count()}")
