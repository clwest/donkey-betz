"""
Debug script to see what's happening with image animation
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory
from content.video_provider import runway_provider

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🔍 ANIMATION DEBUG TEST")
print("=" * 80)

# Get image 272
print("\n📸 Finding image 272...")
image = ImageHistory.objects.filter(user=user).order_by('created_at')[271]  # 0-indexed, so 271 = image 272
print(f"   Found: {image.id}")
print(f"   file_path: {image.file_path}")

# Get full URL
print(f"\n🔗 Calling image.get_full_url()...")
url = image.get_full_url()
print(f"   Result: {url[:100]}...")
print(f"   Length: {len(url)} chars")
print(f"   Starts with 'data:': {url.startswith('data:')}")
print(f"   Starts with '/media/': {url.startswith('/media/')}")
print(f"   Contains 'localhost': {'localhost' in url}")

# Try to animate
print(f"\n🎬 Calling runway_provider.image_to_video()...")
try:
    result = runway_provider.image_to_video(
        image_url=url,
        motion_prompt='natural motion',
        duration=5,
        quality='veo3.1_fast'
    )
    print(f"\n✅ Result:")
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Task ID: {result.task_id}")
        print(f"   Status: {result.status}")
    else:
        print(f"   Error: {result.error_message}")
except Exception as e:
    print(f"\n❌ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
