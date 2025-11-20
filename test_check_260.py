"""
Check what's different about image #260 that made it work
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory

print("="*80)
print("🔍 INVESTIGATING IMAGE #260 (THE WORKING ONE!)")
print("="*80)

try:
    image_260 = ImageHistory.objects.filter(user__username='admin').order_by('created_at')[259]  # 0-indexed

    print(f"\n📸 IMAGE #260:")
    print(f"   ID: {image_260.id}")
    print(f"   Created: {image_260.created_at}")
    print(f"   Prompt: {image_260.prompt[:100] if image_260.prompt else 'N/A'}")
    print(f"\n🔑 KEY INFO:")
    print(f"   File Path: {image_260.file_path[:200]}...")
    print(f"   File Path Type: {'DATA URI' if image_260.file_path.startswith('data:') else 'FILE PATH'}")
    print(f"   File Size: {len(image_260.file_path)} chars")
    print(f"   Project: {image_260.project.name if image_260.project else 'None'}")

    # Test get_full_url
    url = image_260.get_full_url()
    print(f"\n🌐 get_full_url() result:")
    print(f"   Type: {'DATA URI' if url.startswith('data:') else 'URL'}")
    print(f"   Value: {url[:200]}...")
    print(f"   Length: {len(url)} chars")

    # Compare with 270/271
    print(f"\n📊 COMPARISON:")
    image_270 = ImageHistory.objects.filter(user__username='admin').order_by('created_at')[269]
    image_271 = ImageHistory.objects.filter(user__username='admin').order_by('created_at')[270]

    print(f"   Image #260: {len(image_260.file_path):,} chars, Type: {'data' if image_260.file_path.startswith('data:') else 'file'}")
    print(f"   Image #270: {len(image_270.file_path):,} chars, Type: {'data' if image_270.file_path.startswith('data:') else 'file'}")
    print(f"   Image #271: {len(image_271.file_path):,} chars, Type: {'data' if image_271.file_path.startswith('data:') else 'file'}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
