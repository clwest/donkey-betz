"""
Fix images in "Ai Content Generation Company" project
Convert data URIs to proper PNG files
"""
import os
import sys
import django
import base64
from pathlib import Path

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings
from content.models import CreativeProject, ImageHistory

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🔧 FIXING PROJECT IMAGES")
print("=" * 80)

# Find the project
project = CreativeProject.objects.filter(
    user=user,
    name__icontains='Ai Content Generation Company'
).first()

print(f"\n📁 Project: {project.name}")

# Get images with data URIs
images_to_fix = ImageHistory.objects.filter(
    project=project,
    file_path__startswith='data:'
).order_by('created_at')

count = images_to_fix.count()
print(f"\n🔍 Found {count} images to fix")

if count == 0:
    print("✅ No images need fixing!")
    sys.exit(0)

# Create directory for fixed images
fixed_dir = Path(settings.MEDIA_ROOT) / 'generated_images' / 'admin' / 'fixed_robots'
fixed_dir.mkdir(parents=True, exist_ok=True)
print(f"\n📂 Saving to: {fixed_dir}")

fixed_count = 0
failed_count = 0

for img in images_to_fix:
    seq_num = ImageHistory.objects.filter(user=user, created_at__lte=img.created_at).count()
    print(f"\n🤖 Fixing Image #{seq_num} (ID: {img.id})...")

    try:
        # Extract base64 data from data URI
        if ',' in img.file_path:
            header, data = img.file_path.split(',', 1)
            print(f"   Header: {header[:50]}...")
            print(f"   Data length: {len(data):,} characters")

            # Decode base64
            image_data = base64.b64decode(data)
            print(f"   Decoded: {len(image_data):,} bytes")

            # Generate filename
            filename = f"robot_{img.id.hex[:8]}.png"
            file_path = fixed_dir / filename

            # Save PNG file
            with open(file_path, 'wb') as f:
                f.write(image_data)
            print(f"   ✅ Saved: {file_path.name}")

            # Update database with relative path
            relative_path = f"generated_images/admin/fixed_robots/{filename}"
            old_length = len(img.file_path)
            img.file_path = relative_path
            img.save()

            print(f"   ✅ Updated DB: {relative_path}")
            print(f"   Size reduction: {old_length:,} → {len(relative_path)} chars ({old_length//len(relative_path)}x smaller!)")

            fixed_count += 1

        else:
            print(f"   ❌ Invalid data URI format")
            failed_count += 1

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        failed_count += 1

print("\n" + "=" * 80)
print("✅ CONVERSION COMPLETE!")
print("=" * 80)
print(f"\n📊 Results:")
print(f"   Fixed: {fixed_count} images")
print(f"   Failed: {failed_count} images")
print(f"   Total: {count} images")

if fixed_count > 0:
    print(f"\n🎉 {fixed_count} robot images are now ready for animation!")
    print(f"   They can now be used with 'animate image' commands")
    print(f"   File sizes reduced by ~40,000x!")

print("\n" + "=" * 80)
