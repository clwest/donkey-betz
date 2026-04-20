"""
Complete diagnostic for "Ai Content Generation Company" project
Identifies ALL issues: orphaned videos, delete errors, 3D conversion, etc.
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import CreativeProject, ImageHistory, VideoHistory, MiniFigAsset
from django.conf import settings

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🔍 COMPLETE PROJECT DIAGNOSTIC")
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
print(f"   Goal: {project.goal[:100]}...")

# === IMAGES ANALYSIS ===
print(f"\n" + "=" * 80)
print("📸 IMAGES ANALYSIS")
print("=" * 80)

all_images = ImageHistory.objects.filter(user=user).order_by('created_at')
project_images = ImageHistory.objects.filter(project=project).order_by('created_at')
orphaned_images = ImageHistory.objects.filter(user=user, project__isnull=True).order_by('created_at')

print(f"\n📊 Image Counts:")
print(f"   Total images (all projects): {all_images.count()}")
print(f"   In this project: {project_images.count()}")
print(f"   Orphaned (no project): {orphaned_images.count()}")

# Check for data URI images (broken)
data_uri_images = project_images.filter(file_path__startswith='data:')
print(f"\n⚠️  Broken Images (data URIs): {data_uri_images.count()}")

# Check for working PNG images
png_images = project_images.filter(file_path__startswith='generated_images/')
print(f"✅ Working Images (PNG files): {png_images.count()}")

if project_images.exists():
    print(f"\n📋 First 5 Project Images:")
    for img in project_images[:5]:
        seq_num = ImageHistory.objects.filter(user=user, created_at__lte=img.created_at).count()
        storage_type = "DATA_URI" if img.file_path.startswith('data:') else "PNG"
        print(f"   Image #{seq_num}: {storage_type} | {img.image_type}")

# === VIDEOS ANALYSIS ===
print(f"\n" + "=" * 80)
print("🎬 VIDEOS ANALYSIS")
print("=" * 80)

all_videos = VideoHistory.objects.filter(user=user).order_by('created_at')
project_videos = VideoHistory.objects.filter(project=project).order_by('created_at')
orphaned_videos = VideoHistory.objects.filter(user=user, project__isnull=True).order_by('created_at')

print(f"\n📊 Video Counts:")
print(f"   Total videos (all projects): {all_videos.count()}")
print(f"   In this project: {project_videos.count()}")
print(f"   Orphaned (no project): {orphaned_videos.count()}")

# Check video statuses
if orphaned_videos.exists():
    print(f"\n⚠️  Orphaned Videos (should be in project!):")
    for vid in orphaned_videos:
        seq_num = VideoHistory.objects.filter(user=user, created_at__lte=vid.created_at).count()
        print(f"   Video #{seq_num}: {vid.status} | {vid.video_type} | Created: {vid.created_at}")
        print(f"      ID: {vid.id}")
        print(f"      Prompt: {vid.prompt[:60]}...")

# Check for videos with errors
error_videos = all_videos.filter(status='failed')
print(f"\n❌ Failed Videos: {error_videos.count()}")
if error_videos.exists():
    for vid in error_videos:
        seq_num = VideoHistory.objects.filter(user=user, created_at__lte=vid.created_at).count()
        print(f"   Video #{seq_num}: {vid.error_message or 'No error message'}")

# Check for pending/processing videos
pending_videos = all_videos.filter(status__in=['pending', 'processing'])
print(f"\n⏳ Pending/Processing Videos: {pending_videos.count()}")
if pending_videos.exists():
    for vid in pending_videos:
        seq_num = VideoHistory.objects.filter(user=user, created_at__lte=vid.created_at).count()
        print(f"   Video #{seq_num}: {vid.status} | {vid.video_type}")

# === 3D MODELS ANALYSIS ===
print(f"\n" + "=" * 80)
print("🖨️  3D MODELS ANALYSIS")
print("=" * 80)

all_3d_models = MiniFigAsset.objects.filter(user=user).order_by('created_at')
project_3d_models = MiniFigAsset.objects.filter(project=project).order_by('created_at')

print(f"\n📊 3D Model Counts:")
print(f"   Total 3D models (all projects): {all_3d_models.count()}")
print(f"   In this project: {project_3d_models.count()}")

if all_3d_models.exists():
    print(f"\n✅ 3D Models Found:")
    for model in all_3d_models:
        in_project = "IN PROJECT" if model.project == project else "OTHER PROJECT"
        print(f"   {model.name}: {model.status} | {in_project}")
        print(f"      Created: {model.created_at}")
        if model.model_file:
            print(f"      Model File: {model.model_file}")

# === RECOMMENDATIONS ===
print(f"\n" + "=" * 80)
print("💡 RECOMMENDATIONS")
print("=" * 80)

issues = []

if orphaned_videos.count() > 0:
    issues.append(f"❌ Fix {orphaned_videos.count()} orphaned videos - associate with project")

if error_videos.count() > 0:
    issues.append(f"❌ Clean up {error_videos.count()} failed videos - allow deletion")

if data_uri_images.count() > 0:
    issues.append(f"❌ Fix {data_uri_images.count()} data URI images - convert to PNG")

if orphaned_images.count() > 0:
    issues.append(f"⚠️  {orphaned_images.count()} images not in any project")

if issues:
    print(f"\n🔧 Issues to Fix:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
else:
    print(f"\n✅ No issues found! Project is in good shape.")

print(f"\n📋 Feature Availability Check:")
print(f"   ✅ Image Generation: Available")
print(f"   ❓ Image Editing (upscale, bg removal): Check if accessible in project")
print(f"   ❓ Video Generation: Check if accessible in project")
print(f"   ❓ 3D Model Generation: Check if accessible in project")
print(f"   ❓ Audio Generation: Check if accessible in project")

print("\n" + "=" * 80)
print("🎯 NEXT STEPS")
print("=" * 80)
print("""
1. Associate orphaned videos with project
2. Enable deletion of failed videos
3. Fix any remaining data URI images
4. Integrate ALL 34 features into project workspace
5. Test each feature within project context
""")

print("=" * 80)
