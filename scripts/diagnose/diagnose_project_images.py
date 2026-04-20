"""
Diagnose image storage in "Ai Content Generation Company" project
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import CreativeProject, ImageHistory

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🔍 PROJECT IMAGE STORAGE DIAGNOSTIC")
print("=" * 80)

# Find the project
print("\n📁 Searching for 'Ai Content Generation Company' project...")
projects = CreativeProject.objects.filter(
    user=user,
    name__icontains='Ai Content Generation Company'
)

if not projects.exists():
    print("❌ Project not found! Available projects:")
    for p in CreativeProject.objects.filter(user=user):
        print(f"   - {p.name}")
    sys.exit(1)

project = projects.first()
print(f"✅ Found project: {project.name}")
print(f"   ID: {project.id}")

# Get all images in this project
print(f"\n📸 Analyzing images in project...")
images = ImageHistory.objects.filter(project=project).order_by('created_at')
total = images.count()
print(f"   Total images: {total}")

if total == 0:
    print("   No images in project!")
    sys.exit(0)

# Analyze storage types
data_uri_count = 0
png_file_count = 0
other_count = 0

data_uri_images = []
png_images = []

for img in images:
    if img.file_path.startswith('data:'):
        data_uri_count += 1
        data_uri_images.append(img)
    elif img.file_path.startswith('generated_images/'):
        png_file_count += 1
        png_images.append(img)
    else:
        other_count += 1

print(f"\n📊 Storage Analysis:")
print(f"   Data URIs (BAD): {data_uri_count} images ({data_uri_count/total*100:.1f}%)")
print(f"   PNG files (GOOD): {png_file_count} images ({png_file_count/total*100:.1f}%)")
print(f"   Other: {other_count} images")

if data_uri_count > 0:
    print(f"\n⚠️  {data_uri_count} images have DATA URI storage issue!")
    print(f"   These images are from Session 126 regression")
    print(f"   They will FAIL when used for video animation (payload too large)")

    print(f"\n❌ Problem Images (first 5):")
    for img in data_uri_images[:5]:
        seq_num = ImageHistory.objects.filter(user=user, created_at__lte=img.created_at).count()
        size = len(img.file_path)
        print(f"   Image #{seq_num}: {size:,} characters (should be ~50)")
        print(f"      ID: {img.id}")
        print(f"      Created: {img.created_at}")
        print(f"      Type: {img.image_type}")

if png_file_count > 0:
    print(f"\n✅ Working Images (first 5):")
    for img in png_images[:5]:
        seq_num = ImageHistory.objects.filter(user=user, created_at__lte=img.created_at).count()
        print(f"   Image #{seq_num}: {img.file_path[:60]}")
        print(f"      ID: {img.id}")
        print(f"      Created: {img.created_at}")

print("\n" + "=" * 80)
print("🎯 RECOMMENDATION:")
if data_uri_count > 0:
    print(f"   {data_uri_count} images need to be fixed")
    print(f"   Option 1: Delete old images with data URIs")
    print(f"   Option 2: Convert data URIs to proper PNG files")
    print(f"   Option 3: Use only the {png_file_count} working PNG images for animation")
else:
    print("   ✅ All images are stored correctly!")
print("=" * 80)
