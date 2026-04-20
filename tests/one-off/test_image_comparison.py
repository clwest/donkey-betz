"""
Compare images 270 and 271 to find the difference
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory

print("="*80)
print("IMAGE COMPARISON: 270 vs 271")
print("="*80)

try:
    # Get both images
    images = ImageHistory.objects.filter(user__username='admin').order_by('created_at')

    image_270 = images[269]  # 0-indexed
    image_271 = images[270]  # 0-indexed

    print("\n📸 IMAGE #270:")
    print(f"   ID: {image_270.id}")
    print(f"   Created: {image_270.created_at}")
    print(f"   Prompt: {image_270.prompt[:100] if image_270.prompt else 'N/A'}")
    print(f"   File Path: {image_270.file_path[:100]}...")
    print(f"   File Path Type: {'data URI' if image_270.file_path.startswith('data:') else 'file path'}")
    print(f"   File Size: {len(image_270.file_path)} chars")
    print(f"   Project: {image_270.project.name if image_270.project else 'None'}")
    print(f"   Has get_full_url: {hasattr(image_270, 'get_full_url')}")

    print("\n📸 IMAGE #271:")
    print(f"   ID: {image_271.id}")
    print(f"   Created: {image_271.created_at}")
    print(f"   Prompt: {image_271.prompt[:100] if image_271.prompt else 'N/A'}")
    print(f"   File Path: {image_271.file_path[:100]}...")
    print(f"   File Path Type: {'data URI' if image_271.file_path.startswith('data:') else 'file path'}")
    print(f"   File Size: {len(image_271.file_path)} chars")
    print(f"   Project: {image_271.project.name if image_271.project else 'None'}")
    print(f"   Has get_full_url: {hasattr(image_271, 'get_full_url')}")

    # Test get_full_url on both
    print("\n🔍 TESTING get_full_url():")
    try:
        url_270 = image_270.get_full_url()
        print(f"   Image #270 URL: {url_270[:100]}... (length: {len(url_270)})")
    except Exception as e:
        print(f"   ❌ Image #270 get_full_url() failed: {e}")

    try:
        url_271 = image_271.get_full_url()
        print(f"   Image #271 URL: {url_271[:100]}... (length: {len(url_271)})")
    except Exception as e:
        print(f"   ❌ Image #271 get_full_url() failed: {e}")

    # Check gallery visibility
    print("\n📊 GALLERY VISIBILITY CHECK:")
    print(f"   Total images for user: {ImageHistory.objects.filter(user__username='admin').count()}")
    print(f"   Images with project: {ImageHistory.objects.filter(user__username='admin', project__isnull=False).count()}")
    print(f"   Images without project: {ImageHistory.objects.filter(user__username='admin', project__isnull=True).count()}")

    # Get last 10 images
    print("\n📋 LAST 10 IMAGES:")
    last_10 = ImageHistory.objects.filter(user__username='admin').order_by('-created_at')[:10]
    for i, img in enumerate(last_10, 1):
        project_name = img.project.name if img.project else "No Project"
        file_type = "data URI" if img.file_path.startswith('data:') else "file"
        print(f"   {i}. Image #{img.get_sequential_number()}: {project_name} ({file_type}, {len(img.file_path)} chars)")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
